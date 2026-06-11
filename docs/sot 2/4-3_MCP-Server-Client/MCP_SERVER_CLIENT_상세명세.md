# 4-3. MCP Server/Client 상세명세

> **Tier**: 4 - Infrastructure
> **Part2 상태**: PARTIAL (7+11 items, tool schemas missing)
> **SOT 근거**: PHASE_B1, D2.0-04
> **Part2 위치**: V1-Phase 1 MCP 섹션, V1-Phase 4 외부 연동

---

## 개요

VAMOS AI의 MCP(Model Context Protocol) 서버/클라이언트 인프라. Part2에는 내부 도구 7개, 외부 MCP 서버 11개가 이름만 나열되어 있으며, 각 도구의 inputSchema/outputSchema, Bridge 구현 상세, 디스커버리 프로토콜, 서버별 연동 설정이 부재.

---

## 섹션 A: 내부 MCP 도구 (20+개)

### A-1. search (하이브리드 검색)

```json
{
  "name": "search",
  "description": "BM25 + Vector 하이브리드 검색으로 관련 정보를 찾습니다",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": { "type": "string", "description": "검색 쿼리" },
      "top_k": { "type": "integer", "default": 10, "minimum": 1, "maximum": 100 },
      "filters": {
        "type": "object",
        "properties": {
          "source": { "type": "string", "enum": ["memory", "document", "web", "all"] },
          "date_from": { "type": "string", "format": "date" },
          "date_to": { "type": "string", "format": "date" },
          "tags": { "type": "array", "items": { "type": "string" } }
        }
      },
      "search_type": { "type": "string", "enum": ["hybrid", "semantic", "keyword"], "default": "hybrid" }
    },
    "required": ["query"]
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "results": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "id": { "type": "string" },
            "content": { "type": "string" },
            "score": { "type": "number" },
            "source": { "type": "string" },
            "metadata": { "type": "object" }
          }
        }
      },
      "total_count": { "type": "integer" },
      "search_time_ms": { "type": "number" }
    }
  }
}
```

### A-2. memory_read (메모리 조회)

```json
{
  "name": "memory_read",
  "description": "L0~L3 메모리 계층에서 관련 기억을 조회합니다",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": { "type": "string" },
      "level": { "type": "string", "enum": ["L0", "L1", "L2", "L3", "all"], "default": "all" },
      "max_results": { "type": "integer", "default": 5 },
      "min_importance": { "type": "number", "minimum": 0, "maximum": 1, "default": 0.3 }
    },
    "required": ["query"]
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "memories": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "id": { "type": "string" },
            "content": { "type": "string" },
            "level": { "type": "string" },
            "importance": { "type": "number" },
            "created_at": { "type": "string", "format": "date-time" },
            "access_count": { "type": "integer" }
          }
        }
      }
    }
  }
}
```

### A-3. memory_write (메모리 저장)

```json
{
  "name": "memory_write",
  "description": "새로운 기억을 메모리 계층에 저장합니다",
  "inputSchema": {
    "type": "object",
    "properties": {
      "content": { "type": "string", "maxLength": 10000 },
      "level": { "type": "string", "enum": ["L0", "L1"], "default": "L0" },
      "tags": { "type": "array", "items": { "type": "string" }, "maxItems": 20 },
      "importance": { "type": "number", "minimum": 0, "maximum": 1 },
      "source": { "type": "string", "description": "출처 (conversation, user_explicit, agent)" }
    },
    "required": ["content"]
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "id": { "type": "string" },
      "level": { "type": "string" },
      "importance_computed": { "type": "number" }
    }
  }
}
```

### A-4. code_execute (코드 실행)

