---
tags: [type/concept, tier/all, version/V1, lock/ABSOLUTE]
aliases: [설정 프레임워크, config.toml, LOCK 20키]
created: 2026-06-12
---

# VAMOS Configuration Framework (TOML + ENV)

## 정의
VAMOS 설정 체계: 포맷은 **config.toml**(PHASE_B4 정본, V0-005), 적용 우선순위는 **ENV > config.toml > default**(LOCK). config.v1.toml에는 변경 불가 LOCK 키 **20개**가 배치된다(D13: PHASE_B4 §3 LOCK 표기 10 ∪ BASE-1.3/DESIGN 2.0 LOCK 12, 중복 2 제외).

## 이 개념이 등장하는 모든 도메인
- [[T0-Governance]] — LOCK 값·비용 상한 정본
- [[T4-Rust-Tauri]] — config 로딩·`vamos:config:*` IPC
- [[T6-Operations]] — 런타임 설정 운영(warn_threshold 조정은 ADMIN 승인 경로 한정)
- [[Cost-Limits]] — cost.* ABSOLUTE LOCK 키 연결

## 값·수치 (LOCK 20키 — CLAUDE.md §20)
- core.single_decision_lock=true / embedding.model=bge-m3 / embedding.dimension=1024
- vector_db.backend=chroma (V1) / graph_db.backend=json_file (V1)
- cost.daily_limit=1300, cost.monthly_limit=40000 (**ABSOLUTE**) / cost.warn_threshold=80, cost.block_threshold=100
- semantic_cache.similarity_threshold=0.95 / logging.trace_id_required=true / mcp.transport=streamable_http
- self_check.threshold_p0/p1/p2=70/75/80, soft_loop_max=1
- approval.timeout_s=600, approval.p2_timeout_s=300
- blue_nodes.active_node_cap=3 (V1) / ui.min_width=1280 (V1)

## 버전별 차이
- V1: 위 20키 고정 / V2+: backend 키 전환(qdrant·postgres 등)은 버전 게이트 통과 시에만 — LOCK 값 자체 변경 불가

## 원본 참조
- `D:\VAMOS\CLAUDE.md` §7.4/§20 / `D:\VAMOS\docs\sot\PHASE_B4_CONFIG_SPEC` (§3/§5.2) / `D:\VAMOS\_targets\DECISION_REGISTER.md` (D13)
