# Exa 쿼터 모니터링 — 1k/day + 사용률 < 80% (V3)

> **도메인**: 4-3 MCP-Server-Client (#16, Tier 4 Infrastructure)
> **Phase**: V3 (Phase 4 production-ready 정본 승급) — P4-1
> **Status**: **APPROVED** (2026-06-03, DRAFT→APPROVED, Phase 4 RECOVERY Stage B genuine write)
> **정본**: sot 2/4-3_MCP-Server-Client/02_external-servers/exa_quota_monitor.md
> **상속**: P3-1 forward-defined — Exa(#11, `exa-mcp-server`, stdio) 외부 11/11 closure 2건 중 2건
> **LOCK 인용**: LOCK-MCP-05 / LOCK-MCP-06 / LOCK-MCP-07 / LOCK-MCP-08 — verbatim 인용, 재정의 0
> **ReadOnly**: FALSE

---

## §0. 목적

Exa MCP 서버(#11, stdio 전송, API Key)는 검색 카테고리 보조 서버로 Brave Search fallback 체인의 중간 단계이다 (`_index.md` Fallback: `Exa → 내부 web_search`). 본 V3는 Exa를 외부 11/11 ALL CONNECTED closure로 승급하고, **일 1k 쿼터 모니터링 + 사용률 < 80%/일 알림 + Brave Search fallback 자동 전환**을 운영 정본으로 영구 확립한다.

이로써 P4-1의 외부 11/11 closure(Sentry + Exa)가 완성된다.

---

## §1. Exa 서버 사양 (baseline 정합)

| 항목 | 값 | 출처 |
|------|-----|------|
| 패키지 | `exa-mcp-server` | `_index.md` #11 |
| 전송 | stdio (공식 패키지 규격, CLF-MCP-005 RESOLVED-DEFERRED stdio 예외 상속) | `_index.md` #11 |
| 인증 | API Key (`${secrets.EXA_API_KEY}`, R-16-5) | `_index.md` 고유 규칙 |
| AutoConnect | ❌ (on-demand, LOCK-MCP-08 idle 10분) | `_index.md` #11 |
| 일 쿼터 (운영) | 1000 req / day | Exa 운영 정책 baseline |
| Fallback | Brave Search → 내부 `web_search` (검색 체인) | `_index.md` Fallback 매핑 |

> **CLF-MCP-005 stdio 예외 상속**: Exa는 공식 `exa-mcp-server` 패키지로 stdio 전송 사용. PHASE_B1 §4 DEC-017 "stdio 제거"는 클라이언트↔Bridge 구간이며, 외부 MCP 서버↔Bridge 구간은 공식 패키지 규격 stdio 허용 (development_servers §5.1 / search_servers §5.1 선례 직계 계승). 본 문서는 stdio 예외 주석을 상속하며 신규 CONFLICT 0건.

---

## §2. 쿼터 모델 (일 1k)

| 항목 | 값 |
|------|-----|
| 일 상한 | 1000 req / day |
| 카운터 키 | `vamos:mcp:exa:quota:daily:{YYYY-MM-DD}` (Redis, TTL 32h) |
| 경고 임계값 | 일 사용률 ≥ 80% (800 req) → Brave/web_search fallback 권고 |
| 차단 임계값 | 일 사용률 ≥ 100% (1000 req) → 내부 `web_search` 강제 전환 |
| 롤오버 | UTC 자정 자동 (TTL 만료) |

Redis 원자 카운터는 `brave_redis_quota.md §2` LUA atomic increment 패턴 동일 적용 (멀티 인스턴스 sync 공유).

---

## §3. 사용률 < 80%/일 알림 + fallback 자동 전환

```
Exa 검색 호출 요청
  → acquire_quota(exa_daily_key) [LUA EVALSHA]
    → 사용률 ≥ 800 (80%) → 경고 이벤트(6-12) + 내부 web_search 전환 권고 (§3.1 체인 단축, Brave 는 상류이므로 재전환 아님)
    → 사용률 ≥ 1000 (100%) → 차단 → 내부 web_search 강제
    → 정상 → Exa 호출 (LOCK-MCP-05 = 5 슬롯 내 on-demand)
```

### §3.1 fallback 체인 (검색 통합)

```
검색 요청
  → Brave Search (#8)  [1차, brave_redis_quota.md 쿼터]
    → Exa (#11)        [Brave 소진/장애 시, Exa 쿼터 < 80% 조건]
      → 내부 web_search [Exa 도 소진/장애 시 최종]
```

Exa는 Brave fallback의 **중간 단계**이자 자체 쿼터를 가지므로, Brave에서 전환된 트래픽이 Exa 일 80%를 밀어올릴 수 있다. 따라서 Exa 80% 도달 시 즉시 내부 `web_search`로 건너뛴다 (체인 단축).

---

## §4. 운영 메트릭 (6-12 Event-Logging 발행)

| 메트릭 | 설명 | 알림 임계값 |
|--------|------|------------|
| `exa.quota.daily.used` | 일 누적 사용량 | ≥ 800 (80%) 경고 |
| `exa.quota.exceeded.count` | 차단 발생 횟수 | ≥ 1 경고 |
| `exa.fallback.websearch.count` | 내부 web_search 전환 횟수 | 추세 모니터링 |
| `exa.latency.p95` | Exa 응답 지연 | P95 > 3s 경고 |
| `exa.cb.state` | Circuit Breaker 상태 | OPEN 전환 시 P2 |

> **LOCK-MCP-07 인용 (verbatim, 재정의 0)**: "Circuit Breaker = 5회 연속 실패 → OPEN, 60초 후 HALF-OPEN, 3회 성공 → CLOSE".

---

## §5. staging 7일 측정 baseline (forward-defined)

| 측정 항목 | 목표 |
|----------|------|
| 일 쿼터 사용률 | < 80% (7일 연속, 정상 트래픽) |
| 80% 도달 시 fallback 전환 | 100% 자동 전환 (수동 개입 0) |
| 멀티 인스턴스 합산 | 일 1000 초과 0건 |
| 검색 체인 latency | Exa P95 < 3s |

> production 실측은 staging 배포 시점 실계측 위임.

---

## §6. LOCK 정합 요약 (재정의 0)

LOCK-MCP-05 (5 슬롯) / LOCK-MCP-06 (재시도) / LOCK-MCP-07 (CB) / LOCK-MCP-08 (idle 10분) verbatim 인용, 재정의 0건. 31 도구 DEFINED-HERE 무손상. R-16-3 (인증/Rate Limit/Fallback 3종) Exa 전수 정합.

---

*P4-1 V3 production .md 정본. 외부 11/11 ALL CONNECTED closure 완성 (P1 3 + P2 6 + P3/P4 2 = Filesystem/GitHub/Brave/Slack/gdrive/Notion/Linear/Postgres/Puppeteer/Sentry/Exa). CLF-MCP-005 stdio 예외 상속, 신규 CONFLICT 0건.*
