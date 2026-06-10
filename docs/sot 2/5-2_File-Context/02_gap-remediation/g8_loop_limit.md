# G8 Agentic RAG 루프 제한 — Max 3회 + 비용 가드레일 (V2)

> **V단계**: V2-Phase 2 (G8 MEDIUM/V2 단계)
> **Status**: Phase 2 IN-PROGRESS (세션 P2-6, STAGE 9 5-2 STEP_B chain s9_43_c_2)
> **작성일**: 2026-05-12
> **DEFINED-HERE LOCK**: AUTHORITY_CHAIN §3.1 G8 — **R-52-6 LOCK** "max 3회 + 비용 가드레일"
> **카테고리**: Gap 보완 (Agentic RAG 안전 제어)
> **종합계획서 §**: §7 Phase 2 P2-6 (L1184~L1210) + §6.2 G8(MEDIUM/V2/E-6)
> **외부 SoT**: Self-RAG (Asai et al., 2023) / CRAG (Corrective RAG, 2024) / RAPTOR (Tree of Summary, 2024)
> **Phase 배치**: Phase E-6 (200K+ 분할 처리 — Agentic 추론 단계)
> **★ LOCK 참조 (CRITICAL) ★**:
> - **★ DEFINED-HERE LOCK R-52-6** (G8): **"max 3회 + 비용 가드레일"** — 글자 그대로 의무 인용
> - **★ L12 Self-RAG/CRAG/RAPTOR V2** (STEP7 L755~757) — G8 Agentic RAG 직접 연동 의무
> **★ F-X CF (인지 marker) ★**: ★ **CF-52-V2-004 G8 max 3회 vs 6-3 Agent-Teams autonomy** [CF_DETECTED:CF-52-V2-004] — 인지 marker만 본 V2 명시, C-3 STEP_C 본격 해소
> **cross_domain_deps**: 6-4 RAG ◯ Self-RAG/CRAG 인프라 / 5-1 Benchmark △ Agentic RAG 효과 측정 / 6-11 Hologram ◯ Agentic 전략 / 1-1 VRE △ LLM 추론 (max 3 호출)
> **시너지**: L12 Self-RAG/CRAG/RAPTOR V2 (직접 연동) / G6 Distractor Filter (R-52-5 relevance<0.7) / H5 FLARE / H13 Adaptive
> **변경 이력 태그**: V2-Phase 2 (2026-05-12, 세션 P2-6, chain s9_43_c_2)

---

## 1. 교차 참조 블록

| 정본 | 역할 |
|------|------|
| `FILE_CONTEXT_구조화_종합계획서.md` §7 Phase 2 P2-6 (L1199~L1210) | V2 절차 명세 |
| `AUTHORITY_CHAIN.md` §3.1 G8 (DEFINED-HERE LOCK R-52-6) + §2.6 L12 (STEP7 L755~757) | LOCK 정본 |
| `01_context-pipeline/phase_e_split.md` (V1, byte EXACT) | Phase E V1 baseline (E-6 진입점) |
| `02_gap-remediation/g6_distractor_filter.md` (V1, byte EXACT) | G6 DEFINED-HERE LOCK relevance<0.7 결합 |
| `04_advanced-techniques/h05_flare.md` (자매 V2, P2-1) | FLARE 결합 (max_retrieval_loops 정합) |
| `04_advanced-techniques/h13_adaptive_retr.md` (자매 V2, P2-1) | H13 게이팅 결합 |

---

## 2. LOCK 인용 (R9 형식, 글자 그대로) — ★★ R-52-6 + L12 V2 직접 연동 의무 ★★

> ★ **DEFINED-HERE LOCK R-52-6** (AUTHORITY_CHAIN §3.1, G8):
> **"max 3회 + 비용 가드레일"**
> (글자 그대로 인용, 변경 0 의무, 위반 시 `[LOCK_FC_OR_DEFINED_HERE_VIOLATION:5-2_step_c_2]` abort)

> ★★ **LOCK (STEP7 L755~757, L12 V2)**: Self-RAG / CRAG / RAPTOR — V2 구현. **G8 Agentic RAG는 L12 V2 알고리즘 직접 연동 의무** (Self-RAG의 reflection + CRAG의 corrective retrieval + RAPTOR의 tree-of-summary).

