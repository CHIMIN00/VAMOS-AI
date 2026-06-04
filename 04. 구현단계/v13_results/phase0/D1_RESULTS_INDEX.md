# D1 검증 결과 인덱스 (Phase 1 — D1 PASS_CONDITIONAL)

> **판정일**: 2026-06-04 · **판정**: **D1 PASS (CONDITIONAL)** · **엔진**: `_d1/` 결정론 스크립트(동일 입력=동일 출력)
> **정본 우선순위**: RULE > PLAN > DESIGN LOCK · **원칙**: 자동 정본 변경 0 · 보고서 ✅ ≠ 산출물 존재(R16) 전수 디스크 검증
> **머신 판정서**: [D1_VERDICT.json](D1_VERDICT.json)

---

## 1. Must 게이트 결과 (값 게이트 5/5 PASS)

| 게이트 | 지표 | 값 | 목표 | 판정 | 산출물(실경로) |
|--------|------|----|------|:----:|----------------|
| **1-2** SOT 내부 정합 | active CONFLICT | **0** (14건 발견·전부 RESOLVED) | 0 | ✅ | [sot_conflict_report.json](sot_conflict_report.json) |
| **1-3** SOT↔SOT2 교차 | MISMATCH | **0** | 0 | ✅ | [sot2_conflict_scan.json](../../../docs/sot%202/_cross-ref/sot2_conflict_scan.json) · alias `sot2_crossref_report.json` |
| **1-4** SOT2 내부 교차 | LOCK MISMATCH | **0** | 0 | ✅ | [cross_ref_matrix.md](../../../docs/sot%202/_cross-ref/cross_ref_matrix.md) · [lock_consistency.md](../../../docs/sot%202/_cross-ref/lock_consistency.md) · [broken_references.md](../../../docs/sot%202/_cross-ref/broken_references.md) · `sot2_internal_report.json` · `{도메인}.json ×36` |
| **1-4** 깨진 참조(설계) | BROKEN | **1** (사소·네비) | 0 | ⚠️ 이연 | broken_references.json (EXTERNAL 6 제외) |
| **1-5** 구조+LOCK 검증 | SDV-1 critical FAIL | **0** (36/36 AUTHORITY+CONFLICT 존재) | 0 | ✅ | [_sot2_validate_summary.json](../../../docs/sot%202/_extractions/validation/_sot2_validate_summary.json) · `{도메인}_validation.json ×36` |
| **1-5** LOCK 게이트 | SDV-4 LOCK WARN/FAIL | **2** (5-3, 6-5 비차단 이연) | 0 | ⚠️ 이연 | 동상 · alias `sot2_validate_report.json` |
| **1-5** Part2 라인참조 | SDV-7 out-of-range | **0** | 0 | ✅ | 동상 |
| **1-9** 기준선 저장 | snapshot 파일 수 | **2,654** | >0 | ✅ | [integrity_snapshot.json](integrity/integrity_snapshot.json) |

**값 게이트(1-2 CONFLICT · 1-3 MISMATCH · 1-4 LOCK MISMATCH · 1-5 SDV-1 critical/SDV-4 값충돌 · 1-9 snapshot) 전수 PASS.**
SDV-4 WARN 2 + BROKEN 1 은 **LOCK 값 충돌이 아닌** 사전 존재·소유자 문서화 비차단 이연(§3 이연대장).

## 2. Should/조건부 (D1 PASS 비차단 — 후속 Phase 입력)

