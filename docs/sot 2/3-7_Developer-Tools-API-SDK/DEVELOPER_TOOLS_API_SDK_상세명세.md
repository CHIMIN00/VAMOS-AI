# 3-7. Developer Tools / API / SDK 상세명세

| 항목 | 내용 |
|------|------|
| **도메인 ID** | `TIER3-DOMAIN-07` |
| **SOT 근거** | STEP7-L (82 items) |
| **Part2 현황** | MENTION-ONLY — 백로그 원라이너 2건만 존재 |
| **최종 갱신** | 2026-03-22 |
| **상태** | DRAFT v1.0 |

> ⚠️ DEPRECATED — 위 테이블 "SOT 근거" 행의 "82 items" 표기는 P0-1 정정에 의해 실제 L-ID = 56건으로 확정. "82" 산출 근거 부재. CONFLICT_LOG CFL-001 참조

---

## 1. 개요 및 범위

VAMOS 프로젝트의 개발자 도구 생태계는 AI 기반 코딩 지원, 플러그인 확장, IDE 통합을 포괄한다.
본 명세는 STEP7-L의 82개 항목을 6개 서브도메인으로 구조화하여 기술한다.

> ⚠️ DEPRECATED — "82개 항목" 표기는 P0-1 정정에 의해 56 L-ID로 확정. CONFLICT_LOG CFL-001 참조

### 1.1 서브도메인 구성

| # | 서브도메인 | 항목 수 | 우선순위 |
|---|-----------|---------|---------|
| A | Dev Node 코딩 엔진 | 18 | P0 |
| B | 인라인 코드 자동완성 | 14 | P0 |
| C | 코드 리팩토링 자동화 | 12 | P1 |
| D | 자동 테스트 생성 | 15 | P1 |
| E | Plugin SDK | 13 | P1 |
| F | VS Code 확장 | 10 | P2 |

> ⚠️ DEPRECATED — F-VS Code 확장 "P2" 분류는 STEP7-L L-043~L-050 (DX 항목 8개) V1 배정과 불일치. STEP7-L V 배정이 정본. CONFLICT_LOG CFL-010 참조

### 1.2 기술 스택

```
┌─────────────────────────────────────────────┐
│  IDE Layer: VS Code Extension / Neovim LSP  │
├─────────────────────────────────────────────┤
│  Plugin SDK (TypeScript / Rust WASM)        │
├─────────────────────────────────────────────┤
│  Dev Node Engine (Rust core + Python glue)  │
├─────────────────────────────────────────────┤
│  LLM Backend: VAMOS Verifier + External API │
├─────────────────────────────────────────────┤
│  Storage: SQLite(local) / PostgreSQL(cloud) │
└─────────────────────────────────────────────┘
```

---

## 2. Dev Node 코딩 엔진 (서브도메인 A)

### 2.1 AI 코딩 어시스턴트 아키텍처

```
[User Input] → [Context Collector] → [Prompt Builder] → [LLM Router]
                     │                      │                  │
              [File Indexer]         [Template Engine]   [Model Selector]
              [Symbol Table]         [Few-shot Store]    [Fallback Chain]
                     │                      │                  │
                     └──────── [Response Post-processor] ──────┘
                                        │
                              [Code Validator] → [IDE Renderer]
```

### 2.2 코드 생성 파이프라인

```yaml
pipeline_stages:
  - stage: context_collection
    inputs: [active_file, open_tabs, git_diff, project_structure]
    max_tokens: 8192
    strategy: "sliding_window_with_priority"

  - stage: intent_classification
    model: "vamos-intent-classifier-v2"
    classes:
      - code_generation
      - code_explanation
      - bug_fix
      - refactoring
      - test_generation
      - documentation

  - stage: prompt_construction
    template_engine: "Jinja2"
    system_prompt_version: "v3.2"
    few_shot_selection: "embedding_similarity"
    max_examples: 3

  - stage: llm_inference
    primary_model: "vamos-coder-32b"  # ⚠️ DEPRECATED — "vamos-coder-32b"은 STEP7-L 미등장 모델명. CFL-002/CFL-008 참조
    fallback_models: ["qwen-2.5-coder-7b", "gpt-4o", "claude-sonnet"]  # LOCK-DT-04 chain: Qwen 2.5 Coder 7B (로컬) → gpt-4o → claude-sonnet (CFL-003 RESOLVED)
    timeout_ms: 15000
    streaming: true

  - stage: post_processing
    steps:
      - syntax_validation
      - import_resolution
      - style_formatting
      - security_scan
```

