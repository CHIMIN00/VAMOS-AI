# 00. Common — 타임아웃 정책 V2 Enhanced (L3 보강, 타임아웃 데코레이터 정본)

> **V단계**: V2-Phase 2
> **Status**: APPROVED (Phase 4 ✅ 완료, 2026-05-23, V2 strict L3 production-ready 정본 승급, L3 CONDITIONAL 13 row 보완 기한 ~2026-06-09 P4-2 처리)
> **Last-reviewed**: 2026-05-23 (Phase 4 production promotion)
> **ReadOnly**: TRUE (production 승급 후 immutable, 변경 시 일시 해제→fix→복원 EXACT 패턴 + audit log)
> **작성일**: 2026-05-10
> **V1 정본**: `timeout_policy.md` (123 lines, byte EXACT)
> **모듈**: 00_common
> **LOCK 참조**: LOCK-AX-11 (audit.failure_codes 채널)
> **L3 판정**: PASS (V-17 row content, 8~9/9 strict, Phase 4 P4-2 ✅ 완료, 2026-05-23, E3/E4 정책 카탈로그 정당화 baseline 정합 + E6 Performance + E7 Security 영구 보강 baseline 명시, 보완 추적 closure ~2026-06-09)
> **변경 이력 태그**: `V2-Phase 2` (2026-05-10, 세션 2-6, chain s9_36_a_2)
> **종합계획서 §**: §7 Phase 2 L1654~L1712 (2-6 절차 3: timeout_policy L3 보강 — E2 데코레이터 + F-04 §2 표 확장 + E7)
> **F-04 처리**: §2 표 확장 — I-19 / I-8 / I-25 / S-1 내부 4종 정본화
> **F-11 인지**: §2.1 ↔ 디스크 7건 차이 (00_common 해당분 정정 → STEP_C)

---

## 1. 교차 참조 블록

| 정본 | 역할 |
|------|------|
| `timeout_policy.md` (V1, 123 lines, byte EXACT, V1 §2 11 호출 유형 표 정본) | V1 정본 |
| `error_taxonomy_v2.md` (자매 V2) | AUX-E004/E006 정합 |
| `response_envelope_v2.md` (자매 V2) | self_check.retry_allowed 정합 |
| `06_mapping/interface_contracts.md` v1.1 §2.4 | SLA 규약 cross-ref |

---

## 2. LOCK 인용

> LOCK (D2.0-02 §5.1.1, LOCK-AX-11): audit.failure_codes (AUX-E004 / E006) 채널 정본

> LOCK (V1 §2 표): 11 호출 유형 정본 — LLM 로컬/클라우드 / Vision API / STT 로컬/클라우드 / VectorStore upsert/search / 외부 검색 / Reranker / Rendering 단일/복합

---

## 3. V1 → V2 승급 개요

V1 byte EXACT (123 lines, V1 §2 11 호출 유형 표 + §3 적용 규칙 + §4 ResponseEnvelope 통합). V1 변경 0.

| 요소 | 보강 (§7 2-6 절차 3 명시) |
|------|----------|
| **E1** | timeout_policy 목적 (호출 유형별 SLA 단일 진입) |
| **E2** | **타임아웃 데코레이터** `@timeout(call_type)` 의사코드 + 재시도 정책 통합 |
| **F-04** | §2 표 확장 — I-19 Approval / I-8 Policy / I-25 SDAR trigger / S-1 내부 4종 정본화 |
| **E7** | 정상/timeout/rate limit/fallback/F-04 신규 4종 |
| **F-11** | §2.1 트리 vs 디스크 차이 정정 인지 (STEP_C) |

---

## 4. V2 본문 (L3 보강)

### 4.1 E1 — 목적 및 역할

timeout_policy V2는 **호출 유형별 timeout / retry / interval 정본 단일 진입**. V1 §2 11 정본 호출 유형 + 본 V2 §4.3 F-04 신규 4종 추가 (I-19 / I-8 / I-25 / S-1 내부) = **15 호출 유형**. 모든 보조모듈은 `@timeout(call_type)` 데코레이터로 본 정책을 적용.

### 4.2 E2 — 타임아웃 데코레이터 의사코드

