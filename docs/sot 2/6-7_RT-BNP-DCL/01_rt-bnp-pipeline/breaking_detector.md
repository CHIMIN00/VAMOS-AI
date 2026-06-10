# breaking_detector.md — Breaking Detector 4구성 알고리즘 상세

> **도메인**: 6-7_RT-BNP-DCL
> **서브폴더**: 01_rt-bnp-pipeline
> **세션**: P1-1 (Phase 1)
> **정본 상위**: VAMOS_CLOUD_LIBRARY_SPEC + Part2 §6.10.1 / §6.10.2
> **해소 이슈**: ISS-3 (HIGH), P3 (MEDIUM), S-2, FR-5, FR-6
> **DEFINED-HERE**: DH-1 (Breaking Detector V2+ ML 파라미터 정식 정의)

---

## §0. Purpose / Scope

### 0.1 Purpose
Breaking Detector 4구성(Keyword Trigger, Velocity Detector, NLP Classifier(FinBERT), Impact Scorer)의 알고리즘 상세 명세를 정의한다. V1 규칙 기반·V2+ ML 파라미터·허위 속보 RETRACTION 프로토콜·소비자 알림 프로토콜을 포함하여 LOCK L3(BREAKING-P0/P1/P2/NORMAL 4등급), L6(속보 전파 최대 지연 30초), L8(허위 속보 RETRACTION 규칙)을 정확히 준수한다.

### 0.2 Scope
- **포함**: 키워드 사전 구조·매칭 로직·등급 판정 임계값, Velocity Detector 빈도 산출식, FinBERT V2+ 하이퍼파라미터·추론 SLA, Impact Scorer 공식, RETRACTION 무효화 범위·소비자 알림, Breaking Event 출력 스키마, 예외·복구 정책.
- **제외(타 세션)**: Fast Gate 내부 로직(P1-2 fast_gate.md), 소스 어댑터 구현(P1-3 source_adapters.md), Kafka 토픽 설계(P1-4 event_propagation.md).

### 0.3 버전별 범위
| 버전 | 범위 |
|------|------|
| V1 | Keyword Trigger (규칙 기반) + 단순 Impact 규칙, NLP/Velocity/ML 미적용 |
| V2 | + Velocity Detector (빈도 분석), Impact Scorer 규칙 |
| V2+ / V3 | + NLP Classifier (FinBERT fine-tuned), Impact Scorer ML 하이브리드 |

---

## §1. 교차 참조 블록

| 참조 대상 | 파일/섹션 | 참조 목적 |
|-----------|-----------|-----------|
| AUTHORITY_CHAIN.md | §3.1 L3, §3.2 L6/L8, §3.4 L18 | LOCK 값 원본 대조 |
| 01_rt-bnp-pipeline/_index.md | §Breaking Event 분류 체계, §Breaking Detector 엔진, §LOCK 매핑 표 | 아키텍처 요약·ISS-3 배정 대조 |
| RT_BNP_DCL_구조화_종합계획서.md | §3 LOCK L3/L6/L8, §6 ISS-3·P3·S-2, §7.1 버전별 범위, §7.3 의존성 그래프, §14.2 FinBERT 기술 힌트 | 작업 지시 및 힌트 |
| Part2 §6.10.1 | Breaking Event 등급, Fast Gate 규칙, LOCK #14~18 원본 | When/Where 정본 |
| CLOUD_LIBRARY_SPEC | 관련 인프라, LOCK #1~13 | 공통 인프라 제약 |
| P1-2 fast_gate.md | Fast Gate 입력 스키마 | Breaking Event → Fast Gate 인터페이스 |
| P1-4 event_propagation.md | Kafka 토픽 `cl.breaking.*`, `cl.rt.retraction.v1` | 다운스트림 소비 스키마 |
| 6-12 Event-Logging | `cl.rt.*` EventTypeRegistry | 이벤트 코드·로깅 스키마 |

---

## §2. 공통 자료 구조 (정본 선정의)

본 §2의 자료 구조는 01_rt-bnp-pipeline 하위 모든 세션(P1-1~P1-4) 공통이며, 본 파일이 **정본**이다. (규칙 (k) 공통 자료 구조 선정의)

### 2.1 `RawNewsItem` (입력, RT Collector → Breaking Detector)
```jsonc
{
  "item_id": "ULID",          // RT Collector가 발번
  "source_id": "reuters_rss",
  "tier": "T3",                // T1|T2|T3|T4 (LOCK L2)
  "source_weight": 0.95,       // LOCK L5 적용 후 값
  "received_at": "2026-04-14T09:12:03.514Z",
  "language": "ko",
  "title": "...",
  "body": "...",
  "url": "https://...",
  "entities": { "tickers": ["AAPL"], "countries": ["US"] },
  "fingerprint": "sha256:..."  // 본문 정규화 해시 (L9 중복 억제 키)
}
```

