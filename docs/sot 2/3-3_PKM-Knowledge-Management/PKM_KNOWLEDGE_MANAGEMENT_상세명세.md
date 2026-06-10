# PKM_KNOWLEDGE_MANAGEMENT 상세명세

> **Tier**: 3 (Feature Domains) | **Part2 Status**: SHELL (CAT-B catalog only) | **SOT**: STEP7-M (78 items)
> **Version**: 1.0.0 | **최종수정**: 2026-03-22
> **교차참조**: T2-CORE_AI → LLM 추출, T2-DATA_PIPELINE → 인제스트, T3-Multimodal → 멀티모달 캡처

---

## 1. 개요

VAMOS PKM(Personal Knowledge Management) 모듈은 사용자의 지식을 체계적으로
캡처 → 구조화 → 연결 → 복습하는 전체 라이프사이클을 관리한다. Zettelkasten 원칙에
기반한 원자적 노트 시스템과 지식 그래프 운영을 핵심으로 한다.

### 1.1 핵심 원칙

1. **원자성 (Atomicity)**: 하나의 노트는 하나의 개념만 담는다
2. **연결성 (Connectivity)**: 모든 노트는 최소 1개 이상의 링크를 가진다
3. **자동화 (Automation)**: AI 기반 자동 태깅, 관계 추론, 중복 감지
4. **신선도 (Freshness)**: 오래된 지식의 자동 만료 및 갱신 알림

---

## 2. 지식 캡처 파이프라인

### 2.1 캡처 소스 및 흐름

```
[웹 클리핑] ─────→ [AI 요약 + 핵심추출] ──┐
[문서 인제스트] ──→ [청킹 + 임베딩] ────────┤
[스크린 캡처] ───→ [OCR + 지식화] ──────────┤→ [원자적 노트 생성]
[대화 내 지식] ──→ [자동 추출] ─────────────┤       ↓
[수동 메모] ─────→ [메타데이터 태깅] ────────┘  [지식 그래프 삽입]
                                                    ↓
                                              [중복 감지 + 병합]
                                                    ↓
                                              [간격 반복 큐 등록]
```

### 2.2 웹 클리핑 + AI 요약

```python
# web_clipper.py
class WebClipper:
    """브라우저 확장 → API → 지식 노트 변환"""

    async def clip(self, request: ClipRequest) -> list[KnowledgeNote]:
        # 1. URL에서 본문 추출 (Readability.js 알고리즘)
        article = await self._extract_article(request.url)

        # 2. AI 요약 (3단계)
        summary = await self._summarize(article, levels=[
            "one_line",      # 1줄 요약
            "paragraph",     # 1문단 요약
            "structured",    # 구조화된 요약 (핵심개념, 주장, 근거)
        ])

        # 3. 자동 태깅
        tags = await self._auto_tag(article.text, summary)

        # 4. 원자적 노트 분해 (긴 글 → 복수 노트)
        notes = await self._atomize(article, summary)

        return notes

class ClipRequest:
    url: str
    selection_text: Optional[str]    # 선택 영역만 클리핑
    clip_mode: "full" | "selection" | "screenshot"
    tags_hint: list[str]             # 사용자 지정 태그 힌트
```

### 2.3 문서 인제스트

```python
# document_ingest.py
SUPPORTED_FORMATS = {
    "pdf": {"parser": "PyMuPDF", "ocr_fallback": True},
    "docx": {"parser": "python-docx"},
    "pptx": {"parser": "python-pptx", "slide_to_note": True},
    "epub": {"parser": "ebooklib"},
    "md": {"parser": "markdown-it"},
    "html": {"parser": "beautifulsoup4"},
    "txt": {"parser": "plain"},
    "csv/xlsx": {"parser": "pandas", "table_to_knowledge": True},
}

class DocumentIngestConfig:
    chunk_strategy: "semantic" | "fixed" | "paragraph" = "semantic"
    chunk_size: int = 512              # 토큰 기준
    chunk_overlap: int = 50
    extract_images: bool = True
    generate_summary: bool = True
    auto_link: bool = True             # 기존 노트와 자동 링크
```

### 2.4 스크린 캡처 지식화

