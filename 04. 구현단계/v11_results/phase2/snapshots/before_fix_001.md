# Before Fix 001 — FG-B01: 비용 알람 체계 통일
# Snapshot at: 2026-03-12
# Decision: B (3단계 70/85/95%)

## L206-211 (§2 STEP-1 config — 첫 번째 게시)
```
[cost]                           # PHASE_B4 §3.7
daily_limit = 1300               # KRW (B4 정본: daily_limit, _krw 접미사 없음)
monthly_limit = 40000            # LOCK: ₩40,000/월
warn_threshold = 80              # % (B4 정본: warn_threshold, _pct 접미사 없음)
block_threshold = 100            # %
currency = "KRW"
```

## L381-386 (§2 STEP-1 config — 두 번째 게시)
```
[cost]                           # PHASE_B4 §3.7
daily_limit = 1300               # KRW (B4 정본: daily_limit, _krw 접미사 없음)
monthly_limit = 40000            # LOCK: ₩40,000/월
warn_threshold = 80              # % (B4 정본: warn_threshold, _pct 접미사 없음)
block_threshold = 100            # %
currency = "KRW"
```

## L1529 (§3 V1 Phase 1 — 비용 3단계 경보 체계)
```
| I-9 | 비용 3단계 경보 체계 | 70% 경고 / 85% 심화 경고 / 95% 차단 (config.v1.toml cost 섹션) | P30-058 |
```

## §7.1 L4167 (V0 체크리스트)
```
| 14 | 비용 엔진 ₩40,000/월 하드코딩 | ABSOLUTE LOCK | [ ] |
```

## §7.2 L4183 (V1 체크리스트)
```
| 9 | 비용 상한 ₩40,000 통일 | V1-013 | [ ] |
```
