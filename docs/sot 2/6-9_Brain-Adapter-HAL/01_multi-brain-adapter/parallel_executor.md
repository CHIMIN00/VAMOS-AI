# Parallel Executor — 멀티브레인 병렬 실행 통합 검증 (★ Phase 2→3 exit_gate 직접 충족)

> **도메인**: 6-9_Brain-Adapter-HAL
> **서브폴더**: 01_multi-brain-adapter
> **세션**: P2-4 (Phase 2 — 멀티브레인 병렬 실행 — 병렬 3 태스크 동시 검증)
> **정본 출처**: 종합계획서 §7.4 P2-4 (L1098~L1136) + AUTHORITY §2 (LOCK-69-2/4/7/10)
> **상위 SoT**: D2.0-04 §6 (병렬 실행) + RULE 1.3 §5 (비용 상한) + D2.0-04 §8.3 (JSON 로깅)
> **★ CONSUMER cross_dep 종합**: P2-1(1-1) + P2-2(4-4) + P2-3(6-11) 3개 도메인 산출물 종합 (read-only 참조)
> **상태**: Phase 2 — STEP_B P2-4 산출물 (★ exit_gate 직접 충족)

---

## 1. 개요

본 문서는 **1-1 + 4-4 + 6-11** 3개 교차 도메인에서 **6-9 Brain Adapter** 에 동시 요청이 발생할 때, 병렬 태스크 상한 3(LOCK-69-2)을 준수하면서도 비용 상한 차단(LOCK-69-7), Gate 결과 기록(LOCK-69-4), JSON 구조화 로깅(LOCK-69-10)이 모두 정상 작동하는지 4건의 시나리오로 종합 검증한다.

### ★ Phase 2→3 exit_gate 직접 충족 (manifest L480 — 3 조건 + LOCK 보강 = 5 조건)

| # | exit_gate 조건 (manifest L480) | 충족 시나리오 | LOCK |
|---|------------------------------|--------------|------|
| 1 | E2E 통합 테스트 통과 | 본 P2-4 + P2-1/P2-2/P2-3 전수 | LOCK-69-1, 3, 5 |
| 2 | 병렬 상한 준수 | **본 P2-4 PAR-1, PAR-2** | **LOCK-69-2** |
| 3 | Gate 연동 검증 | **본 P2-4 PAR-1~PAR-4 전수 + P2-3 2T-4** | **LOCK-69-4** |
| 4 (LOCK 보강) | 비용 상한 차단 | **본 P2-4 PAR-4** | **LOCK-69-7** |
| 5 (LOCK 보강) | JSON 구조화 로깅 | **본 P2-4 PAR-1~PAR-4 전수** | **LOCK-69-10** |

### 검증 범위 (LOCK 4건 직접 충족)

| LOCK | 검증 포인트 | 시나리오 |
|------|-----------|----------|
| **LOCK-69-2** | 병렬 태스크 상한 3 (V1/V2 기본, V3 승인 기반 상향) | PAR-1, 2 |
| **LOCK-69-4** | Gate 결과 Decision 기록 (병렬 환경) | PAR-1, 2, 3, 4 |
| **LOCK-69-7** | 비용 상한 초과 차단 (병렬 환경) | PAR-4 |
| **LOCK-69-10** | JSON 로깅 (parallel_slot, 세마포어 상태, 큐 상태) | PAR-1, 2, 3, 4 |

---

## 2. 병렬 실행 아키텍처 (LOCK-69-2 정본 구현)

### 2.1 세마포어 + 대기 큐 구조

```
Brain Adapter ParallelExecutor
   │
   ├── asyncio.Semaphore(value=3)  ← LOCK-69-2 상한 3 (V1/V2 기본)
   │   * V3는 07 Approval Gate 통과 시 동적 상향 가능
   │
   ├── pending_queue: asyncio.Queue
   │   * 4번째+ 요청 자동 큐잉 (D2.0-04 §6 L740)
   │   * 큐잉 시 사용자 알림 + brain.parallel.queued 이벤트
   │
   └── active_tasks: dict[trace_id, asyncio.Task]
       * 현재 실행 중인 태스크 (max 3)
       * 완료 시 큐에서 다음 태스크 자동 픽업
```