```json
{
  "name": "code_execute",
  "description": "샌드박스 환경에서 코드를 실행합니다",
  "inputSchema": {
    "type": "object",
    "properties": {
      "code": { "type": "string", "maxLength": 50000 },
      "language": { "type": "string", "enum": ["python", "javascript", "bash", "rust"] },
      "timeout_ms": { "type": "integer", "default": 30000, "maximum": 120000 },
      "env_vars": { "type": "object", "additionalProperties": { "type": "string" } }
    },
    "required": ["code", "language"]
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "stdout": { "type": "string" },
      "stderr": { "type": "string" },
      "exit_code": { "type": "integer" },
      "execution_time_ms": { "type": "number" },
      "truncated": { "type": "boolean" }
    }
  }
}
```

### A-5. file_read / A-6. file_write

| 도구 | Input 핵심 필드 | Output 핵심 필드 |
|------|----------------|-----------------|
| `file_read` | `path: str`, `encoding?: str`, `range?: {start, end}` | `content: str`, `size_bytes: int`, `mime_type: str` |
| `file_write` | `path: str`, `content: str`, `mode: "write"\|"append"` | `bytes_written: int`, `path: str` |

- 보안: `allowlist` 경로 패턴 매칭 (`~/.vamos/data/**`, 프로젝트 디렉토리)
- 차단: `..` 경로 순회, 시스템 디렉토리, 실행 파일 쓰기

### A-7~A-13. 추가 내부 도구

| # | 도구명 | 입력 요약 | 출력 요약 | 설명 |
|---|--------|----------|----------|------|
| 7 | `web_search` | `query: str, max_results: int, region?: str` | `results: [{title, url, snippet}]` | 웹 검색 (Brave/Google) |
| 8 | `calculator` | `expression: str, precision?: int` | `result: number, steps?: str[]` | 수학 연산 |
| 9 | `calendar_read` | `date_range: {from, to}, calendar_id?: str` | `events: [{title, start, end, ...}]` | 캘린더 조회 |
| 10 | `calendar_write` | `event: {title, start, end, ...}` | `event_id: str` | 일정 생성 |
| 11 | `email_send` | `to: str[], subject: str, body: str, attachments?: str[]` | `message_id: str, status: str` | 이메일 전송 |
| 12 | `image_analyze` | `image_url: str \| image_base64: str, prompt?: str` | `description: str, objects?: [], text?: str` | 이미지 분석 |
| 13 | `text_transform` | `text: str, operation: str` | `result: str` | 번역/요약/문법교정 |

### A-14~A-20. 도메인 특화 도구

| # | 도구명 | 입력 요약 | 출력 요약 | 설명 |
|---|--------|----------|----------|------|
| 14 | `knowledge_graph_query` | `cypher: str \| natural_query: str` | `nodes: [], edges: [], paths?: []` | 지식 그래프 쿼리 |
| 15 | `workflow_trigger` | `workflow_id: str, input: {}` | `run_id: str` | 워크플로우 트리거 |
| 16 | `data_visualize` | `data: [], chart_type: str, options: {}` | `svg: str \| png_base64: str` | 데이터 시각화 |
| 17 | `document_parse` | `file_path: str \| url: str` | `content: str, metadata: {}, pages?: int` | 문서 파싱 (PDF, DOCX 등) |
| 18 | `embedding_generate` | `texts: str[], model?: str` | `embeddings: float[][]` | 임베딩 벡터 생성 |
| 19 | `health_tracker_read` | `metric: str, date_range: {}` | `data_points: [{date, value}]` | 건강 데이터 조회 |
| 20 | `flashcard_create` | `front: str, back: str, deck_id?: str, tags?: str[]` | `card_id: str` | 플래시카드 생성 |

---

## 섹션 B: MCP Bridge 구현

### B-1. 연결 관리

```
[VAMOS Python Engine]
    ↓ MCP Client (Streamable HTTP)
[MCP Bridge Layer]
    ↓ Connection Pool (max 10 concurrent)
[External MCP Server 1..N]
```

### B-2. 연결 프로토콜

| 단계 | 동작 | 타임아웃 |
|------|------|---------|
| 1. Discovery | 서버 URL에 `GET /mcp` 요청, capability 확인 | 5s |
| 2. Initialize | `initialize` RPC 호출, 프로토콜 버전 협상 | 10s |
| 3. Tool List | `tools/list` 호출, 사용 가능 도구 캐싱 | 5s |
| 4. Ready | 연결 풀에 등록, 상태 = connected | - |

