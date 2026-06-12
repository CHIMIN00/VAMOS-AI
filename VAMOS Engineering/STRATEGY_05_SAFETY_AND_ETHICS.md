# STRATEGY 05: 제품 안전 및 책임 AI

> **상위 전략**: Microsoft Responsible AI 6원칙 + SRE Defense in Depth
> **포함 관점**: A16(책임 AI) + A21(다층 방어) + A22(사용자 투명성) + A25(예측 신뢰도)
> **적용 Phase**: Phase 3 (R1, X1), Phase 4 (R2a, R2c), Phase 6 (R3)
> **관련 문서**: SOT BASE-1.3 (7개 불변), D2.0-07 (보안/비용/승인), 매트릭스 R행+X행

---

## 1. 전략 개요

```
핵심 원칙:
  "VAMOS는 투자/건강/교육을 다루는 AI — 잘못된 답변은 실제 피해를 준다"

4가지 방어선:
  책임 AI (A16): 편향/안전/윤리 검증 체계
  다층 방어 (A21): Gate 1개 실패해도 안전 보장
  투명성 (A22): 사용자가 "왜 이 답변인지" 확인 가능
  신뢰도 (A25): AI가 "모르면 모른다"고 말할 수 있게
```

---

## 2. A16: 책임 AI / 윤리

### 2.1 VAMOS가 다루는 민감 영역

```
투자/금융 (Quant, Trading, AI-Investing):
  → 편향된 조언 시 금전적 손해
  → 과거 데이터 기반 예측이 미래를 보장하지 않음

건강/웰니스 (Health, EmotionAI):
  → 잘못된 건강 조언 시 신체적 위험
  → 의료 행위 대체 금지 (SOT Non-goal)

교육 (Education):
  → 잘못된 정보 전달 시 학습 피해
  → 저작권 있는 콘텐츠 무단 사용 위험
```

### 2.2 기존 방어 수단 (이미 SOT에 존재)

```
7개 불변 구역 (BASE-1.3):
  safety, cost_ceiling, approval_flow, non_goals,
  audit_log, data_retention, consent

NEVER_AUTO 10항목 (SDAR §5.1):
  RA_NEVER_01~10 — 자동 실행 절대 금지 목록

SelfCheckGate (D2.0-07):
  최종 자가 검증 — PASS/WARN/FAIL

EvidenceGate (D2.0-07):
  근거 충분성 확인 — sufficient/insufficient
```

### 2.3 추가 필요 — 책임 AI 통합 체크리스트

```
Phase 3 X1 보안 전략에 포함:

  □ 투자 조언 시: "과거 성과가 미래를 보장하지 않습니다" 면책 조항 포함
  □ 건강 조언 시: "의료 전문가 상담을 권장합니다" 면책 조항 포함
  □ EvidenceGate: 근거 2건 미만 → 답변 거부 (추측 금지)
  □ NEVER_AUTO: 금전 거래, 개인정보 전송, 외부 API 쓰기 → 항상 사용자 승인
  □ 편향 탐지: 특정 종목/브랜드 반복 추천 시 경고 (V2+)

기존 스킬 활용:
  /guardrails-validate → 가드레일 규칙 검증
  /input-guard → 위험 입력 필터링
  /llama-firewall → 안전 콘텐츠 필터
```

---

## 3. A21: 다층 방어 (Defense in Depth)

### 3.1 문제: 단일 장애점

```
현재 5-Gate 구조:
  PolicyGate → ApprovalGate → CostGate → EvidenceGate → SelfCheckGate
  (2026-06-12 교정: 구 표기 "Cost→Approval" 순서 오기 — 정본 D2.0-07 L969, PHASE3-DEC-001)
  → 소프트웨어 체인으로만 구성
  → PolicyGate 코드에 버그 → 위험한 요청 통과 가능
```

### 3.2 전략: 3개 독립 계층

