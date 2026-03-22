# PHASE_B2_PROJECT_STRUCTURE (v1.0.0)

## 0. 문서 메타

| 항목 | 내용 |
|------|------|
| 문서 ID | B2 |
| 문서명 | PHASE_B2_PROJECT_STRUCTURE |
| 버전 | 1.0.0 |
| 작성일 | 2026-02-22 |
| 역할 | VAMOS AI 에이전트 플랫폼 프로젝트 디렉토리/모듈 구조 설계 |
| 상위 참조 | A1_TECH_STACK (COMBO-V1/V2/V3 LOCK), D1~D8 스키마 문서, D8 UI/UX 계약 |
| 대상 버전 | V1 (로컬 MVP) 기준, V2/V3 확장 경로 포함 |

### 연결 참조
- A1 Tech Stack: COMBO-V1 LOCK (Tauri 2.0 + React / Rust / Python)
- D1 Glossary: 22 용어, 16+ 스키마 매핑
- D2~D7 Schema: Pydantic v2 모델 → Python 모듈 매핑 근거
- D8 UI/UX: 문서형 계약 (Tauri LOCK, Canvas/Artifacts/알림/자율수준UI)

---

## 1. 개요 (Monorepo vs Polyrepo 결정)

### 1.1 결정: Monorepo (LOCK)

| 항목 | Monorepo | Polyrepo |
|------|----------|----------|
| Tauri 호환성 | Tauri 2.0은 src-tauri/와 프론트를 같은 루트에 요구 | 별도 repo 관리 시 빌드 복잡도 증가 |
| 스키마 공유 | Rust/Python/React 간 타입 공유 용이 | 타입 동기화에 별도 패키지 필요 |
| CI/CD | 단일 파이프라인으로 통합 테스트 | 멀티 repo 오케스트레이션 필요 |
| V1 적합성 | 로컬 MVP에 최적 (단일 개발자/소팀) | 오버엔지니어링 |

**결정 근거**: Tauri 2.0 프로젝트 구조 특성상 `src-tauri/`와 프론트엔드가 동일 루트에 위치해야 하며, V1 단일 개발자/소팀 환경에서 Monorepo가 관리 효율이 높다.

### 1.2 저장소 이름

```
vamos/                  # Git 루트 (Monorepo)
```

---

## 2. 루트 디렉토리 레이아웃

```
vamos/
├── .github/                        # GitHub Actions CI/CD
│   └── workflows/
│       ├── ci.yml                  # 통합 CI (lint, test, build)
│       └── release.yml             # 릴리즈 빌드 (Tauri bundle)
├── .vscode/                        # VSCode 공유 설정
│   ├── settings.json               # 포매터/린터 설정
│   └── extensions.json             # 권장 확장
├── src/                            # React 프론트엔드 (섹션 3)
├── src-tauri/                      # Rust Tauri 백엔드 (섹션 4)
├── backend/                        # Python AI/ML 백엔드 (섹션 5)
├── shared/                         # 공유 타입/인터페이스 (섹션 6)
├── tests/                          # 통합 테스트 (섹션 7)
├── config/                         # 설정/환경 파일 (섹션 8)
├── docs/                           # 프로젝트 문서
│   └── schemas/                    # D1~D8 스키마 참조 문서
├── scripts/                        # 빌드/배포 스크립트
│   ├── setup.sh                    # 개발 환경 초기화
│   ├── dev.sh                      # 개발 서버 통합 실행
│   └── build.sh                    # 프로덕션 빌드
├── .env.example                    # 환경 변수 템플릿
├── .gitignore                      # Git 무시 규칙
├── package.json                    # 프론트엔드 의존성 (섹션 B3)
├── tsconfig.json                   # TypeScript 설정
├── vite.config.ts                  # Vite 번들러 설정
├── tailwind.config.ts              # TailwindCSS 설정
├── postcss.config.js               # PostCSS 설정
└── README.md                       # 프로젝트 개요
```

---

## 3. Frontend (React + Tauri)

### 3.1 src/ 구조

