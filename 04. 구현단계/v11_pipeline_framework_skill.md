# VAMOS v11 Pipeline Framework Skill (Deterministic)

> **버전**: v2.6.0-FRAMEWORK — 6차 ABD-1~8 사전 검증 결과 반영 (5건)
> **작성일**: 2026-03-12
> **입력**: v11_gap_analysis_skill.md v2.3.0 (26개 GAP, FROZEN)
> **목적**: GAP-01~25(PART2 대상)의 검증 실행 계획 확정. GAP-26(ABD)은 본 Framework에 대한 외부 사전 검증으로 별도 수행.
> **원칙**: 동일 입력(26개 GAP + PART2 v24.0.0 + v6~v10 자산)에 대해 항상 동일한 실행 계획을 생성
> **1차 검증 반영**: I-01~X-04 (22건)
> **2차 검증 반영**: F-01(classified_issues 산출물 명시), F-02(phase1_summary 생성 단계 추가), F-03(checkpoint 산출물 명시)
> **4차 검증 반영**: BP-01~BP-15 (원본 보호 프로토콜 + 완료조건 12→14개 + 디렉토리 구조 확장)
> **5차 반영**: GAP-26(ABD-1~8) 역할 재정의 — Framework 내부 실행이 아닌, GAP Analysis Skill 에이전트의 외부 사전 검증으로 분리
> **6차 반영**: ABD-1~8 사전 검증 결과 5건 반영 (실패처리/입력경로/운영안전/BP결번/버전참조)
> **GAP-26 사전 검증**: ABD-1~8 실행 완료 → ISSUE 5건 반영 완료 → FROZEN

---

# 1. v11 포지션 (v6~v10 대비)

```
v6  구조 무결성      PART2 ↔ 마크다운 규칙         (외부 기준: 마크다운 스펙)
v7  SOT 교차         PART2 ↔ SRC 41개              (외부 기준: 원본 문서)
v8  4-Dim 통합       PART2 ↔ SRC 43개 + 구현실현    (외부 기준: 원본 + 기술 지식)
v9  구현 준비         PART2 ↔ SRC + 외부 의존성      (외부 기준: 원본 + 패키지/서비스)
v10 Feature Coverage  SRC 기능 → PART2 매핑          (외부 기준: 원본 기능 목록)
────────────────────────────────────────────────────────────
v11 내부 전수 검토    PART2 ↔ PART2 자기 자신        (내부 기준: PART2 단독)
```

**핵심 차별점**: v11은 **외부 SRC를 참조하지 않는다**.
단, GAP-15/16/17은 **외부 기술 지식(패키지 존재/호환성/가격)**을 참조하며 이는 명시적 예외이다. [L-01]
PART2 ~4,400줄을 하나의 독립 문서로 놓고, 내부 논리/일관성/품질/실행가능성을 전수 검증한다.
**v24.0.0 변경분(~107줄)은 v10(v23.0.0 대상) 이후 미검증 상태**이므로 전 Agent가 인식해야 한다. [P-01]

---

# 2. 전체 Phase 구조

```
Phase 0    내부 인덱스 구축 (결정론적)
  ├── 0-A: 섹션 구조 맵
  ├── 0-B: 내부 참조 맵
  ├── 0-C: 수치 레지스트리 (통화/퍼센트 포함)                          [I-02]
  ├── 0-D: 용어 사전
  ├── 0-E: 프롬프트 인벤토리
  ├── 0-F: v6~v10 재활용 데이터 추출 (v23→v24 delta 포함)             [M-01]
  └── 0-G: 코드블록 인벤토리                                          [I-01]
  ↓ 사용자 승인 (Phase 0 실패 시 해당 인덱스 재구축 후 진행)          [X-04]
  ※ GAP-26(ABD)은 본 Framework 사전 검증으로 Phase 0 시작 전 완료됨    [ABD]
  ※ 전 Phase 세션 중단 시 BP-9/BP-10으로 중단 지점 복구               [ABD-6]
Phase 1    25개 GAP 검증 (5 Wave × 14 에이전트)                       [O-01]
  ├── Wave 1: 결정론적 자기 대조 (Agent 1~3)     ← GAP-05,06,07,08,10
  ├── Wave 2: 구조/매핑 교차 (Agent 4~6)          ← GAP-01,02,03,04,09
  ├── Wave 3: 프롬프트 전수 (Agent 7~9)           ← GAP-11,12,13,14    [A-02]
  ├── Wave 4: 심화 검증 (Agent 10~13)             ← GAP-15~22,25
  └── Wave 5: 사용성 종합 (Agent 14)              ← GAP-23,24
  ↓ 사용자 승인
Phase 1.5  적대적 재검증
  └── Agent 15: Wave 1~5 발견사항 전수 재조사 + v8/v9 RULE 1~14 적용  [R-01]
  ↓ 사용자 승인
Phase 2    수정 + 재검증 (원본 보호 프로토콜 BP-1~15 적용)             [BP]
  ├── BP:  원본 백업 + 무결성 기록 (Phase 2 시작 전 1회)               [BP-1~3]
  ├── 2-A: 분류 + Ripple Map(이중검증) + 수정 순서 결정               [PR-02][BP-13]
  ├── 2-B: PART2 수정 반영 (6단계 고정순서: 스냅샷→기록→수정→검증→감지→기록) [BP-12]
  └── 2-C: Phase 0 재실행 + Checkpoint (14개 완료조건)                [C-01][BP]
```

---

# 3. Phase 0 — 내부 인덱스 구축 (1~2세션)

> **목적**: PART2를 기계적으로 파싱하여 Phase 1 에이전트에게 공급할 Ground Truth를 구축
> **원칙**: SRC 참조 없음. PART2 단독 파싱. (0-F만 v6~v10 산출물 참조)
> **실패 처리**: 개별 인덱스 구축 실패 시 해당 인덱스만 재시도. 3회 실패 시 수동 개입 요청. [X-04]
> **대용량 대비**: PART2 ~4,400줄 파싱 시 컨텍스트 제한 대비 섹션별 청킹 허용 (§1~§7 단위). [ABD-6]

## 0-A: 섹션 구조 맵 (Section Structure Map)

```
입력:  PART2 v24.0.0 전문
       경로: D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md      [X-01]
작업:
  1. 모든 heading(#~####)의 (행번호, depth, 제목텍스트) 추출
  2. 각 섹션의 시작행~종료행 범위 매핑
  3. 하위 구조 요소 식별: [작업내용/산출물참조/실행가이드/AI프롬프트/규칙/참조SOT/완료검증]
  4. 섹션별 하위 구조 존재/부재 매트릭스 생성
산출물: D:\VAMOS\04. 구현단계\v11_results\phase0\v11_section_map.json    [X-03]
용도:  GAP-01(서술흐름), GAP-02(구조균일성)
```

## 0-B: 내부 참조 맵 (Internal Reference Map)

