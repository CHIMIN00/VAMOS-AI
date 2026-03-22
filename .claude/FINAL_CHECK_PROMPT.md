# VAMOS TOOL_GUIDE 49개 + 추가 3개 = 52개 스킬 최종 점검 프롬프트

## 배경

TOOL_GUIDE_46.md에 정의된 49개 AI 오류 방지 도구를 전부 구현 완료했습니다.
추가로 E-29 탐색 결과 3개 스킬(eval-audit, write-judge-prompt, validate-evaluator)을 만들었고,
기존 5개 스킬에 CAT 확장(CAT-27,28,31,32,33)을 추가했습니다.
이제 **빠짐없이 전부 만들어졌는지, 적용 가능한지** 5단계로 최종 점검해주세요.

---

## 핵심 파일 위치

- **TOOL_GUIDE**: `D:\VAMOS\.claude\skills\TOOL_GUIDE_46.md`
- **스킬 디렉토리**: `D:\VAMOS\.claude\skills\{스킬명}\SKILL.md`
- **훅 디렉토리**: `D:\VAMOS\.claude\hooks\{파일명}.py|.yaml|.js|.sh`
- **플러그인**: `D:\VAMOS\.claude\plugins\`
- **pre-commit**: `D:\VAMOS\.pre-commit-config.yaml`

---

## 기대 파일 전수 목록 (이 목록 대비 빠짐없이 확인)

### SKILL.md 파일 (52개)

**기존 스킬 (TOOL_GUIDE 이전부터 존재, 11개):**
| # | 스킬명 | 경로 |
|---|--------|------|
| 기존-1 | extract | skills/extract/SKILL.md |
| 기존-2 | validate | skills/validate/SKILL.md |
| 기존-3 | audit | skills/audit/SKILL.md |
| 기존-4 | sot-check | skills/sot-check/SKILL.md |
| 기존-5 | quality-gate | skills/quality-gate/SKILL.md (A-4 OrgForge 보강 포함) |
| 기존-6 | cross-match | skills/cross-match/SKILL.md |
| 기존-7 | delta-apply | skills/delta-apply/SKILL.md |
| 기존-8 | phase-run | skills/phase-run/SKILL.md |
| 기존-9 | report | skills/report/SKILL.md |
| 기존-10 | integrity | skills/integrity/SKILL.md |
| 기존-11 | sot-cache | skills/sot-cache/SKILL.md |

**A그룹 — Claude가 파일만 만들면 됨 (12개, 기존 스킬 보강 포함):**
| # | TOOL_GUIDE 번호 | 스킬명 | SKILL.md | hooks 파일 |
|---|----------------|--------|----------|-----------|
| 1 | A-1 | hallucination-check | skills/hallucination-check/SKILL.md | (없음, Claude 직접 실행) |
| 2 | A-2 | fact-audit | skills/fact-audit/SKILL.md | (없음, Agent tool 사용) |
| 3 | A-3 | cross-examine | skills/cross-examine/SKILL.md | (없음, Agent tool 사용) |
| 4 | A-4 | (OrgForge 보강) | validate, quality-gate SKILL.md 내 섹션 추가 | (없음) |
| 5 | A-5 | consensus | skills/consensus/SKILL.md | (없음) |
| 6 | A-6 | debate | skills/debate/SKILL.md | (없음) |
| 7 | A-7 | json-diff | skills/json-diff/SKILL.md | hooks/json_semantic_diff.py |
| 8 | A-8 | golden-set | skills/golden-set/SKILL.md | hooks/build_golden_set.py |
| 9 | A-9 | symbolic-verify | skills/symbolic-verify/SKILL.md | hooks/symbolic_verifier.py |
| 10 | A-47 | final-review | skills/final-review/SKILL.md | (없음) |
| 11 | A-48 | completeness-map | skills/completeness-map/SKILL.md | (없음) |
| 12 | A-49 | sot-conflict | skills/sot-conflict/SKILL.md | (없음) |

**B그룹 — pip/npm install 필요 (13개):**
| # | TOOL_GUIDE 번호 | 스킬명 | SKILL.md | hooks 파일 | pip 패키지 |
|---|----------------|--------|----------|-----------|-----------|
| 13 | B-10 | guardrails-validate | skills/guardrails-validate/SKILL.md | hooks/guardrails_validator.py | guardrails-ai |
| 14 | B-11 | eval-ea | skills/eval-ea/SKILL.md | hooks/deepeval_metrics.py | deepeval |
| 15 | B-12 | prompt-test | skills/prompt-test/SKILL.md | hooks/promptfoo_config.yaml, hooks/promptfoo_assertions.js | npm: promptfoo |
| 16 | B-13 | artifact-diff | skills/artifact-diff/SKILL.md | hooks/artifact_version_tracker.py | llm-diff |
| 17 | B-14 | input-guard | skills/input-guard/SKILL.md | hooks/input_scanner.py | llm-guard |
| 18 | B-15 | (symbolic-verify 강화) | (A-9에 통합) | hooks/symbolic_verifier.py 내 고급모드 | python-constraint |
| 19 | B-33 | json-repair | skills/json-repair/SKILL.md | hooks/json_auto_repair.py | json-repair |
| 20 | B-34 | deep-diff | skills/deep-diff/SKILL.md | hooks/deep_diff_compare.py | deepdiff |
| 21 | B-35 | ragas-eval | skills/ragas-eval/SKILL.md | hooks/ragas_evaluator.py | ragas |
| 22 | B-36 | korean-nlp | skills/korean-nlp/SKILL.md | hooks/korean_analyzer.py | kiwipiepy |
| 23 | B-37 | minicheck | skills/minicheck/SKILL.md | hooks/minicheck_verifier.py | minicheck |
| 24 | B-38 | docling | skills/docling/SKILL.md | hooks/docling_parser.py | docling |
| 25 | B-39 | dspy-optimize | skills/dspy-optimize/SKILL.md | hooks/dspy_extraction_module.py | dspy |

**C그룹 — API 키 필요 (5개):**
| # | TOOL_GUIDE 번호 | 스킬명 | SKILL.md | hooks 파일 | 필요 패키지 |
|---|----------------|--------|----------|-----------|-----------|
| 26 | C-16 | exa-verify | skills/exa-verify/SKILL.md | hooks/exa_verifier.py | exa-py |
| 27 | C-17 | cross-model | skills/cross-model/SKILL.md | hooks/cross_model_compare.py | openai |
| 28 | C-18 | confidence | skills/confidence/SKILL.md | hooks/confidence_calibrator.py | (없음) |
| 29 | C-40 | hhem-verify | skills/hhem-verify/SKILL.md | hooks/hhem_scorer.py | transformers, torch |
| 30 | C-41 | patronus-check | skills/patronus-check/SKILL.md | hooks/patronus_checker.py | patronus |

**D그룹 — 서버/인프라 필요 (10개):**
| # | TOOL_GUIDE 번호 | 스킬명 | SKILL.md | hooks 파일 |
|---|----------------|--------|----------|-----------|
| 31 | D-19 | trace | skills/trace/SKILL.md | hooks/langfuse_logger.py |
| 32 | D-20 | (Opik) | (별도 SKILL.md 없음, D-19 대안) | (없음) |
| 33 | D-21 | (Evidently) | (별도 SKILL.md 없음) | hooks/evidently_eval.py |
| 34 | D-22 | sot-search | skills/sot-search/SKILL.md | hooks/sot_indexer.py, hooks/sot_search.py |
| 35 | D-23 | (Agenta) | (별도 SKILL.md 없음) | (없음) |
| 36 | D-24 | sot-rag | skills/sot-rag/SKILL.md | hooks/rag_context_injector.py |
| 37 | D-25 | sot-graph | skills/sot-graph/SKILL.md | hooks/sot_graph_builder.py, hooks/sot_graph_query.py |
| 38 | D-26 | lineage | skills/lineage/SKILL.md | hooks/lineage_tracker.py |
| 39 | D-42 | phoenix-observe | skills/phoenix-observe/SKILL.md | hooks/phoenix_tracer.py |
| 40 | D-43 | giskard-scan | skills/giskard-scan/SKILL.md | hooks/giskard_scanner.py |

**E그룹 — 마켓플레이스 (9개):**
| # | TOOL_GUIDE 번호 | 스킬명 | 파일 |
|---|----------------|--------|------|
| 41 | E-27 | (skill-creator) | 플러그인 디렉토리에 설치됨 |
| 42 | E-28 | (claude-code-skills) | plugins/claude-code-skills/ |
| 43 | E-29 | (awesome-agent-skills) | 탐색 완료, 3개 스킬 직접 생성 |
| 44 | E-30 | (claude-code-plugins-plus-skills) | plugins/claude-code-plugins-plus-skills/ |
| 45 | E-31 | (claude-pre-commit) | D:\VAMOS\.pre-commit-config.yaml |
| 46 | E-32 | deterministic | skills/deterministic/SKILL.md |
| 47 | E-44 | llama-firewall | skills/llama-firewall/SKILL.md + hooks/llama_firewall_scanner.py |
| 48 | E-45 | (KR-SBERT) | hooks/kr_sbert_embedder.py |
| 49 | E-46 | gpt-cache | skills/gpt-cache/SKILL.md + hooks/gptcache_manager.py |

**E-29 추가 생성 스킬 (3개):**
| # | 스킬명 | SKILL.md |
|---|--------|----------|
| 50 | eval-audit | skills/eval-audit/SKILL.md |
| 51 | write-judge-prompt | skills/write-judge-prompt/SKILL.md |
| 52 | validate-evaluator | skills/validate-evaluator/SKILL.md |

### CAT 확장 (기존 스킬에 섹션 추가, 5개)

| CAT | 스킬 | 추가된 커맨드 | 확인 방법 |
|-----|------|-------------|----------|
| CAT-27 | sot-conflict | `/sot-conflict ontology` | SKILL.md에 "CAT-27 확장" 섹션 존재 확인 |
| CAT-28 | symbolic-verify | `/symbolic-verify bias-check` | SKILL.md에 "CAT-28 확장" 섹션 존재 확인 |
| CAT-31 | final-review | `/final-review business` | SKILL.md에 "CAT-31 확장" 섹션 존재 확인 |
| CAT-32 | input-guard | `/input-guard mask-pii` | SKILL.md에 "CAT-32 확장" 섹션 존재 확인 |
| CAT-33 | golden-set | `/golden-set reverify` | SKILL.md에 "CAT-33 확장" 섹션 존재 확인 |

### hooks 파일 전수 목록 (34개 .py + 2개 기타)

```
.py 파일 (34개):
cm_validator.py, deterministic_validator.py, build_golden_set.py,
json_semantic_diff.py, guardrails_validator.py, deepeval_metrics.py,
artifact_version_tracker.py, input_scanner.py, json_auto_repair.py,
deep_diff_compare.py, ragas_evaluator.py, korean_analyzer.py,
minicheck_verifier.py, docling_parser.py, dspy_extraction_module.py,
symbolic_verifier.py, exa_verifier.py, cross_model_compare.py,
patronus_checker.py, confidence_calibrator.py, hhem_scorer.py,
langfuse_logger.py, evidently_eval.py, sot_indexer.py,
sot_search.py, rag_context_injector.py, lineage_tracker.py,
sot_graph_query.py, sot_graph_builder.py, phoenix_tracer.py,
giskard_scanner.py, kr_sbert_embedder.py, gptcache_manager.py,
llama_firewall_scanner.py

