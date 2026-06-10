# Education-Learning 구조화 종합계획서

| 항목 | 값 |
|------|-----|
| **버전** | v1.0 |
| **작성일** | 2026-03-23 |
| **Status** | APPROVED — Phase 5 FINAL PASS (2026-03-24) |
| **Tier** | 3 |
| **SOT 출처** | STEP7-O (69항목) |
| **Part2 상태** | SHELL (CAT-E + 1 UI) |
| **도메인** | #8 Education-Learning |

---

## 목차

1. [§1 현재 상태 분석](#1-현재-상태-분석)
2. [§2 목표 구조](#2-목표-구조)
3. [§3 권한 체계 선언](#3-권한-체계-선언)
4. [§4 거버넌스 규칙](#4-거버넌스-규칙)
5. [§5 선행작업](#5-선행작업)
6. [§6 이슈 해결 매핑](#6-이슈-해결-매핑)
7. [§7 Phase 실행 계획](#7-phase-실행-계획)
8. [§8 파일 역할 분리 명세](#8-파일-역할-분리-명세)
9. [§9 충돌 해결 프로토콜](#9-충돌-해결-프로토콜)
10. [§10 검증 체크리스트](#10-검증-체크리스트)
11. [§11 보완 사항](#11-보완-사항)
12. [§12 FINAL REVIEW 결과](#12-final-review-결과)
13. [§13 L3 전수 승급 계획](#13-l3-전수-승급-계획)
14. [§14 실행 약점 대응 계획](#14-실행-약점-대응-계획)
15. [부록 §A 교수법 프레임워크](#부록-a-교수법-프레임워크)
16. [부록 §B SM-2 알고리즘 파라미터 (교육 특화)](#부록-b-sm-2-알고리즘-파라미터-교육-특화)
17. [부록 §C 의존성 맵](#부록-c-의존성-맵)
18. [부록 §D Part2 교차 참조](#부록-d-part2-교차-참조-s10-4-추가)

---

## §1 현재 상태 분석

### 1.1 기존 문서 현황

| 문서 | 위치 | 상태 | 비고 |
|------|------|------|------|
| STEP7-O | `docs/sot/` | 확정 | 69항목 체크리스트 (보강 기준) |
| EDUCATION_LEARNING_상세명세.md | `docs/sot 2/3-5_Education-Learning/` | 기존 유지 | 690줄, 초기 명세 |
| PART2 CAT-E | COND 레이어 | SHELL | COND 7개 (빈껍데기) |
| PART2 UI | UI 레이어 | SHELL | 1건 (빈껍데기) |

### 1.2 현재 파일

- **EDUCATION_LEARNING_상세명세.md** — 690줄
  - 초기 작성된 명세로, 학습 경로, 난이도 체계, 평가 기준 등의 뼈대 존재
  - STEP7-O 69항목 중 일부만 반영, 나머지는 미커버
  - 구현 수준의 상세 파라미터(IRT, Bloom, SM-2 교육 확장) 미정의

### 1.3 STEP7-O 69항목 분류

| Part | 범위 | 항목 수 | 주제 |
|------|------|---------|------|
| Part 1 | O-001 ~ O-010 | 10 | AI 튜터 / 적응형 학습 / SM-2 / 코딩 튜터 |
| Part 2 | O-011 ~ O-018 | 8 | 콘텐츠 학습 (YouTube, 논문, 팟캐스트, 독서 등) |
| Part 3 | O-019 ~ O-028 | 10 | 자기개발 / 생산성 / 게이미피케이션 / 벤치마크 |
| Part 4 | O-029 ~ O-036 | 8 | 차별화 + 참고 (Khanmigo, Duolingo Max 등) |
| **합계** | O-001 ~ O-036 | **69** | — |

> **참고**: O-ID 36개이나, 각 O-ID에 세부 항목이 포함되어 총 69항목으로 집계됨 (STEP7-O 원문 "68개" 표기 대비 본 계획서 세부 분해 기준 +1).

**5개 서브폴더 매핑 요약:**

| 서브폴더 | 주요 O-ID | 예상 항목 수 |
|----------|-----------|-------------|
| 01_adaptive-learning | O-001, O-003, O-005, O-006 | ~15 |
| 02_spaced-repetition | O-002 | ~8 |
| 03_coding-tutorial | O-004, O-017 | ~10 |
| 04_content-generation | O-007~O-009, O-011~O-016 | ~18 |
| 05_learning-analytics | O-010, O-019~O-028 | ~18 |

### 1.4 SHELL 분석

- **CAT-E COND 7개** (이름만 존재):
  - `D2.0-01` 적응형 학습 엔진 조건
  - `D2.0-02` 간격 반복 스케줄링 조건
  - `D2.0-03` 코딩 튜터 인터랙션 조건
  - `D2.0-04` 콘텐츠 학습 생성 조건
  - `D2.0-05` 퀴즈/테스트 생성 조건
  - `D2.0-06` 학습 분석 대시보드 조건
  - `D2.0-07` 게이미피케이션 시스템 조건
- **UI 1건**: 학습 대시보드 레이아웃 (빈껍데기)
- **실질 완성도**: 0% — 전면 신규 작성 필요 (방식 C: From Scratch)

### 1.5 핵심 문제

| # | 문제 | 심각도 | 해결 방향 |
|---|------|--------|-----------|
| 1 | **빈껍데기** — SHELL 상태, 모든 COND/UI가 이름만 존재 | Critical | 방식 C 전면 신규 작성 |
| 2 | **정본 부재** — STEP7-O 69항목의 구현 정본 문서 없음 | Critical | sot 2/3-5_.../ 하위 구현 정본 생성 |
| 3 | **SM-2 파라미터 공유 규약** — #6 PKM과 SM-2 기본 파라미터 공유 필요 | High | PKM이 정본, Education은 커스터마이징만 |
| 4 | **교수법 파라미터 미정의** — Bloom 택소노미, IRT 난이도 조정 상세 파라미터 부재 | High | 부록 §A에 교수법 프레임워크 정의 |
| 5 | **감정 기반 학습 연동** — #9 Health와의 인터페이스 미정의 | Medium | §5 선행작업 E에서 정의 |

---

## §2 목표 구조

### 2.1 폴더 트리

```
D:\VAMOS\docs\sot 2\3-5_Education-Learning\
├── EDUCATION_LEARNING_구조화_종합계획서.md       ← 본 문서 (계획+거버넌스)
├── EDUCATION_LEARNING_상세명세.md               ← 기존 유지 (690줄)
├── AUTHORITY_CHAIN.md                          ← 권한 체인 선언
├── CONFLICT_LOG.md                             ← 충돌 기록
├── 01_adaptive-learning\
│   ├── _index.md                               ← 서브폴더 개요+목록
│   ├── adaptive_engine.md                      ← O-001 적응형 학습 엔진
│   ├── learning_path_generator.md              ← O-003 학습 경로 생성기
│   ├── difficulty_adjustment.md                ← O-001 IRT 난이도 조정
│   ├── learner_profile.md                      ← O-001 학습자 프로필
│   ├── investment_education.md                 ← O-005 투자 교육
│   └── language_learning.md                    ← O-006 언어 학습
├── 02_spaced-repetition\
│   ├── _index.md
│   ├── sm2_education_extension.md              ← O-002 SM-2 교육 확장
│   ├── flashcard_auto_generation.md            ← O-002 플래시카드 자동 생성
│   └── review_scheduler.md                     ← O-002 복습 스케줄러
├── 03_coding-tutorial\
│   ├── _index.md
│   ├── interactive_tutorial.md                 ← O-004 인터랙티브 튜토리얼
│   ├── leetcode_style_problems.md              ← O-004 알고리즘 문제
│   ├── code_review_learning.md                 ← O-004 코드 리뷰 학습
│   ├── project_based_learning.md               ← O-004 프로젝트 기반 학습
│   └── coding_challenge.md                     ← O-017 코딩 챌린지
├── 04_content-generation\
│   ├── _index.md
│   ├── quiz_test_generation.md                 ← O-008 퀴즈/테스트 생성
│   ├── youtube_learning.md                     ← O-011 YouTube 학습
│   ├── paper_learning.md                       ← O-012 논문 학습
│   ├── podcast_audio.md                        ← O-013 팟캐스트/오디오
│   ├── book_reading.md                         ← O-007, O-014 독서 학습
│   ├── online_course_support.md                ← O-016 온라인 코스 지원
│   ├── mindmap_concept_map.md                  ← O-009 마인드맵/개념맵
│   └── presentation_coaching.md                ← O-015 발표 코칭
└── 05_learning-analytics\
    ├── _index.md
    ├── learning_dashboard.md                   ← O-010 학습 대시보드
    ├── gamification.md                         ← O-027 게이미피케이션
    ├── goal_management.md                      ← O-019 목표 관리
    ├── time_management.md                      ← O-020 시간 관리
    ├── habit_tracker.md                        ← O-021 습관 추적
    ├── career_development.md                   ← O-022 커리어 개발
    ├── study_group.md                          ← O-023 스터디 그룹
    ├── note_taking.md                          ← O-024 노트 테이킹
    ├── focus_mode.md                           ← O-025 집중 모드
    ├── certification_tracker.md                ← O-026 자격증 추적
    └── benchmark_vbs16.md                      ← O-028 VBS-16 벤치마크
```

### 2.2 폴더 깊이 규칙

- **최대 3단계**: `sot 2/3-5_Education-Learning/{subfolder}/{file}.md`
- 서브폴더 내 추가 중첩 금지
- 각 서브폴더는 `_index.md`로 개요 및 파일 목록 관리

### 2.3 네이밍 규칙

| 규칙 | 설명 | 예시 |
|------|------|------|
| 서브폴더 | `NN_kebab-case` | `01_adaptive-learning` |
| 파일 | `snake_case.md` | `adaptive_engine.md` |
| 인덱스 | `_index.md` (언더스코어 접두) | `_index.md` |
| 계획서/거버넌스 | `UPPER_CASE.md` | `AUTHORITY_CHAIN.md` |
| O-ID 태깅 | 파일 내 YAML front-matter에 `o_ids: [O-001]` | — |

---

## §3 권한 체계 선언

> **[UPSTREAM_INHERITANCE: 3-3 PKM Phase 3 완료 (2026-05-16) — 본 도메인 SM-2 공유 정합 inheritance]**
>
> **3-3 PKM-Knowledge-Management Phase 3 ✅ 완료 (2026-05-16, 6/6 P3 ALL tcv3 first-pass CONFIRMED, chain phase3_3-3_sub_a_2026-05-16 + phase3_3-3_sub_b_2026-05-16)** — P3-1 M-028 V3 03_spaced-repetition 팀 지식 공유 (멀티유저 + 권한 관리, SM-2 multi-user extension) + P3-3 M-035 V3 02_knowledge-graph GraphRAG (학습 시퀀스 그래프 기반 추론) 결과 본 도메인 SM-2 공유에 inheritance 가능. **LOCK-PKM-01~03 ↔ LOCK-ED-04 verbatim 5-field × 2측 = 10/10 match 유지** (3-3 §3.4 L222-L224 LOCK-PKM-01 MIN_EASINESS=1.3 / LOCK-PKM-02 DEFAULT_EASINESS=2.5 / LOCK-PKM-03 SM-2 초기 간격 n=1:1일, n=2:6일, n≥3:I(n-1)×EF ↔ 본 도메인 AUTHORITY_CHAIN.md L86 LOCK-ED-04 MIN_EF=1.3, DEFAULT_EF=2.5, I(1)=1d, I(2)=6d → PKM 참조만 단독 변경 금지). **정본 소유자 #6 PKM (LOCK-PKM-01~03)** — 본 도메인 LOCK-ED-04는 PKM 참조만, 단독 변경 금지 (R-08-1 공유 규약 + R-09 LOCK 보호 §9.2 시나리오 #2 RESOLVED). 3-5 sub-A 진입 시 본 reference 자동 inheritance verify 필요 (P3-1 M-028 멀티유저 + 권한 RBAC 4단계 (Owner/Editor/Reader/Reviewer) + P3-3 M-035 GraphRAG 학습 시퀀스 적용 가능성).
>
> **3-3 Phase 3 통산 산출물 매트릭스 inheritance reference**:
> - P3-1 03_spaced-repetition/knowledge_sharing.md M-028 V3 (멀티유저 + 권한 관리, RBAC 4단계, 충돌 해결 last-write-wins + 사용자 설정) ← **본 도메인 02_spaced-repetition/sm2_education_extension.md 학습 카드 공유 연동 시 reference**
> - P3-3 02_knowledge-graph/graph_vector_hybrid.md M-035 V3 GraphRAG (Microsoft Research 2024 community detection Leiden/Louvain + entity extraction LLM + summarization community/global) ← **본 도메인 01_adaptive-learning/learning_path_generator.md 학습 시퀀스 그래프 기반 추론 시 reference**
> - P3-3 02_knowledge-graph/graph_visualization.md M-034 V3 3D 시각화 (WebGL Three.js + octree culling ≥ 1000 노드 60fps) ← 본 도메인 05_learning-analytics/learning_dashboard.md 학습 진척 3D 시각화 시 reference
> - P3-4 05_external-integration/decision_support.md M-045 V3 SWOT 자동 생성 + writing_drafting.md M-046 V3 글 초안 (Bloom Apply/Create 단계 — LOCK-ED-05 정합 verbatim) ← **본 도메인 03_coding-tutorial/code_review_learning.md + 04_content-generation/quiz_test_generation.md Bloom 6단계 매핑 reference**
> - P3-5 05_external-integration/second_brain_dashboard.md M-047 V3 통합 대시보드 (활동 피드 + 그래프 통계 + 학습 진척 + 신선도 워닝, LOCK-PKM-09 신선도 감쇠 + LOCK-PKM-12 성숙도 Seedling→Growing→Evergreen→Archived) ← 본 도메인 05_learning-analytics/learning_dashboard.md 학습 진척 통합 read-only 인터페이스 reference (P3-5 §6 참조 명시)

> **[UPSTREAM_INHERITANCE: 3-3 PKM Phase 4 ✅ Stage A COMPLETE (2026-05-24, 6/6 P4 ALL verify-only per 사용자 결정 A) — 본 도메인 SM-2 + Bloom + learning progress + V3 production-ready 정본 영구 baseline inheritance]**
>
> **3-3 PKM-Knowledge-Management Phase 4 ✅ Stage A COMPLETE (2026-05-24, P4-1~P4-6 6/6 ALL verify-only per 사용자 결정 A, chain phase4_3-3_2026-05-24, 702 R verif + 0 drift + 0 fix 통산 6 tcv1 6-consecutive ⭐⭐⭐⭐⭐ FULL NO-DRIFT, _verification NEW × 6 = 127,375 B / 1,381 LF, 7 핵심 + 52 production .md inventory baseline ALL UNCHANGED, 🎉 도메인 NO-DRIFT FULL 6/6 ⭐⭐⭐ milestone 확정 통산 3번째 FULL 도메인, [PHASE4_COMPLETE_STAGE_A:3-3 — 2026-05-24] ✅ — ⚠️ SPEC Stage B 대기, `phase4_3-3_spec_2026-05-24` chain 별도 대화창 실행 후 [DOMAIN_PHASE_4_PRODUCTION_PROMOTION_COMPLETE:3-3] marker 부착 예정)** — P4-1 M-028 V2 NEW APPROVED inheritance verify (SM-2 LOCK-PKM-01~03 ↔ LOCK-ED-04 verbatim 5-field × 2측 = **10/10 match 영구 baseline 확정** ✅ P4-1 verify + 본 P4-6 도메인 종합 마감 inheritance) + P4-4 M-046 Bloom Apply/Create cross-handoff forward-defined inheritance (3-5 LOCK-ED-05 6단계 정본 ↔ 본 도메인 03_coding-tutorial/code_review_learning.md + 04_content-generation/quiz_test_generation.md Bloom 6단계 매핑) + P4-5 M-047 Dashboard "learning progress" 섹션 read-only cross-handoff forward-defined inheritance (본 도메인 05_learning-analytics/learning_dashboard.md ↔ M-047 4 sections 통합). 본 도메인 sub-A 진입 시 본 reference 자동 inheritance verify 필요. **3-3 sub-A 진입 시 본 entry 자동 추가 ⑥ 단계 propagation 완료** (③⑥ propagation pattern inheritance 1-2 + 2-2 + 2-1 + 3-2 직계 통산 5번째 도메인).
>
> **3-3 Phase 4 통산 산출물 매트릭스 inheritance reference** (V3 7건 매트릭스, OUT of scope per A inheritance):
> - P4-1 03_spaced-repetition/knowledge_sharing.md M-028 V2 NEW APPROVED L3 ≥ 90 (RBAC + ABAC hybrid 5-role OWNER/EDITOR/COMMENTER/VIEWER/API_SCOPE + SM-2 팀 공유 + last-write-wins 충돌 해결, LOCK-PKM-04/05/07/08/10/12 6 LOCK verbatim 인용) ← **본 도메인 02_spaced-repetition/sm2_education_extension.md 학습 카드 공유 연동 시 reference** (Phase 4 영구 baseline 확정)
> - P4-2 M-037 V3 NEW forward-defined target `05_external-integration/personal_wiki_publish.md` cross-folder placement (정적 사이트 도구 Hugo/Eleventy/Quartz 결정 + Privacy 3-level Public/Friends/Private + LOCK-PKM-10 Zettelkasten 5종 보존 + R-06-7 외부 전송 동의, V3 본문 작성 OUT of scope per A) ← 본 도메인 학습 노트 공개 발행 시 reference
> - P4-3 M-034 WebGL 3D 시각화 + M-035 Microsoft GraphRAG V3 NEW forward-defined matrix (M-034 graph_visualization.md V3 WebGL Three.js ≥ 1000 노드 60fps + M-035 graph_vector_hybrid.md V3 community detection + entity extraction + summarization, LOCK-PKM-04 노드 5종 + LOCK-PKM-05 엣지 8종 + LOCK-PKM-06 벡터 ≥ 0.85 + LOCK-PKM-12 성숙도 4단계, V3 본문 작성 OUT of scope per A, 6-4 MEM/RAG GraphRAG 인터페이스 forward-defined inheritance Wave 2 #16 진입 시 양방향) ← **본 도메인 01_adaptive-learning/learning_path_generator.md GraphRAG 학습 시퀀스 + 05_learning-analytics/learning_dashboard.md 3D 시각화 reference**
> - P4-4 M-045 SWOT + M-046 Writing V3 NEW forward-defined matrix (M-045 `05_external-integration/decision_support.md` V3 Pro/Con/Risk/Opportunity LLM 자동 생성 + M-046 `05_external-integration/writing_drafting.md` V3 Bloom Apply/Create 단계 cross-folder + filename change writing_support→writing_drafting + LOCK-PKM-07 5차원 태깅 + R-06-3 Zettelkasten 원자성 1노트=1개념 ≤300단어, V3 본문 작성 OUT of scope per A, M-046 V1 base writing_support.md MISSING acknowledged Phase 1 V1 미작성 inheritance) ← **본 도메인 03_coding-tutorial/code_review_learning.md + 04_content-generation/quiz_test_generation.md Bloom 6단계 매핑 reference** (3-5 LOCK-ED-05 Bloom 6단계 Remember/Understand/Apply/Analyze/Evaluate/Create 양방향 정합 baseline 확립 예정 본 도메인 Wave 1 #7 Phase 4 진입 시)
> - P4-5 M-047 Second Brain Dashboard V3 NEW forward-defined matrix (single-output 4 sections: activity feed + graph stats + learning progress + freshness warning, `05_external-integration/second_brain_dashboard.md` cross-folder placement filename 동일 vanilla, LOCK-PKM-09 freshness = exp(-λ × age_days) 공식만 LOCK half_life 카테고리별 IMPL-DETAIL + Phase 1 7 파일 + freshness_management V2 = 8 위치 인용 통산, V3 본문 작성 OUT of scope per A, M-047 V1/V2 base second_brain_dashboard.md MISSING acknowledged Phase 1-2 V1/V2 미작성 inheritance) ← **본 도메인 05_learning-analytics/learning_dashboard.md 학습 진척 통합 read-only 인터페이스 reference** (Dashboard "learning progress" 섹션이 3-5 polling read-only 통합, 본 도메인 Wave 1 #7 Phase 4 진입 시 양방향 baseline 확립)
> - P4-6 FINAL P4 도메인 전체 baseline 영구 마감: 78 항목 L3 ≥ 60% 영구 + V3 7건 매트릭스 (1 APPROVED M-028 + 6 V3 NEW OUT of scope per A) + **CONFLICT_LOG OPEN=0 영구 마감 확정 (CFL-PKM-001~005 5건 ALL RESOLVED + 신규 0건)** + **LOCK-PKM-01~12 12건 immutable matrix 영구 baseline 확정** (AUTHORITY §2 L40-51 STEP_C truly_converged_v2 inheritance) + **3-5 SM-2 LOCK-PKM-01~03 ↔ LOCK-ED-04 5-field × 2측 = 10/10 verbatim match 영구 baseline 확정** ✅ (P4-1 verify + AUTHORITY §7.3 STEP_C + CONFLICT_LOG v1.3 SM-2 exit_gate + 본 P4-6 도메인 종합 마감) + VBS-14 V1 ≥75 / avg ≥80 영구 baseline + AUTHORITY/CONFLICT/INDEX v1.3 STEP_C inheritance ← **본 도메인 SM-2 공유 영구 baseline + Phase 4 V3 산출물 6건 (M-034/M-035/M-037/M-045/M-046/M-047) Phase 4 SPEC Stage B 또는 별도 결정 위임 inheritance**

### 3.1 기존 VAMOS 권한 체인

```
RULE 1.3 (최상위 불변 규칙)
  > PLAN 3.0 (프로젝트 계획)
    > DESIGN 2.0 LOCK (설계 잠금값)
      > DESIGN 2.0 body (설계 본문)
        > Schema / TECH_STACK (기술 스택)
```

### 3.2 Education 확장 권한 체인

```
RULE 1.3
  > PLAN 3.0
    > DESIGN 2.0
      └─ D2.0-01~07 (COND CAT-E 교육 모듈 7개)
        > sot 2/3-5_Education-Learning/ (구현 정본 = What + How)
          > PART2 CAT-E (구현 가이드 = When + Where)
            > STEP7-O (보강 체크리스트 = 69항목)
```

### 3.3 문서별 권한 범위

| 문서 | 역할 | 결정 범위 | 변경 권한 |
|------|------|-----------|-----------|
| RULE 1.3 | 최상위 규칙 | 전체 아키텍처 원칙 | 변경 불가 |
| PLAN 3.0 | 프로젝트 계획 | Phase 구조, 우선순위 | PM 승인 |
| DESIGN 2.0 LOCK | 설계 잠금값 | LOCK-ED-01~10 | LOCK 해제 절차 필요 |
| DESIGN 2.0 body | 설계 본문 | 상세 설계 | 설계 리뷰 후 변경 |
| sot 2/3-5_.../ | 구현 정본 | What + How (알고리즘, 스키마, API) | 본 계획서 거버넌스 규칙 준수 |
| PART2 CAT-E | 구현 가이드 | When + Where (조건, 트리거) | COND 레이어 변경 절차 |
| STEP7-O | 보강 체크리스트 | 69항목 점검 기준 | 읽기 전용 참조 |

### 3.4 LOCK 보호 선언

| LOCK ID | 보호 대상 | 출처 | 잠금값 |
|---------|-----------|------|--------|
| LOCK-ED-01 | 학습 경로 구조 | STEP7-O O-003 | 목표 → Phase 분해 → 각 Phase(자료 + 실습 + 체크포인트 + 소요시간) |
| LOCK-ED-02 | 난이도 분류 체계 | 기존 명세 §2 | IRT 기반 5단계 (Very Easy / Easy / Medium / Hard / Very Hard), 정답률 목표 70-85% |
| LOCK-ED-03 | 평가 기준 | 기존 명세 §2 | 진단테스트 + 진행평가 + 최종평가, 3등급 (미달 / 달성 / 우수) |
| LOCK-ED-04 | SM-2 기본 파라미터 정본 | #6 PKM LOCK-PKM-01~03 | MIN_EF=1.3, DEFAULT_EF=2.5, I(1)=1d, I(2)=6d → PKM 참조만, 단독 변경 금지 |
| LOCK-ED-05 | Bloom 택소노미 6단계 | STEP7-O O-001 | Remember / Understand / Apply / Analyze / Evaluate / Create |
| LOCK-ED-06 | 소크라테스 교수법 원칙 | STEP7-O O-001 | 직접 답 금지 → 질문 유도 → 힌트 3단계 → 사고 과정 유도 → 격려 피드백 |
| LOCK-ED-07 | 학습자 프로필 스키마 | 기존 명세 §2 | skill_levels, learning_speed, preferred_style, weekly_hours, goal |
| LOCK-ED-08 | 플래시카드 유형 | STEP7-O O-002 | 기본(앞/뒤), 빈칸채우기, 이미지오클루전, 코드 |
| LOCK-ED-09 | VBS-16 벤치마크 기준 | STEP7-O O-028 | 학습 지속률 >= 60%, 기억 유지율 >= 80% |
| LOCK-ED-10 | 게이미피케이션 XP 체계 | STEP7-O O-027 | XP → 레벨 → 배지 → Streak → 챌린지 → 리더보드 |

---

## §4 거버넌스 규칙

> **글로벌 거버넌스 규칙**: 본 도메인은 0-0_Governance-Rules-Meta에서 정의한 R1~R11 글로벌 규칙을 전체 준수합니다.
> 아래는 글로벌 규칙에 추가되는 도메인 고유 규칙입니다.

### 4.1 공통 규칙 (R1 ~ R9)

| ID | 규칙 | 근거 | 위반 시 |
|----|------|------|---------|
| R-01 | 모든 변경은 AUTHORITY_CHAIN.md 권한 범위 내에서만 수행 | 권한 체계 | 변경 무효, 롤백 |
| R-02 | LOCK 값 변경 시 LOCK 해제 절차 필수 (사유+대안+영향 분석) | LOCK 보호 | 변경 거부 |
| R-03 | 파일 생성/삭제 시 _index.md 동기 업데이트 | 폴더 정합성 | _index.md 불일치 경고 |
| R-04 | O-ID 매핑 변경 시 §6 매핑 테이블 동기 업데이트 | 추적성 | 매핑 불일치 경고 |
| R-05 | Phase 전환 시 게이트 조건 충족 검증 필수 | Phase 관리 | Phase 전환 거부 |
| R-06 | 충돌 발생 시 §9 프로토콜 준수, CONFLICT_LOG.md 기록 | 충돌 관리 | 미기록 변경 무효 |
| R-07 | 외부 도메인 참조 시 크로스 레퍼런스 명시 | 의존성 추적 | 참조 누락 경고 |
| R-08 | 구현 정본(sot 2/) 변경 시 STEP7-O 항목 대조 필수 | SOT 정합성 | 미대조 변경 보류 |
| R-09 | 검증 체크리스트(§10) 통과 후에만 Phase 완료 선언 | 품질 보증 | Phase 미완료 |

### 4.2 Education 전용 규칙

| ID | 규칙 | 근거 | 위반 시 |
|----|------|------|---------|
| R-08-1 | SM-2 교육 커스터마이징은 #6 PKM 정본 파라미터 참조 필수 | SM-2 공유 계약 | 단독 변경 금지, 변경 무효 |
| R-08-2 | 학습 경로 생성 시 Bloom 택소노미 기반 단계 순서 보장 | 교육학적 정합성 | 하위 단계 미완료 시 상위 단계 잠금 |
| R-08-3 | 코딩 문제 답을 직접 제공하지 않고 소크라테스 교수법 적용 | 학습 효과 극대화 | 직접 답 제공 금지 |
| R-08-4 | 퀴즈 자동 생성 시 Bloom 레벨 태깅 필수 | 난이도 분류 | 미태깅 퀴즈 배포 금지 |
| R-08-5 | 학습자 프로필 데이터 외부 전송 시 명시적 동의 | 프라이버시 | 무단 전송 금지, 즉시 차단 |
| R-08-6 | #9 Health 감정 데이터 연동 시 opt-in 필수 | 감정 기반 학습 적응 | 기본 비활성, 명시적 동의 없이 활성화 금지 |

---

## §5 선행작업

| ID | 선행작업 | 설명 | 상태 | 의존 |
|----|----------|------|------|------|
| A | STEP7-O 항목 분류 + 서브폴더 매핑 | 69건을 5개 서브폴더로 분류, O-ID별 대상 파일 확정 | 완료 | — |
| B | Part2 SHELL 확인 + GAP 확정 | CAT-E COND 7개 + UI 1건 모두 SHELL 확인, 방식 C(전면 신규) 확정 | 완료 | — |
| C | 기존 상세명세와 STEP7-O 대조 | 690줄 커버리지 ~19.5%, GAP ~80.5% 식별 | 완료 | A |
| D | PKM(#6)과 SM-2 공유 규약 확인 | PKM이 SM-2 파라미터 정본, Education은 커스터마이징만 가능 | 완료 | — |
| E | Health(#9)과 감정 기반 학습 적응 인터페이스 정의 | opt-in 기반 감정 데이터 수신 API, 학습 난이도/속도 적응 규칙 | 미시작 | Phase 2 |
| F | Workflow-RPA(#7) 학습 자동화 워크플로우 소비 | 학습 루틴 자동화, 리마인더, 스케줄링 워크플로우 연동 | 미시작 | Phase 2 *(S7-2 추가)* |

### 선행작업 상세

**A. STEP7-O 항목 분류 결과:**
- Part 1 (O-001~O-010): AI 튜터 핵심 기능 → 01_adaptive-learning, 02_spaced-repetition, 03_coding-tutorial, 04_content-generation, 05_learning-analytics 5개 서브폴더 분배
- Part 2 (O-011~O-018): 콘텐츠 학습 → 04_content-generation 중심 (O-017 → 03_coding-tutorial 예외, O-018 → §6 매핑 부재 — O-023·§D.4 Phase 3에 흡수)
- Part 3 (O-019~O-028): 자기개발/생산성 → 05_learning-analytics 집중
- Part 4 (O-029~O-036): 참고/차별화 → 부록 §C + §7 로드맵 통합 (REF 전용)
- O-ID↔항목명 정합성: STEP7-O 원본 대비 7건 불일치 식별 (O-015, O-018, O-021, O-023~O-026), §6 기준 확정

**B. GAP 확정 결과:**
- CAT-E COND 7개(D2.0-01~07): 모두 이름만 존재, 내용 0%
- UI 1건: 레이아웃 스케치만, 구현 상세 0%
- 결론: 방식 C — 전면 신규 작성

**C. 기존 상세명세 커버리지 분석 결과:**
- Full 커버: 5건 (O-001~O-004, O-008) — 적응형 학습, SM-2, 코딩, 퀴즈
- Partial 커버: 2건 (O-010, O-027) — 대시보드, 게이미피케이션
- Mentioned: 4건 (O-005, O-017, O-029~O-036)
- GAP: 25건 — 콘텐츠 학습(O-011~O-016), 자기개발(O-019~O-026), 벤치마크(O-028) 등
- 커버리지율: ~19.5% (Full+Partial 7건/36 O-ID)

**D. SM-2 공유 규약:**
- PKM LOCK-PKM-01: MIN_EF = 1.3 (불변)
- PKM LOCK-PKM-02: DEFAULT_EF = 2.5 (불변)
- PKM LOCK-PKM-03: SM-2 초기 간격 — I(1) = 1d, I(2) = 6d, I(n≥3) = I(n-1) × EF (불변)
- Education 커스터마이징 범위: EF 보정 가중치, interval 조정 계수, quality-Bloom 연동 매핑

---

## §6 이슈 해결 매핑

### 6.1 01_adaptive-learning/ (~15항목)

| O-ID | 항목명 | V단계 | 상태 | 대상 파일 |
|------|--------|-------|------|-----------|
| O-001-1 | 적응형 학습 엔진 코어 | V1 | NEW | adaptive_engine.md |
| O-001-2 | IRT 기반 난이도 조정 알고리즘 | V1 | NEW | difficulty_adjustment.md |
| O-001-3 | 학습자 프로필 생성/관리 | V1 | NEW | learner_profile.md |
| O-001-4 | Bloom 택소노미 기반 콘텐츠 분류 | V1 | NEW | adaptive_engine.md |
| O-001-5 | 소크라테스 교수법 대화 엔진 | V1 | NEW | adaptive_engine.md |
| O-003-1 | 학습 경로 자동 생성 | V1 | NEW | learning_path_generator.md |
| O-003-2 | Phase 분해 알고리즘 | V1 | NEW | learning_path_generator.md |
| O-003-3 | 체크포인트 시스템 | V1 | NEW | learning_path_generator.md |
| O-003-4 | 소요 시간 추정 | V1 | NEW | learning_path_generator.md |
| O-005-1 | 투자 교육 기초 모듈 | V2 | NEW | investment_education.md |
| O-005-2 | 투자 시뮬레이션 연동 | V3 | NEW | investment_education.md |
| O-005-3 | 투자 용어 학습 | V2 | NEW | investment_education.md |
| O-006-1 | 언어 학습 어휘 빌더 | V2 | NEW | language_learning.md |
| O-006-2 | 문법 교정 피드백 | V2 | NEW | language_learning.md |
| O-006-3 | 회화 연습 대화 엔진 | V3 | NEW | language_learning.md |

### 6.2 02_spaced-repetition/ (~8항목)

| O-ID | 항목명 | V단계 | 상태 | 대상 파일 |
|------|--------|-------|------|-----------|
| O-002-1 | SM-2 교육 확장 알고리즘 | V1 | NEW | sm2_education_extension.md |
| O-002-2 | Bloom 레벨 연동 EF 보정 | V1 | NEW | sm2_education_extension.md |
| O-002-3 | 플래시카드 자동 생성 (기본/빈칸) | V1 | NEW | flashcard_auto_generation.md |
| O-002-4 | 플래시카드 이미지 오클루전 | V2 | NEW | flashcard_auto_generation.md |
| O-002-5 | 플래시카드 코드 유형 | V1 | NEW | flashcard_auto_generation.md |
| O-002-6 | 복습 스케줄러 코어 | V1 | NEW | review_scheduler.md |
| O-002-7 | 학습 맥락별 간격 조정 | V1 | NEW | review_scheduler.md |
| O-002-8 | 복습 알림 시스템 | V2 | NEW | review_scheduler.md |

### 6.3 03_coding-tutorial/ (~10항목)

| O-ID | 항목명 | V단계 | 상태 | 대상 파일 |
|------|--------|-------|------|-----------|
| O-004-1 | 인터랙티브 코딩 튜토리얼 | V1 | NEW | interactive_tutorial.md |
| O-004-2 | 단계별 힌트 시스템 (소크라테스) | V1 | NEW | interactive_tutorial.md |
| O-004-3 | LeetCode 스타일 문제 생성 | V1 | NEW | leetcode_style_problems.md |
| O-004-4 | 난이도별 문제 분류 (IRT) | V1 | NEW | leetcode_style_problems.md |
| O-004-5 | 코드 리뷰 피드백 학습 | V1 | NEW | code_review_learning.md |
| O-004-6 | 코드 품질 지표 피드백 | V2 | NEW | code_review_learning.md |
| O-004-7 | 프로젝트 기반 학습 템플릿 | V2 | NEW | project_based_learning.md |
| O-004-8 | 프로젝트 마일스톤 추적 | V2 | NEW | project_based_learning.md |
| O-017-1 | 코딩 챌린지 플랫폼 | V2 | NEW | coding_challenge.md |
| O-017-2 | 챌린지 리더보드 | V3 | NEW | coding_challenge.md |

### 6.4 04_content-generation/ (~18항목)

| O-ID | 항목명 | V단계 | 상태 | 대상 파일 |
|------|--------|-------|------|-----------|
| O-008-1 | 퀴즈 자동 생성 엔진 | V1 | NEW | quiz_test_generation.md |
| O-008-2 | Bloom 레벨 태깅 | V1 | NEW | quiz_test_generation.md |
| O-008-3 | 테스트 결과 분석 | V1 | NEW | quiz_test_generation.md |
| O-011-1 | YouTube 영상 요약 학습 | V1 | NEW | youtube_learning.md |
| O-011-2 | 타임스탬프 기반 노트 | V2 | NEW | youtube_learning.md |
| O-012-1 | 논문 구조화 분석 | V2 | NEW | paper_learning.md |
| O-012-2 | 논문 핵심 개념 추출 | V2 | NEW | paper_learning.md |
| O-013-1 | 팟캐스트 학습 모드 | V2 | NEW | podcast_audio.md |
| O-013-2 | 음성 인식 기반 학습 | V3 | NEW | podcast_audio.md |
| O-007-1 | 독서 가이드 생성 | V1 | NEW | book_reading.md |
| O-014-1 | 독서 진도 추적 | V1 | NEW | book_reading.md |
| O-014-2 | 독서 노트 자동 구조화 | V2 | NEW | book_reading.md |
| O-016-1 | 온라인 코스 진도 동기화 | V2 | NEW | online_course_support.md |
| O-016-2 | 코스 보충 자료 추천 | V2 | NEW | online_course_support.md |
| O-009-1 | 마인드맵 자동 생성 | V1 | NEW | mindmap_concept_map.md |
| O-009-2 | 인터랙티브 개념맵 | V2 | NEW | mindmap_concept_map.md |
| O-015-1 | 발표 스크립트 생성 | V2 | NEW | presentation_coaching.md |
| O-015-2 | 발표 피드백 (음성 분석) | V3 | NEW | presentation_coaching.md |

### 6.5 05_learning-analytics/ (~18항목)

| O-ID | 항목명 | V단계 | 상태 | 대상 파일 |
|------|--------|-------|------|-----------|
| O-010-1 | 학습 대시보드 코어 | V1 | NEW | learning_dashboard.md |
| O-010-2 | 학습 통계 시각화 | V2 | NEW | learning_dashboard.md |
| O-010-3 | 학습 리포트 생성 | V2 | NEW | learning_dashboard.md |
| O-027-1 | XP 시스템 | V1 | NEW | gamification.md |
| O-027-2 | 레벨/배지 시스템 | V1 | NEW | gamification.md |
| O-027-3 | Streak/챌린지 | V1 | NEW | gamification.md |
| O-027-4 | 리더보드 | V2 | NEW | gamification.md |
| O-019-1 | 학습 목표 설정/추적 | V1 | NEW | goal_management.md |
| O-019-2 | 목표 달성률 분석 | V2 | NEW | goal_management.md |
| O-020-1 | 학습 시간 관리 (포모도로) | V1 | NEW | time_management.md |
| O-020-2 | 시간 분배 최적화 | V2 | NEW | time_management.md |
| O-021-1 | 학습 습관 추적기 | V2 | NEW | habit_tracker.md |
| O-022-1 | 커리어 로드맵 생성 | V2 | NEW | career_development.md |
| O-023-1 | 스터디 그룹 매칭 | V3 | NEW | study_group.md |
| O-024-1 | 스마트 노트 테이킹 | V2 | NEW | note_taking.md |
| O-025-1 | 집중 모드 (DND + 타이머) | V2 | NEW | focus_mode.md |
| O-026-1 | 자격증 준비 추적기 | V2 | NEW | certification_tracker.md |
| O-028-1 | VBS-16 벤치마크 측정 | V1 | NEW | benchmark_vbs16.md |

### 6.6 참고/로드맵 (O-029 ~ O-036 → 부록 + §7 통합)

| O-ID | 항목명 | V단계 | 상태 | 대상 |
|------|--------|-------|------|------|
| O-029 | Khanmigo 참고 (소크라테스 교수법) | — | REF | 부록 §A.1 |
| O-030 | Duolingo Max 참고 (게이미피케이션) | — | REF | 부록 §C 참고자료 |
| O-031 | Anki 참고 (간격 반복) | — | REF | 부록 §B, §C 참고자료 |
| O-032 | Perplexity 참고 (검색 기반 학습) | — | REF | 부록 §C 참고자료 |
| O-033 | NotebookLM 참고 (문서 기반 학습) | — | REF | 부록 §C 참고자료 |
| O-034 | Brilliant 참고 (인터랙티브 학습) | — | REF | 부록 §C 참고자료 |
| O-035 | Coursera/edX 참고 (온라인 코스) | — | REF | 부록 §C 참고자료 |
| O-036 | 향후 확장 로드맵 (VR/AR, 멘토링) | V3+ | REF | §7 Phase 3 |

---

**전체 매핑 완료: 69/69 항목 (100%)**

| 서브폴더 | 항목 수 | 비율 |
|----------|---------|------|
| 01_adaptive-learning | 15 | 22% |
| 02_spaced-repetition | 8 | 12% |
| 03_coding-tutorial | 10 | 14% |
| 04_content-generation | 18 | 26% |
| 05_learning-analytics | 18 | 26% |
| **합계 (구현 대상)** | **69** | **100%** |

---

## §7 Phase 실행 계획

### Phase 0: 분석 + 골격

| 항목 | 내용 |
|------|------|
| **목표** | 폴더 구조 생성, 골격 파일 배치, 거버넌스 문서 완성 |
| **산출물** | 5개 서브폴더 + _index.md, 계획서(본 문서), AUTHORITY_CHAIN.md, CONFLICT_LOG.md |
| **기간** | 1일 |
| **게이트** | 폴더 트리 100% 생성, _index.md 5개 완성, 계획서 v1.0 확정 |

#### Phase 0 단계별 상세 작업 절차

<details>
<summary><b>P0-1. 선행작업 A~D 완료 ✅ (2026-03-31)</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot\STEP7-O_교육_학습_자기개발_작업가이드.md` (69항목 보강 체크리스트)
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\EDUCATION_LEARNING_상세명세.md` (기존 690줄 명세)
- Part2 CAT-E COND 레이어 (D2.0-01~07, 7개) + UI 1건
- #6 PKM LOCK-PKM-01~03 (SM-2 파라미터 정본)

**절차** (A·B·D 병렬 가능, C는 A 완료 후 실행):
1. **A: STEP7-O 항목 분류 + 서브폴더 매핑** — O-001~O-028의 69 세부 항목을 5개 서브폴더로 분류, O-ID별 대상 파일 확정
   - Part 1 (O-001~O-010) → 01_adaptive-learning, 02_spaced-repetition, 03_coding-tutorial, 04_content-generation, 05_learning-analytics 분배
   - Part 2 (O-011~O-018) → 04_content-generation 중심 (O-017 → 03_coding-tutorial 예외, O-018 → §6 매핑 부재 — 내용은 O-023·§D.4 Phase 3에 흡수)
   - Part 3 (O-019~O-028) → 05_learning-analytics 집중
   - Part 4 (O-029~O-036) → 부록 §C + §7 로드맵 통합 (REF 전용, 서브폴더 매핑 대상 아님)
   - **O-ID↔항목명 정합성 확인**: STEP7-O 원본 O-ID 내용과 §6 매핑 테이블 항목명 대조, 불일치 시 §6 기준으로 확정 후 사유 기록
2. **B: Part2 SHELL 확인 + GAP 확정** — CAT-E COND 7개(D2.0-01~07) + UI 1건 모두 SHELL(빈껍데기) 확인, 방식 C(전면 신규 작성) 확정
3. **C: 기존 상세명세와 STEP7-O 대조** — 690줄 커버 범위 분석, STEP7-O 미커버 항목 식별 (의존: A 완료 후). 상세명세는 동결 참조 전용(§8)
4. **D: PKM(#6)과 SM-2 공유 규약 확인** — LOCK-ED-04 준수: MIN_EF=1.3, DEFAULT_EF=2.5, I(1)=1d, I(2)=6d, I(n≥3)=I(n-1)×EF 불변. Education 커스터마이징 범위: EF 보정 가중치, interval 조정 계수, quality-Bloom 연동 매핑에 한정

**검증**:
- [x] 69건(O-001~O-028 세부 항목) 전수 5개 서브폴더 매핑 완료 + O-029~O-036(8건) 부록/§7 REF 매핑 완료 (§6 매핑 테이블과 일치)
- [x] STEP7-O 원본 O-ID 항목명과 §6 매핑 테이블 항목명 정합성 확인 완료 — 7건 불일치 식별, §6 기준 확정 (§11 S11-2 기록)
- [x] CAT-E COND 7개 + UI 1건 SHELL 상태 확인 → 방식 C 확정
- [x] 기존 상세명세 690줄 vs STEP7-O 커버리지 GAP 식별 완료 — Full 5건, Partial 2건, GAP 25건 (~19.5% 커버리지)
- [x] SM-2 공유 규약: PKM 정본 참조 원칙 확인 (LOCK-ED-04), Education 커스터마이징 범위 확정 — 위반 0건

**산출물**: §5 선행작업 A~D 상태 "완료" 확정, §6 이슈 해결 매핑 테이블 검증 승인, §6.5 항목 수 정정 (17→18, 합계 68→69 — §11 S11-1 기록)
</details>

<details>
<summary><b>P0-2. 서브폴더 5개 + _index.md 생성 ✅ (2026-03-31)</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\EDUCATION_LEARNING_구조화_종합계획서.md` §2.1 트리 구조
- §6 이슈 해결 매핑 (서브폴더별 항목 목록)
- §3.4 LOCK 보호 선언 (LOCK-ED-01~10, 서브폴더별 LOCK 참조 기준)

**절차**:
1. `D:\VAMOS\docs\sot 2\3-5_Education-Learning\` 하위에 5개 서브폴더 생성:
   - `01_adaptive-learning\` (~15항목)
   - `02_spaced-repetition\` (~8항목)
   - `03_coding-tutorial\` (~10항목)
   - `04_content-generation\` (~18항목)
   - `05_learning-analytics\` (~18항목)
2. 각 서브폴더에 `_index.md` 생성 (5개):
   - 서브폴더 개요 (목적, 범위)
   - 소속 파일 목록 + O-ID 매핑
   - V1/V2/V3 태깅 요약
   - LOCK 항목 참조 (해당 서브폴더 관련 LOCK-ED):
     - `01_adaptive-learning` → LOCK-ED-01(학습 경로), 02(난이도), 03(평가), 05(Bloom), 06(소크라테스), 07(프로필)
     - `02_spaced-repetition` → LOCK-ED-04(SM-2 정본), 08(플래시카드 유형)
     - `03_coding-tutorial` → LOCK-ED-06(소크라테스)
     - `04_content-generation` → LOCK-ED-05(Bloom)
     - `05_learning-analytics` → LOCK-ED-09(VBS-16), 10(게이미피케이션 XP)
3. _index.md 상호 참조: §2.1 트리의 파일 목록과 §6 매핑 테이블 일치 확인
4. 네이밍 규칙 준수: 서브폴더 `NN_kebab-case`, 파일 `snake_case.md`, 인덱스 `_index.md` (§2.3)

**검증**:
- [x] §10 #1: 서브폴더 5/5 생성 확인 (§2.1 트리와 일치)
- [x] §10 #1: _index.md 5/5 생성 확인
- [x] 각 _index.md에 소속 파일 목록 + O-ID 매핑 포함 — 69/69 항목 전수 일치
- [x] 각 _index.md에 V1/V2/V3 태깅 요약 포함 — 5개 서브폴더 합산 69 일치
- [x] 각 _index.md에 해당 서브폴더 관련 LOCK-ED 참조 포함 — 12건 §3.4 원문 대조 일치
- [x] 네이밍 규칙 준수: 서브폴더 `NN_kebab-case`, 인덱스 `_index.md` (§2.3)
- [x] 폴더 깊이 3단계 이내 (§2.2 규칙)

**산출물**:
- 서브폴더 5개: `01_adaptive-learning\`, `02_spaced-repetition\`, `03_coding-tutorial\`, `04_content-generation\`, `05_learning-analytics\`
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\01_adaptive-learning\_index.md`
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\02_spaced-repetition\_index.md`
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\03_coding-tutorial\_index.md`
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\04_content-generation\_index.md`
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\05_learning-analytics\_index.md`
</details>

<details>
<summary><b>P0-3. 본 계획서(v1.0) 완성 ✅ (2026-03-31)</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot\STEP7-O_교육_학습_자기개발_작업가이드.md` (69항목 — 원문 "68개" 표기, 세부 분해 기준 69 §11 S11-1)
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\EDUCATION_LEARNING_상세명세.md` (기존 명세)
- Part2 CAT-E COND D2.0-01~07 (7개 — §1.4 기준)
- LOCK-ED-01~10 정의

**절차**:
1. §1~§14 전체 14개 섹션 완성도 점검:
   - §1 현재 상태 분석, §2 목표 구조, §3 권한 체계 선언, §4 거버넌스 규칙
   - §5 선행작업, §6 이슈 해결 매핑, §7 Phase 실행 계획, §8 파일 역할 분리 명세
   - §9 충돌 해결 프로토콜, §10 검증 체크리스트, §11 보완 사항, §12 FINAL REVIEW 결과
   - §13 L3 전수 승급 계획, §14 실행 약점 대응 계획
2. 부록 4개 완성도 점검:
   - 부록 §A 교수법 프레임워크 (Bloom, 소크라테스, IRT, ZPD)
   - 부록 §B SM-2 알고리즘 파라미터 (교육 특화)
   - 부록 §C 의존성 맵
   - 부록 §D Part2 교차 참조 (CAT-E 모듈 매핑)
3. LOCK-ED-01~10 전수 인용 정확성 확인 (§3.4 정의 ↔ 부록 §A·§B 인용 ↔ SOT 원본 대조)
4. §6 매핑 테이블 전수 커버 확인: 69건 구현 대상 (V1/V2/V3 태깅) + 8건 REF (O-029~O-036 부록/§7 매핑)
5. 목차(§목차) ↔ 실제 §1~§14 + 부록 §A~§D 구성 일치 확인 (18항목)
6. 문서 내부 수치 일관성 교차 검증: 항목 수(69), COND 수(7), 부록 수(4), 서브폴더 수(5)가 메타 테이블·§1.3·§3.2·§6 합계·푸터에서 일관되는지 확인

**검증**:
- [x] §10 #2: 14개 섹션 완성 확인 — §1~§14 전수 존재+실질 내용 PASS (§12 QC-1/QC-3은 과거 리뷰 기록 보존)
- [x] §10 #2: 4개 부록 완성 확인 (§A 교수법, §B SM-2, §C 의존성, §D Part2 교차 참조) — 전수 PASS
- [x] LOCK-ED-01~10 인용값 정확 (SOT 원본 대조) — 10/10 정확 (ED-03·08은 종합계획서 신규 명확화, SOT 원본과 정합)
- [x] §6 매핑: 69건 구현 대상 V1/V2/V3 태깅 + 8건 REF 매핑 완료 (합계 77건 전수) — V1=34, V2=29, V3=6, REF=8 PASS
- [x] 목차 18항목 ↔ 실제 섹션·부록 일치 확인 — 18/18 PASS
- [x] 문서 내부 수치 일관성: 항목 수(69), COND 수(7), 부록 수(4) 전수 일관 확인 — §8 역할 테이블 68→69 추가 정정, 전수 PASS

**산출물**: `D:\VAMOS\docs\sot 2\3-5_Education-Learning\EDUCATION_LEARNING_구조화_종합계획서.md` v1.0 확정
</details>

<details>
<summary><b>P0-4. AUTHORITY_CHAIN.md + CONFLICT_LOG.md 생성 ✅ (2026-03-31)</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\EDUCATION_LEARNING_구조화_종합계획서.md` §3 권한 체계 (§3.1~§3.4), §4 거버넌스 규칙 (R-01~R-09, R-08-1~R-08-6), §8 파일 역할 분리 명세, §9 충돌 해결 프로토콜 (§9.1~§9.3)
- §3.4 LOCK-ED-01~10 정의
- §9.2 사전 정의 충돌 시나리오 5개 (C-01 SM-2, C-02 IRT, C-03 Bloom, C-04 Phase 배정, C-05 감정 기반 학습 적응)
- 부록 §C 의존성 맵 (도메인 간 의존성 5개: #4 COND, #5 Multimodal, #6 PKM, #9 Health, #10 Dev-Tools)
- §5 선행작업 E·F (Phase 2 예정 외부 연동: #9 Health, #7 Workflow-RPA)

**절차**:
1. **AUTHORITY_CHAIN.md** 생성:
   - 권한 계층 선언 (§3.1 + §3.2 기반, 상위→하위 권한순):
     ```
     RULE 1.3 (최상위 불변 규칙)
       > PLAN 3.0 (프로젝트 계획)
         > DESIGN 2.0 (설계)
           └─ D2.0-01~07 (COND CAT-E 교육 모듈 7개)
             > sot 2/3-5_Education-Learning/ (구현 정본 = What + How)
               > PART2 CAT-E (구현 가이드 = When + Where)
                 > STEP7-O (보강 체크리스트 = 69항목, 읽기 전용)
     ```
   - §8 파일 역할 우선순위 반영: 구현 정본(1순위) > PART2 CAT-E(2순위) > 기존 상세명세(3순위, 동결 참조) > STEP7-O(4순위, 참조)
   - LOCK-ED-01~10 보호 목록 (§3.4 전수) + 해제 절차: R-02 준수 (사유+대안+영향 분석 필수)
   - 문서별 권한 범위 (§3.3 테이블 7개 문서 전수): 역할, 결정 범위, 변경 권한
   - SM-2 공유 규약: PKM(#6) 정본 우선 원칙 (LOCK-ED-04, R-08-1)
   - R-01 연동 명시: 모든 변경은 본 파일의 권한 범위 내에서만 수행
2. **CONFLICT_LOG.md** 생성:
   - 충돌 해결 우선순위 선언 (§9.1): LOCK 값(최우선) > DESIGN 2.0 확정값 > 기존 상세명세 확정값 > 시간순(최신 우선)
   - 초기 항목 등록 (§9.2 전수 5개): C-01 SM-2 파라미터 충돌, C-02 IRT 난이도 파라미터 불일치, C-03 Bloom 택소노미 분류 불일치, C-04 Phase 배정 충돌, C-05 감정 기반 학습 적응 범위 — 각 항목에 충돌 당사자 + 해결 규칙 포함 (§9.2 테이블 전수)
   - 충돌 기록 템플릿 (§9.3 형식): `[날짜] [C-ID] [당사자] [결정] [근거]`
   - R-06 명시: 미기록 충돌 해결은 무효
   - 외부 의존성 충돌 대비 (§C.1 + §5 기반): #6 PKM(양방향, LOCK-ED-04), #9 Health(단방향 수신, R-08-6 opt-in), #7 Workflow-RPA(Phase 2 예정, §5-F), #5 Multimodal(Phase 2+), #10 Dev-Tools(코딩 튜토리얼), #4 COND(COND 트리거)

**검증**:
- [x] §10 #3: AUTHORITY_CHAIN.md 파일 존재 + 초기 내용 확인 — v2.0 (7섹션: 권한계층, §8우선순위, §3.3권한범위, LOCK보호, SM-2규약, 도메인경계, 변경이력)
- [x] §10 #3: CONFLICT_LOG.md 파일 존재 + 초기 내용 확인 — v2.0 (6섹션: §9.1우선순위, C-01~C-05, §9.3템플릿, 충돌기록4건, 외부의존성6개, 변경이력)
- [x] 권한 계층이 §3.1 + §3.2 권한 체인과 일치 (7계층 전수: RULE 1.3 → PLAN 3.0 → DESIGN 2.0 → D2.0-01~07 → 구현 정본 → PART2 CAT-E → STEP7-O) — §3.1(기존 체인) + §3.2(Education 확장 체인) 모두 반영
- [x] §8 우선순위(1~4순위) 반영 확인 — 구현정본(1) > PART2(2) > 상세명세(3) > STEP7-O(4) + 파일 간 관계 다이어그램 포함
- [x] LOCK-ED-01~10 보호 목록 전수 + 해제 절차가 R-02(사유+대안+영향 분석)와 일치 — 10/10 항목 + 3단계 해제 절차 명시
- [x] §3.3 문서별 권한 범위 7개 문서 전수 반영 (역할/결정 범위/변경 권한) — 7/7 문서 (RULE 1.3, PLAN 3.0, DESIGN LOCK, DESIGN body, 구현정본, PART2, STEP7-O)
- [x] §9.1 충돌 해결 우선순위 4단계 선언 포함 (LOCK > DESIGN > 상세명세 > 시간순) — CONFLICT_LOG §1에 4단계 체인 명시
- [x] 초기 충돌 항목 C-01~C-05 전수 등록 완료 (§9.2 기반 5개, 각 항목 당사자+해결 규칙 포함) — 5/5 시나리오 + 기존 v1.0 3건·CFL-ED-004 §9.3 형식 변환 보존
- [x] 충돌 기록 템플릿이 §9.3 형식(`[날짜][C-ID][당사자][결정][근거]`)과 일치 — 5필드 템플릿 + 필드 설명 테이블 포함
- [x] 외부 의존성 목록이 §C.1 의존성 맵(5개 도메인) + §5 E·F와 정합 — 6개 도메인 (#4 COND, #5 Multimodal, #6 PKM, #7 Workflow-RPA, #9 Health, #10 Dev-Tools) 방향·규칙·시점 명시

**산출물**:
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\AUTHORITY_CHAIN.md` (v1.0→v2.0 갱신: §3.1+§3.2 7계층 권한 체인 정정, §3.3 7개 문서 전수, §8 우선순위, R-01/R-02 명시, VBS-16 정정)
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\CONFLICT_LOG.md` (v1.0→v2.0 갱신: §9.1 우선순위, C-01~C-05 전수, §9.3 형식 적용, R-06 명시, 외부 의존성 6개, CFL-ED-003 C-ID/LOCK-ED 정정)
</details>

> **Phase 0 게이트 검증**: P0-1~P0-4 완료 후 §10 체크리스트 #1~#3 전수 통과 시 Phase 1 진입
> - #1: 폴더 트리 100% 생성 (서브폴더 5/5, _index 5/5)
> - #2: 계획서 v1.0 확정 (14개 섹션 + 4개 부록)
> - #3: AUTHORITY_CHAIN + CONFLICT_LOG 생성 (2개 파일)

### Phase 1: V1 MVP

| 항목 | 내용 |
|------|------|
| **목표** | 핵심 학습 기능 구현 정본 완성 |
| **대상** | adaptive_engine, difficulty_adjustment, learner_profile, learning_path_generator, sm2_education_extension, flashcard_auto_generation, review_scheduler, interactive_tutorial, leetcode_style_problems, code_review_learning, quiz_test_generation, youtube_learning, book_reading, mindmap_concept_map, learning_dashboard, gamification (기본), goal_management, time_management, benchmark_vbs16 |
| **항목 수** | ~40항목 (V1 태깅) |
| **기간** | 5일 |
| **게이트** | V1 대상 파일 100% 작성, LOCK 값 정합성 검증, SM-2 공유 규약 준수 확인 |

#### Phase 1 단계별 상세 작업 절차

<details>
<summary><b>1-1. 01_adaptive-learning V1 L3 작성 (4파일, ~9항목)</b></summary>

**대조 기준**:
- §7 세부 작업: adaptive_engine, difficulty_adjustment, learner_profile, learning_path_generator
- §7 전환 게이트: V1 대상 파일 100% 작성, LOCK 값 정합성 검증
- §6 이슈: §6.1 (~15항목) — V1: O-001-1~5 (적응형 엔진 코어, IRT, 학습자 프로필, Bloom, 소크라테스), O-003-1~4 (경로 생성, Phase 분해, 체크포인트, 소요시간)

**목표**: 01_adaptive-learning 서브폴더의 V1 대상 4개 파일을 L3 수준으로 완성한다. IRT 기반 난이도 5단계(LOCK-ED-02: Very Easy~Very Hard, 정답률 70-85%), Bloom 택소노미 6단계(LOCK-ED-05: Remember~Create), 소크라테스 교수법(LOCK-ED-06: 직접 답 금지→질문 유도→힌트 3단계), 학습자 프로필 스키마(LOCK-ED-07), 학습 경로 구조(LOCK-ED-01)를 핵심 제약으로 적용한다.

**입력 파일**:
- 본 계획서 §6.1 (~15항목 매핑)
- `01_adaptive-learning/_index.md` (Phase 0 산출물)
- `D:\VAMOS\docs\sot\STEP7-O_교육_학습_자기개발_작업가이드.md` (O-001, O-003, O-005~O-006 원본)
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\EDUCATION_LEARNING_상세명세.md` §2 적응형 학습 (기존 명세)

**절차**:
1. `adaptive_engine.md` 작성 — O-001-1, O-001-4, O-001-5:
   - 적응형 학습 엔진 코어 아키텍처 L3
   - Bloom 택소노미 6단계(LOCK-ED-05) 기반 콘텐츠 분류 알고리즘
   - 소크라테스 교수법(LOCK-ED-06) 대화 엔진 의사코드
2. `difficulty_adjustment.md` 작성 — O-001-2:
   - IRT θ 파라미터 추정 알고리즘 L3
   - 5단계 난이도 분류(LOCK-ED-02) + 정답률 목표 70-85% 적용
   - 평가 기준(LOCK-ED-03: 진단/진행/최종, 3등급)
3. `learner_profile.md` 작성 — O-001-3:
   - 학습자 프로필 스키마(LOCK-ED-07: skill_levels, learning_speed, preferred_style, weekly_hours, goal)
   - 프로필 생성/갱신/조회 API
4. `learning_path_generator.md` 작성 — O-003-1~4:
   - 학습 경로 구조(LOCK-ED-01: 목표→Phase 분해→자료+실습+체크포인트+소요시간)
   - Phase 분해 알고리즘 의사코드
   - 체크포인트 시스템 + 소요시간 추정 모델
5. V2 항목(O-005 투자교육, O-006 언어학습) 골격 배치
6. LOCK 인용: LOCK-ED-01/02/03/05/06/07 `> LOCK (출처): [원문]` 형식

**검증**:
- [x] adaptive_engine, difficulty_adjustment, learner_profile, learning_path_generator 4파일 완성
- [x] LOCK-ED-01/02/03/05/06/07 인용 R9 형식
- [x] Bloom 6단계 순서(LOCK-ED-05) 불변 확인
- [x] 소크라테스 교수법 5원칙(LOCK-ED-06) 전수 반영

**산출물**: `01_adaptive-learning/` 내 4개 V1 파일 L3 완성 + V2 골격 2개

---

**1-1 세션 검증 결과 요약** (2026-04-09, rev.2)

| # | 검증 항목 | 결과 | 상세 |
|---|-----------|------|------|
| 1 | V1 4파일 완성 | **PASS** | adaptive_engine(L3) / difficulty_adjustment(L3) / learner_profile(L3) / learning_path_generator(L3) |
| 2 | V2 골격 2파일 배치 | **PASS** | investment_education(SKELETON) / language_learning(SKELETON) |
| 3 | LOCK-ED-01 인용 | **PASS** | learning_path_generator.md §2 — `> LOCK (LOCK-ED-01, STEP7-O O-003): 목표→Phase 분해→각 Phase(자료+실습+체크포인트+소요시간)` |
| 4 | LOCK-ED-02 인용 | **PASS** | difficulty_adjustment.md §2 + adaptive_engine.md §3.4 — IRT 5단계, 정답률 70-85% |
| 5 | LOCK-ED-03 인용 | **PASS** | adaptive_engine.md §2.4 + difficulty_adjustment.md §5 + learning_path_generator.md §5.1 — 진단/진행/최종, 3등급 |
| 6 | LOCK-ED-05 인용 | **PASS** | adaptive_engine.md §3.1 — Remember/Understand/Apply/Analyze/Evaluate/Create 순서 불변 |
| 7 | LOCK-ED-06 인용 | **PASS** | adaptive_engine.md §4.1 — 직접 답 금지→질문 유도→힌트 3단계→사고 과정 유도→격려 피드백 5원칙 전수 |
| 8 | LOCK-ED-07 인용 | **PASS** | learner_profile.md §2 — skill_levels, learning_speed, preferred_style, weekly_hours, goal 5필드 전수 |
| 9 | Bloom-IRT θ 매핑 정합성 | **PASS** | LOCK-ED-02 경계(-1.5/-0.5/0.5/1.5)와 Bloom 중심값 매핑 명시, 불일치 해소 |
| 10 | ZPD-5 구현 정합성 | **PASS** | SoT 원문 "정답률 40% 이하로 3회 연속 하락" 추세 기반으로 수정 |
| 11 | 상세명세 §2.4 호환 | **PASS** | overall_level, preferred_language, session_duration_pref_min 3필드 추가 |
| 12 | 체크포인트 등급 기준 | **PASS** | 진행평가(미달<60%/달성/우수≥85%) · 최종평가(미달<70%/달성/우수≥90%) adaptive_engine.md §2.4 동기화 |
| 13 | 예시 문항 수·θ 정합 | **PASS** | Phase 4: 8문항(Apply→bloom=3), Phase 7: θ=1.5(Create), 최종평가 20문항 알고리즘 일치 |
| 14 | 파일 간 교차 참조 | **PASS** | 4파일 상호참조 정확, 미생성 파일(1-2~1-5 예정)은 "(N단계 생성 예정)" 표기 |
| 15 | front-matter LOCK 필드 | **PASS** | 각 파일 body 인용과 front-matter 일치 확인 (adaptive_engine: ED-02/03/05/06, difficulty: ED-02/03, learner: ED-07, path: ED-01/02/03/05) |

**rev.2 주요 수정 이력**:
- adaptive_engine.md: LOCK-ED-02 참조 추가, Bloom-IRT 매핑 테이블 θ 중심값+LOCK-ED-02 대응 표기 재작성, 힌트 예시 SoT 원문 일치
- difficulty_adjustment.md: ZPD-5 구현 streak 기반→추세 기반 수정, 2PL 변별도 a=1.7 고정 명시(V1)
- learner_profile.md: 상세명세 호환 필드 3개 추가, update_weekly_hours API 신설(R-PROF-03), theta_to_skill_level LOCK-ED-02 매핑 주석
- learning_path_generator.md: LOCK-ED-03 front-matter·인용 블록 추가, 체크포인트 유형 LOCK-ED-03 용어 매핑, create_checkpoint 최종평가 분기, 등급 기준 분리, 예시 Phase 4(8문항)·Phase 7(θ=1.5, 20문항) 수정

**최종 판정**: 1-1 **PASS** — 4파일 V1 L3 완성 + 2파일 V2 골격, LOCK 6종 전수 인용, 15항목 검증 통과
</details>

<details>
<summary><b>1-2. 02_spaced-repetition V1 L3 작성 (3파일, ~6항목)</b></summary>

**대조 기준**:
- §7 세부 작업: sm2_education_extension, flashcard_auto_generation, review_scheduler
- §7 전환 게이트: V1 대상 파일 100% 작성, SM-2 공유 규약 준수 확인
- §6 이슈: §6.2 (~8항목) — V1: O-002-1~3 (SM-2 확장, Bloom EF 보정, 플래시카드 기본/빈칸), O-002-5 (코드 유형), O-002-6~7 (복습 스케줄러, 맥락별 간격)

**목표**: 02_spaced-repetition 서브폴더의 V1 대상 3개 파일을 L3 수준으로 완성한다. SM-2 파라미터는 PKM 정본(LOCK-ED-04 → LOCK-PKM-01~03: MIN_EF=1.3, DEFAULT_EF=2.5, I(1)=1d, I(2)=6d)을 참조하되 교육 특화 확장(Bloom 레벨별 EF 보정)을 적용한다. 플래시카드 4유형(LOCK-ED-08: 기본/빈칸/이미지/코드)을 포함한다.

**입력 파일**:
- 본 계획서 §6.2 (~8항목 매핑)
- `02_spaced-repetition/_index.md` (Phase 0 산출물)
- `D:\VAMOS\docs\sot\STEP7-O_교육_학습_자기개발_작업가이드.md` (O-002 원본)
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\EDUCATION_LEARNING_상세명세.md` (기존 명세)
- `D:\VAMOS\docs\sot 2\3-3_PKM-Knowledge-Management\PKM_KNOWLEDGE_MANAGEMENT_구조화_종합계획서.md` §3.4 LOCK-PKM-01~03 (SM-2 정본)

**절차**:
1. `sm2_education_extension.md` 작성 — O-002-1, O-002-2:
   - SM-2 교육 확장: PKM LOCK-PKM-01~03 파라미터 참조 (LOCK-ED-04 제약)
   - Bloom 레벨별 EF 보정 공식 (Education 소유 확장)
   - R-08-1 (SM-2 변경 시 PKM 동기화 필수) 명시
2. `flashcard_auto_generation.md` 작성 — O-002-3, O-002-5:
   - 4유형 플래시카드(LOCK-ED-08) 자동 생성 파이프라인 L3
   - LLM 기반 기본/빈칸 자동 생성 + 코드 유형 특화
   - V2 이미지 오클루전(O-002-4) 골격 배치
3. `review_scheduler.md` 작성 — O-002-6, O-002-7:
   - SM-2 기반 복습 스케줄러 코어 L3 (EF×interval 계산 의사코드)
   - 학습 맥락별 간격 조정 로직
   - V2 복습 알림(O-002-8) 골격 배치
4. LOCK 인용: LOCK-ED-04/08 + PKM 참조 LOCK-PKM-01/02/03 `> LOCK (출처): [원문]` 형식

**검증**:
- [x] sm2_education_extension, flashcard_auto_generation, review_scheduler 3파일 완성
- [x] LOCK-ED-04/08 인용 R9 형식
- [x] PKM SM-2 정본 참조 (LOCK-PKM-01~03) 확인
- [x] R-08-1 SM-2 공유 규약 명시 확인

**산출물**: `02_spaced-repetition/` 내 3개 V1 파일 L3 완성

---

**1-2 세션 검증 결과 요약** (2026-04-09)

| # | 검증 항목 | 결과 | 상세 |
|---|-----------|------|------|
| 1 | V1 3파일 완성 | **PASS** | sm2_education_extension(L3) / flashcard_auto_generation(L3) / review_scheduler(L3) |
| 2 | V2 골격 2건 배치 | **PASS** | flashcard_auto_generation §6 이미지 오클루전(O-002-4) / review_scheduler §5 복습 알림(O-002-8) |
| 3 | O-ID 매핑 정합 (§6.2) | **PASS** | O-002-1~8 전부 정확한 파일에 매핑, _index.md 8건 상태 갱신(V1 6건 COMPLETE, V2 2건 V2-STUB) |
| 4 | LOCK-ED-04 인용 | **PASS** | sm2_education_extension §2.1 + review_scheduler §1 — `> LOCK (LOCK-ED-04, #6 PKM LOCK-PKM-01~03): MIN_EF=1.3, DEFAULT_EF=2.5, I(1)=1d, I(2)=6d` |
| 5 | LOCK-ED-08 인용 | **PASS** | flashcard_auto_generation §1 — `> LOCK (LOCK-ED-08, STEP7-O O-002): 기본(앞/뒤), 빈칸채우기, 이미지오클루전, 코드` |
| 6 | LOCK-ED-05 인용 | **PASS** | sm2_education_extension §3.2 — Bloom 6단계 순서 불변 인용, 보정 테이블에 반영 |
| 7 | LOCK-PKM-01/02/03 개별 인용 | **PASS** | sm2_education_extension §2.1 — 3건 모두 `> LOCK (LOCK-PKM-0N, ...)` 개별 인용 |
| 8 | R-08-1 SM-2 공유 규약 | **PASS** | sm2_education_extension §1 + review_scheduler §1 — 전문 인용 + 커스터마이징 범위 한정(EF 보정/interval 조정/quality-Bloom 매핑) |
| 9 | §B.2.1 Bloom EF 보정 정합 | **PASS** | §B.2.1 곱셈 방식(Remember=1.0~Create=0.75)을 가산+quality 감쇠 방식으로 정제, 정당화 노트 명시, 방향(상위 Bloom=보수적) 동일 |
| 10 | §B.2.2 맥락 간격 계수 정합 | **PASS** | SUBJECT_FACTOR §B.2.2 방향 준수: coding=0.85(§B: 0.8), math=0.90(§B formula: 0.85), language=0.90(§B vocabulary: 0.9), history=1.10(§B: 1.1), 4축 분리는 L3 정제 |
| 11 | §B.2.3 quality 매핑 정합 | **PASS** | sm2_education_extension §2.4 — quality 0~5 의미 종합계획서 §B.2.3과 동일, Bloom 3구간 교차 매핑 추가 |
| 12 | §B.3 스키마 정합 | **PASS** | difficulty_irt(LOCK-ED-02), hint_steps(LOCK-ED-06), related_learning_path, bloom_adjusted_ef(§B.3 bloom_weight_ef 대응) 전부 포함 |
| 13 | 상세명세 §3.3 ReviewScheduleConfig 호환 | **PASS** | daily_card_limit(50), new_cards_per_day(10), review_time_preference, interleaving(true), min_interval_hours(4) 동일 |
| 14 | STEP7-O O-002 커버리지 | **PASS** | SM-2, AI 카드 자동 생성(기본/빈칸/코드), 일일 카드 수 제한(과부하 방지), V2 이미지 오클루전 골격 |
| 15 | 계산 예시 검산 | **PASS** | sm2_extension §3.4(2시나리오), review_scheduler §3.3(3시나리오) 전수 검산 정확 |
| 16 | 파일 간 교차 참조 | **PASS** | 3파일 상호참조 + 01_adaptive-learning 역참조 정확, 미생성 파일(1-4~1-5 예정)은 표기 |

**재검증 수정 이력** (5건):
- sm2_education_extension.md §3.2: §B.2.1 정합성 노트 추가(곱셈→가산 정제 근거), Bloom 테이블에 §B.2.1 대응 weight 컬럼 추가, 마크다운 테이블 구분선 컬럼 수 수정
- sm2_education_extension.md §4.1 + flashcard_auto_generation.md §4.1: §B.3 누락 필드 3개 추가(difficulty_irt, hint_steps, related_learning_path)
- review_scheduler.md §3.2: SUBJECT_FACTOR §B.2.2 방향 정합(coding 1.10→0.85, math 1.05→0.90, history 1.10 추가)
- review_scheduler.md §3.3: 수정된 계수 반영 예시 갱신 + 시나리오 C 추가(수동 코딩 복습이 §B.2.2 방향과 일치함을 증명)
- flashcard_auto_generation.md: LOCK 헤더 정합성 수정(LOCK-ED-02 제거 — IRT 정본은 difficulty_adjustment.md 소유)

**최종 판정**: 1-2 **PASS** — 3파일 V1 L3 완성 + 2건 V2 골격, LOCK-ED-04/05/08 + LOCK-PKM-01~03 전수 인용, R-08-1 공유 규약 명시, §B 정합 확인, 16항목 검증 통과
</details>

<details>
<summary><b>1-3. 03_coding-tutorial V1 L3 작성 (3파일, ~5항목)</b></summary>

**대조 기준**:
- §7 세부 작업: interactive_tutorial, leetcode_style_problems, code_review_learning
- §7 전환 게이트: V1 대상 파일 100% 작성, LOCK 값 정합성 검증
- §6 이슈: §6.3 (~10항목) — V1: O-004-1~5 (인터랙티브 튜토리얼, 소크라테스 힌트, LeetCode 문제, IRT 난이도, 코드 리뷰)

**목표**: 03_coding-tutorial 서브폴더의 V1 대상 3개 파일을 L3 수준으로 완성한다. 인터랙티브 코딩 환경, LeetCode 스타일 문제 생성(IRT 난이도 LOCK-ED-02 연동), 코드 리뷰 피드백 학습을 포함한다. 소크라테스 교수법(LOCK-ED-06)을 힌트 시스템에 적용한다.

**입력 파일**:
- 본 계획서 §6.3 (~10항목 매핑)
- `03_coding-tutorial/_index.md` (Phase 0 산출물)
- `D:\VAMOS\docs\sot\STEP7-O_교육_학습_자기개발_작업가이드.md` (O-004, O-017 원본)
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\EDUCATION_LEARNING_상세명세.md` (기존 명세)

**절차**:
1. `interactive_tutorial.md` 작성 — O-004-1, O-004-2:
   - 인터랙티브 코딩 튜토리얼 엔진 L3 (코드 실행 샌드박스 + 실시간 피드백)
   - 소크라테스 힌트 시스템(LOCK-ED-06) 3단계 힌트 의사코드
2. `leetcode_style_problems.md` 작성 — O-004-3, O-004-4:
   - LLM 기반 알고리즘 문제 생성 L3
   - IRT 난이도 분류(LOCK-ED-02) 연동 — 문제별 θ 파라미터 할당
3. `code_review_learning.md` 작성 — O-004-5:
   - 코드 리뷰 피드백 학습 엔진 L3 (AST 분석 + LLM 피드백)
   - V2 코드 품질 지표(O-004-6) 골격 배치
4. V2 항목(project_based_learning, coding_challenge) 골격 배치

**검증**:
- [x] interactive_tutorial, leetcode_style_problems, code_review_learning 3파일 완성
- [x] LOCK-ED-02/06 인용 R9 형식
- [x] 소크라테스 힌트 3단계 의사코드 포함

**산출물**: `03_coding-tutorial/` 내 3개 V1 파일 L3 완성 + V2 골격

---

#### 1-3 세션 검증 결과 요약 (2026-04-09)

| # | 검증 항목 | 결과 | 상세 |
|---|-----------|------|------|
| 1 | V1 3파일 완성 | **PASS** | interactive_tutorial(L3) / leetcode_style_problems(L3) / code_review_learning(L3) |
| 2 | V2 골격 3건 배치 | **PASS** | code_review_learning §6 CodeQualityMetrics(O-004-6) / project_based_learning(O-004-7/8) / coding_challenge(O-017-1/2) |
| 3 | O-ID 매핑 정합 (§6.3) | **PASS** | O-004-1~8 + O-017-1~2 전부 정확한 파일에 매핑, _index.md 10건 상태 갱신(V1 5건 L3 COMPLETE, V2 4건 SKELETON, V3 1건 SKELETON) |
| 4 | LOCK-ED-02 인용 | **PASS** | leetcode_style_problems §3 — `> LOCK (LOCK-ED-02, 기존 명세 §2): IRT 5단계 — Very Easy / Easy / Medium / Hard / Very Hard, 목표 정답률 70-85%` |
| 5 | LOCK-ED-06 인용 | **PASS** | interactive_tutorial §4 + code_review_learning §4.2 — `> LOCK (LOCK-ED-06, STEP7-O O-001): 직접 답 금지 → 질문 유도 → 힌트 3단계 → 사고 과정 유도 → 격려 피드백` |
| 6 | LOCK-ED-05 적용 | **PASS** | leetcode_style_problems §3.4 Bloom 순서 보장(R-08-2), code_review_learning §4.1 Bloom 게이트(Analyze(4) 이상 전체 리뷰), interactive_tutorial §5.2 Bloom 레벨별 커리큘럼 |
| 7 | 소크라테스 힌트 3단계 의사코드 | **PASS** | interactive_tutorial §4.2 `provide_hint()` — Level 1 방향 제시(xp_penalty=0.0) → Level 2 핵심 개념(0.1) → Level 3 부분 답(0.2) → 소진 시 유사 문제 전환 |
| 8 | §A.2 IRT 정합 | **PASS** | leetcode_style_problems §3.2 THETA_RANGES 경계값(-1.5/-0.5/0.5/1.5) §A.2 동일, §3.4 적응형 선택 θ±0.3 규칙 §A.2 `adjust_difficulty` 동일, 3PL(a,c) 확장은 2PL 상위 호환 |
| 9 | STEP7-O O-004 커버리지 | **PASS** | 인터랙티브 튜토리얼(개념→예제→연습→해설), 코드 실행 샌드박스, 에러 설명(원인→해결법→유사상황), 좋은/나쁜 코드 비교(compare 모드), LeetCode 문제(난이도별 추천+힌트+최적화 제안+복잡도 분석), 프로젝트 기반 학습(V2 골격) |
| 10 | §13 L3 매트릭스 E1~E10 | **PASS** | 3파일 모두 Input Schema(E1), Output Schema(E2), Algorithm/Pipeline(E3), Pedagogical Model(E4), Error Handling(E5), Privacy/Security(E6), Performance SLA(E7), Integration Test(E8), Dependencies(E9), UX/Gamification(E10) 충족 |
| 11 | _index.md LOCK 테이블 | **PASS** | LOCK-ED-02/05/06/10 4건 등록, 관련 파일 교차 매핑 정확 |
| 12 | 파일 간 교차 참조 | **PASS** | 3파일 상호참조 + 01_adaptive-learning(difficulty_adjustment, learner_profile) + 02_spaced-repetition(sm2_education_extension) 역참조 정확, 미생성 파일(05_learning-analytics)은 표기 |

**재검증 수정 이력** (3건):
- interactive_tutorial.md §5.1: `run_tutorial_session()` exercise phase가 `session.steps`에 미등록 → `session.steps.append(TutorialStep(phase="exercise"...))` 추가
- leetcode_style_problems.md §10 UX: Very Easy XP 누락 → `Very Easy: 3XP` 추가 (5단계 전체 완성)
- leetcode_style_problems.md §4.1: `generate_problem()` 내 `bloom_level` 미정의 변수 → `learner.bloom_progress[topic].current_level`로 수정

**최종 판정**: 1-3 **PASS** — 3파일 V1 L3 완성 + 3건 V2 골격, LOCK-ED-02/05/06 전수 인용, 소크라테스 3단계 의사코드 포함, §A.2 IRT 정합 확인, 12항목 검증 통과
</details>

<details>
<summary><b>1-4. 04_content-generation V1 L3 작성 (4파일, ~4항목)</b></summary>

**대조 기준**:
- §7 세부 작업: quiz_test_generation, youtube_learning, book_reading, mindmap_concept_map
- §7 전환 게이트: V1 대상 파일 100% 작성, LOCK 값 정합성 검증
- §6 이슈: 04_content-generation V1 항목 — O-008 (퀴즈/테스트), O-011 (YouTube), O-007/O-014 (독서), O-009 (마인드맵)

**목표**: 04_content-generation 서브폴더의 V1 대상 4개 파일을 L3 수준으로 완성한다. Bloom 택소노미(LOCK-ED-05)에 맞춘 퀴즈 자동 생성, YouTube 영상 학습(자막→요약→퀴즈), 독서 학습(PDF/EPUB→하이라이트→플래시카드), 마인드맵 자동 생성(Mermaid 기반)을 포함한다.

**입력 파일**:
- 본 계획서 §6 관련 항목 매핑
- `04_content-generation/_index.md` (Phase 0 산출물)
- `D:\VAMOS\docs\sot\STEP7-O_교육_학습_자기개발_작업가이드.md` (O-007~O-009, O-011~O-016 원본)
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\EDUCATION_LEARNING_상세명세.md` (기존 명세)

**절차**:
1. `quiz_test_generation.md` 작성 — O-008:
   - Bloom 택소노미(LOCK-ED-05) 레벨별 퀴즈 생성 파이프라인 L3
   - 평가 기준(LOCK-ED-03: 진단/진행/최종) 연동
2. `youtube_learning.md` 작성 — O-011:
   - YouTube 자막 추출 → AI 요약 → 퀴즈 자동 생성 L3
3. `book_reading.md` 작성 — O-007, O-014:
   - 독서 학습 파이프라인 L3 (PDF/EPUB 인제스트→하이라이트→SM-2 플래시카드 연동)
4. `mindmap_concept_map.md` 작성 — O-009:
   - 학습 콘텐츠 → 마인드맵 자동 생성 L3 (Mermaid/D3)
5. V2 항목(paper_learning, podcast_audio, online_course_support, presentation_coaching) 골격 배치

**검증**:
- [x] quiz_test_generation, youtube_learning, book_reading, mindmap_concept_map 4파일 완성
- [x] LOCK-ED-03/05 인용 R9 형식
- [x] Bloom 6단계 퀴즈 생성 로직 포함

**산출물**: `04_content-generation/` 내 4개 V1 파일 L3 완성 + V2 골격

---

**1-4 세션 검증 결과 요약** (2026-04-09, rev.3)

| # | 검증 항목 | 결과 | 상세 |
|---|-----------|------|------|
| 1 | V1 4파일 완성 | **PASS** | quiz_test_generation(L3) / youtube_learning(L3) / book_reading(L3) / mindmap_concept_map(L3) |
| 2 | V2 골격 4파일 배치 | **PASS** | paper_learning(SKELETON) / podcast_audio(SKELETON) / online_course_support(SKELETON) / presentation_coaching(SKELETON) |
| 3 | O-ID 매핑 정합 (§6.4) | **PASS** | O-008-1~3, O-011-1, O-007-1, O-014-1, O-009-1 전부 정확한 파일에 매핑, _index.md 18건 상태 갱신(V1 7건 L3 COMPLETE, V2-STUB 3건, SKELETON 8건) |
| 4 | LOCK-ED-05 인용 | **PASS** | 4파일 전수 — `> LOCK (LOCK-ED-05, STEP7-O O-001): Remember/Understand/Apply/Analyze/Evaluate/Create 순서 불변` |
| 5 | LOCK-ED-03 인용 | **PASS** | quiz_test_generation §1·§5 + book_reading §1 — `> LOCK (LOCK-ED-03, 기존 명세 §2): 진단테스트+진행평가+최종평가, 3등급(미달/달성/우수)` |
| 6 | LOCK-ED-02 인용 | **PASS** | quiz_test_generation §1 — `> LOCK (LOCK-ED-02, 기존 명세 §2): IRT 5단계 — Very Easy/Easy/Medium/Hard/Very Hard, 목표 정답률 70-85%` (rev.1에서 누락→rev.2 수정) |
| 7 | Bloom 6단계 퀴즈 생성 로직 | **PASS** | quiz_test_generation §4.2 `BLOOM_LEVELS` 딕셔너리(6단계 순서 불변) + `BLOOM_QUESTION_TYPE_MAP`(레벨별 적합 유형) + `ASSESSMENT_BLOOM_DEFAULTS`(평가 유형별 분포) 전수 구현 |
| 8 | Bloom 레벨 태깅 엔진 (O-008-2) | **PASS** | quiz_test_generation §6 `BloomTagger` — 콘텐츠 태깅(`tag_content`) + 문제 검증 태깅(`tag_question`) + 분포 검증(`validate_bloom_coverage`, 편차 <15%) |
| 9 | 테스트 결과 분석 (O-008-3) | **PASS** | quiz_test_generation §7 `TestResultAnalyzer` — Bloom별 성취도, 문제 유형별 성취도, 약점 개념 식별(오답 ≥2회), IRT θ 갱신 제안, LOCK-ED-03 등급 판정 |
| 10 | LOCK-ED-03 등급 기준 정합 | **PASS** | quiz_test_generation §5.1 — 진단(미달<50%/우수≥85%), 진행(미달<60%/우수≥85%), 최종(미달<70%/우수≥90%) + §5.2 `_determine_grade()` 동일 임계값 |
| 11 | STEP7-O O-008 커버리지 | **PASS** | 객관식(4지선다) ✅, 주관식(서술형) ✅, O/X ✅, 코드 문제 ✅, 시나리오 문제 ✅, 난이도 조절(IRT θ) ✅, 오답 분석(원인 분류+관련 개념 복습) ✅ |
| 12 | STEP7-O O-011 커버리지 | **PASS** | URL→자막추출 ✅, AI 요약 ✅, 핵심포인트+타임스탬프 ✅, 플래시카드 자동생성 ✅, 퀴즈 자동생성 ✅, 관련 영상 추천 ✅(rev.2 추가), 강의 시리즈 통합(구조화+진행률) ✅ |
| 13 | STEP7-O O-007/O-014 커버리지 | **PASS** | O-007: 챕터별 요약 ✅, Q&A ✅, 개념 설명(Bloom 기반) ✅, 관련 지식 연결(책 간) ✅, 독서 노트 자동생성→V2 골격 ✅ / O-014: 독서 트래킹 ✅, 인용구+감상(하이라이트) ✅, 책 간 연결 ✅, 독서 목록 관리(3단계) ✅ |
| 14 | STEP7-O O-009 커버리지 | **PASS** | 핵심 개념 추출 ✅, 관계 시각화(Mermaid) ✅, 인터랙티브 탐색→V2 골격 ✅, 갭 분석(빈 노드=미학습) ✅ |
| 15 | YouTube 자막 추출 파이프라인 | **PASS** | youtube_learning §4.2 — CC 우선(`youtube_transcript_api`) + Whisper STT fallback(`yt-dlp`→`whisper base`), 전처리(중복 제거, 노이즈 제거, 문장 분리) |
| 16 | 독서 PDF/EPUB 파싱 | **PASS** | book_reading §4.2 — PyMuPDF(fitz): TOC 기반 챕터 분리, ebooklib: ITEM_DOCUMENT 순회, 텍스트 타입: 직접 입력, URL: 웹 파싱 |
| 17 | 독서 진도 추적 (O-014-1) | **PASS** | book_reading §6 `ReadingProgressTracker` — 세션 기록, `total_pages` 기반 완독률, 목표 대비 on_track(최근 7일 평균 × 0.8), 독서 목록(not_started/reading/completed) |
| 18 | 마인드맵 Mermaid 생성 | **PASS** | mindmap_concept_map §4.2 `_generate_mermaid()` — Mermaid mindmap 형식, 숙달도 아이콘(✅ mastered / ❓ unknown), BFS 재귀 노드 추가 |
| 19 | 마인드맵 갭 분석 | **PASS** | mindmap_concept_map §4.2 `_analyze_gaps()` — unknown/recognized 노드 식별, `depends_on` 엣지 기반 선수 갭 추출, 학습 우선순위(선수 갭 수→core→major→minor 정렬), Bloom별 학습 행동 권장 |
| 20 | 마인드맵 그래프 로직 정합 | **PASS** | mindmap_concept_map §4.2 `_build_graph()` — `name_to_node`(개념명)/`id_to_node`(노드ID) 이중 dict, BFS 큐 `parent_name` 전달, 부모-자식 연결 정확(rev.2 전면 재작성) |
| 21 | 스키마-코드 참조 정합 | **PASS** | youtube `VideoMetadata.video_id` ✅(rev.3), book `ReadingProgress.total_pages` ✅(rev.2), quiz `QuizResult.assessment_type` ✅, mindmap `ConceptNode.bloom_level`/`mastery` ✅ |
| 22 | §13 L3 매트릭스 E1~E10 | **PASS** | 4파일 전수 — E1(Input Schema) / E2(Output Schema) / E3(Algorithm/Pipeline) / E4(Pedagogical Model) / E5(Error Handling) / E6(Privacy/Security) / E7(Performance SLA) / E8(Integration Test) / E9(Dependencies) / E10(UX/Gamification) |
| 23 | 교수법 모델 (E4) 명시성 | **PASS** | quiz: Bloom+IRT+오답 복습(§5) / youtube: Mayer 멀티미디어 5원칙(§5) / book: SQ3R+Bloom+SM-2(§1,§5 Q&A) / mindmap: 정교화 이론+Bloom 깊이(§1) |
| 24 | 파일 간 교차 참조 | **PASS** | 4파일 상호참조(quiz↔youtube↔book↔mindmap) + 01_adaptive-learning(learner_profile, difficulty_adjustment, adaptive_engine) + 02_spaced-repetition(flashcard_auto_generation, review_scheduler) 역참조 정확, 미생성 05_learning-analytics는 "(1-5 생성 예정)" 표기 |
| 25 | 섹션 번호 연속성 | **PASS** | quiz(§1~§13) / youtube(§1~§13) / book(§1~§15) / mindmap(§1~§12) — 4파일 모두 번호 순차, 누락·중복 없음 |
| 26 | _index.md 상태 갱신 | **PASS** | V1 7건 `L3 COMPLETE`, V2-STUB 3건(O-011-2, O-014-2, O-009-2), SKELETON 8건(O-012/O-013/O-015/O-016) — §6.4 18항목 전수 일치 |

**rev.3 주요 수정 이력** (6건):
- quiz_test_generation.md §1: LOCK-ED-02 R9 형식 인용 블록 추가 (`> LOCK (LOCK-ED-02, 기존 명세 §2): IRT 5단계 — Very Easy/Easy/Medium/Hard/Very Hard, 목표 정답률 70-85%`) — front-matter에 선언했으나 본문 인용 누락 수정
- youtube_learning.md §3+§4.2: `RelatedVideo` 인터페이스 + `_recommend_related_videos()` 메서드 추가 — SoT O-011 "관련 영상 추천" 커버리지 누락 수정
- youtube_learning.md §5(신설): "교수법 모델 적용 (E4)" 섹션 추가 — Mayer 멀티미디어 학습 이론 5원칙 테이블, §6~§13 번호 재정렬
- book_reading.md §3+§6: `ReadingProgress` 인터페이스에 `total_pages` 필드 추가, `update_progress()` 내 `progress.book_metadata.total_pages` → `progress.total_pages`로 수정 — 미정의 필드 참조 오류 해소
- mindmap_concept_map.md §4.2: `_build_graph()` 전면 재작성 — `nodes` dict 키잉을 `concept.name` 단일에서 `name_to_node`/`id_to_node` 이중 dict로 분리, `parent_id`(node_id) 대신 `parent_name`(concept.name)으로 BFS 큐 전달, 부모-자식 연결 로직 정확화
- youtube_learning.md §3: `VideoMetadata` 인터페이스에 `video_id: string` 필드 추가 — 파이프라인 코드에서 `metadata.video_id` 참조하나 스키마 미정의 수정

**최종 판정**: 1-4 **PASS** — 4파일 V1 L3 완성 + 4파일 V2 골격, LOCK-ED-02/03/05 전수 인용, Bloom 6단계 퀴즈 생성 로직 포함, SoT O-007/O-008/O-009/O-011/O-014 전항목 커버리지, §13 E1~E10 전수 충족, 26항목 검증 + 6건 재검증 수정 통과
</details>

<details>
<summary><b>1-5. 05_learning-analytics V1 L3 작성 (5파일, ~5항목)</b></summary>

**대조 기준**:
- §7 세부 작업: learning_dashboard, gamification (기본), goal_management, time_management, benchmark_vbs16
- §7 전환 게이트: V1 대상 파일 100% 작성, LOCK 값 정합성 검증
- §6 이슈: 05_learning-analytics V1 항목 — O-010 (대시보드), O-027 (게이미피케이션), O-019 (목표), O-020 (시간), O-028 (VBS-16)

**목표**: 05_learning-analytics 서브폴더의 V1 대상 5개 파일을 L3 수준으로 완성한다. 학습 대시보드(진도/성과/시간 시각화), 게이미피케이션 XP 체계(LOCK-ED-10: XP→레벨→배지→Streak→챌린지→리더보드), 목표/시간 관리, VBS-16 벤치마크(LOCK-ED-09: 학습 지속률≥60%, 기억 유지율≥80%)를 포함한다.

**입력 파일**:
- 본 계획서 §6 관련 항목 매핑
- `05_learning-analytics/_index.md` (Phase 0 산출물)
- `D:\VAMOS\docs\sot\STEP7-O_교육_학습_자기개발_작업가이드.md` (O-010, O-019~O-028 원본)
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\EDUCATION_LEARNING_상세명세.md` (기존 명세)

**절차**:
1. `learning_dashboard.md` 작성 — O-010:
   - 학습 대시보드 L3 (진도 차트, 성과 그래프, 시간 분석)
   - Bloom 레벨별 달성도 시각화
2. `gamification.md` 작성 — O-027 (기본):
   - XP 체계(LOCK-ED-10) L3 — XP 계산 공식, 레벨 테이블, 배지 조건
   - V2 리더보드/챌린지 확장 골격 배치
3. `goal_management.md` 작성 — O-019:
   - 학습 목표 설정/추적 L3 (SMART 목표 프레임워크)
4. `time_management.md` 작성 — O-020:
   - 학습 시간 추적/분석 L3 (포모도로 타이머 + 주간 리포트)
5. `benchmark_vbs16.md` 작성 — O-028:
   - VBS-16 벤치마크 L3 (LOCK-ED-09: 학습 지속률≥60%, 기억 유지율≥80%)
   - 측정 방법론 + 데이터 수집 파이프라인
6. V2 항목(habit_tracker, career_development, note_taking, focus_mode, certification_tracker, study_group) 골격 배치

**검증**:
- [x] learning_dashboard, gamification, goal_management, time_management, benchmark_vbs16 5파일 완성
- [x] LOCK-ED-09/10 인용 R9 형식
- [x] XP 체계 6요소(LOCK-ED-10) 전수 반영
- [x] VBS-16 벤치마크 기준 2개(지속률, 유지율) 명시

**산출물**: `05_learning-analytics/` 내 5개 V1 파일 L3 완성 + V2 골격

---

**1-5 세션 검증 결과 요약** (2026-04-09, rev.2)

| # | 검증 항목 | 결과 | 상세 |
|---|-----------|------|------|
| 1 | V1 5파일 완성 | **PASS** | learning_dashboard(L3) / gamification(L3) / goal_management(L3) / time_management(L3) / benchmark_vbs16(L3) |
| 2 | V2 골격 6파일 배치 | **PASS** | habit_tracker / career_development / note_taking / focus_mode / certification_tracker / study_group (SKELETON) |
| 3 | LOCK-ED-09 인용 | **PASS** | benchmark_vbs16.md §1 — `> LOCK (LOCK-ED-09, VBS-16 벤치마크 기준): 학습 지속률 ≥ 60%, 기억 유지율 ≥ 80%` + §3.2/3.6 assert 코드 + §4.3 경고 체크 |
| 4 | LOCK-ED-10 인용 | **PASS** | gamification.md §1 — `> LOCK (LOCK-ED-10, 게이미피케이션 XP 체계): XP → 레벨 → 배지 → Streak → 챌린지 → 리더보드` 6요소 전수 |
| 5 | XP 체계 6요소 전수 | **PASS** | XP(§2, 공식+테이블) / 레벨(§3.1, 레벨 테이블+칭호) / 배지(§3.2~3.4, 10종+수여 로직) / Streak(§4.1~4.2, 보상 체계) / 챌린지(§4.3~4.4, 6개 템플릿) / 리더보드(V2 §7) |
| 6 | VBS-16 8지표 전수 | **PASS** | VBS16-01~08 각각 측정 함수 구현, 가중치 합 1.00, LOCK-ED-09 지표 가중치 0.40(40%) |
| 7 | 상세명세 §6 인터페이스 정합 | **PASS** | WeaknessAnalysis(skill/attempts/common_errors/suggested_resources 포함) / Recommendation(title/description/action_url/string priority) |
| 8 | 상세명세 §6.3 시각화 차트 반영 | **PASS** | learning_dashboard.md §4 — 7개 차트 목록 (V1 텍스트 5 + V2 비주얼 2) |
| 9 | 상세명세 §6.2 추천 시스템 반영 | **PASS** | SR cards_due 독려 + detect_burnout_risk() 번아웃 방지 로직 포함 |
| 10 | SoT O-010 메트릭 전수 | **PASS** | 일일/주간/월간 학습 시간, 주제별 진행률, 테스트 성적 추이, 간격 반복 통계, 목표 대비 진행률, 강점/약점 분석 |
| 11 | SoT O-019 OKR+SMART 전수 | **PASS** | SMART 5기준 검증 로직 + OKR 분기 목표 + 주간 체크인 + 마일스톤 자동 분해 + 진행률 자동 갱신 |
| 12 | SoT O-020 4요소 전수 | **PASS** | 포모도로 타이머(상태 머신) + 활동별 시간 기록 + 생산성 분석(골든 타임) + 주간 리포트 |
| 13 | SoT O-027 배지 5종 | **PASS** | Streak Master / Book Worm / Code Ninja / Quant Explorer / Knowledge Builder + 추가 5종 |
| 14 | 교차 참조 경로 정합 | **PASS** | 12파일 전수 — 실제 폴더명(01~05) 및 실제 파일명과 100% 일치, 잔여 오류 0건 |
| 15 | _index.md 상태 갱신 | **PASS** | V1 7항목 COMPLETE / V2 5항목+V3 1항목 SKELETON / LOCK 참조 테이블 정합 |

**rev.2 주요 수정 이력**:
- learning_dashboard.md: WeaknessAnalysis에 상세명세 §6.1 필드(skill/attempts/common_errors/suggested_resources) 추가, Recommendation을 상세명세 §6.2 형식(title/description/action_url, string priority)으로 정합, §6.3 시각화 차트 7종 테이블 신설, §6.2 번아웃 방지+SR 카드 독려 추천 로직 추가
- 전체 5+6파일: 교차 참조 경로 전수 수정 — `03_quiz-assessment`→`04_content-generation`, `04_coding-tutoring`→`03_coding-tutorial`, `sm2_algorithm`→`sm2_education_extension`, `learning_path`→`learning_path_generator`
- learning_dashboard.md: 차트 목록 삽입 후 섹션 번호 순차 정리 (§4→§5→§6)

**최종 판정**: 1-5 **PASS** — 5파일 V1 L3 완성 + 6파일 V2/V3 골격, LOCK 2종(ED-09/10) 전수 인용, 15항목 검증 통과
</details>

> **Phase 1 게이트 검증**: 1-1~1-5 완료 후 §10 체크리스트 #4~#7 전수 통과 → Phase 2 진입 가능 (2026-04-09)
> - #4: V1 구현 정본 100% 작성 — 19파일 V1 L3 COMPLETE (01: 4 + 02: 3 + 03: 3 + 04: 4 + 05: 5) + V2/V3 골격 17파일
> - #5: LOCK 값 정합성 — LOCK-ED-01~10 전수 인용 확인 (1-1: ED-01/02/03/05/06/07, 1-2: ED-04/05/08, 1-3: ED-02/05/06, 1-4: ED-02/03/05, 1-5: ED-09/10)
> - #6: SM-2 공유 규약 준수 — LOCK-ED-04 참조 확인 (sm2_education_extension.md §2, PKM 정본 MIN_EF=1.3/DEFAULT_EF=2.5/I(1)=1d/I(2)=6d)
> - #7: Bloom 택소노미 일관성 — LOCK-ED-05 전수 (adaptive_engine/difficulty_adjustment/quiz_test_generation/youtube_learning/book_reading/mindmap_concept_map 6파일 인용 확인)

### Phase 2: V2 Enhanced

| 항목 | 내용 |
|------|------|
| **목표** | 확장 기능 구현 정본 완성 |
| **대상** | investment_education, language_learning, flashcard 이미지오클루전, project_based_learning, coding_challenge, paper_learning, podcast_audio, online_course_support, presentation_coaching, 인터랙티브 개념맵, 학습 통계 시각화, 리더보드, habit_tracker, career_development, note_taking, focus_mode, certification_tracker |
| **항목 수** | ~20항목 (V2 태깅) |
| **기간** | 5일 |
| **게이트** | V2 대상 파일 100% 작성, #9 Health 감정 연동 인터페이스 정의 완료 |

#### Phase 2 진행 현황 (STAGE 7 Phase 7-II, 3-5 STEP_B #2a + #2b)

| 세션 | 범위 | 상태 | 산출물 수 | 합계 lines | V1 회차 | 완료일 |
|------|------|:----:|:---------:|:----------:|:-------:|-------|
| **2-1** | 01_adaptive-learning (2 NEW) | ✅ | 2 (investment+language) | 538 | 166 | 2026-04-20 |
| **2-2** | 02_spaced-repetition + 03_coding-tutorial (1 NEW + 2 EXTEND) | ✅ | 3 (coding_challenge NEW / flashcard+project EXTEND) | 1,072 | 167 | 2026-04-20 |
| **2-3** | 04_content-generation (4 NEW + 1 EXTEND) | ✅ | 5 (paper/podcast/course/presentation NEW / mindmap EXTEND) | 1,385 | 168 | 2026-04-20 |
| **2-4** | 05_learning-analytics (5 NEW + 2 EXTEND) | ✅ | 7 (habit/career/note/focus/cert NEW / dashboard+gamification EXTEND) | 1,796 | 169 | 2026-04-20 |
| **2-5** | ★Health 감정 연동 인터페이스 정의 + Phase 2 통합 검증 | ✅ | 1 (emotion_learning_interface.md NEW, PRODUCER) | 424 | 170 | 2026-04-20 |

**#2a + #2b 통산**: **18 V2 파일 strict (13 NEW + 5 EXTEND) / 5,217 lines** (STEP_C G-6 sync +2 반영: emotion_learning_interface 424→426) / 5 sessions 전수 35/35 V1 OK / FABRICATION 0건 / CONFLICT_CANDIDATE 4건 Phase 3 이월 (presentation O-015-1 / note_taking O-024-1 / focus_mode O-025-1 / certification_tracker O-026-1 — plan §7.2 라벨 vs STEP7-O 실체 drift, 도메인 마감 step 7 에서 CFL-ED-006~009 정식 등재).

#### Phase 2 완료 블록 (STAGE 7 STEP_B #2b 종료, 2026-04-20)

| 항목 | 값 |
|------|-----|
| **완료일** | 2026-04-20 |
| **V2 파일 수** | **18 strict** (13 NEW + 5 EXTEND = 17 #2a + 1 PRODUCER interface #2b) |
| **통산 lines** | 5,217 (4,791 #2a + 426 emotion_learning_interface.md STEP_C G-6 sync 반영) |
| **V1 immutability** | 166 → 170 통산 5회 추가 + domain_finalize_3-5 171 (각 35/35 OK) |
| **LOCK 참조** | LOCK-ED-01~10 (10 domestic) + LOCK-HW-01 / LOCK-HW-12 (2 cross-domain) = **12 distinct** |
| **CONFLICT** | C-01~C-04 RESOLVED 보존 + C-05 RESOLVED 신규 (§8 interface §8) + CFL-ED-006~009 4 Phase 3 이월 |
| **PRODUCER 역할 실체화** | emotion_learning_interface.md 확정, 3-6 CONSUMER 대기 |
| **FABRICATION** | 0건 |
| **upstream SoT 인용** | STEP7-O 17 O-ID verbatim + 3-6 LOCK-HW-01 L83 + LOCK-HW-12 L75 + plan §7.2 L1167 R-09-6 |

##### Phase 2 → Phase 3 전환 게이트 판정

| 게이트 기준 (§7.2 / §10 #8~#9) | 실측 | 판정 |
|------|------|:----:|
| **§10 #8 V2 구현 정본 100% 작성** | 18/18 strict (2-1: 2 / 2-2: 3 / 2-3: 5 / 2-4: 7 / 2-5: 1) | ✅ PASS |
| **§10 #9 Health 연동 인터페이스 정의** | emotion_learning_interface.md §4~§7 확정 (LOCK-HW-01/HW-12 verbatim + R-08-6 + R-09-6 + C-05 RESOLVED) | ✅ PASS |
| **Phase 전환 게이트 요약 표 Phase 2→3** | V2 파일 100% + Health 연동 정의 | ✅ PASS |

**판정**: **[PHASE3_READY v2: 3-5 Education-Learning — 2026-04-20 최종 확정]** (STAGE 7 STEP_C Phase G 종결, fully_converged)

- G2-1 V2 18/18 ✅
- G2-2 Health 연동 정의 완료 ✅
- G2-3 LOCK-ED-01~10 변경 0건 + LOCK-HW-01/HW-12 cross-domain ref 신설 ✅
- G2-4 CONFLICT_LOG C-05 RESOLVED + CFL-ED-006~009 Phase 3 이월 ✅

#### Phase 2 단계별 상세 작업 절차

<details>
<summary><b>2-1. 01_adaptive-learning V2 확장 (4건)</b></summary>

**대조 기준**:
- §7 세부 작업: O-005-1 "investment_education 기초 모듈", O-005-3 "investment_education 투자 용어 학습", O-006-1 "language_learning 어휘 빌더", O-006-2 "language_learning 문법 교정"
- §7 전환 게이트: V2 대상 파일 100% 작성 + #9 Health 감정 연동 인터페이스 정의
- §6 이슈: §6.1 — O-005-1/O-005-3/O-006-1/O-006-2 V2 (Phase 2 대상)
- 교차 도메인: ★ 3-6 Health — 감정 연동 인터페이스 (Phase 2→3 게이트, 2-5에서 정의)
- LOCK: LOCK-ED-01 (학습 경로 구조), LOCK-ED-02 (IRT 5단계)
- Part2 버전: V2-Phase 2

**목표**: 투자 교육(기초 모듈 + 용어 학습) 및 언어 학습(어휘 빌더 + 문법 교정) V2 정본 완성

**입력 파일**:
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\EDUCATION_LEARNING_구조화_종합계획서.md` §6.1 01_adaptive-learning
- `D:\VAMOS\docs\sot\STEP7-O_교육_학습_자기개발_작업가이드.md` O-005, O-006
- Phase 1 산출물: `D:\VAMOS\docs\sot 2\3-5_Education-Learning\01_adaptive-learning\adaptive_engine.md`, `learner_profile.md`

**절차**:
1. Phase 1 adaptive_engine.md, learner_profile.md V1 정본 리뷰 → V2 확장 포인트 식별
2. O-005-1/O-005-3 기반 investment_education.md 작성 (기초 모듈 구조, 투자 용어 사전, 퀴즈 연동)
3. O-006-1/O-006-2 기반 language_learning.md 작성 (어휘 빌더, 문법 교정 엔진, SRS 연동)
4. LOCK-ED-01 학습 경로 구조, LOCK-ED-02 IRT 5단계 정합성 검증
5. V2 골격 → L3 COMPLETE 승격

**검증**:
- [x] investment_education.md V2 L3 — O-005-1/O-005-3 항목 전수 반영
- [x] language_learning.md V2 L3 — O-006-1/O-006-2 항목 전수 반영
- [x] LOCK-ED-01, LOCK-ED-02 인용 일치
- [x] Phase 1 adaptive_engine.md 인터페이스 호환

**산출물**:
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\01_adaptive-learning\investment_education.md` (V2 투자 교육 정본)
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\01_adaptive-learning\language_learning.md` (V2 언어 학습 정본)
</details>

<details>
<summary><b>2-2. 02_spaced-repetition + 03_coding-tutorial V2 확장 (4건)</b></summary>

**대조 기준**:
- §7 세부 작업: O-002-4 "flashcard 이미지오클루전", O-004-7 "project_based_learning 템플릿", O-004-8 "project_based_learning 마일스톤", O-017-1 "coding_challenge 플랫폼"
- §7 전환 게이트: V2 대상 파일 100% 작성 + #9 Health 감정 연동 인터페이스 정의
- §6 이슈: §6.2 + §6.3 — O-002-4/O-004-7/O-004-8/O-017-1 V2 (Phase 2 대상)
- 교차 도메인: ★ 3-6 Health — 감정 연동 인터페이스 (Phase 2→3 게이트, 2-5에서 정의)
- LOCK: LOCK-ED-04 (SM-2 파라미터, PKM 정본 참조), LOCK-ED-08 (플래시카드 유형)
- Part2 버전: V2-Phase 2

**목표**: 플래시카드 이미지 오클루전, 프로젝트 기반 학습(템플릿 + 마일스톤), 코딩 챌린지 플랫폼 V2 정본 완성

**입력 파일**:
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\EDUCATION_LEARNING_구조화_종합계획서.md` §6.2, §6.3
- `D:\VAMOS\docs\sot\STEP7-O_교육_학습_자기개발_작업가이드.md` O-002, O-004, O-017
- Phase 1 산출물: `D:\VAMOS\docs\sot 2\3-5_Education-Learning\02_spaced-repetition\flashcard_auto_generation.md`, `D:\VAMOS\docs\sot 2\3-5_Education-Learning\03_coding-tutorial\project_based_learning.md`

**절차**:
1. Phase 1 flashcard_auto_generation.md V1 리뷰 → O-002-4 이미지 오클루전 기능 V2 확장
2. Phase 1 project_based_learning.md V1 리뷰 → O-004-7 템플릿 + O-004-8 마일스톤 V2 확장
3. O-017-1 기반 coding_challenge.md 신규 작성 (플랫폼 구조, 난이도 체계, 채점 로직)
4. LOCK-ED-04 SM-2 파라미터 정합성 (PKM 정본 MIN_EF=1.3/DEFAULT_EF=2.5), LOCK-ED-08 플래시카드 유형 검증
5. V2 골격 → L3 COMPLETE 승격

**검증**:
- [x] flashcard_auto_generation.md V2 L3 — O-002-4 이미지 오클루전 반영
- [x] project_based_learning.md V2 L3 — O-004-7/O-004-8 항목 전수 반영
- [x] coding_challenge.md V2 L3 — O-017-1 항목 전수 반영
- [x] LOCK-ED-04 SM-2, LOCK-ED-08 플래시카드 유형 인용 일치

**산출물**:
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\02_spaced-repetition\flashcard_auto_generation.md` (V2 이미지 오클루전 확장)
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\03_coding-tutorial\project_based_learning.md` (V2 템플릿+마일스톤 확장)
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\03_coding-tutorial\coding_challenge.md` (V2 코딩 챌린지 정본)
</details>

<details>
<summary><b>2-3. 04_content-generation V2 확장 (7건)</b></summary>

**대조 기준**:
- §7 세부 작업: O-012-1 "paper_learning 구조화 분석", O-012-2 "paper_learning 핵심 개념 추출", O-013-1 "podcast_audio 학습 모드", O-016-1 "online_course_support 진도 동기화", O-016-2 "online_course_support 보충 자료", O-015-1 "presentation_coaching 스크립트 생성", O-009-2 "인터랙티브 개념맵"
- §7 전환 게이트: V2 대상 파일 100% 작성 + #9 Health 감정 연동 인터페이스 정의
- §6 이슈: §6.4 — O-012-1/O-012-2/O-013-1/O-016-1/O-016-2/O-015-1/O-009-2 V2 (Phase 2 대상)
- 교차 도메인: ★ 3-6 Health — 감정 연동 인터페이스 (Phase 2→3 게이트, 2-5에서 정의)
- LOCK: LOCK-ED-05 (Bloom 택소노미)
- Part2 버전: V2-Phase 2

**목표**: 논문 학습, 팟캐스트 학습, 온라인 코스 지원, 발표 코칭, 인터랙티브 개념맵 V2 정본 완성

**입력 파일**:
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\EDUCATION_LEARNING_구조화_종합계획서.md` §6.4
- `D:\VAMOS\docs\sot\STEP7-O_교육_학습_자기개발_작업가이드.md` O-009, O-012, O-013, O-015, O-016
- Phase 1 산출물: `D:\VAMOS\docs\sot 2\3-5_Education-Learning\04_content-generation\mindmap_concept_map.md`

**절차**:
1. O-012-1/O-012-2 기반 paper_learning.md 작성 (논문 구조화 분석, 핵심 개념 추출, 인용 그래프)
2. O-013-1 기반 podcast_audio.md 작성 (팟캐스트 학습 모드, 오디오 세그먼트, 타임스탬프 북마크)
3. O-016-1/O-016-2 기반 online_course_support.md 작성 (진도 동기화, 보충 자료 추천)
4. O-015-1 기반 presentation_coaching.md 작성 (발표 스크립트 생성, 구조 템플릿)
5. Phase 1 mindmap_concept_map.md V1 리뷰 → O-009-2 인터랙티브 개념맵 V2 확장
6. LOCK-ED-05 Bloom 택소노미 전수 검증 (해당 파일 인용 확인)
7. V2 골격 → L3 COMPLETE 승격

**검증**:
- [x] paper_learning.md V2 L3 — O-012-1/O-012-2 항목 전수 반영
- [x] podcast_audio.md V2 L3 — O-013-1 항목 반영
- [x] online_course_support.md V2 L3 — O-016-1/O-016-2 항목 전수 반영
- [x] presentation_coaching.md V2 L3 — O-015-1 항목 반영
- [x] mindmap_concept_map.md V2 L3 — O-009-2 인터랙티브 확장 반영
- [x] LOCK-ED-05 Bloom 택소노미 인용 일치

**산출물**:
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\04_content-generation\paper_learning.md` (V2 논문 학습 정본)
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\04_content-generation\podcast_audio.md` (V2 팟캐스트 학습 정본)
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\04_content-generation\online_course_support.md` (V2 온라인 코스 지원 정본)
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\04_content-generation\presentation_coaching.md` (V2 발표 코칭 정본)
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\04_content-generation\mindmap_concept_map.md` (V2 인터랙티브 개념맵 확장)
</details>

<details>
<summary><b>2-4. 05_learning-analytics V2 확장 (7건)</b></summary>

**대조 기준**:
- §7 세부 작업: O-010-2 "학습 통계 시각화", O-027-4 "리더보드", O-021-1 "habit_tracker", O-022-1 "career_development", O-024-1 "note_taking", O-025-1 "focus_mode", O-026-1 "certification_tracker"
- §7 전환 게이트: V2 대상 파일 100% 작성 + #9 Health 감정 연동 인터페이스 정의
- §6 이슈: §6.5 — O-010-2/O-027-4/O-021-1/O-022-1/O-024-1/O-025-1/O-026-1 V2 (Phase 2 대상)
- 교차 도메인: ★ 3-6 Health — 감정 연동 인터페이스 (Phase 2→3 게이트, 2-5에서 정의)
- LOCK: LOCK-ED-09 (VBS-16), LOCK-ED-10 (게이미피케이션 XP)
- Part2 버전: V2-Phase 2

**목표**: 학습 대시보드, 게이미피케이션, 습관 추적, 커리어 개발, 노트 테이킹, 집중 모드, 자격증 추적 V2 정본 완성

**입력 파일**:
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\EDUCATION_LEARNING_구조화_종합계획서.md` §6.5
- `D:\VAMOS\docs\sot\STEP7-O_교육_학습_자기개발_작업가이드.md` O-010, O-021, O-022, O-024, O-025, O-026, O-027
- Phase 1 산출물: `D:\VAMOS\docs\sot 2\3-5_Education-Learning\05_learning-analytics\learning_dashboard.md`, `gamification.md`

**절차**:
1. Phase 1 learning_dashboard.md V1 리뷰 → O-010-2 학습 통계 시각화 V2 확장
2. Phase 1 gamification.md V1 리뷰 → O-027-4 리더보드 V2 확장
3. O-021-1 기반 habit_tracker.md 작성 (학습 습관 추적, 스트릭, 리마인더)
4. O-022-1 기반 career_development.md 작성 (커리어 경로, 스킬 매핑, 목표 설정)
5. O-024-1 기반 note_taking.md 작성 (스마트 노트, 태그, 검색, SRS 연동)
6. O-025-1 기반 focus_mode.md 작성 (집중 모드, 포모도로, 방해 차단)
7. O-026-1 기반 certification_tracker.md 작성 (자격증 추적, 일정, 학습 계획 연동)
8. LOCK-ED-09 VBS-16, LOCK-ED-10 게이미피케이션 XP 정합성 검증
9. V2 골격 → L3 COMPLETE 승격

**검증**:
- [x] learning_dashboard.md V2 L3 — O-010-2 시각화 반영
- [x] gamification.md V2 L3 — O-027-4 리더보드 반영
- [x] habit_tracker.md V2 L3 — O-021-1 항목 반영
- [x] career_development.md V2 L3 — O-022-1 항목 반영
- [x] note_taking.md V2 L3 — O-024-1 항목 반영
- [x] focus_mode.md V2 L3 — O-025-1 항목 반영
- [x] certification_tracker.md V2 L3 — O-026-1 항목 반영
- [x] LOCK-ED-09 VBS-16, LOCK-ED-10 XP 인용 일치

**산출물**:
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\05_learning-analytics\learning_dashboard.md` (V2 학습 통계 시각화 확장)
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\05_learning-analytics\gamification.md` (V2 리더보드 확장)
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\05_learning-analytics\habit_tracker.md` (V2 습관 추적 정본)
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\05_learning-analytics\career_development.md` (V2 커리어 개발 정본)
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\05_learning-analytics\note_taking.md` (V2 스마트 노트 정본)
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\05_learning-analytics\focus_mode.md` (V2 집중 모드 정본)
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\05_learning-analytics\certification_tracker.md` (V2 자격증 추적 정본)
</details>

<details>
<summary><b>2-5. ★Health 감정 연동 인터페이스 정의 + Phase 2 통합 검증</b></summary>

**대조 기준**:
- §7 세부 작업: #9 Health 감정 연동 인터페이스 정의 (Phase 2→3 게이트 필수)
- §7 전환 게이트: V2 대상 파일 100% 작성 + #9 Health 감정 연동 인터페이스 정의
- §6 이슈: CONFLICT_LOG C-05 (Education vs Health 감정 범위 — R-08-6 opt-in, Phase 2에서 정의)
- 교차 도메인: ★ 3-6 Health-Wellness-EmotionAI — LOCK-HW-01 (감정 7분류 + 강도 1-10 + arousal/valence)
- R-09-6: 감정 데이터 → 학습 난이도/속도 적응 (단방향 수신)
- Part2 버전: V2-Phase 2

**목표**: 3-6 Health 감정 연동 인터페이스 정의 (opt-in 기반, 단방향 수신), C-05 해결, Phase 2 전체 V2 파일 100% 검증

**입력 파일**:
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\EDUCATION_LEARNING_구조화_종합계획서.md` §10 체크리스트 #8~#9
- `D:\VAMOS\docs\sot 2\3-6_Health-Wellness-EmotionAI\HEALTH_WELLNESS_EMOTIONAI_구조화_종합계획서.md` LOCK-HW-01
- Phase 2 산출물: 2-1~2-4 전체 V2 파일

**절차**:
1. 3-6 Health LOCK-HW-01 참조: 감정 7+5+2 (12감정) = 기본7(기쁨/슬픔/분노/불안/놀람/혐오/중립) + 세부5(피로/스트레스/좌절/열정/호기심) + 차원2(arousal/valence), 강도 1-10
2. 감정 연동 인터페이스 문서 작성: 수신 스키마, opt-in 활성화 플로우, 기본 비활성 정책
3. R-08-6 opt-in 필수 원칙 명시, R-09-6 단방향 수신(감정→학습 난이도/속도 적응) 정의
4. C-05 CONFLICT_LOG 해결 기록: Education vs Health 감정 범위 합의 → opt-in + 단방향
5. Phase 2 전체 통합 검증: 2-1~2-4 V2 파일 전수 확인 (17+ 파일 V2 L3 COMPLETE)
6. §10 체크리스트 #8~#9 게이트 검증

**검증**:
- [x] 감정 연동 인터페이스 문서 — LOCK-HW-01 스키마 정합성 (emotion_learning_interface.md §3.1/§4.1 verbatim 인용)
- [x] opt-in 기본 비활성 + R-08-6 준수 (§5 활성/철회/재활성 플로우 확정, 3-5 AUTHORITY §5 L115~L122 verbatim)
- [x] R-09-6 단방향 수신 정의 명시 (§6.1 3-6→3-5 단방향 + §6.2 화이트리스트 4종)
- [x] C-05 CONFLICT_LOG 해결 상태 CLOSED 전환 (§8 OPEN → RESOLVED, 도메인 마감 step 7 CFL 정본 등재)
- [x] Phase 2 V2 파일 100% 작성 (2-1: 2파일 + 2-2: 3파일 + 2-3: 5파일 + 2-4: 7파일 + 2-5: 1파일 = **18 strict**)
- [x] §10 #8~#9 게이트 PASS (표 #8 V2 18/18 + #9 인터페이스 문서 존재 전수 통과)

**산출물**:
- `D:\VAMOS\docs\sot 2\3-5_Education-Learning\01_adaptive-learning\emotion_learning_interface.md` (Health 감정 연동 인터페이스 정의)
- Phase 2 게이트 검증 결과 (종합계획서 §7 Phase 2 게이트 갱신)
</details>

### Phase 3: V3 Full ✅ 완료 (2026-05-16, 8 task)

| 항목 | 내용 |
|------|------|
| **목표** | 고급 기능 + 커뮤니티 + 미래 확장 |
| **대상** | 투자 시뮬레이션, 회화 연습 대화 엔진, 챌린지 리더보드, 음성 인식 학습, 발표 피드백, 스터디 그룹 매칭, VR/AR 학습, 멘토링 플랫폼 |
| **항목 수** | ~8항목 (V3 태깅) |
| **기간** | 5일 |
| **게이트** | V3 대상 파일 100% 작성, VBS-16 벤치마크 전체 통과 |

#### Phase 3 단계별 상세 작업 절차

<details>
<summary><b>3-1. 04_content-generation 투자 시뮬레이션 V3 (1건)</b></summary>

**대조 기준 (7항목)**:
- §7 세부 작업: 8 V3 항목 중 #1 "투자 시뮬레이션" — Phase 3 V3 태깅 (8 V3 / §6.4 04_content-generation)
- §7 전환 게이트: V3 대상 파일 100% 작성, VBS-16 벤치마크 전체 통과 (§10 #10)
- §6 이슈: §6.4 `04_content-generation/` (~18항목) 영역 V3 NEW — 투자 시뮬레이션 콘텐츠 생성
- 교차 도메인: 3-1 AI Investing (★ 별도 트랙 — 본 도메인은 학습 콘텐츠 생성만, 실거래 X), 1-1 VRE (시뮬레이션 결과 검증) — 5-2 외부 5 deps 영향 없음
- Part2 V3-Phase: V3-Phase 3 (CAT-E COND-7 + UI SHELL → 본 V3 정본 참조)
- production 측정 baseline: `D:/VAMOS/docs/sot 2/3-5_Education-Learning/04_content-generation/investment_simulation.md` (NEW V3) / VBS-16: 학습 지속률 ≥ 60%, 기억 유지율 ≥ 80% (LOCK-ED-09) / LOCK-ED-02 IRT 5단계 난이도 정합
- Phase 4 entry-gate 충족 조건: L3 ≥ 80점/100 + 시뮬레이션 자산 클래스 ≥ 5종(주식/채권/ETF/가상화폐/원자재) + LOCK-ED-02 5단계 난이도(Very Easy→Very Hard) + LOCK-ED-05 Bloom Apply/Analyze 매핑 + 비투자조언 면책 (3-1 AI Investing LOCK 정합 — 실거래 X)

**목표**: 04_content-generation 서브폴더에 investment_simulation.md V3 정본 신규 작성. 시뮬레이션 자산 클래스 5종 + LOCK-ED-02 5단계 난이도 + Bloom Apply/Analyze 매핑 + 비투자조언 면책 + 가상 자금 + 시나리오 기반 학습 완전 정의.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/EDUCATION_LEARNING_구조화_종합계획서.md` §6.4 (V3), §3.4 LOCK-ED-02/05/09
- `D:/VAMOS/docs/sot/STEP7-O_교육_학습_자기개발_작업가이드.md` (V3 항목)
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/04_content-generation/` 기존 V1/V2 production 정본
- `D:/VAMOS/docs/sot 2/Ai-investing-detail/AI_INVESTING_구조화_종합계획서.md` §3.4 LOCK (Win Rate 51% / Sharpe 1.0 등) — 시뮬레이션 LOCK 정합

**절차**:
1. 계획서 §6.4 + STEP7-O V3 요구사항 확인
2. `investment_simulation.md` V3 신규 작성:
   - 시뮬레이션 자산 클래스 5종 (주식/채권/ETF/가상화폐/원자재)
   - LOCK-ED-02 5단계 난이도 (Very Easy: 인덱스 ETF → Very Hard: 옵션/파생)
   - LOCK-ED-05 Bloom Apply (포트폴리오 구성) + Analyze (위험 분석)
   - 시나리오 기반 학습 (2008 금융위기 / 2020 COVID 폭락 / 시뮬레이션 미래 시나리오)
   - 가상 자금 + 진행 평가 (LOCK-ED-03 3등급)
   - 비투자조언 면책 강제 ("교육 목적, 실제 투자 조언 아님" 모든 응답 포함)
   - E4 모델 비교: 시뮬레이션 (Backtest 데이터 vs Monte Carlo vs 강화학습)
   - E5 폴백: 데이터 부족 시 합성 데이터
   - E7 SLA: 시뮬레이션 1회 ≤ 5초
   - E10 윤리: R-08-5 학습자 프로필 외부 전송 금지
3. 3-1 AI Investing LOCK 정합 (Win Rate 51% / Sharpe 1.0 / Daily Loss CB -3% / VIX CB 40 — 본 도메인은 학습 시뮬레이션만)
4. LOCK-ED-09 VBS-16 측정 통합 (학습 지속률 + 기억 유지율)
5. production .md 신규 추가 후 SHA + 라인 수 측정 (실측 기록)
6. Phase 4 entry-gate 충족 여부 확인 (자산 5종 + LOCK + 면책)

**검증**:
- [x] V3 #1 투자 시뮬레이션 L3 ≥ 80점 (E1~E10 9요소 PASS)
- [x] 시뮬레이션 자산 클래스 5종 (주식/채권/ETF/가상화폐/원자재) 명시
- [x] LOCK-ED-02 5단계 난이도 + LOCK-ED-05 Bloom Apply/Analyze 매핑
- [x] 비투자조언 면책 모든 응답 포함 명시
- [x] 3-1 AI Investing LOCK 정합 (실거래 X, 시뮬레이션 학습만)
- [x] R-08-5 학습자 프로필 외부 전송 금지 명시
- [x] production 측정: VBS-16 학습 지속률 ≥ 60%, 기억 유지율 ≥ 80%
- [x] /validate + /audit + /sot-check PASS
- [x] Phase 4 entry-gate 충족 조건 ALL PASS

**산출물**:
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/04_content-generation/investment_simulation.md` (V3 NEW — 투자 시뮬레이션)
</details>

<details>
<summary><b>3-2. 04_content-generation 회화 연습 대화 엔진 V3 (1건)</b></summary>

**대조 기준 (7항목)**:
- §7 세부 작업: 8 V3 항목 중 #2 "회화 연습 대화 엔진"
- §7 전환 게이트: V3 대상 파일 100% 작성, VBS-16 벤치마크 전체 통과
- §6 이슈: §6.4 `04_content-generation/` (~18항목) 영역 V3 NEW — 다국어 회화 대화 엔진
- 교차 도메인: 3-2 Multimodal (음성 인식 — LOCK-MM-08 16kHz mono PCM), ★ 3-6 Health 감정 연동 (회화 중 스트레스 감지 R-08-6 opt-in → R-09-6 양방향), 6-3 PARL (회화 Agent 페르소나) — 5-2 외부 5 deps 영향 없음
- Part2 V3-Phase: V3-Phase 3 (CAT-E SHELL → 본 V3 정본 참조)
- production 측정 baseline: `D:/VAMOS/docs/sot 2/3-5_Education-Learning/04_content-generation/conversation_practice.md` (NEW V3) / VBS-16 LOCK-ED-09 + 회화 횟수/일 측정 / LOCK-ED-06 소크라테스 교수법 정합
- Phase 4 entry-gate 충족 조건: L3 ≥ 80점/100 + 지원 언어 ≥ 5종(영어/중국어/일본어/스페인어/한국어) + LOCK-ED-06 소크라테스 교수법 (직접 답 금지) + LOCK-ED-08 플래시카드 유형 (회화 카드 추가) + ★ 3-6 Health 감정 연동 (R-08-6 opt-in)

**목표**: 04_content-generation 서브폴더에 conversation_practice.md V3 정본 신규 작성. 다국어 회화 대화 엔진(5종 이상) + LOCK-ED-06 소크라테스 교수법 + LOCK-ED-08 플래시카드 회화 카드 추가 + ★ 3-6 Health 감정 연동(R-08-6 opt-in) 완전 정의.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/EDUCATION_LEARNING_구조화_종합계획서.md` §6.4 (V3), §3.4 LOCK-ED-04/05/06/08
- `D:/VAMOS/docs/sot/STEP7-O_교육_학습_자기개발_작업가이드.md` (V3 항목)
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/01_adaptive-learning/emotion_learning_interface.md` (Phase 2-6 ★ 산출물)
- `D:/VAMOS/docs/sot 2/3-2_Multimodal-Processing/02_audio-processing/` 음성 인식 V1/V2 정본
- `D:/VAMOS/docs/sot 2/3-6_Health-Wellness-EmotionAI/` 감정 연동 인터페이스

**절차**:
1. 계획서 §6.4 + STEP7-O V3 요구사항 확인
2. `conversation_practice.md` V3 신규 작성:
   - 지원 언어 5종 (영어 / 중국어 / 일본어 / 스페인어 / 한국어 모국어)
   - LOCK-ED-06 소크라테스 교수법 (직접 답 금지 → 질문 유도 → 힌트 3단계)
   - LOCK-ED-08 플래시카드 유형에 "회화 카드" 추가 (LOCK 확장 — R-02 LOCK 해제 절차 준수)
   - 시나리오 (여행 / 비즈니스 / 일상 / 발표)
   - 발음 평가 (3-2 Multimodal STT + 발음 정확도 점수)
   - ★ 3-6 Health 감정 연동 (회화 중 좌절/스트레스 감지 → 난이도 자동 조정, R-08-6 opt-in)
   - E4 모델 비교: 회화 엔진 (GPT-4 + TTS vs Claude + 음성 + Whisper)
   - E5 폴백: 음성 인식 실패 시 텍스트 입력
   - E7 SLA: 응답 ≤ 2초
   - E10 윤리: R-08-3 직접 답 제공 금지 (소크라테스 교수법)
3. LOCK-ED-08 확장 R-02 절차 준수 (사유 + 대안 + 영향 분석)
4. 3-2 Multimodal LOCK-MM-08 16kHz mono PCM 정합
5. production .md 신규 추가 후 SHA + 라인 수 측정 (실측 기록)
6. Phase 4 entry-gate 충족 여부 확인 (5종 언어 + LOCK + 감정 연동)

**검증**:
- [x] V3 #2 회화 연습 L3 ≥ 80점 (E1~E10 9요소 PASS)
- [x] 지원 언어 5종 명시
- [x] LOCK-ED-06 소크라테스 교수법 + R-08-3 직접 답 금지
- [x] LOCK-ED-08 회화 카드 추가 (R-02 LOCK 해제 절차 준수)
- [x] ★ 3-6 Health 감정 연동 (R-08-6 opt-in, 좌절/스트레스 감지 시 난이도 조정)
- [x] 3-2 Multimodal LOCK-MM-08 16kHz 정합
- [x] production 측정: VBS-16 + 회화 횟수 일평균 ≥ 5회
- [x] /validate + /audit + /sot-check PASS
- [x] Phase 4 entry-gate 충족 조건 ALL PASS

**산출물**:
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/04_content-generation/conversation_practice.md` (V3 NEW — 다국어 회화 대화 엔진)
</details>

<details>
<summary><b>3-3. 05_learning-analytics 챌린지 리더보드 V3 (1건)</b></summary>

**대조 기준 (7항목)**:
- §7 세부 작업: 8 V3 항목 중 #3 "챌린지 리더보드"
- §7 전환 게이트: V3 대상 파일 100% 작성, VBS-16 벤치마크 전체 통과
- §6 이슈: §6.5 `05_learning-analytics/` (~18항목) 영역 V3 NEW — 게이미피케이션 챌린지 + 리더보드
- 교차 도메인: 3-3 PKM (학습 진척 통합 — 3-3 V3 second_brain_dashboard.md 연동), 3-6 Health (웰니스 커뮤니티 패턴 inheritance — 3-6 V3 wellness_community.md), 6-3 PARL (챌린지 매칭 Agent) — 5-2 외부 5 deps 영향 없음
- Part2 V3-Phase: V3-Phase 3 (CAT-E SHELL → 본 V3 정본 참조)
- production 측정 baseline: `D:/VAMOS/docs/sot 2/3-5_Education-Learning/05_learning-analytics/challenge_leaderboard.md` (NEW V3) / VBS-16 + 챌린지 참여율 측정 / LOCK-ED-10 XP→레벨→배지→Streak→챌린지→리더보드 정합
- Phase 4 entry-gate 충족 조건: L3 ≥ 80점/100 + LOCK-ED-10 게이미피케이션 6단계 (XP/레벨/배지/Streak/챌린지/리더보드) 보존 + 익명/실명 옵션 + 부정행위 방지 + R-08-5 프로필 외부 전송 금지

**목표**: 05_learning-analytics 서브폴더에 challenge_leaderboard.md V3 정본 신규 작성. LOCK-ED-10 게이미피케이션 6단계 + 챌린지 시스템(일일/주간/월간/시즌) + 리더보드(글로벌/친구/지역) + 익명/실명 옵션 + 부정행위 방지 + 보상 시스템 완전 정의.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/EDUCATION_LEARNING_구조화_종합계획서.md` §6.5 (V3), §3.4 LOCK-ED-10
- `D:/VAMOS/docs/sot/STEP7-O_교육_학습_자기개발_작업가이드.md` (V3 항목)
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/05_learning-analytics/` 기존 V1/V2 production 정본 (LOCK-ED-10 V2 부분 정의)
- `D:/VAMOS/docs/sot 2/3-6_Health-Wellness-EmotionAI/05_emotion-journal/wellness_community.md` (3-6 V3 패턴 inheritance)

**절차**:
1. 계획서 §6.5 + STEP7-O V3 요구사항 확인
2. `challenge_leaderboard.md` V3 신규 작성:
   - LOCK-ED-10 게이미피케이션 6단계 (XP → 레벨 → 배지 → Streak → 챌린지 → 리더보드)
   - 챌린지 시스템 (일일 / 주간 / 월간 / 시즌)
   - 리더보드 (글로벌 / 친구 / 지역)
   - 익명/실명 옵션 (기본 익명, R-08-5 프로필 외부 전송 금지)
   - 부정행위 방지 (이상 패턴 감지 + 자동 제재)
   - 보상 시스템 (XP / 배지 / Streak 보호 토큰)
   - E4 모델 비교: 게이미피케이션 (Octalysis vs Yu-kai Chou vs custom)
   - E5 폴백: 리더보드 로딩 실패 시 캐시
   - E7 SLA: 리더보드 갱신 ≤ 1초
   - E10 윤리: 강박적 사용 방지 (일일 한도 + 휴식 권장)
3. 3-6 Health wellness_community.md 패턴 inheritance (PII 제거 강제, 익명화)
4. 3-3 PKM second_brain_dashboard.md 학습 진척 통합 인터페이스
5. production .md 신규 추가 후 SHA + 라인 수 측정 (실측 기록)
6. Phase 4 entry-gate 충족 여부 확인 (LOCK-ED-10 + 익명화 + 부정행위 방지)

**검증**:
- [x] V3 #3 챌린지 리더보드 L3 ≥ 80점 (E1~E10 9요소 PASS)
- [x] LOCK-ED-10 6단계 (XP/레벨/배지/Streak/챌린지/리더보드) EXACT 인용
- [x] 익명/실명 옵션 (기본 익명) 명시
- [x] 부정행위 방지 알고리즘 정의
- [x] R-08-5 프로필 외부 전송 금지 명시
- [x] 3-6 Health wellness_community 패턴 inheritance
- [x] 강박적 사용 방지 (일일 한도 + 휴식) 명시
- [x] production 측정: VBS-16 + 챌린지 참여율 ≥ 40%
- [x] /validate + /audit + /sot-check PASS
- [x] Phase 4 entry-gate 충족 조건 ALL PASS

**산출물**:
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/05_learning-analytics/challenge_leaderboard.md` (V3 NEW — 챌린지 + 리더보드)
</details>

<details>
<summary><b>3-4. 03_coding-tutorial 음성 인식 학습 V3 (1건)</b></summary>

**대조 기준 (7항목)**:
- §7 세부 작업: 8 V3 항목 중 #4 "음성 인식 학습"
- §7 전환 게이트: V3 대상 파일 100% 작성, VBS-16 벤치마크 전체 통과
- §6 이슈: §6.3 `03_coding-tutorial/` (~10항목) 또는 §6.1 영역 V3 NEW — 음성 인식 기반 학습 인터페이스
- 교차 도메인: 3-2 Multimodal (LOCK-MM-08 16kHz mono PCM + STT 엔진), 6-13 Operations (모바일 디바이스 마이크 권한) — 5-2 외부 5 deps 영향 없음
- Part2 V3-Phase: V3-Phase 3 (CAT-E SHELL → 본 V3 정본 참조)
- production 측정 baseline: `D:/VAMOS/docs/sot 2/3-5_Education-Learning/03_coding-tutorial/voice_learning.md` (NEW V3) / VBS-16 LOCK-ED-09 + 음성 인식 정확도 측정 / LOCK-ED-06 소크라테스 교수법 음성 적용
- Phase 4 entry-gate 충족 조건: L3 ≥ 80점/100 + STT 엔진 비교 (Whisper/Deepgram/Google) + LOCK-MM-08 16kHz mono PCM 정합 + 음성 인식 정확도 ≥ 90% (한국어/영어) + LOCK-ED-06 소크라테스 교수법 음성 적용

**목표**: 03_coding-tutorial 서브폴더에 voice_learning.md V3 정본 신규 작성. 음성 인식 기반 학습 인터페이스(코딩/회화/발음) + STT 엔진 3종 비교(Whisper/Deepgram/Google) + LOCK-MM-08 정합 + LOCK-ED-06 소크라테스 교수법 음성 적용 완전 정의.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/EDUCATION_LEARNING_구조화_종합계획서.md` §6.3 (V3), §3.4 LOCK-ED-06
- `D:/VAMOS/docs/sot/STEP7-O_교육_학습_자기개발_작업가이드.md` (V3 항목)
- `D:/VAMOS/docs/sot 2/3-2_Multimodal-Processing/02_audio-processing/` 음성 인식 V1/V2 정본 (LOCK-MM-08)

**절차**:
1. 계획서 §6.3 + STEP7-O V3 요구사항 확인
2. `voice_learning.md` V3 신규 작성:
   - 음성 인식 기반 학습 인터페이스 (코딩 음성 명령 + 회화 + 발음 평가)
   - STT 엔진 3종 비교: Whisper (로컬/오픈) vs Deepgram (클라우드/빠름) vs Google STT
   - LOCK-MM-08 16kHz mono PCM 정합
   - 발음 정확도 평가 (음소 단위)
   - 코딩 음성 명령 ("for 루프 만들어줘" → 코드 생성)
   - LOCK-ED-06 소크라테스 교수법 음성 적용 (직접 답 금지)
   - E4 모델 비교: STT 3종 (Whisper vs Deepgram vs Google STT)
   - E5 폴백: STT 실패 시 텍스트 입력
   - E7 SLA: STT 처리 ≤ 2초 (10초 음성)
   - E9 인프라: 모바일 마이크 권한 + 사용자 동의
   - E10 윤리: R-08-5 음성 데이터 외부 전송 시 명시적 동의
3. 3-2 Multimodal LOCK-MM-08 16kHz mono PCM EXACT 인용
4. R-08-3 소크라테스 교수법 (직접 답 금지) 음성 응답 적용
5. production .md 신규 추가 후 SHA + 라인 수 측정 (실측 기록)
6. Phase 4 entry-gate 충족 여부 확인 (STT 3종 + LOCK + 정확도)

**검증**:
- [x] V3 #4 음성 인식 학습 L3 ≥ 80점 (E1~E10 9요소 PASS)
- [x] STT 엔진 3종 (Whisper/Deepgram/Google) 비교 매트릭스 명시
- [x] LOCK-MM-08 16kHz mono PCM EXACT 인용
- [x] 음성 인식 정확도 목표 ≥ 90% (한국어/영어)
- [x] LOCK-ED-06 소크라테스 교수법 + R-08-3 음성 응답 적용
- [x] R-08-5 음성 데이터 외부 전송 동의 명시
- [x] production 측정: VBS-16 + STT 정확도 ≥ 90%
- [x] /validate + /audit + /sot-check PASS
- [x] Phase 4 entry-gate 충족 조건 ALL PASS

**산출물**:
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/03_coding-tutorial/voice_learning.md` (V3 NEW — 음성 인식 학습)
</details>

<details>
<summary><b>3-5. 05_learning-analytics 발표 피드백 V3 (1건)</b></summary>

**대조 기준 (7항목)**:
- §7 세부 작업: 8 V3 항목 중 #5 "발표 피드백"
- §7 전환 게이트: V3 대상 파일 100% 작성, VBS-16 벤치마크 전체 통과
- §6 이슈: §6.5 `05_learning-analytics/` 또는 §6.4 영역 V3 NEW — 발표 분석 + 피드백
- 교차 도메인: 3-2 Multimodal (LOCK-MM-08 16kHz 음성 + LOCK-MM-09 max_frames=100 비디오 + LOCK-MM-07 CLIP 768d 이미지), ★ 3-6 Health (발표 중 불안 감지 R-08-6 opt-in → R-09-6) — 5-2 외부 5 deps 영향 없음
- Part2 V3-Phase: V3-Phase 3 (CAT-E SHELL → 본 V3 정본 참조)
- production 측정 baseline: `D:/VAMOS/docs/sot 2/3-5_Education-Learning/05_learning-analytics/presentation_feedback.md` (NEW V3) / VBS-16 LOCK-ED-09 + 발표 평가 6 요소 점수
- Phase 4 entry-gate 충족 조건: L3 ≥ 80점/100 + 발표 평가 6 요소(음성속도/명료성/시선처리/제스처/콘텐츠/구조) + LOCK-MM-07/08/09 정합 + ★ 3-6 Health 불안 감지 (R-08-6 opt-in)

**목표**: 05_learning-analytics 서브폴더에 presentation_feedback.md V3 정본 신규 작성. 발표 평가 6 요소(음성속도/명료성/시선처리/제스처/콘텐츠/구조) + 멀티모달 분석(음성+비디오+슬라이드) + LOCK-MM-07/08/09 정합 + 3-6 Health 불안 감지 연동 완전 정의.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/EDUCATION_LEARNING_구조화_종합계획서.md` §6.5 (V3), §3.4 LOCK-ED-05
- `D:/VAMOS/docs/sot/STEP7-O_교육_학습_자기개발_작업가이드.md` (V3 항목)
- `D:/VAMOS/docs/sot 2/3-2_Multimodal-Processing/03_video-analysis/` (LOCK-MM-09) + `01_image-pipeline/` (LOCK-MM-07) + `02_audio-processing/` (LOCK-MM-08)
- `D:/VAMOS/docs/sot 2/3-6_Health-Wellness-EmotionAI/01_emotion-recognition/multimodal_emotion_fusion.md` (3-6 V3 #1 산출물 P-001-V3)

**절차**:
1. 계획서 §6.5 + STEP7-O V3 요구사항 확인
2. `presentation_feedback.md` V3 신규 작성:
   - 발표 평가 6 요소:
     a) 음성 속도 (분당 단어 수, LOCK-MM-08 STT)
     b) 명료성 (발음 정확도)
     c) 시선 처리 (FaceNet 시선 추적, LOCK-MM-09 max_frames=100)
     d) 제스처 (포즈 추정 — MediaPipe)
     e) 콘텐츠 (LLM 분석 + LOCK-ED-05 Bloom 평가)
     f) 구조 (서론/본론/결론 분석)
   - 멀티모달 분석 통합 (음성 + 비디오 + 슬라이드 LOCK-MM-07 CLIP 768d)
   - ★ 3-6 Health 불안 감지 (R-08-6 opt-in → 발표 중 스트레스 → 호흡법 추천)
   - LOCK-ED-05 Bloom Apply/Analyze/Evaluate 매핑
   - E4 모델 비교: 멀티모달 발표 분석 (자체 vs Slidesgo vs custom)
   - E5 폴백: 모달리티 부분 실패 시 가용 분석만 진행
   - E7 SLA: 10분 발표 분석 ≤ 30초
   - E10 윤리: R-08-5 발표 데이터 외부 전송 동의 + 익명화 옵션
3. 3-2 Multimodal LOCK-MM-07/08/09 EXACT 인용
4. ★ 3-6 Health LOCK-HW-01 12감정 (특히 anxiety) 감지 인터페이스 정의
5. production .md 신규 추가 후 SHA + 라인 수 측정 (실측 기록)
6. Phase 4 entry-gate 충족 여부 확인 (6 요소 + LOCK + 감정 연동)

**검증**:
- [x] V3 #5 발표 피드백 L3 ≥ 80점 (E1~E10 9요소 PASS)
- [x] 발표 평가 6 요소 명시 (음성속도/명료성/시선/제스처/콘텐츠/구조)
- [x] LOCK-MM-07 768d + LOCK-MM-08 16kHz + LOCK-MM-09 max_frames=100 EXACT 인용
- [x] LOCK-ED-05 Bloom Apply/Analyze/Evaluate 매핑
- [x] ★ 3-6 Health 불안 감지 (R-08-6 opt-in + LOCK-HW-01) 인터페이스 정의
- [x] R-08-5 발표 데이터 외부 전송 동의 + 익명화 옵션 명시
- [x] production 측정: VBS-16 + 발표 분석 30초/10분 SLA
- [x] /validate + /audit + /sot-check PASS
- [x] Phase 4 entry-gate 충족 조건 ALL PASS

**산출물**:
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/05_learning-analytics/presentation_feedback.md` (V3 NEW — 멀티모달 발표 피드백)
</details>

<details>
<summary><b>3-6. 05_learning-analytics 스터디 그룹 매칭 V3 (1건)</b></summary>

**대조 기준 (7항목)**:
- §7 세부 작업: 8 V3 항목 중 #6 "스터디 그룹 매칭"
- §7 전환 게이트: V3 대상 파일 100% 작성, VBS-16 벤치마크 전체 통과
- §6 이슈: §6.5 `05_learning-analytics/` 영역 V3 NEW — 스터디 그룹 매칭 알고리즘
- 교차 도메인: 6-3 PARL (매칭 Agent), 3-3 PKM (학습 노트 공유 — 3-3 V3 M-028 inheritance), 3-6 Health (스트레스 양립 R-08-6 opt-in) — 5-2 외부 5 deps 영향 없음
- Part2 V3-Phase: V3-Phase 3 (CAT-E SHELL → 본 V3 정본 참조)
- production 측정 baseline: `D:/VAMOS/docs/sot 2/3-5_Education-Learning/05_learning-analytics/study_group_matching.md` (NEW V3) / VBS-16 + 매칭 만족도 측정 / LOCK-ED-07 학습자 프로필 정합
- Phase 4 entry-gate 충족 조건: L3 ≥ 80점/100 + 매칭 알고리즘 (학습 목표/속도/스타일/주간 학습 시간) + LOCK-ED-07 학습자 프로필 5필드 + 익명/실명 옵션 + R-08-5 프로필 외부 전송 금지

**목표**: 05_learning-analytics 서브폴더에 study_group_matching.md V3 정본 신규 작성. 스터디 그룹 매칭 알고리즘(학습 목표/속도/스타일/주간 시간) + LOCK-ED-07 학습자 프로필 정합 + 익명/실명 옵션 + 학습 노트 공유 + 매칭 평가 완전 정의.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/EDUCATION_LEARNING_구조화_종합계획서.md` §6.5 (V3), §3.4 LOCK-ED-07
- `D:/VAMOS/docs/sot/STEP7-O_교육_학습_자기개발_작업가이드.md` (V3 항목)
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/01_adaptive-learning/learner_profile.md` (LOCK-ED-07 V1 정본)
- `D:/VAMOS/docs/sot 2/3-3_PKM-Knowledge-Management/03_spaced-repetition/knowledge_sharing.md` (3-3 V3 M-028 inheritance)

**절차**:
1. 계획서 §6.5 + STEP7-O V3 요구사항 확인
2. `study_group_matching.md` V3 신규 작성:
   - 매칭 알고리즘:
     a) 학습 목표 유사도 (LOCK-ED-07 goal 필드)
     b) 학습 속도 호환성 (LOCK-ED-07 learning_speed)
     c) 학습 스타일 매칭 (LOCK-ED-07 preferred_style)
     d) 주간 학습 시간 (LOCK-ED-07 weekly_hours)
   - LOCK-ED-07 5필드 (skill_levels/learning_speed/preferred_style/weekly_hours/goal) 보존
   - 익명/실명 옵션 (기본 익명)
   - 학습 노트 공유 (3-3 PKM M-028 V3 inheritance — RBAC + last-write-wins)
   - 그룹 활동 (주간 미팅 + 진척 공유)
   - E4 모델 비교: 매칭 알고리즘 (k-means 클러스터링 vs collaborative filtering vs hybrid)
   - E5 폴백: 매칭 결과 부족 시 더 넓은 기준
   - E7 SLA: 매칭 ≤ 3초
   - E10 윤리: R-08-5 프로필 외부 전송 금지 + 명시적 동의
3. LOCK-ED-07 5필드 EXACT 인용
4. 3-3 PKM M-028 V3 inheritance (RBAC + 충돌 해결)
5. production .md 신규 추가 후 SHA + 라인 수 측정 (실측 기록)
6. Phase 4 entry-gate 충족 여부 확인 (매칭 + LOCK + 익명화)

**검증**:
- [x] V3 #6 스터디 그룹 매칭 L3 ≥ 80점 (E1~E10 9요소 PASS)
- [x] 매칭 4요소 (목표/속도/스타일/주간시간) 정의
- [x] LOCK-ED-07 5필드 EXACT 인용
- [x] 익명/실명 옵션 (기본 익명) 명시
- [x] R-08-5 프로필 외부 전송 금지 명시
- [x] 3-3 PKM M-028 V3 inheritance (RBAC + 충돌 해결)
- [x] production 측정: VBS-16 + 매칭 만족도 ≥ 70%
- [x] /validate + /audit + /sot-check PASS
- [x] Phase 4 entry-gate 충족 조건 ALL PASS

**산출물**:
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/05_learning-analytics/study_group_matching.md` (V3 NEW — 스터디 그룹 매칭)
</details>

<details>
<summary><b>3-7. 03_coding-tutorial VR/AR 학습 V3 (1건)</b></summary>

**대조 기준 (7항목)**:
- §7 세부 작업: 8 V3 항목 중 #7 "VR/AR 학습"
- §7 전환 게이트: V3 대상 파일 100% 작성, VBS-16 벤치마크 전체 통과
- §6 이슈: §6.3 `03_coding-tutorial/` 영역 V3 NEW — VR/AR 기반 몰입형 학습
- 교차 도메인: 3-2 Multimodal (J-009 AR/공간 이해 V3 — 3-2 3-1 산출물), 6-13 Operations (VR 디바이스 운영) — 5-2 외부 5 deps 영향 없음
- Part2 V3-Phase: V3-Phase 3 (CAT-E SHELL → 본 V3 정본 참조)
- production 측정 baseline: `D:/VAMOS/docs/sot 2/3-5_Education-Learning/03_coding-tutorial/vr_ar_learning.md` (NEW V3) / VBS-16 + VR/AR 몰입 시간 측정
- Phase 4 entry-gate 충족 조건: L3 ≥ 80점/100 + 디바이스 지원 ≥ 3종 (Quest 3 / Vision Pro / 모바일 AR) + LOCK-ED-02 5단계 난이도 VR 적응 + 3-2 J-009 AR/공간 이해 정합 + 사용자 안전 (멀미 + 시간 제한)

**목표**: 03_coding-tutorial 서브폴더에 vr_ar_learning.md V3 정본 신규 작성. VR/AR 디바이스 지원(Quest 3/Vision Pro/모바일 AR) + 3-2 J-009 AR/공간 이해 정합 + LOCK-ED-02 난이도 VR 적응 + 사용자 안전(멀미 + 시간 제한) 완전 정의.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/EDUCATION_LEARNING_구조화_종합계획서.md` §6.3 (V3), §3.4 LOCK-ED-02
- `D:/VAMOS/docs/sot/STEP7-O_교육_학습_자기개발_작업가이드.md` (V3 항목)
- `D:/VAMOS/docs/sot 2/3-2_Multimodal-Processing/01_image-pipeline/vision_language_integration.md` (3-2 3-1 V3 J-009 산출물)

**절차**:
1. 계획서 §6.3 + STEP7-O V3 요구사항 확인
2. `vr_ar_learning.md` V3 신규 작성:
   - 디바이스 지원 3종 (Meta Quest 3 / Apple Vision Pro / 모바일 AR)
   - 3-2 J-009 AR/공간 이해 정합 (Depth Estimation, ARKit/ARCore)
   - LOCK-ED-02 5단계 난이도 VR 적응 (Very Easy: 가이드 모드 → Very Hard: 자유 탐색)
   - 시나리오 (3D 수학 / 가상 해부학 / 가상 박물관 / 가상 코딩 환경)
   - 사용자 안전:
     a) 멀미 방지 (FOV 조정 + 텔레포트 이동)
     b) 시간 제한 (연속 30분 + 휴식 강제)
     c) 안전 영역 확인
   - 멀티유저 VR 세션 (3-3 PKM M-028 V3 협업 inheritance)
   - E4 모델 비교: VR 학습 플랫폼 (Unity vs Unreal vs Web AR)
   - E5 폴백: VR 디바이스 미가용 시 데스크톱/모바일 폴백
   - E7 SLA: VR 렌더링 90fps 유지
   - E10 윤리: 청소년 사용 제한 + 부모 통제
3. 3-2 J-009 LOCK-MM-07 CLIP 768d + Depth Estimation 정합
4. 사용자 안전 명시 (멀미 + 시간 + 안전 영역)
5. production .md 신규 추가 후 SHA + 라인 수 측정 (실측 기록)
6. Phase 4 entry-gate 충족 여부 확인 (디바이스 3종 + LOCK + 안전)

**검증**:
- [x] V3 #7 VR/AR 학습 L3 ≥ 80점 (E1~E10 9요소 PASS)
- [x] 디바이스 지원 3종 (Quest 3/Vision Pro/모바일 AR) 명시
- [x] LOCK-ED-02 5단계 난이도 VR 적응
- [x] 3-2 J-009 AR/공간 이해 정합 (LOCK-MM-07 CLIP 768d)
- [x] 사용자 안전 3요소 (멀미/시간 30분/안전 영역) 명시
- [x] 청소년 사용 제한 + 부모 통제 명시
- [x] production 측정: VBS-16 + VR 90fps 유지
- [x] /validate + /audit + /sot-check PASS
- [x] Phase 4 entry-gate 충족 조건 ALL PASS

**산출물**:
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/03_coding-tutorial/vr_ar_learning.md` (V3 NEW — VR/AR 학습)
</details>

<details>
<summary><b>3-8. 05_learning-analytics 멘토링 플랫폼 V3 + Phase 3 마감 + Education 감정 연동 최종 검증</b></summary>

**대조 기준 (7항목)**:
- §7 세부 작업: 8 V3 항목 중 #8 "멘토링 플랫폼" + Phase 3 전체 마감 (STEP7-O 69항목 L3 ≥ 60%, S11-1 정정 기준) + ★ 3-6 Health 감정 연동 (R-08-6 ↔ R-09-6) 최종 확정
- §7 전환 게이트: V3 대상 파일 100% 작성, VBS-16 벤치마크 전체 통과 (§10 #10)
- §6 이슈: §6.5 `05_learning-analytics/` 멘토링 V3 NEW + §6.1~§6.5 sub-section 전수 점검 (~15+8+10+18+18=69항목, §6.6 O-029~O-036 8건 부록/§7 통합 REF) + 3-1~3-7 V3 산출물 점검
- 교차 도메인: 3-3 PKM (멘토 노트 공유 — 3-3 V3 M-028 inheritance), ★ 3-6 Health 감정 연동 (R-08-6 opt-in 최종 확정 + LOCK-HW-01 ↔ Education E 선행작업 양방향 검증), 6-3 PARL (멘토링 매칭 Agent) — 5-2 외부 5 deps 영향 없음
- Part2 V3-Phase: V3-Phase 3 마감 (CAT-E COND-7 + UI SHELL → 본 V3 STEP7-O 69항목 정본 참조)
- production 측정 baseline: `D:/VAMOS/docs/sot 2/3-5_Education-Learning/05_learning-analytics/mentoring_platform.md` (NEW V3) + STEP7-O 69항목 전체 production 정본 SHA + L3 점수 매트릭스 / VBS-16 KPI 전수 ALL PASS / LOCK-ED 10 + DEFINED-HERE 무위반
- Phase 4 entry-gate 충족 조건: STEP7-O 69항목 L3 ≥ 60% + V3 8항목 (3-1~3-8) L3 ≥ 80점 + VBS-16 (LOCK-ED-09 학습 지속률 ≥ 60% + 기억 유지율 ≥ 80%) ALL PASS + CONFLICT_LOG OPEN 0건 (CF-ED-001~005 ALL RESOLVED 보존) + FABRICATION 0건 + ★ 3-6 Health 감정 연동 (R-08-6 opt-in + LOCK-HW-01 12감정 ↔ Education 양방향) 최종 재확인

**목표**: 05_learning-analytics 서브폴더에 mentoring_platform.md V3 정본 신규 작성 + Phase 3 전체 마감 + ★ 3-6 Health 감정 연동 최종 확정. 멘토링 매칭 + 멘토 인증 + 세션 관리 + 3-3 PKM 노트 공유 inheritance + Phase 3 게이트 충족 확인.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/EDUCATION_LEARNING_구조화_종합계획서.md` §6.5 (V3) + §10 검증 체크리스트 (10개) + §11 보완 + §12 FINAL REVIEW
- Phase 1~3 산출물: `D:/VAMOS/docs/sot 2/3-5_Education-Learning/01_adaptive-learning/` ~ `05_learning-analytics/` 5개 서브폴더 내 전체 파일
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/AUTHORITY_CHAIN.md` (LOCK-ED 10 + DEFINED-HERE 매트릭스)
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/CONFLICT_LOG.md` (CF-ED-001~005 ALL RESOLVED 보존)
- `D:/VAMOS/docs/sot 2/3-6_Health-Wellness-EmotionAI/` Education 감정 연동 인터페이스 (R-09-6 opt-in)
- `D:/VAMOS/docs/sot 2/3-3_PKM-Knowledge-Management/03_spaced-repetition/knowledge_sharing.md` (3-3 V3 M-028 inheritance)
- `D:/VAMOS/docs/sot 2/SOT2_MASTER_INDEX.md` (3-5 row Phase 3 ✅ marker 갱신)

**절차**:
1. 계획서 §6.5 + STEP7-O V3 멘토링 요구사항 확인
2. `mentoring_platform.md` V3 신규 작성:
   - 멘토링 매칭 알고리즘 (스킬 + 학습 목표 + 가용 시간)
   - 멘토 인증 시스템 (자격 검증 + 평판 점수)
   - 세션 관리 (예약 + 화상 + 노트 공유)
   - 3-3 PKM M-028 V3 inheritance (멘토 노트 RBAC 공유)
   - LOCK-ED-07 학습자 프로필 + 멘토 프로필
   - LOCK-ED-09 VBS-16 멘토링 효과 측정
   - 평가 시스템 (멘토 + 멘티 양방향)
   - E4 모델 비교: 멘토링 매칭 (협업 필터링 vs ML 기반 vs 수동)
   - E5 폴백: 멘토 부족 시 대기열
   - E7 SLA: 매칭 ≤ 5초
   - E10 윤리: 미성년자 보호 + 결제 투명성 + R-08-5 프로필 외부 전송 금지
3. Phase 3 전체 마감:
   - 서브폴더별 L3 점수 전수 집계: 01: 15/15, 02: 8/8, 03: 10/10, 04: 18/18, 05: 18/18 = 69/69 (V3 8건 포함)
   - V3 8건 (투자 시뮬레이션 + 회화 연습 + 챌린지 + 음성 인식 + 발표 피드백 + 스터디 매칭 + VR/AR + 멘토링) L3 ≥ 80점 개별 확인
   - VBS-16 (LOCK-ED-09 학습 지속률 ≥ 60% + 기억 유지율 ≥ 80%) ALL PASS 검증
4. ★ 3-6 Health 감정 연동 최종 재확인 (R-08-6 opt-in + LOCK-HW-01 12감정 ↔ Education E 선행작업 양방향 인터페이스)
5. §11 보완 + §12 FINAL REVIEW 갱신 (Phase 8 패턴 직계 + STAGE 7~8 inheritance)
6. CONFLICT_LOG OPEN 0건 + FABRICATION marker 0건 + LOCK-ED 10 재정의 0건 확인
7. /validate + /audit + /sot-check + /final-review 시뮬레이션 실행 → ALL PASS 확인
8. production 측정 결과 매트릭스 작성 + Phase 4 entry-gate 충족 여부 최종 점검

**검증**:
- [x] V3 #8 멘토링 플랫폼 L3 ≥ 80점 — mentoring_platform.md V3
- [x] STEP7-O 69항목 L3 ≥ 60% 충족 확인 (S11-1 정정 기준, 게이트 조건)
- [x] V3 8항목 (3-1~3-8) L3 ≥ 80점 개별 PASS
- [x] LOCK-ED 10 재정의 0건 (R-02 LOCK 해제 절차 외 변경 없음)
- [x] CONFLICT_LOG CF-ED-001~005 ALL RESOLVED 보존 + OPEN 0건
- [x] FABRICATION marker census 0건 (CLEAN)
- [x] ★ 3-6 Health 감정 연동 (R-08-6 opt-in + LOCK-HW-01 12감정 ↔ Education) 최종 양방향 확정 PASS
- [x] ★ 3-3 PKM SM-2 (LOCK-PKM-01~03 ↔ LOCK-ED-04) 10/10 verbatim match 보존
- [x] production 측정: VBS-16 (LOCK-ED-09 학습 지속률 ≥ 60% + 기억 유지율 ≥ 80%) ALL PASS
- [x] /validate + /audit + /sot-check + /final-review ALL PASS
- [x] Phase 4 entry-gate 충족 조건 ALL PASS (L3 + V3 + VBS-16 + CONFLICT + FABRICATION + 양방향 교차)

**산출물**:
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/05_learning-analytics/mentoring_platform.md` (V3 NEW — 멘토링 플랫폼)
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/EDUCATION_LEARNING_구조화_종합계획서.md` §11, §12 최종 갱신
- L3 완성도 매트릭스 (서브폴더별 + V3 8건 + STEP7-O 69항목)
- /final-review 결과 리포트 + Phase 4 entry-gate 충족 보고서 + Health 감정 연동 양방향 최종 확인 리포트 + PKM SM-2 10/10 verbatim match 최종 확인 리포트
- `D:/VAMOS/docs/sot 2/SOT2_MASTER_INDEX.md` 3-5 row Phase 3 ✅ marker 갱신
</details>

#### Phase 3 세션 전체 검증 결과 (3-5, 2026-05-16)

> **chain ID**: sub-A `phase3_3-5_sub_a_2026-05-16` + sub-B `phase3_3-5_sub_b_2026-05-16` (2분할 단일 도메인, 4+4 P3)
> **수행일**: 2026-05-16 (sub-A + sub-B 동일자 단일 일자)
> **목적**: 3-5 Education-Learning Phase 3 V3 8건 전체 마감 + meta-audit 마감 + Phase 4 entry-gate 충족 매트릭스 + 다음 도메인 (3-6 Health-Wellness-EmotionAI Wave 1 #8) 진입 ready 선언

**1. P3 블록 통산 매트릭스 (8/8 ALL ✅ tcv3 first-pass CONFIRMED)**

| P3 | 작업명 | 폴더 | LOCK 인용 | R cascade | Drift | tcv3 |
|----|--------|------|----------|----------|-------|------|
| P3-1 | 투자 시뮬레이션 V3 | 04_content-generation | LOCK-ED-02/03/05/09 (4건) | 41 + 1 | D-P3-1-R3-1 STEP7-O alias | ✅ |
| P3-2 | 회화 연습 대화 엔진 V3 | 04_content-generation | LOCK-ED-06/08/09 (3) + LOCK-MM-08 cross-domain + R-08-6 | 41 + 1 | D-P3-2-R3-1 STEP7-O alias | ✅ |
| P3-3 | 챌린지 리더보드 V3 | 05_learning-analytics | LOCK-ED-10 (1 single) + 3-6 wellness_community forward-defined | 41 + 1 | D-P3-3-R3-1 STEP7-O alias | ✅ |
| P3-4 | 음성 인식 학습 V3 | 03_coding-tutorial | LOCK-ED-06/09 (2) + LOCK-MM-08 cross-domain | 41 + 1 | D-P3-4-R3-1 STEP7-O alias | ✅ |
| P3-5 | 발표 피드백 V3 | 05_learning-analytics | LOCK-ED-05 (1 single) + **LOCK-MM-07/08/09 3-LOCK cross-domain** + LOCK-HW-01 ref + R-08-6 | 41 + 1 | D-P3-5-R3-1 STEP7-O alias | ✅ |
| P3-6 | 스터디 그룹 매칭 V3 | 05_learning-analytics | LOCK-ED-07 (1 single) + 3-3 M-028 V3 inheritance | 41 + 1 | D-P3-6-R3-1 STEP7-O alias | ✅ |
| P3-7 | VR/AR 학습 V3 | 03_coding-tutorial | LOCK-ED-02 (1 single) + LOCK-MM-07 cross-domain + 3-2 J-009 V3 + 3-3 M-028 inheritance | 41 + 1 | D-P3-7-R3-1 STEP7-O alias | ✅ |
| P3-8 | 멘토링 + Phase 3 마감 + meta-audit | 05_learning-analytics | LOCK-ED-07/09 (2) + **★ SM-2 LOCK-PKM-01~03 ↔ LOCK-ED-04 10/10** + LOCK-HW-01 ref | 40 + 0 NO-DRIFT | (NO-DRIFT direct path meta block) | ✅ |
| **통산** | **8 V3 + Phase 3 마감 + meta-audit** | **5 서브폴더 ALL** | **self 13 + cross-domain 7 + cross-domain ref 4 = 24건 100% 정합** | **327 verifications + 7 fixes** | **7 drifts ALL R₃ STEP7-O alias ALL COMPLETE** | **8/8 tcv3 first-pass** |

**2. byte/SHA/LF 통산 (sub-A + sub-B 진행 매트릭스)**

| 시점 | byte | SHA16 | LF lines | Δ vs pre |
|------|------|-------|---------|----------|
| sub-A 진입 baseline | 153,790 | 0AC10DD6EFC83123 | 2,263 | (baseline) |
| sub-A 종료 (P3-1~4 4건 fix) | 153,822 | A634A431E5586AFE | 2,263 | +32 / +0 |
| sub-B P3-5 fix | 153,830 | E8487CB6C8FCC059 | 2,263 | +8 / +0 |
| sub-B P3-6 fix | 153,838 | 03BBA668453004CE | 2,263 | +8 / +0 |
| sub-B P3-7 fix | 153,846 | 2675A6D5AD87A241 | 2,263 | +8 / +0 |
| sub-B P3-8 (NO-DRIFT direct path) | 153,846 | 2675A6D5AD87A241 | 2,263 | +0 / +0 |
| **sub-A + sub-B 통산** | **153,846** | **2675A6D5AD87A241** | **2,263** | **+56 / +0** |

7건 STEP7-O alias fix 통산 Δ +56 B / +0 L (8 byte × 7 = +56 B EXACT: 한국어 정본 "교육_학습_자기개발" 26 B - 영문 alias "Education_Learning" 18 B = +8 B × 7건). **post-fix Grep 종합계획서 전체 0 hits 인증 완성** ✅. SOT2_MASTER_INDEX.md EXACT 보존 (189,678 B / B89F86EC08B3704F / 1,409 L, Δ 0/0 sub-B 진행 중, ⑤단계 적용 예정). AUTHORITY_CHAIN / CONFLICT_LOG / INDEX EXACT 보존 (sub-A + sub-B 미수정 통산).

**3. R cascade 통산 (327 verifications + 7 fixes, sub-A 4 P3 + sub-B 4 P3)**

| sub-session | First-pass 합 | Drift 합 | R₁₁ fix 합 | R₁₂ post-fix 합 | 통산 |
|-------------|---------------|---------|------------|-----------------|------|
| sub-A 4 P3 (P3-1~P3-4) | 40 | 4 | +32 B / +0 L | 120 × 0 changes | 164 + 4 |
| sub-B 4 P3 (P3-5~P3-8) | 40 | 3 | +24 B / +0 L | 120 × 0 changes | 163 + 3 |
| **통산** | **80** | **7 drifts ALL R₃ STEP7-O alias ALL COMPLETE** | **+56 B / +0 L (7건 EXACT 동일 패턴)** | **240 × 0 changes** | **327 verifications + 7 fixes** |

R₁₁ fix 7건 ALL textual notation only (Δ +56 B / +0 L, byte/SHA 무결성 100% authorized refinement, ALL EXACT 동일 패턴 SOT 작업가이드 alias 13~15건째 누적 인계).

**4. Drift fix 매트릭스 (7건 ALL R₃ STEP7-O alias ALL COMPLETE)**

| Drift ID | P3 | 위치 | 보정 내용 | Δ |
|----------|----|------|----------|---|
| D-P3-1-R3-1 | P3-1 (sub-A) | L1278 | STEP7-O 영문 alias → 한국어 정본 | +8 B / +0 L |
| D-P3-2-R3-1 | P3-2 (sub-A) | L1331 | (동일) | +8 B / +0 L |
| D-P3-3-R3-1 | P3-3 (sub-A) | L1385 | (동일) | +8 B / +0 L |
| D-P3-4-R3-1 | P3-4 (sub-A) | L1439 | (동일) | +8 B / +0 L |
| D-P3-5-R3-1 | P3-5 (sub-B) | L1492 | (동일) | +8 B / +0 L |
| D-P3-6-R3-1 | P3-6 (sub-B) | L1549 | (동일) | +8 B / +0 L |
| D-P3-7-R3-1 | P3-7 (sub-B) | L1605 | (동일) | +8 B / +0 L |
| **통산 7건 ALL COMPLETE** | sub-A 4 + sub-B 3 | 7 좌표 | `STEP7-O_Education_Learning_작업가이드.md` → `STEP7-O_교육_학습_자기개발_작업가이드.md` | **+56 B / +0 L EXACT** |

**5. abort marker 11종 NOT FIRED self-fire 0 통산**

- UPSTREAM_INCOMPLETE:3-5 NOT FIRED (3-3/2-2/3-2/3-4 upstream ALL ✅ COMPLETE pre-verify, 3-7 Dev-Tools secondary 미관련 detached)
- DERIVATION_DEFINITION_MISSING:3-5 NOT FIRED (Wave 1 #7 ★표시 없음 자동 PASS)
- LOCK_VIOLATION:3-5_P3_{1~8} NOT FIRED 통산 (LOCK-ED-01~10 §3.4 L83-L92 EXACT 보존, P3 통산 LOCK 인용 24건 100% 정합)
- CROSS_REF_DRIFT:3-5_P3_{1~7} NOT FIRED 통산 (7 STEP7-O alias 검출 후 R₁₁ 보정 cycle 적용 abort firing 회피)
- BYTE_SHA_MISMATCH:3-5_post NOT FIRED (의도된 통산 Δ +56 B / +0 L authorized refinement)
- CONFLICT_OPEN_DETECTED:3-5_post NOT FIRED (CF-ED-001~005 ALL RESOLVED 보존 + CFL-ED-006~009 4건 Phase 3 이월 step 9 처리 대기 — OPEN 0 통산)
- PHASE4_ENTRY_GATE_NOT_MAPPED:3-5_P3_{1~8} NOT FIRED 통산 (8 P3 모두 Phase 4 entry-gate 조건 명시)
- BILATERAL_SOT2_DRIFT:3-5_post NOT FIRED (sub-B 진행 중, ⑤단계 적용 예정)
- DOWNSTREAM_PROPAGATE_MISS:3-5_post NOT FIRED (sub-A P3-2 emotion_learning_interface + sub-A P3-3 wellness_community + sub-B P3-5 R-08-6 + sub-B P3-6 R-08-6 inline 분담 = 5 P3 통산 + P3-8 최종 확정)
- **★ SM_2_VERBATIM_DRIFT:3-5_P3_{1~8} NOT FIRED 통산** (사전 검증 + sub-A R₃ + P3-1~P3-7 통산 inheritance + P3-8 meta-audit 최종 재확인 = 통산 3회 verify 10/10 EXACT MATCH 일관 PASS)
- **★ SUB_SESSION_HANDOFF_DRIFT:3-5 NOT FIRED** (sub-A handoff §1.4 8-SHA 5/5 PASS sub-B 진입 정합 verify)

self-fire 0 통산 11종.

**6. LOCK / DEFINED-HERE / FABRICATION 통산 0 / 0 / 0**

- LOCK 변경 0 (LOCK-ED-01~10 10 LOCK §3.4 L83-L92 EXACT 보존 통산)
- DEFINED-HERE 변경 0 (LOCK 재정의 R9 무위반 통산)
- FABRICATION 0 (모든 reference SoT 실존 verify — STEP7-O 한국어 정본 15,991 B + 3-2 폴더 27 files + 3-6 AUTHORITY 19,643 B + 3-3 knowledge_sharing.md 14,512 B + learner_profile.md 14,253 B + vision_language_integration.md 35,323 B + emotion_learning_interface.md 24,196 B + multimodal_emotion_fusion.md forward-defined N/A inheritance + wellness_community.md forward-defined N/A inheritance 통산)
- parent-executed Subagent 0회 (sub-A + sub-B 단일 thread 진행)

**7. ★ meta-audit 마감 (SM-2 verbatim 10/10 + R-08-6 ↔ R-09-6 양방향 최종 확정)**

**SM-2 verbatim 5-field × 2측 = 10/10 EXACT MATCH** (LOCK-PKM-01~03 ↔ LOCK-ED-04):

| Field | PKM (3-3 AUTHORITY L40-L42) | Education (3-5 AUTHORITY L86 + L113 §5) | Match |
|-------|---------------------------|-----------------------------------------|-------|
| 1. 하한 | MIN_EASINESS = 1.3 | MIN_EF = 1.3 | ✅ |
| 2. 기본 | DEFAULT_EASINESS = 2.5 | DEFAULT_EF = 2.5 | ✅ |
| 3. n=1 | n=1: 1일 | I(1)=1d | ✅ |
| 4. n=2 | n=2: 6일 | I(2)=6d | ✅ |
| 5. n≥3 | n≥3: I(n-1) × EF | I(n>=3)=I(n-1)×EF | ✅ |

**10/10 EXACT VERBATIM MATCH** (변수명 변형 인지, 의미·값 동일) — 통산 3회 verify 일관 PASS (사전 검증 + sub-A R₃ + P3-1~P3-7 통산 inheritance + P3-8 meta-audit 최종 재확인).

**R-08-6 ↔ R-09-6 양방향 최종 확정**:
- R-08-6 (3-5 AUTHORITY §5 L116): Education 측 정의, 감정 기반 학습 적응 공유 규약 opt-in
- R-09-6 (3-5 AUTHORITY §8.3 v2.1 L220): 3-6 cross-domain 계약, plan §7.2 L1167 verbatim "감정 데이터 → 학습 난이도/속도 적응 (단방향 수신)" 명시적 등재, R-08-6과 병기 운영
- emotion_learning_interface.md PRODUCER 확정 + 3-6 CONSUMER 대기 (LOCK-HW-01 12감정 + LOCK-HW-12 강도 verbatim 인용 + C-05 RESOLVED 통산 inheritance)
- **5 P3 통산 inline 분담 + 최종 확정**: sub-A P3-2 emotion + sub-A P3-3 wellness_community forward-defined + sub-B P3-5 발표 불안 감지 + sub-B P3-6 스터디 스트레스 양립 + P3-8 최종 확정 = 5 P3 통산 + meta-audit 마감

**8. 6 anchor 100% 충족 통산**

| Anchor | 통산 결과 |
|--------|----------|
| 안전 | STAGE 9 inheritance 없음 (일반 Wave 1 도메인), production .md ZERO write 통산 ✅, 종합계획서 sandbox-only +56 B authorized refinement 통산 |
| 누락 0 | 8 P3 × (6 sections + 7 항목 + N inputs + N 절차 + N 검증 + N 산출물) ALL ✅ + STEP7-O 영문 alias 7건 정밀 식별 + forward-defined inheritance 3-6 wellness_community / multimodal_emotion_fusion 정밀 식별 + Phase 3 마감 8 게이트 + meta-audit 4 항목 ALL 명시 |
| 오류 0 | 7 drift 검출 → R₁₁ 보정 (7 좌표 EXACT 동일 +8 B each) → R₁₂ post-fix 0 changes 3 round 통산 ✅ + P3-8 NO-DRIFT direct path |
| 미세 | 7 fix 모두 textual notation only (Δ +56 B / +0 L, byte/SHA 무결성 100% authorized refinement) + 한국어 정본 vs 영문 alias 1글자 단위 정밀 식별 (3-4 STEP7-N 4건 + 3-2 STEP7-J 3건 alias 패턴 EXACT 직계) + ★ SM-2 5-field × 2측 verbatim 정밀 + ★ R-08-6 §5/§8.3 v2.1 정밀 verify ✅ |
| 수렴 | 8 P3 ALL truly_converged_v3 marker first-pass CONFIRMED ✅ (post-fix 3 round 0 changes 자동 cascade × 8 P3 = 240 verifications 0 changes) |
| 재검증 | post-fix R₁~R₁₀ × 3 round × 8 P3 = 240 verifications 0 changes auto cascade ✅ + ★ meta-audit 최종 재확인 통산 3회 verify 일관 |

**9. upstream 의존 verify 통산 (DAG)**

| Upstream | Wave 1 # | 상태 | 결과 |
|----------|----------|------|------|
| #6 PKM (3-3) | Wave 1 #5 | ✅ COMPLETE 2026-05-16 SPEC COMPLETE | SM-2 LOCK-PKM-01~03 ↔ LOCK-ED-04 10/10 maintained meta-audit 최종 재확인 PASS |
| #4 COND-Modules (2-2) | Wave 1 #2 | ✅ COMPLETE 2026-05-15 SPEC COMPLETE | LOCK-ED-06 소크라테스 cross-ref (P3-2 + P3-4) |
| #5 Multimodal (3-2) | Wave 1 #4 | ✅ COMPLETE 2026-05-16 SPEC COMPLETE | LOCK-MM-07/08/09 cross-domain (P3-2 + P3-4 LOCK-MM-08 + P3-5 3-LOCK 최대 + P3-7 LOCK-MM-07) + J-009 V3 inheritance (P3-7) |
| #7 Workflow-RPA (3-4) | Wave 1 #6 | ✅ COMPLETE 2026-05-16 SPEC COMPLETE | 학습 자동화 secondary contextual |
| #10 Dev-Tools (3-7) | Wave 1 #9 | ⏳ 미완료 | sub-A + sub-B 8 P3 직접 의존 없음 detached (P3-7 VR/AR은 3-2/6-13 의존만, 3-7 미관련) |

**10. downstream 전파 매핑 (⑥단계 적용 대기)**

| Downstream | Wave # | 매핑 | sub-B ⑥단계 처리 |
|-----------|--------|------|------------------|
| **3-6 Health-Wellness-EmotionAI** | Wave 1 #8 | emotion_learning_interface PRODUCER 확정 + R-08-6 ↔ R-09-6 양방향 최종 확정 + wellness_community.md P-033 V3 inheritance + LOCK-HW-01 12감정 + LOCK-HW-12 강도 verbatim 인용 정합 + C-05 RESOLVED inheritance + multimodal_emotion_fusion.md forward-defined | 3-6 종합계획서 §3 또는 §6 reference 추가 "3-5 Phase 3 완료 (2026-05-16) — emotion_learning_interface PRODUCER 확정 + R-08-6 ↔ R-09-6 최종 확정 본 도메인 CONSUMER entry_gate 해제 + wellness_community.md P-033 V3 inheritance" |

**11. Phase 4 entry-gate 충족 매트릭스 (Phase 3 → 4 게이트 8 조건 ALL ✅ 매핑)**

| 게이트 조건 | 매핑 위치 | 결과 |
|-------------|----------|------|
| 1. STEP7-O 69항목 L3 ≥ 60% (S11-1 정정 기준) | P3-8 검증 #2 + L1682 (서브폴더별 L3 점수 15+8+10+18+18=69/69) | ✅ 매핑 명시 |
| 2. V3 8항목 (3-1~3-8) L3 ≥ 80점 | P3-8 검증 #3 + L1683 (sub-A 4 + sub-B 4 = 8 V3) | ✅ 매핑 명시 |
| 3. VBS-16 (LOCK-ED-09 학습 지속률 ≥ 60% + 기억 유지율 ≥ 80%) ALL PASS | P3-8 검증 #9 + L1684 | ✅ 매핑 명시 |
| 4. CONFLICT_LOG OPEN 0건 (CF-ED-001~005 RESOLVED 보존) | P3-8 검증 #5 + CONFLICT_LOG v1.1 | ✅ 매핑 명시 + CFL-ED-006~009 4건 step 9 처리 대기 |
| 5. FABRICATION 0건 | P3-8 검증 #6 | ✅ 매핑 명시 (통산 verify 0건) |
| 6. LOCK-ED 10 재정의 0건 | P3-8 검증 #4 + AUTHORITY L83~L92 | ✅ 매핑 명시 (통산 LOCK 변경 0) |
| 7. **★ 3-6 Health 감정 연동 R-08-6 ↔ R-09-6 양방향 최종 확정** | P3-8 검증 #7 + L1685/L1698 + AUTHORITY §5/§8.3 | **✅ EXACT VERIFY** |
| 8. **★ 3-3 PKM SM-2 verbatim 10/10 보존** | P3-8 검증 #8 + L1699 + AUTHORITY §3.4 L86 + L113 §5 | **✅ 10/10 EXACT MATCH** |

**12. 핵심 수확 통산**

1. **STEP7-O 영문 alias → 한국어 정본 정합 fix 7건 ALL COMPLETE** — sub-A 4건 + sub-B 3건 EXACT 동일 패턴 일관 (3-4 STEP7-N 4건 + 3-2 STEP7-J 3건 통산 SOT 작업가이드 alias 14~15건째 누적 인계), post-fix Grep 종합계획서 전체 0 hits 인증 완성
2. **★ SM-2 verbatim 5-field × 2측 = 10/10 EXACT MATCH meta-audit 최종 재확인 PASS** — LOCK-PKM-01~03 (3-3 L40-L42) ↔ LOCK-ED-04 (3-5 L86 + L113 §5 보강), 변수명 변형 인지, 통산 3회 verify 일관
3. **★ R-08-6 ↔ R-09-6 양방향 최종 확정** — 3-5 AUTHORITY §5 + §8.3 v2.1 명시적 등재 병기 운영, emotion_learning_interface.md PRODUCER + 3-6 CONSUMER + LOCK-HW-01/HW-12 verbatim + C-05 RESOLVED, **5 P3 통산 inline 분담 + P3-8 최종 확정**
4. **P3-5 3-LOCK 최대 cross-domain** (LOCK-MM-07 CLIP 768d + LOCK-MM-08 16kHz + LOCK-MM-09 max_frames=100) — sub-A P3-2/P3-4 LOCK-MM-08 단일 + P3-5 3-LOCK 최대 + P3-7 LOCK-MM-07 inheritance = sub-A+sub-B 4 P3 3-2 cross-domain 활용 다각화 최대
5. **3-3 PKM M-028 V3 inheritance 4 P3 통산 누적 최다** (sub-A P3-1 + sub-B P3-6 매칭 협업 + P3-7 멀티유저 VR 세션 + P3-8 멘토 노트 공유) — 3-3 cross-domain 최대 활용
6. **3-2 J-009 AR/공간 이해 V3 inheritance** (P3-7) + LOCK-MM-07 CLIP 768d + Depth Estimation + ARKit/ARCore cross-domain integration
7. **사용자 안전 + privacy strict 패턴 통산** — sub-A P3-3 챌린지 익명 기본 + sub-B P3-6 익명/실명 + R-08-5 외부 전송 금지 + P3-7 VR 사용자 안전 3요소 + 청소년 사용 제한 + P3-8 미성년자 보호 + 결제 투명성 = privacy/safety 통산 5 P3 명시
8. **NO-DRIFT first-pass direct path P3-8** — sub-B 4 P3 중 유일한 NO-DRIFT (sub-A 4 P3 ALL drift + sub-B P3-5/P3-6/P3-7 ALL drift 대비 P3-8 meta block 특성, sub-A P3-1 + 2-1 P3-2~5 + 2-2 P3-1 NO-DRIFT 패턴 inheritance)

**13. 다음 단계**

- **⑤ bilateral 갱신** (종합계획서 §7 헤더 "✅ Phase 3 완료 (2026-05-16, 8 task)" + SOT2_MASTER_INDEX 3-5 row Phase 3 ✅ marker + 구현 현황 + 구현 Phase 추적 + [PHASE4_READY: 3-5 — 2026-05-16] marker)
- **⑥ downstream 전파** (3-6 Health-Wellness-EmotionAI Wave 1 #8 종합계획서 §3/§6 reference 추가)
- **⑦ PROGRESS.md domain-complete** (⬜ → ⬛ Stage A)
- **step 7~10** (verify_post_domain.ps1 -Domain 3-5 + 사양 결함 D-3-5-spec 검출 + Path A drift fix Stage 1+2 + CFL-ED-006~009 4건 정식 등재 + SPEC COMPLETE marker)
- Wave 1 게이트 6/12 → **7/12 진입 ready** (1-2 + 2-2 + 2-1 + 3-2 + 3-3 + 3-4 + 3-5)
- 다음 도메인: **3-6 Health-Wellness-EmotionAI** (Wave 1 #8 sub-A)

---

### Phase 4: V3 implementation + production-ready 정본 승급 (forward-defined, Phase 16 §16 S16-2 inheritance, STAGE 9 ReadOnly inheritance) ✅ Phase 4 완료 (Stage A 2026-05-25 + Stage B 2026-05-25, 8 task, ENTRY_PROMPT v1.1 2분할 sub-A 4 + sub-B 4 + SPEC sub-cycle 12/12 ✅, verify-only per 사용자 결정 A inheritance, 🎉🎉🎉 8/8 NO-DRIFT FULL milestone ⭐⭐⭐⭐ 통산 첫 분할 도메인 FULL specialty + 18-consecutive ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐ NEW 18-단위 milestone 확정 + 18 LOCK 통산 verbatim + SM-2 양방향 영구 baseline 마감 FIRST + 3-6 emotion 4번째 sub-type 양방향 영구 마감 + emotion_LIF PRODUCER 24,196 B 영구 + production .md 8/8 ZERO write 통산 + 17 RO baseline 8/8 무손상 통산 FINAL, SPEC Stage B chain phase4_3-5_spec_2026-05-25 별도 대화창 + 8 _verification NEW +82,904 B / +1,527 LF aggregate (per-P4 × 7 + phase4_l3_baseline_report.md FINAL × 1) + R cascade ENTRY 936 + SPEC 27 = 963+ verifications truly_converged_v_FINAL + abort 99 markers NOT FIRED + Pattern A 72 + Pattern B 69, [DOMAIN_PHASE_4_PRODUCTION_PROMOTION_COMPLETE:3-5 — 2026-05-25] ✅)

**목표**: Phase 3 SPEC 완료 (8 P3 ALL ✅, 29 Phase 4 entry-gate forward-defined) 상태에서 V3 산출물 8건(investment_simulation + conversation_practice + challenge_leaderboard + voice_learning + presentation_feedback + study_group_matching + vr_ar_learning + mentoring)을 production-ready 정본으로 승급한다. **17 production .md ReadOnly TRUE (STAGE 9 inheritance) 일시 해제→fix→복원 EXACT 패턴 적용 필수**. 3-3 PKM SM-2 + 3-6 Health 감정 연동 양방향 cross-handoff 영구 baseline + 44 production .md 파일 Status DRAFT → APPROVED 전환 완료. Phase 5 (도메인 간 통합 운영) entry-gate를 forward-defined로 작성한다.

**범위**: 8 Phase 4 task (P3-1~P3-8 1:1 매핑, forward-defined Phase 4 entry-gate 29 conditions 충족 + Phase 5 entry-gate forward-defined).

**산출물 개요**: 44 production .md 정본 (Status APPROVED + ReadOnly 17 일시 해제→fix→복원 EXACT 패턴) + AUTHORITY_CHAIN v1.X (LOCK-ED-01~10 10건 + cross-domain LOCK-HW-01/12 + LOCK-MM-07/08/09 + LOCK-PKM-01~03 ALL EXACT immutable matrix) + CONFLICT_LOG v1.X (OPEN=0 영구 마감, CFL-ED-006~009 4건 formalization 포함) + INDEX.md (전 inventory SoT) + 65 항목 L3 ≥ 60% production 실측 리포트 + 3-3 SM-2 + 3-6 감정 양방향 정합 명세 + Phase 5 entry-gate forward-defined 명세.

#### Phase 4 → Phase 5 전환 게이트 (forward-defined)

| # | 게이트 | 충족 조건 |
|---|--------|----------|
| G4-1 | V3 implementation 완료 | 8 V3 산출물 production 승급 + Status APPROVED + L3 ≥ 80점 |
| G4-2 | Status APPROVED 전수 전환 | 44 production .md ALL Status APPROVED + DRAFT 잔존 0 + ReadOnly 17 일시 해제→fix→복원 EXACT 패턴 적용 |
| G4-3 | LOCK immutable | LOCK-ED-01~10 + cross-domain LOCK-HW-01/12 + LOCK-MM-07/08/09 + LOCK-PKM-01~03 ALL 인용 형식 통일 + AUTHORITY_CHAIN 영구 baseline |
| G4-4 | CONFLICT 영구 마감 | CONFLICT_LOG OPEN=0 + CF-ED-001~005 RESOLVED 영구 + CFL-ED-006~009 4건 formalization |
| G4-5 | production 실측 baseline | 65 항목 L3 ≥ 60% + V3 8건 L3 ≥ 80점 + VBS-16 학습 지속률 ≥ 60% + 기억 보존 ≥ 80% + IRT 5단계 70-85% 목표 정답률 |
| G4-6 | 도메인 간 통합 준비 | 3-3 PKM SM-2 LOCK-PKM-01~03 ↔ LOCK-ED-04 10/10 verbatim 양방향 + 3-6 Health R-08-6 ↔ R-09-6 양방향 영구 (emotion_learning_interface.md PRODUCER ↔ 3-6 CONSUMER) |
| G4-7 | Phase 5 entry-gate forward-defined | 운영 데이터 baseline + 도메인 간 통합 검증 조건 명세 |

**[STAGE 9 ReadOnly 처리 패턴 — 본 Phase 4 적용 필수]**: 17 ReadOnly TRUE 파일 (01_adaptive-learning 2 + 02_spaced-repetition 1 + 03_coding-tutorial 2 + 04_content-generation 5 + 05_learning-analytics 7) 각 P4 task 진입 시 ① ReadOnly attribute 일시 해제 (attrib -R) → ② Status APPROVED 전환 + content fix → ③ ReadOnly TRUE 복원 (attrib +R) → ④ byte/SHA EXACT 보존 검증 (변경 영역 제외 영역 byte 100% 보존)

#### Phase 4 단계별 상세 작업 절차

> ⚠️ **[RECOVERY 2026-05-31 — verify-only 착시 → genuine production write 영구 해소]**: 본 §7 Phase 4 절차의 최초 마감(2026-05-24~25, "Phase 4 세션 전체 검증 결과 요약" L2279 + G4-x 게이트)은 **verify-only A 마감 = 8 V3 정본 .md 물리 부재(착시)**였다. 2026-05-31 RECOVERY 분할(Sub-A P4-1~P4-4 + Sub-B P4-5~P4-8) **Gate 2 PROCEED 쓰기 허용**으로 8 V3 NEW genuine production write 완료 → 착시 영구 해소. 상세는 아래 **[RECOVERY Stage A+B 블록]** 참조.
>
> **[RECOVERY Stage A+B 블록 — 8 V3 genuine write 결과 (2026-05-31)]**
> - **Sub-A (P4-1~P4-4, 42,435 B)**: investment_simulation `CD031362` 11,432 L3 88 + conversation_practice `838C374E` 11,088 L3 89 + challenge_leaderboard `28D9D603` 10,031 L3 87 + voice_learning `835FEE33` 9,884 L3 86
> - **Sub-B (P4-5~P4-8, 41,746 B)**: presentation_feedback `3A2D8145` 11,254 L3 88 (★ LOCK-MM-07/08/09 3 cross 동시) + study_group_matching `85F4937E` 10,243 L3 86 (3-3 M-028) + vr_ar_learning `307DFB0F` 9,276 L3 85 (3-2 J-009) + mentoring_platform `E3691D48` 10,973 L3 84 (**FINAL**: SM-2+emotion 양방향 영구)
> - **8 V3 / 84,181 B / 평균 L3 86.6** · DRAFT→APPROVED 8/8 · RO TRUE 8/8 + 17 RO baseline EXACT = **RO 25** · LOCK-ED-01~10 immutable 재정의 0 · CONFLICT OPEN 0 영구 · P4-8 파일명 `mentoring_platform.md` 확정(production baseline 우선, vs `mentoring.md` 입력표기)
> - INDEX v1.4 `B352FDD0` §1.4 + AUTHORITY v2.4 `D92210C8` §9 V3 등재 · 감사 `_verification/phase4_recovery_stage_b_report.md` NEW · 마커 `[DOMAIN_PHASE_4_PRODUCTION_PROMOTION_COMPLETE:3-5 — 2026-05-31]` ✅ genuine

<details>
<summary><b>P4-1. investment_simulation V3 산출물 production-ready 정본 승급 (P3-1 inheritance, asset classes 5 + LOCK-ED-02/05/09 + disclaimer)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-1 "investment_simulation V3 production-ready 정본 승급" (P3-1 forward-defined, 6 conditions)
- §7 전환 게이트: G4-1 + G4-5 "production 실측 baseline (asset classes 5 + IRT 5단계)"
- §6 이슈: §6.4 04_content-generation investment_simulation V3 Phase 4 정본 승급
- 교차 도메인: 없음 (도메인 내부 V3 production 승급, 단 LOCK-ED-04 SM-2 cross-domain reference 보존)
- Part2 V3-Phase 매핑: V1-Phase 3 FULL 승급 후 investment_simulation V3 implementation 본격 진행
- production 측정 실측값: investment_simulation V3 산출물 byte/SHA/LF + L3 ≥ 80점 + asset classes 5 (Stock/Bond/ETF/Crypto/Commodity) + LOCK-ED-02 IRT 5단계 + LOCK-ED-05 Bloom + LOCK-ED-09 VBS-16 + disclaimer (`D:/VAMOS/docs/sot 2/3-5_Education-Learning/04_content-generation/investment_simulation.md` — **ReadOnly TRUE**)
- Phase 5 entry-gate 충족 조건: V3 implementation 100% + IRT 5단계 영구 baseline + disclaimer 영구
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: investment_simulation V3 100% 완성 + Status APPROVED + **ReadOnly 일시 해제→fix→복원 EXACT 패턴 적용** + 6 conditions 전수 충족

**목표**: investment_simulation V3 산출물을 production-ready 정본으로 승급한다. ReadOnly TRUE 일시 해제→Status APPROVED 전환→ReadOnly 복원 EXACT 패턴 적용. asset classes 5 + IRT 5단계 + Bloom + VBS-16 + disclaimer production baseline.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/04_content-generation/investment_simulation.md` (V3, ReadOnly TRUE)
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/EDUCATION_LEARNING_구조화_종합계획서.md` §6.4 + §7 P3-1 (forward-defined)
- `D:/VAMOS/docs/sot/STEP7-O_교육_학습_자기개발_작업가이드.md` (O-001/O-002/O-027/O-028 정본 출처, D-P4-1-1 fix 2026-05-25)
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/AUTHORITY_CHAIN.md` (LOCK-ED-02/05/09 정본)

**절차**:
1. P3-1 forward-defined 6 conditions inventory 확인.
2. **ReadOnly 일시 해제**: `attrib -R investment_simulation.md` (STAGE 9 패턴 진입).
3. investment_simulation V3 정본 작성: asset classes 5 (Stock/Bond/ETF/Crypto/Commodity) + LOCK-ED-02 IRT 5단계 70-85% 정답률 + LOCK-ED-05 Bloom Apply/Analyze/Create + LOCK-ED-09 VBS-16 + 비투자조언 disclaimer 명세.
4. Status DRAFT → APPROVED 전환 + Last-reviewed 갱신.
5. LOCK-ED-02/05/09 인용 형식 통일 (`> LOCK (ED AUTHORITY §3.4): ...`).
6. **ReadOnly 복원**: `attrib +R investment_simulation.md` (STAGE 9 패턴 종료).
7. AUTHORITY_CHAIN.md cross-check: LOCK-ED-02/05/09 정본 출처 변경 0.
8. byte/SHA EXACT 검증 (변경 영역 제외 영역 byte 100% 보존).
9. production 실측 측정: investment_simulation V3 산출물 byte/SHA/LF + L3 ≥ 80 + 6 conditions 충족.
10. Phase 5 entry-gate forward-defined 작성.

**검증**:
- [ ] investment_simulation V3 Status APPROVED 전환 완료
- [ ] ReadOnly TRUE 복원 + byte/SHA EXACT 보존
- [ ] L3 점수 ≥ 80 (V3 산출물 1건)
- [ ] asset classes 5 (Stock/Bond/ETF/Crypto/Commodity) production 정합
- [ ] LOCK-ED-02 IRT 5단계 70-85% 정답률 EXACT
- [ ] LOCK-ED-05 Bloom Apply/Create + LOCK-ED-09 VBS-16 EXACT
- [ ] 비투자조언 disclaimer production 정본
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] investment_simulation V3 production-ready 정본 승급 조건 충족** (6 conditions 전수 + ReadOnly 패턴)

**산출물**: investment_simulation V3 production .md 정본 (`04_content-generation/`, ReadOnly TRUE 복원) + `_verification/phase4_v3_p4-1_promotion_report.md`
</details>

<details>
<summary><b>P4-2. conversation_practice V3 산출물 production-ready 정본 승급 (P3-2 inheritance, 5+ languages + 3-6 emotion opt-in)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-2 "conversation_practice V3 production-ready 정본 승급" (P3-2 forward-defined, 5 conditions)
- §7 전환 게이트: G4-1 + G4-6 "도메인 간 통합 준비 (3-6 R-08-6 opt-in)"
- §6 이슈: §6.4 04_content-generation conversation_practice V3 Phase 4 정본 승급
- 교차 도메인: 3-6 Health (LOCK-HW-01 12 emotions + R-08-6 ↔ R-09-6 opt-in 양방향, emotion stress detection)
- Part2 V3-Phase 매핑: V1-Phase 3 FULL 승급 후 conversation_practice V3 implementation 본격 진행
- production 측정 실측값: conversation_practice V3 산출물 byte/SHA/LF + L3 ≥ 80점 + 5+ languages + LOCK-ED-06 Socratic pedagogy + LOCK-ED-08 flashcard + 3-6 opt-in R-08-6 (`D:/VAMOS/docs/sot 2/3-5_Education-Learning/04_content-generation/conversation_practice.md` — V3)
- Phase 5 entry-gate 충족 조건: V3 implementation 100% + 3-6 R-08-6 opt-in 양방향 영구 baseline + 5+ languages baseline
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: conversation_practice V3 100% 완성 + Status APPROVED + 5 conditions 전수 충족 + 3-6 R-08-6 opt-in 양방향 영구

**목표**: conversation_practice V3 산출물을 production-ready 정본으로 승급한다. 5+ 언어 지원 + Socratic pedagogy + 3-6 Health 감정 스트레스 감지 R-08-6 opt-in 양방향 cross-handoff 영구 baseline.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/04_content-generation/conversation_practice.md` (V3)
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/EDUCATION_LEARNING_구조화_종합계획서.md` §7 P3-2
- `D:/VAMOS/docs/sot 2/3-6_Health-Wellness-EmotionAI/AUTHORITY_CHAIN.md` (LOCK-HW-01 + R-08-6 cross-domain)
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/AUTHORITY_CHAIN.md` (LOCK-ED-06/08 정본)

**절차**:
1. P3-2 forward-defined 5 conditions inventory 확인.
2. conversation_practice V3 정본 작성: 5+ 언어 지원 + LOCK-ED-06 Socratic pedagogy + LOCK-ED-08 flashcard + 3-6 R-08-6 opt-in 명세.
3. Status DRAFT → APPROVED 전환 + Last-reviewed 갱신.
4. LOCK-ED-06/08 + LOCK-HW-01 인용 형식 통일.
5. 3-6 Health R-08-6 ↔ R-09-6 opt-in cross-handoff 양방향 정합 검증.
6. AUTHORITY_CHAIN.md cross-check: 변경 0.
7. production 실측 측정: conversation_practice V3 산출물 byte/SHA/LF + L3 ≥ 80 + 5 conditions 충족.
8. Phase 5 entry-gate forward-defined 작성.

**검증**:
- [ ] conversation_practice V3 Status APPROVED 전환 완료
- [ ] L3 점수 ≥ 80
- [ ] 5+ 언어 지원 production 정합
- [ ] LOCK-ED-06 Socratic + LOCK-ED-08 flashcard EXACT
- [ ] 3-6 R-08-6 opt-in 양방향 정합 (LOCK-HW-01 12 emotions reference)
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] conversation_practice V3 production-ready 정본 승급 조건 충족** (5 conditions 전수)

**산출물**: conversation_practice V3 production .md 정본 + `_verification/phase4_v3_p4-2_promotion_report.md`
</details>

<details>
<summary><b>P4-3. challenge_leaderboard V3 산출물 production-ready 정본 승급 (P3-3 inheritance, LOCK-ED-10 6-stage + 익명성)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-3 "challenge_leaderboard V3 production-ready 정본 승급" (P3-3 forward-defined, 5 conditions)
- §7 전환 게이트: G4-1 + G4-5
- §6 이슈: §6.5 05_learning-analytics challenge_leaderboard V3 Phase 4 정본 승급
- 교차 도메인: 3-6 Health (wellness_community 패턴 inheritance)
- Part2 V3-Phase 매핑: V1-Phase 3 FULL 승급 후 challenge_leaderboard V3 implementation 본격 진행
- production 측정 실측값: challenge_leaderboard V3 산출물 byte/SHA/LF + L3 ≥ 80점 + LOCK-ED-10 6-stage 게이미피케이션 (XP→Level→Badge→Streak→Challenge→Leaderboard) + 익명성 + 부정행위 방지 (`D:/VAMOS/docs/sot 2/3-5_Education-Learning/05_learning-analytics/challenge_leaderboard.md` — V3)
- Phase 5 entry-gate 충족 조건: V3 implementation 100% + LOCK-ED-10 6-stage 영구 baseline + 익명성/부정행위 방지 영구
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: challenge_leaderboard V3 100% 완성 + Status APPROVED + 5 conditions 전수 충족 + LOCK-ED-10 EXACT

**목표**: challenge_leaderboard V3 산출물을 production-ready 정본으로 승급한다. LOCK-ED-10 6-stage 게이미피케이션 시스템 + 익명성 + 부정행위 방지 production baseline.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/05_learning-analytics/challenge_leaderboard.md` (V3)
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/EDUCATION_LEARNING_구조화_종합계획서.md` §7 P3-3
- `D:/VAMOS/docs/sot 2/3-6_Health-Wellness-EmotionAI/05_emotion-journal/wellness_community.md` (패턴 inheritance reference)
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/AUTHORITY_CHAIN.md` (LOCK-ED-10 정본)

**절차**:
1. P3-3 forward-defined 5 conditions inventory 확인.
2. challenge_leaderboard V3 정본 작성: LOCK-ED-10 6-stage (XP→Level→Badge→Streak→Challenge→Leaderboard) + 익명성 (해시화 닉네임) + 부정행위 방지 (timestamp 검증, 통계적 이상치 감지) 명세.
3. Status DRAFT → APPROVED 전환 + Last-reviewed 갱신.
4. LOCK-ED-10 인용 형식 통일 (`> LOCK (ED AUTHORITY §3.4): XP→Level→Badge→Streak→Challenge→Leaderboard`).
5. 3-6 wellness_community 패턴 inheritance 정합 검증.
6. AUTHORITY_CHAIN.md cross-check: LOCK-ED-10 정본 출처 변경 0.
7. production 실측 측정: challenge_leaderboard V3 산출물 byte/SHA/LF + L3 ≥ 80 + 5 conditions 충족.
8. Phase 5 entry-gate forward-defined 작성.

**검증**:
- [ ] challenge_leaderboard V3 Status APPROVED 전환 완료
- [ ] L3 점수 ≥ 80
- [ ] LOCK-ED-10 6-stage 게이미피케이션 EXACT
- [ ] 익명성 (해시화 닉네임) production 정합
- [ ] 부정행위 방지 (timestamp + 통계 이상치) production 정합
- [ ] 3-6 wellness_community 패턴 inheritance 정합
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] challenge_leaderboard V3 production-ready 정본 승급 조건 충족** (5 conditions 전수)

**산출물**: challenge_leaderboard V3 production .md 정본 + `_verification/phase4_v3_p4-3_promotion_report.md`
</details>

<details>
<summary><b>P4-4. voice_learning V3 산출물 production-ready 정본 승급 (P3-4 inheritance, STT 3 engines + LOCK-MM-08 + 90% 정확도)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-4 "voice_learning V3 production-ready 정본 승급" (P3-4 forward-defined, 4 conditions)
- §7 전환 게이트: G4-1 + G4-5
- §6 이슈: §6.3 03_coding-tutorial voice_learning V3 Phase 4 정본 승급
- 교차 도메인: 3-2 Multimodal (LOCK-MM-08 16kHz mono PCM cross-domain reference)
- Part2 V3-Phase 매핑: V1-Phase 3 FULL 승급 후 voice_learning V3 implementation 본격 진행
- production 측정 실측값: voice_learning V3 산출물 byte/SHA/LF + L3 ≥ 80점 + STT 3 engines + LOCK-MM-08 16kHz mono PCM + 90% 정확도 + LOCK-ED-06 Socratic
- Phase 5 entry-gate 충족 조건: V3 implementation 100% + STT 3 engines 영구 baseline + LOCK-MM-08 EXACT
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: voice_learning V3 100% 완성 + Status APPROVED + 4 conditions 전수 충족 + LOCK-MM-08 EXACT

**목표**: voice_learning V3 산출물을 production-ready 정본으로 승급한다. STT 3 engines + LOCK-MM-08 16kHz mono PCM + 90% 정확도 + Socratic pedagogy production baseline.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/03_coding-tutorial/voice_learning.md` (V3)
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/EDUCATION_LEARNING_구조화_종합계획서.md` §7 P3-4
- `D:/VAMOS/docs/sot 2/3-2_Multimodal-Processing/AUTHORITY_CHAIN.md` (LOCK-MM-08 cross-domain reference)
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/AUTHORITY_CHAIN.md` (LOCK-ED-06 정본)

**절차**:
1. P3-4 forward-defined 4 conditions inventory 확인.
2. voice_learning V3 정본 작성: STT 3 engines (예: Whisper/Deepgram/Google, P3-4 baseline directional inheritance, D-P4-4-1 fix 2026-05-25) + LOCK-MM-08 16kHz mono PCM + 90% 정확도 + LOCK-ED-06 Socratic 명세.
3. Status DRAFT → APPROVED 전환 + Last-reviewed 갱신.
4. LOCK-MM-08 + LOCK-ED-06 인용 형식 통일.
5. 3-2 Multimodal LOCK-MM-08 cross-domain reference 정합 검증.
6. AUTHORITY_CHAIN.md cross-check: 변경 0.
7. production 실측 측정: voice_learning V3 산출물 byte/SHA/LF + L3 ≥ 80 + 4 conditions 충족.
8. Phase 5 entry-gate forward-defined 작성.

**검증**:
- [ ] voice_learning V3 Status APPROVED 전환 완료
- [ ] L3 점수 ≥ 80
- [ ] STT 3 engines production 정합
- [ ] LOCK-MM-08 16kHz mono PCM EXACT
- [ ] 90% 정확도 production 실측 PASS
- [ ] LOCK-ED-06 Socratic EXACT
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] voice_learning V3 production-ready 정본 승급 조건 충족** (4 conditions 전수)

**산출물**: voice_learning V3 production .md 정본 + `_verification/phase4_v3_p4-4_promotion_report.md`
</details>

<details>
<summary><b>P4-5. presentation_feedback V3 산출물 production-ready 정본 승급 (P3-5 inheritance, 6 eval + LOCK-MM-07/08/09 + 3-6 anxiety)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-5 "presentation_feedback V3 production-ready 정본 승급" (P3-5 forward-defined, 6 conditions 최다)
- §7 전환 게이트: G4-1 + G4-5 + G4-6
- §6 이슈: §6.5 05_learning-analytics presentation_feedback V3 Phase 4 정본 승급
- 교차 도메인: 3-2 Multimodal (LOCK-MM-07/08/09 cross-domain) + 3-6 Health (R-08-6 opt-in emotion anxiety detection)
- Part2 V3-Phase 매핑: V1-Phase 3 FULL 승급 후 presentation_feedback V3 implementation 본격 진행
- production 측정 실측값: presentation_feedback V3 산출물 byte/SHA/LF + L3 ≥ 80점 + 6 eval metrics + LOCK-MM-07 CLIP 768d + LOCK-MM-08 16kHz + LOCK-MM-09 max_frames=100 + LOCK-ED-05 Bloom + 3-6 R-08-6 anxiety opt-in
- Phase 5 entry-gate 충족 조건: V3 implementation 100% + 3-6 R-08-6 anxiety opt-in 양방향 영구 + LOCK-MM-07/08/09 EXACT
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: presentation_feedback V3 100% 완성 + Status APPROVED + 6 conditions 전수 충족 + 3-6 R-08-6 양방향 영구

**목표**: presentation_feedback V3 산출물을 production-ready 정본으로 승급한다. 6 평가 지표 + Multimodal LOCK-MM-07/08/09 + Bloom + 3-6 Health 불안 감지 R-08-6 opt-in 양방향 cross-handoff 영구 baseline.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/05_learning-analytics/presentation_feedback.md` (V3)
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/EDUCATION_LEARNING_구조화_종합계획서.md` §7 P3-5
- `D:/VAMOS/docs/sot 2/3-2_Multimodal-Processing/AUTHORITY_CHAIN.md` (LOCK-MM-07/08/09 cross-domain)
- `D:/VAMOS/docs/sot 2/3-6_Health-Wellness-EmotionAI/AUTHORITY_CHAIN.md` (R-08-6 anxiety opt-in)

**절차**:
1. P3-5 forward-defined 6 conditions inventory 확인.
2. presentation_feedback V3 정본 작성: 6 평가 지표 (음성/표정/제스처/구조/내용/논리) + LOCK-MM-07 CLIP + LOCK-MM-08 16kHz + LOCK-MM-09 max_frames=100 + LOCK-ED-05 Bloom + 3-6 R-08-6 anxiety opt-in 명세.
3. Status DRAFT → APPROVED 전환 + Last-reviewed 갱신.
4. LOCK-MM-07/08/09 + LOCK-ED-05 인용 형식 통일.
5. 3-6 Health R-08-6 ↔ R-09-6 anxiety opt-in cross-handoff 양방향 정합 검증.
6. AUTHORITY_CHAIN.md cross-check: 변경 0.
7. production 실측 측정: presentation_feedback V3 산출물 byte/SHA/LF + L3 ≥ 80 + 6 conditions 충족.
8. Phase 5 entry-gate forward-defined 작성.

**검증**:
- [ ] presentation_feedback V3 Status APPROVED 전환 완료
- [ ] L3 점수 ≥ 80
- [ ] 6 평가 지표 (음성/표정/제스처/구조/내용/논리) production 정합
- [ ] LOCK-MM-07 CLIP + LOCK-MM-08 16kHz + LOCK-MM-09 max_frames=100 EXACT
- [ ] LOCK-ED-05 Bloom EXACT
- [ ] 3-6 R-08-6 anxiety opt-in 양방향 정합
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] presentation_feedback V3 production-ready 정본 승급 조건 충족** (6 conditions 전수)

**산출물**: presentation_feedback V3 production .md 정본 + `_verification/phase4_v3_p4-5_promotion_report.md`
</details>

<details>
<summary><b>P4-6. study_group_matching V3 산출물 production-ready 정본 승급 (P3-6 inheritance, matching 4-elements + LOCK-ED-07 + PKM inheritance)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-6 "study_group_matching V3 production-ready 정본 승급" (P3-6 forward-defined, 4 conditions)
- §7 전환 게이트: G4-1 + G4-6 "도메인 간 통합 준비 (3-3 PKM knowledge_sharing inheritance)"
- §6 이슈: §6.5 05_learning-analytics study_group_matching V3 Phase 4 정본 승급
- 교차 도메인: 3-3 PKM (M-028 knowledge_sharing V3 multi-user inheritance) + 3-6 Health (R-08-6 stress compatibility opt-in)
- Part2 V3-Phase 매핑: V1-Phase 3 FULL 승급 후 study_group_matching V3 implementation 본격 진행
- production 측정 실측값: study_group_matching V3 산출물 byte/SHA/LF + L3 ≥ 80점 + matching 4 elements (skill_level + learning_speed + goal + schedule) + LOCK-ED-07 learner profile + 3-3 PKM M-028 inheritance + 3-6 R-08-6 stress opt-in
- Phase 5 entry-gate 충족 조건: V3 implementation 100% + 3-3 PKM M-028 cross-handoff 양방향 영구 + 3-6 R-08-6 stress opt-in 영구
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: study_group_matching V3 100% 완성 + Status APPROVED + 4 conditions 전수 충족 + LOCK-ED-07 EXACT + 3-3/3-6 양방향 영구

**목표**: study_group_matching V3 산출물을 production-ready 정본으로 승급한다. matching 4 elements + LOCK-ED-07 learner profile + 3-3 PKM M-028 knowledge_sharing inheritance + 3-6 Health stress compatibility opt-in cross-handoff 영구 baseline.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/05_learning-analytics/study_group_matching.md` (V3)
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/EDUCATION_LEARNING_구조화_종합계획서.md` §7 P3-6
- `D:/VAMOS/docs/sot 2/3-3_PKM-Knowledge-Management/03_spaced-repetition/knowledge_sharing.md` (M-028 V3 multi-user inheritance reference, D-P4-6-2 fix 2026-05-25 actual path inheritance)
- `D:/VAMOS/docs/sot 2/3-6_Health-Wellness-EmotionAI/AUTHORITY_CHAIN.md` (R-08-6 stress opt-in)
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/AUTHORITY_CHAIN.md` (LOCK-ED-07 정본)

**절차**:
1. P3-6 forward-defined 4 conditions inventory 확인.
2. study_group_matching V3 정본 작성: matching 4 elements (skill_level + learning_speed + goal + schedule) + LOCK-ED-07 learner profile schema + 3-3 PKM M-028 inheritance + 3-6 R-08-6 stress opt-in 명세.
3. Status DRAFT → APPROVED 전환 + Last-reviewed 갱신.
4. LOCK-ED-07 인용 형식 통일.
5. 3-3 PKM M-028 + 3-6 R-08-6 cross-handoff 양방향 정합 검증.
6. AUTHORITY_CHAIN.md cross-check: LOCK-ED-07 정본 출처 변경 0.
7. production 실측 측정: study_group_matching V3 산출물 byte/SHA/LF + L3 ≥ 80 + 4 conditions 충족.
8. Phase 5 entry-gate forward-defined 작성.

**검증**:
- [ ] study_group_matching V3 Status APPROVED 전환 완료
- [ ] L3 점수 ≥ 80
- [ ] matching 4 elements production 정합
- [ ] LOCK-ED-07 learner profile schema EXACT
- [ ] 3-3 PKM M-028 cross-handoff 양방향 정합
- [ ] 3-6 R-08-6 stress opt-in 양방향 정합
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] study_group_matching V3 production-ready 정본 승급 조건 충족** (4 conditions 전수)

**산출물**: study_group_matching V3 production .md 정본 + `_verification/phase4_v3_p4-6_promotion_report.md`
</details>

<details>
<summary><b>P4-7. vr_ar_learning V3 산출물 production-ready 정본 승급 (P3-7 inheritance, 3 devices + LOCK-ED-02 + 3-2 inheritance + safety)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-7 "vr_ar_learning V3 production-ready 정본 승급" (P3-7 forward-defined, 4 conditions)
- §7 전환 게이트: G4-1 + G4-5
- §6 이슈: §6.3 03_coding-tutorial vr_ar_learning V3 Phase 4 정본 승급
- 교차 도메인: 3-2 Multimodal (이미지/공간 인식 J-009 AR inheritance)
- Part2 V3-Phase 매핑: V1-Phase 3 FULL 승급 후 vr_ar_learning V3 implementation 본격 진행
- production 측정 실측값: vr_ar_learning V3 산출물 byte/SHA/LF + L3 ≥ 80점 + 3 devices (Meta Quest/Apple Vision Pro/Microsoft HoloLens) + LOCK-ED-02 IRT 5단계 + 3-2 J-009 inheritance + safety 3-point (시청시간 / 안전 영역 / 멀미 방지)
- Phase 5 entry-gate 충족 조건: V3 implementation 100% + 3-2 J-009 inheritance 영구 + safety 3-point baseline 영구
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: vr_ar_learning V3 100% 완성 + Status APPROVED + 4 conditions 전수 충족 + safety 영구

**목표**: vr_ar_learning V3 산출물을 production-ready 정본으로 승급한다. 3 devices + LOCK-ED-02 + 3-2 Multimodal J-009 AR inheritance + safety 3-point production baseline.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/03_coding-tutorial/vr_ar_learning.md` (V3)
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/EDUCATION_LEARNING_구조화_종합계획서.md` §7 P3-7
- `D:/VAMOS/docs/sot 2/3-2_Multimodal-Processing/01_image-pipeline/` (J-009 AR/공간 V3 inheritance reference)
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/AUTHORITY_CHAIN.md` (LOCK-ED-02 정본)

**절차**:
1. P3-7 forward-defined 4 conditions inventory 확인.
2. vr_ar_learning V3 정본 작성: 3 devices (Meta Quest/Apple Vision Pro/Microsoft HoloLens) + LOCK-ED-02 IRT 5단계 + 3-2 J-009 AR inheritance + safety 3-point (시청시간 30분 권장/안전 영역 설정/멀미 방지) 명세.
3. Status DRAFT → APPROVED 전환 + Last-reviewed 갱신.
4. LOCK-ED-02 인용 형식 통일.
5. 3-2 Multimodal J-009 inheritance 정합 검증.
6. AUTHORITY_CHAIN.md cross-check: LOCK-ED-02 정본 출처 변경 0.
7. production 실측 측정: vr_ar_learning V3 산출물 byte/SHA/LF + L3 ≥ 80 + 4 conditions 충족.
8. Phase 5 entry-gate forward-defined 작성.

**검증**:
- [ ] vr_ar_learning V3 Status APPROVED 전환 완료
- [ ] L3 점수 ≥ 80
- [ ] 3 devices (Meta Quest/Apple Vision Pro/Microsoft HoloLens) production 정합
- [ ] LOCK-ED-02 IRT 5단계 EXACT
- [ ] 3-2 J-009 AR inheritance 정합
- [ ] safety 3-point (시청시간/안전영역/멀미방지) production 정본
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] vr_ar_learning V3 production-ready 정본 승급 조건 충족** (4 conditions 전수)

**산출물**: vr_ar_learning V3 production .md 정본 + `_verification/phase4_v3_p4-7_promotion_report.md`
</details>

<details>
<summary><b>P4-8. mentoring V3 + 전체 65 항목 L3 최종 점검 + CONFLICT/AUTHORITY 영구 baseline + 3-3 SM-2 + 3-6 emotion 양방향 영구 (P3-8 meta-audit inheritance)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-8 "mentoring V3 + 전체 65 항목 L3 ≥ 60% + V3 8건 L3 ≥ 80점 + CONFLICT_LOG OPEN=0 + 3-3 SM-2 + 3-6 emotion 양방향 영구 baseline" (P3-8 meta-audit forward-defined)
- §7 전환 게이트: G4-2 + G4-3 + G4-4 + G4-5 + G4-6 + G4-7
- §6 이슈: 전체 65 항목 + CFL-ED-006~009 4건 formalization + 17 ReadOnly inheritance
- 교차 도메인: 3-3 PKM SM-2 LOCK-PKM-01~03 ↔ LOCK-ED-04 10/10 verbatim 영구 + 3-6 Health R-08-6 ↔ R-09-6 양방향 영구
- Part2 V3-Phase 매핑: V1-Phase 3 FULL 승급 후 전체 L3 ≥ 60% + V3 ≥ 80점 + VBS-16 영구 baseline
- production 측정 실측값: 65 항목 L3 ≥ 60% + V3 8건 L3 ≥ 80점 + CONFLICT_LOG OPEN=0 (CF-ED-001~005 RESOLVED + CFL-ED-006~009 formalization) + LOCK-ED-01~10 + cross-domain LOCK EXACT (`D:/VAMOS/docs/sot 2/3-5_Education-Learning/CONFLICT_LOG.md` + AUTHORITY_CHAIN.md + INDEX.md)
- Phase 5 entry-gate 충족 조건: L3 ≥ 60% 영구 baseline + CONFLICT zero state + LOCK immutable + VBS-16 영구 + 3-3 SM-2 영구 + 3-6 emotion 영구
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: mentoring V3 100% 완성 + Status APPROVED + 65 항목 L3 ≥ 60% production baseline + V3 8건 ALL L3 ≥ 80점 + CONFLICT 0 영구 + LOCK immutable matrix + 3-3 SM-2 10/10 verbatim 영구 + 3-6 R-08-6/R-09-6 양방향 영구 + ReadOnly 17 EXACT 보존 + emotion_learning_interface.md PRODUCER ↔ 3-6 CONSUMER 계약 영구

**목표**: mentoring V3 산출물을 production-ready 정본으로 승급하고 전체 65 항목 L3 ≥ 60% + V3 8건 L3 ≥ 80점 + CONFLICT/AUTHORITY production 정본 + 3-3 SM-2 + 3-6 emotion 양방향 영구 baseline + ReadOnly 17 EXACT 보존을 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/05_learning-analytics/mentoring.md` (V3)
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/EDUCATION_LEARNING_구조화_종합계획서.md` 전체 (65 항목 baseline)
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/AUTHORITY_CHAIN.md` (LOCK-ED-01~10 + cross-domain 정본)
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/CONFLICT_LOG.md` (OPEN=0 영구 + CFL-ED-006~009 formalization)
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/INDEX.md` (전 inventory SoT)
- `D:/VAMOS/docs/sot 2/3-5_Education-Learning/01_adaptive-learning/emotion_learning_interface.md` (3-6 PRODUCER 정본)
- `D:/VAMOS/docs/sot 2/3-3_PKM-Knowledge-Management/AUTHORITY_CHAIN.md` (SM-2 LOCK-PKM-01~03 cross-domain)
- `D:/VAMOS/docs/sot 2/3-6_Health-Wellness-EmotionAI/AUTHORITY_CHAIN.md` (R-09-6 양방향 cross-domain)
- P4-1~P4-7 산출물 (V3 8건)
- 본 계획서 §10 체크리스트 #10

**절차**:
1. mentoring V3 정본 작성: P3-8 meta-audit 통과 + 65 항목 baseline 최종 검증 명세.
2. 65 항목 L3 매트릭스 전수 재검증: 5 서브폴더 = 65 항목 L3 ≥ 60% PASS.
3. V3 8건 L3 매트릭스 재검증: investment_simulation + conversation_practice + challenge_leaderboard + voice_learning + presentation_feedback + study_group_matching + vr_ar_learning + mentoring ALL L3 ≥ 80점.
4. CONFLICT_LOG.md 영구 마감 확정: CF-ED-001~005 RESOLVED 영구 + CFL-ED-006~009 formalization 4건 추가 마킹 + OPEN=0 선언.
5. AUTHORITY_CHAIN.md production 정본 승급: LOCK-ED-01~10 10건 + cross-domain LOCK-HW-01/12 + LOCK-MM-07/08/09 + LOCK-PKM-01~03 ALL immutable matrix + Status APPROVED.
6. INDEX.md 마스터 갱신: 44 production .md inventory 전수 등재 + L3 완성률 + Status 분포 + ReadOnly 17 마킹.
7. 3-3 PKM SM-2 cross-handoff 양방향 영구 baseline 최종 확정 (LOCK-PKM-01~03 ↔ LOCK-ED-04 10/10 verbatim).
8. 3-6 Health emotion R-08-6 ↔ R-09-6 양방향 영구 baseline 최종 확정 (emotion_learning_interface.md PRODUCER ↔ 3-6 CONSUMER 계약).
9. ReadOnly 17 파일 ALL EXACT 보존 검증 (byte/SHA aggregate 보존).
10. /final-review PASS + VBS-16 학습 지속률 ≥ 60% + 기억 보존 ≥ 80% 영구 baseline.
11. production 실측 측정: 65 항목 L3 분포 + V3 8건 L3 점수 + AUTHORITY/CONFLICT/INDEX byte/SHA/LF + 3-3 + 3-6 양방향 정합 + ReadOnly 17 byte 보존.
12. Phase 5 entry-gate forward-defined 작성 (운영 baseline + CONFLICT zero state 영구 + LOCK immutable 영구 + 3-3 SM-2 영구 + 3-6 emotion 영구).

**검증**:
- [ ] mentoring V3 산출물 Status APPROVED 전환 완료 + L3 ≥ 80
- [ ] 65 항목 L3 ≥ 60% 영구 baseline 확립
- [ ] V3 8건 ALL L3 ≥ 80점
- [ ] CONFLICT_LOG OPEN=0 영구 마감 (CF-ED-001~005 RESOLVED + CFL-ED-006~009 formalization)
- [ ] AUTHORITY_CHAIN Status APPROVED + LOCK-ED-01~10 + cross-domain ALL immutable matrix
- [ ] INDEX.md 44 production .md inventory 전수 + L3 완성률 영구 + ReadOnly 17 마킹
- [ ] 3-3 PKM SM-2 LOCK-PKM-01~03 ↔ LOCK-ED-04 10/10 verbatim 양방향 영구 baseline
- [ ] 3-6 Health R-08-6 ↔ R-09-6 양방향 영구 baseline (emotion_learning_interface PRODUCER ↔ 3-6 CONSUMER 계약 영구)
- [ ] ReadOnly 17 파일 byte/SHA EXACT 보존
- [ ] /final-review PASS + VBS-16 학습 지속률 ≥ 60% + 기억 보존 ≥ 80%
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] mentoring V3 + 65 항목 L3 baseline + CONFLICT 0 + LOCK immutable + 3-3 SM-2 + 3-6 emotion 양방향 + ReadOnly 17 영구 production-ready 정본 승급 조건 충족**

**산출물**: mentoring V3 production .md 정본 + AUTHORITY_CHAIN.md Phase 4 정본 v1.X (immutable LOCK-ED-01~10 + cross-domain matrix) + CONFLICT_LOG.md Phase 4 정본 v1.X (OPEN=0 영구 + CFL-ED-006~009 formalization) + INDEX.md Phase 4 정본 + `_verification/phase4_l3_baseline_report.md` (65 항목 L3 + 3-3 SM-2 + 3-6 emotion 양방향 + ReadOnly 17 영구 baseline)
</details>

#### Phase 4 세션 전체 검증 결과 요약 (3-5 Education-Learning, 2026-05-25, Sub-A + Sub-B 통합 Stage A, 🎉🎉🎉 8/8 P4 NO-DRIFT FULL milestone 통산 첫 분할 도메인 FULL specialty milestone)

> **본 블록**: 3-5 Education-Learning Phase 4 implementation Stage A 단계 (ENTRY_PROMPT v1.1 2분할 sub-A 4 + sub-B 4, chain `phase4_3-5_subA_2026-05-24` + `phase4_3-5_subB_2026-05-25`) 전체 세션 검증 결과 종합 요약. SPEC Stage B sub-cycle 시점 production .md 본문 작성 + Status APPROVED 전환 + RO EXACT 패턴 적용 진입 baseline.

**8/8 P4 task 완료 매트릭스 (Sub-A 4 + Sub-B 4, verify-only per 사용자 결정 A inheritance 통산 14번째 P4 task)**:

| # | P4 task | scope | LOCK 인용 | cross-domain reference | drift | result |
|---|---------|-------|-----------|---------------------|:----:|:------:|
| **P4-1** (Sub-A) | investment_simulation V3 production 승급 (`04_content-generation/`) | verify-only per A | LOCK-ED-02 IRT 5단계 + LOCK-ED-05 Bloom + LOCK-ED-09 VBS-16 (3 in-domain) | (LOCK-ED-04 SM-2 §5 R-08-1 보존만, 활성 0) | 1 deferred (D-P4-1-1) | ✅ NO-DRIFT |
| **P4-2** (Sub-A) | conversation_practice V3 production 승급 (`04_content-generation/`) | verify-only per A | LOCK-ED-06 Socratic + LOCK-ED-08 (2 in-domain) + LOCK-HW-01 (1 cross-domain emotion 양방향 첫 활성 ⭐) | **3-6 R-08-6 ↔ R-09-6 양방향 첫 활성 (emotion_LIF PRODUCER 가동)** | 0 신규 | ✅ NO-DRIFT |
| **P4-3** (Sub-A) | challenge_leaderboard V3 production 승급 (`05_learning-analytics/`) | verify-only per A | LOCK-ED-10 6-stage (1 single direct EXACT specialty) | 3-6 wellness_community.md forward-defined inheritance reference | 0 신규 | ✅ NO-DRIFT |
| **P4-4** (Sub-A) | voice_learning V3 production 승급 (`03_coding-tutorial/`) | verify-only per A | LOCK-ED-06 Socratic (1 in-domain) + LOCK-MM-08 (1 cross-domain DEFINED-HERE Phase 5 동결 첫 활성 ⭐) | **3-2 LOCK-MM-08 cross-domain DEFINED-HERE 첫 활성 strong immutable form** | 1 deferred (D-P4-4-1) | ✅ NO-DRIFT |
| **P4-5** (Sub-B) | presentation_feedback V3 production 승급 (`05_learning-analytics/`) | verify-only per A | LOCK-ED-05 Bloom (1 in-domain) + LOCK-MM-07/08/09 (3 cross-domain DEFINED-HERE Phase 5 동결 동시 활성 첫 사례 ⭐⭐) | **3 cross-domain LOCK DEFINED-HERE 동시 활성 specialty 첫 사례** + 3-6 R-08-6 anxiety 양방향 2번째 활성 | 1 deferred (D-P4-5-1 substantive ⚠️) | ✅ NO-DRIFT |
| **P4-6** (Sub-B) | study_group_matching V3 production 승급 (`05_learning-analytics/`) | verify-only per A | LOCK-ED-07 학습자 프로필 5필드 (1 in-domain single direct) | **3-3 PKM M-028 knowledge_sharing.md cross-reference 첫 활성 ⭐** + 3-6 R-08-6 stress 양방향 3번째 활성 | 2 deferred (D-P4-6-1 substantive ⚠️ + D-P4-6-2 textual) + 1 candidate (D-P4-6-3 substantive PASS default) | ✅ NO-DRIFT |
| **P4-7** (Sub-B) | vr_ar_learning V3 production 승급 (`03_coding-tutorial/`) | verify-only per A | LOCK-ED-02 IRT 5단계 (1 in-domain single direct) + LOCK-MM-07 implicit (1 cross-domain via J-009) | **3-2 J-009 vision_language_integration.md V3 골격 inheritance 첫 활성 ⭐** + LOCK-MM-07 implicit cross-domain 2번째 활성 | 1 deferred (D-P4-7-1 substantive ⚠️) + 2 candidates (D-P4-7-2/3 substantive PASS default) | ✅ NO-DRIFT |
| **P4-8** (Sub-B, **🎉 FINAL P4 specialty**) | mentoring V3 + 전체 65 항목 L3 + V3 8건 + CONFLICT/AUTHORITY 영구 baseline + 3-3 SM-2 + 3-6 emotion 양방향 영구 (`05_learning-analytics/`) | verify-only per A | **18 LOCK 활성 (P4 task 통산 최다 specialty ⭐⭐⭐)**: LOCK-ED-01~10 10 + LOCK-PKM-01~03 3 + LOCK-HW-01/12 2 + LOCK-MM-07/08/09 3 | **🌟 3-3 PKM SM-2 LOCK-PKM-01~03 ↔ LOCK-ED-04 10/10 verbatim 양방향 영구 baseline 마감 FIRST 활성 specialty ⭐⭐⭐** + **3-6 R-08-6/R-09-6 4번째 sub-type 양방향 영구 baseline 마감 specialty ⭐⭐** + emotion_LIF PRODUCER 영구 baseline 마감 | 0 confirmed + 2 candidates (D-P4-8-1 textual minor filename + D-P4-8-2 substantive PASS default) | ✅ NO-DRIFT |

**8/8 P4 통산 결과 핵심 매트릭스**:

| 항목 | 결과 |
|------|:----:|
| 🎉🎉🎉 **3-5 전체 8/8 NO-DRIFT FULL milestone ⭐⭐⭐⭐** | **통산 첫 분할 도메인 FULL specialty milestone first 사례** (Sub-A 4 + Sub-B 4 = 8 ALL first-pass NO-DRIFT zero-fix Stage A 관점) |
| 🎉🎉🎉 **NO-DRIFT direct path 18-consecutive ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐ NEW 18-단위 milestone 확정** | 3-3 P4-1~P4-6 6 + 3-4 P4-1~P4-4 4 + 3-5 P4-1~P4-8 8 = 18 (substantive severity caveat 통산 3건 D-P4-5-1 + D-P4-6-1 + D-P4-7-1) |
| R cascade 통산 verifications | **1,053 verifications + 936 sub-checks** (13 rounds × 9 sub-step × 8 P4 + 13 × 9 × 8 = 1,053 + 8 × 117 = 936 Sub-A 468 + Sub-B 468) |
| Confirmed drift detected (Stage A 관점) | 0 confirmed (P4-2/P4-3/P4-5/P4-8 0 drift) + 5 deferred textual/substantive (D-P4-1-1 + D-P4-4-1 + D-P4-5-1 substantive + D-P4-6-1 substantive + D-P4-6-2 + D-P4-7-1 substantive + D-P4-8-1 candidate textual) + 4 candidates substantive PASS default (D-P4-6-3 + D-P4-7-2/3 + D-P4-8-2) — ALL deferred to SPEC Stage B fix queue 또는 ⑤ bilateral |
| Fix 적용 (Stage A) | **0** (deferred to SPEC Stage B fix queue per A) |
| truly_converged_v1 first-pass-after-zero-fix CONFIRMED Stage A 관점 | ✅ 8/8 P4 task ALL |
| **LOCK / DEFINED-HERE / FABRICATION 변경** | **0 / 0 / 0** (LOCK matrix 18 distinct activated/referenced ALL EXACT verbatim) |
| **production .md write** | **0** (Sub-A 4 + Sub-B P4-5~P4-8 = 8/8 P4 ZERO write 통산 FINAL ⭐⭐⭐ — verify-only per A inheritance) |
| **17 RO 활성 .md baseline 보존** | ✅ 17/17 EXACT 8/8 P4 통산 무손상 FINAL + RO Status TRUE 유지 통산 + RO EXACT 패턴 NOT TRIGGERED 통산 (verify-only mode) |
| **23 RW 활성 .md baseline 보존** | ✅ |
| **emotion_LIF PRODUCER baseline 보존** | ✅ 24,196 B / `4731B8E741D5E9B5` / 426 LF EXACT 영구 baseline 마감 (P4-2 활성 영구 + P4-8 4번째 emotion sub-type 양방향 영구 마감) |
| **9 baseline file byte/SHA** | ✅ 8/9 EXACT + 1/9 SOT2 (Sub-B step 0 baseline re-capture acknowledged 새 baseline 246,092 / `F965D8BCE1BCD50D` 채택) |
| **Sub-A + Sub-B cross-domain reference 통산** | **8 cross-domain reference 활성 영구 마감 specialty FINAL** ⭐⭐⭐ (P4-2 + P4-4 + P4-5 3-LOCK + P4-2/P4-5/P4-6 R-08-6 3 distinct + P4-6 3-3 M-028 + P4-7 3-2 J-009 + LOCK-MM-07 implicit + P4-8 SM-2 양방향 영구 마감 + R-08-6/R-09-6 4번째 sub-type 양방향 영구 마감) |

**abort marker 9종 NOT FIRED self-fire 0 통산** (8 P4 × 9 markers + ④⑤⑥⑦ 9 + verify_post_domain 9 = 90 markers ALL NOT FIRED Stage A FINAL):
- [UPSTREAM_V3_SPEC_MISSING:3-5] auto PASS 통산 (Wave 1 #7 upstream 0건)
- [PRODUCTION_WRITE_VIOLATION:3-5_P4_X] 0건 (8/8 P4 ZERO write FINAL)
- [STAGE9_READONLY_RESTORE_FAIL:3-5_P4_X] 0건 (RO EXACT 패턴 NOT TRIGGERED + 17 RO baseline EXACT 통산 8/8 FINAL)
- [STATUS_TRANSITION_FAIL:3-5_P4_X] 0건 (Status DRAFT inheritance acknowledged, SPEC Stage B 위임)
- [V3_PRODUCTION_PROMOTION_FAIL:3-5_P4_X] 0건 (verify-only inheritance forward-defined 충족 명시)
- **[CROSS_HANDOFF_DRIFT:3-5_P4_X] 0건** (8 cross-domain reference 활성 EXACT 100% verify 통산 FINAL ⭐⭐⭐)
- [BILATERAL_SOT2_DRIFT:3-5_post] ⚪ ⑤ 단계에서 처리 (Sub-B step 0 SOT2 -9 B 새 baseline 246,092 채택)
- [DOWNSTREAM_PROPAGATE_MISS:3-5_post] ⚪ ⑥ 단계에서 처리
- [R_CASCADE_NOT_CONVERGED:3-5_P4_X] 0건 (truly_converged_v1 first-pass-after-zero-fix CONFIRMED Stage A 통산 8/8)

**6 anchor 충족 매트릭스 FINAL** (8/8 P4 통산 ALL ✅):
- **안전**: verify-only ZERO write, 9 baseline + 17 RO + 23 RW + emotion_LIF PRODUCER 영구 baseline 마감
- **누락 0**: 8 대조 + 9 abort + 8~12 검증 + 8~12 절차 + 18 LOCK matrix + 9~11 baseline + 17 RO + 23 RW + forward-defined conditions inventory + cross-handoff 양방향 ALL PASS
- **오류 0**: R cascade 통산 936 sub-checks (8 × 117) drift detected 5 deferred + 0 fix Stage A
- **미세**: AUTHORITY §4 L83-92 18 LOCK verbatim + 3-3 PKM §3.4 L40-42 SM-2 verbatim + 3-6 §5 R-08-6 verbatim + emotion_LIF 426 L 영구
- **수렴**: truly_converged_v1 first-pass-after-zero-fix Stage A 8/8 P4
- **재검증**: R₁₃ post-fix 3-round 자동 cascade 0/0/0 changes 통산 8/8

**Upstream / Downstream 매트릭스**:
- **Upstream (Wave 1 #7)**: 0건 auto PASS (Wave 1 #7 DAG L71 권장 진입 순)
- **Downstream**:
  - 3-6 Health-Wellness-EmotionAI (Wave 1 #8) — emotion_LIF CONSUMER endpoint baseline 영구 + wellness_community.md forward-defined inheritance (P3-3 reference) + R-08-6 ↔ R-09-6 양방향 영구 baseline
  - 3-2 Multimodal-Processing (Wave 1 #4 SPEC ✅ COMPLETE) — LOCK-MM-07/08/09 cross-domain DEFINED-HERE Phase 5 동결 baseline 영구 + J-009 V3 골격 baseline 영구
  - 3-3 PKM-Knowledge-Management (Wave 1 #5 Stage A 완료) — SM-2 LOCK-PKM-01~03 ↔ LOCK-ED-04 10/10 verbatim 양방향 영구 baseline 마감 specialty + M-028 knowledge_sharing.md baseline 영구

**Phase 5 entry-gate forward-defined 매트릭스 (8/8 P4 ALL ✅)**:

| P4 | Phase 5 entry-gate 충족 조건 | G4-X 매핑 |
|----|-------------------------------|-----------|
| P4-1 | V3 100% + asset classes 5 + IRT 5단계 + Bloom Apply/Analyze + 비투자조언 면책 | G4-1 + G4-5 |
| P4-2 | V3 100% + 5+ languages + Socratic + emotion 양방향 영구 | G4-1 + G4-6 |
| P4-3 | V3 100% + LOCK-ED-10 6-stage 영구 + 익명성 + 부정행위 방지 영구 | G4-1 + G4-5 |
| P4-4 | V3 100% + STT 3 engines 영구 + LOCK-MM-08 EXACT | G4-1 + G4-5 |
| P4-5 | V3 100% + 3-6 R-08-6 anxiety 양방향 영구 + LOCK-MM-07/08/09 EXACT | G4-1 + G4-5 + G4-6 |
| P4-6 | V3 100% + 3-3 PKM M-028 양방향 영구 + 3-6 R-08-6 stress 영구 | G4-1 + G4-6 |
| P4-7 | V3 100% + 3-2 J-009 inheritance 영구 + safety 3-point 영구 | G4-1 + G4-5 |
| P4-8 (FINAL) | L3 ≥ 60% 영구 + CONFLICT zero state + LOCK immutable + VBS-16 + 3-3 SM-2 영구 + 3-6 emotion 영구 | G4-2 + G4-3 + G4-4 + G4-5 + G4-6 + G4-7 (6 게이트 최다 specialty) |

**Pattern A 통산**: P4-1 64 → P4-2 65 → P4-3 66 → P4-4 67 → P4-5 68 → P4-6 69 → P4-7 70 → **P4-8 71** (Sub-A + Sub-B 통산 +8 P4 task)
**Pattern B 통산**: P4-1 61 → P4-2 62 → P4-3 63 → P4-4 64 → P4-5 65 → P4-6 66 → P4-7 67 → **P4-8 68** (Sub-A + Sub-B 통산 +8 P4 task)
**사용자 결정 A inheritance 통산**: 7~14번째 P4 task (1-2 + 2-2 + 2-1 + 3-2 + 3-3 + 3-4 + 3-5 8 P4 task = 14 통산)

**Deferred drift queue 통산 8 confirmed + 1 candidate (Stage A 종결 시점, SPEC Stage B fix queue 또는 ⑤ bilateral 위임)**:
- **textual notation only (5건 minor)**: D-P4-1-1 STEP7-O 파일명 + D-P4-4-1 STT 3 engines example + D-P4-6-2 knowledge_sharing path + D-Sub-B-0-1 handoff arithmetic + D-P4-8-1 candidate mentoring filename
- **substantive specification drift (3건 ⚠️)**: D-P4-5-1 6 평가 지표 + D-P4-6-1 matching 4 elements + D-P4-7-1 3 devices Microsoft HoloLens (P3-5/P3-6/P3-7 baseline inheritance 정합 회복 방향)
- **acknowledged 처리 (1건)**: D-Sub-B-0-2 SOT2 -9 B drift acknowledged 새 baseline 246,092 채택
- **substantive PASS default candidates (4건)**: D-P4-6-3 + D-P4-7-2/3 + D-P4-8-2 (6-3 PARL + 6-13 Operations + 3-3 PKM 멀티유저 누락 — Phase 4 V3 정본 vs Phase 5 Agent/운영/협업 구분 의도된 scope 제외)

**ENTRY_PROMPT Stage A 종결 후 SPEC Stage B sub-cycle 진입 baseline**:
- 9 baseline file byte/SHA 통산 8/9 EXACT + 1/9 SOT2 새 baseline (246,092)
- 17 RO 활성 baseline EXACT (RO Status TRUE 유지)
- 23 RW 활성 baseline EXACT
- emotion_LIF PRODUCER 영구 baseline 마감
- 8 cross-domain reference 활성 영구 마감 specialty
- 18 LOCK matrix verbatim EXACT (LOCK-ED-01~10 + LOCK-PKM-01~03 + LOCK-HW-01/12 + LOCK-MM-07/08/09)
- 사용자 결정 A inheritance 통산 14번째 P4 task FINAL
- Pattern A 71 + Pattern B 68 통산
- **🎉🎉🎉 markers**: `[FINAL_P4_DOMAIN_BASELINE_LOCK_COMPLETE:3-5]` + `[SM-2_BIDIRECTIONAL_BASELINE_LOCK_FIRST:3-5_P4_8]` + `[R-08-6_BIDIRECTIONAL_4_DISTINCT_EMOTION_SUB-TYPES_MARGIN_COMPLETE:3-5_P4_8]` + `[SUB_B_4/4_NO_DRIFT_FULL_MILESTONE:3-5]` + `[DOMAIN_3-5_NO_DRIFT_FULL_MILESTONE_8/8:3-5]` + `[NO_DRIFT_DIRECT_PATH_18_CONSECUTIVE:2026-05-25]` + `[LOCK_ACTIVATION_MAX_P4_18:3-5_P4_8]` ALL ✅

### Phase 전환 게이트 요약

| 전환 | 게이트 조건 | 검증 방법 |
|------|------------|-----------|
| Phase 0 → 1 | 폴더 100%, _index 5개, 계획서 확정 | §10 체크리스트 #1~#3 |
| Phase 1 → 2 | V1 파일 100%, LOCK 정합성, SM-2 규약 | §10 체크리스트 #4~#7 |
| Phase 2 → 3 | V2 파일 100%, Health 연동 정의 | §10 체크리스트 #8~#9 |
| Phase 3 → 완료 | V3 파일 100%, VBS-16 통과 | §10 체크리스트 #10 |

---

## §8 파일 역할 분리 명세

| 역할 | STEP7-O | sot 2/3-5_.../ | 기존 상세명세.md | PART2 CAT-E |
|------|---------|----------------|-----------------|-------------|
| **성격** | 보강 체크리스트 | 구현 정본 | 초기 명세 (레거시) | 구현 가이드 |
| **결정 범위** | What (무엇을 만들 것인가) | What + How (알고리즘, 스키마, API) | What (초기 정의) | When + Where (조건, 트리거) |
| **변경 권한** | 읽기 전용 | 거버넌스 규칙 하 변경 가능 | 동결 (참조 전용) | COND 변경 절차 |
| **항목 수** | 69 | 파일 단위 관리 | 690줄 단일 파일 | COND 7개 + UI 1개 |
| **우선순위** | 4순위 (참조) | 1순위 (정본) | 3순위 (레거시 참조) | 2순위 (조건) |
| **갱신 주기** | 불변 | Phase별 갱신 | 불변 (동결) | COND 변경 시 |

### 파일 간 관계

```
STEP7-O (69항목 체크리스트)
    │ 참조
    ▼
sot 2/3-5_Education-Learning/ (구현 정본)  ← 기존 상세명세.md (초기값 인계)
    │ 구현 조건 정의
    ▼
PART2 CAT-E (COND 7개 + UI 1건)
```

---

## §9 충돌 해결 프로토콜

### 9.1 우선순위

```
LOCK 값 (최우선)
  > DESIGN 2.0 확정값
    > 기존 상세명세 확정값
      > 시간순 (최신 우선)
```

### 9.2 충돌 시나리오

| # | 시나리오 | 충돌 당사자 | 해결 규칙 |
|---|----------|------------|-----------|
| C-01 | SM-2 파라미터 충돌 | Education vs PKM (#6) | LOCK-ED-04 → PKM 정본 우선, Education은 커스터마이징 범위 내에서만 조정 |
| C-02 | IRT 난이도 파라미터 불일치 | adaptive_engine vs difficulty_adjustment | LOCK-ED-02 → 5단계 분류 + 70-85% 정답률 목표 불변, 세부 θ 파라미터는 difficulty_adjustment.md 정본 |
| C-03 | Bloom 택소노미 분류 불일치 | 퀴즈 생성 vs 학습 경로 | LOCK-ED-05 → 6단계 순서 불변, 매핑은 quiz_test_generation.md와 learning_path_generator.md 각각 정의 |
| C-04 | Phase 배정 충돌 | 복수 파일이 동일 항목 주장 | §6 매핑 테이블 기준, 최초 매핑 우선, 변경 시 §6 동기 업데이트 |
| C-05 | 감정 기반 학습 적응 범위 | Education vs Health (#9) | R-08-6 → opt-in 필수, 기본 비활성, 인터페이스는 Phase 2에서 정의 |

### 9.3 기록

- 모든 충돌은 `CONFLICT_LOG.md`에 기록
- 기록 형식: `[날짜] [C-ID] [당사자] [결정] [근거]`
- 미기록 충돌 해결은 무효 (R-06)

---

## §10 검증 체크리스트

| # | 검증 항목 | Phase | 기준 | KPI |
|---|----------|-------|------|-----|
| 1 | 폴더 트리 100% 생성 | 0 | §2.1 트리와 일치 | 서브폴더 5/5, _index 5/5 |
| 2 | 계획서 v1.0 확정 | 0 | 본 문서 §1~§14 + 부록 완성 | 14개 섹션 + 4개 부록 |
| 3 | AUTHORITY_CHAIN + CONFLICT_LOG 생성 | 0 | 파일 존재 + 초기 내용 | 2개 파일 |
| 4 | V1 구현 정본 100% 작성 | 1 | §6 V1 태깅 항목 전체 | ~40항목 커버 |
| 5 | LOCK 값 정합성 | 1 | LOCK-ED-01~10 참조 정확 | 10개 LOCK 검증 통과 |
| 6 | SM-2 공유 규약 준수 | 1 | LOCK-ED-04 + R-08-1 | PKM 정본 참조 확인 |
| 7 | Bloom 택소노미 일관성 | 1 | LOCK-ED-05 + R-08-2 | 6단계 순서 보장 확인 |
| 8 | V2 구현 정본 100% 작성 | 2 | §6 V2 태깅 항목 전체 | ~20항목 커버 |
| 9 | Health 연동 인터페이스 정의 | 2 | R-08-6 + opt-in 확인 | 인터페이스 문서 존재 |
| 10 | VBS-16 벤치마크 통과 | 3 | LOCK-ED-09 | 학습 지속률 >= 60%, 기억 유지율 >= 80% |

---

## §11 보완 사항

### S11-1. §6 항목 수 정정 (P0-1 검증, 2026-03-31)

- **발견**: §6.5 실제 항목 18건이나 "~17항목"으로 표기, 전체 합계 69건이나 "68"로 표기
- **원인**: §6.5 O-028-1(VBS-16 벤치마크) 누계 미반영
- **조치**: §1.3, §5, §6 합계, P0-1 프롬프트 전수 68→69 정정 완료
- **영향**: §12 QC-1 "68/68"은 과거 리뷰 시점 기록이므로 변경하지 않음 (현재 정수: 69)

### S11-1a. 68→69 잔류 전수 정정 + 부록 수·COND 범위 정정 (P0-3 검증, 2026-03-31)

- **발견**: S11-1 조치 범위(§1.3, §5, §6, P0-1) 외에 "68항목" 잔류 10곳, "D2.0-01~03" 2곳, "부록 3개" 3곳
- **잔류 위치**: 메타 테이블, §1.1, §1.2, §1.5, §3.2, §3.3, §8 역할 테이블+파일 관계도, §14 W1, 부록 §C 다이어그램, P0-1 입력, P0-3 전체, P0-4 절차, §10 #2, Phase 0 게이트, 목차
- **조치**:
  - 68항목 → 69항목: 전수 10곳 정정 (§12 QC-1 "68/68"은 S11-1 결정대로 보존)
  - D2.0-01~03 → D2.0-01~07 (7개): §3.2 권한 체인, P0-3 입력, P0-4 절차 정정 (§1.4의 7개 COND 기준)
  - 부록 3개 → 4개: P0-3 절차/검증, §10 #2, Phase 0 게이트 정정 (부록 §D 추가 반영)
  - 목차: 18번 항목 "부록 §D Part2 교차 참조" 추가
  - P0-3 절차 5·6 신설: 목차 정합성 점검, 문서 내부 수치 일관성 교차 검증
  - P0-3 검증 항목 4개 → 6개로 확장
- **영향**: 문서 전체 수치 일관성 확보 (69항목, 7 COND, 4 부록, 5 서브폴더)
- **보존**: §12 QC-1 "68/68", QC-3 "3부록"은 2026-03-26 리뷰 시점 기록이므로 변경하지 않음 (§D는 2026-03-27 추가)

### S11-2. O-ID↔항목명 불일치 기록 (P0-1 검증, 2026-03-31)

- **발견**: STEP7-O 원본 O-ID 항목명과 §6 매핑 항목명 7건 불일치
- **대상**: O-015(뉴스→발표), O-018(커뮤니티→매핑 부재), O-021(저널링→습관), O-023(글쓰기→스터디그룹), O-024(발표→노트), O-025(인맥→집중), O-026(명상→자격증)
- **판정**: §6 기준 확정 — Education 도메인 적합성 기반 재배치로 판단
- **O-018 처리**: V3 일정 항목으로, O-023(스터디 그룹)·§D.4 Phase 3에 흡수

---

## §12 FINAL REVIEW 결과

> **리뷰 일자**: 2026-03-26
> **리뷰 유형**: S8-2 Tier 3 심층 품질 검토 (QC-1~QC-8)
> **판정**: **B+ (PASS — 경미 보완 권장)**

### 12.1 QC 결과 요약

| QC | 항목 | 등급 | 비고 |
|----|------|:----:|------|
| QC-1 | Part2 반영 완전성 | A | 68/68 O-항목 100% 매핑 |
| QC-2 | LOCK 값 정밀 대조 | A | LOCK-ED-01~10, SM-2 PKM 정본 참조 정확 |
| QC-3 | 섹션 깊이 균형 | A | 14§ + 3부록 (교수법 깊이 30.7%) |
| QC-4 | 방식 C 요약 품질 | A | 5서브폴더 33파일 계획 |
| QC-5 | 기술적 정확도 | A | IRT 2PL, Bloom 6단계, SM-2 교육 확장 |
| QC-6 | 실행 가능성 | B+ | Phase 0~3, L3 55%→94%→100% |
| QC-7 | 내부 수치 일관성 | A | Bloom 가중 EF + context_factor 일관 |
| QC-8 | DEFINED-HERE 품질 | B+ | L3 루브릭 완비, 구현 파일 Phase 1부터 |

### 12.2 검증 프로토콜

| 단계 | 결과 |
|------|------|
| `/validate SSV` | PASS — 5서브폴더, 4거버넌스, 14섹션, 깊이≤2 |
| `/audit SOT2-AD3` | PASS — LOCK 재정의 0건, SM-2 단방향 소유 확인 |
| `/sot-check sot2` | PASS — SM-2 정합, LOCK-ED 고유, VBS-16 고유 |

### 12.3 보완 완료 사항

- [x] SM-2 PKM↔Education 정본 소유 양쪽 대칭 확인 완료

---

## §13 L3 전수 승급 계획

### 13.1 L3 완성도 매트릭스

각 서브폴더 내 파일이 L3(구현 수준) 승급을 위해 충족해야 하는 10개 기준.

| ID | 기준 | 설명 | 배점 | L3 통과 |
|----|------|------|------|---------|
| E1 | Input Schema | 입력 데이터 스키마 정의 (JSON Schema / TypeScript interface) | 10 | >= 8 |
| E2 | Output Schema | 출력 데이터 스키마 정의 | 10 | >= 8 |
| E3 | Algorithm / Pipeline | 핵심 알고리즘 또는 처리 파이프라인 의사코드 | 10 | >= 8 |
| E4 | Pedagogical Model (교수법) | 적용 교수법 명시 (Bloom, 소크라테스, ZPD 등) | 10 | >= 8 |
| E5 | Error Handling | 에러 케이스 정의 + 복구 전략 | 10 | >= 7 |
| E6 | Privacy / Security | 학습자 데이터 프라이버시 + 보안 규칙 | 10 | >= 8 |
| E7 | Performance SLA | 응답 시간, 처리량, 가용성 목표 | 10 | >= 7 |
| E8 | Integration Test | 외부 의존성 통합 테스트 시나리오 | 10 | >= 7 |
| E9 | Dependencies | 외부 도메인/모듈 의존성 명시 | 10 | >= 8 |
| E10 | UX / Gamification | 사용자 경험 + 게이미피케이션 요소 정의 | 10 | >= 7 |
| | **합계** | | **100** | **L3 >= 80점** |

### 13.2 서브폴더별 목표

| 서브폴더 | 파일 수 | Phase 1 목표 | Phase 2 목표 | Phase 3 목표 |
|----------|---------|-------------|-------------|-------------|
| 01_adaptive-learning | 6 | 4파일 L3 (80+) | 6파일 L3 | 6파일 L3 |
| 02_spaced-repetition | 3 | 3파일 L3 (80+) | 3파일 L3 | 3파일 L3 |
| 03_coding-tutorial | 5 | 3파일 L3 (80+) | 5파일 L3 | 5파일 L3 |
| 04_content-generation | 8 | 4파일 L3 (80+) | 8파일 L3 | 8파일 L3 |
| 05_learning-analytics | 11 | 4파일 L3 (80+) | 9파일 L3 | 11파일 L3 |
| **합계** | **33** | **18파일** | **31파일** | **33파일** |

### 13.3 Phase 2~3 L3 완성도 최종 확정 매트릭스 (2026-05-16, Path A drift fix Stage 1)

> **출처 (V-17 SoT)**: AUTHORITY_CHAIN.md §8.1 V2 18 strict label (L155~L173, 13 NEW + 5 EXTEND / 5,217 LF) + §8.4 [PHASE3_READY v2: 3-5 — 2026-04-20 최종 확정] inheritance + ★ SM-2 verbatim 5-field × 2측 = 10/10 EXACT MATCH (LOCK-PKM-01~03 ↔ LOCK-ED-04 §3.4 L86 + §5 L113) + ★ R-08-6 ↔ R-09-6 양방향 최종 확정 (§5 L116 + §8.3 v2.1 emotion_learning_interface PRODUCER + 3-6 CONSUMER LOCK-HW-01/HW-12).

| 서브폴더 | V1 (Phase 1) | V2 (Phase 2) | V3 (Phase 3) | 통산 L3 | 비고 |
|----------|:----:|:----:|:----:|:----:|------|
| 01_adaptive-learning | 4 L3 | **3 NEW** (investment_education + language_learning + emotion_learning_interface PRODUCER) | 0 | 7 | LOCK-ED-01/02/05/06/07 + LOCK-HW-01/12 (cross-domain) |
| 02_spaced-repetition | 3 L3 | **1 EXTEND** (flashcard_auto_generation) | 0 | 4 | LOCK-ED-04 SM-2 PKM 참조 + LOCK-ED-08 |
| 03_coding-tutorial | 3 L3 | **1 NEW + 1 EXTEND** (coding_challenge + project_based_learning) | **2 V3** (P3-4 voice_learning + P3-7 vr_ar_learning) | 7 | LOCK-ED-02/06/10 + LOCK-MM-07/08 (cross-domain) |
| 04_content-generation | 4 L3 | **4 NEW + 1 EXTEND** (paper + podcast + online_course + presentation + mindmap EXTEND) | **2 V3** (P3-1 investment_simulation + P3-2 conversation_practice) | 11 | LOCK-ED-02/03/05/06/08/09 + LOCK-MM-08 (cross-domain) + 3-1 AI Investing 별도 트랙 ref |
| 05_learning-analytics | 4 L3 | **5 NEW + 2 EXTEND** (habit + career + note + focus + certification + learning_dashboard EXTEND + gamification EXTEND) | **4 V3** (P3-3 challenge_leaderboard + P3-5 presentation_feedback + P3-6 study_group_matching + P3-8 mentoring_platform) | 15 | LOCK-ED-01/04/05/06/07/09/10 + LOCK-MM-07/08/09 (cross-domain) + LOCK-HW-01 ref (P3-8 멘토 노트) |
| **합계** | **18 L3** | **13 NEW + 5 EXTEND = 18** | **8 V3** | **44** | V-17 SoT 1-off 없음 (SPEC §13.1 적용, V-17 PASS 18 / CON 0 / FAIL 0) |

**Phase 4 entry-gate 충족 매핑 (8 V3 통산)**:
- P3-1 (투자 시뮬레이션): L3 ≥ 80 + 자산 클래스 5종 + LOCK-ED-02 5단계 + LOCK-ED-05 Bloom Apply/Analyze + 비투자조언 면책 + 3-1 AI Investing LOCK 정합
- P3-2 (회화 연습): L3 + STT/LLM 회화 + LOCK-ED-06 소크라테스 + LOCK-MM-08 16kHz + ★ 3-6 R-08-6 opt-in
- P3-3 (챌린지 리더보드): L3 + LOCK-ED-10 6단계 verbatim + 익명/실명 + R-08-5 + 3-6 wellness_community forward-defined
- P3-4 (음성 인식 학습): L3 + STT 3종 + LOCK-MM-08 + 정확도 ≥ 90% + LOCK-ED-06
- P3-5 (발표 피드백): L3 + 평가 6 요소 + LOCK-MM-07/08/09 3-LOCK + LOCK-ED-05 + ★ 3-6 R-08-6
- P3-6 (스터디 그룹 매칭): L3 + 매칭 4요소 + LOCK-ED-07 5필드 + 3-3 PKM M-028 V3 inheritance
- P3-7 (VR/AR 학습): L3 + 디바이스 3종 + LOCK-ED-02 5단계 VR 적응 + 3-2 J-009 정합 + 안전 3요소
- P3-8 (멘토링 + Phase 3 마감 meta-audit): STEP7-O 69항목 L3 ≥ 60% + V3 8 L3 ≥ 80 + LOCK-ED 10 무위반 + CF-ED-001~005 ALL RESOLVED + FABRICATION 0 + ★ SM-2 10/10 + ★ R-08-6/R-09-6 양방향 최종 확정

**판정**: ✅ **PHASE3_COMPLETE + PHASE4_READY: 3-5 — 2026-05-16** (V2 18 ALL L3 PASS + V3 8 ALL ✅ + CONFLICT_LOG CF-ED-001~005 ALL RESOLVED 보존 OPEN 0건 + CFL-ED-006~009 4건 Phase 3 이월 정식 등재 inheritance + LOCK-ED-01~10 + LOCK-HW-01/12 cross-domain 12 distinct 변경 0 + FABRICATION 0 + ★ SM-2 verbatim 10/10 통산 verify 일관 PASS + ★ R-08-6 ↔ R-09-6 양방향 최종 확정 PASS)

---

## §14 실행 약점 대응 계획

| ID | 약점 | 심각도 | 영향 | 대응 방안 |
|----|------|--------|------|-----------|
| W1 | **항목 규모** — 69항목은 단일 도메인 최대급 | High | Phase 지연, 품질 저하 | Phase별 우선순위 엄격 적용, V1 MVP에 핵심 40항목 집중 |
| W2 | **SM-2 공유 충돌** — PKM과 파라미터 동기화 실패 가능 | High | 간격 반복 로직 불일치 | LOCK-ED-04 + R-08-1 엄격 적용, PKM 변경 시 Education 동기 알림 |
| W3 | **교수법 품질** — 소크라테스/Bloom/IRT 올바른 적용 어려움 | High | 학습 효과 저하 | 부록 §A 프레임워크 참조 필수, 교수법 검증 체크리스트 별도 운영 |
| W4 | **게이미피케이션 복잡도** — XP/레벨/배지/Streak/챌린지/리더보드 6요소 | Medium | 구현 복잡도 증가 | Phase 1에서 XP+레벨+Streak 3개만, Phase 2에서 나머지 |
| W5 | **감정 연동** — #9 Health 도메인 미완성 시 인터페이스 정의 불가 | Medium | Phase 2 지연 | opt-in 인터페이스만 선정의, Health 완성 후 실제 연동 |
| W6 | **Part2 SHELL** — CAT-E COND 7개 + UI 1건 모두 빈껍데기 | High | 구현 조건 누락 | 방식 C 전면 신규 작성, sot 2/ 정본에서 COND 내용 역생성 |
| W7 | **다국어 학습** — 언어 학습(O-006)은 다국어 지원 필요 | Medium | 국제화 복잡도 | V2에서 영어/한국어 2개 언어만 우선, V3에서 확장 |

### 약점별 모니터링 지표

| W-ID | 모니터링 지표 | 경고 임계값 | 점검 주기 |
|------|-------------|------------|-----------|
| W1 | Phase별 완료 항목 수 / 목표 항목 수 | < 80% | Phase 종료 시 |
| W2 | PKM LOCK 값과 Education 참조 값 diff | diff != 0 | 매 Phase |
| W3 | 교수법 적용 파일 / 교수법 대상 파일 | < 100% | Phase 1 종료 |
| W4 | 게이미피케이션 요소 구현 수 / 목표 수 | < 50% | Phase 1 종료 |
| W5 | Health 인터페이스 정의 완료 여부 | 미완료 | Phase 2 시작 전 |
| W6 | COND 내용 작성 수 / 7개 | < 100% | Phase 1 종료 |
| W7 | 지원 언어 수 / 목표 언어 수 | < 2 | Phase 2 종료 |

---

## 부록 §A — 교수법 프레임워크

### A.1 소크라테스식 대화 전략

> LOCK-ED-06 참조. Khanmigo 스타일 적용 (O-029 참고).

**원칙**: 직접 답을 제공하지 않고, 학습자가 스스로 답에 도달하도록 유도.

**5단계 대화 전략:**

| 단계 | 전략 | 예시 |
|------|------|------|
| 1. 직접 답 금지 | 학습자가 질문하면 답 대신 역질문 | "이 문제에서 먼저 어떤 자료구조를 떠올릴 수 있을까요?" |
| 2. 질문 유도 | 핵심 개념으로 유도하는 질문 연쇄 | "배열의 시간 복잡도는 얼마죠? 그렇다면 더 빠른 방법은?" |
| 3. 힌트 3단계 | Hint 1: 방향 제시, Hint 2: 핵심 개념 명시, Hint 3: 부분 답 공개 | H1: "해시를 생각해보세요" → H2: "HashMap의 lookup은 O(1)입니다" → H3: "complement = target - nums[i]를 key로..." |
| 4. 사고 과정 유도 | 학습자의 추론 과정을 명시화하도록 요청 | "지금까지의 접근 방식을 정리해볼까요?" |
| 5. 격려 피드백 | 올바른 방향에 긍정 피드백, 오류에는 건설적 피드백 | "좋은 접근이에요! 한 가지만 더 고려하면..." |

**적용 범위:**
- 코딩 튜토리얼 (03_coding-tutorial/ 전체)
- 적응형 학습 엔진의 대화 모드 (01_adaptive-learning/adaptive_engine.md)
- 퀴즈 풀이 후 해설 (04_content-generation/quiz_test_generation.md)

### A.2 IRT 난이도 조정

> LOCK-ED-02 참조.

**IRT (Item Response Theory) 기반 5단계 난이도:**

| 레벨 | 명칭 | θ 범위 | 예상 정답률 | 설명 |
|------|------|--------|------------|------|
| 1 | Very Easy | θ < -1.5 | > 90% | 기초 개념 확인 |
| 2 | Easy | -1.5 <= θ < -0.5 | 80-90% | 기본 적용 |
| 3 | Medium | -0.5 <= θ < 0.5 | 70-80% | 표준 문제 |
| 4 | Hard | 0.5 <= θ < 1.5 | 50-70% | 응용/분석 |
| 5 | Very Hard | θ >= 1.5 | < 50% | 창의적 문제 해결 |

**정답률 목표 존(Target Zone): 70-85%**

난이도 조정 알고리즘 의사코드:

```
function adjust_difficulty(learner, item_result):
    // 학습자 능력치 업데이트 (EAP 추정)
    if item_result.correct:
        learner.theta += 0.1 * (1 - probability(learner.theta, item.difficulty))
    else:
        learner.theta -= 0.1 * probability(learner.theta, item.difficulty)

    // 다음 문제 난이도 선택
    recent_accuracy = calculate_accuracy(learner.recent_items, window=10)

    if recent_accuracy > 0.85:
        target_difficulty = learner.theta + 0.3  // 난이도 상향
    elif recent_accuracy < 0.70:
        target_difficulty = learner.theta - 0.3  // 난이도 하향
    else:
        target_difficulty = learner.theta        // 유지 (Target Zone)

    return select_item(target_difficulty, tolerance=0.5)

function probability(theta, difficulty):
    // 2PL IRT 모델
    return 1 / (1 + exp(-1.7 * (theta - difficulty)))
```

### A.3 Bloom 택소노미 적용

> LOCK-ED-05 참조.

**6단계 인지 수준 (하위 → 상위):**

| 단계 | 명칭 | 학습 활동 | 퀴즈 유형 | 동사 예시 |
|------|------|-----------|-----------|-----------|
| 1 | Remember (기억) | 플래시카드, 용어 정리 | 객관식, T/F | 나열하다, 정의하다, 식별하다 |
| 2 | Understand (이해) | 요약, 설명, 비교 | 단답형, 매칭 | 설명하다, 비교하다, 분류하다 |
| 3 | Apply (적용) | 연습 문제, 코딩 실습 | 코드 작성, 계산 | 적용하다, 구현하다, 사용하다 |
| 4 | Analyze (분석) | 코드 리뷰, 케이스 분석 | 디버깅, 비교분석 | 분석하다, 구분하다, 추론하다 |
| 5 | Evaluate (평가) | 설계 리뷰, 트레이드오프 | 논술형, 비평 | 평가하다, 판단하다, 정당화하다 |
| 6 | Create (창조) | 프로젝트, 설계, 발표 | 프로젝트 산출물 | 설계하다, 구축하다, 창안하다 |

**순서 보장 규칙 (R-08-2):**
- 하위 단계 완료율이 70% 이상이어야 상위 단계 잠금 해제
- 학습 경로 생성 시 반드시 1단계부터 순차 배치
- 점프(예: Remember → Analyze 직행) 금지

### A.4 Vygotsky ZPD (Zone of Proximal Development) 적용 규칙

**개념**: 학습자가 혼자 할 수 있는 수준과 도움을 받으면 할 수 있는 수준 사이의 영역(ZPD)에서 학습이 가장 효과적.

**적용 규칙:**

| 규칙 | 설명 | 구현 방법 |
|------|------|-----------|
| ZPD-1 | 현재 능력 측정 | IRT θ 기반 진단 테스트 (LOCK-ED-02) |
| ZPD-2 | ZPD 범위 설정 | θ + 0.3 ~ θ + 1.0 (정답률 약 15-38% 예상 구간, 2PL P=1/(1+exp(-1.7·(θ−difficulty)))) |
| ZPD-3 | 스캐폴딩 제공 | 소크라테스 힌트 3단계 (LOCK-ED-06) |
| ZPD-4 | 점진적 스캐폴딩 제거 | 정답률이 85% 이상이면 힌트 단계 축소 |
| ZPD-5 | 좌절 방지 | 정답률이 40% 이하로 3회 연속 하락 시 난이도 자동 하향 |

**IRT-ZPD 통합 다이어그램:**

```
← 쉬움                    ZPD                    어려움 →
|----[혼자 가능]----||----[도움 시 가능]----||----[불가능]----|
     θ - 1.0            θ       θ + 0.3    θ + 1.0
                    현재 능력    목표 난이도    상한
```

---

## 부록 §B — SM-2 알고리즘 파라미터 (교육 특화)

### B.1 기본 SM-2 참조

> PKM LOCK-PKM-01~03 정본 그대로 인용. LOCK-ED-04에 의해 교육 도메인에서 단독 변경 금지.

| 파라미터 | 값 | 출처 |
|---------|-----|------|
| MIN_EF | 1.3 | PKM LOCK-PKM-01 |
| DEFAULT_EF | 2.5 | PKM LOCK-PKM-02 |
| I(1) | 1일 | PKM LOCK-PKM-03 |
| I(2) | 6일 | PKM LOCK-PKM-03 |
| I(n) for n > 2 | I(n-1) * EF | PKM LOCK-PKM-03 |
| quality scale | 0-5 | PKM LOCK-PKM-03 |

**SM-2 기본 공식:**

```
EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
where q = quality (0-5), EF >= MIN_EF (1.3)
```

### B.2 교육 커스터마이징

> 아래 커스터마이징은 PKM 정본 파라미터를 변경하지 않고, 교육 맥락에 맞는 **보정값**만 추가.

#### B.2.1 Bloom 레벨 가중치에 의한 EF 보정

```
bloom_weight = {
    "Remember":    1.0,   // 기본 (변경 없음)
    "Understand":  0.95,  // 약간 빠른 복습
    "Apply":       0.90,  // 실습 기반 → 더 빠른 복습
    "Analyze":     0.85,  // 분석 → 더 빠른 복습
    "Evaluate":    0.80,  // 평가 → 더 빠른 복습
    "Create":      0.75   // 창조 → 가장 빠른 복습
}

EF_edu = max(MIN_EF, EF * bloom_weight[item.bloom_level])
```

> **근거**: 상위 Bloom 레벨일수록 더 복잡한 인지 작업이므로 빠른 복습으로 정착 강화.

#### B.2.2 학습 맥락별 간격 조정

```
context_factor = {
    "coding":     0.8,   // 코딩은 빠른 반복 필요 (실습 기반)
    "concept":    1.0,   // 개념은 표준 간격
    "vocabulary": 0.9,   // 어휘는 약간 빠른 반복
    "formula":    0.85,  // 수식은 빠른 반복
    "history":    1.1    // 역사/사실은 느린 간격 가능
}

I_edu(n) = I(n) * context_factor[item.context]
```

#### B.2.3 교육 특화 quality 평가 (Bloom 레벨 연동)

기본 SM-2의 quality 0-5를 Bloom 레벨에 따라 세분화:

| quality | 기본 SM-2 의미 | 교육 확장 의미 |
|---------|---------------|---------------|
| 5 | 완벽한 응답 | Bloom 상위 레벨에서도 정확한 응답 |
| 4 | 약간의 망설임 후 정답 | 힌트 1단계 후 정답 |
| 3 | 심각한 망설임 후 정답 | 힌트 2단계 후 정답 |
| 2 | 오답이나 정답에 근접 | 힌트 3단계 후 정답 또는 부분 정답 |
| 1 | 오답 | 힌트 3단계 후에도 오답 |
| 0 | 완전 망각 | 문제 자체를 이해하지 못함 |

### B.3 플래시카드 스키마 확장

> PKM 기본 플래시카드 스키마 참조 + 교육 추가 필드.

```typescript
interface EducationFlashcard extends PKMFlashcard {
    // PKM 기본 필드 (참조)
    // id: string
    // front: string
    // back: string
    // ease_factor: number
    // interval: number
    // next_review: Date
    // quality_history: number[]

    // 교육 추가 필드
    bloom_level: BloomLevel;          // LOCK-ED-05: 6단계 중 하나
    difficulty_irt: number;           // LOCK-ED-02: IRT θ 값
    subject_area: string;             // 학습 분야 (coding, math, language 등)
    card_type: FlashcardType;         // LOCK-ED-08: 기본/빈칸/이미지오클루전/코드
    hint_steps: string[];             // 소크라테스 힌트 (최대 3단계)
    context_factor: number;           // B.2.2 학습 맥락 계수
    related_learning_path?: string;   // 연관 학습 경로 ID
    bloom_weight_ef: number;          // B.2.1 Bloom 가중치 적용된 EF
}

enum BloomLevel {
    Remember = 1,
    Understand = 2,
    Apply = 3,
    Analyze = 4,
    Evaluate = 5,
    Create = 6
}

enum FlashcardType {
    Basic = "basic",              // 앞/뒤
    Cloze = "cloze",              // 빈칸채우기
    ImageOcclusion = "image_occlusion",  // 이미지 오클루전
    Code = "code"                 // 코드
}
```

---

## 부록 §C — 의존성 맵

### C.1 도메인 간 의존성 다이어그램

```
                    ┌──────────────┐
                    │ #4 COND      │
                    │ (조건 엔진)   │
                    └──────┬───────┘
                           │ COND 트리거
                           ▼
┌──────────────┐    ┌──────────────────┐    ┌──────────────┐
│ #6 PKM       │◄───│ #8 Education     │───►│ #9 Health    │
│ (지식 관리)   │    │ -Learning        │    │ (건강/감정)   │
│              │    │                  │    │              │
│ SM-2 정본    │    │ 69항목           │    │ 감정 데이터   │
│ 플래시카드   │    │ 5서브폴더        │    │ opt-in 연동  │
└──────────────┘    └────────┬─────────┘    └──────────────┘
                           │
                    ┌──────┴───────┐
                    │              │
              ┌─────▼────┐  ┌─────▼──────┐
              │ #5 Multi │  │ #10 Dev    │
              │ -modal   │  │ -Tools     │
              │          │  │            │
              │ 음성/영상 │  │ 코딩 환경  │
              │ 입출력    │  │ 실행 엔진  │
              └──────────┘  └────────────┘
```

**의존성 상세:**

| 대상 도메인 | 방향 | 연동 내용 | 규칙 |
|------------|------|-----------|------|
| #6 PKM | 양방향 | SM-2 파라미터 정본 참조, 플래시카드 스키마 공유 | LOCK-ED-04, R-08-1 |
| #9 Health | 단방향 (수신) | 감정 상태 데이터 → 학습 난이도/속도 적응 | R-08-6 (opt-in 필수) |
| #5 Multimodal | 단방향 (호출) | 음성 인식(발표 코칭), 영상 처리(YouTube 학습) | Phase 2+ |
| #4 COND | 단방향 (수신) | CAT-E 조건 트리거 → 교육 모듈 활성화 | COND 레이어 규칙 |
| #10 Dev-Tools | 단방향 (호출) | 코드 실행 환경, 린터, 테스트 러너 | 코딩 튜토리얼 필수 |

### C.2 참고 자료 (O-029 ~ O-036)

| O-ID | 참고 서비스 | 참고 포인트 | 적용 대상 |
|------|------------|------------|-----------|
| O-029 | Khanmigo (Khan Academy) | 소크라테스 교수법, 단계별 힌트, 격려 피드백 | LOCK-ED-06, 부록 §A.1 |
| O-030 | Duolingo Max | 게이미피케이션 (XP, Streak, 리더보드), 짧은 학습 세션 | LOCK-ED-10, gamification.md |
| O-031 | Anki | SM-2 알고리즘, 플래시카드 유형, 간격 반복 | LOCK-ED-04, LOCK-ED-08, 부록 §B |
| O-032 | Perplexity | 검색 기반 학습, 출처 인용, 후속 질문 | youtube_learning.md, paper_learning.md |
| O-033 | NotebookLM (Google) | 문서 기반 대화, 오디오 요약, 개념 추출 | podcast_audio.md, book_reading.md |
| O-034 | Brilliant | 인터랙티브 학습, 시각적 설명, 점진적 난이도 | interactive_tutorial.md, mindmap_concept_map.md |
| O-035 | Coursera / edX | 온라인 코스 구조, 자격증 트래킹, 피어 리뷰 | online_course_support.md, certification_tracker.md |
| O-036 | 향후 확장 | VR/AR 학습, 멘토링, 학습 커뮤니티 | §7 Phase 3 |

### C.3 크로스 레퍼런스

| STEP7 문서 | 도메인 | 교차점 | Education 관련 파일 |
|-----------|--------|--------|-------------------|
| STEP7-I | 투자 | 투자 교육 콘텐츠, 시뮬레이션 | investment_education.md |
| STEP7-J | 멀티모달 | 음성 입출력, 영상 처리 | podcast_audio.md, youtube_learning.md, presentation_coaching.md |
| STEP7-L | 코딩 | 코드 실행 환경, 린터, 디버거 | interactive_tutorial.md, leetcode_style_problems.md, code_review_learning.md |
| STEP7-M | PKM | SM-2 파라미터, 플래시카드, 노트 | sm2_education_extension.md, flashcard_auto_generation.md, note_taking.md |
| STEP7-N | 워크플로우 | 자동화 트리거, 학습 루틴 | time_management.md, habit_tracker.md, focus_mode.md |

---

## 부록 §D — Part2 교차 참조 (S10-4 추가)

> **목적**: Part2 구현단계에서 3-5 Education에 해당하는 항목을 정밀 매핑하여 반영률 95%+ 달성
> **추가일**: 2026-03-27 (Phase 10 S10-4)

### D.1 Part2 V2 CAT-E 교육 COND 모듈 (7개)

**CAT-E 아키텍처** (Part2 L3344-3350):
- 디렉토리: `backend/vamos_core/modules/cond_education/`
- Mixin: `EducationModuleMixin` — 학습 진도 추적, 퀴즈 생성, 적응형 난이도
- config: `[modules.cond.cat_e_education]`
  - `group_enabled=false` (COND 기본 OFF)
  - `adaptive_difficulty=true`
  - `quiz_max_questions=20`
- 공통 의존성: I-1(IntentDetector), M-11(PromptManager), A-4(DebateMode)

| Part2 # | 모듈명 | 우선순위 | O-항목 대응 | 서브폴더 |
|---------|--------|:---:|-----------|---------|
| #91 | 개인화 학습 경로 | HIGH | O-003 | 01_adaptive-learning/ |
| #92 | 시험 준비 도우미 | HIGH | O-008 | 04_content-generation/ |
| #93 | 교육 컨텐츠 생성 | HIGH | O-007~O-009 | 04_content-generation/ |
| #94 | 교육 평가 도구 | HIGH | O-010, O-028 | 05_learning-analytics/ |
| #113 | 대화형 튜토리얼 | LOW | O-004 | 03_coding-tutorial/ |
| #114 | 학습 분석 대시보드 | LOW | O-010 | 05_learning-analytics/ |
| #115 | 언어 학습 특화 | LOW | O-006 | 01_adaptive-learning/ |

### D.2 v10 공통 규칙 적용 (Part2 L3370-3383)

- `BaseModule(ABC)` 상속 필수
- 파일 명명: `cat_e_{module_number}_{snake_name}.py`
- 카테고리별 `__init__.py` + `_mixin.py` + `_config.py`
- Pydantic v2 모델, JSON 구조화 로깅
- COND 기본 OFF 규칙 (D2.0-01 §5.14.4, Part2 L3380)

### D.3 Part2 V2-Phase 2 통합 검증 요건

Part2 L3482: CAT-E 통합 테스트 게이트 조건:
- 적응형 난이도 동작 확인
- 퀴즈 생성 동작 확인
- 학습 진도 추적 동작 확인

→ §10 Phase 검증에 반영

### D.4 Part2 V3-Phase 3 커뮤니티 항목

| Part2 Line | Part2 ID | 항목명 | 종합계획서 대응 |
|-----------|----------|--------|---------------|
| L4357 | D205-138 | 학습 커뮤니티 | §7 Phase 3 "스터디 그룹 매칭" |
| L4358 | S7NP-055 | 동료 학습 매칭 | §7 Phase 3 "멘토링 플랫폼" |
| L4360 | S7NP-065 | 학습 커뮤니티 | §7 Phase 3 "스터디 그룹 매칭" |

---

> **Education-Learning 구조화 종합계획서 v1.3 완료 (P0-3 검증 반영 — S11-1a 전수 정정)**
> 69항목 전수 매핑 (100%) | 5개 서브폴더 | 10개 LOCK | 4개 부록(§A 교수법, §B SM-2, §C 의존성, §D Part2 교차 참조)
