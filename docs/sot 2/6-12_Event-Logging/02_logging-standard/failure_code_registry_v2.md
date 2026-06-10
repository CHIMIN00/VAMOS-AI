# FailureCodeRegistry V2 — V2 FailureCode 8건 상세 운영 명세 + R-612-3 매핑 (V2-Phase 2)

> **도메인**: 6-12_Event-Logging / 02_logging-standard
> **파일**: `failure_code_registry_v2.md`
> **정본 선언**: 본 파일은 SOT2 정본(Single Source of Truth)이며, V1 `failure_code_registry.md` §4.11 가 코드명·구분으로 등재한 **V2 FailureCode 8건** (COND_* 3 + RAG_* 1 + SDAR_* 2 + LLAMAGUARD_* 2) 의 **운영 가능 상세 명세** (트리거 조건, Pydantic validator, FC→FB 매핑 R-612-3 정합, Phase 2 테스트 시나리오) 에 대해 권위를 가진다.
> **버전**: v1.0 (2026-04-29, P2-3 신규 — V2-Phase 2 태그)
> **세션**: P2-3 (Phase 2)
> **LOCK 연계**: LOCK-EL-03 (FailureCodeRegistry 48항목, V2 단계 36→44 갱신, V3 4건은 Phase 3 이월), LOCK-EL-04 (FallbackRegistry 35항목, 본 V2 FB 8건 V1 §4.3 등재 정합), LOCK-EL-05 (FC→FB 매핑 정본 = Part2 §6.9 — 본 파일은 V2 8 FC 1:1 매핑 명세), LOCK-EL-06 (NEVER_AUTO 3코드 — V2 8 FC NEVER_AUTO 0건), LOCK-EL-07 (로깅 레벨 5단계 — P2-2 §5.2 권고 매핑 정합)
> **★ 별도 V2 NEW 파일 방안 (a) 채택**: V1 `failure_code_registry.md` byte-prefix SHA UNCHANGED 통산 보존 안전. 4-3/6-2/6-1/6-8 V2 NEW 분리 패턴 계승.

---

## §0. 교차 참조 (Cross-References)

| 문서 | 경로 | 용도 |
|------|------|------|
| AUTHORITY_CHAIN | `../AUTHORITY_CHAIN.md` | LOCK-EL-03 / L4 / L5 / L6 / L7 정의, 도메인 경계 (6-5 SDAR FC→FB 실행 W-1 RESOLVED) |
| 종합계획서 §6 / §7.3 | `../EVENT_LOGGING_구조화_종합계획서.md` §6 ISS-5 / §7.3 P2-3 | I-5 (FailureCode 확장 관리 미정의, MEDIUM) → R-612-3 (FC 추가 시 ≥1 FB 매핑 필수) |
| 02/failure_code_registry.md (V1) | `./failure_code_registry.md` §2 (48 합계) + §4.11 (V2 8 FC row) + §4.12 (V3 4 FC row) | V1 정본 — 코드명/구분/심각도/권고 레벨/1차 FB 힌트 baseline (본 V2 NEW 파일이 상세화) |
| 02/fallback_registry.md (V1) | `./fallback_registry.md` §4.3 V2 8 FB row | V2 FB 8건 정본 (FB_SKIP_COND / FB_REDUCE_BATCH / FB_ISOLATE_MODULE / FB_RAG_FALLBACK_CHROMA / FB_SDAR_ESCALATE / FB_SDAR_ABORT / FB_GUARD_CPU_FALLBACK / FB_GUARD_BLOCK_DEFAULT) |
| 02/fc_fb_mapping.md (V1) | `./fc_fb_mapping.md` | FC→FB 1:N 매핑 최종 정본 (48 FC 전수, V1) — 본 V2 NEW 파일 §3 V2 8 FC 매핑 정합 |
| 02/log_level_spec.md (V1) | `./log_level_spec.md` §4.1 | FailureCode → 로깅 레벨 매핑 규약 |
| 02/never_auto_detector.md (V1) | `./never_auto_detector.md` | NEVER_AUTO 탐지 5규칙 (LOCK-EL-06, V2 8 FC 모두 NEVER_AUTO ❌) |
| 03/structured_logging.md (P2-2) | `../03_trace-context/structured_logging.md` §5.2 | FC 권고 레벨 매핑 정본 (P2 권고 WARN, P1 ERROR/WARN 등) |
| 03/trace_propagation.md (P2-1) | `../03_trace-context/trace_propagation.md` §6.4 | LOCK-EL-08 위반 시 신규 FC `EL_EVT_NO_TRACE_CONTEXT` (P2-1 신규 권고) |
| 01/event_schema.md | `../01_event-system/event_schema.md` §3.1 EventEnvelope | `payload.failure_code` 필드 수용 스키마 |
| Part2 §6.11 | `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` L5962-5969 | V2 FC 8건 정본 출처 + L5875-5927 FC→FB 매핑 정본 (R-T6-1 우선) |
| D2.1-D2 §5.2 | `D:\VAMOS\docs\sot\D2.1-D2_D2_SCHEMA_ORANGE_CORE.md` L291-342 | D2.1-D2 36 FailureCode 원본 (V2 8 FC 는 Part2 §6.11 확장, D2.1-D2 baseline 변경 ❌) |

---

## §1. 목적 및 범위 (Purpose / Scope)

### 1.1 목적
- V1 `failure_code_registry.md` §4.11 가 코드명·구분·1차 FB 힌트로 등재한 **V2 FailureCode 8건** (COND_* 3 + RAG_* 1 + SDAR_* 2 + LLAMAGUARD_* 2) 의 **운영 가능 상세 명세** 를 V2-Phase 2 단계에서 확정한다.
- 각 FC 의 **트리거 조건** (코드 검출 시점, 임계값, 발생 빈도 추정), **Pydantic validator** (FC payload 스키마), **FC→FB 매핑 상세** (R-612-3 정합, 1:N 매핑 시 우선순위), **Phase 2 통합 테스트 시나리오** (각 FC 당 ≥ 2건) 를 정의한다.
- LOCK-EL-03 의 V2 단계 갱신: V1 §2 합계 표 "D2.1-D2 SOT 소계 36 + Part2 V2/V3 확장 12 = 48" 보존, 본 V2 NEW 는 "**36 + V2 8 = 44**" 부분 (V3 4건은 Phase 3 이월) 의 운영 명세를 기여.
- LOCK-EL-05 (FC→FB 매핑 정본 = Part2 §6.9) **재정의 ❌**, 본 파일은 운영 측면 매핑 매트릭스만 제공.
- ISS-5 (P-4: FailureCode 확장 관리 미정의, MEDIUM) → R-612-3 (FC 추가 시 ≥ 1 FB 매핑 필수) 해소.
- exit_gate "03 서브폴더 전 파일 작성 완료 + V2 FailureCode 갱신" 의 V2 FailureCode 갱신 부분 충족.

### 1.2 범위 (In-scope)
- V2 FC 8건 운영 명세: 코드명, 트리거 조건 (코드 위치 / 임계값 / 발생 빈도 추정), 심각도, 권고 레벨, FB 매핑, Pydantic validator, Phase 2 테스트 시나리오.
- FC→FB 매핑 R-612-3 매트릭스 (V2 8 FC × 1+ FB = 8건 매핑).
- V1 baseline 정합 (V1 §4.11 row 8 + V1 §4.3 fallback row 8 + V1 §4 fc_fb_mapping 정합).
- 6-5 SDAR-System cross-handoff (W-1 RESOLVED — 6-12 레지스트리 / 6-5 실행).
- 11 CONSUMER 적용 가이드 (각 namespace 별 FC 발행 시점, 참조만).
- CFL-EL-001 sdar.repair.started 검토 메모 (P2-3 시점 결정 ❌, STEP_C R round 시점 결정 — LOCK-EL-02 134→135 또는 sdar.* 승격).

### 1.3 범위 외 (Out-of-scope)
- V3 FC 4건 (`EXP_SELF_EVO_REGRESSION` / `EXP_AGENT_SPAWN_LIMIT` / `EXP_GPU_OOM` / `EXP_A2A_AUTH_FAIL`) → **Phase 3 이월** (P3-2 `failure_code_registry_v3.md` 또는 V2 EXTEND).
- V1 `failure_code_registry.md` §4.1~§4.10 D2.1-D2 36 FC 본문 수정 ❌ (V1 byte-prefix SHA UNCHANGED 엄수).
- FB 실행 구현체 (예: `FB_RAG_FALLBACK_CHROMA` 의 실제 Chroma 연결 로직) → 6-4 Memory-RAG-Storage 또는 6-5 SDAR-System 도메인.
- NEVER_AUTO 탐지 알고리즘 → V1 `never_auto_detector.md` (P1-9 정본).
- FC payload 의 비즈니스 로직 처리 → 각 CONSUMER 도메인 (1-1 / 2-2 / 6-5 등 자체 STEP_C 결정).