```python
# screen_capture_knowledge.py
class ScreenCaptureKnowledger:
    """스크린 캡처 → OCR → 구조화 → 지식 노트"""

    async def process(self, screenshot: bytes) -> list[KnowledgeNote]:
        # 1. OCR 처리 (→ T3-Multimodal OCR 파이프라인 위임)
        ocr_result = await self.ocr_processor.process(screenshot)

        # 2. 컨텍스트 인식 (어떤 앱/웹사이트에서 캡처했는지)
        context = await self._detect_context(screenshot, ocr_result)

        # 3. 지식 구조화
        knowledge = await self._structurize(ocr_result.text, context)

        # 4. 원자적 노트 생성
        return self._create_notes(knowledge, source_image=screenshot)
```

---

## 3. 대화 지식 추출

### 3.1 자동 추출 파이프라인

```python
# conversation_knowledge_extractor.py
class ConversationKnowledgeExtractor:
    """대화 중 발생하는 지식을 자동으로 감지하고 추출"""

    EXTRACTION_TRIGGERS = [
        "factual_statement",      # 사실 진술 ("파이썬 3.12에서 GIL 제거됨")
        "decision_made",          # 의사결정 ("Redis 대신 Valkey 사용하기로")
        "problem_solved",         # 문제 해결 ("OOM 에러는 배치 크기 줄여서 해결")
        "concept_explained",      # 개념 설명
        "code_pattern",           # 코드 패턴 / 스니펫
        "url_shared",             # URL 공유
        "preference_expressed",   # 선호도 표현
    ]

    async def extract(self, message: Message) -> list[KnowledgeCandidate]:
        """
        1. LLM 기반 지식 후보 추출
        2. 신뢰도 점수 산정
        3. 중복 검사
        4. 사용자 확인 (신뢰도 < 0.8일 때)
        """
        candidates = await self._llm_extract(message)
        for c in candidates:
            c.duplicate_score = await self._check_duplicate(c)
            if c.confidence >= 0.8 and c.duplicate_score < 0.7:
                await self._auto_save(c)
            else:
                await self._queue_for_review(c)
        return candidates
```

### 3.2 메타데이터 태깅 스키마

```typescript
// knowledge_metadata.ts
interface KnowledgeMetadata {
  // 자동 생성
  auto_tags: string[];               // AI가 추출한 태그
  category: KnowledgeCategory;       // "concept" | "fact" | "procedure" | "decision" | "reference"
  confidence: number;                // 추출 신뢰도
  source_type: SourceType;           // "conversation" | "web_clip" | "document" | "manual"
  source_ref: string;                // 원본 참조 (대화ID, URL 등)
  extracted_at: string;              // ISO 8601
  language: string;                  // "ko" | "en"

  // 사용자 편집 가능
  user_tags: string[];
  importance: 1 | 2 | 3 | 4 | 5;    // 중요도
  domain: string;                    // "programming", "finance", "health" 등
  privacy_level: "public" | "private" | "sensitive";
}

type KnowledgeCategory =
  | "concept"       // 개념 정의
  | "fact"          // 사실/데이터
  | "procedure"     // 절차/방법
  | "decision"      // 의사결정 기록
  | "reference"     // 참조 자료
  | "opinion"       // 의견/관점
  | "code_snippet"  // 코드 조각
  | "bookmark";     // 북마크/링크
```

### 3.3 중복 감지

```python
# duplicate_detector.py
class DuplicateDetector:
    """다단계 중복 감지: 정확 → 유사 → 의미적"""

    async def check(self, note: KnowledgeNote) -> DuplicateResult:
        # Stage 1: 정확 매칭 (해시)
        exact = await self._exact_match(note.content_hash)
        if exact:
            return DuplicateResult(type="exact", score=1.0, existing=exact)

        # Stage 2: 유사 매칭 (MinHash LSH, Jaccard ≥ 0.7)
        near = await self._near_duplicate(note.minhash_signature)
        if near and near.jaccard >= 0.7:
            return DuplicateResult(type="near", score=near.jaccard, existing=near.note)

        # Stage 3: 의미적 매칭 (벡터 유사도 ≥ 0.85)
        semantic = await self._semantic_match(note.embedding)
        if semantic and semantic.similarity >= 0.85:
            return DuplicateResult(type="semantic", score=semantic.similarity, existing=semantic.note)

        return DuplicateResult(type="none", score=0.0)
```

---

## 4. 지식 그래프 운영 (Neo4j)

### 4.1 그래프 스키마

