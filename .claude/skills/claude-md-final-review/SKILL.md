---
name: claude-md-final-review
description: CLAUDE.md 검증 Step 8 — Step 1~7 결과 종합 집계 후 GOLD/SILVER/BRONZE/REJECT 판정 (새 판단 추가 금지).
---

# /claude-md-final-review — 종합 판정 (Step 8)

> 기반: TOOL GUIDE A-47 `/final-review` 의 CLAUDE.md 전용 확장 (보강전략 V1.0 §6.4)

## 입력
- `D:\VAMOS\04. 구현단계\claude-md-verification\step1~step7*.md` 전부 Read
- RULE-C13: 판정은 step1~7 파일의 수치만 사용 — 새로운 판단 추가 금지

## 집계
- SOT 모순 N / Hallucination UNVERIFIED N / Fact Audit 확정 UNVERIFIED N / Cross-Examine 불충분 N / Symbolic FAIL N / Consensus 불일치 N / Completeness 누락 N

## 판정 기준
| 등급 | 조건 |
|------|------|
| GOLD | UNVERIFIED 0, FAIL 0, 누락 0 |
| SILVER | UNVERIFIED ≤3, FAIL 0, 누락 ≤5 |
| BRONZE | UNVERIFIED ≤10, FAIL ≤2 |
| REJECT | 그 외 |

## 출력
- 종합 리포트 + 판정 등급
- 저장: `D:\VAMOS\04. 구현단계\claude-md-verification\step8_final_review.md`
- REJECT 시 (A1): 보강 범위 §21~§24 축소 → 재검증 → BRONZE 허용 후 진행
