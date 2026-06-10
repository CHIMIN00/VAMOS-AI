# FailureCodeRegistry — 48항목 정본

> **도메인**: 6-12_Event-Logging / 02_logging-standard
> **파일**: `failure_code_registry.md`
> **정본 선언**: 본 파일은 SOT2 정본(Single Source of Truth)이며, LOCK-EL-03 이 지정한 **48개 FailureCode** (D2.1-D2 36 + Part2 V2/V3 12) 전수 레지스트리 + 심각도 + 권고 로깅 레벨 + NEVER_AUTO 표시에 대해 권위를 가진다.
> **버전**: v1.0.1 (2026-04-14, step2 재검증 — §8 정본 인용 + §10 TL_ERR_403 교정)
> **세션**: P1-6 (Phase 1)
> **LOCK 연계**: LOCK-EL-03 (48항목), LOCK-EL-05 (FC→FB 매핑 정본은 Part2 §6.9 — 본 파일은 "코드 1차 FB 힌트"만 제공), LOCK-EL-06 (NEVER_AUTO 3코드), LOCK-EL-07 (로깅 레벨 5단계)

---

## §0. 교차 참조 (Cross-References)

| 문서 | 경로 | 용도 |
|------|------|------|
| AUTHORITY_CHAIN | `../AUTHORITY_CHAIN.md` | LOCK-EL-03 정의, 48항목 근거 |
| 종합계획서 | `../EVENT_LOGGING_구조화_종합계획서.md` §3.3, §7.2 P1-6 | LOCK 목록 + P1-6 절차 |
| D2.1-D2 §5.2 | `D:\VAMOS\docs\sot\D2.1-D2_D2_SCHEMA_ORANGE_CORE.md` L291-342 | D2.1-D2 36 FailureCode 원본 |
| D2.1-D2 §8 | 같은 문서 L478-505 | D2.1-D2 FC→FB 매핑 원본(35행) |
| Part2 §6.11 | `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` L5846-5975 | 36 FC 재선언 + V2/V3 12 FC 확장 + NEVER_AUTO |
| Part2 §6.11 매핑 | 같은 문서 L5875-5927 | FC→FB 1:N 매핑 정본(§6.9 선언) |
| 02/log_level_spec.md | `./log_level_spec.md` §4.1 | FailureCode → Level 매핑 규약 (P1-5) |
| 02/fallback_registry.md | `./fallback_registry.md` (예정, P1-7) | 35 FallbackAction 상세 |
| 02/fc_fb_mapping.md | `./fc_fb_mapping.md` (예정, P1-8) | FC→FB 1:N 매핑 최종 테이블(48 FC 전수) |
| 02/never_auto_detector.md | `./never_auto_detector.md` (예정, P1-9) | NEVER_AUTO 탐지 메커니즘(LOCK-EL-06) |
| 01/event_type_registry.md | `../01_event-system/event_type_registry.md` | EventTypeRegistry 134항목 (이벤트 코드 관점) |
| 01/event_schema.md | `../01_event-system/event_schema.md` | `payload.failure_code` 필드 수용 스키마 |

---

## §1. 목적 및 범위 (Purpose / Scope)

### 1.1 목적
- LOCK-EL-03 가 확정한 **48개 FailureCode** 를 코드명·구분·설명·심각도·권고 로깅 레벨·NEVER_AUTO 표시·1차 Fallback 힌트·도입 버전과 함께 전수 등록한다.
- 각 코드의 **정본 출처**(D2.1-D2 §5.2 또는 Part2 §6.11)를 명시하여, 변경 시 상위 문서 우선 원칙(R-T6-1)을 강제한다.
- 본 파일은 **코드 카탈로그**(What) 이며, FC→FB 매핑의 최종 정본 테이블은 `fc_fb_mapping.md` (P1-8) 가 가진다. 본 파일의 `1차 FB 힌트` 컬럼은 Part2 §6.11 매핑 요약 스냅샷이다 (변경 시 P1-8 와 동기화).

### 1.2 범위 (In-scope)
- 48 FailureCode 전수 항목 (D2.1-D2 36 + Part2 V2/V3 12).
- 각 코드의 로깅 레벨 기본값 (P1-5 §4.1 매핑 규약 적용).
- NEVER_AUTO 대상 3코드 표시 (LOCK-EL-06).
- 확장 규칙 요약 (R-612-3 — Fallback 매핑 필수; R-612-4 — NEVER_AUTO 탐지 규칙 동시 추가).
- Phase 2 테스트 시나리오 12건.

### 1.3 범위 외 (Out-of-scope)
- FC→FB 전수 매핑 테이블 → **P1-8 `fc_fb_mapping.md`**.
- NEVER_AUTO 탐지기 구현(알고리즘/의사코드) → **P1-9 `never_auto_detector.md`**.
- FailureCode 이벤트 발행 스키마(`payload.failure_code` 필드 타입) → **P1-1 `event_schema.md`**.
- 로깅 레벨 숫자 정의 / 환경별 필터링 → **P1-5 `log_level_spec.md`**.
- 보존 기한 / 알림 정책 → 6-13 Operations 도메인.

---

## §2. 항목 집계 (LOCK-EL-03 검증)

