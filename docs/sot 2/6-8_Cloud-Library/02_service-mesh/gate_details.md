# gate_details.md — CL-G0~CL-G4 Gate 구현 로직 + 임계값 + Fast Gate

> **도메인**: 6-8_Cloud-Library / 02_service-mesh
> **역할**: CL-G0~CL-G4 각 Gate의 판정 알고리즘 · 임계값 · 실패 처리 + Fast Gate(6-7 RT-BNP-DCL 공유) 상세
> **수정 정책**: 정본 — Phase 변경 시 갱신
> **생성일**: 2026-04-28 (P2-1, STAGE 7 STEP_B)
> **변경 이력 태그**: V2-Phase 2
> **정본 참조**: CLOUD_LIBRARY_SPEC §8 (G0-G4 정의 정본 LOCK L4~L8) + Part2 §6.10 (Phase 배정 + Gate ID L22) + AUTHORITY_CHAIN.md §3 (LOCK L4~L8, L19/L20, L22)
> **ISS-4 해결**: 5-Gate 검증 로직 (CL-G0~G4 판정 알고리즘 + 임계값 + V1/V2/V3 단계별 구현)

---

## §1. 교차 참조 블록

| 정본 문서 | 섹션 | 참조 항목 |
|----------|------|----------|
| `D:\VAMOS\docs\sot\VAMOS_CLOUD_LIBRARY_SPEC.md` | §5 + §8 | 평가 4카테고리 100점 만점 (L2) + G0-G4 Gate 정의 (L4~L8) |
| `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` | §6.10 CC-004 | Gate ID 접두어 CL- 필수 (L22) — VAMOS 5-Gate 혼동 방지 |
| `../AUTHORITY_CHAIN.md` | §3 LOCK 레지스트리 | L4 (CL-G0) / L5 (CL-G1 ≥40) / L6 (CL-G2 ≥50) / L7 (CL-G3 ≥30) / L8 (CL-G4 ≥60) / L19 (Quality 최소 40) / L20 (Consistency 최소 50) / L22 (Gate ID 접두어) |
| `./_index.md` | §1 / §2 / §5 | CL-G0~G4 Gate 전체 목록 + V1 Gate 구현 범위 + LOCK 참조 매핑 |
| `../01_cloud-deploy/scoring_system.md` | §5.2 / §5.3 / §8 | 판단 대역(AUTO/NOTIFY/MANUAL/BLOCK) 경계 + Quality 25점→100점 환산식 + SCORE_BORDERLINE EscalationPayload (P1-2 BORDERLINE_NOTE 이월) |
| `../01_cloud-deploy/layer_pipeline.md` | §L8 VALIDATION + §5 | Gate 호출 인터페이스 + EvaluationScore Pydantic 공통 자료 구조 |
| `../01_cloud-deploy/deployment_strategy.md` | §7 | LOCK 운영 제약 (L9/L10/L13/L17/L21) 배포 환경별 Gate 실행 조건 |
| `../CLOUD_LIBRARY_구조화_종합계획서.md` | §6.2 ISS-4 + §3.4 + §A.2 | ISS-4 해결 큐 + LOCK L4~L8/L22 + G0-G4 Gate System 다이어그램 |

---

## §2. LOCK 레지스트리 인용 (AUTHORITY §3 5-field verbatim)

| LOCK ID | 명칭 | 정본 출처 | 값/규칙 (verbatim) | 본 문서 인용 결과 |
|---------|------|----------|------------------|-----------------|
| **L2** | 평가 점수 4카테고리 배점 | CLOUD_LIBRARY_SPEC | Trust(25) + Relevance(30) + Quality(25) + Access(20) = 100 | §3 CL-G1 4카테고리 가중 합산 인용 일치 |
| **L4** | CL-G0 Format/Validation Gate | CLOUD_LIBRARY_SPEC §8 | URL 유효 + robots.txt 허용. 실패 → 즉시 거부 | §3 CL-G0 §3.1 본 문서 상세 인용 일치 |
| **L5** | CL-G1 Content Quality Gate | CLOUD_LIBRARY_SPEC §8 | Quality ≥ 40/100. 실패 → 수집 거부 | §3 CL-G1 §3.2 본 문서 상세 인용 일치 |
| **L6** | CL-G2 Consistency Gate | CLOUD_LIBRARY_SPEC §8 | Consistency ≥ 50/100. 실패 → 우선순위 강등 | §3 CL-G2 §3.3 본 문서 상세 인용 일치 |
| **L7** | CL-G3 Security Gate | CLOUD_LIBRARY_SPEC §8 | 악성 URL/허위 정보 필터 (Score ≥ 30). 실패 → 수집 중단 | §3 CL-G3 §3.4 본 문서 상세 인용 일치 |
| **L8** | CL-G4 Final Gate | CLOUD_LIBRARY_SPEC §8 | 종합 점수 ≥ 60/100. 실패 → 아카이브만 | §3 CL-G4 §3.5 본 문서 상세 인용 일치 |
| **L19** | Content Quality Score 최소 | SPEC §16.11 | 40/100 (CL-G1과 일치) | §3.2 임계값 정합 인용 일치 |
| **L20** | Consistency Score 최소 | SPEC §16.12 | 50/100 (CL-G2와 일치) | §3.3 임계값 정합 인용 일치 |
| **L22** | Gate ID 접두어 | Part2 §6.10 CC-004 | CL-G0~CL-G4 (VAMOS 5-Gate 혼동 방지) | §3 모든 Gate 명칭 CL- 접두어 verbatim 적용 (R-68-2) |

