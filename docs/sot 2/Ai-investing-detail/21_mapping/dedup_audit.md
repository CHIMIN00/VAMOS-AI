# 교차 중복 감사 결과

> **버전**: v1.0
> **Status**: APPROVED
> **작성일**: 2026-03-22
> **대상**: 19개 관점 파일, 172 카테고리, 758 항목

---

## 감사 방법

1. 19개 파일에서 `### B-N.` 패턴의 카테고리 172개 + 하위 항목 758개 추출
2. 키워드 매칭으로 2개+ 관점에 등장하는 개념 그룹핑
3. 각 중복 그룹에서 "가장 핵심적으로 다루는 관점"을 정본 소유자로 배정

---

## 중복 그룹 (30건)

| # | 중복 그룹 | 키워드 | 등장 관점 | 정본 소유자 | 비정본 처리 |
|---|----------|--------|----------|-----------|-----------|
| 1 | 시장 레짐 감지 | regime, 레짐, 레짐 분류 | #1(B-5), #3(B-1), #5(B-5), #8(B-1) | **#1** (01_realtime-adaptive/) | #3: 매크로 레짐은 #3 자체 소유(다른 개념). #5,#8: `> 참조: 01_realtime-adaptive/market_regime.md` |
| 2 | Volume Profile / 거래량 분석 | volume profile, 거래량 클러스터링 | #1(B-1), #12(B-3) | **#1** (01_realtime-adaptive/) | #12: 틱 레벨 체결 분석은 #12 소유, Volume Profile 참조만 추가 |
| 3 | Circuit Breaker 확장 | circuit breaker, 급등급락 방지 | #2(B-8), #19(B-6) | **PART2 §6.8 LOCK** | #2, #19: `> LOCK (SPEC §10.2): [원문]` 형식으로 참조만 |
| 4 | FinBERT / NLP 감성 분석 | FinBERT, NLP, 감성, sentiment | #2(B-5), #14(B-2) | **#2** (02_behavioral-finance/) | #14: 실적 콜 NLP는 #14 소유(다른 용도). FinBERT 감성 참조: `> 참조: 02_behavioral-finance/news_sentiment.md` |
| 5 | 슬리피지 모델 | slippage, 슬리피지, 시장 충격 | #6(B-4), #11(B-7), #5(B-7) | **#6** (06_execution-optimization/) | #11: 비용 관점에서 슬리피지 참조. #5: 백테스트 슬리피지 모델은 #5 소유(시뮬레이션용) |
| 6 | 백테스트 프레임워크 | backtest, 백테스트, 검증 | #5(전체), #10(B-2,B-5) | **#5** (05_backtest-integrity/) | #10: 전략 검증 시 백테스트 참조. 백테스트 진실성/편향 로직은 #5 소유 |
| 7 | 팩터 모델 / 팩터 분석 | factor, 팩터, 팩터 노출 | #3(B-6), #4(B-2), #8(B-4), #15(B-3) | **#15** (15_portfolio-advanced/) | #3: 팩터 타이밍은 #3 소유(매크로 연결). #4: 팩터 귀인은 #4 소유. #8: 교차 자산 팩터는 #8 소유. 공통 팩터 정의 참조: `> 참조: 15_portfolio-advanced/concentration_diversification.md` |
| 8 | SHAP / LIME 설명성 | SHAP, LIME, explainability | #9(B-7), #17(B-1) | **#17** (17_explainability/) | #9: 모델 감사 목적의 SHAP 사용은 #9 소유. 설명 알고리즘 자체는 `> 참조: 17_explainability/decision_explanation.md` |
| 9 | 데이터 품질 검증 | data quality, DQ, 데이터 정합성 | #18(전체), #5(B-8), SPEC §5 | **#18** (18_data-quality/) | #5: 백테스트 데이터 검증은 #5 소유(검증 목적). SPEC §5: MODULE-ARCH 레벨 유지 |
| 10 | 리밸런싱 전략 | rebalancing, 리밸런싱 | #6(B-6), #15(B-4) | **#15** (15_portfolio-advanced/) | #6: 실행 최적화 관점의 리밸런싱 실행은 #6 소유. 전략/규칙은 `> 참조: 15_portfolio-advanced/rebalancing.md` |
| 11 | 스트레스 테스트 | stress test, 스트레스 | #8(B-3), #15(B-6), #19(B-2) | **#15** (15_portfolio-advanced/) | #8: 교차 자산 스트레스는 #8 소유. #19: 유동성 스트레스는 #19 소유. 공통 프레임워크: `> 참조: 15_portfolio-advanced/stress_test.md` |
| 12 | VaR / CVaR | VaR, CVaR, value at risk | #8(B-3), #15(B-1,B-6) | **#15** (15_portfolio-advanced/) | #8: 통합 VaR 계산 로직 참조. `> 참조: 15_portfolio-advanced/portfolio_optimization.md` |
| 13 | Black-Litterman 모델 | Black-Litterman | #3(B-10), #15(B-1) | **#15** (15_portfolio-advanced/) | #3: 매크로 뷰 입력만 제공, 모델 구현은 `> 참조: 15_portfolio-advanced/portfolio_optimization.md` |
| 14 | Risk Parity | risk parity, 리스크 패리티 | #3(B-10), #8(B-4), #15(B-1) | **#15** (15_portfolio-advanced/) | #3, #8: 배분 옵션 언급만. 구현 상세: `> 참조: 15_portfolio-advanced/portfolio_optimization.md` |
| 15 | 호가창 / 오더북 분석 | order book, 호가창, 오더북 | #1(B-3,B-7), #6(B-2), #12(B-1) | **#12** (12_microstructure/) | #1: 매물대 연계 호가창은 #1 소유. #6: 실행용 호가 깊이는 #6 소유. 미시구조 분석: `> 참조: 12_microstructure/order_book.md` |
| 16 | 스마트 머니 추적 | smart money, 기관 추적 | #2(B-9), #12(B-5) | **#12** (12_microstructure/) | #2: 심리 관점의 스마트/덤 머니 구분은 #2 소유. 정보 비대칭 분석: `> 참조: 12_microstructure/information_asymmetry.md` |
| 17 | M&A / 기업 구조 변경 | M&A, merger, 인수 | #13(B-6), #14(B-3) | **#14** (14_corporate-events/) | #13: 이벤트 드리븐 전략은 #13 소유. M&A 분석 상세: `> 참조: 14_corporate-events/ma_restructuring.md` |
| 18 | 온체인 분석 | on-chain, 온체인 | #1(B-7 크립토), #8(B-5), #13(B-3), #18(B-7) | **#13** (13_asset-class-deep/) | #1,#8: 크립토 시그널 활용만. #18: 데이터 품질 검증만. 온체인 분석 상세: `> 참조: 13_asset-class-deep/crypto_strategies.md` |
| 19 | ETF 전략 / 자금 흐름 | ETF, fund flow | #7(B-8), #14(B-8), #13(B-7) | **#14** (14_corporate-events/) | #7: 유니버스 내 ETF 관리는 #7 소유. #13: 대체 투자 전략은 #13 소유. ETF 자금 흐름: `> 참조: 14_corporate-events/institutional_flow.md` |
| 20 | 지정학 리스크 | geopolitical, 지정학 | #3(B-5), #16(B-2) | **#16** (16_global-geopolitics/) | #3: 매크로 연결의 지정학 스코어 활용만. 지정학 분석 상세: `> 참조: 16_global-geopolitics/geopolitical_risk.md` |
| 21 | 전략 앙상블 / 충돌 해결 | ensemble, 앙상블, 전략 충돌 | #1(B-13), #9(B-5) | **#1** (01_realtime-adaptive/) | #9: ML 앙상블 거버넌스는 #9 소유. 전략 레벨 앙상블: `> 참조: 01_realtime-adaptive/strategy_ensemble.md` |
| 22 | A/B 테스트 | A/B test | #5(B-10), #9(B-9) | **#9** (09_model-governance/) | #5: 라이브 vs 백테스트 비교 목적은 #5 소유. A/B 테스트 인프라: `> 참조: 09_model-governance/mlops.md` |
| 23 | 환율 / FX 전략 | 환율, FX, currency, DXY | #3(B-3,B-5), #8(B-4), #13(B-2), #16(B-4) | **#16** (16_global-geopolitics/) | #3: 환율 민감도 매핑은 #3 소유. #8: 환율 헤지 최적화는 #8 소유. #13: 한국 환율 연동은 #13 소유. 환율 전략 상세: `> 참조: 16_global-geopolitics/currency_strategy.md` |
| 24 | 포지션 사이징 | position sizing, Kelly, ATR | #1(B-8), #15(B-2), #19(B-7) | **#15** (15_portfolio-advanced/) | #1: 동적 포지션 관리 실행은 #1 소유. #19: 유동성 기반 사이징은 #19 소유. Kelly/ATR 프레임워크: `> 참조: 15_portfolio-advanced/position_sizing.md` |
| 25 | 실적 서프라이즈 / PEAD | earnings surprise, PEAD | #3(B-8), #14(B-2) | **#14** (14_corporate-events/) | #3: 실적 → 섹터 연결만 활용. 실적 분석 상세: `> 참조: 14_corporate-events/earnings_analysis.md` |
| 26 | 섹터 로테이션 | sector rotation, 업종 | #3(B-2), #13(B-1,B-2) | **#3** (03_macro-sector-stock/) | #13: 섹터별 전략은 #13 소유. 로테이션 엔진: `> 참조: 03_macro-sector-stock/sector_rotation.md` |
| 27 | 모델 드리프트 / 성과 감시 | drift, decay, 성과 모니터링 | #9(B-1), #10(B-8) | **#9** (09_model-governance/) | #10: 알파 감쇠 모니터링은 #10 소유. 모델 드리프트: `> 참조: 09_model-governance/model_drift.md` |
| 28 | 배당 전략 | dividend, 배당 | #13(B-1,B-2), #19(B-3) | **#13** (13_asset-class-deep/) | #19: 배당 수입 예측은 #19 소유. 배당 전략: `> 참조: 13_asset-class-deep/us_stock_strategies.md` |
| 29 | 공매도 / Short | short, 공매도, short interest | #7(B-5), #14(B-6) | **#14** (14_corporate-events/) | #7: 공매도 가능성 필터는 #7 소유. 공매도 분석: `> 참조: 14_corporate-events/short_seller.md` |
| 30 | 마진 / 레버리지 | margin, leverage, 마진콜 | #13(B-4), #19(B-4) | **#19** (19_liquidity-cash/) | #13: 파생상품 전략은 #13 소유. 마진 관리: `> 참조: 19_liquidity-cash/margin_leverage.md` |

