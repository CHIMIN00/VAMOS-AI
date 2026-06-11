---
tags: [tier/T1, module/C-series, module/D-series, status/CORE, version/V1, type/domain, lock/FREEZE]
aliases: [1-1, 검증·추론 엔진, Verifier-Reasoning-Engines]
tier: T1
domain: "1-1 Verifier-Reasoning-Engines"
sot_source: "D:\\VAMOS\\docs\\sot 2\\1-1_Verifier-Reasoning-Engines\\"
design_doc: "[[D2.0-02-Orange-Core]]"
quality_gate: "APPROVED — Phase 5 FINAL PASS / Phase 4 RECOVERY 완료"
step7_category: "[[STEP7-Implementation-Bridge]]"
version_gate: "V1: P0~P1 | V2: P2 | V3: P3"
created: 2026-06-11
---

# 1-1 Verifier-Reasoning-Engines

## 한줄 요약
ORANGE CORE 내부의 검증 엔진(C-1~C-3)과 추론 엔진(D-1~D-2) 5개를 L3 구현 정본으로 관리하는 Tier 1 핵심 지능 도메인.

## 핵심 정의
- 5개 엔진: Logic Verifier(C-1) / Math Verifier(C-2) / Code Verifier(C-3) / Think Engine(D-1) / Multimodal Engine(D-2)
- 표준 5-stage 파이프라인: Perception→Reasoning→Action→Memory→Reflection
- Confidence 판정: ≥0.8 PASS, 0.5~0.8 REVIEW, <0.5 FAIL
- 권한 체인: D2.0-01 §5.11/§5.12 + D2.0-02 §2/§7 LOCK → sot 2/1-1 구현 정본(What+How)

## LOCK 항목 (LOCK-VR-01~15, 15건)
- VR-01 Self-check 임계값 P0≥70/P1≥75/P2≥80 / VR-02 Soft Loop Auto 1회만
- VR-03 5-stage 파이프라인 / VR-04 상태 머신 S0~S8 (S3 Decision Lock immutable)
- VR-05 Confidence ≥0.8 PASS / VR-06 Verify Chain Default OFF+timeboxed
- VR-07 Failover Chain GPT-4o→Claude Sonnet→Ollama / VR-08 tiktoken 표준
- VR-09 게이트 우선순위 policy>cost>evidence / VR-10 S3 이후 결론 불변
- VR-11 ABC 엔진 인터페이스 계약 / VR-12 응답시간 단일≤2s·복합≤10s·Self-check≤1s
- VR-13 C-Series CORE V1:ON / VR-14 D-Series CORE V1:ON / VR-15 C-3 Docker 샌드박스 timeout 30s

## 의존성 (Depends On)
- [[T0-Governance]] — R1~R11 규칙 / [[T6-Security]] — OWASP LLM01/02 체크리스트
- [[T6-Memory-RAG]] — L2 지식 검색 / [[T6-Brain-Adapter]] — LLM 라우팅
- [[T6-Event-Logging]] — oc.i1~i5 이벤트 표준 / [[T6-Agent-Teams]] — Research/Critic Agent 호출

## 제공 (Provides To)
- [[T3-Dev-Tools]] — LLM 추론 결과 검증 / [[T3-Agent-Protocol]] — 가드레일 안전성 검증
- [[T5-File-Context]] — LLM 윈도우·능력 기반 / [[T6-EXP-Modules]] — C-시리즈 모듈 관리

## 횡단 개념 연결
- [[C-Series-Verifiers]] / [[D-Series-Brain-Extensions]] — 엔진 정본
- [[Decision-Lock]] — S3 immutability / [[Failover-Chain-Pattern]] — LLM 폴백
- [[Self-Check-Loop]] — Soft loop 1회 규칙 / [[5-Gate-Decision-Framework]] — 게이트 우선순위

## 관련 모듈 시리즈
- [[MODULE-MAP]] — C-1/C-2/C-3 (CORE, V1:ON), D-1/D-2 (CORE, V1:ON, ui_exposed=false)

## STEP7 매핑
- 출처: Part2 V1-Phase 3 (L2140~2147, When+Where 구현 가이드)

## 버전별 범위
- V1: P0~P1 (5개 엔진 기본) / V2: P2 (performance_benchmark·integration_test 16 산출물) / V3: P3

## 검증 상태
- Quality Gate: APPROVED (Phase 5 FINAL PASS, Phase 4 RECOVERY Sub-A+B 완료 2026-06-02)
- LOCK 검증: 15/15 일치 (AUTHORITY_CHAIN v1.4 §3.4 immutable matrix)

## 원본 문서
- SOT 2: D:\VAMOS\docs\sot 2\1-1_Verifier-Reasoning-Engines\
- Authority: 1-1_Verifier-Reasoning-Engines\AUTHORITY_CHAIN.md (v1.4)
- Design: [[D2.0-01-Overview]] §5.11/§5.12, [[D2.0-02-Orange-Core]] §2/§7
