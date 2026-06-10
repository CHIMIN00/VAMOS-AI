# COND-018: Cognee AI Knowledge Graph — L2+ 상세 명세

> **모듈 ID**: COND-018
> **카테고리**: CAT-B (Knowledge)
> **이름**: Cognee AI Knowledge Graph
> **우선순위**: HIGH
> **Phase**: Phase 0
> **L-Level**: L2+ (Performance Benchmark/Integration Test Spec은 Phase 1/2 보강)
> **LOCK 준수**: LOCK-CD-03 BaseModule ABC (§3.4, D2.0-02 §1.2-A + §12.2 기반), LOCK-CD-04 Runnable 프로토콜 (D2.0-02 §1.2-A), LOCK-CD-05 ErrorHandlingStandard (D2.0-02 §0.3), LOCK-CD-06 VamosError 필드 (D2.0-02 §0.3), LOCK-CD-10 ModuleConfig (종합명세 §공통)
> **HUB NODE**: CAT-B 허브 — 13건 의존 중 9건 관여

---

## E1. Input Schema

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class Document(BaseModel):
    """인제스트 대상 문서"""
    doc_id: str = Field(..., description="문서 고유 ID")
    content: str = Field(..., min_length=1, description="문서 본문 텍스트")
    title: Optional[str] = Field(default=None, description="문서 제목")
    source: str = Field(default="unknown", description="출처 (notion, obsidian, web, etc.)")
    doc_type: Literal["text", "markdown", "html", "pdf_extracted"] = Field(
        default="text", description="문서 유형"
    )
    language: str = Field(default="ko", description="문서 언어 코드")
    metadata: dict = Field(default_factory=dict, description="추가 메타데이터")
    created_at: Optional[datetime] = Field(default=None, description="원본 문서 생성 시각")

class CogneeKGRequest(BaseModel):
    """COND-018 입력 스키마"""
    documents: list[Document] = Field(
        default_factory=list,
        description="인제스트할 문서 목록 (ingest/update 연산 시)"
    )
    operation: Literal["ingest", "query", "update"] = Field(
        ..., description="연산 유형 — ingest: 문서 → KG 추출, query: 그래프 쿼리, update: 기존 노드/엣지 갱신"
    )
    graph_query: Optional[str] = Field(
        default=None,
        description="query 연산 시 자연어 또는 Cypher 쿼리"
    )
    query_type: Literal["natural_language", "cypher", "hybrid"] = Field(
        default="natural_language",
        description="쿼리 유형"
    )
    max_hops: int = Field(
        default=3, ge=1, le=10,
        description="그래프 탐색 최대 홉 수"
    )
    max_results: int = Field(
        default=20, ge=1, le=200,
        description="쿼리 결과 최대 반환 수"
    )
    include_embeddings: bool = Field(
        default=False,
        description="결과에 노드 임베딩 포함 여부"
    )
    namespace: str = Field(
        default="default",
        description="그래프 네임스페이스 (사용자/프로젝트 격리)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "documents": [
                    {
                        "doc_id": "doc-2024-001",
                        "content": "Apple은 2024년 WWDC에서 Apple Intelligence를 발표했다. 이 기능은 iOS 18에 통합되어 Siri의 성능을 대폭 향상시킨다.",
                        "title": "Apple Intelligence 발표",
                        "source": "web",
                        "doc_type": "text",
                        "language": "ko"
                    }
                ],
                "operation": "ingest",
                "namespace": "user-42/tech-news"
            }
        }
```

---

## E2. Output Schema

```python
class KGNode(BaseModel):
    """지식 그래프 노드"""
    node_id: str = Field(description="노드 고유 ID")
    label: str = Field(description="노드 레이블 (엔티티 유형)")
    name: str = Field(description="엔티티 이름")
    properties: dict = Field(default_factory=dict, description="노드 속성")
    embedding: Optional[list[float]] = Field(default=None, description="노드 임베딩 벡터")

class KGEdge(BaseModel):
    """지식 그래프 엣지"""
    edge_id: str = Field(description="엣지 고유 ID")
    source_id: str = Field(description="출발 노드 ID")
    target_id: str = Field(description="도착 노드 ID")
    relation: str = Field(description="관계 유형")
    confidence: float = Field(ge=0.0, le=1.0, description="관계 신뢰도")
    source_doc: Optional[str] = Field(default=None, description="추출 원본 문서 ID")

