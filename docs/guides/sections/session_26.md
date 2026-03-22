---
session: 26
sections: [33, 34]
status: complete
---

# §33. 프로젝트 구조 — Monorepo (모노레포)

## §33.1 전체 디렉토리 구조

### 비유: 회사 건물의 층별 배치도

> 하나의 회사 건물에 1층은 고객 응대(프론트엔드), 2층은 시스템 관리실(Rust 백엔드), 3층은 연구소(Python AI), 그리고 공용 회의실(공유 타입)과 관리실(설정)이 있는 것처럼 — VAMOS도 하나의 저장소(Monorepo) 안에 모든 것이 층별로 정리되어 있습니다.

### 정의

**Monorepo (모노레포)**란 하나의 Git 저장소에 프론트엔드, 백엔드, 설정 등 **모든 코드를 함께 관리**하는 방식입니다. VAMOS는 Monorepo를 **LOCK (변경 불가)**로 확정했습니다. [근거: PHASE_B2 §1.1]

### 왜 Monorepo인가?

| 항목 | Monorepo (채택) | Polyrepo (미채택) |
|------|----------------|------------------|
| Tauri 호환성 | src-tauri/와 프론트를 같은 루트에 요구 | 별도 repo 관리 시 빌드 복잡도 증가 |
| 스키마 공유 | Rust/Python/React 간 타입 공유 용이 | 타입 동기화에 별도 패키지 필요 |
| CI/CD | 단일 파이프라인으로 통합 테스트 | 멀티 repo 오케스트레이션 필요 |
| V1 적합성 | 로컬 MVP에 최적 (단일 개발자/소팀) | 오버엔지니어링 |

[근거: PHASE_B2 §1.1]

### 전체 디렉토리 트리

```
vamos/                              # Git 루트 (Monorepo — LOCK)
├── .github/                        # GitHub Actions CI/CD
│   └── workflows/
│       ├── ci.yml                  # 통합 CI (lint, test, build)
│       └── release.yml             # 릴리즈 빌드 (Tauri bundle)
├── .vscode/                        # VSCode 공유 설정
│   ├── settings.json               # 포매터/린터 설정
│   └── extensions.json             # 권장 확장
│
├── src/                            # [1층] React 프론트엔드 (§33.2)
├── src-tauri/                      # [2층] Rust Tauri 백엔드 (§33.3)
├── backend/                        # [3층] Python AI/ML 백엔드 (§33.4)
├── shared/                         # [공용] 공유 타입/인터페이스 (§33.5)
├── tests/                          # [검사실] 통합 테스트
├── config/                         # [관리실] 설정/환경 파일 (§33.6)
├── docs/                           # 프로젝트 문서
│   └── schemas/                    # D1~D8 스키마 참조 문서
├── scripts/                        # 빌드/배포 스크립트
│   ├── setup.sh                    # 개발 환경 초기화
│   ├── dev.sh                      # 개발 서버 통합 실행
│   └── build.sh                    # 프로덕션 빌드
│
├── .env.example                    # 환경 변수 템플릿
├── .gitignore                      # Git 무시 규칙
├── package.json                    # 프론트엔드 의존성
├── tsconfig.json                   # TypeScript 설정
├── vite.config.ts                  # Vite 번들러 설정
├── tailwind.config.ts              # TailwindCSS 설정
├── postcss.config.js               # PostCSS 설정
└── README.md                       # 프로젝트 개요
```

### 각 주요 디렉토리의 역할

| 디렉토리 | 비유 | 역할 | 사용 기술 |
|----------|------|------|----------|
| `src/` | 1층 고객 응대 | 사용자가 보는 화면(UI) | React 18 + TypeScript |
| `src-tauri/` | 2층 시스템 관리실 | 시스템 제어 + Python 연결 | Rust + Tauri 2.0 |
| `backend/` | 3층 AI 연구소 | AI 추론, 워크플로우 실행 | Python 3.11+ |
| `shared/` | 공용 회의실 | 3개 언어 공통 타입 정의 | JSON Schema |
| `config/` | 관리실 | 환경별 설정 파일 | TOML |
| `tests/` | 검사실 | 통합/E2E 테스트 | pytest + vitest |

[근거: PHASE_B2 §2]

**핵심 요약 (3줄)**
1. VAMOS는 Monorepo(LOCK)로, 하나의 Git 저장소에 프론트엔드/Rust/Python/설정이 모두 포함됩니다.
2. Tauri 2.0의 구조 특성상 src-tauri/와 프론트엔드가 같은 루트에 있어야 하므로 Monorepo가 필수입니다.
3. 6개 주요 디렉토리(src/, src-tauri/, backend/, shared/, config/, tests/)로 계층이 분리됩니다.

---

## §33.2 Frontend (src/) — React 18 + TypeScript

### 비유: 백화점의 매장별 구역

> 백화점에 들어가면 1층 화장품, 2층 의류, 3층 가전처럼 구역이 나뉘어 있죠. src/ 폴더도 마찬가지로, components(부품 매장), pages(전체 매장), hooks(편의시설), stores(창고) 등으로 깔끔하게 나뉘어 있습니다.

### src/ 주요 하위 폴더

