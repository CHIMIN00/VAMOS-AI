# COND-021: Notion/Obsidian 임포트 — L2+ 상세 명세

> **모듈 ID**: COND-021
> **카테고리**: CAT-B (Knowledge)
> **이름**: Notion/Obsidian 임포트
> **우선순위**: HIGH
> **Phase**: Phase 0
> **L-Level**: L2+
> **LOCK 준수**: LOCK-CD-03 BaseModule ABC (§3.4, D2.0-02 §1.2-A + §12.2 기반), LOCK-CD-04 Runnable 프로토콜 (D2.0-02 §1.2-A), LOCK-CD-05 ErrorHandlingStandard (D2.0-02 §0.3), LOCK-CD-06 VamosError 필드 (D2.0-02 §0.3), LOCK-CD-10 ModuleConfig (종합명세 §공통)

---

## E1. Input Schema

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class NotionConnectionConfig(BaseModel):
    """Notion API 연결 설정"""
    api_token: str = Field(..., description="Notion Integration API 토큰")
    database_id: Optional[str] = Field(
        default=None, description="특정 데이터베이스 ID (None이면 전체 워크스페이스)"
    )
    workspace_id: Optional[str] = Field(
        default=None, description="Notion 워크스페이스 ID"
    )

class ObsidianConnectionConfig(BaseModel):
    """Obsidian Vault 연결 설정"""
    vault_path: str = Field(..., description="Obsidian Vault 루트 경로")
    include_hidden: bool = Field(
        default=False, description=".obsidian 등 숨김 디렉토리 포함 여부"
    )

class ConnectionConfig(BaseModel):
    """소스별 연결 설정 (Union)"""
    notion: Optional[NotionConnectionConfig] = None
    obsidian: Optional[ObsidianConnectionConfig] = None

class ImportFilter(BaseModel):
    """임포트 필터링 조건"""
    tags: Optional[list[str]] = Field(
        default=None, description="포함할 태그 목록 (OR 조건)"
    )
    exclude_tags: Optional[list[str]] = Field(
        default=None, description="제외할 태그 목록"
    )
    date_from: Optional[datetime] = Field(
        default=None, description="이 날짜 이후 수정된 문서만"
    )
    date_to: Optional[datetime] = Field(
        default=None, description="이 날짜 이전 수정된 문서만"
    )
    path_pattern: Optional[str] = Field(
        default=None, description="Obsidian 전용: glob 패턴 (예: 'projects/**/*.md')"
    )
    max_documents: int = Field(
        default=1000, ge=1, le=10000,
        description="최대 임포트 문서 수"
    )

class NotionObsidianImportRequest(BaseModel):
    """COND-021 입력 스키마"""
    source: Literal["notion", "obsidian"] = Field(
        ..., description="임포트 소스 플랫폼"
    )
    connection_config: ConnectionConfig = Field(
        ..., description="소스별 연결 설정"
    )
    import_filter: ImportFilter = Field(
        default_factory=ImportFilter,
        description="임포트 필터링 조건"
    )
    preserve_links: bool = Field(
        default=True, description="내부 링크 구조 보존 여부"
    )
    resolve_backlinks: bool = Field(
        default=True, description="백링크 양방향 해석 여부"
    )
    embed_on_import: bool = Field(
        default=True, description="임포트 즉시 임베딩 생성 여부"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "source": "obsidian",
                "connection_config": {
                    "obsidian": {
                        "vault_path": "/home/user/my-vault",
                        "include_hidden": False
                    }
                },
                "import_filter": {
                    "tags": ["project", "reference"],
                    "date_from": "2025-01-01T00:00:00",
                    "max_documents": 500
                },
                "preserve_links": True,
                "resolve_backlinks": True,
                "embed_on_import": True
            }
        }