기타 (2개):
promptfoo_config.yaml, promptfoo_assertions.js

쉘 스크립트 (3개, 기존):
block_invalid_ea.sh, block_invalid_cm.sh, sot_change_detector.sh
```

---

## 5단계 점검 절차

### 1단계: 파일 존재 확인

**목표**: 위 전수 목록의 모든 파일이 실제 존재하는지 확인

**방법**:
1. `D:\VAMOS\.claude\skills\` 하위 모든 SKILL.md 파일 Glob
2. `D:\VAMOS\.claude\hooks\` 하위 모든 파일 Glob
3. 위 전수 목록과 1:1 대조
4. 누락 파일 리스트 출력

**판정**:
- 누락 0개 → PASS
- 누락 1개 이상 → FAIL (누락 목록 + 원인 분석)

**출력 형식**:
```
1단계 결과:
  SKILL.md: 52/52 존재 (또는 N개 누락: [목록])
  hooks: 34/34 .py 존재 (또는 N개 누락: [목록])
  기타: promptfoo_config.yaml ✅, promptfoo_assertions.js ✅, .pre-commit-config.yaml ✅
  플러그인: claude-code-skills/ ✅, claude-code-plugins-plus-skills/ ✅
  판정: PASS 또는 FAIL
```

---

### 2단계: SKILL.md 품질 검증

**목표**: 모든 SKILL.md가 필수 구성요소를 갖추고 있는지 확인

**방법**: 52개 SKILL.md 전부 읽고 아래 체크리스트 확인 (Agent 서브에이전트 병렬 사용 권장)

**필수 구성요소 체크리스트**:
1. YAML frontmatter 존재 (name, description 필드)
2. $ARGUMENTS 처리 섹션 존재
3. 실행 절차 섹션 존재
4. 출력 형식(JSON 스키마 또는 예시) 존재
5. 판정 기준 존재 (PASS/FAIL 또는 유사 판정)
6. 저장 위치 명시
7. hooks .py 경로 참조가 있으면 실제 파일과 일치하는지 확인

**CAT 확장 추가 확인**:
- sot-conflict SKILL.md에 "CAT-27" 또는 "ontology" 섹션 존재
- symbolic-verify SKILL.md에 "CAT-28" 또는 "bias-check" 섹션 존재
- final-review SKILL.md에 "CAT-31" 또는 "business" 또는 "BIZ" 섹션 존재
- input-guard SKILL.md에 "CAT-32" 또는 "mask-pii" 섹션 존재
- golden-set SKILL.md에 "CAT-33" 또는 "reverify" 섹션 존재

**A-4 OrgForge 보강 확인**:
- validate SKILL.md에 "OrgForge" 관련 내용 존재
- quality-gate SKILL.md에 "OrgForge" 관련 내용 존재

**판정 (스킬당)**:
- 7개 항목 전부 충족 → OK
- 5~6개 충족 → WARNING (부족한 항목 명시)
- 4개 이하 → FAIL

**출력 형식**:
```
2단계 결과:
  OK: N개
  WARNING: N개 [스킬명: 부족항목]
  FAIL: N개 [스킬명: 부족항목]
  CAT 확장: 5/5 반영 (또는 N개 미반영: [목록])
  OrgForge 보강: 2/2 반영 (또는 N개 미반영)
  판정: PASS 또는 FAIL
