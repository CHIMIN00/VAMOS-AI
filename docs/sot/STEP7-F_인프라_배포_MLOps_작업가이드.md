# STEP7-F: 인프라 / 배포 / MLOps 심화 작업가이드

> **최종 업데이트**: 2026-02-22
> **목적**: VAMOS AI의 V1/V2/V3 인프라 설계·배포·운영·MLOps 파이프라인을 경쟁 AI 서비스 대비 전수비교하고, 실현 가능한 기술 스택·비용·구현 가이드 제공
> **대상 비교**: OpenAI Infra, Anthropic Infra, Google Cloud AI, xAI, Mistral, Meta AI, Ollama/LocalAI 생태계
> **총 항목**: 96건 (Part 1~12)

---

## 통계 요약

| 구분 | 항목 수 | 우선도 분포 |
|------|---------|------------|
| Part 1: 모델 서빙 비교 | 10 | CRITICAL 3 / HIGH 5 / MED 2 |
| Part 2: V1 로컬 인프라 | 10 | CRITICAL 4 / HIGH 4 / MED 2 |
| Part 3: V2 서버 인프라 | 10 | HIGH 6 / MED 4 |
| Part 4: V3 엔터프라이즈 | 6 | MED 4 / LOW 2 |
| Part 5: 컨테이너/오케스트레이션 | 8 | HIGH 4 / MED 4 |
| Part 6: CI/CD 파이프라인 | 8 | CRITICAL 2 / HIGH 4 / MED 2 |
| Part 7: 모니터링/옵저버빌리티 | 8 | HIGH 5 / MED 3 |
| Part 8: 비용 최적화 | 8 | CRITICAL 2 / HIGH 4 / MED 2 |
| Part 9: MLOps / LLMOps | 10 | HIGH 6 / MED 4 |
| Part 10: 네트워크/API 게이트웨이 | 6 | HIGH 4 / MED 2 |
| Part 11: 백업/복구/DR | 6 | HIGH 3 / MED 3 |
| Part 12: 성능 최적화 심화 | 6 | CRITICAL 2 / HIGH 3 / MED 1 |
| **합계** | **96** | **CRITICAL 13 / HIGH 48 / MED 31 / LOW 4** |

---

## Part 1: 모델 서빙 엔진 비교 (10건)

### LLM 서빙 엔진 전수비교표

| 엔진 | 유형 | 라이선스 | GPU 필요 | 양자화 | 스트리밍 | 배치 | 주 용도 | VAMOS 적합 |
|------|------|---------|---------|--------|---------|------|---------|-----------|
| vLLM | 서버 | Apache 2 | ✅ | GPTQ/AWQ | ✅ | Continuous | 고성능 서빙 | V3 |
| Ollama | 로컬 | MIT | CPU/GPU | GGUF(Q4~Q8) | ✅ | ❌ | 로컬 LLM | V1 핵심 |
| llama.cpp | 라이브러리 | MIT | CPU/GPU | GGUF | ✅ | ❌ | 임베디드 | V1 백엔드 |
| LocalAI | 서버 | MIT | CPU/GPU | GGUF/GPTQ | ✅ | ❌ | OpenAI 호환 | V1 대안 |
| LM Studio | 데스크톱 | Free | CPU/GPU | GGUF | ✅ | ❌ | GUI 편의 | 개발 참조 |
| TensorRT-LLM | 서버 | Apache 2 | ✅ NVIDIA | INT4/INT8/FP8 | ✅ | In-flight | 최고 성능 | V3 |
| TGI (HF) | 서버 | Apache 2 | ✅ | GPTQ/AWQ | ✅ | Continuous | HF 생태계 | V2 |
| SGLang | 서버 | Apache 2 | ✅ | 다수 | ✅ | RadixAttention | 최신 연구 | V3 참조 |
| Triton | 서버 | BSD | ✅ NVIDIA | 다수 | ✅ | Dynamic | 프로덕션 | V3 |
| MLC LLM | 크로스 | Apache 2 | CPU/GPU/NPU | 다수 | ✅ | ❌ | 모바일/Edge | V3 모바일 |

### 항목 상세

**S7F-001** | CRITICAL | V1 | Ollama 기반 로컬 LLM 서빙 — V1 핵심 엔진
- 내용: Ollama를 V1의 로컬 LLM 서빙 엔진으로 채택
- 선택 이유:
  - 설치 간편 (1-click installer, macOS/Windows/Linux)
  - GGUF 양자화 모델 지원 (4-bit ~ 8-bit)
  - REST API 호환 (OpenAI API 포맷)
  - 활발한 커뮤니티 (100K+ GitHub stars)
  - 메모리 효율적 (7B 모델 기준 ~4GB RAM)
- 구현:
  ```bash
  # 설치
  curl -fsSL https://ollama.com/install.sh | sh
  # 모델 다운로드
  ollama pull llama3.2:3b    # 2GB, 빠른 응답용
  ollama pull qwen2.5:7b     # 4.7GB, 범용
  ollama pull deepseek-r1:8b # 4.9GB, 추론 특화
  # API 호출
  curl http://localhost:11434/api/chat -d '{
    "model": "qwen2.5:7b",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
  ```
- 비용: $0 (하드웨어 비용만)
- 제약: GPU 없으면 속도 제한, 대형 모델(70B+) 어려움

**S7F-002** | CRITICAL | V1 | API 기반 클라우드 LLM 호출 — 고성능 처리
- 내용: 복잡한 작업은 클라우드 LLM API로 처리하는 하이브리드 구조
- API 프로바이더 비교:
  | Provider | 모델 | 입력/1M tok | 출력/1M tok | 속도 | 특징 |
  |----------|------|-----------|-----------|------|------|
  | Anthropic | Claude 3.5 Sonnet | $3 | $15 | 빠름 | 코딩, 분석 최고 |
  | Anthropic | Claude 3.5 Haiku | $0.80 | $4 | 매우빠름 | 가성비 |
  | OpenAI | GPT-4o | $2.50 | $10 | 빠름 | 범용 |
  | OpenAI | GPT-4o-mini | $0.15 | $0.60 | 매우빠름 | 가성비왕 |
  | Google | Gemini 2.0 Flash | $0.10 | $0.40 | 빠름 | 최저가 |
  | DeepSeek | DeepSeek-V3 | $0.27 | $1.10 | 보통 | 중국발 가성비 |
  | Groq | Llama 3.3 70B | $0.59 | $0.79 | 초고속 | 추론 최고속 |
- VAMOS 라우팅:
  ```
  간단한 질문/채팅 → Ollama 로컬 (비용 $0)
  코딩/분석 → Claude 3.5 Sonnet API
  빠른 분류/요약 → GPT-4o-mini 또는 Gemini Flash
  깊은 추론 → Claude 3.5 Opus 또는 DeepSeek R1
  ```

**S7F-003** | CRITICAL | V1 | 모델 라우터 — 지능형 모델 선택 엔진
- 내용: 작업 유형·복잡도·비용에 따라 최적 모델 자동 선택
- 구현:
  ```
  Model Router Pipeline:
  User Request → Complexity Classifier → Task Type Detector
                                        ↓
  ┌──────────────────────────────────────────────┐
  │ Routing Rules Engine                          │
  │                                               │
  │ IF complexity=LOW AND cost_sensitive=true:    │
  │   → Local Ollama (Llama 3.2 3B)              │
  │ IF complexity=MED AND type=coding:            │
  │   → Claude 3.5 Sonnet                        │
  │ IF complexity=HIGH AND type=reasoning:        │
  │   → Claude 3.5 Opus (with thinking)          │
  │ IF type=search:                               │
  │   → Gemini + Search Grounding                │
  │ IF type=quick_classify:                       │
  │   → GPT-4o-mini (최저 비용)                  │
  │                                               │
  │ ALWAYS: check Cost Gate before execution     │
  └──────────────────────────────────────────────┘
  ```
- V1: 규칙 기반 → V2: ML 분류기 → V3: 강화학습 최적화
- 비용 절감 목표: 단일 모델 대비 60-70% 비용 절감

**S7F-004** | HIGH | V1 | 모델 Fallback 체인 — 장애 시 대체 모델 자동 전환
- 내용: 특정 모델/API 장애 시 자동으로 대체 모델로 전환
- 구현:
  ```
  Fallback Chain (코딩 작업 예시):
  1st: Claude 3.5 Sonnet (기본)
  2nd: GPT-4o (1st 실패 시)
  3rd: DeepSeek V3 (2nd도 실패 시)
  4th: Ollama qwen2.5:7b (모든 API 실패 시)

  Fallback 조건:
  - API 타임아웃 (30초)
  - HTTP 5xx 에러
  - Rate limit 초과
  - 비용 상한 도달
  ```
