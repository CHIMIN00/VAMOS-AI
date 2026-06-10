# SM-2 교육 확장 알고리즘 — Bloom 레벨 연동 EF 보정

| 항목 | 값 |
|------|-----|
| **파일** | `02_spaced-repetition/sm2_education_extension.md` |
| **o_ids** | O-002-1, O-002-2 |
| **V단계** | V1 (로컬 MVP) |
| **Level** | L3 |
| **LOCK 참조** | LOCK-ED-04, LOCK-ED-05 |
| **PKM 참조** | LOCK-PKM-01, LOCK-PKM-02, LOCK-PKM-03 |
| **SOT 출처** | STEP7-O O-002 (간격 반복 시스템) |
| **상태** | COMPLETE |

---

## 1. 개요

SM-2 교육 확장은 PKM 도메인이 보유한 SM-2 정본 파라미터를 **참조 전용**으로 사용하되, 교육 도메인 고유의 Bloom 택소노미 연동 EF 보정을 추가한다. 두 가지 핵심 축으로 구성된다:

1. **SM-2 교육 확장 알고리즘** (O-002-1) — PKM 정본 파라미터 기반 교육 특화 래퍼
2. **Bloom 레벨 연동 EF 보정** (O-002-2) — Bloom 6단계별 EF 가중치 조정

### 공유 규약 (R-08-1)

> **R-08-1**: SM-2 교육 커스터마이징은 #6 PKM 정본 파라미터 참조 필수. 단독 변경 금지, 변경 무효.

Education 도메인의 SM-2 커스터마이징 범위는 다음에 한정된다:
- **EF 보정 가중치** (Bloom 레벨별 조정 계수)
- **Interval 조정 계수** (학습 맥락별 배율)
- **Quality-Bloom 연동 매핑** (소크라테스 교수법 quality → Bloom 레벨 역산)

기본 파라미터(MIN_EF, DEFAULT_EF, I(1), I(2), I(n≥3) 공식) 자체를 변경하는 것은 **절대 금지**이며, 변경이 필요한 경우 PKM 도메인과 공동 의사결정 후 LOCK-PKM-01~03을 먼저 갱신해야 한다.

---

## 2. O-002-1: SM-2 교육 확장 알고리즘

### 2.1 PKM 정본 파라미터 참조 (LOCK-ED-04)

