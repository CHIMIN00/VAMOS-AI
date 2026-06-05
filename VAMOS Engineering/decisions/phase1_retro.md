# Phase 1 회고 (D1 검증) — 2026-06-04

> A11(STRATEGY_07) Phase 회고 · 판정: **D1 PASS (CONDITIONAL)**

## 잘된 것 3가지
1. **결정론 엔진으로 재현성 확보**: 1-2~1-5·1-9를 `_d1/` Python 스크립트로 구현 → 동일 입력=동일 출력. 재실행 핵심 지표 동일(MISMATCH 0 / BROKEN 1 / OPEN 5 / SDV4-WARN 1, 2026-06-05 감사 정정 후). 각 산출물에 skill_version(+집계물 input_hash) 기록.
2. **거짓 양성(false positive)을 정직하게 추적·해소**: 1-3 초기 MISMATCH 4건을 하나씩 원문 검증 → 모두 (a) 표기차(0.40=0.4) (b) 동음이의(통계 alpha·타 벤치 win-rate) (c) 음성 테스트(ValueError 픽스처) (d) 내 정본 가정 오류(LOCK-AX-06은 α=0.3 BM25 보완쌍)임을 확인하고 탐지기를 실제 정본에 맞게 교정. 충돌을 숨기지 않고 근거로 해소.
3. **R16 착시 차단**: 모든 산출물을 디스크 실파일로 검증(7 핵심 + 36 validation + 36 crossref). 보고서 ✅과 산출물 존재를 분리 확인.

## 안된 것 3가지
1. **스킬이 프롬프트형(AI)인데 대상이 거대(68+2,654 .md)** → 문자 그대로의 스킬 실행 불가. 결정론 스크립트로 충실 구현했으나, AI 의미검증(SSV/SV)은 샘플·개념대조 수준으로 축소.
2. **1-5 SDV-2/5/6 입력 부재**: SOT2 SC-JSON 추출층(`_extractions/`)이 존재하지 않아 추출카운트·스키마타입·canonical-owner 검증은 N/A 처리(허위 PASS 금지). SDV-1/3/4/7만 직접 수행.
3. **사전 존재 비차단 이연 잔존**: 5-3 C-04~C-08(LOCK 매핑)은 2026-04-03부터 OPEN. D1에서 신규 해소 못 하고 이연 등록. (※6-5 W-CB는 1차 D1에서 이연으로 잘못 분류했으나 실제로는 v1.3에서 RESOLVED — 2026-06-05 감사로 정정, 아래 포스트모템 참조.)

## 다음에 바꿀 것 1가지
- **추출층(_extractions/) 정식화**: Phase 2 진입 전 SOT2 SC-JSON 추출을 생성하면 SDV-2/5/6가 실측 가능해져 1-5가 완전체가 된다. (또는 D1 스킬 정의에서 추출층 의존을 명시적 선택 게이트로 분리.)

## 포스트모템 (이연 항목 근본원인 + 재발방지)
- **근본원인**: 5-3 이연은 도메인 경계·교차 정본 매핑이 Phase 1 시점에 미확정 → 도메인 소유자가 '비차단(4-2 선례)'으로 의도적 deferral. D1의 결함이 아니라 거버넌스상 미결 항목. (6-5는 v1.3에서 이미 RESOLVED — 포스트모템 #2 참조.)
- **재발방지**: 이연 4항목을 `D1_RESULTS_INDEX.md §3 이연대장` + `D1_VERDICT.json deferral_register`에 전수 등록(누락 0). 자동 정본 변경 0(RULE>PLAN>DESIGN LOCK 위반 회피). Phase 2/3 협의 시 정본 우선순위로 해소 후 D1 재판정 트리거.
- **검증 무결성**: SOT 68 = 67 OK / 1 CHANGED(readiness review 문서, D2.0 spec 아님). 신규 `integrity_snapshot.json`(2,654 파일)이 D2 상시 감시의 새 기준선.

## 포스트모템 #2 — 2026-06-05 감사 정정 (검증자 카운트 결함)
- **배경**: ultracode 멀티에이전트(34) read-only 재검증에서 1차 D1(2026-06-04) 감사 레지스터의 카운트 결함 발견. **게이트 판정(PASS_CONDITIONAL)·value gates는 불변** — 결함은 "비차단 이연을 세는" 감사 레이어에 국한.
- **근본원인 3종 (엔진 로직)**:
  1. `count_open_conflicts`가 RESOLVED 판정을 **행 전체 텍스트**에 적용 → 5-3 C-07(상태=OPEN이나 본문에 타 충돌 'W-05 RESOLVED' 인용)을 false-negative로 누락. (다른 충돌의 RESOLVED를 인용하는 모든 OPEN 행을 삼키는 일반 결함.)
  2. 동일 결함의 반대 방향: 6-5 W-CB가 CONFLICT_LOG **v1.3 §8.1에서 OPEN 0(RESOLVED)** 인데, append-only 보존된 옛 본문 행의 literal 'OPEN'을 읽어 OPEN으로 2회 카운트.
  3. `check_1_2`가 `active=0`·`resolution='RESOLVED'`를 **하드코딩** → 외부 v13 verdict 주장 복사(자체 재검증 아님). `EXTERNAL_TGT`가 디스크 해소 전 분류 → 실존 내부링크 2건 오분류.
- **정정(재발방지)**: ① RESOLVED/WONTFIX를 **status 컬럼 셀**에만 한정 + **conflict-id 단위 집계(dedupe)** + 최신 전환행 인식, ② `check_1_2` active를 fix-proposal 원장에서 산출하고 resolution을 FIXED/NO_FIX/DEFERRED로 구분, ③ `EXTERNAL_TGT`는 디스크 해소 실패 시에만 적용. → **OPEN 6→5(전부 5-3), 6-5=0, SDV-4 WARN 2→1, EXTERNAL 6→4, 1-2 RESOLVED 11/NO_FIX 1/DEFERRED 2**.
- **교훈**: "외부 verdict 복사 금지 — 결정론 게이트는 원본에서 자체 재계산." append-only 충돌로그는 **최신 버전 섹션이 본문 literal을 supersede**함을 카운터가 반영해야 함. 적대적 멀티에이전트 재검증이 단일 작성자의 카운트 맹점을 잡아냄.