| 구분 | 접두어 | 항목 수 | 버전 | 정본 출처 |
|------|--------|--------|------|----------|
| Intent (I-1) | `OC_I1_*` | 2 | V0+ | D2.1-D2 §5.2 |
| Evidence (I-2) | `OC_I2_*` | 4 | V0+ | D2.1-D2 §5.2 |
| Memory (I-3) | `OC_I3_*` | 3 | V0+ | D2.1-D2 §5.2 |
| Output (I-4) | `OC_I4_*` | 3 | V0+ | D2.1-D2 §5.2 |
| Decision (I-5) | `OC_I5_*` | 5 | V0+ | D2.1-D2 §5.2 |
| General | `PII_* / POLICY_* / GT_* / TOOL_*` | 4 | V0+ | D2.1-D2 §5.2 |
| Format | `FM_ERR_*` | 4 | V0+ | D2.1-D2 §5.2 |
| OC Errors | `OC_ERR_*` | 5 | V0+ | D2.1-D2 §5.2 |
| Tool | `TL_ERR_*` | 3 | V0+ | D2.1-D2 §5.2 |
| Memory Check | `MC_ERR_*` | 3 | V1+ | D2.1-D2 §5.2 |
| **D2.1-D2 SOT 소계** | — | **36** | — | — |
| COND (V2) | `COND_*` | 3 | V2 | Part2 §6.11 L5962-5964 |
| RAG V2 | `RAG_*` | 1 | V2 | Part2 §6.11 L5965 |
| SDAR (V2) | `SDAR_*` | 2 | V2 | Part2 §6.11 L5966-5967 |
| LlamaGuard (V2) | `LLAMAGUARD_*` | 2 | V2 | Part2 §6.11 L5968-5969 |
| Self-Evo (V3) | `EXP_SELF_*` | 1 | V3 | Part2 §6.11 L5970 |
| Agent Mesh (V3) | `EXP_AGENT_*` | 1 | V3 | Part2 §6.11 L5971 |
| GPU (V3) | `EXP_GPU_*` | 1 | V3 | Part2 §6.11 L5972 |
| A2A (V3) | `EXP_A2A_*` | 1 | V3 | Part2 §6.11 L5973 |
| **Part2 V2/V3 확장 소계** | — | **12** | — | — |
| **LOCK-EL-03 합계** | — | **48** | — | D2.1-D2 + Part2 §6.11 |

검증: **36 + 12 = 48** ✅ LOCK-EL-03 일치.

---

## §3. 공통 자료 구조 (Shared Types)

```python
from dataclasses import dataclass
from typing import Literal, Optional

Severity = Literal["P0", "P1", "P2", "P3"]
LogLevel = Literal["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"]
Version  = Literal["V0+", "V1+", "V2", "V3"]
Category = Literal[
    "I1_INTENT", "I2_EVIDENCE", "I3_MEMORY", "I4_OUTPUT", "I5_DECISION",
    "GENERAL", "FORMAT", "OC_ERR", "TOOL", "MEM_CHECK",
    "COND", "RAG", "SDAR", "LLAMAGUARD",
    "EXP_SELF", "EXP_AGENT", "EXP_GPU", "EXP_A2A",
]

@dataclass(frozen=True)
class FailureCodeEntry:
    code: str                         # 예: "OC_I1_PARSE_FAIL"
    category: Category                # §2 구분 중 하나
    prefix: str                       # 예: "OC_I1_"
    description: str                  # 1-2줄 설명
    severity: Severity                # P0~P3 (비즈니스 중단 영향)
    default_level: LogLevel           # LOCK-EL-07 기본 권고 (P1-5 §4.1 규약 적용)
    never_auto: bool                  # LOCK-EL-06 해당 여부
    first_fallback_hint: Optional[str]  # Part2 §6.11 1차 FB 스냅샷 (정본은 P1-8)
    version: Version                  # 도입 버전
    source: Literal["D2.1-D2 §5.2", "Part2 §6.11"]
    notes: Optional[str] = None       # exception level, 연계 등
```

- `default_level` 은 P1-5 `log_level_spec.md` §4.1 "FailureCode → Level 매핑 규약" 의 그룹별 기본값을 따른다. 특례(예: `OC_I1_*` 중 ambiguous = WARN, `OC_I2_*` 중 증거 0 = ERROR) 는 `notes` 에 기록한다.
- `never_auto=True` 시 `default_level` 은 **CRITICAL 로 강제 승격**된다 (P1-5 §4.1 R2/R3 규약).
- `first_fallback_hint` 는 Part2 §6.11 L5879-5927 (36건) 및 L5960-5973 (12건) 의 "1차 Fallback" 열 스냅샷. **정본은 P1-8**.

---

## §4. FailureCodeRegistry 전수 테이블 (48/48)

> **심각도 정책**: `P0 = 서비스 전면 영향` / `P1 = 단일 요청 실패 + 후속 영향` / `P2 = 단일 요청 실패` / `P3 = 경미/복구 가능`.
> **NEVER_AUTO** (LOCK-EL-06): ⛔ = `{OC_I5_POLICY_BLOCK, POLICY_DENY, PII_LONGTERM_DENIED}` 3코드.

### §4.1 Intent (I-1) — D2.1-D2 §5.2

| # | 코드 | 설명 | 심각도 | 권고 레벨 | NEVER_AUTO | 1차 FB 힌트 | 버전 |
|---|------|------|--------|----------|-----------|------------|------|
| 1 | `OC_I1_PARSE_FAIL` | 사용자 입력 파싱 실패 (구문 분해 불가) | P2 | ERROR | — | `FB_INTENT_HEURISTIC_PARSE` | V0+ |
| 2 | `OC_I1_AMBIGUOUS_UNRESOLVED` | 의도 모호성 해소 실패 (명확화 후 재시도) | P3 | WARN | — | `FB_ASK_CLARIFICATION` | V0+ |

### §4.2 Evidence (I-2) — D2.1-D2 §5.2

| # | 코드 | 설명 | 심각도 | 권고 레벨 | NEVER_AUTO | 1차 FB 힌트 | 버전 |
|---|------|------|--------|----------|-----------|------------|------|
| 3 | `OC_I2_RAG_NO_SOURCE` | RAG 검색 결과 0건 (증거 소스 미발견) | P2 | ERROR | — | `FB_RAG_RETRY_EXPAND` | V0+ |
| 4 | `OC_I2_EVIDENCE_QOD_LOW` | 증거 품질(QoD) 임계 미만 | P3 | WARN | — | `FB_RAG_RETRY_EXPAND` | V0+ |
| 5 | `OC_I2_SOURCE_POLICY_BLOCK` | 소스가 정책(저작권/민감도)에 의해 차단 | P2 | ERROR | — | `FB_RAG_SWITCH_SOURCE` | V0+ |
| 6 | `OC_I2_TIMEOUT` | RAG 호출 타임아웃 | P3 | WARN | — | `FB_RETRY_SOFT` | V0+ |

