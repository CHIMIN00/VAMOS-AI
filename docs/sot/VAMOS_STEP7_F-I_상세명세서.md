# VAMOS STEP7 카테고리 F-I 통합 상세명세서

> **문서 버전**: 1.0
> **생성일**: 2026-02-23
> **소스**: STEP7-F(96건), STEP7-G(88건), STEP7-H(78건), STEP7-I(106건) = **총 368건**
> **목적**: VAMOS AI 시스템의 인프라/배포/MLOps, 벤치마크/평가/품질보증, 비즈니스모델/시장전략, AI Investing 보강에 대한 통합 상세 명세

---

## 문서 구성

| 카테고리 | 항목 수 | 범위 |
|---------|---------|------|
| **F. 인프라/배포/MLOps** | 96건 (S7F-001~096) | 모델 서빙, V1/V2/V3 인프라, 컨테이너, CI/CD, 모니터링, 비용, MLOps, 네트워크, 백업, 성능 |
| **G. 벤치마크/평가/품질보증** | 88건 (S7G-001~088) | 표준 벤치마크, 한국어 특화, 코딩, Agent, RAG, 안전성, UX, VAMOS 고유, 자동 평가, QA |
| **H. 비즈니스모델/시장전략** | 78건 (S7H-001~078) | 가격 분석, 가격 전략, 수익 모델, 타겟 페르소나, 시장 규모, 경쟁, GTM, 성장, 리스크, 재무 |
| **I. AI Investing 보강** | 106건 (S7I-001~106) | AI 투자 플랫폼, LLM 분석, 대안 데이터, 한국 시장, 포트폴리오, 리스크, 백테스팅, 실시간, 크립토, Agent 워크플로우, 규제, GAP 해결 |

---

## 우선도 총괄

| 우선도 | F | G | H | I | 합계 |
|--------|---|---|---|---|------|
| CRITICAL | 13 | 11 | 11 | 22 | **57** |
| HIGH | 48 | 47 | 41 | 56 | **192** |
| MED | 31 | 30 | 26 | 28 | **115** |
| LOW | 4 | 0 | 0 | 0 | **4** |
| **합계** | **96** | **88** | **78** | **106** | **368** |

---

# F. 인프라 / 배포 / MLOps (96건)

## F-Part 1: 모델 서빙 엔진 비교 (10건)

### F-Part 1 전수비교표

| 엔진 | 유형 | 라이선스 | GPU 필요 | 양자화 | 스트리밍 | 배치 | VAMOS 적합 |
|------|------|---------|---------|--------|---------|------|-----------|
| vLLM | 서버 | Apache 2 | 필수 | GPTQ/AWQ | O | Continuous | V3 |
| Ollama | 로컬 | MIT | CPU/GPU | GGUF(Q4~Q8) | O | X | V1 핵심 |
| llama.cpp | 라이브러리 | MIT | CPU/GPU | GGUF | O | X | V1 백엔드 |
| LocalAI | 서버 | MIT | CPU/GPU | GGUF/GPTQ | O | X | V1 대안 |
| TensorRT-LLM | 서버 | Apache 2 | NVIDIA 필수 | INT4/INT8/FP8 | O | In-flight | V3 |
| TGI (HF) | 서버 | Apache 2 | 필수 | GPTQ/AWQ | O | Continuous | V2 |
| SGLang | 서버 | Apache 2 | 필수 | 다수 | O | RadixAttention | V3 참조 |
| Triton | 서버 | BSD | NVIDIA 필수 | 다수 | O | Dynamic | V3 |
| MLC LLM | 크로스 | Apache 2 | CPU/GPU/NPU | 다수 | O | X | V3 모바일 |

---

### S7F-001 | CRITICAL | V1 | Ollama 기반 로컬 LLM 서빙

- **모듈 연동**: I(Infra Core) - 로컬 런타임 엔진
- **구현 방식**: Ollama를 V1 로컬 LLM 서빙 엔진으로 채택. 1-click installer로 macOS/Windows/Linux 지원. GGUF 양자화 모델(4-bit~8-bit) 지원, REST API 호환(OpenAI API 포맷), 메모리 효율적(7B 모델 기준 ~4GB RAM)
- **기술 스택**: Ollama, GGUF 양자화, REST API, Go 런타임
- **V1 범위**: `ollama pull llama3.2:3b`(2GB, 빠른 응답), `ollama pull qwen2.5:7b`(4.7GB, 범용), `ollama pull deepseek-r1:8b`(4.9GB, 추론 특화). `http://localhost:11434/api/chat` 엔드포인트로 호출
- **비용**: $0 (하드웨어 비용만). 제약: GPU 없으면 속도 제한, 70B+ 모델 어려움

### S7F-002 | CRITICAL | V1 | API 기반 클라우드 LLM 호출

- **모듈 연동**: E(External API), S(Service Layer)
- **구현 방식**: 복잡한 작업은 클라우드 LLM API로 처리하는 하이브리드 구조. 라우팅 규칙: 간단한 질문/채팅 → Ollama 로컬($0), 코딩/분석 → Claude Sonnet 4.6 API, 빠른 분류/요약 → GPT-4o-mini 또는 Gemini Flash, 깊은 추론 → Claude Opus 4.6 또는 DeepSeek R1
> **[PART1 ST-06]** 모델명 업데이트: Claude 3.5 Sonnet → Claude Sonnet 4.6, Claude 3.5 Haiku → Claude Haiku 4.5. 최신 모델 패밀리 반영.
- **기술 스택**: Anthropic SDK, OpenAI SDK, Google AI SDK, Groq SDK
- **API 프로바이더 비교**: Claude Sonnet 4.6, Claude Haiku 4.5, GPT-4o($2.50/$10), GPT-4o-mini($0.15/$0.60), Gemini 2.0 Flash($0.10/$0.40), DeepSeek-V3($0.27/$1.10), Groq Llama 3.3 70B($0.59/$0.79)
- **V1 범위**: 핵심 API 연동 + 라우팅 기본 규칙

### S7F-003 | CRITICAL | V1 | 모델 라우터 (Model Router)

- **모듈 연동**: A(Agent Layer), I(Infra Core)
- **구현 방식**: 작업 유형/복잡도/비용에 따라 최적 모델 자동 선택. User Request → Complexity Classifier → Task Type Detector → Routing Rules Engine → Cost Gate 확인 → 실행
- **기술 스택**: 커스텀 분류기(V1 규칙 기반 → V2 ML 분류기 → V3 강화학습 최적화)
- **라우팅 규칙**: complexity=LOW+cost_sensitive → 로컬 Ollama(Llama 3.2 3B), complexity=MED+type=coding → Claude Sonnet 4.6, complexity=HIGH+type=reasoning → Claude Opus 4.6(with thinking), type=search → Gemini+Search Grounding, type=quick_classify → GPT-4o-mini
- **비용 절감 목표**: 단일 모델 대비 60-70% 비용 절감

### S7F-004 | HIGH | V1 | 모델 Fallback 체인

- **모듈 연동**: I(Infra Core), S(Service Layer)
- **구현 방식**: 특정 모델/API 장애 시 자동으로 대체 모델 전환. 코딩 작업 예시: 1st Claude Sonnet 4.6(기본) → 2nd GPT-4o → 3rd DeepSeek V3 → 4th Ollama qwen2.5:7b. Fallback 조건: API 타임아웃(30초), HTTP 5xx, Rate limit 초과, 비용 상한 도달
- **기술 스택**: 커스텀 Fallback Manager, Circuit Breaker 패턴
- **V1 범위**: 자동 전환 시 사용자 알림 포함

### S7F-005 | HIGH | V1 | 스트리밍 응답 (SSE 기반)

- **모듈 연동**: S(Service Layer), A(Agent Layer)
- **구현 방식**: 모든 LLM 응답을 Server-Sent Events 스트리밍으로 출력. Unified streaming interface로 Anthropic/OpenAI/Ollama 통합 스트리밍 제공
- **기술 스택**: SSE, TypeScript async generators, anthropic SDK stream, openai SDK stream, ollama SDK stream
- **V1 범위**: 텍스트 스트리밍. V2: 구조화된 스트리밍(코드블록, 표 등 점진적 렌더링)

### S7F-006 | HIGH | V1 | Prompt Caching 활용

- **모듈 연동**: I(Infra Core), E(External API)
- **구현 방식**: 반복 사용 시스템 프롬프트/문서 캐싱으로 비용 절감. Cacheable Items: System Prompt(~2000 tok), Tool Definitions(~5000 tok), User Memory Summary(~1000 tok), Frequently Referenced Documents(~10000 tok)
- **기술 스택**: Claude Prompt Caching(90% 할인, 5분 TTL), OpenAI Automatic Caching(50% 할인), Gemini Context Caching(75% 할인, 최소 32K tokens)
- **V1 범위**: 월 API 비용의 30-50% 절감 예상

### S7F-007 | HIGH | V1 | 양자화 모델 관리

- **모듈 연동**: I(Infra Core)
- **구현 방식**: 로컬 실행 모델의 양자화 수준 관리. Q4_K_M(60% 크기 감소, 미미한 품질 손실) 추천. 사용 가능 RAM/VRAM 기반 최적 양자화 자동 결정
- **기술 스택**: GGUF 포맷, Ollama, llama.cpp
- **양자화 비교**: Q2_K(75% 감소, 심함) → Q4_K_M(60%, 미미, **V1 추천**) → Q5_K_M(50%, 거의 없음) → Q6_K(40%, 없음) → Q8_0(25%, 없음) → FP16(0%, 기준)

### S7F-008 | HIGH | V2 | Model Gateway (통합 모델 게이트웨이)

- **모듈 연동**: I(Infra Core), E(External API)
- **구현 방식**: 모든 LLM 호출을 단일 게이트웨이로 통합. Client → Model Gateway → Provider Selection/Authentication/Rate Limiting/Caching/Logging/Cost Tracking/Fallback/Load Balancing → Response
- **기술 스택**: LiteLLM(무료, Python) - OpenAI 포맷으로 100+ 모델 통합 호출. `from litellm import completion`으로 동일 API로 모든 프로바이더 호출
- **V2 범위**: LiteLLM Proxy 셀프호스팅 무료

### S7F-009 | MED | V2 | Batch Processing (배치 처리)

- **모듈 연동**: I(Infra Core), S(Service Layer)
- **구현 방식**: 대량 문서 처리/반복 분석 배치 효율 처리. OpenAI Batch API(50% 할인, 24시간 내 완료), Claude Batch API(Message Batches, 50% 할인), 로컬 큐(BullMQ/Redis + Worker Pool)
- **기술 스택**: OpenAI Batch API, Claude Message Batches, BullMQ, Redis
- **용도**: 문서 일괄 분석, 포트폴리오 전체 리밸런싱 검토, 지식 베이스 일괄 업데이트

### S7F-010 | MED | V2 | A/B 모델 테스트

- **모듈 연동**: I(Infra Core), A(Agent Layer)
- **구현 방식**: 새 모델 도입 시 기존 모델과 A/B 비교. 동일 요청을 두 모델에 전송 → 품질/속도/비용 비교. ELO 레이팅 시스템(Chatbot Arena 유사)
- **기술 스택**: 커스텀 A/B 프레임워크, ELO 레이팅
- **자동 평가 기준**: 정확성, 응답 시간, 토큰 효율, 사용자 선호. 통계적 유의성 달성 시 자동 전환 권고

---

## F-Part 2: V1 로컬 인프라 설계 (10건)

### V1 아키텍처 개요

User Desktop/Laptop 위에 Tauri App(React/Svelte 프론트엔드) + Ollama(로컬 LLM REST API) + SQLite/SQLCipher + Rust Backend(Core Logic + Node.js sidecar) + Chroma(Vector DB In-Process) + NetworkX(Graph + JSON) + External API Calls(Claude/OpenAI/Google/Search API). Storage: ~/vamos/(~500MB~2GB). Cost: API만(<=10,000원/월). Security: All data local, PII masked for API.

### S7F-011 | CRITICAL | V1 | Tauri 데스크톱 앱

- **모듈 연동**: S(Service Layer), I(Infra Core)
- **구현 방식**: Tauri(Rust + WebView) 기반 데스크톱 앱. Electron 대비 10x 작은 번들(~5MB vs ~150MB), 메모리 50% 이하(~50MB vs ~200MB+), Rust 백엔드로 보안/성능 우수, macOS/Windows/Linux 지원
- **기술 스택**: Frontend: React 18.3 + TypeScript + TailwindCSS + shadcn/ui. Backend: Rust(Tauri) + sidecar Node.js. Build: Vite + Tauri CLI
> **[PART1 ST-03]** 정본: React 18.3 (LOCK, V1-014/PHASE_B3). React 19는 V2+ 평가 대상.
- **비용**: $0 (전부 오픈소스)

### S7F-012 | CRITICAL | V1 | Node.js 사이드카

> ⚠️ **PLAN-3.0 정본 오버라이드**: Python 3.11+ backend (LangGraph Python). 본 항목의 Node.js 아키텍처는 대안 참조로 강등. 정본 통신 계층: React ↔ Tauri IPC ↔ Rust ↔ JSON-RPC ↔ Python.

- **모듈 연동**: A(Agent Layer), I(Infra Core)
- **구현 방식**: Tauri Rust 코어와 함께 Node.js 프로세스를 사이드카로 실행. LLM API 호출(OpenAI/Anthropic SDK), MCP Tool 실행, Agent 오케스트레이션(LangGraph.js), RAG 파이프라인 담당
- **기술 스택**: Node.js 22 LTS, LangGraph.js, @anthropic-ai/sdk, chromadb, IPC: Tauri <-> Node.js(JSON-RPC over stdio)
- **메모리**: Node.js ~100MB + Ollama ~4GB(7B 모델)

### S7F-013 | CRITICAL | V1 | 로컬 저장소 구성 (~/vamos/)

- **모듈 연동**: S(Storage Layer), I(Infra Core)
- **구현 방식**: 모든 사용자 데이터를 로컬 디렉토리에 구조화 저장
> ⚠️ **정본 오버라이드**: PHASE_B2 monorepo 구조가 정본. 아래 `~/vamos/` 경로는 참조용.
- **디렉토리 구조**: `~/vamos/config/`(settings.yaml, constitution.yaml, models.yaml, tools.yaml), `~/vamos/data/`(memory.db SQLCipher, chroma/, knowledge_graph.json, cache/), `~/vamos/logs/`(app.log, security.log, cost.log), `~/vamos/backups/`(YYYY-MM-DD/), `~/vamos/exports/`(*.json) <!-- ⚠️ 정본: .toml (PHASE_B4 LOCK). config.v1.toml 사용 -->
- **총 용량**: ~500MB(기본) ~ 2GB(활발 사용)

### S7F-014 | CRITICAL | V1 | 시스템 요구사항

- **최소 사양**: OS Win10/macOS12/Ubuntu22, CPU 4코어, RAM 8GB, 디스크 10GB SSD, GPU 없어도 됨, 네트워크 1Mbps (API 위주, 로컬 3B 모델만)
- **권장 사양**: OS Win11/macOS14, CPU 8코어, RAM 16GB, 디스크 50GB SSD, GPU 8GB VRAM, 네트워크 10Mbps (로컬 7B + API 혼합)
- **최적 사양**: CPU 12코어+, RAM 32GB, 디스크 100GB NVMe, GPU 16GB+ VRAM, 네트워크 100Mbps (로컬 13B+ 원활)

### S7F-015 | HIGH | V1 | 자동 설치 스크립트

- **모듈 연동**: I(Infra Core)
- **구현 방식**: 원클릭 설치 — Tauri 앱 설치(MSI/DMG/DEB) → Ollama 자동 설치(미설치 시) → 기본 모델 다운로드(Llama 3.2 3B) → 디렉토리 구조 생성 → 초기 설정 마법사 → API Key 입력(선택)
- **플랫폼별**: Windows(MSI + PowerShell), macOS(DMG + Homebrew), Linux(AppImage + apt/dnf)

### S7F-016 | HIGH | V1 | 자동 업데이트

- **모듈 연동**: I(Infra Core)
- **구현 방식**: Tauri Updater 내장 자동 업데이트(코드 서명). 채널: Stable/Beta/Nightly. 업데이트 전 설정/데이터 자동 백업, 실패 시 이전 버전 자동 롤백, 사용자 승인 후 업데이트

### S7F-017 | HIGH | V1 | 프로세스 관리

- **모듈 연동**: I(Infra Core)
- **구현 방식**: Start → Check Ollama → Start Node.js Sidecar → Initialize DB → Ready. Health Check(30초 간격): Ollama 응답, Node.js 상태, DB 접근, 디스크 공간. Graceful Shutdown: 진행 중 작업 완료 대기(최대 30초) → 캐시 flush → DB 해제 → 프로세스 종료

### S7F-018 | HIGH | V1 | 오프라인 모드

- **모듈 연동**: I(Infra Core), S(Service Layer)
- **구현 방식**: 오프라인 가능 — 로컬 LLM 대화(Ollama), 메모리 검색(Chroma+SQLite), 저장된 문서 분석, 이전 대화 검색. 오프라인 불가 — 클라우드 LLM API, 웹 검색, 외부 Tool. 네트워크 복구 시 자동 전환 + 큐잉 작업 실행

### S7F-019 | MED | V1 | 시스템 트레이

- **모듈 연동**: S(Service Layer)
- **구현 방식**: 트레이 아이콘(상태 표시), 글로벌 핫키(Ctrl+Shift+V) → 미니 입력창, 상태 정보(현재 작업, 비용, 메모리), 메뉴(설정, 대화, 일시정지, 종료)

### S7F-020 | MED | V1 | 개발 환경 설정

- **모듈 연동**: I(Infra Core)
- **구현 방식**: Prerequisites: Node.js 22 LTS, Rust(stable), Ollama, Git. Setup: `git clone` → `npm install` → `cargo tauri dev`. 개발 도구: VSCode + Rust Analyzer + Tauri Extension + ESLint + Prettier

---

## F-Part 3: V2 서버 인프라 설계 (10건)

### V2 아키텍처 개요

Web App(Next.js PWA) → API Gateway(Nginx/Traefik + Rate Limit + Auth) → Application Server(Node.js: Agent Orchestrator LangGraph + Model Router LiteLLM + MCP Tool Manager + WebSocket Socket.io) → PostgreSQL(Main DB) + Qdrant(Vector) + Neo4j(Graph) + Redis(Cache) + MinIO/S3(Files) + Loki(Logs). Cost: VPS 20,000원 + DB 10,000원 + API 10,000원 = ~40,000원/월.

### S7F-021 | HIGH | V2 | VPS 선정

- **비교**: Hetzner(4vCPU/8GB/80GB, ~EUR7, 독일/미국, **최저가**), Vultr(4vCPU/8GB/100GB, $48, **서울 있음**), DigitalOcean($48, 싱가포르), AWS Lightsail($48, 서울), Oracle Cloud(4vCPU/24GB/200GB, **$0 Free tier**, 서울), Fly.io(~$32, 도쿄)
- **추천**: Hetzner(가성비) 또는 Oracle Cloud Free(비용 $0). GPU 서버: RunPod/Vast.ai(~$0.20/hr A10G)

### S7F-022 | HIGH | V2 | Next.js 웹 앱

- **기술 스택**: Next.js 15(App Router, RSC), TailwindCSS + shadcn/ui(V1과 컴포넌트 공유), Auth.js(NextAuth v5) + OAuth2, Zustand(클라이언트) + React Query(서버 상태), Socket.io/SSE, next-pwa(오프라인 캐싱), 배포: Vercel 프리 티어 또는 Self-hosted

### S7F-023 | HIGH | V2 | PostgreSQL 메인 DB

- **구현 방식**: V2에서 SQLite → PostgreSQL 마이그레이션. ORM: Drizzle ORM(타입 안전, 경량), 마이그레이션: drizzle-kit migrate, 호스팅: Supabase Free(500MB) 또는 Neon Free(512MB)

### S7F-024 | HIGH | V2 | Qdrant 프로덕션 벡터 DB

- **구현 방식**: V2에서 Chroma → Qdrant. Rust 기반 고성능(Chroma 대비 3-5x), 필터링+벡터 검색 동시(Payload Index), 분산 지원(V3), gRPC+REST API. Docker: `qdrant/qdrant:latest`. 비용: 셀프호스팅 무료 / Qdrant Cloud Free(1GB)

### S7F-025 | HIGH | V2 | Redis 캐시

- **용도**: Session Store(JWT 블랙리스트), Cache(LLM 시맨틱 캐시 TTL 1시간), Rate Limiter(Token Bucket), Queue(BullMQ), Pub/Sub(실시간 알림). 호스팅: Upstash Redis Free(10K req/day)

### S7F-026 | HIGH | V2 | Neo4j 그래프 DB

- **구현 방식**: V2에서 NetworkX+JSON → Neo4j. 대규모 그래프(100만+ 노드), Cypher 쿼리, 시각화 도구 내장, APOC 라이브러리. 호스팅: Neo4j AuraDB Free(50K nodes, 175K relationships)

### S7F-027 | MED | V2 | 메시지 큐

- **구현 방식**: BullMQ(Redis 기반, Node.js 네이티브). 작업 유형: 문서 인덱싱, 배치 분석, 리포트 생성, 메모리 정리. 우선순위 큐: CRITICAL > HIGH > NORMAL > LOW. 재시도 3회 + 지수 백오프 + Dead Letter Queue

### S7F-028 | MED | V2 | 파일 저장소

- **구현 방식**: V1 로컬 파일시스템 → V2 MinIO(S3 호환, 셀프호스팅) 또는 Cloudflare R2(10GB Free). 파일 유형: PDF/TXT/MD/DOCX/CSV/JSON/이미지. 최대: 50MB/파일, 1GB/사용자. 바이러스 스캔: ClamAV(무료)

### S7F-029 | MED | V2 | WebSocket 서버

- **구현 방식**: Socket.io(Node.js, 폴백 지원). 이벤트: `llm_stream`(LLM 스트리밍), `agent_status`(Agent 상태), `cost_update`(비용 실시간), `notification`(알림). JWT 기반 인증, 30초 하트비트

### S7F-030 | MED | V2 | 환경 분리 (Dev/Staging/Prod)

- **구현 방식**: dev(로컬, SQLite, Chroma, 모의 API), staging(프로덕션 미러, 축소 규모), prod(실제 운영 전체 스택). 환경별 .env 파일 분리, API Key 별도 관리

---

## F-Part 4: V3 엔터프라이즈 인프라 (6건)

### S7F-031 | MED | V3 | Kubernetes 배포

- **구현 방식**: K8s 기반 확장성 — Agent별 Pod, HPA(자동 스케일링), 서비스 메시(Istio). 비용: EKS/GKE ~$70/mo + 노드 비용

### S7F-032 | MED | V3 | GPU 클러스터

- **구현 방식**: vLLM/TensorRT-LLM으로 자체 모델 서빙. A10G/L4 GPU(RunPod/Lambda), vLLM continuous batching. 비용: A10G ~$0.20/hr = ~$144/mo(24/7)

### S7F-033 | MED | V3 | 멀티 리전 배포

- **구현 방식**: 아시아/미주/유럽 각 1리전, GeoDNS 라우팅으로 레이턴시 최소화

### S7F-034 | MED | V3 | 데이터 파이프라인

- **구현 방식**: Apache Airflow/Dagster 기반 ETL. 용도: 대량 문서 인덱싱, 모델 평가, 리포트 생성

### S7F-035 | LOW | V3 | 멀티 테넌시

- **구현 방식**: 기업 고객별 완전 데이터 격리. 테넌트별 DB 스키마 분리 또는 별도 DB 인스턴스

### S7F-036 | LOW | V3 | SLA 관리

- **구현 방식**: 99.9% 가용성 목표. 이중화, 자동 장애복구, 상태 페이지(Upptime 무료)

---

## F-Part 5: 컨테이너/오케스트레이션 (8건)

### S7F-037 | HIGH | V2 | Docker Compose

- **구현 방식**: 전체 V2 스택을 Docker Compose로 배포. 서비스: app(Node.js:3000), postgres(16-alpine), qdrant(latest), redis(7-alpine), neo4j(5-community), nginx(alpine:80/443). 원커맨드: `docker compose up -d`

### S7F-038 | HIGH | V2 | Dockerfile 최적화

- **구현 방식**: 멀티스테이지 빌드 — Build stage(node:22-alpine, npm ci, npm run build) → Production stage(node:22-alpine, dist+node_modules만 복사, USER node). 목표: 최종 이미지 <200MB

### S7F-039 | HIGH | V2 | 헬스체크

- **구현 방식**: `/health` 엔드포인트 + Docker HEALTHCHECK + 자동 재시작

### S7F-040 | HIGH | V2 | 시크릿 관리

- **구현 방식**: V2 Docker Secrets/.env 암호화 → V3 HashiCorp Vault

### S7F-041 | MED | V2 | 볼륨 관리

- **구현 방식**: Named Volumes + 자동 백업 스크립트로 데이터 영속성 보장

### S7F-042 | MED | V2 | 네트워크 격리

- **구현 방식**: Docker network로 frontend/backend/db 네트워크 분리

### S7F-043 | MED | V2 | 리소스 제한

- **구현 방식**: 각 컨테이너 `deploy.resources.limits`(CPU/Memory) 설정

### S7F-044 | MED | V3 | Helm Charts

- **구현 방식**: Kubernetes 배포용 Helm Chart. V3 전체 VAMOS 스택 Helm 관리

---

## F-Part 6: CI/CD 파이프라인 (8건)

### S7F-045 | CRITICAL | V1 | GitHub Actions CI

- **구현 방식**: PR마다 자동 빌드/테스트/린트. Jobs: lint(npm ci → npm run lint → npm run typecheck), test(npm test --coverage → codecov), security(npm audit --audit-level=high → semgrep). 비용: GitHub Actions Free(2000분/월 private)

### S7F-046 | CRITICAL | V2 | CD 파이프라인

- **구현 방식**: main merge → Build Docker Image → Push Registry → Deploy Staging → Smoke Test → Manual Approval → Deploy Production → Health Check. Rollback: 실패 시 이전 이미지 자동 롤백. 도구: GitHub Actions + Docker Hub/GHCR

### S7F-047 | HIGH | V1 | 코드 품질 게이트

- **구현 방식**: PR 머지 전 필수 검사 — ESLint+Prettier, TypeScript strict mode, 테스트 커버리지 >=80%, Semgrep(SAST), Bundle Size 확인, Lighthouse CI(웹 성능)

### S7F-048 | HIGH | V1 | 테스트 자동화

- **구현 방식**: Test Pyramid — Unit(Vitest, 70%) + Integration(Vitest+MSW, 25%) + E2E(Playwright, 5%). 추가: Prompt 테스트(promptfoo), Security 테스트(garak), Performance 테스트(k6). 커버리지 목표: Unit 80% / Integration 60% / E2E 핵심 플로우

### S7F-049 | HIGH | V2 | 릴리즈 관리

- **구현 방식**: SemVer(MAJOR.MINOR.PATCH), Conventional Commits(feat/fix/docs/chore), 자동 CHANGELOG(semantic-release/changesets), GitHub Release 바이너리 자동 첨부

### S7F-050 | HIGH | V1 | 의존성 관리

- **구현 방식**: Dependabot 주간 업데이트 PR, npm audit 보안 취약점 스캔, Lockfile 무결성 검증, 업데이트 후 전체 테스트

### S7F-051 | MED | V1 | 브랜치 전략 (Git Flow)

- **구현 방식**: main(프로덕션) → develop(개발 통합) → feature/fix/chore 브랜치. PR 규칙: develop → main은 release 브랜치만

### S7F-052 | MED | V2 | Feature Flag

- **구현 방식**: V2 설정 파일 기반(config/features.yaml) → V3 Unleash(오픈소스)/LaunchDarkly. 용도: 베타 기능 테스트, A/B 테스트, 긴급 비활성화 <!-- ⚠️ 정본: .toml (PHASE_B4 LOCK) -->

---

## F-Part 7: 모니터링/옵저버빌리티 (8건)

### S7F-053 | HIGH | V1 | 구조화된 로깅

- **구현 방식**: Pino(Node.js 최고속 로거) + JSON 포맷. 필드: level, time, msg, request_id, model, tokens_in, tokens_out, cost_usd, latency_ms

### S7F-054 | HIGH | V1 | LLM 메트릭 수집

- **메트릭**: 요청당 토큰 수(입력/출력), 요청당 비용(USD/KRW), 응답 지연(TTFT/TPS), 모델별 사용 분포, 캐시 적중률, 에러율/재시도율, 사용자 만족도(피드백)

### S7F-055 | HIGH | V2 | Grafana 대시보드

- **구현 방식**: 패널: 실시간 API 비용, 모델별 사용량, 응답 시간 분포(P50/P95/P99), 에러율 추이, Agent 타임라인, 메모리/CPU. 비용: Grafana Cloud Free(10K metrics, 50GB logs)

### S7F-056 | HIGH | V2 | Langfuse 통합

- **구현 방식**: LLM 특화 옵저버빌리티 — 프롬프트 버전 관리+A/B, 멀티턴 대화 트레이스, 기능별/사용자별 비용 분석, 자동+수동 품질 평가, 테스트 데이터셋 관리. 비용: Langfuse Cloud Free(50K observations/mo)

### S7F-057 | HIGH | V2 | 알림 규칙

- **알림 조건**: API 에러율 >5%(WARNING→Slack), 응답시간 P95>10s(WARNING), 일일 비용>예산 80%(WARNING→앱내+이메일), >100%(CRITICAL→차단), API 전면 장애(CRITICAL→모든 채널), 보안 이벤트(CRITICAL→모든 채널)

### S7F-058 | MED | V2 | OpenTelemetry 분산 트레이싱

- **구현 방식**: OpenTelemetry SDK + Jaeger(무료)/Tempo(Grafana). 추적: 사용자 입력 → 모델 라우팅 → API 호출 → Tool 실행 → 응답

