"""Defense Layer 3 — NEVER_AUTO 10항목 frozenset 하드코딩 (A21, PHASE3-DEC-008).

정본: SDAR §5.1 L594~603 (RA_NEVER_01~10 verbatim — LOCK 전사, 창작 0).
config 수정으로도 우회 불가 — 소스 수정+재배포만 가능 (최후 방어).
각 계층(L1 config LOCK / L2 5-Gate / L3 본 모듈)은 다른 계층 실패와 무관하게 단독 작동.
"""

from __future__ import annotations

from typing import Final

#: SDAR §5.1 NEVER_AUTO 수리 액션 (절대 자동 실행 금지) — RA_NEVER_01~10 verbatim
NEVER_AUTO_ACTIONS: Final[dict[str, str]] = {
    "RA_NEVER_01": "modify_safety_rules",
    "RA_NEVER_02": "change_cost_ceiling",
    "RA_NEVER_03": "alter_approval_flow",
    "RA_NEVER_04": "modify_non_goals",
    "RA_NEVER_05": "change_audit_format",
    "RA_NEVER_06": "alter_data_retention",
    "RA_NEVER_07": "modify_user_consent",
    "RA_NEVER_08": "escalate_own_privilege",
    "RA_NEVER_09": "disable_guardrails",
    "RA_NEVER_10": "bypass_gate",
}

#: L3 frozenset 정본 (DEC-008 — "코드 내 frozenset 하드코딩")
NEVER_AUTO: Final[frozenset[str]] = frozenset(NEVER_AUTO_ACTIONS.values())

#: V0 사용자 입력 휴리스틱 탐지 키워드 (구현 상세 — 액션 분모는 위 frozenset 정본)
_DETECTION_KEYWORDS: Final[dict[str, tuple[str, ...]]] = {
    "modify_safety_rules": ("안전 규칙 변경", "안전 규칙 수정", "safety rule 변경"),
    "change_cost_ceiling": ("비용 상한 변경", "비용 한도 올려", "monthly_limit 변경",
                            "예산 상한 수정"),
    "alter_approval_flow": ("승인 흐름 변경", "승인 절차 건너뛰", "승인 없이 진행하도록 바꿔"),
    "modify_non_goals": ("non-goal 변경", "금지 목록 수정", "금지 항목 삭제"),
    "change_audit_format": ("감사 로그 형식 변경", "audit 포맷 수정"),
    "alter_data_retention": ("보존 정책 변경", "retention 변경", "로그 보존 기간 수정"),
    "modify_user_consent": ("동의 설정 변경", "동의 없이 처리하도록"),
    "escalate_own_privilege": ("권한 상승시켜", "관리자 권한 부여해", "스스로 권한"),
    "disable_guardrails": ("guardrails 꺼", "가드레일 비활성", "안전장치 꺼"),
    "bypass_gate": ("게이트 우회", "gate 우회", "게이트 건너뛰"),
}


def is_never_auto(action: str) -> bool:
    """액션이 NEVER_AUTO 10항목에 해당하는지 — L3 단독 판정 (다른 계층 무관)."""
    return action in NEVER_AUTO


def detect_never_auto(text: str) -> str | None:
    """사용자 입력에서 NEVER_AUTO 액션 요청 탐지 (V0 휴리스틱) — 매칭 액션명 반환."""
    for action, keywords in _DETECTION_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return action
    return None
