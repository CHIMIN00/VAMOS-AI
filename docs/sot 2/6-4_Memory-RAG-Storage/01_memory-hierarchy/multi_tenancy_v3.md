---
title: 멀티테넌시 V3 (tenant_id 3 계층 + cross-tenant 격리)
domain: 6-4_Memory-RAG-Storage
phase: 4
task: P4-2
status: APPROVED
version: V3
created: 2026-05-27
session: phase4_6-4_p4-2_2026-05-27
authority_chain:
  - RULE 1.3
  - DESIGN 2.0 / D2.0-06 §1 (project_id 격리)
  - Part2 V1-Phase 2 / RULE 1.3 §7.2
  - LOCK-MR-015 (Deny 벡터 삽입 금지)
  - LOCK-MR-017 (project_id 격리 → V3 확장 tenant_id 3 계층)
  - LOCK-MR-019 (루프 저장 폭주 방지)
cross_handoff:
  - 6-2_Security-Governance (RBAC × 테넌트)
  - 6-12_Event-Logging (SOC-2 감사 로그 LogEvent)
  - 5-2_File-Context (테넌트별 컨텍스트 윈도우, sandbox-only reference)
---

# 멀티테넌시 V3 — tenant_id 3 계층 + cross-tenant 격리

> **Phase 4 Task P4-2**: V1 `project_id` 단일 격리 → V3 `tenant_id → project_id → memory_record` 3 계층.
> **LOCK-MR-017 V3 확장 (재정의 아님)**: `<!-- V3 EXTENSION, NOT REDEFINITION -->`.
> **5-2 발신 측 specialty first**: W3 V2 Ensemble Embedding + W6 V2 KG Extraction + W2 V2 Ring Attention 양방향 정합 baseline.

---

## 1. 배경 및 동기

V1 단계에서 `project_id`는 사용자별 작업공간 분리를 제공했습니다 (LOCK-MR-017 정본). 그러나 V3 엔터프라이즈 환경에서는 다음 요구사항이 부각되었습니다:

1. **엔터프라이즈 다중 조직**: 단일 배포 인스턴스에 복수 조직(회사/팀)이 격리되어 운영.
2. **SaaS 수준 격리**: 한 테넌트의 데이터/메트릭/벡터가 다른 테넌트에 절대 노출 불가 (data exfiltration, side-channel 차단).
3. **비용 분리**: 테넌트별 사용량 계측 + 청구 + memory budget per tenant.
4. **컴플라이언스**: 테넌트 X의 GDPR Right to Erasure가 테넌트 Y에 영향 없도록 격리.
5. **RBAC 결합**: 테넌트 × 프로젝트 × 역할 3-way 권한 매트릭스.
6. **테넌트 marketplace (Phase 5+)**: 테넌트별 플러그인/V3 확장 슬롯 활성화 차등.

본 V3는 **LOCK-MR-017을 재정의하지 않고**, `tenant_id` 컬럼/체계를 상위에 추가하여 격리 계층을 1단계 → 3단계로 확장합니다. 정본 LOCK-MR-017 (`project_id` 간 데이터 혼합 금지)는 변경 없이 유지됩니다.

---

## 2. LOCK 인용 매트릭스 (3 LOCK + V3 확장 주석)

| # | LOCK ID | 정본 출처 | V3 적용 | 재정의 여부 |
|---|---------|----------|---------|------------|
| 1 | LOCK-MR-015 | D2.0-06 §3.2 | Deny 판정 시 벡터 삽입 절대 금지. 테넌트 간 cross-leak 방지 추가 적용 | ❌ 재정의 없음 |
| 2 | LOCK-MR-017 | D2.0-06 §1 / RULE 1.3 §7.2 | 정본 `project_id 간 혼합 금지` 유지 + V3 확장 (tenant_id 3 계층) `<!-- V3 EXTENSION, NOT REDEFINITION -->` | ❌ 재정의 없음 (확장만) |
| 3 | LOCK-MR-019 | D2.0-06 머리글 | 루프 저장 폭주 방지. 테넌트별 memory budget 초과 시 동일 정책 강제 | ❌ 재정의 없음 |

<!-- LOCK-MR-017 V3 확장 시작 -->
<!-- V3 EXTENSION, NOT REDEFINITION -->
**LOCK-MR-017 V3 확장 (tenant_id 3 계층)**:

