# sleep_management.md — 수면 관리

> **P-ID**: P-012, P-012-a
> **V단계**: V1
> **상태**: P-012 NEW / P-012-a NEW
> **L3 완성**: 2026-04-10
> **정본 소유자**: sot 2/3-6_Health-Wellness-EmotionAI/03_health-data/

---

## 교차 참조 블록

| 참조 문서 | 위치 | 참조 내용 |
|----------|------|----------|
| 종합계획서 §6.3 | P-012, P-012-a | 수면 관리 + 수면 품질 점수 매핑 |
| 종합계획서 §3.4 | LOCK-HW-02/03/04/06 | LOCK 보호 값 |
| 상세명세 §4.1 | SleepData | 기존 수면 데이터 모델 |
| 상세명세 §4.2 | HealthKitSync.sleep_analysis | 수면 동기화 명세 |
| STEP7-P | P-012 | 수면 관리 원본 |
| AUTHORITY_CHAIN.md | §1~§5 | 정본 계층 및 충돌 해결 |
| health_data_privacy.md | 동일 폴더 | 프라이버시 등급 및 암호화 정책 |
| activity_exercise.md | 동일 폴더 | DataSourceType 공유, VWS 수면 차원 |
| _index.md | 동일 폴더 | DESIGN 참조 #95 수면개선 |

---

## 1. 개요

본 문서는 VAMOS 수면 관리 기능을 L3 구현 즉시 투입 가능 수준으로 정의한다. 수면 시간 기록, 수면 단계 분석(깊은 수면/REM/가벼운 수면), 수면 품질 점수 알고리즘(P-012-a), 수면 패턴 트렌드를 포함한다. 모든 수면 데이터는 PROTECTED 등급(LOCK-HW-02)으로 분류되며, AES-256-GCM(LOCK-HW-06) 암호화를 적용한다.

> **비의료 면책 (LOCK-HW-04)**: VAMOS는 의료 서비스가 아닙니다. 수면 분석 결과는 참고용이며, 수면 장애 진단이나 치료 목적으로 사용할 수 없습니다. 수면 문제가 지속되면 전문 의료인과 상담하십시오.

---

## 2. LOCK 인용

> LOCK (LOCK-HW-02, 기존 명세 §1/P-018): 감정=PRIVATE(로컬전용), 건강=PROTECTED(AES-256+별도PIN), 의료=HIGHEST(외부전송절대금지)

> LOCK (LOCK-HW-03, 기존 명세 §4): 원시건강데이터 24시간TTL, 집계데이터 90일, 감정로그 사용자설정(기본180일)

> LOCK (LOCK-HW-04, STEP7-P 윤리원칙): "VAMOS는 의료 서비스가 아닙니다" 모든 건강 관련 응답에 포함

> LOCK (LOCK-HW-06, 기존 명세 §4): 건강 데이터 저장 시 AES-256-GCM 필수

---

## 3. 데이터 모델 (P-012)

### 3.1 수면 기록 구조

