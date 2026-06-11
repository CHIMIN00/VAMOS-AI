---
tags: [tier/T5, module/E-series, status/CORE, version/V1, type/domain]
aliases: [AI 투자 코어, AI Investing Core 00-07]
sot_source: "D:\\VAMOS\\docs\\sot 2\\Ai-investing-detail\\00_core-integration ~ 07_universe-management"
created: 2026-06-11
---

# AI-Investing Core (00~07)

## 한줄 요약
AI Investing의 기반 8개 하위도메인 — VAMOS Core 통합부터 실시간 적응, 심리/매크로 분석, 백테스트 진실성, 실행/유니버스 관리까지.

> ⚠️ 분석 전용, 실거래 절대 금지 (Non-goal 2.1) — [[AI-Investing-Overview]] 참조.

## 하위도메인 8개 (Status: 전수 APPROVED)
| 폴더 | 핵심 역할 |
|------|----------|
| 00_core-integration | VAMOS Core 통합 스펙 (core_integration_spec) |
| 01_realtime-adaptive | 실시간 적응형 전략 — D-03(실시간 처리 미흡) 극복, market_regime/order_flow/fakeout_detection 등 |
| 02_behavioral-finance | 투자 심리학·행동재무학 — 투자자 편향/군집 탐지/감정 거래 방지 |
| 03_macro-sector-stock | 매크로→섹터→종목 연결 엔진 — FRED/한국은행 데이터의 분석·활용 로직 |
| 04_performance-attribution | 성과 귀인 분석 — Brinson/팩터 귀인, 왜 그 성과가 났는지 분해 |
| 05_backtest-integrity | 백테스트 진실성 — look-ahead bias/data snooping/Monte Carlo/실행 현실성 |
| 06_execution-optimization | 실행 최적화 — **L3 APPROVED** (40+ items, 10/10 파일 E1~E9 전수) |
| 07_universe-management | 투자 유니버스 관리 — **L3 APPROVED** (35 items, 8/8 파일 E1~E9 전수) |

## 핵심 수치
- 백테스트: Walk-Forward Validation (train=252d, test=63d, step=21d) + 자산군별 동적 조절
- Gate: 51% 승률 Gate ([[5-Gate-Decision-Framework]] 연동)

## 의존성 / 제공
- Depends On: [[T5-Benchmark]] — 전략 평가 게이트, [[T6-Memory-RAG]] — 지식 저장
- Provides To: [[AI-Investing-Advanced]] — 기반 데이터·유니버스 제공

## 원본 문서
- SOT 2: `D:\VAMOS\docs\sot 2\Ai-investing-detail\00_core-integration\` ~ `07_universe-management\` (각 _index.md)