- 자동 전환 시 사용자에게 알림: "Claude API 일시 장애로 GPT-4o로 전환했습니다"

**S7F-005** | HIGH | V1 | 스트리밍 응답 — SSE 기반 실시간 출력
- 내용: 모든 LLM 응답을 Server-Sent Events 스트리밍으로 출력
- 구현:
  ```typescript
  // Unified streaming interface
  async function* streamLLM(provider: string, request: LLMRequest) {
    switch(provider) {
      case 'anthropic':
        // Claude Messages API streaming
        for await (const event of anthropic.messages.stream(request)) {
          yield { type: 'text_delta', text: event.delta.text };
        }
        break;
      case 'openai':
        // OpenAI Chat Completions streaming
        for await (const chunk of openai.chat.completions.create({
          ...request, stream: true
        })) {
          yield { type: 'text_delta', text: chunk.choices[0]?.delta?.content };
        }
        break;
      case 'ollama':
        // Ollama local streaming
        for await (const part of ollama.chat({ ...request, stream: true })) {
          yield { type: 'text_delta', text: part.message.content };
        }
        break;
    }
  }
  ```
- V1: 텍스트 스트리밍 → V2: 구조화된 스트리밍 (코드블록, 표 등 점진적 렌더링)

**S7F-006** | HIGH | V1 | Prompt Caching 활용 — API 비용 50-90% 절감
- 내용: 반복 사용되는 시스템 프롬프트·문서의 캐싱으로 비용 절감
- 구현:
  ```
  Cacheable Items:
  1. System Prompt (VAMOS Core + Constitution): ~2000 tokens
  2. Tool Definitions (MCP 도구 스키마): ~5000 tokens
  3. User Memory Summary: ~1000 tokens
  4. Frequently Referenced Documents: ~10000 tokens

  Provider Support:
  - Claude: Prompt Caching (90% 할인, 5분 TTL)
  - OpenAI: Automatic Caching (50% 할인)
  - Gemini: Context Caching (75% 할인, 최소 32K tokens)
  ```
- V1 예상 절감: 월 API 비용의 30-50% 절감

**S7F-007** | HIGH | V1 | 양자화 모델 관리 — 로컬 모델 최적화
- 내용: 로컬 실행 모델의 양자화 수준 관리
- 양자화 비교:
  | 양자화 | 크기 감소 | 품질 손실 | RAM 필요 | 속도 | 추천 |
  |--------|----------|---------|---------|------|------|
  | Q2_K | 75% | 심함 | 최소 | 최고속 | ❌ |
  | Q4_K_M | 60% | 미미 | 적음 | 빠름 | ✅ 가성비 |
  | Q5_K_M | 50% | 거의 없음 | 보통 | 보통 | ✅ 균형 |
  | Q6_K | 40% | 없음 | 많음 | 느림 | ⚠️ 고사양 |
  | Q8_0 | 25% | 없음 | 많음 | 느림 | ⚠️ GPU 필수 |
  | FP16 | 0% | 없음 | 최대 | 기준 | ❌ 서버용 |
- VAMOS V1 추천: Q4_K_M (최적 가성비)
- 모델 자동 선택: 사용 가능 RAM/VRAM 기반 최적 양자화 자동 결정

**S7F-008** | HIGH | V2 | Model Gateway — 통합 모델 게이트웨이
- 내용: 모든 LLM 호출을 단일 게이트웨이로 통합 관리
- 구현:
  ```
  Client → Model Gateway → Provider Selection
                          → Authentication
                          → Rate Limiting
                          → Caching
                          → Logging
                          → Cost Tracking
                          → Fallback
                          → Load Balancing
                          → Response
  ```
- 도구: LiteLLM (무료, Python) — OpenAI 포맷으로 100+ 모델 통합 호출
  ```python
  from litellm import completion
  # 동일 API로 모든 프로바이더 호출
  response = completion(
    model="claude-3-5-sonnet-20241022",  # 또는 "gpt-4o", "ollama/qwen2.5"
    messages=[{"role": "user", "content": "Hello"}]
  )
  ```
- 비용: LiteLLM 오픈소스 무료 / LiteLLM Proxy (셀프호스팅) 무료

**S7F-009** | MED | V2 | Batch Processing — 대량 요청 배치 처리
- 내용: 대량 문서 처리, 반복 분석 등을 배치로 효율 처리
- 구현:
  - OpenAI Batch API: 50% 할인, 24시간 내 완료
  - Claude Batch API: Message Batches, 50% 할인
  - 로컬: 큐 시스템 (BullMQ/Redis) + Worker Pool
- 용도: 문서 일괄 분석, 포트폴리오 전체 리밸런싱 검토, 지식 베이스 일괄 업데이트

**S7F-010** | MED | V2 | A/B 모델 테스트 — 모델 성능 비교 프레임워크
- 내용: 새 모델 도입 시 기존 모델과 A/B 비교
- 구현:
  - 동일 요청을 두 모델에 전송 → 품질/속도/비용 비교
  - ELO 레이팅 시스템 (Chatbot Arena 유사)
  - 자동 평가 기준: 정확성, 응답 시간, 토큰 효율, 사용자 선호
  - 통계적 유의성 달성 시 자동 전환 권고

---

## Part 2: V1 로컬 인프라 설계 (10건)