> **R-68-1 준수**: 본 문서는 L4~L8/L19/L20/L22 정본 출처가 유일 권한이며, 값 변경 0건. 정본 갱신 후에만 반영한다.
> **R-68-2 준수**: 모든 Gate 명칭 CL- 접두어 verbatim 적용 (VAMOS 5-Gate 혼동 방지).
> **R-68-5 준수**: §4 Fast Gate는 6-7 RT-BNP-DCL 범위 경계 내 read-only 인용 (재정의 ❌, 6-7 LOCK L1~L18 read-only).

---

## §3. CL-G0~CL-G4 Gate 순차 실행 흐름

### §3.0 전체 흐름도

```
[소스 데이터]
     │
     ▼
[CL-G0 Format/Validation] ── FAIL ──▶ [즉시 거부 — 파이프라인 진입 불가]
     │
     PASS
     ▼
[CL-G1 Content Quality]    ── FAIL ──▶ [수집 거부 — 최소 품질 미달 차단]
     │
     PASS (Quality ≥ 40)
     ▼
[CL-G2 Consistency]        ── FAIL ──▶ [우선순위 강등 — 아카이브 저장]
     │
     PASS (Consistency ≥ 50)
     ▼
[CL-G3 Security]           ── FAIL ──▶ [수집 중단 — 보안 위험 즉시 차단 + 알림]
     │
     PASS (Security ≥ 30)
     ▼
[CL-G4 Final]              ── FAIL ──▶ [아카이브만 — 활용 불가]
     │
     PASS (종합 ≥ 60)
     ▼
[자동 임베딩 생성 → I-2 VectorStore 인덱싱 (SPEC §8.7)]
```

### §3.0.1 순차 실행 규칙 (LOCK invariant)

- 각 Gate는 **순차 실행** — 앞 Gate 실패 시 후속 Gate 스킵 (성능 + 비용 절감)
- CL-G0 / CL-G1 / CL-G3 실패 → **거부** (수집 자체 차단)
- CL-G2 실패 → **강등** (수집 허용, 우선순위 하락, 아카이브 저장)
- CL-G4 실패 → **아카이브만** (활용 불가, 참고 보관만 허용)
- CL-G4 통과 → 자동 임베딩 생성 → I-2 VectorStore 삽입 (SPEC §8.7)
- **action 규약 (LOCK invariant)**: `passed=False` 는 항상 비-PROCEED 처분을 의미한다 — G0/G1/G3 reject = `action="REJECT"`, G2 강등 = `action="DEMOTE"`, G4 미달 = `action="ARCHIVE_ONLY"`. `action` 미지정 reject 반환은 `REJECT` 로 해석한다 (기본값 `PROCEED` 는 `passed=True` 에만 유효).
- **action 규약 (LOCK invariant)**: `passed=False` 는 항상 비-PROCEED 처분을 의미한다 — G0/G1/G3 reject = `action="REJECT"`, G2 강등 = `action="DEMOTE"`, G4 미달 = `action="ARCHIVE_ONLY"`. `action` 미지정 reject 반환은 `REJECT` 로 해석한다 (기본값 `PROCEED` 는 `passed=True` 에만 유효).

### §3.1 CL-G0 Format/Validation Gate

> **LOCK 정본**: L4 (CLOUD_LIBRARY_SPEC §8) — `URL 유효 + robots.txt 허용. 실패 → 즉시 거부`
> **LOCK 운영 제약**: L10 (크롤링 간격 ≥1초/도메인 robots.txt 준수)

#### §3.1.1 판정 기준

- **입력**: 후보 URL + (선택) 도메인 robots.txt 캐시
- **검증 항목** (이진 판정, AND 결합):
  1. URL 형식 유효성 — RFC 3986 정규식 일치 (scheme=`http(s)`, host 정상, path 인코딩)
  2. URL 길이 ≤ 2,048 char (서버 호환성)
  3. 호스트 도메인 DNS 해석 성공
  4. robots.txt 정책 허용 — User-Agent="VAMOSBot" 기준 `Allow`/`Disallow` 매칭
  5. 도메인 차단 리스트 미포함 (관리자 정의 blacklist)

#### §3.1.2 V1 알고리즘 (의사코드, Big-O O(1))

```python
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

def cl_g0_validate(url: str, blacklist: set[str]) -> GateResult:
    # 1. URL 형식
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return GateResult(passed=False, reason="INVALID_URL_FORMAT", code="G0_FORMAT_FAIL")
    if len(url) > 2048:
        return GateResult(passed=False, reason="URL_TOO_LONG", code="G0_LENGTH_FAIL")

    # 2. blacklist
    if parsed.netloc in blacklist:
        return GateResult(passed=False, reason="DOMAIN_BLACKLISTED", code="G0_BLACKLIST_FAIL")

    # 3. robots.txt (캐시 TTL=L13 24h)
    rp = RobotFileParser()
    rp.set_url(f"{parsed.scheme}://{parsed.netloc}/robots.txt")
    try:
        rp.read()  # network call (cached per L13)
    except Exception:
        return GateResult(passed=False, reason="ROBOTS_FETCH_FAIL", code="G0_ROBOTS_FAIL")

    if not rp.can_fetch("VAMOSBot", url):
        return GateResult(passed=False, reason="ROBOTS_DISALLOW", code="G0_ROBOTS_DENY")

    return GateResult(passed=True, reason="OK", code=None)
```