```
입력:  PART2 v24.0.0 전문
       경로: D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md
작업:
  1. 본문 내 "§N.N" 패턴 전수 추출 → (출현행, 참조대상섹션)
  2. "STEP-N", "Phase N", "V0~V3" 등 교차 참조 패턴 추출
  3. §6.x 참조 → §6.x 실제 존재 여부 대조
  4. §7 체크리스트 항목 → §2~§6 대응 섹션 매핑
  5. HTML 주석 내 참조 (SOURCE_CONFLICT, XREF, NOTE, PATCH) 전수 추출
산출물: D:\VAMOS\04. 구현단계\v11_results\phase0\v11_reference_map.json
용도:  GAP-03(§6↔§2~§5), GAP-04(§7↔§2~§6), GAP-10(정본우선순위)
```

## 0-C: 수치 레지스트리 (Numeric Registry)

```
입력:  PART2 v24.0.0 전문
       경로: D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md
작업:
  1. 모든 수치 출현 추출: (행번호, 수치, 컨텍스트키워드, LOCK여부, ~근사치여부)
  2. 통화 값 추출: $N, ₩N, N원/달러 패턴 → (행번호, 금액, 통화단위, 대상서비스)  [I-02]
  3. 퍼센트 값 추출: N%, ~N% 패턴 → (행번호, 비율, 대상지표)                     [I-02]
  4. 동일 키워드에 대한 수치를 그룹화하여 자기 일치 검증
  5. §1.1 모듈 수 표 ↔ §2~§5 모듈 나열 수 대조 준비
  6. §6.13 작업량 표 ↔ §6.1~§6.12 개별 수치 대조 준비
  7. §7 GO/NO-GO 헤더 항목수 ↔ 실제 체크리스트 행 수
산출물: D:\VAMOS\04. 구현단계\v11_results\phase0\v11_numeric_registry.json
용도:  GAP-06(수치 자기일관), GAP-08(모듈활성화), GAP-17(비용모델)
```

## 0-D: 용어 사전 (Terminology Dictionary)

```
입력:  PART2 v24.0.0 전문
       경로: D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md
작업:
  1. 주요 용어의 모든 표기 변형 추출 (영문/한글/약칭/정식명)
     대상: 81개 모듈명, 5 Gate, 상태코드, 기술스택, 레지스트리명 등
  2. 첫 등장 행 + 정의 유무 + 이후 사용 패턴 매핑
  3. 동일 개념의 다른 표기를 그룹화 (예: SDAR / Self-Directed Adaptive Reasoning / I-25)
산출물: D:\VAMOS\04. 구현단계\v11_results\phase0\v11_terminology_dict.json
용도:  GAP-07(용어일관성), GAP-23(가독성)
```

## 0-E: 프롬프트 인벤토리 (Prompt Inventory)

```
입력:  PART2 v24.0.0 전문
       경로: D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md
작업:
  1. 모든 AI 프롬프트 블록 추출: (섹션, 시작행, 종료행, 줄수)
     §2 STEP 1~6: 6개 + §4 Phase 1~3: 3개 + §5 Phase 1~3: 3개 = 12개
  2. V1(§3)에 AI 프롬프트 부재 확인 + 대안 존재 여부
  3. 각 프롬프트의 하위 구조: [작업목표/규칙/참조SOT/코드블록/완료검증]
  4. 프롬프트 간 입출력 체인: STEP N 산출물 → STEP N+1 전제조건
  5. §1.3 공통규칙 vs 개별 프롬프트 "규칙" 섹션 텍스트 diff 준비
산출물: D:\VAMOS\04. 구현단계\v11_results\phase0\v11_prompt_inventory.json
용도:  GAP-11(자기완결), GAP-12(프롬프트↔테이블), GAP-13(연쇄의존), GAP-14(공통규칙)
```

## 0-F: v6~v10 재활용 데이터 추출

```
입력:  v8~v10 산출물 디렉토리
       v8: D:\VAMOS\04. 구현단계\v8_results\                             [X-01]
       v9: D:\VAMOS\04. 구현단계\v9_results\
       v10: D:\VAMOS\04. 구현단계\v10_results\
작업:
  1. v8 Phase 0 결과 (0-A~0-H) → 구조 무결성 현황 (최신 PART2 버전과 차이 확인)
  2. v9 GT-1(경로), GT-2(산출물체인), GT-3(수량) → Phase 1 참고자료
  3. v10 Feature Registry → §6 시스템별 상세 교차 검증 시 참고
  4. 각 산출물의 대상 PART2 버전 확인 (v20.4.0/v21.0.0/v23.0.0 vs 현재 v24.0.0)
     → 버전 차이가 있는 항목은 "참고만, 재검증 필수" 태깅
  5. v23.0.0→v24.0.0 변경분 delta 추출:                                  [M-01]
     - v10_checkpoint.md 기준 PART2 v23.0.0 행수(4,293) vs v24.0.0 행수(~4,400)
     - v24.0.0 변경이력 섹션에서 v24.0.0 항목의 변경 내역 추출
     - 변경된 행 범위 식별 → Phase 1 Agent 전원에게 "v24 delta zone" 으로 제공
산출물: D:\VAMOS\04. 구현단계\v11_results\phase0\v11_v6v10_reuse_index.json
용도:  전 Agent 참조 (신뢰하지 않되 참고)
```

## 0-G: 코드블록 인벤토리 (Codeblock Inventory) [I-01 — 신규]

```
입력:  PART2 v24.0.0 전문
       경로: D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md
작업:
  1. 모든 코드블록(``` ~ ```) 추출: (시작행, 종료행, 언어태그, 줄수)
  2. 언어별 분류: python, rust, typescript, toml, json, yaml, bash, 기타, 없음
  3. 각 코드블록의 소속 섹션/STEP/Phase 매핑
  4. import/use/require 문 추출 → 패키지 목록 사전 구축
  5. 코드블록 간 참조 관계 (동일 함수명/클래스명 출현) 식별
산출물: D:\VAMOS\04. 구현단계\v11_results\phase0\v11_codeblock_inventory.json
용도:  GAP-15(코드 실행가능성), GAP-16(의존성 호환성)
```

---

# 4. Phase 1 — 25개 GAP 검증 (5 Wave × 14 에이전트) [O-01]

## 4.1 Wave 설계 원칙

```
WAVE-RULE-1: Wave N의 산출물이 Wave N+1의 입력이 되는 경우에만 순차 실행.
             Wave 1~4는 Phase 0 산출물만 사용하므로 상호 독립, 병렬 실행 가능.  [W-01]
             단, Wave 5는 Wave 1~4의 ISSUE 요약을 입력으로 받아야 하므로 순차.   [W-02]
WAVE-RULE-2: 각 에이전트는 PART2 전문 + Phase 0 산출물 중 필요한 것만 수신.
WAVE-RULE-3: 에이전트는 SRC를 읽지 않는다.
             예외: Agent 10(GAP-15,16)과 Agent 11(GAP-17)은 외부 기술 지식 참조 허용.  [L-01]
WAVE-RULE-4: 각 에이전트 산출물은 고정 형식 (§4.3 출력 형식).
WAVE-RULE-5: 모든 에이전트는 0-F의 "v24 delta zone"을 인식하고,                 [P-02]
             해당 영역의 이슈에 [v24-DELTA] 태그를 부여한다.
WAVE-RULE-6: 에이전트 실행 실패 시 해당 에이전트만 재시도 (최대 3회).            [ABD-2]
             3회 실패 시 사용자에게 수동 개입 요청.
             다른 에이전트는 독립 실행 가능하므로 중단하지 않음.
WAVE-RULE-7: 에이전트 컨텍스트 오버플로 발생 시:                                [ABD-6]
             a) 현재까지의 부분 결과를 산출물로 저장
             b) 미완료 GAP 범위를 명시하여 사용자에게 보고
             c) 해당 범위만 별도 세션에서 재실행
```