```
Phase 3 X1 보안 전략에서 확정:

Defense Layer 1: config LOCK (정적 방어)
  → config.v1.toml에 LOCK 값으로 상한선 하드코딩
  → 코드와 별도 파일 — 코드 버그와 무관하게 작동
  → 예: cost_monthly_limit = 40000 (LOCK)
  → 코드가 100,000원 요청해도 config에서 차단
  ※ PART2의 "Security Layer"(보안 성숙도 계층)와 다른 개념
     여기서 "Defense Layer"는 VAMOS 내부 아키텍처 방어 계층

Defense Layer 2: 5-Gate 소프트웨어 체인 (동적 방어)
  → 기존 Gate 체인
  → 각 Gate가 독립적으로 판단 (하나 실패해도 다른 Gate는 동작)
  → Gate 간 의존성 0 — A→B가 아니라 A,B,C,D,E 각각 독립 검증

Defense Layer 3: NEVER_AUTO 하드코딩 (최후 방어)
  → 10개 항목은 코드 내 frozenset으로 하드코딩
  → config 수정으로도 우회 불가
  → 런타임 변경 불가 — 소스 코드 수정 + 재배포만 가능

방어 시나리오:
  Defense Layer 2 PolicyGate 버그 → Defense Layer 1 config LOCK이 비용 초과 차단
  Defense Layer 1 config 파일 손상 → Defense Layer 3 NEVER_AUTO가 위험 행동 차단
  Defense Layer 3 코드 수정 시도 → Git 리뷰 + commitlint 필수 (X2)
```

### 3.3 검증 방법

```
Phase 4 R2a 구현 시:
  ① config LOCK 값 로드 → 런타임 상한선 적용 테스트
  ② 5-Gate 각각 독립 실행 테스트 (Gate A 비활성 → 나머지 4개 동작 확인)
  ③ NEVER_AUTO 항목 우회 시도 → 차단 확인

Phase 5 검증 시:
  ④ config LOCK vs SOT LOCK 대조 (D3)
  ⑤ NEVER_AUTO frozenset vs SOT SDAR §5.1 대조
```

---

## 4. A22: 사용자 투명성 (Explainable AI)

### 4.1 문제: 블랙박스 답변

```
현재: VAMOS가 "A 주식 매수 추천" → 사용자는 "왜?" 모름
      Boeing 737 MAX 교훈: 사용자가 자동화를 이해 못하면 재앙
```

### 4.2 전략: ResponseEnvelope에 판단 근거 포함

```
Phase 3 R1에서 스키마 확정:

※ SOT 정본(D2.1-D2)에서 ResponseEnvelope는 5필드 LOCK:
  request_id, status, data, error, metadata
  아래 신규 필드는 metadata dict 내부에 포함하거나,
  LOCK 해제(Approval Gate 필수) 후 추가하는 2가지 선택지 중
  Phase 3 R1에서 최종 결정. 현 시점에서는 "설계 의도"만 기록.
  ⟦확정⟧ D6 (2026-06-11): 선택지 A 채택 — 선택지 B 기각.
  스키마 상세는 PHASE3-DEC-009 (2026-06-12) 확정.

선택지 A (LOCK 유지 — 권장):
  metadata dict 안에 포함:
  ResponseEnvelope.metadata = {
    "reasoning_trace": [           ← 신규
      {"gate": "EvidenceGate", "result": "PASS", "evidence_count": 3},
      {"gate": "SelfCheckGate", "result": "PASS", "confidence": 0.82},
      {"gate": "PolicyGate", "result": "PASS"}
    ],
    "evidence_sources": [          ← 신규
      {"source": "뉴스A", "date": "2026-04-01", "relevance": 0.9},
      {"source": "재무제표", "date": "2026-03-31", "relevance": 0.85}
    ],
    "confidence_score": 0.82,      ← 신규 (A25 연계)
    "disclaimer": "과거 성과가..."  ← 신규 (A16 연계, 민감 영역 시)
  }
  → 5필드 LOCK 위반 없음 — metadata는 dict 타입이므로 내부 자유

선택지 B (LOCK 해제):
  ResponseEnvelope에 reasoning_trace, evidence_sources,
  confidence_score, disclaimer를 top-level 필드로 추가
  → Approval Gate 승인 필수 (D2.0-07 §4.3)
  → 5필드 → 9필드로 LOCK 재확정
```