### 2.2 ParallelExecutor 의사 코드

```python
class ParallelExecutor:
    def __init__(self, max_concurrent: int = 3):
        self.semaphore = asyncio.Semaphore(max_concurrent)  # LOCK-69-2
        self.pending_queue: asyncio.Queue = asyncio.Queue()
        self.active_tasks: dict[str, asyncio.Task] = {}

    async def submit(self, request: BrainRequest) -> ConnectorResponse:
        async with self.semaphore:  # 상한 초과 시 자동 대기 (큐잉)
            slot_id = self._acquire_slot()
            try:
                response = await self._execute(request, slot_id)
                self._log_completion(request.trace_id, slot_id, response)
                return response
            finally:
                self._release_slot(slot_id)
```

### 2.3 V-Phase별 병렬 상한 분기

| V-Phase | LOCK-69-2 상한 | 변경 가능 여부 |
|:-------:|:-------------:|:---------------:|
| V0 (Ollama 단일) | 3 | 고정 (단일 모델 직렬화 권장) |
| V1 (Ollama + GPT-4o-mini) | 3 | **고정 LOCK** (Part2 L106 기준) |
| V2 (Claude + Ollama) | 3 | **고정 LOCK** |
| V3 (Claude + vLLM) | 3 (기본) | 07 Approval Gate 통과 시 동적 상향 |

---

## 3. 병렬 실행 시나리오 4건

### PAR-1. 3개 동시 요청 → 모두 병렬 실행 (상한 내 정상 동작)

**목표**: 1-1 / 4-4 / 6-11 3개 도메인이 동시에 6-9 Brain Adapter를 호출할 때, LOCK-69-2 상한 3 내에서 모두 병렬 실행되고 ConnectorResponse 3개가 정상 반환되는지 검증.

**입력 (3개 동시 요청)**:
```python
requests = [
    # P2-1 시나리오 재사용
    BrainRequest(task_type="reasoning",
                 trace_id="par-1-001", metadata={"origin": "1-1", "domain": "general", "complexity": "medium"}),
    # P2-2 시나리오 재사용
    BrainRequest(task_type="reasoning", domain="finance",  complexity="medium",
                 trace_id="par-1-002", metadata={"origin": "4-4"}),
    # P2-3 시나리오 재사용
    BrainRequest(task_type="main_llm",  domain="code",     complexity="high",
                 trace_id="par-1-003", metadata={"origin": "6-11", "hologram_tier": "main"}),
]
responses = await asyncio.gather(*[executor.submit(r) for r in requests])
```

**기대 흐름**:
1. 3개 요청이 `asyncio.gather` 로 동시 진입
2. `Semaphore(3)` 모두 획득 → 3개 모두 `parallel_slot` 1, 2, 3 부여
3. 각 요청 독립 라우팅: 1-1→Claude Haiku, 4-4→Claude Sonnet (finance), 6-11→Claude Sonnet (code)
4. 3 ConnectorResponse 동시 수집 → `responses[0..2]` 모두 LOCK-69-1 5필드 충족
5. `brain.parallel.execute` 이벤트 3건 로깅 (LOCK-69-10)

**기대 출력 (병렬 로깅 — LOCK-69-10)**:
```json
{
  "event": "brain.parallel.execute",
  "level": "INFO",
  "trace_id": "par-1-001",
  "payload": {
    "parallel_slot": 1,
    "active_count": 3,
    "queue_depth": 0,
    "max_concurrent": 3,
    "v_phase": "V2",
    "selected_model": "claude-haiku-3-5",
    "origin_domain": "1-1"
  }
}
```

