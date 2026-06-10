# activity_exercise.md — 활동/운동 추적

> **P-ID**: P-011
> **V단계**: V1
> **상태**: EXTEND
> **L3 완성**: 2026-04-10
> **정본 소유자**: sot 2/3-6_Health-Wellness-EmotionAI/03_health-data/

---

## 교차 참조 블록

| 참조 문서 | 위치 | 참조 내용 |
|----------|------|----------|
| 종합계획서 §6.3 | P-011 | 활동/운동 추적 매핑 |
| 종합계획서 §3.4 | LOCK-HW-02/03/04/06 | LOCK 보호 값 |
| 상세명세 §4.1 | ExerciseData, ExerciseActivity | 기존 데이터 모델 |
| 상세명세 §4.2 | HealthKitSync | Apple HealthKit 연동 명세 |
| STEP7-P | P-011 | 활동/운동 추적 원본 |
| AUTHORITY_CHAIN.md | §1~§5 | 정본 계층 및 충돌 해결 |
| health_data_privacy.md | 동일 폴더 | 프라이버시 등급 및 암호화 정책 |
| ethics_framework.md | 06_ethics-privacy/ | 비의료 면책 + 7원칙 |
| _index.md | 동일 폴더 | DESIGN 참조 #96 운동/피트니스 |

---

## 1. 개요

본 문서는 VAMOS 활동/운동 추적 기능을 L3 구현 즉시 투입 가능 수준으로 정의한다. 사용자의 일일 활동량(걸음 수, 활동 시간), 운동 기록(유형, 강도, 칼로리), HealthKit/Google Fit 연동 인터페이스를 포함한다. 모든 건강 데이터는 PROTECTED 등급(LOCK-HW-02)으로 분류되며, AES-256-GCM(LOCK-HW-06) 암호화와 원시 데이터 24시간 TTL(LOCK-HW-03)을 적용한다.

> **비의료 면책 (LOCK-HW-04)**: VAMOS는 의료 서비스가 아닙니다. 활동/운동 추적 데이터는 참고용이며, 의학적 판단이나 치료 목적으로 사용할 수 없습니다. 건강 관련 의사결정은 반드시 전문 의료인과 상담하십시오.

---

## 2. LOCK 인용

> LOCK (LOCK-HW-02, 기존 명세 §1/P-018): 감정=PRIVATE(로컬전용), 건강=PROTECTED(AES-256+별도PIN), 의료=HIGHEST(외부전송절대금지)

> LOCK (LOCK-HW-03, 기존 명세 §4): 원시건강데이터 24시간TTL, 집계데이터 90일, 감정로그 사용자설정(기본180일)

> LOCK (LOCK-HW-04, STEP7-P 윤리원칙): "VAMOS는 의료 서비스가 아닙니다" 모든 건강 관련 응답에 포함

> LOCK (LOCK-HW-06, 기존 명세 §4): 건강 데이터 저장 시 AES-256-GCM 필수

---

## 3. 데이터 모델 (P-011)

### 3.1 활동 기록 구조