```
src/
├── main.tsx                        # React 시작점 (앱 진입)
├── App.tsx                         # 루트 컴포넌트 + 라우터
│
├── components/                     # 재사용 UI 부품 (10개 카테고리)
│   ├── common/                     # 범용 부품 (Button, Modal, Input 등)
│   ├── layout/                     # 레이아웃 (Header, Sidebar, Footer)
│   ├── canvas/                     # 워크플로우 시각화 [D8 §4]
│   ├── artifacts/                  # 산출물 뷰어 [D8 §6]
│   ├── notifications/              # 알림 센터 [D8 §7]
│   ├── autonomy/                   # 자율수준 제어 UI [D8 §10]
│   ├── decision/                   # Decision 결과 표시
│   ├── memory/                     # 메모리 탐색기
│   ├── cost/                       # 비용 대시보드
│   └── log/                        # 로그 뷰어
│
├── pages/                          # 페이지 (라우트 단위)
│   ├── DashboardPage.tsx           # 메인 대시보드
│   ├── ChatPage.tsx                # 대화 인터페이스
│   ├── WorkflowPage.tsx            # 워크플로우 빌더/뷰어
│   ├── MemoryPage.tsx              # 메모리 관리
│   ├── SettingsPage.tsx            # 설정 (RBAC/자율수준/비용)
│   ├── LogPage.tsx                 # 로그/감사
│   └── NodeDetailPage.tsx          # BLUE NODE 상세
│
├── hooks/                          # 커스텀 React 훅 (재사용 로직)
│   ├── useTauriIPC.ts              # Tauri IPC 통신
│   ├── useDecision.ts              # Decision 상태 관리
│   ├── useWorkflow.ts              # 워크플로우 상태
│   ├── useMemory.ts                # 메모리 조회/저장
│   ├── useCost.ts                  # 비용 조회
│   ├── useNotification.ts          # 알림 구독
│   ├── useAutonomy.ts              # 자율수준 제어
│   └── useLog.ts                   # 로그 스트림 구독
│
├── stores/                         # 상태 관리 (Zustand 또는 Jotai)
│   ├── appStore.ts                 # 앱 전역 상태
│   ├── decisionStore.ts            # Decision 상태
│   ├── workflowStore.ts            # 워크플로우 상태
│   ├── memoryStore.ts              # 메모리 상태
│   ├── costStore.ts                # 비용/예산 상태
│   ├── notificationStore.ts        # 알림 상태
│   └── authStore.ts                # RBAC 인증 상태
│
├── types/                          # TypeScript 타입 정의
├── utils/                          # 유틸리티 함수
├── styles/                         # 글로벌 스타일 (TailwindCSS)
└── assets/                         # 정적 자산 (이미지, 아이콘)
```

### UI 컴포넌트 카테고리 (D8 문서 매핑)

| 카테고리 | 디렉토리 | D8 근거 | 비유 |
|----------|----------|---------|------|
| Canvas | `components/canvas/` | D8 §4 | 워크플로우를 지도처럼 보여주는 화면 |
| Artifacts | `components/artifacts/` | D8 §6 | AI가 만든 결과물을 보는 진열장 |
| 알림 | `components/notifications/` | D8 §7 | 스마트폰 알림센터처럼 이벤트를 알려주는 곳 |
| 자율수준 UI | `components/autonomy/` | D8 §10 | AI의 자율성을 조절하는 슬라이더 |
| Decision | `components/decision/` | D2 | 판단 결과를 카드형으로 보여주는 곳 |
| Memory | `components/memory/` | D6 | 기억 저장소를 탐색하는 파일 탐색기 |
| Cost | `components/cost/` | D7 | 비용 사용량을 보여주는 계기판 |
| Log | `components/log/` | D2 | 시스템 활동 기록을 보여주는 일지장 |

[근거: PHASE_B2 §3.1, §3.2]

**핵심 요약 (3줄)**
1. src/ 폴더는 components(UI 부품), pages(페이지), hooks(재사용 로직), stores(상태 관리) 4개 핵심 하위 폴더로 구성됩니다.
2. 10개 UI 컴포넌트 카테고리가 각각 D8 문서의 UI/UX 계약에 매핑되어 있습니다.
3. 모든 Tauri IPC 통신은 useTauriIPC 훅을 통해 표준화되어 처리됩니다.

---

## §33.3 Rust Backend (src-tauri/) — Tauri 2.0

### 비유: 건물의 관리실 + 통역사

> src-tauri/는 건물의 관리실입니다. 고객(React UI)이 요청하면 관리실(Rust)이 접수하고, 필요한 경우 3층 연구소(Python)에 통역(IPC)해서 전달합니다. 관리실은 건물의 전기, 수도, 보안(시스템 리소스)도 관리합니다.

### src-tauri/ 구조

```
src-tauri/
├── Cargo.toml                      # Rust 의존성 관리
├── Cargo.lock                      # 의존성 잠금
├── build.rs                        # Tauri 빌드 스크립트
├── tauri.conf.json                 # Tauri 설정 (윈도우, 번들, 권한)
├── capabilities/                   # Tauri 2.0 권한 정의
│   └── default.json                # 기본 권한 매니페스트
├── icons/                          # 앱 아이콘 (빌드용)
│
└── src/
    ├── main.rs                     # Tauri 시작점
    ├── lib.rs                      # 라이브러리 루트
    │
    ├── commands/                   # IPC 커맨드 모듈 (React와 대화)
    │   ├── mod.rs                  # 커맨드 모듈 루트
    │   ├── decision.rs             # Decision 관련 IPC
    │   ├── workflow.rs             # 워크플로우 실행/조회
    │   ├── memory.rs               # 메모리 CRUD
    │   ├── cost.rs                 # 비용 조회
    │   ├── settings.rs             # 설정 변경
    │   ├── log.rs                  # 로그 조회/스트림
    │   └── system.rs               # 시스템 상태/건강 체크
    │
    ├── bridge/                     # Python 프로세스 관리 (통역사 역할)
    │   ├── mod.rs
    │   ├── python_manager.rs       # Python subprocess 생명주기 관리
    │   ├── ipc_protocol.rs         # JSON-RPC stdin/stdout 프로토콜
    │   └── health_check.rs         # Python 프로세스 건강 체크
    │
    ├── state/                      # 앱 상태 관리
    ├── models/                     # Rust 데이터 모델 (serde)
    ├── utils/                      # 유틸리티
    └── tests/                      # Rust 단위 테스트
```

### IPC Command 모듈 (commands/)

| 모듈 파일 | 주요 커맨드 | 비유 |
|----------|------------|------|
| `decision.rs` | submit_request, get_decision | 판단 접수/결과 전달 창구 |
| `workflow.rs` | run_workflow, get_workflow_status | 작업 진행/상태 확인 창구 |
| `memory.rs` | search_memory, save_memory, delete_memory | 기억 저장/검색 창구 |
| `cost.rs` | get_cost_summary, get_budget_status | 비용 확인 창구 |
| `settings.rs` | get_settings, update_settings | 설정 변경 창구 |
| `log.rs` | get_logs, stream_logs | 활동 기록 열람 창구 |
| `system.rs` | health_check, get_system_info | 시스템 점검 창구 |

[근거: PHASE_B2 §4.1, §4.2]

### Python Subprocess 관리 (bridge/)

```
[React UI] --IPC--> [Rust/Tauri] --subprocess(stdin/stdout)--> [Python AI/ML]
```

