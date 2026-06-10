# 투자 가능성 필터 (Investability Filter)
> **버전**: v2.0
> **Status**: APPROVED
> **작성일**: 2026-03-22
> **Last-reviewed**: 2026-03-23
> **원본 관점**: #7 투자 유니버스 관리
> **정본 소유 개념**: —
> **기술스택 의존성**: SPEC §14 LOCK 범위 내
> **L3 완성도**: E1 ☑ | E2 ☑ | E3 ☑ | E4 ☑ | E5 ☑ | E6 ☑ | E7 ☑ | E8 ☑ | E9 ☑

---

### B-5. 투자 가능성 필터 (Investability Filter)

| # | 항목 | 상세 |
|---|------|------|
| 18 | **법적 제약 필터** | 외국인 투자 제한 종목(한국), 제재 대상 기업, 투자 금지 국가 자산 자동 제외. §10 법적 제약 시스템과 연동 |
| 19 | **ESG/윤리 필터** | 무기, 담배, 도박 등 사용자 설정 기반 윤리적 제외. ESG 등급 기반 필터 옵션 |
| 20 | **공매도 가능성 필터** | 공매도 전략 적용 시 대차 가능 여부 확인. 한국 공매도 금지 기간 반영 |
| 21 | **포지션 사이즈 제약** | 유동성 대비 최대 포지션 크기. 일거래량의 1% 이상 보유 불가 → 자동 제외 또는 크기 제한 |

---

## E1. Input

### Kafka Topics

| Topic | 용도 | Key |
|-------|------|-----|
| `universe.definition.snapshot` | 유니버스 스냅샷 (필터 대상) | `universe_id` |
| `regulation.foreign_limit` | 외국인 투자 한도 데이터 (한국) | `symbol` |
| `regulation.sanctions` | 제재 대상 기업/국가 리스트 | `entity_id` |
| `market.esg.ratings` | ESG 등급 데이터 | `symbol` |
| `market.short_selling.status` | 공매도 가능/금지 상태 | `symbol` |
| `market.lending.availability` | 대차 가능 여부 및 수수료 | `symbol` |
| `market.price.daily` | 일별 거래량 (포지션 사이즈 계산용) | `symbol` |

### Required Fields

```
foreign_limit:
  - symbol: str
  - foreign_ownership_pct: float     # 현재 외국인 보유 비율
  - foreign_limit_pct: float         # 외국인 한도 비율
  - remaining_pct: float             # 잔여 매수 가능 비율
  - is_restricted: bool              # 한도 소진 여부
  - updated_at: datetime

sanctions:
  - entity_id: str
  - entity_name: str
  - entity_type: str                 # "COMPANY", "COUNTRY", "PERSON"
  - sanction_source: str             # "OFAC", "EU", "UN"
  - related_symbols: List[str]
  - effective_date: date

esg_rating:
  - symbol: str
  - provider: str                    # "MSCI", "SUSTAINALYTICS", "INTERNAL"
  - overall_grade: str               # "AAA"~"CCC"
  - environmental_score: float       # 0~100
  - social_score: float
  - governance_score: float
  - controversy_flag: bool
  - sector_exclusions: List[str]     # ["WEAPONS", "TOBACCO", "GAMBLING"]

short_selling:
  - symbol: str
  - market: str
  - short_sellable: bool
  - ban_period_start: Optional[date]
  - ban_period_end: Optional[date]
  - lending_fee_pct: float           # 연간 대차 수수료율
  - shares_available: int

position_constraint:
  - symbol: str
  - avg_daily_volume: float          # 20일 평균 거래대금 (USD)
  - max_position_pct: float          # 일거래량 대비 최대 비율 (기본 1%)
  - max_position_usd: float          # 최대 포지션 크기 (USD)
```

### TimescaleDB Schema

