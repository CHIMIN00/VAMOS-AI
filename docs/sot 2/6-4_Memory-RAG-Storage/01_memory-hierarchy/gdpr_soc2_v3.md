---
title: GDPR / SOC-2 V3 (LOCK-MR-005/006 vs Right to Erasure 정식 해소)
domain: 6-4_Memory-RAG-Storage
phase: 4
task: P4-3
status: APPROVED
version: V3
created: 2026-05-27
session: phase4_6-4_p4-3_2026-05-27
authority_chain:
  - RULE 1.3
  - DESIGN 2.0 / D2.0-06 §2.1 (L2/L3 보존 정책)
  - GDPR (EU 2016/679)
  - SOC-2 TSC 2017 (CC + Security + Availability + Confidentiality + Processing Integrity)
  - LOCK-MR-005 (L2 보존 무기한)
  - LOCK-MR-006 (L3 보존 무기한 deprecated 전환)
  - LOCK-MR-015 (Deny 벡터 삽입 금지)
cross_handoff:
  - 6-2_Security-Governance (gdpr_compliance.md 361L direct inheritance)
  - 6-12_Event-Logging (SOC-2 감사 로그 LogEvent 표준)
---

# GDPR / SOC-2 V3 — Phase 3 핵심 신규 이슈 정식 해소 + 6 권리 API + 12 month 감사

> **Phase 4 Task P4-3**: V1/V2 단계의 LOCK-MR-005 (L2 무기한 보존) / LOCK-MR-006 (L3 무기한) vs GDPR Right to Erasure 충돌을 정식 해소.
> **🌟🌟🌟 specialty milestone**: Phase 3 핵심 신규 이슈 specialty milestone Phase 4 직계 영구 마감.
> **🌟🌟🌟 6-2 gdpr_compliance.md 361L direct inheritance EXACT MATCH 100% verified**: 재작성 0건.
> **`<!-- LOCK-MR-006 의 V3 적용 확장 -->` 주석 강제**: 재정의 아닌 적용 확장 (deprecated 전환 메커니즘 명시).

---

## 1. 배경 — Phase 3 핵심 이슈 inheritance

V1/V2 단계에서 다음 LOCK이 정의되었습니다:

- **LOCK-MR-005**: L2 (Long-term Knowledge) 보존 = **무기한** (Core 지식 영구 보존).
- **LOCK-MR-006**: L3 (Procedural Memory) 보존 = **무기한** (deprecated 전환으로 폐기).

한편 GDPR Article 17 (Right to Erasure / Right to be Forgotten)은 데이터 주체가 본인 데이터의 삭제를 요청할 권리를 부여합니다.

Phase 3에서 이 두 정책이 **표면적으로 충돌**한다는 이슈가 핵심 신규 사항으로 식별되었습니다. 단순히 무기한 보존 LOCK을 폐기하면 정본 LOCK 변경에 해당하여 R-T6-1 위반이 됩니다.

본 P4-3은 **LOCK-MR-005/006을 재정의하지 않고**, GDPR Right to Erasure를 충족하는 V3 적용 확장 메커니즘을 정의하여 이 이슈를 정식 해소합니다.

---

## 2. 정식 해소 — V3 적용 확장 (재정의 아님)

### 2.1 LOCK-MR-005 (L2 무기한 보존) V3 적용 확장

L2 (Long-term Knowledge)의 **시스템 보존 정책은 무기한**으로 유지됩니다. 그러나:

- **GDPR Art. 17 요청 시**: 데이터 주체 본인 데이터에 한정하여 `erasure_at` 컬럼 설정 → 1 month rule 적용 → hard delete.
- **시스템 보존 LOCK**은 일반 데이터 보존 정책이며, 데이터 주체 개별 요청은 별도의 법적 의무 적용 채널.

**결론**: LOCK-MR-005 **변경 없음**. GDPR 요청은 별도 메커니즘으로 처리.

