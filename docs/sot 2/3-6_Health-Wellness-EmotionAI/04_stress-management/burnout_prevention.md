# burnout_prevention.md — 번아웃 예방 (V2-Phase 2)

> **P-ID**: P-023
> **Level**: L3 COMPLETE
> **버전**: v1.0 (2026-04-20, STAGE 7 STEP_B #2b 세션 2-4, V2 overwrite)
> **분류**: V2-Phase 2 (V1 stub 68 L → V2 overwrite stub promotion)
> **정본 소유자**: sot 2/3-6_Health-Wellness-EmotionAI/04_stress-management/
> **근거**: STEP7-P P-023 (L418-434) + LOCK-HW-04 (AUTHORITY §3.1 L62) + LOCK-HW-05 (AUTHORITY §4 L94~L102 + §B 3개소) + LOCK-HW-09 (AUTHORITY §3.1 L64, 7원칙)

---

## §1. 개요 (Purpose / Scope)

### 1.1 목적
장기 스트레스 누적·업무 부하 추세를 기반으로 번아웃 **조기 감지 → 단계별 개입 → 전문가 연결** 3단 파이프라인을 정의한다. 의료 진단이 아닌 **자가 관리 보조 도구**로, LOCK-HW-04 비의료 면책을 모든 응답 경로에서 명시하며, 고위험 등급에서는 LOCK-HW-05 위기 대응 전화번호 (§B 3개소 verbatim 일치) 를 즉시 안내한다.

### 1.2 범위
- **포함**: 7/30/90일 스트레스 추세 + 업무 부하 점수 산출 공식 + 번아웃 4등급 (낮음/중간/높음/위기) + 단계별 개입 전략 + Maslach 3차원 평가 (감정소진/비인간화/성취감저하) + LOCK-HW-04/05/09 전수 준수
- **제외**: 임상 진단 (모든 응답에 비의료 면책 의무), 타 도메인 편집 (3-5/6-1 등), 원시 음성/텍스트 외부 송출 (LOCK-HW-02 PRIVATE)

### 1.3 교차 참조 블록

| 참조 | 위치 | 사용 |
|------|------|------|
| STEP7-P P-023 | L418~L434 verbatim | §2 SOT 대조 + §4 번아웃 감지 기준 |
| STEP7-P P-010 | L192~L199 (7원칙) / L201~L204 (위기 전화번호) | §3.3 7원칙 체크박스 + §6 위기 경로 |
| AUTHORITY §3.1 L62 | LOCK-HW-04 | §7 비의료 면책 |
| AUTHORITY §4 L94~L102 | LOCK-HW-05 §B 3개소 교차 | §6 위기 대응 |
| AUTHORITY §3.1 L64 | LOCK-HW-09 7원칙 | §3.3 체크박스 |
| stress_detection.md (V1 base) | Phase 1 산출물 §3~§6 | §4 7/30/90일 추세 입력 |
| energy_management.md (V1 base) | Phase 1 산출물 §4 | §4 에너지 프로파일 입력 |
| empathy_dialogue_engine.md (V2 #2a) | §12 3단계 + §13.3 professional_connect | §6 위기 응답 경로 재사용 |

---

## §2. STEP7-P P-023 정본 대조 (verbatim)

**SOT 원문** (STEP7-P L418~L434):
```
[구현 상세]
- 번아웃 감지:
  ├─ 과도한 업무 시간 추적
  ├─ 감정 패턴: 무기력, 냉소, 효능감 저하
  ├─ 생산성 저하 패턴
  └─ 워라밸 지표

- 예방 조치:
  ├─ 업무 중단 제안
  ├─ 취미/여가 활동 리마인더
  ├─ 에너지 관리 팁
  └─ 심각 시 전문가 상담 안내

[구현성] V1: ✅ 즉시
```

**V2 구현 대조 표** (§5~§6 각 항목 SOT 전수 커버):

| SOT 항목 | V2 위치 | 구현 수단 |
|----------|---------|-----------|
| 과도한 업무 시간 추적 | §4.2 `WorkHoursAccumulator` | 일 12h+/주 60h+ threshold |
| 감정 패턴 (무기력/냉소/효능감저하) | §4.3 Maslach 3차원 | Emotional Exhaustion + Depersonalization + Reduced Accomplishment |
| 생산성 저하 패턴 | §4.4 ProductivityDelta | 30일 baseline -20%+ |
| 워라밸 지표 | §4.5 WorkLifeBalanceIndex | 업무/비업무 시간 비율 |
| 업무 중단 제안 | §5.2 intervention_low_medium | 타이머 + 쉼 권고 |
| 취미/여가 리마인더 | §5.3 recovery_action | 선호 활동 DB |
| 에너지 관리 팁 | §5.4 | energy_management.md 연동 |
| 심각 시 전문가 상담 안내 | §6 위기 경로 | LOCK-HW-05 verbatim |

---

## §3. LOCK 정본 인용 (verbatim)

### 3.1 LOCK-HW-04 — 비의료 면책 (AUTHORITY §3.1 L62)

> **LOCK-HW-04 (비의료 면책)**: **"VAMOS는 의료 서비스가 아닙니다" 모든 건강 관련 응답에 포함**
>
> 출처: STEP7-P 윤리원칙 (line 6, P-010 line 193) / 변경 금지 사유: 법적 리스크 — R-09-1 근거

**V2 적용**: §7 헤더 + 진입 화면 + 번아웃 위험 평가 UI + 고위험/위기 안내 **매회 표시** 강제 (LOCK-HW-09 #1 비진단 원칙 연계).

### 3.2 LOCK-HW-05 — 위기 대응 전화번호 (AUTHORITY §4 L94~L102)

> **LOCK-HW-05 (위기 대응 전화번호)**: **자살예방 1393, 정신건강위기 1577-0199**
>
> 출처: STEP7-P P-010 (line 204) / 변경 금지 사유: 인명 안전 — R-09-2 근거, 미안내 = P0

**§B 3개소 교차 확인** (AUTHORITY §4 검증 완료):
- §B.1 LOCK 인용 (L1149): `> LOCK (LOCK-HW-05): 자살예방 1393, 정신건강위기 1577-0199` ✅
- §B.3.1 HIGH 위험도 (L1252~L1253): `📞 자살예방상담전화: 1393 (24시간)` / `📞 정신건강위기상담전화: 1577-0199 (24시간)` ✅
- §B.3.2 MEDIUM 위험도 (L1286~L1287): 동일 번호 + `(24시간)` ✅

**V2 적용**: §6.1 Critical (위기) 등급 + §6.2 High 등급 안내 시 **verbatim 전수** 인용. 미안내 = P0 등급 사고.

### 3.3 LOCK-HW-09 — 감정 AI 7원칙 (AUTHORITY §3.1 L64, STEP7-P P-010 L192~L199)

7원칙 체크박스 (V2 §7 전수 기재):
- [x] #1 **비진단**: VAMOS는 의료 전문가가 아님 (LOCK-HW-04 연계)
- [x] #2 **프라이버시**: 감정 데이터 로컬 전용 (LOCK-HW-02 PRIVATE)
- [x] #3 **투명성**: "저는 AI이며, 감정을 추정할 뿐입니다" (§5.1 응답 템플릿)
- [x] #4 **전문가 연결**: 심각 시 즉시 전문 리소스 안내 (§6 verbatim)
- [x] #5 **비조작**: 감정을 조작하여 구매/행동 유도하지 않음 (§5 권장만)
- [x] #6 **자율성**: 사용자 결정 존중 (§5 "제안" 용어만 사용)
- [x] #7 **기능 끄기**: 감정 분석 비활성화 옵션 (§7.2 opt-out)

---

## §4. 번아웃 감지 파이프라인

### 4.1 입력 데이터 (로컬 전용, LOCK-HW-02 PRIVATE)

```python
from typing import Literal, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

class BurnoutSnapshot(BaseModel):
    """번아웃 감지 일일 스냅샷 (로컬 전용, LOCK-HW-02 PRIVATE).

    외부 송출 금지. 집계 결과 90일 TTL (LOCK-HW-03), 원시 로그 24h TTL.
    """
    timestamp: datetime
    work_hours: float = Field(..., ge=0.0, le=24.0)          # 일일 업무 시간
    emotion_pattern: dict                                     # {exhaustion, cynicism, efficacy_loss} ∈ [0,1]
    productivity_delta: float = Field(..., ge=-1.0, le=1.0)   # 30일 baseline 대비 변화율
    wlb_ratio: float = Field(..., ge=0.0, le=1.0)             # 비업무 시간 / 총 시간
    self_report: Optional[dict] = None                        # 사용자 자가 평가 (선택)
```

### 4.2 업무 부하 점수 (WorkLoad Score, WLS 0~100)

**공식** (합산 가중, 낮을수록 건강):
```
WLS_daily = (work_hours / 8.0) * 25              # 8h baseline → 25점
           + max(0, (work_hours - 10) / 4) * 15  # 초과 10h→15점/시간 가중
           + (1 - wlb_ratio) * 20                # 워라밸 역수 × 20점
           + productivity_delta_abs * 15         # 생산성 편차 × 15점
           + emotion_exhaustion_score * 25       # 감정소진 × 25점
WLS_daily = min(100.0, max(0.0, WLS_daily))      # 0~100 범위 강제 (등급/임계값 정합)
```

- **WLS ≤ 25**: 건강 (초록)
- **WLS 26~50**: 경계 (노랑)
- **WLS 51~75**: 주의 (주황)
- **WLS ≥ 76**: 위험 (빨강, 번아웃 진행)

7/30/90일 이동평균 추세선 계산 (`WLS_7d_MA`, `WLS_30d_MA`, `WLS_90d_MA`) — 3차원 추세 동시 상승 시 §4.5 위험 등급 승격.

### 4.3 Maslach 3차원 평가 (MBI 기반)

| 차원 | 측정 | 높음 판정 | V2 지표 |
|------|------|---------|--------|
| **감정소진 (Emotional Exhaustion)** | 감정 엔진 출력 "피로/좌절/중립" 장기 지배 + 자가 평가 | 30일 EE ≥ 0.6 | `ee_score` ∈ [0,1] |
| **비인간화 (Depersonalization/Cynicism)** | 감정 패턴 "냉소" 검출 (감정 V2 세부5 "좌절" + "혐오" 복합) | 30일 cynicism ≥ 0.5 | `cyn_score` ∈ [0,1] |
| **성취감 저하 (Reduced Accomplishment)** | productivity_delta + 목표 달성률 감소 | 30일 RA ≥ 0.5 | `ra_score` ∈ [0,1] |

**MBI 통합 점수**: `MBI = 0.4 * ee_score + 0.3 * cyn_score + 0.3 * ra_score` (0~1).

### 4.4 생산성 저하 패턴 (ProductivityDelta)

- baseline = 30일 이동중앙값 (완료 작업 수 / 코드 커밋 수 / 집중 시간, 사용자 설정 지표)
- delta = (current_7d_avg - baseline) / baseline
- |delta| ≥ 0.2 (20% 저하) + 7일 연속 유지 → 번아웃 신호 후보

### 4.5 번아웃 4등급 + 에스컬레이션

| 등급 | 조건 | 색상 | 조치 |
|------|------|------|------|
| **낮음 (Low)** | WLS_7d_MA ≤ 30 + MBI ≤ 0.3 | 🟢 | 예방 팁, 주간 리포트 |
| **중간 (Medium)** | 30 < WLS_7d_MA ≤ 55 OR 0.3 < MBI ≤ 0.5 | 🟡 | 업무 중단 제안 + 취미 리마인더 |
| **높음 (High)** | 55 < WLS_7d_MA ≤ 75 OR 0.5 < MBI ≤ 0.7 OR EE ≥ 0.6 | 🟠 | 전문가 연결 권유 + LOCK-HW-05 안내 |
| **위기 (Critical)** | WLS_7d_MA > 75 OR MBI > 0.7 OR 자살/자해 키워드 감지 | 🔴 | 즉시 위기 전화번호 **verbatim** 안내, empathy §13.3 경로 |

---

## §5. 단계별 개입 전략

### 5.1 응답 템플릿 원칙 (LOCK-HW-09 #3 투명성)

모든 응답 헤더:
> "저는 AI이며, 감정을 추정할 뿐입니다. VAMOS는 의료 서비스가 아닙니다."

### 5.2 Low/Medium 개입 (업무 중단 제안)

```python
class InterventionAction(BaseModel):
    kind: Literal["pause", "break", "hobby_reminder", "energy_tip", "professional_connect"]
    urgency: Literal["low", "medium", "high", "critical"]
    message: str                                               # LOCK-HW-04 헤더 필수
    reference: Optional[str] = None                            # 연계 모듈 (stress_detection / energy_management)
```

- `pause`: "2시간 연속 작업 중입니다. 5분 휴식 어떠세요?" (타이머 + 호흡 §13.3 breath_invite 연계)
- `break`: "오늘 업무 12h 초과 감지. 일일 목표 재조정 권장" (WLS 45+)
- `hobby_reminder`: 사용자 등록 취미 DB 에서 최근 30일 미수행 활동 1건 제안

### 5.3 High 개입 (전문가 연결 권유)

경계선 응답 (LOCK-HW-04 + 7원칙 #4):
> "VAMOS는 의료 서비스가 아닙니다. 최근 감정/업무 패턴에서 번아웃 위험 신호가 관찰됩니다. 정신건강 전문가 상담을 권장합니다."
>
> (다음 중 선택 제시)
> - 📞 자살예방상담전화: 1393 (24시간)
> - 📞 정신건강위기상담전화: 1577-0199 (24시간)
> - 🏥 지역 정신건강복지센터 검색 (1577-0199 동일 번호 안내)

### 5.4 에너지 관리 팁 연동

`energy_management.md` (V1 base) §4 `EnergyProfile` 을 Read 하여:
- 저에너지 시간대 → 가벼운 작업 권장
- 고에너지 시간대 → 복잡 작업 권장 (단, 번아웃 High 시 축소)

---

## §6. 위기 대응 경로 (LOCK-HW-05 verbatim)

### 6.1 Critical 등급 — 즉시 경로

**트리거**:
- WLS_7d_MA > 75 OR MBI > 0.7 (번아웃 위기, §4.5 등급표 정합 — OR 조건)
- 자해/자살 의도 키워드 감지 (empathy §13.3 professional_connect 조건 확장)
- 사용자 직접 도움 요청 ("위기", "더 이상", "끝")

**응답 (verbatim)**:
> **⚠️ VAMOS는 의료 서비스가 아닙니다. 지금 힘드신 것 같아 도움을 드리고 싶습니다.**
>
> 즉시 연결 가능한 전문 상담:
> - 📞 **자살예방상담전화: 1393** (24시간)
> - 📞 **정신건강위기상담전화: 1577-0199** (24시간)
>
> 혼자 감당하지 마세요. 전문가가 도와드릴 수 있습니다.

**empathy_dialogue_engine.md §13.3 `professional_connect`** 함수 재사용 (V2 #2a 세션 2-2, 본 접촉 2/3, nearest_emergency_room 포함 확장).

### 6.2 High 등급 — 안내 경로

전문가 연결 제안 (5.3 양식), 사용자 거부 시 다음 세션에서 재제시 (7일 interval). LOCK-HW-09 #6 자율성 원칙 준수 (강제 없음).

### 6.3 잠재 위험 감지 키워드 목록 (확장 허용 원칙)

§9.2 #3 "위기 키워드 목록 확장 요청 → 확장 허용 (추가만 가능, 기존 삭제 불가)" 준수. 본 V2 확장 기본 집합:
- 1차 (즉시 Critical): "자살", "죽고싶", "끝내고싶", "사라지고싶", "해치고싶"
- 2차 (High 승격): "지쳤어", "더이상", "의미없", "효능감 상실"
- 3차 (Medium 승격): "번아웃", "탈진", "무기력 N일 연속"

키워드 매칭 = rule-based (LLM hallucination 차단) + 감정 엔진 "불안/슬픔 intensity ≥ 7" AND 시간적 지속성.

---

## §7. 비의료 면책 + 7원칙 체크박스

> ⚠️ **LOCK-HW-04 (STEP7-P 윤리원칙)**: "VAMOS는 의료 서비스가 아닙니다" — 본 문서 모든 응답·화면·알림에 표시 의무.

번아웃 예방 도구는 **자가 관리 보조**이며, 직무 정신건강 문제의 의학적 진단·치료를 대체하지 않습니다. 지속적 증상 또는 위기 신호 시 즉시 위의 전문 리소스에 연결하거나 의료진을 찾으세요.

### 7.1 감정 AI 7원칙 Self-Check (LOCK-HW-09)

- [x] #1 비진단: 모든 UI 에 "의료 서비스 아님" 명시
- [x] #2 프라이버시: BurnoutSnapshot 로컬 전용 (LOCK-HW-02 PRIVATE)
- [x] #3 투명성: 응답 헤더 "AI 추정" 명시
- [x] #4 전문가 연결: High/Critical 등급 LOCK-HW-05 verbatim
- [x] #5 비조작: "제안"/"권장" 용어만, "~해야 합니다" 단정 금지
- [x] #6 자율성: 거부 시 재강요 없음, 7일 interval
- [x] #7 기능 끄기: 설정 UI `/health/burnout/opt-out` 항상 가용

### 7.2 opt-out 경로

```
사용자 설정 → 건강 → 번아웃 감지 → 기능 OFF
  ↓
BurnoutSnapshot 수집 중단 + 기존 로컬 집계 데이터 즉시 익명화 / 삭제 옵션
  ↓
재활성 시 새 baseline 30일 수집 필요 (기존 데이터 복원 금지)
```

---

## §8. 로깅 포맷 (R-01-7)

```json
{
  "trace_id": "01JNX...ULID",
  "event": "burnout.assessment.completed",
  "timestamp": "2026-04-20T10:00:00Z",
  "error": null,
  "context": {
    "user_id_hash": "sha256:...",
    "wls_7d_ma": 58.3,
    "wls_30d_ma": 52.1,
    "mbi": 0.62,
    "risk_level": "high",
    "triggers": ["ee_score>=0.6", "productivity_delta=-0.25"]
  },
  "recovery": {
    "action": "professional_connect_offered",
    "lock_refs": ["LOCK-HW-04", "LOCK-HW-05", "LOCK-HW-09#4"],
    "user_response": null
  }
}
```

외부 송출 금지 (LOCK-HW-02 PRIVATE). trace_id 포함 구조 로깅 필수. `error{}` 블록은 감지 파이프라인 실패 시 채워짐 (정상 시 null).

---

## §9. Phase 3 테스트 시나리오 (10건)

| # | 시나리오 | 기대 결과 |
|---|---------|----------|
| TS-BP-01 | WLS 연속 7일 80+ 증가 | Critical 등급 승격, LOCK-HW-05 verbatim 안내 트리거 |
| TS-BP-02 | MBI 0.75, productivity_delta -0.30 | High 등급, 전문가 연결 제안, empathy §13.3 재사용 |
| TS-BP-03 | "지쳤어 너무" 입력 (2차 키워드) | High 등급 승격, 응답 헤더 7원칙 #3 투명성 표시 |
| TS-BP-04 | "자살" 직접 입력 | Critical 즉시, 1393 + 1577-0199 verbatim 3초 이내 출력 |
| TS-BP-05 | Low 등급 상태 + opt-out 클릭 | BurnoutSnapshot 수집 중지, 기존 데이터 익명화 옵션 |
| TS-BP-06 | 30일 baseline 부재 상태 (신규 사용자) | baseline 수집 안내, WLS 점수 산출 보류, 명시적 "데이터 부족" 메시지 |
| TS-BP-07 | EE 0.7 + cyn 0.6 + RA 0.6 (전 차원 고) | MBI 0.65 High, Maslach 결과 사용자 제시 (동의 시) |
| TS-BP-08 | 거부 후 5일 경과 High 유지 | 재제안 금지 (7일 interval), 6일째 재제안 가능 확인 |
| TS-BP-09 | LOCK-HW-04 미표시 렌더 결과 | 자동 차단 + [LOCK_VIOLATION:LOCK-HW-04] 이벤트 |
| TS-BP-10 | Critical 상태에서 네트워크 단절 | 로컬 캐시된 1393/1577-0199 verbatim 표시 (외부 API 의존 금지) |

---

## §10. V1 ↔ V2 정합 표

| 항목 | V1 상태 (stub 68 L) | V2 (본 문서, ~L3) | 출처 정합 |
|------|---------------------|-----------------------|----------|
| 번아웃 감지 파이프라인 | 골격만 | §4 7/30/90일 추세 + MBI 3차원 + WLS 공식 | STEP7-P P-023 L420~L425 전수 |
| 업무 부하 점수 | 미정의 | §4.2 WLS 공식 (100점) | V2 신규, plan §7.2 L1281 "업무 부하 점수 산출 공식" |
| 번아웃 4등급 | 미정의 | §4.5 Low/Medium/High/Critical | plan §7.2 L1282 "번아웃 위험 등급" |
| 단계별 개입 | "의존성: 전체 스트레스 관리 모듈" 언급만 | §5 4단계 + §6 위기 경로 | STEP7-P P-023 L426~L431 전수 |
| LOCK-HW-04 비의료 면책 | §2, §5 인용 | §3.1 + §7 + 모든 응답 헤더 | AUTHORITY §3.1 L62 verbatim |
| LOCK-HW-05 위기 전화번호 | 미포함 | §3.2 + §6.1 verbatim 3개소 | AUTHORITY §4 L94~L102 + §B 3개소 |
| LOCK-HW-09 7원칙 | 미포함 | §3.3 + §7.1 체크박스 | AUTHORITY §3.1 L64 / STEP7-P P-010 L192~L199 |

---

## §11. 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-04-10 | v0.1 (V1 stub) | 초기 골격 68 L (Phase 1 산출물, V2 L3 완성 예정 명시) |
| 2026-04-20 | v1.0 (V2-Phase 2) | STAGE 7 STEP_B #2b 세션 2-4 V2 overwrite. §1~§11 전수 신설. STEP7-P P-023 L418~L434 verbatim 대조. LOCK-HW-04 (§3.1 L62) + LOCK-HW-05 (§4 L94~L102 §B 3개소) + LOCK-HW-09 (§3.1 L64 7원칙 체크박스) 전수 준수. 번아웃 4등급 + WLS 공식 + Maslach 3차원 MBI. V2-Phase 2 태그. L3 COMPLETE. |

---

**[V2-Phase 2 태그]** — burnout_prevention.md v1.0 / 2026-04-20 / STAGE 7 STEP_B #2b 세션 2-4 / P-023 V2 / LOCK-HW-04/05/09 전수 준수
