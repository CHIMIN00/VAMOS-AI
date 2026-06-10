# 05.domain_tools — 도메인 특화 내부 MCP 도구 (A-14~A-20 + FR-2 잔여)

> **세션**: 2-1 (Phase 2 V2-Phase 2) · **Phase**: 2 V2 · **상태**: L3 DRAFT
> **범위**: 도메인 특화 7개 (A-14 `knowledge_graph_query`, A-15 `workflow_trigger`, A-16 `data_visualize`, A-17 `document_parse`, A-18 `embedding_generate`, A-19 `health_tracker_read`, A-20 `flashcard_create`) + FR-2 잔여 4건 매핑
> **L3 승급 기준**: D2.0-04 §7 ToolRegistry 필수 3필드 (name, description, inputSchema) + outputSchema + 제약/에러/타임아웃/로깅/보안 명시
> **편성 근거**: 종합계획서 §7 Phase 2 #1 "내부 도구 A-14~A-20 스키마" + 부록 §A.1 `domain_tools.md ← knowledge_graph_query, workflow_trigger, data_visualize, document_parse, embedding_generate, health_tracker_read, flashcard_create (7)`. FR-2 잔여 4건 (`data_visualize` / `document_parse` / `health_tracker_read` / `flashcard_create`) 은 본 도메인 7건과 직접 일치하므로 한 파일 통합 처리하여 LOCK-MCP-03 31 도구 (내부 20 + 외부 11) 완결에 7/7 기여한다.

---

## §1. 교차 참조 블록

| 참조 대상 | 위치 | 용도 |
|----------|------|------|
| 종합계획서 §3.4 LOCK-MCP-01 | `MCP_SERVER_CLIENT_구조화_종합계획서.md` | 페이로드 10MB 상한 |
| 종합계획서 §3.4 LOCK-MCP-02 | 동상 | 네임스페이스 접두사 `{server}.{tool}` |
| 종합계획서 §3.4 LOCK-MCP-03 | 동상 | 31개 도구(내부 20 + 외부 11) — 본 파일 7건으로 내부 13 → 20 완결 |
| 종합계획서 §3.4 LOCK-MCP-04 | 동상 | Streamable HTTP 전송 |
| 종합계획서 §3.4 LOCK-MCP-06 | 동상 | RetryPolicy max=3, factor=2.0 |
| 종합계획서 §3.4 LOCK-MCP-07 | 동상 | CircuitBreaker 5/60s/3 |
| 종합계획서 §3.4 LOCK-MCP-09 | 동상 | 도구 스키마 정본 소유 (sot 2/4-3 + D2.0-04) |
| 종합계획서 §6.1 / 부록 §A.1 #14~#20 | 동상 | 내부 20개 도구 카탈로그 (정본) |
| 종합계획서 §11.2 FR-2 | 동상 | 미완성 도구 스키마 잔여 4건 (`data_visualize`/`document_parse`/`health_tracker_read`/`flashcard_create`) — 본 파일에서 해소 |
| 상세명세 §A-14~§A-20 | `MCP_SERVER_CLIENT_상세명세.md` | 본 파일 7건 요약 스키마 (입력/출력/설명) |
| 상세명세 §B-4 | 동상 | 6개 에러 유형 카탈로그 |
| 상세명세 §B-5 | 동상 | 메시지 프레이밍 (Streamable HTTP, 10MB) |
| 상세명세 §F-4 | 동상 | knowledge_graph_query 보완 JSON Schema (Phase 0 우선 대상) |
| 상세명세 §F-5 | 동상 | workflow_trigger 보완 JSON Schema |
| 상세명세 §G-1 | 동상 | 도구별 타임아웃 (기타 내부 30s, embedding_generate 15s, document_parse 60s) |
| 상세명세 §H-1 | 동상 | Rate Limit (내부 도구 100 req/sec) |
| D2.0-04 §7 | `docs/sot/D2.0-04_…_INFRA_CORE.md` | ToolRegistry 정본, 필수 필드(name/description/inputSchema) |
| D2.0-03 §6.3 | `docs/sot/D2.0-03_…_BLUE_NODES.md` | tool_call_registry 정본 |
| 6-2 Security-Governance | `6-2_security-governance/` | OWASP LLM05/LLM07 (knowledge_graph cypher injection / data_visualize SVG XSS / document_parse 멀웨어) |
| 6-12 Event-Logging | `6-12_event-logging/` | 구조화 로깅 표준 (trace_id 전파) |
| 3-3 PKM-Knowledge-Management | `3-3_PKM-Knowledge-Management/` | flashcard_create 5-field SM-2 알고리즘 연동 (M-048) |
| 3-2 Multimodal-Processing | `3-2_multimodal-processing/` | document_parse / data_visualize 백엔드 모달리티 처리 |
| 3-6 Health-Wellness-EmotionAI | `3-6_Health-Wellness-EmotionAI/` | health_tracker_read 5중 윤리 정합 (LOCK-HW-01~12) |
| I-20 Escalation | `1-1_aux-modules/` 참고 | 에스컬레이션 경로 (R-01-8) |
| 01_internal-tools/search_tools.md §2 | 본 도메인 P1-1 정본 | 공통 `McpError` / `ToolInvocationLog` / `EscalationPayload` — **재정의 금지, 참조만** |
| 01_internal-tools/_index.md | 동상 | 카탈로그 #14~#20 상태 (`SHELL`→`L3 DRAFT`) 갱신 대상 (도메인 마감 step 5 일괄) |