## 4.2 에이전트 배정 매트릭스 (14개 검증 에이전트 + 1개 적대적 = 15개 총) [O-02]

### Wave 1: 결정론적 자기 대조 (3 에이전트, 병렬)

> **특성**: Phase 0 인덱스만으로 기계적 대조 가능. FP 최소화.

```
Agent 1: "수치+모듈" — GAP-06, GAP-08
  입력: v11_numeric_registry.json + v11_section_map.json
  PART2 범위: §1.1 + §2~§5(모듈 나열) + §6.13 + §7(항목수)
  작업:
    GAP-06: 수치 레지스트리 내 동일 키워드 그룹에서 불일치 추출
            (v6 0-B/0-E/0-H 커버 범위 제외 — 비-키워드/비-테이블 수치만)
    GAP-08: §1.1 모듈표 ↔ §2~§5 구현 모듈 1:1 대조
            + 테이블 열 간 논리적 정합성 (status=CORE인데 V1=OFF 등)
  검증 항목 수: 50~70건 (수치 그룹 30~45 + 모듈 매핑 20~25)              [N-01]

Agent 2: "용어+정본" — GAP-07, GAP-10
  입력: v11_terminology_dict.json + v11_reference_map.json
  PART2 범위: §1~§7 전체 (용어) + §7.5.4~§7.5.5 + 본문 HTML 주석
  작업:
    GAP-07: 용어 사전 내 동일 개념 그룹에서 표기 불일치 추출
    GAP-10: §7.5.5 인덱스 ↔ 본문 SOURCE_CONFLICT 주석 양방향 대조
            + 정본 우선순위 채택 일관성
            (v6 0-G 커버 범위 제외 — 주석 무결성/값 일치는 v6에서 검증)
  검증 항목 수: 60~90건 (주요 용어 50~65 + SOURCE_CONFLICT 10~25)        [N-01]

Agent 3: "변경이력" — GAP-05
  입력: v11_section_map.json + v11_v6v10_reuse_index.json (v24 delta)
  PART2 범위: 변경 이력 섹션 + §1~§7 전체 (키워드 검색)
  작업:
    GAP-05: 변경 이력 각 항목의 "추가/수정/삭제" 기록 → 본문에서 해당 내용 존재 확인
            + 버전 번호 연속성 검증
            + v23→v24 변경분(~107줄)이 v10 패치 200건과 정합하며
              새로운 불일치를 유발하지 않는지 [v24-DELTA] 집중 검증         [P-02]
  검증 항목 수: 35~50건 (변경이력 항목 25~35 + v24 delta 10~15)          [N-01]
```

### Wave 2: 구조/매핑 교차 (3 에이전트, 병렬)

> **특성**: 섹션 간 교차 대조. Wave 1 결과 불필요.

```
Agent 4: "서술흐름+균일성" — GAP-01, GAP-02
  입력: v11_section_map.json + PART2 v24.0.0 전문 (직접 읽기 필수)       [I-03]
  PART2 범위: §1~§7 전체 (특히 섹션 전환부 + 하위 구조)
  작업:
    GAP-01: §1→§2→...→§7 전환부에서 전방참조오류/톤불균형/중복 검출
            ※ 의미론적 판단이 필요하므로 PART2 원문 직접 읽기 필수         [I-03]
    GAP-02: §2(STEP 1~6) vs §3(Phase 1~6) vs §4(Phase 1~3) vs §5(Phase 1~3)
            하위 구조 균일성 매트릭스 → 부재 요소 식별
  검증 항목 수: 25~35건 (전환부 6 + 하위구조 매트릭스 18 + 불균형 1~11)  [N-01]

Agent 5: "§6↔§2~§5 양방향" — GAP-03
  입력: v11_reference_map.json + v11_section_map.json
  PART2 범위: §6.1~§6.13 ↔ §2~§5 전체
  작업:
    GAP-03: 순방향 (§2~§5에서 "§6.x 참조" → §6.x에 해당 내용 존재?)
            역방향 (§6.x의 항목 → §2~§5 어딘가에서 구현/참조되는가?)
            값 대조 (양쪽에 동일 수치가 있을 때 일치하는가?)
  검증 항목 수: 100~140건 (§6 13개 하위섹션 × 평균 8~11개 항목)         [N-01]

Agent 6: "§7+전환조건" — GAP-04, GAP-09
  입력: v11_reference_map.json + v11_section_map.json
  PART2 범위: §7.1~§7.6 ↔ §2~§6 + 18개 전환조건
  작업:
    GAP-04: §7 체크리스트 64건 → §2~§6 대응 구현 매핑
            + 역방향: §2~§6 LOCK/CORE 구현 → §7 체크리스트 존재 확인
            + §7.6 산출물 인덱스 파일명/줄수/참조 ↔ PART2 본문 일치 검증
    GAP-09: 18개 전환조건 각각에 대해 [구현항목 커버/과잉/모호/중복] 판정
  검증 항목 수: 85~115건 (GO/NO-GO 64 + §7.6 10~15 + 전환조건 18×1~2)  [N-01]
```

### Wave 3: 프롬프트 전수 (3 에이전트, 병렬) [A-02 — Agent 7→8→9로 재분배]

> **특성**: 12개 AI 프롬프트 집중 분석. Agent 7/8/9에 3개 GAP 균등 분배.

```
Agent 7: "프롬프트 자기완결" — GAP-11
  입력: v11_prompt_inventory.json + v11_section_map.json
  PART2 범위: 12개 AI프롬프트 + §1.3
  작업:
    GAP-11: 각 프롬프트의 자기완결성 점수 (5점 척도)
            평가 축: [참조필요도/모호지시수/전제명시수/Method혼재/코드블록자급]
  검증 항목 수: 55~65건 (프롬프트 12 × 5축 = 60)                        [N-01]

Agent 8: "프롬프트 커버리지+규칙" — GAP-12, GAP-14                       [A-02]
  입력: v11_prompt_inventory.json + v11_section_map.json
  PART2 범위: 12개 AI프롬프트 + §1.3 + 각 STEP/Phase 구현항목 테이블
  작업:
    GAP-12: 프롬프트 지시 ↔ 구현항목 테이블 1:1 매핑 → 미커버/초과 항목
    GAP-14: §1.3 공통규칙 11건 ↔ 개별 프롬프트 "규칙" 섹션 텍스트 diff → 불일치/누락
  검증 항목 수: 55~75건 (테이블매핑 ~30 + 공통규칙 11×12프롬프트 체크 ~25~45) [N-01]

Agent 9: "프롬프트 체인" — GAP-13                                        [A-02]
  입력: v11_prompt_inventory.json
  PART2 범위: §2 STEP 1→6 체인 + §4 Phase 1→3 체인 + §5 Phase 1→3 체인
  작업:
    GAP-13: STEP N 산출물 파일 목록 → STEP N+1 전제조건 파일 목록 → 불일치 식별
            3개 체인 × 각 연결점 분석
  검증 항목 수: 25~35건 (V0: 5연결 + V2: 2연결 + V3: 2연결 + 교차: ~16~26) [N-01]
```

