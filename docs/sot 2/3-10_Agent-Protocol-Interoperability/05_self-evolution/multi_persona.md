# 멀티 페르소나 에이전트 — K-065 (V3 신규 L3, Phase 4 production-ready 정본)

> **STEP7-K**: K-065 멀티 페르소나 에이전트 (L1254~L1270 원문 / `150720a3496f557d359a421dcbf0922ebe5b1e4fbaa06611eff40e0865177539`)
> **레벨**: L3 (V3-Phase 3 SPEC 완료 → Phase 4 production 승급, STEP7-K "V1 기본 프롬프트 선행 → V2 자동전환 → V3 컨텍스트 자동 선택")
> **정본 소유**: #13 Agent-Protocol-Interoperability / 05_self-evolution (VAMOS 독자 혁신 영역)
> **V 스코프**: V3-Phase 3 (CFL-AP-006 K-065 V 로드맵 정정 후 — "V1 (프롬프트 기반) → V2 (자동 전환)" Phase 1/2 분리 명시 / V3 컨텍스트→페르소나 자동 선택 알고리즘)
> **Phase 4 태그**: V3-Phase 4 production-ready 정본 승급 (RECOVERY genuine write, P4-1)
> **Status**: APPROVED (DRAFT → APPROVED, 2026-06-03 Phase 4 production promotion)
> **Last-reviewed**: 2026-06-03
> **upstream baseline**: STEP7-K sha256 `150720a3496f557d359a421dcbf0922ebe5b1e4fbaa06611eff40e0865177539`

---

## §1. 교차 참조 블록

| 정본 문서 | 섹션 | 참조 내용 |
|----------|------|----------|
| STEP7-K (Level 2) | L1254~L1270 | K-065 원문 (페르소나 정의/컨텍스트 기반 자동 전환/사용자별 학습) |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-01 | VamosMessage 6필드 — 페르소나 전환 이벤트 전달 스키마 |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-02 | Permission Level 0~5 — 페르소나별 권한 상한 격리 |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-10 | Confidence < 50% HITL (06_autonomy-safety 정본, 본 문서 참조자) — 페르소나 선택 confidence |
| AUTHORITY_CHAIN.md | §4 | 자기진화 전략 #13 정본 소유 |
| 구조화_종합계획서.md | §7.5 P3-1 L1426~L1469 | Phase 3 V3 K-065 멀티페르소나 자동 전환 |
| 05_self-evolution/dream_mode.md | §6 | K-061 — Dream Mode 가 페르소나별 프롬프트 최적화 제공 |
| 05_self-evolution/multi_user.md | §3 tenant | K-066 — 멀티유저 × 페르소나 교차 (사용자별 페르소나 세트) |
| 06_autonomy-safety/guardrail_rules.md (V2) | §V2.2 | LOCK-AP-10 정본 — 페르소나 선택 confidence < 0.5 → HITL |
| 06_autonomy-safety/permission_matrix.md (V2) | §V2.1 | 페르소나별 권한 레벨 상한 매핑 |
| 6-4 Memory-RAG-Storage | 사용자 컨텍스트 메모리 | 페르소나 선택 입력 데이터 정본 |

> **R6 준수**: What+How 전용. 페르소나 선택 confidence < 0.5 HITL 트리거의 임계 정본은 06_autonomy-safety (LOCK-AP-10 DEFINED-HERE).

---

## §2. Purpose & Scope (L3 D1~D8 — E1 목표/E2 범위)

### 2.1 멀티 페르소나 5대 요건 (STEP7-K L1254~L1270 원문)

| 요건 | 원문 | 본 문서 섹션 |
|------|------|-------------|
| 페르소나 정의 schema (역할/톤/제약) | L1255 | §4 페르소나 정의 |
| 컨텍스트 기반 자동 전환 (V3) | L1257 | §5 자동 전환 알고리즘 |
| 사용자별 페르소나 세트 학습 | L1259 | §6 학습·개인화 |
| 페르소나별 권한 격리 (LOCK-AP-02) | L1261 | §4.3 권한 상한 |
| 전환 confidence < 0.5 → HITL | L1263 | §7 confidence 게이트 |

### 2.2 범위 경계 (E2)