```
src/
├── main.tsx                        # React 엔트리포인트
├── App.tsx                         # 루트 컴포넌트 + 라우터
├── vite-env.d.ts                   # Vite 타입 선언
│
├── components/                     # 재사용 UI 컴포넌트
│   ├── common/                     # 범용 컴포넌트 (Button, Modal, Input 등)
│   │   ├── Button.tsx
│   │   ├── Modal.tsx
│   │   ├── Input.tsx
│   │   ├── Card.tsx
│   │   ├── Badge.tsx
│   │   ├── Tooltip.tsx
│   │   └── Spinner.tsx
│   ├── layout/                     # 레이아웃 컴포넌트 (Header, Sidebar, Footer)
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   ├── Footer.tsx
│   │   └── MainLayout.tsx
│   ├── canvas/                     # Canvas 컴포넌트 (D8 §4 — 워크플로우 시각화)
│   │   ├── CanvasView.tsx          # 워크플로우 캔버스 뷰
│   │   ├── NodeInspector.tsx       # 노드 상세 인스펙터
│   │   ├── FlowEdge.tsx           # 노드 간 연결선
│   │   └── MiniMap.tsx            # 캔버스 미니맵
│   ├── artifacts/                  # Artifacts 컴포넌트 (D8 §6 — 산출물 뷰어)
│   │   ├── ArtifactViewer.tsx     # 산출물 뷰어/에디터
│   │   ├── ArtifactList.tsx       # 산출물 목록
│   │   └── ArtifactExport.tsx     # 산출물 내보내기
│   ├── notifications/              # 알림 컴포넌트 (D8 §7 — 이벤트 알림)
│   │   ├── NotificationCenter.tsx # 알림 센터
│   │   ├── NotificationItem.tsx   # 개별 알림 항목
│   │   └── NotificationBadge.tsx  # 알림 배지
│   ├── autonomy/                   # 자율수준 UI (D8 §10 — L0~L3 제어)
│   │   ├── AutonomyPanel.tsx      # 자율수준 제어 패널
│   │   ├── AutonomySlider.tsx     # L0~L3 슬라이더
│   │   └── ApprovalDialog.tsx     # HITL 승인 다이얼로그
│   ├── decision/                   # Decision 관련 UI
│   │   ├── DecisionCard.tsx       # Decision 결과 카드
│   │   ├── DecisionTimeline.tsx   # Decision 타임라인
│   │   └── GateStatus.tsx         # Gate 상태 표시
│   ├── memory/                     # 메모리 관련 UI
│   │   ├── MemoryBrowser.tsx      # 메모리 탐색기 (L0~L3)
│   │   ├── MemoryDetail.tsx       # 메모리 레코드 상세
│   │   └── MemorySearch.tsx       # 메모리 검색
│   ├── cost/                       # 비용/예산 관련 UI
│   │   ├── CostDashboard.tsx      # 비용 대시보드
│   │   ├── BudgetMeter.tsx        # 예산 미터 (Downshift 표시)
│   │   └── CostHistory.tsx        # 비용 이력 차트
│   └── log/                        # 로그 뷰어 UI
│       ├── LogViewer.tsx           # 로그 스트림 뷰어
│       ├── LogFilter.tsx           # 로그 필터 (event_type 기반)
│       └── TraceView.tsx           # Trace 추적 뷰
│
├── pages/                          # 페이지 컴포넌트 (라우트 단위)
│   ├── DashboardPage.tsx           # 메인 대시보드
│   ├── ChatPage.tsx                # 대화 인터페이스 (ORANGE CORE 입력)
│   ├── WorkflowPage.tsx            # 워크플로우 빌더/뷰어
│   ├── MemoryPage.tsx              # 메모리 관리 페이지
│   ├── SettingsPage.tsx            # 설정 페이지 (RBAC/자율수준/비용)
│   ├── LogPage.tsx                 # 로그/감사 페이지
│   └── NodeDetailPage.tsx          # BLUE NODE 상세 페이지
│
├── hooks/                          # 커스텀 React 훅
│   ├── useTauriIPC.ts              # Tauri IPC 통신 훅
│   ├── useDecision.ts              # Decision 상태 관리 훅
│   ├── useWorkflow.ts              # 워크플로우 상태 훅
│   ├── useMemory.ts                # 메모리 조회/저장 훅
│   ├── useCost.ts                  # 비용 조회 훅
│   ├── useNotification.ts          # 알림 구독 훅
│   ├── useAutonomy.ts              # 자율수준 제어 훅
│   └── useLog.ts                   # 로그 스트림 구독 훅
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
│   ├── decision.ts                 # DecisionSchema 타입 (D2 매핑)
│   ├── logEvent.ts                 # LogEventSchema 타입 (D2 매핑)
│   ├── blueNode.ts                 # NodeCapabilityProfile 등 (D3 매핑)
│   ├── workflow.ts                 # WorkflowOutputEnvelope 등 (D5 매핑)
│   ├── memory.ts                   # MemoryRecord, SourceQoD 등 (D6 매핑)
│   ├── safety.ts                   # PolicyCheck, Approval, CostBudget (D7 매핑)
│   ├── infra.ts                    # ToolRegistryEntry, BrainAdapter (D4 매핑)
│   ├── common.ts                   # 공통 타입 (ID, Timestamp, Enum)
│   └── ipc.ts                      # Tauri IPC 메시지 타입
│
├── utils/                          # 유틸리티 함수
│   ├── formatters.ts               # 데이터 포맷팅 유틸
│   ├── validators.ts               # 클라이언트 검증 유틸
│   ├── constants.ts                # 상수 정의 (event_type, failure_code 등)
│   ├── dateUtils.ts                # 날짜/시간 유틸
│   └── tauriHelpers.ts             # Tauri API 래퍼 유틸
│
├── styles/                         # 글로벌 스타일
│   ├── globals.css                 # TailwindCSS 글로벌 스타일
│   ├── variables.css               # CSS 변수 (색상/간격)
│   └── animations.css              # 애니메이션 정의
│
└── assets/                         # 정적 자산 (이미지, 아이콘)
    ├── icons/
    └── images/
```

### 3.2 UI 컴포넌트 카테고리 (D8 매핑)

| 카테고리 | 디렉토리 | D8 근거 | 설명 |
|----------|----------|---------|------|
| Canvas | `components/canvas/` | D8 §4 — 워크플로우 시각화 | LangGraph StateGraph 시각화, 노드 인스펙션 |
| Artifacts | `components/artifacts/` | D8 §6 — 산출물 뷰어 | 워크플로우 산출물 조회/내보내기 |
| 알림 | `components/notifications/` | D8 §7 — 이벤트 알림 | LogEvent 기반 실시간 알림 (ui.* event_type) |
| 자율수준 UI | `components/autonomy/` | D8 §10 — L0~L3 제어 | AutonomyLevel 제어, HITL 승인 UI |
| Decision | `components/decision/` | D2 DecisionSchema | Decision 결과 표시, Gate 상태 |
| Memory | `components/memory/` | D6 MemoryRecordSchema | 메모리 계층 (L0~L3) 탐색/관리 |
| Cost | `components/cost/` | D7 CostBudgetSchema | 비용 대시보드, Downshift 표시 |
| Log | `components/log/` | D2 LogEventSchema | 이벤트 로그 스트림, Trace 추적 |

---

## 4. Backend -- Rust (Tauri Core)

### 4.1 src-tauri/ 구조

