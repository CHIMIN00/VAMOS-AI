---
session: 25
sections: [31, 32]
status: complete
---

# §31. MCP — Model Context Protocol (모델 컨텍스트 프로토콜)

## §31.1 MCP란? — USB 포트 같은 도구 연결 표준

### 비유: USB 포트

> 여러분의 컴퓨터에는 USB 포트가 있습니다. 마우스든, 키보드든, 외장하드든 — USB 규격만 맞으면 어떤 장치든 꽂아서 바로 쓸 수 있죠. MCP는 AI 세계의 USB 포트입니다. 웹 검색이든, 코드 실행이든, 데이터베이스든 — MCP 규격만 맞으면 어떤 도구든 AI에 연결할 수 있습니다.

### 정의

**MCP (Model Context Protocol, 모델 컨텍스트 프로토콜)**는 Anthropic이 만든 **공개 표준 프로토콜 (Open Standard Protocol)**로, LLM(대규모 언어 모델)과 외부 도구를 연결하는 **단일 표준**입니다. [근거: D2.0-03 §6.4.1]

기존에는 도구마다 연결 방식이 달라서 "A 도구는 REST API로, B 도구는 SDK로, C 도구는 직접 코드로" 연결해야 했습니다. MCP는 이 모든 것을 **하나의 규격으로 통일**합니다.

### VAMOS에서 MCP의 위치

```
┌─────────────────────────────────────────────┐
│  ORANGE CORE (판단/제어)                      │
│  "어떤 도구를 쓸지 결정"                        │
└──────────────┬──────────────────────────────┘
               ↓
┌─────────────────────────────────────────────┐
│  MCP Bridge Layer (다리 역할)                 │
│  "도구 호출 요청을 MCP 규격으로 변환"            │
└──────────────┬──────────────────────────────┘
               ↓
┌─────────────────────────────────────────────┐
│  MCP 서버들 (외부 도구)                        │
│  웹 검색 │ 코드 실행 │ DB 접근 │ 문서 파싱 │ ...│
└─────────────────────────────────────────────┘
```

### 핵심 원칙 (LOCK — 변경 불가)

> **[LOCK] VAMOS는 MCP를 외부 도구 연결의 단일 표준으로 확정한다.**
> - 모든 외부 도구 호출은 예외 없이 MCP → ToolRegistry 경로를 사용 [근거: D2.0-03 §6.4.1]
> - LangChain Tool, CrewAI Tools, 자체 API 직접 연동 → 전부 MCP 래핑으로 대체
> - 기존 비MCP 도구도 MCP 래퍼를 통해 등록 (BaseTool 직접 사용 금지)

**핵심 요약 (3줄)**
1. MCP는 Anthropic이 만든 AI↔도구 연결 공개 표준으로, USB 포트처럼 어떤 도구든 표준 규격으로 연결합니다.
2. VAMOS는 MCP를 **유일한** 도구 연결 표준으로 확정(LOCK)하여, 모든 외부 도구는 MCP를 통해서만 접근합니다.
3. MCP Bridge Layer가 ORANGE CORE와 실제 MCP 서버 사이에서 다리 역할을 합니다.

---

## §31.2 Streamable HTTP Transport — 변경 불가 (LOCK)

### 비유: 편지 vs 전화 vs 영상통화

> 도구와 통신하는 방식에도 여러 가지가 있습니다. 편지(stdio)는 간단하지만 느리고, 전화(WebSocket)는 실시간이지만 복잡하고, 영상통화(Streamable HTTP)는 실시간이면서도 표준적입니다. VAMOS는 "영상통화" 방식을 선택했습니다.

### 전송 방식 비교

| 전송 방식 | 비유 | 장점 | 단점 | VAMOS 용도 |
|----------|------|------|------|-----------|
| **stdio** | 편지 | 간단, 로컬에서 빠름 | 원격 불가 | V1 개발/테스트 전용 |
| **SSE (구)** | 라디오 | 단방향 스트리밍 | 양방향 불가 | ❌ **Deprecated (사용 금지)** |
| **Streamable HTTP** | 영상통화 | 양방향 + 표준 HTTP | - | ✅ **프로덕션 기본 (LOCK)** |
| **WebSocket** | 전화 | 완전 양방향 실시간 | 복잡 | V3 실시간 전용 |

[근거: D2.0-03 §4.4, DEC-017]

### 왜 Streamable HTTP인가? (DEC-017 — LOCK — 변경 불가)

> **결정 완료 (DEC-017 LOCK)**: VAMOS의 MCP 전송 계층은 **Streamable HTTP**를 기본값으로 확정합니다.

선택 이유:
1. **표준 HTTP 프로토콜** 기반 — 방화벽, 프록시, 로드 밸런서와 호환
2. **실시간 스트리밍** 지원 — 긴 작업(코드 생성, 문서 분석)의 중간 결과를 실시간 수신
3. **프로덕션 환경 적합** — 안정적인 연결 관리, TLS 보안 지원
4. **양방향 통신** — 요청과 응답을 동시에 주고받을 수 있음

### config.toml 설정 (LOCK)

```toml
[mcp]
transport = "streamable_http"  # DEC-017 확정값 — 변경 불가
timeout_tool_s     = 30        # 도구 호출 기본 타임아웃 30초
timeout_stream_s   = 120       # 스트리밍 응답 120초
max_retries        = 2         # 일시적 실패 시 최대 2회 재시도
tls_required       = true      # 모든 MCP 연결 TLS 필수
auth_injection     = "07_gate" # 자격증명은 07 Gate 경유 필수
```

[근거: D2.0-03 §2.3, §4.4]

**핵심 요약 (3줄)**
1. Streamable HTTP는 표준 HTTP 기반의 양방향 스트리밍 방식으로, 모든 프로덕션 MCP 서버의 기본 전송 계층입니다 (DEC-017 LOCK).
2. SSE(구 방식)는 Deprecated되어 신규 연결에 사용 금지이며, stdio는 로컬 개발/테스트 전용입니다.
3. 도구 호출 타임아웃 30초, 스트리밍 120초, TLS 필수 등 보안/성능 설정이 LOCK으로 고정되어 있습니다.

---

## §31.3 MCP 서버/클라이언트 아키텍처

### 비유: 레스토랑의 주방과 홀

> MCP 세계에서 VAMOS는 **홀 매니저(클라이언트)** 역할입니다. 손님(사용자)의 주문을 받아서, 적절한 **주방(서버)**에 전달합니다. 중식 주방, 양식 주방, 디저트 주방이 각각 있듯이, 웹 검색 서버, 코드 실행 서버, DB 서버가 각각 있습니다.

### VAMOS = MCP 클라이언트

```
┌──────────────────────────────────────────────────────┐
│               VAMOS (MCP 클라이언트)                    │
│                                                      │
│  MCPClientManager (중앙 관리자)                        │
│  ├── Session Pool (연결 풀, 최대 동시 10개)              │
│  ├── 서버 레지스트리 (mcp_server_registry.json)         │
│  └── 핫 리로드 (설정 변경 시 재시작 없이 갱신)             │
└──────────┬───────────┬──────────┬────────────────────┘
           ↓           ↓          ↓
     ┌─────────┐ ┌─────────┐ ┌─────────┐
     │ MCP 서버 │ │ MCP 서버 │ │ MCP 서버 │
     │ (웹검색) │ │ (코드)   │ │ (DB)    │
     └─────────┘ └─────────┘ └─────────┘
```

[근거: D2.0-03 §K-002, §6.7.1]

### VAMOS가 접속하는 외부 MCP 서버 유형

