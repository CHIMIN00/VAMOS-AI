# Layer 2: DIAGNOSIS — 근본 원인 분석 상세

> **도메인**: 6-5_SDAR-System / 01_five-layer-pipeline
> **Tier**: 6 (System-wide Components)
> **정본**: SDAR_SPEC **§2.3** (Layer 2 DIAGNOSIS), **§8.1** (SDARDiagnosis 스키마), **§4** (오류 분류 체계)
> **Part2 출처**: §6.9 (L5412~L5419) — When/Where 정본
> **수정 정책**: Phase 변경 시 갱신 (종합계획서 §8.2)
> **LOCK 매핑**: L1 (5-Layer Pipeline 단계 정의), L6 (MAX_AUTO_REPAIRS_PER_ISSUE_PER_HOUR=3), DH-SDAR-T1 (Diagnosis timeout=120초)
> **Phase**: P1-2
> **생성일**: 2026-04-13
> **ISS 해결**: ISS-1 Layer 2, ISS-2 (DH-SDAR-T1=120초)

---

## 교차 참조 블록

| 참조 대상 | 관계 |
|----------|------|
| **SDAR_SPEC §2.3** | Layer 2 DIAGNOSIS 정의 정본 — 3단계 진단, SDARDiagnosis 스키마, 이벤트 |
| **SDAR_SPEC §4** | 오류 분류 체계 정본 — CATEGORY A~E 정의, AR-Level 매핑 |
| **SDAR_SPEC §8.1** | SDARDiagnosis 스키마 정본 — Pydantic v2 정의 |
| **SDAR_SPEC §6.4** | LogEvent 시스템 통합 — oc.sdar.diagnosis.* 이벤트 |
| **SDAR_SPEC §9.5** | CATEGORY E 특별 규칙 — 자동수리 절대 금지 (LOCK L15) |
| **Part2 §6.9** | When/Where 정본 — Phase별 참조 범위, 구현 위치 |
| **D2.0-02 §7 I-25** | I-25 SDAR Engine 모듈 정의 |
| **01_five-layer-pipeline/_index.md** | P0 총괄 — Layer 2 개요, DH-SDAR-T1 등재 |
| **01_five-layer-pipeline/detection.md** | Layer 1 산출물 — SDARDetectionSignal 스키마 (Layer 2 입력) |
| **02_state-machine/_index.md** | Layer 2 = DIAGNOSING 상태(S2)와 동기화 |
| **AUTHORITY_CHAIN.md §4** | LOCK L1, L6 레지스트리 |
| **AUTHORITY_CHAIN.md §5** | DH-SDAR-T1 정의 (Diagnosis timeout=120초) |

---

## 1. 개요

Layer 2 DIAGNOSIS는 SDAR 5-Layer Pipeline의 두 번째 단계로서, Layer 1 DETECTION이 발행한 `SDARDetectionSignal`을 입력으로 받아 **근본 원인(Root Cause)**을 분석하고, 오류를 **5대 카테고리(CATEGORY A~E)**로 분류하며, **영향 범위(Blast Radius)**를 평가하여 `SDARDiagnosis`를 출력한다. (LOCK L1: Detection → Diagnosis → Prescription → Repair → Verification)

### 1.1 핵심 요구사항

- 3단계 진단 프로세스: Root Cause Analysis → Error Classification → Impact Assessment
- DH-SDAR-T1 timeout=120초 (DEFINED-HERE, AUTHORITY_CHAIN §5) — 초과 시 DIAGNOSING→ESCALATED 전이
- `SDARDiagnosis` 출력 스키마를 통한 표준화된 진단 결과 전달
- MAX_AUTO_REPAIRS_PER_ISSUE_PER_HOUR=3 (LOCK L6) — 진단 시 기존 수리 이력 확인
- NOTIFICATION_MANDATORY (LOCK L9) — 모든 진단 활동 알림 필수
- CATEGORY E (보안 오류) 감지 시 즉시 에스컬레이션 (LOCK L15 — 자동수리 절대 금지)

---

## 2. 3단계 진단 프로세스 상세 (SDAR_SPEC §2.3)

### 2.1 Step 2-1: Root Cause Analysis (근본 원인 분석)

#### 알고리즘

```
FUNCTION root_cause_analysis(signal: SDARDetectionSignal) -> List[SDARRootCause]:
    # 시간복잡도: O(L * D) where L = 관련 로그 수, D = 의존성 그래프 깊이
    # ABC 패턴: BaseRCAAnalyzer(ABC).analyze(signal) → List[RCACandid]
    # LOCK 참조: L1 (Pipeline 순서 — Layer 1 SDARDetectionSignal 입력 보장)
    
    candidates = []
    
    # 기법 1: 로그 상관 분석 (Log Correlation Analysis)
    related_logs = log_store.query(
        trace_id=signal.trace_id,
        time_range=(signal.detected_at - 300s, signal.detected_at),
        order="chronological"
    )
    log_chain = extract_causal_chain(related_logs)
    IF log_chain.root_identified:
        candidates.append(RCACandid(
            source="log_correlation",
            cause=log_chain.root,
            confidence=log_chain.confidence,
            evidence_refs=log_chain.event_ids
        ))
    
    # 기법 2: 의존성 그래프 탐색 (Dependency Graph Traversal)
    dep_graph = module_registry.get_dependency_graph(signal.source_module)
    upstream_failures = dep_graph.find_upstream_failures(
        window=300,  # 5분 이내 상위 모듈 장애
        trace_id=signal.trace_id
    )
    FOR each failure IN upstream_failures:
        candidates.append(RCACandid(
            source="dependency_traversal",
            cause=failure.module_id + ":" + failure.failure_code,
            confidence=calculate_dep_confidence(failure, signal),
            evidence_refs=[failure.event_id]
        ))
    
    # 기법 3: 패턴 매칭 (S-4 Error Pattern Miner DB)
    known = s4_pattern_db.match(
        failure_code=signal.failure_code,
        context=signal.raw_context,
        window=600  # 10분
    )
    IF known:
        candidates.append(RCACandid(
            source="pattern_match",
            cause=known.pattern_description,
            confidence=known.match_score,
            evidence_refs=known.supporting_events,
            pattern_ref=known.pattern_id
        ))
    
    # 기법 4: 시간적 상관관계 (Temporal Correlation)
    recent_changes = change_log.query(
        time_range=(signal.detected_at - 3600s, signal.detected_at),
        types=["config_change", "module_update", "deployment"]
    )
    IF recent_changes AND temporal_overlap(recent_changes, signal):
        candidates.append(RCACandid(
            source="temporal_correlation",
            cause="Recent change: " + recent_changes[0].description,
            confidence=0.6,  # 시간적 상관만으로는 확신도 제한
            evidence_refs=[c.event_id FOR c IN recent_changes]
        ))
    
    # 후보 정렬 및 반환
    candidates.sort(key=lambda c: c.confidence, reverse=True)
    RETURN convert_to_sdar_root_causes(candidates[:5])  # 최대 5개 후보
```

#### RCA 분석 기법 요약

| # | 기법 | 데이터 소스 | 시간 윈도우 | confidence 기본 범위 |
|---|------|-----------|-----------|---------------------|
| 1 | 로그 상관 분석 | LogEvent (trace_id 기반) | 5분 | 0.7~0.95 |
| 2 | 의존성 그래프 탐색 | module_registry 의존성 맵 | 5분 | 0.5~0.85 |
| 3 | 패턴 매칭 | S-4 Error Pattern Miner DB | 10분 | 0.8~0.98 (패턴 DB 신뢰도) |
| 4 | 시간적 상관관계 | change_log (설정/배포 변경) | 1시간 | 0.3~0.6 |