| 계층 | 식별자 | 의미 | 격리 정책 |
|------|--------|------|---------|
| L1 (상위) | `tenant_id` | 조직/회사/팀 | cross-tenant 절대 금지 (Deny) |
| L2 (중위) | `project_id` | 테넌트 내 프로젝트 | cross-project 금지 (정본 LOCK-MR-017) |
| L3 (하위) | `memory_record_id` | 개별 메모리 레코드 | 권한 매트릭스 + RBAC |

**정본 LOCK-MR-017 (project_id 격리)는 변경 없이 유지**됩니다. V3는 상위에 tenant_id 계층을 추가하는 확장입니다.
<!-- LOCK-MR-017 V3 확장 끝 -->

---

## 3. 격리 메커니즘 3종

### 3.1 메커니즘 A — 스키마/SQL 레벨 강제

모든 테이블에 `tenant_id` 컬럼 NOT NULL + (tenant_id, project_id) 복합 인덱스:

```sql
CREATE TABLE memory_records (
    record_id    UUID PRIMARY KEY,
    tenant_id    TEXT NOT NULL,        -- L1
    project_id   TEXT NOT NULL,        -- L2 (정본 LOCK-MR-017)
    ...
    CONSTRAINT chk_tenant_format CHECK (tenant_id ~ '^T-[A-Z0-9]{4,}$')
);
CREATE INDEX idx_tenant_project ON memory_records (tenant_id, project_id);

-- Row Level Security (PostgreSQL)
ALTER TABLE memory_records ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON memory_records
    USING (tenant_id = current_setting('app.tenant_id'))
    WITH CHECK (tenant_id = current_setting('app.tenant_id'));
```

### 3.2 메커니즘 B — 어댑터 레벨 강제

PostgresqlRDBStore (P4-1)의 모든 메서드는 `tenant_id`도 인자로 받으며, WHERE 절에 강제 포함:

```python
def save(self, table, tenant_id, project_id, record):
    if not (tenant_id and project_id):
        raise ValidationError("LOCK-MR-017 V3: tenant_id + project_id required")  # assert 금지 (-O 제거 방지)
    # INSERT 시 tenant_id NOT NULL 강제
```

### 3.3 메커니즘 C — 애플리케이션 레벨 강제 (테넌트 컨텍스트)

```python
@contextmanager
def tenant_context(tenant_id: str, project_id: str):
    """요청 처리 시 tenant context를 thread/async-local에 설정.

    이 컨텍스트 밖에서 RDBStore 호출 시 TenantContextMissingError raise.
    """
    token = _TENANT_CTX.set({"tenant_id": tenant_id, "project_id": project_id})
    try:
        yield
    finally:
        _TENANT_CTX.reset(token)
```

3 메커니즘 ALL 적용 시 **defense-in-depth**가 되어, 한 레이어 우회 시 다른 레이어가 차단합니다.

---

## 4. cross-tenant 차단 시나리오

| # | 시나리오 | 차단 메커니즘 | 결과 |
|---|---------|-------------|------|
| 1 | T-A 사용자가 T-B record_id를 알아내고 GET 시도 | A.SQL WHERE tenant_id=T-A → 0 row | NotFound |
| 2 | T-A 사용자가 어플 레벨 인젝션으로 tenant_id=T-B 위장 | B.assertion + JWT 검증 + RLS | PermissionDenied |
| 3 | T-A의 벡터가 T-B 임베딩 인덱스에 누출 | 별도 Qdrant collection per tenant | 인덱스 분리 |
| 4 | T-A 사용자가 SQL injection으로 ; DROP table | parameterized query + 권한 분리 | SQL syntax error |
| 5 | 로그/메트릭에서 T-A 식별자 노출 | 6-12 LogEvent tenant_id hash 마스킹 | 익명화 |
| 6 | 캐시(semantic_cache)에서 cross-tenant hit | cache key prefix = `{tenant_id}:` | 격리 |
| 7 | Dream Mode 통합 작업 시 (P4-4) cross-tenant 처리 | tenant_id 별 separate pipeline | 격리 |

---

## 5. RBAC × 테넌트 매트릭스 (6-2 연동)

6-2 Security-Governance의 RBAC 시스템과 결합:

| 역할 | tenant_id 범위 | project_id 범위 | 작업 |
|------|--------------|----------------|------|
| `tenant_admin` | 자기 테넌트 | 자기 테넌트 내 모든 프로젝트 | CRUD + 권한 부여 |
| `project_owner` | 자기 테넌트 | 자기 프로젝트 | CRUD + 멤버 초대 |
| `project_editor` | 자기 테넌트 | 자기 프로젝트 | CRU (delete 제한) |
| `project_viewer` | 자기 테넌트 | 자기 프로젝트 | R |
| `system_admin` | 시스템 전체 (감사 목적) | — | 감사 로그 R (PII 마스킹) |
| `tenant_billing` | 자기 테넌트 | 사용량 메트릭만 | R metrics |

