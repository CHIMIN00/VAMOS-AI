# STRATEGY 03: 세션 관리 및 지식 보존

> **상위 전략**: 독립 (실용적 필요에서 도출) + Twitter/X 실패 사례 교훈
> **포함 관점**: A5(작업 중단/재개) + A6(의사결정 기록) + A13(AI 상태 인식)
> **적용 Phase**: 전 Phase 공통
> **관련 문서**: 로드맵 전 Phase 인수인계, 자산 인벤토리

---

## 1. 전략 개요

```
핵심 원칙:
  "대화가 끊겨도, 시간이 지나도, 작업을 이어갈 수 있어야 한다"

3가지 기법:
  Checkpoint: 진행 상태를 파일로 저장 (A5)
  Decision Log: 왜 그렇게 했는지 기록 (A6)
  Context Protocol: AI에게 현재 상태를 알려주는 규약 (A13)
```

---

## 2. A5: 작업 중단/재개 프로토콜

### 2.1 문제 정의

```
현재: 대화 끊기면 → AI가 "지금 어디까지 했지?" 모름
      매번 처음부터 설명 → 시간 낭비 + 중복 작업 위험
```

### 2.2 전략: Progress Checkpoint 파일

**파일 위치**: `D:\VAMOS\VAMOS Engineering\PROGRESS.md`

**파일 포맷:**
```markdown
# VAMOS 진행 상태

> 최종 갱신: 2026-04-XX HH:MM

## 현재 Phase
Phase 2-3 (Obsidian 노트 생성)

## 완료 항목
- Phase 0: 전체 완료 (2026-04-XX)
- Phase 1: D1 PASS (2026-04-XX)
- Phase 2-1: CLAUDE.md 보강 완료
- Phase 2-2: CLAUDE.md SILVER 판정
- Phase 2-3: T0~T2 도메인 12/36 노트 완료

## 미완료 항목
- Phase 2-3: T3~T6 도메인 24개 노트 미생성
- Phase 2-4: 린터/CI 미착수

## 다음 작업
T3-2 Multimodal 도메인 노트 생성

## 참조 파일
- 자산 인벤토리 §3.3 "Obsidian 만들 때"
- Obsidian Strategy v3.0 §5 도메인 노트 Template
```

### 2.3 운영 규칙

```
작업 중단 전: PROGRESS.md 갱신 (2분)
작업 재개 시: PROGRESS.md 읽기 → 즉시 이어서 작업
Phase 완료 시: 해당 Phase를 "완료 항목"으로 이동 + 날짜 기록
```

---

## 3. A6: 의사결정 기록 (Decision Log)

### 3.1 문제 정의

```
현재: "왜 이렇게 결정했지?" → 머릿속에만 있음
      나중에 근거를 모르면 → 잘못된 이유로 변경할 위험
```

### 3.2 전략: ADR (Architecture Decision Record) 패턴

**저장 위치**: `D:\VAMOS\VAMOS Engineering\decisions\`

**파일명 규칙**: `PHASE{N}-DEC-{순번}_{제목}.md`

**파일 포맷:**
```markdown
# PHASE3-DEC-001: 5-Gate 실행 순서 확정

> 날짜: 2026-04-XX
> 상태: CONFIRMED
> Phase: 3 (R1)

## 결정
5-Gate 순서를 PolicyGate → CostGate → ApprovalGate → EvidenceGate → SelfCheckGate로 확정

## 이유
1. 정책 위반 요청은 가장 먼저 차단해야 비용 낭비 방지
2. 비용 초과 요청은 복잡한 검증 전에 차단
3. D2.0-07 정본 순서와 일치

## 검토한 대안
A. CostGate 먼저 → 비용 초과 빠른 차단 가능하나 정책 위반 놓칠 위험
B. SelfCheckGate 먼저 → 자가 검증 선행, 하지만 비용 낭비 후 거부 가능

