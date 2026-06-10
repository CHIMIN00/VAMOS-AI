# 멀티모달 V2 + ImageBind 마이그레이션 — L3 상세 명세

> **도메인**: 6-1_UI-UX-System / 02_hologram-view
> **세션**: P2-1 (Phase 2)
> **버전**: v1.0 (2026-04-26)
> **정본 출처**: D2.0-08 §6.4.1 (CLIP→ImageBind 마이그레이션 정본) / D2.0-08 §10.1 (테마색) / D2.0-08 §5.1 (이벤트 네이밍) / Part2 §6.1.5 (멀티모달 V1~V3)
> **종합계획서**: §7.3 P2-1 (L1583~L1616) / §6 ISS-5 (D8-L03 완전 해결)
> **상위 SoT**: STEP7-C UI/UX 전수비교 작업가이드 (manifest L72 단일, 235 L)
> **선행**: 02_hologram-view/multimodal_ui_v1.md (V1 6건 정본)

---

## 1. 개요

본 문서는 V1 멀티모달 UI(이미지/OCR/STT/TTS/차트/문서) 위에 V2 ImageBind 통합을 얹어 6 신규 기능(통합 검색, 음성→텍스트 UI, 이미지 유사도 HUD, 멀티모달 캐시, Glass HUD 오버레이, 3-point 렌더링 V2)을 L3로 정의하고, **D8-L03 (CLIP ViT-B/32 → ImageBind 마이그레이션 미문서화)** 을 호환성 레이어 + 전환 일정 + 롤백 방안으로 완전 해결한다 (§6 ISS-5 PARTIALLY-RESOLVED → RESOLVED).

**범위**: UI 레이어(6-1) — 컴포넌트 구조 / Glass HUD 표시 / 사용자 인터랙션. 백엔드 임베딩 추론 / 모델 서빙 / GPU 자원은 6-11 Hologram-Main-LLM 및 4-4 MLOps-LLMOps 소관 (DH-W-1 RESOLVED 6-1 UI 구조 vs 6-11 렌더링).

---

## 2. LOCK 참조 (4-field verbatim, AUTHORITY_CHAIN §4)

> **재정의 금지** — LOCK ID + 항목 + 정본 출처 + 값 4-field 분리 인용. `> LOCK (출처): [원문 그대로]` 형식 준수.