**불변 사실**: 어떤 역할도 cross-tenant 접근 권한을 가지지 않음. `system_admin`조차 raw 데이터가 아닌 마스킹된 메트릭만 조회 가능.

---

## 6. memory budget per tenant

테넌트별 메모리 사용량 budget (LOCK-MR-019 정합):

| 항목 | 단위 | 예시 budget (T-PRO 플랜) | 초과 시 |
|------|------|----------------------|--------|
| L0 (Session) | 레코드 수 / 24h | 10,000 | 신규 INSERT 차단 (LOCK-MR-019) |
| L1 (Project) | 레코드 수 (active) | 100,000 | promotion 차단 + Dream Mode P4-4 강제 정리 |
| L2 (Long-term) | 레코드 수 (active) | 1,000,000 | 신규 promotion 보류 + tenant_admin 알림 |
| L3 (Procedural) | 레코드 수 | 10,000 | LOCK-MR-016 ApprovalGate 더 엄격 |
| 벡터 저장 | GB | 50 | 압축/배제 + 알림 |
| 일일 쿼리 | QPS | 100 | rate limit |

초과 시 6-12 LogEvent + 6-1 UI 알림 + tenant_admin 이메일.

---

## 7. 비용 추적

```python
@dataclass
class TenantUsage:
    tenant_id: str
    date: datetime.date
    record_count_l0: int
    record_count_l1: int
    record_count_l2: int
    record_count_l3: int
    vector_size_bytes: int
    query_count: int
    write_count: int
    storage_size_bytes: int

def aggregate_usage_daily(tenant_id: str, day: datetime.date) -> TenantUsage:
    """일 단위 사용량 집계. 6-12 LogEvent 표준 출력 + 청구 시스템 전달."""
```

비용 모델:

| 자원 | 단가 (예시) | 비고 |
|------|-----------|------|
| L0 record | $0.0001 / 1k records | 단기 |
| L1 record | $0.0010 / 1k records | 중기 |
| L2 record | $0.0050 / 1k records | 영구 |
| 벡터 저장 | $0.10 / GB / month | Qdrant + pgvector |
| 쿼리 | $0.001 / 1k queries | LLM 호출 별도 |

---

## 8. cross-domain handoff

### 8.1 6-2 Security-Governance (RBAC × 테넌트)

- 6-2 RBAC 매트릭스 (LOCK-SC-XXX)와 본 §5 결합.
- 6-2 PII 마스킹 (P1-7 LOCK-MR-015 cross-ref)이 테넌트별 정책으로 적용 가능.

### 8.2 6-12 Event-Logging (SOC-2 감사)

- 모든 `save/update/delete` 호출은 `LogEvent`로 6-12 표준 emit.
- 필드: `tenant_id, project_id, record_id, actor, action, ts, ip_hash, user_agent_hash`.
- 보존 12 개월 (SOC-2 TSC), tenant_id는 hash 마스킹 옵션.

### 8.3 5-2 File-Context (테넌트별 컨텍스트 윈도우)

- 5-2 STAGE 9 RO TRUE 12 .md sandbox-only reference 처리.
- **5-2 외부 5 deps 발신 측 specialty first** P4-2 trigger 양방향 정합 baseline verify:
  - **W3 V2 (Ensemble Embedding 3-way)** ⊕ L2 (Embedding 2-way) — 보완 관계 (CF-V2-006 RESOLVED-INLINE 정식), 6-4 L2 V1 영역 변경 없음.
  - **W6 V2 (KG Extraction)** OFF default + 6-4 L18 KG Engine readonly (CF-V2-003 RESOLVED-INLINE 정식).
  - **W2 V2 (Ring Attention + KV Offload)** + L10 정합 inheritance.
  - **L18 + LOCK-MR-008 alpha NOTE**: Level 5 < Level 3 D2.0 LOCK 정합 직계.
- 본 V3는 5-2 V1 LOCK 재정의 권한 없음 (Level 5 < Level 3 D2.0 LOCK 정합 직계).

---

## 9. audit conditions (3건)

