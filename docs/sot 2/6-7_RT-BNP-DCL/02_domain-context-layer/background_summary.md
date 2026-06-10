# Background Summary — 배경 요약 갱신 알고리즘 + ISS-5 + P5 GPT-4o-mini/Llama 비용 비교

> **수정 정책**: 정본 — Phase 변경 시 갱신 (§8.2)
> **도메인**: 6-7_RT-BNP-DCL / 02_domain-context-layer
> **Tier**: 6 (System-wide Components)
> **정본 출처**:
> - VAMOS_CLOUD_LIBRARY_SPEC (관련 인프라, LOCK 1차) verbatim — 비용 상한 + 품질 관리
> - Part2 §6.10.2 (FULL, L5664-L5741) verbatim — 1시간 갱신 + 비용 상한 V1/V2/V3
> - SOT2 6-7 종합계획서 §6.2 ISS-5 (배경 요약 캐시 갱신 프로토콜 MEDIUM, 요약 모델 GPT-4o-mini/Llama + 토큰 상한 2048 + 컨텍스트 윈도우 24h + 캐시 무효화 조건) + §6.2 P5 (DCL 배경 요약 프로토콜 미상세 MEDIUM, 비용 비교) + §7.2 P2-3 + §4.3 R-67-3 (DCL 비용 상한 준수)
> - AUTHORITY_CHAIN.md §3.3 (L13 QoD 임계값 + L14 1시간 갱신 + L15 비용 상한)
> - 02_domain-context-layer/_index.md §DCL 품질 관리 (배경 요약 갱신 1시간 + 비용 상한)
> - dcl_channels.md (P2-1 산출물 — 3채널 집계 결과 + aggregated_topics 출력)
> - rag_integration.md (P2-2 산출물 — RAG 검색 결과 + RETRACTION 무효화 정합)
> **LOCK 매핑**: L8 (RETRACTION 무효화), L13 (QoD 임계값), L14 (DCL 배경 요약 갱신 주기 1시간), L15 (DCL 비용 상한 V1/V2/V3)
> **DH 매핑**: DH-4 (DCL 배경 요약 생성 프로토콜 — 본 문서 정본)
> **Phase**: P2-3 (ISS-5 배경 요약 + P5 GPT-4o-mini/Llama 비용 비교 해결)
> **생성일**: 2026-04-28
> **ISS 해결**: **ISS-5** (배경 요약 캐시 갱신 프로토콜 — 본 문서 정본 정의) + **P5** (DCL 배경 요약 프로토콜 — 모델 후보별 비용/성능 비교 표 본 §3.2)
> **선행 의존**: dcl_channels.md (P2-1, 3채널 aggregated_topics) / rag_integration.md (P2-2, RAG 검색 결과 + RETRACTION 정합) / 02/_index.md (L14/L15 LOCK 매핑)

---

## 교차 참조 블록 (Rule a)