```
src-tauri/
├── Cargo.toml                      # Rust 의존성 (섹션 B3)
├── Cargo.lock                      # 의존성 잠금
├── build.rs                        # Tauri 빌드 스크립트
├── tauri.conf.json                 # Tauri 설정 (윈도우, 번들, 권한)
├── capabilities/                   # Tauri 2.0 권한 정의
│   └── default.json                # 기본 권한 매니페스트
├── icons/                          # 앱 아이콘 (빌드용)
│
└── src/
    ├── main.rs                     # Tauri 엔트리포인트 (setup, 플러그인 등록)
    ├── lib.rs                      # 라이브러리 루트 (모듈 re-export)
    │
    ├── commands/                   # IPC 커맨드 모듈 (4.2 상세)
    │   ├── mod.rs                  # 커맨드 모듈 루트
    │   ├── decision.rs             # Decision 관련 IPC (요청/조회)
    │   ├── workflow.rs             # 워크플로우 실행/조회 IPC
    │   ├── memory.rs               # 메모리 CRUD IPC
    │   ├── cost.rs                 # 비용 조회 IPC
    │   ├── settings.rs             # 설정 변경 IPC
    │   ├── log.rs                  # 로그 조회/스트림 IPC
    │   └── system.rs               # 시스템 상태/건강 체크 IPC
    │
    ├── bridge/                     # Python 프로세스 관리 (4.3 상세)
    │   ├── mod.rs                  # 브리지 모듈 루트
    │   ├── python_manager.rs       # Python subprocess 생명주기 관리
    │   ├── ipc_protocol.rs         # Rust-Python IPC 프로토콜 (JSON-RPC/stdin-stdout)
    │   └── health_check.rs         # Python 프로세스 건강 체크
    │
    ├── state/                      # Tauri 앱 상태 관리
    │   ├── mod.rs                  # 상태 모듈 루트
    │   └── app_state.rs            # 글로벌 앱 상태 (Python 프로세스 핸들 등)
    │
    ├── models/                     # Rust 데이터 모델 (serde)
    │   ├── mod.rs                  # 모델 루트
    │   ├── decision.rs             # DecisionSchema Rust 구조체
    │   ├── log_event.rs            # LogEventSchema Rust 구조체
    │   ├── envelope.rs             # NodeRequest/ResponseEnvelope Rust 구조체
    │   ├── cost.rs                 # CostBudget Rust 구조체
    │   └── common.rs               # 공통 타입 (ID, Timestamp 등)
    │
    ├── utils/                      # 유틸리티
    │   ├── mod.rs
    │   ├── config.rs               # 설정 파일 로드
    │   └── error.rs                # VamosError Rust 구현
    │
    └── tests/                      # Rust 단위 테스트
        ├── command_tests.rs        # IPC 커맨드 테스트
        └── bridge_tests.rs         # Python 브리지 테스트
```

### 4.2 IPC Command 모듈

Tauri 2.0의 `#[tauri::command]` 매크로를 사용하여 프론트엔드(React)와 Rust 백엔드 간 IPC를 정의한다.

| 모듈 | 파일 | 주요 커맨드 | 설명 |
|------|------|------------|------|
| Decision | `commands/decision.rs` | `submit_request`, `get_decision` | ORANGE CORE 요청 전송, Decision 결과 조회 |
| Workflow | `commands/workflow.rs` | `run_workflow`, `get_workflow_status` | 워크플로우 실행, 상태 조회 |
| Memory | `commands/memory.rs` | `search_memory`, `save_memory`, `delete_memory` | 메모리 CRUD (L0~L3) |
| Cost | `commands/cost.rs` | `get_cost_summary`, `get_budget_status` | 비용 요약, 예산 상태 |
| Settings | `commands/settings.rs` | `get_settings`, `update_settings` | 설정 조회/변경 (RBAC, 자율수준) |
| Log | `commands/log.rs` | `get_logs`, `stream_logs` | 로그 조회, 실시간 스트림 |
| System | `commands/system.rs` | `health_check`, `get_system_info` | 시스템 건강 체크, 정보 |

### 4.3 Python Subprocess 관리

Tauri(Rust) 백엔드는 Python AI/ML 백엔드를 subprocess로 관리한다.

```
[React UI] --IPC--> [Rust/Tauri] --subprocess(stdin/stdout)--> [Python AI/ML]
```

| 컴포넌트 | 파일 | 역할 |
|----------|------|------|
| PythonManager | `bridge/python_manager.rs` | Python 프로세스 시작/종료/재시작 |
| IPCProtocol | `bridge/ipc_protocol.rs` | JSON-RPC over stdin/stdout 프로토콜 |
| HealthCheck | `bridge/health_check.rs` | 주기적 건강 체크, 자동 재시작 |

---

## 5. Backend -- Python (AI/ML)

### 5.1 패키지 구조 (vamos_core/)

```
backend/
├── pyproject.toml                  # Python 프로젝트 설정/의존성 (섹션 B3)
├── poetry.lock                     # 의존성 잠금 (Poetry 사용 시)
│
├── vamos_core/                     # 메인 패키지
│   ├── __init__.py                 # 패키지 초기화, 버전 정보
│   ├── main.py                     # IPC 서버 엔트리포인트 (Rust subprocess 수신)
│   ├── config.py                   # 설정 로드 (환경변수, config/*.toml)
│   │
│   ├── orange_core/                # ORANGE CORE 모듈 (5.2 상세)
│   ├── blue_nodes/                 # BLUE NODES 모듈 (5.3 상세)
│   ├── infra/                      # 인프라 모듈 (5.4 상세)
│   ├── agent/                      # Agent 워크플로우 모듈 (5.5 상세)
│   ├── storage/                    # 저장/메모리 모듈 (5.6 상세)
│   ├── safety/                     # 안전/비용 모듈 (5.7 상세)
│   ├── schemas/                    # Pydantic v2 스키마 (5.8 상세)
│   └── mcp/                        # MCP Bridge 모듈 (5.9 상세)
│
└── tests/                          # Python 테스트 (섹션 7)
    ├── conftest.py                 # pytest 공통 fixture
    ├── unit/                       # 단위 테스트
    ├── integration/                # 통합 테스트
    └── e2e/                        # E2E 테스트
```

