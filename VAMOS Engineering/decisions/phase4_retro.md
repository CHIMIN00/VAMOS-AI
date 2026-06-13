# Phase 4 (V0 구현) 회고 — A11

> **작성일**: 2026-06-13 · **세션**: P4-0 ~ P4-3 · **판정**: Phase 4 게이트(4-V) **PASS**(수리 후) → Phase 5 진입 허용
> **모델**: Opus 4.8 (1M) · 게이트 = ultracode + 교차모델 대체(인간 VI-1/VI-2)

## 잘된 것 (Keep) — 3

1. **갭폐쇄 하네스가 실제로 작동했다 (R16 착시 방어)**: P4-3 게이트의 독립 적대검증(III-3)이 PROGRESS의 "매 커밋 mypy strict PASS" 단언을 *디스크에서 반증* — CI 3-job 중 2개(quality mypy·vamos-lint)가 배선 그대로 RED이고 소스에 strict 타입결함 12건이 한 번도 게이트되지 않았음을 잡아냄. "초안 무결"이 아니라 "재검증 수렴"이 품질을 만든다는 DEC-011 §2 명제의 실증.
2. **완전성 비평가(VI-3)의 asymmetric-tolerance 논거**: pytest 스텝엔 V0 0-tests용 `exit 5` 관용이 의도적으로 박혔으나 mypy/lint엔 없음 → "V0이라 mypy를 봐준다"는 자기합리화를 차단. 게이트가 *변명을 적대적으로 검증*해 NO-GO를 정당화.
3. **타입 동기화(A20) seam의 견고함**: Python↔serde(Rust)↔TS 왕복 25/25가 실 cargo test 컴파일 포함으로 끝까지 GREEN. 3언어 seam(R07)이 V0에서 실제 동작.

## 안된 것 (Problem) — 3

1. **하네스 배선 stale를 V0 내내 방치**: `ci.yml`의 `mypy tests/`는 "코드 생성 전 placeholder, V0-STEP-1 후 `mypy .` 전환" 주석이 있었으나 소스 생성(P4-1) 후에도 전환 미집행 → mypy가 소스를 한 번도 검사 안 함. P4-0/1/2가 "mypy clean"을 *좁은 수동 실행*으로 자가확인하며 CI 배선과의 불일치를 못 봄.
2. **"PASS 단언"의 전파**: P4-1/4-2 PROGRESS가 "ruff/vamos_lint/mypy clean"을 실측 명령 없이 단언 → P4-3 게이트가 아니었으면 RED CI가 Phase 5로 새어나갈 뻔. H9-2(사실=디스크 실측만)의 부재가 만든 결함.
3. **소스 strict 타입결함 12건이 누적**: Optional LLM `.ainvoke`(NPE 가능)·`str`→`Literal` 게이트결과 등 — 게이트가 부재했다면 잠복 버그로 V1까지 이월됐을 것.

## 바꿀 것 (Try) — 1

- **하네스 배선 자체를 매 Phase 게이트의 *실측* 대상으로 못박는다**: "ruff/mypy/vamos_lint/pytest PASS"를 *단언*이 아니라 **CI에 배선된 그대로의 명령을 실행해 exit code로 판정**(H9-2 강화). placeholder/전환 예정 배선은 그 전환 조건(예: "V0-STEP-1 후")이 충족되는 즉시 해당 작업 행에서 집행하고, 미집행 시 다음 게이트가 RED로 잡도록 한다. → SESSION_PROMPT_SKELETON H6/H9에 "하네스 = 배선된 명령 실측" 규칙 반영 후보.

## 게이트 서사 요약 (P4-3)

NO-GO(CI 2/3 RED, 독립 적대검증 수렴) → 사용자(VI-1/VI-2) "수리 인가 + 재게이트" 판정 → A1 수리(ADR PHASE4-DEC-012 하: 소스 mypy 12건 수정[순수 타입레벨] + CI mypy→`vamos_core` 재지정 + VL-004 테스트 면제) → 재게이트 round 2 converged(3 job GREEN·fixes_sound=true·masked_bug 0·pytest 118/roundtrip 25·25/IPC PASS) → **PASS**. 잠금 강도(strict=true·룰셋·job 구조) 불변, 스코프/타깃 교정만.