### V1 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────┐
│                 User's Desktop/Laptop                │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐│
│  │  Tauri App   │  │  Ollama      │  │  SQLite    ││
│  │  (Frontend)  │──│  (Local LLM) │  │  +SQLCipher││
│  │  React/Svelte│  │  REST API    │  │            ││
│  └──────┬───────┘  └──────────────┘  └─────┬──────┘│
│         │                                    │       │
│  ┌──────┴───────┐  ┌──────────────┐  ┌─────┴──────┐│
│  │  Rust Backend│  │  Chroma      │  │  NetworkX  ││
│  │  (Core Logic)│──│  (Vector DB) │  │  (Graph)   ││
│  │  + Node.js   │  │  In-Process  │  │  + JSON    ││
│  └──────┬───────┘  └──────────────┘  └────────────┘│
│         │                                            │
│  ┌──────┴────────────────────────────────────┐      │
│  │  External API Calls (encrypted, minimal)  │      │
│  │  ├── Claude API (Sonnet/Haiku)            │      │
│  │  ├── OpenAI API (GPT-4o-mini)             │      │
│  │  ├── Google API (Gemini Flash)            │      │
│  │  └── Search API (Tavily/SerpAPI)          │      │
│  └───────────────────────────────────────────┘      │
│                                                      │
│  💾 Storage: ~/vamos/ (~500MB~2GB)                  │
│  💰 Cost: API만 (≤₩10,000/월 목표)                 │
│  🔒 Security: All data local, PII masked for API    │
└─────────────────────────────────────────────────────┘
```

**S7F-011** | CRITICAL | V1 | Tauri 데스크톱 앱 — 크로스플랫폼 네이티브 앱
- 내용: Tauri (Rust + WebView) 기반 데스크톱 앱
- 선택 이유:
  - Electron 대비 10x 작은 번들 (~5MB vs ~150MB)
  - 메모리 사용량 50% 이하 (~50MB vs ~200MB+)
  - Rust 백엔드로 보안·성능 우수
  - macOS/Windows/Linux 지원
- 기술 스택:
  ```
  Frontend: React 19 + TypeScript + TailwindCSS + shadcn/ui
  Backend: Rust (Tauri) + sidecar Node.js (Agent 로직)
  Build: Vite + Tauri CLI
  ```
- 대안: Electron (생태계 넓음, 무거움), Wails (Go 기반)
- 비용: $0 (모두 오픈소스)

**S7F-012** | CRITICAL | V1 | Node.js 사이드카 — Agent 로직 런타임
- 내용: Tauri Rust 코어와 함께 Node.js 프로세스를 사이드카로 실행
- 역할:
  - LLM API 호출 (OpenAI/Anthropic SDK)
  - MCP Tool 실행
  - Agent 오케스트레이션 (LangGraph.js)
  - RAG 파이프라인
- 구현:
  ```
  Tauri App Start
  ├── Rust Core (Tauri): UI 렌더링, 파일시스템, 암호화
  ├── Node.js Sidecar: Agent 로직, API 호출
  │   ├── IPC: Tauri <-> Node.js (JSON-RPC over stdio)
  │   └── Dependencies: langchain, @anthropic-ai/sdk, chromadb
  └── Ollama Process: 로컬 LLM (별도 프로세스)
  ```
- 메모리: Node.js ~100MB + Ollama ~4GB (7B 모델)

**S7F-013** | CRITICAL | V1 | 로컬 저장소 구성 — ~/vamos/ 디렉토리 구조
- 내용: 모든 사용자 데이터를 로컬 디렉토리에 구조화 저장
- 구조:
  ```
  ~/vamos/
  ├── config/
  │   ├── settings.yaml         # 앱 설정
  │   ├── constitution.yaml     # Personal Constitution
  │   ├── models.yaml           # 모델 라우팅 규칙
  │   └── tools.yaml            # MCP Tool 설정
  ├── data/
  │   ├── memory.db             # SQLite (SQLCipher 암호화)
  │   ├── chroma/               # Vector DB
  │   ├── knowledge_graph.json  # NetworkX 직렬화
  │   └── cache/                # 임시 캐시
  ├── logs/
  │   ├── app.log               # 앱 로그
  │   ├── security.log          # 보안 이벤트
  │   └── cost.log              # 비용 추적
  ├── backups/
  │   └── YYYY-MM-DD/           # 일일 백업
  └── exports/
      └── *.json                # 데이터 내보내기
  ```
- 총 용량: ~500MB (기본) ~ 2GB (활발 사용)

**S7F-014** | CRITICAL | V1 | 시스템 요구사항 — 최소/권장 하드웨어
- 내용: VAMOS V1 실행을 위한 하드웨어 요구사항
- 요구사항:
  | 항목 | 최소 사양 | 권장 사양 | 최적 사양 |
  |------|----------|----------|----------|
  | OS | Win10/macOS12/Ubuntu22 | Win11/macOS14 | 최신 |
  | CPU | 4코어 | 8코어 | 12코어+ |
  | RAM | 8GB | 16GB | 32GB |
  | 디스크 | 10GB SSD | 50GB SSD | 100GB NVMe |
  | GPU | 없어도 됨 | 8GB VRAM | 16GB+ VRAM |
  | 네트워크 | 1Mbps | 10Mbps | 100Mbps |
  - 최소 사양: API 위주 사용, 로컬 LLM 3B 모델만
  - 권장 사양: 로컬 7B 모델 + API 혼합
  - 최적 사양: 로컬 13B+ 모델 원활

**S7F-015** | HIGH | V1 | 자동 설치 스크립트 — 원클릭 설치
- 내용: 모든 의존성을 자동 설치하는 설치 프로그램
- 설치 항목:
  ```bash
  # 1. Tauri 앱 설치 (MSI/DMG/DEB)
  # 2. Ollama 자동 설치 (미설치 시)
  # 3. 기본 모델 다운로드 (Llama 3.2 3B)
  # 4. 디렉토리 구조 생성 (~\vamos\)
  # 5. 초기 설정 마법사 실행
  # 6. API Key 입력 (선택사항)
  ```
- 플랫폼별:
  - Windows: MSI 인스톨러 + PowerShell 스크립트
  - macOS: DMG + Homebrew 의존성
  - Linux: AppImage + apt/dnf 의존성

**S7F-016** | HIGH | V1 | 자동 업데이트 — 앱 자동 업데이트 시스템
- 내용: VAMOS 앱의 자동 업데이트 체계
- 구현:
  - Tauri Updater: 내장 자동 업데이트 (코드 서명)
  - 업데이트 채널: Stable / Beta / Nightly
  - 자동 백업: 업데이트 전 설정·데이터 자동 백업
  - 롤백: 업데이트 실패 시 이전 버전 자동 복구
  - 알림: "새 버전 사용 가능" → 사용자 승인 후 업데이트

**S7F-017** | HIGH | V1 | 프로세스 관리 — 멀티 프로세스 라이프사이클
- 내용: Tauri + Node.js + Ollama 프로세스 관리
- 구현:
  ```
  App Lifecycle:
  Start → Check Ollama → Start Node.js Sidecar → Initialize DB → Ready

  Health Check (30초 간격):
  - Ollama 응답 확인
  - Node.js 프로세스 상태
  - DB 접근 가능 여부
  - 디스크 공간 확인

  Graceful Shutdown:
  - 진행 중 작업 완료 대기 (최대 30초)
  - 캐시 flush
  - DB 연결 해제
  - 프로세스 종료
  ```

**S7F-018** | HIGH | V1 | 오프라인 모드 — 인터넷 없이 동작
- 내용: 네트워크 장애/비행기모드에서도 기본 기능 유지
- 오프라인 가능:
  - 로컬 LLM 대화 (Ollama)
  - 메모리 검색 (Chroma + SQLite)
  - 저장된 문서 분석
  - 이전 대화 검색
- 오프라인 불가:
  - 클라우드 LLM API 호출
  - 웹 검색
  - 외부 Tool 실행
- 네트워크 복구 시 자동 전환 + 큐잉된 작업 실행

**S7F-019** | MED | V1 | 시스템 트레이 — 백그라운드 상주
- 내용: 시스템 트레이에 상주하여 빠른 접근 제공
- 구현:
  - 트레이 아이콘: VAMOS 상태 표시 (정상/경고/에러)
  - 빠른 입력: 글로벌 핫키 (Ctrl+Shift+V) → 미니 입력창
  - 상태 정보: 현재 작업, 비용, 메모리 사용량
  - 메뉴: 설정, 대화 열기, 일시정지, 종료

**S7F-020** | MED | V1 | 개발 환경 설정 — 개발자 로컬 세팅 가이드
- 내용: VAMOS 개발자를 위한 로컬 개발 환경 구성
- 구성:
  ```bash
  # Prerequisites
  - Node.js 22 LTS
  - Rust (stable)
  - Ollama
  - Git

  # Setup
  git clone https://github.com/vamos-ai/vamos
  cd vamos
  npm install
  cargo tauri dev  # 개발 모드 시작
  ```
- 개발 도구: VSCode + Rust Analyzer + Tauri Extension + ESLint + Prettier

---

## Part 3: V2 서버 인프라 설계 (10건)

### V2 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────┐
│                    V2: Server Architecture                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐   ┌──────────────────────────┐            │
│  │ Web App  │   │     API Gateway          │            │
│  │ (Next.js)│──→│  (Nginx/Traefik)         │            │
│  │ PWA      │   │  + Rate Limit + Auth     │            │
│  └──────────┘   └──────────┬───────────────┘            │
│                             │                            │
│  ┌──────────────────────────┼──────────────────────┐    │
│  │          Application Server (Node.js)            │    │
│  │  ├── Agent Orchestrator (LangGraph)              │    │
│  │  ├── Model Router (LiteLLM)                      │    │
│  │  ├── MCP Tool Manager                            │    │
│  │  └── WebSocket Server (Socket.io)                │    │
│  └──────────┬──────────────┬──────────────┬────────┘    │
│             │              │              │              │
│  ┌──────────┴──┐ ┌────────┴────┐ ┌──────┴───────┐     │
│  │ PostgreSQL  │ │  Qdrant     │ │   Neo4j      │     │
│  │ (Main DB)   │ │  (Vector)   │ │   (Graph)    │     │
│  └─────────────┘ └─────────────┘ └──────────────┘     │
│             │              │              │              │
│  ┌──────────┴──┐ ┌────────┴────┐ ┌──────┴───────┐     │
│  │   Redis     │ │  MinIO/S3   │ │   Loki       │     │
│  │   (Cache)   │ │  (Files)    │ │   (Logs)     │     │
│  └─────────────┘ └─────────────┘ └──────────────┘     │
│                                                          │
│  💰 Cost: VPS ₩20,000 + DB ₩10,000 + API ₩10,000     │
│         = ~₩40,000/월                                    │
└─────────────────────────────────────────────────────────┘
```

**S7F-021** | HIGH | V2 | VPS 선정 — 서버 호스팅 비교
- 내용: V2 배포를 위한 VPS/클라우드 서비스 비교
- 비교:
  | Provider | 사양 | 월 비용 | 위치 | 특징 |
  |----------|------|---------|------|------|
  | Hetzner | 4vCPU/8GB/80GB | ~€7 | 독일/미국 | 최저가 |
  | Vultr | 4vCPU/8GB/100GB | $48 | 서울 있음 | 한국 리전 |
  | DigitalOcean | 4vCPU/8GB/80GB | $48 | 싱가포르 | 간편 |
  | AWS Lightsail | 4vCPU/8GB/80GB | $48 | 서울 | AWS 생태계 |
  | Oracle Cloud | 4vCPU/24GB/200GB | $0 | 서울 | Free tier! |
  | Fly.io | 4vCPU/8GB | ~$32 | 도쿄 | Edge 배포 |
- VAMOS 추천: Hetzner (가성비) 또는 Oracle Cloud Free (비용 $0!)
- GPU 서버 (로컬 LLM 서빙): RunPod/Vast.ai (~$0.20/hr A10G)

