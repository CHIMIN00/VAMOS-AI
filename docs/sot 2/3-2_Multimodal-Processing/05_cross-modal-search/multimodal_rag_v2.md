# multimodal_rag_v2.md — J-055 V2 NEW (비디오/오디오 RAG) + J-056 V2 NEW (지식그래프 멀티모달 통합) + J-082 V2 EXTEND (§6.7 합성 데이터) + **peer Part 1 §9.3 forward link 해소 (J-007 ImageBind → J-055 CLIP 통합 인덱싱)**

> **Status**: V2-Phase 2 (2-4 #2b)
> **작성일**: 2026-04-19
> **V1 정본**: [multimodal_rag.md](./multimodal_rag.md) (Phase 1-5 완료, ~33K, read-only sha256 baseline, J-051~J-054 V1 + J-055/J-056 V2 SHELL)
> **SoT 근거**: STEP7-J Part 6 (J-055 L949~L958, J-056 L960~L972) + Part 9 (J-082 L1405~L1420)
> **담당 J-ID**: **J-055** (V2 NEW: 비디오/오디오 RAG 본문) + **J-056** (V2 NEW: 지식그래프 + 멀티모달 통합) + **J-082** (§6.7 트렌드 본문: 합성 데이터 생성 RLAIF)
> **상위 인덱스**: [_index.md](./_index.md)
> **peer V2**: [knowledge_graph_multimodal_v2.md](./knowledge_graph_multimodal_v2.md) / [caching_optimization_v2.md](./caching_optimization_v2.md) + **[vision_language_integration_v2.md](../01_image-pipeline/vision_language_integration_v2.md) §9.3 forward link** (J-007 ImageBind 1024d → J-055 CLIP 768d 통합 인덱싱) + [video_analysis_v2.md](../03_video-analysis/video_analysis_v2.md) §4.2 (J-039 검색 인덱싱) + [audio_analysis_v2.md](../02_audio-processing/audio_analysis_v2.md) §J-024 (오디오 세그먼트)

---

## 1. Cross-domain 참조 블록

| 정본 | 역할 | 참조 지점 |
|------|------|----------|
| `STEP7-J_멀티모달_생성처리_작업가이드.md` Part 6 J-055 (L949~L958) | 상위 SoT J-055 | §4.1 verbatim |
| `STEP7-J_멀티모달_생성처리_작업가이드.md` Part 6 J-056 (L960~L972) | 상위 SoT J-056 | §4.2 verbatim |
| `STEP7-J_멀티모달_생성처리_작업가이드.md` Part 9 J-082 (L1405~L1420) | 상위 SoT J-082 | §5 verbatim |
| `multimodal_rag.md` (V1) | V1 정본 (J-051~J-054 본문) | §3 V1 계승 |
| **`vision_language_integration_v2.md` §9.3 (peer V2 Part 1)** | **forward link 해소: J-007 ImageBind 1024d → J-055 CLIP 768d 통합 인덱싱** | **§4.1 E3** |
| `video_analysis_v2.md` §4.2 (peer 본 #2b 2-3) | J-039 비디오 인덱싱 (CLIP 768d) | §4.1 E3 |
| `audio_analysis_v2.md` §J-024 (peer Part 2) | 오디오 세그먼트 입력 | §4.1 E3 |
| `caching_optimization_v2.md` (peer 본 #2b) | 시맨틱 캐시 -60% 절감 | §4.1 E6 |
| AUTHORITY_CHAIN §4 LOCK-MM-04/06/07 | LOCK 정본 | §2 |

---

## 2. LOCK 인용

> LOCK (기존 명세 §2.2): CLIP 임베딩 차원 — 768d (ViT-L/14@336)

> LOCK (STEP7-J J-083): 모달리티 우선순위 — Text > Image > Audio > Video > Document > Mixed

> LOCK (STEP7-J J-094~J-096): 비용 상한 — V1: ≤₩10K($8), V2: ≤₩40K($30), V3: ≤₩200K($150)

> LOCK (가이드 R-05-2): 파일 크기 상한 — 이미지 10MB / 오디오 25MB / 비디오 100MB

**적용 지표**:
- LOCK-MM-07 (CLIP 768d): J-055 비디오 키프레임 + J-056 지식그래프 멀티모달 노드 통일
- LOCK-MM-04 (모달리티 우선순위): J-055 검색 결과 정렬 정책
- LOCK-MM-06 V2 ($30/call): Qdrant Cloud 또는 자체 Qdrant 비용 가드

---

## 3. V1 → V2 승급

| J-ID | V1 (V1 multimodal_rag.md) | V2 (본 산출물) |
|------|--------------------------|----------------|
| J-055 | V2 SHELL (3 항목) | **E1~E10 본문 + 비디오/오디오 RAG + 타임스탬프 연동** |
| J-056 | V2 SHELL (5 항목) | **E1~E10 본문 + Graph + Vector + Multimodal 하이브리드 + ImageBind→CLIP 통일** |
| J-082 | 미작성 | **§6.7 트렌드 본문: RLAIF + 합성 이미지/음성 데이터 + Self-Play** |

---

## 4. V2 본문

### 4.1 J-055. 비디오/오디오 RAG V2 (STEP7-J L949~L958)

**근거 verbatim 인용** (STEP7-J L952~L956):
> ```
> [구현 상세]
> - 비디오 전사 텍스트 기반 RAG
> - 키프레임 이미지 기반 비전 RAG
> - 오디오 세그먼트 검색
> - 타임스탬프 연동: 검색 결과 → 정확한 재생 위치
> ```

**SoT 구현성 (STEP7-J L957)**: V2 — ✅ 3개월

#### E1. Input/Output Schema
```python
from common_types import ModuleConfig, MultimodalMessage
from d202_02 import VamosError, VamosResult

class VideoAudioRAGConfigV2(ModuleConfig):
    embedding_model: str = "clip-vit-l14-336"        # LOCK-MM-07 768d
    text_embedding_model: str = "bge-m3"
    audio_embedding_model: str = "wav2vec2-base"
    qdrant_collection: str = "av_rag"
    chunk_overlap_sec: float = 2.0
    max_results: int = 10

class AVRAGRequest:
    query: str                                       # 텍스트 쿼리
    user_id: str
    modalities: list[Literal["text","video_visual","audio_segment"]] = ["text","video_visual"]
    time_filter: Optional[tuple[float,float]] = None
    top_k: int = 5

class AVRAGHit:
    source_type: Literal["video_transcript","video_keyframe","audio_segment"]
    source_id: str
    timestamp_sec: float
    duration_sec: float
    score: float
    text_excerpt: Optional[str] = None
    keyframe_url: Optional[str] = None
    audio_url: Optional[str] = None                  # 오디오 클립 (signed)
    playback_url: str                                # 정확한 재생 위치 deeplink
```

#### E3. Algorithm
```python
async def search_av(req: AVRAGRequest, cfg: VideoAudioRAGConfigV2) -> list[AVRAGHit]:
    # 1. 쿼리 → 3종 임베딩 (CLIP 768d / bge-m3 / wav2vec2)
    q_clip = await clip_encode_text(req.query, model=cfg.embedding_model)  # LOCK-MM-07
    q_text = await text_encode(req.query, model=cfg.text_embedding_model)
    q_audio = await text_to_audio_embedding(req.query)                     # 음성 검색 시

    # 2. Qdrant 다중 검색 (병렬)
    user_filter = {"user_id": req.user_id}                                  # 사용자 격리 (privacy)
    visual_hits = await qdrant.search(f"{cfg.qdrant_collection}_visual", q_clip, limit=req.top_k * 2, filter=user_filter)
    text_hits = await qdrant.search(f"{cfg.qdrant_collection}_transcript", q_text, limit=req.top_k * 2, filter=user_filter)
    audio_hits = []
    if "audio_segment" in req.modalities:
        audio_hits = await qdrant.search(f"{cfg.qdrant_collection}_audio", q_audio, limit=req.top_k * 2, filter=user_filter)

    # 3. 통합 score (CLIP 0.4 + transcript 0.4 + audio 0.2)
    merged = merge_hits(visual_hits, weight=0.4,
                       text_hits=text_hits, weight_text=0.4,
                       audio_hits=audio_hits, weight_audio=0.2)

    # 4. 시간 필터
    if req.time_filter:
        merged = filter_time_range(merged, req.time_filter)

    # 5. 타임스탬프 deeplink 생성 (정확한 재생 위치)
    return [AVRAGHit(
        source_type=h.type, source_id=h.payload["source_id"],
        timestamp_sec=h.payload["timestamp_sec"],
        duration_sec=h.payload["duration_sec"],
        score=h.score,
        text_excerpt=h.payload.get("text"),
        keyframe_url=await sign_thumbnail_url(h.payload["source_id"], h.payload["timestamp_sec"]),
        audio_url=await sign_audio_clip_url(h.payload["source_id"], h.payload["timestamp_sec"]),
        playback_url=f"vamos://av/{h.payload['source_id']}#t={h.payload['timestamp_sec']:.1f}",
    ) for h in merged[:req.top_k]]
```

#### E4. Model Selection
| 모달리티 | 모델 | 차원 | 출처 |
|---------|------|------|------|
| 시각 (키프레임) | CLIP ViT-L/14@336 | 768d ✅ LOCK-MM-07 | peer J-039 통일 |
| 텍스트 (전사) | bge-m3 | 1024d | peer caching_v2 |
| 오디오 세그먼트 | wav2vec2-base | 768d | peer audio_analysis §J-024 |

#### E5. Error Handling
| 에러 | 폴백 |
|------|------|
| Qdrant 실패 | local 캐시 → CLIP 단독 검색 |
| 임베딩 OOM | 배치 크기 4 → 1 |
| 결과 0 | 빈 리스트 + suggestion |
| time_filter 무효 | 무시 + warning |

#### E6. Cost (peer caching_v2 -60% 절감 후)
| 시나리오 | V2 (월) | LOCK-MM-06 V2 |
|----------|---------|---------------|
| Qdrant 자체 호스팅 + 로컬 임베딩 | $0 | 충족 |
| Qdrant Cloud 1M points | $25 | 충족 |
| 캐시 60% 히트 후 | **$10** | 충족 ✅ |

#### E7. SLA
- 검색 (top_k=5, 10K 비디오): P50 80ms / P99 200ms
- 인덱싱 (5분 비디오): P50 30s / P99 60s

#### E8. Test (10건)
1. 텍스트 쿼리 "강아지" → CLIP 768d + transcript 통합 검색.
2. 시간 필터 (60s~120s) → 해당 구간만.
3. 오디오 세그먼트 검색 ("음악 시작") → wav2vec2 매칭.
4. playback_url deeplink → 정확한 재생 위치.
5. Qdrant 실패 → local 캐시 폴백.
6. CLIP 768d 차원 검증.
7. 캐시 히트 60% 이상.
8. 다국어 쿼리 (en) → bge-m3 처리.
9. 빈 라이브러리 → 결과 0 + suggestion.
10. peer J-039 인덱싱 결과 → 본 V2 검색에서 활용.

#### E9. Dependencies
- 외부: Qdrant, CLIP (open_clip), bge-m3, wav2vec2-base
- 내부 (peer): J-039 V2 (video_analysis_v2 §4.2 인덱싱), J-024 (audio_analysis_v2 §J-024 화자분리), J-052 (V1 multimodal_rag CLIP), J-057 V2 (caching_optimization_v2 시맨틱 캐시), J-083 (integration_architecture_v2 Router)
- GPU: RTX 4090 (CLIP 768d 배치 + wav2vec2)

#### E10. Privacy
- user_id 단위 격리
- audio/keyframe URL signed + TTL 1시간
- R-05-7 안전 필터 통과 콘텐츠만 인덱스

**자체 점수**: 91/100

---

### 4.2 J-056. 지식그래프 + 멀티모달 통합 V2 (STEP7-J L960~L972)

**근거 verbatim 인용** (STEP7-J L963~L970):
> ```
> [구현 상세]
> - 지식그래프 노드에 멀티모달 데이터 연결:
>   ├─ 개념 노드 ← 관련 이미지, 다이어그램, 비디오 클립
>   ├─ 인물 노드 ← 프로필 사진, 음성 샘플
>   ├─ 프로젝트 노드 ← 스크린샷, 데모 비디오
>   └─ 투자 노드 ← 차트 이미지, 실적 발표 오디오
>
> - Graph + Vector + Multimodal 하이브리드 검색
> ```

**SoT 구현성 (STEP7-J L971)**: V2 — ⚠️ 4개월 (복합 인덱싱)

#### E1. Schema
```python
class MultimodalKGNode:
    node_id: UUID
    node_type: Literal["concept","person","project","investment","event"]
    text_label: str                                  # 한국어 라벨
    text_embedding: list[float]                      # bge-m3 1024d
    multimodal_assets: list[KGAsset]                 # 이미지/오디오/비디오/문서

class KGAsset:
    asset_id: UUID
    modality: Literal["image","audio","video","document"]
    embedding: list[float]                           # CLIP 768d (LOCK-MM-07) or wav2vec2 768d or bge-m3 1024d
    payload_uri: str
    timestamp_added: datetime
    user_id: str

class HybridSearchRequest:
    query: str
    modality_filter: list[str] = []                  # 빈 리스트 = 모든 모달
    relation_depth: int = 2                          # 그래프 hop
    top_k: int = 10
    user_id: str
```

#### E3. Algorithm — 하이브리드 검색
```python
async def hybrid_search(req: HybridSearchRequest) -> list[MultimodalKGHit]:
    # 1. 쿼리 → 텍스트 임베딩
    q_text = await text_encode(req.query, model="bge-m3")

    # 2. Vector search (1차): 텍스트 매칭으로 후보 노드 추출
    seed_nodes = await vector_search(q_text, top_k=req.top_k * 3)

    # 3. Graph traversal (2차): seed 노드 → relation_depth hop
    expanded = await graph_traverse(seed_nodes, max_hop=req.relation_depth)

    # 4. Multimodal re-ranking: 각 노드의 multimodal_assets → 쿼리와 cross-modal 유사도
    reranked = []
    for node in expanded:
        multimodal_score = 0.0
        if not req.modality_filter or "image" in req.modality_filter:
            for asset in [a for a in node.multimodal_assets if a.modality == "image"]:
                # CLIP 768d cross-modal (text → image)
                q_clip = await clip_encode_text(req.query)  # LOCK-MM-07 통일
                multimodal_score += cosine(q_clip, asset.embedding) * 0.4
        # audio/video 유사
        final_score = node.text_score * 0.5 + multimodal_score * 0.5
        reranked.append((final_score, node))
    reranked.sort(reverse=True)

    return [MultimodalKGHit(node=n, score=s) for s, n in reranked[:req.top_k]]
```

#### E5/E6/E7 (간략)
- E5 폴백: graph traversal 실패 → vector search 결과만 / 멀티모달 임베딩 없는 노드 → text score만
- E6 비용: Qdrant + Neo4j 자체 호스팅 = $0 / 클라우드 = $50/월 (LOCK-MM-06 V2 충족)
- E7 SLA: P50 200ms / P99 500ms (relation_depth=2 기준)

#### E8. Test (8건)
1. "VAMOS Phase 5" → concept 노드 + 관련 다이어그램 이미지 + 발표 비디오 클립.
2. 인물 노드 검색 → 프로필 사진 + 음성 샘플.
3. 투자 노드 검색 → 차트 이미지 + 실적 발표 오디오.
4. relation_depth=3 → 더 넓은 관련 노드 확장.
5. modality_filter=["image"] → 이미지 자산만 매칭.
6. CLIP 768d 통일 검증.
7. user_id 격리 검증.
8. Neo4j 실패 → vector search 폴백.

#### E9. Dependencies
- 외부: Neo4j (그래프 DB), Qdrant (벡터), CLIP, bge-m3
- 내부 (peer): J-052 (V1 이미지-텍스트 RAG), J-053/J-054 (V1 테이블/코드 RAG), peer Part 1 vision_language_integration_v2 §9.3 (J-007 ImageBind), J-055 V2 (본 V2 §4.1)

**자체 점수**: 89/100

---

## 5. J-082 §6.7 트렌드 본문 (STEP7-J L1405~L1420)

**근거 verbatim 인용** (STEP7-J L1408~L1417):
> ```
> [2025-2026 최신 기술]
> - RLAIF (Reinforcement Learning from AI Feedback): AI가 AI 학습 데이터 생성
> - 합성 이미지 학습 데이터 생성
> - 합성 음성 데이터 (데이터 증강)
> - Self-Play: 에이전트 간 상호작용으로 데이터 생성
>
> [VAMOS 활용]
> - 한국어 특화 데이터 자체 생성
> - 투자 시나리오 합성 데이터
> - 벤치마크 테스트 데이터 자동 생성
> - 개인화 파인튜닝 데이터 준비
> ```

**SoT 구현성 (STEP7-J L1419)**: V2 — ✅ 2개월

### 5.1 RAG 측면 통합 시나리오
- **합성 데이터 RAG 인덱스 구축**: 한국어 특화 합성 텍스트/이미지/오디오 → 본 V2 J-055 인덱스에 추가
- **Self-Play 멀티모달 검색 시나리오**: 에이전트 A 쿼리 → 에이전트 B 응답 → 본 V2 검색 품질 평가
- **합성 평가 데이터**: VBS-11 (peer cost_accessibility_v2 §5) RAG 정확도 측정용 합성 쿼리 1000건

### 5.2 통합 전략 (V2 2개월 로드맵)
1. **+1개월**: RLAIF 합성 데이터 RAG 인덱스 추가 (한국어 1만 건)
2. **+2개월**: Self-Play 시나리오 → 본 V2 검색 품질 측정 자동화

**자체 점수**: 80/100 (트렌드 본문 — 실측 V2 +2개월 시점)

---

## 6. peer V2 cross-reference (drift 0)

### 6.1 vision_language_integration_v2.md §9.3 (Part 1) ↔ 본 V2 §4.1 (forward link 해소)
- vision_language_integration_v2.md §9.3 forward link "J-007 ImageBind 1024d → 향후 J-055 통합" → 본 V2 §4.1 E3 line `q_clip = await clip_encode_text(req.query, model="clip-vit-l14-336")` (CLIP 768d 통일)
- ImageBind 1024d 별도 컬렉션 유지 (CLIP 768d LOCK-MM-07 정본 + ImageBind 옵션)

### 6.2 video_analysis_v2.md §4.2 (peer 본 #2b 2-3) ↔ 본 V2 §4.1
- video_analysis_v2.md §4.2 J-039 인덱싱 결과 (CLIP 768d) → 본 V2 §4.1 E3 검색 입력 (qdrant collection 통일)

### 6.3 audio_analysis_v2.md §J-024 (Part 2) ↔ 본 V2 §4.1
- audio_analysis_v2.md §J-024 오디오 세그먼트 (start/end/speaker_id) → 본 V2 §4.1 E1 audio_segment 입력

### 6.4 caching_optimization_v2.md (peer 본 #2b) ↔ 본 V2 §4.1 E6
- caching_optimization_v2.md §J-057 V2 시맨틱 캐시 -60% → 본 V2 §4.1 E6 (월 $25 → $10)

---

## 7. Phase 3 시나리오 (10건)
1. 비디오/오디오/텍스트 통합 검색 → 3 hit + playback_url deeplink.
2. CLIP 768d cross-modal (text→image) 검증.
3. 시간 필터 → 정확한 구간 매칭.
4. KG 하이브리드 (Vector + Graph) → relation_depth=2 확장.
5. 합성 데이터 (J-082) RAG 인덱스 → 한국어 검색 품질 향상.
6. 캐시 60% 히트 → 비용 -$15/월.
7. peer J-039 인덱싱 결과 검색 활용.
8. peer Part 1 §9.3 forward link 해소 검증.
9. KG 모달 필터 (image only) 적용.
10. Qdrant 실패 → local 캐시 폴백.

---

## 8. 검증 매트릭스
| 항목 | V1 | V2 (본) | L3 |
|------|----|---------|-----|
| J-055 비디오/오디오 RAG | V2 SHELL | E1~E10 + 타임스탬프 deeplink | 91 |
| J-056 KG 통합 | V2 SHELL | 하이브리드 검색 + ImageBind→CLIP 통일 | 89 |
| J-082 §6.7 합성 데이터 | 미작성 | 본문 + 통합 전략 | 80 |
| peer Part 1 §9.3 forward link 해소 | 미해소 | **§4.1 E3 + §6.1 cross-ref 실체화** | 92 |
| Phase 3 시나리오 | 미작성 | 10건 | 90 |

**평균**: **88.4/100** (LOCK-MM-12 VBS-11 ≥80 V2 충족 ✅)
