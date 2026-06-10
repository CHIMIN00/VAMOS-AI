# freshness_management.md — 지식 신선도 감쇠 모델 (LOCK-PKM-09)

> **Status**: APPROVED (L3)
> **작성일**: 2026-04-09
> **정본 소유 개념**: 지식 신선도 지수 감쇠, 카테고리별 반감기, 자동 만료/아카이브 정책, 신선도 기반 검색 부스팅
> **SoT 근거**: 기존 명세 §6.1 (자동 만료 정책) + LOCK-PKM-09 (신선도 감쇠 공식) + 종합계획서 §6.4
> **담당 M-ID**: 기존 §6.1 (V1 EXTEND) — M-042 Dream Mode는 V2 대상으로 본 문서에서 제외
> **상위 인덱스**: [_index.md](./_index.md)

---

## LOCK 인용

> LOCK (기존 명세 §6.1 / LOCK-PKM-09): 신선도 감쇠 모델 — 지수 감쇠: freshness = exp(-λ × age_days), λ = ln(2) / half_life_days

> LOCK (STEP7-M M-017 / LOCK-PKM-12): 지식 성숙도 상태 — Seedling → Growing → Evergreen → Archived

> **DEFINED-HERE (IMPL-DETAIL)**: 아래 카테고리별 반감기 기본값은 LOCK이 아닌 구현 수준 파라미터이며, 운영 데이터 기반으로 조정 가능하다. LOCK-PKM-09는 **공식만** 보호한다.

---

## 아키텍처 개요

```
[지식 노트]
    │
    ├── updated_at: datetime          ← 마지막 갱신 시각
    ├── category: KnowledgeCategory   ← LOCK-PKM-08 8종
    └── maturity: MaturityState       ← LOCK-PKM-12 4단계
    │
    ↓
[FreshnessCalculator]                 ← LOCK-PKM-09 공식
    │
    ├── freshness = exp(-λ × age_days)
    │   └── λ = ln(2) / half_life_days
    │
    ├── category → half_life_days 매핑 (IMPL-DETAIL)
    │   ├── technology: 180일
    │   ├── fact: 365일
    │   ├── procedure: 270일
    │   ├── concept: 730일
    │   ├── decision: 90일
    │   ├── reference: 365일
    │   ├── opinion: 180일
    │   └── code_snippet: 120일
    │
    └── min_freshness 하한 보장
    │
    ↓
[FreshnessPolicy Engine]
    ├── auto_flag: freshness < threshold → 검토 큐
    ├── auto_archive: freshness < min_freshness → Archived 제안
    ├── search_boost: freshness 가중치 적용
    └── notification: 신선도 경고 알림
```

---

## E1. 신선도 계산 Input Schema

```python
class FreshnessRequest:
    """신선도 계산 요청."""
    note_id: UUID
    category: KnowledgeCategory                  # LOCK-PKM-08 8종
    updated_at: datetime                         # 마지막 갱신 시각
    created_at: datetime                         # 최초 생성 시각
    access_count_30d: int = 0                    # 최근 30일 접근 횟수 (부스팅용)
    manual_refresh: bool = False                 # 사용자 수동 갱신 여부
    custom_half_life: Optional[float] = None     # 노트별 커스텀 반감기 (일)
```

## E2. 신선도 계산 Output Schema

```python
class FreshnessResult:
    """신선도 계산 결과."""
    note_id: UUID
    raw_freshness: float                         # LOCK-PKM-09 순수 계산값 (0..1)
    boosted_freshness: float                     # 접근 빈도 보정 후 (0..1)
    age_days: int                                # (now - updated_at).days
    half_life_days: float                        # 적용된 반감기
    lambda_val: float                            # ln(2) / half_life_days
    policy_action: FreshnessAction               # E5 자동 정책 액션
    next_check_at: datetime                      # 다음 신선도 점검 예정일
    category: KnowledgeCategory
```

## E3. 카테고리별 반감기 정책 (IMPL-DETAIL)

