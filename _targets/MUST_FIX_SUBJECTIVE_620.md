# 주관적 설계선택 620건 — 현황·분포·복원 경로 (세션4, 2026-06-11)

> 결론 먼저: **620건의 항목 리스트는 어떤 산출물에도 실체가 없다.** 존재하는 것은 카운트(도메인별 분포)뿐이다.
> 본 문서가 620건 관련 단일 기준점. `SESSION_HANDOFF.md` §5-2의 구 포인터("MUST_FIX_BACKLOG.json single")는 깨진 안내였음(세션4 정정).

## 1. 실체 부재의 증거 (세션4 전수 추적)

| 추적 위치 | 결과 |
|---|---|
| `MUST_FIX_BACKLOG.json` | totals.subjective_human_review=620 카운트만. 항목 리스트 없음, 'single' 필드 없음 |
| `MUST_FIX_BACKLOG.md` | 요약표의 "주관적 설계선택 → 사람 검토 620" 1행뿐 |
| `_integ/mustfix_result.json` | 36 도메인 각각 `review_subjective_count`만 (합계 620 정확) |
| `_integ/mf_in/*.json` | 판정 입력(confirmed/unconfirmed)만 — 주관 분류 없음 |
| 창1 판정 워크플로 transcript (`3ac8c9bb…\wf_c5fcea74-93d`, 39파일) | StructuredOutput 스키마 자체가 `review_subjective_count`(정수)만 수집 — **항목이 구조화된 적이 없음** |

→ 원인: 판정 단계(w9gt6mb6z)의 출력 스키마 설계가 주관 항목을 개수로만 받았음. 복원이 아니라 **재도출**이 필요.

## 2. 도메인별 분포 (정본 — mustfix_result.json 실측, 합계 620)

| 건수 | 도메인 | 건수 | 도메인 |
|---|---|---|---|
| 89 | Ai-investing-detail | 13 | 6-2_Security-Governance |
| 87 | 2-2_COND-Modules-Detail | 13 | 6-7_RT-BNP-DCL |
| 25 | 3-6_Health-Wellness-EmotionAI | 12 | 3-10_Agent-Protocol-Interop |
| 22 | 3-4_Workflow-RPA | 12 | 4-4_MLOps-LLMOps |
| 22 | 6-3_Agent-Teams-PARL | 12 | 6-9_Brain-Adapter-HAL |
| 19 | 3-7_Developer-Tools-API-SDK | 11 | 3-8_Conversation-A2A |
| 19 | 4-1_Rust-Tauri-Infrastructure | 10 | 3-9_Business-Model-Strategy |
| 19 | 4-2_CICD-Pipeline | 10 | 5-3_v12-Additions-Detail |
| 19 | 6-4_Memory-RAG-Storage | 9 | 6-11_Hologram-Main-LLM |
| 18 | 1-1_Verifier-Reasoning-Engines | 9 | 6-12_Event-Logging |
| 18 | 3-2_Multimodal-Processing | 8 | 2-1_Blue-Node-Architecture |
| 18 | 3-5_Education-Learning | 7 | 0-0_Governance-Rules-Meta |
| 17 | 3-3_PKM-Knowledge-Management | 7 | 5-1_Benchmark-Evaluation |
| 17 | 6-5_SDAR-System | 7 | 6-8_Cloud-Library |
| 15 | 4-3_MCP-Server-Client | 6 | 6-6_Self-Evolution-System |
| 14 | 1-2_Auxiliary-Modules | 3 | 5-4_v23-Extension-Items |
| 14 | 5-2_File-Context | 3 | 6-10_EXP-Modules-Detail |
| 13 | 6-1_UI-UX-System | 3 | 6-13_Operations |

상위 2개(Ai-investing 89 + 2-2 COND 87)가 전체의 28%. 결정 세션은 이 둘부터 묶는 것이 효율적.

## 3. 재도출 경로 3안 (사용자 결정 필요 — 비용 관점)

| 안 | 방법 | 정확도 | 비용 | 권고 |
|---|---|---|---|---|
| **(a) 재판정 재실행** | 동일 입력(`reduced/` CLC + `gpt/GP-A`)으로 36 도메인 판정 워크플로 재실행 — 단, 이번엔 주관 항목을 **전 필드 구조화**(file/defect/choice_options/recommendation)로 수집. 객관 881 재판정 불요(주관만 출력) | 정본급 | 에이전트 ~36 (창1 rate-limit 전례: 배치 5 순차 필요) | ✅ **권고** |
| (b) transcript 산문 발굴 | wf_c5fcea74-93d 39파일에서 에이전트 분석 산문 중 주관 언급 추출 | 불완전·근사 (스키마 미수집이라 산문에 전수 나열됐다는 보장 없음) | 에이전트 ~10 | 보조용만 |
| (c) 역산 | 전체 검토분 − 확정881 − 미확인56 − 오탐284 | **불가** — 오탐 284와 주관 620의 분리 기준이 미기록이라 904 풀에서 분리 불능 | — | ✗ |

> (a) 실행 시점: 사용량 한도 고려해 사용자가 트리거. 실행 절차는 창1 `_integ/wf_mustfix.js` 재사용 + 출력 스키마에 `review_subjective: [{file, defect, options, recommendation}]` 추가.

## 4. 본 문서 이후

(a) 재도출 완료 → 본 문서를 항목 리스트로 대체(v2) → 카테고리 묶음 → §D 결정 세션에 합류.