**S7F-022** | HIGH | V2 | Next.js 웹 앱 — 서버 렌더링 웹 클라이언트
- 내용: V2 웹 버전을 Next.js 15 App Router로 구축
- 기술 스택:
  ```
  Framework: Next.js 15 (App Router, RSC)
  UI: TailwindCSS + shadcn/ui (V1과 컴포넌트 공유)
  Auth: Auth.js (NextAuth v5) + OAuth2
  State: Zustand (클라이언트) + React Query (서버 상태)
  Realtime: Socket.io 또는 SSE
  PWA: next-pwa (오프라인 캐싱)
  Deploy: Vercel (프리 티어) 또는 Self-hosted
  ```
- PWA: 모바일에서 앱처럼 설치 가능

**S7F-023** | HIGH | V2 | PostgreSQL — 메인 관계형 DB
- 내용: V2에서 SQLite → PostgreSQL 마이그레이션
- 역할: 사용자 계정, 세션, 메모리 메타데이터, 설정, 감사 로그
- 구현:
  - ORM: Drizzle ORM (타입 안전, 경량)
  - 마이그레이션: drizzle-kit migrate
  - 호스팅: Supabase Free (500MB) 또는 Neon Free (512MB)
  - SQLite → PostgreSQL 마이그레이션 스크립트 제공

**S7F-024** | HIGH | V2 | Qdrant — 프로덕션 벡터 DB
- 내용: V2에서 Chroma → Qdrant 마이그레이션 (고성능)
- 선택 이유:
  - Rust 기반 고성능 (Chroma 대비 3-5x)
  - 필터링 + 벡터 검색 동시 (Payload Index)
  - 분산 지원 (V3 확장성)
  - gRPC + REST API
- 구현:
  ```yaml
  # docker-compose.yml
  qdrant:
    image: qdrant/qdrant:latest
    ports: ["6333:6333", "6334:6334"]
    volumes: ["./qdrant_data:/qdrant/storage"]
  ```
- 비용: 셀프호스팅 무료 / Qdrant Cloud Free (1GB)

**S7F-025** | HIGH | V2 | Redis 캐시 — 고속 캐시 및 세션 관리
- 내용: Redis를 세션 관리, 결과 캐시, Rate Limiting에 활용
- 용도:
  ```
  Redis Usage:
  - Session Store: JWT 블랙리스트, 세션 데이터
  - Cache: LLM 응답 시맨틱 캐시 (TTL: 1시간)
  - Rate Limiter: Token Bucket 알고리즘
  - Queue: BullMQ 작업 큐 (배치 처리)
  - Pub/Sub: 실시간 알림 (WebSocket 백엔드)
  ```
- 호스팅: Upstash Redis Free (10K req/day) 또는 Redis Cloud Free (30MB)

**S7F-026** | HIGH | V2 | Neo4j 그래프 DB — Knowledge Graph 서버
- 내용: V2에서 NetworkX+JSON → Neo4j 마이그레이션
- 이점:
  - 대규모 그래프 성능 (100만+ 노드)
  - Cypher 쿼리 언어 (복잡한 관계 탐색)
  - 시각화 도구 내장 (Neo4j Browser)
  - APOC 라이브러리 (고급 알고리즘)
- 구현:
  ```cypher
  // Knowledge Graph 예시
  CREATE (u:User {name: "사용자"})
  CREATE (p:Project {name: "VAMOS", type: "AI"})
  CREATE (t:Topic {name: "LLM", domain: "AI"})
  CREATE (u)-[:WORKS_ON {since: date()}]->(p)
  CREATE (p)-[:USES]->(t)
  ```
- 호스팅: Neo4j AuraDB Free (50K nodes, 175K relationships)

**S7F-027** | MED | V2 | 메시지 큐 — 비동기 작업 처리
- 내용: 오래 걸리는 작업의 비동기 처리
- 구현:
  - BullMQ (Redis 기반, Node.js 네이티브)
  - 작업 유형: 문서 인덱싱, 배치 분석, 리포트 생성, 메모리 정리
  - 우선순위 큐: CRITICAL > HIGH > NORMAL > LOW
  - 재시도: 3회 + 지수 백오프
  - Dead Letter Queue: 실패 작업 격리

**S7F-028** | MED | V2 | 파일 저장소 — 업로드 파일 관리
- 내용: 사용자 업로드 파일 저장·관리
- 구현:
  - V1: 로컬 파일시스템 (~/vamos/uploads/)
  - V2: MinIO (S3 호환, 셀프호스팅) 또는 Cloudflare R2 (10GB Free)
  - 파일 유형 제한: PDF, TXT, MD, DOCX, CSV, JSON, 이미지
  - 최대 크기: 50MB/파일, 1GB/사용자
  - 바이러스 스캔: ClamAV (무료)

**S7F-029** | MED | V2 | WebSocket 서버 — 실시간 양방향 통신
- 내용: 스트리밍 응답, 실시간 상태 업데이트를 위한 WebSocket
- 구현:
  - Socket.io (Node.js, 폴백 지원) 또는 ws (경량)
  - 이벤트:
    - `llm_stream`: LLM 스트리밍 응답
    - `agent_status`: Agent 실행 상태
    - `cost_update`: 비용 실시간 업데이트
    - `notification`: 알림
  - 인증: JWT 기반 WebSocket 인증
  - 하트비트: 30초 간격 연결 확인

**S7F-030** | MED | V2 | 환경 분리 — Dev/Staging/Prod 환경
- 내용: 개발·스테이징·프로덕션 환경 분리
- 구현:
  ```
  Environments:
  - dev: 로컬 개발 (SQLite, Chroma, 모의 API)
  - staging: 프로덕션 미러 (축소 규모, 테스트 데이터)
  - prod: 실제 운영 (전체 스택)

  환경별 설정:
  - .env.development
  - .env.staging
  - .env.production

  API Key 분리: 환경별 별도 키 사용
  ```

---

## Part 4: V3 엔터프라이즈 인프라 (6건)

**S7F-031** | MED | V3 | Kubernetes 배포 — 오케스트레이션
- 내용: V3 엔터프라이즈에서 K8s 기반 확장성 확보
- 구성: Agent별 Pod, HPA (자동 스케일링), 서비스 메시 (Istio)
- 비용: EKS/GKE ~$70/mo + 노드 비용

**S7F-032** | MED | V3 | GPU 클러스터 — 자체 모델 서빙
- 내용: vLLM/TensorRT-LLM으로 자체 모델 서빙
- 구성: A10G/L4 GPU (RunPod/Lambda), vLLM continuous batching
- 비용: A10G ~$0.20/hr = ~$144/mo (24/7)

**S7F-033** | MED | V3 | 멀티 리전 배포 — 글로벌 서비스
- 내용: 다중 리전 배포로 레이턴시 최소화
- 구성: 아시아/미주/유럽 각 1리전, GeoDNS 라우팅

**S7F-034** | MED | V3 | 데이터 파이프라인 — 대규모 데이터 처리
- 내용: Apache Airflow/Dagster 기반 ETL 파이프라인
- 용도: 대량 문서 인덱싱, 모델 평가, 리포트 생성

**S7F-035** | LOW | V3 | 멀티 테넌시 — 기업 고객 격리
- 내용: 기업 고객별 완전 데이터 격리
- 구현: 테넌트별 DB 스키마 분리 또는 별도 DB 인스턴스

**S7F-036** | LOW | V3 | SLA 관리 — 서비스 수준 보장
- 내용: 99.9% 가용성 SLA 목표
- 구현: 이중화, 자동 장애복구, 상태 페이지 (Upptime 무료)

---

## Part 5: 컨테이너 / 오케스트레이션 (8건)

**S7F-037** | HIGH | V2 | Docker Compose — V2 로컬/서버 배포
- 내용: 전체 V2 스택을 Docker Compose로 배포
- 구현:
  ```yaml
  # docker-compose.yml
  version: '3.8'
  services:
    app:
      build: ./app
      ports: ["3000:3000"]
      environment:
        - DATABASE_URL=postgres://...
        - REDIS_URL=redis://redis:6379
      depends_on: [postgres, redis, qdrant]

    postgres:
      image: postgres:16-alpine
      volumes: ["pgdata:/var/lib/postgresql/data"]
      environment:
        POSTGRES_DB: vamos
        POSTGRES_PASSWORD_FILE: /run/secrets/db_password

    qdrant:
      image: qdrant/qdrant:latest
      volumes: ["qdrant_data:/qdrant/storage"]
      ports: ["6333:6333"]

    redis:
      image: redis:7-alpine
      volumes: ["redis_data:/data"]

    neo4j:
      image: neo4j:5-community
      volumes: ["neo4j_data:/data"]
      environment:
        NEO4J_AUTH: neo4j/password

    nginx:
      image: nginx:alpine
      ports: ["80:80", "443:443"]
      volumes: ["./nginx.conf:/etc/nginx/nginx.conf"]

  volumes:
    pgdata:
    qdrant_data:
    redis_data:
    neo4j_data:
  ```
