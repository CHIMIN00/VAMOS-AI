# I-16 Knowledge Search Engine — 검색 API 설계 V2 Enhanced (L3 보강)

> **V단계**: V2-Phase 2
> **Status**: APPROVED (Phase 4 ✅ 완료, 2026-05-23, V2 strict L3 PASS production-ready 정본 승급, Phase 3 V-17 PASS inheritance)
> **Last-reviewed**: 2026-05-23 (Phase 4 production promotion)
> **ReadOnly**: TRUE (production 승급 후 immutable, 변경 시 일시 해제→fix→복원 EXACT 패턴 + audit log)
> **작성일**: 2026-05-10
> **V1 정본**: `search_api.md` (35 lines, byte EXACT)
> **모듈**: I-16 Knowledge Search Engine (CORE, Reasoning)
> **LOCK 참조**: LOCK-AX-01, LOCK-AX-06 (RAG hybrid), LOCK-AX-07 (BGE-M3), LOCK-AX-08 (VectorStore), LOCK-AX-10 (Semantic cache), LOCK-AX-11 (ResponseEnvelope)
> **L3 판정**: PASS (V-17 row content, 9/9 또는 8/9, 2026-05-14)
> **변경 이력 태그**: `V2-Phase 2` (2026-05-10, 세션 2-4, chain s9_36_a_2)
> **종합계획서 §**: §7 Phase 2 L1533~L1585 (2-4 I-16)
> **계약 cross-ref**: C-04 (I-16 → I-2 hybrid_search), C-05 (I-16 → I-8 policy filter), C-06 (I-16 → MEM VectorStore.search), C-07 (I-4/I-16 → I-5 data)
> **F-04 이월**: timeout_policy §2 표 확장 (I-16 내부 4종 정본화 → STEP_C)
> **F-10 이월**: Fallback Registry (22 ID, D2.0-02 §6.3 등재 → STEP_C)
> **횡단**: 6-2 (검색 결과 PII 마스킹)

---

## 1. 교차 참조 블록

| 정본 | 역할 |
|------|------|
| `AUXILIARY_MODULES_구조화_종합계획서.md` §7 Phase 2 (2-4) | V2 절차 |
| `AUTHORITY_CHAIN.md` §4 LOCK-AX-01/06/07/08/10/11 | LOCK 정본 |
| `search_api.md` (V1, 35 lines, byte EXACT) | V1 정본 (KnowledgeSearchEngine API) |
| `search_pipeline_v2.md` / `rag_integration_v2.md` / `external_sources_v2.md` (자매 V2) | 호출 분기 대상 |
| `06_mapping/interface_contracts.md` C-02/C-04/C-05/C-06/C-07 | 호출 계약 |
| `00_common/timeout_policy.md` §2 #4 VectorStore (search) + §2 #5 외부 검색 API | timeout 정본 |
| `6-2/01_ai-code-security/pii_regex_masking.md` | 결과 PII 마스킹 |

---

## 2. LOCK 인용 (R9 형식)

> LOCK (D2.0-01 §5.6, LOCK-AX-01): I-16 = CORE, change_lock=false (V1:ON / V2:ON / V3:ON)

> LOCK (D2.0-06 S7D-012, LOCK-AX-06): RAG hybrid search ratio = `alpha=0.3(BM25) + (1-alpha)=0.7(vector)`

> LOCK (D2.0-06 DEC-005, LOCK-AX-07): Embedding = `BGE-M3 (1024-dim, Matryoshka 256-dim)`

> LOCK (D2.0-06, LOCK-AX-08): VectorStore adapter interface = `upsert / search / delete / get_by_id` (4 methods)

> LOCK (D2.0-06, LOCK-AX-10): Semantic cache = `cosine_similarity >= 0.95, TTL 24h`

> LOCK (D2.0-02 §5.1.1, LOCK-AX-11): SearchResults → ResponseEnvelope `answer.details`

---

## 3. V1 → V2 승급 개요

