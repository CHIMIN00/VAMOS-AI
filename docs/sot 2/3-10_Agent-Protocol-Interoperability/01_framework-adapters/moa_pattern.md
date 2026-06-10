# Mixture of Agents (MoA) 패턴 — K-025 (V2 확장, L3)

> **STEP7-K**: K-025 — Mixture of Agents (MoA) 구현 (STEP7-K L479~L512)
> **레벨**: L3 (V2 확장 패턴, 상세 구현)
> **Part2 상태**: MINIMAL (§6.7 Agent Teams 언급) → 본 문서로 L3 보강
> **정본 소유**: #13 Agent-Protocol-Interoperability / 01_framework-adapters
> **V 스코프**: V2-Phase 2 (V1 2-모델 MoA는 즉시, 풀 MoA 2개월)
> **V2 태그**: V2-Phase 2 (2026-04-22, STAGE 7 STEP_B #2a 3-10 도메인 P2-1 세션 신규 작성)
> **upstream baseline**: STEP7-K sha256 `150720a3496f557d359a421dcbf0922ebe5b1e4fbaa06611eff40e0865177539`

---

## §1. 교차 참조 블록

| 정본 문서 | 섹션 | 참조 내용 |
|----------|------|----------|
| STEP7-K (Level 2) | L479~L512 | K-025 MoA 원본 정의 (Layer 1 Proposers 4개 / Layer 2 Aggregator / 활용 시나리오 / 비용 3-4배) |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-05 | **"Lead + max 2 Sub-Agent"** (V1 총 3 agent, 6-3 LOCK-AT-014 교차) |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-07 | A2A + MCP 양방향 (외부 LLM Provider 호출 필수) |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-09 | 비용 상한 V2 ₩93K (MoA 비용 3-4배 주의) |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-10 | HITL 트리거 < 50% (MoA 합의 confidence 저하 시 에스컬레이션) |
| 구조화_종합계획서.md | §7.4 P2-1 L1117~L1149 | Phase 2 V2 K-025 배치 근거 (MINIMAL → L3 승급) |
| 01_framework-adapters/langgraph_adapter.md | §3 | 공통 자료 구조 (VamosMessage, VamosPhase, FrameworkTaskRef, GatePolicy) import |
| 01_framework-adapters/magentic_one.md | §5 Orchestrator 루프 | MoA Aggregator 는 Orchestrator 의 `call_agent()` 대체 경로 |
| 01_framework-adapters/tool_memory_benchmark.md | §4 VBS-12 3-4 | MoA 품질 향상률 평가 (단일 vs 다중 에이전트 품질 비교) |
| 02_service-integration/llm_gateway.md | §§ Proposer Pool | Layer 1 Proposer 4개 (Ollama/Claude/GPT-4o/Gemini) LLM Gateway 경유 |
| **6-3 Agent-Teams-PARL AUTHORITY_CHAIN.md** | **§4 L67 LOCK-AT-014 row (SPEC S7-A-008)** | **값 verbatim "V1=3 / V2=10 / V3=50+"** — 본 도메인 LOCK-AP-05 "Lead + max 2 Sub-Agent" 와 교차 정합 (V1 총 3 = Lead 1 + Sub 2) |
| CONFLICT_LOG.md | #7 CFL-AP-007 | VamosMessage.type canonical `task/result/event/control` alias 매핑 (message_format.md §2.5 보존) |

> **R6 준수**: 본 문서는 What+How 전용. When/Where(Phase/Week)는 Part2 정본, 미기재.

---

## §2. 개요 (Purpose & Scope)

### 2.1 목적
Together AI 의 Mixture-of-Agents(MoA) 아키텍처를 VAMOS 3-10 Framework Adapter Layer 에 구현한다. **Layer 1 Proposers → Layer 2 Aggregator → Layer 3 최종 통합** 3계층 합의 프로세스를 통해 **복수 LLM 의 답변을 통합**하여 품질 향상을 확보한다. VAMOS V1 팀 제약(LOCK-AP-05 Lead+max 2 Sub-Agent, 6-3 LOCK-AT-014 V1=3)을 준수하면서, Aggregator 단일 Lead + 2 Proposers 구성으로 최소 MoA 를 구현한다.

### 2.2 범위
- **In-scope**: 2-모델 MoA (V1, Proposer 2개 + Aggregator 1개) + 풀 MoA (V2, 4-모델 Proposer + Aggregator), 비용 최적화 매트릭스, Layer 1/2 합의 알고리즘, LOCK-AP-09 비용 초과 차단, LLM Gateway(K-031) 의존성.
- **Out-of-scope (V3 이관)**: Layer 3 Meta-Aggregator (추가 계층), Together AI MoA API 직접 호출(V1 로컬 Ollama + 외부 Claude/GPT-4o 조합만 V2), Dynamic Proposer selection(proposer 수 동적 조정, V3), Federated MoA (서로 다른 VAMOS 노드 간 MoA, V3).

### 2.3 비고 — LOCK-AP-05 × LOCK-AT-014 교차 정합 verbatim 재확인

> **LOCK-AP-05 본 도메인 원본값** (AUTHORITY_CHAIN.md §3 row 5):
> - **ID**: LOCK-AP-05
> - **항목**: Agent Teams V1 제한
> - **원본 문서**: Part2 §6.7 LOCK-AT-014 (값 일치 확인: 6-3 LOCK-AT-014 참조)
> - **값**: **Lead + max 2 Sub-Agent**
> - **재정의**: **금지**
>
> **6-3 LOCK-AT-014 정본 값** (6-3 AUTHORITY_CHAIN.md L67, SPEC S7-A-008):
> - **ID**: LOCK-AT-014
> - **항목**: Agent Team size
> - **원본 문서**: 6-3 AUTHORITY_CHAIN.md L67 + Part2 §6.7
> - **값**: **V1=3 / V2=10 / V3=50+**
> - **재정의**: **금지** (6-3 정본 소유)
>
> **교차 정합**: 본 도메인 LOCK-AP-05 "Lead + max 2 Sub-Agent" = **V1 총 3 agent (Lead 1 + Sub 2)** → 6-3 LOCK-AT-014 "V1=3" 일치 ✅. V2 Phase 2 본 문서 작성 시점에서 **V1=3 상한을 MoA 에 그대로 적용**하며, V2=10 확장은 6-3 도메인 Agent-Teams-PARL 자체의 V2 마이그레이션 선행 시에만 본 도메인에서 적용.

---

## §3. 공통 자료 구조 참조

> **정본**: `01_framework-adapters/langgraph_adapter.md §3`. 아래는 참조만.

다음 타입을 **langgraph_adapter.md §3에서 그대로 import** 한다:
`VamosMessage` (LOCK-AP-01), `A2ATaskState` (LOCK-AP-03), `VamosPhase`, `FrameworkTaskRef`, `GatePolicy`, `AdapterResult`.

본 문서 전용 추가 타입:

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class ProposerAnswer(BaseModel):
    """Layer 1 Proposer 응답 단위"""
    proposer_id: Literal[
        "ollama_local_llama4",  # 빠른 초안
        "claude_opus_47",       # 분석적
        "gpt_4o",               # 창의적
        "gemini_25_pro",        # 최신 정보
        # V2 확장 proposer (Together AI, DeepSeek 등) 추가 시 이 Literal 갱신
    ]
    content: str
    confidence: float                       # 0.0 ~ 1.0
    tokens_used: int
    cost_krw: float                         # LOCK-AP-09 누적용
    latency_ms: int
    timestamp: datetime

class AggregatorResult(BaseModel):
    """Layer 2 Aggregator 통합 답변"""
    final_answer: str
    contributing_strengths: list[str]       # 각 proposer 답변의 강점 추출 결과
    contradictions_found: list[str]
    contradictions_resolved: list[str]
    agreement_score: float                  # 0.0 ~ 1.0 (proposer 간 합의 수준)
    total_cost_krw: float                   # Layer 1 + Layer 2 합산
    hitl_required: bool = False             # LOCK-AP-10 < 0.5 시 True

class MoAMode(BaseModel):
    """MoA 활성 모드 (비용 대비 품질 트레이드오프)"""
    mode: Literal["single", "moa_2_model", "moa_full_4_model"]
    budget_limit_krw: float                 # LOCK-AP-09 상한
    trigger_reason: Literal[
        "user_explicit_request",             # "확실한 답변이 필요해"
        "critical_decision",                 # 투자/금융 결정
        "multi_perspective_needed",          # 연구/코드리뷰
        "default",
    ]
```

---

## §4. MoA 3-Layer 아키텍처 (STEP7-K L482~L498 원문 매핑)

### 4.1 Layer 1 — Proposers (독립 초기 답변)

STEP7-K 원본 Proposer 4개 + VAMOS 매핑:

| Proposer | 원문 역할 (STEP7-K L488~L492) | VAMOS 매핑 |
|----------|------------------------------|----------|
| Ollama (로컬 Llama 4) | 빠른 초안 | 로컬 폴백, 비용 0 |
| Claude API (Opus 4.7) | 분석적 답변 | 추론/분석 전문 |
| GPT-4o API | 창의적 답변 | 창작/브레인스토밍 |
| Gemini API (2.5 Pro) | 최신 정보 답변 | 뉴스/시사 |

**V1 축약 (LOCK-AP-05 정합)**: V1 은 Proposer 2개 + Aggregator 1개 = **총 3 agent** (LOCK-AT-014 V1=3). 가장 저렴한 조합 = Ollama + Gemini Flash + Claude Haiku(Aggregator).

### 4.2 Layer 2 — Aggregator (통합 답변)

STEP7-K L494~L497 원문 기능:
- 각 답변의 강점 추출
- 모순점 식별 + 해결
- 통합 답변 생성

**Aggregator 알고리즘** (Big-O: O(N × M) — N=proposer 수, M=평균 답변 토큰):

```python
def moa_aggregate(answers: list[ProposerAnswer], mode: MoAMode) -> AggregatorResult:
    # 1. 강점 추출
    strengths = []
    for a in answers:
        strengths.append(extract_unique_insights(a.content, peers=[x for x in answers if x != a]))
    # 2. 모순 식별
    contradictions = find_contradictions(answers)
    # 3. 모순 해결 (가장 강력한 LLM = Aggregator 자체 판단)
    resolved = [resolve_contradiction(c, peers=answers) for c in contradictions]
    # 4. 합의 점수
    agreement = compute_agreement(answers, resolved)
    # 5. 최종 통합 답변 생성
    final = synthesize(strengths, resolved, agreement)
    # 6. 비용 집계 — LOCK-AP-09
    total_cost = sum(a.cost_krw for a in answers) + aggregator_cost_krw(final)
    if total_cost > mode.budget_limit_krw:
        return AggregatorResult(
            final_answer="[COST_GATE_BLOCKED]",
            contributing_strengths=[], contradictions_found=[], contradictions_resolved=[],
            agreement_score=agreement, total_cost_krw=total_cost,
            hitl_required=True,
        )
    # 7. LOCK-AP-10 HITL 체크
    hitl = agreement < 0.5
    return AggregatorResult(
        final_answer=final, contributing_strengths=strengths,
        contradictions_found=contradictions, contradictions_resolved=resolved,
        agreement_score=agreement, total_cost_krw=total_cost, hitl_required=hitl,
    )
```

### 4.3 Layer 3 — 최종 통합 (V3 영역)

STEP7-K L485 "Layer 3: 최종 통합 답변 (가장 강력한 LLM)". V2 범위에서는 **Aggregator 가 직접 최종 답변을 내므로 Layer 3 생략**. V3 에서는 복수 Aggregator → Meta-Aggregator 계층으로 확장 가능(K-047 자기진화 안전 가드레일과 결합).

---

## §5. 비용 최적화 매트릭스 (STEP7-K L505~L511 원문 기반)

| 질문 유형 | 기본 모드 | 활성 조건 | 예상 비용 (KRW) | LOCK-AP-09 체크 |
|----------|---------|---------|-----------------|-----------------|
| 일반 질문 | `single` | 기본 | 200~800 | V1 ₩40K 여유 |
| 중요 질문 | `moa_2_model` | 사용자 "확실한 답변" 언급 또는 critical_decision 태그 | 단일 × 3~4 | V2 ₩93K 내 |
| 고위험 결정 | `moa_full_4_model` | 금융/투자 결정 + Permission L5 | 단일 × 8~10 | V2 ₩93K + cost gate 필수 |

**자동 MoA 트리거**:
- 사용자 메시지에 "확실", "중요", "리스크" 키워드 → `moa_2_model`
- Permission L5 작업 요청 → `moa_full_4_model` 강제
- 디폴트 → `single`

---

## §6. 활용 시나리오 (STEP7-K L499~L503 원문 4개)

| 시나리오 | MoA 기여 | 위험 완화 |
|----------|---------|---------|
| 투자 분석 (Quant Node) | 다수 LLM 합의 → 신뢰도↑ | 편향 리스크 감소 |
| 코드 리뷰 (Dev Node) | 다각도 검토 | 보안/버그 누락 확률↓ |
| 연구 (Research Node) | 다양한 관점 수집 | 단일 모델 hallucination 완화 |
| 중요 의사결정 | 편향 감소 | LOCK-AP-10 confidence 상승 |

---

## §7. LOCK 매핑 (5필드 분리 인용)

| LOCK ID | 항목 | 원본 문서 | 값 | 재정의 | 본 문서 적용 |
|---------|------|----------|-----|-------|-------------|
| LOCK-AP-01 | 프로토콜 메시지 포맷 | STEP7-K, D2.0-05 | VamosMessage 스키마 (id, type, source, target, content, metadata) | 금지 | Proposer ↔ Aggregator 통신 전수 VamosMessage |
| LOCK-AP-05 | Agent Teams V1 제한 | Part2 §6.7 LOCK-AT-014 | Lead + max 2 Sub-Agent | 금지 | V1 MoA = Proposer 2 + Aggregator 1 = 총 3 |
| LOCK-AP-07 | 인터롭 규격 | STEP7-K | A2A + MCP 양방향 지원 필수 | 금지 | Claude/GPT-4o/Gemini 호출 시 MCP Tool Registry 경유 |
| LOCK-AP-09 | 비용 상한 | Part2 §비용 + 가이드 부록 D (STEP7-H 참조) | V1: ₩40K, V2: ₩93K, V3: ₩266K | 금지 | §4.2 moa_aggregate() 6단계 cost gate |
| LOCK-AP-10 | Confidence 임계값 | DEFINED-HERE (06_autonomy-safety/guardrail_rules.md 정본) | HITL 트리거 < 50% | 금지 | §4.2 agreement < 0.5 → hitl_required=True |
| LOCK-AT-014 | Agent Team size | **6-3 AUTHORITY_CHAIN.md L67 (SPEC S7-A-008) — 본 도메인은 read-only 참조자** | **V1=3 / V2=10 / V3=50+** | 금지 (6-3 정본) | §2.3 verbatim 교차 정합 — V1 MoA 3-agent 상한 |

---

## §8. Phase별 복구/다운그레이드 흐름

```
Phase 1 (Proposer 호출 실패) → 폴백 Ollama 로컬 → confidence -0.05
Phase 2 (Aggregator 모순 해결 실패) → 단일 proposer 답변으로 다운그레이드 → confidence -0.20
Phase 3 (agreement < 0.5) → LOCK-AP-10 HITL → I-19 에스컬레이션
Phase 4 (total_cost > V2 ₩93K) → LOCK-AP-09 Cost Gate → [COST_GATE_BLOCKED]
```

confidence penalty:
- proposer 1개 타임아웃 → -0.05
- 모순 2개 이상 미해결 → -0.20
- 비용 초과 → 즉시 차단 (에스컬레이션 아님)
- agreement < 0.3 → -0.30 + 즉시 HITL

---

## §9. 에스컬레이션 페이로드 (I-20 경유)

```python
class MoAEscalation(BaseModel):
    source_engine: Literal["moa_aggregator"] = "moa_aggregator"
    error_code: Literal["HITL_AGREEMENT_LOW", "COST_GATE_BLOCKED", "PROPOSER_ALL_FAILED", "LOCK_VIOLATION"]
    original_request: VamosMessage
    partial_result: Optional[AggregatorResult]
    retry_count: int
    proposer_answers: list[ProposerAnswer]
    mode: MoAMode
    trace_id: str
    timestamp: datetime
```

---

## §10. 로깅 포맷 (R-01-7 structured JSON)

```json
{
  "trace_id": "...",
  "error": {"code": "HITL_AGREEMENT_LOW", "agreement_score": 0.42},
  "context": {
    "mode": "moa_2_model",
    "proposers": ["ollama_local_llama4", "gemini_25_pro"],
    "aggregator": "claude_haiku_45",
    "lock_at_014": "V1=3 (Lead 1 + Sub 2)",
    "total_cost_krw": 18500
  },
  "recovery": {"action": "hitl_escalation", "route": "I-20", "reason": "agreement_below_threshold"}
}
```

---

## §11. Phase 3 테스트 시나리오 (10건)

1. **V1 2-model MoA 정상**: Proposer=Ollama+Gemini, Aggregator=Claude Haiku → agreement 0.85 → `completed`.
2. **모순 해결 성공**: Ollama vs GPT-4o 결론 충돌 → Aggregator 3안 분석 후 결정 → `contradictions_resolved=3`.
3. **agreement 하락 HITL**: Proposer 답변 편차 커서 agreement 0.42 → I-20 에스컬레이션.
4. **비용 초과 차단**: full MoA 4-model 호출 → 누적 ₩95K → `COST_GATE_BLOCKED`.
5. **Proposer 1개 타임아웃**: GPT-4o 5초 초과 → 폴백 Ollama → confidence -0.05.
6. **Proposer 전체 실패**: 3개 proposer 전부 API 429 → `PROPOSER_ALL_FAILED` → Ollama 로컬만 단일 응답.
7. **LOCK-AT-014 위반 시도 (V2 확장 전)**: Proposer=4 요청 → `[VIOLATION:LOCK-AT-014 V1=3 exceeded]` → 거부.
8. **Permission L5 강제 full MoA**: 금융 주문 요청 → `moa_full_4_model` 강제 → 사용자 확인 요청 + Aggregator 최종 결정.
9. **Cache Hit (K-028 Tool Use 최적화)**: 동일 질문 재호출 → Layer 1 캐시 활용 → cost ₩0.
10. **Magentic-One Orchestrator 호출**: `magentic_one.md §5` Orchestrator 가 `moa_aggregate()` 호출 경로 → Sub2 slot 에 MoA 배치 시 LOCK-AT-014 위반 여부(Orchestrator + Sub1 + MoA(3) = 5 이상) 사전 차단.
11. **message_format.md §2.5 alias**: Proposer 가 STEP7-K 원문 type="request" → canonical "task" 변환 → CFL-AP-007 정책 보존 확인.
12. **VBS-12 3-4 측정 재료**: 동일 질문 single vs MoA_2 vs MoA_4 품질 비교 → `tool_memory_benchmark.md §4` VBS-12 3-4 입력.

---

## §12. 세션 간 인터페이스 cross-check

| 상대 산출물 | 인터페이스 | 일치 여부 |
|------------|-----------|-----------|
| langgraph_adapter.md §3 | VamosMessage, VamosPhase, AdapterResult 공통 타입 | ✅ import 경로 일치 |
| magentic_one.md §5 Orchestrator 루프 | `call_agent(agent_id, step, progress)` 의 agent_id 가 MoA Aggregator 일 때 LOCK-AT-014 중첩 방지 | ✅ §11 시나리오 10 검증 |
| tool_memory_benchmark.md §4 VBS-12 3-4 | MoA 품질 향상률 지표 | ✅ 단일 vs 다중 에이전트 품질 비교 입력 |
| 02_service-integration/llm_gateway.md §§ Proposer Pool | Proposer 4개 LLM Gateway 경유 호출 | ✅ smart routing matrix 활용 |
| 03_data-exchange/message_format.md §2.5 alias 표 | canonical type=`task/result/event/control` 준수 (CFL-AP-007) | ✅ CFL-AP-007 RESOLVED 보존 |
| 03_data-exchange/message_format.md §2 LOCK-AP-01 | VamosMessage 6필드 외 필드 추가 금지 | ✅ Proposer 응답은 content 필드 내 payload |
| **6-3 AUTHORITY_CHAIN.md L67 LOCK-AT-014** | **V1=3 / V2=10 / V3=50+ verbatim** | **✅ §2.3 verbatim 전수 인용** |
| 06_autonomy-safety/guardrail_rules.md LOCK-AP-10 | confidence < 0.5 HITL | ✅ §4.2 agreement_score 연동 |

---

## §13. 검증 자가 체크리스트

- [x] §1 교차 참조 블록 포함 (6-3 LOCK-AT-014 row 명시)
- [x] §2.3 LOCK-AP-05 × LOCK-AT-014 5필드 분리 인용 (verbatim)
- [x] §3 공통 자료 구조 langgraph_adapter.md §3 참조 (중복 정의 금지)
- [x] §4 STEP7-K L479~L512 원문 line refs verbatim (L488~L492 Proposer 4개, L494~L497 Aggregator, L499~L503 시나리오, L505~L511 비용)
- [x] §7 LOCK 매핑 5필드 (ID × 항목 × 원본 × 값 × 재정의)
- [x] Phase 3 테스트 시나리오 ≥ 10건 (§11: 12건)
- [x] 에스컬레이션 페이로드 Python class (§9)
- [x] 로깅 포맷 structured JSON 중첩 3-block (§10)
- [x] V2-Phase 2 헤더 태그
- [x] CFL-AP-007 alias 매핑 표 보존 (§11 시나리오 11, §12)
- [x] FABRICATION 10종 census 0 hits
- [x] R6 준수 (What+How 전용)

---

*정본 소유: #13 Agent-Protocol-Interoperability / 01_framework-adapters*
*V2-Phase 2 최초 작성: 2026-04-22 (STAGE 7 STEP_B #2a, 6-3 LOCK-AT-014 cross-reference 강제)*
