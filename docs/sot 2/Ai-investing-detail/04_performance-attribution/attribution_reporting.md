# 귀인 리포팅 자동화 (Attribution Reporting)
> **버전**: v1.1
> **Status**: APPROVED
> **L3 완성도**: ☑E1 ☑E2 ☑E3 ☑E4 ☑E5 ☑E6 ☑E7 ☑E8 ☑E9
> **작성일**: 2026-03-22
> **Last-reviewed**: 2026-03-23
> **원본 관점**: #4 성과 귀인 분석
> **정본 소유 개념**: —
> **기술스택 의존성**: SPEC §14 LOCK 범위 내

---

### B-9. 귀인 리포팅 자동화 (Attribution Reporting)

**현재**: 완전히 없음
**필요한 것**:

| # | 항목 | 상세 |
|---|------|------|
| 33 | **일간 귀인 스냅샷** | 매일 장 마감 후 자동 생성. 오늘의 P&L = 시장 효과 + 섹터 효과 + 종목 효과 + 전략 효과 분해 |
| 34 | **주간/월간 종합 귀인 리포트** | 기간 누적 귀인, 최대 기여/손실 요인, 전략별 성과 히트맵 |
| 35 | **이상 탐지(Anomaly Detection)** | 귀인 결과에서 비정상 패턴 자동 감지. "특정 전략의 알파가 갑자기 -3σ" → 전략 오작동 경고 |
| 36 | **사용자 맞춤 귀인 뷰** | 초보자: "오늘 +2%는 삼성전자가 올라서(+1.5%)가 가장 컸어요" / 전문가: Brinson 분해 + 팩터 노출 차트 |

---

## E1. Input - 데이터, 필수 필드, 전처리

| 필드명 | 타입 | 필수 | 설명 | 전처리 |
|--------|------|------|------|--------|
| `attribution_data` | `AttributionBreakdown` | Y | Brinson 분해 결과 (시장/섹터/종목/전략 효과) | 합계 = 총 P&L 검증 |
| `portfolio_snapshot` | `PortfolioSnapshot` | Y | 포트폴리오 보유 현황 | 기준일 매칭 |
| `risk_metrics` | `RiskAdjustedMetricsResult` | Y | Sharpe, IR 등 위험 조정 지표 | B-7 출력 |
| `persistence_data` | `PerformancePersistenceResult` | N | 지속성 분석 결과 | B-8 출력 |
| `report_period` | `str` | Y | 리포트 기간: `"daily"`, `"weekly"`, `"monthly"` | enum 검증 |
| `user_level` | `str` | Y | 사용자 수준: `"beginner"`, `"expert"` | enum 검증 |
| `anomaly_threshold_sigma` | `float` | N | 이상 탐지 임계값 (default=3.0) | — |
| `output_format` | `str` | N | `"pdf"`, `"html"`, `"json"` (default=`"json"`) | — |
| `as_of_date` | `date` | Y | 기준일 | — |

**전처리**: 귀인 데이터 합계 검증 → 기간 집계 → 사용자 수준별 필터링

---

## E2. Algorithm - 복사→구현 가능 의사코드 with REAL formulas

### A. Daily Attribution Snapshot (일간 P&L 분해)

```
Total_PnL = Market_Effect + Sector_Effect + Stock_Effect + Strategy_Effect + Residual
  |Residual| < 0.01 × |Total_PnL| 이어야 정합성 통과
```

```python
def generate_daily_snapshot(attribution: AttributionBreakdown,
                            as_of: date) -> dict:
    """일간 귀인 스냅샷 생성"""
    total = attribution.total_pnl
    components = {
        "market_effect": attribution.market_effect,
        "sector_effect": attribution.sector_effect,
        "stock_effect": attribution.stock_effect,
        "strategy_effect": attribution.strategy_effect,
    }
    residual = total - sum(components.values())
    if abs(residual) >= abs(total) * 0.01:
        raise ValueError("귀인 정합성 오류")
    # 기여도 순 정렬
    top_contributors = sorted(attribution.stock_details,
                              key=lambda x: abs(x.contribution), reverse=True)[:5]
    return {
        "date": as_of, "total_pnl": total,
        "components": components, "residual": residual,
        "top_5_contributors": top_contributors,
    }
```

### B. Period Aggregation (주간/월간 누적)

```python
def aggregate_period(daily_snapshots: List[dict],
                     period: str) -> dict:
    """일간 스냅샷을 주간/월간으로 집계"""
    agg = {"market_effect": 0, "sector_effect": 0,
           "stock_effect": 0, "strategy_effect": 0, "total_pnl": 0}
    for snap in daily_snapshots:
        for k in agg:
            agg[k] += snap.get(k, snap.get("components", {}).get(k, 0))
    # 히트맵용 일별 기여도 매트릭스
    heatmap_data = pd.DataFrame([s["components"] for s in daily_snapshots],
                                 index=[s["date"] for s in daily_snapshots])
    return {"period": period, "aggregated": agg, "heatmap": heatmap_data}
```