### §4.3 Memory (I-3) — D2.1-D2 §5.2

| # | 코드 | 설명 | 심각도 | 권고 레벨 | NEVER_AUTO | 1차 FB 힌트 | 버전 |
|---|------|------|--------|----------|-----------|------------|------|
| 7 | `OC_I3_MEMORY_POLICY_DENY` | 메모리 저장 정책 위반 (PII 장기 저장 등) | P1 | ERROR | — | `FB_MEMORY_META_ONLY` | V0+ |
| 8 | `OC_I3_APPROVAL_REQUIRED` | Commit 전 승인 필요 (P1+ 작업) | P3 | INFO | — | `FB_REQUIRE_APPROVAL` | V0+ |
| 9 | `OC_I3_COMMIT_FAIL` | 메모리 커밋 실패 (DB 오류 등) | P2 | ERROR | — | `FB_RETRY_SOFT` | V0+ |

### §4.4 Output (I-4) — D2.1-D2 §5.2

| # | 코드 | 설명 | 심각도 | 권고 레벨 | NEVER_AUTO | 1차 FB 힌트 | 버전 |
|---|------|------|--------|----------|-----------|------------|------|
| 10 | `OC_I4_OUTPUT_SPEC_VIOLATION` | 출력 스펙(구조/필드) 위반 | P2 | ERROR | — | `FB_OUTPUT_REFORMAT` | V0+ |
| 11 | `OC_I4_CITATION_MISSING` | 인용(Citation) 누락 | P3 | WARN | — | `FB_OUTPUT_REFORMAT` | V0+ |
| 12 | `OC_I4_MASK_FAIL` | PII 마스킹 실패 | P1 | ERROR | — | `FB_MASK_AND_CONFIRM` | V0+ |

### §4.5 Decision (I-5) — D2.1-D2 §5.2

| # | 코드 | 설명 | 심각도 | 권고 레벨 | NEVER_AUTO | 1차 FB 힌트 | 버전 |
|---|------|------|--------|----------|-----------|------------|------|
| 13 | `OC_I5_POLICY_BLOCK` | 최종 의사결정에서 정책 차단 | P1 | **CRITICAL** | ⛔ | `FB_POLICY_MASK` | V0+ |
| 14 | `OC_I5_APPROVAL_REQUIRED` | 실행 전 승인 필요 | P3 | INFO | — | `FB_REQUIRE_APPROVAL` | V0+ |
| 15 | `OC_I5_COST_OVER_BUDGET` | 비용 한도 초과 | P2 | ERROR | — | `FB_COST_DOWNSHIFT` | V0+ |
| 16 | `OC_I5_EVIDENCE_INSUFFICIENT` | 최종 검증에서 증거 불충분 | P2 | ERROR | — | `FB_RAG_RETRY_EXPAND` | V0+ |
| 17 | `OC_I5_ROUTE_NOT_FOUND` | 실행 가능한 라우트(노드) 없음 | P2 | ERROR | — | `FB_ROUTE_SAFE_NODE` | V0+ |

### §4.6 General — D2.1-D2 §5.2

| # | 코드 | 설명 | 심각도 | 권고 레벨 | NEVER_AUTO | 1차 FB 힌트 | 버전 |
|---|------|------|--------|----------|-----------|------------|------|
| 18 | `PII_LONGTERM_DENIED` | PII 장기 저장 시도 차단 (BASE 1.3 §2.4) | P0 | **CRITICAL** | ⛔ | `FB_DENY_STORAGE` | V0+ |
| 19 | `POLICY_DENY` | 정책 엔진 DENY 판정 (범용) | P0 | **CRITICAL** | ⛔ | `FB_DENY_WITH_REASON` | V0+ |
| 20 | `GT_ERR_COST_LIMIT` | CostGate 한도 초과 | P2 | ERROR | — | `FB_COST_DOWNSHIFT` | V0+ |
| 21 | `TOOL_TIMEOUT` | 외부 도구 호출 타임아웃 | P3 | WARN | — | `FB_RETRY_SOFT` | V0+ |

### §4.7 Format (FM) — D2.1-D2 §5.2

| # | 코드 | 설명 | 심각도 | 권고 레벨 | NEVER_AUTO | 1차 FB 힌트 | 버전 |
|---|------|------|--------|----------|-----------|------------|------|
| 22 | `FM_ERR_FMT` | 입력 포맷 불일치 (MIME/확장자) | P3 | ERROR | — | `FB_OUTPUT_REFORMAT` | V0+ |
| 23 | `FM_ERR_SIZE` | 입력 크기 한도 초과 | P3 | ERROR | — | `FB_OUTPUT_MINIMAL` | V0+ |
| 24 | `FM_ERR_PII` | 입력에서 PII 감지 (FrontMini 스캐너) | P1 | ERROR | — | `FB_MASK_AND_CONFIRM` | V0+ |
| 25 | `FM_ERR_ZERO` | 빈 입력 (길이 0) | P3 | WARN | — | `FB_RETURN_RAW` | V0+ |

### §4.8 OC Errors — D2.1-D2 §5.2

| # | 코드 | 설명 | 심각도 | 권고 레벨 | NEVER_AUTO | 1차 FB 힌트 | 버전 |
|---|------|------|--------|----------|-----------|------------|------|
| 26 | `OC_ERR_NONGOAL` | Non-goal 요청 감지 (RULE 1.3 §2) | P1 | ERROR | — | `FB_DENY_WITH_REASON` | V0+ |
| 27 | `OC_ERR_P2_LOCK` | P2 도메인 LOCK 위반 (자동 생성/활성 금지) | P1 | ERROR | — | `FB_REQUIRE_APPROVAL` | V0+ |
| 28 | `OC_ERR_COST_LV` | 비용 레벨(Light/Heavy) 오분류 | P3 | ERROR | — | `FB_COST_DOWNSHIFT` | V0+ |
| 29 | `OC_ERR_COST_OV` | 비용 한도 over (즉시 차단) | P1 | ERROR | — | `FB_COST_DOWNSHIFT` | V0+ |
| 30 | `OC_ERR_NO_ROUTE` | 라우트 탐색 실패 (OC-1 Router 수준) | P2 | ERROR | — | `FB_ROUTE_SAFE_NODE` | V0+ |

