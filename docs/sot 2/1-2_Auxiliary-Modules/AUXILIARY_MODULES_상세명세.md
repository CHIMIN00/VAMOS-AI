# 1-2. Auxiliary I-Series Modules 상세명세

> **Tier**: 1 - Core Intelligence (ORANGE CORE 내부)
> **Part2 상태**: PARTIAL (2~3줄 + SOT 포인터만)
> **SOT 근거**: D2.0-01 S5.6, D2.0-02 S7, D2.0-06
> **Part2 위치**: V1-Phase 1 (L1679~1717), V1-Phase 6 (L2600)

---

## 개요

ORANGE CORE 내 보조 모듈들로, Part2에 2~3줄 설명과 SOT 문서 포인터만 존재. 구현에 필요한 인터페이스, 파이프라인, 알고리즘, 트리거 조건 등이 부재.

---

## I-4: Multimodal Interpreter (멀티모달 해석기)

### 현재 Part2 내용 (L1679~1682)
```
I-4 Multimodal Interpreter: 텍스트/이미지/음성 입력 해석
```

### 필요한 상세내용

#### 1. 입출력 스키마
- **Input**: `RawInput`
  - `content: bytes | str` -- 원본 입력
  - `mime_type: str` -- MIME 타입 (자동 감지 가능)
  - `source: Literal["chat", "upload", "clipboard", "mic", "camera"]`
- **Output**: `InterpretedInput`
  - `modality: str` -- 감지된 모달리티
  - `text_content: Optional[str]` -- 텍스트 변환 결과
  - `embeddings: Optional[list[float]]` -- 임베딩 벡터
  - `metadata: dict` -- 해상도, 길이, 언어 등
  - `confidence: float` -- 해석 신뢰도

#### 2. 포맷 감지 로직
```
입력 수신
  ↓
[MIME 타입 감지] magic bytes / Content-Type / 확장자
  ↓
분기:
  text/* → 언어 감지 (langdetect) → 토큰화
  image/* → 이미지 전처리 (PIL) → CLIP 임베딩 + OCR
  audio/* → Whisper STT → 텍스트 + 감정 분석
  video/* → FFmpeg 프레임 추출 → 키프레임 분석 + STT
  application/pdf → docling/Unstructured → 구조화 텍스트
  unknown → fallback: 바이너리 → 텍스트 추출 시도
```

#### 3. 처리 파이프라인 상세

##### 텍스트 입력
- 언어 감지: langdetect (한국어/영어/일본어/중국어)
- 인코딩 감지: chardet
- 토큰화: tiktoken (GPT), sentencepiece (로컬 모델)

##### 이미지 입력
- 전처리: PIL → resize (max 2048px) → normalize
- CLIP 임베딩: openai/clip-vit-large-patch14
- OCR: Tesseract (한/영/일) + EasyOCR (fallback)
- 객체 감지: YOLO (선택적, V3)

##### 음성 입력
- STT: Whisper large-v3 (로컬) / Deepgram (클라우드 fallback)
- 언어 자동 감지
- 감정 분석: 음성 톤 + 텍스트 감정 이중 분석
- VAD (Voice Activity Detection): 무음 구간 제거

##### 문서 입력
- PDF: docling → 구조화 (헤딩/표/이미지 분리)
- DOCX/PPTX: python-docx/python-pptx
- CSV/Excel: pandas

#### 4. Vision API 통합
- Primary: Claude Vision (Anthropic)
- Secondary: GPT-4V (OpenAI) -- 비용 최적화 시
- Routing: 이미지 복잡도에 따라 자동 선택
  - 간단한 텍스트 이미지 → OCR only
  - 복잡한 차트/다이어그램 → Vision API
  - 사진/장면 → CLIP + Vision API

---

## I-13: Multimodal Renderer (멀티모달 렌더러)

### 현재 Part2 내용 (L1707~1709)
```
I-13 Multimodal Renderer: 다중 출력 포맷 (텍스트, 이미지, 오디오)
```

### 필요한 상세내용

#### 1. 렌더러 인터페이스
```python
class BaseRenderer(ABC):
    @abstractmethod
    async def render(self, content: RenderContent) -> RenderedOutput: ...

    @abstractmethod
    def supported_formats(self) -> list[str]: ...

    @abstractmethod
    def estimate_render_time(self, content: RenderContent) -> float: ...
```

#### 2. 포맷별 렌더러