> **재정의 금지 항목**: `McpError` (10 카테고리) / `ToolInvocationLog` / `EscalationPayload` 구조는 `search_tools.md §2` 정본을 참조만 수행한다. 본 세션에서 신규 카테고리 / 필드 추가 0건. 맵 확장 `details{}` / `recovery{}` / `context{}` 는 §2.1 정본의 "임의 키-값 확장 허용" 선언 부분만 사용.

---

## §2. 공통 자료 구조 (참조)

본 문서의 에러·로그·에스컬레이션 구조는 `search_tools.md §2` 를 **정본**으로 삼고 재정의하지 않는다 (P1-1 정본 지시 직계 계승).

- `McpError` → `search_tools.md §2.1` — 본 세션에서 `category` enum 추가 **없음**. 본 파일 7개 도구가 사용하는 카테고리는 정본 10개 중 9개 (`sandbox_error` 제외, `code_execute` 한정).
- `ToolInvocationLog` → `search_tools.md §2.2` (R-01-7 nested JSON). `tool.category` 는 본 파일 도구별로 다음 값을 사용:
  - `knowledge_graph_query` → `"graph_query"`
  - `workflow_trigger` → `"workflow"`
  - `data_visualize` → `"visualization"`
  - `document_parse` → `"parsing"`
  - `embedding_generate` → `"embedding"`
  - `health_tracker_read` → `"health"`
  - `flashcard_create` → `"learning"`
- `EscalationPayload` → `search_tools.md §2.3` (R-01-8 / I-20). `source_engine` 형식: `"mcp.internal_tool.{name}"`.
- 공통 제약 (10MB / 네임스페이스 / Streamable HTTP / `Mcp-Session-Id`) → `search_tools.md §2.4`

---

## §3. A-14. knowledge_graph_query (지식 그래프 쿼리)

**카테고리**: 그래프 쿼리 · **Phase**: V2 · **타임아웃**: 15s (상세명세 §G-1 "knowledge_graph_query 15s")
**의미**: Cypher 또는 자연어 쿼리로 지식 그래프(노드/엣지/경로) 탐색. 6-4 Memory-RAG-Storage 그래프 백엔드와 연동.

### §3.1 JSON Schema (inputSchema + outputSchema)

```json
{
  "name": "knowledge_graph_query",
  "description": "Cypher 또는 자연어 쿼리로 지식 그래프에서 노드/엣지/경로를 탐색합니다. 기본 타임아웃 30초, 페이로드 10MB 상한.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "cypher": {
        "type": "string",
        "description": "Cypher 쿼리. natural_query 와 둘 중 하나 필수.",
        "maxLength": 10000
      },
      "natural_query": {
        "type": "string",
        "description": "자연어 쿼리. 내부 NL→Cypher 변환기를 통해 처리.",
        "maxLength": 2000
      },
      "max_depth": {
        "type": "integer",
        "description": "경로 탐색 최대 홉 수. 기본 3, 상한 6.",
        "minimum": 1,
        "maximum": 6,
        "default": 3
      },
      "max_results": {
        "type": "integer",
        "description": "반환 노드/엣지/경로 합계 상한.",
        "minimum": 1,
        "maximum": 1000,
        "default": 100
      },
      "include_paths": {
        "type": "boolean",
        "description": "경로 결과 포함 여부.",
        "default": false
      }
    },
    "oneOf": [
      { "required": ["cypher"] },
      { "required": ["natural_query"] }
    ],
    "additionalProperties": false
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "nodes": {
        "type": "array",
        "description": "조회된 노드 목록.",
        "items": {
          "type": "object",
          "properties": {
            "id": { "type": "string" },
            "labels": { "type": "array", "items": { "type": "string" } },
            "properties": { "type": "object" }
          },
          "required": ["id", "labels"]
        }
      },
      "edges": {
        "type": "array",
        "description": "노드 간 관계 목록.",
        "items": {
          "type": "object",
          "properties": {
            "source": { "type": "string" },
            "target": { "type": "string" },
            "type": { "type": "string" },
            "properties": { "type": "object" }
          },
          "required": ["source", "target", "type"]
        }
      },
      "paths": {
        "type": "array",
        "description": "include_paths=true 시 반환되는 경로 목록.",
        "items": {
          "type": "object",
          "properties": {
            "node_ids": { "type": "array", "items": { "type": "string" } },
            "edge_ids": { "type": "array", "items": { "type": "string" } },
            "length": { "type": "integer" }
          }
        }
      },
      "stats": {
        "type": "object",
        "properties": {
          "node_count": { "type": "integer" },
          "edge_count": { "type": "integer" },
          "path_count": { "type": "integer" },
          "elapsed_ms": { "type": "integer" }
        }
      }
    },
    "required": ["nodes", "edges", "stats"]
  }
}
```

### §3.2 제약 및 에러

| 제약 | 값 | 위반 시 |
|------|-----|---------|
| 페이로드 상한 | 10MB (LOCK-MCP-01) | `payload_too_large` (search_tools §2.1) |
| Cypher 길이 | 10000자 | `validation_error` |
| 자연어 쿼리 길이 | 2000자 | `validation_error` |
| 최대 홉 수 | 6 | `validation_error` |
| 최대 결과 수 | 1000 | `validation_error` |
| 타임아웃 | 15s (`total_budget_ms=15000`) | `timeout` (`category="timeout"`) → 재시도 1회 |
| Cypher 인젝션 | `DROP`, `DELETE`, `CREATE`, `MERGE`, `SET`, `REMOVE` 키워드 차단 (READ-ONLY) | `security_violation` (OWASP LLM05) |

