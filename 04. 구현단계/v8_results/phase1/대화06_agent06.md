# [Agent 6] 검증 결과 — 메모리 + RAG + 데이터 계층

**검증 일시**: 2026-03-05
**PART2 버전**: v14.0.0 (1933행)
**Phase 0 참조**: 0-D.json (LOCK/FREEZE 80건)

---

## 읽은 파일 (실제 읽은 수 / 할당 수: 6 / 5)

- [x] VAMOS_구현가이드_PART2_구현단계.md (1933행) — 전수 열독 (§2 V0-STEP-5, §3 V1-Phase 2, config.v1.toml, §6.10.2 DCL 포함)
- [x] D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md (2428행 중 ~1200행) — §0~§4.7, S7D 항목 중심 열독
- [x] D2.1-D6_D6_SCHEMA_STORAGE_MEMORY.md (394행) — 전수 열독
- [x] PHASE_B4_CONFIG_SPEC.md (1242행 중 ~550행) — §3 전수 열독 (config 섹션 전체)
- [x] PHASE_B7_MIGRATION_STRATEGY.md (2336행 중 ~300행) — §0~§2 열독 ※ v8 §5 SRC 할당 외 추가 열독 (마이그레이션 교차검증용)
- [x] 0-D.json (571행) — 전수 열독

---

## 검사 통계

- **Dim B** Forward: **15** / MATCH: **8** / MISMATCH: **7** / NO_SOURCE: **0** / Reverse MISSING: **3** (총 **18** 체크)
- **Dim C** Facts checked: **12** / IMP_OK: **5** / IMP_IMPOSSIBLE: **0** / IMP_MISSING: **6** / IMP_CONFLICT: **1**
- **SOURCE_CONFLICT**: **1건**
- 수정 전: BLOCKER **1**건, HIGH **6**건, MEDIUM **8**건 = 총 **15**건
- 수정 후: 미수정 (BLOCKER **1**건 잔여)

---

## 심각도 분류 기준

- **BLOCKER**: LOCK 위반, 구현 차단, 순환 의존, 카운트 오류 ±3 이상
- **HIGH**: 값 오류, 누락 스펙, 카운트 오류 ±2
- **MEDIUM**: 근사/구버전 값, 표기 차이, 출처 오기재
- **LOW**: 서식, 약어 vs 전체명, ±1 근사

---

## Dim B — MISMATCH

