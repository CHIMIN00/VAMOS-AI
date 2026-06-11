---
tags: [type/concept, tier/all, module/A-series, version/V1, lock/FREEZE]
aliases: [Failover Chain, 페일오버 체인, Multi-Brain Failover]
created: 2026-06-11
---

# Failover Chain Pattern

## 정의
LLM/도구 장애 시 순차 전환하는 다단계 폴백 패턴. 정본 체인은 **Multi-Brain Failover: GPT-4o → Claude → Ollama** (3회 타임아웃 시 전환, LOCK). I-20 Failure/Fallback Manager와 A-1 MultiBrain Adapter가 실행 주체.

## 이 개념이 등장하는 모든 도메인
- [[T6-Brain-Adapter]] — HAL/Multi-LLM 라우팅 정본(6-9), 체인 실행
- [[T1-Auxiliary-Modules]] — I-20 Failure/Fallback Manager, I-10 Tool Router
- [[T6-Hologram]] — Main LLM 출력 단계의 모델 전환
- [[T4-MCP]] — MCP 재시도/백오프 정책
- [[T6-Operations]] — 장애 대응 운영 절차
- [[T6-SDAR]] — 자동복구 시 폴백 경로 활용

## 값·수치 (LOCK)
- Multi-Brain Failover: GPT-4o→Claude→Ollama, 3회 타임아웃 시 전환(LOCK)
- MCP max_retries: **V1/V2=2, V3=3** — exponential backoff 1s→2s, V3 +4s (D2.0-03·PHASE_B4 §3.9 정본)
- FallbackRegistry 13개: FB_ASK_CLARIFICATION, FB_RAG_*, FB_COST_*, FB_REQUIRE_*, FB_OUTPUT_*, FB_MEMORY_*, FB_ROUTE_*, FB_DENY_*, FB_RESTRICT_*
- 네이밍: fallback=FB_UPPER_SNAKE / failure=UPPER_SNAKE (LOCK)

## 버전별 차이
- V1: Ollama+GPT-4o mini 로컬 중심 / V2: +Sonnet 서버 / V3: vLLM+외부 조합, max_retries=3

## 원본 참조
- `D:\VAMOS\CLAUDE.md` §7.2·§7.4·§16 / `D:\VAMOS\docs\sot\D2.0-04_04. VAMOS_DESIGN_2.0_INFRA_CORE.md` / `D:\VAMOS\docs\sot 2\6-9_Brain-Adapter-HAL\`
