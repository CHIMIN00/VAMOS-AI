# 02.search_servers — 외부 MCP 검색 서버 연동 (Brave Search)

> **세션**: P1-6 · **Phase**: 1 V1 · **상태**: L3 DRAFT (Brave Search) · SHELL (Exa — Phase 3 대기)
> **범위**: D-8 Brave Search 연동 상세 정의 — 패키지/전송/인증/도구/Rate Limit(2000/월)/Fallback(DuckDuckGo→내부 web_search)/AutoConnect/RetryPolicy 오버라이드 + W-NEW-2 쿼터 80% 경고 및 자동 전환 경로
> **L3 승급 기준**: R-16-3 (인증·Rate Limit·Fallback 3종) + R-16-5 (시크릿) + R-16-6 (AutoConnect) + §14 W-NEW-2 대응 + LOCK-MCP-06 오버라이드 (`retry_circuit_breaker.md §13.1`) 실 값 반영

---

## §1. 교차 참조 블록

| 참조 대상 | 위치 | 용도 |
|----------|------|------|
| 종합계획서 §3.4 LOCK-MCP-01 | `MCP_SERVER_CLIENT_구조화_종합계획서.md` | 페이로드 10MB 상한 |
| 종합계획서 §3.4 LOCK-MCP-02 | 동상 | 네임스페이스 `{server}.{tool}` |
| 종합계획서 §3.4 LOCK-MCP-03 | 동상 | 31개 도구 목록 — 외부 11 중 본 파일 1건 (Brave Search) |
| 종합계획서 §3.4 LOCK-MCP-05 | 동상 | 동시 서버 5 상한 |
| 종합계획서 §3.4 LOCK-MCP-06 | 동상 | RetryPolicy 상한 (max 3 / factor 2.0) |
| 종합계획서 §3.4 LOCK-MCP-07 | 동상 | CB 5/60s/3 |
| 종합계획서 §3.4 LOCK-MCP-10 | 동상 | Pool max 10 |
| 종합계획서 §4.3 R-16-3 | 동상 | 인증/Rate Limit/Fallback 3종 필수 |
| 종합계획서 §4.3 R-16-5 | 동상 | 시크릿 환경 변수 참조 |
| 종합계획서 §4.3 R-16-6 | 동상 | AutoConnect: Brave Search ✅ |
| 종합계획서 §14 W3 | 동상 | Rate Limit 초과 대응 |
| 종합계획서 §14 W-NEW-2 | 동상 | **Brave Search 무료 2000/월 소진 — 80% 경고 + DuckDuckGo 자동 전환** (본 파일 핵심 대응) |
| 종합계획서 부록 §A.2 #8 | 동상 | 서버 카탈로그 (Brave Search) |
| 종합계획서 부록 §B.1 | 동상 | AutoConnect vs On-demand |
| 상세명세 §D-8 | `MCP_SERVER_CLIENT_상세명세.md` | Brave Search 원본 연동 설정 |
| 상세명세 §E-1 | 동상 | mcp_config.json 구조 |
| 상세명세 §H-1 | 동상 | Brave Search 2000 req/월 (로컬 카운터, 월초 리셋) |
| 상세명세 §H-2 | 동상 | 80%/95%/100% 단계별 대응 |
| `bridge_layer.md §2~§10` | `03_connection-management/` | Streamable HTTP 클라이언트 ABC / HTTP→McpError 매핑 |
| `connection_protocol.md §1~§6` | 동상 | 4단계 연결 프로토콜 |
| `retry_circuit_breaker.md §2.1 / §5.1` | 동상 | RetryPolicy / CircuitBreaker 기본값 |
| `retry_circuit_breaker.md §6.1 parse_retry_after` | 동상 | 429 Retry-After 헤더 파싱 (초/HTTP-date) |
| `retry_circuit_breaker.md §6.2` | 동상 | `rate_limit` CB 무영향 원칙 |
| `retry_circuit_breaker.md §6.3` | 동상 | Brave Search W-NEW-2 연동 지점 — **본 세션이 소비** |
| `retry_circuit_breaker.md §13.1` | 동상 | `SERVER_RETRY_OVERRIDES["brave-search"]` 예시 — 본 세션이 실 값 확정 |
| `retry_circuit_breaker.md §14.1 L1~L10` | 동상 | LOCK 지점 — 변경 금지 |
| `search_tools.md §2.1~§2.3` | `01_internal-tools/` | McpError / ToolInvocationLog / EscalationPayload 정본 (재정의 금지) |
| `web_tools.md §1 web_search` | 동상 | 내부 `web_search` 도구 — 최종 Fallback |
| `development_servers.md` | `02_external-servers/` | 본 세션 파트너 파일 (Filesystem / GitHub) |
| 6-12 Event-Logging | `6-12_event-logging/` | trace_id 전파 / 구조화 로깅 |

