---
title: Dream Mode V3 (오프라인 정리 + L4 Archive V2+ 확장)
domain: 6-4_Memory-RAG-Storage
phase: 4
task: P4-4
status: APPROVED
version: V3
created: 2026-05-27
session: phase4_6-4_p4-4_2026-05-27
authority_chain:
  - RULE 1.3
  - DESIGN 2.0 / D2.0-06
  - Part2 V1-Phase 2
  - LOCK-MR-001 (4계층 정본 보존)
  - LOCK-MR-005 (L2 무기한)
  - LOCK-MR-006 (L3 deprecated 전환 메커니즘)
  - CONFLICT_LOG #004 (L4 Archive V2+ 확장)
cross_handoff:
  - 6-6_Self-Evolution-System (S-7 Evolution Scheduler 오프라인 분석)
  - 6-5_SDAR-System (메모리 자가 진단 Dream Mode result input)
---

# Dream Mode V3 — 오프라인 정리 + L4 Archive V2+ 확장

> **Phase 4 Task P4-4**: 시스템 idle 시간에 자동 메모리 정리 (B-3 Decay + promotion/demotion + 충돌 해소 + L2→L4 Archive + 콜드 스토리지 + index 재계산).
> **L4 Archive는 정본 4계층 외 V2+ 확장**: CONFLICT_LOG #004 V2+ 범위 확정 + Dream Mode 활용 명시.
> **🎯 P2-4 promotion_automation.md + P2-5 memory_conflict_resolution.md main beneficiary trigger**.

---

## 1. 배경 및 동기

V1/V2 단계에서 메모리 정리는 다음 한계를 가졌습니다:

1. **실시간 처리만**: 메모리 promotion/demotion이 사용자 활성 시간에 발생 → 사용자 응답 지연.
2. **B-3 Decay 누락**: 백그라운드 자동 감쇠 부재.
3. **L4 Archive 부재**: 비활성 L2 데이터 콜드 스토리지로 분리 못함 → 핫 DB 비용 증가.
4. **메모리 충돌 누적**: P2-5 memory_conflict_resolution.md 정의된 충돌 해소가 자동 실행 안 됨.
5. **인덱스/통계 stale**: 벡터 인덱스 stale, 통계 dashboard (P4-5) 데이터 갱신 지연.

**Dream Mode V3**는 시스템 idle 시간에 다음 6단계 정리 작업을 자동 실행합니다.

---

## 2. LOCK 인용 매트릭스 (3 LOCK)

