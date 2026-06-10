# second_brain_dashboard.md — Second Brain 통합 대시보드 (M-047 V3)

> **Status**: APPROVED (L3 V3)
> **작성일**: 2026-05-31 (Phase 4 RECOVERY Stage B — genuine production write)
> **정본 소유 개념**: 개인 지식 시스템 통합 대시보드 — 활동 피드 + 그래프 통계 + 학습 진척 + 신선도 워닝 4섹션, 위젯 사용자 정의
> **SoT 근거**: STEP7-M Part 4 (M-047 V2/V3) + 종합계획서 §6.4 (M-047 V1/V2 base → V3 NEW)
> **담당 M-ID**: M-047 (V3 NEW — 통합 대시보드 비주얼; filename cross-folder placement design choice)
> **상위 인덱스**: [_index.md](./_index.md)
> **VBS-14 V3 목표**: ≥ 85점 (LOCK-PKM-11 기준 상회)

---

## LOCK 인용 (verbatim — 재정의 ❌)

> LOCK (기존 명세 §6.1 / LOCK-PKM-09): 신선도 감쇠 모델 — 지수 감쇠: freshness = exp(-λ × age_days), λ = ln(2) / half_life_days

> LOCK (STEP7-M M-017 / LOCK-PKM-12): 지식 성숙도 상태 — Seedling → Growing → Evergreen → Archived

> LOCK (STEP7-M M-011 / LOCK-PKM-07): 태그 분류 체계 — 주제/유형/감정/중요도/프로젝트 5차원

> LOCK (기존 명세 §4.1 / LOCK-PKM-04): 지식그래프 노드 타입 — KnowledgeNote, Tag, Domain, Source, Person

> LOCK (기존 명세 §4.1 / LOCK-PKM-05): 지식그래프 엣지 타입 — RELATED_TO, TAGGED_WITH, BELONGS_TO, SOURCED_FROM, CONTRADICTS, SUPERSEDES, SUPPORTS, MENTIONS

**본 V3는 위 LOCK 5종을 통계 집계·시각화로 소비만 한다 (재정의 ❌).**

---

## 아키텍처 개요

```
[Second Brain Dashboard (통합 뷰)]
    ┌─────────────────────────────────────────────┐
    │ [a] 활동 피드      │ [b] 그래프 통계          │
    │  최근 노트/수정/검토 │  노드 분포(PKM-04)        │
    │                    │  엣지 분포(PKM-05)        │
    ├────────────────────┼──────────────────────────┤
    │ [c] 학습 진척       │ [d] 신선도 워닝           │
    │  SM-2 큐 상태       │  감쇠 함수(PKM-09)        │
    │  성숙도 분포(PKM-12) │  오래된 노트 알림         │
    │  ★ 3-5 진척 통합     │                          │
    └─────────────────────────────────────────────┘
    위젯 드래그&드롭 레이아웃 + LOCK-PKM-07 5차원 태그 필터
    ↓
[데이터: PostgreSQL (집계) + Redis (캐시) + Neo4j (그래프)]
```

---

## E1. Input / Output Schema

```python
from pydantic import BaseModel, Field
from typing import Literal

MaturityState = Literal["Seedling", "Growing", "Evergreen", "Archived"]  # LOCK-PKM-12
TagDimension = Literal["주제", "유형", "감정", "중요도", "프로젝트"]        # LOCK-PKM-07

class DashboardRequest(BaseModel):
    sections: list[Literal["activity", "graph_stats", "learning", "freshness"]] = \
        ["activity", "graph_stats", "learning", "freshness"]
    tag_filter: dict[TagDimension, str] = Field(default_factory=dict)  # 5차원 필터
    time_window_days: int = 30
    layout: list[dict] = Field(default_factory=list)   # 위젯 드래그&드롭 위치

class DashboardData(BaseModel):
    activity_feed: list[dict]
    graph_stats: dict          # 노드/엣지 분포 (LOCK-PKM-04/05)
    learning_progress: dict    # SM-2 큐 + 성숙도 분포 + 3-5 통합
    freshness_warnings: list[dict]
    load_duration_ms: int
    cache_hit: bool = False
```

## E2. 섹션 (a) 활동 피드

