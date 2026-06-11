# promptfoo 완전 통합 — S7G-072

> **Phase**: 1-C (P1-3)
> **항목 ID**: S7G-072
> **우선순위**: HIGH / V1
> **작성일**: 2026-04-12
> **상태**: V1 정의 완료
> **이월 반영**: P1-2 → P1-3 핸드오프 — 13건 E2E 실행(C-3) 배포 환경 필요 → 시뮬레이션 모드 + 실 배포 전환 설계로 반영

---

## 교차 참조 블록

| 정본 문서 | 참조 내용 |
|-----------|----------|
| STEP7-G S7G-072 | promptfoo 통합 — PR마다 자동 실행, 품질 저하 시 머지 차단 |
| STEP7-F S7F-070 | promptfoo 구현 상세 — yaml 구조, assert 유형, providers |
| STEP7-G S7G-073 | 회귀 테스트 — 3% 하락 알림 (LOCK-BE-14) |
| AUTHORITY_CHAIN LOCK-BE-01 | MMLU ≥ 85% |
| AUTHORITY_CHAIN LOCK-BE-02 | HumanEval pass@1 ≥ 85% |
| AUTHORITY_CHAIN LOCK-BE-03 | LogicKor ≥ 8.0/10 |
| AUTHORITY_CHAIN LOCK-BE-06 | Bootstrap 95% CI 필수 |
| AUTHORITY_CHAIN LOCK-BE-08 | seed=42, 재현성 |
| AUTHORITY_CHAIN LOCK-BE-14 | 3%+ 하락 시 자동 알림 |
| AUTHORITY_CHAIN LOCK-BE-15 | CRITICAL 45건 V1 배포 차단 |
| Phase 0 F-05 | promptfoo.yaml — MMLU + HumanEval 2건 기본 설정 |
| Phase 0 F-06 | benchmark-smoke.yml — CI 스모크 |
| Phase 0 F-07 | benchmark_store — diff_runs() 인터페이스 |
| Phase 1-A/1-B 산출물 | 22건 벤치마크 정의서 (01~03 서브폴더) |
| 종합계획서 §10 V-12 | promptfoo eval 실행 성공 검증 |
| 종합계획서 §10 V-13 | 3% 하락 알림 발송 확인 |

---

## 1. 확장 개요

### 1.1 Phase 0 → Phase 1 확장 범위

| 항목 | Phase 0 (F-05) | Phase 1-C (S7G-072) |
|------|---------------|---------------------|
| 벤치마크 수 | 2건 (MMLU, HumanEval) | 13건+ (표준 9 + 도메인 4+) |
| 실행 규모 | 70문항 (MMLU 50 + HumanEval 20) | 1,000+ 문항 (전수) |
| 실행 트리거 | 로컬 + CI 스모크 | PR push + nightly + workflow_call |
| 머지 차단 | 없음 (PR 코멘트 경고만) | 자동 차단 (branch protection) |
| 회귀 감지 | 없음 | 3%+ 하락 → FAIL + 알림 (LOCK-BE-14) |
| LLM-as-Judge | 미포함 | MT-Bench + LogicKor 연동 (S7G-071) |
| 실행 모드 | 시뮬레이션만 | 시뮬레이션 + 실 배포 모드 |

### 1.2 P1-2 이월 반영: 시뮬레이션 vs 실 배포 모드

P1-2에서 "13건 E2E 실행(C-3)은 배포 환경 필요"로 이월됨. 이를 해소하기 위해 2단계 실행 모드 설계:

| 모드 | 대상 환경 | API 호출 | 용도 |
|------|----------|---------|------|
| **시뮬레이션 (sim)** | 로컬/CI | Mock responses | 파이프라인 구조 검증, yaml 문법/assert 검증 |
| **실 배포 (live)** | 스테이징/프로덕션 | 실제 API | 실 성능 측정, 회귀 감지, 릴리스 게이트 |

전환 설계:
```yaml
# promptfoo.yaml 공통 설정
env:
  EVAL_MODE: ${EVAL_MODE:-sim}  # sim | live

providers:
  - id: anthropic:messages:claude-sonnet-4-6
    config:
      temperature: 0          # R-18-1
      apiKey: ${ANTHROPIC_API_KEY}
      # sim 모드: ANTHROPIC_API_KEY 미설정 시 mock provider fallback
```

