# PHASE2-DEC-01: pre-commit 훅 재도입 안 함 (ci.yml 대체)

> **결정일**: 2026-06-11 (Phase 2-4) · **포맷**: A6 (결정 + 이유 + 대안 + 근거)

## 결정

`.pre-commit-config.yaml`은 D17(2026-06-11) 집행 상태(`repos: []` + 판정 주석)를 **그대로 유지**하고, pre-commit 훅을 재도입하지 않는다. 커밋 품질 게이트는 **`.github/workflows/ci.yml`(단일 통합: quality + test + vamos-lint job)** 이 담당한다.

## 이유

1. D17 원인이었던 외부 훅(freddo1503/claude-pre-commit)은 upstream 태그 부재로 전 커밋을 차단했던 전력 — 외부 의존 훅 재도입은 동일 리스크 재현.
2. Phase 2-4에서 ci.yml(ruff+mypy+pytest+vamos_lint)이 동일 검사를 서버측에서 수행 — 로컬 훅과 중복.
3. 로컬 즉시 피드백은 .claude/settings.json 코드 생산 Hook(.py 수정 시 ruff 자동 실행, STRATEGY_10 4-V4)이 제공 — pre-commit 없이도 커밋 전 검사 공백 없음.
4. 문서 중심 커밋(현 단계 대부분)에 Python 훅 강제는 마찰만 유발.

## 검토한 대안

- **(기각) 로컬 ruff/pytest pre-commit 훅 재구성**: CI와 중복 + Windows bash 훅 호환성 비용. V1 진입 시(코드 커밋 비중 증가) 재평가 가능.
- **(기각) 파일 삭제**: D17 판정이 "유효한 빈 config + 판정 기록 주석으로 보존"을 명시.

## 근거 SOT/결정

- D17 (`_targets/DECISION_REGISTER.md`) — 훅 블록 제거·repos:[] 보존, "향후 훅 재도입 여부"는 본 결정으로 종결
- 로드맵 2-4: "훅 재도입 여부는 본 작업에서 결정" / STRATEGY_09 §7~§8 (CI 정본)
- PHASE_B6 §2 ci.yml 단일 통합 정본 (PART2 §6.4 L4844 주석)
