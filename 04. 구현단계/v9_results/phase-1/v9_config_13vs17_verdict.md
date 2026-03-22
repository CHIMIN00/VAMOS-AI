# [-1B] Config "13 vs 17" 확정 판정

> **판정일**: 2026-03-07
> **입력**: PART2 line 117, PHASE_B_EXHAUSTIVE_ANALYSIS.md D.3절
> **결론**: **17섹션 확인 (CONFIRMED)**

---

## 1. PART2 V0 config.v1.toml — 13섹션

PART2 lines 117~196에 명시된 V0 축약본 13개 `[section]`:

| # | Section | PART2 B4 참조 |
|---|---------|--------------|
| 1 | `[core]` | §3.1 |
| 2 | `[llm]` | §3.2 |
| 3 | `[embedding]` | §3.3 |
| 4 | `[vector_db]` | §3.4 |
| 5 | `[graph_db]` | §3.5 |
| 6 | `[storage]` | §3.6 |
| 7 | `[cost]` | §3.7 |
| 8 | `[self_check]` | §3.8a |
| 9 | `[approval]` | §3.8b |
| 10 | `[mcp]` | §3.9 |
| 11 | `[rbac]` | §3.10 |
| 12 | `[logging]` | §3.12 |
| 13 | `[semantic_cache]` | §3.15 |

## 2. PHASE_B_EXHAUSTIVE_ANALYSIS.md — 13섹션 (다른 구성)

EXHAUSTIVE_ANALYSIS D.3절 + D.4 Pydantic 모델 목록:

| # | Section | B4 Lines |
|---|---------|----------|
| 1 | `[core]` | 138-153 |
| 2 | `[llm]` | 157-178 |
| 3 | `[embedding]` | 182-197 |
| 4 | `[vector_db]` | 200-216 |
| 5 | `[graph_db]` | 220-235 |
| 6 | `[storage]` | 238-267 |
| 7 | `[cost]` | 271-290 |
| 8 | `[guardrails]` | 294-315 |
| 9 | `[mcp]` | 319-346 |
| 10 | `[rbac]` | 349-389 |
| 11 | `[rate_limit]` | 393-423 |
| 12 | `[logging]` | 426-465 |
| 13 | `[semantic_cache]` | 469-482 |

**차이점**: EXHAUSTIVE_ANALYSIS에는 `[guardrails]`, `[rate_limit]` 포함 / `[self_check]`, `[approval]` 미포함
PART2 V0에는 `[self_check]`, `[approval]` 포함 / `[guardrails]`, `[rate_limit]` 미포함

## 3. B4 정본 전체 = 17섹션 (합집합)

| # | Section | V0 포함 | EXHAUSTIVE 포함 | 비고 |
|---|---------|---------|----------------|------|
| 1 | `[core]` | O | O | 공통 |
| 2 | `[llm]` | O | O | 공통 |
| 3 | `[embedding]` | O | O | 공통 |
| 4 | `[vector_db]` | O | O | 공통 |
| 5 | `[graph_db]` | O | O | 공통 |
| 6 | `[storage]` | O | O | 공통 |
| 7 | `[cost]` | O | O | 공통 |
| 8 | `[mcp]` | O | O | 공통 |
| 9 | `[rbac]` | O | O | 공통 |
| 10 | `[logging]` | O | O | 공통 |
| 11 | `[semantic_cache]` | O | O | 공통 (11개) |
| 12 | `[self_check]` | O | X | V0 포함, B4 §3.8a |
| 13 | `[approval]` | O | X | V0 포함, B4 §3.8b |
| 14 | `[guardrails]` | X | O | V0 생략, V1+ 추가 |
| 15 | `[rate_limit]` | X | O | V0 생략, V1+ 추가 |
| 16 | `[blue_nodes]` | X | X | V0 생략, V1+ 추가 |
| 17 | `[ui]` | X | X | V0 생략, V1+ 추가 |

**합산**: 공통 11 + V0 전용 2 (`self_check`, `approval`) + V0 생략 4 (`guardrails`, `rate_limit`, `blue_nodes`, `ui`) = **17**

## 4. 확정 판정

**CONFIRMED**: B4 정본은 17섹션. V0에서 4개 생략 (`[blue_nodes]`, `[ui]`, `[rate_limit]`, `[guardrails]`).

- PART2 line 117의 HTML 주석 정확: `B4 정본은 17섹션. V0에서 [blue_nodes],[ui],[rate_limit],[guardrails] 생략`
- PART2 line 1121 (XREF-V0-18) 교차 확인 일치
- V0의 13 + 생략 4 = 17 산술 정확

### 주의사항

1. **EXHAUSTIVE_ANALYSIS 불완전성**: D.3절은 B4의 17섹션 중 13개만 기술. `[self_check]`, `[approval]`, `[blue_nodes]`, `[ui]` 4개 누락. GT-3 구축 시 이 불완전성 고려 필요.
2. **`[blue_nodes]`와 `[ui]` 실존 확인 완료**: B4 정본(PHASE_B4_CONFIG_SPEC.md) 원본 직접 확인 결과, `[blue_nodes]` (line 512, §3.13)과 `[ui]` (line 528, §3.14) 모두 실존. PART2 HTML 주석(line 117, line 1121)과 일치.
3. **§번호 매핑 확정**: PART2 line 1123-1127에서 확인 — §3.11=`[rate_limit]`, §3.13=`[blue_nodes]`, §3.14=`[ui]`, §3.16=`[guardrails]`. §3.12=`[logging]`, §3.15=`[semantic_cache]`.

---

> **GT-3 반영**: config 섹션 수 = LOCK 17 (V0=13, V1+=17)