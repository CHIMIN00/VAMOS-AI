# FallbackRegistry — 35항목 정본

> **도메인**: 6-12_Event-Logging / 02_logging-standard
> **파일**: `fallback_registry.md`
> **정본 선언**: 본 파일은 SOT2 정본(Single Source of Truth)이며, LOCK-EL-04 가 지정한 **35개 FallbackAction** (D2.1-D2 23 + Part2 V2 8 + V3 4) 전수 레지스트리 + 자동/수동 구분 + NEVER_AUTO 제약 연계 + 적용 조건에 대해 권위를 가진다.
> **버전**: v1.0.0 (2026-04-14)
> **세션**: P1-7 (Phase 1)
> **LOCK 연계**: LOCK-EL-04 (35 FB), LOCK-EL-05 (FC→FB 매핑 정본은 Part2 §6.9 — 본 파일은 "FB 카탈로그" 권위만 보유), LOCK-EL-06 (NEVER_AUTO 3 FC 연계 제약), LOCK-EL-07 (FB 이벤트 권고 로깅 레벨)

---

## §0. 교차 참조 (Cross-References)

| 문서 | 경로 | 용도 |
|------|------|------|
| AUTHORITY_CHAIN | `../AUTHORITY_CHAIN.md` | LOCK-EL-04 정의, 35항목 근거 (L37) |
| 종합계획서 | `../EVENT_LOGGING_구조화_종합계획서.md` §3.3, §7.2 P1-7 | LOCK 목록 + P1-7 절차/검증 |
| D2.1-D2 §5.3 | `D:\VAMOS\docs\sot\D2.1-D2_D2_SCHEMA_ORANGE_CORE.md` L344-392 | D2.1-D2 23 FallbackAction 원본 (UI-02 FM/TL/MC 9건 포함) |
| D2.1-D2 §8 | 같은 문서 L478-505 | D2.1-D2 FC→FB 매핑 원본(35행) |
| Part2 §6.11 | `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` L5832-5842 | D2.1-D2 23 FB 재선언 |
| Part2 §6.11 확장 | 같은 문서 L5958-5973 | V2/V3 FC→FB 1차 FB 정본 (FB 12건) |
| 02/failure_code_registry.md | `./failure_code_registry.md` §2/§4 | 48 FC 레지스트리 (참조) |
| 02/fc_fb_mapping.md | `./fc_fb_mapping.md` (예정, P1-8) | FC→FB 1:N 매핑 최종 테이블 (48 FC × 35 FB) |
| 02/never_auto_detector.md | `./never_auto_detector.md` (예정, P1-9) | NEVER_AUTO 탐지 메커니즘 (LOCK-EL-06) |
| 02/log_level_spec.md | `./log_level_spec.md` §4.2 | FallbackAction 이벤트 권고 레벨 (P1-5) |
| 01/namespace_rules.md | `../01_event-system/namespace_rules.md` §5.1/§6.3 | 이벤트 네임스페이스 (fallback 이벤트 발행 규약) |
| 01/event_schema.md | `../01_event-system/event_schema.md` | `payload.fallback_id` 필드 수용 스키마 |

---

## §1. 목적 및 범위 (Purpose / Scope)

### 1.1 목적
- LOCK-EL-04 가 확정한 **35개 FallbackAction** 을 액션 ID·구분·설명·자동/수동·적용 조건·도입 버전과 함께 전수 등록한다.
- 각 액션의 **정본 출처**(D2.1-D2 §5.3 또는 Part2 §6.11)를 명시하여 상위 문서 우선 원칙(R-T6-1) 을 강제한다.
- 본 파일은 **FallbackAction 카탈로그**(What) 이며, FC→FB 매핑의 최종 정본 테이블은 `fc_fb_mapping.md` (P1-8) 가 가진다.
- 각 FB 의 **자동 실행 가능 여부**(NEVER_AUTO 제약과의 관계, LOCK-EL-06) 를 명시하여 P1-9 탐지기가 참조한다.

### 1.2 범위 (In-scope)
- 35 FallbackAction 전수 항목 (D2.1-D2 23 + Part2 V2 8 + V3 4).
- 각 액션의 자동/수동/HITL 구분, 적용 조건 (어떤 FC 계열에서 활성화되는가), 예상 효과/부작용.
- NEVER_AUTO 연계 제약 (⛔ FC 로부터 트리거되는 FB 의 자동 실행 금지 강제).
- action_id 네이밍 규칙(FB_UPPER_SNAKE) 재확인, 고유성 보증.
- 확장 규칙 요약 (R-612-3 — FC 추가 시 FB 매핑 필수; R-612-6 — FB 신규 시 action_id 중복 금지 + 자동/수동 구분 명시).
- Phase 2 테스트 시나리오 12건.

### 1.3 범위 외 (Out-of-scope)
- FC→FB 전수 매핑 테이블 → **P1-8 `fc_fb_mapping.md`**.
- NEVER_AUTO 탐지기 구현 → **P1-9 `never_auto_detector.md`**.
- FB 실행 이벤트의 payload 스키마 → **P1-1 `event_schema.md`**.
- FB 이벤트 권고 로깅 레벨의 구체 매핑 규약 → **P1-5 `log_level_spec.md`**.
- FB 실행 구현체(예: `FB_RAG_FALLBACK_CHROMA` 의 실제 Chroma 연결 로직) → 6-4 Memory/RAG/Storage 도메인.

