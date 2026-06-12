---
tags: [tier/T6, module/E-series, status/CORE, version/V1, type/domain, lock/FREEZE, lock/DEFINED-HERE]
aliases: [6-7, 실시간 속보 파이프라인, RT-BNP-DCL, Real-Time Breaking News Pipeline]
tier: T6
domain: "6-7 RT-BNP-DCL"
sot_source: "D:\\VAMOS\\docs\\sot 2\\6-7_RT-BNP-DCL\\"
design_doc: "[[SPEC-Cloud-Library]]"
quality_gate: "APPROVED — Phase 7 FINAL PASS · Content A- (S10-3), Phase 4 RECOVERY 종료 2026-06-02"
step7_category: "[[STEP7-Implementation-Bridge]]"
version_gate: "V1: RSS 60s | V2: API 30s | V3: WebSocket"
created: 2026-06-12
---

# 6-7 RT-BNP-DCL

## 한줄 요약
실시간 속보 파이프라인(RT-BNP: 수집→감지→Fast Gate→전파)과 도메인 컨텍스트 레이어(DCL 3채널)의 정본을 소유하는 Tier 6 도메인.

## 핵심 정의
- 파이프라인: Sources → RT Collector → Breaking Detector → Fast Gate → Kafka → EventBus
- 소스 Tier 4단계: T1(<10s WebSocket) / T2(<60s REST) / T3(<300s RSS) / T4(<600s SNS)
- Breaking Event 4등급: BREAKING-P0/P1/P2/NORMAL, P0 전파 최대 지연 30초
- DCL 3채널: DCL-FIN(금융) / DCL-TECH(기술) / DCL-GEO(지정학), QoD ≥ 0.5 → RAG 삽입

## LOCK 항목 (L1~L18, 18건 + DH-1~5)
- L1 파이프라인 아키텍처 / L2 소스 Tier 4단계 / L3 Breaking 4등급 / L4 Fast Gate 적용 규칙(CL-G0~G4 선택 적용)
- L5 소스 가중치(공식 1.0~SNS 0.4) / L6 P0 전파 지연 30초 / L7 사후 검증 30분 / L8 허위 속보 RETRACTION 즉시
- L9 중복 억제 5분 윈도우 / L10 동시 연결 V2:10/V3:30 / L11 DCL 6계층 정보 환경 / L12 DCL 3채널
- L13 QoD ≥ 0.5 / L14 배경 요약 1시간 갱신 / L15 DCL 비용 상한(V2 +₩5,000/V3 +₩15,000) / L16 CL-G3 보안 필수
- L17 Fast Gate ↔ VAMOS 5-Gate 분리(BaseGate만 공유) / L18 사후 검증 실패 시 RETRACTION

## 의존성 (Depends On)
- [[T6-Cloud-Library]] — Fast Gate(CL-G0~G4) 로직·배치 파이프라인 + LOCK #1~13 준수 (양방향 B20)
- [[T6-Operations]] — RT-BNP 소스 장애 대응 운영 절차

## 제공 (Provides To)
- [[AI-Investing-Overview]] — 속보 → 전략 재평가 / [[T6-Cloud-Library]] — Fast Gate 공유·소스 가중치 (양방향 B20)

## 횡단 개념 연결
- [[Failover-Chain-Pattern]] — 소스 장애·RETRACTION 폴백 / [[RAG-Pipeline]] — DCL QoD≥0.5 RAG 삽입
- [[Event-Logging-Standard]] — bnp.* 이벤트 발행

## 관련 모듈 시리즈
- [[MODULE-MAP]] — E-15 Cloud Collector 인프라(6-8) 연계 데이터 흐름 담당

## STEP7 매핑
- 출처: CLOUD_LIBRARY_SPEC (관련 인프라) + Part2 §6.10.1/§6.10.2 (L5572-L5741)

## 버전별 범위
- V1: RSS 60s 기본 / V2: API 30s + DCL 채널 확장 / V3: WebSocket 실시간

## 검증 상태
- Quality Gate: APPROVED — Content A- / Phase 4 RECOVERY genuine write 도메인 종료 (2026-06-02, retraction_protocol V3 NEW)
- LOCK 검증: 18/18 일치 (AUTHORITY_CHAIN §3 실측, 불일치 0건) + DH-1~5

## 원본 문서
- SOT 2: D:\VAMOS\docs\sot 2\6-7_RT-BNP-DCL\
- Authority: 6-7_RT-BNP-DCL\AUTHORITY_CHAIN.md
- Design: [[SPEC-Cloud-Library]] (관련 인프라)
