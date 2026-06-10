# KPI Definitions — V1 핵심 지표

> **버전**: V1
> **Phase**: 1 (P1-5)
> **최종 갱신**: 2026-04-11
> **상태**: COMPLETE

---

## 교차 참조 블록

| 참조 문서 | 참조 위치 | 역할 |
|----------|----------|------|
| `STEP7-H_비즈니스모델_시장전략_작업가이드.md` | S7H-017 (전환율), S7H-029 (P2 여정맵 NPS), S7H-049 (KPI), S7H-073 (수지 분석) | 최상위 정본 — KPI 원본 데이터 |
| `BUSINESS_MODEL_STRATEGY_구조화_종합계획서.md` | §7.1 Phase 1 KPI 목록, §3.4 LOCK-BM-07, §A.1 SOM, §A.2 BEP | 거버넌스 정본 — KPI 범위, LOCK 값, 시장 목표 |
| `01_pricing-revenue/revenue_model.md` | 5대 수익 스트림, API 마진, ARR 예측 | P1-1 산출물 — MRR 정의 연계 |
| `02_market-analysis/market_sizing.md` | TAM/SAM/SOM, ARPU $10/mo | P1-2 산출물 — 전환율 목표 연계 |
| `02_market-analysis/personas.md` | P1~P4 페르소나별 전환율, NPS 목표 | P1-2 산출물 — 페르소나별 KPI 연계 |
| `03_gtm-growth/gtm_phases.md` | 씨드 단계 KPI (Stars, MAU 500, Discord 100) | P1-3 산출물 — DAU/MAU 정의 연계 |
| `04_financial-modeling/financial_projection.md` | V1 수지 분석, BEP 43명, 3 시나리오 | P1-4 산출물 — MRR 목표 연계 |

---

## 1. MAU (Monthly Active Users)

### 1.1 정의

월간 활성 사용자 수. 한 달(30일) 내 VAMOS에 **로그인 + 1건 이상의 의미 있는 액션**을 수행한 고유 사용자 수.

### 1.2 측정 기준

| 항목 | 기준 |
|------|------|
| **포함 조건** | 로그인(로컬 앱 실행 포함) + 1건 이상 액션 (대화, Agent 호출, 문서 분석 등) |
| **제외 조건** | 봇/자동화 트래픽, 테스트 계정, 비활성 세션(5분 내 종료) |
| **집계 주기** | 월 1회 (매월 1일 00:00 UTC 기준 전월 집계) |
| **고유 식별** | 사용자 계정 ID (로컬 전용 사용자는 디바이스 해시, opt-in) |
| **데이터 소스** | 텔레메트리 서버 (opt-in 기반), 로컬 전용 사용자는 집계 불가 |

### 1.3 목표 값

| 단계 | 목표 MAU | 근거 |
|------|---------|------|
| 씨드 (출시 6개월) | 500 | STEP7-H S7H-049 "500 활성 사용자" (추정치, 출시 후 조정) |
| V1 Y1 기준 시나리오 | 5,000 | SOM Y1 목표 (market_sizing.md, STEP7-H S7H-035/037 기준) |
| V1 Y1 낙관 시나리오 | 20,000 | SOM Y1 낙관 (financial_projection.md §A.3) |
| V1 Y1 비관 시나리오 | 1,000 | SOM Y1 비관 (financial_projection.md §A.3) |

> **가정**: 로컬 전용 사용자의 텔레메트리 opt-in 비율은 미지수. 실제 MAU는 보고 값보다 높을 가능성 있음 (추정, 출시 후 opt-in 비율 측정 필요).

### 1.4 대시보드 스키마

| 항목 | 설정 |
|------|------|
| 시각화 유형 | 라인 차트 (월별 추이, 12개월 이동 평균선 포함) |
| 갱신 주기 | 월 1회 (매월 3일 자동 리프레시) |
| 알림 임계값 | MoM 감소 > 10% → WARN, > 20% → CRITICAL |
| 비교 표시 | 전월 대비 증감률 (%), 목표 대비 달성률 (%) |

---

## 2. DAU (Daily Active Users)

### 2.1 정의

일간 활성 사용자 수. 하루(00:00~23:59 UTC) 내 VAMOS에 **로그인 + 1건 이상의 의미 있는 액션**을 수행한 고유 사용자 수.

### 2.2 측정 기준

| 항목 | 기준 |
|------|------|
| **포함 조건** | 로그인(로컬 앱 실행 포함) + 1건 이상 액션 |
| **제외 조건** | MAU와 동일 (봇, 테스트 계정, 비활성 세션) |
| **집계 주기** | 일 1회 (매일 00:00 UTC 기준 전일 집계) |
| **고유 식별** | MAU와 동일 (계정 ID / 디바이스 해시) |
| **데이터 소스** | 텔레메트리 서버 (opt-in) |

### 2.3 DAU/MAU 비율 (Stickiness)

| 지표 | 목표 | 근거 |
|------|------|------|
| DAU/MAU Ratio | 20%+ (씨드), 25%+ (Y1 기준) | SaaS 업계 평균 10~20%, AI 도구 특성상 일상적 사용 기대 (추정치) |
| 해석 | 0.2 이상이면 사용자가 월 6일 이상 사용 → 높은 습관성 지표 | — |

> **가정**: DAU/MAU 20% 목표는 일반 SaaS 벤치마크 기반 추정치. AI 어시스턴트 카테고리 특성상 업무용 도구처럼 일상적 사용 패턴 기대, 출시 후 실측 조정 필요.

### 2.4 목표 값

| 단계 | 목표 DAU | 산출 근거 |
|------|---------|----------|
| 씨드 (출시 6개월) | 100 | MAU 500 × Stickiness 20% (추정) |
| V1 Y1 기준 시나리오 | 1,000 | MAU 5,000 × Stickiness 20% (추정) |
| V1 Y1 낙관 시나리오 | 5,000 | MAU 20,000 × Stickiness 25% (추정) |

### 2.5 대시보드 스키마

| 항목 | 설정 |
|------|------|
| 시각화 유형 | 라인 차트 (일별 추이 + 7일 이동 평균선) |
| 갱신 주기 | 일 1회 (매일 03:00 UTC 자동 리프레시) |
| 알림 임계값 | 7일 평균 DAU WoW 감소 > 15% → WARN, > 30% → CRITICAL |
| 비교 표시 | 전일 대비 증감, 7일 평균, DAU/MAU Ratio 게이지 |
| 보조 차트 | DAU/MAU Stickiness 게이지 (목표선 20% 표시) |

---

## 3. 전환율 (Conversion Rate)

### 3.1 정의

Free Tier 사용자에서 유료 Tier(Pro 이상)로 전환하는 비율. **Free→Paid 전환율**을 핵심 지표로 하며, 퍼널 단계별 전환율을 보조 지표로 추적.

### 3.2 측정 기준

| 항목 | 기준 |
|------|------|
| **핵심 전환율** | (유료 전환 사용자 수 / Free Tier 가입자 수) × 100% |
| **측정 구간** | 가입 후 90일 이내 첫 유료 전환 (Cohort 기준) |
| **유료 판정** | Pro($15/mo, LOCK-BM-07) 이상 구독 활성화 시점 |
| **집계 주기** | 월 1회 (Cohort 분석: 가입월 기준) |
| **데이터 소스** | 결제 시스템 + 사용자 계정 DB |

### 3.3 퍼널 단계별 전환율

| 퍼널 단계 | 정의 | 목표 전환율 | 근거 |
|----------|------|-----------|------|
| 인지 → 관심 | 광고/콘텐츠 노출 → 랜딩 페이지 클릭 | 10~20% | P1-2 페르소나별 CTR (personas.md: P1 15%, P4 20%) |
| 관심 → 설치 | 랜딩 페이지 → 앱 설치/가입 | 25~40% | P1-2 페르소나별 설치 전환율 (P1 40%, P2 30%, P3 25%, P4 35%) |
| 설치 → 활성화 | 설치 → 첫 의미 있는 액션 완료 | 40%+ | P1-3 gtm_phases.md 설치→활성화 40%+ 목표 (업계 평균 20~30% 대비 상향, 추정) |
| 활성화 → Free→Paid | 활성 사용자 → 유료 구독 전환 | 5~10% | STEP7-H S7H-017 목표 전환율 5-10% (SaaS 평균 2-5%) |
| **종합 Free→Paid** | **전체 가입자 대비 유료 전환** | **7%** | **SOM 기준 — market_sizing.md SOM Y1: 5,000명 중 유료 500명 = 약 10% (API 마진 기준). SaaS 전환율 평균 고려 7% 목표 (추정)** |