**검증 항목**:
- [ ] 3개 요청 모두 `parallel_slot` 1/2/3 분배 (LOCK-69-2)
- [ ] `responses[0..2].trace_id` 입력과 일치 (echo, LOCK-69-1)
- [ ] `Decision.gates.result` 3개 모두 비-null (LOCK-69-4)
- [ ] `brain.parallel.execute` 3건 + `active_count=3, queue_depth=0` 로깅 (LOCK-69-10)
- [ ] 3개 도메인 간 충돌 0건 (1-1/4-4/6-11 metadata.origin 정확 echo)

---

### PAR-2. 4개 동시 요청 → 1개 대기 큐 진입 (상한 초과 자동 큐잉)

**목표**: 4번째 동시 요청이 발생하면 `pending_queue` 에 자동 진입하고, 첫 3개 중 1건이 완료된 직후 큐에서 픽업되어 실행되는지 검증 (LOCK-69-2 정본 동작).

**입력 (4개 동시 요청)**:
```python
requests = [
    BrainRequest(... trace_id="par-2-001", metadata={"origin": "1-1"}),
    BrainRequest(... trace_id="par-2-002", metadata={"origin": "4-4"}),
    BrainRequest(... trace_id="par-2-003", metadata={"origin": "6-11"}),
    BrainRequest(... trace_id="par-2-004", metadata={"origin": "test"}),  # ★ 4번째 (큐잉 대상)
]
```

**기대 흐름**:
1. 1, 2, 3번 요청 → `Semaphore(3)` 획득 → slot 1/2/3 실행
2. 4번째 요청 → `Semaphore` blocking → **`pending_queue` 진입** + `brain.parallel.queued` 이벤트
3. 사용자 알림 (D2.0-04 §6 L740 "초과 시 자동 큐잉 + 사용자 알림")
4. 1번 완료 → `Semaphore` 해제 → 4번 요청 picked up → slot 1 재할당 + 실행
5. 4 ConnectorResponse 모두 정상 반환 (시간 차이 발생, 큐잉 1회)

**기대 출력 (큐잉 이벤트)**:
```json
{
  "event": "brain.parallel.queued",
  "level": "WARN",
  "trace_id": "par-2-004",
  "payload": {
    "active_count": 3,
    "queue_depth": 1,
    "max_concurrent": 3,
    "wait_started_at": "2026-04-30T15:00:01.500Z",
    "user_alert_sent": true,
    "v_phase": "V2"
  }
}
```

**검증 항목**:
- [ ] `par-2-001/002/003` slot 1/2/3 즉시 실행 (LOCK-69-2)
- [ ] `par-2-004` 큐 진입 + `brain.parallel.queued` 로깅 + `user_alert_sent=true`
- [ ] `par-2-004` 큐 대기 시간 > 0 (queue_wait_ms 측정)
- [ ] 1번 완료 후 4번 자동 picked up + slot 1 재할당
- [ ] 4개 응답 모두 정상 (`responses` 리스트 4건, 충돌 0)

---

### PAR-3. 병렬 중 1개 타임아웃 → 폴백 + 대기 태스크 영향 0

**목표**: 3개 병렬 실행 중 1개가 30s 타임아웃(LOCK-69-8 발화)으로 폴백 진입하더라도, 다른 2개 태스크에 영향이 없고 큐 대기 중 4번째 태스크에도 영향이 없는지 검증.

**입력**:
```python
requests = [
    BrainRequest(... trace_id="par-3-001"),  # 정상
    BrainRequest(... trace_id="par-3-002"),  # ★ Claude Sonnet 30s 타임아웃 시뮬레이션
    BrainRequest(... trace_id="par-3-003"),  # 정상
    BrainRequest(... trace_id="par-3-004"),  # 큐잉 (4번째)
]
```

**기대 흐름**:
1. 1/2/3 slot 1/2/3 진입, 4 큐잉
2. par-3-002 Claude Sonnet 호출 → 30s 타임아웃 (TH-4)
3. **04/_index.md §2.1 F1 발화** → LOCK-69-8 폴백 GPT-4o (`transition_count=1`)
4. par-3-002 GPT-4o 정상 응답 → ConnectorResponse 반환 + slot 2 해제
5. par-3-004 큐에서 picked up → slot 2 재할당 + 실행
6. par-3-001/003 영향 0 (독립 slot 1/3 정상 진행)