```cypher
// 노드 타입
(:KnowledgeNote {
  id: String,              // UUID
  title: String,
  content: String,
  category: String,        // concept, fact, procedure...
  created_at: DateTime,
  updated_at: DateTime,
  freshness_score: Float,  // 0.0 ~ 1.0
  review_count: Integer,
  importance: Integer       // 1~5
})

(:Tag { name: String, category: String })
(:Domain { name: String, parent: String })
(:Source { type: String, ref: String, captured_at: DateTime })
(:Person { name: String })  // 관련 인물

// 엣지 타입
(:KnowledgeNote)-[:RELATED_TO { weight: Float, type: String }]->(:KnowledgeNote)
(:KnowledgeNote)-[:TAGGED_WITH]->(:Tag)
(:KnowledgeNote)-[:BELONGS_TO]->(:Domain)
(:KnowledgeNote)-[:SOURCED_FROM]->(:Source)
(:KnowledgeNote)-[:CONTRADICTS { detected_at: DateTime }]->(:KnowledgeNote)
(:KnowledgeNote)-[:SUPERSEDES]->(:KnowledgeNote)    // 최신 버전
(:KnowledgeNote)-[:SUPPORTS]->(:KnowledgeNote)      // 근거 관계
(:KnowledgeNote)-[:MENTIONS]->(:Person)
```

### 4.2 자주 사용하는 쿼리 패턴

```cypher
// 1. 특정 노트의 연결된 지식 네트워크 (2-hop)
MATCH (n:KnowledgeNote {id: $noteId})-[r*1..2]-(connected)
RETURN n, r, connected
LIMIT 50;

// 2. 도메인별 핵심 지식 (PageRank 상위)
CALL gds.pageRank.stream('knowledge-graph')
YIELD nodeId, score
WITH gds.util.asNode(nodeId) AS note, score
WHERE note.domain = $domain
RETURN note.title, score
ORDER BY score DESC
LIMIT 20;

// 3. 충돌 감지된 노트 쌍
MATCH (a:KnowledgeNote)-[:CONTRADICTS]->(b:KnowledgeNote)
WHERE a.freshness_score > 0.5 AND b.freshness_score > 0.5
RETURN a, b;

// 4. 고립 노트 (연결 없는 노트) 감지
MATCH (n:KnowledgeNote)
WHERE NOT (n)-[:RELATED_TO]-() AND NOT (n)-[:SUPPORTS]-()
RETURN n ORDER BY n.created_at DESC;
```

### 4.3 자동 관계 추론

```python
# auto_relation_inference.py
class AutoRelationInferrer:
    """새 노트 삽입 시 기존 노트와의 관계를 자동 추론"""

    RELATION_TYPES = {
        "RELATED_TO":   {"threshold": 0.75, "method": "embedding_similarity"},
        "SUPPORTS":     {"threshold": 0.80, "method": "llm_classification"},
        "CONTRADICTS":  {"threshold": 0.80, "method": "llm_classification"},
        "SUPERSEDES":   {"threshold": 0.90, "method": "temporal_similarity"},
    }

    async def infer(self, new_note: KnowledgeNote) -> list[InferredRelation]:
        # 1. 벡터 유사도로 후보 검색 (top-K)
        candidates = await self.vector_search(new_note.embedding, top_k=20)

        # 2. LLM 분류: 관계 유형 결정
        relations = []
        for candidate in candidates:
            rel_type = await self._classify_relation(new_note, candidate)
            if rel_type and rel_type.confidence >= self.RELATION_TYPES[rel_type.type]["threshold"]:
                relations.append(rel_type)

        # 3. Neo4j에 관계 생성
        await self._create_relations(new_note.id, relations)
        return relations
```

---

## 5. 간격 반복 시스템 (SM-2)

### 5.1 SM-2 알고리즘 구현