| MCP 서버 유형 | 기능 | 예시 |
|-------------|------|------|
| 파일시스템 MCP | 로컬 파일 접근 | 문서 읽기/쓰기 |
| GitHub MCP | 리포지토리 관리 | 코드 리뷰, PR 생성 |
| Slack MCP | 팀 커뮤니케이션 | 메시지 전송 |
| PostgreSQL MCP | 데이터베이스 접근 | 데이터 조회/수정 |
| Brave Search MCP | 웹 검색 | 실시간 정보 검색 |
| Puppeteer MCP | 브라우저 자동화 | 웹 스크래핑 |
| 커스텀 MCP | 사용자 정의 | 자체 서비스 연결 |

### MCP 서버 디스커버리 (발견 방식)

| 버전 | 방식 | 설명 |
|-----|------|------|
| V1 | 로컬 설정 파일 | `mcp_servers.json`에 직접 등록 |
| V2 | 레지스트리 검색 | MCP 레지스트리에서 자동 탐색 |
| V3 | 자동 설치+설정 | 필요한 서버 자동 발견/설치/설정 |

[근거: D2.0-03 §K-002]

### 자원 관리 규칙

- 동시 MCP 세션 상한: **10개** (`max_concurrent_mcp: 10`)
- 세션 풀 TTL: **300초** (반복 연결 비용 절감)
- 미사용 세션: **60초** idle 시 자동 종료

[근거: D2.0-03 §6.7.1]

**핵심 요약 (3줄)**
1. VAMOS는 MCP 클라이언트로서, 여러 외부 MCP 서버(웹 검색, 코드 실행, DB 등)에 접속합니다.
2. MCPClientManager가 모든 MCP 세션을 중앙 관리하며, 동시 10개 세션까지 지원합니다.
3. 서버 발견 방식은 V1(수동 설정) → V2(자동 탐색) → V3(자동 설치)으로 진화합니다.

---

## §31.4 MCP 외부 서버 카탈로그 — 11개 서버

### 비유: 도구 상자의 도구 목록

> 목수에게는 톱, 망치, 드릴 등 각각의 도구가 있듯이, VAMOS에도 웹 검색, 코드 실행, 문서 파싱 등 각각의 MCP 서버가 있습니다. 아래는 VAMOS가 사용하는 11개 도구(서버) 카탈로그입니다.

### MCP 서버 카탈로그 (11개)

| # | 카탈로그 ID | 기능 | 제공자 | 배포 분류 | 위험 등급 | V1 | V2 | V3 |
|---|-----------|------|-------|----------|---------|----|----|-----|
| 1 | mcp.search.tavily | 웹 검색 | Tavily API | cloud | med | ✅ | ✅ | ✅ |
| 2 | mcp.search.serpapi | 검색엔진 API | SerpAPI | cloud | med | ✅ | ✅ | ✅ |
| 3 | mcp.code.e2b | 코드 샌드박스 실행 | E2B | cloud | high | ✅ | ✅ | ✅ |
| 4 | mcp.code.pyodide | 브라우저 Python | Pyodide | local | low | ✅ | ✅ | ✅ |
| 5 | mcp.doc.unstructured | 문서 파싱 | Unstructured.io | cloud | low | ✅ | ✅ | ✅ |
| 6 | mcp.doc.pymupdf | PDF 파싱 | PyMuPDF | local | low | ✅ | ✅ | ✅ |
| 7 | mcp.vision.clip | 이미지 분석 | CLIP | local | low | ❌ | ✅ | ✅ |
| 8 | mcp.speech.whisper | 음성→텍스트(STT) | OpenAI Whisper | cloud | low | ❌ | ✅ | ✅ |
| 9 | mcp.browser.playwright | 브라우저 제어 | Playwright | local | high | ✅ | ✅ | ✅ |
| 10 | mcp.db.postgres | DB 연동 | PostgreSQL | local | high | ✅ | ✅ | ✅ |
| 11 | mcp.realtime.websocket | 실시간 WebSocket | 자체 구현 | hybrid | med | ❌ | ✅ | ✅ |

[근거: D2.0-03 §6.4.2]

### 배포 분류 설명

| 배포 분류 | 의미 | 전송 방식 |
|----------|------|---------|
| **local** | 로컬 프로세스에서 실행 | stdio (개발/테스트 전용) |
| **cloud** | 원격 MCP 서버 | Streamable HTTP (프로덕션 기본) |
| **hybrid** | 로컬+원격 병합 | 특수 도메인용 |

[근거: D2.0-03 §6.3.2]

**핵심 요약 (3줄)**
1. VAMOS MCP 카탈로그에는 11개 외부 서버가 등록되어 있으며, 웹 검색부터 DB 연동까지 다양합니다.
2. V1에서 8개가 활성화되고, V2에서 이미지/음성/실시간 서버 3개가 추가됩니다.
3. 각 서버는 배포 분류(local/cloud/hybrid)와 위험 등급(low/med/high)으로 관리됩니다.

---

## §31.5 Dynamic Tool Registration (동적 도구 등록)

### 비유: 앱 스토어에서 앱 설치/삭제

> 스마트폰에서 앱을 설치하면 바로 쓸 수 있고, 삭제하면 사라지듯이, VAMOS에서도 MCP 도구를 실행 중에 추가하거나 제거할 수 있습니다. 프로그램을 껐다 켤 필요가 없습니다.

### 동적 도구 등록/해제 기능 (K-003)

- **플러그인 설치 시** → 자동으로 Tool 등록
- **사용자가 도구 활성화/비활성화** → 즉시 반영
- **컨텍스트 기반 필터링** → 투자 대화 시 투자 도구만 노출, 코딩 대화 시 코딩 도구만 노출
- **도구 버전 관리** → `tool_id@version` 형식으로 버전 고정 가능

### Tool 스키마 자동 생성

```python
# Python 함수 데코레이터 → JSON Schema 자동 생성
@mcp.tool
def web_search(query: str, max_results: int = 10) -> list[dict]:
    """웹 검색을 실행합니다."""
    ...
# → 자동으로 tool_id, input_schema, output_schema 생성
# → Pydantic으로 파라미터 검증
```

[근거: D2.0-03 §K-003]

### 버전별 활성 여부

| 기능 | V1 | V2 | V3 |
|------|----|----|-----|
| 수동 등록/해제 | ✅ | ✅ | ✅ |
| 플러그인 자동 등록 | ✅ | ✅ | ✅ |
| 컨텍스트 기반 필터링 | ✅ | ✅ | ✅ |
| 마켓플레이스 원클릭 설치 | ❌ | ✅ | ✅ |

**핵심 요약 (3줄)**
1. VAMOS는 런타임에 MCP 도구를 동적으로 추가/제거할 수 있어, 프로그램 재시작이 필요 없습니다.
2. Python 데코레이터로 도구를 정의하면 JSON Schema가 자동 생성되어 등록됩니다.
3. 대화 맥락에 따라 관련 도구만 자동으로 노출되는 컨텍스트 기반 필터링을 지원합니다.

---

## §31.6 MCP Resource System & Prompt Templates

### 비유: 도서관의 책(Resource)과 서식지(Prompt Template)

> Resource는 도서관의 책처럼 외부 데이터(메모리, 지식그래프, 설정 등)에 접근하는 방법입니다. Prompt Template는 서식지처럼, 자주 사용하는 질문/요청 형식을 미리 만들어 둔 것입니다.

### MCP Resource — 외부 리소스 접근 (K-004)

VAMOS는 독자적인 URI 스키마 (주소 체계)로 리소스에 접근합니다:

| URI 스키마 | 대상 | 예시 |
|-----------|------|------|
| `memory://recent` | 최근 대화 메모리 | 지난 대화 내용 조회 |
| `memory://project/{id}` | 프로젝트별 메모리 | 특정 프로젝트 맥락 |
| `kg://entities` | 지식그래프 엔티티 | 등록된 개념/인물 |
| `kg://relations` | 지식그래프 관계 | 개념 간 연결 |
| `investment://portfolio` | 포트폴리오 데이터 | 현재 보유 종목 |
| `investment://watchlist` | 관심종목 | 추적 중인 종목 |
| `config://settings` | 사용자 설정 | 개인 환경설정 |

