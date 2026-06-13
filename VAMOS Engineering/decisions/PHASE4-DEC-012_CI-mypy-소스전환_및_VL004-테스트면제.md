# PHASE4-DEC-012 — CI mypy 타깃 소스 전환 + tests strict 제외 + VL-004 테스트 면제

> **결정일**: 2026-06-13 · **우선순위**: Must (하네스 정합) · **상태**: 확정
> **근거 SOT**: PHASE4-DEC-011 §D(ADR-게이트 — CI job 변경은 별도 ADR 선행) · STRATEGY_09 §8(하네스) · test_strategy §4(V0 phasing) · PART2 §6.4(ci.yml 정본)
> **트리거**: P4-3 게이트(4-V) 적대검증이 **CI 3-job 중 2개가 배선 그대로 RED**임을 독립 재도출(III-3) — 무조건 PASS 불가 → NO-GO → 사용자(VI-1/VI-2) 수리 인가

---

## 1. 결정 (Decision)

PHASE4-DEC-011 §D가 "CI job 추가/변경은 PHASE4-DEC-012+ ADR 선행"으로 예약한 슬롯을 집행한다. 잠긴 하네스의 **강도(strict)는 유지**하되, P4-3 게이트가 노출한 3가지 배선 결함을 교정한다:

1. **CI mypy 타깃을 `tests/` → `vamos_core`로 전환**(`.github/workflows/ci.yml` quality job). 기존 `mypy tests/`는 "코드 디렉토리 생성 전" placeholder였고 주석이 "V0-STEP-1 후 `mypy .` 전환"을 예고했으나 미집행 상태였다. V0-STEP-1(monorepo·소스 디렉토리)은 완료되었으므로 **strict mypy 게이트를 제품 소스(`vamos_core`)에 부착**한다.
2. **tests는 strict mypy 제외**(소스 대상에서 제외 — `mypy vamos_core`). 테스트 코드는 pytest(동작)+ruff(스타일)가 커버하며, strict 타입(`no-untyped-def`·Optional 접근 등)을 테스트에 강제하는 것은 test_strategy §4 V0 phasing("실질 깊이 V1부터")과 정합하지 않는다.
3. **VL-004(LOCK 재할당 금지) 테스트 파일 면제**(`scripts/vamos_lint.py`). 테스트는 LOCK 재할당이 `ValidationError`로 **거부됨을 검증**(Defense Layer 1)하므로, 그 라인을 위반으로 보는 것은 오탐이다. R5의 의도는 "런타임 덮어쓰기 금지"이지 "거부 테스트 금지"가 아니다. VL-001/002/003/005는 테스트에도 계속 적용된다.

## 2. 이유 (Why) — 베이스라인 약화가 아니라 정합 교정

- **strict = true 불변**: pyproject `[tool.mypy] strict=true`는 그대로다. 변경은 *타깃 스코프*(tests→source)뿐이며, 그 결과 **제품 소스가 처음으로 strict mypy 게이트를 통과**하게 된다(이전엔 mypy가 tests만 봐서 소스의 실제 타입결함 12건이 한 번도 게이트되지 않음 — 게이트가 *더 강해짐*).
- **P4-3 게이트 발견(독립 재도출 + 교차검증 수렴)**: `mypy tests/`=88 errors(exit 1, quality RED) · `mypy vamos_core`=12 errors(소스 실결함 미게이트) · `vamos_lint.py backend`=1 violation(test 오탐, vamos-lint RED). "매 커밋 mypy strict PASS" 단언은 소스에 대해 실제로 거짓이었다.
- **asymmetric-tolerance 논거**: pytest 스텝은 V0 0-tests용 `exit 5` 관용이 의도적으로 인코딩됐으나 mypy/lint 스텝엔 없었다 → "V0이라 mypy를 봐준다"는 해석은 성립 불가. RED는 정당한 게이트 실패였다.

## 3. 집행 내역 (이 ADR과 동반 — P4-3 수리 사이클, 사용자 인가)

| 변경 | 파일 | 내용 |
|---|---|---|
| CI mypy 재지정 | `.github/workflows/ci.yml` L24 | `mypy tests/` → `mypy vamos_core` |
| VL-004 테스트 면제 | `scripts/vamos_lint.py` | `lint_file`에 `is_test` 가드(파일명 `test_*` 또는 경로 `tests/` → VL-004 skip) |
| 소스 strict 결함 12건 수정 | `vamos_core/orange_core/{pipeline,i1_intent_detector,i5_decision_engine,i9_cost_manager}.py` · `vamos_core/infra/config_loader.py` | `cast`(ChatModel·GateResult·Priority·dict) 7 + `float()` 2 + or-chain 1 — **순수 타입레벨, 런타임 동작 무변경**(pytest 118 무회귀로 확인) |

## 4. 경계 (Boundary — DEC-011 §D 준수)

- **불변 유지**: ruff 13룰 · mypy `strict=true` · vamos_lint VL-001~005 룰셋 · CI 3-job 구조 · 테스트 피라미드 · SOT. 본 ADR은 *타깃/스코프 교정*이며 룰·강도·job 수를 늘리거나 줄이지 않는다.
- **신규 도구 0**: 뮤테이션/프로퍼티/퍼징 등 §C 보류분은 여전히 P6-0+ ADR 선행(DEC-011 §C 불변).
- **V0→V1 hardening 후보**: 테스트의 strict 타입화(88건)는 V1 Eval(6-7) 시 점진 적용 후보로 등재(차단 아님).

## 5. 검증 (집행 직후 실측, 2026-06-13)

```
cd backend && poetry run ruff check .        # All checks passed
cd backend && poetry run mypy vamos_core     # Success: no issues found in 26 source files (exit 0)
cd backend && poetry run python -m pytest tests/ -q   # 118 passed (무회귀)
python scripts/vamos_lint.py backend         # 위반 0건 (exit 0)
```
3 CI job(quality/test/vamos-lint) 전부 GREEN 실측 → P4-3 재게이트 Must 10·Must 9 PASS 충족.

## 6. 참조

- 본 ADR은 PHASE4-DEC-011 §D 예약 슬롯 집행, A6(의사결정 기록) 준수. PROGRESS.md "P4-3 결과" + 로드맵 추적표에서 참조.
