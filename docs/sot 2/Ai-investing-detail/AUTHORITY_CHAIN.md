# AI INVESTING 권한 체계 선언

> **Status**: APPROVED
> **버전**: v1.0
> **작성일**: 2026-03-22
> **출처**: AI_INVESTING_구조화_종합계획서 §3.1~§3.4

---

## 1. 기존 VAMOS 권한 체인 (§3.1)

```
RULE 1.3 > PLAN 3.0 > DESIGN 2.0 LOCK > DESIGN body > Schema/TECH_STACK
```

---

## 2. AI Investing 확장 권한 체인 (§3.2)

> **⚠️ 교차 검증 결과 (v1.2)**: PART2 line 2549의 `D2.0-01 §5.9 (AI Investing 정본)` 참조는 **오류**임이 확인됨.
> 실제 D2.0-01 §5.9는 "A-Series (A-1~A-7) Multi-Brain/Infra 확장"이며 AI Investing과 무관.
> D2.0-01에서 AI Investing 관련 유일한 내용은 §7.2 DEFER 테이블 #63~67 (5건 DEFER 항목)뿐.
> **조치**: DESIGN 레벨 앵커를 D2.0-01 §5.9에서 **D2.0-03 §1 (BLUE NODE 정의/P0·P1·P2) + §3.3 (P2 도메인 라이프사이클)** + **D2.0-01 §7.2 #63~67 (DEFER 인지)**로 교체.
> Phase 0-1에서 이 오류를 PART2에도 정정 반영 완료.

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

---

## 3. 각 문서의 권한 범위 (§3.3)

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

---

## 4. LOCK 보호 선언 (§3.4)

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

## 도메인 경계

| 인접 도메인 | 본 도메인 소유 | 인접 도메인 소유 |
|------------|--------------|----------------|
| #3 Blue-Node-Architecture | 투자 전략 상세 (7-Layer, 83개 소스), 51% Gate, Circuit Breaker | P2 도메인 라이프사이클 (LOCK-BN-05), P2 승인 타임아웃 |
| #19 v12-Additions | Black-Litterman tau 정본, Factor 6종 정본, Portfolio 비중 제한 정본 | 인덱스 허브 매핑, 도메인 귀속 원칙 |
| #18 Benchmark-Evaluation | VBS-17 Investing 벤치마크 협의 (Disclaimer, Financial analysis) | VBS 프레임워크, 벤치마크 실행 인프라 |
