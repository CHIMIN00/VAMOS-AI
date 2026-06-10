# Coding Benchmarks — 코딩 벤치마크 채점 규칙 및 실행 파라미터

> **Phase**: 1-A (P1-1)
> **범위**: S7G-019 (HumanEval+)
> **작성일**: 2026-04-12
> **상태**: V1 정의 완료

---

## 교차 참조 블록

| 정본 문서 | 참조 내용 |
|-----------|----------|
| STEP7-G S7G-019 | Part 3 코딩 벤치마크 — HumanEval+ 목표값/평가 방식/우선순위 |
| BENCHMARK_EVALUATION_상세명세.md §A-2 | HumanEval 채점: Docker 샌드박스, pass@k 계산, 10초/문제 |
| AUTHORITY_CHAIN.md LOCK-BE-02 | HumanEval pass@1 ≥ 85% (원본 HumanEval 기준, 참조) |
| AUTHORITY_CHAIN.md LOCK-BE-06 | Bootstrap 95% CI 필수 |
| AUTHORITY_CHAIN.md LOCK-BE-08 | seed=42 고정 |
| CONFLICT_LOG C-09 | 코드 샌드박스 타임아웃 10s(평가) vs 30s(운영) — 용도별 분리, 양립 가능 |
| Phase 0 F-01 | benchmark_runner.py — HumanEval 실행 경험 재활용 |
| Phase 0 F-02 | schemas/benchmark_result.schema.json — 결과 스키마 |
| Phase 0 F-05 | promptfoo.yaml — 기존 HumanEval(S7G-002) 설정 참조 |
| general_llm_benchmarks.md S7G-002 | HumanEval 기본 정의 (Docker, pass@1, 10초 타임아웃) |

---

## S7G-019: HumanEval+ (보강 테스트 케이스)

### 개요

| 항목 | 값 |
|------|-----|
| **ID** | S7G-019 |
| **우선순위** | HIGH |
| **버전** | V1 |
| **목표** | pass@1 ≥ 75% (종합계획서 Phase 1-A 정본) |
| **Phase 0 상태** | 미매핑 (§A-2 확장으로 분류) |
| **관련** | S7G-002 HumanEval (원본) — Phase 0에서 실행 완료 |

### HumanEval vs HumanEval+ 차이

| 항목 | HumanEval (S7G-002) | HumanEval+ (S7G-019) |
|------|---------------------|----------------------|
| 문항 수 | 164 | 164 (동일 문항) |
| 테스트 케이스 수 | ~1개/문항 (평균) | **~80배 보강** (~80개/문항) |
| 목표 | pass@1 ≥ 85% (LOCK-BE-02) | pass@1 ≥ 75% (낮은 기준) |
| edge case | 기본 | 경계값, 빈 입력, 대규모 입력, 특수 문자 등 |
| 목적 | 기본 코드 생성 능력 | **견고성(robustness)** 측정 |

### 입력 포맷

HumanEval과 동일한 함수 시그니처 + docstring 형식.

```python
def {function_name}({params}) -> {return_type}:
    """
    {docstring with examples}
    >>> {example_call}
    {expected_output}
    """
    # Model generates function body
```

- **데이터셋**: 164문항 (HumanEval 동일 문항, 테스트만 보강)
- **V1 골든셋**: 30문항 (난이도 분포 + edge case 커버리지 기준 선별, seed=42)
  - HumanEval V1 골든셋(20문항)과 중복 허용 (동일 문항이므로)
- **실행 환경**: Docker 샌드박스, Python 3.11 (Phase 0 S7G-002 설정 재활용)
- **타임아웃**: 10초/문제 (§A-2, CONFLICT_LOG C-09: 평가 환경 기준)

### 채점 방식

