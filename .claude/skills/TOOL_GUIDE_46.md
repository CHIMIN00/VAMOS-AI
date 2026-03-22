# VAMOS AI 오류 방지 도구/기술 전체 가이드 (49개)

> 최종 업데이트: 2026-03-19
> 목적: AI 환각/누락/오류를 최소화하기 위한 도구 및 기술 전체 목록과 설치/구현 가이드
> 변경: 32개 → 46개 → 49개 (메타 스킬 2개 + SOT 모순 탐지 1개 추가)

---

## 목차

- [A그룹: Claude가 파일만 만들면 됨 (12개)](#a그룹-claude가-파일만-만들면-됨-12개)
- [B그룹: pip/npm install 후 진행 (13개)](#b그룹-pipnpm-install-후-진행-13개)
- [C그룹: API 키 설정 필요 (5개)](#c그룹-api-키-설정-필요-5개)
- [D그룹: 서버/인프라 설치 필요 (10개)](#d그룹-서버인프라-설치-필요-10개)
- [E그룹: 마켓플레이스 탐색/설치 (9개)](#e그룹-마켓플레이스-탐색설치-9개)
- [권장 진행 순서](#권장-진행-순서)
- [비용 요약](#비용-요약)
- [검증 영역 커버리지](#검증-영역-커버리지)

---

# A그룹: Claude가 파일만 만들면 됨 (12개)

> 사용자 작업: **없음**
> Claude 작업: SKILL.md 파일 생성 + 기존 스킬 보강
> 추가 설치: **없음**
> 비용: **$0**

---

## A-1. `/hallucination-check` 스킬

**기반 기술**: LLM Hallucination Detection Script
**출처**: https://github.com/Mattbusel/LLM-Hallucination-Detection-Script

### 기능
- EA JSON의 각 항목을 **atomic claim(원자적 주장)** 단위로 분해
- 각 claim을 SOT 원본 파일에서 개별 검증
- 기존 `/audit`의 AD-1(환각 탐지)을 학술적 기법으로 강화
- claim별 VERIFIED / UNVERIFIED / PARTIAL 판정

### 기존 스킬과의 차이
```
/audit AD-1: 무작위 40% 샘플링 → source_text 존재 확인
/hallucination-check: 전 항목을 claim 단위로 분해 → 개별 fact 검증
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\hallucination-check\SKILL.md
```

### 사용자 해야 할 것
```
없음
```

### 실행 방법
```
/hallucination-check [EA파일경로|all]
```

---

## A-2. `/fact-audit` 스킬

**기반 기술**: FACT-AUDIT 패턴 (ACL 2025 논문)
**출처**: https://aclanthology.org/2025.acl-long.17.pdf

### 기능
- **적응형 멀티에이전트 팩트 감사**
- 3개 역할을 Agent tool로 분리:
  1. **Auditor (감사자)**: EA 항목을 SOT에서 검증 시도
  2. **Challenger (반박자)**: 감사자의 "PASS" 판정을 반박 시도
  3. **Judge (판정자)**: 감사자와 반박자의 근거를 비교하여 최종 판정
- 기존 `/audit`가 단일 에이전트라면, 이것은 **토론 구조**

### 기존 스킬과의 차이
```
/audit: 하나의 AI가 "틀렸다고 가정하고 찾아라"
/fact-audit: 3개 AI가 각자 역할로 토론 → 편향 감소
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\fact-audit\SKILL.md
```

### 사용자 해야 할 것
```
없음
```

### 실행 방법
```
/fact-audit [EA파일경로]
```

---

## A-3. `/cross-examine` 스킬

**기반 기술**: MCF (Multi-agent Collaborative Filtering)
**출처**: https://www.sciencedirect.com/science/article/abs/pii/S0957417424025909

### 기능
- 에이전트 A의 결과를 에이전트 B가 **능동적 질문-답변 형식**으로 심문
- 단순 결과 비교가 아닌, "왜 이 값을 추출했는가?" 질문
- 답변이 불충분하면 → 해당 항목 재추출 대상

### 기존 스킬과의 차이
```
/cross-match: 두 EA의 "결과"만 비교 (수동적)
/cross-examine: 한 에이전트가 다른 에이전트에게 "질문" (능동적)
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\cross-examine\SKILL.md
```

### 사용자 해야 할 것
```
없음
```

### 실행 방법
```
/cross-examine [EA-01 EA-07]
```

---

## A-4. OrgForge 철학 적용 (기존 스킬 보강)

**기반 기술**: OrgForge Framework (2026 논문)
**출처**: https://arxiv.org/html/2603.14997

### 기능
- "결정론적 엔진이 ground truth를 유지하고, LLM은 표면 텍스트만 생성"
- VAMOS의 Layer A/B 2계층 구조가 이 철학과 동일
- 기존 `/validate`, `/quality-gate` 스킬에 이 원칙을 명시적으로 추가

### Claude가 할 작업
```
기존 파일 수정:
  D:\VAMOS\.claude\skills\validate\SKILL.md — OrgForge 원칙 섹션 추가
  D:\VAMOS\.claude\skills\quality-gate\SKILL.md — OrgForge 원칙 섹션 추가
```

### 사용자 해야 할 것
```
없음
```

---

## A-5. `/consensus` 스킬

**기반 기술**: Self-Consistency Voting / CISC (Confidence-Integrated Self-Consistency)
**출처**: https://arxiv.org/pdf/2502.06233

### 기능
- 동일 SOT를 **3~5회 반복 추출** → 각 항목별 다수결 투표
- 다수결로 일치하는 값 = 높은 신뢰도
- 불일치하는 값 = **환각 의심 항목** → 수동 확인 대상
- CISC 기법 적용: 각 추출에 confidence 가중치 부여 → 가중 다수결

### 핵심 로직
```
SOT 파일 A를 3회 독립 추출:
  1회차: MODULE_COUNT = 81
  2회차: MODULE_COUNT = 81
  3회차: MODULE_COUNT = 82  ← 불일치!

다수결: 81 (2/3) → 최종값 81
불일치 항목: MODULE_COUNT → 수동 확인 필요
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\consensus\SKILL.md
```

### 사용자 해야 할 것
```
없음
```

### 실행 방법
```
/consensus [SOT파일|EA번호] --rounds 3
```

---

## A-6. `/debate` 스킬

**기반 기술**: Claude Agent Teams 합의 패턴
**출처**: https://code.claude.com/docs/en/agent-teams

### 기능
- 여러 Agent를 spawn → 각자 독립적으로 같은 작업 수행
- 결과를 공유하며 **서로 반박/합의**
- 합의된 결과만 최종 채택
- "Scientific Debate" 패턴: 가설 제시 → 반증 시도 → 합의 도출

### 기존 스킬과의 차이
```
/fact-audit: 역할이 고정 (감사자/반박자/판정자)
/debate: 역할 없이 동등한 에이전트들이 자유 토론
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\debate\SKILL.md
```

### 사용자 해야 할 것
```
없음
```

### 실행 방법
```
/debate [작업설명] --agents 3
```

---

## A-7. `/json-diff` 스킬

**기반 기술**: Graphtage 시맨틱 Diff
**출처**: https://github.com/trailofbits/graphtage

### 기능
- 두 EA/CM JSON 파일 간 **시맨틱(의미적) diff**
- 단순 텍스트 diff가 아닌, JSON 구조를 이해하는 비교
- 키 순서 무시, 배열 요소 재정렬 감지
- 추가/삭제/변경된 항목을 구조적으로 표시
- Phase 재실행 전후 결과 비교에 사용

### 구현 방식
```
방법 A: pip install graphtage (B그룹으로 이동 시)
방법 B: Python 내장 json + difflib로 기본 구현 (A그룹 유지)
→ 기본은 방법 B로 구현, graphtage 설치 시 고급 기능 활성화
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\json-diff\SKILL.md
D:\VAMOS\.claude\hooks\json_semantic_diff.py  (Python 내장 모듈만 사용)
```

### 사용자 해야 할 것
```
없음 (기본 모드)
선택: pip install graphtage (고급 모드)
```

### 실행 방법
```
/json-diff [파일A] [파일B]
/json-diff v13_EA01_old.json v13_EA01_new.json
```

---

## A-8. `/golden-set` 스킬

**기반 기술**: Golden Dataset 자동 구축
**출처**: https://www.confident-ai.com/docs/llm-evaluation/core-concepts/test-cases-goldens-datasets

### 기능
- v8~v13의 **검증 완료된 산출물**에서 "정답 데이터셋" 자동 구축
- 이 정답 데이터셋으로 이후 추출 결과의 정확도를 자동 측정
- 정답 기준: quality-gate GOLD 판정 + 적대적 감사 CLEAN인 항목

### 핵심 로직
```
1. v13 EA 중 GOLD 판정 받은 항목 수집
2. 각 항목의 {key, value, source_file, source_line, source_text} 추출
3. SOT 원본에서 source_text 존재 확인 (결정론적 검증)
4. 확인된 항목 → golden_set.json 저장
5. 이후 /extract 결과를 golden_set과 비교:
   - Precision: 추출된 것 중 정답과 일치하는 비율
   - Recall: 정답 중 추출된 비율
   - F1: 종합 점수
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\golden-set\SKILL.md
D:\VAMOS\.claude\hooks\build_golden_set.py  (Python 내장 모듈만 사용)
```

### 사용자 해야 할 것
```
없음
```

### 실행 방법
```
/golden-set build          — 정답 데이터셋 구축
/golden-set eval [EA파일]  — 추출 결과를 정답과 비교
/golden-set status         — 현재 정답 데이터셋 통계
```

---

## A-9. `/symbolic-verify` 스킬

**기반 기술**: Neuro-Symbolic Verification (NSVIF)
**출처**: https://openreview.net/pdf/54e052e1a574e3c65e6ea8574d4de161c53e7e2e.pdf

### 기능
- EA JSON의 **수치 제약조건을 제약충족문제(CSP)**로 변환
- Python 내장 로직으로 결정론적 검증 (AI 판단 0%)
- DV-7(COUNT↔LIST 교차검증)의 확장판

### 검증 가능한 제약 유형
```
1. 산술 제약: categories 합계 = total_items_extracted = items 길이
2. 범위 제약: 0 < source_line ≤ 파일 줄 수
3. 타입 제약: value_type = "number" → isinstance(value, (int, float))
4. 교차 제약: COUNT 키의 value = 관련 LIST 키의 len(value)
5. 유일성 제약: item_id 중복 없음
6. 포함 제약: LOCK 값이 다른 EA에서도 동일
7. 논리 제약: severity=CRITICAL이면 confidence > 0.9
```

### 구현 방식
```
방법 A: Python 내장 로직 (A그룹 유지)
방법 B: pip install python-constraint (B그룹 #15와 연동 시 고급)
→ 기본은 방법 A로 구현
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\symbolic-verify\SKILL.md
D:\VAMOS\.claude\hooks\symbolic_verifier.py  (Python 내장 모듈만 사용)
```

### 사용자 해야 할 것
```
없음
```

### 실행 방법
```
/symbolic-verify [EA파일|all]
```

## A-49. `/sot-conflict` 스킬

**기반 기술**: SOT 간 교차 모순 탐지
**출처**: 원점 검증에서 발견된 빈 영역 (#6: SOT 내 모호/모순)

### 기능
- **SOT 파일들 사이의 모순/불일치를 자동 탐지**
- 기존 /cross-match가 "EA 간 불일치"를 잡는다면, 이것은 **"SOT 간 불일치"**를 잡음
- 탐지 유형:
  - **수치 모순**: D2.0-01에서 "81개 모듈" vs D2.0-07에서 "79개 모듈"
  - **용어 불일치**: 같은 개념을 다른 이름으로 사용 (예: "안전 모듈" vs "Safety Module")
  - **날짜/버전 충돌**: 문서 A의 일정과 문서 B의 일정이 다름
  - **LOCK 값 분산**: LOCK 관련 값이 여러 SOT에 산재 → 일관성 확인
- AI가 추출 전에 SOT 원본의 품질 문제를 먼저 발견 → 추출 오류 사전 차단

### 기존 스킬과의 차이
```
/cross-match: EA 결과물 간 비교 (추출 후)
/integrity: SOT 파일 변경 여부 모니터링 (해시 기반)
/sot-conflict: SOT 원본 내용 간 모순 탐지 (추출 전)
→ "원본이 모순이면 AI가 뭘 추출해도 틀린다" → 원본 품질부터 검증
```

### 핵심 로직
```
1. SOT 68개 파일에서 핵심 수치/용어/날짜 추출
2. 동일 개념이 여러 파일에 등장하는 경우 수집
3. 값 비교 → 불일치 발견 시 CONFLICT 리포트
4. 불일치 항목에 대해 "어느 파일이 정본인가?" 판단은 사람에게 위임

출력 예시:
  CONFLICT-001: MODULE_COUNT
    D2.0-01.md line 45: "81개 모듈"
    D2.0-07.md line 12: "79개 모듈"
    → 사람 확인 필요

  CONFLICT-002: APPROVAL_DATE
    D2.0-03.md line 78: "2026-02-15"
    D2.0-09.md line 23: "2026-02-20"
    → 사람 확인 필요
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\sot-conflict\SKILL.md
```

### 사용자 해야 할 것
```
없음
```

### 실행 방법
```
/sot-conflict scan              — 전체 SOT 교차 모순 스캔
/sot-conflict [SOT파일A] [SOT파일B]  — 두 파일 간 모순 확인
/sot-conflict numbers           — 수치 불일치만 스캔
/sot-conflict terms             — 용어 불일치만 스캔
```

---

# B그룹: pip/npm install 후 진행 (13개)

> 사용자 작업: **pip/npm install 명령어 실행** (1회)
> Claude 작업: 스킬 + Python/YAML 파일 생성
> 비용: **$0** (오픈소스)

---

## B-10. `/guardrails-validate` 스킬

**기반 기술**: Guardrails AI
**출처**: https://github.com/guardrails-ai/guardrails

### 기능
- DV-1~DV-9를 **Guardrails Validator 클래스**로 래핑
- EA JSON 생성 시 자동 검증 + **실패 시 자동 reask** (LLM에게 재생성 요청)
- JSON Schema + Pydantic 모델로 출력 구조 강제
- 기존 deterministic_validator.py를 프레임워크화

### 기존 스킬과의 차이
```
현재 /validate: 검증 실패 → 사용자에게 오류 보고 → 수동 수정
/guardrails-validate: 검증 실패 → AI에게 자동 재생성 요청 → 재검증
  → "알아서 고쳐서 다시 줘" 자동화
```

### 사용자 해야 할 것
```bash
pip install guardrails-ai
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\guardrails-validate\SKILL.md
D:\VAMOS\.claude\hooks\guardrails_validator.py
```

### 실행 방법
```
/guardrails-validate [EA파일|all]
```

---

## B-11. `/eval-ea` 스킬

**기반 기술**: DeepEval
**출처**: https://github.com/confident-ai/deepeval

### 기능
- EA 추출 결과에 대한 **정량적 평가 메트릭** 자동 계산
- 메트릭 종류:
  - **HallucinationMetric**: source_text vs SOT 원본 비교
  - **FaithfulnessMetric**: value가 source_text에서 도출 가능한지
  - **AnswerRelevancyMetric**: 추출된 key가 context와 관련 있는지
  - **커스텀 메트릭**: DV PASS율, 카테고리 분포 균형, 추출 커버리지

### 출력 예시
```json
{
  "target": "v13_EA01_claude_md.json",
  "metrics": {
    "hallucination_score": 0.02,
    "faithfulness_score": 0.95,
    "relevancy_score": 0.91,
    "dv_pass_rate": 1.0,
    "category_balance": 0.87,
    "coverage_rate": 0.93
  },
  "verdict": "PASS (all metrics above threshold)"
}
```

### 사용자 해야 할 것
```bash
pip install deepeval
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\eval-ea\SKILL.md
D:\VAMOS\.claude\hooks\deepeval_metrics.py
```

### 실행 방법
```
/eval-ea [EA파일|all]
/eval-ea all --compare-with v12   (v12 결과와 비교)
```

---

## B-12. `/prompt-test` 스킬

**기반 기술**: Promptfoo
**출처**: https://github.com/promptfoo/promptfoo

### 기능
- 추출 프롬프트의 품질을 **자동 테스트**
- 여러 프롬프트 변형(variant)으로 동일 SOT 추출 → 어떤 프롬프트가 가장 정확한지 비교
- **회귀 테스트**: 프롬프트 수정 후 이전보다 나빠졌는지 자동 감지
- YAML 설정 파일로 테스트 케이스 정의

### 테스트 시나리오 예시
```yaml
# promptfoo_config.yaml
prompts:
  - phase0_A_extraction_prompt_v1.md
  - phase0_A_extraction_prompt_v2.md

tests:
  - description: "LOCK 값 추출 정확도"
    vars:
      sot_file: "D2.0-07_Safety_Cost_Approval.md"
    assert:
      - type: contains
        value: "NEVER_AUTO"
      - type: javascript
        value: "output.items.length >= 40"

  - description: "수치 카테고리 완전성"
    vars:
      sot_file: "D2.0-01_Overview.md"
    assert:
      - type: javascript
        value: "output.metadata.categories.C1 >= 10"
```

### 사용자 해야 할 것
```bash
npm install -g promptfoo
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\prompt-test\SKILL.md
D:\VAMOS\.claude\hooks\promptfoo_config.yaml
D:\VAMOS\.claude\hooks\promptfoo_assertions.js  (커스텀 검증 로직)
```

### 실행 방법
```
/prompt-test [프롬프트파일|all]
/prompt-test regression   (이전 결과와 비교)
```

---

## B-13. `/artifact-diff` 스킬

**기반 기술**: llm-diff
**출처**: https://github.com/Mattbusel/llm-diff

### 기능
- EA/CM 산출물의 **버전 간 시맨틱 diff + 이력 추적**
- 추가/삭제/변경된 항목을 구조적으로 표시
- 버전 히스토리 저장 (append-only)
- Phase 재실행 전후 결과 비교 자동화
- parent-child 관계 추적 (어떤 버전에서 파생되었는지)

### A-7 `/json-diff`와의 차이
```
/json-diff: 두 파일의 "현재 상태" 비교 (1회성)
/artifact-diff: 버전 히스토리 저장 + 변화 추이 추적 (지속적)
```

### 사용자 해야 할 것
```bash
pip install llm-diff
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\artifact-diff\SKILL.md
D:\VAMOS\.claude\hooks\artifact_version_tracker.py
```

### 실행 방법
```
/artifact-diff [파일A] [파일B]           — 두 파일 비교
/artifact-diff history [EA파일]          — 버전 이력 조회
/artifact-diff regression [phase번호]    — Phase 전후 변화 분석
```

---

## B-14. `/input-guard` 스킬

**기반 기술**: LLM Guard
**출처**: https://protectai.com/llm-guard

### 기능
- SOT 파일에 **prompt injection 패턴**이 있는지 사전 스캔
- EA JSON 출력에 유해/비정상 콘텐츠가 포함되었는지 검사
- 스캐너 종류:
  - **PromptInjection**: 악의적 프롬프트 삽입 탐지
  - **Regex**: 비정상 패턴 탐지 (예: base64 인코딩된 텍스트)
  - **TokenLimit**: 입력 크기 초과 방지
  - **Anonymize**: PII(개인정보) 자동 감지

### 사용 시점
```
SOT 파일이 외부 기여자에 의해 수정될 때
→ 악의적 프롬프트가 SOT에 삽입되면
→ AI가 추출 시 오동작 가능
→ /input-guard로 사전 스캔
```

### 사용자 해야 할 것
```bash
pip install llm-guard
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\input-guard\SKILL.md
D:\VAMOS\.claude\hooks\input_scanner.py
```

### 실행 방법
```
/input-guard [SOT파일|all]
/input-guard scan-output [EA파일]
```

---

## B-15. `/symbolic-verify` 강화 (python-constraint)

**기반 기술**: python-constraint 라이브러리
**출처**: https://pypi.org/project/python-constraint/

### 기능
- A-9 `/symbolic-verify`의 **고급 모드** 활성화
- CSP(제약충족문제) 솔버를 사용한 정식 제약 검증
- 복잡한 다변수 제약도 자동 풀이 가능

### A-9과의 관계
```
A-9 기본 모드: Python if/assert로 간단한 제약 검증
B-15 고급 모드: constraint 라이브러리로 복잡한 교차 제약 풀이
  예: "EA-01의 MODULE_COUNT = EA-07의 TOTAL_MODULES =
       EA-12의 CORE + COND + EXP"
       → 3개 EA에 걸친 다변수 제약을 CSP로 풀기
```

### 사용자 해야 할 것
```bash
pip install python-constraint
```

### Claude가 만들 파일
```
A-9에서 이미 생성된 symbolic_verifier.py에 고급 모드 추가
(별도 SKILL.md 불필요)
```

### 실행 방법
```
/symbolic-verify [EA파일|all] --advanced
```

---

## B-33. `/json-repair` 스킬

**기반 기술**: json-repair 라이브러리
**출처**: https://github.com/mangiucugna/json_repair

### 기능
- AI가 생성한 **깨진/불완전한 JSON을 자동 복구**
- 흔한 오류 자동 수정:
  - 닫히지 않은 괄호/따옴표
  - 후행 쉼표 (trailing comma)
  - 이스케이프 안 된 특수문자
  - 잘린 JSON (토큰 제한으로 중간에 끊김)
- EA JSON 생성 시 파싱 실패 → 자동 복구 → DV 재검증

### 기존 도구와의 차이
```
현재: JSON 파싱 실패 → 전체 재추출 (비용 높음)
json-repair: JSON 파싱 실패 → 자동 복구 시도 → 성공 시 DV 검증만 재실행
```

### 사용자 해야 할 것
```bash
pip install json-repair
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\hooks\json_auto_repair.py
```

### 실행 방법
```
EA/CM 추출 시 자동 적용 (Hook 연동)
```

---

## B-34. `/deep-diff` 스킬

**기반 기술**: DeepDiff
**출처**: https://github.com/seperman/deepdiff

### 기능
- Python 객체/JSON의 **깊은 구조적 비교** (재귀적)
- A-7 json-diff의 pip 강화판:
  - 타입 변경 감지 (string → number)
  - 딕셔너리 키 추가/삭제/변경
  - 리스트 요소 순서 변경 vs 내용 변경 구분
  - 부동소수점 근사 비교 (significant_digits)
- EA 버전 간 정밀 차이 분석

### A-7과의 차이
```
A-7 json-diff: Python 내장 difflib 기반 (텍스트 레벨)
B-34 deep-diff: DeepDiff 라이브러리 기반 (객체 레벨, 타입 인식)
```

### 사용자 해야 할 것
```bash
pip install deepdiff
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\deep-diff\SKILL.md
D:\VAMOS\.claude\hooks\deep_diff_compare.py
```

### 실행 방법
```
/deep-diff [파일A] [파일B]
/deep-diff [파일A] [파일B] --ignore-order    (리스트 순서 무시)
```

---

## B-35. `/ragas-eval` 스킬

**기반 기술**: RAGAS (Retrieval Augmented Generation Assessment)
**출처**: https://github.com/explodinggradients/ragas

### 기능
- RAG 파이프라인의 **정량적 품질 평가 4대 메트릭**:
  - **Faithfulness**: 생성된 답변이 컨텍스트에 충실한지 (0~1)
  - **Answer Relevancy**: 답변이 질문과 관련 있는지 (0~1)
  - **Context Precision**: 검색된 컨텍스트가 정확한지 (0~1)
  - **Context Recall**: 필요한 컨텍스트가 모두 검색되었는지 (0~1)
- D-24 /sot-rag 파이프라인의 품질 측정에 활용
- EA 추출 결과의 SOT 충실도 평가

### B-11 eval-ea와의 차이
```
B-11 eval-ea (DeepEval): 환각/충실성/관련성 메트릭 (추출 결과 중심)
B-35 ragas-eval: RAG 4대 메트릭 (검색+생성 전체 파이프라인 중심)
→ 상호 보완적, 동시 사용 가능
```

### 사용자 해야 할 것
```bash
pip install ragas
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\ragas-eval\SKILL.md
D:\VAMOS\.claude\hooks\ragas_evaluator.py
```

### 실행 방법
```
/ragas-eval [EA파일|all]
/ragas-eval pipeline    (전체 RAG 파이프라인 평가)
```

---

## B-36. `/korean-nlp` 스킬

**기반 기술**: kiwipiepy (Kiwi 한국어 형태소 분석기)
**출처**: https://github.com/bab2min/kiwipiepy

### 기능
- 한국어 SOT 텍스트의 **정밀 형태소 분석**
- 활용 사례:
  - source_text에서 **핵심 명사/동사 자동 추출** → 키워드 매칭 정확도 향상
  - 한국어 문장 분리 (문장 경계 자동 인식)
  - 띄어쓰기 오류 자동 보정
  - 복합 명사 분해 → 표준 키 후보 자동 추천
- 기존 스킬에서 한국어 텍스트 처리 시 자동 활용

### VAMOS 특화 가치
```
SOT 68개 파일 중 한국어 비율이 높음
→ 기존 AI는 한국어 형태소 경계를 정확히 못 자르는 경우 있음
→ kiwipiepy로 정밀 분석 후 AI에게 전달 → 추출 정확도 향상
```

### 사용자 해야 할 것
```bash
pip install kiwipiepy
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\korean-nlp\SKILL.md
D:\VAMOS\.claude\hooks\korean_analyzer.py
```

### 실행 방법
```
/korean-nlp analyze [SOT파일]    — 형태소 분석 + 핵심어 추출
/korean-nlp keywords [EA파일]    — EA 항목의 한국어 키워드 검증
/korean-nlp fix-spacing [텍스트]  — 띄어쓰기 보정
```

---

## B-37. `/minicheck` 스킬

**기반 기술**: MiniCheck (Bespoke Labs)
**출처**: https://github.com/Bespoke-Systems/minicheck

### 기능
- NLI(Natural Language Inference) 기반 **사실 검증**
- EA의 각 claim을 SOT 원문과 1:1 대조:
  - **Supported**: SOT 원문이 이 claim을 뒷받침함
  - **Not Supported**: SOT 원문에서 근거를 찾을 수 없음
- 소형 모델 (Bespoke-MiniCheck-7B) 로컬 실행 가능
- API 모드도 지원 (Bespoke Labs API)

### A-1/A-2와의 차이
```
A-1 hallucination-check: claim 분해 → SOT 텍스트 매칭 (AI 기반)
A-2 fact-audit: 3-에이전트 토론 구조 (AI 기반)
B-37 minicheck: NLI 전용 모델이 사실 검증 (학습된 모델 기반)
→ AI 판단이 아닌 NLI 모델의 결정론적 판단 → Layer A 수준의 신뢰도
```

### 사용자 해야 할 것
```bash
pip install minicheck    # API 모드 (경량)
# 또는 로컬 모델 사용 시:
pip install minicheck[local] torch transformers
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\minicheck\SKILL.md
D:\VAMOS\.claude\hooks\minicheck_verifier.py
```

### 실행 방법
```
/minicheck [EA파일|all]
/minicheck [EA파일] --mode api       (API 모드)
/minicheck [EA파일] --mode local     (로컬 모델)
```

---

## B-38. `/docling` 스킬

**기반 기술**: Docling (IBM Research)
**출처**: https://github.com/DS4SD/docling

### 기능
- **문서 파싱/추출 전문 도구** (PDF, DOCX, PPTX, HTML, Markdown)
- SOT 마크다운 파일의 **구조 인식 파싱**:
  - 표(table) 자동 추출 → 구조화된 데이터
  - 중첩 리스트 정확한 파싱
  - 코드 블록 내 텍스트 vs 본문 텍스트 구분
  - 머리말/꼬리말/주석 구분
- AI가 SOT를 읽기 전에 Docling으로 사전 파싱 → 구조화된 입력 제공

### VAMOS 특화 가치
```
SOT 마크다운에는 복잡한 표, 중첩 리스트, 코드 블록이 혼재
→ AI가 직접 읽으면 구조를 잘못 해석하는 경우 있음
→ Docling 사전 파싱 → 구조화된 데이터로 AI에게 전달
→ 후반부 누락(DV-10) 감소 기대
```

### 사용자 해야 할 것
```bash
pip install docling
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\docling\SKILL.md
D:\VAMOS\.claude\hooks\docling_parser.py
```

### 실행 방법
```
/docling parse [SOT파일|all]        — SOT 구조 파싱
/docling tables [SOT파일]           — 표 자동 추출
/docling structure [SOT파일]        — 문서 구조 트리 출력
```

---

## B-39. `/dspy-optimize` 스킬

**기반 기술**: DSPy (Stanford NLP)
**출처**: https://github.com/stanfordnlp/dspy

### 기능
- **프롬프트 자동 최적화** 프레임워크
- B-12 promptfoo가 "프롬프트 테스트"라면, DSPy는 "프롬프트 자동 개선"
- 작동 방식:
  1. 추출 작업을 DSPy Module로 정의
  2. Golden Set (A-8)을 기준 데이터로 제공
  3. DSPy Optimizer가 자동으로 최적 프롬프트 탐색
  4. 최적화된 프롬프트로 추출 → 정확도 향상
- 지원 최적화 기법: BootstrapFewShot, MIPRO, BayesianSignatureOptimizer

### B-12 promptfoo와의 차이
```
B-12 promptfoo: 여러 프롬프트 변형을 사람이 작성 → 자동 비교 (수동 최적화)
B-39 dspy-optimize: 프롬프트를 AI가 자동 탐색/최적화 (자동 최적화)
→ promptfoo로 현재 성능 측정 → DSPy로 자동 개선 → promptfoo로 개선 확인
```

### 사용자 해야 할 것
```bash
pip install dspy
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\dspy-optimize\SKILL.md
D:\VAMOS\.claude\hooks\dspy_extraction_module.py
```

### 실행 방법
```
/dspy-optimize [EA번호] --metric accuracy    — 정확도 최적화
/dspy-optimize [EA번호] --metric coverage    — 커버리지 최적화
/dspy-optimize compare                       — 최적화 전/후 비교
```

---

### B그룹 일괄 설치 명령어

```bash
# 한 번에 전부 설치 (기존 6개 + 신규 7개)
pip install guardrails-ai deepeval llm-diff llm-guard python-constraint \
            json-repair deepdiff ragas kiwipiepy minicheck docling dspy
npm install -g promptfoo
```

---

# C그룹: API 키 설정 필요 (5개)

> 사용자 작업: **API 키 발급 + 환경변수 설정**
> Claude 작업: 스킬 + 스크립트 생성
> 비용: **최소 $0.60 ~ 최대 $17**

---

## C-16. `/exa-verify` 스킬

**기반 기술**: Exa Hallucination Detector
**출처**: https://github.com/exa-labs/exa-hallucination-detector

### 기능
- EA 항목의 source_text를 **Exa 검색 엔진으로 외부 소스에서 검증**
- Claude가 텍스트를 claim으로 분해 → Exa가 근거 소스 검색 → 일치 여부 판정
- VAMOS에서는 주로 **기술 용어/수치의 외부 정합성** 확인에 활용
  - 예: "Pydantic v2" → Exa에서 실제 Pydantic 버전 확인
  - 예: "Tauri 2.0" → 실제 존재하는 버전인지 확인

### 비용
```
무료 크레딧: 가입 시 $5 제공
검색 1건: $0.003
콘텐츠 추출: $0.001
예상 사용량: 750건 × $0.004 = $3
→ 무료 크레딧 내에서 충분
```

### 사용자 해야 할 것
```
1. https://exa.ai 가입
2. API 키 발급
3. 환경변수 설정:
   Windows: setx EXA_API_KEY "your-key-here"
   또는 .env 파일: EXA_API_KEY=your-key-here

4. Python 패키지 설치:
   pip install exa-py
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\exa-verify\SKILL.md
D:\VAMOS\.claude\hooks\exa_verifier.py
```

### 실행 방법
```
/exa-verify [EA파일] --tech-terms    (기술 용어만 검증)
/exa-verify [EA파일] --all-claims    (전체 claim 검증)
```

---

## C-17. `/cross-model` 스킬

**기반 기술**: Cross-Model Consistency (Zero-Knowledge Hallucination Detection)
**출처**: https://assets.amazon.science/e7/92/56d82a9345a488b213872d425781/zero-knowledge-llm-hallucination-detection-and-mitigation-through-fine-grained-cross-model-consistency.pdf

### 기능
- **동일 SOT를 Claude + GPT로 각각 추출**
- 두 모델의 결과를 item 단위로 비교
- 불일치 = 환각 후보 → 사람이 확인
- 일치 = 높은 신뢰도
- 모델 간 독립성이 핵심 (같은 모델의 편향을 피함)

### 비용
```
GPT-4o-mini 사용 시 (권장):
  입력: 2M 토큰 × $0.15/1M = $0.30
  출력: 0.5M 토큰 × $0.60/1M = $0.30
  합계: 약 $0.60

GPT-4o 사용 시:
  입력: 2M × $2.50/1M = $5.00
  출력: 0.5M × $10.00/1M = $5.00
  합계: 약 $10.00
```

### 사용자 해야 할 것
```
1. https://platform.openai.com 가입
2. API 키 발급
3. 환경변수 설정:
   Windows: setx OPENAI_API_KEY "sk-your-key-here"
   또는 .env 파일: OPENAI_API_KEY=sk-your-key-here

4. Python 패키지 설치:
   pip install openai
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\cross-model\SKILL.md
D:\VAMOS\.claude\hooks\cross_model_compare.py
```

### 실행 방법
```
/cross-model [SOT파일|EA번호] --model gpt-4o-mini
/cross-model all --model gpt-4o-mini    (전체 SOT 교차 검증)
```

---

## C-18. `/confidence` 스킬

**기반 기술**: LLM Uncertainty & Confidence Calibration
**출처**: https://github.com/MiaoXiong2320/llm-uncertainty

### 기능
- EA 추출 시 항목별 **신뢰도 점수를 보정**
- 현재 EA JSON의 confidence는 AI 자체 판단 (보정되지 않음)
- 보정 방법:
  - **방법 A (비용 $0)**: Claude 자체 반복 추출 → 일치율 = 실제 confidence
  - **방법 B (비용 $0.60)**: #17 Cross-Model과 합쳐서 교차 confidence 계산
- confidence < 0.7 항목 → 자동 재추출 대상 분류

### 비용
```
방법 A: $0 (Claude Code 구독 내)
방법 B: C-17과 합산 (추가 비용 없음)
```

### 사용자 해야 할 것
```
방법 A: 없음
방법 B: C-17의 설정이 완료되어 있으면 추가 작업 없음
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\confidence\SKILL.md
D:\VAMOS\.claude\hooks\confidence_calibrator.py
```

### 실행 방법
```
/confidence [EA파일] --method self       (방법 A: 자체 반복)
/confidence [EA파일] --method cross      (방법 B: 교차 모델)
/confidence [EA파일] --recalibrate       (기존 confidence 재보정)
```

---

## C-40. `/hhem-verify` 스킬 *(변경: Cleanlab TLM → Vectara HHEM)*

**기반 기술**: Vectara HHEM-2.1 (Hallucination Evaluation Model)
**출처**: https://huggingface.co/vectara/hallucination_evaluation_model
**변경 사유**: Cleanlab Studio 서비스(studio/app/tlm.cleanlab.ai) 접속 불가 (2026-03-20 확인)
**변경 일자**: 2026-03-20

### 기능
- **환각 탐지 전용 학습 모델**(flan-t5-base 기반)로 사실 일관성 점수 산출
- 기존 C-18 confidence가 "통계적 보정"이라면, HHEM은 "학습된 환각 판정 모델"
- 입력: (premise, hypothesis) 쌍
  - premise = SOT 원문 텍스트
  - hypothesis = EA 추출값을 자연어로 변환
- 출력: 0~1 점수
  - 0.8~1.0: SOT와 일관 → PASS
  - 0.5~0.8: 부분 일관 → 수동 확인 권장 (WARN)
  - 0.0~0.5: 불일관 → 환각 의심 → 재추출 대상 (FAIL)
- **API 키 불필요, GPU 불필요**, CPU에서 로컬 실행

### C-18 confidence와의 차이
```
C-18: 반복 추출 → 일치율 = 신뢰도 (통계적)
C-40: 전용 HHEM 모델이 (SOT, 추출값) 쌍의 일관성 판정 (학습 기반)
→ 병행 사용 시 신뢰도 추정 정확도 극대화
```

### 기존 도구와의 차이
```
C-17 cross-model:  GPT가 판정 (LLM-as-a-judge)
C-18 confidence:   반복 추출 일치율 (통계적)
B-37 minicheck:    NLI 모델 (사실 검증 특화)
C-40 hhem-verify:  환각 탐지 전용 모델 (환각 판정 특화, flan-t5 기반)
→ 4가지 서로 다른 접근법 → 합의 시 신뢰도 극대화
```

### 비용
```
$0 (완전 무료, 로컬 실행)
모델 크기: ~600MB (첫 실행 시 자동 다운로드, 이후 캐시)
처리 속도: ~1.5초/건 (CPU)
```

### 사용자 해야 할 것
```
1. Python 패키지 설치:
   pip install transformers torch
2. API 키: 불필요
3. 환경변수: 불필요
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\hhem-verify\SKILL.md
D:\VAMOS\.claude\hooks\hhem_scorer.py
```

### 실행 방법
```
/hhem-verify [EA파일|all]
/hhem-verify [EA파일] --threshold 0.8    (0.8 미만만 표시)
```

---

## C-41. `/patronus-check` 스킬

**기반 기술**: Patronus Lynx (환각 탐지 전문 모델)
**출처**: https://www.patronus.ai / https://huggingface.co/PatronusAI/Llama-3-Patronus-Lynx-8B-Instruct

### 기능
- **환각 탐지 전문 LLM** (Patronus Lynx 8B/70B)
- 입력: (context, question, answer) 3-튜플
  - context = SOT 원문
  - question = "이 파일에서 X 값은 무엇인가?"
  - answer = EA의 추출값
- 출력: FAITHFUL / NOT_FAITHFUL + 근거 설명
- 범용 LLM(Claude)과 다른 **환각 탐지 특화 모델**

### 기존 도구와의 차이
```
A-1 hallucination-check: Claude 자체가 환각 탐지 (범용 모델)
B-37 minicheck: NLI 모델이 사실 검증 (NLI 특화)
C-41 patronus-check: 환각 탐지 전문 LLM (환각 탐지 특화)
→ 3가지 서로 다른 접근법 → 합의 시 신뢰도 극대화
```

### 비용
```
로컬 실행 (8B 모델): $0 (GPU 필요: VRAM 16GB+)
API 사용: $0.005/호출
HuggingFace에서 무료 다운로드 가능
```

### 사용자 해야 할 것
```
# 방법 A: API 사용
1. https://www.patronus.ai 가입
2. API 키 발급
3. pip install patronus

# 방법 B: 로컬 모델 (GPU 필요)
pip install transformers torch
# HuggingFace에서 모델 다운로드
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\patronus-check\SKILL.md
D:\VAMOS\.claude\hooks\patronus_checker.py
```

### 실행 방법
```
/patronus-check [EA파일|all]
/patronus-check [EA파일] --mode api      (API 모드)
/patronus-check [EA파일] --mode local    (로컬 모델)
```

---

### C그룹 일괄 설치 명령어

```bash
# Python 패키지 (기존 2개 + 신규 2개)
pip install exa-py openai patronus transformers torch

# 환경변수 설정 (Windows)
setx EXA_API_KEY "your-exa-key"
setx OPENAI_API_KEY "sk-your-openai-key"
setx PATRONUS_API_KEY "your-patronus-key"
# HHEM(C-40): 환경변수 불필요 (로컬 모델)
```

### C그룹 비용 총합

| # | 도구 | 최소 비용 | 최대 비용 |
|---|------|----------|----------|
| 16 | Exa | $0 (무료 크레딧) | $3 |
| 17 | Cross-Model | $0.60 (4o-mini) | $10 (4o) |
| 18 | Confidence | $0 (방법 A) | $0 (방법 B) |
| 40 | Vectara HHEM (대체) | $0 (로컬) | $0 |
| 41 | Patronus Lynx | $0 (로컬) | $3.75 |
| | **합계** | **$0.60 (약 800원)** | **$16.75 (약 22,000원)** |

---

# D그룹: 서버/인프라 설치 필요 (10개)

> 사용자 작업: **Docker/DB 설치 + 서버 실행**
> Claude 작업: 스킬 + 연동 스크립트 생성
> 비용: **$0** (오픈소스 자체 호스팅)

---

## D-19. `/trace` 스킬 (Langfuse)

**기반 기술**: Langfuse (LLM Observability)
**출처**: https://langfuse.com / https://github.com/langfuse/langfuse

### 기능
- 모든 EA 추출/검증/감사 결과를 **자동 로깅**
- Phase별 환각률 추이 시각화
- 프롬프트 변경 전후 결과 비교
- 비용 추적 (토큰 사용량)
- 웹 대시보드에서 전체 파이프라인 모니터링

### 사용자 해야 할 것
```
1. Docker Desktop 설치 (없으면)
   https://www.docker.com/products/docker-desktop/

2. Langfuse 서버 실행:
   git clone https://github.com/langfuse/langfuse.git
   cd langfuse
   docker compose up -d

3. http://localhost:3000 접속 → 계정 생성

4. Settings → API Keys → 키 생성

5. 환경변수 설정:
   setx LANGFUSE_PUBLIC_KEY "pk-..."
   setx LANGFUSE_SECRET_KEY "sk-..."
   setx LANGFUSE_HOST "http://localhost:3000"

6. Python 패키지:
   pip install langfuse
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\trace\SKILL.md
D:\VAMOS\.claude\hooks\langfuse_logger.py
```

### 실행 방법
```
/trace start [phase번호]    — Phase 실행 로깅 시작
/trace stop                 — 로깅 중단
/trace dashboard            — 대시보드 URL 출력
```

---

## D-20. Opik by Comet

**출처**: https://github.com/comet-ml/opik

### 기능
- Langfuse와 유사: LLM trace 로깅 + 평가 + 시각화
- Comet ML 생태계와 통합

### 사용자 해야 할 것
```
1. Docker 설치
2. docker compose up으로 Opik 서버 실행
3. pip install opik
4. API 키 설정
```

### Claude가 만들 파일
```
연동 스크립트 (D-19 Langfuse와 택 1 권장)
```

---

## D-21. Evidently AI

**출처**: https://www.evidentlyai.com / https://github.com/evidentlyai/evidently

### 기능
- LLM 앱 평가/테스트/모니터링
- **CI/CD 통합**: GitHub Actions에서 자동 품질 체크
- 회귀 테스트: 이전 결과와 비교하여 품질 하락 자동 감지

### 사용자 해야 할 것
```
pip install evidently
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\hooks\evidently_eval.py
```

---

## D-22. `/sot-search` 스킬 (claude-context MCP)

**기반 기술**: claude-context by Zilliz
**출처**: https://github.com/zilliztech/claude-context

### 기능
- SOT 89,000줄을 **벡터 임베딩으로 인덱싱**
- AI가 SOT를 읽을 때 키워드/개념으로 **정확한 구절 검색**
- /sot-cache의 강화판: 캐시는 "이전 산출물" 기반, 이것은 "원본 벡터 검색"

### 사용자 해야 할 것
```
1. Python 패키지 설치:
   pip install pymilvus sentence-transformers

2. Milvus 서버 실행 (Docker):
   docker run -d --name milvus \
     -p 19530:19530 -p 9091:9091 \
     milvusdb/milvus:latest

3. 또는 Milvus Lite (서버 없이 로컬):
   pip install milvus

4. Claude Code MCP 설정:
   settings.json에 MCP 서버 추가 (Claude가 작성)
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\sot-search\SKILL.md
D:\VAMOS\.claude\hooks\sot_indexer.py       (SOT → 벡터 인덱싱)
D:\VAMOS\.claude\hooks\sot_search.py        (벡터 검색)
settings.json MCP 설정 추가
```

### 실행 방법
```
/sot-search index              — SOT 68파일 벡터 인덱싱
/sot-search "LOCK 관련 조항"    — 의미 검색
/sot-search "모듈 개수"         — 관련 구절 검색
```

---

## D-23. Agenta (프롬프트 버전 관리)

**출처**: https://github.com/Agenta-AI/agenta

### 기능
- 추출 프롬프트의 **Git 스타일 버전 관리**
- 프롬프트 variant별 성능 비교 (A/B 테스트)
- 프로덕션 프롬프트 배포 관리
- 웹 UI에서 프롬프트 편집/테스트

### 사용자 해야 할 것
```
1. Docker Desktop 설치

2. Agenta 서버 실행:
   git clone https://github.com/Agenta-AI/agenta.git
   cd agenta
   docker compose up -d

3. http://localhost:3000 접속

4. pip install agenta
```

### Claude가 만들 파일
```
프롬프트 variant 설정 + 평가 스크립트
```

---

## D-24. `/sot-rag` 스킬 (RAG 파이프라인)

**기반 기술**: Retrieval-Augmented Generation

### 기능
- SOT 원본 자체를 **벡터 임베딩 → 의미 검색 → 컨텍스트 주입**
- AI가 SOT를 읽을 때 관련 구절을 자동으로 컨텍스트에 포함
- /sot-cache(이전 산출물 캐시) + /sot-rag(원본 벡터 검색) = **이중 참조 레이어**

### D-22와의 차이
```
D-22 /sot-search: 사용자가 명시적으로 검색 요청
D-24 /sot-rag: 다른 스킬 실행 시 자동으로 관련 SOT 구절을 컨텍스트에 주입
```

### 사용자 해야 할 것
```
D-22와 동일한 인프라 사용 (벡터 DB + 임베딩 모델)
추가 설치 없음
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\sot-rag\SKILL.md
D:\VAMOS\.claude\hooks\rag_context_injector.py
```

### 실행 방법
```
/sot-rag enable    — 자동 RAG 컨텍스트 주입 활성화
/sot-rag disable   — 비활성화
/sot-rag status    — 현재 인덱스 상태
```

---

## D-25. `/sot-graph` 스킬 (Knowledge Graph)

**기반 기술**: Neo4j LLM Graph Builder
**출처**: https://github.com/neo4j-labs/llm-graph-builder

### 기능
- SOT 68개 파일 간의 **관계를 그래프로 시각화**
- 노드: 문서, 모듈, 개념, 수치
- 엣지: 참조, 의존, 포함, 제약
- 쿼리 예시:
  - "이 문서를 수정하면 어떤 문서가 영향받는지?"
  - "모듈 I-1이 의존하는 모든 모듈은?"
  - "LOCK 값을 참조하는 모든 문서는?"

### 사용자 해야 할 것
```
1. Docker로 Neo4j 설치:
   docker run -d --name neo4j \
     -p 7474:7474 -p 7687:7687 \
     -e NEO4J_AUTH=neo4j/password \
     neo4j:latest

2. http://localhost:7474 접속 확인

3. Python 패키지:
   pip install neo4j
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\sot-graph\SKILL.md
D:\VAMOS\.claude\hooks\sot_graph_builder.py    (SOT → 그래프 변환)
D:\VAMOS\.claude\hooks\sot_graph_query.py      (그래프 쿼리)
```

### 실행 방법
```
/sot-graph build              — SOT → 그래프 구축
/sot-graph impact D2.0-07     — "이 문서 수정 시 영향 범위"
/sot-graph deps I-1           — "이 모듈의 의존성 트리"
/sot-graph visualize          — Neo4j 브라우저 URL 출력
```

---

## D-26. `/lineage` 스킬 (OpenLineage)

**기반 기술**: OpenLineage + Marquez
**출처**: https://github.com/OpenLineage/OpenLineage

### 기능
- 전체 파이프라인의 **데이터 계보(lineage) 추적**
- "이 값이 어디서 왔는지" 역추적:
  ```
  EA-07 item 12의 value=7
    ← D2.0-07_Safety.md line 234
    ← CM-C7에서 EA-01 item 5와 비교됨
    ← Delta D-03으로 수정됨
    ← Phase 0 verdict에서 PASS 판정
  ```
- Phase 간 산출물의 부모-자식 관계 자동 기록

### 사용자 해야 할 것
```
1. Docker로 Marquez 서버 실행:
   git clone https://github.com/MarquezProject/marquez.git
   cd marquez
   docker compose up -d

2. http://localhost:3000 접속 확인

3. Python 패키지:
   pip install openlineage-python
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\lineage\SKILL.md
D:\VAMOS\.claude\hooks\lineage_tracker.py
```

### 실행 방법
```
/lineage track [EA파일]          — 이 파일의 계보 기록 시작
/lineage trace [항목ID]          — 특정 항목의 출처 역추적
/lineage dashboard               — Marquez 대시보드 URL
```

---

## D-42. `/phoenix-observe` 스킬 (Arize Phoenix)

**기반 기술**: Arize Phoenix (LLM Observability & Evaluation)
**출처**: https://github.com/Arize-ai/phoenix

### 기능
- **오픈소스 LLM 관측/평가 올인원 플랫폼** (D-19 Langfuse 대안)
- 주요 기능:
  - **Traces**: 모든 LLM 호출 자동 기록 + 시각화
  - **Evals**: 환각/충실성/관련성 메트릭 내장 (DeepEval/RAGAS 연동)
  - **Datasets**: Golden Set 관리 + 평가 자동화
  - **Experiments**: A/B 테스트 (프롬프트 변형 비교)
  - **Retrieval Analysis**: RAG 파이프라인 검색 품질 시각화
- Jupyter Notebook에서 바로 실행 가능 (서버 설치 선택사항)
- OpenTelemetry 기반 → 표준화된 계측

### D-19 Langfuse와의 차이
```
D-19 Langfuse: Docker 필수, 웹 대시보드 중심
D-42 Phoenix: Docker 선택사항, Notebook에서 바로 실행 가능
→ 진입 장벽이 낮음, 빠른 시작 가능
→ RAGAS/DeepEval 메트릭 네이티브 통합
```

### 사용자 해야 할 것
```bash
# 기본 설치 (Notebook 모드)
pip install arize-phoenix

# 서버 모드 (Docker)
docker run -d --name phoenix -p 6006:6006 arizephoenix/phoenix:latest
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\phoenix-observe\SKILL.md
D:\VAMOS\.claude\hooks\phoenix_tracer.py
```

### 실행 방법
```
/phoenix-observe start              — Phoenix UI 시작 (localhost:6006)
/phoenix-observe trace [phase번호]   — Phase 실행 추적
/phoenix-observe eval [EA파일]       — 평가 메트릭 시각화
/phoenix-observe rag-analysis        — RAG 검색 품질 분석
```

---

## D-43. `/giskard-scan` 스킬

**기반 기술**: Giskard (AI Quality Testing)
**출처**: https://github.com/Giskard-AI/giskard

### 기능
- AI 모델/파이프라인의 **취약점 자동 스캔**
- 스캔 항목:
  - **환각 취약점**: 어떤 입력 유형에서 환각이 잘 발생하는지
  - **편향 취약점**: 특정 카테고리/도메인에서 성능이 떨어지는지
  - **견고성 취약점**: 입력 변형(오타, 줄바꿈, 인코딩)에 얼마나 민감한지
  - **성능 취약점**: 긴 문서/복잡한 구조에서 정확도 하락 패턴
- VAMOS 추출 파이프라인을 Giskard에 래핑 → 자동 취약점 발견
- CI/CD 통합 가능 (GitHub Actions)

### D-21 Evidently와의 차이
```
D-21 Evidently: 결과 모니터링/회귀 탐지 (사후 평가)
D-43 Giskard: 취약점 사전 스캔/발견 (사전 평가)
→ Giskard로 약점 발견 → 수정 → Evidently로 모니터링
```

### 사용자 해야 할 것
```bash
pip install giskard

# Hub 서버 (선택, 웹 UI)
docker run -d --name giskard -p 19000:19000 giskardai/giskard:latest
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\giskard-scan\SKILL.md
D:\VAMOS\.claude\hooks\giskard_scanner.py
```

### 실행 방법
```
/giskard-scan [EA번호|all]           — 추출 파이프라인 취약점 스캔
/giskard-scan report                 — 취약점 리포트 생성
/giskard-scan category [C1~C8]       — 특정 카테고리 집중 스캔
```

---

### D그룹 일괄 설치 명령어

```bash
# Python 패키지 (기존 + 신규 2개)
pip install langfuse pymilvus sentence-transformers neo4j openlineage-python evidently \
            arize-phoenix giskard

# Docker 컨테이너 (필요한 것만)
docker run -d --name milvus -p 19530:19530 milvusdb/milvus:latest
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
docker run -d --name phoenix -p 6006:6006 arizephoenix/phoenix:latest

# Langfuse (git clone 후)
cd langfuse && docker compose up -d

# Marquez (git clone 후)
cd marquez && docker compose up -d
```

---

# E그룹: 마켓플레이스 탐색/설치 (9개)

> 사용자 작업: **GitHub clone 또는 marketplace 명령어**
> Claude 작업: 가이드 제공 + 설정 도움
> 비용: **$0**

---

## E-27. Anthropic skill-creator (Eval/Benchmark)

**출처**: https://github.com/anthropics/skills

### 기능
- 기존 11개 스킬의 **품질을 자동 평가/벤치마크**
- 4개 모드: Create, Eval, Improve, Benchmark
- 스킬이 실제로 의도대로 동작하는지 테스트

### 현재 상태
```
이미 설치됨: C:\Users\dkscl\.claude\plugins\...\skill-creator\
```

### 사용자 해야 할 것
```
Claude Code에서 실행:
  /skill-creator eval         — 스킬 평가
  /skill-creator benchmark    — 벤치마크
```

### Claude가 도울 것
```
평가 기준 설정, 테스트 케이스 작성
```

---

## E-28. claude-code-skills (levnikolaevich)

**출처**: https://github.com/levnikolaevich/claude-code-skills

### 기능
- codebase audit, quality gate, multi-model AI review 포함 6개 플러그인
- 코드 품질 감사, 보안 감사, 아키텍처 감사 스킬 포함

### 사용자 해야 할 것
```bash
# 플러그인 등록
cd D:\VAMOS\.claude\plugins
git clone https://github.com/levnikolaevich/claude-code-skills.git

# 또는 Claude Code에서:
/plugin marketplace add https://github.com/levnikolaevich/claude-code-skills
```

### Claude가 도울 것
```
VAMOS에 필요한 스킬만 선별하여 추천
```

---

## E-29. awesome-agent-skills (VoltAgent)

**출처**: https://github.com/VoltAgent/awesome-agent-skills

### 기능
- 500+ 스킬 큐레이션 목록
- Claude, Codex, Gemini CLI, Cursor 호환
- 문서 검증, 코드 리뷰, 테스트 자동화 등 다양한 카테고리

### 사용자 해야 할 것
```
1. https://github.com/VoltAgent/awesome-agent-skills 방문
2. 카테고리별 스킬 탐색
3. 필요한 스킬 다운로드 → D:\VAMOS\.claude\skills\ 에 복사
```

### Claude가 도울 것
```
문서 검증/품질 관련 스킬 필터링하여 추천
```

---

## E-30. claude-code-plugins-plus-skills

**출처**: https://github.com/jeremylongshore/claude-code-plugins-plus-skills

### 기능
- 340 플러그인 + 1,367 스킬
- CCPI 패키지 매니저로 설치/관리
- Interactive tutorial 포함

### 사용자 해야 할 것
```bash
# CCPI 패키지 매니저 설치
# Claude Code에서:
/plugin marketplace add https://github.com/jeremylongshore/claude-code-plugins-plus-skills

# 또는 수동:
cd D:\VAMOS\.claude\plugins
git clone https://github.com/jeremylongshore/claude-code-plugins-plus-skills.git
```

### Claude가 도울 것
```
VAMOS 검증 파이프라인에 맞는 스킬 선별
```

---

## E-31. claude-pre-commit (스킬/Hook 구조 검증)

**출처**: https://github.com/freddo1503/claude-pre-commit

### 기능
- SKILL.md, hooks, settings.json의 **구조적 유효성 자동 검증**
- git commit 전에 스킬 파일 문법 오류 자동 탐지
- YAML frontmatter 유효성 검증
- 존재하지 않는 스크립트 경로 참조 탐지

### 사용자 해야 할 것
```bash
# pre-commit 설치
pip install pre-commit

# 프로젝트에 설정 추가
cd D:\VAMOS
git clone https://github.com/freddo1503/claude-pre-commit.git .claude-pre-commit

# .pre-commit-config.yaml 생성 (Claude가 작성)
pre-commit install
```

### Claude가 만들 파일
```
D:\VAMOS\.pre-commit-config.yaml
```

---

## E-32. `/deterministic` 스킬 (LLM Output Caching)

**기반 기술**: LLM 재현성 제어
**출처**: https://github.com/nanomaoli/llm_reproducibility

### 기능
- 동일 입력에 대해 **동일 출력을 최대한 재현**
- temperature=0 고정
- 캐시된 이전 결과와 현재 결과 비교 → drift 감지
- "어제와 오늘 같은 작업인데 결과가 다르다" → 원인 분석

### 사용자 해야 할 것
```
Claude Code 설정에서 temperature 조정 (Claude가 가이드)
별도 설치 없음
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\deterministic\SKILL.md
```

### 실행 방법
```
/deterministic on            — 재현성 모드 활성화
/deterministic off           — 비활성화
/deterministic compare       — 이전 결과와 현재 결과 drift 분석
```

## E-44. `/llama-firewall` 스킬

**기반 기술**: LlamaFirewall (Meta)
**출처**: https://github.com/meta-llama/llama-firewall

### 기능
- Meta의 **다계층 AI 보안 프레임워크**
- B-14 LLM Guard의 상위 호환:
  - **PromptGuard 2**: 프롬프트 injection/jailbreak 탐지 (86M 파라미터 전용 모델)
  - **AlignmentCheck**: LLM 출력이 시스템 지침과 일치하는지 검증
  - **CodeShield**: 코드 생성 시 보안 취약점 자동 탐지
  - **Regex Scanner**: 커스텀 패턴 기반 입출력 필터링
- VAMOS에서는 SOT 입력 보안 + EA 출력 검증에 활용

### B-14 LLM Guard와의 차이
```
B-14 LLM Guard: 범용 입출력 스캐너 (규칙 기반 중심)
E-44 LlamaFirewall: Meta 전용 모델 기반 (PromptGuard 2 + AlignmentCheck)
→ LlamaFirewall이 더 정밀하지만 모델 다운로드 필요 (GPU 권장)
→ LLM Guard는 경량, LlamaFirewall은 고정밀
```

### 사용자 해야 할 것
```bash
pip install llama-firewall
# PromptGuard 2 모델 다운로드 (HuggingFace)
# GPU 권장 (CPU도 가능하지만 느림)
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\llama-firewall\SKILL.md
D:\VAMOS\.claude\hooks\llama_firewall_scanner.py
```

### 실행 방법
```
/llama-firewall scan-input [SOT파일]     — SOT 입력 보안 스캔
/llama-firewall scan-output [EA파일]     — EA 출력 보안 검증
/llama-firewall alignment [EA파일]       — 지침 준수 여부 검증
```

---

## E-45. `/kr-sbert` 스킬

**기반 기술**: KR-SBERT (한국어 문장 임베딩)
**출처**: https://github.com/snunlp/KR-SBERT / https://huggingface.co/snunlp/KR-SBERT-V40K-klueNLI-augSTS

### 기능
- **한국어 특화 문장 임베딩 모델** (SBERT 한국어 파인튜닝)
- D-22/D-24의 벡터 검색에서 **한국어 검색 정확도 대폭 향상**
- 기본 sentence-transformers는 영어 중심 → 한국어 SOT에서 검색 품질 저하
- KR-SBERT로 교체 시:
  - "모듈 개수" ↔ "MODULE_COUNT" 의미적 매칭 가능
  - "안전 승인" ↔ "Safety_Approval" 크로스링구얼 매칭
  - 한국어 유사 표현 인식 (동의어, 약어 등)

### D-22/D-24와의 관계
```
D-22 sot-search: sentence-transformers 기본 모델 사용
D-24 sot-rag: sentence-transformers 기본 모델 사용
→ E-45 KR-SBERT 설치 시 자동으로 한국어 최적화 모델로 교체
→ 별도 스킬이 아닌 D-22/D-24의 성능 업그레이드
```

### 사용자 해야 할 것
```bash
pip install sentence-transformers
# 모델 자동 다운로드 (약 250MB)
# python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS')"
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\hooks\kr_sbert_embedder.py   (D-22/D-24에서 자동 사용)
```

### 실행 방법
```
D-22/D-24 설치 시 자동 활성화
/sot-search "안전 승인 모듈"    — 한국어 의미 검색 정확도 향상
```

---

## E-46. `/gpt-cache` 스킬

**기반 기술**: GPTCache
**출처**: https://github.com/zilliztech/GPTCache

### 기능
- LLM 응답 **시맨틱 캐싱** → 비용 절감 + 속도 향상
- 동일/유사한 질문에 대해 이전 응답을 캐시에서 반환
- VAMOS에서의 활용:
  - 동일 SOT 반복 추출 시 캐시 히트 → 비용 0
  - /consensus 3~5회 반복 추출 시 1회만 실제 호출
  - Phase 재실행 시 변경되지 않은 SOT는 캐시 활용
- 시맨틱 유사도 기반 → 완전 동일하지 않아도 캐시 히트 가능

### E-32 deterministic과의 차이
```
E-32 deterministic: 동일 입력 → 동일 출력 보장 (재현성)
E-46 gpt-cache: 유사 입력 → 이전 출력 반환 (캐싱/비용)
→ deterministic은 품질 목적, gpt-cache는 비용/속도 목적
```

### 사용자 해야 할 것
```bash
pip install gptcache
```

### Claude가 만들 파일
```
D:\VAMOS\.claude\skills\gpt-cache\SKILL.md
D:\VAMOS\.claude\hooks\gptcache_manager.py
```

### 실행 방법
```
/gpt-cache enable     — 캐싱 활성화
/gpt-cache disable    — 캐싱 비활성화
/gpt-cache stats      — 캐시 히트율/절감 비용 통계
/gpt-cache clear      — 캐시 초기화
```

---

# 권장 진행 순서

```
[1단계] A그룹 12개 ← 지금 바로 가능 (사용자 작업 0)
  Claude가 SKILL.md + PY 파일 생성 → 즉시 사용

[2단계] B그룹 13개 ← pip/npm install 1회 후
  사용자: pip install guardrails-ai deepeval llm-diff llm-guard python-constraint \
                      json-repair deepdiff ragas kiwipiepy minicheck docling dspy
         npm install -g promptfoo
  Claude: 스킬 + 스크립트 생성
  ★ 핵심: B-36 kiwipiepy(한국어) + B-37 minicheck(사실검증) + B-39 dspy(프롬프트최적화)

[3단계] E-27 skill-creator eval ← 이미 설치되어 있음
  사용자: /skill-creator eval 실행
  목적: 1~2단계에서 만든 스킬의 품질 평가

[4단계] C그룹 5개 ← API 키 설정 후
  사용자: Exa + OpenAI + Cleanlab + Patronus API 키 발급
  Claude: 스킬 + 스크립트 생성
  ★ 핵심: C-40 Cleanlab TLM(신뢰도) + C-41 Patronus Lynx(환각 전문)

[5단계] E그룹 나머지 ← 마켓플레이스 탐색
  사용자: 필요한 스킬 탐색/설치
  ★ 핵심: E-44 LlamaFirewall(보안) + E-45 KR-SBERT(한국어 임베딩)

[6단계] D그룹 10개 ← 인프라 구축 (장기)
  우선순위: D-42 Phoenix(진입장벽↓) → D-22 벡터 검색 → D-25 Knowledge Graph
  ★ 핵심: D-42 Arize Phoenix(Notebook 즉시 사용) + D-43 Giskard(취약점 스캔)
```

---

# 비용 요약

| 그룹 | 항목 수 | 비용 |
|------|--------|------|
| A그룹 | 12개 | $0 |
| B그룹 | 13개 | $0 (오픈소스) |
| C그룹 | 5개 | $0.60 ~ $16.75 |
| D그룹 | 10개 | $0 (자체 호스팅) |
| E그룹 | 9개 | $0 |
| **합계** | **49개** | **$0.60 ~ $16.75** |

---

# 검증 영역 커버리지

| 검증 영역 | 커버하는 도구 |
|-----------|-------------|
| 환각 탐지 | A-1, A-2, C-16, **B-37**, **C-41** |
| 교차 검증 (동일 모델) | A-3, A-5, A-6 |
| 교차 검증 (다른 모델) | C-17 |
| JSON 스키마 강제 | B-10 |
| JSON 구조적 비교 | A-7, B-13, **B-34** |
| JSON 자동 복구 | **B-33** |
| 정량 평가 메트릭 | B-11, **B-35** |
| 프롬프트 품질 테스트 | B-12 |
| 프롬프트 자동 최적화 | **B-39** |
| 프롬프트 버전 관리 | D-23 |
| 신뢰도 점수 보정 | C-18, **C-40** |
| 입력 보안 (injection) | B-14, **E-44** |
| 결정론적 재현성 | E-32 |
| 결정론적 제약 검증 | A-9, B-15 |
| 정답 데이터셋 | A-8 |
| 산출물 버전 diff | B-13 |
| 데이터 계보 추적 | D-26 |
| 지식 그래프 (관계 시각화) | D-25 |
| RAG (벡터 검색) | D-22, D-24 |
| RAG 품질 평가 | **B-35** |
| 한국어 텍스트 처리 | **B-36**, **E-45** |
| 문서 구조 파싱 | **B-38** |
| LLM 관측/로깅 | D-19, D-20, D-21, **D-42** |
| AI 취약점 스캔 | **D-43** |
| LLM 응답 캐싱 | **E-46** |
| SOT 원본 간 모순 탐지 | **A-49** |
| 기존 산출물 캐시 활용 | 기존 /sot-cache |
| SOT 무결성 모니터링 | 기존 /integrity |
| CoT 추론 검증 | A-2, A-9 |
| 스킬 품질 평가 | E-27 |
| Hook/스킬 구조 검증 | E-31 |

---

# 오류율 변화 예측

```
현재 (기존 11 스킬 + 16 Hook):
  환각/누락/오류율: 약 15~25%

A~E 32개 도구 전부 적용 시:
  환각/누락/오류율: 약 3~7%
  → 잔여 영역: 한국어 처리, NLI 기반 검증, 프롬프트 자동 최적화, 취약점 사전 발견

A~E 46개 도구 전부 적용 시:
  환각/누락/오류율: 약 1~3%
  → 신규 14개가 커버하는 잔여 영역:
    - 한국어 정밀 처리: B-36 kiwipiepy + E-45 KR-SBERT
    - NLI 기반 사실 검증: B-37 MiniCheck + C-41 Patronus Lynx
    - 프롬프트 자동 최적화: B-39 DSPy
    - 학습된 신뢰도 모델: C-40 Cleanlab TLM
    - 취약점 사전 발견: D-43 Giskard
    - 깨진 JSON 자동 복구: B-33 json-repair
    - 문서 구조 사전 파싱: B-38 Docling
    - 다계층 보안: E-44 LlamaFirewall
    - LLM 응답 캐싱: E-46 GPTCache

A~E 49개 도구 전부 적용 시:
  환각/누락/오류율: 약 0.5~2%
  → 추가 3개가 커버하는 영역:
    - SOT 원본 간 모순 사전 탐지: A-49 sot-conflict
    - 최종 완료 결정론적 판정: A-47 final-review
    - 도구 커버리지 완전성 증명: A-48 completeness-map

남은 0.5~2%의 성격:
  → LLM 모델 자체의 기본 한계 (temperature, 확률적 생성)
  → SOT 원본의 모호성/불완전성 (A-49로 탐지는 가능, 수정은 사람)
  → 도구로 해결 불가 → 사람의 최종 확인 필요
```

---

# 신규 17개 도구 요약 (v2+v3 추가분)

| # | 도구명 | 그룹 | 핵심 가치 | 기존 도구와의 관계 |
|---|--------|------|----------|-------------------|
| 33 | json-repair | B | 깨진 JSON 자동 복구 | 신규 (기존 없음) |
| 34 | DeepDiff | B | 객체 레벨 JSON 비교 | A-7 json-diff 강화 |
| 35 | RAGAS | B | RAG 4대 메트릭 | B-11 eval-ea 보완 |
| 36 | kiwipiepy | B | 한국어 형태소 분석 | 신규 (한국어 특화) |
| 37 | MiniCheck | B | NLI 기반 사실 검증 | A-1/A-2 보완 (다른 접근) |
| 38 | Docling | B | 문서 구조 파싱 | 신규 (SOT 사전 처리) |
| 39 | DSPy | B | 프롬프트 자동 최적화 | B-12 promptfoo 상위 |
| 40 | Cleanlab TLM | C | 학습된 신뢰도 점수 | C-18 confidence 보완 |
| 41 | Patronus Lynx | C | 환각 전문 탐지 모델 | A-1/C-16 보완 (전문 모델) |
| 42 | Arize Phoenix | D | LLM 관측 올인원 | D-19/D-20 대안 (진입장벽↓) |
| 43 | Giskard | D | AI 취약점 사전 스캔 | D-21 Evidently 보완 |
| 44 | LlamaFirewall | E | Meta 다계층 보안 | B-14 LLM Guard 상위 |
| 45 | KR-SBERT | E | 한국어 문장 임베딩 | D-22/D-24 한국어 강화 |
| 46 | GPTCache | E | LLM 응답 캐싱 | 신규 (비용 절감) |
| **47** | **final-review** | **A** | **최종 완료 판정 (FINAL/NOT_FINAL)** | **신규 (무한루프 방지)** |
| **48** | **completeness-map** | **A** | **오류×도구 커버리지 지도** | **신규 (완전성 증명)** |
| **49** | **sot-conflict** | **A** | **SOT 원본 간 모순 탐지** | **신규 (원점 검증에서 발견)** |

---

# 메타 스킬: 완료 판정 체계 (2개) + SOT 품질 검증 (1개)

> 다른 46개 도구가 "오류를 찾는" 도구라면, 이 2개는 **"더 이상 찾을 오류가 없다는 것을 증명하는"** 도구

## A-47. `/final-review` 스킬

**목적**: "이것이 최종본인가?"에 대한 **결정론적 판정**

### 해결하는 문제
```
"최종본이야?" → "네" → 수정사항 발견 → "최종본이야?" → 무한루프
→ /final-review가 14개 체크리스트로 FINAL/NOT_FINAL 판정
→ FINAL 판정 시 final_review_stamp.json 생성
→ 이후 같은 질문 → stamp 확인 → 즉답 (루프 차단)
```

### 3가지 모드
| 모드 | 명령어 | 대상 |
|------|--------|------|
| 모드 A | `/final-review EA-01` | EA/CM 산출물 최종 판정 |
| 모드 B | `/final-review toolset` | 도구 체계 완전성 판정 |
| 모드 C | `/final-review phase0 --full` | Phase 전체 완료 판정 |

### 판정 기준 (모드 A: 14개 체크리스트)
```
FR-A01: Layer A 결정론적 검증 PASS
FR-A02: Layer B AI 의미적 검증 PASS
FR-A03: 적대적 감사 CLEAN
FR-A04: SOT 원본 대조 MATCH
FR-A05: Quality Gate GOLD/SILVER
FR-A06: 교차 검증 일관성
FR-A07: source_text 물리적 존재
FR-A08: 후반부 커버리지 ≥ 20%
FR-A09: 이전 버전 대비 회귀 없음
FR-A10: 메타데이터 정합성
FR-A11: 표준 키 준수
FR-A12: LOCK 값 일관성
FR-A13: JSON 구조 무결성
FR-A14: 신뢰도 하한선 (confidence ≥ 0.7)
```

### 사용자 해야 할 것
```
없음 (A그룹 — Claude가 파일만 만들면 됨)
```

---

## A-48. `/completeness-map` 스킬

**목적**: 오류 유형별 도구 커버리지 **시각화** + 빈 곳 식별

### 해결하는 문제
```
"이 도구가 전부야? 더 있는 거 아니야?" → 불안
→ /completeness-map이 15개 오류 카테고리 × 4개 검증 계층 매트릭스 생성
→ 빈 셀 = 0이면 "COMPLETE" → 더 이상 추가 불필요 증명
```

### 사용자 해야 할 것
```
없음 (A그룹)
```

### 실행 방법
```
/completeness-map              — 현재 커버리지 매트릭스 출력
/completeness-map update       — 매트릭스 + 빈 곳 해결 방안
```