class KGTriple(BaseModel):
    """지식 그래프 트리플 (주어-관계-목적어)"""
    subject: str = Field(description="주어 엔티티")
    predicate: str = Field(description="관계")
    object: str = Field(description="목적어 엔티티")
    confidence: float = Field(ge=0.0, le=1.0, description="트리플 신뢰도")
    source_doc_id: Optional[str] = Field(default=None, description="원본 문서 ID")

class GraphUpdate(BaseModel):
    """그래프 변경 요약"""
    added_nodes: list[KGNode] = Field(default_factory=list)
    added_edges: list[KGEdge] = Field(default_factory=list)
    updated_nodes: list[str] = Field(default_factory=list, description="갱신된 노드 ID 목록")
    updated_edges: list[str] = Field(default_factory=list, description="갱신된 엣지 ID 목록")
    removed_nodes: list[str] = Field(default_factory=list)
    removed_edges: list[str] = Field(default_factory=list)

class CogneeKGResponse(BaseModel):
    """COND-018 출력 스키마"""
    graph_update: GraphUpdate = Field(
        default_factory=GraphUpdate,
        description="그래프 변경 내역 (ingest/update 시)"
    )
    query_result: list[KGTriple] = Field(
        default_factory=list,
        description="쿼리 결과 트리플 목록 (query 시)"
    )
    insights: list[str] = Field(
        default_factory=list,
        description="그래프 기반 추론 인사이트"
    )
    total_nodes: int = Field(default=0, description="네임스페이스 내 전체 노드 수")
    total_edges: int = Field(default=0, description="네임스페이스 내 전체 엣지 수")
    operation_applied: str = Field(description="수행된 연산 유형")
    qod_scores: dict[str, float] = Field(
        default_factory=dict,
        description="문서별 QoD 점수"
    )
    execution_time_ms: int = Field(description="실행 시간 (밀리초)")

    class Config:
        json_schema_extra = {
            "example": {
                "graph_update": {
                    "added_nodes": [
                        {"node_id": "n-001", "label": "Company", "name": "Apple", "properties": {"industry": "tech"}},
                        {"node_id": "n-002", "label": "Product", "name": "Apple Intelligence", "properties": {}},
                        {"node_id": "n-003", "label": "Event", "name": "WWDC 2024", "properties": {"year": 2024}},
                        {"node_id": "n-004", "label": "Product", "name": "iOS 18", "properties": {}},
                        {"node_id": "n-005", "label": "Product", "name": "Siri", "properties": {}}
                    ],
                    "added_edges": [
                        {"edge_id": "e-001", "source_id": "n-001", "target_id": "n-002", "relation": "ANNOUNCED", "confidence": 0.95},
                        {"edge_id": "e-002", "source_id": "n-002", "target_id": "n-004", "relation": "INTEGRATED_IN", "confidence": 0.92},
                        {"edge_id": "e-003", "source_id": "n-002", "target_id": "n-005", "relation": "ENHANCES", "confidence": 0.88}
                    ]
                },
                "query_result": [],
                "insights": ["Apple Intelligence는 iOS 18과 Siri를 연결하는 핵심 기술로 추론됨"],
                "total_nodes": 5,
                "total_edges": 3,
                "operation_applied": "ingest",
                "qod_scores": {"doc-2024-001": 0.87},
                "execution_time_ms": 2340
            }
        }