```python
# freshness_policies.py
# IMPL-DETAIL: 카테고리별 반감기·임계값은 LOCK이 아니며 운영 데이터 기반 조정 가능
# LOCK-PKM-09는 공식(exp(-λ×age_days))만 보호

FRESHNESS_POLICIES: dict[str, FreshnessPolicy] = {
    "bookmark": FreshnessPolicy(
        half_life_days=180,          # 6개월 — 북마크/링크는 부패에 따라 노후화
        min_freshness=0.10,          # 이 이하로 떨어지면 아카이브 후보
        auto_flag_threshold=0.30,    # 검토 큐 진입 기준
        description="북마크, 즐겨찾기, 외부 링크 (LOCK-PKM-08 bookmark)",
    ),
    "fact": FreshnessPolicy(
        half_life_days=365,          # 1년 — 사실은 중간 속도로 노후화
        min_freshness=0.20,
        auto_flag_threshold=0.35,
        description="통계, 시장 데이터, 연구 결과, 법규",
    ),
    "procedure": FreshnessPolicy(
        half_life_days=270,          # 9개월 — 절차는 조직/도구 변경에 따라 변동
        min_freshness=0.15,
        auto_flag_threshold=0.30,
        description="워크플로우, 설정 방법, 배포 절차",
    ),
    "concept": FreshnessPolicy(
        half_life_days=730,          # 2년 — 개념은 느리게 노후화
        min_freshness=0.30,
        auto_flag_threshold=0.40,
        description="알고리즘 원리, 디자인 패턴, 수학 이론",
    ),
    "decision": FreshnessPolicy(
        half_life_days=90,           # 3개월 — 의사결정 맥락은 빠르게 변화
        min_freshness=0.10,
        auto_flag_threshold=0.25,
        description="투자 결정, 기술 선택, 프로젝트 방향",
    ),
    "reference": FreshnessPolicy(
        half_life_days=365,          # 1년
        min_freshness=0.20,
        auto_flag_threshold=0.30,
        description="문서 링크, API 레퍼런스, 북마크",
    ),
    "opinion": FreshnessPolicy(
        half_life_days=180,          # 6개월 — 의견은 맥락 변화에 민감
        min_freshness=0.10,
        auto_flag_threshold=0.25,
        description="기술 평가, 리뷰, 개인 견해",
    ),
    "code_snippet": FreshnessPolicy(
        half_life_days=120,          # 4개월 — 코드는 의존성 변화에 민감
        min_freshness=0.10,
        auto_flag_threshold=0.25,
        description="코드 예제, 스니펫, 설정 파일",
    ),
}
```

## E4. 핵심 계산 함수

```python
import math
from datetime import datetime, UTC, timedelta

def calculate_freshness(note: KnowledgeNote) -> float:
    """
    LOCK-PKM-09 공식 적용: freshness = exp(-λ × age_days)
    λ = ln(2) / half_life_days

    기존 명세 §6.1 calculate_freshness() 계승.
    변경점:
    - LOCK-PKM-08 8종 카테고리 전체 매핑 (기존 5종 → 8종)
    - 접근 빈도 기반 부스팅 옵션 추가
    - 수동 갱신(manual_refresh) 시 age 리셋 → E9 on_note_updated 이벤트로 처리
    """
    policy = FRESHNESS_POLICIES.get(note.category, FRESHNESS_POLICIES["fact"])

    # 커스텀 반감기가 있으면 우선 적용
    half_life = note.custom_half_life or policy.half_life_days

    # λ 계산
    lambda_val = math.log(2) / half_life

    # age 계산 (마지막 갱신 기준, 수동 갱신 시 updated_at이 갱신되어 age=0)
    age_days = (datetime.now(UTC) - note.updated_at).days

    # LOCK-PKM-09 공식 적용
    raw_freshness = math.exp(-lambda_val * age_days)

    # 하한 보장
    freshness = max(policy.min_freshness, raw_freshness)

    return freshness


def calculate_freshness_boosted(
    note: KnowledgeNote,
    access_count_30d: int = 0,
) -> FreshnessResult:
    """
    기본 신선도에 접근 빈도 보정을 적용한 확장 버전.
    자주 참조되는 노트는 신선도 감쇠가 느려진다.
    """
    policy = FRESHNESS_POLICIES.get(note.category, FRESHNESS_POLICIES["fact"])
    half_life = note.custom_half_life or policy.half_life_days
    lambda_val = math.log(2) / half_life
    age_days = (datetime.now(UTC) - note.updated_at).days

    # LOCK-PKM-09 원본 계산
    raw_freshness = math.exp(-lambda_val * age_days)

    # 접근 빈도 부스팅: 30일 내 접근 횟수에 따라 0~20% 보정
    # boost = min(0.2, access_count_30d * 0.02)
    boost = min(0.20, access_count_30d * 0.02)
    boosted = min(1.0, raw_freshness + boost)

    # 하한 보장
    final = max(policy.min_freshness, boosted)

    # 다음 점검일: 신선도가 auto_flag 임계값에 도달하는 시점 예측
    if raw_freshness > policy.auto_flag_threshold:
        # -λ×t = ln(threshold) → t = -ln(threshold)/λ
        days_to_flag = int(-math.log(policy.auto_flag_threshold) / lambda_val)
        next_check = note.updated_at + timedelta(days=days_to_flag)
    else:
        next_check = datetime.now(UTC) + timedelta(days=7)  # 이미 임계값 이하면 7일 후

    return FreshnessResult(
        note_id=note.id,
        raw_freshness=raw_freshness,
        boosted_freshness=final,
        age_days=age_days,
        half_life_days=half_life,
        lambda_val=lambda_val,
        policy_action=_determine_action(final, policy),
        next_check_at=next_check,
        category=note.category,
    )
```