### S7F-059 | MED | V2 | 상태 페이지

- **구현 방식**: Upptime(GitHub Pages 기반, 무료)/Instatus Free. 표시: 서비스 상태, 인시던트 이력, 예정 유지보수

### S7F-060 | MED | V2 | 로그 보존 정책

- **정책**: 앱 로그 30일 / 보안 로그 1년 / 비용 로그 1년 / 디버그 로그 7일

---

## F-Part 8: 비용 최적화 (8건)

### 버전별 월간 비용 목표

| 항목 | V1 | V2 | V3 |
|------|-----|-----|-----|
| 인프라 | $0(로컬) | ~$20 | ~$100 |
| LLM API | <=$8 | <=$25 | <=$100 |
| DB | $0(로컬) | ~$5 | ~$30 |
| 모니터링 | $0 | $0(Free) | ~$20 |
| **합계** | **<=$8/mo** | **<=$50/mo** | **<=$250/mo** |

### S7F-061 | CRITICAL | V1 | 스마트 모델 라우팅 비용 최적화

- **전략**: 간단한 질문(40%) → 로컬 Ollama $0, 분류/태깅(15%) → GPT-4o-mini $0.15/1M, 요약/검색(20%) → Gemini Flash $0.10/1M, 코딩/분석(15%) → Claude Sonnet $3/1M, 깊은 추론(10%) → Claude Opus $15/1M. 월 1000 요청: 단일 모델 ~$15 → 스마트 라우팅 ~$5(67% 절감)

### S7F-062 | CRITICAL | V1 | 토큰 최적화

- **전략**: 시스템 프롬프트 압축(2000→1200 tok), 컨텍스트 윈도우 관리(최근 N턴+요약), 메모리 관련 요약만 주입, Tool 결과 상세 제거, max_tokens 적절 설정. 예상 절감: 30-40% 토큰 절약

### S7F-063 | HIGH | V1 | 비용 대시보드

- **표시**: 금일/금주/금월 누적 비용, 모델별 분포(파이 차트), 기능별 분포, 요청별 이력, 예산 대비 진행률(프로그레스 바), 비용 절감 팁 자동 제안

### S7F-064 | HIGH | V1 | 예산 하드캡

- **구현**: daily/weekly/monthly/per_request 한도 설정, alert_thresholds(80%/90%/100%), on_limit_reached: "fallback_to_local" 또는 "block"(사용자 선택)

### S7F-065 | HIGH | V1 | Free Tier 최대 활용

- **LLM**: Gemini 무료(15 RPM), Groq 무료(30 RPM), Together.ai $25 크레딧, Mistral 무료
- **DB**: Supabase 500MB, Neo4j Aura 50K nodes, Qdrant Cloud 1GB, Upstash Redis 10K/day
- **Infra**: Oracle Cloud Always Free(4 OCPU/24GB!), Vercel Free, GitHub Actions 2000분, Cloudflare CDN+R2 10GB
- **Monitor**: Grafana Cloud 10K metrics, Langfuse 50K obs, Sentry 5K errors

### S7F-066 | HIGH | V2 | 시맨틱 캐싱

- **구현 방식**: User Query → Embed → Search cache(similarity>=0.95) → cache_hit: return cached($0) / miss: call LLM + store. 적중률 예상 10-20%, 월 10-20% 비용 절감

### S7F-067 | MED | V2 | Spot/Preemptible 인스턴스

- **구현 방식**: 개발/테스트/배치에 Spot 활용. 정가 대비 70-90% 할인

### S7F-068 | MED | V2 | 비용 예측

- **구현 방식**: 이동 평균+추세선으로 월말 예상 비용 산출. 알림: "현재 추세로 월 15,000원 예상(예산: 10,000원)" → 절감 제안

---

## F-Part 9: MLOps/LLMOps (10건)

### S7F-069 | HIGH | V1 | 프롬프트 버전 관리

- **구현 방식**: prompts/system/(core_v1.x.yaml), prompts/agents/, prompts/tools/ 디렉토리. Git 기반 버전 관리 + 변경 이력 + 롤백 <!-- ⚠️ 정본: .toml (PHASE_B4 LOCK) -->

### S7F-070 | HIGH | V1 | 프롬프트 테스트 (promptfoo)

- **구현 방식**: promptfooconfig.yaml로 프롬프트 변경 시 자동 품질 평가. assert: contains, not-contains, llm-rubric. 비용: 무료 오픈소스 <!-- ⚠️ 정본: .toml (PHASE_B4 LOCK) -->

### S7F-071 | HIGH | V2 | 모델 평가 파이프라인

- **평가 차원**: 한국어 품질(KoBEST/KLUE), 코딩(HumanEval/MBPP), 추론(GSM8K/MATH), 도구 사용(BFCL), 지시 따르기(MT-Bench/AlpacaEval), 안전성(ToxiGen/AdvBench), 비용 효율, 속도(TTFT/TPS)

### S7F-072 | HIGH | V2 | 피드백 루프

- **구현 방식**: 피드백 유형: 좋아요/싫어요(모든 응답), 1-5점 상세(선택), 텍스트(선택), 재생성. Loop: Feedback → Aggregate → Pattern Analysis → Prompt Improvement → A/B Test → Deploy. 100% 로컬 저장

### S7F-073 | HIGH | V2 | 프롬프트 최적화

- **구현 방식**: DSPy 프레임워크(Stanford, 무료)로 자동 최적화. V1 수동 → V2 반자동 → V3 완전 자동화

### S7F-074 | HIGH | V2 | 모델 드리프트 감지

- **구현 방식**: 주간 벤치마크 자동 실행, 성능 트렌드 모니터링, 임계값 하락 시 알림+대체 모델 추천, 경쟁 모델 월간 비교

### S7F-075 | MED | V2 | 실험 관리 (A/B 테스트)

- **구현 방식**: Langfuse Experiments. 트래픽 90% Control / 10% Variant, 유의수준 95% 달성 시 자동 결정

### S7F-076 | MED | V1 | 모델 카탈로그

- **구현 방식**: models.yaml에 id, provider, strengths, cost, context_window, speed, available, last_evaluated, eval_score 관리. 새 모델 출시 시 자동 갱신 <!-- ⚠️ 정본: .toml (PHASE_B4 LOCK) -->

### S7F-077 | MED | V2 | Fine-tuning 파이프라인

- **구현 방식**: LoRA/QLoRA로 분류기(라우팅용), 요약기, 한국어 특화 모델 학습. 플랫폼: Together.ai/OpenAI Fine-tuning. 비용: ~$5/million tokens

### S7F-078 | MED | V2 | Guardrails 파이프라인

- **구현 방식**: NeMo Guardrails/Guardrails AI(무료). 입력: Injection 탐지, PII 마스킹, 주제 제한. 출력: 유해 콘텐츠 필터, 사실 확인, 면책 삽입

---

## F-Part 10: 네트워크/API 게이트웨이 (6건)

### S7F-079 | HIGH | V2 | API 게이트웨이

- **구현 방식**: Nginx + rate limiting + auth 또는 Kong(오픈소스). 기능: 인증, Rate Limiting, 로깅, 캐싱, CORS, SSL 종료

### S7F-080 | HIGH | V2 | SSL/TLS

- **구현 방식**: TLS 1.3, Let's Encrypt(무료) + certbot 자동 갱신, HSTS/CSP/X-Frame-Options 보안 헤더

### S7F-081 | HIGH | V2 | CORS 정책

- **구현 방식**: 화이트리스트 기반 CORS, credentials 모드 설정

### S7F-082 | HIGH | V2 | API 버전닝

- **구현 방식**: /api/v1/, /api/v2/ 경로 버전닝. 이전 버전 최소 6개월 지원, 마이그레이션 가이드

### S7F-083 | MED | V2 | CDN 설정

- **구현 방식**: Cloudflare(무료) 또는 Vercel Edge

### S7F-084 | MED | V2 | DDoS 방어

- **구현 방식**: Cloudflare(무료), rate limiting(IP당, 사용자당)

---

## F-Part 11: 백업/복구/DR (6건)

### S7F-085 | HIGH | V1 | 자동 백업

- **구현 방식**: 일일 SQLite+Chroma+KG → ~/vamos/backups/YYYY-MM-DD/. 보존: 최근 7일(일일)+4주(주간)+3개월(월간). 크기: ~50-200MB. 자동: 앱 시작+매일 02:00

### S7F-086 | HIGH | V1 | 복구 절차

- **구현 방식**: 원클릭 복구(설정>백업>날짜 선택>복구). 부분 복구: 메모리만, 설정만, 특정 프로젝트만

### S7F-087 | HIGH | V2 | 오프사이트 백업

- **구현 방식**: E2E 암호화 → Cloudflare R2/Backblaze B2($0.005/GB/mo). 사용자 키로 암호화(서버 열람 불가)

### S7F-088 | MED | V2 | 데이터 마이그레이션 (V1→V2)

- **구현 방식**: SQLite→PostgreSQL(drizzle-kit), Chroma→Qdrant(벡터 변환), NetworkX JSON→Neo4j(Cypher), JSON configs→DB configs. 원클릭 마이그레이션+검증 스크립트

### S7F-089 | MED | V2 | 재해 복구 계획

- **구현 방식**: RTO 4시간 / RPO 24시간. 백업 확인 → 새 인스턴스 → 데이터 복구 → DNS 전환 → 검증

### S7F-090 | MED | V2 | 데이터 export/import

- **구현 방식**: JSON(메모리, 설정) + SQLite(대화 이력) + 첨부파일. GDPR 데이터 이동권 충족

---

## F-Part 12: 성능 최적화 심화 (6건)

### S7F-091 | CRITICAL | V1 | TTFT 최적화

- **전략**: Prompt Caching(TTFT 50% 감소), Streaming(체감 0s), Speculative Decoding(V3, TPS 2-3x), 로컬 LLM 사전 분류(API 대기 제거), 예측 프리페치(사용자 패턴). 목표: TTFT <1초(API) / <200ms(로컬)

### S7F-092 | CRITICAL | V1 | 메모리 사용량 최적화

- **목표**: Tauri ~50MB + Node.js ~100-200MB + Ollama(7B Q4) ~4GB + ChromaDB ~100MB = Total ~4.5GB(16GB RAM의 28%). 최적화: 게으른 로딩, 미사용 모델 언로드, GC 튜닝, 스트리밍 처리

### S7F-093 | HIGH | V1 | 동시성 관리

- **구현 방식**: Node.js Event Loop(비동기 I/O), Promise.all(독립 API 병렬), Worker Threads(CPU 집약), 세마포어(최대 동시 API 호출 5)

### S7F-094 | HIGH | V1 | 응답 시간 SLO

- **SLO**: 간단한 채팅 P50<1s/P95<3s, 검색+답변 P50<3s/P95<8s, 코드 생성 P50<5s/P95<15s, 문서 분석 P50<10s/P95<30s, Agent 작업 P50<30s/P95<120s. SLO 위반 시 자동 알림+원인 분석

### S7F-095 | HIGH | V2 | 데이터베이스 성능

- **구현 방식**: 인덱스 설계, EXPLAIN ANALYZE, 연결 풀링(pg-pool), Redis 읽기 캐시, HNSW 인덱스 최적화(Qdrant ef_construct, m)

### S7F-096 | MED | V2 | 프론트엔드 성능

- **구현 방식**: Virtual Scrolling(react-window), Code Splitting, WebP+레이지 로딩, Web Worker(마크다운 파싱, 코드 하이라이팅), 목표: Lighthouse >=90

---

### F 기술 스택 최종 요약

| 레이어 | V1 | V2 | V3 |
|--------|-----|-----|-----|
| Frontend | Tauri+React | Next.js+PWA | +Native Mobile |
| Backend | Node.js sidecar | Node.js server | +Worker cluster |
| LLM Local | Ollama | Ollama+vLLM | +TensorRT-LLM |
| LLM Cloud | Claude/GPT API | +LiteLLM Gateway | +Self-hosted |
| Main DB | SQLite+SQLCipher | PostgreSQL | +Read replicas |
| Vector DB | Chroma | Qdrant | +Qdrant Cluster |
| Graph DB | NetworkX+JSON | Neo4j | +Neo4j Cluster |
| Cache | In-memory | Redis | +Redis Cluster |
| Queue | -- | BullMQ | +RabbitMQ |
| CI/CD | GitHub Actions | +Docker | +Helm/K8s |
| Monitor | JSON logs | Grafana+Langfuse | +DataDog |
| Backup | Local auto | +Offsite encrypted | +Multi-region |

---

# G. 벤치마크 / 평가 / 품질보증 (88건)

## G-Part 1: 표준 LLM 벤치마크 (10건)

### 주요 벤치마크 전수비교표

> **[PART1 ST-06]** 벤치마크 수치는 조사 시점(2025.02) 기준. 최신 모델: Claude Opus 4.6 / Sonnet 4.6 / Haiku 4.5. 구현 시 최신 벤치마크 참조 필요.

| 벤치마크 | 카테고리 | GPT-4o | Claude 3.5 Sonnet | Gemini 2.0 | Llama 3.3 70B | DeepSeek V3 | VAMOS 활용 |
|---------|---------|--------|-------------------|-----------|--------------|-------------|-----------|
| MMLU | 지식(57과목) | 88.7 | 88.7 | 87.5 | 86.0 | 88.5 | 모델 선택 기준 |
| MMLU-Pro | 지식(강화) | 72.6 | 78.0 | 75.2 | 66.4 | 75.9 | 추론 모델 선택 |
| GPQA | 전문(대학원) | 53.6 | 65.0 | 59.1 | 46.7 | 59.1 | 전문 라우팅 |
| HumanEval | 코딩(Python) | 90.2 | 92.0 | 87.6 | 88.4 | 89.0 | 코딩 Agent |
| MATH | 수학(경시대회) | 76.6 | 78.3 | 83.9 | 77.0 | 84.3 | 수학 능력 |
| GSM8K | 수학(기초) | 95.8 | 96.4 | 95.2 | 93.8 | 96.7 | 기본 추론 |
| MT-Bench | 대화(다턴) | 9.32 | 9.12 | 9.20 | 8.95 | 9.05 | 대화 품질 |
| IFEval | 지시따르기 | 84.3 | 88.4 | 85.7 | 82.1 | 86.2 | 명령 수행력 |
| ARC-C | 추론(과학) | 96.4 | 96.7 | 95.8 | 94.5 | 96.3 | 기본 추론력 |
| HellaSwag | 상식 | 95.3 | 94.8 | 95.0 | 93.2 | 95.1 | 상식 수준 |

### S7G-001 | HIGH | V1 | MMLU/MMLU-Pro

- **모듈 연동**: A(Agent Layer) - 모델 선택 기준
- **구현 방식**: 새 모델 도입 시 MMLU 최소 85+ 필수, MMLU-Pro 65+ 이상 모델만 추론 작업 라우팅, 모델 카탈로그에 MMLU 점수 기록. 자체 테스트: 한국어 번역 MMLU 서브셋(100문항) 자동 실행

### S7G-002 | HIGH | V1 | HumanEval/MBPP

- **구현 방식**: Dev Node 모델 선택 기준: HumanEval 85+. pass@1(단일 시도 통과율) 기준 적용. HumanEval+(엣지 케이스 강화) 필수 테스트. 자체 확장: VAMOS 코딩 유형별 커스텀 테스트(Python, JS, Rust)

### S7G-003 | HIGH | V1 | MT-Bench

- **구현 방식**: 대화 모델 품질 기준: MT-Bench 8.5+. 카테고리별 점수: writing, reasoning, math, coding, extraction, stem, humanities, roleplay. VAMOS 커스텀 카테고리 추가: 한국어, 투자, 개인비서

### S7G-004 | HIGH | V1 | IFEval

- **구현 방식**: Agent 작업 핵심 — 복잡한 지시 정확 수행. 지시 유형: 포맷 제한, 길이 제한, 내용 제한, 조건부 응답. 목표: IFEval 85+ 모델만 Agent 작업 배정. Constitution 준수 테스트와 연계

### S7G-005 | HIGH | V1 | GPQA/ARC-C

- **구현 방식**: Research Node 모델 기준: GPQA 50+. 투자 분석 작업에서 추론력 중요. Quant Node: 수학적 추론 능력 필수

### S7G-006 | HIGH | V1 | MATH/GSM8K

- **구현 방식**: Quant/Trading Node 모델 기준: MATH 70+, GSM8K 95+. 투자 계산, 포트폴리오 분석, 리스크 계산 필수. Chain-of-Thought + Tool Use(계산기) 병행 테스트

### S7G-007 | MED | V2 | AlpacaEval 2.0

- **구현 방식**: 오픈 엔드 지시 품질을 GPT-4 Judge로 자동 평가. 월간 모델 비교, Length-Controlled(LC) 점수로 길이 편향 보정

### S7G-008 | MED | V2 | Chatbot Arena ELO

- **구현 방식**: LMSYS Chatbot Arena 순위 월간 모니터링. 새 모델 평가 시 Arena 순위 참고. VAMOS 내부 A/B 비교 → ELO 산출

### S7G-009 | MED | V2 | WildBench

- **구현 방식**: 실제 사용자 질문 기반 현실적 벤치마크. 학술 벤치마크와 실사용 간 갭 측정, 분기별 실행

### S7G-010 | MED | V2 | LiveBench

- **구현 방식**: 데이터 오염 방지 위해 매월 새 문제로 갱신. 모델의 진짜 실력 측정(학습 데이터 포함 불가)

---

## G-Part 2: 한국어 특화 벤치마크 (8건)

### 한국어 벤치마크 비교표

| 벤치마크 | 측정 대상 | GPT-4o | Claude 3.5 | Gemini 2.0 |
|---------|----------|--------|-----------|-----------|
| KoBEST | 한국어 NLU 5종 | ~92 | ~91 | ~90 |
| KLUE | 한국어 NLU 8종 | ~88 | ~87 | ~86 |
| LogicKor | 한국어 논리 | ~87 | ~88 | ~85 |
| CLIcK | 한국 문화 지식 | ~65 | ~62 | ~60 |
| HAE-RAE | 한국어 종합 | ~85 | ~84 | ~82 |
| Ko-MMLU | MMLU 한국어 | ~82 | ~80 | ~78 |

### S7G-011 | CRITICAL | V1 | KoBEST

- **구현 방식**: 한국어 NLU 5가지 — BoolQ(참거짓), COPA(인과추론), WiC(단어의미), HellaSwag(상식), SentiNeg(감성). 모델 선택 시 KoBEST 평균 88+ 필수. V1 출시 전 모든 후보 모델 KoBEST 테스트 필수

### S7G-012 | CRITICAL | V1 | KLUE

- **구현 방식**: 한국어 NLU 8가지(KAIST) — TC(주제분류), STS(문장유사), NLI(자연어추론), NER(개체명), RE(관계추출), DP(의존파싱), MRC(기계독해), DST(대화상태). NER→메모리 인물/장소/날짜 추출, STS→시맨틱 검색 품질, MRC→RAG 문서 이해. 목표: KLUE 평균 85+

### S7G-013 | HIGH | V1 | LogicKor

- **구현 방식**: 한국어 논리추론 — 수학추론, 논리퍼즐, 작문, 코딩, 이해력. Research/Quant Node 한국어 추론 기준. 투자 분석 보고서 작성 품질 연관. 목표: LogicKor 85+

### S7G-014 | HIGH | V1 | CLIcK

- **구현 방식**: 한국 문화/역사/사회 지식 평가. 한국 공휴일, 문화 관습, 사회 규범 이해. 한국식 감정 표현 이해(STEP7-B 연계). 목표: CLIcK 60+(외국 모델 한계 인식)

### S7G-015 | HIGH | V1 | 한국어 환각 테스트

- **구현 방식**: 한국 팩트체크 데이터셋(SNU FactCheck) 기반. 한국 인물/지역/사건 사실 확인 100개 질문. 환각 유형: 완전 허위/부분 부정확/최신성 오류. 목표: 환각률 <5%

### S7G-016 | HIGH | V1 | 한국어 존댓말/비속어 테스트

- **구현 방식**: 존댓말 일관성(설정에 따른 유지), 비속어/불쾌어 미생성, 호칭 적절성, 번역투 최소화. 목표: 번역투 탐지율 <10%, 존댓말 일관성 >98%

### S7G-017 | MED | V2 | Ko-MMLU

- **구현 방식**: MMLU 한국어 번역판. MMLU 영어/한국어 점수 갭 분석. 갭이 큰 모델은 한국어 작업 제외 또는 번역 파이프라인 추가

### S7G-018 | MED | V2 | 한국어 생성 품질

- **구현 방식**: 요약 정확성(ROUGE-L), 번역 품질(BLEU/COMET), 작문 자연스러움(인간 평가)

---

## G-Part 3: 코딩 벤치마크 (8건)

### S7G-019 | HIGH | V1 | HumanEval/HumanEval+

- **구현 방식**: Python 코드 생성 + 테스트 통과율. Dev Node 모델 선택 1차 기준. pass@1 85+ 모델만 코딩 작업 배정. 목표: HumanEval+ 82+

### S7G-020 | HIGH | V1 | SWE-bench (Verified)

- **구현 방식**: 실제 GitHub 이슈 해결 능력(가장 현실적). Claude Sonnet 계열 49%+ 1위 → VAMOS Dev Node 핵심 모델. SWE-bench Lite(300문제) 빠른 테스트. 목표: VAMOS Agent SWE-bench 40%+

### S7G-021 | HIGH | V1 | BFCL (Berkeley Function Calling)

- **구현 방식**: LLM 함수/Tool 호출 정확도 — Simple/Multiple/Parallel Function, Relevance Detection, AST Summary. MCP Tool 호출 정확도 직결. 모델 선택 시 BFCL 88+ 필수. VAMOS 커스텀 Tool 호출 테스트 30건 추가

### S7G-022 | HIGH | V1 | Aider Polyglot

- **구현 방식**: 기존 코드베이스에서 코드 편집 능력. Python/JavaScript/TypeScript/Rust 다국어 수정. "기존 코드 수정" → Agent 핵심 역량. 목표: 전체 편집 성공률 70+

### S7G-023 | HIGH | V1 | MultiPL-E

- **구현 방식**: Python 외 JS/TS/Rust 다언어 코딩. VAMOS 핵심 언어: TypeScript(프론트), Rust(Tauri), Python(Agent). 언어별 모델 라우팅 최적화

### S7G-024 | MED | V2 | 코드 보안 평가

- **구현 방식**: CWE Top 25 취약점 생성 빈도(SQL Injection, XSS, Buffer Overflow). Semgrep/CodeQL 자동 스캔. 목표: 보안 취약 코드 생성률 <2%

### S7G-025 | MED | V2 | 코드 리뷰 품질

- **구현 방식**: 버그 발견률, 제안 정확성, false positive 비율. Dev Node 코드 리뷰 기능 품질 기준

### S7G-026 | MED | V2 | 디버깅 능력

- **구현 방식**: 버그 코드에서 식별+수정+설명. 데이터셋: BugsInPy, Defects4J

---

## G-Part 4: Agent/Tool Use 벤치마크 (8건)

### S7G-027 | CRITICAL | V1 | BFCL v3

- **구현 방식**: VAMOS MCP Tool 호출 정확도 핵심 벤치마크 — 단일/복수/병렬 Tool 호출, Tool 불필요 시 거부, 복합 시나리오. VAMOS 커스텀 확장 30건: MCP Tool 호출(10건), 5-Gate 판단(10건), Multi-Agent 위임(10건)

### S7G-028 | CRITICAL | V1 | Tau-bench

- **구현 방식**: 대화형 Agent 평가 — 대화 속 Tool 적절 사용. 시나리오: 항공사 예약, 쇼핑 주문. ORANGE CORE 대화형 작업 수행 핵심 지표. 커스텀: 투자 분석 요청, 문서 작성, 일정 관리

### S7G-029 | HIGH | V1 | GAIA

- **구현 방식**: 범용 AI 비서 종합 능력 — Level 1(단순 도구), Level 2(다단계 추론+도구), Level 3(복합 문제, 여러 도구+긴 추론). 분기별 테스트

### S7G-030 | HIGH | V1 | AgentBench

- **구현 방식**: 8가지 환경(OS 조작, DB 쿼리, 지식 그래프, 웹 탐색, 게임, 코딩, 웹쇼핑, 가정환경). Dev Node: 코딩 환경, Research Node: 지식 그래프+웹 탐색

### S7G-031 | HIGH | V2 | ToolBench

- **구현 방식**: 16,000+ API 활용 능력. MCP Tool 확장 시 새 Tool 활용 평가. Zero-shot Tool 학습: 처음 보는 Tool 사용 능력

### S7G-032 | HIGH | V2 | WebArena/VisualWebArena

- **구현 방식**: 웹 브라우저 작업 수행. Computer Use/GUI Agent 품질 평가. V3 웹 자동화 핵심 벤치마크

### S7G-033 | MED | V2 | OSWorld

- **구현 방식**: OS 수준 작업(파일 관리, 앱 설치, 설정 변경). V3 데스크톱 자동화 평가

### S7G-034 | MED | V2 | MLE-bench

- **구현 방식**: Kaggle 대회 수준 ML 파이프라인 구축. Quant Node ML 모델 구축 능력 기준

---

## G-Part 5: RAG 품질 평가 (10건)

### RAG 평가 3차원

1. **Retrieval Quality**: Precision, Recall, MRR, NDCG
2. **Generation Quality**: Faithfulness, Answer Relevancy, Context Precision, Context Recall
3. **End-to-End Quality**: Correctness, Completeness, Harmfulness, Latency

### S7G-035 | CRITICAL | V1 | RAGAS 프레임워크

- **구현 방식**: `from ragas import evaluate` — faithfulness, answer_relevancy, context_precision, context_recall. 비용: 무료 오픈소스. 목표: Faithfulness 0.9+, Answer Relevancy 0.85+, Context Precision 0.8+

### S7G-036 | CRITICAL | V1 | 검색 정확도 평가

- **구현 방식**: VAMOS 커스텀 100개 질문-정답 쌍(사실30/분석30/개인20/코딩20). 지표: Precision@K, Recall@K, MRR, NDCG@10. 검색 방식 비교: 벡터만/키워드만(BM25)/그래프만/하이브리드(RRF)/4-Index Fusion. 목표: 4-Index Fusion이 단일 대비 15%+ 개선

### S7G-037 | HIGH | V1 | Faithfulness 테스트

- **구현 방식**: RAGAS faithfulness, 인용 정확성, 없는 정보 생성 탐지. 목표: 0.90+(V1), 0.95+(V2)

### S7G-038 | HIGH | V1 | Chunking 품질 평가

- **비교**: Fixed 512(간단, 의미 절단) / Fixed 1024(더 많은 컨텍스트) / Semantic(의미 보존, 느림) / Recursive(구조 보존) / Document(전체 맥락). 추천: Semantic Chunking + Contextual Retrieval(Anthropic 방식)

### S7G-039 | HIGH | V1 | Embedding 모델 비교

- **비교**: BGE-M3(1024차원, 한국어 최고, 무료로컬, **V1 선택**), multilingual-e5-large(1024, 대안), text-embedding-3-small(1536, $0.02/1M, V2), Jina-embeddings-v3(1024, 대안), Cohere embed-v3(1024, $0.10/1M), Nomic-embed(768, 경량용). 평가: MTEB 한국어 서브셋 + VAMOS 커스텀 검색 테스트

### S7G-040 | HIGH | V1 | 컨텍스트 윈도우 활용 평가

- **구현 방식**: Needle-in-a-Haystack, Multi-Needle, 위치별 정확도(시작/중간/끝). Claude 200K/GPT 128K/Gemini 2M 비교. RAG vs Long Context 전략 결정 기준

### S7G-041 | HIGH | V2 | RAG vs Long Context

- **구현 방식**: 동일 질문 RAG vs 전체 문서 직접 입력 비교. 정확도/비용/속도 3축. 문서 크기별 최적 전략 결정 규칙 도출

### S7G-042 | MED | V2 | Self-RAG/CRAG 품질 평가

- **구현 방식**: 기본 RAG vs Self-RAG vs CRAG vs RAPTOR 비교. 목표: 기본 RAG 대비 정확도 10%+ 개선

### S7G-043 | MED | V2 | 다국어 RAG 평가

- **구현 방식**: 한국어 질문→영어 문서, 영어 질문→한국어 문서 정확도. BGE-M3 다국어 성능 핵심

### S7G-044 | MED | V2 | Knowledge Graph RAG 평가

- **구현 방식**: KG 검색이 벡터 검색 대비 개선도. 관계 추론 질문("X와 Y의 관계는?") 정확도

---

## G-Part 6: 안전성 벤치마크 (8건)

### S7G-045 | CRITICAL | V1 | TruthfulQA

- **구현 방식**: 일반적 오해에 빠지지 않는 진실된 답변. "모르겠습니다" 허용(거짓보다 나음). 목표: TruthfulQA MC1 55+

### S7G-046 | CRITICAL | V1 | Prompt Injection 저항성

- **구현 방식**: 테스트 100건 — Direct Injection(20), Indirect Injection(20), Prompt Leaking(20), Jailbreak(20), Multi-turn(20). 방어 성공률 95+(V1)/99+(V2). False Positive <2%. 도구: garak(무료), PyRIT(Microsoft)

### S7G-047 | HIGH | V1 | ToxiGen

- **구현 방식**: 유해 콘텐츠 생성 빈도. 목표: <0.5%

### S7G-048 | HIGH | V1 | BBQ (Bias Benchmark)

- **구현 방식**: 성별/인종/나이/종교 편향 평가. 편향 높은 모델의 민감 주제 라우팅 제한

### S7G-049 | HIGH | V1 | AdvBench

- **구현 방식**: 유해 요청 거부 능력. 목표: 거부율 99%+

### S7G-050 | HIGH | V2 | 한국어 안전성 테스트