#### §3.1.3 V2/V3 확장

| Phase | 확장 | 설명 |
|-------|------|------|
| **V1** | URL validator + `urllib.robotparser` | 단순 정규식 + 표준 라이브러리 |
| **V2** | 고급 URL 정규화 + 리다이렉트 추적 | `tldextract` + 301/302 chain ≤ 5 hops + canonical URL |
| **V3** | 실시간 robots.txt 캐시 갱신 | webhook 기반 무효화 + edge worker 분산 캐시 |

#### §3.1.4 실패 처리

- 즉시 거부 — 파이프라인 진입 불가, 후속 Gate 실행 0
- FailureCode 5종: `G0_FORMAT_FAIL` / `G0_LENGTH_FAIL` / `G0_BLACKLIST_FAIL` / `G0_ROBOTS_FAIL` / `G0_ROBOTS_DENY` (→ `error_fallback.md` FailureCodeRegistry §3 매핑)
- 로깅: `cl.rt.gate.g0_reject` 이벤트 발행 (6-12 Event-Logging cl.rt.* 네임스페이스)

---

### §3.2 CL-G1 Content Quality Gate

> **LOCK 정본**: L5 (SPEC §8) — `Quality ≥ 40/100. 실패 → 수집 거부` + L19 (SPEC §16.11) — `40/100 (CL-G1과 일치)`
> **LOCK 의존**: L2 (4카테고리 배점) + L3 (소스 신뢰도 가중치)

#### §3.2.1 판정 기준 — 4카테고리 가중 합산 (L2 verbatim)

```
Quality_Score = Trust(25) + Relevance(30) + Quality(25) + Access(20) = 100
```

| 카테고리 | 배점 | 세부 항목 | 정본 출처 |
|---------|------|----------|----------|
| **Trust** | 25 | 도메인 신뢰도 (소스 가중치 L3) + HTTPS 사용 + SSL 인증서 유효 | SPEC §5.1 |
| **Relevance** | 30 | 시드 키워드 매칭 점수 + 코사인 유사도 (BGE-M3 L15 batch=32) + 카테고리 적합성 | SPEC §5.2 |
| **Quality** | 25 | 콘텐츠 길이 (≥ 500 char) + 구조화 (heading/list 비율) + 메타데이터 완전성 | SPEC §5.3 |
| **Access** | 20 | 응답 속도 (TTFB ≤ 2초) + 가용성 (uptime ≥ 99%) + 다국어 지원 | SPEC §5.4 |

**임계값**: Quality_Score ≥ 40/100 → PASS / Quality_Score < 40 → FAIL (L19 정합)

#### §3.2.2 V1 알고리즘 (의사코드, Big-O O(n) for content length n)

```python
def cl_g1_quality(source: SiteEvaluation, weights: dict[str, float]) -> GateResult:
    # weights = LOCK L3 소스 신뢰도 가중치 (공식=1.0, 학술=0.9, 기술 문서=0.85, ..., SNS=0.3)
    trust = compute_trust(source, weights)        # 0~25
    relevance = compute_relevance(source)          # 0~30
    quality = compute_content_quality(source)      # 0~25
    access = compute_access(source)                # 0~20
    score = trust + relevance + quality + access   # 0~100 (L2 verbatim)

    if score < 40:  # L5/L19 임계값
        return GateResult(
            passed=False,
            reason="QUALITY_BELOW_THRESHOLD",
            code="G1_QUALITY_LOW",
            score=score,
            breakdown={"trust": trust, "relevance": relevance, "quality": quality, "access": access},
        )
    return GateResult(passed=True, reason="OK", code=None, score=score)
```

#### §3.2.3 V2/V3 확장

| Phase | 확장 | 설명 |
|-------|------|------|
| **V1** | 규칙 기반 점수 산출 | 정규식 + 키워드 매칭 + 휴리스틱 |
| **V2** | Semantic Router + LLM 기반 품질 평가 (GPT-4o mini) | LLM 평가자 + few-shot prompt + JSON 응답 검증 |
| **V3** | 완전 자율 품질 진화 | I-21 Source Evolution 연동 + 자기 진화 평가 |

#### §3.2.4 실패 처리

- 수집 거부 — 최소 품질 미달 소스 차단 (저장조차 ❌)
- FailureCode: `G1_QUALITY_LOW` (→ `error_fallback.md` FailureCodeRegistry §4 매핑)
- 경계값 처리: §5 Borderline 정책 참조 (39 ≤ score < 40 → AUTO BLOCK / 79 ≤ score < 80 → NOTIFY 대역 split)

---

### §3.3 CL-G2 Consistency Gate