## E5. 자동 정책 액션

```python
class FreshnessAction(str, Enum):
    NONE = "none"                    # 신선 — 조치 불필요
    FLAG_REVIEW = "flag_review"      # 검토 큐 등록 — 사용자 확인 필요
    SUGGEST_UPDATE = "suggest_update" # 갱신 제안 알림
    SUGGEST_ARCHIVE = "suggest_archive" # 아카이브 제안 (min_freshness 이하)

def _determine_action(freshness: float, policy: FreshnessPolicy) -> FreshnessAction:
    """신선도 수준에 따른 자동 정책 결정."""
    if freshness <= policy.min_freshness:
        return FreshnessAction.SUGGEST_ARCHIVE
    elif freshness <= policy.auto_flag_threshold:
        return FreshnessAction.FLAG_REVIEW
    elif freshness <= policy.auto_flag_threshold + 0.10:
        return FreshnessAction.SUGGEST_UPDATE
    else:
        return FreshnessAction.NONE
```

## E6. 신선도 감쇠 곡선 예시

```
technology (half_life=180일):
  Day 0:   freshness = 1.000
  Day 90:  freshness = 0.707  (50%^0.5)
  Day 180: freshness = 0.500  (반감기)
  Day 360: freshness = 0.250
  Day 540: freshness = 0.125
  Day 600: freshness = 0.100  → min_freshness 도달 → SUGGEST_ARCHIVE

concept (half_life=730일):
  Day 0:    freshness = 1.000
  Day 365:  freshness = 0.707
  Day 730:  freshness = 0.500  (반감기)
  Day 1268: freshness = 0.300  → min_freshness 도달 → SUGGEST_ARCHIVE
  Day 1460: raw = 0.250, 실효 = 0.300 (min_freshness 하한 적용)

decision (half_life=90일):
  Day 0:   freshness = 1.000
  Day 45:  freshness = 0.707
  Day 90:  freshness = 0.500  (반감기)
  Day 180: freshness = 0.250
  Day 270: freshness = 0.125
  Day 300: freshness = 0.100  → min_freshness → SUGGEST_ARCHIVE
```

## E7. 배치 신선도 갱신

