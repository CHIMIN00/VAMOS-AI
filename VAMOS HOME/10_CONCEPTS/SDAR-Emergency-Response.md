---
tags: [type/concept, tier/T6, version/V3, lock/ABSOLUTE]
aliases: [SDAR, Kill Switch, NEVER_AUTO, 자가복구]
created: 2026-06-12
---

# SDAR Emergency Response (Kill Switch · NEVER_AUTO)

## 정의
SDAR(I-25, 자가진단/자동복구)의 비상 대응 체계. 5-Layer(Detection→Diagnosis→Prescription→Repair→Verification)로 장애를 자동 수리하되, **NEVER_AUTO 10개 영역은 어떤 AR-Level에서도 자동 수리 절대 금지**이며 Kill Switch로 전체 중지가 가능하다.

## 이 개념이 등장하는 모든 도메인
- [[T6-SDAR]] — 6-5 정본(5-Layer·AR-Level·Kill Switch·Circuit Breaker)
- [[T1-Auxiliary-Modules]] — I-25 SDAR Engine(COND, D2.0-02 미수록)
- [[T6-Event-Logging]] — sdar.* 이벤트 등록(CC-006)
- [[T6-Operations]] — 6-13 수동 폴백·장애대응 연계
- [[T6-UI-UX]] — Kill Switch UI(6-1 교차)

## 값·수치 (LOCK)
- AR-Level: AR-L0(수동)~AR-L4(고위험자동), **기본 AR-L2**
- NEVER_AUTO 10: safety_rules / cost_ceiling / approval_flow / non_goals / audit_format / data_retention / user_consent / escalate_own_privilege / guardrails / gate
- Kill Switch(SDAR_SPEC §9.4): **모든 RBAC 역할이 활성화 가능**, SDAR_ROLLBACK_FAILED 시 자동 ON
- V2 COND 활성화 조건: AR-L2→AR-L3, LOW 성공률 ≥ 95% (V2-002)
- V3 ON 조건: AR-L4, 수리성공률 ≥ 95%, 스냅샷 복원 100%

## 버전별 차이
- V1: OFF / V2: COND(조건 충족 시) / V3: ON (I-25 V1=OFF, V2=COND, V3=ON)

## 원본 참조
- `D:\VAMOS\CLAUDE.md` §17 / `D:\VAMOS\docs\sot\VAMOS_SDAR_DESIGN_SPECIFICATION.md` (§9.4) / `D:\VAMOS\docs\sot 2\6-5_SDAR-System\AUTHORITY_CHAIN.md`