### B-3. 재시도 로직

```python
class RetryPolicy:
    max_retries: int = 3
    base_delay_ms: int = 1000
    max_delay_ms: int = 30000
    backoff_factor: float = 2.0
    retry_on: list[int] = [408, 429, 500, 502, 503, 504]

    # Circuit breaker
    failure_threshold: int = 5        # 5회 연속 실패 시 open
    recovery_timeout_s: int = 60      # 60초 후 half-open
    success_threshold: int = 3        # 3회 연속 성공 시 close
```

### B-4. 에러 처리

| 에러 유형 | 코드 | 대응 |
|----------|------|------|
| Connection refused | -1 | 재시도 → 서버 상태 확인 → 사용자 알림 |
| Timeout | -2 | 재시도 (증가된 타임아웃) |
| Auth failure | 401/403 | 토큰 갱신 → 재시도 → 사용자에게 재인증 요청 |
| Rate limit | 429 | Retry-After 헤더 존중, 지수 백오프 |
| Server error | 5xx | 재시도 → circuit breaker → fallback |
| Invalid response | -3 | 로깅 후 에러 반환 (재시도 안 함) |

### B-5. 메시지 프레이밍

- **프로토콜**: Streamable HTTP (MCP 2025-03-26 spec)
- **Content-Type**: `application/json` (단일), `text/event-stream` (스트리밍)
- **세션 관리**: `Mcp-Session-Id` 헤더로 세션 유지
- **최대 페이로드**: 10MB (초과 시 분할)

---

## 섹션 C: 도구 디스커버리 프로토콜

### C-1. 도구 등록 흐름

```
1. 서버 연결 시 tools/list 호출
2. 각 도구의 name, description, inputSchema 캐싱
3. 내부 도구 레지스트리에 통합 등록
4. 중복 이름 시: namespace 접두사 부착 (예: github.search_issues)
5. 도구 변경 알림: tools/list_changed notification 구독
```

### C-2. 도구 검색 요청/응답

```python
# 에이전트 → Tool Registry
class ToolSearchRequest:
    query: str                    # 자연어 또는 키워드
    capabilities: list[str]       # 필요 기능 태그 ["file_io", "web"]
    max_results: int = 10
    include_external: bool = True

class ToolSearchResponse:
    tools: list[ToolInfo]         # 매칭된 도구 목록
    relevance_scores: list[float] # 관련도 점수

class ToolInfo:
    name: str
    description: str
    input_schema: dict            # JSON Schema
    server_id: str                # 소속 MCP 서버
    is_internal: bool
    avg_latency_ms: float         # 최근 평균 지연
    success_rate: float           # 최근 성공률
```

### C-3. Capability 협상

| Capability | 설명 | 필수 여부 |
|-----------|------|----------|
| `tools` | 도구 호출 지원 | 필수 |
| `resources` | 리소스 제공 | 선택 |
| `prompts` | 프롬프트 템플릿 | 선택 |
| `sampling` | LLM 샘플링 요청 | 선택 |
| `logging` | 서버 로깅 | 선택 |

---

## 섹션 D: 11개 외부 MCP 서버 연동

### D-1. Filesystem MCP Server

| 항목 | 값 |
|------|-----|
| **패키지** | `@modelcontextprotocol/server-filesystem` |
| **전송** | stdio |
| **인증** | 없음 (로컬) |
| **도구** | `read_file`, `write_file`, `list_directory`, `search_files`, `get_file_info` |
| **설정** | `allowed_directories: ["/home/user/projects", "~/.vamos/data"]` |
| **Fallback** | 내부 `file_read`/`file_write` 도구로 대체 |

### D-2. GitHub MCP Server

