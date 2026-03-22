# v9-B: 파일 경로 정합성 검증 프롬프트

> **Pipeline**: VAMOS v9.0.0
> **관점 ID**: v9-B (Path Consistency)
> **작성일**: 2026-03-07
> **대상 문서**: `VAMOS_구현가이드_PART2_구현단계.md` v20.4.0 (3,807줄)

---

## [1] HEADER

```
v9 SCOPE HEADER — Phase -1I 산출물
> v9 SCOPE: 문서 정합성/완전성/구현 가능성/수량 일관성/경로 정합성/의존성 순서/외부 의존성
> BOUNDARY: §7.5 중 "문서 검증 가능" 태그 항목만 범위 내
> OUT OF SCOPE: 코드 동작 검증, 성능 벤치마크, 보안 침투 테스트, 런타임 행위
> RULE-14: §7.5 "구현 후 검증" 항목 검출 시 → OUT_OF_SCOPE (FN 아님)
```

**관점**: v9-B — 파일 경로 정합성 (Path Consistency)
**핵심 질문**: PART2의 모든 파일경로가 PHASE_B2 모노레포 구조와 일치하는가?
**검출 대상**: PHASE_B2 미존재 경로, 동일 파일의 경로 불일치, 상대/절대 혼재

---

## [2] SCOPE — 검증 대상 범위

**포함 범위**:
- §2 V0 (line 59~1375): AI 프롬프트 내 디렉토리 트리 + 파일 경로
- §3 V1 (line 1377~1711): 테이블 내 파일명/경로 참조
- §4 V2 (line 1713~2099): AI 프롬프트 내 파일 경로
- §5 V3 (line 2101~2697): AI 프롬프트 내 파일 경로
- §6 횡단 상세 (line 2699~3562): CI yml 14개, SDAR 파일 3개, UI 파일 등
- 경로가 등장하는 **모든 위치** (인라인 코드 블록, 테이블, 본문 포함)

**제외 범위**:
- 변경 이력 (line 3777~3807)
- §7.5 이후 경로 미등장 영역

---

## [3] GT REFERENCE — 참조 Ground Truth

| GT | 파일 경로 | 용도 |
|----|----------|------|
| **GT-1** | `D:\VAMOS\04. 구현단계\v9_results\phase0\gt1_file_path_registry.json` | PART2 경로 ↔ PHASE_B2 경로 매칭 결과 |

**GT-1 핵심 구조**:
- `entries[]`: 각 고유 경로의 `normalized_path`, `part2_references[]`, `phase_b2_exists`, `v_scope`, `allowlist`
- `structural_discrepancies[]`: 구조적 불일치 3건 (SD-01: 파일 vs 디렉토리, SD-02: i1_ vs i01_ 명명, SD-03: modules/ 미정의)
- `stats`: `total_unique_paths`, `matched`, `allowlisted`, `unmatched`

**추가 참조**:
- `D:\VAMOS\04. 구현단계\v9_results\phase-1\v9_allowlist.json` — 허용 경로 3건 (rpc/, data/, logs/)

---

## [4] RULES — 적용 방어 규칙

| RULE | 규칙 요약 | 적용 이유 |
|------|----------|----------|
| **RULE-1** | `section.key` 정규화 전체 경로 사용. 부분 문자열 매칭 금지 | 경로 비교 시 전체 경로 기준 |
| **RULE-2** | V0/V1/V2/V3 범위 한정자 먼저 확인 | V2 전용 경로를 V0에서 누락으로 판정 금지 |
| **RULE-5** | 요약 테이블 vs 전체 열거, 약칭 vs 풀네임은 구조적 표현 차이 | `i01_intent_detector.py` vs `i1_intent/` 구조적 차이 |
| **RULE-6** | 코드 주석(`#`) 내 기술명은 참고/예고 분류 | 주석 내 경로를 현재 경로로 오인 방지 |
| **RULE-9** | HTML 주석 내 항목은 허용 목록 자동 PASS | XREF-V0-12 (rpc/), XREF-V0-10 (data/) |
| **RULE-11** | §6 + §7 포함 필수 | §6 CI/CD yml, SDAR 파일 경로 검증 |
| **RULE-14** | v9 범위 = 문서 내부 정합성 | 실제 파일 시스템 존재 여부는 범위 외 |

