# v9-A: 의존성 순서 검증 프롬프트

> **v13 Phase 4 재실행 — 세션 24 프롬프트 갱신**
> 원본: `v9_results/phase0/v9_prompt_A_dependency.md`
> 갱신 사유: GT 경로를 `phase4_v9/gt/`로 변경, v13 enhanced skill 참조 추가

> **Pipeline**: VAMOS v9.0.0 (v13 Phase 4 재실행)
> **관점 ID**: v9-A (Dependency Order)
> **작성일**: 2026-03-07 (갱신: 2026-03-22)
> **대상 문서**: `VAMOS_구현가이드_PART2_구현단계.md` v20.4.0 (3,807줄)

---

## v13 Enhanced Skill 참조

Wave 실행 시 아래 스킬을 활용하여 검증 정확도를 높인다:

- **/symbolic-verify** — 의존성 순서의 기호적(symbolic) 검증. DAG 구성, 순환 검출, 전제 산출물 매칭에 사용

---

## [1] HEADER

```
v9 SCOPE HEADER — Phase -1I 산출물
> v9 SCOPE: 문서 정합성/완전성/구현 가능성/수량 일관성/경로 정합성/의존성 순서/외부 의존성
> BOUNDARY: §7.5 중 "문서 검증 가능" 태그 항목만 범위 내
> OUT OF SCOPE: 코드 동작 검증, 성능 벤치마크, 보안 침투 테스트, 런타임 행위
> RULE-14: §7.5 "구현 후 검증" 항목 검출 시 → OUT_OF_SCOPE (FN 아님)
```

**관점**: v9-A — 의존성 순서 (Dependency Order)
**핵심 질문**: STEP N이 STEP N+2의 산출물을 전제하고 있지 않은가?
**검출 대상**: 순환 의존성, 전제 산출물 미생성, 병렬 vs 순차 모순

---

## [2] SCOPE — 검증 대상 범위

**포함 범위**:
- §2 V0 (line 59~1375): 6 STEP (STEP-1 ~ STEP-6)
- §3 V1 (line 1377~1711): 6 Phase (Phase 1 ~ Phase 6)
- §4 V2 (line 1713~2099): 3 Phase (Phase 1 ~ Phase 3)
- §5 V3 (line 2101~2697): 3 Phase (Phase 1 ~ Phase 3)
- §6 횡단 상세 (line 2699~3562): 13개 하위 섹션 (§6.1~§6.13)
- §7.1~§7.4 GO/NO-GO 검증 (line 3564~3700)

**제외 범위**:
- 변경 이력 (line 3777~3807) — RULE-3, Phase -1F 확정
- §7.5 크로스컷 검토 중 "구현 후 검증" 항목 — RULE-14

---

## [3] GT REFERENCE — 참조 Ground Truth

| GT | 파일 경로 | 용도 |
|----|----------|------|
| **GT-2** | `D:\VAMOS\04. 구현단계\v13_results\phase4_v9\gt\gt2_artifact_chain.json` | 18 Stage별 inputs/outputs/gate_conditions + 병렬 관계 + 횡단 의존성 |

**GT-2 핵심 구조**:
- `stages`: 18개 Stage별 `inputs`, `outputs`, `gate_conditions`, `gate_count`, `next_stage`
- `cross_section_dependencies`: §6 정의 → Stage 매핑 (횡단 의존성)
- `parallel_relations`: 병렬 실행 허용 패턴 (예: V1-Phase 6)
- `go_nogo_mapping`: 62개 GO/NO-GO 항목 ↔ Stage Gate 매핑

**추가 참조**:
- `D:\VAMOS\04. 구현단계\v13_results\phase4_v9\gt\v9_gate_mapping.json` — [-1E] GO/NO-GO ↔ Stage Gate 관계
- `D:\VAMOS\04. 구현단계\v13_results\phase4_v9\gt\v9_cross_section_index.json` — [-1D] §6-§7 교차 인덱스
- `D:\VAMOS\04. 구현단계\v13_results\phase4_v9\gt\v9_dependency_registry.json` — GT-4 (외부 의존성, F관점 참조용)

---

## [4] RULES — 적용 방어 규칙

| RULE | 규칙 요약 | 적용 이유 |
|------|----------|----------|
| **RULE-1** | `section.key` 정규화 전체 경로 사용. 부분 문자열 매칭 금지 | Stage 간 산출물 비교 시 정확 매칭 |
| **RULE-2** | V0/V1/V2/V3 범위 한정자 먼저 확인. V2 전용 항목을 V1 누락으로 판정 금지 | 의존성 검증 시 V 범위 구분 필수 |
| **RULE-3** | changelog, STEP7 보강(K-xxx), 인라인 주석은 불일치 검출 대상에서 제외 | line 3777-3807 제외 |
| **RULE-7** | 비선형 의존성(병렬, 조건부) 별도 분류. "V1-Phase 6: Phase 3-5와 병렬" 패턴은 허용. 병렬 관계를 순환 의존성으로 오판 금지 | V1-P6 병렬 패턴 보호 |
| **RULE-9** | HTML 주석(`<!-- NOTE -->`, `<!-- SOURCE_CONFLICT -->`)은 의도적 기록. 허용 목록 등록 항목은 자동 PASS | SC-01~SC-12 의도적 차이 보호 |
| **RULE-11** | 검증 범위에 §6(13개 하위 섹션) + §7(6개 하위 섹션) 포함 필수 | §6 횡단 의존성 누락 방지 |
| **RULE-14** | v9 범위 = 문서 내부 정합성. §7.5 "코드 동작 검증" 항목 → SKIP | 코드 레벨 검증 배제 |