```python
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
from datetime import datetime, date

class SecurityError(Exception):
    """보안 정책 위반 (LOCK-HW-06 등). health_data_privacy.md 와 동일 의미."""
    pass

class ExerciseIntensity(Enum):
    """운동 강도 등급"""
    LIGHT = "light"         # 가벼운 걷기, 스트레칭
    MODERATE = "moderate"   # 빠른 걷기, 자전거
    VIGOROUS = "vigorous"   # 달리기, 고강도 인터벌

class DataSourceType(Enum):
    """데이터 소스 유형"""
    MANUAL = "manual"
    HEALTHKIT = "healthkit"
    GOOGLE_FIT = "google_fit"
    SAMSUNG_HEALTH = "samsung_health"
    FITBIT = "fitbit"

@dataclass
class ExerciseActivity:
    """
    개별 운동 활동 기록.
    
    상세명세 §4.1 ExerciseActivity 확장.
    프라이버시 등급: PROTECTED (LOCK-HW-02)
    """
    activity_id: str                        # "ACT-{uuid}"
    exercise_type: str                      # "running", "weight_training", "yoga", "swimming"
    duration_min: int                       # 운동 시간 (분)
    calories_burned: float                  # 소모 칼로리 (kcal)
    intensity: ExerciseIntensity
    heart_rate_avg: Optional[int] = None    # 평균 심박수 (bpm)
    heart_rate_max: Optional[int] = None    # 최대 심박수 (bpm)
    distance_m: Optional[float] = None      # 이동 거리 (미터)
    started_at: Optional[str] = None        # ISO 8601
    ended_at: Optional[str] = None          # ISO 8601
    source: DataSourceType = DataSourceType.MANUAL
    notes: Optional[str] = None

@dataclass
class DailyActivityRecord:
    """
    일일 활동 종합 기록.
    
    시간복잡도: 기록 조회 O(1), 활동 추가 O(1) amortized
    공간복잡도: O(n) — n=일일 운동 활동 수 (일반적 n < 10)
    프라이버시 등급: PROTECTED (LOCK-HW-02)
    암호화: AES-256-GCM (LOCK-HW-06)
    보존 기간: 원시 24h, 집계 90일 (LOCK-HW-03)
    """
    record_id: str                          # "DAR-{date}-{user_id}"
    user_id: str
    record_date: date
    
    # 일일 종합 지표
    total_steps: int = 0                    # 총 걸음 수
    total_active_minutes: int = 0           # 총 활동 시간 (분)
    total_calories_burned: float = 0.0      # 총 소모 칼로리
    total_distance_m: float = 0.0           # 총 이동 거리
    
    # 개별 운동 활동 목록
    activities: list[ExerciseActivity] = field(default_factory=list)
    
    # 목표 달성률
    step_goal: int = 10000                  # 기본 목표: 10,000보
    active_minutes_goal: int = 30           # 기본 목표: 30분
    
    # 메타
    source: DataSourceType = DataSourceType.MANUAL
    last_synced_at: Optional[str] = None
    created_at: str = ""
    encrypted: bool = True                  # LOCK-HW-06 필수
    
    @property
    def step_goal_ratio(self) -> float:
        """걸음 수 목표 달성률 (0.0~1.0+)"""
        if self.step_goal <= 0:
            return 0.0
        return self.total_steps / self.step_goal
    
    @property
    def active_minutes_goal_ratio(self) -> float:
        """활동 시간 목표 달성률 (0.0~1.0+)"""
        if self.active_minutes_goal <= 0:
            return 0.0
        return self.total_active_minutes / self.active_minutes_goal
    
    def add_activity(self, activity: ExerciseActivity) -> None:
        """
        운동 활동 추가 및 종합 지표 자동 갱신.
        
        시간복잡도: O(1) amortized
        """
        self.activities.append(activity)
        self.total_active_minutes += activity.duration_min
        self.total_calories_burned += activity.calories_burned
        if activity.distance_m:
            self.total_distance_m += activity.distance_m
```

### 3.2 운동 유형 카탈로그

```python
EXERCISE_CATALOG = {
    "running": {
        "name_ko": "달리기",
        "category": "cardio",
        "default_intensity": ExerciseIntensity.VIGOROUS,
        "met_value": 9.8,  # MET 값 (칼로리 추정용)
    },
    "walking": {
        "name_ko": "걷기",
        "category": "cardio",
        "default_intensity": ExerciseIntensity.LIGHT,
        "met_value": 3.5,
    },
    "cycling": {
        "name_ko": "자전거",
        "category": "cardio",
        "default_intensity": ExerciseIntensity.MODERATE,
        "met_value": 7.5,
    },
    "swimming": {
        "name_ko": "수영",
        "category": "cardio",
        "default_intensity": ExerciseIntensity.VIGOROUS,
        "met_value": 8.0,
    },
    "weight_training": {
        "name_ko": "근력 운동",
        "category": "strength",
        "default_intensity": ExerciseIntensity.MODERATE,
        "met_value": 6.0,
    },
    "yoga": {
        "name_ko": "요가",
        "category": "flexibility",
        "default_intensity": ExerciseIntensity.LIGHT,
        "met_value": 3.0,
    },
    "hiit": {
        "name_ko": "고강도 인터벌",
        "category": "cardio",
        "default_intensity": ExerciseIntensity.VIGOROUS,
        "met_value": 12.0,
    },
    "stretching": {
        "name_ko": "스트레칭",
        "category": "flexibility",
        "default_intensity": ExerciseIntensity.LIGHT,
        "met_value": 2.5,
    },
}
```