#### confidence 계산 공식

```
FUNCTION calculate_dep_confidence(failure, signal) -> float:
    base = 0.5
    
    # 직접 의존 관계 가중
    IF failure.is_direct_dependency(signal.source_module):
        base += 0.2
    
    # 시간 근접도 가중 (5분 내 가까울수록 높음)
    time_gap = signal.detected_at - failure.occurred_at
    time_factor = max(0, 1.0 - (time_gap / 300))  # 300초 = 5분
    base += 0.15 * time_factor
    
    RETURN min(base, 0.95)  # 상한 0.95
```

### 2.2 Step 2-2: Error Classification (오류 분류)

5개 카테고리(CATEGORY A~E)로 분류한다 (SDAR_SPEC §4 정본).

#### 분류 알고리즘

```
FUNCTION classify_error(
    signal: SDARDetectionSignal,
    root_causes: List[SDARRootCause]
) -> Tuple[ErrorCategory, str, Severity]:
    # 시간복잡도: O(R * C) where R = root_cause 수, C = 분류 규칙 수 (현재 46)
    # ABC 패턴: BaseErrorClassifier(ABC).classify(signal, root_causes) → Classification
    # LOCK 참조: L15 (CATEGORY E 자동수리 절대 금지)
    
    IF len(root_causes) == 0:
        # RCA 전 기법 실패 — root_cause 없음 (DIAG-E001)
        RAISE RCAFailureError("DIAG-E001", message="no root cause identified — all RCA techniques failed")
    IF len(root_causes) == 0:
        # RCA 전 기법 실패 — root_cause 없음 (DIAG-E001)
        RAISE RCAFailureError("DIAG-E001", message="no root cause identified — all RCA techniques failed")
    primary_cause = root_causes[0]  # 최고 confidence 원인
    
    # 1. CATEGORY E (보안) 우선 판정 — LOCK L15
    IF is_security_related(signal, primary_cause):
        RETURN ("E", determine_e_code(signal), "critical")
        # ⚠️ CATEGORY E는 즉시 에스컬레이션 경로 진입
    
    # 2. failure_code 기반 직접 매핑 (SDAR_SPEC §4 코드 테이블)
    IF signal.failure_code IN sdar_error_code_registry:
        entry = sdar_error_code_registry[signal.failure_code]
        RETURN (entry.category, entry.error_code, entry.severity)
    
    # 3. root_cause 기반 추론 분류
    category = infer_category_from_root_cause(primary_cause)
    error_code = generate_error_code(category, signal)
    severity = determine_severity(category, signal, root_causes)
    
    RETURN (category, error_code, severity)
```

#### CATEGORY A~E 분류 기준 (SDAR_SPEC §4.1)

| 카테고리 | 명칭 | 대상 오류 | 위험도 범위 | AR-Level 범위 | 코드 수 |
|---------|------|---------|-----------|-------------|---------|
| **A** | Infrastructure (인프라) | DB, API, 네트워크, 디스크, 프로세스 | LOW~HIGH | AR-L2~L4 | 12 (A01~A12) |
| **B** | Model/AI (모델/AI) | 할루시네이션, 품질 저하, 라우팅, QoD | LOW~HIGH | AR-L2~L4 | 8 (B01~B08) |
| **C** | Logic (로직) | 워크플로우, Gate 설정, 스키마, 상태 머신 | MEDIUM~HIGH | AR-L3~L4 | 6 (C01~C06) |
| **D** | Code (코드) | 버그, 회귀, 의존성, 타입 오류 | MEDIUM~HIGH | AR-L3~L4 | 6 (D01~D06) |
| **E** | Security (보안) | 인젝션, 무단 접근, 유출, 권한 상승 | **CRITICAL** | **NEVER_AUTO** | 6 (E01~E06) |

#### CATEGORY A 상세 (SDAR_SPEC §4.1)

| 오류 코드 | 설명 | 위험도 | AR-Level | 수리 액션 |
|----------|------|--------|---------|----------|
| `SDAR_A01_DB_CONN_LOST` | DB 커넥션 끊김 | LOW | AR-L2 | `restart_service`, `retry_with_backoff` |
| `SDAR_A02_DB_TIMEOUT` | DB 쿼리 타임아웃 | LOW | AR-L2 | `retry_with_backoff`, `clear_cache` |
| `SDAR_A03_DB_CORRUPT` | DB 데이터 손상 | HIGH | AR-L4 | `rollback_to_snapshot` |
| `SDAR_A04_API_429` | LLM API Rate Limit 초과 | LOW | AR-L2 | `retry_with_backoff`, `switch_model_fallback` |
| `SDAR_A05_API_5XX` | LLM API 서버 오류 | LOW | AR-L2 | `retry_with_backoff`, `switch_model_fallback` |
| `SDAR_A06_API_AUTH_FAIL` | API 인증 실패 | MEDIUM | AR-L3 | `rotate_api_key` |
| `SDAR_A07_DISK_FULL` | 디스크 용량 부족 | MEDIUM | AR-L3 | `clear_cache`, `compress_logs` |
| `SDAR_A08_MEMORY_OOM` | 메모리 부족 | MEDIUM | AR-L3 | `restart_service`, `clear_cache` |
| `SDAR_A09_PROCESS_CRASH` | 프로세스 크래시 | LOW | AR-L2 | `restart_service` |
| `SDAR_A10_NETWORK_UNREACHABLE` | 네트워크 불통 | LOW | AR-L2 | `retry_with_backoff`, `switch_model_fallback` |
| `SDAR_A11_VECTOR_DB_DOWN` | Vector DB 장애 | MEDIUM | AR-L3 | `restart_service`, `rebuild_vector_index` |
| `SDAR_A12_MCP_SERVER_DOWN` | MCP 서버 응답 없음 | LOW | AR-L2 | `restart_service`, `retry_with_backoff` |

#### CATEGORY B 상세 (SDAR_SPEC §4.1)

| 오류 코드 | 설명 | 위험도 | AR-Level | 수리 액션 |
|----------|------|--------|---------|----------|
| `SDAR_B01_HALLUCINATION` | 할루시네이션 감지 | MEDIUM | AR-L3 | `switch_model_fallback`, `patch_prompt_template` |
| `SDAR_B02_QUALITY_DEGRADATION` | 출력 품질 저하 | MEDIUM | AR-L3 | `switch_model_fallback`, `patch_prompt_template` |
| `SDAR_B03_ROUTING_FAILURE` | 모델 라우팅 실패 | LOW | AR-L2 | `switch_model_fallback` |
| `SDAR_B04_SELFCHECK_FAIL` | Self-check 지속 실패 | MEDIUM | AR-L3 | `switch_model_fallback`, `patch_prompt_template` |
| `SDAR_B05_QOD_COLLAPSE` | QoD 점수 급락 | MEDIUM | AR-L3 | `rebuild_vector_index`, `clear_cache` |
| `SDAR_B06_TOKEN_EXPLOSION` | 토큰 사용량 폭증 | MEDIUM | AR-L3 | `adjust_rate_limit`, `patch_prompt_template` |
| `SDAR_B07_EMBEDDING_DRIFT` | 임베딩 품질 저하 | HIGH | AR-L4 | `rebuild_vector_index` |
| `SDAR_B08_CONTEXT_OVERFLOW` | 컨텍스트 윈도우 초과 | LOW | AR-L2 | `clear_cache`, `patch_prompt_template` |

#### CATEGORY C 상세 (SDAR_SPEC §4.1)

