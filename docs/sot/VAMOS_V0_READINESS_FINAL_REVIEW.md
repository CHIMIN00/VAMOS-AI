# VAMOS AI V0 착수 최종 검토 보고서 (상세)

> **버전**: v1.0.0 | **검토일**: 2026-02-24
> **목적**: BLOCKER 상세 분석 + 사용자 준비사항 + V1/V2/V3 이슈 + 추가 코딩 영역 총정리

---

# PART 1. BLOCKER 8건 상세 분석

---

## BLOCKER 1: PLAN 3.0 vs DESIGN 2.0 — I-모듈 번호 완전 불일치

### 문제 상황

PLAN 3.0 §2.3에 있는 I-모듈 목록과 DESIGN 2.0(정본)의 I-모듈 목록이 **번호-이름 매핑부터 다릅니다**.

**PLAN 3.0이 말하는 것 (구 번호)**:
```
I-1  대화 이해
I-2  RAG·검색
I-3  메모리 관리
I-4  멀티모달 처리
I-5  라우팅
I-6  Self-check·Self-evo
I-7  안전 ← ❌ 틀림
I-8  비용 ← ❌ 틀림
I-9  로그 ← ❌ 틀림
I-10 UI  ← ❌ 틀림
(I-11~I-13, I-17, I-20 아예 누락)
총 21개라고 표기
```

**DESIGN 2.0 정본 (올바른 번호)**:
```
I-1  Intent Detector (대화 이해)
I-2  Context Builder (RAG)
I-3  Memory System
I-4  Multimodal Interpreter
I-5  Condition & Decision Engine
I-6  Self-check Engine
I-7  Project/Session Manager    ← PLAN은 "안전"이라고 함
I-8  Policy Engine              ← PLAN은 "비용"이라고 함
I-9  Cost Manager               ← PLAN은 "로그"라고 함
I-10 Tool Registry/Router       ← PLAN은 "UI"라고 함
I-11 Output Composer            ← PLAN에서 누락
I-12 Workflow Builder           ← PLAN에서 누락
I-13 Multimodal Output Renderer ← PLAN에서 누락
I-14 Summarizer & Memory Distiller
I-15 Evidence & QoD Manager
I-16 Knowledge Search Engine
I-17 Blue Node Manager          ← PLAN에서 누락
I-18 Self-evo Engine
I-19 Approval Manager
I-20 Failure/Fallback Manager   ← PLAN에서 누락
I-21 Source Evolution (소스 진화)
I-22 Task/Project Manager       ← PLAN에 없음
I-23 Doc/Code Structuring       ← PLAN에 없음
I-24 Knowledge Graph Engine     ← PLAN에 없음
I-25 SDAR Engine                ← PLAN에 없음
총 25개
```

### 왜 위험한가?

- 개발자가 PLAN을 읽으면 **I-7을 "안전 모듈"로 구현**하지만, 실제로는 "Project/Session Manager"
- I-11, I-12, I-13, I-17, I-20 총 5개 모듈이 PLAN에서 완전 누락 — 이 모듈들을 몰라서 구현 안 할 위험
- I-22~I-25 총 4개 모듈이 PLAN에 없음 — 25개 중 21개만 보임
- P7-MOD 구현 우선순위도 구 번호 기반이라 "Phase 3: 나머지 11개"라고 했는데 실제로는 14개

### 해결 방법

PLAN-3.0 §2.3의 I-모듈 목록에 **"⚠️ 본 번호는 PLAN 2.0 기준. DESIGN 2.0 §5.6이 정본"** 경고 추가 + 올바른 25개 목록으로 교체

---

## BLOCKER 2: P0 활성 도메인 리스트 — 순환 참조 교착 상태

### 문제 상황

D2.0-03 (BLUE_NODES) §7에서:
```
잠금 보류: '구체 도메인 리스트'는 PLAN 3.0 근거 기반으로만 확정
(현재 문서에서 발명 금지)
```

→ 그런데 PLAN 3.0은 P0/P1/P2 도메인 분류를 **정식으로 정의하지 않음**
→ D2.0-03은 "PLAN을 봐라" → PLAN은 "명시 안 함" → 아무도 결정 못하는 교착 상태

### 왜 위험한가?

- V0 스캐폴딩에서 Blue Node를 몇 개, 어떤 도메인으로 만들지 결정 불가
- IntentFrame의 `domain_hint` 필드에 넣을 값이 없음
- PolicyGate의 P0/P1/P2 승인 로직을 구현할 수 없음

### 해결 방법

PLAN-3.0에 공식 P0/P1/P2 분류를 추가:
- **P0 (기본 활성)**: Dev, Research, Productivity
- **P1 (1회 승인)**: Content, Quant
- **P2 (세션별 승인)**: Trading, Investing

---

## BLOCKER 3: Storage 이벤트 코드 미등록