> **LOCK 정본**: L6 (SPEC §8) — `Consistency ≥ 50/100. 실패 → 우선순위 강등` + L20 (SPEC §16.12) — `50/100 (CL-G2와 일치)`
> **CONFLICT 보존**: CL-C002 (SC-14) — 원본 Part2="Relevance" vs SPEC="Consistency", **Consistency 채택** (FIX-09 RESOLVED 보존)

#### §3.3.1 판정 기준 — 교차 소스 일관성

- **입력**: 후보 소스 + 기존 수집 소스 풀 (최근 30일, 동일 카테고리)
- **검증 항목**:
  1. 시맨틱 일관성 — 후보 임베딩 vs 기존 풀 평균 임베딩 코사인 유사도 (L15 batch=32)
  2. 사실 일관성 — 핵심 entity (인물/날짜/수치) 다수결 검증
  3. 카테고리 일관성 — 분류 라벨 매핑 정확도
  4. 중복도 — 기존 소스와 SHA-256 hash 100% 일치 시 reject (L9 VERSION CONTROL 연동)

**임계값**: Consistency_Score ≥ 50/100 → PASS / Consistency_Score < 50 → 우선순위 강등

#### §3.3.2 V1 알고리즘 (의사코드, Big-O O(k log k) where k=existing pool size)

```python
def cl_g2_consistency(candidate: ExtractedText, pool: list[StoredContent]) -> GateResult:
    # 1. 중복 제거 (해시 기반)
    if any(p.content_hash == candidate.content_hash for p in pool):
        return GateResult(passed=False, reason="DUPLICATE", code="G2_DUPLICATE", score=0, action="REJECT")  # 중복=하드 거부 (error_fallback §4.2.4 FB-X, 저장 ❌)

    # 2. 시맨틱 일관성 (BGE-M3, L15 batch=32)
    cand_emb = embed(candidate.text)             # 1024-dim
    pool_emb_avg = mean([embed(p.text) for p in pool[-100:]])
    semantic_score = cosine_sim(cand_emb, pool_emb_avg) * 50  # 0~50

    # 3. 사실 일관성
    cand_entities = extract_ner(candidate.text)
    pool_entities = aggregate_entities(pool)
    factual_score = entity_consistency(cand_entities, pool_entities) * 30  # 0~30

    # 4. 카테고리 일관성
    category_score = category_match(candidate.category, pool) * 20  # 0~20

    score = semantic_score + factual_score + category_score  # 0~100

    if score < 50:  # L6/L20 임계값
        return GateResult(
            passed=False,
            reason="CONSISTENCY_BELOW_THRESHOLD",
            code="G2_CONSISTENCY_LOW",
            score=score,
            action="DEMOTE",  # 강등 (거부가 아님!)
        )
    return GateResult(passed=True, reason="OK", code=None, score=score)
```

#### §3.3.3 V2/V3 확장

| Phase | 확장 | 설명 |
|-------|------|------|
| **V1** | 키워드 매칭 기반 일관성 체크 | TF-IDF + 키워드 빈도 |
| **V2** | LLM 시맨틱 교차 검증 | GPT-4o mini + Chain-of-Thought 비교 |
| **V3** | 자율 일관성 분석 | 자기 진화 일관성 평가 + 자율 카테고리 진화 |

#### §3.3.4 실패 처리

- **우선순위 강등** (거부가 아님!) — 수집은 허용, 활용 순위 하락, 아카이브 저장
- FailureCode: `G2_DUPLICATE` / `G2_CONSISTENCY_LOW` (→ `error_fallback.md` FailureCodeRegistry §5 매핑)
- 로깅: `cl.rt.gate.g2_demote` 이벤트 발행

---

### §3.4 CL-G3 Security Gate

> **LOCK 정본**: L7 (SPEC §8) — `악성 URL/허위 정보 필터 (Score ≥ 30). 실패 → 수집 중단`

#### §3.4.1 판정 기준

- **입력**: 후보 URL + 추출된 텍스트
- **검증 항목**:
  1. 악성 URL DB 조회 — Google Safe Browsing API + PhishTank + 자체 BL DB
  2. 허위 정보 탐지 — 패턴 매칭 (V1) / ML 분류 (V2+)
  3. 민감 정보 필터링 — PII (주민번호/카드번호/전화번호) 정규식 + entity NER
  4. CSAM zero-tolerance — 이미지 hash 매칭 (NCMEC PhotoDNA), 1건이라도 발견 시 즉시 차단 + 운영자 보고
  5. 6-2 Security 정책 정합 — robots.txt 준수(L10) + 악성 URL 차단(C-3 보안 정책 API)

**임계값**: Security_Score ≥ 30/100 → PASS / Security_Score < 30 → 수집 중단

#### §3.4.2 V1 알고리즘 (의사코드, Big-O O(1) per check)