| 오류 코드 | 설명 | 위험도 | AR-Level | 수리 액션 |
|----------|------|--------|---------|----------|
| `SDAR_C01_WORKFLOW_STUCK` | 워크플로우 교착 상태 | MEDIUM | AR-L3 | `restart_service`, `update_config_parameter` |
| `SDAR_C02_GATE_MISCONFIGURED` | Gate 설정 오류 | HIGH | AR-L4 | `update_config_parameter` |
| `SDAR_C03_SCHEMA_MISMATCH` | 스키마 불일치 | HIGH | AR-L4 | `migrate_schema` |
| `SDAR_C04_STATE_INCONSISTENCY` | 상태 머신 불일치 | MEDIUM | AR-L3 | `restart_service`, `update_config_parameter` |
| `SDAR_C05_LOOP_DETECTED` | 무한 루프 감지 | MEDIUM | AR-L3 | `restart_service` |
| `SDAR_C06_PIPELINE_BROKEN` | 파이프라인 단절 | HIGH | AR-L4 | `restart_service`, `update_config_parameter` |

#### CATEGORY D 상세 (SDAR_SPEC §4.1)

| 오류 코드 | 설명 | 위험도 | AR-Level | 수리 액션 |
|----------|------|--------|---------|----------|
| `SDAR_D01_BUG_DETECTED` | 코드 버그 감지 | HIGH | AR-L4 | `patch_code_hotfix` |
| `SDAR_D02_REGRESSION` | 회귀 버그 | HIGH | AR-L4 | `rollback_to_snapshot`, `patch_code_hotfix` |
| `SDAR_D03_DEPENDENCY_BREAK` | 의존성 깨짐 | HIGH | AR-L4 | `reinstall_dependency` |
| `SDAR_D04_IMPORT_ERROR` | 모듈 임포트 실패 | MEDIUM | AR-L3 | `reinstall_dependency` |
| `SDAR_D05_TYPE_ERROR` | 타입 불일치 | HIGH | AR-L4 | `patch_code_hotfix` |
| `SDAR_D06_CONFIG_SYNTAX_ERROR` | 설정 파일 구문 오류 | MEDIUM | AR-L3 | `update_config_parameter` |

#### CATEGORY E 상세 (SDAR_SPEC §4.1 + §9.5, LOCK L15)

| 오류 코드 | 설명 | 위험도 | AR-Level | 대응 |
|----------|------|--------|---------|------|
| `SDAR_E01_INJECTION_DETECTED` | 프롬프트 인젝션 감지 | CRITICAL | **NEVER_AUTO** | 즉시 차단 + 인간 알림 |
| `SDAR_E02_UNAUTHORIZED_ACCESS` | 무단 접근 시도 | CRITICAL | **NEVER_AUTO** | 즉시 차단 + 인간 알림 |
| `SDAR_E03_DATA_BREACH` | 데이터 유출 감지 | CRITICAL | **NEVER_AUTO** | 즉시 차단 + 인간 알림 |
| `SDAR_E04_PRIVILEGE_ESCALATION` | 권한 상승 시도 | CRITICAL | **NEVER_AUTO** | 즉시 차단 + 인간 알림 |
| `SDAR_E05_SAFETY_BYPASS` | 안전 필터 우회 시도 | CRITICAL | **NEVER_AUTO** | 즉시 차단 + 인간 알림 |
| `SDAR_E06_PII_EXPOSURE` | PII 노출 감지 | CRITICAL | **NEVER_AUTO** | 즉시 마스킹 + 인간 알림 |

#### CATEGORY E 특별 규칙 (LOCK L15, SDAR_SPEC §9.5)

1. **자동수리 절대 금지**: 어떤 AR-Level에서도 CATEGORY E는 자동수리 불가
2. **즉시 차단**: 해당 요청/세션 즉시 차단
3. **감사 로그 강제**: CRITICAL 레벨 감사 로그 생성, 삭제 불가
4. **인간 알림 필수**: 즉시 인간 에스컬레이션
5. **포렌식 데이터 30일 보존**: 관련 데이터 30일 보존

#### 카테고리별 AR-Level 매핑 매트릭스 (SDAR_SPEC §4.2)

```
┌──────────────────────────────────────────────────────────────┐
│           카테고리 × AR-Level 자동수리 허용 매트릭스            │
│                                                              │
│              AR-L0   AR-L1   AR-L2   AR-L3   AR-L4          │
│  CAT-A(Infra)  --    제안    LOW     MED     HIGH           │
│  CAT-B(Model)  --    제안    LOW     MED     HIGH           │
│  CAT-C(Logic)  --    제안     --     MED     HIGH           │
│  CAT-D(Code)   --    제안     --      --     HIGH           │
│  CAT-E(Sec)    --    제안     --      --     NEVER          │
│                                                              │
│  -- = 수리 안 함  /  제안 = 진단 결과만 알림                    │
│  LOW/MED/HIGH = 해당 위험도까지 자동수리 허용                   │
│  NEVER = 어떤 AR-Level에서도 자동수리 금지                     │
└──────────────────────────────────────────────────────────────┘
```

### 2.3 Step 2-3: Impact Assessment (영향 범위 평가)

#### 알고리즘

```
FUNCTION assess_impact(
    signal: SDARDetectionSignal,
    root_causes: List[SDARRootCause],
    error_category: str
) -> SDARImpactAssessment:
    # 시간복잡도: O(M) where M = 전체 모듈 수 (I-Series + S-Series + E-Series)
    # ABC 패턴: BaseImpactAssessor(ABC).assess(signal, root_causes) → SDARImpactAssessment
    # LOCK 참조: L1 (Pipeline 순서 — Step 2-2 Classification 완료 후 실행)
    
    # 1. 영향 범위(scope) 산출
    affected_modules = []
    FOR each cause IN root_causes:
        downstream = module_registry.get_downstream(cause.related_modules)
        affected_modules.extend(downstream)
    affected_modules = deduplicate(affected_modules)
    
    # 2. 사용자 영향도(user_impact) 산출
    user_impact = determine_user_impact(affected_modules, error_category)
    
    # 3. 데이터 위험도(data_risk) 산출
    data_risk = determine_data_risk(error_category, root_causes)
    
    # 4. 연쇄 장애 가능성(propagation) 산출
    propagation = determine_propagation(affected_modules, signal)
    
    # 5. Blast Radius Score 종합 산출
    blast_radius_score = calculate_blast_radius_score(
        scope_count=len(affected_modules),
        user_impact=user_impact,
        data_risk=data_risk,
        propagation=propagation
    )
    
    RETURN SDARImpactAssessment(
        scope=affected_modules,
        user_impact=user_impact,
        data_risk=data_risk,
        propagation=propagation,
        blast_radius_score=blast_radius_score
    )
```

#### Blast Radius 평가 매트릭스

| 차원 | 값 | 기준 | 점수 가중치 |
|------|-----|------|-----------|
| **scope** (범위) | 영향 모듈 목록 | 의존성 그래프 순방향 탐색 | 0~0.3 (모듈 수 비례) |
| **user_impact** (사용자 영향) | none / degraded / blocked / data_loss | 사용자 대면 모듈 포함 여부 | none=0, degraded=0.1, blocked=0.2, data_loss=0.3 |
| **data_risk** (데이터 위험) | none / low / medium / high / critical | 데이터 접근·변경 모듈 관여 여부 | none=0, low=0.05, medium=0.1, high=0.2, critical=0.3 |
| **propagation** (전파) | isolated / spreading / cascading | 연쇄 장애 패턴 분석 | isolated=0, spreading=0.05, cascading=0.1 |