```python
# scripts/run_promptfoo.py
def get_provider(mode: str):
    """
    시뮬레이션 ↔ 실 배포 전환.
    sim: MockProvider (고정 응답), live: AnthropicProvider (실 API)
    """
    if mode == "sim":
        return MockProvider(seed=42)  # 결정론적 mock
    return AnthropicProvider(api_key=os.environ["ANTHROPIC_API_KEY"])
```

---

## 2. 벤치마크 카탈로그 (10+ 벤치마크)

### 2.1 Phase 1 포함 벤치마크 목록

| # | 벤치마크 | S7G | 카테고리 | assert 유형 | 문항 수 | LOCK |
|---|---------|-----|---------|------------|--------|------|
| 1 | MMLU | S7G-001 | 표준 | equals (exact match) | 14,042 | LOCK-BE-01 (≥ 85%) |
| 2 | HumanEval | S7G-002 | 코딩 | python (pass@1) | 164 | LOCK-BE-02 (≥ 85%) |
| 3 | MT-Bench | S7G-003 | 표준 | llm-rubric (Judge) | 80 | ≥ 8.0/10 |
| 4 | IFEval | S7G-004 | 표준 | contains + regex | 541 | ≥ 80% |
| 5 | KoBEST | S7G-011 | 한국어 | equals | 6,000+ | 평균 ≥ 88 |
| 6 | KLUE | S7G-012 | 한국어 | equals | 5,000+ | 평균 ≥ 85 |
| 7 | LogicKor | S7G-013 | 한국어 | llm-rubric (Judge) | 50 | LOCK-BE-03 (≥ 8.0/10) |
| 8 | CLIcK | S7G-014 | 한국어 | equals | 1,995 | ≥ 65% |
| 9 | MBPP | 상세명세 A-3 | 코딩 | python (pass@1) | 427 | ≥ 75% |
| 10 | RAGAS 4지표 | S7G-035 | RAG | python (custom) | 100+ | LOCK-BE-11 |
| 11 | TruthfulQA | S7G-045 | 안전 | equals + llm-rubric | 817 | ≥ 70% |
| 12 | Prompt Injection | S7G-046 | 안전 | not-contains | 200+ | LOCK-BE-09 (≥ 95%) |
| 13 | VAMOS-Safety | (커스텀) | 안전 | custom | 300 | 100% 차단 |

### 2.2 promptfoo 설정 구조