### Wave 4: 심화 검증 (4 에이전트, 병렬)

> **특성**: 일부 GAP은 외부 기술 지식 필요. [L-01]

```
Agent 10: "코드+패키지" — GAP-15, GAP-16
  입력: v11_codeblock_inventory.json + PART2 코드블록 전체                [I-01]
  PART2 범위: §2 STEP 1~6 코드 + §4~§5 코드 + §6 코드
  작업:
    GAP-15: Python/Rust/TS 코드 블록 문법 검증 (import, 타입, async/await, Pydantic v2)
    GAP-16: pyproject.toml/Cargo.toml/package.json 버전 호환성 (웹 검색 허용)
  검증 항목 수: 40~60건 (코드블록 25~35 + 패키지 15~25)                  [N-01]
  ※ 예외적으로 외부 지식 참조 허용 (패키지 존재/호환성)                   [L-01]

Agent 11: "비용+타임라인" — GAP-17, GAP-18
  입력: v11_numeric_registry.json (비용/일정/통화/퍼센트 관련 수치)       [I-02]
  PART2 범위: §1 로드맵 + §2~§5 일정 + §6.8 비용 + §6.10 비용 + §6.13 작업량
              + §6.1~§6.12 개별 시스템 상세 (비용 언급 부분)              [L-02]
  작업:
    GAP-17: 버전별 비용 상한 vs 기술스택 실비용 추정 (웹 검색 허용)
    GAP-18: STEP/Phase별 작업량 vs 할당 기간 적정성 분석
  검증 항목 수: 20~30건 (비용 V1~V3: 8~12 + 타임라인 18 STEP/Phase: 12~18) [N-01]
  ※ 예외적으로 외부 지식 참조 허용 (API 가격, 인프라 비용)               [L-01]

Agent 12: "시스템설계" — GAP-19, GAP-20, GAP-21
  입력: v11_reference_map.json + v11_section_map.json
  PART2 범위: §2 STEP-4 + §3 Phase 3 + §6.1.6 + §6.5 + §6.9 + §6.11
              + §6.1~§6.12 (Gate/상태머신/에러 관련 전체)                 [L-02]
  작업:
    GAP-19: 3개 상태머신(S0~S8, UI 9-state, SDAR 7-state) 상호 매핑 + 전이조건 모순 검증
    GAP-20: 5 Gate 호출 지점 전수 추출 → 파이프라인 내 누락/중복 판정
    GAP-21: FailureCode 36건 + Fallback 23건 → 구현 기능별 커버리지 + escalation 경로
  검증 항목 수: 55~85건 (상태머신매핑 15~25 + Gate 15~25 + 에러경로 25~35) [N-01]

Agent 13: "보안+테스트" — GAP-22, GAP-25
  입력: v11_section_map.json
  PART2 범위: §6.3 + §6.5 + §6.5.1 + §6.7 LOCK-AT + §6.9 CATEGORY E + §7.5.2
  작업:
    GAP-22: 15개 보안항목 + AI보안체크리스트 → 위협 모델(STRIDE/OWASP) 매핑 → 미커버 위협
    GAP-25: §6.3 테스트 ~84건 + VAL-001~010 → §2~§5 구현항목 대조 → 미커버 테스트 영역
  검증 항목 수: 50~70건 (보안 20~30 + 테스트매핑 30~40)                  [N-01]
```

### Wave 5: 사용성 종합 (1 에이전트)

> **특성**: Wave 1~4 결과를 참고하여 문서 전체 사용성 평가.
> **의존성**: Wave 1~4의 ISSUE 요약(§4.3 형식)을 입력으로 수신해야 함. [W-02]

```
Agent 14: "가독성+운영" — GAP-23, GAP-24
  입력: v11_terminology_dict.json + Wave 1~4 발견 요약 (ISSUE 목록 전체)  [W-02]
  PART2 범위: §1~§7 전체
  작업:
    GAP-23: 미정의 용어 목록 + 깨진 참조 목록 + 가독성 이슈 (과도한 테이블, 중복, 진입 가이드 부재)
    GAP-24: 운영 관점 갭 (모니터링/백업/롤백/인시던트/로그 정책) 존재 여부
  검증 항목 수: 30~50건 (가독성 20~30 + 운영 10~20)                      [N-01]
  ※ Wave 1~4 완료 후 실행 (발견사항 참조 필요)
```

## 4.3 에이전트 출력 형식 (필수, 전 에이전트 동일)

```markdown
## [Agent N] v11 검증 결과
> **PART2 버전**: v24.0.0
> **에이전트 버전**: v2.0.0                                              [X-02]

### 담당 GAP
- GAP-XX: (관점명)
- GAP-YY: (관점명)

### 검사 통계
- 검사 항목 수: N건
- ISSUE: N건 / OK: N건 / N/A: N건

### 심각도 기준
- BLOCKER: 구현 진행 시 시스템 오동작 유발 또는 논리적 모순
- HIGH: 내부 불일치로 혼란 유발 (수정 필수)
- MEDIUM: 개선 권장 (품질 향상)
- LOW: 표기/포맷 수준 (선택적 수정)

### ISSUE 목록
| # | GAP | PART2행 | 이슈 내용 | 비교 대상(PART2 내) | 심각도 | v24-DELTA |
|---|-----|---------|----------|-------------------|--------|-----------|

### OK 샘플 (검증 완료 확인)
| # | GAP | PART2행 | 확인 내용 | 결과 |
```

## 4.4 Wave 의존성 다이어그램

```
Phase 0 산출물 (0-A ~ 0-G)
    │
    ├──→ Wave 1 (Agent 1,2,3)    ──┐
    ├──→ Wave 2 (Agent 4,5,6)    ──┤
    ├──→ Wave 3 (Agent 7,8,9)    ──┤── 모두 병렬 가능 (Phase 0만 의존)  [W-01]
    ├──→ Wave 4 (Agent 10,11,    ──┤
    │         12,13)               │
    │                              │
    │   Wave 1~4 ISSUE 요약 수집 ──┘
    │         │
    └─────────┤
              ↓
         Wave 5 (Agent 14)  ← Wave 1~4 ISSUE 전체를 입력으로 수신       [W-02]
              │
              ↓
         Phase 1 완료 보고 → v11_phase1_summary.md 생성                  [F-02]
```

