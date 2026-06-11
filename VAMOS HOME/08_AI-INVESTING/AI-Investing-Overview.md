---
tags: [tier/T5, module/E-series, status/CORE, version/V1, type/domain, responsible-ai]
aliases: [AI 투자, AI Investing, 투자 분석 시스템]
sot_source: "D:\\VAMOS\\docs\\sot 2\\Ai-investing-detail\\"
spec_source: "D:\\VAMOS\\docs\\sot\\VAMOS_AI_INVESTING_SPEC.md"
created: 2026-06-11
---

# AI-Investing Overview

## 한줄 요약
VAMOS AI 투자 **분석 전용** 시스템 — 승률 ≥51%, Sharpe ≥1.0을 목표로 미국 주식/한국 주식/암호화폐를 분석한다.

> ⚠️ **분석 전용, 실거래 절대 금지 (Non-goal 2.1)** — 자동 실거래/주문 실행은 Non-goal이며, Trading BLUE NODE는 P2(승인 필수)로만 동작한다.

## 핵심 정의 (SPEC v2.1, 2026-06-04)
- 24개 섹션 + 부록: 7-Layer 데이터 아키텍처, 83개 데이터 소스, 51% Gate 백테스팅, 전략 96개(기술적 40 + 퀀트/팩터/옵션/ML 56)
- 기술 스택: Python, Airflow, Kafka, TimescaleDB, ChromaDB, Grafana (14-Item Locked + VAMOS 전체 LOCK 병행)
- 비용 상한: [[D2.0-07-Safety-Cost]] 정본 (V1 $30/V2 $70/V3 $200 월)
- Multi-Agent 워크플로우: Perplexity(리서치)/Gemini(분류·PM)/ChatGPT(전략·코드)/Claude(검증·Gate 판정)

## 22개 하위도메인 맵 (Ai-investing-detail\ 실측)
| # | 폴더 | 허브 노트 |
|---|------|----------|
| 00 | core-integration (VAMOS Core 통합) | [[AI-Investing-Core]] |
| 01~07 | realtime-adaptive / behavioral-finance / macro-sector-stock / performance-attribution / backtest-integrity / execution-optimization / universe-management | [[AI-Investing-Core]] |
| 08~15 | cross-asset / model-governance / quant-research / tca / microstructure / asset-class-deep / corporate-events / portfolio-advanced | [[AI-Investing-Advanced]] |
| 16~21 | global-geopolitics / explainability / data-quality / liquidity-cash / strategy-detail / mapping | [[AI-Investing-Infrastructure]] |

## 횡단 개념 연결
- [[5-Gate-Decision-Framework]] — 51% Gate·전략 채택 판정
- [[Cost-Limits]] — 비용 상한 정본 준수
- [[Non-Goals]] — Non-goal 2.1 실거래 금지의 정본
- [[Data-Governance-Pipeline]] — DQ Validation·데이터 품질

## 원본 문서
- SOT 2: `D:\VAMOS\docs\sot 2\Ai-investing-detail\` (00~21, 22개 폴더 + AUTHORITY_CHAIN/CONFLICT_LOG/INDEX)
- SPEC: `D:\VAMOS\docs\sot\VAMOS_AI_INVESTING_SPEC.md` (v2.1)
- STEP7: STEP7-I AI_Investing 보강 작업가이드