---

## 정본 소유자 배정 요약

| 정본 소유자 | 소유 중복 그룹 수 |
|-----------|----------------|
| #1 (01_realtime-adaptive/) | 3건 (#1 시장 레짐, #2 Volume Profile, #21 앙상블) |
| #2 (02_behavioral-finance/) | 1건 (#4 FinBERT) |
| #3 (03_macro-sector-stock/) | 1건 (#26 섹터 로테이션) |
| #5 (05_backtest-integrity/) | 1건 (#6 백테스트) |
| #6 (06_execution-optimization/) | 1건 (#5 슬리피지) |
| #9 (09_model-governance/) | 2건 (#22 A/B 테스트, #27 모델 드리프트) |
| #12 (12_microstructure/) | 2건 (#15 호가창, #16 스마트 머니) |
| #13 (13_asset-class-deep/) | 2건 (#18 온체인, #28 배당) |
| #14 (14_corporate-events/) | 3건 (#17 M&A, #19 ETF, #25 실적, #29 공매도) |
| #15 (15_portfolio-advanced/) | 6건 (#7 팩터, #10 리밸런싱, #11 스트레스, #12 VaR, #13 BL, #14 RP, #24 포지션사이징) |
| #16 (16_global-geopolitics/) | 2건 (#20 지정학, #23 환율) |
| #17 (17_explainability/) | 1건 (#8 SHAP/LIME) |
| #18 (18_data-quality/) | 1건 (#9 데이터 품질) |
| #19 (19_liquidity-cash/) | 1건 (#30 마진) |
| PART2 §6.8 LOCK | 1건 (#3 Circuit Breaker) |

---

## 특수 판정: 동일 키워드지만 다른 개념

| 키워드 | 관점 A (소유) | 관점 B (소유) | 판정 이유 |
|--------|-------------|-------------|----------|
| 레짐 | #1: 시장 레짐 (가격 기반) | #3: 매크로 레짐 (경제 사이클 기반) | 입력 데이터와 분류 기준이 다름 → 각자 소유 |
| 슬리피지 | #6: 실행 슬리피지 (실시간) | #5: 백테스트 슬리피지 (시뮬레이션) | 사용 목적이 다름 → 각자 소유, 모델 공유 참조 |
| 팩터 | #3: 팩터 타이밍 (매크로) | #4: 팩터 귀인 (성과) | #8: 교차 자산 팩터 | #15: 팩터 포트폴리오 → 각자 관점에서 소유, 공통 정의는 #15 참조 |
| NLP/감성 | #2: 시장 심리 감성 | #14: 실적 콜 텍스트 분석 | 분석 대상이 다름 → 각자 소유 |

---

## 미판정 중복: 0건

모든 중복 그룹에 대해 정본 소유자가 배정 완료되었습니다.
