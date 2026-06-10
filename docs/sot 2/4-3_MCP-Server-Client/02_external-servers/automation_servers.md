# 04.automation_servers — 외부 MCP 데이터·자동화 서버 (PostgreSQL, Puppeteer)

> **세션**: 2-3 (Phase 2 V2-Phase 2) · **Phase**: 2 V2 · **상태**: L3 DRAFT
> **범위**: D-7 PostgreSQL, D-9 Puppeteer 2개 외부 MCP 서버 — 패키지/전송/인증/도구/Rate Limit/Fallback/AutoConnect/RetryPolicy 오버라이드 + READ-ONLY DB 제약 + 브라우저 리소스 관리
> **L3 승급 기준**: R-16-3 (인증·Rate Limit·Fallback 3종 전수) + R-16-5 (시크릿 환경 변수) + R-16-6 (AutoConnect 구분) + LOCK-MCP-06 오버라이드 (`retry_circuit_breaker.md §13.1`) 참조 + LOCK-MCP-05 동시 서버 5 제약 정합
> **편성 근거**: 종합계획서 §7 Phase 2 #5 "PostgreSQL + Puppeteer 연동" — `02_external-servers/automation_servers.md` 신규 산출물 (plan §7.3 2-3 산출물 명세 명시)

---

## §1. 교차 참조 블록

| 참조 대상 | 위치 | 용도 |
|----------|------|------|
| 종합계획서 §3.4 LOCK-MCP-01 | `MCP_SERVER_CLIENT_구조화_종합계획서.md` | 페이로드 10MB 상한 |
| 종합계획서 §3.4 LOCK-MCP-02 | 동상 | 네임스페이스 접두사 `{server}.{tool}` |
| 종합계획서 §3.4 LOCK-MCP-03 | 동상 | 31개 도구 — 외부 11 중 본 파일 2건 |
| 종합계획서 §3.4 LOCK-MCP-04 | 동상 | Streamable HTTP — 본 파일 두 서버 stdio 예외 (CLF-MCP-005) |
| 종합계획서 §3.4 LOCK-MCP-05 | 동상 | 최대 동시 서버 5 |
| 종합계획서 §3.4 LOCK-MCP-06 | 동상 | RetryPolicy max=3, factor=2.0 |
| 종합계획서 §3.4 LOCK-MCP-07 | 동상 | CircuitBreaker 5/60s/3 |
| 종합계획서 §3.4 LOCK-MCP-08 | 동상 | idle 10분 |
| 종합계획서 §3.4 LOCK-MCP-10 | 동상 | Connection Pool 최대 10 |
| 종합계획서 §4.3 R-16-3 / R-16-5 / R-16-6 | 동상 | 외부 서버 3종 / 시크릿 / AutoConnect |
| 종합계획서 §6.1 / 부록 §A.2 #7, #9 | 동상 | 서버 카탈로그 |
| 상세명세 §D-7 | `MCP_SERVER_CLIENT_상세명세.md` | PostgreSQL 원본 (3 도구, READ-ONLY 기본) |
| 상세명세 §D-9 | 동상 | Puppeteer 원본 (6 도구, 브라우저 1개/탭 5개/idle 5분) |
| 상세명세 §E-1 / §E-2 / §H-1 | 동상 | mcp_config.json / 라이프사이클 / Rate Limit |
| `bridge_layer.md §2~§10` | `03_connection-management/` | Streamable HTTP 클라이언트 |
| `connection_protocol.md §1~§6` | 동상 | 4단계 연결 프로토콜 |
| `retry_circuit_breaker.md §2.1 / §13.1 / §14.1` | 동상 | RetryPolicy / overrides / LOCK 지점 |
| `01_internal-tools/search_tools.md §2` | `01_internal-tools/` | McpError / ToolInvocationLog / EscalationPayload (재정의 금지) |
| `02_external-servers/development_servers.md` | 본 도메인 P1-6 | 9-section 템플릿 재사용 |
| `02_external-servers/communication_servers.md` | 본 STEP_B 세션 2-3 파트너 | Slack/Drive/Notion/Linear 4건 |
| `04_payload-schema/capability_negotiation.md §8` | 본 STEP_B 세션 2-2 산출 | 9 서버 capability 매트릭스 (본 파일 2 행 추가) |
| 6-12 Event-Logging | `6-12_event-logging/` | 구조화 로깅 |
| 6-2 Security-Governance | `6-2_security-governance/` | DB 시크릿, SQL Injection 방지, Puppeteer 샌드박스 (OWASP LLM05/LLM07) |
| 3-4 Workflow-RPA | `3-4_Workflow-RPA/` | Puppeteer 자동화 워크플로우 통합 |