```

---

## E3. Algorithm Pseudocode

> LOCK (D2.0-06 DEC-004): 하이브리드 RAG (벡터 검색 + GraphRAG) 채택
> LOCK (D2.0-06 DEC-005): BGE-M3 단일 기본값 (1024차원)
> LOCK (D2.0-06 §2.5.2): QoD < 0.4 → L2/L3 저장 금지

```
FUNCTION execute(request: CogneeKGRequest) -> Result<CogneeKGResponse, VamosError>:

    # 0. 입력 검증
    validation = validate_request(request)
    IF validation.is_err:
        RETURN Err(validation.error)

    start_time = now_ms()

    # 1. 그래프DB 연결 확인
    graph_db = GraphDBPool.get_connection(request.namespace)
    IF graph_db IS None:
        RETURN Err(VamosError(COND_018_GRAPHDB_UNAVAILABLE))

    SWITCH request.operation:

        CASE "ingest":
            # 2a. 문서 인제스트 파이프라인
            IF len(request.documents) == 0:
                RETURN Err(VamosError(COND_018_EMPTY_DOCUMENTS))

            all_nodes = []
            all_edges = []
            qod_scores = {}

            FOR doc IN request.documents:
                # 2a-1. QoD 평가
                qod = QoDEvaluator.score(
                    doc.content,
                    source=doc.source,
                    formula="relevance*0.30 + accuracy*0.25 + freshness*0.25 + completeness*0.20"
                )
                qod_scores[doc.doc_id] = qod

                IF qod < 0.4:
                    # LOCK (D2.0-06 §2.5.2): QoD < 0.4 → L2 저장 금지
                    LOG.warn("Document QoD below threshold, skipping KG ingest",
                             doc_id=doc.doc_id, qod=qod)
                    CONTINUE

                # 2a-2. Cognee AI 파이프라인: NER + 관계 추출
                cognee_result = CogneeAI.process(
                    text=doc.content,
                    language=doc.language,
                    pipeline=[
                        "sentence_split",
                        "entity_recognition",
                        "coreference_resolution",
                        "relation_extraction",
                        "entity_linking"
                    ]
                )

                IF cognee_result.is_err:
                    LOG.warn("Cognee processing failed", doc_id=doc.doc_id,
                             error=cognee_result.error)
                    CONTINUE

                # 2a-3. 엔티티 → 노드 변환
                FOR entity IN cognee_result.entities:
                    # 기존 노드 검색 (entity linking / dedup)
                    existing = graph_db.find_node_by_name(
                        name=entity.name,
                        label=entity.type,
                        namespace=request.namespace
                    )

                    IF existing IS NOT None:
                        # 기존 노드에 속성 병합
                        merged_props = merge_properties(existing.properties, entity.properties)
                        graph_db.update_node(existing.node_id, properties=merged_props)
                    ELSE:
                        # 새 노드 생성
                        embedding = EmbeddingService.encode(
                            text=f"{entity.type}: {entity.name}",
                            model="bge-m3", dim=1024
                        )
                        node = KGNode(
                            node_id=generate_uuid(),
                            label=entity.type,
                            name=entity.name,
                            properties=entity.properties,
                            embedding=embedding if request.include_embeddings else None
                        )
                        graph_db.create_node(node, namespace=request.namespace)

                        # VectorStore에 엔티티 임베딩 저장 (하이브리드 RAG용)
                        VectorStore.upsert(
                            id=node.node_id,
                            embedding=embedding,
                            metadata={"label": entity.type, "name": entity.name,
                                      "namespace": request.namespace},
                            namespace=f"{request.namespace}/entities"
                        )
                        all_nodes.append(node)

                # 2a-4. 관계 → 엣지 변환
                FOR relation IN cognee_result.relations:
                    source_node = resolve_node(relation.subject, graph_db, request.namespace)
                    target_node = resolve_node(relation.object, graph_db, request.namespace)

                    IF source_node IS None OR target_node IS None:
                        LOG.warn("Cannot resolve relation endpoints", relation=relation)
                        CONTINUE

                    # 중복 엣지 검사
                    existing_edge = graph_db.find_edge(
                        source_id=source_node.node_id,
                        target_id=target_node.node_id,
                        relation=relation.predicate,
                        namespace=request.namespace
                    )

                    IF existing_edge IS NOT None:
                        # 신뢰도 업데이트 (기존 + 신규의 가중 평균)
                        new_conf = (existing_edge.confidence * 0.6) + (relation.confidence * 0.4)
                        graph_db.update_edge(existing_edge.edge_id, confidence=new_conf)
                    ELSE:
                        edge = KGEdge(
                            edge_id=generate_uuid(),
                            source_id=source_node.node_id,
                            target_id=target_node.node_id,
                            relation=relation.predicate,
                            confidence=relation.confidence,
                            source_doc=doc.doc_id
                        )
                        graph_db.create_edge(edge, namespace=request.namespace)
                        all_edges.append(edge)

            # 그래프 통계
            stats = graph_db.get_stats(namespace=request.namespace)

            RETURN Ok(CogneeKGResponse(
                graph_update=GraphUpdate(added_nodes=all_nodes, added_edges=all_edges),
                insights=generate_ingest_insights(all_nodes, all_edges),
                total_nodes=stats.node_count,
                total_edges=stats.edge_count,
                operation_applied="ingest",
                qod_scores=qod_scores,
                execution_time_ms=elapsed_ms(start_time)
            ))

        CASE "query":
            # 2b. 그래프 쿼리
            IF request.graph_query IS None OR request.graph_query.strip() == "":
                RETURN Err(VamosError(COND_018_EMPTY_QUERY))

            triples = []
            insights = []

            IF request.query_type == "cypher":
                # 2b-1. 직접 Cypher 쿼리
                raw_results = graph_db.execute_cypher(
                    query=request.graph_query,
                    namespace=request.namespace,
                    limit=request.max_results
                )
                triples = cypher_results_to_triples(raw_results)

            ELIF request.query_type == "natural_language":
                # 2b-2. 자연어 → Cypher 변환 + GraphRAG
                # Step A: 쿼리 임베딩으로 관련 엔티티 검색 (벡터 검색)
                query_embedding = EmbeddingService.encode(
                    text=request.graph_query, model="bge-m3", dim=1024
                )
                related_entities = VectorStore.search(
                    embedding=query_embedding,
                    top_k=10,
                    namespace=f"{request.namespace}/entities",
                    min_similarity=0.6
                )

                # Step B: 관련 엔티티 기반 서브그래프 추출
                entity_ids = [e.id for e in related_entities]
                subgraph = graph_db.extract_subgraph(
                    seed_nodes=entity_ids,
                    max_hops=request.max_hops,
                    namespace=request.namespace
                )

                # Step C: 서브그래프 → 트리플 변환
                triples = subgraph_to_triples(subgraph, limit=request.max_results)

                # Step D: 추론 인사이트 생성
                insights = GraphReasoner.infer(
                    subgraph=subgraph,
                    query=request.graph_query,
                    max_insights=5
                )

            ELIF request.query_type == "hybrid":
                # 2b-3. 하이브리드: 벡터 + Cypher 결합
                # LOCK (D2.0-06 DEC-004): 하이브리드 RAG
                vector_triples = execute_vector_query(request, graph_db)
                cypher_query = NL2Cypher.translate(request.graph_query)
                cypher_triples = cypher_results_to_triples(
                    graph_db.execute_cypher(cypher_query, request.namespace, request.max_results)
                )
                triples = merge_and_deduplicate(vector_triples, cypher_triples)
                triples = triples[:request.max_results]
                insights = GraphReasoner.infer_from_triples(triples, request.graph_query)

            stats = graph_db.get_stats(namespace=request.namespace)

            RETURN Ok(CogneeKGResponse(
                query_result=triples,
                insights=insights,
                total_nodes=stats.node_count,
                total_edges=stats.edge_count,
                operation_applied="query",
                execution_time_ms=elapsed_ms(start_time)
            ))

        CASE "update":
            # 2c. 기존 노드/엣지 갱신
            IF len(request.documents) == 0:
                RETURN Err(VamosError(COND_018_EMPTY_DOCUMENTS))

            updated_nodes = []
            updated_edges = []

            FOR doc IN request.documents:
                # 해당 문서에서 추출된 기존 엔티티/관계 조회
                existing_elements = graph_db.find_by_source_doc(
                    doc_id=doc.doc_id, namespace=request.namespace
                )

                # 기존 요소 soft-delete
                FOR elem IN existing_elements:
                    graph_db.soft_delete(elem.id)

                # 재인제스트 (동일 파이프라인)
                cognee_result = CogneeAI.process(
                    text=doc.content, language=doc.language,
                    pipeline=["sentence_split", "entity_recognition",
                              "coreference_resolution", "relation_extraction",
                              "entity_linking"]
                )

                IF cognee_result.is_err:
                    LOG.warn("Cognee re-processing failed", doc_id=doc.doc_id)
                    CONTINUE

                FOR entity IN cognee_result.entities:
                    node = upsert_node(entity, graph_db, request.namespace)
                    updated_nodes.append(node.node_id)

                FOR relation IN cognee_result.relations:
                    edge = upsert_edge(relation, graph_db, request.namespace, doc.doc_id)
                    IF edge IS NOT None:
                        updated_edges.append(edge.edge_id)

            stats = graph_db.get_stats(namespace=request.namespace)

            RETURN Ok(CogneeKGResponse(
                graph_update=GraphUpdate(
                    updated_nodes=updated_nodes,
                    updated_edges=updated_edges
                ),
                total_nodes=stats.node_count,
                total_edges=stats.edge_count,
                operation_applied="update",
                execution_time_ms=elapsed_ms(start_time)
            ))