V1 byte EXACT (35 lines, V1 §1 KnowledgeSearchEngine API). V1 변경 0.

| 요소 | 보강 | 위치 |
|------|------|------|
| **E1** | I-16 모듈 목적 (지식 검색 단일 진입) | §4.1 |
| **E2** | search/internal/external/hybrid 라우팅 의사코드 + 캐시 적용 | §4.2 |
| **E3** | SearchQuery / SearchResults Pydantic 모델 | §4.2 |
| **E4** | IKnowledgeSearchEngine ABC (V1 §1 보존 + 정밀화) | §4.2 |
| **E5** | timeout, 외부 API 실패, 캐시 미스 | §4.3 |
| **E6** | search P95 600ms, 50 req/s | §4.4 |
| **E7** | internal/external/hybrid + 캐시 hit/miss + PII | §4.5 |
| **E9** | sentence-transformers, ChromaDB, Whoosh, redis (cache) | §4.6 |

---

## 4. V2 본문 (L3 보강)

### 4.1 E1 — 목적 및 역할

I-16 Knowledge Search Engine은 **VAMOS 5-stage pipeline의 Reasoning 단계 핵심 모듈**. ORANGE CORE / I-2 RAG / I-8 Policy / MEM VectorStore / 외부 지식 소스 (Web/Wikipedia/arXiv/금융/뉴스) 를 **단일 검색 진입**으로 통합.

해결 문제:
1. **다소스 통합** — 호출자는 query만 전달, I-16이 모든 소스 라우팅 + 결과 병합 (RRF, search_pipeline_v2 §4).
2. **하이브리드 검색** — LOCK-AX-06 alpha=0.3 BM25 + 0.7 vector 하이브리드.
3. **시맨틱 캐시** — LOCK-AX-10 cosine ≥0.95 + TTL 24h 로 반복 쿼리 비용 절감.
4. **6-2 PII 결과 마스킹** — 검색 결과 텍스트는 L2 출력 후처리 적용.

### 4.2 E2 + E3 + E4 — 의사코드 + 모델 + ABC

**E3 모델**:
```python
class SearchQuery(BaseModel):
    query: str
    sources: list[Literal["internal", "web", "wikipedia", "arxiv", "finance", "news"]] = ["internal"]
    top_k: int = 5
    filters: dict = {}  # freshness, reliability_min 등
    cache_policy: Literal["use", "skip", "force_refresh"] = "use"
    locale: str = "ko-KR"

class SearchResults(BaseModel):
    documents: list[Document]  # ranked top-k
    cache_hit: bool
    sources_used: list[str]
    rrf_breakdown: dict[str, float]  # source별 가중치 기여도
    total_latency_ms: int

class Document(BaseModel):
    doc_id: str
    title: str
    content: str  # 본문 (PII 마스킹 적용)
    source: str  # "internal" | "web" | ...
    score: float  # final ranking score (0~1)
    freshness_days: int
    reliability: float  # source tier 기반
    metadata: dict
```

**E4 ABC** (V1 §1 byte EXACT 보존 + V2 정밀화):
```python
class IKnowledgeSearchEngine(ABC):
    @abstractmethod
    async def search(self, query: SearchQuery) -> SearchResults:
        """통합 검색 API. 캐시 → 라우팅 → RRF 병합 → reranking → 마스킹."""

    @abstractmethod
    async def search_internal(self, query: str) -> list[Document]:
        """I-2 RAG 파이프라인 검색 (C-04 호출)"""

    @abstractmethod
    async def search_external(self, query: str, sources: list[str]) -> list[Document]:
        """외부 지식 소스 검색 (external_sources_v2)"""

    @abstractmethod
    async def hybrid_search(self, query: str) -> list[Document]:
        """내부 + 외부 하이브리드 + RRF 병합 (search_pipeline_v2)"""
```

