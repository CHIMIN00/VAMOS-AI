# PHASE4-DEC-007 (P4-0 ⑬): Eval 스택(ragas·deepeval·minicheck) — Phase 5 착수 시 poetry `eval` 그룹(optional) 등재

> **결정일**: 2026-06-12 (P4-0) · **포맷**: A6 · **우선순위**: Should(비차단) · **출처**: P4-PRE B-03a

## 결정

**등재 시점 = Phase 5 착수 세션(5-1 벤치마크 실행 직전). 형식 = `[tool.poetry.group.eval]` optional 그룹** (dev 그룹 아님):

```toml
[tool.poetry.group.eval]
optional = true

[tool.poetry.group.eval.dependencies]
ragas = "..."        # 버전은 등재 시점 실측 고정 (A4 LOCK 버전 원칙)
deepeval = "..."
# minicheck: pip 패키지 가용성 등재 시점 확인 — 불가 시 .claude/hooks/minicheck_verifier.py(기존 스킬 자산) 경로로 대체 명기
```

- Phase 4(V0 코드 생산) 동안 미설치 — V0 하네스(ruff·vamos_lint·pytest)와 무관하며 의존성 트리 오염(ragas의 대형 전이 의존) 방지.
- 5-1 세션 PASS 조건에 "eval 그룹 설치 + import 검증" 1항 포함을 지시(로드맵 5-1 행은 무수정 — 본 ADR이 P5-0/5-1 입력으로 인계).

## 근거
P4-PRE B-03a(정의처 0 — PHASE_B3·PART1 B·PART2 grep 0) · 소비처는 Phase 5 V0 검증(5-1 eval_results.json)과 V1→V2 TC(rag_benchmark.py + RAGAS)가 최초 — Phase 4 내 소비 0. promptfoo는 Phase 2 스킬 자산으로 기존재(중복 등재 불요).

## 기각 대안
- 본 세션(P4-0) dev 그룹 등재 — V0 CI가 매 커밋 불필요 대형 의존 설치, 비용·시간 낭비. 기각.
- 영구 미등재(스킬 hooks 자산으로 갈음) — 5-1의 RAGAS faithfulness 측정(§7.2 TC 표 정본)은 패키지 직접 호출 전제. 기각.
