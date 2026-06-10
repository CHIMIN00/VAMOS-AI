# P1-5. Semantic Cache 구현 상세 (V1)

> **세션**: P1-5 (2026-04-13)
> **산출물 버전**: v1.1 (step2 재검증: 4건 수정)
> **상태**: COMPLETE
> **LOCK 준수**: LOCK-MR-010 (cosine >= 0.95 히트 판정)
> **이슈 전환**: I-4 SHELL->FULL (Semantic Cache 무효화 상세)
> **정본**: D2.0-06 S4.7 (Semantic Cache 설계 — ADD-012, MOD-017), D6 SemanticCacheSchema v3.0.0, Part2 V1-Phase 2 항목5
> **교차 참조**: P0-3 chroma_collection_strategy, P0-4 vectorstore_abc.py, P1-1 L0_session_memory_crud, P1-2 L1_project_memory_crud, P1-3 chroma_adapter
> **권한 체인**: RULE 1.3 > PLAN 3.0 > D2.0-06 (LOCK) > D6 (Schema SOT) > Part2 V1-P2 (구현가이드) > 본 문서 (IMPL-DETAIL)
>
> **LOCK 준수 상세**:
>   - LOCK-MR-010: Semantic Cache cosine >= 0.95 히트 판정
>   - LOCK-MR-017: project_id 기반 격리, 프로젝트 간 캐시 혼합 금지
>   - LOCK-MR-015: Deny 판정 시 캐시 저장 금지
>
> **입력 파일**:
>   - D2.0-06 S4.7 (Semantic Cache 설계, 무효화 정책)
>   - D6 v3.0.0 S4.5 SemanticCacheSchema (8필드)
>   - Part2 V1-Phase 2 항목5 (Semantic Cache 요건 + 파라미터 LOCK 표)
>   - P0-3: `chroma_collection_strategy.md` (Chroma 컬렉션 전략)
>   - P0-4: `vectorstore_abc.py` (VectorStoreABC 인터페이스)
>   - P1-3: `chroma_adapter.md` (ChromaVectorStore FULL 구현 — search 연동)
>
> **이전 단계 이월 사항**: P1-1~P1-4 모두 이월 없음.

---

## 목차