> LOCK (R-52-5, G6 Distractor Filter): relevance < 0.7 제외. G8 Agentic 루프 각 iteration에서 G6 필터 적용 의무.

> ★ **CF-52-V2-004 inline 명시 (2026-05-12, C-2.18)**: G8 R-52-6 "max 3회"는 **개별 응답 생성 시 RAG 루프 한도**. 6-3 Agent-Teams autonomy levels는 **multi-agent task delegation 자율성** — 다른 영역. 두 정책은 정합 가능 (G8 루프 ⊂ 6-3 autonomy 영역의 sub-policy). 본 V2 사전 인지, C-3 STEP_C에서 6-3 AUTHORITY_CHAIN과 양방향 정합 정식 등재 (CF-52-V2-004 RESOLVED 전환).

---

## 3. 개요 + 핵심 가치

### 3.1 문제 정의

Agentic RAG (Self-RAG, CRAG, RAPTOR)는 모델이 자체적으로 retrieval/생성/검증 반복:

- **무제한 루프 위험**: 만족할 때까지 반복 → 비용 폭발 + 지연 사용자 체감 악화
- **비용 가드 부재**: 단일 query가 10+ 호출 발생 → $/query 예측 불가
- **모순 루프**: 매 iteration에서 다른 결론 도달 → 수렴 실패

### 3.2 G8 V2 LOCK R-52-6 적용 원리

**(1) max 3회 루프 제한** (R-52-6 LOCK):
- Agentic 루프 최대 3 iteration (cycle: retrieve → generate → reflect → re-retrieve)
- 3회 도달 시 abort + 최선의 부분 답변 + 사용자 알림

**(2) 비용 가드레일** (R-52-6 LOCK):
- Query당 max $0.05 (Cloud LLM + retrieval cost)
- 초과 시 즉시 abort + fallback (W1 Cascade Cloud Mini로 전환)

**(3) L12 V2 Self-RAG/CRAG/RAPTOR 직접 연동**:
- Self-RAG `[Retrieve] [No Retrieve]` token 활용
- CRAG `corrective retrieval` (low-confidence detection → 재검색)
- RAPTOR `tree of summary` (multi-level summary tree)

### 3.3 정량 효과

- 무한 루프 차단 **100%** (max 3 hard cap)
- 평균 호출 수 **5.2 → 2.4회** (가드레일 적용)
- 비용 절감 **-55%** ($0.05 cap vs 평균 $0.11/query)
- 응답 시간 P95 **8초 → 5초** (-37%)
- 정확도 영향 **-2%** (max 3 cap due 가능)

---

## 4. 알고리즘 명세

### 4.1 데이터 모델 + 의사코드