### 5.2 orange_core/ (I-1~I-5 모듈, Decision Kernel)

ORANGE CORE는 중앙 사령탑으로, 5개 내부 모듈(I-1~I-5)과 Decision Kernel로 구성된다.

```
orange_core/
├── __init__.py                     # ORANGE CORE 패키지 초기화
├── decision_kernel.py              # Decision Kernel — I-1~I-5 오케스트레이션, DecisionSchema 생성
├── front_mini.py                   # Front Mini — 빠른 의도 분류 (경량 LLM)
│
├── i1_intent/                      # I-1: Intent Parser — 의도 해석
│   ├── __init__.py
│   ├── parser.py                   # IntentFrame 생성 (의도 분류)
│   └── classifier.py              # 의도 분류기 (query/action/creative/analysis/chat/other)
│
├── i2_evidence/                    # I-2: Evidence Collector — 근거 수집
│   ├── __init__.py
│   ├── collector.py                # EvidencePack 생성 (RAG + 외부 소스)
│   └── qod_scorer.py              # QoD(Quality of Data) 점수 산출
│
├── i3_memory/                      # I-3: Memory Planner — 메모리 계획
│   ├── __init__.py
│   └── planner.py                  # Memory Plan 생성 (저장 계층/정책 결정)
│
├── i4_output/                      # I-4: Output Structurer — 출력 구조화
│   ├── __init__.py
│   ├── structurer.py               # 출력 포맷팅 (markdown/json/etc)
│   └── masker.py                   # 민감 정보 마스킹 (I-4 mask)
│
└── i5_gate/                        # I-5: Gate Evaluator — 게이트 평가/라우팅
    ├── __init__.py
    ├── evaluator.py                # Policy/Approval/Cost Gate 통합 평가
    └── router.py                   # BLUE NODE 라우팅 결정
```

**D2 스키마 매핑**:
| 모듈 | 생성하는 스키마 | 소유 문서 |
|------|----------------|----------|
| `decision_kernel.py` | DecisionSchema | D2 |
| 전체 모듈 (로그) | LogEventSchema (oc.* event_type) | D2 |
| `i1_intent/parser.py` | IntentFrame (Decision 내부 참조) | D2 |
| `i2_evidence/collector.py` | EvidencePack (Decision 내부 참조) | D2 |

### 5.3 blue_nodes/ (도메인별 노드)

BLUE NODE는 도메인 실행 모듈로, ORANGE CORE의 라우팅 결정에 따라 호출된다.

```
blue_nodes/
├── __init__.py                     # BLUE NODES 패키지 초기화
├── base_node.py                    # BaseBlueNode 추상 클래스 (Runnable 인터페이스)
├── node_registry.py                # NodeRegistry 관리 (D3 NodeRegistry SOT)
│
├── dev/                            # Dev 노드 — 코드 생성/분석/리뷰
│   ├── __init__.py
│   ├── node.py                     # DevNode 구현
│   ├── code_gen.py                 # 코드 생성 도구
│   ├── code_review.py              # 코드 리뷰 도구
│   └── sandbox.py                  # Docker Sandbox 코드 실행
│
├── research/                       # Research 노드 — 리서치/분석
│   ├── __init__.py
│   ├── node.py                     # ResearchNode 구현
│   ├── web_search.py               # 웹 검색 도구
│   └── summarizer.py               # 요약 도구
│
├── content/                        # Content 노드 — 콘텐츠 생성
│   ├── __init__.py
│   ├── node.py                     # ContentNode 구현
│   ├── writer.py                   # 문서 작성 도구
│   └── formatter.py                # 포맷 변환 도구
│
├── quant/                          # Quant 노드 — 정량 분석
│   ├── __init__.py
│   ├── node.py                     # QuantNode 구현
│   ├── data_fetcher.py             # 데이터 수집 도구
│   └── analyzer.py                 # 분석/통계 도구
│
└── trading/                        # Trading 노드 — 투자/매매 [V2+]
    ├── __init__.py
    ├── node.py                     # TradingNode 구현 [V2+]
    ├── signal.py                   # 시그널 생성 [V2+]
    └── executor.py                 # 주문 실행 [V2+]
```

**D3 스키마 매핑**:
| 모듈 | 사용하는 스키마 | 소유 문서 |
|------|----------------|----------|
| `base_node.py` | NodeCapabilityProfileSchema | D3 |
| `base_node.py` | NodeRequestEnvelopeSchema / NodeResponseEnvelopeSchema | D3 |
| `node_registry.py` | NodeRegistry (Registry Slot) | D3 |
| 각 노드의 도구 | ToolCallRegistrySchema | D3 |

### 5.4 infra/ (BrainAdapter, ToolRegistry, PromptCache, RateLimit)

인프라 모듈은 LLM 호출, 도구 관리, 프롬프트 캐시, 속도 제한을 담당한다.

