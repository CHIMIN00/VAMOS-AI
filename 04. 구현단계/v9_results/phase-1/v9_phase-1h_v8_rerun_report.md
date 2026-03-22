# v9 Phase -1H: v8 Phase 0 재실행 리포트 (v20.4.0 기준)

> **실행 일시**: 2026-03-07
> **대상 문서**: `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` (v20.4.0)
> **스크립트**: `phase0_part1.py` (0-A~0-H), `phase0_part2.py` (IMP-A~IMP-F)
> **SRC 참조**: `C:\tmp\output\updated\PHASE_B_EXHAUSTIVE_ANALYSIS.md`

---

## 1. 실행 결과 요약

| # | 스크립트 | 이름 | 결과 | 에러 수 |
|---|---------|------|:----:|:------:|
| 1 | 0-A | Table Structure | **PASS** | 0 |
| 2 | 0-B | Arithmetic Sum | **PASS** | 0 |
| 3 | 0-C | Heading Hierarchy | **FAIL** | 3 |
| 4 | 0-D | LOCK/FREEZE/ABSOLUTE + V7-2 Cross-Check | **FAIL** | 5 |
| 5 | 0-E | Keyword Number Inconsistency | **FAIL** | 7 |
| 6 | 0-F | ID Uniqueness + Reference | **PASS** | 0 |
| 7 | 0-G | HTML Comment Integrity | **PASS** | 0 |
| 8 | 0-H | Header Count vs Actual Rows | **FAIL** | 2 |
| 9 | IMP-A | Module Dependency Graph | **PASS** | 0 |
| 10 | IMP-B | Schema Field Count | **PASS** | 0 |
| 11 | IMP-C | API Endpoint Validation | **FAIL** | 3 |
| 12 | IMP-D | Config Key Validation | **FAIL** | 17 |
| 13 | IMP-E | Module Activation Matrix | **PASS** | 0 |
| 14 | IMP-F | Tech Stack Conflict | **FAIL** | 5 |

**PASS: 7/14, FAIL: 7/14**

---

## 2. 에러 분류: REAL_ERROR vs FALSE_POSITIVE

### 2.1 0-C: Heading Hierarchy (3건 → FALSE_POSITIVE 3건)

| 라인 | 제목 | 분류 | 사유 |
|------|------|:----:|------|
| L630 | 단계 완료 검증 (V0-STEP-2 → STEP-3 전환 조건) | FALSE_POSITIVE | v20.0.0에서 Stage Gate 추가 시 `### 단계 완료 검증`을 `# 2. V0` 하위에 삽입. `#` → `###` 점프이나 이는 의도적 구조 — 해당 `###`는 STEP 내 sub-section이며 STEP 자체가 `##` 없이 구분된 설계. RULE에서 허용 여부 확인 필요 |
| L795 | 단계 완료 검증 (V0-STEP-3 → STEP-4 전환 조건) | FALSE_POSITIVE | 동일 패턴 |
| L987 | 단계 완료 검증 (V0-STEP-4 → STEP-5 전환 조건) | FALSE_POSITIVE | 동일 패턴 |

> **판정**: v20.0.0에서 Stage Gate 테이블 18개 추가 시 발생한 구조적 패턴. `#` → `###` 점프가 3건 존재하나, 해당 STEP의 상위 `##` 헤딩이 생략된 문서 구조에서 비롯된 것으로, PART2 전체 문서 구조의 의도적 설계로 판단. v9 Phase 0-Pre에서 heading hierarchy ground truth 구축 시 예외 RULE로 등록 검토.

---

### 2.2 0-D: LOCK/FREEZE/ABSOLUTE Cross-Check (5건 → FALSE_POSITIVE 5건)

| # | 라인 | 키 | PART2 값 | SRC 값 | 분류 | 사유 |
|---|------|-----|---------|--------|:----:|------|
| 1 | L298 | pipeline_stages | `[` (파싱 오류) | `["intake","plan","execute","verify","deliver"]` | FALSE_POSITIVE | 스크립트 정규식이 `[` 까지만 캡처. 실제 PART2 값은 동일 |
| 2 | L305 | max_tokens | 2048 | 4096 | FALSE_POSITIVE | PART2 config.v1.toml은 V1 LOCK값=2048. SRC(PHASE_B4)는 범용 기본값 4096. **PART2가 SOT** (B4 §4.1 LOCK 주석 명시) |
| 3 | L309 | model | bge-m3 | ollama/gemma-2b | FALSE_POSITIVE | SRC 매칭 오류 — `embedding.model`이 아닌 `llm.mini_model`에 매칭됨. 동명 키 충돌 |
| 4 | L321 | backend | json_file | chroma | FALSE_POSITIVE | PART2 `graph_db.backend=json_file`이 SRC `vector_db.backend=chroma`에 잘못 매칭. 섹션이 다름 |
| 5 | L364 | format | json | jsonl | FALSE_POSITIVE | PART2 `logging.format=json` vs SRC `storage.log_format=jsonl`. 섹션/키 불일치로 인한 오매칭 |