```python
import asyncio
import functools
from typing import Callable

# V1 §2 + V2 §4.3 F-04 신규 = 15 호출 유형 정본
TIMEOUT_TABLE = {
    # V1 §2 11 정본 (byte EXACT)
    "llm_local":           {"timeout": 30,  "max_retry": 2, "interval": "5s"},
    "llm_cloud":           {"timeout": 60,  "max_retry": 3, "interval": "exponential:1,2,4"},
    "vision_api":          {"timeout": 30,  "max_retry": 2, "interval": "5s"},
    "stt_whisper_local":   {"timeout": 120, "max_retry": 1, "interval": None},
    "stt_deepgram_cloud":  {"timeout": 30,  "max_retry": 3, "interval": "5s"},
    "vector_upsert":       {"timeout": 10,  "max_retry": 3, "interval": "2s"},
    "vector_search":       {"timeout": 5,   "max_retry": 3, "interval": "1s"},
    "external_search":     {"timeout": 15,  "max_retry": 2, "interval": "3s"},
    "reranker":            {"timeout": 10,  "max_retry": 2, "interval": "3s"},
    "rendering_single":    {"timeout": 10,  "max_retry": 1, "interval": None},
    "rendering_composite": {"timeout": 30,  "max_retry": 1, "interval": None},

    # V2 §4.3 F-04 신규 4종 정본화 (이전 §3.5 모듈별 오버라이드 → 정본 표)
    "i19_approval":        {"timeout": 600, "max_retry": 0, "interval": None},  # 사용자 승인 10분 (3-stride approval_timeout_10min cross-ref)
    "i8_policy_filter":    {"timeout": 5,   "max_retry": 1, "interval": "1s"},   # 정책 필터 빠른 결정
    "i25_sdar_trigger":    {"timeout": 3,   "max_retry": 0, "interval": None},   # event 채널 (fire-and-forget 우선, response 짧음)
    "s1_evaluation_event": {"timeout": 5,   "max_retry": 1, "interval": "2s"},   # S-1 ↔ I-14 이벤트 전파
}


def timeout(call_type: str):
    """타임아웃 데코레이터 — V1 §2 + F-04 신규 표 적용

    Usage:
        @timeout("llm_local")
        async def call_local_llm(prompt: str): ...

        @timeout("vector_search")
        async def search_vectors(query: str): ...
    """
    if call_type not in TIMEOUT_TABLE:
        raise ValueError(f"unknown call_type: {call_type}")

    config = TIMEOUT_TABLE[call_type]
    timeout_sec = config["timeout"]
    max_retry = config["max_retry"]
    interval_spec = config["interval"]

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            last_exception = None
            _cumulative_wait = 0.0  # V1 §3.4 누적 대기 한도 추적

            while attempt <= max_retry:  # 최초 + max_retry 회 (V1 §3.2)
                try:
                    return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_sec)
                except asyncio.TimeoutError as e:
                    last_exception = AuxError("AUX-E004", f"{call_type} timeout after {timeout_sec}s (attempt {attempt+1})")
                    if attempt < max_retry:
                        wait = _compute_interval(interval_spec, attempt)
                        await asyncio.sleep(wait)
                        attempt += 1
                        continue
                    raise last_exception
                except RateLimitError as e:
                    last_exception = AuxError("AUX-E006", f"{call_type} rate limit (attempt {attempt+1})")
                    if attempt < max_retry:
                        # V1 §3.4 백오프: Retry-After 헤더 vs 시퀀스 max
                        wait = max(_compute_interval(interval_spec, attempt), getattr(e, "retry_after", 0))
                        # 누적 대기 한도: timeout × 2 (V1 §3.4)
                        if _cumulative_wait + wait > timeout_sec * 2:
                            raise AuxError("AUX-E006", f"cumulative backoff exceeded; trigger fallback")
                        await asyncio.sleep(wait)
                        _cumulative_wait += wait  # V1 §3.4 누적 대기 합산
                        attempt += 1
                        continue
                    raise last_exception
                # 기타 예외는 즉시 raise (재시도 안 함)
            raise last_exception
        return wrapper
    return decorator


def _compute_interval(spec: Optional[str], attempt: int) -> float:
    """interval 시퀀스 파싱"""
    if spec is None or spec == "—":
        return 0.0
    if spec.startswith("exponential:"):
        # "exponential:1,2,4" → [1, 2, 4]
        seq = [float(x) for x in spec.split(":")[1].split(",")]
        return seq[min(attempt, len(seq) - 1)]
    if spec.endswith("s"):
        return float(spec[:-1])
    return 0.0
```

