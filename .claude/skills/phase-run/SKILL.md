---
name: phase-run
description: v13 Phase 1~7 재실행 오케스트레이터. v6~v12 파이프라인을 Phase 0 delta 반영 후 순차 재실행. 선행 Phase PASS 확인, 완료 조건 자동 체크.
---

# VAMOS Phase 재실행 오케스트레이터

> `/phase-run [phase번호|status|next]` — Phase 1~7 파이프라인 재실행

## 목적

v13_plan.md에 따라 Phase 1~7(v6~v12 재실행)을 관리합니다.
각 Phase의 선행 조건 확인, 실행, 완료 조건 검증을 자동화합니다.

---

## Phase 매핑

| Phase | 재실행 대상 | 원본 계획서 | 원본 결과물 |
|-------|-----------|-----------|-----------|
| 1 | v6 (구조무결성) | — | `v8_results/phase0/` |
| 2 | v7 (SOT교차검증) | — | — |
| 3 | v8 (4차원통합검증) | — | `v8_results/` |
| 4 | v9 (실장준비완전성) | `v9_pipeline_plan.md` | `v9_results/` |
| 5 | v10 (Feature Coverage) | `v10_pipeline_plan.md` | `v10_results/` |
| 6 | v11 (내부자기정합성) | — | `v11_results/` |
| 7 | v12 (최종완전성검증) | `v12_plan.md` | `v12/v12_results/` |

---

## 실행 모드

### `/phase-run status` — 전체 진행 상황

```
1. v13_results/ 디렉토리 스캔
2. 각 Phase의 결과 디렉토리 존재 여부 확인
3. 완료 조건 충족 여부 확인
4. 진행률 테이블 출력:

   Phase 0: PASS (2026-03-18)
   Phase 1: PENDING
   Phase 2: PENDING
   ...
```

### `/phase-run {N}` — 특정 Phase 실행

```
1. 선행 조건 확인:
   - Phase 0 PASS 확인 (v13_phase0_verdict.md)
   - Phase N-1 PASS 확인 (N>1인 경우)
   - delta 적용 상태 확인 (/delta-apply status)
   ↓ 선행 조건 미충족 시 중단 + 안내

2. 원본 계획서 로딩:
   - 해당 버전의 pipeline_plan.md 읽기
   - 검증 관점/에이전트 목록 확인
   ↓

3. SOT 캐시 확인:
   - /sot-cache 최신 여부 → 최신이면 캐시 활용
   ↓

4. 파이프라인 실행:
   - 원본 계획서의 각 단계를 순차 실행
   - Agent tool로 병렬 가능한 에이전트는 병렬 실행
   - 각 단계 결과를 v13_results/phase{N}/ 에 저장
   ↓

5. 완료 조건 검증:
   - v13_plan.md §4의 8개 완료 조건 체크
   - PASS/FAIL 판정
   ↓

6. 결과 저장:
   - v13_results/phase{N}/phase{N}_verdict.md
   - v13_results/phase{N}/phase{N}_status.json
```

### `/phase-run next` — 다음 미완료 Phase 자동 실행

```
1. status 확인 → 첫 번째 PENDING Phase 결정
2. 해당 Phase 실행 (/phase-run {N}과 동일)
```

---

## 완료 조건 (v13_plan.md §4 기준)

모든 Phase에 공통 적용:

1. Layer A 결정론적 검증 PASS
2. Layer B AI 의미적 검증 PASS
3. 적대적 감사 CLEAN 또는 SUSPICIOUS (CONTAMINATED 불가)
4. BLOCKER 잔존 0건
5. delta 반영 완료
6. 이전 버전 대비 악화 항목 0건
7. SOT hash 일치 (추출 시점과 현재)
8. /quality-gate SILVER 이상

## 출력

**결과 디렉토리**: `D:/VAMOS/04. 구현단계/v13_results/phase{N}/`
**상태 파일**: `v13_results/v13_phase_status.json` (전체 Phase 진행률)

## 주의사항

- Phase는 반드시 순차 실행 (1→2→3→...→7)
- 이전 Phase가 FAIL이면 다음 Phase 진행 불가
- 각 Phase 실행 전 `/integrity` 확인 권장
- Phase 실행 중 SOT 파일 수정 금지