```yaml
# promptfoo_full.yaml — Phase 1 전수 실행 설정
# S7G-072: 10+ 벤치마크 자동 실행
# LOCK-BE-08: seed=42, temperature=0

description: "VAMOS Benchmark Evaluation — Phase 1 Full (13+ benchmarks)"

providers:
  - id: anthropic:messages:claude-sonnet-4-6
    config:
      temperature: 0          # R-18-1 재현성
      max_tokens: 2048
      # seed는 defaultTest.options에서 설정

defaultTest:
  options:
    seed: 42  # LOCK-BE-08
  metadata:
    sot_ref: "S7G-072, S7F-070"
    lock_refs: "LOCK-BE-01,02,03,06,08,09,11,14"

# --- 표준 벤치마크 ---
prompts:
  - id: mmlu_5shot
    label: "MMLU 5-shot (S7G-001)"
    raw: "file://prompts/mmlu_5shot.txt"
  - id: humaneval_completion
    label: "HumanEval (S7G-002)"
    raw: "file://prompts/humaneval.txt"
  - id: mt_bench_turn
    label: "MT-Bench (S7G-003, LLM-as-Judge)"
    raw: "file://prompts/mt_bench.txt"
  - id: ifeval_instruction
    label: "IFEval (S7G-004)"
    raw: "file://prompts/ifeval.txt"
  # --- 한국어 ---
  - id: kobest_nlu
    label: "KoBEST (S7G-011)"
    raw: "file://prompts/kobest.txt"
  - id: klue_understanding
    label: "KLUE (S7G-012)"
    raw: "file://prompts/klue.txt"
  - id: logickor_reasoning
    label: "LogicKor (S7G-013, LLM-as-Judge)"
    raw: "file://prompts/logickor.txt"
  - id: click_culture
    label: "CLIcK (S7G-014)"
    raw: "file://prompts/click.txt"
  # --- 코딩 ---
  - id: mbpp_completion
    label: "MBPP sanitized (상세명세 A-3)"
    raw: "file://prompts/mbpp.txt"
  # --- RAG/안전 ---
  - id: ragas_qa
    label: "RAGAS 4지표 (S7G-035)"
    raw: "file://prompts/ragas.txt"
  - id: truthfulqa
    label: "TruthfulQA (S7G-045)"
    raw: "file://prompts/truthfulqa.txt"
  - id: prompt_injection
    label: "Prompt Injection (S7G-046)"
    raw: "file://prompts/prompt_injection.txt"
  - id: vamos_safety
    label: "VAMOS-Safety (Custom)"
    raw: "file://prompts/vamos_safety.txt"

tests:
  # 데이터셋은 벤치마크별 JSON 파일 참조
  - file: "tests/mmlu_tests.json"      # 14,042문항 (전수) 또는 골든셋 50 (스모크)
  - file: "tests/humaneval_tests.json"  # 164문항
  - file: "tests/mt_bench_tests.json"   # 80쌍
  - file: "tests/ifeval_tests.json"     # 541문항
  - file: "tests/kobest_tests.json"     # 6,000+
  - file: "tests/klue_tests.json"       # 5,000+
  - file: "tests/logickor_tests.json"   # 50문항
  - file: "tests/click_tests.json"      # 1,995문항
  - file: "tests/mbpp_tests.json"       # 427문항
  - file: "tests/ragas_tests.json"      # 100+
  - file: "tests/truthfulqa_tests.json" # 817문항
  - file: "tests/injection_tests.json"  # 200+
  - file: "tests/safety_tests.json"     # 300문항

outputPath: "benchmark_results/promptfoo_full_latest.json"
```

### 2.3 스모크 vs 전수 설정 분리

| 설정 파일 | 용도 | 데이터 | 소요 시간 |
|----------|------|--------|----------|
| `promptfoo_smoke.yaml` | PR push 스모크 | 골든셋 170문항 (F-04) | ~5분 |
| `promptfoo_full.yaml` | nightly 전수 | 전체 28,000+ 문항 | ~2시간 |

---

## 3. CI/CD 통합

### 3.1 PR 머지 차단 게이트 (Branch Protection)

```yaml
# .github/workflows/benchmark-pr-gate.yml
# S7G-072: PR마다 자동 실행 + 머지 차단
name: Benchmark PR Gate

on:
  pull_request:
    branches: [main, develop]
    paths:
      - 'prompts/**'
      - 'src/core/**'
      - 'promptfoo*.yaml'

concurrency:
  group: benchmark-${{ github.head_ref }}
  cancel-in-progress: true

jobs:
  smoke-test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    env:
      EVAL_MODE: ${{ secrets.ANTHROPIC_API_KEY && 'live' || 'sim' }}
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install promptfoo pydantic numpy

      - name: Run smoke benchmarks
        run: |
          promptfoo eval -c promptfoo_smoke.yaml \
            --output benchmark_results/pr_smoke_latest.json

      - name: Convert to BenchmarkResult (F-02)
        run: |
          python scripts/promptfoo_to_benchmark_result.py \
            --input benchmark_results/pr_smoke_latest.json \
            --output benchmark_results/pr_smoke_results/ \
            --mode ${{ env.EVAL_MODE }}

      - name: Check LOCK thresholds
        id: threshold_check
        run: |
          python scripts/check_thresholds.py \
            --results benchmark_results/pr_smoke_results/ \
            --locks LOCK-BE-01,LOCK-BE-02,LOCK-BE-03,LOCK-BE-09

      - name: Check regression (LOCK-BE-14)
        id: regression_check
        run: |
          python scripts/check_regression.py \
            --current benchmark_results/pr_smoke_results/ \
            --threshold 0.03 \
            --critical-threshold 0.01

      - name: Post PR comment
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const summary = fs.readFileSync('benchmark_results/pr_summary.md', 'utf8');
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: summary
            });

      - name: Gate decision
        if: steps.threshold_check.outcome == 'failure' || steps.regression_check.outcome == 'failure'
        run: |
          echo "::error::Benchmark gate FAILED. See PR comment for details."
          exit 1

  # Branch protection rule: require "smoke-test" to pass before merge
```