---

## [5] ALLOWLIST — 허용 목록

**출처**: `D:\VAMOS\04. 구현단계\v13_results\phase4_v9\gt\v9_allowlist.json`

의존성 순서 관점에서 특별히 허용하는 패턴:

| 항목 | 허용 사유 |
|------|----------|
| V1-Phase 6 병렬 실행 | `parallel_with: ["V1-P3", "V1-P4", "V1-P5"]`, `validate_after: "V1-P5"`. 작업은 Phase 3 시작 후 병행 가능, 검증/완료 선언은 Phase 5 완료 후 |
| SC-01 (V0 활성 모듈 5개 vs 6개) | 5개 채택 확정. I-4 제외는 의도적 |
| SC-04 (메모리 4계층 LOCK) | L4 Archive는 V2+ 확장 옵션. V0/V1에서 L4 참조 없음은 오류 아님 |

---

## [6] CHECK ITEMS — 구체적 검증 항목

### [A-1] 순방향 의존성 검증
각 Stage의 `inputs`가 **이전 Stage**의 `outputs`에 포함되는지 확인.

**절차**:
1. GT-2의 `stages` 배열을 순서대로 순회
2. Stage N의 각 `input` 항목에 대해:
   - Stage 1 ~ Stage N-1의 `outputs` 합집합에 해당 항목이 존재하는가?
   - 존재하지 않으면: `REAL_ERROR` (전제 산출물 미생성)
3. 최초 Stage (V0-STEP-1)의 inputs는 외부 전제조건이므로 별도 처리

**검증 대상**: 18개 Stage x 평균 4~8개 inputs = ~90~144건

### [A-2] 순환 의존성 검출
방향 그래프(DAG) 기반 순환 검출.

**절차**:
1. 18개 Stage를 노드로, `inputs`->`outputs` 관계를 엣지로 방향 그래프 구성
2. DFS 기반 사이클 검출 수행
3. 발견된 사이클: `BLOCKER`

**예외**: RULE-7에 의해 병렬 관계(`parallel_with`)는 사이클로 판정하지 않음

### [A-3] 전환 조건(Gate) 구현 매칭
전환 조건의 항목이 해당 Stage에서 실제로 구현(outputs)되는지 확인.

**절차**:
1. 각 Stage의 `gate_conditions` 항목을 순회
2. 해당 항목이 동일 Stage의 `outputs`에 의미적으로 대응되는가?
3. Gate 항목이 outputs에 대응물 없으면: 해당 Gate가 이전 Stage outputs로 커버되는지 확인
4. 어디에서도 커버되지 않는 Gate: `HIGH`

### [A-4] §6 횡단 의존성 참조 가능성
§6의 정의(UI State Machine, LOCK-AT, SDAR 등)가 해당 Stage 이전에 참조 가능한지 확인.

**절차**:
1. GT-2의 `cross_section_dependencies` 항목 순회
2. 각 §6 정의가 의존하는 Stage보다 **먼저** 문서에 정의되어 있는가?
3. §6은 §2-§5 이후에 위치하므로 "문서 순서"가 아닌 "논리적 참조 가능성" 판단:
   - §6 정의는 모든 Stage에서 참조 가능 (§6은 횡단 참조 영역)
   - 단, §6 정의가 특정 Stage의 산출물에 의존한다면 그 Stage 완료 후에만 유효
4. 참조 불가 케이스: `HIGH`

**GT-2 횡단 의존성 매핑 참조**:
| §6 정의 | 의존하는 Stage | 의존 유형 |
|---------|--------------|----------|
| §6.1.6 UI State Machine 9-state | V1-Phase 4 | Phase 4가 구현 전제로 참조 |
| §6.7 LOCK-AT 17건 | V1-Phase 3, V2-Phase 3 | Agent 구현이 이 제약을 준수 |
| §6.9 SDAR 5-Layer/7-State/5-Gate | V2-Phase 2~3 | SDAR 구현 아키텍처 전제 |
| §6.10 Cloud Library 10-Layer/5-Gate | V2-Phase 3 | Cloud Library 구현 전제 |
| §6.8 AI Investing 51% Gate/CB | V1-Phase 6 | AI Investing 구현 전제 |
| §6.11 EventTypeRegistry 123항목 | V1-Phase 1+ | 이벤트 등록 전제 |

### [A-5] 병렬 패턴 검증
V1-Phase 6 병렬 패턴이 RULE-7 허용 패턴과 일치하는지 확인.

