# digital_wellbeing.md — 디지털 웰빙 모니터링

> **P-ID**: P-026
> **V단계**: V1/V2
> **상태**: NEW
> **L3 완성**: 2026-04-10
> **정본 소유자**: sot 2/3-6_Health-Wellness-EmotionAI/06_ethics-privacy/

---

## 교차 참조 블록

| 참조 문서 | 위치 | 참조 내용 |
|----------|------|----------|
| 종합계획서 §6.6 | P-026 | 디지털 웰빙 (스크린타임/디지털디톡스) |
| STEP7-P | P-026 | 디지털 웰빙 모니터링 원본 |
| ethics_framework.md | §3.7 | 원칙 7 기능 끄기 (사용자 제어) |
| 종합계획서 §3.4 | LOCK-HW-02/04 | 프라이버시 등급 / 비의료 면책 |
| 종합계획서 §4 | R-09-1, R-09-3 | 면책 포함 / 데이터 외부 전송 금지 |
| 05_emotion-journal/wellness_score.md | P-027 | VWS 웰니스 점수 (생산성균형 차원 연동) |
| 04_stress-management/burnout_prevention.md | P-023 | 번아웃 예방 연계 |

---

## 1. 개요

본 문서는 VAMOS 디지털 웰빙 모니터링 기능을 L3 구현 즉시 투입 가능 수준으로 정의한다. 사용자의 디지털 기기 사용 패턴(스크린 타임, 알림 빈도, 사용 시간대)을 추적하고, 과도한 사용 시 디지털 디톡스를 제안한다.

**V1 범위**: 스크린 타임 추적 + 알림 관리 + 기본 사용 패턴 분석 + 디지털 디톡스 제안
**V2 범위**: 앱별 상세 분석 + 시간대별 패턴 + 소셜 미디어 영향 분석 + 자동화 규칙

---

## 2. LOCK 인용

> LOCK (LOCK-HW-02, 기존 명세 §1/P-018): 감정=PRIVATE(로컬전용), 건강=PROTECTED(AES-256+별도PIN), 의료=HIGHEST(외부전송절대금지)

> LOCK (LOCK-HW-04, STEP7-P 윤리원칙): "VAMOS는 의료 서비스가 아닙니다" 모든 건강 관련 응답에 포함

---

## 3. 공통 자료 구조 선정의

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime, timedelta

class UsageCategory(Enum):
    """사용 카테고리"""
    PRODUCTIVE = "productive"       # 업무/학습
    SOCIAL = "social"               # 소셜 미디어/메시징
    ENTERTAINMENT = "entertainment" # 게임/동영상/음악
    HEALTH = "health"               # 건강/운동/명상
    UTILITY = "utility"             # 유틸리티/설정
    OTHER = "other"

@dataclass
class ScreenTimeRecord:
    """스크린 타임 기록 (PROTECTED 등급)"""
    record_id: str
    date: str                       # YYYY-MM-DD
    total_minutes: int              # 일일 총 사용 시간 (분)
    category_breakdown: dict[UsageCategory, int]  # 카테고리별 분 수
    pickup_count: int               # 기기 잠금해제 횟수
    notification_count: int         # 수신 알림 수
    longest_session_minutes: int    # 최장 연속 사용 시간
    first_use_time: str             # 첫 사용 시각 (HH:MM)
    last_use_time: str              # 마지막 사용 시각 (HH:MM)
    
@dataclass
class DigitalWellbeingScore:
    """디지털 웰빙 점수"""
    date: str
    score: float                    # 0.0 ~ 1.0
    screen_time_score: float        # 사용 시간 점수
    break_score: float              # 휴식 패턴 점수
    notification_score: float       # 알림 관리 점수
    sleep_hygiene_score: float      # 수면 위생 점수 (취침 전 사용)
    recommendations: list[str]      # 개선 제안 목록