```python
def cl_g3_security(url: str, text: str, malware_db: SafeBrowsingClient) -> GateResult:
    # 1. CSAM zero-tolerance (이미지 첨부 시)
    if has_image(text) and csam_match(extract_images(text)):
        return GateResult(passed=False, reason="CSAM_DETECTED", code="G3_CSAM_BLOCK", score=0)

    # 2. 악성 URL
    if malware_db.lookup(url) == "MALICIOUS":
        return GateResult(passed=False, reason="MALICIOUS_URL", code="G3_MALWARE_BLOCK", score=0)

    # 3. PII 검출
    pii_count = count_pii(text)  # 정규식 + spaCy NER
    if pii_count > 5:
        return GateResult(passed=False, reason="PII_OVERFLOW", code="G3_PII_BLOCK", score=10)

    # 4. 허위 정보 패턴 (V1: 룰 기반)
    misinfo_score = misinformation_pattern_match(text)  # 0~100 (높을수록 의심)

    score = max(0, 100 - misinfo_score - (pii_count * 5))  # clamp 하한 0 (0~100 범위 보장)
    if score < 30:  # L7 임계값
        return GateResult(passed=False, reason="SECURITY_BELOW_THRESHOLD", code="G3_SECURITY_LOW", score=score)
    return GateResult(passed=True, reason="OK", code=None, score=score)
```

#### §3.4.3 V2/V3 확장

| Phase | 확장 | 설명 |
|-------|------|------|
| **V1** | 패턴 매칭 (Blacklist DB 조회) | 정규식 + Hash 기반 + 룰 기반 misinformation |
| **V2** | ML 기반 허위 정보 탐지 | BERT-base 분류기 + Fact-checking API 연동 |
| **V3** | 실시간 위협 인텔리전스 연동 | MITRE ATT&CK + STIX/TAXII 피드 |

#### §3.4.4 실패 처리

- 수집 중단 — 보안 위험 소스 즉시 차단 + 운영자 알림 (Slack/PagerDuty)
- FailureCode: `G3_CSAM_BLOCK` / `G3_MALWARE_BLOCK` / `G3_PII_BLOCK` / `G3_SECURITY_LOW` (→ `error_fallback.md` FailureCodeRegistry §6 매핑)
- CSAM 검출 시 NEVER_AUTO 경로 즉시 트리거 (`error_fallback.md` §6 NEVER_AUTO + 법적 보고 의무)
- 로깅: `cl.rt.gate.g3_block` 이벤트 + 6-2 Security 알람 발행

---

### §3.5 CL-G4 Final Gate

> **LOCK 정본**: L8 (SPEC §8) — `종합 점수 ≥ 60/100. 실패 → 아카이브만`

#### §3.5.1 판정 기준 — 종합 점수 (CL-G0~G3 통과 후)

```
Final_Score = α·CL-G1.score + β·CL-G2.score + γ·CL-G3.score
            = 0.4 · Quality + 0.3 · Consistency + 0.3 · Security
            (α=0.4, β=0.3, γ=0.3 — 가중치 정본 = SPEC §8.5)
```

**임계값**: Final_Score ≥ 60/100 → PASS / Final_Score < 60 → 아카이브만

#### §3.5.2 V1 알고리즘 (의사코드, Big-O O(1))

```python
def cl_g4_final(g1: GateResult, g2: GateResult, g3: GateResult) -> GateResult:
    final_score = 0.4 * g1.score + 0.3 * g2.score + 0.3 * g3.score  # 0~100

    if final_score < 60:  # L8 임계값
        return GateResult(
            passed=False,
            reason="FINAL_BELOW_THRESHOLD",
            code="G4_FINAL_LOW",
            score=final_score,
            action="ARCHIVE_ONLY",  # 아카이브만 (활용 불가)
        )

    return GateResult(passed=True, reason="OK", code=None, score=final_score)
```

#### §3.5.3 V2/V3 확장

| Phase | 확장 | 설명 |
|-------|------|------|
| **V1** | 규칙 기반 가중 합산 | α=0.4, β=0.3, γ=0.3 고정 |
| **V2** | ML 앙상블 종합 판정 | XGBoost + 앙상블 가중치 학습 |
| **V3** | 완전 자율 품질 진화 + 자동 임베딩 | I-21 + 자기 진화 가중치 + 임베딩 자동 |

#### §3.5.4 실패 처리

- **아카이브만** (활용 불가) — 데이터 보관, 검색 색인 ❌, 사용자 노출 ❌
- FailureCode: `G4_FINAL_LOW` (→ `error_fallback.md` FailureCodeRegistry §7 매핑)
- 로깅: `cl.rt.gate.g4_archive` 이벤트 발행

---

## §4. Fast Gate — 6-7 RT-BNP-DCL 공유 로직 (R-68-5 범위 경계)

> **정본**: Part2 §6.10.1 RT-BNP 파이프라인 (6-7 소관, R-68-5 범위 경계)
> **본 6-8 범위**: Gate API 공유 (CL-G0/G1/G3 인터페이스 인용 only) — 6-7 LOCK L1~L18 read-only, 재정의 ❌
> **W-1 정합**: SPEC 공유 6-7 ↔ 6-8 RESOLVED 보존, Gate LOCK 동기화 완료 (S6-7)

### §4.1 Fast Gate 적용 시나리오

- **트리거**: 속보 소스 (속보 RSS, T1/T2 사전 등록 신뢰 소스)
- **목적**: 30분 내 사용자 노출을 위한 검증 단순화
- **트레이드오프**: CL-G2 / CL-G4 건너뜀 → 사후 검증 (30분 내) 으로 보완