```python
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
from datetime import datetime, date, time
# DataSourceType: activity_exercise.md §3.1에서 정의 (공유 Enum)
from health_data.activity_exercise import DataSourceType

class SleepStage(Enum):
    """수면 단계 분류"""
    AWAKE = "awake"
    LIGHT = "light"          # 가벼운 수면 (N1/N2)
    DEEP = "deep"            # 깊은 수면 (N3/SWS)
    REM = "rem"              # REM 수면

@dataclass
class SleepStageSegment:
    """
    수면 단계 구간.
    시간복잡도: O(1) per segment creation
    """
    stage: SleepStage
    start_time: str          # ISO 8601
    end_time: str            # ISO 8601
    duration_min: int

@dataclass
class SleepRecord:
    """
    수면 기록 (상세명세 §4.1 SleepData 확장).
    
    프라이버시 등급: PROTECTED (LOCK-HW-02)
    암호화: AES-256-GCM (LOCK-HW-06)
    보존 기간: 원시 24h, 집계 90일 (LOCK-HW-03)
    """
    record_id: str                          # "SLP-{date}-{user_id}"
    user_id: str
    record_date: date
    
    # 기본 수면 정보
    sleep_time: time                        # 취침 시각
    wake_time: time                         # 기상 시각
    total_hours: float                      # 총 수면 시간
    
    # 수면 단계 분석
    deep_sleep_min: int = 0                 # 깊은 수면 (분)
    rem_sleep_min: int = 0                  # REM 수면 (분)
    light_sleep_min: int = 0               # 가벼운 수면 (분)
    awake_count: int = 0                    # 중간 기상 횟수
    awake_total_min: int = 0               # 중간 기상 총 시간 (분)
    
    # 수면 단계 타임라인 (V1: 수동 입력 시 비어 있을 수 있음)
    stage_segments: list[SleepStageSegment] = field(default_factory=list)
    
    # 수면 품질 점수 (P-012-a)
    quality_score: Optional[float] = None   # 0.0~100.0
    quality_grade: Optional[str] = None     # "excellent" | "good" | "fair" | "poor"
    
    # 환경 메모 (선택)
    notes: Optional[str] = None             # "카페인 섭취", "늦은 운동" 등
    
    # 메타
    source: DataSourceType = DataSourceType.MANUAL  # activity_exercise.md DataSourceType 공유
    encrypted: bool = True                  # LOCK-HW-06 필수
    
    @property
    def sleep_efficiency(self) -> float:
        """수면 효율 (%) = (실제 수면 / 침대 시간) * 100"""
        total_bed_min = self.total_hours * 60
        if total_bed_min <= 0:
            return 0.0
        actual_sleep_min = total_bed_min - self.awake_total_min
        return max(0.0, min(100.0, (actual_sleep_min / total_bed_min) * 100))
```

### 3.2 수면 품질 점수 알고리즘 (P-012-a)