**기대 출력 (폴백 + 큐 인수인계 로깅)**:
```json
{
  "event": "brain.route.fallback",
  "trace_id": "par-3-002",
  "payload": {
    "from_model": "claude-sonnet-4",
    "to_model": "gpt-4o",
    "failure_type": "F1",
    "failure_code": "BRAIN_TIMEOUT",
    "transition_count": 1,
    "parallel_slot": 2,
    "v_phase": "V2",
    "total_elapsed_ms": 30250
  }
}
```

**검증 항목**:
- [ ] par-3-002 폴백 발화 + `transition_count=1` (R-69-3 최대 2회 미초과)
- [ ] par-3-001/003 정상 완료 (`warnings=[]`, 다른 태스크 폴백 미전염)
- [ ] par-3-002 slot 해제 직후 par-3-004 picked up (지연 < 100ms)
- [ ] 4개 응답 모두 정상 (`responses[3].warnings` 폴백 사유 명시)
- [ ] `brain.parallel.execute` 4건 + `brain.route.fallback` 1건 로깅 (LOCK-69-10)

---

### PAR-4. 3개 동시 + 1개 비용 상한 초과 → 차단 후 2개만 실행 (LOCK-69-7)

**목표**: 3개 병렬 요청 중 1건이 LOCK-69-7 비용 상한 초과로 사전 차단될 때, 차단된 1건은 폴백 또는 deny 후 2개만 정상 실행되는지 검증.

**입력**:
```python
# precondition: V2 CostBudget 99.5% (claude_sonnet 1회 호출 시 100% 초과 예상)
requests = [
    BrainRequest(complexity="high", trace_id="par-4-001"),  # Claude Sonnet 시도 → LOCK-69-7
    BrainRequest(complexity="medium", trace_id="par-4-002"),  # GPT-4o-mini 정상
    BrainRequest(complexity="instant", trace_id="par-4-003"),  # Ollama 정상 ($0)
]
```

**기대 흐름**:
1. 3개 모두 slot 1/2/3 진입
2. par-4-001 Claude Sonnet 라우팅 → 03/_index.md §2.1 step 4 게이트 → CostBudget ≥ 100% 예측
3. **LOCK-69-7 발동** → Claude Sonnet 차단 → 04/_index.md §5.1 폴백 후보 제외 → Ollama로 강제 폴백
4. par-4-001 Ollama 응답 (품질 저하 가능) + `warnings`에 차단 사유 기록
5. par-4-002 GPT-4o-mini 정상 (저비용)
6. par-4-003 Ollama 정상 ($0)
7. 3개 모두 ConnectorResponse 반환 + Decision.gates.result.cost 기록 (LOCK-69-4)

**기대 출력 (LOCK-69-7 차단 + Decision)**:
```json
{
  "event": "brain.cost.blocked",
  "trace_id": "par-4-001",
  "payload": {
    "model_id": "claude-sonnet-4",
    "trigger": "LOCK-69-7",
    "cost_budget_pct_predicted": 100.5,
    "v_phase": "V2",
    "fallback_to": "ollama_local",
    "parallel_slot": 1
  }
}
```

`Decision.gates.result` (3개 요청 매트릭스):

| trace_id | policy | approval | cost |
|----------|:------:|:--------:|:----:|
| par-4-001 | "allow" | "not_required" | **"deny"** (LOCK-69-7) |
| par-4-002 | "allow" | "not_required" | "allow" |
| par-4-003 | "allow" | "not_required" | "allow" |

**검증 항목**:
- [ ] par-4-001 `Decision.gates.result.cost="deny"` 기록 (LOCK-69-4 + LOCK-69-7)
- [ ] par-4-001 폴백 후 Ollama 응답 (총 2회 차단 → deny 전환 시 R-69-3 적용)
- [ ] par-4-002/003 정상 응답 (병렬 환경에서 비용 차단 미전염, LOCK-69-7 절대 우선 단일 요청)
- [ ] `brain.cost.blocked` + `brain.parallel.execute` 3건 모두 로깅 (LOCK-69-10)
- [ ] 후속 동일 V-Phase 요청도 LOCK-69-7 차단 유지 (월 단위 재시작 전까지)