```
infra/
├── __init__.py                     # 인프라 패키지 초기화
│
├── brain/                          # BrainAdapter — LLM 호출 추상화
│   ├── __init__.py
│   ├── adapter.py                  # BrainAdapter 인터페이스 (Ollama/OpenAI/Anthropic)
│   ├── ollama_adapter.py           # Ollama 로컬 LLM 어댑터 [V1]
│   ├── openai_adapter.py           # OpenAI API 어댑터 (GPT-4o mini/GPT-4o)
│   ├── anthropic_adapter.py        # Anthropic API 어댑터 (Claude) [V2+]
│   └── token_counter.py            # tiktoken 기반 토큰 카운터 (cl100k_base LOCK)
│
├── tools/                          # ToolRegistry — 도구 관리
│   ├── __init__.py
│   ├── registry.py                 # ToolRegistry 관리 (D4 ToolRegistry SOT)
│   ├── executor.py                 # 도구 실행기 (Gate 경유 의무)
│   └── discovery.py                # 도구 자동 발견 (MCP 연동)
│
├── prompt/                         # PromptCache — 프롬프트 캐시
│   ├── __init__.py
│   └── cache_manager.py            # PromptCacheManager (D4 스키마)
│
├── rate_limit/                     # RateLimit — API 호출 속도 제한
│   ├── __init__.py
│   └── limiter.py                  # RateLimitConfig 기반 속도 제한기 (D4 스키마)
│
└── backup/                         # Backup — 백업 관리 [V2+]
    ├── __init__.py
    └── manager.py                  # BackupConfig 기반 백업 매니저 (D4 스키마)
```

**D4 스키마 매핑**:
| 모듈 | 사용/생성하는 스키마 | 소유 문서 |
|------|---------------------|----------|
| `brain/adapter.py` | BrainAdapterResponseSchema | D4 |
| `tools/registry.py` | ToolRegistryEntrySchema, ToolRegistry | D4 |
| `tools/executor.py` | InfraInvokeResultSchema | D4 |
| `prompt/cache_manager.py` | PromptCacheManagerSchema | D4 |
| `rate_limit/limiter.py` | RateLimitConfigSchema | D4 |
| `backup/manager.py` | BackupConfigSchema | D4 |

### 5.5 agent/ (LangGraph StateGraph, Pipeline, CircuitBreaker, HITL)

Agent 모듈은 LangGraph StateGraph 기반 워크플로우 파이프라인을 구현한다.

```
agent/
├── __init__.py                     # Agent 패키지 초기화
│
├── graph/                          # LangGraph StateGraph 정의
│   ├── __init__.py
│   ├── state.py                    # AgentState 정의 (StateGraph 상태 타입)
│   ├── builder.py                  # StateGraph 빌더 (노드/엣지 구성)
│   └── nodes.py                    # StateGraph 노드 함수 (Intake→Plan→Execute→Verify→Deliver)
│
├── pipeline/                       # 표준 5단계 파이프라인
│   ├── __init__.py
│   ├── intake.py                   # Stage 1: Intake (입력 수신/의도 분류)
│   ├── plan.py                     # Stage 2: Plan (실행 계획 수립)
│   ├── execute.py                  # Stage 3: Execute (BLUE NODE 실행)
│   ├── verify.py                   # Stage 4: Verify (EVX 검증 체인)
│   └── deliver.py                  # Stage 5: Deliver (결과 전달)
│
├── circuit_breaker.py              # CircuitBreaker — 장애 차단기 (D5 스키마)
├── hitl.py                         # HITL (Human-in-the-Loop) 요청/응답 (D5 스키마)
├── gate_pipeline.py                # GatePipelineMapping — Gate와 파이프라인 매핑 (D5 스키마)
└── marketplace.py                  # AgentMarketplace — 에이전트 마켓플레이스 [V2+] (D5 스키마)
```

**D5 스키마 매핑**:
| 모듈 | 사용/생성하는 스키마 | 소유 문서 |
|------|---------------------|----------|
| `pipeline/deliver.py` | WorkflowOutputEnvelopeSchema | D5 |
| `pipeline/*.py` (실패 시) | FailureReportSchema | D5 |
| `pipeline/verify.py` | VerifyChainEntrySchema | D5 |
| `graph/nodes.py` | WorkflowStageSchema | D5 |
| `circuit_breaker.py` | CircuitBreakerSchema | D5 |
| `gate_pipeline.py` | GatePipelineMappingSchema | D5 |
| `hitl.py` | HITLRequestSchema | D5 |
| `marketplace.py` | AgentMarketplaceSchema | D5 |

### 5.6 storage/ (Memory, VectorStore, GraphRAG, SemanticCache)

저장/메모리 모듈은 다계층 메모리와 벡터/그래프 검색을 관리한다.

```
storage/
├── __init__.py                     # Storage 패키지 초기화
│
├── memory/                         # 메모리 관리 (L0~L3)
│   ├── __init__.py
│   ├── manager.py                  # MemoryManager — 메모리 CRUD 통합 관리
│   ├── l0_session.py               # L0: Session Memory (세션 내 대화)
│   ├── l1_project.py               # L1: Project Memory (프로젝트 지식)
│   ├── l2_longterm.py              # L2: Long-term Knowledge (장기 지식)
│   └── l3_procedural.py            # L3: Procedural Memory (절차 기억)
│
├── vector/                         # 벡터 저장소 (임베딩/검색)
│   ├── __init__.py
│   ├── adapter.py                  # VectorStoreAdapter — 추상 인터페이스 (D6 스키마)
│   ├── chroma_store.py             # Chroma 구현 [V1]
│   ├── qdrant_store.py             # Qdrant 구현 [V2+]
│   └── embedder.py                 # 임베딩 생성기 (BGE-M3 [V1] / text-embedding-3-small [V2+])
│
├── graph/                          # Graph RAG
│   ├── __init__.py
│   ├── config.py                   # GraphRAGConfig (D6 스키마)
│   ├── json_graph.py               # JSON 파일 기반 그래프 [V1]
│   └── neo4j_graph.py              # Neo4j 그래프 [V2+]
│
├── cache/                          # Semantic Cache
│   ├── __init__.py
│   └── semantic_cache.py           # SemanticCache — cosine >= 0.95 캐시 (D6 스키마)
│
├── db/                             # 데이터베이스 관리
│   ├── __init__.py
│   ├── sqlite_manager.py           # SQLite 관리 [V1]
│   ├── postgres_manager.py         # Postgres 관리 [V2+]
│   └── migrations/                 # DB 마이그레이션 (Alembic)
│       ├── env.py                  # Alembic 환경 설정
│       └── versions/               # 마이그레이션 버전 파일
│
├── logging/                        # 로그 저장
│   ├── __init__.py
│   ├── jsonl_logger.py             # JSONL 파일 로거 [V1]
│   └── db_logger.py                # DB 로거 (SQLite [V1] / Postgres [V2+])
│
└── kb/                             # Knowledge Base 임베딩
    ├── __init__.py
    └── embedding_record.py         # KBEmbeddingRecord 관리
```

