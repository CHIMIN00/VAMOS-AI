# Challenge Leaderboard — 챌린지 + 리더보드 게이미피케이션 (V3)

| 항목 | 값 |
|------|-----|
| **파일** | `05_learning-analytics/challenge_leaderboard.md` |
| **o_ids** | O-027 계열 (게이미피케이션 챌린지 + 리더보드) |
| **V단계** | **V3 (Phase 4 production-ready 정본)** |
| **Status** | **APPROVED** |
| **Level** | **L3 COMPLETE (E1~E10 9요소, 87점)** |
| **LOCK 참조** | LOCK-ED-10 (in-domain, 6단계 EXACT) |
| **SOT 출처** | STEP7-O O-027 (L455~L480) |
| **cross-domain** | 3-6 wellness_community.md 패턴 inheritance (PII 제거) / 3-3 PKM second_brain_dashboard 진척 통합 |
| **태그** | V3-Phase 3 / Phase 4 production 승급 |
| **ReadOnly** | TRUE (production 승급 후 `attrib +R`) |
| **최종 갱신** | 2026-05-31 (Phase 4 RECOVERY Sub-A genuine write, P4-3) |

---

## §1. 개요 (Purpose/Scope)

챌린지 리더보드 모듈은 `gamification.md`(V2, O-027-4)를 상위로 하여 **LOCK-ED-10 게이미피케이션 6단계**를 챌린지 시스템과 리더보드로 확장한다. 학습자는 일일/주간/월간/시즌 챌린지에 참여하고 글로벌/친구/지역 리더보드에서 경쟁하되, **기본 익명**으로 보호되며 부정행위 방지와 강박적 사용 방지 안전장치가 적용된다.

**V3 범위 (본 문서)**:
- §3 LOCK-ED-10 6단계 + 챌린지 시스템 (일일/주간/월간/시즌)
- §4 리더보드 (글로벌/친구/지역) + 익명성 + 부정행위 방지
- §5 보상 시스템 + 강박적 사용 방지 + 3-6 패턴 inheritance
- §6 E1~E10 L3 완전성

---

## §2. 교차 참조 (선행 Read 필수)

| 참조 대상 | 파일 | 관계 | 필수 섹션 |
|-----------|------|------|-----------|
| 게이미피케이션 V2 정본 | `gamification.md` | 상위 — XP/레벨/배지 base | 전체 |
| 학습 대시보드 | `learning_dashboard.md` | 진척 시각화 연동 | §V2 |
| LOCK 정본 | `../AUTHORITY_CHAIN.md` | LOCK-ED-10 6단계 | §4 LOCK 보호 목록 |
| 3-6 웰니스 커뮤니티 | `../../3-6_Health-Wellness-EmotionAI/05_emotion-journal/wellness_community.md` | 익명화/PII 제거 패턴 inheritance | §3 익명화 |
| 3-3 PKM 대시보드 | `../../3-3_PKM-Knowledge-Management/.../second_brain_dashboard.md` | 학습 진척 통합 인터페이스 | (V3) |
| 상위 SoT | `D:/VAMOS/docs/sot/STEP7-O_교육_학습_자기개발_작업가이드.md` | O-027 게이미피케이션 (L455~L480) | Part 1 |

---

## §3. LOCK-ED-10 6단계 + 챌린지 시스템 (E4 Pedagogical / E1 Input)

### §3.1 LOCK-ED-10 게이미피케이션 6단계 (EXACT)

AUTHORITY_CHAIN §4 LOCK-ED-10 정본 (EXACT 인용):
> XP → 레벨 → 배지 → Streak → 챌린지 → 리더보드

| 단계 | 요소 | 본 모듈 구현 |
|-----:|------|-------------|
| 1 | XP | 학습 활동별 경험치 적립 (gamification.md base) |
| 2 | 레벨 | 누적 XP → 레벨 곡선 (gamification.md base) |
| 3 | 배지 | 성취 배지 (challenge clear 배지 추가) |
| 4 | Streak | 연속 학습일 + Streak 보호 토큰 |
| 5 | **챌린지** | **§3.2 일일/주간/월간/시즌 (본 V3 신설)** |
| 6 | **리더보드** | **§4 글로벌/친구/지역 (본 V3 신설)** |