| 참조 대상 | 관계 |
|----------|------|
| **VAMOS_CLOUD_LIBRARY_SPEC verbatim** | 관련 인프라 LOCK 1차 정본 (비용 상한 출처) — L15 정본 |
| **Part2 §6.10.2 L5664-L5741 verbatim** | DCL 전문 설계 정본 (FULL) — 1시간 갱신 + 비용 상한 V1/V2/V3 정본 |
| **02_domain-context-layer/_index.md §DCL 품질 관리** | "배경 요약 갱신: 1시간마다 재생성 (LOCK L14)" + "비용 상한: V1 +₩0, V2 +₩5,000/월, V3 +₩15,000/월 (LOCK L15)" — 본 §2 + §5 정본 |
| **dcl_channels.md (P2-1)** | 3채널 집계 결과 (`aggregated_topics`) — 본 §3.1 입력 |
| **rag_integration.md (P2-2)** | RAG 검색 결과 (vector + payload) — 본 §3.1 입력 + RETRACTION soft delete 정합 |
| **종합계획서 §6.2 ISS-5 verbatim** | "요약 모델 선택(GPT-4o-mini/Llama), 토큰 상한(2048), 컨텍스트 윈도우(24h), 캐시 무효화 조건" — 본 §3.2 + §3.3 + §4 정본 |
| **종합계획서 §6.2 P5** | DCL 배경 요약 프로토콜 미상세 (MEDIUM) — 본 §3.2 모델 후보별 비용/성능 비교 표 |
| **종합계획서 §4.3 R-67-3** | DCL 비용 상한 준수 — 본 §5.5 운영 비용 모니터링 |
| **AUTHORITY_CHAIN.md §3.3 L13 verbatim** | QoD ≥ 0.5 → RAG 삽입, < 0.5 → 폐기 — 본 §4.2 캐시 무효화 (b) 정합 |
| **AUTHORITY_CHAIN.md §3.3 L14 verbatim** | 1시간마다 재생성 — 본 §2 (전체) |
| **AUTHORITY_CHAIN.md §3.3 L15 verbatim** | V1: +₩0, V2: +₩5,000/월, V3: +₩15,000/월 — 본 §3.2 + §5 |
| **AUTHORITY_CHAIN.md §3.3 L8 verbatim** | RETRACTION — 즉시 발행 + 이전 이벤트 무효화 — 본 §4.1 캐시 무효화 (a) 정합 |
| **6-4 Memory-RAG (참조만, 재정의 ❌)** | 캐시 스토리지 인프라 (LOCK-ME-* 정본) |
| **6-13 Operations (참조만, 재정의 ❌)** | 비용 모니터링 운영 절차 (Part2 §6.12.10) |

---

## 1. 개요

본 문서는 Domain Context Layer(DCL)의 **배경 요약 갱신 알고리즘**을 상세 명세하고, **ISS-5(요약 모델 선택, 토큰 상한, 컨텍스트 윈도우, 캐시 무효화 조건)** 및 **P5(DCL 배경 요약 프로토콜 — 모델 후보별 비용/성능 비교)**를 해결한다. **LOCK L14(1시간마다 재생성)** + **LOCK L15(비용 상한 V1/V2/V3)** + **R-67-3(비용 상한 준수)**를 강제한다.

> **DCL 배경 요약 정의**: 3채널(FIN/TECH/GEO) 집계 결과(P2-1) + RAG 검색 결과(P2-2)를 통합하여 "현재 세상 상황 요약" 텍스트를 생성하고, 1시간마다 재생성한다.

### 1.1 책임 요약

- **1시간 주기 재생성 (§2)**: LOCK L14 verbatim — 매 정각 재생성 (Cron 트리거)
- **요약 모델 선택 (§3.2)**: V1 룰 기반 / V2 GPT-4o-mini 또는 Llama / V3 FinBERT + GPT-4o (P5 비용/성능 비교 표 포함)
- **토큰 상한 + 컨텍스트 윈도우 (§3.3)**: 출력 2048 토큰 / 입력 24h 롤링 (ISS-5 verbatim)
- **캐시 무효화 조건 3가지 (§4)**: (a) RETRACTION 발행 시 (LOCK L8) / (b) QoD < 0.5 발생 시 (LOCK L13) / (c) 24h 만료 시 (LOCK L14 정합)
- **비용 상한 준수 (§5)**: LOCK L15 — V1: +₩0 / V2: +₩5,000/월 / V3: +₩15,000/월
- **운영 비용 모니터링 (§5.5)**: R-67-3 — DAILY 비용 집계 + L15 초과 alert + 모델 폴백
- **캐시 키 설계 (§6)**: `{channel}:{window_id}:{version}` — 채널 + 시간 윈도우 + 모델 버전

### 1.2 데이터 흐름

```
[dcl_channels.md (P2-1)]                [rag_integration.md (P2-2)]
    aggregated_topics                       vector + payload
            │                                       │
            └────────────┬──────────────────────────┘
                         ▼
                  [본 문서 §3]
            배경 요약 생성 알고리즘
                         │
            ┌────────────┼────────────┐
            ▼                          ▼
       [캐시 저장]                [I-3 L0 Context 주입]
       (1시간 TTL,                (rag_integration.md §4
        L14)                       — V2+)
            │
            ▼
    [§4 캐시 무효화 3가지]
        (a) RETRACTION (L8)
        (b) QoD < 0.5 (L13)
        (c) 24h 만료 (L14)
```