### §4.2 Gate 적용 매트릭스

| Gate | Fast Gate 적용 | 사유 | 사후 검증 |
|------|---------------|------|----------|
| **CL-G0** | **적용** (full) | URL 유효성은 모든 시나리오 필수 | — |
| **CL-G1** | **간소화** | T1/T2 사전 등록 소스 자동 통과 (Quality 기본 60 부여) | 30분 내 fully run CL-G1 + 점수 갱신 |
| **CL-G2** | **건너뜀** | 속보는 Impact 기준 적용, 키워드 매칭 부적합 | 30분 내 fully run CL-G2, 강등 시 retroactive demote |
| **CL-G3** | **적용** (full) | 악성 URL/허위 정보 필터 모든 시나리오 필수 | — |
| **CL-G4** | **건너뜀** | 속도 우선, 30분 내 사후 검증 대체 | 30분 내 CL-G4 evaluation, FAIL 시 archive 전환 |

### §4.3 Fast Gate 인터페이스 (BaseGate(ABC) 인터페이스 공유)

```python
from abc import ABC, abstractmethod

class BaseGate(ABC):
    """6-7 ↔ 6-8 공유 인터페이스 (W-1 RESOLVED 정합).
    6-8 = 인프라 운영 정본 / 6-7 = 데이터 흐름 활용 (read-only)."""

    @abstractmethod
    def evaluate(self, candidate: object) -> "GateResult":
        ...

    @abstractmethod
    def fast_evaluate(self, candidate: object, mode: str = "T1") -> "GateResult":
        """Fast Gate 모드 — 6-7 RT-BNP 호출 시 적용. 사후 검증 의무."""
        ...
```

> **R-68-5 경계 선언**: 본 §4는 6-8 = 인프라 운영 (Gate 로직 정본 CL-G0~G4) / 6-7 = 데이터 흐름 (RT-BNP 파이프라인 + DCL 채널) 분리. Fast Gate API 인터페이스만 공유, 6-7 LOCK L1~L18 read-only 인용 (재정의 ❌). RT-BNP/DCL 상세는 6-7 소관, 본 6-8은 인프라·Gate·배포만.

---

## §5. 경계값(Borderline) 정책 — P1-2 BORDERLINE_NOTE 이월 해소

> **이월 출처**: `../01_cloud-deploy/scoring_system.md` §5.2 (판단 대역 AUTO/NOTIFY/MANUAL/BLOCK) + §8 SCORE_BORDERLINE EscalationPayload (P1-2 이월 항목)
> **본 §5 책임**: float 경계 (79<x<80, 59<x<60, 39<x<40 등) floor/ceil/tie-break 정책 확정

### §5.1 판단 대역 정합 (scoring_system.md §5.2 인용)

| 대역 | 점수 범위 | 처리 | 연계 Gate |
|------|----------|------|----------|
| **AUTO** | ≥ 80 | 자동 통과 | CL-G4 통과 + 우선 노출 |
| **NOTIFY** | 60 ≤ score < 80 | 자동 통과 + 운영자 알림 | CL-G4 통과 |
| **MANUAL** | 30 ≤ score < 60 | 운영자 수동 검토 큐 | CL-G4 미통과, BORDERLINE 처리 |
| **BLOCK** | < 30 | 차단 | CL-G3 또는 CL-G4 FAIL |

### §5.2 float 경계 처리 정책 (확정)

| 경계 | 처리 정책 | 사유 |
|------|----------|------|
| **CL-G1 임계값 40** (L19) | `score < 40 → FAIL` (strict less-than). 39.99... → FAIL / 40.00 → PASS | floor 적용 + tie-break = strict less-than |
| **CL-G2 임계값 50** (L20) | `score < 50 → DEMOTE` (strict less-than). 49.99... → DEMOTE / 50.00 → PASS | floor 적용 + tie-break = strict less-than |
| **CL-G3 임계값 30** (L7) | `score < 30 → FAIL` (strict less-than) | floor 적용 |
| **CL-G4 임계값 60** (L8) | `score < 60 → ARCHIVE_ONLY`. 59.99... → ARCHIVE / 60.00 → PASS | floor 적용 |
| **AUTO 경계 80** | `score < 80 → NOTIFY 대역`. 79.99... → NOTIFY / 80.00 → AUTO | floor 적용 |
| **NOTIFY/MANUAL 경계 60** | CL-G4 임계값과 정합 (60 = MANUAL→NOTIFY 전환점) | 동일 정책 |
| **MANUAL/BLOCK 경계 30** | CL-G3 임계값과 정합 (30 = BLOCK→MANUAL 전환점) | 동일 정책 |

> **rationale**: strict less-than (floor) 정책은 LOCK L19/L20 verbatim "≥ 40" / "≥ 50" 동일 의미로, "임계값 도달 시 통과" 원칙 준수. tie-break 시 거부 우선 (안전 우선).

### §5.3 SCORE_BORDERLINE FailureCode 연계

> **정본**: `../01_cloud-deploy/scoring_system.md` §8 SCORE_BORDERLINE EscalationPayload