FUNCTION resolve_node(entity_ref: str, graph_db, namespace: str) -> Optional[KGNode]:
    """엔티티 참조를 기존 노드로 해석 (이름 + 임베딩 유사도 기반)"""
    exact = graph_db.find_node_by_name(name=entity_ref, namespace=namespace)
    IF exact IS NOT None:
        RETURN exact
    # 퍼지 매칭: 임베딩 유사도 ≥ 0.85
    emb = EmbeddingService.encode(text=entity_ref, model="bge-m3", dim=1024)
    candidates = VectorStore.search(
        embedding=emb, top_k=1,
        namespace=f"{namespace}/entities", min_similarity=0.85
    )
    IF len(candidates) > 0:
        RETURN graph_db.get_node(candidates[0].id)
    RETURN None
```

---

## E4. Error Handling

> LOCK (D2.0-02 §0.3): `Result<T, VamosError>`, 예외 throw 금지

| FailureCode | 조건 | fallback_id | 사용자 메시지 |
|-------------|------|------------|--------------|
| `COND_018_GRAPHDB_UNAVAILABLE` | Neo4j/그래프DB 연결 실패 | `F-018-01` | "지식 그래프 데이터베이스에 연결할 수 없습니다." |
| `COND_018_EMPTY_DOCUMENTS` | ingest/update인데 documents가 비어 있음 | `F-018-02` | "처리할 문서가 없습니다." |
| `COND_018_EMPTY_QUERY` | query인데 graph_query가 비어 있음 | `F-018-03` | "검색 쿼리를 입력해 주세요." |
| `COND_018_NER_FAILURE` | Cognee AI 엔티티 추출 실패 | `F-018-04` | "문서에서 지식 정보를 추출하지 못했습니다." |
| `COND_018_CYPHER_SYNTAX_ERROR` | Cypher 쿼리 문법 오류 | `F-018-05` | "그래프 쿼리 문법이 올바르지 않습니다." |
| `COND_018_NAMESPACE_NOT_FOUND` | 요청한 네임스페이스가 존재하지 않음 | `F-018-06` | "지정한 지식 공간을 찾을 수 없습니다." |
| `COND_018_EMBEDDING_FAILURE` | BGE-M3 임베딩 생성 실패 | `F-018-07` | "텍스트 인코딩에 실패했습니다." |
| `COND_018_DOCUMENT_TOO_LARGE` | 단일 문서가 최대 크기 초과 | `F-018-08` | "문서 크기가 최대 허용 한도를 초과합니다." |
| `COND_018_GRAPH_QUERY_TIMEOUT` | 쿼리 실행 시간 초과 | `F-018-09` | "쿼리 실행 시간이 초과되었습니다. 쿼리 범위를 줄여 주세요." |

### VamosError 구조
```python
VamosError(
    failure_code="COND_018_GRAPHDB_UNAVAILABLE",
    message="Neo4j connection failed: {detail}",
    fallback_id="F-018-01",
    trace_id=context.trace_id
)
```

---

## E5. Dependency Map

> §A 의존성 매트릭스 (P0-1 산출물) 반영

### CAT-B 내부 의존 (§A.3.2)
| 관계 | 의존 모듈 | 의존 내용 | 추출 기준 |
|------|-----------|----------|----------|
| **소비** (B-1) | COND-018 → COND-021 | Notion/Obsidian 임포트 데이터를 KG에 인제스트 | ②③ |
| **소비** (B-2) | COND-018 → COND-022 | 스크린캡처 OCR 텍스트를 KG에 인제스트 | ②③ |
| **제공** (B-3) | COND-019 → COND-018 | 신선도 관리가 KG 노드 TTL 관리 | ②③ |
| **제공** (B-4) | COND-020 → COND-018 | 충돌 감지가 KG 모순 탐색 | ②③ |
| **제공** (B-5) | COND-023 → COND-018 | 시간기반 관리가 KG temporal 쿼리 | ②③ |
| **제공** (B-6) | COND-024 → COND-018 | 예측적 서핑이 KG 기반 지식 추천 | ②③ |
| **제공** (B-7) | COND-087 → COND-018 | 개인위키가 KG 구조 활용 | ②③ |
| **제공** (B-8) | COND-089 → COND-018 | 지식 어시스턴트가 KG 쿼리 활용 | ②③ |
| **제공** (B-9) | COND-108 → COND-018 | Zettelkasten이 KG 그래프 구조 활용 | ②③ |

> COND-018은 **Level 1 + HUB NODE** — CAT-B 9건 의존 관여

### I-Series 소비 (§A.2.4)
| I-Module | 용도 | 공통/추가 |
|----------|------|----------|
| I-1 (Intent) | 의도 해석 (ingest/query/update 분류) | 공통 (26개 전체) |
| I-5 (Decision) | 라우팅/결정 | 공통 |
| I-6 (Self-check) | 자기 검증 | 공통 |
| I-9 (Logging) | 로깅 | 공통 |
| **I-3 (Memory)** | Memory 계층 연동 (KG → L2 저장) | **추가** |

### 외부 라이브러리
| 라이브러리 | 버전 | 용도 |
|-----------|------|------|
| `cognee` | ≥0.1 | Cognee AI 지식 추출 프레임워크 |
| `neo4j` | ≥5.0 | 그래프 데이터베이스 드라이버 |
| `spacy` | ≥3.7 | NER 백업 (Cognee 실패 시 fallback) |
| `sentence-transformers` | ≥2.2 | BGE-M3 임베딩 |
| `chromadb` | ≥0.4 | 엔티티 임베딩 벡터 저장 |

### 인프라
| 인프라 | 용도 |
|--------|------|
| Neo4j (persistent) | 지식 그래프 저장/쿼리 |
| ChromaDB | 엔티티 임베딩 벡터 검색 (하이브리드 RAG) |
| GPU (권장) | BGE-M3 임베딩 + NER 추론 가속 |
| 메모리 ≥ 8GB | 그래프 탐색 + NER 파이프라인 |

---

## E6. Performance Benchmark

> Phase 1 보강 예정 — basic SLA targets only

| 메트릭 | 기준 | 측정 방법 |
|--------|------|----------|
| **문서 인제스트 (단일)** | ≤ 3,000ms (1000자 문서) | NER + 관계 추출 + 노드/엣지 생성 |
| **문서 인제스트 (일괄 10건)** | ≤ 15,000ms | 병렬 파이프라인 |
| **자연어 쿼리** | ≤ 1,000ms (1K 노드 그래프) | 벡터 검색 + 서브그래프 추출 |
| **Cypher 쿼리** | ≤ 500ms (1K 노드) | 직접 Cypher 실행 |
| **하이브리드 쿼리** | ≤ 2,000ms (1K 노드) | 벡터 + Cypher 결합 |
| **NER 처리율** | ≥ 500 tokens/sec | Cognee AI 파이프라인 |
| **메모리 사용량** | ≤ 4GB (10K 노드 그래프) | Neo4j heap + 벡터 인덱스 |

### 병목 요인 및 최적화
- **NER 파이프라인**: Cognee AI가 병목 → 배치 처리 + GPU 가속
- **대규모 그래프 탐색**: max_hops 제한 + 인덱스 활용
- **엔티티 중복 해소**: 임베딩 기반 fuzzy match가 I/O 병목 → 캐시 활용

---

## E7. Integration Test Spec

> Phase 2 보강 예정 — skeleton scenarios only

### 시나리오 1: 문서 인제스트 → 쿼리
```yaml
name: "ingest_then_query"
setup:
  - create_namespace("test-ns-018")