---

## §2. LOCK 정본 인용 (verbatim)

### §2.1 LOCK-EL-03 5-field verbatim 인용 (AUTHORITY_CHAIN §LOCK 레지스트리 L3)

| 필드 | 값 |
|------|-----|
| **LOCK ID** | `LOCK-EL-03` |
| **항목** | FailureCodeRegistry 항목 수 |
| **값** | 48항목 (D2.1-D2 36 + Part2 §6.11 V2/V3 12) |
| **정본 출처** | D2.1-D2 + Part2 §6.11 |
| **서브폴더 매핑** | 02 (`02_logging-standard/`) |

### §2.2 LOCK-EL-04 / L5 / L6 / L7 연계 인용 (verbatim)

| LOCK ID | 항목 | 값 | 본 V2 NEW 파일 기여 |
|---------|------|-----|------------------|
| `LOCK-EL-04` | FallbackRegistry 항목 수 | 35항목 (23+12) | V2 FB 8건 V1 §4.3 정합 (FB 정의 변경 ❌) |
| `LOCK-EL-05` | FC→FB 매핑 정본 | Part2 §6.9 선언, §6.11 테이블 | V2 8 FC × 1+ FB 매핑 매트릭스 (운영 측면, 정본 = Part2) |
| `LOCK-EL-06` | NEVER_AUTO 대상 코드 | OC_I5_POLICY_BLOCK / POLICY_DENY / PII_LONGTERM_DENIED | V2 8 FC 모두 NEVER_AUTO ❌ (V1 §5 정합) |
| `LOCK-EL-07` | 로깅 레벨 정의 | DEBUG / INFO / WARN / ERROR / CRITICAL (5단계) | V2 8 FC 권고 레벨 (P2-2 §5.2 매트릭스 정합: P2 → WARN, P1 → ERROR/WARN) |

### §2.3 LOCK 보호 규칙
- 본 V2 NEW 파일에서 LOCK-EL-03 / L4 / L5 / L6 / L7 의 **재정의 / 추가 / 변경 0건** 엄수.
- LOCK-EL-03 합계 48 보존 (V2 단계 운영 명세는 36→44 부분 기여, V3 4건은 Phase 3 이월).
- 충돌 시 우선순위: `R-T6-1 Part2 §6.11 (정본) > AUTHORITY §LOCK > 본 파일 §3~§5` (정본 우선).
- V2 8 FC 코드명 / 1차 FB 힌트 / 심각도 / 권고 레벨은 V1 `failure_code_registry.md` §4.11 정본 100% 보존, 본 파일은 **운영 측면 상세화** 만 추가.

### §2.4 R-612-3 보호 규칙 (FC 추가 시 ≥ 1 FB 매핑 필수)

| R-612-3 의무 | 본 V2 NEW 파일 적용 |
|------------|------------------|
| 신규 FC 등재 시 동시 FB 매핑 등재 의무 | V2 8 FC 모두 V1 §4.3 fallback_registry V2 8 FB 등재 완료 + 본 §3 매트릭스 1:1 매핑 정합 |
| 매핑 0건 등재 ❌ | 본 §3 V2 8 FC × 1+ FB = 8건 매핑 정합 |
| FC 정의 변경 시 매핑 동시 갱신 | V2 8 FC 정의는 V1 §4.11 정본 보존 (변경 ❌), 본 V2 NEW 는 운영 명세만 추가 |

---

## §3. V2 FailureCode 8건 상세 운영 명세

### §3.1 FC 1: `COND_MODULE_INIT_FAIL` — COND 모듈 초기화 실패 (의존성 미충족)

| 항목 | 값 |
|------|-----|
| 코드 | `COND_MODULE_INIT_FAIL` |
| 구분 | COND (V2) |
| V1 row | `failure_code_registry.md` §4.11 row 37 |
| 정본 출처 | Part2 §6.11 L5962 |
| 심각도 | P2 (중간) |
| 권고 레벨 | WARN (P2-2 §5.2 매트릭스) |
| NEVER_AUTO | ❌ (LOCK-EL-06 3코드 외) |
| 1차 FB | `FB_SKIP_COND` (AUTO, V1 §4.3 row 24) |
| Trigger 코드 위치 | `src/orange_core/cond_modules/__init__.py` `_init_module()` |
| Trigger 조건 | (a) Python import 실패 (의존 패키지 부재) **또는** (b) Pydantic config validation 실패 **또는** (c) 외부 리소스 (Vector DB / API key) 부재 |
| 발생 빈도 추정 | 운영 환경 < 1 / month (배포 직후 환경 변수 미설정 시 집중) |
| Pydantic payload schema | 본 §3.1.1 |
| Phase 2 테스트 | 본 §3.1.2 (2건) |

#### §3.1.1 Pydantic payload schema

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional

class CondModuleInitFailPayload(BaseModel):
    """COND_MODULE_INIT_FAIL payload (V2 V2-Phase 2)"""
    failure_code: Literal["COND_MODULE_INIT_FAIL"] = "COND_MODULE_INIT_FAIL"
    module_id: str = Field(..., description="실패한 COND 모듈 ID (예: cond_a_pydantic, cond_g_factcheck)")
    init_stage: Literal["import", "config_validation", "external_resource"] = Field(
        ..., description="실패한 단계"
    )
    error_type: str = Field(..., description="Python exception class name")
    error_message: str = Field(..., max_length=512)
    missing_dependency: Optional[str] = Field(None, description="ImportError 시 누락 모듈명")
    config_field: Optional[str] = Field(None, description="config_validation 시 실패 필드")
    retry_count: int = Field(default=0, ge=0, le=3)
    severity: Literal["P2"] = "P2"
    level: Literal["WARN"] = "WARN"
```

#### §3.1.2 Phase 2 테스트 시나리오

| TS-ID | 시나리오 | 주입 방법 | 기대 결과 |
|-------|---------|---------|---------|
| TS-COND-INIT-1 | 의존 패키지 부재 | `pip uninstall pydantic` 후 cond_a 모듈 import | `COND_MODULE_INIT_FAIL`(init_stage="import", missing_dependency="pydantic") + FB_SKIP_COND AUTO 활성 |
| TS-COND-INIT-2 | config validation 실패 | 환경변수 `COND_BATCH_SIZE=invalid_int` 설정 | `COND_MODULE_INIT_FAIL`(init_stage="config_validation", config_field="batch_size") + FB_SKIP_COND |

---

### §3.2 FC 2: `COND_BATCH_TIMEOUT` — CAT-A~G 배치 처리 타임아웃

| 항목 | 값 |
|------|-----|
| 코드 | `COND_BATCH_TIMEOUT` |
| 구분 | COND (V2) |
| V1 row | §4.11 row 38 |
| 정본 출처 | Part2 §6.11 L5963 |
| 심각도 | P3 (정보) |
| 권고 레벨 | WARN (P3 정보지만 운영 알림 가치) |
| NEVER_AUTO | ❌ |
| 1차 FB | `FB_REDUCE_BATCH` (AUTO, V1 §4.3 row 25 — batch_size 절반 축소 후 재실행) |
| Trigger 코드 위치 | `src/orange_core/cond_modules/batch_executor.py` `_run_batch()` |
| Trigger 조건 | 단일 배치 처리 시간 ≥ 30초 (default timeout, 환경변수 `COND_BATCH_TIMEOUT_SEC` 으로 조정 가능) |
| 발생 빈도 추정 | 운영 환경 < 5 / day (대량 입력 시 일시적) |
| Pydantic payload schema | 본 §3.2.1 |
| Phase 2 테스트 | 본 §3.2.2 (2건) |

#### §3.2.1 Pydantic payload schema

```python
class CondBatchTimeoutPayload(BaseModel):
    """COND_BATCH_TIMEOUT payload (V2)"""
    failure_code: Literal["COND_BATCH_TIMEOUT"] = "COND_BATCH_TIMEOUT"
    module_id: str = Field(..., description="타임아웃 발생 COND 모듈 ID")
    batch_size: int = Field(..., ge=1)
    timeout_threshold_sec: float = Field(default=30.0, gt=0)
    elapsed_sec: float = Field(..., gt=0, description="실제 처리 경과 시간")
    cat_distribution: dict = Field(default_factory=dict, description="CAT-A~G 처리 진행률 (모듈별 0~1.0)")
    retry_count: int = Field(default=0, ge=0, le=3)
    severity: Literal["P3"] = "P3"
    level: Literal["WARN"] = "WARN"
