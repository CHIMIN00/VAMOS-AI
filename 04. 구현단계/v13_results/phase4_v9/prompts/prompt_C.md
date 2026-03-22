# v9-C: 구현 가능성 검증 프롬프트

> **v13 Phase 4 재실행 — 세션 24 프롬프트 갱신**
> 원본: `v9_results/phase0/v9_prompt_C_implementability.md`
> 갱신 사유: GT 경로를 `phase4_v9/gt/`로 변경, v13 enhanced skill 참조 추가

> **Pipeline**: VAMOS v9.0.0 (v13 Phase 4 재실행)
> **관점 ID**: v9-C (Implementability)
> **작성일**: 2026-03-07 (갱신: 2026-03-22)
> **대상 문서**: `VAMOS_구현가이드_PART2_구현단계.md` v20.4.0 (3,807줄)

---

## v13 Enhanced Skill 참조

Wave 실행 시 아래 스킬을 활용하여 검증 정확도를 높인다:

- **/cross-match** — 교차 매칭 기반 구현 가능성 검증. 체크리스트 항목과 실제 프롬프트/테이블 내용 간의 대응 관계 확인에 사용

---

## [1] HEADER

```
v9 SCOPE HEADER — Phase -1I 산출물
> v9 SCOPE: 문서 정합성/완전성/구현 가능성/수량 일관성/경로 정합성/의존성 순서/외부 의존성
> BOUNDARY: §7.5 중 "문서 검증 가능" 태그 항목만 범위 내
> OUT OF SCOPE: 코드 동작 검증, 성능 벤치마크, 보안 침투 테스트, 런타임 행위
> RULE-14: §7.5 "구현 후 검증" 항목 검출 시 → OUT_OF_SCOPE (FN 아님)
```

**관점**: v9-C — 구현 가능성 (Implementability)
**핵심 질문**: AI 프롬프트를 받은 개발자/AI가 실제로 구현할 수 있을 만큼 구체적인가?
**검출 대상**: 모호한 명세, 누락된 파라미터, 참조만 있고 값 없음, 실행 가이드 부재

---

## [2] SCOPE — 검증 대상 범위

**포함 범위**:
- §2 V0 (line 59~1375): AI 프롬프트 6개 (STEP-1 ~ STEP-6)
- §3 V1 (line 1377~1711): 테이블 77행 (Phase 1~6, AI 프롬프트 없음)
- §4 V2 (line 1713~2099): AI 프롬프트 3개 (Phase 1~3)
- §5 V3 (line 2101~2697): AI 프롬프트 3개 (Phase 1~3)
- §6 횡단 상세 (line 2699~3562): 13개 하위 섹션의 고유 정의

**제외 범위**:
- 변경 이력 (line 3777~3807)
- §7 GO/NO-GO (구현 가능성이 아닌 검증 항목)
- §7.5 "구현 후 검증" 항목 (RULE-14)

---

## [3] GT REFERENCE — 참조 Ground Truth

| GT | 파일 경로 | 용도 |
|----|----------|------|
| **GT-5** | `D:\VAMOS\04. 구현단계\v13_results\phase4_v9\gt\v9_implementability_checklist.json` | 구현 가능성 체크리스트 (SOT에서 도출) |

**GT-5 핵심 구조**:

### AI 프롬프트 체크리스트 (V0/V2/V3용, 총 12개 프롬프트)

| # | 필수 항목 | 설명 | PASS 기준 |
|---|----------|------|----------|
| C-1 | 파일 경로 | 생성/수정할 파일의 절대 경로 | 1개 이상의 구체적 파일 경로 명시 |
| C-2 | 입출력 스키마 | 함수/클래스의 입력과 출력 타입 | 주요 함수의 파라미터/리턴 타입 기술 |
| C-3 | 의존성 | import할 모듈/패키지 목록 | import 대상 명시 또는 SOT 참조 |
| C-4 | 설정값 | config에서 읽어야 할 키와 기본값 | config 키 명시 또는 PHASE_B4 참조 |
| C-5 | SOT 참조 | 구현 근거가 되는 SOT 문서와 섹션 | D2.0-XX §N 형태의 참조 1건 이상 |
| C-6 | 성공 기준 | 테스트/검증 방법 (Stage Gate 연결) | Stage Gate 항목과 대응 관계 존재 |
| C-7 | LOCK 제약 | 해당 구현에 적용되는 LOCK/FREEZE 값 | LOCK 값 명시 또는 LOCK 미적용 표기 |