| 영역 | 본 문서 | 정본 소유 |
|------|--------|----------|
| 페르소나 정의·전환·개인화 | ✅ | — |
| 페르소나 선택 confidence HITL 임계 | 참조 | 06_autonomy-safety LOCK-AP-10 정본 |
| 멀티유저 tenant 격리 | ❌ | 05_self-evolution/multi_user.md (K-066) |
| 사용자 컨텍스트 메모리 저장 | 참조 | 6-4 Memory-RAG-Storage |
| 프롬프트 최적화 실행 | ❌ | 4-4 MLOps-LLMOps (Dream Mode 경유) |

### 2.3 VAMOS 독자 혁신 포지셔닝

| 비교 대상 | 기존 AI | VAMOS 멀티 페르소나 |
|----------|---------|--------------------|
| ChatGPT/Claude Custom Instructions | 사용자가 1개 시스템 프롬프트 수동 설정 | 컨텍스트(업무/학습/일상)에 따라 페르소나 자동 전환 + 개인화 학습 |

---

## §3. 공통 자료 구조 Import (E3 인터페이스)

```python
from sot2_domain.agent_protocol_interoperability.types import (
    VamosMessage,        # LOCK-AP-01 6필드
    GatePolicy,
    PermissionLevel,     # LOCK-AP-02 0~5
)
from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, List
from datetime import datetime
from enum import Enum
```

---

## §4. 페르소나 정의 schema (D1 Input / E4 데이터 모델)

### 4.1 PersonaProfile

```python
class PersonaProfile(BaseModel):
    persona_id: str
    name: str                              # "업무 비서" / "학습 튜터" / "일상 동반자"
    role_prompt: str                       # 역할·톤·제약 시스템 프롬프트
    allowed_tools: List[str]
    max_permission_level: int              # LOCK-AP-02 0~5 — 페르소나별 상한
    tone: Literal["formal", "casual", "concise", "empathetic"]
    domain_hints: List[str]                # 컨텍스트 매칭 키워드
    embedding: List[float] = Field(default_factory=list)  # domain_hints 임베딩 (로드 시 계산, §5.1)
    safety_overrides: Dict[str, bool]      # 페르소나별 가드레일 강화 플래그
```

### 4.2 기본 페르소나 세트 (V1 프롬프트 기반 inheritance)

| persona_id | 역할 | max_permission_level | tone |
|-----------|------|:--------------------:|------|
| `work_assistant` | 업무 비서 (일정/문서/이메일 초안) | L4 (외부, HITL) | formal |
| `learning_tutor` | 학습 튜터 (설명/퀴즈/피드백) | L2 (수정) | empathetic |
| `daily_companion` | 일상 동반자 (대화/리마인더) | L1 (생성) | casual |
| `finance_advisor` | 금융 보조 (조언만, 실행 금지) | L2 (수정, L5 금융 영구 금지) | concise |

### 4.3 페르소나별 권한 상한 격리 (LOCK-AP-02 엄수)

페르소나 전환은 **권한 상한을 상승시키지 못한다**. 각 페르소나의 `max_permission_level` 은 LOCK-AP-02 0~5 범위 내 상한 고정이며, 페르소나 전환으로 L3+ 자동 승격 시도 시 §7 confidence 게이트 + HITL 강제.

---

## §5. 컨텍스트 기반 자동 전환 알고리즘 (D3 Algorithm / E5 — V3 핵심)

### 5.1 전환 파이프라인 (Big-O: O(p) — p 페르소나 수, 상수 시간)

```
1. 사용자 입력 + 세션 컨텍스트(최근 N턴 + 활성 앱 + 시간대) 수집
2. 각 PersonaProfile.domain_hints 와 컨텍스트 임베딩 코사인 유사도 산출
3. softmax → persona_score[p] (합=1.0)
4. argmax 페르소나 선택 + select_confidence = max(persona_score)
5. select_confidence ≥ 0.50 → 자동 전환 / < 0.50 → HITL (LOCK-AP-10)
6. 전환 시 PersonaSwitchEvent emit (VamosMessage, trace_id)
7. 직전 페르소나 대비 권한 상한 상승 시 추가 HITL
```