```python
# sm2_algorithm.py
class SM2Algorithm:
    """SuperMemo 2 알고리즘 — 간격 반복 스케줄링"""

    DEFAULT_EASINESS = 2.5
    MIN_EASINESS = 1.3

    def calculate_next_review(self, card: FlashCard, quality: int) -> ReviewSchedule:
        """
        quality: 0~5 (0=완전 모름, 5=완벽 기억)

        알고리즘:
        1. EF' = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))
        2. EF = max(1.3, EF')
        3. 간격 계산:
           - n=1: 1일
           - n=2: 6일
           - n≥3: I(n) = I(n-1) * EF
        4. quality < 3이면 반복 횟수 리셋
        """
        ef = card.easiness_factor
        ef_prime = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_ef = max(self.MIN_EASINESS, ef_prime)

        if quality < 3:
            new_repetition = 0
            new_interval = 1
        else:
            new_repetition = card.repetition + 1
            if new_repetition == 1:
                new_interval = 1
            elif new_repetition == 2:
                new_interval = 6
            else:
                new_interval = round(card.interval * new_ef)

        return ReviewSchedule(
            next_review=datetime.now() + timedelta(days=new_interval),
            interval_days=new_interval,
            easiness_factor=new_ef,
            repetition=new_repetition,
        )
```

### 5.2 플래시카드 스키마

```typescript
interface FlashCard {
  id: string;
  knowledge_note_id: string;      // 원본 노트 참조
  front: string;                  // 질문 / 프롬프트
  back: string;                   // 답변 / 설명
  card_type: "basic" | "cloze" | "reversible" | "code";
  // SM-2 상태
  easiness_factor: number;        // default 2.5
  interval: number;               // 일 단위
  repetition: number;             // 반복 횟수
  next_review: string;            // ISO 8601
  // 통계
  total_reviews: number;
  correct_count: number;
  streak: number;
  created_at: string;
  last_reviewed_at: string;
}
```

---

## 6. 지식 신선도 및 충돌 관리

### 6.1 자동 만료 정책

```python
# freshness_manager.py
FRESHNESS_POLICIES = {
    "reference": {
        "half_life_days": 365,       # 1년 (문서 링크/API 레퍼런스)
        "min_freshness": 0.2,
    },
    "opinion": {
        "half_life_days": 180,       # 6개월 (의견은 맥락 변화에 민감)
        "min_freshness": 0.1,
    },
    "code_snippet": {
        "half_life_days": 120,       # 4개월 (의존성 변화에 민감)
        "min_freshness": 0.1,
    },
    "bookmark": {
        "half_life_days": 180,       # 6개월 (북마크/즐겨찾기)
        "min_freshness": 0.1,
    },
    "fact": {
        "half_life_days": 365,       # 1년 후 50% 감소
        "min_freshness": 0.2,
    },
    "procedure": {
        "half_life_days": 270,
        "min_freshness": 0.15,
    },
    "concept": {
        "half_life_days": 730,       # 2년 (개념은 느리게 노후화)
        "min_freshness": 0.3,
    },
    "decision": {
        "half_life_days": 90,        # 의사결정은 빨리 노후화
        "min_freshness": 0.1,
    },
}

def calculate_freshness(note: KnowledgeNote) -> float:
    """지수 감쇠 모델: freshness = exp(-lambda * age_days)"""
    policy = FRESHNESS_POLICIES.get(note.category, FRESHNESS_POLICIES["fact"])
    lambda_val = math.log(2) / policy["half_life_days"]
    age_days = (datetime.now(timezone.utc) - note.updated_at).days
    freshness = math.exp(-lambda_val * age_days)
    return max(policy["min_freshness"], freshness)
```

### 6.2 충돌 감지 및 해결 프로토콜

```python
# conflict_resolver.py
class ConflictDetector:
    """지식 간 모순/충돌 자동 감지"""

    async def detect_conflicts(self, note: KnowledgeNote) -> list[Conflict]:
        # 1. 유사 노트 검색
        similar = await self.vector_search(note.embedding, threshold=0.8)

        # 2. LLM 기반 충돌 판별
        conflicts = []
        for s in similar:
            result = await self._llm_check_conflict(note, s)
            if result.is_conflict:
                conflicts.append(Conflict(
                    note_a=note.id,
                    note_b=s.id,
                    conflict_type=result.type,  # "contradiction" | "outdated" | "partial"
                    description=result.description,
                    suggested_resolution=result.resolution,
                ))
        return conflicts

RESOLUTION_PROTOCOLS = {
    "contradiction": [
        "1. 두 노트의 출처 신뢰도 비교",
        "2. 최신 노트 우선 (temporal precedence)",
        "3. 사용자에게 선택 요청",
        "4. 해결된 노트에 SUPERSEDES 관계 생성",
    ],
    "outdated": [
        "1. 신선도 점수 비교",
        "2. 최신 노트로 자동 대체 제안",
        "3. 구 노트에 '아카이브' 태그",
    ],
    "partial": [
        "1. 양쪽 노트의 유효 부분 식별",
        "2. 병합 노트 초안 생성 (AI)",
        "3. 사용자 검토 후 병합",
    ],
}
```