- **리소스 구독**: 변경 시 실시간 알림 (Streamable HTTP — DEC-017 LOCK)
- **리소스 캐싱**: 자주 접근하는 리소스는 로컬 캐시에 저장

[근거: D2.0-03 §K-004]

### MCP Prompt Templates — 재사용 가능한 프롬프트 (K-005)

| 템플릿 이름 | 용도 | 변수 예시 |
|-----------|------|---------|
| code_review | 코드 리뷰 | `{language}`, `{context}` |
| investment_analysis | 투자 분석 | `{ticker}`, `{period}` |
| document_summary | 문서 요약 | `{doc_type}`, `{max_length}` |
| bug_report | 버그 리포트 | `{component}`, `{severity}` |
| daily_briefing | 일일 브리핑 | `{user_preference}` |

- 프롬프트 히스토리 추적 (버전 관리)
- CORE의 TemplateSet(I-13)과 연결하여 주입

[근거: D2.0-03 §K-005]

**핵심 요약 (3줄)**
1. MCP Resource는 `memory://`, `kg://` 등 URI 스키마로 외부 데이터(메모리, 지식그래프, 포트폴리오)에 접근합니다.
2. Prompt Template는 코드 리뷰, 투자 분석 등 자주 사용하는 요청 형식을 미리 정의해 재사용합니다.
3. 리소스 변경 시 Streamable HTTP 기반 실시간 알림을 받으며, 자주 접근하는 데이터는 캐시합니다.

---

## §31.7 MCP ↔ Blue Node Bridge

### 비유: 통역사

> Blue Node(전문가 팀)와 외부 MCP 세계 사이에 **통역사**가 있습니다. Blue Node의 기능을 MCP 규격으로 번역해서 외부에서도 쓸 수 있게 하고, 반대로 외부 MCP 도구를 Blue Node가 사용할 수 있게 번역합니다.

### Blue Node → MCP 서버로 노출 (K-010)

| Blue Node | MCP URI | 제공 도구 |
|-----------|---------|---------|
| Dev Node (개발) | `dev://tools` | 코드 실행, 테스트, 디버그 |
| Research Node (연구) | `research://tools` | 검색, 논문 분석 |
| Content Node (콘텐츠) | `content://tools` | 글쓰기, 요약 |
| Quant Node (분석) | `quant://tools` | 데이터 분석, 백테스트 |
| Trading Node (트레이딩) | `trading://tools` | 시장 데이터, 알림 |

→ 외부 MCP 클라이언트가 VAMOS Blue Node 기능을 사용 가능!

[근거: D2.0-03 §K-010]

### MCP Bridge Layer 역할 (S09-B29-003)

```
Claude Tool Use 요청
       ↓
  MCP Bridge Layer
  ├── tool_id 매핑 (어떤 도구인지 확인)
  ├── MCP 서버로 전달 (실제 실행)
  ├── 결과 검증 (output_schema 준수 여부)
  ├── 실패 시 → fallback_tool_id로 자동 전환
  └── Decision.optional_signals에 기록
       ↓
  결과 반환
```

- **상태 비저장 (Stateless)**: 요청-응답 단위로만 동작
- **멱등성 (Idempotent)**: 동일 요청은 동일 결과 보장

[근거: D2.0-03 §6.5.2]

### 버전별 활성 여부

| 기능 | V1 | V2 | V3 |
|------|----|----|-----|
| MCP Bridge Layer | ✅ | ✅ | ✅ |
| Blue Node → MCP 노출 | ❌ | ✅ (3개월) | ✅ |
| A2A ↔ MCP 브리지 | ❌ | ✅ (2개월) | ✅ |

**핵심 요약 (3줄)**
1. MCP Bridge Layer는 ORANGE CORE와 실제 MCP 서버 사이의 다리로, 도구 호출을 중계합니다.
2. V2부터 Blue Node가 MCP 서버로 노출되어, 외부에서도 VAMOS 기능을 사용할 수 있습니다.
3. Bridge Layer는 상태 비저장·멱등성 원칙을 따르며, 실패 시 자동으로 대체 도구로 전환합니다.

---

## §31.8 MCP Tool Use Optimization (도구 호출 최적화)

### 비유: 효율적인 장보기

> 마트에서 장을 볼 때, 필요한 것만 정확히 사고(도구 선택 최적화), 같은 코너의 물건은 한 번에 사고(병렬 호출), 지난주에 산 것을 또 사지 않는(캐싱) 것처럼 — MCP 도구 호출도 최적화합니다.

### 최적화 3가지 전략 (K-028)

#### 1. 도구 선택 최적화
- **관련성 점수**: 질문과 도구의 매칭 정확도 계산
- **조합 최적화**: 어떤 도구 조합이 최적인지 판단
- **순서 최적화**: 도구 호출 순서 자동 결정
- **불필요한 호출 감소**: 쓸데없는 도구 호출 방지

#### 2. 병렬 도구 호출
- **독립 도구** → 동시에 실행 (예: 웹 검색 + DB 조회)
- **의존 도구** → 순차 실행 (예: 검색 결과 → 분석)
- **결과 병합**: 여러 도구 결과를 하나로 합침

#### 3. 도구 결과 캐싱
- **동일 파라미터** → 캐시된 결과 즉시 반환 (재호출 불필요)
- **TTL 기반 무효화**: 시간 경과 시 캐시 자동 삭제
- **실시간 데이터**: 시세 등 실시간 데이터는 캐시 비활성화

[근거: D2.0-03 §K-028]

### MCP 보안 원칙 (LOCK)

| 원칙 | 설명 |
|------|------|
| 입력 검증 | 모든 도구 호출 파라미터는 ToolRegistry 스키마 검증 통과 필수 |
| 프롬프트 인젝션 방어 | 외부 도구 응답 내 악성 지시문 패턴 필터링 |
| 자격증명 격리 | API 키/토큰은 07 Gate를 통해 런타임 주입 (하드코딩 금지) |
| 최소 권한 | tool_id별 risk_class/cost_class에 따라 최소 범위만 허용 |
| 감사 로그 | 모든 외부 도구 호출을 LogEvent로 기록 |

[근거: D2.0-03 §MCP 외부 도구 보안 위협 방어 가이드]

**핵심 요약 (3줄)**
1. MCP 도구 호출은 선택 최적화, 병렬 실행, 결과 캐싱 3가지 전략으로 효율을 극대화합니다.
2. 독립적인 도구는 동시 실행하고, 의존적인 도구는 순차 실행하여 전체 응답 시간을 단축합니다.
3. 보안은 입력 검증, 인젝션 방어, 자격증명 격리, 최소 권한, 감사 로그 5겹으로 보호합니다 (LOCK).

---

---

# §32. 기술 스택 — Tech Stack

## §32.1 V1 Stack — Local MVP (로컬 최소 제품)

### 비유: 1인 작업실

> V1은 혼자서 작업하는 1인 작업실입니다. 노트북 한 대에 모든 도구가 설치되어 있고, 인터넷 없이도 기본 작업이 가능합니다. 비용은 거의 0원이고, 설치도 간단합니다.

### V1 구성 요소