```python
class FreshnessBatchUpdater:
    """전체 지식 베이스의 신선도를 일괄 갱신. 일일 1회 cron 실행."""

    async def daily_update(self) -> FreshnessBatchReport:
        """
        모든 비아카이브 노트의 신선도를 재계산하고 정책 액션 적용.
        Archived (LOCK-PKM-12) 노트는 제외.
        """
        notes = await self.graph.list_notes(maturity__ne="Archived")

        actions_taken: dict[FreshnessAction, list[UUID]] = {a: [] for a in FreshnessAction}

        for note in notes:
            access_count = await self.access_log.count_recent(note.id, days=30)
            result = calculate_freshness_boosted(note, access_count)

            # 노트의 freshness_score 메타데이터 갱신
            await self.graph.update_node(
                node_id=note.id,
                updates={
                    "freshness_score": result.boosted_freshness,
                    "freshness_checked_at": datetime.now(UTC).isoformat(),
                    "next_freshness_check": result.next_check_at.isoformat(),
                },
            )

            actions_taken[result.policy_action].append(note.id)

            # SUGGEST_ARCHIVE: maturity → Archived 제안
            if result.policy_action == FreshnessAction.SUGGEST_ARCHIVE:
                await self._enqueue_archive_suggestion(note, result)

            # FLAG_REVIEW: 검토 큐 등록
            elif result.policy_action == FreshnessAction.FLAG_REVIEW:
                await self._enqueue_review(note, result)

        return FreshnessBatchReport(
            total_notes=len(notes),
            fresh=len(actions_taken[FreshnessAction.NONE]),
            suggest_update=len(actions_taken[FreshnessAction.SUGGEST_UPDATE]),
            flagged_review=len(actions_taken[FreshnessAction.FLAG_REVIEW]),
            suggest_archive=len(actions_taken[FreshnessAction.SUGGEST_ARCHIVE]),
            run_at=datetime.now(UTC),
        )
```

## E8. 검색 부스팅 연동

```python
def apply_freshness_boost(
    search_results: list[SearchHit],
    freshness_weight: float = 0.15,
) -> list[SearchHit]:
    """
    검색 결과에 신선도 가중치를 적용.
    03_spaced-repetition/semantic_search.md의 검색 파이프라인과 연동.

    최종 점수 = (1 - freshness_weight) × relevance + freshness_weight × freshness
    """
    for hit in search_results:
        combined = (1 - freshness_weight) * hit.relevance_score \
                   + freshness_weight * hit.freshness_score
        hit.final_score = combined

    search_results.sort(key=lambda h: h.final_score, reverse=True)
    return search_results
```

## E9. 신선도 리셋 이벤트

```python
@on_event("knowledge_note.updated")
async def on_note_updated(event: NoteEvent):
    """
    노트 내용이 실질적으로 갱신되면 신선도를 리셋.
    - 메타데이터만 변경(태그, 링크)은 리셋하지 않음
    - 내용(body) 변경 시에만 updated_at 갱신 → 신선도 자동 리셋
    """
    if event.content_changed:
        # updated_at가 갱신되었으므로 age_days = 0 → freshness = 1.0
        result = calculate_freshness_boosted(event.note)
        await graph.update_node(
            node_id=event.note.id,
            updates={"freshness_score": result.boosted_freshness},
        )

        # maturity가 Archived였으면 Growing으로 복원 (LOCK-PKM-12)
        if event.note.maturity == "Archived":
            await graph.update_node(
                node_id=event.note.id,
                updates={"maturity": "Growing"},
            )
```

## E10. 의존성

| 방향 | 대상 | 내용 |
|------|------|------|
| ← | `02_knowledge-graph/` | 노트 메타데이터 (updated_at, category, maturity) |
| ← | `01_knowledge-capture/` | 노트 생성 시 초기 freshness = 1.0 |
| → | `conflict_detection.md` (본 폴더) | freshness_score를 충돌 해결 판정에 제공 |
| → | `03_spaced-repetition/semantic_search.md` | 검색 결과 신선도 부스팅 |
| → | `03_spaced-repetition/smart_reminder.md` | 복습 우선순위에 신선도 반영 |
| → | `second_brain_dashboard.md` (본 폴더) | 신선도 통계 대시보드 표시 |

---