### 문제 상황

D2.0-06 §8에서 Storage 관련 이벤트 코드 7개를 **"후보(예시)"**로만 나열:
```
event_type 후보(예시):
  - storage.policy.checked
  - storage.memory.write.requested
  - storage.memory.write.completed
  - storage.vector.insert.denied
  - storage.pii.longterm.denied

failure_code 후보(예시):
  - PII_LONGTERM_DENIED

fallback_id 후보(예시):
  - FB_DENY_STORAGE
```

→ D2.1-D2의 중앙 레지스트리(53개 event_type)에는 `storage.*` 네임스페이스가 **하나도 없음**

### 왜 위험한가?

- PII 장기 저장 차단 로직을 구현해도 이벤트를 emit할 수 없음
- 로그 검증이 실패하고 감사 추적(audit trail) 불가
- I-20 Failure/Fallback Manager가 `FB_DENY_STORAGE`를 찾지 못해 에러 발생

### 해결 방법

D2.1-D2 EventTypeRegistry에 5개 event_type + 1개 failure_code + 1개 fallback_id를 정식 등록

---

## BLOCKER 4: 다운시프트 임계값 — 같은 문서 내 모순

### 문제 상황

**D2.0-07 §4.2 (660줄)**:
```
다운시프트 임계값(LOCK): 80% 경고 / 100% 차단
```

**D2.0-07 §9 (1144줄)**:
```
주의: "근접 임계치 수치(예: 80%)"는 운영 설정 값이며,
정본 잠금은 PLAN/운영 근거로만(발명 금지)
```

→ §4는 "LOCK"이라고 하고, §9는 "80%는 예시일 뿐"이라고 함
→ 같은 문서 안에서 서로 반대되는 권위 수준

### 왜 위험한가?

- 개발자가 `CostGate`에 80%를 하드코딩해야 하는지, 설정 가능하게 해야 하는지 판단 불가
- 다른 문서(D2.0-02, D2.0-04)도 각각 다른 표현 사용

### 해결 방법

§9의 문구를 §4와 일치시킴: "80%/100%는 §4에서 LOCK 확정. 운영 조정은 Approval Gate 승인 필수"

---

## BLOCKER 5: Node.js Sidecar vs Python Backend

### 문제 상황

**STEP7 F-I (S7F-012, CRITICAL V1)**:
```
Backend: Rust(Tauri) + sidecar Node.js
기술 스택: Node.js 22 LTS, LangGraph.js, @anthropic-ai/sdk
```

**PLAN 3.0 정본 (통신 계층)**:
```
React UI ↔ Tauri IPC ↔ Rust Backend ↔ JSON-RPC stdin/stdout ↔ Python AI/ML
```

→ STEP7은 **Node.js + LangGraph.js** 아키텍처
→ 정본은 **Python + LangGraph(Python)** 아키텍처
→ 완전히 다른 기술 스택

### 왜 위험한가?

- Node.js로 시작하면 **모든 패키지가 다름** (npm vs pip)
- LangGraph.js vs LangGraph(Python)은 API가 다름
- PHASE_B1~B7 전체가 Python 기준으로 작성됨 → Node.js면 전부 무용지물

### 해결 방법

STEP7 F-I에 "PLAN-3.0 정본: Python backend" 오버라이드 주석 추가. S7F-012는 대안 참조로 강등

---

## BLOCKER 6: 디렉토리 구조 충돌

### 문제 상황

**STEP7**: `~/vamos/config/settings.yaml` (홈 디렉토리 기반, YAML)
**PHASE_B2 정본**: `vamos/config/config.v1.toml` (monorepo, TOML)

### 해결 방법

PHASE_B2 monorepo를 정본으로 선언. STEP7에 주석 추가

---

## BLOCKER 7: Config 파일 포맷 (YAML vs TOML)

### 문제 상황

STEP7에서 `.yaml` 4곳 이상 사용 (settings.yaml, models.yaml, features.yaml, core_v1.x.yaml)
→ 정본은 `config.toml` (Pydantic v2 + tomli LOCK)

### 해결 방법

STEP7 전체에서 `.yaml` → `.toml` 교체 또는 오버라이드 배너 추가

---

## BLOCKER 8: 스키마 버전 불일치

### 문제 상황

```
D1 SCHEMA_GLOSSARY     = v2.3.0
D2 SCHEMA_ORANGE_CORE  = v2.2.3
D3 SCHEMA_BLUE_NODES   = v2.4.0
D4 SCHEMA_INFRA_CORE   = v2.3.0
D5 SCHEMA_WORKFLOW     = v2.3.0
D6 SCHEMA_STORAGE      = v2.3.1
D7 SCHEMA_SAFETY       = v2.3.0
D8 SCHEMA_UI_UX        = v2.3.0
```

→ 8개 스키마 문서 중 **6개가 다른 버전**
→ V0 GO/NO-GO 체크리스트에 "v3.0.0 통일" 필수 항목