| # | PART2:행 | PART2 값 | 원본 값 | 원본 출처 | Severity |
|---|---------|---------|--------|----------|----------|
| 1 | L351 | L0 TTL "session_end, **최대 7일**" (D2.0-06 SOT 채택 주석) | L0 보존 기간 "세션 종료 시 (**최대 30일**)" (§2.1 Summary View) / "세션 종료 **즉시** 만료" (§2.5.3 TTL 정책) | D2.0-06 §2.1 L121 / §2.5.3 L268 | **BLOCKER** — PART2 SOURCE_CONFLICT 주석이 D2.0-06="최대7일"로 인용하나, D2.0-06 실제값=최대30일. 인용 원본 자체가 오기재. 또한 D2.0-06 내부에서도 30일 vs 즉시만료 충돌 |
| 2 | L461-467 | 6-Stage RAG Pipeline: **QUERY_ANALYZE→RETRIEVE→RERANK→CONTEXT_BUILD→GENERATE→VERIFY** | 6-Stage RAG Pipeline: **Collect(수집)→Chunk(쪼개기)→Embed(벡터화)→Store(저장)→Retrieve(검색)→Generate(생성)** | D2.0-06 §1.1 L64-76 | **HIGH** — PART2는 "D2.0-06 §1.1 LOCK" 인용하지만, D2.0-06 정본은 인제스트+검색 파이프라인. PART2 기재는 쿼리 타임 파이프라인으로 단계명 전수 불일치 |
| 3 | L172-176 | [semantic_cache] 키: `semantic_similarity`, `ttl_seconds`, `max_entries`, `invalidation_policy` | [semantic_cache] 키: `enabled`, `similarity_threshold`, `max_entries`, `ttl_sec` | PHASE_B4 §3.15 L537-543 | **HIGH** — PHASE_B4=config SOT. 키 이름 3개 불일치: semantic_similarity↔similarity_threshold, ttl_seconds↔ttl_sec, invalidation_policy 미존재(PHASE_B4), enabled 미존재(PART2). ※ v8 B#12 (Semantic Cache 무효화 정책) 포함 |
| 4 | L178-183 | 메모리 TTL을 **[memory]** 섹션에 배치 (ttl_L0_session, ttl_L1_project 등) | 메모리 TTL을 **[storage]** 섹션에 배치 (memory_ttl_L0, memory_ttl_L1 등) | PHASE_B4 §3.6 L249-252 | **HIGH** — PHASE_B4=config SOT. 섹션 이름([memory] vs [storage])과 키 이름(ttl_L0_session vs memory_ttl_L0) 모두 불일치 |
| 5 | L159-162 | [graph_db] 키: `backend`, `max_entities=10000`, `relation_types`, `pruning_strategy`, `pruning_threshold` | [graph_db] 키: `backend`, `json_path`, `max_hops=2`, `scope`, `cache_enabled` | PHASE_B4 §3.5 L220-236 | **HIGH** — [graph_db] 섹션의 키 구성 전수 불일치. max_entities, relation_types, pruning 관련 키는 PHASE_B4에 존재하지 않음. 반대로 json_path, max_hops, scope는 PART2에 미존재 |
| 6 | L166-170 | [vector_db] 키: `backend`, `collection_prefix="vamos_"`, `embedding_model`, `distance_metric` | [vector_db] 키: `backend`, `mode`, `collection_name="vamos_default"`, `persist_directory`, `similarity_metric` | PHASE_B4 §3.4 L200-217 | **HIGH** — collection_prefix↔collection_name 불일치, embedding_model(PART2) vs 미존재(B4), mode/persist_directory(B4) vs 미존재(PART2) |
| 7 | L172 주석 | "[semantic_cache] (PHASE_B4 **§3.13** 정본)" | [semantic_cache]는 PHASE_B4 **§3.15** (§3.13=[blue_nodes]) | PHASE_B4 §3.13/§3.15 | **MEDIUM** — 출처 섹션 번호 오기재 (§3.13→§3.15) |

---

## Dim B — NO_SOURCE

| # | PART2:행 | PART2 내용 | 검색한 파일/패턴 | 판정 |
|---|---------|-----------|---------------|------|
| (해당 없음) | | | | |

---

## Dim B — MISSING

| # | 구분 | 원본 출처 | 누락 내용 | Severity |
|---|------|----------|---------|----------|
| 1 | 역방향 | D2.0-06 §2.2-A L172-184 | **VectorStore 어댑터 인터페이스 최소 계약** (upsert, search top_k=10, delete, get_by_id) — PART2 V1-Phase 2에 VectorStore 추상 인터페이스 구현 항목 부재 | **HIGH** |
| 2 | 역방향 | D2.0-06 §2.5.2 L261-262 | **QoD < 0.4 저장 금지 규칙** — PART2 V1-Phase 2에 QoD 임계값 기반 저장 제한 규칙 미반영 | **MEDIUM** |
| 3 | 역방향 | D2.0-06 §4.1 L646-649 | **RAG 재시도 정책** (max_retry=3, 1차:BM25 폴백→2차:캐시 폴백→3차:포기+경고) — PART2에 RAG 실패 시 폴백 체인 미반영 | **MEDIUM** |

---

## Dim B — SOURCE_CONFLICT

| # | 출처A=값 | 출처B=값 | 정본 우선순위 판정 |
|---|---------|---------|------------------|
| 1 | D2.0-06 §2.1 L121="L0 최대 **30일**" | D2.0-06 §2.5.3 L268="세션 종료 **즉시** 만료" / S02-P30-MOD-004 L301="+7일 연장" | D2.0-06 내부 충돌. §2.5.3 TTL 정책 테이블이 더 구체적이므로 "즉시 만료"가 정본으로 적합. +7일은 MOD 항목(선택적 연장). 30일은 Summary View의 오래된 값으로 판단. **PART2가 "7일"로 채택한 것은 타당하나, D2.0-06 §2.1 인용은 부정확 → D2.0-06 수정 필요** |

---

## Dim C — IMP_IMPOSSIBLE

| # | PART2:행 | 명세 내용 | 불가 사유 | 대안 제안 | Severity |
|---|---------|---------|---------|---------|----------|
| (해당 없음) | | | | | |

---

## Dim C — IMP_MISSING