### 2.3 컨텍스트 관리 스키마

```typescript
interface CodingContext {
  session_id: string;                    // UUID v4
  workspace: {
    root_path: string;
    language: ProgrammingLanguage;
    framework: string | null;
    package_manager: "npm" | "pip" | "cargo" | "gradle";
  };
  active_file: {
    path: string;
    content: string;
    cursor_position: { line: number; col: number };
    selection: { start: Position; end: Position } | null;
    language_id: string;
  };
  project_graph: {
    symbols: SymbolNode[];               // 함수, 클래스, 변수 목록
    imports: ImportEdge[];               // 의존성 그래프
    call_graph: CallEdge[];              // 호출 관계
  };
  conversation_history: Message[];       // 최근 20턴
  user_preferences: UserCodingProfile;
}

interface SymbolNode {
  name: string;
  kind: "function" | "class" | "variable" | "type" | "module";
  file_path: string;
  range: { start: Position; end: Position };
  signature: string;
  doc_comment: string | null;
}
```

### 2.4 모델 라우팅 알고리즘

```python
def select_model(context: CodingContext, task: TaskType) -> ModelConfig:
    """복잡도 기반 모델 선택"""
    complexity = estimate_complexity(context, task)
    latency_budget = get_latency_budget(task)

    if complexity < 0.3 and latency_budget < 500:
        return ModelConfig("vamos-coder-7b", quantization="q4")  # ⚠️ DEPRECATED — "vamos-coder-7b"은 STEP7-L 미등장. STEP7-L L-002 정본: Qwen 2.5 Coder 7B. CFL-002 참조
    elif complexity < 0.7:
        return ModelConfig("vamos-coder-32b", quantization="fp16")  # ⚠️ DEPRECATED — CFL-002/CFL-008 참조
    else:
        return ModelConfig("vamos-coder-32b", quantization="fp16",  # ⚠️ DEPRECATED — CFL-002/CFL-008 참조
                          chain_of_thought=True,
                          verifier_enabled=True)
```

---

## 3. 인라인 코드 자동완성 (서브도메인 B)

### 3.1 Tab Completion 아키텍처

```
[Keystroke] → [Debounce 150ms] → [Prefix Extractor]
                                        │
                          ┌─────────────┼─────────────┐
                          ▼             ▼             ▼
                   [Local Cache]  [FIM Model]  [Snippet DB]
                          │             │             │
                          └──── [Ranking Engine] ─────┘
                                       │
                              [Ghost Text Renderer]
```

### 3.2 Fill-in-the-Middle (FIM) 프로토콜

```typescript
interface FIMRequest {
  prefix: string;         // 커서 앞 코드 (최대 4096 토큰)
  suffix: string;         // 커서 뒤 코드 (최대 2048 토큰)
  language: string;
  file_path: string;
  max_tokens: number;     // 기본값 128
  temperature: number;    // 기본값 0.0
  stop_sequences: string[];
}

interface FIMResponse {
  completion: string;
  confidence: number;     // 0.0 ~ 1.0
  tokens_used: number;
  latency_ms: number;
  alternatives: Array<{ text: string; score: number }>;
}
```

### 3.3 실시간 제안 성능 최적화

| 최적화 기법 | 설명 | 목표 지연 |
|------------|------|----------|
| Speculative decoding | Draft 모델로 후보 생성 후 검증 | < 100ms |
| Prefix caching | KV-cache 재활용으로 중복 계산 제거 | < 80ms |
| Trie-based filtering | 로컬 심볼 테이블 기반 사전 필터링 | < 10ms |
| Batched inference | 다중 커서/파일 요청 배치 처리 | < 200ms |
| ONNX Runtime | 경량 모델 로컬 추론 가속 | < 50ms |

### 3.4 제안 랭킹 알고리즘

```python
def rank_completions(candidates: list[Completion], ctx: Context) -> list[Completion]:
    for c in candidates:
        c.score = (
            0.35 * c.model_confidence +
            0.25 * compute_type_match_score(c, ctx) +
            0.20 * compute_recency_score(c, ctx.history) +
            0.10 * compute_length_penalty(c) +
            0.10 * compute_frequency_score(c, ctx.project_symbols)
        )
    return sorted(candidates, key=lambda c: c.score, reverse=True)
```