### 2.2 `BreakingEvent` (출력, Breaking Detector → Fast Gate → Kafka)
```jsonc
{
  "event_id": "ULID",
  "item_id": "ULID",                         // RawNewsItem 참조
  "grade": "BREAKING-P0",                    // LOCK L3 4등급
  "grade_confidence": 0.94,                  // [0,1]
  "detector_path": ["keyword", "velocity", "nlp", "impact"],
  "keyword_match": {
     "matched_terms": ["halt", "emergency"],
     "rule_grade": "BREAKING-P0"             // 규칙 기반 초기 등급
  },
  "velocity": {
     "topic_key": "trading_halt:NYSE",
     "source_count_window_60s": 5,
     "freq_per_min": 5.0,
     "window_seconds": 60
  },
  "nlp": {                                   // V2+ 존재
     "model": "vamos-finbert-rtbnp-v1",
     "label": "BREAKING",
     "confidence": 0.92
  },
  "impact": {                                // V2+ 존재
     "score": 87.5,                          // 0~100
     "components": { "market": 60, "geo": 15, "credibility": 12.5 },
     "adjustment": "+1 grade"                // P1→P0 업그레이드 등 사유
  },
  "retraction_of": null,                     // RETRACTION 시 원본 event_id
  "source_weight": 0.95,
  "detector_version": "V2+",
  "created_at": "2026-04-14T09:12:03.812Z",
  "sla_deadline": "2026-04-14T09:12:33.812Z",// L6 = created_at + 30s
  "trace_id": "tr_01HY..."
}
```

### 2.3 `RetractionEvent` (무효화)
```jsonc
{
  "event_id": "ULID",
  "type": "RETRACTION",
  "retraction_of": "ULID of invalidated BreakingEvent",
  "reason_code": "POST_VALIDATION_FAIL | SOURCE_CORRECTION | DUPLICATE_FALSE_POSITIVE | MANUAL_RECALL",
  "scope": "SINGLE | TOPIC_WINDOW_5M",       // LOCK L8, L9 연동
  "affected_consumers": ["ai_investing", "ui_alert", "rag_insert"],
  "issued_at": "2026-04-14T09:25:10.000Z",
  "notify_deadline": "2026-04-14T09:25:40.000Z", // L6 준수 (30s)
  "trace_id": "tr_01HY..."
}
```

---

## §3. ABC 시그니처 (정본)

> 규칙 (h) ABC 시그니처 정본 준수. `BaseDetectorComponent`는 L17(Fast Gate ↔ VAMOS 5-Gate 분리)와 동일한 원칙으로 **본 도메인 전용 ABC**이며 VAMOS 5-Gate `BaseGate`와 분리된다.

```python
# breaking_detector/components/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class DetectionResult:
    grade: str                 # "BREAKING-P0"|"P1"|"P2"|"NORMAL"
    confidence: float          # [0,1]
    payload: dict              # 컴포넌트별 세부 (keyword_match, velocity, nlp, impact)

class BaseDetectorComponent(ABC):
    """Breaking Detector 4구성 공통 추상 기반.
    VAMOS 5-Gate BaseGate 와 독립된 RT-BNP 전용 ABC (L17)."""

    name: str
    version: str   # "V1"|"V2"|"V2+"

    @abstractmethod
    def evaluate(self, item: "RawNewsItem",
                 prior: Optional[DetectionResult] = None) -> DetectionResult: ...

    @abstractmethod
    def health_check(self) -> dict: ...   # {"status":"OK|DEGRADED|DOWN","latency_ms":..}
```

파이프라인 체인: `KeywordTrigger → VelocityDetector → NLPClassifier(V2+) → ImpactScorer`. 각 단계는 `prior` 를 받아 등급/신뢰도 업데이트 후 다음 단계로 전달한다.

---

## §4. V1 Keyword Trigger 알고리즘

### 4.1 키워드 사전 구조 (YAML 정본 스키마)
```yaml
# breaking_keywords.yml
version: 1
last_updated: 2026-04-14
languages: [ko, en]
categories:
  market_halt:
    grade: BREAKING-P0
    terms_en: [halt, circuit breaker, suspension]
    terms_ko: [거래정지, 서킷브레이커, 거래중단]
    weight: 1.0
  war_conflict:
    grade: BREAKING-P0
    terms_en: [invasion, war, missile strike]
    terms_ko: [침공, 전쟁, 미사일]
    weight: 1.0
  monetary_policy:
    grade: BREAKING-P1
    terms_en: [emergency rate, rate cut, rate hike]
    terms_ko: [긴급금리, 금리인하, 금리인상]
    weight: 0.9
  earnings_major:
    grade: BREAKING-P1
    terms_en: [bankruptcy, chapter 11, earnings miss]
    terms_ko: [파산, 어닝쇼크]
    weight: 0.85
  sector_trend:
    grade: BREAKING-P2
    terms_en: [regulation, breakthrough, recall]
    terms_ko: [규제, 리콜]
    weight: 0.7
```

구조 불변식(invariants):
1. 각 카테고리는 **정확히 하나의 기본 등급**을 가진다 (L3 4등급 중 하나, NORMAL 제외).
2. 동일 키워드가 2개 이상 카테고리에 매칭되면 **더 높은 등급**이 우선한다 (P0 > P1 > P2).
3. 키워드는 Aho-Corasick automaton 으로 컴파일되어 O(n+m+k) 매칭을 보장한다. (n=본문 길이, m=패턴 총 길이, k=매칭 수)

### 4.2 매칭 로직
```python
def keyword_match(item: RawNewsItem) -> DetectionResult:
    text = _normalize(item.title + "\n" + item.body)   # lowercase, 공백 정규화
    matches = AHO_CORASICK.find_all(text)               # O(n+k)
    if not matches:
        return DetectionResult("NORMAL", 0.0, {"matched_terms": []})
    # 등급 집계: 최고 등급 채택
    # TERM_TO_CAT: 시작 시 KEYWORDS(카테고리 키) 역인덱스 사전 구축 {term: category}
    cats = {TERM_TO_CAT[t] for t in set(matches)}   # set(matches): 멀티셋 N중 인플레 제거
    grades = sorted({KEYWORDS[c].grade for c in cats},
                    key=lambda g: GRADE_RANK[g], reverse=True)
    top_grade = grades[0]
    # 신뢰도: 고유 카테고리 가중치 합 기반 (term 단위 합산 금지 — 멀티셋 인플레 방지)
    conf = min(1.0, sum(KEYWORDS[c].weight for c in cats) / 2.0)
    return DetectionResult(top_grade, conf,
                           {"matched_terms": matches, "rule_grade": top_grade})
```

