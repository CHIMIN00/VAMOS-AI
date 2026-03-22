# Phase 2-B 재검증 보고서 (Phase 0 전수 재실행)

> **대상 문서**: `VAMOS_구현가이드_PART2_구현단계.md` v19.0.0 -> v19.1.0
> **재실행 기준**: Phase 2-A Ripple Fix 완료 후 (대화15_phase2a_ripple_fix.md)
> **수행일**: 2026-03-06
> **수행자**: Phase 2-B Revalidator (v8.1 Pipeline)

---

## STEP 3: Phase 0 전수 재실행

### 1차 실행 (v19.0.0)

| Script | Name | Verdict | Errors | 판정 |
|--------|------|---------|--------|------|
| **0-A** | Table Structure | **FAIL** | 1 | **REAL_ERROR**: line 2084 RT-BNP 행 5열 vs 헤더 4열 |
| **0-B** | Arithmetic Sum | PASS | 0 | - |
| **0-C** | Heading Hierarchy | PASS | 0 | - |
| **0-D** | LOCK/FREEZE/ABSOLUTE + V7-2 Cross-Check | FAIL | 5 | FALSE_POSITIVE: 부분 키 매칭으로 다른 섹션 키끼리 교차 비교 (예: embedding.model vs llm.mini_model) |
| **0-E** | Keyword Inconsistency | FAIL | 7 | FALSE_POSITIVE: changelog 섹션 내 과거 버전 값과 현재 값 컨텍스트 차이 |
| **0-F** | ID Uniqueness | PASS | 0 | - |
| **0-G** | HTML Comment Integrity | PASS | 0 | - |
| **0-H** | Header Count vs Rows | FAIL | 2 | FALSE_POSITIVE: 요약 테이블(72개->5행 카테고리), MCP 합계(V1=7개 vs 전체 11행) |
| **IMP-A** | Module Dependency Graph | PASS | 0 | v13.0.0에서 I-10/I-11 순환 해소 완료 |
| **IMP-B** | Schema Field Count | PASS | 0 | v9.0.0에서 DecisionSchema 18 수정 완료 |
| **IMP-C** | API Endpoint | FAIL | 3 | FALSE_POSITIVE: PART2 약칭 vs SRC 전체 열거 구조적 차이 |
| **IMP-D** | Config Key + Canonical Section | FAIL | 17 | FALSE_POSITIVE: V0 의도적 설정 차이, 경로 규약 차이(${VAMOS_DATA_DIR} vs ~/.vamos/), pyproject.toml 섹션 혼입 |
| **IMP-E** | Module Activation Matrix | PASS | 0 | V0=5/V1=32/V2=42/V3=81 전수 통과 |
| **IMP-F** | Tech Stack Conflict | FAIL | 3 | FALSE_POSITIVE: 인라인 주석(V2=qdrant/neo4j), 상태명 S3 오인식(Amazon S3 아님) |

**1차 결과**: PASS 7 / FAIL 7 (REAL_ERROR 1건, FALSE_POSITIVE 6건)

### 1차 수정 내역

| # | 위치 | 수정 내용 | 정본 근거 |
|---|------|----------|----------|
| 1 | line 2084 | RT-BNP 행 5열->4열: 참조(`VAMOS_CLOUD_LIBRARY_SPEC, §6.10.1`)를 구현 내용 셀 말미로 병합 | 테이블 구조 일관성 (헤더 4열 기준) |

### 2차 실행 (v19.1.0)

| Script | Name | Verdict | Errors | 판정 |
|--------|------|---------|--------|------|
| **0-A** | Table Structure | **PASS** | 0 | 1차 수정으로 해소 |
| **0-B** | Arithmetic Sum | PASS | 0 | - |
| **0-C** | Heading Hierarchy | PASS | 0 | - |
| **0-D** | LOCK/FREEZE/ABSOLUTE + V7-2 Cross-Check | FAIL | 5 | FALSE_POSITIVE (변동 없음) |
| **0-E** | Keyword Inconsistency | FAIL | 7 | FALSE_POSITIVE (변동 없음) |
| **0-F** | ID Uniqueness | PASS | 0 | - |
| **0-G** | HTML Comment Integrity | PASS | 0 | - |
| **0-H** | Header Count vs Rows | FAIL | 2 | FALSE_POSITIVE (변동 없음) |
| **IMP-A** | Module Dependency Graph | PASS | 0 | - |
| **IMP-B** | Schema Field Count | PASS | 0 | - |
| **IMP-C** | API Endpoint | FAIL | 3 | FALSE_POSITIVE (변동 없음) |
| **IMP-D** | Config Key + Canonical Section | FAIL | 17 | FALSE_POSITIVE (변동 없음) |
| **IMP-E** | Module Activation Matrix | PASS | 0 | - |
| **IMP-F** | Tech Stack Conflict | FAIL | 3 | FALSE_POSITIVE (변동 없음) |