| 렌더러 | 출력 포맷 | 도구 | 버전 |
|--------|---------|------|------|
| TextRenderer | Markdown, Plain, HTML | CommonMark | V1 |
| ChartRenderer | SVG, PNG, Interactive HTML | Plotly / D3.js | V1 |
| CodeRenderer | Syntax-highlighted code | Prism.js / Shiki | V1 |
| TableRenderer | Markdown table, CSV, Excel | pandas → format | V1 |
| DiagramRenderer | Mermaid, PlantUML | mermaid-js | V2 |
| AudioRenderer | MP3, WAV | TTS 엔진 | V3 |
| ImageRenderer | PNG, SVG | DALL-E / Stable Diffusion | V3 |

#### 3. 복합 출력 구성
```
RenderPlan (I-5 Decision Engine에서 결정)
  ↓
[렌더 순서 결정] 의존성 기반 DAG
  ↓
[병렬 렌더링] 독립 렌더러 병렬 실행
  ↓
[레이아웃 합성] 순서 + 배치 결정
  ↓
[품질 검증] 렌더링 결과 무결성 체크
  ↓
RenderedOutput → UI (I-20 OutputComposer → Frontend)
```

#### 4. 출력 품질 검증
- 차트: 데이터 포인트 수 일치 검증
- 코드: 구문 유효성 검증
- 표: 행/열 수 일치 검증
- 이미지: 해상도/포맷 검증

---

## I-14: Summarizer (요약기)

### 현재 Part2 내용 (L1711~1713)
```
I-14 Summarizer: 대화 요약, 메모리 증류 (L0→L1 승격 판단 지원)
```

### 필요한 상세내용

#### 1. 입출력 스키마
- **Input**: `SummarizeRequest`
  - `content: list[Message]` -- 요약 대상 (대화/문서)
  - `summary_type: Literal["conversation", "document", "memory_distill"]`
  - `max_length: int` -- 요약 최대 길이 (토큰)
  - `preserve_entities: bool` -- 핵심 엔티티 보존 여부
- **Output**: `SummaryResult`
  - `summary: str` -- 요약 텍스트
  - `key_entities: list[Entity]` -- 추출된 핵심 엔티티
  - `key_decisions: list[str]` -- 핵심 결정사항
  - `memory_candidates: list[MemoryCandidate]` -- L1 승격 후보
  - `compression_ratio: float` -- 압축률

#### 2. 요약 알고리즘

##### 대화 요약 (Conversation Summary)
```
1. 턴별 핵심 추출: 각 대화 턴에서 의도/결과 추출
2. 엔티티 체인 구성: 대화 전체에서 엔티티 등장 체인
3. 결정 포인트 식별: 사용자 결정/승인/거부 지점
4. 계층적 요약:
   - L1 (1문장): 대화 주제 + 결론
   - L2 (1단락): 주요 논의 + 결정사항
   - L3 (상세): 턴별 핵심 + 컨텍스트
```

##### 메모리 증류 (Memory Distillation)
```
L0 (세션 메모리) → 요약 → L1 승격 후보 생성
  ↓
[승격 판단 기준]
  - 사용자 명시적 요청 ("기억해줘")
  - 반복 참조 (3회 이상 언급)
  - 결정/선호 표현 ("나는 ~를 선호해")
  - 프로젝트 컨텍스트 (파일 경로, 설정값 등)
  ↓
[증류 규칙]
  - 구체적 사실만 보존 (추측/임시 정보 제외)
  - 날짜/시간 절대값 변환
  - 중복 제거 (기존 L1 메모리와 비교)
```

#### 3. 트리거 조건
- **자동 트리거**:
  - 세션 종료 시 (L0→L1 증류)
  - 대화 20턴 초과 시 (중간 요약)
  - 컨텍스트 윈도우 80% 도달 시 (압축 요약)
- **수동 트리거**:
  - 사용자 "요약해줘" 명령
  - I-5 Decision Engine 요청

---

## I-16: Knowledge Search Engine (지식 검색 엔진)

### 현재 Part2 내용 (L1715~1717)
```
I-16 Knowledge Search Engine: 지식 검색: I-2 RAG와 통합, 외부 지식 소스 검색
```

### 필요한 상세내용

#### 1. 검색 API 설계
```python
class KnowledgeSearchEngine:
    async def search(self, query: SearchQuery) -> SearchResults:
        """통합 검색 API"""

    async def search_internal(self, query: str) -> list[Document]:
        """I-2 RAG 파이프라인 검색"""

    async def search_external(self, query: str, sources: list[str]) -> list[Document]:
        """외부 지식 소스 검색"""

    async def hybrid_search(self, query: str) -> list[Document]:
        """내부 + 외부 하이브리드 검색"""
```