| # | LOCK ID | 정본 출처 | V3 적용 | 재정의 |
|---|---------|----------|---------|-------|
| 1 | LOCK-MR-001 | D2.0-06 §2 | 4계층 정본 (L0~L3) 보존. L4 Archive는 V2+ 확장 (CONFLICT #004) | ❌ |
| 2 | LOCK-MR-005 | D2.0-06 §2.1 | L2 무기한 보존. Dream Mode가 L4 Archive로 이동 시 시스템 보존 LOCK은 유지 (참조 가능) | ❌ |
| 3 | LOCK-MR-006 | D2.0-06 §2.1 | L3 deprecated 전환 메커니즘은 Dream Mode가 비활성 L3 자동 detect → deprecated 후보 추천 (실 전환은 LOCK-MR-016 ApprovalGate 통과 필수) | ❌ |

---

## 3. 트리거 3종

Dream Mode는 다음 3가지 트리거 중 어느 하나라도 충족 시 시작:

| 트리거 | 조건 | 우선순위 |
|--------|------|---------|
| Idle | CPU 부하 < 20% 연속 10분 + 활성 사용자 0 | 1 (가장 즉시) |
| Scheduled | 일일 03:00 KST (asia/seoul) | 2 (정기) |
| Manual | tenant_admin API 호출 | 3 (운영자) |

```python
def should_start_dream_mode() -> Optional[str]:
    if _is_idle(cpu_threshold=0.20, active_users=0, duration_min=10):
        return "idle"
    if _is_scheduled_time(tz="Asia/Seoul", hour=3):
        return "scheduled"
    if _is_manual_request():
        return "manual"
    return None
```

여러 트리거 동시 충족 시 단일 실행 (lock 메커니즘으로 중복 방지).

---

## 4. 정리 작업 6단계

| 단계 | 작업 | 평균 시간 | LOCK |
|------|------|---------|------|
| 1 | B-3 Decay (B-3 → L2 자연 감쇠) | 5-10분 | LOCK-MR-002 |
| 2 | 자동 promotion/demotion (L0↔L1, L1↔L2 후보 detect → 실 전환은 ApprovalGate) | 10-20분 | LOCK-MR-016 |
| 3 | 메모리 충돌 해소 (P2-5 memory_conflict_resolution 알고리즘) | 10-30분 | — |
| 4 | L2 → L4 Archive (90일 이상 미사용 L2 → 콜드) | 30-60분 | CONFLICT #004 |
| 5 | 콜드 스토리지 동기화 (S3 Standard-IA → Glacier) | 30분-2시간 | — |
| 6 | 인덱스/통계 재계산 (벡터 인덱스 vacuum, 통계 dashboard 갱신) | 20-40분 | LOCK-MR-013 |

총 평균 시간: 90분 ~ 4시간. idle 트리거의 경우 활성 사용자 등장 시 단계 경계에서 우아하게 중단.

### 4.1 B-3 Decay (단계 1)

B-3 (감쇠 후보) 레이어의 레코드를 시간 가중치로 감쇠:

```python
def b3_decay():
    decay_lambda = 0.05  # 일별 감쇠율
    candidates = query("memory_records", filter={"b_series": 3})
    for rec in candidates:
        age_days = (now() - rec["created_at"]).days
        new_score = rec["importance"] * exp(-decay_lambda * age_days)
        if new_score < THRESHOLD_DEMOTE:
            mark_demote(rec, target_layer=2)  # L2로 demote 후보
        else:
            update("memory_records", rec["project_id"], rec["record_id"], {"importance": new_score})
```

### 4.2 자동 promotion/demotion (단계 2)

P2-4 `promotion_automation.md` (M-3 acknowledged forward-defined SPEC inheritance)의 규칙:

| 이벤트 | 액션 |
|--------|------|
| L0 record 사용 빈도 ≥ 5회/24h | L1 promotion 후보 (ApprovalGate) |
| L1 record 사용 빈도 < 1회/30일 + 90일 경과 | L2 demotion 후보 (자동, importance ≥ MEDIUM 시) |
| L1 record 사용 빈도 ≥ 10회/30일 | L2 promotion 후보 (ApprovalGate) |
| L2 record 사용 빈도 < 1회/90일 + 1년 경과 | L4 Archive 후보 (이번 단계 4) |

**모든 promotion은 LOCK-MR-016 ApprovalGate를 통과해야 합니다** (자동 강등은 허용).

### 4.3 메모리 충돌 해소 (단계 3)

P2-5 `memory_conflict_resolution.md` (M-3 acknowledged) 알고리즘:

| 충돌 유형 | 해소 |
|---------|------|
| 동일 사실 다른 값 (contradiction) | 최신 + 빈도 + reliability 가중 |
| 시간 의존 사실 stale | timestamp 비교, 최신 유지 |
| 중복 (duplicate) | content hash 동일 시 하나 유지 |
| 권한 변경 (LOCK-MR-015 Deny 신규) | Deny 적용, 기존 레코드 deprecated |

해소 결과는 모두 audit log emit (SOC-2).

### 4.4 L2 → L4 Archive (단계 4)

**CONFLICT_LOG #004 V2+ 확장**: L4 Archive는 정본 4계층(L0~L3) 외 V2+ 확장 기능. Dream Mode가 활용:

```python
def l2_to_l4_archive():
    cold_candidates = query("memory_records", filter={
        "scope": "L2",
        "last_accessed_at": {"<": now() - timedelta(days=365)},
    })
    for rec in cold_candidates:
        # L4 Archive로 이동 (별도 테이블)
        archive_record = compress_zstd(rec)
        insert("memory_archive_l4", archive_record)
        # 원본 L2는 LOCK-MR-005 무기한 보존 → 참조 포인터만 유지
        update("memory_records", rec["project_id"], rec["record_id"], {
            "archived_at": now(),
            "archive_id": archive_record["archive_id"],
        })
```

**불변 사실**: L2 원본은 LOCK-MR-005 무기한 보존. L4는 압축본 + 참조. erasure 요청 시 양쪽 동시 삭제.

### 4.5 콜드 스토리지 동기화 (단계 5)

| 단계 | 매체 | 액세스 시간 | 비용 (월/GB) |
|------|------|----------|---------|
| Hot (L0~L2 active) | RDBMS + Qdrant | ms | $0.10 |
| Warm (L4 recent) | S3 Standard | 100ms | $0.023 |
| Cold (L4 oldest) | S3 Standard-IA | seconds | $0.0125 |
| Glacier (L4 1년+) | S3 Glacier Deep Archive | 12-48h | $0.00099 |

자동 lifecycle policy (AWS):

```json
{
  "Rules": [
    { "Id": "L4-IA", "Status": "Enabled", "Transitions": [{"Days": 90, "StorageClass": "STANDARD_IA"}]},
    { "Id": "L4-Glacier", "Status": "Enabled", "Transitions": [{"Days": 365, "StorageClass": "DEEP_ARCHIVE"}]},
    { "Id": "L4-Erasure", "Status": "Enabled", "Expiration": {"Days": 32} } // GDPR erasure tagged (1 month 유예 + buffer)
  ]
}
```

### 4.6 인덱스/통계 재계산 (단계 6)

- Qdrant collection optimize (`POST /collections/{name}/index`).
- pgvector VACUUM ANALYZE.
- statistics_dashboard_v3 (P4-5) 7+ 메트릭 일일 집계 갱신.
- semantic_cache hit rate 통계.

---

## 5. cross-domain handoff

### 5.1 6-6 Self-Evolution-System (S-7 Evolution Scheduler)

- 6-6의 S-7 Evolution Scheduler는 Dream Mode와 동시에 (또는 직후) 시스템 자가 진화 분석을 실행할 수 있는 trigger 권한 보유 (forward-defined).
- 본 Dream Mode 종료 시 6-6 S-7로 result summary emit.

### 5.2 6-5 SDAR-System (메모리 자가 진단)

- Dream Mode result는 6-5 SDAR (Self-Diagnostic Auto-Repair) 시스템의 input.
- 6-5는 dream_mode_result를 기반으로 메모리 무결성 진단 → 이상 시 자가 수리.

---

## 6. audit conditions (3건)

| # | 조건 | 측정 | Phase 5 gate |
|---|------|------|-------------|
| A1 | 트리거 3종 정확성 (idle/scheduled/manual) | 시뮬레이션 + 메트릭 | ✅ |
| A2 | 6단계 모두 idempotent + 우아한 중단 | 중단/재시작 테스트 | ✅ |
| A3 | L4 Archive 압축률 ≥ 5x (ZSTD level 9) | sample dataset | ✅ |

---

## 7. Phase 5 entry-gate 매핑 (P4-4)

- G4-1: V3 implementation 완료 — 본 문서.
- G4-2: Status DRAFT → APPROVED.
- G4-3: LOCK-MR-001/005/006 변경 0.
- G4-4: CONFLICT #004 V2+ 범위 확정 갱신 (Dream Mode 활용 명시).
- G4-5: 6단계 정리 작업 staging 7일 측정 데이터.
- G4-6: 6-5 / 6-6 cross-handoff forward-defined.
- G4-7: Phase 5+ Dream Mode 콜드 스토리지 S3/Glacier 통합 별도 트랙.

---

## 8. 운영 가이드

### 8.1 메트릭 (statistics_dashboard_v3 연동)

| 메트릭 | 단위 | 알림 |
|--------|------|------|
| `dream_mode_runs_total` | counter | — |
| `dream_mode_duration_seconds` | histogram | p95 > 4h |
| `dream_mode_b3_decayed_count` | counter | — |
| `dream_mode_promoted_count{from,to}` | counter | — |
| `dream_mode_conflicts_resolved_count` | counter | — |
| `dream_mode_archived_count` | counter | — |
| `dream_mode_aborted_total{reason}` | counter | reason=active_user → INFO, error → WARN |
| `dream_mode_index_rebuild_seconds` | histogram | p95 > 2h |

### 8.2 트러블슈팅

- **Dream Mode 시작되지 않음**: cron + idle detection 모두 확인. `dream_mode_runs_total` flat 시 alert.
- **Dream Mode 너무 자주 시작**: lock 누락. instance lease + heartbeat 점검.
- **L4 Archive 압축률 낮음**: ZSTD level 점검, 데이터 entropy 분석.
- **인덱스 재계산 timeout**: vacuum 분할 처리, off-peak window 확대.

### 8.3 운영 권장

| 사항 | 권장 |
|------|------|
| 실행 윈도우 | 02:00-06:00 KST |
| max 동시 instance | 1 (lock) |
| concurrent 트랜잭션 | < 4 |
| 중단 가능성 | 활성 사용자 등장 시 즉시 |
| 백업 시점 | Dream Mode 직후 |

---

## 9. 안전 메커니즘

### 9.1 transaction boundary

- 6단계 각각이 단일 transaction이 아닌, sub-batch 단위 transaction.
- 단계 중간 fail 시 그 sub-batch까지만 rollback, 다음 단계는 안전하게 시작.
- LOCK-MR-019 (루프 저장 폭주 방지) 강제: sub-batch 크기 제한.

### 9.2 GDPR / Erasure 호환

- erasure_at 설정된 레코드는 단계 4 L4 Archive 대상에서 제외.
- 대신 단계 4에서 `erasure_at < NOW() - 1 month` 인 레코드 hard delete (P4-3 §4.3 흐름).
- 단계 6 인덱스 재계산은 hard delete 이후 실행 → stale 인덱스 제거.

### 9.3 cross-tenant 격리 (P4-2 정합)

- Dream Mode는 tenant_id 별 separate pipeline.
- 한 테넌트의 Dream Mode job 실패가 다른 테넌트에 영향 0.
- 자원 budget per tenant 적용 (LOCK-MR-019).

### 9.4 audit trail

```json
{
  "ts": "2026-05-27T03:00:00+09:00",
  "actor": "system:dream_mode",
  "action": "dream_mode_run",
  "trigger": "scheduled",
  "tenants_processed": ["T-001", "T-002", ...],
  "summary": {
    "b3_decayed": 1234,
    "promoted": 56,
    "demoted": 78,
    "conflicts_resolved": 12,
    "archived": 345,
    "index_rebuild_seconds": 1230
  },
  "duration_seconds": 4567,
  "outcome": "completed"
}
```

매 실행 audit_log_soc2 emit, 12 month 보존.

## 10. CONFLICT_LOG #004 V2+ 범위 확정 (Dream Mode 활용 명시)

본 V3는 CONFLICT_LOG.md `#004 — STEP7-D L4 Archive vs D2.0-06 L3 Procedural`을 다음과 같이 갱신합니다 (Stage B):

> **갱신 내용 (2026-05-27)**: V2+ 확장 L4 Archive 기능은 본 dream_mode_v3.md (Phase 4 P4-4) §4.4에서 정식 활용된다. 정본 4계층(L0~L3) LOCK은 변경 없이 유지. L4 Archive는 압축본 + 참조 포인터 형태로만 동작하며, L2 원본 LOCK-MR-005 무기한 보존을 침해하지 않는다.

LOCK-MR-001 4계층 정본 재정의 0건 보장.

## 11. 향후 확장 (Phase 5+ forward-defined)

### 11.1 Dream Mode + ML 기반 importance scoring

- 현재: 빈도 + 시간 기반 heuristic.
- Phase 5+: ML 모델 (사용자 행동 학습) → importance score 자동 산출.
- 학습 데이터: user feedback, 검색 클릭, dwell time.

### 11.2 Dream Mode + Knowledge Graph 통합

- 6-4 L18 KG Engine 정합 시 Dream Mode가 KG 노드/엣지 정리 동시 수행.
- 5-2 W6 KG Extraction OFF default 보존 (CF-V2-003 RESOLVED-INLINE).

### 11.3 multi-region Dream Mode

- 리전별 separate schedule (UTC 시간대 분산).
- cross-region sync는 별도 트랙 (Aurora Global / Cloud Spanner).

### 11.4 Dream Mode SLO

| 지표 | Phase 5+ 목표 |
|------|-------------|
| 일일 실행 성공률 | ≥ 99% |
| 4시간 윈도우 내 완료 | ≥ 95% |
| L4 압축률 | ≥ 5x |
| GDPR erasure 1 month 준수 | 100% |

## 12. 외부 참조

### 12.1 학술/업계 참조

- Sleep consolidation 이론 (Stickgold 2005): human memory consolidation during sleep — Dream Mode 이름의 영감.
- Database vacuum / compaction 표준 패턴 (PostgreSQL VACUUM, MySQL OPTIMIZE TABLE).
- AWS Lifecycle Policy / Google Cloud Storage Object Lifecycle Management.
- ZSTD compression algorithm (Yann Collet, Facebook) — Archive 압축 표준.

### 12.2 관련 RFC / 표준

- RFC 8878 (Zstandard Compression).
- AWS S3 Storage Classes 문서.
- ISO 27001 §A.18 백업 및 아카이브.

## 13. FAQ

**Q1**: Dream Mode 실행 중 사용자 요청이 들어오면?
A: 단계 경계에서 우아하게 중단. 진행 중인 sub-batch는 완료 후 종료. 다음 트리거 시 잔여 작업 재개.

**Q2**: 다중 인스턴스 환경에서 Dream Mode 중복 실행은?
A: distributed lock (Redis SETNX / PostgreSQL advisory lock)으로 단일 인스턴스만 실행.

**Q3**: L4 Archive에서 데이터 복원 시간은?
A: S3 Standard-IA ~100ms / Standard ~ms / Glacier Deep Archive 12-48h. 응답 시한이 중요한 경우 별도 사전 warmup API 제공.

**Q4**: Dream Mode가 GDPR 1 month 응답 시한과 충돌하지 않나?
A: 충돌 없음. GDPR erasure는 별도 채널 (P4-3 §4.3), Dream Mode는 단지 자동화 보조. 1 month 시한은 cron으로 별도 보장.

## 14. 변경 이력

| 일자 | 변경 | 비고 |
|------|------|------|
| 2026-05-27 | V3 NEW 최초 작성 | Phase 4 P4-4 SPEC Stage B production write — L4 Archive V2+ 확장 + Dream Mode 활용 명시 |