```

#### §3.2.2 Phase 2 테스트 시나리오

| TS-ID | 시나리오 | 주입 방법 | 기대 결과 |
|-------|---------|---------|---------|
| TS-COND-BATCH-1 | 타임아웃 트리거 | batch_size=1000 + 모듈 처리 지연 시뮬레이션 (sleep 35s) | `COND_BATCH_TIMEOUT`(elapsed_sec≥30, batch_size=1000) + FB_REDUCE_BATCH (batch_size=500 재실행) |
| TS-COND-BATCH-2 | FB_REDUCE_BATCH 재실행 성공 | TS-COND-BATCH-1 후 batch_size=500 자동 재실행 | 정상 완료, retry_count=1, 후속 INFO 로그 |

---

### §3.3 FC 3: `COND_DEPENDENCY_CONFLICT` — COND 모듈 간 순환 의존 감지

| 항목 | 값 |
|------|-----|
| 코드 | `COND_DEPENDENCY_CONFLICT` |
| 구분 | COND (V2) |
| V1 row | §4.11 row 39 |
| 정본 출처 | Part2 §6.11 L5964 |
| 심각도 | P2 (중간) |
| 권고 레벨 | WARN |
| NEVER_AUTO | ❌ |
| 1차 FB | `FB_ISOLATE_MODULE` (AUTO, V1 §4.3 row 26 — 충돌 모듈 격리 비활성, 운영자 알림 필수) |
| Trigger 코드 위치 | `src/orange_core/cond_modules/dependency_resolver.py` `detect_cycles()` (DAG 검증) |
| Trigger 조건 | COND 모듈 의존 그래프에서 cycle 검출 (DFS 알고리즘, O(V+E)) |
| 발생 빈도 추정 | 매우 드뭄 (< 1 / quarter, 신규 모듈 추가 직후 집중 — 통합 테스트로 사전 차단) |
| Pydantic payload schema | 본 §3.3.1 |
| Phase 2 테스트 | 본 §3.3.2 (2건) |

#### §3.3.1 Pydantic payload schema

```python
class CondDependencyConflictPayload(BaseModel):
    """COND_DEPENDENCY_CONFLICT payload (V2)"""
    failure_code: Literal["COND_DEPENDENCY_CONFLICT"] = "COND_DEPENDENCY_CONFLICT"
    cycle_modules: list[str] = Field(..., min_length=2, description="순환 의존 발생 모듈 목록 (최소 2개)")
    cycle_path: list[str] = Field(..., description="순환 경로 (예: [cond_a, cond_b, cond_c, cond_a])")
    isolated_module: str = Field(..., description="FB_ISOLATE_MODULE 격리 대상 모듈 (cycle 진입점)")
    operator_notified: bool = Field(default=False, description="운영자 알림 발송 여부")
    severity: Literal["P2"] = "P2"
    level: Literal["WARN"] = "WARN"
```

#### §3.3.2 Phase 2 테스트 시나리오

| TS-ID | 시나리오 | 주입 방법 | 기대 결과 |
|-------|---------|---------|---------|
| TS-COND-DEP-1 | 순환 의존 감지 | cond_a → cond_b → cond_a 의존 정의 후 dependency_resolver 실행 | `COND_DEPENDENCY_CONFLICT`(cycle_modules=["cond_a", "cond_b"]) + FB_ISOLATE_MODULE + 운영자 알림 |
| TS-COND-DEP-2 | DAG 검증 통과 | 정상 의존 그래프 (트리 구조) | FC 발행 ❌, 정상 처리 |

---

### §3.4 FC 4: `RAG_QDRANT_CONNECTION` — Qdrant 벡터 DB 연결 실패

| 항목 | 값 |
|------|-----|
| 코드 | `RAG_QDRANT_CONNECTION` |
| 구분 | RAG V2 |
| V1 row | §4.11 row 40 |
| 정본 출처 | Part2 §6.11 L5965 |
| 심각도 | P2 (중간) |
| 권고 레벨 | WARN |
| NEVER_AUTO | ❌ |
| 1차 FB | `FB_RAG_FALLBACK_CHROMA` (AUTO, V1 §4.3 row 27 — Qdrant 대신 로컬 Chroma 사용) |
| Trigger 코드 위치 | `src/rag/vector_store/qdrant_client.py` `connect()` (gRPC / HTTP 핸드셰이크) |
| Trigger 조건 | (a) Qdrant 서버 연결 timeout ≥ 5초 **또는** (b) 인증 실패 (API key invalid) **또는** (c) 컬렉션 미존재 (404) |
| 발생 빈도 추정 | 운영 환경 < 2 / week (네트워크 일시 단절 시 집중) |
| Pydantic payload schema | 본 §3.4.1 |
| Phase 2 테스트 | 본 §3.4.2 (2건) |

#### §3.4.1 Pydantic payload schema

```python
class RagQdrantConnectionPayload(BaseModel):
    """RAG_QDRANT_CONNECTION payload (V2)"""
    failure_code: Literal["RAG_QDRANT_CONNECTION"] = "RAG_QDRANT_CONNECTION"
    qdrant_endpoint: str = Field(..., description="Qdrant 서버 endpoint (예: http://qdrant:6333)")
    error_type: Literal["timeout", "auth_failure", "collection_not_found", "network_error"]
    timeout_threshold_sec: float = Field(default=5.0)
    elapsed_sec: float = Field(..., ge=0)
    collection_name: Optional[str] = Field(None)
    fallback_to_chroma: bool = Field(default=True, description="FB_RAG_FALLBACK_CHROMA 활성 여부")
    severity: Literal["P2"] = "P2"
    level: Literal["WARN"] = "WARN"
```

#### §3.4.2 Phase 2 테스트 시나리오

| TS-ID | 시나리오 | 주입 방법 | 기대 결과 |
|-------|---------|---------|---------|
| TS-RAG-QDRANT-1 | Qdrant 연결 timeout | qdrant 컨테이너 stop 후 RAG 검색 호출 | `RAG_QDRANT_CONNECTION`(error_type="timeout") + FB_RAG_FALLBACK_CHROMA + Chroma 결과 정상 반환 |
| TS-RAG-QDRANT-2 | 컬렉션 미존재 | 존재하지 않는 collection_name 으로 검색 호출 | `RAG_QDRANT_CONNECTION`(error_type="collection_not_found") + FB_RAG_FALLBACK_CHROMA |

---

### §3.5 FC 5: `SDAR_REPAIR_FAIL` — SDAR 자동수리 실패 (3회 재시도 소진)

| 항목 | 값 |
|------|-----|
| 코드 | `SDAR_REPAIR_FAIL` |
| 구분 | SDAR (V2) |
| V1 row | §4.11 row 41 |
| 정본 출처 | Part2 §6.11 L5966 |
| 심각도 | P1 (긴급) |
| 권고 레벨 | WARN (V1 §4.11 정본 — P1 이지만 자동 fallback 활성 가능 시 WARN) |
| NEVER_AUTO | ❌ |
| 1차 FB | `FB_SDAR_ESCALATE` (HITL, V1 §4.3 row 28 — 자동 수리 포기 → 인간 에스컬레이션) |
| Trigger 코드 위치 | `src/sdar/repair_engine.py` `_attempt_repair()` (3 재시도 소진) |
| Trigger 조건 | SDAR `prescribe → repair → verify` 사이클 3회 연속 실패 (verify 단계에서 repair_validation_score < 0.7) |
| 발생 빈도 추정 | 운영 환경 < 1 / week (복잡 장애 시) |
| Cross-handoff | 6-5 SDAR-System (W-1 RESOLVED) — 본 6-12 = FC 정의 / 6-5 = 실행 |
| Pydantic payload schema | 본 §3.5.1 |
| Phase 2 테스트 | 본 §3.5.2 (2건) |

#### §3.5.1 Pydantic payload schema

```python
class SdarRepairFailPayload(BaseModel):
    """SDAR_REPAIR_FAIL payload (V2)"""
    failure_code: Literal["SDAR_REPAIR_FAIL"] = "SDAR_REPAIR_FAIL"
    pipeline_stage: Literal["detect", "diagnose", "prescribe", "repair", "verify"]
    failure_pattern_id: str = Field(..., description="6-5 SDAR FailurePattern ID")
    retry_attempts: list[dict] = Field(..., min_length=1, max_length=3, description="실제 수행된 재시도 결과 1~3건 (소진=최대 3) [{attempt:1, repair_score:0.4}, ...]")
    final_repair_score: float = Field(..., ge=0.0, le=1.0)
    repair_threshold: float = Field(default=0.7)
    escalation_triggered: bool = Field(default=True, description="FB_SDAR_ESCALATE HITL 활성")
    operator_eta_minutes: Optional[int] = Field(None, description="운영자 응답 ETA")
    severity: Literal["P1"] = "P1"
    level: Literal["WARN"] = "WARN"