**2차 결과**: PASS 8 / FAIL 6 (REAL_ERROR 0건, FALSE_POSITIVE 6건)

### 3차 실행: 불필요

REAL_ERROR 0건이므로 추가 수정/재실행 없이 종료.

---

## FALSE_POSITIVE 상세 분류 (6건)

### 0-D (5 errors): 부분 키 매칭 오류

스크립트가 `entry["key"] in sk` 조건으로 부분 문자열 매칭하여 서로 다른 config 섹션의 키를 교차 비교함.

| PART2 키 | PART2 값 | 매칭된 SRC 키 | SRC 값 | 사유 |
|----------|----------|-------------|--------|------|
| pipeline_stages | (array) | core.pipeline_stages | (array) | 공백 차이만 (의미 동일) |
| max_tokens | 2048 | llm.max_tokens | 4096 | V0=2048(B4 §4.1 반영), V1+=4096 |
| model (embedding) | bge-m3 | llm.mini_model | ollama/gemma-2b | 다른 섹션 키 오매칭 |
| backend (graph_db) | json_file | vector_db.backend | chroma | 다른 섹션 키 오매칭 |
| format (logging) | json | storage.log_format | jsonl | 다른 섹션 키 오매칭 |

### 0-E (7 errors): Changelog 컨텍스트 차이

모든 불일치가 changelog(line 3458~3479) 내 과거 버전 참조 값과 현재 본문 값 사이에서 발생. 컨텍스트가 다른 정상적 차이.

| Keyword | 현재값 | Changelog값 | 설명 |
|---------|--------|------------|------|
| max_tokens | 2048 (V0 config) | 4096 (v8.2.0 수정 전 값) | 버전별 변경 이력 |
| I-Series | 25 (현재) | 20 (v9.0.0 수정 전) | 모듈 수 확장 이력 |
| V1/V2/V3 | 다수 | 다수 | GO/NO-GO/Agent/비용 등 다른 맥락 |
| DecisionSchema | 18 (현재) | 16 (v9.0.0 수정 전) | 필드 수 변경 이력 |
| ResponseEnvelope | 5 (현재) | 3 (v8.2.0 수정 전) | 필드 수 변경 이력 |

### 0-H (2 errors): 요약 테이블

| 헤딩 | 숫자 | 실제 행 | 설명 |
|------|------|--------|------|
| 6.2.1 Tauri IPC (72개) | 72 | 5 | 72개 IPC의 카테고리별 5행 요약 테이블 |
| MCP (V1=7개) | 7 | 11 | V1=7/V2+=3/V3=1, 합계=11행 전체 표기 |

### IMP-C (3 errors): 구조적 차이

PART2 §6.2는 IPC 약칭/예시(8개), SRC는 전체 72개 개별 열거. JSON-RPC도 동일 패턴. 데이터 오류 아닌 표현 방식 차이.

### IMP-D (17 errors): V0 의도적 차이

| 분류 | 건수 | 설명 |
|------|------|------|
| 값 불일치 (V0 vs B4 기본) | 11 | V0 config는 로컬/경량 설정(mini_model=llama3.2, max_tokens=2048 등), B4는 V1 기본값 |
| 경로 규약 차이 | 3 | `${VAMOS_DATA_DIR}/...` (PART2) vs `~/.vamos/...` (B4) |
| 섹션 불일치 | 2 | pyproject.toml 섹션(tool.mypy 등) 혼입 + approval/self_check은 V16 분리 결과 |
| 공백 차이 | 1 | pipeline_stages 배열 포맷팅 |

### IMP-F (3 errors): 오인식