```python
async def build_activity_feed(window_days: int) -> list[dict]:
    """최근 노트 + 수정 + 검토 이벤트 타임라인."""
    return await db.query("""
        SELECT event_type, note_id, title, ts
        FROM activity_log
        WHERE ts > now() - (:d * interval '1 day')
        ORDER BY ts DESC LIMIT 50
    """, d=window_days)
```

- 이벤트 종류: 노트 생성 / 수정 / 검토(SM-2 review) / 발행 / 링크 추가
- 그룹핑: 일자별 + 노트 타입(LOCK-PKM-10)별

## E3. 섹션 (b) 그래프 통계 (LOCK-PKM-04/05 분포)

| 통계 | 출처 LOCK | 시각화 |
|------|----------|--------|
| 노드 타입 분포 | LOCK-PKM-04 (KnowledgeNote/Tag/Domain/Source/Person) | 도넛 차트 |
| 엣지 타입 분포 | LOCK-PKM-05 (8종) | 막대 차트 |
| 고차수 노드 Top-10 | — | 허브 노드 리스트 |
| 고립 노드(orphan) 수 | — | 경고 카운터 |
| 클러스터 수 (Louvain) | — | 커뮤니티 통계 |

```python
def graph_stats() -> dict:
    return {
        "node_distribution": count_by_type(NODE_TYPES),   # LOCK-PKM-04 5종
        "edge_distribution": count_by_type(EDGE_TYPES),   # LOCK-PKM-05 8종
        "top_hubs": top_degree_nodes(10),
        "orphans": count_orphan_nodes(),
        "clusters": louvain_community_count(),
    }
```

## E4. 섹션 (c) 학습 진척 (SM-2 + LOCK-PKM-12 + ★ 3-5 통합)

```python
def learning_progress() -> dict:
    return {
        # SM-2 큐 상태 (LOCK-PKM-01~03 정본)
        "sm2_due_today": count_due_cards(),
        "sm2_overdue": count_overdue_cards(),
        "sm2_upcoming_7d": count_upcoming(7),
        # 성숙도 분포 (LOCK-PKM-12 4종 verbatim)
        "maturity_distribution": {
            "Seedling": count_maturity("Seedling"),
            "Growing": count_maturity("Growing"),
            "Evergreen": count_maturity("Evergreen"),
            "Archived": count_maturity("Archived"),
        },
        # ★ 3-5 Education 학습 진척 통합 (read-only)
        "education_progress": fetch_education_progress_readonly(),
    }
```

> **성숙도 4종은 LOCK-PKM-12 정본 그대로 소비**: Seedling → Growing → Evergreen → Archived (재정의 ❌).

## E5. 섹션 (d) 신선도 워닝 (LOCK-PKM-09 감쇠 함수)

```python
import math

def freshness_warnings(half_life_days: dict[str, float]) -> list[dict]:
    """LOCK-PKM-09 감쇠 함수 기반 오래된 노트 알림."""
    warnings = []
    for note in all_notes():
        hl = half_life_days[note.category]           # 카테고리별 half_life (IMPL-DETAIL)
        lam = math.log(2) / hl                        # λ = ln(2) / half_life_days
        freshness = math.exp(-lam * note.age_days)    # freshness = exp(-λ × age_days)
        if freshness < 0.25:
            warnings.append({"note_id": note.id, "title": note.title,
                             "freshness": round(freshness, 3), "age_days": note.age_days})
    return sorted(warnings, key=lambda w: w["freshness"])
```

> **공식만 LOCK-PKM-09**: 카테고리별 half_life 기본값은 IMPL-DETAIL (공식은 재정의 ❌).

## E6. E4 (모델/도구 비교) 대시보드 도구 매트릭스

| 기준 | Grafana | Metabase | custom React |
|------|---------|----------|--------------|
| 시계열/메트릭 | ★★★ 최고 | ★★ 양호 | ★★ 직접 구현 |
| 위젯 드래그&드롭 | ★★ 패널 | ★★ 제한 | ★★★ 완전 자유 |
| 그래프 시각화 임베드 | △ 플러그인 | △ | ★★★ D3/Cytoscape 직접 |
| 커스텀 인터랙션 | ★★ | ★ | ★★★ |
| PKM 데이터 정합 | ★★ | ★★ | ★★★ 도메인 특화 |
| **권장** | 메트릭 모니터링 | BI/SQL 탐색 | **기본값 (PKM 특화 + 그래프 임베드 + 드래그&드롭)** |