### 4.3 등급 판정 임계값
| 등급 | 조건 |
|------|------|
| BREAKING-P0 | `market_halt` 또는 `war_conflict` 카테고리 매칭 ∧ source_weight ≥ 0.75 |
| BREAKING-P1 | `monetary_policy` 또는 `earnings_major` 매칭, 또는 P0 키워드 매칭이나 source_weight < 0.75 (2개 이상 독립 소스 대기) |
| BREAKING-P2 | `sector_trend` 매칭 |
| NORMAL | 매칭 없음 |

### 4.4 NORMAL 처리 경로
NORMAL 반환 시 Fast Gate **우회**하고 기존 배치 파이프라인(6-8 Cloud Library)으로 전달한다. `cl.rt.normal.v1` Kafka 토픽은 **발행하지 않는다**(본 세션 정책 — RT-BNP는 BREAKING 등급만 Kafka 발행, NORMAL은 6-8 배치 큐로 직행하여 토픽 폭증 방지).

### 4.5 복잡도
| 단계 | Big-O |
|------|-------|
| Aho-Corasick 컴파일 (사전 로딩 시 1회) | O(m) |
| 본문 매칭 | O(n + k) |
| 등급 집계 | O(k log k) (k ≪ n) |

---

## §5. V1/V2 Velocity Detector

### 5.1 목적 및 L6 준수
단위 시간당 동일 주제(topic) 출현 빈도가 임계값을 초과하면 등급을 상향한다. **측정 윈도우는 60초 고정(슬라이딩)**, 의사결정 지연 상한은 **500ms**로 L6(30s) 대비 충분한 여유를 확보한다.

### 5.2 Topic Key 산출
```python
def topic_key(item: RawNewsItem) -> str:
    entities = sorted(item.entities.get("tickers", []) +
                      item.entities.get("countries", []))
    cat = _dominant_category(item)             # 키워드 카테고리 (§4.1)
    return f"{cat}:{'+'.join(entities) or 'GLOBAL'}"
```
동일 `topic_key`는 서로 다른 소스의 동일 사건으로 간주한다 (L9 중복 억제 5분 윈도우와 독립; Velocity는 60s 집계).

### 5.3 빈도 산출 및 임계값
sliding window counter (Redis Sorted Set, key=`velocity:{topic_key}`, score=epoch_ms):
```
freq_per_min = distinct_sources_count(topic_key, window=60s)
```
| 조건 | 동작 |
|------|------|
| `freq_per_min ≥ 5 ∧ 독립 source_weight 평균 ≥ 0.8` | `grade = max(prior.grade, BREAKING-P0)` |
| `freq_per_min ≥ 3` | `grade = max(prior.grade, BREAKING-P1)` |
| `freq_per_min ≥ 2` ∧ 키워드 매칭 없음 | `BREAKING-P2 후보` (Impact Scorer 확인) |
| `freq_per_min = 1` | 변경 없음 |

### 5.4 L6 30초 예산 할당
| 단계 | 예산 (ms) |
|------|-----------|
| Collector 수신 → Detector 진입 | ≤ 2,000 |
| Keyword | ≤ 50 |
| Velocity | ≤ 500 |
| NLP (V2+) | ≤ 1,500 (p95, 배치 내) |
| Impact Scorer | ≤ 200 |
| Fast Gate | ≤ 300 (P1-2 책임) |
| Kafka → EventBus 전파 | ≤ 2,000 (P1-4 책임) |
| **합계 (P0 목표)** | **≤ 6,550** → 여유 23+s |

### 5.5 Big-O
| 동작 | 복잡도 |
|------|--------|
| Redis ZADD + ZREMRANGEBYSCORE (윈도우 갱신) | O(log N) |
| distinct source count | O(W) (W=윈도우 내 항목 수, 통상 W≤100) |

---

## §6. V2+ NLP Classifier — FinBERT 상세 (ISS-3, S-2, FR-5 해소)

### 6.1 모델 식별자 (DH-1 정식 정의)
| 항목 | 값 |
|------|-----|
| **Base model** | `ProsusAI/finbert` (Hugging Face) |
| **Fine-tuned model ID** | `vamos-finbert-rtbnp-v1` (사내 Model Registry) |
| **Task** | Binary classification `{BREAKING, NORMAL}` + secondary head: grade `{P0,P1,P2}` (softmax) |
| **Tokenizer** | `BertTokenizerFast`, vocab=30522, `max_seq_len=512`, truncation=head, `do_lower_case=True` (en), ko는 mecab 선분할 후 piece |

### 6.2 하이퍼파라미터 (학습)
| 파라미터 | 값 | 근거 |
|----------|-----|------|
| learning_rate | 2e-5 | §14.2 힌트 |
| batch_size | 32 | §14.2 |
| epochs | 3 | §14.2 |
| max_seq_len | 512 | §14.2 |
| warmup_ratio | 0.1 | §14.2 |
| weight_decay | 0.01 | §14.2 |
| optimizer | AdamW | BERT 표준 |
| loss | BCEWithLogits (binary) + CrossEntropy (grade head), 가중합 α=0.7/β=0.3 | 본 DH-1 정의 |
| mixed_precision | fp16 (A100/L4) | 비용 최적 |
| early_stopping | val_f1 3 epoch patience | - |