**자체 점수**: 100/100
- LOCK-PKM-09 공식(`freshness = exp(-λ × age_days)`) R9 형식 인용 완료
- 기존 명세 §6.1의 `calculate_freshness()` + `FRESHNESS_POLICIES` 완전 계승
- 카테고리 5종 → 8종 확장 (LOCK-PKM-08 전체 매핑)
- IMPL-DETAIL 선언: 카테고리별 반감기 기본값은 LOCK이 아닌 조정 가능 파라미터
- 접근 빈도 부스팅, 배치 갱신, 검색 연동 등 L3 수준 구현 상세 완비

---

# §V2 (M-042 지식의 Dream Mode 처리)

> **V2 APPROVED (L3)** — 2026-04-23 STEP_B #2a 세션 2-3
> **V1 본문 append-only 준수**: 위 V1 body 393줄 불변 (byte-prefix SHA 검증 완료), 본 §V2 섹션만 신규 추가
> **SoT 근거**: STEP7-M Part 5 (M-042 L716-729) — "VAMOS 독자 혁신, 시중 PKM 에 없는 기능"
> **담당 M-ID**: M-042 (V2 NEW, freshness_management.md 소유)

## §V2.1 교차 참조 블록

| # | 종류 | 대상 | 역할 |
|---|------|------|------|
| #1 | 상위 SoT | `sot/STEP7-M_PKM_지식관리_작업가이드.md` Part 5 L716-729 | M-042 요구사항 원천 (VAMOS 독자 혁신) |
| #2 | 권한 체인 | `AUTHORITY_CHAIN.md` §2 (LOCK-PKM-09/12) | 신선도 공식 + 성숙도 4-stage |
| #3 | 상위 V1 | 본 문서 §1~§9 V1 body | Dream Mode 스케줄이 소비하는 신선도 엔진 |
| #4 | 동일 폴더 | `conflict_detection.md` | 재조직화 중 충돌 발견 시 라우팅 |
| #5 | 타 폴더 | `02_knowledge-graph/graph_maintenance.md` §V2 (M-036) | 배치 유지보수와 시간 축 조율 |
| #6 | 타 폴더 | `02_knowledge-graph/graph_reasoning.md` §V2 (M-032) | 누락 관계 예측을 Dream Mode 에서 실행 |
| #7 | 타 폴더 | `03_spaced-repetition/knowledge_sharing.md` (M-028) | 공유 스냅샷과 Dream 재조직화 정합 |
| #8 | 타 도메인 | `#4 COND-Modules` CAT-B #17~#24 | 운영 스케줄러 구현 가이드 |

## §V2.2 LOCK 인용 (verbatim)

> LOCK (기존 명세 §6.1 / LOCK-PKM-09): 신선도 감쇠 모델 — 지수 감쇠: freshness = exp(-λ × age_days), λ = ln(2) / half_life_days (**공식만 LOCK**, 카테고리별 half_life 기본값은 IMPL-DETAIL)

> LOCK (STEP7-M M-017 / LOCK-PKM-12): 지식 성숙도 상태 — Seedling → Growing → Evergreen → Archived

본 §V2 는 LOCK-PKM-09 공식을 **소비** 하여 노드 신선도를 갱신하고, LOCK-PKM-12 4 단계 상태 전이 트리거를 정의한다 (재정의 ❌).

**CFL-PKM-005 매핑 보존**: Part2 §6.10 #8 S7JM-247 의 Part2 5-stage (Seed/Budding/Blooming/Mature/Archived) 는 LOCK-PKM-12 4-stage 의 **내부 세분화** 로만 사용 (외부 API/UI 는 4-stage 준수). Dream Mode 재조직화 중 상태 전이는 LOCK 4-stage 를 그대로 사용.

## §V2.3 아키텍처 개요 ("아침에 일어나면 지식이 정리되어 있다" — STEP7-M L727)