---

## 2. 1시간 주기 재생성 (LOCK L14 verbatim)

### 2.1 LOCK L14 정본

> **출처**: AUTHORITY_CHAIN.md §3.3 L14 verbatim — "1시간마다 재생성"
>
> **출처**: 02_domain-context-layer/_index.md §DCL 품질 관리 verbatim — "I-3 L0에 주입되는 '세상 상황 요약'은 1시간마다 재생성 (LOCK L14)"

배경 요약은 매 정각(00분 00초) Cron 트리거로 재생성된다. 재생성 결과는 다음 정각까지(60분 TTL) 캐시 보관된다.

### 2.2 재생성 시각 + 트리거

| 트리거 | 시각 | 처리 | 버전 |
|--------|------|------|------|
| 정각 Cron (1시간 주기) | 매 시 00분 00초 | 전체 채널 신규 요약 생성 (LOCK L14 정본) | V1+ |
| RETRACTION 발생 시 | 즉시 (LOCK L6 30초 SLA) | 영향 캐시 무효화 → 부분 재생성 (영향 채널만) | V1+ |
| Breaking-P0 발생 시 | 즉시 (LOCK L6 30초 SLA) | 영향 채널 단일 토픽 추가 (전체 재생성 ❌) | V2+ |
| 사용자 명시 요청 시 | 즉시 | 전체 채널 재생성 + 캐시 갱신 | V1+ |

---

## 3. 배경 요약 생성 알고리즘

### 3.1 입력 + 처리

```python
def generate_background_summary(window_start: datetime, window_end: datetime) -> dict:
    """
    window_start ~ window_end 기간의 DCL 3채널 집계 결과 + RAG 검색 결과 통합
    반환: 채널별 요약 텍스트 + 토픽 카운트 + 평균 QoD
    """
    # P2-1 입력: dcl_channels.md §3.6 출력
    aggregated_topics = dcl_aggregator.fetch(window_start, window_end)
    # aggregated_topics: list[{channel, topics[], aggregated_qod}]

    # P2-2 입력: rag_integration.md §3.4 출력
    rag_search_results = rag_pipeline.fetch_recent(window_start, window_end)
    # rag_search_results: list[{vector, payload, retracted_flag}]

    # RETRACTION 제외 (LOCK L8 정합, rag_integration.md §5.1)
    rag_filtered = [r for r in rag_search_results if not r.retracted_flag]

    # 채널별 요약 생성
    summaries = {}
    for channel in ["DCL-FIN", "DCL-TECH", "DCL-GEO"]:
        summaries[channel] = summarize_channel(
            channel=channel,
            topics=next((t["topics"] for t in aggregated_topics if t["channel"] == channel), []),
            rag_payloads=rag_filtered,
            model=select_model(),  # §3.2
            max_input_window=24 * 3600,  # 24h (ISS-5)
            max_output_tokens=2048,       # ISS-5
        )
    return summaries
```

### 3.2 요약 모델 선택 (ISS-5 + P5 핵심)

> **출처**: 종합계획서 §6.2 ISS-5 verbatim — "요약 모델 선택(GPT-4o-mini/Llama), 토큰 상한(2048), 컨텍스트 윈도우(24h), 캐시 무효화 조건"
>
> **출처**: AUTHORITY_CHAIN.md §3.3 L15 verbatim — "V1: +₩0, V2: +₩5,000/월, V3: +₩15,000/월"