> **재정의 금지 항목**: `McpError` / `ToolInvocationLog` / `EscalationPayload` 정본 (`search_tools.md §2`). `RetryPolicy` `max_retries=3` / `backoff_factor=2.0` 상한 불변.

> **CLF-MCP-005 RESOLVED-DEFERRED stdio 예외 상속**: 본 파일 두 서버 모두 공식 `@modelcontextprotocol/server-*` 패키지 stdio 전송 → `development_servers.md §5.1` 선례 직접 계승 stdio 표준 유지 주석 명시.

---

## §2. D-7 PostgreSQL MCP Server

### §2.1 기본 연동 카탈로그

| 항목 | 값 | 근거 |
|------|-----|------|
| **서버 ID** | `postgres` | 상세명세 §D-7, 부록 §A.2 #7 |
| **패키지** | `@modelcontextprotocol/server-postgres` | 상세명세 §D-7 |
| **버전 핀닝** | `@modelcontextprotocol/server-postgres@latest` (W-NEW-1 V2) | §14 W-NEW-1 |
| **전송** | `stdio` (CLF-MCP-005 상속, 공식 패키지 stdio 표준) | 상세명세 §D-7 |
| **실행 명령** | `npx -y @modelcontextprotocol/server-postgres "${env.POSTGRES_CONNECTION_STRING}"` | 상세명세 §E-1 |
| **AutoConnect** | ❌ (On-demand) | R-16-6 |
| **도구 3종** | `query`, `list_tables`, `describe_table` | 상세명세 §D-7 |
| **네임스페이스** | `postgres.query` 등 (LOCK-MCP-02) | LOCK-MCP-02 |
| **capability** | `tools=true`, `resources=true` (테이블 노출 READ-ONLY), `logging=true` | capability_negotiation §8 |
| **READ-ONLY 모드** | 기본 ON, 명시 허용 시만 WRITE (`POSTGRES_ALLOW_WRITE=true` 환경 변수) | 상세명세 §D-7 (보안) |
| **Phase** | V2 | §7 Phase 2 #5 |

### §2.2 인증 (R-16-3 #1 / R-16-5)

| 항목 | 값 |
|------|-----|
| **인증 방식** | Connection String (PostgreSQL 표준 `postgres://user:pass@host:port/db?sslmode=require`) |
| **환경 변수** | `${secrets.POSTGRES_CONNECTION_STRING}` (시크릿 비저장소 관리) |
| **권한 범위** | DB user 권한에 따름 (READ-ONLY 모드 하에서는 SELECT 만 허용) |
| **신뢰 경계** | DB 단위. 다른 DB 접근은 별도 connection string 필요 |
| **TLS** | `sslmode=require` 강제 (운영 환경) |
| **시크릿 회전** | 90일 권장 (운영 런북 6-13) |

### §2.3 Rate Limit (R-16-3 #2)

| 항목 | 값 | 근거 |
|------|-----|------|
| **공식 쿼터** | 없음 (DB 자체 limit, max_connections 기반) | DB 측 정책 |
| **내부 제한** | 100 req/sec (글로벌 내부 도구 슬라이딩 윈도우) | 상세명세 §H-1 |
| **DB Connection Limit** | DB max_connections 의 5% (Bridge 측 양보) | 본 세션 정의 |
| **80% 경고** | DB connection 사용률 80% | 본 세션 정의 |
| **95% pause** | DB connection 사용률 95% → 5초 pause | 본 세션 정의 |
| **CB 영향** | rate_limit → CB 무영향 (LOCK-MCP-07 / §14.1 L10) |

### §2.4 Fallback (R-16-3 #3)