### §4.9 Tool (TL) — D2.1-D2 §5.2

| # | 코드 | 설명 | 심각도 | 권고 레벨 | NEVER_AUTO | 1차 FB 힌트 | 버전 |
|---|------|------|--------|----------|-----------|------------|------|
| 31 | `TL_ERR_TIMEOUT` | 도구 호출 타임아웃 (세분화, `TOOL_TIMEOUT` 하위) | P3 | WARN | — | `FB_RETRY_SOFT` | V0+ |
| 32 | `TL_ERR_403` | 도구 API 권한 오류 (403 Forbidden) | P2 | WARN | — | `FB_REJECT_INPUT` | V0+ |
| 33 | `TL_ERR_PARSE` | 도구 응답 파싱 실패 | P3 | WARN | — | `FB_AUTO_REPAIR` | V0+ |

### §4.10 Memory Check (MC) — D2.1-D2 §5.2

| # | 코드 | 설명 | 심각도 | 권고 레벨 | NEVER_AUTO | 1차 FB 힌트 | 버전 |
|---|------|------|--------|----------|-----------|------------|------|
| 34 | `MC_ERR_LOW_QOD` | MemoryCheck QoD 낮음 (재조회 권고) | P3 | ERROR | — | `FB_RAG_RETRY_EXPAND` | V1+ |
| 35 | `MC_ERR_CONFLICT` | MemoryCheck 에서 모순 감지 | P2 | ERROR | — | `FB_SHOW_CONFLICT` | V1+ |
| 36 | `MC_ERR_STALE` | 메모리 항목 만료(stale) 감지 | P3 | ERROR | — | `FB_SHOW_STALE` | V1+ |

> ↑ D2.1-D2 §5.2 소계 **36/36** ✅.

### §4.11 V2 확장 — COND / RAG / SDAR / LlamaGuard (Part2 §6.11)

| # | 코드 | 설명 | 심각도 | 권고 레벨 | NEVER_AUTO | 1차 FB 힌트 | 버전 |
|---|------|------|--------|----------|-----------|------------|------|
| 37 | `COND_MODULE_INIT_FAIL` | COND 모듈 초기화 실패 (의존성 미충족) | P2 | WARN | — | `FB_SKIP_COND` | V2 |
| 38 | `COND_BATCH_TIMEOUT` | CAT-A~G 배치 처리 타임아웃 | P3 | WARN | — | `FB_REDUCE_BATCH` | V2 |
| 39 | `COND_DEPENDENCY_CONFLICT` | COND 모듈 간 순환 의존 감지 | P2 | WARN | — | `FB_ISOLATE_MODULE` | V2 |
| 40 | `RAG_QDRANT_CONNECTION` | Qdrant 벡터 DB 연결 실패 | P2 | WARN | — | `FB_RAG_FALLBACK_CHROMA` | V2 |
| 41 | `SDAR_REPAIR_FAIL` | SDAR 자동수리 실패 (3회 재시도 소진) | P1 | WARN | — | `FB_SDAR_ESCALATE` | V2 |
| 42 | `SDAR_SNAPSHOT_CORRUPT` | 수리 전 스냅샷 무결성 검증 실패 | P1 | WARN | — | `FB_SDAR_ABORT` | V2 |
| 43 | `LLAMAGUARD_GPU_UNAVAIL` | LlamaGuard GPU 사용 불가 | P2 | ERROR | — | `FB_GUARD_CPU_FALLBACK` | V2 |
| 44 | `LLAMAGUARD_CLASSIFY_FAIL` | LlamaGuard 안전성 분류 타임아웃/오류 | P1 | ERROR | — | `FB_GUARD_BLOCK_DEFAULT` | V2 |

### §4.12 V3 확장 — EXP_* (Part2 §6.11)

| # | 코드 | 설명 | 심각도 | 권고 레벨 | NEVER_AUTO | 1차 FB 힌트 | 버전 |
|---|------|------|--------|----------|-----------|------------|------|
| 45 | `EXP_SELF_EVO_REGRESSION` | Self-evo 후 성능 회귀 감지 | P1 | WARN | — | `FB_EVO_ROLLBACK` | V3 |
| 46 | `EXP_AGENT_SPAWN_LIMIT` | Agent Mesh 스폰 한도 초과(50+) | P2 | WARN | — | `FB_AGENT_QUEUE` | V3 |
| 47 | `EXP_GPU_OOM` | vLLM GPU 메모리 초과 | P2 | ERROR | — | `FB_GPU_OFFLOAD` | V3 |
| 48 | `EXP_A2A_AUTH_FAIL` | A2A 프로토콜 mTLS/JWT 인증 실패 | P1 | ERROR | — | `FB_A2A_RETRY` | V3 |

> ↑ Part2 V2/V3 확장 소계 **12/12** ✅.
> **전수 합계: 36 + 12 = 48 / 48** — LOCK-EL-03 일치 확인.

---

## §5. NEVER_AUTO 표시 (LOCK-EL-06)

| # | 코드 | 위치(§4.x) | 격상 규칙 | 연계 탐지 규칙 |
|---|------|-----------|----------|---------------|
| 1 | `OC_I5_POLICY_BLOCK` | §4.5 row 13 | 레벨 CRITICAL 강제, Fallback 성공 여부와 무관하게 HITL 승인 필수 | NeverAutoDetector R2 (POLICY_DENY 우회 감지) |
| 2 | `POLICY_DENY` | §4.6 row 19 | 레벨 CRITICAL 강제, 후속 노드 실행 금지 | NeverAutoDetector R2 |
| 3 | `PII_LONGTERM_DENIED` | §4.6 row 18 | 레벨 CRITICAL 강제, GDPR 보고서 생성 강제 | NeverAutoDetector R3 (PII 무단 저장 감지) |

