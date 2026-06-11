---
tags: [type/concept, tier/all, version/V1, lock/FREEZE]
aliases: [Decision Lock, 결정 잠금, locked=true]
created: 2026-06-11
---

# Decision Lock

## 정의
"한 시점 / 한 컨텍스트 / 한 결론" 원칙(LOCK). I-5 Condition & Decision Engine이 S3_DECISION_LOCKED에서 `locked=true`를 설정하면 **S3 이후 결정 변경 불가**. Decision 스키마는 18필드 FREEZE.

## 이 개념이 등장하는 모든 도메인
- [[T1-Auxiliary-Modules]] — I-5 Decision Engine(CORE LOCK) 정본
- [[T0-Governance]] — Decision Lock 원칙·FREEZE 관리
- [[T2-Blue-Node]] — routing{blue_node_id, execution_mode} 소비
- [[T4-Rust-Tauri]] — vamos:decision IPC 커맨드(API 15개)
- [[T6-Event-Logging]] — decision_id/trace_id 감사 추적

## 값·수치 (LOCK)
- Decision 18필드(FREEZE): decision_id, trace_id, timestamp, intent_frame_ref, evidence_pack_ref, policy_gate, approval_required, approval_status, cost_gate, routing{}, memory_plan{}, output_spec{}, conclusion, locked=True, optional_signals[], verify{}, gates{}, s_module_hints{}
- conclusion enum: ACCEPT | REJECT | HOLD | ESCALATE
- approval_status enum 4종(D7 SOT): approved/denied/pending/expired (V1-004)
- 상태 머신: S3_DECISION_LOCKED 타임아웃 120s / config: core.single_decision_lock=true(LOCK)

## 버전별 차이
- V1~V3 공통 불변 — 스키마는 V0 진입 시 v3.0.0 통일 승격(CC-001)

## 원본 참조
- `D:\VAMOS\CLAUDE.md` §7.2·§12 / `D:\VAMOS\docs\sot\D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md` / D2.1-D2 스키마