| # | 조건 | 측정 | Phase 5 gate |
|---|------|------|-------------|
| A1 | 모든 RDBMS 쿼리에 tenant_id WHERE 절 포함 | SQL static analysis | ✅ |
| A2 | cross-tenant 시도 7 시나리오 ALL 차단 | 통합 테스트 단위 케이스 | ✅ |
| A3 | tenant budget 초과 시 LOCK-MR-019 강제 | 시뮬레이션 + LogEvent 검증 | ✅ |

---

## 10. Phase 5 entry-gate 매핑 (P4-2)

- G4-1: V3 implementation 완료 — 본 문서.
- G4-2: Status DRAFT → APPROVED.
- G4-3: LOCK 변경 0, V3 확장 `<!-- V3 EXTENSION, NOT REDEFINITION -->` 주석 강제.
- G4-4: CONFLICT 변경 0.
- G4-5: cross-tenant 격리 검증 (DCL Deny 동작) staging 환경.
- G4-6: cross-handoff 6-2/6-12/5-2 forward-defined.
- G4-7: Phase 5+ tenant marketplace baseline.

---

## 11. 마이그레이션 전략 (V1 → V3)

기존 V1 데이터는 `project_id`만 가지고 있습니다. V3 전환 시 모든 레코드에 `tenant_id`를 부여해야 합니다.

### 11.1 단일 테넌트 모드 (default)

- 단일 사용자/단일 조직 deployment의 경우 모든 기존 데이터에 `tenant_id = 'T-DEFAULT'` 부여.
- 마이그레이션 SQL: `UPDATE memory_records SET tenant_id = 'T-DEFAULT' WHERE tenant_id IS NULL;`
- 이후 `ALTER TABLE memory_records ALTER COLUMN tenant_id SET NOT NULL;`

### 11.2 멀티 테넌트 부트스트랩

기존 `project_id` 패턴을 분석하여 자동 그룹화 (선택적):

```python
def derive_tenant_from_project_pattern(project_id: str) -> str:
    """프로젝트 ID 접두사로 테넌트 추론. 예: 'acme-web-001' → 'T-ACME'."""
    prefix = project_id.split("-")[0].upper()
    return f"T-{prefix}"
```

운영자 검토 후 일괄 UPDATE 권장 (수동 매핑 파일 제공).

### 11.3 점진적 활성화

| 단계 | 동작 | 영향 |
|------|------|------|
| Phase A | tenant_id 컬럼 추가 (NULL 허용) | 무영향 |
| Phase B | 모든 데이터 UPDATE | 일회성 batch |
| Phase C | NOT NULL constraint | DDL lock 짧음 |
| Phase D | RLS 활성화 | 어플 코드 변경 필수 |
| Phase E | cross-tenant 차단 enforcement | 완전 격리 모드 |

A→E 점진 전환 권장 (한 번에 E로 가면 운영 risk 높음).

## 12. 테스트 전략

### 12.1 단위 테스트

- 모든 RDBStore 메서드에 tenant_id 누락 → AssertionError.
- 잘못된 tenant_id 포맷 (`^T-[A-Z0-9]{4,}$` mismatch) → ValidationError.
- patch에 layer/b_series 포함 → 거부 (LOCK-MR-001/002).

### 12.2 통합 테스트 — 7 cross-tenant 시나리오

§4의 7 시나리오를 testcontainers-postgres 환경에서 자동화:

```python
@pytest.mark.parametrize("scenario", [
    "sql_where_filter",       # #1
    "jwt_tenant_spoof",       # #2
    "vector_index_leak",      # #3
    "sql_injection",          # #4
    "log_tenant_pii",         # #5
    "cache_cross_tenant",     # #6
    "dream_mode_cross",       # #7
])
def test_cross_tenant_blocking(scenario):
    ...
```

### 12.3 부하 테스트

- 100 테넌트 × 10 프로젝트 × 1000 레코드 = 1M 레코드.
- RLS ON/OFF 성능 비교 (RLS 오버헤드 < 10% 목표).
- tenant_id index 효과 확인 (EXPLAIN ANALYZE).

### 12.4 보안 침투 테스트

- 외부 보안팀 검토: cross-tenant data exfiltration 시도.
- 6-2 STRIDE 위협 모델링 결합.

## 13. 모니터링 메트릭

`statistics_dashboard_v3.md` (P4-5) 연동:

| 메트릭 | 단위 | 알림 |
|--------|------|------|
| `tenant_record_count_total{tenant_id, layer}` | gauge | budget 초과 시 |
| `tenant_query_qps{tenant_id}` | counter | rate limit 도달 시 |
| `tenant_storage_bytes{tenant_id}` | gauge | 80% / 95% / 100% |
| `cross_tenant_access_attempts_total` | counter | > 0 (즉시 알림) |
| `tenant_active_users{tenant_id}` | gauge | — |
| `tenant_budget_breach_count{tenant_id, resource}` | counter | > 0 (warn) |
| `rls_policy_violations_total` | counter | > 0 (CRITICAL) |
| `tenant_cost_usd_daily{tenant_id}` | gauge | 청구 시스템 |

## 14. tenant marketplace (Phase 5+ forward-defined)

테넌트별 V3 확장 슬롯 차등 활성화:

| 플랜 | tenant 수 | 프로젝트 수 | V3 확장 | 가격 |
|------|----------|------------|--------|------|
| Free | 1 | 1 | - | $0 |
| Pro | 1 | 10 | RAG V2 + Hybrid Search | $29/mo |
| Team | 1 | 50 | + KG V2 + Dream Mode | $99/mo |
| Enterprise | unlimited | unlimited | All + tenant marketplace API | Custom |

테넌트별 활성화 플래그는 `tenant_features` 테이블에서 관리.

## 15. SOC-2 / GDPR 정합성 (P4-3 연동)

- **Tenant Isolation 증거**: §4 7 시나리오 통합 테스트 결과 + RLS policy log.
- **GDPR Erasure**: 테넌트 X의 Erasure 요청은 X의 데이터만 영향, Y 영향 0.
- **Data Residency**: 테넌트별 region 선택 가능 (Phase 5+ — EU vs US).
- **DPIA per Tenant**: 고위험 처리 사전 평가, 테넌트 admin 동의.

## 16. 트러블슈팅 / 흔한 이슈

### 16.1 tenant_id 누락 오류

- 증상: `AssertionError: LOCK-MR-017 V3: tenant_id required`.
- 원인: 어플 요청 처리 시 `tenant_context()` 미진입.
- 대처: middleware (FastAPI Depends / Django middleware)에서 JWT 디코드 후 context 자동 설정.

### 16.2 RLS policy로 인한 unexpected 0 row

- 증상: 정상 데이터인데 SELECT 결과 0행.
- 원인: `app.tenant_id` session variable 미설정 또는 잘못된 값.
- 대처: 연결 풀에서 connection check-out 시 `SET app.tenant_id = '{tenant_id}'` 자동 실행.

### 16.3 cross-tenant 통합 시 (M&A 등)

- 시나리오: T-A가 T-B를 인수, 데이터 통합 필요.
- 절차: (1) tenant_admin 양측 승인 → (2) export from T-B with PII redaction → (3) import to T-A with new record_id → (4) T-B archive 후 90일 후 삭제 → (5) audit log 영구 보존.
- **자동 통합 금지** (LOCK-MR-017 V3 정신 — 수동 절차만).

### 16.4 cache cross-tenant hit 의심

- 증상: semantic_cache hit이 다른 테넌트 결과 반환.
- 원인: cache key prefix 누락.
- 대처: cache key는 항상 `{tenant_id}:{project_id}:{query_hash}` 형식 강제.
- 즉시 `rls_policy_violations_total` 메트릭 + PagerDuty CRITICAL.

## 17. 외부 표준 정합성

### 17.1 SaaS Multi-tenancy 패턴 표준

본 V3는 다음 표준 패턴을 따릅니다:

| 패턴 | 적용 | 비고 |
|------|------|------|
| Shared DB, Shared Schema (with tenant_id) | ✅ Primary | 비용 최적, RLS 격리 |
| Shared DB, Separate Schema per tenant | 옵션 (Enterprise) | 강한 격리 필요 시 |
| Database per tenant | 옵션 (강제 격리) | 매우 큰 테넌트만 |
| Hybrid (Bronze=shared / Gold=separate) | Phase 5+ | tenant 플랜 별 |

기본은 Shared DB + RLS (비용 최적 + 강한 격리). Enterprise 플랜은 별도 schema/DB 옵션 제공.

### 17.2 OWASP 권고

- A01:2021 Broken Access Control: §4 7 시나리오로 차단 검증.
- A03:2021 Injection: parameterized query + RLS.
- A04:2021 Insecure Design: defense-in-depth 3 메커니즘 (§3).
- A09:2021 Security Logging: 6-12 LogEvent 표준.

## 18. 변경 이력

| 일자 | 변경 | 비고 |
|------|------|------|
| 2026-05-27 | V3 NEW 최초 작성 | Phase 4 P4-2 SPEC Stage B production write |