| 항목 | 값 |
|------|-----|
| **패키지** | `@modelcontextprotocol/server-github` |
| **전송** | stdio |
| **인증** | Personal Access Token (`GITHUB_TOKEN`) |
| **도구** | `search_repositories`, `get_file_contents`, `create_issue`, `list_issues`, `create_pull_request`, `search_code` |
| **Rate Limit** | 5000 req/hr (authenticated) |
| **Fallback** | GitHub REST API 직접 호출 |

### D-3. Slack MCP Server

| 항목 | 값 |
|------|-----|
| **패키지** | `@modelcontextprotocol/server-slack` |
| **전송** | stdio |
| **인증** | Bot Token (`SLACK_BOT_TOKEN`) + OAuth 2.0 |
| **도구** | `send_message`, `search_messages`, `list_channels`, `get_channel_history`, `add_reaction` |
| **Fallback** | Slack Web API 직접 호출 |

### D-4. Google Drive MCP Server

| 항목 | 값 |
|------|-----|
| **패키지** | `@anthropic/server-google-drive` (커뮤니티) |
| **전송** | Streamable HTTP |
| **인증** | OAuth 2.0 (Google Cloud) |
| **도구** | `search_files`, `read_file`, `create_file`, `update_file`, `share_file` |
| **Fallback** | Google Drive API v3 직접 호출 |

### D-5. Notion MCP Server

| 항목 | 값 |
|------|-----|
| **패키지** | `notion-mcp-server` |
| **전송** | stdio |
| **인증** | Internal Integration Token |
| **도구** | `search_pages`, `read_page`, `create_page`, `update_page`, `query_database`, `create_database_entry` |
| **Fallback** | Notion API 직접 호출 |

### D-6. Linear MCP Server

| 항목 | 값 |
|------|-----|
| **패키지** | `linear-mcp-server` |
| **전송** | stdio |
| **인증** | API Key |
| **도구** | `search_issues`, `create_issue`, `update_issue`, `list_projects`, `get_issue` |
| **Fallback** | Linear GraphQL API 직접 호출 |

### D-7. PostgreSQL MCP Server

| 항목 | 값 |
|------|-----|
| **패키지** | `@modelcontextprotocol/server-postgres` |
| **전송** | stdio |
| **인증** | Connection String (시크릿) |
| **도구** | `query`, `list_tables`, `describe_table` |
| **보안** | READ-ONLY 모드 기본, 명시적 허용 시만 WRITE |
| **Fallback** | SQLAlchemy 직접 연결 |

### D-8. Brave Search MCP Server

| 항목 | 값 |
|------|-----|
| **패키지** | `@modelcontextprotocol/server-brave-search` |
| **전송** | stdio |
| **인증** | Brave Search API Key |
| **도구** | `web_search`, `local_search` |
| **Rate Limit** | 2000 req/month (free), 무제한 (paid) |
| **Fallback** | 내부 `web_search` 도구 (Google CSE) |

### D-9. Puppeteer MCP Server

| 항목 | 값 |
|------|-----|
| **패키지** | `@modelcontextprotocol/server-puppeteer` |
| **전송** | stdio |
| **인증** | 없음 (로컬) |
| **도구** | `navigate`, `screenshot`, `click`, `fill`, `evaluate`, `get_content` |
| **리소스 관리** | 브라우저 인스턴스 1개, 탭 최대 5개, idle 5분 후 종료 |
| **Fallback** | Playwright 직접 실행 |

### D-10. Sentry MCP Server

| 항목 | 값 |
|------|-----|
| **패키지** | `sentry-mcp-server` (커뮤니티) |
| **전송** | Streamable HTTP |
| **인증** | Auth Token (Internal Integration) |
| **도구** | `search_issues`, `get_issue_details`, `list_events`, `get_stacktrace` |
| **Fallback** | Sentry API v0 직접 호출 |

### D-11. Exa MCP Server

| 항목 | 값 |
|------|-----|
| **패키지** | `exa-mcp-server` |
| **전송** | stdio |
| **인증** | Exa API Key |
| **도구** | `search`, `find_similar`, `get_contents` |
| **특화** | Neural search, 학술 논문/기술 문서 검색에 강점 |
| **Fallback** | Brave Search 또는 내부 `web_search` |