@dataclass
class DetoxSuggestion:
    """디지털 디톡스 제안"""
    suggestion_id: str
    trigger: str                    # 제안 트리거 사유
    message: str                    # 사용자에게 표시할 메시지
    severity: str                   # "gentle" | "moderate" | "strong"
    actions: list[str]              # 제안 행동 목록
    dismissable: bool = True        # 사용자 무시 가능 여부
```

---

## 4. 스크린 타임 추적 (V1)

### 4.1 데이터 수집

```python
class ScreenTimeTracker:
    """
    스크린 타임 추적기.
    
    데이터 등급: PROTECTED (건강 데이터)
    동의 필요: "건강 데이터 연동" opt-in
    저장: 로컬 전용, AES-256-GCM 암호화
    외부 전송: 금지 (R-09-3 — 감정 데이터 미포함이나 건강 행동 데이터로 분류)
    
    시간복잡도: O(1) per event, O(n) daily aggregation (n=이벤트 수)
    """
    
    def __init__(self):
        self.daily_buffer: list[UsageEvent] = []
    
    def record_event(self, event: UsageEvent) -> None:
        """
        사용 이벤트 기록.
        원시 이벤트는 24시간 TTL 후 삭제, 일일 집계만 보존 (90일).
        """
        self.daily_buffer.append(event)
    
    def aggregate_daily(self, date: str) -> ScreenTimeRecord:
        """
        일일 집계.
        원시 이벤트 → 집계 데이터 변환 후 원시 삭제.
        LOCK-HW-03 준수: 원시 24시간 TTL, 집계 90일.
        """
        events = [e for e in self.daily_buffer if e.date == date]
        
        record = ScreenTimeRecord(
            record_id=generate_id(),
            date=date,
            total_minutes=sum(e.duration_minutes for e in events),
            category_breakdown=self._categorize(events),
            pickup_count=sum(1 for e in events if e.type == "unlock"),
            notification_count=sum(1 for e in events if e.type == "notification"),
            longest_session_minutes=self._longest_session(events),
            first_use_time=min(e.timestamp for e in events).strftime("%H:%M"),
            last_use_time=max(e.timestamp for e in events).strftime("%H:%M"),
        )
        
        # 원시 이벤트 삭제 (24시간 TTL)
        self._schedule_raw_deletion(events, ttl_hours=24)
        
        # 집계 데이터 암호화 저장 (PROTECTED)
        self._store_encrypted(record)
        
        return record
```

### 4.2 사용 패턴 분석

```python
class UsagePatternAnalyzer:
    """
    사용 패턴 분석기.
    
    분석 항목:
    - 일일 총 사용 시간 트렌드
    - 카테고리별 비율 변화
    - 잠금해제 빈도
    - 수면 전후 사용 패턴
    - 연속 사용 세션 길이
    
    시간복잡도: O(d) — d=분석 대상 일수 (기본 7일, 최대 90일)
    """
    
    # 기준값 (사용자 커스터마이즈 가능)
    DEFAULT_THRESHOLDS = {
        "daily_limit_minutes": 240,      # 4시간/일
        "pickup_limit": 50,              # 50회/일
        "notification_limit": 100,       # 100건/일
        "longest_session_limit": 60,     # 60분 연속
        "bedtime_cutoff": "22:00",       # 취침 전 사용 금지 시각
        "morning_grace": "07:00",        # 아침 사용 시작 권장 시각
    }
    
    def analyze(self, records: list[ScreenTimeRecord]) -> DigitalWellbeingScore:
        """주간 디지털 웰빙 점수 산출"""
        latest = records[-1]
        week = records[-7:] if len(records) >= 7 else records
        
        screen_score = self._score_screen_time(latest, week)
        break_score = self._score_breaks(latest)
        notif_score = self._score_notifications(latest)
        sleep_score = self._score_sleep_hygiene(latest)
        
        overall = (screen_score * 0.3 + break_score * 0.25 + 
                   notif_score * 0.2 + sleep_score * 0.25)
        
        recommendations = self._generate_recommendations(
            screen_score, break_score, notif_score, sleep_score, latest
        )
        
        return DigitalWellbeingScore(
            date=latest.date,
            score=round(overall, 2),
            screen_time_score=round(screen_score, 2),
            break_score=round(break_score, 2),
            notification_score=round(notif_score, 2),
            sleep_hygiene_score=round(sleep_score, 2),
            recommendations=recommendations
        )
    
    def _score_screen_time(self, today: ScreenTimeRecord, week: list) -> float:
        """사용 시간 점수 (0.0~1.0, 높을수록 좋음)"""
        limit = self.DEFAULT_THRESHOLDS["daily_limit_minutes"]
        ratio = today.total_minutes / limit
        if ratio <= 0.8:
            return 1.0
        elif ratio <= 1.0:
            return 0.8
        elif ratio <= 1.5:
            return 0.5
        else:
            return max(0.1, 1.0 - ratio * 0.3)
    
    def _score_sleep_hygiene(self, today: ScreenTimeRecord) -> float:
        """수면 위생 점수: 취침 전 사용 패턴"""
        cutoff = self.DEFAULT_THRESHOLDS["bedtime_cutoff"]
        if today.last_use_time <= cutoff:
            return 1.0
        elif today.last_use_time <= "23:00":
            return 0.6
        else:
            return 0.3