| FailureCode | 트리거 | EscalationPayload 필드 | 처리 |
|-------------|--------|----------------------|------|
| `SCORE_BORDERLINE_G1` | `38 ≤ score < 40` (G1 임계값 ±2) | `source_engine="cl_g1"`, `error_code="SCORE_BORDERLINE"`, `original_request={url, candidate}`, `partial_result={score, breakdown}`, `retry_count=0`, `timestamp=now()` | I-20 운영자 큐 |
| `SCORE_BORDERLINE_G2` | `48 ≤ score < 50` | 동일 패턴 (engine=`cl_g2`) | I-20 운영자 큐 (강등 결정 보류) |
| `SCORE_BORDERLINE_G3` | `28 ≤ score < 30` | 동일 패턴 (engine=`cl_g3`) | I-20 운영자 큐 |
| `SCORE_BORDERLINE_G4` | `58 ≤ score < 60` | 동일 패턴 (engine=`cl_g4`, partial_result 포함 `g1_score, g2_score, g3_score`) | I-20 운영자 큐 (활용 결정 보류) |

> **로깅 포맷 (R-01-7 structured JSON, 중첩 구조 + trace_id)**:
> ```json
> {
>   "error": {"code": "SCORE_BORDERLINE_G4", "msg": "Score 59.7 within ±2 of L8 threshold 60"},
>   "context": {"gate": "CL-G4", "url": "...", "score": 59.7, "components": {"g1": 70, "g2": 65, "g3": 35}},
>   "recovery": {"action": "ESCALATE_I20", "queue": "operator_review", "deadline": "+24h"},
>   "trace_id": "tr-2026-04-28-7f3a..."
> }
> ```

---

## §6. 경계값 테스트 케이스 (Phase 3 검증용 ≥ 8건)

| # | Gate | 입력 score | 기대 동작 | 사유 |
|---|------|-----------|----------|------|
| 1 | CL-G1 | 39.99 | FAIL (G1_QUALITY_LOW) | strict less-than (40 미만) |
| 2 | CL-G1 | 40.00 | PASS | 임계값 도달 |
| 3 | CL-G2 | 49.99 | DEMOTE (G2_CONSISTENCY_LOW) | strict less-than |
| 4 | CL-G2 | 50.00 | PASS | 임계값 도달 |
| 5 | CL-G3 | 29.99 | FAIL (G3_SECURITY_LOW) | strict less-than |
| 6 | CL-G3 | 30.00 | PASS | 임계값 도달 |
| 7 | CL-G4 | 59.99 | ARCHIVE_ONLY (G4_FINAL_LOW) | strict less-than |
| 8 | CL-G4 | 60.00 | PASS | 임계값 도달 |
| 9 | CL-G1 | 38.5 | FAIL + SCORE_BORDERLINE_G1 escalation | 임계값 -2 borderline |
| 10 | CL-G4 | 58.7 | ARCHIVE_ONLY + SCORE_BORDERLINE_G4 escalation | 임계값 -2 borderline |
| 11 | AUTO 대역 | 79.99 | NOTIFY (auto pass with alert) | NOTIFY 대역 진입 |
| 12 | AUTO 대역 | 80.00 | AUTO (full auto) | AUTO 대역 진입 |
| 13 | CL-G3 | 0 (CSAM detect) | G3_CSAM_BLOCK + NEVER_AUTO ESCALATE | zero-tolerance |
| 14 | CL-G2 | 100 (duplicate hash) | G2_DUPLICATE | content_hash collision |

> **Phase 3 시나리오 ≥ 10건 충족** (총 14건 작성, 표준 산출물 품질 §5 충족).

---

## §7. 공통 자료 구조 (Pydantic) — `EvaluationScore` + `GateResult`

> **정본 위치**: `../01_cloud-deploy/layer_pipeline.md` §5 EvaluationScore (Pydantic) — 본 §7은 인용 정합만.
> **본 §7 신규**: GateResult Pydantic dataclass — 모든 §3.* Gate 의 반환 타입 통일

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional

class GateResult(BaseModel):
    """CL-G0~CL-G4 Gate 통합 반환 타입 (본 §7 정본)."""
    passed: bool
    reason: str
    code: Optional[str] = None  # FailureCode (G0_FORMAT_FAIL 등)
    score: Optional[float] = None  # 0~100, CL-G0 제외 적용
    action: Literal["PROCEED", "REJECT", "DEMOTE", "ARCHIVE_ONLY", "ESCALATE_I20"] = "PROCEED"
    breakdown: Optional[dict[str, float]] = None  # 4카테고리 분해 (CL-G1)
    trace_id: Optional[str] = Field(default=None, description="R-01-7 trace_id 표준 준수 (게이트 호출자 주입)")
```

> **§8 인터페이스 cross-check** (산출물 품질 §8): `EvaluationScore` 는 `layer_pipeline.md` §5 정본 Pydantic 모델, `GateResult` 는 본 §7 신규. CL-G0~G4 알고리즘 의사코드는 모두 `GateResult` 반환 일치 (interface match 검증 PASS).

---

## §8. ABC 패턴 매핑 (산출물 품질 §6 + §9)

```python
class BaseGate(ABC):
    """Gate ABC — 모든 CL-G0~G4 인스턴스가 구현."""
    LOCK_ID: str  # L4~L8 중 하나
    THRESHOLD: float  # 임계값 (0 또는 30/40/50/60)

    @abstractmethod
    def evaluate(self, candidate: object) -> GateResult:
        ...

    @abstractmethod
    def fast_evaluate(self, candidate: object, mode: str = "T1") -> GateResult:
        """6-7 Fast Gate 호출용 (R-68-5 경계). CL-G0/G1/G3는 적용, G2/G4는 NotImplemented."""
        ...