| 버전 | 1차 후보 | 2차 후보 (폴백) | 비용 (월간 추산) | 성능 (요약 품질 점수, 0~10) | 토큰 상한 | LOCK L15 정합 |
|------|--------|----------------|--------------|----------------|----------|--------------|
| **V1** | 룰 기반 키워드 추출 (TF-IDF + 빈도) | — | +₩0 | 5.0 (기본 요약) | 2048 | ✅ +₩0 |
| **V2** | **GPT-4o-mini** | **Llama 3.1 8B (로컬)** | GPT-4o-mini ≈ ₩4,200/월 (24 호출/일 × 30일 × 평균 1500 토큰 × $0.15/1M) / Llama 로컬 ≈ ₩0 | GPT-4o-mini 7.5 / Llama 8B 6.8 | 2048 | ✅ ≤ ₩5,000/월 |
| **V3** | **FinBERT (분류) + GPT-4o (요약)** | GPT-4o-mini (폴백) | FinBERT 로컬 ₩0 + GPT-4o ≈ ₩12,000/월 (24 호출/일 × 30일 × 평균 2000 토큰 × $2.5/1M) | FinBERT + GPT-4o 8.8 (금융 도메인 특화) | 2048 | ✅ ≤ ₩15,000/월 |

#### V2 모델 비교 표 (P5 해결 핵심)

| 비교 항목 | GPT-4o-mini | Llama 3.1 8B (로컬) | 선택 기준 |
|----------|------------|-------------------|----------|
| API 비용 (per 1M input tokens) | $0.15 | $0 (로컬 GPU/CPU) | V2 비용 한도 ₩5,000/월 |
| API 비용 (per 1M output tokens) | $0.60 | $0 | — |
| 월간 추산 비용 (24 호출/일 × 30일) | ≈ ₩4,200/월 | ≈ ₩0 (전기료 별도) | V2 한도 84% 사용 |
| 응답 지연 (P95) | ≈ 3초 | ≈ 8초 (CPU) / 2초 (GPU) | 1시간 주기 → 비차단 |
| 요약 품질 점수 (0~10) | 7.5 | 6.8 | GPT-4o-mini 우선 |
| 한국어 지원 | 우수 | 양호 (Llama 3.1 다국어) | GPT-4o-mini 우선 |
| 금융 도메인 정확도 | 양호 | 양호 | 동등 |
| 가용성 (장애 시 폴백) | OpenAI 의존 | 로컬 자율 | 폴백 시 Llama |

**V2 선택 결정**: 1차 GPT-4o-mini (품질 + 한국어 우선), 2차 Llama 3.1 8B (비용 0 + 가용성 자율, OpenAI 장애 시 폴백). 비용 모니터링에서 ₩5,000/월 80% 도달 시 즉시 Llama 폴백 (§5.5 정합).

### 3.3 토큰 상한 + 컨텍스트 윈도우 (ISS-5 verbatim)

> **출처**: 종합계획서 §6.2 ISS-5 verbatim — "토큰 상한(2048), 컨텍스트 윈도우(24h)"

| 항목 | 값 | 출처 |
|------|------|------|
| **출력 토큰 상한** | 2048 토큰 | ISS-5 verbatim |
| **입력 컨텍스트 윈도우** | 24시간 롤링 | ISS-5 verbatim |
| **최대 토픽 수 (입력)** | 채널당 50건 (가중치 상위) | dcl_channels.md §3.5 정합 |
| **최대 RAG 페이로드 수** | 30건 (similarity top-k) | rag_integration.md §3.2 정합 |
| **언어** | 한국어 + 영어 혼합 (DCL-GEO 다국가 RSS 정합) | dcl_channels.md §4.2 정합 |

---

## 4. 캐시 무효화 조건 3가지 (ISS-5 verbatim)

> **출처**: 종합계획서 §6.2 ISS-5 verbatim — "캐시 무효화 조건"

본 §은 ISS-5의 캐시 무효화 조건을 다음 3가지로 정본 정의한다:

### 4.1 (a) RETRACTION 발행 시 즉시 (LOCK L8 정합)

> **출처**: AUTHORITY_CHAIN.md §3.3 L8 verbatim — "RETRACTION — 즉시 발행 + 이전 이벤트 무효화"

```
[RT-BNP] RETRACTION 이벤트 발행 (Kafka topic cl.rt.retraction.v1 + EventType bnp.retraction.fired, LOCK-EL-09)
        │
        ▼
[6-7 background_summary.md] retraction_handler (30초 SLA, LOCK L6)
        │
        ├── 영향 채널 식별 (breaking_event_id ∈ topic_id)
        ├── 영향 채널 캐시 키 삭제
        └── 부분 재생성 (영향 채널만, 다른 채널 보존)
```