### 3.2 Nightly 전수 실행

```yaml
# .github/workflows/benchmark-nightly.yml
# S7G-072: nightly 전수 실행 (WF-9 연동)
name: Benchmark Nightly Full

on:
  schedule:
    - cron: "0 17 * * *"  # 매일 02:00 KST = 17:00 UTC (benchmark_scheduler.md §V3.1 정본 정합)
  workflow_dispatch:
    inputs:
      benchmarks:
        description: "Comma-separated benchmark list (all for full)"
        default: "all"

jobs:
  full-eval:
    runs-on: ubuntu-latest
    timeout-minutes: 180
    env:
      EVAL_MODE: live
    steps:
      - uses: actions/checkout@v4
      - name: Run full benchmarks
        run: promptfoo eval -c promptfoo_full.yaml
      - name: Run LLM-as-Judge
        run: python scripts/run_llm_judge.py --benchmarks mt-bench,logickor
      - name: Store results (F-07)
        run: python scripts/store_results.py --dir benchmark_results/
      - name: Check regression
        run: python scripts/check_regression.py --threshold 0.03 --alert slack
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: nightly-results-${{ github.run_number }}
          path: benchmark_results/
          retention-days: 90
```

### 3.3 Branch Protection 설정

```json
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["smoke-test"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1
  },
  "restrictions": null
}
```

---

## 4. 임계값 자동 판정 알고리즘

```python
def check_thresholds(results: dict, locks: dict) -> dict:
    """
    LOCK 임계값 대비 자동 PASS/FAIL/BORDERLINE 판정.
    시간복잡도: O(n) — n = 벤치마크 수
    LOCK 참조: LOCK-BE-01~03, 06, 09, 11 (개별 임계값)
    """
    verdicts = {}
    for bench_name, result in results.items():
        lock = locks.get(bench_name)
        if not lock:
            verdicts[bench_name] = {"status": "NO_LOCK", "score": result.score}
            continue

        ci = result.confidence_interval  # (lower, upper)
        threshold = lock.threshold

        if ci.lower >= threshold:
            status = "PASS"
        elif ci.upper < threshold:
            status = "FAIL"
        else:
            status = "BORDERLINE"

        verdicts[bench_name] = {
            "status": status,
            "score": result.score,
            "ci": [ci.lower, ci.upper],
            "threshold": threshold,
            "lock_id": lock.id
        }

    # 전체 판정: 1건이라도 FAIL → overall FAIL
    overall = "PASS" if all(v["status"] != "FAIL" for v in verdicts.values()) else "FAIL"
    return {"overall": overall, "benchmarks": verdicts}
```

---

## 5. 로깅 포맷 (R-01-7)

```json
{
  "event": "PROMPTFOO_EVAL_COMPLETE",
  "timestamp": "2026-04-12T03:45:00+00:00",
  "trace_id": "promptfoo-nightly-{run_number}",
  "error": {
    "code": null,
    "message": null,
    "type": null
  },
  "context": {
    "config": "promptfoo_full.yaml",
    "mode": "live",
    "benchmarks_count": 13,
    "total_items": 28500,
    "trigger": "schedule",
    "seed": 42
  },
  "recovery": {
    "attempt": 0,
    "max_retries": 2,
    "strategy": "RESTART_FAILED_BENCHMARKS",
    "fallback": "PARTIAL_RESULT_SAVE"
  },
  "result": {
    "overall_status": "PASS",
    "pass_count": 12,
    "fail_count": 0,
    "borderline_count": 1,
    "duration_seconds": 5400,
    "regression_alerts": 0
  }
}
```

---

## 6. 예외 처리 정책 표