---

## 7. 외부 도구 통합

### 7.1 Notion 양방향 동기화

```python
# notion_sync.py
class NotionSync:
    AUTH_METHOD = "OAuth 2.0"
    SCOPES = ["read_content", "update_content", "insert_content"]

    SYNC_CONFIG = {
        "sync_interval_min": 15,
        "conflict_strategy": "last_write_wins",  # or "manual_merge"
        "field_mapping": {
            "notion_title": "note.title",
            "notion_content": "note.content",
            "notion_tags": "note.metadata.auto_tags",
            "notion_created": "note.created_at",
        },
        "sync_direction": "bidirectional",     # "to_notion" | "from_notion" | "bidirectional"
        "excluded_databases": [],
        # 프라이버시 가드: private/sensitive 노트는 외부 Notion 동기화에서 제외 (schema privacy_level)
        "excluded_privacy_levels": ["private", "sensitive"],
    }
```

### 7.2 Obsidian 통합

```python
# obsidian_sync.py
class ObsidianSync:
    """Obsidian 볼트와 양방향 동기화 (파일 기반)"""

    SYNC_CONFIG = {
        "vault_path": "~/Obsidian/VAMOS-Knowledge",
        "sync_method": "file_watch",           # inotify / FSEvents
        "format": "markdown",
        "frontmatter_mapping": {
            "tags": "metadata.auto_tags",
            "category": "metadata.category",
            "importance": "metadata.importance",
            "vamos_id": "id",
        },
        "link_format": "[[wikilink]]",         # or "[markdown](link)"
        "image_handling": "embed",             # "embed" | "link" | "copy"
    }
```

---

## 8. Zettelkasten 구현

### 8.1 원자적 노트 구조

```typescript
interface ZettelNote {
  id: string;                        // Luhmann-style ID: "21a3b"
  uuid: string;                      // 시스템 내부 UUID
  title: string;                     // 한 줄 제목
  content: string;                   // 마크다운, 최대 300단어 권장
  note_type: "permanent" | "literature" | "fleeting" | "index" | "structure";
  links: ZettelLink[];               // 다른 노트 링크
  backlinks: string[];               // 역참조 (자동 계산)
  sequences: string[];               // 시퀀스 소속 (21a → 21a1, 21a2...)
  tags: string[];
  source_ref?: string;               // 문헌 노트의 경우 원본 참조
  created_at: string;
  modified_at: string;
}

interface ZettelLink {
  target_id: string;
  link_type: "related" | "supports" | "contradicts" | "continues" | "branches";
  context: string;                   // 링크 이유 설명 (1줄)
}
```

### 8.2 링크 네트워크 시각화

```python
# zettel_visualizer.py
class ZettelNetworkVisualizer:
    """D3.js force-directed graph로 지식 네트워크 시각화"""

    def generate_graph_data(self, center_note_id: str, depth: int = 3) -> GraphData:
        """
        중심 노트에서 depth-hop까지의 네트워크를 D3.js 데이터로 변환
        노드 크기: 연결 수 비례
        엣지 색상: link_type별 구분
        클러스터: 도메인/태그 기반 색상 그룹
        """
        return GraphData(
            nodes=[{"id": n.id, "title": n.title, "size": len(n.links), "group": n.domain} for n in nodes],
            edges=[{"source": e.from_id, "target": e.to_id, "type": e.link_type} for e in edges],
        )
```

---

## 9. 교차참조

| 참조 모듈 | 연관 항목 | 참조 방향 |
|----------|---------|----------|
| T2-CORE_AI (2-2) | LLM 기반 추출/요약/관계추론 | ← 사용 |
| T2-DATA_PIPELINE (2-3) | 문서 인제스트, 벡터 검색 | ← 사용 |
| T3-Multimodal (3-2) | OCR, 스크린캡처 처리 | ← 사용 |
| T3-Education (3-5) | SM-2 간격 반복 공유 | ↔ 공유 |
| T4-Frontend (4-1) | 지식 그래프 시각화, 플래시카드 UI | → 제공 |

---

*끝 — PKM_KNOWLEDGE_MANAGEMENT 상세명세 v1.0.0*