input_sequence:
  - step: "ingest"
    request:
      documents:
        - doc_id: "doc-test-001"
          content: "서울시는 2024년 AI 스타트업 지원 프로그램을 발표했다. 총 예산은 500억원이다."
          source: "web"
          doc_type: "text"
          language: "ko"
      operation: "ingest"
      namespace: "test-ns-018"
    expected:
      - len(graph_update.added_nodes) >= 2
      - any(n.name == "서울시" for n in graph_update.added_nodes)
      - len(graph_update.added_edges) >= 1
      - operation_applied == "ingest"
  - step: "query"
    request:
      operation: "query"
      graph_query: "서울시의 AI 관련 프로그램"
      query_type: "natural_language"
      namespace: "test-ns-018"
      max_results: 10
    expected:
      - len(query_result) >= 1
      - any(t.subject == "서울시" for t in query_result)
```

### 시나리오 2: QoD 필터링
```yaml
name: "qod_filtering"
setup:
  - create_namespace("test-ns-018-qod")
  - mock_qod_evaluator(return_score=0.3)
input:
  documents:
    - doc_id: "doc-low-qod"
      content: "확인되지 않은 소문에 의하면 X 회사가 Y를 인수한다고 한다"
      source: "unknown"
  operation: "ingest"
  namespace: "test-ns-018-qod"