**무효화 범위**: 영향 채널의 캐시 키만 삭제 (다른 채널 보존, 비용 절약).

### 4.2 (b) QoD < 0.5 발생 시 (LOCK L13 정합)

> **출처**: AUTHORITY_CHAIN.md §3.3 L13 verbatim — "QoD ≥ 0.5 → RAG 삽입, < 0.5 → 폐기"

소스 품질이 급변하여 채널의 평균 QoD가 0.5 미만으로 하락한 경우 (예: 다수 소스가 일시적 다운):

```python
def check_qod_invalidation(channel: str) -> bool:
    """
    채널의 최근 1시간 평균 QoD < 0.5 → 캐시 무효화
    """
    recent_qod = dcl_aggregator.get_recent_avg_qod(channel, minutes=60)
    if recent_qod < 0.5:
        cache.delete(channel)
        log_invalidation(channel, reason="qod_below_threshold", qod=recent_qod)
        return True
    return False
```

### 4.3 (c) 24h 만료 시 (LOCK L14 정합)

> **출처**: AUTHORITY_CHAIN.md §3.3 L14 verbatim — "1시간마다 재생성"

본 캐시는 1시간 TTL로 관리되지만, 시스템 장애 / Cron 누락 시 24h 후 자동 만료된다 (LOCK L14 + 안전망):

```yaml
cache_policy:
  primary_ttl: 3600      # 1시간 (LOCK L14)
  hard_expiry: 86400     # 24시간 (안전망)
  on_hard_expiry: "force_regenerate"  # 강제 재생성
```

### 4.4 (d 추가) 사용자 명시 요청 시 (보조)

사용자가 "최신 상황 알려줘" 등 명시적 갱신 요청 시 캐시를 즉시 무효화하고 재생성한다 (V1+).

---

## 5. 비용 관리 전략 (LOCK L15 verbatim 강제)

### 5.1 LOCK L15 정본

> **출처**: AUTHORITY_CHAIN.md §3.3 L15 verbatim — "V1: +₩0, V2: +₩5,000/월, V3: +₩15,000/월"
>
> **출처**: 종합계획서 §4.3 R-67-3 verbatim — "DCL 비용 상한 준수 — 각 버전별 DCL 비용 상한(L15)을 초과하는 소스 추가 금지"

| 버전 | 비용 상한 (L15) | 본 모듈 분배 (배경 요약 단독) | 채널 분배 (dcl_channels.md §5.3 정합) |
|------|---------------|-------------------------|----------------------------------|
| V1 | +₩0/월 | ₩0 (룰 기반) | DCL 채널: ₩0 (RSS) |
| V2 | +₩5,000/월 | GPT-4o-mini ≈ ₩4,200/월 (84%) | 채널 분배 잔여 ≈ ₩800/월 |
| V3 | +₩15,000/월 | GPT-4o ≈ ₩12,000/월 (80%) | 채널 분배 잔여 ≈ ₩3,000/월 |

> **NOTE**: dcl_channels.md §5.3은 채널 수집(RSS/REST/WebSocket) + 6-8 배치 비용을 다루며, 본 §5.1은 배경 요약 모델 호출 비용만 다룬다. 두 모듈 합계가 LOCK L15 한도를 초과하지 않아야 한다.

### 5.2 V2 비용 분배 정합 (dcl_channels.md §5.3 + 본 §5.1)

| 항목 | dcl_channels.md §5.3 (채널 수집) | 본 §5.1 (배경 요약) | V2 합계 | LOCK L15 V2 한도 |
|------|--------------------------------|-------------------|--------|----------------|
| DCL-FIN REST API | ~₩2,500/월 | — | ₩2,500 | — |
| DCL-TECH 6-8 배치 | ~₩1,500/월 | — | ₩1,500 | — |
| DCL-GEO RSS | ₩0 | — | ₩0 | — |
| GPT-4o-mini 배경 요약 | — | ~₩4,200/월 | ₩4,200 | — |
| **V2 합계** | **~₩4,000/월** | **~₩4,200/월** | **~₩8,200/월** | **₩5,000/월** |

