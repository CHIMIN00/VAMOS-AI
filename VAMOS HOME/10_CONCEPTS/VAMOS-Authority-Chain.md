---
tags: [type/concept, tier/all, version/V0, lock/ABSOLUTE]
aliases: [문서 위계, Authority Chain, 정본 우선순위]
created: 2026-06-12
---

# VAMOS Authority Chain (문서 위계 ABSOLUTE)

## 정의
VAMOS 문서 우선순위(ABSOLUTE, D2.0-01 L64):
**RULE 1.3(절대규칙) > PLAN 3.0(상위원칙) > DESIGN 2.0 LOCK > DESIGN 본문(01~08) > 스키마/TECH_STACK(D1~D8, A1)**.
충돌 시 상위가 하위를 override한다.

## 이 개념이 등장하는 모든 도메인
- [[T0-Governance]] — 위계·변경관리 규칙 정본
- [[BASE-1.3-Rules]] — 최상위 절대 불변 규칙(Identity/Safety/Cost/Non-goal)
- [[PLAN-3.0-Roadmap]] — 상위원칙·DEC-001~017
- [[LOCK-Mechanism]] — DESIGN LOCK 계층의 작동 방식
- 전 SOT 2 도메인(36개) — 각 도메인 폴더에 AUTHORITY_CHAIN.md 보유(도메인 내 정본 사슬)

## 값·수치 (LOCK)
- 위계 5단계 (위 정의) — ABSOLUTE
- 변경관리: **삭제 금지**(`[DEPRECATE] + 대체 경로`만 허용) / **없는 내용 창작 금지** / Major 변경은 07 Approval Gate 필수
- 코드 스키마 SOT: Python `contracts.py`(Pydantic v2) → TypeScript Zod / Rust serde 파생
- ⚠️ SOT 실측 DEC-001 라벨은 "에이전트 프레임워크 확정/LangChain 금지 FREEZE" — 위계 라벨 정리는 3-0 게이트 대상

## 버전별 차이
- V0~V3 전 버전 동일 적용 (버전 무관 ABSOLUTE)

## 원본 참조
- `D:\VAMOS\CLAUDE.md` §3/§18 / `D:\VAMOS\docs\sot\D2.0-01_01. VAMOS_DESIGN_2_0_OVERVIEW.md` (L64) / `D:\VAMOS\docs\sot\BASE-1.3_VAMOS_RULE_1.3_BASE.md`
