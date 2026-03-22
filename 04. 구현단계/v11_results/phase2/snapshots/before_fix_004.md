# Before Fix 004 — FG-B04: S3 타임아웃 vs 승인 타임아웃 충돌
# Snapshot at: 2026-03-12
# Decision: B (S3a_APPROVE_WAIT 하위 상태 분리)

## L1509-1521 (§3 V1 상태 머신)
```
S0_RECEIVED → S1_INTENT_PARSED (I-1)
  → S2_EVIDENCE_READY (I-2, I-19)
  → S3_DECISION_LOCKED (I-5)
  → S4_EXECUTING (BLUE NODE/TOOLS via I-11)
  → S5_OUTPUT_READY (I-4)
  → S6_SELF_CHECKED (I-6)
  → S7_MEMORY_COMMITTED (I-3 + 06/07)
  → S8_DONE

> **타임아웃 (D2.0-02 §2.2)**: S1=5s, S2=30s, S3=120s, S4=10s, S5=15s
> **LOCK**: 상태 전이 순서 변경 불가. S3 이후 Decision locked=true.
```

## L1554 (§3 V1 완료 검증 #10)
```
| 10 | 상태 타임아웃 | S1=5s, S2=30s, S3=120s, S4=10s, S5=15s 타임아웃 동작 확인 | ✅ |
```