### V1 테이블 체크리스트 (V1 Phase 1~6용, 77행)

| # | 필수 항목 | 설명 | PASS 기준 |
|---|----------|------|----------|
| V1-1 | 모듈 ID + 파일명 | 테이블에 파일명 칼럼 존재 여부 | Phase 1: 6열 구조 (파일명 O), Phase 2~6: 4열 구조 (파일명 X -> FAIL) |
| V1-2 | 구현 내용 구체성 | 1줄 설명만으로 구현 가능한가 | "~를 구현" 수준이면 FAIL, 구체적 기술이면 PASS |
| V1-3 | SOT 참조 | 산출물 참조 칼럼에 구체적 문서+섹션 | D2.0-XX 형태의 참조 존재 |
| V1-4 | LOCK 제약 명시 | 해당 모듈에 적용되는 LOCK 값 기재 | LOCK 값 칼럼 존재 또는 본문 내 명시 |

---

## [4] RULES — 적용 방어 규칙

| RULE | 규칙 요약 | 적용 이유 |
|------|----------|----------|
| **RULE-2** | V0/V1/V2/V3 범위 한정자 먼저 확인 | V1 구조적 한계를 V0/V2/V3와 동일 기준으로 판정 금지 |
| **RULE-4** | MISSING 판정 전 상위 LOCK/FREEZE 계층에서 간접 커버 확인 | 개념적 커버와 완전 부재 구분 |
| **RULE-5** | 요약 테이블 vs 전체 열거, 약칭 vs 풀네임은 구조적 차이 | V1 테이블의 축약된 기술을 오류로 오판 금지 |
| **RULE-8** | `~` 근사치 +-20% 허용, LOCK/FREEZE만 정확 매칭 | 구현 가능성 판단 시 수치 정밀도 구분 |
| **RULE-9** | HTML 주석은 의도적 기록, 허용 목록 자동 PASS | SC 항목의 의도적 차이 보호 |
| **RULE-11** | §6 포함 필수 | §6 고유 정의의 구현 가능성 검증 |
| **RULE-14** | v9 범위 = 문서 정합성. 코드 동작 -> SKIP | 성능/보안 동작 검증 제외 |

---

## [5] ALLOWLIST — 허용 목록

| 항목 | 허용 사유 |
|------|----------|
| V1 Phase 2~6 파일 경로 미명시 | V1 구조적 한계 (테이블 형식). severity=MEDIUM, BLOCKER 아님 |
| V1 AI 프롬프트 부재 | V1은 테이블만 제공. severity=LOW, BLOCKER 아님 |
| SC-01~SC-12 | 의도적 SOURCE_CONFLICT 12건. 채택된 값이 프롬프트에 반영되었으면 PASS |

---

## [6] CHECK ITEMS — 구체적 검증 항목

### [C-1] V0 AI 프롬프트 6개 전수 검증
V0-STEP-1 ~ STEP-6의 각 AI 프롬프트 블록에 C-1~C-7 체크리스트 전수 적용.

**절차**:
1. PART2 §2에서 6개 AI 프롬프트 블록 위치 식별
2. 각 프롬프트에 대해 C-1~C-7 항목 점검:
   - C-1 (파일 경로): 프롬프트 내에 생성할 파일 경로가 명시되어 있는가?
   - C-2 (입출력 스키마): 주요 함수/클래스의 시그니처가 기술되어 있는가?
   - C-3 (의존성): import 대상이 명시되어 있는가?
   - C-4 (설정값): config 키가 언급되어 있는가? (PHASE_B4 참조도 인정)
   - C-5 (SOT 참조): D2.0-XX §N 형태의 참조가 있는가?
   - C-6 (성공 기준): 해당 STEP의 Stage Gate와 대응되는가?
   - C-7 (LOCK 제약): 적용 가능한 LOCK/FREEZE 값이 명시되어 있는가?
3. 각 체크 항목의 결과: PASS / FAIL

**예시 검증 (V0-STEP-4)**:
- "LangGraph 5-Phase 구현" — 노드 이름, 엣지 조건, StateGraph 키가 명시되어 있는가?
- C-2: IntentFrame, EvidencePack의 필드 정의가 프롬프트에 포함되는가?

### [C-2] V1 테이블 77행 전수 검증
V1-Phase 1~6의 테이블 각 행에 V1-1~V1-4 체크리스트 적용.