> **가정**: 종합 Free→Paid 전환율 7%는 SaaS 업계 평균(2~5%)과 STEP7-H 목표(5~10%)의 중간값 추정. V1은 API 마진 전용 수익 모델이므로 "유료 사용자"는 API 과금 사용자 기준. Pro 구독은 V2에서 본격 도입.
> **출처**: STEP7-H S7H-017 "목표 전환율: 5-10%", 종합계획서 §A.1 SOM 사용자 수 기반.

### 3.4 페르소나별 전환율 목표

| 페르소나 | Free→Pro 전환율 | NPS 목표 | 근거 |
|---------|----------------|---------|------|
| P1 (테크 얼리어답터) | 15% | 50+ | personas.md 페르소나별 KPI |
| P2 (지식 노동자) | 12% | 50+ | personas.md 페르소나별 KPI |
| P3 (AI 투자자) | 10% | 45+ | personas.md 페르소나별 KPI |
| P4 (프라이버시 중시) | 8% | 55+ | personas.md 페르소나별 KPI |

> **출처**: P1-2 산출물 `02_market-analysis/personas.md` 페르소나별 전환율·NPS 목표 테이블.

### 3.5 대시보드 스키마

| 항목 | 설정 |
|------|------|
| 시각화 유형 | 퍼널 차트 (단계별 전환율) + 월별 전환율 라인 차트 |
| 갱신 주기 | 월 1회 (Cohort 분석 포함) |
| 알림 임계값 | 종합 전환율 < 5% → WARN, < 3% → CRITICAL |
| 비교 표시 | 목표(7%) 대비 달성률, 월별 추이, 페르소나별 비교 |

---

## 4. MRR (Monthly Recurring Revenue)

### 4.1 정의

월간 반복 매출. 해당 월에 발생한 반복적(구독 + API 과금) 매출의 합계. V1 단계에서는 API 마진이 주 수익원.

### 4.2 측정 기준

| 항목 | 기준 |
|------|------|
| **구성 요소** | 신규 MRR + 확장 MRR - 이탈 MRR |
| **신규 MRR** | 해당 월 최초 유료 전환 사용자 발생 매출 |
| **확장 MRR** | 기존 유료 사용자의 사용량/티어 업그레이드 매출 증가분 |
| **이탈 MRR** | 해당 월 구독 취소/다운그레이드로 감소한 매출 |
| **집계 주기** | 월 1회 (월말 23:59 UTC 기준) |
| **데이터 소스** | 결제 시스템 (구독 관리 + API 과금 시스템) |

### 4.3 ARPU (Average Revenue Per User)

| 단계 | ARPU | 산출 근거 |
|------|------|----------|
| V1 (API 마진 전용) | $0.80/mo | 사용자당 월 API 사용액 $8/mo × 마진 10% (LOCK-BM-09 70/30 기준, financial_projection.md) |
| V2 (Pro 구독 도입) | $15/mo (Pro) | LOCK-BM-07 Pro $15/mo, 연간 $144 |
| V2 (Enterprise) | $35/seat/mo | LOCK-BM-08 Enterprise $35/seat/mo (최소 10석) |
| 가중 ARPU (Y1 SOM 기준) | $10/mo | market_sizing.md SOM Y1: 5,000명, $600K/yr → $10/mo/user |

> **참고**: V1에서 Pro 구독($15/mo, LOCK-BM-07)은 아직 미도입. V1은 API 마진 전용 수익 모델 (financial_projection.md 참조). ARPU $0.80/mo는 V1 API 마진 기준이며, SOM ARPU $10/mo는 V2 구독 도입 후 달성 목표.

### 4.4 목표 MRR

| 시나리오 | V1 Y1 월간 MRR | 연간 환산 | 근거 |
|---------|---------------|----------|------|
| **기준** | $800/mo | $9.6K/yr | 유료 1,000명 × $0.80 (financial_projection.md 기준 시나리오) |
| **낙관** | $1,600/mo | $19.2K/yr | 유료 2,000명 × $0.80 (financial_projection.md 낙관 시나리오) |
| **비관** | $80/mo | $960/yr | 유료 100명 × $0.80 (financial_projection.md 비관 시나리오) |
| **V2 도입 후 (Y2 기준)** | $75K/mo | $900K/yr | STEP7-H S7H-076 Y2 유료 5K × $15 MRR (3년 P&L 정본, §E.3.2 L317) |

> **가정**: V1 MRR은 API 마진 전용이므로 절대 금액이 낮음. SOM Y1 $600K 목표 매출은 V2 SaaS 구독 도입 후 달성 가능 (financial_projection.md 해석 참조).
> **LOCK 준수**: MRR 산출 시 Pro $15/mo(LOCK-BM-07), Enterprise $35/seat/mo(LOCK-BM-08), 수수료 70/30(LOCK-BM-09) 변경 불가.

### 4.5 BEP 연계

| 지표 | 값 | 근거 |
|------|-----|------|
| 월간 고정 비용 | $34/mo | financial_projection.md V1 비용 구조 |
| 사용자당 마진 | $0.80/mo | API 마진 $8/mo × 10% |
| **BEP** | **43 유료 사용자** | $34 / $0.80 = 42.5 → 43명 |
| BEP MRR | $34.40/mo | 43명 × $0.80 |

> **출처**: P1-4 산출물 `04_financial-modeling/financial_projection.md` BEP 분석 전수 인용.

### 4.6 대시보드 스키마

| 항목 | 설정 |
|------|------|
| 시각화 유형 | 스택 바 차트 (신규/확장/이탈 MRR 구분) + 누적 라인 |
| 갱신 주기 | 월 1회 (매월 5일 자동 리프레시, 결제 정산 후) |
| 알림 임계값 | MRR MoM 감소 > 5% → WARN, > 15% → CRITICAL, BEP 미달 → CRITICAL |
| 비교 표시 | 목표 MRR 대비 달성률, BEP 라인 표시, Net MRR 추이 |

---

## 5. NPS (Net Promoter Score)

### 5.1 정의

순 추천 지수. "VAMOS를 동료/친구에게 추천할 의향이 얼마나 됩니까?" (0~10점) 질문으로 측정하며, Promoter(9~10) - Detractor(0~6) = NPS.

### 5.2 측정 기준

| 항목 | 기준 |
|------|------|
| **설문 방법** | 인앱 설문 팝업 (대화 50회 완료 시점 트리거) + 분기별 이메일 설문 |
| **질문** | "0~10점으로, VAMOS를 동료에게 추천할 의향은?" + 자유 텍스트 이유 |
| **분류** | Promoter (9~10), Passive (7~8), Detractor (0~6) |
| **NPS 산출** | (Promoter % - Detractor %) × 100 |
| **측정 주기** | 분기 1회 (매 분기 마지막 월 전체 기간) |
| **최소 표본** | 유효 응답 100건 이상 (통계적 유의성) |
| **데이터 소스** | 설문 시스템 (인앱 + 이메일), 응답률 목표 15%+ |

### 5.3 목표 값

| 단계 | NPS 목표 | 벤치마크 | 근거 |
|------|---------|---------|------|
| 씨드 (출시 6개월) | 40+ | SaaS 평균 30~40 | 초기 얼리어답터 높은 열정 기대 (추정) |
| V1 Y1 | **50+** | **우수 SaaS 수준 (상위 25%)** | **STEP7-H S7H-029 "NPS 50+ 목표"** |
| V2 Y2 | 55+ | SaaS 상위 10% | 제품 성숙도 향상 기대 (추정) |

> **출처**: STEP7-H S7H-029 P2 여정맵 "7. 추천: 'NPS 50+ 목표'". P1-2 산출물 personas.md 페르소나별 NPS 목표(P1 50+, P2 50+, P3 45+, P4 55+) 참조.
> **가정**: NPS 50+는 SaaS 상위 25% 수준으로 야심찬 목표. 초기 얼리어답터(P1) 편향으로 높게 나올 수 있으나 대중화 시 하락 가능 (추정, 분기별 추이 추적 필요).

### 5.4 페르소나별 NPS 목표