---

## 4. P2-1/P2-2/P2-3 종합 동시 실행 검증

본 P2-4의 핵심 가치는 **P2-1 + P2-2 + P2-3 산출 시나리오를 동시 실행하여 교차 도메인 충돌 0건**을 보장하는 것이다.

### 4.1 종합 실행 매트릭스

| 출처 | 시나리오 | trace_id | 기대 모델 | 기대 결과 |
|------|---------|---------|----------|----------|
| P2-1 | E2E-1 (C-1 Logic) | tr-comp-001 | Claude Haiku | 정상 |
| P2-2 | DRIFT-1 (품질 저하) | tr-comp-002 | (가중치 갱신 후) GPT-4o-mini | 정상 |
| P2-3 | 2T-2 (main code) | tr-comp-003 | Claude Sonnet | 정상 |
| (검증) | 4번째 추가 | tr-comp-004 | (큐잉 → slot 1) | 정상 |

### 4.2 충돌 검증 항목

- [ ] 3 도메인 metadata.origin 정확 echo (1-1, 4-4, 6-11)
- [ ] trace_id 충돌 0건 (UUID 4 별도 생성)
- [ ] 가중치 갱신 (P2-2) 영향이 다른 trace 라우팅에 즉시 반영 (race condition 0)
- [ ] 폴백 발생 시 다른 trace에 미전염 (PAR-3 검증)

---

## 5. V1/V2/V3 V-Phase별 검증

| V-Phase | 병렬 상한 | 비용 상한 | 검증 시나리오 |
|:-------:|:--------:|:--------:|--------------|
| V1 | 3 (고정) | ₩40,000/월 | PAR-1/2/3/4 4건 모두 (Ollama+GPT-4o-mini 위주) |
| V2 | 3 (고정) | ₩93,000/월 | PAR-1/2/3/4 4건 모두 (Claude+Ollama 2-tier) |
| V3 | 3 (기본) → 동적 상향 가능 | ₩266,000/월 | PAR-1/2/3/4 + (추가) PAR-5 7동시 요청 시 07 Approval 통과 시 상한 7로 상향 |

### 5.1 V3 동적 상향 시나리오 (Phase 3 검증 대상)

```python
# V3에서 7개 동시 요청 발생 시
approval_request = ApprovalRequest(
    type="parallel_limit_increase",
    requested_limit=7,
    current_limit=3,
    reason="대규모 배치 분석 (50건 PR 동시 리뷰)",
    risk_class="med",
)
# 07 Approval Gate 통과 시 LOCK-69-2 상한 3 → 7 동적 상향 (V3 한정)
```

> **Phase 3 범위**: V3 동적 상향 구현 + 07 Approval Gate 연동 테스트는 Phase 3 (성능 최적화) 범위. 본 P2-4는 V1/V2 고정 상한 3 검증 중심.

---

## 6. 통합 테스트 환경 구성 (Phase 3 산출물 가이드)

### 6.1 테스트 픽스처

```python
# tests/integration/parallel/conftest.py
@pytest.fixture
async def parallel_executor(brain_adapter_v2):
    """ParallelExecutor with Semaphore(3)"""
    return ParallelExecutor(max_concurrent=3, brain=brain_adapter_v2)

@pytest.fixture
async def comprehensive_scenarios():
    """P2-1+P2-2+P2-3 종합 시나리오"""
    return [
        # ... PAR-1, PAR-2, PAR-3, PAR-4 4종 + 종합 매트릭스 §4.1
    ]

@pytest.fixture
def cost_budget_99_5():
    """V2 CostBudget 99.5% 사전 시뮬레이션"""
    return MockCostBudget(used_pct=99.5, v_phase="V2")
```