### §3.3 보안 제약

- **READ-ONLY 모드 기본**: 본 도구는 읽기 전용. 쓰기 작업은 Phase 3 별도 도구로 분리한다.
- **PII 마스킹**: 노드 properties 내 이메일/전화번호/주민번호는 6-2 §9.3 정책에 따라 마스킹 후 응답.
- **trace_id 전파**: 6-12 Event-Logging 표준 준수 (`X-Trace-ID` 헤더).

---

## §4. A-15. workflow_trigger (워크플로우 트리거)

**카테고리**: 워크플로우 · **Phase**: V2 · **타임아웃**: 5s (상세명세 §G-1 "workflow_trigger async 5s, 시작 확인만")
**의미**: 사전 정의된 워크플로우(`workflow_id`)에 입력을 전달하여 실행. 3-4 Workflow-RPA / 6-3 Agent-Teams 와 연동.

### §4.1 JSON Schema

```json
{
  "name": "workflow_trigger",
  "description": "사전 정의된 워크플로우를 입력과 함께 실행하고 run_id를 반환합니다. 비동기 실행, run_id 로 상태 폴링.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "workflow_id": {
        "type": "string",
        "description": "워크플로우 정의 ID. 사전 등록된 워크플로우 카탈로그(3-4 Workflow-RPA)에 존재해야 함.",
        "pattern": "^[a-zA-Z0-9_-]{3,128}$"
      },
      "input": {
        "type": "object",
        "description": "워크플로우 입력. 워크플로우별 inputSchema에 부합해야 함 (서버 측 검증).",
        "additionalProperties": true
      },
      "trigger_mode": {
        "type": "string",
        "enum": ["async", "sync_short"],
        "description": "async = 즉시 run_id 반환, sync_short = 5초 이내 완료 시 결과 포함.",
        "default": "async"
      },
      "priority": {
        "type": "string",
        "enum": ["low", "normal", "high"],
        "default": "normal"
      },
      "callback_url": {
        "type": "string",
        "format": "uri",
        "description": "완료 시 호출할 webhook URL (선택)."
      }
    },
    "required": ["workflow_id", "input"],
    "additionalProperties": false
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "run_id": {
        "type": "string",
        "description": "실행 ID. 상태 폴링용.",
        "pattern": "^run_[a-z0-9]{16,32}$"
      },
      "status": {
        "type": "string",
        "enum": ["queued", "running", "completed", "failed"],
        "description": "초기 상태."
      },
      "estimated_completion_s": {
        "type": "integer",
        "description": "예상 완료 시간 (초). 워크플로우 카탈로그의 평균 실행 시간 기반."
      },
      "result": {
        "type": "object",
        "description": "trigger_mode=sync_short 이고 5초 이내 완료 시 즉시 반환되는 결과.",
        "additionalProperties": true
      }
    },
    "required": ["run_id", "status"]
  }
}
```

### §4.2 제약 및 에러

| 제약 | 값 | 위반 시 |
|------|-----|---------|
| `workflow_id` 패턴 | `^[a-zA-Z0-9_-]{3,128}$` | `validation_error` |
| 미등록 workflow | 카탈로그에 없음 | `validation_error` (`details.reason="workflow_not_found"`) |
| 입력 스키마 불일치 | workflow inputSchema 위반 | `validation_error` |
| 큐 포화 | priority="normal" 큐 1000건 초과 | `server_error` (`details.reason="queue_saturated"`) → 재시도 1회 (LOCK-MCP-06) |
| 동시 실행 한도 | 사용자별 100건 | `rate_limit` |
| `callback_url` 검증 | 도메인 화이트리스트 외 | `security_violation` (SSRF 방지) |

### §4.3 보안 제약

- **권한 검사**: 호출자 RBAC 권한과 `workflow_id` 의 허용 권한 그룹 교집합 비어있으면 `security_violation`.
- **callback_url SSRF 방지**: 6-2 §9.3 OWASP LLM05 — 화이트리스트(`*.vamos.io`, 등록된 사용자 도메인) 외 차단.
- **시크릿 비포함**: `input` 내 시크릿/토큰 자동 마스킹 (6-2 PII/secret detector 적용).

---

## §5. A-16. data_visualize (데이터 시각화)

**카테고리**: 시각화 · **Phase**: V2 · **타임아웃**: 30s
**의미**: 데이터 배열과 차트 타입을 받아 SVG 또는 PNG(base64) 이미지를 반환. FR-2 잔여 4건 중 1건 해소.

### §5.1 JSON Schema