| 구성 요소 | 선택 기술 | 역할 | 비용 |
|----------|---------|------|------|
| 데스크톱 앱 | **Tauri 2.0** + **React 18** | UI 프레임워크 (~30MB) | 무료 |
| 백엔드 | **Python 3.11+** | 서버 로직 | 무료 |
| 데이터베이스 | **SQLite** | 메타데이터/세션 저장 | 무료 |
| 벡터 DB | **Chroma** (임베디드) | RAG 벡터 검색 | 무료 |
| LLM (로컬) | **Ollama** + 경량 모델 | AI 추론 (3B~8B) | 무료 (HW만) |
| LLM (클라우드) | GPT-4o mini API (선택) | 고품질 추론 | 사용량 과금 |
| 임베딩 | **BGE-M3** (로컬) | 벡터 임베딩 (무료) | 무료 |
| 그래프 DB | 파일 기반 JSON 그래프 | 간이 GraphRAG | 무료 |
| 에이전트 | **LangGraph** (LOCK) | 워크플로우 엔진 | 무료 |
| 가드레일 | NeMo + Guardrails AI | 입출력 안전장치 (2-Layer) | 무료 |
| 로깅 | JSONL + SQLite | 구조화 로그 | 무료 |
| 배포 | 로컬 Windows/WSL | 단일 프로세스 실행 | 무료 |

**월 비용 상한: ₩40,000 ($30)** (LOCK — 변경 불가) [근거: D2.1-A1 §A1-7, D2.0-07 §4.1]

[근거: D2.1-A1 §A1-7 COMBO-V1-LOCAL]

**핵심 요약 (3줄)**
1. V1은 Tauri 2.0+React+Python+SQLite+Chroma+Ollama로 구성된 로컬 환경입니다.
2. 로컬 LLM(Ollama)과 로컬 임베딩(BGE-M3) 덕분에 기본 사용 시 비용이 0원입니다.
3. 월 비용 상한은 ₩40,000($30)으로 LOCK 확정되어 있습니다.

---

## §32.2 V2 Stack — Pro Server (팀 서버)

### 비유: 소규모 사무실

> V2는 팀이 함께 쓰는 사무실입니다. 서버 한 대에 Docker로 각 서비스를 분리 설치하고, 더 강력한 도구(PostgreSQL, Qdrant)를 사용합니다. 팀원이 동시에 접속할 수 있습니다.

### V2 추가/변경 요소 (V1 대비)

| 구성 요소 | V1 | V2 (변경/추가) | 이유 |
|----------|----|--------------|----|
| 배포 | 로컬 단일 프로세스 | **Docker Compose** | 서비스 격리, 재현성 |
| 데이터베이스 | SQLite | **PostgreSQL** | 동시 접속, 쿼리 성능 |
| 캐시 | 없음 | **Redis** | 세션/캐시 초고속 |
| 벡터 DB | Chroma | **Qdrant** OSS | 고성능 벡터 검색 |
| 그래프 DB | JSON 파일 | **Neo4j** Community | 본격 GraphRAG |
| LLM | Ollama + mini API | **GPT-4o mini 기본** + 일부 GPT-4o/Claude | 고품질 추론 |
| 임베딩 | BGE-M3 로컬 | **text-embedding-3-small** + BGE-M3 병행 | 품질 향상 |
| 가드레일 | 2-Layer | **4-Layer** (+LlamaGuard+Post-Delivery Audit) | 안전 강화 |
| 로깅 | JSONL+SQLite | **Postgres** + JSONL 압축 | 중앙 로그 관리 |

**월 비용 상한: ₩93,000 ($70)** (LOCK — 변경 불가) [근거: D2.1-A1 §A1-7, D2.0-07 §4.1]

[근거: D2.1-A1 §A1-7 COMBO-V2-SERVER]

**핵심 요약 (3줄)**
1. V2는 Docker Compose 기반으로 PostgreSQL, Redis, Qdrant, Neo4j를 추가하여 팀 사용을 지원합니다.
2. LLM은 GPT-4o mini를 기본으로 하되, 고난도 작업에만 GPT-4o/Claude를 사용합니다.
3. 월 비용 상한은 ₩93,000($70)으로 LOCK 확정되어 있습니다.

---

## §32.3 V3 Stack — Enterprise (운영형)

### 비유: 대형 빌딩의 데이터센터

> V3는 대기업의 데이터센터입니다. 여러 대의 서버가 Kubernetes로 자동 관리되고, 장애 시 자동 복구되며, 실시간 모니터링 대시보드가 있습니다.

### V3 추가/변경 요소 (V2 대비)

| 구성 요소 | V2 | V3 (변경/추가) | 이유 |
|----------|----|--------------|----|
| 배포 | Docker Compose | **Kubernetes** + **Helm** | 자동 스케일링, 고가용성 |
| LLM | API 기반 | **자체 vLLM** + 일부 API | GPU 서빙, 비용 절감 |
| 모니터링 | Postgres 로그 | **Grafana** + **Loki** + **Prometheus** | 실시간 시각화 |
| 벡터 DB | Qdrant OSS | **Qdrant Cloud** (매니지드) | 자동 백업/스케일링 |
| 그래프 DB | Neo4j Community | **Neo4j Aura** (매니지드) | 관리형 서비스 |
| DB | Postgres (셀프) | **매니지드 Postgres** (RDS 등) | 운영 자동화 |
| 가드레일 | 4-Layer | **4-Layer** (풀 구성) | 엔터프라이즈급 |

**월 비용 상한: ₩266,000 ($200)** (LOCK — 변경 불가) [근거: D2.1-A1 §A1-7, D2.0-07 §4.1]

[근거: D2.1-A1 §A1-7 COMBO-V3-OPS]

### 버전별 스택 비교 종합표

| 항목 | V1 (로컬) | V2 (팀 서버) | V3 (운영형) |
|------|----------|------------|-----------|
| 배포 | Windows/WSL | Docker Compose | Kubernetes |
| LLM | Ollama 로컬 | GPT-4o mini API | 자체 vLLM |
| DB | SQLite | PostgreSQL | 매니지드 Postgres |
| 벡터 | Chroma | Qdrant OSS | Qdrant Cloud |
| 그래프 | JSON 파일 | Neo4j Community | Neo4j Aura |
| 캐시 | — | Redis | Redis Cluster |
| 모니터링 | JSONL 파일 | Postgres 로그 | Grafana+Loki |
| UI | Tauri+React | Tauri+React+PWA | Tauri+React+PWA |
| 월 상한 | ₩40,000 | ₩93,000 | ₩266,000 |
| 에이전트 | LangGraph | LangGraph | LangGraph |

**핵심 요약 (3줄)**
1. V3는 Kubernetes+Helm 기반으로 자동 스케일링과 고가용성을 제공하는 운영급 환경입니다.
2. 자체 vLLM GPU 서빙으로 API 비용을 절감하고, Grafana+Loki+Prometheus로 실시간 모니터링합니다.
3. 월 비용 상한은 ₩266,000($200)이며, 모든 인프라가 매니지드 서비스로 전환됩니다.

---

## §32.4 LLM 서빙 — Ollama / vLLM / API 비교

### 비유: 집밥 vs 밀키트 vs 레스토랑

> - **Ollama** (집밥): 직접 요리. 재료비만 들고, 내 입맛대로 만들 수 있지만 실력에 한계.
> - **vLLM** (밀키트): 반조리. 재료+레시피가 세트로 와서 빠르고 맛있지만 주방 장비 필요.
> - **API** (레스토랑): 주문만 하면 OK. 최고 품질이지만 비용이 듦.

### LLM 서빙 엔진 비교

| 항목 | Ollama (로컬) | vLLM (서버) | 클라우드 API |
|------|-------------|-----------|-----------|
| 비유 | 집밥 | 밀키트 | 레스토랑 |
| 비용 | **무료** (HW만) | **중** (GPU 서버) | **사용량 과금** |
| 성능 | 보통 (3B~8B) | **높음** (70B+) | **최고** |
| GPU 필요 | CPU도 가능 | **필수** | 불필요 |
| 양자화 | GGUF (Q4~Q8) | GPTQ/AWQ | 해당 없음 |
| 스트리밍 | ✅ | ✅ | ✅ |
| 배치 처리 | ❌ | ✅ (Continuous) | ✅ (50% 할인) |
| 설정 난이도 | **쉬움** (1-click) | **어려움** | **매우 쉬움** |
| 오프라인 | ✅ | ✅ | ❌ |
| 적합 버전 | **V1** | **V3** | **V1/V2/V3** |