### 해결 방법

전체 D1~D8을 v3.0.0으로 일괄 승격 + 내부 REF 크로스레퍼런스 업데이트

---

# PART 2. 사용자가 직접 준비해야 할 사항

---

## 2.1 V0 시작 전 — 당신이 해야 할 일

### A. API Key / 계정 (1건)

| 항목 | 어디서 | 비용 | 필수 여부 |
|------|--------|------|----------|
| **OpenAI API Key** | https://platform.openai.com 가입 → API Keys 발급 | 종량제 (gpt-4o-mini ~$0.15/1M tokens) | **필수** |

> 이 키 1개만 있으면 V0 시작 가능. 나머지는 전부 로컬.

### B. 소프트웨어 설치 (7건)

| # | 소프트웨어 | 설치 방법 | 비고 |
|---|-----------|----------|------|
| 1 | **Python 3.11+** | python.org 또는 pyenv | venv 필수 |
| 2 | **Node.js 18+ LTS** | nodejs.org 또는 nvm | npm 포함 |
| 3 | **Rust 1.70+** | rustup.rs | stable 채널 |
| 4 | **Ollama** | ollama.ai 에서 다운로드 | Windows 지원 |
| 5 | **Git** | git-scm.com | 최신 버전 |
| 6 | `ollama pull llama3.2:3b` | 터미널에서 실행 | Mini LLM (~2GB) |
| 7 | `ollama pull llama3.1:8b` | 터미널에서 실행 | Main LLM (~5GB) |

### C. 하드웨어 확인

| 항목 | 최소 요구 | 권장 |
|------|----------|------|
| RAM | 8GB | 16GB+ |
| 저장공간 | 20GB 여유 | 50GB+ |
| GPU | 없어도 됨 (CPU 모드) | NVIDIA GPU 있으면 추론 빠름 |
| OS | Windows 11 (현재 환경) | 정상 지원 |

### D. 결정해야 할 사항 (3건)

| # | 결정 사항 | 추천 |
|---|----------|------|
| 1 | **패키지 매니저**: npm vs pnpm | pnpm 추천 (빠르고 디스크 절약) |
| 2 | **Python 의존성 관리**: Poetry vs pip+pip-tools | Poetry 추천 (lock 파일 관리) |
| 3 | **PyTorch CPU vs GPU** | 현재 PC에 GPU 없으면 CPU 버전 |

---

## 2.2 V1 MVP 전 — 추가 준비 사항

### A. 추가 API Key (4건)

| # | 서비스 | 용도 | 가입 URL | 비용 |
|---|--------|------|---------|------|
| 1 | **Tavily** | 웹 검색 (E-2) | tavily.com | Free tier 1000회/월 |
| 2 | **SerpAPI** | 검색엔진 (E-2 보조) | serpapi.com | Free tier 100회/월 |
| 3 | **E2B** | 코드 샌드박스 (E-4) | e2b.dev | Free tier 가능 |
| 4 | **Unstructured.io** | 문서 파싱 (E-3) | unstructured.io | Free tier 가능 |

### B. 추가 소프트웨어 (4건)

| # | 소프트웨어 | 용도 | 비용 |
|---|-----------|------|------|
| 1 | **Docker Desktop** | 코드 실행 샌드박스 (보안) | 무료 (개인) |
| 2 | **Tauri Signing Key** | 앱 서명 (릴리스) | 무료 (자체 생성) |
| 3 | **Playwright** | E2E 테스트 | 무료 |
| 4 | **SQLCipher** | 데이터 암호화 | 무료 (오픈소스) |

### C. GitHub 설정 (2건)

| # | Secret | 용도 |
|---|--------|------|
| 1 | `TAURI_SIGNING_PRIVATE_KEY` | 앱 코드 서명 |
| 2 | `TAURI_SIGNING_PRIVATE_KEY_PASSWORD` | 서명 키 비밀번호 |

---

## 2.3 V2 Pro 전 — 추가 준비 사항

### A. 서버 / 인프라 (비용 발생)

| # | 항목 | 용도 | 예상 월 비용 |
|---|------|------|-------------|
| 1 | **VPS 서버** (Vultr/DigitalOcean 등) | Docker Compose 배포 | ~₩20,000 |
| 2 | **PostgreSQL 16** (Neon/Supabase) | 메인 DB | ~₩10,000 |
| 3 | **Qdrant** (셀프호스팅 or Cloud) | 벡터 DB | Free~₩15,000 |
| 4 | **Neo4j Community** | 그래프 DB | 무료 (GPL 주의) |
| 5 | **Redis 7** | 캐시 | 무료 (로컬) |
| **합계** | | | **~₩45,000/월** |

### B. 추가 API Key (2건)

