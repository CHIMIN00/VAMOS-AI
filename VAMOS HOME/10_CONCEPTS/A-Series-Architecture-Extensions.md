---
tags: [type/concept, tier/all, module/A-series, version/V3, lock/FREEZE]
aliases: [A-Series, 아키텍처 확장, A1~A7]
created: 2026-06-12
---

# A-Series: Architecture Extensions (A-1~A-7)

## 정의
시스템 구조 자체를 확장하는 아키텍처 확장 모듈 7개. CORE 2(A-1·A-2, V1 ON) + EXP 5(V3 중심). Named 81개 모듈(I25+E16+S8+A7+B6+C7+D6+EVX6) 중 A 시리즈.

| ID | 명칭 | V1 | V2 | V3 |
|---|---|---|---|---|
| A-1 | MultiBrain Adapter | ON | ON | ON |
| A-2 | Preset Modularization | ON | ON | ON |
| A-3 | Meta AI | OFF | OFF | ON |
| A-4 | Debate Mode | OFF | COND | ON |
| A-5 | Lazy Generation | OFF | OFF | ON |
| A-6 | Federated Module Network (LOCK) | OFF | OFF | ON |
| A-7 | Remote Executor (LOCK) | OFF | OFF | ON |

## 이 개념이 등장하는 모든 도메인
- [[T6-Brain-Adapter]] — A-1 MultiBrain Adapter 실행 정본 (HAL, Multi-LLM 라우팅)
- [[T6-Agent-Teams]] — A-4 Debate Mode가 협업 패턴 Debate와 연동
- [[T3-Agent-Protocol]] — A-6 Federated / A-7 Remote Executor 상호운용·승인 체계
- [[T6-EXP-Modules]] — EXP status 모듈(A-3~A-7)의 V3 활성 기준 관리

## 값·수치 (LOCK)
- **A-6 = Federated Module Network (LOCK), A-7 = Remote Executor (LOCK)** — CLAUDE.md §7.1
- Multi-Brain Failover (LOCK §7.2): GPT-4o→Claude→Ollama, 3회 타임아웃 시 전환 — A-1 직결
- V3 진입 GO/NO-GO에 "Federated Agent 승인 체계" 항목 포함

## 버전별 차이
- V1: A-1·A-2만 ON / V2: A-4 COND 추가 / V3: A-3~A-7 전부 ON

## 원본 참조
- `D:\VAMOS\CLAUDE.md` §6 (A-Series 표)·§7.1 / `D:\VAMOS\docs\sot\D2.0-01_01. VAMOS_DESIGN_2_0_OVERVIEW.md` / `D:\VAMOS\docs\sot 2\6-9_Brain-Adapter-HAL\`