```

#### §3.5.2 Phase 2 테스트 시나리오

| TS-ID | 시나리오 | 주입 방법 | 기대 결과 |
|-------|---------|---------|---------|
| TS-SDAR-REPAIR-1 | 3회 재시도 소진 | SDAR 장애 패턴 주입 + repair_score 0.3/0.4/0.5 시뮬레이션 | `SDAR_REPAIR_FAIL`(retry_attempts=3, final_score=0.5 < 0.7) + FB_SDAR_ESCALATE HITL + 운영자 알림 |
| TS-SDAR-REPAIR-2 | 2회 재시도 후 성공 | repair_score 0.4 → 0.8 (2회) | FC 발행 ❌, 정상 verify 통과, INFO 로그 |

---

### §3.6 FC 6: `SDAR_SNAPSHOT_CORRUPT` — 수리 전 스냅샷 무결성 검증 실패

| 항목 | 값 |
|------|-----|
| 코드 | `SDAR_SNAPSHOT_CORRUPT` |
| 구분 | SDAR (V2) |
| V1 row | §4.11 row 42 |
| 정본 출처 | Part2 §6.11 L5967 |
| 심각도 | P1 (긴급) |
| 권고 레벨 | WARN |
| NEVER_AUTO | ❌ (단, 데이터 손상 위험으로 MANUAL FB 적용 — 자동 진행 ❌) |
| 1차 FB | `FB_SDAR_ABORT` (MANUAL, V1 §4.3 row 29 — 수리 중단 + 수동 복구 대기) |
| Trigger 코드 위치 | `src/sdar/snapshot_manager.py` `_verify_integrity()` (SHA-256 매니페스트 대조) |
| Trigger 조건 | (a) 스냅샷 SHA-256 manifest 와 실제 파일 SHA mismatch **또는** (b) manifest 파일 자체 부재 **또는** (c) 스냅샷 archive (tar.zst) decompression 실패 |
| 발생 빈도 추정 | 매우 드뭄 (< 1 / quarter, 디스크 손상 / 권한 오류 시) |
| Cross-handoff | 6-5 SDAR-System (W-1 RESOLVED) |
| Pydantic payload schema | 본 §3.6.1 |
| Phase 2 테스트 | 본 §3.6.2 (2건) |

#### §3.6.1 Pydantic payload schema

```python
class SdarSnapshotCorruptPayload(BaseModel):
    """SDAR_SNAPSHOT_CORRUPT payload (V2)"""
    failure_code: Literal["SDAR_SNAPSHOT_CORRUPT"] = "SDAR_SNAPSHOT_CORRUPT"
    snapshot_id: str = Field(..., description="SDAR 스냅샷 ID (timestamp + hash prefix)")
    corruption_type: Literal["sha_mismatch", "manifest_missing", "decompress_failure"]
    expected_sha256: Optional[str] = Field(None)
    actual_sha256: Optional[str] = Field(None)
    affected_files: list[str] = Field(default_factory=list)
    manual_recovery_required: bool = Field(default=True, description="FB_SDAR_ABORT MANUAL 적용")
    operator_action_url: Optional[str] = Field(None, description="운영자 페이지 URL")
    severity: Literal["P1"] = "P1"
    level: Literal["WARN"] = "WARN"
```

#### §3.6.2 Phase 2 테스트 시나리오

| TS-ID | 시나리오 | 주입 방법 | 기대 결과 |
|-------|---------|---------|---------|
| TS-SDAR-SNAP-1 | SHA-256 mismatch | 스냅샷 파일 임의 1 byte 수정 후 verify 호출 | `SDAR_SNAPSHOT_CORRUPT`(corruption_type="sha_mismatch") + FB_SDAR_ABORT MANUAL + 자동 진행 ❌ |
| TS-SDAR-SNAP-2 | manifest 부재 | manifest.json 파일 삭제 후 verify 호출 | `SDAR_SNAPSHOT_CORRUPT`(corruption_type="manifest_missing") + FB_SDAR_ABORT |

---

### §3.7 FC 7: `LLAMAGUARD_GPU_UNAVAIL` — LlamaGuard GPU 사용 불가

| 항목 | 값 |
|------|-----|
| 코드 | `LLAMAGUARD_GPU_UNAVAIL` |
| 구분 | LlamaGuard (V2) |
| V1 row | §4.11 row 43 |
| 정본 출처 | Part2 §6.11 L5968 |
| 심각도 | P2 (중간) |
| 권고 레벨 | ERROR (V1 §4.11 정본 — GPU 부재는 보안 검증 레이턴시 직접 영향) |
| NEVER_AUTO | ❌ |
| 1차 FB | `FB_GUARD_CPU_FALLBACK` (AUTO, V1 §4.3 row 30 — GPU→CPU(INT4) 전환, 레이턴시 증가 감수) |
| Trigger 코드 위치 | `src/security/llamaguard_client.py` `_check_gpu_available()` (CUDA / ROCm 감지) |
| Trigger 조건 | (a) `torch.cuda.is_available()` False **또는** (b) GPU OOM (이전 요청 처리 시 메모리 초과) **또는** (c) GPU device timeout |
| 발생 빈도 추정 | 운영 환경 < 5 / month (피크 시간대 GPU 경합 시) |
| Pydantic payload schema | 본 §3.7.1 |
| Phase 2 테스트 | 본 §3.7.2 (2건) |

#### §3.7.1 Pydantic payload schema

```python
class LlamaguardGpuUnavailPayload(BaseModel):
    """LLAMAGUARD_GPU_UNAVAIL payload (V2)"""
    failure_code: Literal["LLAMAGUARD_GPU_UNAVAIL"] = "LLAMAGUARD_GPU_UNAVAIL"
    gpu_unavail_reason: Literal["cuda_not_available", "gpu_oom", "device_timeout"]
    gpu_device_id: Optional[int] = Field(None, ge=0)
    cuda_version: Optional[str] = Field(None)
    fallback_mode: Literal["cpu_int4"] = "cpu_int4"
    expected_latency_increase_ms: float = Field(default=2000.0, description="CPU(INT4) 전환 시 평균 레이턴시 증가")
    severity: Literal["P2"] = "P2"
    level: Literal["ERROR"] = "ERROR"
```

#### §3.7.2 Phase 2 테스트 시나리오

| TS-ID | 시나리오 | 주입 방법 | 기대 결과 |
|-------|---------|---------|---------|
| TS-GUARD-GPU-1 | CUDA 부재 | `CUDA_VISIBLE_DEVICES=""` 환경 + LlamaGuard 호출 | `LLAMAGUARD_GPU_UNAVAIL`(reason="cuda_not_available") + FB_GUARD_CPU_FALLBACK + 정상 분류 (느린 응답) |
| TS-GUARD-GPU-2 | GPU OOM | 큰 모델 동시 로드 후 LlamaGuard 호출 | `LLAMAGUARD_GPU_UNAVAIL`(reason="gpu_oom") + FB_GUARD_CPU_FALLBACK |

---

### §3.8 FC 8: `LLAMAGUARD_CLASSIFY_FAIL` — LlamaGuard 안전성 분류 타임아웃/오류

| 항목 | 값 |
|------|-----|
| 코드 | `LLAMAGUARD_CLASSIFY_FAIL` |
| 구분 | LlamaGuard (V2) |
| V1 row | §4.11 row 44 |
| 정본 출처 | Part2 §6.11 L5969 |
| 심각도 | P1 (긴급) |
| 권고 레벨 | ERROR |
| NEVER_AUTO | ❌ (단, 보수적 차단 정책으로 DENY_ONLY FB 적용) |
| 1차 FB | `FB_GUARD_BLOCK_DEFAULT` (DENY_ONLY, V1 §4.3 row 31 — 분류 실패 시 "안전하지 않음" 기본값으로 차단) |
| Trigger 코드 위치 | `src/security/llamaguard_client.py` `classify()` |
| Trigger 조건 | (a) 분류 timeout ≥ 10초 **또는** (b) 모델 로드 실패 **또는** (c) 입력 토큰 한도 초과 (≥ 4096) |
| 발생 빈도 추정 | 운영 환경 < 3 / day (분류 실패는 보안상 중요) |
| Pydantic payload schema | 본 §3.8.1 |
| Phase 2 테스트 | 본 §3.8.2 (2건) |

#### §3.8.1 Pydantic payload schema

```python
class LlamaguardClassifyFailPayload(BaseModel):
    """LLAMAGUARD_CLASSIFY_FAIL payload (V2)"""
    failure_code: Literal["LLAMAGUARD_CLASSIFY_FAIL"] = "LLAMAGUARD_CLASSIFY_FAIL"
    classify_fail_reason: Literal["timeout", "model_load_failure", "token_limit_exceeded"]
    timeout_threshold_sec: float = Field(default=10.0)
    elapsed_sec: float = Field(..., ge=0)
    input_token_count: int = Field(..., ge=0)
    token_limit: int = Field(default=4096)
    block_default_active: bool = Field(default=True, description="FB_GUARD_BLOCK_DEFAULT 활성")
    severity: Literal["P1"] = "P1"
    level: Literal["ERROR"] = "ERROR"