- **구현 방식**: 한국 법률 위반 콘텐츠 거부, 민감 주제(정치/남북/역사) 균형 응답, 한국 혐오 표현 탐지, 투자 불법 조언 방지(자본시장법)

### S7G-051 | MED | V2 | AI Deception 테스트

- **구현 방식**: 에러 숨김, 능력 과장, 확신 없는 단정, 출처 날조 탐지

### S7G-052 | MED | V2 | 긴급 상황 대응

- **구현 방식**: 자해/위기 상황 적절 대응. 위기 자원(상담전화) 안내 + 공감적 응답

---

## G-Part 7: 사용자 경험(UX) 평가 (8건)

### S7G-053 | HIGH | V1 | 작업 완수율

- **목표**: 단순 질문 95%, 코딩 85%, 분석 80%, Agent 복합 70%. 실패 원인 분류: 모델 한계/도구 오류/이해 오류/비용 제한

### S7G-054 | HIGH | V1 | 응답 시간 체감

- **목표**: TTFT <1s. 스트리밍 유무에 따른 체감 차이, 진행 상태 표시 효과 측정

### S7G-055 | HIGH | V1 | 사용자 만족도

- **구현 방식**: 좋아요/싫어요(모든 응답), 1-5점(선택), NPS(분기별). 차원별: 정확성, 유용성, 속도, 안전성, 비용 대비

### S7G-056 | HIGH | V1 | 대화 효율성

- **측정**: 평균 턴 수(작업 유형별), 명확화 질문 빈도, 재시도 요청 빈도. 목표: 경쟁 AI 대비 평균 턴 수 20% 감소

### S7G-057 | MED | V1 | 온보딩 효과

- **측정**: 설정 완료율, 소요 시간, 첫 대화 성공률, 7일 리텐션

### S7G-058 | MED | V2 | 개인화 효과

- **구현 방식**: A/B 테스트: 개인화 ON vs OFF → 만족도/정확도/효율성 비교

### S7G-059 | MED | V2 | 접근성 평가

- **기준**: WCAG 2.1 AA, 키보드 네비게이션, 스크린리더 호환

### S7G-060 | MED | V2 | 다국어 UX

- **측정**: 한국어-영어 전환 정확도, 혼합 입력 처리, 번역 품질

---

## G-Part 8: VAMOS 고유 벤치마크 (10건)

### VAMOS Custom Benchmark Suite (VBS) 개요

| VBS | 측정 대상 | 주기 |
|-----|----------|------|
| VBS-1 | 5-Gate 정확도 | 주간 |
| VBS-2 | 모델 라우팅 효율 | 주간 |
| VBS-3 | 메모리 회상 품질 | 주간 |
| VBS-4 | KG 탐색 품질 | 주간 |
| VBS-5 | 자기진화 점수 | 월간 |
| VBS-6 | 비용 효율 비율 | 주간 |
| VBS-7 | Constitution 준수율 | 주간 |
| VBS-8 | Agent 협업 품질 | 월간 |
| VBS-9 | 개인 비서 종합 점수 | 월간 |
| VBS-10 | 투자 분석 품질 | 월간 |

### S7G-061 | CRITICAL | V1 | VBS-1: 5-Gate 정확도

- **구현 방식**: 60건 테스트 — Policy Gate(20건: 통과 10+차단 10), Cost Gate(20건: 예산 내 10+초과 10), Evidence Gate(20건: 근거 충분 10+부족 10). 점수=(정확/60)*100. 목표: 85(V1)/95(V2)

### S7G-062 | CRITICAL | V1 | VBS-2: 모델 라우팅 효율

- **구현 방식**: 50건(카테고리 10건씩) — 간단 질문→Ollama, 코딩→Sonnet, 빠른 분류→4o-mini, 검색→Gemini+Search, 깊은 추론→Opus. 선택 정확도+비용 효율(실제/최적). 목표: 정확도 80%, 비용 효율 1.2x 이하

### S7G-063 | CRITICAL | V1 | VBS-3: 메모리 회상 품질

- **구현 방식**: 30건 — 사실 기억(10: 이름/생일/직업), 선호 기억(10: 음식/코딩 스타일), 맥락 기억(10: 어제 논의 프로젝트). 정확 회상률+선택적 망각(삭제 요청 미회상). 목표: 회상 90%, 망각 100%

### S7G-064 | HIGH | V1 | VBS-6: 비용 효율 비율

- **구현 방식**: CER = (VAMOS 품질/비용) / (ChatGPT 품질/비용). 예: VAMOS 85점/$8=10.6, ChatGPT 90점/$20=4.5, CER=2.36x. 목표: CER >= 2.0x

### S7G-065 | HIGH | V1 | VBS-7: Constitution 준수율

- **구현 방식**: 톤/어투(20건), 경계(20건), 우선순위(10건) 규칙 준수. 목표: 95%+ 준수율

### S7G-066 | HIGH | V1 | VBS-4: KG 탐색 품질

- **구현 방식**: 관계 추론 질문 20건 — KG 있을 때 vs 없을 때 정확도 비교. 목표: KG 사용 시 20%+ 향상

### S7G-067 | HIGH | V2 | VBS-5: 자기진화 점수

- **구현 방식**: 동일 테스트셋 주간 반복 → 점수 추이. 사용 1주/1개월/3개월 후 비교. 개인화 효과 만족도 변화

### S7G-068 | HIGH | V2 | VBS-8: Agent 협업 품질

- **구현 방식**: Research→Dev, Quant→Content, 3개+ Agent 순차/병렬 협업. 목표: 단일 Agent 대비 복합 작업 30%+ 향상

### S7G-069 | MED | V2 | VBS-9: 개인 비서 종합

- **구현 방식**: 일정 관리, 이메일 초안, 요약, 번역, 리마인더, 추천. Google Assistant/Siri 수준 이상

### S7G-070 | MED | V2 | VBS-10: 투자 분석 품질

- **구현 방식**: 기업 분석(10건), 시장 트렌드(10건), 포트폴리오(10건), 리스크 경고(10건). 실제 수익률이 아닌 분석 논리 품질 평가

---

## G-Part 9: 자동 평가 파이프라인 (8건)

### S7G-071 | HIGH | V1 | LLM-as-Judge

- **구현 방식**: GPT-4o Judge로 응답 품질 자동 평가. 평가 기준: 정확성/유용성/완전성/안전성/한국어 자연스러움(각 1-5). 비용: GPT-4o-mini ~$0.001/요청. 다중 Judge로 편향 완화

### S7G-072 | HIGH | V1 | promptfoo 통합

- **구현 방식**: 프롬프트 변경 시 자동 회귀 테스트. CI/CD 통합: PR마다 실행, 품질 저하 시 머지 차단

### S7G-073 | HIGH | V1 | 회귀 테스트 자동화

- **구현 방식**: Core 응답 50건 + Tool 호출 30건 + 안전성 20건 + 한국어 20건 = 120건 고정 테스트. 주간 자동 + PR마다 Core 50건. 임계값: 이전 대비 3% 이상 하락 시 알림

### S7G-074 | HIGH | V1 | 자동 벤치마크 스케줄러

- **스케줄**: 일간 VBS Core(1-3,6-7) ~$0.50, 주간 VBS 전체+안전성 ~$2.00, 월간 전체 표준 ~$10.00, 분기 전체+인간 평가 ~$50.00

### S7G-075 | HIGH | V2 | 평가 대시보드

- **패널**: 종합 점수 추이(시간축), 카테고리별 레이더 차트, 모델별 비교, 비용 효율 산점도, 회귀 테스트 합격/불합격

### S7G-076 | MED | V2 | 자동 리포트 생성

- **포함**: 점수 요약, 추이 분석, 개선 권고, 모델 교체 제안

### S7G-077 | MED | V2 | 경쟁사 추적

- **구현 방식**: ChatGPT/Claude/Gemini 성능 변화 추적. Chatbot Arena, LMSYS, 공식 벤치마크 모니터링

### S7G-078 | MED | V2 | 평가 데이터셋 관리

- **구현 방식**: 골든 데이터셋 500건(카테고리별), 정기 갱신, 버전 관리

---

## G-Part 10: 인간 평가 프로세스 (6건)

### S7G-079 | HIGH | V1 | 자기 평가

- **구현 방식**: 개발자 주 1회 30분 체크리스트 — 대화 품질, 도구 사용, 속도, 안전성, 개인화 효과

### S7G-080 | HIGH | V2 | 베타 테스터 피드백

- **구현 방식**: V2 출시 전 10-20명. 2주 사용 → 설문+인터뷰+로그 분석

### S7G-081 | HIGH | V2 | A/B 인간 비교

- **구현 방식**: VAMOS vs ChatGPT/Claude 블라인드 비교. 100건, 5명 평가자

### S7G-082 | MED | V2 | 시나리오 기반 테스트

- **시나리오**: 일일 업무 비서, 코딩 프로젝트 지원, 투자 분석, 학습 도우미

### S7G-083 | MED | V2 | 전문가 리뷰

- **구현 방식**: 투자/코딩/보안 도메인 전문가의 정확성+깊이 평가

### S7G-084 | MED | V3 | 장기 사용성 연구

- **구현 방식**: 3-6개월 장기 사용 품질 변화 추적. 개인화 효과, 자기진화, 만족도 추이

---

## G-Part 11: 품질 보증 프로세스 (4건)

### S7G-085 | HIGH | V1 | QA 체크리스트

- **릴리즈 품질 게이트**: Unit Test >=80%, Integration Pass, E2E Core Pass, VBS Core >=80, Prompt Regression Pass, Security Test Pass, 한국어 품질 Pass, Performance SLO 달성, 비용 예산 내, 접근성 기본 Pass

### S7G-086 | HIGH | V1 | 버그 트래킹

- **구현 방식**: GitHub Issues + Labels(bug/enhancement/security). 발견 → 재현 → 원인 분석 → 수정 → 테스트 → 릴리즈

### S7G-087 | MED | V2 | 품질 지표 (KPI)

- **V1/V2 목표**: 작업 완수율 80%/90%, 만족도 4.0/4.3, 환각률 <8%/<3%, Injection 방어 95%/99%, CER 2.0x/2.5x, 한국어 자연스러움 85%/92%

### S7G-088 | MED | V2 | 지속적 개선

- **구현 방식**: 측정 → 분석 → 개선 → 검증 → 배포 (월간 반복)

---

# H. 비즈니스 모델 / 시장 전략 (78건)

## H-Part 1: AI 서비스 가격 전수비교 (10건)

### H-Part 1 소비자향 AI 서비스 가격표 (2025.02 기준)

> **[PART1 ST-06]** 가격은 조사 시점 기준. 구현 시 최신 API 가격 확인 필요. Claude 최신: Opus 4.6 / Sonnet 4.6 / Haiku 4.5.

| 서비스 | 무료 | 기본 구독 | 프로 구독 | 팀/기업 | 특징 |
|--------|------|----------|----------|---------|------|
| ChatGPT | GPT-4o-mini | Plus $20/mo | Pro $200/mo | Team $25/user/mo | 가장 큰 사용자 기반 |
| Claude | Claude 3.5 | Pro $20/mo | — | Team $25/user/mo | 최고 코딩/분석 |
| Gemini | Gemini 2.0 | Advanced $20/mo | — | Workspace 추가 | Google 생태계 통합 |
| Perplexity | 기본 검색 | Pro $20/mo | — | Enterprise 맞춤 | 검색 특화 |
| Grok | X 프리미엄 | X Premium $8/mo | X Premium+ $16/mo | — | X/Twitter 통합 |
| Mistral | Le Chat | — | — | Enterprise 맞춤 | 유럽 기반, 오픈소스 |
| Poe | 제한적 | $20/mo | — | — | 멀티 모델 |
| Character.ai | 제한적 | c.ai+ $10/mo | — | — | 캐릭터 특화 |
| Notion AI | — | $10/user/mo | — | Enterprise 맞춤 | 생산성 통합 |
| GitHub Copilot | — | Individual $10/mo | Business $19/user/mo | Enterprise $39/user/mo | 코딩 특화 |
| Cursor | — | Pro $20/mo | Business $40/user/mo | — | AI IDE |

### H-Part 1 API 가격 비교 (입력/출력 per 1M tokens)

| Provider | 모델 | 입력 | 출력 | 컨텍스트 | Cached |
|----------|------|------|------|---------|--------|
| Anthropic | Claude 3.5 Sonnet | $3.00 | $15.00 | 200K | $0.30 |
| Anthropic | Claude 3.5 Haiku | $0.80 | $4.00 | 200K | $0.08 |
| OpenAI | GPT-4o | $2.50 | $10.00 | 128K | $1.25 |
| OpenAI | GPT-4o-mini | $0.15 | $0.60 | 128K | $0.075 |
| Google | Gemini 2.0 Flash | $0.10 | $0.40 | 1M | $0.025 |
| Google | Gemini 1.5 Pro | $1.25 | $5.00 | 2M | $0.315 |
| DeepSeek | DeepSeek-V3 | $0.27 | $1.10 | 128K | $0.07 |
| Mistral | Mistral Large | $2.00 | $6.00 | 128K | — |
| Groq | Llama 3.3 70B | $0.59 | $0.79 | 128K | — |

---

### S7H-001 | HIGH | V1 | 가격 모니터링 대시보드 — API 가격 추적

- **모듈 연동**: I(Infra Core), S(Service Layer) - 비용 관리 서브시스템
- **구현 방식**: 주요 LLM API 가격 변동을 정기 추적하는 대시보드 구축. 월 1회 가격 비교표 갱신, 가격 변동 시 Model Router의 라우팅 규칙 재조정. AI API 가격은 연 30-50% 하락 추세로, 지속적 모니터링이 비용 최적화의 핵심
- **기술 스택**: JSON 기반 가격 테이블, 스케줄러(cron/node-cron), 비용 추적 로그
- **VAMOS 연동**: Model Router(S7F-003)의 비용 기반 라우팅 규칙과 연동하여, 가격 변동 시 자동으로 라우팅 최적화 트리거
- **V1**: 월간 수동 갱신 + 가격 변동 알림 → **V2**: 자동 가격 수집 + 자동 라우팅 조정 → **V3**: AI 기반 가격 예측 + 선제적 계약 협상

### S7H-002 | HIGH | V1 | 구독 서비스 가치 분석 — $20/mo vs VAMOS

- **모듈 연동**: H(비즈니스) - 시장 포지셔닝 분석
- **구현 방식**: ChatGPT Plus/Claude Pro ($20/mo 고정 구독)와 VAMOS의 가치 비교 분석. ChatGPT Plus: GPT-4o 무제한(80msg/3h), DALL-E 3, 파일 분석, GPT Store — 제한: 단일 모델, 개인화 없음, 메모리 제한적. Claude Pro: Claude 3.5 Sonnet/Opus, Projects(5개), Artifacts — 제한: 사용량 제한, 개인화 제한적. VAMOS ($8~10/mo API): 멀티 모델 라우팅, 5-Layer 메모리(완전 개인화), Knowledge Graph, 5-Gate System(비용 제어+안전), Agent Teams, 100% 데이터 주권
- **기술 스택**: 비교 분석 프레임워크, 벤치마크 데이터 수집
- **VAMOS 연동**: 비용 투명성 시스템(S7H-012)과 연계하여 실시간 비용 비교 제공
- **V1**: 정적 비교 콘텐츠 제작 → **V2**: 동적 비용 비교 대시보드 → **V3**: 개인화된 비용 절감 리포트

### S7H-003 | HIGH | V1 | 코딩 AI 가격 분석 — 개발자 도구 비교

- **모듈 연동**: H(비즈니스) - 경쟁 분석
- **구현 방식**: GitHub Copilot($10~39/mo), Cursor($20~40/mo), Sourcegraph Cody 등 코딩 AI 도구와 VAMOS Dev Node의 가격/기능 비교. VAMOS는 범용 비서 + 코딩 통합으로 별도 코딩 AI 구독 없이 동일 기능 제공 가능
- **기술 스택**: 비교 분석 문서, 벤치마크 테스트
- **VAMOS 연동**: Dev Node(Agent Layer), 코딩 벤치마크(S7G Part 3)와 연계
- **V1**: 코딩 AI 비교 콘텐츠 → **V2**: 코딩 벤치마크 결과 기반 자동 비교 → **V3**: IDE 플러그인 직접 경쟁

### S7H-004 | HIGH | V1 | 생산성 AI 가격 분석 — Notion AI 등 비교

- **모듈 연동**: H(비즈니스) - 경쟁 분석
- **구현 방식**: Notion AI($10/user/mo), Microsoft 365 Copilot($30/user/mo) 등 생산성 도구 가격 분석. VAMOS는 별도 구독 없이 API 비용만으로 유사 기능 제공 가능하며, 데이터 주권까지 확보
- **기술 스택**: 기능 매트릭스 비교, TCO 계산 모델
- **VAMOS 연동**: Content Node(Agent Layer), 생산성 벤치마크와 연계
- **V1**: 생산성 AI 비교 콘텐츠 → **V2**: 생산성 통합 플러그인(Notion/Obsidian) → **V3**: 기업용 생산성 스위트

### S7H-005 | HIGH | V1 | TCO 분석 — Total Cost of Ownership

- **모듈 연동**: H(비즈니스), I(Infra Core) - 비용 모델링
- **구현 방식**: VAMOS 사용의 총 소유 비용(TCO) 분석. V1 TCO: 초기 비용 $0(오픈소스, 기존 PC), 설정 30분, 월 API $5-10/mo, 인프라 $0(로컬). 연간 TCO ~$60-120 vs ChatGPT Plus $240/년 vs Claude Pro $240/년 → 50-75% 절감
- **기술 스택**: TCO 계산기, 시나리오별 비용 모델
- **VAMOS 연동**: 비용 제어 시스템(S7H-013), 5-Gate Cost Gate(S7F-003)
- **V1**: TCO 비교 콘텐츠 → **V2**: 개인화 TCO 계산기(사용 패턴 기반) → **V3**: 기업 TCO 분석 도구

#### AI 개발 도구 가이드라인 준수율 비교 [REF:영상6]

> 기존 기능/가격 비교에 "지침 준수 능력" 비교 축 추가

| 도구 | 지침 준수율 | 특징 |
|------|-----------|------|
| Claude Code | 높음 | .rules 파일 기반 규칙 꼼꼼히 준수, 맥락 유지 |
| GitHub Copilot | 중간 | 자동 완성 위주, 프로젝트 규칙 반영 제한적 |
| Cursor | 중간-높음 | .cursorrules 지원, 전체 맥락 참조 가능 |
| OpenAI Codex | 낮음-중간 | 규칙 파일 누락 사례 보고, 단순 작업에 적합 |
| AntiGravity | 낮음 | 새로운 도구, 규칙 준수 기능 미성숙 |

- **VAMOS 시사점**: 외부 도구 연동 시 VAMOS .vamosrules 준수를 강제하는 래퍼 레이어 필요 (E-1 Coding Helper에서 처리)

### S7H-006 | HIGH | V1 | 무료 대안 분석 — Free Tier 경쟁

- **모듈 연동**: H(비즈니스) - 가격 전략
- **구현 방식**: 완전 무료 VAMOS 사용 시나리오 분석. Free Tier 조합: Ollama 로컬 LLM(무료) + Gemini API Free(15 RPM) + Groq Free(Llama 70B, 30 RPM) + Mistral Free. 품질: 유료 대비 ~70%, 속도 제한 있음. 적합: 가벼운 사용, 학습용, 프라이버시 중시 사용자
- **기술 스택**: 무료 API 통합, Ollama 로컬 모델, Fallback 체인
- **VAMOS 연동**: Model Router(S7F-003) Free Tier 라우팅, Fallback Chain(S7F-004)
- **V1**: 무료 조합 최적화 + 문서화 → **V2**: 무료 사용자 경험 개선 → **V3**: 무료→유료 자연스러운 전환 경로

### S7H-007 | MED | V2 | B2B 가격 전략 — 기업 판매 가격 모델

- **모듈 연동**: H(비즈니스) - B2B 전략
- **구현 방식**: V3 기업 판매 시 가격 책정 전략 수립. 사용자 수 기반($15-30/user/mo) 또는 사용량 기반 과금. 볼륨 디스카운트, 연간 계약 할인, 커스텀 SLA 포함
- **기술 스택**: 가격 모델링 스프레드시트, 경쟁사 B2B 가격 조사
- **VAMOS 연동**: Team 버전(V3), 기업 라이선스(S7H-023)
- **V1**: 시장 조사 → **V2**: B2B 가격 모델 설계 → **V3**: 기업 영업 시작

### S7H-008 | MED | V2 | 가격 탄력성 분석 — 최적 가격점 결정

- **모듈 연동**: H(비즈니스) - 가격 최적화
- **구현 방식**: 타겟 사용자의 가격 민감도를 Van Westendorp Price Sensitivity Meter로 분석. 예상 최적 가격점: $10-15/mo(한국 시장). 한국 시장은 $20/mo 구독에 대한 저항이 크므로 저가 전략 필수
- **기술 스택**: 서베이 도구, 통계 분석(Van Westendorp 모델)
- **VAMOS 연동**: 가격 전략(S7H-011), 타겟 페르소나(S7H-027~034)
- **V1**: 정성적 분석 → **V2**: 사용자 설문 기반 정량 분석 → **V3**: A/B 가격 테스트

### S7H-009 | MED | V2 | 프리미엄 기능 정의 — Free vs Paid 경계

- **모듈 연동**: H(비즈니스) - 제품 전략
- **구현 방식**: 무료와 유료의 기능 경계 설정. Free: 로컬 LLM, 기본 메모리(L0-L2), 기본 Tool. Premium: 클라우드 LLM, 고급 Agent, 무제한 메모리(L0-L4), Priority 지원. 전환 유도: 무료 기능의 자연스러운 한계 경험 → 유료 기능 필요성 인지
- **기술 스택**: Feature Flagging 시스템, 사용량 제한 엔진
- **VAMOS 연동**: 티어 관리 시스템, 비용 Gate(S7F-003)
- **V1**: Free/Paid 기능 목록 정의 → **V2**: 동적 Feature Flag 구현 → **V3**: 기업별 커스텀 티어

### S7H-010 | MED | V2 | 번들 전략 — 패키지 구성

- **모듈 연동**: H(비즈니스) - 제품 전략
- **구현 방식**: 기능별 번들 패키지 설계. Personal: $0 / Pro: $10/mo / Power: $20/mo / Team: $15/user/mo. 각 번들별 포함 기능, API 크레딧, 지원 수준 차별화
- **기술 스택**: 구독 관리 시스템(V2), Stripe/Paddle 결제 통합
- **VAMOS 연동**: SaaS 구독 모델(S7H-020), 프리미엄 기능(S7H-009)
- **V1**: 번들 설계 문서화 → **V2**: 구독 시스템 구현 → **V3**: 기업 커스텀 번들

---

## H-Part 2: VAMOS 가격 전략 (8건)

### H-Part 2 가격 전략 구조

```
┌────────────────────────────────────────────────────────────┐
│                   VAMOS Pricing Strategy                     │
├────────────────────────────────────────────────────────────┤
│  Tier 0: VAMOS Free        → $0/mo (로컬+무료API)         │
│  Tier 1: VAMOS Core        → $0+API (사용한 만큼)          │
│  Tier 2: VAMOS Pro (V2)    → $15/mo (서버+크레딧)          │
│  Tier 3: VAMOS Team (V3)   → $20/user/mo (팀+관리)        │
└────────────────────────────────────────────────────────────┘
```

---

### S7H-011 | CRITICAL | V1 | Pay-as-you-go 핵심 전략 — 사용한 만큼만

- **모듈 연동**: H(비즈니스), I(Infra Core) - 핵심 가치 제안
- **구현 방식**: VAMOS V1의 핵심 가치 제안: "구독이 아닌, 사용한 만큼만". ChatGPT Plus/Claude Pro: $20/mo 고정(안 써도 $20). VAMOS: API 사용량 x 단가(안 쓰면 $0). 월 100회 질문 시 ChatGPT $20(회당 $0.20) vs VAMOS ~$3(회당 $0.03, 스마트 라우팅) → 6.7배 비용 효율. 월 1000회 시 ChatGPT $20(회당 $0.02) vs VAMOS ~$8(회당 $0.008) → 2.5배 효율
- **기술 스택**: 요청별 비용 계산기, 실시간 비용 추적 로그, 비용 대시보드
- **VAMOS 연동**: Model Router(S7F-003) 비용 최적 라우팅, Cost Gate(5-Gate System), 비용 투명성(S7H-012)
- **V1**: Pay-as-you-go 핵심 구현(사용자 API 키) → **V2**: VAMOS Proxy(마진 모델) → **V3**: 기업 계약 가격

### S7H-012 | CRITICAL | V1 | 비용 투명성 — 경쟁 차별화 핵심

- **모듈 연동**: I(Infra Core), S(Service Layer) - 비용 UI
- **구현 방식**: 모든 요청의 비용을 실시간으로 투명하게 공개. 요청 전: "이 작업의 예상 비용: ₩15~25". 요청 후: "사용 비용: ₩18 (Claude Sonnet, 1500→800 tokens)". 대시보드: 일/주/월 비용, 모델별 분포, 절감 내역. 절감 리포트: "스마트 라우팅으로 이번 달 ₩12,000 절감". 경쟁 AI 서비스 중 이 수준의 비용 투명성을 제공하는 서비스 없음
- **기술 스택**: 토큰 카운터(tiktoken), 비용 로거(cost.log), React 비용 대시보드, 비용 추이 차트
- **VAMOS 연동**: 모든 LLM 호출 경로(S7F-001~003), Prompt Caching(S7F-006), 비용 제어(S7H-013)
- **V1**: 요청별 비용 표시 + 일/월 요약 → **V2**: 고급 분석 대시보드 + 절감 리포트 → **V3**: 기업 비용 센터 관리

### S7H-013 | CRITICAL | V1 | 비용 제어 — 사용자가 완전히 통제

- **모듈 연동**: I(Infra Core), S(Service Layer) - 5-Gate System
- **구현 방식**: 사용자가 AI 비용을 완전히 통제할 수 있는 시스템. 기능: 일/월 예산 하드캡 설정, 요청당 비용 상한 설정, 비용 경고 임계값(80%, 90%, 100%), 예산 소진 시 로컬 LLM으로 자동 전환, 사용 패턴 분석 → 비용 절감 추천. 핵심 메시지: "절대 예상치 못한 AI 비용 청구 없음"
- **기술 스택**: Cost Gate 엔진(Rust), 예산 관리 DB(SQLite), 알림 시스템, 사용 패턴 분석기
- **VAMOS 연동**: 5-Gate System Cost Gate, Model Router(S7F-003) 비용 기반 라우팅, Fallback Chain(S7F-004) 무료 모델 전환
- **V1**: 일/월 예산 + 경고 + 자동 전환 → **V2**: 사용 패턴 AI 분석 + 절감 추천 → **V3**: 기업 부서별 예산 관리

### S7H-014 | HIGH | V1 | 데이터 주권 가치 — 프라이버시 프리미엄

- **모듈 연동**: H(비즈니스), E(Security Layer) - 마케팅 메시지
- **구현 방식**: 100% 로컬 데이터 보관의 가치 제안. "당신의 데이터는 당신의 컴퓨터에만 존재합니다", "어떤 AI 회사도 당신의 대화를 학습하지 않습니다", "완전한 데이터 소유권 + 삭제 권리". 경쟁사 비교: ChatGPT/Claude — 데이터 서버 저장, opt-out 필요, 삭제 요청 필요, 이동 제한적. VAMOS — 사용자 로컬, 절대 미학습, 즉시 완전 삭제, 완전 포터빌리티
- **기술 스택**: SQLCipher(암호화 DB), E2E 데이터 흐름, PII 마스킹(API 호출 시)
- **VAMOS 연동**: 로컬 저장소(S7F-013), PII 마스킹(STEP7-E), 보안 체계 전체
- **V1**: 로컬 데이터 보관 + PII 마스킹 → **V2**: 데이터 export/import + 암호화 백업 → **V3**: 기업 데이터 거버넌스

### S7H-015 | HIGH | V1 | 오픈소스 전략 — 코어 무료, 프리미엄 유료

- **모듈 연동**: H(비즈니스) - 제품 전략
- **구현 방식**: 오픈소스 코어 + 프리미엄 서비스 모델. 오픈소스(MIT/Apache 2): VAMOS Core Engine, 기본 Agent Framework, 메모리/RAG 파이프라인, UI 컴포넌트. 프리미엄(V2+): 클라우드 호스팅, 프리미엄 MCP Tool 마켓, 기업 관리 기능, 우선 기술 지원. 이점: 커뮤니티 신뢰, 투명성, 기여자 생태계, 빠른 혁신
- **기술 스택**: GitHub(코드 관리), Open Collective/GitHub Sponsors(후원), 라이선스 관리
- **VAMOS 연동**: 전체 코어 시스템, MCP Tool 마켓(S7H-021), 커뮤니티(S7H-046)
- **V1**: 오픈소스 공개 + 문서 정비 → **V2**: 프리미엄 서비스 런칭 → **V3**: 기업 라이선스

### S7H-016 | HIGH | V1 | 초기 사용자 확보 — Launch 전략

- **모듈 연동**: H(비즈니스) - GTM
- **구현 방식**: V1 출시 시 초기 사용자 확보 전략. 채널: GitHub 공개(Star 캠페인), Product Hunt 런칭, 한국 개발자 커뮤니티(GeekNews, OKKY, 디스코드), AI 관련 서브레딧(r/LocalLLaMA, r/ChatGPT), 한국 AI 유튜브/블로그 리뷰. 목표: V1 출시 3개월 내 1,000 GitHub Stars, 500 활성 사용자
- **기술 스택**: GitHub README 최적화, 랜딩 페이지, 디스코드 커뮤니티
- **VAMOS 연동**: 콘텐츠 마케팅(S7H-050), 데모/쇼케이스(S7H-052)
- **V1**: 무비용 런칭 캠페인 → **V2**: 유기적 성장 가속 → **V3**: 유료 확장