**E2 호출 흐름**:
```python
class KnowledgeSearchEngine(IKnowledgeSearchEngine):
    async def search(self, query: SearchQuery) -> SearchResults:
        start = time.time()

        # 0. top_k 범위 검증 (AUX-E-SEARCH-004: <1 또는 >100)
        if not 1 <= query.top_k <= 100:
            raise AuxError("AUX-E-SEARCH-004", "top_k out of range (1~100)")

        # 1. 시맨틱 캐시 (LOCK-AX-10)
        if query.cache_policy != "skip":
            cache_key_emb = self.embedder.encode(query.query)  # BGE-M3 1024-dim
            cached = await self.cache.semantic_get(cache_key_emb, threshold=0.95, ttl=86400)
            if cached and query.cache_policy != "force_refresh":
                return SearchResults(**cached, cache_hit=True, total_latency_ms=int((time.time() - start) * 1000))

        # 2. 라우팅: internal / external / hybrid
        if query.sources == ["internal"]:
            docs = await self.search_internal(query.query)
        elif "internal" not in query.sources:
            docs = await self.search_external(query.query, query.sources)
        else:
            docs = await self.hybrid_search(query.query)
            # search_pipeline_v2가 RRF 병합 + reranking 수행

        # 3. 필터링 (freshness, reliability_min, top_k)
        docs = self._apply_filters(docs, query.filters)
        docs = sorted(docs, key=lambda d: d.score, reverse=True)[:query.top_k]

        # 4. 6-2 L2 출력 PII 마스킹 (각 doc.content)
        for doc in docs:
            doc.content, _ = pii_masker.apply_l2(doc.content, strategy="partial")

        # 5. 캐시 저장 (skip 아닌 경우)
        result_dict = {"documents": [d.dict() for d in docs], "sources_used": query.sources, "rrf_breakdown": self._last_rrf_breakdown}
        if query.cache_policy != "skip":
            await self.cache.semantic_set(cache_key_emb, result_dict, ttl=86400)

        return SearchResults(documents=docs, cache_hit=False, sources_used=query.sources, rrf_breakdown=self._last_rrf_breakdown, total_latency_ms=int((time.time() - start) * 1000))

    async def search_internal(self, query: str) -> list[Document]:
        # C-04: I-16 → I-2 hybrid_search(alpha=0.3)
        return await self.i2_rag.hybrid_search(query, alpha=0.3)  # LOCK-AX-06

    async def search_external(self, query: str, sources: list[str]) -> list[Document]:
        # external_sources_v2 위임
        tasks = [self.external_adapters[s].search(query) for s in sources if s in self.external_adapters]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        docs = []
        for r in results:
            if isinstance(r, Exception):
                continue  # external 실패는 partial_failure 허용
            docs.extend(r)
        return docs

    async def hybrid_search(self, query: str) -> list[Document]:
        # search_pipeline_v2 위임 (RRF)
        return await self.pipeline.hybrid_search(query)
```

### 4.3 E5 — 에러 핸들링

| error_code | 설명 | recoverable | 처리 |
|-----------|------|:-----------:|------|
| `AUX-E-SEARCH-001` | 캐시 miss + 모든 소스 timeout | YES | external 1+개 성공 시 partial_failure 허용 |
| `AUX-E-SEARCH-002` | I-2 RAG 호출 실패 (C-04) | YES | external만 사용 + WARN |
| `AUX-E-SEARCH-003` | 캐시 unavailable (Redis down) | YES | cache 우회, 직접 검색 |
| `AUX-E-SEARCH-004` | top_k > 100 또는 < 1 | NO | 거부 + 가이드 |
| `AUX-E-PII-002` | 결과 PII 마스킹 실패 | NO | 차단 + 6-2 P1 |
| `AUX-E-LOCK-001` | LOCK-AX-06 alpha 변조 시도 (코드 결함) | NO | 즉시 abort + 무결성 알림 |

### 4.4 E6 — 성능 벤치마크