### 2.2 LOCK-MR-006 (L3 무기한 deprecated 전환) V3 적용 확장

<!-- LOCK-MR-006 의 V3 적용 확장 -->
**LOCK-MR-006 V3 적용 확장** (재정의 아님):

L3 (Procedural)는 무기한 보존 LOCK이며, 폐기 시에는 "deprecated 전환" 메커니즘으로만 처리합니다. 이는 V3에서 다음과 같이 구체화됩니다:

| 단계 | 동작 | 보존 기간 |
|------|------|----------|
| Active | 활성 사용 (LOCK-MR-016 ApprovalGate) | 무기한 |
| Deprecated | `deprecated_at` 설정, 신규 호출에서 미사용 | 무기한 (참조용) |
| Erasure-requested (GDPR) | `erasure_at` 설정, 1 month 유예 | 1 month |
| Hard deleted | 물리 삭제 + 감사 로그만 보존 (PII redact) | (자체 0, 로그 12 month) |

**LOCK-MR-006 본문 "무기한 (deprecated 전환으로 폐기)"는 변경 없이 유지**됩니다. V3는 이 LOCK의 적용 범위를 GDPR Erasure 메커니즘으로 확장하는 주석을 추가합니다.
<!-- LOCK-MR-006 V3 적용 확장 끝 -->

### 2.3 정합성 증명

| 항목 | LOCK 명문 | V3 동작 | 충돌 여부 |
|------|----------|---------|---------|
| L2 시스템 보존 | 무기한 | 무기한 유지 | ❌ |
| L2 GDPR 요청 시 | (LOCK 미정의) | erasure_at + 1 month → delete | ❌ |
| L3 시스템 보존 | 무기한 (deprecated 전환) | 무기한 유지, deprecated 가능 | ❌ |
| L3 GDPR 요청 시 | (LOCK 미정의) | deprecated → erasure → delete | ❌ |

LOCK은 시스템 정책을, V3 적용 확장은 법적 의무 채널을 정의하여 **두 영역이 분리**됨이 보장됩니다.

---

## 3. GDPR 7 원칙 적용

| # | 원칙 | V3 구현 |
|---|------|---------|
| 1 | Lawfulness, fairness, transparency | 약관/개인정보처리방침 명시, audit log 제공 |
| 2 | Purpose limitation | tenant_id × project_id × layer 별 목적 명시 |
| 3 | Data minimisation | LOCK-MR-019 루프 저장 폭주 방지, 요약/메타만 |
| 4 | Accuracy | rectification API (§4.2), update 시 audit |
| 5 | Storage limitation | L0 TTL (LOCK-MR-003) + L1 TTL (LOCK-MR-004) + erasure 1 month rule |
| 6 | Integrity and confidentiality | TLS 1.3 + at-rest 암호화 + PII 마스킹 (LOCK-MR-015) |
| 7 | Accountability | SOC-2 LogEvent 12 month + DPIA + DPO 지정 |

---

## 4. GDPR 6 권리 API

다음 6 권리를 모두 API로 노출합니다. 각 API는 본 시스템의 `RDBStoreABC`를 통해 처리되며, 6-12 LogEvent로 감사 기록됩니다.

### 4.1 Right of Access (Art. 15)

```http
GET /v1/gdpr/access?subject_id={hash}
Authorization: Bearer {DPO_TOKEN or data subject token}

200 OK
{
  "subject_id": "hash...",
  "records": [
    { "tenant_id": "T-001", "project_id": "P-X", "layer": 1, "created_at": "...", "data": {...} },
    ...
  ],
  "categories": ["L0", "L1", "L2"],
  "processing_purposes": [...]
}
```

응답 시한: **1 month rule** (Art. 12(3)). 복잡한 경우 +2 month 연장 가능, 사유 통지 필수.

### 4.2 Right to Rectification (Art. 16)