### S7H-017 | MED | V2 | 프리미엄 전환율 — Free → Paid 전략

- **모듈 연동**: H(비즈니스) - 수익화
- **구현 방식**: 무료 사용자의 유료 전환 전략. 전환 트리거: 로컬 LLM 한계 경험 → 클라우드 API 추천, 고급 기능 필요 → Pro 티어 안내, 데이터 동기화 필요 → 서버 티어 안내. 목표 전환율: 5-10%(SaaS 평균 2-5%)
- **기술 스택**: 전환 퍼널 분석, A/B 테스트 프레임워크, 인앱 업그레이드 UI
- **VAMOS 연동**: 프리미엄 기능(S7H-009), 번들 전략(S7H-010), 사용자 여정(S7H-032)
- **V1**: 전환 트리거 포인트 정의 → **V2**: 인앱 업그레이드 플로우 구현 → **V3**: ML 기반 전환 예측

### S7H-018 | MED | V2 | 파트너십 수익 — API 프로바이더 제휴

- **모듈 연동**: H(비즈니스) - 제휴 전략
- **구현 방식**: LLM API 제공사와 제휴 수익 가능성 탐색. 모델: 리퍼럴 수수료(VAMOS를 통한 API 사용량 수수료), 볼륨 할인(대량 사용 시 할인 협상 → 마진 확보), 공동 마케팅("Powered by Claude" 등)
- **기술 스택**: 파트너 계약 관리, API 사용량 어트리뷰션 추적
- **VAMOS 연동**: API 호출 경로(S7F-002), Model Gateway(S7F-008), 비용 추적
- **V1**: 파트너십 가능성 조사 → **V2**: 1-2개 프로바이더 제휴 체결 → **V3**: 멀티 파트너 프로그램

---

## H-Part 3: 수익 모델 설계 (8건)

### H-Part 3 수익 구조 개요

```
Stream 1: API 마진 (V1~)     → $1-2/user/mo
Stream 2: 프리미엄 구독 (V2~) → $15-20/user/mo
Stream 3: MCP Tool 마켓 (V2~) → $2-5/user/mo
Stream 4: 기업 라이선스 (V3~) → $500-5000/mo/기업
Stream 5: 교육/인증 (V3~)     → 부가 수익
```

---

### S7H-019 | CRITICAL | V1 | API 마진 모델 — V1 수익화 시작점

- **모듈 연동**: I(Infra Core), H(비즈니스) - 핵심 수익
- **구현 방식**: VAMOS를 통한 API 호출에 소폭 마진 부과. 직접 API: 사용자가 자기 API 키 입력 → 마진 $0(V1 기본). VAMOS Proxy: VAMOS API 키 사용 → 10-20% 마진. 가치: 사용자는 멀티 모델을 단일 키로 사용하는 편의. 예상: 1000 사용자 x $1.5/mo = $1,500/mo
- **기술 스택**: API Proxy 서버, 사용량 미터링, 마진 계산 엔진
- **VAMOS 연동**: Model Gateway(S7F-008), 비용 투명성(S7H-012), Pay-as-you-go(S7H-011)
- **V1**: 사용자 API 키 직접 사용(마진 $0) → **V2**: VAMOS Proxy 옵션(10-20% 마진) → **V3**: 기업 전용 프록시

### S7H-020 | CRITICAL | V2 | SaaS 구독 모델 — V2 핵심 수익

- **모듈 연동**: H(비즈니스), I(Infra Core) - SaaS 플랫폼
- **구현 방식**: 클라우드 호스팅 + API 크레딧 번들 구독. Free: $0(로컬 전용, 무료 API만). Core: $0+API(자기 API 키). Pro: $15(서버 호스팅 + $10 크레딧). Power: $25(Pro + 고급 Agent + 우선 지원). Team: $20/user(Power + 팀 공유 + 관리)
- **기술 스택**: Stripe/Paddle 결제, 구독 관리 시스템, 크레딧 시스템, 사용량 미터링
- **VAMOS 연동**: V2 서버 인프라(S7F Part 3), 번들 전략(S7H-010), 프리미엄 기능(S7H-009)
- **V1**: 설계 완료 → **V2**: SaaS 런칭 + 결제 통합 → **V3**: 기업 커스텀 플랜

### S7H-021 | HIGH | V2 | MCP Tool 마켓플레이스 — 도구 생태계 수익

- **모듈 연동**: A(Agent Layer), H(비즈니스) - 플랫폼 수익
- **구현 방식**: 서드파티 MCP Tool 판매 플랫폼. 무료 Tool: 커뮤니티 기여(오픈소스). 프리미엄 Tool: 유료 판매(70% 개발자 / 30% VAMOS). 기업 전용 Tool: 커스텀 개발. 예시: 고급 웹 스크래핑($3/mo), 금융 데이터 분석($5/mo), 법률 문서 검토($5/mo)
- **기술 스택**: MCP Tool Registry, 마켓플레이스 UI, 결제 통합, 개발자 대시보드
- **VAMOS 연동**: MCP Tool 시스템(Agent Layer), 생태계 성장(S7H-059)
- **V1**: 핵심 Tool 30개 자체 개발 → **V2**: 마켓플레이스 런칭 + 서드파티 개방 → **V3**: 기업 전용 Tool 스토어

### S7H-022 | HIGH | V2 | 프리미엄 Agent 패키지 — 전문 Agent 유료화

- **모듈 연동**: A(Agent Layer), H(비즈니스) - 부가 수익
- **구현 방식**: 전문 분야 Agent를 프리미엄으로 제공. Developer Pro: 고급 코딩 Agent(코드 리뷰, 아키텍처, CI/CD). Quant Pro: 고급 투자 분석 Agent(기업 분석, 포트폴리오). Content Pro: 고급 콘텐츠 Agent(SEO, 소셜 미디어, 번역). 가격: $5-10/mo 추가
- **기술 스택**: Agent 패키지 관리, 라이선스 시스템, 기능 게이팅
- **VAMOS 연동**: BLUE NODEs(Agent Layer), 크로스 셀(S7H-061)
- **V1**: Agent 기본 기능 → **V2**: 프리미엄 Agent 차별화 + 과금 → **V3**: 기업 맞춤 Agent

### S7H-023 | HIGH | V2 | 기업 라이선스 — B2B 수익

- **모듈 연동**: H(비즈니스) - B2B 수익
- **구현 방식**: 기업 고객을 위한 온프레미스/프라이빗 클라우드 라이선스. 가격: $500-5,000/mo(규모에 따라). 포함: 전용 배포, SLA, 커스텀 Agent, 전담 지원
- **기술 스택**: 라이선스 관리 시스템, 온프레미스 배포 패키지, SLA 모니터링
- **VAMOS 연동**: V3 엔터프라이즈 인프라, B2B 가격 전략(S7H-007), 엔터프라이즈 세일즈(S7H-064)
- **V1**: B2B 시장 조사 → **V2**: 라이선스 모델 설계 → **V3**: 기업 영업 + 전용 배포

### S7H-024 | HIGH | V2 | 데이터 분석 인사이트 — 익명화된 사용 패턴

- **모듈 연동**: H(비즈니스), E(Security Layer) - 부가 수익
- **구현 방식**: 익명화된 집계 데이터에서 AI 사용 트렌드 인사이트 제공. 완전 익명화, 사용자 동의 필수, GDPR 준수. 수익: 산업 리포트 판매, API 가격 추이 분석
- **기술 스택**: 익명화 파이프라인(k-anonymity, differential privacy), 집계 분석 엔진
- **VAMOS 연동**: 사용 로그(S7F Part 4), 보안 체계(STEP7-E), 프라이버시 규정 준수
- **V1**: 데이터 수집 동의 프레임워크 설계 → **V2**: 익명화 파이프라인 구현 → **V3**: 인사이트 리포트 판매

### S7H-025 | MED | V3 | 교육 / 인증 프로그램 — 지식 수익화

- **모듈 연동**: H(비즈니스) - 부가 수익
- **구현 방식**: VAMOS 사용법, AI 비서 구축 교육 프로그램. 형태: 온라인 코스, 워크숍, 인증 프로그램. 파트너: 한국 AI 교육 기관, 대학, 기업 교육
- **기술 스택**: LMS(학습 관리 시스템), 인증 발급 시스템
- **VAMOS 연동**: 투자 온보딩(S7I-106), 커뮤니티(S7H-046)
- **V1**: 문서/튜토리얼 → **V2**: 온라인 코스 개설 → **V3**: 인증 프로그램 + 기업 교육

### S7H-026 | MED | V3 | 화이트 라벨 — 기업 브랜딩 제공

- **모듈 연동**: H(비즈니스) - B2B 고급
- **구현 방식**: VAMOS 엔진을 기업 브랜드로 제공. 대상: AI 비서를 원하지만 자체 개발 역량 없는 기업. 가격: 셋업비 + 월 라이선스
- **기술 스택**: 화이트 라벨 빌드 시스템, 테마/브랜딩 커스터마이징 엔진
- **VAMOS 연동**: 기업 라이선스(S7H-023), 엔터프라이즈 인프라(V3)
- **V1**: 해당 없음 → **V2**: 화이트 라벨 가능성 조사 → **V3**: 화이트 라벨 서비스 런칭

---

## H-Part 4: 타겟 페르소나 (8건)

### H-Part 4 핵심 타겟 페르소나 개요

```
P1: 테크 얼리어답터 개발자 (Primary)  — 25-40세, 오픈소스/CLI 선호
P2: 생산성 추구 지식 노동자 (Secondary) — 28-45세, 비용 불만
P3: AI 투자자 / 트레이더 (Niche)      — 30-50세, 다중 정보원
P4: 프라이버시 중시 사용자 (Niche)     — 전 연령, VPN/오픈소스
P5: 소규모 팀/스타트업 (V2~)          — 3-20명, SaaS 비용 민감
```

---

### S7H-027 | CRITICAL | V1 | P1: 테크 얼리어답터 — 핵심 초기 사용자

- **모듈 연동**: H(비즈니스) - 타겟 전략
- **구현 방식**: 기술에 능숙한 개발자/엔지니어를 초기 핵심 사용자로 확보. 접근: GitHub 공개 + 상세 기술 문서, Hacker News/Product Hunt 런칭, r/LocalLLaMA/r/SelfHosted 커뮨니티, 한국: GeekNews/OKKY/디스코드. 확보 목표: V1 출시 후 6개월 내 2,000 활성 사용자. 핵심 메시지: "당신이 만드는 AI 비서, 코드가 공개되어 있습니다"
- **기술 스택**: GitHub README/Wiki, 기술 블로그, 디스코드 봇
- **VAMOS 연동**: 오픈소스 전략(S7H-015), GTM Phase 1(S7H-049), 콘텐츠 마케팅(S7H-050)
- **V1**: 개발자 커뮤니티 집중 → **V2**: 사용자 기반 확대 → **V3**: 엔터프라이즈 개발팀

### S7H-028 | CRITICAL | V1 | P2: 생산성 추구 지식 노동자 — 주 타겟

- **모듈 연동**: H(비즈니스) - 타겟 전략
- **구현 방식**: ChatGPT/Claude 유료 구독자 중 비용에 민감한 사용자. 접근: "ChatGPT Plus보다 저렴하고 더 개인화된 AI", 비용 비교 콘텐츠 마케팅, 한국 생산성 커뮤니티(노션/투두이스트 사용자), YouTube/블로그 리뷰 + 튜토리얼. 핵심 메시지: "월 $20 → $5~10으로 더 나은 AI 경험"
- **기술 스택**: 랜딩 페이지, 비교 콘텐츠, 온보딩 가이드
- **VAMOS 연동**: 비용 투명성(S7H-012), TCO 분석(S7H-005), 비교 콘텐츠(S7H-045)
- **V1**: 비용 비교 마케팅 → **V2**: 쉬운 사용성 + 웹 접근 → **V3**: 기업 생산성 통합

### S7H-029 | HIGH | V1 | P3: AI 투자자 — 니치 고가치 사용자

- **모듈 연동**: H(비즈니스) - 타겟 전략
- **구현 방식**: AI를 투자 분석에 활용하는 투자자. 접근: 투자 커뮤니티(증권 갤러리, 퀀트 커뮤니티), 투자 유튜브 채널 협업, 실제 투자 분석 데모 시연. 핵심 메시지: "프로 투자자의 AI 파트너, 데이터는 안전하게"
- **기술 스택**: 투자 분석 데모, Quant Node 쇼케이스
- **VAMOS 연동**: STEP7-I 전체(AI Investing), Quant Node(Agent Layer), 투자 온보딩(S7I-106)
- **V1**: 투자 커뮤니티 마케팅 → **V2**: 프리미엄 Quant Pro 패키지 → **V3**: 기관 투자자 서비스

### S7H-030 | HIGH | V1 | P4: 프라이버시 중시 사용자 — 차별화 타겟

- **모듈 연동**: H(비즈니스) - 타겟 전략
- **구현 방식**: 데이터 프라이버시를 최우선시하는 사용자. 접근: 프라이버시 포커스 커뮤니티(Privacy Tools, EFF), EU 사용자(GDPR 강조), 의료/법률/금융 전문가(민감 데이터). 핵심 메시지: "당신의 AI 대화는 당신의 것입니다"
- **기술 스택**: 보안 아키텍처 문서, 데이터 흐름 투명성 페이지
- **VAMOS 연동**: 데이터 주권(S7H-014), 보안 체계(STEP7-E), 로컬 저장소(S7F-013)
- **V1**: 프라이버시 마케팅 → **V2**: 보안 감사 결과 공개 → **V3**: 규제 인증(SOC2, GDPR)

### S7H-031 | HIGH | V2 | P5: 소규모 팀 — V2 확장 타겟

- **모듈 연동**: H(비즈니스) - 타겟 전략
- **구현 방식**: 3-20명 규모 팀/스타트업을 위한 팀 버전. 가치: 팀원당 $20/mo < 개별 ChatGPT Plus $20/mo x N명. 추가 가치: 공유 지식 베이스, 팀 Agent, 관리 기능
- **기술 스택**: 팀 관리 시스템, 공유 메모리, 권한 관리
- **VAMOS 연동**: Team 가격(S7H-020), 기업 라이선스(S7H-023)
- **V1**: 팀 니즈 조사 → **V2**: 팀 버전 출시 → **V3**: 중대형 기업 확장

### S7H-032 | HIGH | V1 | 사용자 여정 맵 — User Journey

- **모듈 연동**: H(비즈니스) - UX 전략
- **구현 방식**: 인지 → 관심 → 설치 → 활성화 → 유지 → 추천 여정 설계. 1) 인지: GitHub/블로그. 2) 관심: 랜딩 페이지(저렴+프라이버시). 3) 설치: 원클릭 인스톨러(5분). 4) 활성화: 온보딩 가이드(첫 대화). 5) Aha Moment: 맞춤 답변(1주). 6) 유지: 매일 사용(2주 리텐션 80%). 7) 추천: NPS 50+ 목표
- **기술 스택**: 사용자 분석(Plausible/PostHog 셀프호스팅), 온보딩 플로우, NPS 서베이
- **VAMOS 연동**: 설치 시스템(S7F-011), 온보딩(S7F Part 2), 이탈 방지(S7H-034)
- **V1**: 여정 설계 + 핵심 Aha Moment 최적화 → **V2**: 전체 퍼널 분석 → **V3**: ML 기반 개인화 여정

### S7H-033 | MED | V2 | 사용자 세그먼트별 기능 우선순위

- **모듈 연동**: H(비즈니스) - 제품 전략
- **구현 방식**: 각 페르소나별 가장 중요한 기능 매핑. P1 개발자: 멀티 모델(5), 코딩 Agent(5), 로컬 데이터(4). P2 지식노동자: 비용 투명성(5), 개인화 메모리(5). P3 투자자: 비용 투명성(5), 투자 Agent(5). P4 프라이버시: 로컬 데이터(5), 오프라인(5)
- **기술 스택**: 기능 우선순위 매트릭스, RICE 스코어링
- **VAMOS 연동**: 전체 페르소나(S7H-027~031), 프리미엄 기능(S7H-009)
- **V1**: 기능 우선순위 정의 → **V2**: 세그먼트별 온보딩 분기 → **V3**: 동적 기능 추천

### S7H-034 | MED | V2 | 이탈 방지 — Churn Prevention

- **모듈 연동**: H(비즈니스) - 리텐션
- **구현 방식**: 사용자 이탈 예측 및 방지 전략. 이탈 신호: 사용 빈도 감소, 에러 빈도 증가, 피드백 부정적. 대응: 개선 제안 푸시, 새 기능 안내, 사용 팁 제공
- **기술 스택**: 사용 패턴 분석, 이탈 예측 모델(V2), 자동 인게이지먼트 시스템
- **VAMOS 연동**: 사용자 여정(S7H-032), 리텐션 전략(S7H-060)
- **V1**: 이탈 신호 정의 → **V2**: 자동 대응 시스템 구현 → **V3**: ML 기반 이탈 예측

---

## H-Part 5: 시장 규모 분석 (6건)

### H-Part 5 AI 시장 규모 (2024-2030)

| 시장 | 2024 | 2025E | 2027E | 2030E | CAGR |
|------|------|-------|-------|-------|------|
| 글로벌 AI 전체 | $214B | $300B | $530B | $1.3T | 36% |
| AI 소프트웨어 | $64B | $90B | $160B | $400B | 35% |
| AI Assistant/Chatbot | $5B | $8B | $15B | $40B | 40% |
| AI 코딩 도구 | $3B | $5B | $10B | $25B | 42% |
| LLM API 시장 | $4B | $7B | $15B | $35B | 43% |

---

### S7H-035 | HIGH | V1 | TAM/SAM/SOM — 시장 규모 단계별 산출

- **모듈 연동**: H(비즈니스) - 시장 분석
- **구현 방식**: VAMOS의 접근 가능 시장 규모 분석. TAM: 글로벌 AI 비서/챗봇 ~$8B(2025), 한국 ~$240M. SAM: 개인용 AI 비서(구독/API) ~$2B, 한국 ~$60M, 타겟 세그먼트 ~$30M. SOM: V1(1년차) 5,000 사용자 x $10/mo = $600K/yr, V2(2년차) 30,000 x $12/mo = $4.3M/yr, V3(3년차) 100,000 + 기업 = $15M/yr
- **기술 스택**: 시장 조사 리포트(Gartner, IDC 참조), 자체 추정 모델
- **VAMOS 연동**: 성장 시나리오(S7H-037), 재무 모델링(S7H-073~078)
- **V1**: TAM/SAM/SOM 초기 추정 → **V2**: 실제 데이터 기반 보정 → **V3**: 글로벌 시장 확장

### S7H-036 | HIGH | V1 | 한국 AI 시장 특수성 — 한국 시장 분석

- **모듈 연동**: H(비즈니스) - 시장 분석
- **구현 방식**: 한국 AI 시장의 특수한 요소 분석. 한국어 AI 품질 요구 높음(존댓말, 문화 맥락), 가격 민감도 높음($20/mo 저항), 프라이버시 의식 증가(개인정보보호법), 높은 기술 접근성, 주식/코인 투자 인구 다수, 네이버/카카오 AI 경쟁(HyperCLOVA X, Kanana)
- **기술 스택**: 한국 시장 조사, 사용자 인터뷰, 경쟁사 분석
- **VAMOS 연동**: 한국어 벤치마크(S7G Part 2), 한국 시장 특화(S7I Part 4)
- **V1**: 한국 시장 특수성 반영(한국어 최적화, 저가 전략) → **V2**: 한국 시장 검증 → **V3**: 글로벌 확장

### S7H-037 | HIGH | V1 | 성장 시나리오 — 낙관/기준/비관

- **모듈 연동**: H(비즈니스) - 재무 전략
- **구현 방식**: 3가지 성장 시나리오 모델링. 비관: Y1 1K/Y2 5K/Y3 15K 사용자, Y1 $120K/Y2 $720K/Y3 $2.2M 매출. 기준: Y1 5K/Y2 30K/Y3 100K, Y1 $600K/Y2 $4.3M/Y3 $15M. 낙관: Y1 20K/Y2 100K/Y3 500K, Y1 $2.4M/Y2 $14.4M/Y3 $75M
- **기술 스택**: 재무 모델 스프레드시트, 시나리오 분석 도구
- **VAMOS 연동**: TAM/SAM/SOM(S7H-035), 재무 모델링(S7H-073~078)
- **V1**: 3개 시나리오 수립 → **V2**: 실적 기반 시나리오 조정 → **V3**: 투자자 리포팅

### S7H-038 | HIGH | V2 | 경쟁 구도 분석 — 5 Forces 분석

- **모듈 연동**: H(비즈니스) - 경쟁 분석
- **구현 방식**: Porter's Five Forces 분석. 기존 경쟁자 위협: HIGH(ChatGPT, Claude, Gemini). 신규 진입자 위협: HIGH(오픈소스 진입 장벽 낮음). 대체재 위협: MED(각 서비스 직접 사용). 공급자 교섭력: HIGH(LLM API 소수 제공자). 구매자 교섭력: HIGH(전환 비용 낮음). 전략: 차별화(개인화+비용+프라이버시)로 경쟁 우위 확보
- **기술 스택**: 경쟁 분석 프레임워크, 정기 모니터링
- **VAMOS 연동**: 핵심 차별화(S7H-041), MOAT 분석(S7H-043)
- **V1**: 초기 5 Forces 분석 → **V2**: 분기별 업데이트 → **V3**: 경쟁 인텔리전스 시스템

### S7H-039 | MED | V2 | 기업 시장 규모 — B2B 기회 분석

- **모듈 연동**: H(비즈니스) - B2B 전략
- **구현 방식**: 기업용 AI 비서 시장 규모 및 기회 분석. Microsoft 365 Copilot($30/user/mo) 시장 참조. VAMOS 기회: 중소기업 대상 저가 대안($20/user/mo)
- **기술 스택**: B2B 시장 조사, 경쟁사 가격 분석
- **VAMOS 연동**: 기업 라이선스(S7H-023), B2B 가격(S7H-007), 엔터프라이즈 세일즈(S7H-064)
- **V1**: B2B 시장 조사 → **V2**: 파일럿 고객 확보 → **V3**: B2B 본격 영업

### S7H-040 | MED | V2 | 지역 확장 전략 — 한국 → 글로벌

- **모듈 연동**: H(비즈니스) - 글로벌 전략
- **구현 방식**: 한국 시장 검증 후 글로벌 확장 로드맵. 1) 한국(Y1): 한국어 최적화, 한국 커뮤니티. 2) 일본(Y2): 일본어 지원, 프라이버시 중시. 3) 동남아(Y2-3): 영어 기반, 비용 절감 어필. 4) 유럽(Y3): GDPR 준수, 데이터 주권. 5) 북미(Y3+): 최대 시장, 영어 품질 최고 수준
- **기술 스택**: i18n 프레임워크, 현지화(L10n) 파이프라인, 지역별 배포
- **VAMOS 연동**: 국제화(S7H-063), 한국어 벤치마크(S7G Part 2)
- **V1**: 한국 + 영어 기본 → **V2**: 일본어 추가 + 지역 확장 시작 → **V3**: 4개 지역 동시 운영

---

## H-Part 6: 경쟁 포지셔닝 (8건)

### H-Part 6 포지셔닝 맵

```
             HIGH CUSTOMIZATION
                    │
    VAMOS ★         │
    (저비용+         │     Notion AI
     개인화)         │     (생산성 통합)
                    │
LOW COST ───────────┼───────────── HIGH COST
                    │
    Ollama          │     ChatGPT Plus
    (무료 로컬)      │     Claude Pro
                    │     ($20/mo)
             LOW CUSTOMIZATION
```

---

### S7H-041 | CRITICAL | V1 | 핵심 차별화 포지션 — "개인화된 AI 비서"

- **모듈 연동**: H(비즈니스) - 핵심 전략
- **구현 방식**: VAMOS의 핵심 포지셔닝 정의. For: AI를 일상적으로 사용하는 테크 사용자와 지식 노동자. Who: ChatGPT/Claude 구독 비용이 아깝거나 데이터 프라이버시가 걱정되는 사용자. VAMOS is: 자기진화하는 개인 AI 비서. That: 사용할수록 나를 더 잘 이해하고, 비용은 사용한 만큼만. Unlike: ChatGPT/Claude(고정 구독, 제한적 개인화, 클라우드 데이터). Our product: 멀티 모델 스마트 라우팅 + 5-Layer 메모리 + 완전한 데이터 주권
- **기술 스택**: 브랜딩 가이드, 메시지 프레임워크, 비주얼 아이덴티티
- **VAMOS 연동**: 전체 시스템의 핵심 가치 제안 — 모든 기능/마케팅의 기반
- **V1**: 포지션 스테이트먼트 확정 + 일관된 메시지 → **V2**: 브랜드 인지도 구축 → **V3**: 시장 리더십

### S7H-042 | CRITICAL | V1 | 경쟁 비교 매트릭스 — 전수비교

- **모듈 연동**: H(비즈니스) - 경쟁 분석
- **구현 방식**: 모든 경쟁 AI 서비스와의 차별점 매트릭스. 비용 모델: 경쟁사 $20 고정 vs VAMOS 사용량 기반. 비용 투명성: 경쟁사 없음 vs VAMOS 완전 투명. 멀티 모델: 경쟁사 자사 모델만 vs VAMOS 모든 모델. 개인화 메모리: 경쟁사 제한 vs VAMOS 5-Layer. Knowledge Graph: 경쟁사 없음 vs VAMOS 개인 KG. 데이터: 경쟁사 클라우드 vs VAMOS 100% 로컬. 자기진화/오픈소스/Agent Teams/비용 제어/오프라인 모두 VAMOS 차별화
- **기술 스택**: 비교 매트릭스 문서, 정기 업데이트 프로세스
- **VAMOS 연동**: 핵심 차별화(S7H-041), 비교 콘텐츠(S7H-045)
- **V1**: 비교 매트릭스 작성 + 분기 갱신 → **V2**: 동적 비교 페이지 → **V3**: AI 기반 자동 비교 업데이트

### S7H-043 | HIGH | V1 | MOAT 분석 — 경쟁 방어벽

- **모듈 연동**: H(비즈니스) - 전략 분석
- **구현 방식**: VAMOS의 지속 가능한 경쟁 우위 분석. Switching Cost(4/5): 개인화된 5-Layer 메모리 + KG는 전환 어려움, 사용할수록 데이터 축적. Network Effect(2/5): 개인 도구라 약함 → V2 MCP Tool 마켓으로 간접 효과. Intangible Assets(3/5): 오픈소스 커뮤니티, 브랜드 → 커뮤니티 기여 강화. Cost Advantage(5/5): 스마트 라우팅 60-70% 비용 절감. Efficient Scale(2/5): 아직 작음 → 볼륨 할인 추구
- **기술 스택**: 전략 분석 프레임워크, 경쟁 모니터링
- **VAMOS 연동**: 5-Layer 메모리(STEP7-B), Knowledge Graph(STEP7-C), Model Router(S7F-003)
- **V1**: MOAT 구축 시작(메모리+비용 우위) → **V2**: 네트워크 효과 강화(Tool 마켓) → **V3**: 전방위 방어벽

### S7H-044 | HIGH | V1 | 핵심 메시지 3개 — 마케팅 메시지

- **모듈 연동**: H(비즈니스) - 마케팅
- **구현 방식**: VAMOS의 3가지 핵심 마케팅 메시지 정의. 1) "사용한 만큼만 지불하세요" — 비용 절감(ChatGPT Plus $20/mo → VAMOS $5~10/mo). 2) "AI가 당신을 기억합니다" — 개인화(사용할수록 더 나아지는 자기진화 비서). 3) "데이터는 당신의 것입니다" — 프라이버시(100% 로컬, 오픈소스, 완전 소유권)
- **기술 스택**: 카피라이팅 가이드, A/B 테스트(V2)
- **VAMOS 연동**: 포지셔닝(S7H-041), 비용 투명성(S7H-012), 데이터 주권(S7H-014)
- **V1**: 메시지 확정 + 전 채널 일관 적용 → **V2**: A/B 테스트로 메시지 최적화 → **V3**: 지역별 맞춤 메시지

### S7H-045 | HIGH | V1 | 비교 콘텐츠 전략 — "vs ChatGPT" 콘텐츠

- **모듈 연동**: H(비즈니스) - 콘텐츠 마케팅
- **구현 방식**: 비교 콘텐츠로 검색 유입 확보. "VAMOS vs ChatGPT Plus: 월 $15 절약하는 법", "VAMOS vs Claude Pro: 어떤 게 더 나을까?", "AI 비서 비용 비교: 2025 완전 가이드", "ChatGPT 구독 해지하고 VAMOS로 전환한 후기"
- **기술 스택**: 블로그(Hugo/Next.js), SEO 최적화, 키워드 리서치
- **VAMOS 연동**: 경쟁 매트릭스(S7H-042), 핵심 메시지(S7H-044), 콘텐츠 마케팅(S7H-050)
- **V1**: 주요 비교 콘텐츠 4-5편 작성 → **V2**: 월 2편 정기 발행 → **V3**: 자동 비교 업데이트

### S7H-046 | HIGH | V2 | 오픈소스 커뮤니티 — 경쟁 차별화

- **모듈 연동**: H(비즈니스) - 커뮤니티 전략
- **구현 방식**: 오픈소스 커뮤니티를 경쟁 우위로 활용. 전략: GitHub 활발한 이슈 관리 + PR 리뷰, 기여자 프로그램(기여자 Pro 무료), 월간 커뮤니티 콜/로드맵 공유, 투명한 개발 프로세스(RFC, ADR 공개)
- **기술 스택**: GitHub(Issues/Discussions/Projects), Discord, Open Collective
- **VAMOS 연동**: 오픈소스 전략(S7H-015), 개발자 애드보케이시(S7H-058)
- **V1**: GitHub 커뮤니티 운영 시작 → **V2**: 기여자 프로그램 + 커뮤니티 콜 → **V3**: 커뮤니티 자치 거버넌스

