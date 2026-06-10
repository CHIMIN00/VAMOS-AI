# 도구 캐시 런타임 — tools/list_changed 구독 + TTL 1h (V3)

> **도메인**: 4-3 MCP-Server-Client (#16, Tier 4 Infrastructure)
> **Phase**: V3 (Phase 4 production-ready 정본 승급) — P4-3
> **Status**: **APPROVED** (2026-06-03, DRAFT→APPROVED, Phase 4 RECOVERY Stage B genuine write)
> **정본**: sot 2/4-3_MCP-Server-Client/04_payload-schema/tool_cache_runtime.md
> **상속**: P3-3 forward-defined + P2-2 `tool_discovery.md §5` (list_changed + cursor + TTL 1h) 직계 확장
> **LOCK 인용**: LOCK-MCP-04 / LOCK-MCP-09 — verbatim, 재정의 0
> **ReadOnly**: FALSE

---

## §0. 목적

도구 카탈로그 캐시의 **TTL 1h 정책 + `tools/list_changed` notification 구독 + 캐시 적중률 ≥ 90%** 운영을 정본화한다. Phase 2 P2-2 `tool_discovery.md §5`(list_changed + cursor + TTL 1h baseline)의 직계 확장으로, Phase 2 이월 사항(`tools/list_changed` 구독 + 도구 캐시 TTL 1시간)을 production-ready로 해소한다.

---

## §1. 캐시 모델 (TTL 1h)

| 항목 | 값 | 출처 |
|------|-----|------|
| 캐시 단위 | 서버별 도구 카탈로그 (`tools/list` 응답) | `tool_discovery.md §1` |
| TTL | listChanged=false: 1시간 (3600s) / listChanged=true: 알림 구독 후 6시간 (21600s) 연장 | `tool_discovery.md §5.3` (조건부 TTL 정본) |
| 캐시 키 | `cache:mcp:tools:{server_id}` | 서버별 격리 (`tool_discovery.md §5.2` 정본 정합) |
| 무효화 트리거 | TTL 만료 OR `tools/list_changed` 수신 (둘 중 먼저) | R-16-4 |
| 캐시 적중률 목표 | ≥ 90% | G4-5 |
| 멀티 인스턴스 sync | Redis 공유 캐시 (인스턴스 간 일관성) | P4-3 |

---

## §2. tools/list_changed notification 구독 (R-16-4)

```
서버 연결 시 capability 협상 (capability_negotiation.md)
  → tools/list_changed 지원 capability 확인
  → notification 구독 등록
  → 서버 도구 변경 발생
    → tools/list_changed notification 수신
    → 100ms 디바운스 (tool_discovery.md §2, 폭주 방지)
    → 캐시 무효화 (`cache:mcp:tools:{server_id}` DEL)
    → tools/list 재호출 → 캐시 갱신 (cursor 페이지네이션)
    → 멀티 인스턴스 Redis pub/sub 전파 (전 인스턴스 캐시 무효화)
```

> **R-16-4 인용**: "tools/list_changed notification" (`tool_discovery.md §5` + `04_payload-schema/_index.md` #2 정합, 100ms 디바운스).

---

## §3. 캐시 적중률 ≥ 90% 메커니즘

| 메커니즘 | 효과 |
|---------|------|
| TTL 1h 유지 | 변경 빈도 낮은 서버는 1h 동안 캐시 적중 |
| list_changed 즉시 무효화 | stale 캐시로 인한 오류 호출 방지 (정확성 우선) |
| cursor 페이지네이션 캐시 | 대용량 카탈로그도 페이지 단위 캐시 |
| Redis 공유 | 멀티 인스턴스 환경에서 한 인스턴스의 갱신을 전 인스턴스가 공유 → 적중률 상승 |
| 워밍업 | AutoConnect 서버는 부팅 시 캐시 프리페치 |

---

## §4. 캐시 일관성 (멀티 인스턴스)

| 보장 | 메커니즘 |
|------|----------|
| 무효화 전파 | Redis pub/sub 채널 `vamos:mcp:tools:invalidate` |
| 경쟁 갱신 방지 | 갱신 시 분산 락(SETNX + TTL) — 한 인스턴스만 tools/list 재호출, 나머지는 결과 공유 |
| stale 차단 | list_changed 수신 시 전 인스턴스 즉시 무효화 (정확성 우선) |

---

## §5. 횡단 cross-handoff

| 도메인 | 적용 |
|--------|------|
| #3 Blue-Node-Architecture | Bridge 도구 카탈로그 캐시 연계 |
| 6-12 Event-Logging | 캐시 히트/미스/무효화 이벤트 |
| 6-13 Operations | 캐시 적중률 모니터링 표준 |

---

## §6. staging 7일 측정 baseline (forward-defined)

| 측정 항목 | 목표 |
|----------|------|
| 캐시 적중률 | ≥ 90% (7일 평균) |
| list_changed 무효화 지연 | P95 < 100ms (디바운스 포함) |
| 멀티 인스턴스 일관성 | stale 호출 0건 |
| TTL 만료 갱신 latency | P95 < 500ms |

> production 실측은 staging 배포 시점 실계측 위임.

---

## §7. LOCK 정합 요약 (재정의 0)

LOCK-MCP-01 (페이로드 10MB, tools/list 응답 상한) / LOCK-MCP-02 (네임스페이스) / LOCK-MCP-04 (Streamable HTTP) / LOCK-MCP-09 (도구 스키마 정본) verbatim 인용, 재정의 0건. P2-2 `tool_discovery.md §5` 직계 확장 정합 유지. R-16-4 (list_changed) 정합. 31 도구 DEFINED-HERE 무손상.

---

*P4-3 V3 production .md 정본. 3 채널 디스커버리는 `discovery_local_runtime.md` 참조. CLF-MCP-001~005 OPEN 0 inheritance, 신규 CONFLICT 0건.*