> LOCK (LOCK-ED-04, #6 PKM LOCK-PKM-01~03): MIN_EF=1.3, DEFAULT_EF=2.5, I(1)=1d, I(2)=6d → PKM 참조만, 단독 변경 금지

| 파라미터 | LOCK ID | 정본 값 | 소유권 |
|---------|---------|---------|--------|
| MIN_EASINESS | LOCK-PKM-01 | **1.3** | PKM (#6) |
| DEFAULT_EASINESS | LOCK-PKM-02 | **2.5** | PKM (#6) |
| 초기 간격 I(1) | LOCK-PKM-03 | **1일** | PKM (#6) |
| 초기 간격 I(2) | LOCK-PKM-03 | **6일** | PKM (#6) |
| 반복 간격 I(n≥3) | LOCK-PKM-03 | **I(n-1) × EF** | PKM (#6) |

> LOCK (LOCK-PKM-01, STEP7-M M-027 / 기존 명세 §5.1): MIN_EASINESS = 1.3

> LOCK (LOCK-PKM-02, STEP7-M M-027 / 기존 명세 §5.1): DEFAULT_EASINESS = 2.5

> LOCK (LOCK-PKM-03, 기존 명세 §5.1): n=1: 1일, n=2: 6일, n≥3: I(n-1) × EF

### 2.2 기본 SM-2 알고리즘 (PKM 정본 그대로)

```
function sm2_base(card, quality):
    // quality ∈ {0, 1, 2, 3, 4, 5}
    // 0 = 완전 실패, 5 = 완벽한 응답

    // Step 1: EF 갱신
    new_ef = card.ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    new_ef = max(MIN_EASINESS, new_ef)    // LOCK-PKM-01: 하한 1.3

    // Step 2: 반복 횟수 갱신
    if quality < 3:
        card.repetition = 0               // 실패 시 리셋
    else:
        card.repetition += 1

    // Step 3: 간격 계산 (LOCK-PKM-03)
    if card.repetition == 1:
        interval = 1                       // I(1) = 1일
    elif card.repetition == 2:
        interval = 6                       // I(2) = 6일
    else:
        interval = round(card.last_interval * new_ef)  // I(n) = I(n-1) × EF

    // Step 4: 결과 반환
    card.ef = new_ef
    card.last_interval = interval
    card.next_review = today() + interval days
    return card
```

### 2.3 교육 확장 래퍼

Education 도메인은 `sm2_base` 결과에 대해 **후처리(post-processing)** 방식으로 Bloom 보정과 맥락 조정을 적용한다. 기본 SM-2 로직 자체는 변경하지 않는다.

```
function sm2_education_extended(card, quality, bloom_level, context):
    // Step 1: PKM 정본 SM-2 계산 (불변)
    card = sm2_base(card, quality)

    // Step 2: Bloom EF 보정 (Education 소유 확장 — §3 참조)
    bloom_adjustment = get_bloom_ef_adjustment(bloom_level, quality)
    adjusted_ef = card.ef + bloom_adjustment
    adjusted_ef = max(MIN_EASINESS, adjusted_ef)   // 하한 보장
    card.ef = adjusted_ef

    // Step 3: 맥락별 간격 조정 (review_scheduler.md 위임)
    // → review_scheduler.md의 context_interval_factor() 사용
    context_factor = get_context_interval_factor(context)
    card.last_interval = round(card.last_interval * context_factor)
    card.last_interval = max(1, card.last_interval)  // 최소 1일

    // Step 4: 다음 복습일 재계산
    card.next_review = today() + card.last_interval days

    return card
```

### 2.4 quality-Bloom 연동 매핑

소크라테스 교수법 대화 엔진(`01_adaptive-learning/adaptive_engine.md` §4.5)의 quality 평가와 Bloom 레벨을 교차하여 SM-2 입력으로 사용한다.

| quality | SM-2 기본 의미 | Bloom 1-2 (Remember/Understand) | Bloom 3-4 (Apply/Analyze) | Bloom 5-6 (Evaluate/Create) |
|---------|---------------|-------------------------------|--------------------------|---------------------------|
| 5 | 완벽한 응답 | 즉시 회상, 설명 가능 | 힌트 없이 적용·분석 완료 | 독립적 평가·창작 |
| 4 | 약간의 망설임 | 약간 지체 후 회상 | 방향 힌트(H1) 후 완료 | 부분적 평가 후 보완 |
| 3 | 심각한 망설임 | 다수 시도 후 회상 | 개념 힌트(H2) 후 완료 | 가이드 후 완료 |
| 2 | 오답 근접 | 부분 회상, 혼동 | 부분 답(H3) 후 완료 | 모방 수준 |
| 1 | 오답 | 회상 실패 | 힌트 3단계 후에도 오답 | 시도 불가 |
| 0 | 완전 실패 | 인지 자체 불가 | 풀이 공개 후에도 미이해 | 개념 미보유 |

---

## 3. O-002-2: Bloom 레벨별 EF 보정

### 3.1 보정 근거

Bloom 상위 단계(Evaluate, Create)는 인지적 부하가 높아 동일 quality에서도 기억 안정성이 다르다. EF 보정을 통해:
- **하위 Bloom** (Remember, Understand): EF를 약간 상향 → 빠르게 간격 확장 (단순 기억은 반복 효율 높음)
- **상위 Bloom** (Evaluate, Create): EF를 약간 하향 → 보수적 간격 → 더 자주 복습 (고차 사고는 망각 빠름)

### 3.2 Bloom EF 보정 테이블

> LOCK (LOCK-ED-05, STEP7-O O-001): Remember / Understand / Apply / Analyze / Evaluate / Create

> **§B.2.1 정합성 노트**: 종합계획서 부록 §B.2.1은 곱셈 방식(`EF_edu = EF × bloom_weight`, Remember=1.0 ~ Create=0.75)을 제안한다. 본 L3 구현 정본은 이를 **가산 + quality 감쇠** 방식으로 정제한다. 근거: (1) 곱셈 방식은 EF가 낮은 카드에서 MIN_EF(1.3)에 과도하게 빈번히 도달하여 보정 효과가 사라지는 문제가 있고, (2) quality 3 미만(실패 구간)에서는 SM-2 기본 리셋이 우선하므로 Bloom 보정을 무효화하는 것이 합리적이다. 최종 방향(상위 Bloom = 더 보수적 간격)은 §B.2.1과 동일하다.

| Bloom 레벨 | 단계 번호 | EF 보정값 (Δ) | §B.2.1 대응 weight | 보정 근거 |
|------------|----------|--------------|-------------------|-----------|
| Remember | 1 | **+0.10** | 1.00 | 단순 회상 — 반복 학습 효율 극대화 |
| Understand | 2 | **+0.05** | 0.95 | 이해 수준 — 약간의 반복 이점 |
| Apply | 3 | **±0.00** | 0.90 | 적용 수준 — 기준점 (보정 없음) |
| Analyze | 4 | **−0.05** | 0.85 | 분석 수준 — 약간 보수적 간격 |
| Evaluate | 5 | **−0.10** | 0.80 | 평가 수준 — 고차 사고, 잦은 복습 필요 |
| Create | 6 | **−0.15** | 0.75 | 창조 수준 — 최고 인지 부하, 가장 보수적 |

### 3.3 EF 보정 공식

```
function get_bloom_ef_adjustment(bloom_level, quality):
    // Bloom 레벨별 기본 보정값
    BLOOM_DELTA = {
        1: +0.10,   // Remember
        2: +0.05,   // Understand
        3:  0.00,   // Apply (기준점)
        4: -0.05,   // Analyze
        5: -0.10,   // Evaluate
        6: -0.15    // Create
    }

    delta = BLOOM_DELTA[bloom_level]

    // quality에 따른 감쇠: quality가 낮을수록 보정 효과 감소
    // (quality 0-2: 실패 구간 — Bloom 보정보다 리셋이 우선)
    if quality < 3:
        // 실패 시 Bloom 보정 무효화 (SM-2 기본 리셋 로직 우선)
        return 0.0

    // quality 3-5: 성공 구간 — Bloom 보정 적용
    // quality_weight: 3→0.5, 4→0.75, 5→1.0
    quality_weight = (quality - 2) / 2.0
    adjusted_delta = delta * quality_weight

    return adjusted_delta
```

### 3.4 보정 적용 예시

**시나리오**: Bloom Level 6 (Create), quality = 4, 현재 EF = 2.5

```
// 1. SM-2 기본 EF 갱신
new_ef = 2.5 + (0.1 - (5-4) * (0.08 + (5-4) * 0.02))
       = 2.5 + (0.1 - 1 * 0.10)
       = 2.5 + 0.0
       = 2.5

// 2. Bloom 보정
delta = -0.15 (Create)
quality_weight = (4 - 2) / 3.0 = 0.667
adjusted_delta = -0.15 * 0.667 = -0.10

// 3. 최종 EF
final_ef = 2.5 + (-0.10) = 2.40
// MIN_EASINESS(1.3) 이상이므로 유효

// 결과: Create 수준 카드는 EF가 더 느리게 증가 → 더 자주 복습
```

**시나리오**: Bloom Level 1 (Remember), quality = 5, 현재 EF = 2.5

```
// 1. SM-2 기본 EF 갱신
new_ef = 2.5 + (0.1 - (5-5) * (0.08 + (5-5) * 0.02))
       = 2.5 + 0.1
       = 2.6

// 2. Bloom 보정
delta = +0.10 (Remember)
quality_weight = (5 - 2) / 3.0 = 1.0
adjusted_delta = +0.10 * 1.0 = +0.10

// 3. 최종 EF
final_ef = 2.6 + 0.10 = 2.70

// 결과: Remember 수준 카드는 EF가 빠르게 증가 → 간격 빠르게 확장
```

### 3.5 EF 하한 보장

Bloom 보정 후에도 반드시 `MIN_EASINESS = 1.3` (LOCK-PKM-01)을 준수한다:

```
final_ef = max(MIN_EASINESS, base_ef + bloom_adjustment)
// MIN_EASINESS = 1.3 (LOCK-PKM-01, 변경 불가)
```

---

## 4. 데이터 스키마

### 4.1 EducationCard 확장 필드

```
interface EducationCard extends SM2Card:
    // SM2Card 기본 필드 (PKM 정본)
    ef: number              // Easiness Factor (≥ 1.3)
    repetition: number      // 연속 성공 횟수
    last_interval: number   // 마지막 간격 (일)
    next_review: date       // 다음 복습일

    // Education 확장 필드 (§B.3 EducationFlashcard 정합)
    bloom_level: BloomLevel         // LOCK-ED-05: 1~6
    difficulty_irt: number          // LOCK-ED-02: IRT θ 값
    subject_area: string            // 학습 분야 (coding, math, language 등)
    card_type: FlashcardType        // LOCK-ED-08: 기본/빈칸/이미지오클루전/코드
    hint_steps: string[]            // 소크라테스 힌트 (최대 3단계, LOCK-ED-06)
    bloom_adjusted_ef: number       // Bloom 보정 적용 후 EF (§B.3 bloom_weight_ef 대응)
    context: LearningContext        // 학습 맥락 (review_scheduler.md 연동)
    related_learning_path?: string  // 연관 학습 경로 ID
    quality_history: QualityEntry[] // 최근 quality 이력 (맥락 분석용)
```

### 4.2 QualityEntry

```
interface QualityEntry:
    timestamp: datetime
    quality: number          // 0~5
    bloom_level: BloomLevel  // 평가 시점의 Bloom 레벨
    hint_count: number       // 소크라테스 힌트 사용 횟수 (0~3)
    response_time_ms: number // 응답 소요 시간
```

---

## 5. 교차 참조

| 참조 대상 | 파일 | 관계 |
|-----------|------|------|
| PKM SM-2 정본 | `sot 2/3-3_PKM-Knowledge-Management/` LOCK-PKM-01~03 | 파라미터 정본 (참조 전용) |
| 플래시카드 자동 생성 | `flashcard_auto_generation.md` | 카드 유형별 Bloom 태깅 연동 |
| 복습 스케줄러 | `review_scheduler.md` | context_interval_factor 사용, 간격 최종 계산 |
| 적응형 엔진 | `../01_adaptive-learning/adaptive_engine.md` | quality-Bloom 매핑, 소크라테스 교수법 연동 |
| 난이도 조정 | `../01_adaptive-learning/difficulty_adjustment.md` | IRT θ 기반 난이도와 Bloom EF 보정 교차 |
| 종합계획서 부록 §B | `EDUCATION_LEARNING_구조화_종합계획서.md` | SM-2 교육 확장 상세 참조 |

---

## 6. V2/V3 확장 예정

| 버전 | 확장 내용 |
|------|-----------|
| V2 | 학습자 개인별 Bloom 보정 테이블 학습 (질의응답 이력 기반 개인화), 망각 곡선 정밀 모델링 |
| V3 | 그룹 학습 SM-2 공유 풀, A/B 테스트 기반 보정값 자동 튜닝 |
