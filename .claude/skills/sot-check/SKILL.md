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

---

## [SOT 2 확장] SOT 2 소스 직접 검증 (v2 추가)

> 기존 SOT 원본 68파일 검증 기능을 유지한 채, SOT 2 파일을 추가 검증 대상으로 확장합니다.

### 추가 검증 대상

```
기존: SOT 원본 68파일 (D:/VAMOS/docs/sot/)
추가: SOT 2 상세명세 (~34파일) + 방식 C 요약 (~7파일) + 계획서 (~34파일)
추가: Part2 구현단계 (D:/VAMOS/docs/guides/VAMOS_구현가이드_PART2_구현단계.md)
```

### 추가 명령어

- `/sot-check sot2 {항목}` → SOT 2 파일에서 해당 항목 직접 검증
- `/sot-check method-c {영역}` → 방식 C 요약 ↔ Part2 정본 대조 검증
- `/sot-check sot2-lock {LOCK명}` → LOCK 값이 SOT 2 전체에서 일관적인지 검증

### SOT 2 검증 판정 기준

| 판정 | 기준 |
|------|------|
| MATCH | SOT 2 값 = Part2 정본 값 (완전 일치) |
| SHIFTED | SOT 2 값은 정확하나 라인 번호 ±10 이동 |
| PARTIAL | SOT 2에 일부만 기재 (누락 필드 존재) |
| MISMATCH | SOT 2 값 ≠ Part2 정본 값 |
| STALE | Part2 업데이트 후 SOT 2 미반영 |
| NOT_IN_SOT2 | Part2에 있으나 SOT 2에 미수록 (방식 C 대상 후보) |

### SOT 2 고유 불일치 추적 (기존 3건과 별도)

SOT 2 작업 과정에서 발견되는 불일치는 별도 추적:
- `D:/VAMOS/docs/sot 2/CONFLICT_LOG.md`에 기록
- Part2 정본 기준으로 해결
- 해결 후 RESOLVED 상태로 전환

### 저장
- `D:/VAMOS/docs/sot 2/_cross-ref/sot2_check_{대상}.json`
