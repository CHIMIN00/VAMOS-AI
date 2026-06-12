# PHASE4-DEC-004 (P4-0 ⑩): V0 GO #15 "Guardrails L1+L2 설정" — 코드 수준 입력/출력 검증으로 갈음

> **결정일**: 2026-06-12 (P4-0) · **포맷**: A6 · **우선순위**: Must(게이트 판정 기준) · **출처**: P4-PRE A-07

## 결정

**V0 GO/NO-GO #15의 충족 수단 = 코드 수준 L1/L2 등가 구현. `[guardrails]` config 섹션 도입은 V1 유지(XREF-V0-18).**

| Layer | 정본 역할 (D2.1-D7 §4.5: L1=입력/L2=출력) | V0 등가 구현 (판정 기준) |
|-------|------------------------------------------|--------------------------|
| L1 입력 | NeMo Guardrails (V1+) | Pydantic `extra="forbid"` 전 모델 + 단계 경계 `.model_validate()` 의무(DEC-004 전이 규칙 3) + I-8 Policy stub non-goal deny + IntentFrame 검증 |
| L2 출력 | Guardrails AI (V1+) | ResponseEnvelope 5필드 LOCK 스키마 검증 + verify 노드(SelfCheckGate stub) 출력 경로 강제 + StructuredOutput.validated |

- V0 GO #15 판정 시 위 항목의 동작 확인으로 PASS 처리한다(프레임워크 도입 아님). V1에서 [guardrails] 섹션 + NeMo/Guardrails AI 본격 도입 시 본 등가 구현은 하위 계층으로 흡수.

## 근거
PART2 L1333/L1339([guardrails]=V1+, B4 §3.16 V1=2-Layer) ↔ §7.1 #15(L6176) 간 공백을 충족 수단 정의로 해소. D2.1-D7 §4.5가 L1=입력/L2=출력 역할을 명문화 — 등가 구현의 매핑 기준. DEC-008 Defense Layer 3계층(A21)은 별개 체계(V0부터 완전체)로 V0 안전망 중복 확보.

## 기각 대안
- V0에서 [guardrails] 섹션+NeMo 조기 도입 — XREF-V0-18(V0 13섹션) 위반 + V0 "실행 가능한 뼈대" 목적 초과. 기각.
- #15를 V1 이연 — V0 GO 16항 분모 변경(GATE-03 연동 훼손). 기각.

## 집행
PART2 §7.1 #15 행에 V0 충족 수단 주석 1줄 부기(본 세션, CRLF 보존). 구현 자체는 4-2(ORANGE CORE) 산출물에 포함.