```sql
-- 투자 가능성 필터 결과 (hypertable)
CREATE TABLE investability_filter_log (
    ts                TIMESTAMPTZ NOT NULL,
    universe_id       TEXT NOT NULL,
    symbol            TEXT NOT NULL,
    filter_type       TEXT NOT NULL,       -- 'LEGAL', 'ESG', 'SHORT', 'POSITION'
    is_investable     BOOLEAN,
    reason            TEXT,
    details           JSONB
);
SELECT create_hypertable('investability_filter_log', 'ts');

-- 외국인 투자 한도 추적
CREATE TABLE foreign_ownership_tracker (
    symbol            TEXT NOT NULL,
    ownership_pct     DOUBLE PRECISION,
    limit_pct         DOUBLE PRECISION,
    remaining_pct     DOUBLE PRECISION,
    is_restricted     BOOLEAN DEFAULT FALSE,
    updated_at        TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (symbol)
);

-- ESG 등급
CREATE TABLE esg_ratings (
    symbol            TEXT NOT NULL,
    provider          TEXT NOT NULL,
    overall_grade     TEXT,
    e_score           DOUBLE PRECISION,
    s_score           DOUBLE PRECISION,
    g_score           DOUBLE PRECISION,
    controversy_flag  BOOLEAN DEFAULT FALSE,
    sector_exclusions TEXT[],
    updated_at        TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (symbol, provider)
);

-- 공매도 상태
CREATE TABLE short_selling_status (
    symbol            TEXT NOT NULL,
    market            TEXT NOT NULL,
    short_sellable    BOOLEAN DEFAULT TRUE,
    ban_start         DATE,
    ban_end           DATE,
    lending_fee_pct   DOUBLE PRECISION,
    shares_available  BIGINT,
    updated_at        TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (symbol, market)
);

-- 포지션 사이즈 제약
CREATE TABLE position_constraints (
    symbol            TEXT NOT NULL,
    avg_daily_volume  DOUBLE PRECISION,
    max_position_pct  DOUBLE PRECISION DEFAULT 0.01,  -- 1%
    max_position_usd  DOUBLE PRECISION,
    updated_at        TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (symbol)
);
```

### Preprocessing Rules

| 항목 | 전처리 규칙 |
|------|------------|
| 외국인 한도 | KIS API로 실시간 조회, 한도 90% 이상 소진 시 경고 |
| 제재 리스트 | OFAC SDN 리스트 주간 갱신, EU/UN 제재 리스트 반영 |
| ESG 등급 | MSCI 기준 우선, 미제공 시 자체 스코어링 |
| 공매도 상태 | 한국 공매도 금지/허용 정책 실시간 반영 (금융위원회 공고) |
| 포지션 제약 | avg_daily_volume은 20일 이동평균, USD 환산 |

---

## E2. Algorithm