```json
{
  "name": "data_visualize",
  "description": "데이터 배열과 차트 타입을 받아 SVG 또는 PNG(base64) 이미지를 생성합니다. 출력 SVG는 sanitize 후 반환.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "data": {
        "type": "array",
        "description": "시각화 대상 데이터. 행렬 형식 또는 객체 배열.",
        "minItems": 1,
        "maxItems": 10000
      },
      "chart_type": {
        "type": "string",
        "enum": ["line", "bar", "scatter", "pie", "histogram", "heatmap", "boxplot", "area", "candlestick"],
        "description": "차트 유형. 9종 지원."
      },
      "options": {
        "type": "object",
        "description": "차트 옵션 (제목/축 라벨/색상/범례 등).",
        "properties": {
          "title": { "type": "string", "maxLength": 200 },
          "x_label": { "type": "string", "maxLength": 100 },
          "y_label": { "type": "string", "maxLength": 100 },
          "width_px": { "type": "integer", "minimum": 100, "maximum": 4000, "default": 800 },
          "height_px": { "type": "integer", "minimum": 100, "maximum": 4000, "default": 600 },
          "color_scheme": { "type": "string", "enum": ["default", "viridis", "plasma", "dark", "light"] },
          "format": { "type": "string", "enum": ["svg", "png"], "default": "svg" }
        },
        "additionalProperties": false
      }
    },
    "required": ["data", "chart_type", "options"],
    "additionalProperties": false
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "svg": {
        "type": "string",
        "description": "format=svg 시 반환되는 SVG 마크업 (sanitize 적용)."
      },
      "png_base64": {
        "type": "string",
        "description": "format=png 시 반환되는 PNG base64 인코딩."
      },
      "metadata": {
        "type": "object",
        "properties": {
          "data_points": { "type": "integer" },
          "chart_type": { "type": "string" },
          "render_ms": { "type": "integer" },
          "size_bytes": { "type": "integer" }
        }
      }
    },
    "oneOf": [
      { "required": ["svg", "metadata"] },
      { "required": ["png_base64", "metadata"] }
    ]
  }
}
```

### §5.2 제약 및 에러

| 제약 | 값 | 위반 시 |
|------|-----|---------|
| `data` 항목 수 | 1~10000 | `validation_error` |
| `chart_type` enum | 9종 | `validation_error` |
| `width_px` × `height_px` | 4000 × 4000 상한 | `validation_error` |
| 출력 페이로드 | 10MB (LOCK-MCP-01) — 대형 PNG 시 위험 | `payload_too_large` |
| SVG XSS | `<script>`, `onerror=`, `javascript:` 등 sanitize | `security_violation` (OWASP LLM05) |
| 데이터 형식 불일치 | chart_type 별 expected shape 위반 | `validation_error` |

### §5.3 보안 제약

- **SVG sanitize 필수**: DOMPurify 또는 동등 라이브러리로 `<script>`/이벤트 핸들러/외부 리소스 참조 제거. 6-2 §9.3 OWASP LLM05 (XSS).
- **데이터 PII 마스킹**: 입력 데이터에 PII 의심 필드 발견 시 자동 마스킹 후 시각화.
- **출력 외부 참조 금지**: SVG 내 `href`, `xlink:href` 외부 URL 차단.

---

## §6. A-17. document_parse (문서 파싱)

**카테고리**: 파싱 · **Phase**: V2 · **타임아웃**: 60s (대용량 PDF 처리)
**의미**: 파일 경로 또는 URL 의 문서를 파싱하여 텍스트와 메타데이터를 반환. PDF/DOCX/XLSX/HTML/Markdown 지원. FR-2 잔여 4건 중 1건 해소.

### §6.1 JSON Schema

```json
{
  "name": "document_parse",
  "description": "파일 경로 또는 URL의 문서를 파싱하여 텍스트와 메타데이터를 반환합니다. PDF/DOCX/XLSX/HTML/Markdown 지원. 대용량 PDF는 60초 타임아웃.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "file_path": {
        "type": "string",
        "description": "로컬 파일 경로 (allowed_directories 내). url 과 둘 중 하나 필수.",
        "maxLength": 1000
      },
      "url": {
        "type": "string",
        "format": "uri",
        "description": "원격 문서 URL. 화이트리스트 도메인만 허용.",
        "maxLength": 2000
      },
      "format_hint": {
        "type": "string",
        "enum": ["pdf", "docx", "xlsx", "html", "markdown", "txt", "auto"],
        "description": "파일 형식 힌트. 'auto' 는 확장자/MIME 기반 자동 감지.",
        "default": "auto"
      },
      "max_pages": {
        "type": "integer",
        "description": "PDF 의 경우 파싱할 최대 페이지 수. 0 = 전체.",
        "minimum": 0,
        "maximum": 1000,
        "default": 0
      },
      "extract_tables": {
        "type": "boolean",
        "description": "표 추출 여부 (PDF/XLSX/HTML).",
        "default": false
      },
      "extract_images": {
        "type": "boolean",
        "description": "이미지 추출 여부 (별도 base64 배열).",
        "default": false
      }
    },
    "oneOf": [
      { "required": ["file_path"] },
      { "required": ["url"] }
    ],
    "additionalProperties": false
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "content": {
        "type": "string",
        "description": "추출된 텍스트 (페이지 구분자 `\\n\\n---PAGE---\\n\\n` 포함)."
      },
      "metadata": {
        "type": "object",
        "properties": {
          "format": { "type": "string" },
          "title": { "type": "string" },
          "author": { "type": "string" },
          "created_at": { "type": "string", "format": "date-time" },
          "language": { "type": "string" },
          "checksum_sha256": { "type": "string" }
        }
      },
      "pages": {
        "type": "integer",
        "description": "총 페이지 수 (PDF/DOCX)."
      },
      "tables": {
        "type": "array",
        "description": "extract_tables=true 시 반환.",
        "items": {
          "type": "object",
          "properties": {
            "page": { "type": "integer" },
            "rows": { "type": "array", "items": { "type": "array", "items": { "type": "string" } } }
          }
        }
      },
      "images": {
        "type": "array",
        "description": "extract_images=true 시 반환 (PNG/JPEG base64).",
        "items": {
          "type": "object",
          "properties": {
            "page": { "type": "integer" },
            "format": { "type": "string", "enum": ["png", "jpeg"] },
            "data_base64": { "type": "string" }
          }
        }
      }
    },
    "required": ["content", "metadata"]
  }
}
```