| 컴포넌트 | 파일 | 비유 |
|----------|------|------|
| PythonManager | `python_manager.rs` | 연구소(Python) 열고/닫기 관리자 |
| IPCProtocol | `ipc_protocol.rs` | 통역사 (한국어↔영어처럼 Rust↔Python 번역) |
| HealthCheck | `health_check.rs` | 연구소가 정상 운영 중인지 점검하는 순찰원 |

[근거: PHASE_B2 §4.3]

**핵심 요약 (3줄)**
1. src-tauri/는 Rust로 작성된 시스템 관리 계층으로, React UI와 Python AI 사이의 중간 다리 역할을 합니다.
2. commands/ 폴더에 7개 모듈이 React의 IPC 요청을 처리하고, bridge/ 폴더가 Python subprocess를 관리합니다.
3. PythonManager가 Python 프로세스의 시작/종료/재시작을, IPCProtocol이 JSON-RPC 통신을 담당합니다.

---

## §33.4 Python Backend (backend/) — vamos_core

### 비유: AI 연구소의 부서별 조직도

> backend/는 VAMOS의 AI 연구소입니다. 연구소 안에는 사령부(ORANGE CORE), 전문가 팀(BLUE NODES), 장비실(인프라), 작업라인(에이전트 파이프라인), 기억 저장소(스토리지), 안전관리팀(세이프티) 등 부서가 있습니다.

### backend/ 구조

```
backend/
├── pyproject.toml                  # Python 프로젝트 설정/의존성
├── poetry.lock                     # 의존성 잠금
│
├── vamos_core/                     # 메인 패키지 (AI 연구소)
│   ├── __init__.py                 # 패키지 초기화
│   ├── main.py                     # IPC 서버 시작점 (Rust에서 호출)
│   ├── config.py                   # 설정 로드
│   │
│   ├── orange_core/                # 사령부 — 판단/제어 (I-1~I-5)
│   ├── blue_nodes/                 # 전문가 팀 — 도메인별 실행
│   ├── infra/                      # 장비실 — LLM 호출, 도구 관리
│   ├── agent/                      # 작업라인 — 워크플로우 파이프라인
│   ├── storage/                    # 기억 저장소 — 메모리, 벡터, 그래프
│   ├── safety/                     # 안전관리팀 — 정책, 비용, 승인
│   ├── schemas/                    # 설계도 — Pydantic v2 스키마
│   └── mcp/                        # 외부 연결 — MCP Bridge
│
└── tests/                          # Python 테스트
    ├── conftest.py                 # 공통 fixture
    ├── unit/                       # 단위 테스트
    ├── integration/                # 통합 테스트
    └── e2e/                        # E2E 테스트
```

### 각 하위 모듈 설명

| 모듈 | 디렉토리 | 비유 | 핵심 역할 | 관련 스키마 |
|------|----------|------|----------|------------|
| ORANGE CORE | `orange_core/` | 사령부 | 의도 파악(I-1) → 근거 수집(I-2) → 메모리 계획(I-3) → 출력 구조화(I-4) → 게이트 평가(I-5) | D2 |
| BLUE NODES | `blue_nodes/` | 전문가 팀 | Dev(코딩), Research(연구), Content(글쓰기), Quant(분석), Trading(매매 V2+) | D3 |
| Infra | `infra/` | 장비실 | BrainAdapter(LLM 호출), ToolRegistry(도구 관리), PromptCache, RateLimit | D4 |
| Agent | `agent/` | 작업라인 | LangGraph StateGraph, 5단계 Pipeline(Intake→Plan→Execute→Verify→Deliver) | D5 |
| Storage | `storage/` | 기억 저장소 | Memory(L0~L3), Vector(Chroma/Qdrant), GraphRAG, SemanticCache | D6 |
| Safety | `safety/` | 안전관리팀 | PolicyCheck, Approval, CostBudget, Guardrails, RBAC, Autonomy | D7 |
| Schemas | `schemas/` | 설계도 보관소 | Pydantic v2 모델 중앙 정의 (contracts.py) | D2~D7 |
| MCP | `mcp/` | 외부 연결 창구 | MCP Bridge Layer, Tool Discovery, Streamable HTTP | D3 |

[근거: PHASE_B2 §5.1~§5.9]

### ORANGE CORE 내부 구조 (orange_core/)

```
orange_core/
├── decision_kernel.py              # Decision Kernel — I-1~I-5 종합 판단
├── front_mini.py                   # Front Mini — 빠른 의도 분류 (경량 LLM)
├── i1_intent/                      # I-1: 의도 해석 (Intent Detector)
├── i2_evidence/                    # I-2: 근거 수집 (Evidence Collector)
├── i3_memory/                      # I-3: 메모리 계획 (Memory Planner)
├── i4_output/                      # I-4: 출력 구조화 (Output Structurer)
└── i5_gate/                        # I-5: 게이트 평가 + 라우팅 (Condition & Decision Engine)
```

[근거: PHASE_B2 §5.2]

### BLUE NODES 종류 및 버전별 활성화

| Blue Node | 도메인 | 역할 | V1 | V2 | V3 |
|-----------|--------|------|----|----|-----|
| Dev Node | 개발 | 코드 생성/리뷰/실행 | ✅ | ✅ | ✅ |
| Research Node | 연구 | 웹 검색/요약 | ✅ | ✅ | ✅ |
| Content Node | 콘텐츠 | 문서 작성/포맷 변환 | ✅ | ✅ | ✅ |
| Quant Node | 분석 | 데이터 수집/통계 | ✅ | ✅ | ✅ |
| Trading Node | 매매 | 시그널/주문 실행 | ❌ | ✅ | ✅ |

[근거: PHASE_B2 §5.3]

**핵심 요약 (3줄)**
1. backend/는 Python AI/ML 백엔드로, 8개 핵심 모듈(orange_core, blue_nodes, infra, agent, storage, safety, schemas, mcp)로 구성됩니다.
2. ORANGE CORE가 사령부로서 I-1~I-5 단계를 거쳐 판단하고, BLUE NODES가 실제 도메인 작업을 실행합니다.
3. 모든 Pydantic v2 스키마는 schemas/contracts.py에 중앙 정의되어 타입 일관성을 보장합니다.

---

## §33.5 Shared Types (shared/) — 공유 타입 정의

### 비유: 3개 국어 사전

> 한국인(React/TypeScript), 독일인(Rust), 프랑스인(Python)이 함께 일할 때, 공통 사전이 있으면 소통이 쉽죠. shared/ 폴더는 3개 언어가 동일한 데이터 구조를 사용하도록 보장하는 **공용 사전**입니다.

