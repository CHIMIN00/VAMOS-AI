# COND-075: 검색엔진 서버 — L3 상세 명세

> **모듈 ID**: COND-075
> **카테고리**: CAT-C (Ops/Infra) — Core
> **우선순위**: HIGH
> **Phase**: Phase 1
> **L3 수준**: L3
> **LOCK 준수**: LOCK-CD-03/04/05/06/08/10
> **인프라 패턴**: Inverted Index, BM25/Vector Hybrid, Sharding, Tail Latency Hedging

---

## E1. Input Schema

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional, Any

class SearchQuery(BaseModel):
    query_string: str = Field(..., min_length=1, max_length=2048)
    index: str
    filters: dict[str, Any] = Field(default_factory=dict)
    facets: list[str] = Field(default_factory=list)
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=200)
    sort: Optional[list[str]] = None
    mode: Literal["bm25", "vector", "hybrid"] = "hybrid"
    highlight: bool = True
    suggest: bool = False
    locale: Optional[str] = None    # 형태소 분석 힌트

class IndexOp(BaseModel):
    op: Literal["create", "delete", "upsert", "reindex"]
    index: str
    documents: Optional[list[dict]] = None
    document_id: Optional[str] = None
    schema_def: Optional[dict] = None

class SearchRequest(BaseModel):
    """COND-075 입력 스키마"""
    operation: Literal["search", "index", "suggest", "stats"] = "search"
    search_query: Optional[SearchQuery] = None
    index_operation: Optional[IndexOp] = None
    index: Optional[str] = None  # stats / suggest 용

    class Config:
        json_schema_extra = {
            "example": {
                "operation": "search",
                "search_query": {"query_string": "vamos 아키텍처",
                                 "index": "docs", "page": 1, "size": 10,
                                 "mode": "hybrid", "highlight": True}
            }
        }
```

---

## E2. Output Schema

```python
class SearchHit(BaseModel):
    document_id: str
    score: float
    source: dict[str, Any]
    highlights: dict[str, list[str]] = Field(default_factory=dict)

class FacetBucket(BaseModel):
    name: str
    buckets: list[dict[str, Any]]   # [{"value": ..., "count": ...}]

class SearchResults(BaseModel):
    hits: list[SearchHit]
    total: int
    facets: list[FacetBucket] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    took_ms: int

class IndexStatus(BaseModel):
    index: str
    docs_count: int
    size_bytes: int
    last_updated: str   # ISO-8601

class SearchResponse(BaseModel):
    """COND-075 출력 스키마"""
    operation: str
    search_results: Optional[SearchResults] = None
    index_status: Optional[IndexStatus] = None
    execution_time_ms: int

    class Config:
        json_schema_extra = {
            "example": {
                "operation": "search",
                "search_results": {
                    "hits": [{"document_id": "d1", "score": 0.92,
                              "source": {"title": "VAMOS 아키텍처 개요"},
                              "highlights": {"title": ["<em>VAMOS</em> <em>아키텍처</em>"]}}],
                    "total": 1, "facets": [], "suggestions": [], "took_ms": 14
                },
                "execution_time_ms": 18
            }
        }