**실행 최적화**: Wave 1~4는 Phase 0 산출물만 있으면 병렬 실행 가능.
Wave 5만 Wave 1~4 완료 후 순차 실행. Wave 내 에이전트도 모두 병렬.
**Phase 1 완료 시**: Agent 1~14 전원의 보고서를 취합하여 v11_phase1_summary.md 생성. [F-02]

---

# 5. Phase 1.5 — 적대적 재검증 (1세션)

```
Agent 15: "적대적 검증자"
  입력: phase1/ 디렉토리 14개 보고서 전체                                       [ABD-3]
        D:\VAMOS\04. 구현단계\v11_results\phase1\wave*_agent*.md (14개 파일)
        + D:\VAMOS\04. 구현단계\v11_results\phase1\v11_phase1_summary.md
  실패 처리: Agent 15 실패 시 재시도 최대 3회.                                  [ABD-2]
             3회 실패 시 Phase 1 ISSUE 목록을 사용자에게 직접 전달하여 수동 판정.
  작업:
    1. 모든 ISSUE를 3가지로 재판정:
       - REAL_ISSUE: 실제 내부 불일치/누락/오류
       - FALSE_POSITIVE: 의도적 차이, 허용 범위 내, 오판
       - NEEDS_CLARIFICATION: 의도적인지 판단 불가 → 사용자 확인 필요

    2. Spot-check (Wave별 OK 항목에서 최소 3건씩, 합계 최소 15건):
       - Agent가 "OK"로 보고한 항목을 직접 PART2에서 재확인
       - 오판율 산출 → 에이전트당 > 20%이면 해당 Agent 범위 전체 재검증

    3. FP 방어 규칙 — v8 RULE 1~6 + v9 RULE 7~14 계승:                  [R-01]

       [v8 계승]
       RULE-1:  ~근사치(~N)는 ±20% 허용
       RULE-2:  HTML 주석(NOTE/XREF/PATCH)은 의도적 기록 — 오류가 아님
       RULE-3:  Changelog 영역(변경이력 섹션)은 본문과 별도 컨텍스트
       RULE-4:  요약 vs 상세 표현 차이는 데이터 오류가 아님
       RULE-5:  "선택적(OPT/COND)" 항목은 부재가 오류가 아님
       RULE-6:  계획(PLAN) 표기와 구현(IMPL) 표기의 시제 차이 허용

       [v9 계승]
       RULE-7:  병렬 의존성(A∥B)에서 순서 차이는 오류가 아님
       RULE-8:  근사치 키워드("약", "정도", "~")가 있으면 정확 일치 불요
       RULE-9:  외부 패키지 버전은 검증 시점 기준 — 미래 변경 불가항력
       RULE-10: SOT 간 고의 차이(SOURCE_CONFLICT 주석 존재)는 오류가 아님
       RULE-11: 테이블 행 순서와 본문 서술 순서의 차이는 오류가 아님
       RULE-12: 섹션 깊이 1-level 차이(예: ####→###)는 v6가 커버
       RULE-13: 요약 표에서 생략된 OPT 항목은 누락이 아님
       RULE-14: V1 AI프롬프트 부재는 설계 결정 확인 후 판정

  산출물: D:\VAMOS\04. 구현단계\v11_results\phase15\v11_adversarial_report.md
```

---

# 6. 원본 보호 프로토콜 (BP-1 ~ BP-15)

> **목적**: Phase 2에서 PART2를 수정할 때 원본 유실/의도치 않은 변경을 원천 차단
> **적용 범위**: Phase 2 전 구간 (2-A ~ 2-C)

## 6.1 Phase 2 시작 전 — 원본 저장 (BP-1 ~ BP-3)

```
[사전 조건] 디스크 공간 확인:                                                  [ABD-6]
      v11_results/ 가용 공간 ≥ PART2 크기 × 20 (백업+스냅샷+diff+archive 여유)
      → 부족 시 사용자에게 경고 후 공간 확보 요청. 확보 전 Phase 2 진입 불가.

BP-1: PART2 v24.0.0 원본 복사 → 금고에 저장
      대상: D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md
      저장: D:\VAMOS\04. 구현단계\v11_results\phase2\v24_original_backup.md
      조건: Phase 2 시작 전 1회만 실행. 이후 절대 덮어쓰지 않음.

BP-2: 원본의 "지문"(무결성 정보) 기록
      저장: D:\VAMOS\04. 구현단계\v11_results\phase2\v24_integrity.json
      내용:
        {
          "source_file": "VAMOS_구현가이드_PART2_구현단계.md",
          "version": "v24.0.0",
          "total_lines": N,
          "sha256": "원본 해시값",
          "sections": [
            {"heading": "§1 ...", "start_line": N, "end_line": N, "line_count": N},
            ...전 섹션
          ]
        }

BP-3: 백업 무결성 확인
      백업 파일(BP-1)의 SHA256 ↔ 원본 SHA256(BP-2) 일치 여부 검증
      → 불일치 시 백업 재생성 (최대 3회, 3회 실패 시 수동 개입)
```

## 6.2 수정 1건마다 — 기록 남기기 (BP-4 ~ BP-8)

```
BP-4: 수정 직전 스냅샷 저장
      저장: D:\VAMOS\04. 구현단계\v11_results\phase2\snapshots\before_fix_NNN.md
      NNN = 수정 순번 (001, 002, ...)

BP-5: 변경 내용을 고정 포맷으로 기록 (diff)
      저장: D:\VAMOS\04. 구현단계\v11_results\phase2\diffs\fix_NNN.json
      포맷 (Edit 도구 old/new 쌍 — 역패치 시 old↔new 스왑만 하면 됨):
        {
          "fix_id": "FIX-NNN",
          "issue_ref": "REAL_ISSUE-XXX",
          "severity": "BLOCKER|HIGH|MEDIUM|LOW",
          "target_sections": ["§6.13", "§7.2"],
          "changes": [
            {"file_line": 1234, "old": "수정 전 텍스트", "new": "수정 후 텍스트"},
            {"file_line": 2345, "old": "수정 전 텍스트", "new": "수정 후 텍스트"}
          ]
        }

BP-6: 비의도 변경 감지 (Ripple Map 연동)
      수정 전 "변경 예정 섹션 목록"을 Ripple Map에서 추출
      → 해당 섹션 = EXPECTED (변동 허용)
      → 그 외 섹션의 행수가 바뀌면 = ALERT (즉시 중단 + 원인 조사)

BP-7: 전체 행수 변동 기록
      수정 후 전체 행수 변화를 fix_NNN.json에 추가 기록
      → 증가/감소 사유 필수 명시 (예: "§6.13 합계행 1줄 추가")

BP-8: 롤백 프로토콜 (역패치 방식)
      BP-8a: 롤백 = fix_NNN.json의 old↔new를 스왑하여 역패치 적용
             → 해당 건만 되돌림, 다른 수정은 보존
      BP-8b: 역패치 적용 후, 해당 건의 Ripple Map에 포함된
             모든 후속 Fix(N+1~현재)를 재검증
             → 연쇄 무효화 발견 시 해당 후속 Fix도 역패치 대상으로 표시
             → 사용자 승인 후 일괄 역패치
      BP-8c: 두 수정이 같은 행을 건드린 경우(충돌)
             → 자동 역패치 불가 → 수동 개입 요청

BP-9:  세션 중단 시 복구 프로토콜                                              [ABD-6]
       a) 현재 진행 중인 수정 건의 상태 확인 (BP-5 fix_NNN.json 기준)
       b) 마지막 완료된 fix_NNN 이후부터 재개
       c) 미완료 수정 건이 있으면 BP-8a 역패치 후 재시도

BP-10: Phase 전환 시 상태 저장                                                 [ABD-6]
       Phase 0/1/1.5/2 각 완료 시점에 상태 기록:
       저장: D:\VAMOS\04. 구현단계\v11_results\v11_phase_status.json
       내용: {"current_phase":"N","completed_agents":[...],"pending":[...]}
       → 다음 세션에서 이 파일을 읽어 중단 지점부터 재개

BP-11: Phase 2 완료 시 원본 무결성 재확인                                      [ABD-7]
       Phase 2-C 완료 후 BP-2 지문과 v24_original_backup.md SHA256 재대조
       → 불일치 시 ALERT + 수동 개입 / PASS 시 완료조건 ⑭ 충족
```