[근거: D2.0-04 §2.1.1]

### API 프로바이더 비교

| 프로바이더 | 모델 | 입력/1M 토큰 | 출력/1M 토큰 | 속도 | 특징 |
|----------|------|------------|------------|------|------|
| Anthropic | Claude 3.5 Sonnet | $3 | $15 | 빠름 | 코딩/분석 최고 |
| Anthropic | Claude 3.5 Haiku | $0.80 | $4 | 매우빠름 | 가성비 |
| OpenAI | GPT-4o | $2.50 | $10 | 빠름 | 범용 |
| OpenAI | GPT-4o-mini | $0.15 | $0.60 | 매우빠름 | **가성비왕** |
| Google | Gemini 2.0 Flash | $0.10 | $0.40 | 빠름 | **최저가** |
| DeepSeek | DeepSeek-V3 | $0.27 | $1.10 | 보통 | 중국발 가성비 |
| Groq | Llama 3.3 70B | $0.59 | $0.79 | **초고속** | 추론 최고속 |

[근거: D2.0-04 §2.1.3]

**핵심 요약 (3줄)**
1. V1은 Ollama(무료 로컬), V2는 클라우드 API(GPT-4o mini), V3는 자체 vLLM(GPU 서빙)이 핵심입니다.
2. 라우팅 전략: 간단한 질문→Ollama, 코딩/분석→Claude, 빠른 분류→GPT-4o-mini/Gemini Flash.
3. 모든 서빙 방식은 Brain Adapter Layer를 통해 통합되므로, 코드 변경 없이 전환 가능합니다.

---

## §32.5 Brain Adapter Layer (두뇌 어댑터)

### 비유: 만능 어댑터 플러그

> 해외여행 시 각 나라 콘센트가 다르지만, 만능 어댑터 하나면 어디든 충전할 수 있죠. Brain Adapter도 마찬가지입니다. OpenAI든, Anthropic이든, Ollama든 — 어떤 LLM이든 **하나의 표준 인터페이스**로 사용할 수 있습니다.

### Brain Adapter 구조 (LOCK)

```
ORANGE CORE (판단/라우팅)
     ↓
  "이 질문은 Claude로 보내자"
     ↓
┌──────────────────────────────┐
│  Brain Adapter Layer (표준)   │
│  BrainAdapter.invoke(query)  │
│  → BrainResponse 반환         │
└──────┬───────┬───────┬───────┘
       ↓       ↓       ↓
  ┌────────┐┌────────┐┌────────┐
  │ OpenAI ││Anthropic││ Ollama │
  │Adapter ││ Adapter ││Adapter │
  └────────┘└────────┘└────────┘
```

[근거: D2.0-04 §3.1~3.2]

### 핵심 계약 (LOCK — 변경 불가)

1. **ORANGE CORE**는 "판단/라우팅/비용결정"만 담당 — 구체 모델을 직접 호출하지 않음
2. **Adapter 뒤의 구현**은 CORE가 인식하지 않음 — `openai.ChatCompletion()` 직접 호출 금지
3. **모든 호출**은 BrainAdapter/ToolRegistry 경유

[근거: D2.0-04 §1.2.2]

### BrainResponse 표준 응답 (LOCK)

| 필드 | 타입 | 설명 |
|------|------|------|
| trace_id | str | 추적 ID |
| model_id | str | 사용된 모델명 |
| raw_output | str | 원본 응답 |
| tokens_input | int | 입력 토큰 수 |
| tokens_output | int | 출력 토큰 수 |
| cost_estimate | float | 비용 추정 |
| latency_ms | int | 응답 시간(ms) |
| cache_hit | bool | 캐시 적중 여부 |

[근거: D2.0-04 §3.3]

### Adapter 설정 (config/brains.yaml)

```yaml
brains:
  - adapter_id: ollama_local
    cost_class: free       # 로컬 무료
    qod_hint: 0.65         # 품질 힌트

  - adapter_id: openai_mini
    cost_class: low        # 저비용
    qod_hint: 0.70         # 품질 힌트

  - adapter_id: openai_gpt4o
    cost_class: high       # 고비용
    qod_hint: 0.95         # 품질 힌트

  - adapter_id: anthropic_sonnet
    cost_class: medium     # 중비용
    qod_hint: 0.90         # 품질 힌트
```

[근거: D2.0-04 §3.6]

**핵심 요약 (3줄)**
1. Brain Adapter Layer는 다양한 LLM을 하나의 표준 인터페이스(`invoke()`)로 통합합니다 (LOCK).
2. ORANGE CORE는 어떤 모델을 쓸지만 결정하고, 실제 호출은 Adapter가 담당합니다.
3. 모든 응답은 BrainResponse 표준 스키마로 통일되어, 모델 변경 시 코드 수정이 불필요합니다.

---

## §32.6 HAL — Hardware Abstraction Layer (하드웨어 추상화 계층)

### 비유: 자동차의 자동 변속기

> 수동 변속기는 운전자가 직접 기어를 바꾸지만, 자동 변속기는 속도와 상황에 맞게 알아서 변속합니다. HAL도 마찬가지입니다. GPU가 있으면 GPU를, CPU만 있으면 CPU를 알아서 선택합니다. 프로그래머는 "어떤 하드웨어인지" 신경 쓸 필요가 없습니다.

### HAL 원칙 (LOCK — 변경 불가)

> **목표**: 계산 자원(GPU/CPU/메모리)의 세부사항을 CORE에서 격리하고, "LLM 호출"과 "벡터/저장소 접근"만 추상화 제공.

[근거: D2.0-04 §4.1]

### 하드웨어 선택 기준 (버전별)

| 항목 | V1 (개인) | V2 (팀 서버) | V3 (운영형) |
|------|----------|------------|-----------|
| GPU | 불필요/통합 GPU | RTX 4070 수준 | A100/H100급 |
| VRAM | N/A | 16GB | 40GB 이상 |
| 주 용도 | CPU 추론, 소형 LLM | 중형 LLM, 벡터 임베딩 | 대형 모델, 고QPS 추론 |
| 선택 우선순위 | 비용 최소화 | 비용/성능 균형 | 성능/가용성 최대화 |

[근거: D2.0-04 §4.3.6.1]

### CUDA / ROCm 지원

| 런타임 | NVIDIA CUDA | AMD ROCm | 비고 |
|--------|------------|----------|------|
| vLLM | 공식 지원 | 실험적 | CUDA 우선 권장 |
| Ollama | 공식 지원 | 공식 (ROCm 6.x+) | AMD도 사용 가능 |
| PyTorch | 공식 지원 | 공식 지원 | 호환성 사전 검증 필요 |

- 원칙: HAL은 CUDA/ROCm 선택을 추상화하며, CORE는 런타임 백엔드를 직접 참조하지 않음

[근거: D2.0-04 §4.3.6.4]

**핵심 요약 (3줄)**
1. HAL은 GPU/CPU 차이를 추상화하여, CORE가 하드웨어 세부사항을 모르게 합니다 (LOCK).
2. V1은 CPU만으로도 동작하고, V2는 중급 GPU, V3는 서버급 GPU를 사용합니다.
3. NVIDIA CUDA와 AMD ROCm 모두 지원하며, HAL이 자동으로 최적 백엔드를 선택합니다.

---

## §32.7 프레임워크 결정 — LangGraph (LOCK — 변경 불가)

### 비유: 게임의 규칙 엔진

> 보드게임에는 "이 칸에 오면 이쪽으로 이동" 같은 규칙이 있죠. LangGraph는 AI 작업의 규칙 엔진입니다. "이 상태에서는 이 단계로 이동", "조건이 맞으면 분기", "실패하면 되돌아감" 같은 **워크플로우를 그래프로 정의**합니다.

### 후보 비교 및 결정