---

## 4. 코드 리팩토링 자동화 (서브도메인 C)

### 4.1 리팩토링 패턴 카탈로그

| 패턴 ID | 이름 | 카테고리 | 안전 등급 |
|---------|------|---------|----------|
| RF-001 | Extract Function | 구조 | SAFE |
| RF-002 | Inline Variable | 단순화 | SAFE |
| RF-003 | Rename Symbol | 명명 | SAFE |
| RF-004 | Move to Module | 구조 | REVIEW |
| RF-005 | Convert Loop to Functional | 현대화 | REVIEW |
| RF-006 | Extract Interface/Type | 추상화 | SAFE |
| RF-007 | Remove Dead Code | 정리 | WARN |
| RF-008 | Simplify Conditional | 단순화 | REVIEW |
| RF-009 | Replace Magic Number | 명명 | SAFE |
| RF-010 | Async/Await Migration | 현대화 | CRITICAL |

### 4.2 AST 분석 파이프라인

```
[Source Code] → [Tree-sitter Parser] → [Concrete Syntax Tree]
                                              │
                                    [AST Normalizer] → [Typed AST]
                                              │
                              ┌───────────────┼───────────────┐
                              ▼               ▼               ▼
                     [Pattern Matcher]  [Scope Analyzer]  [Type Inferrer]
                              │               │               │
                              └──── [Refactoring Planner] ────┘
                                              │
                                    [Code Transformer] → [Diff Generator]
                                              │
                                    [Test Runner] → [Validation]
```

### 4.3 안전한 변환 규칙 스키마

```typescript
interface RefactoringRule {
  id: string;
  pattern: ASTPattern;          // Tree-sitter 쿼리 패턴
  replacement: ASTTemplate;     // 변환 템플릿
  preconditions: Condition[];   // 적용 전 검증 조건
  postconditions: Condition[];  // 적용 후 검증 조건
  safety_level: "SAFE" | "REVIEW" | "WARN" | "CRITICAL";
  rollback_strategy: "git_stash" | "undo_stack" | "snapshot";
  test_requirements: {
    must_pass_existing: boolean;
    generate_new_tests: boolean;
    coverage_threshold: number;
  };
}

interface Condition {
  type: "no_side_effects" | "type_compatible" | "scope_contained"
      | "no_external_refs" | "test_pass";
  params: Record<string, unknown>;
}
```

---

## 5. 자동 테스트 생성 (서브도메인 D)

### 5.1 테스트 생성 파이프라인

```
[Target Function] → [Signature Analysis] → [Dependency Extraction]
                                                    │
                              ┌─────────────────────┼──────────────┐
                              ▼                     ▼              ▼
                      [Happy Path Gen]    [Edge Case Gen]   [Error Path Gen]
                              │                     │              │
                              └───── [Test Assembler] ─────────────┘
                                           │
                                   [Mock Generator] → [Test File Writer]
                                           │
                                   [Coverage Analyzer] → [Gap Reporter]
```

### 5.2 커버리지 분석 스키마

```typescript
interface CoverageReport {
  target: {
    file: string;
    function_name: string;
    line_range: [number, number];
  };
  metrics: {
    line_coverage: number;       // 0.0 ~ 1.0
    branch_coverage: number;
    path_coverage: number;
    mutation_score: number;      // 변이 테스트 점수
  };
  uncovered: {
    lines: number[];
    branches: BranchInfo[];
    edge_cases: EdgeCaseDescription[];
  };
  generated_tests: GeneratedTest[];
}

interface GeneratedTest {
  test_name: string;
  test_type: "unit" | "integration" | "property_based";
  code: string;
  covers_lines: number[];
  covers_branches: string[];
  confidence: number;
  dependencies: MockDependency[];
}
```

### 5.3 엣지 케이스 탐지 알고리즘