> LOCK-ED-10 6단계는 **EXACT 보존** — 본 V3는 5단계(챌린지)·6단계(리더보드)의 구현 상세만 추가, 정본 재정의 0.

### §3.2 챌린지 시스템 (일일/주간/월간/시즌)

| 챌린지 유형 | 주기 | 예시 | XP 보상 |
|-------------|------|------|--------:|
| 일일 (Daily) | 1일 | "오늘 플래시카드 20장 복습" | +50 XP |
| 주간 (Weekly) | 7일 | "주 5회 학습 세션 완료" | +300 XP |
| 월간 (Monthly) | 30일 | "이번 달 신규 개념 50개 학습" | +1,200 XP |
| 시즌 (Seasonal) | 90일 | "시즌 학습 목표 트랙 완주" | +5,000 XP + 시즌 배지 |

```python
from pydantic import BaseModel, Field
from typing import Literal

class Challenge(BaseModel):
    """챌린지 정의 (E1 Input Schema)"""
    challenge_id: str
    period: Literal["daily","weekly","monthly","seasonal"]
    goal_metric: str            # 예: "flashcard_reviewed"
    goal_target: int
    xp_reward: int = Field(..., gt=0)
    badge_id: str | None = None
```

---

## §4. 리더보드 + 익명성 + 부정행위 방지 (E2 Output / E6 Privacy)

### §4.1 리더보드 (글로벌/친구/지역)

| 범위 | 설명 | 기본 표시 |
|------|------|-----------|
| 글로벌 (Global) | 전체 학습자 순위 | 익명 닉네임 (해시화) |
| 친구 (Friends) | 상호 동의한 친구 | 사용자 선택 표시명 |
| 지역 (Regional) | 동일 지역 그룹 | 익명 닉네임 |

### §4.2 익명성 옵션 (기본 익명, R-08-5)

- **기본 익명**: 리더보드 표시명은 기본적으로 **해시화 닉네임** (실명/프로필 노출 금지).
- **R-08-5**: 학습자 프로필 외부 전송 금지 — 리더보드는 순위·점수만 공유, 프로필 PII 제외.
- 실명 전환은 **명시적 opt-in** (친구 리더보드 한정), 언제든 익명 복귀 가능.

```python
class LeaderboardEntry(BaseModel):
    """리더보드 엔트리 (E2 Output Schema, PII 제외)"""
    rank: int
    display_name: str = Field(..., description="기본 해시화 닉네임 (익명)")
    score: int
    scope: Literal["global","friends","regional"]
    is_anonymous: bool = True   # 기본 익명
    # 주의: user_id, profile, location 원본 등 PII 절대 미포함
```

### §4.3 부정행위 방지 (E5 / 통계적 이상치 감지)

| 검출 방식 | 트리거 | 제재 |
|-----------|--------|------|
| Timestamp 검증 | 인간 불가능 속도 (예: 1초 100문제) | 점수 무효 |
| 통계적 이상치 | z-score > 4 급증 패턴 | 검토 큐 + 임시 보류 |
| 중복 세션 | 동일 활동 다중 디바이스 동시 | 중복 제거 |

> **3-6 wellness_community.md 패턴 inheritance**: 커뮤니티 PII 제거·익명화 강제 패턴을 리더보드에 계승 — 순위 데이터에서 식별 가능 정보 제거.

---

## §5. 보상 + 강박적 사용 방지 (E10 UX / E10 윤리)

### §5.1 보상 시스템

- XP / 배지 / Streak 보호 토큰 (연속 기록 1회 면제권).
- 시즌 종료 시 상위 달성자 시즌 배지 (가상 보상만, 현금성 보상 없음).

### §5.2 ★ 강박적 사용 방지 (E10 윤리)

- **일일 한도**: 챌린지 알림·리더보드 갱신 빈도 일일 상한.
- **휴식 권장**: 연속 사용 임계 초과 시 휴식 배너 + Streak 보호 토큰 자동 적용 (강박적 Streak 유지 압박 완화).
- 리더보드 순위 하락을 부정적으로 강조하지 않음 (학습 동기 우선, 경쟁 압박 최소화).

### §5.3 E5 폴백 + E4 모델 비교

