---
name: claude-md-cross-examine
description: CLAUDE.md 검증 Step 4 — LOCK/비용/임계값 핵심 수치에 "출처가 어디?" 능동 질문으로 근거 추적 (Agent A 주장 vs Agent B 검증).
---

# /claude-md-cross-examine — 근거 교차 신문 (Step 4)

> 기반: TOOL GUIDE A-3 `/cross-examine` 의 CLAUDE.md 전용 확장 (보강전략 V1.0 §6.4)

## 대상
- CLAUDE.md §7 LOCK 전수 + §8 Non-goal + §15 메모리 계층 수치 + §20 config LOCK 20키

## 방법
- **Agent A**: CLAUDE.md 내용을 주장
- **Agent B**: "이 수치의 출처 파일과 라인 번호는?" 질문
- Agent A 답변 → Agent B가 실제 SOT를 Read로 직접 확인 (RULE-C9)
- 답변 불충분(파일에서 못 찾음) → 의심(SUSPECT) 표시

## 출력
- 검증된 수치 건수 / 답변 불충분(SUSPECT) 건수 + 목록
- 저장: `D:\VAMOS\04. 구현단계\claude-md-verification\step4_cross_examine.md`