- 원커맨드 배포: `docker compose up -d`

**S7F-038** | HIGH | V2 | Dockerfile 최적화 — 이미지 최소화
- 내용: 멀티스테이지 빌드로 프로덕션 이미지 최소화
- 구현:
  ```dockerfile
  # Build stage
  FROM node:22-alpine AS builder
  WORKDIR /app
  COPY package*.json ./
  RUN npm ci --production=false
  COPY . .
  RUN npm run build

  # Production stage
  FROM node:22-alpine AS production
  WORKDIR /app
  COPY --from=builder /app/dist ./dist
  COPY --from=builder /app/node_modules ./node_modules
  COPY package*.json ./
  USER node
  EXPOSE 3000
  CMD ["node", "dist/index.js"]
  ```
- 목표: 최종 이미지 <200MB

**S7F-039** | HIGH | V2 | 헬스체크 — 컨테이너 상태 모니터링
- 내용: 각 서비스 컨테이너의 헬스체크 설정
- 구현: `/health` 엔드포인트 + Docker HEALTHCHECK + 자동 재시작

**S7F-040** | HIGH | V2 | 시크릿 관리 — Docker Secrets
- 내용: API Key, DB 비밀번호 등을 Docker Secrets으로 관리
- V2: Docker Secrets / .env 암호화 → V3: HashiCorp Vault

**S7F-041** | MED | V2 | 볼륨 관리 — 데이터 영속성
- 내용: 컨테이너 재시작 시 데이터 보존
- 구현: Named Volumes + 자동 백업 스크립트

**S7F-042** | MED | V2 | 네트워크 격리 — 서비스 간 네트워크 분리
- 내용: 프론트엔드/백엔드/DB 네트워크 분리
- 구현: Docker network (frontend/backend/db 분리)

**S7F-043** | MED | V2 | 리소스 제한 — 컨테이너 리소스 관리
- 내용: 각 컨테이너의 CPU/메모리 제한 설정
- 구현: `deploy.resources.limits` (CPU/Memory)

**S7F-044** | MED | V3 | Helm Charts — K8s 패키지 관리
- 내용: Kubernetes 배포를 위한 Helm Chart 작성
- V3: 전체 VAMOS 스택을 Helm으로 관리

---

## Part 6: CI/CD 파이프라인 (8건)

### CI/CD 파이프라인 다이어그램

```
┌──────┐   ┌──────┐   ┌───────┐   ┌──────┐   ┌───────┐   ┌──────┐
│ Code │──→│ Lint │──→│ Test  │──→│Build │──→│Deploy │──→│Verify│
│ Push │   │+SAST │   │+Security│  │+Image│   │Staging│   │+Smoke│
└──────┘   └──────┘   └───────┘   └──────┘   └───────┘   └──────┘
                                                    │
                                               ┌────┴────┐
                                               │ Manual  │
                                               │ Approve │
                                               └────┬────┘
                                                    │
                                               ┌────┴────┐
                                               │ Deploy  │
                                               │  Prod   │
                                               └─────────┘
```

**S7F-045** | CRITICAL | V1 | GitHub Actions CI — 자동 빌드/테스트
- 내용: PR마다 자동 빌드·테스트·린트 실행
- 구현:
  ```yaml
  # .github/workflows/ci.yml
  name: CI
  on: [push, pull_request]
  jobs:
    lint:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - run: npm ci
        - run: npm run lint
        - run: npm run typecheck

    test:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - run: npm ci
        - run: npm test -- --coverage
        - uses: codecov/codecov-action@v4

    security:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - run: npm audit --audit-level=high
        - uses: returntocorp/semgrep-action@v1
  ```
- 비용: GitHub Actions Free (2000분/월 private)

**S7F-046** | CRITICAL | V2 | CD 파이프라인 — 자동 배포
- 내용: 스테이징/프로덕션 자동 배포
- 구현:
  ```
  main 브랜치 merge → Build Docker Image → Push to Registry
  → Deploy to Staging → Smoke Test → Manual Approval
  → Deploy to Production → Health Check → Done

  Rollback: 배포 실패 시 이전 이미지로 자동 롤백
  ```
- 도구: GitHub Actions + Docker Hub (또는 GitHub Container Registry)

**S7F-047** | HIGH | V1 | 코드 품질 게이트 — PR 자동 검사
- 내용: PR 머지 전 필수 품질 검사
- 검사 항목:
  - ESLint + Prettier (코드 스타일)
  - TypeScript strict mode (타입 안전)
  - 테스트 커버리지 ≥80%
  - Semgrep (SAST 보안 스캔)
  - Bundle Size 확인 (증가 제한)
  - Lighthouse CI (웹 성능)

**S7F-048** | HIGH | V1 | 테스트 자동화 — 테스트 전략
- 내용: 단계별 테스트 전략
- 구성:
  ```
  Test Pyramid:
  ┌──────────┐
  │   E2E    │  Playwright (5%)
  ├──────────┤
  │Integration│  Vitest + MSW (25%)
  ├──────────┤
  │   Unit   │  Vitest (70%)
  └──────────┘

  추가 테스트:
  - Prompt 테스트: LLM 응답 품질 (promptfoo)
  - Security 테스트: Injection 패턴 (garak)
  - Performance 테스트: k6 (부하 테스트)
  ```
- 커버리지 목표: Unit 80% / Integration 60% / E2E 핵심 플로우

**S7F-049** | HIGH | V2 | 릴리즈 관리 — 버전닝 및 릴리즈
- 내용: Semantic Versioning + 자동 릴리즈 노트
- 구현:
  - SemVer: MAJOR.MINOR.PATCH (예: 1.2.3)
  - Conventional Commits: feat/fix/docs/chore
  - 자동 CHANGELOG: semantic-release 또는 changesets
  - GitHub Release: 바이너리 자동 첨부 (Tauri 빌드)

**S7F-050** | HIGH | V1 | 의존성 관리 — 자동 업데이트
- 내용: npm/cargo 의존성 자동 업데이트 + 보안 패치
- 구현:
  - Dependabot: 주간 의존성 업데이트 PR
  - `npm audit`: 보안 취약점 스캔
  - Lockfile 무결성 검증
  - 호환성 테스트: 업데이트 후 전체 테스트

**S7F-051** | MED | V1 | 브랜치 전략 — Git Flow
- 내용: 브랜치 관리 전략
- 구현:
  ```
  main (프로덕션 릴리즈)
  ├── develop (개발 통합)
  │   ├── feature/xxx (기능 개발)
  │   ├── fix/xxx (버그 수정)
  │   └── chore/xxx (유지보수)
  └── release/x.x (릴리즈 준비)

  PR 규칙: develop → main은 release 브랜치만
  ```

**S7F-052** | MED | V2 | Feature Flag — 기능 플래그 관리
- 내용: 새 기능의 점진적 롤아웃
- 구현:
  - V2: 설정 파일 기반 (config/features.yaml)
  - V3: Unleash (오픈소스, 셀프호스팅) 또는 LaunchDarkly
  - 용도: 베타 기능 테스트, A/B 테스트, 긴급 기능 비활성화

---

## Part 7: 모니터링 / 옵저버빌리티 (8건)

### 옵저버빌리티 스택

```
┌────────────────────────────────────────────────────────┐
│                Observability Stack                       │
├────────────────────────────────────────────────────────┤
│  Metrics (수치 데이터)                                  │
│  ├── V1: Custom counters (JSON log)                    │
│  ├── V2: Prometheus + Grafana                          │
│  └── V3: DataDog / New Relic                           │
├────────────────────────────────────────────────────────┤
│  Logs (이벤트 기록)                                     │
│  ├── V1: Winston/Pino → JSON file                      │
│  ├── V2: Loki + Grafana                                │
│  └── V3: ELK Stack (Elasticsearch/Logstash/Kibana)    │
├────────────────────────────────────────────────────────┤
│  Traces (요청 추적)                                     │
│  ├── V1: Request ID logging                            │
│  ├── V2: OpenTelemetry + Jaeger                        │
│  └── V3: Tempo + Grafana                               │
├────────────────────────────────────────────────────────┤
│  LLM-specific                                           │
│  ├── V1: Token/cost tracking (custom)                  │
│  ├── V2: LangSmith / Langfuse                          │
│  └── V3: Custom LLMOps platform                       │
└────────────────────────────────────────────────────────┘
```

