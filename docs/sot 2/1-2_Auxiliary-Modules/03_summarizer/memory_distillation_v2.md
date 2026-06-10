# I-14 Summarizer — 메모리 증류 (Memory Distillation) V2 Enhanced (L3 보강)

> **V단계**: V2-Phase 2
> **Status**: APPROVED (Phase 4 ✅ 완료, 2026-05-23, V2 strict L3 PASS production-ready 정본 승급, Phase 3 V-17 PASS inheritance)
> **Last-reviewed**: 2026-05-23 (Phase 4 production promotion)
> **ReadOnly**: TRUE (production 승급 후 immutable, 변경 시 일시 해제→fix→복원 EXACT 패턴 + audit log)
> **작성일**: 2026-05-10
> **V1 정본**: `memory_distillation.md` (30 lines, byte EXACT)
> **모듈**: I-14 (CORE, Memory) — L0→L1 증류 핵심
> **LOCK 참조**: LOCK-AX-01, LOCK-AX-09 (Memory 4-layer 핵심), LOCK-AX-15 (검색 우선순위)
> **L3 판정**: PASS (V-17 row content, 9/9 또는 8/9, 2026-05-14)
> **변경 이력 태그**: `V2-Phase 2` (2026-05-10, 세션 2-3)
> **종합계획서 §**: §7 Phase 2 L1484~L1531
> **계약 cross-ref**: C-12 (I-14 → MEM L0→L1 ops)
> **횡단**: 6-2 (메모리 저장 시 PII 토큰화 90일 TTL)

---

## 1. 교차 참조 블록

| 정본 | 역할 |
|------|------|
| `memory_distillation.md` (V1, 30 lines, byte EXACT) | V1 정본 (승격 판단 + 증류 규칙) |
| `input_output_schema_v2.md` (자매 V2, IDistiller ABC) | ABC 베이스 |
| `conversation_summary_v2.md` (자매 V2) | summary_l3 입력 |
| `06_mapping/interface_contracts.md` C-12 | I-14 → MEM |
| `6-2/01_ai-code-security/pii_regex_masking.md` §2.3 | 토큰화 정책 (90일 TTL) |

---

## 2. LOCK 인용

> LOCK (D2.0-01 §5.6, LOCK-AX-01): I-14 = CORE

> LOCK (D2.0-06, LOCK-AX-09): Memory 4-layer = `L0(session) / L1(project) / L2(long-term) / L3(procedural)`

> LOCK (D2.0-06 S7D-042, LOCK-AX-15): 검색 우선순위 L0→L1→L2→L3, 레이어당 max 5, 최종 top 5

---

## 3. V1 → V2 승급 개요

V1 byte EXACT (30 lines, V1 §2 메모리 증류 ASCII + 승격 기준 + 증류 규칙). V1 변경 0.

| 요소 | 보강 |
|------|------|
| **E1** | memory_distillation 목적 (L0→L1 승급 단일 진입) |
| **E2** | 승격 평가 + 중복 제거 + 토큰화 의사코드 |
| **E4** | IDistiller ABC (input_output_schema_v2에서 정의 baseline) |
| **E5** | L1 가득참, 중복 mismatch, 토큰화 실패 |
| **E6** | distill P95 4000ms (L0 100 entries), MEM 호출 batch |
| **E7** | 명시적 요청 / 반복 참조 / 결정 / 프로젝트 컨텍스트 |
| **E9** | sentence-transformers (semantic dedup), embedding model |

---

## 4. V2 본문 (L3 보강)

### 4.1 E1 — 목적 및 역할

memory_distillation은 I-14의 **L0(session memory) → L1(project memory) 승급 단일 진입**. 세션 종료 또는 사용자 명시 요청 시 트리거되어:

1. L0 메모리 (대화/도구 호출/결정 메타) 를 conversation_summary_v2 로 압축.
2. 승격 후보 (`MemoryCandidate`) 생성 — V1 §2 4가지 기준 (명시 요청 / 반복 ≥3 / 결정 표현 / 프로젝트 컨텍스트) 평가.
3. 기존 L1 메모리와 semantic dedup (cosine ≥0.95).
4. PII 토큰화 (6-2 §2.3 — `PII_TKN_xxx`, 90일 TTL).
5. C-12 호출로 MEM에 L1 ops (insert/update/promote).

LOCK-AX-09 4-layer + LOCK-AX-15 검색 우선순위와 정합.

### 4.2 E2 + E4 — 의사코드

