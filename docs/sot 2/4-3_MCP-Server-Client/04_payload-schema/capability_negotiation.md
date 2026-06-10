# 02.capability_negotiation — MCP Capability 협상 프로토콜

> **세션**: 2-2 (Phase 2 V2-Phase 2) · **Phase**: 2 V2 · **상태**: L3 DRAFT
> **범위**: `initialize` 핸드셰이크 단계 + 클라이언트/서버 capabilities 교환 + protocolVersion 협상 (MCP 2025-03-26) + 부분 불일치 fallback + 본 파일 ↔ `tool_discovery.md` 정합
> **L3 승급 기준**: MCP 2025-03-26 initialize 메시지 정합 + LOCK-MCP-04 Streamable HTTP 전송 정합 + 5 capability (tools/resources/prompts/sampling/logging) 매핑 명시

---

## §1. 교차 참조 블록

| 참조 대상 | 위치 | 용도 |
|----------|------|------|
| 종합계획서 §3.4 LOCK-MCP-04 | `MCP_SERVER_CLIENT_구조화_종합계획서.md` | Streamable HTTP MCP 2025-03-26 spec — 본 파일 정본 |
| 종합계획서 §3.4 LOCK-MCP-01 | 동상 | 페이로드 10MB (initialize 응답 상한) |
| 종합계획서 §3.4 LOCK-MCP-03 | 동상 | 31 도구 목록 (tools capability 활성 시) |
| 상세명세 §B-5 | `MCP_SERVER_CLIENT_상세명세.md` | 메시지 프레이밍 (Mcp-Session-Id, 10MB) |
| 상세명세 §C-3 | 동상 | Capability 협상 5종 정본 |
| `connection_protocol.md §2` | `03_connection-management/` | 4단계 연결 Stage 2 Initialize 10s 타임아웃 |
| `bridge_layer.md §3` | 동상 | Streamable HTTP 클라이언트 핸드셰이크 |
| `tool_discovery.md §6.2` | 본 STEP_B 세션 2-2 파트너 | 부분 capability 불일치 fallback 흐름 |
| `01_internal-tools/search_tools.md §2.1` | 본 도메인 P1-1 정본 | `McpError` (10 카테고리) — 재정의 금지 |

---

## §2. 핸드셰이크 흐름 (4단계)

```
[Stage 1 Discovery] (5s)        — 서버 URL 에 GET /mcp, capability 사전 확인
       ↓
[Stage 2 Initialize] (10s)      — initialize JSON-RPC, protocolVersion + capabilities 교환
       ↓
[Stage 3 ToolList] (5s)         — tools/list (tool_discovery.md §3)
       ↓
[Stage 4 Ready]                 — 연결 풀 등록, 상태 = connected
```

본 파일은 **Stage 2 Initialize** 의 메시지 페이로드와 협상 규칙을 정의한다. Stage 1/3/4 는 `connection_protocol.md` 정본.

---

## §3. initialize 요청 (클라이언트 → 서버)

