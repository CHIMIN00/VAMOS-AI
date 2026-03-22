# Phase 3: PART2 업데이트 실행

> **대화**: 대화 10
> **목표**: Phase 2에서 확정된 수정 사항을 PART2 v25.2.0에 반영 → v26.0.0 생성 (원본 보호 하에)
> **성격**: 실제 문서 수정 단계. 원본 보호 프로토콜 최우선.
> **선행 조건**: Phase 2 PASS

---

## Pre-check Protocol

```
① 본 계획 파일 읽기: D:\VAMOS\04. 구현단계\v12\v12_plan.md
② 본 프롬프트 읽기: D:\VAMOS\04. 구현단계\v12\prompts\phase3_prompt.md
③ 진행 상태 확인: D:\VAMOS\04. 구현단계\v12\v12_results\v12_phase_status.json
④ Phase 2 PASS 확인 (FAIL이면 Phase 3 진행 불가)
⑤ Phase 2 핵심 산출물 로드:
   - v12_final_missing_list.md (최종 누락 목록)
   - v12_update_plan.md (업데이트 계획 — 수정 순서, 영향 분석)
   - v12_s6_final_mapping.md (§6 참조 57건 해소 방안)
   - v12_pattern_resolution.md (v11 패턴 해소 방안)
⑥ Phase 0 산출물 로드:
   - v12_section_map.json (현재 섹션 구조)
   - v12_numeric_registry.json (현재 수치)
⑦ 확인 완료 후 작업 시작
```

---

## 스킬 에이전트 실행 규칙

> **필수**: 본 Phase의 작업은 **Agent tool(스킬 에이전트)**을 활용하여 일관된 결과를 도출합니다.

1. **순차 실행**: PART2 수정 작업(3-A~3-F)은 v12_update_plan.md 순서대로 순차 실행 (동일 파일 수정으로 병렬 불가)
2. **동일 템플릿**: 모든 산출물은 본 프롬프트에 정의된 출력 포맷 준수
3. **증거 기반**: 모든 수정에 diff 기록 + 수정 전/후 텍스트 필수
4. **재현성**: BP-1~15 원본 보호 프로토콜 준수로 역추적 가능 보장

---

## 입력 파일

### Phase 2 산출물 (수정 근거)