```

---

### 3단계: Python 훅 import + 실행 테스트

**목표**: hooks .py 파일들이 실제 실행 가능한지 확인

**방법**:

**3-A. import 테스트 (전수)**:
```python
# 34개 .py 파일 각각에 대해:
python -c "import ast; ast.parse(open('파일경로').read()); print('OK')"
```
- AST 파싱 성공 = 구문 오류 없음

**3-B. 의존성 import 테스트 (설치된 패키지만)**:
```python
# 각 .py 파일의 import 문 추출 → 해당 패키지 import 시도
# 예: deepeval_metrics.py → python -c "import deepeval"
# 미설치 패키지는 SKIP (FAIL이 아님)
```

**3-C. 기본 실행 테스트 (가능한 것만)**:
- `llama_firewall_scanner.py`: LlamaFirewall import + PromptGuard 스캔 테스트
- `kr_sbert_embedder.py`: KR-SBERT 모델 로드 + 임베딩 테스트
- `gptcache_manager.py`: 기본 stats 출력 테스트
- `symbolic_verifier.py`: 샘플 JSON으로 제약 검증 테스트
- `json_auto_repair.py`: 깨진 JSON 복구 테스트
- `korean_analyzer.py`: 한국어 형태소 분석 테스트

**3-D. 버전 충돌 확인**:
```bash
pip check 2>&1 | head -20
```

**판정**:
- 3-A 전수 통과 + 3-B 설치된 것 전부 통과 → PASS
- 3-A 실패 있음 → FAIL (구문 오류)
- 3-B 설치됐는데 import 실패 → FAIL (의존성 깨짐)
- 3-D 충돌 있음 → WARNING (영향도 분석 필요)

**출력 형식**:
```
3단계 결과:
  3-A 구문검증: 34/34 OK (또는 N개 실패: [목록])
  3-B 의존성: N개 테스트, M개 OK, K개 SKIP(미설치), L개 FAIL
  3-C 실행: N개 테스트, M개 OK, L개 FAIL
  3-D 버전충돌: 없음 또는 [충돌 목록]
  판정: PASS 또는 FAIL