**격상 규칙 요약**(P1-5 §4.1 연동):
```
FailureCode.never_auto=True
  → default_level 원본값 무시, CRITICAL 강제
  → Fallback 실행 여부와 무관하게 HITL 승인 경로(P1-9 탐지기) 발동
  → 감사 로그 CRITICAL 심각도로 저장(삭제/수정 불가)
```

> 상세 탐지 알고리즘 / 5규칙 의사코드는 **P1-9 `never_auto_detector.md`** 참조.

---

## §6. 확장 규칙 (R-612-3 / R-612-4)

### 6.1 새 FailureCode 추가 절차
1. **접두어 결정**: 신규 코드는 §2 접두어 규약을 따른다 (예: V4 기능은 `EXP_<SUBSYS>_*`).
2. **1 FB 이상 매핑 필수** (R-612-3): `fc_fb_mapping.md` (P1-8) 에 최소 1개 FB 등록. Fallback 이 존재하지 않으면 `fallback_registry.md` (P1-7) 에 먼저 등록.
3. **LOCK-EL-03 값 갱신**: 항목 수 변경 시 `AUTHORITY_CHAIN.md` L3 (LOCK-EL-03) 행 업데이트 + 본 파일 §2 / §4 갱신 + `_index.md` 갱신.
4. **NEVER_AUTO 해당 시** (R-612-4): `never_auto_detector.md` 에 탐지 규칙 1개 이상 추가. 미추가 시 PR 차단.
5. **변경 통보** (R-612-1): 소비 도메인 11개에 CONFLICT_LOG 기록 + 동기화 요청.

### 6.2 변경 우선순위
```
Part2 §6.11 원문 변경 → SOT2 반영 (R-T6-1: Part2 우선)
D2.1-D2 §5.2 원문 변경 → Part2 §6.11 동기화 → SOT2 반영
SOT2 신규 제안 → Part2 반영 후 본 파일 갱신 (역방향 금지, R10)
```

### 6.3 삭제 정책
- FailureCode 삭제는 **deprecation 2-단계**: (a) `deprecated=True` 플래그 + `removed_in=<version>` 주석, (b) 해당 메이저 버전 릴리스 후 제거. 즉시 삭제는 금지.
- 삭제 시 P1-8 매핑 테이블·P1-9 탐지 규칙 동시 정리.

---

## §7. 예외 처리 정책 (error_code 관점)

> 본 정책은 "FailureCode 그 자체가 예외 발생 시 어떻게 기록/격상되는가"를 규정한다. 전체 에러 파이프라인은 P1-5 §3.2, P1-9 참조.

| error_code | recoverable | 처리 | 레벨 | 비고 |
|-----------|-------------|------|------|------|
| `OC_I1_*` (Intent) | 부분적 (FB 성공 시 복구) | 로깅 → Fallback → 성공이면 WARN, 실패면 ERROR | ERROR / WARN (ambiguous) | P1-5 §4.1 Intent 규약 |
| `OC_I2_*` (Evidence) | 대부분 recoverable | 재검색/소스 전환 FB 시도 | WARN / ERROR (증거 0) | — |
| `OC_I3_*` (Memory) | approval-required 만 복구 가능 | FB→승인 or 저장 거부 | ERROR / INFO (approval) | — |
| `OC_I4_*` (Output) | 부분적 | 재포맷/마스킹 FB | ERROR / WARN (경미) | — |
| `OC_I5_POLICY_BLOCK` | **not recoverable** | CRITICAL + NEVER_AUTO → HITL | **CRITICAL** | LOCK-EL-06 #1 |
| `PII_LONGTERM_DENIED` | **not recoverable** | CRITICAL + GDPR 보고서 | **CRITICAL** | LOCK-EL-06 #3 |
| `POLICY_DENY` | **not recoverable** | CRITICAL + 후속 실행 금지 | **CRITICAL** | LOCK-EL-06 #2 |
| `GT_ERR_COST_LIMIT / OC_ERR_COST_*` | recoverable (downshift) | 비용 절감 FB | ERROR | — |
| `TOOL_TIMEOUT / TL_ERR_*` | recoverable (retry) | 소프트 재시도, 한계 초과 시 ERROR | WARN (한계 초과 시 ERROR) | — |
| `FM_ERR_*` | recoverable | 포맷/마스킹 FB | ERROR (재파싱 성공 시 WARN) | — |
| `MC_ERR_*` | recoverable | 재조회/충돌 표시 | ERROR | — |
| `COND_* / RAG_* / SDAR_*` (V2) | recoverable | 모듈 스킵/대체 DB/에스컬레이션 | WARN (전체 실패 시 ERROR) | — |
| `LLAMAGUARD_*` (V2) | 부분 recoverable | CPU fallback / 기본 차단 | ERROR | — |
| `EXP_*` (V3) | 대부분 recoverable | 롤백/대기열/오프로드/재시도 | WARN / ERROR | — |

---

## §8. 에스컬레이션 페이로드 구조 (R-01-8, I-20 경유)

`OC_I5_POLICY_BLOCK / POLICY_DENY / PII_LONGTERM_DENIED` (NEVER_AUTO) 발생 시 또는 Fallback 소진 시, **I-20 Escalation 경로**로 P1-5 `log_level_spec.md` §6.2 가 정의한 정본 `EscalationPayload` (11필드) 를 그대로 전달한다. 본 파일은 정본을 재정의하지 않고 **그대로 인용** + FailureCode 관점에서의 필드 사용 규약만 추가한다.

### §8.1 정본 인용 (P1-5 §6.2 — 11필드, 변경 금지)