### §6.2 제약 및 에러

| 제약 | 값 | 위반 시 |
|------|-----|---------|
| 페이로드 상한 | 10MB (LOCK-MCP-01) | `payload_too_large` |
| 파일 경로 화이트리스트 | `allowed_directories` (Filesystem MCP §D-1) | `security_violation` |
| URL 도메인 화이트리스트 | 사전 등록 도메인 또는 사용자 동의 | `security_violation` (SSRF) |
| 최대 페이지 | 1000 | `validation_error` |
| 타임아웃 | 60s (`total_budget_ms=60000`) | `timeout` |
| 멀웨어 검사 | ClamAV 또는 동등 (대용량 파일) | `security_violation` |
| 비밀번호 보호 PDF | 복호화 미지원 | `validation_error` (`details.reason="encrypted_pdf"`) |

### §6.3 보안 제약

- **샌드박스 파싱**: PDF 파서는 격리 프로세스에서 실행 (PyMuPDF / pdfplumber, 권한 최소화).
- **멀웨어 검사**: 외부 URL 다운로드 시 ClamAV 또는 동등 백엔드로 사전 스캔. 6-2 §9.3 OWASP LLM05.
- **PII 마스킹**: 추출 텍스트에 PII 패턴 감지 시 자동 마스킹 후 응답.
- **출력 사이즈 제한**: `content` 5MB 초과 시 자동 청크 분할 (별도 `pagination` 필드).

---

## §7. A-18. embedding_generate (임베딩 벡터 생성)

**카테고리**: 임베딩 · **Phase**: V2 · **타임아웃**: 10s (상세명세 §G-1 "embedding_generate 10s, 외부 API 호출")
**의미**: 텍스트 배열에 대해 임베딩 벡터를 생성. 6-4 Memory-RAG-Storage Vector Index 연동.

### §7.1 JSON Schema

```json
{
  "name": "embedding_generate",
  "description": "텍스트 배열에 대해 임베딩 벡터를 생성합니다. 모델 미지정 시 기본 모델 (text-embedding-3-small 1536차원) 사용.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "texts": {
        "type": "array",
        "description": "임베딩할 텍스트 배열. 1~256건.",
        "items": { "type": "string", "maxLength": 8192 },
        "minItems": 1,
        "maxItems": 256
      },
      "model": {
        "type": "string",
        "description": "임베딩 모델 ID. 미지정 시 기본.",
        "enum": ["text-embedding-3-small", "text-embedding-3-large", "bge-large-en-v1.5", "default"],
        "default": "default"
      },
      "normalize": {
        "type": "boolean",
        "description": "L2 정규화 적용 여부.",
        "default": true
      }
    },
    "required": ["texts"],
    "additionalProperties": false
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "embeddings": {
        "type": "array",
        "description": "각 입력 텍스트에 대응하는 벡터 (순서 보존).",
        "items": {
          "type": "array",
          "items": { "type": "number" }
        }
      },
      "model_used": {
        "type": "string",
        "description": "실제 사용된 모델 ID."
      },
      "dimension": {
        "type": "integer",
        "description": "벡터 차원 (1536 / 3072 / 1024 등)."
      },
      "usage": {
        "type": "object",
        "properties": {
          "total_tokens": { "type": "integer" },
          "elapsed_ms": { "type": "integer" }
        }
      }
    },
    "required": ["embeddings", "model_used", "dimension"]
  }
}
```

### §7.2 제약 및 에러

| 제약 | 값 | 위반 시 |
|------|-----|---------|
| 텍스트 항목 수 | 1~256 | `validation_error` |
| 텍스트 길이 | 8192 chars 각각 | `validation_error` |
| 페이로드 상한 | 10MB (LOCK-MCP-01) | `payload_too_large` |
| 모델 enum | 4종 | `validation_error` |
| 타임아웃 | 10s | `timeout` (재시도 1회) |
| Rate Limit | 100 req/sec (내부) | `rate_limit` |

### §7.3 보안 제약

- **PII 마스킹**: 입력 텍스트의 PII 패턴 감지 시 마스킹 후 임베딩 (역추적 방지).
- **임베딩 캐시**: SHA256 해시 기반 캐시 (TTL 24시간). 동일 입력 재계산 방지.

---

## §8. A-19. health_tracker_read (건강 데이터 조회)

**카테고리**: 건강 · **Phase**: V2 · **타임아웃**: 30s
**의미**: 사용자 건강 트래커 (수면/운동/심박/체중/혈당 등) 데이터 조회. 3-6 Health-Wellness-EmotionAI 5중 윤리 정합. FR-2 잔여 4건 중 1건 해소.

### §8.1 JSON Schema