### S7H-047 | MED | V2 | 파트너십 전략 — 전략적 제휴

- **모듈 연동**: H(비즈니스) - 파트너십
- **구현 방식**: 생태계 파트너십으로 경쟁력 강화. LLM 프로바이더: Anthropic, OpenAI(파트너 할인). 개발 도구: VSCode, JetBrains(플러그인). 생산성 도구: Notion, Obsidian(연동). 금융 데이터: 한국투자증권, KIS(데이터 API)
- **기술 스택**: 파트너 관리 시스템, API 연동 프레임워크
- **VAMOS 연동**: MCP Tool 마켓(S7H-021), API 프로바이더 제휴(S7H-018)
- **V1**: 파트너십 로드맵 작성 → **V2**: 핵심 파트너 1-2개 체결 → **V3**: 파트너 생태계 확대

### S7H-048 | MED | V2 | 특허/IP 전략 — 지적 재산 보호

- **모듈 연동**: H(비즈니스) - 법무/IP
- **구현 방식**: 핵심 알고리즘의 특허 또는 공개 전략. 오픈소스이므로 Defensive Patent License 또는 특허 미출원. Trade Secret 대신 Open Innovation 선택
- **기술 스택**: 법률 자문, 라이선스 관리
- **VAMOS 연동**: 오픈소스 전략(S7H-015), 법적 리스크(S7H-070)
- **V1**: 라이선스(MIT/Apache 2) 확정 → **V2**: DPL 검토 → **V3**: IP 포트폴리오 관리

#### OpenAI Codex / AntiGravity 경쟁 분석 [REF:영상6]

| 비교 항목 | VAMOS (Claude Code 기반) | OpenAI Codex | AntiGravity |
|-----------|------------------------|-------------|-------------|
| 아키텍처 | 로컬 + 클라우드 하이브리드 | 클라우드 전용 샌드박스 | 클라우드 전용 |
| 규칙 시스템 | .vamosrules (YAML) | 제한적 | 미성숙 |
| 자율성 | 사용자 승인 기반 (Safety Gate) | 완전 자율 (위험성) | 반자율 |
| 비용 구조 | V1 $30/월 상한 | 사용량 기반 (예측 어려움) | 구독형 |
| 오프라인 | 부분 지원 (Tauri 로컬) | 불가 | 불가 |
| 강점 | 규칙 준수, 안전성, 비용 통제 | 빠른 프로토타이핑 | UI 친화적 |
| 약점 | 초기 설정 복잡 | 규칙 무시 사례 | 기능 제한 |

---

## H-Part 7: GTM (Go-to-Market) 전략 (8건)

### H-Part 7 GTM 단계별 전략

```
Phase 1: Seed(0-6mo) → Phase 2: Growth(6-18mo) →
Phase 3: Scale(18-36mo) → Phase 4: Mature(36mo+)
```

---

### S7H-049 | HIGH | V1 | Phase 1: 씨드 단계 — 최소 비용 런칭

- **모듈 연동**: H(비즈니스) - GTM
- **구현 방식**: V1 출시 첫 6개월 전략. GitHub 공개 + README/문서 최적화, Product Hunt 런칭(day 1 전략), Hacker News "Show HN", 한국 개발자 커뮤니티(GeekNews, 디스코드), 개인 블로그/유튜브 VAMOS 개발기 시리즈, 디스코드/텔레그램 커뮤니티 개설. 비용: ~$0(시간 투자만). KPI: 1,000 GitHub Stars, 500 활성 사용자, 100 디스코드 멤버
- **기술 스택**: GitHub, Product Hunt, Discord, 블로그(Hugo/Ghost)
- **VAMOS 연동**: 초기 사용자 확보(S7H-016), P1 테크 얼리어답터(S7H-027)
- **V1**: 무비용 런칭 실행 → **V2**: Phase 2 전환 → **V3**: Phase 3 스케일

### S7H-050 | HIGH | V1 | 콘텐츠 마케팅 — SEO + 교육 콘텐츠

- **모듈 연동**: H(비즈니스) - 마케팅
- **구현 방식**: 기술 블로그와 교육 콘텐츠로 유기적 유입 확보. 기술 블로그(주 1회): 아키텍처 Deep Dive, 비용 절감 가이드, 프라이버시 가이드, KG 구축 가이드. 비교/리뷰(월 2회): ChatGPT vs VAMOS, AI 비서 비교 가이드. 튜토리얼(월 2회): 설치 가이드, MCP Tool 개발, 투자 분석 파이프라인. SEO 타겟: "AI 비서 비교", "ChatGPT 대안", "로컬 AI", "AI 비용 절감"
- **기술 스택**: 블로그 플랫폼, SEO 도구(Ahrefs/Semrush 무료 대안), Google Search Console
- **VAMOS 연동**: 비교 콘텐츠(S7H-045), 핵심 메시지(S7H-044), 데모(S7H-052)
- **V1**: 주 1-2편 콘텐츠 발행 → **V2**: 주 2-3편 + 유튜브 → **V3**: 콘텐츠 팀 구성

### S7H-051 | HIGH | V2 | 커뮤니티 운영 — 사용자 커뮤니티

- **모듈 연동**: H(비즈니스) - 커뮤니티
- **구현 방식**: 활발한 사용자 커뮤니티 운영. Discord: 주요 커뮤니케이션(general/support/dev/ideas). GitHub Discussions: 기술 토론, RFC. Reddit: r/VAMOS_AI 서브레딧. 활동: 주간 AMA, 월간 로드맵 업데이트, 기여자 하이라이트
- **기술 스택**: Discord 봇, Reddit 관리, 커뮤니티 분석 도구
- **VAMOS 연동**: 오픈소스 커뮤니티(S7H-046), Phase 1(S7H-049)
- **V1**: 디스코드 개설 + 기본 운영 → **V2**: 구조화된 커뮤니티 프로그램 → **V3**: 커뮤니티 매니저 채용

### S7H-052 | HIGH | V1 | 데모 / 쇼케이스 — 실제 사용 시연

- **모듈 연동**: H(비즈니스) - 마케팅
- **구현 방식**: VAMOS 실제 사용 시나리오 데모. "VAMOS로 하루 일과 관리하기"(영상 5분), "AI 비용 실시간 추적 데모"(GIF/영상), "코딩 프로젝트 지원 데모"(라이브 코딩), "투자 분석 리포트 생성 데모"(영상). 채널: YouTube, X(Twitter), Product Hunt, 블로그
- **기술 스택**: 스크린캐스트 도구(OBS), 영상 편집, GIF 생성
- **VAMOS 연동**: 콘텐츠 마케팅(S7H-050), Phase 1(S7H-049)
- **V1**: 핵심 데모 4편 제작 → **V2**: 월간 새 기능 데모 → **V3**: 인터랙티브 데모 사이트

### S7H-053 | HIGH | V2 | Phase 2: 성장 단계 — 유기적 성장

- **모듈 연동**: H(비즈니스) - GTM
- **구현 방식**: 6-18개월차 성장 전략. V2 웹/PWA 출시 → 접근성 확대, 콘텐츠 마케팅 강화(주 2-3회), MCP Tool 마켓 런칭 → 생태계 확장, 인플루언서/유튜버 협업, 컨퍼런스 발표(PyCon, JSConf, AI Summit). KPI: 30,000 활성 사용자, 5,000 유료, $4.3M ARR
- **기술 스택**: V2 인프라(서버), PWA, 마케팅 자동화 도구
- **VAMOS 연동**: V2 인프라(S7F Part 3), SaaS 모델(S7H-020), MCP 마켓(S7H-021)
- **V1**: Phase 2 계획 수립 → **V2**: Phase 2 실행 → **V3**: Phase 3 전환

### S7H-054 | MED | V2 | SEO / ASO 전략 — 검색 최적화

- **모듈 연동**: H(비즈니스) - 마케팅
- **구현 방식**: 검색 엔진 + 앱 스토어 최적화. SEO: 기술 블로그, 비교 콘텐츠, 백링크 빌딩. ASO: 앱 스토어(V3 모바일 앱) 최적화
- **기술 스택**: Google Search Console, Ahrefs/Semrush, 앱 스토어 분석
- **VAMOS 연동**: 콘텐츠 마케팅(S7H-050), 비교 콘텐츠(S7H-045)
- **V1**: 기본 SEO 설정 → **V2**: 본격 SEO + 백링크 → **V3**: ASO + 유료 광고

### S7H-055 | MED | V3 | Phase 3: 스케일 — 유료 확장

- **모듈 연동**: H(비즈니스) - GTM
- **구현 방식**: 18-36개월차 확장 전략. B2B 영업 시작, 유료 광고(Google Ads, LinkedIn), 글로벌 확장
- **기술 스택**: CRM(HubSpot Free), Google Ads, LinkedIn Ads, 글로벌 배포 인프라
- **VAMOS 연동**: 기업 라이선스(S7H-023), 지역 확장(S7H-040), 엔터프라이즈 세일즈(S7H-064)
- **V1**: 해당 없음 → **V2**: Phase 3 준비 → **V3**: Phase 3 실행

### S7H-056 | MED | V3 | 투자 유치 전략 — 펀딩 로드맵

- **모듈 연동**: H(비즈니스) - 재무 전략
- **구현 방식**: 필요 시 투자 유치 계획. Pre-seed: 자체 부트스트래핑(V1). Seed: $500K-$1M(V2 개발, 팀 구성). Series A: $5M+(V3 스케일). 투자자 타겟: Y Combinator, a16z, 한국: SparkLabs, Strong Ventures
- **기술 스택**: 피치 덱, 재무 모델, 투자자 DB
- **VAMOS 연동**: 재무 모델링(S7H-073~078), 성장 시나리오(S7H-037)
- **V1**: 자체 부트스트래핑 → **V2**: Seed 라운드 검토 → **V3**: Series A(필요 시)

---

## H-Part 8: 성장 전략 (8건)

### S7H-057 | HIGH | V1 | 바이럴 메커니즘 — 자연적 확산

- **모듈 연동**: H(비즈니스) - 성장
- **구현 방식**: 사용자가 자발적으로 VAMOS를 추천하도록 유도. "Powered by VAMOS" 워터마크(export 시 선택적), 공유 기능(분석/리포트 공유 시 VAMOS 태그), 오픈소스(GitHub Star = 자연적 확산), 초대 보상(Pro 기능 7일 무료 체험)
- **기술 스택**: 공유 기능 구현, 리퍼럴 시스템(V2), GitHub Star 캠페인
- **VAMOS 연동**: 콘텐츠 마케팅(S7H-050), Phase 1(S7H-049)
- **V1**: 기본 공유 기능 + GitHub Star → **V2**: 리퍼럴 프로그램 → **V3**: 바이럴 루프 최적화

### S7H-058 | HIGH | V1 | 개발자 애드보케이시 — 기술 리더십

- **모듈 연동**: H(비즈니스) - 커뮤니티
- **구현 방식**: 기술 커뮤니티에서 VAMOS 인지도 확보. 기술 블로그 시리즈(아키텍처, 벤치마크 공개), 오픈소스 기여(LangChain, MCP 생태계), 컨퍼런스 발표(기술 스택 공유), GitHub Sponsors/Open Collective
- **기술 스택**: 기술 블로그, GitHub, 컨퍼런스 발표 자료
- **VAMOS 연동**: 오픈소스 전략(S7H-015), 커뮤니티(S7H-046)
- **V1**: 기술 블로그 + GitHub 활동 → **V2**: 컨퍼런스 발표 + 후원 → **V3**: Developer Relations 전담

### S7H-059 | HIGH | V2 | MCP 생태계 성장 — Tool 마켓 플라이휠

- **모듈 연동**: A(Agent Layer), H(비즈니스) - 플랫폼 성장
- **구현 방식**: MCP Tool 생태계 성장으로 플랫폼 가치 증대. 플라이휠: 더 많은 사용자 → 더 많은 Tool 개발 → 더 좋은 경험 → 더 많은 사용자(반복). 시드: 핵심 Tool 30개 자체 개발 → 커뮤니티 기여 유도
- **기술 스택**: MCP SDK, Tool 개발자 가이드, Tool Registry
- **VAMOS 연동**: MCP Tool 마켓(S7H-021), MOAT 네트워크 효과(S7H-043)
- **V1**: 핵심 Tool 30개 → **V2**: 마켓 런칭 + 100개 Tool → **V3**: 500+ Tool 생태계

### S7H-060 | HIGH | V2 | 리텐션 전략 — 사용자 유지

- **모듈 연동**: H(비즈니스) - 리텐션
- **구현 방식**: 사용자가 계속 VAMOS를 사용하도록 유지 전략. 개인화 누적 효과(사용할수록 더 좋아짐 — 메모리, KG), 정기 가치 제공(주간 인사이트, 생산성 리포트), 새 기능 정기 업데이트(월 1회), 사용 통계("이번 달 VAMOS와 200번 대화, ₩15,000 절감")
- **기술 스택**: 사용 분석, 인게이지먼트 시스템, 자동 리포트 생성
- **VAMOS 연동**: 5-Layer 메모리(STEP7-B), Knowledge Graph(STEP7-C), 이탈 방지(S7H-034)
- **V1**: 개인화 누적 효과 기본 → **V2**: 자동 인사이트 + 절감 리포트 → **V3**: ML 기반 리텐션 최적화

### S7H-061 | MED | V2 | 크로스 셀 / 업셀 — 수익 극대화

- **모듈 연동**: H(비즈니스) - 수익화
- **구현 방식**: 기존 사용자에게 추가 서비스 판매. 업셀: Free → Core → Pro → Power. 크로스 셀: Pro 사용자에게 Quant Agent 패키지 추천
- **기술 스택**: 추천 엔진, 인앱 프로모션, A/B 테스트
- **VAMOS 연동**: 프리미엄 전환(S7H-017), 프리미엄 Agent(S7H-022)
- **V1**: 업셀 경로 정의 → **V2**: 인앱 추천 구현 → **V3**: ML 기반 추천

### S7H-062 | MED | V2 | 전략적 인수 대상 — M&A 기회

- **모듈 연동**: H(비즈니스) - 전략
- **구현 방식**: 기능 보완을 위한 인수 또는 합병 대상 분석. 대상: 작은 MCP Tool 개발사, 한국어 NLP 스타트업, 금융 데이터 스타트업
- **기술 스택**: M&A 분석 프레임워크, 기업 평가 모델
- **VAMOS 연동**: 파트너십(S7H-047), 투자 유치(S7H-056)
- **V1**: 대상 리스트 작성 → **V2**: 기술 제휴 우선 → **V3**: M&A 검토(자금 확보 후)

### S7H-063 | MED | V3 | 국제화 — i18n/L10n 전략

- **모듈 연동**: H(비즈니스), S(Service Layer) - 글로벌화
- **구현 방식**: 다국어 지원 전략. 우선순위: 한국어(V1) → 영어(V1) → 일본어(V2) → 중국어(V3). 현지화: UI 번역 + 문화적 맥락 + 현지 LLM 최적화
- **기술 스택**: i18n 프레임워크(react-intl), L10n 파이프라인, 번역 관리(Crowdin)
- **VAMOS 연동**: 지역 확장(S7H-040), 한국어 벤치마크(S7G Part 2)
- **V1**: 한국어 + 영어 → **V2**: 일본어 추가 → **V3**: 중국어 + 추가 언어

### S7H-064 | MED | V3 | 엔터프라이즈 세일즈 — B2B 판매 체계

- **모듈 연동**: H(비즈니스) - B2B 영업
- **구현 방식**: 기업 고객 판매 프로세스 수립. 리드 → 데모 → PoC(2주) → 계약 → 온보딩 → 확장
- **기술 스택**: CRM(HubSpot), 영업 파이프라인, PoC 관리 시스템
- **VAMOS 연동**: 기업 라이선스(S7H-023), B2B 가격(S7H-007), Phase 3(S7H-055)
- **V1**: 해당 없음 → **V2**: 영업 프로세스 설계 → **V3**: B2B 영업팀 구성

---

## H-Part 9: 리스크 분석 (8건)

### H-Part 9 주요 리스크 매트릭스

| 리스크 | 발생 확률 | 영향도 | 심각도 | 대응 전략 |
|--------|----------|--------|--------|----------|
| API 가격 변동 | HIGH | HIGH | CRITICAL | 멀티 프로바이더 |
| 경쟁 심화 | HIGH | MED | HIGH | 차별화 강화 |
| LLM 품질 저하 | MED | HIGH | HIGH | 벤치마크 모니터 |
| 사용자 미확보 | MED | HIGH | HIGH | GTM 다각화 |
| 보안 인시던트 | LOW | VERY HIGH | HIGH | 다층 방어 |
| 규제 변화 | MED | MED | MED | 선제적 준수 |
| 기술 부채 | MED | MED | MED | 리팩토링 주기 |
| 핵심 인력 이탈 | MED | HIGH | HIGH | 문서화, 분산 |

---

### S7H-065 | CRITICAL | V1 | API 가격 리스크 — 가격 변동 대응

- **모듈 연동**: I(Infra Core), H(비즈니스) - 리스크 관리
- **구현 방식**: LLM API 가격 인상 또는 무료 Tier 폐지 리스크 대응. 멀티 프로바이더 전략(단일 의존 제거), 로컬 LLM fallback(항상 무료 대안 유지), 가격 모니터링(변동 시 즉시 라우팅 조정), 장기 계약(볼륨 할인 V2+). 완화: 2024-25 추세는 가격 하락 → 유리한 환경
- **기술 스택**: 가격 모니터링 시스템, 멀티 프로바이더 Fallback, 로컬 LLM 유지 관리
- **VAMOS 연동**: Model Router(S7F-003), Fallback Chain(S7F-004), 무료 대안(S7H-006)
- **V1**: 멀티 프로바이더 + 로컬 fallback → **V2**: 볼륨 할인 협상 → **V3**: 자체 모델 Fine-tune

### S7H-066 | CRITICAL | V1 | 경쟁 리스크 — Big Tech의 무료화 전략

- **모듈 연동**: H(비즈니스) - 리스크 관리
- **구현 방식**: Google/Meta 등이 무료 AI 서비스 확대 시 대응. "무료 서비스의 대가는 당신의 데이터" 메시지, 개인화 + 데이터 주권은 Big Tech이 제공 불가, 오픈소스 + 커뮤니티 충성도로 방어, 니치 시장(투자, 프라이버시) 집중
- **기술 스택**: 경쟁 모니터링, 차별화 강화 전략
- **VAMOS 연동**: 핵심 차별화(S7H-041), 데이터 주권(S7H-014), MOAT(S7H-043)
- **V1**: 차별화 포지셔닝 확립 → **V2**: 커뮤니티 충성도 강화 → **V3**: 니치 시장 지배

### S7H-067 | HIGH | V1 | 기술 리스크 — LLM 품질 저하/변경

- **모듈 연동**: I(Infra Core), G(벤치마크) - 리스크 관리
- **구현 방식**: API 모델 업데이트로 품질 저하 또는 동작 변경 대응. 벤치마크 자동 모니터링(STEP7-G), 모델 Fallback 체인, 프롬프트 버전 관리 + 회귀 테스트, 자체 Fine-tune 모델로 의존도 감소(V2+)
- **기술 스택**: 자동 벤치마크(S7G Part 9), 프롬프트 버전 관리, 회귀 테스트
- **VAMOS 연동**: 벤치마크 시스템(STEP7-G 전체), Fallback Chain(S7F-004), promptfoo(S7G-072)
- **V1**: 자동 벤치마크 + 회귀 테스트 → **V2**: Fine-tune 모델 실험 → **V3**: 자체 경량 모델

### S7H-068 | HIGH | V1 | 사용자 확보 리스크 — PMF 미달성

- **모듈 연동**: H(비즈니스) - 리스크 관리
- **구현 방식**: Product-Market Fit 미달성 리스크 대응. 빠른 MVP 출시 → 사용자 피드백 수집, 핵심 기능 집중(개인화, 비용 투명성), 피봇 준비(니치 시장 — 코딩/투자 집중 전환), 커뮤니티 밀착(주간 피드백)
- **기술 스택**: 사용자 피드백 수집 도구, 분석 대시보드, A/B 테스트
- **VAMOS 연동**: 사용자 여정(S7H-032), 타겟 페르소나(S7H-027~034)
- **V1**: 빠른 MVP + 피드백 루프 → **V2**: PMF 달성 확인 → **V3**: 확장

### S7H-069 | HIGH | V1 | 보안 리스크 — 데이터 유출/인시던트

- **모듈 연동**: E(Security Layer), H(비즈니스) - 리스크 관리
- **구현 방식**: 보안 인시던트 발생 시 브랜드 훼손 대응. STEP7-E 보안 체계 철저 구축, "로컬 데이터" 이점(서버 해킹 시 전체 유출 불가), 인시던트 대응 계획 사전 수립, 보안 감사 + 버그 바운티(V2)
- **기술 스택**: 보안 프레임워크(STEP7-E), 인시던트 대응 플레이북, 버그 바운티 플랫폼(V2)
- **VAMOS 연동**: 보안 체계(STEP7-E 전체), 로컬 저장소(S7F-013), PII 마스킹
- **V1**: 보안 체계 구축 + 인시던트 플레이북 → **V2**: 보안 감사 + 버그 바운티 → **V3**: SOC2 인증

### S7H-070 | HIGH | V2 | 법적 리스크 — AI 규제 대응

- **모듈 연동**: H(비즈니스), E(Security Layer) - 규제
- **구현 방식**: EU AI Act, 한국 AI기본법 등 규제 대응. STEP7-E Part 6 규제 준수 체계 구축, 선제적 규제 대응(투자 기능 면책 조항), 법률 자문 확보(V2 출시 전)
- **기술 스택**: 규제 모니터링, 법률 자문 네트워크, 컴플라이언스 체크리스트
- **VAMOS 연동**: 규제 준수(STEP7-E Part 6), 투자 면책(S7I-085), 자본시장법(S7I-093)
- **V1**: 면책 조항 구현 → **V2**: 법률 자문 + 규제 대응 → **V3**: 규제 인증

### S7H-071 | MED | V1 | 단일 개발자 리스크 — Bus Factor

- **모듈 연동**: H(비즈니스) - 리스크 관리
- **구현 방식**: 핵심 개발자(1인) 이탈/불능 시 프로젝트 중단 리스크 대응. 철저한 문서화(이 STEP7 시리즈가 그 일환), 오픈소스(커뮤니티가 이어받기 가능), 코드 품질(테스트 커버리지, 클린 코드), V2에서 핵심 기여자 2-3명 확보 목표
- **기술 스택**: 기술 문서(ADR, RFC), 테스트 커버리지, CI/CD
- **VAMOS 연동**: QA 체계(S7G-085~088), 오픈소스 전략(S7H-015), 커뮤니티(S7H-046)
- **V1**: 문서화 + 오픈소스 공개 → **V2**: 핵심 기여자 확보 → **V3**: 팀 구성

### S7H-072 | MED | V2 | 기술 부채 리스크 — 누적 기술 부채

- **모듈 연동**: H(비즈니스), I(Infra Core) - 리스크 관리
- **구현 방식**: 빠른 개발로 인한 기술 부채 누적 대응. 분기 1회 리팩토링 스프린트, 코드 리뷰 문화(V2 팀 구성 후), 아키텍처 문서 유지(ADR), 기술 부채 백로그 관리
- **기술 스택**: SonarQube/CodeClimate, GitHub PR 리뷰, ADR 관리
- **VAMOS 연동**: CI/CD(S7F Part 5), QA(S7G Part 11), 코드 품질
- **V1**: 기술 부채 백로그 시작 → **V2**: 분기 리팩토링 제도화 → **V3**: 기술 부채 대시보드

---

## H-Part 10: 재무 모델링 (6건)

### S7H-073 | HIGH | V1 | V1 수지 분석 — MVP 운영 비용

- **모듈 연동**: H(비즈니스) - 재무
- **구현 방식**: V1 MVP 운영의 월간 수지 분석. 비용(개발자 1인): 인프라 $0(로컬), API 테스트 ~$20/mo, 도메인/호스팅 ~$10/mo, GitHub Pro $4/mo → 합계 ~$34/mo. 수익(1,000 사용자): API 마진(10%) 1,000 x $8 x 10% = $800/mo. 순이익 ~$766/mo. 손익분기: 43 사용자(API 마진 기준)
- **기술 스택**: 재무 모델 스프레드시트, 비용 추적 대시보드
- **VAMOS 연동**: API 마진(S7H-019), 비용 추적(S7H-012)
- **V1**: 수지 분석 + 손익분기 달성 → **V2**: V2 수지 전환 → **V3**: 본격 수익화

### S7H-074 | HIGH | V2 | V2 수지 분석 — SaaS 운영

- **모듈 연동**: H(비즈니스) - 재무
- **구현 방식**: V2 SaaS 월간 수지 분석. 비용: 서버 $100-200/mo, DB $50/mo, 모니터링 $20/mo, 인건비 $5,000/mo(1명), 마케팅 $500/mo → 합계 ~$5,770/mo. 수익(5,000 유료): Pro 3,000 x $15 = $45,000, Core API마진 2,000 x $2 = $4,000, Tool 마켓 $1,000 → 합계 ~$50,000/mo. 순이익 ~$44,230/mo. 손익분기: ~385 Pro 사용자
- **기술 스택**: SaaS 재무 모델, MRR/ARR 추적
- **VAMOS 연동**: SaaS 모델(S7H-020), V2 인프라(S7F Part 3)
- **V1**: V2 재무 모델 설계 → **V2**: 실적 대비 모델 조정 → **V3**: V3 재무 모델

### S7H-075 | HIGH | V2 | Unit Economics — 사용자당 경제성

- **모듈 연동**: H(비즈니스) - 재무
- **구현 방식**: 사용자 1명당 경제성 분석. LTV: ARPU $12/mo x Retention 18개월 = $216. CAC: 오가닉(V1) ~$2, 유료(V2+) ~$15-30. LTV/CAC = $216/$15 = 14.4x(매우 건강). 목표: LTV/CAC >= 3x
- **기술 스택**: 코호트 분석, LTV/CAC 추적 대시보드
- **VAMOS 연동**: 리텐션(S7H-060), GTM(S7H-049~056)
- **V1**: 초기 CAC 측정 → **V2**: LTV 추정 + 코호트 분석 → **V3**: Unit Economics 최적화

### S7H-076 | MED | V2 | 3년 재무 전망 — P&L 프로젝션

- **모듈 연동**: H(비즈니스) - 재무
- **구현 방식**: 3년 P&L 프로젝션. Y1: 사용자 5K, 유료 500, MRR $5K, ARR $60K, 비용 $50K, 순이익 $10K, 마진 17%. Y2: 30K/5K/MRR $75K/ARR $900K/비용 $400K/순이익 $500K/마진 56%. Y3: 100K/20K/MRR $300K/ARR $3.6M/비용 $1.5M/순이익 $2.1M/마진 58%
- **기술 스택**: 재무 모델 스프레드시트, 투자자 리포팅 템플릿
- **VAMOS 연동**: 성장 시나리오(S7H-037), 투자 유치(S7H-056)
- **V1**: 초기 P&L 모델 → **V2**: 실적 기반 조정 → **V3**: 투자자 리포팅

### S7H-077 | MED | V2 | 자금 소요 계획 — 자금 로드맵

- **모듈 연동**: H(비즈니스) - 재무
- **구현 방식**: 단계별 자금 소요 및 조달 계획. V1(0-6mo): $0(부트스트래핑). V2(6-18mo): $200K(매출 + Seed). V3(18-36mo): $2M(매출 + Series A). 자체 자금 비율 최대화 → 희석 최소화
- **기술 스택**: 자금 계획 모델, 현금흐름 예측
- **VAMOS 연동**: 투자 유치(S7H-056), 3년 재무 전망(S7H-076)
- **V1**: 부트스트래핑 → **V2**: 자금 조달 검토 → **V3**: 시리즈 A(필요 시)

### S7H-078 | MED | V3 | Exit 전략 — 장기 비전

- **모듈 연동**: H(비즈니스) - 장기 전략
- **구현 방식**: 장기적 Exit 또는 지속 운영 전략. 옵션 1: 독립 운영 — 수익성 있는 오픈소스 기업(Supabase, GitLab 모델). 옵션 2: 전략적 인수 — AI 대기업에 인수(기술+커뮤니티 가치). 옵션 3: IPO — 충분한 규모 달성 시 상장(V3+). 선호: 독립 운영 + 커뮤니티 중심 성장
- **기술 스택**: 기업 가치 평가 모델, Exit 시나리오 분석
- **VAMOS 연동**: 3년 재무 전망(S7H-076), 투자 유치(S7H-056)
- **V1**: 장기 비전 수립 → **V2**: 독립 운영 기반 구축 → **V3**: Exit 옵션 평가

---

## H 카테고리 구현 우선순위 로드맵

### V1 (MVP) — 필수 구현: 30건
- 가격 분석: S7H-001~006 (6건)
- 가격 전략: S7H-011~016 (6건)
- 수익 모델: S7H-019 (1건)
- 페르소나: S7H-027~030, 032 (5건)
- 시장: S7H-035~037 (3건)
- 포지셔닝: S7H-041~045 (5건)
- GTM: S7H-049, 050, 052 (3건)
- 성장: S7H-057, 058 (2건)
- 리스크: S7H-065~069, 071 (6건)
- 재무: S7H-073 (1건)

### V2 (Server) — 확장 구현: 35건

### V3 (Enterprise) — 고급 구현: 13건

---

# I. AI Investing 보강 (106건)

## I-Part 1: 2025 AI 투자 플랫폼 최신 동향 (10건)