```python
# 정본: log_level_spec.md §6.2
class EscalationPayload(BaseModel):
    source_engine: str                                    # e.g. "orange_core.i5_verifier"
    error_code: str                                       # FailureCode (LOCK-EL-03) or "SYSTEM_DOWN" 등
    original_request: dict[str, Any]                      # 최초 요청 스냅샷(PII 마스킹 후)
    partial_result: dict[str, Any] | None
    retry_count: int
    timestamp: str                                        # ISO 8601 UTC ms
    level: str                                            # "ERROR" | "CRITICAL"
    trace_id: str
    context: LogContextBlock
    recovery_attempts: list[LogRecoveryBlock]             # 시도된 FB 기록(action_id, result, latency_ms)
    reason: str                                           # 에스컬레이션 사유 요약
```

### §8.2 FailureCode 관점 필드 사용 규약

| 필드 | NEVER_AUTO (3코드) | 일반 FailureCode | 비고 |
|------|------------------|----------------|------|
| `error_code` | `OC_I5_POLICY_BLOCK` / `POLICY_DENY` / `PII_LONGTERM_DENIED` 중 하나 | §4 의 48 코드 중 하나 | 본 파일 §4 값 도메인 |
| `level` | `"CRITICAL"` 강제 (R3) | 정책상 `"ERROR"` 또는 `"CRITICAL"` | LOCK-EL-07 5단계 도메인 |
| `recovery_attempts` | 빈 리스트 또는 차단된 FB 1건 | 시도된 FB action_id 시퀀스 | `attempted_fallbacks` 의 정본 표현 |
| `reason` | "NEVER_AUTO violation: <코드>" | "<코드> Fallback exhausted after N retries" | 사람이 읽을 요약 |
| `context.severity` (LogContextBlock 내) | §4 의 `severity` (P0~P1 권장) | §4 의 `severity` 값 | 본 파일 §4 값 그대로 전달 |
| `context.never_auto` (LogContextBlock 내) | `True` | `False` | NEVER_AUTO 판단 결과 캐시 |

> **정합성 규칙 (j)**: 본 §8 의 페이로드 정의는 P1-5 §6.2 정본과 동일한 11필드. 새 dataclass 를 정의하지 않는다. severity / never_auto / attempted_fallbacks 같은 FailureCode 메타데이터는 `context: LogContextBlock` 의 확장 필드로 캡슐화되어 전달된다(P1-5 `LogContextBlock` 정의는 동 §1.2 참조).

경로: `<failure_source> → 이벤트(level=ERROR/CRITICAL) → NeverAutoDetector(P1-9) → I-20 Escalation(EscalationPayload) → 인간 승인(S3a)`.

---

## §9. 로깅 포맷 (R-01-7) — FailureCode 발행 예시

모든 FailureCode 발생 이벤트는 `payload.failure_code` 를 포함하고 **중첩 JSON** 로 기록한다 (P1-5 §3.2 예시 구조 준수).

```json
{
  "timestamp": "2026-04-14T19:05:22.318Z",
  "level": "CRITICAL",
  "logger": "orange_core.i5_verifier",
  "message": "NEVER_AUTO policy violation blocked",
  "trace_id": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
  "error": {
    "failure_code": "OC_I5_POLICY_BLOCK",
    "category": "I5_DECISION",
    "severity": "P1",
    "never_auto": true,
    "message": "Policy gate denied output (safety rule SR-03)",
    "stack": "…(프레임 축약)"
  },
  "context": {
    "pipeline_state": "S3",
    "gate": "PolicyGate",
    "request_id": "req_0192ab",
    "user_role": "P1"
  },
  "recovery": {
    "fallback_attempted": ["FB_POLICY_MASK"],
    "fallback_result": "blocked_by_never_auto",
    "escalated_to": "I-20.HumanReview",
    "confidence_penalty": -0.20
  }
}
```

**WARN 레벨 예시** (Fallback 성공):
```json
{
  "timestamp": "2026-04-14T19:07:41.102Z",
  "level": "WARN",
  "logger": "cond.evaluator",
  "message": "COND_BATCH_TIMEOUT recovered via FB_REDUCE_BATCH",
  "trace_id": "00-…",
  "error": {"failure_code": "COND_BATCH_TIMEOUT", "category": "COND", "severity": "P3", "never_auto": false},
  "context": {"pipeline_state": "S2", "batch_size_before": 64, "batch_size_after": 32},
  "recovery": {"fallback_attempted": ["FB_REDUCE_BATCH"], "fallback_result": "success", "confidence_penalty": -0.05}
}
```

---

## §10. Phase별 복구 흐름 (Phase 1→2→3→4)

```
Phase 1 (Perceive / Intake)        Phase 2 (Reason / Plan+Gate)      Phase 3 (Act / Execute)         Phase 4 (Verify+Learn)
───────────────────────────────    ──────────────────────────────    ─────────────────────────────   ──────────────────────────────
 FM_ERR_* (P3 / ERROR)              OC_I1/I2/I3 (P2 / ERROR-WARN)     OC_I4_*, TL_ERR_*, TOOL_       MC_ERR_*, RAG_*, OC_I5_EVID_
   → FB_REJECT_INPUT /                 → FB_INTENT_HEURISTIC /           TIMEOUT (P2-P3 / WARN-ERR)   INSUFFICIENT (P2 / ERROR)
     FB_MASK_AND_CONFIRM               FB_RAG_RETRY_EXPAND /              → FB_RETRY_SOFT /            → FB_RAG_RETRY_EXPAND /
                                       FB_ASK_CLARIFICATION                FB_AUTO_REPAIR             FB_SHOW_STALE
                                                                              ↓ 재시도 한계               ↓ QoD 미달
 (실패 시)                           GT_ERR_COST_LIMIT / OC_ERR_*       TL_ERR_403 → FB_REJECT_INPUT   EXP_SELF_EVO_REGRESSION
   downgrade → S6 Deliver              (P1-P2 / ERROR)                   / FB_DENY_WITH_REASON         → FB_EVO_ROLLBACK
   confidence penalty −0.02               → FB_COST_DOWNSHIFT /           (confidence −0.10)            (confidence −0.10)
                                         FB_REQUIRE_APPROVAL

                                    ▼ NEVER_AUTO 3코드 발생 시 (P0-P1 / CRITICAL) ▼
                                    어떤 Phase 에서든 즉시 I-20 Escalation → HITL → S3a Approve Wait(600s)
                                    confidence penalty −0.20 (Fallback 성공 여부 무관)
```

