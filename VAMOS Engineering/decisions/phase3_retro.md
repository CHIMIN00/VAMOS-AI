# Phase 3 회고 (A11) — 2026-06-12

> R1 런타임 설계 + X1 횡단 전략. 세션: P3-0(게이트) → P3-1(R1 10결정) → P3-2(X1 4전략 + 계획서 2 + Gate).
> 산출: ADR 18건(GATE-01~08 + DEC-001~010) + runtime_decisions.md + 6 전략/계획서. LOCK 재정의 0 · 신규 3건.

## 잘된 것 3

1. **정본 우선 + 무발명 원칙 완주**: R1 10결정 전부 SOT 정본 추인(D2.0-02/05/06/07·PHASE_B1·STRATEGY_05) — 기존 LOCK 재정의 0, 신규 LOCK은 A21/A22/A25 3건만(정본에 미정의였던 부분). 결정문서 7종이 기존 정본을 대체하지 않는 "요약+바인딩" 위상(L293)을 전 산출물에서 유지.
2. **P3-0 게이트가 R1을 막힘없이 통과시킴**: 분모(V0=8/V1=32/Must=11)·V1 귀속·MCP max_retries 단일 표기를 게이트에서 선확정해, P3-1/P3-2에서 분모 충돌·표기 이형으로 멈추는 일이 0. GATE-07d(MCP)·GATE-03(분모)이 DEC-007·계획서에 그대로 흘러듦.
3. **드리프트 능동 탐지·교정**: P3-1에서 STRATEGY_05 §3.1 게이트 순서 오기(Cost↔Approval)를 정본 대조 중 적발·교정. D2.1-D2에 confidence 필드 부재를 실측으로 확인해 A25를 "신규 추가"로 정직하게 분류(없는 것을 있다고 하지 않음).

## 안된 것 3

1. **git autocrlf EOL 손상 사고 (P3-0)**: main ff 체크아웃 왕복 × 시스템 autocrlf=true가 824파일 작업 트리를 CRLF로 재작성. 전수 복구(blob 무변화·diff 0)했으나, 게이트 집행이 부수 사고를 유발한 것은 위험 신호. → repo-local autocrlf=false + fetch 방식 동기화로 재발 방지 규칙 확정([[git-eol-autocrlf-checkout-hazard]]).
2. **STRATEGY_08 매트릭스 "26" 잔존**: R2a 셀이 "V1 26개 활성" 구집계를 유지 — GATE-03에서 V1 CORE=32 확정했으나 매트릭스 본문 미수정(로드맵 6-3이 마스터로 PART2 32 우선 선언 중). 계획서에서 32로 명기·주석했으나 매트릭스 자체 정합은 잔여(비차단).
3. **결정문서 위상의 반복 설명 비용**: "요약+바인딩, 정본 무대체"를 매 산출물 헤더에 반복 기재해야 했음. F-17(검증보고서)이 지적한 이중 정본 위험을 방지하려는 것이나, 위상 선언을 1곳(예: 로드맵 L293)에 집중하고 참조만 하는 방식이 더 간결했을 수 있음.

## 바꿀 것 1

- **Phase 4 진입 전 EOL/저장소 위생 사전 점검을 게이트화**: P4-0(스킬 점검) 세션에 "autocrlf=false 확인 + ls-files --eol 인벤토리 기준선" 항목을 추가해, 코드 생산이 시작되는 Phase 4에서 EOL 회귀가 누적되지 않도록 한다.

## 포스트모템 — autocrlf EOL 손상 (P3-0)

- **증상**: 동기화 복사본 크기 이상 → ls-files --eol에서 i/lf w/crlf 1,406건
- **근인**: 시스템 gitconfig `core.autocrlf=true` + 브랜치 체크아웃이 LF blob을 CRLF로 smudge
- **영향 범위**: 824파일 작업 트리 (커밋/blob은 무손상 — LF 정규화 유지)
- **복구**: autocrlf=false 설정 → 06-04 integrity 해시 ↔ blob LF/CRLF 양방 SHA 대조 + backup_session5 실측으로 역사적 EOL 기계 판정 → LF군 725 blob 복원, CRLF군 27 무손상 확인 → 교차검증(1-1 상세명세 3AE9E739 PASS) → diff 0
- **재발 방지**: ① repo autocrlf=false 영속 ② main 동기화 = `git fetch . <branch>:main`(체크아웃 금지) ③ P4-0 게이트에 EOL 기준선 점검 추가 ④ 역사적 CRLF/LF 이중 상태 ~684파일 정규화는 P4-0 결정 후보

## Phase 3 → 4 인수인계 확인
- ☑ runtime_decisions.md → R2a (runtime_eng_plan §2)
- ☑ IPC+A20(DEC-006) → B2c (4-1)
- ☑ X1 4전략 → X2 (cross_eng_plan §2)
- ☑ LOCK Registry §8 신규 3건 → Phase 4 config(4-5)/코어(4-2) 구현 바인딩
