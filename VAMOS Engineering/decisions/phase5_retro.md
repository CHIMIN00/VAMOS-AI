# Phase 5 (V0 검증 + GO/NO-GO) 회고 — P5-1 (2026-06-13)

> A11 형식 · tag v0-release · 게이트 wf_0229a151-bb3 (9 에이전트)

## 판정: V0 GO (CONDITIONAL→GO, PHASE5-DEC-001 스코프 환원 + 인간 사인오프)

## 잘된 것 (3)
1. **D3 정합 DRIFT 0을 실행으로 증명** — 파일 존재가 아니라 roundtrip 25/25(serde deny_unknown_fields)·registry 런타임 카운트 123/36/23=SOT·LOCK 23/0·score_to_level 실행으로 재도출(III-3). "있음=정합" 착시 회피.
2. **멱등성(A17) 근본원인 규명** — seed=42·temp=0에서도 최초 실패 → Ollama 프롬프트 전환 직후 KV-cache 상태 잔여가 첫 호출을 갈리게 함을 격리 디버깅으로 발견, per-prompt 워밍업으로 결정성 확립(2회 안정 재현). 표면적 "비결정" 단정 대신 메커니즘 규명.
3. **게이트가 스코프 환원을 정직하게 잡음** — 무리한 16/16 GO 단언 대신, 6건이 권위 근거로 정당하나 미기록임을 적대검증(go_refuted=true)이 포착 → CONDITIONAL-GO → ADR 기록 + 인간 사인오프로 수렴. 착시 GO 방지.

## 안 된 것 / 위험했던 것 (3)
1. **하네스 false-skip 함정 반복** — check_config_lock(dir 인자→"부재 스킵 OK" 착시)·vamos_lint(리포루트→구버전 산출물 248 오탐)·poetry run stdout 간헐 버퍼링. 무인자/무경로 실행이 거짓 GREEN을 만들 뻔함. 매번 명시 경로·backend cwd 필요.
2. **§2.8 vs §9.1 분모 발산을 사전에 못 박지 못함** — 두 16표가 다른 항목 집합(Chroma/Alembic 처리 상이)인데 P5-1 진입 전 reconcile 없이 진행 → 게이트에서 6건 스코프 충돌로 표면화. 사전 분모 고정이 더 빨랐음.
3. **II-6 교차모델 미가용** — GPT/Gemini/Fable 접근 불가로 게이트 교차감사를 Opus 앙상블+인간 사인오프로 대체. 자기참조 회피는 했으나 진짜 외부 교차모델 부재는 잔여 리스크(V1 게이트 6-9서 복구 필요).

## 다음에 바꿀 것 (1)
**Phase 진입 게이트에 "분모 단일화 + 하네스 호출규약" 사전 STEP 명시** — (a) 검증 대상 체크리스트가 복수 출처에 발산하면 진입 전 단일 정본으로 reconcile(ADR), (b) 게이트 도구는 항상 명시 경로/cwd로 호출(false-skip 차단)을 프롬프트 STEP 1에 못 박는다. P6-0부터 적용.

## Phase 6 입력
- V0 GO 완료 · tag v0-release. P6-0(V1 준비 게이트) 진입 허용.
- §C 잔여(I-1~I-9) V1 집행: P6-0서 전건 재확인(특히 I-1 CI 배선·I-6 골든·I-7 퍼징은 PHASE4-DEC-012+ ADR 선행).
- 이연 항목 활성화(V1): Chroma 벡터/RAG(I-2)·graph_db·Alembic(스키마 진화 시)·24규칙 잔여 코드화·I-4·NeMo/Guardrails-AI L1/L2.
- II-6 교차모델 복구(6-9 게이트) 우선.
- Eval(QoD 0.8471<0.85): V1 RAG+main_model로 30일 운영 QoD≥0.85 목표(A9).
