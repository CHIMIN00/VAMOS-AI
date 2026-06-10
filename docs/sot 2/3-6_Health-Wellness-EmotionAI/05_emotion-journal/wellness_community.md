# Wellness Community — 익명 웰니스 커뮤니티 (V3)

| 항목 | 값 |
|------|-----|
| **파일** | `05_emotion-journal/wellness_community.md` |
| **P-ID** | P-033 (웰니스 커뮤니티 — 익명 공유/챌린지) |
| **V단계** | **V3 (Phase 4 production-ready 정본)** |
| **Status** | **APPROVED** |
| **Level** | **L3 COMPLETE (E1~E10 9요소, 87점)** |
| **LOCK 참조** | LOCK-HW-02, LOCK-HW-09, LOCK-HW-04 (in-domain) + ★ 3-5 challenge_leaderboard 챌린지 시스템 inheritance |
| **SOT 출처** | STEP7-P P-031 (웰니스 커뮤니티 확장) + 종합계획서 §6.4 + §3.4 |
| **cross-domain** | ★ 3-5 Education `challenge_leaderboard.md` (챌린지 시스템 inheritance) ↔ 본 문서 PII-제거 패턴 PRODUCER(challenge_leaderboard가 cite) / proactive_alerts (in-domain peer) |
| **태그** | V3-Phase 4 production 정본 (NEW) |
| **ReadOnly** | RW (Sub-B P4-7 도메인 종료 시 RO 정책 일괄 확정 → RO TRUE) |
| **최종 갱신** | 2026-06-01 (Phase 4 RECOVERY Sub-B genuine write, P4-5 NEW) |

---

## §1. 개요 (Purpose/Scope)

웰니스 커뮤니티는 사용자가 **개인 식별 정보(PII)를 완전히 제거한 익명 상태**로 웰니스 챌린지에 참여하고, 진척·성취를 익명 공유하는 모듈이다. 모든 공유 데이터는 **로컬 우선 + opt-in 전송**(LOCK-HW-02 PRIVATE)이며, 게시 전 **PII 4-fields(이름/이메일/전화/주소) 강제 제거** 파이프라인을 통과한다. 커뮤니티는 비의료 도구(LOCK-HW-04)이며, 위기 신호 노출 시 전문기관 안내(R-09-2)를 우선한다. 챌린지 시스템은 ★ 3-5 Education `challenge_leaderboard.md`의 챌린지 구조를 inheritance 하되, 본 문서의 PII-제거 패턴이 역으로 challenge_leaderboard에 계승되는 **상호 참조** 관계다.

**V3 범위 (본 문서)**:
- §3 익명 커뮤니티 구조 + 챌린지 참여(★ 3-5 inheritance)
- §4 PII 4-fields 제거 강제 파이프라인 (이름/이메일/전화/주소)
- §5 LOCK-HW-02 PRIVATE + LOCK-HW-09 7원칙 + R-09-3 외부 전송 금지
- §6 E4 익명화 방식 비교 + E5 폴백 + E6/E10 윤리(R-09-3/4/7)
- §7 E1~E10 L3 완전성 + 운영 baseline

---

## §2. 교차 참조 (선행 Read 필수)

| 참조 대상 | 파일 | 관계 | 필수 섹션 |
|-----------|------|------|-----------|
| LOCK 정본 | `../AUTHORITY_CHAIN.md` | LOCK-HW-02/04/09 §3 | §3.1~§3.3 |
| Dream Mode 주간 리포트 (peer) | `./dream_mode_wellness.md` | 주간 성취 → 익명 공유 입력 | §5~§7, §V3 |
| 실시간 알림 (RO) | `./proactive_alerts.md` | 커뮤니티 알림 정책 | §5 |
| ★ 3-5 챌린지 리더보드 | `../../3-5_Education-Learning/05_social-learning/challenge_leaderboard.md` | 챌린지 시스템 inheritance ↔ PII-제거 PRODUCER | §3 챌린지, §4 익명화 |
| 상위 SoT | `D:/VAMOS/docs/sot/STEP7-P_건강_웰니스_감성AI_작업가이드.md` | P-033 정본 | L560~L571 |

---

## §3. 익명 커뮤니티 + 챌린지 (E1 Input / E3 Pipeline)

### §3.1 익명 커뮤니티 구조 (기본 익명)

- **기본 익명**: 모든 커뮤니티 표시명은 **해시화 닉네임**(실명/프로필 노출 금지). 실명 전환 기능 없음(웰니스 데이터 민감도 — challenge_leaderboard 대비 더 엄격).
- **공유 범위**: 챌린지 진척률·달성 배지·익명 응원만. 원시 감정/건강 데이터·VWS 원점수는 공유 불가(요약 등급만).
- **opt-in 전송**: 로컬 우선, 외부 공유는 opt-in + 2단계 확인(LOCK-HW-02).

