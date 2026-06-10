# layer_pipeline.md — 10-Layer 파이프라인 알고리즘 상세 (L1~L10)

> **도메인**: 6-8_Cloud-Library / 01_cloud-deploy
> **역할**: L1 INPUT ~ L10 OUTPUT 각 Layer의 입력·출력·핵심 알고리즘·라이브러리 힌트·V1/V2/V3 구현 단계 명세
> **LOCK 참조**: L1 (10-Layer 파이프라인 아키텍처) — 정본 선언. 운영 제약 L9~L21 인라인 참조
> **DEFINED-HERE 참조**: 없음 (본 파일은 LOCK L1의 파생 상세 문서)
> **수정 정책**: 정본 — Phase 변경 시 갱신
> **작성 세션**: P1-1 (2026-04-14)
> **상위 정본**: `AUTHORITY_CHAIN.md §3 LOCK L1`, `CLOUD_LIBRARY_구조화_종합계획서.md §3.4 L1 / 부록 A.4`

---

## §1. 교차 참조 블록

| 참조 대상 | 경로 | 섹션 | 용도 |
|----------|------|------|------|
| LOCK 레지스트리 (L1, L2, L3, L9~L21) | `D:\VAMOS\docs\sot 2\6-8_Cloud-Library\AUTHORITY_CHAIN.md` | §3 | LOCK 정본 — 본 파일의 상위 근거 |
| DH-CL-D1 (배포 전략) | `D:\VAMOS\docs\sot 2\6-8_Cloud-Library\AUTHORITY_CHAIN.md` | §4 | V1/V2/V3 구현 단계 매핑 |
| 종합계획서 §3.4 LOCK L1 | `CLOUD_LIBRARY_구조화_종합계획서.md` | §3.4 | 10-Layer 아키텍처 정본 |
| 종합계획서 §6.1 P4 / §6.2 ISS-3 | `CLOUD_LIBRARY_구조화_종합계획서.md` | §6 | Layer별 알고리즘 힌트 미상세 해소 대상 |
| 종합계획서 부록 A.4 (S10-3 힌트) | `CLOUD_LIBRARY_구조화_종합계획서.md` | 부록 A.4 | Layer별 알고리즘 힌트 원천 |
| 평가 점수 체계 (L2/L3) | `01_cloud-deploy/scoring_system.md` | (P1-2 산출) | L3 EVALUATION 알고리즘 세부 위임 |
| 배포 전략 (V1/V2/V3) | `01_cloud-deploy/deployment_strategy.md` | (P1-3 산출) | Layer별 V1/V2/V3 배포 매핑 |
| VectorStore (BGE-M3 1024dim) | 6-4 Memory-RAG-Storage `LOCK-MR-011` | — | L10 OUTPUT 임베딩 연동 |
| 01_cloud-deploy 색인 | `01_cloud-deploy/_index.md` | §3 | 10-Layer 전체 목록 |

---

## §2. LOCK L1 선언 참조

본 파일은 **AUTHORITY_CHAIN.md §3 LOCK L1** (10-Layer 파이프라인 아키텍처: L1 INPUT → L2 DISCOVERY → L3 EVALUATION → L4 COLLECTION → L5 DATA LAKE → L6 EXTRACTION → L7 ANALYSIS → L8 VALIDATION → L9 VERSION CONTROL → L10 OUTPUT) 의 **파생 상세 문서**이다.

- **LOCK L1 원문 출처**: `VAMOS_CLOUD_LIBRARY_SPEC §1~§4`
- **변경 정책**: LOCK L1 자체는 상위 정본 갱신 없이는 변경 불가. 본 파일은 L1의 각 Layer 알고리즘 힌트만 상세화하며, Layer의 순서/이름/개수 변경 금지.
- **본 파일이 정의하는 범위**: 각 Layer의 (a) 입력 명세, (b) 출력 명세, (c) 핵심 알고리즘, (d) 라이브러리 힌트, (e) V1/V2/V3 구현 로직, (f) 시간복잡도, (g) 인라인 LOCK 제약.

---

## §3. L1~L10 Layer 테이블

