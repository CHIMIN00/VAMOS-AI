# VAMOS 프로젝트 자산 인벤토리 (Asset Inventory)

> **작성일**: 2026-04-04 · **최종 갱신**: 2026-06-13 (Phase 4 완료 — §2.15 Phase 4 생성 자산 등재; §2.13 Phase 2·§2.14 Phase 3 직계)
> **목적**: D:\VAMOS 내 모든 폴더/파일의 역할, 사용 시점, 매트릭스 셀 매핑, 중복/미사용 식별
> **활용**: Phase 0-0에서 작성 → 매트릭스 갱신, CLAUDE.md 보강, Obsidian 생성의 입력 자료
> **갱신 규칙**: 파일/폴더 추가·삭제 시 본 문서도 갱신

---

## 목차

1. [전체 폴더 구조 맵](#1-전체-폴더-구조-맵)
2. [폴더별 상세 — 역할, 파일 목록, 사용 시점](#2-폴더별-상세)
3. [용도별 분류 — "이 작업할 때 이 파일을 써라"](#3-용도별-분류)
4. [매트릭스 셀별 사용 자산 매핑](#4-매트릭스-셀별-사용-자산-매핑)
5. [중복·미사용·정리 대상 식별](#5-중복미사용정리-대상-식별)
6. [자산 간 의존 관계](#6-자산-간-의존-관계)
7. [자산 인벤토리 유지보수 규칙](#7-자산-인벤토리-유지보수-규칙)

---

# 1. 전체 폴더 구조 맵

```
D:\VAMOS\
│
├── [설계 자산 — 원본]
│   ├── docs/sot/                    68개 파일   89,413줄   SOT 정본
│   ├── docs/sot 2/                  42폴더 2,654개 SOT 2 상세 (Phase4 확장 후 실측; 검증대상 1,979)
│   └── docs/guides/                 4+34개      37,904줄   구현가이드 PART1/PART2/초보자
│
├── [설계 자산 — 요약/접근]
│   ├── CLAUDE.md                    1개 697줄              AI 컨텍스트 (자동 로드)
│   ├── CLAUDE 보강전략 V1.0.md      1개 ~1,400줄           CLAUDE.md 보강 계획
│   └── VAMOS HOME/                  7+17폴더               Obsidian 지식 그래프
│
├── [엔지니어링 관리]
│   ├── VAMOS Engineering/           18개 파일               전략 12개 + 로드맵 프롬프트 + P0-2 산출물 3개 + PROGRESS + workspace
│   └── VAMOS_최종_로드맵.md         1개                     실행 순서
│
├── [AI 도구 — Claude Code]
│   ├── .claude/settings.json        1개                     Hook 설정 (6개 활성)
│   ├── .claude/CLAUDE.md            1개                     .claude 전용 컨텍스트
│   ├── .claude/commands/            3개                     슬래시 커맨드
│   ├── .claude/skills/              55폴더+3파일             검증/생성/분석 스킬
│   ├── .claude/hooks/               39개 스크립트            자동 검증 엔진
│   └── .claude/plugins/             2개 폴더                확장 기능
│
├── [작업 산출물]
│   ├── 04. 구현단계/                696개 파일               v8~v13 추출/검증 결과
│   ├── benchmark_results/           4개 파일                 벤치마크 실행 결과
│   └── benchmarks/golden_set/       14개 파일                골든 셋 테스트
│
├── [자동화 스크립트]
│   ├── scripts/                     4개 파일                 벤치마크/골든셋 생성
│   └── tests/                       3개 파일                 테스트 프레임워크
│
├── [설정 파일]
│   ├── .gitignore                   Git 무시 패턴
│   ├── .gitattributes               Git 속성
│   ├── .env.example                 환경변수 템플릿
│   ├── .pre-commit-config.yaml      pre-commit 설정
│   ├── promptfoo.yaml               Eval 설정 (전체)
│   ├── promptfoo-smoke.yaml         Eval 설정 (스모크)
│   └── *.code-workspace (3개)       VS Code 작업 공간
│
└── [Git/GitHub]
    ├── .git/                        Git 저장소
    └── .github/workflows/           CI 워크플로우 (1개)
```

---

# 2. 폴더별 상세

## 2.1 docs/sot/ — SOT 정본 (68개)

| 역할 | VAMOS의 "무엇을 만들지" 정의하는 원본 설계도 |
|------|-------------------------------------------|
| 파일 수 | 68개, 89,413줄 |
| 사용 시점 | D1(교차 검증), D2(변경 감시), D3(코드 대조), B2b(컨텍스트) |
| 매트릭스 셀 | D1, D2, D3, B2b |
| 수정 권한 | RULE 1.3 > PLAN 3.0 > DESIGN LOCK 우선순위에 따라 변경 |

**핵심 파일:**

| 파일 | 줄 수 | 역할 | 자주 참조하는 Phase |
|------|------|------|-------------------|
| VAMOS_MASTER_SPECIFICATION.md | 1,893 | 전체 통합 참조점 | D1, B2b |
| BASE-1.3_VAMOS_RULE_1.3_BASE.md | 633 | 절대 불변 규칙 | D1, X1 |
| PLAN-3.0_최종완성본.md | 6,948 | 로드맵/비용/버전 | D1, R1 |
| D2.0-01~08 (8개) | ~20,000 | 아키텍처 설계 | D1, R1, R2a |
| D2.1-D1~D8 (8개) | ~10,000 | Pydantic 스키마 | D1, R2a, B2c |
| PHASE_B1~B7 (7개) | ~9,618 | 구현 순서 지시 | B1, R2a, Phase 4 |
| STEP7 (5개) | ~9,019 | AI 기술 보강 상세 | R2b |
| READINESS_GUIDE.md | 1,256 | GO/NO-GO 62건 | Phase 4완료, Phase 6완료 |

## 2.2 docs/sot 2/ — SOT 2 상세 (2,654개 / 검증대상 1,979, _automation 제외 — Phase4 확장 후 실측)

| 역할 | SOT를 도메인별로 상세화한 확장 문서 |
|------|----------------------------------|
| 구조 | 42개 폴더 (36 도메인 + FILE CONTEXT + PHASE3/4_ORCHESTRATION + _automation/_cross-ref/_extractions), 2,654개 파일 |
| 사용 시점 | D1(교차 검증), B2b(컨텍스트 로딩), Obsidian 노트 원본 |
| 매트릭스 셀 | D1, D2, B2b |

**주요 폴더 (Tier별):**

| Tier | 폴더 | 도메인 수 |
|------|------|----------|
| T0 | 0-0_Governance-Rules-Meta | 1 |
| T1 | 1-1, 1-2 | 2 |
| T2 | 2-1, 2-2 | 2 |
| T3 | 3-2~3-10 | 9 |
| T4 | 4-1~4-4 | 4 |
| T5 | 5-1~5-4 | 4 |
| T6 | 6-1~6-13 | 13 |
| 특수 | Ai-investing-detail | 1 (254파일) |

## 2.3 docs/guides/ — 구현가이드

| 파일 | 줄 수 | 역할 | 사용 시점 |
|------|------|------|----------|
| VAMOS_구현가이드_PART1_진입전.md | ~1,300 | 진입전 체크리스트 82건 + 방법론 | Phase 0(참조), Phase 1(D1 BLOCKER) |
| VAMOS_구현가이드_PART2_구현단계.md | ~4,700 | 코드 생성 지시 + 린터/CI 설정 | B1(린터), R2a(코드), Phase 4 전체 |
| VAMOS_AI_전체해설_초보자가이드.md | ~600 | 시스템 개요 | 참조용 |
| VAMOS_초보자가이드_작업세션_운영가이드.md | ~1,400 | 세션 관리 | B2b(세션 운영) |
| sections/ (34개) | 각 ~300 | 세션별 작업 기록 | 참조용 (이력) |

## 2.4 CLAUDE.md — AI 컨텍스트

| 역할 | Claude Code 대화 시작 시 자동 로드되는 요약 브리핑 |
|------|------------------------------------------------|
| 위치 | D:\VAMOS\CLAUDE.md (루트) |
| 줄 수 | 697줄, 20개 섹션 (§1~§20) |
| 사용 시점 | 모든 AI 대화 시 자동 (매트릭스 전 셀) |
| 보강 계획 | 보강전략 V1.0 → ~953줄 (§21~§28 추가) |
| 매트릭스 셀 | B1(보강), B2b(활용) |

## 2.5 CLAUDE 보강전략 V1.0.md

| 역할 | CLAUDE.md를 ~953줄로 확장하는 상세 계획 |
|------|---------------------------------------|
| 줄 수 | ~1,400줄, 10개 섹션 |
| 사용 시점 | Phase 2 (B1: CLAUDE.md 보강 실행 시) |
| 매트릭스 셀 | B1 |
| 포함 내용 | 불일치 7건, 보강 대상, 검증 스킬 8개, 실행 순서 |

## 2.6 VAMOS HOME/ — Obsidian 지식 그래프

| 역할 | 사람이 탐색하는 지식 위키 (Obsidian Vault) |
|------|----------------------------------------|
| 현재 상태 | 00_HUB/ 7개 노트만 존재, 나머지 16개 폴더 비어있음 |
| 사용 시점 | Phase 2 (노트 생성), 이후 상시 참조 |
| 매트릭스 셀 | X1(문서화 전략), Phase 2(생성) |

**현재 존재하는 노트 (00_HUB/):**

| 노트 | 역할 |
|------|------|
| VAMOS-HOME.md | 시스템 진입점 |
| TIER-MAP.md | T0~T6 계층 시각화 |
| MODULE-MAP.md | 187개 모듈 인덱스 |
| DEPENDENCY-GRAPH.md | 112개 의존성 엣지 |
| LOCK-DECISION-REGISTRY.md | 469+ LOCK 항목 |
| 39-FILE-MASTER-INDEX.md | SOT 39개 파일 계층 |
| SOT2-STRUCTURE-MAP.md | SOT 2 42개 폴더 구조 |

**전략 문서:**

| 파일 | 역할 |
|------|------|
| OBSIDIAN-STRATEGY-v3.md | 120+ 노트 생성 계획, 템플릿, 태깅 규칙 |

## 2.7 VAMOS Engineering/ — 엔지니어링 관리 (18개)

| 파일 | 줄 수 | 역할 | 매트릭스 셀 |
|------|------|------|-----------|
| STRATEGY_01~07 (7개) | 각 ~5,000~8,000 | 25건 관점별 전략 (실패/범위/세션/도구/안전/통합/학습) | 전체 |
| STRATEGY_08_ENGINEERING_MATRIX.md | ~1,500 | 전체 작업 분류 (20개 셀) **v1.1** — 미연동 8건 해소, A13/A16/A21/A22/A25 반영, 참조 25개 | 전체 |
| STRATEGY_09_HARNESS_ENGINEERING.md | ~1,200 | AI 코드 생산 품질 보장 | D1, B1, B2a, B2b, B3 |
| STRATEGY_10_VERIFICATION_SYSTEM.md | ~600 | 검증 체계 (24건 갭 해소) | 전체 |
| STRATEGY_11_ASSET_INVENTORY.md | 본 문서 | 자산 인벤토리 | Phase 0-0 |
| ROADMAP_SESSION_EXECUTION_PROMPTS.md | — | 세션별 실행 프롬프트 | 전체 |
| PROGRESS.md | ~30 | Phase 진행 상태 추적 | X1(전체) |
| P0-2_CLAUDE_MD_STRUCTURE_SPEC.md | ~110 | CLAUDE.md §1~§28 구조 명세 | B2b |
| P0-2_OBSIDIAN_MATRIX_MAPPING.md | ~230 | Obsidian 17폴더 × 매트릭스 셀 매핑 | X1 |
| P0-2_DESIGN_ASSET_MAP.md | ~190 | 설계 자산 전체 맵 (4유형 × 매트릭스) | X1 |
| workspace.code-workspace | — | VS Code 작업 공간 | — |

## 2.8 .claude/ — Claude Code 도구

### .claude/settings.json — Hook 설정

| 역할 | PreToolUse/PostToolUse Hook 6개 활성화 |
|------|--------------------------------------|
| 사용 시점 | AI 작업 시 자동 (Write/Edit/Bash 이벤트) |
| 매트릭스 셀 | B2a (하네스 자동 실행) |

### .claude/commands/ — 슬래시 커맨드 (3개)

| 커맨드 | 역할 | 사용 시점 |
|--------|------|----------|
| /audit | 적대적 감사 (환각/오류/누락 탐지) | D1, B3 |
| /sot-check | SOT 원본 직접 대조 검증 | D1, Phase 3 |
| /validate | EA/CM JSON 구조+의미 검증 | D1 |

### .claude/skills/ — 검증/생성/분석 스킬 (55폴더+3파일)

**SOT 검증 그룹 (11개) — D1에서 사용:**

| 스킬 | 크기 | 역할 |
|------|------|------|
| /sot-conflict | 8.7KB | SOT 간 모순 탐지 (4유형) |
| /sot-check | 3.3KB | SOT 원본 직접 라인 대조 |
| /sot2-cross-ref | 6.0KB | SOT 2 교차 참조 검증 (4계층) |
| /validate | 6.0KB | 2계층 검증 (DV-1~9 + SV-1~3) |
| /integrity | 3.1KB | SHA-256 변경 감지 + 영향 분석 |
| /cross-match | 3.3KB | C1~C8 8가지 비교 패턴 |
| /cross-examine | 2.3KB | 멀티에이전트 심문 |
| /fact-audit | 2.7KB | 3역할 토론 (ACL 2025) |
| /hallucination-check | 4.1KB | 원자적 주장 4개 분해 |
| /completeness-map | 9.6KB | 오류유형×도구 커버리지 |
| /audit | 8.1KB | 적대적 감사 + SOT2 지원 |

**Eval/품질 그룹 (8개) — B3에서 사용:**

| 스킬 | 역할 |
|------|------|
| /final-review | 마스터 리뷰 워크플로우 (99KB) |
| /quality-gate | 다단계 품질 게이트 |
| /ragas-eval | RAGAS 4개 메트릭 |
| /eval-audit | 평가 감사 |
| /eval-ea | EA 평가 |
| /prompt-test | 프롬프트 테스트 |
| /golden-set | 골든 셋 구축 |
| /validate-evaluator | 평가기 검증 |

**SOT 2 생성 그룹 (3개) — SOT 2 작업 시 사용:**

| 스킬 | 역할 |
|------|------|
| /sot2-plan-gen | SOT 2 14-섹션 계획 생성 |
| /sot2-method-c | Method C 요약 통합 |
| /extract | Phase 0 추출 |

**AI/ML 도구 그룹 (15개) — Phase 4+ 코드 생산 시 사용:**

| 스킬 | 역할 |
|------|------|
| /confidence | 신뢰도 점수 |
| /consensus | 다모델 합의 |
| /cross-model | 크로스 모델 비교 |
| /debate | 구조적 토론 |
| /dspy-optimize | DSPy 최적화 |
| /symbolic-verify | 기호 실행 검증 |
| /giskard-scan | ML 공정성 스캔 |
| /guardrails-validate | 가드레일 검증 |
| /input-guard | 입력 검증/위생 |
| /llama-firewall | Llama 안전 검사 |
| /minicheck | MiniCheck NLI 검증 |
| /exa-verify | Exa 검증 |
| /hhem-verify | HF 임베딩 검증 |
| /patronus-check | Patronus API |
| /write-judge-prompt | 판사 프롬프트 생성 |

**유틸리티 그룹 (11개):**

| 스킬 | 역할 |
|------|------|
| /artifact-diff | SOT diff 분석 |
| /deep-diff | 시맨틱 diff |
| /delta-apply | 델타 적용 |
| /json-diff | JSON 시맨틱 diff |
| /json-repair | JSON 자동 수리 |
| /korean-nlp | 한국어 NLP |
| /sot-cache | SOT 캐싱/라인 매핑 |
| /sot-graph | SOT 의존성 그래프 |
| /sot-rag | SOT 기반 RAG |
| /sot-search | SOT 시맨틱 검색 |
| /docling | 문서 파싱/OCR |

**운영 그룹 (5개):**

| 스킬 | 역할 |
|------|------|
| /phase-run | Phase 실행 오케스트레이션 |
| /phoenix-observe | Phoenix 관측 |
| /report | 리포트 생성 |
| /lineage | 데이터 계보 추적 |
| /trace | 실행 트레이스 로깅 |

**기타 (2개):**

| 스킬 | 역할 |
|------|------|
| /deterministic | 결정론적 검증 엔진 참조 |
| /gpt-cache | GPT 캐시 최적화 |

**루트 파일 (2개):**

| 파일 | 크기 | 역할 |
|------|------|------|
| TOOL_GUIDE_46.md | 65.6KB | 46개 도구 마스터 가이드 |
| FINAL_CHECK_RESULT.md | 10.9KB | 최종 검증 결과 기록 |
| final_review_stamp_toolguide.json | — | 최종 리뷰 스탬프 |

### .claude/ 루트 파일

| 파일 | 역할 |
|------|------|
| CLAUDE.md | .claude 전용 컨텍스트 |
| FINAL_CHECK_PROMPT.md | 최종 검증 프롬프트 |
| settings.json | Hook 설정 (6개 활성화) |

### .claude/hooks/ — 자동 검증 스크립트 (39개)

**핵심 검증 엔진 (6개 — settings.json에서 활성화):**

| 파일 | 크기 | 역할 | 트리거 |
|------|------|------|--------|
| deterministic_validator.py | 25.9KB | EA JSON DV-1~9 검증 | EA 파일 Write 후 |
| cm_validator.py | 14.7KB | CM JSON CM-DV1~6 검증 | CM 파일 Write 후 |
| block_invalid_ea.sh | ~1KB | DV CRITICAL 시 Write 차단 | EA 파일 Write 전 |
| block_invalid_cm.sh | ~1KB | CM-DV CRITICAL 시 차단 | CM 파일 Write 전 |
| symbolic_verifier.py | 23.7KB | 기호 실행 검증 | 수동 호출 |
| sot_change_detector.sh | ~1KB | SOT 변경 감지 경고 | SOT 파일 Edit 시 |

**Eval/분석 도구 (12개):**

| 파일 | 역할 | Phase |
|------|------|-------|
| ragas_evaluator.py | RAGAS 4개 메트릭 | B3 |
| deepeval_metrics.py | Hallucination/Faithfulness | B3 |
| minicheck_verifier.py | NLI 검증 | B3 |
| giskard_scanner.py | 취약점 스캔 | B3 |
| evidently_eval.py | 데이터 드리프트 | R3 |
| confidence_calibrator.py | 신뢰도 보정 | B3 |
| hhem_scorer.py | 임베딩 점수 | B3 |
| patronus_checker.py | Patronus 검증 | B3 |
| guardrails_validator.py | 가드레일 | B3 |
| exa_verifier.py | Exa 검증 | B3 |
| dspy_extraction_module.py | DSPy 추출 | Phase 4 |
| cross_model_compare.py | 크로스 모델 | B3 |

**인프라/유틸 (11개):**

| 파일 | 역할 | Phase |
|------|------|-------|
| langfuse_logger.py | LLM 호출 추적 | R3 |
| phoenix_tracer.py | OTLP 트레이스 | R3 |
| lineage_tracker.py | 데이터 계보 | R3 |
| sot_graph_builder.py | SOT 그래프 구축 | D1 |
| sot_graph_query.py | SOT 그래프 질의 | D1 |
| sot_indexer.py | SOT 인덱싱 | D1 |
| sot_search.py | SOT 검색 | B2b |
| rag_context_injector.py | RAG 컨텍스트 주입 | B2b |
| korean_analyzer.py | 한국어 분석 | B2b |
| kr_sbert_embedder.py | 한국어 SBERT | B2b |
| input_scanner.py | 입력 스캔 | X2 |

**빌드/생성 (10개):**

| 파일 | 역할 |
|------|------|
| build_golden_set.py | 골든 셋 생성 |
| gptcache_manager.py | GPT 캐시 관리 |
| artifact_version_tracker.py | 산출물 버전 추적 |
| docling_parser.py | 문서 파싱 |
| json_auto_repair.py | JSON 자동 수리 |
| json_semantic_diff.py | JSON 시맨틱 diff |
| deep_diff_compare.py | 딥 diff 비교 |
| llama_firewall_scanner.py | Llama 안전 스캔 |
| promptfoo_assertions.js | promptfoo 커스텀 어서션 |
| promptfoo_config.yaml | promptfoo Hook 설정 |

## 2.9 04. 구현단계/ — 작업 산출물 (696개)

| 역할 | v8~v13 추출/검증/매핑 작업의 산출물 아카이브 |
|------|-------------------------------------------|
| 사용 시점 | 참조용 (과거 작업 이력), D1에서 일부 검증 결과 참조 |
| 매트릭스 셀 | 직접 사용 안 함 (아카이브) |

| 폴더 | 상태 | 내용 |
|------|------|------|
| v8_results/ | 아카이브 | 초기 추출 |
| v9_results/ | 아카이브 | 개선 추출 |
| v10_results/ | 아카이브 | Phase 0a~0f 세분화 |
| v11_results/ | 아카이브 | Phase 0~15 검증 |
| v12/ | 아카이브 | v12 구현 + 프롬프트 |
| v13/ | 아카이브 | v13 프롬프트 |
| v13_results/ | **현행** | Phase 0~8 최신 결과 |
| back up/ | 아카이브 | 백업 |

> **v13_results만 현행 자산. 나머지는 이력 참조용.**

## 2.10 루트 설정 파일

| 파일 | 역할 | 사용 시점 |
|------|------|----------|
| .gitignore | Git 무시 패턴 | 상시 |
| .gitattributes | Git 속성 | 상시 |
| .env.example | 환경변수 템플릿 | Phase 2 (B1) |
| .pre-commit-config.yaml | pre-commit Hook | Phase 2 (B1) |
| promptfoo.yaml | Eval 전체 설정 | Phase 5 (B3) |
| promptfoo-smoke.yaml | Eval 스모크 설정 | Phase 5 (B3) |
| *.code-workspace (3개) | VS Code 작업 공간 | 상시 |

## 2.11 scripts/ — 자동화 스크립트 (4개)

| 파일 | 역할 | Phase |
|------|------|-------|
| generate_golden_set.py | 골든 셋 생성 | B3 |
| generate_smoke_subset.py | 스모크 서브셋 생성 | B3 |
| promptfoo_to_benchmark_result.py | promptfoo→벤치마크 변환 | B3 |
| verify_golden_set.py | 골든 셋 검증 | B3 |

## 2.12 tests/ + benchmarks/ + benchmark_results/

| 폴더 | 파일 수 | 역할 | Phase |
|------|---------|------|-------|
| tests/ | 3개 (.py) | 테스트 프레임워크 스캐폴드 | Phase 4 (B2a) |
| benchmarks/golden_set/ | 14개 — **v2 실데이터 전환 (2026-06-11, D14)**: 162문항(MMLU 50/HumanEval 20/MBPP 50/LogicKor 42 전수), LOCK-BE-01/02 유효화 | 골든 벤치마크 테스트 | Phase 5 (B3) |
| benchmark_results/ | 4개 | MMLU, HumanEval 등 실행 결과 | Phase 5 (B3) |

## 2.13 Phase 2 생성 자산 (2026-06-11~12 등재 — 로드맵 2-8)

| # | 자산 | 위치 | Phase 2 작업 | 사용처 |
|---|------|------|------------|--------|
| 1 | PHASE2_환경리포트.md / PHASE2_RESUME_STATE.md | `_targets\` | 2-0A / 중단 저장 | 2-V 게이트·재개 |
| 2 | 골든셋 v2 (items/metadata 8 + manifest + contamination + smoke) | `benchmarks\golden_set\` | 2-0B (D14) | Phase 5 B3·LOCK-BE 게이트 |
| 3 | rebuild_golden_set_v2.py / verify_golden_set.py(v2) | `scripts\` | 2-0B | 골든셋 재현·검증 |
| 4 | CLAUDE.md 보강본 (946줄, §1~§28, GOLD) | 루트 | 2-1/2-2 | 전 Phase AI 컨텍스트 |
| 5 | claude-md-* 검증 스킬 8종 | `.claude\skills\` | 2-2 | CLAUDE.md 재검증(D1'·회귀) |
| 6 | claude-md-verification 리포트 (step1~8 + 회귀 json) | `04. 구현단계\claude-md-verification\` | 2-2 | 검증 이력 |
| 7 | backend/pyproject.toml + tests/{__init__,conftest}.py | `backend\` | 2-4 | Phase 4 코드 생산 |
| 8 | ci.yml (단일 통합: quality/test/vamos-lint) | `.github\workflows\` | 2-4 | Phase 4+ CI |
| 9 | vamos_lint.py (VL-001~005) / check_config_lock.py | `scripts\` | 2-5/2-4 | 하네스 게이트·Hook |
| 10 | commitlint.config.js | 루트 | 2-5 | 코드 커밋 린트 |
| 11 | settings.json Hook 2종 추가 (16→18) | `.claude\settings.json` | 2-4 | .py ruff 자동·config LOCK 검증 |
| 12 | PHASE2-DEC-01(pre-commit 불재도입)·DEC-02(5-4 SHELL 3-0 이연+유산 이동) | `VAMOS Engineering\decisions\` | 2-4/2-8 | A6 결정 기록 |
| 13 | CPS_TEMPLATE.md / CONTEXT_LOADING_MAP.md | `VAMOS Engineering\` | 2-6/2-7 | Phase 3~4 세션 골격·로딩 |
| 14 | Obsidian 노트 (목표 122 — _NOTE_FILELIST.md 정본) | `VAMOS HOME\` | 2-3 | 지식 그래프(A16 태깅) |
| 15 | D-2 보수 (04_cat-d-media/_index.md 1줄) | `docs\sot 2\2-2_...\` | 2-8 | D1 이연 종결 |
| 16 | 백업 세트 (golden_set_v1/CLAUDE.md.pre-2-1/STRATEGY_11.pre-2-8 등) | `_targets\_integ\backup_phase2\` | 전 작업 | 롤백 |

## 2.14 Phase 3 생성 자산 (2026-06-12 등재 — doc_strategy §2 갱신 규칙)

| # | 자산 | 위치 | Phase 3 작업 | 사용처 |
|---|------|------|------------|--------|
| 1 | PHASE3-GATE-01~08 (ADR 8건) | `VAMOS Engineering\decisions\` | P3-0 게이트 | 분모·귀속·이관 처분 정본 기록 |
| 2 | runtime_decisions.md (R1 10결정 요약+바인딩) | `VAMOS Engineering\` | P3-1 (3-1~3-7c) | Phase 4 R2a 입력 |
| 3 | PHASE3-DEC-001~010 (ADR 10건) | `VAMOS Engineering\decisions\` | P3-1 | R1 결정 전문(A6) |
| 4 | LOCK-DECISION-REGISTRY §8 (신규 LOCK 3: R1-A25/A21/A22) | `VAMOS HOME\00_HUB\` | P3-1 | Phase 4 config/코어 구현 바인딩 |
| 5 | security/test/release/doc_strategy.md (X1 4전략) | `VAMOS Engineering\` | P3-2 (3-8~3-11) | Phase 4~6 X2/X3 입력 |
| 6 | runtime_eng_plan.md / cross_eng_plan.md (계획서 2) | `VAMOS Engineering\` | P3-2 (3-12/3-13) | R2/X2 셀 실행 가이드 |
| 7 | phase3_retro.md (회고 + autocrlf 포스트모템) | `VAMOS Engineering\decisions\` | P3-2 Gate | A11 회고·P4-0 개선 입력 |
| 8 | PHASE3-DEC-011 (3-AI 교차감사 최종 확정) | `VAMOS Engineering\decisions\` | 교차감사 수합 | Phase 3 확정 정본·P4-0 권고 |
| 9 | sot CLAUDE.md 스냅샷 동기화 (946줄 GOLD, 2회: d540332·a8ce7d1) + integrity 체크 20260612T175049 | `docs\sot\`·`04. 구현단계\...\integrity\` | GATE-07b | SOT 코퍼스 정합·새 참조 기준 |
| 10 | git EOL 복구 체계 (repo autocrlf=false + fetch 동기화 규칙 + 분류기 선례) | `.git\config`·결정 기록 | P3-0 사고 대응 | 전 Phase git 운영 규칙 |

---

## 2.15 Phase 4 (V0 구현) 생성 자산 (2026-06-13 등재 — doc_strategy §2 갱신 규칙 · §2.13 Phase 2·§2.14 Phase 3 직계)

| # | 자산 | 위치 | Phase 4 작업 | 사용처 |
|---|------|------|------------|--------|
| 1 | backend/vamos_core/ ORANGE CORE (i1·i2·i5·i8·i9·i19·i20 + storage/memory_store + infra/{config_loader,logger} + safety/never_auto) | `backend\vamos_core\` | P4-1 (4-2/4-4/4-5) | V0 코어 파이프라인·Phase 5 D3 정합 분모 |
| 2 | orange_core/pipeline.py (LangGraph 5노드 직선) + schemas/{contracts.py 25모델, registries.py 123/36/23} | `backend\vamos_core\` | P4-0/4-1 | E2E 흐름·타입 계약 정본 |
| 3 | config/config.v1.toml (14섹션·LOCK 23키 frozen) + schema_registry.toml | `config\` | P4-1 (4-5) | 런타임 LOCK 적용·Phase 5 LOCK 대조 |
| 4 | rpc/server.py (JSON-RPC 13메서드+ping) + src-tauri/ (python_manager spawn·commands·serde generated.rs 25) | `backend\vamos_core\rpc\`·`src-tauri\` | P4-2 (4-1 serde·4-3 IPC) | IPC seam·5-7a 배포무결성 |
| 5 | shared/types/ (vamos.ts·json_schema·validate_roundtrip.mjs) + src/ (React UI: ConfidenceBadge/WhyButton/Disclaimer) + blue_nodes/{dev,research,content} 스캐폴딩 | `shared\`·`src\`·`backend\vamos_core\blue_nodes\` | P4-2 (4-1/4-3/4-6) | 3언어 타입동기·UI·V1 E-Series 슬롯 |
| 6 | scripts/ (roundtrip_test·generate_types·ipc_spawn_check·verify_artifacts·trace_matrix·check_lockfiles + p4_2/p4_3 매니페스트) | `scripts\` | P4-0~P4-3 | 하네스·산출물 게이트·재현 |
| 7 | PHASE4-DEC-001~010·012·013 (ADR — 012 결번 아님, P4-3 집행) + phase4_retro.md | `VAMOS Engineering\decisions\` | P4-0~P4-3 | 결정 전문(A6)·회고(A11) |
| 8 | SESSION_PROMPT_SKELETON.md (H1~H9 갭폐쇄 골격) + PHASE4-DEC-011(Opus↔Fable SOP) | `VAMOS Engineering\` | P4-2/P4-3 갭폐쇄 | Phase 5~8 프롬프트 필수 포함 골격 |

> ※ ADR 실존 목록 = PHASE4-DEC-001~010, 012, 013 (011 SOP 포함). **DEC-012는 P4-3 게이트가 집행**(CI mypy 소스전환+VL-004 테스트면제). 추가 신규 CI job(I-1 vitest/Playwright 등)은 별도 ADR(DEC-014+) 선행 — DEC-011 §D 불변.

## 2.16 Phase 5 (V0 검증 + GO/NO-GO) 생성 자산 (2026-06-13 등재 — doc_strategy §2 갱신 규칙 · §2.15 Phase 4 직계)

| # | 자산 | 위치 | Phase 5 작업 | 사용처 |
|---|------|------|------------|--------|
| 1 | [tool.poetry.group.eval] optional 그룹 (ragas 0.4.3·deepeval 4.0.6, A4 핀) + poetry.lock 갱신 | `backend\pyproject.toml`·`backend\poetry.lock` | 5-1 (DEC-007 집행) | V0/V1 Eval 실행 — dev/CI 격리(optional) |
| 2 | scripts/run_v0_eval.py (골든셋 162 러너 + QoD 5요소 + A17 멱등성 모드, seed=42·temp=0·per-prompt 워밍업) | `scripts\` | 5-1/5-2/A17 | Eval 재현·멱등성 게이트 |
| 3 | benchmark_results/eval_results.json (mmlu 56/he 45/mbpp 66/lk 95.2·QoD 0.8471·idempotency·seed·반복 기록) | `benchmark_results\` | 5-1/5-2 | V0 품질 기준선·V1 QoD 비교 |
| 4 | benchmark_results/alignment_report.json (D3 5-3~5-6 정합·DRIFT 0 실측) + v0_go_nogo_gate_report.json (5-8 게이트 판정·16건·5-V) | `benchmark_results\` | 5-3~5-6/5-8 | D3 정합 증거·게이트 판정서 |
| 5 | scripts/p5_1_manifest.json (P5-1 산출물 매니페스트) + trace_matrix.map.json 5-3~5-6 4행 추가(요구 15·매핑 21) | `scripts\` | H2/IV-3 | 산출물 실존·명세↔테스트 추적 |
| 6 | .vamosrules.json (BASE-1.3 §6.4 — non_goals/cost/self_evo/approval) | 리포 루트 | 5-8 item 12 | ORANGE CORE 초기화 BASE 규칙 자동로딩 템플릿 |
| 7 | PHASE5-DEC-001 (V0 GO/NO-GO 16건 스코프환원 6건) + phase5_retro.md | `VAMOS Engineering\decisions\` | 5-8/마감 | 릴리스 판정 근거(A6)·회고(A11) |
| 8 | git tag **v0-release** | git | 5-8 완료 | V0 릴리스 기준점 — Phase 6(V1) 회귀 비교 |

> ※ ADR 실존 목록 갱신 = PHASE4-DEC-001~010·012·013 + **PHASE5-DEC-001**(011 SOP 포함). 게이트 = wf_0229a151-bb3(9 에이전트, II-6 교차모델 미가용→인간 사인오프). Eval 골든셋 162 = §2.13 Phase 2 자산(v2, D14) 소비처.

---

# 3. 용도별 분류

## 3.1 "SOT 검증할 때" (D1 실행)

```
필요 파일:
  docs/sot/ (68개) ← 검증 대상
  docs/sot 2/ (2,654개; 검증대상 1,979) ← 검증 대상
  .claude/skills/sot-conflict/ ← /sot-conflict scan
  .claude/skills/sot-check/ ← /sot-check all
  .claude/skills/sot2-cross-ref/ ← /sot2-cross-ref all
  .claude/skills/validate/ ← /validate sot2-all
  .claude/skills/integrity/ ← /integrity snapshot
  .claude/hooks/deterministic_validator.py ← DV 엔진
  .claude/hooks/sot_graph_builder.py ← SOT 관계 분석
  docs/guides/PART1 Section E.2 ← BLOCKER 14건 참조
```

## 3.2 "CLAUDE.md 보강할 때" (Phase 2)

```
필요 파일:
  CLAUDE.md ← 보강 대상
  CLAUDE 보강전략 V1.0.md ← 보강 계획
  docs/sot/ + docs/sot 2/ ← 보강 내용 원본
  VAMOS HOME/00_HUB/ ← 구조 참조
  VAMOS Engineering/STRATEGY_08_ENGINEERING_MATRIX.md ← §28 추가
  .claude/skills/ 8개 검증 스킬 ← Phase B 검증
```

## 3.3 "Obsidian 노트 만들 때" (Phase 2)

```
필요 파일:
  VAMOS HOME/OBSIDIAN-STRATEGY-v3.md ← 전략 (템플릿, 태깅 규칙)
  VAMOS HOME/00_HUB/ ← 기존 7개 노트 (확장 기준)
  docs/sot 2/ ← 도메인 노트 내용 원본
  VAMOS HOME/00_HUB/LOCK-DECISION-REGISTRY.md ← LOCK 항목
  VAMOS HOME/00_HUB/DEPENDENCY-GRAPH.md ← 의존성
```

## 3.4 "V0 코드 짤 때" (Phase 4)

```
필요 파일:
  CLAUDE.md (보강된 버전) ← AI 컨텍스트
  docs/guides/PART2 ← 구현 지시
  docs/sot/D2.0-01~08 ← 아키텍처 참조
  docs/sot/D2.1-D1~D8 ← 스키마 정의
  docs/sot/PHASE_B1~B7 ← 구현 순서
  .claude/settings.json ← Hook 자동 실행
  .claude/hooks/deterministic_validator.py ← DV 검증
  B1에서 생성된: pyproject.toml, ruff, vamos_lint, CI yaml
  VAMOS Engineering/STRATEGY_09_HARNESS_ENGINEERING.md ← 하네스 규칙
```

## 3.5 "품질 평가할 때" (Phase 5)

```
필요 파일:
  .claude/hooks/ragas_evaluator.py ← RAGAS 메트릭
  .claude/hooks/deepeval_metrics.py ← Hallucination/Faithfulness
  .claude/hooks/minicheck_verifier.py ← NLI 검증
  .claude/skills/final-review/ ← 마스터 리뷰
  .claude/skills/quality-gate/ ← 품질 게이트
  scripts/generate_golden_set.py ← 골든 셋
  promptfoo.yaml ← Eval 설정
  benchmarks/golden_set/ ← 테스트 데이터
  benchmark_results/ ← 결과 비교
```

---

# 4. 매트릭스 셀별 사용 자산 매핑

| 셀 | 사용하는 파일/도구 |
|----|------------------|
| **D1** | docs/sot/, docs/sot 2/, /sot-conflict, /sot-check, /sot2-cross-ref, /validate, /integrity, PART1 E.2 |
| **D2** | /integrity (변경 감지), /sot-conflict (재검증), .claude/hooks/sot_change_detector.sh |
| **D3** | /sot-check (대조), /cross-match, 코드↔스키마 대조 스크립트 (Phase 5에서 생성) |
| **B1** | PART2 (린터 설정 근거), 보강전략 V1.0, CLAUDE.md, 하네스 계획서 §7~8 |
| **B2a** | .claude/settings.json, ruff, vamos_lint, pytest (B1에서 생성) |
| **B2b** | CLAUDE.md (보강된), docs/sot 2/ 해당 도메인, /sot-check method-c |
| **B2c** | D2.1 스키마, PHASE_B4 IPC, R1 결정 문서 |
| **B3** | ragas_evaluator.py, deepeval_metrics.py, promptfoo.yaml, /final-review, /quality-gate, benchmarks/ |
| **R1** | D2.0-01~08, PHASE_B1~B7, LOCK Registry, PLAN-3.0 |
| **R2a** | D2.0-02 (ORANGE CORE), D2.1 스키마, PHASE_B2 (구조), config LOCK |
| **R2b** | SOT 2 도메인 상세, D2.0-03 (BLUE NODE), STEP7 |
| **R2c** | D2.0-08 (UI/UX), B2c 타입 동기화 결과 |
| **R3** | langfuse_logger.py, phoenix_tracer.py, lineage_tracker.py, evidently_eval.py |
| **X1** | BASE-1.3 (보안), PART2 §3.5 (테스트), PLAN-3.0 (릴리스), Obsidian Strategy |
| **X2** | input_scanner.py, 보안 스캔 도구, commitlint, pytest |
| **X3** | R3 운영 데이터, 회귀 테스트 CI, 감사 리포트 |

---

# 5. 중복·미사용·정리 대상 식별

## 5.1 중복 의심

| 항목 | 위치 1 | 위치 2 | 판단 |
|------|--------|--------|------|
| CLAUDE.md | D:\VAMOS\CLAUDE.md | D:\VAMOS\.claude\CLAUDE.md | 역할 다름 (루트=프로젝트, .claude=도구 설정) → 중복 아님 |
| /audit 스킬 | .claude/skills/audit/ | .claude/commands/audit.md | 스킬=상세 정의, 커맨드=호출 인터페이스 → 중복 아님 |
| SOT 검증 | /sot-conflict vs /cross-match | 다른 검증 유형 | 보완 관계 → 중복 아님 |

## 5.2 미사용 가능성

| 항목 | 근거 | 조치 |
|------|------|------|
| 04. 구현단계/v8~v11 | v13이 최신, 이전 버전은 이력 | 아카이브 유지 (삭제 불필요) |
| 04. 구현단계/back up/ | 백업 폴더 | ✔ **이동 완료 (2026-06-12, PHASE2-DEC-02)** → `D:\VAMOS_ARCHIVE\legacy_phase2\04_구현단계_back_up\` (git 언트래킹 1파일, 디스크 보존) |
| .claude-pre-commit/ | 별도 디렉토리 존재 | ✔ **이동 완료 (2026-06-12, PHASE2-DEC-02)** → `D:\VAMOS_ARCHIVE\legacy_phase2\.claude-pre-commit\` (D17/D18 후속, 디스크 보존) |
| gpt-cache 스킬 | 현재 사용 안 함 | Phase 4+ 에서 필요 시 활용 |

## 5.3 정리 불필요 확인

| 항목 | 이유 |
|------|------|
| *.code-workspace 3개 | 각각 다른 작업 공간 (SOT2, CLAUDE보강, SOT2종합계획서) → 유지 |
| promptfoo 2개 yaml | 전체/스모크 분리 → 유지 |

---

# 6. 자산 간 의존 관계

```
SOT 68개 ────→ SOT 2 2,654개 ────→ CLAUDE.md (요약)
    │               │                  │
    │               │                  ↓
    │               └──────────→ Obsidian 120+ 노트
    │
    └──→ PART2 구현가이드 ──→ 하네스 계획서 ──→ 린터/CI (B1에서 생성)
              │
              └──→ V0/V1 코드 (Phase 4~6에서 생성)

매트릭스 ──→ 로드맵 ──→ 검증 체계
    ↑                       │
    └───────────────────────┘ (교차 참조)

스킬 55개 ──→ D1/B3에서 사용
Hook 39개 ──→ B2a에서 자동 실행
```

---

# 7. 자산 인벤토리 유지보수 규칙

```
규칙 1: 파일/폴더 추가 시
  → 본 문서 §2 해당 섹션에 추가
  → §4 매트릭스 셀 매핑에 추가

규칙 2: 파일/폴더 삭제 시
  → 본 문서에서 제거 + §5에 삭제 이유 기록

규칙 3: 역할 변경 시
  → 본 문서 해당 항목의 "역할" 필드 갱신

규칙 4: Phase 진행에 따른 갱신
  → Phase 2 완료 시: CLAUDE.md 보강 반영, Obsidian 노트 추가
  → Phase 4 완료 시: B1 생성물 (pyproject.toml 등) 추가
  → Phase 6 완료 시: V1 코드 구조 추가

규칙 5: 갱신 주기
  → Phase 경계마다 검토 (인수인계 프로토콜의 일부)
```

---

> **참조 문서**:
> - `D:\VAMOS\VAMOS Engineering\STRATEGY_08_ENGINEERING_MATRIX.md`
> - `D:\VAMOS\VAMOS_최종_로드맵.md`
> - `D:\VAMOS\VAMOS Engineering\STRATEGY_10_VERIFICATION_SYSTEM.md`