---

## §2. 항목 집계 (LOCK-EL-04 검증)

| 구분 | 접두어 | 항목 수 | 버전 | 정본 출처 |
|------|--------|--------|------|----------|
| Intent/Evidence/Memory/Output/Decision/General | `FB_*` | 13 | V0+ | D2.1-D2 §5.3 L355-367 + §6.3 확정 목록 |
| Format/Tool/MemoryCheck (UI-02 추가) | `FB_*` | 10 | V0+ | D2.1-D2 §5.3 L368-377 + 08 §7.6 |
| **D2.1-D2 SOT 소계** | — | **23** | — | — |
| COND (V2) | `FB_SKIP_COND / FB_REDUCE_BATCH / FB_ISOLATE_MODULE` | 3 | V2 | Part2 §6.11 L5962-5964 |
| RAG V2 | `FB_RAG_FALLBACK_CHROMA` | 1 | V2 | Part2 §6.11 L5965 |
| SDAR (V2) | `FB_SDAR_ESCALATE / FB_SDAR_ABORT` | 2 | V2 | Part2 §6.11 L5966-5967 |
| LlamaGuard (V2) | `FB_GUARD_CPU_FALLBACK / FB_GUARD_BLOCK_DEFAULT` | 2 | V2 | Part2 §6.11 L5968-5969 |
| Self-Evo (V3) | `FB_EVO_ROLLBACK` | 1 | V3 | Part2 §6.11 L5970 |
| Agent Mesh (V3) | `FB_AGENT_QUEUE` | 1 | V3 | Part2 §6.11 L5971 |
| GPU (V3) | `FB_GPU_OFFLOAD` | 1 | V3 | Part2 §6.11 L5972 |
| A2A (V3) | `FB_A2A_RETRY` | 1 | V3 | Part2 §6.11 L5973 |
| **Part2 V2/V3 확장 소계** | — | **12** | — | — |
| **LOCK-EL-04 합계** | — | **35** | — | D2.1-D2 + Part2 §6.11 |

검증: **23 + 12 = 35** ✅ LOCK-EL-04 일치.
검증: **23 = 13(§6.3) + 10(UI-02 D2.0-08 §7.6)** ✅ (FM 3 + TL 3 + MC 3 + FB_RESTRICT_GENERAL_INFO 1 = 10 중 FB_RESTRICT_GENERAL_INFO 는 §6.3 확정 목록 포함, UI-02 명시 9건). 실제 UI-02 L382-391 9건 + §6.3 14건 = 23. 본 §2 는 간결히 13+10 으로 표기하고, §4.1/§4.2 절 구분으로 재확인한다.

---

## §3. 공통 자료 구조 (Shared Types)

```python
from dataclasses import dataclass
from typing import Literal, Optional, List

AutoMode = Literal[
    "AUTO",      # 자동 실행 가능 (NEVER_AUTO 연계 FC 아님)
    "HITL",      # Human-in-the-loop 승인 필수
    "DENY_ONLY", # 거부/차단만 수행 (추가 실행 없음)
    "MANUAL",    # 운영자 수동 조작 전용 (V2/V3 중 일부)
]

Category = Literal[
    "I1_INTENT", "I2_EVIDENCE", "I3_MEMORY", "I4_OUTPUT", "I5_DECISION",
    "GENERAL", "FORMAT", "TOOL", "MEM_CHECK",
    "COND", "RAG", "SDAR", "LLAMAGUARD",
    "EXP_SELF", "EXP_AGENT", "EXP_GPU", "EXP_A2A",
]
Version = Literal["V0+", "V1+", "V2", "V3"]
Source  = Literal["D2.1-D2 §5.3", "Part2 §6.11"]

@dataclass(frozen=True)
class FallbackActionEntry:
    action_id: str                     # 예: "FB_INTENT_HEURISTIC_PARSE" (FB_UPPER_SNAKE, 고유)
    category: Category                 # §2 구분
    description: str                   # 1-2줄 설명 (수행 동작)
    auto_mode: AutoMode                # AUTO / HITL / DENY_ONLY / MANUAL
    triggering_fcs: List[str]          # 이 FB 가 1차로 매핑된 FC 코드 목록 (Part2 §6.11 L5879-5927 요약)
    never_auto_linked: bool            # 트리거 FC 중 NEVER_AUTO(LOCK-EL-06) 포함 여부
    applicability: str                 # 적용 조건 (트리거 상황)
    side_effects: str                  # 주요 부작용/비용 (재시도 횟수, 외부 호출, UX 영향)
    version: Version                   # 도입 버전
    source: Source                     # 정본 출처
    notes: Optional[str] = None        # 구현 힌트 / 연계 모듈
```