---

## 섹션 E: MCP 서버 관리 설정

### E-1. 글로벌 설정 (mcp_config.json)

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"],
      "enabled": true,
      "autoConnect": true
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "${secrets.GITHUB_TOKEN}" },
      "enabled": true,
      "autoConnect": false
    }
  },
  "globalSettings": {
    "maxConcurrentServers": 5,
    "defaultTimeout": 30000,
    "retryPolicy": { "maxRetries": 3, "backoffFactor": 2.0 },
    "toolNamespacing": true
  }
}
```

### E-2. 서버 라이프사이클

```
Disconnected → Connecting → Connected → Ready
                    ↓            ↓
               Failed      Disconnecting → Disconnected
                    ↓
              Reconnecting (backoff) → Connecting
```

- **AutoConnect 서버**: 앱 시작 시 자동 연결 (filesystem, brave-search 등)
- **On-demand 서버**: 도구 호출 시 연결 (puppeteer, notion 등)
- **idle 타임아웃**: 10분 미사용 시 on-demand 서버 자동 종료

---

## F. 추가 내부 도구 JSON Schema (Phase 0 우선 대상)

### F-1 file_read
```json
{
  "name": "file_read",
  "description": "파일 시스템에서 파일 내용을 읽어 반환",
  "inputSchema": {
    "type": "object",
    "required": ["path"],
    "properties": {
      "path": { "type": "string", "description": "읽을 파일의 절대 경로" },
      "encoding": { "type": "string", "default": "utf-8", "enum": ["utf-8", "base64", "binary"] },
      "offset": { "type": "integer", "minimum": 0, "description": "읽기 시작 바이트 오프셋" },
      "limit": { "type": "integer", "minimum": 1, "maximum": 10485760, "description": "최대 읽기 바이트 (기본 1MB)" }
    }
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "content": { "type": "string" },
      "size": { "type": "integer" },
      "mime_type": { "type": "string" },
      "truncated": { "type": "boolean" }
    }
  }
}
```

### F-2 file_write
```json
{
  "name": "file_write",
  "description": "파일 시스템에 내용을 기록",
  "inputSchema": {
    "type": "object",
    "required": ["path", "content"],
    "properties": {
      "path": { "type": "string" },
      "content": { "type": "string" },
      "encoding": { "type": "string", "default": "utf-8" },
      "mode": { "type": "string", "enum": ["overwrite", "append", "create_new"], "default": "overwrite" },
      "create_dirs": { "type": "boolean", "default": false }
    }
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "success": { "type": "boolean" },
      "bytes_written": { "type": "integer" },
      "path": { "type": "string" }
    }
  }
}
```

### F-3 web_search
```json
{
  "name": "web_search",
  "description": "웹 검색 수행 후 결과 반환",
  "inputSchema": {
    "type": "object",
    "required": ["query"],
    "properties": {
      "query": { "type": "string", "maxLength": 500 },
      "count": { "type": "integer", "default": 10, "minimum": 1, "maximum": 50 },
      "language": { "type": "string", "default": "ko" },
      "freshness": { "type": "string", "enum": ["day", "week", "month", "any"], "default": "any" }
    }
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "results": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "title": { "type": "string" },
            "url": { "type": "string", "format": "uri" },
            "snippet": { "type": "string" },
            "published_date": { "type": "string", "format": "date-time" }
          }
        }
      },
      "total_count": { "type": "integer" }
    }
  }
}
```

### F-4 knowledge_graph_query
```json
{
  "name": "knowledge_graph_query",
  "description": "지식 그래프에서 엔티티 및 관계 검색",
  "inputSchema": {
    "type": "object",
    "required": ["query"],
    "properties": {
      "query": { "type": "string", "description": "Cypher 또는 자연어 쿼리" },
      "query_type": { "type": "string", "enum": ["cypher", "natural_language"], "default": "natural_language" },
      "max_depth": { "type": "integer", "default": 3, "minimum": 1, "maximum": 10 },
      "limit": { "type": "integer", "default": 50 }
    }
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "nodes": { "type": "array", "items": { "type": "object", "properties": { "id": { "type": "string" }, "label": { "type": "string" }, "properties": { "type": "object" } } } },
      "edges": { "type": "array", "items": { "type": "object", "properties": { "source": { "type": "string" }, "target": { "type": "string" }, "relationship": { "type": "string" } } } }
    }
  }
}
```

### F-5 workflow_trigger
```json
{
  "name": "workflow_trigger",
  "description": "VAMOS 워크플로우를 실행하거나 특정 단계를 트리거",
  "inputSchema": {
    "type": "object",
    "required": ["workflow_id"],
    "properties": {
      "workflow_id": { "type": "string" },
      "input_data": { "type": "object" },
      "step_id": { "type": "string", "description": "특정 단계부터 시작 (선택)" },
      "async": { "type": "boolean", "default": true }
    }
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "execution_id": { "type": "string" },
      "status": { "type": "string", "enum": ["started", "queued", "completed", "failed"] },
      "result": { "type": "object" }
    }
  }
}
```

### F-6 embedding_generate
```json
{
  "name": "embedding_generate",
  "description": "텍스트를 벡터 임베딩으로 변환",
  "inputSchema": {
    "type": "object",
    "required": ["text"],
    "properties": {
      "text": { "type": "string", "maxLength": 8192 },
      "model": { "type": "string", "default": "text-embedding-3-small" },
      "dimensions": { "type": "integer", "default": 1536 }
    }
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "embedding": { "type": "array", "items": { "type": "number" } },
      "model": { "type": "string" },
      "usage": { "type": "object", "properties": { "prompt_tokens": { "type": "integer" } } }
    }
  }
}
```

---

## G. 도구 실행 타임아웃 명세

### G-1 도구별 타임아웃
| 도구 카테고리 | 기본 타임아웃 | 사유 |
|-------------|------------|------|
| search, web_search | 10s | 네트워크 의존, 빠른 응답 기대 |
| memory_read/write, file_read/write | 5s | 로컬 I/O, 지연 최소 |
| code_execute | 60s | 코드 실행 + 출력 대기 |
| knowledge_graph_query | 15s | Neo4j 쿼리 복잡도 가변 |
| workflow_trigger (async) | 5s | 시작 확인만, 완료 대기 아님 |
| embedding_generate | 10s | 외부 API 호출 |
| 기타 내부 도구 | 30s | 기본값 |
| 기타 외부 서버 도구 | 30s | 기본값 |

### G-2 타임아웃 행동
- **단일 도구**: 타임아웃 → AbortController 취소 → McpError(TIMEOUT) 반환
- **연쇄 호출**: 총 예산 120s, 도구별 예산 = min(도구 타임아웃, 잔여 예산)
- **재시도 시**: 재시도별 타임아웃 독립 (누적 아님), 단 총 예산 내

---

## H. 레이트 리밋 명세

### H-1 서버별 레이트 리밋
| 서버 | 제한 | 알고리즘 | 리셋 |
|------|------|---------|------|
| GitHub | 5,000 req/hr | X-RateLimit 헤더 파싱 | 시간당 리셋 |
| Brave Search | 2,000 req/월 (free) | 로컬 카운터 | 월초 리셋 |
| Slack | 1 msg/sec per channel | 토큰 버킷(1/s, burst 5) | 연속 |
| 내부 도구 | 100 req/sec (글로벌) | 슬라이딩 윈도우 | 연속 |

### H-2 레이트 리밋 소진 대응
1. 80% 도달 → 경고 로그 + 우선순위 낮은 요청 지연
2. 95% 도달 → 비필수 도구 호출 일시 중단
3. 100% 도달 → 대체 서버 자동 전환 (가능한 경우) 또는 큐잉 + 리셋 대기
4. 사용자 알림: "외부 도구 사용량이 한도에 도달했습니다. [시간] 후 재시도됩니다."