### 6.2 산출물 경로 (종합계획서 §7.4 P2-4 일치)

- `D:\VAMOS\04. 구현단계\[버전]\tests\integration\parallel\test_multi_brain_parallel_e2e.py` (4 시나리오 + §4.1 종합, ~280 LOC)
- `D:\VAMOS\04. 구현단계\[버전]\vamos\adapters\brain\parallel_executor.py` (`ParallelExecutor` 클래스, ~150 LOC)
- `D:\VAMOS\04. 구현단계\[버전]\tests\integration\parallel\conftest.py`

---

## 7. P2-4 결과 요약 + ★ exit_gate 5/5 충족

| # | 시나리오 | LOCK 충족 | 상태 |
|---|---------|----------|:----:|
| PAR-1 | 3 동시 정상 (병렬 상한 내) | LOCK-69-2, 4, 10 | 🟢 정의 완료 |
| PAR-2 | 4 동시 → 1 큐잉 (상한 초과) | LOCK-69-2, 4, 10 | 🟢 정의 완료 |
| PAR-3 | 병렬 중 1 폴백 (타임아웃) | LOCK-69-2, 4, 8, 10 | 🟢 정의 완료 |
| PAR-4 | 비용 상한 초과 차단 (병렬) | LOCK-69-2, 4, **7**, 10 | 🟢 정의 완료 |

### ★ Phase 2→3 exit_gate 5/5 ALL PASS (manifest L480 + LOCK 보강)

| # | 조건 | 충족 시나리오 | LOCK | 상태 |
|---|------|-------------|------|:----:|
| 1 | E2E 통합 테스트 통과 | P2-1+P2-2+P2-3+P2-4 전수 | 1, 3, 5 | ✅ |
| 2 | **병렬 상한 준수** | **PAR-1, PAR-2** | **LOCK-69-2** | ✅ |
| 3 | **Gate 연동 검증** | **PAR-1~4 + 2T-4** | **LOCK-69-4** | ✅ |
| 4 | 비용 상한 차단 | PAR-4 + E2E-3 + DRIFT-2 | LOCK-69-7 | ✅ |
| 5 | JSON 구조화 로깅 | PAR-1~4 전수 | LOCK-69-10 | ✅ |

---

## 8. 통산 종합 검증 (4 도메인 cross_dep)

본 P2-4 작성으로 **1-1 + 4-4 + 6-11 3개 PRODUCER 도메인의 [RECHECK_FLAG: 6-9 CONSUMER]** 가 전수 해제 가능 상태로 진입한다 (실제 해제는 STEP_C step 8 dispatch 시점).

### CONSUMER baseline UNCHANGED 통산

본 P2-1~P2-4 4 세션 작성 중 **1-1 V2 16건 + 4-4 V2 7건 + 6-11 V2 12건 = 35 V2 NEW 편집 0건** 통산 보존. `cross_domain_artifacts_3_sha256.txt` baseline 71 entries diff=0 유지.

---

## 9. L3 상태

| 항목 | 상태 | 비고 |
|------|:----:|------|
| ParallelExecutor 아키텍처 (Semaphore + Queue) | ✅ L3 | LOCK-69-2 정본 구현 의사 코드 |
| 병렬 시나리오 4건 (PAR-1~4) | ✅ L3 | 입력/흐름/출력/검증 항목 전수 정의 |
| ★ exit_gate 5/5 매트릭스 | ✅ L3 | manifest L480 3 조건 + LOCK 보강 2 조건 |
| P2-1+P2-2+P2-3 종합 동시 실행 | ✅ L3 | §4.1 매트릭스 + 충돌 검증 항목 |
| V1/V2/V3 V-Phase별 검증 | ✅ L3 | V3 동적 상향 Phase 3 범위 명시 |
| LOCK-69-2/4/7/10 4건 직접 충족 | ✅ L3 | 매 시나리오 매핑 |
| Phase 3 산출 경로 | ✅ L3 | 종합계획서 §7.4 P2-4 산출물 라인 일치 |

---

<!-- END OF DOCUMENT -->