### 다운그레이드 시 confidence penalty 표 (P1-5 §5 연동)

| 레벨 | 발생 조건 | penalty |
|------|----------|---------|
| WARN → 요청 완료 | Fallback 1 hop 성공 | **−0.02** |
| WARN → 요청 완료 | Fallback 2 hop 이상 (재시도 포함) | **−0.05** |
| ERROR | FailureCode 발생 + Fallback 성공 (복구됨) | **−0.10** |
| ERROR (복구 실패) | Fallback 모두 실패, 사용자 응답 불가 | **−0.15** |
| CRITICAL / NEVER_AUTO | `OC_I5_POLICY_BLOCK / POLICY_DENY / PII_LONGTERM_DENIED` | **−0.20** |

---

## §11. ABC 패턴 매핑 (정본 준수)

본 파일은 사양 레지스트리로서 실행 로직이 없으므로 **새 ABC 정의를 추가하지 않는다**. FailureCode 소비자 측 ABC 시그니처는 다음과 같이 **정본(`00_common/base_verifier_abc.md`, `base_reasoning_engine_abc.md`) 의 기존 시그니처를 그대로 사용**한다:

| ABC | 정본 메서드 시그니처 (변경 금지) | 용도 |
|-----|------------------------------|------|
| `BaseVerifier` | `async verify(self, request: VerifyRequest) -> VerifyResult` (timeout 은 `VerifyRequest.timeout_ms`) | Gate 검증 결과에서 `failure_code` 필드 채움 |
| `BaseReasoningEngine` | `async reason(self, request: ReasoningRequest, *, timeout_ms: int) -> ReasoningResult` | 추론 실패 시 `result.failure_code` 채움 |

- `VerifyResult` / `ReasoningResult` 에는 **optional `failure_code: Optional[str]`** 필드가 본 레지스트리의 §4 코드 집합을 값 도메인으로 가진다(P1-4 `namespace_rules.md` §12 정합).
- 새 시그니처 추가/변경 금지 (규칙 (h) 정본 준수).

---

## §12. 복잡도 / 연산 특성

본 레지스트리 자체는 **상수 조회 테이블**이다.
- 코드 조회: `O(1)` (48-entry dict 해시 조회).
- 네임스페이스별 집계: `O(48)` (전수 순회, 로드 시 1회 캐싱).
- NEVER_AUTO 판정: `O(1)` (3-entry set `in` 체크, `NeverAutoDetector.NEVER_AUTO_CODES` 참조).
- Fallback 힌트 조회: `O(1)` (본 파일 스냅샷). 최종 1:N 매핑은 P1-8 `fc_fb_mapping.md` 에서 `O(1)` dict-of-list.

LOCK 값 참조:
- `LOCK-EL-03 = 48` → §2 / §4 전수 카운트 일치.
- `LOCK-EL-06 = {OC_I5_POLICY_BLOCK, POLICY_DENY, PII_LONGTERM_DENIED}` → §5 3-row 일치.
- `LOCK-EL-07 = {DEBUG, INFO, WARN, ERROR, CRITICAL}` → §4 권고 레벨 컬럼 도메인.

---

## §13. 세션 간 인터페이스 cross-check

| 상대 산출물 | 인터페이스 | 일치 확인 |
|-----------|-----------|----------|
| P1-1 `event_schema.md` | `payload.failure_code: str?` 필드 타입 | ✅ 본 §4 코드 집합을 값 도메인으로 사용 (소비 측 제약) |
| P1-2 `event_type_registry.md` | 이벤트 코드(oc.*/wf.*/...) 에 failure_code 연계 | ✅ 이벤트 코드 ≠ FailureCode (네임스페이스 분리) — `cl.rt.fast_gate.blocked` 등은 이벤트 코드, 차단 사유는 `payload.failure_code` 로 기재 |
| P1-3 `pipeline_state_map.md` | 각 상태의 on_error 에 FailureCode 연결 | ✅ §10 Phase 흐름이 S0~S8 와 일치, S3 Gate 에서 `OC_I5_*` 등 발행 |
| P1-4 `namespace_rules.md` | FailureCode 접두어 vs 이벤트 네임스페이스 분리 | ✅ FC 는 네임스페이스 개념 외, payload 필드. 접두어 `OC_I*/FM/OC_ERR/TL_ERR/MC_ERR/COND/RAG/SDAR/LLAMAGUARD/EXP_*` 전용. |
| P1-5 `log_level_spec.md` §4.1 | 그룹별 기본 레벨 매핑 | ✅ §4 `권고 레벨` 컬럼이 §4.1 규약을 인용 (특례는 `notes` 및 §7 에 기록) |
| P1-5 `log_level_spec.md` §6.2 | `EscalationPayload` 11필드 정본 | ✅ 본 §8.1 가 정본을 그대로 인용 (재정의 금지), §8.2 에서 FailureCode 관점 필드 규약만 추가 |
| P1-7 `fallback_registry.md` | `first_fallback_hint` 의 FB action_id 존재성 | ⚠️ P1-7 작성 후 교차 검증 필수. 본 파일 스냅샷은 Part2 §6.11 원문 기준 (35건 FB 전수 존재해야 함). |
| P1-8 `fc_fb_mapping.md` | FC 48 전수 매핑 (1:N) | ✅ 본 파일 §4 의 48 row 전수를 P1-8 에서 참조. P1-8 테이블의 primary FB 가 본 파일 `1차 FB 힌트` 와 일치해야 함. |
| P1-9 `never_auto_detector.md` | LOCK-EL-06 3코드 + 5규칙 | ✅ §5 3-row 와 P1-9 `NEVER_AUTO_CODES` set 동일해야 함 |