**절차**:
1. PART2 §3에서 V1 Phase별 테이블 위치 식별:
   - Phase 1: 6열 테이블 (6행) + 5열 테이블 (11행) = 17행
   - Phase 2: ~12행
   - Phase 3: ~12행
   - Phase 4: ~12행
   - Phase 5: ~12행
   - Phase 6: ~12행
   총 ~77행
2. 각 행에 대해:
   - V1-1 (모듈 ID + 파일명): 파일명 칼럼 존재? Phase 1=O, Phase 2~6=X
   - V1-2 (구현 내용): 1줄 설명의 구체성 평가
   - V1-3 (SOT 참조): 산출물 참조 칼럼의 구체성
   - V1-4 (LOCK 제약): LOCK 값 기재 여부

**주의**: Phase 1의 6열 vs 5열 칼럼 비일관성은 별도 보고 (Phase -1H에서 확인 완료)

### [C-3] V2/V3 AI 프롬프트 6개 전수 검증
V2 Phase 1~3 + V3 Phase 1~3의 AI 프롬프트에 C-1~C-7 체크리스트 적용.

**절차**: C-1과 동일하되 V2/V3 고유 패턴 주의:
- V2: 마이그레이션 스크립트, COND 모듈, Docker 배포 패턴
- V3: Multi-Agent, SDAR 고도화, Cloud Library 패턴
- V2/V3에서 V1 산출물 참조 시: V1 산출물의 존재 확인 (관점 A와 연동)

### [C-4] §6 고유 정의 구현 충분성
§6의 13개 하위 섹션에 정의된 고유 구현 사양의 충분성 확인.

**절차**:
1. §6 각 섹션의 구현 정의 식별:
   - §6.1 UI/UX: State Machine 9-state, React 컴포넌트 ~44개 등
   - §6.2 Rust/Tauri: IPC 핸들러 72개, Tauri Command 등
   - §6.3 테스트: 테스트 전략 ~84개 항목
   - §6.4 CI/CD: yml 14개의 구성 상세
   - §6.5 보안: RBAC, PII 마스킹 등 15항목
   - §6.6 MCP: MCP 서버 7개
   - §6.7 Agent Teams: LOCK-AT 17건
   - §6.8 AI Investing: 51% Gate, Circuit Breaker
   - §6.9 SDAR: 5-Layer, 7-State, 5-Gate
   - §6.10 Cloud Library: 10-Layer, 5-Gate
   - §6.11 이벤트/로깅: EventTypeRegistry 123항목
   - §6.12 운영 결정: 2건
   - §6.13 작업량 요약 매트릭스
2. 각 정의에 대해:
   - 구현에 필요한 최소 명세가 포함되어 있는가?
   - §2-§5의 AI 프롬프트/테이블에서 이 정의를 참조하고 있는가?
   - 참조가 없다면: 구현 시 어디서 이 정의를 적용해야 하는지 모호 -> `MEDIUM`

### [C-5] V1 Phase 2~6 "파일 경로 미명시" 플래그
V1 Phase 2~6 구현 항목에 파일 경로가 없음을 플래그.

**절차**:
1. V1 Phase 2~6 각 행의 모듈명 확인
2. §6 파일 경로 또는 PHASE_B2에서 해당 모듈의 예상 파일 위치 추론 가능 여부 확인
3. 추론 가능: severity=MEDIUM ("§6/PHASE_B2에서 추론 가능")
4. 추론 불가: severity=HIGH ("파일 위치 전혀 불명")

### [C-6] V1 "실행 가이드/AI 프롬프트 부재" 플래그
V1이 V0/V2/V3와 달리 AI 프롬프트 블록이 없는 구조적 차이를 기록.

**절차**:
1. V0, V2, V3: 각 STEP/Phase에 AI 프롬프트 블록 존재 여부 확인 -> 있음
2. V1: AI 프롬프트 블록 존재 여부 확인 -> 없음, 테이블만
3. 이 차이를 정보 항목으로 기록
4. severity=LOW (V1 구조적 한계로 인한 것이며, 별도 실행 가이드 부재)

---

## [7] OUTPUT FORMAT — 결과 JSON 스키마

