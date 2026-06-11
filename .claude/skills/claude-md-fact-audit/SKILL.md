---
name: claude-md-fact-audit
description: CLAUDE.md 검증 Step 3 — Step 2의 PARTIAL/UNVERIFIED 항목을 3-Agent 토론(감사자/반박자/판정자)으로 편향 없이 재검증.
---

# /claude-md-fact-audit — 3-Agent 토론 재검증 (Step 3)

> 기반: TOOL GUIDE A-2 `/fact-audit` 의 CLAUDE.md 전용 확장 (보강전략 V1.0 §6.4)

## 대상
- `step2_hallucination.md`에서 PARTIAL/UNVERIFIED 판정된 항목만

## 방법 (3-Agent 토론)
- **Agent 1 (감사자)**: 해당 claim이 SOT와 일치한다는 근거 제시
- **Agent 2 (반박자)**: 불일치 근거를 적극 탐색 (다른 SOT 파일 포함)
- **Agent 3 (판정자)**: 양측 근거를 직접 SOT에서 확인(RULE-C8) → 최종 판정
- 항목별 결과: 승격(→VERIFIED) / 확정(→UNVERIFIED) / 유지(→PARTIAL)

## 출력
- 승격/확정/유지 건수 + 항목별 판정 근거(파일+라인)
- 저장: `D:\VAMOS\04. 구현단계\claude-md-verification\step3_fact_audit.md`
