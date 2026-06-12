---
tags: [type/concept, tier/all, module/D-series, version/V1, lock/FREEZE]
aliases: [D-Series, Brain 확장, D1~D6]
created: 2026-06-12
---

# D-Series: Brain/Planner/RAG 확장 (D-1~D-6)

## 정의
Brain/Planner/RAG 확장 모듈 6개. CORE 2(D-1·D-2, V1 ON) + EXP 4(D-3~D-6, V3). 사고 엔진·멀티모달부터 장기 계획·GraphRAG까지 추론 두뇌를 확장한다.

| ID | 명칭 | status | V1 | V2 | V3 |
|---|---|---|---|---|---|
| D-1 | Think Engine | CORE | ON | ON | ON |
| D-2 | Multimodal Engine | CORE | ON | ON | ON |
| D-3 | Long Horizon Planner | EXP | OFF | OFF | ON |
| D-4 | Personality/Tone Engine | EXP | OFF | OFF | ON |
| D-5 | General Brain (Parallel) | EXP | OFF | OFF | ON |
| D-6 | GraphRAG / Hybrid RAG | EXP | OFF | OFF | ON |

## 이 개념이 등장하는 모든 도메인
- [[T1-Verifier-Engines]] — D-1~D-2 검증엔진 정본(1-1, C-Series와 함께)
- [[T6-Memory-RAG]] — D-6 GraphRAG/Hybrid RAG 실행(6-4), 5-Phase Memory/Store 단계(I-3 + D6)
- [[T3-Multimodal]] — D-2 Multimodal Engine 미디어 처리 연계
- [[T6-EXP-Modules]] — EXP 모듈(D-3~D-6) 관리

## 값·수치 (LOCK)
- DEC-004 GraphRAG (LOCK): 하이브리드 RAG — V1=Basic 64%+, V2=Hybrid+Rerank 83%+, V3=Self-RAG+Graph 90%+ (D-6 직결, [[RAG-Pipeline]])
- Graph 백엔드: V1=JSON(NetworkX) → V2=Neo4j Community → V3=Neo4j Aura (V2-006)
- V3-004(LOW): GraphRAG 90% 목표 벤치마크 기준/측정 방법 미정의 — 미해소 이슈

## 버전별 차이
- V1: D-1·D-2 ON / V2: 동일 / V3: D-3~D-6 추가 전부 ON

## 원본 참조
- `D:\VAMOS\CLAUDE.md` §6 (D-Series 표)·§7.4 / `D:\VAMOS\docs\sot 2\1-1_Verifier-Reasoning-Engines\` / `D:\VAMOS\docs\sot 2\6-10_EXP-Modules-Detail\`