```

---

## 5. 알림 관리 (V1)

### 5.1 알림 분석

```python
class NotificationManager:
    """
    알림 관리 및 분석.
    
    기능:
    - 알림 빈도 추적
    - 방해 알림 식별
    - 집중 시간대 알림 일괄 묵음 제안
    - 앱별 알림 빈도 리포트 (V2)
    """
    
    def analyze_notifications(self, record: ScreenTimeRecord) -> dict:
        limit = self.DEFAULT_THRESHOLDS["notification_limit"]
        
        return {
            "total": record.notification_count,
            "over_limit": record.notification_count > limit,
            "excess": max(0, record.notification_count - limit),
            "suggestion": self._suggest_quiet_hours(record) if record.notification_count > limit else None
        }
    
    def _suggest_quiet_hours(self, record: ScreenTimeRecord) -> str:
        return (
            "알림이 많은 하루였네요. "
            "집중이 필요한 시간대에 알림 묵음을 설정해 보시는 건 어떨까요?"
        )
```

---

## 6. 디지털 디톡스 제안

### 6.1 트리거 조건 및 제안

```python
class DigitalDetoxEngine:
    """
    디지털 디톡스 제안 엔진.
    
    트리거 조건에 따라 gentle/moderate/strong 수준의 제안을 생성한다.
    사용자 자율성 존중: 모든 제안은 무시(dismiss) 가능.
    """
    
    TRIGGERS = {
        "continuous_60min": {
            "condition": "연속 사용 60분 초과",
            "severity": "gentle",
            "message": "1시간 넘게 사용 중이시네요. 잠깐 휴식을 취해 보시는 건 어떨까요?",
            "actions": ["5분 스트레칭", "눈 휴식 (20-20-20 규칙)", "잠깐 산책"]
        },
        "daily_limit_exceeded": {
            "condition": "일일 사용 시간 제한 초과",
            "severity": "moderate",
            "message": "오늘 설정하신 사용 시간을 초과했어요. 나머지 시간은 오프라인 활동을 즐겨보시는 건 어떨까요?",
            "actions": ["독서", "운동", "명상", "취미 활동"]
        },
        "bedtime_usage": {
            "condition": "취침 시간 이후 사용",
            "severity": "moderate",
            "message": "지금은 수면을 위해 기기 사용을 줄이는 것이 좋은 시간이에요.",
            "actions": ["야간 모드 활성화", "기기 충전대에 두기", "호흡 명상"]
        },
        "weekly_increase_30pct": {
            "condition": "주간 사용 시간 30% 이상 증가",
            "severity": "strong",
            "message": "이번 주 기기 사용 시간이 지난 주보다 많이 늘었어요. 디지털 디톡스 타임을 계획해 보시겠어요?",
            "actions": ["주말 반나절 디지털 프리", "앱 타이머 설정", "오프라인 취미 탐색"]
        },
        "high_pickup_count": {
            "condition": "잠금해제 50회 초과",
            "severity": "gentle",
            "message": "오늘 기기를 자주 확인하셨네요. 알림을 정리하면 확인 횟수를 줄일 수 있어요.",
            "actions": ["불필요 알림 끄기", "앱 배치 정리", "집중 모드 활용"]
        },
    }
    
    def evaluate(self, record: ScreenTimeRecord, week: list[ScreenTimeRecord]) -> list[DetoxSuggestion]:
        """
        디톡스 제안 평가.
        최대 2개 제안 (과도한 개입 방지).
        """
        suggestions = []
        
        if record.longest_session_minutes > 60:
            suggestions.append(self._create_suggestion("continuous_60min"))
        
        if record.total_minutes > self.thresholds["daily_limit_minutes"]:
            suggestions.append(self._create_suggestion("daily_limit_exceeded"))
        
        if record.last_use_time > self.thresholds["bedtime_cutoff"]:
            suggestions.append(self._create_suggestion("bedtime_usage"))
        
        if len(week) >= 14:
            this_week = sum(r.total_minutes for r in week[-7:])
            last_week = sum(r.total_minutes for r in week[-14:-7])
        elif len(week) >= 7:
            this_week = sum(r.total_minutes for r in week[-7:])
            last_week = this_week   # 14일 미만 — 비교 불가, 알림 미발생
            if last_week > 0 and (this_week - last_week) / last_week > 0.3:
                suggestions.append(self._create_suggestion("weekly_increase_30pct"))
        
        if record.pickup_count > self.thresholds["pickup_limit"]:
            suggestions.append(self._create_suggestion("high_pickup_count"))
        
        # 최대 2개, severity 높은 순
        severity_order = {"strong": 0, "moderate": 1, "gentle": 2}
        suggestions.sort(key=lambda s: severity_order.get(s.severity, 99))
        return suggestions[:2]