```

---

### 4단계: /final-review toolset (Mode B) 실행

**목표**: 33개 실패 카테고리 전부 커버 + 검증 계층 완전성 확인

**방법**: D:\VAMOS\.claude\skills\final-review\SKILL.md의 Mode B 절차를 따름

**확인 항목**:
```
[FR-B01] 33개 실패 카테고리 커버리지 100%
  - 33개 카테고리 목록은 아래 참조
  - 각 카테고리에 최소 1개 도구 존재 확인

[FR-B02] 검증 계층 완전성
  - Layer A (결정론적): validate DV, symbolic-verify 등
  - Layer B (AI 의미적): validate SV, audit 등
  - Layer C (교차 모델): cross-model, debate 등
  - Layer D (사람 확인): final-review 등

[FR-B03] 중복 제거: 90%+ 기능 중복 도구 쌍 없음
[FR-B04] 무료 도구만으로 주요 검증 가능
[FR-B05] 설치 경로 명확
[FR-B06] VAMOS 적합성
[FR-B07] 수확 체감 확인
[FR-B08] 잔여 오류율
[FR-B09] 경험적 검증
```

**33개 실패 카테고리 (전부 커버되어야 함)**:
```
CAT-01: 환각 (hallucination)
CAT-02: 누락 (omission)
CAT-03: JSON 구조 오류
CAT-04: 타입/값 불일치
CAT-05: 교차 참조 불일치
CAT-06: 프롬프트 품질
CAT-07: 입력 보안
CAT-08: 신뢰도 보정
CAT-09: 한국어 처리
CAT-10: 관측/로깅
CAT-11: 문서 구조 파싱
CAT-12: 버전 비교/회귀
CAT-13: 데이터 계보
CAT-14: 캐싱/비용
CAT-15: SOT 원본 품질
CAT-16: 인코딩/문자 변환 오류
CAT-17: 컨텍스트 윈도우 초과
CAT-18: 중복 추출 항목
CAT-19: 카테고리 분류 오류
CAT-20: 수치 단위/범위 오류
CAT-21: source_line 위치 오류
CAT-22: LOCK/FREEZE 값 불일치
CAT-23: 후반부 추출 누락
CAT-24: 프롬프트 드리프트
CAT-25: JSON 자동 복구 필요
CAT-26: AI 모델 편향
CAT-27: 용어/개념 표준화 (← sot-conflict ontology)
CAT-28: 검증 도구 다양성/편향 (← symbolic-verify bias-check)
CAT-29: 추출 파이프라인 취약점
CAT-30: 메타 평가 (평가의 평가) (← eval-audit, write-judge-prompt, validate-evaluator)
CAT-31: 비즈니스 요구사항 적합성 (← final-review business)
CAT-32: PII/민감정보 노출 (← input-guard mask-pii)
CAT-33: 정답 데이터 레거시 오류 (← golden-set reverify)
```

**판정**:
- FR-B01~B09 전부 PASS → COMPLETE
- 하나라도 FAIL → INCOMPLETE

---

### 5단계: TOOL_GUIDE ↔ 실제 파일 교차 대조

**목표**: TOOL_GUIDE_46.md 문서 내용과 실제 파일이 일치하는지 확인

**방법**:
1. TOOL_GUIDE에서 "Claude가 만들 파일" 섹션의 모든 파일 경로 추출
2. 실제 파일 존재 여부 + 파일명 일치 확인
3. TOOL_GUIDE의 "실행 방법" 섹션의 커맨드가 SKILL.md의 $ARGUMENTS와 일치하는지 확인
4. 비용 요약 테이블의 합계가 맞는지 확인
5. "검증 영역 커버리지" 테이블의 도구명이 실제 존재하는 스킬과 일치하는지 확인
6. 49개 번호 체계 (A-1~A-49, B-10~B-39, C-16~C-41, D-19~D-43, E-27~E-46) 빠짐 확인

**판정**:
- 불일치 0개 → PASS
- 불일치 1개 이상 → FAIL (불일치 목록)

---

## 최종 종합 판정

```
1단계 PASS + 2단계 PASS + 3단계 PASS + 4단계 COMPLETE + 5단계 PASS
→ TOOL_GUIDE 최종 점검 PASS ✅