---

## §2. 범위 선언

본 파일은 `02_external-servers/` 서브폴더의 **검색 카테고리** 를 담당한다.

| # | 서버 | Phase 배정 | 본 세션 상태 | 비고 |
|---|------|-----------|-------------|------|
| 8 | **Brave Search** | V1 (P1-6) | ✅ L3 DRAFT (본 파일 §3) | Gate P1→2 "외부 서버 3개 연동" 3번째 |
| 11 | Exa | V3 (Phase 3) | ⏭️ 본 세션 범위 외 | 본 파일 §6 최소 스텁 |

Gate P1→2 "외부 서버 3개 연동" 조건 중 본 파일이 **Brave Search 1건** 담당. 나머지 2건 (Filesystem, GitHub) 은 `development_servers.md` 가 담당한다.

---

## §3. D-8 Brave Search MCP Server

### §3.1 기본 연동 카탈로그

| 항목 | 값 | 근거 |
|------|-----|------|
| **서버 ID** | `brave-search` | 상세명세 §D-8, 부록 §A.2 #8 |
| **패키지** | `@modelcontextprotocol/server-brave-search` | 상세명세 §D-8 |
| **버전 핀닝** | `@modelcontextprotocol/server-brave-search@latest` (W-NEW-1 대응 V2 특정 버전) | §14 W-NEW-1 |
| **전송 (transport)** | `stdio` (서브프로세스 NDJSON) | 상세명세 §D-8 / 부록 §A.2 #8 |
| **실행 명령** | `npx -y @modelcontextprotocol/server-brave-search` (env 로 `BRAVE_API_KEY` 주입) | 상세명세 §E-1 형식 확장 |
| **AutoConnect** | ✅ (앱 시작 시 자동 연결) | R-16-6 / 부록 §B.1 / 종합계획서 §7.3 Phase 1 #6 |
| **도구 2종** | `web_search`, `local_search` | 상세명세 §D-8 |
| **네임스페이스** | `brave-search.web_search`, `brave-search.local_search` (LOCK-MCP-02) | LOCK-MCP-02 |
| **Phase** | V1 (본 세션 P1-6 L3 DRAFT) | §7.3 Phase 1 #6 |

> **용어 구분**: 외부 서버 `brave-search.web_search` (D-8) 와 내부 도구 `web_search` (A-7, `web_tools.md §1`) 는 **다른 도구**이다. 내부 `web_search` 는 복수 검색 엔진을 추상화한 상위 도구이며, Brave Search 는 그 백엔드 중 하나가 될 수 있다. LOCK-MCP-02 네임스페이스 접두사로 두 도구를 구분한다 (CONFLICT 회피).

### §3.2 인증 (R-16-3 #1 / R-16-5)

| 항목 | 값 |
|------|-----|
| **인증 방식** | API Key (HTTP 헤더 `X-Subscription-Token`, MCP 서버 내부에서 Brave API 호출 시 첨부) |
| **환경 변수명** | `BRAVE_API_KEY` (시크릿 참조: `${secrets.BRAVE_API_KEY}`) |
| **시크릿 주입 경로** | `mcp_config.json §3.5` `env` 블록 → 서브프로세스 `env` 로 전달 |
| **하드코딩 금지** | R-16-5 준수 — VCS 커밋 차단 필터(`.gitignore` + CI 스캔, W4 대응) |
| **401/403 처리** | `McpError.category="auth_failure"` → `auth_failure_max_retries=1` 1회 재시도 후 에스컬레이션 (API Key 재발급 요청) |
| **키 미설정 시** | MCP 서버가 초기화 단계 (Stage 2 Initialize 10s) 에서 실패 → Fallback = 내부 `web_search` 즉시 전환 |

### §3.3 Rate Limit (R-16-3 #2 / W-NEW-2 핵심)

#### §3.3.1 공식 쿼터