#### Blast Radius Score 계산

```
FUNCTION calculate_blast_radius_score(
    scope_count: int,
    user_impact: str,
    data_risk: str,
    propagation: str
) -> float:
    # 정규화된 0.0~1.0 점수
    scope_score = min(scope_count / 10, 0.3)  # 10개 이상이면 최대
    impact_score = {"none": 0, "degraded": 0.1, "blocked": 0.2, "data_loss": 0.3}[user_impact]
    risk_score = {"none": 0, "low": 0.05, "medium": 0.1, "high": 0.2, "critical": 0.3}[data_risk]
    prop_score = {"isolated": 0, "spreading": 0.05, "cascading": 0.1}[propagation]
    
    RETURN min(scope_score + impact_score + risk_score + prop_score, 1.0)
```

---

## 3. 공통 자료 구조 정의 (세션 간 인터페이스)

### 3.1 Layer 1 → Layer 2 인터페이스

Layer 2는 Layer 1의 `SDARDetectionSignal`을 입력으로 받는다. (detection.md §4 참조)

```python
# 입력: SDARDetectionSignal (Layer 1 출력)
# - signal_id: str (UUID v4)
# - trace_id: str (UUID v4)
# - detected_at: str (ISO8601 UTC)
# - channel: Literal["health", "error_pattern", "anomaly"]
# - severity: Literal["info", "warn", "error", "critical"]
# - source_module: str
# - source_event: str
# - failure_code: Optional[str]
# - metrics: dict
# - raw_context: dict
```

### 3.2 Layer 2 → Layer 3 인터페이스

Layer 2는 `SDARDiagnosis`를 출력하며, Layer 3 PRESCRIPTION의 입력이 된다.

```python
# 출력: SDARDiagnosis (SDAR_SPEC §8.1 — 아래 §4 상세)
# - diagnosis_id: str (UUID v4)
# - trace_id: str (UUID v4)
# - signal_ref: str (SDARDetectionSignal.signal_id 참조)
# - error_category: Literal["A", "B", "C", "D", "E"]
# - error_code: str
# - severity: Literal["info", "warn", "error", "critical"]
# - root_causes: List[SDARRootCause]
# - impact: SDARImpactAssessment
```

### 3.3 Layer 2 내부 중간 자료 구조

```python
class RCACandid(BaseModel):
    """RCA 분석 후보 (내부 중간 구조)"""
    source: Literal["log_correlation", "dependency_traversal", "pattern_match", "temporal_correlation"]
    cause: str
    confidence: float  # 0.0~1.0
    evidence_refs: List[str]
    pattern_ref: Optional[str] = None  # S-4 패턴 매칭 시

class ClassificationResult(BaseModel):
    """오류 분류 결과 (내부 중간 구조)"""
    category: Literal["A", "B", "C", "D", "E"]
    error_code: str
    severity: Literal["info", "warn", "error", "critical"]
    is_never_auto: bool  # CATEGORY E 시 True
```

---

## 4. `SDARDiagnosis` 출력 스키마 (SDAR_SPEC §8.1)

### 4.1 스키마 정의 (Pydantic v2)

```python
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Literal
from datetime import datetime


class SDARRootCause(BaseModel):
    """근본 원인 분석 결과"""
    cause_id: str = Field(..., description="원인 식별자")
    description: str = Field(..., description="원인 설명")
    confidence: float = Field(..., ge=0.0, le=1.0, description="원인 확신도")
    evidence_refs: List[str] = Field(default_factory=list, description="근거 LogEvent ID 목록")
    related_modules: List[str] = Field(default_factory=list, description="관련 모듈 ID (I-#, S-#, E-#)")
    causal_chain: List[str] = Field(
        default_factory=list,
        description="인과 체인 (원인 → 중간 → 증상 순서)"
    )


class SDARImpactAssessment(BaseModel):
    """영향 범위 평가"""
    scope: List[str] = Field(default_factory=list, description="영향받는 모듈 목록")
    user_impact: Literal["none", "degraded", "blocked", "data_loss"] = Field(
        ..., description="사용자 영향도"
    )
    data_risk: Literal["none", "low", "medium", "high", "critical"] = Field(
        ..., description="데이터 위험도"
    )
    propagation: Literal["isolated", "spreading", "cascading"] = Field(
        ..., description="연쇄 장애 가능성"
    )
    blast_radius_score: float = Field(
        ..., ge=0.0, le=1.0, description="영향 범위 종합 점수"
    )


class SDARDiagnosis(BaseModel):
    """Layer 2 진단 결과 스키마 (SDAR_SPEC §8.1)"""
    diagnosis_id: str = Field(..., description="진단 고유 ID (UUID v4)")
    trace_id: str = Field(..., description="연관 trace_id")
    signal_ref: str = Field(..., description="Layer 1 SDARDetectionSignal.signal_id 참조")
    diagnosed_at: str = Field(..., description="진단 완료 시각 (ISO8601 UTC)")

    # 오류 분류
    error_category: Literal["A", "B", "C", "D", "E"] = Field(
        ..., description="오류 카테고리 (A=Infra, B=Model, C=Logic, D=Code, E=Security)"
    )
    error_code: str = Field(..., description="SDAR 오류 코드 (e.g., SDAR_A04_API_429)")
    severity: Literal["info", "warn", "error", "critical"] = Field(
        ..., description="심각도"
    )

    # 근본 원인 분석
    root_causes: List[SDARRootCause] = Field(
        ..., min_length=1, description="근본 원인 목록 (최소 1개)"
    )
    primary_root_cause_idx: int = Field(
        default=0, description="주요 근본 원인 인덱스"
    )

    # 영향 범위
    impact: SDARImpactAssessment = Field(..., description="영향 범위 평가")

    # 메타데이터
    diagnosis_duration_ms: int = Field(..., description="진단 소요 시간 (ms)")
    pattern_match_ref: Optional[str] = Field(
        None, description="S-4 Error Pattern Miner 매칭 패턴 ID"
    )
    previous_occurrences: int = Field(
        default=0, description="동일 오류의 과거 발생 횟수 (최근 24시간)"
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "diagnosis_id": "diag_550e8400-e29b-41d4-a716-446655440001",
                "trace_id": "550e8400-e29b-41d4-a716-446655440000",
                "signal_ref": "sig_550e8400-e29b-41d4-a716-446655440002",
                "diagnosed_at": "2026-02-23T10:30:00Z",
                "error_category": "A",
                "error_code": "SDAR_A04_API_429",
                "severity": "warn",
                "root_causes": [{
                    "cause_id": "rc_001",
                    "description": "LLM API Rate Limit 초과 (분당 60회 상한 도달)",
                    "confidence": 0.95,
                    "evidence_refs": ["evt_001", "evt_002"],
                    "related_modules": ["I-10", "I-5"],
                    "causal_chain": ["높은 요청 빈도", "Rate Limit 임계치 도달", "429 응답"]
                }],
                "primary_root_cause_idx": 0,
                "impact": {
                    "scope": ["I-10", "I-5", "I-4"],
                    "user_impact": "degraded",
                    "data_risk": "none",
                    "propagation": "isolated",
                    "blast_radius_score": 0.3
                },
                "diagnosis_duration_ms": 250,
                "pattern_match_ref": "pat_api_429_v1",
                "previous_occurrences": 5
            }
        }
    )
```

### 4.2 필드 상세