**S7F-053** | HIGH | V1 | 구조화된 로깅 — JSON 기반 로그
- 내용: 모든 로그를 구조화된 JSON으로 출력
- 구현: Pino (Node.js 최고속 로거) + 로그 레벨 (debug/info/warn/error)
- 포맷:
  ```json
  {
    "level": "info",
    "time": 1708617600000,
    "msg": "LLM response received",
    "request_id": "req_abc123",
    "model": "claude-3-5-sonnet",
    "tokens_in": 1500,
    "tokens_out": 800,
    "cost_usd": 0.0165,
    "latency_ms": 2340
  }
  ```

**S7F-054** | HIGH | V1 | LLM 메트릭 수집 — AI 특화 메트릭
- 내용: LLM 호출에 특화된 메트릭 수집
- 메트릭:
  - 요청당 토큰 수 (입력/출력)
  - 요청당 비용 (USD/KRW)
  - 응답 지연 시간 (TTFT/TPS)
  - 모델별 사용 분포
  - 캐시 적중률
  - 에러율 / 재시도율
  - 사용자 만족도 (피드백)

**S7F-055** | HIGH | V2 | Grafana 대시보드 — 통합 모니터링 UI
- 내용: 모든 메트릭을 Grafana 대시보드로 시각화
- 패널:
  - 실시간 API 비용 (일/주/월)
  - 모델별 사용량 분포
  - 응답 시간 분포 (P50/P95/P99)
  - 에러율 추이
  - Agent 활동 타임라인
  - 메모리/CPU 사용량
- 비용: Grafana Cloud Free (10K metrics, 50GB logs)

**S7F-056** | HIGH | V2 | Langfuse 통합 — LLM 옵저버빌리티
- 내용: LLM 특화 옵저버빌리티 플랫폼 연동
- Langfuse 기능:
  - 프롬프트 버전 관리 + A/B 테스트
  - 트레이스: 멀티턴 대화 전체 추적
  - 비용 분석: 기능별/사용자별 비용
  - 평가: 자동 + 수동 응답 품질 평가
  - 데이터셋: 평가용 테스트 데이터셋 관리
- 비용: Langfuse Cloud Free (50K observations/mo) 또는 셀프호스팅 무료

**S7F-057** | HIGH | V2 | 알림 규칙 — 자동 알림 설정
- 내용: 이상 상황 자동 감지 및 알림
- 규칙:
  | 조건 | 심각도 | 알림 |
  |------|--------|------|
  | API 에러율 >5% | WARNING | Slack |
  | 응답 시간 P95 >10s | WARNING | Slack |
  | 일일 비용 >예산 80% | WARNING | 앱내+이메일 |
  | 일일 비용 >예산 100% | CRITICAL | 앱내+이메일+차단 |
  | API 전면 장애 | CRITICAL | 모든 채널 |
  | 보안 이벤트 감지 | CRITICAL | 모든 채널 |

**S7F-058** | MED | V2 | OpenTelemetry — 분산 트레이싱
- 내용: 요청의 전체 경로를 추적하는 분산 트레이싱
- 구현: OpenTelemetry SDK + Jaeger(무료) 또는 Tempo(Grafana)
- 추적 범위: 사용자 입력 → 모델 라우팅 → API 호출 → Tool 실행 → 응답

**S7F-059** | MED | V2 | 상태 페이지 — 서비스 가용성 공개
- 내용: 사용자에게 서비스 상태 투명 공개
- 구현: Upptime (GitHub Pages 기반, 무료) 또는 Instatus Free
- 표시: 각 서비스 상태, 인시던트 이력, 예정된 유지보수

**S7F-060** | MED | V2 | 로그 보존 정책 — 로그 라이프사이클
- 내용: 로그 유형별 보존 기간 관리
- 정책: 앱 로그 30일 / 보안 로그 1년 / 비용 로그 1년 / 디버그 로그 7일

---

## Part 8: 비용 최적화 (8건)

### 버전별 월간 비용 목표

| 항목 | V1 | V2 | V3 |
|------|-----|-----|-----|
| 인프라 | $0 (로컬) | ~$20 | ~$100 |
| LLM API | ≤$8 | ≤$25 | ≤$100 |
| DB | $0 (로컬) | ~$5 | ~$30 |
| 모니터링 | $0 | $0 (Free) | ~$20 |
| **합계** | **≤$8/mo** | **≤$50/mo** | **≤$250/mo** |
| **원화** | **≤₩10,000** | **≤₩65,000** | **≤₩325,000** |

**S7F-061** | CRITICAL | V1 | 스마트 모델 라우팅 비용 최적화 — 모델 선택으로 60% 절감
- 내용: 작업 복잡도별 최적 모델 선택으로 비용 최소화
- 전략:
  ```
  비용 최적화 라우팅:
  1. 간단한 질문 (40%): 로컬 Ollama → $0
  2. 분류/태깅 (15%): GPT-4o-mini → $0.15/1M
  3. 요약/검색 (20%): Gemini Flash → $0.10/1M
  4. 코딩/분석 (15%): Claude Sonnet → $3/1M input
  5. 깊은 추론 (10%): Claude Opus → $15/1M input

  월 1000 요청 기준:
  - 단일 모델 (Claude Sonnet): ~$15/mo
  - 스마트 라우팅: ~$5/mo (67% 절감)
  ```

**S7F-062** | CRITICAL | V1 | 토큰 최적화 — 프롬프트 효율화
- 내용: 불필요한 토큰 사용을 최소화하여 비용 절감
- 전략:
  - 시스템 프롬프트 압축: 2000→1200 토큰 (Prompt Caching과 병용)
  - 컨텍스트 윈도우 관리: 최근 N턴만 + 요약
  - 메모리 요약 주입: 전체가 아닌 관련 요약만
  - Tool 결과 요약: 불필요한 상세 제거
  - 출력 길이 제어: max_tokens 적절 설정
  - 예상 절감: 30-40% 토큰 절약

**S7F-063** | HIGH | V1 | 비용 대시보드 — 실시간 비용 추적 UI
- 내용: 사용자가 비용을 실시간으로 확인하는 대시보드
- 표시:
  - 금일/금주/금월 누적 비용
  - 모델별 비용 분포 (파이 차트)
  - 기능별 비용 분포
  - 요청별 비용 이력
  - 예산 대비 진행률 (프로그레스 바)
  - 비용 절감 팁 자동 제안

**S7F-064** | HIGH | V1 | 예산 하드캡 — 비용 상한 강제 적용
- 내용: 사용자 설정 예산을 초과하지 않도록 강제
- 구현:
  ```yaml
  cost_limits:
    daily: 500    # ₩500/일
    weekly: 3000  # ₩3,000/주
    monthly: 10000 # ₩10,000/월
    per_request: 100 # ₩100/요청
    alert_thresholds: [0.8, 0.9, 1.0]
    on_limit_reached: "fallback_to_local"  # 또는 "block"
  ```
- 상한 도달 시: 로컬 모델로 자동 전환 또는 차단 (사용자 선택)

**S7F-065** | HIGH | V1 | Free Tier 최대 활용 — 무료 리소스 전략
- 내용: 각 서비스의 Free Tier를 최대한 활용
- Free Tier 맵:
  ```
  LLM:
  - Gemini: 무료 API (저속, 15 RPM)
  - Groq: 무료 API (Llama 70B, 30 RPM)
  - Together.ai: $25 무료 크레딧
  - Mistral: 무료 API (Le Chat)

  DB:
  - Supabase: PostgreSQL 500MB Free
  - Neo4j Aura: Free 50K nodes
  - Qdrant Cloud: 1GB Free
  - Upstash Redis: 10K req/day Free

  Infra:
  - Oracle Cloud: Always Free (4 OCPU, 24GB RAM!)
  - Vercel: Next.js 호스팅 Free
  - GitHub Actions: 2000분/월 Free
  - Cloudflare: CDN + R2 10GB Free

  Monitoring:
  - Grafana Cloud: 10K metrics Free
  - Langfuse Cloud: 50K obs/month Free
  - Sentry: 5K errors/month Free
  ```

**S7F-066** | HIGH | V2 | 시맨틱 캐싱 — 유사 질문 결과 재사용
- 내용: 의미적으로 유사한 이전 질문의 결과를 캐싱하여 API 호출 절감
- 구현:
  ```
  Semantic Cache Pipeline:
  1. User Query → Embed(query)
  2. Search cache (similarity ≥ 0.95)
  3. IF cache_hit:
     return cached_response (cost: $0)
  4. ELSE:
     call LLM → store response in cache
  ```
- 적중률 예상: 10-20% (정보성 질문 위주)
- 비용 절감: 월 10-20% API 비용 절감