```python
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set
from datetime import datetime, date
from enum import Enum


class FilterType(Enum):
    LEGAL = "LEGAL"
    ESG = "ESG"
    SHORT_SELLING = "SHORT_SELLING"
    POSITION_SIZE = "POSITION_SIZE"


class InvestabilityStatus(Enum):
    INVESTABLE = "INVESTABLE"
    RESTRICTED = "RESTRICTED"        # 부분 제한 (사이즈 제약)
    EXCLUDED = "EXCLUDED"            # 완전 제외


@dataclass
class FilterCheckResult:
    """단일 필터 검사 결과"""
    symbol: str
    filter_type: FilterType
    status: InvestabilityStatus
    reason: str
    details: Dict


@dataclass
class InvestabilityResult:
    """종목별 투자 가능성 종합 결과"""
    symbol: str
    is_investable: bool
    status: InvestabilityStatus
    filter_results: List[FilterCheckResult]
    max_position_usd: Optional[float]     # 포지션 사이즈 제약 시
    restrictions: List[str]


@dataclass
class InvestabilityBatchResult:
    """전체 유니버스 투자 가능성 결과"""
    universe_id: str
    timestamp: datetime
    total_checked: int
    total_investable: int
    total_restricted: int
    total_excluded: int
    results: List[InvestabilityResult]
    exclusion_summary: Dict[str, int]     # filter_type -> excluded count
    confidence: float


# ── 18. 법적 제약 필터 ────────────────────────────────────────

def check_legal_constraints(symbol: str, asset_class: str,
                            foreign_limit: dict, sanctions: list) -> FilterCheckResult:
    """
    법적 제약 필터

    검사 항목:
      1. 외국인 투자 한도 (한국 주식만):
         remaining_pct < 1% → EXCLUDED (매수 불가)
         remaining_pct < 5% → RESTRICTED (소량만 가능)

      2. 제재 대상 (전체):
         OFAC/EU/UN 제재 리스트 매칭 → EXCLUDED

      3. 투자 금지 국가:
         북한, 이란, 시리아, 쿠바 등 관련 자산 → EXCLUDED
    """
    # 외국인 한도 (한국 주식)
    if asset_class == "KR_STOCK" and foreign_limit:
        remaining = foreign_limit.get("remaining_pct", 100.0)
        if remaining < 1.0:
            return FilterCheckResult(
                symbol=symbol,
                filter_type=FilterType.LEGAL,
                status=InvestabilityStatus.EXCLUDED,
                reason=f"외국인 투자 한도 소진 (잔여 {remaining:.1f}%)",
                details={"remaining_pct": remaining, "limit_pct": foreign_limit.get("limit_pct")}
            )
        elif remaining < 5.0:
            return FilterCheckResult(
                symbol=symbol,
                filter_type=FilterType.LEGAL,
                status=InvestabilityStatus.RESTRICTED,
                reason=f"외국인 투자 한도 근접 (잔여 {remaining:.1f}%)",
                details={"remaining_pct": remaining}
            )

    # 제재 대상 검사
    sanctioned_symbols = set()
    for sanction in sanctions:
        sanctioned_symbols.update(sanction.get("related_symbols", []))

    if symbol in sanctioned_symbols:
        return FilterCheckResult(
            symbol=symbol,
            filter_type=FilterType.LEGAL,
            status=InvestabilityStatus.EXCLUDED,
            reason="제재 대상 기업 (OFAC/EU/UN)",
            details={"sanction_match": True}
        )

    return FilterCheckResult(
        symbol=symbol,
        filter_type=FilterType.LEGAL,
        status=InvestabilityStatus.INVESTABLE,
        reason="법적 제약 없음",
        details={}
    )


# ── 19. ESG/윤리 필터 ────────────────────────────────────────

def check_esg_filter(symbol: str, esg_data: dict,
                     user_preferences: dict) -> FilterCheckResult:
    """
    ESG/윤리 필터

    검사 항목:
      1. 섹터 제외 (사용자 설정):
         excluded_sectors: ["WEAPONS", "TOBACCO", "GAMBLING", "FOSSIL_FUEL"]
         해당 섹터 → EXCLUDED

      2. ESG 등급 필터 (옵션):
         min_esg_grade: "BBB" (기본값)
         등급 하위 → EXCLUDED 또는 RESTRICTED

         등급 순서: AAA > AA > A > BBB > BB > B > CCC

      3. 논란(Controversy) 필터:
         controversy_flag = True → RESTRICTED

      4. 크립토 ESG 예외:
         크립토는 ESG 등급 미적용 (데이터 부재)
    """
    esg_grade_order = {"AAA": 7, "AA": 6, "A": 5, "BBB": 4, "BB": 3, "B": 2, "CCC": 1}

    # 크립토 예외
    if not esg_data or esg_data.get("asset_class") == "CRYPTO":
        return FilterCheckResult(
            symbol=symbol,
            filter_type=FilterType.ESG,
            status=InvestabilityStatus.INVESTABLE,
            reason="ESG 필터 비적용 (크립토/데이터 없음)",
            details={}
        )

    # 1. 섹터 제외
    excluded_sectors = set(user_preferences.get("excluded_sectors", []))
    asset_sectors = set(esg_data.get("sector_exclusions", []))
    overlap = excluded_sectors & asset_sectors
    if overlap:
        return FilterCheckResult(
            symbol=symbol,
            filter_type=FilterType.ESG,
            status=InvestabilityStatus.EXCLUDED,
            reason=f"윤리적 제외 섹터: {', '.join(overlap)}",
            details={"excluded_sectors": list(overlap)}
        )

    # 2. ESG 등급 필터
    min_grade = user_preferences.get("min_esg_grade", "BBB")
    current_grade = esg_data.get("overall_grade", "BBB")
    min_order = esg_grade_order.get(min_grade, 4)
    current_order = esg_grade_order.get(current_grade, 4)

    if current_order < min_order:
        return FilterCheckResult(
            symbol=symbol,
            filter_type=FilterType.ESG,
            status=InvestabilityStatus.EXCLUDED,
            reason=f"ESG 등급 미달 ({current_grade} < {min_grade})",
            details={"current_grade": current_grade, "min_grade": min_grade}
        )

    # 3. 논란 필터
    if esg_data.get("controversy_flag", False):
        return FilterCheckResult(
            symbol=symbol,
            filter_type=FilterType.ESG,
            status=InvestabilityStatus.RESTRICTED,
            reason="ESG 논란 종목 (controversy flag)",
            details={"controversy_flag": True}
        )

    return FilterCheckResult(
        symbol=symbol,
        filter_type=FilterType.ESG,
        status=InvestabilityStatus.INVESTABLE,
        reason="ESG 필터 통과",
        details={"grade": current_grade}
    )


# ── 20. 공매도 가능성 필터 ────────────────────────────────────

def check_short_selling(symbol: str, market: str,
                        short_data: dict, today: date) -> FilterCheckResult:
    """
    공매도 가능성 필터

    검사 항목:
      1. 공매도 금지 기간 (한국):
         ban_start <= today <= ban_end → 공매도 불가

      2. 대차 가능 여부:
         shares_available == 0 → 대차 불가, 공매도 불가
         lending_fee_pct > 50% → RESTRICTED (비용 과다)

      3. 크립토 공매도:
         선물/마진 거래 가능 여부 확인
         거래소별 공매도 지원 여부

    ※ 공매도 전략 미사용 시 이 필터는 skip
    """
    if not short_data:
        return FilterCheckResult(
            symbol=symbol,
            filter_type=FilterType.SHORT_SELLING,
            status=InvestabilityStatus.INVESTABLE,
            reason="공매도 데이터 없음 (롱 전략만 사용)",
            details={}
        )

    # 한국 공매도 금지 기간
    if market == "KR":
        ban_start = short_data.get("ban_start")
        ban_end = short_data.get("ban_end")
        if ban_start and ban_end and ban_start <= today <= ban_end:
            return FilterCheckResult(
                symbol=symbol,
                filter_type=FilterType.SHORT_SELLING,
                status=InvestabilityStatus.EXCLUDED,
                reason=f"공매도 금지 기간 ({ban_start}~{ban_end})",
                details={"ban_start": str(ban_start), "ban_end": str(ban_end)}
            )

    # 대차 가능 여부
    if not short_data.get("short_sellable", True):
        return FilterCheckResult(
            symbol=symbol,
            filter_type=FilterType.SHORT_SELLING,
            status=InvestabilityStatus.EXCLUDED,
            reason="공매도 불가 종목",
            details={}
        )

    shares = short_data.get("shares_available", 0)
    if shares == 0:
        return FilterCheckResult(
            symbol=symbol,
            filter_type=FilterType.SHORT_SELLING,
            status=InvestabilityStatus.EXCLUDED,
            reason="대차 가능 주식 없음",
            details={"shares_available": 0}
        )

    # 대차 수수료 과다
    fee = short_data.get("lending_fee_pct", 0)
    if fee > 50.0:
        return FilterCheckResult(
            symbol=symbol,
            filter_type=FilterType.SHORT_SELLING,
            status=InvestabilityStatus.RESTRICTED,
            reason=f"대차 수수료 과다 ({fee:.1f}%)",
            details={"lending_fee_pct": fee}
        )

    return FilterCheckResult(
        symbol=symbol,
        filter_type=FilterType.SHORT_SELLING,
        status=InvestabilityStatus.INVESTABLE,
        reason="공매도 가능",
        details={"shares_available": shares, "lending_fee_pct": fee}
    )


# ── 21. 포지션 사이즈 제약 ────────────────────────────────────

def check_position_size_constraint(symbol: str, avg_daily_volume_usd: float,
                                   target_position_usd: float,
                                   max_volume_pct: float = 0.01) -> FilterCheckResult:
    """
    포지션 사이즈 제약

    규칙:
      max_position = avg_daily_volume × max_volume_pct

      기본: max_volume_pct = 1% (일거래량의 1%)

      target_position > max_position → RESTRICTED (크기 제한)
      max_position < $10,000 → EXCLUDED (투자 비현실적)

    자산군별 조정:
      US Stock: max_volume_pct = 1%
      KR Stock: max_volume_pct = 1%
      Crypto:   max_volume_pct = 0.5% (유동성 리스크 높음)
    """
    max_position = avg_daily_volume_usd * max_volume_pct

    if max_position < 10_000:
        return FilterCheckResult(
            symbol=symbol,
            filter_type=FilterType.POSITION_SIZE,
            status=InvestabilityStatus.EXCLUDED,
            reason=f"최대 포지션 과소 (${max_position:,.0f} < $10,000)",
            details={
                "avg_daily_volume_usd": avg_daily_volume_usd,
                "max_position_usd": max_position,
                "max_volume_pct": max_volume_pct
            }
        )

    if target_position_usd > max_position:
        return FilterCheckResult(
            symbol=symbol,
            filter_type=FilterType.POSITION_SIZE,
            status=InvestabilityStatus.RESTRICTED,
            reason=f"포지션 크기 제한 (목표 ${target_position_usd:,.0f} > 최대 ${max_position:,.0f})",
            details={
                "target_position_usd": target_position_usd,
                "max_position_usd": max_position,
                "reduction_needed_pct": ((target_position_usd - max_position) / target_position_usd) * 100
            }
        )

    return FilterCheckResult(
        symbol=symbol,
        filter_type=FilterType.POSITION_SIZE,
        status=InvestabilityStatus.INVESTABLE,
        reason="포지션 사이즈 제약 없음",
        details={"max_position_usd": max_position}
    )


# ── 전체 투자 가능성 필터 오케스트레이터 ──────────────────────

def run_investability_filter(universe: list, foreign_limits: dict,
                             sanctions: list, esg_ratings: dict,
                             short_data: dict, daily_volumes: dict,
                             user_preferences: dict,
                             target_positions: dict) -> InvestabilityBatchResult:
    """
    전체 유니버스 투자 가능성 필터 실행

    필터 순서 (단락 평가):
      1. 법적 제약 → EXCLUDED이면 나머지 skip
      2. ESG/윤리 → EXCLUDED이면 나머지 skip
      3. 공매도 (공매도 전략 사용 시만)
      4. 포지션 사이즈

    종합 판정:
      하나라도 EXCLUDED → 전체 EXCLUDED
      하나라도 RESTRICTED → 전체 RESTRICTED
      모두 INVESTABLE → 전체 INVESTABLE
    """
    results = []
    excluded_count = 0
    restricted_count = 0
    investable_count = 0
    exclusion_summary: Dict[str, int] = {}
    today = date.today()

    for asset in universe:
        sym = asset["symbol"]
        asset_class = asset.get("asset_class", "")
        market = {"US_STOCK": "US", "KR_STOCK": "KR", "CRYPTO": "CRYPTO"}.get(asset_class, "US")

        filter_results = []
        overall_status = InvestabilityStatus.INVESTABLE
        max_pos = None
        restrictions = []

        # 1. 법적 제약
        legal = check_legal_constraints(
            sym, asset_class,
            foreign_limits.get(sym, {}),
            sanctions
        )
        filter_results.append(legal)
        if legal.status == InvestabilityStatus.EXCLUDED:
            overall_status = InvestabilityStatus.EXCLUDED
            exclusion_summary["LEGAL"] = exclusion_summary.get("LEGAL", 0) + 1
        elif legal.status == InvestabilityStatus.RESTRICTED:
            overall_status = InvestabilityStatus.RESTRICTED
            restrictions.append(legal.reason)

        # 2. ESG/윤리 (EXCLUDED가 아닐 때만)
        if overall_status != InvestabilityStatus.EXCLUDED:
            esg = check_esg_filter(
                sym,
                esg_ratings.get(sym, {}),
                user_preferences
            )
            filter_results.append(esg)
            if esg.status == InvestabilityStatus.EXCLUDED:
                overall_status = InvestabilityStatus.EXCLUDED
                exclusion_summary["ESG"] = exclusion_summary.get("ESG", 0) + 1
            elif esg.status == InvestabilityStatus.RESTRICTED:
                if overall_status != InvestabilityStatus.EXCLUDED:
                    overall_status = InvestabilityStatus.RESTRICTED
                restrictions.append(esg.reason)

        # 3. 공매도 (공매도 전략 사용 시)
        if user_preferences.get("use_short_selling", False) and overall_status != InvestabilityStatus.EXCLUDED:
            short = check_short_selling(
                sym, market,
                short_data.get(sym, {}),
                today
            )
            filter_results.append(short)
            if short.status == InvestabilityStatus.EXCLUDED:
                overall_status = InvestabilityStatus.EXCLUDED
                exclusion_summary["SHORT"] = exclusion_summary.get("SHORT", 0) + 1
            elif short.status == InvestabilityStatus.RESTRICTED:
                if overall_status != InvestabilityStatus.EXCLUDED:
                    overall_status = InvestabilityStatus.RESTRICTED
                restrictions.append(short.reason)

        # 4. 포지션 사이즈
        if overall_status != InvestabilityStatus.EXCLUDED:
            vol_pct = 0.005 if asset_class == "CRYPTO" else 0.01
            pos = check_position_size_constraint(
                sym,
                daily_volumes.get(sym, 0),
                target_positions.get(sym, 0),
                max_volume_pct=vol_pct
            )
            filter_results.append(pos)
            if pos.status == InvestabilityStatus.EXCLUDED:
                overall_status = InvestabilityStatus.EXCLUDED
                exclusion_summary["POSITION"] = exclusion_summary.get("POSITION", 0) + 1
            elif pos.status == InvestabilityStatus.RESTRICTED:
                if overall_status != InvestabilityStatus.EXCLUDED:
                    overall_status = InvestabilityStatus.RESTRICTED
                restrictions.append(pos.reason)
                max_pos = pos.details.get("max_position_usd")

        # 집계
        if overall_status == InvestabilityStatus.EXCLUDED:
            excluded_count += 1
        elif overall_status == InvestabilityStatus.RESTRICTED:
            restricted_count += 1
        else:
            investable_count += 1

        results.append(InvestabilityResult(
            symbol=sym,
            is_investable=overall_status != InvestabilityStatus.EXCLUDED,
            status=overall_status,
            filter_results=filter_results,
            max_position_usd=max_pos,
            restrictions=restrictions
        ))

    total = len(universe)
    confidence = (investable_count + 0.5 * restricted_count) / max(total, 1)

    return InvestabilityBatchResult(
        universe_id="",
        timestamp=datetime.utcnow(),
        total_checked=total,
        total_investable=investable_count,
        total_restricted=restricted_count,
        total_excluded=excluded_count,
        results=results,
        exclusion_summary=exclusion_summary,
        confidence=round(confidence, 4)
    )
```