| 항목 | 값 | 근거 |
|------|-----|------|
| **무료 티어 쿼터** | 2000 req / month | 상세명세 §D-8 / §H-1 |
| **유료 티어** | 무제한 | 상세명세 §D-8 (본 세션은 무료 티어 기준 대응) |
| **측정 방식** | **로컬 카운터** (Bridge 내 월별 카운터) — Brave API 는 표준 `X-RateLimit-*` 헤더 미제공 | 상세명세 §H-1 |
| **리셋 주기** | **월초** (매월 1일 00:00 UTC) | 상세명세 §H-1 |
| **카운터 저장소** | **Redis 공유 원자 카운터** `vamos:mcp:brave:quota:{YYYY-MM}` (`brave_redis_quota.md §2` LUA atomic, 멀티 인스턴스 sync 정본). 로컬 `memory_write` 단일 인스턴스 카운터는 deprecated — Redis 연결 실패 시 fail-closed 폴백으로만 사용 | `02_external-servers/brave_redis_quota.md §2` |

#### §3.3.2 80% / 95% / 100% 단계별 대응 (§H-2 + W-NEW-2)

| 단계 | 임계 (Remaining) | 동작 | 출력 |
|------|-----------------|------|------|
| **정상** | ≥ 400 req (≤ 80% 사용) | Brave Search 정상 경로 | `context.warnings=[]` |
| **80% 도달 경고** | < 400 req (> 80% 사용) | ① 경고 로그 ② 우선순위 낮은 요청 지연 (`priority="low"` 호출은 1s 큐잉) ③ 사용자 노출 배너 (I-20 비차단) | `context.warnings += ["brave_quota_80pct"]` |
| **95% 소진** | < 100 req (> 95% 사용) | 비필수 호출 일시 중단 — `priority = low` 만 차단, `priority ∈ {medium, high}` 허용 (기본 priority=medium 보존) | `context.warnings += ["brave_quota_95pct"]` |
| **100% 소진** | 0 req | **DuckDuckGo 자동 전환** (W-NEW-2 정본) — 본 파일 §3.4 Fallback 체인 1차 | `context.warnings += ["brave_quota_exhausted"]`, `recovery.fallback_chain="duckduckgo"` |
| **리셋** | 월초 00:00 UTC | 로컬 카운터 `memory_write` 재설정 (`brave_search_quota_{YYYY-MM}` 새 키) | — |

#### §3.3.3 `priority` 필드 해석

- 도구 호출 요청 파라미터 `priority` (`low` / `medium` / `high`, 기본 `medium`) 는 `ToolInvocationLog.context.priority` 에서 유래.
- 본 세션은 해석 규칙만 정의하며, 실 호출 분류는 Blue Node (`reasoning_engine`) 책임.

#### §3.3.4 429 수신 경로

무료 티어 2000/월 소진 시 Brave API 는 보통 429 를 반환하지 않고 권한 오류를 반환할 수 있으나, 쿼터 정책 변경에 대비하여 본 세션은 429 수신 시에도:

1. `retry_circuit_breaker.md §6.1 parse_retry_after()` 호출 — `Retry-After` 헤더 (초/HTTP-date 둘 다 허용).
2. `rate_limit` 카테고리로 매핑, CB 무영향 (`retry_circuit_breaker.md §14.1 L10`).
3. `Retry-After` 가 `total_budget_ms` (§3.7 = 60000ms) 를 초과하면 예산 포기 → §3.4 Fallback 체인 진입.
4. `Retry-After` 가 1초 미만이거나 누락 시 `initial_delay_ms=2000` (§3.7 오버라이드) 적용.

### §3.4 Fallback 체인 (R-16-3 #3 / W-NEW-2)

```
Brave Search (1차 시도)
  ├─[Stage 1~3 실패 / 5xx / CB OPEN]──▶ DuckDuckGo HTML scraper (2차)
  ├─[100% 쿼터 소진 / 429 Retry-After > 예산]──▶ DuckDuckGo HTML scraper (2차)
  │                                                  │
  │                                                  ├─[DuckDuckGo 실패]──▶ 내부 web_search (3차, `web_tools.md §1`)
  │                                                  │                          │
  │                                                  │                          └─[실패]──▶ `recovery_hint="manual_review"`
  │
  └─[auth_failure / 서버 초기화 실패]──▶ 내부 web_search (2차 직행)
```

| 단계 | 트리거 | 경로 | 근거 |
|------|-------|------|------|
| 1 | Brave Search 정상 | `brave-search.web_search` / `brave-search.local_search` | 상세명세 §D-8 |
| 2a | **100% 쿼터 소진** | DuckDuckGo HTML scraper (무인증, 무쿼터) — Bridge 내 fallback 어댑터 | **W-NEW-2 정본** (종합계획서 §14) |
| 2b | 서버 연결 실패 (Stage 1~3 에러) | 동 (DuckDuckGo) | 본 파일 §3.4 |
| 2c | CB OPEN 60초 연속 | 동 (DuckDuckGo) | `retry_circuit_breaker.md §5.4` |
| 2d | `auth_failure` (API Key 미설정/만료) | **내부 `web_search` 직행** (DuckDuckGo 스킵 — 인증 문제는 DuckDuckGo 로 해결 안 됨이 아니지만, 운영팀 교정 요구 명확성 우선) | `retry_circuit_breaker.md §3.3` |
| 3 | DuckDuckGo 실패 | 내부 `web_search` (`web_tools.md §1`, Google CSE 또는 대체 엔진) | `web_tools.md §1` |
| 4 | 내부 `web_search` 도 실패 | `recovery_hint="manual_review"` + 에스컬레이션 | `retry_circuit_breaker.md §11.2` |