```

---

## E2. Output Schema

```python
class ImportedDocument(BaseModel):
    """임포트된 개별 문서"""
    doc_id: str = Field(description="VAMOS 내부 문서 ID")
    source_id: str = Field(description="원본 소스의 문서 ID/경로")
    title: str = Field(description="문서 제목")
    content_hash: str = Field(description="콘텐츠 SHA-256 해시 (중복 감지용)")
    tags: list[str] = Field(default_factory=list, description="문서 태그")
    outgoing_links: list[str] = Field(
        default_factory=list, description="이 문서에서 나가는 링크 목록 (doc_id)"
    )
    metadata: dict = Field(
        default_factory=dict,
        description="원본 메타데이터 (frontmatter, Notion properties 등)"
    )
    embedded: bool = Field(description="임베딩 생성 완료 여부")

class ImportStats(BaseModel):
    """임포트 통계"""
    total_scanned: int = Field(description="스캔된 총 문서 수")
    total_imported: int = Field(description="임포트 성공 문서 수")
    total_skipped: int = Field(description="필터/중복으로 건너뛴 문서 수")
    total_failed: int = Field(description="임포트 실패 문서 수")
    total_links_resolved: int = Field(description="해석된 링크 수")
    total_backlinks_created: int = Field(description="생성된 백링크 수")
    elapsed_ms: int = Field(description="총 소요 시간 (밀리초)")

class NotionObsidianImportResponse(BaseModel):
    """COND-021 출력 스키마"""
    imported: list[ImportedDocument] = Field(
        description="임포트된 문서 리스트"
    )
    link_map: dict[str, list[str]] = Field(
        description="문서 간 링크 맵 {source_doc_id: [target_doc_id, ...]}"
    )
    stats: ImportStats = Field(description="임포트 통계")

    class Config:
        json_schema_extra = {
            "example": {
                "imported": [
                    {
                        "doc_id": "vamos-doc-a1b2c3",
                        "source_id": "projects/my-project.md",
                        "title": "My Project Notes",
                        "content_hash": "sha256:abcdef1234567890",
                        "tags": ["project", "reference"],
                        "outgoing_links": ["vamos-doc-d4e5f6"],
                        "metadata": {"created": "2025-06-01", "author": "user"},
                        "embedded": True
                    }
                ],
                "link_map": {
                    "vamos-doc-a1b2c3": ["vamos-doc-d4e5f6"],
                    "vamos-doc-d4e5f6": ["vamos-doc-a1b2c3"]
                },
                "stats": {
                    "total_scanned": 150,
                    "total_imported": 120,
                    "total_skipped": 25,
                    "total_failed": 5,
                    "total_links_resolved": 340,
                    "total_backlinks_created": 210,
                    "elapsed_ms": 45000
                }
            }
        }
