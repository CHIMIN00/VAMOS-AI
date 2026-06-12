---
tags: [type/concept, tier/all, version/V1, lock/ABSOLUTE]
aliases: [이벤트 로깅, trace_id, 로깅 표준]
created: 2026-06-12
---

# Event Logging Standard (trace_id · JSON · 네이밍)

## 정의
VAMOS 전사 로깅 규약(LOCK): **JSON Structured only(평문 금지) + trace_id 필수**. 모든 이벤트/실패/폴백/상태는 네이밍 규칙으로 충돌 없이 분리된다.

## 이 개념이 등장하는 모든 도메인
- [[T6-Event-Logging]] — 6-12 정본(EventTypeRegistry·Loki, LOCK-EL)
- [[T6-Operations]] — 운영/장애대응의 감사 로그 소비
- [[T6-SDAR]] — sdar.* 이벤트 등록(EventTypeRegistry 통합, CC-006)
- [[T0-Governance]] — 7개 불변 구역 중 audit_format
- 전 도메인 — 모든 Gate 실패는 감사로그 필수

## 값·수치 (LOCK)
- 네이밍: event=**lower.dot** / failure=UPPER_SNAKE / fallback=FB_UPPER_SNAKE / state=S#_ / module=S-#
- 레지스트리: EventTypeRegistry 53+ (oc.i1.*, oc.i2.*, wf.*, ui.*, mem.*, agent.*, sdar.*) / FailureCodeRegistry 20 / FallbackRegistry 13
- config LOCK: `logging.trace_id_required = true`
- 응답 규격: `{success, data/error, trace_id}` (API 88개 공통)

## 버전별 차이
- V1: JSONL + SQLite / V2: PostgreSQL + JSONL (V2-004 마이그레이션) + Loki 준비 / V3: Loki/ELK + Grafana

## 원본 참조
- `D:\VAMOS\CLAUDE.md` §7.4/§16 / `D:\VAMOS\docs\sot 2\6-12_Event-Logging\` (failure_code_registry, AUTHORITY_CHAIN.md)
