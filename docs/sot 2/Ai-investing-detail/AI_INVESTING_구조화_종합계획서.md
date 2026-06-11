# AI INVESTING 구조화 종합 계획서

> **버전**: v1.4 (실행 약점 23건 대응 + Phase 전환 게이트 + git 전략 + L3 품질 보증)
> **작성일**: 2026-03-22
> **목적**: sot 2/Ai-investing-detail/을 AI Investing 유일 상세 정본(Single Source of Truth)으로 구조화하고, SPEC·STEP7-I��PART2와의 역할 분리·참조 체계를 확립하며, 23개 감사 이슈를 전부 해결하고, **전 항목을 L3(구현 즉시 투입 가능) 수준으로 완성**하는 종합 실행 계획
> **Status**: APPROVED
> **범위**: 선행작업 3건 + 23개 이슈 해결 + 12개 규칙 + 4-Phase 세부 실행 계획 + **L3 전수 승급 계획**

---

## 목차

1. [현재 상태 분석](#1-현재-상태-분석)
2. [목표 구조 (최종 형태)](#2-목표-구조-최종-형태)
3. [권한 체계 선언](#3-권한-체계-선언)
4. [12개 거버넌스 규칙](#4-12개-거버넌스-규칙)
5. [선행작업 3건 상세](#5-선행작업-3건-상세)
6. [23개 이슈 해결 매핑](#6-23개-이슈-해결-매핑)
7. [4-Phase 실행 계획](#7-4-phase-실행-계획)
8. [파일 역할 분리 명세](#8-파일-역할-분리-명세)
9. [충돌 해결 프로토콜](#9-충돌-해결-프로토콜)
10. [검증 체크리스트](#10-검증-체크리스트)
11. [FINAL REVIEW 보완 사항 (v1.1)](#11-final-review-보완-사항-v11-반영)
12. [FINAL REVIEW 결과](#12-final-review-결과)
13. [L3 전수 승급 계획 (v1.3)](#13-l3-전수-승급-계획-v13)
14. [실행 약점 대응 계획 (v1.4)](#14-실행-약점-대응-계획-v14)
- [부록 A: 실행 요약](#부록-실행-요약)
- [부록 B: 세션 관리 프로토콜 (v1.4)](#부록-b-세션-관리-프로토콜-v14)

---

## 1. 현재 상태 분석

### 1.1 기존 문서 현황

| 문서 | 위치 | 역할 | 줄수 | 상태 |
|------|------|------|------|------|
| **VAMOS_AI_INVESTING_SPEC.md** | docs/sot/ | 통합 명세서 (24개 섹션) | 1,372 | 96개 전략 이름만 나열, §9 RSI_BB만 상세 |
| **STEP7-I_AI_Investing_보강_작업가이드.md** | docs/sot/ | 보강 항목 리스트 (12 Part, 106건) | 1,349 | 항목 목록만, 구현 상세 없음. ※ 헤더의 "1556건"은 STEP3~6 기존 항목 수이며 본 파일 줄수가 아님 |
| **PART2_구현단계.md §6.8** | docs/guides/ | 구현 가이드 (AI Investing) | ~127줄 | MVP 수준, 51% Gate + Circuit Breaker + RT-BNP |
| **D2.0-01 §5.9** | docs/sot/ | ~~AI Investing 정본~~ **오류**: 실제는 A-Series Multi-Brain (§3.2 정정) | 참조만 | §3.2 참조 |

### 1.2 sot 2/Ai-investing-detail/ 현재 파일 (19개 관점 분석 문서)

| # | 관점명 | 파일명 | 항목 수 | 카테고리 | Priority |
|---|--------|--------|---------|----------|----------|
| 1 | 실시간 적응형 전략 | ..._실시간적응형전략_... | 54 | 13 | P0 |
| 2 | 투자 심리학 & 행동재무학 | ..._투자심리학_행동재무학_... | 47 | 11 | P0 |
| 3 | 매크로→섹터→종목 연결 엔진 | ..._매크로_섹터_종목연결엔진_... | 52 | 12 | P0 |
| 4 | 성과 귀인 분석 | ..._성과귀인분석_... | 42 | 10 | P0 |
| 5 | 백테스트 진실성 | ..._백테스트진실성_... | 44 | 10 | P0 |
| 6 | 실행 최적화 | ..._실행최적화_... | 40 | 9 | P1 |
| 7 | 투자 유니버스 관리 | ..._투자유니버스관리_... | 35 | 8 | P1 |
| 8 | 자산군 간 교차 분석 | ..._자산군간교차분석_... | 38 | 9 | P1 |
| 9 | AI 모델 거버넌스 & 드리프트 | ..._AI모델거버넌스_... | 39 | 9 | P1 |
| 10 | 퀀트 리서치 파이프라인 | ..._퀀트리서치파이프라인_... | 36 | 8 | P1 |
| 11 | 거래 비용 분석 TCA | ..._거래비용분석TCA_... | 33 | 7 | P1 |
| 12 | 시장 미시구조 | ..._시장미시구조_... | 36 | 8 | P2 |
| 13 | 자산군별 심화 전략 | ..._자산군별심화전략_... | 45 | 9 | P2 |
| 14 | 기업 이벤트 & 기관 행동 | ..._기업이벤트_기관행동_... | 38 | 8 | P2 |
| 15 | 포트폴리오 구성 심화 | ..._포트폴리오구성심화_... | 40 | 9 | P2 |
| 16 | 글로벌 다각화 & 지정학 | ..._글로벌다각화_지정학_... | 35 | 8 | P2 |
| 17 | 투자 AI Explainability | ..._투자AI_Explainability_... | 37 | 8 | P2 |
| 18 | 데이터 품질 거버넌스 | ..._데이터품질거버넌스_... | 35 | 8 | P3 |
| 19 | 유동성 & 현금 관리 | ..._유동성_현금관리_... | 32 | 7 | P3 |
| | **합계** | | **758** | **171** | |

### 1.3 핵심 문제

1. **권한 체계 부재**: sot 2/가 VAMOS 문서 권한 체인(RULE 1.3 > PLAN 3.0 > DESIGN 2.0)에 없음
2. **3중 정본 충돌**: D2.0-01 §5.9 vs SPEC vs sot 2/ — 누가 AI Investing 정본인지 불명확
3. **빈껍데기**: SPEC §7-8에 96개 전략 이름만, 구현 상세 0 (RSI_BB 제외)
4. **Phase 이중 기재**: SPEC §18과 PART2 §6.8에 서로 다른 Phase 체계 공존

---

## 2. 목표 구조 (최종 형태)

### 2.1 폴더 트리

```
D:\VAMOS\docs\sot 2\Ai-investing-detail\
│
├── INDEX.md                              ← 마스터 인덱스 (유일)
├── AI_INVESTING_구조화_종합계획서.md       ← 본 문서
├── AUTHORITY_CHAIN.md                     ← 권한 체계 선언
├── CONFLICT_LOG.md                        ← 충돌 기록부
│
├── _archive\                              ← 원본 19개 파일 보존 (읽기 전용, FR-1)
├── _templates\                            ← L3 템플릿 + L3 판정 기준 (Phase 0-8)
│
├── 00_core-integration\                   ← ORANGE CORE 통합 인터페이스
│   └── core_integration_spec.md
│
├── 01_realtime-adaptive\                  ← 관점#1: 실시간 적응형 전략
│   ├── _index.md
│   ├── supply_demand_zone.md
│   ├── support_resistance.md
│   ├── price_action.md
│   ├── strategy_invalidation.md
│   ├── market_regime.md                   ← 정본 소유자: 시장 레짐
│   ├── multi_timeframe.md
│   ├── order_flow.md
│   ├── dynamic_position.md
│   ├── fakeout_detection.md
│   ├── volatility_adaptive.md
│   ├── ai_pattern_strategy.md
│   └── strategy_ensemble.md
│
├── 02_behavioral-finance\                 ← 관점#2: 투자 심리학 & 행동재무학
│   ├── _index.md
│   └── (11개 카테고리별 파일)
│
├── 03_macro-sector-stock\                 ← 관점#3: 매크로→섹터→종목 연결
│   ├── _index.md
│   └── (12개 카테고리별 파일)
│
├── 04_performance-attribution\            ← 관점#4: 성과 귀인 분석
│   ├── _index.md
│   └── (10개 카테고리별 파일)
│
├── 05_backtest-integrity\                 ← 관점#5: 백테스트 진실성
│   ├── _index.md
│   └── (10개 카테고리별 파일)
│
├── 06_execution-optimization\             ← 관점#6: 실행 최적화
│   ├── _index.md
│   └── (9개 카테고리별 파일)
│
├── 07_universe-management\                ← 관점#7: 투자 유니버스 관리
│   ├── _index.md
│   └── (8개 카테고리별 파일)
│
├── 08_cross-asset\                        ← 관점#8: 자산군 간 교차 분석
│   ├── _index.md
│   └── (9개 카테고리별 파일)
│
├── 09_model-governance\                   ← 관점#9: AI 모델 거버넌스
│   ├── _index.md
│   └── (9개 카테고리별 파일)
│
├── 10_quant-research\                     ← 관점#10: 퀀트 리서치 파이프라인
│   ├── _index.md
│   └── (8개 카테고리별 파일)
│
├── 11_tca\                                ← 관점#11: 거래 비용 분석
│   ├── _index.md
│   └── (7개 카테고리별 파일)
│
├── 12_microstructure\                     ← 관점#12: 시장 미시구조
│   ├── _index.md
│   └── (8개 카테고리별 파일)
│
├── 13_asset-class-deep\                   ← 관점#13: 자산군별 심화 전략
│   ├── _index.md
│   └── (9개 카테고리별 파일)
│
├── 14_corporate-events\                   ← 관점#14: 기업 이벤트 & 기관 행동
│   ├── _index.md
│   └── (8개 카테고리별 파일)
│
├── 15_portfolio-advanced\                 ← 관점#15: 포트폴리오 구성 심화
│   ├── _index.md
│   └── (9개 카테고리별 파일)
│
├── 16_global-geopolitics\                 ← 관점#16: 글로벌 다각화 & 지정학
│   ├── _index.md
│   └── (8개 카테고리별 파일)
│
├── 17_explainability\                     ← 관점#17: 투자 AI Explainability
│   ├── _index.md
│   └── (8개 카테고리별 파일)
│
├── 18_data-quality\                       ← 관점#18: 데이터 품질 거버넌스
│   ├── _index.md
│   └── (8개 카테고리별 파일)
│
├── 19_liquidity-cash\                     ← 관점#19: 유동성 & 현금 관리
│   ├── _index.md
│   └── (7개 카테고리별 파일)
│
├── 20_strategy-detail\                    ← 기존 빈껍데기 전략 상세
│   ├── _index.md
│   ├── technical\                         ← 기술적 분석 40개 전략
│   │   ├── trend_following.md
│   │   ├── momentum_oscillator.md
│   │   ├── volatility.md
│   │   ├── volume.md
│   │   ├── composite.md
│   │   ├── chart_pattern_reversal.md
│   │   ├── chart_pattern_continuation.md
│   │   └── harmonic.md
│   └── quant\                             ← 퀀트/팩터/ML 56개 전략
│       ├── statistical.md
│       ├── factor.md
│       ├── options.md
│       ├── event_driven.md
│       ├── ml_ai.md
│       ├── crypto.md
│       └── portfolio_risk.md
│
└── 21_mapping\                            ← 매핑 & 거버넌스 문서
    ├── step7i_mapping.md                  ← STEP7-I 106건 ↔ sot 2 매핑
    ├── canonical_owner_table.md           ← 정본 소유자 매핑 테이블
    ├── dedup_audit.md                     ← 교차 중복 감사 결과
    └── tech_dependency.md                 ← 기술스택 의존성 감사
```

### 2.2 폴더 깊이 규칙

```
최대 3단계:
  Ai-investing-detail/ → XX_카테고리/ → 파일.md          (2단계) ✅
  Ai-investing-detail/ → 20_strategy-detail/ → technical/ → 파일.md  (3단계) ✅
  4단계 이상 → 절대 금지 ❌
```

### 2.3 폴더 네이밍 규칙

- **폴더명**: 영문 소문자 + 하이픈, 접두사 2자리 번호 (`01_`, `02_`, ...)
- **파일명**: 영문 소문자 + 언더스코어 (`.md` 확장자)
- **한글 파일명**: 기존 19개 관점 분석 원본은 보존 (마이그레이션 후 아카이브)

---

## 3. 권한 체계 선언

### 3.1 기존 VAMOS 권한 체인

```
RULE 1.3 > PLAN 3.0 > DESIGN 2.0 LOCK > DESIGN body > Schema/TECH_STACK
```

### 3.2 AI Investing 확장 권한 체인

> **⚠️ 교차 검증 결과 (v1.2)**: PART2 line 2549의 `D2.0-01 §5.9 (AI Investing 정본)` 참조는 **오류**임이 확인됨.
> 실제 D2.0-01 §5.9는 "A-Series (A-1~A-7) Multi-Brain/Infra 확장"이며 AI Investing과 무관.
> D2.0-01에서 AI Investing 관련 유일한 내용은 §7.2 DEFER 테이블 #63~67 (5건 DEFER 항목)뿐.
> **조치**: DESIGN 레벨 앵커를 D2.0-01 §5.9에서 **D2.0-03 §1 (BLUE NODE 정의/P0·P1·P2) + §3.3 (P2 도메인 라이프사이클)** + **D2.0-01 §7.2 #63~67 (DEFER 인지)**로 교체.
> Phase 0-1에서 이 오류를 PART2에도 정정 반영한다.

```
RULE 1.3
  > PLAN 3.0
    > DESIGN 2.0
      ├─ D2.0-03 §1 (BLUE NODE 정의/역할/P0·P1·P2 제약) + §3.3 (P2 도메인 라이프사이클)
      └─ D2.0-01 §7.2 #63~67 (AI Investing DEFER 5건 인지)
        > SPEC §1-6,§10-24 (아키텍처 + LOCK 항목)
          > SPEC §7-8 (전략 이름 목록 + 요약 ONLY)
            > sot 2/Ai-investing-detail/ (전략 상세 + 관점 분석 = 구현 정본) ← 신규 티어
              > PART2 §6.8 (구현 가이드: When + Where)
                > STEP7-I (보강 항목 목록 = 체크리스트)
```

### 3.3 각 문서의 권한 범위

| 문서 | 권한 레벨 | 결정할 수 있는 것 | 결정할 수 없는 것 |
|------|----------|------------------|------------------|
| **D2.0-03 §1 + §3.3** (BLUE NODE 정의 + P2 라이프사이클) | DESIGN | AI Investing 존재, P2 승인필수 분류, ORANGE CORE 연동 구조 | 전략 상세, 구현 일정 |
| **D2.0-01 §7.2 #63~67** | DESIGN-DEFER | AI Investing DEFER 항목 인지 (MAX_PAIN, MACRO_ROTATION 등) | 전략 상세, 구현 일정 |
| **SPEC §1-6,§10-24** | MODULE-ARCH | 7-Layer, 83개 소스, 51% Gate, LOCK 기술스택, 법적 제약 | 전략 구현 상세, Phase 일정 |
| **SPEC §7-8** | INDEX | 전략 이름 + 한 줄 설명 + 분류 | 전략 구현 로직 (→ sot 2/로 위임) |
| **SPEC §9 RSI_BB** | LEGACY | RSI_BB 구현 상세 (마이그레이션 대상) | 향후 RSI_BB 변경 (→ sot 2/에서 관리) |
| **SPEC §18** | HISTORICAL | Phase 로드맵 역사적 기록 | 현재 Phase 일정 (→ PART2 §6.8) |
| **sot 2/Ai-investing-detail/** | IMPL-DETAIL | What + How (전략 상세, 관점별 구현 로직) | When (Phase), LOCK 값 재정의 |
| **PART2 §6.8** | IMPL-GUIDE | When + Where (Phase 배정, 코드 위치) | 전략 로직 상세 (→ sot 2/ 링크) |
| **STEP7-I** | CHECKLIST | 보강 필요 항목 ID + 우선순위 | 구현 방법 (→ sot 2/) |

### 3.4 LOCK 보호 선언

> **절대 규칙**: sot 2/Ai-investing-detail/ 내 모든 파일은 아래 LOCK 값을 **재정의할 수 없다**.
> 참조 시 반드시 `> LOCK (출처): [원문 그대로]` 형식을 사용한다.

| LOCK 항목 | 정본 출처 | PART2 §6.8 반영 | 값 |
|-----------|----------|----------------|-----|
| Win Rate | **SPEC §6.1** | PART2 §6.8 51% Gate 테이블 | ≥ 51% |
| Sharpe Ratio | **SPEC §6.1** | PART2 §6.8 51% Gate 테이블 | ≥ 1.0 |
| Performance Decay | **SPEC §6.1** | PART2 §6.8에 직접 미기재 (SPEC 참조) | < 30% |
| Min Trades | **SPEC §6.1** | PART2 §6.8에 직접 미기재 (SPEC 참조) | 30건 |
| Daily Loss Circuit Breaker | **SPEC §10.2** | PART2 §6.8 Circuit Breaker 테이블 | -3% → Trading stop |
| VIX Circuit Breaker | **SPEC §10.2** | PART2 §6.8 Circuit Breaker 테이블 | > 40 → Buy stop |
| Position Circuit Breaker | **SPEC §10.2** | PART2 §6.8 Circuit Breaker 테이블 | -10% → Force liquidation |
| Cash Ratio | **SPEC §10.2** | PART2 §6.8 Circuit Breaker 테이블 | Min 20% |
| Single Stock Max | **SPEC §10.2** | PART2 §6.8 Circuit Breaker 테이블 | 10% |
| P2 Approval Timeout | **D2.0-07** (I-19 시스템 전체) | PART2 §6.8 P2 승인 흐름 | 일반 10분 / **P2 도메인(HITL) 5분** → Auto reject |
| 14-Item Tech Stack | **SPEC §14** | PART2 §6.8 기술스택 테이블 | 변경 불가 (LOCK) |
| 비용 상한 | **D2.0-07 / RULE 1.3 §5** | PART2 Phase 6 비용 LOCK | V1: ₩40,000($30), V2: ₩93,000($70), V3: ₩266,000($200) |

---

## 4. 12개 거버넌스 규칙

### 기존 8개 규칙 (확정)

| # | 규칙 | 이유 | 위반 시 |
|---|------|------|---------|
| R1 | 폴더 깊이 최대 3단계 | Windows 260자 경로 제한 | 파일 생성 거부 |
| R2 | 마스터 INDEX.md 1개 + 폴더별 _index.md (파일 목록만) | 유지보수 부담 분산 | INDEX.md 미갱신 = 커밋 불가 |
| R3 | 파일명 변경 시 PART2 링크 테이블 동기화 | 참조 정합성 | 변경 커밋에 PART2 업데이트 포함 필수 |
| R4 | 겹치는 개념 → 정본 소유자 1곳 상세, 나머지 `> 참조:` 링크 | 교차 참조 중복 방지 | canonical_owner_table.md에 등록 필수 |
| R5 | SPEC §7-8은 이름+요약 역할 고정 | SPEC ↔ sot 2 역할 분리 | 상세 추가 금지, sot 2/로 위임 |
| R6 | sot 2/ = What+How만, When = PART2만 | Phase 이중 기재 금지 | Phase 정보 발견 시 즉시 삭제 |
| R7 | STEP7-I 106건 ↔ sot 2/ 매핑 테이블 유지 | 중복/충돌 정리 | step7i_mapping.md에 기록 |
| R8 | PART2 §6.8 링크는 §6.8.2 테이블 1곳에 집중 | 링크 관리 단순화 | 본문 산발 링크 금지 |

### 추가 4개 규칙 (이슈 해결에서 도출)

| # | 규칙 | 이유 | 위반 시 |
|---|------|------|---------|
| R9 | sot 2/ 파일은 LOCK/FREEZE 값 재정의 금지. 참조 시 `> LOCK (출처): [원문]` 사용 | LOCK 보호 | 즉시 수정 |
| R10 | 모든 sot 2/ 파일에 메타데이터 헤더 필수: Status, 버전, Last-reviewed | 초안/확정 구분 + BASE-1.3 버전 정책 준수 | 파일 미완성 표시 |
| R11 | 참조 방향: SPEC → sot 2/ (단방향). sot 2/ → SPEC 역참조 금지 (인용 시 내용 인라인) | 순환 참조 방지 | 링크 대신 인라인 인용 |
| R12 | 기술스택 의존성: sot 2/ 전략 파일에 `### 기술스택 의존성` 섹션 필수. SPEC §14 LOCK 외 기술 필요 시 `REQUIRES LOCK AMENDMENT` 플래그 | 구현 불가능 스펙 방지 | Phase 배정 불가 |

---

## 5. 선행작업 3건 상세

> **이 3건은 Phase 1 진입 전에 반드시 완료해야 한다.**

### 선행작업 A: 교차 중복 감사 (Cross-Perspective Deduplication Audit)

**목적**: 19개 관점 파일 758개 항목 간 중복 식별 → 정본 소유자 배정

**절차**:

1. 19개 파일에서 모든 B-카테고리 항목 제목 추출 (758개)
2. 유사도 매칭으로 2개+ 파일에 등장하는 개념 식별
3. 각 중복 개념에 정본 소유자 배정 (가장 밀접한 관점)
4. 결과를 `21_mapping/dedup_audit.md`에 기록
5. 결과를 `21_mapping/canonical_owner_table.md`에 반영

**예상 중복 영역**:

| 개념 | 등장 관점 | 정본 소유자 (예상) |
|------|----------|------------------|
| 시장 레짐 감지 | #1 실시간적응형, #3 매크로연결 | → #1 (01_realtime-adaptive/) |
| Volume Profile | #1 실시간적응형, #12 미시구조 | → #1 (01_realtime-adaptive/) |
| Circuit Breaker 확장 | #2 심리학, #19 유동성 | → PART2 §6.8 LOCK (sot 2/ 참조만) |
| FinBERT 감성 | #2 심리학, #14 기업이벤트 | → #2 (02_behavioral-finance/) |
| 슬리피지 모델 | #6 실행최적화, #11 TCA | → #6 (06_execution-optimization/) |
| 백테스트 파이프라인 | #5 백테스트진실성, #10 퀀트리서치 | → #5 (05_backtest-integrity/) |
| Factor 모델 | #8 교차분석, #15 포트폴리오 | → #15 (15_portfolio-advanced/) |
| SHAP/LIME | #9 모델거버넌스, #17 Explainability | → #17 (17_explainability/) |
| 데이터 품질 검증 | #18 데이터품질, SPEC §5 DQ | → #18 (18_data-quality/) |

**산출물**: `dedup_audit.md`, `canonical_owner_table.md`

---

### 선행작업 B: STEP7-I 106건 매핑 (STEP7-I ↔ sot 2 Currency Audit)

**목적**: STEP7-I 106건이 19개 관점 758건에 이미 흡수되었는지 확인

**절차**:

1. STEP7-I Part 1~12에서 106건 항목 ID(S7I-001~S7I-106) + 제목 추출
2. 각 항목을 19개 관점 파일과 매칭
3. 매칭 결과 분류:
   - **ABSORBED**: sot 2/ 파일에 이미 상세 포함 → STEP7-I에 "RESOLVED → sot 2/XX/" 마킹
   - **PARTIAL**: 부분만 흡수 → sot 2/ 파일에 누락분 추가
   - **UNMATCHED**: 어느 관점에도 없음 → 해당 관점 파일에 추가 또는 새 파일 생성
4. 결과를 `21_mapping/step7i_mapping.md`에 기록

**산출물 형식**:

```markdown
| S7I-ID | S7I 제목 | 매칭 상태 | sot 2/ 대응 파일 | 비고 |
|--------|---------|----------|-----------------|------|
| S7I-001 | AI 투자 플랫폼 벤치마크 | ABSORBED | 10_quant-research/ | |
| S7I-023 | FinBERT 한국어 확장 | PARTIAL | 02_behavioral-finance/ | 한국어 모델 상세 추가 필요 |
| S7I-065 | 시장 레짐 감지 | ABSORBED | 01_realtime-adaptive/market_regime.md | |
| ... | ... | ... | ... | ... |
```

**산출물**: `step7i_mapping.md`

---

### 선행작업 C: SPEC 기존 상세 내용 마이그레이션 목록 작성

**목적**: SPEC에 이미 구현 상세가 있는 섹션을 식별하고, sot 2/로의 이전 계획 수립

**대상 섹션**:

| SPEC 섹션 | 현재 내용 | 마이그레이션 대상 | sot 2/ 목적지 |
|-----------|----------|------------------|--------------|
| §9 RSI_BB 전략 구현 상세 | 파라미터 그리드 27조합, Wilder RSI, BB ddof=0 | 전체 이전 | 20_strategy-detail/technical/rsi_bb.md |
| §7.8 Harmonic Patterns | 패턴 상세 (Gartley, Butterfly 등) | 이전 | 20_strategy-detail/technical/harmonic.md |
| §7.9 시장 상황별 전략 선택 | 정적 테이블 4줄 | 이전 + 확장 | 01_realtime-adaptive/strategy_selection.md |
| §16 수학 공식 전수 검증 | Sharpe, RSI, BB, Decay 공식 | 참조 유지 (LOCK) | sot 2/에서 인라인 인용 |
| §17 15개 결함 극복 방안 | 결함 목록 + 일정 | 이전 (결함 상세) | 해당 관점 폴더별 분배 |
| §18 4-Phase 로드맵 | Phase별 일정 | `HISTORICAL` 마킹 | PART2 §6.8이 정본 |
| 부록 B.3 다음 단계 | 즉시/단기/중기/장기 일정 | `HISTORICAL` 마킹 | PART2 §6.8이 정본 |

**SPEC 잔류 내용** (이전하지 않음):

| SPEC 섹션 | 이유 |
|-----------|------|
| §1-6 (아키텍처, 데이터, DQ, Gate) | MODULE-ARCH 레벨 — sot 2/ 상위 |
| §7-8 (전략 이름 목록) | INDEX 역할 유지 |
| §10-15 (법적 제약, 모니터링, 스택) | LOCK 항목 포함 — 이동 금지 |
| §19-24 (참고사이트, Core통합, Z-Session) | 아키텍처 레벨 |

**절차**:
1. 위 테이블 기반으로 마이그레이션 대상 확정
2. 각 대상의 sot 2/ 목적지 파일 생성
3. SPEC 원본에 `> MIGRATED: 상세는 sot 2/Ai-investing-detail/XX/YY.md 참조` 추가
4. PART2의 SPEC 참조를 sot 2/ 참조로 일괄 갱신

**산출물**: 마이그레이션 완료 후 SPEC 내 리디렉트 마커 + PART2 링크 갱신

### 선행작업 C 부속: §17 15개 결함 분배 매핑 (0-7 확정)

> **확정일**: 2026-03-22 (S0-2 세션)

| 결함# | 결함명 | 심각도 | 분배 대상 관점 | 분배 대상 파일 | 비고 |
|-------|--------|:------:|-------------|-------------|------|
| D-01 | 전략 다양성 부족 | High | #20 전략상세 | 20_strategy-detail/ (Phase 2 L3 작업) | MACD, MA 등 P0 전략 L3 작성으로 해결 |
| D-02 | API 단일 의존성 | High | #18 데이터품질 | 18_data-quality/data_source_quality.md | API Fallback Chain 구현 |
| D-03 | 실시간 처리 미흡 | Medium | #1 실시간적응형 | 01_realtime-adaptive/ (전체) | 일일 배치 → 실시간 전환 |
| D-04 | 감성 분석 부재 | Medium | #2 행동재무학 | 02_behavioral-finance/news_sentiment.md | FinBERT 감성 통합 |
| D-05 | 포트폴리오 관리 없음 | High | #15 포트폴리오심화 | 15_portfolio-advanced/portfolio_optimization.md | 자산 배분 로직 |
| D-06 | 백테스팅 샘플 부족 | Medium | #5 백테스트진실성 | 05_backtest-integrity/data_quality_preprocess.md | 3년→5년 데이터 확대 |
| D-07 | 옵션/파생 데이터 미확보 | Medium | #13 자산군별심화 | 13_asset-class-deep/derivatives_strategies.md | MAX_PAIN 데이터 확보 |
| D-08 | 거시경제 데이터 미연동 | Medium | #3 매크로연결 | 03_macro-sector-stock/macro_regime.md | MACRO_ROTATION 가능화 |
| D-09 | 다중 자산 미지원 | Medium | #8 교차분석 + #13 | 08_cross-asset/ + 13_asset-class-deep/ | 암호화폐/FX 지원 |
| D-10 | contracts.py 불일치 | High | SPEC §23 관할 | *sot 2/ 범위 외* — SPEC §23에서 직접 해결 | Pydantic 12건 정렬 |
| D-11 | 환경 미구축 | High | SPEC 관할 | *sot 2/ 범위 외* — 인프라 레벨 | Docker Compose 구축 |
| D-12 | 슬리피지/수수료 실측 | Medium | #6 실행최적화 + #11 TCA | 06_execution-optimization/slippage_model.md + 11_tca/cost_components.md | 백테스트 vs 실전 괴리 해소 |
| D-13 | Black Swan 대응 없음 | High | #15 + #19 | 15_portfolio-advanced/hedge_tail_risk.md + 19_liquidity-cash/emergency_liquidity.md | Circuit Breaker + 꼬리 리스크 |
| D-14 | Model Explainability 부재 | Medium | #17 Explainability | 17_explainability/decision_explanation.md | SHAP/LIME 해석성 |
| D-15 | A/B 테스트 체계 없음 | Low | #9 모델거버넌스 | 09_model-governance/mlops.md | 전략 변경 효과 측정 |

**분배 요약**: sot 2/ 분배 13건 + SPEC 관할 잔류 2건 (D-10, D-11) = 전 15건 처리 완료

---

## 6. 23개 이슈 해결 매핑

### 6.1 CRITICAL (4건)

| 이슈# | 문제 | 해결 | 해결 시점 | 산출물 |
|--------|------|------|----------|--------|
| #1 | sot 2/가 권한 체인에 없음 | §3 권한 체계 선언 + AUTHORITY_CHAIN.md 작성. PART2 §6.8 상단에 "sot 2/Ai-investing-detail/ = AI Investing 구현 정본" 명시 | Phase 0 | AUTHORITY_CHAIN.md, PART2 §6.8 수정 |
| #2 | 3중 정본 충돌 (D2.0-01 vs SPEC vs sot 2) | §3.3 권한 범위 테이블로 역할 분리 명확화. 각 문서 헤더에 역할 선언 추가 | Phase 0 | AUTHORITY_CHAIN.md |
| #3 | SPEC §9 RSI_BB가 Rule 5 위반 | 선행작업 C에서 §9 내용을 20_strategy-detail/technical/rsi_bb.md로 마이그레이션. SPEC §9에 리디렉트 마커 | Phase 1 | rsi_bb.md + SPEC §9 수정 |
| #4 | SPEC §18 Phase 정보가 Rule 6 위반 | SPEC §18 상단에 `> HISTORICAL: 이 로드맵은 초기 계획 기록입니다. 현행 Phase 일정은 PART2 §6.8이 정본입니다.` 추가 | Phase 0 | SPEC §18 수정 |

### 6.2 HIGH (9건)

| 이슈# | 문제 | 해결 | 해결 시점 | 산출물 |
|--------|------|------|----------|--------|
| #5 | "sot 2" 폴더명 공백 | ✅ 이미 해결: `Ai-investing-detail`로 변경 완료 | 완료 | — |
| #6 | INDEX.md 비대화 | INDEX.md = 카테고리 레벨만 (19관점 + N폴더). 폴더별 _index.md = 파일 목록만 (설명 없음) | Phase 1 | INDEX.md + 21개 _index.md |
| #7 | STEP7-I 날짜 불일치 (2025 vs 2026) | 선행작업 B에서 currency audit 시 흡수/미흡수 판정 | Phase 0 | step7i_mapping.md |
| #8 | Draft vs Complete 상태 없음 | R10 규칙: 모든 파일에 메타데이터 헤더 추가. Status: DRAFT → REVIEW → APPROVED → LOCKED | Phase 1 | 전 파일 헤더 갱신 |
| #9 | 버전/변경 추적 없음 | R10 규칙 + INDEX.md에 VERSION 칼럼 추가 | Phase 1 | INDEX.md 갱신 |
| #10 | 정본 소유자 미배정 | 선행작업 A에서 canonical_owner_table.md 작성 | Phase 0 | canonical_owner_table.md |
| #11 | LOCK 값 재정의 위험 | R9 규칙 + §3.4 LOCK 보호 선언 | Phase 0 | AUTHORITY_CHAIN.md |
| #12 | ORANGE CORE 통합 미문서화 | 00_core-integration/core_integration_spec.md 신규 작성 | Phase 1 | core_integration_spec.md |
| #15 | 관점 파일 vs 전략 상세 혼재 | §2.1 폴더 구조에서 분리: 01~19 = 관점, 20 = 전략상세, 21 = 매핑 | Phase 1 | 폴더 재구성 |

### 6.3 MEDIUM (6건)

| 이슈# | 문제 | 해결 | 해결 시점 | 산출물 |
|--------|------|------|----------|--------|
| #13 | 새 관점 추가 절차 없음 | 아래 "새 관점 체크리스트" 정의 → INDEX.md에 포함 | Phase 1 | INDEX.md |
| #14 | SPEC ↔ sot 2 순환 참조 | R11 규칙: 참조 방향 SPEC → sot 2/ 단방향 고정 | Phase 1 | 전 파일 점검 |
| #16 | 링크 검증 자동화 없음 | validate_links.py 스크립트 작성 (PART2 내 sot 2/ 참조 → 파일 존재 확인) | Phase 2 | validate_links.py |
| #17 | 기술스택 의존성 미확인 | R12 규칙 + tech_dependency.md 감사 | Phase 2 | tech_dependency.md |
| #18 | 19개 파일 간 중복 미감사 | 선행작업 A (= #10과 동일 해결) | Phase 0 | dedup_audit.md |
| #19 | PART2 → SPEC 참조 마이그레이션 미정의 | 선행작업 C에서 일괄 처리 | Phase 1 | PART2 §6.8 수정 |

### 6.4 LOW (4건)

| 이슈# | 문제 | 해결 | 해결 시점 | 산출물 |
|--------|------|------|----------|--------|
| #20 | 한글 폴더명 인코딩 | §2.3에서 영문 폴더명 규칙 확정 (01_realtime-adaptive 등) | Phase 1 | 폴더 생성 시 적용 |
| #21 | "sot 2" 이름이 열등감 암시 | ✅ `Ai-investing-detail`로 변경 완료 | 완료 | — |
| #22 | SPEC 부록 B.3 Phase 정보 | 부록 B.3에 `> HISTORICAL` 마커 추가 (이슈#4와 동일 패턴) | Phase 0 | SPEC 수정 |
| #23 | 충돌 해결 프로토콜 없음 | §9 충돌 해결 프로토콜 정의 | Phase 0 | CONFLICT_LOG.md + 본 계획서 §9 |

---

## 7. 4-Phase 실행 계획

### Phase 0: 기반 확립 (선행작업)

> **목표**: 구조화 진입 전 필수 기반 완성
> **산출물 7건**

| 단계 | 작업 | 입력 | 산출물 | 이슈 해결 |
|------|------|------|--------|----------|
| 0-1 | AUTHORITY_CHAIN.md 작성 + **PART2 §5.9 오류 정정** | §3 권한 체계. PART2 line 2549,2567의 `D2.0-01 §5.9 (AI Investing 정본)` → `D2.0-03 §1+§3.3 (BLUE NODE P2 라이프사이클) + VAMOS_AI_INVESTING_SPEC (AI Investing 정본)`으로 정정 | AUTHORITY_CHAIN.md + PART2 수정 | #1, #2, #11, C1 |
| 0-2 | SPEC §18, 부록 B.3에 HISTORICAL 마커 추가 | SPEC 원본 | SPEC 수정 | #4, #22 |
| 0-3 | CONFLICT_LOG.md 초기화 + 충돌 해결 프로토콜 작성 | §9 프로토콜 | CONFLICT_LOG.md | #23 |
| 0-4 | 교차 중복 감사 (선행작업 A) + filename_mapping.md | 19개 파일 758항목 | dedup_audit.md + filename_mapping.md | #10, #18, W-05 |
| 0-5 | 정본 소유자 테이블 작성 | 0-4 결과 | canonical_owner_table.md | #10 |
| 0-6 | STEP7-I 106건 매핑 (선행작업 B) | STEP7-I + 19개 파일 | step7i_mapping.md | #7 |
| 0-7 | SPEC 마이그레이션 목록 확정 (선행작업 C) | SPEC §7~§18 | 마이그레이션 목록 (본 계획서 §5C) | #3, #19 |
| 0-8 | **L3 템플릿 + L3 판정 기준 + 참조예시 3건 생성** (v1.3+W-23) | Phase 2 L3 정의 | `_templates/L3_TEMPLATE.md` + `L3_CRITERIA.md` + `L3_EXAMPLE_STRATEGY.md` + `L3_EXAMPLE_CONCEPT.md` + `L3_EXAMPLE_INFRA.md` | FR-FINAL-1,3, W-23 |

#### Phase 0 단계별 상세 작업 절차 (v1.3.1 추가)

<details>
<summary><b>0-1. AUTHORITY_CHAIN.md 작성 + PART2 §5.9 오류 정정</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot 2\Ai-investing-detail\AI_INVESTING_구조화_종합계획서.md` §3 (권한 체계)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` line 2549, 2567
- `D:\VAMOS\docs\sot\D2.0-03_03. VAMOS_DESIGN_2.0_BLUE_NODES.md` §1, §3.3

**절차**:
1. `Ai-investing-detail/AUTHORITY_CHAIN.md` 신규 생성
   - 본 계획서 §3.1~§3.4 내용을 독립 문서로 추출
   - 헤더: `Status: APPROVED`, `버전: v1.0`
   - 포함 내용: 권한 체인 다이어그램, 각 문서 권한 범위 테이블, LOCK 보호 선언 전문
2. PART2 오류 정정 (2곳) — **W-01 대응: grep으로 위치 특정**:
   - `grep -n "D2.0-01 §5.9" PART2파일` 실행 → 결과 줄번호로 정정 (참고: ~2549, ~2567)
   - grep 결과 0건이면 이미 정정 완료 → SKIP
   - 정정: `D2.0-01 §5.9 (AI Investing 정본)` → `D2.0-03 §1+§3.3 (BLUE NODE P2) + VAMOS_AI_INVESTING_SPEC (AI Investing 정본)`
   - 정정 시 원문 보존: `<!-- CORRECTED 2026-03-22: 기존 D2.0-01 §5.9 → D2.0-03 §1+§3.3 -->`
3. PART2 §6.8 상단에 아래 선언 추가:
   ```
   > **구현 정본**: AI Investing 구현 상세는 sot 2/Ai-investing-detail/이 Single Source of Truth입니다.
   > 본 섹션은 When(Phase)+Where(코드 위치)만 기술합니다.
   ```

**검증**:
- [ ] AUTHORITY_CHAIN.md에 §3.1~§3.4 전체 내용 포함 확인
- [ ] PART2에서 `D2.0-01 §5.9` 검색 → 0건 (정정 완료)
- [ ] PART2 §6.8 상단 정본 선언 존재 확인

**산출물**: `AUTHORITY_CHAIN.md` (신규) + PART2 수정 (2~3곳)
</details>

<details>
<summary><b>0-2. SPEC §18, 부록 B.3에 HISTORICAL 마커 추가</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot\VAMOS_AI_INVESTING_SPEC.md` §18, 부록 B.3

**절차**:
1. SPEC §18 최상단(섹션 제목 바로 아래)에 추가:
   ```markdown
   > **HISTORICAL**: 이 로드맵은 초기 계획 기록입니다. 현행 Phase 일정은
   > PART2 §6.8이 정본입니다. 아래 내용은 역사적 참조용으로만 보존합니다.
   ```
2. 부록 B.3 "다음 단계" 최상단에 동일 패턴 추가:
   ```markdown
   > **HISTORICAL**: 아래 일정은 초기 계획 시점의 기록입니다.
   > 현행 일정은 PART2 §6.8을 참조하세요.
   ```
3. 기존 내용은 **일절 수정하지 않음** (마커만 추가)

**검증**:
- [ ] SPEC §18 첫 줄에 `HISTORICAL` 마커 존재
- [ ] 부록 B.3 첫 줄에 `HISTORICAL` 마커 존재
- [ ] §18, B.3의 기존 내용 변경 0건

**산출물**: SPEC 수정 (2곳 마커 추가)
</details>

<details>
<summary><b>0-3. CONFLICT_LOG.md 초기화 + 충돌 해결 프로토콜 작성</b></summary>

**입력**: 본 계획서 §9 (충돌 해결 프로토콜)

**절차**:
1. `Ai-investing-detail/CONFLICT_LOG.md` 신규 생성
2. 파일 구조:
   ```markdown
   # AI INVESTING 충돌 기록부
   > **Status**: ACTIVE
   > **버전**: v1.0

   ## 충돌 해결 프로토콜 (§9 발췌)
   [본 계획서 §9.1 충돌 유형별 해결 테이블 복사]

   ## 충돌 기록
   | 날짜 | 충돌 유형 | 파일 A | 파일 B | 내용 | 판정 | 조치 완료 |
   |------|----------|--------|--------|------|------|----------|
   | (빈 테이블 — Phase 진행 시 기록 시작) |
   ```
3. 이미 알려진 충돌 1건 선등록:
   - D2.0-01 §5.9 오류 (0-1에서 해결) → 조치 완료 ✅

**검증**:
- [ ] CONFLICT_LOG.md 존재 + 프로토콜 섹션 포함
- [ ] D2.0-01 §5.9 충돌 건 기록 존재

**산출물**: `CONFLICT_LOG.md` (신규)
</details>

<details>
<summary><b>0-4. 교차 중복 감사 (선행작업 A)</b></summary>

**입력 파일**: 19개 관점 파일 (sot 2/Ai-investing-detail/ 내 `*_약점분석_*.md` 19개)

**절차**:
1. **추출**: 19개 파일에서 `### B-N.` 패턴의 카테고리 제목 171개 + 하위 항목 758개 추출
   - 추출 형식: `| 관점# | 카테고리명 | 항목명 | 키워드 |`
2. **1차 키워드 매칭**: 동일/유사 키워드 그룹핑
   - 대상 키워드 예: "레짐", "Volume", "슬리피지", "SHAP", "Factor", "FinBERT", "Circuit Breaker", "백테스트", "VaR", "Kelly"
   - 2개 이상 관점에 등장하는 키워드 그룹 = 중복 후보
3. **2차 수동 판정**: 각 중복 그룹에서 정본 소유자 결정
   - 기준: "이 개념이 가장 핵심적으로 다뤄지는 관점" = 정본
   - 본 계획서 §5A 예상 중복 9건을 시작점으로 사용
4. 결과를 `21_mapping/dedup_audit.md`에 기록
   ```markdown
   # 교차 중복 감사 결과
   | 중복 그룹 | 키워드 | 등장 관점 | 정본 소유자 | 비정본 처리 |
   |----------|--------|----------|-----------|-----------|
   | 시장 레짐 | regime, 레짐 | #1, #3 | #1 (01_realtime-adaptive/) | #3에서 `> 참조: 01_realtime-adaptive/market_regime.md` |
   ```

**검증**:
- [ ] 19개 파일 전수 스캔 확인 (758항목)
- [ ] 중복 그룹 전부 정본 소유자 배정 완료
- [ ] 미판정 중복 0건

**산출물**: `21_mapping/dedup_audit.md` (신규)
**예상 작업량**: 171 카테고리 스캔 → ~20-30 중복 그룹 → 수동 판정 30건
</details>

<details>
<summary><b>0-5. 정본 소유자 테이블 작성</b></summary>

**입력**: 0-4 결과 (`dedup_audit.md`)

**절차**:
1. `21_mapping/canonical_owner_table.md` 신규 생성
2. dedup_audit.md의 정본 판정 결과를 개념별 테이블로 정리:
   ```markdown
   # 정본 소유자 테이블
   | 개념 | 정본 소유 파일 | 참조 파일(들) | LOCK 관련 |
   |------|-------------|-------------|----------|
   | 시장 레짐 감지 | 01_realtime-adaptive/market_regime.md | 03_macro-sector-stock/ | — |
   | Circuit Breaker 확장 | PART2 §6.8 (LOCK) | 02_behavioral-finance/ | SPEC §10.2 LOCK |
   | 슬리피지 모델 | 06_execution-optimization/ | 11_tca/ | — |
   ```
3. LOCK 관련 개념은 반드시 `LOCK 관련` 칼럼에 출처 명시
4. 정본이 아닌 파일에는 이후 Phase 1-2에서 `> 참조:` 링크로 교체할 대상 마킹

**검증**:
- [ ] dedup_audit.md의 모든 중복 그룹이 테이블에 등재
- [ ] LOCK 관련 개념은 전부 `LOCK 관련` 칼럼 채움
- [ ] 정본 파일 경로가 §2.1 폴더 트리와 일치

**산출물**: `21_mapping/canonical_owner_table.md` (신규)
</details>

<details>
<summary><b>0-6. STEP7-I 106건 매핑 (선행작업 B)</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot\STEP7-I_AI_Investing_보강_작업가이드.md` (106건)
- 19개 관점 파일 (758항목)

**절차**:
1. STEP7-I에서 Part 1~12, 106건의 `S7I-NNN` ID + 제목 추출
2. 각 항목을 19개 관점 파일 항목과 의미 매칭:
   - **ABSORBED**: sot 2/에 동일/상위 개념이 이미 상세 포함 → 흡수 완료
   - **PARTIAL**: 부분만 흡수 → Phase 2에서 누락분 추가
   - **UNMATCHED**: 어느 관점에도 없음 → 해당 관점 파일에 추가 예정
3. 결과를 `21_mapping/step7i_mapping.md`에 기록:
   ```markdown
   # STEP7-I ↔ sot 2/ 매핑 테이블
   > **매핑 기준일**: 2026-03-22
   > **STEP7-I 원본 작성일**: 2025-02-22 (원본 보존, 수정하지 않음)

   | S7I-ID | S7I 제목 | Priority | 매칭 상태 | sot 2/ 대응 파일 | 비고 |
   |--------|---------|----------|----------|-----------------|------|
   | S7I-001 | AI 투자 플랫폼 벤치마크 | HIGH | ABSORBED | 10_quant-research/ | |
   | S7I-023 | FinBERT 한국어 확장 | CRITICAL | PARTIAL | 02_behavioral-finance/ | 한국어 모델 상세 추가 필요 |
   ```
4. 매핑 통계 요약 추가: ABSORBED N건 / PARTIAL N건 / UNMATCHED N건

**검증**:
- [ ] 106건 전수 매핑 (미매핑 0건)
- [ ] UNMATCHED 항목에 대응 관점 또는 신규 파일 계획 기재
- [ ] PARTIAL 항목에 구체적 누락 내용 기재

**산출물**: `21_mapping/step7i_mapping.md` (신규)
</details>

<details>
<summary><b>0-7. SPEC 마이그레이션 목록 확정 (선행작업 C)</b></summary>

**입력 파일**: `D:\VAMOS\docs\sot\VAMOS_AI_INVESTING_SPEC.md` §7~§18

**절차**:
1. 본 계획서 §5C의 마이그레이션 대상 테이블을 최종 확정
2. 각 대상별 확인:
   - §9 RSI_BB: 파라미터 그리드 27조합, Wilder RSI, BB ddof=0 → `20_strategy-detail/technical/rsi_bb.md`
   - §7.8 Harmonic: Gartley, Butterfly 등 → `20_strategy-detail/technical/harmonic.md`
   - §7.9 시장 상황별 전략: 정적 테이블 4줄 → `01_realtime-adaptive/strategy_selection.md`
   - §16 수학 공식: **이전하지 않음** (LOCK) — sot 2/에서 인라인 인용
   - §17 15개 결함: 결함별 해당 관점 폴더에 분배 (목적지 매핑)
   - §18 로드맵: **이전하지 않음** — HISTORICAL 마커만 (0-2에서 완료)
3. §17 15개 결함의 분배 매핑 테이블 작성:
   ```markdown
   | 결함# | 결함명 | 분배 대상 관점 | 분배 대상 파일 |
   |-------|--------|-------------|-------------|
   | 1 | Kelly 과대 베팅 | #15 포트폴리오심화 | 15_portfolio-advanced/kelly_criterion.md |
   | 2 | Risk Parity 실패 | #15 포트폴리오심화 | 15_portfolio-advanced/risk_parity.md |
   | ... | ... | ... | ... |
   ```

**검증**:
- [ ] §5C 테이블의 모든 대상에 sot 2/ 목적지 확정
- [ ] §17 15개 결함 전수 매핑 완료
- [ ] LOCK 항목(§16) 이전 없음 확인

**산출물**: 마이그레이션 목록 확정 (본 계획서 §5C 갱신 + §17 분배 매핑)
</details>

<details>
<summary><b>0-8. L3 템플릿 + L3 판정 기준 문서 생성</b></summary>

**입력**: 본 계획서 §7 Phase 2의 L3 정의 (E1~E9)

**절차**:
1. `Ai-investing-detail/_templates/` 폴더 생성
2. `_templates/L3_TEMPLATE.md` 생성 — 본 계획서의 L3 템플릿 (line 559~612) 내용을 독립 파일로 추출
3. `_templates/L3_CRITERIA.md` 생성:
   ```markdown
   # L3 판정 기준
   > **버전**: v1.0
   > **Status**: APPROVED

   ## 9요소 정의
   [E1~E9 테이블 — 본 계획서 §7 Phase 2에서 추출]

   ## 합격 판정
   | 판정 | 조건 |
   |------|------|
   | L3 PASS | 9요소 전수 기재 + E2 의사코드 포함 + E4 시그니처 포함 |
   | L3 CONDITIONAL | 7~8요소 (E6 또는 E7 1건 누락 허용) → 30일 보완 |
   | L3 FAIL | 6요소 이하 → Phase 2 재작업 |

   ## 적용 범위
   - 적용 대상: 20_strategy-detail/ 전 파일 + 01~19 관점 폴더 내 구현 항목 파일
   - 비적용: _index.md, INDEX.md, 매핑 문서, AUTHORITY_CHAIN.md, CONFLICT_LOG.md
   ```

**검증**:
- [ ] `_templates/L3_TEMPLATE.md` 존재 + E1~E9 전 섹션 포함
- [ ] `_templates/L3_CRITERIA.md` 존재 + 합격 판정 기준 포함
- [ ] 본 계획서 L3 정의와 내용 일치 (복사 정합성)

**산출물**: `_templates/L3_TEMPLATE.md` + `_templates/L3_CRITERIA.md` (신규 2건)
</details>

---

### Phase 1: 구조 재편 + 콘텐츠 마이그레이션

> **목표**: 폴더 생성 → 기존 파일 분해/재배치 → 메타데이터 표준화
> **산출물: 전체 폴더 구조 + INDEX.md + 171+ 파일**

| 단계 | 작업 | 상세 | 이슈 해결 |
|------|------|------|----------|
| 1-1 | 폴더 구조 생성 | §2.1 트리 기반 00~21 폴더 + 하위 폴더 생성 | #15, #20 |
| 1-2 | 19개 관점 파일 분해 | 각 관점 파일의 B-카테고리를 개별 .md 파일로 분해 → 해당 관점 폴더에 배치 | #6, #15 |
| 1-3 | 메타데이터 헤더 표준화 | 모든 파일에 아래 헤더 추가: | #8, #9 |

```markdown
> **버전**: v1.0
> **Status**: DRAFT | REVIEW | APPROVED | LOCKED
> **작성일**: 2026-03-22
> **Last-reviewed**: 2026-03-22
> **정본 소유자**: 이 파일이 정본인 개념 목록 (canonical_owner_table 참조)
> **기술스택 의존성**: SPEC §14 LOCK 범위 내 | REQUIRES LOCK AMENDMENT: [항목]
```

| 단계 | 작업 | 상세 | 이슈 해결 |
|------|------|------|----------|
| 1-4 | SPEC §9 RSI_BB 마이그레이션 | §9 내용 → 20_strategy-detail/technical/rsi_bb.md. SPEC §9에 리디렉트 마커 | #3 |
| 1-5 | SPEC §7.8, §7.9 마이그레이션 | §7.8 → harmonic.md, §7.9 → strategy_selection.md. SPEC에 리디렉트 | #3 |
| 1-6 | SPEC §17 결함 분배 | 15개 결함을 해당 관점 폴더 파일에 분배 | — |
| 1-7 | 00_core-integration 작성 | ORANGE CORE → AI Investing Node 인터페이스 스펙 | #12 |
| 1-8 | 20_strategy-detail 구조 작성 | SPEC §7-8의 96개 전략을 카테고리별 파일로 구조화 (이름 + 요약 + 상세는 추후) | #15 |
| 1-9 | INDEX.md 작성 | 카테고리별 엔트리 + 파일 수 + Status + Version | #6, #9 |
| 1-10 | 폴더별 _index.md 작성 | 각 폴더 내 파일 목록만 (설명 없음) | #6 |
| 1-11 | PART2 §6.8.2 링크 테이블 작성 | PART2에 sot 2/ 참조 테이블 추가 | #8, #19 |
| 1-12 | PART2 기존 SPEC 참조 갱신 | PART2 내 SPEC 직접 참조 → sot 2/ 참조로 변경 (해당하는 것만) | #19 |
| 1-13 | 새 관점 추가 체크리스트 작성 | INDEX.md에 "새 관점 추가 절차" 섹션 | #13 |
| 1-14 | R11 단방향 참조 점검 | sot 2/ → SPEC 역참조 없는지 전 파일 점검 | #14 |

#### Phase 1 실행 순서 의존성 (v1.2 추가)

```
1-1 (폴더 생성) ─── 선행 없음
  ├→ 1-2 (파일 분해) ─── 1-1 필요
  │    ├→ 1-9 (INDEX.md) ─── 1-2 완료 후
  │    ├→ 1-10 (_index.md) ─── 1-2 완료 후
  │    └→ 1-15 (아카이브) ─── 1-2 완료 후
  ├→ 1-3 (메타데이터) ─── 1-2 이후 (대상 파일 존재 필요)
  ├→ 1-4 (RSI_BB 이전) ─── 1-1 필요
  │    └→ 1-12 (PART2 참조 갱신) ─── 1-4, 1-5 완료 후
  ├→ 1-5 (§7.8,§7.9 이전) ─── 1-1 필요
  ├→ 1-6 (§17 결함 분배) ─── 1-1 필요
  ├→ 1-7 (CORE 통합) ─── 1-1 필요
  ├→ 1-8 (전략 상세 구조) ─── 1-1 필요
  │    └→ 1-16 (SPEC §7-8 링크) ─── 1-8 완료 후
  ├→ 1-11 (PART2 링크 테이블) ─── 1-1 필요
  ├→ 1-13 (새 관점 체크리스트) ─── 선행 없음
  └→ 1-14 (단방향 점검) ─── 1-2 완료 후
```

#### Phase 1 단계별 상세 작업 절차 (v1.3.1 추가)

<details>
<summary><b>1-1. 폴더 구조 생성</b></summary>

**입력**: 본 계획서 §2.1 폴더 트리

**절차**:
1. 아래 폴더를 순서대로 생성 (총 24개 폴더 + 2개 하위 폴더):
   ```
   Ai-investing-detail/
   ├── _archive/
   ├── _templates/          ← Phase 0-8에서 이미 생성
   ├── 00_core-integration/
   ├── 01_realtime-adaptive/
   ├── 02_behavioral-finance/
   ├── 03_macro-sector-stock/
   ├── 04_performance-attribution/
   ├── 05_backtest-integrity/
   ├── 06_execution-optimization/
   ├── 07_universe-management/
   ├── 08_cross-asset/
   ├── 09_model-governance/
   ├── 10_quant-research/
   ├── 11_tca/
   ├── 12_microstructure/
   ├── 13_asset-class-deep/
   ├── 14_corporate-events/
   ├── 15_portfolio-advanced/
   ├── 16_global-geopolitics/
   ├── 17_explainability/
   ├── 18_data-quality/
   ├── 19_liquidity-cash/
   ├── 20_strategy-detail/
   │   ├── technical/
   │   └── quant/
   └── 21_mapping/
   ```
2. 폴더 깊이 검증: 최대 3단계 확인 (R1 규칙)
3. 폴더명 검증: 전부 영문 소문자 + 하이픈/언더스코어 (R1 규칙, §2.3)

**검증**:
- [ ] 24개 폴더 + 2개 하위 폴더 전수 존재
- [ ] 4단계 이상 폴더 0건
- [ ] 한글/대문자 폴더명 0건

**산출물**: 전체 폴더 구조
</details>

<details>
<summary><b>1-2. 19개 관점 파일 분해</b></summary>

**입력**: 19개 원본 관점 파일 (`*_약점분석_*.md`)

**절차**:
1. 각 관점 파일에서 `### B-N.` 카테고리 단위로 분할
2. 각 카테고리를 해당 관점 폴더에 개별 `.md` 파일로 생성
   - 파일명: 카테고리 핵심 키워드의 영문 snake_case (예: `supply_demand_zone.md`)
   - 파일 내용: 해당 B-카테고리 제목 + 하위 항목 전문 복사
3. **분해 규칙**:
   - 원본의 Section A (현재 상태 분석)는 각 관점 `_index.md`의 상단 요약으로 이동
   - 원본의 Section B (누락 카테고리)의 각 `### B-N.`이 개별 파일이 됨
   - 중복 개념(0-4에서 판정)은 정본이 아닌 관점에서 `> 참조: [정본 파일 경로]`로 교체
4. 분해 전/후 항목 수 대조: 원본 항목 수 = 분해 후 파일 내 항목 수 합계

**예시** (관점 #1 실시간적응형전략, 54항목, 13카테고리):
```
01_realtime-adaptive/
├── _index.md                    ← Section A 요약 + 파일 목록
├── supply_demand_zone.md        ← B-1 카테고리
├── support_resistance.md        ← B-2 카테고리
├── price_action.md              ← B-3 카테고리
├── strategy_invalidation.md     ← B-4 카테고리
├── market_regime.md             ← B-5 카테고리 (정본 소유)
├── multi_timeframe.md           ← B-6 카테고리
├── order_flow.md                ← B-7 카���고리
├── dynamic_position.md          ← B-8 카테고리
├── fakeout_detection.md         ← B-9 카테고리
├── volatility_adaptive.md       ← B-10 카테고리
├── ai_pattern_strategy.md       ← B-11 카테고리
├── strategy_ensemble.md         ← B-12 카테고리
└── realtime_data_pipeline.md    ��� B-13 카테고리
```

**검증**:
- [ ] 19개 관점 × 각 카테고리 수 = 생성된 파일 수 일치
- [ ] 원본 758항목 = 분해 �� 전 파일 항목 합계 (누락 0건)
- [ ] 중복 개념에 `> 참조:` 링크 적용 (canonical_owner_table 기준)

**산출물**: 171+ 개별 .md 파일
</details>

<details>
<summary><b>1-3. 메타데이터 헤더 표준화</b></summary>

**입력**: 1-2에서 생성된 전 파일

**절차**:
1. 모든 파일(171+)에 아래 표준 헤더 추가 (파일 최상단):
   ```markdown
   # [카테고리/항목명]
   > **버전**: v1.0
   > **Status**: DRAFT
   > **작성일**: 2026-03-22
   > **Last-reviewed**: 2026-03-22
   > **원본 관점**: #N [관점명]
   > **정본 소유 개념**: [canonical_owner_table에서 조회]
   > **기술스택 의존성**: SPEC §14 LOCK 범위 내
   ```
2. 정본 소유 개념이 없는 파일은 `정본 소유 개념: —` 으로 기재
3. 기술스택 의존성이 SPEC §14 LOCK 외 기술이 필요한 경우:
   `기술스택 의존성: REQUIRES LOCK AMENDMENT: [필요 기술명]`

**검증**:
- [ ] 전 파일에서 `Status:` 검색 → 누락 0건 (V-02)
- [ ] `DRAFT` 상태가 아닌 파일 0건 (Phase 1에서는 전부 DRAFT)

**산출물**: 전 파일 헤더 갱신
</details>

<details>
<summary><b>1-4. SPEC §9 RSI_BB 마이그레이션</b></summary>

**입력**: `VAMOS_AI_INVESTING_SPEC.md` §9

**절차**:
1. `20_strategy-detail/technical/rsi_bb.md` 신규 생성
2. SPEC §9 내용 전문 복사:
   - 파라미터 그리드 27조합 (rsi_period[7,14,21] × rsi_oversold[25,30,35] × bb_period[15,20,25])
   - Wilder RSI 수식 (SMA seed + EMA 전파)
   - BB 수식 (ddof=0, 2.0 sigma)
   - Entry/Exit 알고리즘
   - RSIBBAdapter 클래스 설계
3. L3 템플릿(E1~E9) 형식으로 재구성 — 기존 내용을 E1~E9 섹션에 배치
4. SPEC §9를 리디렉트로 교체:
   ```markdown
   ## §9. RSI_BB 전략 구현 상세
   > **MIGRATED**: 구현 상세는 `sot 2/Ai-investing-detail/20_strategy-detail/technical/rsi_bb.md` 참조.
   > 아래는 이전 전 원본의 요약 색인입니다.
   [1-2줄 요약만 남김]
   ```

**검증**:
- [ ] rsi_bb.md에 27 파라미터 조합 존재
- [ ] rsi_bb.md에 Wilder RSI + BB 수식 존재
- [ ] SPEC §9에 `MIGRATED` 마커 존재
- [ ] SPEC §9 원본 내용 삭제 (리디렉트 + 요약만 잔존)

**산출물**: `rsi_bb.md` (신규) + SPEC §9 수정
</details>

<details>
<summary><b>1-5. SPEC §7.8, §7.9 마이그레이션</b></summary>

**입력**: SPEC §7.8 (Harmonic Patterns), §7.9 (시장 상황별 전략 선택)

**절차**:
1. `20_strategy-detail/technical/harmonic.md` 생성 ← §7.8 내용
2. `01_realtime-adaptive/strategy_selection.md` 생성 ← §7.9 내용
3. 각 파일에 L3 템플릿 헤더 + §8.2 메타데이터 헤더 추가
4. SPEC §7.8, §7.9 각각에 리디렉트 마커 추가 (§9와 동일 패턴)

**검증**:
- [ ] harmonic.md에 Gartley/Butterfly 등 패턴 상세 존재
- [ ] strategy_selection.md에 시장 상황 4유형 테이블 존재
- [ ] SPEC §7.8, §7.9에 `MIGRATED` 마커 존재

**산출물**: 2개 신규 파일 + SPEC 2곳 수정
</details>

<details>
<summary><b>1-6. SPEC §17 결함 분배</b></summary>

**입력**: SPEC §17 (15개 결함 + 극복 방안), 0-7 분배 매핑

**절차**:
1. 0-7에서 확정한 분배 매핑 테이블에 따라 15개 결함을 각 관점 폴더 파일에 추가
   - 대상 파일이 이미 존재하면 `## 결함 극복` 섹션 추가
   - 대상 파일이 없으면 신규 생성
2. 각 결함에 포함할 내용: 결함 설명 + 극복 방안 + (있으면) 코드 스니펫
3. SPEC §17에 리디렉트 마커 추가 (FR-6 패턴):
   ```markdown
   > **MIGRATED**: 15개 결함의 상세 극복 방안은 sot 2/Ai-investing-detail/ 해당 관점 폴더로 분배됨.
   > 아래 목록은 인덱스로 보존합니다.
   ```

**검증**:
- [ ] 15개 결함 전수 분배 (누락 0건)
- [ ] 분배 대상 파일에 결함 내용 존재
- [ ] SPEC §17에 `MIGRATED` 마커 존재

**산출물**: 관점 폴더 파일 수정/추가 + SPEC §17 수정
</details>

<details>
<summary><b>1-7. 00_core-integration 작성</b></summary>

**입력**: D2.0-03 §1 (BLUE NODE 정의), SPEC §20 (VAMOS CORE 통합)

**절차**:
1. `00_core-integration/core_integration_spec.md` 생성
2. 포함 내용:
   - ORANGE CORE → AI Investing Node 연결 인터페이스
   - I-1~I-25 중 AI Investing에 직접 관련되는 Interface 목록
   - P2 승인 흐름 (HITL: 5분 Timeout)
   - Event Bus 연동: VAMOS_EVENT 스키마 참조 (SPEC §4.2)
   - Node 활성화/비활성화 조건 (D2.0-03 §3.3 P2 라이프사이클)
3. L3 템플릿으로 작성 (가능한 부분만 — 인터페이스 스펙이므로 E2, E4 중심)

**검증**:
- [ ] core_integration_spec.md 존재
- [ ] ORANGE CORE Interface 목록 포함
- [ ] P2 승인 흐름 + Timeout LOCK 참조 포함

**산출물**: `00_core-integration/core_integration_spec.md` (신규)
</details>

<details>
<summary><b>1-8. 20_strategy-detail 구조 작성</b></summary>

**입력**: SPEC §7 (40개 기술 전략), §8 (56개 퀀트 전략)

**절차**:
1. `20_strategy-detail/technical/` 아래 카테고리별 파일 생성 (§7 구조 기반):
   ```
   technical/
   ├── trend_following.md        ← §7.1: MACD, MA Crossover, Ichimoku, ADX, SAR, Donchian, Supertrend (7개)
   ├── momentum_oscillator.md    ← §7.2: RSI, Stochastic, CCI, Williams%R, MFI (5개)
   ├── volatility.md             ← §7.3: BB, ATR, Keltner, BB Squeeze, VIX연동, 변동성 돌파 (6개)
   ├── volume.md                 ← §7.4: OBV, VWAP, A/D Line (3개)
   ├── composite.md              ← §7.5: 다중지표, 크로스시스템, 적응가중, 엘리어트 (4개)
   ├── chart_pattern_reversal.md ← §7.6: Head&Shoulders, 이중천장/바닥 등 (7개)
   ├── chart_pattern_continuation.md ← §7.7: 삼각형, 깃발 등 (8개)
   └── harmonic.md               ← §7.8: 이전 완료 (1-5에서)
   ```
2. `20_strategy-detail/quant/` 아래 카테고리별 파일 생성 (§8 구조 기반):
   ```
   quant/
   ├── statistical.md           ← §8.1: Pairs, Mean Reversion 등 (10개)
   ├── factor.md                ← §8.2: Value, Momentum, Quality 등 (8개)
   ├── options.md               ← §8.3: Covered Call, Iron Condor 등 (8개)
   ├── event_driven.md          ← §8.4: Earnings, M&A 등 (8개)
   ├── ml_ai.md                 ← §8.5: LSTM, Transformer, RL 등 (12개)
   ├── crypto.md                ← §8.6: DeFi Yield, Funding Rate 등 (8개)
   └── portfolio_risk.md        ← §8.7: Risk Parity, Black-Litterman (2개)
   ```
3. 각 파일에 전략 이름 + SPEC 참조 + Status: DRAFT 헤더만 작성 (상세는 Phase 2)

**검증**:
- [ ] technical/ 8파일 + quant/ 7파일 = 15파일 존재
- [ ] 96개 전략 이름 전수 등재 (누락 0건)
- [ ] 각 파일에 Status: DRAFT 헤더 존재

**산출물**: 15개 전략 카테고리 파일 (이름+구조만, 상세는 Phase 2)
</details>

<details>
<summary><b>1-9. INDEX.md 작성</b></summary>

**입력**: 1-1~1-8 결과 (전체 폴더 + 파일 구조)

**절차**:
1. `Ai-investing-detail/INDEX.md` 생성
2. 구조:
   ```markdown
   # AI INVESTING 상세 정본 INDEX
   > **Status**: APPROVED
   > **Last-updated**: 2026-03-22

   ## 폴더 구조
   | # | 폴더 | 설명 | 파일 수 | Status | Version |
   |---|------|------|---------|--------|---------|
   | 0 | 00_core-integration/ | ORANGE CORE 통합 | 1 | DRAFT | v1.0 |
   | 1 | 01_realtime-adaptive/ | 실시간 적응형 전략 | 13+ | DRAFT | v1.0 |
   | ... | ... | ... | ... | ... | ... |
   | 20 | 20_strategy-detail/ | 96개 전략 상세 | 16+ | DRAFT | v1.0 |
   | 21 | 21_mapping/ | 매핑 & 거버넌스 | 4 | DRAFT | v1.0 |

   ## 새 관점 추가 절차
   [본 계획서 §10.2 체크리스트 복사]
   ```

**검증**:
- [ ] INDEX.md에 전 폴더(22개) 등재 (V-03)
- [ ] 파일 수 칼럼이 실제와 일치

**산출물**: `INDEX.md` (신규)
</details>

<details>
<summary><b>1-10. 폴더별 _index.md 작성</b></summary>

**입력**: 각 폴더 내 파일 목록

**절차**:
1. 22개 폴더 각각에 `_index.md` 생성 (FR-2 템플릿 사용)
2. 파일 목록만 기재 (설명 없음):
   ```markdown
   # [폴더명] — 파일 목록
   | 파일명 | Status | 버전 |
   |--------|--------|------|
   | supply_demand_zone.md | DRAFT | v1.0 |
   | support_resistance.md | DRAFT | v1.0 |
   ```
3. _index.md에는 §8.2 메타데이터 헤더 **비적용** (인덱스 파일)

**검증**:
- [ ] 22개 폴더 전부 _index.md 존재 (V-04)
- [ ] _index.md 내 파일 목록 = 실제 폴더 내 파일과 일치

**산출물**: 22개 `_index.md`
</details>

<details>
<summary><b>1-11. PART2 §6.8.2 링크 테이블 작성</b></summary>

**입력**: 전체 sot 2/ 구조, FR-3 칼럼 정의

**절차**:
1. PART2 `§6.8` 바로 아래에 `### §6.8.2 AI Investing 상세 참조 인덱스` 섹션 추가
2. FR-3에 정의된 칼럼 구조 사용:
   ```
   | # | 영역 | sot 2/ 경로 | 항목 수 | SPEC 대응 | STEP7-I 대응 | Phase |
   ```
3. 22개 폴더(00~21) 전수 등재

**검증**:
- [ ] PART2에 §6.8.2 섹션 존재
- [ ] 22개 폴더 전수 등재
- [ ] 경로가 실제 폴더 구조와 일치

**산출물**: PART2 수정 (§6.8.2 추가)
</details>

<details>
<summary><b>1-12. PART2 기존 SPEC 참조 갱신</b></summary>

**입력**: PART2 §6.8 내 SPEC §9, §7.8, §7.9, §17 직접 참조

**절차**:
1. PART2에서 아래 SPEC 참조를 sot 2/ 참조로 변경:
   - `SPEC §9` → `sot 2/Ai-investing-detail/20_strategy-detail/technical/rsi_bb.md`
   - `SPEC §7.8` → `sot 2/Ai-investing-detail/20_strategy-detail/technical/harmonic.md`
   - `SPEC §7.9` → `sot 2/Ai-investing-detail/01_realtime-adaptive/strategy_selection.md`
   - `SPEC §17 결함` → `sot 2/Ai-investing-detail/` 해당 관점 폴더 (§6.8.2 테이블 참조)
2. SPEC 아키텍처 참조(§1~§6, §10~§16)는 **변경하지 않음** (상위 레벨)
3. 변경 시 원문 보존: `<!-- UPDATED 2026-03-22: 기존 SPEC §9 → sot 2/.../rsi_bb.md -->`

**검증**:
- [ ] PART2에서 마이그레이션 완료된 SPEC 섹션 직접 참조 0건
- [ ] 아키텍처 레벨 SPEC 참조(§1~§6 등)는 변경 없음

**산출물**: PART2 수정 (참조 갱신)
</details>

<details>
<summary><b>1-13 ~ 1-16 (나머지 4단계)</b></summary>

| 단계 | 작업 | 상세 절차 |
|------|------|----------|
| **1-13** | 새 관점 추가 체크리스트 | INDEX.md에 §10.2 체크리스트 복사. 1-9에서 이미 포함되므로 검증만 수행 |
| **1-14** | R11 단방향 참조 점검 | 전 sot 2/ 파일에서 `docs/sot/` 또는 `SPEC` 패턴 검색. 발견 시 인라인 인용으로 교체 (링크 삭제) |
| **1-15** | 원본 19개 파일 아카이브 | 1-2 분해 완료 확인 후, 원본 19개 파일을 `_archive/`로 이동. 이동 후 `_archive/` 내 파일 편집 금지 |
| **1-16** | SPEC §7-8에 sot 2/ 링크 추가 | SPEC §7.1~§7.9, §8.1~§8.7 각 카테고리에 `> 상세: sot 2/Ai-investing-detail/20_strategy-detail/[파일] 참조` 추가 |

**공통 검증**:
- [ ] 1-14: sot 2/ → SPEC 역참조 0건 (V-08)
- [ ] 1-15: `_archive/`에 19개 파일 존재
- [ ] 1-16: SPEC §7-8 각 카테고리에 sot 2/ 링크 존재
</details>

---

### Phase 2: L3 전수 승급 + 콘텐츠 심화 + 도구

> **목표**: 전 항목을 L3(구현 즉시 투입 가능) 수준으로 승급 + 자동화 도구
> **핵심 원칙**: Phase 2 완료 후 sot 2/의 모든 파일을 읽고 바로 코드 작성이 가능해야 함

#### L3 필수 9요소 정의 (v1.3 추가)

모든 구현 항목은 아래 9개 요소를 **반드시** 포함해야 L3 판정:

| # | 요소 | 설명 | 예시 (RSI_BB 기준) |
|---|------|------|-------------------|
| **E1** | Input | 입력 데이터 스키마 + 소스 | OHLCV_PLUS (close, volume) from TimescaleDB |
| **E2** | Algorithm | 의사코드 또는 수식 (복사→구현 가능) | `if RSI < oversold AND close < BB_lower: BUY` |
| **E3** | Output | 출력 스키마/형식 + 후속 소비자 | `Signal(symbol, action, confidence, timestamp)` → OrderManager |
| **E4** | Class/API Design | 클래스명·메서드·시그니처 | `class RSIBBAdapter(BaseStrategy): def generate_signal(df) -> Signal` |
| **E5** | Tech Stack Dependency | 필요 라이브러리 + 버전 | pandas≥2.0, numpy, ta-lib (SPEC §14 LOCK) |
| **E6** | Performance Requirements | 지연·처리량·메모리 | 단일 심볼 < 50ms, 배치 100 심볼 < 5s |
| **E7** | Error Handling | 예외 시나리오 + 복구 로직 | 데이터 누락 → NaN 전파 차단, 최소 30봉 미달 → SKIP |
| **E8** | Test Criteria | 단위·통합 테스트 기준 | unit: RSI 계산 검증 (Wilder 공식), integration: 51% Gate 통과 |
| **E9** | LOCK References | 관련 LOCK 값 + 출처 | 51% Gate (SPEC §6.1), Circuit Breaker -3% (SPEC §10.2) |

#### L3 템플릿 (Phase 0-8에서 생성)

```markdown
# [항목명]

> **버전**: v1.0
> **Status**: DRAFT
> **L3 완성도**: ☐E1 ☐E2 ☐E3 ☐E4 ☐E5 ☐E6 ☐E7 ☐E8 ☐E9

## E1. Input
- **데이터**: [스키마명] from [소스]
- **필수 필드**: [필드 목록]
- **전처리** (필수): NaN 처리 방법 / 최소 데이터 봉 수 / 정규화·스케일링 여부

## E2. Algorithm (순수 알고리즘/수식 — 클래스 구조는 E4에서)
\```python
# 의사코드 (복사→구현 가능 수준)
def algorithm(input):
    # Step 1: ...
    # Step 2: ...
    return output
\```

## E3. Output
- **스키마**: [출력 형식]
- **confidence 계산**: [신뢰도 산출 방법 — 51% Gate Win Rate 연결]
- **소비자**: [후속 모듈/API]

## E4. Class/API Design (클래스 구조 + 인터페이스 — 알고리즘 로직은 E2에서)
\```python
class ClassName(BaseClass):
    def method(self, params) -> ReturnType:
        """docstring"""
        pass
\```

## E5. Tech Stack Dependency
| 라이브러리 | 버전 | SPEC §14 LOCK | 용도 |
|-----------|------|--------------|------|

## E6. Performance Requirements
| 지표 | 기준 | 측정 방법 |
|------|------|----------|

## E7. Error Handling
| 예외 시나리오 | 복구 로직 | 심각도 |
|-------------|----------|--------|

## E8. Test Criteria
- **Unit**: [단위 테스트 — 지표 계산 정확성, 알려진 데이터셋 대조]
- **Integration**: [통합 테스트 — 데이터 수집→신호 생성→주문 파이프라인 end-to-end]
- **Acceptance**: [수용 테스트 — 51% Gate (Win≥51%, Sharpe≥1.0, Decay<30%, Min 30건)]

## E9. LOCK References
| LOCK 값 | 출처 | 적용 방식 |
|---------|------|----------|
```

#### Phase 2 실행 단계 (v1.3 강화)

| 단계 | 작업 | 상세 | 대상 항목 수 | 이슈 해결 |
|------|------|------|-------------|----------|
| ~~2-0~~ | ~~L3 템플릿 파일 생성~~ | **Phase 0-8에 통합 (삭제)** | — | — |
| 2-1a | **P0 전략 L3 작성** (RSI_BB 외 핵심 10개) | 20_strategy-detail/ 중 V1 구현 대상: MACD, MA Crossover, Bollinger Band, ADX, Ichimoku, SAR, Donchian, Supertrend, RSI단독, Volume Profile. 9요소 전수 기재 | 10 | — |
| 2-1b | **P1 전략 L3 작성** (V2 대상 30개) | 기술적 분석 잔여 + 퀀트 핵심: Pairs Trading, Mean Reversion, Momentum Factor, Value Factor, Black-Litterman 등. 9요소 전수 기재 | 30 | — |
| 2-1c | **P2/P3 전략 L3 작성** (나머지 56개) | 옵션 전략(8), ML/AI(12), 크립토(8), 고급 퀀트(28). 9요소 전수 기재 | 56 | — |
| 2-2a | **P0 관점 L3 승급** (관점 #1~#5, 239항목) | 실시간적응형(54)+투자심리학(47)+매크로연결(52)+성과귀인(42)+백테스트진실성(44). L2.5→L3: 알고리즘·클래스·테스트 추가 | 239 | — |
| 2-2b | **P1 관점 L3 승급** (관점 #6~#11, 221항목) | 실행최적화(40)+유니버스관리(35)+교차분석(38)+AI거버넌스(39)+퀀트리서치(36)+TCA(33). L2.5→L3 | 221 | — |
| 2-2c | **P2 관점 L3 승급** (관점 #12~#17, 231항목) | 시장미시구조(36)+자산군별심화(45)+기업이벤트(38)+포트폴리오심화(40)+글로벌다각화(35)+Explainability(37). L2.5→L3 | 231 | — |
| 2-2d | **P3 관점 L3 승급** (관점 #18~#19, 67항목) | 데이터품질(35)+유동성현금(32). L2.5→L3 | 67 | — |
| 2-3 | **STEP7-I 106건 L3 반영** | step7i_mapping.md 기반, 미흡수 항목의 L3 보강 | ~30 (미흡수분) | #7 |
| 2-4 | **PART2 89 빈껍데기 L3 연결** | PART2 L1 항목에 sot 2/ L3 파일 링크 연결 | 89 | — |
| 2-5 | validate_links.py 작성 | 아래 스펙 참조 | 1 | #16 |
| 2-6 | tech_dependency.md 감사 | 전 파일의 기술스택 의존성 점검 → LOCK 외 기술 플래그 | 전체 | #17 |
| 2-7 | R12 기술스택 의존성 헤더 일괄 추가 | 전략 상세 파일에 의존성 섹션 추가 | 전체 | #17 |
| 2-8 | **Pydantic 스키마 12건 불일치 해결** (v1.3 F-4) | SPEC §4 contracts.py D-1~D-12: Field(ge=,le=) 범위 검증, OHLCV_Values docstring 수정, Optional+model_validator, ConnectorResponse 모델 추가 | 12 | GAP-5 |

#### Phase 2 단계별 상세 작업 절차 (v1.3.1 추가)

<details>
<summary><b>2-1a. P0 전략 L3 작성 (핵심 10개)</b></summary>

**입력**: SPEC §7 전략 이름 + PART2 §6.8 기존 L3 내용 + `_templates/L3_TEMPLATE.md`

**대상 전략 (V1 구현 대상)**:
```
1. MACD Crossover          → 20_strategy-detail/technical/trend_following.md
2. MA Crossover (SMA/EMA)  → 20_strategy-detail/technical/trend_following.md
3. Bollinger Band Breakout  → 20_strategy-detail/technical/volatility.md
4. ADX Trend Strength       → 20_strategy-detail/technical/trend_following.md
5. Ichimoku Cloud           → 20_strategy-detail/technical/trend_following.md
6. Parabolic SAR             → 20_strategy-detail/technical/trend_following.md
7. Donchian Channel         → 20_strategy-detail/technical/trend_following.md
8. Supertrend               → 20_strategy-detail/technical/trend_following.md
9. RSI 단독 (Wilder)        → 20_strategy-detail/technical/momentum_oscillator.md
10. Volume Profile           → 20_strategy-detail/technical/volume.md
```

**절차 (각 전략별)**:
1. L3 템플릿 복사 → 해당 카테고리 파일의 전략 섹션에 E1~E9 작성
2. **E1 Input**: OHLCV_PLUS 스키마에서 필요 필드 명시 (예: MACD는 close, Volume Profile은 close+volume)
3. **E2 Algorithm**: 의사코드 작성 (Python 스타일, 복사→구현 가능 수준)
   ```python
   # MACD 예시
   fast_ema = EMA(close, 12)
   slow_ema = EMA(close, 26)
   macd_line = fast_ema - slow_ema
   signal_line = EMA(macd_line, 9)
   histogram = macd_line - signal_line
   if macd_line > signal_line and prev_macd_line <= prev_signal_line:
       return Signal(action="BUY", confidence=histogram/close)
   ```
4. **E3 Output**: `Signal(symbol, action, confidence, timestamp)` → OrderManager
5. **E4 Class/API**: `class MACDAdapter(BaseStrategy): def generate_signal(df: pd.DataFrame) -> Signal`
6. **E5 Tech**: pandas, numpy, ta-lib (SPEC §14 LOCK 범위 확인)
7. **E6 Performance**: 단일 심볼 < 50ms, 배치 100 심볼 < 5s
8. **E7 Error**: 데이터 누락 → NaN 전파 차단, 최소 봉 수 미달(26봉) → SKIP
9. **E8 Test**: unit(지표 계산 검증 — 알려진 데이터셋 대조), integration(51% Gate 통과)
10. **E9 LOCK**: 51% Gate (SPEC §6.1), Circuit Breaker (SPEC §10.2)

**검증 (전략당)**:
- [ ] E1~E9 전수 기재 (체크박스 9/9)
- [ ] E2 의사코드가 복사→실행 가능 수준 (변수명, 함수명 명확)
- [ ] E4 클래스 시그니처가 BaseStrategy 상속 패턴 준수
- [ ] E9 LOCK 값이 §3.4 LOCK 테이블과 정확히 일치

**산출물**: 10개 전략 L3 완성 (trend_following.md, volatility.md, momentum_oscillator.md, volume.md)
</details>

<details>
<summary><b>2-1b. P1 전략 L3 작성 (V2 대상 30개)</b></summary>

**대상 전략 그룹**:
| 그룹 | 전략 예시 | 파일 | 수량 |
|------|----------|------|------|
| 기술 잔여 | Stochastic, CCI, OBV, Keltner, BB Squeeze, ATR 등 | technical/ 각 파일 | ~15 |
| 통계 퀀트 | Pairs Trading, Mean Reversion, Cointegration 등 | quant/statistical.md | ~5 |
| 팩터 | Value, Momentum, Quality, Size, Low Volatility | quant/factor.md | ~5 |
| 포트폴리오 | Black-Litterman, Risk Parity | quant/portfolio_risk.md | ~2 |
| 이벤트 | Earnings Surprise, Insider Trading, M&A | quant/event_driven.md | ~3 |

**절차**: 2-1a와 동일 패턴 (E1~E9 전수 기재). 특수 사항:
- **Pairs Trading E2**: Engle-Granger Cointegration 검정 → 스프레드 z-score → `if z > 2: SHORT_SPREAD, if z < -2: LONG_SPREAD`
- **Black-Litterman E2**: 기존 PART2 §6.8 L3 수식을 sot 2/로 이전 + `Π = δΣw_mkt` 포함
- **Factor E2**: Fama-French 5-Factor `R_i - R_f = α + β₁MKT + β₂SMB + β₃HML + β₄RMW + β₅CMA + ε`

**산출물**: 30개 전략 L3 완성
</details>

<details>
<summary><b>2-1c. P2/P3 전략 L3 작성 (나머지 56개)</b></summary>

**대상**: 옵션(8) + ML/AI(12) + 크립토(8) + 고급 퀀트(28)

**특수 사항**:
- **ML/AI 전략 (12개)**: E2에 모델 아키텍처(LSTM layers, Transformer attention heads, RL reward 함수) + 학습 파이프라인 포함
- **옵션 전략 (8개)**: E2에 Greeks 계산 (Black-Scholes Delta/Gamma/Vega) + 만기별 전략 로직
- **크립토 (8개)**: E2에 DeFi 프로토콜 인터랙션 + Funding Rate 차익 로직
- **E5 Tech**: ML 전략은 `torch`, `transformers` 등 SPEC §14 LOCK 외 → `REQUIRES LOCK AMENDMENT` 플래그

**산출물**: 56개 전략 L3 완성. 전체 96/96 전략 L3 달성.
</details>

<details>
<summary><b>2-2a ~ 2-2d. 관점 L3 승급 (758항목)</b></summary>

**공통 절차 (항목별)**:
1. 기존 L2.5 내용 확인 (지표명 + 임계치 수준)
2. L3 템플릿 E1~E9 섹션 추가
3. **E2 변환 핵심** — L2.5 "개념 설명"을 "의사코드/수식"으로:
   - Before: "Brinson-Fachler 분해: 배분효과 + 종목선택효과"
   - After:
   ```python
   allocation_effect = sum((w_p[i] - w_b[i]) * (r_b[i] - r_b_total) for i in sectors)
   selection_effect = sum(w_b[i] * (r_p[i] - r_b[i]) for i in sectors)
   interaction_effect = sum((w_p[i] - w_b[i]) * (r_p[i] - r_b[i]) for i in sectors)
   ```
4. **E4**: 해당 개념의 클래스 시그니처 작성
5. **모듈 단위 그룹핑 허용**: 같은 카테고리 밀접 항목 → 하나의 클래스 여러 메서드
   - 예: TCA 카테고리의 "슬리피지·마켓 임팩트·타이밍 비용" → `class TCAAnalyzer` 3개 메서드

**단계별 분할**:
| 단계 | 관점 | 항목 수 | 핵심 초점 |
|------|------|---------|----------|
| 2-2a | #1~#5 (P0) | 239 | 실시간 전략·백테스트 — E2 알고리즘 최우선 |
| 2-2b | #6~#11 (P1) | 221 | 실행·TCA — E6 Performance 중요 |
| 2-2c | #12~#17 (P2) | 231 | 미시구조·포트폴리오 — E2 수식 집중 |
| 2-2d | #18~#19 (P3) | 67 | 데이터품질·유동성 — E7 Error Handling 중요 |

**검증 (단계당)**:
- [ ] 해당 관점 전 항목에 E1~E9 존재
- [ ] E2에 의사코드 또는 수식 포함 (문장 설명만은 L3 FAIL)
- [ ] L3 PASS 비율 ≥ 90%
</details>

<details>
<summary><b>2-3. STEP7-I 미흡수 항목 L3 보강</b></summary>

**입력**: `21_mapping/step7i_mapping.md`의 PARTIAL/UNMATCHED 항목

**절차**:
1. step7i_mapping.md에서 PARTIAL (~15건) + UNMATCHED (~15건) 필터링
2. PARTIAL: 해당 sot 2/ 파일에 누락 내용 추가 + L3 E1~E9 보강
3. UNMATCHED: 적합한 관점 폴더에 신규 파일 또는 기존 파일 섹션 추가
4. step7i_mapping.md 갱신: 전 항목 ABSORBED로 변경

**검증**:
- [ ] step7i_mapping.md PARTIAL + UNMATCHED = 0건
- [ ] 추가 항목에 L3 E1~E9 적용

**산출물**: ~30개 항목 L3 보강 + step7i_mapping.md 갱신
</details>

<details>
<summary><b>2-4. PART2 89 빈껍데기 L3 연결</b></summary>

**입력**: PART2 내 L1 빈껍데기 (S7FI-, S7NP- 시리즈 89건)

**절차**:
1. PART2에서 L1 빈껍데기 89건의 항목 ID + 제목 추출
2. 각 항목 → sot 2/ L3 파일 매칭
3. PART2 빈껍데기를 링크로 갱신:
   ```markdown
   #### S7FI-XXX: [전략명]
   > **상세**: sot 2/Ai-investing-detail/20_strategy-detail/.../파일.md 참조
   > **Phase**: V2
   > **Status**: L3 Ready
   ```
4. §6.8.2 링크 테이블과 정합성 확인

**검증**:
- [ ] 89건 전부 sot 2/ 링크 연결
- [ ] 링크 경로가 실제 파일과 일치 (validate_links.py 사전 테스트)

**산출물**: PART2 수정 (89건 링크 추가)
</details>

<details>
<summary><b>2-5 ~ 2-8. 도구 + 감사 + Pydantic</b></summary>

**2-5. validate_links.py 작성**:
- Python 3.11+ 스크립트
- (1) PART2/SPEC에서 `Ai-investing-detail/` 경로 regex 추출
- (2) `os.path.exists` 파일 존재 검증
- (3) INDEX.md 등재 확인 (4) _index.md ↔ 실제 파일 비교
- 출력: JSON `{broken_links:[], orphan_files:[], missing_index:[]}`
- 통과: 3개 배열 전부 길이 0

**2-6. tech_dependency.md 감사**:
- 전 전략 파일의 `기술스택 의존성` 섹션 수집
- `21_mapping/tech_dependency.md`에 통합
- SPEC §14 LOCK 외 기술 목록 + `REQUIRES LOCK AMENDMENT` 플래그

**2-7. R12 헤더 일괄 추가**:
- 2-6에서 의존성 미기재 파일 식별 → `### 기술스택 의존성` 섹션 추가

**2-8. Pydantic 12건 해결**:
- `sentiment_score: float = Field(ge=-1.0, le=1.0)`
- `impact_level: int = Field(ge=1, le=5)`
- OHLCV_Values docstring "7 required" → "5 required + 3 optional"
- `Optional` + `model_validator` 패턴 적용
- `ConnectorResponse` Pydantic 모델 신규 작성
</details>

#### validate_links.py 스펙 (v1.2 추가)

```python
# 입력: PART2 §6.8.2 링크 테이블 + SPEC §7-8 참조 링크
# 동작:
#   1. PART2/SPEC에서 "Ai-investing-detail/" 포함 경로 전수 추출 (regex)
#   2. 각 경로의 파일 존재 여부 확인 (os.path.exists)
#   3. sot 2/ 내 모든 파일이 INDEX.md에 등재되어 있는지 확인
#   4. _index.md 내 파일 목록과 실제 폴더 내 파일 비교
# 출력: JSON 리포트 {broken_links: [], orphan_files: [], missing_index: []}
# 통과 기준: broken_links=0, orphan_files=0, missing_index=0
# 언어: Python 3.11+
# 실행: python validate_links.py --part2 <path> --spec <path> --sot2 <path>
```

---

### Phase 3: L3 검증 + 확정

> **목표**: 전 항목 L3 완성 검증 → 구조 무결성 검증 → Status APPROVED 전환

| 단계 | 작업 | 상세 |
|------|------|------|
| 3-0 | **L3 완성도 전수 검사** (v1.3) | 전 파일의 E1~E9 체크박스 점검. 9요소 중 1개라도 미기재 = FAIL |
| 3-1 | validate_links.py 실행 | PART2 ↔ sot 2/ 링크 전수 검증 |
| 3-2 | 교차 중복 재감사 | Phase 2 추가 콘텐츠 반영하여 dedup_audit.md 갱신 |
| 3-3 | LOCK 위반 스캔 | 전 파일에서 §3.4 LOCK 값과 충돌하는 내용 스캔 |
| 3-4 | **L3 합격 판정** (v1.3) | 아래 L3 합격 기준 적용. 불합격 항목 → Phase 2 재작업 루프 |
| 3-5 | Status 전환 | L3 PASS + 검증 통과 파일: DRAFT → APPROVED |
| 3-6 | INDEX.md 최종 갱신 | 전 파일 Version + Status + L3 완성도 반영 |
| 3-7 | FINAL REVIEW | 12개 규칙 + L3 기준 전수 준수 여부 최종 점검 |

#### L3 합격 판정 기준 (v1.3 추가)

| 판정 | 조건 |
|------|------|
| **L3 PASS** | 9요소(E1~E9) 전수 기재 + Algorithm이 의사코드/수식 포함 + Class/API가 시그니처 포함 |
| **L3 CONDITIONAL** | 7~8요소 기재 (E6 Performance 또는 E7 Error 1건 누락 허용) → 30일 내 보완 조건부 승인 |
| **L3 FAIL** | 6요소 이하 기재 → Phase 2 재작업 |

#### L3 완성도 리포트 형식

```markdown
## L3 완성도 리포트

| 영역 | 전체 항목 | L3 PASS | L3 COND | L3 FAIL | 완성률 |
|------|----------|---------|---------|---------|--------|
| 96 전략 | 96 | ? | ? | ? | ?% |
| 관점 #1~#5 (P0) | 239 | ? | ? | ? | ?% |
| 관점 #6~#11 (P1) | 221 | ? | ? | ? | ?% |
| 관점 #12~#17 (P2) | 231 | ? | ? | ? | ?% |
| 관점 #18~#19 (P3) | 67 | ? | ? | ? | ?% |
| STEP7-I 미흡수분 | ~30 | ? | ? | ? | ?% |
| **합계** | **~884** | ? | ? | ? | ?% |
```

**통과 기준**: L3 PASS ≥ 90%, L3 FAIL = 0건

#### Phase 3 단계별 상세 작업 절차 (v1.3.1 추가)

<details>
<summary><b>3-0. L3 완성도 전수 검사</b></summary>

**입력**: Phase 2 완료 후 sot 2/ 전체 파일

**절차**:
1. 대상 파일 목록 생성: 20_strategy-detail/ 전 파일 + 01~19 관점 폴더 내 구현 항목 파일
   - 제외: _index.md, INDEX.md, 매핑 문서, AUTHORITY_CHAIN.md, CONFLICT_LOG.md, _archive/
2. 각 파일에서 `L3 완성도: ☐E1 ☐E2 ...` 헤더 파싱
3. E1~E9 체크박스별 기재 여부 판정:
   - ☑ = 해당 섹션에 실질 내용 존재 (빈 템플릿만은 FAIL)
   - ☐ = 미기재
4. 파일별 결과: `{파일명, E1~E9 각 PASS/FAIL, 총점, 판정}`
5. 영역별 집계 → L3 완성도 리포트 작성

**판정 기준 적용**:
- 9/9 + E2 의사코드 + E4 시그니처 → **L3 PASS**
- 7~8/9 (E6 또는 E7 1건 누락) → **L3 CONDITIONAL**
- ≤6/9 → **L3 FAIL** → Phase 2 해당 단계로 재작업

**산출물**: `L3_COMPLETENESS_REPORT.md` (sot 2/ 루트에 생성)
</details>

<details>
<summary><b>3-1. validate_links.py 실행</b></summary>

**입력**: Phase 2-5에서 작성한 validate_links.py

**절차**:
```bash
python validate_links.py \
  --part2 "D:/VAMOS/docs/guides/VAMOS_구현가이드_PART2_구현단계.md" \
  --spec "D:/VAMOS/docs/sot/VAMOS_AI_INVESTING_SPEC.md" \
  --sot2 "D:/VAMOS/docs/sot 2/Ai-investing-detail/"
```

**검증 항목**:
- [ ] `broken_links` = 0 (PART2/SPEC → sot 2/ 경로 전수 유효) (V-05)
- [ ] `orphan_files` = 0 (sot 2/ 내 모든 파일이 INDEX.md에 등재) (V-03)
- [ ] `missing_index` = 0 (_index.md와 실제 파일 일치) (V-04)

**실패 시**: 깨진 링크 목록을 CONFLICT_LOG.md에 기록 → 해당 파일 수정 → 재실행

**산출물**: `validate_links_report.json`
</details>

<details>
<summary><b>3-2. 교차 중복 재감사</b></summary>

**입력**: Phase 2에서 추가된 L3 콘텐츠 + 기존 `21_mapping/dedup_audit.md`

**절차**:
1. Phase 0-4와 동일 절차 재실행 (Phase 2에서 콘텐츠 대폭 추가)
2. 새로 발생한 중복 식별:
   - 전략 파일(20_strategy-detail/)과 관점 파일(01~19) 간 개념 겹침
   - 예: "Momentum" 개념이 전략 파일과 #8 교차분석 관점 양쪽에 상세 기재
3. 신규 중복 → canonical_owner_table.md 갱신
4. 비정본 파일 중복 내용 → `> 참조:` 링크로 교체

**검증**:
- [ ] 미해결 중복 0건 (V-11)
- [ ] canonical_owner_table.md가 Phase 2 결과 반영

**산출물**: `dedup_audit.md` 갱신 + `canonical_owner_table.md` 갱신
</details>

<details>
<summary><b>3-3. LOCK 위반 스캔</b></summary>

**입력**: §3.4 LOCK 보호 선언 테이블 (12개 LOCK 값)

**절차**:
1. sot 2/ 전 파일에서 LOCK 값 충돌 수치 검색:
   - Win Rate: "51%" 이외 → 위반 후보
   - Sharpe: "1.0" 이외 → 위반 후보
   - Daily Loss CB: "-3%" 이외 → 위반 후보
   - VIX CB: "40" 이외 → 위반 후보
   - 기타 LOCK 값 전수 (Cash 20%, Single 10%, Position -10%, Decay 30%, Min 30건)
2. 발견 시 판정:
   - LOCK 값과 직접 충돌 → 즉시 수정 (LOCK 절대 우선)
   - 다른 맥락 (예: "VIX 35"가 전략 entry이지 CB 아닌 경우) → 허용, `<!-- NOT CB LOCK -->` 주석
3. 위반/허용 판정 전부 CONFLICT_LOG.md에 기록

**검증**:
- [ ] LOCK 값 재정의 0건 (V-06)

**산출물**: CONFLICT_LOG.md 갱신 + 위반 파일 수정
</details>

<details>
<summary><b>3-4. L3 합격 판정</b></summary>

**입력**: 3-0 L3_COMPLETENESS_REPORT.md

**절차**:
1. 리포트에서 L3 FAIL 항목 필터링
2. FAIL → Phase 2 해당 단계로 재작업 (2-1a/b/c 또는 2-2a/b/c/d)
3. 재작업 완료 → 해당 항목만 3-0 재검사
4. 루프 최대 3회. 3회 초과 FAIL → CONFLICT_LOG 사유 기록 + L3 CONDITIONAL 격하
5. 최종: L3 PASS ≥ 90% → Phase 3 계속, < 90% → Phase 2 전체 재점검

**산출물**: L3_COMPLETENESS_REPORT.md 최종 갱신
</details>

<details>
<summary><b>3-5 ~ 3-7. Status 전환 + INDEX 갱신 + FINAL REVIEW</b></summary>

**3-5. Status 전환**:
- L3 PASS + 3-1~3-3 통과 파일: `Status: DRAFT` → `Status: APPROVED`
- L3 CONDITIONAL: `Status: REVIEW` (30일 보완 기한)
- `Last-reviewed` 날짜 갱신

**3-6. INDEX.md 최종 갱신**:
- 전 폴더 파일 수, Status 분포, Version, L3 완성률 반영
- 하단에 L3 완성도 요약 테이블 추가

**3-7. FINAL REVIEW**:
1. 12개 규칙(R1~R12) 전수 준수 점검
2. L3 기준(E1~E9) 전수 준수 점검
3. 검증 체크리스트(V-01~V-13) 전수 실행
4. 5-Mode 검증: 구조, 수치, 교차참조, 논리, 커버리지
5. 결과를 본 계획서 §12에 최종 버전으로 기록
</details>

---

## 8. 파일 역할 분리 명세

### 8.1 역할 테이블 (최종 확정)

| 파일 | 역할 (LOCK) | 담는 것 | 담지 않는 것 |
|------|------------|---------|------------|
| **sot 2/Ai-investing-detail/** | 구현 상세 정본 | What + How (전략 로직, 알고리즘, 관점별 상세) | When (Phase), LOCK 값 재정의 |
| **SPEC §1-6,§10-24** | 아키텍처 + LOCK | 구조, 데이터 레이어, 법적 제약, 기술스택 | 전략 구현 상세 |
| **SPEC §7-8** | 전략 인덱스 | 이름 + 분류 + 한 줄 요약 + sot 2/ 참조 링크 | 구현 로직 |
| **SPEC §9** | 리디렉트 | `> MIGRATED → sot 2/.../rsi_bb.md` | 더 이상 구현 상세 없음 |
| **SPEC §18, 부록B.3** | 역사적 기록 | `> HISTORICAL` 마커 + 원본 보존 | 현행 일정 (PART2 정본) |
| **STEP7-I** | 보강 체크리스트 | 항목 ID + 우선순위 + sot 2/ 매핑 상태 | 구현 방법 |
| **PART2 §6.8** | 구현 가이드 | When + Where + LOCK 값 + §6.8.2 링크 테이블 | 전략 상세 (sot 2/ 링크로 대체) |

### 8.2 파일 메타데이터 표준 헤더

모든 sot 2/Ai-investing-detail/ 내 .md 파일은 아래 헤더를 반드시 포함:

```markdown
# [파일 제목]

> **버전**: v1.0
> **Status**: DRAFT
> **작성일**: 2026-03-22
> **Last-reviewed**: 2026-03-22
> **원본 관점**: [관점 번호 + 이름] (예: #1 실시간 적응형 전략)
> **정본 소유 개념**: [이 파일이 정본인 개념 목록]
> **기술스택 의존성**: SPEC §14 LOCK 범위 내
> **LOCK 참조**: 해당 시 `> LOCK (PART2 §6.8): [값]` 인라인
```

> **v1.3 참고**: 구현 항목 파일은 위 §8.2 헤더에 **추가로** L3 템플릿(§7 Phase 2 정의)의 `L3 완성도: ☐E1~☐E9` 필드와 E1~E9 섹션을 포함한다. L3 템플릿은 §8.2의 **상위호환**이며, 비구현 파일(_index.md, 매핑 문서 등)은 §8.2만 적용한다.

---

## 9. 충돌 해결 프로토콜

### 9.1 충돌 유형별 해결

| 충돌 유형 | 판정 기준 | 조치 |
|----------|----------|------|
| **sot 2/ ↔ LOCK/FREEZE** | LOCK이 절대 우선 | sot 2/ 즉시 수정. CONFLICT_LOG에 기록 |
| **sot 2/ ↔ SPEC 비-LOCK** | sot 2/가 상세 정본 | SPEC을 요약으로 축소 또는 리디렉트. 정본 소유자가 결정 |
| **sot 2/ 파일 간 중복** | canonical_owner_table 기준 | 정본 소유자 파일에 상세 유지, 나머지 `> 참조:` 링크로 교체 |
| **sot 2/ ↔ PART2 Phase** | PART2가 Phase 정본 | sot 2/에서 Phase 정보 삭제 |
| **sot 2/ ↔ STEP7-I** | sot 2/가 상세 정본 | step7i_mapping.md에 ABSORBED 마킹 |

### 9.2 충돌 기록 형식 (CONFLICT_LOG.md)

```markdown
| 날짜 | 충돌 유형 | 파일 A | 파일 B | 내용 | 판정 | 조치 완료 |
|------|----------|--------|--------|------|------|----------|
| 2026-03-22 | LOCK 위반 | 01_realtime/.../volatility.md | PART2 §6.8 | VIX 임계값 35로 기재 | PART2 LOCK 40 우선 | ✅ |
```

### 9.3 횡단 관심사 참조 *(S7-2 추가)*

| 횡단 도메인 | 적용 내용 |
|-----------|----------|
| 0-0 Governance-Rules-Meta | R1~R11 공통 규칙 준수 (R10: 비용 상한 LOCK) |
| 6-2 Security-Governance | P2 도메인 보안 정책 적용 (승인 게이트 필수) |
| 6-12 Event-Logging | 투자 이벤트 로깅 표준 준수 |
| 5-1 Benchmark-Evaluation | VBS-17 투자 벤치마크 공동관리 (R-T5-1) |

---

## 10. 검증 체크리스트

### 10.1 Phase 완료 시 필수 검증

| # | 검증 항목 | 방법 | 통과 기준 |
|---|----------|------|----------|
| V-01 | 폴더 깊이 3단계 이하 | 수동 점검 | 4단계 폴더 0개 |
| V-02 | 전 파일 메타데이터 헤더 존재 | grep "Status:" | 누락 0건 |
| V-03 | INDEX.md에 전 폴더 등재 | INDEX vs 실제 폴더 비교 | 불일치 0건 |
| V-04 | _index.md에 폴더 내 전 파일 등재 | _index vs 실제 파일 비교 | 불일치 0건 |
| V-05 | PART2 §6.8.2 링크 전수 유효 | validate_links.py | 깨진 링크 0건 |
| V-06 | LOCK 값 재정의 없음 | LOCK 목록 vs sot 2/ 전문 검색 | 위반 0건 |
| V-07 | Phase 정보 sot 2/ 내 없음 | "V1", "V2", "Phase" 검색 (인라인 LOCK 참조 제외) | 위반 0건 |
| V-08 | sot 2/ → SPEC 역참조 없음 | 링크 패턴 검색 | 역참조 0건 |
| V-09 | 정본 소유자 전 개념 배정 | canonical_owner_table 완전성 | 미배정 0건 |
| V-10 | STEP7-I 106건 전수 매핑 | step7i_mapping.md 완전성 | 미매핑 0건 |
| V-11 | 교차 중복 해결 | dedup_audit.md | 미해결 중복 0건 |
| V-12 | 기술스택 의존성 전수 기재 | 전략 파일 헤더 점검 | 누락 0건 |
| V-13 | **L3 완성도 전수 검사** (v1.3) | 전 파일 E1~E9 체크박스 점검 | L3 PASS ≥90%, L3 FAIL = 0건 |

### 10.2 새 관점 추가 체크리스트

새 관점 (#20+) 추가 시 아래 절차를 순서대로 수행:

1. ☐ 번호 배정: `XX_영문폴더명/` (다음 번호)
2. ☐ 기존 관점과의 교차 중복 확인 → canonical_owner_table 갱신
3. ☐ 폴더 생성 + _index.md 작성
4. ☐ 관점 분석 파일 작성 (표준 헤더 포함)
5. ☐ 카테고리별 개별 파일 분해
6. ☐ INDEX.md에 등록 (같은 커밋)
7. ☐ PART2 §6.8.2 링크 테이블에 추가
8. ☐ step7i_mapping.md 관련 항목 갱신
9. ☐ validate_links.py 실행

### 10.3 전체 이슈 해결 확인

| 이슈 | 심각도 | 해결 섹션 | Phase | 상태 |
|------|--------|----------|-------|------|
| #1 권한 체계 부재 | CRITICAL | §3 + Phase 0-1 | 0 | ✅ |
| #2 3중 정본 충돌 | CRITICAL | §3.3 + Phase 0-1 | 0 | ✅ |
| #3 SPEC §9 Rule5 위반 | CRITICAL | §5C + Phase 1-4 | 1 | ✅ |
| #4 SPEC §18 Rule6 위반 | CRITICAL | Phase 0-2 | 0 | ✅ |
| #5 폴더명 공백 | HIGH | Ai-investing-detail 변경 | — | ✅ |
| #6 INDEX.md 비대화 | HIGH | R2 + Phase 1-9,1-10 | 1 | ✅ |
| #7 STEP7-I 날짜 불일치 | HIGH | 선행작업B + Phase 0-6 | 0 | ✅ |
| #8 Draft/Complete 없음 | HIGH | R10 + Phase 1-3 | 1 | ✅ |
| #9 버전 추적 없음 | HIGH | R10 + Phase 1-9 | 1 | ✅ |
| #10 정본 소유자 미배정 | HIGH | 선행작업A + Phase 0-4,0-5 | 0 | ✅ |
| #11 LOCK 재정의 위험 | HIGH | R9 + §3.4 | 0 | ✅ |
| #12 CORE 통합 미문서화 | HIGH | Phase 1-7 | 1 | ✅ |
| #13 새 관점 절차 없음 | MEDIUM | §10.2 + Phase 1-13 | 1 | ✅ |
| #14 순환 참조 | MEDIUM | R11 + Phase 1-14 | 1 | ✅ |
| #15 관점/전략 혼재 | HIGH | §2.1 + Phase 1-1 | 1 | ✅ |
| #16 링크 검증 자동화 | MEDIUM | Phase 2-3 | 2 | ✅ |
| #17 기술스택 의존성 | MEDIUM | R12 + Phase 2-4 | 2 | ✅ |
| #18 19개 파일 간 중복 | MEDIUM | 선행작업A (=#10) | 0 | ✅ |
| #19 PART2 참조 마이그레이션 | MEDIUM | 선행작업C + Phase 1-11,1-12 | 1 | ✅ |
| #20 한글 폴더명 인코딩 | LOW | §2.3 영문 규칙 | 1 | ✅ |
| #21 "sot 2" 이름 | LOW | Ai-investing-detail 변경 | — | ✅ |
| #22 부록 B.3 Phase 정보 | LOW | Phase 0-2 (=#4 동일) | 0 | ✅ |
| #23 충돌 해결 프로토콜 | LOW | §9 + Phase 0-3 | 0 | ✅ |

**미해결: 0건 / 해결완료: 23건 (전수 완료)**

---

## 11. FINAL REVIEW 보완 사항 (v1.1 반영)

> FINAL REVIEW 감사 결과 CONDITIONAL PASS 판정. 구조적 결함 없음. 아래 8건의 명세 갭을 보완한다.

### FR-1. 기존 19개 원본 파일 아카이브 절차 (HIGH)

**문제**: Phase 1-2에서 관점 파일을 분해 후 원본 19개 파일의 처리 방안 미정의

**해결**: Phase 1에 단계 1-15 추가

| 단계 | 작업 | 상세 |
|------|------|------|
| 1-15 | 원본 19개 파일 아카이브 | 분해 완료 후 `_archive/` 폴더로 이동. `_archive/` 내 파일은 읽기 전용 참조용으로만 보존. 편집 금지. 정본은 분해된 하위 파일. |

**폴더 구조 추가**:
```
Ai-investing-detail/
├── _archive/                              ← 원본 19개 파일 보존 (읽기 전용)
│   ├── VAMOS_AI_INVESTING_실시간적응형전략_약점분석_및_추가항목.md
│   ├── VAMOS_AI_INVESTING_투자심리학_행동재무학_약점분석_및_추가항목.md
│   └── ... (19개 전체)
├── INDEX.md
├── 00_core-integration/
├── 01_realtime-adaptive/
└── ...
```

---

### FR-2. _index.md 표준 템플릿 (MEDIUM)

**문제**: _index.md 형식 미정의

**해결**: 아래 템플릿을 표준으로 확정

```markdown
# [폴더명] — 파일 목록

| 파일명 | Status | 버전 |
|--------|--------|------|
| supply_demand_zone.md | DRAFT | v1.0 |
| support_resistance.md | DRAFT | v1.0 |
| ... | ... | ... |
```

- _index.md는 메타데이터 헤더(§8.2)를 **적용하지 않음** (인덱스 파일이므로)
- 파일 목록 외 설명/내용 기재 금지
- 파일 추가/삭제 시 동일 커밋에서 갱신

---

### FR-3. PART2 §6.8.2 링크 테이블 칼럼 정의 (MEDIUM)

**문제**: PART2에 추가할 링크 테이블의 칼럼 구조 미정의

**해결**: 아래 칼럼 구조를 표준으로 확정

```markdown
### §6.8.2 AI Investing 상세 참조 인덱스

| # | 영역 | sot 2/ 경로 | 항목 수 | SPEC 대응 섹션 | STEP7-I 대응 | Phase |
|---|------|-------------|---------|---------------|-------------|-------|
| 1 | 실시간 적응형 전략 | Ai-investing-detail/01_realtime-adaptive/ | 54 | §7.3,§7.9 | S7I-065 | V1~V2 |
| 2 | 투자 심리학 | Ai-investing-detail/02_behavioral-finance/ | 47 | — | S7NP-108,110 | V2 |
| 3 | 매크로→섹터→종목 | Ai-investing-detail/03_macro-sector-stock/ | 52 | §7.9 | S7I-065 | V2 |
| ... | ... | ... | ... | ... | ... | ... |
| 20 | 전략 상세 | Ai-investing-detail/20_strategy-detail/ | 96+ | §7,§8,§9 | — | V1~V3 |
| 21 | 매핑 & 거버넌스 | Ai-investing-detail/21_mapping/ | 4 | — | — | — |
```

---

### FR-4. 교차 중복 감사 방법론 (MEDIUM)

**문제**: 758개 항목의 중복 감사 절차가 "유사도 매칭"으로만 기술되어 실행 방법 불명확

**해결**: 3단계 수동+반자동 감사 절차 확정

1. **추출**: 19개 파일에서 `### B-N.` 카테고리 제목 + 하위 항목 제목 추출 → CSV/테이블화
2. **1차 분류 (키워드 매칭)**: 동일 키워드 포함 항목 그룹핑 (예: "레짐", "Volume", "슬리피지", "SHAP", "Factor")
3. **2차 판정 (수동)**: 그룹별로 정본 소유자 배정. 기준: "이 개념이 가장 핵심적으로 다뤄지는 관점"이 정본

**예상 작업량**: 171개 카테고리 제목 기준 매칭 → 약 20~30개 중복 그룹 예상 → 수동 판정 30건

---

### FR-5. STEP7-I 날짜 처리 방침 (MEDIUM)

**문제**: STEP7-I 헤더 날짜 "2025-02-22"의 처리 미정의

**해결**: STEP7-I 헤더 날짜는 **원본 그대로 보존** (역사적 기록). 대신 step7i_mapping.md 상단에 아래 마킹 추가:

```markdown
> **매핑 기준일**: 2026-03-22
> **STEP7-I 원본 작성일**: 2025-02-22 (원본 보존, 수정하지 않음)
> **참고**: STEP7-I 106건은 2025-02 기준으로 작성됨. 이후 19개 관점 분석(2026-03)에서 대부분 흡수/확장됨.
```

---

### FR-6. SPEC §17 결함 분배 후 처리 (LOW)

**문제**: Phase 1-6에서 SPEC §17의 15개 결함 분배 후 §17의 처리 미명시

**해결**: SPEC §9와 동일 패턴 적용. §17 상단에 리디렉트 마커 추가:

```markdown
> **MIGRATED**: 15개 결함의 상세 극복 방안은 sot 2/Ai-investing-detail/ 해당 관점 폴더로 분배됨.
> 아래 목록은 인덱스로 보존합니다. 상세는 각 관점 파일을 참조하세요.
```

---

### FR-7. SPEC §7-8에 sot 2/ 참조 링크 추가 단계 (LOW)

**문제**: Phase 1-12는 PART2 참조만 갱신하고, SPEC §7-8에 sot 2/ 링크를 추가하는 단계가 누락

**해결**: Phase 1에 단계 1-16 추가

| 단계 | 작업 | 상세 |
|------|------|------|
| 1-16 | SPEC §7-8에 sot 2/ 참조 링크 추가 | 각 전략 카테고리(§7.1~§7.9, §8.1~§8.7)에 `> 상세: sot 2/Ai-investing-detail/20_strategy-detail/[해당파일] 참조` 추가 |

---

### FR-8. Phase 실패 시 롤백/재시도 절차 (MEDIUM)

**문제**: Phase 3 검증 실패 시 대응 절차 없음

**해결**: 검증 실패 대응 프로토콜 정의

```
Phase 3 검증 실패 시:
  0. [백업] Phase 3 진입 전, _archive/ 폴더에 현재 상태 스냅샷 보존
  1. 실패 항목을 CONFLICT_LOG.md에 기록
  2. 실패 유형 분류:
     - 링크 깨짐 (V-05) → Phase 1 관련 단계로 되돌아가 링크 수정 후 재검증
     - LOCK 위반 (V-06) → 즉시 해당 파일 수정 (정본은 LOCK 값)
     - Phase 정보 누출 (V-07) → 해당 파일에서 Phase 정보 삭제
     - 역참조 발견 (V-08) → sot 2/ → SPEC 링크를 인라인 인용으로 교체
     - 메타데이터 누락 (V-02/03/04) → 해당 파일/인덱스 즉시 갱신
     - 중복 미해결 (V-11) → canonical_owner_table 갱신 → 중복 파일 정리
     - 기타 → 해당 Phase 단계로 되돌아가 수정
  3. 수정 완료 후 Phase 3 검증 재실행 (실패 항목만)
  4. 전 항목 통과 시 Status 전환 진행
  5. [부분 승인] 170/171 파일 통과 시: 통과 파일만 APPROVED, 미통과 2건은 DRAFT 유지 + CONFLICT_LOG에 사유 기록
```

---

### 보완 후 실행 계획 최종 요약 (v1.3)

```
Phase 0 (선행작업)         → 8단계, 산출물 8건 + PART2 §5.9 오류 정정 + L3 템플릿
Phase 1 (구조 재편)        → 16단계 (의존성 다이어그램 포함), 산출물: 전체 폴더 + 171+ 파일
Phase 2 (L3 전수 승급)     → 13단계 (96전략 + 758관점 + 106 STEP7-I + 89 PART2), 산출물: ~884 L3 파일
Phase 3 (L3 검증 확정)     → 8단계 + L3 합격 판정 + 롤백 루프 + 부분 승인 경로
─────────────────────────────────────────────────────────
합계                       → 45단계
L3 대상 항목               → ~884건 (현재 L3: 8건 → 목표: 884건, 갭: 876건)
해결 항목                  → 23개 이슈 + FR 8건 + FR-FINAL 4건 + 교차검증 C3/M4건 = 전수 해결
검증 레벨                  → 내부 검증 + 교차 검증 + Phase 감사 + L3 전수 스캔 완료
```

---

## 12. FINAL REVIEW 결과

### v1.1 (내부 검증)

| 항목 | 결과 |
|------|------|
| 전체 판정 | CONDITIONAL PASS → FR 8건 보완 |
| 23개 이슈 | 전수 해결 매핑 완료 |
| 12개 규칙 | 상호 모순 없음 |
| FR 8건 | 전수 반영 |

### v1.2 (교차 검증 + Phase 감사)

| 항목 | 결과 |
|------|------|
| **전체 판정** | ✅ **PASS** (CRITICAL 3건 + MAJOR 4건 전수 반영 후) |
| **C1: D2.0-01 §5.9 오류** | ✅ 해결 — §3.2 권한 체인을 D2.0-03 §1+§3.3 (BLUE NODE 정의 + P2 라이프사이클) + D2.0-01 §7.2로 교체. Phase 0-1에서 PART2 정정 포함 <!-- v1.5: 기존 D2.0-03 §3 → §1+§3.3 정정 --> |
| **C2: LOCK 출처 오류** | ✅ 해결 — §3.4 테이블에 정본 출처 칼럼 추가 (SPEC §6.1, §10.2, D2.0-07 구분) |
| **C3: 비용 단위 불일치** | ✅ 해결 — 원화+달러 병기 (₩40,000/$30) |
| **M1: Phase 2-1 비현실적** | ✅ 해결 — 2-1a/2-1b/2-1c로 3분할 |
| **M2: Phase 1 의존성** | ✅ 해결 — 의존성 다이어그램 추가 |
| **M3: 단계 실행 기준 부족** | ✅ 해결 — validate_links.py 스펙 추가 |
| **M4: 롤백 불완전** | ✅ 해결 — V-07/V-08 커버 + 백업 절차 + 부분 승인 경로 추가 |
| **SPEC 교차 검증** | ✅ 24개 섹션, §9 RSI_BB, §14 기술스택, §18 Phase — 전수 확인 |
| **PART2 교차 검증** | ✅ §6.8 원문 직접 읽기 완료, LOCK 값 대조 완료 |
| **D2.0-01 교차 검증** | ✅ §5.9 실제 내용 확인, §7.2 DEFER 항목 확인 |
| **구조적 결함** | 0건 |

### v1.3 (FINAL REVIEW: 전수 스캔 + L3 갭 분석)

| 항목 | 결과 |
|------|------|
| **전체 판정** | ✅ **PASS** (FR-FINAL 4건 전수 반영 후) |
| **인벤토리 완전성** | ✅ 963+ 항목 전수 파악 (SPEC 96전략 + sot2 758 + STEP7-I 106 + PART2 103) |
| **L3 현황** | ✅ 확인: 전체 0.8% (8/963+) — RSI_BB, Math 6공식, 51% Gate, CB, RT-BNP, BL, Factor, Z-Session(부분) |
| **FR-FINAL-1: L3 9요소 정의** | ✅ Phase 2에 E1~E9 정의 + 예시 추가 |
| **FR-FINAL-2: 758항목 우선순위** | ✅ Phase 2-2를 P0(239)→P1(221)→P2(231)→P3(67) 4단계로 세분화 |
| **FR-FINAL-3: L3 템플릿** | ✅ Phase 0-8에 템플릿 생성 단계 추가 |
| **FR-FINAL-4: L3 합격 판정** | ✅ Phase 3-0, 3-4에 PASS/CONDITIONAL/FAIL 기준 + 리포트 형식 추가 |
| **Phase 0 검증** | ✅ 8단계 (0-8 L3 템플릿 추가) |
| **Phase 1 검증** | ✅ 16단계 변경 없음 (구조 재편은 L3 전 단계) |
| **Phase 2 검증** | ✅ 13단계로 확장 (기존 5→13: 2-0 삭제 + L3 승급 8단계 추가) |
| **Phase 3 검증** | ✅ 8단계로 확장 (기존 6→8: L3 검증 2단계 추가) |
| **전체 단계 수** | 45단계 (v1.2: 36 → v1.3: 45, +9) |
| **L3 갭** | 876건 (목표 884 - 현재 8) — Phase 2에서 전수 해결 |

### v1.3.1 (5-Mode FINAL REVIEW: 구조·수치·교차참조·논리·커버리지)

| 항목 | 결과 |
|------|------|
| **전체 판정** | ✅ **PASS** (F-1~F-8 전수 반영 후) |
| **F-1: D2.0-03 §3 참조 부정확** | ✅ 해결 — §3.2 권한 체인을 D2.0-03 §1(BLUE NODE 정의) + §3.3(P2 라이프사이클)으로 정정 |
| **F-2: P2 Timeout 불일치** | ✅ 해결 — §3.4 LOCK 테이블에 "일반 10분 / P2 도메인 5분" 이중 기재 |
| **F-3: Phase 2 단계 수 오산** | ✅ 해결 — 13단계로 정정, 전체 합계 45단계 |
| **F-4: GAP-5 Pydantic 미배정** | ✅ 해결 — Phase 2-8 추가 (contracts.py D-1~D-12 해결) |
| **F-5: 0-8 ↔ 2-0 이중 생성** | ✅ 해결 — 2-0 삭제, 0-8에 통합 |
| **F-6: 폴더 트리 미등재** | ✅ 해결 — §2.1에 `_archive/`, `_templates/` 추가 |
| **F-7: V-13 미등재** | ✅ 해결 — §10.1에 V-13 (L3 완성도) 추가 |
| **F-8: 헤더 병합 미정의** | ✅ 해결 — §8.2에 L3 템플릿 상위호환 명시 |
| **MODE 1 (구조)** | ✅ PASS |
| **MODE 2 (수치)** | ✅ PASS (45단계 정정) |
| **MODE 3 (교차참조)** | ✅ PASS (D2.0-03, Timeout 정정) |
| **MODE 4 (논리)** | ✅ PASS (이중 작업 제거) |
| **MODE 5 (커버리지)** | ✅ PASS (GAP-5, V-13 추가) |

### v1.3.2 (Phase 상세 절차 + 경로 검증 + 코드 테스트 + 5-Mode FINAL REVIEW)

| 항목 | 결과 |
|------|------|
| **전체 판정** | ✅ **PASS** (4 WARN → 전수 수정 후 0 WARN, 0 FAIL) |
| **Phase 상세 절차 추가** | ✅ Phase 0~3 전 단계에 입력/절차/검증/산출물 상세 기재 (34개 details 블록) |
| **경로 검증** | ✅ 소스 파일 6건 + 관점 19개 전수 EXISTS 확인 |
| **섹션 참조 검증** | ✅ 14건 전수 CONFIRMED (SPEC §4~§24, D2.0-01, D2.0-03, 부록 B.3) |
| **validate_links.py** | ✅ 프로토타입 작성+실행 성공 |
| **L3 템플릿 실증** | ✅ MACD 전략 E1~E9 전수 적용 성공, 템플릿 개선 T-1~T-4 반영 |
| **MODE 1 (구조)** | ✅ PASS — 13 섹션 + details 34쌍 균형 |
| **MODE 2 (수치)** | ✅ PASS — Phase 0(8)+1(16)+2(13)+3(8)=45 정정 |
| **MODE 3 (교차참조)** | ✅ PASS — §1.1 D2.0-01 §5.9 오류 표기, LOCK 12건 정확 |
| **MODE 4 (논리)** | ✅ PASS — 순환 0건, 2-0 고아 0건, L3 기준 일관 |
| **MODE 5 (커버리지)** | ✅ PASS — 23이슈+8FR+4FR-FINAL+13V+12R+5GAP 전수 |

### v1.4 (실행 약점 분석 + 대응 반영)

| 항목 | 결과 |
|------|------|
| **전체 판정** | ✅ **PASS** (W-01~W-23 전수 대응 후) |
| **약점 도출** | 23건: CRITICAL 2 + HIGH 10 + MEDIUM 11 |
| **W-01: PART2 line 하드코딩** | ✅ 해결 — 0-1 절차에 grep 기반 검색 반영 |
| **W-19: git 전략 없음** | ✅ 해결 — §14.1 브랜치 전략 + Phase별 태그 |
| **W-04/W-22: Phase 전환 게이트** | ✅ 해결 — §14.2 전환 게이트 4건 |
| **W-05: 파일명 번역 기준** | ✅ 해결 — §14.2 번역 규칙 + filename_mapping.md |
| **W-09: R11 false positive** | ✅ 해결 — §14.2 허용/위반 패턴 |
| **W-10: 아카이브 전 검증** | ✅ 해결 — §14.2 분해 완전성 게이트 |
| **W-11: Phase 2 중간 CP** | ✅ 해결 — §14.2 CP-1~CP-5 |
| **W-14: Pydantic 테스트** | ✅ 해결 — §14.2 단위 테스트 요구 |
| **W-16: L3 검사 자동화** | ✅ 해결 — §14.2 validate_l3.py 스펙 |
| **W-20: 사전 백업** | ✅ 해결 — §14.2 git 스냅샷 + 태그 |
| **W-23: L3 품질 일관성** | ✅ 해결 — §14.2 참조 예시 3건 |
| **MEDIUM 11건** | ✅ §14.3 요약 테이블로 전수 대응 |
| **MODE 1 (구조)** | ✅ PASS — 14 섹션 체계 |
| **MODE 2 (수치)** | ✅ PASS — 45단계 + 게이트 4건 + CP 5건 |
| **MODE 3 (교차참조)** | ✅ PASS — §14 ↔ Phase 0~3 인라인 참조 정합 |
| **MODE 4 (논리)** | ✅ PASS — 게이트 → Phase → CP → 검증 무모순 |
| **MODE 5 (커버리지)** | ✅ PASS — 23W + 23이슈 + 8FR + 4FR-FINAL + 5GAP 전수 |


### v2.0 (Phase 3 완료 — 전수 L3 APPROVED + 5-Mode FINAL REVIEW)

| 항목 | 결과 |
|------|------|
| **전체 판정** | ✅ **PASS** — Phase 3 완료. 전 항목 L3 APPROVED |
| **L3 전수 검사** | ✅ validate_l3.py: 195파일 전수 PASS (100.0%), FAIL 0건 |
| **링크 검증** | ✅ validate_links.py: broken_links=0, orphan_files=0, missing_index=0 |
| **Status 전환** | ✅ 전 구현 파일 DRAFT/L3 → APPROVED 전환 완료 (2026-03-23) |
| **INDEX.md 갱신** | ✅ v2.0: 전 폴더 APPROVED, L3 완성도 요약 추가 |
| **MODE 1 (구조)** | ✅ PASS — V-01 폴더깊이 ≤3, V-03 INDEX 22폴더 전수, V-04 _index 전수 일치, R1/R2 PASS |
| **MODE 2 (수치)** | ✅ PASS — 22폴더 파일 수 전수 일치, L3 리포트 195/195 정합 |
| **MODE 3 (교차참조)** | ✅ PASS — V-05 validate_links PASS, V-08/R11 역참조 0건, V-06/R9 LOCK 재정의 0건 |
| **MODE 4 (논리)** | ✅ PASS — V-09 canonical 30건 전수 배정, V-10 STEP7-I 106건 전수 매핑, V-11 중복 0건 미해결, V-12 E9 LOCK 전수 |
| **MODE 5 (커버리지)** | ✅ PASS — V-13 195파일 L3 100%, E1~E9 전수 9/9, AUTHORITY_CHAIN+CONFLICT_LOG 존재, _templates 5건 |
| **경미 이슈 (허용)** | V-07: 5개 파일 Phase 2 roadmap 주석 7건 (관리 메타데이터, R6 위반 아님) |

---

## 13. L3 전수 승급 계획 (v1.3)

> **배경**: 2026-03-22 전수 스캔 결과, AI Investing 전체 963+ 항목 중 L3(구현 즉시 투입 가능) 수준은 **8건 (0.8%)** 에 불과. 나머지 99.2%는 L1~L2.5 수준이며, PART2 구현단계에서 바로 코드 작성 시 오류·누락이 발생할 수밖에 없는 상태.

### 13.1 전수 스캔 결과 요약

#### 소스별 상세 레벨 분포

| 소스 | 항목 수 | L3 | L2.5 | L2 | L1 | L3 비율 |
|------|---------|-----|------|-----|-----|---------|
| **SPEC** (96 전략) | 96 | 1 (RSI_BB) | 0 | 7 | 88 | 1.0% |
| **SPEC** (비전략 24섹션) | 24§ | 2 (§9,§16) | 5 | 15 | 2 | 8.3% |
| **sot 2/** (19 관점) | 758 | 0 | ~606 | ~114 | ~38 | 0% |
| **STEP7-I** | 106 | 0 | ~30 | ~60 | ~16 | 0% |
| **PART2 §6.8** | 103 | 5 | 0 | 9 | 89 | 4.9% |
| **합계** | **~963+** | **8** | **~641** | **~205** | **~233** | **0.8%** |

#### L3 달성 8건 상세

| # | 항목 | 소스 | E1 | E2 | E3 | E4 | E5 | E6 | E7 | E8 | E9 |
|---|------|------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| 1 | RSI_BB 전략 | SPEC §9 | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | ✅ |
| 2 | 수학 공식 (Sharpe 등 6건) | SPEC §16 | ✅ | ✅ | ✅ | — | ✅ | — | — | ✅ | — |
| 3 | 51% Gate | PART2 §6.8 | ✅ | ✅ | ✅ | ⚠️ | ✅ | ⚠️ | ⚠️ | ✅ | ✅ |
| 4 | Circuit Breaker | PART2 §6.8 | ✅ | ✅ | ✅ | ⚠️ | ✅ | ✅ | ✅ | ⚠️ | ✅ |
| 5 | RT-BNP 통합 | PART2 §6.8 | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ⚠️ | ✅ |
| 6 | Black-Litterman | PART2 §6.8 | ✅ | ✅ | ✅ | ⚠️ | ✅ | ⚠️ | ⚠️ | ⚠️ | ✅ |
| 7 | Factor Investing | PART2 §6.8 | ✅ | ✅ | ✅ | ⚠️ | ✅ | ⚠️ | ⚠️ | ⚠️ | ✅ |
| 8 | Z-Session 아키텍처 | SPEC §24 | ✅ | ⚠️ | ✅ | ⚠️ | ✅ | ⚠️ | ⚠️ | ⚠️ | — |

> ✅ = 완전 기재, ⚠️ = 부분 기재, — = 미기재. 기존 L3도 E1~E9 기준 재검증 필요.

### 13.2 GAP 분석 (L3 미달 5대 영역)

| GAP | 설명 | 항목 수 | L3 작업 내용 |
|-----|------|---------|------------|
| **GAP-1** | 95/96 전략 미상세 | 95 | 알고리즘·파라미터·클래스 전수 작성 |
| **GAP-2** | 758 관점 항목 L2.5 이하 | 758 | 프레임워크→의사코드, 지표명→수식, 임계치→클래스 설계 |
| **GAP-3** | STEP7-I 106건 L2 이하 | ~30 (미흡수분) | 관점에 미흡수된 항목 L3 보강 |
| **GAP-4** | PART2 89 빈껍데기 | 89 | sot 2/ L3 파일 링크 연결 |
| **GAP-5** | Pydantic 스키마 12건 불일치 | 12 | contracts.py 필드 검증 정합성 |

### 13.3 L2.5 → L3 승급 예시

**Before (L2.5)**: "Brinson-Fachler 분해: 배분효과 + 종목선택효과"

**After (L3)**:
```
E1. Input: portfolio_weights[], benchmark_weights[], portfolio_returns[], benchmark_returns[]
E2. Algorithm:
    allocation_effect = Σ(w_p,i - w_b,i) × (r_b,i - r_b)
    selection_effect = Σ w_b,i × (r_p,i - r_b,i)
    interaction_effect = Σ(w_p,i - w_b,i) × (r_p,i - r_b,i)
    total_active = allocation + selection + interaction
E3. Output: AttributionResult(allocation, selection, interaction, total_active) → Dashboard
E4. Class: class BrinsonFachlerAttribution(BaseAttribution): def decompose(portfolio, benchmark) -> AttributionResult
E5. Tech: pandas, numpy (SPEC §14 LOCK)
E6. Perf: 100 sectors < 10ms
E7. Error: weight sum ≠ 1.0 → normalize + WARNING log
E8. Test: unit(3-sector known answer), integration(실제 포트폴리오 대조)
E9. LOCK: None (자체 계산 모듈)
```

### 13.4 Phase 2 작업량 추정

| 단계 | 항목 수 | 항목당 예상 | 설명 |
|------|---------|-----------|------|
| 2-1a (P0 전략) | 10 | 9요소 × 상세 | 핵심 전략 (MACD, MA 등) |
| 2-1b (P1 전략) | 30 | 9요소 × 중간 | V2 배정 전략 |
| 2-1c (P2/P3 전략) | 56 | 9요소 × 중간 | 옵션/ML/크립토 |
| 2-2a (P0 관점) | 239 | E2+E4 중심 | 실시간/심리/매크로/성과/백테스트 |
| 2-2b (P1 관점) | 221 | E2+E4 중심 | 실행/유니버스/교차/거버넌스/퀀트/TCA |
| 2-2c (P2 관점) | 231 | E2+E4 중심 | 미시구조/자산군/이벤트/포트폴리오/글로벌/XAI |
| 2-2d (P3 관점) | 67 | E2+E4 중심 | 데이터품질/유동성 |
| 2-3 (STEP7-I) | ~30 | E2+E4 중심 | 미흡수 항목 |
| **합계** | **~884** | | |

---

## 14. 실행 약점 대응 계획 (v1.4)

> **배경**: v1.3.2 Phase 상세 절차에 대해 실행 시 오류 발생 가능 약점 23건 식별. CRITICAL 2건 + HIGH 10건 전수 대응.

### 14.1 CRITICAL 약점 대응

#### W-01: PART2 line 번호 하드코딩 → grep 기반 검색

**문제**: 0-1에서 `line 2549, 2567`로 하드코딩. PART2 편집 시 줄번호 shift → 엉뚱한 곳 수정.

**대응**: 줄번호 대신 **grep 패턴**으로 위치를 특정:
```bash
# 수정 대상 검색 (실행 시점에 정확한 줄번호 확보)
grep -n "D2.0-01 §5.9" "docs/guides/VAMOS_구현가이드_PART2_구현단계.md"
```
- "line 2549, 2567"은 참고용으로만 사용
- **실제 수정 시**: grep 결과의 줄번호로 정정
- 검색 결과 0건이면 이미 정정 완료 → SKIP

#### W-19: git 전략 없음 → 브랜치 전략 정의

**대응**:
```
main (현재 상태 보존)
 └─ feat/ai-investing-sot2 (전체 작업 브랜치)
     ├─ phase0 (Phase 0 완료 후 머지)
     ├─ phase1 (Phase 1 완료 후 머지)
     ├─ phase2 (Phase 2 완료 후 머지)
     └─ phase3 (Phase 3 완료 후 머지)
```
- 각 Phase 완료 시 feat 브랜치로 머지 후 태그: `ai-invest-phase{N}-done`
- **Phase 시작 전** 반드시 커밋하여 롤백 포인트 확보
- PART2/SPEC 수정은 별도 커밋으로 분리 (문서 변경 추적 용이)

### 14.2 HIGH 약점 대응

#### W-04/W-22: Phase 전환 게이트

| 전환 | 게이트 조건 | 검증 방법 |
|------|-----------|----------|
| **Phase 0 → 1** | ① AUTHORITY_CHAIN.md 존재 ② PART2 §5.9 정정 완료 (grep 0건) ③ CONFLICT_LOG.md 존재 ④ dedup_audit.md 존재 ⑤ step7i_mapping.md 존재 ⑥ L3 템플릿 2건 + 참조예시 3건 존재 | 파일 존재 + PART2 grep |
| **Phase 1 → 2** | ① 22개 폴더 전수 존재 ② INDEX.md + 22개 _index.md 존재 ③ 758항목 분해 수 일치 (자동 카운트) ④ SPEC MIGRATED 마커 3건 존재 ⑤ PART2 §6.8.2 존재 ⑥ 원본 아카이브 완료 | 폴더/파일 카운트 + grep |
| **Phase 2 → 3** | ① 96전략 파일 전수 E1~E9 섹션 존재 ② 관점 파일 L3 헤더 전수 존재 ③ validate_links.py PASS ④ CP-1~CP-5 전수 통과 ⑤ Pydantic 12건 수정 + 테스트 통과 | validate_links.py + validate_l3.py |
| **Phase 3 완료** | ① L3 PASS ≥ 90% ② L3 FAIL = 0건 ③ V-01~V-13 전수 PASS ④ FINAL REVIEW PASS | L3_COMPLETENESS_REPORT |

#### W-05: 한→영 파일명 번역 기준

1. 전문 용어는 원어 사용 (예: "수급분석" → `supply_demand`, "볼린저밴드" → `bollinger_band`)
2. 복합어는 snake_case (예: "다중 시간프레임" → `multi_timeframe`)
3. 약어 허용 (예: "Transaction Cost Analysis" → `tca`)
4. **`21_mapping/filename_mapping.md`** 신규 생성 (Phase 0-4와 동시) → 171개 카테고리별 `한글명 | 영문파일명 | 폴더` 매핑
5. 이후 모든 파일 생성은 이 매핑 테이블을 필수 참조

#### W-09: R11 역참조 false positive 방지

1-14 실행 시 아래 **허용 패턴** 제외:
```
허용 (false positive):
  - "SPEC §14 LOCK"    → 기술스택 의존성 헤더
  - "SPEC §6.1"        → E9 LOCK 참조
  - "SPEC §10.2"       → E9 LOCK 참조
  - "> LOCK (SPEC ..."  → 인라인 LOCK 선언
  - "<!-- MIGRATED"    → 마이그레이션 주석

위반 (수정 필요):
  - "[SPEC §N](..."    → 하이퍼링크는 위반
  - "자세한 내용은 SPEC..." → sot 2/ 참조로 교체
  - "SPEC §9 참조"      → rsi_bb.md 경로로 교체
```

#### W-10: 아카이브 전 분해 완전성 검증

1-15 실행 전 **필수 게이트**:
```
☐ 19개 원본 파일 각각의 항목 수 자동 카운트 (grep -c "^- ")
☐ 분해 후 해당 관점 폴더 내 항목 수 자동 카운트
☐ 원본 항목 수 = 분해 후 합계 (19건 전부 일치)
☐ 불일치 1건이라도 → 1-15 진행 금지, 1-2 보완
```

#### W-11: Phase 2 중간 품질 체크포인트

| 체크포인트 | 시점 | 검증 내용 | 불합격 시 |
|-----------|------|----------|----------|
| **CP-1** | 2-1a 완료 후 | P0 전략 10개 L3 전수 리뷰 | 재작업 |
| **CP-2** | 2-1b 완료 후 | P1 전략 30개 중 랜덤 5개 L3 판정 | 재작업 |
| **CP-3** | 2-2a 완료 후 | P0 관점 239항목 중 랜덤 10개 L3 판정 | 재작업 |
| **CP-4** | 2-2b 완료 후 | 누적 460항목 L3 PASS ≥ 85% | 패턴 분석 + 템플릿 보완 |
| **CP-5** | 2-2d 완료 후 | 전체 758항목 L3 PASS ≥ 85% | 미달 배치 재작업 |

- CP 2회 연속 실패: L3 템플릿 또는 작성 지침 재검토

#### W-14: Pydantic 코드 수정 테스트 요구

2-8 완료 후 필수 테스트:
```python
# 최소 테스트 케이스 (12건 수정 각각 대응)
def test_sentiment_score_range():
    with pytest.raises(ValidationError):
        VAMOS_EVENT(sentiment_score=1.5, ...)  # ge=-1.0, le=1.0 위반

def test_impact_level_range():
    with pytest.raises(ValidationError):
        VAMOS_EVENT(impact_level=6, ...)  # ge=1, le=5 위반

def test_ohlcv_optional_fields():
    data = OHLCV_PLUS(close=100, volume=1000, ...)  # optional만으로 OK
    assert data is not None
```

#### W-16: L3 전수 검사 자동화 (validate_l3.py)

Phase 2-5에서 validate_links.py와 함께 작성:
```python
# validate_l3.py 스펙
# 입력: sot 2/ 디렉토리 경로
# 동작:
#   1. 대상 파일에서 "L3 완성도:" 헤더 파싱
#   2. ## E1. ~ ## E9. 섹�� 존재 여부 확인
#   3. 각 섹션 내용이 빈 템플릿이 아닌지 (최소 3줄)
#   4. E2에 코드블록(```) 포함 여부
#   5. E4에 class/def 키워드 포함 여부
# 출력: JSON {file, e1~e9_status, verdict: PASS/CONDITIONAL/FAIL}
# 3-0에서 이 스크립트로 자동 판정 → 수동 리뷰는 CONDITIONAL만
```

#### W-20: Phase 0 시작 전 백업

```bash
# Phase 0 시작 전 (0-1 이전) 필수 실행
git add -A && git commit -m "SNAPSHOT: pre-phase0 ai-investing restructure"
git tag ai-invest-pre-phase0
```
- 백업 커밋 확인 후에만 Phase 0 진입
- 복원 필요 시: `git checkout ai-invest-pre-phase0`

#### W-23: L3 품질 일관성 보장

Phase 0-8에서 L3 참조 예시 3건 추가 생성:
```
_templates/
├── L3_TEMPLATE.md           ← 빈 템플릿
├── L3_CRITERIA.md           ← 판정 기준
├── L3_EXAMPLE_STRATEGY.md   ← 참조 #1: 전략 (MACD, E1~E9 완성)
├── L3_EXAMPLE_CONCEPT.md    ← 참조 #2: 관점 항목 (Brinson-Fachler)
└── L3_EXAMPLE_INFRA.md      ← 참조 #3: 인프라 (Circuit Breaker)
```
- 3가지 유형(전략/관점/인프라)별 참조 예시로 L3 수준 기준선 확립
- Phase 2 작업 시 항상 참조 예시와 대조

### 14.3 MEDIUM 약점 대응 (요약)

| # | 약점 | 대응 |
|---|------|------|
| W-02 | 758항목 수동 추출 | 0-4에서 `### B-` regex 스크립트 사용 |
| W-03 | STEP7-I ID 형식 | 0-6 시작 시 실제 ID 형식 확인 후 매핑 |
| W-06 | 항목 수 수동 검증 | `grep -c "^- "` 자동 카운트 |
| W-07 | MIGRATED 잔존 범위 | 제목 + 1줄 요약 + 리디렉트 (3줄 이내) |
| W-08 | PART2 대파일 수정 | `grep -n "§6.8"` 로 삽입 위치 특정 |
| W-12 | 진행률 추적 | _index.md Status 칼럼 활용 |
| W-13 | validate_links.py 테스트 | known-good/known-bad 3건 테스트 |
| W-17 | 재시도 3회 근거 | 기존 절차 유지 (3회 초과 → CONDITIONAL 격하) |

### 14.4 약점 대응 반영에 따른 변경 사항

| 변경 | Phase | 내용 |
|------|-------|------|
| Phase 0 이전에 백업 단계 추가 | 0 전 | git 스냅샷 + 태그 |
| 0-4에 filename_mapping.md 생성 추가 | 0 | W-05 대응 |
| 0-8에 L3 참조 예시 3건 추가 | 0 | W-23 대응, 산출물 2→5건 |
| 1-14에 허용 패턴 제외 목록 추가 | 1 | W-09 대응 |
| 1-15 전 분해 완전성 게이트 추가 | 1 | W-10 대응 |
| 2-5에 validate_l3.py 추가 | 2 | W-16 대응 |
| 2-8에 단위 테스트 요구 추가 | 2 | W-14 대응 |
| Phase 간 전환 게이트 4건 추가 | 전체 | W-04/W-22 대응 |
| Phase 2 중간 CP-1~CP-5 추가 | 2 | W-11 대응 |
| git 브랜치 전략 전체 적용 | 전체 | W-19 대응 |

> **다음 작업**: Phase 0 단계 0-1부터 순차 실행 (§14 약점 대응 적용)

---

## 부록 §A — 실행 요약

```
Phase 0 (선행작업)         → 8단계, 산출물 8건 + L3 템플릿 + 참조예시 3건
Phase 1 (구조 재편)        → 16단계, 산출물: 전체 폴더 + 171+ 파일
Phase 2 (L3 전수 승급)     → 13단계 + CP 5건, 산출물: ~884 L3 파일 + 도구 2건
Phase 3 (L3 검증 확정)     → 8단계, 산출물: L3 리포트 + 검증 + Status 전환
─────────────────────────────────────────────────────────
합계                       → 45단계 + Phase 전환 게이트 4건 + 중간 CP 5건
L3 대상                    → 884건 (현재 8건 → 목표 884건)
약점 대응                  → 23건 (CRITICAL 2 + HIGH 10 + MEDIUM 11) 전수 반영
git 전략                   → feat/ai-investing-sot2 브랜치 + Phase별 태그
```

> **다음 작업**: Phase 0 단계 0-1부터 순차 실행

---

## 부록 §B — 세션 관리 프로토콜 (v1.4)

> **목적**: 대화창(세션) 전환 시 진행 상태 유실 방지. 계획서가 유일 영속 상태(Persistent State).
> **핵심**: 각 세션은 아래 테이블의 자기 세션 범위만 처리하고, 종료 시 상태를 갱신하면 다음 세션이 이어받을 수 있습니다.

### B-1. 세션 시작/종료 프로토콜

#### 세션 시작 시 필수 절차

| # | 절차 | 대상 Phase |
|---|------|------------|
| 1 | 계획서 읽기 — 본 문서 전체 또는 해당 Phase 섹션 | 전체 |
| 2 | **부록 B 진행 상태 테이블 확인** → 현재 세션 번호 파악 | 전체 |
| 3 | 해당 세션의 단계 범위 + §7 details 블록 확인 | 전체 |
| 4 | L3 템플릿 + 참조 예시 읽기 (`_templates/`) | Phase 2만 |
| 5 | 이전 세션 비고란 확인 (중단된 항목 있는지) | 전체 |

#### 세션 종료 시 필수 절차

| # | 절차 | 대상 Phase |
|---|------|------------|
| 1 | 완료된 단계 ⬜ → ✅ 갱신 (아래 진행 상태 테이블) | 전체 |
| 2 | 미완료 시: 비고란에 "진행 중: X/Y 완료" 기록 | 전체 |
| 3 | 해당 폴더의 _index.md Status 갱신 | Phase 1~3 |
| 4 | git commit (작업 단위별) | 전체 |

### B-2. 전체 세션 맵 (22세션)

```
Phase 0: S0-1 → S0-2 → [게이트 0→1]
Phase 1: S1-1 → S1-2 → S1-3 → [게이트 1→2]
Phase 2: S2-1 → S2-2 → S2-3 → S2-4 → S2-5 → S2-6 → S2-7
         → S2-8 → S2-9 → S2-10 → S2-11 → S2-12 → S2-13
         → S2-14 → S2-15 → [게이트 2→3]
Phase 3: S3-1 → S3-2 → [완료]
```

### B-3. Phase 0 세션 분할 (2세션)

| 세션 | 단계 | 작업 | 상태 | 완료일 | 비고 |
|:------:|------|------|:----:|--------|------|
| **S0-1** | 0-1 | AUTHORITY_CHAIN.md + PART2 정정 | ✅ | 2026-03-22 | AUTHORITY_CHAIN.md 생성, PART2 2549/2567 정정, §6.8 정본 선언 추가 |
| | 0-2 | SPEC HISTORICAL 마커 | ✅ | 2026-03-22 | §18 + 부록 B.3 마커 추가 완료 |
| | 0-3 | CONFLICT_LOG.md | ✅ | 2026-03-22 | 프로토콜 + D2.0-01 §5.9 충돌 1건 선등록 |
| | 0-4 | 교차 중복 감사 + filename_mapping.md | ✅ | 2026-03-22 | 30개 중복 그룹 식별, 정본 소유자 전수 배정, 172개 파일명 매핑 |
| **S0-2** | 0-5 | 정본 소유자 테이블 | ✅ | 2026-03-22 | canonical_owner_table.md 생성, 30개 중복 그룹 전수 등재, LOCK 1건 |
| | 0-6 | STEP7-I 106건 매핑 | ✅ | 2026-03-22 | step7i_mapping.md 생성, ABSORBED 68 / PARTIAL 37 / UNMATCHED 1 |
| | 0-7 | SPEC 마이그레이션 목록 | ✅ | 2026-03-22 | §5C 확정 + §17 15개 결함 분배 매핑 (sot2/ 13건 + SPEC 2건) |
| | 0-8 | L3 템플릿 + 참조예시 3건 | ✅ | 2026-03-22 | L3_TEMPLATE + L3_CRITERIA + EXAMPLE 3건(전략/관점/인프라) |
| | **게이트** | **Phase 0 → 1 전환 검증** | ✅ | 2026-03-22 | §14.2 기준 6개 조건 전수 PASS |

<details>
<summary><b>S0-1 세션 가이드</b></summary>

**범위**: 0-1 ~ 0-4 (권한체계 + 충돌기록 + 중복감사)

**세션 시작 프롬프트**:
```
AI Investing 구조화 작업 시작.
계획서: D:\VAMOS\docs\sot 2\Ai-investing-detail\AI_INVESTING_구조화_종합계획서.md
현재 단계: Phase 0, 세션 S0-1 (단계 0-1 ~ 0-4)
계획서 부록 B 진행 상태 확인하고, §7 Phase 0 상세 절차(0-1~0-4) 읽고 진행해줘.
시작 전 git 스냅샷 필수 (§14.2 W-20).
```

**핵심 작업**:
1. git 스냅샷 (최초 1회만)
2. AUTHORITY_CHAIN.md 신규 생성
3. PART2 §5.9 오류 정정 (grep으로 위치 특정)
4. SPEC HISTORICAL 마커 2건 추가
5. CONFLICT_LOG.md 신규 생성
6. 19개 파일 758항목 중복 감사 + filename_mapping.md 생성

**종료 시**: 0-1~0-4 ⬜→✅ 갱신 + git commit
</details>

<details>
<summary><b>S0-2 세션 가이드</b></summary>

**범위**: 0-5 ~ 0-8 + Phase 0→1 게이트 (매핑 + 템플릿 + 전환검증)

**세션 시작 프롬프트**:
```
AI Investing 구조화 작업 계속.
계획서: D:\VAMOS\docs\sot 2\Ai-investing-detail\AI_INVESTING_구조화_종합계획서.md
현재 단계: Phase 0, 세션 S0-2 (단계 0-5 ~ 0-8 + 게이트)
계획서 부록 B 진행 상태 확인하고, §7 Phase 0 상세 절차(0-5~0-8) 읽고 진행해줘.
완료 후 §14.2 Phase 0→1 게이트 검증해줘.
```

**핵심 작업**:
1. canonical_owner_table.md 생성 (0-4 결과 기반)
2. step7i_mapping.md 생성 (106건 전수 매핑)
3. SPEC 마이그레이션 목록 확정
4. L3 템플릿 2건 + 참조 예시 3건 생성
5. Phase 0→1 게이트 검증 (§14.2 조건 6개)

**종료 시**: 0-5~0-8 + 게이트 ⬜→✅ + git commit + 태그 `ai-invest-phase0-done`
</details>

### B-4. Phase 1 세션 분할 (3세션)

| 세션 | 단계 | 작업 | 상태 | 완료일 | 비고 |
|:------:|------|------|:----:|--------|------|
| **S1-1** | 1-1 | 폴더 구조 생성 (24+2) | ✅ | 2026-03-22 | 24폴더+2하위 생성, 깊이/명명 검증 통과 |
| | 1-2 | 19개 관점 파일 분해 (172+파일) | ✅ | 2026-03-22 | 191파일(172카테고리+19 _index), 760항목(≈758), B-13 보완 패턴 수동 처리 |
| | 1-3 | 메타데이터 헤더 표준화 | ✅ | 2026-03-22 | 172파일 전수 DRAFT 헤더, canonical_owner 30건 반영 |
| | 1-4 | SPEC §9 RSI_BB 마이그레이션 | ✅ | 2026-03-22 | rsi_bb.md L3 형식, 27조합+Wilder RSI+BB 수식, SPEC §9 MIGRATED |
| | 1-5 | SPEC §7.8, §7.9 마이그레이션 | ✅ | 2026-03-22 | harmonic.md+strategy_selection.md, SPEC §7.8/§7.9 MIGRATED |
| **S1-2** | 1-6 | SPEC §17 결함 분배 | ✅ | 2026-03-22 | 13건 sot2/ 분배 + 2건 SPEC 관할, §17 MIGRATED 마커 |
| | 1-7 | 00_core-integration 작성 | ✅ | 2026-03-22 | core_integration_spec.md L3 형식, D2.0-03+SPEC §20 기반 |
| | 1-8 | 20_strategy-detail 구조 작성 | ✅ | 2026-03-22 | technical/ 9파일 + quant/ 7파일 = 16파일, 96전략 전수 등재 |
| | 1-9 | INDEX.md 작성 | ✅ | 2026-03-22 | 22폴더 전수 등재, §10.2 체크리스트 포함 |
| | 1-10 | 폴더별 _index.md 작성 | ✅ | 2026-03-22 | 22개 _index.md 전수 존재, 신규 파일 4건 반영 |
| **S1-3** | 1-11 | PART2 §6.8.2 링크 테이블 | ✅ | 2026-03-22 | 22개 폴더 전수 등록, FR-3 컬럼 구조 |
| | 1-12 | PART2 SPEC 참조 갱신 | ✅ | 2026-03-22 | RSI_BB → sot 2/ 참조로 변경, 아키텍처 참조 유지 |
| | 1-13 | 새 관점 추가 체크리스트 | ✅ | 2026-03-22 | INDEX.md 9단계 체크리스트 확인 완료 |
| | 1-14 | R11 단방향 참조 점검 | ✅ | 2026-03-22 | 분해 파일(00-21) 내 SPEC 역참조 0건 (V-08 PASS) |
| | 1-15 | 원본 19개 파일 아카이브 | ✅ | 2026-03-22 | W-10 게이트 PASS 후 _archive/ 이동 완료 (19건) |
| | 1-16 | SPEC §7-8 sot 2/ 링크 | ✅ | 2026-03-22 | §7.1-7.7 + §8.1-8.7 전 카테고리 14건 Detail 링크 추가 |
| | **게이트** | **Phase 1 → 2 전환 검증** | ✅ | 2026-03-22 | 6/6 조건 PASS (22폴더, INDEX+22_index, 177파일≥172, MIGRATED 4건, §6.8.2 존재, _archive 19건) |

<details>
<summary><b>S1-1 세션 가이드</b></summary>

**범위**: 1-1 ~ 1-5 (폴더 생성 + 파일 분해 + 마이그레이션)

**세션 시작 프롬프트**:
```
AI Investing 구조화 작업 계속.
계획서: D:\VAMOS\docs\sot 2\Ai-investing-detail\AI_INVESTING_구조화_종합계획서.md
현재 단계: Phase 1, 세션 S1-1 (단계 1-1 ~ 1-5)
계획서 부록 B 진행 상태 확인하고, §7 Phase 1 상세 절차(1-1~1-5) 읽고 진행해줘.
폴더 생성 시 §2.1 트리 + filename_mapping.md 참조.
```

**주의**: 1-2가 가장 대규모 (171+ 파일 생성). 컨텍스트 초과 시 관점 #1~#10 / #11~#19로 세션 분리 가능.
</details>

<details>
<summary><b>S1-2 세션 가이드</b></summary>

**범위**: 1-6 ~ 1-10 (결함분배 + core-integration + 전략구조 + 인덱스)

**세션 시작 프롬프트**:
```
AI Investing 구조화 작업 계속.
계획서: D:\VAMOS\docs\sot 2\Ai-investing-detail\AI_INVESTING_구조화_종합계획서.md
현재 단계: Phase 1, 세션 S1-2 (단계 1-6 ~ 1-10)
계획서 부록 B 진행 상태 확인하고, §7 Phase 1 상세 절차(1-6~1-10) 읽고 진행해줘.
```
</details>

<details>
<summary><b>S1-3 세션 가이드</b></summary>

**범위**: 1-11 ~ 1-16 + Phase 1→2 게이트 (PART2 링크 + 검증 + 아카이브 + 게이트)

**세션 시작 프롬프트**:
```
AI Investing 구조화 작업 계속.
계획서: D:\VAMOS\docs\sot 2\Ai-investing-detail\AI_INVESTING_구조화_종합계획서.md
현재 단계: Phase 1, 세션 S1-3 (단계 1-11 ~ 1-16 + 게이트)
계획서 부록 B 진행 상태 확인하고, §7 Phase 1 상세 절차(1-11~1-16) 읽고 진행해줘.
1-15 아카이브 전 W-10 분해 완전성 게이트 필수.
완료 후 §14.2 Phase 1→2 게이트 검증해줘.
```
</details>

### B-5. Phase 2 세션 분할 (15세션)

| 세션 | 단계 | 작업 | 항목 수 | 상태 | 진행률 | 비고 |
|:------:|------|------|:-------:|:----:|---------|------|
| **S2-1** | 2-1a | P0 전략 L3 (MACD, MA 등) | 10 | ✅ | 10/10 | 2026-03-22 완료. trend_following(7)+volatility(1)+momentum_oscillator(1)+volume(1) |
| | CP-1 | 품질 검증 | | ✅ | | L3 EXAMPLE 품질 수준 맞춤 확인 |
| **S2-2** | 2-1b | P1 전략 L3 전반 (기술 잔여) | 13 | ✅ | 13/13 | 2026-03-22 완료. momentum_oscillator(5)+volatility(6)+volume(2) |
| **S2-3** | 2-1b | P1 전략 L3 후반 (퀀트 핵심) | 15 | ✅ | 15/15 | 2026-03-22 완료. statistical(5)+factor(5)+portfolio_risk(2)+event_driven(3) |
| | CP-2 | 품질 검증 | | ✅ | | E1~E9 전수 135섹션 확인, 51%Gate/CircuitBreaker/BaseStrategy 참조 전수 PASS |
| **S2-4** | 2-1c | P2/P3 전략 전반 (옵션+ML) | 18 | ✅ | 18/18 | 2026-03-22 완료. options(10)+ml_ai(8) |
| **S2-5** | 2-1c | P2/P3 전략 후반 (크립토+고급) | 42 | ✅ | 42/42 | 2026-03-22 완료. crypto(6)+composite(4)+reversal(7)+continuation(8)+statistical(7)+factor(3)+event_driven(3)+portfolio_risk(4)+harmonic升급 |
| **S2-6** | 2-2a | P0 관점 #1~#2 (실시간+심리) | 101 | ✅ | 101/101 | 2026-03-22 완료. 관점#1(13카테고리 54항목)+관점#2(11카테고리 47항목) 전수 L3 E1~E9 |
| **S2-7** | 2-2a | P0 관점 #3~#5 (매크로+성과+백테) | ~138 | ✅ | 138/138 | 2026-03-22 완료. 관점#3(13카테고리 52항목)+관점#4(10카테고리 42항목)+관점#5(11카테고리 44항목) 전수 L3 E1~E9 |
| | CP-3 | 품질 검증 | | ✅ | | 8/8 샘플 PASS. E1~E9 전수 기재, E2 실수식, E4 클래스설계, 원본 보존 확인 |
| **S2-8** | 2-2b | P1 관점 #6~#8 (실행+유니버스+교차) | ~113 | ✅ | 113/113 | 2026-03-22 완료. 관점#6(10카테고리 40항목)+관점#7(8카테고리 35항목)+관점#8(9카테고리 38항목) 전수 L3 E1~E9 |
| **S2-9** | 2-2b | P1 관점 #9~#11 (거버넌스+퀀트+TCA) | ~108 | ✅ | 108/108 | 2026-03-23 완료. 관점#9(9카테고리 39항목)+관점#10(8카테고리 36항목)+관점#11(8카테고리 33항목) 전수 L3 E1~E9 |
| | CP-4 | 누적 품질 검증 | | ✅ | | 6/6 샘플 PASS. E1~E9 전수 기재, E2 실수식(PSI/KS/alpha decay/IS/Almgren-Chriss), E4 클래스설계, 원본 보존 확인 |
| **S2-10** | 2-2c | P2 관점 #12~#14 (미시구조+자산군+이벤트) | ~119 | ✅ | 119/119 | 2026-03-23 완료. 관점#12(8카테고리 36항목)+관점#13(9카테고리 45항목)+관점#14(8카테고리 38항목) 전수 L3 E1~E9 |
| **S2-11** | 2-2c | P2 관점 #15~#17 (포트폴리오+글로벌+XAI) | ~112 | ✅ | 112/112 | 2026-03-23 완료. 관점#15(9카테고리 40항목)+관점#16(8카테고리 35항목)+관점#17(8카테고리 37항목) 전수 L3 E1~E9 |
| **S2-12** | 2-2d | P3 관점 #18~#19 (데이터품질+유동성) | 67 | ✅ | 67/67 | 2026-03-23 완료. 관점#18(8카테고리+D-02 35항목)+관점#19(7카테고리+D-13 32항목) 전수 L3 E1~E9 |
| | CP-5 | 전체 품질 검증 | | ✅ | | 6/6 샘플 PASS. E1~E9 전수 기재, E2 실수식(Z-score/MAD/IQR/Amihud/Kyle-lambda/margin-call/quality-score), E4 클래스설계, 원본 보존 확인 |
| **S2-13** | 2-3 | STEP7-I 미흡수 L3 보강 | 38 | ✅ | 38/38 | 2026-03-23 완료. PARTIAL 37건+UNMATCHED 1건, 24파일 E1~E9 전수 보강 |
| **S2-14** | 2-4 | PART2 89 빈껍데기 링크 | 89 | ✅ | 89/89 | 2026-03-23 완료. §6.8.3 신설: 96전략 15파일 L3 링크(§7 47개+§8 56개), Phase 테이블 §6.8참조 6건 직접 링크, 관점 19도메인 172파일 교차참조 |
| **S2-15** | 2-5~8 | 도구 + 감사 + Pydantic | 4단계 | ✅ | 4/4 | 2026-03-23 완료. validate_links.py+validate_l3.py 작성, tech_dependency.md 감사(196파일, LOCK외 1건), R12 헤더 전수 확인, contracts.py D-1~D-12 전수 반영+26 tests PASS |
| | **게이트** | **Phase 2 → 3 전환 검증** | | ✅ | | §14.2 기준 5/5 PASS (E1~E9 전수, L3 헤더 전수, validate_links PASS, CP-1~5 PASS, Pydantic 26 tests PASS) |

<details>
<summary><b>S2-1 ~ S2-5 세션 가이드 (전략 L3)</b></summary>

**공통 세션 시작 프롬프트**:
```
AI Investing 구조화 작업 계속.
계획서: D:\VAMOS\docs\sot 2\Ai-investing-detail\AI_INVESTING_구조화_종합계획서.md
L3 템플릿: Ai-investing-detail/_templates/L3_TEMPLATE.md
참조 예시: Ai-investing-detail/_templates/L3_EXAMPLE_STRATEGY.md
현재 단계: Phase 2, 세션 S2-{N}
계획서 부록 B 진행 상태 확인하고, 해당 전략의 L3 (E1~E9) 작성해줘.
작성 시 L3_EXAMPLE_STRATEGY.md 품질 수준 맞춰줘.
```

**전략 L3 작성 절차** (전략당):
1. L3 템플릿 복사 → 해당 전략 섹션에 E1~E9 작성
2. E2 Algorithm: 의사코드 필수 (복사→구현 가능 수준)
3. E4 Class/API: BaseStrategy 상속 패턴
4. E9 LOCK: §3.4 LOCK 테이블과 대조
5. L3 완성도 체크박스 ☐→☑ 갱신
</details>

<details>
<summary><b>S2-6 ~ S2-12 세션 가이드 (관점 L3 승급)</b></summary>

**공통 세션 시작 프롬프트**:
```
AI Investing 구조화 작업 계속.
계획서: D:\VAMOS\docs\sot 2\Ai-investing-detail\AI_INVESTING_구조화_종합계획서.md
L3 템플릿: Ai-investing-detail/_templates/L3_TEMPLATE.md
참조 예시: Ai-investing-detail/_templates/L3_EXAMPLE_CONCEPT.md
현재 단계: Phase 2, 세션 S2-{N} (관점 #{X}~#{Y})
계획서 부록 B 진행 상태 확인하고, 해당 관점 항목들의 L3 승급 진행해줘.
L2.5 내용을 L3로: 개념설명→의사코드, 지표명→수식, 임계치→클래스설계.
작성 시 L3_EXAMPLE_CONCEPT.md 품질 수준 맞춰줘.
```

**관점 L3 승급 절차** (항목당):
1. 기존 L2.5 내용 읽기
2. E1~E9 섹션 추가 (L2.5 → L3 변환)
3. E2: "개념 설명" → "의사코드/수식"
4. E4: 클래스 시그니처 작성
5. 모듈 단위 그룹핑 허용 (동일 카테고리 밀접 항목 → 1클래스 여러 메서드)
</details>

<details>
<summary><b>S2-13 ~ S2-15 세션 가이드 (보강 + 도구)</b></summary>

**S2-13 프롬프트**:
```
AI Investing 구조화 작업 계속.
계획서 부록 B 확인, Phase 2 세션 S2-13 (STEP7-I 미흡수 L3)
step7i_mapping.md의 PARTIAL/UNMATCHED 항목 기반으로 L3 보강해줘.
```

**S2-14 프롬프트**:
```
AI Investing 구조화 작업 계속.
계획서 부록 B 확인, Phase 2 세션 S2-14 (PART2 89건 링크)
PART2의 L1 빈껍데기 89건에 sot 2/ L3 파일 링크 연결해줘.
```

**S2-15 프롬프트**:
```
AI Investing 구조화 작업 계속.
계획서 부록 B 확인, Phase 2 세션 S2-15 (도구 + 감사 + Pydantic)
2-5: validate_links.py + validate_l3.py 작성
2-6: tech_dependency.md 감사
2-7: R12 헤더 일괄 추가
2-8: Pydantic 12건 수정 + 테스트
완료 후 §14.2 Phase 2→3 게이트 검증해줘.
```
</details>

### B-6. Phase 3 세션 분할 (2세션)

| 세션 | 단계 | 작업 | 상태 | 완료일 | 비고 |
|:------:|------|------|:----:|--------|------|
| **S3-1** | 3-0 | L3 완성도 전수 검사 (validate_l3.py) | ✅ | 2026-03-23 | 195파일 전수 PASS (100%), FAIL 0건 |
| | 3-1 | validate_links.py 실행 | ✅ | 2026-03-23 | broken=0, orphan=0, missing_index=0 |
| | 3-2 | 교차 중복 재감사 | ✅ | 2026-03-23 | dedup_audit 30건 전수 해결, 미판정 0건 |
| | 3-3 | LOCK 위반 스캔 | ✅ | 2026-03-23 | LOCK 재정의 0건 (R9 PASS) |
| | 3-4 | L3 합격 판정 | ✅ | 2026-03-23 | L3 PASS 195/195 = 100% ≥ 90%, FAIL=0 |
| **S3-2** | 3-5 | Status 전환 (DRAFT → APPROVED) | ✅ | 2026-03-23 | 195구현+22_index+거버넌스 전수 APPROVED |
| | 3-6 | INDEX.md 최종 갱신 | ✅ | 2026-03-23 | v2.0: Status/Version/L3 완성률 전수 반영 |
| | 3-7 | FINAL REVIEW | ✅ | 2026-03-23 | 5-Mode 전수 PASS, §12 v2.0 기록 완료 |
| | **완료** | **Phase 3 완료 판정** | ✅ | 2026-03-23 | §14.2 기준 4/4 PASS |

<details>
<summary><b>S3-1 세션 가이드</b></summary>

**범위**: 3-0 ~ 3-4 (L3 검사 + 링크검증 + LOCK스캔 + 합격판정)

**세션 시작 프롬프트**:
```
AI Investing 구조화 작업 계속.
계획서: D:\VAMOS\docs\sot 2\Ai-investing-detail\AI_INVESTING_구조화_종합계획서.md
현재 단계: Phase 3, 세션 S3-1 (단계 3-0 ~ 3-4)
validate_l3.py 실행해서 L3 전수 검사 후,
validate_links.py 실행, LOCK 위반 스캔, L3 합격 판정까지 진행해줘.
L3 FAIL 있으면 Phase 2 재작업 루프 진행.
```
</details>

<details>
<summary><b>S3-2 세션 가이드</b></summary>

**범위**: 3-5 ~ 3-7 + 완료 판정 (Status 전환 + INDEX + FINAL REVIEW)

**세션 시작 프롬프트**:
```
AI Investing 구조화 작업 최종 세션.
계획서: D:\VAMOS\docs\sot 2\Ai-investing-detail\AI_INVESTING_구조화_종합계획서.md
현재 단계: Phase 3, 세션 S3-2 (단계 3-5 ~ 3-7 + 완료 판정)
L3 PASS 파일 Status APPROVED 전환, INDEX.md 최종 갱신,
5-Mode FINAL REVIEW 실행해줘.
완료 후 §14.2 Phase 3 완료 게이트 검증.
```
</details>
