# VAMOS v13 Enhanced Pipeline — 52 스킬 통합 전수 재검증 계획서

> **버전**: v13.3.0-ENHANCED
> **작성일**: 2026-03-20
> **기반**: v13_plan.md v13.2.0 + TOOL_GUIDE 52개 스킬 통합
> **원칙**: 하나도 빠짐없이 전수 재실행 + 52개 스킬로 검증 강화 + 최대 병렬성

---

# 0. 52 스킬 → v13 Phase 매핑 총괄

## 0.1 Layer별 스킬 배치

```
Layer A (결정론적, AI 판단 0%):
  /validate DV-1~DV-10    → 모든 EA/CM JSON 저장 시 자동 실행
  /symbolic-verify         → LOCK/FREEZE 값 기호 비교
  /json-repair             → JSON 구조 오류 자동 복구
  /integrity               → SHA256 해시 + 구조 무결성
  /deterministic           → 프롬프트 해시 비교 (동일 입력 → 동일 출력 확인)
  /deep-diff               → 버전 간 정밀 diff
  /json-diff               → JSON 구조 변경 추적
  /korean-nlp              → 한국어 형태소 분석 (용어 일관성)

Layer B (AI 의미적 검증):
  /audit                   → 적대적 감사 (Devil's Advocate)
  /hallucination-check     → 환각 탐지 (source_text ↔ SOT 직접 대조)
  /fact-audit              → 사실 기반 검증 (숫자, 출처)
  /validate SV-1~SV-3      → 의미적 정확성 + 완전성 + 키 적절성
  /sot-check               → SOT 원본 직접 대조
  /cross-examine           → 교차 심문 (모순 탐지)
  /consensus               → 다중 관점 합의
  /completeness-map        → 오류 카테고리 × 도구 커버리지 매트릭스

Layer C (교차 모델/외부):
  /cross-model             → 다른 AI 모델과 교차 검증 (API 키 필요)
  /hhem-verify             → NLI 기반 충실성 검증
  /patronus-check          → Patronus API 검증 (API 키 필요)
  /minicheck               → MiniCheck NLI 로컬 검증
  /exa-verify              → Exa 검색 기반 외부 사실 확인 (API 키 필요)

Layer D (사람 확인):
  /final-review            → 최종 리뷰 (Mode A/B/C/D)
  /quality-gate            → GOLD/SILVER/BRONZE/REJECT 판정
  /report                  → 종합 보고서 생성
  /debate                  → 토론 모드 (찬반 논증)
```

## 0.2 인프라/지원 스킬

```
데이터 관리:
  /sot-cache               → SOT 파일 캐싱 (68개 파일 89,374줄 처리)
  /sot-search              → SOT 전문 검색 (Whoosh 인덱스)
  /sot-rag                 → SOT 기반 RAG 컨텍스트 주입
  /sot-graph               → SOT 관계 그래프 (Neo4j)
  /sot-conflict            → SOT 간 충돌 탐지 (ontology 포함)

추적/관측:
  /trace                   → 실행 추적 (Langfuse)
  /lineage                 → 데이터 계보 추적 (OpenLineage)
  /phoenix-observe         → 실행 관측 (Phoenix)

평가:
  /eval-ea                 → EA 추출 결과 평가 (DeepEval)
  /ragas-eval              → RAG 품질 평가
  /golden-set              → 정답 데이터셋 관리 (reverify 포함)
  /prompt-test             → 프롬프트 회귀 테스트 (promptfoo)
  /confidence              → 신뢰도 보정
  /giskard-scan            → 취약점 사전 스캔

보안/보호:
  /input-guard             → 입력 보안 (mask-pii 포함)
  /llama-firewall          → LLM 방화벽
  /guardrails-validate     → Guardrails AI 검증

버전 비교:
  /artifact-diff           → 산출물 버전 간 정밀 비교 (B-13)

파이프라인:
  /extract                 → SOT→JSON 추출
  /cross-match             → 교차 매칭 (C1~C8)
  /delta-apply             → 델타 적용
  /phase-run               → Phase 오케스트레이션
  /gpt-cache               → 응답 캐싱 (비용 절감)

메타 평가:
  /eval-audit              → 평가 도구 자체 감사
  /write-judge-prompt       → 판정 프롬프트 작성
  /validate-evaluator       → 검증기 검증
  /dspy-optimize           → DSPy 프롬프트 최적화
  /docling                 → 문서 구조 파싱
```

---

# 1. Tier 구분 및 사전 준비

## Tier 1: Claude 내장 (설치 불필요, 즉시 사용) — 23개

```
/extract, /validate, /audit, /sot-check, /quality-gate, /cross-match,
/delta-apply, /phase-run, /report, /integrity, /sot-cache,
/hallucination-check, /fact-audit, /cross-examine, /consensus,
/debate, /json-diff, /golden-set, /symbolic-verify, /final-review,
/completeness-map, /sot-conflict, /deterministic
= 23개 스킬 (순수 Claude 로직, 외부 의존성 없음)
```

## Tier 2: pip install 필요 (무료) — 23개

```
스킬 목록 (23개):
  Layer A 의존: /json-repair (json_repair), /deep-diff (deepdiff), /korean-nlp (kiwipiepy)
  Layer C 로컬: /hhem-verify (sentence_transformers), /minicheck (NLI 로컬)
  데이터 관리:  /sot-search (whoosh), /sot-rag (sentence_transformers)
  평가:        /eval-ea (deepeval), /ragas-eval (ragas), /prompt-test (promptfoo),
               /confidence (calibration), /giskard-scan (giskard)
  보안:        /input-guard (mask-pii), /llama-firewall (llama-firewall),
               /guardrails-validate (guardrails)
  버전 비교:   /artifact-diff (deepdiff)
  파이프라인:  /gpt-cache (gptcache)
  메타 평가:   /eval-audit, /write-judge-prompt, /validate-evaluator,
               /dspy-optimize (dspy), /docling (docling)
  관측:        /phoenix-observe (phoenix, pip install arize-phoenix)

설치 상태 (2026-03-21 실측 기준):
  OK (29개 패키지): guardrails, deepeval, json_repair, deepdiff, ragas,
                    kiwipiepy, docling, dspy, sentence_transformers,
                    whoosh (v2.7.4), marquez-python (v0.50.0) 등
  OK (1개 패키지): phoenix (v13.15.0) — starlette v0.52.1로 충돌 해결됨
  N/A (1개 패키지): llama_firewall — PyPI 미등록, /input-guard로 대체 가능

사전 설치 필요: 없음 (전수 설치 완료)
  ※ llama_firewall: Meta 미공개 패키지. /input-guard (LLM Guard 기반)가 동일 역할 수행
  ※ 패키지명 주의: marquez_client → pip install marquez-python (PyPI 패키지명 상이)
```

## Tier 3: API 키 필요 (선택) — 3개

```
/cross-model: OpenAI API 키 (GPT-4o 교차 검증)
/exa-verify: Exa API 키 (외부 사실 확인)
/patronus-check: Patronus API 키
→ 없어도 Tier 1+2로 33개 CAT 전부 커버 가능
  (근거: TOOL_GUIDE_46.md 커버리지 매트릭스 — 33개 오류 카테고리 × Tier 1+2 도구 매핑 전수 확인,
   FINAL_CHECK FR-B04 참조)

[사용자 승인 결정 — 2026-03-21]:
  선택적 사용 (비용 최적화):
    /exa-verify      → Phase 4 세션 26 (GT-4 외부사실 검증)에서만 사용
                       사유: Claude 학습 컷오프 이후 정보(라이브러리 최신 버전, API 가용성) 검증 불가
    /cross-model     → Phase 8 세션 52 (최종 판정)에서 1회 사용
                       사유: Claude 자기맹점 보완, 최종 판정 신뢰도 강화
    /patronus-check  → 사용 안 함
                       사유: /minicheck + /hhem-verify (Tier 2 로컬 NLI)로 동일 기능 충분 커버
  예상 비용: ~$3-8 (전 Phase 사용 시 ~$100+ 대비 95% 절감)
    /exa-verify ~$1-3 (50-100 검색 쿼리)
    /cross-model ~$2-5 (GPT-4o 1회 교차 검증)
```

## Tier 4: 서버 인프라 (선택) — 3개

```
/sot-graph: Neo4j (Docker 또는 Neo4j Desktop)
/lineage: Marquez 서버 (Docker)
/trace: Langfuse (클라우드 또는 셀프호스팅)
→ 없어도 진행 가능, 있으면 추적/관측/데이터 계보 강화
```

---

# 2. Phase 0: SOT 68개 파일 내부 전수 정합성 검증

> v6~v12에서 한 번도 수행하지 않은 신규 검증
> 52 스킬 중 최대 투입

## 2.1 Phase 0-A: SOT 전수 추출 (15 에이전트)

```
실행 흐름:
  1. /sot-cache all          → 68개 SOT 파일 인덱싱 + 캐싱
  2. /input-guard scan       → SOT 파일 입력 보안 스캔 (PII 확인)
  3. /extract EA-1~EA-15     → 15개 에이전트 병렬 추출
     ├→ [자동 Hook] deterministic_validator.py (DV-1~DV-7)
     ├→ [자동 Hook] block_invalid_ea.sh (CRITICAL 시 저장 차단)
     └→ /validate --layer-a    → Layer A 결정론적 검증
  4. /korean-nlp normalize   → 한국어 용어 정규화
  5. /quality-gate EA-{1~15} → 각 추출물 GOLD/SILVER/BRONZE/REJECT

병렬 구조 (3그룹 × 5에이전트):
  Group 1 (세션 1): EA-1~EA-5  (CLAUDE.md, BASE, PLAN, MASTER, D2.0-01/02)
  Group 2 (세션 2): EA-6~EA-10 (D2.0-03~08, D2.1, PHASE_B1~B7)
  Group 3 (세션 3): EA-11~EA-15 (SPEC 5개, STEP7, READINESS, BEGINNER)

52스킬 투입:
  - /extract (추출)
  - /validate (DV검증)
  - /sot-cache (캐싱)
  - /input-guard (보안)
  - /korean-nlp (용어)
  - /quality-gate (판정)
  - /json-repair (오류 복구)
  - /integrity (무결성)
  - /docling (문서파싱, 복잡한 표 구조 SOT용)
  - /gpt-cache (반복 호출 캐싱)

세션: 3개 (병렬), 산출물: EA-{1~15}.json + DV 결과 + QG 판정
```

## 2.2 Phase 0-B: 크로스 매칭 (8 에이전트)

```
선행조건: Phase 0-A 전수 SILVER 이상

실행 흐름:
  1. /cross-match CM-1~CM-8  → 8개 유형별 크로스 매칭
  2. /symbolic-verify         → LOCK/FREEZE 값 기호 대조
  3. /sot-conflict scan       → SOT 간 충돌 전수 탐지 (ontology 포함)
  4. /deep-diff               → 파일 간 값 정밀 diff

병렬 구조 (2그룹 × 4에이전트):
  Group A (세션 4): CM-1(동일값), CM-2(카운트), CM-3(분류), CM-4(명칭)
  Group B (세션 5): CM-5(범위), CM-6(버전), CM-7(수식), CM-8(참조)

52스킬 투입:
  - /cross-match (매칭)
  - /symbolic-verify (기호)
  - /sot-conflict (충돌)
  - /deep-diff (diff)
  - /json-diff (JSON비교)
  - /fact-audit (사실검증)
  - /completeness-map (커버리지)

세션: 2개 (병렬), 산출물: CM-{1~8}.json
```

## 2.3 Phase 0-C~F: 확정 + 수정 + 재검증

```
세션 6: 불일치 확정 + 심각도 분류
  - /cross-examine            → 교차 심문으로 오탐 제거
  - /consensus                → 다중 관점 합의
  - /hallucination-check      → 환각 여부 확인
  - /confidence               → 신뢰도 보정

세션 7: SOT 수정안 도출 + 적대적 재검증 + 반영
  - /audit                    → 적대적 감사
  - /golden-set reverify      → 정답 데이터 기반 재확인
  - /delta-apply              → 수정 반영
  - /integrity                → 수정 후 해시 검증

완료 조건 (PC-1~PC-6):
  PC-1: 68개 파일 전수 읽기 100%
  PC-2: C1~C8 유형별 크로스 매칭 전수 완료
  PC-3: 기존 3건 불일치 (INC-001/002/003) 해소
  PC-4: 신규 CRITICAL 0건 (전건 수정 후 — D-2)
  PC-5: 적대적 재검증 오판율 ≤10%
  PC-6: 사용자 승인 [CP-USER-1]

세션: 2개 (순차), 산출물: 불일치 목록 + 수정 기록 + 적대적 결과
```

### Phase 0 에이전트 입출력 명세

```
┌──────────┬─────────────────────────────┬─────────────────────────────────────┬──────────────────────────────────────┐
│  세션    │ 에이전트/스크립트            │ 입력                                │ 출력                                 │
├──────────┼─────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────┤
│ 세션 1   │ EA-1~EA-5 (병렬)            │ docs/sot/CLAUDE.md                  │ phase0/extraction/v13_EA01.json      │
│          │                             │ docs/sot/BASE-1.3*.md               │ phase0/extraction/v13_EA02.json      │
│          │                             │ docs/sot/PLAN-*.md                  │ phase0/extraction/v13_EA03.json      │
│          │                             │ docs/sot/VAMOS_MASTER*.md           │ phase0/extraction/v13_EA04.json      │
│          │                             │ docs/sot/D2.0-01*.md, D2.0-02*.md  │ phase0/extraction/v13_EA05.json      │
│          │ 자동 Hook                    │ 각 EA JSON                          │ phase0/extraction/validation/*_dv.json│
│          │                             │                                     │ phase0/extraction/validation/*_qg.json│
├──────────┼─────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────┤
│ 세션 2   │ EA-6~EA-10 (병렬)           │ docs/sot/D2.0-03~08*.md             │ phase0/extraction/v13_EA06~10.json   │
│          │                             │ docs/sot/D2.1-*.md                  │ + validation/*_dv.json, *_qg.json    │
│          │                             │ docs/sot/PHASE_B1~B7*.md            │                                      │
├──────────┼─────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────┤
│ 세션 3   │ EA-11~EA-15 (병렬)          │ docs/sot/*SPEC*.md (5개)            │ phase0/extraction/v13_EA11~15.json   │
│          │                             │ docs/sot/STEP7-*.md                 │ + validation/*_dv.json, *_qg.json    │
│          │                             │ docs/sot/*READINESS*.md             │                                      │
│          │                             │ docs/sot/*BEGINNER*.md              │                                      │
├──────────┼─────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────┤
│ 세션 4   │ CM-1~CM-4 (병렬)            │ phase0/extraction/v13_EA01~15.json  │ phase0/cross_match/v13_CM01.json     │
│          │ C1=동일값, C2=카운트         │ (전체 EA 결과)                       │ phase0/cross_match/v13_CM02.json     │
│          │ C3=분류, C4=명칭             │                                     │ phase0/cross_match/v13_CM03.json     │
│          │                             │                                     │ phase0/cross_match/v13_CM04.json     │
├──────────┼─────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────┤
│ 세션 5   │ CM-5~CM-8 (병렬)            │ phase0/extraction/v13_EA01~15.json  │ phase0/cross_match/v13_CM05~08.json  │
│          │ C5=범위, C6=버전             │                                     │ + validation/v13_CM0X_cm_dv.json     │
│          │ C7=수식, C8=참조             │                                     │                                      │
├──────────┼─────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────┤
│ 세션 6   │ 불일치 확정 에이전트         │ phase0/cross_match/v13_CM01~08.json │ phase0/v13_sot_inconsistency_list.json│
│          │ /cross-examine + /consensus  │ phase0/extraction/v13_EA01~15.json  │ (확정된 불일치 목록 + 심각도 분류)     │
│          │ + /hallucination-check       │                                     │                                      │
├──────────┼─────────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────┤
│ 세션 7   │ 수정 + 적대적 에이전트       │ v13_sot_inconsistency_list.json     │ phase0/v13_sot_fix_proposals.json     │
│          │ /audit + /golden-set         │ docs/sot/* (수정 대상)               │ phase0/v13_sot_delta.json             │
│          │ + /delta-apply + /integrity  │                                     │ phase0/fixes/*_backup_v13.md          │
│          │                             │                                     │ phase0/fixes/v13_sot_corrections.md   │
│          │                             │                                     │ phase0/v13_adversarial_review.json    │
│          │                             │                                     │ phase0/v13_phase0_verdict.md          │
└──────────┴─────────────────────────────┴─────────────────────────────────────┴──────────────────────────────────────┘
```

### Phase 0 → Phase 1 핸드오프

```
Phase 0 출력 → Phase 1 입력:
  필수:
    ✓ phase0/v13_phase0_verdict.md         → PC-1~PC-6 전수 PASS 확인
    ✓ docs/sot/* (수정 완료본)              → Phase 1 이후 모든 Phase의 SOT 기준
    ✓ phase0/extraction/v13_EA01~15.json   → Phase 1 재추출 시 비교 기준
    ✓ phase0/cross_match/v13_CM01~08.json  → Phase 1 크로스 매칭 비교 기준
  참조:
    ○ phase0/v13_sot_delta.json            → SOT 변경 내역 (어떤 값이 바뀌었는지)
    ○ phase0/v13_adversarial_review.json   → 적대적 감사 결과 (주의 항목)
```

### Phase 0 소계