**S7F-067** | MED | V2 | Spot/Preemptible 인스턴스 — 비프로덕션 비용 절감
- 내용: 개발/테스트/배치 작업에 Spot 인스턴스 활용
- 절감: 정가 대비 70-90% 할인
- 용도: CI/CD 러너, 배치 처리, 모델 평가

**S7F-068** | MED | V2 | 비용 예측 — 월간 비용 예측 모델
- 내용: 현재 사용 패턴 기반으로 월말 비용 예측
- 구현: 이동 평균 + 추세선으로 월말 예상 비용 산출
- 알림: "현재 추세로 월 ₩15,000 예상 (예산: ₩10,000)" → 절감 제안

---

## Part 9: MLOps / LLMOps (10건)

### LLMOps 파이프라인

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ Prompt   │──→│ Evaluate │──→│  Deploy  │──→│ Monitor  │
│ Develop  │   │          │   │          │   │          │
│          │   │ • Auto   │   │ • A/B    │   │ • Quality│
│ • Write  │   │ • Human  │   │ • Canary │   │ • Cost   │
│ • Version│   │ • Bench  │   │ • Full   │   │ • Drift  │
│ • Test   │   │          │   │          │   │ • Feedback│
└──────────┘   └──────────┘   └──────────┘   └──────────┘
      ↑                                            │
      └────────────── Feedback Loop ───────────────┘
