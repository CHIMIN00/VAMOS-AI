# Phase 1 회고 (D1 검증) — 2026-06-04

> A11(STRATEGY_07) Phase 회고 · 판정: **D1 PASS (CONDITIONAL)**

## 잘된 것 3가지
1. **결정론 엔진으로 재현성 확보**: 1-2~1-5·1-9를 `_d1/` Python 스크립트로 구현 → 동일 입력=동일 출력. 2회 재실행 핵심 지표 동일(MISMATCH 0 / BROKEN 1 / OPEN 6 / SDV4-WARN 2). 각 산출물에 timestamp+input_hash+skill_version 기록.
2. **거짓 양성(false positive)을 정직하게 추적·해소**: 1-3 초기 MISMATCH 4건을 하나씩 원문 검증 → 모두 (a) 표기차(0.40=0.4) (b) 동음이의(통계 alpha·타 벤치 win-rate) (c) 음성 테스트(ValueError 픽스처) (d) 내 정본 가정 오류(LOCK-AX-06은 α=0.3 BM25 보완쌍)임을 확인하고 탐지기를 실제 정본에 맞게 교정. 충돌을 숨기지 않고 근거로 해소.
3. **R16 착시 차단**: 모든 산출물을 디스크 실파일로 검증(7 핵심 + 36 validation + 36 crossref). 보고서 ✅과 산출물 존재를 분리 확인.

## 안된 것 3가지
1. **스킬이 프롬프트형(AI)인데 대상이 거대(68+2,654 .md)** → 문자 그대로의 스킬 실행 불가. 결정론 스크립트로 충실 구현했으나, AI 의미검증(SSV/SV)은 샘플·개념대조 수준으로 축소.
2. **1-5 SDV-2/5/6 입력 부재**: SOT2 SC-JSON 추출층(`_extractions/`)이 존재하지 않아 추출카운트·스키마타입·canonical-owner 검증은 N/A 처리(허위 PASS 금지). SDV-1/3/4/7만 직접 수행.
3. **사전 존재 비차단 이연 잔존**: 5-3 C-04~C-08(LOCK 매핑) + 6-5 W-CB(소유권)는 2026-04-03부터 OPEN 상태로 Phase 4까지 진행됨. D1에서 신규 해소 못 하고 이연 등록.

## 다음에 바꿀 것 1가지
- **추출층(_extractions/) 정식화**: Phase 2 진입 전 SOT2 SC-JSON 추출을 생성하면 SDV-2/5/6가 실측 가능해져 1-5가 완전체가 된다. (또는 D1 스킬 정의에서 추출층 의존을 명시적 선택 게이트로 분리.)

## 포스트모템 (이연 항목 근본원인 + 재발방지)
- **근본원인**: 5-3/6-5 이연은 도메인 경계(소유권)·교차 정본 매핑이 Phase 1 시점에 미확정 → 도메인 소유자가 '비차단(4-2 선례)'으로 의도적 deferral. D1의 결함이 아니라 거버넌스상 미결 항목.
- **재발방지**: 이연 5항목을 `D1_RESULTS_INDEX.md §3 이연대장` + `D1_VERDICT.json deferral_register`에 전수 등록(누락 0). 자동 정본 변경 0(RULE>PLAN>DESIGN LOCK 위반 회피). Phase 2/3 협의 시 정본 우선순위로 해소 후 D1 재판정 트리거.
- **검증 무결성**: SOT 68 = 67 OK / 1 CHANGED(readiness review 문서, D2.0 spec 아님). 신규 `integrity_snapshot.json`(2,654 파일)이 D2 상시 감시의 새 기준선.