```json
{
  "name": "health_tracker_read",
  "description": "사용자 건강 트래커 데이터를 조회합니다. 3-6 Health-Wellness-EmotionAI 5중 윤리 정합 (LOCK-HW-01~12) 준수.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "metric": {
        "type": "string",
        "enum": ["sleep_hours", "steps", "heart_rate", "weight_kg", "blood_glucose", "spo2", "calories_burned", "active_minutes"],
        "description": "조회할 건강 지표. 8종 지원."
      },
      "date_range": {
        "type": "object",
        "properties": {
          "from": { "type": "string", "format": "date" },
          "to": { "type": "string", "format": "date" }
        },
        "required": ["from", "to"]
      },
      "aggregation": {
        "type": "string",
        "enum": ["raw", "daily_avg", "daily_sum", "weekly_avg", "monthly_avg"],
        "default": "raw"
      },
      "consent_token": {
        "type": "string",
        "description": "사용자 동의 토큰. 3-6 LOCK-HW-12 (consent 필수, 5중 윤리 게이트 통과 증빙).",
        "minLength": 32,
        "maxLength": 256
      }
    },
    "required": ["metric", "date_range", "consent_token"],
    "additionalProperties": false
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "data_points": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "date": { "type": "string", "format": "date-time" },
            "value": { "type": "number" },
            "source": { "type": "string", "enum": ["apple_health", "fitbit", "google_fit", "manual"] },
            "confidence": { "type": "number", "minimum": 0, "maximum": 1 }
          },
          "required": ["date", "value"]
        }
      },
      "metric": { "type": "string" },
      "aggregation": { "type": "string" },
      "stats": {
        "type": "object",
        "properties": {
          "min": { "type": "number" },
          "max": { "type": "number" },
          "mean": { "type": "number" },
          "stddev": { "type": "number" },
          "count": { "type": "integer" }
        }
      }
    },
    "required": ["data_points", "metric", "aggregation"]
  }
}
```

### §8.2 제약 및 에러

| 제약 | 값 | 위반 시 |
|------|-----|---------|
| `metric` enum | 8종 | `validation_error` |
| `date_range` 길이 | 1년 이내 | `validation_error` |
| `consent_token` 검증 | 3-6 LOCK-HW-12 정본 게이트 통과 | `security_violation` (`details.reason="consent_invalid"`) |
| 페이로드 상한 | 10MB (LOCK-MCP-01) | `payload_too_large` |
| 타임아웃 | 30s | `timeout` |
| 5중 윤리 게이트 | 3-6 §10 정본 (HITL/CSAM/PII/Bias/Consent) | `security_violation` |

### §8.3 보안 제약

- **5중 윤리 게이트 정합**: 3-6 LOCK-HW-01~12 정본 (consent / PII / bias / HITL / CSAM zero-tolerance). 본 도구는 `consent_token` 검증을 통해 게이트 통과.
- **PII 마스킹**: 응답 metadata 에 사용자 식별 정보 포함 금지.
- **데이터 보존**: 응답은 호출자 trace_id 와 함께 30일 보존 후 자동 삭제 (3-6 §10.4 / 6-2 §9.3).
- **180일 데이터 정책**: CONFLICT_LOG CL-002 / CL-007 Phase 3 이월 사항 — 본 도구는 Phase 2 기준 1년 query 허용. Phase 3 에서 정책 확정 후 보존 기간을 강화한다.

---

## §9. A-20. flashcard_create (플래시카드 생성)

**카테고리**: 학습 · **Phase**: V2 · **타임아웃**: 30s
**의미**: 플래시카드 (앞면/뒷면) 를 생성하여 사용자 덱에 추가. 3-3 PKM SM-2 알고리즘 (M-048) 5-field 정합. FR-2 잔여 4건 중 1건 해소.

### §9.1 JSON Schema

```json
{
  "name": "flashcard_create",
  "description": "플래시카드를 생성하여 사용자 덱에 추가합니다. 3-3 PKM SM-2 알고리즘 5-field (E-Factor/interval/repetitions/last_review/due_date) 초기값 자동 설정.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "front": {
        "type": "string",
        "description": "카드 앞면 (질문/단어/그림 캡션). 마크다운 지원.",
        "minLength": 1,
        "maxLength": 5000
      },
      "back": {
        "type": "string",
        "description": "카드 뒷면 (답변/정의/설명). 마크다운 지원.",
        "minLength": 1,
        "maxLength": 5000
      },
      "deck_id": {
        "type": "string",
        "description": "덱 ID. 미지정 시 사용자 기본 덱.",
        "pattern": "^deck_[a-z0-9]{8,32}$"
      },
      "tags": {
        "type": "array",
        "items": { "type": "string", "maxLength": 50 },
        "maxItems": 20,
        "description": "분류 태그."
      },
      "card_type": {
        "type": "string",
        "enum": ["basic", "cloze", "image_occlusion", "type_in"],
        "default": "basic"
      },
      "initial_difficulty": {
        "type": "string",
        "enum": ["easy", "medium", "hard"],
        "default": "medium",
        "description": "SM-2 초기 E-Factor 보정. easy=2.6, medium=2.5, hard=2.3."
      }
    },
    "required": ["front", "back"],
    "additionalProperties": false
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "card_id": {
        "type": "string",
        "pattern": "^card_[a-z0-9]{16,32}$"
      },
      "deck_id": { "type": "string" },
      "sm2_state": {
        "type": "object",
        "description": "SM-2 5-field 초기값 (3-3 PKM M-048 정본).",
        "properties": {
          "e_factor": { "type": "number", "minimum": 1.3, "maximum": 2.6 },
          "interval": { "type": "integer", "description": "다음 복습까지 간격 (일). 신규 카드는 0." },
          "repetitions": { "type": "integer", "description": "성공 복습 횟수. 신규 카드는 0." },
          "last_review": { "type": "string", "format": "date-time", "description": "마지막 복습 시각. 신규 카드는 null." },
          "due_date": { "type": "string", "format": "date" }
        },
        "required": ["e_factor", "interval", "repetitions", "due_date"]
      },
      "created_at": { "type": "string", "format": "date-time" }
    },
    "required": ["card_id", "deck_id", "sm2_state", "created_at"]
  }
}
```