| 트리거 | Fallback 경로 |
|--------|---------------|
| **서버 연결 실패** | SQLAlchemy 직접 연결 (`psycopg2` driver) |
| **`query` 실행 실패** | 재시도 1회 후 manual_review (DB 무결성 보호) |
| **`list_tables` 실패** | 캐시된 schema (TTL 1시간) 사용 |
| **CB OPEN** | manual_review |
| **READ-ONLY 위반** (WRITE 시도) | 즉시 `security_violation` (운영 정책 차단) |

### §2.5 라이프사이클

```
[On-demand]
  → 도구 호출 시 Connecting (Stage 1~3)
  → DB Connection Pool 확보 (max 5 / Bridge)
  → idle 10분 → Disconnecting (LOCK-MCP-08, DB connection 반납)
```

### §2.6 설정 파일

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "${secrets.POSTGRES_CONNECTION_STRING}"
      ],
      "env": {
        "POSTGRES_ALLOW_WRITE": "false"
      },
      "enabled": true,
      "autoConnect": false,
      "transport": "stdio",
      "retryOverride": "postgres",
      "readOnly": true
    }
  }
}
```

- stdio 예외 (상세명세 §D-7 원본 보존, 공식 MCP 레퍼런스 서버 패키지 — CLF-MCP-005 상속).
- `readOnly=true` — Bridge 측 추가 가드. WRITE 쿼리 (INSERT/UPDATE/DELETE/DROP/TRUNCATE) 감지 시 `security_violation` 즉시 차단.

### §2.7 RetryPolicy 오버라이드

```python
SERVER_RETRY_OVERRIDES["postgres"] = RetryPolicy(
    max_retries=2,           # LOCK-MCP-06 상한 3 이하 ✅ (DB 부하 보호)
    backoff_factor=2.0,
    initial_delay_ms=500,    # DB 응답 빠른 편
    max_delay_ms=5000,
    jitter_ratio=0.15,
    total_budget_ms=15000,   # 복잡 쿼리 고려
)
```

### §2.8 CircuitBreaker

기본값 적용. `postgres` 인스턴스 별도 운용. **DB 연결 실패는 critical** → CB OPEN 시 모든 후속 query 즉시 reject (cascade 방지).

### §2.9 보안 제약 (READ-ONLY 강제)

- **SQL Injection 방지**: query parameter binding 강제. 문자열 concat 차단.
- **WRITE 쿼리 차단**: `INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER|CREATE|GRANT|REVOKE` 정규식 매칭 시 `security_violation` (6-2 §9.3 OWASP LLM05).
- **PII 마스킹**: 결과 row 의 PII 의심 열 (이메일/전화번호) 자동 마스킹 후 응답.
- **schema 노출 제한**: `list_tables` 는 사전 화이트리스트 schema 만 노출 (`pg_catalog`, `information_schema` 차단).

### §2.10 테스트 설계 (T-PG)

| # | 테스트 ID | 시나리오 | 기대 결과 |
|---|----------|---------|----------|
| 1 | T-PG-01 | `query SELECT * FROM users LIMIT 10` | rows[] 반환, 1초 이내 |
| 2 | T-PG-02 | `query DROP TABLE users` (READ-ONLY 위반) | security_violation, 즉시 차단 |
| 3 | T-PG-03 | `query SELECT * FROM users WHERE name='" OR 1=1; --'` (SQL Injection) | 매개변수 binding 강제 → validation_error |
| 4 | T-PG-04 | `list_tables` (whitelist schema) | tables[] 반환 (pg_catalog 제외) |
| 5 | T-PG-05 | DB connection 실패 | connection_refused, retry 2회 후 fallback SQLAlchemy |
| 6 | T-PG-06 | 11MB 결과 row | payload_too_large, 페이지네이션 권장 |
| 7 | T-PG-07 | DB max_connections 95% | rate_limit, pause 5초 |
| 8 | T-PG-08 | TLS 미사용 (sslmode=disable) | security_violation (운영 정책) |
| 9 | T-PG-09 | `describe_table users` (PII 의심 열) | 열 정의 + PII 플래그 메타데이터 |

---

## §3. D-9 Puppeteer MCP Server

### §3.1 기본 연동 카탈로그

| 항목 | 값 | 근거 |
|------|-----|------|
| **서버 ID** | `puppeteer` | 상세명세 §D-9, 부록 §A.2 #9 |
| **패키지** | `@modelcontextprotocol/server-puppeteer` | 상세명세 §D-9 |
| **버전 핀닝** | `@modelcontextprotocol/server-puppeteer@latest` | §14 W-NEW-1 |
| **전송** | `stdio` (CLF-MCP-005 상속) | 상세명세 §D-9 |
| **실행 명령** | `npx -y @modelcontextprotocol/server-puppeteer` | 상세명세 §E-1 |
| **AutoConnect** | ❌ (On-demand, 리소스 무거움) | R-16-6 |
| **도구 6종** | `navigate`, `screenshot`, `click`, `fill`, `evaluate`, `get_content` | 상세명세 §D-9 |
| **네임스페이스** | `puppeteer.navigate` 등 (LOCK-MCP-02) | LOCK-MCP-02 |
| **capability** | `tools=true`, `logging=true` | capability_negotiation §8 |
| **리소스 제약** | 브라우저 인스턴스 1개, 탭 최대 5개, idle 5분 후 종료 | 상세명세 §D-9 |
| **Phase** | V2 | §7 Phase 2 #5 |

### §3.2 인증

| 항목 | 값 |
|------|-----|
| **인증 방식** | 없음 (로컬 브라우저 실행) |
| **환경 변수** | 해당 없음 (시크릿 없음) — R-16-5 대상 외 |
| **권한 범위** | 부모 프로세스 UID/GID 상속 + 화이트리스트 도메인 (SSRF 방지) |
| **신뢰 경계** | 로컬 브라우저 인스턴스, headless 모드 강제 |

### §3.3 Rate Limit

| 항목 | 값 | 근거 |
|------|-----|------|
| **공식 쿼터** | 없음 (로컬) | 본 도메인 |
| **내부 제한** | 동시 5 탭 / 인스턴스 1개 (LOCK-MCP-08 기반 idle 5분) | 상세명세 §D-9 |
| **OS 제약** | 메모리 (브라우저당 ~500MB), CPU (페이지 렌더) | 본 세션 정의 |
| **80% 경고** | 동시 4 탭 (80%) | 본 세션 정의 |
| **95% pause** | 5 탭 모두 사용 시 새 요청 큐 적재 | 본 세션 정의 |

### §3.4 Fallback

| 트리거 | Fallback 경로 |
|--------|---------------|
| **서버 연결 실패** | Playwright 직접 실행 (Bridge 내 어댑터) |
| **브라우저 크래시** | 새 인스턴스 생성, 진행 중 탭 5개 일괄 손실 (manual_review) |
| **`navigate` 타임아웃** | 30초 → connection_refused, 1회 재시도 |
| **`screenshot` 실패** | 빈 PNG + warning 메타데이터 |
| **CB OPEN** | manual_review |

### §3.5 라이프사이클

```
[On-demand]
  → 도구 호출 시 Connecting + 브라우저 인스턴스 생성 (3~5초)
  → 탭 1~5 활성
  → idle 5분 (탭 미사용) → 탭 자동 close
  → 탭 idle 5분: 탭 자동 close (리소스 정책) / 인스턴스 idle 10분: 인스턴스 종료 (LOCK-MCP-08)