| # | 파일 | 경로 |
|---|------|------|
| 1 | 최종 누락 목록 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase2\v12_final_missing_list.md` |
| 2 | 업데이트 계획 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase2\v12_update_plan.md` |
| 3 | §6 최종 매핑 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase2\v12_s6_final_mapping.md` |
| 4 | 패턴 해소 방안 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase2\v12_pattern_resolution.md` |
| 5 | Phase 2 판정 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase2\v12_phase2_verdict.md` |

### Phase 0 산출물 (인덱스)

| # | 파일 | 경로 |
|---|------|------|
| 6 | Section Map | `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_section_map.json` |
| 7 | Numeric Registry | `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_numeric_registry.json` |
| 8 | Reference Map | `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_reference_map.json` |

### Phase -1 산출물

| # | 파일 | 경로 |
|---|------|------|
| 9 | v25 편집 충돌 검사 결과 (Phase -1) | `D:\VAMOS\04. 구현단계\v12\v12_results\phase-1\v12_v25_conflict.md` |

### PART2 원본 (수정 대상)

| 파일 | 경로 |
|------|------|
| PART2 구현단계 v25.2.0 | `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` |

### v12 구현 스킬 에이전트 (갱신 대상)

| 파일 | 경로 |
|------|------|
| v12 impl_skill_agent | `D:\VAMOS\04. 구현단계\v12\v12_impl_skill_agent.md` |

---

## 스킬 에이전트 패턴

| 패턴 | 출처 | 적용 |
|------|------|------|
| 원본 보호 프로토콜 BP-1~15 | v11 | 3-0 백업 + 전체 수정 프로세스 |
| 정본 우선순위 | v6 §4-A | 내용 충돌 시 |
| Phase 테이블 삽입 | v10 Phase C | 3-A 신규 항목 삽입 |

### v11 원본 보호 프로토콜 BP-1~15 (전수 적용)

| BP | 규칙 | 적용 |
|----|------|------|
| BP-1 | 수정 전 백업 | 3-0에서 수행 |
| BP-2 | SHA256 지문 기록 | 3-0에서 수행 |
| BP-3 | diff 저장 | 건별 diff 저장 |
| BP-4 | 기존 행 삭제 금지 | 모든 수정에서 준수 |
| BP-5 | 기존 행 변경 최소화 | 참조 구체화, 수치 갱신만 기존 행 변경 |
| BP-6 | 삽입은 테이블 끝에 추가 | Phase 테이블 항목 삽입 시 |
| BP-7 | 마커 부착 | `<!-- feature_id v26 -->` 형식 |
| BP-8 | 버전 헤더 갱신 | v25.2.0 → v26.0.0 |
| BP-9 | changelog 추가 | 문서 하단 변경이력 |
| BP-10 | 행 수 기록 | 수정 전/후 행 수 |
| BP-11 | 중복 ID 확인 | 삽입 시 기존 ID 충돌 확인 |
| BP-12 | LOCK 값 보호 | LOCK/FREEZE 값 변경 금지 |
| BP-13 | heading 계층 보호 | heading 추가/변경 시 계층 확인 |
| BP-14 | 참조 무결성 | 새 항목이 참조하는 §N 존재 확인 |
| BP-15 | 역패치 가능 | 모든 수정 되돌리기 가능하도록 diff 보존 |

---

## 작업 상세

### 작업 3-0: 원본 백업 + SHA256 지문

**반드시 모든 수정 전에 수행**

**작업**:
1. PART2 v25.2.0 전체 복사 → 백업 파일
2. SHA256 해시 계산

**실행 명령** (참고):
```bash
cp "D:/VAMOS/docs/guides/VAMOS_구현가이드_PART2_구현단계.md" "D:/VAMOS/04. 구현단계/v12/v12_results/phase3/backup/VAMOS_구현가이드_PART2_구현단계_v25.2.0_backup.md"
sha256sum "D:/VAMOS/04. 구현단계/v12/v12_results/phase3/backup/VAMOS_구현가이드_PART2_구현단계_v25.2.0_backup.md"
```

**산출물**:
- `D:\VAMOS\04. 구현단계\v12\v12_results\phase3\backup\VAMOS_구현가이드_PART2_구현단계_v25.2.0_backup.md`
- `D:\VAMOS\04. 구현단계\v12\v12_results\phase3\backup\v25_backup.md` (백업 메타데이터)
- `D:\VAMOS\04. 구현단계\v12\v12_results\phase3\backup\v25_integrity.json`

**v25_integrity.json 포맷**:
```json
{
  "source": "D:\\VAMOS\\docs\\guides\\VAMOS_구현가이드_PART2_구현단계.md",
  "version": "v25.2.0",
  "lines": 5858,
  "sha256": "...",
  "backup_path": "...",
  "backup_sha256": "...",
  "timestamp": "2026-03-XX"
}
```

---

### 작업 3-A: MISSING 항목 PART2 반영

**입력**: `v12_final_missing_list.md`에서 "신규 삽입" 유형

※ v12_v25_conflict.md 참조: Phase -1에서 발견된 편집 충돌 영역 회피하여 수정

**작업**:
1. v12_update_plan.md의 수정 순서에 따라 실행
2. 각 MISSING 항목을 해당 Phase 테이블에 삽입
3. 삽입 위치: 해당 Phase 테이블의 마지막 행 다음 (BP-6)
4. 마커 부착: `<!-- feature_id v26 -->` (BP-7)
5. 건별 diff 기록

**삽입 행 포맷** (v10 Phase C 계승):
```markdown
| 작업ID | 세부 작업 | AI 프롬프트 매핑 | 비고 | <!-- feature_id v26 -->
```

**diff 저장**: 건별로 `D:\VAMOS\04. 구현단계\v12\v12_results\phase3\diffs\diff_NNN.md`

**diff 파일 포맷**:
```markdown
# Diff NNN: [feature_id]
- **유형**: 신규 삽입
- **대상 섹션**: §X.Y Phase Z
- **삽입 위치**: L행 다음
- **삽입 내용**: (실제 삽입 텍스트)
- **영향**: (연쇄 영향 있으면 기재)
```

---

### 작업 3-B: §6 참조 57건 해소

**입력**: `v12_s6_final_mapping.md`

**작업 (분류별)**:

1. **§6.X 구체화 가능** (참조만 변경):
   - "§6 참조" → "§6.X 참조" 텍스트 변경
   - 기존 행 변경 (BP-5 주의)
   - diff 저장

2. **§6에 내용 추가 필요**:
   - §6.X 해당 위치에 새 항목/설명 추가
   - 마커 부착
   - diff 저장

3. **§2~§5에 직접 기재**:
   - 해당 Phase 테이블에 세부 내용 추가
   - "§6 참조" 텍스트 제거 또는 보충
   - diff 저장

---

### 작업 3-C: v11 미해결 패턴 A/B 해소

**입력**: `v12_pattern_resolution.md`에서 OPEN 판정된 패턴

**작업**:
1. Pattern A (연쇄 미갱신): §6.13 작업량 테이블 수치 갱신, §7.4 GO/NO-GO 체크리스트 갱신
2. Pattern B (Gate 명칭): Stage Gate 명칭 통일 (모든 출현 위치)
3. V1 구조 고립: §3 Phase 테이블 포맷을 §4/§5와 통일
4. V3 과적재: §5에 충분한 구현 상세 추가
5. V2-P2 저커버리지: §4.2 AI 프롬프트 커버 범위 확장

**주의**: 각 수정은 Phase 2 해소 방안에 명시된 방법으로만 수행. 독자적 판단 금지.

---

### 작업 3-D: v12 impl_skill_agent §5.2 동기화

**입력**: `v12_impl_skill_agent.md` (현재 v24.0.0 기준, 440줄)
**작업**:
1. §5.2 I/O 요약의 V1 ❌/⚠️ → v25.2.0/v26.0.0 반영 후 ✅로 갱신
2. impl_status.json 스키마가 v26.0.0과 일치하는지 확인
3. LOCK 값 40개가 v26.0.0과 일치하는지 확인

**산출물**: v12_impl_skill_agent.md 직접 수정

---

### 작업 3-E: 소폭 수정

**작업**:
1. V0-STEP-6 R1~R11 참조 확인 및 필요 시 보완
2. §6.12.6 번호 중복 오류 수정 (이전 대화에서 발견)
3. 기타 소폭 수정 (Phase 2에서 식별된 건만)

---

### 작업 3-F: 버전 업데이트

**작업**:
1. 문서 상단 버전: v25.2.0 → v26.0.0
2. changelog 추가:
```markdown
| v26.0.0 | 2026-03-XX | v12 검증 파이프라인 결과 반영: MISSING X건 삽입, §6 참조 57건 구체화, v11 패턴 해소, §6.12.6 중복 수정 |
```
3. 최종 행 수 기록

---

### Ripple Map 생성

**작업**: 모든 수정 건의 연쇄 영향 추적

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase3\v12_ripple_map.json`

