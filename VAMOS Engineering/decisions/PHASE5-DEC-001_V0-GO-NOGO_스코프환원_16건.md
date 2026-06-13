# PHASE5-DEC-001 — V0 GO/NO-GO §2.8 16건 스코프 환원 (6건 V0-deferred/code-equiv/programmatic)

> **결정일**: 2026-06-13 (P5-1, 5-8 게이트) · **포맷**: A6 · **우선순위**: Must (릴리스 판정) · **상태**: 확정
> **승인**: 인간 사인오프(VI-2/VI-1) — II-6 교차모델(GPT/Gemini/Fable) 미가용에 따른 정규 폴백(PHASE4-DEC-011 §B-6, H9-3). Opus 페르소나 대체 아님.
> **게이트 근거**: ultracode 워크플로 wf_0229a151-bb3 (9 에이전트·III-3 독립재도출 + II-1 적대 3 + VI-3 완전성, loop-until-dry) → CONDITIONAL-GO

## 결정

READINESS §2.8 V0 GO/NO-GO 16건 중 **6건(2·7·11·13·15·16)**은 리터럴 문구 그대로는 미충족이나, **V0 스코프상 정당한 이연(V1)·코드수준 등가·programmatic 초기화**로 충족된 것으로 **공식 기록**한다. 나머지 10건은 디스크/실행 실측 충족. 본 결정으로 게이트 CONDITIONAL-GO → **GO**, `git tag v0-release` 진입을 승인한다.

| # | 항목 | 리터럴 상태 | V0 환원 판정 | 권위 근거 |
|---|------|------------|-------------|----------|
| 2 | BASE-1.3 24규칙 코드매핑 | 안전핵심 부분집합만 코드화(Non-goal 7 + RA_NEVER 10 + cost downshift) | **부분 매핑 = V0 충족** — 안전-차단 핵심은 코드, 잔여(prompt/RBAC/schema/RAG/logging/config-load-order)는 config·skeleton·prompt 수준 등가 | P4-0 결정⑩(Guardrails V0=코드수준등가) · READINESS §9.1 대안 16표가 24규칙 전수 코드화를 V0 요건으로 열거 안 함 |
| 7 | I-1~I-5 + I-19 스켈레톤 | I-1/2/3(memory_store)/5/19 실재, **I-4 전용 파일 부재** | **충족** — I-4(Multimodal Interpreter)는 V1:ON | D2.0-01 §5.6 L621 "I-4 ... V1:ON / V2:ON / V3:ON" (V0 비범위) |
| 11 | Guardrails L1+L2 (NeMo+Guardrails AI) | NeMo/Guardrails-AI 미설치, safety+5-Gate+config LOCK 3계층으로 대체 | **코드수준 등가 = V0 충족** | P4-0 결정⑩ · §2.7 "최소 구현" · pipeline.py L9-10/L97 3계층 명시 |
| 13 | data/ 5서브디렉(sqlite/chroma/logs/graph/backups) | logs/sqlite 2종만 런타임 생성 | **V0 활성분 충족** — chroma/graph는 V1(vector_db/graph_db '(V1)'), backups는 첫 백업 시 생성 | config.v1.toml L37/44 '(V1)' · PHASE_B2 scaffold가 data subdir 미열거 · logger.py:52 mkdir 멱등 |
| 15 | Chroma 임베디드 초기화 | vamos_core chromadb import 0건 | **V1 이연** | config vector_db backend='chroma' # LOCK (V1) · V2-005 Chroma→Qdrant=V2 · PART2 V0-STEP-5는 L0 SQLite/JSONL/config만 요구 |
| 16 | SQLite 스키마 + Alembic 초기 마이그레이션 | SQLite 스키마 실재(vamos.db, CREATE TABLE IF NOT EXISTS, init() 검증), **Alembic 미채택** | **SQLite 충족 + Alembic programmatic 대체** | memory_store.py aiosqlite 멱등 초기화 · PART2 V0 의존성 목록(L402~411)이 alembic 미포함 · READINESS §9.1 'SQLite 초기화'만 열거(Alembic 무) |