```
세션: 7개 (3병렬 + 2병렬 + 2순차)
에이전트: 26개 (15추출 + 8크로스 + 1확정 + 1수정 + 1적대적)
52스킬 투입: ~20개
```

---

# 3. Phase 1: v6 전수 재실행 (52스킬 강화)

> 원본: 8 Phase0 스크립트 + 5 에이전트 + 적대적 + Phase 2
> 강화: Layer A 자동 검증 + 52스킬 병렬 적용

## 3.1 v6 Phase 0 재실행 (8 스크립트)

```
0-A(테이블) → /validate DV-1 + /symbolic-verify
0-B(산술)   → /validate DV-2,DV-7 + /fact-audit
0-C(Heading) → /validate DV-5
0-D(LOCK)   → /symbolic-verify + /sot-conflict
0-E(수치불일치) → /deep-diff + /cross-match C1
0-F(ID유일성)   → /validate DV-5
0-G(HTML주석)   → /validate DV-1
0-H(헤더카운트) → /validate DV-2

세션 8: Phase 0 전체 1세션 (8스크립트 순차, 스킬 자동 Hook)
```

## 3.2 v6 Phase 1 재실행 (5 에이전트 × 순방향+역방향)

```
v6 Agent 매핑:
  Agent 1 (§6.1~§6.4 ORANGE CORE):
    + /hallucination-check + /sot-check + /cross-examine
  Agent 2 (§6.5~§6.8 BLUE/Storage):
    + /hallucination-check + /sot-check + /sot-rag
  Agent 3 (§6.9~§6.10 Safety/Cost):
    + /symbolic-verify + /guardrails-validate + /input-guard
  Agent 4 (§6.11~§6.13 UI/CI/Version + PART1):
    + /cross-match + /deep-diff + /fact-audit
  Agent 5 (§3~§5 V1/V2/V3 Phase):
    + /completeness-map + /cross-examine + /consensus

병렬: Agent 1~3 동시 (세션 9), Agent 4~5 동시 (세션 10)

P1~P11 오류 패턴 탐지 강화:
  P1(창작원칙)  → /hallucination-check + /sot-check
  P2(필드수오류) → /validate DV-2 + /symbolic-verify
  P3(출처오기재) → /fact-audit + /sot-search
  P4(replace_all) → /json-diff + /deep-diff
  P5(내부산술)  → /validate DV-7 + /fact-audit
  P6(충돌수용)  → /sot-conflict + /cross-examine
  P7(교차정밀도) → /cross-match C1 + /deep-diff
  P8~P11       → /validate + /integrity
```

## 3.3 v6 Phase 1.5 + Phase 2

```
세션 11:
  Phase 1.5 적대적:
    /audit (Devil's Advocate)
    /cross-examine (교차 심문)
    /minicheck (NLI 충실성)
    /eval-ea (결과 평가)
    /golden-set reverify (정답 재확인)

  Phase 2 (Pass 1에서는 발견만):
    발견사항 기록 (수정은 Pass 2에서 통합 수행)
    /artifact-diff (이전 v6 산출물과 비교)

CHECKPOINT (PC1-1 ~ PC1-7, Pass 1: 발견사항 기준):
  PC1-1: v6 8개 Phase 0 스크립트 전수 실행 완료 (0-A~0-H)
  PC1-2: v6 Agent 1~5 순방향(PART→원본) 전수 완료
  PC1-3: v6 Agent 1~5 역방향(원본→PART) 전수 완료
  PC1-4: P1~P11 오류 패턴 탐지 결과 기록 (발견 건수 명시)
  PC1-5: 적대적 감사 완료 — 오판율 ≤15%
  PC1-6: /artifact-diff 이전 v6 산출물 대비 변경점 기록
  PC1-7: 발견사항 JSON 저장 완료 (수정은 Pass 2에서)
```

### Phase 1 에이전트 입출력 명세

```
┌──────────┬──────────────────────────┬──────────────────────────────────┬────────────────────────────────────────┐
│  세션    │ 에이전트                  │ 입력                             │ 출력                                   │
├──────────┼──────────────────────────┼──────────────────────────────────┼────────────────────────────────────────┤
│ 세션 8   │ 0-A~0-H (8스크립트 순차)  │ docs/sot/* (Phase 0 수정본)       │ phase1_v6/phase0/0-A~0-H_result.json  │
│          │                          │ phase0/v13_sot_delta.json        │ phase1_v6/phase0/phase0_summary.json   │
├──────────┼──────────────────────────┼──────────────────────────────────┼────────────────────────────────────────┤
│ 세션 9   │ Agent 1 (§6.1~§6.4)      │ docs/sot/D2.0-01~02*.md          │ phase1_v6/agent1_findings.json         │
│ (병렬)   │ Agent 2 (§6.5~§6.8)      │ docs/sot/D2.0-03~06*.md          │ phase1_v6/agent2_findings.json         │
│          │ Agent 3 (§6.9~§6.10)     │ docs/sot/D2.0-07~08*.md          │ phase1_v6/agent3_findings.json         │
├──────────┼──────────────────────────┼──────────────────────────────────┼────────────────────────────────────────┤
│ 세션 10  │ Agent 4 (§6.11~6.13)     │ docs/sot/PHASE_B*.md             │ phase1_v6/agent4_findings.json         │
│ (병렬)   │ Agent 5 (§3~§5 V1/V2/V3) │ docs/sot/PLAN*.md                │ phase1_v6/agent5_findings.json         │
├──────────┼──────────────────────────┼──────────────────────────────────┼────────────────────────────────────────┤
│ 세션 11  │ 적대적 Agent 6            │ phase1_v6/agent1~5_findings.json │ phase1_v6/adversarial_review.json      │
│          │ + Phase 2 발견 기록        │ v8_results/ (이전 v6 산출물)      │ phase1_v6/artifact_diff.json           │
│          │                          │                                  │ phase1_v6/phase1_findings.json         │
│          │                          │                                  │ phase1_v6/phase1_checkpoint.json       │
└──────────┴──────────────────────────┴──────────────────────────────────┴────────────────────────────────────────┘
```

### Phase 1 → Phase 2 핸드오프

```
Phase 1 출력 → Phase 2 입력:
  필수:
    ✓ phase1_v6/phase1_checkpoint.json     → PC1-1~PC1-7 전수 확인
    ✓ phase1_v6/phase1_findings.json       → 발견사항 (Pass 2 수정 대상)
    ✓ phase1_v6/agent1~5_findings.json     → 에이전트별 상세 결과
  참조:
    ○ phase1_v6/adversarial_review.json    → 적대적 감사 결과
    ○ phase1_v6/artifact_diff.json         → v6 이전 산출물 대비 변경점
```

### Phase 1 소계

```
세션: 4개 (1 + 2병렬 + 1)
에이전트: ~19개 실행 단위 (8스크립트 + 5에이전트×순역방향 + 1적대적)
52스킬 투입: ~18개
```

---

# 4. Phase 2: v7 전수 재실행 (52스킬 강화)

> 원본: 8 Phase0 + 10 에이전트 + 189 항목 + 18 Tiers + 적대적
> 강화: 4계층 검증 완전 적용

## 4.1 v7 Phase 0 + Phase 1 (10 에이전트)

```
Phase 0: 세션 12 (v6 Phase 0과 동일 8스크립트, SOT 수정본 기준)

Phase 1 에이전트 매핑 (189항목, 18 Tiers):
  세션 13: Agent 1(코어) + Agent 2(보안) + Agent 3(SDAR)
    + /symbolic-verify + /sot-check + /guardrails-validate
  세션 14: Agent 4(Teams/MCP) + Agent 5(스키마) + Agent 6(메모리/RAG)
    + /cross-match + /sot-rag + /ragas-eval
  세션 15: Agent 7(UI) + Agent 8(인프라) + Agent 9(의사결정) + Agent 10(도메인)
    + /completeness-map + /deep-diff + /fact-audit

순방향(STEP A) + 역방향(STEP B) 각 에이전트:
  STEP A: PART → 원본 1:1 대조
    + /hallucination-check (환각)
    + /validate DV-4 (source_text 매칭)
  STEP B: 원본 → PART 누락 확인
    + /sot-check (SOT 대조)
    + /cross-examine (교차 심문)
```

## 4.2 v7 Phase 1.5 + Phase 2

```
세션 16:
  Agent 11 적대적 + 50건+ spot-check:
    /audit + /cross-examine + /minicheck + /hhem-verify

  Phase 2 (Pass 1에서는 발견만):
    Ripple Map 생성 + 발견사항 기록 (수정은 Pass 2에서 통합)
    /artifact-diff (이전 v7 산출물과 비교)

CHECKPOINT (PC2-1 ~ PC2-8, Pass 1: 발견사항 기준):
  PC2-1: v7 8개 Phase 0 스크립트 전수 실행 완료 (SOT 수정본 기준)
  PC2-2: v7 Agent 1~10 STEP A(순방향) 189항목 전수 완료
  PC2-3: v7 Agent 1~10 STEP B(역방향) 누락 확인 전수 완료
  PC2-4: 18 Tiers 분류별 검증 결과 기록
  PC2-5: P1~P11 오류 패턴 탐지 결과 기록
  PC2-6: 적대적 50건+ spot-check 완료 — 오판율 ≤15%
  PC2-7: Ripple Map 생성 + /artifact-diff 이전 v7 산출물 대비 기록
  PC2-8: 발견사항 JSON 저장 완료 (수정은 Pass 2에서)
```

### Phase 2 에이전트 입출력 명세

```
┌──────────┬────────────────────────────┬──────────────────────────────────┬────────────────────────────────────────┐
│  세션    │ 에이전트                    │ 입력                             │ 출력                                   │
├──────────┼────────────────────────────┼──────────────────────────────────┼────────────────────────────────────────┤
│ 세션 12  │ 0-A~0-H (8스크립트)         │ docs/sot/* (Phase 0 수정본)       │ phase2_v7/phase0/0-A~0-H_result.json  │
├──────────┼────────────────────────────┼──────────────────────────────────┼────────────────────────────────────────┤
│ 세션 13  │ Agent 1(코어)               │ PART2 §2 코어 섹션               │ phase2_v7/agent1~3_findings.json       │
│ (병렬)   │ Agent 2(보안)               │ PART2 §6.9~6.10 보안 섹션        │                                        │
│          │ Agent 3(SDAR)              │ SDAR 설계 문서                    │                                        │
├──────────┼────────────────────────────┼──────────────────────────────────┼────────────────────────────────────────┤
│ 세션 14  │ Agent 4(Teams/MCP)          │ PART2 §6.4~6.6                  │ phase2_v7/agent4~6_findings.json       │
│ (병렬)   │ Agent 5(스키마)             │ D2.1 스키마 문서                  │                                        │
│          │ Agent 6(메모리/RAG)          │ PART2 §6.5~6.6                  │                                        │
├──────────┼────────────────────────────┼──────────────────────────────────┼────────────────────────────────────────┤
│ 세션 15  │ Agent 7(UI §6.7~6.8)        │ PART2 §6.7~6.8 (UI/UX)          │ phase2_v7/agent7~10_findings.json      │
│ (병렬)   │ Agent 8(인프라 §6.11)       │ PART2 §6.11 (CI/CD/Infra)       │                                        │
│ (병렬)   │ Agent 9(의사결정)           │ PART2 §7                         │                                        │
│          │ Agent 10(도메인)            │ AI투자 도메인 문서                 │                                        │
├──────────┼────────────────────────────┼──────────────────────────────────┼────────────────────────────────────────┤
│ 세션 16  │ Agent 11 적대적             │ phase2_v7/agent*_findings.json   │ phase2_v7/adversarial_review.json      │
│          │ + Phase 2 발견 기록          │ v9_results/ (이전 v7 산출물)      │ phase2_v7/ripple_map.json              │
│          │                            │                                  │ phase2_v7/artifact_diff.json            │
│          │                            │                                  │ phase2_v7/phase2_findings.json          │
│          │                            │                                  │ phase2_v7/phase2_checkpoint.json        │
└──────────┴────────────────────────────┴──────────────────────────────────┴────────────────────────────────────────┘
```

### Phase 2 → Phase 3 핸드오프

```
Phase 2 출력 → Phase 3 입력:
  필수:
    ✓ phase2_v7/phase2_checkpoint.json     → PC2-1~PC2-8 전수 확인
    ✓ phase2_v7/phase2_findings.json       → 발견사항 (Pass 2 수정 대상)
  참조:
    ○ phase2_v7/ripple_map.json            → 연쇄 영향 맵
    ○ phase2_v7/adversarial_review.json    → 적대적 감사 결과
```

### Phase 2 소계

```
세션: 5개 (1 + 3병렬 + 1)
에이전트: ~29개 실행 단위 (8스크립트 + 10에이전트×순역방향 + 1적대적)
52스킬 투입: ~22개
```

---

# 5. Phase 3: v8 전수 재실행 (52스킬 강화)

> 원본: 14 Phase0 스크립트 + 12+1 에이전트 + 4-Dimension + ~791항목
> 강화: Dim C(구현가능성) + Dim D(프롬프트) 스킬 보강

## 5.1 v8 Phase 0 (14 스크립트)

```
세션 17:
  구조 (8개, v6 계승): 0-A~0-H
    → /validate + /symbolic-verify
  구현 (6개, v8 신규): IMP-A~IMP-F
    IMP-A(파일경로) → /sot-search + Phase B2 대조
    IMP-B(의존성순서) → /symbolic-verify (순환 탐지)
    IMP-C(단위/포맷) → /korean-nlp + /validate DV-6
    IMP-D(타임아웃) → /symbolic-verify + /fact-audit
    IMP-E(에러코드) → /cross-match C8 (참조 무결성)
    IMP-F(테스트커버리지) → /completeness-map
```

## 5.2 v8 Phase 1 (12+1 에이전트, 4-Dimension)

```
세션 18: Agent 1~4 (V0~V3 버전별 검증, Dim B+C)
  + /prompt-test (프롬프트 회귀)
  + /guardrails-validate (보안 명세)

세션 19: Agent 5~8 (§6.1~§6.10 상세, Dim B+C)
  + /ragas-eval (RAG 관련 §6.5~6.6)
  + /giskard-scan (취약점 스캔)

세션 20: Agent 9~12 (§6.11~§7 + 프롬프트 + 트리플매핑, Dim B+C+D)
  + /cross-model 미사용 (D-1: Phase 8 세션 52에서만 사용)
  + /dspy-optimize (프롬프트 최적화)
  + /eval-audit (메타 평가)

세션 21: Agent 13 적대적
  + /audit + /cross-examine + /minicheck
  + /consensus (다중 관점)
  + /write-judge-prompt (판정 프롬프트 품질)

v8 오류 패턴 P1~P11 + I1~I12 + PR1~PR5 탐지:
  I1~I12 (구현): /symbolic-verify + /sot-search + /deep-diff
  PR1~PR5 (프롬프트): /prompt-test + /validate-evaluator + /hallucination-check
```

## 5.3 v8 Phase 2 수정

```
세션 22: Phase 2 (Pass 1에서는 발견만)
  Ripple Map 생성 + 발견사항 기록 (수정은 Pass 2에서 통합)
  + /artifact-diff (이전 v8 산출물과 비교)

CHECKPOINT (PC3-1 ~ PC3-8, Pass 1: 발견사항 기준):
  PC3-1: v8 14개 Phase 0 스크립트 전수 실행 완료 (0-A~0-H + IMP-A~IMP-F)
  PC3-2: v8 Agent 1~12 4-Dimension(B+C+D) 검증 전수 완료
  PC3-3: ~791항목 전수 검증 결과 기록
  PC3-4: P1~P11 + I1~I12(구현) + PR1~PR5(프롬프트) 오류 패턴 탐지 완료
  PC3-5: Dim C(구현가능성) IMP-A~F 전수 PASS 또는 발견사항 기록
  PC3-6: Dim D(프롬프트) 18개 AI 프롬프트 회귀 테스트 완료
  PC3-7: 적대적 감사 완료 — 오판율 ≤15%
  PC3-8: Ripple Map + 발견사항 JSON 저장 완료
```

### Phase 3 에이전트 입출력 명세

```
┌──────────┬─────────────────────────────┬─────────────────────────────────┬──────────────────────────────────────┐
│  세션    │ 에이전트                     │ 입력                            │ 출력                                 │
├──────────┼─────────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ 세션 17  │ 0-A~0-H (구조 8개)           │ docs/sot/* (Phase 0 수정본)      │ phase3_v8/phase0/struct_result.json  │
│          │ IMP-A~IMP-F (구현 6개)       │ docs/sot/PHASE_B2*.md (경로기준) │ phase3_v8/phase0/impl_result.json    │
├──────────┼─────────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ 세션 18  │ Agent 1~4 (V0~V3, Dim B+C)  │ PART2 버전별 섹션               │ phase3_v8/agent1~4_findings.json     │
├──────────┼─────────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ 세션 19  │ Agent 5~8 (§6.1~6.10,Dim B+C)│ PART2 §6 상세 섹션             │ phase3_v8/agent5~8_findings.json     │
├──────────┼─────────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ 세션 20  │ Agent 9~12 (§6.11~7,Dim B+C+D)│ PART2 §6.11~§7 + 프롬프트     │ phase3_v8/agent9~12_findings.json    │
├──────────┼─────────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ 세션 21  │ Agent 13 적대적              │ phase3_v8/agent*_findings.json  │ phase3_v8/adversarial_review.json    │
├──────────┼─────────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ 세션 22  │ Phase 2 발견 기록             │ v8_results/ (이전 산출물)        │ phase3_v8/ripple_map.json            │
│          │                             │                                 │ phase3_v8/artifact_diff.json          │
│          │                             │                                 │ phase3_v8/phase3_findings.json        │
│          │                             │                                 │ phase3_v8/phase3_checkpoint.json      │
└──────────┴─────────────────────────────┴─────────────────────────────────┴──────────────────────────────────────┘
```