### shared/ 구조

```
shared/
├── types/                          # 공유 타입 정의 (Golden Source)
│   ├── schemas.json                # JSON Schema 정의 (D2~D7 기반)
│   └── enums.json                  # 공유 Enum 정의 (event_type, failure_code 등)
│
└── codegen/                        # 타입 코드 생성 스크립트
    ├── generate_ts.py              # JSON Schema → TypeScript 타입 생성
    ├── generate_rs.py              # JSON Schema → Rust serde 구조체 생성
    └── generate_py.py              # JSON Schema → Pydantic v2 모델 생성
```

### 타입 동기화 전략

```
[Python contracts.py]  ←── 정본(SOT, 진짜 원본)
         │
         ↓ (자동 추출)
[shared/types/schemas.json]  ←── Golden Source (중간 형식)
         │
         ├──→ generate_ts.py  → src/types/*.ts       (React용)
         ├──→ generate_rs.py  → src-tauri/models/*.rs (Rust용)
         └──→ generate_py.py  → 검증용 (원본과 대조)
```

> **중요**: Python의 `schemas/contracts.py`가 **진짜 원본(정본)**이며, TypeScript와 Rust 타입은 이를 기반으로 자동 생성됩니다. [근거: PHASE_B2 §6.1, §6.2]

**핵심 요약 (3줄)**
1. shared/ 폴더는 React(TypeScript), Rust, Python 3개 언어가 동일한 데이터 구조를 사용하도록 보장합니다.
2. Python contracts.py가 정본이며, JSON Schema를 거쳐 TypeScript/Rust 타입이 자동 생성됩니다.
3. 코드 생성 스크립트(codegen/)가 타입 동기화를 자동화하여 수작업 실수를 방지합니다.

---

## §33.6 Config (config/) — 설정 파일

### 비유: 가전제품의 설정 메뉴

> TV의 설정 메뉴에 밝기, 소리, 언어 등이 있듯이, config/ 폴더에는 VAMOS의 모든 설정이 카테고리별로 정리되어 있습니다. LLM 설정, 저장소 설정, 안전 설정 등 각각의 토글과 값을 TOML 파일로 관리합니다.

### config/ 구조

```
config/
├── default.toml                    # 기본 설정 (모든 환경 공통)
├── development.toml                # 개발 환경 설정
├── production.toml                 # 프로덕션 환경 설정
├── test.toml                       # 테스트 환경 설정
│
├── llm/                            # LLM 설정
│   ├── ollama.toml                 # Ollama 로컬 LLM [V1]
│   ├── openai.toml                 # OpenAI API [V1/V2]
│   └── anthropic.toml              # Anthropic API [V2+]
│
├── embedding/                      # 임베딩 설정
│   ├── bge_m3.toml                 # BGE-M3 로컬 임베딩 [V1]
│   └── openai_embedding.toml       # OpenAI 임베딩 [V2+]
│
├── storage/                        # 저장소 설정
│   ├── sqlite.toml                 # SQLite [V1]
│   ├── chroma.toml                 # Chroma 벡터 DB [V1]
│   ├── postgres.toml               # Postgres [V2+]
│   ├── qdrant.toml                 # Qdrant 벡터 DB [V2+]
│   └── neo4j.toml                  # Neo4j 그래프 DB [V2+]
│
├── safety/                         # 안전/가드레일 설정
│   ├── guardrails.toml             # 4-Layer Guardrails 설정
│   ├── rbac.toml                   # RBAC 역할/권한 설정
│   ├── autonomy.toml               # 자율 수준 (L0~L3)
│   └── cost_budget.toml            # 비용 예산 (V1: 40K/mo LOCK)
│
├── mcp/                            # MCP 설정
│   └── mcp_servers.toml            # MCP 서버 목록
│
└── nemo/                           # NeMo Guardrails 레일 정의
    ├── config.yml
    └── rails/
        ├── input.co                # 입력 레일
        └── output.co               # 출력 레일
```

### 환경 변수 (.env) 주요 항목

```bash
VAMOS_ENV=development               # 환경 (development/production/test)
VAMOS_LOG_LEVEL=debug               # 로그 레벨
OPENAI_API_KEY=sk-...               # OpenAI API 키
OLLAMA_HOST=http://localhost:11434  # Ollama 엔드포인트 [V1]
SQLITE_DB_PATH=./data/vamos.db     # SQLite 경로 [V1]
CHROMA_PERSIST_DIR=./data/chroma   # Chroma 데이터 경로 [V1]
VAMOS_COST_LIMIT_USD=30            # V1 월 비용 상한 ($30 = ₩40,000)
MCP_SERVER_URL=http://localhost:8080 # MCP 서버 URL
```

[근거: PHASE_B2 §8, §8.1]

**핵심 요약 (3줄)**
1. config/ 폴더에 환경별(개발/프로덕션/테스트) 설정과 카테고리별(LLM/저장소/안전/MCP) 설정이 TOML 파일로 관리됩니다.
2. API 키 등 비밀 정보는 .env 파일에 저장하고, .env.example만 Git에 커밋합니다.
3. 비용 예산(V1: ₩40,000/월 LOCK)과 자율 수준(L0~L3) 같은 핵심 설정이 여기서 관리됩니다.

---

---

# §34. API & 통신 시스템 — 88개 엔드포인트

## §34.1 Tauri IPC 커맨드 (72개)

### 비유: 은행의 번호표 창구 시스템

> 은행에 가면 "입출금", "대출", "외환" 등 업무별 창구가 있고, 번호표를 뽑아 순서대로 처리하죠. VAMOS의 IPC(프로세스 간 통신)도 마찬가지입니다. React UI(고객)가 Rust(은행 직원)에게 **번호표(trace_id)**를 받고, **창구(카테고리)**별로 요청을 보냅니다.

### 정의

**IPC (Inter-Process Communication, 프로세스 간 통신)**란 서로 다른 프로그램끼리 데이터를 주고받는 방식입니다. VAMOS에서는 React UI ↔ Rust 백엔드 사이의 통신을 **Tauri IPC**라고 합니다. [근거: PHASE_B1 §1.1]

### 88개 엔드포인트 전체 구성