> **기본 선택 = custom React**: 위젯 드래그&드롭 자유도 + 그래프 시각화(graph_visualization.md V3) 직접 임베드 + PKM 4섹션 도메인 특화가 핵심.

## E7. 폴백 전략 (E5 폴백 — 캐시)

| 실패 지점 | 폴백 | 결과 |
|----------|------|------|
| PostgreSQL 집계 지연/장애 | Redis 캐시 데이터 표시 (`cache_hit=true`) | stale 표시 + 갱신 시각 명시 |
| Neo4j 그래프 통계 실패 | 마지막 스냅샷 통계 | 그래프 섹션 stale 배지 |
| 3-5 Education 진척 조회 실패 | 해당 위젯만 비활성 (graceful degrade) | 나머지 3섹션 정상 |
| 신선도 계산 타임아웃 | 사전 배치 계산 캐시 | 워닝 섹션 캐시 표시 |

## E8. 에스컬레이션 (Pydantic)

```python
class DashboardEscalation(BaseModel):
    severity: Literal["info", "warning", "error", "critical"]
    reason: Literal[
        "data_load_timeout",
        "cache_stale_critical",
        "education_integration_unreachable",
        "lock_maturity_state_unknown",      # LOCK-PKM-12 외 상태
        "lock_tag_dimension_unknown",       # LOCK-PKM-07 외 차원
    ]
    context: dict = Field(default_factory=dict)
    requires_user_review: bool = False
```

## E9. SLA / 성능 + 인프라

| 지표 | 목표 | 측정 |
|------|------|------|
| 대시보드 로딩 (4섹션) | **≤ 2초** | 캐시 히트 < 200ms / 미스 < 2s |
| 그래프 통계 집계 | ≤ 800ms | Neo4j + 캐시 |
| 신선도 워닝 계산 | 사전 배치 (야간) | 조회 < 100ms |
| 위젯 레이아웃 저장 | 즉시 (localStorage + DB) | — |

**인프라**:
- **집계 DB**: PostgreSQL (활동 로그 + 통계 머티리얼라이즈드 뷰)
- **캐시**: Redis (대시보드 데이터 + 신선도 사전 계산, TTL 5분)
- **그래프**: Neo4j (노드/엣지 분포 LOCK-PKM-04/05)
- **프론트**: custom React + D3.js (그래프 임베드)

## E10. 로깅 / 프라이버시

```json
{"event":"dashboard.loaded","sections":4,"load_ms":1850,"cache_hit":false,"tag_filter":{"프로젝트":"VAMOS"}}
```

```json
{"event":"dashboard.freshness_scan","total":1240,"warnings":48,"threshold":0.25}
```

```json
{"event":"dashboard.education_integration","status":"ok","mode":"read_only"}
```

- **read-only 통합**: ★ 3-5 Education 학습 진척은 **read-only** 인터페이스로만 조회 (대시보드가 Education 데이터를 변경하지 않음).
- **로컬 우선**: 대시보드 데이터는 로컬/개인 영역 — 외부 전송 없음.
- **태그 필터 프라이버시**: LOCK-PKM-07 5차원 필터는 클라이언트 측 적용 (서버 로그 최소화).

## E11. 교차 도메인 참조

| 대상 | 관계 | 계약 |
|------|------|------|
| ★ 3-5 Education | 공유 ↔ | **학습 진척 통합 인터페이스 (read-only)** — SM-2 큐 + Bloom 진척 조회. LOCK-PKM-01~03 정합 (10/10 verbatim) |
| 6-3 PARL Agent Teams | 소비 ← | Second Brain Agent 통합 (대시보드 데이터 소스 제공) |
| 3-2 Multimodal | 소비 ← | 다중 미디어 노트 썸네일 표시 |
| 02_knowledge-graph | 소비 ← | graph_visualization.md V3 (그래프 통계/임베드) |
| 5-2 외부 5 deps | 영향 없음 | 대시보드는 외부 5 deps에 영향 없음 |