| Layer ID | Layer명 | 입력 (Input) | 출력 (Output) |
|----------|---------|--------------|---------------|
| L1 | INPUT | 소스 URL(str) + 메타데이터(dict: source_type, priority, submitted_at) | `ValidatedSource` (url, robots_allowed, rate_limit_ms, metadata) |
| L2 | DISCOVERY | `ValidatedSource` | `DiscoveredLinkSet` (root_url, links: List[URL], depth_map, crawl_order) |
| L3 | EVALUATION | `DiscoveredLinkSet` 또는 개별 소스 메타 | `EvaluationScore` (trust, relevance, quality, access, total, source_type_weight) |
| L4 | COLLECTION | `EvaluationScore` 통과분 + URL | `CollectedContent` (raw_html, markdown, size_bytes, content_type, multimedia_meta) |
| L5 | DATA LAKE | `CollectedContent` | `DataLakeRecord` (record_id, storage_path, metadata≤10KB, quality_gate_passed) |
| L6 | EXTRACTION | `DataLakeRecord` | `StructuredInfo` (entities, keywords, summary, consistency_score) |
| L7 | ANALYSIS | `StructuredInfo` + 교차 소스 | `AnalysisReport` (claim_verification, cross_source_consistency, security_score) |
| L8 | VALIDATION | `AnalysisReport` + 4-Gate 누적 점수 | `ValidationResult` (total_score, gate_pass: bool, archive_only: bool) |
| L9 | VERSION CONTROL | `ValidationResult` (통과분) + 이전 `content_hash` | `VersionedRecord` (version_id, content_hash, change_diff, next_crawl_at) |
| L10 | OUTPUT | `VersionedRecord` | `IndexedEmbedding` (vector_id, embedding_1024dim, vectorstore_ref) |

---

## §4. Layer별 알고리즘 상세

### L1. INPUT

**LOCK 인라인**: L10 (크롤링 간격 ≥1초/도메인, robots.txt 준수)

- **입력 명세**: `source_url: str`, `metadata: {source_type, priority, submitted_at}`
- **출력 명세**: `ValidatedSource(url, robots_allowed: bool, rate_limit_ms: int≥1000, metadata)`
- **핵심 알고리즘**: URL 파싱 + robots.txt 검증
- **라이브러리 힌트 (S10-3)**: `urllib.parse`, `urllib.robotparser`
- **V1 로직**: 단일 URL 단위로 동기 검증. robots.txt fetch 실패 시 default-deny.
- **V2 로직**: robots.txt 캐시(TTL=24h, LOCK L13) 도입, 병렬 검증.
- **V3 로직**: Redis 공유 캐시 + 도메인별 rate-limit 버킷(K8s ConfigMap).
- **시간복잡도**: O(1) per URL (robots.txt 캐시 가정). 캐시 미스 시 O(1) + 네트워크 RTT.
- **ABC 패턴 매핑**: Validator — `validate(ValidatedSource) -> bool`.

### L2. DISCOVERY

**LOCK 인라인**: L11 (max_depth=3), L9 (최대 동시 크롤러=5), L10 (간격 ≥1초)

- **입력 명세**: `ValidatedSource`
- **출력 명세**: `DiscoveredLinkSet(root_url, links: List[URL], depth_map: Dict[URL,int], crawl_order: List[URL])`
- **핵심 알고리즘**: 링크 추출 + BFS 크롤링 (깊이 ≤3)
- **라이브러리 힌트 (S10-3)**: `BeautifulSoup` (HTML 파싱) + `asyncio` 비동기 크롤링
- **V1 로직**: BFS 단일 도메인 크롤. 큐 기반, `seen` 셋으로 중복 제거.
- **V2 로직**: REST API 소스 탐색 추가(사이트맵/JSON-API 우선), 워커 풀=5 (LOCK L9).
- **V3 로직**: Sitemap priority + 적응형 깊이(품질 피드백), K8s Job 분산.
- **시간복잡도**: O(V + E) — V=페이지 수, E=링크 수. max_depth=3 (LOCK L11)로 상계.
- **ABC 패턴 매핑**: Crawler — `async crawl(ValidatedSource) -> DiscoveredLinkSet`.