```

#### §3.8.2 Phase 2 테스트 시나리오

| TS-ID | 시나리오 | 주입 방법 | 기대 결과 |
|-------|---------|---------|---------|
| TS-GUARD-CLS-1 | 분류 타임아웃 | LlamaGuard 모델 응답 지연 시뮬레이션 (15s) | `LLAMAGUARD_CLASSIFY_FAIL`(reason="timeout", elapsed_sec≥10) + FB_GUARD_BLOCK_DEFAULT (DENY) |
| TS-GUARD-CLS-2 | 토큰 한도 초과 | 5000 토큰 입력 + LlamaGuard 호출 | `LLAMAGUARD_CLASSIFY_FAIL`(reason="token_limit_exceeded", input_token_count=5000) + FB_GUARD_BLOCK_DEFAULT |

---

## §4. R-612-3 매핑 매트릭스 (V2 8 FC × 1+ FB = 8건)

| # | FC | 1차 FB | 매핑 정책 | LOCK-EL-05 정합 (Part2 §6.9) |
|---|------|-------|---------|----------------------------|
| 1 | `COND_MODULE_INIT_FAIL` | `FB_SKIP_COND` (AUTO) | 1:1 (단순 비활성) | ✅ V1 §4.3 row 24 일치 |
| 2 | `COND_BATCH_TIMEOUT` | `FB_REDUCE_BATCH` (AUTO) | 1:1 (batch 절반 후 재실행) | ✅ V1 §4.3 row 25 일치 |
| 3 | `COND_DEPENDENCY_CONFLICT` | `FB_ISOLATE_MODULE` (AUTO) | 1:1 (격리 + 운영자 알림) | ✅ V1 §4.3 row 26 일치 |
| 4 | `RAG_QDRANT_CONNECTION` | `FB_RAG_FALLBACK_CHROMA` (AUTO) | 1:1 (Chroma 전환) | ✅ V1 §4.3 row 27 일치 |
| 5 | `SDAR_REPAIR_FAIL` | `FB_SDAR_ESCALATE` (HITL) | 1:1 (인간 에스컬레이션) | ✅ V1 §4.3 row 28 일치 |
| 6 | `SDAR_SNAPSHOT_CORRUPT` | `FB_SDAR_ABORT` (MANUAL) | 1:1 (수동 복구 강제) | ✅ V1 §4.3 row 29 일치 |
| 7 | `LLAMAGUARD_GPU_UNAVAIL` | `FB_GUARD_CPU_FALLBACK` (AUTO) | 1:1 (CPU INT4 전환) | ✅ V1 §4.3 row 30 일치 |
| 8 | `LLAMAGUARD_CLASSIFY_FAIL` | `FB_GUARD_BLOCK_DEFAULT` (DENY_ONLY) | 1:1 (보수적 차단) | ✅ V1 §4.3 row 31 일치 |

**R-612-3 검증**: V2 8 FC 모두 ≥ 1 FB 매핑 등재 ✅. 매핑 0건 등재 ❌ 위반 0건. LOCK-EL-05 정본 Part2 §6.9 변경 ❌.

### §4.1 FB 실행 모드 분포 (V1 §4.3 정합)

| 모드 | FC 수 | FC 목록 |
|------|-------|--------|
| AUTO | 5 | COND_MODULE_INIT_FAIL / COND_BATCH_TIMEOUT / COND_DEPENDENCY_CONFLICT / RAG_QDRANT_CONNECTION / LLAMAGUARD_GPU_UNAVAIL |
| HITL | 1 | SDAR_REPAIR_FAIL |
| MANUAL | 1 | SDAR_SNAPSHOT_CORRUPT |
| DENY_ONLY | 1 | LLAMAGUARD_CLASSIFY_FAIL |

---

## §5. LOCK-EL-03 V2 단계 갱신 매트릭스 (36 → 44, V3 4건 Phase 3 이월)

| 단계 | 항목 수 | 누계 | 정본 출처 | 본 V2 NEW 파일 기여 |
|------|--------|------|----------|------------------|
| D2.1-D2 SOT 베이스라인 | 36 | 36 | D2.1-D2 §5.2 (V0+ V1+) | 인용만 (V1 정본 보존) |
| **V2 단계 추가 (본 P2-3)** | **+8** | **44** | **Part2 §6.11 L5962-5969** | **본 §3 8 FC 운영 명세** |
| V3 단계 (Phase 3 이월) | +4 | 48 | Part2 §6.11 L5970-5973 | 본 P2-3 범위 외 (P3-2 또는 V2 EXTEND) |

**LOCK-EL-03 합계 48 보존**: V1 §2 합계 표 36+12=48 변경 ❌. 본 V2 NEW 파일은 36→44 부분 (V2 8건) 의 운영 명세만 추가, 합계 정본 변경 ❌.

### §5.1 V3 4 FC Phase 3 이월 명시

| # | V3 FC | 정본 출처 | Phase 3 이월 사유 |
|---|------|---------|----------------|
| 45 | `EXP_SELF_EVO_REGRESSION` | Part2 §6.11 L5970 | Self-Evolution 시스템 V3 단계 (6-6 도메인 완료 후 통합) |
| 46 | `EXP_AGENT_SPAWN_LIMIT` | Part2 §6.11 L5971 | Agent Mesh V3 단계 (6-3 SPECIAL 도메인 완료 후) |
| 47 | `EXP_GPU_OOM` | Part2 §6.11 L5972 | vLLM V3 단계 (인프라 V3 후) |
| 48 | `EXP_A2A_AUTH_FAIL` | Part2 §6.11 L5973 | A2A 프로토콜 V3 단계 |

---

## §6. CFL-EL-001 검토 메모 (P2-3 시점 결정 ❌, STEP_C 결정)

| 항목 | 값 |
|------|-----|
| CFL ID | CFL-EL-001 |
| 상태 | OPEN (비차단) |
| 발견 | P1-3 (`pipeline_state_map.md` §10.K) |
| 설명 | Part2 §6.11 L5809 S8 Evolve on_enter primary event `sdar.repair.started` 가 V1 `event_type_registry.md` 134항목 (LOCK-EL-02) 미등재 |
| 본 P2-3 결정 | **❌ 본 P2-3 시점에서 결정하지 않음** (R-T6-1 정본 우선 + 자동 RESOLVE 금지 원칙) |
| STEP_C 시점 결정 옵션 | (a) `sdar.repair.started` 레지스트리 등재 → LOCK-EL-02 134→135 변경 (`[LOCK_CHANGE_NEEDED]` 게이트 트리거, 비차단 결정) **또는** (b) `sdar.*` 네임스페이스 승격 후 재분류 (LOCK-EL-09 조정) **또는** (c) DEFERRED_TO_PHASE3 (Phase 3 v3_evolution 단계 재검토) |
| 본 V2 NEW 파일 영향 | 0 (CFL-EL-001 은 LOCK-EL-02 EventTypeRegistry 관련, 본 파일은 LOCK-EL-03 FailureCodeRegistry 관련) |

> **STEP_C R round 시점에 사용자 승인 후 결정 — 본 STEP_B 에서는 보존 (자동 RESOLVE 금지)**.

---

## §7. 11 CONSUMER 도메인 V2 FC 발행 적용 가이드

> ★ 본 §7 은 **참조만**. 11 CONSUMER 도메인 자체 sandbox/production 직접 편집 ❌. RECHECK_FLAG 발행은 STEP_B step 8 시점에 본 6-12 sandbox 4 위치만 기록.

| # | CONSUMER | namespace | V2 FC 발행 시점 | 적용 FC |
|---|---------|-----------|--------------|--------|
| 1 | 1-1 Verifier-Reasoning | `oc.i1~i5` | 추론 단계 실패 시 | (V2 직접 발행 ❌, 본 V2 8 FC 는 COND/RAG/SDAR/LlamaGuard 도메인 한정) |
| 2 | 2-1 Blue-Node-Architecture | `oc.blue.*` | 노드 실행 실패 시 | (V2 8 FC 적용 ❌, V1 D2.1-D2 36 FC 적용) |
| 3 | 2-2 COND-Modules-Detail | `oc.cond.*` | COND 모듈 진입 / 실행 실패 | **COND_MODULE_INIT_FAIL / COND_BATCH_TIMEOUT / COND_DEPENDENCY_CONFLICT** (3건) |
| 4 | 3-7 Dev-Tools | `dev.*` | tool 실행 실패 | (V2 직접 발행 ❌, V1 TL_ERR_* 적용) |
| 5 | 4-1 Rust-Tauri-Infrastructure | `ipc.*` | IPC 통신 실패 | (V2 직접 발행 ❌, V1 TL_ERR_* 적용) |
| 6 | 4-3 MCP-Server-Client | `mcp.*` | MCP 호출 실패 | (V2 직접 발행 ❌, V1 TL_ERR_* 적용) |
| 7 | 6-1 UI-UX-System | `ui.builder.*` | 사용자 액션 실패 | (V2 직접 발행 ❌) |
| 8 | 6-3 Agent-Teams-PARL | `agent.*` | 에이전트 실행 실패 | (V2 직접 발행 ❌, V3 EXP_AGENT_SPAWN_LIMIT 이월) |
| 9 | 6-5 SDAR-System | `sdar.*` | SDAR 사이클 실패 (W-1 RESOLVED) | **SDAR_REPAIR_FAIL / SDAR_SNAPSHOT_CORRUPT** (2건) |
| 10 | 6-8 Cloud-Library | `cl.rt.*` | RAG 검색 실패 | **RAG_QDRANT_CONNECTION** (1건) |
| 11 | 6-13 Operations | `ops.*` | (소비만, 신규 발행 ❌) | Loki LogQL 추출 |

### §7.1 LlamaGuard 발행 도메인 (보안 횡단)

| FC | 발행 도메인 | 사유 |
|------|----------|------|
| `LLAMAGUARD_GPU_UNAVAIL` | 6-2 Security-Governance + (호출자 도메인) | 보안 검증 호출 시 발행 (보안 정책은 6-2 소유) |
| `LLAMAGUARD_CLASSIFY_FAIL` | 6-2 Security-Governance + (호출자 도메인) | 분류 실패 시 발행 |

> **6-2 Security-Governance** 는 11 CONSUMER 표 외이지만, LlamaGuard 발행 책임 도메인. W-3 RESOLVED (NEVER_AUTO 6-2 ↔ 6-12) 경계 정합.

### §7.2 RECHECK_FLAG 발행 trigger (STEP_B step 8)

본 V2 NEW 파일 신설로 인한 RECHECK 의무:
- (a) 2-2 COND / 6-5 SDAR / 6-8 Cloud / 6-2 Security 도메인 자체 V2 FC 발행 코드 추가 (Phase 3 또는 자체 STEP_B 시점).
- (b) §3.X.1 Pydantic payload schema 자체 채택 (각 CONSUMER 도메인).
- (c) §3.X.2 Phase 2 테스트 시나리오 16건 (V2 8 FC × 2 시나리오) 자체 검증.

본 6-12 STEP_B step 8 시점에 4 위치만 기록 (CONFLICT_LOG / plan §7 / memory / SOT2_MASTER_INDEX), CONSUMER 직접 편집 ❌. **DEFERRED_TO_PHASE3** 판정.

---

## §8. NEVER_AUTO 검증 (LOCK-EL-06 정합)

| FC | NEVER_AUTO | 사유 |
|------|----------|------|
| COND_* (3건) | ❌ | LOCK-EL-06 3코드 (OC_I5_POLICY_BLOCK / POLICY_DENY / PII_LONGTERM_DENIED) 외 |
| RAG_QDRANT_CONNECTION | ❌ | (LOCK-EL-06 외) |
| SDAR_* (2건) | ❌ | (LOCK-EL-06 외, 단 SNAPSHOT_CORRUPT 는 MANUAL FB 로 자동 진행 차단) |
| LLAMAGUARD_* (2건) | ❌ | (LOCK-EL-06 외, 단 CLASSIFY_FAIL 는 DENY_ONLY FB 로 보수적 차단) |

**LOCK-EL-06 보존**: V2 8 FC 모두 NEVER_AUTO ❌, LOCK-EL-06 3코드 (OC_I5_POLICY_BLOCK / POLICY_DENY / PII_LONGTERM_DENIED) 변경 ❌. V1 `failure_code_registry.md` §5 정본 보존.

---

## §9. ABC 패턴 매핑 (정본 준수)

| ABC | 본 §N | 시그니처 |
|-----|-------|---------|
| `BaseFailureCodePayload` (Pydantic 추상) | §3.X.1 8 schemas | `failure_code: Literal[...] / severity / level + 도메인별 필드` |
| `BaseFallbackExecutor` (실행 추상) | §4 매트릭스 | `def execute(payload: BaseFailureCodePayload, mode: Literal["AUTO", "HITL", "MANUAL", "DENY_ONLY"]) -> Result` |
| `BaseFCRegistry` (V1 정본 인용) | V1 `failure_code_registry.md` §3.1 | `_FC_PREFIXES` frozenset (12 prefix) + 48 합계 |

**ABC 정본 위치**: `00_common/base_failure_code_abc.md` (Phase 3 신설 예정).

---

## §10. 복잡도 / 연산 특성

| 연산 | 시간 복잡도 | 공간 복잡도 | 주석 |
|------|-----------|-----------|------|
| Pydantic payload validation | O(필드 수) ≈ O(8~12) | O(payload_size) | 매 FC 발행 시 |
| FC → FB lookup (§4 매트릭스) | O(1) (8 entry dict) | O(8) | dict.get() |
| 8 FC × 2 테스트 시나리오 실행 | O(16 × 시나리오 복잡도) | O(test_data) | Phase 2 통합 테스트 |
| `_verify_integrity()` SHA-256 (FC 6) | O(snapshot_size) | O(SHA digest) ≈ O(32) | SDAR_SNAPSHOT_CORRUPT 검증 |
| `detect_cycles()` DFS (FC 3) | O(V+E) (모듈 그래프) | O(V) | COND_DEPENDENCY_CONFLICT 검증 |

---

## §11. 세션 간 인터페이스 cross-check

### §11.1 본 P2-3 ← P2-1 (`trace_propagation.md`) ← P2-2 (`structured_logging.md`)

| P2-N §N | 인터페이스 | 본 P2-3 정합 |
|---------|----------|-----------|
| P2-1 §6.4 신규 FC `EL_EVT_NO_TRACE_CONTEXT` | LOCK-EL-08 위반 알람 | 본 §3 V2 8 FC 와 **별개 항목** (Phase 3 검토 또는 P2-1 자체 등재 별도 진행) |
| P2-2 §5.2 P0~P3 권고 레벨 | FC 권고 레벨 매핑 | 본 §3 8 FC 권고 레벨 (P2 → WARN, P1 → ERROR/WARN) 정합 |
| P2-2 §5.3 NEVER_AUTO 강제 CRITICAL | LOCK-EL-06 3코드 격상 | 본 §8 V2 8 FC NEVER_AUTO ❌ 검증 |

### §11.2 본 P2-3 → V1 baseline 정합

| V1 파일 | §N | 본 P2-3 정합 |
|---------|-----|-----------|
| `failure_code_registry.md` §2 합계 | 36 + 12 = 48 | 합계 변경 ❌, 본 §5 매트릭스 정합 |
| `failure_code_registry.md` §4.11 V2 8 row | 코드명 / 구분 / 권고 레벨 / 1차 FB | 본 §3.1~§3.8 운영 명세 정합 (V1 row → V2 1 섹션 1:1) |
| `fallback_registry.md` §4.3 V2 8 FB row | FB 코드명 / 모드 / 적용 FC | 본 §4 매트릭스 정합 (1:1 매핑) |
| `fc_fb_mapping.md` (V1 P1-8) | FC → FB 1:N 매핑 정본 | 본 §4 8 FC × 1 FB = 1:1 매핑 정합 |
| `never_auto_detector.md` (V1 P1-9) | NEVER_AUTO 5규칙 + LOCK-EL-06 3코드 | 본 §8 V2 8 FC NEVER_AUTO ❌ 검증 |
| `log_level_spec.md` (V1 P1-5) §4.1 FC→Level 매핑 규약 | P0~P3 매핑 | 본 §3 권고 레벨 정합 |

### §11.3 6-5 SDAR-System cross-handoff (W-1 RESOLVED)

| 6-12 책임 | 6-5 책임 |
|---------|---------|
| FC 정의 (코드명 / 심각도 / 권고 레벨) | FC 발행 (사이클 실패 시점 감지) |
| 본 §3.5 / §3.6 Pydantic payload schema | payload 인스턴스 생성 + 발행 |
| §4 FC → FB 매핑 정본 | FB 실행 (FB_SDAR_ESCALATE / FB_SDAR_ABORT) |

본 6-12 LOCK 재정의 ❌, 6-5 자체 도메인 LOCK 재정의 ❌. W-1 RESOLVED 경계 보존.

---

## §12. Phase별 복구 흐름 (Phase 1→2→3→4)

```
Phase 1 (V1 baseline)              Phase 2 (V2, 본 P2-3)              Phase 3 (V3, P3-2)             Phase 4 (운영)
──────────────────────             ──────────────────────             ──────────────────             ──────────────
failure_code_registry.md           failure_code_registry_v2.md (본)   failure_code_registry_v3.md    Loki + Grafana 알람
§4.11 V2 8 FC row 등재             V2 8 FC 운영 명세 + Pydantic + TS  V3 4 FC 추가 (EXP_*)           각 FC × FB 자동 실행
                                   §4 R-612-3 매핑 매트릭스           V0→V3 인프라 진화                FailureCode 통계 대시보드
                                                                                                    NEVER_AUTO 강제 격상
                                          │
                                          ▼ (V2 단계 실패 시)
                                   FC payload schema 미일치 → Pydantic ValidationError → V2 운영 진입 차단
                                   FB 매핑 0건 → R-612-3 위반 → CONFLICT_LOG 등재 + 자동 RESOLVE 금지
                                   LOCK-EL-03 합계 48 변경 → [VIOLATION:LOCK-EL-03_redefinition] + 즉시 abort
                                   V1 failure_code_registry.md byte-prefix SHA mismatch → V1 EXTEND 위반 → 즉시 abort