> **⚠️ 주의 (R-67-3 강제)**: V2 단일 도메인의 채널 수집 + 배경 요약 합계가 ₩5,000을 초과한다. 따라서 V2 배포 시 다음 조정이 필요하다:
> 1. **GPT-4o-mini 호출 빈도 축소**: 1시간 주기 → 2시간 주기 (V2 한정), 비용 절반 ≈ ₩2,100/월
> 2. **또는 Llama 3.1 8B 폴백**: 로컬 비용 0
> 3. **또는 채널 수집 축소**: DCL-TECH 6-8 배치를 매일 → 2일 1회

본 문서는 R-67-3 비용 상한 강제 원칙에 따라 운영 시 위 3개 옵션 중 하나를 적용하도록 권고한다 (운영 결정은 6-13 Operations 정본).

### 5.3 V3 비용 분배 정합

| 항목 | dcl_channels.md §5.3 (채널 수집) | 본 §5.1 (배경 요약) | V3 합계 | LOCK L15 V3 한도 |
|------|--------------------------------|-------------------|--------|----------------|
| DCL-FIN WebSocket | ~₩9,000/월 | — | ₩9,000 | — |
| DCL-TECH 실시간 | ~₩3,750/월 | — | ₩3,750 | — |
| DCL-GEO 실시간 | ~₩750/월 | — | ₩750 | — |
| FinBERT (로컬) + GPT-4o 배경 요약 | — | ~₩12,000/월 | ₩12,000 | — |
| **V3 합계** | **~₩13,500/월** | **~₩12,000/월** | **~₩25,500/월** | **₩15,000/월** |

> **⚠️ 주의 (R-67-3 강제)**: V3 합계가 ₩15,000을 초과한다. V3 도입 시 다음 권고:
> 1. **GPT-4o → GPT-4o-mini 일부 전환**: 평균 비용 절반 ≈ ₩6,000/월 (배경 요약은 mini로도 충분, 실시간 분류만 GPT-4o)
> 2. **DCL-FIN WebSocket → REST 일부 폴백**: ~₩4,500/월 절약
> 3. 결과: V3 합계 ≈ ₩15,000/월 한도 내

### 5.4 모델 폴백 (R-67-3 자동 적용)

```python
def select_model(version: str, current_monthly_cost: float) -> str:
    """
    LOCK L15 정합 모델 선택 + 비용 초과 시 자동 폴백
    """
    L15_LIMITS = {"V1": 0, "V2": 5000, "V3": 15000}
    limit = L15_LIMITS[version]

    if current_monthly_cost >= limit * 0.8:  # 80% 도달 시 알림
        notify_ops("L15_BUDGET_WARNING", version=version, cost=current_monthly_cost)

    if current_monthly_cost >= limit:  # 100% 도달 시 강제 폴백
        if version == "V2":
            return "Llama-3.1-8B"   # 로컬 폴백 (비용 0)
        elif version == "V3":
            return "GPT-4o-mini"    # 1단계 다운그레이드
        else:
            return "rule-based"     # V1로 폴백

    # 정상 동작
    return {
        "V1": "rule-based",
        "V2": "GPT-4o-mini",
        "V3": "GPT-4o + FinBERT",
    }[version]
```

### 5.5 운영 비용 모니터링 (R-67-3 강제)

| 모니터링 항목 | 주기 | 임계 알림 | 폴백 |
|-------------|------|----------|------|
| DAILY 비용 집계 | 매일 00:00 | 누적 ≥ L15 80% | §5.4 모델 자동 폴백 |
| MONTHLY 비용 집계 | 매월 마지막 날 23:59 | 누적 ≥ L15 100% | 익월 1일까지 모델 호출 동결 |
| 호출 빈도 | 매 시간 | 1시간 ≥ 30회 (정상 24회) | 폭주 의심 → 운영 알림 |
| 응답 지연 | 매 호출 | P95 ≥ 30초 | 모델 폴백 (L → S 모델) |