### Phase 3 → Phase 4 핸드오프

```
Phase 3 출력 → Phase 4 입력:
  필수:
    ✓ phase3_v8/phase3_checkpoint.json     → PC3-1~PC3-8 전수 확인
    ✓ phase3_v8/phase3_findings.json       → 발견사항 (Pass 2 수정 대상)
  참조:
    ○ phase3_v8/phase0/impl_result.json    → IMP-A~F 구현 검증 결과 (Phase 4 GT-5 참조)
    ○ phase3_v8/ripple_map.json            → 연쇄 영향 맵
```

### Phase 3 소계

```
세션: 6개 (1 + 3병렬 + 1 + 1)
에이전트: ~35개 실행 단위 (14스크립트 + 12에이전트 + 1적대적 + Phase2기록)
52스킬 투입: ~28개
```

---

# 6. Phase 4: v9 전수 재실행 (52스킬 강화)

> 원본: GT 5개 + 6관점 + 3-Wave + ~663 checks + 14 규칙
> 강화: GT 구축에 스킬 투입, 외부 의존성 실제 확인

## 6.1 Phase -1 + Phase 0-Pre (기반 정비 + GT 5개)

```
세션 23:
  Phase -1: PART2 무결성 + SRC 동기화
    /integrity (해시) + /sot-cache (재인덱싱)

  Phase 0-Pre: Ground Truth 5개 재구축
    GT-1(파일경로) → /symbolic-verify + /validate DV-2 (경로 유효성 + 구조 검증)
    GT-2(산출물체인) → /lineage (데이터 계보)
    GT-3(수량) → /fact-audit (수치 사실 정확성)
    GT-4(외부사실) → /exa-verify (Tier 3 사용 확정 — D-1) + /fact-audit
    GT-5(기술실행가능성) → /giskard-scan + /prompt-test
```

## 6.2 Phase 0 + Phase 1 (6관점 × 3-Wave)

```
세션 24: Phase 0 프롬프트 작성 + Phase 0-Validate 시범
  6관점: A(파일경로→GT-1) B(산출물체인→GT-2) C(수량일관성→GT-3내부)
         D(외부사실→GT-4) E(수량정확성→GT-3외부) F(기술실행가능성→GT-5)
  ※ C(내부 일관)와 E(사실 정확)는 GT-3의 상보적 두 축
  + /prompt-test (프롬프트 품질)
  + /dspy-optimize (프롬프트 최적화)

세션 25: Phase 1 Wave 1(관점 A/B) + Wave 2(관점 C)
  Wave 1: A → /symbolic-verify (파일경로 의존순서)
          B → /sot-search (산출물체인 경로 일관성)
  Wave 2: C → /cross-match (수량 내부 일관성)

세션 26: Phase 1 Wave 3 (관점 D/E/F)
  D → /exa-verify (Tier 3 확정 — D-1) + /fact-audit (외부사실 검증 — GT-4 대응)
  E → /fact-audit + /symbolic-verify (수량 사실 정확성 — GT-3 대응)
  F → /giskard-scan + /prompt-test (기술실행가능성 — GT-5 대응)

RULE 1~14 준수: /validate + /symbolic-verify + /korean-nlp
```

## 6.3 Phase 2 수정

```
세션 27: Phase 2 (Pass 1에서는 발견만)
  발견사항 기록 → CHECKPOINT

CHECKPOINT (PC4-1 ~ PC4-8, Pass 1: 발견사항 기준):
  PC4-1: GT 5개 재구축 완료 (GT-1 파일경로, GT-2 산출물체인, GT-3 수량, GT-4 외부사실, GT-5 기술실행가능성)
  PC4-2: 6관점(A~F) × 3-Wave 전수 검증 완료 (Wave 1: A/B, Wave 2: C, Wave 3: D/E/F)
  PC4-3: RULE 1~14 전수 준수 확인 (위반 시 발견사항 기록)
  PC4-4: ~663 checks 전수 실행 결과 기록 (세션 25~26 Wave 검증 누적)
  PC4-5: GT 대비 실제 데이터 일치율 ≥ 90% (세션 25~26 Wave 결과에서 산출)
  PC4-6: 외부 의존성(GT-4) 실존 확인 (세션 26 관점 D, exa-verify 또는 fact-audit)
  PC4-7: 교차심문 결과 기록 (세션 27에서 /cross-examine 실행)
  PC4-8: 발견사항 JSON 저장 완료

  RULE 준수 목록 (14개):
    RULE-1~14: /validate + /symbolic-verify + /korean-nlp로 개별 확인
    위반 건수 0 = PASS, 위반 있으면 발견사항에 기록
```

### Phase 4 에이전트 입출력 명세

```
┌──────────┬─────────────────────────────┬──────────────────────────────────┬──────────────────────────────────────┐
│  세션    │ 에이전트                     │ 입력                            │ 출력                                 │
├──────────┼─────────────────────────────┼──────────────────────────────────┼──────────────────────────────────────┤
│ 세션 23  │ Phase -1: PART2 무결성       │ PART2 문서, SRC 파일             │ phase4_v9/phase-1/integrity.json     │
│          │ Phase 0-Pre: GT 1~5 구축     │ docs/sot/PHASE_B2*.md           │ phase4_v9/gt/gt1_filepath.json       │
│          │                             │ v9_results/phase0/*.json         │ phase4_v9/gt/gt2_artifact_chain.json │
│          │                             │                                  │ phase4_v9/gt/gt3_quantity.json       │
│          │                             │                                  │ phase4_v9/gt/gt4_external.json       │
│          │                             │                                  │ phase4_v9/gt/gt5_feasibility.json    │
├──────────┼─────────────────────────────┼──────────────────────────────────┼──────────────────────────────────────┤
│ 세션 24  │ Phase 0 프롬프트 작성        │ phase4_v9/gt/*.json              │ phase4_v9/prompts/prompt_A~F.md      │
│          │ + Phase 0-Validate 시범       │                                  │ phase4_v9/phase0_validate.json       │
├──────────┼─────────────────────────────┼──────────────────────────────────┼──────────────────────────────────────┤
│ 세션 25  │ Wave 1+2 (관점 A/B/C)       │ phase4_v9/prompts/*.md           │ phase4_v9/wave1_ABC.json             │
├──────────┼─────────────────────────────┼──────────────────────────────────┼──────────────────────────────────────┤
│ 세션 26  │ Wave 3 (관점 D/E/F)         │ phase4_v9/wave1_ABC.json (참조)  │ phase4_v9/wave3_DEF.json             │
├──────────┼─────────────────────────────┼──────────────────────────────────┼──────────────────────────────────────┤
│ 세션 27  │ Phase 2 발견 기록             │ v9_results/ (이전 산출물)        │ phase4_v9/phase4_findings.json       │
│          │                             │                                  │ phase4_v9/phase4_checkpoint.json     │
│          │                             │                                  │ phase4_v9/rule_compliance.json       │
└──────────┴─────────────────────────────┴──────────────────────────────────┴──────────────────────────────────────┘
```

### Phase 4 → Phase 5 핸드오프

```
Phase 4 출력 → Phase 5 입력:
  필수:
    ✓ phase4_v9/phase4_checkpoint.json     → PC4-1~PC4-8 전수 확인
    ✓ phase4_v9/phase4_findings.json       → 발견사항
    ✓ phase4_v9/gt/*.json                  → Ground Truth (Phase 5 Feature 추출 기준)
  참조:
    ○ phase4_v9/rule_compliance.json       → RULE 1~14 준수 결과
```

### Phase 4 소계

```
세션: 5개 (1 + 1 + 2순차 + 1)
  ※ 세션 25→26 순차 (Wave 3이 Wave 1+2 결과 참조)
에이전트: ~40+개 실행 단위 (GT5 + 6관점×3Wave + 프롬프트 + 발견기록)
52스킬 투입: ~20개
```

---

# 7. Phase 5: v10 전수 재실행 (52스킬 강화)

> 원본: 68개 SRC → 3,943 features → PART2 매핑 + 22 에이전트 + 33 세션
> 강화: Feature 추출 자동화 + 매핑 검증 스킬 대폭 투입

## 7.1 Phase 0-A~0-F (Feature 추출)

```
세션 28: Phase 0-A + 0-B (정의 + CLAUDE.md 인덱스)
  /extract + /sot-cache + /korean-nlp

세션 29-31: Phase 0-C (15 에이전트, 68개 SRC 기능 추출)
  3세션 × 5에이전트 병렬
  각 에이전트:
    /extract → /validate DV → /quality-gate
    /docling (복잡한 표 SOT)
    /gpt-cache (반복 호출 캐싱)

세션 32: Phase 0-D + 0-E + 0-F (교차검증 + 이전 산출물 대사 + Registry 확정)
  /cross-match + /deep-diff + /json-diff
  /golden-set (정답 데이터 기반)
```

## 7.2 Phase 1 + 1.5 + 2

```
세션 33: Phase 1 매핑 에이전트 6개 (병렬 2그룹 × 3)
  Feature → PART2 §2~§7 섹션별 매핑
  /cross-match + /hallucination-check + /sot-check

세션 34: Phase 1.5 적대적 + Phase 2 발견 기록
  /audit + /cross-examine + /minicheck
  발견사항 기록 (수정은 Pass 2에서 통합)

CHECKPOINT (PC5-1 ~ PC5-9, Pass 1: 발견사항 기준):
  PC5-1: 68개 SRC 전수 Feature 추출 완료
  PC5-2: Feature Registry 총 수 확인 (기준: ~3,943 features)
  PC5-3: 이전 산출물 대사 완료 (v10_results 대비 delta)
  PC5-4: Feature → PART2 §2~§7 매핑 전수 완료 (6에이전트)
  PC5-5: 매핑 누락률 ≤ 5% (MISSING 항목 기록)
  PC5-6: /quality-gate 전수 SILVER 이상
  PC5-7: 적대적 감사 완료 — 오판율 ≤15%
  PC5-8: /golden-set 기반 정답 대비 정확도 확인
  PC5-9: 발견사항 JSON 저장 완료
```

### Phase 5 에이전트 입출력 명세

```
┌──────────┬──────────────────────────────┬─────────────────────────────────┬──────────────────────────────────────┐
│  세션    │ 에이전트                      │ 입력                            │ 출력                                 │
├──────────┼──────────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ 세션 28  │ Phase 0-A(정의) + 0-B(인덱스) │ docs/sot/CLAUDE.md 등            │ phase5_v10/phase0/definitions.json   │
│          │                              │                                 │ phase5_v10/phase0/index.json         │
├──────────┼──────────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ 세션29-31│ Phase 0-C (15에이전트×3세션)   │ docs/sot/* (68개 전수)           │ phase5_v10/features/src_C01~C15.json │
│ (병렬)   │ 3그룹 × 5에이전트             │                                 │ + validation/*_dv.json, *_qg.json   │
├──────────┼──────────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ 세션 32  │ Phase 0-D~F (교차+대사+확정)  │ phase5_v10/features/*.json      │ phase5_v10/feature_registry.json     │
│          │                              │ v10_results/*.json (이전 산출물) │ phase5_v10/v10_delta.json            │
├──────────┼──────────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ 세션 33  │ 매핑 에이전트 6개 (2그룹×3)    │ phase5_v10/feature_registry.json │ phase5_v10/mapping/sect2~7.json      │
├──────────┼──────────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ 세션 34  │ 적대적 + Phase 2 발견 기록     │ phase5_v10/mapping/*.json       │ phase5_v10/adversarial_review.json   │
│          │                              │                                 │ phase5_v10/phase5_findings.json      │
│          │                              │                                 │ phase5_v10/phase5_checkpoint.json    │
└──────────┴──────────────────────────────┴─────────────────────────────────┴──────────────────────────────────────┘
```

### Phase 5 → Phase 6 핸드오프

```
Phase 5 출력 → Phase 6 입력:
  필수:
    ✓ phase5_v10/phase5_checkpoint.json    → PC5-1~PC5-9 전수 확인
    ✓ phase5_v10/feature_registry.json     → Feature Registry (Phase 6 인덱스 참조)
    ✓ phase5_v10/phase5_findings.json      → 발견사항
  참조:
    ○ phase5_v10/v10_delta.json            → 이전 v10 대비 변경점
    ○ phase5_v10/mapping/sect2~7.json      → PART2 매핑 결과
```

### Phase 5 소계

```
세션: 7개 (1 + 3병렬 + 1 + 1병렬 + 1)
에이전트: ~25+개 실행 단위 (15추출 + 6매핑 + 교차+대사+적대적)
52스킬 투입: ~18개
```

---

# 8. Phase 6: v11 전수 재실행 (52스킬 강화)

> 원본: 7 인덱스 + 5 Wave × 14 에이전트 + 26 GAP + BP-1~15
> 강화: 내부 자기 정합성에 /sot-conflict + /symbolic-verify 집중 투입

## 8.1 Phase 0 (7 인덱스 재구축)

```
세션 35:
  0-A~0-G 인덱스 재구축
  /sot-cache + /extract + /validate
```

## 8.2 Phase 1 (5 Wave × 14 에이전트)

```
세션 36: Wave 1 (Agent 1~3, GAP-05/06/07/08/10 수치/참조)
  + /symbolic-verify + /fact-audit + /validate DV-2/7
  + /sot-conflict (LOCK값 자기모순)

세션 37: Wave 2 (Agent 4~6, GAP-01/02/03/04/09 구조/매핑)
  + /cross-match + /completeness-map + /deep-diff

세션 38: Wave 3 (Agent 7~9, GAP-11/12/13/14 프롬프트)
  + /prompt-test + /validate-evaluator + /hallucination-check

세션 39: Wave 4 (Agent 10~13, GAP-15~22/25 심화)
  + /giskard-scan (기술실현성/보안)
  + /ragas-eval (RAG 관련 GAP)
  + /eval-audit (메타 평가)
  + /guardrails-validate (보안커버리지)

세션 40: Wave 5 (Agent 14, GAP-23/24 사용성)
  + /korean-nlp (문서 탐색성)
  + /docling (문서 구조)
```

## 8.3 Phase 1.5 + Phase 2

```
세션 41:
  Agent 15 적대적:
    /audit + /cross-examine + /consensus + /debate

  Phase 2 (Pass 1에서는 발견만):
    발견사항 기록 + BP-1~15 준비 (수정은 Pass 2에서 통합)
    /artifact-diff (이전 v11 산출물과 비교)

CHECKPOINT (PC6-1 ~ PC6-14, Pass 1: 발견사항 기준):
  PC6-1:  7개 인덱스(0-A~0-G) 재구축 완료
  PC6-2:  GAP-05/06/07/08/10 수치/참조 검증 완료 (Wave 1)
  PC6-3:  GAP-01/02/03/04/09 구조/매핑 검증 완료 (Wave 2)
  PC6-4:  GAP-11/12/13/14 프롬프트 검증 완료 (Wave 3)
  PC6-5:  GAP-15~22/25 심화 검증 완료 (Wave 4)
  PC6-6:  GAP-23/24 사용성 검증 완료 (Wave 5)
  PC6-7:  26개 GAP 전수 검증 완료 (GAP-01~25 + 추가분)
  PC6-8:  LOCK값 자기모순 0건 (/sot-conflict)
  PC6-9:  프롬프트 회귀 테스트 PASS (/prompt-test)
  PC6-10: 보안 커버리지 확인 (/guardrails-validate)
  PC6-11: 적대적 감사 완료 — /debate 포함
  PC6-12: BP-1~15 준비 완료 (원본 보호 프로토콜 목록)
  PC6-13: /artifact-diff 이전 v11 산출물 대비 기록
  PC6-14: 발견사항 JSON 저장 완료
```

### Phase 6 에이전트 입출력 명세

```
┌──────────┬──────────────────────────────┬─────────────────────────────────┬──────────────────────────────────────┐
│  세션    │ 에이전트                      │ 입력                            │ 출력                                 │
├──────────┼──────────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ 세션 35  │ 0-A~0-G 인덱스 재구축         │ docs/sot/* (Phase 0 수정본)      │ phase6_v11/index/0-A~0-G.json       │
│          │                              │ phase5_v10/feature_registry.json│                                      │
├──────────┼──────────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ 세션 36  │ Wave 1: Agent 1~3 (수치/참조) │ phase6_v11/index/*.json         │ phase6_v11/wave1_findings.json       │
│ 세션 37  │ Wave 2: Agent 4~6 (구조/매핑) │ v11_results/*.json              │ phase6_v11/wave2_findings.json       │
│ 세션 38  │ Wave 3: Agent 7~9 (프롬프트)  │                                 │ phase6_v11/wave3_findings.json       │
│ 세션 39  │ Wave 4: Agent 10~13 (심화)    │                                 │ phase6_v11/wave4_findings.json       │
│ 세션 40  │ Wave 5: Agent 14 (사용성)     │                                 │ phase6_v11/wave5_findings.json       │
├──────────┼──────────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ 세션 41  │ Agent 15 적대적              │ phase6_v11/wave*_findings.json  │ phase6_v11/adversarial_review.json   │
│          │ + Phase 2 발견 기록            │ v11_results/ (이전 산출물)       │ phase6_v11/bp_preparation.json       │
│          │                              │                                 │ phase6_v11/phase6_findings.json      │
│          │                              │                                 │ phase6_v11/phase6_checkpoint.json    │
└──────────┴──────────────────────────────┴─────────────────────────────────┴──────────────────────────────────────┘
```

