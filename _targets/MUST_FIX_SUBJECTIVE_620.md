# 주관적 설계선택 — 재도출 v2 전수 리스트 (2026-06-11 세션6)

> **v1(실체 부재 보고서)을 본 v2가 대체한다.** 재도출 워크플로: wf_d775e706-682(24도메인) + wf_370f0b4a-370(12도메인) = **36/36 도메인 전수**.
> 원본 상세(options·근거 전문): `_integ/w1_620_partial_raw.json`(525KB) + `_integ/w1b_620_raw.json`(122KB).
> 재도출 합계 **615건** (원판정 620 — 차이는 도메인별 notes에 사유 기록: 중복 병합·기해소·앵커 초과분 등).
> 판정: **KEEP 591건**(현행 값 합리·정본 무모순 — 결정 불필요, 그대로 채택) / **CHANGE 24건**(정본 모순 발견 — 세션6에서 일괄 적용).
> 사용자 결정 잔여: 0건 — 전권 위임에 따라 전 항목 단일 결론 처리됨. 이후 변경 원하면 항목별 재개정.

## 도메인별 요약

| 도메인 | 재도출 | 원판정 | CHANGE |
|---|---:|---:|---:|
| Ai-investing-detail | 89 | 89 | 0 |
| 2-2_COND-Modules-Detail | 67 | 87 | 0 |
| 3-6_Health-Wellness-EmotionAI | 26 | 25 | 2 |
| 3-4_Workflow-RPA | 26 | 22 | 2 |
| 6-3_Agent-Teams-PARL | 24 | 22 | 4 |
| 1-1_Verifier-Reasoning-Engines | 20 | 18 | 0 |
| 3-7_Developer-Tools-API-SDK | 19 | 19 | 0 |
| 4-1_Rust-Tauri-Infrastructure | 19 | 19 | 2 |
| 6-4_Memory-RAG-Storage | 19 | 19 | 3 |
| 3-5_Education-Learning | 19 | 18 | 0 |
| 4-2_CICD-Pipeline | 18 | 19 | 1 |
| 3-2_Multimodal-Processing | 18 | 18 | 0 |
| 3-3_PKM-Knowledge-Management | 17 | 17 | 0 |
| 6-5_SDAR-System | 17 | 17 | 0 |
| 4-4_MLOps-LLMOps | 16 | 12 | 1 |
| 4-3_MCP-Server-Client | 15 | 15 | 0 |
| 1-2_Auxiliary-Modules | 14 | 14 | 3 |
| 5-2_File-Context | 14 | 14 | 0 |
| 6-1_UI-UX-System | 13 | 13 | 0 |
| 6-2_Security-Governance | 13 | 13 | 0 |
| 6-7_RT-BNP-DCL | 13 | 13 | 0 |
| 3-10_Agent-Protocol-Interoperability | 12 | 12 | 0 |
| 6-9_Brain-Adapter-HAL | 12 | 12 | 1 |
| 3-8_Conversation-A2A | 12 | 11 | 0 |
| 3-9_Business-Model-Strategy | 10 | 10 | 0 |
| 5-1_Benchmark-Evaluation | 9 | 7 | 0 |
| 5-3_v12-Additions-Detail | 9 | 10 | 3 |
| 6-11_Hologram-Main-LLM | 9 | 9 | 0 |
| 6-12_Event-Logging | 9 | 9 | 0 |
| 2-1_Blue-Node-Architecture | 8 | 8 | 2 |
| 0-0_Governance-Rules-Meta | 7 | 7 | 0 |
| 6-8_Cloud-Library | 7 | 7 | 0 |
| 6-6_Self-Evolution-System | 6 | 6 | 0 |
| 5-4_v23-Extension-Items | 3 | 3 | 0 |
| 6-10_EXP-Modules-Detail | 3 | 3 | 0 |
| 6-13_Operations | 3 | 3 | 0 |
| **합계** | **615** | **620** | **24** |

## 전수 항목 (도메인별)

### Ai-investing-detail (89건)

1. **[KEEP]** `docs/sot 2/Ai-investing-detail/01_realtime-adaptive/fakeout_detection.md`:114 — Bull/Bear Trap confidence의 거래량 통계로 돌파구간 prev_bars의 max volume을 사용
   - 선택지: max(순간 최대, 보수적) vs mean(평균 강도) vs 마지막 봉 거래량
   - 판정: KEEP — 정본(RULE/PLAN/LOCK) 어디에도 통계 선택 미규정; max는 '거래량 많았던 돌파'를 trap에서 빠르게 배제하는 보수적 선택으로 합리. docstring에 선택 근거 1줄 명시 권고
2. **[KEEP]** `docs/sot 2/Ai-investing-detail/01_realtime-adaptive/market_regime.md`:483 — HMM 레짐 모델 파라미터 N_REGIMES=6, n_iter=100, MIN_BARS=120
   - 선택지: 상태수 4~8, n_iter 50~200, 최소봉수 60~250
   - 판정: KEEP — AUTHORITY_CHAIN §14는 기술스택(라이브러리) LOCK으로 이 값을 정의하지 않음 → 값은 설계 기본값으로 유지. 'SPEC §14' 출처 라벨만 '설계 기본값(LOCK 후보)'로 정정(객관 트랙)
3. **[KEEP]** `docs/sot 2/Ai-investing-detail/01_realtime-adaptive/multi_timeframe.md`:391 — EMA(20,50), ALIGNMENT_THRESHOLD=0.6, RSI_PERIOD=14 지표 파라미터
   - 선택지: EMA(12,26)/(20,50)/(50,200), 정합 임계 0.5~0.7
   - 판정: KEEP — 정본 §14는 지표 주기/임계 미정의. 표준 관행 범위 내 설계 재량. E9 출처 라벨만 정정 권고
4. **[KEEP]** `docs/sot 2/Ai-investing-detail/01_realtime-adaptive/strategy_invalidation.md`:612 — 전략 전환 제안 시 신규 전략 승률>51% 검증을 51% Gate로 적용
   - 선택지: 전환 시 게이트 재검증 vs 최초 승인 시에만 적용
   - 판정: KEEP — SPEC §6.1 51% Gate의 정본 의미(Win Rate≥51%)와 일치하는 적용 범위 확장이며 정본 무모순. E2 구현 누락(T8-062)은 별도 객관 트랙
5. **[KEEP]** `docs/sot 2/Ai-investing-detail/01_realtime-adaptive/strategy_ensemble.md`:234 — ensemble_vote 동률 시 BUY 우선 tie-break
   - 선택지: BUY 우선 vs SELL 우선 vs 동률=HOLD
   - 판정: KEEP — 정본 미정의 정책이고 min_agreement_ratio 게이트가 균형 투표를 실질 차단. 동률=HOLD가 더 보수적이나 현행도 무모순
6. **[KEEP]** `docs/sot 2/Ai-investing-detail/01_realtime-adaptive/strategy_ensemble.md`:182 — resolve_conflict confidence = agreement × (1 − 1/n) 소수전략 페널티 스케일링
   - 선택지: agreement 그대로 vs n-페널티 vs 가중 평균 confidence
   - 판정: KEEP — 참여 전략 수가 적을 때 과신을 구조적으로 낮추는 보수적 설계로 합리. 본문에 의도 주석 권고
7. **[KEEP]** `docs/sot 2/Ai-investing-detail/01_realtime-adaptive/price_action.md`:550 — ATR 접근 ×0.3 / 돌파 ×0.5 / 거래량 서지 ×1.5 / 벽 ×5.0 임계값
   - 선택지: ATR 배수 0.2~1.0, 서지 1.2~2.0 등 연속 스펙트럼
   - 판정: KEEP — SPEC §6.2(엔진 설정)는 이 값들 미정의 → 값은 설계 기본값으로 유지, 인용 라벨 정정은 객관 트랙
8. **[KEEP]** `docs/sot 2/Ai-investing-detail/01_realtime-adaptive/supply_demand_zone.md`:219 — volume_score가 구역 거래량 5%에서 1.0 포화하는 분모(total×0.05)
   - 선택지: 5% vs 10% 포화 vs 비포화 연속 스케일
   - 판정: KEEP — '5%+ 구역은 동급 최강'이라는 단순화는 재량이며 0.4 가중 내 변별력 손실은 수용 가능한 트레이드오프. 포화점 캘리브레이션 후보
9. **[KEEP]** `docs/sot 2/Ai-investing-detail/01_realtime-adaptive/supply_demand_zone.md`:429 — 볼륨 프로파일 시간 반감기 168h(7일), MA 주기/스윙 룩백/합류 허용오차
   - 선택지: 반감기 24h~720h 등
   - 판정: KEEP — §6.2가 이 수치를 정의하지 않으므로 값은 설계 기본값. 같은 표의 'Value Area 70% | 업계 표준(CBOT)' 표기 선례대로 출처 라벨 정정 권고
10. **[KEEP]** `docs/sot 2/Ai-investing-detail/01_realtime-adaptive/volatility_adaptive.md`:160 — GARCH(1,1) '간이 추정': alpha=0.10/beta=0.85 고정 + omega만 variance targeting
   - 선택지: 고정 persistence(간이) vs MLE 완전 적합(arch 라이브러리)
   - 판정: KEEP — docstring이 '간이 추정' 명시; RiskMetrics류 고정 persistence는 표준 단순화. 함수명 fit→calibrate 수준 명칭 보수화만 권고
11. **[KEEP]** `docs/sot 2/Ai-investing-detail/02_behavioral-finance/investor_behavior.md`:143 — DISPOSITION_RATIO_THRESHOLD=1.5 (본문 예시 '3배'보다 민감)
   - 선택지: 1.5(조기 경고) vs 3.0(예시 수준 확증)
   - 판정: KEEP — 본문 L19의 '3배'는 극단 사례 서술이지 임계 규정이 아님(본문>스키마 위계상 규정 부재). 조기 경고용 민감 튜닝은 재량
12. **[KEEP]** `docs/sot 2/Ai-investing-detail/03_macro-sector-stock/industry_value_chain.md`:165 — 산업 사이클 판정에 z>0 단순 부호 불리언(데드밴드/히스테리시스 없음), 가동률 0.75 임계
   - 선택지: 데드밴드(|z|>0.5) 추가 vs 단순 부호
   - 판정: KEEP — V1 단순 부호 판정은 재량이고 정본 무모순. 노이즈 플립플롭 억제용 데드밴드는 V2 보강 후보
13. **[KEEP]** `docs/sot 2/Ai-investing-detail/03_macro-sector-stock/macro_regime.md`:426 — favorability<0.2 시 방어 모드 전환 트리거 값
   - 선택지: 0.1~0.3 임계 스펙트럼
   - 판정: KEEP — 트리거 값 자체는 설계 재량이고 정본 무모순. 'Circuit Breaker -3% (§10.2)' 인용과의 혼동은 라벨 분리(객관 트랙) 사안
14. **[KEEP]** `docs/sot 2/Ai-investing-detail/04_performance-attribution/attribution_reporting.md`:768 — 주간 리포트 기간을 (today−4일, today)로 산정
   - 선택지: 달력 주(월~금) 정렬 vs 고정 4일 윈도우
   - 판정: KEEP — 단순화 재량이며 정본 미정의. 비금요일 캐치업 실행 시 윈도우 가정 주석 권고
15. **[KEEP]** `docs/sot 2/Ai-investing-detail/04_performance-attribution/brinson_attribution.md`:281 — 귀인 분해 잔차 5% 초과 시 신뢰도 경고 임계값
   - 선택지: 1%~10% 잔차 경고 스펙트럼
   - 판정: KEEP — 잔차 경고선 자체는 설계 재량. §10.2(거래 중단 CB) 인용은 오귀속이므로 라벨만 정정(객관 트랙)
16. **[KEEP]** `docs/sot 2/Ai-investing-detail/04_performance-attribution/risk_adjusted_metrics.md`:126 — Treynor에서 beta==0 정확 일치 시에만 0.0 반환(근사-0 가드 없음)
   - 선택지: epsilon 가드(|beta|<1e-6) vs 정확 일치
   - 판정: KEEP — 음수 beta 유효 처리 포함 동작 정의는 유효하고 정본 무모순. epsilon 가드는 수치 강건성 개선 후보
17. **[KEEP]** `docs/sot 2/Ai-investing-detail/05_backtest-integrity/execution_realism.md`:152 — 지연 가격 시프트 방향에 seed 미주입 random.choice([-1,1]) 사용
   - 선택지: seed 파라미터 주입 vs 매회 비결정 난수
   - 판정: KEEP — E8 검증은 1000회 분포 검정이라 결정성 불요; 재현 필요 워크플로에만 seed 인자 추가 후보. 정본 무모순
18. **[KEEP]** `docs/sot 2/Ai-investing-detail/05_backtest-integrity/reproducibility.md`:395 — NOT_REPRODUCIBLE 결과의 승인 차단 정책(51% Gate 라벨로 표기)
   - 선택지: 차단(현행) vs 경고 후 조건부 승인
   - 판정: KEEP — 재현 불가 결과 승인 차단은 백테스트 진실성 도메인 취지에 부합하는 재량. '51% Gate' 명칭 차용만 별도 라벨 정정 권고
19. **[KEEP]** `docs/sot 2/Ai-investing-detail/06_execution-optimization/execution_performance.md`:377 — total_cost_bps = IS(timing+impact+commission)로 정의하고 spread_cost는 별도 보고(합산 제외)
   - 선택지: spread 합산(이중계상 위험) vs 분리 보고(현행)
   - 판정: KEEP — market_impact가 arrival→fill 구간을 포함하므로 spread 분리가 이중계상을 방지(자매 finding T8-562도 동일 논리). E3에 정의 1줄 명시 권고
20. **[KEEP]** `docs/sot 2/Ai-investing-detail/06_execution-optimization/order_type_timing.md`:810 — 타이밍 가중치 (0.4, 0.35, 0.25), 스프레드 임계 20bps, 체인 최대 10 등 알고리즘 파라미터
   - 선택지: 가중 재배분/임계 조정 스펙트럼
   - 판정: KEEP — §14(기술스택 LOCK)는 이 수치 미정의 → 값은 설계 기본값 유지, 출처 라벨 정정은 객관 트랙
21. **[KEEP]** `docs/sot 2/Ai-investing-detail/06_execution-optimization/smart_order_routing.md`:866 — 호가 freshness 500ms, max_slippage 30bps, 깊이 가중 0.4/0.35/0.25, KR 수수료 0.015%
   - 선택지: freshness 100ms~1s, slippage 10~50bps
   - 판정: KEEP — 정본 §14 미정의 값들로 설계 재량 범위. 라벨 정정 권고 외 값 변경 불요
22. **[KEEP]** `docs/sot 2/Ai-investing-detail/07_universe-management/cross_asset_universe.md`:1078 — 한국 펀드 return_ytd를 1y 수익률로 근사('간소화' 주석)
   - 선택지: 정식 연초 대비 계산 vs 1y 근사(현행)
   - 판정: KEEP — '간소화' 주석으로 의도 명시된 V1 재량. V2에서 연초 기준 계산 승격 후보
23. **[KEEP]** `docs/sot 2/Ai-investing-detail/07_universe-management/cross_asset_universe.md`:481,907 — 최소 상장경과: 글로벌 ETF 365일(etf_min_age_days) vs 한국 펀드 180일(MIN_LISTING_DAYS) 차등
   - 선택지: 단일 기준 통일 vs 자산군/시장별 차등(현행)
   - 판정: KEEP — 서로 다른 유니버스에 대한 차등 기준은 재량이고 정본 무모순. 두 상수의 적용 범위 주석 권고
24. **[KEEP]** `docs/sot 2/Ai-investing-detail/07_universe-management/universe_analytics.md`:786 — 상관 매트릭스 의사코드를 순수 Python 루프로 명세(800×800 ≤30s 목표와 병기)
   - 선택지: 벡터화 코드 명세 vs 알고리즘 명료성 우선 의사코드(현행)
   - 판정: KEEP — L3 의사코드는 알고리즘 정의가 목적; 성능 목표 달성은 구현 단계 numpy 벡터화로 충족 가능. E6에 '벡터화 전제' 1줄 권고
25. **[KEEP]** `docs/sot 2/Ai-investing-detail/08_cross-asset/integrated_risk.md`:579 — overall risk_level을 3종 VaR 평균 단독으로 등급화(MDD/스트레스 미반영)
   - 선택지: VaR 단독(현행) vs VaR+MDD+스트레스 합성 점수
   - 판정: KEEP — 등급화 입력 선택은 재량이고 정본 무모순. 스트레스 손실 반영은 V2 개선 후보로 기록
26. **[KEEP]** `docs/sot 2/Ai-investing-detail/09_model-governance/ensemble_governance.md`:229 — diversity_score 임계 이원화: confidence HIGH >0.5 vs Acceptance 합격 >0.3
   - 선택지: 단일 임계 vs 목적별 이원 임계(현행)
   - 판정: KEEP — 합격선(0.3)과 고신뢰선(0.5)은 목적이 다른 게이트로 공존 가능. 본문에 두 임계의 역할 구분 1줄 명시 권고
27. **[KEEP]** `docs/sot 2/Ai-investing-detail/09_model-governance/feature_governance.md`:370 — NaN 비율 상한 30%, PIT 미래상관 임계 |corr|>0.5
   - 선택지: NaN 10~50%, corr 0.3~0.7
   - 판정: KEEP — 통계 관행 범위의 설계 임계값. 'SPEC §9' 귀속이 미확인이므로 출처 라벨만 '설계 기본값'으로 정정 권고
28. **[KEEP]** `docs/sot 2/Ai-investing-detail/09_model-governance/hyperparameter_management.md`:177 — 재학습 주기 변동성 조정식 1/(1+asset_volatility)
   - 선택지: 연율 기준 약한 조정(현행 해석) vs 일율 기준 강한 조정 — 단위 정의에 따름
   - 판정: KEEP — 조정식 자체는 재량. 입력 단위(연율화 변동성)를 E1에 명시해 해석 고정 권고
29. **[KEEP]** `docs/sot 2/Ai-investing-detail/09_model-governance/model_fairness.md`:279 — 편향 밴드 이원화: 감지 경고 0.5~2.0 vs Acceptance 수용 0.3~3.0
   - 선택지: 단일 밴드 vs 경고/차단 이원 밴드(현행)
   - 판정: KEEP — 감지(조기 경고)와 수용(차단)의 분리는 설계 가능 구조. is_biased 플래그의 의미(경고이지 차단 아님) 명시 권고
30. **[KEEP]** `docs/sot 2/Ai-investing-detail/09_model-governance/model_drift.md`:326 — PSI 임계 0.25, KS alpha 0.05 등 드리프트 판정 기준
   - 선택지: PSI 0.1(민감)/0.25(표준)
   - 판정: KEEP — PSI 0.25는 업계 표준으로 표 자체가 '업계 표준' 병기. §9 귀속 부분만 라벨 정리 권고
31. **[KEEP]** `docs/sot 2/Ai-investing-detail/09_model-governance/model_explainability.md`:290 — audit_store_uri 기본값 'timescaledb://localhost/audit'
   - 선택지: 기본값 없음(필수 주입) vs localhost 개발 기본값(현행)
   - 판정: KEEP — 설계 문서의 개발용 기본값은 재량. 배포 시 환경변수 주입 전제 주석 권고(프로덕션 결합은 구현 단계 사안)
32. **[KEEP]** `docs/sot 2/Ai-investing-detail/10_quant-research/research_quality.md`:129 — Bonferroni t-임계 계산에 df=100 고정 근사
   - 선택지: 표본 길이 기반 df vs 고정 근사(현행)
   - 판정: KEEP — '근사' 주석 명시; 일반적 백테스트 표본(>100)에서 t분포는 df에 둔감해 영향 미미. 정본 무모순
33. **[KEEP]** `docs/sot 2/Ai-investing-detail/10_quant-research/research_quality.md`:391 — 편향 검증 모듈은 51% Gate를 직접 집행하지 않고 소비자(평가 게이트)에 위임
   - 선택지: 모듈 내 집행 vs 소비자 위임(현행)
   - 판정: KEEP — 게이트 집행 위치는 아키텍처 재량이고 §6.1과 무모순. E9 행에 '집행 주체: strategy_evaluation_gate' 명시 권고
34. **[KEEP]** `docs/sot 2/Ai-investing-detail/11_tca/asset_class_cost_model.md`:226 — 가스비 계산용 토큰 가격 하드코딩(ETH=3000 등, '실시간 조회 대체' 주석)
   - 선택지: 시세 입력 파라미터 vs V1 placeholder 상수(현행)
   - 판정: KEEP — placeholder임이 주석으로 명시된 설계 단계 재량. 구현 시 market data 입력+TTL 캐시로 대체하는 노트 권고
35. **[KEEP]** `docs/sot 2/Ai-investing-detail/10_quant-research/strategy_evaluation_gate.md`:111 — Net Sharpe 분모에 gross 수익률 std 사용(비용 차감은 평균에만)
   - 선택지: 비용 반영 net 시계열 재구성 vs 평균만 차감 근사(현행)
   - 판정: KEEP — finding 스스로 'minor' 인정; 비용의 분산 영향은 통상 미미한 표준 근사. '근사' 주석 1줄 권고
36. **[KEEP]** `docs/sot 2/Ai-investing-detail/12_microstructure/market_manipulation.md`:160 — wash_score 합성의 vpd/100 정규화 상수와 0.3 기여 상한
   - 선택지: 고정 상수(현행) vs 심볼별 분포 기반 정규화
   - 판정: KEEP — 휴리스틱 합성 점수의 상수 선택은 재량이고 상한 0.3이 폭주를 차단. 실데이터 캘리브레이션 후보로 기록
37. **[KEEP]** `docs/sot 2/Ai-investing-detail/13_asset-class-deep/derivatives_strategies.md`:494 — 커버드콜 target_delta 0.30, 풋보험 비용 상한 2%, 레버리지 5x 등 전략 파라미터
   - 선택지: delta 0.2~0.4, 보험 1~3%
   - 판정: KEEP — 옵션 전략 관행 범위의 설계 값. 'SPEC §13-2x' 인용 검증 불가는 라벨 트랙 사안이며 값 자체는 무모순
38. **[KEEP]** `docs/sot 2/Ai-investing-detail/13_asset-class-deep/us_stock_strategies.md`:162 — 섹터 페어 시그널에 stop_z 부재(entry 2.0/exit 0.5만; 자매 statistical_arbitrage는 stop_z=4.0 보유)
   - 선택지: stop_z 추가 vs 구조적 수렴 가정 단순화(현행)
   - 판정: KEEP — 전략별 출구 구성은 재량이고 정본 무모순. 자매 모듈과의 정합 차원에서 stop_z=4.0 추가를 V2 후보로 기록
39. **[KEEP]** `docs/sot 2/Ai-investing-detail/13_asset-class-deep/us_stock_strategies.md`:115 — exdiv 패턴 confidence = avg_pre_exdiv_return_5d × 100 선형 매핑(cap 1.0)
   - 선택지: 선형 ×100(현행) vs 승률 캘리브레이션 매핑
   - 판정: KEEP — cap이 존재하고 매핑 방식은 재량. 51% Gate와의 스케일 의미(0.51=0.51% 수익) 주석 권고
40. **[KEEP]** `docs/sot 2/Ai-investing-detail/14_corporate-events/event_classification.md`:748 — 알림 중복 억제 키 생성에 MD5 사용
   - 선택지: md5(현행, 비암호 용도) vs sha256
   - 판정: KEEP — dedup 키는 비암호 용도로 md5 충돌 리스크 실질 무시 가능(LOW). 보안 결벽 원하면 sha256 1줄 교체 후보
41. **[KEEP]** `docs/sot 2/Ai-investing-detail/14_corporate-events/earnings_analysis.md`:334 — transcript 충분성 판단 기준 len>1000자(confidence 0.3 가중 항)
   - 선택지: 1000자(사실상 항상 충족, 보수적 무해) vs 단어/토큰 기준
   - 판정: KEEP — 임계 선택은 재량이고 실콜 transcript에서 1.0 수렴은 무해(과소 아님). 단위 재검토 후보로 기록
42. **[KEEP]** `docs/sot 2/Ai-investing-detail/14_corporate-events/earnings_analysis.md`:189 — 가이던스 방향 임계 ±0.02, conservative_pattern beat_ratio>0.75
   - 선택지: ±0.01~0.05, 0.6~0.8
   - 판정: KEEP — 정본 미정의 파라미터로 설계 재량. 실증 보정 근거 주석 추가 권고(LOCK 인용 불요)
43. **[KEEP]** `docs/sot 2/Ai-investing-detail/14_corporate-events/insider_trading.md`:93 — 내부자 net_signal 비대칭 규칙(SELL은 buys×2 초과 요구, STRONG_BUY는 클러스터 매수자≥3)
   - 선택지: 대칭 규칙 vs 매도 보수화 비대칭(현행)
   - 판정: KEEP — 내부자 매도는 비정보적 사유(유동성/세금)가 많아 매도 신호를 보수화하는 것은 행동재무 표준 관행. 정본 무모순
44. **[KEEP]** `docs/sot 2/Ai-investing-detail/14_corporate-events/ma_restructuring.md`:57 — 머저암 스프레드 연환산에 90일 고정 horizon 가정
   - 선택지: 실제 예상 종결일 입력 vs 고정 90일(현행, '가정' 주석)
   - 판정: KEEP — '90일 가정' 주석으로 명시된 V1 단순화. expected_close_date 입력 추가를 V2 후보로 기록
45. **[KEEP]** `docs/sot 2/Ai-investing-detail/15_portfolio-advanced/rebalancing.md`:310 — tax_rate_short = tax_rate_long = 0.22 동일 세율 기본값
   - 선택지: 미국식 단기/장기 차등 vs 한국 해외주식 단일 22%(현행)
   - 판정: KEEP — 한국 거주자 해외주식 양도세는 보유기간 무관 22% 단일률로 기본값이 현실 정합. 분기 로직은 다국 확장 대비 구조로 유지
46. **[KEEP]** `docs/sot 2/Ai-investing-detail/15_portfolio-advanced/stress_test.md`:452 — 역사적 시나리오 최소 3종(GFC, COVID, RATE_HIKE) 유지 정책
   - 선택지: 3종 vs 5종+ 시나리오 확대
   - 판정: KEEP — 최소 시나리오 수는 설계 재량이고 §17 D-13 인용 미확인은 라벨 트랙. 3종 핵심 커버리지는 합리적 베이스라인
47. **[KEEP]** `docs/sot 2/Ai-investing-detail/16_global-geopolitics/country_risk.md`:407 — SEC 규제 세부(S7I-097, Reg T/SHO)를 country_risk.md 내 보강 섹션으로 배치
   - 선택지: 별도 컴플라이언스 모듈 분리 vs 문서 내 STEP7-I 보강 배치(현행)
   - 판정: KEEP — 콘텐츠 조직/배치는 재량이고 보강 근거(step7i_mapping PARTIAL)가 명시됨. 모듈 분리는 V2 리팩토링 후보(내용 결함은 별도 트랙)
48. **[KEEP]** `docs/sot 2/Ai-investing-detail/16_global-geopolitics/currency_strategy.md`:219 — 헤지 효익 평가를 변동성 감소 × 명목금액 근사로 산정
   - 선택지: utility/VaR 기반 평가 vs 단순 근사(현행, '(근사)' 주석)
   - 판정: KEEP — 방법론 선택은 재량이고 근사임이 주석에 명시. 리스크 회피 계수 기반 평가는 고도화 후보
49. **[KEEP]** `docs/sot 2/Ai-investing-detail/16_global-geopolitics/geopolitical_risk.md`:133 — GPR 정규화 분모 50.0 (경험적 상한: 일일 500건 기준 주석)
   - 선택지: 고정 경험 상수(현행) vs rolling 분위수 동적 정규화
   - 판정: KEEP — 경험 근거가 주석으로 명시된 캘리브레이션 상수. 기사량 증가 시 재캘리브레이션 절차 1줄 추가 권고
50. **[KEEP]** `docs/sot 2/Ai-investing-detail/16_global-geopolitics/geopolitical_risk.md`:259 — 이벤트 분류 임계 THRESHOLD=0.15를 매칭비율(match/len(keywords))에 적용 — 카테고리별 키워드 수에 따라 실효 임계 상이
   - 선택지: 비율 임계(현행) vs 절대 매칭 수 vs 가중 키워드
   - 판정: KEEP — 임계 방식 선택은 재량. 키워드 수가 많은 카테고리의 단일 결정 키워드 미발화는 의도된 보수성으로 해석 가능; E8 기대값 정합(객관 트랙)만 별도 처리
51. **[KEEP]** `docs/sot 2/Ai-investing-detail/16_global-geopolitics/global_allocation.md`:172 — 누락 통화 변동성 기본값 .get(ccy, 0.01)
   - 선택지: 결측 통화 제외 vs 1% 기본값(현행)
   - 판정: KEEP — 기본값 부여는 재량이고 1%는 주요 통화 하단 근사. 결측 시 헤지비율 영향 주석 권고
52. **[KEEP]** `docs/sot 2/Ai-investing-detail/16_global-geopolitics/synchronization_decoupling.md`:62 — DCC 기본값 a=0.05/b=0.93 채택 + a+b<1 런타임 가드 미구현(기본값은 조건 충족)
   - 선택지: 파라미터 가드 추가 vs 문헌 표준 기본값 신뢰(현행)
   - 판정: KEEP — 기본값은 DCC 문헌 표준 범위로 안정 조건(합 0.98<1) 충족. 호출자 변경 대비 가드는 방어적 프로그래밍 보강 후보
53. **[KEEP]** `docs/sot 2/Ai-investing-detail/17_explainability/interactive_explanation.md`:985 — COMPARE 벤치마크 기본값 KOSPI200
   - 선택지: KOSPI200(현행) vs S&P500 vs 사용자 프로파일 기반
   - 판정: KEEP — 한국 사용자 대상 제품의 기본 벤치마크로 합리적 재량. 'SPEC §6.1' 귀속 미확인은 라벨 트랙
54. **[KEEP]** `docs/sot 2/Ai-investing-detail/18_data-quality/data_source_quality.md`:197 — fetch 성공 시마다 2차 소스 실시간 교차검증 수행(샘플링/캐시 가드 없음)
   - 선택지: 전수 교차검증(현행, 품질 우선) vs 샘플링/주기적 검증(비용 우선)
   - 판정: KEEP — 품질 우선 설계 재량이고 정본 무모순. rate limit 소모(alpha_vantage 5rpm) 대응 샘플링은 운영 보강 후보
55. **[KEEP]** `docs/sot 2/Ai-investing-detail/18_data-quality/ingestion_quality.md`:305 — is_pass = severity in (OK, MEDIUM) — MEDIUM 위반 통과 정책
   - 선택지: MEDIUM 차단 vs 통과+로그(현행)
   - 판정: KEEP — 심각도 통과선은 운영 정책 재량(HIGH/CRITICAL은 차단됨). MEDIUM 통과 시 WARN 로그/지표 적재 의무화 1줄 권고
56. **[KEEP]** `docs/sot 2/Ai-investing-detail/18_data-quality/pipeline_quality.md`:346 — 스키마 additive 변경(MEDIUM, AUTO_REGISTER)을 품질 게이트 PASS로 처리
   - 선택지: additive 드리프트 차단 vs 자동등록+통과(현행)
   - 판정: KEEP — additive 스키마 자동 수용은 일반적 파이프라인 설계 재량. 운영자 사후 ack 큐 추가를 보강 후보로 기록
57. **[KEEP]** `docs/sot 2/Ai-investing-detail/18_data-quality/source_quality.md`:607 — Tier 분류 0.90/0.70, 교차검증 0.5%/2%, 타임아웃 30s/120s, SLA 5.0x 등 품질 임계 세트
   - 선택지: 임계 상향/하향 스펙트럼
   - 판정: KEEP — §14가 정의하지 않는 품질 운영 임계로 설계 재량. 출처 라벨을 '설계 기본값'으로 정정 권고
58. **[KEEP]** `docs/sot 2/Ai-investing-detail/19_liquidity-cash/emergency_liquidity.md`:666 — MAX_MARKET_IMPACT_PCT=1.0, TARGET_SELF_CUSTODY_RATIO=0.30
   - 선택지: 충격 상한 0.5~2.0%, 자가보관 0.2~0.5
   - 판정: KEEP — §10.2/§14 어디에도 미정의 → 값은 설계 재량으로 유지. SOT 앵커 부재는 라벨 트랙('설계 기본값' 표기)
59. **[KEEP]** `docs/sot 2/Ai-investing-detail/19_liquidity-cash/liquidity_constraints.md`:740 — 계절 유동성 조정의 비대칭 적용(저유동기에만 사이즈 축소, 고유동기 확대 없음)
   - 선택지: 대칭 조정 vs 축소만 비대칭(현행)
   - 판정: KEEP — 고유동기에 사이즈를 늘리지 않는 것은 보수적 리스크 관리 재량. confidence 측과의 적용 차이 주석 권고
60. **[KEEP]** `docs/sot 2/Ai-investing-detail/19_liquidity-cash/liquidity_risk.md`:155 — 3개 유동성 등급이 모두 다를 때 MEDIUM(중간) 채택 합의 규칙
   - 선택지: 최악 등급 채택(더 보수) vs 중간 채택(현행)
   - 판정: KEEP — 동률 해소 규칙은 재량이고 다수결 경로가 우선 적용됨. '보수적'이라는 주석 표현만 '중간값' 으로 보정 권고
61. **[KEEP]** `docs/sot 2/Ai-investing-detail/20_strategy-detail/quant/crypto.md`:245 — Grid confidence = filled_ratio×0.5 + atr_stability×0.5 (신규 그리드는 상한 0.5)
   - 선택지: filled_ratio 가중 축소/부트스트랩 보정 vs 신규 그리드 저신뢰(현행)
   - 판정: KEEP — 체결 이력 없는 신규 그리드의 낮은 confidence는 의도된 보수성으로 해석 가능. 초기 신호의 51% Gate 상호작용(웜업 기간) 명시 권고
62. **[KEEP]** `docs/sot 2/Ai-investing-detail/20_strategy-detail/quant/crypto.md`:312 — NUM_GRIDS=10, ATR_MULTIPLIER=3.0, BASE_AMOUNT, WHALE_THRESHOLD 등 전략 파라미터 값
   - 선택지: 그리드 5~20, ATR 배수 2~4
   - 판정: KEEP — 값 자체는 설계 재량이고 정본 무모순. 'SPEC §14(기술스택 LOCK)' 귀속은 범위 드리프트로 라벨 정정(객관 트랙) — 같은 파일 τ행이 LOCK-V12-03으로 정정된 portfolio_risk 선례 준용
63. **[KEEP]** `docs/sot 2/Ai-investing-detail/20_strategy-detail/quant/crypto.md`:1083 — DeFi Yield: 수익 풀 없으면(IL로 일시 음수 포함) 자동 WITHDRAW 정책
   - 선택지: 즉시 철수(현행, 보수) vs 음수 지속기간 조건 후 철수
   - 판정: KEEP — IL 일시 음수에도 철수하는 것은 자본 보호 우선의 보수적 재량. net_yield 음수 지속 N일 조건은 V2 보강 후보
64. **[KEEP]** `docs/sot 2/Ai-investing-detail/20_strategy-detail/quant/event_driven.md`:539 — 머저암 딜 실패 하방을 downside = spread×0.8로 모델링('보수적 가정' 주석)
   - 선택지: 스프레드 비례(현행) vs 고정 10%+ 급락 가정 vs 역사적 브레이크 분포
   - 판정: KEEP — 하방 모델 선택은 재량이고 주석으로 가정 명시. E7의 >10% 급락 경로가 별도 방어를 제공. 역사 분포 캘리브레이션 후보
65. **[KEEP]** `docs/sot 2/Ai-investing-detail/20_strategy-detail/quant/options.md`:289 — 커버드콜 confidence의 premium_yield×20 스케일 상수(0.3 가중)
   - 선택지: ×20(1.7% 수익률에서 만점) vs 다른 스케일/시그모이드
   - 판정: KEEP — confidence 합성 상수는 재량(전형 프리미엄 1~3%를 0~1로 사상하는 설계). 근거 주석 추가 권고
66. **[KEEP]** `docs/sot 2/Ai-investing-detail/20_strategy-detail/quant/options.md`:3461 — MIN_OPEN_INTEREST=0 (비활성 기본값, OI==0은 전처리 제거 주석)
   - 선택지: 0(비활성, 전처리 위임) vs 양수 임계 활성화
   - 판정: KEEP — 전처리에서 OI==0 제거를 주석으로 명시했고 파라미터는 향후 튜닝 슬롯으로 유지하는 재량. 주석 그대로 유지
67. **[KEEP]** `docs/sot 2/Ai-investing-detail/20_strategy-detail/quant/options.md`:3509 — OI 집중도 정규화 상수 total_oi/100000
   - 선택지: 고정 상수(현행) vs 심볼별 히스토리 분위수 정규화
   - 판정: KEEP — Max Pain 보조지표의 휴리스틱 상수로 재량. 시장별(KR/US) 캘리브레이션 후보로 기록
68. **[KEEP]** `docs/sot 2/Ai-investing-detail/20_strategy-detail/quant/options.md`:3399 — 원거리 DTE(>14)는 dte_weight 0.5 감쇠로 신호 유지(차단 아님)
   - 선택지: DTE 게이트로 차단 vs 감쇠 유지(현행)
   - 판정: KEEP — 보조지표 신호를 감쇠로 살려두고 최종 게이트(0.51)에 위임하는 구조는 재량. '만기 근접 시 최대 유효' 의도와 모순 없음(감쇠가 그 의도 구현)
69. **[KEEP]** `docs/sot 2/Ai-investing-detail/20_strategy-detail/quant/portfolio_risk.md`:349 — BL/사이징 하이퍼파라미터 δ=2.5, MAX_TRACKING_ERROR=0.10, KELLY_MULTIPLIER=0.5, RISK_PER_TRADE=0.02 등
   - 선택지: 문헌 표준 범위 내 조정(δ 2~3, half-Kelly 등)
   - 판정: KEEP — He-Litterman(1999) 등 문헌 표준값으로 합리. τ행이 이미 LOCK-V12-03(5-3 AUTHORITY_CHAIN) 인용으로 정정된 선례에 따라 잔여 행의 '§14 기술스택' 라벨도 동일 방식 정정 권고(값 변경 불요)
70. **[KEEP]** `docs/sot 2/Ai-investing-detail/20_strategy-detail/technical/chart_pattern_continuation.md`:1297 — Flag 패턴 탐지를 삼중 루프(flag_end×flag_len×pole_len) 의사코드로 명세
   - 선택지: 벡터화/조기종료 명세 vs 탐색 공간 명료성 우선(현행)
   - 판정: KEEP — L3 의사코드의 명료성 우선은 재량; E6 80ms 목표는 구현 단계 최적화(조기 종료, 증분 탐색)로 충족 가능. 구현 노트 1줄 권고
71. **[KEEP]** `docs/sot 2/Ai-investing-detail/20_strategy-detail/technical/harmonic.md`:267 — 거래량 미달 시 volume_factor 0.7 고정 → 저패턴가중(Crab 0.60 등) 패턴은 0.51 게이트 미달로 suppress
   - 선택지: 거래량 확인을 사실상 필수화(현행) vs volume_factor 완화/패턴 weight 상향
   - 판정: KEEP — 거래량 미확인 하모닉 신호의 suppress는 의도된 보수 게이트로 해석 가능하며 §6.1과 무모순. 패턴별 weight 재캘리브레이션은 백테스트 Evidence 확보 후 검토
72. **[KEEP]** `docs/sot 2/Ai-investing-detail/20_strategy-detail/technical/momentum_oscillator.md`:166 — RSI류 confidence를 과매수/과매도 '깊이' 정규화로 정의(승률 캘리브레이션 아님)
   - 선택지: 깊이 스케일(현행) vs 백테스트 승률 매핑
   - 판정: KEEP — 경계 신호(얕은 과매도)가 0.51 미달로 억제되는 것은 보수적 재량. confidence 의미론(깊이∝확신) 문서화 권고
73. **[KEEP]** `docs/sot 2/Ai-investing-detail/20_strategy-detail/technical/trend_following.md`:284 — MA Crossover SELL에 추세필터 동조(not above_trend) 요구 — 200MA 위 데드크로스는 HOLD
   - 선택지: 데드크로스 즉시 SELL vs 추세필터 결합 비대칭(현행)
   - 판정: KEEP — 상승추세 중 일시 데드크로스를 무시하는 것은 추세추종 철학의 재량. 보유 포지션 출구 지연 리스크는 트레일링 스톱 병행으로 보완 권고
74. **[KEEP]** `docs/sot 2/Ai-investing-detail/20_strategy-detail/technical/rsi_bb.md`:50 — Wilder RSI를 봉별 반복 루프 의사코드로 명세(ewm 벡터화 대신)
   - 선택지: ewm(alpha=1/period) 벡터화 vs 정의 그대로의 루프(현행)
   - 판정: KEEP — Wilder 정의를 직역한 명세는 교육적 명료성 재량; 성능 목표는 구현 단계 ewm 치환으로 충족. 구현 노트 권고
75. **[KEEP]** `docs/sot 2/Ai-investing-detail/20_strategy-detail/technical/volume.md`:319 — Value Area 70% 상수 채택
   - 선택지: 70%(시장 표준) vs 68%(1σ) 등
   - 판정: KEEP — TPO/볼륨프로파일 시장 표준 상수로 표 자체가 '시장 표준' 병기. supply_demand_zone L428의 '업계 표준(CBOT)' 표기 선례대로 §14 라벨만 정정 권고
76. **[KEEP]** `docs/sot 2/Ai-investing-detail/20_strategy-detail/technical/volume.md`:147 — Volume Profile confidence = 이탈 깊이/(VAH−VAL) 비례(얕은 이탈은 0.51 미달로 억제)
   - 선택지: 깊이 비례(현행) vs 고정 confidence + 별도 필터
   - 판정: KEEP — 얕은 VAL/VAH 이탈 억제는 의도된 보수성이고 본문에 '클램프 0~1' 명시. 좁은 VA 분모 가드(최소 폭)만 보강 후보
77. **[KEEP]** `docs/sot 2/Ai-investing-detail/_templates/L3_EXAMPLE_STRATEGY.md`:90 — 템플릿 예시 confidence = |histogram|/rolling_max(50) 정규화(승률 비연동 모멘텀 프록시)
   - 선택지: 모멘텀 프록시 예시(현행) vs 승률 캘리브레이션 예시
   - 판정: KEEP — 템플릿의 예시 수준 재량. '예시이며 전략별 캘리브레이션 필요' 주석 1줄 추가 권고
78. **[KEEP]** `docs/sot 2/Ai-investing-detail/_test_l3_macd.md`:236 — MACD EMA 기간 (12, 26, 9) 채택
   - 선택지: 12/26/9(시장 표준) vs 변형 주기
   - 판정: KEEP — MACD 보편 표준 파라미터로 값 무모순. 'SPEC §14(기술스택 LOCK)' 분류만 전략 파라미터로 재배정 권고(라벨 트랙)
79. **[KEEP]** `docs/sot 2/Ai-investing-detail/02_behavioral-finance/cognitive_debiasing.md`:380 — 디바이어싱 체크리스트를 16항목 pass_rate≥0.75 단일 게이트로 구성(stop_loss 등도 항목 중 하나)
   - 선택지: 위험 필수항목 hard-fail 분리 vs 통과율 단일 게이트(현행)
   - 판정: KEEP — 게이트 구성 방식은 재량이고 정본 미규정. stop_loss/사이징의 hard-gate 분리는 리스크 관리 보강 후보로 기록
80. **[KEEP]** `docs/sot 2/Ai-investing-detail/03_macro-sector-stock/industry_value_chain.md`:287 — 병목 식별에 exact betweenness centrality 채택(5000노드 <1s 목표 병기)
   - 선택지: 근사 betweenness(k-샘플링)/사전계산 vs exact(현행)
   - 판정: KEEP — 알고리즘 정확도 우선 선택은 재량; 5k 노드 규모는 구현 최적화(샘플링·캐시)로 목표 충족 가능. E6에 근사 허용 여부 1줄 권고
81. **[KEEP]** `docs/sot 2/Ai-investing-detail/04_performance-attribution/factor_attribution.md`:149 — 잔차 알파 지속성 판정에 Ljung-Box(잔차 무자기상관) 단일 검정 사용
   - 선택지: 롤링 알파/OOS 유지율/기간별 t-stat vs LB 단독(현행)
   - 판정: KEEP — 검정 선택은 방법론 재량이고 정본 미규정. 'is_persistent' 명칭을 'residual_clean' 수준으로 보수화하거나 보조 검정 병기 권고
82. **[KEEP]** `docs/sot 2/Ai-investing-detail/05_backtest-integrity/data_quality_preprocess.md`:19 — 데이터 기간 기준: '3년→5년 확대' 라벨과 2019~2026 고정 시작 범위 병기
   - 선택지: rolling 5년 vs 고정 시작점 2019(코로나 포함)
   - 판정: KEEP — 위기 레짐(2020) 포함을 위한 고정 시작점 선택은 재량이고 Acceptance(2019~2026)와 일치. '5년' 라벨을 '2019-01-01부터'로 명확화하는 Decision 1줄 권고
83. **[KEEP]** `docs/sot 2/Ai-investing-detail/07_universe-management/cross_asset_universe.md`:529 — 유니버스 사이즈 최적화를 커버리지 한계효용-한계비용 등식화 단순 모델로 정의
   - 선택지: 예산 제약 최적화/SLA 제약 vs 한계 등식화(현행)
   - 판정: KEEP — 최적화 모델 선택은 재량. 커버리지 점수 1점의 USD 가치 계수를 명시해 단위 정합성 보강 권고
84. **[KEEP]** `docs/sot 2/Ai-investing-detail/09_model-governance/model_security.md`:134 — 모델 추출 방어로 예측 노이즈 주입(noise_scale=0.01, seed 기본 None) 채택
   - 선택지: 노이즈 방어 전체 적용 vs 외부 API 응답에만 한정
   - 판정: KEEP — 추출 방어 메커니즘 선택은 보안-재현성 트레이드오프 재량. 내부 의사결정 신호 경로 제외와 감사 로그 명시를 권고
85. **[KEEP]** `docs/sot 2/Ai-investing-detail/11_tca/cost_benchmarking.md`:302 — 분석 유형별 상이한 최소 표본 기준(최소 5영업일/랭킹 20일/권장 30일)
   - 선택지: 단일 최소 표본 vs 분석 유형별 차등(현행)
   - 판정: KEEP — 분석 목적별 통계 요건 차등은 재량. 정책 테이블 한 곳으로 모아 함수들이 참조하게 일원화 권고
86. **[KEEP]** `docs/sot 2/Ai-investing-detail/16_global-geopolitics/country_risk.md`:96 — CDS 평가를 절대 수준 없이 상대 z-score 단독으로 산정
   - 선택지: 절대 임계 병행 vs 상대 z-score 단독(현행)
   - 판정: KEEP — 변화 감지 중심 설계는 재량이고 정본 미규정. 고착 고위험(고CDS 저변동) 케이스 대응으로 절대 레벨 항 병행을 보강 후보로 기록
87. **[KEEP]** `docs/sot 2/Ai-investing-detail/20_strategy-detail/quant/ml_ai.md`:224 — Adapter 검증은 추론 lookback(SEQUENCE_LENGTH=60 등) 기준, E1의 학습 최소 표본(500/1000봉)과 분리 운용
   - 선택지: 학습/추론 요구 통합 단일 게이트 vs 분리(현행)
   - 판정: KEEP — 추론 경로 최소 봉수와 학습 최소 표본은 본질적으로 별개 요구로 분리가 타당. training_min_bars/inference_lookback 스키마 분리 명시 권고
88. **[KEEP]** `docs/sot 2/Ai-investing-detail/20_strategy-detail/quant/portfolio_risk.md`:1999 — 보호성 exit(트레일링 스톱 발동) 신호도 51% Gate 일괄 적용 대상에 포함
   - 선택지: exit 신호 게이트 우회(risk_urgency 별도 채널) vs 일괄 적용(현행)
   - 판정: KEEP — 게이트 일괄 적용은 파이프라인 단순성 재량이고 §6.1 명문 위반 아님. 단 §10.2 보호 철학과의 긴장을 고려해 exit 신호의 confidence 산정 방식(거리 기반 아님) 재정의를 V2 검토 권고
89. **[KEEP]** `docs/sot 2/Ai-investing-detail/20_strategy-detail/technical/harmonic.md`:14 — 하모닉 패턴별 '역사적 성공률' 60~75%를 pattern_weight로 채택
   - 선택지: 문헌/관행 수치 채택(현행) vs 자체 백테스트 보정 후 적용
   - 판정: KEEP — 하모닉 트레이딩 문헌의 관행 수치를 초기값으로 쓰는 것은 재량. 자체 백테스트 Evidence 연결 전까지 '미검증 파라미터' 주석 표기 권고

> notes: 방법: 입력 4종 전수 검토 — clc 579건(tight 467건은 전부 clc의 부분집합으로 ID 동일), gpt 473건, mf_in(확정 29+검증중 25)은 제외 기준으로 사용. 제외: (1) mf_in과 동일/중복 finding ~50건, (2) clc verify=refuted 79건(디스크 실측 반박), (3) SYNONYM/표기·오타류(T5 대부분, 라벨 오기, 카운트 불일치), (4) 객관결함 — 내부 모순(E1↔E2↔E7↔E8 불일치), 스키마-구현 불일치, 정본 확정 위반(51% Gate 재정의 T6-336/337/397/398, §8.3/§10.2 오귀속 확정건, LOCK 미집행), 보안 omission, 수학/단위 오류. 잔여에서 '사실이지만 검증 가능한 정본 위반 없이 설계자가 고를 수 있는 값/아키텍처/정책'만 등재. 89건 도출 — 원판정 앵커 89와 수치 일치하나 원 리스트가 유실되어 ID 단위 동일성은 보장 불가(독립 재도출). 전 89건 디스크 실측(file:line) 완료: 라인·값·주석 전부 현존 확인(스팟체크: EMA 20/50, N_REGIMES=6, THRESHOLD=0.15, etf_min_age_days=365

### 2-2_COND-Modules-Detail (67건)

1. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\01_cat-a-ai-ml\cond_011_shap_lime.md`:45,430 — 입력 스키마 상한(background_sample_size le=1000)과 런타임 캡(max_background_samples=500)을 이원화한 검증 계층 선택
   - 선택지: 스키마 상한을 500으로 일치 / 현행(스키마 여유+런타임 캡) / 캡 단일화
   - 판정: KEEP — 정본(RULE/PLAN/LOCK) 규정 없음. 스키마 여유+운영 캡 이원화는 운영자 상향 여지를 주는 합리적 선택, E3에 min(request,config) clamp 주석만 L3 보강 권장
2. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\01_cat-a-ai-ml\cond_012_batch_processing.md`:202 — deadline 모드 정렬 키를 상대 지연예산(req.max_latency_ms)으로 쓰는 근사 EDF 스케줄링 선택
   - 선택지: 절대 deadline(enqueue+budget) EDF / 현행 상대 예산 정렬
   - 판정: KEEP — 단일 배치 윈도(max_wait_ms) 내 도착시각 편차가 작아 근사 EDF로 합리적, 정본 위반 없음. 절대 EDF는 L3 최적화 선택지
3. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\01_cat-a-ai-ml\cond_025_emotion_pattern_learning.md`:515 — 60초급 LSTM 학습 모듈에 retry_policy(max_retries=1, backoff 2000ms)를 부여한 재시도 정책 선택
   - 선택지: 재시도 0회 / 1회(현행) / 멱등키 도입 후 재시도
   - 판정: KEEP — LOCK-CD-10 표준 필드의 모듈별 값 선택. 일시 장애 1회 재시도는 합리적이며 결정적 실패(MODEL_TRAINING_FAILED)는 E4 fallback에서 분리 가능
4. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\01_cat-a-ai-ml\cond_026_bias_audit.md`:226 — 감사 예측 시 보호속성을 피처에서 무조건 제외하는 감사 방법론 선택
   - 선택지: 보호속성 포함 예측 / 무조건 제외(현행) / 모델 학습계약 기반 동적 결정
   - 판정: KEEP — 공정성 감사에서 보호속성 제외는 표준 관행이고 정본 무모순. 모델별 피처 계약 불일치는 L3 ModelRegistry 메타데이터로 해소 권장
5. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\01_cat-a-ai-ml\cond_085_crewai_role_engine.md`:293-296,515 — 비용 한도를 사전 추정(Blue Node CostGate L515)+사후 정산 검증(step7)으로 집행하고 실행 중 kill-switch는 두지 않는 비용 집행 전략
   - 선택지: 실시간 중단 콜백(hard-stop) / 사전추정+사후정산(현행)
   - 판정: KEEP — CostGate가 실행 전 '에이전트 수×추론 비용'을 검증해 게이트 정본(§B.7.1)과 무모순. CrewAI 런타임 제약상 mid-run 중단은 L3 강화 선택지
6. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\01_cat-a-ai-ml\cond_085_crewai_role_engine.md`:603 — 비멱등·과금성 멀티에이전트 워크플로우에 retry_policy(max_retries=1)를 부여한 선택
   - 선택지: 재시도 0회 / 1회(현행) / 체크포인트+멱등키 후 재시도
   - 판정: KEEP — 표준 5필드 값 선택이며 정본 무모순. 비용 중복 우려는 cost_limit_usd 사후 검증으로 상쇄, 멱등키는 L3 보강 여지
7. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\01_cat-a-ai-ml\cond_026_bias_audit.md`:573 — severity_thresholds 'low':0.80을 pass 기준(default_threshold 0.8)과 동일 경계로 둔 임계값 선택
   - 선택지: low 경계를 0.85 등으로 분리 / 동일 경계(현행, 통과+low=경계 통과 신호)
   - 판정: KEEP — DI=0.80이 '통과하되 low 편향 주의'로 표기되는 것은 경계 신호로서 의도 가능한 분류 설계, 정본 임계 규정 없음
8. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\01_cat-a-ai-ml\cond_105_s5_feedback_learning.md`:186 — auto 모드에서 corrections 비율 ≥0.3이면 DPO를 선택하는 휴리스틱 게이트 값/기준 선택
   - 선택지: pair 가용성 직접 검사 / corrections 비율 0.3(현행) / 혼합 기준
   - 판정: KEEP — 임계 0.3은 설계 휴리스틱으로 정본 무모순. build_dpo_pairs 결과 0쌍 시 RLHF 폴백 한 줄을 L3 보강 권장
9. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\01_cat-a-ai-ml\cond_105_s5_feedback_learning.md`:35 — timestamp 기본값을 datetime.utcnow(naive UTC)로 둔 타임스탬프 관례 선택
   - 선택지: datetime.now(timezone.utc) tz-aware / utcnow(현행)
   - 판정: KEEP — 의사코드 수준 관례 선택으로 정본 규정 없음. L3 구현 시 tz-aware(timezone.utc) 통일 권장
10. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\02_cat-b-knowledge\cond_017_memgpt_letta_memory.md`:46,100 — 'recall'을 operation 이름(L46)과 tier 이름(L100)에 중복 사용하는 용어 선택
   - 선택지: tier명 변경(예: recent) / MemGPT 원전 용어 유지(현행)
   - 판정: KEEP — MemGPT/Letta 원전 용어 충실성을 택한 명명 선택, 정본 무모순. 용어집 주석 1줄 보강 여지
11. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\02_cat-b-knowledge\cond_018_cognee_knowledge_graph.md`:301 — 엣지 신뢰도 갱신 가중치 existing*0.6+new*0.4 고정값 선택
   - 선택지: 대칭 0.5/0.5 / 시간감쇠 가중 / 현행 0.6/0.4 보수 갱신
   - 판정: KEEP — 기존 증거를 보수적으로 우대하는 KG 안정화 선택, 정본 무모순. config 노출은 L3 선택지
12. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\02_cat-b-knowledge\cond_020_knowledge_conflict_detection.md`:425 — scan_completeness를 '필터 후 후보쌍/이론적 전체쌍'으로 정의한 메트릭 정의 선택
   - 선택지: 실제 비교쌍 기준 / 필터 후 후보쌍 기준(현행)
   - 판정: KEEP — 메트릭 정의 선택으로 정본 무모순. 명칭 의미(semantic-candidate coverage) 주석 보강 권장
13. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\02_cat-b-knowledge\cond_023_temporal_knowledge.md`:88 — valid_from/to에 '(transaction time)' 라벨을 부여한 bi-temporal 축 명명 선택(표준 관례와 교차)
   - 선택지: 표준 명명(valid=실세계축)으로 스왑 / 현행 내부 일관 명명 유지
   - 판정: KEEP — 파일 내부적으로 일관 사용되어 동작 모순 없음(정본 명명 규정 없음). 표준 용어와의 매핑 주석 보강 권장
14. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\02_cat-b-knowledge\cond_023_temporal_knowledge.md`:223-224 — query_at 연산이 as_of와 effective_at에 동일 target_time을 쓰는 단일 타임스탬프 API 단순화 선택
   - 선택지: 이축 독립 파라미터(T1,T2) / 단일 시점 질의(현행)
   - 판정: KEEP — '시점 T의 지식 상태' 단일 질의는 유효한 API 스코프 선택. 이축 분리 질의는 L3 확장 연산으로 추가 가능
15. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\02_cat-b-knowledge\cond_024_predictive_knowledge_surfing.md`:297 — 예측 confidence를 상위 후보 relevance_score 단순 평균으로 산출(Markov 전이확률·코사인 혼합)하는 휴리스틱 선택
   - 선택지: 소스별 정규화 후 결합 / 단순 평균(현행)
   - 판정: KEEP — 프리페치 우선순위용 경량 휴리스틱으로 합리적, 정본 무모순. 소스별 스케일 정규화는 L3 개선 여지
16. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\02_cat-b-knowledge\cond_107_morpheme_tokenizer.md`:516 — health를 주 엔진(mecab/kiwi)+도메인사전으로만 정의하고 fallback 엔진(komoran)을 제외한 health 범위 선택
   - 선택지: komoran 포함 AND / 주 엔진만(현행, fallback은 degraded 신호)
   - 판정: KEEP — fallback 엔진 다운이 모듈 전체 unhealthy로 번지지 않게 한 가용성 설계로 합리적. komoran 상태는 details 노출로 L3 보강 권장
17. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\02_cat-b-knowledge\cond_108_zettelkasten_advanced.md`:751 — embedding_dim=1024 단일 필드+'Matryoshka 256 for search' 주석(검색 차원 미구현)의 임베딩 차원 전략 선택
   - 선택지: search_dim 별도 config 즉시 도입 / 1024 단일+향후 최적화 주석(현행)
   - 판정: KEEP — DEC-005(BGE-M3) 준수 하에 256 절단은 명시된 향후 최적화 옵션. 미구현이 정본 모순 아님, L3에서 search_dim 필드화 권장
18. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\03_cat-c-ops-infra\core\cond_029_version_control.md`:136,154 — merge 충돌을 에러가 아닌 Ok(merge_conflicts) 응답으로 반환하는 git식 결과 모델 선택
   - 선택지: COND_029_MERGE_CONFLICT Err 반환 / Ok+conflicts 목록(현행)
   - 판정: KEEP — E4 fallback이 FB_COND_029_RETURN_CONFLICTS로 '충돌 반환'을 명시해 본문과 정합. 충돌은 정상 워크플로 산출물이라는 설계 선택
19. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\03_cat-c-ops-infra\core\cond_030_distributed_tracing.md`:135 — 입력 캡(le=86400)과 config 기본값(max_query_window_seconds=86400)을 동일하게 둔 기본값 선택(기본 상태에서 QUERY_TOO_LARGE 미발동)
   - 선택지: config 기본을 86400 미만으로 / 동일 기본+운영자 하향 시 활성(현행)
   - 판정: KEEP — 운영자가 윈도를 줄이면 활성화되는 2차 방어선으로 dead code 아님, 정본 무모순
20. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\03_cat-c-ops-infra\core\cond_075_search_engine_server.md`:127 — 벡터 검색 페이지네이션을 top_k=size*page의 offset식으로 처리(cursor 없음)하는 단순화 선택
   - 선택지: cursor 기반 / offset식 top_k(현행)
   - 판정: KEEP — 얕은 페이지 중심 워크로드에 합리적 단순화, 정본 무모순. 깊은 페이지 비용은 L3 cursor 보강 여지
21. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\03_cat-c-ops-infra\e-series\cond_037_e026_api_gateway.md`:339 — retry_policy를 LOCK-CD-10 표준 5필드 선언으로 두고 E3 내 재시도 로직을 두지 않는(호출측/프레임워크 소비) 책임 배치 선택
   - 선택지: 모듈 내 재시도 구현 / 선언적 config+오케스트레이터 집행(현행)
   - 판정: KEEP — LOCK-CD-10이 ModuleConfig 표준 필드로 규정한 선언 계약이며 E3 미구현은 모순 아님(39모듈 공통 패턴)
22. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\03_cat-c-ops-infra\e-series\cond_041_e030_healthcheck.md`:33 — operation Literal에 'propagate'를 추가해 SOT 3종 probe 외 의존 헬스 전파를 4번째 연산으로 확장한 capability 설계
   - 선택지: SOT 3종만 / propagate 포함 4종(현행)
   - 판정: KEEP — SOT probe_type 3종은 프로브 분류이고 연산 확장은 금지되지 않음. 전파는 COND-072 연계의 의도된 확장
23. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\03_cat-c-ops-infra\e-series\cond_041_e030_healthcheck.md`:107 — 헬스체크 모듈도 39개 e-series 공통의 '자체 백엔드 미가용 fast-fail' 가드를 동일 적용하는 일관성 선택
   - 선택지: 헬스체크 전용 예외(백엔드 다운도 보고) / 공통 가드 유지(현행)
   - 판정: KEEP — 가드 대상은 모듈 자체 저장 인프라이지 프로브 대상이 아니므로 자기모순 아님. 공통 패턴 유지가 정본(골격 일관성)과 정합
24. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\03_cat-c-ops-infra\e-series\cond_047_e039_feature_flag.md`:33 — SOT 3연산(evaluate/set/rollout) 외 'kill'을 추가한 kill-switch 확장 선택
   - 선택지: 3종 유지 / kill 포함 4종(현행)
   - 판정: KEEP — 안전장치 연산 추가는 SOT 시그니처를 침해하지 않는 상향 확장, capabilities에 일관 반영됨
25. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\03_cat-c-ops-infra\e-series\cond_047_e039_feature_flag.md`:338 — timeout_ms=80을 p99 Alert 경계(>80ms)와 동일값으로 둔 임계값 선택
   - 선택지: timeout을 alert보다 크게(예 160ms) / 동치(현행, 초과는 에러율 알람으로 포착)
   - 판정: KEEP — 플래그 평가는 fail-fast가 합리적이고 초과분은 에러율 SLA로 관측됨. P2-1 부하시험 보강 예정 명시와 정합
26. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\03_cat-c-ops-infra\e-series\cond_056_e050_disaster_recovery.md`:226 — 이벤트 구동 DR 모듈에 처리량 SLA ≥1 req/s(Alert <1)를 부여한 골격 SLA 값 선택
   - 선택지: 처리량 메트릭 제외 / 최소값 1req/s 골격(현행)
   - 판정: KEEP — 39모듈 전수 4메트릭 골격 프레임(I-04)의 차등 최소값이며 'L2 골격, P2-1 부하시험 L3 보강' 명시로 정본 정합
27. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\03_cat-c-ops-infra\e-series\cond_052_e046_certificate_mgmt.md`:311 — L2 골격 health_check가 latency_ms=0 상수를 반환하는 스텁 수준 선택(052~056 동일)
   - 선택지: 실측 elapsed 즉시 구현 / L2 스텁+L3 실측 보강(현행)
   - 판정: KEEP — L2 골격 단계의 명시적 단순화로 정본(단계적 보강 계획)과 정합. L3에서 elapsed 실측 대체 권장
28. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\03_cat-c-ops-infra\e-series\cond_057_e069_perf_profiling.md`:224 — 프로파일링 모듈 p99 5000ms/Alert 20000ms의 느슨한 SLA 값 선택
   - 선택지: 엄격 SLA / 연산 특성 반영 느슨한 골격값(현행)
   - 판정: KEEP — 프로파일링은 본질적으로 장시간 연산이며 골격 SLA 차등 프레임 내 값 선택. P2-1 실측 보강 예정
29. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\03_cat-c-ops-infra\e-series\cond_058_e070_capacity_planning.md`:59 — SOT 3출력(forecast/scaling_recommendation/cost_estimate)을 L2에서 단일 result envelope로 접고 L3 typed 보강을 예고한 스키마 단계화 선택
   - 선택지: 즉시 typed 3필드 / L2 envelope+L3 정밀화(현행)
   - 판정: KEEP — forward declaration과 'L3 보강 예정'이 본문에 명시된 단계적 설계로 SOT 시그니처 추적성 유지
30. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\03_cat-c-ops-infra\e-series\cond_059_e071_sla_monitoring.md`:337 — timeout_ms=800을 p99 Alert 경계(>800ms)와 동치로 둔 임계값 선택
   - 선택지: timeout>alert 분리 / 동치(현행)
   - 판정: KEEP — cond_047과 동일한 fail-fast 일관 패턴, 초과는 에러율로 관측. 정본 무모순
31. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\03_cat-c-ops-infra\e-series\cond_066_e084_infra_autoscaling.md`:220 — 오토스케일링 제어연산에 p99 5000ms/throughput 100req/s 골격 SLA를 부여한 값 선택
   - 선택지: 이벤트성 연산용 별도 메트릭 / 골격 4메트릭 차등값(현행)
   - 판정: KEEP — I-04 전수 골격 프레임의 차등값이며 P2-1 부하시험 보강 예정 명시로 정합
32. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\03_cat-c-ops-infra\e-series\cond_063_e081_blue_green_deploy.md`:225,338 — 배포 모듈 p99 10000ms/Alert 40000ms/timeout_ms 40000 동치 구성의 골격 SLA·타임아웃 값 선택
   - 선택지: 분 단위 별도 배포 타임아웃 / 골격 동치값(현행)
   - 판정: KEEP — L2 골격 차등값(p99=10000ms 명시) + P2-1 부하시험 데이터 기반 L3 보강 예정. 정본 모순 없음
33. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\03_cat-c-ops-infra\e-series\cond_064_e082_canary_deploy.md`:221 — 카나리 배포에 블루그린과 동일 골격 SLA(p99 10000ms)·단일 타임아웃을 적용하고 rollback 전용 하한 타임아웃을 두지 않은 선택
   - 선택지: rollback 전용 짧은 타임아웃 추가 / 단일 타임아웃(현행)
   - 판정: KEEP — 골격 단계 단순화로 합리적. 안전연산 차등 타임아웃은 L3 보강 선택지
34. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\03_cat-c-ops-infra\e-series\cond_065_e083_rolling_update.md`:98 — abort/pause 안전연산을 start/resume과 동일 파이프라인(쿼터·가드 포함)으로 처리하는 균일 디스패치 선택
   - 선택지: 안전연산 쿼터 면제·우선 처리 / 균일 파이프라인(현행)
   - 판정: KEEP — 39모듈 공통 E3 골격의 일관성 유지 선택, 정본 무모순. 안전연산 우선순위는 L3 보강 여지
35. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\03_cat-c-ops-infra\e-series\cond_071_e090_graceful_shutdown.md`:339 — graceful shutdown 모듈에도 표준 retry_policy(max_retries=2)를 일괄 적용한 선택
   - 선택지: shutdown 전용 retry 0 / 표준 5필드 일괄(현행)
   - 판정: KEEP — LOCK-CD-10 표준 필드의 골격 일괄값이며 집행은 호출측 정책. drain/save 멱등성 주석은 L3 보강 권장
36. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\04_cat-d-media\cond_080_style_transfer.md`:459 — max_vram_mb=6144(6GB) VRAM 예산 값 선택(CLIP-guided 8GB 요구 백엔드는 예산 내 거부됨)
   - 선택지: 8192로 상향 / 6144 유지(타깃 GPU 보수 예산)
   - 판정: KEEP — 타깃 하드웨어 예산 선택으로 정본 무모순. CLIP 경로는 VRAM 가드로 일관 거부되므로 동작 모순 아님, 주석 보강 여지
37. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\03_cat-c-ops-infra\e-series\cond_072_e091_dependency_health_propagation.md`:310 — health_check latency_ms=0 상수 반환의 L2 스텁 선택(073 동일)
   - 선택지: 실측 elapsed / L2 스텁(현행)
   - 판정: KEEP — cond_052 계열과 동일한 골격 단계 단순화, L3 실측 대체 권장
38. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\03_cat-c-ops-infra\e-series\cond_073_e092_ops_dashboard_data.md`:242 — happy-path 테스트 상한을 SLA 목표(≤200ms)가 아닌 Alert 경계(<800ms)로 잡은 테스트 여유폭 선택
   - 선택지: 목표치 기준 단언 / Alert 경계 기준 단언(현행)
   - 판정: KEEP — CI 환경 변동성을 감안한 테스트 상한 선택으로 정본 무모순. SLA 회귀는 E6 모니터링이 담당
39. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\04_cat-d-media\cond_080_style_transfer.md`:190 — 모든 출력 포맷에 quality=92 통일 저장 파라미터를 전달(PNG에는 무의미하나 무해)하는 단순화 선택
   - 선택지: 포맷별 분기 / 통일 파라미터(현행)
   - 판정: KEEP — PNG는 무손실이라 파라미터가 무시될 뿐 동작 결함 아님. 통일 파라미터는 합리적 단순화
40. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\06_cat-f-wellbeing\cond_099_social_relationship.md`:227-229 — isolation_risk를 3개 불리언의 가중합(0.5/0.3/0.2, 8단계 이산값)으로 산출하는 스코어링 설계 선택
   - 선택지: 연속 스코어 모델 / 이산 가중합(현행, 해석 용이)
   - 판정: KEEP — 임계 0.7 알림과 결합해 해석 가능성을 우선한 휴리스틱, 정본 무모순. 연속화는 L3 개선 여지
41. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\06_cat-f-wellbeing\cond_116_wellbeing_dashboard.md`:142 — progress_pct를 0.0~2.0(0~200% 분수) 범위로 표현하는 단위/명명 선택
   - 선택지: 0~200 정수 % / 0~2.0 분수(현행)+설명 보강
   - 판정: KEEP — 초과달성(>100%) 표현을 위한 범위 선택으로 정본 무모순. description에 '1.0=100%' 명시 보강 권장
42. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\07_cat-g-integration\cond_090_notion_obsidian_sync.md`:452 — 내부 처리량 V2 목표 ≥20 req/s를 Notion rate limit 3 req/s × coalesce 전제로 설정한 SLA 값 선택
   - 선택지: 3req/s로 하향 / coalesce 전제 20req/s(현행)
   - 판정: KEEP — 변경 병합(coalesce)으로 내부 요청:외부 호출이 N:1이 되므로 양립 가능, 표에 전제가 명시되어 정합
43. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\07_cat-g-integration\cond_090_notion_obsidian_sync.md`:547-548 — RetryPolicy.retry_on에 RATE_LIMIT_EXCEEDED를 포함(지수 백오프 전제)한 재시도 대상 선택
   - 선택지: 429 재시도 제외 / 백오프+재시도(현행, Retry-After 존중은 L3)
   - 판정: KEEP — 지수 백오프 기반 429 재시도는 표준 관행이며 backoff='exponential'이 명시됨. Retry-After 헤더 존중 주석만 L3 보강
44. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\08_e-series-ops\cond_039_e028_metric_collection.md`:390 — 메트릭 노출 포트 기본값 prometheus_port=9090(관례상 Prometheus 서버 포트) 선택
   - 선택지: 9091+ 등 exporter 관례 포트 / 9090(현행, 운영 설정으로 변경 가능)
   - 판정: KEEP — 포트 기본값은 배포 설정 선택이고 정본 규정 없음. 동거 배포 충돌 가능성 주석 보강 여지
45. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\08_e-series-ops\cond_038_e027_log_collection.md`:192-198 — PII 마스킹 범위를 message(정규식)+user_id(해시)+metadata(deep_mask)로 한정한 마스킹 경계 선택
   - 선택지: 전 필드 스캔 / 지정 경로 마스킹(현행), 타 모듈 자체 경로는 각 모듈 정책
   - 판정: KEEP — 본 모듈 수집 경로에 대한 마스킹은 완결적이며, 모듈 외부 저장 경로는 해당 모듈 소관이라는 경계 설정이 합리적
46. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\COND_MODULES_종합명세.md`:533 — COND-034 핵심 기술 목록에 CRDT를 포함(마스터-슬레이브 읽기 복제 맥락)한 기술 후보 나열 선택
   - 선택지: CRDT 삭제 / 후보 기술로 유지(현행)
   - 판정: KEEP — 종합명세의 기술 후보 나열이며 상세정본(cond_034)이 구현 기술을 확정함(본문>요약 우선). 충돌 해소·미래 active-active 대비 후보로 무모순
47. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\01_cat-a-ai-ml\cond_013_time_travel_debug.md`:22-43,452 — 디버깅 권한 검증을 입력 스키마가 아닌 Blue Node PolicyGate(호출 패턴 L452)에 두는 게이트 중심 인가 아키텍처 선택
   - 선택지: 스키마에 requester/scope 필드 추가 / 게이트 일원화(현행)
   - 판정: KEEP — §B.7.1 5-Gate 정본 구조상 PolicyGate가 권한을 담당하므로 모듈 스키마 부재는 모순 아님. audit_reason 필드는 L3 보강 여지
48. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\01_cat-a-ai-ml\cond_025_emotion_pattern_learning.md`:201-204,427-430 — 동의/정책 검증을 사전 게이트(PolicyGate/ApprovalGate)+모듈 내 사후 PrivacyGuard 재검증의 2계층에 배치한 선택
   - 선택지: 수집 전 모듈 내 검증으로 이동 / 게이트 사전+모듈 사후(현행)
   - 판정: KEEP — 정본 게이트(§B.7.1)가 실행 전 승인·정책을 보장하고 모듈 내 검증은 심층방어. 수집 전 재배치는 L3 강화 선택지
49. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\01_cat-a-ai-ml\cond_085_crewai_role_engine.md`:618 — log_agent_thoughts 기본값 True(에이전트 사고 로그 기본 수집)의 관측성 우선 기본값 선택
   - 선택지: False 기본+옵트인 / True 기본(현행, 디버깅 가시성)
   - 판정: KEEP — 정본 금지 규정 없음. 멀티에이전트 디버깅 가시성 우선은 유효한 선택, 운영 프로파일에서 False 전환 권장 주석 여지
50. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\01_cat-a-ai-ml\cond_085_crewai_role_engine.md`:240,615 — allowed_tools 강제 지점을 resolve_tools 구현 내부에 위임(명시적 allowlist 검증 스텝 없음)한 책임 배치 선택
   - 선택지: E3에 ⊆ allowed_tools 명시 검증 추가 / resolve_tools 위임(현행)
   - 판정: KEEP — config allowed_tools가 존재하고 resolve_tools가 해석 지점이므로 구현 위임은 유효한 선택. L3에서 명시 검증+실패 코드 보강 권장
51. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\01_cat-a-ai-ml\cond_104_ambient_intelligence.md`:468-469 — enable_location_features=True / privacy_mode=False 기본값(기능성 우선, 프라이버시 모드 옵트인)의 기본값 선택
   - 선택지: privacy_mode=True 기본 / 현행 기능 우선 기본
   - 판정: KEEP — 호출 패턴의 PolicyGate 최소수집 조건이 사전 게이트로 작동해 정본 무모순. privacy_mode 기본 상향은 정책 결정 사항으로 보류
52. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\02_cat-b-knowledge\cond_021_notion_obsidian_import.md`:22 — Notion api_token을 요청 스키마로 직접 전달(서버측 토큰 비저장, 1회성 임포트 도구 특성)하는 자격증명 전달 방식 선택
   - 선택지: KMS/SecretRef 브로커 경유(cond_111 방식) / 요청 전달(현행)
   - 판정: KEEP — 1회성 임포트 도구에서 비저장 전달은 유효한 선택이며 정본 금지 없음. L3에서 SecretRef 전환·로그 마스킹 명시 권장
53. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\02_cat-b-knowledge\cond_021_notion_obsidian_import.md`:32 — vault_path 통제를 validate_vault_path+ApprovalGate 조합으로 두고 경로 allowlist/샌드박스는 두지 않은 선택
   - 선택지: allowlist/샌드박스 추가 / 검증함수+승인게이트(현행)
   - 판정: KEEP — 로컬 개인 vault 임포트 특성상 사용자 승인 게이트로 충분한 통제, 정본 무모순. allowlist는 L3 강화 선택지
54. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\02_cat-b-knowledge\cond_023_temporal_knowledge.md`:547 — healthy를 db_ok만으로 판정하고 cache_ok는 details로만 노출(캐시=비필수 구성요소)하는 health 정의 선택
   - 선택지: db AND cache / db만(현행, 캐시 다운=성능 저하일 뿐)
   - 판정: KEEP — 캐시 미가용은 기능 상실이 아니므로 가용성 우선 정의가 합리적, details 노출로 관측성도 유지
55. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\02_cat-b-knowledge\cond_024_predictive_knowledge_surfing.md`:611 — healthy=mem_ok AND vs_ok로 판정하고 semantic_cache는 비필수로 분리한 health 범위 선택
   - 선택지: 3종 AND / 핵심 2종(현행)
   - 판정: KEEP — cond_023과 동일한 캐시 비필수 원칙의 일관 적용, 정본 무모순
56. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\02_cat-b-knowledge\cond_108_zettelkasten_advanced.md`:703 — health를 핵심 저장소 3종(NoteStore/VectorStore/KG)으로 한정하고 보조 컴포넌트(embedding/cluster/link_store)는 제외한 범위 선택
   - 선택지: 6종 전수 / 핵심 3종(현행)
   - 판정: KEEP — 상태 보유 저장소만 health 게이트로 삼는 일관 원칙. embedding 등은 호출 시점 실패로 표면화되므로 합리적
57. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\03_cat-c-ops-infra\e-series\_index.md`:92-100 — 39개 e-series 모듈에 5종 표준 FailureCode(195개 프레임)만 등록하고 capability별 세부 코드는 L3로 이연한 오류 모델 단계화 선택
   - 선택지: 모듈별 세부 코드 즉시 정의 / 표준 5종+L3 세분화(현행)
   - 판정: KEEP — 'L3 보강 시 capability별 세부 코드 추가 예정'이 본문에 명시된 단계적 설계이며 LOCK-CD-06 4필드 전수 적용과 정합
58. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\03_cat-c-ops-infra\e-series\cond_035_e024_session_mgmt.md`:36-38 — L2 골격에서 payload: dict[str,Any] generic envelope를 쓰고 'L3에서 정밀 타입 교체'를 예고한 스키마 단계화 선택
   - 선택지: 즉시 typed union / generic envelope+L3 교체(현행)
   - 판정: KEEP — 본문에 교체 계획이 명시된 39모듈 공통 L2 전략으로 PLAN(Phase 단계화)과 정합. 모순 아님
59. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\05_cat-e-education\cond_091_personalized_learning_path.md`:456-459 — learner 동의/승인을 입력 스키마 필드가 아닌 Permission Level(P1: learner 명시 승인 시 활성)+게이트 계층에 두는 인가 아키텍처 선택
   - 선택지: 스키마에 consent_id/approval 토큰 추가 / Permission+게이트 일원화(현행)
   - 판정: KEEP — §B.6.1 Blue Node 패턴 정본상 Permission/게이트가 동의를 담당. GDPR/CCPA consent 명시로 정합, 스키마 중복은 불필요
60. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\06_cat-f-wellbeing\_index.md`:126 — LOCK-HW-03(24h TTL/90일) 프레임 아래 모듈별 보존기간을 §1.4에서 차등(30/90/180/365일 등) 문서화한 데이터 보존 정책 선택
   - 선택지: 전 모듈 동일 90일 / 모듈·데이터 유형별 차등+opt-in 연장(현행)
   - 판정: KEEP — 8/8 모듈이 §1.4에서 LOCK-HW-03을 인용하며 차등 사유를 문서화(유사 건 T6-644는 원검증에서 반박됨). LOCK 위반 확증 없음
61. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\06_cat-f-wellbeing\cond_095_sleep_improvement.md`:101,282 — sleep_data 스키마 하한(min_length=1)과 분석 가능 하한(<7 → INSUFFICIENT_DATA 런타임 실패코드)을 분리한 검증 계층화 선택
   - 선택지: 스키마 min_length=7 / 스키마 관대+런타임 실패코드(현행)
   - 판정: KEEP — 7일 미만 입력에 구조적 422가 아닌 도메인 실패코드를 주는 의도적 계층화이며 테스트 095-S5와 정합
62. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\04_cat-d-media\cond_016_multimedia_library.md`:440 — CAT-D 모듈군에서 retry_policy를 선언적 표준 필드로만 두고 모듈 내 재시도 로직을 두지 않은(프레임워크 소비) 선택
   - 선택지: 모듈 내 구현 / 선언+호출측 집행(현행)
   - 판정: KEEP — LOCK-CD-10 표준 5필드 계약으로 e-series와 동일 패턴. E3 미구현은 모순 아님
63. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\04_cat-d-media\cond_086_code_conversion.md`:299-301 — tree-sitter grammar·포매터(black/prettier 등) 외부 라이브러리 버전을 latest로 추적하는 의존성 핀 정책 선택
   - 선택지: 전부 버전 핀 고정 / 핵심(tree-sitter ≥0.21)만 핀+주변 latest(현행)
   - 판정: KEEP — 핵심 파서는 하한 핀, 포매터류는 latest 추적이라는 차등 정책으로 합리적. 재현성 요구 시 L3 lockfile 권장 한 줄
64. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\07_cat-g-integration\cond_110_etl_tool.md`:92,329 — idempotency_strategy에 append_only를 '멱등성 없음, 운영 책임'으로 명시 문서화하여 옵션으로 제공하는 전략 집합 선택
   - 선택지: append_only 제거 / 문서화된 옵션 제공(현행)
   - 판정: KEEP — §4.6이 비멱등성을 명시적으로 고지(opt-in 책임 이전)하므로 'Idempotent Load' 표방과 모순 아닌 옵션 설계
65. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\07_cat-g-integration\cond_111_zapier_make.md`:101-103 — OAuth 토큰을 요청 스키마에서 배제하고 KMS 토큰스토어+consent_flags로 관리(§1.4 보존정책·L402 로그 배제 명시)하는 자격증명 아키텍처 선택
   - 선택지: 요청에 토큰 포함 / 브로커 관리+스키마 배제(현행)
   - 판정: KEEP — 토큰의 요청/로그 노출을 차단하는 보안 우위 설계이며 OAuth 플로(§L305-333)와 refresh 실패코드가 일관 정의됨
66. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\07_cat-g-integration\cond_112_jira_linear.md`:504 — query 처리량 목표 ≥30 req/s를 JIRA 100 req/min(write) rate limit '고려' 전제로 설정한 SLA 값 선택
   - 선택지: 100/min에 맞춰 하향 / 캐시·배치 전제 30req/s(현행)
   - 판정: KEEP — query 축은 캐시/로컬 미러로 외부 호출과 N:1 분리 가능하며 표에 rate limit 고려가 명시됨. 정본 무모순
67. **[KEEP]** `docs\sot 2\2-2_COND-Modules-Detail\COND_MODULES_DETAIL_구조화_종합계획서.md`:667,675 — 156개 SLA 골격값을 모듈 특성별 차등(p99 10ms~30s, throughput 1~50,000)으로 부여하고 측정환경·부하모델은 Phase 2 P2-1 부하시험으로 이연한 단계화 선택
   - 선택지: 측정 방법론 즉시 명세 / 골격값+P2-1 실측 보강(현행)
   - 판정: KEEP — PLAN 자체가 'Phase 2 부하시험 데이터 기반 L3 보강 예정'을 명시한 의도적 단계화. SLA 값들은 검증 가능한 정본 위반 없는 설계 선택

> notes: 방법: 4개 입력 전수 검토(CLC 237건, TIGHT 196건=CLC 부분집합, GPT 312건, mf_in 객관 41확정+18미확정). 제외: (1) mf_in 객관결함과 동일/직계 계열(미정의 변수·도달불가 실패코드·dead config·예시/테스트 자기모순·LOCK 인용 왜곡·post-hoc 타임아웃 계열 등)은 객관측으로 분류, (2) CLC verify=refuted 21건 오탐, (3) GPT의 ZIP-범위 한정 오탐(CAT-A~G README placeholder 47건 — 디스크에 01_~08_ 정본 실존 확인, 2-2-COND-001/002/015, D04-024, G-021 등), (4) 단순 표기(T8-021, T8-342, T8-611 등). 모든 등재 항목은 D:\VAMOS\docs\sot 2\2-2_COND-Modules-Detail\ 디스크 실측(file:line)으로 확인했고, 정본 우선순위(RULE>PLAN>DESIGN LOCK>본문>스키마) 모순이 확인된 항목이 없어 전건 KEEP(CHANGE 0). 카운트 차이(87→67) 사유: (a) 원판정 87은 CLC/TIGHT/GPT 소스별 중복 finding을 별건 집계했을 가

### 3-6_Health-Wellness-EmotionAI (26건)

1. **[KEEP]** `docs\sot 2\3-6_Health-Wellness-EmotionAI\01_emotion-recognition\text_emotion_analysis.md`:666 — 저신뢰 폴백 트리거를 'softmax 결과 전체 <0.1'(준균등분포 감지)로 정의한 임계값 선택
   - 선택지: (a) 전체 <0.1 준균등 감지(현행) (b) top-1 확률 < 임계(예: 0.3) (c) 엔트로피 기반 임계
   - 판정: KEEP — 12-class 균등분포는 각 ~0.083으로 조건 도달 가능하며 최대 불확실 상태를 정확히 포착, LOCK/SOT 어디에도 폴백 트리거 규정 없음(정본 무모순)
2. **[KEEP]** `docs\sot 2\3-6_Health-Wellness-EmotionAI\02_adaptive-response\empathy_dialogue_engine.md`:460-466 — 반복 회피 전환을 ACKNOWLEDGE→REFLECT, SUPPORT→VALIDATE 2종으로만 한정하고 기타는 유지하는 전략 범위 선택
   - 선택지: (a) 2종 전환+기타 유지(현행, §4.2 L616 '과도한 전환 방지' 명문) (b) 전 전략 순환 전환 (c) 무작위 대체
   - 판정: KEEP — §4.2 L616에 '기타 → 유지 (과도한 전환 방지)' 의도가 명문화된 설계며 §9 L754 폴백 행도 존재, 정본 무모순(§9 행 문구를 실제 로직에 맞게 다듬는 것만 후속 권고)
3. **[KEEP]** `docs\sot 2\3-6_Health-Wellness-EmotionAI\03_health-data\health_dashboard.md`:59-60 — STEP7-P 원본 5축(수면/운동/식사/감정/체중)을 LOCK-HW-11 5축으로 재매핑하며 '식사'를 생산성균형 대체+영양 서브 지표로 둔 축 매핑 선택
   - 선택지: (a) LOCK-HW-11 5축 + 영양 서브 표시(현행) (b) 원본 5축 그대로 6+축 확장 (c) 식사/체중 축 제외
   - 판정: KEEP — DESIGN LOCK(LOCK-HW-11, AUTHORITY §3.1 L67 'SOT 원문 일치')이 5축 구조의 정본이고 매핑 근거가 L60에 주석으로 투명하게 명시됨
4. **[KEEP]** `docs\sot 2\3-6_Health-Wellness-EmotionAI\03_health-data\activity_exercise.md`:279-301 — HealthDataSyncAdapter ABC를 V1에서는 인터페이스 정의만 두고 OAuth 인증/재시도/rate-limit을 V2 실연동으로 미룬 범위 선택
   - 선택지: (a) V1 인터페이스+수동 입력, V2 실연동(현행) (b) V1부터 인증·재시도 계약 포함 (c) V1에서 어댑터 자체 제외
   - 판정: KEEP — L282-283에 'V1에서는 동기화 인터페이스 정의 + 수동 입력 지원. V2에서 HealthKit/Google Fit 실 연동 (P-011-a)' 단계 설계가 명문화돼 정본 무모순; V2 진입 시 인증·백오프 계약 추가만 권고
5. **[🔧CHANGE]** `docs\sot 2\3-6_Health-Wellness-EmotionAI\03_health-data\medical_records.md`:234 — 감정 로그 기본 보존 기간 180일(LOCK-HW-03, 계획서 §A.1 독자 정의) 설계값 선택
   - 선택지: (a) 기본 180일 유지+CL-002 Phase3 확정 대기(현행) (b) 90일로 축소(상세명세 §4 집계 기준 정합) (c) 사용자 설정 무기본값
   - 판정: 180일 값 자체는 KEEP(CL-002 DEFERRED_TO_PHASE3로 정본 출처 확정 이월 중)이나, 파일 내 'CL-002 OPEN' 표기는 정본 상태 레지스트리 CONFLICT_LOG v2.2(2026-04-20 DEFERRED_TO_PHASE3 확정)와 모순 → 상태 표기 교정
6. **[KEEP]** `docs\sot 2\3-6_Health-Wellness-EmotionAI\03_health-data\nutrition_management.md`:284 — 미등록 음료 종류의 카페인 함량을 50mg으로 추정하는 기본값 선택
   - 선택지: (a) 50mg 기본값(현행) (b) 0mg+미상 플래그 (c) 입력 거부+사용자 확인
   - 판정: KEEP — 50mg은 일반 음료 중앙값 수준의 합리적 추정치이고 400mg 한도 자체는 비-LOCK 가이드 값(정본 무모순); 미상 입력 시 경고 로그 추가만 개선 권고
7. **[KEEP]** `docs\sot 2\3-6_Health-Wellness-EmotionAI\03_health-data\work_health.md`:154-158 — 스트레칭/눈휴식 알림을 좌식 시간의 모듈로 일치(% 50 == 0)로 발화시키는 에지 트리거 설계 선택
   - 선택지: (a) 분 단위 체크 전제 모듈로 트리거(현행) (b) 임계값 래칭+발화 기록 (c) 스케줄러 기반 절대시각 트리거
   - 판정: KEEP — 분 단위 정기 호출을 전제로 한 단순 설계로 정본(SOT 50분 간격 권고) 무모순; 틱 누락 내성을 위한 래칭 전환은 V2 개선 권고
8. **[KEEP]** `docs\sot 2\3-6_Health-Wellness-EmotionAI\04_stress-management\burnout_prevention.md`:166-171 — 번아웃 4등급을 OR 조건 밴딩(WLS OR MBI OR 키워드)으로 정의하고 등급 간 평가 우선순위를 관례(상위 우선)에 맡긴 판정 체계 선택
   - 선택지: (a) OR 밴딩+상위 등급 우선 암묵(현행) (b) AND 강화 조건 (c) 단일 합성 점수 단조 밴딩
   - 판정: KEEP — OR 밴딩은 안전 우선(위기 과소판정 방지) 설계이고 Critical 행이 §4.5 정본 표와 일치; '복수 행 일치 시 상위 등급 우선' 1줄 명시만 권고
9. **[KEEP]** `docs\sot 2\3-6_Health-Wellness-EmotionAI\04_stress-management\habit_formation.md`:167-175 — completion_rate 분모를 캘린더 일수가 아닌 체크인 제출 횟수(total_days)로 둔 지표 의미론 선택
   - 선택지: (a) 체크인 기준 분모(현행, 미완료 체크인도 제출 전제) (b) 캘린더 일수 기준 (c) 양 지표 병행
   - 판정: KEEP — update_streak가 완료/미완료 체크인을 모두 수신하는 일일 체크인 전제 설계로 내적 일관(else 분기 존재), '완료율 90%(30일)' 정본 위반 아님; 무제출일 자동 미완료 처리 권고
10. **[KEEP]** `docs\sot 2\3-6_Health-Wellness-EmotionAI\04_stress-management\stress_detection.md`:224 — 추세 점수 스케일 trend_score = 50 + slope×10 (기울기 ±5 → 0-100 매핑) 계수 선택
   - 선택지: (a) 계수 10(현행, 시간당 1회 기록 캐던스 전제 L228) (b) 샘플링 주기 정규화 후 매핑 (c) 백분위 기반 매핑
   - 판정: KEEP — L228 'N = 최대 ~168, 시간당 1회 기준'의 시간당 기록 전제에서 계수 10은 포화되지 않는 합리적 스케일(정본 무모순); 일 단위 데이터 혼용 대비 주기 정규화 권고
11. **[KEEP]** `docs\sot 2\3-6_Health-Wellness-EmotionAI\05_emotion-journal\emotion_journal_trend.md`:266-268 — 강도≥9 실시간 위기 점검 대상 감정을 {슬픔, 불안, 분노} 3종으로 한정한 위기 감정 집합 선택
   - 선택지: (a) 부정 핵심 3종(현행) (b) DISGUST 포함 4종(§5.2 부정 집합 정합) (c) 전 감정 강도 기반
   - 판정: KEEP — R-09-2 정본의 주 경로는 키워드 기반 crisis_protocol이고 본 감정-강도 점검은 추가 안전망이므로 대상 집합은 설계 재량(정본 무모순); §5.2 부정 집합과의 일관성 위해 혐오 포함 검토 권고
12. **[KEEP]** `docs\sot 2\3-6_Health-Wellness-EmotionAI\05_emotion-journal\emotion_journal_trend.md`:403-404 — 트렌드 분석에서 30일 분량을 decrypt=True 일괄 복호화하며 별도 재인증 게이트를 두지 않는 로컬 신뢰 모델 선택
   - 선택지: (a) 서비스 계층 신뢰+일괄 복호화(현행) (b) 분석 호출별 재인증/세션 토큰 (c) 암호화 상태 집계 후 최소 복호화
   - 판정: KEEP — PRIVATE(LOCK-HW-02)는 외부 전송 금지 규정이며 로컬 단일 사용자 앱 내 복호화 경로는 미규정(정본 무모순); analyze() 호출 감사 로그 추가 권고
13. **[KEEP]** `docs\sot 2\3-6_Health-Wellness-EmotionAI\05_emotion-journal\wellness_score.md`:191-198 — 부분 데이터 차원을 weighted_sum/total_weight×20으로 비례 보정(만점 환산)하는 정규화 전략 선택
   - 선택지: (a) 비례 보정+completeness 표기(현행) (b) 결측 서브컴포넌트 0점 처리 (c) completeness 미달 차원 N/A 처리
   - 판정: KEEP — completeness 필드(L197)로 데이터 불완전성이 투명하게 노출되는 설계며 LOCK-HW-11은 5축 0-20 구조만 규정(정본 무모순); 표시 계층에서 completeness 병기 권고
14. **[KEEP]** `docs\sot 2\3-6_Health-Wellness-EmotionAI\05_emotion-journal\wellness_investment_link.md`:156 — '좋은 컨디션' 시나리오 트리거를 VWS total ≥75 + 긍정감정 + 강도≥6으로 둔 임계값 선택
   - 선택지: (a) 75 컷오프(현행, GOOD 상위 구간) (b) 80(EXCELLENT 정합) (c) 70(GOOD 중간)
   - 판정: KEEP — wellness_score §6 등급표는 표시용 등급이고 시나리오 트리거 임계값은 독립 설계 재량(정본 무모순); 75 선택 근거 1줄 주석 권고
15. **[KEEP]** `docs\sot 2\3-6_Health-Wellness-EmotionAI\06_ethics-privacy\crisis_protocol.md`:644-657 — 오탐 피드백 학습을 분기별 패턴 임계값 조정 + Level 3 직접 표현 제외로 운영하는 FP 거버넌스 설계 선택
   - 선택지: (a) 분기별 조정+Level3 제외(현행) (b) 위원회 승인 게이트 추가 (c) 자동 학습 전면 금지
   - 판정: KEEP — §8.3 L657 'Level 3 직접적 표현은 임계값 조정 대상에서 제외 (안전 우선)' 안전장치가 명문이고 §9.2 #3(키워드 삭제 불가)이 LOCK-HW-05를 보호(정본 무모순); 분기 조정에 휴먼 리뷰 기록 의무 추가 권고
16. **[KEEP]** `docs\sot 2\3-6_Health-Wellness-EmotionAI\06_ethics-privacy\crisis_protocol.md`:355-356 — 3인칭 주어 표현에 위험도 -0.2 보정을 적용하는 오탐 방지 보정값 선택
   - 선택지: (a) -0.2(현행) (b) -0.1 완화 (c) 보정 없이 LLM 판정 위임
   - 판정: KEEP — MEDIUM 기준(0.4)은 LLM confidence ≥0.667이면 충족돼 T7(친구 걱정→MEDIUM) 달성 가능하고, 보정값은 §8.2 오탐 방지 전략 표의 명문 설계(정본 무모순)
17. **[KEEP]** `docs\sot 2\3-6_Health-Wellness-EmotionAI\HEALTH_WELLNESS_EMOTIONAI_구조화_종합계획서.md`:209, 317-320 — 감정 데이터 PRIVATE(원시 로컬전용)을 유지하면서 파생 요약(카테고리+강도+arousal/valence)만 opt-in 공유하는 프라이버시 경계 설계 선택
   - 선택지: (a) 원시 로컬전용+파생 opt-in 공유(현행) (b) 전면 공유 금지 (c) 원시 포함 동의 기반 공유
   - 판정: KEEP — L319-320에 '7분류+강도+arousal/valence만 허용, 원시 텍스트/음성 절대 금지'가 R-09-6/§9.2 #5와 일관 문서화된 carve-out이며 LOCK-HW-02(원시 로컬전용)와 양립(정본 무모순)
18. **[KEEP]** `docs\sot 2\3-6_Health-Wellness-EmotionAI\HEALTH_WELLNESS_EMOTIONAI_구조화_종합계획서.md`:1831 — V3 KPI 게이트 값(멀티모달 감정인식 ≥90%, 위기감지 Recall ≥99%, 웰빙 개선율 ≥25%, 만족도 ≥4.5/5) 선택
   - 선택지: (a) 강화 목표치(현행) (b) LOCK-HW-10 floor(80%/10%) 그대로 (c) 단계별 점증 게이트
   - 판정: KEEP — DESIGN LOCK(LOCK-HW-10)은 하한(80%/10%)만 고정하며 V3 게이트는 이를 초과하는 강화 목표로 정본 무모순; 측정 프로토콜은 VBS-17 §4와 연동 유지
19. **[KEEP]** `docs\sot 2\3-6_Health-Wellness-EmotionAI\HEALTH_WELLNESS_EMOTIONAI_구조화_종합계획서.md`:3062-3063 — 동일 세션 오탐 피드백 2회 이상 시 위기 감지 임계값 +0.2 상향(Level 3 제외)하는 과개입 방지 정책 선택
   - 선택지: (a) +0.2 상향+Level3 제외(현행) (b) +0.1 보수 상향 (c) 상향 없이 확인 질문만 강화
   - 판정: KEEP — L3063 'Level 3 직접적 표현은 임계값 조정 대상에서 제외 (안전 우선)' 예외로 인명 안전 경로(R-09-2)가 보존되는 trade-off 설계(정본 무모순); MEDIUM 하향분류 모니터링 지표 추가 권고
20. **[KEEP]** `docs\sot 2\3-6_Health-Wellness-EmotionAI\HEALTH_WELLNESS_EMOTIONAI_구조화_종합계획서.md`:2709 — 키 파생을 PBKDF2-HMAC-SHA256 최소 100,000 iterations 하한으로 규정한 보안 파라미터 선택
   - 선택지: (a) 최소 100k 하한(현행, 운영값 600k는 별도) (b) 하한 600k 상향(NIST 2023) (c) Argon2id 전환
   - 판정: KEEP — '최소' 하한 규정으로 health_data_privacy의 600k 운영값과 양립(정본 무모순, LOCK-HW-06은 AES-256-GCM만 고정); NIST SP 800-132 개정 반영해 하한 600k 상향을 Phase3 RFC 검토 권고
21. **[KEEP]** `docs\sot 2\3-6_Health-Wellness-EmotionAI\06_ethics-privacy\crisis_protocol.md`:606 — 위기 세션 기록(HIGHEST, 메타데이터만) 접근권한을 '시스템 관리자만 (사용자 요청 시 본인 열람 가능)'으로 둔 접근 정책 선택
   - 선택지: (a) 관리자 운영 접근+본인 열람(현행) (b) 사용자 본인만(ethics_framework §HIGHEST 정합) (c) break-glass 조건부 관리자 접근
   - 판정: KEEP — LOCK-HW-02는 외부 전송 금지만 규정하고 내부 접근 역할은 미규정이며, 기록이 대화 원문 제외 메타데이터(L604)라 위기 운영상 합리적 설계; break-glass 사유·감사 로그·사용자 통지 명문화 권고
22. **[KEEP]** `docs\sot 2\3-6_Health-Wellness-EmotionAI\03_health-data\medical_records.md`:238-240 — 의료 기록 삭제를 soft-delete 30일 유예 후 overwrite-then-unlink 완전 삭제로 운영하는 삭제 전략 선택
   - 선택지: (a) 30일 유예+완전 삭제(현행) (b) P-018 문자적 즉시 완전 삭제 (c) 즉시 삭제 옵션+기본 유예 병행
   - 판정: KEEP — P-018 '특별 보호'(암호화/AI학습제외/완전삭제)는 CL-005 RESOLVED에서 보존 정책과 보완 관계로 판정됐고 L239-240이 P-018 L343-344를 직접 인용하며 충족(AI 학습 제외 포함); 사용자 명시 요청 시 '즉시 완전 삭제' 옵션 병행 제공 권고
23. **[KEEP]** `docs\sot 2\3-6_Health-Wellness-EmotionAI\05_emotion-journal\investment_emotion_guard.md`:415-439 — AI Investing→Health 내부 cross-domain API(POST /api/health/investment-guard/evaluate)에 인증 토큰/동의 증명 필드를 두지 않는 로컬 신뢰 모델 선택
   - 선택지: (a) 로컬 단일 프로세스 신뢰(현행) (b) opt-in scope 토큰+consent version 필드 추가 (c) 게이트웨이 계층 위임
   - 판정: KEEP — V1 로컬 단일 사용자 앱 내부 IPC로 외부 노출 없어 LOCK-HW-02/R-09-3(외부 전송 금지) 무모순; V2 프로세스 분리/외부화 시 OptInConsent 토큰(3-5 선례) 스키마 추가 권고
24. **[KEEP]** `docs\sot 2\3-6_Health-Wellness-EmotionAI\05_emotion-journal\benchmark_vbs17.md`:14-17 — VBS-17을 SOT 8 core + 9 파생 = 17 지표 interim 구조로 해석한 벤치마크 체계 설계 선택
   - 선택지: (a) 8 core+9 파생 interim(현행, CL-007 DEFERRED) (b) SOT 8 항목만 (c) 17 항목 전부 동급 LOCK
   - 판정: KEEP — CL-007이 '자동 RESOLVE 금지+Phase 3 RFC 최종 확정'으로 정본 절차에 등재돼 있고 L14가 LOCK-HW-10 임계값(≥80%/≥10%)을 최상위 게이트로 고정(정본 무모순); 8 core의 SOT verbatim 지위 유지 필수
25. **[KEEP]** `docs\sot 2\3-6_Health-Wellness-EmotionAI\01_emotion-recognition\emotion_pattern_learning.md`:143-145, 170 — 패턴 학습 하이퍼파라미터(cold_start_min_samples=50, bayesian_prior_strength=5.0, 90일 반감기, 1.5σ 또는 top-1 shift 트리거) 값 선택
   - 선택지: (a) 현행 값 세트 (b) 보수화(σ 2.0, cold-start 100) (c) 사용자별 적응 캘리브레이션
   - 판정: KEEP — 전형적 튜너블 설계값으로 LOCK-HW-12 clamp(L167)와 LOCK-HW-06 암호화(L153) 등 정본 제약은 모두 준수(무모순); Phase 3 베이스라인 수집 시 FP/FN 기준 캘리브레이션 근거 문서화 권고
26. **[🔧CHANGE]** `docs\sot 2\3-6_Health-Wellness-EmotionAI\05_emotion-journal\education_emotion_integration_report.md`:41 (및 43) — Education 공유 범위(동의 UI 명시 스코프)에 세부5(subcategory)를 포함시킨 cross-domain 공유 스코프 선택
   - 선택지: (a) 7분류+세부5+강도+arousal/valence(현행 보고서) (b) 7분류+강도+arousal/valence만(AUTHORITY/계획서 정본) (c) AUTHORITY에 Decision 추가 후 세부5 허용
   - 판정: CHANGE — 정본 우선순위상 계획서 결정(L319 '감정 카테고리(7분류) + 강도(1-10) + arousal/valence만 허용')과 AUTHORITY_CHAIN 공유 규약(L145 동일 문구)이 보고서 본문보다 상위이며 '만 허용'과 세부5 포함이 직접 모순; L43 row6의 subcategory 표기도 동일 기준으로 후속 정합 필요

> notes: 재도출 결과 26건 (앵커 25 대비 +1, 강제 짜맞춤 금지 원칙 적용). 전수 분류 모집단: clc 77건 + tight 51건(전부 clc 부분집합, 신규 0) + GPT 19건. 제외 내역 — (1) mf_in 객관결함 확정 42건과 동일/중복: clc 37건(T8-002/007/013/016/025/026/028/030/033/056/077/078/086/103/109/110/111/124/129/130/131/133/142/155/164/180/182/183/213/237/247/249/254/258/264/346/347, T5-078, T6-180 포함) + GPT 8건(HWE-001/002/003/004/005/007/008/011/016) + 파생 중복 T8-039(mf i=11과 동일 retry 루프), T6-255(mf i=30 동일 루트 클러스터). T8-001은 mf_in 'unconfirmed' 객관 트랙에 귀속돼 주관 제외. (2) 디스크 실측 반박 오탐: T6-136(AUTHORITY_CHAIN §4 L98-100에 LOCK-HW-05 §B 3개소 인용 실존·일치), T8-278(위기 키워드 사전 §B.1 L2853 실존, '기준

### 3-4_Workflow-RPA (26건)

1. **[KEEP]** `docs\sot 2\3-4_Workflow-RPA\01_dag-engine\dag_architecture.md`:535-571 (§4.12) — CodeNode 스펙 수준에서 네트워크 egress 차단·출력 크기 상한 등 추가 보안통제를 어디까지 명시할지의 깊이 선택
   - 선택지: (a) 현행 — sandbox:true 강제+timeout/memory+allowed_imports deny-all(L549 명시), 세부는 샌드박스 구현 위임 / (b) CodeNode 전용 SandboxPolicy(network deny, fs write-temp-only, 출력 상한) 스펙 명시
   - 판정: KEEP — LOCK-WF-10·R-07-4(샌드박스 필수·파일시스템 제한)는 충족되고 deny-all import 기본까지 L549에 명시됨(mf i=28 교정 반영 확인); egress/출력 상한의 명세 위치는 설계 재량, 보강 시 LOCK-WF-10 하위 정책으로 추가 권장
2. **[KEEP]** `docs\sot 2\3-4_Workflow-RPA\01_dag-engine\advanced_dag.md`:67, 78, 96 — 재귀 깊이 상한 값 5와 경계 의미론(max_depth 리터럴 5, depth≤5 허용 → 총 실행 프레임 6) 선택
   - 선택지: (a) 현행 ≤5 허용/>5 거부 / (b) <5 (총 5프레임) / (c) max_depth 가변 필드+상한 5
   - 판정: KEEP — E3.2 가드표·E3.3 검증코드·E5 폴백 모두 '≤5 허용, >5 거부'로 문서 내 일관하며, 경계 포함 여부를 규정하는 LOCK/정본 없음 → 값·경계는 설계 재량
3. **[KEEP]** `docs\sot 2\3-4_Workflow-RPA\01_dag-engine\error_handling.md`:254 — AI 에러 분석기 모델로 비버전 alias "claude-3-sonnet" 지정(모델 선택)
   - 선택지: (a) 현행 비버전 alias / (b) 버전드 현행 모델 alias / (c) 종합계획서 D.3 A-1 MultiBrain failover 체인 경유
   - 판정: KEEP — 내부 에러 분석용 모델을 강제하는 정본 없음(정본 모순 없음); 다만 은퇴 alias 리스크 해소를 위해 운영 시 D.3 MultiBrain 체인(Part2 L2118-2121) 경유를 권장
4. **[KEEP]** `docs\sot 2\3-4_Workflow-RPA\01_dag-engine\execution_engine.md`:255-263 — cancel()의 협조적 취소 의미론 — docstring '현재 노드 완료 후 중단' 명시, 실행 중 노드 즉시 강제 중단하지 않음
   - 선택지: (a) 협조적 취소(현행) / (b) 선제적 asyncio task cancel+보상 롤백
   - 판정: KEEP — LOCK-WF-09는 CANCELLED 전이만 규정하고 중단 시점은 미규정; 협조적 취소는 노드 출력 일관성에 유리한 통상 설계이며 docstring으로 의도가 명시됨
5. **[🔧CHANGE]** `docs\sot 2\3-4_Workflow-RPA\02_nl-to-workflow\intent_parsing.md`:483 — 다의 키워드 '확인'의 노드 타입 매핑 선택(ConditionNode vs HumanApprovalNode)
   - 선택지: (a) 현행 '확인'→ConditionNode / (b) 정본 §5.2 정렬 '확인'→HumanApprovalNode / (c) 컨텍스트 기반 분기
   - 판정: CHANGE — 본 파일 L472가 nl_to_dag_conversion.md §5.2를 '정본 참조'로 자기 선언했고 §5.2 L226은 '승인, 확인, 검토, 결재'→HumanApprovalNode(본문 정본 우선) → 정본 정렬 필요; '각각'/'계산'은 §5.2도 복수 매핑이라 단일화 재량 인정
6. **[KEEP]** `docs\sot 2\3-4_Workflow-RPA\02_nl-to-workflow\nl_to_dag_conversion.md`:238-242 (vs 703-709) — generate_dag() Step1에서 match_template 방어적 재실행(엔트리포인트가 이미 매칭 후 miss 시에만 호출 → LLM 경로 이중 탐색)
   - 선택지: (a) 방어적 재확인 유지(generate_dag 단독 호출 안전) / (b) 엔트리포인트 단일 매칭으로 Step1 제거
   - 판정: KEEP — 함수 단독 호출 안전성을 위한 방어적 중복으로 정본 모순 없음; 템플릿 매칭은 fast-path라 성능 영향 미미
7. **[KEEP]** `docs\sot 2\3-4_Workflow-RPA\02_nl-to-workflow\visual_editor.md`:140 — 프런트엔드 순환 검증을 dag_architecture §3.3 DAGValidator.detectCycle '재사용'으로 두는 구현 채널 선택(TS 포팅 vs 백엔드 API 호출)
   - 선택지: (a) 동일 알고리즘 TS 재구현 / (b) 백엔드 검증 API 호출 / (c) 현행 문구 유지
   - 판정: KEEP — 검증 로직의 단일 정본(dag_architecture §3.3) 참조는 R4(정본 소유자 1곳) 정합이며 구현 채널은 설계 재량; '(Pydantic 모델 import)' 문구만 'TS 포팅(알고리즘 동일)' 또는 'API 위임'으로 명확화 권장
8. **[KEEP]** `docs\sot 2\3-4_Workflow-RPA\03_trigger-system\ambient_trigger.md`:98, 102 — 앰비언트 감지 poll_interval_sec=60 기본값 선택(절 제목에 LOCK-WF-05를 맥락 근거로 인용)
   - 선택지: (a) 60s 기본+배터리 보호(현행, min_battery 15% 가드) / (b) 30s 또는 적응형 주기
   - 판정: KEEP — 폴링 주기를 규정하는 정본 없음, 60s+배터리 가드는 합리적 설계; 제목의 LOCK-WF-05 인용은 '발화 후 실행이 동시 10 내'라는 맥락 註로 한정 표기 권장(폴링 자체는 실행 슬롯 아님)
9. **[KEEP]** `docs\sot 2\3-4_Workflow-RPA\03_trigger-system\ambient_trigger.md`:89 — foreground_app_id 해시화를 '권장'(필수 아님)으로 두는 프라이버시 강도 선택
   - 선택지: (a) 해시 권장(현행) / (b) 해시 필수(스키마 강제)
   - 판정: KEEP — LOCK-WF-10은 샌드박스/파일시스템/자격증명 암호화만 규정하고 앱 식별자 해시 의무 정본 없음 + §3.1 옵트인 게이트 별도 존재; 강화는 정책 선택지로 보강 후보
10. **[KEEP]** `docs\sot 2\3-4_Workflow-RPA\04_template-library\meeting_automation.md`:135 — STTConfig.chunk_duration_sec를 TS 리터럴 30으로 고정(인스턴스별 오버라이드 불가 스펙 상수화)
   - 선택지: (a) 리터럴 30 고정(현행) / (b) number 타입+기본 30
   - 판정: KEEP — 청크 길이를 규정하는 정본 없음; 30s 고정은 Whisper 청크 관행과 부합하는 스펙 상수 선택이며, 가변 필요가 확인되면 number로 완화 가능
11. **[KEEP]** `docs\sot 2\3-4_Workflow-RPA\04_template-library\report_generation.md`:126 — CodeNode 스니펫의 plotly 정적 export(kaleido) 의존성을 스펙 문서에 선언할지의 문서화 범위 선택
   - 선택지: (a) 스펙 미선언(현행 — 의존성은 구현 매니페스트 소관) / (b) 템플릿 요구 패키지 절 추가
   - 판정: KEEP — 템플릿 스펙의 의존성 선언 깊이는 문서 설계 재량(정본 무관); 구현 단계 requirements에 kaleido 명시 권장
12. **[KEEP]** `docs\sot 2\3-4_Workflow-RPA\05_browser-rpa\browser_security.md`:342 (vs 85) — 메모리 누수 강제종료 임계 500MB를 하드캡 512MB(기본)보다 낮게 두는 조기 차단 임계 선택
   - 선택지: (a) '지속 증가+500MB 초과' 조기 kill(현행) / (b) 임계=캡 512MB 통일
   - 판정: KEEP — 누수 규칙은 '지속 증가' 조건과 결합된 leak detector로, OOM 도달 전 조기 차단하는 심층방어 설계이며 두 한도를 규정하는 정본 없음 — 모순 아닌 의도적 마진
13. **[KEEP]** `docs\sot 2\3-4_Workflow-RPA\04_template-library\sns_content_automation.md`:257-263 — 13번째 카테고리 sns_publishing을 카탈로그 본문 수정 없이 '선언만'(append-only, 본문 반영 Phase 3 이월)으로 등재하는 패턴 선택
   - 선택지: (a) declare-only append(현행, V1 수정 금지 원칙) / (b) template_catalog 본문 직접 추가 / (c) 기존 content 카테고리(rows 11-12) 확장으로 흡수
   - 판정: KEEP — V1 수정 금지 하 append-only 확장 패턴은 설계 재량이고 파일이 이월·선언만임을 자체 명시(L263); 단 cross-ref의 '§5'는 카테고리 본문이 실제 §3(template_catalog.md L101)이므로 포인터 교정 권장(표기)
14. **[KEEP]** `docs\sot 2\3-4_Workflow-RPA\05_browser-rpa\form_autofill.md`:290 — 입력 로그 마스킹 기법(절단/해시/고정 토큰) 미특정 — '입력값은 마스킹 처리'만 규정하는 명세 깊이 선택
   - 선택지: (a) 기법 구현 위임(현행) / (b) 고정 토큰/해시 등 기법 명세+LLM 매칭 컨텍스트 최소화 명시
   - 판정: KEEP — '마스킹 필수' 정책은 규정되어 LOCK-WF-10 취지 충족, 기법 선택은 구현 재량; LLM 전달 프로필 값 최소화 명시는 보강 후보
15. **[KEEP]** `docs\sot 2\3-4_Workflow-RPA\05_browser-rpa\nocode_api.md`:262-278 — 문서 URL 자동 파싱의 SSRF/허용목록 통제를 파일 내 재기술하지 않고 도메인 공통 NetworkPolicy 상속에 위임하는 선택
   - 선택지: (a) browser_security §10 매핑 상속(현행 — L355에 nocode_api '네트워크 정책, TLS 필수' 명시, block_internal_ips 기본 true) / (b) §8에 URL 검증 절 재기술
   - 판정: KEEP — R4(겹치는 개념은 정본 소유자 1곳+참조) 원칙상 보안 정책 단일 정본 상속이 정합이며 needs_review 사용자 게이트도 존재; §8에 '> 참조: browser_security §7/§10' 링크 추가 권장
16. **[KEEP]** `docs\sot 2\3-4_Workflow-RPA\WORKFLOW_RPA_구조화_종합계획서.md`:216 — LOCK-WF-08 데스크톱 액션 12종 집합의 큐레이션 — 소스 §7 대비 type_text·ocr_extract·image_match·wait_element·scroll·drag_drop 추가/개명(wait_image→wait_element), focus_window·file_dialog 제외(상세명세 L515/L524 실재 확인)
   - 선택지: (a) 현행 LOCK 12종 유지(이후 전 파일이 이 집합 준수) / (b) §7 원형 복원
   - 판정: KEEP — LOCK 제정 시점의 집합 재구성은 설계 권한이며 DESIGN LOCK > 본문으로 이후 정본은 LOCK; '정본 출처' 칸을 '기존 명세 §7 발췌+개편'으로 명시해 verbatim 오해만 제거 권장
17. **[KEEP]** `docs\sot 2\3-4_Workflow-RPA\WORKFLOW_RPA_구조화_종합계획서.md`:215 — LOCK-WF-07 브라우저 액션 10종 큐레이션 — 소스 §6 대비 hover 추가, fill_form·download 제외(상세명세 L456-457 실재 확인)
   - 선택지: (a) 현행 LOCK 10종 / (b) §6 원형(fill_form/download 포함, hover 없음)
   - 판정: KEEP — T6-231과 동일 논리로 LOCK 큐레이션은 설계 권한; fill_form/download는 LOCK-WF-01 '최소 집합' 선례 해석상 확장 액션으로 본문 존치 가능, 출처 표기만 '발췌+개편' 명시 권장
18. **[🔧CHANGE]** `docs\sot 2\3-4_Workflow-RPA\WORKFLOW_RPA_상세명세.md`:447-458 — 본문 BrowserAction enum 구성 선택 — 11종(fill_form/download 포함, hover 부재) vs LOCK-WF-07 10종
   - 선택지: (a) 현행 11종 유지 / (b) LOCK 10종으로 교체 / (c) LOCK 10종 전부 포함+확장 2종 병기
   - 판정: CHANGE — 정본 우선순위 DESIGN LOCK > 본문: LOCK-WF-07이 명시한 hover가 enum에 없음(grep 0건 실측)은 정본 모순이므로 HOVER 추가; fill_form/download는 최소집합 해석상 확장으로 존치(제거 불요)
19. **[KEEP]** `docs\sot 2\3-4_Workflow-RPA\WORKFLOW_RPA_구조화_종합계획서.md`:207-218 — 워크플로우 전체 실행 타임아웃 LOCK을 정의하지 않는 선택(노드별 타임아웃+LOCK-WF-02 50노드+모듈별 상한으로 간접 바운드)
   - 선택지: (a) 전역 타임아웃 없음(현행) / (b) LOCK/R-규칙 신설(예: 총 실행 ≤30분)
   - 판정: KEEP — 전역 상한 도입 여부는 정책 선택; HumanApproval 대기(10분)·DelayNode until(≤24h) 등 장주기 노드가 정본에 존재해 일률 상한은 부작용 — 필요 시 트리거/카테고리별 R-규칙로 추가 권장
20. **[KEEP]** `docs\sot 2\3-4_Workflow-RPA\WORKFLOW_RPA_구조화_종합계획서.md`:248, 218 — R-07-4/LOCK-WF-10 샌드박스의 기술 스택(gVisor·Docker·seccomp 등)과 경계 정의를 명시하지 않고 구현 단계에 위임하는 선택
   - 선택지: (a) 기술 중립 정책 선언(현행) / (b) 샌드박스 기술·금지 syscall 목록 명시
   - 판정: KEEP — R6(sot2=What/How, When=PART2) 체계에서 정책 선언+기술 선택의 구현 위임은 통상 설계이며 기술을 규정하는 상위 정본 없음; Part2 구현 시 선택 기록 권장
21. **[KEEP]** `docs\sot 2\3-4_Workflow-RPA\WORKFLOW_RPA_구조화_종합계획서.md`:251 — R-07-7(NL→DAG 변환 시 사용자 확인 필수)의 통제 범위를 변환 시점으로 한정하고 승인 후 변경(TOCTOU) 재승인 규칙은 두지 않는 선택
   - 선택지: (a) 현행 범위(변환 시점 확인) / (b) 승인본 해시 고정+변경 시 재승인 규칙 추가
   - 판정: KEEP — 통제 범위 확장은 정책 선택으로 정본 모순 없음; workflow_versioning이 버전 이력을 보존하므로 재승인 게이트는 보강 후보로 권고
22. **[KEEP]** `docs\sot 2\3-4_Workflow-RPA\WORKFLOW_RPA_구조화_종합계획서.md`:2070 — Webhook HMAC-SHA256 인증에 timestamp/nonce 재전송(replay) 방지를 포함하지 않는 보안 강도 선택(rate limit 100/min만 — webhook_trigger.md에도 부재 실측)
   - 선택지: (a) HMAC+rate limit(현행) / (b) timestamp 허용창+nonce 캐시 추가
   - 판정: KEEP — 재전송 방지를 의무화하는 정본 없음, 강도 수준은 설계 선택; 산업 관행상 서명 페이로드에 timestamp 검증 추가를 권장(보강 후보)
23. **[KEEP]** `docs\sot 2\3-4_Workflow-RPA\WORKFLOW_RPA_상세명세.md`:92 — R-07-4/LOCK-WF-10 '샌드박스 필수' 문언의 적용 범위 해석 — 브라우저/데스크톱 RPA 문언에 CodeNode(RPA 프리셋 포함)·EXECUTE_JS를 포함시킬지
   - 선택지: (a) 현행 — CodeNode는 dag_architecture §4.12 sandbox:true 강제로 별도 충족(L546) / (b) R-07-4 문언을 'RPA+사용자 코드 실행'으로 확장
   - 판정: KEEP — CodeNode 샌드박스는 §4.12에서 이미 강제되어 실질 공백 없음(L92도 RPA를 CodeNode 프리셋으로 명시, mf i=6 교정 반영 상태); 감사 범위 문언 명확화는 보강 후보
24. **[KEEP]** `docs\sot 2\3-4_Workflow-RPA\WORKFLOW_RPA_상세명세.md`:547 — AI 비전 요소 탐색 3단계 fallback(템플릿 매칭→OCR→AI 비전)의 최종 단계 모델로 GPT-4o 지정
   - 선택지: (a) GPT-4o(현행) / (b) 추상 프로바이더 인터페이스+failover 체인
   - 판정: KEEP — 종합계획서 D.3/Part2 L2118-2121의 A-1 MultiBrain 체인이 Primary GPT-4o→Claude→Ollama를 정의해 현행 선택과 정합; 직접 교체 불요, 해당 체인 참조 주석 권장
25. **[KEEP]** `docs\sot 2\3-4_Workflow-RPA\INDEX.md`:149-156 — cross_domain_deps=[](변경 전파 manifest)와 AUTHORITY_CHAIN §4.2 기능 의존성 표(소비4/제공3)의 이원 의미론 선택
   - 선택지: (a) 현행 이원 체계(manifest=Phase 2 종료 시점 횡단 영향 0, 기능 참조는 별도 표) / (b) manifest에 기능 의존성 일치 반영
   - 판정: KEEP — INDEX §7은 'Phase 2 종료 시점에 횡단 영향 0(전파 불필요)' 의미로 한정 명시(L156)되어 기능 참조 표와 모순 아님; '기능 참조 vs manifest dependency' 정의 주석 1줄 추가 권장
26. **[KEEP]** `docs\sot 2\3-4_Workflow-RPA\05_browser-rpa\browser_security.md`:74 — BrowserSandboxConfig network.mode에 "unrestricted" 옵션을 존치하는 선택(기본은 whitelist/default deny + block_internal_ips=true)
   - 선택지: (a) 옵션 존치+기본 deny(현행) / (b) unrestricted 제거 또는 ADMIN 승인 게이트 명시
   - 판정: KEEP — LOCK-WF-10은 모드 집합을 규정하지 않으며 기본값이 deny·내부IP차단 true로 fail-safe(L76, L207); unrestricted 사용 조건(승인+감사 로그) 명시는 보강 후보

> notes: 입력 union: clc 60 + tight 38(전수 clc 부분집합) + GP-A 21 → mf_in 객관확정 39건 및 그 소스 중복(T8-006/010… 등 매핑 확인) 제외 후 후보 ~44건 전수 디스크 실측. 주관 26건 도출(앵커 22 대비 +4) — 강제 짜맞춤 금지 지침에 따라 실측 결과 유지. 차이 추정 사유: 원판정이 LOCK 큐레이션 계열(T6-231/232, T8-284)과 경계 항목(T8-165/T8-288 등) 일부를 객관 또는 오탐 버킷으로 처리했을 가능성. [오탐(디스크 반박) 7]: T8-017(재귀 depth는 create_child_state로 분기별 전달, 공유 카운터 증가 race 없음 — dag_architecture.md:441), T8-145(overlap은 APScheduler max_instances로 강제 — time_trigger.md:217 _overlap_to_max_instances), WF-RPA-3-4-010(보고서가 desktop 이월을 자체 공개 — phase2_security_audit_report.md:84,101), T8-046류 아님 주의, T8-192의 '§5 부재' 주장 절반(§5 실

### 6-3_Agent-Teams-PARL (24건)

1. **[KEEP]** `docs\sot 2\6-3_Agent-Teams-PARL\01_parl-pattern\reward_function.md`:177 (정상범위 §3.5 L93) — 보상 클리핑 범위를 실제 신호 크기(최대 ~+1.5)보다 넓은 [-10,+10]으로 설정한 안전 마진 선택.
   - 선택지: (a) 현행 [-10,+10] 넓은 안전 클립 유지 (b) 신호 범위 밀착 [-2,+2]로 축소 (c) 클립 제거
   - 판정: (a) 유지 — RULE/PLAN/LOCK 어디에도 클리핑 범위 정본이 없고, 넓은 클립은 향후 보상항 추가 시 재학습 불요한 보수적 가드이며 §3.5 정상범위 [0,1.0]과 모순되지 않음(L175 LOCK 위반 -100 경로는 클립 미적용으로 별도 보존).
2. **[KEEP]** `docs\sot 2\6-3_Agent-Teams-PARL\01_parl-pattern\parl_security.md`:109-120 — 행동 이상 탐지 알고리즘으로 IsolationForest(contamination=0.05 고정, 자기 window fit-predict)를 선택.
   - 선택지: (b) IsolationForest 유지 (a) z-score/EWMA 등 경량 통계 기법 (c) 사전 학습된 정상 프로파일 대비 판정
   - 판정: 현행 IsolationForest 유지 — _index.md §6 정본은 '행동 패턴 클러스터링' 방식만 지정하고 구체 알고리즘은 미지정이므로 설계 재량이며, contamination 값과 fit/predict 분리는 운영 튜닝 항목으로 본문 주석에 한계(자기데이터 판정)만 명시 권고.
3. **[🔧CHANGE]** `docs\sot 2\6-3_Agent-Teams-PARL\01_parl-pattern\ppo_algorithm.md`:173, 177 — PPO 학습 루프에 task-TEE 상한과 별도인 학습 루프 반복 상한(TEE_MAX_V3)을 도입하는 선택.
   - 선택지: (a) 학습 루프 별도 상한 도입(현행) (b) AT-010 P-level 값(3/5/10)을 학습 루프에 직접 적용 (c) max_episodes만으로 제한
   - 판정: 별도 학습 루프 상한 자체는 합리적 설계 선택으로 유지하되, AUTHORITY_CHAIN §5(L157) 정본이 'AT-009/010 상한은 P-level 기반(버전 무관)'이라 명시하므로 LOCK 인용문에 '[V3는 별도 PPO 학습 루프 상한 적용]'을 덧붙인 것은 DESIGN LOCK 인용 변형 = 정본 모순 — 설계 상수임을 분리 표기하고 TEE_MAX_V3 값을 본 문서에 정의해야 함(현재 미정의 forward 상수).
4. **[🔧CHANGE]** `docs\sot 2\6-3_Agent-Teams-PARL\01_parl-pattern\ppo_algorithm.md`:185-200 — 비용 상한(AT-011) 차단 검사를 episode 시작 전 1회로 두고 rollout step 중에는 누적만 하는 검사 주기 선택.
   - 선택지: (a) episode 경계 검사(현행) (b) step마다 exceeded() 즉시 검사·차단 (c) rollout 버퍼 단위 검사
   - 판정: (b) step 단위 즉시 차단으로 보강 — RULE 1.3 §5 L215 직계 LOCK-AT-011 정본은 '비용 상한 초과 호출은 승인 없이 자동 차단'이므로, 한 rollout(최대 2048 step) 내 초과 후 후속 env.step 호출이 계속되는 현행은 정본의 '초과 호출 차단'과 모순(검사 주기는 설계 재량이나 정본 하한은 즉시 차단).
5. **[KEEP]** `docs\sot 2\6-3_Agent-Teams-PARL\01_parl-pattern\convergence_criteria.md`:71, 126 — 수렴 판정을 production 4/5 메트릭(보수적 게이트), 안정성 인증을 5/5(더 엄격)로 두는 계층형 게이트 설계.
   - 선택지: (a) 계층형 4/5+5/5(현행, §3.3에서 §3.1 '3개 모두'·§3.2 '2/3'를 매핑 통합) (b) 단일 게이트로 일원화 (c) §3.2 2/3 관용 정책 채택
   - 판정: (a) 유지 — §3.3이 P3-1 직계(§3.1)와 _index 직계(§3.2)를 명시적으로 매핑한 뒤 production 채택을 4/5로 단일 확정했고(L71) R-63-5 정합 표기까지 있어 정본 모순 없음; 5/5(L126)는 별도 '안정성 인증' 상위 단계로 역할이 구분됨.
6. **[KEEP]** `docs\sot 2\6-3_Agent-Teams-PARL\01_parl-pattern\convergence_criteria.md`:150-165 — 수렴 후 안정성 '유지' 검증(StabilityValidator)을 보상 평균 10% 하락 부재 단일 지표로 한정하는 검증 범위 선택.
   - 선택지: (a) 보상 유지 단일 지표(현행) (b) 5 메트릭 전체 재계산 유지 검증 (c) 보상+KL 2지표
   - 판정: (a) 유지하되 역할 명시 — §4.1c의 '5 메트릭 5/5'는 안정성 인증 진입 조건이고 §4.3 validator는 수렴 후 50 episode '유지 확인' 전용이라는 단계 구분을 본문에 1줄 명시 권고; 진입 조건이 이미 5/5를 강제하므로 유지 검증 지표 축소는 비용-효익상 합리적 재량.
7. **[🔧CHANGE]** `docs\sot 2\6-3_Agent-Teams-PARL\02_agent-swarm\P1-07_in_memory_messagebus.md`:132 (동일 패턴 L136/289/330/431 등) — 모든 버스 메시지에 trace_id를 필수화(누락 시 TraceMissingError 거부)하는, 정본 LOCK보다 엄격한 추적 정책 선택.
   - 선택지: (a) 전 메시지 trace_id 필수(현행) (b) Checkpoint/Replay/Fork 관련 메시지만 필수(LOCK 문언 그대로) (c) 권장+경고
   - 판정: 전 메시지 필수 정책(a)은 LOCK보다 엄격한 상위 정책으로 유지 — 단 AUTHORITY_CHAIN L62/L85 정본은 LOCK-AT-007을 'Checkpoint/Replay/Fork는 trace_id 단위로만 허용'으로 한정하므로 이 정책을 'LOCK-AT-007'로 라벨링한 것은 DESIGN LOCK 범위 재정의 = 정본 모순이며 라벨만 교정.
8. **[KEEP]** `docs\sot 2\6-3_Agent-Teams-PARL\02_agent-swarm\P1-07_in_memory_messagebus.md`:472-477 — 구독자 콜백을 asyncio.gather가 아닌 순차 await로 직렬 호출하는 전달 모델 선택(head-of-line 지연 감수).
   - 선택지: (a) 직렬 전달(현행 — 순서 결정성·에러 격리 단순) (b) gather 병렬 전달 (c) create_task fire-and-forget
   - 판정: (a) 유지 — V1 in-memory 버스는 sequence_number 기반 FIFO 순서 보장(L144)이 본문 계약이고 직렬 호출이 이를 가장 단순히 보장하며, 처리량 요구는 V2 Redis 버스(message_bus.md)로 위임되는 단계 구조라 정본 모순 없음.
9. **[KEEP]** `docs\sot 2\6-3_Agent-Teams-PARL\02_agent-swarm\P1-07_in_memory_messagebus.md`:145-146 — hmac_signature(LOCK-AT-012)와 ttl_seconds를 V1에서는 예약 필드(None)로만 두고 시행을 V2로 이연하는 단계적 기능 적용 선택.
   - 선택지: (a) V1 예약+V2 시행(현행 — L133 'V2에서 활성화 예정', P1-04 IT-06 'AT-012 V2 HMAC 서명' 동일) (b) V1부터 HMAC/TTL 시행 (c) 필드 제거 후 V2 추가
   - 판정: (a) 유지 — 단일 프로세스 in-memory 버스(V1)는 신뢰 경계 내부라 HMAC 실익이 없고 도메인 전반(P1-04/P1-07)이 V2 활성화로 일관 표기하므로 무모순; 단 ttl_seconds는 'V1 미시행(만료 검사 없음)'을 본문에 명시해 오사용 방지 권고.
10. **[KEEP]** `docs\sot 2\6-3_Agent-Teams-PARL\02_agent-swarm\decision_aggregator.md`:756, 772 — vote_distribution을 정수 백분율 int(v*100)로 표기하고 raw 가중치는 metadata.weighted_votes_raw에 보존하는 표현 단위 선택.
   - 선택지: (a) 정수 % + raw metadata 보존(현행) (b) float raw 직접 노출 (c) 정규화 비율 float
   - 판정: (a) 유지 — 스키마 표현 단위는 정본 규정이 없는 설계 재량이고 raw 값이 metadata에 무손실 보존되므로(L762) 정보 손실 없음; confidence와 단위가 다름을 필드 주석으로 명시하면 충분.
11. **[KEEP]** `docs\sot 2\6-3_Agent-Teams-PARL\02_agent-swarm\decision_aggregator.md`:865, 920 — Consensus veto·deadlock 결과를 별도 status 없이 'TIE'(tied_choices=None)로 수렴시키는 상태 어휘 선택(TIE = 'Lead 단독 결정 필요' 우산 의미).
   - 선택지: (a) TIE 오버로드(현행 — metadata.reason으로 구분) (b) VETO/DEADLOCK 별도 status 추가 (c) INSUFFICIENT 재사용
   - 판정: (a) 유지 — 모든 경로가 lead_decision_required=True로 LOCK-AT-002(Lead 단독 확정) 정본을 충족하고 metadata.reason(veto_exercised/deadlock_max_rounds)으로 의미가 보존되므로 모순 없음; status enum 확장은 소비자 호환성 비용만 추가.
12. **[KEEP]** `docs\sot 2\6-3_Agent-Teams-PARL\02_agent-swarm\message_bus.md`:1062-1064 — Istio outlierDetection 수치(consecutive5xxErrors:5, interval:30s, baseEjectionTime:30s)를 OBSERVE_ONLY 주석과 함께 예시값으로 게재하는 선택.
   - 선택지: (a) 예시값+OBSERVE_ONLY 주석(현행) (b) 수치 삭제·6-5 정본 링크만 (c) Phase 3 확정값 대기
   - 판정: (a) 유지 — 각 행에 '6-5 정본 OBSERVE_ONLY (Phase 3 런타임 결정)' 주석이 명시돼 정본 권위를 침범하지 않는 참고 예시임이 분명하고(L1057 sot2-source 주석 포함), 6-5 SDAR 정본과의 충돌이 발생하지 않음.
13. **[KEEP]** `docs\sot 2\6-3_Agent-Teams-PARL\02_agent-swarm\message_bus.md`:587-588 (목표 L823) — 재연결 정책을 exponential backoff(0.5s×2^n, cap 60s)·max retry 12회·실패 시 In-Memory fallback 5분으로 설정한 회복 전략 선택.
   - 선택지: (a) 현행(짧은 단절 <60s 회복 + 장기 장애 fallback 이원화) (b) retry 축소로 <60s 총합 정합 (c) fast-fail 즉시 fallback
   - 판정: (a) 유지 — L823 '<60s 회복' 목표는 'Redis 5초 단절' 시나리오 측정 기준으로 12회 retry 총합과 다른 층위라 모순 아님(장기 장애는 L589 5분 fallback이 담당); 단 L588 '≈ 합 2,047s'는 cap 60s 미반영 산술이므로 cap 반영 재계산 표기(약 7분) 권고.
14. **[🔧CHANGE]** `docs\sot 2\6-3_Agent-Teams-PARL\03_team-composition\P1-01_lead_agent_definition.md`:520 — Lead Agent 장애 시 Fallback 재시도 횟수를 3회로 설정한 값 선택.
   - 선택지: (a) 3회(현행) (b) 1회 후 즉시 에스컬레이션 (c) 지수 backoff 5회
   - 판정: 3회 값 자체는 합리적 재량으로 유지하되, '= LOCK-AT-010 P0 기준'은 오인용 — LOCK-AT-010 정본(Part2 §6.7 L5048)은 TEE 반복 상한이지 fallback 재시도 규정이 아니므로(숫자 3 일치는 우연) DESIGN LOCK 인용 모순을 교정.
15. **[KEEP]** `docs\sot 2\6-3_Agent-Teams-PARL\03_team-composition\P1-06_delegation_chain.md`:45-46, 703 — V1에서 위임 깊이 상한을 MAX_DEPTH_V1=2 하드코딩으로 두고 config 기반 동적 상한(V2+=3)은 후속 Phase로 이연하는 단계적 구현 선택.
   - 선택지: (a) V1 하드코딩+Phase 이연(현행 — L703 'max_depth=2 하드코딩' 명시) (b) V1부터 config 플럼빙 (c) 상수 2개(V1/V2) 동시 정의
   - 판정: (a) 유지 — LOCK-AT-004 정본 '위임 체인 최대 깊이 3단계 (V1 config=2)'와 값이 정확히 일치하고(§2.2 verbatim 인용), §4.2 Phase 복구 정책 표가 하드코딩임을 투명하게 명시하므로 V2 전환 시점에 config화하면 충분.
16. **[KEEP]** `docs\sot 2\6-3_Agent-Teams-PARL\03_team-composition\P1-10_turn_limit.md`:290-300, 621 — V1 턴 카운터를 단일 asyncio 루프 전제의 인메모리 비원자 구조로 두고 분산 원자화(Redis)는 Phase 2로 이연하는 동시성 모델 선택.
   - 선택지: (a) V1 인메모리+Phase 2 Redis 원자화(현행 — L621 명시) (b) V1부터 lock 도입 (c) V1부터 Redis
   - 판정: (a) 유지 — V1 배포 단위가 단일 프로세스 asyncio이고 분산 전환 시점의 Redis 원자 증가가 Phase 2 표(L621)와 예외 정책 E-6(L776)에 이미 설계돼 있어 단계 계획이 정본 본문에 내재화된 선택임(LOCK-AT-009 값 자체는 무변).
17. **[KEEP]** `docs\sot 2\6-3_Agent-Teams-PARL\03_team-composition\P1-10_turn_limit.md`:415-417 — TurnRecord.is_final을 '상한 도달 마지막 턴'에만 표시하고 조기 종료 대화에는 미표시하는 플래그 의미론 선택.
   - 선택지: (a) is_final=상한 도달 의미(현행) (b) 모든 종료 시 마지막 턴 마킹 (c) 종료 사유 enum으로 대체
   - 판정: (a) 유지 — is_final의 정본 규정이 없어 의미론은 재량이며 조기 종료의 종결 정보는 force_terminate의 _termination_reason과 스냅샷이 담당; 필드 주석에 '상한 도달 시에만 True' 1줄 명시로 소비자 오해만 차단 권고.
18. **[KEEP]** `docs\sot 2\6-3_Agent-Teams-PARL\03_team-composition\cost_budget.md`:251-259 — 100% 차단(CostLimitExceeded raise)을 80% 경고보다 선행 평가해 단일 add()로 80%→100%를 건너뛰는 경우 경고를 생략하는 순서 정책 선택.
   - 선택지: (a) 차단 우선(현행 — 안전 우선) (b) 경고 선발행 후 차단 (c) 차단 예외에 경고 정보 동봉
   - 판정: (a) 유지 — LOCK-AT-011 정본 요구(100% 자동 차단)는 충족되며 80% 경고는 보조 관측 신호로 정본 의무가 아님; §5.5의 '차단 시 비용 리포트 생성' 경로가 초과 사실을 어차피 보고하므로 관측 공백은 실질 미미(개선 시 (c) 권장).
19. **[KEEP]** `docs\sot 2\6-3_Agent-Teams-PARL\03_team-composition\cost_budget.md`:261-265 — P2 에이전트의 OWNER 세션 미확인 시 예산을 P0(100k)으로 강등하는 보수적 폴백 정책 선택.
   - 선택지: (a) P0 폴백(현행 — fail-safe 축소) (b) 즉시 차단(예산 0) (c) P1 중간값 폴백
   - 판정: (a) 유지 — LOCK-AT-008/RULE 1.3 §3.3의 'P2는 명시적 승인 필수' 취지에 부합하는 fail-safe 방향(미승인 시 최소 예산)이며 정본 모순 없음; 세션 중 확인 상태 변동 시 예산 플립은 '승인 시점부터 P2 예산 적용'을 본문 1줄로 명시해 해소 권고.
20. **[KEEP]** `docs\sot 2\6-3_Agent-Teams-PARL\03_team-composition\cost_budget.md`:249-257 (요구: P1-12_cost_limit.md L54/L99) — P1-12의 'Σ(agent_cost) ≤ session_budget' 관계를 런타임 합산 검사가 아닌 Agent별 예산 분배(per-agent cap)로 충족시키는 강제 메커니즘 선택.
   - 선택지: (a) 분배 기반 보장(현행 — (agent_id,session_id) 키 개별 상한) (b) add() 경로에 세션 합산 원자 검사 추가 (c) 이원화(개별+합산)
   - 판정: (c) 권고 — P1-12 정본 본문(L54, L99)이 Σ 관계 자체를 요구하나 메커니즘은 미지정('round-robin 또는 priority-based 분배')이므로 분배 기반도 적합하지만, 분배 합이 session_budget을 넘지 않음을 보장하는 규칙이 cost_budget.md에 미명시라 합산 검사 1단계 추가가 가장 저비용 정합화.
21. **[KEEP]** `docs\sot 2\6-3_Agent-Teams-PARL\04_autonomy-levels\P1-08_gate_integration.md`:358-362 — check_cost에서 cost_limit 미설정(기본 inf) 또는 ≤0일 때 ratio를 0으로 강제해 통과시키는 '0/음수 = 무제한' 의미론 선택.
   - 선택지: (a) 0/음수=무제한 통과(현행) (b) 0=명시적 차단, 음수=설정 오류 거부 (c) 미설정만 통과·0 이하 거부
   - 판정: (c) 권고하되 현행 유지 가능 — LOCK-AT-011 정본은 '상한 초과 시 차단'만 규정하고 미설정/0 의미론은 미규정이라 설계 재량이나, 0 예산의 fail-open은 안전 게이트 관례와 어긋나므로 차기 개정 시 0 이하 명시 거부로 강화 권고(현행이 정본을 위반하지는 않음).
22. **[KEEP]** `docs\sot 2\6-3_Agent-Teams-PARL\04_autonomy-levels\P1-09_execute_tool_restriction.md`:474-482 — reset() 시 TEE 상태(_current_phase/_tee_iteration/_completed)는 초기화하되 위반 로그는 '감사 추적' 목적으로 유지하는 감사 보존 정책 선택.
   - 선택지: (a) 위반 로그 인스턴스 수명 유지(현행 — L482 주석 명시) (b) reset마다 로그도 초기화 (c) reset 시 외부 sink로 flush 후 초기화
   - 판정: (a) 유지 — 감사 추적 보존은 의도가 주석으로 명시된 정당한 설계이며 정본 모순 없음; 인스턴스를 다중 태스크에 재사용할 경우 로그 항목에 task 식별자를 포함시켜 경계 구분만 보강 권고((c)는 V2 구조화 로깅 연동 시 자연 해소).
23. **[KEEP]** `docs\sot 2\6-3_Agent-Teams-PARL\04_autonomy-levels\p2_trading_policy.md`:219-235 (RULE 인용 L132-135) — P2 Trading 상태 머신(§4.2, 13 전이)의 범위를 세션 수명주기(활성화/자동 OFF/비상 OFF)로 한정하고 'ON 상태 매 요청 확인 프롬프트'는 상태 전이 외부 요청 처리 계층에 두는 모델링 범위 선택.
   - 선택지: (a) 세션 수명주기 상태 머신+요청 게이트 외부화(현행) (b) ON 상태 self-transition으로 매 요청 확인을 상태 머신에 포함 (c) 요청별 미니 상태 추가
   - 판정: (a) 유지하되 명문화 필수 — RULE 1.3 §3.3 L142-145(최상위 정본, 본문 L133-135 verbatim 인용)가 'P2 실행: 매 요청마다 확인 프롬프트 필수'를 요구하므로, 상태 머신 외부에서 이 게이트를 수행한다는 운영 절차(미확인 요청 trade_p2_denied 거부 포함)를 §4 또는 §5에 명시해 RULE 요구가 설계상 어디서 충족되는지 추적 가능하게 해야 함(모델링 범위 자체는 재량).
24. **[KEEP]** `docs\sot 2\6-3_Agent-Teams-PARL\02_agent-swarm\execution_engine.md`:374-377 — TEE 실행 엔진에서 07 Gate(LOCK-AT-005) 검증을 엔진 내부 강제가 아닌 '호출 경로 선행 통과 전제'로 두는 enforcement 위치 선택.
   - 선택지: (a) 호출자 책임 전제(현행 — P1-04/P1-05/각 Agent 정의가 게이트 수행) (b) agent.execute 직전 엔진 레벨 토큰 검증 추가 (c) 이중 검증(호출자+엔진)
   - 판정: (a) 유지 가능 — LOCK-AT-005 정본(Part2 §6.7 L5043)은 '모든 에이전트 실행은 07 Gate 선행 통과 필수'로 검증 위치를 지정하지 않아 호출 경로 게이트(P1-04 _check_gate_for_stage, P1-05 Phase 1, P1-08 GateChecker)로 충족 가능한 계층화 선택이나, defense-in-depth로 (c) 엔진 직전 token verify 추가를 차기 개정 권고.

> notes: 방법론: 4개 입력 전수(클로드 clc 105건+tight 부분집합, GPT GP-A 15건, mf_in 객관확정 38건+미확정 1건) 대조 후, (1) mf_in 확정분과 동일/중복 finding 제외, (2) verify=refuted 24건 오탐 제외, (3) SYNONYM/표기류(T5-159, T5-310, T5-391, T5-411, T8-180, T6-015, T6-395, T6-468 등) 제외, (4) lock 부재 동시성 4건(T8-034/124/332/400)은 mf_in #3·#4(P1-08/P1-13 동시성 확정)와 동일 패턴 중복으로 제외, (5) 'documented-but-unimplemented' 패턴(T8-245/271/176 등)은 mf_in #28/#29/#32와 동일 성격 중복으로 제외했다. 잔여 후보 전수를 디스크 실측(파일:라인 확인) 후 24건을 주관적 설계선택으로 확정 — 앵커 22 대비 +2. 차이 사유: (a) 원판정의 finding 단위 병합 방식을 알 수 없어 본 재도출은 동일 쟁점 다중 ID를 3건 병합(T8-003+6-3-001, T6-031+T6-045, T8-050+T8-256)했고, (b) 경계 항목

### 1-1_Verifier-Reasoning-Engines (20건)

1. **[KEEP]** `docs\sot 2\1-1_Verifier-Reasoning-Engines\00_common\base_reasoning_engine_abc.md`:160 — D-시리즈 추론 엔진의 should_escalate() 기본 임계값을 0.5(또는 FAILED 상태)로 설정 — 검증 엔진(0.8)과 다른 값.
   - 선택지: (a) 0.5 유지(FAIL 밴드 <0.5 정렬) (b) 검증 엔진과 동일 0.8 (c) 기본값 없이 엔진별 오버라이드 강제
   - 판정: KEEP (a) — LOCK-VR-05(DESIGN LOCK)는 verdict 밴드만 정의하고 추론엔진 에스컬레이션 임계는 미규정. 0.5는 FAIL 밴드와 정렬된 합리적 기본값이며 본문 L150이 오버라이드 가능을 명시.
2. **[KEEP]** `docs\sot 2\1-1_Verifier-Reasoning-Engines\00_common\confidence_thresholds.md`:68-78 — REVIEW 구간(0.5~0.8)에서 I-19 승인 경로와 I-20→D-1 에스컬레이션 경로를 병행·독립 실행하고 D-1 결과가 I-19 판정을 자동 대체하지 않는 아키텍처.
   - 선택지: (a) 병행 독립 + I-19 비대체(현행) (b) 직렬화(D-1 완료 후 I-19) (c) 충돌 우선순위 규칙 명문화
   - 판정: KEEP (a) — 본문 L77-78이 비차단·비대체 원칙을 명시한 의도적 설계이며, 우선순위 충돌 규칙은 escalation_flow.md L594 GAP-3로 Phase 1 확정 예정으로 등재됨. 정본 모순 없음.
3. **[KEEP]** `docs\sot 2\1-1_Verifier-Reasoning-Engines\00_common\confidence_thresholds.md`:80-86 — FAIL(<0.5)을 잠정 판정으로 두고 D-1 재검증 성공 시 D-1의 새 VerifyResult가 원 FAIL 판정을 대체하는 정책.
   - 선택지: (a) D-1 대체 허용(현행) (b) FAIL 최종 확정 + 재검증 결과는 참고만 (c) FAIL_AUTO_REJECT/FAIL_ESCALATED 상태 분리
   - 판정: KEEP (a) — base_verifier_abc.md §5.1 흐름('성공 → 결과 반환')과 정합하는 명시 설계(L85 인용 명기). LOCK 위반 없음, finality 명문화는 Phase 1 개선 옵션.
4. **[KEEP]** `docs\sot 2\1-1_Verifier-Reasoning-Engines\00_common\failover_policy.md`:118-124 — SoT 미정의 영역에서 LOCK-VR-07의 '연속 3회' 규칙을 GPT-4o/Claude Sonnet/Ollama 각 failover 단계에 동일 적용(단계별 최대 3회).
   - 선택지: (a) 단계별 3회 동일 적용(현행) (b) 전체 경로 global deadline + 잔여 예산 차감형 (c) 단계별 차등 재시도 수
   - 판정: KEEP (a) — L118이 '신규 정의 (SoT 미정의)'로 권한 경계를 명시한 보수적 확장이며 LOCK-VR-07 원문과 무모순. 전역 deadline 추가는 Phase 1 운영 튜닝 사항.
5. **[KEEP]** `docs\sot 2\1-1_Verifier-Reasoning-Engines\01_logic-verifier\performance_benchmark.md`:178 — SAT Phase 3 입력 상한을 CNF 변수 V>30 거부(VRE_INVALID_INPUT)로 설정.
   - 선택지: (a) V=30 상한(현행) (b) 상한 하향(예: 20) (c) 시간예산 기반 동적 상한
   - 판정: KEEP (a) — worst-case 지수 메모리 방어용 신규 설계값으로 SoT 미규정. S-5(V=25, timeout 500ms)와 error_handling T3(V≥20)는 상한 내 타임아웃 유도 시나리오로 경계 모순 아님.
6. **[KEEP]** `docs\sot 2\1-1_Verifier-Reasoning-Engines\01_logic-verifier\error_handling.md`:186 — C-1 재시도 백오프 전략을 '즉시 재시도(no delay)'로 설정.
   - 선택지: (a) no-delay(현행) (b) 짧은 고정 backoff (c) 지수 backoff
   - 판정: KEEP (a) — 근거 열에 LOCK-VR-12 단일응답 ≤2s SLA를 명시한 의도적 정책 선택. 최대 1회 재시도(D2.0-02 §3.2 RULE 인용)라 반복 hammering 위험이 구조적으로 제한됨.
7. **[KEEP]** `docs\sot 2\1-1_Verifier-Reasoning-Engines\01_logic-verifier\spec.md`:649-651 — shallow 깊이 검증 시 confidence를 min(conf, 0.7)로 캡 — 결과적으로 shallow는 PASS(≥0.8) 불가, 항상 REVIEW 이하.
   - 선택지: (a) 0.7 캡 유지(shallow 자동 PASS 금지) (b) 캡 제거 (c) 캡 유지 + I/O 계약에 '항상 REVIEW' 동작 명문화
   - 판정: KEEP (a) — Phase 3 미수행 검증의 자동 통과를 막는 보수적 정책('보수적 하한 적용' 주석 명시)으로 LOCK-VR-05 밴드 정의와 무모순. (c)의 문서화 보강은 선택적 개선.
8. **[KEEP]** `docs\sot 2\1-1_Verifier-Reasoning-Engines\02_math-verifier\spec.md`:948 — is_valid를 '차원 일관성 AND confidence≥0.5'로 정의 — 판정 임계와 결합한 필드 의미론.
   - 선택지: (a) 현행 정의 (b) is_valid=구조적/차원 유효성만 (c) is_valid 제거, judgment로 일원화
   - 판정: KEEP (a) — VerifyResult.is_valid의 의미 부여는 스키마 수준 설계 재량이며 §10.5에 산식이 명시됨. 정본(LOCK/RULE)이 is_valid 의미를 규정하지 않아 무모순.
9. **[KEEP]** `docs\sot 2\1-1_Verifier-Reasoning-Engines\02_math-verifier\performance_benchmark.md`:255-256 — Phase 3 symbolic/numeric 각 타임아웃을 min(등급 캡, phase3_budget//2)로 클램프하는 산출 알고리즘.
   - 선택지: (a) //2 클램프(현행) (b) 비례 배분(예: sym 70%/num 30%) (c) 클램프 발동 시 경고 로그 추가
   - 판정: KEEP (a) — docstring(L248)이 '합 = symbolic + numeric ≤ Phase 3 예산' 불변식을 명시한 보수적 산식. 소예산에서 등급 캡보다 작아지는 것은 의도된 안전 동작.
10. **[KEEP]** `docs\sot 2\1-1_Verifier-Reasoning-Engines\02_math-verifier\spec.md`:1058-1062 — 예산 70% 소진 시 Phase 3을 numeric-only 간소화 모드로 전환하는 중간 타임아웃 체크포인트(계수 0.7).
   - 선택지: (a) 0.7 단일 체크포인트(현행) (b) Phase별 다중 체크포인트 (c) 계수 조정(0.6~0.8)
   - 판정: KEEP (a) — LOCK-VR-12 내 완료를 위한 조기 강등(degradation) 전략으로 합리적 값 선택. 체크포인트 추가·계수 조정은 실측 후 튜닝 사항이며 정본 미규정.
11. **[KEEP]** `docs\sot 2\1-1_Verifier-Reasoning-Engines\03_code-verifier\error_handling.md`:210 — C-3 재시도 백오프 전략을 '즉시 재시도(no delay)'로 설정(Docker 일시 장애 포함).
   - 선택지: (a) no-delay(현행) (b) Docker 장애 대비 짧은 backoff (c) 에러 코드별 차등 backoff
   - 판정: KEEP (a) — LOCK-VR-15(Sandbox 30s)/LOCK-VR-12 근거가 명시된 정책 선택이고, 컨테이너 재생성 1회 허용·SANDBOX_OOM 메모리 1.5배 상향(L213-214) 등 보완책이 동반됨.
12. **[KEEP]** `docs\sot 2\1-1_Verifier-Reasoning-Engines\03_code-verifier\spec.md`:460-467 — 치명적(severity=error) 구문 오류 발견 시 VRE_INVALID_INPUT으로 조기 실패(검증 결과 반환 대신 fail-fast).
   - 선택지: (a) hard-fail(현행) (b) is_valid=False + syntax_errors 채워서 반환 (c) 요청 플래그로 두 모드 선택
   - 판정: KEEP (a) — 경고 수준 이슈는 syntax_errors로 수집·반환(L457-458)하고 파싱 불능 입력만 거부하는 입력 검증 정책. CodeVerifyResult 계약과 양립하며 정본 위반 없음.
13. **[KEEP]** `docs\sot 2\1-1_Verifier-Reasoning-Engines\04_think-engine\monitoring_metrics.md`:75-76 — M-COM-03 Error Rate 경보 임계를 WARNING ≥20% / CRITICAL =100%로 설정.
   - 선택지: (a) 현행 유지 (b) WARNING 5%/CRITICAL ≥50% 등 강화 (c) CRITICAL만 ≥99%로 완화(등호 위험 제거)
   - 판정: KEEP (a) — 경보 임계는 SoT/LOCK 미규정 운영 튜닝값으로 설계 재량. 운영 데이터 확보 후 =100% 등호를 ≥로 바꾸는 강화 검토 권장하나 현행이 정본 모순은 아님.
14. **[KEEP]** `docs\sot 2\1-1_Verifier-Reasoning-Engines\04_think-engine\reasoning_strategies.md`:643-647 — GoT prune_low_confidence를 리프 노드 한정 pruning으로 설계(내부 노드 비대상).
   - 선택지: (a) 리프 한정(현행, 그래프 연결성 보존) (b) 내부 노드 포함 pruning (c) 경로 단위 pruning
   - 판정: KEEP (a) — docstring이 'confidence 미만 리프 노드를 pruning'으로 범위를 명시한 알고리즘 선택. 내부 노드 제거는 그래프 무결성 훼손 비용이 있어 리프 한정이 표준적.
15. **[KEEP]** `docs\sot 2\1-1_Verifier-Reasoning-Engines\04_think-engine\reasoning_strategies.md`:388-392 — ToT 최적 경로 점수를 경로 상 노드 confidence의 곱(확률적 해석)으로 산정, 동점 시 토큰 소비 적은 경로 우선.
   - 선택지: (a) confidence 곱(현행) (b) 기하평균(깊이 정규화) (c) 최소값/산술평균
   - 판정: KEEP (a) — '확률적 해석' 근거가 docstring에 명시된 알고리즘 선택이며 정본 미규정. 깊이 편향이 실측에서 확인되면 기하평균 정규화를 Phase 1 후 검토.
16. **[KEEP]** `docs\sot 2\1-1_Verifier-Reasoning-Engines\05_multimodal-engine\fusion_pipeline.md`:624-635 — Hybrid Stage-2 그룹 품질점수로 Early Fusion 결과의 confidence를 프록시 사용(없으면 멤버 품질 가중평균 fallback).
   - 선택지: (a) confidence 프록시(현행) (b) 멤버 품질(§6.2 completeness/clarity/relevance) 가중평균만 사용 (c) 두 값 혼합 가중
   - 판정: KEEP (a) — docstring(L630-631)이 'Early Fusion 결과의 confidence 또는 멤버 품질의 가중 평균'으로 프록시 선택과 fallback을 모두 명시한 설계. 정본 위반 없음.
17. **[KEEP]** `docs\sot 2\1-1_Verifier-Reasoning-Engines\05_multimodal-engine\modality_preprocessors.md`:389 — 청크 임베딩 per-chunk 타임아웃을 timeout_ms*0.9/len(chunks) 균등 분배(하한 가드 없음)로 산출.
   - 선택지: (a) 균등 분배(현행) (b) per-chunk 하한 가드 추가(예: ≥50ms) (c) 청크 수 상한 도입
   - 판정: KEEP (a) — 예산 총합 불변식(≤0.9×timeout)을 보장하는 단순 균등 분배 설계. 128K 토큰 극단 입력은 spec §3.2 최대 크기 내 희귀 케이스로, 하한 가드는 Phase 1 실측 후 추가 검토.
18. **[KEEP]** `docs\sot 2\1-1_Verifier-Reasoning-Engines\04_think-engine\performance_benchmark.md`:131-142 — D-1 시간예산 이원화 — ABC §7.2 시나리오 기본값(단순 CoT ≤800ms/심층 ≤4,000ms)과 벤치마크 §4.1 전략별 권장 timeout(CoT 4,200/ToT·GoT 6,200ms, 10s 복합 SLA 기준)을 병존시키는 배분.
   - 선택지: (a) 이원 유지(시나리오 기본값 vs 전략별 권장 상한) (b) ABC §7.2 값으로 통일 (c) 벤치마크 값으로 ABC 표 개정
   - 판정: KEEP (a) — 정본은 LOCK-VR-12(2s/10s)뿐이며 두 표 모두 SLA 내. ABC §7.2는 'IMPL-DETAIL 신규 설계' 시나리오 기본값(L398), 벤치 §4.1은 10s 기준 전략별 상한으로 적용 축이 달라 무모순(L142 출처 정합 명시).
19. **[KEEP]** `docs\sot 2\1-1_Verifier-Reasoning-Engines\VERIFIER_REASONING_ENGINES_구조화_종합계획서.md`:3884, 3996 — §B 부록 스키마 스케치의 timeout_ms 기본값 30,000/60,000ms(상한 300s/600s) — LOCK-VR-12 SLA(2s/10s)보다 큰 failsafe 상한 부여.
   - 선택지: (a) 승급 스키마 정본 기준(필수 필드·기본값 없음, common_types.md L48-51/L146-149 현행) (b) 부록 기본값 채택 (c) SLA 정렬 기본값(2s/10s)
   - 판정: KEEP — R-01-3 원문(plan L275)은 'timeout_ms 필드 필수 기재'만 요구하고 LOCK-VR-12는 응답 SLA(목표)이지 타임아웃 상한 규정이 아님. 승급 스키마 정본 common_types.md가 '미지정 불가(호출자 필수 설정)'로 더 엄격히 확정했으므로 부록 스케치 기본값은 역사 기록으로 무해, 정본 모순 불성립.
20. **[KEEP]** `docs\sot 2\1-1_Verifier-Reasoning-Engines\VERIFIER_REASONING_ENGINES_구조화_종합계획서.md`:1545 — Early-Fusion 예산 구성(권장 timeout 5,400ms + FIXED_OVERHEAD 600ms + PREPROCESS 1,000ms = 7,000ms)으로 10s 복합 SLA 대비 3,000ms 마진을 두는 배분.
   - 선택지: (a) 현행 7,000ms 구성(30% 마진) (b) 마진 확대(timeout 하향) (c) 외부 RTT(I-4/I-13)의 명시적 예산화
   - 판정: KEEP (a) — LOCK-VR-12 ≤10s 내 30% 마진의 예산 배분 선택이며 safety_margin 0.90이 별도 적용됨(05 benchmark §9.2 'Phase 3 실측 후 조정 가능' 명시). 마진 적정성은 실측 후 튜닝 영역.

> notes: 전수 처리: clc 77건 + tight 47건(clc 부분집합, 신규 0) + GPT 15건. 카운트 20 vs 원판정 18(+2) 사유: (1) 명시적 이연 GAP 4건(T8-031/VRE-AUDIT-002/008/009·013 — 'Phase 1 확정 필요'로 문서화된 미결정 항목)은 '이루어진 설계선택'이 아니므로 비등재 — 원판정이 이 중 일부를 주관으로 셌다면 차이 발생. (2) confidence_thresholds.md의 REVIEW 병행(T8-008계열)과 FAIL 대체(VRE-AUDIT-006)를 별개 정책 2건으로 분리 — 원판정이 1건 합산했을 가능성. (3) GPT 소스 비중 불확실. 강제 짜맞춤은 하지 않음. 제외 내역: [mf_in 21건 동일/중복] T8-067·T8-117(i3/i19 max_attempts 의미론 중복), T8-102(i20 페널티 모델 중복), T5-243(i5 think/reason 중복), VRE-AUDIT-015(i5 동일), GAP-T8-025(등재 #2 REVIEW 병행 정책의 plan측 중복 — plan L1717 실측 확인됨). [오탐/반박] T8-001·013(코드 표기 해석), T8-065·2

### 3-7_Developer-Tools-API-SDK (19건)

1. **[KEEP]** `docs/sot 2/3-7_Developer-Tools-API-SDK/01_coding-engine/autonomous_coding.md`:231-244 — 반복 루프에서 커버리지 미달을 먼저 보강(augment_plan_with_tests)하고 테스트 실패는 다음 iteration에서 처리하는 순차 우선순위 전략
   - 선택지: (a) 현행: 커버리지 우선 순차 처리 (b) 커버리지+실패 동시 보강 (c) 실패 우선 처리
   - 판정: KEEP 현행 (a) — 정본 LOCK-DT-10은 80% 임계값만 규정하고 처리 순서는 미규정이며, max_iterations 루프 내 순차 수렴은 합리적 알고리즘 선택
2. **[KEEP]** `docs/sot 2/3-7_Developer-Tools-API-SDK/01_coding-engine/code_review_ai.md`:69 (+autonomous_coding.md:126) — 모듈별 severity 어휘 체계 분리 — ReviewComment는 critical/warning/info, ReviewFinding은 info/warning/error
   - 선택지: (a) 현행: 모듈별 독립 enum (b) 도메인 공통 severity enum 통일
   - 판정: KEEP 현행 (a) — 각 스키마 내부 일관적이고 autonomous_coding L249의 'error' 필터는 자기 스키마(ReviewFinding) 기준으로 정합(통합 버그 주장 T8-016은 refuted). 정본 위반 없음; 향후 통합 시 매핑 1줄 추가가 저비용 개선안
3. **[KEEP]** `docs/sot 2/3-7_Developer-Tools-API-SDK/01_coding-engine/dev_node_architecture.md`:306 (+87) — E_CONTEXT_TOO_LARGE 복구 시 컨텍스트 축소 타깃을 4096 토큰으로 설정(기본 max_context_tokens 8192의 절반)
   - 선택지: (a) 현행: 절반(4096)으로 축소 (b) 비율 기반 동적 축소 (c) 8192 유지+우선순위 삭제만
   - 판정: KEEP 현행 (a) — 축소 타깃이 기본값보다 작은 것은 복구 동작의 목적상 당연하며 4096은 LOCK 미규정 설계값. '모순' 주장은 해석 오류
4. **[KEEP]** `docs/sot 2/3-7_Developer-Tools-API-SDK/01_coding-engine/container_docker.md`:99-101 — SECURITY_SCAN의 스캔 대상을 빌드된 이미지가 아닌 Dockerfile 텍스트(빌드 전 정적 분석)로 선택
   - 선택지: (a) 현행: Dockerfile 정적 스캔(trivy config/hadolint류) (b) 빌드 후 이미지 CVE 스캔 (c) 양자 병행
   - 판정: KEEP 현행 (a) — trivy config 등 Dockerfile 대상 misconfig 스캔은 실존 기법으로 스키마 불부합이 아니며, 스캔 단계(빌드 전 vs 후) 선택은 정본 미규정 설계 재량. 이미지 CVE 스캔은 V2 확장 옵션
5. **[KEEP]** `docs/sot 2/3-7_Developer-Tools-API-SDK/03_refactoring/ast_pipeline.md`:899-905 — 언어별 타입 호환성 체커 선택(§E.7 표: mypy/tsc/cargo check/go vet/javac -Xlint:all -d /dev/null)
   - 선택지: (a) 현행: 단일 파일 컴파일러 직접 호출 (b) 빌드 시스템 통합 검사 (c) LSP 기반 진단
   - 판정: KEEP 현행 (a) — 체커 도구 선택은 알고리즘 설계 재량이고 LOCK-DT-06 per-check 30s 정합(L897). /dev/null의 Windows 이식성은 구현 단계 치환(NUL) 사항으로 정본 모순 아님
6. **[KEEP]** `docs/sot 2/3-7_Developer-Tools-API-SDK/03_refactoring/safe_transform_rules.md`:278-280 (+324) — 롤백 실패 시 재시도/무결성 재검증 없이 즉시 L3 긴급 에스컬레이션으로 위임하는 폴백 전략(동시 편집 안전은 잠금 대신 E_INTEGRITY 해시 검사로 담보)
   - 선택지: (a) 현행: 1회 시도 후 L3 에스컬레이션 + 해시 기반 무결성 (b) bounded retry 후 에스컬레이션 (c) 파일 잠금 추가
   - 판정: KEEP 현행 (a) — D4(L324) 'E_ROLLBACK_FAIL → L3 긴급'이 본문 정본으로 명시된 일관 전략이며, 정책표 L332 '무결성 우선'이 동시 편집을 해시로 커버. 정본 무모순
7. **[KEEP]** `docs/sot 2/3-7_Developer-Tools-API-SDK/03_refactoring/safe_transform_rules.md`:181-189 (+304,322,334) — 커버리지 미달 처리를 status='rejected'+approval_required=True 단일 표현으로 통합(별도 'warning' 상태나 ValidationLevel별 명시 분기 없음)
   - 선택지: (a) 현행: rejected+approval_required 조합 표현 (b) 별도 pending_approval/warning 상태 추가 (c) ValidationLevel별 명시 분기(STRICT=reject, NORMAL=warn)
   - 판정: KEEP 현행 (a) — LOCK-DT-10은 80% 임계값만 규정. D4 L322 '경고+승인요청'은 approval_required=True가 표현하고 있어 모순이 아닌 표현형 선택(clc verify=refuted와 정합). 레벨별 분기는 V2 개선 옵션
8. **[KEEP]** `docs/sot 2/3-7_Developer-Tools-API-SDK/04_test-generation/edge_case_detection.md`:199-204 (+211) — 함수당 상한(max_cases_per_function) 적용 시 카테고리 삽입 순서로 절단하고 전역 단계(L211)에서만 priority 정렬하는 캡 정책
   - 선택지: (a) 현행: 함수 내 삽입순 절단 + 전역 priority sort (b) 함수 내 priority sort 후 절단 (c) 소스별 쿼터 보장
   - 판정: KEEP 현행 (a) — 캡 값과 절단 전략은 정본 미규정 설계값이며 request.categories 나열 순서가 설계자의 보존 우선순위로 기능. 함수 내 sort 1줄 추가는 저비용 개선 옵션
9. **[KEEP]** `docs/sot 2/3-7_Developer-Tools-API-SDK/05_plugin-sdk/hook_system.md`:613-624 — 훅 재시도(retry_on_fail)를 asyncio.TimeoutError에 한정하고 일반 Exception은 로그 후 skip하는 재시도 범위 정책
   - 선택지: (a) 현행: timeout만 재시도 (b) 모든 예외 1회 재시도 (c) 예외 유형별 재시도 화이트리스트
   - 판정: KEEP 현행 (a) — §E.0 #5 '재시도 1회 per 훅, 실패 시 skip' 문언은 범위를 특정하지 않아 해석 재량이며, 결정적 오류(코드 버그)의 재시도는 무의미해 timeout 한정이 오히려 합리적. 정본 무모순
10. **[KEEP]** `docs/sot 2/3-7_Developer-Tools-API-SDK/05_plugin-sdk/command_palette.md`:272-273 — Phase1 네이티브(코어 등록) 커맨드 핸들러를 격리 없이 코어 프로세스 내 직접 호출(cmd.handler(**request.args))하는 신뢰경계 구분
   - 선택지: (a) 현행: 네이티브=코어 신뢰 직접 호출, 플러그인=WASM 격리 (b) 전 핸들러 일괄 샌드박스 경유 (c) 인자 스키마 검증 계층 추가
   - 판정: KEEP 현행 (a) — LOCK-DT-05의 WASM 격리 대상은 플러그인 코드이며 코어 자체 등록 핸들러는 신뢰 경계 내부라는 아키텍처 구분은 설계 재량. 정본 위반 없음
11. **[KEEP]** `docs/sot 2/3-7_Developer-Tools-API-SDK/06_vscode-extension/lsp_integration.md`:154-160 (+415,490) — completion에 2,000ms(p95 UX SLA 소프트 타깃)와 30,000ms(LOCK-DT-06 하드 가드) 이중 계층 타임아웃 적용
   - 선택지: (a) 현행: 소프트 2s + 하드 30s 계층 (b) 단일 2s 강제 취소 (c) 단일 30s
   - 판정: KEEP 현행 (a) — §7.1 표(L415)가 두 값을 한 행에 병기하고 §8(L490)이 '≤2,000ms, LOCK-DT-06 하위, UX 요구'로 계층 관계를 명시한 의도적 설계. 모순이 아닌 SLA 임계값 선택
12. **[KEEP]** `docs/sot 2/3-7_Developer-Tools-API-SDK/06_vscode-extension/lsp_integration.md`:166-171 — LSP 서버 재시작 backoff에 jitter 없이 순수 exp backoff(1000*2^n, MAX_RESTART 회)만 사용
   - 선택지: (a) 현행: 결정적 exp backoff (b) exp backoff + full jitter (c) 고정 간격 재시도
   - 판정: KEEP 현행 (a) — 로컬 단일 클라이언트가 자기 LSP 프로세스를 재시작하는 맥락이라 thundering herd 전제가 약하고, jitter 유무는 정본 미규정 백오프 전략 선택. 서버 공유 배포 시 jitter 추가 검토
13. **[KEEP]** `docs/sot 2/3-7_Developer-Tools-API-SDK/06_vscode-extension/feedback_system.md`:172-179 — 피드백 익명화 수준을 무salt SHA-256 해시 + PII 마스킹 + 로컬 우선 저장 + 옵트인 전송 조합(가명화)으로 설정
   - 선택지: (a) 현행: SHA-256 가명화+옵트인 (b) salt/pepper 추가 keyed-hash (c) user_id 완전 미수집
   - 판정: KEEP 현행 (a) — 익명화 강도는 정본 미규정 프라이버시 정책 선택이며 로컬 저장+옵트인 전송이 위험을 이중 완화. 텔레메트리 V2에서 서버측 pepper 추가가 자연스러운 강화 경로
14. **[KEEP]** `docs/sot 2/3-7_Developer-Tools-API-SDK/06_vscode-extension/onboarding_wizard.md`:216 — NPS 설문 트리거 임계값을 count_completed >= 3 (3단계 이상 완료)으로 설정
   - 선택지: (a) 현행: 완료 3단계 이상 (b) 전 단계 완료 시만 (c) 완료 수 무관 시간 기반
   - 판정: KEEP 현행 (a) — UX 정책 임계값으로 정본 미규정. 전 단계 스킵(완료 0) 시 NPS 미발화는 L216 식에서 명확히 도출되어 T10과도 무모순
15. **[KEEP]** `docs/sot 2/3-7_Developer-Tools-API-SDK/07_marketplace/webhook_events.md`:344-346 — 엔드포인트 에스컬레이션 사유 delivery_failed_5x — 단일 이벤트의 4 attempt와 별개로 '연속 실패 delivery 건수' 5회를 임계값으로 선택
   - 선택지: (a) 현행: 연속 실패 delivery 5건 (b) 단일 이벤트 4 attempt 소진 즉시 (c) 시간창 기반 실패율
   - 판정: KEEP 현행 (a) — delivery(이벤트 단위 배달) 5건과 attempt(배달 내 재시도) 4회는 다른 단위로 상호 모순이 아니며, 업계 표준(연속 N회 실패 시 endpoint disable) 패턴의 임계값 선택. 본문에 단위 주석 1줄 추가가 개선 옵션
16. **[KEEP]** `docs/sot 2/3-7_Developer-Tools-API-SDK/07_marketplace/vadd_marketplace.md`:91, 117 — 플러그인 격리 검증 한도를 'WASM 256MB/30s'로 구체화 — LOCK-DT-05('WASM 격리, 선언된 권한만 허용')에 수치를 specialization으로 부가
   - 선택지: (a) 현행: 256MB/30s base 계승 명기 (b) 수치를 별도 LOCK으로 승격 (c) 수치 제거하고 LOCK verbatim만
   - 판정: KEEP 현행 (a) — LOCK-DT-05는 수치를 규정하지 않아 위반이 아니고, 30s는 LOCK-DT-06(30초)과 정합하며 256MB는 설계값. L117이 'specialization (base 계승)'으로 출처 성격을 이미 표기
17. **[KEEP]** `docs/sot 2/3-7_Developer-Tools-API-SDK/07_marketplace/rest_api.md`:589, 604 — V1 권한 모델을 엔드포인트별 매트릭스 없이 read/write/admin 3계층 scope로 단순화
   - 선택지: (a) 현행: 키/토큰 단위 3-scope (b) 엔드포인트별 RBAC/scope 매트릭스 (c) 리소스 그룹별 중간 granularity
   - 판정: KEEP 현행 (a) — scope granularity는 정본 미규정 권한 모델 선택이고 §5.1~5.3에 일관 적용. 민감 엔드포인트별 매트릭스는 V2(JWT)/V3(OAuth) 단계의 자연스러운 강화 경로
18. **[KEEP]** `docs/sot 2/3-7_Developer-Tools-API-SDK/07_marketplace/rest_api.md`:261-262, 615 — /api/v1/health를 인증 불필요·rate limit 예외 공개 엔드포인트로 설정
   - 선택지: (a) 현행: 공개·무제한 (b) IP/소스 스로틀 추가 (c) LB 내부 전용 path 분리+최소 응답
   - 판정: KEEP 현행 (a) — L262 'LB 30초 무응답 시 제거' 운영 요구가 명시된 의도적 선택이고 LOCK-DT-08은 '기본 quota'만 규정하며 L615가 엔드포인트별 예외를 명시 허용. 정본 무모순
19. **[KEEP]** `docs/sot 2/3-7_Developer-Tools-API-SDK/01_coding-engine/cloud_iac.md`:99 — IaC apply 타임아웃을 30000ms로 설정하되 'apply 단일 step 상한'(LOCK-DT-06 계승)으로 범위 한정
   - 선택지: (a) 현행: per-step 30s (LOCK-DT-06 계승) (b) async job 상태머신+provider별 타임아웃 (c) 전체 apply 단일 상한
   - 판정: KEEP 현행 (a) — L99 주석이 '단일 step 상한'으로 명시해 장기 provisioning은 step 분할로 수용 가능하며 30s는 DESIGN LOCK(LOCK-DT-06) 정합 값. GPT 자체도 is_confident=false. async job화는 V2 옵션

> notes: 재도출 19/19 앵커 일치(짜맞춤 아님 — 독립 분류 후 경계 5건을 원칙적 기준으로 객관/표기 측에 귀속한 결과). 전건 디스크 실측(file:line) 확인, 전건 KEEP(정본 모순 0건, CHANGE 0건). 제외 내역: (1) mf_in 객관 확정 27+미확정 2 및 동일 family 중복(LOCK-DT-04 4단계: T6-084/T6-085/T6-098/T6-355/DT-001, 22리소스: T8-339/DT-022, condition lambda: DT-002 등). (2) verify=refuted 오탐: T8-005, T8-016, T8-116, T8-117, T6-120, T8-143, T8-178, T8-196, T8-246, T8-308, T6-312. (3) 표기/오타: T5-067(알람/알림), T8-254/T8-303(E1~E10 9요소), T6-108(인용 행번호), T6-378(82 vs 56 헤더). (4) 인용 미검증성: T6-014, T6-068. (5) 객관 성격(주관 아님)으로 잔류한 비-mf_in finding: T8-001/T8-002(자체 안전장치 주장 vs 미구현), T8-029, T8-044, T8-058, 

### 4-1_Rust-Tauri-Infrastructure (19건)

1. **[KEEP]** `01_ipc-commands/agent_commands.md`:120-126 (실측: SEC-1~3/6 '전수 7/7') — plan §A.4가 SEC-3을 Safety 19개, SEC-6을 외부 API 커맨드로 한정함에도 Agent 카테고리 전 커맨드(7/7)에 RBAC·레이트리밋을 확대 적용한 defense-in-depth 선택
   - 선택지: (a) plan §A.4 최소 범위만 적용 (b) 현행 전수 적용 superset 유지
   - 판정: KEEP 전수 적용 — PLAN 3.0(§A.4)은 최소 적용 대상 정의이며 보안 superset 확대는 정본 위반이 아님(plan L1806 SEC-1 '모든 IPC 커맨드' 패턴과 일관). §V2.2에 'plan 최소범위 대비 확장' 명시만 권장
2. **[🔧CHANGE]** `01_ipc-commands/memory_commands.md`:124, 220 (실측: SEC-4 '✅ 특화 / 경로 인자 커맨드' + TS-SEC-MEM-2 MemoryQuery.filters.path) — 메모리 커맨드에 SEC-4 경로탐색 방지를 선제(방어적) 적용하기로 한 선택 — 단 TS가 모델 정본에 없는 filters.path 필드를 인용
   - 선택지: (a) plan §A.4대로 SEC-4를 File 6개 커맨드 한정·memory N/A (b) D6 스키마 확정 대비 선제 적용 유지 + TS를 모델 정합으로 교정
   - 판정: SEC-4 선제 특화 자체는 설계 재량으로 유지하되, memory_models.md §3.4 MemoryQuery 정본(L202-213: text/top_k/level_filter/tag_filter/min_importance/time_range — path 필드 없음)과 plan §A.4 L1809(SEC-4=File 6개)에 모순되는 TS-SEC-MEM-2의 filters.path 인용을 D6 [PRE-1 대조] 보류 마커로 교정 — 스키마 정본 우선
3. **[🔧CHANGE]** `01_ipc-commands/health_commands.md`:215 (실측: TS-SEC-HLT-1 anon 예외) vs 22-24, 126 (RBAC health:read 전수 3/3) — health_check를 무인증(anon) liveness 엔드포인트로 허용할지 vs V1 RBAC 열대로 health:read를 요구할지의 정책 선택
   - 선택지: (a) anon 예외 + 민감정보 redact (b) V1 RBAC 열 정본대로 health:read 전수 요구
   - 판정: V1 §1 RBAC 열이 본 파일 선언 정본(L127 'V1 §1 표의 RBAC 열 정본 사용')이고 §V2.2가 SEC-3 '전수 3/3'을 확약하므로, TS-SEC-HLT-1의 anon 예외는 자기 정본과 모순 — health:read 유지로 TS 교정(anon 채택 시 V1 표 갱신+LOCK 절차 필요)
4. **[KEEP]** `01_ipc-commands/file_commands.md`:70-74, 146-149 (실측: 단일 sandbox root + symlink read 전용/write·upload 거부) — file_write와 file_upload가 동일 sandbox root($APPDATA/vamos/sandbox/)와 동일 canonicalize+whitelist 검증을 공유하는 단일 검증 경로 선택
   - 선택지: (a) upload 전용 별도 검증 경로/격리 디렉터리 신설 (b) 단일 sandbox + 연산별 symlink 차등(현행)
   - 판정: KEEP — §V2.4가 이미 연산별 차등(symlink: read 허용 O_NOFOLLOW / write·upload 거부, 상대경로 거부, 시스템 경로 block-list)을 명세하므로 정본 무모순. upload 별도 경로 분리는 선택적 강화일 뿐
5. **[KEEP]** `01_ipc-commands/mcp_commands.md`:122 (실측: 'SEC-6 레이트 리밋: Safety 1000 req/s') — MCP 3개 커맨드가 속한 Safety 카테고리 레이트리밋을 1000 req/s로 높게 잡은 임계값 선택(conversation 50 req/s 대비 20배)
   - 선택지: (a) 1000 req/s 유지 (b) MCP 외부 서버 보호 위해 하향(예: 50~100 req/s) (c) 카테고리 대신 커맨드군별 세분화
   - 판정: 값 자체는 D4 RateLimitConfig 연동 임계값으로 설계 재량 — 단 mf_in i0(50 vs 1000 모순)의 객관 교정에서 D4 정본 단일값 확정 시 그 값을 채택. plan §A.4는 SEC-6 적용 대상만 정의하고 수치를 정하지 않으므로 정본 모순 없음
6. **[KEEP]** `03_python-bridge/method_catalog.md`:67, 318-325 (실측: '1:1 start_agent (agent_type = node_type 해석)' + LanggraphNodeDispatchParams{node_id, parent_run_id}) — langgraph.node.dispatch를 상세명세 §C #7 start_agent와 1:1로 매핑하되 agent_type→node_id 재해석 + parent_run_id 확장 필드를 추가한 인터페이스 적응 선택
   - 선택지: (a) 상세명세 시그니처 그대로 복제 (b) 해석·확장을 명시한 적응형 DEFINED-HERE(현행)
   - 판정: KEEP — §2.2 매핑 표가 '(agent_type = node_type 해석)'으로 적응을 명시 문서화했고 LOCK-RT-03은 메서드명만 동결(이름 불변), 상세명세 §C는 참조용 스키마(CFL-RT-002 RESOLVED)이므로 정본 위반 없음. '1:1' 라벨은 semantic match 의미
7. **[KEEP]** `03_python-bridge/method_catalog.md`:536-541 (실측: McpBridgeInitParams.auth Bearer/ApiKey/OAuth — 파일 내 redact/마스킹 규칙 grep 0건) — auth 자격증명에 대한 명시적 로그 redaction 규칙 대신 params 비로깅(params_size_bytes만 기록) 패턴으로 충분하다고 본 로깅 정책 선택
   - 선택지: (a) 'auth/server_uri 비로깅' 명시 규칙 추가 (b) 현행 params_size_bytes 패턴 의존
   - 판정: KEEP — 검증 가능한 정본 위반 없음(spawn_protocol L196이 'API KEY는 env가 아닌 mcp.bridge.init.params.credentials로 전달'을 이미 명세, 로그 카탈로그는 params 원문 미기록). 명시적 redaction 규칙 추가는 보안 강화 권장 사항
8. **[KEEP]** `05_process-management/healthcheck.md`:297-299 (실측: §5.4 공정성 보장 — HC와 일반 RPC Semaphore(50) 공유 + 3s 취득 timeout Phase 2 유보) — HC RPC에 전용 lane을 두지 않고 일반 RPC와 Semaphore(50)를 공유시키며, 포화 시 HC 실패를 시스템 비가용 신호로 간주하는 아키텍처 선택
   - 선택지: (a) HC 전용 예약 lane/우선순위 semaphore (b) 공유 + 포화=비가용 신호 해석(현행, Phase 2에 3s timeout 완화 유보)
   - 판정: KEEP — §5.4가 트레이드오프('부하 포화 시에도 HC 탐지 기능 유지')와 Phase 2 완화 계획을 명시 문서화한 의도적 선택이며 LOCK-RT-12(15s/5s/3회)와 무모순. Phase 2 유보 항목 이행만 추적
9. **[KEEP]** `04_build-signing/tauri_build_config.md`:188-190, 199 (실측: deb.depends 블록 잔존 + targets [nsis,dmg,appimage] 'DEB→AppImage 로 정제') — bundle.targets에서 deb를 제외(DEB→AppImage 정제)하면서 deb.depends 설정 블록을 향후 재활성 대비 placeholder로 잔존시킨 선택
   - 선택지: (a) deb 블록 삭제(완전 정리) (b) inert placeholder로 잔존(현행)
   - 판정: KEEP — targets 배열이 빌드 정본이며 Tauri는 target 미포함 시 deb 블록을 무시(무해한 dead config). 정본 모순 없음. 정리 차원 삭제 또는 '비활성 placeholder' 주석 추가는 선택사항
10. **[KEEP]** `04_build-signing/tauri_build_config.md`:45 (실측: S7F-017 verbatim 'Health Check 30초 간격') vs healthcheck.md 49 (LOCK-RT-12 15초 정본) — SOT(STEP7-F) 기준 HC 30초 대신 15초 간격을 LOCK-RT-12로 동결한 운영 파라미터 선택
   - 선택지: (a) SOT 30s 복원 (b) LOCK-RT-12 15s 유지(현행, Phase 5 동결)
   - 판정: KEEP 15s — DESIGN LOCK(LOCK-RT-12, 상세명세 §D-2 DEFINED-HERE '15초마다 health_check RPC 호출' 근거 명시)이 SOT 본문 인용보다 우선. §1.3 표는 SOT verbatim 인용 테이블이라 보존이 목적이고, 같은 파일 L201이 'LOCK-RT-12 HC 15초 간격 대상'으로 현행 정본을 이미 명시 — 충돌 미해소 주장은 약함
11. **[KEEP]** `04_build-signing/tauri_build_config.md`:42 (실측: S7F-011 verbatim 'sidecar Node.js') vs 200 ('sidecar Node.js 와 달리 VAMOS 4-1 은 Python sidecar') — SOT가 명기한 Node.js sidecar 대신 Python sidecar(LOCK-RT-11 JSON-RPC 2.0 over stdio)를 채택한 아키텍처 선택
   - 선택지: (a) SOT대로 Node.js sidecar (b) Python sidecar(현행, 도메인 전체 일관)
   - 판정: KEEP Python sidecar — DESIGN LOCK(LOCK-RT-11)과 도메인 전체(externalBin binaries/python, spawn/HC/restart 전부)가 Python 전제로 동결됐고, L200 근거 표가 SOT 대비 편차를 명시 문서화함. SOT 인용표(§1.3 verbatim)는 보존 대상이므로 별도 amendment flag는 선택사항
12. **[KEEP]** `RUST_TAURI_INFRASTRUCTURE_상세명세.md`:412-425 (실측: F-1 다이어그램 — Restarting→Dead '(5회 실패)' 단일 경로) — F-1 상태 머신 다이어그램을 요약 추상화 수준(Dead 전이 단일 표기)으로 유지하고 조건별 임계(OOM 3회/HC 3회/비정상 5회)는 restart_policy.md에 위임한 문서화 선택
   - 선택지: (a) F-1에 조건별 Dead 전이 임계 전부 반영 (b) F-1=요약, restart_policy=운영 상세 정본(현행)
   - 판정: KEEP — restart_policy.md §7(OOM 3회→Suspended 등)이 조건별 임계의 운영 정본이며, F-1은 개요 다이어그램으로 추상화 수준 선택의 문제. 두 문서 간 값 자체 모순은 없음(5회=비정상 경로 최대치)
13. **[KEEP]** `05_process-management/restart_policy.md`:369-371, 621 (실측: vamos:bridge:unsuspend/restart + bridge:admin scope) vs AUTHORITY_CHAIN.md 61-62 (LOCK-RT-01 72개) — operator 전용 bridge 운영 커맨드(unsuspend/restart)를 LOCK-RT-01 72개 사용자 IPC 카탈로그 밖의 별도 네임스페이스로 둔 선택
   - 선택지: (a) LOCK-RT-01 카탈로그에 정식 추가(72→74) (b) 비-LOCK 운영 커맨드로 별도 유지(현행) (c) 기존 system:admin 커맨드로 재매핑
   - 판정: (b) 유지 — LOCK-RT-01은 72개 이름의 동결이지 추가 운영 커맨드 금지가 아니며, L371이 'T1-1 secure_commands 참조 — 경계'로 경계를 명시. 단 bridge:admin scope 정의 위치를 AUTHORITY_CHAIN에 비-LOCK 운영 커맨드로 등재 권고(LOCK 재정의 0 유지)
14. **[KEEP]** `03_python-bridge/method_catalog.md`:37, 54-58, 65-76 (실측: LOCK-RT-04 '신규 struct 선언 금지' vs §2.1 원칙 3 GAP→DEFINED-HERE 신규 스키마) — Part2 13 메서드 중 상세명세 1:1 부재 GAP 6건에 대해 bridge 전용 DTO를 본 파일 DEFINED-HERE로 신규 정의하기로 한 경계 설정 선택
   - 선택지: (a) 신규 DTO를 02_serde-models로 이동 + LOCK-RT-04 카운트 갱신 (b) bridge DTO를 카탈로그 DEFINED-HERE로 유지(현행)
   - 판정: KEEP — §2.1 해소 원칙 3이 GAP 시 '본 파일에서 신규 스키마를 DEFINED-HERE으로 정의(§9.1 5순위 상세명세와 동급 정본 지위)'를 명시적 메커니즘으로 확립했고, LOCK-RT-04의 금지는 Serde 25 모델 영역(T1-2 소유) 한정으로 읽는 것이 내부 정합적. 경계 명시 한 줄 보강만 권장
15. **[KEEP]** `01_ipc-commands/message_framing.md`:118-119, 133 (실측: L118 '프레이밍 정본 = 10 MB'로 기교정됨, L133 대용량 우회 전략) — IPC payload 한도 초과 대용량 전송 전략 — 파일 경로 기반 우회 vs 사전 분할(file_chunk류 커맨드, LOCK-RT-01 미등재) 중 무엇을 정본 전략으로 둘지의 선택
   - 선택지: (a) 파일 경로 기반 우회 단일 전략 (b) chunk 커맨드 신설(LOCK-RT-01 확장 필요) (c) 병기(현행 L133)
   - 판정: (a) 파일 경로 기반 우회를 정본 전략으로 — L118이 이미 '바이너리 대용량은 file 커맨드 또는 파일 경로 참조로 우회'를 명시하고 file_chunk는 LOCK-RT-01 72개에 없으므로 예시 문구는 비실재 커맨드 인용. 한도 수치(8 MiB 잔존 L133/L180/L217)는 mf_in i2 객관교정 영역으로 본 항목에서 제외
16. **[KEEP]** `RUST_TAURI_INFRASTRUCTURE_구조화_종합계획서.md`:1780-1787, 1799 (실측: §A.3 SLA 6 카테고리 P99 표 + '모니터링 관점 재구성' 주석) — 카테고리 단위 P99 SLA(System/Health ≤30ms 등)에 장기 실행 커맨드(apply_update 60s, consolidate 60s, health_check 5s 타임아웃)를 같은 범주로 묶을지의 SLA 범주화 granularity 선택
   - 선택지: (a) 커맨드 class별 SLA 분리(장기 작업 async job SLA) (b) 카테고리 P99 단일 표 유지(현행)
   - 판정: KEEP 표 자체(STEP_B T2-3 정본 확정·ISS-08 해소, PLAN 정본) — 단 L1799가 '모니터링 관점 재구성·LOCK 확장 0건'으로 성격을 한정하므로, 장기 실행 커맨드를 P99 산정 제외 클래스로 명시하는 각주 보강 권고. 정본 모순 아님(SLA와 per-command 타임아웃은 다른 축)
17. **[KEEP]** `05_process-management/spawn_protocol.md`:117-135, 188-196 (실측: config>$VAMOS_PYTHON>which python 3단 우선순위 + 존재/실행권한 검증 + env_clear whitelist) — Python 바이너리 해석을 3단 폴백(설정→환경변수→PATH)으로 두고 신뢰성 검증을 존재/실행권한 수준으로 한정한 선택(해시/서명 검증 미채택)
   - 선택지: (a) production은 번들/설정 경로만 허용 + hash/signature 검증 (b) 3단 폴백 + 기본 검증(현행)
   - 판정: KEEP — 정본(상세명세 §D-1 Step 1 'venv 경로 확인')과 정합하고, tauri_build_config externalBin(binaries/python 번들)이 production 기본 경로여서 PATH 폴백은 개발 편의 폴백. env_clear whitelist(L195)로 LD_PRELOAD류 교란 차단 근거도 명시. 해시 검증 추가는 선택적 강화
18. **[KEEP]** `RUST_TAURI_INFRASTRUCTURE_구조화_종합계획서.md`:1812 (실측: SEC-7 'IPC 메시지 무결성') vs system_commands.md 122 ('✅ 특화 민감 쓰기'), tool_commands.md 123 / file_commands.md 128 (N/A) — SEC-7 HMAC 서명의 적용 범위를 전 IPC 메시지가 아닌 민감 쓰기 커맨드(settings/system/mcp)로 한정한 커버리지 선택
   - 선택지: (a) 모든 mutating/admin IPC로 확장 (b) 민감 커맨드 한정(현행) + 제외 근거 명시
   - 판정: (b) 유지 — plan §A.4의 '적용 대상' 문구가 커맨드를 열거하지 않아 모순 단정 불가하고, message_framing TS-SEC-FRM-10이 '민감 커맨드 settings/system/mcp'로 한정 적용을 일관 명세. plan §A.4 문구를 '민감 쓰기 커맨드'로 명확화하는 보강 권고
19. **[KEEP]** `INDEX.md`:8, 158 (실측: cross_domain_deps=[] + CFL-RT-009 OBSERVE_ONLY 비차단) vs CONFLICT_LOG.md 167-168 (잠정 매핑→V4 후 canonical 교체, RESOLVED-DEFERRED) — 6-12 Event-Logging V4 의존을 차단성 cross_domain_dep이 아닌 OBSERVE_ONLY 비차단 관찰로 분류하고 canonical 교체를 후속 태스크로 이연한 프로세스 선택
   - 선택지: (a) 6-12를 실제 의존으로 cross_domain_deps에 등재 (b) 자기완결 + 비차단 관찰 + RESOLVED-DEFERRED(현행)
   - 판정: KEEP — INDEX L8이 자기완결 선언에 'CFL-RT-009 6-12 V4 cross-handoff 관찰만, 비차단' 단서를 함께 명기해 두 기록이 이미 정합(모순 아닌 의도된 이연). 로컬 rt.py_bridge.* 네임스페이스가 LOCK-EL-03 48건과 충돌하지 않는 구조도 CONFLICT_LOG에 근거 명시

> notes: 원판정 앵커 19건과 정확히 일치(강제 짜맞춤 아님 — 독립 재도출 결과 19건 수렴). 분류 회계: 전체 고유 finding 약 52건(clc 39 + GPT 17, tight 29건은 clc 완전 부분집합으로 보조 확인용) 중 (1) mf_in 객관결함 25건과 동일/중복 26건 제외(T8-002/003/004/034/048/084/097/110/113/114/136/137/138/139/146/176/177, T6-185, RT-AUD-001/002/003/004/006/008/010/013/016 — T8-146은 i4와, RT-AUD-004는 i12와 중복), (2) verify=refuted 오탐 6건 제외(T8-040 세 한도는 각각 입력payload/export/title로 별개 대상, T8-059 deny_unknown_fields, T6-071 EventLog when, T8-096 janitor 수거 설계, T8-098 oneshot 묵살은 tolerated 설계, T8-122 CSP는 webview가 아닌 Rust 측 HTTP 호출이라 비차단), (3) 단순 표기 3건 제외(T8-005 'TS-SEC-FRM-1~74' 카운트 오기, T8

### 6-4_Memory-RAG-Storage (19건)

1. **[KEEP]** `docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\B3_memory_decay.md`:122-129 — Decay 감쇠 함수로 S7D-005 선형 대신 지수 반감기(half_life 30d) 모델 채택
   - 선택지: 선형 감쇠(S7D-005 원문) vs 지수 감쇠(에빙하우스 망각 곡선)
   - 판정: KEEP 지수 감쇠 — S7D-005는 REF(제안)이며 LOCK 아님. 문서가 L126-129에서 선택 근거와 'V2+ freshness_score에 선형 별도 사용'을 명시해 정본 무모순 (본문 자기 결정).
2. **[KEEP]** `docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\B3_memory_decay.md`:401, 607 — Decay 배치 인덱스를 (scope,memory_type,pinned,decay_score)로 설계하고 ORDER BY last_accessed_at 정렬 비용을 수용
   - 선택지: 인덱스에 last_accessed_at 추가(정렬 커버) vs 부분 인덱스 서브셋 + LIMIT 100 정렬 수용
   - 판정: KEEP — 부분 인덱스가 L2/B-3/pinned=0 서브셋만 스캔(L615 자인)하고 batch_size=100 LIMIT로 정렬 비용이 상수급. §9 L607의 O(log N) 표기는 본문 자기 주장으로 정본(RULE/PLAN/LOCK) 모순 아님.
3. **[KEEP]** `docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\B3_memory_decay.md`:237-242 — L2→L1 강등(옵션 B) 시 TTL 90일 적용하되 기산점(created_at vs 강등 시점) 리셋 정책 미규정
   - 선택지: 강등 시점 기준 TTL 재기산 vs created_at 기준 유지(즉시 만료 가능)
   - 판정: KEEP — V1 기본은 옵션 A(비활성화, L240)이고 옵션 B는 사용자 명시 선택+확인 필수(LOCK-MR-018 준용 L227)라 즉시 만료 리스크가 사용자 게이트 뒤에 있음. LOCK-MR-004(90일) 무모순. 강등 시점 재기산 명시 추가는 개선 권장 사항.
4. **[KEEP]** `docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\MemoryRecordSchema.md`:138-145 — QoD 컴포넌트를 DEC-014 4요소 대신 D6 3요소(freshness/reliability/completeness) 정본 채택, 'relevance+accuracy→reliability 통합' 해석
   - 선택지: D2.0-06 DEC-014 4요소 vs D6 SourceQoDSchema 3요소(DN-009 A 확정)
   - 판정: KEEP D6 3요소 — Schema SOT 명시 채택(L143)으로 해석 권한 내 결정. 단 L145가 예고한 CONFLICT_LOG '#007'은 실제 로그에서 GDPR 충돌이 점유 중(QoD 항목 미등재) — 신규 번호로 정식 등재 필요.
5. **[KEEP]** `docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\L1_project_memory_crud.md`:727-732 — LOCK-MR-004 '프로젝트 단위 30일 연장 가능'을 관리자 판단의 레코드 단위·최대 1회(90d→120d) 연장으로 해석
   - 선택지: 프로젝트 일괄 연장 vs 레코드 단위 연장 / 무제한 vs 1회 상한
   - 판정: KEEP — §4.3이 '설계 결정'으로 명시하고 근거(무한 연장은 L2 역할 침범) 제시. LOCK 문언이 단위·횟수를 규정하지 않아 보수적 해석은 LOCK 무모순. 해석 내용을 AUTHORITY_CHAIN에 결정 기록 권장.
6. **[KEEP]** `docs\sot 2\6-4_Memory-RAG-Storage\02_rag-pipeline\hybrid_search.md`:150, 158 — 초기 검색 Top-K=20 채택 (SOT D2.0-06 S7D-012의 top-10 대비 확대)
   - 선택지: top-10(S7D-012) vs Top-K=20(Part2 L2034, LOCK=N config 조정 가능)
   - 판정: KEEP Top-K=20 — 종합계획서 L96이 'Top-K=20 (Part2 L2034/L2038 LOCK)'으로 채택했고 PLAN > DESIGN 우선순위에서 정본 정합. 문서도 LOCK=N(조정 가능)을 명시해 회귀 여지 보존.
7. **[🔧CHANGE]** `docs\sot 2\6-4_Memory-RAG-Storage\02_rag-pipeline\hybrid_search.md`:728 vs 1052/1150 — 에러 코드 체계 운용 — α override를 WARNING 레벨로 처리하되 발화 코드 선택
   - 선택지: 코드가 HYB_WARN_001(미등재) 발화 vs §13 레지스트리 정의 HYB_ERR_007(ALPHA_OVERRIDE, WARNING)
   - 판정: WARNING 레벨 자체는 합리적 설계 선택이나, 발화 코드 HYB_WARN_001은 §13(L1052)·§16.2(L1150) 레지스트리에 미등재 — 본문 레지스트리가 코드 정본이므로 pseudocode를 HYB_ERR_007로 정합화 (정본 모순 → CHANGE).
8. **[KEEP]** `docs\sot 2\6-4_Memory-RAG-Storage\02_rag-pipeline\hybrid_search.md`:511-515 — Sparse를 독립 recall 경로가 아닌 Dense 보충 가중치(booster)로만 운용 — Sparse-only 후보는 threshold로 자동 배제
   - 선택지: Sparse booster(현행, α=0.7 Dense 우선) vs 진성 hybrid recall(Sparse-only fetch + 별도 threshold/RRF)
   - 판정: KEEP booster — §8.3이 '설계 의도'로 명시하고 LOCK-MR-008(α=0.7 Dense 가중)의 설계 철학과 정합. 키워드-only 회수가 필요해지면 V2에서 RRF 경로 보강이 자연스러운 진화 경로.
9. **[KEEP]** `docs\sot 2\6-4_Memory-RAG-Storage\02_rag-pipeline\json_graphrag.md`:1487-1503 — _atomic_write 백업을 단일 고정 .bak 슬롯(회전 없음) + tmpfile→rename 원자 쓰기로 설계
   - 선택지: 단일 .bak vs 회전 백업(N세대)/타임스탬프 백업
   - 판정: KEEP — V1 로컬 JSON 저장소에서 원자 쓰기(rename)가 1차 방어이고 .bak은 보조. 백업 보존 깊이는 정본 규정이 없는 운영 정책 선택. 회전 백업은 V2 개선 후보.
10. **[KEEP]** `docs\sot 2\6-4_Memory-RAG-Storage\03_vector-db\chroma_adapter.md`:229-237 — Matryoshka 256dim을 BGE-M3 1024dim의 앞 256차원 슬라이스(vec[:256]) + L2 재정규화로 생성
   - 선택지: prefix slice(현행 MRL 표준 사용법) vs MRL 전용 학습 모델/별도 256dim 인코더
   - 판정: KEEP — LOCK은 'Matryoshka 256dim 검색용'만 규정하고 축소 기법은 미규정. prefix slice + 재정규화는 구현 선택으로 정본 무모순. BGE-M3의 MRL 비학습 우려는 recall 회귀 벤치로 검증 권장.
11. **[KEEP]** `docs\sot 2\6-4_Memory-RAG-Storage\03_vector-db\chroma_adapter.md`:786-809 — 용량 상한을 프로젝트 단위(MAX_VECTORS_PER_PROJECT=450)로만 시행하고 전역 상한 미시행
   - 선택지: per-project 상한만(R-64-5) vs 전역 컬렉션 상한 병행
   - 판정: KEEP — R-64-5(D2.0-06 §4.1: 15문서×30청크=450/프로젝트)가 정본이며 per-project 시행이 정확히 정합. L798의 미사용 전체 카운트 변수는 정리 대상이나 정본 모순 아님.
12. **[KEEP]** `docs\sot 2\6-4_Memory-RAG-Storage\03_vector-db\chroma_adapter.md`:314-321, 375-394, 927 — 배치 upsert를 100건 순차 sub-batch + 사전검증(deny/용량/차원 선행) + 인프라 실패 시 부분 성공(VEC_ERR_010) 허용으로 설계
   - 선택지: 전체 원자성(보상 삭제 롤백) vs 사전검증 후 부분 성공 허용
   - 판정: KEEP — deny 검증이 Step 1(L314-315)로 모든 쓰기보다 선행하여 T-04 '배치 전체 거부'(L1022) 기대를 충족. VEC_ERR_010 부분 성공은 인프라 실패 한정으로 §12(L927)에 명시된 정합적 선택 (SQLite 단일 writer 근거 L381).
13. **[KEEP]** `docs\sot 2\6-4_Memory-RAG-Storage\04_memory-distillation\export_import.md`:230, 254 — L2 export에 '별도 승인 필요'를 부과 — LOCK-MR-016(L3 게이트)보다 보수적인 확장 적용
   - 선택지: L2 무승인 export(LOCK 문언 그대로) vs L2 조건부 승인(Core 지식 보호 강화)
   - 판정: KEEP — LOCK-MR-016은 L3 게이트이나 L2 승인 추가는 LOCK보다 엄격한 방향의 확장으로 정본 위반 아님. 근거 표기도 '간접'으로 명시(L230)해 직접 LOCK 인용으로 오인되지 않음.
14. **[KEEP]** `docs\sot 2\6-4_Memory-RAG-Storage\04_memory-distillation\export_import.md`:863-868 — 동시성 모델을 SQLite WAL + busy_timeout=5000 단일 writer + 배치 단위 롤백으로 설계 (export 중 read-snapshot 격리 수준 별도 미규정)
   - 선택지: 단일 writer 차단(현행 V1) vs 명시적 스냅샷 격리/export 락
   - 판정: KEEP — V1 로컬 단일 사용자 환경에서 WAL 단일 writer 차단(L868)으로 in-flight import와의 경합이 실질 차단됨. 스냅샷 일관성 명문화는 V2 멀티 writer 전환 시 보강 사항.
15. **[🔧CHANGE]** `docs\sot 2\6-4_Memory-RAG-Storage\04_memory-distillation\pii_masking.md`:203 vs 619-625 — CONFIDENTIAL 등급의 저장 범위 결정 (L1만 vs L0+L1)
   - 선택지: 표 §2.2(L203): 'L1만 (TTL 강제)' S7D-065 인용 vs 코드맵(L620): storage_allowed=["L0","L1"]
   - 판정: 표 §2.2의 'L1만'이 정본 — 정본 인용(S7D-065)이 명시된 본문 표 > 코드맵(스키마 레벨)이고, L620 인라인 주석 자체도 'L1만'이라 코드맵이 자기모순. L0 제거로 정합화 (정본 모순 → CHANGE).
16. **[🔧CHANGE]** `docs\sot 2\6-4_Memory-RAG-Storage\02_rag-pipeline\rag_6stage_pipeline.md`:1015 — B-3 Decay 결과의 벡터 처리 방식 (자동 삭제 vs 비활성화 태깅)
   - 선택지: P2-T-RAG-08 시나리오 'TTL 만료 벡터 → 자동 삭제' vs B3 §4.5(L232) 'LOCK-MR-005: 시간 기반 자동 삭제 금지, 모든 경로 DELETE 불포함' + §4.6 벡터 메타데이터 태깅
   - 판정: 비활성화 태깅이 정본 — DESIGN LOCK(LOCK-MR-005) > 본문 테스트 행. 검증 셀('Decay 후 검색 결과 미포함')은 이미 비활성화와 정합하므로 시나리오 문구만 교정 (정본 모순 → CHANGE).
17. **[KEEP]** `docs\sot 2\6-4_Memory-RAG-Storage\MEMORY_RAG_STORAGE_구조화_종합계획서.md`:544, 549-551 — top_k 기본값 이원화 — ABC search는 D2.0-06 원본 기본값 10 유지, 파이프라인 레벨은 config default_top_k=20 오버라이드
   - 선택지: ABC 기본값을 20으로 통일 vs 계층 분리(API=10 정본 정합 + 파이프라인=20)
   - 판정: KEEP 계층 분리 — L544가 '정합 처리'로 명시 설계했고 검증 L551이 'top_k=10 D2.0-06 §2.2-A 원본 1:1 정합 (R3: DESIGN > IMPL)'으로 통과 확인. config 미적용 리스크는 파이프라인 초기화 검증으로 커버 가능.
18. **[KEEP]** `docs\sot 2\6-4_Memory-RAG-Storage\MEMORY_RAG_STORAGE_구조화_종합계획서.md`:427 — source_refs→source_qod 참조를 물리 FK 없이 논리적 FK(애플리케이션 레벨 정합성)로 설계
   - 선택지: JSON 배열 + 논리 FK(현행) vs 정규화 교차 테이블 + 물리 FK + orphan sweep
   - 판정: KEEP — L427이 'SQLite JSON 배열이므로 물리적 FOREIGN KEY 미적용'을 명시 결정. SQLite에서 JSON 배열 멤버에 물리 FK는 불가하므로 기술 제약 내 합리적 선택. orphan 탐지 스윕은 GDPR erasure 연동 개선 후보(정본 무모순).
19. **[KEEP]** `docs\sot 2\6-4_Memory-RAG-Storage\MEMORY_RAG_STORAGE_구조화_종합계획서.md`:96-98 — α 기호 표기 규약 — 도메인 전체에서 α=Dense 가중치(0.7)로 통일 (D2.0-06 S7D-012의 α=BM25(0.3)와 반대 표기)
   - 선택지: D2.0-06 표기(α=BM25 0.3) vs Part2 L2034/L2038 표기(α=Dense 0.7, 현행)
   - 판정: KEEP α=Dense — L98이 '표기 통일: 본 도메인에서 α는 Dense 가중치(0.7), BM25=1-α' + GLOSSARY_CROSS_DOMAIN.md 참조로 명시 선언. PLAN > DESIGN 우선순위 정합이며 수식 자체(0.7·dense+0.3·bm25)는 양 표기에서 수치 동치라 실질 모순 없음.

> notes: 재도출 결과 19건 — 원판정 앵커 19와 자연 일치(짜맞춤 없음). 풀: clc 78 + GPT 15 = 93건(tight는 clc 부분집합). 분해: (1) mf_in 객관결함 39건이 clc 38개 finding + GPT 10개 finding을 커버(중복 통합 포함: T8-180/190, T8-218/229 등). (2) verify=refuted 오탐 17건(T8-020/036/037/057/070/076/111/117/118/187/189, T6-251/253/295, T8-255/265/294) + 추가 디스크 반박 1건: T8-256은 AUTHORITY_CHAIN.md가 D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\AUTHORITY_CHAIN.md에 실존하여 오탐 확정. (3) 단순 표기/경미 문서누락으로 주관 제외 5건: T5-014(비활성화 vs soft-delete 라벨), T5-094(hybrid_score/final_score 동의어), T5-184(memory_id docstring 잔재), T6-071(인용 출처 혼용), T8-228(클래스 계보도에 invalidate_by_drift 누락 — 문서 

### 3-5_Education-Learning (19건)

1. **[KEEP]** `docs\sot 2\3-5_Education-Learning\01_adaptive-learning\difficulty_adjustment.md`:137-156 — 연속패턴 보정의 비대칭 임계(연속 3정답 +0.2 / 연속 2오답 -0.2)와 보정 크기·누적 허용(Phase3 ±0.3 + Phase4 ±0.2 = 최대 ±0.5)을 채택한 튜닝 값 선택.
   - 선택지: (a) 현행 비대칭(오답에 더 민감, 3/-2) (b) 대칭 임계(3/-3 또는 2/-2) (c) 보정 크기 축소(±0.1)로 누적 여유 확보
   - 판정: KEEP — LOCK-ED-02는 목표 정답률 70-85%만 고정하고 보정 임계는 미규정이며, emotion_learning_interface §7.4(L295-298)의 '단일 세션 θ 변화 최대 ±0.5'는 θ 추정치에 적용되는 cap이고 본 보정은 target_difficulty(문항 선택 오프셋)라 정본 무모순. 오답 민감 비대칭은 ZPD-5 좌절방지(L146-156) 방향과 정합.
2. **[KEEP]** `docs\sot 2\3-5_Education-Learning\02_spaced-repetition\flashcard_auto_generation.md`:152-177 — quality_filter의 답 누출 검사를 'card.back in card.front' 단일 exact-containment 규칙(L160)으로 두고 카드 서브타입별 분기를 두지 않은 필터 강도 선택.
   - 선택지: (a) 현행 단순 containment + 기준5 LLM 자체평가 병행 (b) 서브타입별 검사(cloze_text/expected_output 별도 규칙) (c) 유사도 기반 누출 검사
   - 판정: KEEP — 어떤 정본도 누출 검사 알고리즘을 고정하지 않으며, 기준5 LLM 품질평가(L172-175, threshold 0.6)가 2차 방어로 존재해 필터 정밀도는 설계 재량. 서브타입 분기는 Phase5 품질 개선 후보로만 권고.
3. **[KEEP]** `docs\sot 2\3-5_Education-Learning\02_spaced-repetition\flashcard_auto_generation.md`:292, 469 — 동일한 LOCK-ED-02 IRT θ 값을 FlashCard는 difficulty_irt(L292), ImageOcclusionCard V2는 difficulty_theta(L469)로 모델별 상이한 필드명으로 설계한 스키마 명명 선택.
   - 선택지: (a) 현행 모델별 개별 명명 (b) difficulty_theta로 통일 (c) difficulty_irt로 통일
   - 판정: KEEP — LOCK-ED-02는 IRT 5단계 체계(값 의미)만 고정하고 필드명은 미규정이므로 정본 위반 아님. 두 필드 모두 LOCK-ED-02 주석으로 의미 추적 가능. 차기 스키마 정비 시 difficulty_theta(범위 제약 Field(ge=-3,le=3) 보유) 기준 통일 권고.
4. **[KEEP]** `docs\sot 2\3-5_Education-Learning\02_spaced-repetition\review_scheduler.md`:61-69, 80-101 — 일일 카드 한도/최소 간격을 schedule_review는 전역 상수(DAILY_CARD_LIMIT/MIN_INTERVAL_HOURS, L63/L68), build_daily_queue는 학습자별 config(L81-101, 기본 50/4h)로 이원화한 설정 아키텍처 선택.
   - 선택지: (a) 현행 이원화(전역 게이트 + 학습자별 큐 설정) (b) 학습자별 config 단일 출처화 (c) 전역 상수를 하드캡, config를 그 이내 개인화로 관계 명시
   - 판정: KEEP — 정본(LOCK-ED-04는 SM-2 파라미터만 고정)이 한도 출처를 규정하지 않아 무모순. 단 (c) 방식으로 전역 상수=시스템 상한, config=개인 설정이라는 관계 주석을 추가하는 명세 보강 권고(값 변경 불요).
5. **[KEEP]** `docs\sot 2\3-5_Education-Learning\02_spaced-repetition\review_scheduler.md`:227-238 — SUBJECT_FACTOR 계수를 인용 SOT §B.2.2(coding=0.8, formula=0.85)에서 의도적으로 완화(coding=0.85, math=0.90)하고 그 편차를 주석으로 명시(L228-229 '4축 분리 설계이므로 방향 준수')한 튜닝 값 선택.
   - 선택지: (a) 현행 완화값(4축 분리 설계 보정) (b) §B.2.2 원값 그대로(0.8/0.85) (c) §B.2.2 갱신 후 양측 동기화
   - 판정: KEEP — 본문이 §B.2.2를 '방향(direction)' 기준으로 인용하며 4축 분리(시간대·세션강도 factor 별도 적용으로 중복 페널티 방지)라는 편차 근거를 명시(L229). LOCK 위반 없고 최종 clamp 0.5~2.0(L241) 내 안전. 편차가 문서화된 합리적 설계.
6. **[KEEP]** `docs\sot 2\3-5_Education-Learning\03_coding-tutorial\code_review_learning.md`:266-272 — LLM 복잡도 분석의 교차검증을 'AST 중첩루프 depth>=2 AND 출력에 O(n) substring 존재' 단순 휴리스틱으로 설계한 검증 알고리즘 선택.
   - 선택지: (a) 현행 substring 휴리스틱 (b) 정규식/구조화 출력(complexity enum) 파싱 (c) AST 단독 판정으로 LLM 출력 덮어쓰기
   - 판정: KEEP — 검증 휴리스틱의 정밀도는 정본 미규정 영역의 설계 재량이며 LLM 과소평가의 최빈 케이스(O(n) 표기)를 잡는 저비용 1차 방어로 합리적. 차기 개선 시 output_schema(L263 ComplexityAnalysis)에 complexity를 enum으로 강제하는 (b) 권고.
7. **[KEEP]** `docs\sot 2\3-5_Education-Learning\03_coding-tutorial\coding_challenge.md`:130-156 — 점수 공식의 streak_factor 계수(0.1×연속정답, 캡 2.0)·time_factor 하한(0.5)·힌트 감점(10점/회) 등 스코어링 정책 값과 리셋 시점(§5.3 포기 시 초기화만 명시) 선택.
   - 선택지: (a) 현행 계수(10연속 시 2배 캡) (b) 완만한 계수(0.05×, 캡 1.5) (c) 오답 시 리셋 명시 추가
   - 판정: KEEP — LOCK-ED-06은 힌트 3단계 구조만 고정(L149-156 준수)하고 점수 계수는 미규정. 캡 2.0으로 발산 방지되어 합리적. 오답 시 streak 리셋 여부만 §5.3에 한 줄 보강 권고(게임 밸런스 설계 재량).
8. **[KEEP]** `docs\sot 2\3-5_Education-Learning\04_content-generation\conversation_practice.md`:130-136 — 회화 중 감정 적응 트리거를 좌절은 intensity ≥ 6, 스트레스는 arousal > 0.5로 서로 다른 척도(강도 1~10 vs 차원 0~1)로 정의한 임계값 선택.
   - 선택지: (a) 현행 혼합 척도 (b) emotion_learning_interface §7.2 정합(스트레스 intensity ≥ 7) (c) 전 트리거 arousal/valence 차원 통일
   - 판정: KEEP — LOCK-HW-01(L127-128 verbatim 인용)은 기본7+세부5+차원2(arousal,valence)를 모두 제공하며 임계값 자체는 어느 정본도 고정하지 않음. 스트레스를 각성 차원으로 잡는 것은 유효한 설계. 일관성 위해 차기 정비 시 emotion_learning_interface §7.2와 척도 통일 권고.
9. **[KEEP]** `docs\sot 2\3-5_Education-Learning\04_content-generation\conversation_practice.md`:94-116 — 회화 카드를 LOCK-ED-08 4유형의 재정의가 아닌 별도 ConversationCard 모델의 card_type Literal 5번째 값('회화')으로 추가한 확장 패턴 선택(R-02 LOCK 해제 절차 문서화: 사유/대안검토/영향분석 L100-102).
   - 선택지: (a) 현행 신규 모델 내 5값 Literal 확장(정본 4유형 불변 명시) (b) 별도 conversation_subtype 필드 분리(GPT 권고) (c) LOCK-ED-08 정식 개정으로 5유형화
   - 판정: KEEP — AUTHORITY_CHAIN §4 LOCK-ED-08(L90, 4유형)은 byte 불변이고 본 파일이 '정본 재정의 0'을 명시(L102)하며 R-02 절차로 사유·대안·영향을 문서화한 모범적 확장 설계. 스키마 소비자 혼동 우려는 ConversationCard가 FlashCard와 별개 모델이므로 실해 없음.
10. **[KEEP]** `docs\sot 2\3-5_Education-Learning\04_content-generation\online_course_support.md`:72-85 — 외부 플랫폼 동기화 파이프라인(§4.2)을 고수준 흐름도로만 명세하고 OAuth 토큰 저장/갱신·rate-limit·재시도를 본문에 두지 않은 명세 granularity 선택(E5 폴백은 §7 S-9 local 캐시 한 줄).
   - 선택지: (a) 현행 고수준 명세 + E5 폴백 위임 (b) 표준 통합 컴포넌트(토큰 매니저/재시도 정책) 본문 상세화 (c) 공통 외부연동 모듈로 위임 명시
   - 판정: KEEP — 정본은 외부 연동 상세 수준을 규정하지 않으며 L3 스펙에서 인프라 공통 관심사를 위임하는 것은 통상적 설계 재량. E5 폴백 경로가 존재(S-9)해 결함 아님. Phase5 구현 시 (c) 공통 모듈 참조 한 줄 보강 권고.
11. **[KEEP]** `docs\sot 2\3-5_Education-Learning\04_content-generation\online_course_support.md`:75 — Udemy 진도 동기화를 공식 API 대신 'Udemy Scraper'로 구현하기로 한 외부 연동 전략 선택.
   - 선택지: (a) 현행 스크래퍼 (b) Udemy Affiliate/Instructor API 한정 연동 (c) 수동 진도 입력 폴백 단일화
   - 판정: KEEP — 어떤 정본도 특정 플랫폼 연동 방식을 고정하지 않아 무모순이며 Coursera/edX는 API 경로(L75) 유지. 단 스크래핑의 ToS/파손 리스크를 §7 위험 표에 1행 명시하고 (c)를 폴백으로 연결하는 문서 보강 권고(설계 변경 불요).
12. **[KEEP]** `docs\sot 2\3-5_Education-Learning\04_content-generation\youtube_learning.md`:338-354 — _find_best_matching_segment의 자막 구간 매칭 알고리즘으로 TF-IDF 코사인 대신 token-set Jaccard 중첩(L346-350)을 채택한 유사도 알고리즘 선택(docstring L341은 'TF-IDF 코사인 유사도' 표기).
   - 선택지: (a) 현행 Jaccard(경량, 의존성 0) (b) 실제 TF-IDF 코사인 구현 (c) 임베딩 cosine
   - 판정: KEEP — 정본은 구간 매칭 알고리즘을 미규정하며 자막 구간 길이 특성상 Jaccard는 합리적 경량 선택. 단 docstring을 'token-set Jaccard 유사도'로 정정해 명칭-구현을 일치시키는 표기 수정 권고(paper/podcast 동일 표기 포함).
13. **[KEEP]** `docs\sot 2\3-5_Education-Learning\04_content-generation\quiz_test_generation.md`:626-634 — §9 E6 Privacy/보안을 데이터 보존(90일)·노출 권한(L631 '해당 사용자에게만 노출')·AES-256 수준으로 명세하고 세부 authN/authZ(요청자 권한 검사, QuizResult 접근제어, url 검증)는 플랫폼 계층에 위임한 보안 아키텍처 선택.
   - 선택지: (a) 현행 도메인 규칙 + 플랫폼 위임 (b) 도메인 스펙 내 RBAC/SSRF 가드 상세화 (c) 3-3 PKM M-028 RBAC 참조 명시
   - 판정: KEEP — L631이 기본 접근통제 원칙(소유자 한정 노출)을 이미 정의하고, 도메인 L3가 인증 인프라를 재명세하지 않는 것은 전 도메인 공통 설계 관례. 정본 위반 없음. content_source url 타입의 fetch 검증만 (c) 방식 cross-ref 보강 권고.
14. **[KEEP]** `docs\sot 2\3-5_Education-Learning\05_learning-analytics\time_management.md`:42-74 — 포모도로 상태머신(L44-60)에 PAUSE/재개 전이를 두지 않고(start/complete/resume/cancel/reset만) 중단은 데이터 모델의 status 'interrupted'(L73)와 Interruption[] 기록으로만 처리하는 엄격(no-pause) 타이머 설계 선택.
   - 선택지: (a) 현행 no-pause(포모도로 정통 기법: 중단 시 세트 무효) (b) PAUSED 상태 + pause/resume 전이 추가 (c) FSM에 interrupted 종단 전이만 추가
   - 판정: KEEP — 포모도로 기법의 정통 설계는 일시정지를 허용하지 않으며(중단=세트 무효) 어떤 정본도 PAUSE 지원을 요구하지 않음. 모델-FSM 정합을 위해 FOCUSING→(interrupt)→IDLE 종단 전이 1개와 'interrupted는 cancel의 중단 사유 기록 변형'이라는 주석 보강 권고(설계 유지).
15. **[KEEP]** `docs\sot 2\3-5_Education-Learning\05_learning-analytics\mentoring_platform.md`:52-58 — 멘토 인증(§3.2)을 3단계 배지 체계(자격/평판 ≥4.0/활동)로 정의하고 검증 주체·증빙 스키마·인증 취소·이의제기 절차는 미정의로 둔 거버넌스 granularity 선택.
   - 선택지: (a) 현행 기준값만 정의(운영 절차는 Phase5) (b) mentor_verification_state/revocation_policy 스키마 상세화 (c) 외부 자격 검증 서비스 위임
   - 판정: KEEP — 정본은 멘토 인증 절차를 규정하지 않으며 L3 단계에서 임계값(평점 4.0/5.0 유지)과 배지 구조를 고정한 것으로 충분. S-2/S-8 테스트 시나리오(L162,168)가 검증 경로를 커버. 운영 거버넌스(취소/이의)는 Phase5 운영 명세 항목으로 이연하는 설계 재량.
16. **[KEEP]** `docs\sot 2\3-5_Education-Learning\05_learning-analytics\mentoring_platform.md`:70, 166 — 멘티를 기본 익명(mentee_id 익명 ID, L70)으로 두면서 좌절/스트레스 감정 신호를 opt-in 시 멘토에게 분류 결과만 전달(S-6, L166)하는 프라이버시 정책 조합 선택(동의 주체 상세는 미정의).
   - 선택지: (a) 현행 익명+opt-in 분류결과 전달 (b) 감정 전달 시 익명 해제 동의 별도 요구 (c) 감정 신호 멘토 전달 자체 비활성
   - 판정: KEEP — AUTHORITY R-08-6/R-09-6 정본이 '학습자(멘티) opt-in 필수, 기본 비활성, 분류 결과만'을 이미 고정하며 본 파일이 이를 준수(원시 데이터 금지 R-09-3). 익명 ID와 감정 카테고리 전달의 조합은 재식별 위험이 낮은 합리적 설계. 동의 주체=멘티임을 §6.2 S-6에 명시 보강만 권고.
17. **[KEEP]** `docs\sot 2\3-5_Education-Learning\05_learning-analytics\gamification.md`:249 (+habit_tracker.md 75, challenge_leaderboard.md 56) — streak 1일 보호 메커니즘을 모듈별로 'Streak 방어권'(gamification L249)/'freeze_tokens'(habit_tracker L75, 주 1개 지급)/'Streak 보호 토큰'(challenge_leaderboard L56·L130·L136)으로 각자 명명·지급 규칙을 달리한 기능별 분산 설계 선택.
   - 선택지: (a) 현행 모듈별 독립 메커니즘(보상형/주급형/자동적용형으로 의미상 상이) (b) 단일 용어·단일 토큰 풀로 통합 (c) 용어만 통일하고 지급 규칙은 모듈별 유지
   - 판정: KEEP — LOCK-ED-10은 6단계 체계(XP→레벨→배지→Streak→챌린지→리더보드)만 고정하고 보호 토큰 메커니즘은 미규정. 세 모듈의 지급 조건이 실제로 다르므로(마일스톤 보상 vs 주간 지급 vs 웰빙 자동적용) 별개 메커니즘으로 보는 것이 타당. 차기 정비 시 (c) 용어 사전 통일만 권고.
18. **[KEEP]** `docs\sot 2\3-5_Education-Learning\05_learning-analytics\study_group_matching.md`:82-103 — 그룹 매칭 알고리즘(§4.1)을 '4요소 군집 → 호환도 가중합 → 3~6인 추천' 고수준으로 명세하고 요소별 weight·cutoff·tie-break·cold-start를 미고정한 알고리즘 파라미터 granularity 선택.
   - 선택지: (a) 현행 고수준 명세(파라미터는 구현/튜닝 단계 결정) (b) weight/cutoff/tie-break를 스키마로 고정 (c) 가중치를 학습자 설정으로 노출
   - 판정: KEEP — LOCK-ED-07 5필드 EXACT 보존(L49-61)을 준수하며 매칭 가중치는 어떤 정본도 고정하지 않는 튜닝 영역. compatibility 0~1 범위와 그룹 크기 3~6인은 이미 고정(L101,L93)되어 출력 계약은 명확. 가중치 사전 고정은 A/B 튜닝 여지를 없애므로 현행이 합리적.
19. **[KEEP]** `docs\sot 2\3-5_Education-Learning\EDUCATION_LEARNING_상세명세.md`:110-134 — V1 초안 DifficultyAdjuster.adjust의 하향 트리거를 정답률 <0.50으로만 두고 0.50~0.70 구간은 '유지'로 처리한 보수적 dead-band 설계 선택(docstring L115-117에 의도 명시: 70~85% 유지/>85% +1/<50% -1).
   - 선택지: (a) 현행 dead-band(연속 2오답 규칙 L127-128이 보조 하향 경로 제공) (b) <0.70 하향 분기 추가(현행 L3 difficulty_adjustment.md L128 방식) (c) 0.50~0.70 완만 하향 + <0.50 대폭 하향 2단계
   - 판정: KEEP — 본 문서는 superseded V1 초안(동결)이며 현행 정본인 L3 difficulty_adjustment.md(L124-131)가 이미 <0.70 하향을 구현해 LOCK-ED-02 70-85% 추구는 production 경로에서 충족됨. 초안 자체도 docstring으로 의도를 명시한 휴리스틱+streak 보조 경로의 정합적 설계라 소급 수정 불요.

> notes: [방법] 풀=clc 60 + tight(전건 clc 부분집합, 신규 0) + GPT 13 = 고유 67건. 제외 단계: (1) mf_in confirmed 24건 매칭 — T8-278/289·T8-279/291·T8-038·T8-157·T8-039·T8-037·T8-036·T8-034·T8-065·T8-075·T8-134·T8-146·T8-159·T8-201·T8-259·T8-236/T6-235·T8-015·T8-042·T8-147·EDU-AUD-009·T8-009·T8-091·T8-174·T6-288·EDU-AUD-006. (2) mf_in unconfirmed 2건(T5-007, T6-246)도 객관결함 후보 트랙으로 제외. (3) verify=refuted 오탐 9건: T8-019/047/066/109/124, T6-176, T8-224/260/271 (+T8-237 uncertain). (4) 단순 표기/라인인용 5건: T5-204(단복수), T6-206(인용 라인범위), T6-117(부등호 표기), EDU-AUD-012(LF 집계), EDU-AUD-013(68vs69 표기). (5) 주관 아닌 잔여 객관성 항목: O-ID/SOT 인용 불일치 fami

### 4-2_CICD-Pipeline (18건)

1. **[KEEP]** `docs\sot 2\4-2_CICD-Pipeline\01_ci-workflows\WF-13_nightly.md`:61 — nightly 전체 목표 <60분(병렬 최적화)/최대 120분 — step별 타임아웃 합(145분)은 worst-case 상한이며 목표치와 별개로 두는 SLA 설계
   - 선택지: (a) 목표 60분+타임아웃은 안전상한으로 유지 (b) 목표를 critical-path 합산 기준으로 상향 (c) step 타임아웃 축소
   - 판정: KEEP — 상세명세 L395 'nightly.yml < 60분 전체 포함'이 정본이며 일치. 타임아웃은 per-step 안전 상한이고 T-10이 전체 >120분 시 타임아웃+부분결과 저장을 별도 정의해 상태머신 완결.
2. **[KEEP]** `docs\sot 2\4-2_CICD-Pipeline\01_ci-workflows\WF-4_build-tauri.md`:94 — 아티팩트 retention을 release_mode 시 30일/비릴리스 7일로 차등하는 비용 최적화 (상세명세 L144는 무조건 30일)
   - 선택지: (a) 조건부 7/30일 차등 (b) 상세명세대로 무조건 30일
   - 판정: KEEP — 비릴리스(dry-run/CI check) 7일은 합리적 스토리지 최적화. retention은 LOCK 비대상이며 상세명세 L144는 릴리스 경로 요약 스케치, WF 상세파일이 L2 구현 정본(secrets_mapping L126 'WF 상세 산출물 기반 보강' 관행)으로 우선.
3. **[KEEP]** `docs\sot 2\4-2_CICD-Pipeline\02_cd-workflows\WF-7_deploy-prod.md`:70 — monitor-30min job 타임아웃 35분 sizing + full-deploy 부분 실패 시 '해당 노드만 롤백'(P5R) 노드 단위 복구 전략(멱등성 키 미도입)
   - 선택지: (a) 35분(30분 창+5분 버퍼)+노드별 롤백 유지 (b) 타임아웃 확대+재실행 멱등성 키/re-entrancy 가드 추가
   - 판정: KEEP — 35분은 30분 모니터링 창에 5분 버퍼로 합리적이며 정본 위반 없음. 부분 실패 복구는 §8 P5R '해당 노드만 롤백, 나머지 유지'로 정의된 설계 선택. 멱등성 가드는 Phase 5 운영 보강 후보로만 기록.
4. **[KEEP]** `docs\sot 2\4-2_CICD-Pipeline\02_cd-workflows\WF-6_deploy-staging.md`:79 — 스테이징 배포 게이트의 벤치마크 회귀 임계 10%(경고+수동 승인) — nightly 회귀 다단계 정책(+20/30/50%)과 별도 축
   - 선택지: (a) 배포 게이트 10% 유지 (b) benchmark_baseline §6.2 다단계(+20/30/50)로 통일
   - 판정: KEEP — 상세명세 F-1 L414 '벤치마크 회귀 < 10%'와 byte 일치(배포 게이트 정본). +20/30/50은 benchmark_baseline §6.2의 nightly 관측·알림 정책으로 목적이 다르며 mttr_metrics_dashboard §5도 양자를 구분 인용. 배포 게이트가 더 엄격한 것은 정합적 설계.
5. **[KEEP]** `docs\sot 2\4-2_CICD-Pipeline\02_cd-workflows\k8s_argocd_pipeline.md`:352-358 (§8.1 L608, T-7 L658) — update-helm-values release-bot push의 충돌 처리를 워크플로 YAML 예시가 아닌 §8.1 에스컬레이션 매트릭스('자동 retry 1회 → 실패 시 수동 개입')로 명세하는 문서화 수준
   - 선택지: (a) §8.1/T-7 정책 명세 유지, YAML은 정본 구조 예시 (b) YAML에 retry 루프 직접 삽입
   - 판정: KEEP — §8.1 L608이 retry 1회+수동 개입 정책을 정본으로 규정하고 T-7(L658)이 시험 계약으로 고정. 스펙 문서의 YAML은 구조 예시이며 구현 시 §8.1을 따르면 모순 없음(본문 내 정책>예시 코드).
6. **[KEEP]** `docs\sot 2\4-2_CICD-Pipeline\03_security-scanning\runbook_secret_rotation.md`:71 — 만료 60일 전 알림을 GitHub Secret 메타데이터(created_at/updated_at) + §3 로테이션 주기표(90/180/365/730일) 합산으로 추정하는 만료 산정 방식
   - 선택지: (a) created_at+정의된 주기 합산 추정 (b) 외부 인벤토리(인증서 실만료일 DB) 별도 구축
   - 판정: KEEP — GitHub Actions secrets API는 expires_at을 노출하지 않으므로 created_at+§3 주기 합산이 실행 가능한 유일한 내장 방식이며, §3 주기표가 본 문서 정본. 인증서 실만료일(APPLE_* 등)은 §3 주기를 만료일에 정렬해 운용하는 설계 선택.
7. **[KEEP]** `docs\sot 2\4-2_CICD-Pipeline\05_release-management\WF-14_version-bump.md`:92-104 (T-6 L182) — bump() 의사코드에서 next_pre_counter()의 prerelease 타입 전환 리셋 로직을 전개하지 않고 T-6 시험(alpha→rc ⇒ 1.2.4-rc.1)으로 계약을 고정하는 추상화 수준
   - 선택지: (a) 의사코드 스케치+시험 계약 고정 유지 (b) 타입 전환 리셋 분기를 의사코드에 명시
   - 판정: KEEP — LOCK-CI-04(SemVer 2.0.0)는 형식만 규정하며 카운터 리셋 동작은 T-6(L182)이 기대값 rc.1로 명확히 고정. 의사코드의 상세 수준은 설계자 선택이고 시험이 구현을 구속하므로 정본 모순 없음.
8. **[KEEP]** `docs\sot 2\4-2_CICD-Pipeline\CICD_PIPELINE_구조화_종합계획서.md`:936, 945 (mttr_metrics_dashboard.md L74) — P0~P2만 수치 MTTR(30min/2h/24h)을 부여하고 P3은 best-effort(backlog)로 두는 우선도 SLA 설계
   - 선택지: (a) P3=best-effort 무수치 (b) P3에도 수치 MTTR(예: ≤72h) 부여
   - 판정: KEEP — mttr_metrics_dashboard.md §4 L74에 'P3 | best-effort | 동일 | backlog' 행이 실존하여 P3 정책이 정의돼 있음. 저우선 인시던트에 수치 SLA를 두지 않는 것은 표준 운영 설계이며 PLAN(종합계획서)은 P0~P2 수치만 요구해 무모순.
9. **[🔧CHANGE]** `docs\sot 2\4-2_CICD-Pipeline\CICD_PIPELINE_상세명세.md`:451, 467-470 — G-3 타임스탬프 서버 폴백을 단일 대체(sectigo)로 한정하는 폴백 전략 + G-2 macOS keychain 생성 비밀번호 처리 방식
   - 선택지: (a) 단일 TSA 폴백+빈 비밀번호 예시 유지 (b) 단일 TSA 폴백 유지+keychain 비밀번호를 WF-4 §5.2 정본 패턴(openssl rand)으로 정합화 (c) TSA 다단 폴백+retry 추가
   - 판정: 옵션 (b) — G-3 단일 sectigo 폴백은 서명 실패 시 on-call 알림(G-3-1)과 결합된 합리적 설계로 유지. 그러나 G-2 L451 `-p ""`는 객관결함(i13) 교정으로 WF-4 §5.2가 KEYCHAIN_PW=$(openssl rand -base64 32) 패턴을 정본화한 뒤 남은 모순 잔재이므로 본문 정본(WF-4 §5.2)에 정렬.
10. **[KEEP]** `docs\sot 2\4-2_CICD-Pipeline\02_cd-workflows\docker_compose_pipeline.md`:310-323, 497, 589, 629, 634 — V2 deploy-v2.yml에 카나리 입력/job을 두지 않고(environment/version만) 카나리 오케스트레이션을 WF-7 deploy-prod 계층에 위임, §5.1은 상세명세 §F-3 결정 트리를 verbatim 인용하는 계층화 설계
   - 선택지: (a) 카나리는 WF-7 소관, V2는 compose 배포+F-3 verbatim 인용 (b) deploy-v2.yml에 canary_percentage 입력+canary job 추가 (c) V2 문서에서 카나리 행 제거
   - 판정: KEEP — §5.1이 '상세명세 §F-3 verbatim' 인용임을 명시하고 카나리 실행 주체(canary_percentage 입력)는 WF-7이 보유. 인프라 계층(WF-7 게이트)과 compose 계층(deploy-v2)의 분리는 정합적 아키텍처 선택. T-2/T-7은 WF-7 경유 통합 시나리오로 읽힘 — 주석 보강은 선택 사항.
11. **[KEEP]** `docs\sot 2\4-2_CICD-Pipeline\02_cd-workflows\k8s_argocd_pipeline.md`:148-174, 381-387, 460-486 — 카나리 점진 배포를 Argo Rollouts CRD 소유로 위임(L381 주석)하고 Helm chart 트리에는 Deployment+AnalysisTemplate만 명세, Rollout/traffic-routing 리소스 상세는 구현 단계로 이연하는 명세 수준
   - 선택지: (a) AnalysisTemplate+위임 주석 수준 유지 (b) Rollout CRD/Ingress weighted routing 템플릿까지 명세 (c) canary 옵션 제거 후 단순 sync 축소
   - 판정: KEEP — L381 '카나리/블루-그린 진행은 Argo Rollouts CRD가 소유' + §5.2 자동 롤백 명세 + kubectl argo rollouts promote(L386)로 책임 소재가 정의됨. CRD 템플릿 상세화 수준은 ISS-08 '부분 해소'(§7) 스코프 내 설계 선택이며 정본 위반 없음. Phase 5에서 Rollout 템플릿 보강 권고.
12. **[KEEP]** `docs\sot 2\4-2_CICD-Pipeline\02_cd-workflows\docker_compose_pipeline.md`:378, 459 (k8s_argocd_pipeline.md:366-369) — GitHub Action 참조를 태그/브랜치(trivy-action@master, slack-github-action@v1.26.0)로 핀하고 argocd CLI를 버전 고정 URL에서 checksum 검증 없이 다운로드하는 공급망 핀닝 수준
   - 선택지: (a) 태그/버전 핀 유지 (b) 전 Action commit SHA 핀 + 바이너리 checksum/signature 검증 추가
   - 판정: KEEP — 도메인 정본(R-15-2, LOCK-CI-07/08/09)에 SHA 핀/체크섬 검증을 요구하는 규정이 없어 정본 모순 아님(핀닝 수준은 보안 정책 선택). 다만 @master는 mutable ref이므로 보안팀 승인 경로로 SHA 핀 전환을 강화 권고(특히 trivy-action@master).
13. **[KEEP]** `docs\sot 2\4-2_CICD-Pipeline\03_security-scanning\WF-8_security-scan.md`:23-39 (전 문서 permissions 0건; secrets_mapping.md:300) — 최소권한 permissions: 블록 명시 범위를 WF-9/10/14로 한정하고 WF-8은 기본 워크플로 권한에 의존하는 권한 명세 스코프
   - 선택지: (a) 현행(3개 WF만 명시 확인) 유지 (b) WF-8에 contents: read + security-events: write 명시 추가
   - 판정: KEEP — secrets_mapping §8.2 L300이 '(WF-9, WF-10, WF-14 확인)'으로 명시 범위를 정확히 한정 기재해 허위 주장 없음. 명시 범위는 거버넌스 스코프 선택. 단 SARIF 업로드에 security-events: write가 필요하므로 차기 개정 시 WF-8 permissions 블록 추가를 권고.
14. **[KEEP]** `docs\sot 2\4-2_CICD-Pipeline\AUTHORITY_CHAIN.md`:37 (optimization_report.md:141-147, docker_compose:576, k8s:596, WF-13:153) — LOCK-CI-11(cancel-in-progress: true)을 CI/PR 워크플로 표준으로 해석하고 release/deploy/scheduled 워크플로는 false 예외(배포 부분적용·결과 유실 방지)로 운용하는 스코프 해석
   - 선택지: (a) 예외 해석 유지(각 WF 정당화 주석+optimization_report §4.2 분류) (b) LOCK-CI-11 정본 자체를 'CI=true/deploy=false'로 개정 (c) 전 WF true 강제
   - 판정: KEEP — 배포 중 취소는 compose 부분 적용 위험(docker_compose L328 주석), nightly는 결과 유실(WF-13 L35)로 false가 운영상 합리적이며, optimization_report §4.2/L147이 예외 체계를 정합화하고 WF-13 §8이 '예외 정당화'를 LOCK 체크에 명시. LOCK 정본 문구 개정은 PHASE_B6 승인 사항(AUTHORITY L37 변경 권한)으로 Phase 5 이관 권고 — 단독 편집 불가.
15. **[KEEP]** `docs\sot 2\4-2_CICD-Pipeline\02_cd-workflows\docker_compose_pipeline.md`:441, 519 — 6서비스 전수 헬스체크 판정을 docker compose ps + grep -E "healthy|running" 단일 패턴으로 수행하는 검증 엄격도
   - 선택지: (a) 단일 패턴(healthy 또는 running 허용) 유지 (b) healthcheck 정의 서비스=healthy만, 미정의 서비스=running 허용 분기
   - 판정: KEEP — §3.3 compose 정본이 6서비스 전수에 healthcheck를 정의하고 start_period 대기(L434) 후 검증하므로 실용적 선택이며 정본 위반 없음. 더 엄밀한 분기 검증(healthy-only)은 T-12 healthcheck 매트릭스 시나리오와 함께 Phase 5 강화 후보로 권고.
16. **[KEEP]** `docs\sot 2\4-2_CICD-Pipeline\02_cd-workflows\docker_compose_pipeline.md`:526-530 — 이미지 태그 롤백과 데이터/스키마 롤백을 분리하고, 스키마 호환성은 자동 preflight 게이트 대신 'release notes 마이그레이션 호환 매트릭스 필수'+on-call 에스컬레이션으로 관리하는 절차 설계
   - 선택지: (a) 수동 매트릭스+에스컬레이션 유지 (b) deploy preflight에 자동 호환성 게이트 추가
   - 판정: KEEP — §5.3이 qdrant forward-only/alembic mismatch 위험을 명시적으로 인지하고 '호환 매트릭스 필수'를 절차 요건으로 규정. 자동 게이트 vs 문서화된 수동 절차는 설계자 선택이며 정본 모순 없음. V3 K8s 트랙(Phase 5 entry-gate)에서 자동화 검토 권고.
17. **[KEEP]** `docs\sot 2\4-2_CICD-Pipeline\03_security-scanning\secrets_mapping.md`:115-116, 277-286 — V2 런타임 시크릿(POSTGRES_*/QDRANT_API_KEY/NEO4J_AUTH/OPENAI_API_KEY)을 master table 32건에 포함하지 않고 §7.1 Stub으로 분리, 승격/별도 runtime_secrets_mapping.md 분리는 차기 결정으로 이연하는 거버넌스 스코프 phasing
   - 선택지: (a) Stub 분리 유지(§0.2 스코프 결정) (b) master table 승격+rotation/owner 즉시 정의 (c) runtime_secrets_mapping.md 별도 정본 신설
   - 판정: KEEP — §0.2가 '빌드/배포 시점 시크릿만 커버'를 스코프 정본으로 명시하고 L286이 승격/분리 결정을 명시적으로 이연 기록. deploy-v2.yml은 environment: 보호 하에 secrets.*로만 참조(R-15-2 충족)하므로 정본 위반 없음. ARGOCD_AUTH_TOKEN은 이미 §7.1에 등재됨(L283, 단 L283-284 중복 행 정리 필요 — 표기 사항).
18. **[KEEP]** `docs\sot 2\4-2_CICD-Pipeline\02_cd-workflows\k8s_argocd_pipeline.md`:545, 553-554 — LOCK-CI-06 5-target 확장 보류(F-15 옵션 B) 결정의 근거로 'Linux ARM64 desktop 점유율 <1%(일반 분포 참조)'와 'GitHub-hosted ARM64 runner 2026-Q1 제한적 지원'을 외부 정량 증빙 없이 서술하는 의사결정 근거 수준
   - 선택지: (a) 현행 서술+DEFERRED_TO_PHASE3 유지 (b) Evidence 출처 부기 (c) 수치 제거 후 '근거 부족, Phase 3 재평가'만 잔존
   - 판정: KEEP — 결정 자체가 LOCK 변경이 아닌 [LOCK_UNCHANGED] 보류이며 §6.2 근거 5건+자동 RESOLVE 금지 원칙을 따르고 AUTHORITY_CHAIN 변경 이력(2026-04-24 row)에 정식 등재됨. L553이 '(공개 시장 조사 통계 일반 분포 참조)'로 한정 표기해 fabrication 아님. Phase 3 재평가 시 실증 데이터 첨부 권고.

> notes: 앵커 19 대비 18건 — 강제 짜맞춤 없이 차이 1건 보고. 도출 과정: 입력 4파일 전수 대조로 후보 풀 = clc 28 + GPT 18 중 mf_in 21건 객관결함과 매핑되는 26건(clc T8-006/027/038/046/048/049/053/057/058/075/T5-077/078/079/105/T6-106/107/131 + GPT CI-001/002/003/006/009/011/012/013/017; i5는 T8-027·T8-078·CI-012 3중 매핑)을 제외 → 잔여 20건 전수 디스크 실측. 제외 2건: (1) T6-132 = 오탐(디스크 반박): WF-7_deploy-prod.md L36-38에 canary_percentage options [10,25,50,100] 실존 + cross_validation 리포트 L89가 '인프라 노드 비율 vs LOCK-ML-08 모델 트래픽 비율' 축 구분을 명시 — clc verify=refuted와 일치. (2) T8-116 = 단순 카운트 표기: V-04 '22개(15+7)'는 Phase 0 baseline 주석이고 동일 행에 'P1-2 secrets_mapping v1.1 32건 확장(base

### 3-2_Multimodal-Processing (18건)

1. **[KEEP]** `docs\sot 2\3-2_Multimodal-Processing\01_image-pipeline\image_generation.md`:121-131 (E3, 실측: 세마포어/큐 부재 grep 0건) — 단일 RTX 4090 로컬 GPU 작업에 admission control(큐/세마포어) 없이 OOM을 E5에서 사후 대응(halve-size)하는 동시성 전략
   - 선택지: (a) 현행 reactive OOM 대응 (b) GPU 세마포어 1-job 직렬화 큐 (c) 배치 admission control
   - 판정: KEEP — RULE 1.3/PLAN 3.0/LOCK 어디에도 GPU 동시성 직렬화 요구 없음. 현행 reactive 전략은 합리적 선택이나 V2 운영 진입 전 세마포어 추가를 권장 노트로 남길 것
2. **[KEEP]** `docs\sot 2\3-2_Multimodal-Processing\01_image-pipeline\image_generation.md`:732 (실측: '외부 fetch (`href`, `xlink:href`) 차단 옵션') — SVG 외부 fetch(href/xlink:href) 차단을 강제 기본값이 아닌 '옵션'으로 두는 보안 기본값 선택
   - 선택지: (a) 현행 옵션(opt-in 차단) (b) default-on 차단 + opt-out (c) 무조건 차단
   - 판정: KEEP — 정본 위반 없음(sanitize_svg 허용리스트는 L697에서 강제됨, LOCK-MM-02 준수). 다만 SSRF 방어 관점에서 default-on 전환이 바람직하다는 권고를 부기
3. **[KEEP]** `docs\sot 2\3-2_Multimodal-Processing\01_image-pipeline\image_safety_metadata.md`:146 (실측: score >= 0.4 reject; L92 minors low=0.20/mid=0.40) — minors zero-tolerance의 reject 경계를 mid(0.40)로 두고 0.20-0.39 구간은 flag+blur/sanitize로 처리하는 임계값 선택
   - 선택지: (a) 현행 reject@0.40 (b) reject 경계를 low(0.20)로 하향(완전 보수화) (c) manual_review 중간 단계 추가
   - 판정: KEEP — RULE/PLAN/LOCK에 minors 수치 임계 정본 없음. L92 주석 '보수적'과 같이 0.40은 오탐율과의 트레이드오프 선택. 더 보수화하려면 (b)는 정책 결정 사안
4. **[KEEP]** `docs\sot 2\3-2_Multimodal-Processing\01_image-pipeline\vision_language_integration_v2.md`:100,110 (xxhash64) vs vision_language_integration.md:145 (SHA256(normalized_bytes)) — 캐시 키 해시를 V1=SHA256, V2=xxhash64로 세대별 다르게 쓰는 알고리즘 선택
   - 선택지: (a) 현행 세대별 분리(V2 고속 비암호 해시) (b) SHA256 통일 (c) xxhash64 통일+V1 마이그레이션
   - 판정: KEEP — V1/V2 캐시 네임스페이스가 분리돼 있어 키 충돌 없음. LOCK-MM-07은 임베딩 차원만 규정, 해시 알고리즘 정본 없음. V2의 xxhash64 전환은 성능 목적의 정당한 선택. 양 문서에 각자 명시돼 있어 표기 일관성만 유지하면 됨
5. **[KEEP]** `docs\sot 2\3-2_Multimodal-Processing\02_audio-processing\audio_safety_v2.md`:167 (실측: constitutional_ok = True 선초기화, L172-177 denied시 raise) — GATE 4에서 constitutional_ok를 True로 선초기화하고 denied 판정 시에만 raise하는 변수 초기화 패턴
   - 선택지: (a) 현행 True 초기화+denied raise (b) False 초기화+승인시 True 전환 (c) 3-상태(pending/ok/denied)
   - 판정: KEEP — 분류기 호출(L168 await) 실패는 예외 전파로 흐름이 중단되므로 R-05-7 fail-safe=reject와 실질 모순 없음. 변수 초기화 방향은 코딩 스타일 선택. 구현 시 (b) 패턴이 더 방어적이라는 권고만 부기
6. **[KEEP]** `docs\sot 2\3-2_Multimodal-Processing\02_audio-processing\voice_chat_v2.md`:191-192 (실측: 'Claude Sonnet 4.6'/'Claude Opus 4.7'/'Claude 4.7 native') — V2/V3 단계 모델명을 forward-looking placeholder('Claude Sonnet 4.6/Opus 4.7')로 표기하는 명명 컨벤션
   - 선택지: (a) 현행 placeholder 버전명 (b) 실재 모델 ID 핀 고정(claude-sonnet-4-20250514 등) (c) 추상 티어명(haiku/sonnet/opus tier)
   - 판정: KEEP — 상세명세 L112의 모델 ID는 V1 기준이고 본 표는 V2/V3 미래 단계 표기라 직접 모순 아님(정본 우선순위상 본문 간 충돌 불성립). 도메인 전반 일관 사용 확인. 구현 착수 시점에 실 모델 ID로 핀 고정할 것만 권고
7. **[KEEP]** `docs\sot 2\3-2_Multimodal-Processing\02_audio-processing\stt_engine.md`:117-120 (실측: streaming→deepgram-nova-2 단일, google-stt-v2는 비스트리밍 한국어 분기) — 실시간(streaming) STT를 Deepgram 단일 경로로 강제하고 Google STT v2 실시간 폴백을 두지 않는 라우팅 정책
   - 선택지: (a) 현행 Deepgram 단일 실시간 경로 (b) Google STT v2 streaming 폴백 추가 (c) prefer_local 무시하고 비용 기준 동적 선택
   - 판정: KEEP — E4 라우팅 표('한국어 실시간=Deepgram')와 코드가 정합하며 finding 스스로 '이 논리는 실제로 문제없으나'로 인정. 실시간 폴백 추가는 가용성 요구가 정본화될 때 검토할 설계 선택
8. **[KEEP]** `docs\sot 2\3-2_Multimodal-Processing\04_document-generation\document_generation.md`:453 (write), 479/483 (실측: 'syntax 오류→rollback (write 전 백업)', '.bak 후 적용, 실패 시 자동 복구') — inline_comments에서 LLM 출력의 사전(pre-write) syntax 검증 대신 .bak 백업+사후 rollback으로 안전성을 확보하는 쓰기 전략
   - 선택지: (a) 현행 백업+사후 rollback (b) write 전 AST/syntax 검증 게이트 (c) diff 프리뷰+사용자 승인
   - 판정: KEEP — E5에 syntax 오류 rollback 폴백이 명시돼 있어 무방비 덮어쓰기가 아님. 사전검증 vs 사후복구는 정본 요구 없는 설계 선택. 시크릿 주입 방어용 정적 스캔 추가는 권장 노트
9. **[KEEP]** `docs\sot 2\3-2_Multimodal-Processing\04_document-generation\translation_prototype_v2.md`:187 (실측: confidence=0.92 고정 반환) — 프로토타입 단계에서 번역 confidence를 0.92 고정값으로 반환하는 품질지표 단순화
   - 선택지: (a) 현행 고정 0.92 (b) 엔진별 기본값 테이블 (c) COMET/품질추정 모델 연동 동적 산출
   - 판정: KEEP — 파일 자체가 prototype 명세이고 confidence 산출 방식에 대한 정본 요구 없음(엔진 분기·else 폴백은 현행본에서 이미 보완 확인 L161-162). 정식화 시 (b)→(c) 단계 도입 권장
10. **[KEEP]** `docs\sot 2\3-2_Multimodal-Processing\05_cross-modal-search\caching_optimization_v2.md`:88-91 (실측: scan_recent(method, limit=100) + 선형 cosine 루프) — V2 시맨틱 캐시 매칭을 최근 100건 선형 코사인 스캔으로 구현하고 V1의 Qdrant ANN을 쓰지 않는 알고리즘 선택
   - 선택지: (a) 현행 recent-100 브루트포스 (b) V1 방식 Qdrant ANN 인덱스 (c) 하이브리드(소규모 선형→임계 초과 시 ANN)
   - 판정: KEEP — 캐시 규모가 작은 V2 초기 단계의 단순성 우선 선택으로 합리적이며 정본 위반 없음(테넌트 격리 L79는 이미 반영 확인). 히트율 60% 주장 검증과 규모 증가 시 (b) 전환 트리거를 운영 지표로 명시할 것 권고
11. **[KEEP]** `docs\sot 2\3-2_Multimodal-Processing\06_multimodal-dialog\computer_use_agent_v2.md`:161 (실측: req.target_app == 'hts' 조건으로 전 step 3-Gate) — HTS 대상 작업은 읽기 전용 액션 포함 모든 step에 3-Gate 사용자 확인을 강제하는 보수적 안전 정책
   - 선택지: (a) 현행 전 step 게이트(과차단 감수) (b) 쓰기/주문성 액션만 게이트 (c) 최초 1회 세션 게이트+위험 액션별 게이트
   - 판정: KEEP — L65 '읽기 전용 기본'은 기능 기본값 서술이지 게이트 면제 정본이 아님. 금융 도메인에서 over-blocking은 안전 측으로 기우는 정당한 선택. UX 요구가 정본화되면 (b) 완화 검토
12. **[KEEP]** `docs\sot 2\3-2_Multimodal-Processing\06_multimodal-dialog\cost_accessibility_v2.md`:268-273 (실측: all>=70 ∧ all>=85(비latency) ∧ latency>=90 ∧ weighted>=85) — pass_v2에 수학적으로 포섭되는 V1 base 게이트(>=70)를 명시적으로 중복 유지하는 방어적 표현
   - 선택지: (a) 현행 중복 유지(V1 계승 가독성) (b) >=70 절 제거 (c) 주석으로만 V1 계승 표기
   - 판정: KEEP — 기능적으로 무해한 dead clause이며 'V1 base' 주석(L269)으로 계승 의도를 문서화하는 표현 선택. 정본 모순 없음. 코드 생성 시 린트 경고 가능성만 인지
13. **[KEEP]** `docs\sot 2\3-2_Multimodal-Processing\05_cross-modal-search\multimodal_rag_v2.md`:119-122 (실측: CLIP 0.4 + transcript 0.4 + audio 0.2 고정, audio 미요청 시 재정규화 없음) — search_av 모달 융합 가중치를 0.4/0.4/0.2 고정으로 두고 부재 모달리티 가중치를 재분배하지 않는 랭킹 설계
   - 선택지: (a) 현행 고정 가중치 (b) 존재 모달리티 합=1 재정규화 (c) 쿼리 적응형 가중치 학습
   - 판정: KEEP — 동일 쿼리 내 모든 후보가 균일하게 deflate되므로 상대 랭킹은 불변, 실해는 절대 score 해석에 한정. 가중치 값 자체는 정본 규정 없는 선택. score를 절대 임계와 비교하는 소비자가 생기면 (b) 도입
14. **[KEEP]** `docs\sot 2\3-2_Multimodal-Processing\06_multimodal-dialog\memory_integration_v2.md`:115-119 (실측: 동의 게이트 L116 존재, L117 복사 승격 — 원본 L1/L2 demote 없음) — L3 자동 승격을 '복사' 방식으로 수행하고 원본 L1/L2 사본을 demote/삭제하지 않는 계층 보존 정책
   - 선택지: (a) 현행 copy-promote(L1은 TTL 7일 자연 만료) (b) move-promote(원본 즉시 제거) (c) 원본에 promoted 마커+GC
   - 판정: KEEP — 사용자 동의 게이트(L116)는 이미 반영돼 객관결함부는 해소. 잔여 쟁점인 중복 보관은 L1 TTL 만료로 수렴하는 보존 정책 선택이며 정본 요구 없음. L2→L3 중복은 스토리지 비용 관점에서 idempotency 키 추가 권장
15. **[KEEP]** `docs\sot 2\3-2_Multimodal-Processing\06_multimodal-dialog\memory_integration_v2.md`:133-138 (실측: image .4 + audio .2 + video .3 + text .1 = 1.0) — ContextBudgetV2 모달별 토큰 가중치를 합 1.0으로 배분하고 응답 예약분을 본 스키마에서 따로 두지 않는 할당 설계
   - 선택지: (a) 현행 합 1.0 + peer adjust_context 위임 (b) V1식 reserved_for_response 선공제 후 배분 (c) 가중치 합 0.9로 헤드룸 확보
   - 판정: KEEP — 실제 할당은 L140-144에서 integration_architecture_v2 §4.3 adjust_context에 위임되므로 예약 처리 위치의 선택 문제. 가중치 값 자체는 정본 규정 없음. 위임처에 response 예약이 없음이 확인되면 그때 (b)로 보정
16. **[KEEP]** `docs\sot 2\3-2_Multimodal-Processing\06_multimodal-dialog\cost_accessibility_v2.md`:228-239, 245 (실측: 모달별 P99 45s/120s 행 + L239 '통합 평균' ≤2s/≤5s + L245 통과기준) — 응답지연 SLA를 모달리티별 개별 P99(비디오 45s/120s 허용)와 '통합 평균' ≤2s/≤5s의 이중 구조로 정의하는 SLA 집계 방식
   - 선택지: (a) 현행 모달별 목표+통합평균 게이트 (b) 전 모달 hard P99 SLO 단일화 (c) 모달 그룹별(실시간/배치) SLO 분리
   - 판정: KEEP — 표가 L239에서 ≤2s/≤5s를 '통합 평균(모달리티별 평균)' 행으로 명시해 모달별 값과의 외형 모순은 집계 방식 선택으로 해소됨. 다만 L245 '전수'의 적용 범위(5모달 측정 대상에 비디오 포함 여부)를 한 줄 명확화할 것 권고
17. **[KEEP]** `docs\sot 2\3-2_Multimodal-Processing\02_audio-processing\tts_engine_v2.md`:104, 118, 136 (실측: assert est_cost<=cap / assert len<=25MB) — 의사코드 명세에서 비용·출력크기 게이트(LOCK-MM-06/-10)를 assert 문으로 표현하는 표기 컨벤션
   - 선택지: (a) 현행 assert 표기(명세 가독성) (b) if+raise PolicyViolation 명시 (c) 데코레이터/미들웨어 게이트 추상화
   - 판정: KEEP — 게이트의 존재와 임계값(LOCK 인용)은 정본과 정합하며, assert는 spec 의사코드의 압축 표기 선택. 단 구현 가이드에 'python -O에서 assert 비활성화되므로 프로덕션은 명시적 raise로 구현'을 부기할 것
18. **[KEEP]** `docs\sot 2\3-2_Multimodal-Processing\06_multimodal-dialog\integration_architecture_v2.md`:122-137 (실측: smart_routing 조기 return으로 user preference 분기 미도달; cycle/timeout 검색 0건) + task_planner_v2.md:77,125 (deadline_minutes 정의 후 미사용) — V2 라우팅/DAG 실행을 베스트에포트로 두는 범위 선택 — smart_routing을 user preference보다 우선하는 정책 순서, DAG cycle detection·per-step timeout·deadline_minutes 활용을 V2 범위에서 제외
   - 선택지: (a) 현행(smart routing 우선, DAG 견고성 기능 후속) (b) preference override를 smart routing 앞에 배치+deadline/cycle 검출 V2 포함 (c) preference를 smart routing score feature로 통합
   - 판정: KEEP — 라우팅 우선순위와 DAG 견고성 기능 범위는 RULE/PLAN/LOCK 어디에도 강제 정본이 없는 아키텍처 선택. 단 enable_user_preference=True 기본값이 실질 무효가 되는 점은 문서에 우선순위 1줄 명시를, deadline_minutes는 V3 활용 예정 표기를 권고

> notes: 재도출 결과 18/18로 원판정 앵커와 일치(짜맞춤 아님 — T8-277과 MP-AUD-017은 동일한 DAG 견고성 범위 선택이라 1건 통합, MP-AUD-016과 같은 항목군). 분류 근거: (1) mf_in 객관결함 28건+unconfirmed 1건 및 동일 finding(clc/tight/GPT 중복 포함) 전부 제외. (2) verify=refuted 2건(T8-002 월간게이트, T8-062 speaker_verified) 제외. (3) 디스크 실측 반박 제외: T8-103(stt_engine.md L108에서 16kHz mono PCM 정규화 선행 — 포맷차 해시분기·스트리밍 캐시불가 주장 무효), T6-361/MP-AUD-002(CONFLICT_LOG가 V1/V2 모두 ViT-L/14 768d로 확정한 resolved conflict 사안). (4) 단순 표기/stale 인용 제외: T6-005(줄수 stale), T6-029(KPI 줄번호 오인용), T8-276(Step 4 번호 누락), T8-336(환율 반올림), T8-350·MP-AUD-007(WER 라벨), T8-365(단위 주석), T6-094(표현 과장), MP-AUD-024/025

### 3-3_PKM-Knowledge-Management (17건)

1. **[KEEP]** `docs\sot 2\3-3_PKM-Knowledge-Management\01_knowledge-capture\rss_newsfeed.md`:152 — 피드 아이템과 노트의 추적 관계를 1:1(대표 후보 cands[0]만 note_id로 기록)로 설계 — 나머지 후보는 그래프에는 삽입되되 피드 추적에서 제외.
   - 선택지: (a) 현행: 대표 후보 1건만 note_id 기록 (b) FeedItem.note_id를 list로 바꿔 전 후보 추적 (c) 별도 매핑 테이블
   - 판정: KEEP — 정본 위반 없음(LOCK-PKM 무관). FeedRunResult/FeedItem 스키마가 note_id 단수로 일관 설계돼 있고 후보는 그래프에 보존되므로 대표-노트 1:1은 합리적 추적 단순화. 전 후보 추적 필요 시 스키마 확장으로 충분.
2. **[KEEP]** `docs\sot 2\3-3_PKM-Knowledge-Management\01_knowledge-capture\email_message_extraction.md`:160 — Gmail OAuth scope를 gmail.readonly + gmail.metadata 2종 조합으로 선언.
   - 선택지: (a) 현행: readonly+metadata 병기 (b) readonly 단독(본문 추출에 충분, 최소권한) (c) metadata 단독(본문 불가)
   - 판정: KEEP — readonly가 metadata의 상위집합이라 병기는 중복이지만 기능 결함이 아니며 정본(스코프 LOCK 없음) 무모순. 최소권한 원칙상 차기 정비 시 readonly 단독으로 축약 권장(본문 §4.5 본문추출 요건이 우선 근거).
3. **[KEEP]** `docs\sot 2\3-3_PKM-Knowledge-Management\01_knowledge-capture\voice_memo.md`:44 — 단일 음성메모 상한 max_duration_min 기본값을 30분으로 설정(mp3 인코딩 전제, 25MB 한도 내).
   - 선택지: (a) 현행: 30분(mp3 ≈ 25MB) (b) 13분(wav 16k mono 기준 보수치) (c) 포맷별 동적 상한
   - 판정: KEEP — 인라인 주석이 'mp3 ≈ 30분'으로 LOCK-MM-10(25MB, DESIGN LOCK) 충족 근거를 명시. wav 경로는 분할 처리로 흡수되므로 기본값 30은 LOCK 무모순의 합리적 값 선택.
4. **[KEEP]** `docs\sot 2\3-3_PKM-Knowledge-Management\02_knowledge-graph\auto_tagging_classification.md`:46 — TagBundle.type(유형 축) 어휘에 'fact','opinion'을 채택 — LOCK-PKM-08 카테고리 축과 동일 단어를 다른 축에서 재사용.
   - 선택지: (a) 현행: 두 축에서 동일 단어 허용 (b) type 축 어휘를 'factual_claim','subjective_view' 등으로 개명 (c) 접두사 네임스페이스
   - 판정: KEEP — LOCK-PKM-07은 5차원 구조만, LOCK-PKM-08은 카테고리 enum만 보호(AUTHORITY_CHAIN L46-47). type 축 어휘는 비LOCK 영역의 명명 선택이며 정본 무모순. 소비자 혼동 방지 주석 추가는 선택 사항.
5. **[KEEP]** `docs\sot 2\3-3_PKM-Knowledge-Management\01_knowledge-capture\screen_capture.md`:251 — 타임라인 시맨틱 검색의 CLIP 재랭킹 cosine threshold를 0.30으로 설정.
   - 선택지: (a) 현행: 0.30 (recall 우선) (b) 0.25~0.28 (더 관대) (c) 0.35+ (precision 우선)
   - 판정: KEEP — LOCK-PKM-06(0.7/0.85)은 중복감지 임계값으로 별개 관심사이며 타임라인 검색 임계값은 LOCK 비대상. FTS 1차필터+Top-50 절단이 결합돼 0.30은 recall 우선의 합리적 선택. 운영 데이터로 튜닝 가능한 IMPL-DETAIL.
6. **[KEEP]** `docs\sot 2\3-3_PKM-Knowledge-Management\02_knowledge-graph\graph_reasoning.md`:177 — GraphReasoningEscalation.hop_count 스키마 상한을 conint(le=8)로 — 런타임 max_hops=4(L88)의 2배 헤드룸 허용.
   - 선택지: (a) 현행: 스키마 le=8 / 런타임 4 (b) 스키마도 le=4로 일치 (c) 상한 제거
   - 판정: KEEP — 에스컬레이션은 path_explosion 등 한도 초과 상황을 기록하는 스키마이므로 런타임 한도(4)보다 큰 관측치를 담을 수 있어야 함. 스키마 헤드룸 le=8은 정본 무모순의 의도적 설계(원판정 verify에서도 결함 반박됨).
7. **[KEEP]** `docs\sot 2\3-3_PKM-Knowledge-Management\02_knowledge-graph\maturity_tracking.md`:225 — days_since_last_access를 별도 접근 이벤트 추적 대신 n.updated_at(쓰기 타임스탬프) 프록시로 산출.
   - 선택지: (a) 현행: updated_at 프록시 (read 시 write 부하 없음) (b) last_accessed_at 필드 신설+read마다 갱신 (c) 별도 접근 로그 테이블
   - 판정: KEEP — 정본에 접근 추적 방식 규정 없음. 로컬 단일사용자 환경에서 read-on-write 오버헤드를 피하는 프록시는 합리적 트레이드오프. 아카이브 제안 정밀도가 문제되면 (b)로 점진 전환 가능(스키마 수준 변경).
8. **[KEEP]** `docs\sot 2\3-3_PKM-Knowledge-Management\03_spaced-repetition\rag_optimization.md`:196-199, 247 — 신선도 가중을 fusion 직후 final_score에 혼합(E4)한 뒤 E5 source_priority boost를 동일 final_score에 곱하는 2단 직렬 가중 파이프라인.
   - 선택지: (a) 현행: (fusion⊕freshness)×priority 직렬 (b) fusion×priority 후 freshness 별도 적용 (c) 3요소 단일 선형결합
   - 판정: KEEP — LOCK-PKM-09(DESIGN LOCK)는 freshness 공식만 보호하며 L194에서 exp(-λ·age) 원문 그대로 사용. 가중 결합 순서는 비LOCK 랭킹 설계 선택이고 rank-then-boost는 표준 패턴. 의미 중첩은 가중치 튜닝으로 흡수 가능(원판정 verify에서도 결함 반박됨).
9. **[KEEP]** `docs\sot 2\3-3_PKM-Knowledge-Management\03_spaced-repetition\knowledge_statistics.md`:292 — review_score를 max(0, 100 - 밀린카드수×2)의 절대치 패널티로 산출(총량 비정규화, 50장에서 0점 포화).
   - 선택지: (a) 현행: 절대 패널티 (b) overdue/total 비율 정규화 (c) 로그 스케일 패널티
   - 판정: KEEP — 통계 표시용 점수 공식은 LOCK 비대상(LOCK-PKM-01~03은 SM-2 파라미터만 보호). '밀린 카드 50장=관리 실패'라는 절대 기준은 개인 PKM 맥락에서 방어 가능한 설계. 대규모 사용자 경험 데이터 확보 후 정규화 검토 가능.
10. **[KEEP]** `docs\sot 2\3-3_PKM-Knowledge-Management\03_spaced-repetition\knowledge_statistics.md`:408 — median_ef를 sorted[n//2] 상위 중앙값(짝수 길이 시 두 중앙값 평균 생략)으로 단순화.
   - 선택지: (a) 현행: 상위 중앙값 (b) statistics.median 진중앙값 (c) 분위수 라이브러리
   - 판정: KEEP — 대시보드 통계 표시값으로 EF 분포(1.3~2.5+)에서 상위/진중앙값 차이는 무시 가능 수준이며 정본 무모순. 단순화는 의도적 구현 선택(IMPL-DETAIL). 정밀도 요구 시 statistics.median 1줄 교체로 충분.
11. **[KEEP]** `docs\sot 2\3-3_PKM-Knowledge-Management\03_spaced-repetition\smart_reminder.md`:488 (cf. 235, 260) — 일일 복습 한도를 이원화 — SLA 절대상한 daily_review_limit=50(L488) vs 큐 기본값 DAILY_DEFAULT_LIMIT=20(L260)/max_cards=20(L235).
   - 선택지: (a) 현행: 상한 50 / 기본 20 이원화 (b) 단일값 통일 (c) 사용자 설정 단일 소스
   - 판정: KEEP — 두 값 모두 디스크 실존 확인. '최대(hard cap) 50 vs 기본(default) 20'은 모순이 아니라 표준적 한도 계층 설계이며 정본 무모순(원판정 verify에서도 결함 반박됨). 본문에 max-vs-default 관계 주석 1줄 추가하면 더 명확.
12. **[KEEP]** `docs\sot 2\3-3_PKM-Knowledge-Management\05_external-integration\personal_assistant.md`:199-201 — UserPreferenceProfile+RecentSummary+LongTermGoal을 매 요청 시스템 프롬프트에 자동 주입하되, 별도 인젝션 무해화(sanitization) 없이 #sensitive 태그 제외만 적용하는 신뢰 모델.
   - 선택지: (a) 현행: 자기 소유 PKM 데이터 신뢰 + sensitive 태그 제외 (b) 외부 동기화 유래 콘텐츠 무해화 필터 추가 (c) 주입 전 LLM 사전검사
   - 판정: KEEP — 정본 위반 없음. L201에 #sensitive/financial·medical 자동 제외(6-2 정책 소비)가 이미 명시돼 위협모델이 정의됨. 자기 소유 로컬 PKM의 신뢰 수준은 설계자 선택 영역. Notion/Obsidian 외부 유래 콘텐츠 비중 증가 시 (b) 보강 권장.
13. **[KEEP]** `docs\sot 2\3-3_PKM-Knowledge-Management\05_external-integration\predictive_surfing.md`:202 — investment 분기 관련성 식의 클램프 구조 — min(1.0, 0.6|0.1)+cat_bonus로 타 분기(가산 후 클램프)와 다른 식 구조 채택.
   - 선택지: (a) 현행: 분기별 상이한 클램프 위치 (b) 전 분기 가산-후-클램프 통일 (c) 공통 스코어 빌더 함수
   - 판정: KEEP — 최대치 0.6+0.2=0.8 ≤ 1.0으로 상한 위반이 실제로 발생하지 않아 기능 결함 아님. 분기별 식 구조는 스타일/설계 선택이며 정본 무모순. 일관성 차원에서 (b) 통일은 무해한 정비 후보.
14. **[KEEP]** `docs\sot 2\3-3_PKM-Knowledge-Management\PKM_KNOWLEDGE_MANAGEMENT_상세명세.md`:493 — Notion 양방향 동기화 충돌 전략으로 last_write_wins 채택(주석으로 manual_merge 대안 명시, 15분 polling 전제).
   - 선택지: (a) 현행: last_write_wins (b) manual_merge 전면 (c) version vector/ETag 낙관적 잠금
   - 판정: KEEP — 충돌 해소 전략은 정본 LOCK 비대상이며 단일 사용자 PKM에서 LWW는 단순성 우선의 방어 가능한 선택(주석이 manual_merge 옵션도 보존). 타임스탬프 문자열 비교 결함(mf_in i=36)은 별도 객관결함으로 이미 확정 — 전략 자체와 분리.
15. **[KEEP]** `docs\sot 2\3-3_PKM-Knowledge-Management\PKM_KNOWLEDGE_MANAGEMENT_상세명세.md`:481-504 — 상세명세 §7(V1 요약층)에는 OAuth 토큰 저장/갱신·레이트리밋 처리를 기술하지 않고 L3 정본(notion_sync.md)에 위임하는 문서 깊이 배분.
   - 선택지: (a) 현행: 요약층 생략 + L3 위임 (b) 상세명세에도 운영 명세 중복 기술 (c) cross-ref 한 줄 추가
   - 판정: KEEP — L3 정본 notion_sync.md가 토큰 KMS 참조(L90 access_token_ref '평문 금지', L98) 및 NOTION_RATE_LIMITED 정책(L340, L364)을 실제로 커버함을 실측 확인. 본문(L3) > 요약 스키마 우선순위상 운영 상세의 L3 단일화는 올바른 배치. (c) cross-ref 추가는 선택 정비.
16. **[KEEP]** `docs\sot 2\3-3_PKM-Knowledge-Management\01_knowledge-capture\screen_capture.md`:118, 215-223 — 암호화 범위를 스크린샷 PNG(at-rest 암호화)로 한정하고 FTS5 검색 테이블의 텍스트 필드(active_app/window_title/ocr_text/ui_narrative)는 평문 저장하는 보안 경계 설정.
   - 선택지: (a) 현행: 이미지만 암호화 + G-1~G-5 게이트/G-3 민감패턴 블러 선행 (b) SQLCipher 등 DB 전체 암호화 (c) 필드 단위 마스킹 후 색인
   - 판정: KEEP — 정본 위반 없음. G-3 민감패턴 블러가 OCR 전에 적용되고 G-5 opt-in·privacy_score 게이트가 존재(L158-164)하며, FTS 평문은 로컬 SQLite 검색 기능성을 위한 의도적 트레이드오프. 위협모델 상향 시 (b) DB 암호화가 자연스러운 강화 경로.
17. **[KEEP]** `docs\sot 2\3-3_PKM-Knowledge-Management\02_knowledge-graph\import_export.md`:33 — ImportRequest가 로컬 file_path 문자열을 직접 수령해 파서에 전달하는 로컬 우선(local-first) 임포트 입력 설계 — canonicalization/allowlist 미규정.
   - 선택지: (a) 현행: 로컬 경로 직접 수령 (b) 업로드 ID/격리 임시 핸들 간접화 (c) 경로 수령 + canonicalize/allowlist 검증 계층
   - 판정: KEEP — 로컬 단일사용자 데스크톱 앱의 자기 파일 임포트라는 신뢰 경계에서 경로 직접 수령은 방어 가능한 설계(GPT 원판정도 is_confident=false). 정본 무모순. 다중사용자/원격 노출 시나리오가 생기면 (c) 검증 계층 추가 권장.

> notes: 재도출 17건 = 원판정 앵커 17건과 정확히 일치(강제 짜맞춤 아님 — 독립 도출 후 일치 확인). 전수 처리 내역: (1) clc 70건+tight(부분집합)+GPT 12건 전수 스캔. (2) mf_in confirmed 39건과 동일/중복 제외 — T5-011(i=3 중복), T6-155/156(i=9), T6-176/177/186/187(i=10), T6-178/188/189(i=11), T6-200/T5-201(i=12) 등 LOCK-PKM-04/05 계열 전부 객관 확정분. mf_in unconfirmed 5건(T8-014/126/232/236/353)도 객관 분류분으로 제외. (3) 오탐 제외 8건: T8-009/015/016/044/143/292/326/349 — verify=refuted이며 주관 후보성 없음. T8-323은 직접 실측으로 반박: 05_external-integration/personal_wiki_publish.md 실존하여 종합계획서 §13.3(L2497)의 M-037 V3→05 배치가 디스크와 정합(M-046 writing_drafting.md, M-047 second_brain_dashboard.md도 05에 실존) — 

### 6-5_SDAR-System (17건)

1. **[KEEP]** `docs\sot 2\6-5_SDAR-System\01_five-layer-pipeline\repair.md`:633-638 — L13 쿨다운(60초) 검사 키를 다단계 수리 후보의 대표 액션(selected.steps[0].action_id) 하나로 잡은 쿨다운 키 입도 선택
   - 선택지: (a) 현행: step[0] 대표 액션만 검사 (b) 전 스텝 action_id 전수 검사 (c) plan_id 단위 쿨다운
   - 판정: KEEP (a) — DESIGN LOCK L13 정본(SDAR_SPEC §9.2)은 '동일 액션 반복 실행 간 60초'만 정의하고 다단계 후보의 키 범위는 미규정이므로 대표 액션 기준은 정본 무모순; 전수 검사로 강화하려면 DEFINED-HERE 등재가 선행돼야 함
2. **[KEEP]** `docs\sot 2\6-5_SDAR-System\01_five-layer-pipeline\repair.md`:903 — 분산 수리 Lock TTL을 1800초(30분 안전 상한)로 설정한 운영 파라미터 값 선택
   - 선택지: (a) 현행: TTL 1800s (b) 짧은 TTL(예: 300s)+갱신(heartbeat) (c) TTL 없이 명시적 해제만
   - 판정: KEEP (a) — LOCK L5(MAX_CONCURRENT_REPAIRS=1) 정본은 직렬화만 강제하고 TTL 값은 미규정; 1800s는 최장 수리+검증 시간을 덮는 합리적 crash-safety 상한이며 holder crash 시에도 TTL 만료로 자동 회복됨(영구 DoS 아님)
3. **[KEEP]** `docs\sot 2\6-5_SDAR-System\01_five-layer-pipeline\verification.md`:892,896,900 — VER-E012(관찰 기간 타임아웃) 에러코드를 EX-1(RepairResult 수신 불가)·EX-5(관찰 중 재시작)·EX-9(S5 타임아웃)에 공용하는 에러코드 분류 입도 선택
   - 선택지: (a) 현행: 관찰-중단 계열 1개 코드 공용 (b) 시나리오별 신규 코드 분리(VER-E013/E014 등)
   - 판정: KEEP (a) — 정본(SDAR_SPEC §2.6) 에러코드 체계에 1:1 분리 강제 규정 없음; 세 경우 모두 '관찰 불능/중단' 의미군으로 공용은 설계 재량이며, 분리가 필요해지면 코드 추가는 비파괴적 확장
4. **[KEEP]** `docs\sot 2\6-5_SDAR-System\02_state-machine\event_catalog.md`:85-86 — 수리 실패(repair.failed)도 S4→S5로 보내 롤백 판단을 검증 단계에 위임하는 verify-always 파이프라인 아키텍처 선택
   - 선택지: (a) 현행: 성공/실패 무관 S4→S5, 검증에서 롤백 판단 (b) 실패 시 S4에서 즉시 롤백/에스컬레이션 분기
   - 판정: KEEP (a) — SPEC §7.3 정본 전이가 '수리 완료→S5'이며 L85-86 트리거 컬럼에 '검증 단계에서 롤백 판단'이 명시된 의도된 설계; S4↔S5 진동은 L6(시간당 3회)로 유계
5. **[KEEP]** `docs\sot 2\6-5_SDAR-System\01_five-layer-pipeline\verification.md`:8 vs 508 — 파일 헤더 LOCK 매핑(L1,L8,L9,L11,L12,L13)에 본문 L508의 governance_summary가 인용하는 L18을 포함하지 않은 헤더 등재 범위 선택
   - 선택지: (a) 현행: 헤더에는 본 파일이 구현·집행하는 LOCK만 등재, 단순 인용은 제외 (b) 인용 LOCK까지 전부 헤더 등재
   - 판정: KEEP (a) — AUTHORITY_CHAIN §4 정본에 헤더 등재 범위 규정 없음; L18(Self-evo 보고)은 6-6 측 집행 LOCK이고 본 파일은 필드 출처 인용만 하므로 구현-LOCK만 등재하는 현행 컨벤션은 무모순
6. **[KEEP]** `docs\sot 2\6-5_SDAR-System\04_self-diagnosis\repair_action_catalog.md`:81-83 — 액션 카탈로그 총수를 '26 = 목록 ID 24(RA_001~014+RA_NEVER_01~10) + AR-L1 NOTIFY 2 명목'으로 세는 카운트 컨벤션 선택
   - 선택지: (a) 현행: 26 (24 ID + 2 명목, L83에 자체 문서화) (b) 24 (ID만 카운트) (c) AR-L1 NOTIFY 2건에 RA ID 부여 후 물리 26
   - 판정: KEEP (a) — SDAR_SPEC §3.1/§5.1 정본은 액션 총수를 LOCK하지 않으므로(§3.1은 위험도 범위만 서술) 카운트 방식은 설계 재량이며, L83 '카운트 정합 검증' 노트가 24+2 분해를 명시적으로 문서화해 자기일관성 확보
7. **[KEEP]** `docs\sot 2\6-5_SDAR-System\L3_COMPLETENESS_REPORT.md`:117, 300 — L3 리포트가 카탈로그의 26 카운트 컨벤션을 그대로 인용하되 괄호에는 ID 범위(24개분)만 약기한 인용 표기 선택
   - 선택지: (a) 현행: '26개 액션 (RA_001~RA_014 + RA_NEVER_01~10)' 약기 (b) 카탈로그 L83 분해('24 ID + AR-L1 NOTIFY 2 명목')를 병기
   - 판정: KEEP (a) 단 (b) 병기가 바람직 — 26은 카탈로그 §3(본문 정본)의 선언 카운트를 추종한 것이고 괄호는 ID 범위 약기이므로 정본 모순은 아님; 산술 오해 방지 위해 차기 갱신 시 '= 24 ID + 2 명목' 병기 권고
8. **[KEEP]** `docs\sot 2\6-5_SDAR-System\L3_COMPLETENESS_REPORT.md`:251 vs 313 (실측 26,315B/315L) — 리포트 자기 크기(byte/LF)를 측정 시점 스냅샷으로 본문에 박제하고 이후 append 시 갱신하지 않는 자기참조 크기 표기 컨벤션 선택
   - 선택지: (a) 현행: 측정 시점 스냅샷 보존 (append-only, 자기참조 크기는 필연적으로 stale) (b) 매 append마다 전수 재기입 (c) 크기 실측은 INDEX/외부 레지스트리에 위임
   - 판정: KEEP (a) — entry-gate 조건(≥300 LF)은 313/315 어느 값으로도 충족되어 판정 영향 0이고, 자기참조 크기의 사후 재기입은 그 자체가 크기를 바꾸는 순환 문제(6-6 도메인 SHA drift 선례)가 있어 스냅샷 보존이 합리적; live 값은 INDEX 위임 권고
9. **[KEEP]** `docs\sot 2\6-5_SDAR-System\L3_COMPLETENESS_REPORT.md`:148 — LOCK L1~L20 출처 정합(SDAR_SPEC §2/§7/… + Part2 §6.9 L5442-5461) 검증을 도메인 내부 grep set-accuracy 방식으로 수행하고 외부 SOT 원본 대조는 AUTHORITY_CHAIN에 위임한 검증 방법론 선택
   - 선택지: (a) 현행: 내부 set-accuracy + AUTHORITY_CHAIN 위임 (b) 리포트가 외부 SOT 원본까지 직접 byte 대조
   - 판정: KEEP (a) — 검증 깊이는 정본이 강제하지 않는 방법론 선택이고, per-LOCK 원본 §/L 매핑의 단일 정본은 AUTHORITY_CHAIN.md §4이므로 리포트의 위임 구조는 정본 우선순위와 정합; finding 자체도 '확인 불가'이지 오류 적발이 아님
10. **[KEEP]** `docs\sot 2\6-5_SDAR-System\SDAR_SYSTEM_구조화_종합계획서.md`:1821 vs 1443,1478-1480 — W-CB 충돌 해소(Option C RESOLVED)를 §9.3 원본 표 수정 대신 §7.5/§7.6/§7.R append 기록으로만 반영하는 append-only 문서 갱신 전략 선택
   - 선택지: (a) 현행: 원본 §9.3 표는 OPEN 표기 보존 + 후행 §7.5/§7.R 기록이 supersede (b) §9.3 표를 직접 RESOLVED로 갱신
   - 판정: KEEP (a) — CONFLICT_LOG.md v1.3(L198,226)이 'append-only 정책 엄수, 전환은 §7.3/§8.3 변동이력이 정본'을 명문화한 도메인 공식 컨벤션이며, 현행 충돌 상태의 정본은 CONFLICT_LOG v1.3(OPEN 0/RESOLVED 8)으로 무모순
11. **[KEEP]** `docs\sot 2\6-5_SDAR-System\SDAR_SYSTEM_구조화_종합계획서.md`:461 vs 1818-1821 — SPEC §7.1 S6_DONE vs 부록 A ESCALATED 불일치를 CONFLICT_LOG 정식 등재 대신 02_state-machine/_index.md:68의 XREF-S6-05 약칭(alias) 매핑 문서화로 해소한 충돌 처리 메커니즘 선택
   - 선택지: (a) 현행: XREF-S6-05 alias 매핑으로 비충돌 확정(ESCALATED=S6_DONE 하위 경로, 편의 표기) (b) CONFLICT_LOG에 정식 ID 등재 후 RESOLVED 처리
   - 판정: KEEP (a) — 실측상 02/_index.md:68과 state_transitions.md:61이 'SPEC §7 원본 S0~S6, ESCALATED는 편의상 7상태 표기'로 정본 모델을 보존·문서화해 실질 충돌이 소멸했으므로 정식 등재는 형식 차이; 차기 CONFLICT_LOG 갱신 시 XREF-S6-05를 RESOLVED 행으로 소급 등재하면 추적성 개선
12. **[KEEP]** `docs\sot 2\6-5_SDAR-System\SDAR_SYSTEM_구조화_종합계획서.md`:1958-1981 — 부록 A.1 ASCII 다이어그램에 메인 플로우만 그리고 DIAGNOSING→ESCALATED(RCA 타임아웃)·PRESCRIBING→ESCALATED(5-Gate REJECT) 예외 엣지는 A.3 표로 분리한 다이어그램 입도 선택
   - 선택지: (a) 현행: A.1=정상 경로 중심 + A.3=예외 전이 표 분리 (b) A.1에 14경로 전부 표기
   - 판정: KEEP (a) — 전이 전수(14경로)의 정본은 state_transitions.md L3 매트릭스이고 부록은 개요 시각화이므로 가독성 위한 분리 표기는 설계 재량; A.1에 'A.3 예외 전이 별도' 캡션 추가 권고
13. **[KEEP]** `docs\sot 2\6-5_SDAR-System\SDAR_SYSTEM_구조화_종합계획서.md`:1955-1981 — 부록 A.1에서 ESCALATED를 별도 7번째 상태처럼 표기하는 편의 표기 선택 (정본 모델은 S0~S6, ESCALATED=S6_DONE 하위 경로)
   - 선택지: (a) 현행: 편의상 별도 표기 + XREF-S6-05로 정본 관계 명문화 (b) 다이어그램을 S0~S6 정식 명칭으로 재작성
   - 판정: KEEP (a) — 02_state-machine/_index.md:68 및 state_transitions.md:61의 XREF-S6-05가 '편의상 7번째 상태로 별도 표기, SPEC §7 원본은 S0~S6'를 명시해 정본 우선순위(본문 정본=SPEC §7.1) 보존하의 표현 선택임이 문서화됨
14. **[KEEP]** `docs\sot 2\6-5_SDAR-System\SDAR_SYSTEM_구조화_종합계획서.md`:2000-2003 (cf. 460) — 부록 A.3 예외 전이표에 프로세스 레벨 타임아웃(DH-SDAR-T1 120초)만 표기하고 SPEC §7.2 S2 상태 레벨 60초(1차 경고)는 생략한 부록 요약 범위 선택
   - 선택지: (a) 현행: A.3=에스컬레이션 유발 타임아웃만 표기, 60초/120초 이중 타임아웃 상세는 본문 위임 (b) A.3에 60초 상태 타임아웃 병기
   - 판정: KEEP (a) — 60초(상태 레벨 경고) vs 120초(프로세스 레벨 DH-SDAR-T1)의 스코프 차이는 plan L460에 명시돼 있고 상세 정본은 state_transitions.md/SPEC §7.2이므로 부록 요약 생략은 재량; 혼동 방지 위해 A.3에 '상태 레벨 60초 경고는 SPEC §7.2 참조' 각주 권고
15. **[KEEP]** `docs\sot 2\6-5_SDAR-System\SDAR_SYSTEM_구조화_종합계획서.md`:1958-1981, 2000-2005 (cf. 465) — 부록 다이어그램/예외표에 CATEGORY E 즉시 에스컬레이션(S2→S6, L15/ISS-4) 엣지를 생략하고 본문(§ P0-4 절차 5 ISS-4, L465)과 event_catalog.md에 위임한 안전 경로 표기 위치 선택
   - 선택지: (a) 현행: CATEGORY E 경로는 본문/이벤트 카탈로그 정본에만 명시, 부록 생략 (b) A.1/A.3에 CATEGORY E S2→S6 엣지 추가
   - 판정: KEEP (a) — CATEGORY E S2→S6 일관성은 L3 리포트 §6에서 'S2→S6 15+ matches' 전수 검증돼 본문 정본 무결이고 부록 표기 여부는 시각화 재량; 다만 안전-critical 경로이므로 차기 갱신 시 (b) 추가가 바람직
16. **[KEEP]** `docs\sot 2\6-5_SDAR-System\04_self-diagnosis\gate_integration.md`:193, 208-213, 224-225, 240, 343-352 — SDAR ON 3중 검증에서 AR-L4 성공 샘플 부족(n<20) 시 무기한 수동 모드(AR-L2 캡)를 유지하는 fail-closed 콜드스타트 정책 선택 — 신규 환경 bootstrap 경로(shadow run/staging 샘플 등)는 미규정
   - 선택지: (a) 현행: INSUFFICIENT_SAMPLES → 수동 모드 유지 + '샘플 누적 중' 알림 (보수 기본값) (b) shadow/dry-run AR-L4 샘플을 성공률 산정에 포함하는 bootstrap 경로 신설 (c) 수동 승인 trial run을 표본 인정
   - 판정: KEEP (a) — 종합계획서 §6.2 ISS-8 정본(W3 'V2→V3 전환 시 AR-L4 안전성' 대응)은 3중 검증 ALL PASS 전 AR-L2 캡을 의도된 안전장치로 규정하며 fail-closed는 정본 취지에 부합; bootstrap 경로 신설은 별도 Decision 사안이지 현행 스펙 결함 아님
17. **[KEEP]** `docs\sot 2\6-5_SDAR-System\04_self-diagnosis\gate_integration.md`:247-250, 274-275 — 스냅샷 복원 성공률 조건을 100%(한 건도 실패 X) 임계 + 주 1회 5건 dry-run 스케줄로 설계하되 AR-L4 조건과 달리 최소 표본 수(MIN_SAMPLE_SIZE)를 두지 않은 임계값 설계 선택
   - 선택지: (a) 현행: threshold 100% + total==0이면 NO_DATA 차단, 주간 5건 dry-run으로 표본 자연 누적 (b) AR-L4와 동일하게 MIN_SAMPLE_SIZE 명시 + 미달 시 INSUFFICIENT_SAMPLES
   - 판정: KEEP (a) — 정본(종합계획서 §6.2 ISS-8 + LOCK L8)은 '스냅샷 복원 100%'만 규정하고 표본 하한은 미규정; NO_DATA가 verify_all에서 PASS가 아니므로 무표본 통과는 차단되고, 30일 lookback × 주 5건 dry-run이면 실질 표본 ~20건 확보되어 위험 낮음 — 표본 하한 명시는 개선 옵션이지 결함 아님

> notes: 입력 4파일 전수 판독. raw 55건(clc 43 + GPT 12; tight 33건은 전부 clc 부분집합으로 별도 신규 없음) → (1) mf_in 객관결함 25건 제외: clc 17건(T8-017/T6-028/T6-030/T8-054/T8-055/T8-066/T8-072/T8-083/T8-084/T8-089/T8-113/T6-138/T6-141/T6-156/T8-167/T8-174/T8-178)+GPT 8건(SDAR-AUDIT-001~005/007/008/011)으로 1:1 매핑 확인. (2) verify="refuted" 오탐 11건 제외(T8-001/012/035/073/091/092/111/139/149/157/177). (3) GPT-012(26 카운트)는 clc T6-110/T8-127과 동일 이슈로 T6-110 항목에 source 병합. 잔여 17건 = 원판정 주관 카운트 17과 정확히 일치(강제 짜맞춤 없이 자연 도출). 전 항목 디스크 실측 file:line 확인 완료. 전건 KEEP — CHANGE 요건(정본 모순)에 해당하는 항목 없음: 핵심 근거는 (i) repair_action_catalog.md L83의 24+2명목=26 컨벤션

### 4-4_MLOps-LLMOps (16건)

1. **[KEEP]** `docs\sot 2\4-4_MLOps-LLMOps\01_prompt-versioning\ab_test_framework.md`:88, 248-249 — traffic_split 상한을 0.5 하드캡(ValidationError)으로 차단할지, 0.0~1.0 허용+0.5 초과 경고 로그로 둘지의 정책 선택 (실측: L88 '상한/하한은 자유, 0.5 초과 시 경고' vs L248-249 'le=0.5 ... 초과 시 ValidationError').
   - 선택지: (a) 스키마 하드캡 le=0.5 차단(현행) / (b) le=1.0 허용 + 0.5 초과 경고 로그(L88 서술)
   - 판정: KEEP (a) — 상위 SoT 90/10은 기본값이고 C-02는 '상세명세 우선(§A-5 가변)'으로 해소됐으며, 하드캡은 §A-5 범위의 보수적 협소화로 정본 무모순(challenger>50%는 A/B 자체를 훼손); L88 '경고' 문구만 차단 정책 기술로 후속 정비 권고.
2. **[KEEP]** `docs\sot 2\4-4_MLOps-LLMOps\01_prompt-versioning\ab_test_framework.md`:206, 363, 496-553 — min_detectable_effect(MDE)를 decide_winner 판정 게이트에 포함하지 않고 표본설계(power 계산)용으로만 쓰는 선택 (실측: L206 MDE 필드, L363 INCONCLUSIVE 주석 'effect_size 미달', L510-538 판정은 p_eff+방향만).
   - 선택지: (a) MDE는 표본설계용, 판정은 p+방향(현행) / (b) effect_size<MDE 시 Winner.INCONCLUSIVE 반환 추가
   - 판정: KEEP (a) — DESIGN LOCK(LOCK-ML-04)은 α=0.05만 고정하고 MDE 게이팅은 어떤 정본도 요구하지 않으며, MDE를 검정력/표본 계산에 한정하는 것은 표준적 통계 설계; 단 L363 주석과 코드의 표현 정합은 후속 정비 권고.
3. **[KEEP]** `docs\sot 2\4-4_MLOps-LLMOps\01_prompt-versioning\dspy_optimization.md`:660 (상세명세.md:159-163 교차) — LOCK-ML-05 5규칙 전부를 promote 동시충족 하드게이트로 적용하는 선택 — 상세명세 §B-5는 p95_latency_ms/cost_per_interaction을 severity='warn'으로 분리 (실측: dspy L660 '동시 충족 필요', 상세명세 L162-163 warn).
   - 선택지: (a) 5규칙 전부 하드게이트(현행 dspy promote gate) / (b) §B-5대로 block 3 + warn 2 분리
   - 판정: KEEP (a) — AUTHORITY L33 LOCK-ML-05는 5개 임계값만 정의하고 게이트 severity는 미규정이므로 SOT(warn)보다 엄격한 승급 게이트는 정본 위반 없는 보수적 설계 선택; 완화하려면 §B-5 severity 체계로 회귀하는 명시 Decision 필요.
4. **[KEEP]** `docs\sot 2\4-4_MLOps-LLMOps\01_prompt-versioning\promptfoo_test_spec.md`:326-329, 574 — 테스트 케이스 최소 10건 강제를 Pydantic Field(min_length=1)가 아닌 validate_config() 앱 레이어에 두는 검증 레이어링 선택 (실측: L326-329 min_length=1 + '최소 10건' description, L574 len<10 검사).
   - 선택지: (a) 스키마 관대(min_length=1) + validate_config 강제(현행) / (b) Field min_length=10 + 카테고리 최소수 model_validator 승격
   - 판정: KEEP (a) — '최소 10건'은 종합계획서 1-3 절차 5의 운영 절차 요건이지 스키마 LOCK이 아니며, 부분 구성(드래프트) 직렬화를 허용하고 실행 직전 검증하는 레이어링은 합리적 선택; validate_config 호출을 run 경로에 필수화하는 것만 권고.
5. **[KEEP]** `docs\sot 2\4-4_MLOps-LLMOps\01_prompt-versioning\promptfoo_test_spec.md`:838-840 (ab_test_framework.md:462 교차) — promptfoo 오프라인 A/B 브릿지의 검정을 기본 ttest_ind(Student, equal_var=True)로 두는 알고리즘 선택 — ab_test_framework §6.2 canonical 매핑은 Welch(equal_var=False) (실측: promptfoo L840, ab L462).
   - 선택지: (a) 기본 ttest_ind(현행 브릿지) / (b) Welch equal_var=False로 ab_test_framework §6.2와 정렬
   - 판정: KEEP (a)이되 (b) 정렬 권장 — 검정 방법은 RULE/PLAN/LOCK 어디에도 고정돼 있지 않은 알고리즘 선택(LOCK-ML-04는 α만 고정)이라 정본 모순은 아니나, 본문 정본인 ab_test_framework §6.2가 연속형에 Welch를 canonical로 두므로 차기 정비 시 equal_var=False 정렬이 바람직.
6. **[KEEP]** `docs\sot 2\4-4_MLOps-LLMOps\01_prompt-versioning\promptfoo_test_spec.md`:820-836 (feedback_pipeline.md:590 교차) — 오프라인 테스트케이스 점수 리스트를 A/B 유의성 브릿지 표본으로 쓰고 min_sample(500) 충족 여부는 게이트가 아닌 informational 플래그(min_sample_met)로 반환하는 보조도구 설계 선택 (실측: L824 '>= 500 (§F-2)', L829-836 플래그 산출).
   - 선택지: (a) 오프라인 브릿지=보조 신호, min_sample_met 정보 제공(현행) / (b) §A-6 트래픽 기반 A/B로만 유의성 판정 일원화
   - 판정: KEEP (a) — feedback_pipeline §11.1 reconcile(L590)이 min_sample=500을 'RLHF-lite 전용 인스턴스값, CONFLICT 아님'으로 정본 확정했으므로 오프라인 브릿지가 이를 게이트로 삼지 않는 현행 설계는 정본 정합; 승급 판정 자체는 §A-6 트래픽 A/B가 담당.
7. **[KEEP]** `docs\sot 2\4-4_MLOps-LLMOps\01_prompt-versioning\version_tagging_rollback_spec.md`:360-365 — auto_detect_change_type의 무변경(no-change) 케이스를 별도 NO_CHANGE 상태 대신 PATCH 폴백으로 처리하는 폴백 전략 선택 (실측: L364-365 '변경 없음 (이론상 도달하지 않아야 함) return ChangeType.PATCH' — 도달 불가를 문서가 자인).
   - 선택지: (a) 방어적 PATCH 폴백(현행, 호출부에서 동일성 사전 차단 전제) / (b) NO_CHANGE enum 추가 + tag() 거부
   - 판정: KEEP (a) — LOCK-ML-02 SemVer 규칙은 변경 유형 3종만 정의하고 무변경 처리는 미규정이며, '이론상 도달하지 않는' 경로의 안전 폴백은 정본 무모순 설계 선택; 빈 diff 이력 오염이 실측되면 그때 (b) 승급 검토.
8. **[KEEP]** `docs\sot 2\4-4_MLOps-LLMOps\01_prompt-versioning\version_tagging_rollback_spec.md`:426-437 — rollback()에서 target_version==현재 production 가드를 두지 않아 동일 버전 재지정(no-op 롤백)을 허용하는 멱등성 정책 선택 (실측: L427-428 current→deprecated 후 L432 검사라 동일 버전도 통과).
   - 선택지: (a) 동일버전 롤백 허용(멱등 재고정, 현행) / (b) from==to 시 ValueError 거부 가드 추가
   - 판정: KEEP (a) — 상세명세 §A-4 4단계 절차는 동일버전 금지를 규정하지 않으며 no-op 롤백은 상태를 훼손하지 않는 무해한 재고정; RollbackEvent 노이즈가 문제되면 가드 추가는 자유 선택.
9. **[KEEP]** `docs\sot 2\4-4_MLOps-LLMOps\02_model-evaluation\model_catalog_spec.md`:661-704 — CatalogUpdater를 Phase 1 수동 갱신 스텁 + 로컬 단일 작성자 전제로 두고 파일락/원자쓰기(temp+rename)/자동백업을 명세하지 않는 아키텍처 선택 (실측: L663 'Phase 1 수동 갱신 + 구조 확립', L666-691 스텁).
   - 선택지: (a) 로컬 단일 프로세스 단일 작성자, Phase 2 자동화 시 보강(현행) / (b) 파일락+원자쓰기+백업 즉시 명세
   - 판정: KEEP (a) — VAMOS는 로컬 단일 사용자 앱으로 동시 작성자가 구조적으로 없고 문서가 Phase 1 수동/Phase 2 자동화 단계를 명시했으므로 정본 무모순 단계화 선택; Phase 2(2-1 webhook 연동) 진입 시 원자쓰기 명세 추가 권고.
10. **[KEEP]** `docs\sot 2\4-4_MLOps-LLMOps\03_drift-detection\drift_engine.md`:541, 595-596 — M7(응답지연) 자동대응 트리거(>5s)를 알림 임계(LOCK-ML-06 M7 >5s)와 동일값으로 두는 임계값 선택 — M4는 알림 10%/자동대응 30%로 의도적 분리 (실측: L541 'LOCK-ML-06 M7 임계와 동일' 명시, L595-596 >5000 시 _enforce_cache).
   - 선택지: (a) M7 알림=자동대응 동일 임계 5s(현행, 캐시강화는 저위험 액션) / (b) M4처럼 자동대응 임계 분리 상향
   - 판정: KEEP (a) — 상세명세 §C-4 L217 정본 자체가 '응답 지연 급등: p95 > 5s'를 자동대응 조건으로 동일하게 규정하므로 현행은 정본 verbatim이며, 캐시 강화/배치 축소는 롤백류와 달리 가역적 저위험 대응이라 동일 임계가 합리적.
11. **[🔧CHANGE]** `docs\sot 2\4-4_MLOps-LLMOps\03_drift-detection\drift_engine.md`:539 vs 568-574 (상세명세.md:215 교차) — QoD CRITICAL 자동 롤백을 운영자 설정(auto_rollback) 없이 항상 실행할지, 정본 §C-4대로 'auto_rollback=true 설정 시'로 조건화할지의 정책 선택 (실측: L539 표는 정본 조건 보존, L556-574 __init__에 설정 부재 + respond()는 무조건 rollback).
   - 선택지: (a) CRITICAL 시 무조건 자동 롤백(현행 코드) / (b) §C-4 정본대로 auto_rollback 설정 게이트(현행 표)
   - 판정: CHANGE → (b) — 상세명세 §C-4 L215 정본이 'auto_rollback=true 설정 시' 조건을 명시하고 본 문서 §7.1 표(L539)도 이를 보존하는데 코드만 조건을 누락해 정본·자기 표와 모순; __init__에 auto_rollback: bool = True 필드 추가가 동반 필요하며, (b)/(c) 재평가·에스컬레이션을 무조건 유지하려면 롤백 액션만 분리 게이트하는 후속 정리 권고.
12. **[KEEP]** `docs\sot 2\4-4_MLOps-LLMOps\04_canary-deployment\canary_router.md`:440-444, 1139 — CanaryRouter에 promote() 메서드를 두지 않고 단계 전환을 외부 오케스트레이터 호출에 위임하는 API 설계 선택 (실측: 클래스 메서드는 route/judge/rollback/pause 4종, L1139 '후속 promote() (별도 외부 호출)' 명시 — 의도된 분리).
   - 선택지: (a) judge()=판정만, 전환은 외부 promote() 위임(현행, 판정/실행 책임 분리) / (b) 클래스 내 promote() 추가
   - 판정: KEEP (a) — L1139가 외부 호출 설계를 명시 문서화했고 어떤 정본도 promote()의 클래스 내 구현을 요구하지 않으며, 판정(judge)과 실행(promote)의 책임 분리는 §3 수동 개입(엔지니어/관리자 승인) 단계와도 정합하는 아키텍처 선택; 외부 promote() 계약 명세 1개 추가만 권고.
13. **[KEEP]** `docs\sot 2\4-4_MLOps-LLMOps\03_drift-detection\guardrails_input_rails.md`:80-95 (output/dialog/retrieval rails 동형) — 4종 Guardrails POST API에 호출자 인증/인가/rate limit 계약을 명세하지 않고 로컬 전용(local_only, R-17-5) + 접근제어 6-2 위임 전제로 두는 아키텍처 선택 (실측: L80 storage local_only, L93 M-5 '접근 제어 (6-2)').
   - 선택지: (a) 로컬 단일 사용자 전제, 인증은 6-2 보안 도메인 위임(현행) / (b) 각 Rails API에 인증·identity·rate limit·fail-closed 자체 명세
   - 판정: KEEP (a) — R-17-5/LOCK-ML-12 로컬 전용 아키텍처에서 네트워크 노출이 없는 로컬 IPC성 API에 자체 인증 계약을 강제하는 정본은 없고 M-5가 접근제어를 6-2로 명시 위임했으므로 무모순 선택; fail-closed는 IR_E01에 이미 명세됨.
14. **[KEEP]** `docs\sot 2\4-4_MLOps-LLMOps\04_canary-deployment\canary_router.md`:631-634 (상세명세.md:240 교차) — 카나리 트래픽 버킷팅 해시를 상세명세 §D-2 의사코드의 hash(user_id)%100 대신 SHA-256(user_id:deployment_id) 첫 4바이트 %100으로 구현하는 알고리즘 선택 (실측: canary_router L631-634, 상세명세 L240).
   - 선택지: (a) SHA-256 결정적 해시(현행 구현, 프로세스 재시작 간 sticky 보장) / (b) §D-2 의사코드 그대로 Python hash()
   - 판정: KEEP (a) — §D-2의 의도('고정 사용자 할당-일관성')를 Python hash()는 PYTHONHASHSEED 비결정성으로 충족 못 하고 SHA-256이 충족하므로 구현이 정본 의도에 더 정합한 알고리즘 선택; 차기 상세명세 정비 시 D-2 의사코드를 SHA-256 기준으로 갱신 권고.
15. **[KEEP]** `docs\sot 2\4-4_MLOps-LLMOps\04_canary-deployment\canary_lifecycle_sop.md`:41, 45 — Stage 2(Partial) 승격 게이트 QoD 임계를 원문 3.8/5.0(=0.76 환산)에서 0.85로 상향해 LOCK-ML-05와 단일화한 임계값 선택 (실측: L45 'SOT DEC-010/CONF-ML-002 SUPERSEDED 결정에 따라 ... LOCK-ML-05 정본 0.85 적용' + AUTHORITY L33 'QoD≥0.85 (SOT DEC-010 0.0~1.0 스케일)').
   - 선택지: (a) 0.85 단일 임계(현행, DEC-010 비준·LOCK-ML-05 등재) / (b) 0.76(=3.8/5.0 등가 환산) 유지
   - 판정: KEEP (a) — DESIGN LOCK(LOCK-ML-05) + SOT DEC-010이 0.85를 정본 등재 완료했으므로 임계 상향은 비준된 설계 선택으로 무모순; 다만 '척도 통일/환산' 프레이밍(T6-234)은 '환산(0.76)+상향 결정(0.85)'으로 표현 정정이 바람직(표기 정비, 값 변경 아님).
16. **[KEEP]** `docs\sot 2\4-4_MLOps-LLMOps\05_feedback-loop\feedback_pipeline.md`:563-571 (상세명세 §F-2 L412-417 정본) — FewShot 이상적 응답 초안 생성을 Claude Sonnet(시스템 메인 LLM)으로 수행하는 모델 선택 — LOCK-ML-12(피드백 100% 로컬 저장)와의 경계 정책 (실측: L567 '이상적 응답 생성 (Claude Sonnet 으로 초안 작성)', L563 '§F-2 L412~L417 정본' 그대로 인용).
   - 선택지: (a) 메인 LLM(Claude Sonnet) 초안 + 인간 검토 48h SLA(현행, §F-2 정본) / (b) 로컬 모델 한정 또는 마스킹 후 호출 정책 추가
   - 판정: KEEP (a) — 해당 단계는 상세명세 §F-2 정본 5단계 verbatim이고 LOCK-ML-12는 피드백 '저장'의 로컬 전용을 규정하며 시스템 메인 추론이 Claude인 아키텍처에서 추론 호출까지 금지하지 않으므로 무모순; 대표 입력의 PII 마스킹 적용 명문화만 후속 권고.

> notes: 앵커 12 대비 16건(+4) — 강제 짜맞춤 금지 지시에 따라 정의(사실+정본 위반 없는 값/아키텍처/정책 선택)와 디스크 실측을 충족하는 전수를 등재. 차이 사유: (1) 원판정 주관 리스트 부재로 경계 항목 판단 기준 복원 불가, (2) GPT 단독 finding(ML-4-4-002/003/011/013/015/018/019/020)을 실측 후 다수 편입한 결과로 추정. 제외 처리 상세: [mf_in 객관결함 동일/중복 26개 finding id 제외] T8-029/047/057/058/070/071/086/087/133/134/151/223/240/253/263/277/278(상세명세 signal_score는 i 미등재이나 production 문서 dspy_optimization.md L677·feedback_pipeline FR-7에 signal_score 필드 실존으로 현행 정본 차원 해소→비주관)/292, T6-088/152, ML-4-4-001/006/007/008/009/012/014. [verify=refuted 오탐 13] T8-017/032/163/164/184/198/207/224/239/264/293, T6-197/206. [경계→비

### 4-3_MCP-Server-Client (15건)

1. **[KEEP]** `docs\sot 2\4-3_MCP-Server-Client\01_internal-tools\domain_tools.md`:787 — timeout 카테고리 재시도 횟수를 1회로 설정(타 카테고리 server_error는 3회, 큐 포화는 1회로 사유별 차등)
   - 선택지: (a) timeout retry 1회 유지(긴 30~60s 예산 도구) (b) LOCK-MCP-06 일괄 3회 (c) 도구별 차등표 명문화
   - 판정: KEEP retry 1회 — LOCK-MCP-06(종합계획서 L156)은 'max 3회' 상한 규정이지 고정값이 아니므로 1회는 무모순. 이미 30~60s 타임아웃이 부여된 도구의 재시도 최소화는 합리적 정책 선택
2. **[KEEP]** `docs\sot 2\4-3_MCP-Server-Client\01_internal-tools\search_tools.md`:415 (cross: 224, 469) — payload_too_large를 RetryPolicy상 비재시도(X)로 두되 top_k 자동 축소 후 재요청을 별도 복구 경로로 설계
   - 선택지: (a) 비재시도+파라미터 축소 재요청 분리 유지 (b) §6 표에 '조건부 재시도(축소 시)' 표기 (c) 축소 재요청 자체 폐지
   - 판정: KEEP — §6 표의 재시도는 LOCK-MCP-06 동일 페이로드 자동 재시도 의미이고, top_k 축소(L224 §3.3, L469 T5)는 §7 Phase4 fallback 계열의 별개 복구 동작. 동일 페이로드 재시도가 무의미한 에러에 대한 표준적 설계 패턴으로 정본 무모순
3. **[KEEP]** `docs\sot 2\4-3_MCP-Server-Client\01_internal-tools\web_tools.md`:416, 561 — calendar_write attendees>50 + send_invitations=true 무승인 시 에러 카테고리를 security_violation으로 분류(즉시 I-20)
   - 선택지: (a) security_violation(즉시 I-20, 강한 게이트) (b) validation_error (c) rate_limit
   - 판정: KEEP — 대량 초대를 스팸/유출 방지 게이트로 취급하는 의도가 L416 승인 Gate(P2 이상)와 짝으로 명시되어 있고, McpError 10 카테고리 정본(search_tools §2.1) 재정의 없음. 에러 카테고리 배정은 설계 재량이며 보수적 분류가 6-2 보안 정책 방향과 정합
4. **[KEEP]** `docs\sot 2\4-3_MCP-Server-Client\01_internal-tools\web_tools.md`:543 (cross: 558, 32) — email_send 사용자당 시간당 100통 Rate Limit 설계값 채택
   - 선택지: (a) 100통/h/유저 유지 (b) §H-1 '내부 100/s' 준용 (c) 한도 미설정
   - 판정: KEEP — 100통/h/유저는 이메일 남용 방지용 신규 설계값으로 합리적(초당 100통 준용은 이메일에 부적절). §H-1(상세명세) 자체에 email 한도가 없어 위반할 정본이 없으며, L558 비고의 §H-1은 행 공통 인용(Brave 2000/월 포함) 수준. 차기 개정 시 출처를 '본 문서'로 병기하면 족함
5. **[KEEP]** `docs\sot 2\4-3_MCP-Server-Client\02_external-servers\communication_servers.md`:84 — Slack tier-1(공식 60/min) 대비 80% 경고 임계를 50/min으로 설정('본 세션 정의' 명시)
   - 선택지: (a) 50/min(운영 라운딩, ~83%) (b) 48/min(산술적 80%) (c) 54/min(90%)
   - 판정: KEEP — 근거 칼럼이 '본 세션 정의'로 신규 설계값임을 투명 선언했고 공식 쿼터(L82, §H-1 Slack 1/s) 아래의 보수적 선제 경고로 합리적. 괄호 '(90% 도달 직전)' 표현은 산술상 ~83%라 다듬을 여지가 있으나 임계값 자체는 정본 무모순
6. **[KEEP]** `docs\sot 2\4-3_MCP-Server-Client\02_external-servers\search_servers.md`:141-148 — DuckDuckGo HTML scraper를 Brave 2차 fallback으로 채택하고 리스크 완화는 robots.txt/UA/0.5req/s 수준으로 한정
   - 선택지: (a) DDG scraper 유지 + 차단/CAPTCHA 대응·법적 검토 보강 (b) Exa 경유로 대체 (c) 내부 web_search 직행
   - 판정: KEEP — DDG 채택 자체는 W-NEW-2 정본(종합계획서 §14, L141 '**W-NEW-2 정본**' 명시) 근거가 있어 PLAN 차원에서 승인된 선택. 차단·약관 리스크 완화 깊이는 설계 재량이며 L148이 인터페이스 선언+bridge 위임을 명시. (Exa 체인과의 이중화 충돌은 mf_in i=9 별도 객관건)
7. **[KEEP]** `docs\sot 2\4-3_MCP-Server-Client\03_connection-management\jsonrpc_4-1_cross_ref.md`:47 — execute_tool 행의 '4-3 Bridge 참조 용도' 칼럼에 4-3 측 파생 수치 '31 도구 + 마켓'을 기재
   - 선택지: (a) 현행 유지 (b) 'LOCK-MCP-03' 출처 병기 (c) 시그니처만 기재하고 용도 칼럼 수치 제거
   - 판정: KEEP — 31은 LOCK-MCP-03 정본 수치(CONFLICT_LOG L52 'LOCK-MCP-03: 31개')이고 해당 칼럼(L42 헤더)은 명시적으로 4-3 측 용도 설명 칼럼이라 4-1 method_catalog EXACT MATCH 주장(시그니처 한정)과 충돌 없음. 출처 병기는 선택적 개선
8. **[KEEP]** `docs\sot 2\4-3_MCP-Server-Client\04_payload-schema\capability_negotiation.md`:148 — initialized 알림 미송출 시 서버측 connection close 대기시간 30초 설정(핸드셰이크 단계 전용 타임아웃)
   - 선택지: (a) 30s 유지 (b) Stage 2 타임아웃 10s 배수로 산식화 (c) LOCK/AUTHORITY 등재 후 고정
   - 판정: KEEP — 본문이 'LOCK-MCP-08 idle 10분과 별개의 핸드셰이크 단계 타임아웃'으로 구분을 명시했고 B-2 Stage 타임아웃(5s/10s/5s)과도 모순 없음. SOT 미인용 신규 운영값이지만 위반할 정본이 없는 전형적 설계값 — 차기 개정 시 AUTHORITY 등재 권장
9. **[KEEP]** `docs\sot 2\4-3_MCP-Server-Client\MCP_SERVER_CLIENT_상세명세.md`:225, 235-242 — B-3 RetryPolicy.retry_on은 HTTP 상태코드(408/429/5xx)만 정의하고 내부 음수 코드(-1/-2/-3)의 재시도 정책은 B-4 대응 칼럼 산문으로 2계층 분리
   - 선택지: (a) 2계층 분리 유지(전송계층 retry_on + B-4 정책표) (b) retry_on에 내부 코드 통합 (c) 카테고리 기반 단일 집합
   - 판정: KEEP — B-4 대응 칼럼이 -1 재시도/-2 재시도/-3 재시도 안 함을 직접 규정하여 분리 공간이 모순 없이 동작하며, 실구현 정본 retry_circuit_breaker.md가 카테고리 기반 retriable 집합으로 통합 구현(LOCK-MCP-06 무모순). 코드 공간 분리는 전송/도메인 계층화 설계 선택
10. **[KEEP]** `docs\sot 2\4-3_MCP-Server-Client\MCP_SERVER_CLIENT_상세명세.md`:142 (cross: 644; code_tools.md 77, 110-111) — code_execute 스키마 default 30000ms와 G-1 카테고리 기본 60s를 2층 타임아웃 구조로 병존(보수적 요청 기본 30s, 카테고리 60s, override 최대 120s)
   - 선택지: (a) 2층 구조 유지 (b) 스키마 default를 60000으로 정렬 (c) G-1을 30s로 정렬
   - 판정: KEEP — 하위 정본 code_tools.md L77이 '상세명세 §A-4 default 30000. 기본 카테고리 타임아웃(§G-1)은 60s 이나 호출별 override 가능(최대 120s)'으로 양 값의 공존을 명시적 설계로 reconcile 완료(동일 계열 T8-003이 refuted 처리된 근거). 본문 우선순위상 모순 해소 상태
11. **[KEEP]** `docs\sot 2\4-3_MCP-Server-Client\MCP_SERVER_CLIENT_상세명세.md`:143 (cross: code_tools.md 79-82, 120-121) — code_execute env_vars를 무필터 수용하되 보호를 샌드박스 격리(네트워크 기본 차단)+R-16-5 시크릿 참조 권장에 위임
   - 선택지: (a) 현행(샌드박스 격리+권장) (b) 시크릿 패턴 deny-list 강제 (c) env_vars allowlist 화이트리스트제
   - 판정: KEEP — code_tools.md §3.3(L120-121)이 샌드박스 필수+네트워크 기본 차단으로 유출 경로를 1차 차단하고 L82가 R-16-5 시크릿 참조 형식 권장을 명시한 보안 태세 선택. deny-list 추가는 개선 권장 사항이며 위반된 정본 규정 없음
12. **[KEEP]** `docs\sot 2\4-3_MCP-Server-Client\04_payload-schema\capability_negotiation.md`:187-202 — §8 capability 매트릭스를 Phase 2 누적 9서버 스코프로 유지하고 Sentry/Exa는 '추가 대상(11 서버 완결)'로 명시 유보
   - 선택지: (a) 현행 스코핑 유지(Sentry/Exa 협상값은 P4 V3 개별 문서 위임) (b) 매트릭스에 Sentry/Exa 2행 즉시 추가
   - 판정: KEEP — L187/L202가 11서버 완결 경로를 명시적으로 예고한 문서 스코핑 선택이고, Sentry/Exa 운영 명세는 Phase 4 V3 sentry_alert_sop.md/exa_quota_monitor.md가 보유(_index L97 11/11 ALL CONNECTED). 차기 개정에서 2행 추가가 바람직하나 silent 누락이 아니어서 정본 모순 아님
13. **[KEEP]** `docs\sot 2\4-3_MCP-Server-Client\CONFLICT_LOG.md`:54, 58-60 — CLF-MCP-005(stdio vs DEC-017)를 OPEN/DEFERRED가 아닌 RESOLVED-DEFERRED 독립 상태로 분류하고 거버넌스 후속 과제로 이관
   - 선택지: (a) RESOLVED-DEFERRED 유지(아티팩트 해소+후속 과제 명시) (b) DEFERRED 재분류 (c) OPEN 재개
   - 판정: KEEP — 요약표(L58-60)가 RESOLVED-DEFERRED=1을 별도 칼럼으로 가시화하여 '카운트에서 사라졌다'는 전제가 부분 반박됨. 아티팩트 레벨 해소(§5.1 stdio 예외 주석) 완료+거버넌스 후속 과제 본문 명시 상태에서 상태 분류 체계는 도메인 거버넌스 설계 재량(자동 RESOLVE 금지 원칙도 준수됨)
14. **[KEEP]** `docs\sot 2\4-3_MCP-Server-Client\02_external-servers\development_servers.md`:221, 229-230 — GitHub 429/쿼터 소진 시 Retry-After 대기를 1차로 하고 예산 초과 시에만 동일 PAT의 REST API v3 직접 호출로 폴백
   - 선택지: (a) 현행(대기 우선+예산 초과 시 REST 직접) (b) REST 직접 폴백을 서버 연결 실패 트리거로 한정 (c) 429 시 폴백 전면 금지
   - 판정: KEEP — L221/L230이 429의 1차 대응을 Retry-After/X-RateLimit-Reset 대기(§H-2 단계 3 정합)로 규정하고 REST 직접은 예산 초과 시 최후 수단으로 한정. 동일 PAT 한계는 인지 가능한 트레이드오프로 폴백 전략 설계 재량. 개선 여지: REST 직접 경로에도 쿼터 회계·감사 로그 동일 적용 명시
15. **[KEEP]** `docs\sot 2\4-3_MCP-Server-Client\01_internal-tools\code_tools.md`:286-303 — file_write에 temp file/atomic rename/fsync/rollback을 요구하지 않고 allowlist+실행파일 차단+append file lock+create_new 충돌 에러 수준의 동시성·안전 정책 채택
   - 선택지: (a) 현행 유지 (b) same-dir temp+atomic rename+fsync 의무화 (c) overwrite 모드만 atomic 적용
   - 판정: KEEP — 정본(상세명세 §A-5/§A-6/§F-2, LOCK-MCP-01)은 쓰기 원자성을 규정하지 않으며 L302 append flock/LockFileEx 필수, L303 create_new 명시 에러 등 1차 방어가 존재. 원자적 쓰기 보강은 품질 개선 제안 수준으로 MUST-FIX 정본 위반 아님

> notes: 앵커 15건과 정확히 일치(15/15). 방법: (1) mf_in 객관결함 28건과 동일/중복 finding 제외 — CLC/tight 측 T8-001·T6-013/014/015·T6-051·T8-053/056/074/077/097/117/118/119/130/132/147·T6-139·T8-179/180·T5-181·T8-185 및 동일 계열 T8-072(=mf i22 LOCK-MCP-05/10 혼동)·T8-182(=mf i17 Puppeteer 5/10분), GPT 측 MCP-AUD-001/003/004/005/006/007/008/009/011/014. (2) verify=refuted 오탐 8건 제외: T8-003/082/089/099/133/164/165/184. (3) 단순 표기성 1건 제외: T6-028(web_tools L62 헤더·L69 description의 fallback 체인 축약 — 4단계 정본은 enum L144/§8 L587/§9.1 L639에서 일관, 설계 선택이 아닌 요약 표기 부정확). 등재 15건 전건 디스크 실측(file:line) 확인 완료, 전건 정본(RULE 1.3>PLAN 3.0>DESIGN LOCK>본문>스키마) 

### 1-2_Auxiliary-Modules (14건)

1. **[KEEP]** `docs\sot 2\1-2_Auxiliary-Modules\01_multimodal-interpreter\audio_pipeline_v2.md`:11, 234-238 — L3 판정을 실측치 대신 선언형 영구 baseline + closure tracking(~2026-06-09)으로 PASS 부여하는 판정 정책
   - 선택지: (a) 정량 실측 전 CONDITIONAL 유지 (b) 선언 baseline+추적기한으로 PASS 승급(현행)
   - 판정: KEEP — PLAN 3.0/Phase4 P4-2 절차가 forward-defined baseline+closure tracking을 명시 허용(L234-238에 사전/사후/기한 투명 기록), 정본 위반 없음
2. **[KEEP]** `docs\sot 2\1-2_Auxiliary-Modules\01_multimodal-interpreter\vision_api_integration_v2.md`:104-107, 156-160 — Primary 백오프 스케줄: attempt 0,1만 sleep(1s,2s) 후 attempt 2 break→Secondary 조기 전환(실 누적 3s), E6 표 '+7000ms worst'는 3-sleep 가정 보수 상한
   - 선택지: (a) 3회 sleep(1,2,4s) 완주 후 전환 (b) 2회 sleep 후 조기 Secondary 전환(현행), E6는 상한 표기
   - 판정: KEEP — timeout_policy_v2 §4.2 정본(vision_api max_retry=2=총 3회 시도)과 무모순이며 E6 +7000ms는 실측(≤3s)을 포함하는 보수적 상한, 전환 시점은 설계 재량
3. **[KEEP]** `docs\sot 2\1-2_Auxiliary-Modules\02_multimodal-renderer\audio_renderer_v2.md`:103, 111, 133 — TTS 추정 휴리스틱 상수 선택: duration_estimate_sec=len/200, estimate_render_time=1.0+len/1000 (서로 다른 목적의 두 추정식)
   - 선택지: (a) 발화속도 기반 단일 상수 통일(예: len/5 ≈ 한국어 5자/초) (b) 용도별 별도 휴리스틱 유지(현행)
   - 판정: KEEP — RULE/PLAN/LOCK 어디에도 발화속도·렌더시간 추정 정본 없음, metadata 추정치는 non-LOCK 부속 필드로 설계 재량(T-01 '~5s'는 재생 길이 기대로 스코프 상이)
4. **[KEEP]** `docs\sot 2\1-2_Auxiliary-Modules\02_multimodal-renderer\chart_renderer_v2.md`:64, 80-89 — chart_type if/elif 체인에 방어적 else 생략 — Pydantic Literal[bar,line,scatter,pie,heatmap](L64) 스키마 검증 단일 방어선에 위임
   - 선택지: (a) defensive else + AUX-E-RENDER-010 이중 방어 (b) 닫힌 Literal 도메인 신뢰(현행)
   - 판정: KEEP — chart_type은 Literal로 닫힌 도메인이라 dead-else이며, 이중 방어 여부는 정본 무관 설계 재량(타입 추가 시 Literal과 체인 동시 확장이 전제)
5. **[KEEP]** `docs\sot 2\1-2_Auxiliary-Modules\04_knowledge-search\rag_integration_v2.md`:151-154 — 인덱스 갱신 시 캐시 무효화 granularity: 영향 entry 불명 → 전체 invalidate('보수적' 주석 명시) 선택
   - 선택지: (a) doc 연관 entry 선택적 invalidate (b) 전체 flush 보수적 선택(현행)
   - 판정: KEEP — LOCK-AX-10(cosine≥0.95, TTL 24h)은 무효화 granularity를 규정하지 않음, 정확성 우선 보수 선택은 정본 무모순(E6 cache-hit≥80%는 Phase 5 forward-defined 운영 측정 후 조정 여지)
6. **[KEEP]** `docs\sot 2\1-2_Auxiliary-Modules\03_summarizer\conversation_summary_v2.md`:123, 153, 158 — compression_ratio = 1 - len(l3)/total 정의에 음수 클램프 미적용 — ≤2턴은 AUX-E-SUMM-005 거부(T-06)로 극단 케이스 차단
   - 선택지: (a) max(0.0, ratio) 클램프 추가 (b) 원시 메트릭 그대로 노출(현행, 짧은 대화는 입구 거부)
   - 판정: KEEP — T-01 ≥0.5는 5턴 정상 시나리오 기대치이며 메트릭 정의 자체는 정본 미규정 설계 재량, ≤2턴 거부가 음수 케이스 대부분 차단
7. **[KEEP]** `docs\sot 2\1-2_Auxiliary-Modules\04_knowledge-search\search_pipeline_v2.md`:53, 153, 221 — P95 SLO 3계층 스코프 운용: 500ms(internal only)/2000ms(외부 포함, L153 병기)/모듈 SLO default 800ms(L221 P4-2 baseline)
   - 선택지: (a) 단일 SLO 수치로 통일 (b) 스코프별 계층 SLO(현행)
   - 판정: KEEP — SLA 임계값은 설계 선택이고 L153이 internal/external 스코프를 명시 구분, L221은 Phase 5 정량 보완 forward-defined 모듈 default로 층위가 달라 정본 모순 아님
8. **[KEEP]** `docs\sot 2\1-2_Auxiliary-Modules\06_mapping\interface_contracts.md`:425, 872, 920 — governance 호출(I-19/I-8/I-25) SLA를 fail-closed + 잠정 오버라이드(예: L874 10s/2/2s) + 후속 정본화로 운영하는 정책
   - 선택지: (a) 본 문서에서 직접 SLA 수치 고정 (b) fail-closed 선언 + timeout_policy 표 확장 위임(현행)
   - 판정: KEEP — fail-closed는 보안 우선 설계 선택이고 '무한 블록' 우려는 timeout_policy_v2 §4.2 F-04 정본화(600s/5s/3s bound)로 해소됨, 값의 정본은 timeout_policy_v2가 보유(문서 동기화는 별도 항목 CHANGE 참조)
9. **[KEEP]** `docs\sot 2\1-2_Auxiliary-Modules\04_knowledge-search\external_sources_v2.md`:150-169 — FinanceAdapter(V1/P1)·NewsAdapter(V2, 6-7 RT-BNP cross-ref) search 본문을 '...' placeholder로 두고 registry 등록을 유지하는 단계적 구현 phasing
   - 선택지: (a) 미구현 adapter registry 제거 (b) placeholder 등록 + V2 게이트/AUX-E-EXT-005로 차단(현행)
   - 판정: KEEP — NewsAdapter는 _v2_active() 게이트로 빈 결과 반환, 미활성 경로는 AUX-E-EXT-005가 규정하며 구현 상세는 해당 Phase 정본화 시점 보강이 계획된 scope 선택(FinanceAdapter placeholder는 P1 주석 명시)
10. **[KEEP]** `docs\sot 2\1-2_Auxiliary-Modules\04_knowledge-search\external_sources_v2.md`:87, 187-193 — 오류 처리 전략: os.environ 직접 접근(키 미설정=즉시 KeyError fail-fast) + parallel_search 개별 실패 continue(partial_failure 허용), 상세 정책은 E5 에러표 선언에 위임
   - 선택지: (a) 의사코드에 KeyError/429/스키마 오류 분기 전부 명시 (b) E5 에러표(AUX-E-EXT-002/003/004)를 정책 정본으로 두고 의사코드는 happy-path(현행)
   - 판정: KEEP — E5 표가 backoff/거부+audit/6-2 알림 정책을 이미 정본 선언하고 timeout은 _safe_search가 audit 처리, 의사코드 상세도는 설계 재량(fail-fast 키 접근도 6-2 api_key_management 정책 주석과 정합)
11. **[🔧CHANGE]** `docs\sot 2\1-2_Auxiliary-Modules\06_mapping\interface_contracts.md`:116 — 표 미수록 4종(I-19/I-8/I-25/S-1) timeout 정본화를 '후속 처리(PENDING)'로 표기한 문서 동기화 전략
   - 선택지: (a) PENDING 유지 (b) timeout_policy_v2 §4.2 F-04 정본화 완료 반영(권고)
   - 판정: CHANGE — timeout_policy_v2.md §4.1/§4.2(본문 정본, '15 호출 유형')가 F-04 4종을 이미 정본화(i19_approval 600s, i8_policy_filter 5s, i25_sdar_trigger 3s, s1_evaluation_event 5s)했으므로 '현 상태: PENDING'은 정본 모순 stale 표기
12. **[🔧CHANGE]** `docs\sot 2\1-2_Auxiliary-Modules\00_common\_index.md`:37 — 폴더 인덱스의 LOCK 요약 표기 granularity — LOCK-AX-04 요약에 P0/P1/P2를 부착(LOCK-AX-05 의미와 혼합)
   - 선택지: (a) 현행 혼합 요약 유지 (b) AUTHORITY_CHAIN §5A 정본대로 AX-04(<0.4/>=0.7)와 AX-05(P0>=70/P1>=75/P2>=80) 분리 기재(권고)
   - 판정: CHANGE — AUTHORITY_CHAIN.md L75-76 정본이 AX-04=QoD thresholds(<0.4/>=0.7), AX-05=Self-check thresholds(P0/P1/P2)로 명확 분리하므로 현행 요약은 정본 모순(하위 문서 오참조 유발)
13. **[🔧CHANGE]** `docs\sot 2\1-2_Auxiliary-Modules\00_common\_index.md`:38 — 폴더 인덱스가 ResponseEnvelope '필수 필드'로 운영 메타 세트(request_id/status/payload 등)를 광고하는 요약 표현 선택
   - 선택지: (a) 운영 편의 필드 세트 표기 유지 (b) LOCK-AX-11 정본 5키(answer/evidence/self_check/decision_ref/audit)로 정정(권고)
   - 판정: CHANGE — response_envelope.md §2(LOCK 정본 5키)·§3 L107(운영 메타는 non-LOCK)·§4 L113(status 미정의 명시)과 직접 모순, 정본 우선순위상 본문 정본이 _index 요약에 우선
14. **[KEEP]** `docs\sot 2\1-2_Auxiliary-Modules\INDEX.md`:19, 162-173, 183 — 인벤토리 집계 기준 선택: L19 '총 55개'(INDEX 자신 제외 V1-era 스냅샷) vs §9 'V1 56(자신 포함) + V2 NEW 35' 분리 집계
   - 선택지: (a) 단일 총계로 통일(production/_archive/_verification 분리 표) (b) 개요=V1 스냅샷, §9=상세 분리 집계(현행)
   - 판정: KEEP — 55=56−INDEX 자신으로 두 수치는 집계 스코프 차이일 뿐 모순 아님(§9 표가 산식 명시), 자기 포함 여부·V2 분리 집계는 표기 기준 선택. 차기 개정 시 L19에 집계 기준 1줄 주석 권장

> notes: 원판정 앵커 14건과 정확 일치(count_found=14, 강제 짜맞춤 아님 — 전수 도출 결과 자연 일치). 도출 과정: (1) 입력 union 69건(CL-C 57 + GPT 12, tight 41은 CL-C 부분집합·신규 0) 중 mf_in 객관결함 29건(i=0~28)과 동일/중복 41건 제외 — LOCK-AX-04 Modality 오라벨 family(T6-001/027/028, AUX-AUDIT-002), embeddings 모순(T8-031/043), LOCK-AX-02 fabricated citation family(T6-179/T8-192, AUX-AUDIT-001), QoD 4/5-factor family(T6-147/204/210, T8-205), LOCK-AX-11 §B.6 family(T8-211/T6-193), NameError/dead-code류(T8-002/003/004/016/017/053/081/082/083/113/114/115/117, AUX-AUDIT-005/006/008), 기타(T8-014/034/042/056/104/128/138/166, T6-139/149). (2) verify:"refuted" 11건 오탐 제외

### 5-2_File-Context (14건)

1. **[KEEP]** `docs\sot 2\5-2_File-Context\01_context-pipeline\phase_d_v3_strategy.md`:L63-65 (fallback expected_g3_loss=0.18), L81 (§1.4) — GPU 부족 fallback의 경고(0.15~0.30 밴드) 표현을 라우팅 결과 객체의 명시 warning 필드가 아니라 §1.4 사전 게이트가 expected_g3_loss 값을 소비해 발화하도록 둔 스키마 설계 선택.
   - 선택지: (a) 현행: 결과 객체에 expected_g3_loss만 싣고 §1.4 게이트가 warning 발화 + reason 문자열로 'Phase E 분할 권장' 전달 / (b) PhaseD0V3Decision에 warning: bool 필드 추가
   - 판정: KEEP 현행 — DESIGN LOCK R-52-4(≤0.15 정상/0.15~0.30 경고/>0.30 거부, AUTHORITY_CHAIN L286)는 밴드 정책만 규정하고 경고 발화 위치는 규정하지 않으며, 본문 §1.4(L81)가 expected_g3_loss 기반 warning을 이미 명세하므로 정본 무모순.
2. **[KEEP]** `docs\sot 2\5-2_File-Context\02_gap-remediation\g6_distractor_filter.md`:L170 — SEAE 교차 일관성 불일치 판정을 'BERTScore<0.75 AND 코사인<0.65' AND 결합으로 둔 집계 규칙 선택.
   - 선택지: (a) 현행 AND(양 메트릭 동시 하회 시만 플래그 — 오탐 억제, precision 우선) / (b) OR(어느 하나 하회 시 플래그 — recall 우선) / (c) 결합 점수
   - 판정: KEEP 현행 AND — SEAE 임계는 LOCK 비대상(R-52-5 LOCK은 'relevance<0.7 제외+ChunkRAG'만 규정)이고 불일치 청크의 과잉 제외(정보 손실)를 막는 보수적 선택으로 정본 무모순; OR 전환은 실측 회귀 데이터 확보 후 결정 사항.
3. **[KEEP]** `docs\sot 2\5-2_File-Context\03_weakness-mitigation\w04_synthetic_data.md`:L121 (diversity_min_cosine=0.05 거리), L177 (cosine_sim>=0.95 하드코드) — 합성 QA 중복 제거 임계를 cosine 유사도 0.95(=거리 0.05)로 둔 값 선택 및 config 필드 대신 리터럴을 사용한 배선 스타일 선택.
   - 선택지: (a) 현행: 0.95 유사도 임계 하드코드(config 0.05 거리와 수치 동치) / (b) cfg.diversity_min_cosine을 코드에 배선 / (c) 임계값 자체 조정
   - 판정: KEEP 현행 — 0.05(거리)≡1-0.95(유사도)로 config와 코드 값이 상호 정합하여 finding의 '모순' 주장은 성립하지 않고, 0.95는 합리적 dedup 임계로 정본(LOCK/PLAN) 비대상; config 배선은 비차단 후속 정리 권장.
4. **[KEEP]** `docs\sot 2\5-2_File-Context\02_gap-remediation\g8_loop_limit.md`:L199 (내부 is_satisfactory=(score>=0.7)), L150 (caller cfg 게이트), L101 (reflection_threshold=0.7 기본값) — Self-RAG reflection 만족 판정을 내부 고정 0.7 + caller의 cfg.reflection_threshold 이중 게이트로 둔 방어적 이중화 설계 선택.
   - 선택지: (a) 현행: 내부 0.7 고정(만족 정의) + 외부 cfg 게이트 AND 결합 / (b) 내부 판정도 cfg 주입으로 단일화
   - 판정: KEEP 현행 — 내부 0.7은 cfg.reflection_threshold 기본값(L101)과 동치이고 caller가 cfg를 추가로 게이트하므로 config 강화 방향 변경은 여전히 유효하며, DEFINED-HERE LOCK R-52-6(max 3회+비용 가드레일)과 무관·무모순.
5. **[KEEP]** `docs\sot 2\5-2_File-Context\03_weakness-mitigation\w02_ring_attention.md`:L182-187 (0.15~0.30 경고+계속, >0.30 raise), L281 (§10 LOCK 표 3-밴드) — G3 손실 0.15~0.30 구간을 차단 없이 '경고 로그 + 계속'으로 처리하는 soft-tier 정책 선택.
   - 선택지: (a) 현행: 3-밴드(≤0.15 정상 / 0.15~0.30 경고+계속 / >0.30 거부) / (b) >0.15 즉시 차단 hard gate
   - 판정: KEEP 현행 — DESIGN LOCK R-52-4가 '≤0.15 정상 / 0.15~0.30 경고 / >0.30 압축 거부' 3-밴드를 verbatim 규정(AUTHORITY_CHAIN L286)하므로 soft-tier가 곧 정본 설계이며, 디스크 §10 표(L281)도 3-밴드로 표기되어 finding의 '≤0.15 ✅ 과소표기' 지적도 현행에서 해소.
6. **[KEEP]** `docs\sot 2\5-2_File-Context\03_weakness-mitigation\w05_speculative_decoding.md`:L264 (이론 결합 ≈540 tok/s), L353-359 (실측 피크 ~410 / 평균 265) — Speculative×Medusa 결합 효과를 이론 곱셈 상한(120×2.5×1.8≈540)으로 제시하고 벤치마크 실측(410/265)을 별도 표로 병기한 문서 표현 선택.
   - 선택지: (a) 현행: 이론 상한 산식 + 실측 표 병기 / (b) 이론 산식 삭제·실측만 기재 / (c) 540에 '이론 상한, 비중첩 가정' 주석 추가
   - 판정: KEEP 현행 — PLAN 목표는 360 tok/s(§6.3 12x)이고 실측 410(피크)/265(평균)·3.4x가 목표 마진을 충족해 정본 위반이 없으며, 540은 명시적으로 '결합 효과' 추정 산식으로 제시됨; (c) 주석 추가는 선택적 개선.
7. **[KEEP]** `docs\sot 2\5-2_File-Context\03_weakness-mitigation\w07_mdcure_multidoc.md`:L149 (cosine<0.85 AND entity_overlap==0 → NLI skip), L114 (similarity_threshold=0.85) — NLI 호출 비용 절감을 위해 cosine<0.85이면서 entity 공유가 전혀 없는 명제쌍을 후보에서 가지치기하는 비용/재현율 트레이드오프 선택.
   - 선택지: (a) 현행: 0.85 AND entity 0 가지치기(NLI 비용 O(n²) 억제) / (b) 임계 하향(예: 0.6) / (c) 전수 NLI(비용 폭증)
   - 판정: KEEP 현행 — 가지치기 임계는 LOCK 비대상 설계 파라미터이고 entity 결합 경로(W6 연동)가 동일 사실 모순쌍의 주요 검출 루트를 보전하므로 정본 무모순; +45% 모순 검출 목표 미달이 실측되면 그때 임계 조정.
8. **[KEEP]** `docs\sot 2\5-2_File-Context\04_advanced-techniques\h03_query_routing.md`:L167 — semantic-router 결과 객체에 confidence 속성이 없으면 명명된 route를 그대로 수용하는 fail-open 폴백 정책 선택(hasattr 가드).
   - 선택지: (a) 현행: fail-open(속성 부재 시 라이브러리 판정 신뢰) / (b) fail-closed(getattr(result,'confidence',0.0)로 부재 시 hybrid 폴백)
   - 판정: KEEP 현행 — confidence_threshold 게이트 자체는 LOCK 비대상이고 부재 시 L2 LOCK hybrid(alpha=0.3, RRF k=60) 폴백 경로가 result.name is None 분기로 이미 확보되어 정본 무모순; 보수화(b)는 선택적 강건성 개선.
9. **[KEEP]** `docs\sot 2\5-2_File-Context\04_advanced-techniques\h09_proposition.md`:L164-171 — 청크 점수를 '소속 명제 점수의 max'로 집계해 1차 정렬한 뒤 Cross-Encoder rerank로 최종 순위를 결정하는 점수 집계 전략 선택.
   - 선택지: (a) 현행: 명제 max-score 1차 정렬 + L3 LOCK CE rerank 최종 / (b) 명제+청크 점수 가중합 literal hybrid / (c) CE 단독
   - 판정: KEEP 현행 — 최종 순위가 L3 LOCK(Cross-Encoder Reranking) 경로를 통과하므로 정본 정합이고 max-aggregation은 표준 ParentDocument 패턴; L164 주석 'Hybrid 점수' 라벨만 '명제 max 점수'로 후속 정리 권장(비차단).
10. **[KEEP]** `docs\sot 2\5-2_File-Context\04_advanced-techniques\h08_parent_child.md`:L150 — ParentDocumentRetriever의 docstore 백엔드를 스펙(V1) 수준에서 InMemoryStore로 둔 저장소 선택.
   - 선택지: (a) 현행: InMemoryStore(스펙 단순화, LangChain 표준 예시 패턴) / (b) 영속 저장소(Redis/SQLite/LocalFileStore) 명시
   - 판정: KEEP 현행 — docstore 백엔드는 LOCK/PLAN 비대상 구현 선택이며 L7 LOCK(청크 크기/오버랩)은 splitter 파라미터로 충족됨; production 영속화 요구가 정본화되면 그때 백엔드 교체를 V2+ 절로 명세 권장.
11. **[KEEP]** `docs\sot 2\5-2_File-Context\04_advanced-techniques\h12_colpali.md`:L160-167 — ColPali 시각 검색을 전 코퍼스 페이지 대상 Late-Interaction MaxSim 전수 스캔으로 구현한 검색 아키텍처 선택.
   - 선택지: (a) 현행: 전수 MaxSim(late-interaction의 표준 정확 계산, 소규모 시각 코퍼스 전제) / (b) ANN 1차 필터 + MaxSim rerank 2단계
   - 판정: KEEP 현행 — token-level late interaction은 표준 ANN 인덱스로 직접 대체 불가하여 전수 MaxSim이 ColPali 원 설계의 정확 구현이고 V1/V2 시각 코퍼스 규모에서 합리적; 대규모화는 V3+ 확장 트랙에서 ANN 사전필터 도입 권장.
12. **[KEEP]** `docs\sot 2\5-2_File-Context\04_advanced-techniques\h17_cov_rag.md`:L220-223 (compute_consistency), L210-216 (L15 NLI 의무 연쇄) — CoV 검증 답변과 원 사실의 일치 판정을 양방향 문자열 포함 비교 휴리스틱으로 둔 알고리즘 선택(docstring에 V3 embedding cosine 확장 명시).
   - 선택지: (a) 현행: 단순 포함 비교 + 'V3에서 embedding cosine 확장 가능' 명시 / (b) 즉시 embedding cosine / (c) NLI 기반 비교
   - 판정: KEEP 현행 — 본문 docstring(L221)이 의도된 단순화와 V3 업그레이드 경로를 명시한 설계 선택이고, false negative 리스크는 직후 L15 NLI V2 CRITICAL 의무 연쇄(L210-216, 본문 §4.3 L4.5)가 안전망으로 흡수하므로 정본 무모순.
13. **[KEEP]** `docs\sot 2\5-2_File-Context\FILE_CONTEXT_구조화_종합계획서.md`:L174 (L9 LOCK row) — 도메인 QoD 점수 체계로 CLAUDE.md의 5-요소 가중(Accuracy 0.30+Relevance 0.25+Completeness 0.20+Safety 0.15+Efficiency 0.10)을 채택하고 DEC-014 RAG 변형(4-요소)을 사용하지 않은 가중 벡터 선택.
   - 선택지: (a) 현행: L9 LOCK = 5-요소 PLAN정본 가중 verbatim 인용 / (b) DEC-014 QoD(RAG) 4-요소 가중 채택 / (c) 양 변형 관계를 plan에 명시 주석
   - 판정: KEEP 현행 — RULE(CLAUDE.md L264-266) > PLAN 우선순위상 5-요소 가중의 verbatim 인용이 정본 정합이고 DEC-014은 RAG 스코어 전용의 별개 스코프로 공존 가능; (c) 변형 관계 1줄 주석은 선택적 개선.
14. **[KEEP]** `docs\sot 2\5-2_File-Context\02_gap-remediation\g2_context_rot.md`:g2 L96 (user_message 필드), L162-175 (UX 표 + R9 원칙); phase_a_reception.md L101 (accuracy_estimate 내부 메타데이터, R9 노출 금지) — 정확도 저하 경고를 내부 원시 추정치(accuracy_estimate, R9 비노출)와 사용자용 추상화 메시지(user_message, 배너/팝업 노출)로 2계층 분리한 사용자 노출 정책 선택.
   - 선택지: (a) 현행: 내부 메타데이터 비노출 + 사용자용 추상 메시지 노출(g2 §4.2 UX원칙 3 'R9 준수: 내부 Phase 명칭/파이프라인 상세 비노출') / (b) 전면 비노출 / (c) 원시 추정치 직접 노출
   - 판정: KEEP 현행 — R9은 내부 파이프라인 상세 비노출 규칙이고 g2 §4.2가 사용자 경고용 추상 메시지를 R9 준수 형태로 명문화(L175)했으므로 phase_a의 'accuracy_estimate 비노출'과 g2의 user_message는 충돌이 아닌 계층 분담으로 정본 무모순.

> notes: [방법] clc 45건 + tight 36건(전수 clc 부분집합, 고유 0건) + GPT 13건 = 고유 finding 49건을 mf_in 객관결함 29건(i=0~28)과 대조해 매칭 제외(T8-001/002/005/023/024/025/028/046/048/055/063/074/079/080/106+107(i=11 통합)/108/109/126/127/129/133/143/149/151/159/204, FC-001/003/004/005 + GPT i=14·15·19·20 대응). 잔여 후보 전건을 디스크 실측 후 분류 — 표본 없음. [카운트] 14/14 앵커 일치. [오탐/디스크 반박 제외] FC-5-2-008(g8 L4·w12 L4 현행 Status=APPROVED — 디스크 반박), FC-5-2-010(phase_a L135 'L18 KG=V3:ON이므로 V1 KG→hybrid 폴백'은 h03 L178과 의미 정합 — 어색한 문구일 뿐), T8-187(커버리지 55=18+G8+W12+H17, '고유'는 A-series(기존 SOT 장점 활용)를 신규 기술 집계에서 제외한 산식으로 설명 가능), T6-114/T6-135(HyPE +42%p·Step-Ba

### 6-1_UI-UX-System (13건)

1. **[KEEP]** `docs\sot 2\6-1_UI-UX-System\01_builder-view\cli_interface.md`:L309 (CLI-CST-003), L173 (CLI-APR-005) — CLI 명령별 RBAC 거부 경계 — cost 모드 변경은 OPERATOR까지 거부(ADMIN+ 전용), 승인 에러 주석은 VIEWER만 예시로 명기하는 명령별 권한 부여 설계.
   - 선택지: (a) 현행: 에러 설명은 대표 사례만 주석, 권한 실체는 rbac_access_control §6.5 매트릭스 위임 / (b) CLI 에러 표마다 4역할 전체 매트릭스 명기 / (c) 각 에러 행에 rbac 정본 cite 추가
   - 판정: KEEP — 정본 rbac_access_control.md §3(D2.0-07 §3.6 원문: OPERATOR '개인 설정만 변경 가능'·승인 비활성)·§6.5와 CLI 거부 규정이 무모순. 괄호 주석 차등은 표기 수준 선택이지 권한 매트릭스 임의 부여가 아님.
2. **[KEEP]** `docs\sot 2\6-1_UI-UX-System\01_builder-view\builder_view_cockpit.md`:L196 — HITL 승인 타임아웃(고위험 5분/일반 10분) 미응답 시 자동 deny — 에스컬레이션/일시정지 대신 fail-closed 폴백 전략.
   - 선택지: (a) 자동 deny(fail-closed, 현행) / (b) 에스컬레이션·HOLD 연장 / (c) 자동 approve(금지 대상)
   - 판정: KEEP — DESIGN LOCK L18(D2.0-07 §4.3 정본 verbatim '미응답 시 자동 deny', rbac_access_control.md L47/L224 동일 인용) + R-61-8 '자동 승인 절대 금지'와 정합하는 안전 측 기본값. 정본이 직접 규정한 폴백 전략으로 결함 아님.
3. **[KEEP]** `docs\sot 2\6-1_UI-UX-System\01_builder-view\cli_interface.md`:L172 (CLI-APR-004) — TIMEOUT_EXPIRED의 exit_code를 사용자 오류군과 동일한 1로 배정(내부 오류만 3)하는 2단 exit code 체계.
   - 선택지: (a) 현행 2단(1=실패 일반/3=내부 오류) / (b) timeout 전용 exit code(예: 2) 분리 / (c) 에러군별 세분 코드
   - 판정: KEEP — 정본 D2.0-08 §2.3에 exit code 세분 요구 없음. 스크립트는 JSON 출력의 에러 코드 필드(CLI-APR-004)로 구분 가능하므로 exit 1/3 단순 체계는 합리적 설계 선택.
4. **[KEEP]** `docs\sot 2\6-1_UI-UX-System\02_hologram-view\ar_spatial_v3.md`:L113-121 (§3.7) vs L127-136 (§4) — §3.7 L3 세부 표를 사용자 인터랙션 5건으로 한정하고, 시스템/라이프사이클 EventType 4건(spatial_anchor_set·occlusion_resolved·hand_tracking_lost·scene_understanding_ready)은 §4 발행 시점 표에만 두는 문서 스코프 설계.
   - 선택지: (a) 현행: 인터랙션 5건 한정(§3.7 표제가 '5건' 명시) / (b) §3.7에 8 EventType 전부 입력원 매핑 추가
   - 판정: KEEP — 미매핑 4건은 사용자 입력이 아닌 시스템 통지(6-11→6-1 포함)로 §4 표에 발행 시점이 정의되어 있고(L131-135), §3.7 표제 자체가 '5건'으로 범위를 한정. 정본 위반 없는 문서 구성 선택.
5. **[KEEP]** `docs\sot 2\6-1_UI-UX-System\02_hologram-view\hologram_view.md`:L641-650 (§7.4) — 스트림 중단 복구를 자동 reconnect/부분 토큰 복구/backpressure 명세 대신 Failure UI(D2.0-08 §7 정본, L20) + Regenerate 수동 복구로 위임하는 복구 전략.
   - 선택지: (a) 현행: 정본 Failure/Fallback 체계 위임 + 수동 Regenerate / (b) 자동 재연결·부분 토큰 복구·backpressure 상세 명세 추가
   - 판정: KEEP — L650이 '스트림 중단 시 → Failure UI(D2.0-08 §7 정본, L20) 표시'로 LOCK L20 FailureCode/FallbackRegistry 체계에 명시 위임. 자동 재연결은 정본 요구사항이 아니며 로컬 Tauri 환경 특성상 수동 복구 우선은 합리적 선택.
6. **[KEEP]** `docs\sot 2\6-1_UI-UX-System\03_ui-state-machine\nine_state_machine.md`:L336 (#6), L341 (#11); T-08/T-09 정의 L47-48 — 스트리밍 청크 구간을 'T-08 (점진적)' 진행으로, S6 중 selfcheck 실패를 'T-09 (조건부)'로 표기하는 스트리밍 상태 귀속 모델링 선택.
   - 선택지: (a) 현행: 점진적/조건부 주석 모델(스트리밍 중 논리적 S4 체류) / (b) 스트리밍 전용 서브상태 신설 / (c) S6→S7 전이 ID 신규 추가
   - 판정: KEEP — T-08(S4→S6)·T-09(S4→S7) 정의와 9x9 매트릭스(L61-71)는 불변이고, '(점진적)'/'(조건부)' 주석이 진행 중 모델을 명시. 정본 전이 ID 재정의 없이 이벤트 그룹의 상태 귀속을 표현한 설계 선택.
7. **[KEEP]** `docs\sot 2\6-1_UI-UX-System\UI_UX_SYSTEM_구조화_종합계획서.md`:L1185-1186 (#9 절차 3-4) — plan 절차에서 RECOVERY 복구 실패 최종 상태를 'ERROR'로 단순 기술하고, 에스컬레이션 경로·최대 재시도 한도는 L3 상세(nine_state_machine T-14/T-15)에 위임하는 명세 분담 선택.
   - 선택지: (a) 현행: plan은 요약, 재시도 한도는 T-14 'retry < max_retry'·복구 포기는 T-15가 보유 / (b) plan 절차에 에스컬레이션·알림·ADMIN 개입 트리거 명기
   - 판정: KEEP — nine_state_machine.md L53-54에 T-14(재시도 횟수 < max_retry)·T-15(복구 포기→S1) 경로가 이미 정의되어 있고 plan 절차 텍스트는 요약 수준. PLAN 3.0 본문과 L3 정본 간 모순 없음.
8. **[KEEP]** `docs\sot 2\6-1_UI-UX-System\UI_UX_SYSTEM_구조화_종합계획서.md`:L1533 (#12 절차 4) — WCAG 2.1 AA 대비 검증 범위를 다크 배경(LOCK L7 다크모드 기본) 기준으로 한정하고 미충족 시 보정 규칙으로 처리하는 검증 스코프 선택.
   - 선택지: (a) 현행: 다크 배경 우선 검증 + '미충족 시 보정 규칙' / (b) 라이트 배경·텍스트 크기·사용 맥락별 전수 대비 검증 명기
   - 판정: KEEP — LOCK L7(다크모드 기본) 하에서 다크 배경 우선 검증은 정합적이며, design_system_orange_blue.md §6.2가 라이트 모드용 보정 팔레트(#C2410C/#0E7490)를 별도 정의해 라이트 대비를 실질 처리. 검증 범위는 설계 재량.
9. **[KEEP]** `docs\sot 2\6-1_UI-UX-System\AUTHORITY_CHAIN.md`:L306-315 (§9.1) + plan L1984 + INDEX.md L83-88 — Phase 4 entry-gate 노치(ar_spatial ≥350L, avatar ≥400L 등 라인 수)를 byte/E1~E9 완성도 기준으로 대체 승인한 게이트 기준 선택 (실측 229/276/255L).
   - 선택지: (a) 게이트 FAILED/PENDING 회귀 / (b) 라인 기준 충족까지 증량 / (c) 현행: byte/완성도 대체 + AUTHORITY §9.1 명시 기록
   - 판정: KEEP — AUTHORITY_CHAIN L315가 '라인 수는 §7.4 forward-defined 노치값 대비 일부 미달이나 byte/E1~E9 완성도 기준 sibling 초과'로 대체 근거를 정본에 명시 기록했고, 동일 패턴이 3-7/4-4 등 sibling 도메인에서 일관 수용된 관행. plan의 노치는 forward-defined 추정치로 정본 모순 아님.
10. **[KEEP]** `docs\sot 2\6-1_UI-UX-System\05_custom-hooks\zustand_stores.md`:L765-774 (authStore partialize) + rbac_access_control.md L605 — 인증 상태(user/role/isAuthenticated/tokenExpiresAt)를 Tauri localStorage에 persist하는 UI 표시 캐시 아키텍처 — 6-2 검증 전 상태를 부팅 직후 표시에 사용.
   - 선택지: (a) persist 전면 제거(매 기동 6-2 재인증 대기) / (b) 현행: 표시 캐시 persist + 6-2 우선·캐시 무효화·세션 만료 규칙 병행
   - 판정: KEEP — rbac_access_control.md §8.4(L605-609)가 '6-2 보안 규칙이 6-1 UI 규칙보다 우선(AUTHORITY_CHAIN §5.3)' + 즉시 반영 + 캐시 무효화 + 30분 자동 잠금(D2.0-07 §3.7)을 이미 명세. UI 계층 캐시는 표시 전용으로 정본 위계와 정합하는 아키텍처 선택.
11. **[KEEP]** `docs\sot 2\6-1_UI-UX-System\04_react-components\extension_slots_v3.md`:L100 (PLUGIN_LOAD_TIMEOUT), L107-112 (§3.4 전이표) — PLUGIN_LOAD_TIMEOUT의 구체 timeout 수치·retry 횟수·cooldown을 고정하지 않고 LOCK L17 ≤500ms 상한 내 구현 재량으로 두는 수치 미고정 선택.
   - 선택지: (a) 수치 즉시 고정(예: timeout=500ms, retry 1회, cooldown 명시) / (b) 현행: L17 ≤500ms 상한만 명시, 확정은 Phase 5 운영 측정 후
   - 판정: KEEP — §3.4 표제가 'LOCK L17 ≤500ms'로 상한 정본을 명시해 FB_RETRY_SOFT의 '원래 타임아웃 1.5배' 계산 기준이 L17 상한에서 유도 가능. INDEX §8 Phase 5 게이트(staging 7일 측정)가 수치 확정 시점으로 예약되어 있어 현 단계 미고정은 합리적 설계 재량.
12. **[KEEP]** `docs\sot 2\6-1_UI-UX-System\03_ui-state-machine\event_type_v2_sync.md`:L114-120 (§3.1 절차), L256 (§10) + INDEX.md L143 — ISS-7 RESOLVED 판정 기준을 '6-1측 책임(V2 56 EventType 명세 + 6-12 등록 큐 등재) 완료' 시점으로 두고, 6-12 레지스트리 반영·테스트는 RECHECK_FLAG로 추적하는 프로세스 기준 선택.
   - 선택지: (a) PENDING/WATCH 유지 후 6-12 반영 커밋·테스트 증거로 RESOLVED / (b) 현행: 발신측 책임 완료 기준 RESOLVED + 6-12 RECHECK_FLAG 추적
   - 판정: KEEP — INDEX §7(L149-156)이 6-12를 RECHECK 관계 '동기 등록 큐'로 등재하고 LOCK-EL-* 재정의 금지(§3.1 절차 명시)를 준수. cross-handoff에서 발신 도메인이 자기 측 책임 완료로 마감하고 수신측 반영을 RECHECK_FLAG로 추적하는 것은 VAMOS 도메인 표준 관행으로 정본 모순 없음.
13. **[KEEP]** `docs\sot 2\6-1_UI-UX-System\04_react-components\extension_slots_v3.md`:L206, L214 (§8) + INDEX.md L139/L166 — extension_slots §8의 '100% 매핑'을 'V3 범위 플러그인 그룹의 슬롯 귀속 매핑 100%'로 한정 정의하고, STEP7-C 항목별 커버리지 100%는 INDEX Phase 5 게이트에 위임하는 범위 정의 선택.
   - 선택지: (a) '100%' 표현을 항목 커버리지와 분리 명기·재서술 / (b) 현행: §8 표제('슬롯 매핑 매트릭스')와 표 구성이 범위를 한정, 항목 커버리지는 INDEX L166 Phase 5 보유
   - 판정: KEEP — §8 표제·도입문(L206 'STEP7-C 잔여 ~70+ V3 범위 중 ... 어떤 슬롯에 주입되는지 매핑')이 슬롯 귀속 매핑임을 스스로 한정하고, 항목 커버리지 100%는 INDEX §8(L166) Phase 5 게이트가 정본으로 보유 — 두 문서는 상이한 범위를 서술하므로 무모순.

> notes: 원판정 앵커 13건과 일치(강제 짜맞춤 없음). 도출 과정: (1) 전체 풀 = clc 41 + GPT 12 = 53 finding(tight 27은 clc 부분집합). (2) 객관결함 제외 24 ID — mf_in 21건에 매핑되는 T6-001/T8-034/036/046/083/T6-084/T8-114/154/157/164/169/175/182/232/233/234/T6-255/256/T8-257/263 + AUD-004~007. (3) 오탐 제외 12건 — verify=refuted 중 디스크 실측으로 내용 부재 또는 주장 반박 확인: T6-014(LOCK L19 출처는 양 파일 모두 §5.1로 일관, §5.6-A는 CLI EventType 목록 위치 표기), T6-047, T8-060, T8-096, T8-097, T6-139(finding 스스로 'no contradiction' 인정), T8-140(react_components_catalog L278 렌더링 규칙이 severity별 5s/10s/수동을 별도 정의 — prop default는 INFO 기준), T8-142, T8-181, T8-184, T8-210, T6-249. (4) 단순 표기/용

### 6-2_Security-Governance (13건)

1. **[KEEP]** `docs\sot 2\6-2_Security-Governance\01_ai-code-security\guardrails_ai_l2_output.md`:114,177,237 (REFRAIN) vs llamaguard_integration.md:105-121,135 (차단/block) — L2 실패 액션은 Guardrails AI 고유명(REASK/FIX/REFRAIN), L3는 LlamaGuard 관행(block/차단)을 쓰는 계층별 용어 선택.
   - 선택지: (a) 계층별 프레임워크 고유 용어 유지 (b) 도메인 공통 용어('차단')로 통일
   - 판정: (a) 유지 — DESIGN LOCK L7이 계층별 도구(NeMo/Guardrails AI/LlamaGuard)를 별도 지정하므로 도구 고유 액션명 사용은 정본 무모순이며 최종 효과(출력 차단)는 동일.
2. **[KEEP]** `docs\sot 2\6-2_Security-Governance\01_ai-code-security\gdpr_compliance.md`:94,102,127-129 (oc.gdpr.*) vs llamaguard_integration.md:85,157,168,183,199 (oc.security.*) vs guardrails_ai_l2_output.md:207 (security.guardrails.l2.validation) — 감사 이벤트 네임스페이스를 기능 영역별로 분할(oc.gdpr.* / oc.security.* / security.*)하는 네이밍 체계 선택.
   - 선택지: (a) 영역별 분할 유지 (b) 단일 oc.security.* 통일 (c) 6-12 이벤트 레지스트리 정본에 일원화 위임
   - 판정: (a) 유지 — 6-2 정본에 이벤트 네이밍 LOCK이 없고 이벤트 ID 등록 정본은 6-12 Event-Logging 관할. 차기 6-12 레지스트리 동기 시 oc.* 접두사 일원화 권장(현행은 정본 모순 아님).
3. **[KEEP]** `docs\sot 2\6-2_Security-Governance\03_stride-threat-model\dec003_tool_allowlist.md`:172 (P2 최소 RBAC=L2 Admin), 136 (allowed_roles [OWNER,ADMIN]), 228 (includes 검사) — P2(위험) 도구의 호출 최소 RBAC 레벨을 OWNER 전용이 아닌 ADMIN으로 설정.
   - 선택지: (a) ADMIN 호출 허용 + 명시적 승인(L9) (b) P2 도구 OWNER 전용 제한
   - 판정: (a) 유지 — DESIGN LOCK L8 verbatim(AUTHORITY_CHAIN.md:179)은 'P2 승인은 OWNER만'으로 승인 권한만 제한하며 호출 주체는 제한하지 않음. ADMIN 호출+L9 타임아웃 승인 흐름은 정본 무모순(§4에 승인자=OWNER 명시는 개선 옵션).
4. **[KEEP]** `docs\sot 2\6-2_Security-Governance\05_advanced-security\security_test_pipeline_v3.md`:42 — CI/CD 8단계 각 단계 타임아웃 = 5분 (괄호 근거 'L12 30s × 10 batch 적용' 도출 표기 포함).
   - 선택지: (a) 5분 유지 (b) 단계별 차등 타임아웃 (c) L12 30s 직접 적용
   - 판정: (a) 유지 — DESIGN LOCK L12(Docker 샌드박스 30s)는 §5 매트릭스에서 단계 6 Red Team 격리에 별도 verbatim 적용 중이며, CI 단계 타임아웃 5분은 LOCK 비대상 자유 설계값. 괄호 도출식은 참고 표기로 L12 재정의 아님.
5. **[KEEP]** `docs\sot 2\6-2_Security-Governance\05_advanced-security\security_test_pipeline_v3.md`:61-68 (§4 자동 차단 임계값 4종) — 보안 게이트 실패 처리 전략 = 엄격 fail-closed(배포 중단/즉시 키 회수), waiver·재시도·롤백 경로 미정의.
   - 선택지: (a) strict fail-closed 유지 (b) accepted-risk waiver + transient-failure retry + 단계 롤백 절차 추가
   - 판정: (a) 유지 — DESIGN LOCK L20 'deny 기본' 및 NEVER_AUTO 정책과 정합하는 보수적 선택. 예외(waiver)는 운영 필요 시 P2 인간 승인 경로로 추가 가능하며 현행이 정본 모순 없음.
6. **[KEEP]** `docs\sot 2\6-2_Security-Governance\05_advanced-security\security_test_pipeline_v3.md`:119, 208 (검증항목 #5 '19 직접 + 73 자동 RESOLVED') — STEP7-E 92건의 Evidence 단위 — 19건 직접 ID 매핑 + 73건은 8단계 파이프라인 통과 시 상속 일괄 RESOLVED(G4-7 baseline).
   - 선택지: (a) 파이프라인 상속 일괄 RESOLVED 유지 (b) 92건 전수 개별 row(ID/대응 단계/검증 방법/Evidence 위치) 작성
   - 판정: (a) 유지 — 정본 게이트 G4-7은 'STEP7-E 92건 100% RESOLVED 명세'만 요구하고 per-item Evidence 형식을 강제하지 않으며, L208이 19+73 분해를 투명 공시. 73건의 단계 귀속표 추가는 개선 옵션이지 의무 아님.
7. **[KEEP]** `docs\sot 2\6-2_Security-Governance\05_advanced-security\anomaly_detection_v3.md`:75 (정상 평균 - 2σ 추출 의심 임계값) — 추출 공격 entropy 탐지 민감도 = 2σ(단측 FP 약 2.3%) 통계 임계값 선택.
   - 선택지: (a) 2σ 유지(리콜 우선) (b) 3σ 완화(FP 최소화) (c) 사용자군별 동적 임계값
   - 판정: (a) 유지 — 원 finding의 NEVER_AUTO 모순부(자동 90일 차단)는 객관결함(mf_in i15)으로 이미 교정되어 L76이 '자동 throttle + P2 인간 승인 후 90일 차단'을 명시. 인간 승인 게이트가 후단에 있으므로 2σ는 탐지 리콜 우선의 합리적 선택이며 임계값 LOCK 부재로 정본 무모순.
8. **[KEEP]** `docs\sot 2\6-2_Security-Governance\01_ai-code-security\gdpr_compliance.md`:173 (§6.1 #4 Vector Embeddings 암호화 ❌ '벡터 자체는 PII 아님') — Vector Embeddings를 비PII로 분류하여 SQLCipher 암호화 대상에서 제외(보유 기간은 Memory cascade 적용).
   - 선택지: (a) 비PII 분류 + 암호화 제외 유지 (b) 파생 개인정보로 취급하여 암호화·접근통제·재식별 위험 평가 추가
   - 판정: (a) 유지 — DESIGN LOCK L13은 암호화 방식(AES-256-CBC)만 LOCK하고 적용 대상 카테고리를 강제하지 않으며, 삭제 cascade(§4.1 scope에 vector_embeddings 포함)가 이미 정의되어 L15 §2.4 무모순. 임베딩 역추론(inversion) 위험 평가 Evidence 추가는 권장 개선.
9. **[KEEP]** `docs\sot 2\6-2_Security-Governance\01_ai-code-security\guardrails_ai_l2_output.md`:57-67 (on_fail=FIX), 113, 168-170 (위험 함수/시크릿/SQLi → FIX) — L2 출력의 위험 함수·하드코딩 시크릿·SQLi 취약 코드에 대한 실패 처리 = FIX 자동 제거/마스킹/파라미터 바인딩 교체(REFRAIN/REASK 아님).
   - 선택지: (a) FIX 자동 수정 유지 (b) 위험 함수·SQLi는 REFRAIN 또는 REASK로 강등 + diff/테스트/승인 조건 부가
   - 판정: (a) 유지 — DESIGN LOCK L7은 L2 역할(출력 품질·안전성 검증)만 정의하고 실패 액션을 강제하지 않으며, L20 NEVER_AUTO는 P1+ '승인' 금지 축으로 안전 방향 출력 필터링 자동 조치와 무관. FIX 적용 내역은 L2Result.fixes_applied + 감사 로그(T-09)로 추적됨.
10. **[KEEP]** `docs\sot 2\6-2_Security-Governance\05_advanced-security\anomaly_detection_v3.md`:83-85 (§3.4 V3 일반 15 req/min) vs AUTHORITY_CHAIN.md:90,139 (L16 '10 req/min 기본') — V3 모드 일반 사용자 rate limit을 LOCK L16 기본값 10 대비 15 req/min으로 상향하는 모드별 파생값 선택.
   - 선택지: (a) V3=15 req/min 유지(L14 자율 L3 인용) (b) 전 모드 10 req/min 고정
   - 판정: (a) 유지 — DESIGN LOCK L16 원문은 '10 req/min 기본'으로 기본값(default) 정의이며, §3.4 표가 V1=10 (LOCK L16)을 보존하고 V3 값을 'L14 자율 L3 통합' 인용과 함께 모드별 파생으로 명시. LOCK 재정의가 아닌 모드별 설정으로 정본 무모순.
11. **[KEEP]** `docs\sot 2\6-2_Security-Governance\05_advanced-security\anomaly_detection_v3.md`:76 ('90일 grace 차단') vs AUTHORITY_CHAIN.md:123 (L5 grace period 24h) + red_team_automation_v3.md:133,143 + security_test_pipeline_v3.md:68 ('90일 grace skip') — 'grace' 용어를 HMAC 키 순환 유예(24h, L5)와 사용자/공격 90일 차단 기간 양쪽에 사용하는 명명 선택.
   - 선택지: (a) 현행 용어 유지 (b) 차단 측을 '90일 정지(suspension)' 등 별도 용어로 개명 + 해제 조건/승인권자 Policy화
   - 판정: (a) 유지 — 정본 용어 레지스트리 LOCK 부재로 명명은 설계 선택이며, 각 사용처에 기간(24h vs 90일)과 LOCK 근거(L5 vs L20)가 병기되어 실질적 해석 충돌이 차단됨. 차기 개정 시 (b) 권장하나 의무 아님.
12. **[KEEP]** `docs\sot 2\6-2_Security-Governance\05_advanced-security\security_test_pipeline_v3.md`:202-219 (§11 forward-defined), 229 (G4-5) + anomaly_detection_v3.md:170-193 + AUTHORITY_CHAIN.md:402 — Phase 5 entry-gate G4-5 'production 실측 baseline'의 통과 의미를 검증 항목 forward-defined 명세 완료(실측 staging 7일은 이월)로 정의하고 Status=APPROVED 처리.
   - 선택지: (a) 명세 완료 기준 게이트 유지 (b) DESIGN_APPROVED / IMPLEMENTATION_VERIFIED 상태 분리 + 실측 Evidence 파일 존재 시에만 baseline 완료 전환
   - 판정: (a) 유지 — AUTHORITY_CHAIN §7.5(L402) 자체가 G4-5 PASS 근거를 '43 검증 항목 forward-defined + staging 7일 명세'로 정의하여 게이트 의미가 정본 수준에서 일관(SPEC 단계 산출물 특성). 실측 상태 분리는 Phase 5 운영 개선 옵션.
13. **[KEEP]** `docs\sot 2\6-2_Security-Governance\02_hmac-timing-defense\api_key_management.md`:27-42 (V1 .env + 0600 + .gitignore) + hmac_agent_auth.md:85 ('V1: .env+dotenv / V2: HashiCorp Vault KV v2') — 키 저장 아키텍처 단계화 — V1은 .env(chmod 0600, .gitignore 필수), V2부터 HashiCorp Vault KV v2 + Docker secrets/K8s SealedSecrets 배포.
   - 선택지: (a) V1 .env → V2 Vault 단계적 도입 유지 (b) V1부터 OS keychain/Vault 필수화 + local-dev 한정 문구·백업 제외·긴급 폐기 runbook 동일 블록 고정
   - 판정: (a) 유지 — 로컬 데스크톱 V1 범위에서 .env 0600 + gitleaks pre-commit(hmac_agent_auth L85)은 통상 관행이며 정본 금지 규정 없음. hmac_agent_auth L85가 V1/V2 경로를 명시 분리하고 키 유출 시 P0 즉시 대응(L203)이 정의됨. V1 local-dev 한정 문구 추가는 개선 옵션.

> notes: 방법론: (1) 입력 4파일 전수 대조 — clc 31건, tight 24건(clc 부분집합, 신규 0), GP-A 22건(SG-62-001~022), mf_in 객관결함 26건(i0~i25). (2) 제외 처리: [객관 중복] T8-002/003/035/037/040/045/046/047/051/067/071/081, T6-102/126, T8-135, SG-62-001/002/003/005/006/007/010/011/012/013/014/015/018/020 → mf_in i0~i25와 1:1 매핑 확인. [verify=refuted 오탐] T8-026/079/133/134, T6-108, T8-116/117 7건 제외(L9 '일반 10분/HITL 5분'은 AUTHORITY_CHAIN.md:83,157에 실존하므로 T6-108/T8-116/117의 '정본 부재' 주장은 디스크 반박). [분해 처리] T8-073: NEVER_AUTO 모순부=객관 i15(디스크 기교정: anomaly L76 'throttle+P2 승인'), 2σ 임계값부만 주관 등재. T8-091: mf_in i15 defect 본문이 '안전 방향 예외(§5)' 논의까지 포괄 + L20 

### 6-7_RT-BNP-DCL (13건)

1. **[KEEP]** `docs\sot 2\6-7_RT-BNP-DCL\01_rt-bnp-pipeline\breaking_detector.md`:L321 (p99 ≤ 2,500ms) / L324 (Timeout 2,500ms → V1 폴백) — NLP 추론 Timeout을 p99 SLA와 동일한 2,500ms로 설정해 SLA 경계 초과분을 즉시 V1 키워드 폴백으로 보내는 임계값 선택.
   - 선택지: (a) Timeout=p99 2,500ms 동일값(현행, 폴백 단순·보수적) (b) Timeout=p99+지터 여유(예 3,000ms) (c) p99 하향+Timeout 분리
   - 판정: KEEP — plan §14.2 폴백 전략(L1699 'ML 장애 시 V1 자동 폴백, R-67-2 정확성 우선')과 무모순이고 어떤 정본도 Timeout>p99를 요구하지 않음; 경계 1%를 검증된 V1 경로로 회수하는 것은 합리적 SLA 설계 선택.
2. **[KEEP]** `docs\sot 2\6-7_RT-BNP-DCL\01_rt-bnp-pipeline\fast_gate.md`:L261 (xss_pattern → fail("G3_MALICIOUS_URL")) / L147-149 (§3.5 G3 코드 3종) — XSS/콘텐츠 인젝션 탐지를 별도 reason_code 신설 없이 기존 G3_MALICIOUS_URL 코드로 귀속시키는 3-코드 택소노미 입도 선택.
   - 선택지: (a) G3 코드 3종 유지, 인젝션을 MALICIOUS_URL에 포함(현행) (b) G3_XSS/G3_CONTENT_INJECTION 코드 신설로 감사 분해능 향상
   - 판정: KEEP — AUTHORITY L16(CL-G3 필수 적용)과 §3.5 코드 표 어디에도 코드 개수·입도 규정이 없어 정본 위반 없음; 라벨 의미론은 설계 재량이며, 감사 분해능이 필요해지면 V2+에서 코드 추가 검토(권고 수준).
3. **[KEEP]** `docs\sot 2\6-7_RT-BNP-DCL\02_domain-context-layer\dcl_channels.md`:L120-121 (qod_fin 식) vs L161-162 (§3.4 공통식 completeness×0.10), 서술 L117 — DCL-FIN QoD에서 공통식의 completeness×0.10을 impact_score×0.10으로 치환(가중치 합 1.00 유지)하는 채널 특화 가중 구성 선택.
   - 선택지: (a) completeness→impact_score 치환(현행, 합 1.00 보존) (b) impact 추가 후 6항 재정규화 (c) 공통식 유지+impact 별도 보너스 항
   - 판정: KEEP — LOCK L13은 'QoD ≥ 0.5 → RAG 삽입' 임계만 고정하고 가중 구성은 미규정이므로 채널 특화 치환은 무모순; 다만 L117 '가중치로 추가한다' 서술을 'completeness를 impact_score로 대체'로 명확화하면 좋음(서술 명확화는 권고 수준, 정본 모순 아님).
4. **[KEEP]** `docs\sot 2\6-7_RT-BNP-DCL\02_domain-context-layer\rag_integration.md`:L182 (헤딩 'Part2 §6.10.2 verbatim') / L184 (출처 블록 '_index.md verbatim') — 헤딩에는 궁극 정본(Part2 §6.10.2), 출처 블록에는 근접 verbatim 운반체(02/_index.md)를 적는 2-hop 인용 관행 선택.
   - 선택지: (a) 2-hop 표기 유지(현행: 헤딩=궁극 출처, 블록=직접 인용원) (b) 양쪽 모두 Part2로 통일 (c) 인용 체인(Part2→_index→본문) 명시
   - 판정: KEEP — 인용된 I-3 L0 문구는 Part2 §6.10.2 계열 내용을 _index.md가 verbatim 운반하는 구조로 내용 모순이 없고, 정본 우선순위상 궁극 귀속(Part2)이 헤딩에 보존되어 있음; 혼동 방지용 체인 명시는 선택 사항.
5. **[KEEP]** `docs\sot 2\6-7_RT-BNP-DCL\01_rt-bnp-pipeline\breaking_detector.md`:§17.1 L625 (P/R/F1 ≥ 0.87 정식화) vs plan L1700 (§14.2 힌트 Precision≥0.90) — V2+ ML 성능 게이트를 §14.2 힌트의 P≥0.90/R≥0.85/F1≥0.87 분리값 대신 P/R/F1 일괄 ≥0.87로 정식 확정한 임계값 선택.
   - 선택지: (a) 일괄 ≥0.87(현행 §17 정식 확정, 카나리/재학습 트리거와 단일 기준) (b) 힌트대로 P≥0.90 분리 유지(허위 속보 최소화 강조)
   - 판정: KEEP — plan §14.2는 자기선언상 비구속 '기술 힌트'(L1690 'Phase 1 DH-1에서 정식 정의 예정', L1702)이고 DH-1 정본 위치는 breaking_detector §6+§17(§17.4 명시)이므로 본문 확정 0.87이 유효 정본, LOCK 위반 없음; P≥0.90 복원은 Decision으로 검토 가능한 선택지(AUD-012도 '완전 확정 불가' 인정).
6. **[KEEP]** `docs\sot 2\6-7_RT-BNP-DCL\01_rt-bnp-pipeline\breaking_detector.md`:L313 (§6.3 월 1회) / L627 (§17.1 weekly — '§6.3 "월 1회+성능 하락 즉시" 확장') vs plan L1698 — 모델 재학습 주기를 월 1회(힌트·§6.3)에서 weekly 정기 + drift KL>0.15 즉시로 강화 확정한 운영 주기 선택.
   - 선택지: (a) weekly 정기+drift 즉시 트리거(현행 §17) (b) monthly+성능하락 즉시(§14.2 힌트/§6.3 원안)
   - 판정: KEEP — §17.1 L627이 '§6.3 계승·강화'로 명시적 기록하고 weekly⊃monthly(상위 충족)여서 직접 모순 아님(clc verify=refuted와 일치); §14.2는 비구속 힌트이므로 DH-1 본문 확정이 정본.
7. **[KEEP]** `docs\sot 2\6-7_RT-BNP-DCL\RT_BNP_DCL_구조화_종합계획서.md`:L1590-1591 (§11 S-2/S-3 OPEN) · L1606-1613 (§12 FR-5/6 PARTIAL, 'Phase 10 S10-3 2026-03-27') vs FINAL_REVIEW_REPORT.md L40-45 (ALL PASS) — plan의 과거 시점 스냅샷(§11/§12)을 append-only로 보존하고 현행 게이트 상태는 후행 FINAL_REVIEW_REPORT(+§7.R)가 운반하는 문서화 컨벤션 선택.
   - 선택지: (a) append-only 보존+후행 리포트 supersede(현행 도메인 컨벤션) (b) §11/§12 in-place 동기화 (c) historical snapshot 배너 추가
   - 판정: KEEP — §12는 일자 명기 스냅샷('CONDITIONAL APPROVED — Phase 10 S10-3 2026-03-27')이고 §7.R(2026-06-02 genuine write)이 FR-5/6 PARTIAL→PASS 전환 근거(P4-2 §17/retraction_protocol)를 기록하므로 단일 현행 상태 결정 가능; byte-prefix 보존 강제(plan L1644)와 정합한 확립 컨벤션.
8. **[KEEP]** `docs\sot 2\6-7_RT-BNP-DCL\01_rt-bnp-pipeline\fast_gate.md`:L194/L203 (source_weight ≥ 0.4 PASS) · L213-214 (SNS 0.40 경계값 태깅 / SNS 단일 <0.40 FAIL); source_adapters.md L300; breaking_detector.md L361 — SNS source_weight 0.40을 즉시 차단 대신 '경계값 PASS + sns_cross_check_required 태깅 + 사후 30분 재검증(L7) + Velocity 교차확인 업그레이드'로 처리하는 게이트 강도 선택.
   - 선택지: (a) 경계 태깅+사후 검증 조합(현행) (b) ≤0.40 즉시 차단 (c) 교차확인 미완 시 BREAKING-P0/P1 승급 금지 하드 게이트 추가
   - 판정: KEEP — AUTHORITY L5가 SNS 0.4를 '다수 소스 교차 확인 시' 조건부로 정의하고 fast_gate L214가 단일 SNS <0.40 FAIL 경계를, source_adapters L300이 교차확인(≥2 독립 소스 60초 내) 업그레이드 경로를, breaking_detector L361이 강등 금지+교차확인 요구를 각각 정의 — 다층 보완이 정본에 존재하므로 enforcement 강도는 설계 재량; 하드 게이트 추가는 R-67-2 강화 옵션(권고 수준).
9. **[KEEP]** `docs\sot 2\6-7_RT-BNP-DCL\02_domain-context-layer\dcl_channels.md`:L192-201 (§3.5 resolve_conflict: 점수 가중평균 + primary_source 본문 단독 채택) — 소스 충돌 해결에서 qod/accuracy는 신뢰도 가중 평균, 텍스트 본문은 최고 가중치 소스 단독 채택하는 알고리즘 선택.
   - 선택지: (a) primary 본문 채택+contributing_sources 추적(현행, 단순·저비용) (b) claim-level merge+conflicting_claims 필드 (c) LLM 합성 요약
   - 판정: KEEP — §3.5가 DH-3(DCL Aggregator 알고리즘)의 정본 정의 위치(AUTHORITY §9.4 L219)로 확정되어 있고 contributing_sources로 다중 소스 추적성을 보존 — 알고리즘 선택은 설계 재량이며 어떤 LOCK/RULE도 claim-merge를 요구하지 않음.
10. **[KEEP]** `docs\sot 2\6-7_RT-BNP-DCL\RT_BNP_DCL_구조화_종합계획서.md`:L1645 (§13.3 02에 'NEW 1 retraction_protocol' 사전 배정, 2026-05-19) vs L1479 (§7.R 01_rt-bnp-pipeline 실기록, 2026-06-02) + 01/_index.md L154 — retraction_protocol.md의 canonical 위치를 §13.3 forward-defined 배정(02_domain-context-layer)이 아닌 01_rt-bnp-pipeline으로 확정한 파일 배치 선택.
   - 선택지: (a) 01 배치(현행 디스크 실물+§7.R+01/_index APPROVED 등재, RETRACTION=RT-BNP 파이프라인 소유 LOCK L8) (b) §13.3 원안대로 02 배치
   - 판정: KEEP — 후행 §7.R(genuine write 실기록)이 선행 §13.3(일자 명기 forward-defined 스냅샷)을 supersede하며 디스크 실물·01/_index L154 등재·LOCK L8 소유권 모두 01로 일관 — §13.3 표는 append-only 보존된 이력으로 정본 모순 아님.
11. **[KEEP]** `docs\sot 2\6-7_RT-BNP-DCL\01_rt-bnp-pipeline\_index.md`:L140-142 (ISS-1~3 '🔄 미착수') · L150-153 ('📋 Phase 1') vs L154/L172-192 (Phase 4 APPROVED·footer); AUTHORITY_CHAIN.md L210-211 '예정'; INDEX.md L140 '(예정 step 8)' — V1 메타 파일 본문의 초기 상태 표기(미착수/예정)를 byte-prefix 보존하고 상태 갱신은 footer/후행 리포트 append로만 수행하는 컨벤션 선택.
   - 선택지: (a) append-only footer 컨벤션(현행, V1 SHA UNCHANGED 보존과 정합) (b) in-place 상태 동기화 (c) stale section 배너 부착
   - 판정: KEEP — 도메인 전반의 V1 byte-prefix SHA UNCHANGED 강제(plan L1644, _index footer L179/L188의 verify 체인)와 정합하며, ISS-1~3 실해소는 AUTHORITY §9.4 L223('DH-1/DH-2 Phase 1 정본 정의 완료')과 FINAL_REVIEW가 운반 — 현행 상태 결정 규칙(후행 footer 우선)이 존재하므로 정본 모순 아님.
12. **[KEEP]** `docs\sot 2\6-7_RT-BNP-DCL\AUTHORITY_CHAIN.md`:L245 (§9.6 최종확정 row 6) · L247 (폐문단) · L248 (STEP_B 시점 구버전 row 6 잔존) — §9.6 표를 최종확정(L245)하면서 STEP_B 시점 구버전 row 6(L248)을 삭제하지 않고 폐문단 뒤에 잔존시킨 append-only 이력 보존 선택.
   - 선택지: (a) 잔존 보존(현행, append-only 이력 관행) (b) L248 제거로 표 정리 (c) 'STEP_B 시점 이력' 주석 부착
   - 판정: KEEP — L245(STEP_C ✅ 최종)와 L248(STEP_B 시점 '갱신 예정')은 시계열상 모순 없는 신구 버전 관계이고 §9.6 최종확정 표가 유효 상태를 단일하게 운반 — 어떤 LOCK/RULE도 위반하지 않는 가독성 사안; 정리한다면 L248 한 줄 제거가 유일 후보이나 정본 모순이 아니므로 KEEP.
13. **[KEEP]** `docs\sot 2\6-7_RT-BNP-DCL\FINAL_REVIEW_REPORT.md`:L99 ('7 L3 production 파일은 per-file Status 필드 부재 → 본 리포트 + INDEX 논리 등재로 APPROVED 확정 (production .md byte-EXACT 보존)') — 7개 L3 production 파일에 per-file Status 헤더를 넣지 않고 FINAL_REVIEW+INDEX 논리 등재로 APPROVED를 확정하는 승인 상태 운반 방식 선택.
   - 선택지: (a) 리포트+INDEX 논리 등재(현행, production byte-EXACT 보존) (b) 각 파일 헤더에 Status: APPROVED 또는 status_ref 필드 추가
   - 판정: KEEP — V1 Pure/baseline byte-prefix SHA UNCHANGED 보존 강제와 양립하는 유일한 방식이며 6-6/6-7/6-8 도메인 공통 확립 선례(L3_COMPLETENESS+FINAL_REVIEW+INDEX 3중 등재로 추적성 확보) — per-file Status 주입은 SHA 체인을 깨므로 오히려 정본 보존 규칙과 충돌.

> notes: 앵커 13건과 정확히 일치(짜맞춤 아님 — 잔여 풀 산술이 자연 수렴). 도출 과정: clc 18 + GPT 16 = 34건을 클러스터링하면 ~27개 distinct cluster이고, mf_in 객관결함 14건이 14개 클러스터(ACK 30/60/600s=T8-002·AUD-003, 비용 LOCK L15=T8-032/033/039/081/082·AUD-001, 임베딩 768=T8-054, cl_g3_passed=T8-063·AUD-009, 무효화 4대상=T8-080, EventType 3종=T5-030·AUD-007, keyword multiset=T8-009, list/dict=AUD-010, emit_rag 무재시도=T8-057, fail-open=AUD-004, 인증 부재=AUD-005, T3 reserved=T8-036, YAML priority=T8-055, dedup 2종=AUD-008)를 커버 — 잔여 13개 클러스터 전부가 검증 가능한 정본 위반 없는 설계 선택으로 판정(오탐 0, 단순 표기로 강등한 항목 0: AUD-015도 append-only 이력 관행 범주로 등재). 전 항목 디스크 실측 완료, action 13/13 KEEP·CHAN

### 3-10_Agent-Protocol-Interoperability (12건)

1. **[KEEP]** `docs\sot 2\3-10_Agent-Protocol-Interoperability\02_service-integration\llm_gateway.md`:199 (대조: 03_data-exchange/event_bus.md L238) — LLM Gateway rate-limit 백오프는 3회(1s,2s,4s) 후 폴백, Event Bus 핸들러 재시도는 5회(1,2,4,8,16s)로 컴포넌트별 차등 재시도 정책을 채택.
   - 선택지: (a) 도메인 전역 단일 재시도 정책으로 통일(3회 또는 5회) (b) 컴포넌트별 차등 유지 — 외부 429는 짧게+폴백, 내부 버스는 길게+dead letter
   - 판정: KEEP — RULE/PLAN/LOCK 어디에도 전역 재시도 규칙이 없고, 외부 rate-limit(2순위 provider 폴백 경로 존재)과 내부 이벤트 전달(at-least-once 지향+dead letter)은 실패 특성이 달라 차등이 합리적. 각 문서에 차등 사유 1줄 명시만 권장.
2. **[KEEP]** `docs\sot 2\3-10_Agent-Protocol-Interoperability\04_deployment-scaling\config_spec.md`:258 — 배포환경(dev/staging/prod)별 LLM 예산 상한을 40K/60K/93K로 매핑하고 staging에 LOCK 비정본 값 60,000을 부여한 환경별 예산 설계.
   - 선택지: (a) 환경축을 V-tier LOCK 값에만 1:1 고정(staging도 40K 또는 93K) (b) V-tier 상한 이하 범위에서 환경별 독자 상한 허용(현행)
   - 판정: KEEP — LOCK-AP-09 정본은 V1/V2/V3=40K/93K/266K로 V-tier 예산만 규정하며 배포환경 상한은 미규정. staging 60K는 V2 93K 이하로 정본 무모순(실측 L258 dict 확인). 다만 dict명 lock_ap_09 → env_budget_cap 류 개명으로 LOCK 오인 표기 해소 권장(표기 수준).
3. **[KEEP]** `docs\sot 2\3-10_Agent-Protocol-Interoperability\04_deployment-scaling\logging_spec.md`:237-247 — STEP7-K L1138 정본('30일 V1/90일 V2/1년 V3')을 로그 행에만 verbatim 적용하고, 트레이스 14/30/90·메트릭 30/90/400·LLM 365/730/2555·감사 2555일 등 카테고리별 보존기간을 자체 설계로 확장.
   - 선택지: (a) 인용 범위(로그)만 기재, 나머지 카테고리는 미정 처리 (b) 카테고리별 확장 보존표 유지(현행)
   - 판정: KEEP — 정본 원문은 '로그' 보존만 규정하고 §8 헤더가 출처를 명시하며 로그 행은 30/90/365 그대로 보존(L243 실측). 추가 카테고리 보존값은 설계자 재량 영역. 표에 '로그 행만 verbatim, 나머지는 본 도메인 설계' 각주 1줄 권장.
4. **[KEEP]** `docs\sot 2\3-10_Agent-Protocol-Interoperability\04_deployment-scaling\logging_spec.md`:282 — 정상 INFO 로그 샘플링 1%(readiness probe 포함), 정상 LLM call 10%, WARN/ERROR/LOCK 위반 100%라는 비용 제어 샘플링 비율 선택.
   - 선택지: (a) INFO 10~100% 상향으로 비오류 트레이스 재구성 용이화 (b) 1% 유지로 비용 절감(현행)
   - 판정: KEEP — 정본에 샘플링 하한 규정이 없고 WARN 이상·LOCK 위반 100%로 사고 조사 경로는 보존(L284-286 실측). §9.2 관측 소계가 LOCK-AP-09 V2 93K의 26%인 비용 구조상 1%는 합리적 선택. 필요 시 트레이스 테일 샘플링 보강은 후속 옵션.
5. **[KEEP]** `docs\sot 2\3-10_Agent-Protocol-Interoperability\01_framework-adapters\moa_pattern.md`:105 (+185, 279) — V1=3 상한(LOCK-AT-014) 하에서 moa_full_4_model(4 proposer+aggregator)을 V2 조건부 모드로 enum과 비용표에 선정의한 forward-design.
   - 선택지: (a) V1 문서에서 4-model 모드 삭제 후 V2 마이그레이션 시 추가 (b) enum 선정의 + V1 런타임 게이트 차단(현행)
   - 판정: KEEP — §2.3(L59)이 'V2=10 확장은 6-3 V2 마이그레이션 선행 시에만 적용'을 명시하고 테스트 #7(L279)이 V1에서 Proposer=4를 LOCK-AT-014 위반으로 거부해 정본 가드 작동(LOCK 우선순위 보존). V2 모드 선정의는 설계 선택.
6. **[KEEP]** `docs\sot 2\3-10_Agent-Protocol-Interoperability\01_framework-adapters\tool_memory_benchmark.md`:260 — VBS12_BELOW_THRESHOLD/TOOL_ALL_FAILED 등 운영 실패 에스컬레이션 페이로드의 채널을 I-20(사후분석)으로 선택 — I-19(HITL 승인)가 아님.
   - 선택지: (a) I-19로 변경(승인형 에스컬레이션 간주) (b) I-20 유지(운영 실패 사후 보고 채널, 현행)
   - 판정: KEEP — guardrail_rules 정본은 I-19를 SG-009 등 HITL '승인'에 매핑하며, 본 §9 페이로드는 승인 요청이 아닌 실패 보고(§8 L256: VBS-12<75는 '품질 경고, 차단 아님'). llm_gateway §8(L212)도 동일 I-20 관례. mf_in 객관결함군(LOCK-AP-10 HITL 승인 경로의 I-20 오기)과 달리 정본 무모순.
7. **[KEEP]** `docs\sot 2\3-10_Agent-Protocol-Interoperability\06_autonomy-safety\constitutional_ai.md`:151, 155, 163-173 — 윤리 composite < 0.85를 LOCK-AP-10(0.50 누적)과 별개의 R-13-1 HITL 독립 트리거로 운용하는 이중 임계 설계(penalty -0.25는 누적 기여만, R-13-1 명칭 재사용).
   - 선택지: (a) 윤리 위반도 LOCK-AP-10 누적식으로만 처리하고 0.85 독립 트리거 폐지 (b) 0.85 독립 HITL(R-13-1) + 0.50 누적(LOCK-AP-10) 병행(현행)
   - 판정: KEEP — PLAN 3.0(종합계획서 L1526/L1545/L1836)이 '윤리 점수 < 0.85 → R-13-1 HITL 트리거'를 Phase 4 entry-gate로 직접 명시해 정본이 이 설계를 승인. §8.1(L163, L173)이 LOCK-AP-10 재정의 0·참조자임을 선언해 DEFINED-HERE 무모순. R-13-1(L3 전환 HITL) 메커니즘 재사용은 계획서 사양.
8. **[KEEP]** `docs\sot 2\3-10_Agent-Protocol-Interoperability\05_self-evolution\agent_marketplace.md`:80-91 (+104) — 마켓플레이스 등록 인입 경로의 anti-abuse(제출 rate-limit/중복·replay 방지/manifest 서명 선검증)를 자체 구현하지 않고 6-2 보안 심사 단계(코드 서명+샌드박스 행동분석)에 위임한 보안 아키텍처 선택.
   - 선택지: (a) 인입 단계 자체 rate-limit+서명 선검증 추가 (b) §5 직렬 심사 파이프라인(자동테스트→6-2 보안심사→interop→HITL)에 위임(현행)
   - 판정: KEEP — 정본에 인입 단계 anti-abuse 의무 규정이 없고 §5(L102-108)가 승인 전 6-2 보안심사·confidence<0.50 HITL(LOCK-AP-10) 게이트를 직렬 배치해 위협이 배포 전 차단됨. 6-2 핸드오프에 인입 rate-limit 책임 소재 1줄 명시 권장.
9. **[KEEP]** `docs\sot 2\3-10_Agent-Protocol-Interoperability\04_deployment-scaling\migration_guide.md`:169 — V2-Phase 2 범위 문서의 config 호환성 매트릭스에 v2.0→v3.0 breaking 행을 자동변환기 ❌·수작업+HITL L3로 선기재한 forward-호환성 문서화 선택.
   - 선택지: (a) v3.0 행 삭제 후 V3 이관 시 추가 (b) breaking 사실과 수작업·HITL 전제만 선언(현행)
   - 판정: KEEP — plan §7.5 V3 deferral과 무모순: 해당 행은 v3 마이그레이터를 구현하지 않고(자동 변환기 ❌, L169 실측) breaking 성격과 HITL 절차만 예고. 매트릭스 완결성을 위한 문서화 재량.
10. **[KEEP]** `docs\sot 2\3-10_Agent-Protocol-Interoperability\06_autonomy-safety\guardrail_rules.md`:168 (§3.2; §3.1 L150-162) — 3-phase 가드(pre/runtime/post) 중 pre-action만 의사코드로 제공하고 runtime(SG-006~008)/post-action(SG-009~010)은 §3.1 다이어그램+규칙표로 명세한 문서화 깊이 선택.
   - 선택지: (a) 3 phase 전부 의사코드 제공 (b) 대표 1 phase 의사코드 + 표/다이어그램 기반 명세(현행)
   - 판정: KEEP — 정본 요구는 규칙·임계·라우팅의 명세이며 §3.1(L150-162)이 SG-006~010 전부의 트리거와 라우팅(I-19 escalate, deny+kill, log+alert+HITL L3)을 규정. 의사코드 제공 범위는 문서화 재량으로 정본 무모순. 후속 보강 권장 수준.
11. **[KEEP]** `docs\sot 2\3-10_Agent-Protocol-Interoperability\03_data-exchange\message_format.md`:276 (+290) — input-required↔working HITL 진자 루프 cap(최대 3회 초과 시 canceled 강제 전이)을 §3.5.3 prose로 규정하고, §3.3 전이표 guard 등재와 MSG-080 오류코드 등재를 Step 7로 명시 이연한 선택.
   - 선택지: (a) 즉시 §3.3 guard 컬럼 + §8 오류표에 MSG-080 등재 (b) prose 규범 + 명시적 이연 기록(현행)
   - 판정: KEEP — cap=3·canceled 동작 자체는 L276에 규범적으로 정의되어 구현 가능하고, 문서가 '§3.3 guard 에 명시적 limit 추가 권고'(L276)와 'MSG-080 후보 — Step 7 에서 등재 검토'(L290)로 이연을 자가 기록. 등재 시점은 설계 일정 선택이며 정본 무모순.
12. **[KEEP]** `docs\sot 2\3-10_Agent-Protocol-Interoperability\AGENT_PROTOCOL_INTEROPERABILITY_상세명세.md`:230-231 — 루트 상세명세 ServiceRegistration 스키마에서 AuthConfig/RateLimitConfig를 타입명만 선언하고 필드 상세(인증 갱신·scope·429 처리)를 하위 컴포넌트 정본에 위임한 스키마 상세도 선택.
   - 선택지: (a) 루트에서 두 타입을 필드 단위로 전체 정의 (b) 루트는 인터페이스 골격, 실계약은 02_service-integration 정본(현행)
   - 판정: KEEP — 인증·rate-limit 실계약은 02 정본에 존재(llm_gateway §7 L199 429 backoff 1,2,4s·3회 폴백, L201 인증 401/403→갱신+HITL)하고 루트 상세명세는 요약 정본 역할. 골격+하위 상세 분담은 정본 우선순위와 무모순. 루트에 '상세는 02_service-integration 정본' cross-ref 1줄 권장.

> notes: 재도출 방법: clc 44건 + tight 31건(부분집합) + GPT 17건에서 mf_in 객관결함 33건 매핑분을 제외하고, 잔여 전수를 디스크 실측(file:line) 후 분류. 전 항목 실측 확인 완료, 표본 아님. 12건 전원 KEEP(정본 모순 0건) — CHANGE/edit 없음. [제외 내역] (1) 객관결함 중복: T8-002, T6-031/032/033/035, T5-082, T8-052, T8-056, T8-069/070/073, T8-083, T8-092/093, T8-125, T8-158/159/160/168/169, T8-203, T8-230/242, T6-241, AP-AUDIT-001/003/004/006/007/008/009/010/011/012/013/014, AP-AUDIT-017(mf_in i=31 REPLAN_LIMIT와 동일 위치 중복), T8-029(mf_in i=31 동일). (2) 오탐(디스크/의미 반박): T8-001·T6-012(LOCK-AT-004 깊이 해석 반박), T8-013(langgraph L303-312 실측 — open→half_open 전이 시 failure_count 미리셋이라 half-open

### 6-9_Brain-Adapter-HAL (12건)

1. **[KEEP]** `docs\sot 2\6-9_Brain-Adapter-HAL\02_hal-interface\hal_v2_deployment.md`:66-70 (hal), 85-89 (litellm) — Docker healthcheck 프로브 파라미터를 interval=30s/timeout=30s/retries=3으로 설정 (timeout=interval 동일값).
   - 선택지: 현행(timeout 30s=interval) vs 프로브 timeout 분리 단축(예: 5~10s, retries 유지)
   - 판정: KEEP — interval 30s는 TH-4 health_check 30s 정합(L68 주석이 interval에만 TH-4 인용), 컨테이너 프로브 timeout 값은 RULE/PLAN/LOCK 어느 정본도 규정하지 않아 모순 없음; Phase 5 운영 튜닝에서 timeout 5s 하향은 선택지.
2. **[KEEP]** `docs\sot 2\6-9_Brain-Adapter-HAL\01_multi-brain-adapter\P1-1_brain_adapter_v1_spec.md`:102,113,125 (§3 표) vs 193-208 (§5 resolver+매핑 표) — 설정 키 ENV 네이밍을 SDK 표준(OLLAMA_HOST/OPENAI_API_BASE) 재사용+일부 VAMOS_BRAIN_* 혼용으로 하고, YAML 경로를 §3 약식(config.yaml:ollama.host)/§5 전체경로(brain.ollama.host)로 병기.
   - 선택지: §5 키별 매핑 표를 정본으로 유지(SDK 표준 ENV 우선) vs VAMOS_BRAIN_* 단일 규칙으로 전면 통일
   - 판정: KEEP — LOCK-69-6(ENV > config.yaml > 코드 기본값, AUTHORITY L50)은 어느 네이밍으로도 무모순; §5 표(L200-208)가 키별 명시 정본 매핑이고 resolver 의사코드(L194-198)는 일반형, §3의 config.yaml:ollama.host는 brain.* 전체경로의 약식 표기로 정합. 구현 시 §5 표만 참조하면 일관 동작.
3. **[KEEP]** `docs\sot 2\6-9_Brain-Adapter-HAL\03_llm-routing\P1-3_llm_router_v1_spec.md`:208-212 (vs 03_llm-routing/_index.md:113-117) — 비용 게이트 기준 변수를 P1-3은 잔여율(cost_budget_remaining_pct), _index는 소진율로 framing하고 경계 0/100%를 deny에 귀속.
   - 선택지: 잔여율 단일화 vs 소진율(used_pct) 단일화 vs 현행 병기(괄호 동치 환산)
   - 판정: KEEP — P1-3 표가 괄호로 소진율 동치를 병기(0~20 잔여=80~100% 소진, ≤0=100% 소진)해 _index §3.3·TH-3과 수치 완전 동일하며, deny=≤0은 LOCK-69-7(RULE 1.3 §5) 정합; P1-4 next_candidate(L232)가 <=0.0 deny를 선평가해 경계 모호성 없음.
4. **[KEEP]** `docs\sot 2\6-9_Brain-Adapter-HAL\04_fallback-chain\P1-4_fallback_chain_v1_spec.md`:193-194, 222-227, 446 (AUTHORITY_CHAIN.md:57, 종합계획서:180/628/634) — R-69-3 max_transitions=2 — LOCK-69-8 4-모델 체인 전체 소진 보장보다 지연/비용 가드를 우선하는 전환 상한 값 선택.
   - 선택지: A) max_transitions=3 상향(4-모델 전체 도달 보장) B) 현행 2 유지+로컬 tail은 F7 직행 등 실패유형별 경로로 도달 C) 로컬 전환 카운터 미소모 예외
   - 판정: KEEP — R-69-3(PLAN 종합계획서 L180)과 AUTHORITY L57(LOCK-69-8 집행부 '최대 2회 전환 후 deny')이 모두 정본으로 2를 고정; V1 3-모델 _BASE_ORDER에선 2회로 Ollama 도달(U-FB-3 L446 정합), V2/V3 최악경로 local 미도달은 F7 네트워크 오류 시 로컬 직행(계획서 L634)으로 보완된 의도적 트레이드오프. 정본 변경 불요.
5. **[🔧CHANGE]** `docs\sot 2\6-9_Brain-Adapter-HAL\03_llm-routing\cost_optimization_report.md`:42 (동일 연관: 303, 326, 344) — 라우팅 가중치(quality 0.6/cost 0.3/latency 0.1)를 LOCK-69-3 '적용' 행에 묶어 표기한 편집 선택.
   - 선택지: LOCK-69-3 행에 비용 가중치 포함(현행) vs ToolRegistry 경유만 남기고 가중치는 03 §3.4 설계값으로 분리 표기
   - 판정: CHANGE — DESIGN LOCK 정본 AUTHORITY_CHAIN.md L47은 LOCK-69-3을 'ToolRegistry 경유 필수(직접 URL/SDK/코드 호출 금지)'로만 정의(D2.0-04 §7.2); 비용 가중치는 03 _index §3.4 라우팅 설계값으로 LOCK-69-3 범위 밖 → 본문 표기가 DESIGN LOCK과 모순이므로 분리. L303/L326/L344의 동일 연관도 후속 동기화 필요.
6. **[KEEP]** `docs\sot 2\6-9_Brain-Adapter-HAL\03_llm-routing\routing_performance_benchmark.md`:391-403 (PASS 표), 477 (M-P4-3-1) — staging 7일/SPEC 기반 baseline 수치(p95 1.42초, 102 QPS 등)를 ✅ PASS로 표기하고 production 실계측을 Phase 5로 위임하는 보고 컨벤션.
   - 선택지: baseline을 PASS로 표기+방법론 주석 공개(현행) vs 실계측 완료까지 DEFER 표기
   - 판정: KEEP — M-P4-3-1(L477)이 'staging 7일 측정 baseline, production 실계측은 Phase 5 갱신'을 명시 공개하고 §11 Phase 5 entry-gate(L467-471)가 재측정을 게이트로 강제 → 검증 가능한 정본 위반 없는 판정 시점 선택.
7. **[KEEP]** `docs\sot 2\6-9_Brain-Adapter-HAL\03_llm-routing\cost_optimization_report.md`:16-26, 377 (M-P4-4-1), 390 — 비용 절감 ~38%(트래픽 믹스 가정 기반 추정)를 30%+ 목표 PASS 근거로 사용하는 판정 시점 선택.
   - 선택지: 추정치 기반 목표 PASS+방법론 주석 공개(현행) vs Phase 5 실계측까지 측정 PASS DEFER
   - 판정: KEEP — M-P4-4-1(L377)이 '~38%는 트래픽 믹스 가정 기반 추정, production 실계측은 Phase 5 staging 7일 갱신'을 명시; LOCK-69-7 V3 ₩26.6만 자동 차단은 절감치와 무관하게 별도 강제되어 정본 무모순.
8. **[KEEP]** `docs\sot 2\6-9_Brain-Adapter-HAL\02_hal-interface\hal_v3_deployment.md`:145-157 — API 키 주입 메커니즘 — native K8s Secret(stringData, <sealed> placeholder) 예시 채택, SealedSecret/외부 vault는 대안 허용.
   - 선택지: native Secret(+etcd 암호화/RBAC 보강) vs SealedSecret vs ExternalSecret/Vault 중 택일
   - 판정: KEEP — L157 정책 자체가 'Secret(또는 SealedSecret/외부 vault)' 3옵션을 명시 허용하고 본질 규제는 ConfigMap 평문 금지(6-2 정합)이며 예시 값은 placeholder; 메커니즘 단일화는 Phase 5 운영 결정 사항으로 정본 무모순.
9. **[KEEP]** `docs\sot 2\6-9_Brain-Adapter-HAL\02_hal-interface\hal_v3_deployment.md`:159-187 (정책 표 L183-187) — Ingress 보안에서 'TLS 강제 + 4-1 Tauri 클라이언트 인증'을 정책으로 선언하되 구체 인증 메커니즘(mTLS/JWT/OIDC/API key)은 미고정.
   - 선택지: mTLS vs JWT/OIDC vs API key+allowlist — 4-1 도메인 합류 시 택일
   - 판정: KEEP — 6-9 정본 어디에도 특정 클라이언트 인증 메커니즘을 규정하지 않으며 인증 주체가 4-1 Tauri 측이므로 메커니즘 선택은 4-1 연동 시점의 설계 결정; L187 정책 선언으로 요구사항은 LOCK됨. Phase 5/4-1 진입 시 단일 메커니즘 고정 권고.
10. **[KEEP]** `docs\sot 2\6-9_Brain-Adapter-HAL\02_hal-interface\hal_v3_deployment.md`:216 — vLLM 컨테이너 이미지 태그 정책 — vllm/vllm-openai:latest(mutable) 사용.
   - 선택지: latest(현행) vs 버전 태그/digest pinning + 업그레이드 게이트
   - 판정: KEEP — 모델 자체는 정본 고정(meta-llama/Llama-3.1-8B-Instruct, Part2 L3894 cite, L219)이고 이미지 태그 정책은 정본 미규정 영역이라 모순 없음; 재현성/롤백 위해 Phase 5 배포 시 digest pin 전환을 권고(현 시점 스펙 문서로는 유지 가능).
11. **[KEEP]** `docs\sot 2\6-9_Brain-Adapter-HAL\BRAIN_ADAPTER_HAL_구조화_종합계획서.md`:940 (P1-4 spec L204-209, L217) — V1 전용 동일모델 타임아웃 재시도(v1_timeout_retries=3, 전환 카운터 미소모)를 R-69-3 전환 2회와 별도 카운터로 공존시켜 최악 지연(최대 4×30s)을 수용하는 가용성 우선 선택.
   - 선택지: 현행(이중 카운터, 총 지연 미상한) vs E2E 총 타임아웃 예산 추가 vs V1 재시도 횟수 축소
   - 판정: KEEP — 분리 근거가 정본에 기재(L940 'R-69-3 max_transitions=2 (V2/V3) / V1 v1_timeout_retries=3 별도 카운터')되고 V1은 개인용 저비용 phase로 로컬/저가 모델 가용성 우선이 합리적; 총 지연 상한을 규정한 정본 없음 → 현행 유지, Phase 5에서 E2E 타임아웃 예산 추가는 선택지.
12. **[KEEP]** `docs\sot 2\6-9_Brain-Adapter-HAL\BRAIN_ADAPTER_HAL_구조화_종합계획서.md`:1334 (benchmark §8 L391-426, §8.1 분해) — 성능 목표값 선택 — p95<1.5초(V3 vLLM)/p95<2초(V2)/100 QPS/폴백<1%를 SLA 목표로 단정(측정 전제 일부 미명시).
   - 선택지: 현행 목표 유지(+Phase 5 실계측 검증) vs 토큰 길이/동시성 조건별 목표 세분화 vs 목표 완화
   - 판정: KEEP — SLA 목표값은 설계자 선택 영역이고 정본 모순 없음; benchmark §8.1이 latency 분해(vLLM 추론 ~1,300ms)와 hal_v3 §3.1이 하드웨어 전제(A10G GPU, Llama-3.1-8B, max-model-len 8192)를 보완 기재하며 §8.3 SLA 알림과 Phase 5 entry-gate 실계측이 현실성 검증을 담당 → 현행 목표 유지.

> notes: 원판정 앵커 12건과 동수 재도출(강제 짜맞춤 아님 — 후보 16건 중 4건을 근거 기반 제외). 분류 내역: (1) mf_in 객관결함 중복 제외 20건 = T8-001/002/005/018/019/055/057/061/062/067/107 + BAH-002/003/005/006/007/008/011/016/017 (참고: T8-057 Big-O와 T8-018 await 구문은 디스크에서 이미 교정 확인 — P1-4 L217 '1+3+2=6', P1-1 L159 asyncio.gather). (2) 오탐 제외(디스크 실측 반박) 8건: T6-008·T8-043(P1-3 §18 L595-596이 V1 축약 체인 'no DeepSeek' 주석을 명시 정본화 — LOCK-69-8 모순 아님), T8-056(±0.05는 warn 등급 시나리오 검증항목 L127-140, DRIFT-1은 critical 등급 별도), T8-066(Phase 2b break 후 Phase 4 소진 처리가 후속 — silent exit 아님, 전반부는 자기반박), T8-101(계획서 L632 '단 LOCK-69-7 범위 내에서만 에스컬레이션' + L639 전환 1회 카운트 명시로 충돌 

### 3-8_Conversation-A2A (12건)

1. **[KEEP]** `docs\sot 2\3-8_Conversation-A2A\01_a2a-protocol\agent_card_spec.md`:527 (§7 예외표), 552-554 (§8 로깅 예시) — 인증 실패(JWT 만료 포함)를 전용 인증 에러 코드가 아닌 -32600 Invalid Request 단일 코드 + 메시지 코드(TOKEN_EXPIRED 등)로 매핑하는 선택
   - 선택지: (a) -32600 단일 코드+메시지 구분(현행) (b) 인증 전용 커스텀 코드(-3201x) 신설 (c) HTTP 401/403만 사용
   - 판정: KEEP (a) — 도메인 인증 에러 정본 mtls_jwt.md §7.1(L584-595)이 인증 실패 9건 전수를 -32600으로 단일화(§9 정합표 L805 MATCH)했고 agent_card_spec은 이를 그대로 따름(본문 정본 정합, 위반 없음)
2. **[KEEP]** `docs\sot 2\3-8_Conversation-A2A\01_a2a-protocol\error_codes.md`:335 (60000 리터럴), 502-503 (recovery_timeout_ms: 60000) — CB 복구 타임아웃 60초를 의사코드에 60000 리터럴로 표기할지 인터페이스 필드 참조로 표기할지의 표현 선택
   - 선택지: (a) LOCK 값 60000 리터럴+주석(현행) (b) circuitBreaker.recovery_timeout_ms 필드 참조로 치환
   - 판정: KEEP (a) — DESIGN LOCK LOCK-A2A-09가 '60초 후 HALF-OPEN'을 고정(종합계획서 L162, error_codes §8 L474)하며 인터페이스 L503도 60000 고정 리터럴 타입이라 단일 진실원천 위반이 실질 성립하지 않음
3. **[KEEP]** `docs\sot 2\3-8_Conversation-A2A\03_security\audit_logging.md`:697 (§9.1 P1-5 예외 #7) — CRL/OCSP 조회 실패(soft-fail)를 신규 이벤트 타입 대신 A-8 cert_revoked_attempt에 '(간접)' WARN으로 합류시키는 이벤트 택소노미 선택
   - 선택지: (a) A-8 간접 매핑 + WARN soft-fail(현행) (b) 전용 이벤트(예: a2a.auth.revocation_check_failed) 신설
   - 판정: KEEP (a) — 표가 '(간접)'·'WARN (soft-fail)'로 의도를 명시해 P1-5 soft-fail 정책과 정합하며, 이벤트 타입 신설 여부를 강제하는 정본 없음(설계 재량)
4. **[KEEP]** `docs\sot 2\3-8_Conversation-A2A\03_security\audit_logging.md`:660 (§8.2 아카이브 시스템 행), 662-678 (§8.3 무결성 체인) — 아카이브 시스템의 '보존 기간 경과 후' DELETE 허용 정책에서 삭제 전 해시 검증 의무를 별도 규정하지 않는 선택
   - 선택지: (a) 보존기간 게이트 + §8.3 해시체인/Ed25519 서명으로 변조 탐지(현행) (b) 삭제 전 무결성 검증 단계 의무화
   - 판정: KEEP (a) — §8.3 해시체인이 변조 탐지를 제공하고 삭제는 보존기간 경과 후로 제한되어 정본 위반 없음; 사전 검증 의무화는 추가 하드닝 선택지
5. **[KEEP]** `docs\sot 2\3-8_Conversation-A2A\04_advanced-features\conversation_state_machine.md`:258 (awaiting_agent 5초), 259 (agent_thinking 30초) — awaiting_agent(분기 결정) 5초와 agent_thinking 30초를 별개 상태의 독립 timeout 값으로 두는 선택
   - 선택지: (a) 상태별 독립 timeout 5s/30s(현행) (b) 통합 30s (c) 5s 상향 조정
   - 판정: KEEP (a) — §6 표가 두 상태를 별개 행으로 명시 분리하며 정본 제약은 R-11-7(스트리밍 300초)뿐이고 L261(agent_streaming 300초)에서 준수됨; 5초 분기 결정 윈도우는 설계자 선택 값
6. **[KEEP]** `docs\sot 2\3-8_Conversation-A2A\03_security\mtls_jwt.md`:470 (§5.1 Step 6 jti 중복 확인; jti 언급 L320/590/899 전수 — TTL 정책 부재 확인) — jti 재사용 방지 저장소의 TTL/보존 기간을 스펙에 고정하지 않고 구현 재량으로 남기는 추상화 수준 선택
   - 선택지: (a) 구현 재량(현행) (b) TTL=토큰 exp 윈도우 이상으로 스펙 명시 (c) 고정값(예: 24h) 규정
   - 판정: KEEP (a) — jti 검사 자체는 정본 정의됨(L470, §7.1 L590 TOKEN_REPLAY_DETECTED, §10 시나리오 L899); TTL≥토큰 만료 윈도우면 충분한 구현 세부로 정본 위반 없음(운영 가이드 보강은 선택)
7. **[KEEP]** `docs\sot 2\3-8_Conversation-A2A\05_monitoring\metrics_dashboard.md`:250 (§4.2 cb_trip_reason 4종 열거), 255 (§4.3 push_failed) — cb_trip_reason 라벨 집합을 §4.2 4종 닫힌 열거로 볼지 peer 연동(§4.3)에서 push_failed 확장을 허용하는 열린 라벨 정책으로 볼지의 선택
   - 선택지: (a) 확장 가능 라벨 — §4.3 peer 연동이 push_failed 추가(현행) (b) §4.2 열거에 push_failed 포함해 닫힌 집합으로 동기화
   - 판정: KEEP (a) — 라벨 집합을 고정하는 정본 제약 없음; §4.3이 push_notifications §6.2와의 연동을 명시 정의하므로 연동 확장으로 일관 해석 가능(카디널리티 영향 +1), 닫힌 열거 동기화는 개선 선택지
8. **[KEEP]** `docs\sot 2\3-8_Conversation-A2A\01_a2a-protocol\error_codes.md`:76-85 (§4 카탈로그 8건 동결, 확장 코드 grep 0건); streaming_sse.md 169(-32029)/push_notifications.md 279(-32031)/artifact_chunking.md 157-159(-32034~36)/moa_pattern.md 436(-32030) — 중앙 에러 카탈로그를 -32001~-32008 8건으로 동결하고 기능별 확장 코드는 '(비표준)' 명시 후 파일-로컬(-32029~-32036 비충돌 범위)로 운용하는 등록 정책 선택
   - 선택지: (a) 파일-로컬 비표준 확장 + 비충돌 범위(현행) (b) error_codes.md에 확장 레인지 섹션 정식 등재
   - 판정: KEEP (a) — artifact_chunking §11 L249가 '비표준 확장 -32034/-32035/-32036 (청크 전용, 카탈로그 -32001~-32008와 비충돌)'로 정책을 명문화했고 객관 교정(mf_in i4)도 -32029+ 확장 레인지 사용을 전제; 중앙 등재는 개선 선택지일 뿐 정본 위반 아님
9. **[KEEP]** `docs\sot 2\3-8_Conversation-A2A\04_advanced-features\push_notifications.md`:161-163 (§3.3 HMAC 서명 원본에 X-A2A-Timestamp 포함), 167 (§3.4 delivery-id 1시간 idempotent) — webhook 재전송 방어를 delivery-id 1시간 idempotency로 두고 timestamp freshness window 값을 스펙에 고정하지 않는 선택
   - 선택지: (a) delivery-id 1h idempotent + 서명에 timestamp 포함(현행) (b) freshness window(예: ±5분) 및 거부 응답 명시 추가
   - 판정: KEEP (a) — 서명 원본에 timestamp가 포함되고 1시간 delivery-id idempotency가 중복 전달을 차단하므로 window 값은 추가 하드닝 선택; 이를 강제하는 상위 정본(RULE/PLAN/LOCK) 없음
10. **[KEEP]** `docs\sot 2\3-8_Conversation-A2A\INDEX.md`:6 ('V2 파일 수 = 8 strict'), 24-37 (§2 표 9행 + 합계 '8 files, P2-3 dual-file 포함 = 9 lines' + L37 주석) — V2 산출물 집계를 세션 산출물 단위(8 strict)로 할지 물리 파일 단위(9)로 할지의 카운트 컨벤션 선택
   - 선택지: (a) '8 strict' 산출물 단위 + dual-file 주석으로 9행 병기(현행) (b) 물리 파일 9로 통일 표기
   - 판정: KEEP (a) — §2 합계행과 L37 주석이 dual-file 세션 구조(세션 7, dual P2-3/P2-6)를 자체 설명하며 도메인 관례상 슬롯/물리 이원 집계는 수용된 컨벤션(1-1 'INDEX 53 슬롯 vs 물리 45' 선례); 상위 정본 모순 없음
11. **[KEEP]** `docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_상세명세.md`:403-414 (§5.1 상태표: Artifact Chunking/Agent Composition=설계, Priority Queuing/Conversation Branching=계획) vs INDEX.md L5/L190-202 (Phase 4 APPROVED 6/6) — V1 상세명세 본문(§5.1 상태표)을 historical snapshot으로 byte 보존하고 현행 상태 정본을 INDEX에 두는 문서 보존 컨벤션 선택
   - 선택지: (a) V1 본문 동결 + INDEX §10이 현행 정본(현행) (b) 상세명세 §5.1을 Phase 4 기준으로 소급 갱신
   - 판정: KEEP (a) — 도메인 컨벤션이 V1 정본 본문 byte 보존(Phase 4 RECOVERY도 V1 무변경 원칙 유지)이며 INDEX §10(L194-202)이 6 V3 APPROVED 6/6으로 현행 상태를 정본 제공; 정본 우선순위상 현행은 INDEX가 지배하므로 모순 아님
12. **[KEEP]** `docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_구조화_종합계획서.md`:93-98 (§2.1 트리: 04_advanced-features 4파일만 표기; 실파일 8 .md + _index 실존 Glob 확인) — 종합계획서 §2.1 폴더 트리를 Phase 0 설계 시점 스냅샷으로 동결(append-only)하고 현행 파일 census를 §6.1 배정표와 INDEX에 위임하는 선택
   - 선택지: (a) 본문 동결 + §6.1 16항목/INDEX가 현행 정본(현행) (b) §2.1 트리를 매 Phase 소급 갱신
   - 판정: KEEP (a) — 계획서는 append-only(§7.R supersede 마커) 운영이 도메인 관례이고 §6.1이 04_advanced-features 16항목 배정을 정본 제공하며 push_notifications/conversation_branching/priority_queuing/agent_composition 실파일 존재 확인; 트리 소급 수정은 본문 byte 보존 원칙과 충돌

> notes: [방법] clc 41건 + tight 26건 + GPT 15건을 mf_in 객관확정 30건과 대조 후 잔여 23건 전수 디스크 실측. [제외 내역] (1) mf_in 동일/중복: T8-002/003/004/011/021/027/041/050/053/063/064/069/087/089/094/095/097/098/100/117/218, T6-042/094/160, A2A-001~007/009/010/011 + T8-099(-32003 충돌 동족, mf_in i5/i17과 동일 결함군). (2) verify=refuted 오탐(디스크 반박 또는 주장 오인): T8-030(C-7 분류 오독+failover 깊이는 §7.3 제약표로 규정), T8-130(ESCALATE 경로에 '단일 proposer fallback' 명시되어 결함 주장 불성립), T8-180(LOCK-A2A-10이 구현/아키텍처 레이어 분할 소유를 자체 정의, R1 '각 항목 canonical_owner 지정'과 정합), T8-183/T8-240(raise_no_agent_error()는 유효한 함수 호출 표현식), T8-200/T8-221/T8-222(계획서 주장 반박), T8-241(상세명세 V

### 3-9_Business-Model-Strategy (10건)

1. **[KEEP]** `docs\sot 2\3-9_Business-Model-Strategy\04_financial-modeling\financial_projection.md`:373 (원판정 시점 372; L411에도 동일 260개월 재인용) — 순burn $770/mo 수준에서 Runway를 'Seed $200K / $770 ≈ 260개월 (초기 안전)'으로 그대로 제시할지, 표시 상한(예: 24+개월)으로 캡할지의 지표 표현 방식 선택
   - 선택지: (a) 산술 그대로 260개월 표기 + '초기 안전' 해석 주석 (현행) / (b) '24+개월(사실상 무제한)' 캡 표기 / (c) Net Burn 절대액만 표기하고 Runway 생략
   - 판정: KEEP 현행 (a) — 산술 자체는 정확하고 LOCK/STEP7-H 어디에도 Runway 표시 규약 정본이 없으며, L411 시나리오4가 세션5 교정으로 '비관 정상 운영 +$4,230/mo 흑자, 적자는 V2 초기 램프 한정' 맥락 주석을 이미 보강해 오독 위험이 해소됨
2. **[KEEP]** `docs\sot 2\3-9_Business-Model-Strategy\INDEX.md`:8 (cross_domain_deps `[]` 자기완결) vs 120-128 (§8 #14/#16/#17 RECHECK_FLAG) + AUTHORITY_CHAIN.md 103-110 (§7 교차 참조) — cross_domain_deps 메타필드를 'blocking dependency 한정([], Part2 ABSENT 자기완결)'으로 정의하고 비차단 교차참조(RECHECK_FLAG)는 §8 표로 분리 관리하는 의존성 표현 체계 선택
   - 선택지: (a) cross_domain_deps=[] 유지 + §8 RECHECK_FLAG 별도 표 (현행) / (b) cross_domain_deps에 #14/#16/#17 등재 / (c) 필드 정의 주석 추가
   - 판정: KEEP 현행 (a) — INDEX §8과 AUTHORITY §7/§8이 교차 LOCK 영향과 RECHECK_FLAG를 이미 완결 기술하므로 자동 그래프 누락 위험은 도메인 내부에서 상쇄되며, 메타필드 의미론은 RULE/PLAN 정본에 단일 정의가 없어 설계자 재량 범위
3. **[KEEP]** `docs\sot 2\3-9_Business-Model-Strategy\AUTHORITY_CHAIN.md`:5 (Status: APPROVED Phase 2 완료) vs 6/8 (버전 v1.2·최종 갱신 2026-06-01 Phase 4) + INDEX.md 3 (Phase 4 ✅ COMPLETE) — AUTHORITY_CHAIN의 Status 필드를 '승인 상태(APPROVED, Phase 2 마감 앵커)'로 고정하고 Phase 진행은 버전/최종 갱신 라인 + §9 변경 이력 + INDEX 헤더로 추적하는 상태 표기 체계 선택
   - 선택지: (a) Status=APPROVED(Phase 2 앵커) 유지, phase는 버전 라인으로 추적 (현행) / (b) Status를 Phase 4 COMPLETE로 갱신 / (c) approval_status·phase_status 필드 분리
   - 판정: KEEP 현행 (a) — Phase 4 RECOVERY가 동일 헤더의 버전·최종 갱신 라인은 2026-06-01로 갱신하면서 Status는 의도적으로 보존했고(v1.2 변경 이력 기재), Phase 현황 정본은 INDEX L3이 담당하므로 모순이 아닌 역할 분담; 단일 정본 우선 원칙상 phase 상태 조회는 INDEX 기준
4. **[KEEP]** `docs\sot 2\3-9_Business-Model-Strategy\CONFLICT_LOG.md`:5-7 (v1.0·최종 갱신 2026-04-22) + 224 (v1.0 유지 선언) vs INDEX.md 35 (Phase 2~4 신규 0건) — CONFLICT_LOG 버전 인상을 '신규 CFL 등재 시에만' 수행하고, 신규 충돌 0건인 Phase 4 검증 결과는 INDEX §2/§7과 AUTHORITY v1.2에 기록하는 로그 버저닝 정책 선택
   - 선택지: (a) v1.0 유지 + 신규 0건은 타 거버넌스 문서에 기록 (현행) / (b) Phase 4 검증 행(신규 0·OPEN 0·날짜·범위)을 CONFLICT_LOG에 추가하고 v1.1 인상
   - 판정: KEEP 현행 (a) — L224에 'v1.0 유지(신규 CFL 등재 없음)' 정책이 명시 선언돼 있고 13건 전수 RESOLVED·신규 0건 사실은 INDEX L35/AUTHORITY 변경 이력으로 추적 가능하므로 정본 위반 없음; 추적성 강화용 Phase 4 행 추가는 선택적 개선 사항
5. **[KEEP]** `docs\sot 2\3-9_Business-Model-Strategy\CONFLICT_LOG.md`:14 (우선순위 체인 LOCK > STEP7-H > sot2 계획서 > 상세명세) vs 152-163 (CFL-010 계획서 §B 7티어 최종 정본 채택) — 충돌 해결에서 '승인된 상위 통합 파생안(계획서 §B 7티어)이 원문 4티어들을 superset으로 대체'하는 예외를 허용하는 충돌 판정 메타규칙 선택
   - 선택지: (a) CFL-010 판정 유지(통합안이 양 정본의 superset이므로 최종 정본) (현행) / (b) STEP7-H 4티어(Free/Core/Pro/Team)로 환원 / (c) superset-예외 규칙을 우선순위 체인에 명문화 또는 CFL-010을 LOCK/Decision 승격
   - 판정: KEEP 현행 (a) — 7티어는 STEP7-H 티어 전부와 LOCK-BM-06/07/08 가격값을 보존한 채 확장한 superset이라 LOCK·STEP7-H 실질 위반이 없고, AUTHORITY §6에 이미 최종 정본으로 등재(C-7 해결)·상세명세 4티어 결함은 별도 객관건(T8-133)으로 기처리됨; 재현성 향상용 예외 규칙 명문화는 선택적
6. **[KEEP]** `docs\sot 2\3-9_Business-Model-Strategy\03_gtm-growth\growth_strategy.md`:677-683 (기준 ACV $150K, L683 'ACV = 평균 80석 × $35/seat/mo × 12 + 부가 (추정)') + gtm_phases.md 641 (40계약 × ACV $150K) — Enterprise 평균 ACV $150K(좌석 $33.6K + 부가 ~$116K) 가정을 부가 항목 분해 없이 `(추정)` 표기 + 3시나리오 범위($90K~$200K)로 제시하는 재무 가정 수준 선택
   - 선택지: (a) ACV $150K (추정) + R-12-3 3시나리오 범위 병기 (현행) / (b) implementation fee/support/white-label/usage/SLA 항목별 단가 분해 / (c) ACV를 좌석 매출 기반 ~$40K로 하향 재계산
   - 판정: KEEP 현행 (a) — STEP7-H/LOCK 어디에도 ACV 정본값이 없고, LOCK-BM-08 정가($35/seat 최소 10석)는 L671에 verbatim 인용·재정의 0이며, R-12-4(출처·시점·추정 표기)와 R-12-3(3시나리오, 비관 $90K)을 준수한 사업 가정이므로 결함이 아닌 설계 선택; 부가 매출 분해는 V3 실집행 시점 보강 사항
7. **[KEEP]** `docs\sot 2\3-9_Business-Model-Strategy\05_kpi-dashboard\kpi_definitions.md`:821-828 (§V3.7 V1/V2/V3 전수 '✅ 8 요소' 매트릭스) vs 24-59 (V1 MAU: 정의/측정 기준/목표 값/대시보드 스키마 4섹션 형식) — V1/V2 KPI를 V3식 8요소 단일 표로 재작성하지 않고, 기존 4섹션 형식에 8요소(이름·정의·수식·단위·소스·주기·목표·임계)가 분산 충족된 것으로 매핑 인정하는 문서 형식 선택
   - 선택지: (a) V1/V2 기존 형식 보존 + §V3.7 논리적 8요소 충족 매핑 (현행) / (b) V1/V2를 V3와 동일한 8필드 표로 재작성 / (c) '8 요소' 주장을 V3 한정으로 축소
   - 판정: KEEP 현행 (a) — §V3 헤더(L732)가 'V1+V2 영역 byte 무변경 prefix EXACT' append-only 규약을 명시하므로 V1 재작성(b)은 오히려 도메인 보존 규약 위반이며, V1 MAU에도 소스(L38)·주기(L36)·목표(L44-47)·임계(L57)가 실재해 8요소가 형식만 다르게 충족됨; 형식 통일성은 검증 가능한 정본 위반이 아닌 표현 선택
8. **[KEEP]** `docs\sot 2\3-9_Business-Model-Strategy\02_market-analysis\personas.md`:7-8 (헤더 담당 항목 S7H-027~030/032 + C-5 'P1~P4 기준') + 16 (cross-ref P1~P4) vs 358-360 (§E.1.1 CFL-008 P1~P5 5종 정본 채택) — V1 헤더/cross-ref 블록을 V1 시점 그대로 동결(byte 보존)하고 P5 추가는 §E append 영역 + CONFLICT_LOG CFL-008로만 반영하는 append-only 문서 진화 방식 선택
   - 선택지: (a) V1 헤더 동결 + §E.1.1/CFL-008에서 P1~P5 정본 선언 (현행) / (b) 헤더 담당 항목·cross-ref를 P1~P5/S7H-027~031 기준으로 갱신
   - 판정: KEEP 현행 (a) — 도메인 전체가 'V1+V2 prefix byte EXACT' append-only 보존 규약(INDEX §9 v1.1, Phase 4 RECOVERY 검증 5/5)을 채택하고 있어 헤더 갱신(b)이 오히려 규약 모순이며, P5 정본 채택은 §E.1.1(L360)과 CONFLICT_LOG CFL-008(RESOLVED)에 추적 가능하게 명시돼 실질 오해 위험이 통제됨
9. **[KEEP]** `docs\sot 2\3-9_Business-Model-Strategy\AUTHORITY_CHAIN.md`:96 (Enterprise: SSO/SAML+감사+SLA 99.9%) + personas.md 398 (관리 기능: 권한+감사 로그+SSO) + risk_analysis.md 257-261 (STEP7-E 보안 체계 mitigation) + growth_strategy.md 668 (PoC: SSO/SAML+감사 로그+SLA 검증) — Enterprise 보안 요구(역할/권한 매트릭스, 감사 이벤트 taxonomy, tenant isolation, SAML/SCIM 경계, 보안 리뷰 Gate)의 상세 명세를 3-9 도메인 내부에 두지 않고 STEP7-E 보안 체계 등 타 도메인 소유로 위임하는 도메인 경계 설계 선택
   - 선택지: (a) 3-9는 가격·SLA 기준(LOCK-BM-05/08)만 소유, 보안 상세는 STEP7-E/보안 도메인 참조 (현행) / (b) 3-9 내 Enterprise 판매 Gate용 security contract(owner domain·통제·감사 이벤트 ID·tenant model·acceptance criteria) 신설
   - 판정: KEEP 현행 (a) — AUTHORITY §8 도메인 경계가 3-9 소유를 '가격 체계·비용 상한·SLA 기준'으로 한정하고 risk_analysis L257이 보안 아키텍처를 STEP7-E 정본으로 명시 위임하므로 도메인 내 부재는 결함이 아닌 경계 설계이며, GPT 원 finding도 is_confident:false로 확정 결함 단정을 유보함
10. **[KEEP]** `docs\sot 2\3-9_Business-Model-Strategy\03_gtm-growth\gtm_phases.md`:609/615 (Y3 ARR ≥ $20M Scale 목표) + 621 (출처: 계획서 §7.6 P3-2 entry-gate forward-defined L1353 + S7H-037 정합) vs revenue_model.md 797-803 (V3 누적 ARR ~$15M, S7H-037 정합) — Y3 ARR을 단일 값으로 통합하지 않고 $15M(S7H-037 상위 집계 base)과 $20M(계획서 P3-2 entry-gate/스케일 stretch 목표) 이중 목표로 운용하는 목표 체계 선택
   - 선택지: (a) $15M=S7H-037/SOM base + $20M=계획서 §7.6 P3-2 gate/stretch 이중 운용 (현행) / (b) base/stretch/gate 라벨을 양 파일에 명시 분리 / (c) 단일 ARR LOCK으로 통합
   - 판정: KEEP 현행 (a) — 정본 우선순위상 STEP7-H S7H-037($15M~)이 base 정본, PLAN(종합계획서 §7.6 P3-2 entry-gate 'ARR ≥ $20M', forward-defined L1353)이 gate 정본으로 각각 출처가 살아 있고, gtm_phases L621이 $20M을 S7H-037 보수~낙관($3.6M~$75M) 범위 내 V3 목표로 포지셔닝하는 관계 설명을 이미 보유해 정본 상호 모순이 아님; ARR LOCK 신설(c)은 LOCK-BM 체계(비용·가격 보호 목적)와 성격이 달라 불필요

> notes: 재도출 결과 10/10 — 원판정 앵커와 정확히 일치(짜맞춤 아님: 제외 적용 후 잔여가 자연히 10건). [도출 절차] 고유 풀 29건(clc 22 + tight 17은 clc 진부분집합 + GPT 14) 중 (1) mf_in 객관확정 19건 매핑 제외: T8-004(i9)/020(i10)/021(i8)/022(i11)/026(i7)/030(i12)/031(i4)/065(i13)/068(i14)/072(i15)/132(i5)/133(i3), T6-043(i0)/067(i1)/078(i2), BM-AUD-005(i6)/006(i4 중복)/007(i16)/008(i17)/012(i18·BM-AUD-013과 별건); (2) verify:"refuted" 디스크 반박 오탐 7건 제외: T8-023/042/052/053/103/110/116. 잔여 10건(T8-066 + BM-AUD-001/002/003/004/009/010/011/013/014) 전건 디스크 실측 file:line 확인 완료. [기해소 관찰] 세션5(2026-06-11) 교정 흔적 확인: financial_projection.md L411 시나리오4가 T8-065(객관, mf_in i13) 교정본

### 5-1_Benchmark-Evaluation (9건)

1. **[KEEP]** `docs\sot 2\5-1_Benchmark-Evaluation\01_standard-benchmarks\coding_benchmarks.md`:94 — pass@k 추정식이 수학적으로 정의되지 않는 k>n 경계에서 'IF k > n: RETURN 1.0 if c > 0 else 0.0' 낙관적 관례를 채택
   - 선택지: (a) 현행 낙관 관례 c>0→1.0 (b) n≥k assert로 에러 처리(OpenAI 원 구현 방식) (c) 복원추출 근사 1-(1-c/n)^k
   - 판정: KEEP — 정본(LOCK-BE-01~15, R-18-x)은 pass@k 경계 관례를 규정하지 않으며, 실행 파라미터 k_values [1,5,10]·seed=42 결정론(LOCK-BE-08) 하에서 k>n은 방어적 dead-branch. 본문 L95 정상 경로 식 1-product((n-c-i)/(n-i))는 표준식과 일치.
2. **[KEEP]** `docs\sot 2\5-1_Benchmark-Evaluation\03_domain-benchmarks\vbs_core.md`:32, 505-513 — S7G-061/062/063 목표값을 _index.md의 엄격한 값(S7G-063 ≥90%) 대신 종합계획서/V1 값(≥80%)으로 채택해 PASS/FAIL 표를 구성
   - 선택지: (a) V1/종합계획서 ≥80% 유지 (b) _index.md ≥90% 상향 (c) 단계적 상향(80→90)
   - 판정: KEEP — CONFLICT_LOG C-19/C-20(L53-54)이 OPEN→RESOLVED '일치 확인, V1 정본 값 유지'로 종결 → V1 vbs_core.md의 80% 채택이 정본 결정과 정합. L513이 _index.md 90% 기준을 투명하게 병기. 헤더 L32 CONFLICT_CANDIDATE 배너는 stale 표기이나 값 선택 자체는 무모순.
3. **[KEEP]** `docs\sot 2\5-1_Benchmark-Evaluation\03_domain-benchmarks\vbs_core.md`:486 — S7G-063 Memory Recall 사실판정 judge로 외부 단일 모델 'openai:gpt-4-turbo'를 채택하고, 장애 대응은 예외처리표(L633)의 '3회 실행 majority vote' 일관성 정책만 둠(API 장애 fallback 체인 없음)
   - 선택지: (a) 현행 단일 외부 judge + majority vote (b) 로컬/대체 judge fallback 체인 추가 (c) 듀얼 judge 합의 방식
   - 판정: KEEP — 어떤 LOCK도 judge 모델·fallback을 규정하지 않는 설계 재량 영역. temperature 0 + seed 42로 재현성(R-18-1) 충족, 예외처리표가 일관성 저하 시나리오를 커버. LogicKor judge 명세 보강은 mf_in i=22 객관건(상세명세 A-4)으로 별도 트랙.
4. **[KEEP]** `docs\sot 2\5-1_Benchmark-Evaluation\05_test-items\benchmark_scheduler.md`:40 (+promptfoo_integration.md:309) — 전수 실행 시간 예산을 이원화: 월간 full_suite_vbs timeout_min 360 vs 야간 promptfoo full(GitHub Actions) timeout-minutes 180
   - 선택지: (a) 현행 이원 예산(월간 360/야간 180) (b) 단일 예산으로 통일 (c) 스코프별 산식(분/항목) 정의
   - 판정: KEEP — benchmark_scheduler §V3.1 L144가 'schedule 값 = LOCK 아님'(LOCK-BE-12는 주기 정책만 LOCK)을 명시. 두 실행은 스코프·주기가 다름(월간=VBS 포함 전체 suite, 야간=promptfoo_full+judge)이므로 360>180 배분은 무모순인 예산 설계 선택.
5. **[KEEP]** `docs\sot 2\5-1_Benchmark-Evaluation\05_test-items\scheduler_cicd_integration.md`:39, 45 — 4-2 CI 게이트의 merge 차단 최소 통과율을 pass_ratio < 0.95 → FAIL로 설정 — LOCK 미등재 신규 임계값
   - 선택지: (a) 0.95 유지 (b) AUTHORITY_CHAIN LOCK-BE 신규 등재 후 0.95 고정 (c) CRITICAL suite 1.0 / 전체 0.95 이원화
   - 판정: KEEP — AUTHORITY_CHAIN 실측상 pass_ratio LOCK 부재 확인(LOCK-BE-09 ≥95%는 Prompt Injection 방어율로 무관). LOCK-BE-14는 회귀 하락 알림(3%/CRITICAL 1%)만 규정하고 L45는 이를 verbatim 정합 인용 — pass_ratio 최솟값은 미규정 영역의 설계 재량이며 R-18-3(LOCK 등재 임계값 변경 절차)에도 저촉 없음. 운영 안정 후 AUTHORITY_CHAIN 등재 검토 권장.
6. **[KEEP]** `docs\sot 2\5-1_Benchmark-Evaluation\BENCHMARK_EVALUATION_구조화_종합계획서.md`:400 — R-18-2 인간평가 동점 해소: 2점 이상 차이 시 3차 평가자 투입 후 최종 점수를 '합의 결과 또는 중앙값'으로 산출 — 둘 사이 우선순위를 평가 주관자 재량에 위임
   - 선택지: (a) 현행 '합의 또는 중앙값' 재량 (b) 중앙값 고정 (c) '합의 불성립 시 중앙값' 우선순위 명문화
   - 판정: KEEP — R-18-2는 도메인 고유 거버넌스 규칙으로 그 자체가 정본이며 핵심 요건(최소 2인+3차 투입)은 명확. 1/3/5 극단 분기에서도 중앙값이 자연 default로 동작해 판정 불능이 발생하지 않음. 차기 개정 시 '합의 불성립 시 중앙값' 1구절 명시 권장(현행 무모순).
7. **[KEEP]** `docs\sot 2\5-1_Benchmark-Evaluation\BENCHMARK_EVALUATION_구조화_종합계획서.md`:1362 (+2252) — LogicKor(S7G-013) 목표를 GPT-4 Judge 스케일 '≥ 8.0/10' 정본 + STEP7-G 백분율 '85+' 병행 표기로 운영 — Phase 1-A 표는 85+, L1415 계열/korean_benchmarks는 8.0/10
   - 선택지: (a) 현행 이중 스케일 병행 표기 (b) 8.0/10 단일화 (c) 백분율 85+ 단일화
   - 판정: KEEP — DESIGN LOCK 정본인 AUTHORITY_CHAIN L33 LOCK-BE-03이 '≥ 8.0/10 (GPT-4 Judge 기준)... S7G-013의 85+는 백분율 기준으로 병행 (CONFLICT_LOG C-02 참조)'을 명시 → 두 스케일 공존은 LOCK이 승인한 표기 정책 선택. G4-3 L2252의 'LogicKor ≥ 85+' 보존 인용도 이 병행 조항과 정합(정본 위반 0).
8. **[KEEP]** `docs\sot 2\5-1_Benchmark-Evaluation\BENCHMARK_EVALUATION_구조화_종합계획서.md`:3230-3233 — CAT-06 MCP 테스트 매핑: MCP 연결/도구호출(T-116/117)을 S7G-027(BFCL v3)로 프록시 매핑하고, T-119 'MCP 인증/권한'(CRITICAL)은 S7G 매핑 '-'로 두고 Security 카테고리(자동화 ✅)로 커버
   - 선택지: (a) 현행 프록시 매핑 + 카테고리 커버 (b) MCP 프로토콜 적합성 전용 S7G 신설 (c) T-119를 6-2 Security/4-3 MCP 도메인에 측정 위임 명시
   - 판정: KEEP — S7G '-' 매핑은 카탈로그 전반의 정상 패턴(T-030/031/034/035 등 동일 실측)이고 BFCL v3는 tool-calling 능력의 합리적 프록시. R-T5-1 횡단 원칙(L392)상 MCP 프로토콜 적합성 정본은 4-3 도메인 소유이므로 5-1 측 매핑 선택은 측정 위임 재량 — 정본 위반 없음.
9. **[KEEP]** `docs\sot 2\5-1_Benchmark-Evaluation\BENCHMARK_EVALUATION_상세명세.md`:112-114 — 배포 전 골든셋 스모크 테스트(V1 170문항: MMLU 50+HumanEval 20+MBPP 50+LogicKor 50)의 시간 예산을 '5분 이내'로 설정 — HumanEval 문항당 timeout 10s 최악치 직렬 가정(200s)과 긴장 관계
   - 선택지: (a) 5분 유지(병렬 실행 전제) (b) 10분으로 완화 (c) 스모크 문항수 축소
   - 판정: KEEP — 5분은 '목적' 수준의 목표 예산이고 timeout 10s(A-2)는 문항당 최악치 상한이지 전형 latency가 아님. 병렬 worker≥4면 최악치로도 충족 가능하며 어떤 정본(LOCK/RULE)도 스모크 예산을 규정하지 않음. B-2에 병렬도 전제 1줄 명시 권장(현행 무모순).

> notes: [재도출 방법] mf_in 객관확정 23건(i=0~22)을 CL-C 28건/tight 24건(CL-C 부분집합)/GPT 13건과 매칭 제외 → 잔여 후보 12건 전수 디스크 실측 후 분류. [카운트 차이 9 vs 앵커 7] 원판정과 +2 차이. 추정 원인: 원판정이 T6-072(clc verify=refuted — 'CONFLICT_LOG 해소 없이'라는 주장부가 C-19/C-20 RESOLVED 실존으로 반박됨)와 T6-141(LOCK-BE-03 '85+ 백분율 병행' 조항으로 모순 주장 반박)을 오탐으로 분류했을 가능성이 큼. 본 재도출은 두 건 모두 지적 내용(80% 채택, 이중 스케일)이 디스크에 실존하고 그 선택 자체가 정본이 승인한 설계 재량이므로 '파일에 그런 내용 없음' 오탐 기준에 해당하지 않아 주관으로 등재. 이 2건을 빼면 정확히 7건(T8-010/T8-073/T8-096/T8-118/T8-132/T8-181/T8-196)으로 앵커와 일치. [제외 3건] T5-115: notifier/통보 채널 혼용 — 단순 표기, 기준상 제외. BE-AUD-007: safety_benchmarks L18 '충돌 없음' vs L25/L28 CONFLICT

### 5-3_v12-Additions-Detail (9건)

1. **[KEEP]** `docs\sot 2\5-3_v12-Additions-Detail\04_investing-additions\black_litterman_model.md`:12 (+ AUTHORITY_CHAIN.md:44, 상세명세 L329 '통상 0.025~0.05', Ai-investing portfolio_optimization.md L99/L388/L610 실측) — Black-Litterman 스케일링 팩터 tau 기본값을 0.025로 잠글지 0.05 또는 동적 1/T로 둘지의 파라미터 선택
   - 선택지: 0.025(Idzorek/top_down_allocation 기본, 현행 LOCK-V12-03) vs 0.05(He-Litterman 1999, 구 portfolio_optimization E9) vs 동적 1/T(0.01~0.05 범위)
   - 판정: LOCK-V12-03 tau=0.025 단일 정본 유지 — RULE 1.3/PLAN 3.0에 tau 부재, DESIGN LOCK 계층 유일 등재값(0.025)이 본문(구 0.05 기재)에 우선(D5 2026-06-11 기판정과 동일 결론)
2. **[KEEP]** `docs\sot 2\5-3_v12-Additions-Detail\V12_ADDITIONS_DETAIL_구조화_종합계획서.md`:1179 (§A.1 #14 C-2 행 LOCK 상속 칼럼 — 'AI-Invest Factor 6종 LOCK'만 기재, Constraints LOCK 미병기 실측) — §A.1 마스터 테이블 LOCK 상속 칼럼에 항목당 대표 LOCK 1개만 적을지 상속 LOCK 전부(LOCK-V12-08 포함)를 병기할지의 요약 표기 깊이 선택
   - 선택지: 대표 LOCK 요약 표기(현행 §A.1) vs 전체 나열(factor_investing.md L12·04_investing-additions/_index.md L12와 동일 수준)
   - 판정: LOCK 매핑 정본은 §A.4 매트릭스(L1254 V12-08←C-2)+AUTHORITY_CHAIN L49로 정합 유지 중이므로 §A.1 요약 표기는 무모순 — 현행 유지, 차기 §A.1 갱신 시 'AI-Invest Factor 6종 LOCK + Constraints LOCK' 병기 권장. (T8-013의 현금 5% vs 20% 부분은 객관 i7로서 C-06 RESOLVED(D3, 맥락 구분: 20%=CB-4 LOCK 안전장치/5%=cash_allocation 운영 목표) 기해소)
3. **[🔧CHANGE]** `docs\sot 2\5-3_v12-Additions-Detail\V12_ADDITIONS_DETAIL_구조화_종합계획서.md`:153-158 (§2.1 트리: 4개 분리 파일) vs 166 (§2.2: '_index.md 내부 섹션으로 처리') — 디스크 실측: 06_v2-v3-advanced에 _index.md 단일, 27건 전수 등재 — 06_v2-v3-advanced의 E/F/G 27건을 별도 4개 파일(v2_phase3_high/medium, v3_phase2_medium, v3_phase3_low)로 분리할지 _index.md 단일 파일 내부 섹션으로 처리할지의 파일 구조 선택
   - 선택지: 4파일 분리(§2.1 목표 트리) vs _index.md 단일(§2.2 깊이 규칙 + 현행 디스크 + V-01 DONE 6/6·51건 전수 등록)
   - 판정: 실제 구현·§2.2 규칙·검증 완료 상태(V-01 DONE)가 모두 _index 단일안으로 일치하므로 §2.1 트리의 4파일 기재가 자체 정본(거버넌스 규칙+검증된 산출물)과 모순 — 트리를 _index 단일로 정정
4. **[KEEP]** `docs\sot 2\5-3_v12-Additions-Detail\03_agent-teams\template_sets.md`:12 (+ AUTHORITY_CHAIN.md:48, 계획서 L231 §3.4·L1253 §A.4, CONFLICT_LOG.md:19 C-07 RESOLVED 실측) — TS 3종(TS_CORE/TS_WEB_RESEARCH/TS_CODE) 보호를 위해 전용 LOCK을 신설할지, B-2를 조건부로 유지할지, 기존 상위 정본 LOCK으로 상속 출처를 정정할지의 거버넌스 전략 선택
   - 선택지: 3-8/4-4 전용 LOCK 신설 vs B-2 CONDITIONAL 유지 vs D2.0-03 §4.2 '(LOCK) TemplateSet=3종'+2-1 LOCK-BN-18로 출처 정정(D4 채택)
   - 판정: DESIGN 2.0 LOCK(D2.0-03 §4.2)이 정본 우선순위상 S7-4 레벨 판정(W-05)에 우선하므로 D4(2026-06-11) 채택안 유지 — 전용 LOCK 신설은 D2.0-03 §4.2 규칙1(BLUE NODE 템플릿 정본 소유 금지)·R-T5-1(공동 소유 금지) 위반이라 금지. 기해소: C-07 RESOLVED, AUTHORITY_CHAIN L48·계획서 §3.4/§A.4 동시 정정 실측. B-2 정본 파일 placeholder(L11)는 Phase 2 귀속 확정 이월로 §7.3/S-3에 명시 추적 중
5. **[KEEP]** `docs\sot 2\5-3_v12-Additions-Detail\V12_ADDITIONS_DETAIL_구조화_종합계획서.md`:1054 (§10.2 V-07: 기준 '10/10 일치' vs 상태 '✅ DONE (2026-04-12) — ... C-04~C-08 OPEN 5건' dated 기록 잔존 실측) — 검증 행 상태 'DONE'의 의미론 선택 — 검증 절차 수행 완료 기록으로 볼지 기준(10/10 일치) 충족으로 볼지, 그리고 dated 검증 레코드의 append-only 보존 방식
   - 선택지: DONE=절차 수행 기록 유지+일자·예외 병기(현행) vs CONDITIONAL/FAIL로 소급 변경 vs 재검증 행 추가
   - 판정: dated 레코드(2026-04-12)의 append-only 보존이 VAMOS 정본 컨벤션이므로 소급 수정 금지 — 현행 유지하되 C-04~C-08 전건 RESOLVED(2026-06-11 D1~D5)로 기준 10/10이 현재 충족되므로 차기 갱신 시 V-07에 2026-06-11 재검증 노트 1행 추가 권장. 행 내 'OPEN 5건' 문구는 당시 사실의 이력 기록으로 CONFLICT_LOG 현행과의 차이는 모순 아님
6. **[KEEP]** `docs\sot 2\5-3_v12-Additions-Detail\V12_ADDITIONS_DETAIL_구조화_종합계획서.md`:1089 (§11 S-10: '✅ RESOLVED — C-1→VALID, C-2→VALID, B-2→CONDITIONAL 유지(Phase 2 귀속 확정 시 처리)' 실측) — 부분 해소 항목의 상태 라벨링 선택 — 범위 한정 RESOLVED + 이월 명시로 처리할지 PARTIAL/OPEN 상태를 신설·환원할지
   - 선택지: RESOLVED(범위=경로 특정)+B-2 CONDITIONAL 유지 명시(현행) vs PARTIAL 또는 OPEN 환원
   - 판정: S-10의 정의 범위는 '서브폴더 경로 특정'이며 C-1/C-2는 완료 — B-2 잔여는 S-3(OPEN, L1082)·§7.3(L968 '대기 CONDITIONAL')·P1 리포트 L148의 3중 추적으로 유실 없음이 실측되므로 현행 라벨링 유지(추적 손실이라는 우려 사실관계 불성립)
7. **[🔧CHANGE]** `docs\sot 2\5-3_v12-Additions-Detail\04_investing-additions\_index.md`:11-12 (괄호 placeholder 잔존 실측; §A.1 L1178-1179·항목 파일 L11은 확정 경로 기재) — 서브폴더 _index의 '정본 경로' 칼럼 상세도 선택 — P1-1 확정 경로를 동기화할지 괄호 추정 표기를 요약 수준으로 둘지
   - 선택지: 괄호 placeholder 유지(현행 _index) vs §A.1 확정 경로 동기화(15_portfolio-advanced/portfolio_optimization.md, 20_strategy-detail/quant/factor.md)
   - 판정: LOCK-V12-10 정본(부록 §A.1 L1178-1179)과 항목 파일(black_litterman_model.md L11, factor_investing.md L11)이 모두 P1-1 확정 경로를 기재 — 동일 허브 내 _index만 stale로 정본 모순 + R-19-2 양방향 정합성 위배이므로 확정 경로로 정정
8. **[🔧CHANGE]** `docs\sot 2\5-3_v12-Additions-Detail\V12_ADDITIONS_DETAIL_구조화_종합계획서.md`:64 (§1.3 '4건 (11 컴포넌트)') + 변형 L302 '(4건, 11 컴포넌트)' vs L392 §6.8 '10건' 실측 — 섹션 A 수량 표기 단위 선택 — 그룹 단위(4건)+컴포넌트 병기 컨벤션 vs 컴포넌트 단위 단독, 그리고 컴포넌트 집계값
   - 선택지: '4건(그룹)+컴포넌트 병기'(§1.3/§6.1) vs '컴포넌트 단위 10건'(§6.8)
   - 판정: 병기 컨벤션 자체는 유효한 표기 선택이나 컴포넌트 수 '11'은 어느 컨벤션으로도 도출 불가 — 상세명세 실측 A-1 3+A-2 2+A-3 2+A-4 3=10, §6.8 L392 '10건', §A.1 #1~#10, 같은 행 본문 '3종+2종+2종+3종'=10과 자기모순이므로 10으로 정정. L302 '(4건, 11 컴포넌트)'도 동반 정정 필요(별도 위치, 본 edit 범위 외)
9. **[KEEP]** `docs\sot 2\5-3_v12-Additions-Detail\V12_ADDITIONS_상세명세.md`:422 (§D-1 '병합 충돌 해결: LWW(Last Writer Wins) 또는 CRDT 기반' 잔존 실측) — Evolution Control Policy의 병합 충돌 해결 알고리즘 선택 — LWW vs CRDT
   - 선택지: LWW(단순, 마지막 쓰기 우선, 변경 손실 허용) vs CRDT(충돌 보존, 구현 복잡) vs 데이터 유형별 혼합
   - 판정: D-1의 정본은 #6 PKM(§A.1 #15 `3-3_PKM.../01_knowledge-capture/`)이므로 알고리즘 확정은 PKM 정본 소관(R-19-1) — Level 4 레거시 참조인 상세명세의 양안 나열은 정본 무모순. PKM 정본 확정 시 단일안: 노트 단위 기본 LWW(원자적 노트 원칙과 정합)+실시간 공동 편집 도입 시 해당 문서 유형만 CRDT 승격

> notes: [집계] 원판정 주관 10건 vs 재도출 9건(유니크). 차이 사유: tau 항목이 CLC(T6-005)와 GPT(V53-011) 양 소스에서 별개 finding으로 집계되면 10건과 일치 — 본 재도출은 동일 사안을 1건으로 병합. T8-035(SM2 초기 간격)는 CLC verify=refuted 오탐으로 제외(현행 L175-178은 표준 SM-2와 정합·기교정). [기해소 확인] 세션5 D1~D5 디스크 기적용 실측: tau 0.025 단일화(C-08 RESOLVED, portfolio_optimization.md L99/L388/L610), TS LOCK 출처 정정(C-07 RESOLVED, AUTHORITY_CHAIN L48), CBT 15종 전사(C-04), 링크 5종(C-05), 현금 비중 부재(C-06). 객관 기교정도 다수 실측: §3.4 절대규칙 L221, R6 L251, P2-1 게이트 L947(CONFIRMED≥19 분리), P1-1 요약 L905(누적 OPEN 분리), §7.3 L968(B-2 대기), SM2 리셋 L177, BreathingPattern hold2_seconds L40, factor_investing.md 'Low V

### 6-11_Hologram-Main-LLM (9건)

1. **[KEEP]** `docs\sot 2\6-11_Hologram-Main-LLM\04_main-llm-integration\two_tier_routing.md`:193 — CostHudSnapshot.threshold_pct 상한을 le=150.0(150%)으로 클램프할지, overlay_schema의 ratio_to_budget처럼 상한 없이(ge=0.0만) 둘지의 값 선택.
   - 선택지: (a) le=150.0 유지 — LLM 페이로드 폭주값 차단용 안전 클램프 / (b) 상한 제거하여 overlay_schema ratio_to_budget(0~1+ 초과 가능, UI clamp)와 대칭 / (c) 다른 상한값(예: 200%)
   - 판정: 현행 (a) 유지 — LOCK-HM-10은 수치 상한을 정의하지 않으며(정본 무규정), 두 필드는 서로 다른 스키마(HologramContextPayload 입력 vs GlassHUDData 출력)라 모순이 아님. >100=초과 게이지 로직(L193 description)과도 양립. 상한 근거 한 줄 주석 추가만 권고.
2. **[KEEP]** `docs\sot 2\6-11_Hologram-Main-LLM\05_glass-hud-overlay\overlay_schema.md`:430-431 (트리거 표) / 208-221 (EvidenceHudSnapshot) — Uncertainty Alert 트리거(CONFLICTING_SOURCES 분산>0.3, STALE_DATA >24h)를 per-source 데이터가 있는 상류(Front Mini/I-10, T2-2 EvidenceSummary)에서 평가할지, HUD 스냅샷에 sources[i].confidence/retrieved_at_ms를 실어 GlassHUDData 단독 평가 가능하게 할지의 아키텍처 선택.
   - 선택지: (a) 상류 평가 + 최소 스냅샷(현행: source_count+top_source_title만 유지, 트리거 결과는 uncertainty_alert.items로 전달) / (b) 스냅샷에 per-source 필드 추가하여 HUD 측 자체 평가
   - 판정: 현행 (a) 유지 — §3.5 트리거 표의 '입력 소스' 컬럼이 T2-2 sources/6-9 meta를 명시해 평가 위치가 상류임이 본문에 이미 내재. HUD 스냅샷 최소화는 LOCK-HM-10 '최소 필드 추출' 취지(L206)와 정합. §3.5에 '평가 위치=build 시점, GlassHUDData 단독 재평가 불가' 명시 한 줄만 권고.
3. **[KEEP]** `docs\sot 2\6-11_Hologram-Main-LLM\05_glass-hud-overlay\rendering_rules.md`:101 (§2.1), 110-111 (§2.2) — Fixed HUD 앵커링 구현을 position:fixed + Right Panel contain:layout(로컬 containing block화)으로 할지, position:sticky 등가 구현으로 할지의 CSS 아키텍처 선택.
   - 선택지: (a) fixed + contain:layout (현행 정본 해석) / (b) Right Panel position:relative + sticky (본문 §2.2가 '동등'이라고 스스로 인정하는 대안) / (c) 순수 viewport-fixed
   - 판정: 현행 (a) 유지 — D2.0-08 §9.1 Option A 'Fixed HUD' LOCK은 앵커링 메커니즘을 규정하지 않고, contain:layout이 fixed 자손의 containing block이 되는 것은 CSS Containment 표준 동작이라 정본 위반 없음. §2.2가 sticky 등가 구현을 이미 허용하므로 구현 시점 선택 여지로 두는 게 적절. 브라우저 지원 가드(@supports) 노트 추가만 권고.
4. **[KEEP]** `docs\sot 2\6-11_Hologram-Main-LLM\performance_benchmark_baseline.md`:26 (T-2), 32 (D-P4-5-2 reconcile) — Glass HUD 갱신 지연 SLA를 Phase3 <50ms에서 Phase4 <100ms로 완화한 임계값 선택.
   - 선택지: (a) <100ms 유지 (Phase4 정본, D-P4-5-2 reconcile 명시) / (b) <50ms 복원 (Phase3 baseline) / (c) 실측 데이터 첨부 후 재확정
   - 판정: 현행 (a) 유지 — LOCK-HM-10은 '실시간 표시'만 규정하고 수치 지연값을 갖지 않으므로(finding 스스로 확인) 정본 위반 없음. D-P4-5-2 reconcile 노트가 본문 정본으로 완화를 명문화했고 100ms는 인지 한계(RAIL) 내 합리값. '실측 기반' 주장의 측정 run ID 인용 추가만 권고 (값 변경 불요).
5. **[KEEP]** `docs\sot 2\6-11_Hologram-Main-LLM\06_streaming-canvas\stream_protocol.md`:664/675 (resync·response GET), 731-732 (fetch), 55/965-968 (인증 scope-out·§10.4) — resync/full-resync 엔드포인트의 trace_id 소유권(ownership) 검증을 본 프로토콜 문서에 명세할지, 6-2 Security-Governance(서버 구현은 6-12/6-9) 경계로 위임할지의 책임 배치 선택.
   - 선택지: (a) 현행 — §0 In/Out 표(L55)가 인증/세션 검증을 6-2 소유로 명시 위임, 본 문서는 401/세션만료(§10.4)만 연계 / (b) 본 문서에 403/404·ownership 검증·audit log 규칙 직접 추가
   - 판정: 현행 (a) 유지 — 본 문서 §0이 '인증/세션 재검증 구현 제외(6-2 소유)'를 명시한 도메인 경계 설계이고 정본(도메인 소유권 체계)과 무모순. 검증 자체가 누락된 게 아니라 명세 위치가 6-2임. §7.3/§7.4에 '6-2 세션+trace 소유권 검증 상속, 실패 시 403/410' cross-ref 한 줄 추가만 권고.
6. **[KEEP]** `docs\sot 2\6-11_Hologram-Main-LLM\06_streaming-canvas\token_rendering.md`:264-269 (§5.1 파이프라인 채택표) — 메인 응답 Markdown 렌더 경로의 raw HTML/sanitizer 정책 — remark→rehype 기본 파이프라인(raw HTML 미통과, safe-by-default)에 암묵 의존할지, artifact_rendering(L379 DOMPurify 명시)처럼 명시 정책을 둘지의 보안 정책 표기 선택.
   - 선택지: (a) 현행 — unified+remark-parse+remark-rehype+rehype-react 기본값(allowDangerousHtml=false)이 raw HTML을 통과시키지 않으므로 암묵 안전 / (b) rehype-sanitize·URL allowlist·HTML_SANITIZED 전용 경로를 token_rendering에 명문화
   - 판정: 현행 (a) KEEP — 채택된 파이프라인의 표준 기본 동작이 raw HTML을 렌더하지 않아 객관 결함이 아닌 명세 강도 선택. 단 UserResponseFormat에 HTML_SANITIZED가 존재(response_formatting L154)하므로, 방어선 명문화를 위해 §5.1에 'allowDangerousHtml=false 고정 + HTML_SANITIZED는 rehype-sanitize 경유' 1행 추가를 권고(정본 모순은 아니므로 CHANGE 아님).
7. **[KEEP]** `docs\sot 2\6-11_Hologram-Main-LLM\performance_benchmark_baseline.md`:30 (T-6) + stream_protocol.md:586-593 (백오프 표) — T-6 'SSE 재연결 시간 <5s (P95)'의 측정 범위 정의 — 첫 재연결 시도 지연인지, 성공까지 총 소요인지, 그리고 지수 백오프(3차 누적 7s~5차 31s)와의 양립 방식 선택.
   - 선택지: (a) P95 성공-기준 해석 유지 — 정상망에서 1~2차(누적 ≤3s) 성공이 대다수이므로 P95<5s와 백오프 표는 양립, 3차 이상은 꼬리 5% / (b) '첫 attempt 시작 시간'으로 재정의 / (c) 백오프 표를 SLO에 맞춰 단축
   - 판정: 현행 (a) KEEP — P95 지표는 꼬리(3차 이상 재시도)를 허용하는 통계 정의라 백오프 표(stream_protocol §6.1 정본, realtime_update와 verbatim 공유)와 수치 모순이 아님. 백오프 변경(c)은 peer 2개 문서 verbatim 정합을 깨므로 비권장. T-6 비고란에 '성공까지 시간, P95, 자동재시도 5회 내' 측정 범위 1행 명시만 권고.
8. **[KEEP]** `docs\sot 2\6-11_Hologram-Main-LLM\07_orchestration-layer\cost_evidence_log.md`:492-514 (write_all_stores·위반 시 롤백), 645-650 (recovery.action=rollback_stores), 675 (TS-CEL-12) — store_write_order 위반 시 rollback_stores의 구현 전략 — snapshot-restore 방식인지 per-store compensation 방식인지, idempotency/재실패 처리 수준을 어디까지 명세할지의 복구 아키텍처 선택.
   - 선택지: (a) 현행 — rollback_stores 액션·next_retry_ms=100·user_facing=false만 계약으로 규정, 메커니즘은 구현 자유 / (b) write 전 7-store snapshot + 역순 restore 명세 / (c) store별 compensation action 테이블 명세
   - 판정: 현행 (a) KEEP — 정본(LOCK-HM 체계·overlay_schema store_write_order verbatim)은 쓰기 순서만 규정하고 롤백 메커니즘은 무규정이므로 구현 선택지. 동기 7-store 메모리 쓰기라 snapshot-restore가 자명한 구현이며 계약 수준 명세로 충분. 차기 개정 시 §8.1에 'write 전 스냅샷 보관 → 역순 복원' 2행 추가 권고(의무 아님).
9. **[KEEP]** `docs\sot 2\6-11_Hologram-Main-LLM\03_ui-state-machine\state_definitions.md`:375-377 (근거/실행/포맷 축) vs 340/353 (retryAxis·user.retry.* 영문) vs 391 (evidence 재수집) — 재시도 3축의 표기 컨벤션 — 기계값(retryAxis enum·trigger명)은 영문 {evidence, execution, format}, 본문 산문·에러표는 한글 {근거, 실행, 포맷}으로 이원화할지, 단일 언어로 통일할지의 네이밍 선택.
   - 선택지: (a) 현행 이원화 유지 (기계값 영문 / 표시·산문 한글, 1:1 대응 자명) / (b) 문서 전체 영문 통일 / (c) 한↔영 매핑 표 1개 추가
   - 판정: 현행 (a) KEEP — 근거=evidence, 실행=execution, 포맷=format 1:1 대응이 명확하고 trigger/ctx 기계값은 영문으로 일관(L340/353/472)되어 구현 모호성 없음. 정본 위반 없는 표기 컨벤션 선택. §5 에러표 옆에 '(근거=evidence/실행=execution/포맷=format)' 매핑 1행 추가만 권고.

> notes: 앵커 9건과 정확히 일치 (count_found=9, 짜맞춤 아님 — 후보 도출이 자연히 9건으로 수렴). 도출 절차: (1) mf_in 객관결함 25건(i0~i24)을 소스 ID로 역매핑해 제외 — T8-002/004/009/033/034/035/038/065/067/080/097/105/129/141/143/161/162/175/186/204, T6-234/235, AUD-001~005 (T8-106은 mf_in i21과 동근원 중복, T8-185는 i14와 동근원 중복으로 제외). (2) verify=refuted 오탐 9건 제외 — T8-005/010/019/089/091/117/128/185/262. (3) 잔여 9건 전수를 디스크 실측 확인 후 등재. 디스크 라인 보정: T8-108은 finding L192→현재 L193, T6-273은 L31→L32. 기해소 확인사항: 세션5 객관 168건 적용 흔적이 디스크에 확인됨 — stream_protocol.md L707-713에 handleGap 후 OOO 버퍼 flush(T8-161 해소), L741-748에 빈배열/partial escalation(T8-162 해소)이 이미 패치되어 있음 (둘 다 

### 6-12_Event-Logging (9건)

1. **[KEEP]** `docs/sot 2/6-12_Event-Logging/02_logging-standard/failure_code_registry_v2.md`:282-283 (§3.5 심각도 P1 / 권고 레벨 WARN) — P1(긴급) SDAR_REPAIR_FAIL의 권고 로그 레벨을 ERROR가 아닌 WARN으로 두는 레벨 매핑 선택
   - 선택지: (a) WARN 유지(자동 fallback 활성 가능 시, V1 §4.11 정본 cite) vs (b) HITL 에스컬레이션 경로이므로 ERROR 격상
   - 판정: KEEP WARN — 정본 우선: V1 §4.11 권고 레벨 cite + log_level_spec §4.1 규약 'SDAR_* (V2) → WARN, 예외 없음'(충돌 시 본 규약 우선 명시)과 정합하며, 알림 부족은 FB_SDAR_ESCALATE HITL + 운영자 알림(TS-SDAR-REPAIR-1)으로 보상됨
2. **[KEEP]** `docs/sot 2/6-12_Event-Logging/02_logging-standard/failure_code_registry_v2.md`:155-156 (§3.2 심각도 P3 / 권고 레벨 WARN) — COND_BATCH_TIMEOUT P3(정보)를 INFO가 아닌 WARN으로 매핑하는 선택 — LOCK-EL-07 연계 규칙(§2.2)이 P2/P1만 명시하고 P3은 미규정
   - 선택지: (a) WARN 유지('P3 정보지만 운영 알림 가치' 근거 명기) vs (b) P3→INFO 일괄 규칙 신설 vs (c) §2.2에 P3→WARN 규칙 명문화
   - 판정: KEEP WARN — 정본 우선: log_level_spec §4.1 규약 'COND_* (V2) → WARN (예외 COND_BLOCK=ERROR)'이 이미 상위 규약으로 커버하므로 LOCK 위반 없음, 레지스트리 행에 근거('운영 알림 가치')도 명기됨
3. **[KEEP]** `docs/sot 2/6-12_Event-Logging/03_trace-context/loki_integration_v3.md`:67 (§3 알림 룰 4 EXP_A2A_AUTH_FAIL [5m] > 5, FB_A2A_RETRY mTLS 재시도 3회) — A2A 인증 실패 알림 임계값(>5/5m)과 lockout 없는 재시도 전용 폴백 전략의 선택
   - 선택지: (a) >5/5m + FB_A2A_RETRY 유지 vs (b) 임계 하향(>0~3) + rate-limit/lockout 에스컬레이션 추가
   - 판정: KEEP — 정본 우선: FB_A2A_RETRY는 fallback_registry V1 canonical cite-only 값이고 임계값은 LOCK 미규정 자유 설계값, ERROR 레벨 + 보안 라우팅으로 모니터링은 확보됨 (lockout 정책은 6-2 Security 소관의 향후 확장 후보)
4. **[KEEP]** `docs/sot 2/6-12_Event-Logging/02_logging-standard/log_level_spec.md`:402 (§6.4 '총 penalty ≥ 0.30 이면 강제 ERROR 승격(추가 규칙)') — 누적 confidence penalty 0.30을 강제 ERROR 승격 임계로 두는 추가 규칙의 임계값/적용 범위 선택
   - 선택지: (a) ≥0.30 승격 규칙 유지 vs (b) 누적 단위(요청별/이벤트별) 명문화 후 유지 vs (c) 규칙 삭제(Phase별 레벨로 충분)
   - 판정: KEEP — 임계값은 LOCK 미규정 설계값이며 R6(-0.50, 이미 CRITICAL)과의 충돌 주장은 레벨 승격이 단조(max) 연산이라 실효 모순 없음; 본문 우선순위상 §6.4가 자체 정본('충돌 시 본 규약 우선')
5. **[KEEP]** `docs/sot 2/6-12_Event-Logging/02_logging-standard/never_auto_detector.md`:170 (detect_never_auto confidence_penalty=-0.20 고정) vs 260-262 (§4.2 HITL 승인 -0.10 / 거부 -0.20) — 탐지 시점에 잠정 penalty -0.20(레지스트리 정본값)을 선할당하고 HITL 승인 성공 시 -0.10으로 완화하는 2단계 penalty 부여 설계
   - 선택지: (a) 탐지=잠정 -0.20, 결과 확정 후 §4.2 표로 최종값 적용(현행) vs (b) 탐지 시 penalty 미할당, HITL 결과 후 일괄 부여
   - 판정: KEEP — 정본 우선: 탐지 verdict의 -0.20은 failure_code_registry §9 'CRITICAL/NEVER_AUTO −0.20' 정본 cite이고 §4.2가 결과별 최종값(-0.10/-0.20/-0.50)을 별도 정본(registry §9 + fc_fb_mapping §4)으로 명시하므로 보수적 선할당-후완화는 무모순 설계
6. **[KEEP]** `docs/sot 2/6-12_Event-Logging/02_logging-standard/never_auto_detector.md`:192-195 (_route_rule: R1 명시 분기 + '그 외 OC_I5_POLICY_BLOCK → R1 기본값') — OC_I5_POLICY_BLOCK 미분류 케이스를 가장 일반적/엄격한 R1으로 fail-safe 기본 라우팅하는 설계 (S3 가드 분기와 기본값이 동일 결과)
   - 선택지: (a) R1 기본값 유지(명시 분기는 정상 경로 문서화 역할) vs (b) 미분류 케이스 전용 R0/UNKNOWN 분기 신설 vs (c) S3 가드 제거
   - 판정: KEEP — R1 기본값은 NEVER_AUTO 도메인에서 가장 안전한 fail-closed 선택이고(어느 경로든 CRITICAL+escalate), 가드 분기는 R4/R5 판별 순서를 정의하는 역할로 기능상 무해; 정본 위반 없음
7. **[KEEP]** `docs/sot 2/6-12_Event-Logging/01_event-system/event_schema.md`:116 (§2.3 선택 필드 `severity`) vs log_level_spec LogRecord `level` / registry 'Level 권고' — 이벤트 envelope 계층의 선택 필드명은 `severity`, 로그 레코드 계층은 `level`로 계층별로 다른 필드명을 쓰는 명명 설계
   - 선택지: (a) 계층별 이원 명명 유지(envelope=severity, log=level) vs (b) 전 계층 `level` 단일화
   - 판정: KEEP — structured_logging §3.1 row 7이 `severity`→`level`(add_log_level) 매핑을 명시적으로 정본 등재해 두 명칭의 대응이 문서화되어 있고, LOCK-EL-07은 5단계 값만 잠그지 필드명은 잠그지 않음(비필수 권고 필드, non-LOCK 명시)
8. **[KEEP]** `docs/sot 2/6-12_Event-Logging/02_logging-standard/log_level_spec.md`:237 (§3.2.5 'LOCK-EL-06 5규칙'), 308-315 (§4.3 NEVER_AUTO 5규칙 표) vs never_auto_detector §3.3 (5규칙→3 FC 매핑) — NEVER_AUTO를 '탐지 상황 5규칙(R1~R5)'으로 표현하면서 정본 코드는 3 FailureCode로 수렴시키는 m:1 프레이밍 설계
   - 선택지: (a) 5규칙 표현 유지(탐지 상황) + 3코드 정본(LOCK-EL-06) 이원 구조 vs (b) 3코드 단일 표현으로 통일 vs (c) log_level_spec에 5→3 수렴 각주 추가
   - 판정: KEEP — 정본 우선: LOCK-EL-06 정본 범위(3코드)는 never_auto_detector §3.3 표가 R1~R5→3 FC 매핑으로 이미 reconcile했고(P1-9), 탐지 규칙 수와 코드 수를 분리하는 것은 검증 가능한 정본 위반이 없는 표현 설계
9. **[KEEP]** `docs/sot 2/6-12_Event-Logging/CONFLICT_LOG.md`:6 (헤더 OPEN 0/RESOLVED 6) vs 15, 29 (본문 CFL-EL-001/002 '상태: OPEN') + AUTHORITY_CHAIN.md 172-177 (§7.5 OPEN 2 스냅샷) vs 300-302 (§7.12.3 OPEN 0) — 메타 문서를 append-only로 운영해 본문 등재 시점 상태(OPEN)와 단계별 스냅샷(§7.5)을 byte 보존하고, 현행 상태는 헤더·변경이력 row로만 갱신하는 문서화 컨벤션
   - 선택지: (a) append-only 유지 + 헤더/변경이력=현행 정본(현행) vs (b) 본문 상태를 RESOLVED로 in-place 갱신 vs (c) §7.5에 'historical snapshot' 라벨만 추가
   - 판정: KEEP — 정본 우선: 현행 상태의 정본은 헤더 L6('OPEN 0건 ✅')와 v1.4/v1.5 변경이력 row이며, 본문 OPEN 보존은 6-5/6-7 등 도메인 횡단 선례가 확립된 append-only 컨벤션(V1 byte-prefix SHA UNCHANGED 엄수)이라 모순이 아닌 의도된 설계

> notes: 전수 처리 완료(표본 없음). 입력 4파일 dedup 결과: clc 25건 + tight 15건(전부 clc 부분집합) + GPT 12건 → mf_in 객관 19건(i0~i18)과 동일/중복인 T8-001·T6-019, T8-026, T5-056, T8-007, T8-010, T8-021, T8-020, T8-009, T8-075, T8-076, T8-083, T8-043, T8-059, T5-040, EL-AUDIT-003/004/005/006/007/009 제외. 추가 제외: T6-004(인용 시작라인 5814 vs 5830 — 단순 표기), T8-093(plan 48→52 수치 — 최종 정본 48=44+4로 객관 영역, 설계선택 아님), EL-AUDIT-008(stale 참조 46건 실재하나 CFL-EL-002 RESOLVED 자체가 'V3 단계 일괄 교정 forward-defined' 결정이므로 잔존은 결정 이행 상태 — 9번 항목의 append-only/V1 동결 컨벤션과 동일 뿌리라 별도 등재 안함), EL-AUDIT-010(structured_logging L269 startup 예시가 자기 파일 §3.1 required 규칙 위반 — 객관성 결

### 2-1_Blue-Node-Architecture (8건)

1. **[KEEP]** `docs\sot 2\2-1_Blue-Node-Architecture\01_permission-matrix\integration_test_permission.md`:319 — IT-PM-13(MCP tier read-only → PermissionLevel.READ) 테스트 행의 LOCK 인용 범위를 BN-02(레벨 의미)+BN-11(MCP 전송 경로 맥락)로 잡은 인용 granularity 선택 — tier→Level 매핑 자체를 고정하는 LOCK은 존재하지 않음.
   - 선택지: (a) 현행 BN-02+BN-11 병기 유지 (b) BN-11 제거하고 07_mcp-bridge §6.2 본문 인용으로 교체 (c) tier→Level 매핑 전용 LOCK 신설
   - 판정: KEEP 현행 — 매핑 정본은 LOCK이 아닌 07 §6.2 본문이며(정본 우선순위상 본문 수준), 시나리오가 MCP 외부 클라이언트 경로(LOCK-BN-11 streamable_http 전송)를 실제로 경유하므로 BN-11 병기는 맥락 인용으로 무모순. tier 라벨 명칭 문제는 mf_in i5가 객관결함으로 별도 처리함.
2. **[KEEP]** `docs\sot 2\2-1_Blue-Node-Architecture\04_node-lifecycle\integration_test_lifecycle.md`:327-337 (시나리오 E), 394 (IT-LC-08) — 도메인 우선순위 선점 알고리즘(PriorityComparator/priority_evict)을 04 §11 정본화 이전에 '합리적 추론' 기반으로 선행 테스트 명세하는 방법론 선택.
   - 선택지: (a) 추론 기반 테스트 유지 + Phase 3 정본화 시 동기화 (b) 정본화 전까지 시나리오 E/IT-LC-08 제거 (c) 04 §11에 즉시 알고리즘 정본화
   - 판정: KEEP 현행 — L337 'MODULE-ARCH 경계' 노트가 비정본 상태(LOCK-BN-12/15 임계값 기반 합리적 추론, Phase 3 baseline 확정 시 04 §11 정본화 예정)를 명시적으로 선언하고 있고, P0>P1>P2 선점 순서는 LOCK-BN-05 우선순위 위계와 정합. 검증 가능한 정본 위반 없음.
3. **[KEEP]** `docs\sot 2\2-1_Blue-Node-Architecture\01_permission-matrix\integration_test_permission.md`:339 (-0.1), 341 (-0.15), 382 (0.0); sibling 02_core-node-interface/integration_test_core_bn.md:345/375 (-0.2/-0.3/-1.0) — confidence_penalty 크기 값 선택 — Permission층 -0.1(CAP_EXCEEDED 관측)/-0.15(강제 우회), Interface층 -0.2(TRACE_ID_MISMATCH)/-0.3(필드 누락)/-1.0(Node-to-Node 직접통신, 재시도 금지). JSON 샘플 0.0은 무오류 성공 케이스.
   - 선택지: (a) 현행 계층별·오류유형별 독립 값 유지 (b) 전 도메인 단일 penalty 스케일 레지스트리 통일 (c) penalty 제도 폐지
   - 판정: KEEP 현행 — penalty 값을 고정하는 LOCK/SOT 정본이 없고 L341이 '단위 없음, 상대 점수'로 성격을 명시. 위반 심각도에 따른 차등(-0.1 관측성 → -1.0 LOCK-BN-14 위반)은 합리적 설계 재량이며 0.0 샘플은 성공 경로라 모순 아님. Phase 3에서 스케일 근거 주석 추가는 선택적 개선.
4. **[KEEP]** `docs\sot 2\2-1_Blue-Node-Architecture\01_permission-matrix\integration_test_permission.md`:316 (IT-PM-10), 292 (W-04-b), 296 (검증 포인트) — Permission 통합테스트 한 시나리오 안에서 계층 경계 횡단 기대값(Permission allowed=true + 상위 Gate CAP_EXCEEDED 거부)을 함께 검증하는 테스트 설계 선택.
   - 선택지: (a) 현행 — 통합테스트가 Permission/Lifecycle 경계 협력을 1시나리오로 검증 (b) CAP_EXCEEDED 기대값을 04 lifecycle 테스트로 이관하고 IT-PM-10은 allowed=true까지만 검증
   - 판정: KEEP 현행 — W-04-b(L292)와 검증 포인트(L296 'Permission 층은 Cap 책임이 아니다 — LOCK-BN-12/15는 Lifecycle/Cap 층 책임')가 계층 책임을 명시한 상태에서 경계 협력을 검증하는 것은 통합테스트 고유 목적이며, §8.1 L339가 CAP_EXCEEDED를 '신설 — W-04'로 출처 표기해 층 책임 혼동 없음. 정본 위반 아님.
5. **[🔧CHANGE]** `docs\sot 2\2-1_Blue-Node-Architecture\BLUE_NODE_ARCHITECTURE_상세명세.md`:114-150 (§2.1 VamosMessage) — 상세명세 §2.1의 비-LOCK 필드(auth_token/permission_level/signature/correlation_id/version/heartbeat 등) 처분 — 종합계획서 L420이 '삭제 또는 MODULE-ARCH 확장 필드로 재분류' 양자택일을 설계자 선택으로 열어둠. 단 현재 디스크의 §2.1 스키마(message_id/destination/payload 구조)는 LOCK-BN-16(id, type, source, target, content, metadata 필수)과 모순 상태로 잔존하며 §1.1과 달리 정본위임 주석이 없음.
   - 선택지: (a) §2.1 전면 재작성(K-049 기준, PLAN 절차 1) (b) §1.1 세션5 교정 선례에 따라 정본위임 주석 추가 + 잔여 필드 MODULE-ARCH 확장 초안으로 격하 (c) §2.1 삭제
   - 판정: PLAN 3.0(종합계획서 L415-421 선행 교정) + DESIGN LOCK(LOCK-BN-16) 우선 — 02_core-node-interface/_index.md §1이 LOCK 구현 정본(L77-84)이고 07 L299가 CF-007 해소를 기록하므로, 최소 침습인 (b) 정본위임 주석 방식 채택(§1.1 L35 기교정 선례와 동일 패턴).
6. **[🔧CHANGE]** `docs\sot 2\2-1_Blue-Node-Architecture\BLUE_NODE_ARCHITECTURE_상세명세.md`:152-213+ (§2.2 NodeRequestEnvelope, §2.3 NodeResponseEnvelope) — 상세명세 §2.2~2.3의 비-LOCK 필드(conversation_turn/task_type/task_params/relevant_memory/template_set_id/response_id/confidence/memory_updates 등) 처분 — 종합계획서 L426/L434가 '삭제 또는 constraints 내부/MODULE-ARCH 확장 재분류' 선택지를 열어둠. 단 현재 디스크의 §2.2/2.3은 LOCK-BN-03(7필수)/LOCK-BN-04(7필수, status 2종 success|fail)와 모순 상태로 잔존(status 4종 포함)하며 정본위임 주석 없음.
   - 선택지: (a) §2.2~2.3 전면 재작성(AC-D3-004/005 기준, PLAN 절차 2~3) (b) 정본위임 주석 추가 + 잔여 필드 constraints 내부/MODULE-ARCH 확장 격하 (c) §2.2~2.3 삭제
   - 판정: PLAN 3.0(종합계획서 L422-434 선행 교정) + DESIGN LOCK(LOCK-BN-03/04) 우선 — 02_core-node-interface/_index.md §2~§3이 7필수+5선택 구현 정본이고 07 L299가 '상세명세 L2 필드는 02에서 삭제됨(intent_summary 통합/constraints 재분류)'을 기록하므로, 최소 침습인 (b) 정본위임 주석 방식 채택(§1.1 기교정 선례 동일 패턴).
7. **[KEEP]** `docs\sot 2\2-1_Blue-Node-Architecture\05_memory-sharing\_index.md`:513 (CAS conflict → BN 재시도), 601-602 (재시도 책임/LWW 모드) — CAS 충돌 재시도 책임을 MemoryBroker가 아닌 BN(클라이언트)에 위임하고 재시도 파라미터(max_attempts/backoff/jitter/idempotency key)를 미고정, expected_version 미명시 시 LWW 기본 — 동시성 제어 전략 선택.
   - 선택지: (a) 현행 — BN 재시도 책임 + LWW 기본(단일 라이터 권장) 유지, 파라미터는 Phase 3 구현 결정 (b) MemoryBroker 측 재시도 정책(max_attempts/backoff/idempotency) 정본 고정 (c) LWW 폐지, CAS 전면 강제
   - 판정: KEEP 현행 — L602가 'V1 단일 프로세스 가정 부합, D2.0-03 K-029 Line 904'를 SOT 근거로 명시한 의도적 위임이고, is_critical 경로는 LOCK-BN-10 Gate 승인으로 별도 보호(L517-519). 재시도 파라미터를 고정하는 정본이 없어 위반 없음. V2 멀티프로세스 전환 시 BN MemoryClient 표준 재시도 정책 정의를 Phase 3 이월 항목으로 권장.
8. **[KEEP]** `docs\sot 2\2-1_Blue-Node-Architecture\07_mcp-bridge\_index.md`:214-220 (MCPClient 모델), 471-476 (인증 6단계) — 외부 MCP 클라이언트의 권한 scope 축을 allowed_node_ids + allowed_tool_patterns 2축으로 한정하고 project/session binding(allowed_project_ids)을 도입하지 않은 테넌시 경계 아키텍처 선택 — project_id/session_id는 Bridge 세션 컨텍스트에서 주입(L296-315).
   - 선택지: (a) 현행 — node/tool 2축 scope + Bridge 컨텍스트 주입 유지 (b) MCPClient에 allowed_project_ids 추가 + 인증 단계 4~6 사이 project/session scope 검증 신설
   - 판정: KEEP 현행 — VAMOS V1은 단일 사용자 로컬 시스템 전제로 교차 프로젝트 위협 모델이 약하고, AuthResult가 permission_level ≤ 4 상한(Level 5 금융 매핑 절대 금지, L226-232 LOCK 주석)과 단계 6 required_permission_level 검증으로 방어선을 보유. project binding을 요구하는 정본 부재(GPT 원판정도 is_confident=false). 멀티테넌트 노출 시점(V3 Realtime API 확장)에 (b) 검토를 권장.

> notes: 원판정 앵커 8건과 정확히 일치(짜맞춤 아님 — 자연 도출). 도출 과정: 전체 후보 = clc 21 + GPT 17(tight 10은 clc 부분집합, 신규 0). (1) mf_in 객관 16건과 동일/중복 제외: T8-088/T8-089/T6-090/T6-100/T5-101/T8-102/T8-103/T8-104/T8-006(clc) + BN-AUD-001/002/005/006/007/008/009/010/011/012/013/014/017(GPT). (2) verify=refuted 6건 오탐 제외: T8-017/T8-022/T8-055/T8-057/T8-080/T8-081 — T8-022는 AUTHORITY_CHAIN L72 LOCK-BN-19가 '일반 10분 / P2(HITL) 5분'을 직접 정의함을 실측해 refuted 타당성 재확증. (3) verify=uncertain 2건(T6-039/T6-040) 제외: SOT(D2.0-03/D2.0-01) 인용 충실도 주장으로 설계 선택이 아니며 도메인 외부 문서 검증 필요 — 주관 분류 부적합. 잔여 8건 전수 디스크 실측 후 등재. 기해소 관찰: 상세명세 §1.1(L26-35)은 세션5에서 LOCK-BN

### 0-0_Governance-Rules-Meta (7건)

1. **[KEEP]** `docs\sot 2\0-0_Governance-Rules-Meta\03_phase-checklists\S8-4_QC_RESULT.md`:492 — Post-Review §13에서 COMPLETENESS_MATRIX 3번째 차원 0.0%를 차원 명칭·사유 설명 없이 '✅ 확인'으로 수용하는 QC 보고 granularity 선택.
   - 선택지: (a) 현행 유지 — 0.0%는 해당 단계 미적용 차원으로 수용, 설명 생략 / (b) 3축 명칭과 0.0% 사유 주석 추가 / (c) 미설명 0값을 검증 FAIL로 처리
   - 판정: KEEP — COMPLETENESS_MATRIX 3축의 정의를 강제하는 정본(RULE 1.3/PLAN 3.0/DESIGN LOCK)이 부재하므로 검증 가능한 정본 위반이 없고, 0.0%를 어느 수준까지 해설할지는 QC 작성자의 보고 설계 선택이다(주석 보강은 권고 수준).
2. **[KEEP]** `docs\sot 2\0-0_Governance-Rules-Meta\GOVERNANCE_RULES_META_규칙서.md`:164 (L3 pipeline_stages), 182 (L21 9-State), 89 (Glossary S0~S8) — 5단계 논리 파이프라인(intake→plan→execute→verify→deliver, LOCK L3)과 9-State 상태머신(S0~S8, LOCK L21)을 명시적 매핑 없이 이중 상태 모델로 공존시키는 아키텍처 선택.
   - 선택지: (a) 이중 모델 유지 — L3은 논리 단계, L21은 실행 상태머신으로 추상화 수준 분리 / (b) 단일 모델로 통합 / (c) 5단계↔9-State 매핑 표를 본문에 추가
   - 판정: KEEP — 두 모델 모두 DESIGN LOCK급 정본(L3=PHASE_B4 §3.1, L21=pipeline.py)으로 동급이며 상호 모순 값이 아니라 추상화 수준이 다른 공존 설계다. 정본 우선순위상 어느 쪽도 다른 쪽을 무효화하지 않으므로 현행 유지(매핑 표 추가는 개선 권고일 뿐 결함 아님).
3. **[KEEP]** `docs\sot 2\0-0_Governance-Rules-Meta\GOVERNANCE_RULES_META_규칙서.md`:386 — 보안 검토 기준의 PII 마스킹을 precision/recall/FN 허용치 분해 없이 '주민번호/전화번호/이메일/카드번호 탐지율 99%+' 단일 지표로 정의하는 스펙 granularity 선택.
   - 선택지: (a) 99%+ 단일 임계 유지 — 세부 메트릭·테스트셋·실패 정책은 6-2 Security 구현 레벨에 위임 / (b) recall/precision/FN 허용치/테스트셋/실패 시 deny·quarantine 정책으로 분해 정의
   - 판정: KEEP — 99%+는 검증 가능한 정본 위반이 없는 임계값 설계 선택이며, 거버넌스(0-0) 문서는 상위 기준만 LOCK하고 메트릭 분해는 6-2 도메인 구현 명세에 위임하는 계층 구조가 정본 우선순위(RULE>PLAN>LOCK>본문)와 정합한다.
4. **[KEEP]** `docs\sot 2\0-0_Governance-Rules-Meta\GOVERNANCE_RULES_META_규칙서.md`:115 (R4), 133 (§2.2 #4) — R4 no-delete를 예외 없는 절대 규칙으로 두고 삭제 필요 시 '[DEPRECATE] + 대체 경로' 단일 경로만 허용하는 거버넌스 정책 선택(SECURITY/SECRET 사유 hard delete 예외 절차 미정의).
   - 선택지: (a) 무예외 no-delete 유지 — AI 임의 삭제로 인한 자산 소실 방지가 최우선 / (b) SECURITY/SECRET/LEGAL 사유 승인 기반 hard delete 예외 Gate + 감사 로그 추가
   - 판정: KEEP — R4는 Part2 §1.3 원문에서 직수입된 최상위 정본(RULE 1.3급) 규칙으로, 무예외 no-delete 자체가 의도된 설계다. 예외 추가는 정본 변경(R-T0-1 전 도메인 동기화) 사안이지 결함 교정이 아니며, 비밀정보 파일은 [DEPRECATE]+마스킹으로 처리 가능해 정본 모순이 없다.
5. **[KEEP]** `docs\sot 2\0-0_Governance-Rules-Meta\PROMPT_INTEGRITY_REPORT.md`:120-138 (PI-1~PI-4), 156-160 (결론 PASS) — 프롬프트 정합성 게이트에서 ERROR/MINOR 2단 심각도를 두고, 라인범위·SOT출처 헤더 미명시 4건(PI-1~PI-4)을 '산출물 영향 0건' 근거로 MINOR=비차단 PASS 처리하는 QC 게이트 정책 선택.
   - 선택지: (a) 현행 유지 — 산출물 영향 0건이면 MINOR는 권고로만 이월(Phase 8 참고 전달) / (b) MINOR도 정확한 Part2 라인 범위·SOT 경로 보완 후에만 PASS / (c) 영향 0건 판정의 근거 파일/라인 추가
   - 판정: KEEP — 어느 정본도 'MINOR 미명시 시 차단'을 강제하지 않으며, 각 MINOR에 보완 경로(INTEGRATION_PLAN §3 대조 가능)와 산출물 정확성 확인이 기재되어 있어 게이트 심각도 체계는 검증 프로세스 설계자의 합리적 선택이다.
6. **[KEEP]** `docs\sot 2\0-0_Governance-Rules-Meta\GOVERNANCE_RULES_META_규칙서.md`:171-173 (LOCK L10~L12), 423 (§3.6.5 #8), 92 (P0=긴급 정의) — self_check 임계값을 P0≥70 < P1≥75 < P2≥80으로 — 즉 긴급도가 높을수록 낮은 품질 임계를 부여(속도 우선)하는 임계값 설계 선택.
   - 선택지: (a) 현행 유지 — P0=긴급(L92 정의)이므로 낮은 임계로 신속 통과, 위험은 NEVER_AUTO(L23 P1+ 자동승인 금지) 등 별도 게이트가 보완 / (b) P0/P1/P2를 위험도로 재정의하고 P0 임계를 최고로 역전
   - 판정: KEEP — L10~L12는 PHASE_B4 §3.8a 출처의 DESIGN LOCK 정본이고, 규칙서 L92가 P0~P3을 '우선순위(P0=긴급~P3=낮음)'로 명시해 위험도 해석 여지가 정본상 없다. 긴급 작업의 낮은 self-check 임계는 승인 게이트와 분업하는 일관된 설계로 정본 모순 없음(원판정 GPT 측도 is_confident=false).
7. **[KEEP]** `docs\sot 2\0-0_Governance-Rules-Meta\GOVERNANCE_RULES_META_규칙서.md`:90, 181 (LOCK L20), 417 (§3.6.5 #2); GLOSSARY_CROSS_DOMAIN.md:156-157 — 전역 VAMOS-5-Gate 순서를 Policy→Approval→Cost→Evidence→SelfCheck(Approval이 Evidence 선행)로 하고, SDAR-Gate는 PolicyGate→EvidenceGate→CostGate→ApprovalGate→SelfCheckGate 별도 순서로 분리 운영하는 게이트 순서 아키텍처 선택.
   - 선택지: (a) 두 체계 별도 유지 — GLOSSARY §13이 접두사 구분 규칙('5-Gate 단독=VAMOS 정본, SDAR/CL은 접두사 필수')으로 공존 등재 / (b) Evidence 선행으로 전역 순서 변경 통일 / (c) EvidenceGate 의미(승인 전 근거검증 vs 승인 후 증빙기록) 주석 명시
   - 판정: KEEP — L20 LOCK(pipeline.py)이 VAMOS-5-Gate 순서의 DESIGN LOCK 정본이고, GLOSSARY §13(Phase 11 S11-6 CM-1)이 SDAR-Gate를 용도 상이(수리 안전성 평가 전용)한 별도 체계로 이미 정본 등재해 직접 충돌이 없다. 전역 게이트에서 Approval 선행은 사용자 승인 후 비용·근거 검증을 수행하는 설계자의 순서 선택이며 정본 모순 미발견(원판정 GPT 측도 is_confident=false).

> notes: 앵커 7건과 정확히 일치(짜맞춤 없이 자연 도출). [제외 내역] (1) mf_in 객관결함 10건과 동일/중복: GOV-001=i0(V0 비용), T6-053=i1(자율도 오프셋), T6-050·GOV-002=i2(§2.9 범위), T5-051=i3(3-10 명칭), GOV-003=i4(R1~R9 재사용), GOV-006=i5(DEFINED-HERE 40건), GOV-007=i6(DH-SDAR-T1/DH-CL-D1), T8-059·GOV-004=i7(DEPENDENCY_GRAPH §5.2 vs §7), GOV-005=i8(34/35/36 도메인 수), T8-035=i9(R-63-7 off-by-one). (2) verify=refuted 오탐 5건: T8-001, T8-011, T8-012, T6-036(RAGAS 0.80/0.85), T8-081. (3) 단순 표기 1건: T5-057 'L2(COPILOT)' vs 'L2_COPILOT' underscore 유무(규칙서 L26/L71 실측 — 표기 형식 분기일 뿐 값 동일). [기해소 관찰 — 객관분이라 등재 대상 아님] 세션5(2026-06-11) 교정이 디스크에 기반영됨을 실측: 규칙서 L26 'V0=

### 6-8_Cloud-Library (7건)

1. **[KEEP]** `docs\sot 2\6-8_Cloud-Library\02_service-mesh\error_fallback.md`:133 — CL-G1 내부에 Trust 하한 서브게이트(G1_TRUST_LOW, L3 가중치 적용 후 ≤5)를 두고 FB-X 즉시 거부로 처리하는 임계값·게이트 책임 배치 선택
   - 선택지: (a) 현행 weighted ≤5 유지 (b) raw 점수 기준으로 변경 (c) G1에서 Trust 조건 제거하고 L3 소스 가중치 정책에 위임
   - 판정: (a) 현행 유지 — DESIGN LOCK L1~L22에 Trust 하한 규정이 없어 정본 위반이 아니며, 행 내 괄호 주석 '(L3 가중치 SNS=0.3 적용 후)'가 weighted 기준임을 명시해 자기일관적(가중 후 최대 7.5 대비 ≤5는 유의미한 컷)
2. **[KEEP]** `docs\sot 2\6-8_Cloud-Library\02_service-mesh\error_fallback.md`:200-205, 224, 268 — FailureCode/Fallback 수량 집계 컨벤션 — SCORE_BORDERLINE_* 코드를 V1 합계(36)에 포함할지 별도 분류할지, §5.2 매핑 행수(39행)와 정본 합계(FB 35)의 관계 정의
   - 선택지: (a) Part2 §6.10 L5743-L5787 정본 합계(FC 36/48, FB 23/35) 보존 + Borderline 별도 분류 (b) 표 행수 실측 기준으로 정본 합계 자체를 재산정
   - 판정: (a) — PLAN 3.0급 상위 정본(Part2 §6.10)의 합계 보존이 우선이며, 디스크 L203-204·L207·L268에 reconcile note('V1 합계 정본 36, +1 차이는 SCORE_BORDERLINE_G1 V1 포함 여부', '정본 합계 보존')가 이미 기재되어 집계 컨벤션이 명시화됨(기해소)
3. **[KEEP]** `docs\sot 2\6-8_Cloud-Library\03_cdn-scaling\v12_extensions.md`:89 — change_type 'gate_threshold_change'를 semver scope=minor로 분류하면서 승인정책은 MAJOR_APPROVE로 격상하는 2축 분리(영향도 분류 vs 위험 기반 승인) 설계
   - 선택지: (a) 현행: scope=minor + MAJOR_APPROVE(LOCK 보호) 병행 (b) scope를 major로 격상해 두 열을 일치
   - 판정: (a) 현행 유지 — R-68-1(SPEC §16 LOCK 불변 원칙) 보호를 승인정책 열이 단일 판정 기준으로 담보하고, 같은 행의 자동 적용=❌/승인 필수=✅ 열과 §3.5 'gate_threshold_change → 즉시 MAJOR_APPROVE (LOCK L4~L8/L19/L20 보호)' 설명으로 오독 여지가 차단됨; scope는 semver 버전 영향도 분류로 별개 축
4. **[KEEP]** `docs\sot 2\6-8_Cloud-Library\02_service-mesh\gate_details.md`:304-313 — CL-G3 PII 처리 정책 — pii_count>5에서만 G3_PII_BLOCK 차단, 1~5건은 건당 5점 감점 후 통과 허용하는 임계값·감점 계수 선택
   - 선택지: (a) 현행 임계(>5 차단, 1~5 감점×5) 유지 (b) PII≥1 즉시 redaction/quarantine 선행 (c) 임계 하향 또는 embedding 전 PII 제거 검증 추가
   - 판정: (a) 현행 유지 — DESIGN LOCK L7은 'Security_Score≥30'만 규정하고 PII 건수 임계를 정본화하지 않아 설계 재량 영역이며, 장기 저장 금지는 PII_LONGTERM_DENIED NEVER_AUTO 경로(error_fallback §4.2.10/§6)가 별도 커버; redaction 선행은 V2+(BERT/위협인텔 확장) 단계의 강화 선택지
5. **[KEEP]** `docs\sot 2\6-8_Cloud-Library\01_cloud-deploy\deployment_strategy.md`:61 — V1 디스크 용량 설계 — L12×L14 이론상한 500GB 대비 실사용 10% 가정으로 Hetzner CX31 160GB 채택(admission control 미규정)
   - 선택지: (a) 160GB + 10% 실사용 가정 명시 유지 (b) 저장 전 admission control/eviction 규칙 추가 (c) 디스크 증설로 상한 전수 수용
   - 판정: (a) 현행 유지 — DH-CL-D1(DEFINED-HERE, AUTHORITY_CHAIN §4 정본)이 V1=Hetzner CX31(160GB SSD)로 고정하고 본 파일 §2.2가 그 값 변경을 금지하며, L12/L14는 상한(cap)이지 기대 사용량이 아님; 근거 열에 'V1 실사용 10% 수용(일반 소스 ≪ 50MB)' 가정이 이미 명시되어 정본 무모순
6. **[KEEP]** `docs\sot 2\6-8_Cloud-Library\01_cloud-deploy\deployment_strategy.md`:111-114 — V1 API를 8080 포트로 노출하면서 인증/인가/TLS를 V1 범위에서 생략하는 보안 강화 단계화(phasing) 선택
   - 선택지: (a) V1 단일 호스트 무인증 유지 + V2 Swarm/V3 K8s에서 인증·TLS 도입 (b) V1부터 API 인증/TLS/RBAC 의무화
   - 판정: (a) — 정본(DH-CL-D1, LOCK L1~L22)에 API 인증 요구가 없고 V1은 단일 VM 내부 Compose 구성이라 노출면이 제한적이므로 단계화는 설계 재량; 단 finding의 승인자 무결성 부분(approver Optional, security_fix 자동)은 mf_in i=17 객관결함 트랙에서 별도 처리됨(중복 제외)
7. **[KEEP]** `docs\sot 2\6-8_Cloud-Library\FINAL_REVIEW_REPORT.md`:30-42 (및 L3_COMPLETENESS_REPORT.md:78-90) — 완결성/최종 리뷰 PASS 판정 근거로 grep occurrence 실측 + 체크리스트 방식을 채택한 검증 방법론 선택
   - 선택지: (a) grep 실측 기반 검증 유지 (b) parsed-table count·스키마 검증·산식 단일성 검사로 대체/보강
   - 판정: (a) 현행 유지 — 검증 방법론은 RULE/PLAN/LOCK이 규정하지 않는 설계 재량 영역이고 보고서가 grep 근거(39/73/60/100 occ)와 예외(V10 'PASS substantive' accepted exception)를 투명 기재함; 의미 불일치류 실결함은 객관 트랙(mf_in 18건, 세션5 168건 기적용 — gate_details.md:312 clamp 등 확인)에서 별도 교정되어 보고서 방법론 자체는 결함이 아님

> notes: 앵커 7건 = 재도출 7건 정확 일치(강제 짜맞춤 없음). [제외 내역] ① mf_in 18건 객관결함과 동일/중복: clc/tight T8-025(=i0)·T8-026(=i8)·T8-027(=i6)·T8-028(=i7)·T8-029(=i12)·T8-030(=i13)·T8-032(=i15), GPT 6-8-001(=i1)·002(=i2)·003(=i0)·004(=i3)·005(=i11)·006(=i5)·008(=i16)·009(=i14)·010(=i4)·013(=i10)·015(=i9), 6-8-014의 approver Optional 부분(=i17). ② T8-001(verify=real)은 mf i=1(G1 합산 vs Quality 단독 입력 모순)의 동일 근원 로깅 사례(디스크 error_fallback.md:437-447 score 38=4카테고리 합, quality:10 → Quality_100=40 통과여야 함)로 중복 제외 — 주관 아님. ③ verify=refuted 오탐 6건 제외: T8-012(L15 batch '초과'=OOM 트리거 조건이지 LOCK 위반 상태 아님), T8-039(gate_details.md:339 'CL-G0~G3 통과

### 6-6_Self-Evolution-System (6건)

1. **[KEEP]** `docs\sot 2\6-6_Self-Evolution-System\01_s-series-modules\s05_feedback_loop.md`:168-171 — S-5 출력 스키마의 주 작업 명칭을 FeedbackInsight로 두고 _index.md §1.1 정본 명칭 LearningUpdate를 하위 호환 별칭 서브클래스(class LearningUpdate(FeedbackInsight))로 유지하는 이중 명명 구조.
   - 선택지: (a) 현행 — FeedbackInsight 주 클래스 + LearningUpdate 별칭(스키마 동일, '정본 명칭 보존' 명시 문서화) / (b) LearningUpdate를 주 클래스로 승격하고 FeedbackInsight를 별칭으로 강등하여 §2/§3.3/§9 전반 단일 명칭 통일
   - 판정: 현행 유지 — 별칭이 s05:168-170에 '하위 호환 별칭 (정본 명칭 유지)·동일 스키마(_index.md §1.1)'로 명시 문서화되어 정본(_index §1.1 LearningUpdate)과 무모순이며 소비자 S-3는 정본 명칭으로 수신 가능. 검증 가능한 정본 위반 없는 명명 설계 선택.
2. **[KEEP]** `docs\sot 2\6-6_Self-Evolution-System\01_s-series-modules\s07_evolution_scheduler.md`:255-256 (s08_governance.md:394-421 DH-7 별개 명시) — S-8 pre-exec 재확인을 신규 평가(DH-2 600s)와 분리된 경량 게이트로 설계 — S8_PREEXEC_TIMEOUT_SEC=10s + MAX_RETRIES=2, 타임아웃 시 HOLD(다음 Cron 슬롯)→ABORT_S8_REJECT.
   - 선택지: (a) 현행 — 10s 경량 즉시 재확인(이미 1차 승인된 plan의 승인 당시 vs 현재 상태 차이 검증 전용) / (b) pre-exec에서도 DH-2 600s 전체 재평가 수행 / (c) 중간 타임아웃(예: 60s)
   - 판정: 현행 유지 — s08 §4.5(L396-421)와 AUTHORITY §5 DH-7이 '10s는 DH-2 600s와 별개 항목, 신규 평가 600s와 구분'을 명시해 finding의 전제(재확인이 600s 평가를 촉발)가 스펙상 배제됨. 1차 승인된 plan의 실행 직전 재확인 SLA로 10s+재시도2회는 합리적 설계 선택, 정본(AUTHORITY DH-7) 무모순.
3. **[KEEP]** `docs\sot 2\6-6_Self-Evolution-System\01_s-series-modules\s08_governance.md`:131-151, 609 — S-8 승인 채널에 자체 큐 깊이 상한·rate limit·deduplication 필드를 두지 않고 DH-2 600s eval_deadline 타임아웃 + 상류 S-7 back-pressure(MAX_QUEUE_DEPTH=500, MAX_JOBS_PER_TICK=20) 위임으로 보호하는 아키텍처.
   - 선택지: (a) 현행 — timeout 600s 보호 + 큐 상한은 S-7 소유(DH-7e L609 명시) / (b) GPT 권고 — S-8 자체 MAX_APPROVAL_QUEUE_DEPTH·MAX_INFLIGHT_APPROVALS·source별 rate limit·plan_id/trace_id dedup·overflow audited reject 추가
   - 판정: 현행 유지 — DH-7e(s08:609)가 '큐/틱 상한 (S-7 영역, MAX_QUEUE_DEPTH=500 — s07 §3.1 정본), 본 모듈 자체 승인 채널은 timeout 600s 보호'로 정합화되어 s07↔s08 객관 모순(mf_in i13)은 기해소 상태이며 잔여 쟁점은 순수 아키텍처 선택. 정본 무모순이므로 유지하되 S-2 직행 경로(s2_new_pattern) 폭주가 운영에서 관측되면 S-8 측 상한 추가를 후속 검토.
4. **[KEEP]** `docs\sot 2\6-6_Self-Evolution-System\01_s-series-modules\s03_strategy_optimizer.md`:246 — S-3 evolve()가 S-8 결정을 동기 대기하지 않고 COLLECT_S8_DECISIONS(plans, timeout=60s) async 수집 윈도우만 사용하여 SELF_EVO_TIMEOUT(120s) 예산 내 반환하는 호출자 측 대기 전략.
   - 선택지: (a) 현행 — 60s async 수집 후 반환, 미도착 결정은 pending / (b) DH-2 600s까지 동기 대기(S-5/S-6의 구 패턴 — mf_in i7에서 객관결함 확정) / (c) 완전 비동기 콜백 — 제출 즉시 반환, S-8 결정 이벤트 콜백으로 보상 갱신
   - 판정: 현행 유지 — 60s async는 공통 evolve 예산 120s(정본 SELF_EVO_TIMEOUT)와 무모순인 유일한 동기-수집 선택지이며 S-8 DH-2 600s는 S-8 측 결정 마감일 뿐 호출자 대기 의무가 아님. 단 60s 이후 도착 결정의 보상 반영은 mf_in i16 교정 방향(evaluation_window 만료 콜백)과 함께 (c) 콜백 경로로 수렴시키는 것을 권고.
5. **[KEEP]** `docs\sot 2\6-6_Self-Evolution-System\01_s-series-modules\s06_adaptation_engine.md`:283-284 (s07_evolution_scheduler.md:238-239, 626; AUTHORITY_CHAIN.md:123-131) — L6 순차 활성화 게이트에서 DH-1 안정화를 '에러율<1%·스키마 검증률 100%·3주기 연속 PASS' 요약형으로 운영화 — 정본 DH-1(AUTHORITY §5)은 4메트릭(에러율<1%/스키마100%/I-Module≥99%/리소스<80%)·7일 관찰.
   - 선택지: (a) 현행 — 모듈 docstring 요약 인용 + '3주기 연속 PASS'를 보조 운영 게이트로 병기 / (b) GPT 권고 — AUTHORITY_CHAIN DH-1 4메트릭·7일 전문을 그대로 인용하고 3주기 PASS는 별도 보조 조건으로 분리 명기
   - 판정: 현행 유지 — 정본 우선순위상 AUTHORITY_CHAIN §5 DH-1(4메트릭·7일·상태 확정, L123-131)이 규범이고 s06/s07 docstring은 DH-1을 명칭으로 인용하는 요약문이지 재정의가 아니므로(s08 DH 매핑 L600도 'DH-1 안정화 4메트릭 변경 없음' 확인) 정본 모순 없음. 안정화 게이트의 운영 단순화(3주기 연속 PASS 병기)는 설계 선택이며, 규범 판정 시 DH-1 전문 기준 적용을 전제로 유지.
6. **[KEEP]** `docs\sot 2\6-6_Self-Evolution-System\03_model-upgrade-strategy\upgrade_safety.md`:167-179, 512, 520-522 — ISS-5(4-4 MLOps 연동)를 송신측 6-필드 정본 스키마(ModelUpgradeRequest, 6-6→4-4 단방향 발행)로 해결 처리하고, 4-4 측 MLOpsUpgradeReceiver 직수신 채널은 §12 C-1 HIGH 향후 확장([RECHECK_FLAG: 4-4] 발행)으로 이월하는 단계적 통합 전략.
   - 선택지: (a) 현행 — sender 정본 확정 + ISS-5 ✅ 표기 + receiver는 C-1 HIGH 이월 추적 / (b) GPT 권고 — ISS-5를 sender-defined/receiver-unverified로 강등하고 4-4 receiver schema·ack·timeout 계약 완성 전 resolved 표기 금지
   - 판정: 현행 유지 — 도메인 경계상 4-4 receiver 계약은 4-4 정본 소유 영역이며 6-6은 발행 스키마를 정본 확정(§3, ISS-5 추상 정의 위임 수용)하고 §12 C-1 HIGH + RECHECK_FLAG로 투명 추적 중. 종합계획서 G4-6(L1553)에 4-4 reverse-inheritance(LOCK-ML read-only) 정합이 Phase4에 기록되어 미수신 위험도 완화됨. 정본 위반 없는 단계적 통합 scope 선택.

> notes: 읽기 전용 수행, 파일 수정 0건. count_found=6=원판정 앵커 6과 자연 수렴(짜맞춤 없음). [입력 매핑] clc 24건+tight 16건(clc 부분집합, 신규 0)+GPT 12건+mf_in confirmed 20건/unconfirmed 1건. mf_in 동일/중복으로 제외된 객관 finding: T8-001(i11)/003(i5)/004(i15)/005(i16)/006(i17)/013(i12)/018(i6)/025(i7)/029(i18)/035(i8)/036(i7 s06 동일)/049(i19)/053(i2 동일 timeout 모순)/055(i13)/073(i9)/093(i10)/103(i10 중복)/105(i0), AUD-001(i1)/002(i2)/004(i3)/005(i14)/006(i8)/007(i4)/012(i9 포함). [비주관 제외 5건] T6-012=SOT 원문 미확인 메타 finding(결함 단정 불가, 설계선택 아님); T5-031=EnvironmentMetric 체크리스트 단순 표기; T5-054=S8_/S7_ PREEXEC 접두어 단순 표기; T8-059=params.cooldown_default 의사코드 표기 수준(s07

### 5-4_v23-Extension-Items (3건)

1. **[KEEP]** `docs\sot 2\5-4_v23-Extension-Items\V23_EXTENSION_ITEMS_구조화_종합계획서.md`:815, 839, 870 vs 954 — 인덱스 자동 갱신을 '설계상 선언(Part2 로드맵 외부 트리거)'으로 두고 실제 자동화 스크립트 구현은 S-3로 Phase 3+에 이연하는 로드맵 선택.
   - 선택지: (a) 현행: §7.3은 자동 갱신을 목표 메커니즘으로 선언(L815 '자동 추적...자동 갱신됨', L839 '산출물: Part2 릴리스 시 자동 갱신', L870 '외부 트리거로 자동 실행')하고 §11 S-3(L954)는 스크립트를 LOW/Phase 3+/OPEN으로 유지 / (b) §7.3에 '현재 미구현, 수동 갱신 절차' 명시 / (c) 자동화 스크립트 입출력·트리거·실패처리 명세를 정본에 선반영
   - 판정: KEEP 현행(a). RULE 1.3/PLAN 3.0/Part2(Level 2) 어디에도 자동화 구현 시점을 강제하는 정본 없음 — §7.3의 '자동'은 Part2 종속 외부 트리거 추적 설계 선언이고 S-3는 그 구현 스크립트의 시기 선택이며, 본 도메인이 STAGE 9 B-2(L849)에서 영구 EXCLUDED(Part2 종속, 자체 수동 실행 없음)로 확정되어 Phase 3+ 이연이 합리적.
2. **[KEEP]** `docs\sot 2\5-4_v23-Extension-Items\V23_EXTENSION_ITEMS_구조화_종합계획서.md`:925-942 vs 968-980 — §10 검증 체크리스트를 미체크 템플릿(검증 기준 카탈로그)으로 유지하고 실행 검증 기록은 §12 FINAL REVIEW에 단일화하는 문서화 컨벤션 선택.
   - 선택지: (a) 현행: §10 전 항목 [ ] 유지 + §12가 실행 기록 정본(87건 전수/SOT2 경로/LOCK/거버넌스/OPEN 3건 전부 PASS, Gate APPROVED L980) / (b) §10 완료 항목을 [x]로 갱신하고 §12 PASS 근거와 상호 링크 / (c) §10 상단에 '검증 템플릿' 라벨 추가
   - 판정: KEEP 현행(a). 정본 우선순위상 §12 FINAL REVIEW(Status APPROVED — Phase 8 QC B+ → Phase 10 QC A-, L970)가 검증 실행 기록의 본문 정본이며 §10은 기준 목록으로 읽는 데 모순 없음 — 체크리스트를 템플릿으로 둘지 기록으로 쓸지는 검증 가능한 정본 위반 없는 표기 정책 선택(원하면 (c) 라벨 추가가 저비용 개선이나 필수 아님).
3. **[KEEP]** `docs\sot 2\5-4_v23-Extension-Items\V23_EXTENSION_ITEMS_인덱스.md`:4 (vs 종합계획서.md L9, CONFLICT_LOG.md L107-117 CL-002) — 인덱스 헤더 'Part2 상태'에 Part2 원문 표기(~100+ items)를 보존하고, 계획서 헤더에는 v23 subset 정밀 집계(~87건)를 쓰는 표현 방식 선택.
   - 선택지: (a) 현행: 인덱스 L4 'SHELL (~100+ items, 이름만 존재)' = SOT 원문 충실 표기, 계획서 L9 'SHELL (이름만 존재, ~87건)' = v23 정밀 집계 / (b) 두 헤더를 'Part2 원문: ~100+ / v23 subset: 87건' 병기 형식으로 통일 / (c) 양쪽 모두 87건으로 단일화
   - 판정: KEEP 현행(a). 충돌 해석은 이미 CONFLICT_LOG CL-002 RESOLVED(L107-117)가 정본으로 확정 — Part2 '~100+'는 전체 확장 범위(v12+v23+기타) 포괄 추정치, 87건이 v23 Extension Items 정본 수치 — 이므로 정본 위반 없는 표기 선택이며, SOT 원문(Part2, Level 2)에 충실한 인덱스 헤더 보존이 권한 체계(§3.2)와도 정합.

> notes: 전수 재도출 결과 주관 3건 = 원판정 앵커 3건과 정확히 일치(짜맞춤 아님, 디스크 실측 기반). [입력 전수 분해] 고유 finding 10건: CLC/tight 2건(T8-001/T8-003)은 GPT 5-4-LOGIC-001 및 mf_in i0/i1과 동일 사안으로 객관 중복 제외. mf_in 객관 6건(i0 게이트 모순, i1 81vs87, i2 DONE/DEPRECATED, i3 V3-P3 REF-only, i4 추적 34/87, i5 T-03 오라클)은 제외 기준이며 전부 2026-06-11 세션5 기적용으로 디스크에서 기해소 확인: R-20-2 L232 단일 게이트 명시, 인덱스 분포표 L184/190/193/194/196 = 87 정합, §4.4 L247 DONE/DEPRECATED 게이트 제외 노트, §7.3 L823 비핵심(MEDIUM 40+LOW 13) 추적 노트, §7.4 L880 'MEDIUM 70% 이상 STUB/REF', 01_high-priority/_index.md L137 T-03 비교 기준 인덱스+§6.1/부록 A.2로 교정. [제외 1건] 5-4-SECURITY-009(권한/감사로그/롤백 부재)는 디스크 실측으로 핵심 전

### 6-10_EXP-Modules-Detail (3건)

1. **[KEEP]** `docs\sot 2\6-10_EXP-Modules-Detail\CONFLICT_LOG.md`:L30(출처 B: B-5 Knowledge Distillation) vs L34(해결: B-5 'Few-Shot Manager') — 카탈로그.md L38·L137-147 실측 B-5=Few-Shot Manager(MMR) 일관 — B-5 슬롯의 공식 정식명·기능 범위를 'Few-Shot Manager'(MMR 기반 동적 예제 관리)로 채택할지 'Knowledge Distillation'(지식 증류)로 채택할지의 명명·범위 결정
   - 선택지: (a) Few-Shot Manager 정식명 유지(현행, CFL-610-002 S10-5 결정) (b) Knowledge Distillation으로 환원 + 카탈로그/B-시리즈 인덱스 되돌림 (c) CONFLICT_LOG 출처 B 행 재서술
   - 판정: (a) 유지 — CFL-610-002 해결란이 SOT2 카탈로그 정식명 채택을 명시적 결정(결정자 S10-5)으로 기록했고, sot2 카탈로그(본문 정본) 전체가 Few-Shot Manager로 일관(L38, L137-147, 01_b-series/_index.md L24). 출처 B 행은 충돌 등록 시점(S8-6)의 역사 기록으로 append-only 보존이 원칙이라 정본 모순 아님
2. **[KEEP]** `docs\sot 2\6-10_EXP-Modules-Detail\EXP_MODULES_DETAIL_카탈로그.md`:L346-358(§3.1 공통 인터페이스 예시: category+enabled만) vs AUTHORITY_CHAIN.md L32(LOCK-610-1 표준 필드: category, module_id, enabled, version, dependencies) — 공통 인터페이스 예시 코드에 표준 필드 5종 검증을 전부 명시할지, 정본(D2.0-01 §5.5) 참조로 위임하고 예시는 최소 발췌로 둘지의 문서화 상세 수준 결정
   - 선택지: (a) 현행 최소 예시 유지 + R-610-4로 정본 위임(현행) (b) 예시에 module_id/version/dependencies 필드·검증 로직 추가 (c) BaseModule 스키마 별도 절 신설
   - 판정: (a) 유지 — 정본 우선순위상 표준 필드 정본은 D2.0-01 §5.5(DESIGN 2.0)이고, 카탈로그 §3.2 R-610-4(L368)가 '표준 필드 준수→LOCK'을 이미 규범으로 강제하므로 예시 코드(`# 모듈 로직 구현 ...` 발췌 성격)의 필드 생략은 강제력 공백이 아닌 표현 선택. 정본 모순 없음
3. **[KEEP]** `docs\sot 2\6-10_EXP-Modules-Detail\EXP_MODULES_DETAIL_카탈로그.md`:L158(B-6: 100 에피소드 수렴·분산<0.1), L245(A-3: QoD 개선≥3%), L302(D-4: 페르소나 일관성≥90%·스타일 편차<10%) — LOCK 비보호 모듈별 테스트 임계값(에피소드 수, 분산 한계, QoD 개선율, 일관성/편차 비율)의 수치와 측정 산식 상세화 수준 결정
   - 선택지: (a) 현행 임계값 유지 + 산식은 구현 단계(I-14 Benchmark·S-4 Monitor 연동)에서 구체화(현행) (b) 임계값마다 산식·데이터셋·window·단위를 카탈로그에 즉시 추가 (c) 임계값 자체 재조정
   - 판정: (a) 유지 — 전형적 SLA 임계값 설계 선택으로, LOCK-610-8(D-6 90%, Part2 V3-P2 L4039 정본 고정)과 달리 어떤 정본(RULE 1.3/PLAN 3.0/DESIGN LOCK)도 다른 값·산식을 고정하지 않으며, 본 도메인은 SDV 예외(EXEMPTED, AUTHORITY_CHAIN L82-87) 카탈로그 형식이라 14-section 상세명세 수준의 산식 정의 의무가 없음. 값 자체도 합리적 범위

> notes: 앵커 3건과 재도출 3건 정확히 일치(짜맞춤 없음). 도출 경로: GPT 12건 중 9건이 mf_in 객관확정분 i0~i8과 1:1 대응(LOGIC-001→i0 LOCK 번호체계, LOGIC-003→i1 L1/L3 상태, LOGIC-007→i2 A-6 DEFER, OMISSION-010→i3 EVX-1 rollback, SECURITY-008→i4 A-7, LOGIC-005→i5 DAG, LOGIC-006→i6 Z3, LOGIC-012→i7 V3-004, SECURITY-009→i8 Thought Buffer)→중복 제외; 잔여 3건이 주관. 제외 상세: (1) CLC T8-012(EVX-1 샌드박스 미명세)=verify 'refuted'+실측 반박 — 카탈로그 L168 '샌드박스 실행'·L171 실행시간<30s·L172 vamos-experimental 격리 명시 → 오탐. (2) CLC/tight T8-013(A-6 Federated mTLS)=mf_in i2와 실질 중복(동일 근거 FEDERATED_AUTH_FAIL→mTLS vs DEFER-AT-004) + 세션5 교정으로 03_a-series/_index.md L57이 이미 '에러 처리 DEFER/테

### 6-13_Operations (3건)

1. **[KEEP]** `docs\sot 2\6-13_Operations\OPERATIONS_운영매뉴얼.md`:174 (QoD 이동평균 행 LOCK-ML-07 참조), 224 (R4); AUTHORITY_CHAIN.md:38-53 (레지스트리는 LOCK-OP-01~14만) — 타 도메인 소유 LOCK(LOCK-ML-07)을 소비할 때 로컬 AUTHORITY_CHAIN 레지스트리에 등재할지, cite-only 참조로만 둘지의 거버넌스 설계 선택
   - 선택지: (a) 현행: cite-only 참조, 레지스트리는 도메인 소유 14건 전용 / (b) AUTHORITY_CHAIN에 '외부 소비 LOCK' 섹션 신설 등재 / (c) 별도 dependency registry 파일
   - 판정: KEEP (a) — AUTHORITY_CHAIN 헤더가 'LOCK 항목 수: 14건(LOCK-OP-01~14)'으로 레지스트리를 도메인 소유 LOCK 전용으로 명시 스코프하고, R8(LOCK 재정의 금지)·VAMOS 교차도메인 cite-only 컨벤션과 부합한다. R4는 본 도메인 LOCK/DEFINED-HERE 출처 추적 의무이지 외부 LOCK 등재 의무가 아니므로 정본 위반 없음
2. **[KEEP]** `docs\sot 2\6-13_Operations\06_rollback\_index.md`:28-39 (V2 롤백 실행 명령); 10_sdar-fallback/_index.md:39-44 (AR-L2 config 수정); OPERATIONS_운영매뉴얼.md:193 (L3 Kill Switch 검토) — 고위험 운영 조치(롤백·config 수정·Kill Switch)에 승인 주체·2인 확인·감사 필드·실행 전 Gate를 어느 강도로 문서화할지의 권한 모델 설계 선택
   - 선택지: (a) 현행: §5.3 에스컬레이션 단계별 담당 주체(당번/운영팀/팀 리드+의사결정권자)만 정의, 조치별 승인 매트릭스 없음 / (b) P0/P1 조치별 승인자·2인 확인·감사 이벤트·롤백 전 백업 Gate 명시 / (c) 권한 모델 상세를 6-2 Security-Governance로 위임
   - 판정: KEEP (a) — Part2 §6.12.3/§6.12.5와 LOCK-OP-11/12 어디에도 승인 매트릭스·2인 룰 의무가 없고, 운영매뉴얼 §5.3(L188-201)이 단계별 담당·자동/수동·판단 주체를 이미 정의하며, §7 도메인 경계상 권한/접근제어 정책 정의는 6-2 소유다. 1인 운영 규모에서 승인 강도는 설계자 재량이며 정본 모순 없음
3. **[KEEP]** `docs\sot 2\6-13_Operations\12_cloud-library-failover\_index.md`:52 (월 1회 LLM API 페일오버 테스트: 'API 키 임시 무효화 → Ollama 전환 확인') — LLM API 페일오버 월간 드릴의 장애 주입 방법으로 운영 키 임시 무효화를 쓸지, 대체 주입 기법을 쓸지의 테스트 전략 선택
   - 선택지: (a) 현행: API 키 임시 무효화 (인증 실패 경로를 실제 end-to-end 검증) / (b) LLM_PROVIDER 강제 전환·feature flag 주입 / (c) 네트워크 차단·mock endpoint / (d) 테스트 전용 키
   - 판정: KEEP (a) — Part2 §6.12.11(L6104-6113)과 LOCK 어디에도 테스트 주입 방법이 규정되지 않은 설계 재량 영역이며, 키 무효화는 타임아웃 감지→이벤트 발행→Ollama 전환 전 경로를 실제로 검증하는 장점이 있다(키 재발급으로 가역). 복구 누락 리스크는 런북(failover_test_plan.md 예정)에 키 복원 체크 항목으로 흡수 가능하므로 정본 모순 없음

> notes: 도출 방법: GPT 16건(OP-001~016) 중 mf_in 객관결함 13건(i0~i12 = OP-001,002,003,004,005,006,007,008,009,010,011,013,016)을 매핑 제외, CL-C 2건(T6-009 LOCK-OP-14 600s 앵커 부재 주장 / T8-012 RTO V2 2h vs P1 1h)은 verify=refuted 오탐으로 제외(T8-012는 재해복구 RTO와 인시던트 복구목표가 별개 개념으로 반박됨), tight 0건. 잔여 3건이 원판정 주관 카운트 3과 정확히 일치 — 강제 짜맞춤 없음. 디스크 실측: 주관 3건 모두 현행 디스크에 그대로 존재(기해소 아님). 반면 세션5 기적용 확인분(객관, mf_in 소속): 12_cloud-library-failover L27 타임아웃 30초→5초(OP-009 기해소), L35 cite-only 정본 이벤트(OP-016 기해소), L43-46 PG 쓰기 거부 503(OP-010 기해소), 06_rollback L32-34 PREVIOUS_IMAGE_TAG 반영(OP-007 기해소), 운영매뉴얼 L276 V-5 '12개 도메인'(OP-013 기해소) — 이들로 인해 OP-