**D6 스키마 매핑**:
| 모듈 | 사용/생성하는 스키마 | 소유 문서 |
|------|---------------------|----------|
| `memory/manager.py` | MemoryRecordSchema | D6 |
| `memory/manager.py` | SourceQoDSchema | D6 |
| `vector/adapter.py` | VectorStoreAdapterSchema | D6 |
| `graph/config.py` | GraphRAGConfigSchema | D6 |
| `cache/semantic_cache.py` | SemanticCacheSchema | D6 |

### 5.7 safety/ (PolicyCheck, Approval, CostBudget, Guardrails, RBAC, Autonomy)

안전/비용 모듈은 정책 검사, 승인, 비용 관리, 가드레일, 접근 제어, 자율 수준을 담당한다.

```
safety/
├── __init__.py                     # Safety 패키지 초기화
│
├── policy/                         # 정책 검사
│   ├── __init__.py
│   └── checker.py                  # PolicyCheck — deny/restrict/allow 판정 (D7 스키마)
│
├── approval/                       # 승인 관리
│   ├── __init__.py
│   └── manager.py                  # Approval — 승인 요청/응답/만료 관리 (D7 스키마)
│
├── cost/                           # 비용/예산 관리
│   ├── __init__.py
│   ├── budget.py                   # CostBudget — 예산 추적/경고 (D7 스키마)
│   └── downshift.py                # Downshift — 저비용 모델 전환 (80% 경고 / 100% 차단)
│
├── guardrails/                     # 3-Layer Guardrails
│   ├── __init__.py
│   ├── checker.py                  # GuardrailsCheck 통합 검사기 (D7 스키마)
│   ├── nemo_rail.py                # Layer 1: NeMo Guardrails (입력 레일)
│   ├── guardrails_ai.py            # Layer 2: Guardrails AI (출력 검증)
│   └── llamaguard.py               # Layer 3: LlamaGuard (안전 분류) [V2+ 옵션]
│
├── rbac/                           # RBAC 접근 제어
│   ├── __init__.py
│   └── manager.py                  # RBACRole — OWNER/ADMIN/OPERATOR/VIEWER (D7 스키마)
│
└── autonomy/                       # 자율 수준 관리
    ├── __init__.py
    └── level.py                    # AutonomyLevel — L0(수동)~L3(완전자율) (D7 스키마)
```

**D7 스키마 매핑**:
| 모듈 | 사용/생성하는 스키마 | 소유 문서 |
|------|---------------------|----------|
| `policy/checker.py` | PolicyCheckSchema | D7 |
| `approval/manager.py` | ApprovalSchema | D7 |
| `cost/budget.py` | CostBudgetSchema | D7 |
| `cost/downshift.py` | DownshiftSchema | D7 |
| `guardrails/checker.py` | GuardrailsCheckSchema | D7 |
| `rbac/manager.py` | RBACRoleSchema | D7 |
| `autonomy/level.py` | AutonomyLevelSchema | D7 |

### 5.8 schemas/ (contracts.py -- Pydantic v2 모델)

모든 Pydantic v2 모델을 중앙에서 정의하여 일관된 타입 검증을 보장한다.

```
schemas/
├── __init__.py                     # 스키마 패키지 (전체 re-export)
├── contracts.py                    # 중앙 Pydantic v2 모델 정의 (전수 검증 의무)
├── enums.py                        # 공통 Enum 정의 (EventType, FailureCode, FallbackId 등)
├── validators.py                   # 커스텀 Pydantic 검증기
└── registry_types.py               # Registry 타입 정의 (Literal 기반)
```

**contracts.py 스키마-문서 매핑** (D1 §3.3 기반):