| 후보 | 장점 | 리스크 | 상태 |
|------|------|--------|------|
| **LangGraph** | **유연한 그래프 기반, StateGraph 패턴** | **학습 곡선** | **✅ LOCK (채택)** |
| AutoGen | 멀티 에이전트 대화 | 복잡도 높음 | ❌ 비채택 |
| CrewAI | 역할 기반 에이전트 | VAMOS 아키텍처 호환성 | ❌ 비채택 |
| LlamaIndex | RAG 특화 | 전체 워크플로우 한계 | ❌ 비채택 |

[근거: D2.1-A1 §A1-9]

### 왜 LangGraph인가?

1. **StateGraph 패턴**: 상태 기반 워크플로우 그래프 → VAMOS 5단계 Pipeline과 정합
2. **Conditional Edge (조건부 분기)**: 정책/비용/위험에 따른 자동 분기
3. **Human-in-the-Loop**: 사용자 확인이 필요한 단계에서 자동 중단
4. **Checkpoint/Replay**: 체크포인트 저장 → 재현/되감기 가능
5. **VAMOS Gate 경유 의무**: LangGraph + MCP(DEC-017 LOCK) + A2A 프로토콜 연동

### LOCK 이유

> **결정 (LOCK)**: LangGraph를 VAMOS의 에이전트/워크플로우 프레임워크로 확정합니다.
> - 모든 워크플로우는 LangGraph StateGraph 기반
> - Gate 선행 의무 (07 PolicyCheck/Approval/Cost)를 깨지 않는 구조
> - trace_id 단위 추적 보장

[근거: D2.0-05 §7.3, D2.1-A1 §A1-9]

**핵심 요약 (3줄)**
1. VAMOS는 AutoGen, CrewAI, LlamaIndex를 비교한 끝에 LangGraph를 워크플로우 엔진으로 확정했습니다 (LOCK).
2. LangGraph의 StateGraph, 조건부 분기, Checkpoint/Replay 기능이 VAMOS 아키텍처와 가장 잘 맞습니다.
3. 모든 워크플로우는 LangGraph 기반이며, 07 Gate 경유 의무와 trace_id 추적이 보장됩니다.

---

## §32.8 프롬프트 캐싱 — API 비용 50~90% 절감

### 비유: 단골 카페의 "같은 거요"

> 단골 카페에서 매번 같은 주문을 하면, 바리스타가 "같은 거요?" 하고 바로 만들어주죠. 프롬프트 캐싱도 마찬가지입니다. 반복되는 시스템 프롬프트나 문서를 한 번 전송하면, 다음부터는 "같은 거"로 처리해서 비용을 크게 절감합니다.

### 캐시 가능 항목

| 항목 | 토큰 수 | 반복 빈도 |
|------|--------|---------|
| System Prompt (VAMOS Core) | ~2,000 | 매 요청 |
| Tool Definitions (MCP 스키마) | ~5,000 | 매 요청 |
| User Memory Summary | ~1,000 | 매 세션 |
| 빈번 참조 문서 | ~10,000 | 자주 |

### 프로바이더별 캐싱 할인

| 프로바이더 | 캐싱 방식 | 할인율 | TTL | 조건 |
|----------|---------|--------|-----|------|
| **Claude** (Anthropic) | Prompt Caching | **90% 할인** | 5분 | cache_control 블록 마킹 |
| **OpenAI** | Automatic Caching | **50% 할인** | 자동 | 1,024+ 토큰 prefix |
| **Gemini** (Google) | Context Caching | **75% 할인** | 설정 | 최소 32K 토큰 |

- **V1 예상 절감**: 월 API 비용의 **30~50% 절감**

[근거: D2.0-04 §2.1.4]

### 캐시 인프라 (PromptCacheManager)

- `PromptCacheManager`가 프로바이더별 캐시 전략을 추상화
- Anthropic: ephemeral cache_control 블록 마킹
- OpenAI: 1024+ 토큰 prefix 자동 캐싱
- 캐시 계층: L0(인메모리, 10분) → L1(Redis, 1시간) → miss 시 실제 호출

[근거: D2.0-04 §STEP7 R1 S7D-047]

**핵심 요약 (3줄)**
1. 프롬프트 캐싱은 반복되는 시스템 프롬프트/도구 정의를 재사용하여 API 비용을 50~90% 절감합니다.
2. Claude 90%, OpenAI 50%, Gemini 75% 할인이 적용되며, V1에서 월 30~50% 비용 절감이 예상됩니다.
3. PromptCacheManager가 프로바이더별 캐시 전략을 추상화하여 자동 관리합니다.

---

## §32.9 양자화 관리 — Q4_K_M 권장

### 비유: 사진 압축

> 고화질 사진(10MB)을 카카오톡으로 보내면 오래 걸리죠. 적당히 압축하면(2MB) 빠르게 전송되면서도 눈으로 보기에 차이가 거의 없습니다. 양자화 (Quantization)는 AI 모델을 "적당히 압축"하는 기술입니다.

### 양자화란?

**양자화 (Quantization)**는 AI 모델의 숫자 정밀도를 낮춰서 **크기를 줄이고 속도를 높이는** 기술입니다.
- 원래: 16비트(FP16) → 숫자 하나에 16비트 사용 (고정밀)
- 양자화: 4비트(Q4) → 숫자 하나에 4비트만 사용 (경량화)

### 양자화 레벨 비교

| 양자화 | 크기 감소 | 품질 손실 | RAM 필요 | 속도 | 추천 |
|--------|----------|---------|---------|------|------|
| Q2_K | 75% | **심함** | 최소 | 최고속 | ❌ 비추천 |
| **Q4_K_M** | **60%** | **미미** | **적음** | **빠름** | ✅ **가성비 추천** |
| Q5_K_M | 50% | 거의 없음 | 보통 | 보통 | ✅ 균형 추천 |
| Q6_K | 40% | 없음 | 많음 | 느림 | 고사양 |
| Q8_0 | 25% | 없음 | 많음 | 느림 | GPU 필수 |
| FP16 | 0% | 없음 | 최대 | 기준 | 서버용 |

[근거: D2.0-04 §2.1.5]

### VAMOS V1 추천: Q4_K_M

> **Q4_K_M**을 선택한 이유: 크기가 60% 줄어들면서도 품질 손실이 **미미**합니다. 7B 모델 기준 약 **4GB RAM**이면 실행 가능합니다.

- **모델 자동 선택**: 사용 가능한 RAM/VRAM을 기반으로 최적 양자화를 자동 결정
  - RAM 8GB 미만 → Q4_K_M 강제
  - RAM 16GB → Q5_K_M 또는 Q6_K
  - VRAM 24GB+ → FP16 가능

**핵심 요약 (3줄)**
1. 양자화는 AI 모델의 숫자 정밀도를 낮춰 크기와 메모리를 절감하는 기술입니다.
2. VAMOS V1은 **Q4_K_M**을 권장하며, 60% 크기 감소에 품질 손실이 미미합니다.
3. RAM/VRAM에 따라 최적 양자화 레벨을 자동 선택하는 기능이 제공됩니다.

---

## §32.10 Model Gateway — LiteLLM

### 비유: 공항의 환승 데스크

> 어느 항공사 비행기를 타든 환승 데스크 하나로 모든 항공사 연결이 가능하듯, Model Gateway는 어떤 LLM 프로바이더든 **하나의 API**로 호출할 수 있게 해줍니다.

### Model Gateway 구조

```
Client (VAMOS)
    ↓
Model Gateway (LiteLLM)
    ├── Provider Selection (어떤 프로바이더?)
    ├── Authentication (인증)
    ├── Rate Limiting (속도 제한)
    ├── Caching (캐싱)
    ├── Logging (로깅)
    ├── Cost Tracking (비용 추적)
    ├── Fallback (실패 시 대체)
    ├── Load Balancing (부하 분산)
    └── Response (응답)
```