하나라도 FAIL이면:
→ 실패 항목 목록 + 수정 방안 제시
→ 수정 후 해당 단계만 재검증
```

## 중간 저장 (컨텍스트 보호)

각 단계 완료 시 결과를 아래 파일에 저장:
```
D:\VAMOS\.claude\skills\FINAL_CHECK_RESULT.md
```
- 1단계 완료 시 → 1단계 결과 저장
- 2단계 완료 시 → 2단계 결과 추가
- ...
- 5단계 완료 시 → 종합 판정 추가

컨텍스트가 부족해지면, 이 파일을 읽어서 이전 단계 결과를 복원하세요.

## 실패 시 조치

| 단계 | 실패 유형 | 조치 |
|------|----------|------|
| 1단계 | 파일 누락 | 누락 파일 생성 |
| 2단계 | SKILL.md 불완전 | 부족한 섹션 추가 |
| 3단계 | 구문 오류 | .py 파일 수정 |
| 3단계 | 의존성 깨짐 | pip install 안내 |
| 4단계 | CAT 미커버 | 해당 CAT 커버 스킬 추가/확장 |
| 5단계 | GUIDE↔파일 불일치 | TOOL_GUIDE 또는 파일명 수정 |

---

## 실행 지시

위 5단계를 순서대로 전부 실행해주세요.
- 2단계는 서브에이전트(Agent tool) 병렬 처리로 컨텍스트를 보호하세요.
- 각 단계 완료 시 FINAL_CHECK_RESULT.md에 중간 결과를 저장하세요.
- 5단계까지 완료 후 종합 판정을 출력하세요.
- FAIL 항목이 있으면 수정까지 진행하고, 수정 후 해당 단계만 재검증하세요.