---

## E3. Output

### Output Dataclass

```python
@dataclass
class InvestabilityBatchResult:
    universe_id: str                      # 유니버스 식별자
    timestamp: datetime                   # 필터 실행 시점
    total_checked: int                    # 검사 대상 종목 수
    total_investable: int                 # 투자 가능 종목 수
    total_restricted: int                 # 부분 제한 종목 수
    total_excluded: int                   # 완전 제외 종목 수
    results: List[InvestabilityResult]    # 종목별 상세 결과
    exclusion_summary: Dict[str, int]     # 필터 유형별 제외 건수
    confidence: float                     # 0~1
```

### Kafka Output Topics

| Topic | 내용 | Key |
|-------|------|-----|
| `investability.filter.result` | 전체 필터 결과 | `universe_id` |
| `investability.filter.excluded` | 제외 종목 알림 | `symbol` |
| `investability.filter.restricted` | 제한 종목 알림 (사이즈 제약 포함) | `symbol` |
| `investability.position.limit` | 포지션 사이즈 제약 정보 | `symbol` |

### Confidence Levels

| Level | 범위 | 의미 |
|-------|------|------|
| HIGH | 0.85 ~ 1.0 | 85% 이상 종목 투자 가능 |
| MEDIUM | 0.70 ~ 0.84 | 15~30% 종목 제외/제한 |
| LOW | < 0.70 | 30% 이상 종목 제외 (유니버스 재검토 필요) |

