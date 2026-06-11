---
tags: [type/concept, module/COND, status/COND, tier/T2, version/V2]
aliases: [CAT-E, Education 모듈, 교육 COND]
created: 2026-06-11
---

# COND CAT-E: Education (7개)

## 정의
COND 106개 중 교육/학습 카테고리. 적응형 학습(Knowledge Tracing), 시험 준비(IRT/CAT), 교육 컨텐츠 생성(Bloom 분류), 평가/채점, 대화형 튜토리얼(소크라테스식), 학습 분석(xAPI), 언어 학습(SM-2/CEFR)을 담당한다. 모듈 ID 범위 #91-#94, #113-#115. 7/7 L3 승급 완료(2026-04-19).

## 모듈 목록 (7)
| ID | 이름 | 핵심 기술 |
|---|---|---|
| COND-091 | 개인화 학습경로 (HIGH) | BKT/DKT hybrid + Knowledge Graph DAG + IRT 3-PL |
| COND-092 | 시험준비 도우미 | IRT 3-PL + CAT(Maximum Fisher Information) + SM-2 |
| COND-093 | 교육 컨텐츠 생성 (HIGH) | LLM 3-stage chain + Bloom's Taxonomy 6 |
| COND-094 | 교육 평가 도구 | AES + LLM grading + self-consistency + 표절 탐지 |
| COND-113 | 대화형 튜토리얼 | Socratic + Scaffolding 4 hint levels |
| COND-114 | 학습 분석 | xAPI/Caliper + LightGBM dropout 예측 + PII fail-closed |
| COND-115 | 언어 학습 | Anki SM-2 ease [1.3, 2.5] + CEFR A1~C2 + STT/TTS |

## 등장 도메인
- [[T2-COND-Modules]] — 정본 소유 (2-2 COND 카테고리 체계)
- [[T3-Education]] — COND-091/092/093 교육 평가·학습경로 교차 참조
- [[T3-A2A-Protocol]] — COND-113 소크라테스식 대화 모델 연동
- [[T2-Blue-Node]] — Learning Node가 주요 소비 (Permission P1, 승인 후 활성)

## 값·수치 (LOCK 여부)
- Mixin: `EducationMixin` (학습자 프로필, 진도 추적, 적응형 알고리즘) / Config Group: `education_config`
- 의존성: spaCy, IRT 엔진 / CAT-B(지식 그래프)·CAT-A(ML 추론) 소비
- §13.1 완성도 매트릭스 8항목 × 7모듈 = 56/56 전수 충족 (LOCK-CD-04/05/06/08/10 준수)

## 원본 경로
- `D:\VAMOS\docs\sot 2\2-2_COND-Modules-Detail\COND_MODULES_DETAIL_구조화_종합계획서.md` (L67~76)
- `D:\VAMOS\docs\sot 2\2-2_COND-Modules-Detail\05_cat-e-education\_index.md`