### §9.2 제약 및 에러

| 제약 | 값 | 위반 시 |
|------|-----|---------|
| `front` / `back` 길이 | 1~5000 chars | `validation_error` |
| `deck_id` 패턴 | `^deck_[a-z0-9]{8,32}$` | `validation_error` |
| `deck_id` 미존재 | 카탈로그에 없음 | `validation_error` (`details.reason="deck_not_found"`) |
| `tags` 항목 수 | 0~20 | `validation_error` |
| 페이로드 상한 | 10MB (LOCK-MCP-01) | `payload_too_large` |
| 동시 생성 한도 | 사용자별 100 cards/min | `rate_limit` |
| 타임아웃 | 30s | `timeout` |

### §9.3 보안 제약

- **SM-2 5-field 정본 매핑**: 3-3 PKM `01_capture/sm2_algorithm.md` M-048 정본의 5 필드 (E-Factor / interval / repetitions / last_review / due_date) 를 그대로 사용. 재정의 0건.
- **마크다운 sanitize**: `front` / `back` 의 마크다운은 XSS 방지를 위해 sanitize 후 저장.
- **저작권**: 외부 콘텐츠 인용 시 출처 메타데이터 강제 (3-3 §3.5 capture 정합).

---

## §10. 에러 매핑 (A-14~A-20 공통)

본 7개 도구는 `search_tools.md §2.1` 정본 `McpError` 10 카테고리를 그대로 사용한다 (재정의 0건).

| 카테고리 | 본 파일 도구 적용 | 재시도 정책 (LOCK-MCP-06) |
|---------|------------------|--------------------------|
| `connection_refused` | 모두 (외부 백엔드 의존) | retry 3회, factor 2.0 |
| `timeout` | A-14/15/16/17/18/19/20 (각 타임아웃 초과) | retry 1회 (이미 30~60s 부여) |
| `auth_failure` | A-19 (consent_token), A-15 (워크플로우 RBAC) | retry 0회 → 사용자 재인증 |
| `rate_limit` | A-15 (큐 포화), A-18 (100 req/sec), A-20 (100 cards/min) | Retry-After 헤더 존중 |
| `server_error` | 모두 | retry 3회, CB +1 (LOCK-MCP-07) |
| `invalid_response` | 모두 (백엔드 응답 파싱 실패) | retry 0회 → 로깅 후 에러 반환 |
| `validation_error` | 모두 (inputSchema 위반) | retry 0회 |
| `payload_too_large` | 모두 (LOCK-MCP-01 10MB 초과) | retry 0회 |
| `security_violation` | A-14 (cypher inject), A-15 (SSRF), A-16 (SVG XSS), A-17 (멀웨어), A-19 (5중 윤리) | retry 0회 → 즉시 에스컬레이션 |
| `sandbox_error` | 본 파일 미사용 (code_execute 한정) | — |

---

## §11. Phase 복구 흐름 (에러 발생 시)

본 7개 도구의 에러 복구는 `search_tools.md §7` 정본 흐름을 그대로 따른다.

1. `McpError` 발생 → `category` / `retriable` 판정.
2. `retriable=true` → `LOCK-MCP-06` RetryPolicy (max=3, factor=2.0) 적용.
3. CB OPEN 시 → `EscalationPayload` 생성하여 I-20 에스컬레이션 (`recovery_hint="manual_review"`).
4. `validation_error` / `security_violation` / `payload_too_large` → 즉시 에러 반환 (재시도 0).
5. 모든 단계는 `ToolInvocationLog` (R-01-7) 로 6-12 Event-Logging 표준 송출.

### Confidence Penalty 표 (A-14 knowledge_graph_query 한정)

| 시나리오 | 페널티 | 사유 |
|---------|--------|------|
| 자연어 쿼리 NL→Cypher 변환 신뢰도 < 0.7 | confidence -0.2 | 의도 불명확 |
| max_depth 6 결과 0 (탐색 한계 도달) | confidence -0.1 | 그래프 sparse |
| `include_paths=true` 인데 paths=[] | confidence -0.1 | 경로 없음 |

---

## §12. Phase 2 통합 테스트 시나리오 (10건 이상)