```

---

## E3. Algorithm Pseudocode

```
FUNCTION execute(request) -> Result[SearchResponse, VamosError]:
    SWITCH request.operation:
      CASE "search":
          q = request.search_query
          IF NOT index_registry.has(q.index):
              RETURN Err(VamosError("COND_075_INDEX_NOT_FOUND", ...))
          analyzer = analyzer_for(q.locale OR config.default_locale)
          tokens = analyzer.tokenize(q.query_string)
          filters = compile_filters(q.filters)
          # Hedged request: 두 샤드에 동시 발사 + 빠른 응답 채택
          shard_replicas = router.shards_for(q.index)
          IF q.mode == "bm25":
              ranked = bm25_search(shard_replicas, tokens, filters, page=q.page, size=q.size, hedged=true)
          ELIF q.mode == "vector":
              embedding = embed_query(q.query_string)
              ranked = vector_search(shard_replicas, embedding, filters, top_k=q.size * q.page)
          ELSE:  # hybrid
              bm25 = bm25_search(shard_replicas, tokens, filters, top_k=200)
              vec  = vector_search(shard_replicas, embed_query(q.query_string), filters, top_k=200)
              ranked = reciprocal_rank_fusion(bm25, vec, top_k=q.size * q.page)
          page_hits = paginate(ranked, q.page, q.size)
          IF q.highlight:
              for h IN page_hits: h.highlights = highlight(h.source, tokens)
          facets = compute_facets(ranked, q.facets) IF q.facets ELSE []
          suggestions = suggest_corrections(tokens) IF q.suggest ELSE []
          RETURN Ok(SearchResponse(operation="search",
                                   search_results=SearchResults(hits=page_hits, total=len(ranked),
                                                                facets=facets, suggestions=suggestions,
                                                                took_ms=elapsed)))

      CASE "index":
          op = request.index_operation
          SWITCH op.op:
              CASE "create":  index_registry.create(op.index, op.schema_def)
              CASE "delete":  index_registry.delete_doc(op.index, op.document_id)
              CASE "upsert":  bulk_indexer.upsert(op.index, op.documents)
              CASE "reindex": reindex_job.start(op.index)
          RETURN Ok(...)

      CASE "suggest":
          completions = suggester.lookup(request.index, prefix=request.search_query.query_string,
                                         limit=config.suggest_limit)
          RETURN Ok(... search_results.suggestions=completions ...)

      CASE "stats":
          status = index_registry.stats(request.index)
          RETURN Ok(SearchResponse(operation="stats", index_status=status))
```

---

## E4. Error Handling

| FailureCode | 조건 | fallback_id | 사용자 메시지 |
|-------------|------|-------------|--------------|
| `COND_075_INDEX_NOT_FOUND` | index 미존재 | `FB_COND_REJECT` | "검색 인덱스를 찾을 수 없습니다." |
| `COND_075_QUERY_PARSE_ERROR` | query 구문 오류 | `FB_COND_075_PLAINTEXT` | "검색식 구문 오류. 일반 검색으로 대체." |
| `COND_075_SHARD_UNAVAILABLE` | 일부 샤드 장애 | `FB_COND_075_PARTIAL_RESULTS` | "일부 결과만 표시됩니다." |
| `COND_075_INDEXING_BACKLOG_FULL` | 인덱싱 큐 한도 초과 | `FB_COND_075_DEFER` | "인덱싱이 지연됩니다." |
| `COND_075_VECTOR_BACKEND_DOWN` | 벡터 검색 장애 | `FB_COND_075_BM25_ONLY` | "BM25 모드로 대체합니다." |
| `COND_075_QUERY_TOO_LARGE` | query/페이지 한도 초과 | `FB_COND_075_NARROW` | "쿼리 범위를 줄여 주세요." |
| `COND_075_EXECUTE_TIMEOUT` | timeout_ms 초과 | `FB_COND_SKIP` | "검색 시간 초과." |

```python
return Err(VamosError(
    failure_code="COND_075_INDEX_NOT_FOUND",
    message=f"index '{index}' is not registered",
    fallback_id="FB_COND_REJECT",
    trace_id=ctx.trace_id,
))
```

---

## E5. Dependency Map

| 관계 | 항목 |
|------|------|
| 소비 | — |
| 제공 | 모든 CAT (전문 검색) |

| I-Module | 용도 |
|----------|------|
| I-1, I-5, I-6, I-9 | 공통 |

| 인프라 / 라이브러리 | 사양 |
|----------------------|------|
| Elasticsearch / OpenSearch / Meilisearch | 검색 백엔드 |
| Tantivy (Rust) | 임베디드 옵션 |
| `sentence-transformers` / OpenAI embeddings | 벡터 인코딩 |
| Redis | suggestion cache |

---

## E6. Performance Benchmark (I-04)

| 메트릭 | SLA 목표 | 임계값 | 측정 |
|--------|---------|--------|------|
| **search p95 (BM25)** | ≤ 80 ms | > 250 ms | histogram |
| **search p95 (Hybrid)** | ≤ 200 ms | > 600 ms | histogram |
| **suggest p99** | ≤ 30 ms | > 100 ms | histogram |
| **indexing throughput** | ≥ 5,000 doc/s | < 1,000 | counter |
| **인덱싱 lag** | ≤ 5 s | > 30 s | gauge |
| **가용성** | 99.9 % | < 99.5 % | uptime |

---

## E7. Integration Test Spec

```yaml
- name: "search_basic_bm25"
  setup: [create_index("docs"), upsert([{id: "d1", title: "VAMOS 개요", body: "..."}])]
  input: { operation: "search", search_query: {query_string: "VAMOS", index: "docs", mode: "bm25"} }
  expected: [search_results.hits[0].document_id == "d1", search_results.total == 1]