```json
{
  "perspective": "v9-C",
  "perspective_name": "구현 가능성",
  "timestamp": "2026-MM-DDTHH:mm:ssZ",
  "target_doc": "VAMOS_구현가이드_PART2_구현단계.md v20.4.0",
  "gt_version": "v9_implementability_checklist.json",
  "rules_applied": ["RULE-2", "RULE-4", "RULE-5", "RULE-8", "RULE-9", "RULE-11", "RULE-14"],

  "summary": {
    "total_checks": 0,
    "v0_prompts_checked": 6,
    "v1_rows_checked": 77,
    "v2v3_prompts_checked": 6,
    "s6_sections_checked": 13,
    "pass": 0,
    "real_error": 0,
    "false_positive": 0,
    "style_concern": 0,
    "out_of_scope": 0,
    "blocker": 0,
    "high": 0,
    "medium": 0,
    "low": 0
  },

  "checklist_results": {
    "v0_prompts": [
      {
        "stage": "V0-STEP-N",
        "line": 0,
        "c1_path": "PASS | FAIL",
        "c2_schema": "PASS | FAIL",
        "c3_dependency": "PASS | FAIL",
        "c4_config": "PASS | FAIL",
        "c5_sot_ref": "PASS | FAIL",
        "c6_success": "PASS | FAIL",
        "c7_lock": "PASS | FAIL",
        "overall": "PASS | PARTIAL | FAIL",
        "missing_items": ["C-N"],
        "notes": ""
      }
    ],
    "v1_rows": [
      {
        "phase": "V1-Phase-N",
        "row": 0,
        "module_id": "",
        "line": 0,
        "v1_1_file": "PASS | FAIL",
        "v1_2_specificity": "PASS | FAIL",
        "v1_3_sot_ref": "PASS | FAIL",
        "v1_4_lock": "PASS | FAIL",
        "overall": "PASS | PARTIAL | FAIL"
      }
    ],
    "v2v3_prompts": [],
    "s6_sections": []
  },

  "findings": [
    {
      "id": "C-xxx-nnn",
      "check_item": "C-1 | C-2 | C-3 | C-4 | C-5 | C-6",
      "stage": "V0-STEP-N | V1-Phase-N | V2-Phase-N | V3-Phase-N | §6.N",
      "line": 0,
      "checklist_item": "C-1~C-7 | V1-1~V1-4",
      "description": "발견 내용 상세 기술",
      "expected": "체크리스트 기준",
      "actual": "PART2 실제 상태",
      "severity": "BLOCKER | HIGH | MEDIUM | LOW",
      "classification": "REAL_ERROR | FALSE_POSITIVE | STYLE_CONCERN | OUT_OF_SCOPE",
      "rule_applied": "RULE-N (해당 시)"
    }
  ]
}
```

---

## [8] SEVERITY — 판정 기준

| 등급 | 기준 | 이 관점의 예시 |
|------|------|--------------|
| **BLOCKER** | 핵심 파라미터 누락으로 구현 불가 | StateGraph 키 누락, 필수 스키마 미정의, 핵심 함수 시그니처 부재 |
| **HIGH** | SOT 참조 없이 모호한 명세 | "~를 구현하라" 수준의 기술, SOT 참조 0건, V1 행에서 구현 내용 완전 모호 |
| **MEDIUM** | 파일 경로 미명시 (추론 가능) | V1 Phase 2~6 파일 경로 없음 (§6/PHASE_B2에서 추론 가능) |
| **LOW** | 실행 가이드 부재 (구조적 한계) | V1 AI 프롬프트 부재, config 키 미명시 (PHASE_B4에서 추론 가능) |

---

## 실행 지시

1. **분할 실행 권장** (Phase 1 Wave 3에서 C-1~C-5로 분할):
   - C-1: V0 (STEP-1~6, line 59~1375)
   - C-2: V1 (Phase 1~6, line 1377~1711)
   - C-3: V2 (Phase 1~3, line 1713~2099) + V3 (Phase 1~3, line 2101~2697)
   - C-4: §6 (line 2699~3562)
   - C-5+C-6: V1 플래그 (C-2 실행 시 병행)
2. 체크리스트 항목별 PASS/FAIL을 먼저 집계한 후, FAIL 항목만 findings에 상세 기록
3. RULE-2 주의: V1 체크리스트(V1-1~V1-4)와 V0/V2/V3 체크리스트(C-1~C-7) 구분 적용
4. RULE-4 주의: C-4(설정값) FAIL 판정 전 상위 LOCK/FREEZE에서 간접 커버 확인
5. RULE-5 주의: V1 테이블의 축약 기술을 자동 FAIL로 판정하지 않음
6. **/cross-match** 스킬을 활용하여 체크리스트-프롬프트 간 교차 매칭 검증을 수행할 것