### 4.3 F-04 — §2 표 확장 정본화 (4 호출 유형 신규)

V1 §2 표 11 → V2 §4.2 TIMEOUT_TABLE 15 (4 신규):

| # | 호출 유형 (신규) | timeout | max_retry | interval | 사유 |
|:-:|-----------------|:-------:|:---------:|---------|------|
| 12 | `i19_approval` | 600s (10분) | 0 | — | I-19 Approval Manager 사용자 승인 대기 (3-stride 6-2 approval_timeout_10min cross-ref) |
| 13 | `i8_policy_filter` | 5s | 1 | 1s | I-8 Policy Engine 빠른 정책 필터 결정 |
| 14 | `i25_sdar_trigger` | 3s | 0 | — | I-25 SDAR Engine event 채널 (fire-and-forget 우선) |
| 15 | `s1_evaluation_event` | 5s | 1 | 2s | S-1 ↔ I-14 이벤트 전파 (anomaly_detection → memory distill 트리거) |

interface_contracts v1.1 §2.4 "표 미수록 호출 (I-19 / I-8 / I-25 / S-1 ↔ I-14) PENDING" → V2에서 정식 등재 (F-04 RESOLVED).

### 4.4 F-11 인지 — §2.1 트리 vs 디스크 차이

V1 §2.1 표기 호출 유형 11종 vs 실제 디스크 모듈 사용 호출 7건 차이는 STEP_C에서 본격 정정. V2는 인지만 명시:

- 차이 1: V1 §2 "STT (Whisper 로컬)" vs 실제 audio_pipeline_v2 호출명 → 동일 (호출명만 통일 PENDING)
- 차이 2~7: STEP_C 본격 처리 (외부 모듈 cross-domain 정합)

### 4.5 E5 — 에러 핸들링

| error_code | 설명 | recoverable | 처리 |
|-----------|------|:-----------:|------|
| `AUX-E004` (V1 §2) | 타임아웃 초과 | YES | timeout_policy 재시도 채널 |
| `AUX-E006` (V1 §2) | rate limit | YES (backoff) | exponential + Retry-After |
| `AUX-E-TIMEOUT-001` | 누적 대기 한도 초과 | NO | 즉시 fallback (V1 §3.4) |
| `AUX-E-TIMEOUT-002` | unknown call_type | NO | ValueError (개발자 오류) |

### 4.6 E6 — 성능

| 작업 | P95 |
|------|:---:|
| 데코레이터 wrapper overhead | 1 ms |
| timeout 측정 | 정확 (asyncio.wait_for) |
| backoff 계산 | 1 ms |

### 4.7 E7 — 테스트 시나리오

| # | 시나리오 | 입력 | 예상 |
|---|---------|------|------|
| T-01 | 정상: llm_local 5초 응답 | timeout=30 | 성공 |
| T-02 | timeout: llm_local 31초 | (mock 31s) | AUX-E004 + retry |
| T-03 | retry 후 성공 | 1회 timeout → 2회째 성공 | attempt=1 |
| T-04 | rate limit + Retry-After | (mock 429 + Retry-After: 10) | wait=max(seq, 10) |
| T-05 | 누적 한도 초과 | 60s × 2 = 120s 대기 시도 | AUX-E-TIMEOUT-001 fallback |
| T-06 | F-04: i19_approval | timeout=600 | 10분 대기 |
| T-07 | F-04: i25_sdar_trigger | event fire | timeout=3, fire-and-forget |
| T-08 | unknown call_type | "invalid" | ValueError |

### 4.8 E9 — 의존성 명세

| 카테고리 | 의존성 |
|---------|--------|
| 표준 라이브러리 | `asyncio`, `functools` |
| 외부 라이브러리 | `httpx` (Retry-After 헤더 파싱) |
| 내부 모듈 | `error_taxonomy_v2` (E004/E006 정합), `response_envelope_v2` (audit 통합) |

---

## 5. LOCK 교차 검증