### LiteLLM — 통합 모델 게이트웨이

```python
from litellm import completion

# 동일 API로 모든 프로바이더 호출!
response = completion(
    model="claude-3-5-sonnet-20241022",  # 또는 "gpt-4o", "ollama/qwen2.5"
    messages=[{"role": "user", "content": "Hello"}]
)
```

- **도구**: LiteLLM (무료, Python 오픈소스)
- **기능**: OpenAI 포맷으로 **100+** 모델 통합 호출
- **비용**: 오픈소스 무료 / Proxy 셀프호스팅 무료

[근거: D2.0-04 §2.1.6]

### 버전별 활성 여부

| 기능 | V1 | V2 | V3 |
|------|----|----|-----|
| Brain Adapter (직접) | ✅ | ✅ | ✅ |
| LiteLLM Gateway | ❌ | ✅ | ✅ |
| 자동 Fallback 체인 | ❌ | ✅ | ✅ |

**핵심 요약 (3줄)**
1. Model Gateway(LiteLLM)는 100+ LLM 프로바이더를 하나의 OpenAI 호환 API로 통합합니다.
2. 인증, 비용 추적, Fallback, 로드 밸런싱을 자동으로 처리하여 운영 복잡도를 줄입니다.
3. V2부터 도입되며, 오픈소스 무료로 비용 부담이 없습니다.

---

## §32.11 Batch Processing — 50% 비용 절감

### 비유: 택배 모아보내기

> 물건 하나씩 택배 보내면 건당 배송비가 드는데, 모아서 한 번에 보내면 할인받을 수 있죠. Batch Processing도 마찬가지로, 급하지 않은 요청을 모아서 한 번에 처리하면 API 비용을 **50%** 절감할 수 있습니다.

### Batch Processing 개요

| 항목 | 내용 |
|------|------|
| 대상 | 비동기 가능 요청 (문서 요약, 벡터 임베딩, 보고서 생성 등) |
| 배치 조건 | 큐 크기 ≥ 10 또는 대기 시간 ≥ 5분 |
| 배치 최대 크기 | 50건 (API rate limit 고려) |
| 우선순위 | high → 즉시 실행 / normal → 배치 대기 / low → 마지막 |
| 할인 | OpenAI Batch API: **50% 할인** (24h 내 완료) |
| | Claude Batch API: **50% 할인** (Message Batches) |
| 적합 용도 | 문서 일괄 분석, 포트폴리오 리밸런싱, 지식 베이스 업데이트 |

[근거: D2.0-04 §2.1.7, §5.2]

**핵심 요약 (3줄)**
1. Batch Processing은 급하지 않은 요청을 모아서 처리하여 API 비용을 50% 절감합니다.
2. OpenAI/Claude 모두 Batch API를 통한 50% 할인을 제공합니다.
3. 큐 크기 10건 이상 또는 대기 5분 이상이면 자동으로 배치 실행됩니다.

---

## §32.12 A/B Model Testing Framework (모델 비교 테스트)

### 비유: 블라인드 테스트

> 커피 블라인드 테스트처럼, 두 AI 모델에게 동일한 질문을 던지고 어느 모델의 답이 더 나은지 비교하는 것입니다. 충분한 테스트 후 자동으로 더 좋은 모델을 추천합니다.

### A/B 테스트 프레임워크

```
동일한 요청
    ↓
┌─────────┐    ┌─────────┐
│ 모델 A   │    │ 모델 B   │
│ (기존)   │    │ (신규)   │
└─────┬───┘    └─────┬───┘
      ↓              ↓
  결과 A          결과 B
      ↓              ↓
┌─────────────────────────┐
│ 비교 평가 (ELO 레이팅)    │
│ 정확성/속도/비용/사용자선호 │
└─────────────────────────┘
```

| 항목 | 내용 |
|------|------|
| 평가 방식 | ELO 레이팅 시스템 (Chatbot Arena 유사) |
| 자동 평가 기준 | 정확성, 응답 시간, 토큰 효율, 사용자 선호 |
| 최소 테스트 | 1,000건, 최소 7일 |
| 전환 조건 | 통계적 유의성 달성 시 자동 전환 권고 |
| 적합 버전 | V2+ |

[근거: D2.0-04 §2.1.8, P6-INF-02]

**핵심 요약 (3줄)**
1. A/B Model Testing은 새 모델 도입 시 기존 모델과 동일 요청으로 품질/속도/비용을 비교합니다.
2. ELO 레이팅 시스템으로 객관적으로 평가하고, 통계적 유의성 달성 시 자동 전환을 권고합니다.
3. 최소 1,000건/7일 테스트 후 V2부터 사용 가능합니다.

---

## §32.13 ★MoA — Mixture of Agents 실행 패턴 — GAP-3

### 비유: 3명의 의사에게 동시에 진료받기

> 아프면 의사 한 명에게만 묻는 대신, 내과·외과·한의사 3명에게 동시에 물어보고 의견을 종합하면 더 정확한 진단을 받을 수 있죠. MoA도 마찬가지로, **여러 LLM에게 동시에 질문**하고 결과를 종합하여 더 좋은 답을 만들어냅니다.

### MoA (Mixture of Agents) 정의

**MoA (Mixture of Agents, 에이전트 혼합)**는 **여러 LLM 모델을 동시에 실행**하여, 각각의 결과를 종합(집계)해서 최선의 답을 도출하는 패턴입니다.

### 실행 구조

```
┌──────────────────────────────────────────┐
│          사용자 질문                        │
└──────┬───────┬───────┬──────────────────┘
       ↓       ↓       ↓
  ┌────────┐┌────────┐┌────────┐
  │ Claude ││ GPT-4o ││ Ollama │  ← 병렬 실행
  │ 결과 A ││ 결과 B ││ 결과 C │
  └────┬───┘└────┬───┘└────┬───┘
       ↓         ↓         ↓
┌──────────────────────────────────────────┐
│          Aggregator (집계기)               │
│  - 다수결 투표                              │
│  - 품질 가중 평균                           │
│  - 또는 "최고 결과 선택"                     │
└──────────────────────────────────────────┘
       ↓
  ┌──────────┐
  │ 최종 응답  │
  └──────────┘
```

[근거: D2.0-04 §6 멀티브레인/병렬 실행 정책]

### 운영 제약 (LOCK)

| 항목 | 규칙 |
|------|------|
| 병렬 태스크 최대 | **3개** (V1/V2 기본, LOCK) |
| 외부 API 호출 | **10회/분** |
| 고비용 모델 호출 | **3회/분** |
| 초과 시 | 자동 큐잉 + 사용자 알림 |
| 비용 상한 | 병렬 실행도 비용 상한을 우회할 수 없음 |

[근거: D2.0-04 §6]

### MoA 평가 기준

- 품질 향상률: 단일 모델 대비 얼마나 나은지
- 비용 효율: 추가 비용 대비 품질 향상 비율
- 지연 시간: 가장 느린 모델의 응답 시간
- 최적 조합 탐색: 어떤 모델 조합이 최선인지

### 버전별 활성 여부

| 기능 | V1 | V2 | V3 |
|------|----|----|-----|
| 단일 모델 호출 | ✅ | ✅ | ✅ |
| MoA 기본 (2모델) | ❌ | ✅ | ✅ |
| MoA 고급 (3+모델) | ❌ | ❌ | ✅ |

**핵심 요약 (3줄)**
1. MoA는 여러 LLM을 동시에 실행하고 결과를 종합하여 단일 모델보다 더 정확한 답을 만듭니다.
2. 병렬 태스크 최대 3개(LOCK), 비용 상한 우회 불가 등 엄격한 운영 제약이 적용됩니다.
3. V2에서 2모델 기본 MoA, V3에서 3+모델 고급 MoA가 활성화됩니다.

---

## §32.14 ★Docker Sandboxing & 코드 실행 격리 — GAP-2