> **DuckDuckGo HTML scraper 주의사항**: robots.txt 존중 / User-Agent 명시 / rate 0.5 req/s 제한. 본 세션은 인터페이스만 선언하며 실 구현은 Bridge 내 fallback 어댑터 (`bridge_layer.md`) 에 위임.

### §3.5 AutoConnect 라이프사이클 (R-16-6)

```
[앱 시작]
  ↓
Disconnected → Connecting (Stage 1 Discovery 5s)
             → Connecting (Stage 2 Initialize 10s — API Key 검증 포함)
             → Connecting (Stage 3 ToolList 5s, `tools/list`)
             → Connected → Ready
  ↓  [항시 유지 — LOCK-MCP-08 idle 10분 적용 안 함]
  ↓  [CB OPEN 시에만 Disconnecting → Reconnecting backoff]
  ↓  [쿼터 100% 소진은 연결 유지 + Fallback 라우팅 — 서버 종료 아님]
```

- **idle 타임아웃 제외** — AutoConnect 서버는 LOCK-MCP-08 적용 대상 아님 (부록 §B.1).
- **재연결** — Stage 실패 시 §3.7 오버라이드 적용.
- **쿼터 소진 ≠ 서버 중단** — 본 세션 정본: 쿼터 100% 소진 시에도 MCP 서버 프로세스는 유지하며 Bridge 레벨에서 Fallback 라우팅만 활성화. 다음 월초 리셋 시 자동 복귀.

### §3.6 설정 파일 (mcp_config.json §E-1 확장)

```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "${secrets.BRAVE_API_KEY}"
      },
      "enabled": true,
      "autoConnect": true,
      "transport": "stdio",
      "retryOverride": "brave-search",
      "quota": {
        "source": "local_counter",
        "storage": "memory_write:persistent:brave_search_quota_${YYYY-MM}",
        "monthlyLimit": 2000,
        "warningThresholdPct": 80,
        "pauseThresholdPct": 95,
        "resetCron": "0 0 1 * *",
        "fallbackChain": ["duckduckgo", "internal_web_search"]
      }
    }
  }
}
```

- **쿼터 소스 = 로컬 카운터** — 상세명세 §H-1 "Brave Search 로컬 카운터" 원칙 준수.
- **리셋 cron** — 월초 0시 0분 (UTC) — `6-12 Event-Logging` 의 스케줄러 또는 `6-13 Operations` 런북에서 구동.
- **저장소 키 템플릿** — `${YYYY-MM}` 치환은 Bridge 실행 시 동적으로 수행.

### §3.7 RetryPolicy 오버라이드 (P1-5 → P1-6 핸드오프 실 값)

`retry_circuit_breaker.md §13.1 SERVER_RETRY_OVERRIDES["brave-search"]` 의 예시 값을 본 세션에서 최종 확정한다. 예시 그대로 유지 (튜닝 불필요).

```python
SERVER_RETRY_OVERRIDES["brave-search"] = RetryPolicy(
    max_retries=3,           # LOCK-MCP-06 상한 불변
    backoff_factor=2.0,      # LOCK-MCP-06 불변
    initial_delay_ms=2000,   # Brave 공용 API — 1s 너무 짧음, 2s 로 완화
    max_delay_ms=30000,      # 기본
    jitter_ratio=0.3,        # 공용 API — jitter 강화 (다중 VAMOS 인스턴스 thundering herd 완화)
    total_budget_ms=60000,   # 기본 1분
)
```

| 필드 | 값 | 근거 |
|------|-----|------|
| `max_retries` | `3` | LOCK-MCP-06 상한 그대로, 공용 API 특성상 일시 장애 재시도 필요 |
| `backoff_factor` | `2.0` | LOCK-MCP-06 불변 |
| `initial_delay_ms` | `2000` | §13.1 예시 — "1s 너무 짧음" (공용 API 보호) |
| `max_delay_ms` | `30000` | 기본 |
| `jitter_ratio` | `0.3` | §13.1 예시 — "공용 API 이므로 jitter 강화" |
| `total_budget_ms` | `60000` | 기본 — 1분 예산 초과 시 Fallback 진입 |