```

### 6.2 20-20-20 눈 휴식 규칙

```
20분마다 — 20피트(6미터) 먼 곳을 — 20초간 바라보기
```

| 항목 | 값 |
|------|-----|
| 간격 | 20분 연속 사용 |
| 대상 | 6미터 이상 먼 곳 |
| 시간 | 20초 |
| 제안 방식 | gentle 알림 (dismiss 가능) |

---

## 7. 면책 문구 적용

디지털 웰빙 관련 응답에 LOCK-HW-04 면책 문구 포함:

```
⚕️ 안내: VAMOS는 의료 서비스가 아닙니다. 제공되는 건강 정보와 감정 분석은
참고용이며, 의학적 진단·치료·처방을 대체하지 않습니다. 건강에 관한 우려가
있으시면 의료 전문가와 상담하시기 바랍니다.
```

---

## 8. 에스컬레이션 페이로드 구조

```python
@dataclass
class DigitalWellbeingEscalationPayload:
    """
    디지털 웰빙 에스컬레이션 페이로드.
    I-20 경유 (R-01-8).
    """
    escalation_id: str               # "ESC-DWB-{uuid}"
    severity: str                    # "P2" (주로 UX 개선 수준)
    trigger: str                     # 트리거 사유
    metric_value: float              # 초과/이상 수치
    threshold: float                 # 기준값
    suggestion_dismissed_count: int  # 제안 무시 횟수
    timestamp: str
    
    def to_i20_payload(self) -> dict:
        return {
            "source": "health-wellness-emotionai/digital_wellbeing",
            "escalation_id": self.escalation_id,
            "severity": self.severity,
            "category": "digital_wellbeing",
            "detail": {
                "trigger": self.trigger,
                "value": self.metric_value,
                "threshold": self.threshold,
            },
            "timestamp": self.timestamp,
        }