1. **코드 추출**: ` ```python ` 블록 또는 함수 본문 자동 추출 (S7G-002 동일 로직)
2. **실행**: Docker 샌드박스에서 **보강된 테스트 케이스** 전수 실행
3. **판정**: pass (보강 테스트 **전부** 통과) / fail (하나라도 실패)
4. **부분 점수 없음** (binary — 원본 테스트만 통과하고 보강 테스트 실패 시 FAIL)
5. **pass@k 계산**: `1 - C(n-c, k) / C(n, k)`
6. **메트릭**: pass@1 (primary), 원본 HumanEval 대비 하락률 (secondary)
7. **신뢰구간**: Bootstrap 95% CI (LOCK-BE-06, B=10000)

### 알고리즘: pass@k 산출

```
Algorithm: pass_at_k(n, c, k)
Input: n (총 시도), c (통과 수), k (k값)
Output: pass@k 확률

Time Complexity: O(k) — 조합 계산
Space Complexity: O(1)

LOCK 참조: LOCK-BE-08 (seed=42로 n 시도 결정론적)
ABC 패턴: Compute → Aggregate → Report

1. IF c >= n: RETURN 1.0
2. IF k > n: RETURN 1.0 if c > 0 else 0.0
3. pass_at_k = 1 - product((n-c-i)/(n-i) for i in range(k))
4. RETURN pass_at_k
```

### 실행 파라미터

```yaml
benchmark_id: S7G-019
name: HumanEval+
type: code_generation_robust
model: ${MODEL_ID}
temperature: 0
seed: 42
max_tokens: 2048
dataset_size: 164
golden_set_size: 30
test_suite: humaneval_plus   # 보강 테스트 (~80x)
scoring: pass_at_k
k_values: [1, 5, 10]
primary_metric: pass_at_1
execution_env: docker
docker_image: python:3.11-slim  # Phase 0 재활용
timeout_seconds: 10              # §A-2 기준
ci_method: bootstrap
ci_level: 0.95
ci_bootstrap_b: 10000
```

### PASS/FAIL 판정

| 구간 | 판정 | 조건 |
|------|------|------|
| pass@1 ≥ 85% | **PASS** | 목표 충족 (LOCK-BE-02, CONFLICT_LOG C-13 RESOLVED) |
| 72% ≤ pass@1 < 75% | **BORDERLINE** | CI 상한 75%+ 시 조건부 PASS |
| pass@1 < 72% | **FAIL** | 목표 미충족 |

### 예외 처리 정책 표

| error_code | 설명 | recoverable | 처리 |
|------------|------|:-----------:|------|
| E-TIMEOUT | 코드 실행 10초 초과 | No | FAIL 판정, 다음 문항 진행 |
| E-SYNTAX | 생성 코드 구문 오류 | No | FAIL 판정, 로그 기록 |
| E-RUNTIME | 런타임 예외 (IndexError 등) | No | FAIL 판정, 에러 유형 기록 |
| E-MEMORY | 메모리 초과 (512MB 제한) | No | FAIL 판정, 제한 초과 경고 |
| E-IMPORT | 허용되지 않은 모듈 import | No | FAIL 판정, 보안 위반 로그 |
| E-EXTRACT | 코드 블록 추출 실패 | No | FAIL 판정, 추출 실패 로그 |
| E-API | API 호출 실패 | Yes | retry (max 3, backoff 2^n초) |
| E-DOCKER | Docker 컨테이너 실패 | Yes | 컨테이너 재생성 후 retry (max 2) |

### 로깅 포맷 (R-01-7)

```json
{
  "trace_id": "bench-humaneval-plus-{run_id}",
  "benchmark": "S7G-019",
  "timestamp": "{ISO-8601}",
  "error": {
    "code": null,
    "message": null,
    "timeout_count": 0,
    "syntax_error_count": 0,
    "runtime_error_count": 0
  },
  "context": {
    "model_id": "{model_version}",
    "seed": 42,
    "dataset_size": 30,
    "test_suite": "humaneval_plus",
    "docker_image": "python:3.11-slim",
    "timeout_seconds": 10,
    "environment": "{os/python/gpu}"
  },
  "recovery": {
    "retry_count": 0,
    "docker_restart_count": 0,
    "fallback_used": false
  }
}
```

### 에스컬레이션 (I-20 경유, R-01-8)

```json
{
  "escalation_type": "BENCHMARK_THRESHOLD_BREACH",
  "benchmark_id": "S7G-019",
  "lock_id": null,
  "threshold": 0.75,
  "actual": "{pass_at_1}",
  "severity": "HIGH",
  "route": "I-20 → QA-GATE",
  "note": "HumanEval+ 견고성 기준 — S7G-002 HumanEval 대비 하락률도 함께 보고"
}
```

---

## 공통 인터페이스 — Phase 0 산출물 정합성

### benchmark_runner.py (F-01) 등록 인터페이스

```python
# S7G-019 등록 (Phase 1-A 확장)
runner.register(
    benchmark_id="S7G-019",
    name="HumanEval+",
    scorer=CodeExecScorer(
        docker_image="python:3.11-slim",
        timeout=10,
        test_suite="humaneval_plus"  # 보강 테스트 사용
    ),
    dataset=GoldenSet("humaneval_plus", size=30),
    ci_config=CIConfig(method="bootstrap", B=10000, level=0.95),
    threshold=ThresholdConfig(lock_id=None, pass_value=0.75, borderline_delta=0.03)
)
```

### schemas/benchmark_result.schema.json (F-02) 매핑

| F-02 필드 | S7G-019 값 |
|-----------|-----------|
| benchmark_name | "HumanEval+" |
| model_id | ${MODEL_ID} |
| run_date | ISO-8601 |
| score | pass_at_1 |
| confidence_interval | {ci_low, ci_high, level: 0.95, method: "bootstrap", B: 10000} |
| metadata | {seed: 42, docker_image, timeout: 10, test_suite: "humaneval_plus", golden_set_used: true} |
| status | PASS/BORDERLINE/FAIL |
| extended | {humaneval_original_pass_at_1: (S7G-002 결과 참조), delta: pass@1_original - pass@1_plus} |

### promptfoo.yaml assertion 매핑

| 벤치마크 | assertion type | threshold | LOCK |
|---------|---------------|-----------|------|
| S7G-019 HumanEval+ | python_exec (pass@1, robust tests) | ≥ 0.75 | (목표값, LOCK 미등록) |

---

## 복구/재시도 흐름도

```
[실행 시작] → [코드 생성 API 호출]
  ├── 성공 → [코드 추출] → [Docker 실행 (보강 테스트)]
  │     ├── 전체 통과 → PASS
  │     ├── 원본 통과 + 보강 실패 → FAIL (견고성 미달)
  │     ├── 원본도 실패 → FAIL
  │     └── 타임아웃 → FAIL (E-TIMEOUT)
  ├── API 실패 → retry (max 3)
  └── Docker 실패 → 컨테이너 재생성 (max 2)