**포맷**:
```json
{
  "modifications": [
    {
      "id": "MOD-001",
      "type": "insert|modify|delete",
      "section": "§X.Y",
      "line_before": 123,
      "line_after": 125,
      "ripple_targets": ["§6.13", "§7.4"],
      "ripple_applied": true
    }
  ],
  "summary": {
    "total_modifications": 0,
    "inserts": 0,
    "modifies": 0,
    "deletes": 0,
    "lines_before": 5858,
    "lines_after": 0
  }
}
```

---

### 교차검증 ⑥: 건별 diff 검증 + 구조 무결성

**작업**:
1. diff 파일 전수 확인 (건수 = 총 수정 건수)
2. 구조 무결성 검증:
   - heading 계층 확인 (§1~§7)
   - 테이블 산술 확인 (§6.13)
   - LOCK 값 유지 확인 (₩40,000/월, cosine≥0.95, CB 60s 등)
   - ID 참조 무결성 (중복 0건)
3. 기존 행 변경/삭제 0건 확인 (참조 구체화, 수치 갱신 제외)
4. 역패치 가능성 확인 (diff로 되돌리기 가능한지)

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase3\v12_phase3_verdict.md`

**포맷**:
```markdown
# v12 Phase 3 검증 보고서

## 수정 통계
| 항목 | 수치 |
|------|------|
| v25.2.0 원본 행 수 | 5,858 |
| v26.0.0 최종 행 수 | X |
| 추가 행 | +X |
| 변경 행 | X (참조 구체화 + 수치 갱신) |
| 삭제 행 | 0 |
| diff 파일 수 | X |