```python
def detect_edge_cases(func_ast: FunctionAST) -> list[EdgeCase]:
    """정적 분석 + LLM 하이브리드 엣지 케이스 탐지"""
    edges = []

    # 1) 정적 분석 기반
    for param in func_ast.parameters:
        if param.type in NUMERIC_TYPES:
            edges += [EdgeCase(param, v) for v in [0, -1, MAX_INT, MIN_INT, NaN]]
        elif param.type == "string":
            edges += [EdgeCase(param, v) for v in ["", " ", None, VERY_LONG_STRING]]
        elif param.type.startswith("list") or param.type.startswith("array"):
            edges += [EdgeCase(param, v) for v in [[], [None], LARGE_LIST]]

    # 2) 분기 분석 기반
    for branch in extract_branches(func_ast):
        edges.append(EdgeCase.from_boundary(branch.condition))

    # 3) LLM 기반 시맨틱 엣지 케이스
    llm_edges = llm_suggest_edge_cases(func_ast.source_code)
    edges.extend(llm_edges)

    return deduplicate(edges)
```

---

## 6. Plugin SDK (서브도메인 E)

### 6.1 확장 개발 SDK 아키텍처

```
┌──────────────────────────────────────────────┐
│            VAMOS Plugin Host Runtime          │
├──────────────────────────────────────────────┤
│  WASM Sandbox (LOCK-DT-05: WASM 격리 단일 정본 런타임)        │
│  (Node.js VM / Python Subprocess: 레거시 호환 한정 —          │
│   wasm_sandbox.md §7, CFL-005 RESOLVED 'WASM 격리 우선')      │
├──────────────────────────────────────────────┤
│              Plugin SDK API Layer             │
├──────────────────────────────────────────────┤
│  Core APIs:                                   │
│  - editor.*    (에디터 조작)                    │
│  - llm.*       (LLM 호출)                      │
│  - storage.*   (키-값 저장)                     │
│  - ui.*        (패널/다이얼로그)                 │
│  - vamos.*     (VAMOS 전용 기능)               │
└──────────────────────────────────────────────┘
```

> ⚠️ DEPRECATED — 위 다이어그램의 "Node.js VM", "Python Subprocess" 런타임은 LOCK-DT-05 ("WASM 격리, 선언된 권한만 허용")와 불일치. Node.js VM/Python Subprocess의 WASM 격리 수준 충족 여부 불명확. CONFLICT_LOG CFL-005 참조

### 6.2 API Surface 테이블

| 네임스페이스 | 메서드 | 설명 | 권한 |
|-------------|--------|------|------|
| `editor.getActiveFile()` | GET | 현재 활성 파일 정보 | `read:editor` |
| `editor.applyEdit(edit)` | POST | 코드 편집 적용 | `write:editor` |
| `llm.complete(prompt)` | POST | LLM 완성 요청 | `use:llm` |
| `llm.chat(messages)` | POST | LLM 대화 요청 | `use:llm` |
| `storage.get(key)` | GET | 플러그인 로컬 스토리지 읽기 | `read:storage` |
| `storage.set(key, value)` | PUT | 플러그인 로컬 스토리지 쓰기 | `write:storage` |
| `ui.showPanel(config)` | POST | 사이드 패널 표시 | `use:ui` |
| `ui.showNotification(msg)` | POST | 알림 표시 | `use:ui` |
| `vamos.getVerifierResult()` | GET | Verifier 분석 결과 조회 | `read:vamos` |
| `vamos.triggerPipeline(id)` | POST | VAMOS 파이프라인 실행 | `exec:vamos` |

### 6.3 플러그인 매니페스트 (VADD 모듈 카드 표준)

```json
{
  "$schema": "https://vamos.dev/schemas/plugin-manifest-v1.json",
  "id": "com.example.my-plugin",
  "name": "My VAMOS Plugin",
  "version": "1.0.0",
  "vamos_sdk_version": ">=2.0.0",
  "runtime": "wasm",
  "entry_point": "dist/plugin.wasm",
  "permissions": ["read:editor", "use:llm", "write:storage"],
  "activation_events": ["onLanguage:typescript", "onCommand:myPlugin.run"],
  "contributes": {
    "commands": [
      { "id": "myPlugin.run", "title": "Run My Plugin" }
    ],
    "menus": {
      "editor/context": [
        { "command": "myPlugin.run", "group": "vamos" }
      ]
    }
  },
  "vadd_card": {
    "category": "code-quality",
    "tags": ["linting", "ai-assisted"],
    "icon": "assets/icon.png",
    "screenshots": ["assets/screenshot1.png"],
    "pricing": "free"
  }
}
```