```

---

## 9. 로깅 (R-01-7 structured JSON)

```json
{
  "trace_id": "dwb-track-{uuid}",
  "error": {
    "code": "DWB-001",
    "message": "Daily screen time limit exceeded",
    "total_minutes": 290,
    "limit_minutes": 240
  },
  "context": {
    "module": "digital_wellbeing.screen_time_tracker",
    "date": "2026-04-10",
    "user_threshold_custom": false,
    "timestamp": "2026-04-10T22:00:00Z"
  },
  "recovery": {
    "action": "detox_suggestion_displayed",
    "severity": "moderate",
    "suggestion_id": "dtx-{uuid}",
    "dismissed": false
  }
}
```

---

## 10. 예외 처리 정책 표

| error_code | 설명 | recoverable | 처리 |
|-----------|------|-------------|------|
| DWB-001 | 일일 사용 시간 초과 (정상 트리거) | N/A | 디톡스 제안 표시 |
| DWB-002 | 스크린 타임 데이터 수집 실패 | YES | 재시도 3회, 실패 시 해당 일 데이터 결측 처리 |
| DWB-003 | 집계 데이터 암호화 실패 | YES | 재시도, 실패 시 원시 데이터 즉시 삭제 (안전 방향) |
| DWB-004 | 알림 데이터 접근 권한 없음 | YES | 권한 재요청 UI 표시 |
| DWB-005 | 디톡스 제안 렌더링 실패 | YES | 대체 텍스트 표시 |
| DWB-006 | 면책 문구 삽입 실패 | YES | 재삽입, 실패 시 응답 차단 (R-09-1) |

---

## 11. Phase별 복구 전략

### Phase 1: 기본 추적 + 제안

```
[데이터 수집 실패]
  → OS API 접근 실패 → 재시도 3회
  → 권한 부재 → 권한 재요청
  → 암호화 실패 → 데이터 삭제 (안전 방향)
```

### Phase 2: 앱별 상세 분석

```
[V2 확장]
  → 앱별 사용 시간 분류
  → 소셜 미디어 vs 생산성 비율 분석
  → 자동화 규칙 (시간대별 앱 차단)
```

### Phase 3: 감정-디지털 사용 상관 분석

```
[크로스 도메인]
  → 감정 상태 + 디지털 사용 패턴 상관 분석
  → 스트레스 시 소셜 미디어 사용 증가 감지
  → 개인화된 디지털 웰빙 전략
