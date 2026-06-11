---
tags: [type/concept, tier/all, version/V1, lock/ABSOLUTE, responsible-ai]
aliases: [비용 상한, Cost Ceiling, 비용 한도]
created: 2026-06-11
---

# Cost Limits (비용 상한 — ABSOLUTE LOCK)

## 정의
버전별 월/일 비용 절대 상한. 7개 불변 구역 중 cost_ceiling에 해당하며 Self-evo·SDAR로도 변경 절대 불가(ABSOLUTE).

| 버전 | 월 상한 | 일 상한 | 모델 배분 |
|------|---------|---------|----------|
| V1 | ₩40,000 ($30) | ₩1,300 ($1) | Mini 90%+ |
| V2 | ₩93,000 ($70) | ₩3,100 ($2.3) | Mini 60-70% / Main 30-40% |
| V3 | ₩266,000 ($200) | ₩8,900 ($6.7) | Main 중심, Flagship 적극 |

## 이 개념이 등장하는 모든 도메인
- [[T0-Governance]] — BASE-1.3 비용 LOCK 정본
- [[T1-Auxiliary-Modules]] — I-9 Cost Manager(CORE LOCK)
- [[T6-Security]] — RBAC 예산: OWNER ₩266K / ADMIN ₩93K / OPERATOR ₩40K / VIEWER ₩0
- [[T6-UI-UX]] — 비용 경고 색상 80%=#FBBF24, 100%=#EF4444 (DEC-015)
- [[T6-Brain-Adapter]] — 모델 라우팅/Downshift 실행 지점

## 값·수치 (LOCK)
- Downshift(LOCK): **80% warn/force_mini, 100% block(자동 차단)**
- config.v1.toml: cost.monthly_limit=40000(ABSOLUTE), cost.daily_limit=1300(ABSOLUTE), warn_threshold=80, block_threshold=100
- V0 비용 상한 = V1 동일 적용(V0-001) / CostGate 판정: normal/downshift/split/stop

## 버전별 차이
- V1→V2→V3 상한만 단계 상향, Downshift 80/100% 규칙은 전 버전 동일
- V3-003: V3 상한은 V2 운영 데이터 기반 재산정 예정

## 원본 참조
- `D:\VAMOS\docs\sot\BASE-1.3_VAMOS_RULE_1.3_BASE.md` / `D:\VAMOS\CLAUDE.md` §7.3·§20 / `D:\VAMOS\docs\sot\PLAN-3.0_VAMOS_PLAN_3_0_최종완성본.md`
