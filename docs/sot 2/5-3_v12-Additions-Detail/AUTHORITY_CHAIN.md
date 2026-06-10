# AUTHORITY_CHAIN — v12 Additions Detail (#19)

> **최종 갱신**: 2026-04-12
> **도메인**: 5-3_v12-Additions-Detail
> **Tier**: 5 — Quality/Cross-cutting (횡단 허브)
> **LOCK 항목 수**: 10개
> **특성**: 자체 LOCK 2개 + 도메인 상속 LOCK 8개

---

## 권한 체계

```
Level 0: VAMOS 마스터 플랜 (PLAN-3.0)
Level 1: D2.0 DESIGN 문서
Level 2: Part2 (§6.1, §6.7, §6.8, §6.10, V2/V3 Phase)  ← v12 항목 존재 선언
Level 3: 각 도메인 sot 2/ 정본 폴더                       ← 구현 상세 정본 (What + How)
Level 4: sot 2/5-3_v12-Additions-Detail/상세명세          ← 통합 기술 명세 (레거시 참조)
Level 5: sot 2/5-3_v12-Additions-Detail/인덱스 허브       ← 매핑 + 추적 (When + Where + Who)
Level 6: 구현 코드
```

> **핵심 원칙**: 이 도메인은 **인덱스 허브**이다.
> - 각 v12 항목의 LOCK은 해당 도메인의 LOCK을 **상속**한다.
> - 이 폴더에서 자체 정의하는 LOCK은 LOCK-V12-01(귀속 원칙)과 LOCK-V12-10(매핑 테이블) 2건뿐이다.
> - 나머지 8건은 상속 참조이며, 원본 변경 시 자동 갱신된다.

---

## LOCK 항목 목록

### 자체 정의 LOCK (2건)

| ID | LOCK 항목 | 정본 출처 | 값 / 기준 | 변경 시 필요 조치 |
|----|----------|----------|----------|-----------------|
| LOCK-V12-01 | v12 항목 도메인 귀속 원칙 | R-19-1 (본 계획서 §4) | "v12 항목은 해당 도메인 sot 2/ 폴더에 원본 유지, 여기는 인덱스만" | 계획서 §4 + 부록 §A 동시 변경 필요 |
| LOCK-V12-10 | 도메인 정본 연결 매핑 테이블 | 계획서 부록 §A | 51건 전체 매핑 (24건 확정 + 27건 잠정) | 항목 추가/삭제/이동 시 부록 §A 갱신 + 해당 도메인 폴더 동시 갱신 (R-19-2) |

### 도메인 상속 LOCK (8건)

| ID | LOCK 항목 | 상속 원본 도메인 | 상속 원본 LOCK | 값 / 기준 | 변경 시 필요 조치 |
|----|----------|----------------|---------------|----------|-----------------|
| LOCK-V12-02 | SM-2 알고리즘 공식 | #6 PKM + #8 Education | PKM SM-2 LOCK (공유) | ease_factor = max(1.3, EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))); interval 계산 규칙 | 원본 도메인(#6 PKM) LOCK 변경 시 자동 상속. #8 Education은 참조만 |
| LOCK-V12-03 | Black-Litterman tau 값 | AI Investing | AI-Invest tau LOCK | tau = 0.025 (스케일링 계수); Omega = diag(P * tau * Sigma * P^T) | 원본 도메인(AI Investing) LOCK 변경 시 자동 상속 |
| LOCK-V12-04 | Factor Investing 6종 정의 | AI Investing | AI-Invest Factor LOCK | Value (PER/PBR), Momentum (3/6/12개월 수익률), Quality (ROE/부채비율), Size (시가총액), Low Volatility (변동성 역수), Dividend (배당수익률) | 원본 도메인(AI Investing) LOCK 변경 시 자동 상속 |
| LOCK-V12-05 | CBT 15가지 인지 왜곡 유형 | #9 Health-Wellness | LOCK-HW-09 관련 | 전부 아니면 전무(All-or-Nothing), 과잉일반화(Overgeneralization), 정신적 필터(Mental Filter), 긍정 격하(Disqualifying the Positive), 성급한 결론(Jumping to Conclusions), 파국화(Catastrophizing), 감정적 추론(Emotional Reasoning), 당위적 진술(Should Statements), 낙인찍기(Labeling), 개인화(Personalization), 독심술(Mind Reading), 점쟁이 오류(Fortune Telling), 비난(Blaming), 공정성 오류(Fallacy of Fairness), 변화 기대(Fallacy of Change), 통제의 오류(Control Fallacy) | 원본 도메인(#9 Health-Wellness) LOCK 변경 시 자동 상속 |
| LOCK-V12-06 | BreathingPattern 4-7-8 기본 패턴 | #9 Health-Wellness | LOCK-HW-07 | 4-7-8 패턴: 흡기 4초 → 유지 7초 → 호기 8초; Box: 4-4-4-4; 횡격막: 4-2-6 | 원본 도메인(#9 Health-Wellness) LOCK 변경 시 자동 상속 |
| LOCK-V12-07 | TemplateSets 3종 구성 | #11 Conversation-A2A + #17 MLOps | 공유 LOCK | TS_CORE (범용 대화), TS_WEB_RESEARCH (웹 검색+요약), TS_CODE (코드 생성+리뷰). 각 세트는 system_prompt + few_shot_examples + output_format + constraints로 구성 | 원본 도메인(#11 A2A 주, #17 MLOps 참조) LOCK 변경 시 자동 상속 |
| LOCK-V12-08 | PortfolioConstraints 최대 비중 | AI Investing | AI-Invest Constraints LOCK | 단일 종목 최대 비중: 10%, 단일 섹터 최대 비중: 30% | 원본 도메인(AI Investing) LOCK 변경 시 자동 상속 |
| LOCK-V12-09 | Zettelkasten 원자적 노트 원칙 | #6 PKM | PKM Zettelkasten LOCK | Luhmann-style 원자적 노트; 1 노트 = 1 아이디어; 링크 타입 4종 (RELATED_TO, SUPPORTS, CONTRADICTS, SUPERSEDES); ID 체계 = 계층적 영숫자 | 원본 도메인(#6 PKM) LOCK 변경 시 자동 상속 |