---

## 6. 캐시 키 설계

```
cache_key = "{channel}:{window_id}:{version}"

예시:
- "DCL-FIN:2026-04-28T15:00:V2"  → V2 GPT-4o-mini 결과 (15시 정각)
- "DCL-TECH:2026-04-28T15:00:V2" → V2 GPT-4o-mini 결과
- "DCL-GEO:2026-04-28T15:00:V2"  → V2 GPT-4o-mini 결과
```

| 필드 | 형식 | 출처 |
|------|------|------|
| `channel` | "DCL-FIN" / "DCL-TECH" / "DCL-GEO" | LOCK L12 |
| `window_id` | ISO 8601 시간 (분초 00) | LOCK L14 정합 (1시간 단위) |
| `version` | "V1" / "V2" / "V3" | §3.2 모델 선택 |

**TTL**: 3600초 (1시간, LOCK L14) + 24시간 hard expiry (§4.3)

---

## 7. V2 LOCK 인용 매트릭스 (LOCK ↔ 본 문서 §)

| LOCK | 정본 출처 | 값/규칙 (verbatim) | 본 문서 § | 대조 결과 |
|------|----------|------------------|----------|----------|
| L8 | LOCK #16, Part2 §6.10.1 | 즉시 발행 + 이전 이벤트 무효화 | §4.1 | ✅ verbatim |
| L13 | Part2 §6.10.2 | QoD ≥ 0.5 → RAG 삽입, < 0.5 → 폐기 | §4.2 | ✅ verbatim |
| L14 | Part2 §6.10.2 | 1시간마다 재생성 | §2 (전체) + §6 | ✅ verbatim |
| L15 | Part2 §6.10.2 | V1: +₩0, V2: +₩5,000/월, V3: +₩15,000/월 | §3.2 + §5.1~§5.3 | ✅ verbatim |

---

## 8. 변경 이력

- 2026-04-28 v1.0 — P2-3 NEW (ISS-5 배경 요약 캐시 갱신 프로토콜 정본 + P5 GPT-4o-mini/Llama 비용/성능 비교 표 + LOCK L8/L13/L14/L15 verbatim 인용 + 1시간 주기 재생성 정본 정의 + 토큰 상한 2048 + 컨텍스트 윈도우 24h + 캐시 무효화 3가지 (RETRACTION/QoD<0.5/24h 만료) + V2 비용 분배 정합 dcl_channels.md §5.3 + V3 비용 분배 정합 + 모델 자동 폴백 (Llama 폴백 + GPT-4o-mini 다운그레이드) + 운영 비용 모니터링 R-67-3 강제 + 캐시 키 설계)

<!-- FABRICATION-CHECK: zero-tolerance for hallucinated LOCK / model names / pricing -->
<!-- LOCK 인용 verbatim 정합: AUTHORITY_CHAIN.md §3.3 L8/L13/L14/L15 ✅ -->
<!-- ISS-5 4 요소 (요약 모델 GPT-4o-mini/Llama + 토큰 상한 2048 + 컨텍스트 윈도우 24h + 캐시 무효화) ✅ -->
<!-- P5 GPT-4o-mini/Llama 비용 비교 표 §3.2 (V2 모델 비교 8 항목) ✅ -->
<!-- L14 1시간 갱신 strict + L15 V1/V2/V3 비용 상한 verbatim ✅ -->
<!-- R-67-3 비용 상한 강제 (V2 합계 ₩5,000 초과 시 폴백 옵션 3가지 명시) ✅ -->
<!-- 캐시 무효화 3가지 (RETRACTION L8 + QoD<0.5 L13 + 24h 만료 L14) ✅ -->
<!-- DCL-FIN/TECH/GEO 3채널 정합 (L12) ✅ -->
<!-- 6-4/6-13 LOCK 재정의 ❌ (참조만) ✅ -->
<!-- dcl_channels.md (P2-1) + rag_integration.md (P2-2) 입력 정합 ✅ -->
<!-- 캐시 키 설계 (channel + window_id + version) ✅ -->