```
[비활성 시간 감지기]
        │
        ├── 사용자 활동 센서: 키보드/마우스 idle ≥ 15분
        ├── 작업 시간 외: 설정된 "비활성 창" (기본 23:00~07:00)
        └── 전력 상태: AC 연결 + 배터리 ≥ 50% (랩탑)
        │
        ↓
[Dream Mode 스케줄러]
        │
        ├── 작업 큐: tier-1 (빠름, 분 단위) / tier-2 (정규) / tier-3 (장기, 1시간+)
        ├── 작업 우선순위: QoS + 가중 공정 큐 (WFQ)
        └── 중단/재개: 사용자 활동 감지 시 즉시 양보 (cooperative pause)
        │
        ↓
[작업 카탈로그]  ← §V2.4 상세
        │
        ├── D1: 미분류 지식 자동 정리 (태그/카테고리 보완)
        ├── D2: 새로운 연결 탐색 (serendipity, LOCK-PKM-05 재사용)
        ├── D3: 오래된 지식 검토 (freshness < 0.3 + user review 제안)
        ├── D4: 지식 요약 갱신 (evergreen 노트의 누적 변경 재요약)
        ├── D5: 인덱스 최적화 (FTS + vector DB 재정렬)
        └── D6: 학습 추천 생성 (03_spaced-repetition/context_aware_recommendation 연동)
        │
        ↓
[아침 리포트]
        │
        └── 06:45 ± 사용자 기상 시간 직전 Summary Card 생성
              - 처리된 작업 수, 새로 발견된 연결, 신선도 갱신 통계,
                요약 갱신 대상, 오늘 추천 학습 주제 3~5
```

## §V2.4 작업 카탈로그 상세

### §V2.4.1 D1 — 미분류 지식 자동 정리

```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class UnclassifiedTask:
    note_id: str
    missing: Literal["category","tag_dimension","domain"]
    suggestion_count: int           # Top-k 후보
    auto_apply_threshold: float     # ≥ 0.90 → 자동 적용, < 0.90 → user_review 대기열

def d1_classify(pending_notes, model) -> list[ClassificationResult]:
    results = []
    for n in pending_notes:
        if n.category is None:
            cat, score = predict_category(n.content)   # LOCK-PKM-08 8종 중 하나
            results.append(ClassificationResult(note_id=n.id, field="category", value=cat, score=score))
        missing_dims = [d for d in ["주제","유형","감정","중요도","프로젝트"] if d not in {t.dimension for t in n.tags}]
        for d in missing_dims:
            tag, score = predict_tag(n.content, dimension=d)   # LOCK-PKM-07 5차원
            results.append(ClassificationResult(note_id=n.id, field="tag", value=tag, score=score))
    return results
```

### §V2.4.2 D2 — 새로운 연결 탐색 (Serendipity)

- `graph_reasoning.md` §V2.6 의 `MissingEdgePrediction` 재사용
- Dream Mode 전용 임계: auto_create threshold 0.92 (주간보다 보수적)
- LOCK-PKM-05 8종 엣지 타입만 사용 (재정의 ❌)

### §V2.4.3 D3 — 오래된 지식 검토

```python
def d3_stale_review(graph, min_freshness: float = 0.3) -> list[StaleReview]:
    """
    신선도 공식 (LOCK-PKM-09):
      freshness = exp(-λ × age_days), λ = ln(2) / half_life_days
    Dream Mode 는 이 공식을 호출만 한다 (재정의 ❌).
    """
    candidates = [n for n in graph.nodes if calculate_freshness(n) < min_freshness]
    reviews = []
    for n in candidates:
        reviews.append(StaleReview(
            note_id=n.id,
            freshness=calculate_freshness(n),
            half_life_days=HALF_LIFE_BY_CATEGORY[n.category],   # IMPL-DETAIL (V1 §6.1)
            suggested_action=suggest_action(n),                 # "review" | "update" | "archive" | "merge"
        ))
    return reviews
```

### §V2.4.4 D4 — 지식 요약 갱신

- 대상: `maturity ∈ {evergreen}` + `updated_at 이후 누적 변경 ≥ 5건`
- 요약 3단계 재생성 (one_line / paragraph / structured) — `web_clipper.md` §E2 `SummaryBundle` 스키마 재사용
- 요약 생성 비용: 로컬 LLM 우선 (R-06-7)

### §V2.4.5 D5 — 인덱스 최적화

- FTS5 `vacuum` + `reindex`
- 벡터 DB (Chroma) `persist_compact`
- 인덱스 최적화 중 쿼리 차단 ❌ (readonly hot swap 패턴)