| # | 항목 | 결과 | 산출물 | 용도 |
|---|------|------|--------|------|
| 1-6 | CLAUDE.md GAP (method-c) | 12개 핵심 사실 중 10 PRESENT / **GAP 2** (HYBRID_RATIO, MAX_RETRIES) | [claude_md_gap_report.json](extraction/sot_check/claude_md_gap_report.json) · `CLAUDE_md_sot_check.json` | Phase 2-1 CLAUDE.md 보강 입력 |
| 1-7 | Obsidian 정합 | 36 도메인 중 35 참조 / **미참조 1** | [obsidian_gap_report.json](extraction/sot_check/obsidian_gap_report.json) | Phase 2-3 Obsidian 노트 입력 |
| 1-8 | BLOCKER 재확인 | PART1 BLOCKER **14건** baseline 기록 / **변경 0** | [blocker_log.json](extraction/sot_check/blocker_log.json) | 변경 시 1-2~1-5 재실행 트리거 |
| 1-9 | /integrity all | SOT68 = **67 OK / 1 CHANGED** (review 문서) | [v13_integrity_check_20260604T233844.json](integrity/v13_integrity_check_20260604T233844.json) | D2 상시 감시 |

## 3. 이연 대장 (Deferral Register — 누락 0, 자동 정본 변경 0)

> 전 항목 **LOCK 값 충돌 아님 · 비차단(non-blocking) · 소유자 문서화**. D1_VERDICT.json `deferral_register` 동기화.

| # | 항목 | 유형 | 상태 / 근거 | 책임 Phase |
|---|------|------|------------|:----------:|
| D-1 | **5-3 C-04~C-08** (5건) | LOCK-V12 상속/출처 매핑 불일치 | OPEN · 2026-04-03부터 '게이트 영향 없음/4-2 선례' (CONFLICT_LOG) | Phase 2/3 협의 |
| D-2 | **6-5 W-CB** (1건) | Circuit Breaker 소유권 미확정 | OPEN · `DEFERRED_TO_PHASE3 OBSERVE_ONLY` 마커 | Phase 3 (6-2 협의) |
| D-3 | **2-2 `04_cat-d-media/_index.md → ../_index.md`** | 깨진 네비 링크 | BROKEN · 도메인 루트 `_index.md` 부재(cosmetic) | Phase 2 문서 보강 |
| D-4 | **INDEX.md 부재 6 도메인** (0-0/5-3/5-4/6-4/6-10/6-13) | 보조 인덱스 부재 | WARN · AUTHORITY_CHAIN+CONFLICT_LOG 전수 존재 + 전역 SOT2_MASTER_INDEX 보유 | Phase 2 (선택) |
| D-5 | **VAMOS_IMPLEMENTATION_READINESS_REVIEW.md** | SOT 1건 변경 | CHANGED vs 2026-03-27 baseline (review 문서, D2.0 spec 아님) · 신규 snapshot이 새 D2 기준선 | 기록만 |

**OPEN 충돌 레지스터(원문 발췌)**: D1_VERDICT.json `open_conflict_register` (5-3 ×5 + 6-5 ×1 = 6행).

## 4. 재현성 메타

- 결정론(1-2~1-5, 1-9): **동일 입력 = 동일 출력** — 2회 재실행 핵심 지표 동일(MISMATCH 0 / BROKEN 1 / OPEN 6 / SDV4-WARN 2).
- 각 산출물에 `timestamp + input_hash(SHA-256) + skill_version` 기록.
- 엔진 스크립트: `_d1/{d1_common,d1_runner,d1_runner2,d1_integrity,d1_aux,d1_verdict}.py`
- SOT2 매니페스트 SHA-256: `26ff46ba0f1e3b78639022410b3997b0bb2ba2293ca44a53b1b502a724f9e574` (2,654 파일)

## 5. 판정

**D1 PASS (CONDITIONAL)** — 값 게이트 5/5 통과. 이연 5항목(D-1~D-5) 전수 등록(누락 0), 자동 정본 변경 0건.
사용자 지시(안전·무누락·무오류)에 따라 위험한 정본 콘텐츠 자동 수정 없이 전 항목을 추적 이연 처리.
다음: **Phase 2-0** (외부 의존성 재확인) → 2-1(CLAUDE.md 보강, 1-6 GAP 입력).