```python
class SleepQualityScorer:
    """
    수면 품질 점수 산출 알고리즘.
    
    5가지 구성 요소를 가중 합산하여 0-100점 산출.
    
    시간복잡도: O(1) per scoring
    공간복잡도: O(1)
    
    NOTE (LOCK-HW-04): 수면 품질 점수는 참고용이며
    수면 장애 진단 도구가 아닙니다.
    """
    
    # 가중치 (총합 1.0)
    WEIGHTS = {
        "duration": 0.25,       # 총 수면 시간 적절성
        "efficiency": 0.20,     # 수면 효율 (깨지 않은 비율)
        "deep_sleep": 0.25,     # 깊은 수면 비율
        "rem_sleep": 0.15,      # REM 수면 비율
        "consistency": 0.15,    # 취침/기상 시간 일관성
    }
    
    # 적정 범위 (성인 기준)
    OPTIMAL_RANGES = {
        "duration_hours": (7.0, 9.0),       # 7~9시간
        "efficiency_pct": (85.0, 100.0),    # 85% 이상
        "deep_sleep_pct": (13.0, 23.0),     # 13~23%
        "rem_sleep_pct": (20.0, 25.0),      # 20~25%
    }
    
    def score(
        self,
        record: SleepRecord,
        recent_records: Optional[list[SleepRecord]] = None,
    ) -> tuple[float, str]:
        """
        수면 품질 점수 산출.
        
        Args:
            record: 당일 수면 기록
            recent_records: 최근 7일 기록 (일관성 점수용, 선택)
            
        Returns:
            (score: 0.0~100.0, grade: "excellent"|"good"|"fair"|"poor")
        """
        scores = {
            "duration": self._score_duration(record.total_hours),
            "efficiency": self._score_efficiency(record.sleep_efficiency),
            "deep_sleep": self._score_deep_sleep(record),
            "rem_sleep": self._score_rem_sleep(record),
            "consistency": self._score_consistency(record, recent_records or []),
        }
        
        total = sum(
            scores[k] * self.WEIGHTS[k] for k in self.WEIGHTS
        )
        
        grade = self._to_grade(total)
        return round(total, 1), grade
    
    def _score_duration(self, total_hours: float) -> float:
        """수면 시간 점수 (0-100)"""
        lo, hi = self.OPTIMAL_RANGES["duration_hours"]
        if lo <= total_hours <= hi:
            return 100.0
        elif total_hours < lo:
            return max(0.0, 100.0 - (lo - total_hours) * 20)
        else:
            return max(0.0, 100.0 - (total_hours - hi) * 15)
    
    def _score_efficiency(self, efficiency_pct: float) -> float:
        """수면 효율 점수 (0-100)"""
        lo, _ = self.OPTIMAL_RANGES["efficiency_pct"]
        if efficiency_pct >= lo:
            return 100.0
        return max(0.0, efficiency_pct / lo * 100)
    
    def _score_deep_sleep(self, record: SleepRecord) -> float:
        """깊은 수면 비율 점수 (0-100)"""
        total_min = record.total_hours * 60
        if total_min <= 0:
            return 0.0
        deep_pct = (record.deep_sleep_min / total_min) * 100
        lo, hi = self.OPTIMAL_RANGES["deep_sleep_pct"]
        if lo <= deep_pct <= hi:
            return 100.0
        elif deep_pct < lo:
            return max(0.0, deep_pct / lo * 100)
        else:
            return max(0.0, 100.0 - (deep_pct - hi) * 5)
    
    def _score_rem_sleep(self, record: SleepRecord) -> float:
        """REM 수면 비율 점수 (0-100)"""
        total_min = record.total_hours * 60
        if total_min <= 0:
            return 0.0
        rem_pct = (record.rem_sleep_min / total_min) * 100
        lo, hi = self.OPTIMAL_RANGES["rem_sleep_pct"]
        if lo <= rem_pct <= hi:
            return 100.0
        elif rem_pct < lo:
            return max(0.0, rem_pct / lo * 100)
        else:
            return max(0.0, 100.0 - (rem_pct - hi) * 5)
    
    def _score_consistency(
        self, record: SleepRecord, recent: list[SleepRecord]
    ) -> float:
        """취침/기상 시간 일관성 점수 (0-100)"""
        if len(recent) < 3:
            return 70.0  # 데이터 부족 시 중간값
        
        # 취침 시각 표준편차 (분 단위)
        sleep_minutes = [self._time_to_minutes(r.sleep_time) for r in recent]
        wake_minutes = [self._time_to_minutes(r.wake_time) for r in recent]
        
        sleep_std = self._std(sleep_minutes)
        wake_std = self._std(wake_minutes)
        avg_std = (sleep_std + wake_std) / 2
        
        # 표준편차 30분 이하 → 100점, 120분 이상 → 0점
        if avg_std <= 30:
            return 100.0
        elif avg_std >= 120:
            return 0.0
        else:
            return 100.0 - (avg_std - 30) / 90 * 100
    
    def _time_to_minutes(self, t: time) -> int:
        """시각을 자정 기준 분으로 변환 (자정 이후 처리)"""
        minutes = t.hour * 60 + t.minute
        if minutes < 360:  # 오전 6시 이전 → 전날 밤으로 간주
            minutes += 1440
        return minutes
    
    def _std(self, values: list[int]) -> float:
        """표준편차 산출"""
        n = len(values)
        if n < 2:
            return 0.0
        mean = sum(values) / n
        variance = sum((v - mean) ** 2 for v in values) / (n - 1)
        return variance ** 0.5
    
    def _to_grade(self, score: float) -> str:
        """점수 → 등급 변환"""
        if score >= 85:
            return "excellent"
        elif score >= 70:
            return "good"
        elif score >= 50:
            return "fair"
        else:
            return "poor"
```

---

## 4. 수면 인사이트 엔진