| # | 서비스 | 용도 | 비용 |
|---|--------|------|------|
| 1 | **Anthropic (Claude)** | V2 메인 LLM | 종량제 |
| 2 | **Slack Webhook** | 배포 알림 | 무료 |

### C. GitHub Secrets (9건 추가)

`STAGING_SSH_KEY`, `STAGING_HOST`, `PROD_SSH_KEY`, `PROD_HOST_LIST`, `POSTGRES_USER`, `POSTGRES_PASSWORD`,
`QDRANT_API_KEY`, `NEO4J_AUTH`, `OPENAI_API_KEY` (CI용), `SLACK_WEBHOOK_URL`

---

## 2.4 V3 Enterprise 전 — 추가 준비 사항

| # | 항목 | 예상 월 비용 |
|---|------|-------------|
| 1 | **Kubernetes 클러스터** | 변동 |
| 2 | **GPU 서버** (A10G for vLLM) | ~$144 (~₩190,000) |
| 3 | **Qdrant Cloud** (관리형) | 유료 |
| 4 | **Neo4j Aura** (관리형) | 유료 |
| **합계** | | **₩266,000 이내 (비용 상한)** |

---

# PART 3. V1/V2/V3 관점 이슈 재정리

---

## 3.1 V1 이슈 총정리 (19건)

### HIGH (해결 없이 V1 출시 불가) — 12건

| # | ID | 문제 | 해결안 | 카테고리 |
|---|-----|------|--------|---------|
| 1 | V1-001 | I-Series 모듈 수 21 vs 25 | 25개 정본 확정 | 문서 |
| 2 | V1-016 | I-21~I-25 정의 누락 | 5개 모듈 추가 정의 | 문서 |
| 3 | V1-002 | E-15 명칭 충돌 | 이중명 "File System / Cloud Collector" | 문서 |
| 4 | V1-003 | S-5 명칭 충돌 | 이중명 "Router Evolution / Cloud Evolver" | 문서 |
| 5 | V1-008 | 38개 DEFER/TBD 미분류 | 전수 태깅 완료 (V1 blocking=0) | 문서 |
| 6 | V1-015 | Python backend 진입점 미정 | `backend/main.py` 확정 | 설계 |
| 7 | OC-2 | QoD 임계값 수치 미잠금 | 운영 기본값 0.4/0.7 채택 | 설계 |
| 8 | OC-5 | 한국어 로컬 LLM 미확정 | DEFER V1.1 / GPT-4o 임시 | 설계 |
| 9 | BN-12 | 이벤트 네이밍 최종 잠금 미완 | STEP 1.1 표준을 V1 정본 | 설계 |
| 10 | CC-006 | EventTypeRegistry agent.*/sdar.* 미등록 | D2 레지스트리 추가 | 스키마 |
| 11 | CC-007 | Python/TypeScript 스키마 동기화 없음 | Pydantic→Zod 변환기 구축 | 도구 |
| 12 | IF-21 | 강등 규칙(use_mini_only) 근거 미확보 | D2.0-07 §4 LOCK 근거 채택 | 설계 |

### MEDIUM (V1 출시 가능하지만 개선 필요) — 4건

| # | ID | 문제 | 해결안 |
|---|-----|------|--------|
| 1 | V1-004 | approval_status enum 2값 vs 4값 | 4값 통일 |
| 2 | V1-006 | QoD 가중치 4요소 vs 5요소 | PLAN-3.0 5요소 |
| 3 | V1-010 | Guardrails 3Layer vs 4Layer | 4Layer 정본 |
| 4 | V1-013 | 비용 ₩40K vs $8 혼동 | BASE 정본 |

### LOW (V1.1에서 해결 가능) — 3건

| # | ID | 문제 |
|---|-----|------|
| 1 | V1-005 | datetime.utcnow() deprecated |
| 2 | V1-009 | LangChain 허용 범위 명시 |
| 3 | V1-014 | React 18 vs 19 |

---

## 3.2 V2 이슈 총정리 (12건)

| # | ID | 문제 | 심각도 | 실질 미결정? |
|---|-----|------|--------|------------|
| 1 | V2-003 | Agent Teams vs FREEZE 충돌 | HIGH | 해결안 있음 |
| 2 | V2-008 | STEP7 TITLE_ONLY 44% 상세화 | HIGH | 작업 필요 |
| 3 | V2-001 | 10-Layer 명칭 충돌 | MEDIUM | 해결안 있음 |
| 4 | V2-002 | SDAR 활성화 조건 | MEDIUM | 해결안 있음 |
| 5 | V2-004 | JSONL→PostgreSQL 로그 마이그레이션 | MEDIUM | 스크립트 필요 |
| 6 | V2-005 | Chroma→Qdrant 벡터 재임베딩 | MEDIUM | 스크립트 필요 |
| 7 | V2-006 | NetworkX→Neo4j 그래프 변환 | MEDIUM | 스크립트 필요 |
| 8 | CC-004 | Gate G0-G4 이중 사용 | MEDIUM | 접두사 추가 |
| 9 | CC-012 | HMAC 서명 키 관리 | MEDIUM | 프로토콜 설계 필요 |
| 10 | DEFER-AT-001 | **MessageBus: Redis vs In-Memory** | MEDIUM | **실질 미결정** |
| 11 | DEFER-AT-002 | **GroupChat 순서 알고리즘** | MEDIUM | **실질 미결정** |
| 12 | SF-54 | GDPR 기능 (열람/이동/제한) | MEDIUM | V2 구현 |