| 필드 | 타입 | 필수/선택 | 설명 |
|------|------|----------|------|
| `diagnosis_id` | `str` (UUID v4) | **필수** | 진단 고유 식별자 |
| `trace_id` | `str` (UUID v4) | **필수** | 연관 trace_id — 로그 상관 분석용 |
| `signal_ref` | `str` | **필수** | Layer 1 SDARDetectionSignal.signal_id 참조 |
| `diagnosed_at` | `str` (ISO8601 UTC) | **필수** | 진단 완료 시각 |
| `error_category` | `Literal["A","B","C","D","E"]` | **필수** | 오류 카테고리 |
| `error_code` | `str` | **필수** | SDAR 오류 코드 |
| `severity` | `Literal["info","warn","error","critical"]` | **필수** | 심각도 |
| `root_causes` | `List[SDARRootCause]` (min 1) | **필수** | 근본 원인 목록 |
| `primary_root_cause_idx` | `int` | 선택 (기본 0) | 주요 근본 원인 인덱스 |
| `impact` | `SDARImpactAssessment` | **필수** | 영향 범위 평가 |
| `diagnosis_duration_ms` | `int` | **필수** | 진단 소요 시간 (ms) |
| `pattern_match_ref` | `Optional[str]` | 선택 | S-4 패턴 매칭 ID |
| `previous_occurrences` | `int` | 선택 (기본 0) | 과거 발생 횟수 (24시간) |

---

## 5. DH-SDAR-T1 Timeout=120초 적용 상세

### 5.1 정의 (AUTHORITY_CHAIN §5.1)

| 항목 | 값 |
|------|-----|
| DH-ID | DH-SDAR-T1 |
| 항목명 | Diagnosis 단계 timeout |
| 값 | **120초** (설정 가능, 기본값) |
| 근거 | Detection(30초) 후 Diagnosis 단계에서 과도한 지연 방지 |
| 정본 출처 | SOT2 DEFINED-HERE (SDAR_SPEC 미명시 영역) |
| 향후 | SDAR_SPEC에서 명시 시 상위 정본 우선 적용 |

### 5.2 적용 위치

```
FUNCTION diagnosis_with_timeout(signal: SDARDetectionSignal) -> SDARDiagnosis:
    # DH-SDAR-T1 = 120초 timeout
    # LOCK 참조: L2 (7-State Machine) — DIAGNOSING→ESCALATED 예외 전이
    
    start_time = now()
    
    TRY WITH TIMEOUT(DH_SDAR_T1=120):  # 120초
        # Step 2-1: RCA
        root_causes = root_cause_analysis(signal)
        
        # 중간 체크: 경과 시간 확인
        elapsed = now() - start_time
        IF elapsed > DH_SDAR_T1 * 0.8:  # 96초 경과 — 경고
            LOG warn("Diagnosis approaching timeout", elapsed_s=elapsed)
        
        # Step 2-2: Classification
        category, error_code, severity = classify_error(signal, root_causes)
        
        # CATEGORY E 즉시 처리 (LOCK L15)
        IF category == "E":
            RETURN handle_category_e(signal, root_causes, error_code)
        
        # Step 2-3: Impact Assessment
        impact = assess_impact(signal, root_causes, category)
        
        # L6 카운팅 기준점: 동일 이슈 과거 수리 횟수 확인
        previous = repair_history.count(
            error_code=error_code,
            window=3600  # 1시간
        )
        
        RETURN SDARDiagnosis(
            diagnosis_id=generate_uuid_v4(),
            trace_id=signal.trace_id,
            signal_ref=signal.signal_id,
            diagnosed_at=now_iso8601(),
            error_category=category,
            error_code=error_code,
            severity=severity,
            root_causes=root_causes,
            impact=impact,
            diagnosis_duration_ms=(now() - start_time).ms,
            previous_occurrences=previous
        )
    
    CATCH TimeoutError:
        # DH-SDAR-T1 초과 → DIAGNOSING→ESCALATED 전이
        EMIT oc.sdar.diagnosis.failed(
            signal_ref=signal.signal_id,
            reason="DH-SDAR-T1 timeout exceeded (120s)",
            elapsed_ms=(now() - start_time).ms
        )
        ESCALATE(signal, reason="diagnosis_timeout")
        RAISE DiagnosisTimeoutError(DIAG_E002)
```

### 5.3 타임아웃 시 동작 명세

| 단계 | 동작 |
|------|------|
| 1 | DH-SDAR-T1(120초) 초과 감지 |
| 2 | 진행 중인 RCA/Classification/Impact 강제 중단 |
| 3 | `oc.sdar.diagnosis.failed` 이벤트 발행 (reason="timeout") |
| 4 | DIAG-E002 에러 코드 로깅 |
| 5 | DIAGNOSING→ESCALATED 상태 전이 (부록 A.3 예외 전이) |
| 6 | I-20 에스컬레이션 페이로드 발송 |

### 5.4 SDAR_SPEC §7.2 S2 타임아웃 60초와의 관계

> **스코프 차이**: SDAR_SPEC §7.2의 S2_DIAGNOSED 타임아웃=60초는 **상태 레벨** 타임아웃 (S2 상태에 머무는 최대 시간), DH-SDAR-T1=120초는 **프로세스 레벨** 타임아웃 (Layer 2 진단 전체 프로세스 소요 시간). S1_DETECTED(30초 상태 타임아웃) 이후 진입하므로 전체 프로세스 120초 = S1 대기(최대 30초) + S2 실행(최대 60초) + 전이 오버헤드(최대 30초)로 분해된다.

### 5.5 설정 가능 파라미터

| 파라미터 | 기본값 | 범위 | 설명 |
|---------|-------|------|------|
| `DH_SDAR_T1` | 120초 | 30초~600초 | Diagnosis 전체 프로세스 timeout |
| `DH_SDAR_T1_WARN_RATIO` | 0.8 | 0.5~0.95 | timeout 경고 발생 비율 |
| `RCA_MAX_LOG_WINDOW` | 300초 | 60초~1800초 | RCA 로그 조회 윈도우 |
| `RCA_MAX_CANDIDATES` | 5 | 1~10 | RCA 최대 후보 수 |
| `CLASSIFICATION_CONFIDENCE_THRESHOLD` | 0.5 | 0.3~0.9 | 분류 최소 confidence |

---

## 6. MAX_AUTO_REPAIRS_PER_ISSUE_PER_HOUR=3 (LOCK L6) 카운팅 기준점

### 6.1 카운팅 규칙

Layer 2 진단 시 동일 이슈의 과거 수리 이력을 확인하여 L6 제한에 도달 여부를 `SDARDiagnosis.previous_occurrences` 필드에 기록한다.

```
FUNCTION check_l6_limit(error_code: str) -> Tuple[int, bool]:
    # LOCK L6: MAX_AUTO_REPAIRS_PER_ISSUE_PER_HOUR = 3
    
    count = repair_history.count(
        error_code=error_code,
        window=3600,  # 1시간
        status="completed"  # 완료된 수리만 카운트
    )
    
    limit_reached = count >= 3  # L6 상한
    
    IF limit_reached:
        LOG warn("L6 limit reached", error_code=error_code, count=count)
        # Layer 3에서 AR-Level 강등 또는 에스컬레이션 판단에 사용
    
    RETURN (count, limit_reached)
```

### 6.2 L6 제한 도달 시 Layer 3 전달 정보

`SDARDiagnosis.previous_occurrences`에 카운트를 기록하여 Layer 3(Prescription)이 수리 계획 수립 시 참조한다. L6 상한(3회) 도달 시 Layer 3은 자동수리를 억제하고 인간 에스컬레이션을 권장한다.

---