```

### §3.6 설정 파일

```json
{
  "mcpServers": {
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
      "env": {
        "PUPPETEER_HEADLESS": "true",
        "PUPPETEER_MAX_TABS": "5",
        "PUPPETEER_IDLE_TAB_MS": "300000",
        "PUPPETEER_ALLOWED_DOMAINS": "${env.PUPPETEER_ALLOWED_DOMAINS:-*.example.com,*.vamos.io}"
      },
      "enabled": true,
      "autoConnect": false,
      "transport": "stdio",
      "retryOverride": "puppeteer",
      "sandbox": "no-internal-network"
    }
  }
}
```

- stdio 예외 상속 (CLF-MCP-005).
- `sandbox=no-internal-network` — Bridge 측 가드. SSRF 방지 (private IP 범위 차단).

### §3.7 RetryPolicy 오버라이드

```python
SERVER_RETRY_OVERRIDES["puppeteer"] = RetryPolicy(
    max_retries=1,           # LOCK-MCP-06 상한 이하 ✅ (브라우저 작업 비결정적)
    backoff_factor=2.0,
    initial_delay_ms=2000,   # 브라우저 안정화 대기
    max_delay_ms=10000,
    jitter_ratio=0.1,
    total_budget_ms=60000,   # navigate 타임아웃 30s + 재시도 여유
)
```

### §3.8 CircuitBreaker

기본값 적용. 브라우저 크래시는 critical → CB OPEN 시 인스턴스 재시작 트리거.

### §3.9 보안 제약 (샌드박스 + SSRF 방지)

- **headless 모드 강제**: `PUPPETEER_HEADLESS=true`. UI 모드 운영 환경 차단.
- **도메인 화이트리스트**: `PUPPETEER_ALLOWED_DOMAINS` 환경 변수에 명시된 도메인만 navigate 가능. 6-2 §9.3 OWASP LLM05 (SSRF).
- **private IP 차단**: `127.0.0.1` / `10.0.0.0/8` / `172.16.0.0/12` / `192.168.0.0/16` / `169.254.0.0/16` 차단.
- **`evaluate` JS 실행**: 사용자 제공 스크립트는 sandbox iframe 내 실행, parent context 접근 불가.
- **PII 마스킹**: `screenshot` / `get_content` 응답에서 PII 의심 텍스트 자동 마스킹.

### §3.10 테스트 설계 (T-PP)

| # | 테스트 ID | 시나리오 | 기대 결과 |
|---|----------|---------|----------|
| 1 | T-PP-01 | `navigate https://example.com` | URL 도달, screenshot 가능 |
| 2 | T-PP-02 | `navigate http://127.0.0.1` (SSRF) | security_violation, 차단 |
| 3 | T-PP-03 | `navigate https://internal-network.example.com` (도메인 미허용) | security_violation |
| 4 | T-PP-04 | 6번째 탭 동시 요청 | 큐 적재, 5 탭 중 1 탭 close 후 진행 |
| 5 | T-PP-05 | `evaluate window.parent.document.cookie` (parent context 접근) | sandbox 차단, undefined 반환 |
| 6 | T-PP-06 | 브라우저 크래시 | connection_refused, CB +1, 인스턴스 재시작 |
| 7 | T-PP-07 | idle 5분 후 탭 자동 close | 다음 호출 시 새 탭 생성 |
| 8 | T-PP-08 | `screenshot fullPage=true` 11MB PNG | payload_too_large, 압축 권장 |
| 9 | T-PP-09 | `navigate` 30초 타임아웃 | timeout, retry 1회 |