> V2에서만 진정한 미결정이 2건 (MessageBus, GroupChat)

---

## 3.3 V3 이슈 총정리 (4건 + 미결정 3건)

| # | ID | 문제 | 심각도 |
|---|-----|------|--------|
| 1 | V3-001 | K8s 배포 명세 불충분 | MEDIUM |
| 2 | V3-002 | Self-evo Governance 미상세 | MEDIUM |
| 3 | V3-003 | 비용 상한 현실성 (GPU ~$144/월) | LOW |
| 4 | V3-004 | GraphRAG 90% 벤치마크 미정의 | LOW |

**V3 미결정 사항**:
- DEFER-AT-003: Agent Marketplace 등록 기준
- DEFER-AT-004: Federated Agent 승인 정책
- DEFER-AT-005: A2A 프로토콜 설계

---

# PART 4. 추가 코딩 영역 총정리 (V0~V3 파이프라인 외)

> V0~V3의 I-Series, E-Series 모듈 구현 외에도 **대량의 추가 코딩 작업**이 필요합니다.

---

## 4.1 UI/UX 코딩 (가장 큰 영역 — ~135개 항목)

### A. 핵심 레이아웃 (V1)

| 항목 | 설명 | 복잡도 |
|------|------|--------|
| **3-Column Fluid Layout** | 좌(250-300px) / 중앙(flex) / 우(350-400px) 리사이즈 가능 | 중 |
| **Builder View (Cockpit)** | 리소스 트리 + 워크플로우 그래프 캔버스 + 로그/승인/비용 패널 | 높음 |
| **Hologram View** | 타임라인 사이드바 + 스트리밍 캔버스 + Glass HUD 카드 | 높음 |
| **CLI Interface** | `vamos run`, `approve`, `status`, `cost`, `memory` 명령어 | 중 |

### B. React 페이지 (5개, V1)

| 페이지 | 설명 | 복잡도 |
|--------|------|--------|
| Dashboard | 프로젝트 개요, 최근 세션, 시스템 상태 | 중 |
| Chat | Hologram View 채팅 (스트리밍, 아티팩트, 증거 패널) | 높음 |
| Workflow | Builder View 그래프 시각화, 노드 인스펙터 | 높음 |
| Memory | L0/L1/L2/L3 메모리 탐색기, 마스킹 미리보기 | 중 |
| Settings | 설정 편집기, 테마, 언어, 모델 선택 | 중 |

### C. React 컴포넌트 (~39개, V1)

| 그룹 | 항목 수 | 핵심 컴포넌트 |
|------|---------|-------------|
| Decision | 3 | DecisionCard, DecisionLockBadge, Decision 시각화 |
| Chat | 6 | ChatPanel, UserBubble, AIBubble, ThinkingBlock, ArtifactEmbed, StreamingEffect |
| Approval | 3 | ApprovalDialog, ApprovalCard (슬라이드인), P2 확인 모달 |
| Cost | 5 | CostDashboard, BudgetGauge, DownshiftControl, TokenCounter, 경고 Toast |
| Evidence | 4 | VerificationBadge, UncertaintyAlert, 인용 점프, QoD 표시 |
| Memory | 4 | MemoryCandidateList, MaskingPreview, CommitButton, PII 거부 카드 |
| Node/Flow | 4 | NodeStatusBadge, ORANGE 헥사곤, BLUE 서클, Flow Edge 애니메이션 |
| Guardrails | 3 | GuardrailsAlert, PolicyBlockedCard, PII 감지 모달 |
| Input | 4 | 멀티라인 텍스트, 드래그앤드롭, 클립보드, 음성 입력 |
| Navigation | 3 | 대화 사이드바, 프로젝트 폴더, 세션 목록 |
| 기타 | 5 | ModelSelector, Table, Diagram, Log Viewer, Keyboard Shortcuts |

### D. Custom Hooks (8개) + Zustand Stores (7개)

```
Hooks: useTauriIPC, useDecision, useWorkflow, useStreaming, useCost, useApproval, useIPC, useConfig
Stores: appStore, decisionStore, costStore, agentStore, configStore, memoryStore, workflowStore
```

### E. i18n 국제화 (V1)

