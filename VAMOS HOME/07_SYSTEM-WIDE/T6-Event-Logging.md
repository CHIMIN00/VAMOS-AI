---
tags: [tier/T6, module/I-series, status/CORE, version/V1, type/domain, lock/FREEZE]
aliases: [6-12, 이벤트 로깅, Event-Logging]
tier: T6
domain: "6-12 Event-Logging"
sot_source: "D:\\VAMOS\\docs\\sot 2\\6-12_Event-Logging\\"
design_doc: "[[D2.1-Schema-Index]]"
quality_gate: "APPROVED (AUTHORITY v1.5, Phase 4 RECOVERY 도메인 종료 2026-06-03)"
step7_category: "[[STEP7-Implementation-Bridge]]"
version_gate: "V1: P1 기본 | V2: P2 분산 | V3: P3 Loki"
created: 2026-06-12
---

# 6-12 Event-Logging

## 한줄 요약
EventType/FailureCode/Fallback 3대 레지스트리와 이벤트 스키마·네임스페이스·추적 컨텍스트 표준의 정본을 소유하는 Tier 6 횡단 로깅 도메인.

## 핵심 정의
- 3대 레지스트리: EventTypeRegistry 134항목(123+11) / FailureCodeRegistry 48항목(36+12) / FallbackRegistry 35항목(23+12)
- 이벤트 스키마 필수 필드 6: timestamp, event_type, trace_id, source, version, payload
- 네임스페이스: oc.* / cl.rt.* / agent.* / sdar.* / storage.* / mem.* / wf.* / ui.*
- FC→FB 매핑 정본 = Part2 §6.9 선언, 9-State↔UI↔이벤트 매핑 테이블

## LOCK 항목 (LOCK-EL-01~10, 10건)
- EL-01 이벤트 스키마 필수 필드 6 / EL-02 EventTypeRegistry 134 / EL-03 FailureCodeRegistry 48
- EL-04 FallbackRegistry 35 / EL-05 FC→FB 매핑 정본(Part2 §6.9) / EL-06 NEVER_AUTO 대상 코드 3종
- EL-07 로깅 레벨 5단계(DEBUG~CRITICAL) / EL-08 W3C Trace Context 호환+correlation_id 필수 전파
- EL-09 이벤트 네임스페이스 8종 / EL-10 9-State↔UI↔이벤트 매핑

## 의존성 (Depends On)
- [[T6-Memory-RAG]] — 메모리 감사 로그 입력 / [[T6-Operations]] — 로그 보존 정책 (양방향 B21)
- [[T6-Security]] — 보안 이벤트 정의 (양방향 B15)

## 제공 (Provides To)
- [[T1-Verifier-Engines]] — oc.i1~i5 퍼블리싱 표준 / [[T2-Blue-Node]] — BLUE NODE 이벤트 네임스페이스
- [[T2-COND-Modules]] — COND FailureCode (COND_*) / [[T3-Dev-Tools]] — 로깅 표준 / [[T4-Rust-Tauri]] — IPC 이벤트 버스
- [[T4-MCP]] — MCP 통신 이벤트 / [[T6-UI-UX]] — ui.builder.* / [[T6-Agent-Teams]] — agent.*
- [[T6-SDAR]] — sdar.* + FailureCode / [[T6-Cloud-Library]] — cl.rt.* / [[T6-Operations]] — 운영 모니터링/알림

## 횡단 개념 연결
- [[Event-Logging-Standard]] — 본 도메인이 정본 / [[Failover-Chain-Pattern]] — FC→FB 매핑
- [[Cross-Domain-Terminology]] — 네임스페이스 일관성

## 관련 모듈 시리즈
- [[MODULE-MAP]] — I-9 로그 모듈 발행 표준 연계

## STEP7 매핑
- 출처: Part2 §6.11 (L5788-5975) + D2.1-D2 (3대 레지스트리 정본)

## 버전별 범위
- V1: P1 기본 로깅 / V2: P2 분산 추적 / V3: P3 Loki + Grafana/Alertmanager (V3 FC 4건 EXP_*)

## 검증 상태
- Quality Gate: APPROVED — Phase 4 RECOVERY 도메인 종료 (2026-06-03, V3 NEW 3 + EXTEND 3, Tier 6 11/11 종결)
- LOCK 검증: 10/10 일치 (AUTHORITY_CHAIN v1.5 실측, 변경 0건 통산, 100% distinct 인용)

## 원본 문서
- SOT 2: D:\VAMOS\docs\sot 2\6-12_Event-Logging\
- Authority: 6-12_Event-Logging\AUTHORITY_CHAIN.md
- Design: [[D2.1-Schema-Index]] (D2 레지스트리 정본)