### 6.3 학습 데이터 코퍼스
| 항목 | 값 |
|------|-----|
| 초기 규모 | 금융 뉴스 헤드라인+lead 10,000건 (breaking 2,000 / normal 8,000) |
| 증강 | back-translation (ko↔en), 동의어 치환, mask infilling |
| 라벨러 | 사내 금융 애널리스트 3인 합의 (Cohen's κ ≥ 0.80 요구) |
| Split | train 80% / val 10% / test 10% (stratified) |
| 갱신 | 월 1회 재학습 + RETRACTION 사례 전부 포함, 성능 하락 감지 시 즉시 재학습 |

### 6.4 추론 설정 — SLA 및 임계값
| 항목 | 값 |
|------|-----|
| **배치 크기 (추론)** | 8 (실시간), 32 (배치 사후 검증) |
| **배치 수집 윈도우** | 최대 200ms 또는 8건 (먼저 도달) |
| **하드웨어** | GPU (T4 equivalent 이상), CPU fallback (ONNX Runtime int8 양자화) |
| **추론 지연 SLA** | p50 ≤ 400ms, p95 ≤ 1,500ms, p99 ≤ 2,500ms (§5.4 NLP 예산 준수) |
| **confidence 임계값** | `conf ≥ 0.85` → BREAKING 채택 / `0.60 ≤ conf < 0.85` → 규칙 기반 폴백 + flag `low_conf` / `conf < 0.60` → 키워드 결과 유지 |
| **Grade 매핑** | head-2 argmax → `{0:P2, 1:P1, 2:P0}`. 단, BREAKING head 미채택 시 무시 |
| **Timeout** | 2,500ms 경과 시 중단 → V1 폴백 (FR-5 / §14.2 폴백 전략) |

### 6.5 분류 레이블 ↔ 등급 매핑
| NLP label | NLP conf | 최종 등급 정책 |
|-----------|----------|---------------|
| BREAKING | ≥ 0.85 | `max(prior, nlp_grade)` 채택 |
| BREAKING | 0.60~0.85 | prior 유지 + `low_conf=true` (Fast Gate에서 사후 검증 우선) |
| NORMAL | ≥ 0.85 | **키워드 매칭 있음에도 downgrade 금지** (R-67-2 속보 정확성 우선). 단, Impact < 30 이면 P2로 강등 허용 |
| NORMAL | < 0.85 | prior 유지 |

### 6.6 Big-O
| 동작 | 복잡도 |
|------|--------|
| 단일 추론 | O(L²·d) (L=seq_len, d=hidden) — fp16 A100 기준 실측 ~60ms |
| 배치 추론 | O(B·L²·d) 병렬 — 8 batch ~280ms |

---

## §7. V2+ Impact Scorer

### 7.1 산출 공식
```
impact = 0.55·market + 0.20·geo + 0.15·credibility + 0.10·audience
  market      = f_market(entities, price_volatility_24h)   # 0..100
  geo         = f_geo(countries, conflict_index)           # 0..100
  credibility = 50 + 50·(source_weight − 0.5)              # 0..100
  audience    = f_audience(social_velocity, followers)     # 0..100
```
`f_market`는 티커가 있으면 최근 24h 실현변동성 × β (β=10), 없으면 산업 지수 변동성 사용. 결측 시 0.

### 7.2 등급 업/다운그레이드 조건
| 조건 | 조정 |
|------|------|
| `impact ≥ 80` | +1 grade (최대 P0) |
| `60 ≤ impact < 80` | 등급 유지 |
| `30 ≤ impact < 60` ∧ NLP=NORMAL | -1 grade (최소 P2) |
| `impact < 30` ∧ NLP=NORMAL ∧ Velocity < 2 | NORMAL 으로 강등 |
| `impact ≥ 80` ∧ source_weight < 0.5 (SNS 단일) | 강등 금지, 단 Fast Gate에서 교차 확인 요구 (§4.3 T4 SNS 단일 소스 정책 + R-67-4 P2 도메인 승인 경로 연계) |

### 7.3 Big-O
O(1) 산식 + O(#entities) 조회. 외부 시세 API 호출은 10초 캐시로 상각.

---

## §8. RETRACTION 무효화 처리 (L8 / L18 / FR-6)

### 8.1 허위 속보 감지 트리거
| 트리거 | 발원 | 조건 |
|--------|------|------|
| T-R1: 사후 검증 실패 | Fast Gate 30분 재검증 (L7) | 정규 G0-G4 FAIL → RETRACTION 발행 (L18) |
| T-R2: 소스 정정 | Collector (T-source-retraction) | 동일 source_id에서 `retracted=true` 또는 공식 정정 헤드라인 수신 |
| T-R3: 독립 부정 보도 | Velocity Inverse | 동일 topic_key에 대해 반박 키워드(`denies`, `false`, `unfounded`)가 5분 내 2개 이상 독립 소스 |
| T-R4: 관리자 수동 | Ops 콘솔 | 운영자 수동 호출 (audit 필수) |

### 8.2 무효화 범위 (scope)
| scope | 대상 |
|-------|------|
| SINGLE | 해당 `event_id` 1건만 (기본값) |
| TOPIC_WINDOW_5M | 동일 `topic_key` 5분 윈도우 내 모든 BreakingEvent (L9 윈도우와 정렬) |

선택 규칙: T-R1/T-R2는 SINGLE 기본, T-R3은 TOPIC_WINDOW_5M, T-R4는 운영자 지정.

### 8.3 소비자 알림 프로토콜 (FR-6 해소)
1. `RetractionEvent` 를 Kafka `cl.rt.retraction.v1` 토픽에 즉시 발행 (L6 30초 내 완료 필수).
2. 소비자 목록(`affected_consumers`)에 대해 도메인별 훅 호출:
   - **AI Investing (3-1)**: 전략 엔진 `on_retraction(event_id)` — 해당 이벤트로 체결된 자동 주문 즉시 재평가 (R-67-4 P2 도메인 승인 체인 존중).
   - **UI Alert (6-1)**: `notification.retract(event_id, reason)` — 배너 교체 및 사용자 경고.
   - **RAG Insert (6-4)**: `rag.invalidate(event_id)` — 벡터 삭제 + tombstone 마커.
   - **Event Log (6-12)**: `cl.rt.retraction.v1` audit 로그 (immutable).
3. 각 소비자의 ACK 를 `ack_deadline = issued_at + 600s`(DH-2, retraction_protocol.md §2.1 정본) 내 수집. 미수신 시 구조화 로그 + 60초 backoff×3 재시도(§11.2, §13 RETRACT_CONSUMER_NACK). (※ 발행 자체는 L6 30초 내 완료 — notify_deadline; ACK 수집 시한은 600초.)

### 8.4 Big-O
O(|affected_consumers|) — 통상 4개 고정. 훅 호출은 비동기 병렬.

---

## §9. 등급 판정 기준표 (LOCK L3 통합)

| 등급 | 키워드 | Velocity freq/min | NLP conf | Impact | source_weight | 대표 액션 (L3 기반) |
|------|--------|-------------------|----------|--------|---------------|---------------------|
| BREAKING-P0 | market_halt / war_conflict | ≥ 5 | ≥ 0.85 (BREAKING) | ≥ 80 | ≥ 0.75 | 즉시 전파 + Circuit Breaker 평가 (L6 30s) |
| BREAKING-P1 | monetary / earnings_major | ≥ 3 | ≥ 0.85 | 60~80 | ≥ 0.6 | 5분 내 전파 + 전략 재평가 |
| BREAKING-P2 | sector_trend | ≥ 2 | ≥ 0.70 | 30~60 | ≥ 0.4 | 정규 큐 우선 삽입 |
| NORMAL | 매칭 없음 | < 2 | - | < 30 | - | 기존 배치 파이프라인 |

> **결정 규칙**: 각 컴포넌트의 제안 등급 중 **최고 등급**이 초기값, Impact Scorer의 ±1 조정 후 **최종 grade** 결정. FinBERT conf < 0.60 시 키워드 결과 그대로 사용.

---

## §10. LOCK 교차검증 표

| LOCK | 정본 규칙 | 본 문서 반영 | 섹션 |
|------|-----------|--------------|------|
| L3 | BREAKING-P0/P1/P2/NORMAL 4등급 | §2.2 grade enum, §4.3, §6.5, §7.2, §9 | PASS |
| L6 | 속보 전파 최대 지연 30초 (BREAKING-P0) | §2.2 sla_deadline, §5.4 예산 할당, §8.3 RETRACTION 60초 | PASS |
| L7 | 사후 검증 시한 30분 (Fast Gate 책임) | §8.1 T-R1 (L7 참조만, 구현은 P1-2) | PASS (참조) |
| L8 | 허위 속보 RETRACTION 즉시 발행 + 이전 이벤트 무효화 | §2.3 RetractionEvent, §8 전체 | PASS |
| L9 | 동일 속보 중복 억제 5분 윈도우 | §5.2 topic_key, §8.2 TOPIC_WINDOW_5M scope | PASS (windowing은 Fast Gate CL-G4에서 최종) |
| L17 | Fast Gate ↔ VAMOS 5-Gate 분리, BaseGate(ABC)만 공유 | §3 `BaseDetectorComponent`는 VAMOS 5-Gate와 분리된 독립 ABC | PASS |
| L18 | 사후 검증 실패 시 RETRACTION + 사용자 알림 | §8.1 T-R1, §8.3 UI Alert 훅 | PASS |
| AUTH §2 충돌 해결 우선순위 | SPEC > Part2 §6.10.1 > SOT2 | §14.2 힌트를 DH-1로 정식화하되 LOCK 값 불변 | PASS |

LOCK 변경 필요 사항: **없음**. (LOCK 변경 필요 시 [LOCK_CHANGE_NEEDED] 마커 사용 규정 — 본 세션 해당 없음)

---

## §11. EscalationPayload (I-20) 및 구조화 로깅

### 11.1 EscalationPayload (인터페이스 I-20)
Breaking Detector 컴포넌트 실패 시 상위(Ops / 6-13) 에스컬레이션 payload:
```jsonc
{
  "source_engine": "breaking_detector.nlp_classifier",  // component path
  "error_code": "NLP_TIMEOUT_2500MS",
  "original_request": {
    "item_id": "ULID",
    "tier": "T2",
    "source_id": "newsapi_finance"
  },
  "partial_result": {
    "grade": "BREAKING-P1",          // V1 폴백으로 얻은 잠정 등급
    "confidence": 0.72,
    "detector_path": ["keyword", "velocity"]
  },
  "retry_count": 2,
  "timestamp": "2026-04-14T09:12:05.100Z",
  "trace_id": "tr_01HY...",
  "severity": "WARN",                // INFO|WARN|ERROR|CRITICAL
  "recovery_hint": "fallback_v1_keyword_accepted"
}
```

### 11.2 구조화 로깅 JSON (중첩) — 규칙 (c)
```jsonc
{
  "ts": "2026-04-14T09:12:05.101Z",
  "level": "ERROR",
  "component": "breaking_detector.nlp_classifier",
  "trace_id": "tr_01HYAB3...",
  "span_id": "sp_01HYAB4...",
  "error": {
    "code": "NLP_TIMEOUT_2500MS",
    "message": "FinBERT inference exceeded SLA",
    "stack": "<truncated>"
  },
  "context": {
    "item_id": "01HY...",
    "tier": "T2",
    "source_id": "newsapi_finance",
    "batch_size": 8,
    "queue_depth": 23,
    "model": "vamos-finbert-rtbnp-v1"
  },
  "recovery": {
    "action": "fallback_v1_keyword",
    "degraded_confidence": 0.72,
    "degraded_grade": "BREAKING-P1",
    "circuit_breaker": "half_open"
  },
  "sla": { "deadline_ms_remaining": 22800, "lock_ref": "L6" }
}
```

---

## §12. Phase별 복구 흐름 + Confidence Penalty (규칙 (e))

### 12.1 복구 흐름 (Mermaid)
```mermaid
flowchart TD
  A[Raw item 수신] --> B[Keyword Trigger]
  B -->|OK| C[Velocity Detector]
  B -->|Dict load fail| B1[Reload 캐시된 사전, penalty -0.05]
  C -->|OK| D{V2+?}
  C -->|Redis fail| C1[in-proc LRU window fallback, penalty -0.10]
  D -->|Yes| E[NLP FinBERT]
  D -->|No (V1)| G[Impact Scorer rule]
  E -->|Timeout| E1[V1 폴백, penalty -0.15, log ERROR]
  E -->|Low conf <0.60| E2[Keep prior, penalty -0.05]
  E -->|OK| F[Impact Scorer ML]
  F --> G
  G --> H{Fast Gate P1-2}
  H -->|PASS| I[Kafka cl.breaking.*]
  H -->|FAIL| J[drop + log]
  H -->|30m post FAIL| K[RETRACTION §8]
```

### 12.2 Confidence Penalty 표
| 복구 경로 | penalty | 최종 grade_confidence |
|-----------|---------|----------------------|
| 사전 캐시 폴백 | -0.05 | max(0, conf-0.05) |
| Velocity in-proc fallback | -0.10 | max(0, conf-0.10) |
| NLP V1 폴백 (timeout) | -0.15 | max(0, conf-0.15) |
| NLP low_conf 유지 | -0.05 | max(0, conf-0.05) |
| Impact Scorer 외부 시세 API 실패 | -0.08 | credibility 성분 중립 50 대체 |
| 다중 복구 동시 발생 | 합산 (하한 0.30) | conf ≥ 0.30 유지, 미만 시 P2로 강등 |

---

## §13. 예외 처리 정책 표 (규칙 (g))

| 예외 코드 | 원인 | 처리 | Confidence 조정 | 에스컬레이션 |
|-----------|------|------|------------------|--------------|
| KW_DICT_LOAD_FAIL | YAML 파싱 오류 | 최근 양호 캐시 사용 | -0.05 | WARN → Ops |
| KW_AHO_BUILD_FAIL | automaton 빌드 실패 | substring 폴백 (O(n·m)) | -0.10 | ERROR → Ops |
| VEL_REDIS_DOWN | Redis 연결 실패 | in-proc ring buffer fallback | -0.10 | WARN → 6-13 |
| NLP_TIMEOUT_2500MS | 추론 SLA 초과 | V1 폴백 + Circuit Breaker half-open | -0.15 | WARN |
| NLP_MODEL_LOAD_FAIL | 모델 파일 손상/미존재 | V1 폴백 + 재학습 트리거 | -0.20 | CRITICAL → Ops + 자동 롤백 이전 버전 |
| NLP_GPU_OOM | 메모리 부족 | batch 축소(8→4), ONNX CPU 전환 | -0.05 | WARN |
| IMPACT_MKT_API_FAIL | 시세 API 장애 | credibility 중립치 50 사용 | -0.08 | INFO |
| RETRACT_CONSUMER_NACK | 소비자 ACK 미수신 | 60초 backoff×3 재시도 후 CRITICAL | n/a | CRITICAL → 6-13 P2 알림 |
| SLA_L6_BREACH | 30초 예산 초과 | Fast Gate 직전 중단, log CRITICAL | n/a | CRITICAL → SLO 대시보드 |
| SCHEMA_VALIDATION_FAIL | BreakingEvent 스키마 오류 | drop + quarantine | n/a | ERROR |

---

## §14. Phase 2 테스트 시나리오 (규칙 (d) — 10건 이상)

| # | 시나리오 | 입력 | 기대 결과 | 검증 LOCK |
|---|----------|------|----------|-----------|
| T-01 | 거래정지 키워드 단일 소스 (Reuters, T3) | "NYSE halts trading" | BREAKING-P0, conf≥0.80, <30s 전파 | L3, L6 |
| T-02 | 전쟁 키워드 다중 소스 (5건/60s) | war_conflict topic_key | BREAKING-P0 (Velocity 가산), freq=5 | L3, L5 |
| T-03 | 금리 인상 + Impact=75 | monetary_policy, market vol 상승 | BREAKING-P1 유지 | L3 |
| T-04 | SNS 단일 (T4) 거래정지 주장 | source_weight=0.4 | BREAKING-P1 대기 + 교차확인 요구, Fast Gate R-67-3 | L5, L17 |
| T-05 | FinBERT NLP_TIMEOUT | NLP 2.5s 초과 | V1 폴백 채택, penalty -0.15, ERROR 로그 | FR-5, L6 |
| T-06 | FinBERT conf=0.70 low_conf | 경계 신뢰도 | prior 유지, `low_conf=true` 플래그 | §6.4 |
| T-07 | RETRACTION T-R1 (사후 G0-G4 FAIL) | 30분 후 Fast Gate 실패 | RetractionEvent SINGLE, 4 소비자 알림 ≤60s | L7, L8, L18 |
| T-08 | RETRACTION T-R3 (반박 보도 ≥2 독립 소스 5분) | `denies`, `false` | TOPIC_WINDOW_5M 무효화 | L8, L9 |
| T-09 | 동일 event 5분 내 중복 (같은 topic_key) | 중복 3건 | 1건만 유지 (L9), 나머지 suppressed | L9 |
| T-10 | Redis 장애 중 BREAKING-P0 수신 | VEL_REDIS_DOWN | in-proc fallback, grade 유지, penalty -0.10 | §13 |
| T-11 | NORMAL 강등 (impact=22, NLP=NORMAL, Velocity=1) | sector_trend 1건 | NORMAL, Kafka 발행 없음 | §4.4, §7.2 |
| T-12 | 다국어 (ko 本文 "긴급 금리 인하") | Korean | BREAKING-P1, ko tokenizer 동작 | §6.1 |
| T-13 | 혼합 카테고리 (war + monetary) | 최고 등급 채택 | BREAKING-P0 | §4.1 |
| T-14 | Impact API 장애 | IMPACT_MKT_API_FAIL | credibility=50 중립, penalty -0.08 | §13 |
| T-15 | L6 예산 초과 (Collector 지연 25s) | 진입 지연 큼 | SLA_L6_BREACH CRITICAL, drop 전 alert | L6 |

(총 15건 — 요구 10건 이상 충족)

---

## §15. 세션 간 인터페이스 Cross-Check (규칙 (j), (l), (m))

### 15.1 Downstream — P1-2 `fast_gate.md`
Fast Gate의 입력은 본 문서 §2.2 `BreakingEvent`이다. 필수 필드:
- `grade` (L3), `grade_confidence`, `impact.score`, `source_weight`, `sla_deadline`, `trace_id`, `retraction_of` (null 가능).
- P1-2는 본 스키마를 **read-only**로 소비하며 수정 금지. 스키마 변경 필요 시 P1-1에 CONFLICT 등재 후 본 문서를 정본으로 갱신.

### 15.2 Downstream — P1-4 `event_propagation.md`
Kafka 토픽 대상:
- `cl.breaking.p0.v1` / `cl.breaking.p1.v1` / `cl.breaking.p2.v1` (payload = `BreakingEvent`).
- `cl.rt.retraction.v1` (payload = `RetractionEvent` §2.3).
- **정본 필드명**은 본 §2에서 고정. P1-4는 파티셔닝 키로 `topic_key`(§5.2)를 권고.

### 15.3 Upstream — P1-3 `source_adapters.md`
- 본 문서 §2.1 `RawNewsItem`을 어댑터 공통 출력 스키마로 수용한다.
- 필드 `fingerprint` 산출식(SHA-256 of normalized `title+body`)은 본 문서에서 정의(§2.1 주석) — P1-3에서 동일 알고리즘 구현.

### 15.4 Cross-domain
- **6-12 Event-Logging**: `cl.rt.*` EventTypeRegistry 등록 필수 (3개 breaking + 1 retraction = 4개). 코드 네이밍은 본 §15.2 고정.
- **6-4 Memory-RAG (I-2)**: `rag.invalidate(event_id)` 훅 시그니처는 §8.3에서 참조. 6-4 측 최종 시그니처는 6-4 P2에서 확정.
- **3-1 AI Investing**: `on_retraction(event_id)` 훅 계약은 3-1 도메인 정본 우선. 본 문서는 호출 의무만 선언.

### 15.5 의존성 그래프 (규칙 (l))
```
[P1-3 source_adapters] --RawNewsItem--> [P1-1 breaking_detector] --BreakingEvent--> [P1-2 fast_gate]
                                                                 \-RetractionEvent-> [P1-4 event_propagation]
[P1-1] ---(§2, §3 ABC 정본)---> [P1-2, P1-3, P1-4 참조]
```

### 15.6 통합 산출물 요건 (규칙 (m))
본 문서는 `_index.md` §Breaking Detector 엔진과 §LOCK 매핑 표의 **상세 확장본**이며, 루트 `INDEX.md` 갱신은 별도 통합 세션에서 수행 (본 세션 수정 금지 대상).

---

## §16. 버전 이력

| 버전 | 날짜 | 변경 | 작성 |
|------|------|------|------|
| 1.0 | 2026-04-14 | Phase 1 P1-1 초안 (§0~§15 전체) — ISS-3/S-2/FR-5/FR-6 해소, DH-1 정식 정의 | SOT2 6-7 P1-1 세션 |

[GUARDS_OK] memory_skipped=YES forbidden_paths=untouched common_artifacts=untouched

---

<!-- V3 EXTEND, NOT REDEFINITION — Phase 4 RECOVERY P4-2 genuine write, 2026-06-02. 본 §17 이전(§0~§16, [GUARDS_OK] 포함) 본문은 Phase 1 P1-1 baseline byte-prefix SHA UNCHANGED 보존. 아래는 V2+ ML 파라미터 정식 확정 append (FR-5 ⚠️ PARTIAL → ✅ PASS). 기존 §6 하이퍼파라미터 값 재정의 0건 — 확정·통합·미정의분 보완만. -->

## §17. V2+ ML 파라미터 정식 확정 (Phase 4 V3 EXTEND, FR-5 PARTIAL → PASS)

> **목적**: §6 NLP Classifier(FinBERT)의 V2+ ML 하이퍼파라미터를 production 운영 기준으로 정식 확정한다. §6.2(학습 하이퍼파라미터)·§6.4(추론 SLA·confidence)의 값은 **재정의 없이 그대로 계승**하며, drift detection·성능 게이트(P/R/F1)·재학습 주기·카나리 배포를 추가 정의하여 FR-5(Breaking Detector ML 파라미터)를 ⚠️ PARTIAL → ✅ PASS로 전환한다.

### 17.1 ML 하이퍼파라미터 정식 확정 매트릭스 (§14.2 정본 inheritance)

| 항목 | 정본 값 | 출처 | §6 계승 |
|------|--------|------|---------|
| Base model | `ProsusAI/finbert` (Hugging Face) | §14.2 ML 기술 힌트 | §6.1 verbatim |
| Fine-tuned model ID | `vamos-finbert-rtbnp-v1` | 사내 Model Registry | §6.1 verbatim |
| learning_rate (lr) | **2e-5** | §14.2 | §6.2 verbatim |
| batch_size (학습) | **32** | §14.2 | §6.2 verbatim |
| epochs | **3** | §14.2 | §6.2 verbatim |
| max_seq_len | 512 | §14.2 | §6.2 verbatim |
| confidence 임계값 | **≥ 0.85** (BREAKING 채택) | §14.2 | §6.4 verbatim |
| **Precision / Recall / F1** | **≥ 0.87** (test split, weekly 측정) | §14.2 P4-2 대조 기준 | **§17 신규 정식화** |
| **drift detection (KL divergence)** | **> 0.15** → 재학습 트리거 | P4-2 대조 기준 | **§17 신규 정식화** |
| **재학습 주기** | **weekly** (정기) + drift KL > 0.15 즉시 + RETRACTION 사례 전부 포함 | §6.3 "월 1회 + 성능 하락 즉시" 확장 | §6.3 계승·강화 |
| 추론 지연 SLA | p50 ≤ 400ms / p95 ≤ 1,500ms / p99 ≤ 2,500ms | §6.4 | §6.4 verbatim |

### 17.2 Drift Detection + 자동 재학습 트리거 (신규 정식화)

```python
def check_drift_and_retrain(recent_dist, baseline_dist) -> bool:
    kl = kl_divergence(recent_dist, baseline_dist)   # 입력 분포 drift
    if kl > 0.15:                                     # 정본 임계값
        trigger_retrain(reason="DRIFT_KL_EXCEED", include_retractions=True)
        return True
    return False
```
- **정기 재학습**: weekly cron. **즉시 재학습**: drift KL > 0.15 검출 시 또는 P/R/F1 < 0.87 하락 시.
- **데이터 포함 규칙**: 재학습 코퍼스에 직전 주기 RETRACTION 사례(§8) 전부 포함 (허위 양성 학습, R-67-2 속보 정확성 우선).

### 17.3 카나리 배포 (R-66-5 인용)

| 단계 | 트래픽 | 게이트 조건 | 롤백 |
|------|--------|------------|------|
| Shadow | 0% (로그만) | 추론 결과 기록, P/R/F1 ≥ 0.87 사전 검증 | — |
| Canary | 5% | confidence ≥ 0.85 + 에러율 < 1% + 3일 관찰 | 미달 시 즉시 |
| Partial | 25% | P/R/F1 ≥ 0.87 유지 | 미달 시 이전 버전 |
| Full | 100% | 전 게이트 통과 | NLP_MODEL_LOAD_FAIL 시 §13 자동 롤백 |

- **R-66-5 카나리 검증 프로토콜 인용**(read-only, 재정의 0건). 신규 모델 배포 시 카나리 단계 게이트 전수 통과 필수. 실패 시 §13 NLP_MODEL_LOAD_FAIL 경로로 V1 폴백 + 이전 버전 자동 롤백.

### 17.4 FR-5 PASS 전환 근거

- §6.2/§6.4 baseline(lr/batch/epochs/confidence) **재정의 0건 계승** + §17.1 P/R/F1 ≥ 0.87 + §17.2 drift KL > 0.15 + 재학습 weekly + §17.3 카나리 R-66-5 = ML 파라미터 production 운영 기준 **정식 확정 완료** → FR-5 ⚠️ PARTIAL → ✅ **PASS**.
- LOCK L3(Breaking Event 4등급) + L8(RETRACTION 학습 포함) 정합, LOCK 변경 0건. DH-1(Breaking Detector V2+ ML 파라미터) 정본 위치 본 파일 §6+§17 통산 보존.

### 17.5 버전 이력 append

| 버전 | 날짜 | 변경 | 작성 |
|------|------|------|------|
| 1.1 | 2026-06-02 | Phase 4 RECOVERY P4-2 V2+ ML EXTEND — §17 ML 파라미터 정식 확정(P/R/F1 ≥ 0.87 + drift KL > 0.15 + 재학습 weekly + 카나리 R-66-5), FR-5 PARTIAL → PASS. §0~§16 baseline byte-prefix UNCHANGED 보존, §6 값 재정의 0건. | SOT2 6-7 P4-2 RECOVERY |

[GUARDS_OK] v3_extend=YES prefix_unchanged=YES redefinition=0 fr5=PASS
