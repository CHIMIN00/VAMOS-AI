---
name: validate
description: EA/CM 산출물의 결정론적 검증(DV-1~DV-9 / CM-DV1~DV6) + AI 의미적 검증. 저장 후 또는 검증 필요 시 사용.
---

# VAMOS v13 산출물 검증 스킬 (2계층) v2

> `/validate [파일경로|all]` — 결정론적 검증(Layer A) + AI 의미적 검증(Layer B)

## 핵심 원칙

**Layer A (결정론적)가 먼저, Layer B (AI)는 그 다음입니다.**
Layer A가 FAIL이면 Layer B를 실행하지 않습니다.

---

## Layer A: 결정론적 검증 (프로그램 — AI 판단 0%)

### EA 산출물인 경우 (v13_EA*.json):

```bash
python "D:/VAMOS/.claude/hooks/deterministic_validator.py" "<대상_EA_JSON_경로>"
```

**DV-1~DV-9 검증 항목** (프로그램이 자동 수행):
- DV-1: JSON 스키마 필수 필드 존재 여부
- DV-2: metadata.categories 합계 = total_items_extracted = items 길이
- DV-3: source_line이 0 초과 & 파일 줄 수 이하
- DV-4: source_text 키워드가 해당 줄 ±3줄에 존재
- DV-5: item_id 연속성 (건너뛴 번호)
- DV-6: value_type vs value 실제 타입 일치
- DV-7: COUNT key ↔ LIST key 길이 교차 검증
- DV-8: [v2] 표준 키 목록 대조 (비표준 키 네이밍, 유사 키 오타)
- DV-9: [v2] source_file_hash 변경 감지 (SOT 변경 시 EA 무효화)

### CM 산출물인 경우 (v13_CM*.json):

```bash
python "D:/VAMOS/.claude/hooks/cm_validator.py" "<대상_CM_JSON_경로>"
```

**CM-DV1~CM-DV6 검증 항목** (프로그램이 자동 수행):
- CM-DV1: JSON 스키마 필수 필드 존재
- CM-DV2: 메타데이터 카운트 정합성
- CM-DV3: source 참조 EA 존재 확인
- CM-DV4: source_text SOT 원본 대조
- CM-DV5: result/severity 유효성
- CM-DV6: 중복 비교 탐지

**판정**: CRITICAL ≥ 1이면 FAIL → Layer B 진행 불가. 오류 수정 후 재실행.

---

## Layer B: AI 의미적 검증 (Layer A PASS 후에만)

Layer A를 통과한 항목에 대해 **AI가 판단해야만 하는 것들**만 검증합니다:

### SV-1: 의미적 정확성 (AI 전용)
- source_text의 맥락과 추출된 key/context가 의미적으로 맞는지
- 예: "COND 모듈 10개"에서 추출한 key가 `EXP_MODULE_COUNT`이면 의미 불일치

### SV-2: 추출 완전성 (AI 전용)
- SOT 원본 파일을 Read tool로 전체 읽기
- C1~C8에 해당하는 값이 원본에 있으나 JSON에 누락된 것이 있는지 확인
- 특히: 숫자(C1), "N개"(C2), LOCK/FREEZE(C7), "참조/§"(C8) 패턴 집중

### SV-3: 표준 키 적절성 (AI 전용)
- 표준 키 목록에 있는 개념을 자유 키로 추출한 경우 WARNING
- 동일 개념을 다른 key로 추출한 경우 WARNING

---

## OrgForge 원칙 (A-4)

> 기반: OrgForge Framework (2026) — "결정론적 엔진이 ground truth를 유지하고, LLM은 표면 텍스트만 생성"

이 스킬의 2계층 구조는 OrgForge 철학과 동일합니다:

| OrgForge 원칙 | VAMOS /validate 대응 |
|--------------|---------------------|
| 결정론적 엔진 = ground truth | Layer A: python 스크립트가 PASS/FAIL 판정 |
| LLM = 표면 텍스트 생성만 | Layer B: AI는 의미적 판단만 수행 |
| 엔진이 먼저, LLM이 나중 | Layer A FAIL → Layer B 실행 불가 |

**적용 규칙**:
1. Layer A의 결정론적 판정을 AI가 번복할 수 없습니다
2. Layer B는 Layer A가 검증할 수 없는 "의미적" 영역만 담당합니다
3. 수치, 구조, 스키마 검증은 반드시 프로그램(Layer A)이 수행합니다

---

## 실행 절차

```
1. 파일 유형 판별: EA(v13_EA*.json) 또는 CM(v13_CM*.json)
   ↓
2. Layer A 실행:
   - EA → python deterministic_validator.py <파일>
   - CM → python cm_validator.py <파일>
   ↓ PASS?
3. Layer A 결과 읽기: validation/ 디렉토리의 결과 확인
   ↓ CRITICAL = 0?
4. Layer B 실행: SV-1 ~ SV-3 (AI 판단)
   ↓
5. 종합 결과 저장
```

## 출력

Layer A 결과: `v13_results/phase0/extraction/validation/{파일명}_dv_result.json` (자동 생성)
Layer B 결과: `v13_results/phase0/extraction/validation/{파일명}_sv_result.json` (이 스킬이 생성)

---

## $ARGUMENTS 처리

- `$ARGUMENTS`가 파일 경로면 → 해당 파일만 검증
- `$ARGUMENTS`가 `all`이면 → extraction/ 디렉토리의 모든 v13_EA*.json 검증
- `$ARGUMENTS`가 비어있으면 → 가장 최근 생성된 EA JSON 파일 검증

---

## [SOT 2 확장] SOT 2 구조화 추출물 검증 (v2 추가)

> 기존 EA JSON DV-1~DV-9 검증을 유지한 채, SOT 2 추출물(SC1~SC8)에 대한 검증 규칙을 추가합니다.

### SOT 2 전용 결정론적 검증 (SDV-1~SDV-7)

| 규칙 | 검증 내용 | 판정 |
|------|---------|------|
| SDV-1 | SC JSON 필수 필드 존재 (source_file, domain, items) | PASS/FAIL |
| SDV-2 | SC 카테고리 합계 = 전체 항목 수 | PASS/FAIL |
| SDV-3 | source_line 범위 유효 (0 < line ≤ 파일 총 줄수) | PASS/FAIL |
| SDV-4 | LOCK 값이 Part2 정본과 일치 (sot-check 연동) | PASS/WARN/FAIL |
| SDV-5 | 스키마 필드 타입 일치 (Pydantic 모델 검증) | PASS/FAIL |
| SDV-6 | 도메인 간 중복 정의 없음 (canonical owner 확인) | PASS/WARN |
| SDV-7 | part2_reference 라인이 실제 Part2에 존재 | PASS/SHIFTED/FAIL |

### 추가 명령어

- `/validate sot2 {파일}` → SOT 2 추출물 SDV-1~SDV-7 검증
- `/validate sot2-all` → SOT 2 전체 추출물 검증
- `/validate sot2-locks` → LOCK 값 전수 검증 (SDV-4 집중)

### SOT 2 AI 의미 검증 (SSV-1~SSV-3, 기존 SV와 별도)

| 규칙 | 검증 내용 |
|------|---------|
| SSV-1 | 상세명세 내용이 SOT 원본의 의도와 일치하는가 |
| SSV-2 | 방식 C 요약이 Part2 정본의 핵심을 정확히 포착하는가 |
| SSV-3 | 계획서의 Phase 구분이 상세명세 항목 수/복잡도와 적절한가 |

### 저장 위치
- `D:/VAMOS/docs/sot 2/_extractions/validation/{도메인}_validation.json`