### L3. EVALUATION

**LOCK 인라인**: L2 (점수 4카테고리 배점), L3 (소스 신뢰도 가중치)

- **입력 명세**: `DiscoveredLinkSet` 또는 개별 소스 메타
- **출력 명세**: `EvaluationScore(trust≤25, relevance≤30, quality≤25, access≤20, total≤100, source_type_weight ∈[0.3,1.0])`
- **핵심 알고리즘**: 4카테고리 가중 합산 + 소스 타입 가중치 적용
  - `total = (trust × source_type_weight) + relevance + quality + access` (상세 공식은 scoring_system.md §5)
- **라이브러리 힌트 (S10-3)**: 규칙 기반(V1) → LLM 기반(V2+). 상세 scoring_system.md에 위임.
- **V1 로직**: 규칙 기반 점수(도메인 whitelist, keyword match). LOCK L3 가중치 하드코딩.
- **V2 로직**: LLM 기반 Quality/Relevance 재평가 + 통계적 Trust 보정.
- **V3 로직**: ML 분류기 + 사용자 피드백 루프.
- **시간복잡도**: O(n) — n=카테고리 수(고정=4). LLM 경로는 O(토큰 수).
- **ABC 패턴 매핑**: Scorer — `score(source) -> EvaluationScore`. 세부는 `scoring_system.md` 참조.

### L4. COLLECTION

**LOCK 인라인**: L12 (단일 소스 최대 50MB), L10 (간격 ≥1초)

- **입력 명세**: `EvaluationScore` 통과분 + URL
- **출력 명세**: `CollectedContent(raw_html, markdown, size_bytes ≤ 50MB, content_type, multimedia_meta)`
- **핵심 알고리즘**: 콘텐츠 수집 + HTML→Markdown 변환 + 멀티미디어 메타 추출
- **라이브러리 힌트 (S10-3)**: `readability-lxml`, `markdownify`
- **V1 로직**: 단일 페이지 fetch → readability 본문 추출 → markdownify 변환. 50MB 초과 시 즉시 거절.
- **V2 로직**: 멀티미디어 메타(이미지 alt, 비디오 transcript 플레이스홀더) 추가.
- **V3 로직**: Headless browser (Playwright) 동적 콘텐츠 수집, CDN 오프로딩.
- **시간복잡도**: O(n) — n=HTML 크기 바이트. 50MB 상계(LOCK L12)로 O(50MB) 고정.
- **ABC 패턴 매핑**: Collector — `async collect(url, score) -> CollectedContent`.

### L5. DATA LAKE

**LOCK 인라인**: L14 (최대 저장 소스 수=10,000), L18 (메타데이터 ≤10KB/소스), L19 (Quality ≥40)

- **입력 명세**: `CollectedContent`
- **출력 명세**: `DataLakeRecord(record_id, storage_path, metadata≤10KB, quality_gate_passed: bool)`
- **핵심 알고리즘**: 원본 저장 + 메타데이터 색인 + CL-G1 품질 필터
- **라이브러리 힌트 (S10-3)**: SQLite(V1) / PostgreSQL(V2+). Object store는 로컬 파일시스템(V1) → S3 호환(V3).
- **V1 로직**: SQLite + 로컬 파일시스템. Quality <40 시 아카이브 only 플래그.
- **V2 로직**: PostgreSQL + full-text index. LOCK L14 도달 시 LRU 퇴거.
- **V3 로직**: 분산 object store + 파티셔닝(날짜/source_type).
- **시간복잡도**: 저장 O(1), 조회 인덱스 O(log n), n=저장 소스 수 ≤ 10,000 (LOCK L14).
- **ABC 패턴 매핑**: Storage — `persist(CollectedContent) -> DataLakeRecord`.

### L6. EXTRACTION

**LOCK 인라인**: L20 (Consistency ≥50)