| Tech | 위치 | 실제 내용 | 사유 |
|------|------|----------|------|
| Qdrant | V0 line 314 | `backend = "chroma" # LOCK (V1), V2=qdrant` | 인라인 주석에서 V2 예고 |
| Neo4j | V0 line 321 | `backend = "json_file" # LOCK (V1), V2=neo4j` | 인라인 주석에서 V2 예고 |
| S3 | V1 line 1325 | `S3=120s` (상태 머신 S3 타임아웃) | Amazon S3 아닌 State S3 |

---

## STEP 4: 버전업 + Changelog

### 변경 사항

| 항목 | Before | After |
|------|--------|-------|
| 헤더 버전 | v19.0.0 | v19.1.0 |
| 정본 근거 | 8차 V2/V3 실행 가이드 추가 | +9차 Phase 2-A Ripple Fix 11건+Phase 2-B 재검증 1건 |
| Changelog | v19.0.0 행까지 | +v19.1.0 행 추가 |
| 최종갱신일 | 2026-03-06 (유지) | 2026-03-06 (동일) |

### Changelog 추가 내용 (v19.1.0)

Phase 2-B 재검증(Phase 0 전수 재실행): **수정 1건** - V3-Phase 2 EXP 모듈 테이블 line 2084 RT-BNP 행 열 수 불일치 해소(5열->4열, 참조를 구현 내용 셀로 병합). Phase 0 14개 스크립트 2차 실행 결과: PASS 8/FAIL 6, 잔여 FAIL 6건 전수 FALSE_POSITIVE 판정.

---

## 미해결 항목 목록

### PART2 외 대상 (Phase 2-A에서 이월)

| # | 대상 | 설명 | 비고 |
|---|------|------|------|
| C-3 | CLAUDE.md | SDAR 명칭 미반영 | Phase 2-B CLAUDE.md 수정 시 |
| C-4 | CLAUDE.md | L0 TTL 미반영 | Phase 2-B CLAUDE.md 수정 시 |
| H-B6 | CLAUDE.md | approval_status 불일치 | Phase 2-B CLAUDE.md 수정 시 |
| P2 #28 | PHASE_B6 | Rust nightly -> stable | PHASE_B 개별 수정 |
| P2 #29 | PHASE_B1 | IPC 47 -> 72 정정 | PHASE_B 개별 수정 |

### SOURCE_CONFLICT (수정 제외, HTML 주석 기록 완료)

| ID | PART2 값 | SRC 값 |
|----|----------|--------|
| SC-01 | CL-G1 "Trust Score" | CLOUD_LIBRARY_SPEC §8 "Content Quality" |
| SC-02 | CL-G2 "Relevance" | CLOUD_LIBRARY_SPEC §8 "Consistency" |

### 스크립트 개선 권고 (선택)

| Script | 권고 | 사유 |
|--------|------|------|
| 0-D | 정확한 `section.key` 매칭으로 교체 | 부분 문자열 매칭이 false positive 유발 |
| 0-E | changelog 섹션(변경 이력) 라인 범위 제외 | 과거 값과 현재 값 혼동 |
| 0-H | 요약 테이블 감지 로직 추가 | 카테고리별 요약행 vs 개별 항목행 구분 |
| IMP-F | 코드 주석(`#`) 내 tech 키워드 제외 | 인라인 주석의 V2 예고 문구 오탐 |
| IMP-F | State Machine `S\d+` 패턴 제외 | S3(상태) vs S3(Amazon) 오인식 |

---

## 최종 결론

| 항목 | 값 |
|------|-----|
| Phase 0 전수 재실행 | 2회 (1차: REAL_ERROR 발견+수정, 2차: REAL_ERROR 0건) |
| 총 수정 건수 | 1건 (테이블 열 수 정정) |
| REAL_ERROR 잔존 | **0건** |
| FALSE_POSITIVE | 6건 (스크립트 한계, 미수정) |
| PART2 최종 버전 | **v19.1.0** |
| 미해결 (PART2 외) | 5건 (CLAUDE.md 3건 + PHASE_B 2건) |
| SOURCE_CONFLICT | 2건 (HTML 주석 기록 완료) |

**Phase 2-B 판정: PASS** - PART2 문서 내 REAL_ERROR 전수 해소 완료.