```

---

## E3. Algorithm Pseudocode

```
FUNCTION execute(request: NotionObsidianImportRequest) -> Result<NotionObsidianImportResponse, VamosError>:

    # 1. 소스 커넥터 초기화
    IF request.source == "notion":
        connector = NotionConnector(request.connection_config.notion)
        validation = connector.validate_token()
        IF validation.is_err:
            RETURN Err(VamosError(COND_021_AUTH_FAILED, fallback=F-021-01))
    ELSE:  # obsidian
        connector = ObsidianVaultParser(request.connection_config.obsidian)
        validation = connector.validate_vault_path()
        IF validation.is_err:
            RETURN Err(VamosError(COND_021_VAULT_NOT_FOUND, fallback=F-021-02))

    # 2. 문서 목록 수집 (RAG pipeline — Collect stage, §1.1)
    raw_documents = connector.list_documents()
    filtered = apply_import_filter(raw_documents, request.import_filter)
    LOG info: f"Scanned {len(raw_documents)}, filtered to {len(filtered)}"

    # 3. 문서 본문 추출 및 변환
    imported_docs = []
    failed_docs = []
    FOR doc_ref IN filtered:
        TRY_RESULT:
            raw_content = connector.fetch_content(doc_ref)

            IF request.source == "notion":
                # Notion Block → Markdown 변환
                markdown = notion_blocks_to_markdown(raw_content.blocks)
                metadata = extract_notion_properties(raw_content.properties)
                links = extract_notion_links(raw_content.blocks)
            ELSE:
                # Obsidian Markdown 파싱
                frontmatter, body = parse_obsidian_md(raw_content)
                metadata = frontmatter
                markdown = body
                links = extract_wikilinks(body) + extract_markdown_links(body)

            content_hash = sha256(markdown)

            # 중복 검사
            existing = knowledge_store.find_by_hash(content_hash)
            IF existing IS NOT None:
                skipped += 1
                CONTINUE

            # 4. VAMOS 문서 생성
            doc_id = generate_doc_id()
            vamos_doc = ImportedDocument(
                doc_id=doc_id,
                source_id=doc_ref.id,
                title=doc_ref.title,
                content_hash=content_hash,
                tags=metadata.get("tags", []),
                outgoing_links=links,
                metadata=metadata,
                embedded=False
            )
            imported_docs.append(vamos_doc)

        ON_ERR(e):
            failed_docs.append(doc_ref)
            LOG warn: f"Failed to import {doc_ref.id}: {e}"

    # 5. 링크 구조 해석
    link_map = {}
    backlink_count = 0
    IF request.preserve_links:
        # 소스 ID → VAMOS doc_id 매핑 테이블 구축
        id_mapping = {doc.source_id: doc.doc_id FOR doc IN imported_docs}

        FOR doc IN imported_docs:
            resolved_links = []
            FOR link IN doc.outgoing_links:
                target_id = id_mapping.get(link)
                IF target_id IS NOT None:
                    resolved_links.append(target_id)
            link_map[doc.doc_id] = resolved_links
            doc.outgoing_links = resolved_links

        # 백링크 생성 (양방향)
        backlink_count = 0
        IF request.resolve_backlinks:
            FOR source_id, targets IN link_map.items():
                FOR target_id IN targets:
                    IF target_id NOT IN link_map:
                        link_map[target_id] = []
                    IF source_id NOT IN link_map[target_id]:
                        link_map[target_id].append(source_id)
                        backlink_count += 1

    # 6. VectorStore 저장 및 임베딩 (D2.0-06 §1.1 RAG pipeline — Embed+Store)
    IF request.embed_on_import:
        FOR doc IN imported_docs:
            chunks = chunk_document(doc, strategy="semantic", max_tokens=512)
            embeddings = bge_m3_embed(chunks)  # DEC-005: BGE-M3, 1024dim
            vector_store.upsert(
                ids=[f"{doc.doc_id}_chunk_{i}" FOR i IN range(len(chunks))],
                embeddings=embeddings,
                metadatas=[{"doc_id": doc.doc_id, "chunk_idx": i} FOR i IN range(len(chunks))]
            )
            doc.embedded = True

    # 7. 통계 산출 및 반환
    stats = ImportStats(
        total_scanned=len(raw_documents),
        total_imported=len(imported_docs),
        total_skipped=len(raw_documents) - len(filtered) - len(failed_docs),
        total_failed=len(failed_docs),
        total_links_resolved=sum(len(v) FOR v IN link_map.values()),
        total_backlinks_created=backlink_count,
        elapsed_ms=elapsed_ms()
    )

    RETURN Ok(NotionObsidianImportResponse(
        imported=imported_docs,
        link_map=link_map,
        stats=stats
    ))