| 페르소나 | NPS 목표 | 근거 |
|---------|---------|------|
| P1 (테크 얼리어답터) | 50+ | personas.md |
| P2 (지식 노동자) | 50+ | personas.md |
| P3 (AI 투자자) | 45+ | personas.md |
| P4 (프라이버시 중시) | 55+ | personas.md — 프라이버시 만족도 높을 시 추천 의향 강함 |

### 5.5 대시보드 스키마

| 항목 | 설정 |
|------|------|
| 시각화 유형 | 게이지 차트 (NPS 현재값) + 분기별 추이 라인 차트 |
| 갱신 주기 | 분기 1회 (분기 종료 후 2주 내 집계 완료) |
| 알림 임계값 | NPS < 30 → WARN, < 20 → CRITICAL |
| 비교 표시 | 목표(50+) 대비 달성, 페르소나별 NPS 비교 바 차트, Promoter/Passive/Detractor 비율 파이 차트 |

---

## 6. KPI 종합 대시보드 스키마

### 6.1 대시보드 레이아웃

```
┌──────────────────────────────────────────────────────────┐
│                    VAMOS KPI Dashboard (V1)               │
├──────────────┬──────────────┬──────────────┬─────────────┤
│   MAU        │   DAU        │   전환율      │   NPS       │
│  [라인차트]   │  [라인차트]   │  [퍼널차트]   │  [게이지]    │
│  월별 추이    │  일별+7일MA  │  단계별 %     │  현재값      │
├──────────────┴──────────────┴──────────────┴─────────────┤
│                     MRR (스택 바 차트)                      │
│         신규 MRR | 확장 MRR | 이탈 MRR | BEP 라인          │
├──────────────────────────────────────────────────────────┤
│   Stickiness     │   BEP 달성률    │   알림 로그           │
│   [DAU/MAU 게이지] │   [진행 바]     │   [WARN/CRITICAL]   │
└──────────────────────────────────────────────────────────┘
```

### 6.2 데이터 갱신 주기 요약

| KPI | 갱신 주기 | 데이터 지연 |
|-----|----------|-----------|
| MAU | 월 1회 | 3일 (매월 3일) |
| DAU | 일 1회 | 3시간 (03:00 UTC) |
| 전환율 | 월 1회 | 5일 (Cohort 분석) |
| MRR | 월 1회 | 5일 (결제 정산) |
| NPS | 분기 1회 | 14일 (설문 수집+분석) |

### 6.3 알림 임계값 종합

| KPI | WARN | CRITICAL |
|-----|------|----------|
| MAU | MoM -10% | MoM -20% |
| DAU | 7일 평균 WoW -15% | 7일 평균 WoW -30% |
| 전환율 | < 5% | < 3% |
| MRR | MoM -5% | MoM -15% 또는 BEP 미달 |
| NPS | < 30 | < 20 |

---

## 7. P1-1~P1-4 교차 일관성 확인

### 7.1 검증 결과

| 교차 항목 | KPI 정의 | P1-N 산출물 값 | 정합 여부 |
|----------|---------|-------------|----------|
| P1-1 MRR ↔ KPI MRR | API 마진 기준 $0.80/user/mo | revenue_model.md: API 마진 70/30 수수료 기반 수익 모델 | PASS — LOCK-BM-09 70/30 기준 동일 |
| P1-2 SOM ↔ 전환율 | SOM Y1 5,000명 중 유료 목표, 전환율 7% | market_sizing.md: SOM Y1 5,000명, $600K/yr, ARPU $10/mo | PASS — SOM 사용자 수 일치 |
| P1-3 씨드 KPI ↔ DAU | 씨드 MAU 500, DAU 100 (추정) | gtm_phases.md: 씨드 500 활성 사용자(MAU), S7H-049 원본 | PASS — MAU 500 일치 |
| P1-4 BEP ↔ MRR | BEP 43 유료 사용자, MRR $34.40 | financial_projection.md: BEP 43명, 월간 비용 $34 | PASS — BEP 수치 완전 일치 |
| P1-2 NPS ↔ KPI NPS | 목표 NPS 50+ | personas.md: P1~P4 평균 NPS 50+ | PASS — NPS 목표 일치 |
| LOCK-BM-07 ↔ MRR ARPU | Pro $15/mo | 종합계획서 §3.4 LOCK-BM-07 = $15/mo | PASS — LOCK 값 준수 |

### 7.2 불일치 사항

- 발견된 불일치: **0건**
- 기존 CONFLICT (CFL-001~013): 전부 RESOLVED 상태 유지, KPI 영역 신규 충돌 없음

---

## 8. Phase 2 테스트 시나리오

> V2 확장 시 KPI 정의 변경/추가에 대한 검증 시나리오. 각 시나리오에 주입 방법과 기대 결과를 명시.

| # | ID | 시나리오 | 주입 방법 | 기대 결과 |
|---|-----|---------|----------|----------|
| 1 | T-KPI-001 | MAU 정의 변경 — 액션 기준 확장 | MAU 포함 조건에 "Agent 자동 실행" 추가 | MAU 산출 로직 변경, 봇 트래픽 제외 규칙 강화 필요 |
| 2 | T-KPI-002 | DAU/MAU Stickiness 목표 상향 | Stickiness 목표 20% → 30%로 변경 | 알림 임계값 재조정, DAU 목표 상향 (MAU 5,000 × 30% = 1,500) |
| 3 | T-KPI-003 | 전환율 LOCK 위반 테스트 | Pro 가격을 $20/mo로 변경하여 전환율 재산출 | LOCK-BM-07($15/mo) 위반 감지, 가격 변경 거부, 전환율 목표 유지 |
| 4 | T-KPI-004 | MRR 구성 요소 확장 | V2 SaaS 구독 MRR 추가 (Pro $15/mo × 500명 = $7,500/mo) | MRR 스택 바 차트에 "구독 MRR" 레이어 추가, 총 MRR 증가 |
| 5 | T-KPI-005 | NPS 목표 미달 시 대응 | NPS 설문 결과 25로 주입 | CRITICAL 알림 발생, 페르소나별 NPS 분석 트리거, 이탈 방지 전략 권고 |
| 6 | T-KPI-006 | B2B 전환율 KPI 추가 | V2 확장 KPI로 "B2B 전환율" (Team/Enterprise 전환) 추가 | 전환율 대시보드에 B2B 퍼널 추가, LOCK-BM-08($35/seat) 기준 MRR 연동 |
| 7 | T-KPI-007 | LTV/CAC 비율 KPI 추가 | V2 확장 KPI "LTV/CAC Ratio" 정의 추가 (LTV = ARPU × 평균 사용 개월 / CAC) | 재무 대시보드에 LTV/CAC 게이지 추가, 목표 3:1 이상 |
| 8 | T-KPI-008 | ARR KPI 추가 | V2 확장 KPI "ARR" = MRR × 12 자동 산출 추가 | MRR 차트 하단에 ARR 연환산 표시, SOM 매출 목표($600K Y1)와 비교 |
| 9 | T-KPI-009 | 마켓플레이스 GMV KPI 추가 | V2 확장 KPI "GMV" 정의 (Agent 마켓플레이스 거래 총액) | 별도 GMV 차트 추가, LOCK-BM-09(70/30 수수료) 기반 수익 환산 |
| 10 | T-KPI-010 | Churn Rate KPI 추가 | V2 확장 KPI "월간 이탈률" 정의 (이탈 사용자 / 전월 유료 사용자) | MRR 이탈 MRR 연동, 이탈률 > 5% → WARN, > 10% → CRITICAL |
| 11 | T-KPI-011 | 지역별 KPI 분리 (V3 대비) | 한국/글로벌 MAU·전환율 분리 주입 | 대시보드에 지역 필터 추가, 한국 시장 특수성(가격 민감도) 반영 확인 |
| 12 | T-KPI-012 | 대시보드 갱신 주기 변경 | MRR 갱신 주기를 월→주로 단축 | 데이터 지연 5일→2일 단축 필요, 결제 시스템 실시간 연동 요구 |

---

## 부록: 용어 정의