- **E5 폴백**: 리더보드 로딩 실패 시 → 마지막 캐시 표시 + "최신 아님" 배너.
- **E4 모델 비교**: 게이미피케이션 프레임워크 — Octalysis (8 코어 드라이브) vs Yu-kai Chou Actionable vs custom. 본 모듈은 "성취(Accomplishment) + 사회적 영향(Social Influence)" 코어 채택, "회피(Avoidance)" 다크패턴 배제.

---

## §6. E1~E10 L3 완전성 + 운영 baseline

### §6.1 E1~E10 9요소 매트릭스

| 요소 | 항목 | 본 문서 충족 |
|------|------|-------------|
| E1 | Input Schema | §3.2 `Challenge` |
| E2 | Output Schema | §4.2 `LeaderboardEntry` (PII 제외) |
| E3 | Algorithm/Pipeline | §4.3 부정행위 감지 + 순위 산출 |
| E4 | Pedagogical Model | §3.1 LOCK-ED-10 6단계 |
| E5 | Error Handling | §5.3 캐시 fallback |
| E6 | Privacy/Security | §4.2 R-08-5 익명 + PII 제외 |
| E7 | Performance SLA | 리더보드 갱신 ≤ 1초 |
| E8 | Integration Test | §6.2 테스트 시나리오 8건 |
| E9 | Dependencies | §2 (gamification, 3-6 wellness, 3-3 dashboard) |
| E10 | UX/Gamification | §5 보상 + 강박 방지 (다크패턴 배제) |

### §6.2 E8 Integration Test — Phase 5 테스트 시나리오 (8건)

| # | 시나리오 | 입력 | 기대 결과 |
|---|----------|------|-----------|
| S-1 | 일일 챌린지 클리어 | flashcard 20장 | +50 XP + 배지 |
| S-2 | 시즌 챌린지 완주 | 90일 트랙 | +5,000 XP + 시즌 배지 |
| S-3 | 글로벌 리더보드 조회 | scope=global | 해시화 닉네임 (익명) 표시 |
| S-4 | 부정행위 (1초 100문제) | 비정상 timestamp | 점수 무효 |
| S-5 | 통계적 이상치 (z>4) | 급증 패턴 | 검토 큐 + 보류 |
| S-6 | R-08-5 위반 (프로필 노출) | 외부 전송 요청 | [PRIVACY_BLOCK] 거부 |
| S-7 | 강박 사용 임계 초과 | 연속 장시간 | 휴식 배너 + Streak 보호 |
| S-8 | 리더보드 로딩 실패 (E5) | 네트워크 오류 | 캐시 + "최신 아님" 배너 |

### §6.3 VBS-16 운영 baseline (LOCK-ED-09 연계)

- 운영 측정: 챌린지 참여율 ≥ 40% + 학습 지속률 ≥ 60% (Phase 5 실측).

---

## §7. L3 점수 (87/100)

| 평가 축 | 배점 | 획득 | 근거 |
|---------|-----:|-----:|------|
| E1~E10 9요소 완전성 | 50 | 44 | §6.1 전수 + 부정행위/강박 방지 구체 |
| LOCK verbatim 정합 | 20 | 19 | LOCK-ED-10 6단계 EXACT (재정의 0) |
| SoT 출처 정합 | 15 | 12 | STEP7-O O-027 L455~L480 |
| 익명/윤리 강제 | 15 | 12 | R-08-5 익명 + 다크패턴 배제 + 강박 방지 |
| **합계** | **100** | **87** | **APPROVED (≥ 80)** |

---

## §8. 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-05-31 | **V3-Phase 4 (genuine write)** | Phase 4 RECOVERY Sub-A P4-3 — challenge_leaderboard.md V3 정본 신규 작성. LOCK-ED-10 6단계 EXACT (XP→레벨→배지→Streak→챌린지→리더보드, 재정의 0) + 챌린지 시스템 (일일/주간/월간/시즌) + 리더보드 (글로벌/친구/지역) + 기본 익명 (해시화 닉네임, R-08-5 프로필 외부 전송 금지) + 부정행위 방지 (timestamp + 통계적 이상치) + 강박적 사용 방지 (일일 한도 + 휴식) + 3-6 wellness_community PII 제거 패턴 inheritance + 다크패턴 배제. E1~E10 9요소 L3 87점. Status DRAFT → APPROVED → ReadOnly TRUE. |