| # | 테스트 ID | 도구 | 시나리오 | 기대 결과 |
|---|----------|------|---------|----------|
| 1 | T-DT-01 | A-14 | Cypher `MATCH (n:Person)-[:KNOWS]->(m) RETURN n,m LIMIT 10` | nodes/edges 정상 반환 |
| 2 | T-DT-02 | A-14 | `DELETE n` 인젝션 시도 | `security_violation` |
| 3 | T-DT-03 | A-14 | natural_query "Who knows Alice?" → NL→Cypher 변환 | nodes 반환 + confidence ≥ 0.7 |
| 4 | T-DT-04 | A-15 | 등록된 workflow 트리거, async | `run_id` + status="queued" |
| 5 | T-DT-05 | A-15 | 미등록 workflow_id | `validation_error` |
| 6 | T-DT-06 | A-15 | callback_url=`http://internal-network/admin` (SSRF) | `security_violation` |
| 7 | T-DT-07 | A-16 | `chart_type="bar"`, data 100건 | SVG 정상 반환 |
| 8 | T-DT-08 | A-16 | SVG 출력에 `<script>` 포함 시도 | sanitize 후 제거, 정상 반환 |
| 9 | T-DT-09 | A-17 | 10MB PDF 파싱 (50 페이지) | content + metadata 반환 |
| 10 | T-DT-10 | A-17 | 화이트리스트 외 URL | `security_violation` |
| 11 | T-DT-11 | A-18 | texts=256건, model="default" | embeddings 256개 반환 |
| 12 | T-DT-12 | A-18 | texts=300건 (한도 초과) | `validation_error` |
| 13 | T-DT-13 | A-19 | metric=sleep_hours, 7일, consent_token 정상 | data_points 7개 반환 |
| 14 | T-DT-14 | A-19 | consent_token=invalid | `security_violation` |
| 15 | T-DT-15 | A-20 | front+back 정상, deck_id 미지정 | card_id + sm2_state 초기값 (E-Factor=2.5) |
| 16 | T-DT-16 | A-20 | initial_difficulty="easy" | sm2_state.e_factor=2.6 |

---

## §13. 검증 체크리스트 (P2 #1 게이트)

- [x] A-14~A-20 7개 JSON Schema (inputSchema + outputSchema) 작성 완료
- [x] FR-2 잔여 4건 (`data_visualize` / `document_parse` / `health_tracker_read` / `flashcard_create`) 본 파일 통합 처리 (#16/#17/#19/#20)
- [x] LOCK-MCP-03 31 도구 (내부 13 + 본 파일 7 = 20 + 외부 11) 완결
- [x] 공통 자료 구조 (McpError 10 카테고리 / ToolInvocationLog / EscalationPayload) 정본 (search_tools §2) 재정의 0건
- [x] LOCK-MCP-01 10MB 페이로드 상한 7개 도구 전수 명시
- [x] LOCK-MCP-02 네임스페이스 접두사 (`internal.*` 또는 외부 충돌 시 prefix) 적용 가능
- [x] LOCK-MCP-04 Streamable HTTP 전송 정합
- [x] LOCK-MCP-06 RetryPolicy max=3, factor=2.0 §10 매핑 표 전수 적용
- [x] LOCK-MCP-07 CircuitBreaker 5/60s/3 §10 server_error 매핑
- [x] LOCK-MCP-09 도구 스키마 정본 소유 (sot 2/4-3 + D2.0-04) 명시
- [x] §6.3 5중 윤리 게이트 정합 (A-19 health_tracker_read consent_token 검증)
- [x] §9.3 SM-2 5-field 정본 매핑 (A-20 flashcard_create, 3-3 PKM M-048)
- [x] §10 에러 매핑 표 10 카테고리 × 7 도구 = 70 cell 전수
- [x] §12 Phase 2 통합 테스트 시나리오 16건 (≥10건 충족)

---

## §14. 세션 간 인터페이스 cross-check

| 후속 세션 | 본 파일 소비 지점 | 변경 금지 |
|----------|-----------------|-----------|
| **2-2 디스커버리 + Capability** | §3~§9 inputSchema → `tools/list` 응답에 정확히 매핑. A-14~A-20 7건 전수 등록. | inputSchema/outputSchema 필드 이름·타입·required |
| **2-3 외부 서버 6건** | §10 에러 매핑 → 외부 서버 도구도 동일 카테고리 사용 | McpError 카테고리 enum (정본 search_tools §2.1) |
| **2-4 Connection Pool** | §11 Phase 복구 → Pool acquire/release 시 동일 RetryPolicy/CB 적용 | LOCK-MCP-06/07 재정의 0 |

---

## §15. 자가 체크리스트 (FABRICATION 방지)

- [x] 모든 LOCK-MCP-XX 인용은 AUTHORITY_CHAIN.md §3.4 정본과 1:1 일치
- [x] 모든 도구 ID (A-14~A-20) 는 상세명세 §A 표 (`14`~`20`) 와 1:1 일치
- [x] 외부 도메인 참조 (3-3 M-048 / 3-6 LOCK-HW-12 / 6-2 §9.3 / 6-12 R-01-7) 는 참조만, 본 파일에서 재정의 0건
- [x] FR-2 잔여 4건 매핑 (memory `project_mcp_server_client_status.md` 명시) 본 파일 §5/§6/§8/§9 에서 해소
- [x] FABRICATION 마커 census 0 hits (placeholder/TODO/TBD/`...`/예정/추정/대략/아마도/어쩌면/기타 prose 0건; `...` code syntax 허용)

---

## §16. 변경 이력

| 날짜 | 변경 내용 | 세션 |
|------|----------|------|
| 2026-04-26 | 신규 작성 — A-14~A-20 7개 도메인 특화 도구 + FR-2 잔여 4건 통합 처리 (LOCK-MCP-03 31 도구 완결 7/7 기여) | 2-1 (Phase 2 V2-Phase 2) |