```python
class SleepInsightEngine:
    """
    수면 패턴 분석 및 인사이트 생성.
    
    시간복잡도: O(d) — d=분석 기간 일 수
    
    NOTE (LOCK-HW-04): 수면 인사이트는 참고용이며
    수면 장애 진단이나 치료 권고가 아닙니다.
    """
    
    DISCLAIMER = (
        "VAMOS는 의료 서비스가 아닙니다. "
        "이 수면 분석은 참고용이며, 수면 문제가 지속되면 "
        "전문 의료인과 상담하십시오."
    )  # LOCK-HW-04
    
    def analyze_weekly(self, records: list[SleepRecord]) -> dict:
        """
        주간 수면 트렌드 분석.
        
        Returns:
            {
                "avg_hours": float,
                "avg_quality": float,
                "avg_efficiency": float,
                "deep_sleep_avg_pct": float,
                "consistency_score": float,
                "trend": "improving" | "stable" | "declining",
                "insights": list[str],
                "disclaimer": str,
            }
        """
        if not records:
            return {"error": "no_data", "disclaimer": self.DISCLAIMER}
        
        avg_hours = sum(r.total_hours for r in records) / len(records)
        avg_quality = sum(
            r.quality_score for r in records if r.quality_score is not None
        ) / max(sum(1 for r in records if r.quality_score is not None), 1)
        avg_efficiency = sum(r.sleep_efficiency for r in records) / len(records)
        
        insights = []
        if avg_hours < 7.0:
            insights.append("평균 수면 시간이 7시간 미만입니다. 취침 시간을 앞당겨 보세요.")
        if avg_efficiency < 85.0:
            insights.append("수면 효율이 85% 미만입니다. 침대에서 수면 외 활동을 줄여 보세요.")
        
        return {
            "avg_hours": round(avg_hours, 1),
            "avg_quality": round(avg_quality, 1),
            "avg_efficiency": round(avg_efficiency, 1),
            "insights": insights,
            "disclaimer": self.DISCLAIMER,
        }
```

---

## 5. 수면 데이터 저장 파이프라인

```python
class SleepDataPipeline:
    """
    수면 데이터 수집 → 점수 산출 → 암호화 → 저장 파이프라인.
    
    LOCK-HW-06: AES-256-GCM 암호화 필수
    LOCK-HW-03: 원시 24h TTL, 집계 90일
    LOCK-HW-02: PROTECTED 등급
    """
    
    PRIVACY_LEVEL = "PROTECTED"
    ENCRYPTION = "AES-256-GCM"
    RAW_DATA_TTL_HOURS = 24
    AGGREGATE_RETENTION_DAYS = 90
    
    def __init__(self):
        self.scorer = SleepQualityScorer()
    
    async def ingest(self, record: SleepRecord) -> str:
        """수면 기록 수집 + 품질 점수 산출 + 암호화 저장"""
        # 1. 품질 점수 산출 (P-012-a)
        recent = await self._fetch_recent(record.user_id, days=7)
        score, grade = self.scorer.score(record, recent)
        record.quality_score = score
        record.quality_grade = grade
        
        # 2. 검증
        self._validate(record)
        
        # 3. AES-256-GCM 암호화 (LOCK-HW-06)
        encrypted = self._encrypt(record)
        
        # 4. PROTECTED 등급 저장
        record_id = await self._store(
            encrypted,
            privacy_level=self.PRIVACY_LEVEL,
            ttl_hours=self.RAW_DATA_TTL_HOURS,
        )
        
        # 5. 로깅
        self._log(record_id, record)
        
        return record_id
    
    def _validate(self, record: SleepRecord) -> None:
        if record.total_hours < 0 or record.total_hours > 24:
            raise ValueError("total_hours must be 0-24")
        if not record.encrypted:
            raise SecurityError("LOCK-HW-06: 암호화 미적용")
    
    def _encrypt(self, record: SleepRecord) -> bytes:
        """AES-256-GCM 암호화"""
        ...
    
    async def _store(self, payload: bytes, privacy_level: str, ttl_hours: int) -> str:
        ...
    
    async def _fetch_recent(self, user_id: str, days: int) -> list[SleepRecord]:
        ...
    
    def _log(self, record_id: str, record: SleepRecord) -> None:
        ...
```

---

## 6. VWS 연동 인터페이스