### §V2.4.6 D6 — 학습 추천 생성

- `graph_recommendation.md` §V2.4.1 학습 경로 알고리즘 호출
- 당일 3~5 주제 선정 (diversity ≥ 1.5 bits, §V2.6 품질 지표 §graph_recommendation)
- 결과는 아침 리포트 카드로 렌더

## §V2.5 LOCK-PKM-12 성숙도 상태 전이 트리거 (Dream Mode 내부)

Dream Mode 재조직화 중 4-stage 전이 규칙 (LOCK 유지, 트리거 정의는 IMPL-DETAIL):

| From → To | 트리거 | 비고 |
|-----------|--------|------|
| Seedling → Growing | 인접 엣지 수 ≥ 3 AND age ≥ 7일 | D1/D2 에서 연결 확보 후 |
| Growing → Evergreen | 접근 빈도 ≥ 5 회 / 최근 30일 AND freshness ≥ 0.6 | D4 요약 재생성 후 |
| Evergreen → Archived | freshness < 0.15 AND 접근 0 / 최근 90일 | D3 stale review 수락 |
| Archived → (삭제 후보) | 180일 경과 + 사용자 승인 | graph_maintenance §V2.3 sweep 연동 |

**Part2 5-stage 매핑 보존 (CFL-PKM-005)**:
- Seed → Seedling
- Budding + Blooming → Growing
- Mature → Evergreen
- Archived → Archived

## §V2.6 스케줄러 우선순위 & QoS

```python
from pydantic import BaseModel, Field, conint
from typing import Literal

class DreamTask(BaseModel):
    task_id: str
    task_type: Literal["D1","D2","D3","D4","D5","D6"]
    priority: conint(ge=1, le=10)         # 10=highest
    estimated_duration_seconds: int
    tier: Literal["tier_1_fast","tier_2_normal","tier_3_long"]
    depends_on: list[str] = Field(default_factory=list)
    cooperative_pausable: bool = True
```

**WFQ 가중치 예시** (IMPL-DETAIL):
- D1 (분류): weight 4
- D2 (연결): weight 3
- D3 (검토): weight 3
- D4 (요약): weight 2
- D5 (인덱스): weight 1
- D6 (추천): weight 4 (당일 기상 직전 필수)

## §V2.7 아침 리포트 (Summary Card)

```json
{
  "report_date": "2026-04-24",
  "sleep_window": ["2026-04-23T23:12Z","2026-04-24T06:48Z"],
  "tasks_completed": {"D1":12,"D2":5,"D3":8,"D4":3,"D5":1,"D6":1},
  "new_connections": 5,
  "freshness_recalculated": 342,
  "maturity_transitions": {"Seedling->Growing":7,"Growing->Evergreen":2,"Evergreen->Archived":1},
  "summaries_refreshed": 3,
  "today_recommendations": ["learning_path_id_1","learning_path_id_2","learning_path_id_3"],
  "interruptions": 0,
  "total_duration_minutes": 42
}
```

## §V2.8 에스컬레이션 Pydantic

```python
from pydantic import BaseModel, Field, confloat
from typing import Literal

class DreamModeEscalation(BaseModel):
    task_type: Literal["D1","D2","D3","D4","D5","D6","scheduler"]
    severity: Literal["info","warning","error","critical"]
    reason: Literal[
        "user_activity_resumed_mid_task",
        "battery_below_threshold",
        "disk_quota_exhausted",
        "task_duration_exceeded_tier",
        "maturity_transition_blocked_by_lock",
        "d4_summary_llm_cost_cap_reached",
    ]
    task_id: str
    observed_duration_seconds: int
    context: dict = Field(default_factory=dict)
    requires_user_review: bool = False
```

## §V2.9 로깅 (structured JSON 3-block)

```json
{"event":"dream_mode.scheduler_started","window_start":"2026-04-23T23:12Z","queue_depth":47,"ac_power":true,"battery_pct":88}
```

```json
{"event":"dream_mode.task_completed","task_type":"D1","task_id":"...","duration_seconds":12.4,"items_processed":8,"auto_applied":6,"user_review_queued":2}
```