## 6.3 검증 보강 (BP-13 ~ BP-14)

```
BP-13: Ripple Map 이중 검증
       Ripple Map 작성 후, 0-A 섹션맵 기준 전 섹션에 대해
       수정 키워드의 출현 여부를 재확인 (grep + 섹션 컨텍스트)
       → grep 결과 중 무관한 항목은 제외 태깅 (예: 페이지번호 81 ≠ 모듈 수 81)
       → 의미론적 연쇄는 Agent가 해당 섹션을 직접 읽어 판단
       → Ripple Map 누락률 목표: 0건

BP-14: 수정 재시도 한계
       수정 1건당 재시도 최대 3회
       → 3회 연속 FAIL 시:
          a) 해당 건을 DEFERRED로 분류
          b) 다음 건으로 진행
          c) 전체 수정 완료 후 DEFERRED 건을 모아서 사용자와 협의
       → 무한루프 원천 차단
```

## 6.4 완료 후 — 정리 (BP-15)

```
BP-15: 스냅샷 보존 정책
       - Phase 2-B 진행 중: 전체 보존 (삭제 금지)
       - Phase 2-C 완료 + Checkpoint 14개 전부 PASS 후:
         → 최초 원본(v24_original_backup.md) + 최종본만 보존
         → 중간 스냅샷(snapshots/) + diff(diffs/)는 ZIP 압축 후 archive/로 이동
       - 사용자 승인 후 archive/ 삭제 가능
```

## 6.5 수정 1건 실행 흐름 (BP + PR 통합) [BP-12]

```
수정 1건 = 6단계 고정 순서:

  ① BP-4:  스냅샷 저장 (before_fix_NNN.md)
  ② BP-5:  변경 내용 기록 (fix_NNN.json)
  ③ 실제 수정 적용 (Edit 도구)
  ④ PR-01: 해당 건 검증 항목 즉시 재실행 → PASS/FAIL
  ⑤ BP-6:  비의도 섹션 변동 체크 (Ripple Map EXPECTED 외 ALERT)
  ⑥ BP-7:  전체 행수 변동 기록

  → ④ FAIL 시: BP-8a 역패치 → BP-14 재시도 (최대 3회)
  → ⑤ ALERT 시: 즉시 중단 → 원인 조사 → 사용자 확인
  → ④⑤ 모두 PASS 시: 다음 건으로 진행
```

---

# 7. Phase 2 — 수정 + 재검증 (2~3세션)

## 2-A: 분류 + Ripple Map + 수정 순서 결정

```
입력:  Phase 1.5 REAL_ISSUE 확정 목록                                          [ABD-3]
       D:\VAMOS\04. 구현단계\v11_results\phase15\v11_adversarial_report.md
작업:
  1. REAL_ISSUE를 수정 유형별 분류:
     - FIX: 값/수치/용어 수정
     - ADD: 누락 내용 추가 (전환조건, 운영 정보 등)
     - RESTRUCTURE: 구조 변경 (균일성 확보, 프롬프트 보강 등)
     - CLARIFY: 모호한 표현 명확화
  2. 각 수정 건의 Ripple Map 작성:
     - 수정 위치의 모든 영향 범위 추적 (grep 기반)
     - §6.13 합계, §7 체크리스트, 변경이력에 연쇄 영향 확인
  3. 수정 순서 결정:                                                     [PR-02]
     - 우선순위: BLOCKER → HIGH → MEDIUM → LOW
     - 동일 심각도 내: ripple 없는 단순 FIX 먼저 → ripple 있는 건 나중
     - RESTRUCTURE는 마지막 (가장 넓은 영향 범위)
     - 순서 확정 후 사용자 승인
산출물: D:\VAMOS\04. 구현단계\v11_results\phase2\v11_ripple_map.json
        D:\VAMOS\04. 구현단계\v11_results\phase2\v11_classified_issues.md [F-01]
        D:\VAMOS\04. 구현단계\v11_results\phase2\v11_fix_order.md        [PR-02]
```

## 2-B: PART2 수정 반영 (건별 즉시 검증 + 원본 보호)

```
★ 수정 1건 = §6.5의 6단계 고정 순서를 따른다 [BP-12]

  ① BP-4:  스냅샷 저장 (before_fix_NNN.md)
  ② BP-5:  변경 내용 JSON 기록 (fix_NNN.json)
  ③ 실제 수정 적용 (Edit 도구 — Ripple Map의 모든 영향 위치를 한 번에 수정)
  ④ PR-01: 해당 건 검증 항목 즉시 재실행 → PASS/FAIL
  ⑤ BP-6:  비의도 섹션 변동 체크 (Ripple Map EXPECTED 외 ALERT)
  ⑥ BP-7:  전체 행수 변동 기록

  → ④ FAIL 시: BP-8a 역패치 → BP-14 재시도 (최대 3회, 3회 FAIL → DEFERRED)
  → ⑤ ALERT 시: 즉시 중단 → 원인 조사 → 사용자 확인
  → ④⑤ 모두 PASS 시: 다음 건으로 진행

  replace_all 사용 시 → Changelog 과거 행 변경 여부 즉시 확인

  전체 수정 완료 후:
  1. DEFERRED 건이 있으면 사용자와 협의 후 처리
  2. 버전 업: v24.0.0 → v25.0.0
  3. 변경이력 섹션에 v25.0.0 항목 추가
```

## 2-C: Phase 0 재실행 + Checkpoint (14개 완료조건)