```python
class SleepVWSContributor:
    """
    수면 데이터 → VWS 웰니스 점수 수면 차원 기여.
    
    LOCK-HW-11: 수면 차원 0-20점.
    05_emotion-journal/wellness_score.md 에서 소비.
    """
    
    def compute_sleep_score(self, record: SleepRecord) -> int:
        """
        일일 수면 점수 산출 (0-20).
        
        산출 공식:
        - 수면 시간 적절성: min(abs(total_hours - 8) 역수, 1.0) * 8  (최대 8점)
        - 수면 품질 점수 기여: (quality_score / 100) * 7  (최대 7점)
        - 수면 효율 기여: (efficiency / 100) * 5  (최대 5점)
        - 총점: 합산 후 round, min(20, score)
        """
        # 수면 시간 적절성 (8시간 기준, 편차 클수록 감점)
        deviation = abs(record.total_hours - 8.0)
        duration_score = max(0, 1.0 - deviation / 4.0) * 8
        
        # 수면 품질
        quality = record.quality_score if record.quality_score is not None else 50.0
        quality_score = (quality / 100.0) * 7
        
        # 수면 효율
        efficiency_score = (record.sleep_efficiency / 100.0) * 5
        
        total = round(duration_score + quality_score + efficiency_score)
        return min(20, max(0, total))
```

---

## 7. R-01-7 중첩 JSON 로깅

```json
{
  "trace_id": "hlth-slp-{uuid}",
  "event": "sleep_data_ingested",
  "context": {
    "module": "health_data.sleep_management",
    "user_id": "{user_uuid}",
    "record_date": "2026-04-10",
    "source": "manual",
    "privacy_level": "PROTECTED",
    "encryption": "AES-256-GCM"
  },
  "data": {
    "total_hours": 7.5,
    "deep_sleep_min": 85,
    "rem_sleep_min": 95,
    "light_sleep_min": 270,
    "awake_count": 2,
    "quality_score": 78.5,
    "quality_grade": "good"
  },
  "retention": {
    "raw_ttl_hours": 24,
    "aggregate_retention_days": 90,
    "policy": "LOCK-HW-03"
  },
  "timestamp": "2026-04-10T07:30:00Z"
}
```

---

## 8. 에스컬레이션 페이로드

```python
@dataclass
class SleepDataEscalationPayload:
    """수면 데이터 이상 에스컬레이션. I-20 경유 (R-01-8)."""
    escalation_id: str           # "ESC-SLP-{uuid}"
    severity: str                # "P1" | "P2"
    issue_type: str              # "encryption_failure" | "scoring_error" | "data_integrity"
    detail: str
    affected_records: int
    timestamp: str
    auto_action_taken: str
    
    def to_i20_payload(self) -> dict:
        return {
            "source": "health-wellness-emotionai/sleep-management",
            "escalation_id": self.escalation_id,
            "severity": self.severity,
            "category": "health_data_integrity",
            "detail": {
                "issue_type": self.issue_type,
                "description": self.detail,
                "affected_records": self.affected_records,
            },
            "auto_action": self.auto_action_taken,
            "timestamp": self.timestamp,
        }
```

---

## 9. 예외 처리 정책 표

| error_code | 설명 | recoverable | 처리 |
|-----------|------|-------------|------|
| SLP-001 | 암호화 실패 (LOCK-HW-06) | YES | 재시도 3회, 실패 시 저장 차단 |
| SLP-002 | 수면 시간 음수/24시간 초과 | YES | 클램핑 + 경고 로그 |
| SLP-003 | 품질 점수 산출 실패 | YES | 기본값 50 적용 + 경고 |
| SLP-004 | 원시 데이터 TTL 미삭제 | YES | 강제 삭제 + 집계 확인 |
| SLP-005 | 면책 문구 누락 (LOCK-HW-04) | YES | 강제 삽입, 실패 시 응답 차단 |
| SLP-006 | PROTECTED 데이터 외부 전송 시도 | NO | 즉시 차단 + P0 에스컬레이션 |
| SLP-007 | 수면 단계 합계 불일치 | YES | 자동 보정 + 경고 로그 |

---

## 10. Phase별 복구 전략