### C. Anomaly Detection (이상 탐지)

```
z_score_i = (alpha_i - μ_alpha) / σ_alpha
  |z_score| > 3.0 → 이상 패턴 경고
```

```python
def detect_anomalies(strategy_alphas: pd.Series,
                     sigma_threshold: float = 3.0) -> List[dict]:
    """전략별 알파에서 비정상 패턴 감지"""
    mu = strategy_alphas.mean()
    sigma = strategy_alphas.std()
    anomalies = []
    for date, alpha in strategy_alphas.items():
        z = (alpha - mu) / (sigma + 1e-10)
        if abs(z) > sigma_threshold:
            anomalies.append({
                "date": date, "alpha": alpha,
                "z_score": z, "severity": "CRITICAL" if abs(z) > 4.0 else "WARNING"
            })
    return anomalies
```

### D. User-Level View Rendering

```python
def render_view(snapshot: dict, user_level: str) -> dict:
    """사용자 수준별 귀인 뷰 생성"""
    if user_level == "beginner":
        top = snapshot["top_5_contributors"][0]
        return {
            "summary": f"오늘 {snapshot['total_pnl']:+.2%}는 "
                       f"{top.symbol}이(가) {top.contribution:+.2%}로 가장 컸습니다.",
            "chart_type": "simple_bar",
            "data": {k: v for k, v in snapshot["components"].items()},
        }
    else:  # expert
        return {
            "brinson_decomposition": snapshot["components"],
            "residual": snapshot["residual"],
            "top_contributors": snapshot["top_5_contributors"],
            "chart_type": "stacked_waterfall",
            "factor_exposure": snapshot.get("factor_exposure", {}),
        }
```

### E. PDF/Dashboard Output

```python
def export_report(report_data: dict, output_format: str,
                  template_path: str) -> bytes:
    """리포트 내보내기"""
    if output_format == "pdf":
        # weasyprint / reportlab
        html = render_jinja_template(template_path, report_data)
        return weasyprint.HTML(string=html).write_pdf()
    elif output_format == "html":
        return render_jinja_template(template_path, report_data).encode()
    else:  # json
        return json.dumps(report_data, default=str).encode()
```

---

## E3. Output - @dataclass, confidence, 소비자

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import date

@dataclass
class AttributionReport:
    """귀인 리포트 결과"""
    as_of_date: date
    report_period: str                           # "daily" | "weekly" | "monthly"
    user_level: str                              # "beginner" | "expert"

    # P&L 분해
    total_pnl: float
    market_effect: float
    sector_effect: float
    stock_effect: float
    strategy_effect: float
    residual: float

    # 상위 기여 종목
    top_contributors: List[dict]                 # [{symbol, contribution, pct}]
    bottom_contributors: List[dict]              # 최대 손실 기여

    # 기간 집계
    period_heatmap: Optional[dict]               # 일별 효과 매트릭스

    # 이상 탐지
    anomalies: List[dict]                        # [{date, alpha, z_score, severity}]

    # 렌더링
    rendered_view: dict                          # 사용자 수준별 뷰 데이터
    output_bytes: Optional[bytes]                # PDF/HTML 바이트 (요청 시)

    # 메타
    confidence: float                            # 귀인 정합성 기반 0.0~1.0
    circuit_breaker_triggered: bool = False      # 이상 탐지 CRITICAL 시

# 소비자: 대시보드 UI, 알림 시스템, PDF 다운로드 API
```

---

## E4. Class/API Design - class with methods

```python
class AttributionReporter:
    """귀인 리포팅 자동화 엔진"""

    def __init__(self, config: dict):
        self.sigma_threshold: float = config.get("anomaly_threshold_sigma", 3.0)
        self.template_dir: str = config.get("template_dir", "templates/attribution")
        self.default_format: str = config.get("output_format", "json")

    # --- 스냅샷 ---
    def daily_snapshot(self, attribution: AttributionBreakdown,
                       as_of: date) -> dict:
        """일간 귀인 스냅샷"""
        ...

    # --- 기간 집계 ---
    def aggregate(self, snapshots: List[dict], period: str) -> dict:
        """주간/월간 누적 귀인"""
        ...

    # --- 이상 탐지 ---
    def detect_anomalies(self, alpha_series: pd.Series) -> List[dict]:
        """σ 기반 이상 패턴 탐지"""
        ...

    # --- 렌더링 ---
    def render(self, snapshot: dict, user_level: str) -> dict:
        """사용자 수준별 뷰 생성"""
        ...

    # --- 내보내기 ---
    def export(self, report: AttributionReport,
               output_format: Optional[str] = None) -> bytes:
        """PDF / HTML / JSON 내보내기"""
        ...

    # --- Circuit Breaker ---
    def check_circuit_breaker(self, anomalies: List[dict]) -> bool:
        """CRITICAL 이상 탐지 존재 시 True"""
        return any(a["severity"] == "CRITICAL" for a in anomalies)

    # --- 통합 실행 ---
    def run(self, attribution: AttributionBreakdown,
            risk_metrics: RiskAdjustedMetricsResult,
            as_of: date, period: str = "daily",
            user_level: str = "expert",
            output_format: str = "json") -> AttributionReport:
        """전체 리포트 생성 파이프라인"""
        ...