### 3.3 칼로리 추정 엔진

```python
class CalorieEstimator:
    """
    MET 기반 칼로리 소모량 추정.
    
    공식: 칼로리(kcal) = MET * 체중(kg) * 시간(h)
    시간복잡도: O(1) per estimation
    
    NOTE (LOCK-HW-04): 이 추정값은 참고용이며 의학적 판단에 사용할 수 없습니다.
    """
    
    def estimate(
        self,
        exercise_type: str,
        duration_min: int,
        body_weight_kg: float,
        intensity_override: Optional[ExerciseIntensity] = None,
    ) -> float:
        """
        운동 칼로리 소모량 추정.
        
        Args:
            exercise_type: EXERCISE_CATALOG 키
            duration_min: 운동 시간 (분)
            body_weight_kg: 사용자 체중 (kg)
            intensity_override: 강도 오버라이드 (선택)
            
        Returns:
            추정 칼로리 소모량 (kcal)
        """
        catalog_entry = EXERCISE_CATALOG.get(exercise_type)
        if not catalog_entry:
            # 미등록 운동 → 기본 MET 4.0 (중간 강도)
            met = 4.0
        else:
            met = catalog_entry["met_value"]
            
        # 강도에 따른 MET 보정
        if intensity_override:
            met = self._adjust_met_by_intensity(met, intensity_override)
        
        duration_hours = duration_min / 60.0
        return met * body_weight_kg * duration_hours
    
    def _adjust_met_by_intensity(
        self, base_met: float, intensity: ExerciseIntensity
    ) -> float:
        """강도별 MET 보정 계수 적용"""
        INTENSITY_FACTOR = {
            ExerciseIntensity.LIGHT: 0.7,
            ExerciseIntensity.MODERATE: 1.0,
            ExerciseIntensity.VIGOROUS: 1.3,
        }
        return base_met * INTENSITY_FACTOR[intensity]
```

---

## 4. HealthKit/Google Fit 연동 인터페이스 (V1 기초)

### 4.1 동기화 엔진

```python
from abc import ABC, abstractmethod

class HealthDataSyncAdapter(ABC):
    """
    외부 건강 플랫폼 동기화 어댑터 추상 클래스.
    V1에서는 동기화 인터페이스 정의 + 수동 입력 지원.
    V2에서 HealthKit/Google Fit 실 연동 (P-011-a).
    
    프라이버시: PROTECTED (LOCK-HW-02) — AES-256+별도PIN
    보존: 원시 24h TTL, 집계 90일 (LOCK-HW-03)
    """
    
    @abstractmethod
    async def sync(self, user_id: str, since: datetime) -> list[DailyActivityRecord]:
        """지정 시각 이후의 활동 데이터 동기화"""
        ...
    
    @abstractmethod
    async def get_permissions(self) -> list[str]:
        """필요 권한 목록 반환"""
        ...
    
    @abstractmethod
    async def revoke_access(self, user_id: str) -> bool:
        """연동 해제 및 데이터 접근 권한 철회"""
        ...

class ManualInputAdapter(HealthDataSyncAdapter):
    """
    수동 입력 어댑터 (V1 기본).
    사용자가 직접 활동 데이터를 입력한다.
    """
    
    async def sync(self, user_id: str, since: datetime) -> list[DailyActivityRecord]:
        # V1: 수동 입력만 지원 → 동기화 대상 없음
        return []
    
    async def get_permissions(self) -> list[str]:
        return ["manual_input"]
    
    async def revoke_access(self, user_id: str) -> bool:
        return True  # 수동 입력은 연동 해제 불필요

class HealthKitAdapter(HealthDataSyncAdapter):
    """
    Apple HealthKit 어댑터 (V2 대상, P-011-a).
    V1에서는 인터페이스만 정의하고 NotImplementedError 반환.
    
    동기화 카테고리 (상세명세 §4.2):
    - sleep_analysis: 6시간 주기
    - step_count: 1시간 주기
    - heart_rate: 1시간 주기
    - active_energy: 1시간 주기
    """
    
    SYNC_CATEGORIES = {
        "sleep_analysis": {"hk_type": "HKCategoryTypeIdentifierSleepAnalysis", "interval_h": 6},
        "step_count": {"hk_type": "HKQuantityTypeIdentifierStepCount", "interval_h": 1},
        "heart_rate": {"hk_type": "HKQuantityTypeIdentifierHeartRate", "interval_h": 1},
        "active_energy": {"hk_type": "HKQuantityTypeIdentifierActiveEnergyBurned", "interval_h": 1},
    }
    
    async def sync(self, user_id: str, since: datetime) -> list[DailyActivityRecord]:
        raise NotImplementedError("V2 구현 예정 (P-011-a)")
    
    async def get_permissions(self) -> list[str]:
        return list(self.SYNC_CATEGORIES.keys())
    
    async def revoke_access(self, user_id: str) -> bool:
        raise NotImplementedError("V2 구현 예정 (P-011-a)")

class GoogleFitAdapter(HealthDataSyncAdapter):
    """
    Google Fit 어댑터 (V2 대상, P-011-a).
    V1에서는 인터페이스만 정의.
    """
    
    async def sync(self, user_id: str, since: datetime) -> list[DailyActivityRecord]:
        raise NotImplementedError("V2 구현 예정 (P-011-a)")
    
    async def get_permissions(self) -> list[str]:
        return ["activity", "body", "sleep"]
    
    async def revoke_access(self, user_id: str) -> bool:
        raise NotImplementedError("V2 구현 예정 (P-011-a)")
```

