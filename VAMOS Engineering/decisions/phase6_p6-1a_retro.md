# P6-1a 회고 (A11) — Phase 6 (V1) [3분할 1/3]: 6-1 D1' + 6-2 B1'

> **세션**: P6-1a · **일자**: 2026-06-13 · **모델**: claude-opus-4-8[1m] · **모드**: 표준 구현(effort high + 하네스 + II-3, 고위험분 II-1) — 게이트 아님
> **판정**: PASS → P6-1b(6-3 CORE 분모 32) 진입 허용 · **하네스**: ruff/mypy strict 26/vamos_lint 39/pytest **121**(118+3) GREEN

## 결과 요약

| 작업 | 산출 | 검증 |
|------|------|------|
| 6-1 D1' 재검증 | d1_prime_verify.py + d1_prime_report.json (regression 0) | D3 코드 재도출=baseline(DRIFT 0·123/36/23) · COND 106 검증범위 · 24규칙 24행 매핑 |
| 6-1 item 16 Alembic | backend/alembic/ baseline 0001_v0_baseline + 테스트 3 | drift-guard·V0 read-compat·stamp PASS (II-1 데이터손실/호환 적대) |
| 6-2 B1' Layer 2 | vamos_lint VL-006~008 + 테스트 12 | backend 회귀 0 · VL-001~005 불변 · SOT 2 연동(COND 런타임 로드) |

## 잘된 점 (3)

1. **D1' integrity drift를 은폐 않고 정직하게 귀속 분류 + 적대검증으로 오귀속 자가 교정** — Jun-4 baseline 대비 485 drift를 mtime 실측으로 "prior-session SOT2 진화(Jun-11/12 Obsidian, 54f3010=HEAD ancestor)"로 분리해 "P6-1a 귀속 0"을 입증. **II-1 적대검증이 1차 초안의 오귀속을 잡음**: "현 코퍼스=P6-0 'A7 깨진참조 0' 검증"은 거짓(그 A7=훅/스킬→코드 점검, ≠SOT2 cross-ref). 정정: SOT2 conflict 스캔도 Jun-5 stale → 현 코퍼스 active CONFLICT 0은 CONDITIONAL·재스캔 owed(2 비차단 FLAG로 표면화). 초기 "drift 0→재현" carry-forward 로직도 stale baseline에 무효화돼 재설계.
2. **Alembic baseline을 V0 정본에서 동결 + 드리프트 테스트로 강제** — 마이그레이션 불변성(frozen copy)과 V0 정합(memory_store 일치)을 동시 충족: PRAGMA 지문 대조 테스트가 baseline↔memory_store drift를 자동 차단. `IF NOT EXISTS`로 기존 V0 db 무손실(II-1 호환 적대 통과).
3. **Layer 2 오탐 0을 "규칙 보정"으로 달성** — backend가 bare `gate`/`score`/`qod`를 정당히 쓴다는 FP 표면을 *사전 실측*하고, VL-007을 "도메인/COND 모듈 파일 한정"으로 스코프해 CORE 회귀 0. VL-006은 범위 초과만 flag(유효 ID 통과). SOT 2 정본을 런타임 로드해 "187/COND 106"을 하드코딩 아닌 SOT 연동으로 구현.

## 안된 점 / 마찰 (3)

1. **EOL/cp949 함정 2회** — (a) d1 리포트 출력 cp949 인코딩 에러(PYTHONIOENCODING 필요), (b) alembic.ini의 한글/em-dash가 Windows configparser(cp949)에서 디코드 실패 → 테스트 3건 FAIL. alembic.ini를 ASCII-only로 강제해 해결. 설정 파일은 처음부터 ASCII로.
2. **D3 재도출 정규식 1차 버그** — `Final[tuple[str, ...]]`의 중첩 대괄호가 `[^\]]*`를 조기 종료시켜 registry 카운트 -1. PRAGMA/AST 아닌 텍스트 정규식의 한계 — 첫 실행에서 잡혀 수정(consistent=True).
3. **"sot 재실행" 정의의 모호성** — 프롬프트의 "/sot-conflict/sot2-cross-ref/validate 재실행"은 AI 주도 스킬(36 도메인)이라 표준 effort에서 전수 재실행은 비현실적. 결정론적 integrity+코드 재도출+P6-0 검증 carry로 대체했으나, baseline staleness가 그 carry의 가정을 흔들어 재설계 비용 발생.

## 바꿀 것 (1)

- **integrity baseline을 Phase 게이트마다 refresh**(또는 d1_prime_verify에 `--refresh-baseline` 추가) — Jun-4 단일 baseline이 9일치 prior-session 변경으로 stale해져 D1' 해석이 복잡해졌다. 각 Phase 종료 시 현 코퍼스를 새 baseline으로 stamp하면, 다음 D1'은 "직전 검증 상태 대비 회귀"를 직접 측정. (P6-1b에서 도구화 검토 — 단 D1 정본 baseline은 보존, go-forward용 별도 snapshot.)

## P6-1b 인계

- 6-3 CORE 활성화 분모 **32**(PART2 §1.1) · item 2 24규칙 코드 전수 활성화(P6-1a 매핑·등재 기반) · item 7 I-4 Multimodal · item 11 NeMo/Guardrails-AI · effort `max+uc`(H8 고위험).
- B1' Layer 2 CI 3-job 강제 승격은 **PHASE4-DEC-014 절차 선행**(P6-1a 보류).
- **P6-3(6-9) 이연 불변**: V1-004 enum·V1 GO/NO-GO 분모 발산·II-6 교차모델 복구.