**절차**:
1. PART2에서 V1-Phase 6의 "병렬" 기술 위치 식별
2. GT-2의 `parallel_relations`와 대조:
   - `parallel_with: ["V1-P3", "V1-P4", "V1-P5"]`
   - `validate_after: "V1-P5"`
3. PART2 기술과 GT-2 정의가 일치하면: `PASS`
4. 불일치 시: `MEDIUM` (문서 내 모호성)
5. 다른 Stage에 미등록 병렬 패턴이 있는지 확인 -> 미등록 병렬: `HIGH`

### [A-6] GO/NO-GO UNIQUE 항목 실행 가능성
GO/NO-GO 항목 중 UNIQUE 유형(Stage Gate에 매핑되지 않는 항목)이 실제로 해당 버전 내에서 수행 가능한지 확인.

**절차**:
1. GT-2의 `go_nogo_mapping`에서 `type: "UNIQUE"` 항목 필터
2. 각 UNIQUE 항목이:
   - 해당 버전(V0/V1/V2/V3)의 Stage 범위 내에서 구현 가능한가?
   - 이전 버전의 산출물을 전제로 하는가? (전제 존재 확인)
   - 문서 작업(예: PLAN-2.0 표기)인 경우 별도 분류
3. 구현 불가능한 UNIQUE: `HIGH`
4. 문서 작업 UNIQUE: `PASS` (v9 범위 내 추가 검증 불필요)

---

## [7] OUTPUT FORMAT — 결과 JSON 스키마

```json
{
  "perspective": "v9-A",
  "perspective_name": "의존성 순서",
  "timestamp": "2026-MM-DDTHH:mm:ssZ",
  "target_doc": "VAMOS_구현가이드_PART2_구현단계.md v20.4.0",
  "gt_version": "gt2_artifact_chain.json",
  "rules_applied": ["RULE-1", "RULE-2", "RULE-3", "RULE-7", "RULE-9", "RULE-11", "RULE-14"],

  "summary": {
    "total_checks": 0,
    "pass": 0,
    "real_error": 0,
    "false_positive": 0,
    "out_of_scope": 0,
    "blocker": 0,
    "high": 0,
    "medium": 0,
    "low": 0
  },

  "findings": [
    {
      "id": "A-xxx-nnn",
      "check_item": "A-1 | A-2 | A-3 | A-4 | A-5 | A-6",
      "stage": "V0-STEP-N | V1-Phase-N | ...",
      "line": 0,
      "description": "발견 내용 상세 기술",
      "expected": "GT-2 기준 예상 값/상태",
      "actual": "PART2 실제 값/상태",
      "severity": "BLOCKER | HIGH | MEDIUM | LOW",
      "classification": "REAL_ERROR | FALSE_POSITIVE | STYLE_CONCERN | OUT_OF_SCOPE",
      "rule_applied": "RULE-N (해당 시)",
      "evidence": "근거 인용 (PART2 줄 번호 + GT-2 항목)"
    }
  ],

  "dag_analysis": {
    "total_nodes": 18,
    "total_edges": 0,
    "cycles_detected": [],
    "parallel_relations": [],
    "longest_path": []
  }
}
```

---

## [8] SEVERITY — 판정 기준

| 등급 | 기준 | 이 관점의 예시 |
|------|------|--------------|
| **BLOCKER** | 구현 불가 또는 런타임 오류 | 순환 의존성 발견 (A-2), 전제 산출물 완전 미생성 (A-1) |
| **HIGH** | 구현은 가능하나 결과가 SOT와 불일치 | Gate 항목이 어떤 Stage에서도 커버 안 됨 (A-3), §6 횡단 참조 불가 (A-4), 미등록 병렬 패턴 (A-5), UNIQUE 항목 구현 불가 (A-6) |
| **MEDIUM** | 구현에 영향은 적으나 혼란 유발 | 병렬 패턴 기술 모호 (A-5), Gate 항목과 outputs 간 의미적 대응 불명확 (A-3) |
| **LOW** | 미관/일관성 문제 | Stage 간 inputs/outputs 표기 불통일 (A-1), 문서 작업 UNIQUE 항목 미기술 (A-6) |

---

## 실행 지시

1. PART2 §2-§5를 순서대로 읽으며 18개 Stage의 inputs/outputs/gate_conditions를 GT-2와 대조
2. A-1 -> A-2 -> A-3 순서로 검증 (A-1이 A-2의 입력, A-2가 A-3의 전제)
3. A-4, A-5, A-6은 A-1~A-3과 독립적으로 병렬 실행 가능
4. 모든 findings를 위 JSON 스키마에 맞춰 출력
5. RULE-7 주의: V1-Phase 6 병렬 패턴을 순환 의존성으로 오판하지 않을 것
6. RULE-2 주의: V2 전용 산출물이 V1 Stage의 input으로 나타나면 V 범위 확인 후 판정
7. **/symbolic-verify** 스킬을 활용하여 DAG 구성 및 순환 검출의 기호적 검증을 수행할 것