```
┌──────────────────────────────────────────────────┐
│     VAMOS API 전체 — 총 88개 엔드포인트             │
│                                                  │
│  [Layer 1] Tauri IPC Commands     → 72개          │
│  (React ↔ Rust)                                  │
│                                                  │
│  [Layer 2] Python-Rust JSON-RPC   → 13개          │
│  (Rust → Python)                                 │
│                                                  │
│  [Layer 3] MCP Tool Protocol      →  3개          │
│  (Python → 외부 도구)                              │
│                                                  │
│  합계: 72 + 13 + 3 = 88개                         │
└──────────────────────────────────────────────────┘
```

[근거: PHASE_B1 §5.1~§5.3]

### IPC 커맨드 네이밍 규칙

모든 IPC 커맨드는 `vamos:{카테고리}:{동작}` 패턴을 따릅니다.

```
vamos:decision:create
  │      │        │
  │      │        └── 동작 (create, get, list, lock 등)
  │      └── 카테고리 (decision, workflow, memory 등)
  └── VAMOS 접두사 (모든 커맨드 공통)
```

[근거: PHASE_B1 §0 규칙]

### 통신 방향

| 방향 | 의미 | 비유 |
|------|------|------|
| **invoke** | React → Rust (요청-응답) | 고객이 창구에 요청하고 답을 받음 |
| **event** | Rust → React (단방향 푸시) | 은행에서 고객에게 알림을 보냄 |

### Tauri IPC 72개 — 카테고리별 분류

#### Core 카테고리 (15개) — 핵심 판단/워크플로우/세션

| # | Command | 방향 | 설명 |
|---|---------|------|------|
| 1 | `vamos:decision:create` | invoke | 새 Decision 생성 요청 |
| 2 | `vamos:decision:get` | invoke | Decision 조회 |
| 3 | `vamos:decision:list` | invoke | Decision 목록 조회 |
| 4 | `vamos:decision:lock` | invoke | Decision 잠금 (단일결정 원칙) |
| 5 | `vamos:decision:event` | event | Decision 상태 변경 알림 |
| 6 | `vamos:workflow:start` | invoke | 워크플로우 시작 (5단계 파이프라인 진입) |
| 7 | `vamos:workflow:status` | invoke | 현재 워크플로우 상태 조회 |
| 8 | `vamos:workflow:cancel` | invoke | 워크플로우 취소 |
| 9 | `vamos:workflow:output` | invoke | 워크플로우 최종 출력 조회 |
| 10 | `vamos:workflow:stage_event` | event | 워크플로우 단계 전환 알림 |
| 11 | `vamos:workflow:failure_report` | invoke | 실패 리포트 조회 |
| 12 | `vamos:session:create` | invoke | 새 세션 생성 |
| 13 | `vamos:session:get` | invoke | 세션 정보 조회 |
| 14 | `vamos:session:list` | invoke | 세션 목록 조회 |
| 15 | `vamos:session:close` | invoke | 세션 종료 |

[근거: PHASE_B1 §2.1]

#### Agent 카테고리 (15개) — 노드/파이프라인/마켓플레이스

| # | Command | 방향 | 설명 |
|---|---------|------|------|
| 16 | `vamos:node:dispatch` | invoke | Blue Node에 작업 전달 |
| 17 | `vamos:node:response` | event | Blue Node 실행 결과 알림 |
| 18 | `vamos:node:profile` | invoke | Node 역량 프로필 조회 |
| 19 | `vamos:node:list` | invoke | 등록된 Node 목록 조회 |
| 20 | `vamos:node:register` | invoke | 새 Node 등록 |
| 21 | `vamos:pipeline:gate_status` | invoke | 파이프라인 Gate 상태 조회 |
| 22 | `vamos:pipeline:gate_mapping` | invoke | Gate-Pipeline 매핑 조회/수정 |
| 23 | `vamos:pipeline:verify_chain` | invoke | Verify Chain 상태 조회 |
| 24 | `vamos:pipeline:circuit_breaker` | invoke | Circuit Breaker 상태 조회/제어 |
| 25 | `vamos:pipeline:hitl_respond` | invoke | HITL 요청에 응답 |
| 26 | `vamos:pipeline:hitl_event` | event | HITL 요청 알림 |
| 27 | `vamos:marketplace:list` | invoke | 마켓플레이스 에이전트 목록 |
| 28 | `vamos:marketplace:get` | invoke | 에이전트 상세 조회 |
| 29 | `vamos:marketplace:install` | invoke | 에이전트 설치 |
| 30 | `vamos:marketplace:uninstall` | invoke | 에이전트 제거 |

[근거: PHASE_B1 §2.2]

#### Storage 카테고리 (18개) — 메모리/벡터/캐시/GraphRAG/QoD

| # | Command | 방향 | 설명 |
|---|---------|------|------|
| 31 | `vamos:memory:save` | invoke | 메모리 레코드 저장 |
| 32 | `vamos:memory:get` | invoke | 메모리 레코드 조회 |
| 33 | `vamos:memory:search` | invoke | 메모리 검색 (텍스트/태그) |
| 34 | `vamos:memory:delete` | invoke | 메모리 레코드 삭제 |
| 35 | `vamos:memory:list` | invoke | 메모리 레코드 목록 |
| 36 | `vamos:memory:update_event` | event | 메모리 변경 알림 |
| 37 | `vamos:vector:search` | invoke | 벡터 유사도 검색 |
| 38 | `vamos:vector:upsert` | invoke | 벡터 삽입/업데이트 |
| 39 | `vamos:vector:delete` | invoke | 벡터 삭제 |
| 40 | `vamos:vector:adapter_config` | invoke | Vector Store 어댑터 설정 조회 |
| 41 | `vamos:cache:semantic_lookup` | invoke | 시맨틱 캐시 조회 |
| 42 | `vamos:cache:semantic_save` | invoke | 시맨틱 캐시 저장 |
| 43 | `vamos:cache:prompt_lookup` | invoke | 프롬프트 캐시 조회 |
| 44 | `vamos:cache:invalidate` | invoke | 캐시 무효화 |
| 45 | `vamos:graphrag:query` | invoke | GraphRAG 질의 (엔티티-관계 순회) |
| 46 | `vamos:graphrag:config` | invoke | GraphRAG 설정 조회/수정 |
| 47 | `vamos:qod:get` | invoke | 소스 QoD 점수 조회 |
| 48 | `vamos:qod:compute` | invoke | QoD 점수 재계산 요청 |

[근거: PHASE_B1 §2.3]