### ★ 3-5 Education 학습 진척 통합 인터페이스 (read-only)

```python
class EducationProgressReadOnly(BaseModel):
    """3-5 Education 학습 진척 read-only 조회 계약."""
    bloom_distribution: dict       # 6단계 분포 (LOCK-ED-05)
    mastery_rate: float            # 숙달률
    active_courses: int
    # ⚠️ read-only: 본 대시보드는 조회만, Education 데이터 변경 ❌
```

## E12. LOCK 5필드 매핑표

| LOCK ID | 항목 | 정본 출처 | 값 | 재정의 |
|---------|------|-----------|-----|--------|
| LOCK-PKM-09 | 신선도 감쇠 모델 | 기존 명세 §6.1 | freshness = exp(-λ × age_days), λ = ln(2) / half_life_days | ❌ (공식) |
| LOCK-PKM-12 | 지식 성숙도 상태 | STEP7-M M-017 | Seedling → Growing → Evergreen → Archived | ❌ |
| LOCK-PKM-07 | 태그 분류 체계 | STEP7-M M-011 | 주제/유형/감정/중요도/프로젝트 5차원 | ❌ |
| LOCK-PKM-04 | 지식그래프 노드 타입 | 기존 명세 §4.1 | KnowledgeNote, Tag, Domain, Source, Person | ❌ |
| LOCK-PKM-05 | 지식그래프 엣지 타입 | 기존 명세 §4.1 | RELATED_TO, TAGGED_WITH, BELONGS_TO, SOURCED_FROM, CONTRADICTS, SUPERSEDES, SUPPORTS, MENTIONS | ❌ |

## E13. Phase 4 테스트 시나리오 (10건)

| # | 시나리오 | 기대 | LOCK/규칙 |
|---|---------|------|-----------|
| T1 | 4섹션 대시보드 로딩 | ≤ 2초 | §E9 |
| T2 | 캐시 미스 후 PostgreSQL 집계 | < 2s, cache_hit=false | §E9 |
| T3 | PostgreSQL 장애 | Redis 캐시 표시, cache_hit=true | §E7 |
| T4 | 노드 분포 통계 | LOCK-PKM-04 5종 도넛 | §E3 |
| T5 | 엣지 분포 통계 | LOCK-PKM-05 8종 막대 | §E3 |
| T6 | 성숙도 분포 | LOCK-PKM-12 4종 verbatim | §E4 |
| T7 | 신선도 워닝 (age > half_life) | freshness < 0.25 알림 | §E5 LOCK-PKM-09 |
| T8 | 3-5 Education 진척 조회 | read-only, 변경 0 | §E11 |
| T9 | 위젯 드래그&드롭 레이아웃 저장 | 즉시 영속 | §E1 |
| T10 | LOCK-PKM-07 5차원 태그 필터 | 주제/유형/감정/중요도/프로젝트 | §E12 |

## E14. 자가 체크리스트

- [x] 대시보드 4섹션 (활동 피드 + 그래프 통계 + 학습 진척 + 신선도 워닝) (§E2~E5)
- [x] LOCK-PKM-09 신선도 감쇠 공식 인용 + 적용 (§E5, §E12)
- [x] LOCK-PKM-12 성숙도 4종 verbatim (§E4, §E12)
- [x] LOCK-PKM-07 5차원 태그 필터링 verbatim (§E12, T10)
- [x] LOCK-PKM-04/05 노드/엣지 분포 (§E3)
- [x] 위젯 사용자 정의 (드래그&드롭) (§E1, T9)
- [x] E4 모델 비교 Grafana/Metabase/custom React (§E6)
- [x] E5 폴백: 데이터 로딩 실패 시 캐시 (§E7)
- [x] E7 SLA: 대시보드 로딩 ≤ 2초 (§E9)
- [x] E9 인프라: PostgreSQL + Redis 캐시 (§E9)
- [x] ★ 3-5 Education 학습 진척 통합 인터페이스 (read-only) (§E11)
- [x] E1~E14 9요소 이상 + L3 ≥ 80점 (VBS-14 V3 ≥ 85 목표)