#### 2. 검색 파이프라인
```
검색 쿼리
  ↓
[쿼리 확장] 동의어, 한영 번역, 약어 확장
  ↓
[병렬 검색]
  ├── I-2 RAG (벡터 + BM25 하이브리드)
  ├── Knowledge Graph (Neo4j Cypher)
  └── External Sources (Web, API)
  ↓
[결과 병합] RRF (Reciprocal Rank Fusion)
  ↓
[Reranking] BGE-reranker / cross-encoder
  ↓
[필터링] 신선도, 신뢰도, 관련성 필터
  ↓
SearchResults (top-k)
```

#### 3. I-2 RAG 통합 상세
- 벡터 검색: ChromaDB + BGE-M3 (768차원)
- BM25 검색: Whoosh (로컬) / Elasticsearch (V2+)
- Hybrid 가중치: α=0.7 (벡터) + β=0.3 (BM25) -- LOCK
- Reranking: top-20 → rerank → top-5

#### 4. 외부 지식 소스
| 소스 | 검색 방법 | 신뢰도 | 버전 |
|------|---------|--------|------|
| Web (E-2) | Tavily/Serper API | 0.6~0.8 | V1 |
| Wikipedia | MediaWiki API | 0.8 | V1 |
| arXiv | arXiv API | 0.9 | V2 |
| 금융 데이터 | Yahoo Finance / KRX | 0.9 | V1 (P1) |
| 뉴스 | RT-BNP Pipeline | Tier별 | V2 |

#### 5. 랭킹 알고리즘
```
최종 점수 = w1 * relevance + w2 * freshness + w3 * reliability + w4 * source_tier

w1 = 0.4 (관련성)
w2 = 0.2 (신선도: 최근 데이터 가중)
w3 = 0.2 (신뢰도: 소스별 tier)
w4 = 0.2 (소스 등급)
```

---

## S-1: Self-check Engine (자가점검 엔진)

### 현재 Part2 내용 (L2600~2602)
```
S-1 Self-check Engine: I-6 출력 수집 → QoD 점수 기반 시스템 상태 평가 → 이상 감지 시 I-25(SDAR) 트리거
```

### 필요한 상세내용

#### 1. QoD (Quality of Decision) 점수 체계
| 메트릭 | 가중치 | 측정 방법 | 임계값 |
|--------|--------|---------|--------|
| accuracy | 0.3 | C-1~C-3 검증 통과율 | < 0.7 → 경고 |
| latency | 0.2 | 응답 시간 p95 | > 5s → 경고 |
| hallucination_rate | 0.25 | 환각 감지 비율 | > 0.1 → 위험 |
| user_satisfaction | 0.15 | 명시적/암시적 피드백 | < 0.6 → 경고 |
| cost_efficiency | 0.1 | 토큰당 품질 비율 | < 임계값 → 경고 |

```
QoD = Σ(weight_i × metric_i)  // 0.0 ~ 1.0
```

#### 2. 평가 윈도우
- **실시간**: 최근 1시간 슬라이딩 윈도우
- **일간**: 24시간 집계
- **주간**: 7일 트렌드 분석

#### 3. 이상 감지 기준
```
Level 1 (INFO): QoD < 0.8 지속 30분 → 로그 기록
Level 2 (WARNING): QoD < 0.6 지속 15분 → 알림 발송
Level 3 (ALERT): QoD < 0.4 즉시 → SDAR AR-L1 트리거
Level 4 (CRITICAL): QoD < 0.2 즉시 → SDAR AR-L3 트리거 + 운영자 알림
```

#### 4. SDAR 트리거 조건
| 조건 | SDAR 레벨 | 설명 |
|------|----------|------|
| QoD < 0.4 연속 3회 | AR-L1 (진단) | 자동 진단 실행 |
| hallucination_rate > 0.2 | AR-L2 (수리) | 프롬프트/캐시 수리 |
| latency p99 > 10s 연속 5분 | AR-L2 (수리) | 모델 라우팅 조정 |
| QoD < 0.2 | AR-L3 (긴급) | 서비스 격리 + 사용자 알림 |
| 보안 이벤트 감지 | AR-L4 (최대) | Emergency Kill Switch |

#### 5. 모니터링 메트릭 (Prometheus 노출)
```
vamos_qod_score{window="1h"} gauge
vamos_hallucination_rate{window="1h"} gauge
vamos_response_latency_seconds{quantile="0.95"} summary
vamos_sdar_trigger_total{level="L1|L2|L3|L4"} counter
vamos_selfcheck_evaluation_total counter
```

---

## 공통 SOT 참조
- `D2.0-01` Section 5.6 (모듈 카탈로그)
- `D2.0-02` Section 7 (ORANGE CORE 모듈 상세)
- `D2.0-06` Section 1~4 (Storage/Memory -- I-14, I-16 관련)
- `VAMOS_SDAR_DESIGN_SPECIFICATION.md` (S-1 → I-25 연동)