```

---

## E5. Tech Stack Dependency - table

| 구성요소 | 기술/라이브러리 | 버전 | 용도 | LOCK 참조 |
|----------|----------------|------|------|-----------|
| 데이터 처리 | pandas | ≥2.0 | 기간 집계, 히트맵 매트릭스 | SPEC §14 |
| 수치 연산 | numpy | ≥1.24 | z-score, 통계량 | SPEC §14 |
| 템플릿 엔진 | Jinja2 | ≥3.1 | HTML/PDF 템플릿 렌더링 | SPEC §14 |
| PDF 생성 | WeasyPrint | ≥60.0 | HTML → PDF 변환 | SPEC §14 |
| 시각화 | plotly | ≥5.18 | 인터랙티브 차트 (대시보드) | — |
| 시각화 (정적) | matplotlib | ≥3.8 | PDF 내 정적 차트 | — |
| JSON 직렬화 | json (stdlib) | — | API 응답 | — |
| 스케줄러 | APScheduler / cron | — | 일간/주간 자동 생성 | — |

---

## E6. Performance Requirements - table

| 지표 | 목표 | 비고 |
|------|------|------|
| 일간 스냅샷 생성 | < 200ms | 귀인 데이터 수신 후 |
| 월간 집계 (22일) | < 500ms | 히트맵 포함 |
| 이상 탐지 | < 100ms | 100개 전략 스캔 |
| beginner 뷰 렌더링 | < 100ms | 텍스트 요약 생성 |
| expert 뷰 렌더링 | < 300ms | 차트 데이터 포함 |
| PDF 내보내기 | < 3s | A4 5페이지 기준 |
| HTML 대시보드 렌더링 | < 1s | plotly 차트 포함 |
| 전체 `run()` | < 5s | PDF 포함 시 |

---

## E7. Error Handling - table

| 에러 상황 | 감지 방법 | 대응 | 심각도 |
|-----------|----------|------|--------|
| 귀인 정합성 오류 (잔차 > 1%) | `abs(residual) > 0.01 * abs(total)` | WARN 로그, 잔차 별도 표시 | HIGH |
| 귀인 데이터 미수신 | None / timeout | 전일 스냅샷 재사용, ALERT | HIGH |
| PDF 렌더링 실패 | WeasyPrint exception | JSON fallback, 에러 로그 | MEDIUM |
| 이상 탐지 CRITICAL (z > 4σ) | z_score 검사 | **Circuit Breaker**: 즉시 알림 발송 | CRITICAL |
| 사용자 수준 미지정 | enum 검증 실패 | default `"expert"` | LOW |
| 히트맵 데이터 부족 (< 5일) | len(snapshots) 검사 | 히트맵 미생성, 텍스트만 반환 | LOW |
| 템플릿 파일 미발견 | FileNotFoundError | 기본 템플릿 사용, WARN | MEDIUM |
| 51% Gate: 잔차 > 51% of total | 비율 검사 | 귀인 모델 재검증 권고 | HIGH |

---

## E8. Test Criteria - Unit/Integration/Acceptance

### Unit Tests
- `test_daily_snapshot_consistency`: 모든 효과 합 = total_pnl (잔차 < 1%)
- `test_aggregate_weekly_sum`: 5일 일간 합 = 주간 집계값
- `test_anomaly_detection_3sigma`: z=3.5 데이터 → anomaly 감지
- `test_anomaly_detection_normal`: z<2 → anomaly 미감지
- `test_beginner_view_text`: 초보자 뷰에 종목명·수익률 포함 확인
- `test_expert_view_brinson`: 전문가 뷰에 Brinson 분해 포함 확인
- `test_export_json_valid`: JSON 내보내기 파싱 가능 확인
- `test_export_pdf_bytes`: PDF 바이트 시작 `%PDF` 확인

### Integration Tests
- `test_full_report_pipeline`: 실제 귀인 데이터로 전체 리포트 생성
- `test_anomaly_triggers_alert`: CRITICAL 이상 → Circuit Breaker → 알림 연동
- `test_scheduled_daily_generation`: 스케줄러 트리거 → 스냅샷 자동 생성

### Acceptance Criteria
- 일간 리포트: 장 마감 후 5분 내 자동 생성
- PDF 리포트: 차트·테이블 정상 렌더링, 깨짐 없음
- 이상 탐지: 인위적 3σ 이상 주입 시 100% 감지
- 초보자 뷰: 비전문 사용자 이해도 테스트 통과 (UX 리뷰)

---

## E9. LOCK References - table

| LOCK ID | 항목 | 본 문서 관련 내용 |
|---------|------|-------------------|
| SPEC §14 | 기술스택 범위 | pandas, Jinja2, WeasyPrint, plotly |
| B-6 | Benchmark Management | 벤치마크 귀인 데이터 소스 |
| B-7 | Risk-Adjusted Metrics | Sharpe/IR 등 리포트 포함 지표 |
| B-8 | Performance Persistence | 지속성 분석 결과 리포트 포함 |
| B-10 | Cost Attribution | Gross vs Net 비용 귀인 리포트 연계 |
| 51% Gate | 의사결정 임계값 | 귀인 잔차 51% 초과 시 모델 재검증 |

---

## STEP7-I 보강: 정기 분석 보고서 자동 생성 템플릿 (S7I-074)

> **보강 근거**: step7i_mapping.md PARTIAL — 일간/주간/월간 성과 요약, 귀인 분석, 리스크 지표, 시장 코멘터리를 자동 생성하는 정기 보고서 템플릿 상세 누락
> **Priority**: MED

### E1. Input
- **데이터**: 포트폴리오 성과 데이터, 귀인 분석 결과, 리스크 지표, 시장 데이터
- **필수 필드**:
  - `portfolio_id: str` — 포트폴리오 식별자
  - `report_type: str` — `"daily"` | `"weekly"` | `"monthly"`
  - `period_start: date` — 리포트 기간 시작일
  - `period_end: date` — 리포트 기간 종료일
  - `performance_data: Dict` — 성과 데이터 `{"total_return", "benchmark_return", "excess_return", "sharpe", "sortino", "max_drawdown"}`
  - `attribution_data: Dict` — 귀인 분석 `{"market_effect", "sector_effect", "stock_effect", "strategy_effect", "top_contributors", "bottom_contributors"}`
  - `risk_data: Dict` — 리스크 지표 `{"var_95", "cvar_95", "volatility", "beta", "tracking_error"}`
  - `market_data: Dict` — 시장 지표 `{"kospi_return", "sp500_return", "bond_yield", "usd_krw", "vix"}`
  - `output_format: str` — `"pdf"` | `"html"` | `"email"`
  - `template_id: Optional[str]` — 커스텀 템플릿 ID
  - `recipients: List[str]` — 배포 대상 (이메일 또는 user_id)
- **전처리**:
  1. 성과 데이터 기간 일치 검증 (attribution + risk + market 동일 기간)
  2. 수익률 연율화 (일간→연간: × 252, 월간→연간: × 12; 변동성 연율화에만 × √252 적용)
  3. 통화 단위 통일 (KRW/USD 혼합 시 KRW 기준)

### E2. Algorithm
```python
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import date, datetime
from enum import Enum