### 비유: 실험실의 안전 챔버

> 위험한 화학 실험은 밀폐된 안전 챔버(Safety Chamber) 안에서만 진행합니다. 폭발이 일어나도 챔버 밖은 안전하죠. Docker Sandboxing도 마찬가지로, AI가 생성한 코드를 **격리된 컨테이너 안에서만 실행**하여 호스트 시스템을 보호합니다.

### 배경

AI가 생성한 코드를 격리 없이 실행하면:
- 파일 삭제/변조 위험
- 시스템 설정 변경 위험
- 네트워크를 통한 데이터 유출 위험
- 무한 루프로 시스템 마비 위험

### Docker 샌드박스 설계 원칙 (확정)

> **확정**: VAMOS 내 모든 AI 생성 코드 실행은 **Docker 샌드박스 컨테이너** 내에서만 수행한다.

| 원칙 | 설정 | 설명 |
|------|------|------|
| 네트워크 | **기본 차단** | 허용 목록만 열림 |
| 파일시스템 | **임시 볼륨만** | 호스트 경로 직접 접근 금지 |
| 실행 시간 | **30초 제한** | I-8 Cost Gate 연동 |
| 메모리/CPU | **상한 설정** | 설정 파일로 관리 |

[근거: D2.0-02 §1.3-A]

### E-4 Code Executor 연동

| 도구 | 역할 | 배포 | 위험 등급 |
|------|------|------|---------|
| **E2B** (mcp.code.e2b) | 클라우드 코드 샌드박스 | cloud | high |
| **Pyodide** (mcp.code.pyodide) | 브라우저 Python | local | low |
| **Docker 자체** | 로컬 격리 컨테이너 | local | high |

### 실패 처리

| 실패 코드 | 원인 | 처리 |
|----------|------|------|
| SANDBOX_TIMEOUT | 30초 초과 | deny + 로그 기록 |
| SANDBOX_OOM | 메모리 초과 | deny + 로그 기록 |
| SANDBOX_POLICY_DENIED | 정책 위반 | deny + 사용자 오류 알림 |

[근거: D2.0-02 §1.3-A, CLAUDE.md]

### 버전별 활성 여부

| 기능 | V1 | V2 | V3 |
|------|----|----|-----|
| E2B 클라우드 샌드박스 | ✅ | ✅ | ✅ |
| Pyodide 브라우저 실행 | ✅ | ✅ | ✅ |
| Docker 로컬 격리 | ❌ | ✅ | ✅ |

**핵심 요약 (3줄)**
1. AI 생성 코드는 반드시 Docker 샌드박스 컨테이너 안에서만 실행하여 호스트를 보호합니다 (확정).
2. 네트워크 차단, 임시 볼륨만 마운트, 30초 실행 제한, 메모리/CPU 상한 등 4중 격리가 적용됩니다.
3. 실패 시 SANDBOX_TIMEOUT/OOM/POLICY_DENIED 코드로 분류되어 즉시 차단+로그 기록됩니다.

---

## §32.15 ★프레임워크 패턴 참조 — Runnable Protocol — GAP-18

### 비유: 레고 블록의 표준 연결부

> 레고 블록은 크기나 색깔은 달라도, **연결부(studs)**가 모두 같은 규격이라 어떤 블록이든 서로 결합됩니다. Runnable Protocol도 마찬가지로, 모든 파이프라인 단계가 **동일한 인터페이스(invoke)**를 가져서 자유롭게 연결·조합할 수 있습니다.

### Runnable Protocol이란?

**Runnable Protocol**은 LangChain에서 유래한 **파이프라인 단계의 표준 인터페이스 패턴**입니다.
- 모든 단계는 `invoke(input) → output` 형태
- 단계들을 자유롭게 연결 (체이닝) 가능
- VAMOS는 LangChain을 직접 사용하지 않고, **패턴만 참조**합니다 (DEC-002 FREEZE)

### LangChain 패턴 → VAMOS 대응

| # | LangChain 패턴 | 설명 | VAMOS 대응 |
|---|---------------|------|-----------|
| 1 | LCEL | 체인 조합 문법 | VAMOS Runnable 프로토콜(02) |
| 2 | RunnablePassthrough | 입력 패스스루 | 파이프라인 단계 스킵 로직 |
| 3 | RunnableLambda | 커스텀 함수 래핑 | Sub-agent 래퍼 |
| 4 | PromptTemplate | 프롬프트 템플릿 | §7.5 프롬프트 라이브러리 |
| 5 | OutputParser | 출력 파싱 | Pydantic 스키마 기반 파싱 |
| 6 | ChatModel | 모델 추상화 | Brain Adapter (04) |
| 7 | Retriever | 검색기 추상화 | RAG Retriever (06) |
| 8 | DocumentLoader | 문서 로더 | 인덱싱 파이프라인 (06) |

[근거: D2.0-05 §12.2.2, D2.0-02 §0.7-A]

### 핵심 원칙 (DEC-002 FREEZE — 변경 불가)

> **LangChain 의존 방식 확정 (DEC-002 FREEZE)**:
> - **허용**: LangChain의 아키텍처 개념(LCEL, RunnablePassthrough, PromptTemplate 패턴)을 참조
> - **금지**: `from langchain import *` 형태의 직접 의존성
> - **예외**: 특정 기능이 구현 난이도가 현저히 높을 경우, Adapter 계층(04)에서만 허용

[근거: D2.0-02 §0.7-A]

### 실제 의존성 (langchain-core 사용)

```
langgraph >= 0.2.60          # LangGraph StateGraph (LOCK)
langchain-core >= 0.3.25     # Runnable 인터페이스
langchain-openai >= 0.2.14   # OpenAI 통합
langchain-community >= 0.3.15 # Ollama 등 커뮤니티
langchain-anthropic >= 0.3.0  # Claude [V2+]
```

- `langchain-core`의 **Runnable 인터페이스**만 사용
- 전체 LangChain 프레임워크는 사용하지 않음

[근거: PHASE_B3_DEPENDENCIES]

**핵심 요약 (3줄)**
1. Runnable Protocol은 LangChain에서 유래한 파이프라인 표준 인터페이스로, 모든 단계를 `invoke(input)→output`으로 통일합니다.
2. VAMOS는 LangChain을 직접 사용하지 않고 패턴만 참조하되, langchain-core의 Runnable 인터페이스는 사용합니다 (DEC-002 FREEZE).
3. 8개 LangChain 패턴(LCEL, RunnablePassthrough 등)이 VAMOS 자체 구현에 매핑되어 있습니다.

---

---

# 검증 체크리스트

- [x] V1/V2/V3 스택 모두? ✅ (§32.1, §32.2, §32.3)
- [x] LLM 서빙 비교? ✅ (§32.4 — Ollama/vLLM/API 비교표)
- [x] Brain Adapter? ✅ (§32.5 — 표준 인터페이스 LOCK)
- [x] LangGraph LOCK? ✅ (§32.7 — 후보 비교 + 채택 이유)
- [x] 프롬프트 캐싱/Batch 절감? ✅ (§32.8 — 50~90%, §32.11 — 50%)
- [x] MCP 11개 서버 카탈로그? ✅ (§31.4 — 11개 서버 표)
- [x] Streamable HTTP LOCK? ✅ (§31.2 — DEC-017 LOCK)
- [x] ★MoA 실행 GAP-3? ✅ (§32.13 — 멀티모델 병렬 실행)
- [x] ★Docker Sandbox GAP-2? ✅ (§32.14 — 코드 격리 아키텍처)
- [x] ★Runnable Protocol GAP-18? ✅ (§32.15 — 8개 패턴 매핑)
- [x] 비유 설명 포함? ✅ (모든 섹션에 비유 포함)
- [x] 근거 SOT 참조 표기? ✅ (모든 섹션에 [근거:] 표기)
