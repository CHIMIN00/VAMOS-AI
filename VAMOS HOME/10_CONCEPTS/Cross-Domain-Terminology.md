---
tags: [type/concept, tier/all, status/CORE, version/V1, lock/DEFINED-HERE]
aliases: [용어 충돌, 교차 도메인 용어, GLOSSARY]
created: 2026-06-12
---

# Cross-Domain Terminology (교차 도메인 용어 15개)

## 정의
동일 용어가 도메인별로 다른 의미를 갖는 15건의 충돌 레지스트리(충돌 7 + 5-2 참조 5 + Phase 11 신규 3). 코드/설정은 `prefix_term` 형식(예: `aux_qod`, `ml_qod`)으로 구분하며, 신규 LOCK/FREEZE 정의 시 본 레지스트리 충돌 확인 필수.

## 15개 전사 (CLAUDE.md §23)
| # | 용어 | 구분 |
|---|------|------|
| 1 | QoD | AUX-QoD(1-2, 검색품질 5-factor) vs ML-QoD(4-4, LLM출력) — 둘 다 0.0~1.0 |
| 2 | Gate | QA-Gate(4-4) vs EVAL-Gate(AINV 퀀트 5단계) vs PHASE-Gate(단계 전환) |
| 3 | Pipeline | CICD(4-2) vs IO(3-2) vs MODEL(4-4) |
| 4 | Agent | Agent-Team(6-3, 협업) vs Agent-Service(3-8, 등록/발견) |
| 5 | Discovery | Service-Discovery(3-8) vs Anomaly-Detection(AINV data-quality) |
| 6 | Score | Alpha-Score(0~1) vs Div-Score(0~100) vs Task-Quality(5-1, 1~5) vs Response-Quality(4-4, 0.0~1.0) |
| 7 | Breaking | Breaking-Change(3-7 API) vs BreakingNews(6-7 RT-BNP) |
| 8 | Context Rot | 5-2 정본 — 입력 길이 증가에 따른 LLM 성능 저하 (6-4 소비) |
| 9 | Lost-in-the-Middle | 5-2 정본 — 중간 위치 정보 정확도 30%+ 하락 (5-1 측정) |
| 10 | Ms-PoE | 5-2 정본 — 다중 스케일 위치 인코딩 (V2) |
| 11 | NoLiMa | 5-2 정본 — 컨텍스트 중간 삽입 공격 |
| 12 | Agentic RAG | 5-2 정본, 6-4/6-3 소비 — Self-RAG/CRAG 기반 V2 |
| 13 | 5-Gate | VAMOS-5-Gate(0-0 정본) vs SDAR-Gate(6-5) vs CL-Gate(6-8) — 단독 사용 시 VAMOS-5-Gate |
| 14 | Autonomy Level | 정본 L0~L4(3-10) / 운영 L0~L3(6-2) / 확장 L0~L4+NEVER(6-5) |
| 15 | Alpha 표기 | 정본 alpha=BM25 가중치=0.3(LOCK-AX-06) — 6-4의 α=0.7은 Dense 관점 동일 값 |

## 등장 도메인 / 원본 참조
- [[T0-Governance]] — GLOSSARY 정본 소유 / [[T5-File-Context]] — #8~#12 정본 / [[T6-Memory-RAG]]·[[T5-Benchmark]]·[[T4-MLOps]] — 주요 소비처
- LOCK-BM 충돌 해결: 5-1은 LOCK-BE-01~15 (LOCK-BM은 3-9 전용)
- `D:\VAMOS\CLAUDE.md` §23 / `D:\VAMOS\docs\sot 2\0-0_Governance-Rules-Meta\GLOSSARY_CROSS_DOMAIN.md`