class ReportType(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class OutputFormat(Enum):
    PDF = "pdf"
    HTML = "html"
    EMAIL = "email"

@dataclass
class ReportSection:
    """보고서 섹션"""
    title: str
    content: str                        # HTML 렌더링 가능 컨텐츠
    charts: List[Dict] = field(default_factory=list)   # 차트 데이터
    tables: List[Dict] = field(default_factory=list)   # 테이블 데이터
    order: int = 0

@dataclass
class GeneratedReport:
    """생성된 보고서"""
    report_id: str
    portfolio_id: str
    report_type: ReportType
    period: tuple                       # (start_date, end_date)
    sections: List[ReportSection]
    generated_at: datetime
    output_format: OutputFormat
    output_bytes: Optional[bytes] = None    # PDF/HTML 바이트
    metadata: Dict = field(default_factory=dict)

# ── 보고서 템플릿 구조 ──
REPORT_TEMPLATES = {
    "daily": {
        "sections": [
            {"id": "executive_summary", "title": "일간 요약", "order": 1},
            {"id": "performance", "title": "성과 현황", "order": 2},
            {"id": "attribution", "title": "P&L 분해", "order": 3},
            {"id": "top_movers", "title": "주요 변동 종목", "order": 4},
            {"id": "risk_snapshot", "title": "리스크 스냅샷", "order": 5},
            {"id": "market_commentary", "title": "시장 코멘터리", "order": 6},
        ],
    },
    "weekly": {
        "sections": [
            {"id": "executive_summary", "title": "주간 요약", "order": 1},
            {"id": "performance_trend", "title": "주간 성과 추이", "order": 2},
            {"id": "attribution_weekly", "title": "주간 귀인 분석", "order": 3},
            {"id": "sector_analysis", "title": "섹터별 분석", "order": 4},
            {"id": "risk_evolution", "title": "리스크 변화", "order": 5},
            {"id": "strategy_performance", "title": "전략별 성과", "order": 6},
            {"id": "outlook", "title": "다음 주 전망", "order": 7},
        ],
    },
    "monthly": {
        "sections": [
            {"id": "executive_summary", "title": "월간 요약", "order": 1},
            {"id": "performance_detail", "title": "월간 성과 상세", "order": 2},
            {"id": "attribution_monthly", "title": "월간 귀인 분석", "order": 3},
            {"id": "risk_analysis", "title": "리스크 분석 상세", "order": 4},
            {"id": "factor_exposure", "title": "팩터 노출 분석", "order": 5},
            {"id": "cost_analysis", "title": "비용 분석", "order": 6},
            {"id": "peer_comparison", "title": "벤치마크/피어 비교", "order": 7},
            {"id": "market_review", "title": "시장 리뷰", "order": 8},
            {"id": "outlook", "title": "다음 달 전망", "order": 9},
        ],
    },
}

class PeriodicReportGenerator:
    """정기 분석 보고서 자동 생성기"""

    def __init__(self, template_engine, chart_renderer,
                 pdf_renderer, email_service, scheduler):
        self.template_engine = template_engine   # Jinja2
        self.chart_renderer = chart_renderer     # plotly/matplotlib
        self.pdf_renderer = pdf_renderer         # WeasyPrint
        self.email_service = email_service
        self.scheduler = scheduler

    # ── 1. 스케줄 등록 ──
    def schedule_report(self, portfolio_id: str, report_type: str,
                         schedule_config: Dict) -> Dict:
        """
        정기 보고서 스케줄 등록.
        - daily: 매 영업일 장 마감 후 30분 (18:00 KST)
        - weekly: 매주 금요일 장 마감 후 1시간 (19:00 KST)
        - monthly: 매월 마지막 영업일 장 마감 후 2시간 (20:00 KST)
        """
        cron_map = {
            "daily": {"hour": 18, "minute": 0, "day_of_week": "mon-fri"},
            "weekly": {"hour": 19, "minute": 0, "day_of_week": "fri"},
            "monthly": {"hour": 20, "minute": 0, "day": "last"},
        }

        cron = cron_map.get(report_type, cron_map["daily"])
        job_id = f"report_{portfolio_id}_{report_type}"

        self.scheduler.add_job(
            func=self._generate_and_distribute,
            trigger="cron",
            id=job_id,
            kwargs={"portfolio_id": portfolio_id, "report_type": report_type,
                    "recipients": schedule_config.get("recipients", []),
                    "output_format": schedule_config.get("format", "pdf")},
            **cron,
        )

        return {"job_id": job_id, "schedule": cron, "status": "scheduled"}

    # ── 2. 데이터 집계 ──
    def aggregate_data(self, portfolio_id: str, report_type: str,
                        period_start: date, period_end: date) -> Dict:
        """
        보고서에 필요한 데이터를 기간별로 집계.
        - 성과: 기간 수익률, 벤치마크 대비, Sharpe, MDD
        - 귀인: 시장/섹터/종목/전략 효과 분해
        - 리스크: VaR, 변동성, 베타
        - 시장: 주요 지수, 환율, VIX
        """
        aggregated = {
            "performance": self._aggregate_performance(portfolio_id, period_start, period_end),
            "attribution": self._aggregate_attribution(portfolio_id, period_start, period_end),
            "risk": self._aggregate_risk(portfolio_id, period_start, period_end),
            "market": self._aggregate_market(period_start, period_end),
            "top_movers": self._get_top_movers(portfolio_id, period_start, period_end),
            "strategy_breakdown": self._get_strategy_breakdown(portfolio_id, period_start, period_end),
        }

        return aggregated

    def _aggregate_performance(self, pid, start, end) -> Dict:
        """성과 데이터 집계"""
        # 포트폴리오 DB 조회 → 기간 수익률 계산
        return {
            "total_return": 0.0,
            "benchmark_return": 0.0,
            "excess_return": 0.0,
            "sharpe": 0.0,
            "sortino": 0.0,
            "max_drawdown": 0.0,
            "win_rate": 0.0,
            "daily_returns": [],       # 일별 수익률 시계열 (차트용)
        }

    def _aggregate_attribution(self, pid, start, end) -> Dict:
        """귀인 데이터 집계"""
        return {
            "market_effect": 0.0,
            "sector_effect": 0.0,
            "stock_effect": 0.0,
            "strategy_effect": 0.0,
            "top_contributors": [],
            "bottom_contributors": [],
        }

    def _aggregate_risk(self, pid, start, end) -> Dict:
        """리스크 데이터 집계"""
        return {"var_95": 0.0, "cvar_95": 0.0, "volatility": 0.0, "beta": 0.0, "tracking_error": 0.0}

    def _aggregate_market(self, start, end) -> Dict:
        """시장 데이터 집계"""
        return {"kospi_return": 0.0, "sp500_return": 0.0, "bond_yield": 0.0, "usd_krw": 0.0, "vix": 0.0}

    def _get_top_movers(self, pid, start, end) -> Dict:
        """주요 변동 종목"""
        return {"gainers": [], "losers": []}

    def _get_strategy_breakdown(self, pid, start, end) -> Dict:
        """전략별 성과"""
        return {}

    # ── 3. 템플릿 선택 ──
    def select_template(self, report_type: str,
                         template_id: Optional[str] = None) -> Dict:
        """
        보고서 템플릿 선택.
        - 기본 템플릿: REPORT_TEMPLATES[report_type]
        - 커스텀 템플릿: template_id로 조회
        """
        if template_id:
            custom = self._load_custom_template(template_id)
            if custom:
                return custom

        return REPORT_TEMPLATES.get(report_type, REPORT_TEMPLATES["daily"])

    def _load_custom_template(self, template_id: str) -> Optional[Dict]:
        """커스텀 템플릿 로드"""
        return None  # DB 조회

    # ── 4. 컨텐츠 생성 ──
    def generate_content(self, template: Dict, data: Dict,
                          report_type: str) -> List[ReportSection]:
        """
        템플릿 + 데이터 → 섹션별 컨텐츠 생성.
        각 섹션별로 텍스트, 차트, 테이블 생성.
        """
        sections = []

        for section_def in template["sections"]:
            sid = section_def["id"]

            if sid == "executive_summary":
                content = self._generate_executive_summary(data, report_type)
            elif sid in ("performance", "performance_trend", "performance_detail"):
                content = self._generate_performance_section(data, report_type)
            elif sid in ("attribution", "attribution_weekly", "attribution_monthly"):
                content = self._generate_attribution_section(data, report_type)
            elif sid == "risk_snapshot" or sid == "risk_evolution" or sid == "risk_analysis":
                content = self._generate_risk_section(data, report_type)
            elif sid == "market_commentary" or sid == "market_review":
                content = self._generate_market_commentary(data, report_type)
            elif sid == "top_movers":
                content = self._generate_top_movers(data)
            elif sid == "outlook":
                content = self._generate_outlook(data, report_type)
            else:
                content = ReportSection(title=section_def["title"], content="", order=section_def["order"])

            if isinstance(content, ReportSection):
                content.order = section_def["order"]
                sections.append(content)

        return sorted(sections, key=lambda s: s.order)

    def _generate_executive_summary(self, data: Dict, report_type: str) -> ReportSection:
        """경영진 요약 생성"""
        perf = data["performance"]
        period_label = {"daily": "오늘", "weekly": "이번 주", "monthly": "이번 달"}[report_type]
        sign = "+" if perf["total_return"] >= 0 else ""

        content = (
            f"<h3>{period_label} 성과 요약</h3>"
            f"<p>포트폴리오 수익률: <strong>{sign}{perf['total_return']*100:.2f}%</strong> "
            f"(벤치마크: {perf['benchmark_return']*100:.2f}%)</p>"
            f"<p>초과 수익: {perf['excess_return']*100:.2f}%p | "
            f"Sharpe: {perf['sharpe']:.2f} | MDD: {perf['max_drawdown']*100:.1f}%</p>"
        )

        return ReportSection(
            title=f"{period_label} 요약",
            content=content,
            charts=[{"type": "equity_curve", "data": perf.get("daily_returns", [])}],
            tables=[{"type": "performance_summary", "data": perf}],
        )

    def _generate_performance_section(self, data, report_type) -> ReportSection:
        """성과 섹션"""
        perf = data["performance"]
        return ReportSection(
            title="성과 현황",
            content="<p>기간별 수익률 및 위험 조정 성과</p>",
            charts=[
                {"type": "return_bar", "data": perf},
                {"type": "drawdown_chart", "data": perf.get("daily_returns", [])},
            ],
            tables=[{"type": "risk_return_table", "data": perf}],
        )

    def _generate_attribution_section(self, data, report_type) -> ReportSection:
        """귀인 분석 섹션"""
        attr = data["attribution"]
        return ReportSection(
            title="P&L 분해",
            content="<p>시장/섹터/종목/전략 효과별 P&L 귀인 분석</p>",
            charts=[
                {"type": "waterfall", "data": attr},
                {"type": "contributor_bar", "data": attr.get("top_contributors", [])},
            ],
            tables=[
                {"type": "attribution_table", "data": attr},
                {"type": "top_bottom_table", "data": {
                    "top": attr.get("top_contributors", []),
                    "bottom": attr.get("bottom_contributors", []),
                }},
            ],
        )

    def _generate_risk_section(self, data, report_type) -> ReportSection:
        """리스크 섹션"""
        risk = data["risk"]
        return ReportSection(
            title="리스크 분석",
            content="<p>포트폴리오 리스크 지표 현황</p>",
            charts=[{"type": "risk_gauge", "data": risk}],
            tables=[{"type": "risk_metrics_table", "data": risk}],
        )

    def _generate_market_commentary(self, data, report_type) -> ReportSection:
        """시장 코멘터리"""
        market = data["market"]
        return ReportSection(
            title="시장 코멘터리",
            content=(
                f"<p>KOSPI: {market['kospi_return']*100:+.2f}% | "
                f"S&P500: {market['sp500_return']*100:+.2f}% | "
                f"USD/KRW: {market['usd_krw']:,.0f} | VIX: {market['vix']:.1f}</p>"
            ),
            charts=[{"type": "market_overview", "data": market}],
        )

    def _generate_top_movers(self, data) -> ReportSection:
        """주요 변동 종목"""
        movers = data.get("top_movers", {})
        return ReportSection(
            title="주요 변동 종목",
            content="",
            tables=[
                {"type": "gainers", "data": movers.get("gainers", [])},
                {"type": "losers", "data": movers.get("losers", [])},
            ],
        )

    def _generate_outlook(self, data, report_type) -> ReportSection:
        """전망"""
        return ReportSection(
            title="전망",
            content="<p>향후 전략 방향 및 리스크 요인</p>",
        )

    # ── 5. 렌더링 ──
    def render(self, sections: List[ReportSection],
                output_format: str, metadata: Dict = None) -> bytes:
        """
        섹션 리스트 → PDF/HTML 렌더링.
        - PDF: Jinja2 HTML 템플릿 → WeasyPrint → PDF bytes
        - HTML: Jinja2 렌더링 → HTML string → bytes
        - EMAIL: HTML 렌더링 → 이메일 본문 구성
        """
        html_content = self.template_engine.render(
            "report_base.html",
            sections=sections,
            metadata=metadata or {},
            generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
        )

        # 차트 렌더링
        for section in sections:
            for chart in section.charts:
                chart["rendered"] = self.chart_renderer.render(chart["type"], chart["data"])

        if output_format == "pdf":
            return self.pdf_renderer.html_to_pdf(html_content)
        elif output_format == "html":
            return html_content.encode("utf-8")
        else:  # email
            return html_content.encode("utf-8")

    # ── 6. 배포 ──
    def distribute(self, report: GeneratedReport,
                    recipients: List[str],
                    output_format: str) -> Dict:
        """
        생성된 보고서를 수신자에게 배포.
        - PDF: 이메일 첨부 파일 + 대시보드 다운로드 링크
        - HTML: 이메일 본문 + 대시보드 인라인
        - 알림: 보고서 생성 완료 push
        """
        delivery_results = {"success": 0, "failed": 0, "details": []}

        for recipient in recipients:
            try:
                if output_format == "pdf":
                    self.email_service.send_with_attachment(
                        to=recipient,
                        subject=f"[AI Investing] {report.report_type.value} 리포트 - {report.period[1]}",
                        body="정기 분석 보고서가 생성되었습니다. 첨부 파일을 확인해주세요.",
                        attachment=report.output_bytes,
                        filename=f"report_{report.portfolio_id}_{report.period[1]}.pdf",
                    )
                elif output_format in ("html", "email"):
                    self.email_service.send_html(
                        to=recipient,
                        subject=f"[AI Investing] {report.report_type.value} 리포트 - {report.period[1]}",
                        html_body=report.output_bytes.decode("utf-8") if report.output_bytes else "",
                    )
                delivery_results["success"] += 1
                delivery_results["details"].append({"recipient": recipient, "status": "sent"})
            except Exception as e:
                delivery_results["failed"] += 1
                delivery_results["details"].append({"recipient": recipient, "status": "failed", "error": str(e)})

        return delivery_results

    async def _generate_and_distribute(self, portfolio_id: str, report_type: str,
                                        recipients: List[str], output_format: str):
        """스케줄러에서 호출되는 통합 실행 함수"""
        # 기간 결정
        today = date.today()
        if report_type == "daily":
            period = (today, today)
        elif report_type == "weekly":
            period = (today - __import__("datetime").timedelta(days=4), today)
        else:
            period = (today.replace(day=1), today)

        # 파이프라인 실행
        data = self.aggregate_data(portfolio_id, report_type, period[0], period[1])
        template = self.select_template(report_type)
        sections = self.generate_content(template, data, report_type)
        output_bytes = self.render(sections, output_format)

        report = GeneratedReport(
            report_id=f"{portfolio_id}_{report_type}_{today}",
            portfolio_id=portfolio_id,
            report_type=ReportType(report_type),
            period=period,
            sections=sections,
            generated_at=datetime.utcnow(),
            output_format=OutputFormat(output_format),
            output_bytes=output_bytes,
        )

        self.distribute(report, recipients, output_format)
```

### E3. Output
- **스키마**:
  ```python
  @dataclass
  class GeneratedReport:
      report_id: str
      portfolio_id: str
      report_type: ReportType
      period: tuple
      sections: List[ReportSection]
      generated_at: datetime
      output_format: OutputFormat
      output_bytes: Optional[bytes]
      metadata: Dict
  ```
- **소비자**: 이메일 수신자, 대시보드 UI (다운로드/인라인), 아카이브 스토리지 (S3/GCS)

### E4. Class/API Design
```python
class PeriodicReportGenerator:
    """정기 분석 보고서 자동 생성기.

    일간/주간/월간 성과, 귀인, 리스크, 시장 코멘터리 보고서 자동 생성 및 배포.
    """

    def __init__(self, template_engine, chart_renderer,
                 pdf_renderer, email_service, scheduler): ...

    def schedule_report(self, portfolio_id: str, report_type: str,
                         schedule_config: Dict) -> Dict:
        """정기 보고서 스케줄 등록 (cron 기반)."""
        ...

    def aggregate_data(self, portfolio_id: str, report_type: str,
                        period_start: date, period_end: date) -> Dict:
        """보고서용 데이터 집계."""
        ...

    def select_template(self, report_type: str,
                         template_id: Optional[str] = None) -> Dict:
        """보고서 템플릿 선택 (기본/커스텀)."""
        ...

    def generate_content(self, template: Dict, data: Dict,
                          report_type: str) -> List[ReportSection]:
        """템플릿 + 데이터 → 섹션별 컨텐츠 생성."""
        ...

    def render(self, sections: List[ReportSection],
                output_format: str, metadata: Dict = None) -> bytes:
        """PDF/HTML 렌더링."""
        ...

    def distribute(self, report: GeneratedReport,
                    recipients: List[str], output_format: str) -> Dict:
        """이메일/대시보드 배포."""
        ...
```

### E5. Tech Stack Dependency
| 라이브러리 | 버전 | SPEC §14 LOCK | 용도 |
|-----------|------|--------------|------|
| Jinja2 | ≥3.1 | ☑ | HTML 보고서 템플릿 렌더링 |
| WeasyPrint | ≥60.0 | ☑ | HTML → PDF 변환 |
| plotly | ≥5.18 | — | 인터랙티브 차트 (HTML 보고서) |
| matplotlib | ≥3.8 | — | 정적 차트 (PDF 보고서) |
| APScheduler | ≥3.10 | — | cron 기반 스케줄링 |
| pandas | ≥2.0 | ☑ | 데이터 집계 |

### E6. Performance Requirements
| 지표 | 기준 | 측정 방법 |
|------|------|----------|
| 일간 보고서 생성 | ≤ 30s | 데이터 집계 + 렌더링 |
| 주간 보고서 생성 | ≤ 60s | 5일 데이터 + 차트 |
| 월간 보고서 생성 | ≤ 120s | 22일 데이터 + 상세 분석 |
| PDF 렌더링 | ≤ 10s | A4 10페이지 기준 |
| 이메일 발송 | ≤ 5s / 수신자 | SMTP 발송 |
| 스케줄 정확도 | ±1분 | APScheduler cron |

### E7. Error Handling
| 예외 시나리오 | 복구 로직 | 심각도 |
|-------------|----------|--------|
| 성과 데이터 미수신 | 전일 데이터 사용 + "데이터 미확정" 워터마크 | HIGH |
| 귀인 분석 실패 | 귀인 섹션 "분석 불가" 표시, 나머지 섹션 정상 생성 | MEDIUM |
| PDF 렌더링 실패 | HTML fallback + 에러 로그 | MEDIUM |
| 이메일 발송 실패 | 3회 재시도 → 대시보드 다운로드 링크 push 알림 | MEDIUM |
| 차트 렌더링 오류 | 해당 차트 "차트 생성 실패" placeholder | LOW |
| 스케줄 미실행 (서버 장애) | 서버 복구 후 미생성 보고서 소급 생성 | HIGH |

### E8. Test Criteria
- **Unit**:
  - 일간 템플릿: 6개 섹션 정상 생성 확인
  - 월간 템플릿: 9개 섹션 정상 생성 확인
  - 경영진 요약: 수익률 +2.5% → "포트폴리오 수익률: +2.50%" 포함
  - PDF 렌더링: 출력 바이트 시작 `%PDF` 확인
  - 빈 데이터 입력 → 0값/빈 테이블로 정상 렌더링 (오류 없음)
- **Integration**:
  - 전체 파이프라인: aggregate → template → content → render → distribute E2E
  - 스케줄러 트리거 → 보고서 자동 생성 → 이메일 발송
  - 귀인 분석 모듈 연동 → attribution 섹션 데이터 정합성
- **Acceptance**:
  - 일간 보고서: 장 마감 후 30분 내 자동 생성 및 배포
  - PDF 보고서: 차트/테이블 렌더링 정상, 깨짐 없음 (수동 검수)
  - 월간 보고서: 전문 투자자 피드백 만족도 ≥ 4.0/5.0

### E9. LOCK References
| LOCK 값 | 출처 | 적용 방식 |
|---------|------|----------|
| 일간 스케줄 18:00 KST | 본 문서 정의 | 장 마감 후 30분 |
| 주간 스케줄 금 19:00 KST | 본 문서 정의 | 주말 전 생성 |
| 월간 스케줄 말일 20:00 KST | 본 문서 정의 | 월말 마감 후 |
| SPEC §14 기술스택 | SPEC §14 | Jinja2, WeasyPrint, pandas |
| B-9 귀인 데이터 연동 | B-9 | 귀인 리포팅 자동화 결과 참조 |

---
