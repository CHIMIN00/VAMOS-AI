# 04. D-Series — 생성 모듈 (Generation)

> **도메인**: 6-10_EXP-Modules-Detail
> **서브폴더**: 04_d-series
> **정본 출처**: D2.0-01 §5.12 (Long Horizon/Personality/Parallel/GraphRAG 정본)
> **모듈 수**: 4 (D-3 ~ D-6)
> **상태**: Phase 0 — 인터페이스 정의

---

## 1. 개요

D-시리즈는 VAMOS의 생성 역량을 담당하는 모듈 그룹이다. 장기 계획(D-3), 페르소나(D-4), 병렬 생성(D-5), GraphRAG(D-6)으로 구성된다.

> **참고**: D-1(World Model/Imagination)과 D-2(MCTS)는 1-1_Verifier-Reasoning에서 관리. 본 서브폴더는 D-3~D-6만 수록.

---

## 2. 모듈 요약

| ID | 모듈명 | Input 타입 | Output 타입 | 핵심 알고리즘 | 패키지 |
|----|--------|-----------|-----------|-------------|--------|
| D-3 | Long Horizon Planner | PlanRequest | Plan | HTN + MCTS 최적 경로 탐색 | — |
| D-4 | Personality Engine | PersonalityConfig | PersonalityState | Big Five 기반 프롬프트 동적 생성 | — |
| D-5 | Parallel Generator | ParallelGenRequest | ParallelGenResult | Best-of-N 병렬 생성 + 합성 | — |
| D-6 | GraphRAG | GraphRAGQuery | GraphRAGResult | KG 서브그래프 + 벡터 검색 + LLM 합성 | neo4j, networkx |

---

## 3. 의존성 관계

```
I-5 (Decision) ──→ D-3 (Long Horizon) ──→ D-5 (Parallel Gen)
                                               │
I-1 (Intent) ──→ D-4 (Personality)             └──→ Brain Adapter (6-9)

I-24 (KG Engine, 1-2) ──→ D-6 (GraphRAG) ──→ I-2 (RAG)
```

---

## 4. V3-004 벤치마크 요구사항

| 항목 | 기준 |
|------|------|
| **대상 모듈** | D-6 GraphRAG |
| **벤치마크 ID** | V3-004 |
| **정확도 목표** | ≥ 90% (LOCK-610-8) |
| **평가 방법** | 정확도/재현율/F1 + 사전 준비된 평가 데이터셋 |
| **사전 해결** | Part2 V3-Phase 2 "V3-004: GraphRAG 90% 벤치마크 미정의" — 벤치마크 기준 및 평가 파이프라인 ADD 필요 |

---

## 5. L3 상태 요약

| 모듈 | L3 시트 | Input/Output | 알고리즘 | 에러 처리 | 테스트 기준 | 비고 |
|------|---------|:----------:|:-------:|:--------:|:---------:|------|
| D-3 | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| D-4 | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| D-5 | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| D-6 | ✅ | ✅ | ✅ | ✅ | PARTIAL | V3-004 벤치마크 (미정의 — §4 ADD 필요) |

> 상세 L3 시트는 상위 카탈로그 문서 §2 참조