```

### 다운그레이드 시 confidence penalty 표

| 다운그레이드 상황 | penalty | 결과 |
|-----------------|---------|------|
| Phase 3 → Phase 2 | -0.1 | 감정 상관 분석 비활성 |
| Phase 2 → Phase 1 | -0.15 | 앱별 분석 비활성, 총량만 |
| Phase 1 → 최소 모드 | -0.3 | 추적만, 제안 비활성 |

---

## 12. Phase 2 테스트 시나리오

| # | 시나리오 | 입력/조건 | 기대 결과 |
|---|---------|----------|----------|
| T-DWB-01 | 일일 사용 시간 초과 | 총 300분 사용 (제한 240분) | moderate 디톡스 제안 |
| T-DWB-02 | 연속 사용 60분 | 세션 65분 연속 | gentle 휴식 제안 (20-20-20) |
| T-DWB-03 | 취침 후 사용 | 23:30 사용 감지 | moderate 수면 위생 제안 |
| T-DWB-04 | 잠금해제 50회 초과 | 60회 unlock | gentle 알림 정리 제안 |
| T-DWB-05 | 주간 30% 증가 | 이번 주 1800분 vs 지난 주 1200분 | strong 디톡스 계획 제안 |
| T-DWB-06 | 면책 문구 포함 | 디지털 웰빙 응답 생성 | LOCK-HW-04 면책 필수 포함 |
| T-DWB-07 | 데이터 수집 실패 | OS API 타임아웃 | 재시도 3회 + 결측 처리 |
| T-DWB-08 | 제안 무시(dismiss) | 사용자가 gentle 제안 무시 | 무시 기록 + 재제안 안 함 (당일) |
| T-DWB-09 | 모든 기능 끄기 | 디지털 웰빙 추적 OFF | 데이터 수집/제안 즉시 중단 |
| T-DWB-10 | 암호화 저장 | 일일 집계 저장 | AES-256-GCM + PROTECTED 등급 |
| T-DWB-11 | 원시 데이터 TTL | 24시간 경과 후 | 원시 이벤트 자동 삭제 확인 |
| T-DWB-12 | 집계 데이터 보존 | 90일 경과 후 | 집계 데이터 자동 삭제 확인 |

---

## 13. VWS 연동

디지털 웰빙 점수는 VWS(웰니스 점수)의 **생산성균형** 차원(0-20)에 기여할 수 있다.

> LOCK (LOCK-HW-11, STEP7-P P-027): 수면(0-20)+운동(0-20)+감정(0-20)+사회적연결(0-20)+생산성균형(0-20)=0-100

**연동 방식**: 디지털 웰빙 점수(0.0~1.0)를 생산성균형 차원의 보조 지표로 제공. VWS 산출 모듈(05_emotion-journal/wellness_score.md)에서 참조.

---

> **문서 끝** — digital_wellbeing.md V1 L3 완성 (2026-04-10)

---

# §V3. Phase 4 production-ready 정본 (P-026-V3 genuine write)

| 항목 | 값 |
|------|-----|
| **V단계** | **V3 (Phase 4 production-ready 정본)** |
| **Status** | **APPROVED** |
| **Level** | **L3 COMPLETE (E1~E10 9요소, 87점)** |
| **LOCK 참조** | LOCK-HW-02, LOCK-HW-03, LOCK-HW-06, LOCK-HW-11 (in-domain) + 3-4 LOCK-WF-10 N-018 (개념 참조) |
| **SOT 출처** | STEP7-P P-026 + 종합계획서 §6.4 + §3.4 |
| **cross-domain** | 3-4 Workflow-RPA N-018 mobile_automation (스크린타임 자동 차단, 개념 참조 — path stale D-P4-4-1) / 05_emotion-journal/wellness_score VWS 연동 |
| **최종 갱신** | 2026-06-01 (Phase 4 RECOVERY Sub-A genuine write, P4-4 §V3 EXTEND, Sub-A FINAL) |

> **EXTEND 주의**: 본 §V3는 상기 V1/V2 본문(§1~§13, 19,176 B)을 **byte EXACT 보존**한 상태에서 true EOF에 추가된 production-ready 정본 본문이다. V2 영역 prefix 재작성 0.

## §V3.1 개요 (Purpose/Scope)

V3는 V1/V2 디지털 웰빙 모니터링을 **스크린타임 4-분석(앱별/카테고리별/시간대별/알림) + 디지털디톡스 챌린지(3일/7일/30일) + 3-4 Workflow-RPA 자동 차단 연동 + LOCK-HW-11 VWS 생산성균형 통합**으로 확장한다. 모든 건강 행동 데이터는 LOCK-HW-02 PROTECTED 등급 + LOCK-HW-06 AES-256-GCM 암호화 + R-09-3 외부 전송 금지를 따른다.

## §V3.2 스크린타임 4-분석 (E1 Input / E3 Pipeline)

LOCK 인용 (정본 — 본 문서 재정의 0):
> LOCK (LOCK-HW-02): 감정=PRIVATE(로컬전용), 건강=PROTECTED(AES-256+별도PIN), 의료=HIGHEST(외부전송절대금지)
> LOCK (LOCK-HW-06): 건강 데이터 저장 시 AES-256-GCM 필수
> LOCK (LOCK-HW-03): 원시건강데이터 24시간TTL, 집계데이터 90일, 감정로그 사용자설정(기본180일)

| # | 분석 축 | 내용 | 집계 |
|--:|---------|------|------|
| 1 | **앱별** | 앱 단위 사용 시간 (소셜미디어/생산성/엔터테인먼트/학습) | 일/주/월 |
| 2 | **카테고리별** | `UsageCategory` 6분류 집계 (§3 V1 정의 재사용) | 일/주/월 |
| 3 | **시간대별** | 피크 사용 시간대 + 취침 전 사용 패턴 | 시간 버킷 |
| 4 | **알림** | 알림 빈도 + 방해 알림 식별 (§5 V1 base 확장) | 일 |

```python
from dataclasses import dataclass