### Phase 6 → Phase 7 핸드오프

```
Phase 6 출력 → Phase 7 입력:
  필수:
    ✓ phase6_v11/phase6_checkpoint.json    → PC6-1~PC6-14 전수 확인
    ✓ phase6_v11/phase6_findings.json      → 발견사항
    ✓ phase6_v11/bp_preparation.json       → BP-1~15 원본 보호 프로토콜
  참조:
    ○ phase6_v11/index/*.json              → 7개 인덱스 (Phase 7 Feature Registry 참조)
    ○ phase6_v11/wave*_findings.json       → Wave별 상세 결과
```

### Phase 6 소계

```
세션: 7개 (1 + 5순차Wave + 1)
에이전트: ~30+개 실행 단위 (7인덱스 + 14에이전트×5Wave + 1적대적)
52스킬 투입: ~22개
```

---

# 9. Phase 7: v12 전수 재실행 (52스킬 강화)

> 원본: 15 추출 + 7 매핑 + 적대적 + v10 교차 + v7 역방향 + §6 참조 57건 + v11 미해결 5건
> 강화: 최종 완전성 검증에 전 스킬 총동원

## 9.1 Phase 0 (Feature Registry 재구축)

```
세션 42-44: 15 에이전트 (3세션 × 5에이전트 병렬)
  68개 SOT → Feature 추출
  /extract + /validate DV + /quality-gate
  /sot-cache + /docling + /gpt-cache
```

## 9.2 Phase 1~5 (매핑 + 교차 + 역방향 + 참조 + 미해결)

```
세션 45: Phase 1 매핑 (7 에이전트)
  SOT → PART2 매핑
  /cross-match + /hallucination-check + /sot-check

세션 46: Phase 1.5 적대적
  /audit + /cross-examine + /minicheck + /hhem-verify

세션 47: Phase 2(v10 교차) + Phase 3(v7 역방향)
  v13 Phase 5 산출물 ↔ v12 결과 교차
  v13 Phase 2 산출물 ↔ v12 역방향
  /deep-diff + /json-diff + /cross-match

세션 48: Phase 4(§6 참조 57건) + Phase 5(v11 미해결 5건) + Phase 6(발견 기록)
  /sot-search (참조 해소)
  /sot-conflict (미해결 패턴)
  발견사항 기록 (수정은 Pass 2에서 통합)

CHECKPOINT (PC7-1 ~ PC7-12, Pass 1: 발견사항 기준):
  PC7-1:  Feature Registry 재구축 완료 (68 SRC 전수, 15 에이전트)
  PC7-2:  SOT → PART2 매핑 100% (7 매핑 에이전트)
  PC7-3:  MISSING BLOCKER 0건
  PC7-4:  적대적 재검증 PASS (/audit + /hhem-verify)
  PC7-5:  v10 교차 검증 완료 (Phase 5 산출물 ↔ v12 결과)
  PC7-6:  v7 역방향 교차 검증 완료 (Phase 2 산출물 ↔ v12)
  PC7-7:  §6 참조 57건 전수 해소 (/sot-search)
  PC7-8:  v11 미해결 5건 패턴 해소 (/sot-conflict)
  PC7-9:  PART2 반영 완전성 확인
  PC7-10: 수치/참조 일관성 (LOCK + 산술) 확인
  PC7-11: 원본 보호 확인 (SHA256 백업 대조)
  PC7-12: 발견사항 JSON 저장 완료
```

### Phase 7 에이전트 입출력 명세

```
┌──────────┬──────────────────────────────┬─────────────────────────────────┬──────────────────────────────────────┐
│  세션    │ 에이전트                      │ 입력                            │ 출력                                 │
├──────────┼──────────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│세션 42-44│ 15 추출 에이전트 (3세션×5병렬) │ docs/sot/* (68개 전수)           │ phase7_v12/features/src_*.json       │
│          │                              │                                 │ + validation/*_dv.json, *_qg.json   │
├──────────┼──────────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ 세션 45  │ 7 매핑 에이전트               │ phase7_v12/features/*.json      │ phase7_v12/mapping/mapping.json      │
│          │                              │ PART2 §2~§7                     │ phase7_v12/feature_registry.json     │
├──────────┼──────────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ 세션 46  │ 적대적 에이전트               │ phase7_v12/mapping/*.json       │ phase7_v12/adversarial_review.json   │
├──────────┼──────────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ 세션 47  │ v10 교차 + v7 역방향          │ phase5_v10/feature_registry.json│ phase7_v12/v10_cross.json            │
│          │                              │ phase2_v7/agent*_findings.json  │ phase7_v12/v7_reverse.json           │
│          │                              │ v12/v12_results/*.json           │                                      │
├──────────┼──────────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ 세션 48  │ §6 참조 + v11 미해결 + 기록   │ phase6_v11/phase6_findings.json │ phase7_v12/s6_references.json        │
│          │                              │ v11_results/*.json              │ phase7_v12/v11_unresolved.json       │
│          │                              │                                 │ phase7_v12/phase7_findings.json      │
│          │                              │                                 │ phase7_v12/phase7_checkpoint.json    │
└──────────┴──────────────────────────────┴─────────────────────────────────┴──────────────────────────────────────┘
```

### Phase 7 → Pass 2 핸드오프

```
Phase 7 출력 → Pass 2 입력:
  필수 (Phase 1~7 전체 발견사항):
    ✓ phase1_v6/phase1_findings.json
    ✓ phase2_v7/phase2_findings.json
    ✓ phase3_v8/phase3_findings.json
    ✓ phase4_v9/phase4_findings.json
    ✓ phase5_v10/phase5_findings.json
    ✓ phase6_v11/phase6_findings.json
    ✓ phase7_v12/phase7_findings.json
    ✓ 각 Phase의 *_checkpoint.json → 전수 PASS 확인
  참조:
    ○ 각 Phase의 ripple_map.json, adversarial_review.json
    ○ phase6_v11/bp_preparation.json → BP-1~15 원본 보호
```

### Phase 7 소계

```
세션: 7개 (3병렬 + 4순차)
에이전트: ~50+개 실행 단위 (15추출 + 7매핑 + 적대적 + 교차×2 + 참조+미해결)
52스킬 투입: ~20개
```

---

# 9.5 Pass 2: 통합 수정 + 전 Phase 재검증 (ABD-3)

> Pass 1(Phase 1~7)에서 수집된 전체 발견사항을 1회 통합 수정 후 재검증

## 9.5.1 통합 발견사항 정리

```
세션 49: 전체 발견사항 통합
  Phase 1~7 발견사항 JSON 전수 수집
  /cross-match (Phase 간 중복 발견사항 제거)
  /completeness-map (발견사항 × 오류 카테고리 매트릭스)
  심각도 재분류: CRITICAL → 필수 수정, WARNING → 선택 수정

세션 50: Ripple Map + 통합 수정
  /delta-apply (전 발견사항 1회 수정)
  /integrity (수정 전후 해시 비교)
  /deep-diff (수정 범위 확인)
  /json-diff (JSON 변경 추적)
  BP-1~15 원본 보호 프로토콜 적용

세션 51: 전 Phase CHECKPOINT 재검증
  Phase 0: SOT 정합성 재검증 (EA+CM 핵심 항목 + 0-A~0-H 스크립트 재실행, 수정 반영)
  Phase 1~7: 각 Phase CHECKPOINT 조건 재확인
  /artifact-diff (수정 전후 비교)
  /validate + /quality-gate (수정된 산출물 재판정)
```

### Pass 2 CHECKPOINT

```
  PC-P2-1: Phase 1~7 발견사항 JSON 7개 파일 전수 수집 완료
  PC-P2-2: 중복 발견사항 제거 — /cross-match 교차 비교 완료
  PC-P2-3: 심각도 재분류 완료 (CRITICAL → 필수, WARNING → 선택)
  PC-P2-4: 통합 수정 대상 목록 확정 — completeness_matrix.json 생성
  PC-P2-5: 전 발견사항 1회 통합 수정 완료 (/delta-apply)
  PC-P2-6: 수정 전후 해시 일치 확인 (/integrity SHA-256)
  PC-P2-7: /deep-diff + /json-diff 수정 범위 기록 완료
  PC-P2-8: BP-1~15 원본 보호 프로토콜 적용 확인 (백업 해시 대조)
  PC-P2-9: Phase 0 SOT 정합성 재검증 (EA+CM + 0-A~0-H) — 수정 반영분 검증 완료
  PC-P2-10: Phase 1~7 각 CHECKPOINT 조건 재확인 — 전수 PASS
  PC-P2-11: /artifact-diff 수정 전후 비교 보고서 생성
  PC-P2-12: /validate + /quality-gate 수정된 산출물 재판정 PASS
```

### Pass 2 에이전트 입출력 명세

```
┌──────────┬──────────────────────────────┬─────────────────────────────────┬──────────────────────────────────────┐
│  세션    │ 에이전트                      │ 입력                            │ 출력                                 │
├──────────┼──────────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ 세션 49  │ 통합 수집 에이전트             │ phase1_v6/phase1_findings.json  │ pass2/merged_findings.json           │
│          │                              │ phase2_v7/phase2_findings.json  │ pass2/completeness_matrix.json       │
│          │                              │ phase3_v8/phase3_findings.json  │ pass2/severity_reclassification.json │
│          │                              │ phase4_v9/phase4_findings.json  │ pass2/dedup_report.json              │
│          │                              │ phase5_v10/phase5_findings.json │                                      │
│          │                              │ phase6_v11/phase6_findings.json │                                      │
│          │                              │ phase7_v12/phase7_findings.json │                                      │
├──────────┼──────────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ 세션 50  │ Ripple Map + 수정 에이전트    │ pass2/merged_findings.json      │ pass2/ripple_map.json                │
│          │                              │ pass2/severity_reclassification │ pass2/delta_apply_log.json           │
│          │                              │ docs/sot/* (전수)               │ pass2/integrity_before_after.json    │
│          │                              │ v8~v11_results/+v12/v12_results/│ pass2/deep_diff_report.json          │
│          │                              │ phase6_v11/bp_preparation.json  │ pass2/json_diff_report.json          │
│          │                              │                                 │ pass2/backup_hash_verification.json  │
├──────────┼──────────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ 세션 51  │ 전 Phase 재검증 에이전트       │ pass2/delta_apply_log.json      │ pass2/phase0_revalidation.json       │
│          │                              │ phase0~7 각 checkpoint.json     │ pass2/phase1-7_recheckpoint.json     │
│          │                              │ docs/sot/* (수정본)             │ pass2/artifact_diff_report.json      │
│          │                              │                                 │ pass2/final_validation.json          │
│          │                              │                                 │ pass2/pass2_checkpoint.json          │
└──────────┴──────────────────────────────┴─────────────────────────────────┴──────────────────────────────────────┘
```

### Pass 2 → Phase 8 핸드오프

```
Pass 2 출력 → Phase 8 입력:
  필수:
    ✓ pass2/pass2_checkpoint.json (전 Phase 재검증 PASS 확인)
    ✓ pass2/merged_findings.json (통합 발견사항 전수)
    ✓ pass2/final_validation.json (수정 후 최종 판정)
    ✓ pass2/artifact_diff_report.json (수정 전후 변경 추적)
  참조:
    ○ pass2/ripple_map.json (파급 영향 맵)
    ○ pass2/integrity_before_after.json (해시 비교)
    ○ pass2/deep_diff_report.json + json_diff_report.json
  게이트:
    pass2_checkpoint.json 내 전 Phase RECHECKPOINT = PASS 필수
    → 1개라도 FAIL 시 해당 Phase 재수정 후 세션 51 반복
```

### Pass 2 소계

```
세션: 3개 (순차 — 각 세션이 이전 세션 출력에 의존)
산출물: 통합 수정 기록 + 전 Phase CHECKPOINT 재검증 결과
에이전트: ~15개 실행 단위
52스킬 투입: ~15개
```

---

# 10. Phase 8: 최종 종합 판정

> F1~F10 전수 PASS 확인 + 초보자가이드 33개 세션 재검토

## 10.1 종합 판정

```
세션 52:
  /completeness-map         → 33개 CAT × 도구 커버리지 최종 확인
  /final-review Mode B      → FR-B01~B09 자동 체크
  /eval-audit               → 평가 도구 자체 감사
  /validate-evaluator       → 검증기 검증
  /write-judge-prompt       → 판정 프롬프트 품질 확인
  /report                   → 종합 보고서 생성

F1~F10 판정:
  F1:  Phase 0 SOT 불일치 CRITICAL 0건
  F2:  Phase 1 (v6) CHECKPOINT PASS
  F3:  Phase 2 (v7) CHECKPOINT PASS
  F4:  Phase 3 (v8) CHECKPOINT PASS
  F5:  Phase 4 (v9) CHECKPOINT PASS
  F6:  Phase 5 (v10) CHECKPOINT PASS
  F7:  Phase 6 (v11) CHECKPOINT PASS
  F8:  Phase 7 (v12) CHECKPOINT PASS
  F9:  v13 신규 발견 CRITICAL 0건
  F10: 초보자가이드 33개 세션 정합성
```

## 10.2 초보자가이드 재검토

```
세션 53:
  Phase 0~7 SOT 수정 반영분 → 33개 세션 파일 grep
  /sot-search (영향 세션 식별)
  /cross-match (수정 값 정합)
  /hallucination-check (오염 확인)
  /korean-nlp (한국어 표현 일관)
  /quality-gate (최종 판정)
```

### Phase 8 CHECKPOINT

```
  PC8-1:  F1 Phase 0 SOT 불일치 CRITICAL 0건 확인
  PC8-2:  F2 Phase 1 (v6) CHECKPOINT 전항 PASS
  PC8-3:  F3 Phase 2 (v7) CHECKPOINT 전항 PASS
  PC8-4:  F4 Phase 3 (v8) CHECKPOINT 전항 PASS
  PC8-5:  F5 Phase 4 (v9) CHECKPOINT 전항 PASS
  PC8-6:  F6 Phase 5 (v10) CHECKPOINT 전항 PASS
  PC8-7:  F7 Phase 6 (v11) CHECKPOINT 전항 PASS
  PC8-8:  F8 Phase 7 (v12) CHECKPOINT 전항 PASS
  PC8-9:  F9 v13 신규 발견 CRITICAL 0건 확인
  PC8-10: F10 초보자가이드 33개 세션 정합성 확인
  PC8-11: /eval-audit 평가 도구 자체 감사 PASS
  PC8-12: /validate-evaluator 검증기 검증 PASS
  PC8-13: /completeness-map 33개 CAT × 도구 커버리지 100%
  PC8-14: /final-review Mode B 전항 PASS (FR-B01~B09)
  PC8-15: /write-judge-prompt 판정 프롬프트 품질 확인
  PC8-16: /report 종합 보고서 생성 완료
  PC8-17: 초보자가이드 33개 세션 SOT 수정 반영 확인 (/sot-search)
  PC8-18: 수정 값 정합 확인 (/cross-match)
  PC8-19: 환각 오염 0건 확인 (/hallucination-check)
  PC8-20: 한국어 표현 일관성 확인 (/korean-nlp)
  PC8-21: /quality-gate 최종 판정 PASS
```

### Phase 8 에이전트 입출력 명세

```
┌──────────┬──────────────────────────────┬─────────────────────────────────┬──────────────────────────────────────┐
│  세션    │ 에이전트                      │ 입력                            │ 출력                                 │
├──────────┼──────────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ 세션 52  │ 종합 판정 에이전트             │ pass2/pass2_checkpoint.json     │ phase8/completeness_map.json         │
│          │                              │ pass2/final_validation.json     │ phase8/final_review_mode_b.json      │
│          │                              │ pass2/merged_findings.json      │ phase8/eval_audit_report.json        │
│          │                              │ phase0~7 각 checkpoint.json     │ phase8/evaluator_validation.json     │
│          │                              │ docs/sot/* (전수)               │ phase8/judge_prompt_review.json      │
│          │                              │                                 │ phase8/f1_f10_verdict.json           │
│          │                              │                                 │ phase8/final_report.json             │
├──────────┼──────────────────────────────┼─────────────────────────────────┼──────────────────────────────────────┤
│ 세션 53  │ 초보자가이드 재검토 에이전트   │ phase8/f1_f10_verdict.json      │ phase8/guide_sot_sync.json           │
│          │                              │ pass2/delta_apply_log.json      │ phase8/guide_cross_match.json        │
│          │                              │ docs/guides/sections/session_*.md│ phase8/guide_hallucination.json      │
│          │                              │ docs/sot/* (수정본)             │ phase8/guide_korean_nlp.json         │
│          │                              │                                 │ phase8/guide_quality_gate.json       │
│          │                              │                                 │ phase8/phase8_checkpoint.json        │
│          │                              │                                 │ phase8/FINAL_VERDICT.json            │
└──────────┴──────────────────────────────┴─────────────────────────────────┴──────────────────────────────────────┘
```

### Phase 8 최종 출력 명세