expected:
  - len(graph_update.added_nodes) == 0
  - qod_scores["doc-low-qod"] < 0.4
```

### 시나리오 3: Cypher 직접 쿼리
```yaml
name: "cypher_direct_query"
setup:
  - create_namespace("test-ns-018-cypher")
  - seed_graph(nodes=[{name: "Apple", label: "Company"}, {name: "iPhone", label: "Product"}],
               edges=[{source: "Apple", target: "iPhone", relation: "PRODUCES"}])
input:
  operation: "query"
  graph_query: "MATCH (c:Company)-[:PRODUCES]->(p:Product) RETURN c.name, p.name"
  query_type: "cypher"
  namespace: "test-ns-018-cypher"
expected:
  - len(query_result) >= 1
  - query_result[0].subject == "Apple"
  - query_result[0].object == "iPhone"
```

### 시나리오 4: 에러 — GraphDB 연결 실패
```yaml
name: "error_graphdb_unavailable"
setup:
  - shutdown_neo4j()
input:
  documents: [{doc_id: "d1", content: "test"}]
  operation: "ingest"
  namespace: "test-ns"
expected:
  - error.failure_code == "COND_018_GRAPHDB_UNAVAILABLE"
  - error.fallback_id == "F-018-01"
```

---

## E8. Blue Node Integration

> §B.6.2 CAT-B 연동 프로토콜 (P0-2 산출물) 반영
> LOCK (D2.0-03 §1.1): NODE는 CORE 규칙 상속, **독립 실행 불가** (LOCK-CD-08)

### 연동 프로토콜 (§B.6.2)
| 항목 | 값 |
|------|-----|
| **연동 Blue Node** | Research Node + Content Node |
| **Permission Level** | P0 (기본 활성) |
| **게이트 요구** | policy + evidence |
| **우선순위** | HIGH |

### 호출 패턴
```
User → "이 기사에서 주요 정보를 정리해 줘"
  → ORANGE CORE (I-1 Intent 해석: knowledge_ingest)
    → I-5 라우팅 → Research Node
      → Research Node: COND-018.execute(operation="ingest", documents=[...])
        → 5-Gate 평가 (§B.7.1):
          [1] PolicyGate ✅ (문서 인제스트 정책 충족)
          [2] CostGate — 해당 없음
          [3] EvidenceGate ✅ (문서 출처 QoD 검증)
          → COND-018 실행 → CogneeKGResponse 반환
            → Content Node (인사이트 요약 구성)
              → ORANGE CORE → User