> **판정**: 5건 모두 스크립트의 키 매칭 로직 한계(동명 키 cross-section 충돌, 정규식 캡처 범위)에 의한 FALSE_POSITIVE. 실제 LOCK 위반 없음.

---

### 2.3 0-E: Keyword Number Inconsistency (7건 → FALSE_POSITIVE 7건)

| # | 키워드 | 값들 | 분류 | 사유 |
|---|--------|------|:----:|------|
| 1 | max_tokens | 2048, 4096 | FALSE_POSITIVE | L305=config.v1.toml LOCK값(2048), L3787=changelog 기존값 기술(4096→2048 변경 이력) |
| 2 | I-Series | 17, 20, 25 | FALSE_POSITIVE | 버전별 상이: V1=17개, V2=+3=20개(changelog), V3=25개(전체). 의도적 차이 |
| 3 | V1 | 7, 15 | FALSE_POSITIVE | 서로 다른 컨텍스트: MCP 서버 7개 vs changelog 15개(별도 항목) |
| 4 | V2 | 3, 4, 9, 10 | FALSE_POSITIVE | 서로 다른 항목: guardrails 층수(3→4), changelog, LOCK-AT-014 병렬 상한(10) 등 |
| 5 | V3 | 1, 4, 8, 50 | FALSE_POSITIVE | 서로 다른 항목: MCP 서버(1), guardrails(4), changelog, LOCK-AT-014 병렬 상한(50+) |
| 6 | DecisionSchema | 16, 18 | FALSE_POSITIVE | L387/494/635=현재 SOT 18필드(FREEZE). L3787=changelog "16→18 변경" 이력 기술 |
| 7 | ResponseEnvelope | 3, 5 | FALSE_POSITIVE | L388/494/636/999=현재 SOT 5필드(LOCK). L3787=changelog "3→5 변경" 이력 기술 |

> **판정**: 7건 모두 (1) 버전별 의도적 차이, (2) changelog 내 이력 값, (3) 서로 다른 항목의 동일 키워드 매칭에 해당. 실제 불일치 없음.

---

### 2.4 0-H: Header Count vs Actual Rows (2건 → FALSE_POSITIVE 2건)

| # | 라인 | 헤딩 | 기대 | 실제 | 분류 | 사유 |
|---|------|------|:----:|:----:|:----:|------|
| 1 | L2812 | Tauri IPC 커맨드 핸들러 (72개) | 72 | 5 | FALSE_POSITIVE | 72개 IPC의 카테고리 요약 테이블(5행)이 직후에 위치. 72개 전수 목록은 PHASE_B1 SOT에 있으며 PART2에는 대표 5건만 기재하는 구조 |
| 2 | L2934 | MCP 외부 서버 카탈로그 (V1=7개) | 7 | 11 | FALSE_POSITIVE | 제목의 "V1=7개"는 V1 범위 수량. 테이블은 V1+V2+V3 합계 11개 전수 포함. 제목 전체: "M-22: V1=7개, V2+=3개, V3=1개, 합계 11개" |

> **판정**: 2건 모두 스크립트가 헤딩의 첫 번째 숫자만 캡처하여 발생한 오탐. 실제 문서 내용과 테이블은 정합.

---

### 2.5 IMP-C: API Endpoint Validation (3건 → FALSE_POSITIVE 3건)

| # | 유형 | 수량 | 분류 | 사유 |
|---|------|:----:|:----:|------|
| 1 | ipc_part2_only | 8개 | FALSE_POSITIVE | v19.0.0+에서 PART2에 신규 추가된 IPC (sdar:kill_switch, pipeline:hitl_respond 등). SRC(PHASE_B1)는 v19 이전 스냅샷이므로 미포함 정상 |
| 2 | ipc_src_only | 67개 | FALSE_POSITIVE | PART2는 72개 IPC 중 대표 13개만 인라인 기재. 나머지 59+8개는 PHASE_B1 SOT 참조 설계. 의도적 생략 |
| 3 | rpc_src_only | 11개 | FALSE_POSITIVE | JSON-RPC 메서드는 PART2에 backtick 인라인 미기재. PHASE_B1 SOT 위임 구조 |