```

### §12.1 다운그레이드 confidence 감산 (penalty)

| 트리거 | confidence 감산 | 이유 |
|--------|-------------|------|
| FC payload Pydantic validation 실패 | -0.10 | 스키마 정합성 저하 |
| FB 매핑 0건 (R-612-3 위반) | -0.30 | 복구 경로 부재, 시스템 안정성 직접 영향 |
| 권고 레벨 위반 (P2-2 §5.2 매트릭스 외) | -0.05 | 알림 분류 정합성 저하 |
| NEVER_AUTO 오격상 (LOCK-EL-06 외 코드 CRITICAL 격상) | -0.20 | 부정확한 격상은 운영 부담 |

---

## §13. 에스컬레이션 페이로드 구조 (R-01-8)

```python
@dataclass
class FCRegistryViolationPayload:
    """V2 FC 발행 / FB 매핑 위반 시 I-20 경유"""
    # P1-5 §6.2 11필드 (변경 금지)
    source_engine: str                         # FC 발행 모듈
    error_code: str = "EL_FC_REGISTRY_VIOLATION"
    original_request: dict = field(default_factory=dict)
    partial_result: Optional[dict] = None      # 검증 성공 필드
    retry_count: int = 0
    timestamp: str = ""
    severity: str = "P1"
    level: str = "ERROR"
    fallback_id: str = "FB_FC_REGISTRY_RECONFIGURE"
    recovery_action: str = "FC schema 재로딩 + 매핑 재검증"
    failure_chain: list = field(default_factory=list)

    # 본 §13 FC 5필드 (LOCK-EL-03 / L4 / L5 위반)
    violated_fc_code: Optional[str] = None     # 위반 FC 코드명
    expected_fb_mapping: Optional[str] = None  # 예상 FB 코드 (§4)
    actual_fb_mapping: Optional[str] = None    # 실제 매핑 (None / 다른값)
    schema_validation_error: Optional[str] = None  # Pydantic ValidationError msg
    r_612_3_violation: bool = False            # R-612-3 위반 (FB 매핑 0건)