### 5.2 자동 전환 confidence 산식 (LOCK-AP-10 참조자)

```python
def select_persona(ctx_embedding, personas: List[PersonaProfile]) -> tuple[str, float]:
    scores = {p.persona_id: cosine(ctx_embedding, p.embedding) for p in personas}
    total = sum(math.exp(s) for s in scores.values())
    probs = {pid: math.exp(s) / total for pid, s in scores.items()}
    best = max(probs, key=probs.get)
    return best, probs[best]   # confidence < 0.50 → HITL (06_autonomy-safety 정본)
```

### 5.3 전환 히스테리시스 (drift 방지 — R-13-6)

연속 페르소나 플리핑 방지: 직전 전환 후 `min_dwell = 3턴` 또는 confidence 차이 ≥ 0.15 일 때만 재전환. `max_strategy_drift` (06_autonomy-safety 정본) 초과 시 전환 동결 + HITL 보고.

---

## §6. 사용자별 학습·개인화 (E6 — Dream Mode 연동)

| 학습 신호 | 출처 | 적용 |
|----------|------|-----|
| 사용자 명시적 페르소나 선택 (수동 override) | UI | domain_hints 가중치 +0.1 |
| 페르소나 전환 후 만족도 (재전환/이탈) | 세션 텔레메트리 | 음의 보상 → drift 검증 후 조정 |
| Dream Mode 페르소나별 프롬프트 최적화 | dream_mode.md §6 | role_prompt shadow 승격 (L2) |

> ML 기반 페르소나 자동 학습(강화학습 보상 모델)은 **Phase 4+ 이월** — 본 V3 는 규칙 기반 + 가중치 조정까지.

---

## §7. Confidence 게이트 + Phase 별 복구 흐름 + Confidence Penalty (E7)

| 이벤트 | Confidence Penalty | HITL (< 0.50) |
|--------|:-----------------:|:-------------:|
| 페르소나 선택 confidence < 0.50 | 트리거 자체 | ✅ (사용자 확인) |
| 페르소나 전환으로 권한 상한 상승 시도 | -0.40 | ✅ (즉시 abort) |
| 연속 플리핑 (min_dwell 위반) | -0.10 | 누적 기준 |
| max_strategy_drift 초과 | -0.20 | ✅ |
| finance_advisor L5 금융 실행 시도 | -0.50 | ✅ (영구 차단) |

> LOCK-AP-10 재정의 없음 — 06_autonomy-safety/guardrail_rules.md (P2-6 정본) cumulative 기준 (`base_confidence - sum(event_penalties_{24h}) - cumulative_penalty_{24h} < 0.50`).

---

## §8. 에스컬레이션 페이로드 Python Class (E8)

```python
class PersonaEscalation(BaseModel):
    trace_id: str
    event_class: Literal[
        "low_select_confidence",
        "permission_elevation_attempt",
        "persona_flipping",
        "strategy_drift_exceeded",
        "finance_execution_attempt",
    ]
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    confidence_delta: float = Field(..., le=0.0, ge=-1.0)
    from_persona: Optional[str]
    to_persona: Optional[str]
    recommended_action: Literal[
        "request_user_confirm",
        "block_elevation",
        "freeze_switching",
        "escalate_hitl_L3",
    ]
    occurred_at: datetime
```

---

## §9. LOCK 매핑 5필드 표 (E9)

| LOCK ID | 항목 | 원본 문서 | 값 | 재정의 | 본 문서 적용 지점 |
|---------|------|----------|-----|--------|------------------|
| LOCK-AP-01 | 프로토콜 메시지 포맷 | STEP7-K, D2.0-05 | VamosMessage 6필드 | 금지 | §3 import + §5.1 PersonaSwitchEvent trace_id |
| LOCK-AP-02 | 에이전트 권한 레벨 | STEP7-K K-041 | Permission Level 0~5 | 금지 | §4.3 페르소나별 max_permission_level 상한 격리 |
| LOCK-AP-10 | Confidence 임계값 | DEFINED-HERE (본 도메인 06_autonomy-safety 정본; MASTER_SPEC §5/§7.9 참조) | HITL 트리거 < 50% | 금지 | §5.2 select_confidence < 0.50 → HITL (참조자, 재정의 없음) |

