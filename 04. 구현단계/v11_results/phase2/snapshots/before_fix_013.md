# Before Fix 013 — FG-H01: FIX-09 Gate 명칭 전파 + B-시리즈 매핑
# Snapshot at: 2026-03-13

## L4036-4037 (LOCK 테이블 내 구명칭)
```
| 11 | Trust Score 최소 | 40/100 | §16.11 (CL-G1과 일치) |
| 12 | Relevance Score 최소 | 50/100 | §16.12 (CL-G2와 일치) |
```

## L4088-4089 (Fast Gate 테이블 내 구명칭)
```
| CL-G1 (Trust) | 간소화 | T1/T2 사전 등록 소스는 자동 통과 |
| CL-G2 (Relevance) | 스킵 | 속보는 키워드 매칭이 아닌 Impact 기준 |
```

## L1596-1599 (B↔L 매핑 테이블)
```
| B-1 Episodic | 사건/대화 기록 | L1 (Project) | 프로젝트 컨텍스트 |
| B-2 Procedural | 절차/템플릿 | L3 (Procedural) | 전역/프로젝트 절차 |
| B-3 Semantic | 정리된 사실/지식 | L2 (Long-term) | 전역 검색 기반 |
| B-4 Working | 세션 컨텍스트 | L0 (Session) | 단일 세션 휘발 |
```