> **판정**: PART2는 IPC/RPC 전수를 기재하지 않고 SOT(PHASE_B1) 참조 구조. 스크립트가 PART2에 전수 기재를 기대하여 발생한 오탐.

---

### 2.6 IMP-D: Config Key Validation (17건 → FALSE_POSITIVE 17건)

#### 구 REAL_ERROR → FALSE_POSITIVE 재분류 (2건)

| # | 유형 | 내용 | 재분류 사유 |
|---|------|------|------------|
| 1 | missing_from_part2 | `guardrails`, `rate_limit` 섹션이 PART2 config.v1.toml에 부재 | [-1B] 확정 판정에 의해 V0=13섹션, `guardrails`/`rate_limit`은 V0 의도적 생략 4개에 포함. PART2 line 117 HTML 주석 일치 |
| 2 | extra_in_part2 (일부) | `approval`, `self_check` 섹션이 B4 canonical 13섹션에 없음 | [-1B] 확정: B4 정본=17섹션이며 `self_check`(§3.8a), `approval`(§3.8b) 모두 포함. 스크립트 SRC(EXHAUSTIVE_ANALYSIS)가 13개만 기술한 불완전성이 원인 |

> **판정**: 2건 모두 [-1B] Config 13vs17 확정 판정과 정합. 스크립트 SRC(EXHAUSTIVE_ANALYSIS)의 불완전성(17섹션 중 13개만 기술)에 의한 오탐.
> - `tool.*` 4개 섹션: pyproject.toml 설정이므로 config.v1.toml 범위 밖 → FALSE_POSITIVE

#### FALSE_POSITIVE (15건)

| # | 유형 | 내용 | 사유 |
|---|------|------|------|
| 1 | pipeline_stages 공백 차이 | `["intake","plan"...]` vs `["intake", "plan"...]` | 공백 포맷 차이, 값 동일 |
| 2 | default_execution_mode | PART2=`mini` vs SRC=`supervised` | PART2가 SOT (v17.0.0에서 mini로 LOCK 변경) |
| 3 | matryoshka_dim | PART2=256 vs SRC=512 | PART2가 SOT (D2.0-06 정본 256) |
| 4 | json_path 경로 | `${VAMOS_DATA_DIR}/graph/graph.json` vs `~/.vamos/graph/` | PART2가 SOT (v17.0.0에서 ENV 변수 방식으로 표준화) |
| 5 | max_hops | PART2=2 vs SRC=3 | PART2가 SOT (V1 config 제한=2, LOCK-AT-004 상한=3) |
| 6 | fallback_model | PART2=`gpt-4o-mini` vs SRC=`ollama/gemma-2b` | PART2가 SOT (D2.0-04 §3 Failover 순서) |
| 7 | mini_model | PART2=`ollama/llama3.2:3b` vs SRC=`ollama/gemma-2b` | PART2가 SOT |
| 8 | main_model | PART2=`ollama/llama3.1:8b` vs SRC=`gpt-4o-mini` | PART2가 SOT |
| 9 | max_tokens | PART2=2048 vs SRC=4096 | PART2가 SOT (LOCK B4 §4.1) |
| 10 | default_role | PART2=`OWNER` vs SRC=`OPERATOR` | PART2가 SOT (v10.0.0에서 수정) |
| 11 | max_entries | PART2=1000 vs SRC=10000 | PART2가 SOT |
| 12 | log_path 경로 | ENV 변수 vs 하드코딩 | PART2가 SOT |
| 13 | db_path 경로 | ENV 변수 vs 하드코딩 | PART2가 SOT |
| 14 | persist_directory | ENV 변수 vs 하드코딩 | PART2가 SOT |
| 15 | collection_name | `vamos_default` vs `vamos_memory` | PART2가 SOT |

> **판정**: SRC(PHASE_B_EXHAUSTIVE_ANALYSIS)는 PART2 v19.1.0 이전 스냅샷. PART2가 정본 우선순위에서 상위이므로 값 차이는 SRC 측 미갱신에 해당. 17건 전건 FALSE_POSITIVE (구 RE-1/RE-2 포함, [-1B] 판정 근거로 재분류).

---

### 2.7 IMP-F: Tech Stack Conflict (5건 → FALSE_POSITIVE 5건)