---

## §10. Phase 3 테스트 시나리오 (≥ 10건, E10)

| # | ID | 설명 | 기대 결과 |
|---|----|------|----------|
| 1 | MP-01 | 업무 컨텍스트 입력 → work_assistant 자동 선택 | ✅ §5.1 |
| 2 | MP-02 | select_confidence 0.42 → HITL 트리거 | ✅ LOCK-AP-10 |
| 3 | MP-03 | learning_tutor → work_assistant 권한 상승 전환 시 추가 HITL | ✅ §4.3 |
| 4 | MP-04 | 연속 플리핑 (min_dwell 3턴 위반) → 전환 차단 | ✅ §5.3 |
| 5 | MP-05 | max_strategy_drift 초과 → 전환 동결 + HITL 보고 | ✅ §7 |
| 6 | MP-06 | finance_advisor L5 금융 실행 시도 → 영구 차단 | ✅ §4.2/§7 |
| 7 | MP-07 | 사용자 수동 override → domain_hints 가중치 +0.1 학습 | ✅ §6 |
| 8 | MP-08 | Dream Mode role_prompt 최적화 → L2 shadow 승격 | ✅ §6 + dream_mode.md §6 |
| 9 | MP-09 | 페르소나 전환 이벤트 PersonaSwitchEvent emit (VamosMessage) | ✅ LOCK-AP-01 |
| 10 | MP-10 | multi_user tenant 격리 × 페르소나 세트 교차 | ✅ multi_user.md §3 |
| 11 | MP-11 | confidence 차이 ≥ 0.15 시에만 재전환 (히스테리시스) | ✅ §5.3 |
| 12 | MP-12 | Langfuse trace `persona.switch.*` span 기록 | ✅ logging_spec.md §5.1 |

---

## §11. 세션 간 인터페이스 Cross-check 표

| 인터페이스 | 대상 파일 | 검증 기준 |
|-----------|----------|----------|
| 페르소나 × 멀티유저 | `multi_user.md §3` | tenant_id × persona_id 교차 격리 |
| Dream Mode 프롬프트 최적화 | `dream_mode.md §6` | role_prompt shadow 승격 계약 |
| confidence HITL 임계 | `06_autonomy-safety/guardrail_rules.md §V2.2` | LOCK-AP-10 < 0.50 read-only |
| 권한 상한 매핑 | `06_autonomy-safety/permission_matrix.md §V2.1` | max_permission_level read-only |
| 사용자 컨텍스트 메모리 | `6-4 Memory-RAG-Storage` | 읽기 전용, LOCK-AP-02 L0 |

---

## §12. 검증 자가 체크리스트 (L3 D1~D8 + E1~E10)

- [x] STEP7-K L1254~L1270 K-065 5대 요건 전수 구현 (정의/자동전환/학습/권한격리/HITL)
- [x] CFL-AP-006 K-065 V 로드맵 정정 후 V3 컨텍스트 자동 선택 알고리즘 (§5)
- [x] LOCK-AP-01/02/10 5필드 분리 인용 (§9)
- [x] LOCK-AP-02 페르소나별 권한 상한 격리 (§4.3) + L3+ 전환 HITL 필수
- [x] LOCK-AP-10 재정의 없음 (§5.2/§7 참조자)
- [x] R-13-6 max_strategy_drift 정합 (§5.3) + R-13-7 외부 에이전트 사용자 승인 정합
- [x] multi_user (K-066) tenant 교차 cross-ref (§11)
- [x] Phase 3 테스트 12건 (≥ 10 요건 충족, §10)
- [x] 에스컬레이션 Pydantic + 5 event_class (§8)
- [x] ML 페르소나 자동 학습 Phase 4+ 이월 명시 (§6)
- [x] Status DRAFT → APPROVED 전환 (Phase 4 production 승급)

---

*정본 소유: #13 Agent-Protocol-Interoperability (자기진화 전략 — 멀티 페르소나)*
*LOCK-AP-10 HITL<50% 는 06_autonomy-safety/guardrail_rules.md (P2-6 정본) 에서 정의, 본 문서는 참조자*
*ML 기반 페르소나 자동 학습은 Phase 4+ 이월*