### 4.2 데이터 저장 파이프라인

```python
class ActivityDataPipeline:
    """
    활동 데이터 수집 → 암호화 → 저장 → TTL 관리 파이프라인.
    
    LOCK-HW-06: AES-256-GCM 암호화 필수
    LOCK-HW-03: 원시 24h TTL, 집계 90일
    LOCK-HW-02: PROTECTED 등급
    
    시간복잡도: O(n) per daily aggregation — n=일일 활동 수
    """
    
    PRIVACY_LEVEL = "PROTECTED"         # LOCK-HW-02
    ENCRYPTION = "AES-256-GCM"          # LOCK-HW-06
    RAW_DATA_TTL_HOURS = 24             # LOCK-HW-03
    AGGREGATE_RETENTION_DAYS = 90       # LOCK-HW-03
    
    async def ingest(self, record: DailyActivityRecord) -> str:
        """
        활동 기록 수집 및 암호화 저장.
        
        Returns:
            저장된 record_id
        """
        # 1. 데이터 검증
        self._validate(record)
        
        # 2. AES-256-GCM 암호화 (LOCK-HW-06)
        encrypted_payload = self._encrypt(record)
        
        # 3. PROTECTED 등급 저장 (LOCK-HW-02: AES-256 + 별도 PIN)
        record_id = await self._store_encrypted(
            encrypted_payload,
            privacy_level=self.PRIVACY_LEVEL,
            ttl_hours=self.RAW_DATA_TTL_HOURS,
        )
        
        # 4. 로깅 (R-01-7)
        self._log_ingestion(record_id, record.user_id)
        
        return record_id
    
    async def aggregate_daily(self, user_id: str, target_date: date) -> dict:
        """
        일일 활동 데이터 집계 (원시 → 집계 변환).
        원시 데이터 24h TTL 만료 전에 집계 수행.
        집계 데이터는 90일 보존 (LOCK-HW-03).
        """
        raw_records = await self._fetch_raw(user_id, target_date)
        
        aggregate = {
            "date": target_date.isoformat(),
            "total_steps": sum(r.total_steps for r in raw_records),
            "total_active_minutes": sum(r.total_active_minutes for r in raw_records),
            "total_calories": sum(r.total_calories_burned for r in raw_records),
            "total_distance_m": sum(r.total_distance_m for r in raw_records),
            "activity_count": sum(len(r.activities) for r in raw_records),
            "step_goal_achieved": any(r.step_goal_ratio >= 1.0 for r in raw_records),
        }
        
        await self._store_aggregate(
            user_id, aggregate,
            retention_days=self.AGGREGATE_RETENTION_DAYS,
        )
        
        return aggregate
    
    def _validate(self, record: DailyActivityRecord) -> None:
        """입력 검증"""
        if record.total_steps < 0:
            raise ValueError("total_steps must be >= 0")
        if record.total_active_minutes < 0:
            raise ValueError("total_active_minutes must be >= 0")
        if not record.encrypted:
            raise SecurityError("LOCK-HW-06: 암호화 미적용 데이터 저장 불가")
    
    def _encrypt(self, record: DailyActivityRecord) -> bytes:
        """AES-256-GCM 암호화 (LOCK-HW-06)"""
        # 구현: AES-256-GCM 암호화 적용
        ...
    
    async def _store_encrypted(self, payload: bytes, privacy_level: str, ttl_hours: int) -> str:
        """암호화된 데이터 저장"""
        ...
    
    async def _fetch_raw(self, user_id: str, target_date: date) -> list[DailyActivityRecord]:
        """원시 데이터 조회"""
        ...
    
    async def _store_aggregate(self, user_id: str, aggregate: dict, retention_days: int) -> None:
        """집계 데이터 저장"""
        ...
    
    def _log_ingestion(self, record_id: str, user_id: str) -> None:
        """R-01-7 중첩 JSON 로깅"""
        ...
```

