---
name: claude-md-consensus
description: CLAUDE.md 검증 Step 6 — 핵심 수치 50개를 3회 독립 추출 후 다수결로 안정성 판정 (라운드 간 결과 비공유).
---

# /claude-md-consensus — 3회 독립 다수결 (Step 6)

> 기반: TOOL GUIDE A-5 `/consensus` 의 CLAUDE.md 전용 확장 (보강전략 V1.0 §6.4)

## 대상 (핵심 수치 50개 고정 목록)
- [모듈] I(25), E(16), S(8), A(7), B(6), C(7), D(6), EVX(6), COND(106), Named(81), 전체(187)
- [비용] V1 월(40000)/일(1300), V2 월(93000)/일(3100), V3 월(266000)/일(8900), Downshift warn(80%)/block(100%)
- [임계값] Self-check P0(70)/P1(75)/P2(80), Semantic cache(0.95), QoD block(<0.4)/hold(<0.7), 병렬(3), 대화턴 P0(5)/P1(10)/P2(20)
- [Gate] Policy/Cost/Approval/Evidence/SelfCheck 5종 존재
- [메모리] L0 TTL(7일), L1 TTL(90일), B-4→L0, B-1→L1, B-3→L2, B-2→L3
- [기타] BGE-M3 dim(1024), embedding model(bge-m3), RBAC 4등급, Non-goal(7), Guardrails 4-Layer, 승인 타임아웃(10분)

## 방법 (RULE-C11: 각 라운드 독립 Agent spawn, 이전 결과 전달 금지)
- Round 1/2/3: 각 Agent가 SOT에서 50개 수치 독립 추출
- 다수결: 3/3 = 안정, 2/3 = 경고, 1/3 = 수동확인 필요

## 출력
- 일치율 %, 불일치 항목 목록
- 저장: `D:\VAMOS\04. 구현단계\claude-md-verification\step6_consensus.md`
