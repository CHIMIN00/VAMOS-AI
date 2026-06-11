---
tags: [tier/T4, status/CORE, version/V1, type/domain, lock/FREEZE, lock/DEFINED-HERE]
aliases: [4-1, 러스트-타우리 인프라, Rust-Tauri-Infrastructure]
tier: T4
domain: "4-1 Rust-Tauri-Infrastructure"
sot_source: "D:\\VAMOS\\docs\\sot 2\\4-1_Rust-Tauri-Infrastructure\\"
design_doc: "[[D2.0-04-Infra]]"
quality_gate: "APPROVED — Phase 4 RECOVERY 도메인 종료 (§12 SILVER, 2026-06-03)"
step7_category: "[[STEP7-Implementation-Bridge]]"
version_gate: "V1: P0 GATE PASS → P1 | V2: build-signing/IPC §V2 19 EXTEND | V3: 3 L3 production 승급"
created: 2026-06-11
---

# 4-1 Rust-Tauri-Infrastructure

## 한줄 요약
Tauri(Rust) 데스크톱 셸과 Python 엔진을 잇는 IPC 72커맨드·JSON-RPC 13메서드·프로세스 관리의 인프라 정본 도메인.

## 핵심 정의
- IPC 커맨드 72개 (`vamos:{category}:{action}`), 카테고리 배분 Core 15 / Agent 15 / Storage 18 / Safety 19 / UI 5
- JSON-RPC 2.0 stdin/stdout 통신: langgraph.*(5) + embedding.*(2) + llm.*(3) + mcp.*(3) = 13 메서드
- Rust 핵심 모듈 4개: ipc_protocol.rs / python_manager.rs / config.rs / serde 모델 25개
- 권한 체인: BASE 1.3 → PLAN 3.0 → D2.0-04 → D2.1-D2/D3/D4 (REF-only) → PHASE_B1/B2 → Part2 §6.2 → sot 2 상세명세(DEFINED-HERE)

## LOCK 항목 (LOCK-RT-01~15, 15건)
- RT-01 IPC 72개 이름 / RT-02 카테고리 배분 15·15·18·19·5 / RT-03 JSON-RPC 13 메서드명 / RT-04 Rust 모듈 4개
- RT-05 D2.1 스키마 14 Schema+3 Registry / RT-06 EventTypeRegistry 134건 / RT-07 FailureCodeRegistry 48건 / RT-08 FallbackRegistry 35건 (6-12 정본 REF-only)
- RT-09 ToolRegistry 엔트리 구조 / RT-10 NodeRegistry 엔트리 구조
- RT-11 JSON-RPC 2.0 `\n` 구분 / RT-12 헬스체크 15s·5s·3회 (DEFINED-HERE) / RT-13 Restart backoff 1→2→4→8→16s (DEFINED-HERE)
- RT-14 TauriError enum 7 variant (DEFINED-HERE) / RT-15 stdout=JSON-RPC·stderr=로그 분리

## 의존성 (Depends On)
- [[T6-Security]] — IPC 보안·Python Bridge 인증 / [[T6-Event-Logging]] — IPC 이벤트 버스 표준
- [[T6-Operations]] — 헬스체크·롤백·모니터링 표준 / [[T0-Governance]] — R1~R11

## 제공 (Provides To)
- [[T2-Blue-Node]] — IPC 계층(CORE↔NODE 통신) / [[T6-UI-UX]] — IPC 백엔드 72 commands
- [[T6-Cloud-Library]] — E-15 Cloud Collector IPC / [[T6-Hologram]] — IPC/Tauri 인프라
- [[T3-Business-Model]] — 인프라 비용→가격 원가 / [[T4-CICD]] — Tauri 빌드 설정 (양방향)

## 횡단 개념 연결
- [[VAMOS-Configuration-Framework]] — config.rs TOML 로드 / [[Event-Logging-Standard]] — Registry 134/48/35 소비
- [[VAMOS-Authority-Chain]] — REF-only/DEFINED-HERE 구분

## STEP7 매핑
- 출처: PHASE_B1(IPC 72 정본) + PHASE_B2(Python bridge 정본) + Part2 §6.2 (PARTIAL)

## 버전별 범위
- V1: IPC 72 시그니처·25 Serde 모델·13 JSON-RPC 스키마 / V2: build-signing 2 NEW + 13 IPC §V2 EXTEND (~2,470L) / V3: 3 L3(session/method_catalog/spawn) DRAFT→APPROVED 메타 승급형

## 검증 상태
- Quality Gate: APPROVED — Phase 4 RECOVERY §12 SILVER (2026-06-03, Wave 3 #20)
- LOCK 검증: 15/15 일치 (AUTHORITY_CHAIN v1.9, 재정의 0 + DEFINED-HERE 4종 동결)

## 원본 문서
- SOT 2: D:\VAMOS\docs\sot 2\4-1_Rust-Tauri-Infrastructure\
- Authority: 4-1_Rust-Tauri-Infrastructure\AUTHORITY_CHAIN.md (v1.9)
- Design: [[D2.0-04-Infra]], [[D2.1-Schema-Index]] (D2/D3/D4 REF-only)