---

## 5. 활동 분석 및 인사이트

```python
class ActivityInsightEngine:
    """
    활동 패턴 분석 및 인사이트 생성.
    
    시간복잡도: O(d) — d=분석 기간 (일 수, 기본 7~30일)
    
    NOTE (LOCK-HW-04): 분석 결과는 참고용이며
    의학적 판단이나 운동 처방으로 사용할 수 없습니다.
    """
    
    DISCLAIMER = (
        "VAMOS는 의료 서비스가 아닙니다. "
        "이 분석 결과는 참고용이며, 운동 프로그램 변경 시 "
        "전문 의료인과 상담하십시오."
    )  # LOCK-HW-04
    
    def analyze_weekly_trend(self, records: list[DailyActivityRecord]) -> dict:
        """
        주간 활동 트렌드 분석.
        
        Returns:
            {
                "avg_steps": int,
                "avg_active_minutes": int,
                "avg_calories": float,
                "goal_achievement_rate": float,  # 0.0~1.0
                "trend": "improving" | "stable" | "declining",
                "disclaimer": str,  # LOCK-HW-04
            }
        """
        if not records:
            return {"error": "no_data", "disclaimer": self.DISCLAIMER}
        
        avg_steps = sum(r.total_steps for r in records) / len(records)
        avg_active = sum(r.total_active_minutes for r in records) / len(records)
        avg_calories = sum(r.total_calories_burned for r in records) / len(records)
        goal_rate = sum(1 for r in records if r.step_goal_ratio >= 1.0) / len(records)
        
        # 트렌드 판정 (전반 vs 후반 비교)
        mid = len(records) // 2
        first_half_avg = sum(r.total_steps for r in records[:mid]) / max(mid, 1)
        second_half_avg = sum(r.total_steps for r in records[mid:]) / max(len(records) - mid, 1)
        
        if second_half_avg > first_half_avg * 1.1:
            trend = "improving"
        elif second_half_avg < first_half_avg * 0.9:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "avg_steps": int(avg_steps),
            "avg_active_minutes": int(avg_active),
            "avg_calories": round(avg_calories, 1),
            "goal_achievement_rate": round(goal_rate, 2),
            "trend": trend,
            "disclaimer": self.DISCLAIMER,
        }
    
    def generate_recommendation(self, weekly_analysis: dict) -> str:
        """
        활동 기반 추천 생성.
        
        LOCK-HW-04: 모든 추천에 비의료 면책 문구 포함.
        LOCK-HW-09 원칙1(비진단): 의학적 조언 금지.
        """
        trend = weekly_analysis.get("trend", "stable")
        goal_rate = weekly_analysis.get("goal_achievement_rate", 0)
        
        if goal_rate >= 0.8:
            msg = "이번 주 활동 목표를 잘 달성하셨습니다! 현재 페이스를 유지해보세요."
        elif goal_rate >= 0.5:
            msg = "절반 이상 목표를 달성하셨습니다. 조금만 더 움직여볼까요?"
        else:
            msg = "이번 주는 활동이 적었네요. 짧은 산책부터 시작해보는 건 어떨까요?"
        
        return f"{msg}\n\n{self.DISCLAIMER}"
```