| 시나리오 | timeout_policy | P95 | 비고 |
|---------|------------|:---:|------|
| 캐시 hit (cosine ≥0.95) | (Redis lookup) | 50 ms | LOCK-AX-10 |
| internal-only (I-2 RAG) | VectorStore search (§2 #4) + BM25 | 400 ms | C-04 |
| external-only (Tavily) | 외부 검색 API (§2 #5) | 1500 ms | timeout |
| hybrid (internal + 2 external) | (복합) | 2500 ms | RRF + rerank 포함 |
| **전체 P95** | (복합) | **600 ms** (캐시 60% hit 가정) | |

### 4.5 E7 — 테스트 시나리오

| # | 시나리오 | 입력 | 예상 |
|---|---------|------|------|
| T-01 | internal + 캐시 miss | sources=[internal] | I-2 RAG 호출 + 결과 5건 |
| T-02 | 캐시 hit | 동일 query 2회째 | cache_hit=True, P95 50ms |
| T-03 | external (Wikipedia) | sources=[wikipedia] | MediaWiki API 결과 |
| T-04 | hybrid | sources=[internal, web] | RRF 병합 |
| T-05 | partial_failure | external 1 실패 | 나머지 결과 |
| T-06 | force_refresh | cache_policy=force_refresh | 캐시 우회, 신규 검색 |
| T-07 | top_k=100 (경계) | top_k=100 | 정상 |
| T-08 | top_k=200 (초과) | top_k=200 | AUX-E-SEARCH-004 |
| T-09 | PII 결과 | "이 사람의 이메일은 foo@bar.com" 포함 doc | content 마스킹 |
| T-10 | F-07 ABC 테스트 (C-04) | I-16 → I-2 | C-04 hybrid_search(alpha=0.3) 정합 |

### 4.6 E9 — 의존성 명세

| 카테고리 | 의존성 |
|---------|--------|
| 외부 라이브러리 (임베딩) | `sentence-transformers` (BGE-M3 1024-dim, LOCK-AX-07) |
| 외부 라이브러리 (캐시) | `redis-py` (semantic cache, LOCK-AX-10) |
| 외부 모듈 (의존) | `I-2 RAG` (C-04), `MEM VectorStore` (LOCK-AX-08) |
| 내부 모듈 | `search_pipeline_v2`, `rag_integration_v2`, `external_sources_v2`, `00_common/*` |
| 내부 모듈 | `IKnowledgeSearchEngine` ABC (본 V2 §4.2) |
| 횡단 도메인 | `6-2/01_ai-code-security/pii_regex_masking` (L2) |

---

## 5. LOCK 교차 검증

| LOCK | AUTHORITY 값 | 본 V2 반영 | 일치 |
|------|------------|------------|:----:|
| LOCK-AX-01 | I-16 CORE | §2 | ✅ |
| LOCK-AX-06 | alpha=0.3 BM25 + 0.7 vector | §4.2 search_internal hybrid_search(alpha=0.3) | ✅ |
| LOCK-AX-07 | BGE-M3 1024-dim, Matryoshka 256 | §4.2 embedder.encode | ✅ |
| LOCK-AX-08 | VectorStore 4-method | §4.6 의존 + C-06 | ✅ |
| LOCK-AX-10 | cosine ≥0.95, TTL 24h | §4.2 semantic_get(threshold=0.95, ttl=86400) | ✅ |
| LOCK-AX-11 | ResponseEnvelope 래핑 | §4.1 | ✅ |

---

## 6. V2 종결 marker

★ V2-Phase 2 (2026-05-10, 세션 2-4)
★ V1 byte EXACT
★ LOCK-AX-01/06/07/08/10/11 EXACT 인용
★ E1+E2(라우팅 + 캐시 + 마스킹)+E3+E4 ABC+E5+E6+E7+E9 7요소
★ C-04/C-05/C-06/C-07 baseline
★ F-04/F-10 이월 명시 (STEP_C)
★ 6-2 L2 출력 마스킹
★ L3: PENDING