- **입력 명세**: `DataLakeRecord`
- **출력 명세**: `StructuredInfo(entities: List[Entity], keywords: List[str], summary: str, consistency_score ≤100)`
- **핵심 알고리즘**: NER + 키워드 추출 + 요약 생성 + CL-G2 일관성 체크
- **라이브러리 힌트 (S10-3)**: `spaCy` (NER), `YAKE` 또는 TF-IDF (키워드)
- **V1 로직**: spaCy en_core_web_sm + YAKE 키워드(top-k=10) + extractive 요약.
- **V2 로직**: 다국어 모델(xx_ent_wiki_sm) + LLM 요약(abstractive).
- **V3 로직**: 도메인 특화 NER 파인튜닝 + 구조화 스키마 출력(JSON-LD).
- **시간복잡도**: NER O(n), TF-IDF O(n log n), n=토큰 수. LLM 경로는 O(토큰 수) 네트워크 경계.
- **ABC 패턴 매핑**: Extractor — `extract(DataLakeRecord) -> StructuredInfo`.

### L7. ANALYSIS

**LOCK 인라인**: CL-G3 보안 ≥30 (LOCK L7 Gate)

- **입력 명세**: `StructuredInfo` + 교차 소스 레코드 N개
- **출력 명세**: `AnalysisReport(claim_verification: Dict, cross_source_consistency ≤100, security_score ≤100)`
- **핵심 알고리즘**: Claim verification + 교차 소스 일관성 분석 + 악성 URL/허위 정보 필터
- **라이브러리 힌트 (S10-3)**: V1 규칙 기반(블랙리스트 DB) → V2+ LLM 심층 분석
- **V1 로직**: 악성 URL DB 조회 + 중복 claim 집계.
- **V2 로직**: LLM 기반 claim verification + semantic similarity 교차 검증.
- **V3 로직**: 실시간 위협 인텔리전스 피드 + ML 허위 정보 탐지.
- **시간복잡도**: O(N²) 교차 소스 pairwise. LSH/embedding 인덱스로 O(N log N) 축약 가능(V2+).
- **ABC 패턴 매핑**: Analyzer — `analyze(StructuredInfo, peers) -> AnalysisReport`.

### L8. VALIDATION

**LOCK 인라인**: CL-G4 종합 ≥60 (LOCK L8 Gate)

- **입력 명세**: `AnalysisReport` + 누적 Gate 점수 (G0/G1/G2/G3)
- **출력 명세**: `ValidationResult(total_score ≤100, gate_pass: bool, archive_only: bool)`
- **핵심 알고리즘**: CL-G0~CL-G4 5개 Gate 누적 통과 검증 + 종합 점수 계산 (Gate 상세는 Phase 2 gate_details.md)
- **라이브러리 힌트 (S10-3)**: 내부 판정 로직(외부 라이브러리 불요)
- **V1 로직**: 선형 Gate 통과 확인. 실패 시 archive_only=True.
- **V2 로직**: 부분 점수 허용(특정 Gate 재시도 정책).
- **V3 로직**: 자율 품질 진화(Gate 임계값 자동 조정).
- **시간복잡도**: O(1) — Gate 수 고정=5 (CL-G0~CL-G4).
- **ABC 패턴 매핑**: Validator — `validate(AnalysisReport, gate_scores) -> ValidationResult`.

### L9. VERSION CONTROL

**LOCK 인라인**: L16 (재크롤링 주기=7일)

- **입력 명세**: `ValidationResult` 통과분 + 이전 `content_hash`
- **출력 명세**: `VersionedRecord(version_id, content_hash: SHA-256, change_diff, next_crawl_at)`
- **핵심 알고리즘**: `content_hash` (SHA-256) 비교 + 변경 이력 기록
- **라이브러리 힌트 (S10-3)**: `hashlib.sha256`, diff는 `difflib` (V1) → 의미 기반 diff(V2+)
- **V1 로직**: SHA-256 해시 비교. 변경 시 새 version_id 발급.
- **V2 로직**: 의미 기반 diff(embedding 유사도 임계).
- **V3 로직**: Git-like branch/merge.
- **시간복잡도**: SHA-256 O(n) — n=콘텐츠 바이트. 비교는 O(1).
- **ABC 패턴 매핑**: VersionManager — `version(ValidationResult, prev_hash) -> VersionedRecord`.

### L10. OUTPUT

**LOCK 인라인**: L15 (임베딩 배치=32), L17 (동시 임베딩 워커=2)