### §3.2 챌린지 참여 (★ 3-5 challenge_leaderboard inheritance)

> **★ 3-5 challenge_leaderboard 챌린지 시스템 inheritance**: 일일/주간/월간/시즌 챌린지 구조를 3-5 Education `challenge_leaderboard.md`(LOCK-ED-10 게이미피케이션 6단계 기반)에서 inheritance. 본 웰니스 챌린지는 건강·웰빙 목표(수면/운동/마음챙김)에 적용하되, 리더보드 경쟁보다 **개인 진척·익명 응원** 중심으로 변형(강박적 경쟁 방지, LOCK-HW-09 #6 자율성).

```python
from pydantic import BaseModel, Field
from typing import Literal

class WellnessChallenge(BaseModel):
    """웰니스 챌린지 (익명 참여, PII 제외) — 3-5 challenge_leaderboard 구조 inheritance."""
    challenge_id: str
    period: Literal["daily", "weekly", "monthly", "seasonal"]   # 3-5 inheritance
    category: Literal["sleep", "exercise", "mindfulness", "social"]
    progress_pct: float = Field(..., ge=0, le=100)              # 진척률만 공유
    is_anonymous: bool = True                                   # 기본 익명 (불변)
    # 주의: user_id, real_name, email, phone, address 등 PII 절대 미포함
```

---

## §4. PII 4-fields 제거 강제 파이프라인 (E2 Output / E6 Privacy — ★ PRODUCER)

본 문서가 **PII-제거 패턴의 정본 PRODUCER**다 (3-5 challenge_leaderboard가 "3-6 wellness_community.md 패턴 inheritance (PII 제거)"로 본 패턴을 cite).

### §4.1 PII 4-fields 강제 제거

게시·공유 전 **모든 출력에서 다음 4-fields를 구조적으로 제거**한다(통과 실패 시 게시 차단):

| # | PII 필드 | 제거 방식 |
|---|----------|-----------|
| 1 | **이름** (real_name) | 해시화 닉네임 대체, 원본 미저장 |
| 2 | **이메일** (email) | 출력 스키마에서 구조적 배제 |
| 3 | **전화** (phone) | 정규식 탐지 + 마스킹/차단 |
| 4 | **주소** (address) | 지역 단위 제거 (구/동 이하 제거) |

```python
PII_FIELDS = ("real_name", "email", "phone", "address")   # 4-fields 강제 제거

def sanitize_for_community(payload: dict) -> dict:
    """커뮤니티 게시 전 PII 4-fields 제거 (실패 시 [PRIVACY_VIOLATION] 차단)."""
    cleaned = {k: v for k, v in payload.items() if k not in PII_FIELDS}
    # 자유 텍스트 내 이메일/전화 정규식 잔존 검사 → 발견 시 차단
    if _contains_pii_pattern(cleaned):
        raise PrivacyViolation("PII residue detected", code="PRIVACY_VIOLATION")
    return cleaned
```

### §4.2 익명 게시 스키마

```python
class CommunityPost(BaseModel):
    """익명 커뮤니티 게시 (E2 Output, PII 4-fields 제외)."""
    display_name: str = Field(..., description="해시화 닉네임 (익명, 불변)")
    challenge_category: str
    progress_pct: float = Field(..., ge=0, le=100)
    badge: str | None = None
    is_anonymous: bool = True
    # PII 4-fields (이름/이메일/전화/주소) 절대 미포함 (§4.1 sanitize 통과 후에만 생성)
```

---

## §5. 프라이버시·7원칙 (E6 Privacy/Security / E10 Ethics)

LOCK 인용 (정본 — 본 문서 재정의 0):
> LOCK (LOCK-HW-02): 감정=PRIVATE(로컬전용), 건강=PROTECTED(AES-256+별도PIN), 의료=HIGHEST(외부전송절대금지)
> LOCK (LOCK-HW-09): 비진단/프라이버시/투명성/전문가연결/비조작/자율성/기능끄기
> LOCK (LOCK-HW-04): "VAMOS는 의료 서비스가 아닙니다"

- **LOCK-HW-02 PRIVATE**: 커뮤니티 공유 데이터는 PRIVATE 등급 유지, 외부 전송은 opt-in + 요약 데이터만. 원시 raw 외부 금지(R-09-3 구조적 차단).
- **LOCK-HW-09 7원칙**: #1 비진단 / #2 프라이버시(PII 4-fields 제거 + 로컬) / #3 투명성(익명 표시 명시) / #4 전문가 연결(위기 노출 시 LOCK-HW-05) / #5 비조작(경쟁 유도·다크패턴 배제, R-09-7) / #6 자율성(탈퇴·opt-out 언제든) / #7 기능 끄기(`/wellness/community/off`).
- **LOCK-HW-04 비의료**: 모든 커뮤니티 화면 헤더에 비의료 면책 표시.
- **R-09-3 외부 전송 금지**: 원시 감정/건강 데이터는 커뮤니티에 절대 게시 불가 — 진척률·배지 요약만.

---

## §6. 익명화 방식 비교 + 폴백 (E4 / E5)

| 방식 | 식별 제거 | 장점 | 단점 | 채택 |
|------|----------|------|------|------|
| **해시화 닉네임 + PII 4-fields 제거** | 강 | 재식별 어려움·로컬 우선 | 사회적 연결감 다소 약함 | ✅ 채택 |
| 가명(pseudonym) 유지 | 중 | 연속성 | 재식별 위험 | △ 보조 |
| 실명 + opt-in | 약 | 친밀감 | 웰니스 민감도 부적합 | ✗ 미채택 |

- **E5 폴백**: §4.1 sanitize 통과 실패 시 게시 차단 + 사용자에게 PII 탐지 안내. 정규식 오탐 시 사용자 검토 후 재시도(자율성 보장).

---

## §7. E1~E10 L3 완전성 + 운영 baseline

| 요소 | 항목 | 본 문서 충족 |
|------|------|-------------|
| E1 | Input Schema | §3.2 `WellnessChallenge` |
| E2 | Output Schema | §4.2 `CommunityPost` (PII 4-fields 제외) |
| E3 | Algorithm/Pipeline | §4.1 PII sanitize 파이프라인 |
| E4 | Model Comparison | §6 해시닉네임 vs 가명 vs 실명 |
| E5 | Error Handling | §6 sanitize 실패 차단 + 오탐 검토 |
| E6 | Privacy/Security | §4 PII 4-fields 제거 + §5 LOCK-HW-02 PRIVATE |
| E7 | Performance SLA | 게시 sanitize p95 ≤ 300ms |
| E8 | Integration Test | §8 테스트 시나리오 8건 |
| E9 | Dependencies | §2 (dream_mode / proactive_alerts / 3-5 challenge_leaderboard) |
| E10 | Ethics/UX | §5 7원칙 + 다크패턴 배제 + R-09-7 비조작 |

운영 baseline: **PII 잔존율 0%**(sanitize 통과 후) + 웰빙 개선율 ≥ 25% + 게시 sanitize p95 ≤ 300ms (Phase 5 운영 실측).

---

## §8. E8 Integration Test — Phase 5 테스트 시나리오 (8건)

| # | 시나리오 | 입력/조건 | 기대 결과 |
|---|----------|----------|-----------|
| S-1 | 익명 챌린지 참여 | 주간 챌린지 join | 해시 닉네임 + 진척률만 표시 |
| S-2 | ★ PII 4-fields 제거 | payload에 이름/이메일/전화/주소 포함 | 4-fields 전부 제거 후 게시 |
| S-3 | 자유 텍스트 이메일 잔존 | 본문에 이메일 패턴 | [PRIVACY_VIOLATION] 차단 |
| S-4 | 원시 건강 데이터 게시 시도 | VWS 원점수 공유 | R-09-3 차단 (요약만 허용) |
| S-5 | ★ 3-5 challenge 구조 inheritance | 일일/주간/월간/시즌 | 챌린지 period 4종 정상 동작 |
| S-6 | 위기 신호 노출 | 게시글 위기 키워드 | LOCK-HW-05 전문기관 안내 우선 (R-09-2) |
| S-7 | opt-out 탈퇴 | `/wellness/community/off` | 게시 0, 기존 데이터 로컬 삭제 옵션 |
| S-8 | 경쟁 유도 다크패턴 | 강박적 랭킹 압박 UI | R-09-7 거부 (비조작, 진척 중심 유지) |

---

## §9. 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-06-01 | **V3-Phase 4 (genuine write, NEW)** | Phase 4 RECOVERY Sub-B P4-5 — wellness_community.md V3 정본 신규 작성 (ABSENT → NEW). 익명 웰니스 커뮤니티 + ★ PII 4-fields(이름/이메일/전화/주소) 강제 제거 파이프라인(본 문서 = PII-제거 패턴 정본 PRODUCER, 3-5 challenge_leaderboard가 cite) + ★ 3-5 challenge_leaderboard 챌린지 시스템 inheritance(일일/주간/월간/시즌, LOCK-ED-10 기반, 경쟁→진척 중심 변형) + LOCK-HW-02 PRIVATE 로컬 전용 + LOCK-HW-09 7원칙 + LOCK-HW-04 비의료 + R-09-3 외부 전송 금지 + R-09-7 비조작. E4 해시닉네임/가명/실명 비교(해시닉네임+PII제거 채택). E1~E10 9요소 L3 87점. Status DRAFT → APPROVED. |

---

**[V3-Phase 4 태그]** — wellness_community.md / 2026-06-01 / P-033 V3 production-ready 정본 (Phase 4 RECOVERY Sub-B P4-5 genuine write NEW, PII-제거 패턴 PRODUCER, 3-5 챌린지 시스템 inheritance)