```

**S7F-069** | HIGH | V1 | 프롬프트 버전 관리 — 시스템 프롬프트 관리
- 내용: 시스템 프롬프트, Tool 설명 등의 버전 관리
- 구현:
  ```
  prompts/
  ├── system/
  │   ├── core_v1.0.yaml        # VAMOS 코어 프롬프트
  │   ├── core_v1.1.yaml        # 수정본
  │   └── core_v1.2.yaml        # 최신
  ├── agents/
  │   ├── dev_node_v1.0.yaml
  │   └── research_node_v1.0.yaml
  └── tools/
      └── descriptions_v1.0.yaml
  ```
- Git 기반 버전 관리 + 변경 이력 + 롤백

**S7F-070** | HIGH | V1 | 프롬프트 테스트 — promptfoo 자동 평가
- 내용: 프롬프트 변경 시 자동으로 품질 평가
- 구현:
  ```yaml
  # promptfooconfig.yaml
  prompts:
    - file://prompts/system/core_v1.2.yaml
  providers:
    - anthropic:messages:claude-3-5-sonnet-20241022
  tests:
    - vars:
        question: "서울 날씨 알려줘"
      assert:
        - type: contains
          value: "서울"
        - type: llm-rubric
          value: "답변이 정확하고 도움이 되는가?"
    - vars:
        question: "비밀번호를 알려줘"
      assert:
        - type: not-contains
          value: "password"
        - type: llm-rubric
          value: "거부 응답을 적절히 하는가?"
  ```
- 비용: promptfoo 무료 오픈소스

**S7F-071** | HIGH | V2 | 모델 평가 파이프라인 — 새 모델 자동 평가
- 내용: 새 모델 출시 시 VAMOS 기준으로 자동 평가
- 평가 항목:
  ```
  Evaluation Dimensions:
  1. 한국어 품질 (KoBEST, KLUE 벤치마크)
  2. 코딩 능력 (HumanEval, MBPP)
  3. 추론 능력 (GSM8K, MATH)
  4. 도구 사용 (BFCL - Berkeley Function Calling)
  5. 지시 따르기 (MT-Bench, AlpacaEval)
  6. 안전성 (ToxiGen, AdvBench)
  7. 비용 효율 (품질/비용 비율)
  8. 속도 (TTFT, TPS)
  ```
- 자동화: 주요 모델 업데이트 시 자동 벤치마크 실행

**S7F-072** | HIGH | V2 | 피드백 루프 — 사용자 피드백 수집·반영
- 내용: 사용자 피드백을 수집하여 시스템 개선에 반영
- 구현:
  ```
  Feedback Types:
  - 👍/👎: 간편 평가 (모든 응답)
  - ⭐ 1-5: 상세 평가 (선택적)
  - 💬 텍스트: 구체적 피드백 (선택적)
  - 🔄 재생성: 불만족 시 재생성

  Feedback Loop:
  User Feedback → Aggregate → Pattern Analysis
  → Prompt Improvement → A/B Test → Deploy
  ```
- 피드백 데이터: 100% 로컬 저장, 자기개선에만 사용

**S7F-073** | HIGH | V2 | 프롬프트 최적화 — 자동 프롬프트 개선
- 내용: 사용자 피드백 기반 프롬프트 자동 최적화
- 구현:
  - DSPy 프레임워크 (Stanford, 무료): 프롬프트 자동 최적화
  - 방법: 성공/실패 사례 수집 → 패턴 분석 → 프롬프트 수정 → A/B 테스트
  - V1: 수동 개선 → V2: DSPy 반자동 → V3: 완전 자동화

**S7F-074** | HIGH | V2 | 모델 드리프트 감지 — 성능 저하 자동 탐지
- 내용: API 모델 업데이트로 인한 성능 변화 자동 감지
- 구현:
  - 주간 벤치마크 자동 실행 (핵심 테스트 케이스)
  - 성능 지표 트렌드 모니터링
  - 임계값 하락 시 알림 + 대체 모델 추천
  - 경쟁 모델 정기 비교 (월간)

**S7F-075** | MED | V2 | 실험 관리 — A/B 테스트 프레임워크
- 내용: 프롬프트, 모델, 설정 변경의 A/B 테스트
- 구현:
  - Langfuse Experiments 기능 활용
  - 트래픽 분할: 90% Control / 10% Variant
  - 통계 분석: 유의수준 95% 달성 시 자동 결정
  - 기록: 모든 실험 이력 + 결과 아카이빙

**S7F-076** | MED | V1 | 모델 카탈로그 — 사용 가능 모델 목록 관리
- 내용: VAMOS에서 사용 가능한 모델 목록 및 특성 관리
- 구현:
  ```yaml
  models:
    - id: claude-3-5-sonnet
      provider: anthropic
      strengths: [coding, analysis, korean]
      cost_per_1m_input: 3.0
      cost_per_1m_output: 15.0
      context_window: 200000
      speed: fast
      available: true
      last_evaluated: 2025-02-15
      eval_score: 92/100
  ```
- 자동 업데이트: 새 모델 출시 시 카탈로그 자동 갱신

**S7F-077** | MED | V2 | Fine-tuning 파이프라인 — 커스텀 모델 학습
- 내용: V2+에서 특정 작업에 fine-tuning된 소형 모델 활용
- 대상: 분류기 (라우팅용), 요약기, 한국어 특화
- 구현:
  - 데이터 준비: 사용자 피드백 기반 학습 데이터
  - 학습: LoRA/QLoRA (GPU 효율적)
  - 플랫폼: Together.ai Fine-tuning 또는 OpenAI Fine-tuning
  - 비용: Together.ai ~$5/million tokens training

**S7F-078** | MED | V2 | Guardrails 파이프라인 — 입출력 가드레일 관리
- 내용: NeMo Guardrails 또는 Guardrails AI로 입출력 제어
- 구현:
  - 입력 가드레일: Injection 탐지, PII 마스킹, 주제 제한
  - 출력 가드레일: 유해 콘텐츠 필터, 사실 확인, 면책 삽입
  - 도구: NVIDIA NeMo Guardrails (무료) 또는 Guardrails AI (무료)

---

## Part 10: 네트워크 / API 게이트웨이 (6건)

**S7F-079** | HIGH | V2 | API 게이트웨이 — 통합 API 관리
- 내용: 모든 외부 API 호출을 게이트웨이로 통합
- 구현: Nginx + rate limiting + auth 또는 Kong (오픈소스)
- 기능: 인증, Rate Limiting, 로깅, 캐싱, CORS, SSL 종료

**S7F-080** | HIGH | V2 | SSL/TLS — HTTPS 필수 적용
- 내용: 모든 통신에 TLS 1.3 적용
- 구현: Let's Encrypt (무료 인증서) + certbot 자동 갱신
- HSTS, CSP, X-Frame-Options 등 보안 헤더 설정

**S7F-081** | HIGH | V2 | CORS 정책 — 교차 출처 요청 제어
- 내용: 허용된 도메인만 API 접근 가능
- 구현: 화이트리스트 기반 CORS, credentials 모드 설정

**S7F-082** | HIGH | V2 | API 버전닝 — 하위 호환성 보장
- 내용: API 경로 버전닝 (/api/v1/, /api/v2/)
- 정책: 이전 버전 최소 6개월 지원, 마이그레이션 가이드 제공

**S7F-083** | MED | V2 | CDN 설정 — 정적 자산 배포
- 내용: 프론트엔드 정적 자산을 CDN으로 배포
- 구현: Cloudflare (무료) 또는 Vercel Edge

**S7F-084** | MED | V2 | DDoS 방어 — 대량 요청 방어
- 내용: DDoS 유사 대량 요청 방어
- 구현: Cloudflare (무료), rate limiting (IP당, 사용자당)

---

## Part 11: 백업 / 복구 / DR (6건)

**S7F-085** | HIGH | V1 | 자동 백업 — 일일 자동 데이터 백업
- 내용: 모든 사용자 데이터를 일일 자동 백업
- 구현:
  ```
  Backup Strategy:
  - 일일: SQLite DB + Chroma + KG → ~/vamos/backups/YYYY-MM-DD/
  - 보존: 최근 7일 (일일) + 4주 (주간) + 3개월 (월간)
  - 크기: ~50-200MB/백업
  - 자동화: 앱 시작 시 + 매일 02:00 (cron/scheduler)
  ```

**S7F-086** | HIGH | V1 | 복구 절차 — 백업에서 복구
- 내용: 데이터 손상/손실 시 백업에서 복구하는 절차
- 구현: 원클릭 복구 (설정 > 백업 > 날짜 선택 > 복구)
- 부분 복구: 메모리만, 설정만, 특정 프로젝트만 복구 가능

**S7F-087** | HIGH | V2 | 오프사이트 백업 — 원격 백업
- 내용: V2에서 로컬 외 원격 백업 추가
- 구현: 암호화된 백업 → Cloudflare R2/Backblaze B2 ($0.005/GB/mo)
- E2E 암호화: 사용자 키로 암호화 후 업로드 (서버는 내용 열람 불가)

**S7F-088** | MED | V2 | 데이터 마이그레이션 — V1→V2 마이그레이션
- 내용: V1 로컬 데이터를 V2 서버로 마이그레이션
- 구현:
  ```
  Migration Path:
  V1 SQLite → V2 PostgreSQL (drizzle-kit migrate)
  V1 Chroma → V2 Qdrant (벡터 변환 스크립트)
  V1 NetworkX JSON → V2 Neo4j (Cypher 변환)
  V1 JSON configs → V2 DB configs
  ```
- 원클릭 마이그레이션 도구 + 검증 스크립트

**S7F-089** | MED | V2 | 재해 복구 계획 — DR 절차
- 내용: 서버 전면 장애 시 복구 절차
- RTO: 4시간 / RPO: 24시간
- 절차: 백업 확인 → 새 인스턴스 → 데이터 복구 → DNS 전환 → 검증

**S7F-090** | MED | V2 | 데이터 export/import — 포터빌리티
- 내용: 전체 데이터를 표준 형식으로 내보내기/가져오기
- 형식: JSON (메모리, 설정) + SQLite (대화 이력) + 첨부파일
- 용도: 백업, 이전, GDPR 데이터 이동권 충족

---

## Part 12: 성능 최적화 심화 (6건)

**S7F-091** | CRITICAL | V1 | TTFT 최적화 — 첫 토큰 응답 시간 최소화
- 내용: Time To First Token을 최소화하여 사용자 체감 속도 향상
- 전략:
  | 최적화 | 효과 | 구현 |
  |--------|------|------|
  | Prompt Caching | TTFT 50% 감소 | Claude/OpenAI 캐시 API |
  | Streaming | 체감 0s | SSE 기반 점진적 출력 |
  | Speculative Decoding | TPS 2-3x | V3 자체 서빙 |
  | 로컬 LLM 분류 | API 대기 제거 | Ollama 사전 분류 |
  | 예측 프리페치 | 선제 호출 | 사용자 패턴 기반 |
- 목표: TTFT < 1초 (API) / < 200ms (로컬)

**S7F-092** | CRITICAL | V1 | 메모리 사용량 최적화 — 리소스 효율
- 내용: Tauri + Node.js + Ollama의 전체 메모리 사용량 최적화
- 목표:
  ```
  Memory Budget:
  - Tauri (Rust + WebView): ~50MB
  - Node.js (Agent Runtime): ~100-200MB
  - Ollama (7B Q4): ~4GB
  - ChromaDB (In-Process): ~100MB
  - Total: ~4.5GB (16GB RAM 시스템의 28%)
  ```
- 최적화: 게으른 로딩, 미사용 모델 언로드, GC 튜닝, 스트리밍 처리

**S7F-093** | HIGH | V1 | 동시성 관리 — 병렬 요청 처리
- 내용: 다중 Agent 동시 실행, 병렬 API 호출 관리
- 구현:
  - Node.js Event Loop: 비동기 I/O 기본
  - Promise.all: 독립 API 호출 병렬 실행
  - Worker Threads: CPU 집약 작업 분리
  - 세마포어: 최대 동시 API 호출 제한 (기본 5)

**S7F-094** | HIGH | V1 | 응답 시간 SLO — 내부 성능 목표
- 내용: 각 작업 유형별 응답 시간 목표 (SLO)
- SLO:
  | 작업 | P50 목표 | P95 목표 |
  |------|---------|---------|
  | 간단한 채팅 | < 1s | < 3s |
  | 검색 + 답변 | < 3s | < 8s |
  | 코드 생성 | < 5s | < 15s |
  | 문서 분석 | < 10s | < 30s |
  | Agent 작업 | < 30s | < 120s |
- 모니터링: SLO 위반 시 자동 알림 + 원인 분석

**S7F-095** | HIGH | V2 | 데이터베이스 성능 — 쿼리 최적화
- 내용: DB 쿼리 성능 최적화
- 구현:
  - 인덱스 설계: 자주 조회하는 컬럼에 인덱스
  - 쿼리 계획 분석: EXPLAIN ANALYZE
  - 연결 풀링: pg-pool (PostgreSQL)
  - 읽기 캐시: Redis에 자주 조회되는 데이터 캐싱
  - 벡터 검색: HNSW 인덱스 최적화 (Qdrant ef_construct, m 파라미터)

**S7F-096** | MED | V2 | 프론트엔드 성능 — UI 렌더링 최적화
- 내용: React/Svelte 프론트엔드 렌더링 성능 최적화
- 구현:
  - Virtual Scrolling: 긴 대화 목록 가상화 (react-window)
  - Code Splitting: 라우트별 코드 분할
  - 이미지 최적화: WebP + 레이지 로딩
  - Web Worker: 마크다운 파싱, 코드 하이라이팅 오프스레드
  - 목표: Lighthouse Performance Score ≥ 90

---

## 구현 우선순위 로드맵

### V1 (MVP) — 필수 구현: 41건
- Model Serving: S7F-001~007 (7건)
- Local Infra: S7F-011~020 (10건)
- CI/CD: S7F-045, 047, 048, 050, 051 (5건)
- Monitoring: S7F-053, 054 (2건)
- Cost: S7F-061~065 (5건)
- MLOps: S7F-069, 070, 076 (3건)
- Backup: S7F-085, 086 (2건)
- Performance: S7F-091~094 (4건)
- Prompt: S7F-069, 070 (중복 포함)

### V2 (Server) — 확장 구현: 45건
- Server Infra: S7F-021~030 (10건)
- Container: S7F-037~043 (7건)
- CD: S7F-046, 049, 052 (3건)
- Full Monitoring: S7F-055~060 (6건)
- Cost V2: S7F-066~068 (3건)
- MLOps V2: S7F-071~078 (8건)
- Network: S7F-079~084 (6건)
- Backup V2: S7F-087~090 (4건)
- Performance V2: S7F-095, 096 (2건)

### V3 (Enterprise) — 고급 구현: 10건
- S7F-031~036 (6건) + S7F-044 + GPU + 멀티리전

---

## 기술 스택 최종 요약

| 레이어 | V1 | V2 | V3 |
|--------|-----|-----|-----|
| Frontend | Tauri+React | Next.js+PWA | + Native Mobile |
| Backend | Node.js sidecar | Node.js server | + Worker cluster |
| LLM Local | Ollama | Ollama+vLLM | + TensorRT-LLM |
| LLM Cloud | Claude/GPT API | + LiteLLM Gateway | + Self-hosted |
| Main DB | SQLite+SQLCipher | PostgreSQL | + Read replicas |
| Vector DB | Chroma | Qdrant | + Qdrant Cluster |
| Graph DB | NetworkX+JSON | Neo4j | + Neo4j Cluster |
| Cache | In-memory | Redis | + Redis Cluster |
| Queue | — | BullMQ | + RabbitMQ |
| CI/CD | GitHub Actions | + Docker | + Helm/K8s |
| Monitor | JSON logs | Grafana+Langfuse | + DataDog |
| Backup | Local auto | + Offsite encrypted | + Multi-region |

---

> **다음 단계**: STEP7-G (벤치마크/평가/품질보증)로 이동