## 근거 SOT
D2.0-07 §4.1 Gate 실행 순서 (LOCK)
```

### 3.3 운영 규칙

```
기록 대상:
  - 아키텍처 결정 (R1 7개 LOCK)
  - 전략 결정 (X1 4개 전략)
  - 스코프 축소 결정 (A9 적용 시)
  - 예외 허용 결정 (Must 미통과인데 진행하는 경우)

기록 안 해도 되는 것:
  - 단순 작업 수행 (코드 작성, 파일 생성)
  - SOT에 이미 LOCK으로 확정된 것 (근거가 SOT 자체)
```

---

## 4. A13: AI 컨텍스트 프로토콜

### 4.1 문제 정의

```
현재: 새 대화 시작 → AI는 CLAUDE.md 697줄만 봄
      현재 Phase, 사용할 파일, 이전 작업 결과를 모름
```

### 4.2 전략: Phase별 컨텍스트 세트 정의

**Phase별 AI에게 줄 정보:**

| Phase | 첫 메시지에 참조 지시할 파일 |
|-------|--------------------------|
| Phase 0 | PROGRESS.md + 자산 인벤토리 + 매트릭스 |
| Phase 1 | PROGRESS.md + 자산 인벤토리 §3.1 + D1 스킬 목록 + SOT 2 해당 도메인 |
| Phase 2 (CLAUDE) | PROGRESS.md + 보강전략 V1.0 + D1 gap report |
| Phase 2 (Obsidian) | PROGRESS.md + Obsidian Strategy v3.0 + SOT 2 해당 도메인 |
| Phase 2 (린터) | PROGRESS.md + 하네스 계획서 §7~8 + PART2 line 1410~1536 |
| Phase 3 (R1) | PROGRESS.md + D2.0-01~08 + LOCK Registry + 자산 인벤토리 §3.4 |
| Phase 3 (X1) | PROGRESS.md + BASE-1.3 + PART2 §3.5 + PLAN-3.0 §2 |
| Phase 4 | PROGRESS.md + 자산 인벤토리 §3.4 + R1 결정 문서 + PART2 |
| Phase 5 | PROGRESS.md + 자산 인벤토리 §3.5 + 벤치마크 설정 |
| Phase 6 | PROGRESS.md + V0 완료 결과 + PART1 Section B.2 |

### 4.3 첫 메시지 템플릿

```
새 대화 시작 시 복사/붙여넣기:

"현재 Phase [N]-[작업번호] 진행 중.
 PROGRESS.md 확인 후, [해당 Phase 참조 파일] 읽어주세요.
 이전 완료: [마지막 완료 항목].
 이번 작업: [현재 작업 상세]."

예시:
"현재 Phase 2-3 진행 중.
 PROGRESS.md 확인 후, Obsidian Strategy v3.0 + SOT 2/3-2_Multimodal 읽어주세요.
 이전 완료: T0~T2 도메인 12개 노트.
 이번 작업: T3-2 Multimodal 도메인 노트 생성."
```

### 4.4 CLAUDE.md 보강 시 §28에 포함할 내용

```
Phase 2에서 CLAUDE.md를 보강할 때 §28에 다음을 포함:

§28 엔지니어링 프레임워크
  - 매트릭스 위치: VAMOS Engineering/STRATEGY_08_*
  - 현재 Phase: PROGRESS.md 참조
  - Phase별 참조 파일: (위 테이블)
  - 진행 상태 기록: PROGRESS.md
  - 의사결정 기록: decisions/ 폴더

→ AI가 §28을 읽으면 "PROGRESS.md를 먼저 확인해야겠다" 판단 가능
```

---

## 5. 관점 간 연결

```
A5(중단/재개) → PROGRESS.md가 있어야 → A13(AI 상태 인식) 작동
A6(결정 기록) → decisions/ 폴더가 있어야 → A11(회고) 시 참조 가능
A13(AI 컨텍스트) → CLAUDE.md §28이 있어야 → AI가 자동으로 PROGRESS.md 참조
```

---

> **참조**: STRATEGY_07 (회고 시 결정 기록 활용), STRATEGY_10 (검증 체계 인수인계)