```
phase8/FINAL_VERDICT.json:
  {
    "verdict": "PASS" | "FAIL",
    "timestamp": "ISO-8601",
    "f1_f10": { "F1": "PASS", ..., "F10": "PASS" },
    "total_findings": { "critical": 0, "warning": N, "info": N },
    "pass2_applied": true,
    "guide_33_sessions_synced": true,
    "checkpoint_summary": {
      "phase0": "PASS", "phase1": "PASS", ..., "phase7": "PASS",
      "pass2": "PASS", "phase8": "PASS"
    },
    "cross_model_verified": true,
    "integrity_hash": "SHA-256 of FINAL_VERDICT.json contents",
    "pipeline_version": "v13-enhanced",
    "user_decisions": { "D-1": "Tier3 selective", "D-2": "full fix", "D-3": "review before fix" }
  }

phase8/final_report.json:
  전체 파이프라인 실행 보고서 (53세션 × 264+ 에이전트 × 11,000+ 체크항목)
  Phase별 통계, 발견사항 분포, 수정 내역, 소요 시간, 스킬 활용 현황 포함
```

### Phase 8 소계

```
세션: 2개 (순차 — 세션 53은 세션 52의 F1~F10 판정 결과 필요)
에이전트: ~10개 실행 단위
  세션 52: /completeness-map + /final-review + /eval-audit + /validate-evaluator
           + /write-judge-prompt + /report = 6개 스킬 단위
  세션 53: /sot-search + /cross-match + /hallucination-check + /korean-nlp
           + /quality-gate = 5개 검증 단위
  → 스킬 단위 합산 ~10+
52스킬 투입: ~12개
```

---

# 11. 전체 요약

## 11.1 세션 총계

```
┌──────────┬────────┬────────────┬──────────┬────────────────────┐
│  Phase   │ 세션수  │ 에이전트   │ 체크항목  │ 52스킬 투입        │
├──────────┼────────┼────────────┼──────────┼────────────────────┤
│ Phase 0  │   7    │    26      │   ~500+  │ ~20개              │
│ Pass 1:  │        │            │          │                    │
│ Phase 1  │   4    │    19      │   ~100+  │ ~18개              │
│ Phase 2  │   5    │    29      │    189   │ ~22개              │
│ Phase 3  │   6    │    35      │   ~791   │ ~28개              │
│ Phase 4  │   5    │    40+     │   ~663   │ ~20개              │
│ Phase 5  │   7    │    25+     │  3,943   │ ~18개              │
│ Phase 6  │   7    │    30+     │  ~970    │ ~22개              │
│ Phase 7  │   7    │    50+     │ ~4,000+  │ ~20개              │
│ Pass 2:  │   3    │    재검증   │  재확인   │ ~15개              │
│ Phase 8  │   2    │    10+     │   F1~10  │ ~12개              │
├──────────┼────────┼────────────┼──────────┼────────────────────┤
│ **합계** │ **53** │ **~264+**  │**~11,000+**│ **52개 (43 명시적 + 9 인프라)** │
└──────────┴────────┴────────────┴──────────┴────────────────────┘

※ 원본 v13_plan.md 예상: 27-38세션. 본 계획 53세션 (+15~26)
   증가 사유: 52개 스킬 통합 오버헤드 + Pass 2 재검증 3세션 추가
   병렬 최적화로 ~80+ → 53 압축 (34% 절감)
```

## 11.2 Phase 순서 의존성 (병렬 가능 구간)

```
Phase 0 (SOT) ──────────────────── 필수 선행 (SOT 수정은 여기서만)
  ↓
Pass 1 (발견만, 수정 없음 — ABD-3 준수):
  Phase 1 (v6) → Phase 2 (v7) → Phase 3 (v8)    ← SRC 범위 확장 순서
    → Phase 4 (v9) → Phase 5 (v10)               ← 구현준비→Feature 순서
    → Phase 6 (v11) → Phase 7 (v12)              ← 내부정합→최종완전성
  ※ Phase 간: 순차 (이전 Phase 산출물 참조)
  ※ Phase 내: 최대 병렬 (에이전트 그룹 동시 실행)
  ※ 각 Phase의 "Phase 2 수정" 단계는 발견사항 기록만 수행, 실제 수정 보류
  ↓
Pass 2 (통합 수정 + 재검증):
  전체 발견사항 통합 정리 → Ripple Map → 1회 수정 → 전 Phase CHECKPOINT 재검증
  ↓
Phase 8: 최종 종합 판정
```

## 11.3 병렬 최적화 포인트

```
1. Phase 0-A: 15 추출 에이전트 → 3그룹 × 5 병렬 (3세션)
2. Phase 0-B: 8 크로스 에이전트 → 2그룹 × 4 병렬 (2세션)
3. v6 Phase 1: 5 에이전트 → 2그룹 병렬 (2세션)
4. v7 Phase 1: 10 에이전트 → 3그룹 병렬 (3세션)
5. v8 Phase 1: 12 에이전트 → 3그룹 병렬 (3세션)
6. v10 Phase 0-C: 15 추출 → 3그룹 × 5 병렬 (3세션)
7. v12 Phase 0: 15 추출 → 3그룹 × 5 병렬 (3세션)
→ 병렬 미적용 시 ~80+ 세션 → 병렬 적용 시 53세션으로 압축 (34% 절감)

※ 세션 수 증가 사유 (원본 v13_plan.md 27-38세션 대비 +15~26세션):
  - 52개 스킬 통합으로 각 Phase에 스킬 실행 오버헤드 추가 (+1~2세션/Phase)
  - Phase 0-A 추출 시 /quality-gate 필수 실행으로 3세션→3세션 (변동 없음)
  - Pass 2 통합 수정 세션 추가 (3세션: 세션 49~51)
  - 원본의 "Pass 1 15~20세션"이 53세션 중 41세션에 해당 (Phase 1~7, 병렬 압축 적용)
```

## 11.4 비용 추정

```
Tier 1 (Claude 내장): $0 — 23개 스킬, 모든 Phase에서 사용
Tier 2 (pip): $0 — 23개 스킬, 설치만 필요
Tier 3 (API): 선택적 사용 (사용자 승인 2026-03-21)
  /exa-verify   → Phase 4 세션 26에서만 사용: ~$1-3 (50-100 쿼리)
  /cross-model  → Phase 8 세션 52에서만 사용: ~$2-5 (GPT-4o 1회)
  /patronus-check → 사용 안 함 ($0) — /minicheck+/hhem-verify로 대체
Tier 4 (서버): $0 (로컬) — 3개 스킬, Docker 선택

총 추가 비용: ~$3-8 (Tier 3 선택적 사용 확정)
```

## 11.5 산출물 디렉토리 구조

```
D:\VAMOS\04. 구현단계\v13_results\
├── phase0\                 ← SOT 내부 정합성
│   ├── extraction\         ← EA-{1~15}.json + DV + QG
│   ├── cross_match\        ← CM-{1~8}.json
│   └── fixes\              ← SOT 수정 기록
├── phase1_v6\              ← v6 재실행
├── phase2_v7\              ← v7 재실행
├── phase3_v8\              ← v8 재실행
├── phase4_v9\              ← v9 재실행
├── phase5_v10\             ← v10 재실행
├── phase6_v11\             ← v11 재실행
├── phase7_v12\             ← v12 재실행
├── phase8\                 ← 최종 종합 판정 (세션 52~53 산출물)
│   ├── f1_f10_verdict.json
│   ├── final_report.json
│   ├── guide_sot_sync.json
│   ├── guide_cross_match.json
│   ├── guide_hallucination.json
│   ├── guide_korean_nlp.json
│   ├── guide_quality_gate.json
│   ├── phase8_checkpoint.json
│   └── FINAL_VERDICT.json
└── pass2\                  ← Pass 2 통합 수정 (세션 49~51 산출물)
```

---

# 12. 각 Phase 시작 시 필수 체크리스트

```
□ 이전 Phase CHECKPOINT 전수 PASS 확인
□ SOT Phase 0 수정본 사용 확인
□ /sot-cache 인덱스 최신 상태 확인
□ /integrity 해시 변경 없음 확인
□ 이전 세션 phase_summary.json 로드 (5KB 이내)
□ 에이전트 산출물 JSON 디스크 저장 확인
□ /quality-gate SILVER 이상 확인 (EA/CM 관련)
```

---

# 13. 실행 시작 조건

```
v13 Enhanced 실행 시작 전:
  ✅ TOOL_GUIDE 52개 스킬 최종 점검 PASS (완료)
  ✅ v13_plan.md v13.2.0 기반 계획 수립 (완료)
  ✅ v13_enhanced_plan.md final-review PLAN-VERIFIED (2026-03-21)
  ✅ Tier 2 패키지 설치 완료: whoosh (v2.7.4), marquez-python (v0.50.0)
  ✅ phoenix starlette 버전 충돌 해결: starlette v0.52.1, phoenix v13.15.0
  ✅ Tier 3 API 키 3개 전수 설정 완료 (OpenAI, Exa, Patronus)
  ⚠️ llama_firewall: PyPI 미등록 → /input-guard로 대체 (실행 차단 아님)
  ✅ 사용자 최종 승인 (2026-03-21)

사용자 최종 승인 결정 사항 (2026-03-21):
  [D-1] Tier 3 API 사용 범위:
    선택적 사용 (비용 최적화, 예상 ~$3-8)
    - /exa-verify    → Phase 4 세션 26 (GT-4 외부사실 검증)에서만 사용
                       사유: Claude 학습 컷오프 이후 정보 검증 불가 (유일한 실질적 갭)
    - /cross-model   → Phase 8 세션 52 (최종 판정)에서 1회 사용
                       사유: Claude 자기맹점 보완, 최종 판정 신뢰도 강화
    - /patronus-check → 사용 안 함
                       사유: /minicheck + /hhem-verify (Tier 2)로 동일 기능 충분 커버

  [D-2] Phase 0 SOT 수정 범위:
    전건 수정 (CRITICAL/MAJOR/MINOR 전부 포함, 미세 부분까지)
    - 수정 후 /integrity 해시 검증 + /audit 적대적 재검증 필수
    - 수정 전후 백업 필수 (fixes/*_backup_v13.md)

  [D-3] Pass 2 통합 수정 승인 방식:
    수정 목록 사전 제시 → 사용자 리뷰 → 승인 후 수정
    - 세션 49 완료 후 merged_findings.json 사용자에게 제시
    - 사용자 승인 확인 후 세션 50 (delta-apply) 진행
    - 승인 없이 수정 진행 불가

실행 중 사용자 승인 필요 체크포인트 (3개):
  [CP-USER-1] Phase 0 완료 (세션 7 후): SOT 수정 결과 + Phase 0 Verdict 리뷰
  [CP-USER-2] Pass 2 수정 전 (세션 49 후): merged_findings.json 리뷰 → 수정 대상 확정
  [CP-USER-3] FINAL VERDICT (세션 53 후): 최종 판정 결과 확인
```

---

# 14. 세션별 실행 가이드 (Session-by-Session Execution Guide)

> 53개 세션을 순서대로 실행하기 위한 세부 Step 가이드.
> 각 세션마다 **사전조건 → Step 목록 → 산출물 확인 → 게이트** 구조로 기술.
> ABD-3 원칙: Pass 1(Phase 1~7)에서는 **발견만, 수정 없음**. 수정은 Pass 2에서 1회 통합.

### 14.0 경로 정의 및 v6 재실행 방침

```
v13 산출물 루트 (모든 세션 산출물의 기준 경로):
  D:\VAMOS\04. 구현단계\v13_results\
  ※ 세션별 "산출물:" 행의 경로는 이 루트 하위의 상대경로

SOT 경로 (68개 파일):
  D:\VAMOS\docs\sot\*
  = SRC 43개 (설계/구현/SPEC) + STEP7 작업가이드 25개

SRC 원본 경로 (v6 프롬프트 기준 44개):
  C:\Users\dkscl\OneDrive\바탕 화면\VAMOS\00. 통합\02. TECH\00. FINAL SUMMARY\STEP6_pipeline\output\updated\*
  ※ docs/sot/는 SRC의 상위집합 (STEP7-B~P 작업가이드 25개 추가)

v6 검증 대상 (PART1/PART2/RPT):
  PART1: C:\Users\dkscl\OneDrive\바탕 화면\VAMOS\04. 구현단계\VAMOS_구현가이드_PART1_진입전.md
  PART2: C:\Users\dkscl\OneDrive\바탕 화면\VAMOS\04. 구현단계\VAMOS_구현가이드_PART2_구현단계.md
  RPT:   C:\Users\dkscl\OneDrive\바탕 화면\VAMOS\04. 구현단계\검증_결과_리포트.md

v6 재실행 방침:
  - 완전 재시작 아님 — v13 프레임워크 안에서 v6 방법론을 52스킬 강화 재적용
  - 이전 결과(v8_results/phase0/, v8_results/phase1/) 참조하여 artifact-diff 수행
  - SOT 통일: 모든 Phase에서 docs/sot/ (68개)를 정본 참조 경로로 사용
  - v6 고유 대상(PART1/PART2)은 위 OneDrive 경로에서 직접 Read

이전 산출물 디렉토리 매핑:
  v6 이전 결과: D:\VAMOS\04. 구현단계\v8_results\phase1\ (Agent 대화 12개)
                D:\VAMOS\04. 구현단계\v8_results\phase0\ (0-A~0-H + IMP-A~F)
  v7 이전 결과: D:\VAMOS\04. 구현단계\v9_results\
  v8 이전 결과: D:\VAMOS\04. 구현단계\v8_results\phase0\ (구조검증)
  v9 이전 결과: D:\VAMOS\04. 구현단계\v9_results\
  v10 이전 결과: D:\VAMOS\04. 구현단계\v10_results\
  v11 이전 결과: D:\VAMOS\04. 구현단계\v11_results\
  v12 이전 결과: D:\VAMOS\04. 구현단계\v12\v12_results\
```

---

## Phase 0: SOT 내부 정합성 검증 (세션 1~7)

### 세션 1: SOT 전수 추출 — Group 1

```
사전조건: Tier 1+2 스킬 설치 완료, docs/sot/* 68개 파일 접근 가능
실행모드: 5 에이전트 병렬

Step 1: /sot-cache 실행 — 68개 SOT 파일 인덱스 구축
Step 2: EA-1 에이전트 — CLAUDE.md 추출 → v13_EA01.json
        /extract + /validate DV-1~DV-7 + /quality-gate
Step 3: EA-2 에이전트 — BASE-1.3*.md 추출 → v13_EA02.json (Step 2와 병렬)
        /extract + /validate + /quality-gate
Step 4: EA-3 에이전트 — PLAN-*.md 추출 → v13_EA03.json (Step 2와 병렬)
        /extract + /validate + /quality-gate
Step 5: EA-4 에이전트 — VAMOS_MASTER*.md 추출 → v13_EA04.json (Step 2와 병렬)
        /extract + /validate + /quality-gate
Step 6: EA-5 에이전트 — D2.0-01*.md, D2.0-02*.md 추출 → v13_EA05.json (Step 2와 병렬)
        /extract + /validate + /quality-gate + /input-guard + /korean-nlp
Step 7: 각 EA JSON에 /json-repair 실행 (구조 오류 시)
Step 8: /integrity — 5개 EA JSON SHA-256 해시 기록
Step 9: /docling — 복잡 테이블 SOT 구조 파싱 (해당 시)
Step 10: /gpt-cache — 반복 추출 캐싱 설정

산출물: phase0/extraction/v13_EA01~05.json
        phase0/extraction/validation/*_dv.json, *_qg.json
게이트: 5개 EA 전수 SILVER+ 판정 확인
```

### 세션 2: SOT 전수 추출 — Group 2

```
사전조건: 세션 1 추출 인덱스 참조 가능
실행모드: 5 에이전트 병렬

Step 1: EA-6 에이전트 — D2.0-03~04*.md 추출 → v13_EA06.json
Step 2: EA-7 에이전트 — D2.0-05~06*.md 추출 → v13_EA07.json (병렬)
Step 3: EA-8 에이전트 — D2.0-07~08*.md 추출 → v13_EA08.json (병렬)
Step 4: EA-9 에이전트 — D2.1-*.md 추출 → v13_EA09.json (병렬)
Step 5: EA-10 에이전트 — PHASE_B1~B3*.md 추출 → v13_EA10.json (병렬)
Step 6: 각 EA JSON /validate DV + /quality-gate 실행
Step 7: /json-repair (구조 오류 시) + /integrity 해시 기록

산출물: phase0/extraction/v13_EA06~10.json + validation/*
게이트: 5개 EA 전수 SILVER+ 판정 확인
```

### 세션 3: SOT 전수 추출 — Group 3

```
사전조건: 세션 1~2 추출 완료
실행모드: 5 에이전트 병렬

Step 1: EA-11 에이전트 — PHASE_B4~B7*.md 추출 → v13_EA11.json
Step 2: EA-12 에이전트 — *SPEC*-1~3.md 추출 → v13_EA12.json (병렬)
Step 3: EA-13 에이전트 — *SPEC*-4~5.md 추출 → v13_EA13.json (병렬)
Step 4: EA-14 에이전트 — STEP7-*.md 추출 → v13_EA14.json (병렬)
Step 5: EA-15 에이전트 — *READINESS*.md, *BEGINNER*.md 추출 → v13_EA15.json (병렬)
Step 6: 각 EA JSON /validate DV + /quality-gate 실행
Step 7: /integrity — 전체 15개 EA JSON 해시 최종 기록
Step 8: 전수 추출 완료 확인 — 68개 SOT × 15 EA = 누락 0건 확인

산출물: phase0/extraction/v13_EA11~15.json + validation/*
게이트: 15개 EA 전수 SILVER+ 판정 확인 → Phase 0-A 완료
```

### 세션 4: 크로스 매칭 — Group A