### Consumers

| Consumer | 용도 |
|----------|------|
| Universe Definition (B-1) | Active 유니버스 최종 결정 |
| Portfolio Optimizer | 투자 가능 종목 + 포지션 제약 반영 |
| Order Executor | 주문 전 투자 가능성 최종 확인 |
| Compliance Monitor | 법적 제약 위반 감시 |

---

## E4. Class/API Design

```python
from abc import ABC, abstractmethod


class BaseInvestabilityFilter(ABC):
    """투자 가능성 필터 기본 클래스"""

    @abstractmethod
    def check(self, symbol: str, **kwargs) -> FilterCheckResult:
        """단일 필터 검사"""
        ...

    @abstractmethod
    def batch_check(self, universe: list) -> InvestabilityBatchResult:
        """전체 유니버스 배치 검사"""
        ...


class InvestabilityFilterService(BaseInvestabilityFilter):
    """
    투자 가능성 필터 서비스

    Responsibilities:
      - 법적 제약 검사 (외국인 한도, 제재)
      - ESG/윤리 필터 적용
      - 공매도 가능성 확인
      - 포지션 사이즈 제약 계산
      - 종합 투자 가능성 판정
    """

    def __init__(self, db_pool, kafka_producer, regulation_service,
                 esg_provider):
        self.db = db_pool
        self.producer = kafka_producer
        self.reg_svc = regulation_service
        self.esg_provider = esg_provider

    def check(self, symbol: str, **kwargs) -> FilterCheckResult:
        """단일 종목 투자 가능성 검사"""
        ...

    def batch_check(self, universe: list) -> InvestabilityBatchResult:
        """전체 유니버스 배치 투자 가능성 검사"""
        ...

    def check_legal(self, symbol: str) -> FilterCheckResult:
        """법적 제약 필터"""
        ...

    def check_esg(self, symbol: str, preferences: dict) -> FilterCheckResult:
        """ESG/윤리 필터"""
        ...

    def check_short_selling(self, symbol: str) -> FilterCheckResult:
        """공매도 가능성 필터"""
        ...

    def check_position_size(self, symbol: str,
                            target_usd: float) -> FilterCheckResult:
        """포지션 사이즈 제약 검사"""
        ...

    def get_max_position(self, symbol: str) -> float:
        """해당 종목 최대 포지션 크기 조회"""
        ...
```