- **입력 명세**: `VersionedRecord`
- **출력 명세**: `IndexedEmbedding(vector_id, embedding: Vector[1024], vectorstore_ref)`
- **핵심 알고리즘**: BGE-M3 1024dim 임베딩 생성 + VectorStore 인덱싱
- **라이브러리 힌트 (S10-3)**: BGE-M3 (6-4 `LOCK-MR-011`), `FlagEmbedding` 또는 `sentence-transformers`
- **V1 로직**: 로컬 BGE-M3 + FAISS index. batch=32 (LOCK L15), 워커=2 (LOCK L17).
- **V2 로직**: VectorStore (I-2 RAG) 연동 업서트.
- **V3 로직**: 분산 임베딩(K8s Job) + ANN 인덱스(HNSW) 샤딩.
- **시간복잡도**: 임베딩 O(m) — m=토큰 수. 배치 처리로 상각 O(m/32). 인덱스 삽입 O(log N) (HNSW).
- **ABC 패턴 매핑**: Embedder — `embed(VersionedRecord) -> IndexedEmbedding`.

---

## §5. 공통 자료 구조 선정의 (Pydantic 스케치)

> 본 섹션은 L1~L10 출력 타입의 공통 자료 구조를 선정의한다. 상세 스키마는 Phase 2 common_types(있을 시)에 위임, 여기서는 최소 필드만 고정.

```python
from pydantic import BaseModel
from typing import List, Dict, Optional

class ValidatedSource(BaseModel):
    url: str
    robots_allowed: bool
    rate_limit_ms: int  # ≥1000 (LOCK L10)
    metadata: Dict

class DiscoveredLinkSet(BaseModel):
    root_url: str
    links: List[str]
    depth_map: Dict[str, int]  # max=3 (LOCK L11)
    crawl_order: List[str]

class EvaluationScore(BaseModel):
    # L3 EVALUATION 출력 — 상세 정본은 scoring_system.md §6 EvaluationScore
    # 본 파일은 L3 Layer 경계에서의 최소 필드만 선언. scoring_system.md의 EvaluationScore(source_weight, subscores, band 등)와 정합.
    trust: float              # ≤25 (LOCK L2) — scoring_system.md trust_raw에 대응
    relevance: float          # ≤30           — scoring_system.md relevance_raw에 대응
    quality: float            # ≤25           — scoring_system.md quality_raw에 대응
    access: float             # ≤20           — scoring_system.md access_raw에 대응
    total: float              # ≤100          — scoring_system.md total_score에 대응
    source_type_weight: float # ∈[0.3,1.0] (LOCK L3) — scoring_system.md source_weight에 대응 (별칭)

class CollectedContent(BaseModel):
    raw_html: bytes
    markdown: str
    size_bytes: int  # ≤50MB (LOCK L12)
    content_type: str
    multimedia_meta: Dict

class DataLakeRecord(BaseModel):
    record_id: str
    storage_path: str
    metadata: Dict   # ≤10KB (LOCK L18)
    quality_gate_passed: bool  # CL-G1 (≥40, LOCK L19)

class StructuredInfo(BaseModel):
    entities: List[Dict]
    keywords: List[str]
    summary: str
    consistency_score: float  # CL-G2 (≥50, LOCK L20)

class AnalysisReport(BaseModel):
    claim_verification: Dict
    cross_source_consistency: float
    security_score: float  # CL-G3 (≥30)

class ValidationResult(BaseModel):
    total_score: float  # CL-G4 (≥60)
    gate_pass: bool
    archive_only: bool

class VersionedRecord(BaseModel):
    version_id: str
    content_hash: str  # SHA-256
    change_diff: Optional[str]
    next_crawl_at: str  # +7d (LOCK L16)

class IndexedEmbedding(BaseModel):
    vector_id: str
    embedding: List[float]  # 1024-dim (LOCK-MR-011)
    vectorstore_ref: str
```

---

## §6. 예외 처리 정책 표