### I-Part 1 AI 투자 플랫폼 전수비교 (2025.02 기준)

| 플랫폼 | 유형 | AI 기능 | 한국 지원 | 가격 | VAMOS 연동 |
|--------|------|---------|----------|------|-----------|
| QuantConnect | 퀀트 플랫폼 | 코드 기반 백테스트 | 미국/글로벌 | Free~$20/mo | API |
| Alpaca | 브로커 API | 자동 매매 API | 미국주식 | 수수료 무료 | API |
| Interactive Brokers | 종합 브로커 | TWS API | 글로벌 | 수수료 기반 | API |
| TradingView | 차트/분석 | Pine Script | 한국 | Free~$60/mo | Webhook |
| 키움증권 OpenAPI | 한국 브로커 | API 제공 | 핵심 | 수수료 | API |
| 한국투자증권 KIS | 한국 브로커 | REST API | 한국 | 수수료 | API |
| Koyfin | 펀더멘털 | AI 스크리닝 | 글로벌 | Free~$50/mo | V2 |
| OpenBB | 오픈소스 | 터미널 | 글로벌 | Free | 참조 |

---

### S7I-001 | CRITICAL | V1 | 최신 AI 투자 도구 통합 전략 — 2025 생태계 매핑

- **모듈 연동**: A(Agent Layer) - Quant Node, I(Infra Core)
- **구현 방식**: 2025년 기준 VAMOS Quant/Trading Node가 활용해야 할 도구 생태계 재정리. 기존 83개 소스에 10개 추가: OpenBB Platform v4(P1), FinGPT(P1), Perplexity Finance API(P2), SEC EDGAR Full-Text(P1), FRED API(P0), 한국은행 ECOS API(P0), 금융감독원 DART API(P0), 네이버 금융 크롤링(P1), CoinGecko API v3(P1), Alternative.me Fear & Greed(P1). 소스 총수: 83 → 93개
- **기술 스택**: API 통합 프레임워크, OpenBB SDK, 데이터 정규화 파이프라인
- **VAMOS 연동**: 7-Component Pipeline(collect→standardize→validate→store→strategy→legal→trade), 데이터 소스 분류(P0/P1/S0/S1)
- **V1**: 93개 소스 매핑 + P0 소스 연동 → **V2**: P1 소스 전체 연동 → **V3**: 프리미엄 데이터 소스

### S7I-002 | CRITICAL | V1 | FinGPT 통합 — 금융 특화 LLM 활용

- **모듈 연동**: A(Agent Layer) - Quant Node, I(Infra Core)
- **구현 방식**: FinGPT(오픈소스 금융 LLM)를 VAMOS에 통합. 금융 뉴스/보고서 학습 특화, 감성 분석 정확도 일반 LLM 대비 15-20% 향상, LoRA 기반 경량 Fine-tuning, Apache 2.0 라이선스. Quant Node 모델 라우팅: 일반 분석 → Claude/GPT(범용), 금융 감성 → FinGPT(특화), 한국어 금융 → KoFinBERT(V2). 비용: 로컬 실행 $0(7B ~4GB)
- **기술 스택**: FinGPT(HuggingFace), LoRA, Ollama 로컬 실행, Model Router 통합
- **VAMOS 연동**: Model Router(S7F-003), Ollama(S7F-001), 뉴스 감성 분석(S7I-008)
- **V1**: FinGPT 로컬 통합 + 감성 분석 → **V2**: KoFinBERT 한국어 확장 → **V3**: 자체 금융 모델 Fine-tune

### S7I-003 | CRITICAL | V1 | OpenBB Platform v4 연동 — 오픈소스 금융 터미널

- **모듈 연동**: A(Agent Layer) - Quant Node, I(Infra Core)
- **구현 방식**: OpenBB Platform을 VAMOS의 데이터 수집 백엔드로 활용. 50+ 데이터 프로바이더 통합(yfinance, Alpha Vantage, FRED 등), 표준화된 데이터 포맷(OBBject), Python SDK + REST API, 커스텀 프로바이더 확장 가능, 무료 오픈소스. `obb.equity.price.historical()`, `obb.equity.fundamental.income()`, `obb.economy.gdp.nominal()`, `obb.news.company()` 등 통합 호출
- **기술 스택**: OpenBB SDK(Python), REST API, 커스텀 Provider 개발
- **VAMOS 연동**: 7-Component Pipeline collect 단계, MCP Tool 래핑(V2)
- **V1**: OpenBB SDK 직접 활용 → **V2**: MCP Tool로 래핑 → **V3**: 커스텀 Provider 개발

### S7I-004 | HIGH | V1 | FRED/한국은행 API — 거시경제 데이터 통합

- **모듈 연동**: A(Agent Layer) - Quant/Research Node
- **구현 방식**: 거시경제 지표 데이터 실시간 연동. FRED(미국): GDP, CPI, PPI, PCE, Fed Funds Rate, 10Y Treasury, 실업률, ISM PMI, S&P 500 Earnings Yield. 한국은행 ECOS: GDP, CPI, PPI, 기준금리, 국고채, 수출입, 경상수지, 소비자심리지수, BSI. API 모두 무료(키 필요)
- **기술 스택**: FRED API, 한국은행 Open API, OpenBB economy 모듈
- **VAMOS 연동**: 섹터 분석(S7I-015), 글로벌 매크로 대시보드(S7I-020), 스트레스 테스트(S7I-054)
- **V1**: 핵심 지표 10개 연동 → **V2**: 전체 지표 + 자동 해석 → **V3**: 매크로 예측 모델

### S7I-005 | HIGH | V1 | 금융감독원 DART API — 한국 기업 공시 분석

- **모듈 연동**: A(Agent Layer) - Research Node
- **구현 방식**: 한국 상장기업 공시자료 실시간 수집/분석. DART Open API(무료). 데이터: 기업 재무제표(연결/별도), 주요사항보고서(유상증자, CB, BW), 대량보유 보고서(5%+), 임원 주식 거래, 감사보고서. VAMOS 활용: 자동 공시 모니터링 → 알림, 재무제표 자동 분석(수익성/성장성/안정성), 공시 이벤트 기반 투자 시그널
- **기술 스택**: DART OpenAPI, XML/JSON 파서, LLM 분석 파이프라인
- **VAMOS 연동**: 재무제표 분석(S7I-013), 공시 알림(S7I-068), 기업 분석 리포트(S7I-011)
- **V1**: DART 연동 + 자동 공시 알림 → **V2**: LLM 자동 분석 + 시그널 → **V3**: 고급 공시 분석 Agent

### S7I-006 | HIGH | V1 | SEC EDGAR — 미국 기업 공시 분석

- **모듈 연동**: A(Agent Layer) - Research Node
- **구현 방식**: SEC EDGAR Full-Text Search로 미국 기업 공시 분석. 데이터: 10-K, 10-Q, 8-K, Form 4(내부자 거래), 13F(기관 포트폴리오). VAMOS 활용: LLM으로 10-K 자동 요약(핵심 리스크, 성장 동인), 13F 분석(워렌 버핏 등 유명 기관 추적), 내부자 거래 패턴 분석
- **기술 스택**: SEC EDGAR API, Full-Text Search, LLM 요약 파이프라인
- **VAMOS 연동**: 기관 포트폴리오(S7I-023), 내부자 거래(S7I-022), 기업 분석(S7I-011)
- **V1**: 10-K/13F 기본 조회 + LLM 요약 → **V2**: 자동 모니터링 + 시그널 → **V3**: 고급 NLP 분석

### S7I-007 | HIGH | V1 | Earnings Call 분석 — 실적발표 자동 분석

- **모듈 연동**: A(Agent Layer) - Research Node
- **구현 방식**: 기업 실적발표 컨퍼런스 콜 트랜스크립트 분석. 소스: Seeking Alpha, Motley Fool, The Earnings Whisper(무료). LLM 분석: 1) 핵심 수치 추출(매출, EPS, 가이던스), 2) 서프라이즈 분석(실적 vs 컨센서스), 3) 경영진 톤 분석(FinGPT 감성), 4) 핵심 키워드(AI, 구조조정 등), 5) 가이던스 변화 추적, 6) Q&A 핵심 이슈 요약
- **기술 스택**: 트랜스크립트 크롤링, FinGPT 감성 분석, LLM 구조화 요약
- **VAMOS 연동**: FinGPT(S7I-002), 뉴스 감성(S7I-008), 기업 분석(S7I-011)
- **V1**: 수동 트랜스크립트 분석 → **V2**: 자동 수집 + 실시간 분석 → **V3**: 실적 예측 모델

### S7I-008 | HIGH | V1 | 뉴스 감성 분석 — 실시간 금융 뉴스 분석

- **모듈 연동**: A(Agent Layer) - Research Node
- **구현 방식**: 금융 뉴스 감성(긍정/부정/중립) 실시간 분석. 파이프라인: 1) 수집(NewsAPI, Google News, 네이버 금융), 2) 전처리(제목+본문 요약), 3) 감성 분류(영어: FinBERT 로컬, 한국어: Claude V1→KoFinBERT V2), 4) 종합 점수(시간가중 감성 스코어), 5) 감성 시계열 DB 저장. 알림: 특정 종목 감성 급변 → 즉시 알림, 시장 전체 감성 극단값 → 경고
- **기술 스택**: FinBERT(HuggingFace, 로컬), NewsAPI, Claude API(한국어 V1), 시계열 DB
- **VAMOS 연동**: FinGPT(S7I-002), 소셜 감성(S7I-021), Fear & Greed(S7I-024)
- **V1**: FinBERT(영어) + Claude(한국어) → **V2**: KoFinBERT 로컬 → **V3**: 멀티모달 감성(뉴스+영상+소셜)

### S7I-009 | MED | V2 | AI 투자 논문 추적 — 최신 연구 모니터링

- **모듈 연동**: A(Agent Layer) - Research Node
- **구현 방식**: 금융 AI 최신 논문 자동 추적/요약. 소스: arXiv(q-fin), SSRN, Google Scholar. 키워드: LLM trading, AI portfolio, sentiment analysis, alternative data. VAMOS 활용: Research Node가 주간 투자 AI 논문 다이제스트 생성
- **기술 스택**: arXiv API, SSRN 크롤링, LLM 논문 요약
- **VAMOS 연동**: Research Node(Agent Layer), 콘텐츠 생성(Content Node)
- **V1**: 수동 추적 → **V2**: 자동 다이제스트 → **V3**: 논문 기반 전략 자동 생성

### S7I-010 | MED | V2 | 투자 교육 콘텐츠 — 사용자 금융 리터러시

- **모듈 연동**: H(비즈니스), A(Agent Layer)
- **구현 방식**: VAMOS 사용자의 투자 이해도 향상 콘텐츠. 기본 투자 개념, 리스크 관리, 백테스팅 이해, AI 투자 한계점. "AI가 투자를 대신해주는 것이 아님" 교육 필수
- **기술 스택**: 교육 콘텐츠 시스템, 인터랙티브 튜토리얼
- **VAMOS 연동**: 투자 온보딩(S7I-106), 면책 시스템(S7I-085)
- **V1**: 기본 투자 가이드 문서 → **V2**: 인터랙티브 교육 → **V3**: AI 튜터 모드

---

## I-Part 2: LLM 기반 투자 분석 고도화 (10건)

### S7I-011 | CRITICAL | V1 | 기업 분석 리포트 자동 생성 — 구조화된 분석

- **모듈 연동**: A(Agent Layer) - Research/Content Node
- **구현 방식**: 특정 기업에 대한 포괄적 분석 리포트를 LLM으로 자동 생성. 리포트 구조: 1) 기업 개요(사업, 제품, 시장 위치), 2) 재무 분석(매출/영업이익/순이익 추이 3년, ROE/ROA/영업이익률, YoY 성장률, 부채비율/유동비율), 3) 밸류에이션(PER/PBR/EV/EBITDA 동종업계 비교, 간이 DCF), 4) 산업/경쟁(트렌드, 경쟁사, SWOT), 5) 리스크 요인, 6) 최근 이벤트(3개월 뉴스/공시), 7) AI 분석 요약(확신도 표시 + 면책). 데이터 소스: DART, yfinance, 뉴스 API. 비용: ~₩45/리포트
- **기술 스택**: Claude/GPT 구조화 출력, DART API, yfinance, Markdown 리포트 생성
- **VAMOS 연동**: DART(S7I-005), SEC EDGAR(S7I-006), 재무제표 분석(S7I-013), 면책 시스템(S7I-085)
- **V1**: 수동 요청 시 생성 → **V2**: 관심 종목 정기 자동 생성 → **V3**: 기관급 리포트

### S7I-012 | CRITICAL | V1 | 멀티 소스 교차 검증 — 정보 신뢰도

- **모듈 연동**: A(Agent Layer) - Quant/Research Node
- **구현 방식**: 투자 정보를 다중 소스에서 교차 검증하여 신뢰도 확보. 주가: yfinance + KRX API 교차. 재무제표: DART + 기업 IR + Bloomberg 교차. 뉴스 감성: 3개+ 소스 일치도. 애널리스트: 다수 컨센서스. 신뢰도 점수: 단일 소스 20%, 2개 일치 60%, 3개+ 일치 90%. 상충 시 양측 근거 명시
- **기술 스택**: 교차 검증 파이프라인, 신뢰도 스코어링 엔진
- **VAMOS 연동**: 데이터 파이프라인(7-Component), 뉴스 감성(S7I-008)
- **V1**: 주가/재무 기본 교차 검증 → **V2**: 전체 소스 자동 교차 검증 → **V3**: 신뢰도 AI 모델

### S7I-013 | HIGH | V1 | 재무제표 자동 분석 — 한국/미국 표준

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 재무제표 자동 수집/분석/시각화. 수익성(매출총이익률, 영업이익률, 순이익률, ROE, ROA, ROIC), 성장성(매출 QoQ/YoY, EPS 성장률), 안정성(부채비율, 유동비율, 이자보상배율), 효율성(자산회전율, 재고회전율), 투자(CAPEX/매출, R&D/매출, FCF, FCF Yield). 3년/5년 추이 분석
- **기술 스택**: DART OpenAPI(한국), SEC EDGAR(미국), OpenBB, pandas 분석, JSON + Markdown 출력
- **VAMOS 연동**: DART(S7I-005), OpenBB(S7I-003), 기업 분석(S7I-011)
- **V1**: 기본 재무 지표 자동 계산 → **V2**: 차트 시각화 + AI 해석 → **V3**: 동종업계 자동 비교

### S7I-014 | HIGH | V1 | 밸류에이션 자동 계산 — DCF/비교 분석

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 주요 밸류에이션 지표 자동 계산. 1) 상대 밸류에이션: PER/PBR/EV/EBITDA/PEG 동종업계 비교. 2) 절대 밸류에이션(간이 DCF): 가정(성장률/할인율/영구성장률) 명시, 민감도 분석(성장률 ±2%, 할인율 ±1% 매트릭스), "가정에 따라 결과 크게 달라짐" 경고 필수. 3) 역사적 밸류에이션: 5년 PER/PBR 밴드(현재 위치). 면책: "밸류에이션은 참고 자료"
- **기술 스택**: DCF 모델(Python), 밸류에이션 비교 엔진, 민감도 분석 매트릭스
- **VAMOS 연동**: 재무제표(S7I-013), 기업 분석(S7I-011), 면책(S7I-085)
- **V1**: PER/PBR 비교 + 간이 DCF → **V2**: 고급 DCF + 시각화 → **V3**: 멀티 모델 밸류에이션

### S7I-015 | HIGH | V1 | 섹터/산업 분석 — 탑다운 분석

- **모듈 연동**: A(Agent Layer) - Research Node
- **구현 방식**: 섹터별 동향 분석 및 로테이션 시그널. GICS 11개 섹터별 성과 비교, 섹터 ETF 자금 흐름 분석, 경기 사이클별 섹터 매핑(Expansion/Peak/Contraction/Trough), 한국 KOSPI 업종별 비교
- **기술 스택**: 섹터 ETF 데이터, 경기 사이클 모델, FRED 데이터
- **VAMOS 연동**: FRED(S7I-004), 거시경제 대시보드(S7I-020), 포트폴리오 분석(S7I-044)
- **V1**: 섹터 성과 비교 → **V2**: 로테이션 시그널 + 시각화 → **V3**: AI 섹터 예측

### S7I-016 | HIGH | V1 | 경쟁사 비교 분석 — Peer Comparison

- **모듈 연동**: A(Agent Layer) - Research/Quant Node
- **구현 방식**: 동종업계 경쟁사 비교 분석 자동화. 비교 항목: 시가총액, PER, PBR, 매출성장률, 영업이익률, ROE. 레이더 차트(V2) + 구조화 테이블 출력
- **기술 스택**: Peer Group 분류 엔진, 비교 테이블 생성, 레이더 차트(V2)
- **VAMOS 연동**: 재무제표(S7I-013), 밸류에이션(S7I-014), 기업 분석(S7I-011)
- **V1**: 비교 테이블 자동 생성 → **V2**: 레이더 차트 + AI 해석 → **V3**: 글로벌 Peer 비교

### S7I-017 | HIGH | V1 | 투자 아이디어 생성 — AI 기반 스크리닝

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 조건 기반 종목 스크리닝 + LLM 분석 결합. 예: "PER 10 이하, ROE 15%+, 부채비율 100% 미만, 3년 매출 성장 10%+인 한국 기업". 파이프라인: 1) 조건 파싱, 2) 데이터 필터링, 3) 조건 충족 종목 리스트, 4) 각 종목 LLM 요약, 5) 종합 점수 제안, 6) 면책 표시
- **기술 스택**: 자연어 → 쿼리 변환(LLM), 스크리닝 엔진, 종합 점수 알고리즘
- **VAMOS 연동**: 재무제표(S7I-013), 기업 분석(S7I-011), 면책(S7I-085)
- **V1**: 기본 조건 스크리닝 → **V2**: 자연어 스크리닝 + AI 분석 → **V3**: 복합 전략 스크리닝

### S7I-018 | MED | V2 | 애널리스트 컨센서스 추적 — 목표가 모니터링

- **모듈 연동**: A(Agent Layer) - Research Node
- **구현 방식**: 증권사 애널리스트의 목표가/투자 의견 변화 추적. 소스: TipRanks(참조), FnGuide(한국), Thomson Reuters Eikon(V3)
- **기술 스택**: 컨센서스 데이터 수집, 변화 추적 알림
- **VAMOS 연동**: 기업 분석(S7I-011), 공시 알림(S7I-068)
- **V1**: 수동 조회 → **V2**: 자동 추적 + 변화 알림 → **V3**: 컨센서스 예측 모델

### S7I-019 | MED | V2 | 테마/모멘텀 분석 — 시장 테마 포착

- **모듈 연동**: A(Agent Layer) - Research Node
- **구현 방식**: 현재 시장 테마(AI, 반도체, 친환경 등)와 모멘텀 분석. 뉴스 클러스터링 + 섹터 자금 흐름 + 검색 트렌드(Google Trends) 결합
- **기술 스택**: 뉴스 클러스터링(LLM), Google Trends API, 자금 흐름 분석
- **VAMOS 연동**: 뉴스 감성(S7I-008), 섹터 분석(S7I-015)
- **V1**: 수동 테마 분석 → **V2**: 자동 테마 감지 → **V3**: 테마 기반 전략

### S7I-020 | MED | V2 | 글로벌 매크로 대시보드 — 거시 경제 총정리

- **모듈 연동**: A(Agent Layer) - Quant Node, S(Service Layer)
- **구현 방식**: 주요 거시경제 지표를 한 화면에 요약. 패널: 미국/한국/중국 GDP, CPI, 금리, 실업률, PMI, 환율
- **기술 스택**: FRED API, 한국은행 ECOS, 대시보드 UI(React)
- **VAMOS 연동**: FRED/ECOS(S7I-004), 섹터 분석(S7I-015)
- **V1**: 텍스트 기반 요약 → **V2**: 시각적 대시보드 → **V3**: AI 매크로 해석

---

## I-Part 3: 대안 데이터 (Alternative Data) (10건)

### S7I-021 | HIGH | V1 | 소셜 미디어 감성 분석 — Reddit/X 금융 감성

- **모듈 연동**: A(Agent Layer) - Research Node
- **구현 방식**: Reddit(r/wallstreetbets, r/stocks), X(Twitter) 금융 감성 분석. 파이프라인: 1) 수집(Reddit API, X API/크롤링), 2) 필터(금융 관련만), 3) FinBERT 감성 분류, 4) 종목별/시장별 감성 점수(시간 가중), 5) 감성 급변 알림. 한국: 네이버 금융 토론방, 클리앙, 디시인사이드 주식갤, 에프엔가이드
- **기술 스택**: Reddit API, X API, FinBERT, 시계열 감성 DB
- **VAMOS 연동**: 뉴스 감성(S7I-008), Fear & Greed(S7I-024), FinGPT(S7I-002)
- **V1**: 수동 분석 → **V2**: 자동 수집 + 실시간 대시보드 → **V3**: 예측 모델

### S7I-022 | HIGH | V1 | 내부자 거래 추적 — 임원 매수/매도 시그널

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 기업 임원 자사주 매수/매도 추적으로 시그널 생성. 소스: SEC Form 4(미국), DART 임원 주식 거래(한국). 분석: 클러스터 매수(다수 임원 동시 매수) → 강한 시그널, CEO/CFO 매수 vs 일반 임원(가중치), 정기 매도(스톡옵션) vs 비정기 매도 구분
- **기술 스택**: SEC Form 4 파서, DART 임원거래 API, 시그널 생성 엔진
- **VAMOS 연동**: SEC EDGAR(S7I-006), DART(S7I-005), 가격 알림(S7I-067)
- **V1**: 기본 추적 + 알림 → **V2**: 패턴 분석 + 시그널 → **V3**: 내부자 거래 전략

### S7I-023 | HIGH | V1 | 기관 포트폴리오 추적 — 13F 분석

- **모듈 연동**: A(Agent Layer) - Quant/Research Node
- **구현 방식**: 유명 기관/펀드 포트폴리오 변동 추적(SEC 13F). 대표 추적: Berkshire Hathaway(Buffett), Bridgewater(Dalio), ARK Invest(Wood), Soros Fund, Renaissance Technologies. 분석: 신규 매수, 비중 확대/축소, 완전 매도, 집중도 변화. 갱신: 분기별(13F 제출 후 45일). 주의: "45일 지연 데이터 → 현재 포지션 아닐 수 있음" 고지
- **기술 스택**: SEC 13F 파서, 포트폴리오 비교 엔진, 변동 추적 알림
- **VAMOS 연동**: SEC EDGAR(S7I-006), 포트폴리오 분석(S7I-044)
- **V1**: 주요 기관 5개 추적 → **V2**: 20+ 기관 + 자동 알림 → **V3**: 기관 전략 복제 분석

### S7I-024 | HIGH | V1 | Fear & Greed Index — 시장 심리 지표

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 시장 공포/탐욕 지수 종합 분석. 구성: 1) CNN Fear & Greed(미국), 2) VIX(변동성), 3) Put/Call Ratio, 4) Safe Haven Demand(금/채권), 5) Market Breadth(상승/하락 비율), 6) Alternative.me Crypto Fear & Greed, 7) 한국: KOSPI 투자심리선, 고객예탁금. 종합 점수: 0(극단 공포)~100(극단 탐욕). 투자 활용: "남들이 공포에 떨 때 매수" 역발상 시그널
- **기술 스택**: CNN F&G API, Alternative.me API, VIX 데이터, 종합 스코어링 엔진
- **VAMOS 연동**: 뉴스 감성(S7I-008), 소셜 감성(S7I-021), 리스크 관리(S7I Part 6)
- **V1**: 종합 심리 지표 표시 → **V2**: 시각적 대시보드 + 알림 → **V3**: 심리 기반 전략

### S7I-025 | HIGH | V1 | 특허/R&D 데이터 — 기술 혁신 분석

- **모듈 연동**: A(Agent Layer) - Research Node
- **구현 방식**: 기업 특허 출원 및 R&D 투자 추적. 소스: Google Patents(무료), KIPRIS(한국 특허). 분석: 연간 특허 출원 수 추이, AI/반도체 등 핵심 분야 특허, 경쟁사 대비 기술 우위
- **기술 스택**: Google Patents API, KIPRIS API, 특허 분류 분석
- **VAMOS 연동**: 기업 분석(S7I-011), 경쟁사 비교(S7I-016)
- **V1**: 기본 특허 건수 조회 → **V2**: 트렌드 분석 + 기술 지도 → **V3**: 특허 기반 투자 시그널

### S7I-026 | HIGH | V1 | 크립토 온체인 데이터 — 블록체인 분석

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 블록체인 온체인 데이터 분석(Part 9와 연계). 소스: Glassnode(Free tier), Dune Analytics(무료 대시보드). 지표: 거래소 순유입/유출, 고래 지갑 이동, NVT Ratio, MVRV
- **기술 스택**: Glassnode API, Dune Analytics API, 온체인 지표 엔진
- **VAMOS 연동**: 크립토 시장(S7I-075), 크립토 감성(S7I-077)
- **V1**: 핵심 온체인 지표 조회 → **V2**: 자동 추적 + 알림 → **V3**: 온체인 전략

### S7I-027 | MED | V2 | 웹 트래픽/앱 사용량 — 디지털 성장 지표

- **모듈 연동**: A(Agent Layer) - Research Node
- **구현 방식**: 기업 웹사이트 트래픽과 앱 다운로드 추적. 기업 성장 선행 지표, 경쟁사 비교 활용
- **기술 스택**: SimilarWeb 참조, 앱 스토어 데이터
- **VAMOS 연동**: 기업 분석(S7I-011), 경쟁사 비교(S7I-016)
- **V1**: 수동 조회 → **V2**: 자동 추적 → **V3**: 디지털 성장 예측

### S7I-028 | MED | V2 | ESG 데이터 — ESG 점수 분석

- **모듈 연동**: A(Agent Layer) - Research Node
- **구현 방식**: 기업 ESG(환경/사회/거버넌스) 점수 분석. 소스: MSCI ESG(참조), Sustainalytics, 한국기업지배구조원. ESG 스크리닝, 지속가능 투자 전략
- **기술 스택**: ESG 데이터 수집, 스코어링 통합
- **VAMOS 연동**: 기업 분석(S7I-011), 스크리닝(S7I-017)
- **V1**: ESG 정보 참조 → **V2**: ESG 스크리닝 통합 → **V3**: ESG 투자 전략

### S7I-029 | MED | V2 | 고용 데이터 — 채용 트렌드 분석

- **모듈 연동**: A(Agent Layer) - Research Node
- **구현 방식**: 기업 채용 공고 추적으로 성장/구조조정 시그널 감지. 소스: LinkedIn, Glassdoor, 사람인, 잡코리아. 대량 채용 = 성장 시그널, 대량 해고 = 구조조정 경고
- **기술 스택**: 채용 공고 크롤링, 트렌드 분석
- **VAMOS 연동**: 기업 분석(S7I-011), 대안 데이터 종합
- **V1**: 수동 조회 → **V2**: 자동 추적 + 시그널 → **V3**: 고용 기반 전략

### S7I-030 | MED | V2 | 이벤트 캘린더 — 투자 이벤트 추적

- **모듈 연동**: A(Agent Layer) - Quant Node, S(Service Layer)
- **구현 방식**: 실적발표, FOMC, 옵션 만기, IPO 등 투자 이벤트 자동 추적. 이벤트: 실적발표(한국/미국), FOMC/ECB/한은 금통위, 옵션/선물 만기일(쿼드러플 위칭), IPO/공모, 배당락일/지급일
- **기술 스택**: 이벤트 캘린더 DB, API 연동, 알림 시스템
- **VAMOS 연동**: 경제 지표 알림(S7I-071), 배당 캘린더(S7I-045), 공시 알림(S7I-068)
- **V1**: 핵심 이벤트 수동 등록 → **V2**: 자동 캘린더 + 알림 → **V3**: 이벤트 기반 전략

---

## I-Part 4: 한국 시장 특화 보강 (10건)

### S7I-031 | CRITICAL | V1 | 키움증권 OpenAPI+ 연동 — 한국 주식 실시간

- **모듈 연동**: A(Agent Layer) - Trading Node, I(Infra Core)
- **구현 방식**: 키움증권 OpenAPI+로 한국 주식 실시간 시세 및 주문 기능. 실시간 시세(현재가/호가/체결), 일봉/분봉 차트, 계좌 잔고, 주문(매수/매도) — 사용자 최종 확인 필수. 제약: Windows 전용(OCX), 영업일 09:00-15:30. 대안: 한국투자증권 KIS API(REST, 크로스플랫폼)
- **기술 스택**: 키움 OpenAPI+(OCX, Windows), Python COM 인터페이스
- **VAMOS 연동**: Trading Node(Agent Layer), 투자 안전장치(S7I-084), KIS API(S7I-032)
- **V1**: 데이터 조회 위주 → **V2**: 주문 기능(확인 프로세스 필수) → **V3**: 자동 매매 프레임워크

### S7I-032 | CRITICAL | V1 | 한국투자증권 KIS API — REST 기반 대안

- **모듈 연동**: A(Agent Layer) - Trading Node, I(Infra Core)
- **구현 방식**: REST API 기반 크로스플랫폼 한국 증권사 API. Windows 독립, REST API, 모바일 호환. 시세 조회, 잔고 조회, 주문(매수/매도/정정/취소). VAMOS 우선 채택: KIS API(크로스플랫폼) → 키움(Windows만 백업)
- **기술 스택**: KIS REST API, OAuth 인증, JSON 응답 처리
- **VAMOS 연동**: Trading Node(Agent Layer), 키움 API(S7I-031), 투자 안전장치(S7I-084)
- **V1**: KIS 시세/잔고 조회 → **V2**: 주문 기능 + 안전장치 → **V3**: 자동 매매