## 이유 (Why)

- V0 = **스켈레톤 릴리스**(§2.7: I-3 L0 only, RAG/벡터 stub, Guardrails 최소 구현). 위 6건의 "리터럴 미충족"은 능력 결손이 아니라 **V0/V1 스코프 경계**의 결과이며, 각 항목은 별도 권위 출처(PART2 V0-STEP-5·config '(V1)' 표지·P4-0 ⑩·D2.0-01 I-4 V1:ON·DEC-007·READINESS §9.1)가 V0 비범위/등가를 이미 지지한다.
- 문제는 이 환원이 **§2.8 분모에 대해 명시 기록된 결정이 없어** 게이트가 리터럴 16/16을 단언할 수 없었던 점(III-3 보수 원칙). 본 ADR이 그 기록을 제공한다.
- §2.8 자체가 §9.1(다른 16표: 'Ollama+Chroma+SQLite 초기화' 1항 통합·Alembic 무)과 발산 — §2.8이 일부 항목을 과명세. 본 결정은 §2.8을 분모로 유지하되 6건의 V0 해석을 고정한다.

## 게이트 본체 PASS 실측 (CONDITIONAL의 "본체")

- D3 DRIFT 0 (모듈 25↔8 · 스키마 25/25 왕복 · Registry 123/36/23=D2.1-D2 §5.1 · LOCK 23/0)
- 배포 무결성 A24 3단계 PASS · 멱등성 A17 3회 동일 · Defense 3계층 독립 · confidence_score 3곳
- 하네스: mypy strict 26/0 · pytest 118 · roundtrip 25/25 · LOCK 23키 위반 0 · lockfile drift 0 · vamos_lint backend 0

## 검토한 대안

- **리터럴 충족 요구(NO-GO)** — Chroma 초기화·Alembic·24규칙 전수·I-4·NeMo/Guardrails-AI 실구현 후 GO. 기각: V0 스코프(스켈레톤) 위반 + Phase 4 복귀 = 설계 의도 역행(벡터/RAG는 V1 정본).
- **무기록 GO** — 기각: III-3/게이트 보수 원칙 위반(분모 대비 미기록 환원은 16/16 착시).
- **채택: 기록된 스코프 환원 + 인간 사인오프** — 권위 근거를 §2.8에 명시 링크, II-6 미가용분은 인간(VI-2/VI-1)이 수용.

## 비차단 후속 (flag)

- PART2 L1621 'EventType 134' = stale 교차참조(D2.1-D2 §5.1 정본 123·코드 123) → 문서 정정 권고.
- PROGRESS.md L186/로드맵 L443 'V0 16건=PART2 §7.1' 라벨 = 부정확(디스크 검증원 = READINESS §2.8) → 정정.
- data/backups 디렉토리 = backup_enabled=true이나 미생성 → 첫 백업 시 생성/V1 점검.

## 집행 추적 (2026-06-13, 누락 방지 — §C 선례 동일)

> 이연 6건이 P6-0 핸드오프 노트(PROGRESS "P6-0 입력 ③"·phase5_retro)에만 의존하지 않도록, **로드맵 6-0(P6-0) 행에 6건 활성화 배정을 직접 cross-ref로 등재**(DEC-011 §C 보류대장이 6-0/6-5/6-7에 박힌 선례 동일). 배정: item 2→6-1 D1'/6-3 · item 7(모듈 I-4 Multimodal, §C 프로퍼티-테스트 I-4와 별개)→6-3 CORE · item 11(NeMo+Guardrails AI)→6-3/6-4 · item 13(chroma·graph·backups dirs)→6-4/6-6/6-3·6-4 · item 15(Chroma)→6-4 · item 16(Alembic)→6-1 A23. → 6건이 핸드오프 + 로드맵 작업표 양쪽에 등재되어 P6-0서 전건 게이트화.

본 ADR은 A6 준수 산출물이며 PROGRESS.md·로드맵 추적표에서 참조한다.