1. [SemanticCache 클래스 설계](#1-semanticcache-클래스-설계)
2. [D6 SemanticCacheSchema 필드 매핑](#2-d6-semanticcacheschema-필드-매핑)
3. [캐시 키 생성 및 유사도 비교](#3-캐시-키-생성-및-유사도-비교)
4. [캐시 히트/미스 판정 로직](#4-캐시-히트미스-판정-로직)
5. [캐시 저장 (PUT)](#5-캐시-저장-put)
6. [캐시 조회 (GET)](#6-캐시-조회-get)
7. [캐시 무효화 전략 (I-4 SHELL->FULL)](#7-캐시-무효화-전략-i-4-shellfull)
8. [캐시 크기 관리 (LRU + max_entries)](#8-캐시-크기-관리-lru--max_entries)
9. [project_id 격리 (LOCK-MR-017)](#9-project_id-격리-lock-mr-017)
10. [에러 코드 정의](#10-에러-코드-정의)
11. [복구/재시도 전략](#11-복구재시도-전략)
12. [에스컬레이션 정책](#12-에스컬레이션-정책)
13. [로깅 규격 (R-01-7)](#13-로깅-규격-r-01-7)
14. [시간복잡도 분석 (Big-O)](#14-시간복잡도-분석-big-o)
15. [예외 처리 정책 표](#15-예외-처리-정책-표)
16. [단위 테스트 시나리오](#16-단위-테스트-시나리오)
17. [Phase 2 통합 테스트](#17-phase-2-통합-테스트)
18. [세션 간 인터페이스 cross-check](#18-세션-간-인터페이스-cross-check)
19. [LOCK-MR 참조 추적표](#19-lock-mr-참조-추적표)
20. [교차 참조 블록](#20-교차-참조-블록)
21. [I-4 SHELL->FULL 전환 명세](#21-i-4-shellfull-전환-명세)

---

## 1. SemanticCache 클래스 설계

### 1.1 클래스 계층

```
SemanticCache (본 문서)
  ├── __init__(config: SemanticCacheConfig)
  ├── _compute_embedding(query_text: str) -> list[float]
  ├── _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float
  ├── _find_best_match(query_embedding: list[float], project_id: str) -> tuple[CacheEntry | None, float]
  ├── _evict_expired(project_id: str) -> int
  ├── _evict_lru(project_id: str) -> int
  ├── get(query_text: str, project_id: str) -> CacheResult
  ├── put(query_text: str, response_text: str, source_refs: list[str], project_id: str, policy_decision: str = "allow") -> CacheEntry
  ├── invalidate(cache_id: str, project_id: str) -> bool
  ├── invalidate_by_source(source_ref: str, project_id: str) -> int
  ├── invalidate_by_pattern(pattern: str, project_id: str) -> int
  ├── flush(project_id: str) -> int
  ├── flush_all() -> int
  ├── stats(project_id: str) -> CacheStats
  └── _check_drift(entry: CacheEntry, current_embedding: list[float]) -> bool
```

### 1.2 SemanticCacheConfig 구조

```python
@dataclass
class SemanticCacheConfig:
    """Semantic Cache 설정 — D2.0-06 §4.7 + Part2 V1-P2 파라미터 표 기반"""
    similarity_threshold: float = 0.95       # LOCK-MR-010: cosine >= 0.95
    ttl_sec: int = 86400                     # 24시간 (D2.0-06 §4.7.2)
    max_entries: int = 1000                  # config.v1.toml 기준
    embedding_model: str = "bge-m3"          # LOCK-MR-011 연동
    embedding_dim: int = 256                 # Matryoshka 256dim 검색용
    drift_threshold: float = 0.05            # Part2: Embedding Drift > 0.05 시 무효화
    storage_backend: str = "in_memory"       # V1=인메모리(LRU), V2+=Redis
    eviction_policy: str = "lru"             # LRU 정책
    enable_source_invalidation: bool = True  # 소스 변경 연동 무효화
    enable_qod_invalidation: bool = True     # QoD < 0.4 시 무효화 (D2.0-06 §4.7.2)
    qod_invalidation_threshold: float = 0.4  # QoD 하한
```

> **LOCK-MR-010 (D2.1-D6 / Part2 V1-P2)**: `similarity_threshold`는 0.95 이상만 허용. 0.95 미만 값으로 설정 시 `CacheConfigError` (CACHE_ERR_001) 발생.

---

## 2. D6 SemanticCacheSchema 필드 매핑

> 정본: D6 v3.0.0 §4.5 SemanticCacheSchema — [REF:D6:semantic-cache-schema:Schema:SemanticCacheSchema:v3.0.0]

| D6 필드 | CacheEntry 속성 | 타입 | 기본값 | 근거 |
|---------|-----------------|------|--------|------|
| `cache_id` | `cache_id` | string | `"scache_{uuid4_short}"` | D6 예시: `scache_001` |
| `query_embedding` | `query_embedding` | list[float] | (산출) | BGE-M3 256dim (LOCK-MR-011) |
| `query_text` | `query_text` | string | (입력) | 원본 질문 텍스트 |
| `response_text` | `response_text` | string | (입력) | 캐시된 응답 전문 |
| `similarity_threshold` | `similarity_threshold` | float | 0.95 | LOCK-MR-010 |
| `hit_count` | `hit_count` | int | 0 | 히트 시 +1 증가 |
| `ttl_sec` | `ttl_sec` | int | 86400 | D2.0-06 §4.7.2: 24시간 |
| `created_at` | `created_at` | string | (생성 시각 ISO 8601) | D6 예시 포맷 |

### 2.1 CacheEntry 확장 필드 (구현 전용)

| 추가 필드 | 타입 | 설명 | 근거 |
|-----------|------|------|------|
| `project_id` | string | 프로젝트 격리 키 | LOCK-MR-017 |
| `source_refs` | list[string] | 응답 생성에 사용된 소스 참조 ID 목록 | D2.0-06 §4.7.1 캐시 레코드 `source_refs` |
| `query_hash` | string | `sha256(query_text)` — 정확 일치 빠른 검색용 | D2.0-06 §4.7.1 `query_hash` |
| `last_accessed_at` | string | LRU 정렬 기준 (ISO 8601) | 캐시 크기 관리용 |
| `expires_at` | string | `created_at + ttl_sec` 산출 (ISO 8601) | TTL 만료 판정용 |
| `invalidated` | bool | 수동/자동 무효화 플래그 | I-4 무효화 전략 |
| `invalidation_reason` | string? | `"TTL" | "DRIFT" | "SOURCE_CHANGE" | "QOD_DROP" | "MANUAL" | None` | I-4 추적 |

### 2.2 CacheEntry 전체 구조

```python
@dataclass
class CacheEntry:
    """D6 SemanticCacheSchema v3.0.0 기반 캐시 엔트리"""
    # -- D6 필드 (8필드 전수) --
    cache_id: str                    # scache_{uuid4_short}
    query_embedding: list[float]     # BGE-M3 256dim
    query_text: str                  # 원본 질문
    response_text: str               # 캐시된 응답
    similarity_threshold: float      # 0.95 (LOCK-MR-010)
    hit_count: int                   # 히트 카운트
    ttl_sec: int                     # 86400
    created_at: str                  # ISO 8601

    # -- 구현 확장 필드 --
    project_id: str                  # LOCK-MR-017
    source_refs: list[str]           # 소스 참조 ID
    query_hash: str                  # sha256(query_text)
    last_accessed_at: str            # LRU 기준
    expires_at: str                  # created_at + ttl_sec
    invalidated: bool = False        # 무효화 플래그
    invalidation_reason: str | None = None
```

---

## 3. 캐시 키 생성 및 유사도 비교

### 3.1 쿼리 임베딩 산출

```
입력: query_text (str)
  ↓
  BGE-M3 모델 로드 (P1-3 EmbeddingFunction 재사용)
  ↓
  encode(query_text) → 1024dim 원본 벡터
  ↓
  Matryoshka 256dim 절단 ([:256] + L2 정규화)
  ↓
출력: query_embedding (list[float], len=256)
```

> **LOCK-MR-011**: BGE-M3 1024dim 원본 + Matryoshka 256dim 검색용. 캐시 키 비교는 256dim 벡터 기준.

### 3.2 코사인 유사도 계산

```python
def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    코사인 유사도 산출.
    vec_a, vec_b: L2-정규화된 256dim 벡터.
    반환: -1.0 ~ 1.0 (L2 정규화 시 dot product와 동치)
    """
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = sqrt(sum(a * a for a in vec_a))
    norm_b = sqrt(sum(b * b for b in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)
```

> **최적화 참고**: BGE-M3 출력을 L2 정규화한 상태로 저장하면 `dot product = cosine similarity`이므로 norm 계산 생략 가능. V1에서는 안전하게 full cosine 계산.

### 3.3 최적 매칭 탐색

```python
def _find_best_match(
    query_embedding: list[float],
    project_id: str
) -> tuple[CacheEntry | None, float]:
    """
    project_id 범위 내 모든 유효 캐시 엔트리와 유사도 비교.
    가장 높은 유사도의 엔트리와 스코어 반환.
    """
    best_entry = None
    best_score = -1.0

    for entry in self._cache[project_id].values():
        if entry.invalidated:
            continue
        if _is_expired(entry):
            continue
        score = _cosine_similarity(query_embedding, entry.query_embedding)
        if score > best_score:
            best_score = score
            best_entry = entry

    return (best_entry, best_score)
```

> **V1 한계**: 인메모리 선형 탐색 O(N). V2에서 Chroma/Qdrant `vamos_cache` 컬렉션으로 ANN 검색 전환 예정 (S7D-048 참조).

---

## 4. 캐시 히트/미스 판정 로직

### 4.1 판정 플로우차트

```
get(query_text, project_id)
  │
  ├─ 1. query_hash = sha256(query_text)
  │     → 정확 일치 검색 (V1: O(N) 순회, hash 인덱스 추가 시 O(1) 가능)
  │     → 매칭 시: cosine 검증 생략, 즉시 HIT (score=1.0)
  │
  ├─ 2. query_embedding = _compute_embedding(query_text)
  │     → BGE-M3 256dim
  │
  ├─ 3. (best_entry, best_score) = _find_best_match(query_embedding, project_id)
  │
  ├─ 4. best_score >= 0.95?                    ← LOCK-MR-010
  │     ├─ YES: CACHE HIT
  │     │   ├─ entry.hit_count += 1
  │     │   ├─ entry.last_accessed_at = now()
  │     │   ├─ LOG: level=INFO, status=CACHE_HIT, score=best_score
  │     │   └─ return CacheResult(hit=True, response=entry.response_text, score=best_score, cache_id=entry.cache_id)
  │     │
  │     └─ NO: CACHE MISS
  │         ├─ LOG: level=INFO, status=CACHE_MISS, best_score=best_score
  │         └─ return CacheResult(hit=False, response=None, score=best_score, cache_id=None)
  │
  └─ 5. 호출측: MISS 시 → RAG Pipeline 정상 실행 → put() 으로 결과 캐싱
```

### 4.2 CacheResult 구조

```python
@dataclass
class CacheResult:
    hit: bool                   # True=캐시 히트, False=캐시 미스
    response: str | None        # 히트 시 캐시된 응답, 미스 시 None
    score: float                # 최고 유사도 스코어 (-1.0 = 캐시 비어있음)
    cache_id: str | None        # 히트 시 캐시 엔트리 ID
    source_refs: list[str] | None  # 히트 시 소스 참조 목록
```

### 4.3 LOCK-MR-010 검증 경계

| cosine score 범위 | 판정 | 동작 |
|-------------------|------|------|
| >= 0.95 | **HIT** | 캐시 응답 반환, LLM 호출 생략 |
| 0.90 ~ 0.9499 | MISS (근접) | RAG 실행, LOG에 near_miss=true 기록 |
| < 0.90 | MISS | RAG 정상 실행 |
| < 0.0 (빈 캐시) | MISS | RAG 정상 실행 |

> **LOCK-MR-010 경계 준수**: 0.95 미만은 절대 HIT 판정 불가. `>=` 연산자 사용 (0.95 포함).

---

## 5. 캐시 저장 (PUT)

### 5.1 저장 플로우

```
put(query_text, response_text, source_refs, project_id)
  │
  ├─ 1. 만료 엔트리 제거: _evict_expired(project_id)
  │
  ├─ 2. 용량 검사: len(cache[project_id]) >= max_entries?
  │     └─ YES: _evict_lru(project_id) — LRU 1건 제거
  │
  ├─ 3. 중복 검사: 동일 query_hash 존재?
  │     ├─ YES: 기존 엔트리 갱신 (response_text, source_refs, created_at, expires_at 리프레시)
  │     └─ NO: 신규 CacheEntry 생성
  │
  ├─ 4. CacheEntry 필드 설정:
  │     ├─ cache_id = "scache_{uuid4_short}"
  │     ├─ query_embedding = _compute_embedding(query_text)
  │     ├─ query_hash = sha256(query_text)
  │     ├─ similarity_threshold = 0.95  (LOCK-MR-010)
  │     ├─ hit_count = 0
  │     ├─ ttl_sec = config.ttl_sec (86400)
  │     ├─ created_at = now() (ISO 8601)
  │     ├─ expires_at = now() + ttl_sec
  │     ├─ last_accessed_at = now()
  │     ├─ project_id = project_id (LOCK-MR-017)
  │     └─ source_refs = source_refs
  │
  ├─ 5. cache[project_id][cache_id] = entry
  │
  └─ 6. LOG: level=INFO, operation=CACHE_PUT, cache_id, project_id
```

### 5.2 Deny 판정 시 캐시 저장 차단

> **LOCK-MR-015**: RAG Pipeline에서 DCL policy_decision=deny인 경우, 해당 응답을 캐시에 저장하지 않는다.

```python
def put(query_text, response_text, source_refs, project_id, policy_decision="allow"):
    if policy_decision == "deny":
        raise CacheDenyError("LOCK-MR-015: Deny 판정 시 캐시 저장 금지")
    # ... 이하 정상 저장 흐름
```

---

## 6. 캐시 조회 (GET)

### 6.1 get() 전체 의사코드

```python
def get(query_text: str, project_id: str) -> CacheResult:
    """
    Semantic Cache 조회 — LOCK-MR-010 (cosine >= 0.95) 준수.
    """
    # 0. project_id 격리 검증 (LOCK-MR-017)
    if project_id not in self._cache:
        return CacheResult(hit=False, response=None, score=-1.0, cache_id=None, source_refs=None)

    # 1. 정확 일치 (hash) 빠른 경로
    query_hash = sha256(query_text)
    for entry in self._cache[project_id].values():
        if entry.query_hash == query_hash and not entry.invalidated and not _is_expired(entry):
            entry.hit_count += 1
            entry.last_accessed_at = now()
            _log_hit(entry, score=1.0)
            return CacheResult(hit=True, response=entry.response_text, score=1.0,
                             cache_id=entry.cache_id, source_refs=entry.source_refs)

    # 2. 의미 유사도 탐색
    query_embedding = self._compute_embedding(query_text)
    best_entry, best_score = self._find_best_match(query_embedding, project_id)

    # 3. 히트 판정 (LOCK-MR-010)
    if best_entry is not None and best_score >= self.config.similarity_threshold:  # >= 0.95
        best_entry.hit_count += 1
        best_entry.last_accessed_at = now()
        _log_hit(best_entry, best_score)
        return CacheResult(hit=True, response=best_entry.response_text, score=best_score,
                         cache_id=best_entry.cache_id, source_refs=best_entry.source_refs)

    # 4. 캐시 미스
    _log_miss(query_text, project_id, best_score)
    return CacheResult(hit=False, response=None, score=best_score if best_entry else -1.0,
                     cache_id=None, source_refs=None)
```

### 6.2 RAG Pipeline 연동 흐름

```
사용자 질문 입력
  ↓
SemanticCache.get(query_text, project_id)
  ├─ HIT → 캐시 응답 즉시 반환 (LLM 호출 생략, 응답 시간 90%+ 절감)
  └─ MISS → 6-Stage RAG Pipeline 실행 (LOCK-MR-007)
              ↓
            Collect → Chunk → Embed → Store → Retrieve → Generate
              ↓
            SemanticCache.put(query_text, response, source_refs, project_id)
              ↓
            응답 반환
```

> **P1-3 접점**: 캐시 MISS 시 `ChromaVectorStore.search()` (P1-3 §5) 호출이 RAG Stage 5(Retrieve)에서 실행됨.
> **P1-10 접점** (미래): RAG Pipeline 전체 오케스트레이션은 P1-10에서 구현 예정. 본 문서는 캐시 레이어만 담당.

---

## 7. 캐시 무효화 전략 (I-4 SHELL->FULL)

> **I-4 상태**: SHELL(3가지 정책명만 나열) -> FULL(TTL/Drift/소스변경/QoD/수동 무효화 구현 로직 상세)

### 7.1 무효화 정책 총괄

| # | 정책 | 트리거 | 동작 | 정본 근거 |
|---|------|--------|------|-----------|
| INV-1 | **TTL 기반** | `now() > entry.expires_at` | 자동 만료 (lazy eviction) | D2.0-06 §4.7.2: 기본 24시간 |
| INV-2 | **소스 변경 연동** | 인덱싱 문서 갱신/삭제 이벤트 | `source_refs`에 해당 문서 ID 포함된 캐시 즉시 무효화 | D2.0-06 §4.7.2 |
| INV-3 | **Embedding Drift** | 원본 문서 재임베딩 시 cosine 차이 > 0.05 | 관련 캐시 무효화 | Part2 V1-P2 무효화 정책 |
| INV-4 | **QoD 변동 연동** | 소스 QoD 재평가 결과 < 0.4 | 관련 캐시 무효화 | D2.0-06 §4.7.2 |
| INV-5 | **수동 무효화** | `vamos:cache:invalidate` IPC 명령 | 특정 키/패턴/프로젝트/전역 삭제 | D2.0-06 §4.7.2 |

### 7.2 INV-1: TTL 기반 무효화

```python
def _is_expired(entry: CacheEntry) -> bool:
    """TTL 만료 판정 — D2.0-06 §4.7.2: 기본 24시간"""
    return now() > parse_iso(entry.expires_at)

def _evict_expired(project_id: str) -> int:
    """만료 엔트리 일괄 제거 (lazy eviction)"""
    expired_ids = [
        eid for eid, entry in self._cache[project_id].items()
        if _is_expired(entry)
    ]
    for eid in expired_ids:
        entry = self._cache[project_id].pop(eid)
        entry.invalidated = True
        entry.invalidation_reason = "TTL"
        _log_invalidation(entry, "TTL")
        _emit_event("cache.invalidated", entry)  # D2.0-06 §4.7.2: 02 Registry 이벤트
    return len(expired_ids)
```

> **TTL 설정**: 기본 86400초 (24시간). 소스 변동이 잦은 프로젝트는 config에서 21600초 (6시간)으로 단축 가능 (D2.0-06 §4.7.2 단서).

### 7.3 INV-2: 소스 변경 연동 무효화

```python
def invalidate_by_source(source_ref: str, project_id: str) -> int:
    """
    인덱싱 문서 갱신/삭제 시 호출.
    source_refs에 해당 source_ref를 포함하는 모든 캐시 엔트리 무효화.
    D2.0-06 §4.7.2: "해당 문서를 source_refs로 참조하는 캐시 항목을 즉시 무효화"
    """
    invalidated_count = 0
    for eid, entry in list(self._cache.get(project_id, {}).items()):
        if source_ref in entry.source_refs and not entry.invalidated:
            entry.invalidated = True
            entry.invalidation_reason = "SOURCE_CHANGE"
            entry.hit_count = 0  # 무효화된 항목 카운트 리셋
            _log_invalidation(entry, "SOURCE_CHANGE", source_ref=source_ref)
            _emit_event("cache.invalidated", entry)
            invalidated_count += 1
    return invalidated_count
```

### 7.4 INV-3: Embedding Drift 기반 무효화

```python
def _check_drift(entry: CacheEntry, current_embedding: list[float]) -> bool:
    """
    원본 문서 재임베딩 후 기존 캐시 엔트리의 query_embedding과 비교.
    cosine 차이 > drift_threshold(0.05) 시 drift 판정.
    Part2 V1-P2: "Embedding Drift(>0.05)면 캐시 무효화"
    """
    original_similarity = _cosine_similarity(entry.query_embedding, current_embedding)
    drift = 1.0 - original_similarity
    return drift > self.config.drift_threshold  # > 0.05

def invalidate_by_drift(source_ref: str, new_embedding: list[float], project_id: str) -> int:
    """소스 재임베딩 시 drift 검사 + 무효화"""
    invalidated_count = 0
    for eid, entry in list(self._cache.get(project_id, {}).items()):
        if source_ref in entry.source_refs and not entry.invalidated:
            if self._check_drift(entry, new_embedding):
                entry.invalidated = True
                entry.invalidation_reason = "DRIFT"
                _log_invalidation(entry, "DRIFT", source_ref=source_ref)
                _emit_event("cache.invalidated", entry)
                invalidated_count += 1
    return invalidated_count
```

### 7.5 INV-4: QoD 변동 연동 무효화

```python
def invalidate_by_qod_drop(source_ref: str, new_qod: float, project_id: str) -> int:
    """
    소스 QoD가 재평가되어 0.4 이하로 하락 시 관련 캐시 무효화.
    D2.0-06 §4.7.2: "소스 QoD가 재평가되어 0.4 이하로 하락하면 관련 캐시 항목 무효화"
    """
    if new_qod > self.config.qod_invalidation_threshold:  # > 0.4
        return 0  # QoD 양호 — 무효화 불필요

    invalidated_count = 0
    for eid, entry in list(self._cache.get(project_id, {}).items()):
        if source_ref in entry.source_refs and not entry.invalidated:
            entry.invalidated = True
            entry.invalidation_reason = "QOD_DROP"
            _log_invalidation(entry, "QOD_DROP", source_ref=source_ref, qod=new_qod)
            _emit_event("cache.invalidated", entry)
            invalidated_count += 1
    return invalidated_count
```

### 7.6 INV-5: 수동 무효화

```python
def invalidate(cache_id: str, project_id: str) -> bool:
    """단일 캐시 엔트리 수동 무효화"""
    entry = self._cache.get(project_id, {}).get(cache_id)
    if entry is None or entry.invalidated:
        return False
    entry.invalidated = True
    entry.invalidation_reason = "MANUAL"
    _log_invalidation(entry, "MANUAL")
    _emit_event("cache.invalidated", entry)
    return True

def invalidate_by_pattern(pattern: str, project_id: str) -> int:
    """패턴 기반 수동 무효화 — query_text에 패턴 포함 시 무효화"""
    invalidated_count = 0
    for eid, entry in list(self._cache.get(project_id, {}).items()):
        if pattern in entry.query_text and not entry.invalidated:
            entry.invalidated = True
            entry.invalidation_reason = "MANUAL"
            _log_invalidation(entry, "MANUAL", pattern=pattern)
            _emit_event("cache.invalidated", entry)
            invalidated_count += 1
    return invalidated_count

def flush(project_id: str) -> int:
    """프로젝트 전체 캐시 초기화 — D2.0-06 §4.7.2: 관리자 강제 초기화"""
    count = len(self._cache.get(project_id, {}))
    self._cache[project_id] = {}
    _log_flush(project_id, count)
    _emit_event("cache.flushed", {"project_id": project_id, "count": count})
    return count

def flush_all() -> int:
    """전역 캐시 초기화"""
    total = sum(len(entries) for entries in self._cache.values())
    self._cache.clear()
    _log_flush("__all__", total)
    _emit_event("cache.flushed", {"project_id": "__all__", "count": total})
    return total
```

### 7.7 무효화 이벤트 기록

> D2.0-06 §4.7.2: "무효화 이벤트는 `cache.invalidated` event_type으로 02 Registry에 기록."

```python
def _emit_event(event_type: str, payload: dict | CacheEntry):
    """EventTypeRegistry에 무효화 이벤트 발행"""
    event = {
        "event_type": event_type,        # "cache.invalidated" | "cache.flushed"
        "timestamp": now(),
        "source": "SemanticCache",
        "payload": {
            "cache_id": getattr(payload, 'cache_id', None),
            "project_id": getattr(payload, 'project_id', payload.get('project_id', None)),
            "invalidation_reason": getattr(payload, 'invalidation_reason', None),
        }
    }
    # 02 EventTypeRegistry 연동 (P1-10 RAG Pipeline에서 구독)
    EventBus.publish(event)
```

---

## 8. 캐시 크기 관리 (LRU + max_entries)

### 8.1 LRU Eviction 정책

```python
def _evict_lru(project_id: str) -> int:
    """
    max_entries(1000) 초과 시 가장 오래 접근되지 않은 엔트리 제거.
    V1: 인메모리 LRU (D2.0-06 §4.7.1: "V1=인메모리(LRU)")
    """
    entries = self._cache.get(project_id, {})
    if len(entries) < self.config.max_entries:
        return 0

    # last_accessed_at 기준 오름차순 정렬 → 가장 오래된 것 제거
    sorted_entries = sorted(entries.items(), key=lambda kv: kv[1].last_accessed_at)
    evict_count = len(entries) - self.config.max_entries + 1  # 1건 여유 확보

    evicted = 0
    for cache_id, entry in sorted_entries[:evict_count]:
        del entries[cache_id]
        _log_eviction(entry, "LRU")
        evicted += 1

    return evicted
```

### 8.2 용량 정책 요약

| 파라미터 | 값 | LOCK | 근거 |
|---------|---|:---:|------|
| max_entries (프로젝트당) | 1000 | N | config.v1.toml |
| eviction_policy | LRU | N | D2.0-06 §4.7.1 |
| ttl_sec | 86400 (24h) | N | D2.0-06 §4.7.2 |
| ttl_sec (변동 잦은 프로젝트) | 21600 (6h) | N | D2.0-06 §4.7.2 단서 |
| similarity_threshold | **0.95** | **Y** | LOCK-MR-010 |
| drift_threshold | 0.05 | N | Part2 |

### 8.3 캐시 통계

```python
@dataclass
class CacheStats:
    project_id: str
    total_entries: int
    active_entries: int          # invalidated=False & not expired
    expired_entries: int
    invalidated_entries: int
    total_hits: int              # sum(hit_count)
    hit_ratio: float             # total_hits / (total_hits + total_misses)
    total_misses: int
    avg_response_time_saved_ms: float  # 추정 절감 시간
    cache_size_bytes: int        # 추정 메모리 사용량
    oldest_entry_at: str | None
    newest_entry_at: str | None

def stats(project_id: str) -> CacheStats:
    """캐시 통계 — D2.0-06 §4.7.3: 히트율, 평균 응답 시간 절감, 캐시 크기"""
    # ... 통계 산출 로직
    # 히트율 < 10% 시 WARN 로그 (D2.0-06 §4.7.3: "히트율 < 10% 시 캐시 전략 재검토 알림")
    if stats.hit_ratio < 0.10:
        _log_warn("CACHE_LOW_HIT_RATIO", project_id, stats.hit_ratio)
    return stats
```

---

## 9. project_id 격리 (LOCK-MR-017)

### 9.1 격리 구조

```python
# 캐시 저장소: project_id → {cache_id → CacheEntry}
self._cache: dict[str, dict[str, CacheEntry]] = {}
```

> **LOCK-MR-017 (D2.0-06 §1 / RULE 1.3 §7.2)**: 프로젝트 간 데이터 혼합 금지. 모든 get/put/invalidate/flush 메서드는 project_id를 필수 인자로 받으며, 다른 프로젝트의 캐시에 접근 불가.

### 9.2 격리 위반 방지

```python
def _validate_project_id(project_id: str) -> None:
    """project_id 유효성 검증"""
    if not project_id or not isinstance(project_id, str):
        raise ProjectIsolationError("LOCK-MR-017: project_id는 비어있을 수 없음")
    if project_id.strip() == "":
        raise ProjectIsolationError("LOCK-MR-017: project_id는 공백 불가")
```

- get(): project_id 범위 내에서만 캐시 탐색
- put(): project_id 키 하위에 엔트리 저장
- invalidate*(): project_id 범위 내에서만 무효화
- flush(): 해당 project_id의 캐시만 삭제
- flush_all(): 전역 — 관리자 전용 (사용 시 WARN 로그)

---

## 10. 에러 코드 정의

| 에러 코드 | 클래스 | 심각도 | 설명 | 복구 가능 |
|-----------|--------|--------|------|:---------:|
| `CACHE_ERR_001` | `CacheConfigError` | ERROR | similarity_threshold < 0.95 (LOCK-MR-010 위반) | N |
| `CACHE_ERR_002` | `CacheEmbeddingError` | ERROR | BGE-M3 임베딩 생성 실패 | Y (재시도) |
| `CACHE_ERR_003` | `CacheDenyError` | WARN | Deny 판정 시 캐시 저장 시도 (LOCK-MR-015) | N |
| `CACHE_ERR_004` | `ProjectIsolationError` | ERROR | project_id 누락/비정상 (LOCK-MR-017) | N |
| `CACHE_ERR_005` | `CacheCapacityError` | WARN | max_entries 도달, LRU eviction 실행 | Y (자동) |
| `CACHE_ERR_006` | `CacheCorruptionError` | ERROR | 캐시 엔트리 무결성 검증 실패 | Y (삭제+재생성) |
| `CACHE_ERR_007` | `CacheSerializationError` | ERROR | 엔트리 직렬화/역직렬화 오류 | Y (삭제) |
| `CACHE_ERR_008` | `CacheTimeoutError` | WARN | 임베딩 산출 타임아웃 | Y (재시도) |
| `CACHE_ERR_009` | `CacheDriftError` | INFO | Embedding drift > 0.05 감지 | Y (무효화) |
| `CACHE_ERR_010` | `CacheQoDError` | INFO | QoD < 0.4 연동 무효화 | Y (무효화) |
| `CACHE_ERR_011` | `CacheLowHitRatioWarn` | WARN | 히트율 < 10% 재검토 필요 | Y (설정 조정) |
| `CACHE_ERR_012` | `CacheFlushError` | ERROR | 전역 flush 실패 | Y (재시도) |

---

## 11. 복구/재시도 전략

### 11.1 Phase별 복구 전략

| Phase | 실패 유형 | 1차 복구 | 2차 복구 | 3차 (에스컬레이션) |
|-------|----------|---------|---------|-------------------|
| GET | 임베딩 산출 실패 | 1회 재시도 (500ms 대기) | hash 정확 일치만 시도 | RAG Pipeline fallback (캐시 우회) |
| GET | 유사도 비교 오류 | 오류 엔트리 삭제 | 전체 유사도 재계산 | CACHE MISS 반환 + WARN 로그 |
| PUT | 임베딩 산출 실패 | 1회 재시도 (500ms 대기) | 캐시 저장 생략 (응답은 정상 반환) | WARN 로그 + 에스컬레이션 |
| PUT | 용량 초과 | LRU eviction 자동 실행 | 만료 엔트리 일괄 제거 | flush(project_id) 후 재시도 |
| INVALIDATE | 무효화 대상 미존재 | 무시 (정상) | — | — |
| INVALIDATE | 이벤트 발행 실패 | 1회 재시도 | 로컬 로그에만 기록 | ERROR 로그 |

### 11.2 재시도 정책

```python
RETRY_CONFIG = {
    "max_retries": 2,
    "base_delay_ms": 500,
    "backoff_factor": 2.0,    # 500ms → 1000ms
    "max_delay_ms": 3000,
    "retryable_errors": [
        "CACHE_ERR_002",  # 임베딩 생성 실패
        "CACHE_ERR_008",  # 타임아웃
        "CACHE_ERR_012",  # flush 실패
    ]
}
```

---

## 12. 에스컬레이션 정책

### 12.1 EscalationPayload 구조

```json
{
  "escalation_id": "ESC-CACHE-{uuid}",
  "timestamp": "2026-04-13T10:30:00Z",
  "source": "SemanticCache",
  "severity": "WARN | ERROR | CRITICAL",
  "category": "SEMANTIC_CACHE",
  "project_id": "proj_xxx",
  "operation": "get | put | invalidate | flush | stats",
  "error_code": "CACHE_ERR_002 | CACHE_ERR_006 | ...",
  "error_type": "CacheEmbeddingError | CacheCorruptionError | ...",
  "message": "사람이 읽을 수 있는 오류 설명",
  "context": {
    "cache_entries_count": 500,
    "hit_ratio": 0.08,
    "similarity_threshold": 0.95,
    "ttl_sec": 86400,
    "eviction_policy": "lru"
  },
  "recommended_action": "임베딩 모델 재로드 | 캐시 flush | 관리자 확인",
  "auto_resolved": false
}
```

### 12.2 에스컬레이션 레벨 매트릭스

| 상황 | 레벨 | 자동 복구 | 사용자 알림 | 관리자 알림 |
|------|------|----------|-----------|-----------|
| 캐시 HIT/MISS 정상 | — | — | N | N |
| 용량 80% (800/1000) 도달 | INFO | N | Y | N |
| 용량 100% + LRU eviction | WARN | Y | Y | N |
| 임베딩 산출 실패 (재시도 후 복구) | WARN | Y | N | N |
| 임베딩 산출 실패 (재시도 소진) | ERROR | 캐시 우회 | Y | Y |
| 캐시 엔트리 무결성 오류 | ERROR | 해당 엔트리 삭제 | Y | Y |
| 히트율 < 10% 지속 | WARN | N | Y | Y |
| LOCK-MR-010 위반 시도 | CRITICAL | N (설정 거부) | Y | Y |
| LOCK-MR-017 위반 시도 | CRITICAL | N (요청 거부) | Y | Y |

---

## 13. 로깅 규격 (R-01-7)

### 13.1 중첩 JSON 로그 구조

```json
{
  "log_id": "LOG-CACHE-{uuid}",
  "timestamp": "2026-04-13T10:30:00.123Z",
  "level": "INFO",
  "component": "SemanticCache",
  "operation": "get",
  "project_id": "proj_investment_01",
  "entity_id": "scache_001",
  "status": "CACHE_HIT",
  "duration_ms": 8,
  "details": {
    "query_text_truncated": "VAMOS 아키텍처 설명...",
    "similarity_score": 0.97,
    "hit_count": 5,
    "cache_stats": {
      "total_entries": 234,
      "active_entries": 210,
      "hit_ratio": 0.45
    }
  },
  "lock_checks": {
    "MR-010_similarity_threshold": "PASS (0.97 >= 0.95)",
    "MR-017_project_isolation": "PASS",
    "MR-015_deny_check": "N/A"
  },
  "trace_id": "TRACE-{session_uuid}"
}
```

### 13.2 로그 레벨 매핑

| 이벤트 | 레벨 | 포함 정보 |
|--------|------|----------|
| 캐시 HIT | INFO | operation=get, score, cache_id, hit_count |
| 캐시 MISS | INFO | operation=get, best_score, near_miss 여부 |
| 캐시 MISS (근접, 0.90~0.9499) | INFO | near_miss=true, score |
| 캐시 PUT 성공 | INFO | operation=put, cache_id, ttl_sec |
| 캐시 PUT (중복 갱신) | INFO | operation=put, action=update, cache_id |
| 무효화 (TTL/SOURCE/DRIFT/QOD) | INFO | invalidation_reason, affected_count |
| 수동 무효화 | INFO | invalidation_reason=MANUAL, pattern |
| 캐시 flush | WARN | project_id, evicted_count |
| LRU eviction | INFO | evicted_cache_id, last_accessed_at |
| 용량 경고 (80%) | WARN | current_count, max_entries, usage_pct |
| 임베딩 실패 | ERROR | error_type, retry_count |
| LOCK 위반 시도 | ERROR | lock_id, attempted_value, required_value |
| 히트율 < 10% | WARN | hit_ratio, total_hits, total_misses |

---

## 14. 시간복잡도 분석 (Big-O)

> N = 캐시 엔트리 수 (프로젝트당), D = 임베딩 차원 (256), S = source_refs 평균 길이

| 연산 | 시간복잡도 | 공간복잡도 | 비고 |
|------|----------|----------|------|
| `get()` — hash 정확 일치 | O(N) worst | O(1) | hash 인덱스 시 O(1) 가능 |
| `get()` — 의미 유사도 탐색 | O(N * D) | O(D) | N 엔트리 x D dim cosine |
| `put()` | O(N * D) | O(D) | 중복 검사 + 임베딩 산출 |
| `_evict_expired()` | O(N) | O(K) | K = 만료 엔트리 수 |
| `_evict_lru()` | O(N log N) | O(N) | 정렬 기반 LRU |
| `invalidate()` | O(1) | O(1) | 직접 lookup |
| `invalidate_by_source()` | O(N * S) | O(1) | 전체 순회 |
| `invalidate_by_drift()` | O(N * S * D) | O(D) | 순회 + cosine 비교 |
| `flush()` | O(N) | O(1) | dict clear |
| `stats()` | O(N) | O(1) | 전체 순회 |
| `_cosine_similarity()` | O(D) | O(1) | D=256 |
| `_compute_embedding()` | O(T) | O(D) | T = 모델 추론 시간 |

> **V1 성능 한계**: max_entries=1000, D=256이므로 get()의 worst case는 256,000 연산. 단일 쿼리 < 10ms 예상 (인메모리). V2에서 ANN 검색으로 O(log N) 전환 예정.

---

## 15. 예외 처리 정책 표

| 예외 상황 | 에러 코드 | 재시도 | 복구 전략 | fallback 응답 |
|-----------|----------|:------:|----------|--------------|
| similarity_threshold < 0.95 설정 시도 | CACHE_ERR_001 | N | 설정 거부, 기본값 유지 | 서비스 시작 거부 |
| 임베딩 모델 로드 실패 | CACHE_ERR_002 | Y (2회) | 모델 재로드 | 캐시 비활성화, RAG 직접 실행 |
| Deny 판정 + 캐시 저장 시도 | CACHE_ERR_003 | N | 저장 차단 | 응답 미캐싱 |
| project_id 누락 | CACHE_ERR_004 | N | 요청 거부 | 400 오류 |
| max_entries 초과 | CACHE_ERR_005 | Y (자동) | LRU eviction | 저장 후 가장 오래된 항목 제거 |
| 엔트리 무결성 실패 | CACHE_ERR_006 | N | 해당 엔트리 삭제 | MISS 반환 |
| 직렬화 오류 | CACHE_ERR_007 | N | 해당 엔트리 삭제 | MISS 반환 |
| 임베딩 타임아웃 | CACHE_ERR_008 | Y (2회) | 대기 후 재시도 | MISS 반환 (RAG fallback) |
| Drift > 0.05 감지 | CACHE_ERR_009 | — | 무효화 실행 | 정상 흐름 |
| QoD < 0.4 | CACHE_ERR_010 | — | 무효화 실행 | 정상 흐름 |
| 히트율 < 10% | CACHE_ERR_011 | — | 알림 발행 | 정상 운영 |
| flush 실패 | CACHE_ERR_012 | Y (1회) | 재시도 | 에스컬레이션 |

---

## 16. 단위 테스트 시나리오

| # | 테스트 ID | 시나리오 | 기대 결과 | LOCK 검증 |
|---|----------|---------|----------|-----------|
| 1 | UT-SC-001 | cosine=0.97 쿼리 → get() | HIT, 캐시 응답 반환 | MR-010 |
| 2 | UT-SC-002 | cosine=0.95 (경계값) → get() | HIT, 캐시 응답 반환 | MR-010 |
| 3 | UT-SC-003 | cosine=0.9499 → get() | MISS, response=None | MR-010 |
| 4 | UT-SC-004 | cosine=0.50 → get() | MISS, response=None | MR-010 |
| 5 | UT-SC-005 | 빈 캐시 → get() | MISS, score=-1.0 | — |
| 6 | UT-SC-006 | put() → get() 왕복 | HIT, 동일 응답 | MR-010 |
| 7 | UT-SC-007 | TTL 24시간 경과 후 get() | MISS (만료) | — |
| 8 | UT-SC-008 | source 변경 → invalidate_by_source() → get() | MISS (무효화) | — |
| 9 | UT-SC-009 | Drift > 0.05 → invalidate_by_drift() | 무효화 실행 | — |
| 10 | UT-SC-010 | QoD 0.3 → invalidate_by_qod_drop() | 무효화 실행 | — |
| 11 | UT-SC-011 | max_entries=1000 도달 → put() | LRU eviction + 저장 성공 | — |
| 12 | UT-SC-012 | project_id=A → put(), project_id=B → get() | MISS (격리) | MR-017 |
| 13 | UT-SC-013 | project_id="" → get() | ProjectIsolationError | MR-017 |
| 14 | UT-SC-014 | policy_decision=deny → put() | CacheDenyError | MR-015 |
| 15 | UT-SC-015 | flush(project_id) → get() | MISS (전체 삭제) | — |
| 16 | UT-SC-016 | 동일 query_text 2회 put() | 기존 엔트리 갱신 (중복 방지) | — |
| 17 | UT-SC-017 | 수동 invalidate(cache_id) → get() | MISS | — |
| 18 | UT-SC-018 | hash 정확 일치 (동일 텍스트) → get() | HIT (score=1.0, 임베딩 비교 생략) | — |
| 19 | UT-SC-019 | similarity_threshold=0.90 설정 시도 | CacheConfigError (LOCK 위반) | MR-010 |
| 20 | UT-SC-020 | 히트율 < 10% → stats() | WARN 로그 발행 | — |

---

## 17. Phase 2 통합 테스트

| # | 테스트 ID | 시나리오 | 연동 세션 | 검증 내용 |
|---|----------|---------|----------|----------|
| 1 | P2-T-SC-01 | L0 CRUD + Semantic Cache 중복 억제 | P1-1 | cosine >= 0.95 시 중복 L0 생성 억제 |
| 2 | P2-T-SC-02 | L1 CRUD + Semantic Cache 중복 검출 | P1-2 | cosine >= 0.95 시 중복 L1 생성 억제 |
| 3 | P2-T-SC-03 | Chroma search 스킵 (캐시 히트 시) | P1-3 | 캐시 HIT → ChromaVectorStore.search 미호출 |
| 4 | P2-T-SC-04 | RAG Pipeline Stage 5 우회 | P1-10 | 캐시 HIT → Retrieve+Generate 스킵 |
| 5 | P2-T-SC-05 | 캐시 무효화 + RAG Pipeline 재실행 | P1-10 | 소스 변경 → 캐시 무효화 → 다음 쿼리 시 RAG 재실행 |
| 6 | P2-T-SC-06 | PII 마스킹 + 캐시 저장 | P1-7 | restrict 마스킹된 응답이 캐시에 저장됨 |
| 7 | P2-T-SC-07 | PII Deny + 캐시 차단 | P1-7 | deny 판정 시 캐시 저장 차단 (LOCK-MR-015) |
| 8 | P2-T-SC-08 | Hybrid Search + 캐시 미스 fallback | P1-11 | MISS → Dense+Sparse 검색 정상 실행 |
| 9 | P2-T-SC-09 | GraphRAG 노드 변경 → 캐시 무효화 | P1-4 | 그래프 노드 갱신 → source_ref 연동 무효화 |
| 10 | P2-T-SC-10 | B-3 Decay + 캐시 엔트리 연동 | P1-8 | 메모리 decay 시 관련 캐시 무효화 |
| 11 | P2-T-SC-11 | 캐시 flush + 전체 RAG 재실행 | — | 관리자 flush → 모든 쿼리 RAG fallback |
| 12 | P2-T-SC-12 | project_id 격리 E2E | P1-1, P1-2 | 프로젝트 A 캐시가 프로젝트 B에 노출 안 됨 |

---

## 18. 세션 간 인터페이스 cross-check

### 18.1 P1-1 (L0 Session Memory CRUD) 접점

| 접점 | P1-1 측 | P1-5 측 | 정합 여부 |
|------|---------|---------|:---------:|
| L0 생성 전 캐시 확인 | P1-1 §11.2: P1-5 접점 — "cosine>=0.95 시 중복 L0 생성 억제" | §6.2: RAG Pipeline 연동 — HIT 시 L0 생성 스킵 | OK |
| project_id 격리 | P1-1: LOCK-MR-017 준수 | §9: LOCK-MR-017 격리 | OK |

### 18.2 P1-2 (L1 Project Memory CRUD) 접점

| 접점 | P1-2 측 | P1-5 측 | 정합 여부 |
|------|---------|---------|:---------:|
| L1 생성 전 캐시 확인 | P1-2 §12.2: P1-5 접점 — "cosine>=0.95 시 중복 L1 생성 억제" | §6.2: RAG Pipeline 연동 — HIT 시 L1 생성 스킵 | OK |
| project_id 격리 | P1-2: LOCK-MR-017 준수 | §9: LOCK-MR-017 격리 | OK |

### 18.3 P1-3 (Chroma Vector DB) 접점

| 접점 | P1-3 측 | P1-5 측 | 정합 여부 |
|------|---------|---------|:---------:|
| 캐시 HIT → search 스킵 | P1-3 §14 P2-T-08: "cosine>=0.95 캐시 히트 → 벡터 검색 미실행" | §6.2: HIT 시 RAG Pipeline Retrieve 단계 스킵 | OK |
| BGE-M3 256dim 공유 | P1-3: EmbeddingFunction BGE-M3 256dim | §3.1: 동일 모델/차원 사용 | OK |
| Deny 차단 | P1-3: LOCK-MR-015 | §5.2: Deny → 캐시 저장 차단 | OK |

### 18.4 P1-4 (JSON GraphRAG) 접점

| 접점 | P1-4 측 | P1-5 측 | 정합 여부 |
|------|---------|---------|:---------:|
| 그래프 노드 변경 → 캐시 무효화 | P1-4: 노드 CRUD 시 source_ref로 추적 가능 (이벤트 발행은 P2 통합 시 구현) | §7.3: invalidate_by_source — source_ref 연동 | OK (P2 통합 시 확인) |
| project_id 격리 | P1-4: LOCK-MR-017 3중 격리 | §9: LOCK-MR-017 격리 | OK |

### 18.5 P1-7 (PII 마스킹, 미래) 접점

| 접점 | 예상 P1-7 인터페이스 | P1-5 측 | 비고 |
|------|---------------------|---------|------|
| Restrict → 마스킹 후 캐시 저장 | PII 파이프라인 → 마스킹된 텍스트 반환 | §5: put()에 마스킹된 response_text 전달 | P1-7 구현 시 확인 필요 |
| Deny → 캐시 차단 | policy_decision=deny 전달 | §5.2: CacheDenyError 발생 | LOCK-MR-015 |

### 18.6 P1-10 (RAG Pipeline, 미래) 접점

| 접점 | 예상 P1-10 인터페이스 | P1-5 측 | 비고 |
|------|---------------------|---------|------|
| Stage 0: 캐시 조회 | RAG 진입 전 SemanticCache.get() 호출 | §6: get() API 제공 | P1-10 구현 시 확인 필요 |
| Stage 6 후: 캐시 저장 | Generate 완료 후 SemanticCache.put() 호출 | §5: put() API 제공 | P1-10 구현 시 확인 필요 |

### 18.7 P1-11 (Hybrid Search, 미래) 접점

| 접점 | 예상 P1-11 인터페이스 | P1-5 측 | 비고 |
|------|---------------------|---------|------|
| 캐시 MISS → Hybrid Search 실행 | Dense+Sparse 검색 호출 | §6.2: MISS 반환 → 호출측에서 RAG 실행 | P1-11 구현 시 확인 필요 |

---

## 19. LOCK-MR 참조 추적표

| LOCK-MR | 항목 | 본 문서 적용 위치 | 준수 상태 |
|---------|------|------------------|:---------:|
| LOCK-MR-010 | Semantic Cache cosine >= 0.95 | §1.2 config, §4 판정 로직, §6 get(), §15 예외, §16 UT-SC-001~004,019 | PASS |
| LOCK-MR-011 | BGE-M3 256dim 검색용 | §1.2 config, §3.1 임베딩 산출 | PASS |
| LOCK-MR-015 | Deny 벡터 삽입 금지 | §5.2 Deny 차단, §10 CACHE_ERR_003, §16 UT-SC-014 | PASS |
| LOCK-MR-017 | project_id 격리 | §9 전체, §16 UT-SC-012~013, §17 P2-T-SC-12 | PASS |
| LOCK-MR-007 | 6-Stage RAG Pipeline | §6.2 RAG 연동 흐름 (MISS → 6단계 실행) | PASS (참조) |
| LOCK-MR-018 | 저장 전 사용자 확인 | §5: put() 호출은 RAG Pipeline 이후 — 사용자 질의 응답 캐싱이므로 별도 확인 불필요 (참조) | N/A |
| LOCK-MR-019 | 루프 저장 폭주 방지 | §5: put()은 쿼리당 1회 — 반복 루프 중 원문 저장 없음 | PASS (참조) |

---

## 20. 교차 참조 블록

```yaml
cross_references:
  schema_sot:
    - ref: "[REF:D6:semantic-cache-schema:Schema:SemanticCacheSchema:v3.0.0]"
      usage: "§2 필드 매핑 전수, §2.2 CacheEntry 구조"
  design_sot:
    - ref: "D2.0-06 §4.7 (ADD-012, MOD-017)"
      usage: "§7 무효화 전략 5종, §8 캐시 크기 관리, §4 히트 판정"
    - ref: "D2.0-06 §4.7.2 (MOD-017)"
      usage: "§7.2 TTL 기반, §7.3 소스 변경, §7.5 QoD 변동, §7.6 수동 flush"
    - ref: "D2.0-06 §4.7.3"
      usage: "§8.3 CacheStats — 히트율/응답시간/크기 모니터링"
  step7_items:
    - ref: "S7D-048 (Semantic Cache 구현)"
      usage: "§1 GPTCache 참조 아키텍처, §7 무효화 정책"
  lock_refs:
    - "LOCK-MR-010: §1.2, §4.1, §4.3, §6.1, §10, §16"
    - "LOCK-MR-011: §1.2, §3.1"
    - "LOCK-MR-015: §5.2, §10, §16"
    - "LOCK-MR-017: §9, §16, §17"
  session_deps:
    - "P0-3 chroma_collection_strategy → §3.1 임베딩 모델/차원"
    - "P0-4 vectorstore_abc.py → §3.1 EmbeddingFunction 재사용"
    - "P1-1 L0_session_memory_crud → §18.1 중복 L0 억제"
    - "P1-2 L1_project_memory_crud → §18.2 중복 L1 억제"
    - "P1-3 chroma_adapter → §18.3 search 스킵, BGE-M3 공유"
    - "P1-4 json_graphrag → §18.4 노드 변경 연동"
  future_deps:
    - "P1-7 PII 마스킹 → §18.5 Deny/Restrict 연동"
    - "P1-10 RAG Pipeline → §18.6 get()/put() 호출"
    - "P1-11 Hybrid Search → §18.7 MISS fallback"
  part2_guide:
    - ref: "Part2 V1-Phase 2 항목5"
      usage: "§1.2 파라미터 표, §7 무효화 정책 3종"
  acceptance_criteria:
    - "AC-D6-010: similarity_threshold 0.95 이상만 캐시 히트 (LOCK)"
```

---

## 21. I-4 SHELL->FULL 전환 명세

### 21.1 I-4 이전 상태 (SHELL)

> §6 이슈 테이블 I-4: "Semantic Cache 무효화 상세 — 3가지 정책명만 나열 (TTL/Drift/수동)"

### 21.2 I-4 이후 상태 (FULL) — 본 문서에서 완성

| 항목 | SHELL 상태 | FULL 상태 (본 문서) | 위치 |
|------|-----------|-------------------|------|
| 무효화 정책 수 | 3가지 명칭만 | 5종 상세 (TTL/소스변경/Drift/QoD/수동) | §7.1 |
| TTL 기반 | "TTL 기반" 한 줄 | 만료 판정 로직 + lazy eviction + 6시간 단축 옵션 | §7.2 |
| 소스 변경 연동 | (미정의) | invalidate_by_source() 구현 + source_refs 매칭 | §7.3 |
| Embedding Drift | "Drift" 명칭만 | drift_threshold=0.05 + cosine 차이 비교 + 무효화 흐름 | §7.4 |
| QoD 변동 연동 | (미정의) | QoD < 0.4 감지 + 관련 캐시 무효화 | §7.5 |
| 수동 무효화 | "수동" 명칭만 | invalidate/invalidate_by_pattern/flush/flush_all 4메서드 | §7.6 |
| 무효화 이벤트 기록 | (미정의) | cache.invalidated event_type + EventBus 발행 | §7.7 |
| 무효화 사유 추적 | (미정의) | invalidation_reason 필드 6종 | §2.1 |
| 에러 코드 | (미정의) | CACHE_ERR_009 (Drift), CACHE_ERR_010 (QoD) | §10 |
| 복구 전략 | (미정의) | INVALIDATE Phase 복구 매트릭스 | §11.1 |

### 21.3 I-4 전환 확인

- [x] TTL 기반 무효화: 구현 로직 상세 (§7.2)
- [x] Embedding Drift 기반 무효화: 구현 로직 상세 (§7.4)
- [x] 소스 변경 연동 무효화: 구현 로직 상세 (§7.3)
- [x] QoD 변동 연동 무효화: 구현 로직 상세 (§7.5)
- [x] 수동 무효화 (4메서드): 구현 로직 상세 (§7.6)
- [x] 무효화 이벤트 기록: EventBus 발행 (§7.7)

**I-4 전환 결과: SHELL -> FULL 완료**

---

## 검증 체크리스트

- [x] cosine >= 0.95 히트 판정 정확 (LOCK-MR-010) — §4.1, §4.3
- [x] cosine < 0.95 시 캐시 미스 -> RAG 실행 — §4.1, §6.2
- [x] 캐시 무효화 전략 문서화 (I-4 SHELL->FULL) — §7 전체, §21
- [x] 캐시 크기 관리 정책 정의 — §8 (LRU, max_entries=1000)
- [x] TTL=24시간, max_entries=1000 설정 준수 — §1.2, §8.2
- [x] D6 SemanticCacheSchema 8필드 전수 매핑 — §2
- [x] project_id 격리 — §9 (LOCK-MR-017)
- [x] Deny 판정 시 캐시 저장 금지 — §5.2 (LOCK-MR-015)

---

*문서 끝 — P1-5 Semantic Cache v1.0 (2026-04-13)*