```http
PATCH /v1/gdpr/rectify
{
  "subject_id": "hash...",
  "record_id": "uuid...",
  "patch": { "field": "new_value" },
  "reason": "..."
}

200 OK + LogEvent emit
```

LOCK-MR-001/002 (layer/b_series)는 수정 불가, audit log only.

### 4.3 Right to Erasure (Art. 17) — 본 P4-3 핵심

```http
POST /v1/gdpr/erasure
{
  "subject_id": "hash...",
  "scope": "all" | "tenant" | "project" | "record",
  "tenant_id": "T-001",
  "project_id": "P-X",
  "record_id": "uuid...",
  "reason": "..."
}

200 OK
{
  "request_id": "ERA-...",
  "status": "pending",
  "erasure_at": "2026-05-27T...",
  "scheduled_hard_delete": "2026-06-27T..."
}
```

처리 흐름:

1. 요청 검증 (DPO 또는 데이터 주체 본인 인증).
2. 대상 레코드에 `erasure_at = NOW()` 설정.
3. 즉시 응답 제한: 새로운 처리에서 해당 레코드 미사용.
4. **1 month 후** 자동 hard delete (cron).
5. 감사 로그는 PII redact 후 12 month 보존.

**LOCK-MR-005/006 호환**: 시스템 보존 LOCK은 별도. GDPR 요청은 데이터 주체 권리 채널.

### 4.4 Right to Restriction of Processing (Art. 18)

```http
POST /v1/gdpr/restrict
{
  "subject_id": "...",
  "restriction_type": "accuracy_dispute" | "unlawful_processing" | "legal_claim" | "objection_pending"
}
```

`restricted_at` 컬럼 설정 → 해당 레코드는 read-only 동결 상태 유지 (저장은 OK, 처리/공유 차단).

### 4.5 Right to Data Portability (Art. 20)

```http
GET /v1/gdpr/export?subject_id={hash}&format=json

200 OK
Content-Disposition: attachment; filename="export-{subject_id}-{date}.json"
{...} (machine-readable, structured, commonly used format)
```

JSON 우선, CSV / XML 옵션. 데이터 주체 자체 다운로드 + 다른 컨트롤러로 직접 전송 (Art. 20(2)).

### 4.6 Right to Object (Art. 21)

```http
POST /v1/gdpr/object
{
  "subject_id": "...",
  "processing_type": "direct_marketing" | "profiling" | "legitimate_interests",
  "reason": "..."
}
```

직접 마케팅(Art. 21(2))은 무조건 정지. 그 외는 compelling legitimate grounds 판단.

---

## 5. 1 month rule + Art. 33 72h 통보

### 5.1 응답 시한

| 권리 | 표준 시한 | 연장 가능 | 비고 |
|------|----------|---------|------|
| Access | 1 month | +2 month | Art. 12(3) |
| Rectification | 1 month | +2 month | |
| Erasure | 1 month | +2 month (drift risk) | hard delete까지 |
| Restriction | 즉시 (1 month 답변) | — | |
| Portability | 1 month | +2 month | |
| Objection | 즉시 (특히 direct marketing) | — | |

### 5.2 Art. 33 72h Breach Notification

개인정보 유출 인지 시 **72 시간 이내** 감독기관(DPA) 통보:

| 단계 | 시한 | 행동 |
|------|------|------|
| T+0 | 인지 시점 | 보안팀 즉시 출동, scope 파악 |
| T+24h | impact assessment | 영향 범위, 카테고리, 데이터 주체 수 |
| T+72h | DPA 통보 | 표준 양식 (Art. 33(3)) 제출 |
| T+72h | 데이터 주체 통보 | high risk 시 (Art. 34) |
| T+30d | 사후 보고서 | DPO 작성 + 이사회 결재 |

자동화: 6-12 LogEvent에서 `severity=CRITICAL` 감지 시 보안 oncall PagerDuty + DPO 자동 알림.

---