---

## §4. 공통 — 로깅·에스컬레이션·메트릭

### §4.1 ToolInvocationLog 채움 규칙

| 필드 경로 | postgres | puppeteer |
|----------|----------|-----------|
| `tool.name` | `postgres.query` 등 | `puppeteer.navigate` 등 |
| `tool.server_id` | `"postgres"` | `"puppeteer"` |
| `tool.phase` | `"V2"` | `"V2"` |
| `context.timeout_budget_ms` | 15000 | 60000 |
| `context.warnings[]` | `"db_conn_pool_80pct"` | `"puppeteer_4tabs_warning"` |
| `recovery.cb_state` | CB 상태 | CB 상태 |
| `recovery.rate_limit_source` | `null` (DB 자체) | `null` (로컬) |
| `recovery.read_only_violation` | true/false (READ-ONLY 위반 시) | — |
| `recovery.sandbox_violation` | — | true/false (SSRF/private IP 시) |

### §4.2 EscalationPayload `source_engine`

- postgres: `source_engine="mcp.retry.postgres"`
- puppeteer: `source_engine="mcp.retry.puppeteer"`

### §4.3 6-12 Event-Logging 표준

- `event="mcp.tool.invocation"` 정본 (search_tools §2.2).
- `trace_id` 전파.
- PII 마스킹: postgres 결과 PII 열 + puppeteer screenshot PII 텍스트 자동 마스킹.

### §4.4 KPI

| KPI | 목표 | postgres | puppeteer |
|-----|------|----------|-----------|
| 도구 호출 성공률 | > 99.0% | 99.5% | 98.0% (브라우저 비결정성) |
| CB OPEN 빈도 | < 1회/일 | < 1회/일 | < 1회/주 |
| 평균 응답 시간 | < 5s | < 1s | < 5s (페이지 렌더) |