User → "Apple과 관련된 기술 정보를 찾아줘"
  → ORANGE CORE (I-1 Intent 해석: knowledge_query)
    → I-5 라우팅 → Research Node
      → Research Node: COND-018.execute(operation="query", graph_query="Apple 관련 기술")
        → 5-Gate 평가 (§B.7.1):
          [1] PolicyGate ✅
          [3] EvidenceGate ✅ (결과 근거 확인)
          → COND-018 실행 → CogneeKGResponse 반환
            → Research Node → ORANGE CORE → User
```

### 이벤트 매핑 (§B.4 lower.dot 네이밍, §B.4.1 LogEvent 8필드)

| 이벤트 | event_type | 트리거 |
|--------|-----------|--------|
| 모듈 초기화 | `cond.b.018.initialized` | initialize() 완료 |
| KG 연산 시작 | `cond.b.018.execute_start` | execute() 진입 |
| KG 연산 완료 | `cond.b.018.execute_done` | 정상 반환 |
| KG 연산 실패 | `cond.b.018.execute_fail` | VamosError 발생 |
| 인제스트 완료 | `cond.b.018.ingest_done` | 문서 인제스트 성공 |
| 쿼리 완료 | `cond.b.018.query_done` | 그래프 쿼리 성공 |
| 헬스체크 | `cond.b.018.health` | health_check() 호출 |
| 모듈 종료 | `cond.b.018.shutdown` | shutdown() 호출 |

### Decision 기록 연결 (§B.8, D2.0-03 §6.0 LOCK)
- **실행 전**: `ModuleRequest.decision_id` → Decision 레코드에 참조 기록
- **실행 후**: `Decision.optional_signals` ← `{ "cond_module_id": "COND-018", "execution_ms": N, "operation": "ingest|query|update", "nodes_affected": M, "edges_affected": K }`
- **trace_id 필수**: decision_id 부재 시에도 trace_id로 추적 (D2.0-03 §5.2)

---

## E9. BaseModule ABC 적합성

> LOCK (§3.4 LOCK-CD-03): `initialize() / execute() / health_check() / shutdown()`
> LOCK (§3.4 LOCK-CD-04): Runnable 프로토콜 `run(input) → output, get_metadata(), health_check()`
> **CD-03 ↔ CD-04 관계**: execute()는 내부적으로 Runnable.run()을 위임, initialize()/shutdown()은 Runnable에 없는 생명주기 확장

```python
class Cond018CogneeKnowledgeGraph(BaseModule):
    """COND-018 Cognee AI Knowledge Graph — CAT-B HUB NODE"""

    async def initialize(self) -> Result[None, VamosError]:
        """Neo4j 연결, ChromaDB 연결, Cognee AI 파이프라인 초기화, BGE-M3 로드"""
        self._graph_db = await Neo4jDriver.connect(
            uri=self.config.neo4j_uri,
            auth=(self.config.neo4j_user, self.config.neo4j_password)
        )
        self._vector_store = await ChromaAdapter.connect(self.config.chroma_url)
        self._cognee = CogneeAI(
            ner_model=self.config.ner_model,
            relation_model=self.config.relation_model
        )
        self._embedding_model = await load_embedding_model("bge-m3", dim=1024)
        self._qod_evaluator = QoDEvaluator()
        self._emit_event("cond.b.018.initialized")
        return Ok(None)

    async def execute(self, request: CogneeKGRequest) -> Result[CogneeKGResponse, VamosError]:
        """Runnable.run() 위임 — Cognee AI 지식 그래프 연산 수행"""
        return await self.run(request)

    async def health_check(self) -> Result[HealthStatus, VamosError]:
        """Neo4j + ChromaDB + Cognee AI + BGE-M3 가용성 확인"""
        neo4j_ok = await self._graph_db.verify_connectivity()
        chroma_ok = await self._vector_store.ping()
        cognee_ok = self._cognee.is_ready()
        embedding_ok = self._embedding_model.is_loaded()
        healthy = neo4j_ok and chroma_ok and cognee_ok and embedding_ok
        return Ok(HealthStatus(
            healthy=healthy,
            latency_ms=elapsed,
            details={
                "neo4j": neo4j_ok,
                "chromadb": chroma_ok,
                "cognee_ai": cognee_ok,
                "embedding_model": embedding_ok
            }
        ))

    async def shutdown(self) -> Result[None, VamosError]:
        """Neo4j 연결 해제, ChromaDB 해제, Cognee 리소스 정리"""
        await self._graph_db.close()
        await self._vector_store.disconnect()
        self._cognee.cleanup()
        self._embedding_model.unload()
        self._emit_event("cond.b.018.shutdown")
        return Ok(None)

    def get_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            id="COND-018", version="1.0.0",
            capabilities=[
                "knowledge_graph_ingest", "knowledge_graph_query",
                "knowledge_graph_update", "entity_extraction",
                "relation_extraction", "hybrid_rag", "graph_reasoning"
            ]
        )