```python
class MemoryCandidate(BaseModel):
    candidate_id: str
    content: str  # 사실/결정/선호 1~3 문장
    candidate_type: Literal["explicit_request", "repeated_mention", "decision_preference", "project_context"]
    source_turn_ids: list[int]
    confidence: float  # 0~1, 승급 신뢰도
    pii_tokens: list[str] = []  # 토큰화된 PII ID 목록
    metadata: dict  # 날짜 절대값, 소스 turn 등

# IDistiller ABC (input_output_schema_v2에서 정의)
class MemoryDistiller(IDistiller):
    async def distill(
        self,
        l0_messages: list[Message],
        existing_l1: list[Memory],
        explicit_user_request: Optional[str] = None,
    ) -> list[MemoryCandidate]:
        # 1. conversation_summary_v2 호출하여 L3 detail summary 획득
        summary = await self.conv_summarizer.summarize_conversation(l0_messages, max_length=2048)
        # entity chain + decisions를 후보 1차 풀로 활용
        raw_candidates = []

        # 2-a. explicit_request 기반 후보
        if explicit_user_request:
            raw_candidates.append({
                "content": explicit_user_request,
                "type": "explicit_request",
                "confidence": 0.95,
            })

        # 2-b. 반복 참조 (≥3회) 기반 후보 — entity_chain 활용
        for ent in summary.entity_chain:
            if len(ent["mentions"]) >= 3:
                raw_candidates.append({
                    "content": f"{ent['canonical']} ({ent['label']})",
                    "type": "repeated_mention",
                    "confidence": min(0.5 + 0.1 * len(ent["mentions"]), 0.9),
                })

        # 2-c. 결정/선호 표현 기반 후보 — key_decisions 활용
        for dec in summary.key_decisions:
            raw_candidates.append({
                "content": dec["content"],
                "type": "decision_preference",
                "confidence": 0.85,
            })

        # 2-d. 프로젝트 컨텍스트 (파일 경로, 설정값) 추출
        proj_ctxs = await self._extract_project_context(l0_messages)
        for ctx in proj_ctxs:
            raw_candidates.append({"content": ctx, "type": "project_context", "confidence": 0.80})

        # 3. 증류 규칙 (V1 §2 정합)
        distilled = []
        for raw in raw_candidates:
            # 3-a. 구체적 사실만 보존 (LLM filter: "이 문장은 추측인가?")
            if not await self._is_concrete_fact(raw["content"]):
                continue

            # 3-b. 날짜/시간 절대값 변환 ("어제" → "2026-05-09")
            content = self._normalize_dates(raw["content"], session_date=l0_messages[-1].timestamp)

            # 3-c. 6-2 PII 토큰화 (마스킹이 아닌 토큰화 — 메모리는 복원 가능 토큰)
            content, pii_tokens = pii_masker.tokenize_for_memory(content, ttl_days=90)

            # 3-d. 중복 제거 (semantic dedup: 기존 L1과 cosine 유사도)
            embedding = self.embedder.encode(content)  # BGE-M3 (LOCK-AX-07)
            duplicate = self._find_duplicate(embedding, existing_l1, threshold=0.95)
            if duplicate:
                # 기존 L1 업데이트 (mentions++)
                duplicate.metadata["mentions"] = duplicate.metadata.get("mentions", 0) + 1
                continue  # 새 candidate 미생성

            distilled.append(MemoryCandidate(
                candidate_id=str(uuid.uuid4()),
                content=content,
                candidate_type=raw["type"],
                source_turn_ids=raw.get("source_turn_ids", []),
                confidence=raw["confidence"],
                pii_tokens=pii_tokens,
                metadata={"normalized_dates": True},
            ))

        # 4. confidence 내림차순 + L1 max 5 개 (LOCK-AX-15)
        distilled = [c for c in distilled if c.confidence >= 0.70]  # 승급 게이트 (evaluate_promotion 임계값)
        distilled = [c for c in distilled if c.confidence >= 0.70]  # 승급 게이트 (evaluate_promotion 임계값)
        distilled.sort(key=lambda c: c.confidence, reverse=True)
        return distilled[:5]

    async def evaluate_promotion(self, candidate: MemoryCandidate) -> bool:
        return candidate.confidence >= 0.70  # 임계값

    async def deduplicate(self, candidate, existing_l1):
        emb = self.embedder.encode(candidate.content)
        dup = self._find_duplicate(emb, existing_l1, threshold=0.95)
        return None if dup else candidate
```

### 4.3 E5 — 에러 핸들링

