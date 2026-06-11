# SOT 2 LOCK 일관성 (lock_consistency)

> 생성: 2026-06-05T19:38:52 · MISMATCH=0
>
> ⚠️ **알려진 한계(스캐너 거짓음성 — 오류리스트 2026-06-10 L112, 주석 2026-06-11)**: ① 아래 "도메인별 LOCK ID 수"는 `LOCK-*` 접두 ID만 집계함 — 무접두 L-번호 LOCK 체계를 쓰는 5개 도메인(0-0, 6-1, 6-5, 6-7, 6-8)은 실제 LOCK이 존재함에도 0으로 오보고됨(예: 6-5 AUTHORITY L1~L20, 6-7 L1~L18, 6-8 L1~L22). ② 상단 개념 게이트 표는 미관측값(`{}` — 예: COST_GATE)도 CONSISTENT로 표기되며 SDV 게이트 7개 중 4개는 영구 N/A. MISMATCH=0은 전수 일치 보증이 아니므로 수치 인용 시 각 도메인 AUTHORITY_CHAIN.md를 정본으로 할 것.

| 개념 | 허용값 | 관측값 | 상태 |
|---|---|---|---|
| QOD_L2_BAN | [0.4] | {'0.4': 18} | CONSISTENT |
| HYBRID_ALPHA | [0.3, 0.7] | {'0.7': 44, '0.3': 14} | CONSISTENT |
| HYBRID_BETA | [0.3, 0.7] | {'0.3': 3} | CONSISTENT |
| CONF_HIGH | [0.85] | {'0.85': 63} | CONSISTENT |
| CONF_LOW | [0.3] | {'0.3': 12} | CONSISTENT |
| COST_MONTHLY | [40.0] | {'40.0': 8} | CONSISTENT |
| COST_GATE | [80.0] | {} | CONSISTENT |

## 도메인별 LOCK ID 수 (AUTHORITY_CHAIN)

| 도메인 | LOCK ID 수 | CONFLICT OPEN |
|---|---|---|
| 0-0_Governance-Rules-Meta | 0 | 0 |
| 1-1_Verifier-Reasoning-Engines | 16 | 0 |
| 1-2_Auxiliary-Modules | 16 | 0 |
| 2-1_Blue-Node-Architecture | 19 | 0 |
| 2-2_COND-Modules-Detail | 14 | 0 |
| 3-10_Agent-Protocol-Interoperability | 13 | 0 |
| 3-2_Multimodal-Processing | 12 | 0 |
| 3-3_PKM-Knowledge-Management | 13 | 0 |
| 3-4_Workflow-RPA | 10 | 0 |
| 3-5_Education-Learning | 16 | 0 |
| 3-6_Health-Wellness-EmotionAI | 19 | 0 |
| 3-7_Developer-Tools-API-SDK | 11 | 0 |
| 3-8_Conversation-A2A | 14 | 0 |
| 3-9_Business-Model-Strategy | 10 | 0 |
| 4-1_Rust-Tauri-Infrastructure | 18 | 0 |
| 4-2_CICD-Pipeline | 15 | 0 |
| 4-3_MCP-Server-Client | 13 | 0 |
| 4-4_MLOps-LLMOps | 16 | 0 |
| 5-1_Benchmark-Evaluation | 15 | 0 |
| 5-2_File-Context | 1 | 0 |
| 5-3_v12-Additions-Detail | 12 | 5 |
| 5-4_v23-Extension-Items | 8 | 0 |
| 6-10_EXP-Modules-Detail | 8 | 0 |
| 6-11_Hologram-Main-LLM | 14 | 0 |
| 6-12_Event-Logging | 11 | 0 |
| 6-13_Operations | 14 | 0 |
| 6-1_UI-UX-System | 0 | 0 |
| 6-2_Security-Governance | 1 | 0 |
| 6-3_Agent-Teams-PARL | 20 | 0 |
| 6-4_Memory-RAG-Storage | 19 | 0 |
| 6-5_SDAR-System | 0 | 0 |
| 6-6_Self-Evolution-System | 2 | 0 |
| 6-7_RT-BNP-DCL | 0 | 0 |
| 6-8_Cloud-Library | 0 | 0 |
| 6-9_Brain-Adapter-HAL | 13 | 0 |
| Ai-investing-detail | 1 | 0 |
