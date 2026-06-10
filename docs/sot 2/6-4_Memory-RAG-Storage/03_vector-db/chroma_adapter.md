# ChromaVectorStore 어댑터 구현 상세 (V1)

> **Phase**: P1-3 산출물
> **정본 출처**:
>   - D2.0-06 §2.2 (LOCK-MR-012: V1 Chroma), §2.2-A (LOCK-MR-014: 4메서드)
>   - D6 v3.0.0 §4.3 VectorStoreAdapterSchema, §7-A.1 KB_EMBEDDING_RECORD
>   - Part2 V1-Phase 2 항목3 (Chroma Vector DB)
> **작성일**: 2026-04-13
> **세션**: P1-3
> **권한 체인**: RULE 1.3 > PLAN 3.0 > D2.0-06 (LOCK) > D6 (Schema SOT) > P0-3/P0-4 (전략/ABC) > 본 문서 (IMPL-DETAIL)
>
> **LOCK 준수**:
>   - LOCK-MR-011: BGE-M3 1024dim 원본 + Matryoshka 256dim 검색용
>   - LOCK-MR-012: V1 Chroma 로컬 임베디드
>   - LOCK-MR-014: upsert/search/delete/get_by_id 4개 메서드
>   - LOCK-MR-015: Deny 판정 시 벡터 삽입 절대 금지
>   - LOCK-MR-017: project_id 기반 격리, 프로젝트 간 데이터 혼합 금지
>
> **입력 파일**:
>   - P0-3: `chroma_collection_strategy.md` (단일 컬렉션 + 메타데이터 필터 전략)
>   - P0-4: `vectorstore_abc.py` (VectorStoreABC 4메서드 + ChromaAdapter 스텁)
>   - P0-1: `MemoryRecordSchema.md` (MemoryRecordSchema 20필드 정본)
>   - P1-1: `L0_session_memory_crud.md` (L0 CRUD — §11.2 P1-3 접점)
>   - P1-2: `L1_project_memory_crud.md` (L1 CRUD — §12.2 P1-3 접점)
>
> **이전 단계 이월 사항**: P1-1/P1-2 모두 이월 없음. P0-4 ChromaAdapter 스텁의 `NotImplementedError` 4건을 본 세션에서 FULL 구현.

---

## 목차