> 오버라이드 상한 검증: `max_retries=3 ≤ 3` ✅, `backoff_factor=2.0 == 2.0` ✅ (§14.1 L1 불변 준수).
>
> 결과: 본 세션은 `retry_circuit_breaker.md §13.1` 예시값 3종 (`initial_delay_ms=2000` / `jitter_ratio=0.3` / `total_budget_ms=60000`) 을 **그대로 확정**하며 별도 튜닝 없음.

### §3.8 CircuitBreaker 파라미터 (LOCK-MCP-07 재사용)

- 기본값 (`failure_threshold=5` / `recovery_timeout_s=60` / `success_threshold=3`) 그대로 적용 (§14.1 L2 불변).
- Brave Search 인스턴스 CB 는 `get_circuit_breaker("brave-search")` 로 조회.
- `rate_limit` (쿼터 소진/429) 은 CB 무영향 (§14.1 L10) — 월초 리셋 후 정상 동작하는 서버가 차단되지 않도록.
- `connection_refused` / `timeout` / `server_error` 만 CB 카운트 증가.

### §3.9 테스트 설계 (T-BS)

| # | 테스트 ID | 시나리오 | 기대 결과 |
|---|----------|---------|----------|
| 1 | T-BS-01 | AutoConnect 정상 — Stage 1~3 5+10+5s 이내 완료, API Key 검증 통과 | Connected→Ready, 로컬 카운터 초기화 (월 첫 호출 시) |
| 2 | T-BS-02 | 정상 `web_search(q="VAMOS")` — Remaining=1999 → 1998 | `context.warnings=[]`, 응답 정상 |
| 3 | T-BS-03 | Remaining=399 진입 (80% 도달) | `context.warnings=["brave_quota_80pct"]` 로그 + `priority=low` 호출 1s 큐잉 |
| 4 | T-BS-04 | Remaining=99 진입 (95% 도달) | `priority=low/medium` 차단, `priority=high` 만 통과 |
| 5 | T-BS-05 | Remaining=0 (100% 소진) | **DuckDuckGo 자동 전환** — `recovery.fallback_chain="duckduckgo"` |
| 6 | T-BS-06 | DuckDuckGo 도 실패 | 내부 `web_search` 3차 Fallback |
| 7 | T-BS-07 | 모든 Fallback 실패 | `recovery_hint="manual_review"` 에스컬레이션 |
| 8 | T-BS-08 | `BRAVE_API_KEY` 미설정 | Stage 2 Initialize 실패 → `auth_failure` → 내부 `web_search` 직행 |
| 9 | T-BS-09 | 429 수신 (`Retry-After: 3600`) | `parse_retry_after()` = 3600000ms > `total_budget_ms=60000` → 예산 포기 → Fallback 진입 |
| 10 | T-BS-10 | 429 수신 (`Retry-After: 30`) | 30s 대기 후 재시도 (`initial_delay_ms=2000` 아닌 `Retry-After` 우선) |
| 11 | T-BS-11 | 5xx 5회 연속 | CB OPEN, 60초 대기, HALF_OPEN probe |
| 12 | T-BS-12 | 월초 리셋 | 로컬 카운터 재초기화, `context.warnings=[]` 복귀 |
| 13 | T-BS-13 | 10MB 초과 응답 | `payload_too_large` (LOCK-MCP-01) — 서버 거절 |
| 14 | T-BS-14 | `brave-search.local_search` 호출 | 지역 검색 정상 동작, 쿼터 카운트 +1 |
| 15 | T-BS-15 | 쿼터 99% + 정상 요청 5회 연속 성공 | CB 는 변동 없음 (rate_limit CB 무영향) |

---

## §4. 공통 — 로깅·에스컬레이션·메트릭

### §4.1 ToolInvocationLog 채움 규칙

`search_tools.md §2.2` 정본 구조 그대로 사용 (재정의 0건).