```
1. Phase 0 (0-A~0-G) 재실행 → 수정 후 인덱스 재구축
2. 14개 완료 조건 판정:
3. 산출물:
   - D:\VAMOS\04. 구현단계\v11_results\v11_checkpoint.md                 [F-03]
   - D:\VAMOS\04. 구현단계\v11_results\phase2\v11_phase2_final_report.md [3차-02]

   [기존 9개]
   ① Phase 0 인덱스 7개 전부 재구축 완료 (0-A~0-G)
   ② Phase 1 REAL_ISSUE 전건 수정 완료 (잔여 0건)
   ③ Phase 1.5 Spot-check 오판율 ≤ 10%
   ④ Ripple Map 전건 추적 완료
   ⑤ §6.13 산술 재검증 PASS
   ⑥ §7 GO/NO-GO 항목수 재검증 PASS
   ⑦ 변경이력 v25.0.0 항목 추가 완료
   ⑧ 모듈 수 §1.1 ↔ §2~§5 재검증 PASS
   ⑨ SOURCE_CONFLICT 인덱스 ↔ 본문 주석 재검증 PASS

   [신규 3개 — Wave 3~5 GAP 커버]                                        [C-01]
   ⑩ AI 프롬프트 12개: 자기완결성 점수 전원 3점 이상 + 테이블 매핑 전건 OK
   ⑪ 코드블록 전수: 문법 오류 0건 + 패키지 호환성 경고 0건
   ⑫ 운영/보안 GAP: BLOCKER/HIGH 잔여 0건

   [신규 2개 — 원본 보호 프로토콜 커버]                                   [BP]
   ⑬ 0-A 섹션맵 기준 Ripple Map 외 의도치 않은 섹션 삭제/행수 변동 0건
   ⑭ 원본 백업(v24_original_backup.md) SHA256 무결성 유지 확인 (BP-11)
```

---

# 8. 예상 대화 수 및 실행 순서

| 대화 | Phase | 작업 | 계획 | 실제 |
|------|-------|------|------|------|
| 대화 1 | Phase 0 (0-A~0-G) | 인덱스 7개 구축 | 1세션 | ✅ 1세션 |
| 대화 2 | Phase 1 (Wave 1~5, Agent 1~14) | 25개 GAP 전수 검증 | 6세션 | ✅ 1세션 |
| 대화 3 | Phase 1.5 (Agent 15) | 적대적 재검증 | 1세션 | ✅ 1세션 |
| 대화 4 | Phase 2-A + 2-B | 분류/Ripple/수정 순서 + PART2 수정 | 2~3세션 | ✅ 1세션 |
| 대화 5 | Phase 2-C | 재검증 + Checkpoint (14조건) | 1세션 | ⏳ 미실행 |

**계획: 11세션 → 실제: 5세션 (Phase 0~2-B 완료: 4세션)**
**압축 부작용**: Summary 합계 산술 오류 1건 (Phase 1, 수정 완료) + fix_order 수치 오류 (Phase 2-A, Phase 2-B 완료로 무영향)

---

# 9. v6~v10 자산 활용 요약

| v시리즈 자산 | v11 활용 방법 | 활용 Phase |
|-------------|-------------|-----------|
| v8 Phase 0 스크립트 (0-A~0-H) | PART2 v24.0.0 구조 무결성 현황 파악 (0-F) | Phase 0 |
| v8 RULE 1~6 | Phase 1.5 FP 필터 적용 (RULE-1~6) | Phase 1.5 |
| v9 GT-1 (파일경로), GT-3 (수량) | Phase 0 수치/경로 레지스트리 교차 참고 | Phase 0 |
| v9 RULE 7~14 | Phase 1.5 FP 필터 적용 (RULE-7~14) | Phase 1.5 |
| v9 Wave 실행 패턴 | Phase 1 Wave 구조 설계에 반영 | Phase 1 |
| v10 Feature Registry (3,940건) | Agent 5(§6교차) 참고 자료 | Phase 1 Wave 2 |
| v10 분류 체계 (Python 스크립트) | Phase 2-A 자동 분류 시 패턴 참조 | Phase 2 |

---

# 10. 산출물 디렉토리 구조

```
D:\VAMOS\04. 구현단계\v11_results\
├── phase0\
│   ├── v11_section_map.json        ← 0-A
│   ├── v11_reference_map.json      ← 0-B
│   ├── v11_numeric_registry.json   ← 0-C
│   ├── v11_terminology_dict.json   ← 0-D
│   ├── v11_prompt_inventory.json   ← 0-E
│   ├── v11_v6v10_reuse_index.json  ← 0-F
│   └── v11_codeblock_inventory.json ← 0-G                              [I-01]
├── phase1\
│   ├── wave1_agent01_numeric_module.md
│   ├── wave1_agent02_term_priority.md
│   ├── wave1_agent03_changelog.md
│   ├── wave2_agent04_flow_uniformity.md
│   ├── wave2_agent05_s6_bidirectional.md
│   ├── wave2_agent06_s7_stagegate.md
│   ├── wave3_agent07_prompt_selfcontain.md                              [A-02]
│   ├── wave3_agent08_prompt_coverage_rule.md                            [A-02]
│   ├── wave3_agent09_prompt_chain.md                                    [A-02]
│   ├── wave4_agent10_code_package.md
│   ├── wave4_agent11_cost_timeline.md
│   ├── wave4_agent12_system_design.md
│   ├── wave4_agent13_security_test.md
│   ├── wave5_agent14_usability_ops.md
│   └── v11_phase1_summary.md
├── phase15\
│   └── v11_adversarial_report.md
├── phase2\
│   ├── v24_original_backup.md       ← BP-1: 원본 백업 (절대 덮어쓰기 금지)
│   ├── v24_integrity.json           ← BP-2: 원본 지문 (행수/SHA256/섹션별)
│   ├── snapshots\                   ← BP-4: 수정 건별 스냅샷
│   │   ├── before_fix_001.md
│   │   ├── before_fix_002.md
│   │   └── ...
│   ├── diffs\                       ← BP-5: 수정 건별 변경 기록 (JSON)
│   │   ├── fix_001.json
│   │   ├── fix_002.json
│   │   └── ...
│   ├── archive\                     ← BP-15: 완료 후 스냅샷+diff ZIP 보관
│   ├── v11_ripple_map.json
│   ├── v11_fix_order.md                                                 [PR-02]
│   ├── v11_classified_issues.md
│   └── v11_phase2_final_report.md
├── v11_phase_status.json          ← BP-10: Phase 전환 상태              [ABD-6]
└── v11_checkpoint.md
```

---

# 11. 결정론 보증