| LOCK ID | 항목 | 정본 출처 | LOCK 값 |
|---------|------|----------|---------|
| **L1** | UI 9-State | D2.0-08 §4.1 | UI_S0_BOOT, UI_S1_IDLE, UI_S2_EDITING, UI_S3_READY, UI_S4_RUNNING, UI_S5_AWAIT_APPROVAL, UI_S6_PRESENTING, UI_S7_RECOVERY, UI_S8_ARCHIVED (9개) |
| **L5** | ORANGE 테마색 | D2.0-08 §10.1 | #F97316 (ORANGE CORE) — CONF-61-001 RESOLVED |
| **L6** | BLUE 테마색 | D2.0-08 §10.1 | #00F6FF (BLUE NODE) — CONF-61-002 RESOLVED |
| **L7** | 다크모드 | D2.0-08 §10.1 / Part2 V1-P4 | 기본값 = Dark (#1E1E1E), Light는 토글 |
| **L11** | V1 최소 해상도 | D2.0-08 §3.1 | 1280 x 720 (데스크톱 전용) |
| **L12** | Tauri 기본 크기 | D2.0-08 §3.1 | 1440 x 900 |
| **L17** | 상태 전이 지연 | D2.0-08 §4.4 | 최대 500ms |
| **L19** | 이벤트 네이밍 | D2.0-08 §5.1 | `ui.{layer}.{subject}.{action}` |

> **LOCK (D2.0-08 §6.4.1 J-001 L756~L758, 원문 그대로)**:
> - V1: 로컬 CLIP ViT-B/32 임베딩 + API 멀티모달 모델 전송
> - V2: 자체 이미지 임베딩 서버 (CLIP ViT-L/14, SigLIP)
> - V3: 커스텀 비전 인코더 파인튜닝

> **LOCK (D2.0-08 §6.4.1 J-007 L808, 원문 그대로)**: V1: CLIP 기본 | V2: ImageBind 통합 3개월

> **LOCK (D2.0-08 §6.4.1 J-007 L803, 원문 그대로)**: 모델: CLIP(이미지-텍스트), ImageBind(6모달리티 통합), CLAP(오디오-텍스트)

> **LOCK (D2.0-08 §6.4.1 J-007 L806~L807, 원문 그대로)**: 벡터DB 확장: Chroma/Qdrant 컬렉션 — text_embeddings(BGE-M3, 1024dim LOCK), image_embeddings(CLIP 768d), audio_embeddings(CLAP 512d), multimodal_index(통합 검색용). ⚠️ 텍스트 임베딩은 BGE-M3/1024dim (DEC-005 UPDATED LOCK). CLIP 768d는 이미지 전용이며, 텍스트와 혼용하지 않는다.

> 본 V2 문서는 LOCK 신규 추가 0건 (V3 범위 이월). LOCK L13 ~44 → 48개 확장은 P2-3 v12_components.md 에서 카탈로그 append (정의 변경 없음).

---

## 3. ISS-5 D8-L03 완전 해결 — CLIP→ImageBind 마이그레이션

### 3.1 D8-L03 원문 (Part2 §6.1.5 L4619~L4620 정본)

> **V2 사전 해결 필요 (PART1 A.4에서 이동)**
> - **D8-L03**: D2.0-08 §6.4.1 CLIP 버전별 차원(512d→768d) 마이그레이션 미문서화 — V2 ImageBind 통합 전 ADD 필요

### 3.2 차원/모델 마이그레이션 매트릭스

| 단계 | 모델 | 차원 | 처리 모달리티 | UI 표기 (Glass HUD) | Phase |
|------|------|------|--------------|---------------------|-------|
| V1 | CLIP ViT-B/32 | 512d | 텍스트 + 이미지 | `MM:CLIP-B/32 (512d)` ORANGE 배지 | V1-P4 (Week 13-14) ✅ |
| V2-A (호환 단계) | CLIP ViT-L/14 | 768d | 텍스트 + 이미지 | `MM:CLIP-L/14 (768d)` ORANGE 배지 | V2 1개월 |
| V2-B (확장 단계) | SigLIP | 768d | 텍스트 + 이미지 (대비손실 고도화) | `MM:SigLIP (768d)` ORANGE 배지 | V2 2개월 |
| V2-C (통합 단계) | ImageBind | 768d | 6모달리티 통합 (이미지/텍스트/오디오/IMU/심도/열) | `MM:ImageBind (768d) ★6모달` BLUE 배지 | V2 3개월 |
| V3 | 커스텀 비전 인코더 | 미정 | 파인튜닝 멀티모달 | `MM:Custom (V3 fine-tune)` | V3 |

### 3.3 호환성 레이어 — `MultimodalEmbeddingAdapter`

```typescript
// 6-1 UI 측 호환 어댑터 인터페이스 (실제 추론은 6-11 / 4-4 소관)
interface MultimodalEmbeddingAdapter {
  // 모델 식별: V1 CLIP-B/32 / V2-A CLIP-L/14 / V2-B SigLIP / V2-C ImageBind
  modelId: "CLIP-B/32" | "CLIP-L/14" | "SigLIP" | "ImageBind" | "Custom-V3";
  dimension: 512 | 768 | 1024;
  modalities: ("text" | "image" | "audio" | "imu" | "depth" | "thermal")[];

  // UI 측 표시 메타: 어떤 임베딩을 사용 중인지 Glass HUD에 노출
  displayBadge(): { label: string; color: "ORANGE" | "BLUE"; tooltip: string };

  // V2 전환 중 V1 임베딩 결과를 새 차원으로 사상하지 않음 (서로 다른 공간).
  // UI는 단순히 modelId를 표시하고, 검색 결과 해석은 백엔드 메타데이터에 의존.
  // 호환 규칙: 동일 컬렉션 내 차원 혼합 금지 → 백엔드(6-4 Memory-RAG-Storage)
  // Chroma/Qdrant 별도 컬렉션 운영 (D2.0-08 §6.4.1 J-007 L807 원문 준수).
}
```

### 3.4 전환 일정 (3개월, D2.0-08 §6.4.1 J-007 L808 정본 준거)

| 월 | 단계 | 6-1 UI 작업 | 6-11/4-4 백엔드 작업 (참조만) | 사용자 영향 |
|----|------|-------------|------------------------------|--------------|
| M1 | V2-A 호환 단계 | Glass HUD 배지 모델 라벨 노출 + `MultimodalEmbeddingAdapter` 인터페이스 도입 | CLIP ViT-L/14 모델 서빙 시작 (4-4 MLOps), 컬렉션 `image_embeddings_v2` 신규 (6-4) | V1 사용자: 변화 없음 (V1 컬렉션 유지). V2 opt-in 사용자: ViT-L/14 정확도 향상 |
| M2 | V2-B 확장 단계 | "이미지 유사도 임계값" 사용자 설정 슬라이더 추가 (`SimilarityThresholdSlider`) | SigLIP 추가 모델 서빙 + A/B 테스트 (4-4) | 검색 정확도 ~3-5% 향상 (사용자 설정 기반 토글) |
| M3 | V2-C 통합 단계 | "통합 검색" 새 패널 (`UnifiedSearchPanel`), 6모달리티 입력 UI (image/audio drop 추가) | ImageBind 모델 서빙 + 통합 컬렉션 `multimodal_index` (6-4 J-007 L806 정본) | 통합 검색 정식 출시. V1 컬렉션은 deprecation 예고 (V3 시점 제거) |

### 3.5 롤백 방안 — `RollbackPlan` (3 단계)

| 발동 조건 | 자동/수동 | 6-1 UI 동작 | 6-11/4-4 백엔드 동작 (참조만) | 사용자 영향 |
|-----------|-----------|-------------|------------------------------|--------------|
| **R1: 모델 서빙 SLA 미달** (p99 latency > 5s 30분 지속) | 자동 | Glass HUD 배지 색상 → 회색(`stale`), `<MultimodalDegradationToast>` 발화 | 트래픽을 V1 CLIP-B/32 컬렉션으로 즉시 라우팅 | V2 검색 정확도 일시 저하, 사용자 안내 토스트 |
| **R2: 정확도 회귀 감지** (사용자 만족도 ≤ V1 -10% 7일 평균) | 수동 (OWNER 승인) | 설정 화면에서 "V1 임베딩으로 복귀" 토글 활성화, 토글 시 `<RollbackConfirmDialog>` (LOCK L18 P2 승인 5분 타임아웃 적용) | OWNER 승인 시 V2-B/V2-C 컬렉션 read-only 전환 + V1 트래픽 100% 복귀 | OWNER가 결정. 일반 사용자는 자동 V1 fallback |
| **R3: 데이터 무결성 손상** (임베딩 컬렉션 sha 검증 실패) | 자동 | Glass HUD 빨간 `[INTEGRITY:embedding_corrupted]` 배너 + 검색 비활성화 | 컬렉션 백업 복원 (4-4 RPO 24h, RTO 4h) | 일시적 멀티모달 검색 중단, 텍스트 검색은 정상 (BGE-M3 별도 컬렉션) |

> **D8-L03 해결 선언**: 본 §3.1~§3.5 로 CLIP→ImageBind 마이그레이션 경로/차원/일정/롤백 4축 전부 문서화. ISS-5 PARTIALLY-RESOLVED → RESOLVED 상태 전환 (도메인 마감 step 7 crossref_sync 에서 plan §6 + AUTHORITY 변경 이력 cascade).

---

## 4. 멀티모달 V2 6 기능 정의 (L3 9요소 E1~E9)

### 4.1 기능 #1 — ImageBind 통합 검색 (`UnifiedSearchPanel`)

| L3 요소 | 내용 |
|---------|------|
| **E1 Input** | { query: string, modalities: Set<"text"\|"image"\|"audio">, top_k: number=10, similarity_threshold: number=0.7 } — text/image/audio drop zone. drop 시 `useMultimodalDropzone` Hook |
| **E2 State** | UI_S2_EDITING(쿼리 작성) → UI_S4_RUNNING(검색 중) → UI_S6_PRESENTING(결과 표시). 전이 지연 ≤ 500ms (LOCK L17). 검색 중 `<UnifiedSearchSpinner>` ORANGE 표시 |
| **E3 Output** | `Array<UnifiedSearchResult>` — { rank, score, modality, source_id, preview_url\|preview_text\|preview_audio_clip, embedding_metadata: { model_id, dimension } } |
| **E4 Class/API** | `<UnifiedSearchPanel topK={10} threshold={0.7} onResult={fn} />`. 백엔드 호출: `vamos:multimodal:search` (4-1 IPC 커맨드 그룹 Storage 19개 중 1개 — IPC 정의는 4-1 소관, 6-1은 호출 인터페이스만) |
| **E5 Style** | Glass HUD 우측 패널 (≤ 350-400px LOCK L3). 결과 카드: ORANGE #F97316 헤더 / BLUE #00F6FF 강조 / 다크 배경 #1E1E1E (LOCK L5/L6/L7) |
| **E6 Accessibility** | 결과 카드별 aria-label 음성 출력 호환, 키보드 ↑/↓ 탐색, Enter 선택, Esc 닫기. WCAG 2.1 AA 대비 ≥ 4.5:1 (LOCK L8) |
| **E7 Error** | `EM_ERR_MODEL_LATENCY` (p99 > 5s) → §3.5 R1 자동 롤백. `OC_ERR_NO_RESULT` → "결과 없음, 임계값 낮춰 재검색" 안내 (FailureCode 참조 D2.0-08 §7.6) |
| **E8 Test** | unit: 결과 정렬 / threshold 필터 / 모달리티 토글. integration: ImageBind 응답 mock 으로 컬렉션 라우팅. e2e: V2-C 단계에서 image+text 동시 검색 1초 이내 |
| **E9 Event** | `ui.hologram.unified_search.started` / `.result_received` / `.fallback_to_v1` (LOCK L19 네이밍 준수, 6-12 Event-Logging 동기 — P2-4 협력 대상) |

### 4.2 기능 #2 — 음성→텍스트 변환 UI (`VoiceToTextPanel`)

| L3 요소 | 내용 |
|---------|------|
| **E1 Input** | mic stream (MediaStream API) → 청크 단위 (1초/16kHz/mono PCM) |
| **E2 State** | UI_S2_EDITING (녹음 중, 빨간 점) → UI_S4_RUNNING (스트리밍 STT 호출) → UI_S6_PRESENTING (텍스트 표시) |
| **E3 Output** | `{ partial_text: string, final_text: string, confidence: number, is_final: boolean }` — 스트리밍 부분 결과 + 최종 결과 |
| **E4 Class/API** | `<VoiceToTextPanel onPartial={fn} onFinal={fn} />`. Whisper(V1) → SeamlessM4T (V2) 백엔드 어댑터 (4-4 MLOps 소관). 6-1은 stream 인터페이스만 |
| **E5 Style** | 좌측 ≤ 250-300px (LOCK L2) 또는 중앙 모달. 파형 시각화 BLUE #00F6FF, 녹음 인디케이터 ORANGE #F97316 깜빡임 (1Hz) |
| **E6 Accessibility** | 키보드 단축키 Ctrl+Shift+V (시작/정지), 스크린리더에 "음성 입력 시작/종료" 안내, 청각 장애 사용자 시각 파형 + 진행률 텍스트 |
| **E7 Error** | `MIC_PERMISSION_DENIED` → 설정 안내 모달. `STT_TIMEOUT` (10초 무음) → 자동 정지 + 재시작 버튼 (FailureCode 참조 D2.0-08 §7.6) |
| **E8 Test** | unit: 마이크 권한 mock / 청크 buffering / partial→final 전이. integration: STT 백엔드 응답 mock. e2e: 한국어 5초 발화 → WER ≤ 10% (V1 KPI, J-098) |
| **E9 Event** | `ui.hologram.voice_to_text.started` / `.partial_received` / `.finalized` / `.error` (LOCK L19) |

### 4.3 기능 #3 — 이미지 유사도 HUD (`ImageSimilarityHUD`)

| L3 요소 | 내용 |
|---------|------|
| **E1 Input** | { reference_image: ImageRef, candidate_images: ImageRef[], similarity_metric: "cosine" \| "dot" = "cosine" } |
| **E2 State** | UI_S4_RUNNING (임베딩 계산) → UI_S6_PRESENTING (Top-N 격자 표시) |
| **E3 Output** | `Array<ImageSimilarity>` — { image_id, similarity_score: 0~1, embedding_model: "CLIP-B/32"\|"CLIP-L/14"\|"SigLIP"\|"ImageBind", thumbnail_url } |
| **E4 Class/API** | `<ImageSimilarityHUD reference={imgRef} candidates={list} top={6} />`. 호출: `vamos:multimodal:similarity` (4-1 IPC 인터페이스만, 백엔드는 6-11/4-4) |
| **E5 Style** | Glass HUD 오버레이 (Right Panel ≤ 350-400px LOCK L3) — 6-grid, 각 셀에 score 라벨(BLUE) + similarity 진행 바(ORANGE), 다크 배경 #1E1E1E |
| **E6 Accessibility** | aria-describedby 로 점수 → "유사도 87%" 음성 안내. 키보드 Tab 순회. 색약 사용자: 색상 + 패턴(스트라이프/도트) 이중 표기 |
| **E7 Error** | `EMBEDDING_DIM_MISMATCH` (V1↔V2 차원 혼합) → "동일 모델 임베딩으로 비교하세요" 안내 (§3.3 호환 어댑터 정책) |
| **E8 Test** | unit: cosine vs dot product 계산. integration: 6 candidates Top-3 정렬. e2e: V2-C ImageBind 1024d 결과 6셀 ≤ 800ms |
| **E9 Event** | `ui.hologram.image_similarity.computed` / `.dim_mismatch` / `.shown` (LOCK L19) |

### 4.4 기능 #4 — 멀티모달 캐시 (6-4 Semantic Cache 연동, `MultimodalCacheStatusBadge`)

| L3 요소 | 내용 |
|---------|------|
| **E1 Input** | { request_hash: string, cache_layer: "L0_session" \| "L1_project" \| "L2_global" } |
| **E2 State** | UI_S4_RUNNING (캐시 조회 → hit/miss 결정) → UI_S6_PRESENTING (캐시 hit 배지 표시) |
| **E3 Output** | `{ hit: boolean, layer: string, age_seconds: number, source_request_id?: string }` |
| **E4 Class/API** | `<MultimodalCacheStatusBadge requestId={id} />`. 6-1은 표시만. 캐시 정책 / TTL / 적중률 측정은 6-4 Memory-RAG-Storage 소관 (참조만, 6-4 LOCK-MR 재정의 ❌) |
| **E5 Style** | Cache HIT: BLUE #00F6FF 배지 "L1 hit (3s)". Cache MISS: 회색 "miss"). HUD 우측 상단 마이크로 배지 |
| **E6 Accessibility** | 배지 hover 툴팁 + aria-label "캐시 적중 L1 프로젝트 3초 전 동일 요청" |
| **E7 Error** | `CACHE_BACKEND_UNAVAILABLE` → 배지 숨김 + 검색 정상 진행 (캐시는 최적화이지 의존성 아님) |
| **E8 Test** | unit: hit/miss 렌더링. integration: 6-4 mock 응답 L0/L1/L2 분기. e2e: 동일 쿼리 2회 → 2회차 hit 배지 노출 |
| **E9 Event** | `ui.hologram.cache.hit` / `.miss` / `.unavailable` (LOCK L19) |

### 4.5 기능 #5 — Glass HUD 멀티모달 오버레이 (`MultimodalGlassHUD`)

| L3 요소 | 내용 |
|---------|------|
| **E1 Input** | { active_modalities: Set<modality>, current_model: ModelId, search_in_progress: boolean, last_result_summary?: ResultSummary } |
| **E2 State** | UI_S1_IDLE (배지만 노출) ↔ UI_S4_RUNNING (진행률 링) ↔ UI_S6_PRESENTING (결과 요약 카드) |
| **E3 Output** | 시각적 오버레이만 (data sink). 사용자 클릭 시 `UnifiedSearchPanel` 열기 |
| **E4 Class/API** | `<MultimodalGlassHUD>` Wrapper, slot 패턴: Status / Progress / Summary 3 slot. backdrop-filter: blur(12px), 다크 배경 #1E1E1E + 70% 투명도 |
| **E5 Style** | ORANGE #F97316 → 활성 ORANGE 모달 / BLUE #00F6FF → 활성 BLUE Node / WCAG AA 대비율 ≥ 4.5:1 (LOCK L5/L6/L8) |
| **E6 Accessibility** | role="region" aria-label="멀티모달 상태 패널". 키보드 Alt+M 으로 포커스 이동 |
| **E7 Error** | 배지 렌더링 실패 시 fallback 텍스트 "MM:idle" |
| **E8 Test** | unit: 3 slot 렌더링. integration: 활성 모달리티 변화에 따른 색상 전환. visual regression: blur backdrop 1280×720 / 1440×900 (LOCK L11/L12) |
| **E9 Event** | `ui.hologram.glass_hud.opened` / `.modality_changed` (LOCK L19) |

### 4.6 기능 #6 — 3-point 렌더링 V2 품질 (`StreamingEffectV2`)

| L3 요소 | 내용 |
|---------|------|
| **E1 Input** | { user_response_chunk: string, evidence_summary?: EvidenceSummary, log_report?: LogReport } — 6-11 LLM 스트림 인터페이스 (참조만) |
| **E2 State** | UI_S4_RUNNING (스트리밍 출력 진행) → UI_S6_PRESENTING (스트림 종료, 3 파트 완성) |
| **E3 Output** | DOM 업데이트만 (data sink) — 3 파트: user_response (메인) + evidence_summary (접기) + log_report (접기) |
| **E4 Class/API** | `<StreamingEffectV2 stream={readableStream} />` — V1 `<StreamingEffect>` 대체. 토큰 단위 ≤ 30ms 렌더링 (V1 ≤ 50ms 대비 단축) |
| **E5 Style** | user_response: 본문 텍스트 (다크 배경 #1E1E1E + ORANGE 강조 #F97316). evidence_summary: BLUE #00F6FF 인용 박스. log_report: 모노스페이스 + 회색 |
| **E6 Accessibility** | aria-live="polite" 점진 안내 (스크린리더 깜빡임 방지). 사용자 "스트리밍 중 reduce-motion" 토글 지원 (LOCK L7 다크모드 + reduce-motion) |
| **E7 Error** | 스트림 중단 → `EM_STREAM_INTERRUPTED` 토스트 + "재시도" 버튼 (FailureCode 참조 D2.0-08 §7.6, LOCK L20) |
| **E8 Test** | unit: 청크 buffering / 3 파트 분리 / reduce-motion. integration: 6-11 스트림 mock. e2e: 한국어 1000자 응답 ≤ 5초 (V1 KPI 응답 지연) |
| **E9 Event** | `ui.hologram.stream.chunk_rendered` / `.completed` / `.interrupted` (LOCK L19) |

---

## 5. 6-11 Hologram-Main-LLM 경계 참조 (DH-W-1 RESOLVED)

> **AUTHORITY_CHAIN §5.1 정본 인용** — 본 V2 문서는 6-11 도메인 정본을 재정의하지 않으며, 인터페이스 경계만 명시.

| 구분 | 6-1 (본 V2 문서 범위) | 6-11_Hologram-Main-LLM (참조만) |
|------|----------------------|-------------------------------|
| **범위** | UI 레이어 — Glass HUD 패널 / 6 멀티모달 V2 컴포넌트 / Streaming UI | 렌더링 로직 — Main LLM 파이프라인 / ImageBind 추론 / 3-point 응답 생성 |
| **정본** | React 컴포넌트, 상태관리, Glass HUD 표시, 호출 인터페이스 | LLM 통합, 임베딩 추론, 프롬프트 조합, 콘텐츠 생성 |
| **경계** | `<StreamingEffectV2>` 컴포넌트가 받는 `ReadableStream` 인터페이스 (data contract) | `ReadableStream` 생산자 (스트림 청크 emit) |
| **충돌 시** | 본 V2 산출물 — UI View 구조 정의만, 6-11 정본 재정의 ❌ | 6-11 정본 (DH-W-1 RESOLVED, S6-2/S6-4 경계 확정) |

> **본 V2 문서가 정의하지 않는 것** (6-11 소관): ImageBind 모델 서빙 토폴로지 / GPU 메모리 할당 / 6모달리티 임베딩 융합 알고리즘 / 3-point 응답 분해 LLM 프롬프트.

---

## 6. STEP7-C 상위 SoT 매핑 (P2-1 범위)

| STEP7-C 항목 ID | 출처 (235L) | V2 P2-1 매핑 |
|-----------------|-------------|--------------|
| S7C-026 음성 입력 버튼 | Part 3 (L84) | §4.2 `VoiceToTextPanel` |
| S7C-051 멀티모달 음성 | Part 5 (L1838 — D2.0-08 §6 연동) | §4.2 + §4.5 (Glass HUD 오버레이) |
| S7C-018 차트/그래프 인터랙티브 | Part 2 (L69) | §4.1 `UnifiedSearchPanel` 결과 카드 (차트 modality 미래 확장 포인트) |
| S7C-022 Decision Object 시각화 | Part 2 (L73) | §4.6 `StreamingEffectV2` evidence_summary |
| (잔여 매핑은 P2-4 event_type_v2_sync.md 에서 통합) | — | — |

> **upstream baseline**: STEP7-C `9c7b4ea26c2d1d1d6cf32eaa8089e41ee5a16ce913c6f3cb4eed1e1b0f11f709` (235 L) — 본 V2 문서는 STEP7-C 본문을 인용만 하며 **수정 0건**.

---

## 7. Phase 배정 및 의존성

| 항목 | 값 |
|------|-----|
| **Phase 배정** | Phase 2 (V2 리팩토링) — V2-A M1 / V2-B M2 / V2-C M3 (D2.0-08 §6.4.1 J-007 L808 정본) |
| **Phase 1 의존성** | multimodal_ui_v1.md (V1 6건 정본), hologram_view.md (Glass HUD 3-Pane Layout) |
| **상위 도메인** | 6-11 Hologram-Main-LLM (LLM 추론, ImageBind 모델 서빙) — 참조만 |
| **하위 도메인** | (없음 — 본 V2는 UI 산출물, LOCK 정본 재정의 0건) |
| **Phase 3 이월** | 통합 검색 V3 6모달리티 입력 UI 확장 (3D/AR), 커스텀 비전 인코더 V3 fine-tune UI |

---

## 8. 검증 (§7.3 P2-1 검증 항목 4/4 충족)

- [x] **ISS-5(D8-L03) 완전 해결**: §3.1~§3.5 4축 (원문 인용 / 마이그레이션 매트릭스 / 호환 어댑터 / 전환 일정 / 롤백 방안) 전수 문서화
- [x] **멀티모달 V2 기능 6건** §4.1~§4.6 각각 L3 9요소(E1~E9) 프레임 포함
- [x] **LOCK L5(ORANGE #F97316), L6(BLUE #00F6FF) 테마색** §4.1/§4.3/§4.5/§4.6 Glass HUD 오버레이 반영
- [x] **6-11 Hologram-Main-LLM 경계 참조** §5 명시 (DH-W-1 RESOLVED 인용, 정본 재정의 0건)

---

## 9. 변경 이력

| 일자 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-04-26 | v1.0 | NEW (P2-1) — D8-L03 ImageBind 마이그레이션 4축 / 멀티모달 V2 6 기능 L3 / 6-11 경계. ISS-5 PARTIALLY-RESOLVED → RESOLVED 대상 |

<!-- END OF DOCUMENT -->