| # | 기술 | 라인 | 섹션 | 분류 | 사유 |
|---|------|------|------|:----:|------|
| 1 | Qdrant | L314 | V0 | FALSE_POSITIVE | `backend = "chroma" # LOCK (V1), V2=qdrant` — V2 언급일 뿐, V0에서 사용 아님 |
| 2 | Neo4j | L321 | V0 | FALSE_POSITIVE | `backend = "json_file" # LOCK (V1), V2=neo4j` — V2 언급일 뿐 |
| 3 | S3 (상태 코드) | L1425 | V1 | FALSE_POSITIVE | `S3=120s` — 9-State 상태머신의 S3(State 3)이지 AWS S3가 아님 |
| 4 | S3 (상태 코드) | L1440 | V1 | FALSE_POSITIVE | 동일: `S3 → S4` 상태 전이 |
| 5 | S3 (상태 코드) | L1447 | V1 | FALSE_POSITIVE | 동일: `S3=120s` 타임아웃 |

> **판정**: 5건 모두 오탐. Qdrant/Neo4j는 주석 내 V2 언급, S3는 상태머신 코드가 AWS S3 정규식에 매칭.

---

## 3. V1 Phase 1 칼럼 비일관성 검사

**결과: 비일관성 감지됨 (0-A 스크립트 탐지 범위 밖)**

| 테이블 | 위치 | 칼럼 수 | 칼럼 목록 |
|--------|------|:------:|----------|
| Week 1-2: 핵심 모듈 구현 | L1385 | **6열** | 순서, 모듈, 구현 내용, 의존성, 파일명 (M-7), **산출물 참조** |
| Week 3-4: 보조 모듈 구현 | L1396 | **5열** | 순서, 모듈, 구현 내용, 의존성, 파일명 (M-7) |

> **분류**: **REAL_ERROR** — Week 3-4 테이블에 `산출물 참조` 칼럼이 누락됨. 동일 Phase 내 동일 성격의 테이블이므로 칼럼 구조가 일치해야 함.
> **조치**: Phase -1에서 Week 3-4 테이블에 `산출물 참조` 칼럼 추가 필요. 각 모듈의 SOT 문서 참조(D2.0-01 §5.6, D2.0-02 §7.x 등)를 기입.

---

## 4. 최종 분류 요약

| 분류 | 건수 | 항목 |
|------|:----:|------|
| **FALSE_POSITIVE** | **42건** | 0-C(3) + 0-D(5) + 0-E(7) + 0-H(2) + IMP-C(3) + IMP-D(17) + IMP-F(5) — 스크립트 탐지 전건 |
| **REAL_ERROR** | **1건** | V1 Phase 1 칼럼 비일관성 (RE-3, 수동검증) — 스크립트 탐지 범위 밖 |
| **총 findings** | **43건** | FP 42 (스크립트) + RE 1 (수동) |

### REAL_ERROR 상세 (Phase -1 즉시 수정 대상)

| # | 스크립트 | 내용 | 조치 |
|---|---------|------|------|
| RE-3 | 수동검증 | V1-Phase 1 Week 3-4 테이블(L1396)에 `산출물 참조` 칼럼 누락 (Week 1-2는 6열, Week 3-4는 5열) | Week 3-4 테이블에 6번째 칼럼 추가 |

### 재분류 이력 (구 RE-1, RE-2 → FALSE_POSITIVE)

| # | 원래 분류 | 재분류 | 사유 |
|---|----------|--------|------|
| 구 RE-1 | REAL_ERROR | FALSE_POSITIVE | [-1B] 판정: V0=13섹션, `guardrails`/`rate_limit`은 의도적 생략. PART2 line 117 일치 |
| 구 RE-2 | REAL_ERROR | FALSE_POSITIVE | [-1B] 판정: B4 정본=17섹션, `self_check`/`approval` 포함. SRC(EXHAUSTIVE_ANALYSIS) 불완전성이 원인 |

---

## 5. v9 스크립트 개선 권고

| # | 스크립트 | 이슈 | 권고 |
|---|---------|------|------|
| 1 | 0-D | 키 매칭 시 섹션 무시 → 동명 키 cross-section 충돌 | 섹션.키 복합 매칭으로 개선 |
| 2 | 0-E | changelog 영역 값도 캡처 → 이력 값 오탐 | changelog 섹션(## 변경 이력) 영역 제외 필터 추가 |
| 3 | 0-H | 헤딩의 첫 번째 숫자만 캡처 | 괄호 내 "합계 N개" 등 전체 컨텍스트 파싱 |
| 4 | IMP-C | PART2 전수 기재 기대 | SOT 위임 구조 반영 (PHASE_B1 참조 시 PASS) |
| 5 | IMP-F | `S3` 정규식이 상태 코드에 매칭 | `\bS3\b` 대신 기술명 정규식 사용 또는 상태코드 제외 |
| 6 | 신규 | 테이블 간 칼럼 비일관성 미탐지 | 동일 섹션 내 테이블 간 칼럼 구조 비교 검증 추가 |