---
tags: [tier/T6, module/I-series, status/CORE, version/V2, type/domain, lock/FREEZE, lock/DEFINED-HERE, responsible-ai]
aliases: [6-5, SDAR 시스템, SDAR-System, Self-Diagnosis and Auto-Repair, A16]
tier: T6
domain: "6-5 SDAR-System"
sot_source: "D:\\VAMOS\\docs\\sot 2\\6-5_SDAR-System\\"
design_doc: "[[SPEC-SDAR]]"
quality_gate: "APPROVED (AUTHORITY v1.5, Phase 4 verify-only genuine 확정 2026-06-02)"
step7_category: "[[STEP7-Implementation-Bridge]]"
version_gate: "V1: OFF | V2: V2-P2 ON | V3: V3-P2 확장"
created: 2026-06-12
---

# 6-5 SDAR-System

## 한줄 요약
5-Layer 자가진단·자동수리 파이프라인(Detection→Verification)과 7-State 머신, AR-Level 자율수리 등급의 정본을 소유하는 Tier 6 도메인 (I-25, Responsible AI: A16).

## 핵심 정의
- 5-Layer: Detection → Diagnosis → Prescription → Repair → Verification
- 7-State: IDLE→DETECTING→DIAGNOSING→PRESCRIBING→REPAIRING→VERIFYING→IDLE (실패 시 ESCALATED)
- AR-Level: L0(0)→L1(2)→L2(5)→L3(5)→L4(4) + NEVER(10), SDAR 전용 5-Gate (Policy/Evidence/Cost/Approval/SelfCheck)
- I-25 공식 명칭 = "Self-Diagnosis and Auto-Repair" (SC-08 결정, SDAR_SPEC 채택)

## LOCK 항목 (L1~L20, 20건 + DH-SDAR-T1 등 DEFINED-HERE)
- L1 5-Layer / L2 7-State / L3 5-Gate / L4 AR-Level / L5 동시 수리 최대 1 / L6 동일 이슈 시간당 3회
- L7 동시 인스턴스 3 / L8 스냅샷 필수(MEDIUM/HIGH) / L9 알림 필수 / L10 승인 타임아웃 600초
- L11 관찰 300초 / L12 롤백 타임아웃 300초 / L13 쿨다운 60초 / L14 Kill Switch / L15 CATEGORY E 자동수리 절대 금지(5규칙)
- L16 P2 수리 인간 승인 필수 / L17 비용 상한 내 수리(일일 10% 초과 시 승인) / L18 Self-evo 자동 적용 금지
- L19 NEVER_AUTO 10항목(불변구역 7+운영금지 3) / L20 Gate 코드 공유 BaseGate(ABC)

## 의존성 (Depends On)
- [[T6-Security]] — STRIDE 위협→SDAR 트리거 (양방향 B14) / [[T6-Memory-RAG]] — 메모리 상태 보고 (양방향 B18)
- [[T6-Event-Logging]] — sdar.* 이벤트+FailureCode 레지스트리 / [[T6-Operations]] — SDAR OFF 수동 폴백 절차
- [[T1-Auxiliary-Modules]] — BaseGate(ABC) 인터페이스 (양방향 B26) / [[T6-Self-Evolution]] — S-3 전략 제안→카탈로그 (양방향 B19)

## 제공 (Provides To)
- [[T6-Self-Evolution]] — repair_result → S-2 Pattern Miner (양방향 B19)
- [[T1-Auxiliary-Modules]] — I-25 SDAR 모듈 (양방향 B26)

## 횡단 개념 연결
- [[SDAR-Emergency-Response]] — Kill Switch·CATEGORY E 정본 / [[5-Gate-Decision-Framework]] — SDAR 전용 5-Gate 변형
- [[Failover-Chain-Pattern]] — 수리 실패 시 에스컬레이션

## 관련 모듈 시리즈
- [[MODULE-MAP]] — I-25 (Self-Diagnosis and Auto-Repair) 정본 소유

## STEP7 매핑
- 출처: SDAR_SPEC (VAMOS_SDAR_DESIGN_SPECIFICATION) + Part2 §6.9 (L5397-L5509)

## 버전별 범위
- V1: OFF / V2: V2-P2 ON / V3: V3-P2 확장 (circuit_breaker_v3 W-CB Option C)

## 검증 상태
- Quality Gate: APPROVED (Phase 4 Stage A+B verify-only genuine 확정, 회수 불필요 2026-06-02)
- LOCK 검증: 20/20 일치 (AUTHORITY_CHAIN §4 실측, XREF-01/02 교정 반영) / Responsible AI 지정: A16

## 원본 문서
- SOT 2: D:\VAMOS\docs\sot 2\6-5_SDAR-System\
- Authority: 6-5_SDAR-System\AUTHORITY_CHAIN.md
- Design: [[SPEC-SDAR]], [[D2.0-02-Orange-Core]] (§7 I-25)