```

---

## E4. Error Handling

> LOCK (D2.0-02 §0.3): `Result<T, VamosError>`, 예외 throw 금지

| FailureCode | 조건 | fallback_id | 사용자 메시지 |
|-------------|------|------------|--------------|
| `COND_021_AUTH_FAILED` | Notion API 토큰 인증 실패 | `F-021-01` | "Notion 인증에 실패했습니다. API 토큰을 확인해 주세요." |
| `COND_021_VAULT_NOT_FOUND` | Obsidian Vault 경로가 존재하지 않거나 접근 불가 | `F-021-02` | "Obsidian Vault 경로를 찾을 수 없습니다." |
| `COND_021_RATE_LIMITED` | Notion API rate limit 초과 | `F-021-03` | "Notion API 호출 한도를 초과했습니다. 잠시 후 다시 시도해 주세요." |
| `COND_021_PARSE_ERROR` | Markdown/Block 파싱 실패 (깨진 포맷) | `F-021-04` | "일부 문서의 형식을 해석할 수 없습니다." |
| `COND_021_LINK_RESOLUTION_FAIL` | 링크 대상 문서를 찾을 수 없음 | `F-021-05` | "일부 링크의 대상 문서를 찾을 수 없습니다." |
| `COND_021_EMBED_FAILED` | 임베딩 생성 또는 VectorStore upsert 실패 | `F-021-06` | "임베딩 저장 중 오류가 발생했습니다." |
| `COND_021_QUOTA_EXCEEDED` | 임포트 문서 수가 시스템 한도 초과 | `F-021-07` | "임포트 한도를 초과했습니다. 필터를 조정해 주세요." |

### VamosError 구조
```python
VamosError(
    failure_code="COND_021_AUTH_FAILED",
    message="Notion API authentication failed: invalid token",
    fallback_id="F-021-01",
    trace_id=context.trace_id
)
```

---

## E5. Dependency Map

> §A 의존성 매트릭스 (P0-1 산출물) 반영

### CAT-B 내부 의존 (§A.3.2)
| 관계 | 의존 모듈 | 의존 내용 | 추출 기준 |
|------|-----------|----------|----------|
| **소비됨** | COND-018 (지식 통합) → COND-021 | 018이 021을 호출하여 Notion/Obsidian 소스 임포트 실행 | ②③ |

> COND-021은 **Level 0** — CAT-B 내부 다른 모듈에 의존하지 않음. 018에 의해 소비됨

### I-Series 소비 (§A.2.4)
| I-Module | 용도 | 공통/추가 |
|----------|------|----------|
| I-1 (Intent) | 의도 해석 | 공통 (26개 전체) |
| I-5 (Decision) | 라우팅/결정 | 공통 |
| I-6 (Self-check) | 자기 검증 | 공통 |
| I-9 (Logging) | 로깅 | 공통 |
| **I-11 (External Tool)** | Notion API / Obsidian Vault 외부 접근 | **추가** |

### 외부 라이브러리
| 라이브러리 | 버전 | 용도 |
|-----------|------|------|
| `notion-client` | ≥2.2 | Notion API 클라이언트 |
| `pyyaml` | ≥6.0 | YAML frontmatter 파싱 |
| `python-frontmatter` | ≥1.0 | Markdown frontmatter 추출 |
| `mistune` | ≥3.0 | Markdown 파싱 및 AST 변환 |
| `hashlib` | stdlib | SHA-256 해시 (중복 감지) |

### 인프라
| 인프라 | 용도 |
|--------|------|
| VectorStore (ChromaDB) | 임베딩 저장 (D2.0-06 §1.1) |
| BGE-M3 Embedding Server | 1024dim 벡터 생성 (DEC-005) |
| 파일시스템 접근 | Obsidian Vault 읽기 |
| 네트워크 (HTTPS) | Notion API 호출 |

### D2.0-06 LOCK Citations

> LOCK (D2.0-06 §1.1): RAG 파이프라인 6단계 — 수집(Collect): 문서/청크 소스 수집 (파일, URL, DB 등)
> LOCK (D2.0-06 §2.2-A): VectorStore 어댑터 — upsert(records) / search(query_vector, top_k, filters) / delete(ids) / get_by_id(id)

---

## E6. Performance Benchmark

> Phase 1 보강 예정 — basic SLA targets only

| 메트릭 | 기준 | 측정 방법 |
|--------|------|----------|
| **Notion 단일 페이지 임포트** | ≤ 2,000ms | API fetch + parse + store |
| **Obsidian 단일 파일 임포트** | ≤ 200ms | 파일 읽기 + parse + store |
| **배치 100문서 (Notion)** | ≤ 120,000ms | 병렬 3 연결, rate limit 준수 |
| **배치 100문서 (Obsidian)** | ≤ 10,000ms | 순차 읽기 + 병렬 임베딩 |
| **링크 해석 (1000 links)** | ≤ 3,000ms | ID 매핑 + 백링크 생성 |
| **임베딩 (100문서, 평균 5 chunks)** | ≤ 30,000ms | BGE-M3 batch embed + upsert |
| **메모리 사용량** | ≤ 1GB (1000문서 배치) | peak RSS 측정 |

### 병목 요인 및 최적화
- **Notion API rate limit**: 3 req/s → 커넥션 풀 + exponential backoff
- **대규모 Vault**: 10,000+ 파일 → 스트리밍 처리, 청크 단위 임베딩
- **링크 그래프 구축**: O(N*M) → 해시 기반 역인덱스로 O(N) 최적화

---

## E7. Integration Test Spec

> Phase 2 보강 예정 — skeleton scenarios only

### 시나리오 1: Obsidian Vault 기본 임포트
```yaml
name: "obsidian_basic_import"
setup:
  - create_test_vault("/tmp/test-vault", files=10, with_wikilinks=True)
  - ensure_vectorstore_empty()