- name: "search_hybrid_outranks_bm25"
  setup: [seed_index_with_synonyms()]
  input: { operation: "search", search_query: {query_string: "automobile", index: "docs", mode: "hybrid"} }
  expected: ["car" in search_results.hits[0].source.title]

- name: "search_index_not_found"
  input: { operation: "search", search_query: {query_string: "x", index: "missing"} }
  expected: [error.failure_code == "COND_075_INDEX_NOT_FOUND"]
```

---

## E8. Blue Node Integration

| 항목 | 값 |
|------|-----|
| **연동 Blue Node** | Research Node, Content Node (지식·문서 검색) |
| **Permission Level** | P0 |
| **게이트 요구** | policy, evidence (검색 결과 인용 시) |
| **호출 패턴** | OpsInfraMixin.search() / index() |

| 이벤트 | event_type |
|--------|------------|
| 초기화 | `cond.c.075.initialized` |
| 실행 시작/완료/실패 | `cond.c.075.execute_start` / `execute_done` / `execute_fail` |
| 헬스체크 | `cond.c.075.health` |
| 종료 | `cond.c.075.shutdown` |

Decision: `optional_signals ← {cond_module_id: "COND-075", op, index, mode, hits_count, took_ms}`

---

## E9. BaseModule ABC 적합성

```python
class Cond075SearchEngine(BaseModule):
    async def initialize(self) -> Result[None, VamosError]:
        self._client = await SearchBackend.connect(self.config.backend_dsn)
        self._embedder = Embedder.from_config(self.config)
        self._registry = await IndexRegistry.connect(self.config.registry_dsn)
        self._emit_event("cond.c.075.initialized")
        return Ok(None)

    async def execute(self, request: SearchRequest) -> Result[SearchResponse, VamosError]:
        return await self.run(request)

    async def health_check(self) -> Result[HealthStatus, VamosError]:
        return Ok(HealthStatus(healthy=await self._client.ping() and await self._registry.ping(),
                               latency_ms=elapsed))

    async def shutdown(self) -> Result[None, VamosError]:
        await self._registry.close(); await self._client.close()
        self._emit_event("cond.c.075.shutdown")
        return Ok(None)

    def get_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(id="COND-075", version="1.0.0",
                              capabilities=["search", "index", "suggest", "stats", "hybrid"])
```

---

## E10. Configuration

```python
class Cond075Config(ModuleConfig):
    enabled: bool = True
    priority: Literal["critical", "high", "medium", "low"] = "high"
    max_concurrent: int = 500
    timeout_ms: int = 3000
    retry_policy: RetryPolicy = RetryPolicy(max_retries=2, backoff_ms=200)

    backend_dsn: str
    registry_dsn: str
    default_locale: str = "ko-KR"
    default_mode: Literal["bm25", "vector", "hybrid"] = "hybrid"
    embedding_model: str = "BAAI/bge-m3"
    embedding_dim: int = 1024
    suggest_limit: int = 10
    max_query_length: int = 2048
    indexing_queue_max: int = 50000
```