- react-i18next 설정
- `locales/ko-KR/`, `locales/en-US/` 번역 파일
- 하드코딩 텍스트 전면 금지

### F. 디자인 시스템 (V1)

- CSS Custom Properties (ORANGE #F97316, BLUE #00F6FF 등)
- 아이콘 시스템, 알림 우선순위 (P0/P1/P2)
- 애니메이션 시스템 (Node 펄싱, Flow 애니메이션, 로딩 등)

### G. 멀티모달 UI (V1~V3)

| V1 (핵심) | V2 (확장) | V3 (고급) |
|-----------|-----------|-----------|
| 이미지 입력 (CLIP) | 실시간 음성 채팅 | 3D 생성 |
| OCR (Tesseract+PyMuPDF) | 이미지 생성 게이트웨이 | 실시간 비디오 스트리밍 |
| STT (Whisper 로컬) | Computer Use Agent | 아바타/디지털 휴먼 |
| TTS (Edge TTS) | 멀티모달 RAG | 음성 클로닝 |
| 차트 생성 (Mermaid+Plotly) | 팟캐스트 자동 생성 | AR/공간 이해 |
| 문서 생성 (Markdown→PDF) | PPT 자동 생성 | 다중 사용자 협업 |
| 비디오 분석 (yt-dlp+Whisper) | 멀티모달 워크플로우 | 수어 생성 |

---

## 4.2 Rust/Tauri 인프라 코딩 (~108개 항목)

### A. 72개 Tauri IPC 커맨드 핸들러

모든 `vamos:{category}:{action}` 형태의 Rust 핸들러:

| 카테고리 | 커맨드 수 | 예시 |
|---------|----------|------|
| Core (Decision/Workflow/Session) | 15 | `vamos:decision:create`, `vamos:workflow:start` |
| Agent (Node/Pipeline/Marketplace) | 15 | `vamos:node:dispatch`, `vamos:pipeline:hitl_respond` |
| Storage (Memory/Vector/Cache/GraphRAG/QoD) | 18 | `vamos:memory:save`, `vamos:vector:search` |
| Safety (Policy/Cost/Approval/Guardrails/RBAC) | 19 | `vamos:policy:check`, `vamos:cost:budget_get` |
| UI (Log/Config/Theme/Notification) | 5 | `vamos:ui:log_stream`, `vamos:ui:config_set` |

### B. 13개 Python-Rust JSON-RPC 메서드

```
langgraph.workflow.run       langgraph.stage.execute
langgraph.decision.create    langgraph.node.dispatch
langgraph.verify.run_chain   embedding.encode
embedding.store              llm.generate
llm.record_invoke            llm.rate_limit.get
mcp.bridge.init              mcp.bridge.health
mcp.tools.discover
```

### C. Rust 핵심 모듈

| 모듈 | 설명 | 복잡도 |
|------|------|--------|
| `ipc_protocol.rs` | JSON 직렬화, trace_id 주입, 에러 표준화 | 중 |
| `python_manager.rs` | Python 프로세스 스폰/헬스체크/재시작/stdin/stdout 파이프 | 높음 |
| `config_loader.rs` | config.toml → Rust struct, ENV 오버라이드 | 낮음 |
| serde 모델 구조체 | D2.1 스키마와 매칭되는 Rust struct 24개 | 중 |

---

## 4.3 테스트 코딩 (~97개 항목)

| 테스트 유형 | 파일 수 | 대상 |
|-----------|---------|------|
| Python Unit (pytest) | ~40 | 스키마 11 + orange_core 6 + blue_nodes 6 + safety 7 + storage 5 + agent 10 |
| Rust Unit (cargo test) | ~8 | IPC 핸들러 4 + Python 프로세스 관리 4 |
| React Unit (vitest) | ~15 | 컴포넌트 6 + Store 3 + Hook 2 + 기타 4 |
| Integration | ~13 | IPC 브릿지, 파이프라인 E2E, Gate 검증, Storage 스택 등 |
| E2E (Playwright) | ~8 | 기본 채팅, 비용 다운시프트, HITL 승인, Guardrails 차단 등 |
| 커버리지 목표 | - | Python 80%+, Rust 60%+, React 70%+ |

---

## 4.4 CI/CD 코딩 (~18개 항목)

| GitHub Actions 워크플로우 | 용도 | 버전 |
|--------------------------|------|------|
| `quality-python.yml` | ruff lint + mypy | V1 |
| `quality-rust.yml` | cargo fmt + clippy | V1 |
| `quality-react.yml` | eslint + tsc | V1 |
| `quality-schema.yml` | Pydantic 모델 검증 | V1 |
| `test-python.yml` | pytest + coverage | V1 |
| `test-rust.yml` | cargo test + tarpaulin | V1 |
| `test-react.yml` | vitest + v8 coverage | V1 |
| `coverage-report.yml` | 3개 언어 커버리지 병합 | V1 |
| `build-tauri.yml` | 크로스 플랫폼 빌드 (Win/Mac/Linux) | V1 |
| `release.yml` | 전체 릴리스 파이프라인 | V1 |
| `security.yml` | pip-audit, cargo-audit, npm audit | V1 |
| `build-docker.yml` | Docker 이미지 빌드 | V2 |
| `deploy-v2.yml` | Docker Compose SSH 배포 | V2 |
| `deploy-v3.yml` | K8s Helm Blue-Green 배포 | V3 |

---

## 4.5 도구/자동화 코딩 (~19개 항목)

| 도구 | 설명 | 복잡도 | 버전 |
|------|------|--------|------|
| **24개 Pydantic v2 스키마 클래스** | D2.1 → contracts.py (SOT) | 높음 | V0 |
| **Pydantic→Zod 변환기** | Python→TypeScript 스키마 동기화 | 높음 | V1 |
| **Pydantic→serde 변환기** | Python→Rust 스키마 동기화 | 높음 | V1 |
| **JSON Schema Golden Source** | shared/types/ 자동 생성 | 중 | V0 |
| **EventTypeRegistry (53+)** | 전체 이벤트 코드 enum | 중 | V0 |
| **Config 로더 (Python)** | ENV > toml > default 우선순위 | 중 | V0 |
| **Config 로더 (Rust)** | toml → serde struct | 낮음 | V0 |
| **SQLite→PostgreSQL 마이그레이션** | V2 DB 전환 | 높음 | V2 |
| **Chroma→Qdrant 마이그레이션** | V2 벡터 DB 전환 | 높음 | V2 |
| **NetworkX→Neo4j 마이그레이션** | V2 그래프 DB 전환 | 높음 | V2 |

---

## 4.6 보안 코딩 (~15개 항목)

| 항목 | 설명 | 버전 |
|------|------|------|
| NeMo Guardrails (Layer 1) | 입력 방어 rail 설정 + 통합 | V1 |
| Guardrails AI (Layer 2) | 출력 검증, 구조화 출력 | V1 |
| LlamaGuard (Layer 3) | 안전 분류 (GPU 필요) | V2 |
| PII Regex 마스킹 | 주민번호, 전화번호, 이메일, 카드번호 등 | V1 |
| RBAC 시스템 | OWNER/ADMIN/OPERATOR/VIEWER 4레벨 | V1 |
| Autonomy 레벨 관리 | L0~L3 자율성 게이팅 | V1 |
| P2 세션 승인 + 자동 OFF | 세션 종료 시 자동 비활성화 | V1 |
| Docker 코드 실행 샌드박스 | 네트워크 격리, 30초 타임아웃 | V1 |
| 승인 타임아웃 (10분 auto-deny) | 타임아웃 시 자동 거부 | V1 |
| SQLCipher 암호화 | AES-256-CBC 데이터 암호화 | V1 |
| API Key 관리 | .env + dotenv + .gitignore | V1 |
| 입력 검증 | Zod + regex 패턴 | V1 |
| HMAC-SHA256 키 관리 | Agent Teams MessageBus 인증 | V2 |

---

## 4.7 MCP 서버/클라이언트 코딩 (~7개)

| 항목 | 설명 | 버전 |
|------|------|------|
| **MCP Bridge Layer** | Streamable HTTP 클라이언트, 도구 탐색/호출 라우팅 | V1 |
| **MCP Server** | VAMOS 자체 도구 노출 | V1 |
| **MCP Client** | 외부 MCP 서버 연결 | V1 |
| **Pyodide MCP 래퍼** | 로컬 Python 실행 | V1 |
| **PyMuPDF MCP 래퍼** | 로컬 PDF 파싱 | V1 |
| **CLIP MCP 래퍼** | 로컬 이미지 분석 | V2 |
| **Playwright MCP 래퍼** | 브라우저 자동화 | V1 |

---

## 4.8 LangGraph 프레임워크 코딩

| 항목 | 설명 | 복잡도 |
|------|------|--------|
| **StateGraph 정의** | 5-Phase 파이프라인 (Intake→Plan→Execute→Verify→Deliver) | 높음 |
| **Gate 통합 노드** | Policy/Cost/Approval/Evidence/SelfCheck를 LangGraph 노드로 | 높음 |
| **Soft/Hard Loop 제어** | 검증 실패 → 1회 자동 재시도 → HITL 승인 | 중 |
| **Circuit Breaker** | closed/open/half_open 상태 관리 | 중 |

---

## 4.9 이벤트/로깅 시스템

| 항목 | 설명 |
|------|------|
| EventTypeRegistry 구현 | 53+ 이벤트 across all 네임스페이스 |
| FailureCodeRegistry 구현 | 20개 실패 코드 + 핸들러 매핑 |
| FallbackRegistry 구현 | 13개 폴백 전략 + 실행 로직 |
| Event Bus / Pub-Sub | trace 기반 이벤트 라우팅 |
| JSON 구조화 로거 | Python/Rust/TypeScript 3개 언어, trace_id 필수 |

---

## 4.10 기타 코딩 영역

### AI 투자 분석 (V1 Week 10-12)

| 항목 | 설명 |
|------|------|
| Paper Trading MVP | 시뮬레이션 트레이딩 (51% Gate) |
| 5-Agent Pipeline | Perplexity→Gemini→ChatGPT→Claude→Copilot 체인 |
| 법적 컴플라이언스 | Wash Sale, PDT, Uptick Rule 자동 감지 |

### Multi-Brain Adapter (A-1, V1)

| 항목 | 설명 |
|------|------|
| LLM 어댑터 추상화 | Ollama/GPT-4o/Claude/vLLM 통합 인터페이스 |
| Failover 로직 | GPT-4o → Claude → Ollama (3-타임아웃 전환) |
| 비용 기반 라우터 | V1=Mini 90%+ / V2=Mini 60-70%, Main 30-40% |

### Agent Teams (V2/V3)

| 항목 | 설명 | 버전 |
|------|------|------|
| Lead Agent + Sub-Agent 위임 | 3-깊이 위임 체인 | V1(기본) |
| MessageBus | 에이전트 간 통신 버스 | V2 |
| 5가지 협업 패턴 | Sequential/Parallel/Debate/Supervisor/Handoff | V2/V3 |
| Agent Marketplace | 에이전트 탐색/설치/검증 | V3 |

---

# PART 5. 전체 코딩 작업량 요약

| 영역 | V0 | V1 | V2 | V3 | 합계 |
|------|----|----|----|----|------|
| **UI/UX 컴포넌트/페이지** | 0 | ~75 | ~40 | ~20 | **~135** |
| **인프라 (Rust IPC, Docker, 빌드)** | ~8 | ~80 | ~15 | ~5 | **~108** |
| **테스트 (Unit/Integration/E2E)** | ~15 | ~75 | ~5 | ~2 | **~97** |
| **CI/CD (GitHub Actions)** | 0 | ~12 | ~4 | ~2 | **~18** |
| **도구 (스키마 생성, Config, 마이그레이션)** | ~10 | ~5 | ~4 | 0 | **~19** |
| **보안 (Guardrails, RBAC, PII)** | 0 | ~8 | ~5 | ~2 | **~15** |
| **MCP 서버/클라이언트** | 0 | ~5 | ~2 | 0 | **~7** |
| **기타 (이벤트, 로깅, LangGraph, Agent)** | ~8 | ~25 | ~10 | ~10 | **~53** |
| **합계** | **~41** | **~285** | **~85** | **~41** | **~452** |

> **V1이 가장 큰 작업량** (~285개 항목). UI/UX가 가장 큰 단일 영역 (~135개).

---

# PART 6. 최종 체크리스트 요약

## 사용자 즉시 액션 (V0 시작 전)

- [ ] OpenAI API Key 발급
- [ ] Python 3.11+ 설치 확인
- [ ] Node.js 18+ LTS 설치 확인
- [ ] Rust 1.70+ 설치 확인
- [ ] Ollama 설치 + `ollama pull llama3.2:3b` + `ollama pull llama3.1:8b`
- [ ] Git 설치 확인
- [ ] 패키지 매니저 결정 (npm vs pnpm)
- [ ] Python 의존성 관리 결정 (Poetry vs pip)
- [ ] PyTorch CPU vs GPU 결정

## 문서 수정 (BLOCKER 해결, ~3시간)

- [ ] BLOCKER 1: PLAN-3.0 I-모듈 목록 교정 (I-25까지)
- [ ] BLOCKER 2: PLAN-3.0에 P0/P1/P2 도메인 분류 추가
- [ ] BLOCKER 3: D2.1-D2 레지스트리에 storage.* 코드 등록
- [ ] BLOCKER 4: D2.0-07 §9 다운시프트 정본 통일
- [ ] BLOCKER 5: STEP7 F-I Python backend 오버라이드
- [ ] BLOCKER 6: STEP7 F-I 디렉토리 구조 정본 주석
- [ ] BLOCKER 7: STEP7 F-I config.toml 통일
- [ ] BLOCKER 8: D1~D8 스키마 v3.0.0 일괄 승격

## 이후 순서

1. BLOCKER 해결 (문서 수정 ~3시간)
2. V0 스캐폴딩 시작 (1-2주)
3. V1 Phase 1: ORANGE CORE (4주)
4. V1 Phase 2-3: Storage + Blue Nodes (병렬, 6주)
5. V1 Phase 4: UI/UX (4주)
6. V1 Phase 5: Integration + Test (4주)
7. V1 릴리스
8. V2 준비 (서버/DB 준비 + 마이그레이션)