---

## E5. Tech Stack Dependency

| Library | Version | LOCK Status | 용도 |
|---------|---------|-------------|------|
| `asyncpg` | 0.29.x | §14 LOCK | TimescaleDB 비동기 접속 |
| `confluent-kafka` | 2.3.x | §14 LOCK | Kafka produce/consume |
| `pandas` | 2.1.x | §14 LOCK | 제재 리스트 매칭, 배치 처리 |
| `pydantic` | 2.5.x | §14 LOCK | 필터 설정/결과 스키마 검증 |
| `httpx` | 0.27.x | §14 LOCK | KIS API, OFAC 리스트 조회 |
| `redis` | 5.0.x | §14 LOCK | 외국인 한도/공매도 상태 캐시 |

---

## E6. Performance Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| 전체 유니버스 배치 필터 | ≤ 15s | 800종목 전체 4단계 필터 |
| 단일 종목 필터 | ≤ 100ms | 주문 전 실시간 검사 |
| 외국인 한도 조회 | ≤ 200ms | KIS API + 캐시 |
| 제재 리스트 매칭 | ≤ 1s | 전체 유니버스 vs 제재 리스트 |
| 포지션 사이즈 계산 | ≤ 50ms | 단일 종목 |
| 메모리 사용량 | ≤ 128MB | 필터 프로세스 |