```

---

## §14. 로깅 포맷 (R-01-7) — V2 FC 발행 예시 (P2-2 §3.2 정합)

### §14.1 정상 V2 FC 발행 (예: COND_MODULE_INIT_FAIL)

```json
{
  "timestamp": "2026-04-29T14:32:18.234Z",
  "level": "WARN",
  "event_type": "oc.cond.init_fail",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "correlation_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "source": "orange_core/cond_modules/init",
  "version": "1.0.0",
  "payload": {
    "failure_code": "COND_MODULE_INIT_FAIL",
    "module_id": "cond_a_pydantic",
    "init_stage": "import",
    "error_type": "ImportError",
    "error_message": "No module named 'pydantic'",
    "missing_dependency": "pydantic",
    "config_field": null,
    "retry_count": 0,
    "severity": "P2",
    "level": "WARN"
  }
}
```

### §14.2 R-612-3 위반 알람 (FB 매핑 0건)

```json
{
  "timestamp": "2026-04-29T14:32:19.567Z",
  "level": "ERROR",
  "event_type": "el.violation.r_612_3",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "source": "orange_core/event_validator",
  "version": "1.0.0",
  "error": {
    "code": "EL_FC_REGISTRY_VIOLATION",
    "lock_id": "LOCK-EL-05",
    "rule_id": "R-612-3",
    "violated_fc_code": "COND_NEW_HYPOTHETICAL",
    "r_612_3_violation": true
  },
  "context": {
    "expected_fb_mapping": "(at least 1 FB)",
    "actual_fb_mapping": null,
    "config_check_url": "/admin/fc_registry"
  },
  "recovery": {
    "fallback_id": "FB_FC_REGISTRY_RECONFIGURE",
    "action": "관리자 페이지에서 FC 매핑 등재 후 재로딩"
  },
  "payload": {}
}
```

---

## §15. Phase 3 통합 테스트 시나리오 (≥10 — 16건 = 8 FC × 2)

§3.1.2 ~ §3.8.2 8 FC × 2 시나리오 = **16건** 모두 등재 ✅. 본 §15 는 §3.X.2 인용 요약.

| FC | TS-IDs |
|------|-------|
| COND_MODULE_INIT_FAIL | TS-COND-INIT-1, TS-COND-INIT-2 |
| COND_BATCH_TIMEOUT | TS-COND-BATCH-1, TS-COND-BATCH-2 |
| COND_DEPENDENCY_CONFLICT | TS-COND-DEP-1, TS-COND-DEP-2 |
| RAG_QDRANT_CONNECTION | TS-RAG-QDRANT-1, TS-RAG-QDRANT-2 |
| SDAR_REPAIR_FAIL | TS-SDAR-REPAIR-1, TS-SDAR-REPAIR-2 |
| SDAR_SNAPSHOT_CORRUPT | TS-SDAR-SNAP-1, TS-SDAR-SNAP-2 |
| LLAMAGUARD_GPU_UNAVAIL | TS-GUARD-GPU-1, TS-GUARD-GPU-2 |
| LLAMAGUARD_CLASSIFY_FAIL | TS-GUARD-CLS-1, TS-GUARD-CLS-2 |

---

## §16. 변경 이력

| 버전 | 날짜 | 세션 | 변경 내용 |
|------|------|------|---------|
| v1.0 | 2026-04-29 | P2-3 | 신규 작성 — V2-Phase 2 태그. **별도 V2 NEW 파일 방안 (a) 채택** (V1 `failure_code_registry.md` byte-prefix SHA UNCHANGED 통산 보존). V2 FC 8건 운영 명세: COND_* 3 + RAG_* 1 + SDAR_* 2 + LLAMAGUARD_* 2. 각 FC: 트리거 조건 + Pydantic payload schema + Phase 2 테스트 시나리오 (×2). §4 R-612-3 매핑 매트릭스 (V2 8 FC × 1+ FB = 8건). §5 LOCK-EL-03 36→44 V2 단계 갱신 (V3 4건은 Phase 3 이월). §6 CFL-EL-001 검토 메모 (P2-3 결정 ❌, STEP_C 결정). §7 11 CONSUMER 적용 가이드 (참조만, 직접 편집 ❌). §8 NEVER_AUTO 0건 검증 (LOCK-EL-06 3코드 변경 ❌). FABRICATION 0/10 CLEAN. ISS-5 해소. exit_gate "V2 FailureCode 갱신" 충족. |

---

## §17. 자체 검증 체크리스트

| # | 검증 항목 | 결과 |
|---|---------|------|
| V-1 | LOCK-EL-03 verbatim 5-field 인용 | ✅ §2.1 |
| V-2 | LOCK-EL-04 / L5 / L6 / L7 verbatim 인용 | ✅ §2.2 |
| V-3 | LOCK 재정의/추가/변경 0건 | ✅ §2.3 |
| V-4 | LOCK-EL-03 합계 48 보존 (V2 단계 36→44 부분 기여) | ✅ §5 |
| V-5 | DH 신규 추가 0건 (DH 0건 보존 강제) | ✅ |
| V-6 | V2 8 FC 운영 명세 (8 섹션 §3.1~§3.8) | ✅ |
| V-7 | 각 FC Pydantic payload schema | ✅ §3.X.1 (8건) |
| V-8 | R-612-3 매핑 매트릭스 (V2 8 FC × 1+ FB) | ✅ §4 (8건 1:1) |
| V-9 | LOCK-EL-05 정본 (Part2 §6.9) 변경 ❌ | ✅ |
| V-10 | LOCK-EL-06 NEVER_AUTO 3코드 변경 ❌ | ✅ §8 |
| V-11 | LOCK-EL-07 권고 레벨 매핑 정합 (P2-2 §5.2) | ✅ §3 |
| V-12 | V1 baseline 정합 (V1 §4.11 + §4.3 + fc_fb_mapping) | ✅ §11.2 |
| V-13 | V3 4 FC Phase 3 이월 명시 | ✅ §5.1 |
| V-14 | CFL-EL-001 자동 RESOLVE 금지 (STEP_C 결정 큐) | ✅ §6 |
| V-15 | 11 CONSUMER 적용 가이드 (참조만, 직접 편집 ❌) | ✅ §7 |
| V-16 | 6-5 SDAR cross-handoff W-1 RESOLVED 보존 | ✅ §11.3 |
| V-17 | Phase 3 테스트 시나리오 ≥ 10 | ✅ §15 (16건) |
| V-18 | FABRICATION 10-marker census 0/N CLEAN | ✅ |
| V-19 | 별도 V2 NEW 파일 방안 (a) 채택, V1 byte-prefix SHA UNCHANGED | ✅ |
| V-20 | 2-stage upstream + self chain 인용 (D2.1-D2 + Part2 §6.11 > SOT2 6-12) | ✅ §0 |

---

## §V3. V3 FailureCode 4건 운영 명세 (Phase 4 implementation, 44 → 48, EXP_*)

> **§V3 신설 사유 (2026-06-03 Phase 4 RECOVERY Stage A+B P4-2)**: §5.1 에서 Phase 3 이월로 명시된 V3 FailureCode 4건(EXP_*)의 운영 명세를 V3 단계에서 종결한다. **본 §V3 는 EXTEND 이며 §1~§17 V2 본문은 byte-prefix 보존(변경 0)** 한다. LOCK-EL-03 합계 48 보존 (36+8+4), 재정의 0. **V3 FC 4건의 코드/권고 레벨/1차 FB 힌트는 V1 정본 `failure_code_registry.md` §(45~48) + `fc_fb_mapping.md` §3.12 + `fallback_registry.md` §4/§5(items 32~35) 에 이미 등재된 canonical 정의를 cite-only** 하며 (재정의 0), 본 §V3 는 Pydantic payload schema + Phase 4 운영 확정만 추가한다.

### §V3.1 V3 FC 4건 상세 명세 (#45~#48, V1 정본 cite-only)

| # | V3 FC | 분류 | 정본 출처 | 권고 레벨 (LOCK-EL-07) | 1차 FB 힌트 (LOCK-EL-04 V3, canonical) |
|---|------|------|---------|----------------------|------------------------------|
| 45 | `EXP_SELF_EVO_REGRESSION` | 자체진화 회귀 (P1) | Part2 §6.11 L5970 | WARN | `FB_EVO_ROLLBACK` (AUTO, 직전 버전 롤백 + 거버넌스 로그 필수) |
| 46 | `EXP_AGENT_SPAWN_LIMIT` | 에이전트 스폰 한도 초과(50+) (P2) | Part2 §6.11 L5971 | WARN | `FB_AGENT_QUEUE` (AUTO, 스폰 대기열 처리) |
| 47 | `EXP_GPU_OOM` | vLLM GPU 메모리 초과 (P2) | Part2 §6.11 L5972 | ERROR | `FB_GPU_OFFLOAD` (AUTO, CPU 오프로드) |
| 48 | `EXP_A2A_AUTH_FAIL` | A2A mTLS/JWT 인증 실패 (P1) | Part2 §6.11 L5973 | ERROR | `FB_A2A_RETRY` (AUTO, mTLS/JWT 재시도 3회) |

> ⚠️ 코드·권고 레벨·1차 FB 힌트는 V1 정본 `failure_code_registry.md` 행 45~48 verbatim cite (재정의 0). NEVER_AUTO 대상 0건 (4건 모두 AUTO Fallback).

### §V3.2 각 V3 FC Pydantic payload schema

```python
# #45 EXP_SELF_EVO_REGRESSION
class ExpSelfEvoRegressionPayload(BaseModel):
    failure_code: Literal["EXP_SELF_EVO_REGRESSION"]
    candidate_id: str
    baseline_metric: float
    regression_metric: float
    delta_pct: float            # 음수 = 회귀
    rollback_target: str        # 이전 안정 버전 ID