## 7. 이벤트 카탈로그 (SDAR_SPEC §2.3)

| 이벤트 타입 | 설명 | 발행 시점 | 포함 데이터 |
|------------|------|----------|-----------|
| `oc.sdar.diagnosis.started` | 진단 시작 | Layer 2 진입 시 | signal_ref, trace_id, start_time |
| `oc.sdar.diagnosis.root_cause_found` | 근본 원인 특정 | RCA 완료 시 | cause_id, confidence, source_method |
| `oc.sdar.diagnosis.classified` | 오류 분류 완료 | Classification 완료 시 | error_category, error_code, severity |
| `oc.sdar.diagnosis.impact_assessed` | 영향 범위 평가 완료 | Impact Assessment 완료 시 | blast_radius_score, scope_count, propagation |
| `oc.sdar.diagnosis.completed` | 진단 완료 | SDARDiagnosis 생성 완료 시 | diagnosis_id, duration_ms, error_category |
| `oc.sdar.diagnosis.failed` | 진단 실패 | 타임아웃/원인 특정 불가 시 | signal_ref, reason, elapsed_ms |

---

## 8. 에러 코드 카탈로그 (DH-2: Layer 2)

| 에러 코드 | 심각도 | 설명 | 복구 가능 | 처리 |
|----------|--------|------|----------|------|
| `DIAG-E001` | ERROR | RCA 분석 실패 — 근본 원인 특정 불가 | YES | 부분 결과로 SDARDiagnosis 생성 (confidence 감소), 3회 재시도 후 에스컬레이션 |
| `DIAG-E002` | CRITICAL | DH-SDAR-T1 timeout 초과 (120초) | NO | DIAGNOSING→ESCALATED 전이, I-20 에스컬레이션 |
| `DIAG-E003` | ERROR | 오류 분류 불가 — 알려지지 않은 failure_code | YES | 기본 CATEGORY A(Infra) 분류 + 수동 검토 플래그, confidence 감소 |
| `DIAG-E004` | WARN | S-4 Pattern Miner 연결 실패 | YES | 패턴 매칭 건너뛰기, 나머지 기법으로 RCA 계속 |
| `DIAG-E005` | ERROR | Impact Assessment 실패 — 의존성 그래프 조회 오류 | YES | 기본 impact(isolated, user_impact=degraded) 적용, 수동 검토 플래그 |
| `DIAG-E006` | ERROR | Layer 1 SDARDetectionSignal 스키마 불일치 | YES | 호환 가능 필드로 파싱 시도, 실패 시 에스컬레이션 |
| `DIAG-E007` | WARN | 동일 이슈 L6 상한 접근 (2/3회) | YES | Layer 3에 L6 경고 전달, 자동수리 억제 권장 |
| `DIAG-E008` | CRITICAL | CATEGORY E 보안 오류 감지 | NO | 즉시 차단 + DIAGNOSING→ESCALATED 전이 (LOCK L15) |
| `DIAG-E009` | WARN | 복수 root_cause 간 confidence 차이 미미 (<0.1) | YES | 모든 후보 유지, primary_root_cause_idx 경고 주석 |
| `DIAG-E010` | ERROR | 과거 수리 이력 조회 실패 | YES | previous_occurrences=0으로 기본값 설정, 수동 검토 플래그 |
| `DIAG-E011` | WARN | RCA 기법 일부 동작 불가 (S-4 제외 3기법 중 1건 실패) | YES | 가용 기법으로 계속, confidence 감소 |
| `DIAG-E012` | CRITICAL | Kill Switch 활성화로 Diagnosis 중단 | NO | 즉시 중단, SDAR_S0_MONITORING(IDLE) 전이 (LOCK L14) |

### 8.1 예외 처리 정책 표

| error_code | recoverable | 처리 | 재시도 횟수 | 에스컬레이션 조건 |
|-----------|-------------|------|-----------|-----------------|
| DIAG-E001 | YES | 부분 결과 + confidence 감소 | 3 | 3회 연속 실패 |
| DIAG-E002 | NO | 즉시 에스컬레이션 | 0 | 즉시 (timeout) |
| DIAG-E003 | YES | 기본 분류 + 수동 검토 | 1 | 분류 불가 지속 |
| DIAG-E004 | YES | 부분 RCA 계속 | 3 | 3회 연속 연결 실패 |
| DIAG-E005 | YES | 기본 impact 적용 | 2 | 2회 실패 |
| DIAG-E006 | YES | 호환 파싱 시도 | 1 | 파싱 실패 |
| DIAG-E007 | YES | L6 경고 전달 | N/A | N/A |
| DIAG-E008 | NO | 즉시 에스컬레이션 | 0 | 즉시 (CATEGORY E) |
| DIAG-E009 | YES | 모든 후보 유지 | N/A | N/A |
| DIAG-E010 | YES | 기본값 설정 | 2 | 2회 실패 |
| DIAG-E011 | YES | 가용 기법 계속 | N/A | 모든 기법 실패 |
| DIAG-E012 | NO | 즉시 중단 | 0 | Kill Switch 해제 대기 |

---

## 9. 에스컬레이션 페이로드 구조 (I-20 경유, R-01-8)

### 9.1 Diagnosis Timeout 에스컬레이션

Layer 2에서 DH-SDAR-T1(120초) 초과 시:

```json
{
  "escalation": {
    "type": "sdar_diagnosis_timeout",
    "escalation_id": "uuid-v4",
    "source": "sdar.layer2.diagnosis",
    "timestamp": "2026-04-13T12:02:00Z",
    "severity": "critical"
  },
  "error": {
    "code": "DIAG-E002",
    "message": "Diagnosis timeout exceeded — DH-SDAR-T1=120s",
    "elapsed_ms": 120500,
    "signal_ref": "sig_uuid-v4",
    "partial_result": {
      "rca_completed": true,
      "classification_completed": false,
      "impact_completed": false
    }
  },
  "context": {
    "signal_channel": "health",
    "signal_severity": "critical",
    "source_module": "I-6",
    "rca_candidates_found": 2,
    "rca_elapsed_ms": 95000,
    "classification_elapsed_ms": 25500
  },
  "recovery": {
    "attempted": ["timeout_extension_not_available"],
    "all_failed": true,
    "recommended": "human_intervention",
    "estimated_impact": "Diagnosis incomplete — repair plan cannot be generated"
  },
  "trace_id": "uuid-v4"
}
```

### 9.2 CATEGORY E 에스컬레이션

CATEGORY E (보안 오류) 감지 시 (LOCK L15):

```json
{
  "escalation": {
    "type": "sdar_security_alert",
    "escalation_id": "uuid-v4",
    "source": "sdar.layer2.diagnosis",
    "timestamp": "2026-04-13T12:01:00Z",
    "severity": "critical"
  },
  "error": {
    "code": "DIAG-E008",
    "message": "CATEGORY E security error detected — auto-repair NEVER allowed (LOCK L15)",
    "error_category": "E",
    "error_code": "SDAR_E01_INJECTION_DETECTED",
    "signal_ref": "sig_uuid-v4"
  },
  "context": {
    "signal_channel": "error_pattern",
    "signal_severity": "critical",
    "source_module": "I-10",
    "root_cause": {
      "cause_id": "rc_sec_001",
      "description": "Prompt injection attempt detected",
      "confidence": 0.99,
      "evidence_refs": ["evt_sec_001", "evt_sec_002"]
    },
    "category_e_rules": [
      "auto_repair_forbidden",
      "immediate_block",
      "audit_log_critical",
      "human_notification_mandatory",
      "forensic_data_30day_retention"
    ]
  },
  "recovery": {
    "attempted": ["immediate_block_executed", "audit_log_created"],
    "all_failed": false,
    "recommended": "human_security_review",
    "estimated_impact": "Potential security breach — manual investigation required",
    "forensic_retention_days": 30
  },
  "trace_id": "uuid-v4"
}
```