| 필드 경로 | Brave Search |
|----------|--------------|
| `tool.name` | `brave-search.web_search` / `brave-search.local_search` (LOCK-MCP-02) |
| `tool.server_id` | `"brave-search"` |
| `tool.phase` | `"V1"` |
| `context.session_id` | `Mcp-Session-Id` (Stage 2 Initialize 응답) |
| `context.timeout_budget_ms` | 60000 (§3.7 `total_budget_ms`) |
| `context.priority` | `"low"` / `"medium"` / `"high"` (Blue Node 주입) |
| `context.warnings[]` | `"brave_quota_80pct"` / `"brave_quota_95pct"` / `"brave_quota_exhausted"` |
| `context.quota_remaining` | 로컬 카운터 현재 값 (0~2000) |
| `recovery.cb_state` | CB 상태 |
| `recovery.cb_consecutive_failures` | CB 카운트 |
| `recovery.rate_limit_source` | `"local_counter"` (Brave Search 는 헤더 없음) |
| `recovery.fallback_chain` | `null` / `"duckduckgo"` / `"internal_web_search"` |

> `recovery{}` 의 3 신규 키 (`cb_state` / `cb_consecutive_failures` / `rate_limit_source`) 는 `retry_circuit_breaker.md §14.1 L9` 정본.
> `context.quota_remaining` / `recovery.fallback_chain` 는 본 세션이 `context{}` / `recovery{}` 맵에 **추가**한 키. 맵 확장 허용 (§14.1 L9 "기존 5 키 재정의 금지, 추가는 허용").

### §4.2 EscalationPayload `source_engine` 형식

`retry_circuit_breaker.md §14.1 L8` 정본 형식 준수: `source_engine="mcp.retry.brave-search"`.

### §4.3 6-12 Event-Logging 표준 준수

- `event: "mcp.tool.invocation"` (search_tools §2.2)
- `trace_id` 전파 — Blue Node → Bridge → MCP 서브프로세스 stdin
- 쿼터 80% 도달 시 별도 이벤트 `event: "mcp.quota.warning"` 발행 (본 세션 신규 — 6-12 표준 준수)
- 쿼터 100% 소진 시 `event: "mcp.quota.exhausted"` 발행 → 6-13 Operations 런북 알림 채널 연동

### §4.4 KPI

| KPI | 목표 | Brave Search |
|-----|------|--------------|
| 도구 호출 성공률 | > 99.5% | Fallback 체인 포함 시 99.9% 기대 (DuckDuckGo/내부 `web_search` 로 복원) |
| CB OPEN 빈도 | < 1회/일 | < 1회/주 (rate_limit CB 무영향 → OPEN 빈도 낮음) |
| 평균 응답 시간 | < 2s | < 1.5s (Brave Search Typical) |
| 월 쿼터 소진율 | < 80% (무료 티어) | W-NEW-2 경고 임계 |

---

## §5. CONFLICT / LOCK 점검

### §5.1 LOCK 준수 (변경 0건)

| LOCK | 본 세션 관련 | 변경 여부 |
|------|-------------|-----------|
| LOCK-MCP-01 10MB | T-BS-13 테스트에서 경계 검증 | 참조만 ✅ |
| LOCK-MCP-02 네임스페이스 | §3.1 `brave-search.web_search` / `brave-search.local_search` | 참조만 ✅ |
| LOCK-MCP-03 31개 도구 | 본 파일 1 서버 2 도구 (외부 11 중 1건) | 참조만 ✅ |
| LOCK-MCP-04 Streamable HTTP | Brave Search 는 stdio 예외 (상세명세 §D-8 원문) | 참조만 ✅ |
| LOCK-MCP-05 동시 서버 5 | 본 파일 기여분 1 | 참조만 ✅ |
| LOCK-MCP-06 max 3 / factor 2.0 | §3.7 `max_retries=3` / `backoff_factor=2.0` 상한 준수 | 참조만 ✅ |
| LOCK-MCP-07 5/60s/3 CB | 기본값 재사용 | 참조만 ✅ |
| LOCK-MCP-08 idle 10분 | AutoConnect 제외 (§3.5) | 참조만 ✅ |
| LOCK-MCP-09 정본 소유 | sot 2/4-3 정본 작성 | 참조만 ✅ |
| LOCK-MCP-10 Pool max 10 | 본 파일 슬롯 1 점유 | 참조만 ✅ |
| `retry_circuit_breaker.md §14.1 L1~L10` | 모든 지점 참조만 | 참조만 ✅ |
| `retry_circuit_breaker.md §6.2 rate_limit CB 무영향` | §3.3/§3.8 재선언 | 참조만 ✅ |
| `retry_circuit_breaker.md §6.3 W-NEW-2 연동 지점` | 본 세션이 소비하여 §3.3/§3.4 확정 | 소비만 (변경 0건) |

### §5.2 CONFLICT 후보