---

## [5] ALLOWLIST — 허용 목록

**경로 허용 목록** (Phase -1C):

| 경로 | 사유 | 태그 |
|------|------|------|
| `rpc/` | PHASE_B2 미명시. Tauri↔Python 통신 기능적 필요 | XREF-V0-12 |
| `data/` | CLAUDE.md 기준 추가. PHASE_B2 미포함 | XREF-V0-10 |
| `logs/` | CLAUDE.md 기준 추가. PHASE_B2 미포함 | NOTE |

**구조적 불일치 허용** (GT-1 structural_discrepancies):

| ID | 내용 | 처리 |
|----|------|------|
| SD-01 | PART2는 단일 파일(`i01_intent_detector.py`), PHASE_B2는 서브디렉토리(`i1_intent/`) | 경로 불일치로 보고하되 severity=MEDIUM (관점 C에서 추가 검증) |
| SD-02 | V0-STEP-4(`i1_`)와 V1-Phase 1(`i01_`) 명명 불일치 | severity=LOW (동일 모듈 인식 가능) |
| SD-03 | V2/V3 `modules/` 디렉토리가 PHASE_B2에 미정의 | severity=MEDIUM |

---

## [6] CHECK ITEMS — 구체적 검증 항목

### [B-1] GT-1 unmatched 경로 0건 확인
GT-1에서 `phase_b2_exists: false`이고 `allowlist: false`인 경로가 0건인지 확인.

**절차**:
1. GT-1의 `entries[]`에서 `phase_b2_exists == false && allowlist == false` 필터
2. 해당 항목이 0건이면: `PASS`
3. 1건 이상이면: 각 항목에 대해
   - PART2 참조 위치(`part2_references`) 확인
   - V 범위 확인 (V2+ 전용 경로는 PHASE_B2 미포함 가능)
   - 오탐 여부 판정 후 `REAL_ERROR` 또는 `FALSE_POSITIVE` 분류

**Severity**: unmatched 경로가 Stage의 핵심 산출물이면 `HIGH`, 보조 파일이면 `MEDIUM`

### [B-2] 동일 파일 경로 일관성
동일 파일의 경로가 PART2 내 모든 출현 위치에서 일관적인지 확인.

**절차**:
1. GT-1의 각 `entry`에서 `part2_references[]`의 경로 표현을 비교
2. 동일 파일에 대해 서로 다른 경로 표현이 있으면:
   - 상대경로 vs 절대경로 차이인가? → B-3에서 처리
   - 명명 불일치 (예: `i1_` vs `i01_`)인가? → SD-02 참조, severity=LOW
   - 완전히 다른 경로인가? → `HIGH`
3. 일관적이면: `PASS`

### [B-3] 상대경로 ↔ 절대경로 동일 파일 확인
상대경로 참조가 절대경로와 동일 파일을 가리키는지 확인.

**절차**:
1. GT-1에서 `format: "relative"`인 참조 항목 추출
2. 해당 상대경로를 PHASE_B2 디렉토리 구조 기준으로 절대경로로 해석
3. 해석된 절대경로가 GT-1의 `normalized_path`와 일치하는가?
4. 불일치 시: `HIGH` (경로 혼동 위험)
5. 일치 시: `PASS`

### [B-4] §6 파일 경로 ↔ PHASE_B2 일치
§6에 등장하는 파일 경로(CI yml 14개, SDAR 파일 3개 등)가 PHASE_B2와 일치하는지 확인.

**절차**:
1. §6에서 파일 경로가 등장하는 모든 위치 식별:
   - §6.4 CI/CD: yml 14개 (ci.yml, deploy.yml 등)
   - §6.9 SDAR: 관련 파일 3개
   - §6.1 UI: 컴포넌트 파일 경로
   - §6.2 Rust/Tauri: IPC 핸들러 파일 경로
   - §6.5 보안: 보안 관련 모듈 경로
2. 각 경로를 GT-1과 대조
3. GT-1에 없는 경로: PHASE_B2에 직접 확인 후 `REAL_ERROR` 또는 `FALSE_POSITIVE`
4. XREF-V0-19 주의: PHASE_B6은 ci.yml 단일 통합, PART2는 역할별 분리 → 구조적 차이로 허용