1. [ChromaVectorStore 클래스 설계](#1-chromavectorstore-클래스-설계)
2. [Chroma 클라이언트 초기화](#2-chroma-클라이언트-초기화)
3. [BGE-M3 임베딩 연동](#3-bge-m3-임베딩-연동)
4. [upsert() 구현](#4-upsert-구현)
5. [search() 구현](#5-search-구현)
6. [delete() 구현](#6-delete-구현)
7. [get_by_id() 구현](#7-get_by_id-구현)
8. [BM25 인덱스 동기화](#8-bm25-인덱스-동기화)
9. [V1 RAG 운영 한계 적용](#9-v1-rag-운영-한계-적용)
10. [에러 코드 정의](#10-에러-코드-정의)
11. [복구/재시도 전략](#11-복구재시도-전략)
12. [로깅 포맷](#12-로깅-포맷)
13. [단위 테스트 시나리오](#13-단위-테스트-시나리오)
14. [Phase 2 통합 테스트](#14-phase-2-통합-테스트)
15. [세션 간 인터페이스 cross-check](#15-세션-간-인터페이스-cross-check)
16. [LOCK-MR 참조 추적표](#16-lock-mr-참조-추적표)
17. [교차 참조 블록](#17-교차-참조-블록)
18. [I-3 SHELL→FULL 전환 확인](#18-i-3-shellfull-전환-확인)

---

## 1. ChromaVectorStore 클래스 설계

### 1.1 클래스 계층

```
VectorStoreABC (P0-4 vectorstore_abc.py)
  ├── __init__(adapter_id, backend, mode, embedding_model, dimension, collection_name, version_tier, connection_url?)
  ├── _enforce_project_filter(project_id, filters?) → dict
  ├── _check_policy_before_upsert(records) → None | ValueError
  ├── upsert(records, project_id) → None              [abstract]
  ├── search(query_vector, project_id, top_k=10, filters?) → list[VectorRecord]  [abstract]
  ├── delete(ids, project_id) → None                   [abstract]
  └── get_by_id(id, project_id) → VectorRecord | None  [abstract]
        │
        ▼ 상속
ChromaVectorStore (본 문서)
  ├── __init__(persist_dir, adapter_id, embedding_model, dimension, collection_name, version_tier)
  ├── _init_collection() → chromadb.Collection
  ├── _get_embedding_fn() → EmbeddingFunction
  ├── _to_chroma_format(record, project_id) → dict
  ├── _from_chroma_result(result_row) → VectorRecord
  ├── _check_capacity(project_id) → None | CapacityError
  ├── _sync_bm25_index(action, project_id, records?) → None
  ├── upsert(records, project_id) → None              [구현]
  ├── search(query_vector, project_id, top_k=10, filters?) → list[VectorRecord]  [구현]
  ├── delete(ids, project_id) → None                   [구현]
  └── get_by_id(id, project_id) → VectorRecord | None  [구현]
```

### 1.2 D6 VectorStoreAdapterSchema 필드 매핑

| D6 필드 | ChromaVectorStore 기본값 | 타입 | 근거 |
|---------|------------------------|------|------|
| `adapter_id` | `"vs_chroma_local"` | string | D6 §4.3 예시 |
| `backend` | `"chroma"` | string | LOCK-MR-012 |
| `mode` | `"embedded"` | string | D2.0-06 §2.2: 로컬 임베디드 |
| `embedding_model` | `"bge-m3"` | string | LOCK-MR-011 |
| `dimension` | `256` | integer | Matryoshka 256dim 검색용 (P0-3 §2.1) |
| `collection_name` | `"vamos_memory"` | string | P0-3 §3.2 결정 |
| `connection_url` | `None` | string? | 임베디드 모드 — 연결 URL 불필요 |
| `version_tier` | `"V1"` | string | V1 scope |

### 1.3 config.toml 연동

```toml
[memory.vector]
backend = "chroma"               # 어댑터 선택 (LOCK-MR-012: V1=chroma)
mode = "embedded"                # 운영 모드
persist_dir = "data/chroma/"     # 영속 경로 (P0-3 §1.1)
collection_name = "vamos_memory" # 컬렉션 이름
embedding_model = "bge-m3"       # 임베딩 모델 (LOCK-MR-011)
search_dimension = 256           # 검색용 벡터 차원 (Matryoshka)
storage_dimension = 1024         # 원본 벡터 차원
default_top_k = 20               # 파이프라인 레벨 top_k (Part2, LOCK=N 조정 가능)
similarity_threshold = 0.75      # LOCK-MR-009
alpha = 0.7                      # Dense 가중치 (LOCK-MR-008)
fusion_method = "weighted_sum"   # V1 기본: 가중 합산 (RRF 전환 가능)
max_docs_per_project = 15        # R-64-5
max_chunks_per_doc = 30          # R-64-5
```

> **어댑터 교체 제약 (D2.0-06 L184)**: `backend` 값을 `"qdrant"`로 변경하면 QdrantAdapter가 로드되며, 비즈니스 로직 수정 없이 전환 가능.

---

## 2. Chroma 클라이언트 초기화

### 2.1 PersistentClient 생성

```python
import chromadb
from chromadb.config import Settings

class ChromaVectorStore(VectorStoreABC):

    def __init__(
        self,
        *,
        persist_dir: str = "data/chroma/",
        adapter_id: str = "vs_chroma_local",
        embedding_model: str = "bge-m3",
        dimension: int = 256,
        collection_name: str = "vamos_memory",
        version_tier: str = "V1",
    ) -> None:
        super().__init__(
            adapter_id=adapter_id,
            backend="chroma",
            mode="embedded",
            embedding_model=embedding_model,
            dimension=dimension,
            collection_name=collection_name,
            version_tier=version_tier,
        )
        self.persist_dir = persist_dir

        # Chroma PersistentClient — 단일 writer 패턴 (D2.0-06 §2.2 L161)
        self._client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=False,        # 운영 안전: 컬렉션 리셋 금지
            ),
        )

        # 컬렉션 생성/접속 — P0-3 §3.2 단일 컬렉션 전략
        self._collection = self._init_collection()

        # BM25 인덱스 초기화 (§8 참조)
        self._bm25_index: dict[str, object] = {}  # project_id → BM25 인스턴스 (delete_by_project 직접 참조용)
        self._bm25_manager = BM25IndexManager()   # §8.1 — _sync_bm25_index(rebuild/remove_project) 대상 (delete_by_project 직접 참조용)
        self._bm25_manager = BM25IndexManager()   # §8.1 — _sync_bm25_index(rebuild/remove_project) 대상
```

### 2.2 컬렉션 초기화

```python
    def _init_collection(self) -> chromadb.Collection:
        """단일 컬렉션 vamos_memory 생성/접속.

        P0-3 §3.2 결정: 단일 컬렉션 + 메타데이터 필터.
        hnsw:space="cosine" — 코사인 유사도 기반 검색.
        """
        return self._client.get_or_create_collection(
            name=self.collection_name,
            metadata={
                "hnsw:space": "cosine",           # 코사인 거리
                "hnsw:construction_ef": 128,      # V1 기본 HNSW 파라미터
                "hnsw:search_ef": 64,             # V1 기본 검색 효율
            },
        )
```

### 2.3 시간복잡도

| 연산 | 시간복잡도 | 비고 |
|------|-----------|------|
| `__init__` (PersistentClient) | O(1) | SQLite 파일 열기 |
| `get_or_create_collection` | O(1) | 메타데이터 조회/생성 |
| HNSW 인덱스 로딩 | O(N) amortized | N = 현재 벡터 수, 최초 로딩 시 |

---

## 3. BGE-M3 임베딩 연동

### 3.1 이중 벡터 생성 (LOCK-MR-011)

```python
from FlagEmbedding import BGEM3FlagModel

class BGEm3Embedder:
    """BGE-M3 임베딩 생성기.

    LOCK-MR-011: 1024dim 원본 + Matryoshka 256dim 검색용.
    6-Stage RAG Pipeline Stage 3(Embed)에서 호출.
    """

    def __init__(self, model_name: str = "BAAI/bge-m3"):
        self._model = BGEM3FlagModel(model_name, use_fp16=True)

    def encode(self, texts: list[str]) -> dict[str, list[list[float]]]:
        """텍스트 → 이중 벡터 생성.

        Returns:
            {
                "dense_1024": list[list[float]],   # 원본 1024dim (SQLite BLOB 저장)
                "dense_256": list[list[float]],     # Matryoshka 256dim (Chroma 저장)
            }
        """
        # BGE-M3 Matryoshka 벡터 생성
        embeddings_1024 = self._model.encode(
            texts,
            batch_size=12,
            max_length=8192,
        )["dense_vecs"]  # 1024dim 전체

        # Matryoshka 차원 축소: 1024dim → 256dim (앞 256개 차원 슬라이싱)
        embeddings_256 = [vec[:256] for vec in embeddings_1024]

        # L2 정규화 (코사인 유사도 사용 시 필수)
        import numpy as np
        embeddings_256_norm = [
            (np.array(v) / np.linalg.norm(v)).tolist()
            for v in embeddings_256
        ]

        return {
            "dense_1024": [v.tolist() if hasattr(v, 'tolist') else v for v in embeddings_1024],
            "dense_256": embeddings_256_norm,
        }

    def encode_query(self, query: str) -> list[float]:
        """단일 쿼리 → 256dim 검색 벡터 생성."""
        result = self.encode([query])
        return result["dense_256"][0]
```

### 3.2 임베딩 생성 시점

```
MemoryRecord 생성 요청
    │
    ▼
[D7 PolicyCheck] → deny → 차단 (벡터 미생성)
    │ allow/restrict
    ▼
[BGEm3Embedder.encode(content_summary)]
    ├── dense_1024 → SQLite KB_EMBEDDING_RECORD BLOB 저장 (D6 §7-A.1)
    └── dense_256  → ChromaVectorStore.upsert() → Chroma 컬렉션 저장
```

### 3.3 벡터 차원 검증

```python
    def _validate_vector_dim(self, vector: list[float]) -> None:
        """벡터 차원 검증. LOCK-MR-011 준수 확인.

        Chroma 컬렉션에 저장되는 벡터는 검색용 256dim.
        """
        if len(vector) != self.dimension:
            raise VEC_ERR_003(
                f"벡터 차원 불일치: expected={self.dimension}, "
                f"actual={len(vector)} (LOCK-MR-011)"
            )
```

---

## 4. upsert() 구현

### 4.1 전체 흐름

```python
    def upsert(
        self,
        records: list[VectorRecord],
        project_id: str,
    ) -> None:
        """Chroma upsert — 벡터 레코드 삽입/갱신.

        D2.0-06 §2.2-A: upsert(records: VectorRecord[]) → void

        절차:
          1. policy_decision 검사 — deny 시 즉시 거부 (LOCK-MR-015)
          2. project_id 격리 필터 강제 (LOCK-MR-017)
          3. 프로젝트 용량 검사 (R-64-5)
          4. 벡터 차원 검증 (LOCK-MR-011)
          5. Chroma collection.upsert 실행
          6. BM25 인덱스 동기화
          7. 감사 로그 기록

        시간복잡도: O(B * log N)
          B = len(records) (배치 크기)
          N = 컬렉션 내 벡터 수 (HNSW 삽입)

        Raises:
          ValueError: deny 레코드 포함 시 (LOCK-MR-015)
          ValueError: project_id 누락 시 (LOCK-MR-017)
          VEC_ERR_004: 용량 초과 시 (R-64-5)
          VEC_ERR_003: 벡터 차원 불일치 시 (LOCK-MR-011)
        """
        # Step 1: 정책 검사 (LOCK-MR-015, R-64-3)
        self._check_policy_before_upsert(records)

        # Step 2: project_id 격리 (LOCK-MR-017)
        filters = self._enforce_project_filter(project_id)

        # Step 3: 용량 검사 (R-64-5)
        self._check_capacity(project_id, additional_count=len(records))

        # Step 4: 벡터 차원 검증 (LOCK-MR-011)
        for record in records:
            self._validate_vector_dim(record.vector)

        # Step 5: Chroma upsert — 배치 처리
        ids = []
        embeddings = []
        documents = []
        metadatas = []

        for record in records:
            # 메타데이터에 project_id 강제 주입 (P0-3 §4.1)
            metadata = dict(record.metadata)
            metadata["project_id"] = project_id
            metadata["scope"] = metadata.get("scope", "L0")
            metadata["memory_type"] = metadata.get("memory_type", "B-4")
            metadata["record_id"] = record.id
            metadata["policy_decision"] = record.policy_decision.value

            ids.append(record.id)
            embeddings.append(record.vector)
            documents.append(record.document)
            metadatas.append(metadata)

        self._collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

        # Step 6: BM25 인덱스 동기화 (§8) — VEC_ERR_009: 실패해도 벡터는 유효, 전파 금지
        try:
            self._sync_bm25_index("upsert", project_id, records)
        except Exception as e:
            self._log_operation("BM25_SYNC_FAIL", project_id, error_code="VEC_ERR_009", severity="WARNING", detail=str(e))
            # 벡터는 이미 정상 저장됨 (VEC_ERR_009 WARNING) — 예외 전파 금지

        # Step 7: 감사 로그 (§12 R-01-7 포맷)
        self._log_operation("UPSERT", project_id, count=len(records), ids=ids)
```

### 4.2 policy_decision별 동작 상세

| policy_decision | 동작 | 벡터 삽입 | 메타데이터 | 근거 |
|----------------|------|----------|-----------|------|
| `allow` | 정상 삽입 | 허용 | `policy_decision="allow"` | P0-3 §7.1 |
| `restrict` | 마스킹된 content_summary로 임베딩 생성 후 삽입 | 허용 (마스킹 후) | `policy_decision="restrict"`, `masked=true` 호출부 보장 | P0-3 §7.1, LOCK-MR-019 |
| `deny` | **즉시 거부** — ValueError 발생, 어떤 삽입도 불가 | **절대 금지** | 삽입 안 됨 | **LOCK-MR-015**, R-64-3 |

> **중요**: `restrict` 레코드의 마스킹은 **호출부(L0/L1 CRUD 계층)에서 완료**한 상태로 전달됨. ChromaVectorStore는 마스킹 후 content_summary를 그대로 임베딩/저장함. P1-7(PII 마스킹)에서 마스킹 파이프라인 상세 정의.

### 4.3 배치 처리 전략

```
upsert 배치 크기 제한:
  - V1 기본: max_batch_size = 100 (config.toml [memory.vector].max_batch_size)
  - 초과 시: 100건 단위 분할 처리 (순차)
  - 근거: Chroma 임베디드 모드의 SQLite 단일 writer 패턴 (D2.0-06 §2.2 L161)

def upsert(self, records, project_id):
    ...
    MAX_BATCH = 100
    for i in range(0, len(ids), MAX_BATCH):
        batch_ids = ids[i:i+MAX_BATCH]
        batch_emb = embeddings[i:i+MAX_BATCH]
        batch_doc = documents[i:i+MAX_BATCH]
        batch_meta = metadatas[i:i+MAX_BATCH]
        self._collection.upsert(
            ids=batch_ids,
            embeddings=batch_emb,
            documents=batch_doc,
            metadatas=batch_meta,
        )
```

---

## 5. search() 구현

### 5.1 전체 흐름

```python
    def search(
        self,
        query_vector: list[float],
        project_id: str,
        top_k: int = 10,
        filters: Optional[dict] = None,
    ) -> list[VectorRecord]:
        """Chroma search — 벡터 유사도 검색.

        D2.0-06 §2.2-A: search(query_vector, top_k=10, filters) → VectorRecord[]

        절차:
          1. project_id 격리 필터 강제 (LOCK-MR-017)
          2. 쿼리 벡터 차원 검증 (LOCK-MR-011: 256dim)
          3. Chroma collection.query 실행
          4. cosine distance → similarity 변환 (P0-3 §6.1)
          5. similarity threshold 필터링 (LOCK-MR-009: >= 0.75)
          6. VectorRecord 변환/반환

        top_k 기본값=10 (D2.0-06 §2.2-A L177).
        파이프라인 레벨에서 config.toml default_top_k=20으로 오버라이드 가능.

        시간복잡도: O(log N + K)
          N = 컬렉션 내 벡터 수 (HNSW 검색)
          K = top_k

        Returns:
          list[VectorRecord]: 유사도 내림차순 정렬, threshold 이상만 포함
        """
        # Step 1: project_id 격리 (LOCK-MR-017)
        filters = self._enforce_project_filter(project_id, filters)

        # Step 2: 쿼리 벡터 차원 검증
        self._validate_vector_dim(query_vector)

        # Step 3: Chroma query — where 절에 project_id 필터 적용
        #   Chroma where 절 구성: {"project_id": project_id} + 추가 필터
        where_clause = {"project_id": filters["project_id"]}

        # 추가 필터 병합 (scope, memory_type 등)
        extra_filters = {k: v for k, v in filters.items() if k != "project_id"}
        if extra_filters:
            # Chroma $and 연산자로 다중 필터 결합
            where_clause = {
                "$and": [
                    {"project_id": filters["project_id"]},
                    *[{k: v} for k, v in extra_filters.items()],
                ]
            }

        results = self._collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            where=where_clause,
            include=["distances", "metadatas", "documents", "embeddings"],
        )

        # Step 4+5: distance → similarity 변환 + threshold 필터링
        #   Chroma hnsw:space="cosine" → distance = 1 - cosine_similarity
        #   따라서: similarity = 1 - distance (P0-3 §6.1)
        #   LOCK-MR-009: threshold = 0.75
        threshold = 0.75  # LOCK-MR-009

        output: list[VectorRecord] = []
        if results and results["ids"] and results["ids"][0]:
            for idx, record_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][idx]
                similarity = 1.0 - distance  # P0-3 §6.1 검증 완료

                if similarity < threshold:
                    continue  # threshold 미달 — 결과에서 제외

                metadata = results["metadatas"][0][idx] if results["metadatas"] else {}
                document = results["documents"][0][idx] if results["documents"] else ""
                embedding = results["embeddings"][0][idx] if results["embeddings"] else []

                record = VectorRecord(
                    id=record_id,
                    project_id=metadata.get("project_id", project_id),
                    document=document,
                    vector=embedding,
                    metadata=metadata,
                    policy_decision=PolicyDecision(
                        metadata.get("policy_decision", "deny")  # fail-closed: 메타 누락/손상 시 deny (LOCK-MR-015), allow로 승격 금지
                    ),
                )
                # 유사도 점수를 metadata에 첨부 (후속 Rerank 단계 참조용)
                record.metadata["_similarity"] = round(similarity, 6)
                output.append(record)

        # 유사도 내림차순 정렬
        output.sort(key=lambda r: r.metadata.get("_similarity", 0), reverse=True)

        # 감사 로그
        self._log_operation(
            "SEARCH", project_id,
            top_k=top_k, results_count=len(output),
            threshold_applied=threshold,
        )

        return output
```

### 5.2 Hybrid Search 통합 접점

ChromaVectorStore.search()는 **Dense 검색** 부분만 담당. Hybrid Search는 애플리케이션 레벨에서 구현 (P0-3 §5.2):

```
[Hybrid Search 호출 (P1-11 소관)]
    ├── ChromaVectorStore.search(query_vec_256, project_id, top_k=20)  ← Dense
    └── BM25Search.search(query_text, project_id, top_k=20)           ← Sparse
    │
    ▼ 결과 융합
[가중 합산 (V1 기본)]
    score = α(0.7) × dense_similarity + (1-α)(0.3) × sparse_score
    → threshold >= 0.75 필터링 (LOCK-MR-009)
    → Top-K rerank=5 (Cross-Encoder)
```

> **본 세션 범위**: ChromaVectorStore.search()의 Dense 검색 구현. Hybrid Search 결합은 P1-11에서 정의.

---

## 6. delete() 구현

### 6.1 전체 흐름

```python
    def delete(
        self,
        ids: list[str],
        project_id: str,
    ) -> None:
        """Chroma delete — 벡터 레코드 삭제.

        D2.0-06 §2.2-A: delete(ids: str[]) → void

        절차:
          1. project_id 격리 필터 강제 (LOCK-MR-017)
          2. 대상 레코드 소유권 검증 (크로스 프로젝트 삭제 차단)
          3. Chroma collection.delete 실행
          4. BM25 인덱스 동기화
          5. 감사 로그 기록

        시간복잡도: O(B * log N)
          B = len(ids) (삭제 대상 수)
          N = 컬렉션 내 벡터 수

        Raises:
          ValueError: project_id 누락 시 (LOCK-MR-017)
          VEC_ERR_005: 크로스 프로젝트 삭제 시도 시
        """
        # Step 1: project_id 격리 (LOCK-MR-017)
        self._enforce_project_filter(project_id)

        # Step 2: 소유권 검증 — 삭제 대상이 해당 project_id 소유인지 확인
        existing = self._collection.get(
            ids=ids,
            include=["metadatas"],
        )

        if existing and existing["ids"]:
            for idx, existing_id in enumerate(existing["ids"]):
                meta = existing["metadatas"][idx] if existing["metadatas"] else {}
                if meta.get("project_id") != project_id:
                    raise VEC_ERR_005(
                        f"크로스 프로젝트 삭제 차단: record_id={existing_id}, "
                        f"owner={meta.get('project_id')}, "
                        f"requester={project_id} (LOCK-MR-017)"
                    )

        # Step 3: Chroma delete — where 절로 project_id 이중 검증
        self._collection.delete(
            ids=ids,
            where={"project_id": project_id},
        )

        # Step 4: BM25 인덱스 동기화
        self._sync_bm25_index("delete", project_id)

        # Step 5: 감사 로그
        self._log_operation("DELETE", project_id, count=len(ids), ids=ids)
```

### 6.2 프로젝트 삭제 시 벡터 일괄 삭제

```python
    def delete_by_project(self, project_id: str) -> int:
        """프로젝트 전체 벡터 삭제.

        P0-3 §4.4: 프로젝트 삭제 시 해당 project_id의 모든 벡터 bulk delete.
        D2.0-06 L1865: "프로젝트 삭제 시 관련 메모리 완전 삭제 (GDPR 준수)"

        Returns: 삭제된 벡터 수
        """
        self._enforce_project_filter(project_id)

        # 현재 프로젝트의 벡터 수 조회
        existing = self._collection.get(
            where={"project_id": project_id},
            include=[],
        )
        count = len(existing["ids"]) if existing and existing["ids"] else 0

        if count > 0:
            self._collection.delete(
                where={"project_id": project_id},
            )

        # BM25 인덱스에서 해당 프로젝트 제거
        self._bm25_index.pop(project_id, None)

        self._log_operation("DELETE_PROJECT", project_id, count=count)
        return count
```

---

## 7. get_by_id() 구현

### 7.1 전체 흐름

```python
    def get_by_id(
        self,
        id: str,
        project_id: str,
    ) -> Optional[VectorRecord]:
        """Chroma get_by_id — 단일 레코드 조회.

        D2.0-06 §2.2-A: get_by_id(id: str) → VectorRecord | None

        절차:
          1. project_id 격리 필터 강제 (LOCK-MR-017)
          2. Chroma collection.get 실행 (ids + where)
          3. project_id 불일치 시 None 반환 (타 프로젝트 접근 차단)
          4. VectorRecord 변환/반환

        시간복잡도: O(1)
          Chroma ID 조회는 해시 기반.

        Returns:
          VectorRecord if found and project_id matches, else None
        """
        # Step 1: project_id 격리 (LOCK-MR-017)
        self._enforce_project_filter(project_id)

        # Step 2: Chroma get — where 절로 project_id 필터 동시 적용
        result = self._collection.get(
            ids=[id],
            where={"project_id": project_id},
            include=["metadatas", "documents", "embeddings"],
        )

        # Step 3: 결과 없음 → None (project_id 불일치 포함)
        if not result or not result["ids"]:
            return None

        # Step 4: VectorRecord 변환
        metadata = result["metadatas"][0] if result["metadatas"] else {}
        document = result["documents"][0] if result["documents"] else ""
        embedding = result["embeddings"][0] if result["embeddings"] else []

        return VectorRecord(
            id=result["ids"][0],
            project_id=metadata.get("project_id", project_id),
            document=document,
            vector=embedding,
            metadata=metadata,
            policy_decision=PolicyDecision(
                metadata.get("policy_decision", "allow")
            ),
        )
```

---

## 8. BM25 인덱스 동기화

> P0-3 §5.3: BM25 인덱스는 벡터 upsert/delete 시 동기 갱신. project_id별 격리.

### 8.1 인덱스 관리 구조

```python
from rank_bm25 import BM25Okapi
from typing import Optional

class BM25IndexManager:
    """project_id별 BM25 인덱스 관리.

    Chroma Dense 검색 + BM25 Sparse 검색의 Hybrid Search 지원.
    P0-3 §5.3 설계 기반.
    """

    def __init__(self):
        self._indices: dict[str, dict] = {}
        # 구조: { project_id: { "corpus": [...], "ids": [...], "bm25": BM25Okapi } }

    def rebuild(self, project_id: str, documents: list[str], ids: list[str]) -> None:
        """BM25 인덱스 재구축.

        Args:
            project_id: 프로젝트 ID
            documents: content_summary 텍스트 목록
            ids: record_id 목록 (documents와 1:1 대응)
        """
        tokenized = [doc.split() for doc in documents]  # V1: 공백 토크나이저
        self._indices[project_id] = {
            "corpus": documents,
            "ids": ids,
            "bm25": BM25Okapi(tokenized) if tokenized else None,
        }

    def search(
        self,
        project_id: str,
        query: str,
        top_k: int = 20,
    ) -> list[tuple[str, float]]:
        """BM25 키워드 검색.

        Returns:
            list[(record_id, bm25_score)] — 점수 내림차순 정렬
        """
        index = self._indices.get(project_id)
        if not index or not index["bm25"]:
            return []

        tokenized_query = query.split()
        scores = index["bm25"].get_scores(tokenized_query)

        scored = [(index["ids"][i], float(scores[i])) for i in range(len(scores))]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def remove_project(self, project_id: str) -> None:
        """프로젝트 BM25 인덱스 제거."""
        self._indices.pop(project_id, None)
```

### 8.2 ChromaVectorStore 내 동기화

```python
    def _sync_bm25_index(self, action: str, project_id: str, records=None) -> None:
        """BM25 인덱스 동기화. upsert/delete 후 호출.

        V1 구현: 전체 재구축 (프로젝트당 최대 450 벡터 — 성능 문제 없음).
        V2+에서 증분 업데이트로 최적화 가능.
        """
        # 해당 project_id의 전체 문서 재조회
        all_docs = self._collection.get(
            where={"project_id": project_id},
            include=["documents"],
        )

        if all_docs and all_docs["ids"]:
            self._bm25_manager.rebuild(
                project_id,
                documents=all_docs["documents"],
                ids=all_docs["ids"],
            )
        else:
            self._bm25_manager.remove_project(project_id)
```

---

## 9. V1 RAG 운영 한계 적용

> R-64-5 (D2.0-06 §1.1, §4.1): 문서 15개/프로젝트, 청크 30개/문서
> P0-3 §8: 프로젝트당 최대 450 벡터 (15 x 30)

### 9.1 용량 검사

```python
    # 상수 정의
    MAX_DOCS_PER_PROJECT = 15      # R-64-5: D2.0-06 §4.1
    MAX_CHUNKS_PER_DOC = 30        # R-64-5: D2.0-06 §4.1
    MAX_VECTORS_PER_PROJECT = 450  # 15 x 30

    def _check_capacity(
        self,
        project_id: str,
        additional_count: int = 0,
    ) -> None:
        """프로젝트 벡터 용량 검사. R-64-5 상한 초과 시 거부.

        P0-3 §8.2: 애플리케이션 레벨 검사.

        Raises:
            VEC_ERR_004: 용량 초과
        """
        current = self._collection.count()  # 전체 컬렉션
        # project_id별 카운트
        project_vectors = self._collection.get(
            where={"project_id": project_id},
            include=[],
        )
        current_project = len(project_vectors["ids"]) if project_vectors and project_vectors["ids"] else 0

        if current_project + additional_count > self.MAX_VECTORS_PER_PROJECT:
            raise VEC_ERR_004(
                f"프로젝트 벡터 용량 초과: project_id={project_id}, "
                f"current={current_project}, adding={additional_count}, "
                f"max={self.MAX_VECTORS_PER_PROJECT} (R-64-5)"
            )
```

### 9.2 V3 상향 경로

> D2.0-06 §4.1: "V3 상향은 07 Approval/Cost 게이트 승인 후에만 허용"

```
V1: max=450 (15 docs × 30 chunks)
V2: config.toml 설정 변경 가능 (운영 결정)
V3: D7 ApprovalGate 승인 후 상향 (LOCK-MR-016 연동)
```

---

## 10. 에러 코드 정의

| 코드 | 이름 | 심각도 | 설명 | LOCK |
|------|------|--------|------|------|
| `VEC_ERR_001` | POLICY_DENY_INSERT | ERROR | Deny 판정 벡터 삽입 시도 | LOCK-MR-015 |
| `VEC_ERR_002` | PROJECT_ID_MISSING | ERROR | project_id 누락 | LOCK-MR-017 |
| `VEC_ERR_003` | DIMENSION_MISMATCH | ERROR | 벡터 차원 불일치 (expected 256) | LOCK-MR-011 |
| `VEC_ERR_004` | CAPACITY_EXCEEDED | WARNING | 프로젝트 벡터 용량 초과 | R-64-5 |
| `VEC_ERR_005` | CROSS_PROJECT_DELETE | ERROR | 크로스 프로젝트 삭제 시도 | LOCK-MR-017 |
| `VEC_ERR_006` | COLLECTION_INIT_FAIL | CRITICAL | Chroma 컬렉션 초기화 실패 | — |
| `VEC_ERR_007` | EMBEDDING_FAIL | ERROR | BGE-M3 임베딩 생성 실패 | LOCK-MR-011 |
| `VEC_ERR_008` | CHROMA_QUERY_FAIL | ERROR | Chroma 쿼리 실행 실패 | — |
| `VEC_ERR_009` | BM25_SYNC_FAIL | WARNING | BM25 인덱스 동기화 실패 | — |
| `VEC_ERR_010` | UPSERT_BATCH_PARTIAL | WARNING | 배치 upsert 중 일부 실패 | — |
| `VEC_ERR_011` | PERSIST_DIR_ACCESS | CRITICAL | 영속 경로 접근 불가 | — |
| `VEC_ERR_012` | RECORD_NOT_FOUND | INFO | get_by_id 결과 없음 | — |

### 10.1 에러 코드 구조

```python
class VectorStoreError(Exception):
    """VectorStore 에러 기본 클래스."""
    def __init__(self, code: str, message: str, severity: str = "ERROR"):
        self.code = code
        self.message = message
        self.severity = severity
        super().__init__(f"[{code}] {message}")

# 구체 에러 클래스
class VEC_ERR_001(VectorStoreError):
    def __init__(self, msg): super().__init__("VEC_ERR_001", msg, "ERROR")

class VEC_ERR_003(VectorStoreError):
    def __init__(self, msg): super().__init__("VEC_ERR_003", msg, "ERROR")

class VEC_ERR_004(VectorStoreError):
    def __init__(self, msg): super().__init__("VEC_ERR_004", msg, "WARNING")

class VEC_ERR_005(VectorStoreError):
    def __init__(self, msg): super().__init__("VEC_ERR_005", msg, "ERROR")
```

---

## 11. 복구/재시도 전략

### 11.1 복구 흐름도

```
[ChromaVectorStore 연산]
    │
    ├── 성공 → 정상 완료 + 감사 로그
    │
    └── 실패
        │
        ├── VEC_ERR_006 (컬렉션 초기화 실패)
        │   └── 재시도: 3회, 지수 백오프 (1s, 2s, 4s)
        │       ├── 성공 → 정상 계속
        │       └── 3회 실패 → CRITICAL 에스컬레이션
        │           confidence_penalty: 0.0 (서비스 불가)
        │
        ├── VEC_ERR_001 (Deny 삽입 시도)
        │   └── 재시도 불가 — 즉시 거부 (LOCK-MR-015)
        │       confidence_penalty: N/A (정상 거부)
        │
        ├── VEC_ERR_008 (Chroma 쿼리 실패)
        │   └── 재시도: 2회, 고정 간격 (500ms)
        │       ├── 성공 → 정상 반환
        │       └── 2회 실패 → fallback: 빈 결과 + WARNING 로그
        │           confidence_penalty: -0.3
        │
        ├── VEC_ERR_004 (용량 초과)
        │   └── 재시도 불가 — 사용자 알림 반환
        │       confidence_penalty: -0.1
        │
        ├── VEC_ERR_009 (BM25 동기화 실패)
        │   └── 재시도: 1회
        │       ├── 성공 → 정상 (벡터 삽입은 이미 완료)
        │       └── 실패 → WARNING 로그, 벡터 삽입은 유효
        │           confidence_penalty: -0.05
        │
        └── VEC_ERR_011 (영속 경로 접근 불가)
            └── 재시도: 1회 (경로 존재 확인 + 생성)
                ├── 성공 → 정상 계속
                └── 실패 → CRITICAL 에스컬레이션
                    confidence_penalty: 0.0 (서비스 불가)
```

### 11.2 재시도 정책 표

| 에러 코드 | 재시도 | 백오프 | 최대 시도 | 실패 시 동작 | confidence_penalty |
|-----------|--------|--------|----------|-------------|-------------------|
| VEC_ERR_001 | 불가 | — | 1 | 즉시 거부 | N/A |
| VEC_ERR_002 | 불가 | — | 1 | 즉시 거부 | N/A |
| VEC_ERR_003 | 불가 | — | 1 | 즉시 거부 | N/A |
| VEC_ERR_004 | 불가 | — | 1 | 사용자 알림 | -0.1 |
| VEC_ERR_005 | 불가 | — | 1 | 즉시 거부 | N/A |
| VEC_ERR_006 | 가능 | 지수 (1s,2s,4s) | 3 | CRITICAL 에스컬레이션 | 0.0 |
| VEC_ERR_007 | 가능 | 고정 (1s) | 2 | 에스컬레이션 | -0.2 |
| VEC_ERR_008 | 가능 | 고정 (500ms) | 2 | 빈 결과 + WARNING | -0.3 |
| VEC_ERR_009 | 가능 | 즉시 | 1 | WARNING (벡터는 유효) | -0.05 |
| VEC_ERR_010 | 가능 | 즉시 | 1 | 부분 성공 + WARNING | -0.15 |
| VEC_ERR_011 | 가능 | 즉시 | 1 | CRITICAL 에스컬레이션 | 0.0 |

### 11.3 에스컬레이션 페이로드

```json
{
  "escalation_type": "VECTOR_STORE_FAILURE",
  "source_domain": "6-4_Memory-RAG-Storage",
  "source_component": "ChromaVectorStore",
  "error_code": "VEC_ERR_006",
  "severity": "CRITICAL",
  "timestamp_utc": "2026-04-13T09:35:00Z",
  "project_id": "proj_abc123",
  "retry_count": 3,
  "retry_exhausted": true,
  "context": {
    "persist_dir": "data/chroma/",
    "collection_name": "vamos_memory",
    "last_error_message": "SQLite database is locked"
  },
  "recommended_action": "Chroma 프로세스 재시작 또는 persist_dir 접근 권한 확인",
  "confidence_penalty": 0.0,
  "target_handler": "6-5_SDAR"
}
```

---

## 12. 로깅 포맷

### 12.1 R-01-7 중첩 JSON 포맷

```json
{
  "log_id": "VEC-2026-04-13T09:35:00.123Z-001",
  "timestamp_utc": "2026-04-13T09:35:00.123Z",
  "level": "INFO",
  "domain": "6-4_Memory-RAG-Storage",
  "component": "ChromaVectorStore",
  "operation": "UPSERT",
  "session_id": "P1-3",
  "details": {
    "project_id": "proj_abc123",
    "record_count": 5,
    "record_ids": ["rec_001", "rec_002", "rec_003", "rec_004", "rec_005"],
    "collection_name": "vamos_memory",
    "vector_dim": 256,
    "embedding_model": "bge-m3",
    "policy_decisions": {
      "allow": 4,
      "restrict": 1,
      "deny": 0
    },
    "batch_index": 1,
    "batch_total": 1,
    "duration_ms": 42,
    "lock_refs": ["LOCK-MR-011", "LOCK-MR-012", "LOCK-MR-015", "LOCK-MR-017"]
  },
  "result": {
    "status": "SUCCESS",
    "error_code": null,
    "retry_count": 0
  },
  "lock_checks": {
    "MR-011_bge_m3_dim": "PASS",
    "MR-012_chroma_v1": "PASS",
    "MR-015_deny_vector_block": "PASS",
    "MR-017_project_isolation": "PASS"
  },
  "trace_id": "TRACE-{session_uuid}"
}
```

### 12.2 연산별 로깅 수준

| 연산 | 성공 시 | 실패 시 |
|------|---------|---------|
| UPSERT | INFO | ERROR |
| SEARCH | DEBUG (정상) / INFO (threshold 필터 결과 0건) | ERROR |
| DELETE | INFO | ERROR |
| GET_BY_ID | DEBUG | WARNING (not found) |
| DELETE_PROJECT | WARNING (감사 목적 항상 WARNING) | ERROR |

---

## 13. 단위 테스트 시나리오

### 13.1 테스트 매트릭스

| # | 테스트 | 대상 메서드 | LOCK | 기대 결과 |
|---|--------|-----------|------|----------|
| T-01 | allow 레코드 upsert 성공 | `upsert` | MR-015 | 정상 삽입, 메타데이터에 project_id 포함 |
| T-02 | restrict 레코드 upsert 성공 | `upsert` | MR-015 | 마스킹 후 삽입, `policy_decision="restrict"` |
| T-03 | deny 레코드 upsert 거부 | `upsert` | MR-015 | `VEC_ERR_001` 발생, 삽입 0건 |
| T-04 | deny 1건 포함 배치 전체 거부 | `upsert` | MR-015 | `VEC_ERR_001`, 배치 전체 롤백 |
| T-05 | project_id 누락 시 거부 | `upsert` | MR-017 | `ValueError` 발생 |
| T-06 | 벡터 256dim 정상 삽입 | `upsert` | MR-011 | 정상 삽입 |
| T-07 | 벡터 1024dim 삽입 시 거부 | `upsert` | MR-011 | `VEC_ERR_003` (차원 불일치) |
| T-08 | 벡터 128dim 삽입 시 거부 | `upsert` | MR-011 | `VEC_ERR_003` (차원 불일치) |
| T-09 | 프로젝트 용량 450 초과 시 거부 | `upsert` | R-64-5 | `VEC_ERR_004` (용량 초과) |
| T-10 | 동일 id로 upsert → 갱신 | `upsert` | MR-014 | 기존 레코드 갱신, 카운트 변경 없음 |
| T-11 | search 유사도 0.8 결과 반환 | `search` | MR-009 | threshold 0.75 이상 → 포함 |
| T-12 | search 유사도 0.7 결과 필터 | `search` | MR-009 | threshold 0.75 미만 → 제외 |
| T-13 | search project_id 격리 확인 | `search` | MR-017 | 타 프로젝트 레코드 반환 0건 |
| T-14 | search top_k=10 기본값 확인 | `search` | MR-014 | 최대 10건 반환 |
| T-15 | search 빈 컬렉션 결과 | `search` | — | 빈 리스트 반환 |
| T-16 | delete 정상 삭제 | `delete` | MR-017 | 해당 레코드 삭제 확인 |
| T-17 | delete 크로스 프로젝트 차단 | `delete` | MR-017 | `VEC_ERR_005` 발생 |
| T-18 | get_by_id 정상 조회 | `get_by_id` | MR-017 | VectorRecord 반환 |
| T-19 | get_by_id 타 프로젝트 → None | `get_by_id` | MR-017 | None 반환 |
| T-20 | get_by_id 존재하지 않는 ID | `get_by_id` | — | None 반환 |
| T-21 | 컬렉션 hnsw:space=cosine 확인 | `__init__` | — | 메타데이터 검증 |
| T-22 | BM25 인덱스 upsert 후 동기화 | `_sync_bm25_index` | — | BM25 검색 가능 확인 |
| T-23 | BM25 인덱스 delete 후 동기화 | `_sync_bm25_index` | — | 삭제된 문서 BM25 미반환 |
| T-24 | delete_by_project 벡터 전수 삭제 | `delete_by_project` | MR-017 | 0건 남음 확인 |
| T-25 | 배치 100건 초과 분할 처리 | `upsert` | — | 분할 실행, 전수 삽입 확인 |

---

## 14. Phase 2 통합 테스트

| # | 테스트 | 연동 세션 | 기대 결과 |
|---|--------|----------|----------|
| P2-T-01 | L0 Create → allow → ChromaVectorStore.upsert 호출 | P1-1 | 벡터 삽입 성공, project_id 메타데이터 확인 |
| P2-T-02 | L0 Create → deny → ChromaVectorStore.upsert 차단 | P1-1 | VEC_ERR_001, L0_ERR_006 연쇄 |
| P2-T-03 | L1 Create → restrict → PII 마스킹 → upsert | P1-2, P1-7 | 마스킹된 content로 벡터 생성/삽입 |
| P2-T-04 | L0→L1 승격 시 벡터 재생성 | P1-1, P1-2 | L1 scope 벡터 삽입, L0 벡터 유지/삭제 정책 확인 |
| P2-T-05 | Hybrid Search (Dense+BM25) 결합 | P1-11 | α=0.7 가중 합산, threshold=0.75 필터 |
| P2-T-06 | 6-Stage RAG Pipeline Stage 4(Store) 연동 | P1-10 | Embed→ChromaVectorStore.upsert 정상 흐름 |
| P2-T-07 | 6-Stage RAG Pipeline Stage 5(Retrieve) 연동 | P1-10 | ChromaVectorStore.search→Rerank 정상 흐름 |
| P2-T-08 | Semantic Cache 히트 시 search 스킵 | P1-5 | cosine>=0.95 캐시 히트 → 벡터 검색 미실행 |
| P2-T-09 | L1 프로젝트 삭제 → delete_by_project | P1-2 | 해당 프로젝트 벡터 0건, BM25 인덱스 제거 |
| P2-T-10 | BGE-M3 1024dim→256dim Matryoshka 정합 검증 | — | 원본 1024 저장(SQLite) + 256 저장(Chroma) |
| P2-T-11 | DCL 정책 변경 → 기존 벡터 재평가 | P1-9 | restrict→deny 전환 시 기존 벡터 삭제 여부 |
| P2-T-12 | 대화 내보내기 시 벡터 메타데이터 포함 | P1-6 | export JSON에 record_id→벡터 매핑 참조 포함 |

---

## 15. 세션 간 인터페이스 cross-check

### 15.1 P1-1 (L0 Session Memory CRUD) 접점

| 접점 | P1-1 정의 | 본 세션 (P1-3) | 정합 상태 |
|------|----------|---------------|----------|
| 벡터 삽입 트리거 | L0 Create → policy=allow/restrict → 벡터 삽입 요청 | upsert(records, project_id) | PASS — 인터페이스 일치 |
| deny 차단 | L0_ERR_006 반환 | VEC_ERR_001 발생 (LOCK-MR-015) | PASS — deny 양측 차단 |
| project_id 전달 | 모든 CRUD에 project_id 필수 | upsert/search/delete/get_by_id 전체 project_id 필수 | PASS — LOCK-MR-017 양측 |
| 에러 코드 네임스페이스 | L0_ERR_XXX | VEC_ERR_XXX | PASS — 접두사 분리 |

### 15.2 P1-2 (L1 Project Memory CRUD) 접점

| 접점 | P1-2 정의 | 본 세션 (P1-3) | 정합 상태 |
|------|----------|---------------|----------|
| 벡터 삽입 트리거 | L1 Create → policy=allow/restrict → 벡터 삽입 요청 | upsert(records, project_id) | PASS |
| L0→L1 승격 | 세션 종료 시 자동 요약 → L1 Create | 승격 후 L1 scope 벡터 upsert | PASS |
| deny 차단 | L1_ERR_006 반환 | VEC_ERR_001 발생 | PASS |
| project_id 격리 | project_id별 완전 분리 | where={"project_id": ...} 필터 | PASS |

### 15.3 P0-4 (VectorStoreABC) 접점

| 접점 | P0-4 정의 | 본 세션 (P1-3) | 정합 상태 |
|------|----------|---------------|----------|
| ABC 4메서드 | upsert/search/delete/get_by_id | 4메서드 전체 구현 | PASS (LOCK-MR-014) |
| _check_policy_before_upsert | deny → ValueError | upsert Step 1에서 호출 | PASS (LOCK-MR-015) |
| _enforce_project_filter | project_id 강제 | 모든 메서드에서 호출 | PASS (LOCK-MR-017) |
| __init__ D6 필드 | 8필드 VectorStoreAdapterSchema | super().__init__ 전체 전달 | PASS |
| ChromaAdapter 스텁 | NotImplementedError 4건 | 전체 구현 (FULL) | PASS (I-3 SHELL→FULL) |

### 15.4 P0-3 (Chroma 컬렉션 전략) 접점

| 접점 | P0-3 정의 | 본 세션 (P1-3) | 정합 상태 |
|------|----------|---------------|----------|
| 단일 컬렉션 | vamos_memory + 메타데이터 필터 | collection_name="vamos_memory" | PASS |
| Matryoshka 256dim | 검색용 벡터 256dim | dimension=256, 검증 로직 포함 | PASS |
| 1024dim SQLite 저장 | KB_EMBEDDING_RECORD BLOB | §3.2 — Chroma 외부, SQLite 저장 | PASS (범위 외 참조만) |
| cosine distance 변환 | similarity = 1 - distance | §5.1 Step 4 — 동일 공식 | PASS |
| threshold=0.75 | 후처리 필터링 | §5.1 Step 5 — LOCK-MR-009 | PASS |
| 정책 검사 플로우 | deny→금지, restrict→마스킹 후, allow→정상 | §4.2 — 동일 3단계 | PASS |
| BM25 동기화 | upsert/delete 시 동기 갱신 | §8 — _sync_bm25_index | PASS |
| R-64-5 용량 한계 | 450 벡터/프로젝트 | §9.1 — _check_capacity | PASS |

---

## 16. LOCK-MR 참조 추적표

| LOCK ID | 항목 | 반영 위치 | 값 | 검증 |
|---------|------|----------|---|------|
| **LOCK-MR-011** | BGE-M3 임베딩 | §3 BGEm3Embedder, §3.3 _validate_vector_dim | 1024dim 원본 + 256dim 검색용 | PASS |
| **LOCK-MR-012** | V1 Vector DB | §2 ChromaVectorStore, backend="chroma", mode="embedded" | Chroma 로컬 임베디드 | PASS |
| **LOCK-MR-014** | VectorStore 4메서드 | §4~§7 upsert/search/delete/get_by_id 전체 구현 | 4개 메서드 | PASS |
| **LOCK-MR-015** | Deny 벡터 금지 | §4.1 Step 1 _check_policy_before_upsert | Deny→삽입 절대 금지 | PASS |
| **LOCK-MR-017** | project_id 격리 | §4~§7 전체 메서드 _enforce_project_filter | 프로젝트 간 데이터 혼합 금지 | PASS |
| LOCK-MR-008 | Hybrid Search α | §5.2 참조 (P1-11 소관) | α=0.7 | PASS (참조) |
| LOCK-MR-009 | Similarity threshold | §5.1 Step 5 threshold=0.75 | 0.75 | PASS |
| LOCK-MR-019 | 루프 저장 폭주 방지 | §4.2 — document=content_summary (원문 아님) | 요약/메타만 저장 | PASS |

---

## 17. 교차 참조 블록

### 17.1 정본 문서 참조

| 참조 ID | 문서 | 섹션 | 참조 내용 |
|---------|------|------|----------|
| REF-D206-22 | D2.0-06 | §2.2 | V1 Chroma 로컬 임베디드, SQLite 백엔드, 단일 writer 패턴 |
| REF-D206-22A | D2.0-06 | §2.2-A | VectorStore 어댑터 인터페이스 4메서드, VectorRecord 타입, top_k=10 |
| REF-D206-32 | D2.0-06 | §3.2 | policy_decision=deny 시 벡터 삽입 절대 금지 |
| REF-D206-41 | D2.0-06 | §4.1 | V1 RAG 운영 한계: 문서 15개/프로젝트, 청크 30개/문서 |
| REF-D6-43 | D6 v3.0.0 | §4.3 | VectorStoreAdapterSchema 8필드 정의 |
| REF-D6-7A1 | D6 v3.0.0 | §7-A.1 | KB_EMBEDDING_RECORD 확장: vector_dim=1024, embedding_model=bge-m3 |
| REF-PART2-3 | Part2 | V1-Phase 2 항목3 | BGE-M3 1024dim + Matryoshka 256dim, Hybrid Search LOCK |

### 17.2 도메인 내 참조

| 참조 ID | 산출물 | 참조 내용 |
|---------|--------|----------|
| REF-P03 | chroma_collection_strategy.md (P0-3) | 단일 컬렉션 전략, Hybrid Search 파라미터, 정책 플로우, BM25 |
| REF-P04 | vectorstore_abc.py (P0-4) | VectorStoreABC 4메서드, ChromaAdapter 스텁, VectorRecord 타입 |
| REF-P01 | MemoryRecordSchema.md (P0-1) | 20필드 스키마, policy_decision 연동, TTL, B↔L 매핑 |
| REF-P11 | L0_session_memory_crud.md (P1-1) | L0 CRUD → upsert 호출 접점, L0_ERR_006 deny 처리 |
| REF-P12 | L1_project_memory_crud.md (P1-2) | L1 CRUD → upsert 호출 접점, L0→L1 승격 벡터 재생성 |

### 17.3 인접 도메인 참조

| 도메인 | 접점 | 방향 | 설명 |
|--------|------|------|------|
| 5-2 File-Context | ChromaVectorStore.search() 결과 소비 | 6-4→5-2 | 5-2가 검색 전략·알고리즘 설계, 6-4가 인프라 실행 |
| 6-2 Security | PII 마스킹 정책 정의 → restrict 벡터 처리 | 6-2→6-4 | 정의(6-2) vs 적용(6-4) |
| 6-5 SDAR | VectorStore 에스컬레이션 수신 | 6-4→6-5 | 이상 탐지, 자가 수리 |
| 6-12 Event-Logging | 감사 로그 생성 → 전달 | 6-4→6-12 | 로그 발생(6-4) vs 관리(6-12) |

---

## 18. I-3 SHELL→FULL 전환 확인

### 18.1 전환 체크리스트

| # | I-3 항목 | Phase 0 상태 | Phase 1 상태 | 근거 |
|---|---------|-------------|-------------|------|
| 1 | VectorStore ABC 정의 | SHELL (P0-4 시그니처만) | **FULL** (P0-4 유지, ABC 변경 없음) | P0-4 §2.3 |
| 2 | ChromaAdapter upsert 구현 | SHELL (NotImplementedError) | **FULL** (§4 완전 구현) | 본 문서 §4 |
| 3 | ChromaAdapter search 구현 | SHELL (NotImplementedError) | **FULL** (§5 완전 구현) | 본 문서 §5 |
| 4 | ChromaAdapter delete 구현 | SHELL (NotImplementedError) | **FULL** (§6 완전 구현) | 본 문서 §6 |
| 5 | ChromaAdapter get_by_id 구현 | SHELL (NotImplementedError) | **FULL** (§7 완전 구현) | 본 문서 §7 |
| 6 | Chroma 클라이언트 초기화 | SHELL (주석 코드) | **FULL** (§2 PersistentClient) | 본 문서 §2 |
| 7 | BGE-M3 임베딩 연동 | 참조만 | **FULL** (§3 BGEm3Embedder) | 본 문서 §3 |
| 8 | BM25 인덱스 동기화 | 미구현 | **FULL** (§8 BM25IndexManager) | 본 문서 §8 |
| 9 | 에러 코드 체계 | 미정의 | **FULL** (§10 VEC_ERR_001~012) | 본 문서 §10 |
| 10 | 복구/재시도 전략 | 미정의 | **FULL** (§11 흐름도 + 정책표) | 본 문서 §11 |

> **I-3 최종 상태**: SHELL → **FULL** (10/10 항목 완료)

---

## 예외 처리 정책 표

| 예외 상황 | 처리 정책 | 복구 가능 | 데이터 영향 |
|----------|----------|----------|-----------|
| Deny 레코드 삽입 시도 | 즉시 거부, 배치 전체 롤백 | N/A (정상 거부) | 변경 없음 |
| project_id 누락 | 즉시 거부 | N/A | 변경 없음 |
| 벡터 차원 불일치 | 즉시 거부 | N/A | 변경 없음 |
| 용량 초과 | 거부 + 사용자 알림 | 기존 데이터 삭제 후 재시도 | 변경 없음 |
| Chroma DB 잠김 | 지수 백오프 재시도 (3회) | 대부분 복구 | 변경 없음 |
| Chroma 쿼리 실패 | 고정 간격 재시도 (2회) | 대부분 복구 | 변경 없음 |
| BM25 동기화 실패 | 1회 재시도 → WARNING | 벡터 삽입은 유효 | BM25 인덱스 stale |
| 영속 경로 접근 불가 | 1회 재시도 → CRITICAL | 서비스 불가 | 변경 없음 |
| 크로스 프로젝트 접근 | 즉시 거부 | N/A (보안 위반) | 변경 없음 |

---

## 설계 결정 요약

| # | 결정 | 선택 | 근거 |
|---|------|------|------|
| 1 | ABC 상속 | VectorStoreABC (P0-4) | LOCK-MR-014, D2.0-06 §2.2-A |
| 2 | 컬렉션 전략 | 단일 컬렉션 vamos_memory + 메타데이터 필터 | P0-3 §3.2 결정 |
| 3 | 검색 벡터 차원 | 256dim (Matryoshka) | LOCK-MR-011, P0-3 §2.1 |
| 4 | 정책 검사 위치 | upsert() 최상단 | LOCK-MR-015, R-64-3 |
| 5 | threshold 적용 | search() 후처리 필터링 | P0-3 §6.1 (Chroma where 미지원) |
| 6 | BM25 동기화 | 전체 재구축 (V1) | V1 소규모 (450 벡터/프로젝트 이내) |
| 7 | 배치 처리 | 100건 단위 분할 | Chroma 단일 writer 패턴 |
| 8 | 에러 코드 체계 | VEC_ERR_XXX (12종) | L0_ERR/L1_ERR와 네임스페이스 분리 |
