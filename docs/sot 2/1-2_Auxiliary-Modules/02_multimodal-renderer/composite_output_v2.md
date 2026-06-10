# I-13 Multimodal Renderer — 복합 출력 구성 V2 Enhanced (L3 보강)

> **V단계**: V2-Phase 2
> **Status**: APPROVED (Phase 4 ✅ 완료, 2026-05-23, V2 strict L3 PASS production-ready 정본 승급, Phase 3 V-17 PASS inheritance)
> **Last-reviewed**: 2026-05-23 (Phase 4 production promotion)
> **ReadOnly**: TRUE (production 승급 후 immutable, 변경 시 일시 해제→fix→복원 EXACT 패턴 + audit log)
> **작성일**: 2026-05-10
> **V1 정본**: `composite_output.md` (29 lines, byte EXACT)
> **모듈**: I-13 (CORE, Action) — composite_output 핵심 (DAG 스케줄링 정본)
> **LOCK 참조**: LOCK-AX-01, LOCK-AX-11, LOCK-AX-12, LOCK-AX-13
> **L3 판정**: PASS (V-17 row content, 9/9 또는 8/9, 2026-05-14)
> **변경 이력 태그**: `V2-Phase 2` (2026-05-10, 세션 2-2)
> **종합계획서 §**: §7 Phase 2 L1431~L1482 (2-2 핵심 — DAG 스케줄링 정본)
> **계약 cross-ref**: C-08 (I-5 → I-13 render_composite), C-09 (I-13 → I-20)
> **F-06 이월**: composite_output → 스케줄러→I-14 out-of-scope 호출 경로 명시 (§7 2-2 절차 9)
> **횡단**: 6-2 (composite 결과 응답에 PII 통합 점검)

---

## 1. 교차 참조 블록

| 정본 | 역할 |
|------|------|
| `composite_output.md` (V1, 29 lines, byte EXACT) | V1 정본 (DAG 스케줄링 ASCII) |
| `renderer_interface_v2.md` | BaseRenderer ABC |
| `text_renderer_v2.md` ~ `code_renderer_v2.md` (자매 V2, 7 sub-renderers) | 병렬 실행 대상 |
| `quality_validation_v2.md` | 합성 결과 무결성 |
| `06_mapping/interface_contracts.md` C-08 (render_composite) | 호출 계약 |
| `06_mapping/module_dependency_graph.md` v1.1 | 19 엣지 출처 |
| `6-2/01_ai-code-security/pii_regex_masking.md` | 통합 응답 PII |

---

## 2. LOCK 인용 (R9 형식)

> LOCK (D2.0-01 §5.6, LOCK-AX-01): I-13 = CORE

> LOCK (D2.0-02 §2.1, LOCK-AX-12): composite_output = Action (Standard 5-stage)

> LOCK (D2.0-02 §2.2, LOCK-AX-13): 상태 전이 S0~S8, S3 Decision Lock 불변 — composite는 S4~S5 단계 산출

> LOCK (V1 §3 ASCII): RenderPlan → DAG → 병렬 → 레이아웃 → 품질검증 → I-20

---

## 3. V1 → V2 승급 개요

### 3.1 V1 정본 byte EXACT 보존
- V1: `composite_output.md` (29 lines, V1 §3 RenderPlan→DAG ASCII 정본)
- V1 변경 0

### 3.2 V2 보강 요소 (§13.1 L3 + §7 2-2 절차 2/8/9)

| 요소 | 보강 | 위치 |
|------|------|------|
| **E1** | composite_output 목적 (DAG 합성 단일 정본) | §4.1 |
| **E2** | DAG topological sort + 병렬 asyncio.gather + 레이아웃 의사코드 | §4.2 |
| **E3** | CompositeRenderContent / CompositeRenderedOutput | §4.2 |
| **E5** | DAGCycleError, partial_failure, layout 충돌 | §4.3 |
| **E6** | composite P95 3000ms (sub-renderer P95 합산) | §4.4 |
| **E7** | chart+table+text 합성 / cycle / partial fail | §4.5 |
| **F-06** | out-of-scope 호출 경로 명시 (스케줄러→I-14 distill) | §4.7 |
| **E9** | asyncio, networkx (DAG 검증) | §4.6 |

---

## 4. V2 본문 (L3 보강)

### 4.1 E1 — 목적 및 역할

composite_output은 I-13의 **다모달 합성 핵심 sub-renderer**. I-5 Decision Engine이 결정한 RenderPlan (예: "차트 + 표 + 설명 텍스트") 을 (1) 의존성 기반 DAG 구성, (2) 독립 노드 병렬 실행 (asyncio.gather), (3) 레이아웃 합성 (순서/배치/grid), (4) 품질 검증 (`quality_validation_v2`), (5) I-20 OutputComposer 인계의 5단계로 처리. V1/V2 활성.