```

| Gate Class | LOCK_ID | THRESHOLD | fast_evaluate |
|-----------|---------|-----------|---------------|
| `ClG0FormatGate` | L4 | 0 (이진) | full apply |
| `ClG1QualityGate` | L5 | 40 (L19) | 간소화 (T1/T2 자동 통과) |
| `ClG2ConsistencyGate` | L6 | 50 (L20) | NotImplemented (skip) |
| `ClG3SecurityGate` | L7 | 30 | full apply |
| `ClG4FinalGate` | L8 | 60 | NotImplemented (skip) |

> **시간복잡도 (Big-O)**: G0 O(1), G1 O(n) for content length n, G2 O(k log k) for pool k, G3 O(1) per check, G4 O(1).

---

## §9. 에러/폴백 연계 (cross-ref)

> **정본 위치**: `./error_fallback.md` (P2-2 V2 산출물) — Pipeline S0~S8 + FailureCodeRegistry 48 + FallbackRegistry 35 + SDAR V2+ 5-Layer + NEVER_AUTO 3가지

| Gate FailureCode | error_fallback.md FC 매핑 | error_fallback.md FB 매핑 |
|-----------------|--------------------------|--------------------------|
| `G0_FORMAT_FAIL` / `G0_LENGTH_FAIL` / `G0_BLACKLIST_FAIL` / `G0_ROBOTS_FAIL` / `G0_ROBOTS_DENY` | §3 Pipeline S1 G0_BLOCK FC 매핑 | FB-1 (재시도 ❌, 거부) |
| `G1_QUALITY_LOW` | §4 Pipeline S2 G1_REJECT FC 매핑 | FB-2 (재평가 V2 LLM) / 3차 SDAR |
| `G2_DUPLICATE` / `G2_CONSISTENCY_LOW` | §5 Pipeline S3 G2_DEMOTE FC 매핑 | FB-3 (강등 자동) |
| `G3_CSAM_BLOCK` | §6 NEVER_AUTO 즉시 ESCALATED + 법적 보고 | NEVER_AUTO 경로 |
| `G3_MALWARE_BLOCK` / `G3_PII_BLOCK` / `G3_SECURITY_LOW` | §6 Pipeline S4 G3_SECURITY_BLOCK FC 매핑 | FB-4 (운영자 알림) |
| `G4_FINAL_LOW` | §7 Pipeline S5 G4_ARCHIVE_ONLY FC 매핑 | FB-5 (아카이브 저장) |
| `SCORE_BORDERLINE_G1~G4` | §5.3 SCORE_BORDERLINE FC | I-20 운영자 큐 |

> **P2-1 ↔ P2-2 verbatim 매핑 강제**: §3.* 에서 발생하는 모든 FailureCode 는 `error_fallback.md` §3~§7 (S1~S5) 에 1:1 매핑. mismatch 발견 시 step 7 정합 검증 단계에서 보정.

---

## §10. CONFLICT 상태 (CONFLICT_LOG.md 인용)

| ID | 대상 | 본 §3 인용 | 상태 |
|----|------|-----------|------|
| **CL-C001 (SC-13)** | G1 Gate명 ("Trust Score" → "Content Quality") | §3.2 CL-G1 명칭 = "Content Quality" verbatim 채택 (FIX-09 RESOLVED 보존) | ✅ RESOLVED |
| **CL-C002 (SC-14)** | G2 Gate명 ("Relevance" → "Consistency") | §3.3 CL-G2 명칭 = "Consistency" verbatim 채택 (FIX-09 RESOLVED 보존) | ✅ RESOLVED |
| **W-1** | SPEC 공유 6-7 ↔ 6-8 | §4 Fast Gate BaseGate(ABC) 인터페이스 공유 정합 보존 | ✅ RESOLVED |

> 신규 [CONFLICT_CANDIDATE]: 0건 (P2-1 본 작성 시점). step 7 cross-ref sync 시점 재검증.

---

## §11. ISS-4 해결 표기

**ISS-4 해결**: 5-Gate 검증 로직 미상세 (MEDIUM) → CL-G0~G4 판정 알고리즘 + 임계값 + V1/V2/V3 단계별 구현 + Fast Gate 6-7 cross-handoff + scoring §5.2 BORDERLINE 경계 정책 + 14건 테스트 케이스 + 공통 자료 구조 GateResult Pydantic + ABC 매핑 = ISS-4 ✅ 완료 (Phase 2 P2-1 산출물).

---

## §12. 변경 이력

| 일자 | 버전 | 변경 | 근거 |
|------|------|------|------|
| 2026-04-28 | V2-Phase 2 P2-1 | NEW — STAGE 7 STEP_B P2-1 V2 신규 작성 | ISS-4 해결, exit_gate 4/4 산출물 1번째 |

---

<!-- END OF DOCUMENT -->