---

## 6. VWS 연동 인터페이스

```python
class ActivityVWSContributor:
    """
    활동 데이터 → VWS 웰니스 점수 운동 차원 기여.
    
    LOCK-HW-11: 운동 차원 0-20점.
    05_emotion-journal/wellness_score.md 에서 소비.
    """
    
    def compute_exercise_score(self, daily_record: DailyActivityRecord) -> int:
        """
        일일 운동 점수 산출 (0-20).
        
        산출 공식:
        - 걸음 수 기여: min(total_steps / 10000, 1.0) * 8  (최대 8점)
        - 활동 시간 기여: min(active_minutes / 30, 1.0) * 7  (최대 7점)
        - 운동 다양성 기여: min(len(activities), 3) / 3 * 5  (최대 5점)
        - 총점: 합산 후 round, min(20, score)
        """
        step_score = min(daily_record.total_steps / 10000, 1.0) * 8
        active_score = min(daily_record.total_active_minutes / 30, 1.0) * 7
        variety_score = min(len(daily_record.activities), 3) / 3 * 5
        
        total = round(step_score + active_score + variety_score)
        return min(20, max(0, total))
```

---

## 7. R-01-7 중첩 JSON 로깅

```json
{
  "trace_id": "hlth-act-{uuid}",
  "event": "activity_data_ingested",
  "context": {
    "module": "health_data.activity_exercise",
    "user_id": "{user_uuid}",
    "record_date": "2026-04-10",
    "source": "manual",
    "privacy_level": "PROTECTED",
    "encryption": "AES-256-GCM"
  },
  "data": {
    "total_steps": 8542,
    "total_active_minutes": 45,
    "total_calories": 320.5,
    "activities_count": 2,
    "step_goal_ratio": 0.85
  },
  "retention": {
    "raw_ttl_hours": 24,
    "aggregate_retention_days": 90,
    "policy": "LOCK-HW-03"
  },
  "timestamp": "2026-04-10T09:00:00Z"
}
```

---

## 8. 에스컬레이션 페이로드

```python
@dataclass
class ActivityDataEscalationPayload:
    """
    활동 데이터 이상 에스컬레이션 페이로드.
    I-20 경유 (R-01-8).
    """
    escalation_id: str           # "ESC-ACT-{uuid}"
    severity: str                # "P1" | "P2"
    issue_type: str              # "encryption_failure" | "ttl_violation" | "sync_error"
    detail: str
    affected_records: int
    timestamp: str
    auto_action_taken: str
    
    def to_i20_payload(self) -> dict:
        return {
            "source": "health-wellness-emotionai/activity-exercise",
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
| ACT-001 | 암호화 실패 (LOCK-HW-06 위반) | YES | 재시도 3회, 실패 시 저장 차단 + 에스컬레이션 |
| ACT-002 | 원시 데이터 TTL 초과 미삭제 (LOCK-HW-03) | YES | 강제 삭제 + 집계 확인 |
| ACT-003 | 칼로리 추정 음수값 | YES | 0으로 클램핑 + 경고 로그 |
| ACT-004 | 외부 동기화 실패 (V2) | YES | 재시도 3회, 실패 시 수동 입력 폴백 |
| ACT-005 | 면책 문구 누락 (LOCK-HW-04) | YES | 강제 삽입, 실패 시 응답 차단 |
| ACT-006 | PROTECTED 데이터 외부 전송 시도 | NO | 즉시 차단 + P0 에스컬레이션 |
| ACT-007 | 비정상 데이터 (걸음 수 > 100,000/일) | YES | 경고 + 사용자 확인 요청 |

---

## 10. Phase별 복구 전략

### Phase 1 (현재): 기본 복구

```
[데이터 수집 실패]
  → 암호화 재시도 (3회)
  → 실패 시 수동 입력 폴백
  → 로그 기록 + 에스컬레이션
```

### Phase 2: 자동 복구 강화

```
[동기화 실패]
  → HealthKit/Google Fit 재연결 시도
  → 오프라인 큐 → 연결 복구 시 자동 동기화
  → 데이터 정합성 자동 검증
```

### Phase 3: 예측 기반 예방

```
[사전 예측]
  → 동기화 실패 패턴 분석 → 선제 알림
  → 배터리/네트워크 상태 기반 동기화 스케줄링