```
사전조건: Phase 0-A 완료 (세션 1~3), 15개 EA JSON 전수 접근 가능
실행모드: 4 에이전트 병렬

Step 1: CM-1 에이전트 — 동일값 매칭 → v13_CM01.json
        /cross-match C1 + /symbolic-verify
Step 2: CM-2 에이전트 — 개수 검증 → v13_CM02.json (병렬)
        /cross-match C2 + /fact-audit
Step 3: CM-3 에이전트 — 분류 매칭 → v13_CM03.json (병렬)
        /cross-match C3 + /sot-conflict
Step 4: CM-4 에이전트 — 명명 매칭 → v13_CM04.json (병렬)
        /cross-match C4 + /deep-diff
Step 5: 4개 CM JSON /validate DV 실행
Step 6: /completeness-map — CM1~4 오류 카테고리 매트릭스 생성

산출물: phase0/cross_match/v13_CM01~04.json + validation/*
게이트: 4개 CM 전수 완료 확인
```

### 세션 5: 크로스 매칭 — Group B

```
사전조건: Phase 0-A 완료, CM-1~4 참조 가능
실행모드: 4 에이전트 병렬

Step 1: CM-5 에이전트 — 범위 매칭 → v13_CM05.json
        /cross-match C5 + /symbolic-verify
Step 2: CM-6 에이전트 — 버전 매칭 → v13_CM06.json (병렬)
        /cross-match C6 + /deep-diff
Step 3: CM-7 에이전트 — 수식 매칭 → v13_CM07.json (병렬)
        /cross-match C7 + /symbolic-verify
Step 4: CM-8 에이전트 — 참조 매칭 → v13_CM08.json (병렬)
        /cross-match C8 + /json-diff
Step 5: 8개 CM JSON 전수 /validate DV 실행
Step 6: /completeness-map — CM1~8 전체 오류 카테고리 매트릭스 통합

산출물: phase0/cross_match/v13_CM05~08.json + validation/*
게이트: 8개 CM 전수 완료 → Phase 0-B 완료
```

### 세션 6: 불일치 확정 및 심각도 분류

```
사전조건: Phase 0-B 완료 (세션 4~5), 8개 CM + 15개 EA 전수 접근 가능
실행모드: 순차

Step 1: /cross-examine — CM 결과에서 불일치 후보 목록 추출
Step 2: /consensus — 다중 관점 합의로 불일치 확정 (오탐 제거)
Step 3: /hallucination-check — SOT 원본 대조로 환각 여부 확인
Step 4: /confidence — 각 불일치 항목 신뢰도 보정
Step 5: 심각도 분류: CRITICAL (데이터 무결성) / MAJOR (논리 오류) / MINOR (표현 불일치)
Step 6: v13_sot_inconsistency_list.json 저장

산출물: phase0/v13_sot_inconsistency_list.json
게이트: 심각도 분류 완료, CRITICAL 건수 확인
```

### 세션 7: SOT 수정 및 적대적 재검증

```
사전조건: 세션 6 완료, 불일치 목록 확정
실행모드: 순차
※ 전건 수정 (D-2): CRITICAL/MAJOR/MINOR 전부 포함, 미세 부분까지 수정

Step 1: 전체 불일치 항목(CRITICAL+MAJOR+MINOR) 수정 제안 작성 → v13_sot_fix_proposals.json
Step 2: /delta-apply — SOT 원본에 전건 수정 적용 (D-2)
Step 3: /integrity — 수정 전후 SHA-256 해시 비교 기록
Step 4: 수정된 SOT 백업 저장 → fixes/*_backup_v13.md
Step 5: /audit — 적대적 감사 (수정 타당성 검증)
Step 6: /golden-set reverify — 정답 데이터 재확인
Step 7: /cross-examine — 수정이 새로운 불일치 유발하지 않음 확인
Step 8: v13_phase0_verdict.md 작성 (Phase 0 전체 판정)
Step 9: v13_adversarial_review.json 저장

산출물: phase0/v13_sot_fix_proposals.json
        phase0/v13_sot_delta.json
        phase0/fixes/*_backup_v13.md, v13_sot_corrections.md
        phase0/v13_adversarial_review.json
        phase0/v13_phase0_verdict.md
게이트: Phase 0 CHECKPOINT 전항 PASS → Phase 1 진입 가능
```

---

## Phase 1: v6 전수 재실행 (세션 8~11)

### 세션 8: v6 Phase 0 — 8개 스크립트 전수 실행

```
사전조건: Phase 0 CHECKPOINT PASS, SOT 수정본 사용
실행모드: 순차 (8 스크립트)
검증대상: PART1 + PART2 + RPT (v6 프롬프트 §3 기준, 14.0절 경로 참조)

Step 1: □ 이전 Phase CHECKPOINT 전수 PASS 확인
Step 2: □ /sot-cache 인덱스 최신 상태 확인
Step 3: 0-A 테이블 검증 — /validate DV-1
Step 4: 0-B 산술 검증 — /validate DV-2 + /symbolic-verify
Step 5: 0-C 제목 구조 검증 — /validate DV-5
Step 6: 0-D LOCK 값 검증 — /symbolic-verify + /sot-conflict
Step 7: 0-E 수치 불일치 검증 — /validate DV-7 + /fact-audit
Step 8: 0-F ID 유일성 검증 — /validate DV-1
Step 9: 0-G HTML 주석 검증 — /deep-diff
Step 10: 0-H 헤더 수 검증 — /cross-match
Step 11: phase0_summary.json 통합 저장

산출물: phase1_v6/phase0/0-A~0-H_result.json
        phase1_v6/phase0/phase0_summary.json
게이트: 8개 스크립트 전수 실행 완료 확인 (PC1-1)
```

### 세션 9: v6 Agent 1~3 — 순방향+역방향 검증 (§6.1~6.10)

```
사전조건: 세션 8 완료
실행모드: 3 에이전트 병렬

Step 1: Agent 1 — §6.1~§6.4 ORANGE CORE 검증
        /hallucination-check + /sot-check + /cross-examine
        입력: docs/sot/D2.0-01~02*.md
Step 2: Agent 2 — §6.5~§6.8 BLUE/Storage 검증 (병렬)
        /hallucination-check + /sot-check + /sot-rag
        입력: docs/sot/D2.0-03~06*.md
Step 3: Agent 3 — §6.9~§6.10 Safety/Cost 검증 (병렬)
        /symbolic-verify + /guardrails-validate + /input-guard
        입력: docs/sot/D2.0-07~08*.md
Step 4: 각 Agent findings JSON 저장

산출물: phase1_v6/agent1_findings.json
        phase1_v6/agent2_findings.json
        phase1_v6/agent3_findings.json
게이트: 3개 Agent 순방향 검증 완료
```

### 세션 10: v6 Agent 4~5 — 순방향+역방향 검증 (§6.11~§5)

```
사전조건: 세션 8~9 완료
실행모드: 2 에이전트 병렬

Step 1: Agent 4 — §6.11~6.13 UI/CI/Version + PART1 검증
        /cross-match + /deep-diff + /fact-audit
        입력: docs/sot/PHASE_B*.md
Step 2: Agent 5 — §3~§5 V1/V2/V3 Phase 검증 (병렬)
        /completeness-map + /cross-examine + /consensus
        입력: docs/sot/PLAN*.md
Step 3: 각 Agent findings JSON 저장

산출물: phase1_v6/agent4_findings.json
        phase1_v6/agent5_findings.json
게이트: Agent 1~5 순방향+역방향 전수 완료 (PC1-2, PC1-3)
```

### 세션 11: v6 적대적 감사 + 발견 기록

```
사전조건: 세션 9~10 완료 (Agent 1~5 결과)
실행모드: 순차

Step 1: /audit — Agent 1~5 결과에 대한 적대적 감사 (Agent 6)
Step 2: /cross-examine — 모순 탐지
Step 3: /minicheck — NLI 기반 충실성 검증
Step 4: /eval-ea — EA 추출 결과 평가
Step 5: /golden-set reverify — 정답 데이터 재확인
Step 6: /artifact-diff — 이전 v6 산출물(v8_results/phase1/ + v8_results/phase0/) 대비 변경점 기록
Step 7: P1~P11 오류 패턴 탐지 결과 기록
Step 8: phase1_findings.json 저장 (발견만, 수정 없음 — ABD-3)
Step 9: phase1_checkpoint.json 저장 (PC1-1~PC1-7 판정)

산출물: phase1_v6/adversarial_review.json
        phase1_v6/artifact_diff.json
        phase1_v6/phase1_findings.json
        phase1_v6/phase1_checkpoint.json
게이트: PC1-1~PC1-7 전항 PASS → Phase 2 진입 가능
```

---

## Phase 2: v7 전수 재실행 (세션 12~16)

### 세션 12: v7 Phase 0 — 8개 스크립트 전수 실행

```
사전조건: Phase 1 CHECKPOINT PASS
실행모드: 순차

Step 1: □ Phase 1 CHECKPOINT 전수 PASS 확인
Step 2: □ /sot-cache 인덱스 최신 확인
Step 3: 0-A~0-H 8개 스크립트 순차 실행 (세션 8과 동일 구조, v7 SOT 대상)
        /validate + /symbolic-verify
Step 4: phase0_summary.json 저장

산출물: phase2_v7/phase0/0-A~0-H_result.json
게이트: 8개 스크립트 전수 실행 완료 (PC2-1)
```

### 세션 13: v7 Agent 1~3 — Core/Security/SDAR

```
사전조건: 세션 12 완료
실행모드: 3 에이전트 병렬

※ 각 Agent는 STEP A(순방향: PART→원본 대조) + STEP B(역방향: 원본→PART 누락확인) 수행

Step 1: Agent 1 — PART2 §2 Core 검증
        STEP A: /hallucination-check + /validate DV-4
        STEP B: /sot-check + /cross-examine
Step 2: Agent 2 — PART2 §6.9~6.10 Security 검증 (병렬)
        STEP A: /guardrails-validate + /hallucination-check
        STEP B: /sot-check + /cross-examine
Step 3: Agent 3 — SDAR 설계문서 검증 (병렬)
        STEP A: /validate DV-4 + /symbolic-verify
        STEP B: /sot-check + /cross-examine
Step 4: 각 Agent findings JSON 저장

산출물: phase2_v7/agent1~3_findings.json
게이트: 3개 Agent 순방향+역방향 검증 완료
```

### 세션 14: v7 Agent 4~6 — Teams/Schema/Memory

```
사전조건: 세션 13 완료
실행모드: 3 에이전트 병렬

※ 각 Agent는 STEP A(순방향) + STEP B(역방향) 수행

Step 1: Agent 4 — PART2 §6.4~6.6 Teams/MCP 검증
        STEP A: /hallucination-check + /validate DV-4
        STEP B: /cross-match + /sot-rag
Step 2: Agent 5 — D2.1 Schema 문서 검증 (병렬)
        STEP A: /ragas-eval + /hallucination-check
        STEP B: /sot-check + /cross-examine
Step 3: Agent 6 — PART2 §6.5~6.6 Memory/RAG 검증 (병렬)
        STEP A: /hallucination-check + /validate DV-4
        STEP B: /sot-check + /ragas-eval
Step 4: 각 Agent findings JSON 저장

산출물: phase2_v7/agent4~6_findings.json
게이트: 6개 Agent 누적 순방향+역방향 검증 완료
```

### 세션 15: v7 Agent 7~10 — UI/Infra/Decision/Domain

```
사전조건: 세션 14 완료
실행모드: 4 에이전트 병렬

※ 각 Agent는 STEP A(순방향) + STEP B(역방향) 수행

Step 1: Agent 7 — PART2 §6.7~6.8 UI/UX 검증
        /completeness-map + /deep-diff + /hallucination-check
Step 2: Agent 8 — PART2 §6.11 CI/CD/Infra 검증 (병렬)
        /fact-audit + /cross-examine + /sot-check
Step 3: Agent 9 — PART2 §7 Decision 검증 (병렬)
        /hallucination-check + /cross-examine
Step 4: Agent 10 — AI 투자 도메인 문서 검증 (병렬)
        /fact-audit + /hallucination-check
Step 5: 각 Agent findings JSON 저장

산출물: phase2_v7/agent7~10_findings.json
게이트: 10개 Agent 전수 완료
```

### 세션 16: v7 적대적 감사 + 발견 기록

```
사전조건: 세션 13~15 완료 (Agent 1~10 결과)
실행모드: 순차

Step 1: /audit — Agent 1~10 결과 적대적 감사 (Agent 11)
Step 2: /cross-examine + /minicheck + /hhem-verify
Step 3: 50+ 스팟체크 수행 (189건 체크항목 중 임의 추출)
Step 4: 18 Tiers 분류별 검증 결과 집계 (PC2-4) — 세션 13~15 Agent 결과에서 산출
Step 5: P1~P11 오류 패턴 탐지 결과 집계 (PC2-5) — 세션 13~15 findings에서 추출
Step 6: /artifact-diff — 이전 v7 산출물(v9_results/) 대비 변경점 기록
Step 7: Ripple Map 생성 → ripple_map.json
Step 8: phase2_findings.json 저장 (발견만, 수정 없음)
Step 9: phase2_checkpoint.json 저장 (PC2-1~PC2-8 판정)

산출물: phase2_v7/adversarial_review.json
        phase2_v7/ripple_map.json
        phase2_v7/artifact_diff.json
        phase2_v7/phase2_findings.json
        phase2_v7/phase2_checkpoint.json
게이트: PC2-1~PC2-8 전항 PASS → Phase 3 진입 가능
```

---

## Phase 3: v8 전수 재실행 (세션 17~22)

### 세션 17: v8 Phase 0 — 14개 스크립트 전수 실행

```
사전조건: Phase 2 CHECKPOINT PASS
실행모드: 순차 (8 구조 + 6 구현)

Step 1: □ Phase 2 CHECKPOINT 전수 PASS 확인
Step 2: 0-A~0-H 구조 검증 8개 스크립트 실행
        /validate + /symbolic-verify
Step 3: IMP-A 파일경로 — /sot-search + Phase B2 교차 확인
Step 4: IMP-B 의존순서 — /symbolic-verify (순환 탐지)
Step 5: IMP-C 단위/형식 — /korean-nlp + /validate DV-6
Step 6: IMP-D 타임아웃 — /symbolic-verify + /fact-audit
Step 7: IMP-E 오류코드 — /cross-match C8 (참조 무결성)
Step 8: IMP-F 테스트 커버리지 — /completeness-map
Step 9: struct_result.json + impl_result.json 저장

산출물: phase3_v8/phase0/struct_result.json
        phase3_v8/phase0/impl_result.json
게이트: 14개 스크립트 전수 실행 완료 (PC3-1)
```

### 세션 18: v8 Agent 1~4 — V0~V3 버전별 검증

```
사전조건: 세션 17 완료
실행모드: 4 에이전트 병렬

Step 1: Agent 1 — V0 버전 검증
        /prompt-test + /guardrails-validate
Step 2: Agent 2 — V1 버전 검증 (병렬)
        /hallucination-check + /validate DV-4
Step 3: Agent 3 — V2 버전 검증 (병렬)
        /sot-check + /hallucination-check
Step 4: Agent 4 — V3 버전 검증 (병렬)
        /prompt-test + /sot-check
Step 5: 각 Agent findings JSON 저장

산출물: phase3_v8/agent1~4_findings.json
게이트: 4개 버전별 Agent 완료 (Dim B+C, PC3-2 부분)
```

### 세션 19: v8 Agent 5~8 — §6 상세 검증

```
사전조건: 세션 18 완료
실행모드: 4 에이전트 병렬

Step 1: Agent 5 — §6.1~6.3 검증
        /hallucination-check + /cross-examine
Step 2: Agent 6 — §6.4~6.6 검증 (병렬)
        /ragas-eval + /giskard-scan
Step 3: Agent 7 — §6.7~6.8 검증 (병렬)
        /hallucination-check + /cross-examine
Step 4: Agent 8 — §6.9~6.10 검증 (병렬)
        /giskard-scan + /guardrails-validate
Step 5: 각 Agent findings JSON 저장

산출물: phase3_v8/agent5~8_findings.json
게이트: 8개 Agent 누적 완료 (Dim B+C, PC3-2 부분 + PC3-5)
        ※ IMP-A~F 구현가능성 검증은 세션 17에서 완료
```

### 세션 20: v8 Agent 9~12 — §6.11~§7 + 프롬프트 + 트리플 매핑

```
사전조건: 세션 19 완료
실행모드: 4 에이전트 병렬

Step 1: Agent 9 — §6.11~§7 검증
        /cross-examine (※ /cross-model은 Phase 8 세션 52에서만 사용 — D-1)
Step 2: Agent 10 — 프롬프트 검증 (병렬)
        /dspy-optimize + /prompt-test
Step 3: Agent 11 — 트리플 매핑 검증 (병렬)
        /eval-audit + /validate-evaluator
Step 4: Agent 12 — 메타 평가 (병렬)
        /write-judge-prompt + /eval-audit
Step 5: 각 Agent findings JSON 저장

산출물: phase3_v8/agent9~12_findings.json
게이트: 12개 Agent 전수 완료 (Dim B+C+D, PC3-2 완료 + PC3-6)
```

### 세션 21: v8 적대적 감사