| 후보 | 판정 | 근거 |
|------|------|------|
| 내부 `web_search` (A-7, `web_tools.md §1`) vs 외부 `brave-search.web_search` (D-8) 이름 충돌 | **후보 아님** | LOCK-MCP-02 네임스페이스 접두사로 구분 (`brave-search.web_search` vs `web_search`). §3.1 Tip 박스에서 명시. |
| 상세명세 §D-8 "내부 `web_search` (Google CSE)" 표기 vs `web_tools.md §1` 실 백엔드 | 후보 아님 | 내부 `web_search` 는 복수 백엔드 추상화, Google CSE 는 한 예시일 뿐. `web_tools.md §1` 가 정본. |
| W-NEW-2 DuckDuckGo 자동 전환 vs `retry_circuit_breaker.md §6.3` 위임 | 후보 아님 | §6.3 이 "P1-6 에 위임" 명시, 본 세션이 §3.4 에서 실 경로 확정 |
| 쿼터 로컬 카운터 vs 다중 인스턴스 VAMOS | **향후 고려** | 본 세션은 단일 인스턴스 기준. 다중 인스턴스 시 공유 카운터 필요 → Phase 2/3 에서 Redis 공유 또는 6-13 런북 이관. 본 세션 `[INTERFACE_MISMATCH]` 는 아님 (LOCK 위반 없음). |

`[INTERFACE_MISMATCH]` 0건 / `[LOCK_CHANGE_NEEDED]` 0건.

---

## §6. Exa MCP Server (D-11, Phase 3 스텁)

> **상태**: SHELL — Phase 3 (V3) 배정. 본 세션은 Gate P1→2 "외부 서버 3개 연동" 범위 외.

| 항목 | 값 |
|------|-----|
| **서버 ID** | `exa` |
| **패키지** | `exa-mcp-server` |
| **전송** | `stdio` |
| **인증** | Exa API Key (`EXA_API_KEY`) |
| **도구** | `search`, `find_similar`, `get_contents` |
| **AutoConnect** | ❌ (On-demand) |
| **Fallback** | Brave Search → 내부 `web_search` (상세명세 §D-11) |
| **Phase** | V3 (Phase 3) |

Phase 3 세션에서 본 파일 §6 를 전면 작성한다. 본 세션은 참조만.

---

## §7. 후속 세션 핸드오프