해결 문제:
1. **다모달 응답 통합** — LLM이 "차트로 매출 추이 + 표로 상세 + 설명" 같이 복합 요청 시 단일 응답 봉투에 통합.
2. **병렬 처리 비용 절감** — 독립 sub-renderer 병렬 실행으로 P95 50% 감소.
3. **DAG 무결성 보장** — 사이클 검출 + 의존 순서 보장.
4. **부분 실패 회복** — 1 sub-renderer 실패 시 fallback (예: 차트 실패 → 표만).

### 4.2 E2 + E3 — 의사코드 + 모델

```python
class CompositeRenderItem(BaseModel):
    item_id: str  # "chart_1", "table_2"
    render_type: Literal["text", "image", "audio", "chart", "diagram", "table", "code"]
    content: dict  # render_type별 페이로드
    depends_on: list[str] = []  # item_id 의존성 (DAG)

class CompositeRenderContent(BaseModel):
    items: list[CompositeRenderItem]
    layout: Literal["sequential", "grid", "tabs"] = "sequential"
    grid_cols: int = 2  # layout=grid 시
    title: Optional[str] = None

class CompositeRenderedOutput(BaseModel):
    items: list[RenderedOutput]  # 각 sub-renderer 결과
    layout_html: str  # 레이아웃 합성된 최종 HTML
    failed_items: list[str]  # partial_failure 시 실패한 item_id 목록

async def render_composite(content: CompositeRenderContent) -> RenderedOutput:
    # 0. grid_cols 검증 (AUX-E-RENDER-023: <1 또는 >5)
    if content.layout == "grid" and not 1 <= content.grid_cols <= 5:
        raise AuxError("AUX-E-RENDER-023", "grid_cols 무효 (<1 or >5)")

    # 1. DAG 구성 + 사이클 검출
    G = networkx.DiGraph()
    for item in content.items:
        G.add_node(item.item_id)
        for dep in item.depends_on:
            G.add_edge(dep, item.item_id)
    if not networkx.is_directed_acyclic_graph(G):
        raise AuxError("AUX-E-RENDER-004", "DAGCycleError")

    # 2. Topological sort + 레이어별 병렬 실행
    layers = list(networkx.topological_generations(G))
    results: dict[str, RenderedOutput] = {}
    failed: list[str] = []

    for layer in layers:
        # 한 레이어 내 노드들은 모두 의존성이 해소된 상태 → 병렬 가능
        tasks = []
        for item_id in layer:
            item = next(it for it in content.items if it.item_id == item_id)
            renderer = registry[item.render_type]
            tasks.append(renderer.render(_to_render_content(item.render_type, item.content)))

        # asyncio.gather with return_exceptions for partial_failure
        layer_results = await asyncio.gather(*tasks, return_exceptions=True)
        for item_id, res in zip(layer, layer_results):
            if isinstance(res, Exception):
                failed.append(item_id)
                results[item_id] = _fallback_render(item_id)  # placeholder "이 항목은 렌더 실패"
            else:
                results[item_id] = res

    # 3. 레이아웃 합성 (HTML 결합)
    if content.layout == "sequential":
        layout_html = "\n".join(_render_html(r) for r in results.values())
    elif content.layout == "grid":
        layout_html = _grid_layout(results, cols=content.grid_cols)
    else:  # tabs
        layout_html = _tabs_layout(results)

    if content.title:
        layout_html = f"<h2>{html.escape(content.title)}</h2>\n{layout_html}"

    # 4. 6-2 PII 통합 점검 (HTML 본문 마스킹은 각 sub-renderer가 이미 적용 → 중복 검출만)
    _verify_no_pii_in_html(layout_html)  # raise AUX-E-PII-002 if leak

    # 5. 합성 응답
    composite_artifact = layout_html.encode()
    return RenderedOutput(
        render_type="composite",
        artifact_inline=composite_artifact if len(composite_artifact) <= 1_000_000 else None,
        artifact_url=_upload_cdn(composite_artifact) if len(composite_artifact) > 1_000_000 else None,
        mime_type="text/html",
        bytes_size=len(composite_artifact),
        metadata={
            "engine": "composite",
            "layout": content.layout,
            "item_count": len(content.items),
            "failed_items": failed,
            "dag_layers": len(layers),
        },
        quality_check=await quality_validator.validate_composite(results, failed),
    )
```

### 4.3 E5 — 에러 핸들링