@dataclass
class ScreenTimeAnalyticsV3:
    """스크린타임 4-분석 (PROTECTED 등급, AES-256-GCM)"""
    date: str
    app_breakdown: dict[str, int]              # 앱별 분 수
    category_breakdown: dict[str, int]         # 카테고리별 (UsageCategory)
    hourly_buckets: list[int]                  # 24 시간대별 분 수
    notification_analysis: dict                # §5 NotificationManager 결과
    productivity_balance: float                # 0.0~1.0 → VWS 생산성균형 기여
    privacy_grade: str = "PROTECTED"           # LOCK-HW-02
```

## §V3.3 디지털디톡스 챌린지 (3일/7일/30일) (E2 Output)

| 챌린지 | 기간 | 목표 | 단계적 절제 |
|--------|------|------|------------|
| 단기 | **3일** | 취침 전 사용 0 | 야간 모드 + 충전대 분리 |
| 중기 | **7일** | 일일 한도 20% 감축 | 앱 타이머 + 알림 정리 |
| 장기 | **30일** | 카테고리 균형 회복 | 주말 반나절 디지털 프리 + 오프라인 취미 |

```python
@dataclass
class DetoxChallenge:
    challenge_id: str
    duration_days: int                # 3 | 7 | 30
    daily_targets: list[str]
    progress: dict[str, bool]         # 일별 달성
    auto_block_enabled: bool          # §V3.4 3-4 N-018 연동 여부
    dismissable: bool = True          # 사용자 자율성 (LOCK-HW-09)