```

---

## E10. Configuration

> LOCK (종합명세 §공통 / LOCK-CD-10): ModuleConfig 표준 필드

```python
class Cond018Config(ModuleConfig):
    """COND-018 모듈 설정"""
    # ModuleConfig 상속 (enabled, priority, max_concurrent, timeout_ms, retry_policy)
    enabled: bool = True
    priority: Literal["critical", "high", "medium", "low"] = "high"
    max_concurrent: int = 5
    timeout_ms: int = 30000
    retry_policy: RetryPolicy = RetryPolicy(max_retries=2, backoff_ms=1000)

    # COND-018 전용 설정
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = Field(default_factory=lambda: os.environ["VAMOS_NEO4J_PASSWORD"])
    chroma_url: str = "http://localhost:8000"
    embedding_model: str = "bge-m3"
    embedding_dim: int = 1024
    ner_model: str = "cognee-default"
    relation_model: str = "cognee-default"
    max_document_size_chars: int = 50000
    max_batch_size: int = 50
    entity_similarity_threshold: float = 0.85
    default_max_hops: int = 3
    default_max_results: int = 20
    qod_minimum_threshold: float = 0.4
    enable_graph_reasoning: bool = True
    cypher_query_timeout_ms: int = 10000
    ingest_parallel_workers: int = 4
```
