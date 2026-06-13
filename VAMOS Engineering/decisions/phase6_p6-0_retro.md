# Phase 6 P6-0 (V1 진입 게이트) 회고 (A11)

> **작성일**: 2026-06-13 · 세션: P6-0 (Phase 6 V1 구현 진입 게이트) · 모델: claude-opus-4-8[1m] · effort: max+uc
> 판정: **PASS-WITH-CONDITIONS → P6-1 진입 허용**. 신규 코드 0(점검·결정·SOT 정합 정정만). 게이트 적대검증 wf_a202edf4-b5c(7 에이전트, 523k tok, loop-until-dry converged).

## 잘된 점 (3)

1. **III-3 독립 재도출이 작성 단계 착시를 잡아냄**: SourceQoD(데이터 4요소) vs 출력 QoD(PLAN-3.0 5요소) 구분을 디스크에서 재도출하여, GATE-06 #20의 리터럴 지시("SourceQoDSchema에 5 출력필드 반영")가 **잠긴 계약(DN-009 v3.0.0·D3 DRIFT 0)을 깨뜨릴 오지시**이며 후행 결정 GATE-07 §a C-005에 의해 superseded임을 확인 → #20을 verify-only로 환원(계약 보존). #37도 이미 충족(L6)임을 실측 → 중복 편집 회피.
2. **F1(pytest 110 vs 118) 환경 함정을 디스크로 정산**: 적대 에이전트가 bare `python -m pytest`로 110(jsonrpcserver 미설치)을 본 것을, 정본 명령 `poetry run`으로 **118 passed + jsonrpcserver-5.0.9 poetry.lock 핀**을 실측해 refute. "118 단언"이 정본 명령 한정임을 정직하게 기록(H9-2).
3. **forward-requirement 누락 방지 제도화**: stale "DEC-012+" 표기(012=CI-mypy·013=jsonrpcserver 소비)를 PHASE4-DEC-014 신설 + SKELETON H4/부록 정정으로 해소 — 부착 Phase(6-2/3/4/5/7)서 누락될 위험을 ADR 대장으로 고정.

## 안된 점 / 아쉬운 점 (3)

1. **워크플로 첫 런 0-에이전트 공회전**: 오케스트레이션 본문(agent 호출) 없이 meta+상수만 작성해 1회 무위 실행 → scriptPath 편집 후 재실행으로 복구. 워크플로 작성 시 본문 유무 사전점검 누락.
2. **적대 에이전트(Explore)의 환경 미인지**: poetry 비경유 pytest로 HIGH(F1) 오탐 생성 — 에이전트 프롬프트에 "정본 하네스 명령=poetry run"을 명시했어야 함.
3. **V1 GO/NO-GO 분모 발산(§3.9 15 vs 6-9 22)·V1-004 enum(READINESS 4값 vs MASTER_SPEC 2값)** 은 본 게이트서 해소 못 하고 P6-3/후속 reconcile로 이연 — 분모/잔여 staleness가 누적.

## 다음에 바꿀 것 (1)

- **게이트 적대 워크플로 프롬프트에 "정본 명령·환경(poetry/cargo/pnpm) 실행법 + 분모 정본 위치"를 표준 헤더로 박는다** — 에이전트가 잘못된 env/분모로 오탐 HIGH를 만드는 것을 차단(F1류 재발 방지). SKELETON 부록 적대셋 문구에 1줄 추가 후보.

## 산출/조치 요약

- SOT 정합 정정 5건 집행(승인): MASTER_SPEC §8.8·§17.4(QoD 용도구분, C-005/#18), D2.0-06 §S7D-027·§S7D-014(embedding 기본 1024+Matryoshka256, C-007), STEP7_F-I(₩40,000 LOCK vs $8 목표 구분, #25), 마스터인덱스(CC-011 range-bundle 사유, R-8), BEGINNER_GUIDE §4.3(B↔L 매핑표, #36/CC-009). verify-only 2건: #20(superseded·계약보존), #37(L6 기충족).
- 신규 ADR: PHASE4-DEC-014(신규 테스트도구·CI job 도입 계획) + SKELETON H4/부록 "DEC-012+"→"DEC-014" 정정.
- 점검 PASS: A7 깨진 참조 0 / B.2 12건(외부 4 V1필수+2 V2옵션·SW4·Secret2) / §C I-1~9 부착(I-6/I-8=5-4 종결) / PHASE5-DEC-001 6건 배정 누락 0 / A23 규칙 / 6-3 분모 32.
