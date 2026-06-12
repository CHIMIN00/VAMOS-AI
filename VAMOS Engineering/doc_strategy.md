# VAMOS 문서화 전략 — doc_strategy.md (3-11, X1)

> **확정일**: 2026-06-12 (P3-2) · **우선순위**: Could · **매트릭스 셀**: X1 (문서화 전략 ⑩⑪)
> **위상 (로드맵 L293)**: 기존 정본(OBSIDIAN-STRATEGY-v3·STRATEGY_04·STRATEGY_11 자산 인벤토리)의 **결정 요약 + 로드맵 바인딩**. 정본 무대체.

## 1. 코드 문서 vs 설계 문서 주체 (⑩)

| 구분 | 주체 | 위치 | 갱신 시점 |
|------|------|------|----------|
| **설계 문서 (정본)** | 사람 판단 (LOCK 절차) | `docs/sot`(D2.0·PHASE_B·PLAN/RULE)·`docs/sot 2`(30 도메인) | 설계 변경 시 — RULE 1.3 > PLAN 3.0 > DESIGN LOCK 위계, 변경은 LOCK 절차 |
| **코드 문서 (파생)** | 코드와 동기 (자동 우선) | docstring·README·타입 정의 | 코드 변경 시 — Pydantic 정본에서 자동 생성(A20), 수동 편집 금지 대상(serde/TS) |
| **결정 문서 (ADR)** | AI+사람 (A6) | `VAMOS Engineering/decisions` | 결정 시 — PHASE{N}-DEC/GATE 네임스페이스 |
| **로드맵 바인딩** | 본 X1/R1 전략 문서 | `VAMOS Engineering/*.md` | Phase 진행 시 — 정본 요약, 충돌 시 정본 우선 |

- **원칙**: 설계 문서가 정본, 코드 문서는 코드를 따른다(드리프트 시 코드 문서를 코드에 맞춤, 설계 문서 불일치는 D3 정합 검증으로 해소). 정본 우선순위 = DEC-001 위계.
- **A20 연계**: 타입/스키마 문서는 Pydantic 단일 정본에서 파생(PHASE3-DEC-006) — 수동 작성 금지.

## 2. VAMOS HOME 지식 그래프 갱신 규칙 (⑪)

- **Obsidian Vault 정본**: `VAMOS HOME` — Phase 2-3에서 **124노트** 구축(17폴더, 깨진 [[wikilink]] 0/1,289, A16 responsible-ai 태그 9노트)
- **갱신 트리거 (X2 ⑨ "코드 변경에 따른 VAMOS HOME 갱신")**:
  - 코드/도메인 변경 → 해당 도메인 노트 + 00_HUB 인덱스 갱신
  - LOCK 추가/변경 → `00_HUB/LOCK-DECISION-REGISTRY.md` 갱신 (P3-1에서 §8 신규 3건 등재 선례)
  - 결정 → ADR 생성 + 관련 노트 [[링크]] 연결
- **무결성 규칙**: 깨진 wikilink 0 유지 · 수치/LOCK은 SOT2 대조 일치(창작 0) · 형식 태그 일관(STRATEGY_11 §2.13 자산 등재)
- **갱신 주체**: D2 상시 감시(Hook → "/sot-conflict scan 권장") + 자산 인벤토리 갱신(2-8 패턴)

## 3. 문서화 도구·자동화 (STRATEGY_04 바인딩)
- 검증 스킬: /sot-check·/sot-conflict·claude-md-* 8종 (Phase 2 기구축)
- Hook 18(Phase 2): SOT 수정 시 정합 검사 트리거 — 문서 드리프트 조기 탐지
- CONTEXT_LOADING_MAP.md(Phase 2-7): Phase별 컨텍스트 로딩 골격 — 세션 문서화 골격

## 4. 회귀 정합
- Phase 2 Obsidian 124노트·CPS_TEMPLATE·CONTEXT_LOADING_MAP과 모순 0 — 본 전략은 그 위 갱신 규칙 바인딩
- 본 P3-2 산출물(6 전략/계획서)도 본 규칙 적용 대상 — Phase 3 완료 후 VAMOS HOME 반영(X3 문서 운영)

## 정본 인용
STRATEGY_08 X1 셀 ⑩⑪ · STRATEGY_04(도구 유지)·STRATEGY_11 §2.13 · OBSIDIAN-STRATEGY-v3 · LOCK Registry §8(P3-1) · DEC-001 위계 · PHASE3-DEC-006(A20)
