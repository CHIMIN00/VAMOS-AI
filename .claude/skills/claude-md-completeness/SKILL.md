---
name: claude-md-completeness
description: CLAUDE.md 검증 Step 7 — SOT 68파일·SOT2 36도메인·187모듈·LOCK 네임스페이스 대비 CLAUDE.md 누락 탐지 (ls/grep 직접 비교).
---

# /claude-md-completeness — 누락 탐지 (Step 7)

> 기반: TOOL GUIDE A-48 `/completeness-map` 의 CLAUDE.md 전용 확장 (보강전략 V1.0 §6.4)

## 비교 항목 (RULE-C12: ls/grep 결과 직접 비교 — AI 기억 의존 금지)
1. SOT 68개 파일명(ls) vs CLAUDE.md 언급 파일명(grep) → 누락 파일
2. SOT 2 36개 도메인 폴더명(ls) vs §21 라우팅 테이블 → 누락 도메인
3. 187개 모듈 ID vs §6 테이블 행 수 → 누락 모듈
4. LOCK 네임스페이스(GLOSSARY/AUTHORITY) vs §7 → 누락 LOCK
5. Non-goal 7개 vs §8
6. 교차 용어 15개 vs §23

## 출력
- 참조율 %, 누락 항목 목록
- 저장: `D:\VAMOS\04. 구현단계\claude-md-verification\step7_completeness.md`
- 비고: §2가 "핵심 39 / 전체 68" 구조이므로 비핵심 29개의 개별 미언급은 누락이 아닌 설계 — §21/§24 경유 참조로 판정