### Phase 1 (현재): 기본 복구

```
[수면 기록 실패]
  → 암호화 재시도 (3회)
  → 품질 점수 기본값 폴백
  → 로그 기록 + 에스컬레이션
```

### Phase 2: 자동 복구 강화

```
[수면 센서 연동 실패]
  → HealthKit 재연결
  → 오프라인 큐 → 복구 시 자동 반영
  → 수면 단계 보간 알고리즘
```

### 다운그레이드 시 confidence penalty 표

| 다운그레이드 상황 | penalty | 결과 |
|-----------------|---------|------|
| Phase 2 → Phase 1 | -0.2 | 자동 연동 비활성, 수동 입력만 |
| Phase 1 → 긴급 모드 | -0.5 | 수면 기록 중단, 기존 집계만 조회 |

---

## 11. Phase 2 테스트 시나리오

| # | 시나리오 | 입력/조건 | 기대 결과 | 관련 LOCK |
|---|---------|----------|----------|----------|
| T-SLP-01 | 수면 기록 저장 | 취침 23:00, 기상 07:00, 8h | AES-256-GCM 암호화 저장 성공 | HW-06 |
| T-SLP-02 | 품질 점수 산출 | 8h, 깊은 수면 90분, REM 100분 | 점수 75-85 범위, grade="good" | - |
| T-SLP-03 | 원시 데이터 TTL | 24h 경과 | 원시 삭제 + 집계 보존 | HW-03 |
| T-SLP-04 | 면책 문구 확인 | 수면 인사이트 응답 | LOCK-HW-04 문구 포함 | HW-04 |
| T-SLP-05 | 수면 효율 산출 | 8h 침대, 깨어남 30분 | 효율 93.75% | - |
| T-SLP-06 | 일관성 점수 | 7일 취침 시간 표준편차 15분 | 일관성 점수 100 | - |
| T-SLP-07 | 일관성 점수 (불규칙) | 7일 취침 시간 표준편차 90분 | 일관성 점수 33.3 | - |
| T-SLP-08 | VWS 수면 점수 산출 | 8h, 품질 80, 효율 90% | 0-20 점수 산출 확인 | HW-11 |
| T-SLP-09 | PROTECTED 외부 전송 차단 | HTTP POST 시도 | 차단 + 에스컬레이션 | HW-02 |
| T-SLP-10 | 수면 시간 24h 초과 | total_hours=25 | ValueError 발생 | - |
| T-SLP-11 | 품질 점수 산출 실패 폴백 | 잘못된 데이터 입력 | 기본값 50 적용 + 경고 로그 | - |
| T-SLP-12 | 수면 단계 합계 불일치 | deep+rem+light != total | 자동 보정 + 경고 | - |

---

## 12. 공통 자료 구조 선정의

| 클래스/Enum | 용도 | 참조 위치 |
|------------|------|----------|
| `SleepStage` | 수면 단계 4분류 | §3.1 |
| `SleepRecord` | 수면 기록 구조 | §3.1, VWS 연동 |
| `SleepQualityScorer` | 수면 품질 점수 알고리즘 | §3.2 (P-012-a) |
| `SleepVWSContributor` | VWS 수면 차원 기여 | §6 |
| `SleepDataEscalationPayload` | 에스컬레이션 | §8 |

---

## 13. 세션 간 인터페이스 cross-check

| 인터페이스 | 제공 측 | 소비 측 | 상태 |
|-----------|--------|--------|------|
| `SleepRecord` | 본 문서 (P-012) | wellness_score.md (P-027) | V1 정의 완료 |
| `SleepVWSContributor.compute_sleep_score()` | 본 문서 | 05_emotion-journal/wellness_score.md | V1 정의 완료 |
| `DataSourceType` | activity_exercise.md (P-011) | 본 문서 | V1 공유 |
| `SleepQualityScorer` | 본 문서 (P-012-a) | health_dashboard.md (V2) | V1 정의 완료 |

---

> **문서 끝** — sleep_management.md V1 L3 완성 (2026-04-10)