```json
{
  "jsonrpc": "2.0",
  "id": "boot:0",
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-03-26",
    "capabilities": {
      "roots": {
        "listChanged": false
      }
    },
    "clientInfo": {
      "name": "vamos-mcp-bridge",
      "version": "1.0.0"
    }
  }
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `params.protocolVersion` | string | ✅ | MCP 프로토콜 버전. `"2025-03-26"` (LOCK-MCP-04) |
| `params.capabilities` | object | ✅ | 클라이언트 capability 선언 |
| `params.capabilities.roots` | object | 선택 | 클라이언트 root URI 제공 (filesystem 등) |
| `params.capabilities.sampling` | object | 선택 | LLM 샘플링 요청 수신 capability |
| `params.clientInfo.name` | string | ✅ | 클라이언트 식별자 |
| `params.clientInfo.version` | string | ✅ | semver |

---

## §4. initialize 응답 (서버 → 클라이언트)

```json
{
  "jsonrpc": "2.0",
  "id": "init_1",
  "result": {
    "protocolVersion": "2025-03-26",
    "capabilities": {
      "tools": {
        "listChanged": true
      },
      "resources": {
        "subscribe": true,
        "listChanged": true
      },
      "prompts": {
        "listChanged": true
      },
      "logging": {}
    },
    "serverInfo": {
      "name": "filesystem-mcp-server",
      "version": "0.6.2"
    },
    "instructions": "Filesystem MCP server. Use read_file/write_file with allowed_directories paths."
  }
}
```

### §4.1 5 Capability 정본 (상세명세 §C-3)

| Capability | 설명 | 필수 여부 | 본 도메인 사용 |
|-----------|------|----------|--------------|
| `tools` | 도구 호출 지원 (`tools/list` + `tools/call`) | 필수 | ✅ 31 도구 (LOCK-MCP-03) |
| `resources` | 리소스 제공 (`resources/list` + `resources/read`) | 선택 | ⬜ Phase 3 (Filesystem 등 일부 서버 활성) |
| `prompts` | 프롬프트 템플릿 (`prompts/list` + `prompts/get`) | 선택 | ⬜ Phase 3 |
| `sampling` | LLM 샘플링 요청 수신 | 선택 | ⬜ Phase 3 (서버 → 클라이언트 LLM 호출) |
| `logging` | 서버 로깅 송출 | 선택 | ✅ 6-12 Event-Logging 표준 통합 |

### §4.2 Capability 매개 변수

- `tools.listChanged: bool` — `notifications/tools/list_changed` 알림 송출 여부 (`tool_discovery.md §5` 정본).
- `resources.subscribe: bool` — `resources/subscribe` 메서드 지원 여부.
- `resources.listChanged: bool` — `notifications/resources/list_changed` 알림 송출 여부.
- `prompts.listChanged: bool` — `notifications/prompts/list_changed` 알림 송출 여부.

### §4.3 부분 capability 불일치 fallback

| 시나리오 | 처리 |
|---------|------|
| 클라이언트가 `tools` 요청, 서버가 미지원 | 즉시 disconnect + `McpError(category="invalid_response", details.reason="tools_capability_required")`. `tools` 는 필수 |
| 서버가 `resources` 활성, 클라이언트 미지원 | 클라이언트 측 `resources/*` 호출 비활성. 서버 알림 무시 |
| 서버가 `prompts` 활성, 클라이언트 미지원 | 동상 |
| 서버가 `sampling` 활성, 클라이언트 미지원 | 서버 측 sampling 요청 시 `McpError(category="invalid_response")` 응답 |
| protocolVersion 불일치 (예: 클라이언트 2025-03-26, 서버 2024-10) | downgrade 협상 미지원 → disconnect (`McpError(category="invalid_response", details.reason="protocol_version_mismatch")`) |

본 흐름은 `tool_discovery.md §6.2` 와 정합한다.

---

## §5. initialized 알림 (클라이언트 → 서버)

initialize 응답 수신 후 클라이언트는 **즉시** 다음 알림을 송출하여 핸드셰이크를 완료한다.

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized",
  "params": {}
}
```

- 본 알림 후 클라이언트는 Stage 3 ToolList 진행 가능.
- 알림 미송출 시 서버는 30초 후 connection close (LOCK-MCP-08 idle 10분과 별개의 핸드셰이크 단계 타임아웃).

---

## §6. 메시지 프레이밍 (LOCK-MCP-04 정합)

- **프로토콜**: Streamable HTTP (MCP 2025-03-26 spec).
- **Content-Type**: `application/json` (initialize 요청/응답은 단일 메시지).
- **세션 헤더**: 첫 initialize 요청은 `Mcp-Session-Id` 헤더 없음 → 서버가 응답 헤더에 `Mcp-Session-Id` 발급. 이후 모든 호출은 본 세션 ID 헤더 포함.
- **stdio 예외 (CLF-MCP-005 RESOLVED-DEFERRED)**: stdio 전송 서버는 initialize 메시지를 stdin/stdout NDJSON 으로 송수신. `Mcp-Session-Id` 는 stdio 단일 서브프로세스 컨텍스트에서 무관 (서브프로세스 PID 가 implicit session).

---

## §7. 에러 처리

### §7.1 에러 카테고리 (search_tools.md §2.1 정본)

| 시나리오 | 카테고리 | 재시도 (LOCK-MCP-06) |
|---------|---------|--------------------|
| Stage 2 10s 타임아웃 | `timeout` | retry 3회 (factor 2.0) |
| protocolVersion 불일치 | `invalid_response` | retry 0회 (downgrade 미지원) |
| `tools` capability 미지원 | `invalid_response` | retry 0회 |
| 인증 실패 (서버 측) | `auth_failure` | retry 0회 → 재인증 |
| Stage 1 connection refused | `connection_refused` | retry 3회 |
| 응답 10MB 초과 | `payload_too_large` | retry 0회 |

### §7.2 부분 실패 시 클라이언트 상태

```
[Stage 2 실패]
   → connection_refused / timeout / auth_failure → Stage 1 부터 재시작 (LOCK-MCP-06)
   → invalid_response (protocol/capability 불일치) → 영구 실패 → CB +1 (LOCK-MCP-07)
   → payload_too_large → 서버 설정 검토 필요 (관리자 알림)
```

---

## §8. 5 Capability 매트릭스 (서버별)

본 도메인 9 서버 (Phase 2 누적) 의 capability 활성 매트릭스. Phase 3 Sentry/Exa 추가 시 11 서버 완결.

| 서버 | tools | resources | prompts | sampling | logging |
|------|-------|-----------|---------|----------|---------|
| 내부 (search/code/web/analysis/domain_tools 통합) | ✅ | ⬜ | ⬜ | ⬜ | ✅ |
| Filesystem | ✅ | ✅ (allowed_directories 노출) | ⬜ | ⬜ | ✅ |
| GitHub | ✅ | ⬜ | ⬜ | ⬜ | ✅ |
| Brave Search | ✅ | ⬜ | ⬜ | ⬜ | ✅ |
| Slack | ✅ | ⬜ | ⬜ | ⬜ | ✅ |
| Notion | ✅ | ✅ (페이지 노출) | ⬜ | ⬜ | ✅ |
| Linear | ✅ | ⬜ | ⬜ | ⬜ | ✅ |
| Google Drive | ✅ | ✅ (파일 노출) | ⬜ | ⬜ | ✅ |
| PostgreSQL | ✅ | ✅ (테이블 노출, READ-ONLY) | ⬜ | ⬜ | ✅ |
| Puppeteer | ✅ | ⬜ | ⬜ | ⬜ | ✅ |

> Phase 3 추가 대상: Sentry / Exa (11 서버 완결).

---

## §9. LOCK / CONFLICT 점검

### §9.1 LOCK 준수 (변경 0건)

| LOCK | 본 세션 관련 | 변경 여부 |
|------|-------------|-----------|
| LOCK-MCP-01 10MB | §6 메시지 프레이밍, §7.1 payload_too_large | 참조만 ✅ |
| LOCK-MCP-03 31 도구 | §4.1 tools capability 활성 (필수) | 참조만 ✅ |
| LOCK-MCP-04 Streamable HTTP | §3 / §4 / §6 정본 인용 | 참조만 ✅ |
| LOCK-MCP-06 RetryPolicy | §7.1 시나리오별 재시도 횟수 | 참조만 ✅ |
| LOCK-MCP-07 CircuitBreaker | §7.2 invalid_response 영구 실패 시 CB +1 | 참조만 ✅ |
| LOCK-MCP-08 idle 10분 | 본 파일은 핸드셰이크 단계, idle 타임아웃은 Stage 4 Ready 이후 적용 | 참조만 ✅ |

### §9.2 CONFLICT 후보

| 후보 | 판정 | 근거 |
|------|------|------|
| protocolVersion downgrade 미지원 | 후보 아님 | MCP 2025-03-26 spec 명시, §4.3 fallback 정의 |
| stdio 모드 Mcp-Session-Id 무관 | 후보 아님 | CLF-MCP-005 RESOLVED-DEFERRED 상속 |
| `sampling` capability 클라이언트 미지원 | 후보 아님 | §4.3 명시 처리 (서버 sampling 요청 시 invalid_response) |

`[INTERFACE_MISMATCH]` 0건 / `[LOCK_CHANGE_NEEDED]` 0건 / `[CONFLICT_CANDIDATE]` 0건.

---

## §10. Phase 2 통합 테스트 시나리오 (≥10건)

| # | 테스트 ID | 시나리오 | 기대 결과 |
|---|----------|---------|----------|
| 1 | T-CN-01 | initialize (정상) → initialized 알림 → ToolList 진입 | Stage 2 < 10s, Mcp-Session-Id 발급, capability 5 매트릭스 정합 |
| 2 | T-CN-02 | protocolVersion="2024-10-01" (구버전) | invalid_response, disconnect |
| 3 | T-CN-03 | 서버 응답에 tools capability 없음 | invalid_response (`tools_capability_required`), disconnect |
| 4 | T-CN-04 | 서버가 sampling 활성, 클라이언트 미지원 | 클라이언트는 무시, 서버 sampling 요청 시 invalid_response 응답 |
| 5 | T-CN-05 | Stage 2 10s 타임아웃 | timeout, retry 3회 후 영구 실패 |
| 6 | T-CN-06 | initialize 응답 11MB | payload_too_large, retry 0 |
| 7 | T-CN-07 | initialized 알림 미송출, 30s 경과 | 서버 측 connection close |
| 8 | T-CN-08 | tools.listChanged=true 서버 | tool_discovery.md §5 알림 구독 + TTL 6h |
| 9 | T-CN-09 | tools.listChanged=false 서버 | 알림 미구독, TTL 1h (tool_discovery.md §5.3) |
| 10 | T-CN-10 | resources.subscribe=true 서버 | resources/subscribe 가능 (Phase 3 활성) |
| 11 | T-CN-11 | logging capability 활성 서버 | 서버 로그 → 6-12 Event-Logging 통합 |
| 12 | T-CN-12 | stdio 전송 서버 | initialize 메시지 stdin/stdout NDJSON, Mcp-Session-Id 무관 |

---

## §11. 검증 체크리스트 (P2 #3 게이트)

- [x] initialize 요청/응답 메시지 MCP 2025-03-26 spec 정합 (§3 / §4)
- [x] 5 capability (tools/resources/prompts/sampling/logging) 정의 + 매트릭스 (§4.1 / §8)
- [x] capability 매개 변수 (listChanged / subscribe) 정의 (§4.2)
- [x] 부분 capability 불일치 fallback 5 시나리오 (§4.3)
- [x] initialized 알림 (§5) + 30s 타임아웃 명시 (§5)
- [x] LOCK-MCP-04 Streamable HTTP 정본 인용 (§6)
- [x] CLF-MCP-005 stdio 예외 상속 (§6)
- [x] 에러 카테고리 6 시나리오 (§7.1) + CB 영향 (§7.2)
- [x] 9 서버 capability 매트릭스 (§8) + Phase 3 11 서버 완결 명시
- [x] 공통 자료 구조 (search_tools §2) 재정의 0건
- [x] Phase 2 통합 테스트 시나리오 12건 (≥10 충족)

---

## §12. 세션 간 인터페이스 cross-check

| 후속 세션 | 본 파일 소비 지점 | 변경 금지 |
|----------|-----------------|-----------|
| **2-3 외부 서버 6건** | §8 9 서버 capability 매트릭스 → 6 신규 서버 capability 행 추가 (Slack/Notion/Linear/Drive/Postgres/Puppeteer) | capability enum 5종 (LOCK-MCP-04 정본) |
| **2-4 Connection Pool** | §2 4단계 연결 + Stage 2 Initialize 10s | Stage 진입/종료 조건 (`connection_protocol.md §3` 정본) |
| **본 파일 ↔ tool_discovery.md** | §4.3 capability 불일치 ↔ tool_discovery §6.2 부분 fallback | invalid_response 카테고리 (정본 §2.1) |

---

## §13. 자가 체크리스트 (FABRICATION 방지)

- [x] MCP 2025-03-26 spec initialize 메시지 형식은 상세명세 §B-5 / §C-3 정본 인용
- [x] 5 capability 정본 (tools/resources/prompts/sampling/logging) 은 상세명세 §C-3 표 매핑 그대로
- [x] §8 9 서버 capability 매트릭스는 development_servers.md / search_servers.md / domain_tools.md / 본 STEP_B 2-3 세션 6 서버 정본 매핑
- [x] FABRICATION 마커 census 0 hits (placeholder/TODO/TBD/`...` prose 0건)

---

## §14. 변경 이력

| 날짜 | 변경 내용 | 세션 |
|------|----------|------|
| 2026-04-26 | 신규 작성 — Capability 협상 프로토콜 (initialize 핸드셰이크 + 5 capability 매트릭스 + protocolVersion 협상 + fallback + 12 테스트) | 2-2 (Phase 2 V2-Phase 2) |