> 인터페이스 불일치 감지 시 `[INTERFACE_MISMATCH: <설명>]` 마커로 보고한다. **현재 발견된 불일치 없음** (P1-5~P1-4 까지만 존재하므로 P1-7/8/9 작성 시점 재검증).

---

## §14. Phase 2 통합 테스트 시나리오 (≥10 — 12건)

> 각 시나리오는 주입 방법(Given) + 기대 결과(Then) 로 구성.

| # | 시나리오 | 주입 | 기대 결과 |
|---|----------|------|----------|
| T-01 | **48항목 전수 등록 검증** | 레지스트리 dump 후 set 크기 측정 | `len(registry) == 48` AND 중복 코드 0 AND 접두어 집계 = §2 소계 |
| T-02 | **LOCK-EL-03 일치** | §2 소계 합산 | `sum(subtotals) == 48` (36+12) |
| T-03 | **NEVER_AUTO 3코드 정확성** | `{e.code for e in registry if e.never_auto}` 추출 | `== {"OC_I5_POLICY_BLOCK","POLICY_DENY","PII_LONGTERM_DENIED"}` (LOCK-EL-06) |
| T-04 | **NEVER_AUTO 레벨 격상** | `OC_I5_POLICY_BLOCK` / `POLICY_DENY` / `PII_LONGTERM_DENIED` 이벤트 발행 | 실제 로그 `level == "CRITICAL"` AND `error.never_auto == true` AND I-20 escalation 발송 확인 |
| T-05 | **FM_ERR_PII 마스킹 경로** | FrontMini 에 PII 포함 입력 | `FM_ERR_PII` (P1/ERROR) + `FB_MASK_AND_CONFIRM` 실행 → 마스킹된 입력 재수락 AND confidence penalty −0.10 |
| T-06 | **OC_I2_TIMEOUT 소프트 재시도** | RAG 호출 인위적 지연 | `FB_RETRY_SOFT` → 성공 시 WARN + penalty −0.02; 실패 시 ERROR + penalty −0.10 |
| T-07 | **OC_I5_COST_OVER_BUDGET 다운시프트** | CostBudget 초과 요청 주입 | `FB_COST_DOWNSHIFT` 실행, 모델 경량화, penalty −0.10 |
| T-08 | **COND_BATCH_TIMEOUT → FB_REDUCE_BATCH** (V2) | batch_size=128 인위적 timeout | `batch_size=64` 로 재시도, WARN, penalty −0.05 |
| T-09 | **LLAMAGUARD_GPU_UNAVAIL CPU fallback** (V2) | GPU 비활성 모의 | `FB_GUARD_CPU_FALLBACK` (INT4) 실행, ERROR, 응답 지연 허용, penalty −0.10 |
| T-10 | **EXP_A2A_AUTH_FAIL 재시도 3회** (V3) | mTLS 키 회전 직후 호출 | `FB_A2A_RETRY` 3회 시도, 성공 시 WARN, 실패 시 ERROR |
| T-11 | **Fallback 누락 감지 (R-612-3)** | 임의 FC 추가 후 FB 매핑 미수 | CI 체크에서 `[MAPPING_MISSING: <code>]` 에러 차단 |
| T-12 | **NEVER_AUTO 탐지 규칙 누락 감지 (R-612-4)** | FC 에 `never_auto=True` 추가 후 P1-9 탐지기 미갱신 | CI 체크에서 `[DETECTOR_MISSING: <code>]` 에러 차단 |

---

## §15. 변경 이력

| 일자 | 버전 | 변경 내용 | 세션 |
|------|------|----------|------|
| 2026-04-14 | v1.0.0 | 초기 작성 — 48항목 전수 등록, LOCK-EL-03/06/07 연동, P1-5 §4.1 규약 적용, Phase 2 테스트 12건, 교차참조 11건, NEVER_AUTO 3코드 격상 규칙, R-612-3/4 확장 규칙 | P1-6 |
| 2026-04-14 | v1.0.1 | step2 재검증 1-pass — (1) §10 Phase 흐름 `TL_ERR_403` 1차 FB 표기를 §4.9 row 32 및 Part2 §6.11 L5921 정본(`FB_REJECT_INPUT` / `FB_DENY_WITH_REASON`) 과 일치하도록 교정 (정합성 규칙 j), (2) §8 EscalationPayload 정의를 P1-5 §6.2 정본 11필드 그대로 인용으로 변경(자체 dataclass 폐기) + §8.2 FailureCode 관점 필드 사용 규약 추가, (3) §13 cross-check 행에 P1-5 §6.2 EscalationPayload 인터페이스 일치 확인 행 추가 | P1-6 |

---

## §16. 자체 검증 체크리스트

- [x] 총 항목 수 48개 (D2.1-D2 36 + Part2 V2/V3 12) — §2 / §4 확인
- [x] 각 항목별 코드명·설명·심각도·권고 로깅레벨 기재 — §4.1~§4.12
- [x] NEVER_AUTO 해당 항목(LOCK-EL-06) 표시 — §4.5 row13, §4.6 row18/19 + §5
- [x] LOCK-EL-03 참조 명시 — Header + §2 + §16
- [x] P1-5 (log_level_spec.md) 상호 참조 링크 포함 — §0 + §4 권고 레벨 + §13
- [x] 교차 참조 블록 — §0
- [x] 공통 자료 구조 선정의 — §3 `FailureCodeEntry`
- [x] Phase별 복구 흐름도 + confidence penalty 표 — §10
- [x] EscalationPayload 구조 — §8
- [x] 로깅 포맷 (R-01-7, 중첩 JSON, `error{} / context{} / recovery{} / trace_id`) — §9
- [x] Phase 2 테스트 시나리오 ≥10 — §14 (12건)
- [x] 예외 처리 정책 표 — §7
- [x] ABC 시그니처 정본 준수 — §11 (변경 없음, 정본 인용만)
- [x] 세션 간 인터페이스 cross-check 표 — §13