---

## 도메인 간 LOCK 상속 흐름도

```
#9 Health-Wellness (LOCK-HW-07, HW-08, HW-09)
    ├──→ LOCK-V12-05 (CBT 15유형)
    └──→ LOCK-V12-06 (호흡 패턴)

#6 PKM (SM-2 LOCK, Zettelkasten LOCK)
    ├──→ LOCK-V12-02 (SM-2 알고리즘)  ←─ #8 Education도 참조
    └──→ LOCK-V12-09 (Zettelkasten 원칙)

AI Investing (tau LOCK, Factor LOCK, Constraints LOCK)
    ├──→ LOCK-V12-03 (Black-Litterman tau)
    ├──→ LOCK-V12-04 (Factor 6종)
    └──→ LOCK-V12-08 (Portfolio 비중 제한)

#11 A2A + #17 MLOps (공유 LOCK)
    └──→ LOCK-V12-07 (TemplateSets 3종)

본 계획서 (자체 정의)
    ├──→ LOCK-V12-01 (도메인 귀속 원칙)
    └──→ LOCK-V12-10 (매핑 테이블)
```

---

## LOCK 변경 프로토콜

### 상속 LOCK 변경 시 절차

1. **감지**: 원본 도메인의 AUTHORITY_CHAIN에서 LOCK 값 변경 확인
2. **전파**: 본 AUTHORITY_CHAIN의 해당 LOCK-V12-XX 값을 갱신
3. **영향 분석**: 변경된 LOCK이 참조하는 인덱스 파일 목록 확인
4. **갱신**: 해당 인덱스 파일의 LOCK 참조 값 갱신
5. **기록**: 아래 변경 이력 테이블에 기록

### 자체 LOCK 변경 시 절차

1. **제안**: 변경 사유 + 영향 범위 문서화
2. **검토**: 영향받는 도메인 담당자 확인 (LOCK-V12-10 변경 시 해당 도메인 전부)
3. **승인**: 계획서 §4 거버넌스 규칙에 따라 승인
4. **실행**: LOCK 값 변경 + 관련 인덱스/도메인 폴더 동시 갱신 (R-19-2)
5. **기록**: 아래 변경 이력 테이블에 기록

---

## 도메인 경계

| 인접 도메인 | 본 도메인 소유 | 인접 도메인 소유 |
|------------|--------------|----------------|
| #6 PKM + #8 Education | 인덱스 허브 매핑 (LOCK-V12-10), 도메인 귀속 원칙 (LOCK-V12-01) | SM-2 알고리즘 정본 (#6), Zettelkasten 원칙 (#6) |
| #9 Health-Wellness | v12 항목 통합 추적 (CBT 15유형, 호흡 패턴) | 감정 분류 모델, 호흡법 타이밍 정본 (LOCK-HW-07) |
| AI Investing | v12 항목 통합 추적 (Black-Litterman, Factor 6종, Portfolio 제약) | 투자 전략 상세 정본, 51% Gate |

---

## 변경 이력

| 날짜 | LOCK ID | 변경 내용 | 승인자 |
|------|---------|----------|--------|
| 2026-03-24 | 전체 | 초기 작성 (10개 LOCK 등록: 자체 2개 + 상속 8개) | 도메인 #19 구조화 세션 |
| 2026-04-03 | 전체 | **P0-3 LOCK 상속 검증 완료** — 10건 전수 대조 (자체 2건 PASS + 도메인 8건 대조). 5건 PASS(V12-01,02,04,06,10), 3건 CONDITIONAL(V12-03,07,08), 2건 FAIL(V12-05,09). CONFLICT_LOG C-04~C-08 등록. P0-1/P0-2 산출물 교차확인 24건 PASS. §3.4↔§A.4 정합성 PASS | P0-3 절차 |
| 2026-04-12 | 전체 | **Phase 1 완료 검증** — P1-1 링크 검증 23/24 VALID (95.8%, 게이트 PASS). LOCK 10건 변경 0건. CONFLICT_LOG C-04~C-08 OPEN 5건 유지 (신규 등록 0건). B-2 TemplateSets CONDITIONAL 1건 잔여 | P1 Step 7 횡단 동기화 |

---

## 참조 문서

| 문서 | 위치 | 역할 |
|------|------|------|
| V12_ADDITIONS_DETAIL_구조화_종합계획서.md | 본 폴더 | 마스터 플랜 (§3 권한 체계 상세) |
| V12_ADDITIONS_상세명세.md | 본 폴더 | 535줄 기술 명세 (레거시 참조) |
| CONFLICT_LOG.md | 본 폴더 | 도메인 간 충돌 기록 |
| 각 도메인 AUTHORITY_CHAIN.md | 해당 도메인 폴더 | 상속 원본 LOCK 정의 |