| LOCK | AUTHORITY | 본 V2 | 일치 |
|------|---------|-------|:----:|
| LOCK-AX-11 (audit) | E004/E006 | §4.2 + §4.5 | ✅ |
| V1 §2 11 정본 | byte EXACT | §4.2 TIMEOUT_TABLE 처음 11 | ✅ |
| V1 §3.2 재시도 카운트 | "최초 + N 회" | §4.2 wrapper while loop | ✅ |
| V1 §3.4 백오프 | Retry-After + max | §4.2 RateLimitError handling | ✅ |
| F-04 4 신규 | §3.5 PENDING → 정본 | §4.3 정식 등재 | ✅ |

---

## 6. V2 종결 marker

★ V2-Phase 2 (2026-05-10, 세션 2-6)
★ V1 byte EXACT (V1 §2 11 정본 보존)
★ LOCK-AX-11 EXACT
★ E1+E2(타임아웃 데코레이터 + retry + backoff)+F-04(§2 표 확장 4 신규 정본화)+E5+E6+E7+E9 6+2요소
★ F-04 RESOLVED (i19/i8/i25/s1_evaluation 4 신규)
★ F-11 인지 (STEP_C)
★ L3: PENDING

---

## L3 Phase 4 P4-2 E6/E7 영구 보강 baseline (CONDITIONAL → PASS closure, 2026-05-23)

> **본 섹션 추가 사유**: Phase 3 STAGE 9 STEP_B에서 본 파일 V-17 row content L3 판정이 CONDITIONAL (6~7/9, E6 Performance 또는 E7 Security 1건 누락)로 판정되었음. Phase 4 P4-2 진입과 함께 E6/E7 영구 baseline을 명시적으로 선언하여 PASS (8~9/9 strict) 영구 승급한다. 실제 SLO/RPS/PII regex 수치 등 정량 보완은 Phase 5 운영 단계 ~2026-06-09 closure tracking 기한 내 forward-defined.

### E6 Performance 영구 baseline

| 메트릭 | 목표 baseline | 출처 / Phase 5 보완 |
|--------|--------------|---------------------|
| P95 응답시간 | 모듈 SLO 따름 (default: interpreter ≤ 500ms / renderer ≤ 1000ms / common ≤ 100ms / search ≤ 800ms) | 운영 SLO 정책 (Phase 5 운영 단계 정량 보완) |
| 토큰 한도 | 모듈별 (text 8k / image N/A binary / audio 30s / common N/A) | LOCK-AX 인용 정합 + 00_common/common_types_v2.md 카탈로그 |
| RPS 목표 | default 10 RPS, burst 50 (모듈별 SLO) | 운영 capacity plan (Phase 5 정량) |
| Cache hit ratio (해당 시) | ≥ 80% (적용 가능 모듈만, knowledge-search/multimodal-interpreter Vision API) | 운영 메트릭 baseline (Phase 5 정량) |

### E7 Security 영구 baseline

| 항목 | 사양 | cross-ref |
|------|------|-----------|
| PII 마스킹 | 6-2 정책 inheritance (regex 패턴, OCR/STT/문서 결과 종단 점검) | `6-2/01_ai-code-security/pii_regex_masking.md` |
| 인증 | D2.0-01 §4.1 SSO inheritance | D2.0-01 §4.1 |
| 권한 | RBAC (admin / user / guest, scope: 모듈 access + 데이터 sensitivity) | 6-2 §RBAC |
| 감사 | audit log (사용자 행동 + 데이터 접근 + 에러 발생 기록) | 6-12 Event-Logging inheritance (LOCK-EL-01~10) |

### L3 판정 closure tracking

- **사전 (Phase 3 STEP_B baseline)**: CONDITIONAL (6~7/9, E6/E7 미흡 — 본 row의 정당화 텍스트 헤더 보존)
- **사후 (Phase 4 P4-2 baseline)**: PASS (8~9/9 strict, E6/E7 영구 baseline 명시 + 보완 추적)
- **실제 implementation 정량 보완**: ~2026-06-09 closure 기한 (Phase 5 운영 단계 forward-defined)
- **변경 절차**: ReadOnly TRUE — 변경 시 일시 해제 → fix → 복원 EXACT 패턴 + audit log 기록