| error_code | 설명 | recoverable | 처리 |
|-----------|------|:-----------:|------|
| `AUX-E-MEM-001` | L1 가득참 (LOCK-AX-15 layer max 도달) | YES | LRU eviction → L2 강등 |
| `AUX-E-MEM-002` | embedding 모델 미로드 | NO | distillation 일시 차단 |
| `AUX-E-MEM-003` | dedup 결과 모두 중복 | YES | distilled=[] 반환, audit |
| `AUX-E-PII-003` | PII 토큰화 실패 (regex 컴파일) | NO | 차단 + 6-2 P1 |
| `AUX-E-MEM-004` | C-12 MEM 호출 실패 | YES | retry 3회 + audit |

### 4.4 E6 — 성능 벤치마크

| 작업 | timeout_policy | P95 | 비고 |
|------|------------|:---:|------|
| conversation_summary 호출 | (위임, conversation_summary §4.4) | 3000 ms | summary 사전 |
| LLM 추측 필터 (raw_candidate × 5) | LLM 추론 (로컬) | 500 ms | _is_concrete_fact |
| 임베딩 (BGE-M3, candidate × 5) | (인-프로세스, GPU) | 100 ms | 1024-dim |
| dedup (cosine vs L1 100 entries × 5) | (인-프로세스) | 50 ms | numpy dot |
| MEM L1 insert (C-12) | VectorStore upsert | 200 ms | timeout_policy §2 #5 |
| **전체 P95** | (복합) | **4000 ms** | L0 100 entries |

### 4.5 E7 — 테스트 시나리오

| # | 시나리오 | 입력 | 예상 |
|---|---------|------|------|
| T-01 | 명시 요청 | "기억해줘: 나는 채식주의자" | candidate.type=explicit_request, confidence=0.95 |
| T-02 | 반복 참조 (3회) | 같은 프로젝트명 3회 언급 | type=repeated_mention |
| T-03 | 결정 표현 | "나는 Python을 선호해" | type=decision_preference |
| T-04 | 프로젝트 컨텍스트 | "src/main.py 수정" | type=project_context |
| T-05 | 추측 (필터) | "아마도 ~일 것 같아" | _is_concrete_fact False, 제외 |
| T-06 | 중복 (semantic dedup) | 기존 L1과 cosine 0.97 | duplicate, mentions++ |
| T-07 | 날짜 정규화 | "어제 회의" | "2026-05-09 회의" |
| T-08 | PII 토큰화 | "내 이메일 foo@bar.com" | content에 PII_TKN_xxx, 90일 TTL |
| T-09 | L1 max 5 (LOCK-AX-15) | distilled 8개 | top 5만 반환 |
| T-10 | C-12 timeout | (mock 30s) | retry 3회 후 AUX-E-MEM-004 |

### 4.6 E9 — 의존성 명세

| 카테고리 | 의존성 |
|---------|--------|
| 외부 라이브러리 | `sentence-transformers` (BGE-M3, LOCK-AX-07) |
| 외부 라이브러리 | `numpy` (cosine sim) |
| 외부 라이브러리 | `python-dateutil` (날짜 정규화) |
| 내부 모듈 | `input_output_schema_v2` (IDistiller), `conversation_summary_v2` | 위임 |
| 외부 모듈 | `MEM` (D2.0-06 VectorStore) | C-12 |
| 횡단 도메인 | `6-2/01_ai-code-security/pii_regex_masking` §2.3 | 토큰화 90일 TTL |

---

## 5. LOCK 교차 검증

| LOCK | AUTHORITY | 본 V2 | 일치 |
|------|---------|-------|:----:|
| LOCK-AX-01 | I-14 CORE | §2 | ✅ |
| LOCK-AX-09 (4-layer) | L0/L1/L2/L3 | §4.1 + §4.2 (L0→L1 승급, L1→L2 강등) | ✅ |
| LOCK-AX-15 (검색 우선순위) | layer max 5 | §4.2 distilled[:5] | ✅ |
| 6-2 §2.3 토큰화 90일 | TTL 90 days | §4.2 step 3-c | ✅ |

---

## 6. V2 종결 marker

★ V2-Phase 2 (2026-05-10, 세션 2-3)
★ V1 byte EXACT
★ LOCK-AX-01/09/15 EXACT 인용
★ E1+E2(승격 평가 + dedup + 토큰화)+E4 ABC+E5+E6+E7+E9 6요소
★ C-12 baseline (I-14 → MEM)
★ 6-2 §2.3 토큰화 90일 TTL 명시
★ LOCK-AX-15 max 5 정합
★ L3: PENDING
