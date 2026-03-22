---
name: sot-check
description: SOT 원본 파일 직접 대조 검증. 특정 key나 EA에 대해 SOT 원본에서 값을 직접 확인. 의심 항목 발생 시 또는 /audit 후 실행.
---

# VAMOS v13 SOT 원본 대조 스킬

> `/sot-check [EA번호|key명|all]`

## 용도

/validate (결정론적) → /audit (적대적) 에서 발견된 **의심 항목**을 SOT 원본에서 직접 확인합니다.

---

## 모드

- `/sot-check EA-1` → EA-1 산출물의 모든 항목을 SOT 원본 대조
- `/sot-check TOTAL_MODULE_COUNT` → 특정 key가 등장하는 모든 EA에서 SOT 대조
- `/sot-check known` → 기존 3대 불일치(A/B/C) 집중 확인
- `/sot-check all` → 전체

$ARGUMENTS 를 파싱하여 모드 결정.

---

## 핵심 규칙

1. **SOT 파일은 반드시 전체 읽기**. 2000줄 초과 시 분할 읽기.
2. **Read tool의 행 번호만 신뢰**. 산출물의 source_line은 검증 대상.
3. **원문 텍스트 직접 비교**. 의역/요약이 아닌 글자 그대로 매칭.

## 판정

| 판정 | 의미 |
|------|------|
| `MATCH` | 정확히 해당 행에 존재, value 일치 |
| `SHIFTED` | ±10줄 이내에 존재 (행 번호만 틀림) |
| `PARTIAL` | 일부만 매칭 (축약/변형) |
| `MISMATCH` | 텍스트는 있으나 value가 다름 |
| `NOT_FOUND` | 파일 전체에서 미발견 — **환각 확정** |

## 3대 불일치 추적 (known 모드)

- 불일치 A: IMMUTABLE_ZONE_COUNT(7) vs NEVER_AUTO_COUNT(10) — 범위 차이
- 불일치 B: COND MEDIUM 9→8, LOW 3→4 — 상세 목록이 정본
- 불일치 C: 3-tier vs 4-tier — 분류 기준 차이

**저장**: `v13_results/phase0/extraction/sot_check/{대상}_sot_check.json`