### S7I-033 | CRITICAL | V1 | 한국 ETF 분석 — 한국 ETF 포트폴리오

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 한국 ETF 활용 포트폴리오 구성 분석. 카테고리: 지수(KODEX 200, TIGER 200), 섹터(반도체, 2차전지, 바이오), 해외(S&P500, 나스닥100), 채권(국채, 회사채), 원자재(금, 은, 원유), 인컴(고배당, 리츠), 레버리지/인버스. 분석: 수익률(1M~3Y), 추적오차, 총보수, 거래량, 설정액
- **기술 스택**: KRX ETF 데이터, yfinance 한국 ETF, 비교 분석 엔진
- **VAMOS 연동**: 포트폴리오 최적화(S7I-041), 자산배분(S7I-042), 리밸런싱(S7I-043)
- **V1**: ETF 비교 분석 → **V2**: ETF 기반 포트폴리오 추천 → **V3**: 자동 ETF 리밸런싱

### S7I-034 | HIGH | V1 | 한국 세금 계산 — 투자 세금 자동 계산

- **모듈 연동**: A(Agent Layer) - Quant/Trading Node
- **구현 방식**: 한국 투자자 세금 자동 계산. 주식: 양도소득세(대주주 10억+), 금투세(2027 시행, 5천만원 초과 22%), 증권거래세(0.18%), 배당소득세(15.4%). 해외주식: 양도소득세(250만원 공제 후 22%), 미국 배당 15% 원천. 크립토: 기타소득세(250만원 공제 후 22%). VAMOS: 연간 실현 손익 자동 계산, 세금 예상액 실시간, 세금 최적화(손실 상계), "정확한 세금은 세무사 확인" 면책
- **기술 스택**: 세금 계산 엔진, 한국 세법 규칙 DB, 손익 추적 시스템
- **VAMOS 연동**: 포트폴리오 분석(S7I-044), Tax-Loss Harvesting(S7I-048), 면책(S7I-085)
- **V1**: 기본 세금 계산기 → **V2**: 세금 최적화 제안 → **V3**: 세무사 연동

### S7I-035 | HIGH | V1 | 한국 투자 용어 사전 — 한국어 금융 NLP

- **모듈 연동**: A(Agent Layer) - 전체, M(Memory Layer)
- **구현 방식**: 한국 특유 투자 용어를 LLM이 정확히 이해하도록 지원. 용어: 개미(개인투자자), 외인, 기관, 따상(공모가 2배+상한가), 따따블, 물타기, 불타기, 손절, 익절, 흑자전환, 어닝서프라이즈/쇼크, 테마주, 작전주, 공매도, 대차잔고, 신용잔고, 코스닥 vs 코스피, KONEX. 구현: 용어 사전 JSON → 프롬프트 컨텍스트 주입
- **기술 스택**: 용어 사전 JSON, 프롬프트 인젝션, 한국어 NLP
- **VAMOS 연동**: 한국어 벤치마크(S7G Part 2), 메모리 시스템(STEP7-B)
- **V1**: 용어 사전 200+ 항목 구축 → **V2**: 자동 확장 + 사용자 정의 → **V3**: 한국어 금융 모델

### S7I-036 | HIGH | V1 | 한국 배당주 분석 — 배당 투자 전략

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 한국 고배당주 분석 및 배당 투자 전략 지원. 분석: 배당수익률, 배당성장률, 배당성향, 배당락 일정, 배당금 수령 예상
- **기술 스택**: KRX 배당 데이터, DART 재무정보, 배당 분석 엔진
- **VAMOS 연동**: 배당 캘린더(S7I-045), 재무제표(S7I-013), 세금(S7I-034)
- **V1**: 배당 분석 기본 → **V2**: 배당 투자 전략 제안 → **V3**: 배당 포트폴리오 자동화

### S7I-037 | HIGH | V1 | IPO/공모 분석 — 신규 상장 분석

- **모듈 연동**: A(Agent Layer) - Research Node
- **구현 방식**: 한국 IPO 종목 분석 지원. 분석: 공모가 적정성, 수요예측 결과, 동종업계 비교, 상장 후 예상. 소스: DART 증권신고서, KRX IPO 일정
- **기술 스택**: DART 증권신고서 파서, IPO 분석 모델
- **VAMOS 연동**: DART(S7I-005), 밸류에이션(S7I-014), 면책(S7I-085)
- **V1**: 기본 IPO 정보 제공 → **V2**: LLM 분석 리포트 → **V3**: IPO 성과 예측

### S7I-038 | HIGH | V2 | 한국 펀드 분석 — 펀드/ETF 비교

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 한국 공모펀드/사모펀드 비교 분석. 소스: 금융투자협회, FnGuide
- **기술 스택**: 펀드 데이터 수집, 성과 비교 엔진
- **VAMOS 연동**: ETF 분석(S7I-033), 포트폴리오(S7I-044)
- **V1**: ETF 위주 → **V2**: 펀드 비교 추가 → **V3**: 펀드 vs ETF 통합 분석

### S7I-039 | MED | V2 | 한국 부동산 연계 — REITs/부동산 분석

- **모듈 연동**: A(Agent Layer) - Research Node
- **구현 방식**: 한국 REITs(리츠), 부동산 시장 분석. 소스: 한국리츠협회, 국토교통부 실거래가
- **기술 스택**: 부동산 데이터 API, 리츠 분석 엔진
- **VAMOS 연동**: 포트폴리오(S7I-044), 자산배분(S7I-042)
- **V1**: 리츠 기본 정보 → **V2**: 부동산/리츠 분석 → **V3**: 부동산 포트폴리오 통합

### S7I-040 | MED | V2 | 한국 연금/IRP — 절세 투자 전략

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 연금저축/IRP를 통한 절세 투자 전략 분석. 세액공제 한도, 적격 ETF 추천, 자산배분 제안
- **기술 스택**: 세금 규칙 엔진, ETF 적격 DB
- **VAMOS 연동**: 세금 계산(S7I-034), ETF 분석(S7I-033), 자산배분(S7I-042)
- **V1**: 연금 기본 안내 → **V2**: 절세 전략 제안 → **V3**: 연금 포트폴리오 최적화

---

## I-Part 5: 포트폴리오 최적화 심화 (8건)

### S7I-041 | HIGH | V1 | Modern Portfolio Theory — 평균-분산 최적화

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: MPT 기반 포트폴리오 최적화. scipy.optimize.minimize로 최대 샤프 비율 포트폴리오, 최소 변동성 포트폴리오, 효율적 프론티어(20 포인트) 계산. risk_free_rate=0.035(한국 기준금리). 시각화: 효율적 프론티어 그래프(V2 UI). 면책: "과거 데이터 기반이며 미래 수익을 보장하지 않습니다"
- **기술 스택**: scipy, numpy, pandas, 포트폴리오 최적화 엔진(Python)
- **VAMOS 연동**: 재무제표(S7I-013), 포트폴리오 분석(S7I-044), 면책(S7I-085)
- **V1**: 기본 MPT 최적화 → **V2**: 효율적 프론티어 시각화 → **V3**: 제약조건 최적화

### S7I-042 | HIGH | V1 | 자산배분 전략 — 전략적 자산배분

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 주요 자산배분 전략 분석/추천. 고전: 60/40, All Weather(레이 달리오), Permanent Portfolio(해리 브라운), Golden Butterfly. 현대: Risk Parity, Black-Litterman, Factor Investing. VAMOS 구현: 1) 위험 성향 평가(5단계), 2) 투자 기간 설정, 3) 전략 비교(백테스트), 4) 맞춤 자산배분 제안, 5) 리밸런싱 알림
- **기술 스택**: 자산배분 모델(Python), 백테스트 엔진, 설문 시스템
- **VAMOS 연동**: 백테스팅(S7I-059), 리밸런싱(S7I-043), ETF 분석(S7I-033)
- **V1**: 고전 전략 + 비교 → **V2**: 맞춤 제안 + 시각화 → **V3**: 동적 자산배분

### S7I-043 | HIGH | V1 | 리밸런싱 — 자동 리밸런싱 알림

- **모듈 연동**: A(Agent Layer) - Quant/Trading Node
- **구현 방식**: 포트폴리오 비중 이탈 시 리밸런싱 알림. 목표 비중 설정(예: 주식60/채권30/금10), 이탈 임계값(±5%), 리밸런싱 필요 시 구체적 매수/매도 수량 계산, 세금 효율 리밸런싱(손실 상계 고려). 주기: 수동/월간/분기별/밴드 기반
- **기술 스택**: 리밸런싱 계산 엔진, 알림 시스템, 세금 최적화 로직
- **VAMOS 연동**: 포트폴리오 분석(S7I-044), 세금(S7I-034), Trading Node(Agent Layer)
- **V1**: 알림 + 수량 계산 → **V2**: 원클릭 리밸런싱(V2 주문 연동) → **V3**: 자동 리밸런싱

### S7I-044 | HIGH | V1 | 포트폴리오 분석 대시보드 — 현황 시각화

- **모듈 연동**: A(Agent Layer) - Quant Node, S(Service Layer)
- **구현 방식**: 현재 포트폴리오 다각적 분석. 자산별 비중(파이 차트), 섹터별 노출(GICS 11섹터), 지역별 노출(한국/미국/기타), 위험 지표(베타, 변동성, VaR), 수익률(일/주/월/연, 벤치마크 대비), 상관관계 매트릭스(종목 간)
- **기술 스택**: 포트폴리오 분석 엔진, 차트 라이브러리(recharts/Chart.js), 대시보드 UI
- **VAMOS 연동**: 리밸런싱(S7I-043), VaR(S7I-049), 드로다운(S7I-052)
- **V1**: 텍스트 기반 분석 → **V2**: 시각적 대시보드 → **V3**: 실시간 업데이트

### S7I-045 | HIGH | V1 | 배당 캘린더 — 배당금 수령 일정

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 보유 종목 배당 일정 및 예상 배당금 추적. 배당락일, 배당기준일, 배당금 지급일, 예상 배당금 표시
- **기술 스택**: 배당 데이터 DB, 캘린더 UI, 알림 시스템
- **VAMOS 연동**: 한국 배당주(S7I-036), 이벤트 캘린더(S7I-030), 포트폴리오(S7I-044)
- **V1**: 배당 일정 + 예상 금액 → **V2**: 시각적 캘린더 → **V3**: 배당 최적화 전략

### S7I-046 | MED | V2 | Factor 분석 — 팩터 노출 분석

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 포트폴리오의 팩터(Value/Growth/Size/Momentum/Quality) 노출 분석. 과도한 팩터 집중 경고, 팩터 분산 제안
- **기술 스택**: 팩터 분석 모델, Fama-French 데이터
- **VAMOS 연동**: 포트폴리오 분석(S7I-044), 자산배분(S7I-042)
- **V1**: 기본 팩터 정보 → **V2**: 팩터 노출 분석 + 시각화 → **V3**: 팩터 기반 전략

### S7I-047 | MED | V2 | 시나리오 분석 — What-If 시뮬레이션

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: "만약 ~한다면" 시나리오 분석. 시나리오: 금리 +1%, 환율 10% 상승, 특정 종목 -30%, 경기침체
- **기술 스택**: 시나리오 시뮬레이션 엔진, 민감도 분석
- **VAMOS 연동**: 스트레스 테스트(S7I-054), 포트폴리오 분석(S7I-044)
- **V1**: 기본 시나리오 → **V2**: 커스텀 시나리오 + 시각화 → **V3**: 몬테카를로 시뮬레이션

### S7I-048 | MED | V2 | 세금 최적화 — Tax-Loss Harvesting

- **모듈 연동**: A(Agent Layer) - Quant/Trading Node
- **구현 방식**: 손실 종목 매도하여 세금 줄이는 전략 추천. 해외주식 양도소득세, 금투세(2027 시행 시) 적용
- **기술 스택**: Tax-Loss Harvesting 알고리즘, 세금 시뮬레이션
- **VAMOS 연동**: 세금 계산(S7I-034), 포트폴리오(S7I-044), 리밸런싱(S7I-043)
- **V1**: 세금 기본 정보 → **V2**: TLH 자동 제안 → **V3**: 자동 실행(사용자 확인)

---

## I-Part 6: 리스크 관리 고도화 (10건)

### S7I-049 | CRITICAL | V1 | VaR 계산 — Value at Risk

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 포트폴리오 최대 손실 가능 금액 계산. 방법: 1) Historical VaR(과거 수익률 분포), 2) Parametric VaR(정규분포 가정), 3) Monte Carlo VaR(시뮬레이션). 예: "포트폴리오 1억원, 95% VaR = -2.3%" → "하루 95% 확률로 최대 230만원 이내 손실". 일간/주간/월간 VaR 표시
- **기술 스택**: VaR 계산 엔진(Python), numpy, scipy, Monte Carlo 시뮬레이션
- **VAMOS 연동**: 포트폴리오 분석(S7I-044), 리스크 스코어카드(S7I-053), 스트레스 테스트(S7I-054)
- **V1**: Historical + Parametric VaR → **V2**: Monte Carlo VaR + 시각화 → **V3**: 조건부 VaR(CVaR)

### S7I-050 | CRITICAL | V1 | 최대 손실 제한 — Stop Loss 관리

- **모듈 연동**: A(Agent Layer) - Trading Node
- **구현 방식**: 개별 종목/포트폴리오 전체 손절 관리. 개별 -10%~-20%(사용자 설정), 포트폴리오 전체 -5%~-15%, 트레일링 스톱(고점 대비 -X%). 알림: -5% 주의, -10% 경고+손절 제안, -15%+ 긴급+강력 손절 권고. 자동 매도 아님: 알림+제안만, 실행은 사용자
- **기술 스택**: Stop Loss 엔진, 가격 모니터링, 알림 시스템
- **VAMOS 연동**: 가격 알림(S7I-067), Trading Node(Agent Layer), 투자 안전장치(S7I-084)
- **V1**: 알림 + 제안 → **V2**: 원클릭 손절(사용자 확인) → **V3**: 자동 손절(명시적 동의 시)

### S7I-051 | HIGH | V1 | 상관관계 분석 — 분산 투자 검증

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 보유 종목 간 상관관계 분석으로 분산 효과 검증. 상관관계 매트릭스, 히트맵 시각화. 상관관계 0.8+ 종목 쌍 → "분산 부족" 경고
- **기술 스택**: pandas 상관관계 계산, 히트맵(seaborn/plotly)
- **VAMOS 연동**: 포트폴리오 분석(S7I-044), MPT(S7I-041)
- **V1**: 상관관계 계산 + 경고 → **V2**: 히트맵 시각화 → **V3**: 동적 상관관계 추적

### S7I-052 | HIGH | V1 | 드로다운 분석 — 최대 낙폭 관리

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 포트폴리오 최대 낙폭(MDD) 분석. 현재 MDD, 역사적 MDD, 회복 시간 측정. MDD 설정 임계값 초과 시 알림
- **기술 스택**: MDD 계산 엔진, 회복 기간 추적
- **VAMOS 연동**: 포트폴리오 분석(S7I-044), 백테스트 성과(S7I-062)
- **V1**: MDD 계산 + 알림 → **V2**: 시각화 + 회복 분석 → **V3**: MDD 예측

### S7I-053 | HIGH | V1 | 리스크 스코어카드 — 투자 위험 종합 점수

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 포트폴리오 리스크 종합 점수. 변동성 위험(25점): 포트폴리오 표준편차. 집중 위험(25점): 단일 종목/섹터 비중. 유동성 위험(20점): 거래량 대비 보유량. 매크로 위험(15점): 금리/환율 민감도. 이벤트 위험(15점): 실적/규제/정치. 등급: 0-30(안전)/31-60(보통)/61-80(주의)/81-100(위험)
- **기술 스택**: 리스크 스코어링 엔진, 가중 평균 모델
- **VAMOS 연동**: VaR(S7I-049), 상관관계(S7I-051), 포트폴리오(S7I-044)
- **V1**: 종합 리스크 점수 → **V2**: 시각적 스코어카드 → **V3**: AI 리스크 예측

### S7I-054 | HIGH | V1 | 스트레스 테스트 — 극단 시나리오 시뮬레이션

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 역사적 위기 상황에서 포트폴리오 성과 시뮬레이션. 역사적: 2008 금융위기(-57%), 2020 코로나(-34%), 2022 금리인상(-25%), 1997 IMF(-72%), 2000 닷컴(-78%). 커스텀: S&P500 -30%, 한국 금리 +2%, 원/달러 1500원, 특정 섹터 -50%
- **기술 스택**: 스트레스 테스트 엔진, 역사적 데이터 DB, 시뮬레이션
- **VAMOS 연동**: VaR(S7I-049), 포트폴리오(S7I-044), 시나리오 분석(S7I-047)
- **V1**: 역사적 시나리오 5개 → **V2**: 커스텀 시나리오 + 시각화 → **V3**: AI 시나리오 생성

### S7I-055 | HIGH | V2 | 포지션 사이징 — 켈리 기준

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: Kelly Criterion 기반 최적 포지션 크기 계산. Kelly% = W - (1-W)/R (W=승률, R=평균수익/평균손실). Half-Kelly(50%), Quarter-Kelly(25%) 보수적 접근 권장. "Kelly는 이론적 최적값이며, 실제로는 Half-Kelly 이하 권장"
- **기술 스택**: Kelly 계산기, 포지션 사이징 엔진
- **VAMOS 연동**: 백테스트 성과(S7I-062), Trading Node(Agent Layer)
- **V1**: Kelly 계산 기본 → **V2**: 자동 포지션 사이징 제안 → **V3**: 동적 포지션 조절

### S7I-056 | MED | V2 | 환율 리스크 — 해외 투자 환율 관리

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 해외 투자 시 환율 변동 리스크 분석. 환율 민감도, 환헤지 비용, 환율 전망
- **기술 스택**: 환율 데이터 API, 환율 민감도 분석
- **VAMOS 연동**: 포트폴리오(S7I-044), FRED(S7I-004)
- **V1**: 환율 정보 표시 → **V2**: 환율 민감도 분석 → **V3**: 환헤지 전략

### S7I-057 | MED | V2 | 유동성 리스크 — 거래량 분석

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 보유 종목 유동성 리스크 분석. 일 거래량 대비 보유 비중 10%+ 시 유동성 경고
- **기술 스택**: 거래량 분석, 유동성 스코어링
- **VAMOS 연동**: 포트폴리오(S7I-044), 리스크 스코어카드(S7I-053)
- **V1**: 기본 유동성 정보 → **V2**: 유동성 경고 시스템 → **V3**: 유동성 조정 최적화

### S7I-058 | MED | V2 | 블랙 스완 대비 — 꼬리 리스크 관리

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 극단적 사건(블랙 스완)에 대한 대비 전략. 풋옵션 헤지(V3), 안전자산 비중, 현금 버퍼 유지
- **기술 스택**: 꼬리 리스크 모델, Fat-tail 분포 분석
- **VAMOS 연동**: 스트레스 테스트(S7I-054), VaR(S7I-049)
- **V1**: 꼬리 리스크 교육 → **V2**: 대비 전략 제안 → **V3**: 자동 헤지

---

## I-Part 7: 백테스팅/시뮬레이션 보강 (8건)

### S7I-059 | CRITICAL | V1 | 백테스팅 엔진 통합 — Blue Node 완성

- **모듈 연동**: A(Agent Layer) - Quant Node(Blue Node)
- **구현 방식**: 기존 GAP인 백테스팅 Blue Node 통합 완성. BacktestNode 클래스: run_backtest(strategy, data, config) → 수익률 시계열, 성과 지표(Sharpe, MDD, Win Rate), 거래 내역, 시각화 데이터. walk_forward_validation(과적합 방지). monte_carlo_simulation(견고성 검증). 백엔드: vectorbt(고속), backtrader(유연)
- **기술 스택**: vectorbt, backtrader, pandas, numpy, Python
- **VAMOS 연동**: Quant Node(Agent Layer), 7-Component Pipeline, RSI_BB 전략(S7I-060)
- **V1**: 기본 백테스트 → **V2**: Walk-Forward + 몬테카를로 → **V3**: 실시간 전략 검증

### S7I-060 | CRITICAL | V1 | RSI_BB 전략 5년 데이터 확보 — GAP-01 해결

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 기존 INSUFFICIENT_SAMPLE 이슈 해결. 데이터: 미국 yfinance 5년+ 일봉(S&P500), 한국 KRX 5년+(KOSPI200), 크립토 CoinGecko 3년+. Grid Search: RSI Period[7,14,21], Oversold[25,30,35,40], Overbought[60,65,70,75], BB Period[20], BB Std[1.5,2.0,2.5]. 검증: 51% Gate 통과, Walk-Forward 안정성, 시장 조건별(상승/하락/횡보)
- **기술 스택**: yfinance, KRX 데이터, CoinGecko, Grid Search 프레임워크
- **VAMOS 연동**: 백테스팅(S7I-059), 51% Gate System, 과적합 방지(S7I-061)
- **V1**: 데이터 수집 + Grid Search → **V2**: 전략 최적화 + 검증 → **V3**: 다중 전략 레지스트리

### S7I-061 | HIGH | V1 | 과적합 방지 — 견고성 검증 체계

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 백테스팅 과적합(Overfitting) 방지. Walk-Forward Optimization(훈련/검증 분리), 몬테카를로 시뮬레이션(무작위 변동 적용), Out-of-Sample 테스트(최신 1년 테스트), 파라미터 안정성 검사(인접 파라미터 유사 성과?), 거래 횟수 최소 요건(연 30회+)
- **기술 스택**: Walk-Forward 프레임워크, Monte Carlo 시뮬레이션, 파라미터 안정성 분석
- **VAMOS 연동**: 백테스팅(S7I-059), RSI_BB(S7I-060), 백테스트 성과(S7I-062)
- **V1**: Walk-Forward + OOS 테스트 → **V2**: 몬테카를로 + 파라미터 안정성 → **V3**: AI 기반 과적합 탐지

### S7I-062 | HIGH | V1 | 백테스트 성과 지표 — 종합 성과 분석

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 표준화된 성과 지표. 수익: CAGR, 총수익률, Alpha(벤치마크 대비). 리스크: 연 변동성, MDD, VaR(95%), Calmar Ratio(CAGR/MDD). 효율: Sharpe Ratio(>1.0 목표), Sortino Ratio, Information Ratio. 거래: 승률(>51% 목표), Profit Factor, 거래 빈도, 수수료 포함 순수익
- **기술 스택**: 성과 지표 계산 엔진, quantstats 라이브러리
- **VAMOS 연동**: 백테스팅(S7I-059), 51% Gate, 전략 비교(S7I-064)
- **V1**: 핵심 지표 10개 → **V2**: 전체 지표 + 시각화 → **V3**: 자동 성과 리포트

### S7I-063 | HIGH | V2 | Paper Trading — 모의 투자

- **모듈 연동**: A(Agent Layer) - Trading Node
- **구현 방식**: 실제 돈 없이 전략 실시간 테스트. 가상 계좌(초기 자본 설정), 실시간 시세 기반 가상 거래, 실제 매매 동일 수수료/슬리피지 적용, 일일 P&L + 누적 수익률. 51% Gate 통과 후에만 실제 매매 고려
- **기술 스택**: Paper Trading 엔진, 가상 포트폴리오 DB, 실시간 시세 연동
- **VAMOS 연동**: 백테스팅(S7I-059), Trading Node(Agent Layer), 51% Gate
- **V1**: 백테스트 위주 → **V2**: 실시간 Paper Trading → **V3**: Paper → 실전 전환

### S7I-064 | HIGH | V2 | 전략 비교 프레임워크 — 전략 간 A/B 테스트

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 여러 전략 성과를 표준화된 방식으로 비교. 동일 기간, 동일 유니버스, 동일 비용 가정
- **기술 스택**: 전략 비교 프레임워크, 표준화 벤치마크 셋
- **VAMOS 연동**: 백테스팅(S7I-059), 백테스트 성과(S7I-062)
- **V1**: 수동 비교 → **V2**: 표준화 비교 대시보드 → **V3**: AI 전략 추천

### S7I-065 | MED | V2 | 시장 조건 분류 — 시장 레짐 감지

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 현재 시장이 상승/하락/횡보/고변동성인지 분류. 이동평균, VIX, 추세 지표 조합. 시장 조건에 맞는 전략 자동 전환
- **기술 스택**: 시장 레짐 분류 모델(HMM, 규칙 기반)
- **VAMOS 연동**: 백테스팅(S7I-059), Fear & Greed(S7I-024)
- **V1**: 규칙 기반 분류 → **V2**: ML 레짐 감지 → **V3**: 레짐 기반 자동 전략 전환

### S7I-066 | MED | V2 | 슬리피지/수수료 모델 — 현실적 비용 모델링

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 백테스트에서 현실적 거래 비용 반영. 고정 수수료 + 슬리피지(거래량 함수) + 시장 충격
- **기술 스택**: 거래 비용 모델, 슬리피지 추정 엔진
- **VAMOS 연동**: 백테스팅(S7I-059), 백테스트 성과(S7I-062)
- **V1**: 고정 수수료 모델 → **V2**: 동적 슬리피지 모델 → **V3**: 시장 충격 모델

---

## I-Part 8: 실시간 데이터 & 알림 (8건)

### S7I-067 | HIGH | V1 | 가격 알림 — 목표가/손절가 알림

- **모듈 연동**: A(Agent Layer) - Trading Node, S(Service Layer)
- **구현 방식**: 관심 종목 가격이 설정 조건 충족 시 알림. 목표가 도달, 손절가 도달, 거래량 급증, 급등/급락
- **기술 스택**: 가격 모니터링 엔진, 알림 시스템(데스크톱 알림 V1, 푸시 V2)
- **VAMOS 연동**: Stop Loss(S7I-050), Trading Node(Agent Layer)
- **V1**: 데스크톱 알림 → **V2**: 모바일 푸시 → **V3**: 다채널 알림

### S7I-068 | HIGH | V1 | 공시/뉴스 알림 — 실시간 이벤트 알림

- **모듈 연동**: A(Agent Layer) - Research Node
- **구현 방식**: 보유/관심 종목 관련 공시/뉴스 실시간 알림. 소스: DART(공시), 뉴스 API, SEC EDGAR
- **기술 스택**: 공시 모니터링(DART API 폴링), 뉴스 피드, 알림 시스템
- **VAMOS 연동**: DART(S7I-005), SEC EDGAR(S7I-006), 뉴스 감성(S7I-008)
- **V1**: 핵심 공시 알림 → **V2**: 뉴스 + AI 요약 알림 → **V3**: 맞춤 필터링

### S7I-069 | HIGH | V1 | 포트폴리오 일일 리포트 — 자동 일간 요약

- **모듈 연동**: A(Agent Layer) - Content Node
- **구현 방식**: 매일 장 마감 후 포트폴리오 일일 리포트 자동 생성. 일일 수익/손실, 주요 종목 변동, 뉴스 요약, 이벤트 캘린더
- **기술 스택**: 리포트 생성 엔진(LLM), 스케줄러, Markdown 템플릿
- **VAMOS 연동**: 포트폴리오(S7I-044), 뉴스 감성(S7I-008), Content Node(Agent Layer)
- **V1**: 텍스트 일일 리포트 → **V2**: 시각적 리포트 → **V3**: 맞춤 리포트 형식

### S7I-070 | HIGH | V1 | 시장 오버뷰 — 매일 시장 요약

- **모듈 연동**: A(Agent Layer) - Research/Content Node
- **구현 방식**: 매일 아침/저녁 글로벌 시장 요약. 미국 마감(S&P/나스닥/다우), 한국 마감(KOSPI/KOSDAQ), 환율, 금리, 원자재
- **기술 스택**: 시장 데이터 API, LLM 요약 생성, 스케줄러
- **VAMOS 연동**: FRED(S7I-004), 거시경제 대시보드(S7I-020)
- **V1**: 텍스트 시장 요약 → **V2**: 시각적 대시보드 → **V3**: AI 시장 해석

### S7I-071 | HIGH | V1 | 경제 지표 알림 — 주요 경제 지표 발표 알림

- **모듈 연동**: A(Agent Layer) - Research Node
- **구현 방식**: FOMC, CPI, 고용지표 등 주요 경제 지표 발표 시 알림 + 요약
- **기술 스택**: 경제 캘린더 DB, 알림 시스템, LLM 해석
- **VAMOS 연동**: FRED(S7I-004), 이벤트 캘린더(S7I-030)
- **V1**: 핵심 지표 알림 → **V2**: AI 해석 추가 → **V3**: 시장 영향 예측

### S7I-072 | MED | V2 | 실시간 대시보드 — 포트폴리오 라이브

- **모듈 연동**: S(Service Layer) - V2 웹 UI
- **구현 방식**: 포트폴리오 실시간 업데이트 대시보드(V2 웹). WebSocket 기반 실시간 시세 업데이트
- **기술 스택**: WebSocket, React 실시간 UI, 차트 라이브러리
- **VAMOS 연동**: V2 서버 인프라(S7F Part 3), 포트폴리오(S7I-044)
- **V1**: 새로고침 기반 → **V2**: 실시간 WebSocket → **V3**: 모바일 앱 대시보드

### S7I-073 | MED | V2 | 커스텀 알림 규칙 — 사용자 정의 알림

- **모듈 연동**: S(Service Layer), A(Agent Layer)
- **구현 방식**: "IF 조건 THEN 알림" 커스텀 규칙 생성. 예: "삼성전자 PER < 8 이면 알림", "VIX > 30 이면 알림"
- **기술 스택**: 규칙 엔진, 조건 파서, 알림 시스템
- **VAMOS 연동**: 가격 알림(S7I-067), 스크리닝(S7I-017)
- **V1**: 기본 알림 → **V2**: 커스텀 규칙 엔진 → **V3**: 자연어 규칙 생성

### S7I-074 | MED | V2 | 주간/월간 리포트 — 정기 분석 보고서