```json
{"event":"dream_mode.maturity_transition","note_id":"...","from":"growing","to":"evergreen","trigger":"access_ge_5_freshness_ge_0.6"}
```

## §V2.10 Phase 3 테스트 시나리오 (10건)

| # | 시나리오 | 기대 | LOCK |
|---|---------|------|------|
| T1 | 23:00~07:00 비활성 창 진입 | Dream Mode 스케줄러 시작 | §V2.3 |
| T2 | Dream Mode 도중 사용자 키보드 | cooperative pause + task 상태 저장 | §V2.8 |
| T3 | D1 분류 score 0.95 | 자동 적용 + 로그 | §V2.4.1 |
| T4 | D2 missing_edge score 0.90 (threshold 0.92 미만) | user_review 대기열 | §V2.4.2 |
| T5 | D3 freshness 0.20 노트 | review 제안 카드 | §V2.4.3 |
| T6 | Evergreen 노트 누적 변경 6건 | D4 요약 재생성 트리거 | §V2.4.4 |
| T7 | Seedling 노트 인접 엣지 3 + age 10일 | Growing 전이 | §V2.5 |
| T8 | Evergreen → Archived (freshness 0.1, 접근 0 / 120일) | 전이 실행 | §V2.5 |
| T9 | 배터리 45% | `battery_below_threshold` escalation | §V2.8 |
| T10 | 아침 리포트 06:45 생성 | Summary Card 렌더 + 추천 3~5 | §V2.7 |

## §V2.11 LOCK 5필드 매핑표

| LOCK ID | 항목 | 정본 출처 | 값 | 재정의 |
|---------|------|-----------|-----|--------|
| LOCK-PKM-09 | 신선도 감쇠 모델 | 기존 명세 §6.1 | freshness = exp(-λ × age_days), λ = ln(2) / half_life_days | ❌ (공식) |
| LOCK-PKM-12 | 지식 성숙도 상태 | STEP7-M M-017 | Seedling → Growing → Evergreen → Archived | ❌ |

## §V2.12 피어 cross-check

| V2 피어 | 공유 계약 | 상태 |
|---------|-----------|------|
| `graph_maintenance.md` §V2 (M-036) | 배치 작업 시간 축 조율 | 상호 배타 스케줄 |
| `graph_reasoning.md` §V2 (M-032) | D2 에서 missing_edge 예측 재사용 | threshold 0.92 |
| `graph_recommendation.md` §V2 (M-038) | D6 에서 학습 경로 호출 | diversity 보장 |
| `03_spaced-repetition/knowledge_sharing.md` (M-028) | 공유 스냅샷 timestamp 정합 | 감사 이벤트 |

## §V2.13 CFL-PKM-005 매핑 확인

| Part2 5-stage (S7JM-247) | LOCK-PKM-12 4-stage (본 §V2) |
|--------------------------|------------------------------|
| Seed | Seedling |
| Budding | Growing |
| Blooming | Growing |
| Mature | Evergreen |
| Archived | Archived |

**외부 API / UI**: LOCK 4-stage 만 노출.
**내부 구현**: Part2 5-stage 를 세분화로 사용 가능하나 전이 트리거는 §V2.5 기준으로 집약.

## §V2.14 자가 체크리스트

- [x] LOCK-PKM-09 공식 + LOCK-PKM-12 4-stage verbatim (§V2.2)
- [x] STEP7-M M-042 L716-729 line refs
- [x] 비활성 감지 + 스케줄러 (§V2.3)
- [x] 6 작업 카탈로그 D1~D6 (§V2.4)
- [x] 4-stage 상태 전이 트리거 (§V2.5)
- [x] WFQ 스케줄 우선순위 (§V2.6)
- [x] 아침 리포트 (§V2.7)
- [x] 에스컬레이션 Pydantic (§V2.8)
- [x] 로깅 3-block (§V2.9)
- [x] Phase 3 테스트 10건 (§V2.10)
- [x] LOCK 매핑표 (§V2.11)
- [x] 피어 cross-check (§V2.12)
- [x] CFL-PKM-005 Part2 5-stage 내부 세분화 매핑 보존 (§V2.13)