### 4.3 UI 표현

```
Phase 4 R2c에서 구현:

기본 표시:
  "A 주식 분석 결과 긍정적입니다. [왜?]"

[왜?] 클릭 시 펼침:
  📊 근거 3건:
    - 뉴스A (2026-04-01) — 관련도 90%
    - 재무제표 (2026-03-31) — 관련도 85%
    - 산업 보고서 (2026-03-28) — 관련도 72%
  
  🔒 검증:
    - EvidenceGate: 근거 충분 (3건 ≥ 2건 기준)
    - SelfCheck: 자가 검증 통과
    - 신뢰도: 82% (보통~높음)
  
  ⚠️ 면책: 과거 성과가 미래를 보장하지 않습니다.
```

---

## 5. A25: 예측 신뢰도 / 불확실성 표현

### 5.1 문제: 모든 답변이 "확정적"

```
현재: Decision 스키마에 confidence 없음
      AI가 50% 확신이든 99% 확신이든 같은 톤으로 답변
      Zillow 교훈: 확신 없는 예측에 $500M → 파산
```

### 5.2 전략: confidence_score + 임계값 기반 행동 분기

```
Phase 3 R1에서 Decision 스키마 확정:

Decision {
  conclusion: str                 ← 기존
  confidence_score: float         ← 신규 (0.0~1.0)
  confidence_level: str           ← 신규 (HIGH/MEDIUM/LOW/REFUSE)
  ...
}

임계값 (config.v1.toml LOCK):
  confidence_high_threshold = 0.85     (LOCK)
  confidence_medium_threshold = 0.60   (LOCK)
  confidence_refuse_threshold = 0.30   (LOCK)

행동 분기:
  0.85+ → HIGH: 정상 답변
  0.60~0.85 → MEDIUM: "⚠ 확신도 보통" 표시 + 답변 제공
  0.30~0.60 → LOW: "⚠ 불확실한 답변입니다. 직접 확인을 권장합니다" + 답변 제공
  0.30 미만 → REFUSE: "판단이 어렵습니다. 더 많은 정보가 필요합니다" + 답변 거부
```

### 5.3 SOT 정합성

```
이 전략은 SOT BASE-1.3의 핵심 철학과 일치:
  "정확성/근거 기반 (환각 최소화)" — 6대 철학 #2
  "모르면 모른다고 답하라" — Non-goal에 "근거 없는 추측" 포함

EvidenceGate와 연계:
  EvidenceGate "insufficient" → confidence 자동 하향 (0.30 미만)
  → REFUSE 발동 → "판단 불가" 응답
```

---

## 6. 관점 간 연결

```
A16(책임AI) → 민감 영역 식별 → A22(투명성)에서 면책 조항 표시
A21(다층방어) → 3개 계층 독립 → A25(신뢰도)의 confidence가 낮아도 NEVER_AUTO가 보호
A22(투명성) → reasoning_trace에 → A25(confidence_score) 포함
A25(신뢰도) → REFUSE 발동 시 → A16(책임AI)의 "근거 없으면 답변 거부" 원칙 실현

전체 흐름:
  사용자 질문 → PolicyGate(A21 Layer2) → EvidenceGate → confidence 계산(A25)
  → 0.30 미만이면 REFUSE(A25) + "판단 불가" 표시(A22)
  → 0.60 이상이면 답변 + reasoning_trace(A22) + 면책 조항(A16)
  → 전 과정에서 config LOCK(A21 Layer1) + NEVER_AUTO(A21 Layer3) 보호
```

---

> **참조**: STRATEGY_08 (매트릭스 R행, X행), STRATEGY_06 (인터페이스에 스키마 반영)
