---
tags: [tier/T6, module/D-series, status/CORE, version/V1, type/domain, lock/FREEZE]
aliases: [6-9, 브레인 어댑터, Brain-Adapter-HAL]
tier: T6
domain: "6-9 Brain-Adapter-HAL"
sot_source: "D:\\VAMOS\\docs\\sot 2\\6-9_Brain-Adapter-HAL\\"
design_doc: "[[D2.0-04-Infra]]"
quality_gate: "APPROVED (AUTHORITY v1.5, Phase 4 RECOVERY 도메인 종료 2026-06-03) · Content A (S10-5)"
step7_category: "[[STEP7-Implementation-Bridge]]"
version_gate: "V1: Week 1~6 | V2: Week 7~10 | V3: Week 11~14"
created: 2026-06-12
---

# 6-9 Brain-Adapter-HAL

## 한줄 요약
멀티 브레인 어댑터·HAL 추상화·LLM 라우팅·폴백 체인의 정본을 소유하며, 모든 LLM 호출을 단일 인터페이스로 중재하는 Tier 6 인프라 도메인.

## 핵심 정의
- ConnectorResponse 최소 필드 5 + optional 2 (output_text, evidence_summary, cost_used_estimate, warnings, trace_id)
- 폴백 체인 기본: Claude → GPT-4o → DeepSeek → Ollama 로컬 (30s 타임아웃, 최대 2회 전환 후 deny)
- CORE 실행 금지 원칙(판단/제어만), ToolRegistry 경유 필수(직접 URL/SDK 호출 금지)
- 설정 우선순위: ENV > config.yaml/.env > 코드 기본값

## LOCK 항목 (LOCK-69-1~10, 10건)
- 69-1 ConnectorResponse 최소 필드 / 69-2 병렬 태스크 상한 3(V3 승인 상향) / 69-3 ToolRegistry 경유 필수
- 69-4 Gate 결과 Decision 기록 / 69-5 CORE 실행 금지 / 69-6 설정 우선순위 / 69-7 비용 상한 초과 자동 차단
- 69-8 폴백 체인 기본 순서 / 69-9 LangChain import 금지(DEC-002) / 69-10 JSON 구조화 로깅(평문 금지)

## 의존성 (Depends On)
- [[T4-MCP]] — MCP Tool 호출 → ToolRegistry / [[T4-MLOps]] — 드리프트 감지 → 라우팅 가중치 동적 업데이트
- [[T0-Governance]] — R1~R11, LOCK/FREEZE 레지스트리

## 제공 (Provides To)
- [[T1-Verifier-Engines]] — 추론 엔진의 LLM 호출 인터페이스 / [[T6-Hologram]] — Main LLM 2-tier 라우팅 (양방향 B27)
- [[T6-EXP-Modules]] — EVX-3 Log-prob, A-5 Lazy Gen, D-5 Parallel Gen 경유

## 횡단 개념 연결
- [[Failover-Chain-Pattern]] — 폴백 체인 정본(LOCK-69-8) / [[D-Series-Brain-Extensions]] — D-시리즈 호출 경유
- [[VAMOS-Configuration-Framework]] — 설정 우선순위 / [[Cost-Limits]] — 상한 초과 자동 차단

## 관련 모듈 시리즈
- [[MODULE-MAP]] — D-Series/EVX-Series 모듈의 LLM 호출 게이트웨이

## STEP7 매핑
- 출처: D2.0-04 §2-§7 (INFRA_CORE) + Part2 V3-Phase 2 (L3993-4335)

## 버전별 범위
- V1: Week 1~6 기본 어댑터 / V2: Week 7~10 (LiteLLM, Docker Compose) / V3: Week 11~14 (K8s Helm, vLLM)

## 검증 상태
- Quality Gate: APPROVED · Content A — Phase 4 RECOVERY Stage A+B 도메인 종료 (2026-06-03, 4 V3 NEW)
- LOCK 검증: 10/10 일치 (AUTHORITY_CHAIN 실측, Phase 2~4 변경 0건 통산, 6-9↔6-11 cycle EXACT)

## 원본 문서
- SOT 2: D:\VAMOS\docs\sot 2\6-9_Brain-Adapter-HAL\
- Authority: 6-9_Brain-Adapter-HAL\AUTHORITY_CHAIN.md
- Design: [[D2.0-04-Infra]], [[D2.0-02-Orange-Core]] (Runnable 프로토콜)