---

## §5. CONFLICT / LOCK 점검

### §5.1 LOCK 준수 (변경 0건)

| LOCK | 본 세션 관련 | 변경 여부 |
|------|-------------|-----------|
| LOCK-MCP-01 10MB | T-PG-06 / T-PP-08 경계 | 참조만 ✅ |
| LOCK-MCP-02 네임스페이스 | §2.1 / §3.1 `{server}.{tool}` | 참조만 ✅ |
| LOCK-MCP-03 31 도구 | 본 파일 2 서버 9 도구 (3+6) | 참조만 ✅ |
| LOCK-MCP-04 Streamable HTTP | 두 서버 stdio 예외 (CLF-MCP-005 상속) | 참조만 ✅ |
| LOCK-MCP-05 동시 서버 5 | 본 파일 기여 2 → Phase 2 누계 9 서버 중 active 5 제한 | 참조만 ✅ |
| LOCK-MCP-06 max=3 / factor=2.0 | §2.7 max=2 / §3.7 max=1 모두 상한 이하 | 참조만 ✅ |
| LOCK-MCP-07 5/60s/3 | 두 서버 모두 기본값 | 참조만 ✅ |
| LOCK-MCP-08 idle 10분 | postgres 적용. puppeteer 는 탭 idle 5분 별개 정책 (인스턴스 idle 10분 동시 적용) | 참조만 ✅ |
| LOCK-MCP-09 정본 소유 | 본 세션 = sot 2/4-3 정본 | 참조만 ✅ |
| LOCK-MCP-10 Pool max 10 | 본 파일 2 슬롯 점유 | 참조만 ✅ |
| `retry_circuit_breaker.md §14.1 L1~L10` | 변경 0건 | 참조만 ✅ |

### §5.2 CONFLICT 후보

| 후보 | 판정 | 근거 |
|------|------|------|
| postgres stdio vs LOCK-MCP-04 Streamable HTTP | 후보 아님 | CLF-MCP-005 RESOLVED-DEFERRED 상속 |
| puppeteer stdio vs LOCK-MCP-04 | 후보 아님 | CLF-MCP-005 RESOLVED-DEFERRED 상속 |
| READ-ONLY 모드 강제 vs 상세명세 §D-7 "명시적 허용 시만 WRITE" | 후보 아님 | Bridge 측 추가 가드 (§2.6 readOnly=true), 상세명세 옵션 보존 (`POSTGRES_ALLOW_WRITE=true` 환경 변수 명시) |
| puppeteer 브라우저 1개 / 탭 5개 vs LOCK-MCP-10 Pool 10 | 후보 아님 | LOCK-MCP-10 은 MCP connection pool, puppeteer 내부 탭은 별개 리소스 정책 (상세명세 §D-9) |
| puppeteer idle 탭 5분 vs LOCK-MCP-08 idle 10분 | 후보 아님 | 두 정책 동시 적용 (§5.1 LOCK-MCP-08 row 명시) |

`[INTERFACE_MISMATCH]` 0건 / `[LOCK_CHANGE_NEEDED]` 0건 / `[CONFLICT_CANDIDATE]` 0건.

---

## §6. 후속 세션 핸드오프

| 후속 세션 | 본 파일 소비 지점 | 변경 금지 |
|----------|-----------------|-----------|
| **2-4 Connection Pool** | §2.5 / §3.5 라이프사이클 + LOCK-MCP-10 Pool 슬롯 (2 슬롯) | AutoConnect/On-demand (R-16-6) |
| **communication_servers.md (본 STEP_B 파트너)** | §1 교차 참조 + §4 공통 패턴 | 정본 search_tools §2 |
| **6-13 Operations 런북** | §2.3 DB connection 80% / §3.3 puppeteer 탭 80% | 헤더 필드명 |
| **6-12 Event-Logging** | §4.1 신규 필드 (`read_only_violation` / `sandbox_violation`) | retry_circuit_breaker.md §14.1 L9 |
| **3-4 Workflow-RPA** | §3 Puppeteer 도구 6종 → 자동화 워크플로우 통합 | tool 이름 (LOCK-MCP-02) |
| **Phase 3 Sentry / Exa** | 9-section 템플릿 직접 재사용 | LOCK-MCP-* 재정의 0 |

