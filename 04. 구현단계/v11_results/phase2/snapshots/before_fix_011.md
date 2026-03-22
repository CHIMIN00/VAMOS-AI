# Before Fix 011 — FG-H05: config 값 불일치 수정
# Snapshot at: 2026-03-12

## L164/L340 autonomy_level = "L1" vs L1498 "L2_COPILOT"
```
L164: autonomy_level = "L1"            # LOCK
L340: autonomy_level = "L1"            # LOCK
L1498: > - I-1: `autonomy_level` 기본값 `L2_COPILOT` (PHASE_B4 §3.1 LOCK)
```

## L2226 max_turns(50) vs L2385 max_turns_per_session = 100
```
L2226: (3) max_turns(50) 도달
L2385: i07.max_turns_per_session = 100
```

## L1301 "V0: strict 미적용" vs L1407 strict = true
```
L1301: run: cd backend && poetry run mypy .  # V0: strict 미적용. V1+에서 --strict 활성화 권장
L1407: strict = true
```