## 구조 무결성
| 항목 | 결과 |
|------|------|
| heading 계층 | PASS/FAIL |
| 테이블 산술 | PASS/FAIL |
| LOCK 값 유지 | PASS/FAIL |
| ID 무결성 | PASS/FAIL |
| 기존 행 보호 | PASS/FAIL |
| 역패치 가능 | PASS/FAIL |

## 판정: PASS/FAIL
```

---

## 산출물 전수 목록

| # | 파일 | 경로 |
|---|------|------|
| 1 | 원본 백업 | `v12_results/phase3/backup/VAMOS_구현가이드_PART2_구현단계_v25.2.0_backup.md` |
| 2 | 백업 메타데이터 | `v12_results/phase3/backup/v25_backup.md` |
| 3 | 무결성 JSON | `v12_results/phase3/backup/v25_integrity.json` |
| 4 | Diff 파일들 | `v12_results/phase3/diffs/diff_NNN.md` (N개) |
| 5 | Ripple Map | `v12_results/phase3/v12_ripple_map.json` |
| 6 | Phase 3 판정 | `v12_results/phase3/v12_phase3_verdict.md` |
| 7 | PART2 v26.0.0 | `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` (직접 수정) |
| 8 | v12 impl_skill_agent | `D:\VAMOS\04. 구현단계\v12\v12_impl_skill_agent.md` (직접 수정) |

---

## AI 오류 방지 규칙 (이 Phase에서 준수)

1. **원본 백업 최우선**: 3-0 완료 전 어떤 수정도 하지 말 것
2. **BP-1~15 전수 준수**: 매 수정 건마다 체크리스트 확인
3. **LOCK 값 절대 변경 금지**: ₩40,000/월, cosine≥0.95, CB 60s 등 — 읽기만
4. **기존 행 삭제 금지**: 신규 삽입은 테이블 끝에 추가. 기존 행은 변경하지 않음 (참조 구체화, 수치 갱신 제외)
5. **마커 필수**: 모든 신규/변경 행에 `<!-- feature_id v26 -->` 마커
6. **diff 필수**: 모든 수정 건 diff 파일 저장
7. **수정 순서 준수**: v12_update_plan.md의 순서대로 실행
8. **과잉 수정 금지**: Phase 2에서 확정된 건만 수정. 추가 발견 시 기록만 (Phase 4 보고서에 포함하여 후속 조치 판단)
9. **필드 값 enum 준수**: Ripple Map `type`은 `insert`/`modify`/`delete`(3개)만 허용. 이전 Phase에서 확정된 priority/category/source_group/status/severity 값 변경 금지

---

## 완료 시 수행

1. 위 산출물 전수 존재 확인
2. PART2 v26.0.0 행 수 확인
3. `v12_phase_status.json` 업데이트:
   ```json
   {
     "phase3": {
       "status": "completed",
       "conversation": "대화 10",
       "pass": true/false,
       "started_at": "2026-03-XX",
       "completed_at": "2026-03-XX"
     }
   }
   ```
4. 수정 통계 요약 출력
5. FAIL이면 원본 복구 절차 안내 (백업에서 복구)