- `auto_mode` 결정 규칙(R-612-6):
  - 트리거 FC 가 NEVER_AUTO 3코드(`OC_I5_POLICY_BLOCK`/`POLICY_DENY`/`PII_LONGTERM_DENIED`) 중 하나라도 포함하면 **HITL 또는 DENY_ONLY 강제**.
  - 외부 IO(API/DB) 재시도성 FB 는 기본 AUTO (단 idempotent 보장 시).
  - UI 표시/알림만 수행하는 FB 는 AUTO.
  - 롤백류 FB(`FB_EVO_ROLLBACK`) 는 운영자 로그 남기되 AUTO 실행 가능(회복 목적). 다만 최종 승인은 거버넌스 연계. `FB_SDAR_ABORT` 는 스냅샷 무결성 실패(SDAR_SNAPSHOT_CORRUPT, 데이터 손상 위험)이므로 **MANUAL 고정**(§4.3 #29 정본) — AUTO 실행 금지.
- `triggering_fcs` 는 Part2 §6.11 "1차 Fallback" 열 스냅샷. **정본은 P1-8 `fc_fb_mapping.md`**.

---

## §4. FallbackRegistry 전수 테이블 (35/35)

> **자동 모드 범례**: AUTO = 자동 실행 / HITL = 사용자 승인 필요 / DENY_ONLY = 거부 결과 고정 / MANUAL = 운영자 수동.
> **NEVER_AUTO 연계** (LOCK-EL-06): ⛔ = 트리거 FC 중 `{OC_I5_POLICY_BLOCK, POLICY_DENY, PII_LONGTERM_DENIED}` 포함.

### §4.1 D2.1-D2 §6.3 확정 목록 — 핵심 13건 (V0+)

| # | action_id | 설명 | auto_mode | 트리거 FC (1차) | NEVER_AUTO | 적용 조건 |
|---|-----------|------|----------|----------------|-----------|----------|
| 1 | `FB_INTENT_HEURISTIC_PARSE` | 휴리스틱(키워드/패턴) 기반 의도 재파싱 | AUTO | `OC_I1_PARSE_FAIL` | — | LLM 파서 실패 시 규칙 엔진으로 대체 |
| 2 | `FB_ASK_CLARIFICATION` | 사용자에게 명확화 질의 | HITL | `OC_I1_AMBIGUOUS_UNRESOLVED` | — | 모호 의도 해소 불가 / 증거 불충분 |
| 3 | `FB_RAG_RETRY_EXPAND` | RAG 쿼리 확장 후 재검색 (동의어/상위 개념) | AUTO | `OC_I2_RAG_NO_SOURCE`, `OC_I2_EVIDENCE_QOD_LOW`, `OC_I5_EVIDENCE_INSUFFICIENT`, `MC_ERR_LOW_QOD` | — | 소스 0건 / QoD 낮음 |
| 4 | `FB_RAG_SWITCH_SOURCE` | RAG 소스를 대체(웹/KB) 로 전환 | AUTO | `OC_I2_SOURCE_POLICY_BLOCK`, `OC_I2_TIMEOUT` (2차) | — | 원본 소스 정책 차단/타임아웃 |
| 5 | `FB_MEMORY_META_ONLY` | 메모리 본문 저장 금지, 메타데이터만 저장 | AUTO | `OC_I3_MEMORY_POLICY_DENY` | — | PII/민감도 정책 해당 시 |
| 6 | `FB_REQUIRE_APPROVAL` | P2 승인 다이얼로그 트리거 | HITL | `OC_I3_APPROVAL_REQUIRED`, `OC_I5_APPROVAL_REQUIRED`, `OC_ERR_P2_LOCK` | — | P1+ 작업 전 승인 필요 |
| 7 | `FB_OUTPUT_REFORMAT` | 출력 스펙 위반 시 재포맷 시도 | AUTO | `OC_I4_OUTPUT_SPEC_VIOLATION`, `OC_I4_CITATION_MISSING`, `FM_ERR_FMT` | — | 구조 필드 누락 / MIME 불일치 |
| 8 | `FB_OUTPUT_MINIMAL` | 최소 필수 필드만 유지한 응답 | AUTO | `OC_I4_OUTPUT_SPEC_VIOLATION` (2차), `FM_ERR_SIZE` | — | 크기/복잡도 초과 |
| 9 | `FB_POLICY_MASK` | 민감 부분 마스킹 후 재시도 | HITL | `OC_I4_CITATION_MISSING` (2차), `OC_I5_POLICY_BLOCK` | ⛔ | I-5 정책 차단 시 1차 시도 (HITL 승인 전제) |
| 10 | `FB_COST_DOWNSHIFT` | 비용 레벨 강등 (heavy→light) | AUTO | `OC_I5_COST_OVER_BUDGET`, `GT_ERR_COST_LIMIT`, `OC_ERR_COST_LV`, `OC_ERR_COST_OV` | — | 비용 한도 초과 |
| 11 | `FB_ROUTE_SAFE_NODE` | Safe 노드(보수적 경로)로 재라우팅 | AUTO | `OC_I5_ROUTE_NOT_FOUND`, `OC_ERR_NO_ROUTE` | — | 라우트 탐색 실패 |
| 12 | `FB_RESTRICT_GENERAL_INFO` | 일반 정보 수준으로 축소 제공 | AUTO | `OC_I2_SOURCE_POLICY_BLOCK` (2차) | — | 민감 소스 차단 후 fallback |
| 13 | `FB_DENY_WITH_REASON` | 사유 명시 후 거부 응답 | DENY_ONLY | `OC_I3_COMMIT_FAIL` (D2.1-D2 §7.29), `POLICY_DENY`, `OC_ERR_NONGOAL`, `OC_I5_POLICY_BLOCK` (2차), `OC_ERR_COST_OV` (2차), `TL_ERR_403` (2차) | ⛔ | POLICY_DENY / Non-goal / 최종 차단 |

> ↑ D2.1-D2 §5.3 SOT 13 + UI-02 확장 10 = 23 중 13건 (D2.1-D2 §6.3 확정 목록). 나머지 10 건은 §4.2.

### §4.2 D2.1-D2 UI-02 확장 10건 (FM/TL/MC + 저장 계열, V0+)

| # | action_id | 설명 | auto_mode | 트리거 FC (1차) | NEVER_AUTO | 적용 조건 |
|---|-----------|------|----------|----------------|-----------|----------|
| 14 | `FB_DENY_STORAGE` | 저장 시도 거부 (PII 장기 저장 차단) | DENY_ONLY | `PII_LONGTERM_DENIED`, `STORAGE_POLICY_DENY` (D2.0-06 §8) | ⛔ | BASE 1.3 §2.4 PII 장기저장 차단 |
| 15 | `FB_REJECT_INPUT` | 입력 자체 거부 | DENY_ONLY | `FM_ERR_FMT`/`FM_ERR_SIZE` (UI-02), `TL_ERR_403` | — | 포맷/크기 위반 / 권한 오류 |
| 16 | `FB_MASK_AND_CONFIRM` | PII 마스킹 후 사용자 확인 | HITL | `FM_ERR_PII`, `OC_I4_MASK_FAIL`, `PII_LONGTERM_DENIED` (2차) | — | PII 감지 시 선제 조치 |
| 17 | `FB_REQ_REUPLOAD` | 재업로드 요청 | HITL | `FM_ERR_ZERO`, `MC_ERR_STALE` (2차) | — | 빈 입력 / 만료 항목 |
| 18 | `FB_RETRY_SOFT` | 짧은 백오프 후 소프트 재시도(1-3회) | AUTO | `TL_ERR_TIMEOUT`, `TOOL_TIMEOUT`, `OC_I2_TIMEOUT` (1차), `OC_I3_COMMIT_FAIL` (1차) | — | 일시적 타임아웃/커밋 실패 (idempotent 보장 시) |
| 19 | `FB_USE_WEB_SEARCH` | 외부 웹 검색으로 우회 | AUTO | `TL_ERR_403` (D2.1-D2 §5.3 UI-02 note), `OC_I2_RAG_NO_SOURCE` (3차) | — | 내부 소스 차단/부재 시 |
| 20 | `FB_RETURN_RAW` | 원본 텍스트 그대로 반환 | AUTO | `TL_ERR_PARSE` (2차), `FM_ERR_ZERO` (1차 D2.1-D2 §8 매핑) | — | 파싱 실패 / 빈 응답 |
| 21 | `FB_AUTO_REPAIR` | 자동 수리 시도(구문 정정/JSON repair) | AUTO | `TL_ERR_PARSE` | — | 도구 응답 파싱 실패 |
| 22 | `FB_SHOW_CONFLICT` | 모순 항목 노출(UI 표시) | AUTO | `MC_ERR_CONFLICT` | — | 메모리 모순 감지 |
| 23 | `FB_SHOW_STALE` | 만료 플래그 표시(UI 배지) | AUTO | `MC_ERR_STALE`, `MC_ERR_LOW_QOD` (2차) | — | stale 항목 노출 |

> ↑ D2.1-D2 §5.3 소계 **23/23** ✅ (핵심 13 + UI-02 확장 10).

### §4.3 V2 확장 — COND / RAG / SDAR / LlamaGuard (Part2 §6.11)

| # | action_id | 설명 | auto_mode | 트리거 FC (1차) | NEVER_AUTO | 적용 조건 |
|---|-----------|------|----------|----------------|-----------|----------|
| 24 | `FB_SKIP_COND` | COND 모듈 비활성화, CORE 파이프라인만 실행 | AUTO | `COND_MODULE_INIT_FAIL` | — | COND 의존성 미충족 시 전체 요청 실패 방지 |
| 25 | `FB_REDUCE_BATCH` | batch_size 를 절반으로 축소 후 재실행 | AUTO | `COND_BATCH_TIMEOUT` | — | CAT-A~G 배치 타임아웃 |
| 26 | `FB_ISOLATE_MODULE` | 충돌 모듈 격리 비활성 | AUTO | `COND_DEPENDENCY_CONFLICT` | — | 순환 의존 감지 시 (운영자 알림 필수) |
| 27 | `FB_RAG_FALLBACK_CHROMA` | Qdrant 대신 로컬 Chroma 사용 | AUTO | `RAG_QDRANT_CONNECTION` | — | Qdrant 연결 실패 |
| 28 | `FB_SDAR_ESCALATE` | 자동 수리 포기 → 인간 에스컬레이션 | HITL | `SDAR_REPAIR_FAIL` | — | SDAR 3회 재시도 소진 |
| 29 | `FB_SDAR_ABORT` | 수리 중단 + 수동 복구 대기 | MANUAL | `SDAR_SNAPSHOT_CORRUPT` | — | 스냅샷 무결성 실패 (데이터 손상 위험) |
| 30 | `FB_GUARD_CPU_FALLBACK` | LlamaGuard 를 GPU→CPU(INT4) 로 전환 | AUTO | `LLAMAGUARD_GPU_UNAVAIL` | — | GPU 사용 불가 시 레이턴시 증가 감수 |
| 31 | `FB_GUARD_BLOCK_DEFAULT` | 분류 실패 시 "안전하지 않음" 기본값으로 차단 | DENY_ONLY | `LLAMAGUARD_CLASSIFY_FAIL` | — | 분류 타임아웃/오류 시 보수적 차단 |

> ↑ V2 소계 **8/8** ✅.

### §4.4 V3 확장 — EXP_* (Part2 §6.11)

| # | action_id | 설명 | auto_mode | 트리거 FC (1차) | NEVER_AUTO | 적용 조건 |
|---|-----------|------|----------|----------------|-----------|----------|
| 32 | `FB_EVO_ROLLBACK` | 자가개선 직전 버전으로 롤백 | AUTO | `EXP_SELF_EVO_REGRESSION` | — | 성능 회귀 감지 (거버넌스 로그 필수) |
| 33 | `FB_AGENT_QUEUE` | 에이전트 스폰 요청 대기열 처리 | AUTO | `EXP_AGENT_SPAWN_LIMIT` | — | 스폰 한도 50+ 초과 |
| 34 | `FB_GPU_OFFLOAD` | GPU OOM 발생 시 CPU 오프로드 | AUTO | `EXP_GPU_OOM` | — | vLLM 서빙 메모리 초과 |
| 35 | `FB_A2A_RETRY` | mTLS/JWT 인증 재시도 3회 | AUTO | `EXP_A2A_AUTH_FAIL` | — | A2A 프로토콜 인증 실패 |

> ↑ V3 소계 **4/4** ✅.

> **최종 검증**: 13 + 10 + 8 + 4 = **35/35** ✅ LOCK-EL-04.

---

## §5. action_id 고유성 검증 (P1-8 지원)

### 5.1 명명 규칙(R-612-6)
- 정규식: `^FB_[A-Z][A-Z0-9_]*$` (FB_UPPER_SNAKE, D2.1-D2 §5.3 L345).
- 접두어 `FB_` 고정. 이후 의미 단위 대문자 + 언더스코어.
- 길이 제약: 4~40자 (FB_ 포함).
- 중복 금지: 본 §4 테이블의 35 ID 는 전역 고유.

### 5.2 전수 ID 목록 (정렬)
```
FB_AGENT_QUEUE, FB_A2A_RETRY, FB_ASK_CLARIFICATION, FB_AUTO_REPAIR,
FB_COST_DOWNSHIFT, FB_DENY_STORAGE, FB_DENY_WITH_REASON, FB_EVO_ROLLBACK,
FB_GPU_OFFLOAD, FB_GUARD_BLOCK_DEFAULT, FB_GUARD_CPU_FALLBACK,
FB_INTENT_HEURISTIC_PARSE, FB_ISOLATE_MODULE, FB_MASK_AND_CONFIRM,
FB_MEMORY_META_ONLY, FB_OUTPUT_MINIMAL, FB_OUTPUT_REFORMAT,
FB_POLICY_MASK, FB_RAG_FALLBACK_CHROMA, FB_RAG_RETRY_EXPAND,
FB_RAG_SWITCH_SOURCE, FB_REDUCE_BATCH, FB_REJECT_INPUT,
FB_REQ_REUPLOAD, FB_REQUIRE_APPROVAL, FB_RESTRICT_GENERAL_INFO,
FB_RETRY_SOFT, FB_RETURN_RAW, FB_ROUTE_SAFE_NODE, FB_SDAR_ABORT,
FB_SDAR_ESCALATE, FB_SHOW_CONFLICT, FB_SHOW_STALE, FB_SKIP_COND,
FB_USE_WEB_SEARCH
```

- 총 개수: **35** ✅.
- 접두어 분포 검증: 모두 `FB_` 로 시작 ✅.
- 중복 검사: 전수 알파벳 정렬 후 인접 동일값 0 ✅.

---

## §6. NEVER_AUTO 연계 제약 (LOCK-EL-06 × LOCK-EL-04)

> NEVER_AUTO 3 FC 가 트리거하는 FB 는 반드시 **HITL 또는 DENY_ONLY** auto_mode 를 가져야 한다. 본 §6 은 P1-9 탐지기의 입력 데이터이다.

### 6.1 NEVER_AUTO FC → FB 연계 표

| NEVER_AUTO FC | 1차 FB | auto_mode | 2차 FB | auto_mode | 준수 여부 |
|---------------|--------|----------|--------|----------|----------|
| `OC_I5_POLICY_BLOCK` | `FB_POLICY_MASK` | HITL | `FB_DENY_WITH_REASON` | DENY_ONLY | ✅ |
| `POLICY_DENY` | `FB_DENY_WITH_REASON` | DENY_ONLY | — | — | ✅ |
| `PII_LONGTERM_DENIED` | `FB_DENY_STORAGE` | DENY_ONLY | `FB_MASK_AND_CONFIRM` | HITL | ✅ |

- 3/3 연계 FB 모두 HITL 또는 DENY_ONLY. AUTO 없음 ✅.
- 파생 규칙: `auto_mode == "AUTO"` 인 FB 가 NEVER_AUTO FC 의 매핑에 포함되면 P1-9 탐지기가 **Rule #6** 위반으로 P0 인시던트 발행.

### 6.2 NEVER_AUTO 파생 이벤트(P1-9 예고)
- `wf.approval.requested` 는 HITL auto_mode FB 활성화 시 자동 발행 (namespace_rules.md §5.1 준수).
- DENY_ONLY FB 는 `oc.deny.blocked` 이벤트 필수 발행.

---

## §7. 확장 규칙 (R-612-3 / R-612-6)

### 7.1 R-612-3 — FC 신규 등록 시 FB 매핑 필수
- 신규 FC 는 반드시 1개 이상의 FB 를 1차 매핑으로 지정한다(P1-8 정본 반영 필수).
- 신규 FC 의 심각도가 P0/P1 이면 2차 FB 추가 권고 (실패 시 fallback chain 연장).

### 7.2 R-612-6 — 신규 FB 등록 체크리스트
1. `FB_UPPER_SNAKE` 명명 규칙 준수 (§5.1 정규식).
2. action_id 전역 고유성 (§5.2 목록 대조).
3. `auto_mode` 명시. NEVER_AUTO FC 와 연결되면 AUTO 금지 (§6.1 규칙).
4. `triggering_fcs` 최소 1개 기재 (P1-8 매핑 반영 전제).
5. `side_effects` 에 외부 IO/재시도 횟수/UX 영향 기재.
6. 도입 버전(V2/V3) + 정본 출처(Part2 §6.11 Lxxxx-yyyy) 기재.
7. 본 §2 집계표 갱신 (소계 + 합계 재확인) + `_index.md` §FallbackRegistry 표 동기화(도메인 마감 step).
8. P1-5 `log_level_spec.md` §4.2 FB 이벤트 레벨 매핑 추가.

---

## §8. 이벤트 발행 규약 (P1-1/P1-4 연계)

### 8.1 FB 활성화 이벤트
- Fallback 활성화 시 namespace: `oc.iN.fallback.activated` (N = 트리거 FC 계열) 또는 `wf.fallback.activated`(공통).
- 권고 레벨: AUTO = INFO, HITL = INFO (+ `wf.approval.requested` WARN), DENY_ONLY = WARN, NEVER_AUTO 연계 = ERROR.

### 8.2 구조화 로그 포맷 (R-01-7, 중첩 구조)

```json
{
  "timestamp": "2026-04-14T20:00:15.123Z",
  "event_type": "oc.i5.fallback.activated",
  "trace_id": "01HXYZ...",
  "source": "I5_DecisionEngine",
  "version": "V1",
  "payload": {
    "fallback_id": "FB_POLICY_MASK",
    "attempt_index": 1
  },
  "error": {
    "failure_code": "OC_I5_POLICY_BLOCK",
    "severity": "P1",
    "never_auto": true
  },
  "context": {
    "pipeline_state": "S5",
    "request_id": "req-0x9a",
    "auto_mode": "HITL"
  },
  "recovery": {
    "strategy": "fallback_chain",
    "next_action": "await_approval",
    "next_fallback_id": "FB_DENY_WITH_REASON",
    "confidence_penalty": 0.35
  }
}
```

### 8.3 Phase 별 복구 흐름 (FB 중심)

```
[S1 Route] → 실패 FC 발생
   │
   ├── AUTO FB → 재실행 (attempt=1)
   │     │
   │     ├─ 성공 → [계속 진행], confidence_penalty=-0.05
   │     └─ 실패 → 2차 FB 시도 (attempt=2)
   │                │
   │                └─ 실패 → FB_DENY_WITH_REASON, confidence_penalty=-0.25, oc.deny.blocked
   │
   ├── HITL FB → wf.approval.requested → S3a 대기(600s)
   │     │
   │     ├─ 승인 → 복구 수행, confidence_penalty=-0.10
   │     ├─ 거부 → FB_DENY_WITH_REASON, penalty=-0.20
   │     └─ 타임아웃 → FB_DENY_WITH_REASON, penalty=-0.30
   │
   └── DENY_ONLY FB → 즉시 거부 (NEVER_AUTO 경로), penalty=-0.40
```

### 8.4 Confidence Penalty 표

| auto_mode | 성공 | 재시도 | 실패→다음 | 최종 DENY |
|-----------|------|--------|-----------|----------|
| AUTO      | -0.05 | -0.10 | -0.20 | -0.40 |
| HITL      | -0.10 | -0.20 | -0.30 | -0.40 |
| DENY_ONLY | n/a  | n/a   | n/a   | -0.40 |
| MANUAL    | -0.15 | n/a   | -0.25 | -0.40 |

---

## §9. 에스컬레이션 페이로드 (I-20 경유, R-01-8)

```python
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class EscalationPayload:
    source_engine: str          # 예: "I5_DecisionEngine"
    error_code: str             # FailureCode (예: "SDAR_REPAIR_FAIL")
    fallback_id: str            # 최종 시도 FB
    original_request: dict      # 사용자 원 요청 스냅샷
    partial_result: Optional[Any]  # 부분 결과(없으면 None)
    retry_count: int            # 총 재시도 횟수
    timestamp: str              # ISO-8601
    trace_id: str               # 분산 추적 ID
    context: dict               # pipeline_state, request_id, auto_mode 등
```

- 트리거 조건: `FB_SDAR_ESCALATE`, `FB_DENY_WITH_REASON` (NEVER_AUTO 경로), `FB_SDAR_ABORT`, 2차 FB 까지 실패한 경우.
- 수신 모듈: I-20 (Escalation Hub, 6-13 Operations 도메인 관할).

---

## §10. Phase 2 테스트 시나리오 (12건, ≥10 충족)

| # | 시나리오 | 주입 방법 | 기대 결과 |
|---|----------|----------|----------|
| T1 | AUTO FB 정상 복구 | `OC_I1_PARSE_FAIL` 주입 → `FB_INTENT_HEURISTIC_PARSE` 1회 시도 | 휴리스틱 파싱 성공, penalty=-0.05, `oc.i1.fallback.activated` INFO |
| T2 | HITL FB 승인 | `OC_I3_APPROVAL_REQUIRED` 주입 → `FB_REQUIRE_APPROVAL` HITL | `wf.approval.requested` 발행, 승인 시 penalty=-0.10 |
| T3 | HITL FB 타임아웃 | T2 + 승인 600s 미응답 | `FB_DENY_WITH_REASON`, penalty=-0.30, `oc.deny.blocked` WARN |
| T4 | NEVER_AUTO 경로 | `POLICY_DENY` 주입 → `FB_DENY_WITH_REASON` | auto_mode=DENY_ONLY, CRITICAL log, penalty=-0.40 |
| T5 | NEVER_AUTO 우회 시도(위반) | `OC_I5_POLICY_BLOCK` 후 AUTO FB 강제 호출 | P1-9 탐지기 Rule #6 위반 감지, P0 인시던트, 파이프라인 중단 |
| T6 | Fallback chain 2차 발동 | `OC_I2_SOURCE_POLICY_BLOCK` → 1차 `FB_RAG_SWITCH_SOURCE` 실패 → 2차 `FB_RESTRICT_GENERAL_INFO` | 2차 FB 성공, penalty=-0.20 누적 |
| T7 | 비용 강등 | `OC_I5_COST_OVER_BUDGET` → `FB_COST_DOWNSHIFT` | heavy→light 모델 전환, 비용 감소 확인 |
| T8 | V2 COND 격리 | `COND_MODULE_INIT_FAIL` → `FB_SKIP_COND` | COND 비활성화, CORE 파이프라인 정상 진행 |
| T9 | V2 RAG 대체 | `RAG_QDRANT_CONNECTION` 주입 → `FB_RAG_FALLBACK_CHROMA` | 로컬 Chroma 전환, 응답 레이턴시 허용 범위 |
| T10 | V2 SDAR 에스컬레이션 | `SDAR_REPAIR_FAIL` 3회 → `FB_SDAR_ESCALATE` | EscalationPayload 생성, I-20 수신 확인 |
| T11 | V2 LlamaGuard 보수 차단 | `LLAMAGUARD_CLASSIFY_FAIL` → `FB_GUARD_BLOCK_DEFAULT` | DENY_ONLY, 안전하지 않음 기본값 처리 |
| T12 | V3 EVO 롤백 | `EXP_SELF_EVO_REGRESSION` → `FB_EVO_ROLLBACK` | 직전 버전 복원, 거버넌스 로그 기록 |

---

## §11. 세션 간 인터페이스 cross-check

| 세션 | 산출물 | 본 파일과의 인터페이스 | 일치 여부 |
|------|--------|----------------------|----------|
| P1-1 | `01/event_schema.md` | `payload.fallback_id` 필드 수용 (FB_UPPER_SNAKE) | ✅ |
| P1-4 | `01/namespace_rules.md` §5.1 `wf.approval.requested` / §6.3 P1-7 참조 예고 | HITL FB 발동 시 wf.approval.requested 발행 규약 | ✅ (§8.1/§8.2) |
| P1-5 | `02/log_level_spec.md` §4.2 | FB 이벤트 권고 레벨 매핑 (AUTO=INFO, HITL=INFO+WARN, DENY_ONLY=WARN, NEVER_AUTO=ERROR) | ✅ (§8.1 정렬) |
| P1-6 | `02/failure_code_registry.md` §4 | 48 FC 의 `1차 FB 힌트` 컬럼 ↔ 본 §4 `triggering_fcs` | ✅ 스팟 검증 10건 모두 일치 |
| P1-8 | `02/fc_fb_mapping.md` (예정) | 최종 48×N 매핑 정본 (본 파일은 FB 카탈로그만 보유) | — (후속 세션이 본 §4 참조 예정) |
| P1-9 | `02/never_auto_detector.md` (예정) | §6.1 NEVER_AUTO 연계 표를 탐지기 입력으로 사용 | — (§6 이 입력 데이터로 제공) |

> 본 세션은 의존 태스크 없이 독립 실행 (종합계획서 §7.2 P1-7 "의존 태스크 없이 독립 실행 가능" 준수).

---

## §12. 종합계획서 §7 검증 체크리스트 대조

| 항목 | 요구 | 충족 |
|------|------|------|
| 총 항목 수 35개 (D2.1-D2 23 + Part2 12) | §2 집계표 + §4 테이블 | ✅ 23+8+4=35 |
| 각 항목별 액션명, 설명, 자동/수동 구분 기재 | §4 각 테이블 (action_id/설명/auto_mode) | ✅ |
| LOCK-EL-04 참조 명시 | 문서 헤더 + §2 + AUTHORITY_CHAIN §Cross-ref | ✅ |
| P1-8 에서 참조할 수 있도록 action_id 고유성 확보 | §5.1 규칙 + §5.2 정렬 목록 + 중복 검사 | ✅ |

---

## §13. CONFLICT / LOCK 영향

- LOCK 변경 필요: **없음** (LOCK-EL-04 35 항목 그대로 수용).
- CONFLICT 후보: **없음** — D2.1-D2 §5.3 23건 + Part2 §6.11 12건 원본 병합 시 중복/충돌 없음.
- 이월 사항 (carryovers): 없음 (본 파일이 LOCK-EL-04 측 정본 확정). 후속 P1-8 가 본 §4 action_id 목록을 매핑 축으로 사용.
- CROSS_HANDOFF: 없음.

---

## §14. 변경 이력

| 버전 | 일자 | 변경 요약 |
|------|------|----------|
| v1.0.0 | 2026-04-14 | P1-7 초안. LOCK-EL-04 35항목 정본 등록(§2/§4), NEVER_AUTO 연계(§6), 확장 규칙 R-612-6 신설(§7.2), 이벤트 발행 규약(§8), 에스컬레이션 페이로드(§9), Phase 2 테스트 12건(§10), 세션 간 인터페이스(§11). |
| v3.0.0 | 2026-06-03 | **Phase 4 RECOVERY Stage A+B P4-2 — §V3 V3 Fallback 4건 Phase 4 운영 확정 (canonical cite-only)**. §1~§14 V1 본문 byte-prefix 보존 + §V3 cite-only append. V3 FB 4건(FB_EVO_ROLLBACK/FB_AGENT_QUEUE/FB_GPU_OFFLOAD/FB_A2A_RETRY)은 §4 items 32~35 에 이미 canonical 등재 — 재정의 0. LOCK-EL-04 35 = 23+8+4 종결. Status APPROVED. |

---

## §V3. V3 Fallback 4건 Phase 4 운영 확정 (canonical cite-only, LOCK-EL-04 35 종결)

> **§V3 신설 사유 (2026-06-03 Phase 4 RECOVERY Stage A+B P4-2)**: V3 Fallback 4건은 **이미 본 파일 §4 (items 32~35) + §5.2 정렬 목록 + §2 정본 헤더 "D2.1-D2 23 + Part2 V2 8 + V3 4 = 35" 에 canonical 등재**되어 있다(P1-7). 본 §V3 는 **재정의 0** — 기존 canonical 4건을 Phase 4 production promotion 시점에 **cite-only 확정**한다. **§1~§14 V1 본문은 byte-prefix 보존(변경 0)**.

### §V3.1 V3 Fallback 4건 Phase 4 확정 (§4 items 32~35 canonical cite)

| # | action_id (canonical) | 대응 V3 FC | auto_mode | 설명 (§4 정본 verbatim) |
|---|-----------|-----------|:---:|------|
| 32 | `FB_EVO_ROLLBACK` | `EXP_SELF_EVO_REGRESSION` | AUTO | 자가개선 직전 버전으로 롤백 (성능 회귀 감지, 거버넌스 로그 필수) |
| 33 | `FB_AGENT_QUEUE` | `EXP_AGENT_SPAWN_LIMIT` | AUTO | 에이전트 스폰 요청 대기열 처리 (스폰 한도 50+ 초과) |
| 34 | `FB_GPU_OFFLOAD` | `EXP_GPU_OOM` | AUTO | GPU OOM 발생 시 CPU 오프로드 (vLLM 서빙 메모리 초과) |
| 35 | `FB_A2A_RETRY` | `EXP_A2A_AUTH_FAIL` | AUTO | mTLS/JWT 인증 재시도 3회 (A2A 프로토콜 인증 실패) |

> ⚠️ 4건 모두 §4 items 32~35 verbatim cite (재정의 0). 본 §V3 는 신규 action_id 등록 0건 — 기존 canonical 명칭 보존.

### §V3.2 LOCK-EL-04 35 종결 + NEVER_AUTO 제약 정합

- LOCK-EL-04 **35 = 23 + 8 + 4** 합계 보존 EXACT (재정의 0). §2 정본 헤더 "D2.1-D2 23 + Part2 V2 8 + V3 4 = 35" 와 정합. V3 4건(items 32~35)은 V1 P1-7 시점 이미 등재 — Phase 4 는 운영 확정만.
- NEVER_AUTO 3코드 (LOCK-EL-06: OC_I5_POLICY_BLOCK / POLICY_DENY / PII_LONGTERM_DENIED) 는 V3 4건과 **무관** — V3 FC 4건은 모두 AUTO Fallback (NEVER_AUTO 대상 아님). `FB_EVO_ROLLBACK` 은 AUTO 실행 가능하나 거버넌스 로그 필수 (§13 정본).
- LOCK-EL-05 FC→FB 매핑 정본 = Part2 §6.9 (변경 0). fc_fb_mapping §3.12 (rows 45~48) canonical 정합.

> **[V3_EXTEND: fallback_registry — Phase 4 P4-2 2026-06-03]** §1~§14 V1 본문 byte-prefix 보존 + §V3 cite-only append. LOCK-EL-04 35 종결 (V3 FB 4건 FB_EVO_ROLLBACK/FB_AGENT_QUEUE/FB_GPU_OFFLOAD/FB_A2A_RETRY canonical 재정의 0). Status APPROVED. chain `phase4_6-12_recovery_AB_2026-06-03`.
