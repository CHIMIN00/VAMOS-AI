---
tags: [type/concept, tier/all, module/EVX-series, version/V3, lock/FREEZE]
aliases: [EVX, 검증 체인, EVX1~6, Verify Chain]
created: 2026-06-12
---

# EVX-Series: Verification Chain (EVX-1~EVX-6)

## 정의
검증 체인 모듈 6개 — **전부 V3-only**. CORE 5 + EXP 1(EVX-3). 5-Phase 파이프라인의 Reflection/Verify 단계(I-6 + EVX)에서 동작하며 VerifyChainRegistry(EVX-1~EVX-6)에 등록된다. EVX-7+는 미정의(V2+ Self-evo 확장 시 정의).

| ID | 명칭 | LOCK | status | V1 | V2 | V3 |
|---|---|---|---|---|---|---|
| EVX-1 | Code-as-Policy | false | CORE | OFF | OFF | ON |
| EVX-2 | Adversarial Verifier | **true (LOCK)** | CORE | OFF | OFF | ON |
| EVX-3 | Log-prob Confidence | false | EXP | OFF | OFF | ON |
| EVX-4 | Thought Buffer | false | CORE | OFF | OFF | ON |
| EVX-5 | Gen-Verify-Learn | false | CORE | OFF | OFF | ON |
| EVX-6 | Z3 Solver Routing | false | CORE | OFF | OFF | ON |

## 이 개념이 등장하는 모든 도메인
- [[T6-EXP-Modules]] — EVX-Series 관리 정본(6-10, B/D/EVX)
- [[T1-Verifier-Engines]] — C/D-Series 검증엔진과 체인 결합
- [[T1-Auxiliary-Modules]] — I-6 Self-check Engine과 Reflection/Verify 단계 공동 담당
- [[T6-Self-Evolution]] — EVX-5 Gen-Verify-Learn 자기진화 루프 연계

## 값·수치 (LOCK)
- **EVX-2 Adversarial Verifier = LOCK true** (시리즈 중 유일)
- E-*/EVX-* 구분 (LOCK §7.1): E-*=외부기능, EVX-*=Verify 확장 — E 변형 금지
- EVX-6은 E-6 Z3 Solver로 라우팅 (E-6은 V1부터 ON)

## 버전별 차이
- V1/V2: 전부 OFF / V3: 전부 ON (V3-only 시리즈)

## 원본 참조
- 정의: `D:\VAMOS\docs\sot\D2.0-01_01. VAMOS_DESIGN_2_0_OVERVIEW.md` §5.13 / 참조: `D:\VAMOS\docs\sot 2\6-10_EXP-Modules-Detail\` / `D:\VAMOS\CLAUDE.md` §6·§16