#### Safety 카테고리 (19개) — 정책/비용/승인/가드레일/RBAC/자율수준

| # | Command | 방향 | 설명 |
|---|---------|------|------|
| 49 | `vamos:policy:check` | invoke | 정책 체크 실행 |
| 50 | `vamos:policy:result` | invoke | 정책 체크 결과 조회 |
| 51 | `vamos:policy:block_event` | event | 정책 차단 알림 |
| 52 | `vamos:cost:budget_get` | invoke | 비용 예산 조회 |
| 53 | `vamos:cost:budget_update` | invoke | 비용 사용량 업데이트 |
| 54 | `vamos:cost:downshift_status` | invoke | 다운시프트 상태 조회 |
| 55 | `vamos:cost:downshift_event` | event | 다운시프트 트리거 알림 |
| 56 | `vamos:approval:request` | invoke | 승인 요청 생성 |
| 57 | `vamos:approval:decide` | invoke | 승인/거부 결정 |
| 58 | `vamos:approval:get` | invoke | 승인 상태 조회 |
| 59 | `vamos:approval:list` | invoke | 미결 승인 목록 조회 |
| 60 | `vamos:approval:request_event` | event | 승인 요청 알림 |
| 61 | `vamos:guardrails:check` | invoke | 4-Layer Guardrails 검사 |
| 62 | `vamos:guardrails:result` | invoke | 검사 결과 조회 |
| 63 | `vamos:guardrails:block_event` | event | Guardrails 차단 알림 |
| 64 | `vamos:rbac:get_role` | invoke | 현재 사용자 역할 조회 |
| 65 | `vamos:rbac:check_permission` | invoke | 권한 확인 |
| 66 | `vamos:autonomy:get_level` | invoke | 현재 자율 수준 조회 |
| 67 | `vamos:autonomy:set_level` | invoke | 자율 수준 변경 |

[근거: PHASE_B1 §2.4]

#### UI 카테고리 (5개) — 로그/설정/테마/알림

| # | Command | 방향 | 설명 |
|---|---------|------|------|
| 68 | `vamos:ui:log_stream` | event | UI 로그 스트림 (실시간) |
| 69 | `vamos:ui:config_get` | invoke | UI 설정 조회 |
| 70 | `vamos:ui:config_set` | invoke | UI 설정 변경 |
| 71 | `vamos:ui:theme_set` | invoke | 테마 설정 |
| 72 | `vamos:ui:notification` | event | UI 알림 (안전/비용/승인) |

[근거: PHASE_B1 §2.5]

### 카테고리별 요약표

| 카테고리 | 개수 | invoke | event | 주요 소스 스키마 |
|---------|------|--------|-------|----------------|
| Core (판단/워크플로우/세션) | 15 | 13 | 2 | D2, D5 |
| Agent (노드/파이프라인) | 15 | 13 | 2 | D3, D5 |
| Storage (메모리/벡터/캐시) | 18 | 17 | 1 | D4, D6 |
| Safety (정책/비용/승인) | 19 | 15 | 4 | D7 |
| UI (로그/설정/알림) | 5 | 3 | 2 | D2, D8 |
| **합계** | **72** | **61** | **11** | |

**핵심 요약 (3줄)**
1. Tauri IPC는 React↔Rust 통신 계층으로, 총 72개 커맨드가 5개 카테고리(Core/Agent/Storage/Safety/UI)로 분류됩니다.
2. 모든 커맨드는 `vamos:{카테고리}:{동작}` 패턴을 따르며, invoke(요청-응답) 61개 + event(단방향 푸시) 11개입니다.
3. 모든 요청과 응답에 trace_id가 필수로 포함되어 추적 가능성을 보장합니다.

---

## §34.2 Python-Rust JSON-RPC (13개)

### 비유: 사내 전화 내선 시스템

> 은행 창구(Rust)가 고객 요청을 받았는데, 전문가(Python AI)의 분석이 필요할 때 내선 전화(JSON-RPC)로 연구부서를 호출합니다. 내선 번호(method)를 누르고, 요청 내용(params)을 전달하면, 연구부서가 결과(result)를 돌려줍니다.

### 정의

**JSON-RPC**란 JSON 형식으로 원격 함수를 호출하는 경량 프로토콜입니다. VAMOS V1에서는 Rust가 Python 프로세스를 subprocess로 실행하고, **stdin/stdout**(표준 입출력)을 통해 JSON-RPC 2.0 메시지를 교환합니다. [근거: PHASE_B1 §3.0]

### 13개 Python-Rust JSON-RPC 메서드

| # | Method | 소스 스키마 | 비유 |
|---|--------|------------|------|
| 1 | `langgraph.workflow.run` | D5 WorkflowOutputEnvelopeSchema | 작업라인 전체 가동 |
| 2 | `langgraph.stage.execute` | D5 WorkflowStageSchema | 작업라인 한 단계만 실행 |
| 3 | `langgraph.decision.create` | D2 DecisionSchema | 사령부에 판단 요청 |
| 4 | `langgraph.node.dispatch` | D3 NodeRequest/ResponseEnvelope | 전문가 팀에 작업 배정 |
| 5 | `langgraph.verify.run_chain` | D5 VerifyChainEntrySchema | 검증 체인 실행 |
| 6 | `embedding.encode` | D6 KBEmbeddingRecordSchema | 텍스트를 벡터로 변환 |
| 7 | `embedding.store` | D6 VectorStoreAdapterSchema | 벡터 저장 |
| 8 | `llm.generate` | D4 BrainAdapterResponseSchema | LLM에 텍스트 생성 요청 |
| 9 | `llm.record_invoke` | D4 InfraInvokeResultSchema | LLM 호출 기록 저장 |
| 10 | `llm.rate_limit.get` | D4 RateLimitConfigSchema | 속도 제한 설정 조회 |
| 11 | `mcp.bridge.init` | D3 MCPBridgeLayerSchema | MCP Bridge 초기화 |
| 12 | `mcp.bridge.health` | D3 MCPBridgeLayerSchema | MCP Bridge 건강 체크 |
| 13 | `mcp.tools.discover` | D3 ToolCallRegistrySchema | MCP 도구 발견 |

[근거: PHASE_B1 §5.2]

### JSON-RPC 메시지 형식