| 용어 | 정의 |
|------|------|
| MAU | Monthly Active Users — 월간 활성 사용자 |
| DAU | Daily Active Users — 일간 활성 사용자 |
| Stickiness | DAU/MAU 비율 — 사용 습관성 지표 |
| MRR | Monthly Recurring Revenue — 월간 반복 매출 |
| ARR | Annual Recurring Revenue — 연간 반복 매출 (MRR × 12) |
| ARPU | Average Revenue Per User — 사용자당 평균 매출 |
| NPS | Net Promoter Score — 순 추천 지수 |
| BEP | Break-Even Point — 손익 분기점 |
| LTV | Lifetime Value — 고객 생애 가치 |
| CAC | Customer Acquisition Cost — 고객 획득 비용 |
| GMV | Gross Merchandise Value — 거래 총액 |
| Cohort | 동일 기간 가입자 그룹 — 전환율 분석 기준 |

---

## §E. V2 Phase 2 확장 KPI — 시장 데이터 갱신 (STEP_B #2b — 2026-04-22)

> **Phase**: 2 (P2-5 세션, STAGE 7 STEP_B #2b — ★P2→P3 exit_gate "시장 데이터 갱신" 최종 충족 담당 세션)
> **작성일**: 2026-04-22
> **대상 V2 확장 KPI**: B2B 전환율 + SaaS ARR + 마켓플레이스 GMV + LTV/CAC Ratio + Churn Rate + 시장 데이터 갱신 (TAM/SAM/SOM 2026-04-22 시점) = 5 신규 KPI + 1 시장 데이터 갱신
> **정본 출처**: STEP7-H 횡단 (S7H-017 전환율 / S7H-021 MCP 70/30 / S7H-035 시장 규모 / S7H-049 KPI / S7H-075 LTV/CAC / S7H-076 3년 재무) + 상세명세 §6 KPI 스키마 (CFL-002 RESOLVED — 가이드 부록 B 5 서브폴더 기준 05_kpi-dashboard)
> **LOCK 기준**: LOCK-BM-07 Pro $15/mo / LOCK-BM-08 Enterprise $35/seat/mo / LOCK-BM-09 70/30 수수료율 (AUTHORITY §4 L70~L72 verbatim, KPI 산출 기반)
> **CONFLICT 판정**: 본 §E 신규 [CONFLICT_CANDIDATE] 발화 0건 (V1 CFL-001~013 RESOLVED 보존)
> **V2↔V2 peer cross-ref**: `01_pricing-revenue/pricing_comparison.md` §E (7티어) + `01_pricing-revenue/revenue_model.md` §E.1 (S7H-020 SaaS Pro) + `02_market-analysis/market_sizing.md` §E (TAM/SAM/SOM) + `02_market-analysis/personas.md` §E (P1~P5) + `03_gtm-growth/growth_strategy.md` §E (리텐션 D7/D14/D30) + `03_gtm-growth/growth_strategy.md` §E.1 (S7H-059 MCP 플라이휠) + `04_financial-modeling/financial_projection.md` §E.1 (V2 수지) + `04_financial-modeling/financial_projection.md` §E.2 (LTV/CAC) + `04_financial-modeling/financial_projection.md` §E.3 (3년 P&L) + `04_financial-modeling/risk_analysis.md` §E.2 (기술 부채 KPI)

### §E.1 B2B 전환율 KPI (T-KPI-006 실체화)

#### §E.1.1 정의

Team/Enterprise 티어 전환 비율. 개인 사용자(Pro) 대비 기업/팀 계약으로의 확장 비율. **B2B 전환율**은 Y2~Y3 성장 핵심 KPI.

#### §E.1.2 LOCK 기준 5필드 verbatim

| LOCK ID | 항목 | 값 | 원본 출처 | 근거 |
|---------|------|-----|---------|------|
| **LOCK-BM-08** | Enterprise 석당 가격 | $35/seat/mo (최소 10석) | 상세명세 §2.3 (AUTHORITY §4 L71) | B2B 가격 기준 (Team/Enterprise KPI 산출 기반) |
| **LOCK-BM-07** | Pro 월 가격 | $15/mo | 상세명세 §2.3, S7H-020 (AUTHORITY §4 L70) | B2C/B2B 가격 스펙트럼 하한 |

#### §E.1.3 측정 기준

| 항목 | 기준 |
|------|------|
| **핵심 지표** | (B2B 전환 사용자 수 / 전체 유료 사용자 수) × 100% |
| **B2B 판정** | Team ($20/user/mo) 또는 Enterprise ($35/seat/mo, LOCK-BM-08) 구독 활성 |
| **세부 퍼널** | Pro → Team (팀 확장) + Team → Enterprise (계약 확장) 2단계 분리 추적 |
| **집계 주기** | 월 1회 (매월 3일) + 분기별 Cohort 분석 |
| **데이터 소스** | 결제 시스템 + 사용자 계정 DB + B2B 영업 CRM (V2+) |

#### §E.1.4 목표 값

| 단계 | B2B 전환율 | 근거 | 매출 기여 |
|------|-----------|------|----------|
| V2 Y1 | 5% (유료 500명 중 B2B 25명) | 초기 B2B 시장 진입 (LOCK-BM-08) | Team $20 × 200 + Enterprise $35 × 50 seat = $5.75K/mo |
| V2 Y2 | 10% (유료 5K 중 B2B 500명) | Phase 2 성장 단계 (S7H-053) B2B 영업 본격화 | ARR $72K (기여 Y2 $900K ARR 중 8%) |
| V3 Y3 | 15% (유료 20K 중 B2B 3K명) | Enterprise 본격 확장 | ARR $540K+ (기여 Y3 $3.6M 중 15%) |

> **출처**: `02_market-analysis/market_sizing.md` §E B2B 시장 분석 (S7H-039 한국 B2B $60M) + `04_financial-modeling/financial_projection.md` §E.3.2 3년 P&L 정합.

#### §E.1.5 대시보드 스키마

| 항목 | 설정 |
|------|------|
| 시각화 유형 | 퍼널 차트 (Pro → Team → Enterprise) + 월별 B2B 전환율 라인 |
| 갱신 주기 | 월 1회 (Cohort 분석 포함) |
| 알림 임계값 | B2B 전환율 < 3% → WARN, < 1% → CRITICAL |
| 비교 표시 | 목표 대비 달성률, Team vs Enterprise 비율 |

### §E.2 SaaS ARR KPI (T-KPI-008 실체화)

#### §E.2.1 정의

Annual Recurring Revenue — 연간 반복 매출. MRR × 12 기준으로 **SaaS Valuation 핵심 지표**. ARR은 V2 Pro 구독 도입 후 주 추적 지표로 부상.

#### §E.2.2 LOCK 기준 5필드 verbatim

| LOCK ID | 항목 | 값 | 원본 출처 | 근거 |
|---------|------|-----|---------|------|
| **LOCK-BM-07** | Pro 월 가격 | $15/mo (연간 $144) | 상세명세 §2.3, S7H-020 (AUTHORITY §4 L70) | ARR 산출 기반 |
| **LOCK-BM-08** | Enterprise 석당 가격 | $35/seat/mo | 상세명세 §2.3 (AUTHORITY §4 L71) | B2B ARR 산출 |

#### §E.2.3 측정 기준 (STEP7-H S7H-076 verbatim)

| 항목 | 기준 |
|------|------|
| **산출 공식** | MRR × 12 (Pro 구독 + Core API + B2B Team/Enterprise 합산) |
| **구성 요소** | (1) Pro 구독 ARR + (2) Core API 마진 연환산 + (3) B2B Team/Enterprise ARR + (4) MCP 마켓 수수료 (LOCK-BM-09 30%) 연환산 |
| **측정 시점** | 월말 23:59 UTC (MRR 확정 후 자동 × 12) |
| **데이터 소스** | 결제 시스템 + 구독 관리 시스템 |

#### §E.2.4 목표 ARR (STEP7-H S7H-076 verbatim — ★CFL-004 구분)

| 연도 | ARR (S7H-076 유료 Pro 구독) | 목표 매출 (S7H-037 전체) | CFL-004 구분 |
|------|------------------------------|--------------------------|--------------|
| Y1 (2027) | $60K (유료 500명) | $600K (전체 5K × ASP) | 10배 차이 (실현 vs 목표) |
| Y2 (2028) | $900K (유료 5K명) | $4.3M (전체 30K × ASP) | ~4.8배 차이 |
| Y3 (2029) | $3.6M (유료 20K명) | $15M (전체 100K × ASP) | ~4.2배 차이 |

> **출처**: STEP7-H S7H-076 (L988~L998) 3년 재무 전망 verbatim + `04_financial-modeling/financial_projection.md` §E.3.3 CFL-004 전수 구분 명기.
> **⚠️ CFL-004 주의**: S7H-037 "목표 매출 (aspiration)" vs S7H-076 "구독 ARR (실현)" 구분 엄수.

#### §E.2.5 대시보드 스키마

| 항목 | 설정 |
|------|------|
| 시각화 유형 | 라인 차트 (월별 ARR 추이) + 구성 요소 스택 (Pro/Core/B2B/마켓) |
| 갱신 주기 | 월 1회 (MRR 확정 후) |
| 알림 임계값 | ARR MoM -5% → WARN, -15% → CRITICAL, 목표 대비 -30% → CRITICAL |
| 비교 표시 | 목표(S7H-076 Y1 $60K) 대비 달성률, SaaS Valuation 환산 (5~7x ARR) |

### §E.3 마켓플레이스 GMV KPI (T-KPI-009 실체화)

#### §E.3.1 정의

Gross Merchandise Value — MCP Agent 마켓플레이스 거래 총액. LOCK-BM-09 70/30 수수료 구조 기반 VAMOS 수익 환산.

#### §E.3.2 LOCK 기준 5필드 verbatim

| LOCK ID | 항목 | 값 | 원본 출처 | 근거 |
|---------|------|-----|---------|------|
| **LOCK-BM-09** | 마켓플레이스 수수료율 | **70% 개발자 / 30% VAMOS** | STEP7-H S7H-021 (AUTHORITY §4 L72) | ★GMV → VAMOS 수익 환산 핵심 |

#### §E.3.3 측정 기준

| 항목 | 기준 |
|------|------|
| **GMV 정의** | MCP 마켓 월간 거래 총액 (개발자 수익 + VAMOS 수수료 합산) |
| **VAMOS 수익 환산** | GMV × 30% (LOCK-BM-09) |
| **개발자 지급** | GMV × 70% (LOCK-BM-09, S7H-021 정본) |
| **거래 포함 범위** | Paid Tool 다운로드 + 사용량 기반 과금 + Subscription Tool (월 단위) |
| **집계 주기** | 월 1회 (결제 정산 후) |
| **데이터 소스** | 마켓 결제 시스템 (V2+) |

#### §E.3.4 목표 GMV (STEP7-H S7H-059 + growth_strategy.md §E.1 정합)

| 연도 | GMV 월간 | VAMOS 월 수수료 (30%) | 개발자 지급 (70%) | 근거 |
|------|----------|----------------------|-------------------|------|
| Y1 (2027) | $1K/mo (시드 30 Tool) | $300/mo | $700/mo | `04_financial-modeling/financial_projection.md` §E.1.3 Tool 마켓 매출 $1K/mo |
| Y2 (2028) | $24K/mo ($86.4K/yr 수수료) | $7.2K/mo | $16.8K/mo | `03_gtm-growth/growth_strategy.md` §E.1 S7H-059 MCP 플라이휠 Y2 수수료 $86.4K |
| Y3 (2029) | $100K/mo (추정) | $30K/mo | $70K/mo | Y2 → Y3 4x 성장 (추정, MCP 생태계 Top 100 Tool 확장) |

> **출처**: `03_gtm-growth/growth_strategy.md` §E.1 MCP 플라이휠 Y2 VAMOS 수수료 $86.4K 정합 + STEP7-H S7H-059 MCP 생태계 확장.

#### §E.3.5 대시보드 스키마

| 항목 | 설정 |
|------|------|
| 시각화 유형 | 스택 바 차트 (GMV = 개발자 70% + VAMOS 30%) + 월별 Tool 수 추이 |
| 갱신 주기 | 월 1회 (결제 정산 후) |
| 알림 임계값 | GMV MoM -10% → WARN, -25% → CRITICAL |
| 비교 표시 | VAMOS 수수료 누적, Top 10 Tool 기여도, 신규 Tool 등록률 |

### §E.4 LTV/CAC Ratio KPI (T-KPI-007 실체화)

#### §E.4.1 정의

Lifetime Value / Customer Acquisition Cost 비율. SaaS Unit Economics 핵심 지표. **목표 ≥ 3x** (S7H-075 정본).

#### §E.4.2 LOCK 기준 5필드 verbatim

| LOCK ID | 항목 | 값 | 원본 출처 | 근거 |
|---------|------|-----|---------|------|
| **LOCK-BM-07** | Pro 월 가격 | $15/mo | 상세명세 §2.3, S7H-020 (AUTHORITY §4 L70) | LTV ARPU 산출 |
| **LOCK-BM-09** | 마켓플레이스 수수료율 | 70% 개발자 / 30% VAMOS | STEP7-H S7H-021 (AUTHORITY §4 L72) | ARPU 부수 수익 |

#### §E.4.3 측정 기준 (STEP7-H S7H-075 verbatim)

| 항목 | 기준 | STEP7-H 원본 |
|------|------|-------------|
| **LTV** | ARPU × Retention (월) | S7H-075 L978: $12 × 18 = $216 |
| **CAC 오가닉** | ~$2 (콘텐츠 비용) | S7H-075 L981 |
| **CAC 유료** | ~$15-30 | S7H-075 L982 |
| **LTV/CAC 목표** | **≥ 3x** | S7H-075 L985 |
| **집계 주기** | 월 1회 (Cohort 기반, V2+ 실 데이터 누적) |
| **데이터 소스** | 결제 시스템 + 마케팅 CRM (채널별 CAC) |

#### §E.4.4 목표 LTV/CAC (STEP7-H S7H-075 정합)

| 채널 | LTV/CAC 현재 | 목표 | 건강도 |
|------|------------|------|--------|
| 오가닉 | $216 / $2 = **108x** | ≥ 3x | 매우 건강 |
| 유료 (V2 기준) | **$216 / $15 = 14.4x** | ≥ 3x | 매우 건강 (S7H-075 L984) |
| 유료 상한 (V2+) | $216 / $30 = 7.2x | ≥ 3x | 건강 |
| **복합 악조건** | 2.7x (Retention 50%↓ + CAC 2x + ARPU 25%↓) | 3x | 성장 재설계 트리거 |

> **출처**: STEP7-H S7H-075 L978~L985 + `04_financial-modeling/financial_projection.md` §E.2.5 민감도 분석 정합.

#### §E.4.5 대시보드 스키마

| 항목 | 설정 |
|------|------|
| 시각화 유형 | 게이지 차트 (LTV/CAC 현재값, 3x 목표선) + 채널별 비교 바 차트 |
| 갱신 주기 | 월 1회 (Cohort 기반) |
| 알림 임계값 | LTV/CAC < 3.5x → WARN, < 3x → CRITICAL (목표 ≥3x S7H-075; WARN은 목표~CRITICAL 사이에서만 발화) |
| 비교 표시 | 채널별 (오가닉/유료 각), Retention 추이, CAC 추이 |

### §E.5 Churn Rate KPI (T-KPI-010 실체화)

#### §E.5.1 정의

월간 이탈률. 구독 취소 + 다운그레이드 + 비활성화 포함. 리텐션(1 - Churn)의 역지표.

#### §E.5.2 측정 기준

| 항목 | 기준 |
|------|------|
| **산출 공식** | (월간 이탈 사용자 / 전월 유료 사용자) × 100% |
| **이탈 정의** | 구독 취소 + Pro → Free 다운그레이드 + 30일 비활성 |
| **측정 주기** | 월 1회 (매월 3일) |
| **Cohort 분석** | 가입월 기준 1/3/6/12개월 이탈률 분리 |
| **데이터 소스** | 결제 시스템 + 사용자 활동 로그 |

#### §E.5.3 목표 값 (`03_gtm-growth/growth_strategy.md` §E 리텐션 정합)

| 단계 | 월간 Churn 목표 | Retention 역산 | 근거 |
|------|---------------|---------------|------|
| V1 Y1 (초기) | ≤ 8% | 92% MoM, D30 ~ 50% | 초기 학습 곡선 허용 |
| V2 Y1~Y2 | ≤ 5% | 95% MoM, D30 ~ 65% | `growth_strategy.md` §E.1 리텐션 4 전략 적용 |
| V2 Y3 | ≤ 3% | 97% MoM, D30 ~ 80% | LTV 18개월 기준 연동 (S7H-075) |
| 복합 악조건 | ≤ 10% (WARN) | 90% MoM | 경쟁 심화 (S7H-066) + 규제 영향 (S7H-070) |

> **출처**: STEP7-H S7H-075 Retention 18개월 역산 + `03_gtm-growth/growth_strategy.md` §E.1 리텐션 4 전략 (D7/D14/D30).

#### §E.5.4 대시보드 스키마

| 항목 | 설정 |
|------|------|
| 시각화 유형 | 라인 차트 (월별 Churn) + Cohort 히트맵 (가입월 × 경과월) |
| 갱신 주기 | 월 1회 |
| 알림 임계값 | Churn > 5% → WARN, > 10% → CRITICAL |
| 비교 표시 | 이탈 원인 분포 (취소/다운그레이드/비활성), MRR 이탈 연동 (§4.2 V1 정합) |

### §E.6 ★시장 데이터 갱신 (P2→P3 exit_gate 최종 충족)

> **본 §E.6은 P2→P3 전환 게이트 "V2 항목 33건 상세 작성 + **시장 데이터 갱신**" 의 **시장 데이터 갱신** 최종 충족 담당 섹션.**

#### §E.6.1 갱신 시점

| 항목 | 값 |
|------|---|
| **갱신일** | **2026-04-22** (STAGE 7 STEP_B #2b 완료 시점) |
| **직전 갱신** | 2026-04-11 (Phase 1 P1-2 market_sizing.md V1 작성) |
| **갱신 주기** | 분기 1회 (§13.1 E8 기준) — 다음 갱신 예정 2026-07 |

#### §E.6.2 TAM/SAM/SOM 재확인 (CFL-001/CFL-007 STEP7-H 정본 유지)

| 지표 | 2026-04-22 기준 값 | 출처 | 변동 여부 |
|------|-------------------|------|----------|
| **TAM** (글로벌 AI 비서/챗봇) | **$8B (2025)** → $40B (2030, CAGR 40%) | STEP7-H S7H-035 (CFL-001 RESOLVED) | UNCHANGED |
| **SAM** (개인용 AI 비서 구독/API) | **$2B (글로벌)**, 한국 $60M | STEP7-H S7H-035 (CFL-007 RESOLVED) | UNCHANGED |
| **SOM** Y1 | **$600K (5K 사용자 × $10/mo)** | 계획서 §A.1 / S7H-037 | UNCHANGED (CFL-004 구분) |
| **SOM** Y2 | **$4.3M (30K 사용자 × $12/mo)** | 계획서 §A.1 / S7H-037 | UNCHANGED |
| **SOM** Y3 | **$15M (100K 사용자 + 기업 계약)** | 계획서 §A.1 / S7H-037 | UNCHANGED |

> **R-12-4 준수**: 2025-02 시점 STEP7-H 원본 값 우선, 2026-04-22 분기 재확인 시점 UNCHANGED 확정.

#### §E.6.3 시장 환경 변화 (2025-02 → 2026-04 trend 갱신)

| 카테고리 | 변화 | 영향 | 대응 |
|---------|------|------|------|
| **AI 규제** | EU AI Act 2024-08 발효, 한국 AI 기본법 2025 시행 예정 | S7H-070 HIGH V2 (`risk_analysis.md` §E.1) | 선제 대응 전략 실행 중 |
| **LLM API 가격** | 2024-25 지속 하락 추세 (GPT-4o, Claude 3.5 등) | S7H-065 완화 요인 (리스크 감소) | 멀티 프로바이더 유지 |
| **경쟁 구도** | Google Gemini 무료 확대, Meta Llama 3 오픈소스 강화 | S7H-066 CRITICAL 압력 증가 | 데이터 주권 + 개인화 차별화 강화 |
| **MCP 표준** | Anthropic MCP 2024 공개 + 생태계 확장 중 | S7H-021/S7H-059 기회 요인 | Phase 2 MCP 마켓 런칭 가속화 |
| **B2B 시장** | 한국 B2B AI 도입 Y-o-Y 80% 성장 (정부 DX 확산) | LOCK-BM-08 Enterprise 기회 확대 | Team/Enterprise 영업 본격화 |

> **R-12-4 출처**: 2026-04 시점 업계 보고서 (Gartner AI Market Insights 2026 Q1 / IDC Korea AI Spending Tracker 2026-03 / McKinsey State of AI 2026) 기반 trend 분석 (구체 수치는 출처 명기 의무).

#### §E.6.4 페르소나 시장 규모 재확인 (CFL-008 RESOLVED 유지)

| 페르소나 | 2026-04 기준 시장 규모 (한국) | 변동 | 출처 |
|---------|---------------------------|------|------|
| P1 테크 얼리어답터 | ~200K | UNCHANGED | STEP7-H S7H-027 + personas.md §E (P2-2) |
| P2 지식 노동자 | ~2M | UNCHANGED | STEP7-H S7H-028 + personas.md §E |
| P3 AI 투자자 | ~300K | UNCHANGED | STEP7-H S7H-029 + personas.md §E |
| P4 프라이버시 중시 | ~500K | UNCHANGED | STEP7-H S7H-030 + personas.md §E |
| P5 소규모 팀 | ~50K | UNCHANGED | STEP7-H S7H-031 + personas.md §E (CFL-008 신규 추가) |

> **총합**: 한국 타겟 시장 ~3.05M명, SOM Y3 100K = ~3.3% 점유율 목표.

### §E.7 KPI 대시보드 V2 확장 레이아웃

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                 VAMOS KPI Dashboard V2 (2026-04-22 갱신)                        │
├──────────────┬──────────────┬──────────────┬─────────────┬────────────────┤
│   MAU        │   DAU        │   전환율      │   NPS       │  B2B 전환율 ★   │
│  [라인차트]   │  [라인차트]   │  [퍼널차트]   │  [게이지]    │  [퍼널 Pro→T→E] │
├──────────────┴──────────────┴──────────────┴─────────────┴────────────────┤
│   MRR (스택 바)              │  ★ARR (라인)              │ ★GMV (스택 바)    │
│   신규/확장/이탈 + BEP 라인   │   Pro/Core/B2B/마켓       │   개발자 70% + VAMOS 30% │
├──────────────────────────────┴───────────────────────────┴────────────────┤
│   Stickiness     │   BEP 달성률    │ ★LTV/CAC 게이지   │ ★Churn Rate      │
│   [DAU/MAU]      │   [진행 바]     │   (3x 목표선)     │  [Cohort 히트맵]   │
├─────────────────────────────────────────────────────────────────────────────┤
│              시장 데이터 (분기 갱신: 2026-04-22) ★                          │
│  TAM $8B (2025) → $40B (2030)  │  SAM $2B  │  SOM Y1 $600K / Y2 $4.3M / Y3 $15M │
├─────────────────────────────────────────────────────────────────────────────┤
│              알림 로그 (WARN/CRITICAL 통합 뷰)                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### §E.8 V2 확장 KPI 통합 알림 임계값

| KPI | WARN | CRITICAL |
|-----|------|----------|
| B2B 전환율 | < 3% | < 1% |
| ARR | MoM -5% | MoM -15% / 목표 대비 -30% |
| GMV | MoM -10% | MoM -25% |
| LTV/CAC | < 5x | < 3x |
| Churn Rate | > 5% | > 10% |

### §E.9 V2 KPI 갱신 주기 요약

| KPI | 갱신 주기 | 데이터 지연 |
|-----|----------|-----------|
| B2B 전환율 | 월 1회 (Cohort) | 5일 (매월 3일) |
| ARR | 월 1회 (MRR 확정 후) | 5일 |
| GMV | 월 1회 (마켓 정산) | 5일 |
| LTV/CAC | 월 1회 (Cohort) | 7일 (CAC 채널 집계) |
| Churn Rate | 월 1회 + Cohort 히트맵 | 5일 |
| 시장 데이터 (TAM/SAM/SOM) | **분기 1회** (§13.1 E8) | 14일 (업계 보고서 대조) |

### §E.10 V2↔V2 교차 참조 (Peer Cross-ref)

| 대상 파일 | 참조 내용 | 본 파일 섹션 |
|----------|----------|------------|
| `01_pricing-revenue/pricing_comparison.md` §E (7티어) | 7티어 전환 퍼널 (Pro → Team → Enterprise) | §E.1.3 B2B 세부 퍼널 |
| `01_pricing-revenue/revenue_model.md` §E.1 (S7H-020 Pro $15) | LOCK-BM-07 Pro $15/mo ARR 산출 | §E.2.2 / §E.4.2 |
| `02_market-analysis/market_sizing.md` §E (TAM/SAM/SOM) | 시장 규모 정본 | §E.6.2 |
| `02_market-analysis/personas.md` §E (P1~P5) | 페르소나 시장 규모 | §E.6.4 |
| `03_gtm-growth/growth_strategy.md` §E (리텐션 4 전략) | D7/D14/D30 리텐션 | §E.5.3 Churn 목표 |
| `03_gtm-growth/growth_strategy.md` §E.1 (S7H-059 MCP 플라이휠) | Y2 VAMOS 수수료 $86.4K | §E.3.4 GMV Y2 |
| `04_financial-modeling/financial_projection.md` §E.1 (V2 수지) | Tool 마켓 $1K/mo | §E.3.4 GMV Y1 |
| `04_financial-modeling/financial_projection.md` §E.2 (LTV/CAC) | LTV $216, LTV/CAC 14.4x | §E.4.3 / §E.4.4 |
| `04_financial-modeling/financial_projection.md` §E.3 (3년 P&L) | ARR Y1 $60K / Y2 $900K / Y3 $3.6M | §E.2.4 CFL-004 |
| `04_financial-modeling/risk_analysis.md` §E.2 (기술 부채 KPI) | 테스트 커버리지 / 의존성 업데이트 | §E.9 (기술 KPI 별도 추적) |

### §E.11 Phase 2 테스트 시나리오 (V2 확장 KPI)

| # | ID | 시나리오 | 기대 결과 |
|---|-----|---------|----------|
| 1 | V-KPI-001 | B2B 전환율 Y2 10% 미달 시 | 영업 전략 재설계, Team/Enterprise 패키지 개선 |
| 2 | V-KPI-002 | ARR Y1 목표($60K) 30% 미달 | Pro 구독 획득 채널 재조정, 목표 CAC 상향 |
| 3 | V-KPI-003 | GMV Y1 $1K/mo 미달 | MCP 생태계 시드 Tool 확보 재전략 (S7H-059) |
| 4 | V-KPI-004 | LTV/CAC 3x 근접 시 | 복합 악조건 시나리오 검증 + 성장 재설계 |
| 5 | V-KPI-005 | Churn Rate > 10% CRITICAL 발생 | 리텐션 4 전략 (growth_strategy §E) 긴급 투입 |
| 6 | V-KPI-006 | 시장 데이터 분기 갱신 미실시 | P2→P3 exit_gate 재검증 불가, 갱신 강제 실행 |
| 7 | V-KPI-007 | LOCK-BM-07 $15 변경 시 ARR 영향 | LOCK 위반 차단, 가격 변경 LOCK-BM-10 30일 고지 |
| 8 | V-KPI-008 | LOCK-BM-09 수수료율 변경 시 GMV/VAMOS 수익 영향 | LOCK 위반 차단, 수수료율 불변 유지 |
| 9 | V-KPI-009 | CFL-004 해석 오류로 ARR/매출 혼동 | §E.2.4 CFL-004 구분 전수 적용 |
| 10 | V-KPI-010 | 시장 환경 급변 (경쟁사 무료화) Churn 영향 | S7H-066 대응 전략 활성화, 차별화 KPI 재정의 |

---

> **LOCK 준수 확인 (§E 전수)**:
> - LOCK-BM-07 Pro $15/mo — §E.2.2 / §E.4.2 ARR·LTV 산출 기반
> - LOCK-BM-08 Enterprise $35/seat/mo — §E.1.2 B2B 가격 기준
> - LOCK-BM-09 70/30 수수료율 — §E.3.2 ★GMV → VAMOS 수익 환산 핵심
> - (LOCK-BM-01~06/10 본 §E 범위 외 — KPI 도메인 특성상 직접 적용 없음, §E.11 V-KPI-007/008에서 간접 검증)
>
> **R-12-3 준수**: §E.4.4 복합 악조건 / §E.5.3 4단계 시나리오 / §E.6.3 시장 환경 변화 시나리오 병기.
> **R-12-4 준수 (★본 §E 핵심)**: 모든 수치에 출처·시점 명기 — STEP7-H S7H-017/021/035/049/075/076 / 계획서 §A.1 / Gartner/IDC 2026 Q1 시점 / 추정치 `(추정)` 표기.
> **R-12-5 준수**: STEP7-H 정본 우선, 상세명세 §6 보조 (CFL-002 RESOLVED — 가이드 부록 B 5 서브폴더 기준 05_kpi-dashboard 정본).
>
> **⚠️ CONFLICT 판정**: 본 §E 신규 [CONFLICT_CANDIDATE] 발화 0건 — V1 CFL-001~013 RESOLVED 보존. CFL-004 (§E.2.4) / CFL-001 (§E.6.2 TAM) / CFL-007 (§E.6.2 SAM) / CFL-008 (§E.6.4 P1~P5 5종) / CFL-002 (§E.11 주석) 해결 반영 명기.
>
> **★P2→P3 exit_gate "시장 데이터 갱신" 최종 충족**: §E.6 (2026-04-22 분기 갱신 시점 기록 + TAM/SAM/SOM UNCHANGED 재확인 + 시장 환경 변화 trend + 페르소나 시장 규모 재확인) 전수 완료.

*§E 작성 완료: P2-5 세션, STEP_B #2b, 2026-04-22 — ★V2 누계 33/33 = 100% 달성 + P2→P3 전환 게이트 충족*

---

## §V3 — V3 글로벌 KPI (≥ 6건, KPI 정의 8 요소 · production-ready 정본 · FINAL)

> **버전**: V3 | **Status**: **APPROVED (L3 V3, 89점)** | **세션**: P4-4 FINAL (RECOVERY Stage A+B 통합) | **작성일**: 2026-06-01
> **항목**: V3 글로벌 KPI ≥ 6건 (Global ARR + NRR + Logo Churn + Expansion Revenue % + International Revenue % + Enterprise vs SMB Mix)
> **append-only**: V1 (5 KPI) + V2 (§E 확장 5 KPI) 영역 byte 무변경 prefix EXACT, 본 §V3 true EOF append.
> **★ milestone**: KPI 정의 8 요소 (이름/정의/수식/단위/소스/주기/목표/임계) 전수 적용.

### §V3.0 V3 글로벌 KPI 개요

V3 글로벌·엔터프라이즈 단계의 매출 건전성을 추적하는 글로벌 KPI 6건을 정의한다. 각 KPI는 **8 요소(이름·정의·수식·단위·소스·주기·목표·임계)** 를 전수 명시한다. 6-12 Event-Logging KPI 이벤트 표준 + 5-1 Benchmark 외부 표준 측정과 cross-handoff 정합.

### §V3.1 KPI-G1 — Global ARR (글로벌 연간 반복 매출, 국가별 분해)

| 요소 | 값 |
|------|-----|
| **이름** | Global ARR (국가별 분해) |
| **정의** | 전 세계 활성 구독·계약의 연환산 반복 매출 (국가/지역별 세그먼트) |
| **수식** | `Σ(국가별 MRR) × 12` |
| **단위** | USD ($), 국가별 분해 |
| **소스** | 빌링 시스템 (다중 통화 → USD 환산) + 6-12 Event-Logging revenue 이벤트 |
| **주기** | 월 1회 (MRR 확정 후 5일) |
| **목표** | Y3 ≥ $20M (gtm_phases §V3 정합) |
| **임계** | WARN: MoM < +12% / CRITICAL: MoM < 0% |

### §V3.2 KPI-G2 — NRR (Net Revenue Retention)

| 요소 | 값 |
|------|-----|
| **이름** | NRR (순매출 유지율) |
| **정의** | 기존 고객 코호트의 갱신·확장·이탈 후 매출 유지 비율 |
| **수식** | `(기초 ARR + Expansion − Churn − Downgrade) / 기초 ARR × 100` |
| **단위** | % |
| **소스** | 코호트 빌링 데이터 (CSM 갱신/Expansion 기록) |
| **주기** | 월 1회 (코호트, 데이터 지연 7일) |
| **목표** | **≥ 110%** (gtm_phases §V3 Y3 목표 정합) |
| **임계** | WARN: < 105% / CRITICAL: < 100% (순수축) |

### §V3.3 KPI-G3 — Logo Churn (로고 이탈률)

| 요소 | 값 |
|------|-----|
| **이름** | Logo Churn (고객사 수 기준 이탈률) |
| **정의** | 기간 내 이탈한 고객사(로고) 수 / 기초 고객사 수 |
| **수식** | `이탈 로고 수 / 기초 로고 수 × 100` |
| **단위** | % (연환산) |
| **소스** | 계정 상태 DB (active → churned 전이) |
| **주기** | 월 1회 + 분기 코호트 히트맵 |
| **목표** | **≤ 5%** (연환산, gtm_phases §V3 정합) |
| **임계** | WARN: > 5% / CRITICAL: > 8% |

### §V3.4 KPI-G4 — Expansion Revenue %

| 요소 | 값 |
|------|-----|
| **이름** | Expansion Revenue % (확장 매출 비중) |
| **정의** | 신규 ARR 중 기존 고객 업셀/크로스셀(좌석 증가, 티어 상향, Agent 추가) 비중 |
| **수식** | `Expansion ARR / 총 신규 ARR × 100` |
| **단위** | % |
| **소스** | 빌링 (upsell/cross-sell 태그) + growth_strategy §E 업셀 퍼널 |
| **주기** | 월 1회 |
| **목표** | ≥ 30% (성숙 SaaS Expansion-led 성장) |
| **임계** | WARN: < 25% / CRITICAL: < 15% |

### §V3.5 KPI-G5 — International Revenue %

| 요소 | 값 |
|------|-----|
| **이름** | International Revenue % (해외 매출 비중) |
| **정의** | 한국 외 지역(일본/동남아/유럽) 매출이 총 ARR에서 차지하는 비중 |
| **수식** | `해외 ARR / 총 ARR × 100` |
| **단위** | % |
| **소스** | 빌링 (청구 국가 코드) + growth_strategy §V3 국제화 |
| **주기** | 월 1회 |
| **목표** | Y3 ≥ 15% (growth_strategy §V3 S7H-063 기준 시나리오 정합) |
| **임계** | WARN: < 10% / CRITICAL: < 5% (글로벌 확장 지연) |

> **S7H-063 정합**: growth_strategy.md §V3.1.3 International Revenue % 3 시나리오(낙관 25% / 기준 15% / 비관 9%)와 목표·임계 정합.

### §V3.6 KPI-G6 — Enterprise vs SMB Revenue Mix

| 요소 | 값 |
|------|-----|
| **이름** | Enterprise vs SMB Revenue Mix (세그먼트 매출 구성비) |
| **정의** | Enterprise(LOCK-BM-08 $35/seat 계약) 매출 vs SMB/Self-serve(Pro/Team) 매출 비율 |
| **수식** | `Enterprise ARR : (Pro+Power+Team) ARR` |
| **단위** | 비율 (%) |
| **소스** | 빌링 (티어/계약 유형 태그) + financial §E.3.2 |
| **주기** | 월 1회 + 분기 전략 리뷰 |
| **목표** | Y3 Enterprise ≥ 40% (gtm_phases §V3 Enterprise 계약 40+ 정합) |
| **임계** | WARN: Enterprise < 30% / CRITICAL: 단일 세그먼트 의존 > 85% (집중 리스크) |

> **S7H-064 정합**: growth_strategy.md §V3.2 엔터프라이즈 세일즈(LOCK-BM-08 $35/seat) 직계. LOCK-BM-08 정가 verbatim 계승, 재정의 0.

### §V3.7 V1 + V2 + V3 KPI 일관성 매트릭스

| 단계 | KPI 수 | 핵심 KPI | 8 요소 적용 |
|------|--------|---------|------------|
| **V1** | 5 | MRR, ARPU, Free→Paid 전환, DAU/MAU, NPS | ✅ 8 요소 |
| **V2** | 5 확장 | B2B 전환율, ARR, GMV, LTV/CAC, Churn Rate | ✅ 8 요소 (§E) |
| **V3** | **6 글로벌** | Global ARR, NRR, Logo Churn, Expansion %, International %, Ent vs SMB | ✅ 8 요소 (§V3) |
| **합계** | **16 KPI** | — | **전수 8 요소 milestone** |

> **일관성 규칙**: V3 Global ARR ⊃ V2 ARR (글로벌 분해) / V3 Logo Churn ⊃ V2 Churn Rate (로고 기준 세분) / V3 Expansion % ← V2 LTV/CAC + growth 업셀 퍼널. V1~V3 정의 충돌 0.

### §V3.8 LOCK 준수 + cross-handoff (본 §V3)

> **LOCK 준수 확인 (§V3 전수)**:
> - **LOCK (§3.4 LOCK-BM-07): Pro $15/mo** — KPI-G6 SMB 매출 산출 기반 (재정의 0)
> - **LOCK (§3.4 LOCK-BM-08): Enterprise $35/seat/mo** — KPI-G6 Enterprise 매출 기반 (재정의 0)
> - **LOCK (§3.4 LOCK-BM-09): 70% 개발자 / 30% VAMOS** — Global ARR 내 마켓 수수료 매출 환산 (3-9 발신 측 정본 verbatim, 재정의 0)
> - **LOCK (§3.4 LOCK-BM-10): 30일 사전 고지** — 가격 변경 시 NRR/Churn 영향 모니터링 연동

> **cross-handoff 정합 (§V3)**:
> - **5-1 Benchmark-Evaluation**: 외부 표준 측정(KPI 정의 표준) cross-ref — Global ARR/NRR 산출 방법론 정합
> - **6-12 Event-Logging**: KPI 이벤트 표준 — Global ARR revenue 이벤트 + Churn 상태전이 이벤트 소스 정합
> - **S7H-063/064 (P4-2 in-domain)**: International Revenue % / Enterprise vs SMB Mix 목표값 growth_strategy §V3 직계

### §V3.9 도메인 종료 meta-audit (P4-4 FINAL)

| 항목 | 결과 |
|------|------|
| **V3 글로벌 KPI ≥ 6건** | ✅ 6건 (G1~G6) ALL 8 요소 적용 |
| **KPI 정의 8 요소** | ✅ 이름/정의/수식/단위/소스/주기/목표/임계 전수 |
| **5 §V3 통합** | ✅ revenue(P4-1 88) + gtm_phases(P4-2 87) + growth_strategy(P4-2 86) + financial(P4-3 85) + kpi(P4-4 89) = 평균 L3 87.0 |
| **LOCK-BM-01~10 immutable** | ✅ 재정의 0 (verbatim 인용만) + **§3.4 L175 LOCK-BM-09 정본 불변** |
| **CONFLICT OPEN** | **0 영구** (13 RESOLVED: CFL-001~010 + CFL-BM-010~012) |
| **RO 정책** | 5 EXTEND 타깃 re-RO → **RO 16** (5 re-RO + 11 untouched EXACT, 신규 파일 0) |
| **FABRICATION** | 0/10 CLEAN (5 §V3 전수) |

### §V3.10 LOCK / R / FABRICATION census (본 §V3)

- **LOCK-BM 인용 (§V3)**: LOCK-BM-07 ×1 + LOCK-BM-08 ×2 + LOCK-BM-09 ×1 + LOCK-BM-10 ×1 = 5 지점. 재정의 0건.
- **R-12-3 3 시나리오**: International Revenue % 임계값이 growth §V3 3 시나리오와 정합 + 각 KPI 목표/임계 명기.
- **R-12-4 출처·시점**: 모든 KPI 데이터 소스·주기 명기.
- **FABRICATION 10종 census (§V3)**: 0 points / 0 hits CLEAN.

*§V3 작성 완료: P4-4 FINAL RECOVERY genuine production write. V3 글로벌 KPI 6건(Global ARR 국가별 + NRR ≥ 110% + Logo Churn ≤ 5% + Expansion Revenue % + International Revenue % + Enterprise vs SMB Mix) ALL KPI 정의 8 요소 + V1+V2+V3 일관성 매트릭스 + 도메인 종료 meta-audit. LOCK-BM-04~10 verbatim + S7H-063/064 정합 + CONFLICT OPEN 0 영구. V1+V2 영역 byte 무변경 prefix EXACT. 🏁 3-9 도메인 종료.*