input:
  source: "obsidian"
  connection_config:
    obsidian:
      vault_path: "/tmp/test-vault"
      include_hidden: false
  import_filter:
    max_documents: 100
  preserve_links: true
  resolve_backlinks: true
  embed_on_import: true
expected:
  - stats.total_imported == 10
  - stats.total_failed == 0
  - all(doc.embedded == true for doc in imported)
  - len(link_map) > 0
  - stats.total_backlinks_created > 0
```

### 시나리오 2: Notion 데이터베이스 필터 임포트
```yaml
name: "notion_filtered_import"
setup:
  - mock_notion_api(database_id="db-123", pages=50, tags=["work", "personal"])
input:
  source: "notion"
  connection_config:
    notion:
      api_token: "test-token-xxx"
      database_id: "db-123"
  import_filter:
    tags: ["work"]
    date_from: "2025-01-01T00:00:00"
    max_documents: 100
  preserve_links: true
  embed_on_import: false
expected:
  - stats.total_scanned == 50
  - stats.total_imported < 50
  - all("work" in doc.tags for doc in imported)
  - all(doc.embedded == false for doc in imported)
```

### 시나리오 3: 인증 실패 에러
```yaml
name: "error_notion_auth_failed"
setup:
  - mock_notion_api(return_401=True)
input:
  source: "notion"
  connection_config:
    notion:
      api_token: "invalid-token"
  import_filter: {}
expected:
  - error.failure_code == "COND_021_AUTH_FAILED"
  - error.fallback_id == "F-021-01"
```

### 시나리오 4: 중복 문서 건너뛰기
```yaml
name: "skip_duplicate_documents"
setup:
  - create_test_vault("/tmp/test-vault-dup", files=5)
  - pre_import_vault("/tmp/test-vault-dup")  # 사전 임포트
input:
  source: "obsidian"
  connection_config:
    obsidian:
      vault_path: "/tmp/test-vault-dup"
  import_filter: {}
  embed_on_import: true
expected:
  - stats.total_scanned == 5
  - stats.total_imported == 0
  - stats.total_skipped == 5
```

---

## E8. Blue Node Integration

> §B.6.2 CAT-B 연동 프로토콜 (P0-2 산출물) 반영
> > LOCK (D2.0-03 §1.1): NODE는 CORE 규칙 상속, **독립 실행 불가** (LOCK-CD-08)

### 연동 프로토콜 (§B.6.2)
| 항목 | 값 |
|------|-----|
| **연동 Blue Node** | Content Node |
| **Permission Level** | P0 (기본 활성) |
| **게이트 요구** | policy, approval |
| **우선순위** | HIGH |

### 호출 패턴
```
User → "내 Obsidian 볼트에서 프로젝트 관련 노트 가져와줘"
  → ORANGE CORE (I-1 Intent 해석: import_knowledge_source)
    → I-5 라우팅 → Content Node
      → Content Node: COND-021.execute(source="obsidian", ...)
        → 5-Gate 평가 (§B.7.1):
          [1] PolicyGate ✅ (외부 파일 접근 정책 준수)
          [2] ApprovalGate ✅ (사용자 임포트 승인 확인)
          [3] CostGate — 해당 없음 (로컬 파일 접근)
          → COND-021 실행 → NotionObsidianImportResponse 반환
            → Content Node → ORANGE CORE → User