```
Rust → Python (요청):
{
  "jsonrpc": "2.0",
  "method": "langgraph.workflow.run",     ← 내선 번호
  "params": { "trace_id": "...", ... },    ← 요청 내용
  "id": "req_001"                          ← 통화 번호
}

Python → Rust (성공 응답):
{
  "jsonrpc": "2.0",
  "result": { ... },                       ← 결과
  "id": "req_001"                          ← 통화 번호 (매칭)
}

Python → Rust (에러 응답):
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32000,                        ← VAMOS 비즈니스 에러
    "message": "에러 메시지",
    "data": {
      "failure_code": "OC_I5_COST_OVER_BUDGET",
      "trace_id": "..."
    }
  },
  "id": "req_001"
}
```

[근거: PHASE_B1 §3.0]

### 버전별 통신 방식 변화

| 버전 | 통신 방식 | 설명 |
|------|----------|------|
| V1 | JSON-RPC over subprocess (stdin/stdout) | 간단하고 안정적, 로컬 전용 |
| V2+ | gRPC (선택 전환 가능) | 고성능, 바이너리 프로토콜 |

[근거: PHASE_B1 §1.3]

**핵심 요약 (3줄)**
1. Python-Rust JSON-RPC는 Rust가 Python AI를 호출하는 13개 내부 API로, subprocess stdin/stdout을 통해 통신합니다.
2. 5개 LangGraph 메서드(워크플로우/판단/노드/검증), 3개 임베딩/LLM 메서드, 3개 MCP 메서드 등으로 분류됩니다.
3. V1은 JSON-RPC subprocess, V2+는 gRPC로 전환할 수 있습니다.

---

## §34.3 MCP Tool Protocol (3개)

### 비유: 해외 주문 시스템

> 국내 업무는 내선 전화(JSON-RPC)로 처리하지만, 해외 거래(외부 도구 호출)는 국제 표준 양식(MCP Protocol)을 사용합니다. 웹 검색, 코드 실행, DB 접근 같은 외부 도구는 모두 MCP 표준으로 호출합니다.

### 3개 MCP Tool Protocol 메서드

| # | Method | 프로토콜 | 설명 | 비유 |
|---|--------|---------|------|------|
| 1 | `tools/call` | MCP Streamable HTTP | 외부 도구 실제 호출 (JSON-RPC 2.0) | 해외에 주문 전송 |
| 2 | `mcp.tool_registry.get` | 내부 | ToolRegistry 단건 조회 | 도구 카탈로그에서 하나 찾기 |
| 3 | `mcp.tool_registry.list` | 내부 | ToolRegistry 목록 조회 | 도구 카탈로그 전체 목록 보기 |

[근거: PHASE_B1 §5.3]

### MCP 도구 호출 예시 (`tools/call`)

```
POST http://localhost:3001/mcp
Content-Type: application/json
Authorization: Bearer {token}

{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "web_search",           ← 어떤 도구?
    "arguments": {
      "query": "VAMOS AI 에이전트",   ← 검색어
      "max_results": 10              ← 최대 결과 수
    }
  },
  "id": "call_001"
}
```

> **전송 방식**: **Streamable HTTP** (DEC-017 LOCK — 변경 불가). 모든 MCP 통신은 이 방식만 사용합니다. [근거: PHASE_B1 §4]

**핵심 요약 (3줄)**
1. MCP Tool Protocol은 외부 도구를 호출하는 3개 메서드로, MCP 표준 규격을 따릅니다.
2. 실제 도구 호출은 `tools/call`로 하고, 나머지 2개는 도구 카탈로그 조회용입니다.
3. 전송 방식은 Streamable HTTP만 사용합니다 (DEC-017 LOCK).

---

## §34.4 IPC Bridge (Rust ↔ Python)

### 비유: 통역사 (두 언어 사이에서 번역)

> 한국어(React/Rust)와 프랑스어(Python)를 사용하는 두 팀이 함께 일할 때, 통역사가 양쪽 말을 번역해줍니다. IPC Bridge가 바로 이 통역사 역할입니다. Rust가 Python에게 "이 작업 해줘"라고 요청하면, Bridge가 JSON-RPC 형식으로 번역하여 Python에게 전달하고, 결과를 다시 Rust에게 돌려줍니다.

### 통신 방식: subprocess + JSON-RPC

```
┌──────────┐                      ┌──────────┐
│ React UI │                      │ Python   │
│ (고객)    │                      │ AI/ML    │
│          │                      │ (연구소)  │
└─────┬────┘                      └─────┬────┘
      │ Tauri IPC (invoke/event)        │
      ↓                                 ↑
┌──────────────────────────────────────────┐
│             Rust/Tauri (관리실)            │
│                                          │
│  commands/  ←→  bridge/                  │
│  (IPC 접수)     (통역사)                   │
│                   │                      │
│                   │ subprocess           │
│                   │ stdin/stdout         │
│                   │ JSON-RPC 2.0         │
│                   ↓                      │
│              PythonManager               │
│              (Python 프로세스 관리)        │
└──────────────────────────────────────────┘
```

### IPC Bridge 구성 요소

| 구성 요소 | 파일 위치 | 역할 | 비유 |
|----------|----------|------|------|
| PythonManager | `src-tauri/src/bridge/python_manager.rs` | Python 프로세스 시작/종료/재시작 | 연구소 문 열고 닫기 |
| IPCProtocol | `src-tauri/src/bridge/ipc_protocol.rs` | JSON-RPC 메시지 인코딩/디코딩 | 통역사의 번역 작업 |
| HealthCheck | `src-tauri/src/bridge/health_check.rs` | Python 프로세스 건강 체크 | 연구소 정상 운영 확인 순찰 |

[근거: PHASE_B2 §4.3]

### 전체 데이터 흐름

```
React UI  ──[invoke]──→  Rust IPC Handler
                              │
                    ┌─────────┴─────────┐
                    │                   │
              [JSON-RPC]          [MCP HTTP]
                    │                   │
              Python Backend       MCP Server
              (LangGraph/LLM)     (외부 도구)
```

1. **React UI** → `invoke`로 Rust에 요청
2. **Rust** → 단순 작업은 직접 처리, AI 관련은 Python에 JSON-RPC로 전달
3. **Python** → LangGraph/LLM으로 처리 후 결과 반환
4. **Rust** → 결과를 React에 전달 (또는 event로 실시간 푸시)

[근거: PHASE_B1 §1.2]

