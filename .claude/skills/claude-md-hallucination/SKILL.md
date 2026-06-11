---
name: claude-md-hallucination
description: CLAUDE.md 검증 Step 2 — CLAUDE.md 전체를 atomic claim으로 분해해 SOT 원본에서 개별 검증 (VERIFIED/UNVERIFIED/PARTIAL).
---

# /claude-md-hallucination — atomic claim 검증 (Step 2)

> 기반: TOOL GUIDE A-1 `/hallucination-check` 의 CLAUDE.md 전용 확장 (보강전략 V1.0 §6.4)

## 대상
- `D:\VAMOS\CLAUDE.md` (보강 후 — §1~§28)

## 방법
1. 모든 주장을 atomic claim 단위로 분해 (RULE-C6: 테이블 각 셀 = 독립 claim)
   - 예: `I-1 | Intent Detector | CORE | ON | ON | ON` → claim 5개
2. 각 claim을 SOT 원본에서 검증 (D2.0-01/D2.0-02 등 source_file + source_line 탐색)
3. 판정: VERIFIED / UNVERIFIED / PARTIAL
4. RULE-C7: UNVERIFIED 시 "SOT에서 찾을 수 없는 이유" 필수 기술

## 출력
- 총 claim 수, VERIFIED %, UNVERIFIED/PARTIAL 목록 (근거: 파일+라인)
- 저장: `D:\VAMOS\04. 구현단계\claude-md-verification\step2_hallucination.md`
- 목표: 95%+ VERIFIED