# #46 EXP_AGENT_SPAWN_LIMIT
class ExpAgentSpawnLimitPayload(BaseModel):
    failure_code: Literal["EXP_AGENT_SPAWN_LIMIT"]
    team_id: str
    requested_count: int
    limit: int
    queue_depth: int

# #47 EXP_GPU_OOM
class ExpGpuOomPayload(BaseModel):
    failure_code: Literal["EXP_GPU_OOM"]
    device_id: str
    requested_mb: int
    available_mb: int
    batch_size: int             # 컨텍스트 (FB_GPU_OFFLOAD = CPU 오프로드 판단)

# #48 EXP_A2A_AUTH_FAIL
class ExpA2AAuthFailPayload(BaseModel):
    failure_code: Literal["EXP_A2A_AUTH_FAIL"]
    peer_id: str
    auth_method: str
    fail_reason: str
    retry_count: int
```

### §V3.3 LOCK-EL-03 48 = 44 + 4 종결 매트릭스

| 단계 | 항목 수 | 누계 | 정본 출처 | 본 §V3 기여 |
|------|--------|------|----------|------------|
| D2.1-D2 SOT 베이스라인 (V0+V1) | 36 | 36 | D2.1-D2 §5.2 | 인용만 (V1 정본 보존) |
| V2 단계 (P2-3 §3) | +8 | 44 | Part2 §6.11 L5962-5969 | 인용만 (§3 V2 본문 보존) |
| **V3 단계 (본 §V3)** | **+4** | **48** | **Part2 §6.11 L5970-5973** | **본 §V3.1/§V3.2 4 FC 운영 명세 종결** |

**LOCK-EL-03 합계 48 보존 EXACT** (재정의 0). §5 V2 단계 "V3 4건 Phase 3 이월" → 본 §V3 에서 운영 명세 종결.

### §V3.4 D-P4-2-1 reconcile (EXP_* vs 6-5 SDAR FC)

plan §7.8 narrative "SDAR_REPAIR_FAIL / SDAR_SNAPSHOT_CORRUPT V3 추가 FC" 는 **6-5 SDAR 측 cross-ref FC 표기**이다. SDAR_REPAIR_FAIL/SDAR_SNAPSHOT_CORRUPT 는 본 도메인에서 이미 **V2 FC** (§3 V2 8건 중)이며, V3 4건은 **EXP_\*** 이다. 명명 conflation = content 정합 reconcile (6-5 측 V3 FC cross-ref ≠ 6-12 측 V3 FC 4건). version_evolution.md §3 / loki_integration_v3.md §4 정합.

### §V3.5 §V3 자체 검증 체크리스트

| # | 검증 항목 | 결과 |
|---|---------|------|
| VV-1 | V3 FC 4건 EXP_* 운영 명세 (§V3.1) | ✅ 4/4 |
| VV-2 | 각 V3 FC Pydantic payload schema (§V3.2) | ✅ 4/4 |
| VV-3 | LOCK-EL-03 48=44+4 합계 보존 (재정의 0) | ✅ §V3.3 |
| VV-4 | LOCK-EL-04 V3 FB 4건 canonical cite (FB_EVO_ROLLBACK/FB_AGENT_QUEUE/FB_GPU_OFFLOAD/FB_A2A_RETRY, fallback_registry §4/§5 정본 재정의 0) | ✅ §V3.1 |
| VV-5 | LOCK-EL-07 권고 레벨 V1 정본 cite (45 WARN/46 WARN/47 ERROR/48 ERROR) | ✅ §V3.1 |
| VV-6 | D-P4-2-1 reconcile (EXP_* vs SDAR FC) | ✅ §V3.4 |
| VV-7 | §1~§17 V2 본문 byte-prefix 보존 (변경 0) | ✅ EXTEND only |
| VV-8 | DH 0건 보존 (AUTHORITY §4 미존재) | ✅ |

> **[V3_EXTEND: failure_code_registry_v2 — Phase 4 P4-2 2026-06-03]** v2 → v3 EXTEND. §1~§17 V2 본문 byte-prefix 보존 + §V3 append. LOCK-EL-03 48 종결 (44→48 V3 4건 EXP_*). Status APPROVED. chain `phase4_6-12_recovery_AB_2026-06-03`.
