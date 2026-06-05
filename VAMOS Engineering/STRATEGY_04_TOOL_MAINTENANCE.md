# STRATEGY 04: 도구 유지보수 및 로드맵 관리

> **상위 전략**: 독립 (실용) + SAFe (Inspect & Adapt)
> **포함 관점**: A7(스킬/Hook 유지보수) + A8(스킬 간 의존관계) + A12(로드맵 갱신 주기)
> **적용 Phase**: Phase 경계마다
> **관련 문서**: 자산 인벤토리 §2.8, 로드맵

---

## 1. 전략 개요

```
핵심 원칙:
  "도구와 계획은 시간이 지나면 낡는다 — 정기적으로 점검해야 한다"

3가지 기법:
  Health Check: Phase 착수 전 도구 동작 확인 (A7)
  Dependency Map: 스킬 간 의존 관계 시각화 (A8)
  Living Document: 로드맵을 현실과 주기적 대조 (A12)
```

---

## 2. A7: 스킬/Hook 유지보수

### 2.1 문제 정의

```
현재: 스킬 56개 + Hook 37개가 있는데
      코드 구조 변경 시 깨질 수 있음 → 점검 계획 없음
```

### 2.2 전략: Phase 경계 건강 검진

**점검 시점:**
```
Phase 4 착수 전: V0 코드 생산 시작이므로 모든 도구 정상 확인
Phase 6 착수 전: V1 확장이므로 도구 호환성 재확인
스킬 관련 파일 수정 후: 해당 스킬 동작 확인
```

**점검 방법:**
```
핵심 검증 스킬 11개 점검:
  /sot-conflict scan → 실행 가능? 알려진 결과와 일치?
  /sot-check all → 실행 가능?
  /sot2-cross-ref all → 실행 가능?
  /validate → DV-1~9 실행 가능?
  /integrity → 스냅샷 생성 가능?
  나머지 6개: 실행 가능 여부만 확인

Hook 6개 점검:
  settings.json의 matcher 경로가 실제 파일과 일치?
  block_invalid_ea.sh 실행 가능?
  deterministic_validator.py 실행 가능?
```

**점검 결과 기록:**
```
위치: PROGRESS.md의 "도구 점검" 섹션
포맷:
  2026-04-XX Phase 4 착수 전 점검:
    스킬 11개: 11/11 PASS
    Hook 6개: 6/6 PASS
    → 도구 정상, Phase 4 착수 가능
```

---

## 3. A8: 스킬 간 의존관계

### 3.1 의존관계 맵

```
[독립 실행 가능 — 외부 의존 없음]
  /sot2-cross-ref
  /sot2-plan-gen
  /sot2-method-c
  /cross-examine
  /fact-audit
  /hallucination-check
  /completeness-map
  /report
  /phase-run

[Hook 스크립트에 의존]
  /validate → deterministic_validator.py (DV-1~9 엔진)
             → cm_validator.py (CM-DV1~6, CM 전용)
  /audit → deterministic_validator.py (AD-2 수치 검증)
  /sot-conflict → sot_indexer.py (SOT 파일 인덱싱)
                 → sot_search.py (SOT 검색)
  /integrity → sot_indexer.py (해시 비교)
  /sot-check → sot_search.py (라인 매칭)

[외부 도구에 의존 — Phase 4+ 이후]
  /ragas-eval → ragas_evaluator.py → ragas 패키지 (pip)
  /giskard-scan → giskard_scanner.py → giskard 패키지
  /minicheck → minicheck_verifier.py → minicheck 패키지
  /symbolic-verify → symbolic_verifier.py → z3-solver 패키지

[스킬 간 의존]
  /cross-match → /validate의 DV 결과를 입력으로 사용 가능
  /audit → /hallucination-check 결과를 AD-1에서 참조 가능
  /final-review → /validate + /audit + /cross-match 결과 통합
```

### 3.2 영향 분석

```
deterministic_validator.py가 깨지면:
  → /validate FAIL
  → /audit AD-2 FAIL
  → /final-review 부분 FAIL
  영향 범위: 3개 스킬

sot_indexer.py가 깨지면:
  → /sot-conflict FAIL
  → /integrity FAIL
  영향 범위: 2개 스킬

sot_search.py가 깨지면:
  → /sot-conflict FAIL
  → /sot-check FAIL
  영향 범위: 2개 스킬
```

---

## 4. A12: 로드맵 갱신 주기

### 4.1 전략: Phase 경계 검토

```
규칙:
  Phase N 완료 시 → 로드맵의 Phase N+1 내용을 현실과 대조
  
판단 기준:
  불일치 0~2건: 메모만 남기고 계속 진행
  불일치 3건 이상: 로드맵 갱신 (해당 Phase 이후만)
  구조적 변경 필요: Phase 0 매트릭스부터 재검토

검토 항목:
  ① Phase N+1 작업 목록이 현실과 맞는가?
  ② 병렬/순차 관계가 여전히 유효한가?
  ③ 완료 조건이 현실적인가?
  ④ 새로 발견된 작업이 있는가?
  ⑤ 제거해야 할 작업이 있는가?
```

### 4.2 갱신 시 규칙

```
원칙: 이전 Phase는 수정하지 않음 (이미 완료된 것)
      현재 Phase 이후만 수정
      수정 시 PROGRESS.md에 "로드맵 갱신" 기록
      수정 이유를 decisions/ 폴더에 기록 (A6)
```

---

## 5. 관점 간 연결

```
A7(스킬 유지) → 깨진 스킬 발견 시 → A8(의존맵)에서 영향 범위 파악
A12(로드맵 갱신) → 갱신 사유 → A6(결정 기록)에 기록
A7(점검 결과) → PROGRESS.md에 기록 → A5(중단/재개)에서 참조
```

---

> **참조**: STRATEGY_03 (PROGRESS.md 관리), STRATEGY_11 (자산 인벤토리 §2.8)