| # | PART2:행 | 명세 내용 | 부족 정보 | Severity |
|---|---------|---------|---------|----------|
| 1 | L350-351 | L0 TTL "session_end" SQLite 구현 | **session_end 3조건** 미정의: (1) 명시적 로그아웃/세션 종료 (2) 비활성 타임아웃 (몇 분?) (3) 앱 종료/크래시. SQLite에서 세션 종료 감지 메커니즘 미명시. Python 프로세스 종료 시 atexit handler? Tauri window close 이벤트? | **HIGH** |
| 2 | L461-467 | 6-Stage RAG Pipeline — LangGraph vs 함수 체인 | D2.0-06 §1.1 인제스트 파이프라인과 PART2 쿼리 파이프라인이 **별도 파이프라인임에도 동일 "6-Stage"로 표기**. 각각의 구현 방식(LangGraph 노드 vs 순차 함수 체인) 미명시. 또한 인제스트 파이프라인이 PART2 V1-Phase 2에 **명시적으로 부재** | **HIGH** |
| 3 | L469-477 | BM25 인덱스 저장 | V1에서 BM25 인덱스 저장 위치(인메모리/SQLite/파일) 미명시. 앱 재시작 시 BM25 인덱스 재구축 필요 여부 불명. D2.0-06 S7D-012는 BM25 구현만 언급하고 영속 저장 미명시 | **MEDIUM** |
| 4 | L444-445 | Chroma 1024dim + JSON GraphRAG 10000 엔티티 | V1 로컬 환경에서 (1) Chroma 1024dim 인덱스의 RAM 영향 분석 부재 (~40MB/10K vectors, 관리 가능하나 명시 필요) (2) NetworkX JSON 10000 노드+50000 엣지 직렬화/로딩 시간 미분석 (JSON ~50MB 예상, 시작 시 전체 로드 필요) | **MEDIUM** |
| 5 | L482-483 | Embedding Drift 캐시 무효화 (cosine 차이 > 0.05) | 원본 문서 재임베딩 시 이전 임베딩과 비교하여 drift 감지하는 **구체적 구현 방법** 미명시. 이전 임베딩 저장 필요. 언제 재임베딩 트리거? 모델 변경 시? 정기적? | **MEDIUM** |
| 6 | L450-451 | DCL RSS→RAG 삽입 (DCL-FIN RT-BNP RSS + DCL-TECH RSS 1시간) | DCL 자동 수집 콘텐츠가 **RAG 문서 상한 (15개/project)과 충돌** 가능. RSS 피드는 지속적으로 새 문서를 생성하므로 상한 관리 정책 필요. 또한 DCL 수집 문서의 QoD 기본값, 자동 만료(TTL) 정책 미명시 | **MEDIUM** |

---

## Dim C — IMP_CONFLICT

| # | 출처A:행:값 | 출처B:행:값 | 충돌 내용 | 판정 |
|---|-----------|-----------|---------|------|
| 1 | D2.0-06 §4.7.2 L749: Semantic Cache 기본 TTL=**86400초(24시간)** | PHASE_B4 §3.15 L542: ttl_sec=**3600초(1시간)** / PART2 L174: ttl_seconds=**3600** | D2.0-06 설계값(24h)과 PHASE_B4 config 구현값(1h)이 24배 차이. D2.0-06은 MOD-017 (LOCK 미표기)이므로 PHASE_B4가 config SOT로서 V1 값을 3600으로 재정의할 수 있으나, **설계 의도와의 큰 괴리를 주석으로 명시해야 함**. PART2도 PHASE_B4와 일치하므로 config 관점에서는 정합하나, D2.1-D6 SemanticCacheSchema (L194: ttl_sec=86400)와도 불일치 | PART2/PHASE_B4=3600 유지 가능. 단, SOURCE_CONFLICT 주석 추가 권장 |

---

## Phase 0 교차 참조