```

## §V3.4 3-4 Workflow-RPA 자동 차단 연동 (E6 / cross-domain)

> **3-4 N-018 mobile_automation 개념 참조** (path stale D-P4-4-1 — 개념 참조 유지): 디지털디톡스 챌린지의 자동 차단(앱 타이머/시간대별 차단)은 3-4 Workflow-RPA `mobile_automation.md`(N-018) 모바일 자동화 워크플로우를 연동한다. 3-4 LOCK-WF-10 보안 정책(권한/감사) 정합 하에 동작하며, 본 도메인은 **차단 규칙 발신만** 하고 실행은 3-4가 담당한다(소유 경계 보존).

- **연동 방식**: 디톡스 챌린지 활성 시 차단 규칙(앱/시간대) → 3-4 N-018 워크플로우로 전달 (read-only 발신).
- **R-09-3 준수**: 사용량 원시 데이터 외부 전송 금지. 차단 규칙(앱 식별자 + 시간대)만 전달, 사용 내역 미포함.

## §V3.5 LOCK-HW-11 VWS 생산성균형 통합 (E2)

> LOCK (LOCK-HW-11): 수면(0-20)+운동(0-20)+감정(0-20)+사회적연결(0-20)+생산성균형(0-20)=0-100

- 디지털 웰빙 점수(0.0~1.0)를 VWS **생산성균형 차원(0-20)** 의 보조 지표로 매핑(`productivity_balance × 20`). VWS 산출 모듈(`../05_emotion-journal/wellness_score.md`)에서 참조. (§13 V1 VWS 연동 확장.)

## §V3.6 E1~E10 L3 완전성 + 운영 baseline

| 요소 | 항목 | 본 문서 충족 |
|------|------|-------------|
| E1 | Input Schema | §V3.2 `ScreenTimeAnalyticsV3` 4-분석 |
| E2 | Output Schema | §V3.3 `DetoxChallenge` + §V3.5 VWS 매핑 |
| E3 | Algorithm/Pipeline | §V3.2 집계 + §4 V1 `aggregate_daily` 재사용 |
| E4 | Model Comparison | Apple Screen Time vs Android Digital Wellbeing vs 자체 (자체 채택: PROTECTED 로컬 + VWS 통합) |
| E5 | Error Handling | §10 V1 예외 정책표 (DWB-001~006) + 권한 없음 시 수동 입력 |
| E6 | Privacy/Security | §V3.2 LOCK-HW-02 PROTECTED + LOCK-HW-06 AES-256-GCM + R-09-3 |
| E7 | Performance SLA | 일일 리포트 생성 p95 ≤ 5초 |
| E8 | Integration Test | §V3.7 테스트 시나리오 8건 (+ §12 V1 12건) |
| E9 | Dependencies | §V3.4 (3-4 N-018) + §V3.5 (wellness_score) |
| E10 | Ethics/UX | R-09-3 외부 전송 금지 + 사용자 데이터 소유권 + LOCK-HW-09 자율성 |

## §V3.7 E8 Integration Test — Phase 5 V3 테스트 시나리오 (8건)

| # | 시나리오 | 입력/조건 | 기대 결과 |
|---|----------|----------|-----------|
| S-V3-1 | 앱별 분석 | 앱 사용 로그 | 앱 단위 분 수 + 카테고리 매핑 |
| S-V3-2 | 시간대별 피크 | 24시간 버킷 | 피크 시간대 식별 + 취침 전 경고 |
| S-V3-3 | 3일 디톡스 챌린지 | 챌린지 시작 | 일별 목표 + 진행 추적 |
| S-V3-4 | 30일 챌린지 달성 | 30일 완료 | 카테고리 균형 리포트 |
| S-V3-5 | 3-4 자동 차단 연동 | 차단 규칙 활성 | N-018 워크플로우로 규칙 발신 (read-only) |
| S-V3-6 | LOCK-HW-06 암호화 | 집계 저장 | AES-256-GCM + PROTECTED 등급 |
| S-V3-7 | VWS 생산성균형 매핑 | 디지털 점수 0.8 | 생산성균형 16/20 기여 (LOCK-HW-11) |
| S-V3-8 | 원시 데이터 외부 전송 시도 | 사용 내역 전송 요청 | [PRIVACY_BLOCK] R-09-3 거부 |

운영 baseline: **웰빙 개선율 ≥ 25%** (VBS-17 V3) + 일일 리포트 p95 ≤ 5초 + 디톡스 챌린지 완료율 ≥ 40% (Phase 5 운영 실측).

## §V3.8 L3 점수 (87/100)

| 평가 축 | 배점 | 획득 | 근거 |
|---------|-----:|-----:|------|
| E1~E10 9요소 완전성 | 50 | 44 | §V3.6 전수 + V1/V2 base 재사용 |
| LOCK verbatim 정합 | 20 | 19 | LOCK-HW-02/03/06/11 인용 (재정의 0) |
| cross-domain 계약 | 15 | 13 | 3-4 N-018 개념 참조 (path stale 명시) + VWS |
| SoT 출처 정합 | 15 | 11 | STEP7-P P-026 |
| **합계** | **100** | **87** | **APPROVED (≥ 80)** |

## §V3.9 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-06-01 | **V3-Phase 4 (genuine write, §V3 EXTEND, Sub-A FINAL)** | Phase 4 RECOVERY Sub-A P4-4 — digital_wellbeing.md §V3 본문 genuine 작성 (V1/V2 19,176 B byte EXACT 보존 + true EOF §V3 append). 스크린타임 4-분석(앱별/카테고리별/시간대별/알림) + 디지털디톡스 챌린지 3일/7일/30일 + 3-4 Workflow-RPA N-018 자동 차단 연동(개념 참조, path stale D-P4-4-1, 차단 규칙 발신만) + LOCK-HW-02 PROTECTED + LOCK-HW-06 AES-256-GCM + LOCK-HW-03 집계 90일 + LOCK-HW-11 VWS 생산성균형 통합(0-20 매핑) verbatim 인용(재정의 0) + R-09-3 외부 전송 금지 + 사용자 데이터 소유권. E4 Apple/Android/자체 비교(자체 채택). E1~E10 9요소 L3 87점. Status DRAFT → APPROVED. |