```
사전조건: 세션 18~20 완료 (Agent 1~12 결과)
실행모드: 순차

Step 1: /audit — Agent 1~12 결과 적대적 감사 (Agent 13)
Step 2: /cross-examine — 모순 탐지
Step 3: /minicheck + /consensus — 다중 관점 합의
Step 4: /write-judge-prompt — 판정 프롬프트 품질 확인
Step 5: adversarial_review.json 저장

산출물: phase3_v8/adversarial_review.json
게이트: 적대적 감사 완료, 오판율 ≤15% 확인 (PC3-7)
```

### 세션 22: v8 발견 기록

```
사전조건: 세션 21 완료
실행모드: 순차

Step 1: /artifact-diff — 이전 v8 산출물(v8_results/phase0/ 구조검증분) 대비 변경점 기록
Step 2: P1~P11 + I1~I12 + PR1~PR5 오류 패턴 탐지 결과 기록 (PC3-4)
        ※ P1~P11: 세션 18~20 Agent findings에서 집계
        ※ I1~I12(구현): 세션 17 IMP-A~F 결과에서 집계
        ※ PR1~PR5(프롬프트): 세션 20 Agent 10~12 결과에서 집계
Step 3: ~791항목 전수 검증 결과 집계 (PC3-3) — 세션 17~21 누적
Step 4: Ripple Map 생성
Step 5: phase3_findings.json 저장 (발견만, 수정 없음)
Step 6: phase3_checkpoint.json 저장 (PC3-1~PC3-8 판정)

산출물: phase3_v8/ripple_map.json
        phase3_v8/artifact_diff.json
        phase3_v8/phase3_findings.json
        phase3_v8/phase3_checkpoint.json
게이트: PC3-1~PC3-8 전항 PASS → Phase 4 진입 가능
```

---

## Phase 4: v9 전수 재실행 (세션 23~27)

### 세션 23: Phase -1 + Phase 0-Pre — GT 재구축

```
사전조건: Phase 3 CHECKPOINT PASS
실행모드: 순차

Step 1: □ Phase 3 CHECKPOINT 전수 PASS 확인
Step 2: /integrity — PART2 무결성 확인
Step 3: /sot-cache + /sot-search — SRC 동기화
Step 4: /lineage — 데이터 계보 추적 설정
Step 5: GT-1 파일경로 GT 재구축 → gt1_filepath.json
        /symbolic-verify + /validate DV-2
Step 6: GT-2 산출물체인 GT 재구축 → gt2_artifact_chain.json
        /lineage
Step 7: GT-3 수량 GT 재구축 → gt3_quantity.json
        /fact-audit
Step 8: GT-4 외부사실 GT 재구축 → gt4_external.json
        /exa-verify (Tier 3 확정 — D-1) + /fact-audit
Step 9: GT-5 기술실행가능성 GT 재구축 → gt5_feasibility.json
        /giskard-scan + /prompt-test
Step 10: phase-1/integrity.json 저장

산출물: phase4_v9/phase-1/integrity.json
        phase4_v9/gt/gt1~gt5.json (5개 Ground Truth)
게이트: 5개 GT 전수 구축 완료 (PC4-1, PC4-2)
```

### 세션 24: Phase 0 프롬프트 작성 + 시범

```
사전조건: 세션 23 완료 (GT 5개)
실행모드: 순차

Step 1: /prompt-test — 6개 관점(A~F) 프롬프트 작성
Step 2: /dspy-optimize — 프롬프트 최적화
Step 3: Phase 0-Validate 시범 실행
Step 4: 시범 결과 확인 → phase0_validate.json 저장

산출물: phase4_v9/prompts/prompt_A~F.md
        phase4_v9/phase0_validate.json
게이트: 6개 관점 프롬프트 준비 완료
```

### 세션 25: Phase 1 Wave 1+2 — 관점 A/B/C

```
사전조건: 세션 24 완료
실행모드: 순차 (Wave 간 의존성)

Step 1: Wave 1 — 관점 A 실행 (파일경로)
        /symbolic-verify (의존순서)
Step 2: Wave 1 — 관점 B 실행 (산출물체인)
        /sot-search (경로 일관성)
Step 3: Wave 2 — 관점 C 실행 (수량 일관성)
        /cross-match (수량 일관성)
Step 4: Wave 1+2 결과 통합 → wave1_ABC.json 저장

산출물: phase4_v9/wave1_ABC.json
게이트: Wave 1+2 완료, 3개 관점 검증 완료
```

### 세션 26: Phase 1 Wave 3 — 관점 D/E/F

```
사전조건: 세션 25 완료 (Wave 1+2 결과 참조 필요)
실행모드: 순차

Step 1: Wave 3 — 관점 D 실행 (외부사실)
        /exa-verify (Tier 3 사용 확정 — D-1) + /fact-audit (외부사실 검증 — GT-4 대응)
Step 2: Wave 3 — 관점 E 실행 (수량)
        /fact-audit + /symbolic-verify (수량 검증)
Step 3: Wave 3 — 관점 F 실행 (기술실행가능성)
        /giskard-scan + /prompt-test (GT-5 대응, 세션 23 GT 구축 스킬과 일치)
Step 4: Wave 3 결과 통합 → wave3_DEF.json 저장

산출물: phase4_v9/wave3_DEF.json
게이트: 6개 관점 × 3 Wave 전수 완료
```

### 세션 27: v9 발견 기록 + RULE 1~14 검증

```
사전조건: 세션 26 완료
실행모드: 순차

Step 1: RULE 1~14 준수 여부 전수 확인
        /validate + /symbolic-verify + /korean-nlp
        ※ RULE 정의: docs/sot/BASE-1.3*.md 의 14개 규칙 참조
Step 2: GT 대비 실제 데이터 일치율 산출 — 세션 25~26 Wave 결과 집계 (PC4-5)
        /cross-examine + /confidence
Step 3: /artifact-diff — 이전 v9 산출물(v9_results/) 대비 변경점 기록
Step 4: rule_compliance.json 저장 (RULE 1~14)
Step 5: phase4_findings.json 저장 (발견만, 수정 없음)
Step 6: phase4_checkpoint.json 저장 (PC4-1~PC4-8 판정)

산출물: phase4_v9/rule_compliance.json
        phase4_v9/phase4_findings.json
        phase4_v9/phase4_checkpoint.json
게이트: PC4-1~PC4-8 전항 PASS → Phase 5 진입 가능
```

---

## Phase 5: v10 전수 재실행 (세션 28~34)

### 세션 28: v10 Phase 0-A + 0-B — 정의 + 인덱스

```
사전조건: Phase 4 CHECKPOINT PASS
실행모드: 순차

Step 1: □ Phase 4 CHECKPOINT 전수 PASS 확인
Step 2: Phase 0-A — 정의 추출
        /extract + /sot-cache + /korean-nlp
Step 3: Phase 0-B — CLAUDE.md 인덱스 구축
Step 4: definitions.json + index.json 저장

산출물: phase5_v10/phase0/definitions.json
        phase5_v10/phase0/index.json
게이트: Phase 0-A/B 완료
```

### 세션 29: v10 Phase 0-C — 추출 Group 1

```
사전조건: 세션 28 완료
실행모드: 5 에이전트 병렬

Step 1: C-1~C-5 에이전트 — 5개 SOT 그룹 추출 (병렬)
        /extract + /validate DV + /quality-gate + /docling + /gpt-cache
Step 2: 5개 src_C01~C05.json 저장
Step 3: /integrity 해시 기록

산출물: phase5_v10/features/src_C01~C05.json + validation/*
게이트: Group 1 추출 완료
```

### 세션 30: v10 Phase 0-C — 추출 Group 2

```
사전조건: 세션 29 완료
실행모드: 5 에이전트 병렬

Step 1: C-6~C-10 에이전트 — 5개 SOT 그룹 추출 (병렬)
Step 2: 5개 src_C06~C10.json 저장
Step 3: /integrity 해시 기록

산출물: phase5_v10/features/src_C06~C10.json + validation/*
게이트: Group 2 추출 완료
```

### 세션 31: v10 Phase 0-C — 추출 Group 3

```
사전조건: 세션 30 완료
실행모드: 5 에이전트 병렬

Step 1: C-11~C-15 에이전트 — 5개 SOT 그룹 추출 (병렬)
Step 2: 5개 src_C11~C15.json 저장
Step 3: /integrity — 전체 15개 추출 해시 최종 기록
Step 4: 68개 SOT 전수 추출 확인 — 누락 0건

산출물: phase5_v10/features/src_C11~C15.json + validation/*
게이트: 15개 에이전트 전수 추출 완료 → Phase 0-C 완료
```

### 세션 32: v10 Phase 0-D~F — 교차검증 + 대사 + 레지스트리

```
사전조건: 세션 29~31 완료
실행모드: 순차

Step 1: Phase 0-D — /cross-match 교차 검증
Step 2: Phase 0-E — /deep-diff + /json-diff 대사(Reconciliation)
Step 3: Phase 0-F — /golden-set 레지스트리 확정
Step 4: v10 이전 산출물(v10_results/) 대비 delta 기록
Step 5: feature_registry.json + v10_delta.json 저장

산출물: phase5_v10/feature_registry.json
        phase5_v10/v10_delta.json
게이트: Feature Registry 확정 + 이전 산출물 대사 완료 (PC5-1~PC5-3)
```

### 세션 33: v10 Phase 1 — 6 매핑 에이전트

```
사전조건: 세션 32 완료
실행모드: 3 에이전트 병렬 × 2 그룹

Step 1: Group 1 — 매핑 에이전트 1~3 (§2~§4 매핑, 병렬)
        /cross-match + /hallucination-check + /sot-check
Step 2: Group 2 — 매핑 에이전트 4~6 (§5~§7 매핑, 병렬)
        /cross-match + /hallucination-check + /sot-check
Step 3: 6개 매핑 결과 통합 → mapping/sect2~7.json 저장

산출물: phase5_v10/mapping/sect2~7.json
게이트: 6개 매핑 전수 완료 (PC5-4~PC5-7)
```

### 세션 34: v10 적대적 감사 + 발견 기록

```
사전조건: 세션 33 완료
실행모드: 순차

Step 1: /audit — 매핑 결과 적대적 감사 (PC5-7)
Step 2: /cross-examine + /minicheck
Step 3: /golden-set 기반 정답 대비 정확도 확인 (PC5-8)
Step 4: phase5_findings.json 저장 (발견만, 수정 없음) (PC5-9)
Step 5: phase5_checkpoint.json 저장 (PC5-1~PC5-9 판정)

산출물: phase5_v10/adversarial_review.json
        phase5_v10/phase5_findings.json
        phase5_v10/phase5_checkpoint.json
게이트: PC5-1~PC5-9 전항 PASS → Phase 6 진입 가능
```

---

## Phase 6: v11 전수 재실행 (세션 35~41)

### 세션 35: v11 Phase 0 — 7 인덱스 재구축

```
사전조건: Phase 5 CHECKPOINT PASS
실행모드: 순차

Step 1: □ Phase 5 CHECKPOINT 전수 PASS 확인
Step 2: 0-A~0-G 7개 인덱스 순차 재구축
        /sot-cache + /extract + /validate
Step 3: phase5_v10/feature_registry.json 참조
Step 4: 7개 인덱스 JSON 저장

산출물: phase6_v11/index/0-A~0-G.json
게이트: 7개 인덱스 재구축 완료 (PC6-1)
```

### 세션 36: v11 Phase 1 Wave 1 — 수치/참조

```
사전조건: 세션 35 완료
실행모드: 순차

Step 1: Agent 1 — 수치 검증
        /symbolic-verify + /validate DV-2/7
Step 2: Agent 2 — 참조 검증
        /fact-audit + /sot-conflict (LOCK 값 자가모순)
Step 3: Agent 3 — 추가 수치/참조 검증
Step 4: wave1_findings.json 저장

산출물: phase6_v11/wave1_findings.json
게이트: Wave 1 완료 (PC6-2)
```

### 세션 37: v11 Phase 1 Wave 2 — 구조/매핑

```
사전조건: 세션 36 완료
실행모드: 순차

Step 1: Agent 4 — 구조 검증
        /cross-match + /completeness-map
Step 2: Agent 5 — 매핑 검증
        /deep-diff
Step 3: Agent 6 — 추가 구조/매핑 검증
Step 4: wave2_findings.json 저장

산출물: phase6_v11/wave2_findings.json
게이트: Wave 2 완료 (PC6-3)
```

### 세션 38: v11 Phase 1 Wave 3 — 프롬프트

```
사전조건: 세션 37 완료
실행모드: 순차

Step 1: Agent 7 — 프롬프트 검증
        /prompt-test + /validate-evaluator
Step 2: Agent 8 — 환각 검증
        /hallucination-check
Step 3: Agent 9 — 추가 프롬프트 검증
Step 4: wave3_findings.json 저장

산출물: phase6_v11/wave3_findings.json
게이트: Wave 3 완료 (PC6-4)
```

### 세션 39: v11 Phase 1 Wave 4 — 고급 검증

```
사전조건: 세션 38 완료
실행모드: 순차

Step 1: Agent 10 — 기술 실현가능성/보안
        /giskard-scan
Step 2: Agent 11 — RAG 관련 검증
        /ragas-eval
Step 3: Agent 12 — 메타 평가
        /eval-audit
Step 4: Agent 13 — 보안 커버리지
        /guardrails-validate
Step 5: wave4_findings.json 저장

산출물: phase6_v11/wave4_findings.json
게이트: Wave 4 완료 (PC6-5)
```

### 세션 40: v11 Phase 1 Wave 5 — 사용성

```
사전조건: 세션 39 완료
실행모드: 순차

Step 1: Agent 14 — 문서 발견가능성
        /korean-nlp + /docling
Step 2: wave5_findings.json 저장

산출물: phase6_v11/wave5_findings.json
게이트: Wave 5 완료 (PC6-6) + 전수 누적 확인 (PC6-7~PC6-9)
```

### 세션 41: v11 적대적 감사 + BP 준비 + 발견 기록

```
사전조건: 세션 36~40 완료
실행모드: 순차

Step 1: /audit — Wave 1~5 결과 적대적 감사 (Agent 15)
Step 2: /cross-examine + /consensus + /debate
Step 3: BP-1~15 원본 보호 프로토콜 준비 → bp_preparation.json
Step 4: /artifact-diff — 이전 v11 산출물(v11_results/) 대비 변경점 기록
Step 5: phase6_findings.json 저장 (발견만, 수정 없음)
Step 6: phase6_checkpoint.json 저장 (PC6-1~PC6-14 판정)

산출물: phase6_v11/adversarial_review.json
        phase6_v11/bp_preparation.json
        phase6_v11/phase6_findings.json
        phase6_v11/phase6_checkpoint.json
게이트: PC6-1~PC6-14 전항 PASS → Phase 7 진입 가능
```

---

## Phase 7: v12 전수 재실행 (세션 42~48)

### 세션 42: v12 Phase 0 — 추출 Group 1

```
사전조건: Phase 6 CHECKPOINT PASS
실행모드: 5 에이전트 병렬

Step 1: □ Phase 6 CHECKPOINT 전수 PASS 확인
Step 2: 15 추출 에이전트 중 Group 1 (5개) 실행
        /extract + /validate DV + /quality-gate + /sot-cache + /docling + /gpt-cache
Step 3: src_01~05.json 저장

산출물: phase7_v12/features/src_01~05.json + validation/*
게이트: Group 1 추출 완료
```

### 세션 43: v12 Phase 0 — 추출 Group 2

```
사전조건: 세션 42 완료
실행모드: 5 에이전트 병렬

Step 1: Group 2 (5개) 추출 실행
Step 2: src_06~10.json 저장

산출물: phase7_v12/features/src_06~10.json + validation/*
게이트: Group 2 추출 완료
```

### 세션 44: v12 Phase 0 — 추출 Group 3

```
사전조건: 세션 43 완료
실행모드: 5 에이전트 병렬

Step 1: Group 3 (5개) 추출 실행
Step 2: src_11~15.json 저장
Step 3: /integrity — 전체 15개 추출 해시 최종 기록
Step 4: 68개 SOT 전수 추출 확인 — 누락 0건

산출물: phase7_v12/features/src_11~15.json + validation/*
게이트: 15개 에이전트 전수 추출 완료 (PC7-1)
```

### 세션 45: v12 Phase 1 — 7 매핑 에이전트

```
사전조건: 세션 42~44 완료
실행모드: 순차

Step 1: 7 매핑 에이전트 — PART2 §2~§7 매핑
        /cross-match + /hallucination-check + /sot-check
Step 2: mapping.json + feature_registry.json 저장

산출물: phase7_v12/mapping/mapping.json
        phase7_v12/feature_registry.json
게이트: 매핑 완료, Feature Registry 확정 (PC7-2, PC7-3)
```

### 세션 46: v12 적대적 감사

```
사전조건: 세션 45 완료
실행모드: 순차

Step 1: /audit — 매핑 결과 적대적 감사
Step 2: /cross-examine + /minicheck + /hhem-verify
Step 3: adversarial_review.json 저장

산출물: phase7_v12/adversarial_review.json
게이트: 적대적 감사 완료 (PC7-4)
```

### 세션 47: v10 교차 + v7 역방향 검증

```
사전조건: 세션 46 완료
실행모드: 순차

Step 1: v10 교차 검증 — Phase 5 산출물 ↔ v12 결과
        /deep-diff + /json-diff + /cross-match
        입력: phase5_v10/feature_registry.json  (※ 산출물 루트: v13_results/)
              + D:\VAMOS\04. 구현단계\v12\v12_results\*.json (이전 v12 산출물)
Step 2: v7 역방향 검증 — Phase 2 산출물 ↔ v12
        입력: phase2_v7/agent*_findings.json
Step 3: v10_cross.json + v7_reverse.json 저장

산출물: phase7_v12/v10_cross.json
        phase7_v12/v7_reverse.json
게이트: 교차+역방향 검증 완료 (PC7-5, PC7-6)
```

