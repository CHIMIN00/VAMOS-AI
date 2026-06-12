# PHASE3-DEC-010 (3-7c): 예측 신뢰도 — confidence_score + 임계값 LOCK + 행동 분기 (A25)

> **결정일**: 2026-06-12 (P3-1) · **포맷**: A6 · **우선순위**: Must

## 결정

### Decision 스키마 확장 (A20 절차로 추가)
```python
Decision {
  ...기존 필드...
  confidence_score: float        # 신규, 0.0~1.0
  confidence_level: Literal["HIGH","MEDIUM","LOW","REFUSE"]   # 신규 (임계값 적용 결과)
}
```
- D2.1-D2 DecisionSchema에 confidence 필드 부재 실측(2026-06-12 grep 0) — **신규 추가** 확정, 집행은 V0-STEP-2 Pydantic 정본에서 A20 6 Step(DEC-006)으로.
- 기존 `Decision.optional_signals`의 uncertainty 신호(D2.0-02 §11.1.4)와 역할 구분: optional_signals.uncertainty = 입력 신호(힌트), confidence_score = 산출 판정값. IntentFrame.confidence(<0.5 HITL)는 의도 파싱 신뢰도로 별개.

### 임계값 LOCK (config.v1.toml 신규 3키 — **신규 LOCK 등록**)
```toml
confidence_high_threshold = 0.85     # (LOCK)
confidence_medium_threshold = 0.60   # (LOCK)
confidence_refuse_threshold = 0.30   # (LOCK)
```
- ⚠️ 분모 영향 명기: config LOCK 키 분모는 D13 확정 **20** (현행) — 본 결정으로 V0 구현 시점 **+3 = 23** (D13 재정의 아님 — 신규 키 추가 이벤트로 기록. CLAUDE.md §20 표·검증 스크립트 check_config_lock.py의 분모 갱신은 Phase 4 4-5 집행 항목으로 바인딩).

### 행동 분기
| confidence | level | 행동 |
|------------|-------|------|
| ≥ 0.85 | HIGH | 정상 답변 |
| 0.60 ~ 0.85 | MEDIUM | "⚠ 확신도 보통" 표시 + 답변 제공 |
| 0.30 ~ 0.60 | LOW | "⚠ 불확실한 답변입니다. 직접 확인을 권장합니다" + 답변 제공 |
| < 0.30 | REFUSE | "판단이 어렵습니다. 더 많은 정보가 필요합니다" + **답변 거부** |

- 연계 규칙: **EvidenceGate "insufficient" → confidence 강제 < 0.30 → REFUSE 발동** (STRATEGY_05 §5.3) — "근거 없으면 추측 금지"(BASE-1.3 Non-goal) 실현
- 값 전파: Decision.confidence_score → ResponseEnvelope.metadata.confidence_score(DEC-009) → UI 0-100% 표시(S7B-019, D2.0-02 L1874)

## 근거 (정본 라인)
STRATEGY_05 §5.2 L215-233(스키마+임계값+분기 원형)·§5.3 L239-245(SOT 철학 정합: BASE-1.3 6대 철학 #2·Non-goal) · 로드맵 3-7c 행(0.85/0.60/0.30 LOCK)·L400(V0-STEP-2 confidence_score)·4-5 행(임계값 3개) · D2.1-D2 실측(부재→신규) — 기존 LOCK 재정의 0 + 신규 LOCK 1건(임계값 3종) 등록.

## 이유·대안
임계값 3개를 config LOCK으로 두는 것은 Defense Layer 1(DEC-008) 편입 효과 — 코드 버그로 REFUSE가 무력화되는 것을 정적 계층이 차단. 대안(임계값 코드 상수화)은 운영 조정 경로(Approval Gate 승인) 차단으로 기각, (임계값 별도 발명)은 정본 0.85/0.60/0.30 기확정으로 기각.

## 구현 바인딩
Phase 4: 4-1(스키마)·4-2(분기 로직)·4-5(config 3키) — V0 GO/NO-GO 전 confidence 임계값 config 검증 포함(로드맵 4-V·A25).