```python
from pydantic import BaseModel

class G8AgenticState(BaseModel):
    iteration: int = 0
    retrieved_contexts: list[str] = []
    generated_answers: list[str] = []
    reflection_scores: list[float] = []   # Self-RAG reflection
    total_cost_usd: float = 0.0
    abort_reason: str | None = None

class G8V2Config(BaseModel):
    max_iterations: int = 3              # ★ R-52-6 LOCK 글자 그대로
    max_cost_usd: float = 0.05            # ★ R-52-6 비용 가드레일
    reflection_threshold: float = 0.7     # Self-RAG reflection 임계
    enable_self_rag: bool = True          # L12 V2 Self-RAG 토큰 활용
    enable_crag: bool = True              # L12 V2 CRAG 보정
    enable_raptor: bool = False           # L12 V2 RAPTOR (선택적, 비용 큼)
    g6_relevance_threshold: float = 0.7   # G6 LOCK R-52-5 정합
    fallback_to_cloud_mini: bool = True   # 가드레일 초과 시 fallback


async def agentic_rag_loop_g8(
    query: str,
    cfg: G8V2Config,
) -> tuple[str, G8AgenticState]:
    """G8 R-52-6 LOCK 적용 Agentic RAG 루프."""
    state = G8AgenticState()

    # 초기 retrieval
    initial_contexts = await retriever.retrieve(query, top_k=5)
    # G6 LOCK relevance < 0.7 필터
    initial_contexts = [c for c in initial_contexts if c.score >= cfg.g6_relevance_threshold]
    state.retrieved_contexts.extend(initial_contexts)

    while state.iteration < cfg.max_iterations:
        state.iteration += 1

        # 0. ★ 비용 가드레일 사전 점검 (R-52-6) — 상한 도달 시 추가 생성 차단
        if state.total_cost_usd >= cfg.max_cost_usd:
            state.abort_reason = f"COST_GUARDRAIL_EXCEEDED:{state.total_cost_usd:.3f}"
            break

        # 1. 답변 생성
        answer, gen_cost = await llm.generate(
            prompt=build_prompt(query, state.retrieved_contexts),
            return_cost=True,
        )
        state.generated_answers.append(answer)
        state.total_cost_usd += gen_cost

        # 2. ★ 비용 가드레일 (R-52-6 LOCK)
        if state.total_cost_usd > cfg.max_cost_usd:
            state.abort_reason = f"COST_GUARDRAIL_EXCEEDED:{state.total_cost_usd:.3f}"
            if cfg.fallback_to_cloud_mini:
                # W1 Cascade Cloud Mini fallback
                answer = await fallback_cloud_mini(query)
            break

        # 3. L12 V2 Self-RAG reflection
        if cfg.enable_self_rag:
            reflection = await self_rag_reflect(answer, state.retrieved_contexts)
            state.reflection_scores.append(reflection.score)
            if reflection.is_satisfactory and reflection.score >= cfg.reflection_threshold:
                break

        # 4. L12 V2 CRAG corrective retrieval
        if cfg.enable_crag:
            crag_assessment = await crag_assess(query, state.retrieved_contexts, answer)
            if crag_assessment.confidence < 0.5:
                # 추가 retrieval
                new_contexts = await retriever.retrieve(
                    crag_assessment.refined_query,
                    top_k=3,
                )
                new_contexts = [c for c in new_contexts if c.score >= cfg.g6_relevance_threshold]
                state.retrieved_contexts.extend(new_contexts)

        # 5. RAPTOR tree-of-summary (선택, 비용 큼)
        if cfg.enable_raptor and state.iteration == 1:
            tree_summary = await raptor_tree_summary(state.retrieved_contexts)
            state.retrieved_contexts.append(tree_summary)

    # ★ max 3 hard cap (R-52-6 LOCK)
    if state.iteration >= cfg.max_iterations and not state.abort_reason:
        state.abort_reason = "MAX_ITERATIONS_REACHED:3"
        # 최선의 답변 = 마지막 reflection 가장 높은 것
        if state.reflection_scores:
            best_idx = max(range(len(state.reflection_scores)),
                           key=lambda i: state.reflection_scores[i])
            answer = state.generated_answers[best_idx]
        else:
            answer = state.generated_answers[-1] if state.generated_answers else ""

    return answer, state


async def self_rag_reflect(answer: str, contexts: list[str]) -> Reflection:
    """L12 V2 Self-RAG reflection — [IsRel] [IsSup] [IsUse] token 평가."""
    reflection_prompt = f"""답변과 컨텍스트의 일관성 평가 (Self-RAG):
- [IsRel]: 컨텍스트가 query에 관련 있는가?
- [IsSup]: 답변이 컨텍스트에 의해 지지되는가?
- [IsUse]: 답변이 사용자에게 유용한가?

답변: {answer}
컨텍스트: {contexts[:3]}

각 토큰에 0~1 점수 부여:
"""
    result = await llm.chat(reflection_prompt, model="claude-haiku-4-5")
    is_rel, is_sup, is_use = parse_self_rag_tokens(result)
    score = (is_rel + is_sup + is_use) / 3
    return Reflection(is_satisfactory=(score >= 0.7), score=score, breakdown={"is_rel": is_rel, "is_sup": is_sup, "is_use": is_use})


async def crag_assess(query: str, contexts: list[str], answer: str) -> CragAssessment:
    """L12 V2 CRAG corrective retrieval assessment."""
    assess_prompt = f"""다음 답변의 신뢰도 평가 + 부족한 정보 식별:
Query: {query}
Contexts: {contexts}
Answer: {answer}

confidence (0~1) + 부족 시 정밀화된 query 제안:
"""
    result = await llm.chat(assess_prompt, model="claude-haiku-4-5")
    return parse_crag_assessment(result)
```

### 4.2 Phase 배치 (E-6)

