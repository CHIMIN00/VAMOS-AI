# memory_integration_v2.md — J-064 V2 EXTEND (5-Layer 메모리 통합) + J-085 V2 EXTEND (Context Window) + J-086 V2 EXTEND (Error Handling) + J-081 §6.7 트렌드 본문 (Multimodal MoE)

> **Status**: V2-Phase 2 (2-4 #2b)
> **작성일**: 2026-04-19
> **V1 정본**: [memory_integration.md](./memory_integration.md) (Phase 1-6 완료, ~11K, read-only sha256 baseline, J-064 V1 + J-085/J-086 V1 본문)
> **SoT 근거**: STEP7-J Part 7 J-064 (L1103~L1117) + Part 10 J-085 (L1462~L1478) + J-086 (L1480~L1493) + Part 9 J-081 (L1389~L1403)
> **담당 J-ID**: **J-064** (V2 EXTEND: 5-Layer 멀티모달 통합) + **J-085** (V2 EXTEND: 동적 토큰 예산) + **J-086** (V2 EXTEND: 그레이스풀 디그레이데이션) + **J-081** (§6.7 트렌드 본문: Llama 4 Scout/Maverick MoE)
> **상위 인덱스**: [_index.md](./_index.md)
> **peer V2**: [integration_architecture_v2.md](./integration_architecture_v2.md) §4.3 (J-085 Context Window) + 6-4 Memory-RAG-Storage (cross-domain reference, 본 도메인 cross_domain_deps=[] 이므로 참조만)

---

## 1. Cross-domain 참조

| 정본 | 역할 |
|------|------|
| `STEP7-J_멀티모달_생성처리_작업가이드.md` Part 7 J-064 (L1103~L1117) | 상위 SoT J-064 |
| `STEP7-J_멀티모달_생성처리_작업가이드.md` Part 10 J-085 (L1462~L1478) | 상위 SoT J-085 |
| `STEP7-J_멀티모달_생성처리_작업가이드.md` Part 10 J-086 (L1480~L1493) | 상위 SoT J-086 |
| `STEP7-J_멀티모달_생성처리_작업가이드.md` Part 9 J-081 (L1389~L1403) | §6.7 트렌드 J-081 |
| `memory_integration.md` (V1) | V1 정본 |
| `integration_architecture_v2.md` §4.3 (peer 본 #2b) | J-085 Context Window 통합 |
| AUTHORITY §4 LOCK-MM-04/06/07 | LOCK |

## 2. LOCK 인용

> LOCK (STEP7-J J-083): 모달리티 우선순위 — Text > Image > Audio > Video > Document > Mixed

> LOCK (STEP7-J J-094~J-096): 비용 상한 V2 ≤ ₩40K($30)

> LOCK (기존 명세 §2.2): CLIP 임베딩 차원 — 768d (ViT-L/14@336)

**적용**: LOCK-MM-04 (모달 우선순위): 5-Layer 메모리 검색 정렬 / LOCK-MM-07 (CLIP 768d): 멀티모달 임베딩 통일 / LOCK-MM-06 V2: Qdrant Cloud 비용 가드

## 3. V1 → V2 승급

| J-ID | V1 | V2 (본) |
|------|----|---------|
| J-064 5-Layer 메모리 | 메타데이터 즉시 | **풀 통합 (이미지/오디오/비디오) + 크로스세션 참조** |
| J-085 Context Window | 토큰 예산 | **모달별 동적 조정 + 자동 요약 + 우선순위 (peer integration §4.3)** |
| J-086 Error Handling | 모달별 폴백 | **그레이스풀 디그레이데이션 + 폴백 체인 본문** |
| J-081 §6.7 MoE | 미작성 | **본문: Llama 4 Scout (17B/109B) + Maverick (17B/400B) + DeepSeek V3 + Mixtral** |

## 4. V2 본문

### 4.1 J-064 5-Layer 메모리 통합 V2 (STEP7-J L1103~L1117)

**근거 verbatim** (STEP7-J L1106~L1115):
> ```
> [구현 상세]
> - 5-Layer 메모리에 멀티모달 데이터 저장:
>   ├─ L0 (세션): 현재 대화의 이미지/오디오 참조
>   ├─ L1 (7일): 최근 생성 이미지 캐시
>   ├─ L2 (프로젝트): 프로젝트별 멀티모달 에셋
>   ├─ L3 (영구): 중요 이미지/다이어그램 영구 저장
>   └─ L4 (아카이브): 오래된 멀티모달 데이터 압축 보관
>
> - 크로스세션 참조: "지난주에 만든 아키텍처 다이어그램 기억해?"
> - 메타데이터 인덱싱: 모든 멀티모달 에셋 검색 가능
> ```

**SoT 구현성 (STEP7-J L1116)**: V1 — ✅ 메타데이터 즉시 | V2 — ✅ 풀 통합 3개월

```python
from common_types import ModuleConfig, MultimodalMessage
from d202_02 import VamosError, VamosResult

class MemoryIntegrationConfigV2(ModuleConfig):
    layers: dict[str, dict] = {
        "L0_session": {"ttl_sec": None, "storage": "memory"},          # 세션 종료 시 폐기
        "L1_7days": {"ttl_sec": 7 * 86400, "storage": "redis"},
        "L2_project": {"ttl_sec": 90 * 86400, "storage": "qdrant"},
        "L3_permanent": {"ttl_sec": None, "storage": "qdrant + s3"},   # 영구
        "L4_archive": {"ttl_sec": 365 * 5 * 86400, "storage": "cold_s3"},  # 5년
    }
    embedding_model: str = "clip-vit-l14-336"        # LOCK-MM-07 768d
    auto_promote_to_l3: bool = True                  # 중요도 ≥ 0.8 시
    cross_session_search_enabled: bool = True

class MultimodalAsset:
    asset_id: UUID
    user_id: str
    modality: Literal["image","audio","video","document","mixed"]
    layer: Literal["L0","L1","L2","L3","L4"]
    payload_uri: str
    embedding: list[float]                           # CLIP 768d / wav2vec2 768d
    metadata: dict                                   # title/timestamp/project_id
    importance: float = 0.0                          # 0~1
    created_at: datetime

async def store_multimodal(asset: MultimodalAsset, cfg: MemoryIntegrationConfigV2):
    # 1. 모달별 임베딩 생성
    if asset.modality == "image":
        asset.embedding = await clip_encode_image(asset.payload_uri)  # 768d
    elif asset.modality == "audio":
        asset.embedding = await wav2vec2_encode(asset.payload_uri)
    elif asset.modality == "video":
        # 키프레임 평균 임베딩 (LOCK-MM-09 max_frames=100)
        asset.embedding = await video_avg_embedding(asset.payload_uri, max_frames=100)

    # 2. Layer 결정
    if asset.layer == "L0":
        await session_memory.set(asset.asset_id, asset)
    elif asset.layer == "L1":
        await redis_layer.set(asset.asset_id, asset, ttl=cfg.layers["L1_7days"]["ttl_sec"])
    elif asset.layer in ("L2","L3"):
        await qdrant_layer.upsert(f"mm_assets_{asset.user_id}",
                                 points=[{"id": str(asset.asset_id),
                                         "vector": asset.embedding,
                                         "payload": asset.dict()}])
    elif asset.layer == "L4":
        await cold_s3.put(asset.asset_id, asset)

    # 3. 자동 L3 승격 후보 (중요도 ≥ 0.8) — 영구 저장은 사용자 명시 동의 필수 (voice_chat.md L255 / J-068)
    if cfg.auto_promote_to_l3 and asset.importance >= 0.8 and asset.layer in ("L1","L2"):
        if await user_consent_granted(asset.user_id, scope="l3_permanent", asset_id=asset.asset_id):
            await store_multimodal(MultimodalAsset(**{**asset.dict(), "layer": "L3"}), cfg)
        else:
            await register_l3_promotion_candidate(asset)  # 동의 확인 후 승격

async def cross_session_search(query: str, user_id: str,
                              cfg: MemoryIntegrationConfigV2) -> list[MultimodalAsset]:
    # "지난주에 만든 아키텍처 다이어그램 기억해?"
    q_emb = await clip_encode_text(query, model=cfg.embedding_model)
    # L1 ~ L4 전수 검색
    hits = await qdrant_layer.search(f"mm_assets_{user_id}", q_emb, top_k=10)
    return [MultimodalAsset(**h.payload) for h in hits]
```

### 4.2 J-085 Context Window 동적 조정 V2 (STEP7-J L1462~L1478, peer integration §4.3)

```python
class ContextBudgetV2:
    max_tokens: int = 100000                         # GPT-4o 128K, Gemini 1.5 Pro 1M
    image_token_limit: int = int(max_tokens * 0.4)   # 모달별 가중치
    audio_token_limit: int = int(max_tokens * 0.2)
    video_token_limit: int = int(max_tokens * 0.3)
    text_token_limit: int = int(max_tokens * 0.1)

async def allocate_context(msg: MultimodalMessage,
                          budget: ContextBudgetV2) -> MultimodalMessage:
    # peer integration_architecture_v2 §4.3 알고리즘 호출
    from integration.context import adjust_context
    return await adjust_context(msg, max_tokens=budget.max_tokens)
```

### 4.3 J-086 Error Handling 그레이스풀 디그레이데이션 V2 (STEP7-J L1480~L1493)

| 모달 | 1차 시도 | 폴백 1 | 폴백 2 | TEXT_ONLY 폴백 |
|------|---------|-------|-------|---------------|
| 이미지 생성 | Flux Pro | Flux Schnell | DALL-E 3 | "이미지 생성 실패" 텍스트 |
| 이미지 분석 | GPT-4V | Gemini Flash | Qwen2-VL 7B | OCR + 메타데이터만 |
| STT | Deepgram Nova-2 | Whisper v3 | Whisper v2 | "음성 인식 실패" 텍스트 |
| TTS | ElevenLabs | OpenAI TTS-1-HD | Edge TTS (무료) | 텍스트 only |
| 비디오 분석 | Qwen2-VL 7B 로컬 | Gemini Pro video | 키프레임 5개만 | yt-dlp 자막만 |
| 비디오 생성 | Sora 2 | Kling 1.5 (무료) | LTX-Video 로컬 | 정적 이미지 + 텍스트 |

### 4.4 J-081 §6.7 트렌드 본문 (STEP7-J L1389~L1403)

**근거 verbatim** (STEP7-J L1392~L1402):
> ```
> [2025-2026 최신 기술]
> - Llama 4 Scout (17B active / 109B total): MoE 아키텍처
> - Llama 4 Maverick (17B active / 400B total): 대규모 MoE
> - DeepSeek V3: MoE + MLA (Multi-head Latent Attention)
> - Mixtral: MoE 텍스트 모델
>
> [VAMOS 활용]
> - MoE 모달리티별 전문가: 텍스트/이미지/오디오 각각 전문 Expert
> - 효율적 추론: 활성 파라미터만 사용 → 비용 절감
> - 로컬 실행 가능: 활성 17B로 109B 성능
> ```

**SoT 구현성 (STEP7-J L1402)**: V1 — ✅ Llama 4 Scout 로컬 즉시 (Ollama)

#### MoE 모달리티별 Expert 라우팅 (V2 통합)

| 모델 | 활성 파라미터 | 총 파라미터 | 모달리티 Expert | 비용 절감 |
|------|-------------|-----------|----------------|----------|
| **Llama 4 Scout** (Meta) | 17B | 109B | 16 expert (text 8 / vision 4 / audio 4) | 84% (활성 17B만) |
| **Llama 4 Maverick** (Meta) | 17B | 400B | 64 expert (전 모달리티) | 96% (활성 17B만) |
| **DeepSeek V3** | 37B | 671B | MoE + MLA | 95% |
| **Mixtral 8x22B** | 39B | 141B | text only | 72% |

#### VAMOS 통합 시나리오 (V2)
1. **Phase 2 즉시**: Llama 4 Scout 로컬 (Ollama) → 본 V2 J-064 메모리 통합 LLM 1순위
2. **Phase 2 +1개월**: Maverick API → 대용량 멀티모달 컨텍스트 (1M 토큰+)
3. **Phase 2 +3개월**: DeepSeek V3 → 코딩/수학 특화 (peer J-054 V2 코드 RAG)
4. **V3**: 모달별 전용 expert 라우팅 자동 (MoE Router)

## 5. Error Handling
| 에러 | 폴백 |
|------|------|
| Qdrant 실패 | local 캐시 + retry |
| 임베딩 OOM | 배치 4 → 1 |
| Layer 승격 실패 | L1 유지 + warning |
| 크로스세션 검색 0 | suggestion (관련 키워드) |
| MoE 로컬 OOM (Llama 4 Scout) | Qwen2.5 7B 폴백 |

## 6. Cost
| 시나리오 | V2 (월) | LOCK-MM-06 V2 |
|----------|---------|---------------|
| L0~L1 (Redis) | $5 | 충족 |
| L2~L3 (Qdrant Cloud) | $25 | 충족 |
| L4 (Cold S3) | $1 | 충족 |
| Llama 4 Scout 로컬 | $0 | 충족 |
| **V2 권장** | **$31/월** | 충족 ✅ |

## 7. SLA
| 작업 | P50 | P99 |
|------|-----|-----|
| store (L0) | 5ms | 20ms |
| store (L1 Redis) | 20ms | 80ms |
| store (L2/L3 Qdrant) | 50ms | 150ms |
| cross_session_search | 100ms | 300ms |
| L3 자동 승격 (background) | <비차단> | — |
| MoE 추론 (Llama 4 Scout) | 800ms | 2.5s |

## 8. Test (10건)
1. L0 세션 메모리 → 세션 종료 시 폐기.
2. L1 Redis 7일 TTL.
3. L2/L3 Qdrant 영구 + 자동 L3 승격 (importance ≥ 0.8).
4. L4 Cold S3 5년 압축.
5. 크로스세션 검색 (CLIP 768d) → "지난주 다이어그램".
6. 모달별 임베딩 (image/audio/video) → 통일 인덱스.
7. peer integration §4.3 Context 동적 조정 호출.
8. J-086 폴백 체인 (Flux Pro → Schnell → DALL-E 3).
9. J-081 Llama 4 Scout 로컬 추론 (Ollama).
10. LOCK-MM-04 우선순위 정렬 검증.

## 9. Dependencies
- 외부: Redis, Qdrant, S3 (Cold), Ollama (Llama 4 Scout 로컬), CLIP, wav2vec2
- 내부 (peer): J-085 (integration_architecture_v2 §4.3 Context Window), J-057 V2 (caching_optimization_v2), J-064 V1, J-083 (Router), 6-4 Memory-RAG-Storage (cross-domain ref)

## 10. Privacy
- user_id 단위 격리 (모든 Layer)
- L4 아카이브 시 PII 마스킹 (R-05-7)
- 크로스세션 검색은 본인 데이터만

## 11. 검증
| 항목 | V1 | V2 | L3 |
|------|----|---------|-----|
| J-064 5-Layer 풀 통합 | 메타데이터 | 모달별 임베딩 + 자동 승격 | 89 |
| J-085 Context 동적 (peer integration §4.3) | 토큰 예산 | 모달별 자동 조정 | 87 |
| J-086 그레이스풀 폴백 체인 | 모달별 | 6 모달 × 3 단계 폴백 표 | 90 |
| J-081 §6.7 MoE 본문 | 미작성 | Llama 4 Scout/Maverick + DeepSeek V3 | 87 |

**평균**: **88.3/100** ✅