```

### 이벤트 매핑 (§B.4 lower.dot 네이밍, §B.4.1 LogEvent 8필드)

| 이벤트 | event_type | 트리거 |
|--------|-----------|--------|
| 모듈 초기화 | `cond.b.021.initialized` | initialize() 완료 |
| 임포트 시작 | `cond.b.021.execute_start` | execute() 진입 |
| 임포트 진행 | `cond.b.021.progress` | 매 50문서 처리 시 |
| 임포트 완료 | `cond.b.021.execute_done` | 정상 반환 |
| 임포트 실패 | `cond.b.021.execute_fail` | VamosError 발생 |
| 헬스체크 | `cond.b.021.health` | health_check() 호출 |
| 모듈 종료 | `cond.b.021.shutdown` | shutdown() 호출 |

### Decision 기록 연결 (§B.8, D2.0-03 §6.0 LOCK)
- **실행 전**: `ModuleRequest.decision_id` → Decision 레코드에 참조 기록
- **실행 후**: `Decision.optional_signals` ← `{ "cond_module_id": "COND-021", "execution_ms": N, "result_type": "import", "docs_imported": M }`
- **trace_id 필수**: decision_id 부재 시에도 trace_id로 추적 (D2.0-03 §5.2)

---

## E9. BaseModule ABC 적합성

> LOCK (§3.4 LOCK-CD-03): `initialize() / execute() / health_check() / shutdown()`
> LOCK (§3.4 LOCK-CD-04): Runnable 프로토콜 `run(input) → output, get_metadata(), health_check()`
> **CD-03 ↔ CD-04 관계**: execute()는 내부적으로 Runnable.run()을 위임, initialize()/shutdown()은 Runnable에 없는 생명주기 확장

```python
class Cond021NotionObsidianImport(BaseModule):
    """COND-021 Notion/Obsidian 임포트"""

    async def initialize(self) -> Result[None, VamosError]:
        """VectorStore 연결, 임베딩 서비스 초기화, 커넥터 팩토리 준비"""
        self._vector_store = await VectorStoreAdapter.connect()  # V1=ChromaAdapter
        self._embedder = BgeM3Embedder(dim=1024)  # DEC-005
        self._notion_factory = NotionConnectorFactory()
        self._obsidian_factory = ObsidianParserFactory()
        self._emit_event("cond.b.021.initialized")
        return Ok(None)

    async def execute(
        self, request: NotionObsidianImportRequest
    ) -> Result[NotionObsidianImportResponse, VamosError]:
        """Runnable.run() 위임 — Notion/Obsidian 임포트 실행"""
        return await self.run(request)

    async def health_check(self) -> Result[HealthStatus, VamosError]:
        """VectorStore 연결 + 임베딩 서비스 가용성 확인"""
        vs_ok = await self._vector_store.ping()
        embed_ok = await self._embedder.ping()
        return Ok(HealthStatus(
            healthy=vs_ok and embed_ok,
            details={"vectorstore": vs_ok, "embedder": embed_ok}
        ))

    async def shutdown(self) -> Result[None, VamosError]:
        """커넥터 정리, VectorStore 연결 해제"""
        await self._vector_store.disconnect()
        self._emit_event("cond.b.021.shutdown")
        return Ok(None)

    def get_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            id="COND-021", version="1.0.0",
            capabilities=["notion_import", "obsidian_import", "link_resolution", "backlink_creation"]
        )
```

---

## E10. Configuration

> LOCK (종합명세 §공통 / LOCK-CD-10): ModuleConfig 표준 필드

```python
class Cond021Config(ModuleConfig):
    """COND-021 모듈 설정"""
    # ModuleConfig 상속 (enabled, priority, max_concurrent, timeout_ms, retry_policy)
    enabled: bool = True
    priority: Literal["critical", "high", "medium", "low"] = "high"
    max_concurrent: int = 2
    timeout_ms: int = 120000
    retry_policy: RetryPolicy = RetryPolicy(max_retries=2, backoff_ms=2000)

    # COND-021 전용 설정
    notion_rate_limit_rps: int = 3
    notion_retry_on_429: bool = True
    obsidian_file_extensions: list[str] = [".md", ".markdown"]
    chunk_strategy: Literal["semantic", "fixed", "paragraph"] = "semantic"
    chunk_max_tokens: int = 512
    embedding_batch_size: int = 32
    dedup_enabled: bool = True
    max_import_per_session: int = 5000
    link_resolution_timeout_ms: int = 10000
    preserve_frontmatter: bool = True
```