```
고정 입력:
  1. v11_gap_analysis_skill.md v2.3.0 (26개 GAP, FROZEN)
  2. PART2 v24.0.0 구조 (§1~§7 + 변경이력, ~4,400줄)
  3. v6~v10 커버 범위 및 산출물 (확정)

고정 출력:
  - Phase 구조: Phase 0 (7 인덱스) → Phase 1 (5 Wave) → Phase 1.5 → Phase 2
  - 에이전트 수: 15개 (검증 14 + 적대적 1)                              [O-02]
  - Wave 배정: 25 GAP → 14 에이전트 (매핑 고정)                         [O-01]
  - GAP-26(ABD): 실행 전 외부 사전 검증 (GAP Analysis Skill 에이전트)    [ABD]
  - 산출물 구조: 위 디렉토리 (변경 불가)
  - 완료 조건: 14개 (기존 9 + Wave커버 3 + 원본보호 2)                   [C-01][BP]
  - 대화 수: 11 (±2)

1차 검증 반영 (v1.0.0 → v2.0.0):
  I-01:  Phase 0에 0-G 코드블록 인벤토리 추가
  I-02:  0-C에 통화/퍼센트 파싱 추가
  I-03:  Agent 4에 PART2 직접 읽기 필수 명시
  A-02:  Wave 3를 Agent 7/8/9로 재분배 (GAP-11 | GAP-12+14 | GAP-13)
  C-01:  완료조건 ⑩⑪⑫ 추가 (Wave 3~5 GAP 커버)
  R-01:  Phase 1.5에 v8 RULE 1~6 + v9 RULE 7~14 명시 계승
  PR-01: Phase 2-B에 건별 즉시 검증 프로토콜 추가
  PR-02: Phase 2-A에 수정 순서 결정 전략 추가
  N-01:  모든 Agent의 검증 항목 수를 범위(min~max)로 표기
  W-01:  Wave 1~4 병렬 가능 근거 명시 (Phase 0만 의존)
  W-02:  Wave 5의 Wave 1~4 의존 형식 명시 (ISSUE 요약 수신)
  O-01:  Phase 1 에이전트 수 14개로 정정 (검증 14 + 적대적 1 = 총 15)
  O-02:  전체 에이전트 수 15개로 정정
  L-01:  외부 참조 예외 Agent(10,11) 명시 + WAVE-RULE-3 보완
  L-02:  Agent 11/12의 §6 상세 범위 확장
  X-01:  Phase 0 입력 경로를 절대 경로로 명시
  X-02:  에이전트 출력 형식에 버전 필드 추가
  X-03:  모든 산출물 경로를 절대 경로로 명시
  X-04:  Phase 0 실패 처리 프로토콜 추가
  M-01:  0-F에 v23→v24 delta 추출 단계 추가
  P-01:  v24.0.0 미검증 상태 경고 문구 추가
  P-02:  WAVE-RULE-5 추가 + Agent 3에 v24 delta 집중 검증 명시

2차 검증 반영 (v2.0.0 → v2.1.0):
  F-01:  Phase 2-A 산출물에 v11_classified_issues.md 추가
  F-02:  Phase 1 완료 시 v11_phase1_summary.md 생성 단계 명시
  F-03:  Phase 2-C 산출물에 v11_checkpoint.md 명시

3차 검증 반영 (v2.1.0 → v2.2.0):
  3차-01: 결정론 보증 고정 입력의 gap_analysis 버전을 v2.1.0으로 정정
  3차-02: Phase 2-C 산출물에 v11_phase2_final_report.md 추가

4차 반영 (v2.2.0 → v2.3.0) — 원본 보호 프로토콜:
  BP-01: Phase 2 시작 전 PART2 원본 백업 저장
  BP-02: 원본 무결성 정보(행수/SHA256/섹션별 행수) JSON 기록
  BP-03: 백업 ↔ 원본 SHA256 일치 검증
  BP-04: 수정 건별 스냅샷 저장 (before_fix_NNN.md)
  BP-05: 수정 건별 변경 내용 JSON 기록 (old/new 쌍 — 역패치용)
  BP-06: Ripple Map 연동 비의도 섹션 변동 감지 (EXPECTED/ALERT 구분)
  BP-07: 수정 건별 전체 행수 변동 기록 (증감 사유 필수)
  BP-08: 역패치 롤백 (old↔new 스왑) + 연쇄 무효화 감지 + 충돌 시 수동 개입
  BP-12: PR-01과 BP 통합 6단계 고정 실행 순서 확정
  BP-13: Ripple Map 이중 검증 (grep + 직접 읽기)
  BP-14: 수정 재시도 최대 3회 + DEFERRED 분류 (무한루프 차단)
  BP-15: 스냅샷 보존 정책 (완료 후 ZIP → archive/)
  ⑬:    완료조건 — Ripple Map 외 의도치 않은 삭제/행수 변동 0건
  ⑭:    완료조건 — 원본 백업 SHA256 무결성 유지 확인
  §9:    디렉토리 구조에 snapshots/, diffs/, archive/ 추가
  §번호: 전체 섹션 번호 재정렬 (§6 원본보호 삽입 → §7~§11)

5차 반영 (v2.3.0 → v2.5.0) — GAP-26 ABD 역할 재정의:
  GAP-26: gap_analysis v2.2.0의 GAP-26(ABD-1~8) 인식 — 단, Framework 내부 실행이 아닌 외부 사전 검증으로 분리
  ABD분리: Phase 1.5 Agent 15에서 ABD 상세 제거 (Framework는 검증 대상이지 검증 실행자가 아님)
  역할정의: ABD-1~8은 GAP Analysis Skill 에이전트가 본 Framework를 대상으로 실행 전 수행
           → 발견사항은 Framework에 수정 반영 → 반영 완료 후 FROZEN
  §2:    Phase 1 = 25개 GAP(PART2 대상), GAP-26은 사전 검증 완료 표기
  §4:    Phase 1 제목 25개 GAP 유지
  §11:   고정 입력 gap_analysis v2.2.0(26개), 고정 출력 Phase 1은 25개 GAP 실행
  입력참조: v2.1.0→v2.3.0 업데이트 (26개 GAP 인식하되 Phase 1 실행은 25개)

6차 반영 (v2.5.0 → v2.6.0) — ABD-1~8 사전 검증 결과 반영:
  ABD-2: Phase 1/1.5 에이전트 실패 처리 추가 (WAVE-RULE-6 + Agent 15 실패 프로토콜)  [ISSUE-1]
  ABD-3: Phase 1.5 Agent 15 + Phase 2-A 입력 파일 경로 명시                          [ISSUE-2]
  ABD-6: 운영 안전 장치 추가 — Phase 0 청킹, WAVE-RULE-7(컨텍스트 오버플로),         [ISSUE-3]
         BP 사전 조건(디스크), BP-9(세션복구), BP-10(Phase 상태 저장), §2 세션 복구 노트
  ABD-7: BP-9~11 결번 해소 — BP-9(세션복구)/BP-10(상태저장)/BP-11(무결성재확인) 정의  [ISSUE-4]
  ABD-7: 입력 gap_analysis 버전 v2.2.0 → v2.3.0 보정 (전체 replace_all)             [ISSUE-5]
  §2:    세션 중단 복구 노트 추가 (BP-9/BP-10)
  §10:   v11_phase_status.json 추가

결과: Phase 0(7 인덱스) + Phase 1(5 Wave, 14 에이전트, 25개 GAP) + Phase 1.5(1 에이전트) + Phase 2(14 완료조건) + 원본보호(BP-1~15, 결번 해소) + GAP-26 ABD(사전 검증 완료, 5건 반영)

이 Framework는 추가/삭제 없이 확정(FROZEN)으로 취급한다.
```