| # | 0-D.json 항목 | PART2 값 | 0-D.json 값 | 판정 |
|---|--------------|---------|------------|------|
| 1 | 메모리 4계층 L0-L3 (LOCK) | L0 Session / L1 Project / L2 Long-term / L3 Procedural | 4계층 LOCK | ✅ MATCH |
| 2 | B→L 매핑 (LOCK) | B-1/L1, B-2/L3, B-3/L2, B-4/L0 | 동일 매핑 LOCK | ✅ MATCH |
| 3 | 6-Stage RAG Pipeline (LOCK) | QUERY_ANALYZE→...→VERIFY | Collect→...→Generate | ⚠️ MISMATCH (MISMATCH #2) |
| 4 | Hybrid Search α (LOCK) | Dense=0.7 / Sparse(BM25)=0.3 | alpha=0.3 (BM25 가중치) | ✅ MATCH |
| 5 | Semantic Cache cosine ≥ 0.95 (LOCK) | ≥ 0.95 | cosine_similarity ≥ 0.95 | ✅ MATCH |

---

## Dim B — MATCH 확인

| # | v8 B# | 검증 항목 | PART2 값 | 원본 값 | 원본 출처 | 판정 |
|---|-------|----------|---------|--------|----------|------|
| 1 | B#1 | 메모리 L0~L3 4계층 | L0 Session / L1 Project / L2 Long-term / L3 Procedural | 동일 4계층 (L0~L3), 4계층 LOCK | D2.0-06 §2 L80-101 | **MATCH** |
| 2 | B#3 | B→L 매핑 | B-1/L1, B-2/L3, B-3/L2, B-4/L0 | 동일 매핑 (LOCK) | D2.0-06 §2.1 L109-115 | **MATCH** |
| 3 | B#5 | B-3 Decay vs Deep Reflection | V1-Phase 2: "메모리 B-3 Decay: TTL 기반 자동 만료" + SOURCE_CONFLICT 주석 (§5.10 LOCK 채택) | B-3 = Semantic. "B-3 Decay"는 D2.0-01 §5.10 명칭, D2.0-06에서는 "Semantic"으로 정의 | D2.0-06 §2.1 L107 / D2.0-01 §5.10 | **MATCH** (SOURCE_CONFLICT 주석 적절, §5.10 LOCK 채택 타당) |
| 4 | B#7 | Hybrid Search α | Dense=0.7 / Sparse(BM25)=0.3 (LOCK Y) | alpha=0.3 (BM25), 즉 Vector=0.7 | D2.0-06 S7D-012 L778, S7D-034 L1097 | **MATCH** (α 기호 부여 대상이 다르나 실제 가중치 동일) |
| 5 | B#8 | 임베딩 BGE-M3 1024dim + Matryoshka 256dim | config: model=bge-m3, dimension=1024, matryoshka_dim=256 | BGE-M3 1024차원, 256차원 Matryoshka | D2.0-06 §2.2 L146 / PHASE_B4 §3.3 L185-187 | **MATCH** |
| 6 | B#9 | SQLite→PostgreSQL 마이그레이션 | V2 마이그레이션 항목 포함 | V1=SQLite → V2=Postgres (메타/인덱스) | PHASE_B7 §1.1 L27 | **MATCH** |
| 7 | B#10 | Vector/Graph DB V2+ | V2=Qdrant(서버), V3=Qdrant Cloud | V1=Chroma → V2=Qdrant(서버) → V3=Qdrant Cloud | PHASE_B7 §1.1 L29 | **MATCH** |
| 8 | B#11 | Semantic Cache cosine | ≥ 0.95 LOCK | cosine_similarity ≥ 0.95 (LOCK) | D2.0-06 §4.7.1 L744 / D2.1-D6 L192-193 | **MATCH** |

> **B#12 (Semantic Cache 무효화 정책)**: MISMATCH #3에 포함 — [semantic_cache] `invalidation_policy` 키가 PHASE_B4 SOT에 미존재.

---

## 임베딩 라이브러리 참고 사항

| 항목 | D2.0-06 기재 | 실제/권장 | 비고 |
|------|------------|---------|------|
| BGE-M3 라이브러리 | `sentence-transformers` (S7D-027 L772) | **FlagEmbedding** (BAAI 공식 라이브러리, `pip install FlagEmbedding`) | D2.0-06 오류. bge-m3는 BAAI/FlagEmbedding이 정식. sentence-transformers도 호환 가능하나 공식 아님. PART2는 라이브러리명을 명시하지 않아 직접 충돌은 없음. **D2.0-06 수정 권장** |

---

## 종합 판정

### BLOCKER (1건)

| # | 유형 | 항목 | 내용 |
|---|------|------|------|
| BLK-1 | MISMATCH | L0 TTL "최대 7일" 인용 오류 | PART2 SOURCE_CONFLICT 주석에서 D2.0-06 §2.1을 "최대7일"로 인용하나, D2.0-06 §2.1 실제값은 "최대30일". D2.0-06 내부에서도 §2.1(30일) vs §2.5.3(즉시만료) 충돌. → D2.0-06 내부 정합 수정 필요 + PART2 인용 근거 정정 필요 |

### HIGH (6건)

| # | 유형 | 항목 | 내용 |
|---|------|------|------|
| H-1 | MISMATCH | 6-Stage RAG Pipeline 단계명 전수 불일치 | D2.0-06 인제스트 파이프라인(Collect→...→Generate) vs PART2 쿼리 파이프라인(QUERY_ANALYZE→...→VERIFY). 동일 "6-Stage" 표기이나 완전히 다른 파이프라인 |
| H-2 | MISMATCH | [semantic_cache] config 키 이름 3개 불일치 | PHASE_B4 SOT: enabled, similarity_threshold, ttl_sec. PART2: semantic_similarity, ttl_seconds, invalidation_policy |
| H-3 | MISMATCH | [memory] vs [storage] 섹션 + 키 이름 불일치 | PHASE_B4=[storage], PART2=[memory]. 키 이름도 memory_ttl_L0 vs ttl_L0_session |
| H-4 | MISMATCH | [graph_db] config 키 구성 전수 불일치 | PART2: max_entities, relation_types, pruning. PHASE_B4: json_path, max_hops, scope. 공통 키 backend만 일치 |
| H-5 | MISMATCH | [vector_db] config 키 불일치 | collection_prefix vs collection_name, embedding_model vs 미존재, mode/persist_directory vs 미존재 |
| H-6 | MISSING | VectorStore 어댑터 인터페이스 누락 | D2.0-06 §2.2-A LOCK(upsert, search, delete, get_by_id). PART2 V1-Phase 2에 구현 항목 부재 |

### MEDIUM (8건)

| # | 유형 | 항목 | 내용 |
|---|------|------|------|
| M-1 | MISMATCH | [semantic_cache] 섹션 번호 오기재 | PART2: §3.13 → 실제: §3.15 |
| M-2 | MISSING | QoD < 0.4 저장 금지 규칙 | D2.0-06 §2.5.2 LOCK. PART2 미반영 |
| M-3 | MISSING | RAG 재시도 정책 | D2.0-06 §4.1 max_retry=3 폴백 체인. PART2 미반영 |
| M-4 | IMP_CONFLICT | Semantic Cache TTL 설계 vs 구현 괴리 | D2.0-06=86400초(24h), PHASE_B4/PART2=3600초(1h). 24배 차이. SOURCE_CONFLICT 주석 부재 |
| M-5 | IMP_MISSING | BM25 인덱스 저장 위치 미명시 | 인메모리/SQLite/파일 선택 미정의. 앱 재시작 시 재구축 필요 여부 불명 |
| M-6 | IMP_MISSING | Chroma 1024dim + GraphRAG 10000 엔티티 RAM 영향 | ~40MB/10K vectors + ~50MB JSON. V1 로컬 환경 리소스 분석 부재 |
| M-7 | IMP_MISSING | Embedding Drift 캐시 무효화 구현 | cosine 차이 > 0.05 감지 시 이전 임베딩 저장/비교 방법, 재임베딩 트리거 조건 미명시 |
| M-8 | IMP_MISSING | DCL RSS→RAG 삽입 상한 충돌 | RSS 자동 수집이 RAG 문서 상한(15개/project)과 충돌 가능. 상한 관리 정책, QoD 기본값, TTL 미명시 |

---

## 검증 완료 선언

- 수정 전: BLOCKER **1**건, HIGH **6**건, MEDIUM **8**건 = 총 **15**건 (SOURCE_CONFLICT **1**건은 severity에 포함)
- 수정 후: 미수정 (BLOCKER **1**건 잔여)
- Dim B: Forward **15** + Reverse **3** = **18** 체크 — MATCH **8**, MISMATCH **7**, NO_SOURCE **0**, MISSING **3**
- Dim C: **12**항목 — IMP_OK **5**, IMP_MISSING **6**, IMP_CONFLICT **1**, IMP_IMPOSSIBLE **0**
- ⚠️ **BLOCKER 1건 미해소** — L0 TTL 인용 오류 (D2.0-06 내부 정합 수정 + PART2 인용 정정 필요). Phase 2에서 수정 필요.
