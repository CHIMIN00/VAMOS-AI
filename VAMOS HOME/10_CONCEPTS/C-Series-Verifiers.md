---
tags: [type/concept, tier/all, module/C-series, version/V1, lock/FREEZE]
aliases: [C-Series, 검증 모듈, C1~C7, Verifier 확장]
created: 2026-06-12
---

# C-Series: Verifier/Reasoning 확장 (C-1~C-7)

## 정의
Verifier/Reasoning 확장 모듈 7개. CORE 3(C-1~C-3, V1 ON) + EXP 4(C-4~C-7, V3). 논리/수학/코드 검증을 V1부터 제공하고 V3에서 시뮬레이션·베이지안·RL·GNN으로 확장한다.

| ID | 명칭 | status | V1 | V2 | V3 |
|---|---|---|---|---|---|
| C-1 | Logic Verifier | CORE | ON | ON | ON |
| C-2 | Math Verifier | CORE | ON | ON | ON |
| C-3 | Code Verifier | CORE | ON | ON | ON |
| C-4 | Domain Simulator | EXP | OFF | OFF | ON |
| C-5 | Bayesian Belief Engine | EXP | OFF | OFF | ON |
| C-6 | RL Advisor | EXP | OFF | OFF | ON |
| C-7 | GNN Score Model | EXP | OFF | OFF | ON |

## 이 개념이 등장하는 모든 도메인
- [[T1-Verifier-Engines]] — C-1~C-7 검증엔진 정본(1-1, D-1~D-2와 함께)
- [[T6-EXP-Modules]] — EXP 모듈(C-4~C-7) 관리
- [[T1-Auxiliary-Modules]] — I-6 Self-check Engine·I-15 Evidence & QoD Manager와 협업
- [[T5-Benchmark]] — 검증 결과 품질 측정(5-1)

## 값·수치 (LOCK)
- 검증 결과는 SelfCheckGate(PASS/WARN/FAIL)로 수렴 — Self-check 임계값 P0:70 / P1:75 / P2:80 (LOCK), Soft loop 자동 1회만
- Gate 우회 불가 (LOCK): Policy→Approval→Cost→Evidence 필수 통과
- C-Series 자체 수치 LOCK 없음 (활성 게이트는 status/버전 표가 정본)

## 버전별 차이
- V1: C-1~C-3 ON / V2: 동일 / V3: C-4~C-7 추가 전부 ON

## 원본 참조
- `D:\VAMOS\CLAUDE.md` §6 (C-Series 표)·§7.2 / `D:\VAMOS\docs\sot 2\1-1_Verifier-Reasoning-Engines\` / `D:\VAMOS\docs\sot\D2.0-01_01. VAMOS_DESIGN_2_0_OVERVIEW.md`