---

## E7. Error Handling

| Error Scenario | Recovery Logic | Severity |
|----------------|---------------|----------|
| 외국인 한도 API 실패 | 캐시된 한도 데이터 사용 (4시간 TTL), 캐시 미스 시 보수적 판단(RESTRICTED) | HIGH |
| 제재 리스트 갱신 실패 | 이전 유효 리스트 사용, 1주 이상 미갱신 시 경고 | CRITICAL |
| ESG 등급 데이터 미제공 | 해당 종목 ESG 필터 skip, "BBB" 기본 등급 가정 | LOW |
| 공매도 금지 기간 정보 부정확 | 금융위 공고 재확인, 불확실 시 공매도 차단 | HIGH |
| 포지션 사이즈 계산 실패 (거래량 0) | 해당 종목 EXCLUDED 처리 | MEDIUM |
| 필터 순서 의존성 실패 | 실패한 필터 이후 나머지 필터 계속 실행, 부분 결과 반환 | MEDIUM |

---

## E8. Test Criteria

### Unit Tests

| Test ID | 시나리오 | Expected Result |
|---------|---------|-----------------|
| UT-IF-01 | 외국인 한도 잔여 0.5% → 법적 필터 | status=EXCLUDED |
| UT-IF-02 | 외국인 한도 잔여 3% → 법적 필터 | status=RESTRICTED |
| UT-IF-03 | 외국인 한도 잔여 50% → 법적 필터 | status=INVESTABLE |
| UT-IF-04 | OFAC 제재 기업 → 법적 필터 | status=EXCLUDED |
| UT-IF-05 | 무기 섹터 + 사용자 제외 설정 → ESG 필터 | status=EXCLUDED |
| UT-IF-06 | ESG 등급 CCC, 최소 BBB → ESG 필터 | status=EXCLUDED |
| UT-IF-07 | 한국 공매도 금지 기간 중 → 공매도 필터 | status=EXCLUDED |
| UT-IF-08 | 대차 수수료 60% → 공매도 필터 | status=RESTRICTED |
| UT-IF-09 | 일거래량 $100M, 목표 $2M → 포지션 | status=INVESTABLE (max=$1M) |
| UT-IF-10 | 일거래량 $500K, 크립토 → 포지션 | max_position=$2,500 (0.5%) |