- **모듈 연동**: A(Agent Layer) - Content Node
- **구현 방식**: 주간/월간 포트폴리오 분석 리포트 자동 생성
- **기술 스택**: 리포트 생성 엔진, 스케줄러, PDF/Markdown 출력
- **VAMOS 연동**: 일일 리포트(S7I-069), Content Node(Agent Layer)
- **V1**: 일일 리포트 위주 → **V2**: 주간/월간 정기 리포트 → **V3**: 맞춤 리포트 구독

---

## I-Part 9: 크립토/DeFi 투자 (8건)

### S7I-075 | HIGH | V1 | 크립토 시장 데이터 — BTC/ETH/주요 코인

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 주요 암호화폐 시세 및 시장 데이터 통합. 소스: CoinGecko API(무료), Binance API, Upbit API(한국). 데이터: 시세, 시가총액, 거래량, 거래소 순유입/유출
- **기술 스택**: CoinGecko API, Binance API, Upbit API, 데이터 정규화
- **VAMOS 연동**: 온체인 데이터(S7I-026), 크립토 감성(S7I-077), 포트폴리오(S7I-078)
- **V1**: 주요 코인 10개 시세 → **V2**: 100+ 코인 + 실시간 → **V3**: 전체 크립토 시장

### S7I-076 | HIGH | V1 | 온체인 분석 — 블록체인 데이터

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 비트코인/이더리움 온체인 데이터 분석. 지표: 활성 주소, 해시레이트, NVT, MVRV, 거래소 잔고. 소스: Glassnode(Free tier), Blockchain.com
- **기술 스택**: Glassnode API, Blockchain.com API, 온체인 지표 계산
- **VAMOS 연동**: 크립토 시장(S7I-075), 온체인 대안 데이터(S7I-026)
- **V1**: 핵심 온체인 지표 5개 → **V2**: 20+ 지표 + 시각화 → **V3**: 온체인 기반 전략

### S7I-077 | HIGH | V1 | 크립토 감성 분석 — 공포/탐욕 지수

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 크립토 시장 고유 감성 지표 분석. Crypto Fear & Greed Index, 소셜 언급량, 펀딩 레이트
- **기술 스택**: Alternative.me API, 소셜 분석, 펀딩 레이트 데이터
- **VAMOS 연동**: Fear & Greed(S7I-024), 소셜 감성(S7I-021), 크립토 시장(S7I-075)
- **V1**: 공포/탐욕 지수 표시 → **V2**: 종합 크립토 감성 대시보드 → **V3**: 감성 기반 전략

### S7I-078 | HIGH | V1 | 크립토 포트폴리오 — 크립토 자산 관리

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 크립토 자산의 포트폴리오 관리(전통 자산과 통합). 거래소 잔고 조회, 수익률 추적, 세금 계산
- **기술 스택**: 거래소 API(Upbit/Binance), 포트폴리오 통합 엔진
- **VAMOS 연동**: 포트폴리오 분석(S7I-044), 세금 계산(S7I-034), 크립토 시장(S7I-075)
- **V1**: 크립토 자산 추적 → **V2**: 전통+크립토 통합 포트폴리오 → **V3**: 크립토 자동 리밸런싱

### S7I-079 | MED | V2 | DeFi 분석 — TVL/수익률 분석

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: DeFi 프로토콜의 TVL, APY, 리스크 분석. 소스: DeFi Llama(무료), Dune Analytics
- **기술 스택**: DeFi Llama API, Dune Analytics API
- **VAMOS 연동**: 크립토 시장(S7I-075), 온체인(S7I-076)
- **V1**: DeFi 기본 정보 → **V2**: TVL/APY 분석 → **V3**: DeFi 전략

### S7I-080 | MED | V2 | NFT/토큰 분석 — 토큰 이코노믹스

- **모듈 연동**: A(Agent Layer) - Research Node
- **구현 방식**: 토큰의 발행/소각/잠금 등 토큰 이코노믹스 분석
- **기술 스택**: 토큰 데이터 API, 토큰 분석 모델
- **VAMOS 연동**: 크립토 시장(S7I-075), 온체인(S7I-076)
- **V1**: 기본 토큰 정보 → **V2**: 토큰 이코노믹스 분석 → **V3**: 토큰 가치 평가

### S7I-081 | MED | V2 | 크립토 규제 모니터링 — 각국 규제 동향

- **모듈 연동**: A(Agent Layer) - Research Node
- **구현 방식**: 한국/미국/EU 암호화폐 규제 동향 모니터링
- **기술 스택**: 규제 뉴스 모니터링, LLM 요약
- **VAMOS 연동**: 크립토 규제(S7I-098), 뉴스 감성(S7I-008)
- **V1**: 수동 모니터링 → **V2**: 자동 규제 뉴스 추적 → **V3**: 규제 영향 분석

### S7I-082 | MED | V2 | 에어드랍/이벤트 — 크립토 이벤트 추적

- **모듈 연동**: A(Agent Layer) - Research Node
- **구현 방식**: 에어드랍, 하드포크, 토큰 세일 등 이벤트 추적
- **기술 스택**: 크립토 이벤트 캘린더, 알림 시스템
- **VAMOS 연동**: 이벤트 캘린더(S7I-030), 크립토 시장(S7I-075)
- **V1**: 수동 추적 → **V2**: 자동 이벤트 캘린더 → **V3**: 이벤트 기반 전략

---

## I-Part 10: AI Agent 투자 워크플로우 (10건)

### I-Part 10 VAMOS 투자 Agent 아키텍처

```
ORANGE CORE (투자 관제): 투자 정책 + 비용 제어 + 리스크 제어
├── QUANT NODE (정량): 데이터 수집/정제, 백테스팅, 포트폴리오, 시그널
├── RESEARCH NODE (정성): 뉴스/공시 분석, 산업 리서치, 감성, 인사이트
├── TRADING NODE (매매 보조): 주문(사용자 확인), 모니터링, 알림, 세금
└── CONTENT NODE (리포트): 분석 리포트, 일일/주간 요약, 투자 일지, 차트
⚠️ 핵심: 모든 매매는 사용자 최종 확인 필수!
```

---

### S7I-083 | CRITICAL | V1 | Quant Node 워크플로우 — 정량 분석 파이프라인

- **모듈 연동**: A(Agent Layer) - Quant Node(BLUE NODE)
- **구현 방식**: Quant Node 정량 분석 워크플로우 상세 정의. 1) 데이터 수집(자동): 소스→수집→정규화→검증→저장. 2) 시그널 생성(자동): 전략 실행→51% Gate 검증→시그널 생성. 3) 분석 리포트(자동): 시그널→맥락 분석→리포트→사용자 전달. 4) 매매 보조(사용자 확인 필수): 시그널→사용자 리뷰→사용자 결정→사용자 실행. VAMOS는 절대 자동 매매하지 않음(V1)
- **기술 스택**: LangGraph.js Agent, 7-Component Pipeline, vectorbt, 51% Gate
- **VAMOS 연동**: 7-Component Pipeline, 51% Gate System, 백테스팅(S7I-059), 투자 안전장치(S7I-084)
- **V1**: 데이터+시그널+리포트(자동), 매매(수동) → **V2**: Paper Trading 추가 → **V3**: 자동 매매 프레임워크(명시적 동의)

### S7I-084 | CRITICAL | V1 | 투자 안전장치 — 이중 확인 시스템

- **모듈 연동**: A(Agent Layer) - ORANGE CORE
- **구현 방식**: 투자 관련 작업의 안전장치 체계. Level 1(정보 제공, 자동): 시세/뉴스/재무 → 안전장치 불필요. Level 2(분석/제안, 자동+면책): 포트폴리오 분석, 리밸런싱, 스크리닝 → 면책 자동 표시. Level 3(주문 보조, 이중 확인): 매수/매도 주문 → 1차 AI 확인 + 2차 사용자 PIN + 3차 증권사 확인. Level 4(자동 매매, V3 삼중 확인): 별도 동의서 + 일일 한도 + 즉시 중지 버튼
- **기술 스택**: 안전장치 엔진, 다단계 확인 시스템, 면책 자동 삽입
- **VAMOS 연동**: ORANGE CORE(Agent Layer), 면책 시스템(S7I-085), Trading Node
- **V1**: Level 1-2(자동) + Level 3(이중 확인) → **V2**: Level 3 강화 → **V3**: Level 4(삼중 확인)

### S7I-085 | CRITICAL | V1 | 투자 면책 시스템 — 법적 보호

- **모듈 연동**: A(Agent Layer) - ORANGE CORE, E(Security Layer)
- **구현 방식**: 투자 관련 모든 출력에 자동 면책 표시. 표준 면책: "VAMOS AI가 제공하는 투자 관련 정보는 참고 자료이며, 투자 결정은 전적으로 사용자 본인의 판단과 책임입니다. VAMOS AI는 투자자문업자가 아니며, 투자 손실에 대한 어떠한 법적 책임도 지지 않습니다." 강화 면책(특정 종목 시): "특정 종목 언급은 매수/매도 추천이 아닙니다." 자동 삽입 위치: 분석 리포트, 스크리닝 결과, 포트폴리오 제안, 백테스트("과거 수익률이 미래 수익을 보장하지 않습니다")
- **기술 스택**: 면책 자동 삽입 엔진, 컨텍스트 감지(종목 언급/백테스트/제안), 면책 DB
- **VAMOS 연동**: 안전장치(S7I-084), 자본시장법(S7I-093), Constitution
- **V1**: 모든 투자 출력에 면책 자동 삽입 → **V2**: 컨텍스트별 맞춤 면책 → **V3**: 다국어 면책

### S7I-086 | HIGH | V1 | 투자 일지 — 매매 기록 + AI 분석

- **모듈 연동**: A(Agent Layer) - Trading/Content Node, M(Memory Layer)
- **구현 방식**: 매매 기록 자동 저장 + AI 패턴 분석. 기록: 매수/매도(시간, 가격, 수량, 이유), AI 분석 시점 시장 상황, 결과(수익/손실), 사후 분석("이 매매에서 배울 점")
- **기술 스택**: 투자 일지 DB(SQLite), LLM 사후 분석, 패턴 인식
- **VAMOS 연동**: 5-Layer 메모리(STEP7-B), Trading Node, 자기진화(S7I-090)
- **V1**: 수동 기록 + AI 분석 → **V2**: 자동 기록 + 패턴 분석 → **V3**: 투자 행동 코칭

### S7I-087 | HIGH | V1 | Research Node 투자 리서치 — 정성 분석

- **모듈 연동**: A(Agent Layer) - Research Node(BLUE NODE)
- **구현 방식**: Research Node의 투자 관련 정성 리서치 워크플로우. 1) 사용자 요청(예: "삼성전자 분석해줘"), 2) 다중 소스 정보 수집(DART, 뉴스, 실적), 3) LLM 분석 + 요약, 4) 교차 검증 + 확신도 표시, 5) 구조화된 리포트 출력
- **기술 스택**: LangGraph.js Agent, 다중 소스 수집, LLM 분석 파이프라인
- **VAMOS 연동**: DART(S7I-005), 뉴스 감성(S7I-008), 교차 검증(S7I-012), 기업 분석(S7I-011)
- **V1**: 수동 요청 → 리포트 생성 → **V2**: 자동 정기 리서치 → **V3**: 실시간 리서치

### S7I-088 | HIGH | V1 | Content Node 리포트 — 투자 보고서 생성

- **모듈 연동**: A(Agent Layer) - Content Node(BLUE NODE)
- **구현 방식**: Content Node의 투자 분석 보고서 자동 생성. 유형: 기업 분석, 섹터 분석, 매크로 분석, 포트폴리오 리뷰
- **기술 스택**: LLM 리포트 생성, Markdown/PDF 출력, 차트 생성(V2)
- **VAMOS 연동**: Research Node(S7I-087), 일일 리포트(S7I-069)
- **V1**: Markdown 리포트 → **V2**: PDF + 차트 → **V3**: 인터랙티브 리포트

### S7I-089 | HIGH | V2 | 멀티 Agent 협업 — Quant + Research + Content

- **모듈 연동**: A(Agent Layer) - ORANGE CORE + BLUE NODEs
- **구현 방식**: 여러 Agent가 협업하는 종합 투자 분석. 예: "AI 관련 투자 기회 분석해줘" → 1) ORANGE CORE 작업 분할, 2) Research Node: AI 산업 리서치, 3) Quant Node: AI 종목 스크리닝 + 밸류에이션, 4) Content Node: 종합 리포트, 5) ORANGE CORE: 검증 + 최종 출력
- **기술 스택**: LangGraph.js 멀티 Agent, 작업 분할 엔진, 결과 통합
- **VAMOS 연동**: ORANGE CORE(Agent Layer), 모든 BLUE NODEs
- **V1**: 단일 Agent 분석 → **V2**: 멀티 Agent 협업 → **V3**: 자율 투자 리서치

### S7I-090 | HIGH | V2 | 투자 학습 모드 — 자기진화 투자 분석

- **모듈 연동**: A(Agent Layer), M(Memory Layer)
- **구현 방식**: 사용자의 투자 스타일 학습으로 개인화. 학습: 선호 분석 스타일(가치/성장/퀀트), 관심 섹터/종목, 리스크 성향, 선호 리포트 포맷, 매매 패턴(빈도, 보유 기간)
- **기술 스택**: 5-Layer 메모리, 사용자 프로파일링, 개인화 엔진
- **VAMOS 연동**: 5-Layer 메모리(STEP7-B), 투자 일지(S7I-086), Knowledge Graph(STEP7-C)
- **V1**: 기본 선호 설정 → **V2**: 자동 학습 + 개인화 → **V3**: 완전 맞춤형 투자 비서

### S7I-091 | MED | V2 | 투자 시뮬레이터 — 교육용 가상 투자

- **모듈 연동**: A(Agent Layer) - Trading Node
- **구현 방식**: 실제 돈 없이 투자를 배우는 시뮬레이터. 가상 자금, 실시간 시세, 성과 추적, AI 피드백
- **기술 스택**: 시뮬레이터 엔진, 가상 포트폴리오, AI 피드백 생성
- **VAMOS 연동**: Paper Trading(S7I-063), 투자 교육(S7I-010)
- **V1**: 백테스트 위주 → **V2**: 실시간 시뮬레이터 → **V3**: 게이미피케이션

### S7I-092 | MED | V2 | 자동 매매 프레임워크 — V2+ 자동 실행

- **모듈 연동**: A(Agent Layer) - Trading Node
- **구현 방식**: 검증된 전략의 자동 매매 프레임워크(V2+). 조건: 51% Gate 통과, Paper Trading 3개월+, 사용자 명시적 동의. 안전장치: 일일 한도, 즉시 중지, 비정상 거래 탐지
- **기술 스택**: 자동 매매 엔진, 안전장치 시스템, 모니터링
- **VAMOS 연동**: 안전장치(S7I-084), Paper Trading(S7I-063), 51% Gate
- **V1**: 수동 매매 → **V2**: 반자동(사용자 확인) → **V3**: 자동(엄격한 조건+동의)

---

## I-Part 11: 규제/컴플라이언스 보강 (8건)

### S7I-093 | CRITICAL | V1 | 자본시장법 준수 — 한국 금융 규제

- **모듈 연동**: E(Security Layer), A(Agent Layer)
- **구현 방식**: 한국 자본시장법의 투자자문업 규제 준수. VAMOS는 "투자 참고 정보 제공"이지 "투자 자문"이 아님. 투자자문업 등록 대상 아니도록 기능 범위 명확화. 면책 조항 필수. "매수/매도 추천" 표현 절대 금지 → "분석 결과", "참고 정보", "사용자 판단 필요" 사용
- **기술 스택**: 금지 표현 필터, 면책 자동 삽입, 법적 가이드라인 DB
- **VAMOS 연동**: 면책 시스템(S7I-085), Constitution 투자 규칙, 안전장치(S7I-084)
- **V1**: 면책 + 표현 필터 → **V2**: 법률 자문 확보 → **V3**: 규제 인증

### S7I-094 | CRITICAL | V1 | 금투세 대비 — 금융투자소득세

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 2027년 시행 예정 금융투자소득세 대비. 실현 손익 자동 추적, 손실 이월 공제 관리, 세금 예상 계산기, Tax-Loss Harvesting 알림
- **기술 스택**: 금투세 계산 엔진, 손실 이월 DB, TLH 알림
- **VAMOS 연동**: 세금 계산(S7I-034), TLH(S7I-048), 포트폴리오(S7I-044)
- **V1**: 금투세 시뮬레이션 → **V2**: 자동 추적 + 최적화 → **V3**: 세무 연동

### S7I-095 | HIGH | V1 | 불법 행위 방지 — 시세조종/내부자거래 차단

- **모듈 연동**: E(Security Layer), A(Agent Layer) - ORANGE CORE
- **구현 방식**: VAMOS가 불법 투자 행위를 돕지 않도록 방지. 시세조종 목적 대량 주문 차단, 미공개 정보 기반 분석 거부, "주가 조작"/"작전" 등 불법 키워드 필터링, Constitution에 투자 윤리 규칙 내장
- **기술 스택**: 불법 행위 감지 필터, 키워드 블랙리스트, Constitution 투자 윤리
- **VAMOS 연동**: Constitution(STEP7-B), 안전장치(S7I-084), 5-Gate Safety Gate
- **V1**: 키워드 필터 + 거부 → **V2**: 패턴 감지 강화 → **V3**: AI 불법 행위 탐지

### S7I-096 | HIGH | V1 | 적합성 원칙 — 투자자 보호

- **모듈 연동**: A(Agent Layer) - ORANGE CORE
- **구현 방식**: 사용자 투자 경험과 위험 감수 능력에 맞는 정보 제공. 초기 설정: 투자 경험/목적/위험 성향 설문. 등급: 보수적/중립/적극적/공격적. 등급에 맞지 않는 고위험 상품 경고
- **기술 스택**: 투자자 프로파일 시스템, 적합성 검사 엔진
- **VAMOS 연동**: 투자 온보딩(S7I-106), 안전장치(S7I-084)
- **V1**: 기본 적합성 설문 + 경고 → **V2**: 동적 적합성 업데이트 → **V3**: 규제 준수 인증

### S7I-097 | HIGH | V1 | 미국 SEC 규제 — 해외 주식 규제

- **모듈 연동**: E(Security Layer), A(Agent Layer)
- **구현 방식**: 미국 주식 투자 시 관련 규제 고려. PDT Rule(이미 구현), Wash Sale Rule(이미 구현). 추가: Regulation Best Interest(Reg BI) 참조
- **기술 스택**: SEC 규제 규칙 DB, 자동 검증 엔진
- **VAMOS 연동**: 법적 프레임워크(기존 7-Component legal), 안전장치(S7I-084)
- **V1**: PDT + Wash Sale 유지 → **V2**: Reg BI 참조 추가 → **V3**: 글로벌 규제 통합

### S7I-098 | HIGH | V2 | 크립토 규제 — 암호화폐 관련 법률

- **모듈 연동**: E(Security Layer), A(Agent Layer)
- **구현 방식**: 한국 특금법, 미국 SEC 규제 등 크립토 규제 모니터링. VASP 등록 여부, 투자자 보호, 과세 기준
- **기술 스택**: 크립토 규제 DB, 규제 모니터링
- **VAMOS 연동**: 크립토 규제 모니터링(S7I-081), 세금(S7I-034)
- **V1**: 기본 규제 정보 → **V2**: 규제 모니터링 → **V3**: 규제 자동 대응

### S7I-099 | MED | V2 | 해외 송금/환전 규제 — 외환 관련

- **모듈 연동**: E(Security Layer)
- **구현 방식**: 해외 투자 시 외환 거래 관련 규제 고려. 외국환거래법, 해외 직접투자 신고 기준
- **기술 스택**: 외환 규제 DB
- **VAMOS 연동**: 환율 리스크(S7I-056), SEC 규제(S7I-097)
- **V1**: 기본 정보 → **V2**: 규제 알림 → **V3**: 자동 준수 확인

### S7I-100 | MED | V2 | 투자 감사 추적 — 규제 대응 로그

- **모듈 연동**: E(Security Layer), S(Storage Layer)
- **구현 방식**: 투자 관련 모든 활동의 감사 추적 로그 유지. 모든 분석 요청, 시그널, 주문 보조 내역 기록
- **기술 스택**: 감사 로그 DB, 불변 로그, 검색/필터
- **VAMOS 연동**: 보안 로그(STEP7-E), 투자 일지(S7I-086)
- **V1**: 기본 활동 로그 → **V2**: 구조화된 감사 추적 → **V3**: 규제 리포팅 자동화

---

## I-Part 12: 기존 GAP 해결 + 품질 개선 (6건)

### S7I-101 | CRITICAL | V1 | GAP-06 해결: ConnectorResponse Pydantic 모델 생성

- **모듈 연동**: I(Infra Core) - 데이터 파이프라인
- **구현 방식**: 기존 JSON Schema를 Pydantic v2 모델로 변환. `contracts.py`에 ConnectorResponse, OHLCVData, TickData 모델 생성. 타입 안전성 + 자동 검증 확보
- **기술 스택**: Pydantic v2, Python, 자동 스키마 생성
- **VAMOS 연동**: 7-Component Pipeline standardize 단계, 데이터 검증(validate)
- **V1**: Pydantic 모델 생성 + 기존 코드 마이그레이션 → **V2**: 자동 스키마 검증 → **V3**: 스키마 버전 관리

### S7I-102 | CRITICAL | V1 | GAP-07 해결: OHLCV tick vs candle 필드 정의

- **모듈 연동**: I(Infra Core) - 데이터 파이프라인
- **구현 방식**: tick 데이터와 candle 데이터의 필수/선택 필드 차이 문서화. CandleData: timestamp, open, high, low, close, volume(필수) + adjusted_close, vwap(선택). TickData: timestamp, price, volume(필수), candle 필드 불필요
- **기술 스택**: Pydantic v2 모델, 조건부 검증
- **VAMOS 연동**: ConnectorResponse(S7I-101), 데이터 파이프라인 전체
- **V1**: 필드 정의 + Pydantic 모델 → **V2**: 자동 변환(tick→candle) → **V3**: 다중 타임프레임

### S7I-103 | CRITICAL | V1 | GAP-03 해결: yfinance 폴백 절차 완성

- **모듈 연동**: I(Infra Core) - 데이터 수집
- **구현 방식**: yfinance 장애 시 대체 경로 문서화/구현. 1st: yfinance(기본). 2nd: Alpha Vantage(API 키, 무료 5calls/min). 3rd: OpenBB Provider 자동 전환. 4th: 사용자 수동 입력 요청
- **기술 스택**: Fallback 체인, Alpha Vantage API, OpenBB Provider
- **VAMOS 연동**: OpenBB(S7I-003), Model Fallback(S7F-004) 패턴 적용
- **V1**: 폴백 체인 구현 + 문서화 → **V2**: 자동 전환 + 알림 → **V3**: 다중 소스 자동 선택

### S7I-104 | HIGH | V1 | GAP-01 해결 계획: RSI_BB 데이터 확보 로드맵

- **모듈 연동**: A(Agent Layer) - Quant Node
- **구현 방식**: 5년 데이터 수집 + Grid Search 실행 계획. V1 출시 전 데이터 수집, V1.1에서 전략 검증 완료
- **기술 스택**: 데이터 수집 파이프라인, Grid Search 프레임워크
- **VAMOS 연동**: RSI_BB 전략(S7I-060), 백테스팅(S7I-059), 과적합 방지(S7I-061)
- **V1**: 데이터 수집 + 초기 Grid Search → **V2**: 전략 최적화 → **V3**: 다중 전략 레지스트리

### S7I-105 | HIGH | V1 | 투자 기능 품질 벤치마크 — VBS-10 구체화

- **모듈 연동**: G(벤치마크), A(Agent Layer)
- **구현 방식**: STEP7-G VBS-10 투자 분석 품질 벤치마크 구체화. 기업 분석 정확성(20건, 전문가 평가), 밸류에이션 합리성(20건, 동종업계 비교), 리스크 경고 적절성(20건, 위기 시나리오), 면책 표시 완전성(20건, 법적 요건 충족)
- **기술 스택**: 벤치마크 프레임워크(S7G Part 9), 전문가 평가 체계
- **VAMOS 연동**: VBS-10(S7G-070), 기업 분석(S7I-011), 면책(S7I-085)
- **V1**: 80건 테스트셋 구축 + 초기 평가 → **V2**: 정기 벤치마크 → **V3**: 자동화 + 외부 검증

### S7I-106 | HIGH | V1 | 투자 온보딩 — 초기 설정 마법사

- **모듈 연동**: A(Agent Layer), S(Service Layer)
- **구현 방식**: 투자 기능 최초 사용 시 안내 마법사. 플로우: 1) 투자 경험 수준(초보/중급/고급), 2) 투자 목적(장기/단기/배당/트레이딩), 3) 위험 성향 평가, 4) 관심 자산(한국주식/미국주식/ETF/크립토), 5) 데이터 소스 연결(증권사 API, 포트폴리오 입력), 6) 면책 조항 동의, 7) 완료 → 맞춤 대시보드
- **기술 스택**: 온보딩 UI 플로우, 설문 시스템, 데이터 소스 연결 마법사
- **VAMOS 연동**: 적합성 원칙(S7I-096), 면책(S7I-085), 투자 학습(S7I-090)
- **V1**: 기본 온보딩 플로우 → **V2**: 시각적 마법사 → **V3**: AI 맞춤 온보딩

---

## I 카테고리 구현 우선순위 로드맵

### V1 (MVP) — 필수 구현: 52건
- Part 1: S7I-001~008 (8건)
- Part 2: S7I-011~017 (7건)
- Part 3: S7I-021~026 (6건)
- Part 4: S7I-031~037 (7건)
- Part 5: S7I-041~045 (5건)
- Part 6: S7I-049~054 (6건)
- Part 7: S7I-059~062 (4건)
- Part 8: S7I-067~071 (5건)
- Part 9: S7I-075~078 (4건)
- Part 10: S7I-083~088 (6건)
- Part 11: S7I-093~097 (5건)
- Part 12: S7I-101~106 (6건)

### V2 (Server) — 확장 구현: 42건

### V3 (Enterprise) — 고급 구현: 12건

---

# 크로스 레퍼런스 매트릭스

## F-I 카테고리 간 연동 관계

| 연동 | F(인프라) | G(벤치마크) | H(비즈니스) | I(투자) |
|------|----------|-----------|-----------|---------|
| **F(인프라)** | — | F→G: 모델 서빙이 벤치마크 대상 | F→H: 인프라 비용이 가격 전략 기반 | F→I: 모델 라우터가 투자 분석 모델 선택 |
| **G(벤치마크)** | G→F: 벤치마크 결과로 모델 교체 판단 | — | G→H: 품질 지표가 마케팅 근거 | G→I: VBS-10이 투자 품질 평가 |
| **H(비즈니스)** | H→F: 비용 전략이 인프라 설계 제약 | H→G: 경쟁 비교가 벤치마크 우선순위 결정 | — | H→I: 투자자 페르소나가 투자 기능 방향 |
| **I(투자)** | I→F: 투자 데이터 파이프라인이 인프라 요구 | I→G: 투자 분석 정확도 평가 필요 | I→H: 투자 기능이 니치 차별화 핵심 | — |

## STEP7 전체 시리즈 연동

| 카테고리 | F-I 주요 연동 |
|---------|-------------|
| A(메모리/아키텍처) | F: 메모리 저장소(SQLite), I: 투자 일지 기억 |
| B(Self-Evolution) | H: 개인화가 핵심 MOAT, I: 투자 스타일 학습 |
| C(Knowledge Graph) | I: 기업/산업 관계 그래프, H: 개인화 차별화 |
| D(MCP/Tool) | F: MCP Tool 실행 인프라, I: 투자 데이터 Tool |
| E(보안/프라이버시) | F: 보안 인프라, H: 데이터 주권 가치, I: 투자 데이터 보호 |

---

# 문서 종결부

## 총괄 통계

| 구분 | 항목 수 | CRITICAL | HIGH | MED | LOW |
|------|---------|----------|------|-----|-----|
| F. 인프라/배포/MLOps | 96 | 13 | 48 | 31 | 4 |
| G. 벤치마크/평가/품질보증 | 88 | 11 | 47 | 30 | 0 |
| H. 비즈니스모델/시장전략 | 78 | 11 | 41 | 26 | 0 |
| I. AI Investing 보강 | 106 | 22 | 56 | 28 | 0 |
| **합계** | **368** | **57** | **192** | **115** | **4** |

## 버전별 구현 계획

| 버전 | F | G | H | I | 합계 |
|------|---|---|---|---|------|
| V1 (MVP) | 40 | 40 | 30 | 52 | **162** |
| V2 (Server) | 40 | 38 | 35 | 42 | **155** |
| V3 (Enterprise) | 16 | 10 | 13 | 12 | **51** |

## VAMOS F-I 통합 차별화 요약

| 축 | 경쟁사(ChatGPT/Claude) | VAMOS |
|-----|----------------------|-------|
| 인프라(F) | 클라우드 전용, 단일 모델 | 로컬+클라우드 하이브리드, 멀티 모델 라우팅 |
| 품질(G) | 자체 벤치마크 비공개 | 투명한 벤치마크, VAMOS 고유 지표(VBS) |
| 비즈니스(H) | $20/mo 고정 구독 | 사용량 기반 $5-10/mo, 비용 투명성 |
| 투자(I) | 범용 AI, 투자 특화 없음 | 93개 데이터 소스, 백테스팅, 한국 시장 특화 |

---

> **STEP7 F-I 통합 상세명세서 완료**
> - F(96건) + G(88건) + H(78건) + I(106건) = **총 368건**
> - STEP7 시리즈 전체: A(316) + B(88) + C(104) + D(82) + E(92) + F(96) + G(88) + H(78) + I(106) = **총 1,050건**

---

<\!-- END OF DOCUMENT -->
