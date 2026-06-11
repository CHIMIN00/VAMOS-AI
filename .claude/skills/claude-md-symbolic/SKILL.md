---
name: claude-md-symbolic
description: CLAUDE.md 검증 Step 5 — 수치 합산/범위/경로 존재를 결정론적으로 검증 (AI 판단 0%, Bash/PowerShell 도구만).
---

# /claude-md-symbolic — 결정론적 수치 검증 (Step 5)

> 기반: TOOL GUIDE A-9 `/symbolic-verify` 의 CLAUDE.md 전용 확장 (보강전략 V1.0 §6.4)

## 대상
- `D:\VAMOS\CLAUDE.md` 내 모든 수치

## 검증 제약 8개 (RULE-C10: wc -l, grep -c 등 도구로 실행 — AI 계산 금지)
- C1: I-Series 테이블 행 수 = 25
- C2: I(25)+E(16)+S(8)+A(7)+B(6)+C(7)+D(6)+EVX(6) = 81
- C3: COND CAT 합산 13+13+53+8+7+8+4 = 106
- C4: 81 Named + 106 COND = 187
- C5: V1(40000) < V2(93000) < V3(266000) 비용 순서
- C6: B↔L 매핑 4쌍 = 4쌍 (B-4→L0, B-1→L1, B-3→L2, B-2→L3)
- C7: §21 Tier 도메인 합계 = 36 / 기재된 모든 파일 경로 실존 확인
- C8: §4 기재 줄 수 vs 실측(ReadAllLines) 오차 ±5% 이내

## 출력
- 제약별 PASS/FAIL
- 저장: `D:\VAMOS\04. 구현단계\claude-md-verification\step5_symbolic.md`