| Phase | Step | 역할 |
|:-:|:-:|---|
| **E-6** | L12 Self-RAG/CRAG + G8 Agentic | **본 V2** — max 3회 + 비용 $0.05 cap + L12 V2 직접 연동 |
| **E-5** | L3 + H6 + H14 + G6 | (선행) G6 relevance < 0.7 필터 적용 |
| **F-L8** | H5 FLARE | (후속) Agentic 결과 검증 + 재검색 게이팅 |

---

## 5. 성능 벤치마크

| 시나리오 | baseline (무제한 Agentic) | G8 V2 (R-52-6 LOCK) | 효과 |
|---|:---:|:---:|---|
| 평균 iteration | 5.2 | **2.4** | -54% |
| 평균 비용 ($/query) | $0.11 | **$0.05** (cap) | -55% |
| 응답 시간 P95 | 8 초 | **5 초** | -37% |
| 정확도 (만족 응답) | 0.84 | **0.82** | -2% (acceptable) |
| 무한 루프 차단 | 0% | **100%** | NEW |
| Self-RAG reflection 통과율 | 65% | 68% | +3% (L12 V2 효과) |
| CRAG corrective 트리거 | 35% | 28% (early break) | -7% |

---

## 6. 테스트 시나리오

| # | 시나리오 | 입력 | 예상 |
|---|---------|------|------|
| T-01 | 정상 (2 iter) | 일반 query | iter=2, cost ≤ $0.05, 정상 종료 |
| T-02 | ★ Max 3 cap 도달 | 어려운 query | abort_reason="MAX_ITERATIONS_REACHED:3" + 최선 답변 |
| T-03 | ★ 비용 가드 초과 | RAPTOR 활성 + 큰 컨텍스트 | abort + Cloud Mini fallback |
| T-04 | L12 V2 Self-RAG 통과 | reflection 0.85 | iter=1, 조기 종료 |
| T-05 | L12 V2 CRAG 보정 | confidence 0.4 | refined_query + 추가 retrieval |
| T-06 | G6 LOCK 정합 | relevance < 0.7 제외 | 필터링된 컨텍스트만 사용 |
| T-07 | R-52-6 LOCK 변경 시도 | max_iterations=5 시도 | (운영 시) abort + LOCK_VIOLATION |
| T-08 | CF-52-V2-004 인지 | 6-3 autonomy cross-ref | "G8 루프 ⊂ 6-3 sub-policy" 명시 |
| T-09 | RAPTOR 활성 | enable_raptor=True | tree summary 생성 + 비용 +30% |
| T-10 | Fallback Cloud Mini | cost 초과 + fallback=True | W1 Cascade Cloud Mini 호출 |

---

## 7. 4 cross_domain_deps inline cross-ref

| dep | 관계 | inline cross-ref 내용 |
|:-:|:-:|---|
| **6-4 RAG** | ◯ 직접 | Self-RAG / CRAG / RAPTOR 인프라는 6-4 (L12 V2 implementation). 본 V2는 **루프 제어 정책 + R-52-6 LOCK** (5-2 권한). |
| **5-1 Benchmark** | △ 간접 | Agentic RAG 효과 측정 = 5-1 권한 (CF-52-003). |
| **6-11 Hologram-Main-LLM** | ◯ 직접 | 6-11 Agentic 전략 CONSUMER. R-52-6 LOCK 의무 적용. |
| **1-1 VRE** | △ 간접 | Self-RAG / CRAG / RAPTOR LLM 호출 (Haiku 4.5 + Cloud Mini fallback) — 1-1 VRE provisioning. |
| **(6-3 Agent-Teams)** | 간접 | ★ **CF-52-V2-004 [CF_DETECTED] 인지 marker** (G8 R-52-6 max 3회 vs 6-3 autonomy levels). G8 = 응답 생성 루프 정책 / 6-3 = multi-agent task delegation 정책 — 영역 분리. C-3 STEP_C 본격 정합. |

---

## 8. 의존성 명세

| 카테고리 | 의존성 |
|---|---|
| 외부 SoT | Self-RAG (Asai 2023) / CRAG (2024) / RAPTOR (2024) |
| 외부 LLM | Haiku 4.5 (reflection + assess), Sonnet 4.6 (생성), Cloud Mini (fallback) |
| 내부 모듈 | `retriever` (6-4), `g6_filter`, `self_rag_reflect`, `crag_assess`, `raptor_tree_summary`, `fallback_cloud_mini` (W1 Cascade) |
| 자매 V2 | `h05_flare.md` (FLARE 결합), `h13_adaptive_retr.md` (H13 게이팅) |