| Pydantic 모델 | 소유 문서 | 근거 |
|---------------|----------|------|
| `DecisionSchema` | D2 | 02 §3.2 Decision Kernel |
| `LogEventSchema` | D2 | 02 §6.1 LogEvent Registry |
| `NodeCapabilityProfileSchema` | D3 | 03 NodeRegistry |
| `NodeRequestEnvelopeSchema` | D3 | 03 CORE-NODE 통신 |
| `NodeResponseEnvelopeSchema` | D3 | 03 CORE-NODE 통신 |
| `ToolCallRegistrySchema` | D3 | 03 §6.3 MCP 도구 |
| `MCPBridgeLayerSchema` | D3 | 03 §6.4.1 DEC-017 |
| `ToolRegistryEntrySchema` | D4 | 04 §7.2 ToolRegistry |
| `BrainAdapterResponseSchema` | D4 | 04 BrainAdapter |
| `InfraInvokeResultSchema` | D4 | 04 InfraInvoke |
| `PromptCacheManagerSchema` | D4 | 04 §6.x PromptCache |
| `RateLimitConfigSchema` | D4 | 04 §5.x RateLimit |
| `BackupConfigSchema` | D4 | 04 §9.x Backup |
| `WorkflowOutputEnvelopeSchema` | D5 | 05 §7.2 Workflow 산출물 |
| `FailureReportSchema` | D5 | 05 FailureReport |
| `VerifyChainEntrySchema` | D5 | 05 Verify 체인 |
| `WorkflowStageSchema` | D5 | 05 §7.1 Workflow 단계 |
| `AgentMarketplaceSchema` | D5 | STEP7 R2 |
| `CircuitBreakerSchema` | D5 | 05 §4.x CircuitBreaker |
| `GatePipelineMappingSchema` | D5 | 05 §7.x Gate-Pipeline |
| `HITLRequestSchema` | D5 | STEP7 R2 HITL |
| `MemoryRecordSchema` | D6 | 06 §2.1 Memory |
| `SourceQoDSchema` | D6 | 06 QoD |
| `VectorStoreAdapterSchema` | D6 | 06 §4.x Vector |
| `GraphRAGConfigSchema` | D6 | 06 §4.x DEC-004 |
| `SemanticCacheSchema` | D6 | 06 §4.7 ADD-012 |
| `PolicyCheckSchema` | D7 | 07 §6.4 PolicyCheck |
| `ApprovalSchema` | D7 | 07 §6.2 Approval |
| `CostBudgetSchema` | D7 | 07 §6.3 CostBudget |
| `DownshiftSchema` | D7 | 07 §4.2 Downshift |
| `GuardrailsCheckSchema` | D7 | 07 §1.1 ADD-013~015 |
| `RBACRoleSchema` | D7 | 07 §3.6 MOD-023 |
| `AutonomyLevelSchema` | D7 | 07 §3.2.1 Autonomy |

### 5.9 mcp/ (MCP Bridge, Tool Discovery)

MCP(Model Context Protocol) 브리지는 외부 도구와의 표준 연결을 담당한다.

```
mcp/
├── __init__.py                     # MCP 패키지 초기화
├── bridge.py                       # MCPBridgeLayer — Streamable HTTP 전송 (DEC-017 LOCK)
├── server.py                       # MCP 서버 구현 (도구 노출)
├── client.py                       # MCP 클라이언트 (외부 도구 호출)
├── tool_discovery.py               # MCP 기반 도구 자동 발견
└── protocol.py                     # MCP 프로토콜 메시지 정의
```

**D3 스키마 매핑**:
| 모듈 | 사용/생성하는 스키마 | 소유 문서 |
|------|---------------------|----------|
| `bridge.py` | MCPBridgeLayerSchema | D3 |
| `tool_discovery.py` | ToolCallRegistrySchema | D3 |

---

## 6. 공유 타입 / 인터페이스 (Rust <-> Python <-> React)

### 6.1 공유 타입 디렉토리

```
shared/
├── types/                          # 공유 타입 정의 (Golden Source)
│   ├── schemas.json                # JSON Schema 정의 (D2~D7 스키마 기반)
│   └── enums.json                  # 공유 Enum 정의 (event_type, failure_code 등)
│
└── codegen/                        # 타입 코드 생성 스크립트
    ├── generate_ts.py              # JSON Schema → TypeScript 타입 생성
    ├── generate_rs.py              # JSON Schema → Rust serde 구조체 생성
    └── generate_py.py              # JSON Schema → Pydantic v2 모델 생성 (검증용)
```

### 6.2 타입 동기화 전략

```
[shared/types/schemas.json]  ←── Golden Source (D1~D8 스키마 기반)
         │
         ├──→ [codegen/generate_ts.py]  → src/types/*.ts (React)
         ├──→ [codegen/generate_rs.py]  → src-tauri/src/models/*.rs (Rust)
         └──→ [codegen/generate_py.py]  → backend/vamos_core/schemas/contracts.py (Python, 검증용)
```

> **NOTE**: Python의 `schemas/contracts.py`가 정본(SOT)이며, TypeScript/Rust 타입은 이를 기반으로 생성된다. `shared/types/schemas.json`은 중간 형식으로, contracts.py에서 자동 추출하여 동기화한다.

---

## 7. 테스트 디렉토리 구조

### 7.1 Python 테스트 (pytest)

```
backend/tests/
├── conftest.py                     # 공통 fixture (DB mock, LLM mock 등)
├── pytest.ini                      # pytest 설정
│
├── unit/                           # 단위 테스트
│   ├── test_orange_core/           # ORANGE CORE 테스트
│   │   ├── test_decision_kernel.py
│   │   ├── test_i1_intent.py
│   │   ├── test_i2_evidence.py
│   │   ├── test_i3_memory.py
│   │   ├── test_i4_output.py
│   │   └── test_i5_gate.py
│   ├── test_blue_nodes/            # BLUE NODES 테스트
│   │   ├── test_dev_node.py
│   │   ├── test_research_node.py
│   │   └── test_content_node.py
│   ├── test_infra/                 # 인프라 테스트
│   │   ├── test_brain_adapter.py
│   │   ├── test_tool_registry.py
│   │   └── test_prompt_cache.py
│   ├── test_agent/                 # Agent 테스트
│   │   ├── test_pipeline.py
│   │   ├── test_circuit_breaker.py
│   │   └── test_hitl.py
│   ├── test_storage/               # Storage 테스트
│   │   ├── test_memory_manager.py
│   │   ├── test_vector_store.py
│   │   ├── test_graph_rag.py
│   │   └── test_semantic_cache.py
│   ├── test_safety/                # Safety 테스트
│   │   ├── test_policy_check.py
│   │   ├── test_approval.py
│   │   ├── test_cost_budget.py
│   │   ├── test_guardrails.py
│   │   └── test_rbac.py
│   ├── test_schemas/               # 스키마 검증 테스트
│   │   └── test_contracts.py       # Pydantic v2 모델 직렬화/역직렬화 검증
│   └── test_mcp/                   # MCP 테스트
│       ├── test_bridge.py
│       └── test_tool_discovery.py
│
├── integration/                    # 통합 테스트
│   ├── test_decision_flow.py       # ORANGE CORE → BLUE NODE 전체 흐름
│   ├── test_memory_pipeline.py     # 메모리 저장/검색 파이프라인
│   ├── test_gate_enforcement.py    # Gate 강제 적용 검증
│   └── test_workflow_e2e.py        # 워크플로우 E2E (Intake→Deliver)
│
└── e2e/                            # 엔드투엔드 테스트
    ├── test_full_pipeline.py       # 전체 파이프라인 E2E
    └── test_rust_python_ipc.py     # Rust-Python IPC 통신 검증
```