---

## §7. 본 파일 LOCK 지점

| # | LOCK 지점 | 섹션 | 변경 조건 |
|---|-----------|------|----------|
| L-AS-1 | `postgres` 서버 ID + 도구 3종 네임스페이스 | §2.1 | 상세명세 §D-7 변경 시만 |
| L-AS-2 | READ-ONLY 모드 기본 + WRITE 차단 정규식 | §2.9 | 운영 정책 변경 시만 |
| L-AS-3 | `SERVER_RETRY_OVERRIDES["postgres"]` 6 필드 | §2.7 | LOCK-MCP-06 상한 유지 |
| L-AS-4 | `puppeteer` 서버 ID + 도구 6종 네임스페이스 | §3.1 | 상세명세 §D-9 변경 시만 |
| L-AS-5 | `SERVER_RETRY_OVERRIDES["puppeteer"]` 6 필드 | §3.7 | 동 |
| L-AS-6 | 도메인 화이트리스트 + private IP 차단 | §3.9 | 6-2 §9.3 변경 시만 |
| L-AS-7 | 시크릿 환경 변수명 (`POSTGRES_CONNECTION_STRING`) | §2.6 | R-16-5 변경 시만 |
| L-AS-8 | `PUPPETEER_HEADLESS=true` / `PUPPETEER_MAX_TABS=5` | §3.6 | 운영 정책 변경 시만 |
| L-AS-9 | `sandbox=no-internal-network` | §3.6 | SSRF 정책 변경 시만 |
| L-AS-10 | TLS `sslmode=require` 강제 | §2.2 | 운영 환경 정책 변경 시만 |

---

## §8. 검증 요약 (자체)

| 체크 | 결과 | 근거 |
|------|------|------|
| R-16-3 인증/Rate Limit/Fallback 3종 전수 | ✅ | postgres §2.2/§2.3/§2.4 + puppeteer §3.2/§3.3/§3.4 = 2×3 = 6 항목 |
| R-16-5 시크릿 환경 변수 | ✅ | postgres `${secrets.POSTGRES_CONNECTION_STRING}` 명시. puppeteer 시크릿 없음 (R-16-5 대상 외) |
| R-16-6 AutoConnect 구분 | ✅ | 두 서버 모두 On-demand |
| LOCK-MCP-06 상한 준수 | ✅ | postgres max=2, puppeteer max=1, factor=2.0 |
| LOCK-MCP-08 idle 10분 | ✅ | postgres 적용. puppeteer 는 탭 idle 5분 + 인스턴스 idle 10분 |
| LOCK-MCP-10 Pool 슬롯 | ✅ | 2 슬롯 기여 |
| McpError / ToolInvocationLog / EscalationPayload 재정의 | ✅ 0건 | §4.1/§4.2 정본 참조만 |
| `retry_circuit_breaker.md §14.1 L1~L10` 변경 | ✅ 0건 | §5.1 전수 점검 |
| Gate P2→3 "11개 외부 서버 연동" 기여 | ✅ 2/11 | 본 파일 2 + communication_servers 4 + P1-6 3 = 9, Phase 3 Sentry+Exa 잔여 |
| READ-ONLY 강제 vs 상세명세 옵션 | ✅ | `POSTGRES_ALLOW_WRITE=false` 기본, `true` 시 명시 허용 |
| 샌드박스 + SSRF 방지 (puppeteer) | ✅ | §3.9 도메인 화이트리스트 + private IP 차단 + headless 강제 |
| CLF-MCP-005 stdio 예외 상속 | ✅ 두 서버 §2.6/§3.6 주석 | development_servers.md §5.1 선례 |
| FABRICATION 마커 census | ✅ 0/10 prose | 마커 prose 0건 |

---

## §9. 변경 이력

| 날짜 | 변경 내용 | 세션 |
|------|----------|------|
| 2026-04-26 | 신규 작성 — PostgreSQL + Puppeteer 2 외부 MCP 서버 (Phase 2 #5, 9 도구, READ-ONLY 강제 + SSRF 방지, R-16-3/5/6 전수, 본 STEP_B 외부 서버 6건 누계 4+2) | 2-3 (Phase 2 V2-Phase 2) |