| error_code | 발생 Layer | recoverable | 처리 |
|------------|-----------|-------------|------|
| `E_L1_ROBOTS_FETCH` | L1 | yes | default-deny, 1회 재시도 후 skip |
| `E_L1_URL_INVALID` | L1 | no | 즉시 거부 (CL-G0 실패) |
| `E_L2_DEPTH_EXCEEDED` | L2 | no | max_depth=3 초과 링크 drop (LOCK L11) |
| `E_L2_CRAWLER_BUSY` | L2 | yes | 큐 백오프, 워커≤5 (LOCK L9) |
| `E_L3_SCORE_BELOW_G1` | L3 | no | Quality <40 → 수집 거부 (저장 ❌, LOCK L5 '실패 → 수집 거부'; L19=점수 최소 40) |
| `E_L4_SIZE_EXCEEDED` | L4 | no | 50MB 초과 시 거부 (LOCK L12) |
| `E_L5_STORAGE_FULL` | L5 | yes | LRU 퇴거 (최대 10,000, LOCK L14) |
| `E_L6_NER_TIMEOUT` | L6 | yes | 규칙 기반 fallback |
| `E_L7_SECURITY_FAIL` | L7 | no | CL-G3 score <30 → 수집 중단 |
| `E_L8_GATE_FAIL` | L8 | yes (archive) | 종합 <60 → archive_only (LOCK L8) |
| `E_L9_HASH_COLLISION` | L9 | yes | 재크롤 스케줄 (LOCK L16) |
| `E_L10_EMBED_FAIL` | L10 | yes | 배치 분할 재시도, 워커=2 (LOCK L17) |

---

## §7. Phase별 복구 전략 (다운그레이드 + confidence penalty)

```
[L1~L2 실패] ──► 수집 거부 (CL-G0) ──► 비복구 코드(E_L1_URL_INVALID 등)만 I-20 에스컬레이션, 나머지는 로그만
[L3 실패]    ──► downgrade: quality gate bypass → archive_only
[L4~L5 실패] ──► 재시도(최대 1회) → 실패 시 archive_only
[L6~L7 실패] ──► downgrade: V2 LLM → V1 규칙 기반 fallback
[L8 실패]    ──► archive_only (CL-G4 미달)
[L9~L10 실패]──► 배치 재시도 → 실패 시 다음 주기(+7d, LOCK L16)로 지연
```

**Confidence penalty 표**:

| 다운그레이드 | penalty |
|--------------|---------|
| V2 LLM → V1 규칙 기반 (L3/L6/L7) | -0.15 |
| 부분 gate 통과 (L8) | -0.10 |
| 재크롤 지연 (L9/L10) | -0.05 |
| archive_only 전환 (L5/L8) | -0.30 |

---

## §8. 에스컬레이션 페이로드 구조 (I-20 경유, R-01-8)

```python
class EscalationPayload(BaseModel):
    source_engine: str          # "L{N}" 형식, 예: "L7"
    error_code: str             # §6 표의 error_code
    original_request: Dict      # 원 입력(직렬화)
    partial_result: Optional[Dict]  # 실패 전까지의 Layer 출력
    retry_count: int
    timestamp: str              # ISO 8601 UTC
    trace_id: str               # R-01-7 로깅과 공유
```

에스컬레이션 대상: L7 security fail (`E_L7_SECURITY_FAIL`), L1 URL invalid (`E_L1_URL_INVALID`), L4 size exceeded (`E_L4_SIZE_EXCEEDED`) 등 비복구 오류는 I-20으로 전달하여 상위 오케스트레이터 결정.

---

## §9. 로깅 포맷 (R-01-7 structured JSON)

```json
{
  "trace_id": "cl-p-<uuid4>",
  "layer": "L3",
  "timestamp": "2026-04-14T10:00:00Z",
  "error": {
    "code": "E_L3_SCORE_BELOW_G1",
    "message": "Quality score 32 < 40 (LOCK L19)",
    "severity": "warn"
  },
  "context": {
    "source_url": "https://example.com/article",
    "source_type": "blog",
    "scores": {"trust": 14, "relevance": 20, "quality": 32, "access": 18}
  },
  "recovery": {
    "action": "archive_only",
    "confidence_penalty": -0.30,
    "retry_count": 0
  }
}
```