### 7.2 React 테스트 (vitest)

```
src/
├── __tests__/                      # vitest 테스트 (또는 *.test.tsx 파일 병치)
│   ├── components/                 # 컴포넌트 테스트
│   │   ├── DecisionCard.test.tsx
│   │   ├── CanvasView.test.tsx
│   │   └── AutonomyPanel.test.tsx
│   ├── hooks/                      # 훅 테스트
│   │   ├── useTauriIPC.test.ts
│   │   └── useDecision.test.ts
│   └── stores/                     # 스토어 테스트
│       └── decisionStore.test.ts
```

### 7.3 Rust 테스트 (cargo test)

```
src-tauri/src/tests/                # Rust 단위 테스트
├── command_tests.rs                # IPC 커맨드 테스트
├── bridge_tests.rs                 # Python subprocess 브리지 테스트
└── model_tests.rs                  # Rust 모델 직렬화 테스트
```

### 7.4 통합 테스트

```
tests/                              # 루트 레벨 통합 테스트
├── integration/
│   ├── test_tauri_python.py        # Tauri(Rust) → Python IPC 통합
│   └── test_full_stack.py          # React → Rust → Python 전체 스택
└── fixtures/                       # 공유 테스트 데이터
    ├── sample_decision.json        # DecisionSchema 샘플
    ├── sample_log_event.json       # LogEventSchema 샘플
    └── sample_workflow.json        # WorkflowOutputEnvelope 샘플
```

---

## 8. 설정 / 환경 파일 구조

```
config/
├── default.toml                    # 기본 설정 (모든 환경 공통)
├── development.toml                # 개발 환경 설정
├── production.toml                 # 프로덕션 환경 설정
├── test.toml                       # 테스트 환경 설정
│
├── llm/                            # LLM 설정
│   ├── ollama.toml                 # Ollama 설정 (모델, 엔드포인트) [V1]
│   ├── openai.toml                 # OpenAI API 설정 [V1/V2]
│   └── anthropic.toml              # Anthropic API 설정 [V2+]
│
├── embedding/                      # 임베딩 설정
│   ├── bge_m3.toml                 # BGE-M3 로컬 임베딩 설정 [V1]
│   └── openai_embedding.toml       # OpenAI 임베딩 설정 [V2+]
│
├── storage/                        # 저장소 설정
│   ├── sqlite.toml                 # SQLite 설정 [V1]
│   ├── chroma.toml                 # Chroma 벡터 DB 설정 [V1]
│   ├── postgres.toml               # Postgres 설정 [V2+]
│   ├── qdrant.toml                 # Qdrant 벡터 DB 설정 [V2+]
│   └── neo4j.toml                  # Neo4j 그래프 DB 설정 [V2+]
│
├── safety/                         # 안전/가드레일 설정
│   ├── guardrails.toml             # 3-Layer Guardrails 설정
│   ├── rbac.toml                   # RBAC 역할/권한 설정
│   ├── autonomy.toml               # 자율 수준 설정 (L0~L3)
│   └── cost_budget.toml            # 비용 예산 설정 (V1: 40K/mo LOCK)
│
├── mcp/                            # MCP 설정
│   └── mcp_servers.toml            # MCP 서버 목록 (Streamable HTTP)
│
└── nemo/                           # NeMo Guardrails 레일 정의
    ├── config.yml                  # NeMo 설정
    └── rails/                      # 레일 정의 파일
        ├── input.co                # 입력 레일
        └── output.co               # 출력 레일
```

### 8.1 환경 변수 (.env)

```
# .env.example — 커밋되지 않는 환경 변수 템플릿
VAMOS_ENV=development                    # 환경 (development/production/test)
VAMOS_LOG_LEVEL=debug                    # 로그 레벨

# LLM API 키
OPENAI_API_KEY=sk-...                    # OpenAI API 키
ANTHROPIC_API_KEY=sk-ant-...             # Anthropic API 키 [V2+]

# Ollama
OLLAMA_HOST=http://localhost:11434       # Ollama 엔드포인트 [V1]

# 저장소
SQLITE_DB_PATH=./data/vamos.db          # SQLite 경로 [V1]
CHROMA_PERSIST_DIR=./data/chroma        # Chroma 데이터 경로 [V1]

# 비용 상한
VAMOS_COST_LIMIT_USD=30                  # V1 월 비용 상한 ($30 = 40K KRW)

# MCP
MCP_SERVER_URL=http://localhost:8080     # MCP 서버 URL
```

---

## 9. 문서 이력

| 버전 | 일자 | 변경 내용 |
|------|------|----------|
| 1.0.0 | 2026-02-22 | Phase B2 초기 생성 — 프로젝트 디렉토리/모듈 구조 설계. A1 COMBO-V1 기반. D1~D8 스키마 → Python 모듈 매핑 명시. Monorepo LOCK. |

---

<\!-- END OF DOCUMENT -->
