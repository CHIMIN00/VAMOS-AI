# Brave Search 쿼터 공유 Redis 카운터 — 멀티 인스턴스 sync (V3)

> **도메인**: 4-3 MCP-Server-Client (#16, Tier 4 Infrastructure)
> **Phase**: V3 (Phase 4 production-ready 정본 승급) — P4-1
> **Status**: **APPROVED** (2026-06-03, DRAFT→APPROVED, Phase 4 RECOVERY Stage B genuine write)
> **정본**: sot 2/4-3_MCP-Server-Client/02_external-servers/brave_redis_quota.md
> **상속**: P3-1 forward-defined + P2-2 이월(d) "다중 인스턴스 Brave 쿼터 공유 카운터(Redis 기반)" 해소
> **LOCK 인용**: LOCK-MCP-05 (maxConcurrentServers=5) / LOCK-MCP-06 (재시도 max 3) / LOCK-MCP-07 (CB 5/60s/3) — verbatim 인용, 재정의 0
> **ReadOnly**: FALSE (Production 승급 직접 편집 가능)

---

## §0. 목적

Brave Search MCP 서버(#8, `@modelcontextprotocol/server-brave-search`)는 무료 티어 **2000/month** Rate Limit을 가진다 (`02_external-servers/_index.md` #8 정합). VAMOS가 멀티 인스턴스(다중 Tauri 프로세스 / 다중 워커)로 배포될 때, 각 인스턴스가 독립 로컬 카운터를 가지면 합산 쿼터가 월 상한을 초과한다. 본 문서는 **Redis 기반 공유 원자적(atomic) 쿼터 카운터**로 모든 인스턴스가 단일 쿼터 풀을 공유하도록 하는 운영 정본을 확립한다.

이는 Phase 2 P2-2 이월 사항 (d) "다중 인스턴스 Brave 쿼터 공유 카운터(Redis 기반)"의 **해소**이다.

---

## §1. 쿼터 모델

| 항목 | 값 | 출처 |
|------|-----|------|
| 무료 티어 월 상한 | 2000 req / month | Brave API free plan (`_index.md` #8) |
| 일 소프트 상한 (운영) | `ceil(2000 / 30) = 67 req/day` | 월 상한 균등 분배 + burst 허용 |
| 경고 임계값 | 월 사용률 ≥ 80% (1600 req) | Exa fallback 자동 전환 트리거 |
| 차단 임계값 | 월 사용률 ≥ 100% (2000 req) | 내부 `web_search` fallback 전환 |
| 카운터 키 | `vamos:mcp:brave:quota:{YYYY-MM}` | 월 단위 롤오버 |
| 일 카운터 키 | `vamos:mcp:brave:quota:daily:{YYYY-MM-DD}` | 일 모니터링 |

> 월 키는 자연 월 경계(UTC)에서 자동 롤오버되며, TTL은 32일로 설정하여 롤오버 후 자동 만료된다.

---

## §2. 원자적 증가 (Redis SETNX + LUA atomic increment)

다중 인스턴스 동시 호출에서 race condition 없이 카운터를 증가시키고 상한을 검사하기 위해 **단일 LUA script**로 "검사 + 증가"를 원자적으로 수행한다.

```lua
-- KEYS[1] = monthly key, KEYS[2] = daily key
-- ARGV[1] = monthly limit (2000), ARGV[2] = monthly TTL (sec), ARGV[3] = daily TTL (sec)
local cur = tonumber(redis.call('GET', KEYS[1]) or '0')
if cur >= tonumber(ARGV[1]) then
  return {-1, cur}            -- 차단: 상한 도달
end
local newval = redis.call('INCR', KEYS[1])
if newval == 1 then
  redis.call('EXPIRE', KEYS[1], ARGV[2])   -- 최초 생성 시에만 TTL 부여 (SETNX 등가)
end
local dnew = redis.call('INCR', KEYS[2])
if dnew == 1 then
  redis.call('EXPIRE', KEYS[2], ARGV[3])
end
return {newval, dnew}         -- 허용: 증가 후 월/일 카운트 반환
```

**원자성 보장**: Redis는 LUA script를 단일 atomic 단위로 실행하므로, N개 인스턴스가 동시에 호출해도 `GET → 비교 → INCR` 사이에 다른 인스턴스가 끼어들 수 없다. 이것이 로컬 카운터가 합산 초과를 일으키는 문제의 근본 해결이다.

### §2.1 클라이언트 호출 흐름

```
Brave Search 도구 호출 요청
  → acquire_quota(monthly_key, daily_key) [LUA EVALSHA]
    → return[0] == -1  → QuotaExceeded → §4 fallback 체인
    → return[0] >= 1600 (80%) → 경고 이벤트 발행(6-12) + Exa fallback 권고
    → 정상 → Brave Search 서버 호출 (LOCK-MCP-05 = 5 슬롯 내 회전)
```

---

## §3. 멀티 인스턴스 sync 보장

| 보장 | 메커니즘 |
|------|----------|
| 단일 쿼터 풀 | 모든 인스턴스가 동일 Redis 키 `vamos:mcp:brave:quota:{YYYY-MM}` 참조 |
| 원자적 증가 | LUA script 단일 atomic 실행 (§2) |
| 네트워크 분할 내성 | Redis 연결 실패 시 **보수적 차단**(fail-closed) — 로컬 폴백 카운터로 인스턴스당 `floor(67 / MAX_INSTANCES)` (최소 보수 버스트, 기본 MAX_INSTANCES 가정 시 ≤ 10/day) 임시 상한 적용 → 전 인스턴스 합산이 월 2000 상한을 초과하지 않도록 보장 → 재연결 시 월 키로 reconcile |
| 시계 동기화 비의존 | 키는 UTC 월/일 문자열 기반, 인스턴스 로컬 시계 drift 영향 최소화 |
| 재시도 정책 | Redis 명령 실패 시 LOCK-MCP-06 (재시도 max 3, 지수 백오프 factor 2.0) 적용 |

> **LOCK-MCP-06 인용 (verbatim, 재정의 0)**: "재시도 정책 = max 3회, 지수 백오프 (factor 2.0)" (AUTHORITY §4 / 상세명세 §B-3).

---

## §4. Fallback 체인 (쿼터 소진 시)

`_index.md` Fallback 매핑 정합:

```
Brave Search (쿼터 소진/장애)
  → Exa (#11)            [월 80% 도달 시 우선 전환, Exa 쿼터 < 80% 조건]
    → 내부 web_search    [Exa 도 소진/장애 시 최종 fallback]
```

- Exa 자체 쿼터(1k/day)도 80% 초과 시 즉시 내부 `web_search`로 전환 (`exa_quota_monitor.md` 정합).
- Circuit Breaker (LOCK-MCP-07) 적용: Brave 서버 5회 연속 실패 → OPEN(60초) → fallback 강제, 60초 후 HALF-OPEN 3회 성공 → CLOSE.

> **LOCK-MCP-07 인용 (verbatim, 재정의 0)**: "Circuit Breaker = 5회 연속 실패 → OPEN, 60초 후 HALF-OPEN, 3회 성공 → CLOSE" (AUTHORITY §4 / 상세명세 §B-3).

---

## §5. 운영 메트릭 (6-12 Event-Logging 발행)

| 메트릭 | 설명 | 알림 임계값 |
|--------|------|------------|
| `brave.quota.monthly.used` | 월 누적 사용량 | ≥ 1600 (80%) 경고 |
| `brave.quota.daily.used` | 일 누적 사용량 | ≥ 67 (소프트 상한) 정보 |
| `brave.quota.exceeded.count` | 차단 발생 횟수 | ≥ 1 경고 |
| `brave.fallback.exa.count` | Exa fallback 전환 횟수 | 추세 모니터링 |
| `brave.redis.sync.error` | Redis 동기화 실패 | ≥ 1 경고 (fail-closed 발동) |

이벤트 표준은 6-12 Event-Logging §9.3 횡단 참조 정합. 운영 알림 채널은 6-13 Operations 매핑.

---

## §6. staging 7일 측정 baseline (forward-defined)

| 측정 항목 | 목표 baseline |
|----------|--------------|
| 멀티 인스턴스 합산 쿼터 정합 | 월 상한 2000 초과 0건 (3 인스턴스 동시 부하) |
| LUA atomic 경합 | race condition 0건 (1000 동시 호출 테스트) |
| Redis sync 지연 | P95 < 5ms |
| fail-closed 복구 | Redis 재연결 후 reconcile 오차 ≤ 인스턴스 수 × 1 |

> production 실측은 staging 배포 시점 실계측 위임. 본 문서는 운영 정본 명세를 확립한다.

---

## §7. LOCK 정합 요약 (재정의 0)

| LOCK | 값 | 본 문서 적용 |
|------|-----|------------|
| LOCK-MCP-05 | maxConcurrentServers=5 | Brave on-demand 슬롯 5 내 회전 |
| LOCK-MCP-06 | 재시도 max 3, factor 2.0 | Redis 명령 + Brave 호출 재시도 |
| LOCK-MCP-07 | CB 5/60s/3 | Brave 서버 장애 시 fallback 강제 |

LOCK-MCP-01~10 verbatim 영구 보존 (R9), 재정의 0건. 31 도구 DEFINED-HERE 정본 무손상.

---

*P4-1 V3 production .md 정본. CLF-MCP-001~005 OPEN 0 inheritance. 본 문서 작성 중 신규 CONFLICT 0건.*