**핵심 요약 (3줄)**
1. IPC Bridge는 Rust와 Python 사이의 통역사로, subprocess + JSON-RPC stdin/stdout 방식으로 통신합니다.
2. PythonManager가 Python 프로세스를 관리하고, IPCProtocol이 메시지를 번역하며, HealthCheck가 건강을 감시합니다.
3. 전체 흐름은 React → Rust(IPC) → Python(JSON-RPC) → 외부 도구(MCP HTTP) 순서입니다.

---

## §34.5 응답 형식 표준 (trace_id 필수)

### 비유: 택배 송장번호

> 택배를 보내면 송장번호가 있어서 어디에 있는지 추적할 수 있죠. VAMOS의 **trace_id**도 마찬가지입니다. 모든 요청과 응답에 고유한 추적 ID가 붙어서, "이 결과가 어떤 요청에서 나왔는지" 완벽하게 추적할 수 있습니다.

### trace_id란?

**trace_id (추적 ID)**는 하나의 사용자 요청이 시스템을 통과하는 전체 경로를 추적하기 위한 **고유 식별자**입니다.

```
사용자 질문: "삼성전자 주가 분석해줘"
     ↓
trace_id: "tr_01HZX9R1ABCDE"  ← 이 번호로 전 과정 추적 가능
     ↓
React → Rust → Python → MCP → 결과 반환
     (모든 단계에 같은 trace_id가 따라감)
```

[근거: PHASE_B1 §0 규칙]

### 표준 성공 응답 JSON 구조

```typescript
{
  success: true,                    // 성공 여부
  data: {                           // 실제 데이터 (요청마다 다름)
    // ... 커맨드별 결과 데이터
  },
  trace_id: "tr_01HZX9R1ABCDE"     // 추적 ID (필수!)
}
```

### 표준 에러 응답 JSON 구조

```typescript
{
  success: false,                   // 실패
  error: {
    code: "OC_I5_COST_OVER_BUDGET", // 에러 코드 (D2 FailureCodeRegistry)
    message: "비용 한도를 초과했습니다. 경량 모델로 전환합니다.",
    trace_id: "tr_01HZX9R1ABCDE",  // 추적 ID (필수!)
    fallback_id: "FB_COST_DOWNSHIFT", // 대안 동작 ID (D2 FallbackRegistry)
    details: { ... }                 // 추가 상세 (선택)
  }
}
```

[근거: PHASE_B1 §0 규칙, §6.1]

### 주요 에러 코드 (FailureCode) 일부 발췌

| 에러 코드 | 의미 | 대안 동작 (Fallback) | 사용자 메시지 |
|----------|------|---------------------|-------------|
| `OC_I1_PARSE_FAIL` | 의도 파싱 실패 | 경험적 파싱 재시도 | "입력을 이해하지 못했습니다. 다시 시도합니다." |
| `OC_I2_RAG_NO_SOURCE` | RAG 소스 없음 | 검색 범위 확장 | "관련 자료를 찾지 못했습니다." |
| `OC_I5_POLICY_BLOCK` | 정책 차단 | 사유와 함께 거부 | "정책에 의해 실행이 차단되었습니다." |
| `OC_I5_COST_OVER_BUDGET` | 비용 초과 | 경량 모델 전환 | "비용 한도를 초과했습니다." |
| `OC_I5_APPROVAL_REQUIRED` | 승인 필요 | 승인 요청 | "실행을 위해 승인이 필요합니다." |
| `TOOL_TIMEOUT` | 도구 호출 타임아웃 | 재시도 후 대체 | "외부 도구 호출 시간이 초과되었습니다." |

[근거: PHASE_B1 §6.2]

### HTTP 상태 코드 매핑 (MCP/외부 API용)

| 상태 코드 | 용도 | 비유 |
|-----------|------|------|
| 200 | 성공 | 주문 완료 |
| 400 | 잘못된 요청 (파라미터 오류) | 주문서 작성 오류 |
| 401 | 인증 실패 | 신분증 미제시 |
| 403 | 권한 없음 (RBAC 차단) | 출입 금지 구역 |
| 404 | 리소스 없음 | 찾는 물건 없음 |
| 429 | Rate Limit 초과 | 주문 너무 많음, 잠시 대기 |
| 500 | 내부 서버 에러 | 시스템 고장 |
| 503 | Circuit Breaker 차단 중 | 장애로 일시 중단 |

[근거: PHASE_B1 §6.3]

### 전체 88개 엔드포인트 — 최종 요약

| 계층 | 프로토콜 | 방향 | 개수 | 비유 |
|------|---------|------|------|------|
| Layer 1: Tauri IPC | Tauri invoke/event | React ↔ Rust | **72개** | 은행 창구 |
| Layer 2: Python-Rust | JSON-RPC subprocess | Rust → Python | **13개** | 내선 전화 |
| Layer 3: MCP Tool | Streamable HTTP | Python → 외부 도구 | **3개** | 해외 주문 |
| **총합** | | | **88개** | |

**핵심 요약 (3줄)**
1. 모든 응답(성공/에러)에 trace_id가 필수로 포함되어, 요청의 전체 경로를 택배 송장번호처럼 추적할 수 있습니다.
2. 에러 발생 시 FailureCode + FallbackID 조합으로 자동 대안 동작이 실행됩니다 (예: 비용 초과 → 경량 모델 전환).
3. 88개 엔드포인트는 3개 계층(Tauri IPC 72개, JSON-RPC 13개, MCP 3개)으로 명확히 분리되어 있습니다.

---

---

# 검증 체크리스트

- [x] 전체 디렉토리 트리? (§33.1 — 루트~하위 전체 트리 표시)
- [x] Frontend/Rust/Python 각각 설명? (§33.2 src/, §33.3 src-tauri/, §33.4 backend/)
- [x] 88개 엔드포인트 분류? (§34.1~§34.3 — 72+13+3=88 확인)
- [x] Tauri IPC 72개? (§34.1 — 5개 카테고리별 전체 목록)
- [x] JSON-RPC 13개? (§34.2 — 13개 메서드 전체 목록)
- [x] IPC Bridge 설명? (§34.4 — subprocess + JSON-RPC 통신 구조)
- [x] trace_id 표준? (§34.5 — 성공/에러 응답 표준 JSON 구조)
- [x] 비유 설명 포함? (모든 섹션에 비유 포함)
- [x] 근거 SOT 참조 표기? (모든 섹션에 [근거:] 표기)