| error_code | 설명 | recoverable | 처리 |
|-----------|------|:-----------:|------|
| `AUX-E-RENDER-004` | DAGCycleError | NO | 거부 + I-5 fallback (sequential 강제) |
| `AUX-E-RENDER-022` | partial_failure (≥1 sub-renderer 실패) | YES | placeholder + audit |
| `AUX-E-RENDER-023` | grid_cols 무효 (<1 or >5) | YES | sequential fallback |
| `AUX-E-PII-002` | 통합 응답 PII 누출 | NO | 차단 + 6-2 P1 |
| `AUX-E-QUAL-001` | quality_validation FAIL | YES | 재렌더 1회 |

### 4.4 E6 — 성능 벤치마크

| 시나리오 | timeout_policy | P95 |
|---------|------------|:---:|
| 2 items 병렬 (text + chart) | Rendering 복합 (§2 #11) | 800 ms (chart bound) |
| 5 items 2-layer DAG | Rendering 복합 | 1500 ms |
| 10 items 3-layer DAG | Rendering 복합 | 3000 ms |

### 4.5 E7 — 테스트 시나리오

| # | 시나리오 | 입력 | 예상 |
|---|---------|------|------|
| T-01 | 2 independent (text + chart) | items=2, depends_on=[] | 병렬, P95 800ms |
| T-02 | 3 with dependency (chart depends on table) | A→B chain | sequential, ~2초 |
| T-03 | DAGCycle | A→B→A | AUX-E-RENDER-004 |
| T-04 | partial_failure | chart 실패, table OK | placeholder 차트 + audit |
| T-05 | grid layout | 4 items + grid_cols=2 | 2x2 그리드 |
| T-06 | tabs layout | 3 items + tabs | tab UI |
| T-07 | F-06 out-of-scope | 스케줄러→I-14 distill 트리거 | §4.7 명시 |

### 4.6 E9 — 의존성 명세

| 카테고리 | 의존성 |
|---------|--------|
| 표준 라이브러리 | `asyncio` (gather + return_exceptions) |
| 외부 라이브러리 | `networkx` (DAG topological sort + cycle detect) |
| 내부 모듈 | `renderer_interface_v2`, 7 sub-renderer V2 (text/image/audio/chart/diagram/table/code), `quality_validation_v2`, `00_common/*` |
| 횡단 도메인 | `6-2` (통합 응답 PII 점검) |

### 4.7 F-06 이월 — out-of-scope 호출 경로 명시 (§7 2-2 절차 9)

본 모듈은 1-6 module_dependency_graph v1.1의 **19 엣지에 등장하지 않는** 다음 호출 경로를 *intentionally out of scope* 로 분류한다. STEP_C에서 정식 등재 검토:

| 호출 경로 | 트리거 | 현 상태 | 향후 |
|----------|------|------|------|
| 스케줄러 → I-14 distill | composite 종료 후 token 임계 도달 시 메모리 증류 트리거 | OOS (composite_output에서 호출 안 함) | I-14 trigger_conditions_v2 + I-13 → 스케줄러 이벤트로 분리 (STEP_C) |
| CORE → S-1 활성화 | composite 결과 응답 후 QoD 평가 | OOS (S-1이 자체 sliding window) | sdar_trigger_v2 또는 S-1 자체 evaluation_window 처리 |
| I-15 Evidence & QoD Manager 연결 | S-1 ↔ I-15 통합 (F-05) | PENDING | F-05 결정 후 등재 (STEP_C) |

---

## 5. LOCK 교차 검증

| LOCK | AUTHORITY | 본 V2 | 일치 |
|------|---------|-------|:----:|
| LOCK-AX-01 | I-13 CORE | §2 | ✅ |
| LOCK-AX-11 (ResponseEnvelope) | composite → answer.details | §4.2 | ✅ |
| LOCK-AX-12 (Action) | composite ⊂ Action | §4.1 | ✅ |
| LOCK-AX-13 (S0~S8) | composite는 S4~S5 산출 | §2 | ✅ |
| F-06 (out-of-scope) | 스케줄러→I-14 / CORE→S-1 | §4.7 명시 | ✅ |

---

## 6. V2 종결 marker

★ V2-Phase 2 (2026-05-10, 세션 2-2)
★ V1 byte EXACT (V1 §3 DAG ASCII 정본 보존)
★ LOCK-AX-01/11/12/13 EXACT 인용
★ E1+E2(networkx DAG + asyncio.gather + 레이아웃 + partial_failure)+E3+E5+E6+E7+E9 7요소 + F-06
★ interface_contracts C-08 (render_composite) baseline
★ 6-2 통합 응답 PII 점검 명시
★ V2 활성 (composite 핵심)
★ L3: PENDING