---

## §10. Phase 2 통합 테스트 시나리오 (10건+)

| # | 시나리오 | 주입 방법 | 기대 결과 |
|---|---------|----------|-----------|
| T-01 | L1 robots.txt 거부 | `robots_allowed=False` stub | `ValidatedSource` 생성 안 됨, 수집 거부(CL-G0) |
| T-02 | L2 max_depth 초과 | depth=4 링크 주입 | depth=3 링크만 포함 (LOCK L11) |
| T-03 | L2 동시 크롤러 6개 요청 | 6개 URL 동시 | 5개 실행 + 1개 대기 (LOCK L9) |
| T-04 | L3 블로그 가중치 적용 | `source_type=blog` | `source_type_weight=0.7` (LOCK L3), total 감소 확인 |
| T-05 | L4 50MB 초과 콘텐츠 | 51MB HTML stub | `E_L4_SIZE_EXCEEDED`, 수집 거부 |
| T-06 | L5 Quality 39점 | score.quality=39 | `quality_gate_passed=False`, archive_only 플래그 |
| T-07 | L5 저장 한도 초과 | 10,001 번째 소스 | LRU 퇴거 (LOCK L14) |
| T-08 | L6 Consistency 49 | StructuredInfo.consistency=49 | CL-G2 미달(LOCK L20), priority 강등 |
| T-09 | L7 악성 URL DB hit | malicious_url_list 주입 | security_score<30, 수집 중단, I-20 에스컬레이션 |
| T-10 | L8 종합점수 59 | gate_scores 합=59 | `gate_pass=False`, `archive_only=True` (CL-G4) |
| T-11 | L9 content_hash 불변 | 동일 콘텐츠 재수집 | 새 version_id 미발급, next_crawl_at=+7d (LOCK L16) |
| T-12 | L10 임베딩 배치 32 | 33건 입력 | 32+1 배치 분할 (LOCK L15), 워커=2 (LOCK L17) |
| T-13 | 전체 Happy path | 공식 문서(weight=1.0) | L1~L10 완주, `IndexedEmbedding` 생성 |
| T-14 | V1→V2 downgrade | L6 LLM timeout | 규칙 기반 fallback, penalty=-0.15 |

---

## §11. 세션 간 인터페이스 cross-check

| 대상 세션 | 산출물 | 인터페이스 | 정합 상태 |
|----------|--------|-----------|-----------|
| P1-2 | `scoring_system.md` | L3 `EvaluationScore` 필드(trust/relevance/quality/access/total/source_type_weight) | 본 파일 §5에 공통 자료 구조 선정의 — P1-2가 동일 필드 준수 필요 |
| P1-3 | `deployment_strategy.md` | V1/V2/V3 각 Layer 배포 매핑 | 본 파일 §4의 V1/V2/V3 로직 기준, P1-3가 인프라 매핑 |
| Phase 2 P2-1 | `gate_details.md` | L4/L5/L6/L7/L8 Gate 점수 임계값 | CL-G0~G4 임계값은 LOCK L4~L8 준수, 본 파일은 Layer 로직만 기술 |

세션 간 인터페이스 불일치는 발견되지 않음.

---

## §12. ISS-3 해결 표기

**ISS-3 해결**: S10-3 힌트 통합 완료 — 부록 A.4(S10-3)의 10-Layer 알고리즘 힌트 전 10건을 §4 각 Layer 섹션에 인라인 반영. 핵심 라이브러리(BeautifulSoup, spaCy, BGE-M3, readability-lxml, markdownify, YAKE, urllib.robotparser 등) 힌트 제공. ✅ DEFINED-HERE (layer_pipeline.md §4).

**P4 해결**: Layer별 알고리즘 미상세 — §4에서 L1~L10 전 Layer에 핵심 알고리즘·라이브러리 힌트·V1/V2/V3 구현 로직·시간복잡도 명세로 해소. ✅

---

## §13. 변경 이력

| 일시 | 세션 | 변경 | 비고 |
|------|------|------|------|
| 2026-04-14 | P1-1 | 최초 작성 | LOCK L1 파생, ISS-3/P4 해결 |