## 6. DPIA (Data Protection Impact Assessment)

고위험 처리 항목별 DPIA 사전 실시 (Art. 35):

| 처리 항목 | 위험도 | DPIA 결과 | 대응 |
|----------|-------|----------|------|
| 메모리 L0~L3 저장 | Medium | DPIA-MR-001 | LOCK-MR-015 PII 마스킹, encryption |
| 벡터 인덱스 (BGE-M3) | Medium | DPIA-MR-002 | tenant_id 분리 collection |
| Hybrid Search (LOCK-MR-008) | Low | — | 기본 처리 |
| Dream Mode (P4-4) | Medium | DPIA-MR-004 | offline 처리, 권한 격리 |
| Statistics Dashboard (P4-5) | Low | — | 집계만, PII 제외 |
| Cross-tenant 격리 (P4-2) | High | DPIA-MR-005 | RLS + 3 메커니즘 defense-in-depth |
| GDPR Erasure (본 P4-3) | High | DPIA-MR-006 | DPO 결재 + 1 month rule + audit |

DPIA 결과는 12 month 보존, 매년 갱신.

---

## 7. SOC-2 5 TSC 매핑

| TSC | 본 V3 구현 |
|-----|-----------|
| Security | LOCK-MR-015 Deny, RBAC × 테넌트, RLS, encryption |
| Availability | managed_db_v3 HA, Multi-AZ, RPO 5분 / RTO 60초 |
| Confidentiality | PII 마스킹, tenant_id 격리, in-transit TLS 1.3 |
| Processing Integrity | trace/audit log, hash verify (managed_db_v3 §6.2) |
| Privacy | GDPR 6 권리 API (§4), 1 month rule, DPIA |

### 7.1 감사 로그 12 month 보존

```sql
CREATE TABLE audit_log_soc2 (
    log_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ts            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    tenant_id     TEXT NOT NULL,
    actor_hash    TEXT NOT NULL,       -- PII redact (sha256(actor))
    action        TEXT NOT NULL,       -- save/update/delete/access/erasure/...
    resource_type TEXT NOT NULL,
    resource_id   TEXT,
    severity      TEXT NOT NULL,        -- INFO/WARN/ERROR/CRITICAL
    metadata      JSONB,
    ip_hash       TEXT,                 -- sha256(client_ip || salt)
    user_agent_hash TEXT,
    success       BOOLEAN NOT NULL,
    error_code    TEXT
);

CREATE INDEX idx_audit_ts ON audit_log_soc2 (ts DESC);
CREATE INDEX idx_audit_tenant ON audit_log_soc2 (tenant_id, ts DESC);
CREATE INDEX idx_audit_severity ON audit_log_soc2 (severity) WHERE severity IN ('ERROR', 'CRITICAL');

-- TTL: 12 month (cold archive 후 추가 36 month 콜드 스토리지, 매니지드 별도 트랙)
```

### 7.2 5 TSC 외부 감사 인증 forward-defined

- Type 1 (design): Phase 5 진입 전 .
- Type 2 (operating effectiveness, 6+ month observation): Phase 5+ 별도 트랙.
- 외부 감사인: Big 4 (Deloitte / EY / KPMG / PwC) 또는 동급.
- 매년 갱신.

---

## 8. PII 마스킹 (LOCK-MR-015 + P1-7 cross-ref)

저장 경로 INSERT 시 다음 PII 패턴 자동 마스킹:

| PII 유형 | 패턴 | 마스킹 결과 |
|---------|------|-----------|
| email | regex | `***@***.***` (도메인 보존) |
| 주민등록번호 | regex | `******-*******` |
| 카드번호 | Luhn | `**** **** **** 1234` (뒤 4자리) |
| IP | regex | `xxx.xxx.xxx.0` (마지막 octet 0) |
| 전화번호 | regex | `010-****-****` |
| 좌표 (lat,lon) | regex | 50m 정확도로 fuzz |