### 세션 48: §6 참조 + v11 미해결 + 발견 기록

```
사전조건: 세션 47 완료
실행모드: 순차

Step 1: §6 참조 57건 전수 해소 — /sot-search
        입력: phase6_v11/phase6_findings.json
Step 2: v11 미해결 5건 패턴 해소 — /sot-conflict
        입력: D:\VAMOS\04. 구현단계\v11_results\*.json (이전 v11 산출물)
Step 3: PART2 반영 완전성 확인
Step 4: 수치/참조 일관성 (LOCK + 산술) 확인
Step 5: 원본 보호 확인 (SHA256 백업 대조)
Step 6: phase7_findings.json 저장 (발견만, 수정 없음)
Step 7: phase7_checkpoint.json 저장 (PC7-1~PC7-12 판정)

산출물: phase7_v12/s6_references.json
        phase7_v12/v11_unresolved.json
        phase7_v12/phase7_findings.json
        phase7_v12/phase7_checkpoint.json
게이트: PC7-1~PC7-12 전항 PASS → Pass 2 진입 가능
```

---

## Pass 2: 통합 수정 + 전 Phase 재검증 (세션 49~51)

### 세션 49: 전체 발견사항 통합 정리

```
사전조건: Phase 7 CHECKPOINT PASS, Phase 1~7 발견사항 JSON 7개 파일 전수 접근 가능
실행모드: 순차

Step 1: Phase 1~7 발견사항 JSON 7개 파일 전수 수집
        phase1_v6/phase1_findings.json
        phase2_v7/phase2_findings.json
        phase3_v8/phase3_findings.json
        phase4_v9/phase4_findings.json
        phase5_v10/phase5_findings.json
        phase6_v11/phase6_findings.json
        phase7_v12/phase7_findings.json
Step 2: /cross-match — Phase 간 중복 발견사항 제거
Step 3: /completeness-map — 발견사항 × 오류 카테고리 매트릭스 생성
Step 4: 심각도 재분류: CRITICAL → 필수 수정, WARNING → 선택 수정
Step 5: merged_findings.json 저장
Step 6: completeness_matrix.json 저장
Step 7: severity_reclassification.json 저장
Step 8: dedup_report.json 저장

산출물: pass2/merged_findings.json
        pass2/completeness_matrix.json
        pass2/severity_reclassification.json
        pass2/dedup_report.json
게이트: 전체 발견사항 통합 완료 (PC-P2-1~PC-P2-4)
```

### 세션 50: Ripple Map + 통합 수정

```
사전조건: 세션 49 완료 + [CP-USER-2] 사용자 승인 완료 (D-3)
실행모드: 순차
※ 사용자 승인 절차 (D-3):
  세션 49 완료 후 merged_findings.json을 사용자에게 제시
  → 사용자 리뷰 → 승인 확인 후 세션 50 진행
  → 승인 없이 수정 진행 불가

Step 1: Ripple Map 생성 — 수정 파급 영향 분석
Step 2: /delta-apply — 전 발견사항 1회 통합 수정 (사용자 승인 후)
        입력: pass2/merged_findings.json + docs/sot/*
              + v8_results/ (v6+v8) + v9_results/ (v7+v9)
              + v10_results/ + v11_results/ + v12/v12_results/
Step 3: /integrity — 수정 전후 SHA-256 해시 비교 기록
Step 4: /deep-diff — 수정 범위 확인
Step 5: /json-diff — JSON 변경 추적
Step 6: BP-1~15 원본 보호 프로토콜 적용
        입력: phase6_v11/bp_preparation.json
Step 7: 백업 해시 대조 확인
Step 8: ripple_map.json 저장
Step 9: delta_apply_log.json 저장
Step 10: integrity_before_after.json 저장
Step 11: deep_diff_report.json 저장
Step 12: json_diff_report.json 저장
Step 13: backup_hash_verification.json 저장

산출물: pass2/ripple_map.json
        pass2/delta_apply_log.json
        pass2/integrity_before_after.json
        pass2/deep_diff_report.json
        pass2/json_diff_report.json
        pass2/backup_hash_verification.json
게이트: 통합 수정 완료 + 원본 보호 확인 (PC-P2-5~PC-P2-8)
```

### 세션 51: 전 Phase CHECKPOINT 재검증

```
사전조건: 세션 50 완료
실행모드: 순차

Step 1: Phase 0 — SOT 정합성 재검증 (EA+CM 핵심 항목 + 0-A~0-H 스크립트 재실행)
Step 2: Phase 1 — PC1-1~PC1-7 재확인
Step 3: Phase 2 — PC2-1~PC2-8 재확인
Step 4: Phase 3 — PC3-1~PC3-8 재확인
Step 5: Phase 4 — PC4-1~PC4-8 재확인
Step 6: Phase 5 — PC5-1~PC5-9 재확인
Step 7: Phase 6 — PC6-1~PC6-14 재확인
Step 8: Phase 7 — PC7-1~PC7-12 재확인
Step 9: /artifact-diff — 수정 전후 비교 보고서 생성
Step 10: /validate + /quality-gate — 수정된 산출물 재판정
Step 11: phase0_revalidation.json 저장
Step 12: phase1-7_recheckpoint.json 저장
Step 13: artifact_diff_report.json 저장
Step 14: final_validation.json 저장
Step 15: pass2_checkpoint.json 저장 (PC-P2-1~PC-P2-12 판정)

산출물: pass2/phase0_revalidation.json
        pass2/phase1-7_recheckpoint.json
        pass2/artifact_diff_report.json
        pass2/final_validation.json
        pass2/pass2_checkpoint.json
게이트: PC-P2-1~PC-P2-12 전항 PASS → Phase 8 진입 가능
        ※ 1개라도 FAIL 시 해당 Phase 재수정 후 세션 51 반복
```

---

## Phase 8: 최종 종합 판정 (세션 52~53)

### 세션 52: F1~F10 종합 판정

```
사전조건: Pass 2 CHECKPOINT PASS
실행모드: 순차

Step 1: □ Pass 2 CHECKPOINT 전수 PASS 확인
Step 2: /completeness-map — 33개 CAT × 도구 커버리지 최종 확인
Step 3: /final-review Mode B — FR-B01~B09 자동 체크
Step 4: /eval-audit — 평가 도구 자체 감사
Step 5: /validate-evaluator — 검증기 검증
Step 6: /write-judge-prompt — 판정 프롬프트 품질 확인
Step 6.5: /cross-model — GPT-4o 교차 검증 (Tier 3 사용 확정 — D-1)
          F1~F10 판정 결과를 GPT-4o에 전달, Claude 자기맹점 보완
Step 7: F1 판정 — Phase 0 SOT 불일치 CRITICAL 0건 확인
Step 8: F2 판정 — Phase 1 (v6) CHECKPOINT PASS 확인
Step 9: F3 판정 — Phase 2 (v7) CHECKPOINT PASS 확인
Step 10: F4 판정 — Phase 3 (v8) CHECKPOINT PASS 확인
Step 11: F5 판정 — Phase 4 (v9) CHECKPOINT PASS 확인
Step 12: F6 판정 — Phase 5 (v10) CHECKPOINT PASS 확인
Step 13: F7 판정 — Phase 6 (v11) CHECKPOINT PASS 확인
Step 14: F8 판정 — Phase 7 (v12) CHECKPOINT PASS 확인
Step 15: F9 판정 — v13 신규 발견 CRITICAL 0건 확인
Step 16: F10 판정 — 초보자가이드 33개 세션 정합성 (예비, 세션 53에서 상세)
Step 17: /report — 종합 보고서 생성
Step 18: f1_f10_verdict.json 저장
Step 19: final_report.json 저장

산출물: phase8/completeness_map.json
        phase8/final_review_mode_b.json
        phase8/eval_audit_report.json
        phase8/evaluator_validation.json
        phase8/judge_prompt_review.json
        phase8/cross_model_review.json   ← GPT-4o 교차 검증 결과 (D-1)
        phase8/f1_f10_verdict.json
        phase8/final_report.json
게이트: F1~F10 전항 PASS (PC8-1~PC8-16)
```

### 세션 53: 초보자가이드 33개 세션 재검토 + FINAL VERDICT

```
사전조건: 세션 52 완료 (F1~F10 판정)
실행모드: 순차

Step 1: Phase 0~7 SOT 수정 반영분 식별
        /sot-search — docs/guides/sections/session_*.md 33개 파일 grep
        ※ 실제 경로: D:\VAMOS\docs\guides\sections\session_01.md ~ session_33.md
Step 2: 영향 세션 식별 → guide_sot_sync.json 저장
Step 3: /cross-match — 수정 값 정합 확인
        → guide_cross_match.json 저장
Step 4: /hallucination-check — 오염 확인 (환각 0건)
        → guide_hallucination.json 저장
Step 5: /korean-nlp — 한국어 표현 일관성 확인
        → guide_korean_nlp.json 저장
Step 6: /quality-gate — 최종 판정
        → guide_quality_gate.json 저장
Step 7: phase8_checkpoint.json 저장 (PC8-1~PC8-21 최종 판정)
Step 8: FINAL_VERDICT.json 생성
        {
          "verdict": "PASS",
          "f1_f10": { "F1":"PASS", ..., "F10":"PASS" },
          "total_findings": { "critical":0, "warning":N, "info":N },
          "pass2_applied": true,
          "guide_33_sessions_synced": true,
          "checkpoint_summary": {
            "phase0":"PASS", "phase1":"PASS", ..., "phase7":"PASS",
            "pass2":"PASS", "phase8":"PASS"
          },
          "integrity_hash": "SHA-256",
          "pipeline_version": "v13-enhanced"
        }

산출물: phase8/guide_sot_sync.json
        phase8/guide_cross_match.json
        phase8/guide_hallucination.json
        phase8/guide_korean_nlp.json
        phase8/guide_quality_gate.json
        phase8/phase8_checkpoint.json
        phase8/FINAL_VERDICT.json
게이트: PC8-1~PC8-21 전항 PASS
        FINAL_VERDICT = "PASS" → v13 Enhanced Pipeline 완료
```

---

## 14.1 세션별 실행 요약표

```
┌──────┬──────────────────────────────────────────────────┬────────┬─────────────────────┐
│ 세션 │ 작업 내용                                         │ 모드   │ 게이트              │
├──────┼──────────────────────────────────────────────────┼────────┼─────────────────────┤
│  1   │ SOT 추출 Group 1 (EA-1~5)                        │ 5병렬  │ 5 EA SILVER+        │
│  2   │ SOT 추출 Group 2 (EA-6~10)                       │ 5병렬  │ 5 EA SILVER+        │
│  3   │ SOT 추출 Group 3 (EA-11~15)                      │ 5병렬  │ 15 EA 전수 완료      │
│  4   │ 크로스 매칭 Group A (CM-1~4)                      │ 4병렬  │ 4 CM 완료           │
│  5   │ 크로스 매칭 Group B (CM-5~8)                      │ 4병렬  │ 8 CM 전수 완료       │
│  6   │ 불일치 확정 + 심각도 분류                          │ 순차   │ 분류 완료           │
│  7   │ SOT 수정 + 적대적 재검증                          │ 순차   │ Phase 0 PASS        │
├──────┼──────────────────────────────────────────────────┼────────┼─────────────────────┤
│  8   │ v6 Phase 0 (8 스크립트)                           │ 순차   │ PC1-1               │
│  9   │ v6 Agent 1~3 순방향+역방향 (§6.1~6.10)              │ 3병렬  │ 3 Agent 완료         │
│ 10   │ v6 Agent 4~5 순방향+역방향 (§6.11~§5)             │ 2병렬  │ PC1-2, PC1-3        │
│ 11   │ v6 적대적 + 발견 기록                              │ 순차   │ PC1-1~7 PASS        │
├──────┼──────────────────────────────────────────────────┼────────┼─────────────────────┤
│ 12   │ v7 Phase 0 (8 스크립트)                           │ 순차   │ PC2-1               │
│ 13   │ v7 Agent 1~3 Core/Security/SDAR                  │ 3병렬  │ 3 Agent 완료         │
│ 14   │ v7 Agent 4~6 Teams/Schema/Memory                 │ 3병렬  │ 6 Agent 완료         │
│ 15   │ v7 Agent 7~10 UI/Infra/Decision/Domain           │ 4병렬  │ 10 Agent 완료        │
│ 16   │ v7 적대적 + 발견 기록                              │ 순차   │ PC2-1~8 PASS        │
├──────┼──────────────────────────────────────────────────┼────────┼─────────────────────┤
│ 17   │ v8 Phase 0 (14 스크립트)                          │ 순차   │ PC3-1               │
│ 18   │ v8 Agent 1~4 V0~V3                               │ 4병렬  │ 4 Agent 완료         │
│ 19   │ v8 Agent 5~8 §6 상세                              │ 4병렬  │ 8 Agent 완료         │
│ 20   │ v8 Agent 9~12 §6.11~§7 + 메타                    │ 4병렬  │ 12 Agent 완료        │
│ 21   │ v8 적대적 감사                                    │ 순차   │ PC3-7               │
│ 22   │ v8 발견 기록                                      │ 순차   │ PC3-1~8 PASS        │
├──────┼──────────────────────────────────────────────────┼────────┼─────────────────────┤
│ 23   │ v9 Phase -1 + GT 5개 재구축                       │ 순차   │ PC4-1, PC4-2        │
│ 24   │ v9 Phase 0 프롬프트 + 시범                        │ 순차   │ 6관점 준비 완료      │
│ 25   │ v9 Wave 1+2 (관점 A/B/C)                         │ 순차   │ Wave 1+2 완료        │
│ 26   │ v9 Wave 3 (관점 D/E/F)                           │ 순차   │ 6관점 전수 완료      │
│ 27   │ v9 RULE 1~14 + 발견 기록                         │ 순차   │ PC4-1~8 PASS        │
├──────┼──────────────────────────────────────────────────┼────────┼─────────────────────┤
│ 28   │ v10 Phase 0-A/B 정의 + 인덱스                    │ 순차   │ 0-A/B 완료          │
│ 29   │ v10 추출 Group 1 (C-1~5)                         │ 5병렬  │ Group 1 완료         │
│ 30   │ v10 추출 Group 2 (C-6~10)                        │ 5병렬  │ Group 2 완료         │
│ 31   │ v10 추출 Group 3 (C-11~15)                       │ 5병렬  │ 15 추출 완료         │
│ 32   │ v10 교차검증 + 대사 + 레지스트리                   │ 순차   │ PC5-1~3             │
│ 33   │ v10 6 매핑 에이전트                               │ 3×2병렬│ PC5-4~7             │
│ 34   │ v10 적대적 + 발견 기록                            │ 순차   │ PC5-1~9 PASS        │
├──────┼──────────────────────────────────────────────────┼────────┼─────────────────────┤
│ 35   │ v11 Phase 0 (7 인덱스 재구축)                     │ 순차   │ PC6-1               │
│ 36   │ v11 Wave 1 수치/참조                              │ 순차   │ PC6-2               │
│ 37   │ v11 Wave 2 구조/매핑                              │ 순차   │ PC6-3               │
│ 38   │ v11 Wave 3 프롬프트                               │ 순차   │ PC6-4               │
│ 39   │ v11 Wave 4 고급 검증                              │ 순차   │ PC6-5               │
│ 40   │ v11 Wave 5 사용성                                 │ 순차   │ PC6-6~9             │
│ 41   │ v11 적대적 + BP + 발견 기록                       │ 순차   │ PC6-1~14 PASS       │
├──────┼──────────────────────────────────────────────────┼────────┼─────────────────────┤
│ 42   │ v12 추출 Group 1 (5병렬)                          │ 5병렬  │ Group 1 완료         │
│ 43   │ v12 추출 Group 2 (5병렬)                          │ 5병렬  │ Group 2 완료         │
│ 44   │ v12 추출 Group 3 (5병렬)                          │ 5병렬  │ PC7-1               │
│ 45   │ v12 7 매핑 에이전트                               │ 순차   │ PC7-2, PC7-3        │
│ 46   │ v12 적대적 감사                                   │ 순차   │ PC7-4               │
│ 47   │ v10 교차 + v7 역방향                              │ 순차   │ PC7-5, PC7-6        │
│ 48   │ §6 참조 + v11 미해결 + 발견 기록                  │ 순차   │ PC7-1~12 PASS       │
├──────┼──────────────────────────────────────────────────┼────────┼─────────────────────┤
│ 49   │ 전체 발견사항 통합 정리                            │ 순차   │ PC-P2-1~4           │
│ 50   │ Ripple Map + 통합 수정                            │ 순차   │ PC-P2-5~8           │
│ 51   │ 전 Phase CHECKPOINT 재검증                        │ 순차   │ PC-P2-1~12 PASS     │
├──────┼──────────────────────────────────────────────────┼────────┼─────────────────────┤
│ 52   │ F1~F10 종합 판정 + 보고서                         │ 순차   │ F1~F10 PASS         │
│ 53   │ 초보자가이드 재검토 + FINAL VERDICT               │ 순차   │ PC8-1~21 PASS       │
│      │                                                  │        │ FINAL_VERDICT=PASS  │
└──────┴──────────────────────────────────────────────────┴────────┴─────────────────────┘
```