### Integration Tests

| Test ID | 시나리오 | Expected Result |
|---------|---------|-----------------|
| IT-IF-01 | 800종목 배치 필터 → 결과 DB 저장 → Kafka publish | 15초 이내 완료 |
| IT-IF-02 | 주문 전 실시간 필터 → 투자 가능성 확인 | 100ms 이내 응답 |
| IT-IF-03 | 외국인 한도 변경 이벤트 → 필터 재실행 → 상태 변경 알림 | E2E 정상 동작 |

### Acceptance Criteria

- [ ] 법적 제약 종목 100% 자동 제외
- [ ] ESG 필터 사용자 설정 기반 동작
- [ ] 공매도 금지 기간 정확 반영 (한국)
- [ ] 포지션 사이즈 제약 자동 계산 및 적용
- [ ] 주문 전 실시간 투자 가능성 확인 100ms 이내

---

## E9. LOCK References

| LOCK 항목 | Source | 적용 |
|-----------|--------|------|
| §14 기술스택 | SPEC §14 | asyncpg, confluent-kafka, pandas, pydantic, httpx, redis |
| §10 법적 제약 | SPEC §10 | 외국인 한도, 제재, 공매도 규제 연동 |
| §7 유니버스 관리 | SPEC §7 | Investable Universe 필터 기준 |
| §6 자산군 정의 | SPEC §6 | 자산군별 포지션 사이즈 차등 |
| §8 리스크 관리 | SPEC §8 | 포지션 사이즈 제약 |

---

## L3 판정

| 섹션 | 상태 | 비고 |
|------|------|------|
| E1. Input | ✅ | Kafka 7개 토픽, TimescaleDB 5개 테이블, 전처리 규칙 |
| E2. Algorithm | ✅ | 4개 항목 전체 Python 구현, 포지션 계산 공식, 단락 평가 로직 |
| E3. Output | ✅ | 출력 스키마, Kafka 4개 출력 토픽, confidence 3단계 |
| E4. Class/API Design | ✅ | BaseInvestabilityFilter → InvestabilityFilterService 계층 |
| E5. Tech Stack | ✅ | 6개 라이브러리 §14 LOCK |
| E6. Performance | ✅ | 6개 메트릭 정량 목표 |
| E7. Error Handling | ✅ | 6개 에러 시나리오, 복구 로직, 심각도 |
| E8. Test Criteria | ✅ | UT 10개, IT 3개, AC 5개 |
| E9. LOCK References | ✅ | 5개 SPEC 참조 |