### 9.3 RCA 실패 에스컬레이션

RCA 3회 연속 실패 시:

```json
{
  "escalation": {
    "type": "sdar_diagnosis_rca_failure",
    "escalation_id": "uuid-v4",
    "source": "sdar.layer2.diagnosis",
    "timestamp": "2026-04-13T12:01:30Z",
    "severity": "error"
  },
  "error": {
    "code": "DIAG-E001",
    "message": "RCA failed 3 consecutive times — root cause unidentifiable",
    "consecutive_failures": 3,
    "signal_ref": "sig_uuid-v4"
  },
  "context": {
    "signal_channel": "health",
    "signal_severity": "error",
    "source_module": "I-6",
    "attempted_methods": ["log_correlation", "dependency_traversal", "pattern_match", "temporal_correlation"],
    "method_results": {
      "log_correlation": "no_causal_chain_found",
      "dependency_traversal": "no_upstream_failures",
      "pattern_match": "no_match",
      "temporal_correlation": "no_recent_changes"
    }
  },
  "recovery": {
    "attempted": ["retry_1", "retry_2", "retry_3"],
    "all_failed": true,
    "recommended": "human_investigation",
    "estimated_impact": "Unknown root cause — manual diagnosis required"
  },
  "trace_id": "uuid-v4"
}
```

---

## 10. Phase별 복구 전략

### 10.1 복구 흐름도

```
Phase 1 (현재) — Diagnosis 자체 복구
  ├── DIAG-E001: RCA 재시도 (최대 3회) → 부분 결과 전달
  ├── DIAG-E002: timeout 에스컬레이션 (DH-SDAR-T1=120초)
  ├── DIAG-E003: 기본 CATEGORY A 분류 → 수동 검토 플래그
  ├── DIAG-E004: S-4 제외 RCA 계속
  ├── DIAG-E005: 기본 impact 적용
  ├── DIAG-E008: CATEGORY E 즉시 에스컬레이션 (LOCK L15)
  └── 실패 시 → I-20 에스컬레이션

Phase 2 — Diagnosis + Detection 연계 복구
  ├── Layer 1 오탐 역전파 기반 분류 정확도 향상
  ├── RCA confidence 임계값 자동 조정
  └── S-4 패턴 DB 피드백 루프

Phase 3 — 전체 Pipeline 통합 복구
  ├── Layer 4/5 결과 → 분류 정확도 역추적 검증
  ├── CATEGORY 변경 이력 기반 분류기 자동 튜닝
  └── Blast Radius 예측 정확도 개선 (실제 영향 vs 예측 비교)

Phase 4 — 거버넌스 완성
  ├── 진단 정확도 KPI 자동 보고
  ├── 카테고리별 진단 소요 시간 감사
  └── L6 도달 빈도 통계 → 근본 문제 식별
```

### 10.2 다운그레이드 시 confidence penalty 표

| 다운그레이드 상황 | 영향받는 단계 | confidence 감소 | 비고 |
|-----------------|-------------|----------------|------|
| S-4 연결 실패 (DIAG-E004) | Step 2-1 RCA | -25% | 패턴 매칭 불가 |
| RCA 기법 1건 실패 (DIAG-E011) | Step 2-1 RCA | -15% | 교차 검증 약화 |
| 의존성 그래프 조회 실패 (DIAG-E005) | Step 2-3 Impact | -30% | 범위 평가 불완전 |
| 과거 이력 조회 실패 (DIAG-E010) | L6 카운팅 | -10% | 수리 횟수 미확인 |
| 분류 불가 → 기본 CATEGORY A (DIAG-E003) | Step 2-2 분류 | -40% | 분류 정확도 미보장 |
| 단일 RCA 기법만 동작 | Step 2-1 전체 | -50% | 교차 검증 불가 |

---

## 11. 로깅 포맷 (R-01-7 structured JSON)

### 11.1 Diagnosis 진행 로그 구조

```json
{
  "log_event": {
    "event_type": "oc.sdar.diagnosis.started",
    "timestamp": "2026-04-13T12:00:00Z",
    "level": "INFO",
    "trace_id": "uuid-v4"
  },
  "error": {
    "code": null,
    "message": null,
    "recoverable": null
  },
  "context": {
    "signal_ref": "sig_uuid-v4",
    "signal_channel": "health",
    "signal_severity": "critical",
    "source_module": "I-6",
    "dh_sdar_t1_timeout_s": 120,
    "rca_methods_enabled": ["log_correlation", "dependency_traversal", "pattern_match", "temporal_correlation"]
  },
  "recovery": {
    "action": "diagnosis_in_progress",
    "timeout_remaining_s": 120
  },
  "trace_id": "uuid-v4"
}
```

### 11.2 RCA 완료 로그 구조

```json
{
  "log_event": {
    "event_type": "oc.sdar.diagnosis.root_cause_found",
    "timestamp": "2026-04-13T12:00:05Z",
    "level": "INFO",
    "trace_id": "uuid-v4"
  },
  "error": {
    "code": null,
    "message": null,
    "recoverable": null
  },
  "context": {
    "signal_ref": "sig_uuid-v4",
    "rca_method": "log_correlation",
    "cause_id": "rc_001",
    "confidence": 0.92,
    "evidence_count": 3,
    "candidates_total": 2,
    "elapsed_ms": 5200
  },
  "recovery": {
    "action": "proceed_to_classification",
    "timeout_remaining_s": 114.8
  },
  "trace_id": "uuid-v4"
}
```

### 11.3 Classification 완료 로그 구조

```json
{
  "log_event": {
    "event_type": "oc.sdar.diagnosis.classified",
    "timestamp": "2026-04-13T12:00:06Z",
    "level": "INFO",
    "trace_id": "uuid-v4"
  },
  "error": {
    "code": null,
    "message": null,
    "recoverable": null
  },
  "context": {
    "signal_ref": "sig_uuid-v4",
    "error_category": "A",
    "error_code": "SDAR_A04_API_429",
    "severity": "warn",
    "classification_method": "direct_mapping",
    "is_never_auto": false,
    "elapsed_ms": 6100
  },
  "recovery": {
    "action": "proceed_to_impact_assessment",
    "timeout_remaining_s": 113.9
  },
  "trace_id": "uuid-v4"
}
```

### 11.4 에러 로그 구조

```json
{
  "log_event": {
    "event_type": "oc.sdar.diagnosis.error",
    "timestamp": "2026-04-13T12:02:00Z",
    "level": "ERROR",
    "trace_id": "uuid-v4"
  },
  "error": {
    "code": "DIAG-E002",
    "message": "Diagnosis timeout exceeded — DH-SDAR-T1=120s",
    "recoverable": false,
    "elapsed_ms": 120500
  },
  "context": {
    "signal_ref": "sig_uuid-v4",
    "rca_completed": true,
    "classification_completed": false,
    "impact_completed": false,
    "partial_root_causes": 2
  },
  "recovery": {
    "action": "escalate_to_human",
    "escalation_type": "sdar_diagnosis_timeout",
    "escalation_id": "esc_uuid-v4"
  },
  "trace_id": "uuid-v4"
}
```

### 11.5 CATEGORY E 보안 감사 로그 구조 (LOCK L15 — 삭제 불가)

