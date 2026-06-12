"""I-8 Policy Engine (V0 stub) — Non-goal deny + 비용 downshift 신호.

정본: PART2 V0-STEP-4 #4 + BASE-1.3 §2 Non-goal 7항(L96~128 — deny 목록 정본, 창작 금지).
PolicyCheck.decision은 contracts 정본 enum(deny|restrict|allow) — PART2의 "downshift" 표기는
restrict + fallback_id=FB_COST_DOWNSHIFT로 표현(스키마 enum 보존).
"""

from __future__ import annotations

import uuid

from vamos_core.infra.logger import log_event
from vamos_core.schemas.contracts import IntentFrame, PolicyCheck

#: BASE-1.3 §2 Non-goal 절대 금지 7항 (verbatim — 항목명·번호 정본)
NON_GOALS: tuple[tuple[str, str], ...] = (
    ("2.1", "실거래·주문·계좌·API 연동"),
    ("2.2", "불법 행위·해킹·권한 상승"),
    ("2.3", "의료·법률 단정적 판단 또는 대리 결정 제공"),
    ("2.4", "민감 개인정보 장기 저장"),
    ("2.5", "저작권·약관 위반"),
    ("2.6", "P2 도메인 자동 생성 금지"),
    ("2.7", "위험 기능 자동 실행 금지"),
)

#: V0 휴리스틱 매칭 키워드 (구현 상세 — PART2 L1122 "Non-goal 목록 하드코딩 (예: ...)" 예시 경로.
#: deny 근거 목록 자체는 위 NON_GOALS 정본)
_NON_GOAL_KEYWORDS: dict[str, tuple[str, ...]] = {
    "2.1": ("매수해", "매도해", "주문 실행", "실거래", "계좌에서", "주식 매매 실행"),
    "2.2": ("해킹", "침투 코드", "권한 상승", "타인 계정"),
    "2.3": ("암입니까", "서명해도 됩니까", "진단해줘"),
    "2.4": ("주민등록번호 저장", "비밀번호 저장", "계좌번호 저장", "개인정보 수집"),
    "2.5": ("유료 콘텐츠 전문 복사", "크랙", "불법 다운로드"),
    "2.6": ("P2 자동 활성", "승인 없이 P2"),
    "2.7": ("무감독 실행", "일괄 삭제", "자동으로 전부 실행"),
}


class PolicyEngine:
    """check(intent_frame, cost_usage_ratio) -> PolicyCheck."""

    async def check(
        self,
        intent_frame: IntentFrame,
        trace_id: str,
        cost_usage_ratio: float = 0.0,
    ) -> PolicyCheck:
        text = f"{intent_frame.user_goal}"
        matched = [
            (num, label)
            for num, label in NON_GOALS
            if any(kw in text for kw in _NON_GOAL_KEYWORDS.get(num, ()))
        ]
        if matched:
            check = PolicyCheck.model_validate(
                {
                    "check_id": f"pc_{uuid.uuid4().hex[:12]}",
                    "decision": "deny",
                    "reasons": [f"Non-goal {num}: {label}" for num, label in matched],
                    "rule_refs": [f"BASE-1.3 §{num}" for num, _ in matched],
                    "detected_sensitive_types": [],
                    "fallback_id": "FB_DENY_WITH_REASON",
                }
            )
            log_event(
                "oc.i5.policy.blocked",
                producer="I-8",
                payload={"check_id": check.check_id, "reasons": check.reasons},
                trace_id=trace_id,
                severity="warn",
                links={"failure_code": ["OC_ERR_NONGOAL"],
                       "fallback_id": ["FB_DENY_WITH_REASON"]},
            )
            return check
        if cost_usage_ratio >= 0.8:  # 비용 상한 근접 — downshift 신호 (PART2 #4)
            return PolicyCheck.model_validate(
                {
                    "check_id": f"pc_{uuid.uuid4().hex[:12]}",
                    "decision": "restrict",
                    "reasons": [
                        f"비용 사용률 {cost_usage_ratio:.0%} ≥ 80% — force_mini 다운시프트"
                    ],
                    "rule_refs": ["D2.0-07 §4.2 (DEC-005)"],
                    "detected_sensitive_types": [],
                    "fallback_id": "FB_COST_DOWNSHIFT",
                }
            )
        return PolicyCheck.model_validate(
            {
                "check_id": f"pc_{uuid.uuid4().hex[:12]}",
                "decision": "allow",
                "reasons": [],
                "rule_refs": [],
                "detected_sensitive_types": [],
            }
        )