| 예외 상황 | 감지 방법 | 처리 | 에스컬레이션 |
|----------|----------|------|-------------|
| promptfoo eval 실행 실패 | exit code ≠ 0 | 실패 벤치마크만 재실행 (최대 2회) | 3회 실패 시 부분 결과 저장 + 알림 |
| API rate limit | HTTP 429 | exponential backoff (30s, 60s, 120s) | 한도 소진 시 나머지 벤치마크 스킵 + 알림 |
| 시뮬레이션 모드에서 LOCK 판정 불가 | EVAL_MODE=sim | "SIM_MODE" 라벨 + 구조 검증만 | 실 판정은 live 모드 필수 |
| 골든셋 데이터 누락 | FileNotFoundError | 해당 벤치마크 스킵 + 경고 | 데이터셋 복구 후 재실행 |
| CI 타임아웃 (15분 초과) | workflow timeout | 스모크 문항 수 축소 (170 → 100) | 파이프라인 최적화 필요 |
| branch protection 미설정 | 수동 확인 | 설정 가이드 + PR 알림 | Phase 2 필수 설정 |
| BORDERLINE 결과 (CI가 임계값 포함) | check_thresholds | PR에 경고 코멘트 + 수동 머지 허용 | 3회 연속 BORDERLINE 시 리뷰 |

### 6.1 EscalationPayload 구조

```json
{
  "type": "PROMPTFOO_PERSISTENT_FAILURE",
  "domain": "5-1_Benchmark-Evaluation",
  "lock_id": "LOCK-BE-15",
  "failed_benchmarks": ["<benchmark_name>", "..."],
  "fail_count": "<int>",
  "consecutive_failures": "<int>",
  "eval_mode": "sim | live",
  "config_file": "<yaml path>",
  "last_error": "<error_message>",
  "recommended_action": "INFRA_CHECK | CONFIG_FIX | PROVIDER_SWITCH",
  "trace_id": "<uuid>"
}
```

---

## 7. Phase 2 통합 테스트 시나리오 (10건 이상)

| # | 시나리오 | 검증 대상 | 기대 결과 | LOCK/S7G |
|---|---------|----------|----------|----------|
| 1 | 13건 벤치마크 전수 promptfoo eval 실행 | E2E 동작 | 전체 JSON 결과 + 임계값 판정 | S7G-072 |
| 2 | PR push → 자동 스모크 실행 | CI 트리거 | 5분 이내 완료 + PR 코멘트 | S7G-072 |
| 3 | LOCK 임계값 미달 → 머지 차단 | Branch protection | status check FAIL → 머지 불가 | S7G-072 |
| 4 | nightly 전수 실행 → 결과 저장 | 스케줄 | BenchmarkStore에 13건 결과 적재 | F-07 |
| 5 | 시뮬레이션 → 실 배포 모드 전환 | 모드 전환 | EVAL_MODE=live → 실 API 호출 | P1-2 이월 |
| 6 | 3%+ 하락 → 회귀 알림 | 회귀 감지 | Slack/Email 알림 + PR FAIL | LOCK-BE-14 |
| 7 | seed=42 재현성 (2회 실행) | 재현성 | 결과 일치 (live 모드 포함) | LOCK-BE-08 |
| 8 | Bootstrap 95% CI 포함 리포트 | CI 리포트 | 모든 벤치마크에 CI 표시 | LOCK-BE-06 |
| 9 | BORDERLINE 결과 시 PR 경고 | 경계 판정 | 코멘트에 BORDERLINE 표시 | S7G-072 |
| 10 | API rate limit → graceful degradation | 예외 처리 | 부분 결과 저장 + 미실행 목록 | S7G-072 |
| 11 | LLM-as-Judge 연동 (MT-Bench, LogicKor) | Judge 통합 | llm-rubric assert 정상 동작 | S7G-071 |
| 12 | 프롬프트 변경 감지 → 관련 벤치마크만 실행 | 선택 실행 | paths 필터 동작 확인 | S7G-072 |

---

## 부록: ABC 패턴 매핑

| ABC 단계 | promptfoo 통합 매핑 |
|---------|-------------------|
| A (분석) | 변경 범위 파악 + 실행 대상 벤치마크 결정 + 설정 로드 |
| B (실행) | promptfoo eval 실행 + LLM-as-Judge 연동 + 결과 변환 |
| C (검증) | 임계값 판정 + 회귀 감지 + PR 코멘트/머지 차단 |