| 후속 세션 | 본 파일 소비 지점 | 변경 금지 |
|----------|-----------------|-----------|
| **P1-7** (#7 에러 카탈로그) | §3.3 쿼터 단계별 사용자 노출 메시지, §3.4 Fallback 체인의 `auth_failure` / `rate_limit` / `server_error` 에러 유형 | §3.7 RetryPolicy, §3.3 임계값, §3.4 Fallback 순서, `recovery{}` 추가 키 |
| **P2-2** (도구 디스커버리) | §3.1 도구 2종 (`web_search`, `local_search`) 을 `tools/list` 결과 캐시 (TTL 1시간, W-NEW-1) 초기값 | 도구 이름 문자열 (LOCK-MCP-02) |
| **P2-6** (Pool 최적화) | §3.5 라이프사이클 + AutoConnect 규칙 + Pool 슬롯 1 점유 | R-16-6 AutoConnect 값 |
| **Phase 3 Exa 세션** | §6 스텁을 참조하여 L3 승급 | — |
| **6-12 Event-Logging** | §4.3 `mcp.quota.warning` / `mcp.quota.exhausted` 이벤트 정의 | — |
| **6-13 Operations 런북** | §3.3 월초 리셋 cron + 쿼터 알림 채널 | §3.6 cron 표현 |
| **다중 인스턴스 VAMOS (Phase 3)** | 쿼터 로컬 카운터 → 공유 카운터 이관 | — |

---

## §8. 본 파일 LOCK 지점 (본 세션 신규)

| # | LOCK 지점 | 섹션 | 변경 조건 |
|---|-----------|------|----------|
| L-SS-1 | `brave-search` 서버 ID 및 도구 2종 네임스페이스 | §3.1 | 상세명세 §D-8 변경 시만 |
| L-SS-2 | `SERVER_RETRY_OVERRIDES["brave-search"]` 6 필드 값 | §3.7 | LOCK-MCP-06 상한 유지 조건 하에 운영 튜닝 가능 |
| L-SS-3 | `BRAVE_API_KEY` 환경 변수명 + `${secrets.BRAVE_API_KEY}` 치환 표현 | §3.2 / §3.6 | R-16-5 변경 시만 |
| L-SS-4 | 쿼터 80% / 95% / 100% 3단계 임계 (400 / 100 / 0) | §3.3 | 상세명세 §H-2 변경 시만 |
| L-SS-5 | 로컬 카운터 저장 키 형식 `brave_search_quota_{YYYY-MM}` | §3.3 / §3.6 | memory_write persistent 스킴 변경 시만 |
| L-SS-6 | **Fallback 체인 순서**: Brave → DuckDuckGo → 내부 `web_search` → `manual_review` | §3.4 | W-NEW-2 대응 변경 시만 |
| L-SS-7 | 월초 리셋 cron `"0 0 1 * *"` (UTC) | §3.6 | — |
| L-SS-8 | AutoConnect=true (LOCK-MCP-08 idle 제외) | §3.1 / §3.5 | R-16-6 변경 시만 |
| L-SS-9 | `recovery{}` 맵 추가 키 `fallback_chain` / `context{}` 맵 추가 키 `quota_remaining` / `priority` | §4.1 | 기존 5+3 키 재정의 금지 (§14.1 L9) |
| L-SS-10 | `mcp.quota.warning` / `mcp.quota.exhausted` 이벤트 이름 | §4.3 | 6-12 Event-Logging 표준 변경 시만 |

### §8.1 변경 프로토콜

1. 후속 세션 보고서에 `[INTERFACE_MISMATCH]` 마커 기재.
2. 본 문서 §8 에 수정 이력 추가 (일자 / 이유 / 영향 세션).
3. 상위 LOCK (LOCK-MCP-01~10) 변경 필요 시 `MCP_SERVER_CLIENT_구조화_종합계획서.md §3.4` 정본 변경 → AUTHORITY_CHAIN 경유.

---

## §9. 검증 요약 (자체)

| 체크 | 결과 | 근거 |
|------|------|------|
| R-16-3 인증/Rate Limit/Fallback 3종 | ✅ | §3.2 / §3.3 / §3.4 = 3 항목 |
| R-16-5 시크릿 환경 변수 참조 | ✅ | `BRAVE_API_KEY` `${secrets.BRAVE_API_KEY}` (§3.2/§3.6) |
| R-16-6 AutoConnect 구분 | ✅ | Brave Search AutoConnect=true (§3.1/§3.5) |
| W-NEW-2 대응 (80%/95%/100% 3단계 + DuckDuckGo 자동 전환) | ✅ | §3.3 / §3.4 전수 정의 |
| LOCK-MCP-06 상한 준수 | ✅ | `max_retries=3 ≤ 3`, `backoff_factor=2.0 == 2.0` (§3.7) |
| LOCK-MCP-07 CB 기본값 | ✅ | 변경 0건 (§3.8) |
| LOCK-MCP-10 Pool 슬롯 | ✅ | 본 파일 1 슬롯 기여 |
| `rate_limit` CB 무영향 (§14.1 L10) | ✅ | §3.3.4 / §3.8 재선언 |
| `McpError` / `ToolInvocationLog` / `EscalationPayload` 재정의 | ✅ 0건 | §4.1 정본 참조만, `context{}`/`recovery{}` 맵 확장만 (§14.1 L9 허용) |
| `retry_circuit_breaker.md §13.1` 예시 값 확정 | ✅ | §3.7 `initial_delay_ms=2000` / `jitter_ratio=0.3` / `total_budget_ms=60000` 그대로 확정 |
| `retry_circuit_breaker.md §14.1 L1~L10` 변경 | ✅ 0건 | §5.1 전수 점검 |
| `retry_circuit_breaker.md §6.3 W-NEW-2 연동 지점` 소비 | ✅ | 쿼터 80% 경고 / DuckDuckGo 자동 전환 모두 §3.3/§3.4 로 이관 |
| Gate P1→2 "외부 서버 3개 연동" 기여 | ✅ 1/3 | 본 파일 1 (Brave Search) + `development_servers.md` 2 (Filesystem, GitHub) = 3 |
| §10 V9 기여 | ✅ 부분 | 11 중 3 완료 (Phase 2/3 에서 나머지 8) |

**완료**: 2026-04-11. D-8 Brave Search 외부 MCP 서버의 L3 DRAFT 연동 상세 작성 — R-16-3 3종 + R-16-5 시크릿 + R-16-6 AutoConnect + **W-NEW-2 쿼터 80% 경고 + DuckDuckGo 자동 전환 Fallback 체인** 전수 정의. `retry_circuit_breaker.md §13.1 SERVER_RETRY_OVERRIDES["brave-search"]` 예시값 확정. `retry_circuit_breaker.md §6.3` 위임 지점 소비 완료. `development_servers.md` 와 합쳐 **Gate P1→2 "외부 서버 3개 연동" 조건 (3/3) 충족**. D-11 Exa 는 Phase 3 스텁으로 보류.