LOCK-MR-015 강제: Deny 판정 시 벡터 삽입 절대 금지.

본 V3는 6-2 PII Masking (`pii_masker.md` / `pii_masking.md` M-4 acknowledged) 모듈을 직접 호출합니다. 6-2 산출물 재작성 0건.

---

## 9. 6-2 gdpr_compliance.md 361L direct inheritance EXACT MATCH

6-2 Security-Governance의 `gdpr_compliance.md` (361 LF / 20,905 B / `C922CE10D7224770`)는 본 V3의 정본 소스입니다. 본 P4-3은 그 산출물을 **재작성 없이 inheritance** 합니다.

**불변 사실**: 6-2 P2-3 산출물 cross-domain inheritance 재작성 0건. 본 V3는 6-4 도메인 적용 가이드만 추가하며, GDPR 정책 정의는 6-2에 있습니다.

NTFS 실측 (Stage A end 시점):

- 파일: `D:\VAMOS\docs\sot 2\6-2_Security-Governance\05_advanced-security\gdpr_compliance.md` (또는 P2-3 위치)
- 361 LF / 20,905 B / SHA-16 `C922CE10D7224770`
- 6-2 P2-3 ✅ APPROVED inheritance, 본 P4-3 진입 시점 EXACT MATCH 100% verified.

---

## 10. cross-domain handoff

### 10.1 6-2 Security-Governance

- `gdpr_compliance.md` 361L 직접 inheritance (재작성 0건).
- `pii_masker.md` / `pii_masking.md` LOCK-MR-015 cross-ref.
- RBAC × 테넌트 (multi_tenancy_v3.md §5) 결합.

### 10.2 6-12 Event-Logging

- SOC-2 감사 로그는 6-12 `LogEvent` 표준 사용 (severity / actor_hash / resource).
- 12 month 보존 + cold archive 36 month.
- Art. 33 72h breach notification 자동 트리거.

---

## 11. audit conditions (4건)

| # | 조건 | 측정 | Phase 5 gate |
|---|------|------|-------------|
| A1 | LOCK-MR-005/006 변경 0 (정본 명문 보존) | AUTHORITY_CHAIN grep | ✅ |
| A2 | GDPR 6 권리 API 모두 1 month rule 응답 | API 통합 테스트 | ✅ |
| A3 | Art. 33 72h notification 시뮬레이션 PASS | breach 시뮬레이션 + 알림 | ✅ |
| A4 | SOC-2 감사 로그 12 month 보존 + redaction | audit_log_soc2 SQL 쿼리 | ✅ |

---

## 12. CONFLICT_LOG 신규 RESOLVED 등재 (Stage B 작성)

본 V3 작성 시 CONFLICT_LOG.md에 신규 항목 등재:

```markdown
### #007 — LOCK-MR-005/006 vs GDPR Right to Erasure (Phase 3 핵심 신규 이슈)

| 항목 | 내용 |
|------|------|
| 발견일 | Phase 3 (P3-3, 2026-04~05) |
| 출처 A | LOCK-MR-005: L2 무기한 보존 / LOCK-MR-006: L3 무기한 deprecated 전환 |
| 출처 B | GDPR Art. 17 Right to Erasure (1 month rule) |
| 충돌 유형 | 시스템 보존 LOCK vs 법적 의무 채널 표면적 충돌 |
| 해결 | LOCK 명문 변경 0. V3 적용 확장 메커니즘 (`erasure_at` + 1 month + hard delete) 별도 채널로 분리. LOCK-MR-006에 `<!-- LOCK-MR-006 의 V3 적용 확장 -->` 주석 명시 |
| 영향 | gdpr_soc2_v3.md (본 P4-3) 정의, 6-2 gdpr_compliance.md 361L direct inheritance |
| 상태 | ✅ 해결 (Phase 4 P4-3, 2026-05-27) |
```

---