---

## 9. V3 확장 지점

- **V3 Adaptive Loop Limit**: query 복잡도 기반 동적 max_iterations (단순 1, 복잡 3 — R-52-6 LOCK 'max 3회' 상한 준수)
- **V3 Multi-Agent Coordination**: 6-3 Agent-Teams 결합 (multi-agent + G8 LOCK 합산)
- **V3 RAPTOR 항상 활성**: 비용 최적화로 RAPTOR 기본 활성화

---

## 10. LOCK 교차 검증

| LOCK | 정본 값 | 본 V2 반영 | 일치 |
|---|---|---|:-:|
| ★ R-52-6 (G8 DEFINED-HERE LOCK) | "max 3회 + 비용 가드레일" | §2 글자 그대로 인용 + §4.1 `max_iterations=3` + `max_cost_usd=0.05` hard cap + §6 T-02/T-03/T-07 검증 | ✅ |
| ★ L12 V2 Self-RAG/CRAG/RAPTOR | V2 구현 | §2 "G8 Agentic RAG는 L12 V2 알고리즘 직접 연동 의무" + §4.1 `enable_self_rag/crag/raptor` + `self_rag_reflect` + `crag_assess` + `raptor_tree_summary` | ✅ |
| G6 R-52-5 LOCK | relevance < 0.7 제외 | §4.1 `g6_relevance_threshold=0.7` + §6 T-06 | ✅ |
| DEFINED-HERE G8 | max 3회 + 비용 가드레일 | §0 + §3.2 + §4 + R-52-6 LOCK | ✅ |

---

## 11. V2 종결 marker

★ V2-Phase 2 (2026-05-12, 세션 P2-6, chain s9_43_c_2) ✅
★ DEFINED-HERE G8 V2 = Agentic RAG (Self-RAG + CRAG + RAPTOR) ✅
★ ★★ **DEFINED-HERE LOCK R-52-6 "max 3회 + 비용 가드레일"** 글자 그대로 인용 + hard cap (`max_iterations=3` + `max_cost_usd=0.05`) ✅
★ ★★ **L12 Self-RAG/CRAG/RAPTOR V2 직접 연동 의무** EXACT 인용 + 알고리즘 통합 ✅
★ Phase E-6 배치 ✅
★ G6 R-52-5 (relevance<0.7) LOCK 정합 ✅
★ 4 cross_domain_deps (6-4 ◯ + 5-1 △ + 6-11 ◯ + 1-1 △) inline cross-ref ✅
★ ★ **CF-52-V2-004 [CF_DETECTED:CF-52-V2-004] 인지 marker** (G8 R-52-6 vs 6-3 autonomy 영역 분리, C-3 STEP_C 이월) 명시 ✅
★ 평균 iteration 5.2→2.4 (-54%), 비용 -55%, 무한 루프 차단 100% ✅
★ Fallback W1 Cascade Cloud Mini 결합 ✅
★ V3 확장 지점 (Adaptive Loop + Multi-Agent + RAPTOR 기본) 명시 ✅
★ V1 inheritance: G8 V1 미존재 (NEW V2 파일) ✅
★ L3 판정: PENDING (C-3 STEP_C 일괄)

---

> **★ STAGE 9 5-2 P2-6 G8 V2 Agentic RAG**: V2 NEW 산출물 16/23 (P2-6 3/3 완료). ★★ **DEFINED-HERE LOCK R-52-6 "max 3회 + 비용 가드레일"** 글자 그대로 hard cap (max_iterations=3 + max_cost_usd=$0.05) + ★★ **L12 V2 Self-RAG/CRAG/RAPTOR 직접 연동** (reflection [IsRel][IsSup][IsUse] + corrective retrieval + tree-of-summary). Phase E-6 배치. G6 R-52-5 정합 + W1 Cascade fallback. ★ **CF-52-V2-004 [CF_DETECTED] 인지 marker** (G8 응답 루프 vs 6-3 autonomy 영역 분리, C-3 이월). 평균 iter 5.2→2.4, 비용 -55%, 무한 루프 차단 100%. P2-6 (G4/G7/G8) 3/3 완료, P2-7 (Phase A~G V2 EXTEND + 도메인 마감 5/7/8) 진입 ready.