```json
{
  "log_event": {
    "event_type": "oc.sdar.diagnosis.security_alert",
    "timestamp": "2026-04-13T12:01:00Z",
    "level": "CRITICAL",
    "trace_id": "uuid-v4",
    "audit": {
      "immutable": true,
      "retention_days": 30,
      "lock_ref": "L15"
    }
  },
  "error": {
    "code": "DIAG-E008",
    "message": "CATEGORY E security error — auto-repair NEVER allowed",
    "recoverable": false,
    "error_category": "E",
    "error_code": "SDAR_E01_INJECTION_DETECTED"
  },
  "context": {
    "signal_ref": "sig_uuid-v4",
    "source_module": "I-10",
    "blocked_action": "immediate_session_block",
    "forensic_data_preserved": true,
    "category_e_rules_applied": [
      "auto_repair_forbidden",
      "immediate_block",
      "audit_log_critical_immutable",
      "human_notification",
      "forensic_30day_retention"
    ]
  },
  "recovery": {
    "action": "human_security_review_required",
    "escalation_id": "esc_uuid-v4",
    "auto_recovery_blocked": true,
    "reason": "LOCK L15 — CATEGORY E auto-repair absolutely forbidden"
  },
  "trace_id": "uuid-v4"
}
```

---

## 12. LOCK 참조 요약

| LOCK # | 항목 | 값 | 본 문서 적용 위치 |
|--------|------|-----|-----------------|
| **L1** | 5-Layer Pipeline 단계 정의 | Detection → Diagnosis → Prescription → Repair → Verification | §1 개요 — Layer 2 위치 |
| **L6** | MAX_AUTO_REPAIRS_PER_ISSUE_PER_HOUR | 3 (동일 이슈 시간당 최대 3회) | §6 — L6 카운팅 기준점 |
| **DH-SDAR-T1** | Diagnosis 단계 timeout | 120초 (DEFINED-HERE) | §5 — timeout 적용 상세 |

### 관련 LOCK (본 문서에서 참조만)

| LOCK # | 항목 | 값 | 참조 목적 |
|--------|------|-----|----------|
| L2 | 7-State Machine | DIAGNOSING 상태 관련 | §5 timeout → ESCALATED 전이 |
| L9 | NOTIFICATION_MANDATORY | 모든 활동 알림 필수 | §1.1 알림 요구사항 |
| L14 | Kill Switch 트리거 조건 | 모든 RBAC 역할 활성화 | DIAG-E012 Kill Switch 중단 |
| L15 | CATEGORY E 자동수리 절대 금지 | 5규칙 적용 | §2.2 CATEGORY E 분류, §9.2 에스컬레이션 |

---

## 13. Phase 2 테스트 시나리오

| # | 시나리오 | 기대 결과 | 검증 방법 |
|---|---------|----------|----------|
| T-DIAG-01 | RCA: 로그 상관 분석으로 DB 장애 원인 특정 | SDARDiagnosis(root_causes[0].source=log_correlation, confidence>=0.7) | root_cause 검증 + evidence_refs 확인 |
| T-DIAG-02 | RCA: 의존성 그래프로 상위 모듈 장애 추적 | SDARDiagnosis(root_causes[0].source=dependency_traversal) | related_modules + causal_chain 확인 |
| T-DIAG-03 | RCA: S-4 패턴 매칭 성공 | SDARDiagnosis(pattern_match_ref != null, confidence>=0.8) | pattern_match_ref + S-4 패턴 ID 확인 |
| T-DIAG-04 | Classification: CATEGORY A(Infra) — SDAR_A04_API_429 | error_category="A", error_code="SDAR_A04_API_429", severity="warn" | 분류 결과 검증 |
| T-DIAG-05 | Classification: CATEGORY E(Security) — 즉시 에스컬레이션 | DIAG-E008 발생, DIAGNOSING→ESCALATED 전이, 감사 로그 생성 | 에스컬레이션 페이로드 + 감사 로그 + L15 규칙 적용 확인 |
| T-DIAG-06 | Impact: Blast Radius — cascading propagation | blast_radius_score >= 0.7, propagation="cascading" | scope 모듈 목록 + 점수 계산 검증 |
| T-DIAG-07 | DH-SDAR-T1 timeout 초과 (120초) | DIAG-E002 발생, DIAGNOSING→ESCALATED 전이 | timeout 에스컬레이션 페이로드 + 상태 전이 확인 |
| T-DIAG-08 | L6 상한 도달 (3/3회) | DIAG-E007 경고, previous_occurrences=3 | L6 카운팅 + Layer 3 전달 데이터 확인 |
| T-DIAG-09 | S-4 연결 실패 중 RCA | RCA 계속(3기법), confidence -25%, DIAG-E004 로깅 | 부분 동작 + confidence 감소 검증 |
| T-DIAG-10 | 알 수 없는 failure_code 분류 | DIAG-E003 발생, 기본 CATEGORY A 분류, 수동 검토 플래그 | 기본 분류 + 플래그 확인 |
| T-DIAG-11 | Kill Switch 활성화 중 Diagnosis 진행 | DIAG-E012 발생, 즉시 중단, S0 전이 | 중단 확인 + 상태 전이 검증 |
| T-DIAG-12 | 복수 root_cause confidence 차이 <0.1 | DIAG-E009 경고, 모든 후보 유지 | 후보 목록 + 경고 로그 확인 |
| T-DIAG-13 | Layer 1 SDARDetectionSignal 스키마 불일치 | DIAG-E006 발생, 호환 파싱 시도 | 파싱 결과 + 에러 로그 확인 |
| T-DIAG-14 | 전체 3단계 정상 흐름 (CATEGORY A, LOW risk) | SDARDiagnosis 정상 생성, 6개 이벤트 순차 발행 | 전체 이벤트 시퀀스 + 스키마 검증 |
| T-DIAG-15 | RCA 3회 연속 실패 | DIAG-E001 에스컬레이션, partial_result 전달 | 에스컬레이션 페이로드 + 부분 결과 확인 |

---

## 14. ISS-1 Layer 2 + ISS-2 해결 확인

| 검증 항목 | 상태 | 근거 |
|----------|------|------|
| 3단계 진단 전체 상세 (RCA, Classification, Impact Assessment) | **완료** | §2.1 Step 2-1, §2.2 Step 2-2, §2.3 Step 2-3 |
| `SDARDiagnosis` 출력 스키마 완전 정의 | **완료** | §4 전체 필드 + 서브 모델(SDARRootCause, SDARImpactAssessment) |
| CATEGORY A~E 분류 기준 포함 | **완료** | §2.2 CATEGORY A~E 상세 테이블 + 매핑 매트릭스 |
| DH-SDAR-T1=120초 timeout 정식 적용 및 동작 명세 | **완료** | §5 전체 — 적용 위치, 타임아웃 시 동작, 설정 파라미터 |
| L6 카운팅 기준점 명세 | **완료** | §6 — 카운팅 규칙 + Layer 3 전달 |
| 에러 코드 카탈로그 | **완료** | §8 DIAG-E001~DIAG-E012 |
| LOCK L1, L6, DH-SDAR-T1 매핑 | **완료** | §12 LOCK 참조 요약 |
| 이벤트 카탈로그 | **완료** | §7 (oc.sdar.diagnosis.*) |
| ISS-1 Layer 2 | **해결** | 본 문서 전체 — Layer 2 L3 상세 정의 완성 |
| ISS-2 (DH-SDAR-T1=120초) | **해결** | §5 — timeout 적용 상세, SDAR_SPEC §7.2 S2 타임아웃과의 관계 명시 |

---

*끝*