### [B-5] V1 Phase 2~6 파일 경로 부재 보고
V1 Phase 2~6에 파일 경로가 전무한 상태를 정보 항목으로 보고.

**절차**:
1. PART2 §3 (V1 Phase 2~6)에서 파일 경로 등장 여부 확인
2. 파일 경로가 없으면: `INFO` (ERROR가 아님)
   - 이유: V1은 테이블 형식으로 모듈명만 기재, 파일 경로 미포함이 구조적 한계
   - 관점 C(구현 가능성)에서 별도 검증
3. 파일 경로가 있으면: GT-1과 대조하여 정상 처리

**분류**: `STYLE_CONCERN` (오류 아님, 개선 권장)

---

## [7] OUTPUT FORMAT — 결과 JSON 스키마

```json
{
  "perspective": "v9-B",
  "perspective_name": "파일 경로 정합성",
  "timestamp": "2026-MM-DDTHH:mm:ssZ",
  "target_doc": "VAMOS_구현가이드_PART2_구현단계.md v20.4.0",
  "gt_version": "gt1_file_path_registry.json",
  "rules_applied": ["RULE-1", "RULE-2", "RULE-5", "RULE-6", "RULE-9", "RULE-11", "RULE-14"],

  "summary": {
    "total_checks": 0,
    "total_unique_paths": 0,
    "matched": 0,
    "allowlisted": 0,
    "unmatched": 0,
    "pass": 0,
    "real_error": 0,
    "false_positive": 0,
    "style_concern": 0,
    "info": 0,
    "blocker": 0,
    "high": 0,
    "medium": 0,
    "low": 0
  },

  "structural_discrepancies": [
    {
      "id": "SD-nn",
      "description": "구조적 불일치 설명",
      "severity": "MEDIUM | LOW",
      "part2_pattern": "PART2 경로 패턴",
      "phase_b2_pattern": "PHASE_B2 경로 패턴"
    }
  ],

  "findings": [
    {
      "id": "B-xxx-nnn",
      "check_item": "B-1 | B-2 | B-3 | B-4 | B-5",
      "path": "검증 대상 경로",
      "line": 0,
      "section": "PART2 섹션",
      "description": "발견 내용 상세 기술",
      "expected": "GT-1 / PHASE_B2 기준 경로",
      "actual": "PART2 실제 경로",
      "severity": "HIGH | MEDIUM | LOW",
      "classification": "REAL_ERROR | FALSE_POSITIVE | STYLE_CONCERN | INFO",
      "rule_applied": "RULE-N (해당 시)",
      "allowlist_match": "허용 목록 항목 ID (해당 시)"
    }
  ]
}
```

---

## [8] SEVERITY — 판정 기준

| 등급 | 기준 | 이 관점의 예시 |
|------|------|--------------|
| **BLOCKER** | 구현 불가 | 핵심 모듈의 경로가 완전히 잘못되어 구현 불가 (극히 드문 경우) |
| **HIGH** | 경로 불일치로 구현 결과가 SOT와 다름 | unmatched 핵심 경로 (B-1), 완전히 다른 경로 (B-2), 상대/절대 불일치 (B-3) |
| **MEDIUM** | 혼란 유발 | 파일 vs 디렉토리 구조 차이 (SD-01), V2+ modules/ 미정의 (SD-03), §6 경로 미등록 (B-4) |
| **LOW** | 표기 불통일 | i1_ vs i01_ 명명 (SD-02), V1 경로 부재 (B-5) |

---

## 실행 지시

1. GT-1의 `stats` 섹션으로 전체 현황 먼저 파악
2. B-1 (unmatched 0건 확인)을 최우선으로 실행 — 가장 기계적이고 명확
3. B-2, B-3은 GT-1의 `part2_references[]` 비교로 수행
4. B-4는 §6 (line 2699~3562)을 직접 읽으며 경로 추출 후 GT-1 대조
5. B-5는 §3 V1 (line 1377~1711)에서 경로 존재 여부 확인 — INFO 수준
6. RULE-9 주의: 허용 목록(rpc/, data/, logs/)에 해당하는 경로는 자동 PASS
7. RULE-5 주의: 약칭/풀네임, 요약/상세 표현 차이를 오류로 판정하지 않음