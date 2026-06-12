# PHASE4-DEC-006 (P4-0 ⑫=STEP 2b): EOL 정규화 — 자연 수렴 유지 + .gitattributes 코드 확장자 한정 규칙 추가

> **결정일**: 2026-06-12 (P4-0) · **포맷**: A6 · **우선순위**: Must · **출처**: P4-PRE B-02a + GATE-07 EOL 사건 이관

## 결정

1. **기존 이중 상태(CRLF-디스크/LF-blob) 683파일(2026-06-12 실측, `_targets/eol_baseline_p4-0.txt` 기준선): 일괄 정규화 커밋 하지 않음 — 자연 수렴 경로 유지.** 해당 파일을 수정 커밋하는 시점에 blob이 디스크 EOL로 수렴(PART2 d5bc6e8 선례 — P4-PRE §6 공시 경로). 수정 커밋 시 diff에 EOL 수렴이 포함될 수 있음을 공시 후 진행.
2. **`.gitattributes`에 코드 확장자 한정 EOL 규칙 추가 — 집행 완료(본 세션)**: `*.py/*.rs/*.ts/*.tsx/*.js/*.jsx/*.toml/*.yml/*.yaml/*.sh text eol=lf`. 기존 LFS 규칙(golden_set·benchmark_results) **무변경 보존, 추가만**. `*.md`·`*.json` 제외(문서=자연 수렴 유지 / json=LFS 규칙 간섭 방지).
3. 재발 방지 3중 장치 완성: ① repo-local `core.autocrlf=false`(기설정) ② 브랜치 체크아웃 금지+`git fetch . <branch>:main`(GATE-08/release_strategy) ③ 본 규칙(Phase 4+ 신규 코드 LF 고정 — clone·타 도구의 autocrlf 설정과 무관하게 강제).

## 근거
- 집행 직후 실측: 기존 추적 코드 파일 126건에 변경 감지 0건(비파괴) — 규칙은 신규/수정 시점부터 적용.
- 일괄 정규화의 비용: 683파일 일제 blob 재기록 → 커밋 이력 노이즈 + `git blame` 단절 + 24~25개 백업/integrity 기준선과의 대조성 저하. 자연 수렴은 d5bc6e8에서 무사고 검증 완료(diff 2줄 정확).

## 기각 대안
- (i) 일괄 정규화 커밋 — 상기 비용 대비 이득(일관성)이 자연 수렴으로도 점진 달성됨. 기각.
- (iii)' 전역 `* text=auto eol=lf` — 문서군(PART1/PART2 등 역사적 CRLF 27건 포함)까지 재정규화 대상화 → EOL 사건 재발 벡터. 기각.

## 집행
.gitattributes 추가 완료(STEP 2b) · 기준선 `_targets/eol_baseline_p4-0.txt` 저장 완료(i/lf w/crlf 683 · i/crlf w/crlf 3 · i/lf w/lf 981) · sot CLAUDE.md SHA-256 루트 일치 확인(45120F11…) · 재동기화 상시 규칙 release_strategy.md §1 1줄 추가 완료(DEC-011 §4 집행).