```

### 다운그레이드 시 confidence penalty 표

| 다운그레이드 유형 | 점수 penalty | 적용 대상 |
|-----------------|-------------|----------|
| 보강 테스트 → 원본 테스트만 | 결과를 S7G-002와 동등 취급 (S7G-019 결과로 미인정) | S7G-019 |
| 타임아웃 10s → 30s | 표기 변경 (CONFLICT_LOG C-09 참조), 성능 비교 불가 | S7G-019 |
| 데이터셋 축소 (164 → 서브셋) | CI 폭 확대 | S7G-019 |
| seed 변경 | 재현성 LOCK-BE-08 위반 경고 | S7G-019 |

---

## Phase 2 통합 테스트 시나리오 (10건 이상)

| # | 시나리오 | 주입 방법 | 기대 결과 |
|---|---------|----------|----------|
| T-01 | 전수(164문항) HumanEval+ 실행 | 전체 데이터셋 투입 | pass@1 산출, CI 범위 확인, 총 실행시간 < 30분 |
| T-02 | 원본 HumanEval 통과 but HumanEval+ 실패 문항 분석 | S7G-002 PASS + S7G-019 FAIL 교차 분석 | 하락률 리포트 (예: 85% → 75%, 10%p 하락), edge case 유형별 분류 |
| T-03 | Docker 보안 격리 — 파일시스템 접근 시도 | open('/etc/passwd') 등 포함 코드 | 샌드박스 차단, FAIL, 보안 로그 |
| T-04 | 메모리 폭탄 코드 (512MB 초과) | 대규모 리스트 생성 코드 | E-MEMORY 판정, 컨테이너 정상 종료, 다음 문항 진행 |
| T-05 | seed=42 재현성 검증 | 동일 설정 2회 연속 실행 | 바이트 수준 동일 결과 |
| T-06 | 목표값 경계 테스트 (pass@1 74.9%) | 시뮬레이션으로 74.9% 주입 | status=FAIL, BORDERLINE 조건 확인 |
| T-07 | 다국어 코드 생성 (Python + 주석 한국어) | 한국어 docstring 문항 | 코드 추출기가 한국어 주석 정상 처리 |
| T-08 | 동시 실행 (S7G-002 + S7G-019) Docker 격리 | 두 벤치마크 병렬 실행 | 별도 컨테이너, 결과 독립 |
| T-09 | 보강 테스트 중 빈 입력 edge case | function([]) → expected output | 빈 입력 처리 정확성 검증 |
| T-10 | 코드 추출 실패 시 graceful degradation | 모델이 설명만 출력 (코드 블록 없음) | E-EXTRACT 판정, 해당 문항 FAIL, 로그 기록, 전체 실행 계속 |
| T-11 | pass@5, pass@10 계산 정확성 | n=10 시도, c=7 통과 주입 | pass@1=0.7, pass@5 계산값 검증 |
| T-12 | promptfoo assertion 연동 | promptfoo eval에서 S7G-019 assertion 실행 | threshold ≥ 0.75 assertion 결과 + F-02 변환 성공 |

---

## 변경 이력

| 날짜 | 변경 내용 | 근거 |
|------|----------|------|
| 2026-04-12 | Phase 1-A P1-1 초기 작성: S7G-019 HumanEval+ 채점 규칙 + 실행 파라미터 정의 | §7.3 Phase 1-A 절차 3 |
| 2026-04-12 | Phase 0 HumanEval(S7G-002) Docker 설정 재활용, 보강 테스트 차이점 명시 | §7.3 Phase 1-A 절차 3 |

---

## Phase 4 §확장 (V3-Phase 4 production-ready, RECOVERY genuine write 2026-06-03)

> **Status**: **APPROVED** | **scope**: P4-6 그룹 2 (코딩, 3-7 cross-domain). V1/V2 본문(상기) byte 무변경 prefix EXACT.

### S7G-024 코드 보안 평가 — CWE/SAST 기반
- **측정**: CWE Top 25 생성 빈도 + SQLi/XSS/Buffer Overflow + Semgrep/CodeQL 자동 스캔. **목표: 보안 취약 코드 생성률 < 2%**.

### S7G-025 코드 리뷰 품질 — PR 리뷰 정확도
- **측정**: 버그 발견률 + 제안 정확성 + false positive 비율. 3-7 Dev Node 코드 리뷰 기능 품질 기준.

### S7G-026 디버깅 능력 — 버그 찾기·고치기
- **측정**: 버그 식별률 + 수정 정확률 + 설명 품질. 데이터셋 BugsInPy, Defects4J (Java).

- **3-7 cross-domain 측정 위임 (R-T5-1)**: S7G-024~026 V3 측정 위임 — 3-7 Developer-Tools (Wave 1 #9 ✅) 정본 소유 항목 측정 routing, source 0 touch. **LOCK 재정의 0**. S7G-024/025/026 = DONE.