### 6.4 플러그인 등록/배포 파이프라인

```
[개발자] → [vamos plugin init] → [로컬 개발/테스트]
                                       │
                              [vamos plugin pack] → [.vpkg 패키지]
                                       │
                              [vamos plugin publish] → [VADD Registry]
                                       │
                              [자동 검증: 보안스캔/호환성테스트/성능벤치]
                                       │
                              [승인 → VADD Marketplace 게시]
```

---

## 7. VS Code 확장 (서브도메인 F)

### 7.1 확장 아키텍처

```
┌─────────────── VS Code Host ───────────────────┐
│  ┌─────────────────────────────────────────┐   │
│  │  VAMOS Extension (TypeScript)           │   │
│  │  ├── Extension Entry (activate/deactive)│   │
│  │  ├── InlineSuggestionProvider           │   │
│  │  ├── ChatParticipant (@vamos)           │   │
│  │  ├── CodeActionProvider                 │   │
│  │  ├── TreeDataProvider (Side Panel)      │   │
│  │  └── SettingsSyncProvider               │   │
│  └───────────────┬─────────────────────────┘   │
│                  │ LSP / stdio                   │
│  ┌───────────────▼─────────────────────────┐   │
│  │  VAMOS Language Server (Rust binary)     │   │
│  │  ├── Completion Provider                 │   │
│  │  ├── Diagnostics Engine                  │   │
│  │  ├── Code Actions                        │   │
│  │  └── Hover / Signature Help              │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

### 7.2 LSP 통합 프로토콜

```typescript
// VAMOS 전용 LSP 확장 메서드
interface VAMOSLSPExtensions {
  "vamos/inlineSuggest": {
    params: { textDocument: TextDocumentIdentifier; position: Position };
    result: InlineSuggestion[];
  };
  "vamos/explainCode": {
    params: { textDocument: TextDocumentIdentifier; range: Range };
    result: { explanation: string; confidence: number };
  };
  "vamos/refactor": {
    params: { textDocument: TextDocumentIdentifier; range: Range; kind: string };
    result: WorkspaceEdit;
  };
  "vamos/generateTest": {
    params: { textDocument: TextDocumentIdentifier; functionName: string };
    result: { testCode: string; testFile: string };
  };
}
```

### 7.3 설정 동기화 스키마

```json
{
  "vamos.model.primary": "vamos-coder-32b",  // ⚠️ DEPRECATED — STEP7-L 미등장 모델명. CFL-002/CFL-008 참조
  "vamos.model.fallback": "gpt-4o",  // ⚠️ DEPRECATED — LOCK-DT-04: 3단계 chain (Qwen 2.5 Coder 7B → gpt-4o → claude-sonnet). 단일 fallback 미반영. CFL-007 참조
  "vamos.completion.enabled": true,
  "vamos.completion.debounceMs": 150,
  "vamos.completion.maxTokens": 128,
  "vamos.completion.temperature": 0.0,
  "vamos.refactoring.autoSuggest": true,
  "vamos.refactoring.safetyLevel": "REVIEW",
  "vamos.testing.autoGenerate": false,
  "vamos.testing.coverageThreshold": 0.8,
  "vamos.sync.enabled": true,
  "vamos.sync.scope": "workspace"
}
```

---

## 8. 버전 로드맵

| 버전 | 시기 | 핵심 기능 | 기술 의존성 | 성공 지표 |
|------|------|----------|-----------|----------|
| v0.1 (MVP) | V1 Phase 1-2 | DevNode 코딩 엔진 기본, FIM 인라인 완성 | vamos-coder-7b, Tree-sitter | FIM 응답 < 200ms, HumanEval ≥ 70% |
| v0.2 (Enhancement) | V1 Phase 3-4 | 리팩토링 패턴 10종, 자동 테스트 생성 | AST 파이프라인, coverage.py | 리팩토링 안전 등급 GREEN ≥ 80%, 커버리지 + 15% |
| v0.3 (Plugin) | V2 Phase 1 | Plugin SDK + VADD 마켓플레이스 | WASM 런타임, Plugin Registry | 플러그인 3+ 개 검증 통과, SDK API 10개 안정 |
| v0.4 (Scale) | V2 Phase 2-3 | vamos-coder-32b 전환, 멀티모달 코드 분석 | GPU 인프라 (LOCK-DT-01) | HumanEval ≥ 85%, MBPP ≥ 75% |
| v1.0 (GA) | V3 Phase 3 | 전 기능 GA, LSP 확장 안정화, CI/CD 통합 | 전 의존성 GA | 외부 벤치마크 상위 10%, NPS ≥ 50 |

> ⚠️ DEPRECATED — 위 로드맵 테이블 관련 2건:
> 1. v0.1 행 "vamos-coder-7b" 및 v0.4 행 "vamos-coder-32b"는 STEP7-L 미등장 모델명. CFL-002/CFL-008 참조
> 2. v0.4 행 "(LOCK-DT-01)"은 잘못된 LOCK 참조. LOCK-DT-01 = API 버저닝 규칙이며 GPU 인프라와 무관. CFL-006 참조

### 8.1 버전 간 하위 호환성 정책
- **PATCH**: 하위 호환 100% — 버그 수정만
- **MINOR**: 하위 호환 유지 — 신규 API 추가, 기존 API deprecated 주석만 (삭제 금지)
- **MAJOR**: 마이그레이션 가이드 필수 — 최소 1 MINOR 버전 deprecated 경고 후 삭제
- **Plugin SDK**: SemVer 독립 — 플러그인 매니페스트에 `min_sdk_version` 명시

---

## 9. 의존성 매트릭스

### 9.1 외부 의존성
| 의존성 | 버전 | 용도 | 대체 전략 | 리스크 |
|--------|------|------|----------|--------|
| Tree-sitter | ≥ 0.22 | AST 파싱 (리팩토링, 코드 분석) | 없음 (핵심 의존성) | LOW — 활발한 오픈소스 |
| vamos-coder-7b | v0.1+ | FIM 인라인 완성, 코드 생성 | Claude/GPT 폴백 체인 (LOCK-DT-04) | HIGH — 자체 모델 미출시 |
| vamos-coder-32b | v0.2+ | 고급 코드 분석, 멀티파일 리팩토링 | vamos-coder-7b 폴백 | HIGH — 로드맵 의존 |

> ⚠️ DEPRECATED — "vamos-coder-7b", "vamos-coder-32b" 모델명은 STEP7-L에 미등장. STEP7-L L-002 정본: Qwen 2.5 Coder 7B, DeepSeek Coder V2, StarCoder 2, CodeLlama, Claude 4.6 Sonnet, GPT-4o, Gemini 2.5 Flash. CONFLICT_LOG CFL-008 참조
| coverage.py | ≥ 7.0 | Python 커버리지 측정 | pytest-cov 호환 | LOW |
| VS Code Extension API | ≥ 1.85 | LSP 통합, InlineSuggestion | — | LOW — 후방 호환 |
| WASM Runtime (Wasmtime) | ≥ 15.0 | 플러그인 샌드박스 | WasmEdge 대체 가능 | MEDIUM |

### 9.2 내부 의존성 (SOT 2 도메인 간)
| 소스 도메인 | 제공 인터페이스 | 사용 목적 |
|------------|--------------|----------|
| 1-1 Verifier | 검증 파이프라인 API | 코드 생성 결과 검증 |
| 1-2 Auxiliary | RAG 파이프라인 | 코드 컨텍스트 검색 |
| 4-1 Rust-Tauri | IPC 커맨드 (A-5~A-6) | Tool 실행 인터페이스 |
| 4-2 CI/CD | 워크플로우 트리거 | 자동 테스트 실행 |
| 4-3 MCP | 도구 등록 API | Plugin→MCP Tool 브릿지 |
| 5-1 Benchmark | VBS-13 코드 벤치마크 | HumanEval/MBPP 측정 |

### 9.3 의존성 건강 관리
- **CVE 스캔**: 주간 자동 (pip-audit, cargo-audit)
- **버전 고정**: pyproject.toml + Cargo.lock 의무화
- **EOL 모니터링**: 분기별 의존성 수명 확인
- **폴백 체인 테스트**: 월간 — 외부 모델 전환 E2E 검증

---

*본 문서는 STEP7-L SOT 82개 항목을 기반으로 작성되었으며, 구현 진행에 따라 갱신된다.*

> ⚠️ DEPRECATED — "82개 항목" 표기는 P0-1 정정에 의해 56 L-ID로 확정. CONFLICT_LOG CFL-001 참조