```

### 다운그레이드 시 confidence penalty 표

| 다운그레이드 상황 | penalty | 결과 |
|-----------------|---------|------|
| Phase 3 → Phase 2 | -0.1 | 예측 동기화 비활성 |
| Phase 2 → Phase 1 | -0.2 | 외부 연동 비활성, 수동 입력만 |
| Phase 1 → 긴급 모드 | -0.5 | 데이터 수집 중단, 기존 집계만 조회 |

---

## 11. Phase 2 테스트 시나리오

| # | 시나리오 | 입력/조건 | 기대 결과 | 관련 LOCK |
|---|---------|----------|----------|----------|
| T-ACT-01 | 수동 활동 기록 | 걷기 30분, 5000보 | 저장 성공 + AES-256-GCM 암호화 확인 | HW-06 |
| T-ACT-02 | 칼로리 자동 추정 | 달리기 30분, 체중 70kg | 추정 칼로리 약 343 kcal (MET 9.8) | - |
| T-ACT-03 | 원시 데이터 24h TTL | 24시간 경과 시뮬레이션 | 원시 데이터 삭제 + 집계 보존 확인 | HW-03 |
| T-ACT-04 | 집계 데이터 90일 보존 | 90일 경과 시뮬레이션 | 집계 데이터 삭제 확인 | HW-03 |
| T-ACT-05 | 면책 문구 포함 확인 | 활동 인사이트 응답 | LOCK-HW-04 면책 문구 포함 | HW-04 |
| T-ACT-06 | PROTECTED 등급 외부 전송 차단 | HTTP POST 시도 | 차단 + 에스컬레이션 | HW-02 |
| T-ACT-07 | 주간 트렌드 분석 | 7일 활동 데이터 | 개선/유지/감소 트렌드 판정 | - |
| T-ACT-08 | 목표 달성률 계산 | 걸음 8000/10000 | 달성률 0.8 반환 | - |
| T-ACT-09 | VWS 운동 점수 산출 | 10000보 + 30분 + 2종목 | 0-20 점수 산출 확인 | HW-11 |
| T-ACT-10 | 비정상 데이터 검증 | 걸음 수 150,000 | 경고 + 사용자 확인 요청 | - |
| T-ACT-11 | HealthKit 어댑터 V1 | sync() 호출 | NotImplementedError (V2 예정) | - |
| T-ACT-12 | 암호화 미적용 저장 시도 | encrypted=False | SecurityError 발생 | HW-06 |

---

## 12. 공통 자료 구조 선정의

| 클래스/Enum | 용도 | 참조 위치 |
|------------|------|----------|
| `ExerciseIntensity` | 운동 강도 3단계 | §3.1, 전 서브폴더 |
| `DataSourceType` | 데이터 소스 유형 | §3.1, sleep/nutrition 공유 |
| `DailyActivityRecord` | 일일 활동 종합 기록 | §3.1, VWS 연동 |
| `ExerciseActivity` | 개별 운동 활동 | §3.1 |
| `HealthDataSyncAdapter` | 외부 플랫폼 동기화 ABC | §4.1 |
| `ActivityDataEscalationPayload` | 에스컬레이션 페이로드 | §8 |

---

## 13. 세션 간 인터페이스 cross-check

| 인터페이스 | 제공 측 | 소비 측 | 상태 |
|-----------|--------|--------|------|
| `DailyActivityRecord` | 본 문서 (P-011) | wellness_score.md (P-027) | V1 정의 완료 |
| `ExerciseIntensity` | 본 문서 (P-011) | stress_detection.md (P-004) | V1 정의 완료 |
| `DataSourceType` | 본 문서 (P-011) | sleep_management.md (P-012), nutrition_management.md (P-013) | V1 공유 |
| `HealthDataSyncAdapter` | 본 문서 (P-011) | V2 HealthKit/Google Fit 실 구현 | V1 ABC 정의, V2 구현 예정 |
| `ActivityVWSContributor.compute_exercise_score()` | 본 문서 | 05_emotion-journal/wellness_score.md | V1 정의 완료 |

---

> **문서 끝** — activity_exercise.md V1 L3 완성 (2026-04-10)