## 13. Phase 5 entry-gate 매핑 (P4-3)

- G4-1: V3 implementation 완료 — 본 문서 + CONFLICT_LOG 신규 RESOLVED.
- G4-2: Status DRAFT → APPROVED.
- G4-3: LOCK-MR-005/006 변경 0, V3 적용 확장 주석 명시.
- G4-4: CONFLICT_LOG OPEN 0 + 신규 RESOLVED (#007) 등재.
- G4-5: 6 권리 API + 1 month rule + Art. 33 72h.
- G4-6: 6-2 / 6-12 cross-handoff 양방향 EXACT MATCH 100%.
- G4-7: SOC-2 Type 2 인증 Phase 5+ forward-defined.

---

## 14. 외부 표준 매핑

| 표준 | 적용 |
|------|------|
| GDPR (EU 2016/679) | Art. 5 / 12-22 / 33 / 35 |
| CCPA (California) | Right to Know / Delete / Opt-out — 호환 적용 |
| PIPL (China) | 데이터 분류 + cross-border 검토 |
| K-PIPA (Korea) | 개인정보 보호법 — 본 시스템 1차 준수 대상 |
| SOC-2 | TSC 2017 5 categories |
| ISO 27001 | 정보보안 관리 시스템 |
| ISO 27701 | PII 처리 확장 |

---

## 15. 트러블슈팅

### 15.1 erasure 후 GET 시 NotFound가 아닌 stale 캐시 반환

- 원인: semantic_cache 미invalidation.
- 대처: erasure_at 설정 시 cache key prefix 자동 expire.

### 15.2 1 month 자동 hard delete cron 누락

- 원인: cron job 실패 / DAG 단절.
- 대처: 매일 `pending_erasure` 카운트 메트릭 + `> 0 with erasure_at < NOW() - 1 month` 알림.

### 15.3 audit log PII redact 실패

- 원인: 마스킹 모듈 회귀.
- 대처: 매주 audit_log sample → regex PII scan → hit 시 즉시 CRITICAL.

---

## 16. 데이터 분류 및 처리 카테고리

### 16.1 카테고리

| 카테고리 | 예시 | 마스킹 | 보존 |
|---------|------|-------|------|
| 공개 (Public) | 도메인명, 공개 정책 | 불필요 | 무기한 |
| 일반 식별 | tenant_id, project_id | 해시 옵션 | 무기한 (LOCK-MR-005) |
| 식별 정보 (Identifying) | actor, email, name | 마스킹 | erasure on request |
| 민감 정보 (Sensitive — Art. 9) | health, biometric, racial, political | Deny 기본 (LOCK-MR-015) | 저장 금지 원칙 |
| 결제/금융 | 카드번호, 계좌 | tokenization | PCI-DSS 별도 |
| 어린이 (Art. 8) | 16세 미만 | 부모 동의 필수 | 별도 워크플로우 |

### 16.2 처리 활동 등록부 (Records of Processing Activities, Art. 30)

```python
@dataclass
class ProcessingActivity:
    activity_id: str
    name: str
    controller: str         # 데이터 컨트롤러
    processor: str          # 데이터 프로세서
    purposes: List[str]
    legal_basis: str        # consent / contract / legal_obligation / vital_interest / public_task / legitimate_interests
    data_categories: List[str]
    subject_categories: List[str]
    recipients: List[str]
    international_transfer: bool
    transfer_safeguard: Optional[str]
    retention_period: str
    technical_measures: List[str]
    organizational_measures: List[str]
```

분기별 갱신 + DPO 검토 + 감독기관 요청 시 제출.

## 17. 국제 이전 (Cross-border Transfers)

### 17.1 EU → non-adequacy 국가

- Standard Contractual Clauses (SCC) 2021 버전 강제.
- Transfer Impact Assessment (TIA) per Schrems II 요구사항.
- 보충 조치: encryption + pseudonymization + 처리 제한.

### 17.2 Multi-region deployment

- 테넌트별 region 선택 (Phase 5+ Multi-tenancy V3 §15 forward-defined).
- EU 테넌트 → EU 리전 강제.
- US 테넌트 → CCPA + US 리전.
- 한국 테넌트 → K-PIPA + KR 리전.

### 17.3 데이터 매핑 다이어그램

```
[데이터 주체 (EU)]
       │ HTTPS TLS 1.3
       v
[API Gateway (EU region)]
       │ mTLS
       v
[Application Tier (EU region)]
       │ encrypted + RLS
       v
[PostgreSQL Primary (EU region)] ─ replica ─> [Standby (EU AZ-2)]
       │
       v
[Cold Backup (S3 EU)]
```

cross-border 출국 0 by default. 백업도 EU 내에서만.

## 18. 사고 대응 플레이북

### 18.1 Severity 분류

| 등급 | 정의 | 통보 시한 |
|------|------|---------|
| P0 — Critical | 1,000+ 데이터 주체 영향, 민감 정보 유출 | 즉시 + DPO + 이사회 |
| P1 — High | 100+ 영향, 식별 정보 유출 | 1시간 |
| P2 — Medium | 10+ 영향 또는 시스템 우회 시도 | 4시간 |
| P3 — Low | 단일 사용자, 시도 차단 성공 | 24시간 |

### 18.2 P0 대응 절차

1. T+0: oncall PagerDuty, 즉시 격리 (compromised 서비스 차단).
2. T+15min: 보안팀 + DPO + CEO 화상 회의.
3. T+1h: scope 파악 (영향 데이터 주체 수, 카테고리).
4. T+4h: forensics 시작, evidence 보존.
5. T+24h: 영향 평가 보고서 (DPA 통보용 초안).
6. T+72h: DPA 공식 통보 (Art. 33), high risk 시 데이터 주체 통보 (Art. 34).
7. T+30d: post-mortem + remediation plan.
8. T+90d: external 감사 (필요 시).

## 19. DPO (Data Protection Officer) 책무

| 항목 | 책무 |
|------|------|
| 임명 | 회사 임원 또는 외부 위탁, 감독기관 등록 |
| 독립성 | CEO 직보, 처벌 면제 |
| 책무 | DPIA 검토, GDPR 6 권리 처리 결재, breach 통보 결재, DPA 연락 창구 |
| 보고 | 분기별 이사회 보고 + 연간 외부 감사인 회의 |

## 20. 약관/정책 문서

다음 외부 노출 문서가 본 V3 시행 기준 갱신 대상:

| 문서 | 위치 | 갱신 주기 |
|------|------|---------|
| 개인정보처리방침 | /privacy | GDPR 변경 시 |
| 약관 | /terms | 서비스 변경 시 |
| 쿠키 정책 | /cookies | 매년 |
| DPA (Data Processing Agreement) — B2B | /legal/dpa | 계약 별 |
| 데이터 주체 권리 행사 가이드 | /gdpr-rights | DPO 갱신 |

## 21. KPI (Phase 5+ forward-defined)

| KPI | 목표 | 측정 |
|-----|------|------|
| GDPR 요청 처리 시한 | 100% within 1 month | API metrics |
| Breach 통보 시한 | 100% within 72h | incident log |
| DPIA 갱신 주기 | 100% annual | DPIA register |
| 직원 GDPR 교육 이수율 | 100% | LMS |
| Phishing 시뮬레이션 통과율 | > 95% | 보안 캠페인 |
| 외부 감사 finding | 0 high-risk | 감사 보고서 |

## 22. 변경 이력

| 일자 | 변경 | 비고 |
|------|------|------|
| 2026-05-27 | V3 NEW 최초 작성 | Phase 4 P4-3 SPEC Stage B production write — LOCK-MR-005/006 vs GDPR 정식 해소 specialty milestone |
