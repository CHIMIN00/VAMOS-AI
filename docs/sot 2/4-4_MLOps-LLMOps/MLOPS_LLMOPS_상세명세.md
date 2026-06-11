# 4-4. MLOps/LLMOps 상세명세

> **Tier**: 4 - Infrastructure
> **Part2 상태**: NOT COVERED
> **SOT 근거**: STEP7-F Part 9 (10 items)
> **Part2 위치**: 해당 없음 (Part2에 미포함, SOT에만 존재)

---

## 개요

VAMOS AI의 모델 운영/관리 인프라. STEP7-F Part 9에 10개 항목이 정의되어 있으나 Part2에 전혀 반영되지 않음. 프롬프트 버전 관리, 모델 평가 파이프라인, 드리프트 감지, Canary 배포, 피드백 루프 등 LLM 운영에 필수적인 인프라 명세.

---

## 섹션 A: 프롬프트 버전 관리

### A-1. 프롬프트 저장소 구조

```
prompts/
├── registry.json              # 전체 프롬프트 인덱스
├── system/
│   ├── core_system.yaml       # 핵심 시스템 프롬프트
│   ├── agent_planner.yaml     # 에이전트 계획 프롬프트
│   └── safety_guard.yaml      # 안전 가드레일 프롬프트
├── domain/
│   ├── education/
│   ├── wellness/
│   ├── coding/
│   └── investing/
└── templates/
    ├── TS_CORE/
    ├── TS_WEB_RESEARCH/
    └── TS_CODE/
```

### A-2. 프롬프트 스키마

```python
class PromptVersion:
    id: str                           # "prompt_core_system_v3.2.1"
    name: str                         # "core_system"
    version: str                      # semver "3.2.1"
    template: str                     # Jinja2 템플릿 본문
    variables: list[PromptVariable]   # 템플릿 변수 정의
    metadata: PromptMetadata
    hash: str                         # SHA256 of template content

class PromptMetadata:
    author: str
    created_at: datetime
    description: str
    model_compatibility: list[str]    # ["claude-4-sonnet", "gpt-4o"]
    max_tokens: int                   # 이 프롬프트의 예상 토큰 소비
    tags: list[str]
    status: Literal["draft", "staging", "production", "deprecated"]
```

### A-3. 버전 태깅 규칙

| 변경 유형 | 버전 범프 | 예시 |
|----------|----------|------|
| 문구 미세 조정 | PATCH (x.x.+1) | 오타 수정, 어조 조정 |
| 구조 변경 (변수 추가/제거) | MINOR (x.+1.0) | 새 컨텍스트 변수 추가 |
| 역할/목적 변경 | MAJOR (+1.0.0) | 시스템 프롬프트 전면 개편 |

### A-4. 롤백 메커니즘

```
현재: v3.2.1 (production)
  ↓ 문제 감지 (품질 게이트 실패 또는 수동)
롤백 명령: prompt rollback core_system --to v3.1.0
  ↓
1. v3.2.1 상태 → deprecated
2. v3.1.0 상태 → production (재활성화)
3. 활성 세션에 즉시 반영 (다음 턴부터)
4. 롤백 이벤트 로깅 + 알림
```

### A-5. Diff 및 비교

- **텍스트 diff**: 버전 간 unified diff 생성
- **변수 diff**: 추가/삭제/변경된 변수 목록
- **토큰 diff**: 예상 토큰 수 변화
- **영향 분석**: 해당 프롬프트를 사용하는 에이전트/워크플로우 목록

### A-6. A/B 테스트 인프라

```python
class ABTestConfig:
    test_id: str
    prompt_a: str                     # 프롬프트 버전 ID (제어군)
    prompt_b: str                     # 프롬프트 버전 ID (실험군)
    traffic_split: float              # 0.0~1.0, B에 할당되는 비율
    metrics: list[str]                # 측정 메트릭 ["quality_score", "latency", "user_satisfaction"]
    min_sample_size: int              # 통계적 유의성을 위한 최소 샘플
    max_duration_hours: int           # 최대 테스트 기간
    auto_promote: bool                # 승자 자동 승격 여부
    significance_level: float         # p-value 임계치 (기본 0.05)

class ABTestResult:
    test_id: str
    winner: Literal["A", "B", "inconclusive"]
    metrics_a: dict[str, MetricStats]
    metrics_b: dict[str, MetricStats]
    p_value: float
    confidence_interval: tuple[float, float]
    sample_size_a: int
    sample_size_b: int
    recommendation: str
```

---

## 섹션 B: 모델 평가 파이프라인

### B-1. 자동화 평가 스크립트

```
[트리거] → [데이터셋 로드] → [모델 추론] → [메트릭 계산] → [리포트 생성] → [품질 게이트]
   ↓            ↓                ↓              ↓               ↓              ↓
 스케줄/      골든셋           배치 API        자동 채점       HTML/JSON      Pass/Fail
 수동/PR    + 샘플링         (50% 할인)      + 인간 평가      + Slack        → 배포 차단
```

### B-2. 평가 메트릭 수집

| 카테고리 | 메트릭 | 수집 방법 | 목표치 |
|---------|--------|----------|--------|
| **정확도** | Task completion rate | 자동 (골든셋 대조) | >= 85% |
| **품질** | QoD score (0.0~1.0) | LLM-as-judge + 인간 샘플링 | >= 0.85 |
| **안전성** | Safety violation rate | 자동 (가드레일 로그) | < 0.1% |
| **지연** | p50/p95 latency | 자동 (APM) | p95 < 3s |
| **비용** | Cost per interaction | 자동 (토큰 카운트) | < $0.05 |
| **한국어** | Korean accuracy delta | 자동 (LogicKor) | >= 90% of English |

### B-3. 리포팅

- **일일 리포트**: 주요 메트릭 대시보드 자동 갱신
- **주간 리포트**: 추세 분석, 이상 탐지 요약
- **릴리스 리포트**: 전체 벤치마크 결과, 이전 버전 대비 비교
- **형식**: HTML (대시보드), JSON (프로그래매틱), Slack 요약

### B-4. 평가 스케줄

| 평가 유형 | 주기 | 트리거 |
|----------|------|--------|
| 스모크 테스트 (10개 골든셋) | 매 배포 | CI/CD |
| 핵심 벤치마크 (100개) | 매일 | cron 0 4 * * * |
| 전체 벤치마크 (1000+개) | 매주 | cron 0 2 * * 1 |
| 회귀 테스트 | PR 머지 시 | GitHub webhook |

### B-5. 품질 게이트

```python
class QualityGate:
    gates: list[GateRule] = [
        GateRule(metric="task_completion", op=">=", threshold=0.85, severity="block"),
        GateRule(metric="qod_score", op=">=", threshold=0.85, severity="block"),
        GateRule(metric="safety_violation", op="<", threshold=0.001, severity="block"),
        GateRule(metric="p95_latency_ms", op="<", threshold=3000, severity="warn"),
        GateRule(metric="cost_per_interaction", op="<", threshold=0.05, severity="warn"),
    ]

    def evaluate(self, results: EvalResults) -> GateDecision:
        # block 하나라도 실패 → FAIL
        # warn만 실패 → PASS_WITH_WARNINGS
        # 전부 통과 → PASS
```

---

## 섹션 C: 모델 드리프트 감지

### C-1. 품질 모니터링 아키텍처

```
[실시간 추론 로그]
    ↓ (샘플링 5%)
[드리프트 감지 엔진]
    ↓
[지표 계산] → [시계열 DB (Prometheus)]
    ↓
[알림 규칙 평가]
    ↓ (임계치 초과)
[알림 발송] + [자동 대응]
```

### C-2. 드리프트 지표 정의

| 지표 | 계산 방법 | 윈도우 | 임계치 |
|------|----------|--------|--------|
| **QoD 이동 평균** | 최근 1000건 이동 평균 | 24h | 기준선 대비 -0.3 |
| **응답 길이 분포** | KL divergence vs 기준 분포 | 7일 | KL > 0.1 |
| **거부율** | safety guard 거부 비율 | 24h | > 5% (기준: 1%) |
| **도구 호출 실패율** | 실패/전체 도구 호출 | 6h | > 10% |
| **사용자 재시도율** | 동일 메시지 재전송 비율 | 24h | > 15% |
| **임베딩 코사인 유사도** | 응답 임베딩 vs 기준 클러스터 중심 | 7일 | cosine < 0.85 |
| **응답 지연 (p95)** | 추론 응답 시간 p95 백분위수 | 6h | > 5s |

### C-3. 알림 트리거

| 심각도 | 조건 | 알림 채널 | 응답 시간 |
|--------|------|----------|----------|
| CRITICAL | QoD < 0.60 (24h 평균) | PagerDuty + Slack | 15분 |
| HIGH | 드리프트 지표 2개+ 동시 초과 | Slack + Email | 1시간 |
| MEDIUM | 단일 드리프트 지표 초과 | Slack | 4시간 |
| LOW | 추세 경고 (7일 하락 추세) | 주간 리포트 | 다음 리뷰 |

### C-4. 자동 대응

| 트리거 | 자동 대응 | 조건 |
|--------|----------|------|
| QoD CRITICAL | 이전 프롬프트 버전 롤백 | auto_rollback=true 설정 시 |
| 도구 실패율 급등 | 해당 도구 비활성화 + fallback 활성 | 실패율 > 30% |
| 응답 지연 급등 | 캐시 강화 + 배치 크기 축소 | p95 > 5s |
| API 제공자 장애 | 대체 모델 전환 (예: Claude → GPT) | 연속 5회 5xx |

---

## 섹션 D: Canary 배포

### D-1. 점진적 롤아웃

```
Stage 0: Shadow (0%)    → 새 버전에 트래픽 복제, 결과 비교만
Stage 1: Canary (5%)    → 5% 실 트래픽 라우팅
Stage 2: Partial (25%)  → 25% 트래픽
Stage 3: Majority (75%) → 75% 트래픽
Stage 4: Full (100%)    → 완전 전환
```

### D-2. 트래픽 분배 규칙

```python
class CanaryRouter:
    def route(self, request: Request) -> ModelVersion:
        # 1. 고정 사용자 할당 (일관성)
        user_hash = hash(request.user_id) % 100

        # 2. 현재 스테이지에 따라 라우팅
        if user_hash < self.canary_percentage:
            return self.new_version
        else:
            return self.current_version

    # 특수 규칙
    # - 내부 팀: 항상 canary (beta tester)
    # - 유료 사용자: Stage 2까지 제외 (안전 우선)
    # - 특정 도메인 (의료/금융): Stage 3까지 제외
```

### D-3. 롤백 조건

| 조건 | 판정 | 액션 |
|------|------|------|
| Canary QoD < Current QoD - 0.2 | 자동 롤백 | Stage 0으로 복귀 |
| Canary 에러율 > Current * 2 | 자동 롤백 | 즉시 |
| Canary p95 latency > Current * 1.5 | 경고 | Stage 진행 중단 |
| 사용자 불만 리포트 3건+ | 수동 검토 | Stage 동결 |

### D-4. 메트릭 기반 자동 판정

```python
class CanaryJudge:
    observation_window: timedelta = timedelta(hours=6)
    min_samples: int = 100

    def judge(self, canary_metrics, baseline_metrics) -> Decision:
        # Mann-Whitney U test for QoD scores
        stat, p_value = mannwhitneyu(canary_metrics.qod, baseline_metrics.qod)

        if p_value < 0.05 and canary_metrics.qod_mean < baseline_metrics.qod_mean:
            return Decision.ROLLBACK

        if canary_metrics.error_rate > baseline_metrics.error_rate * 2:
            return Decision.ROLLBACK

        if len(canary_metrics.samples) >= self.min_samples and p_value >= 0.05:
            return Decision.PROMOTE  # 다음 Stage로

        return Decision.WAIT  # 데이터 부족, 계속 관찰
```

---

## 섹션 E: 피드백 루프

### E-1. 사용자 피드백 수집 파이프라인

```
[사용자 인터랙션]
    ↓
[암시적 피드백]                    [명시적 피드백]
 - 재시도 (negative)               - 👍/👎 버튼
 - 대화 계속 (positive)            - 품질 점수 (1~5, 내부 QoD 변환: score/5.0 → 0.0~1.0)
 - 응답 복사 (positive)            - 텍스트 피드백
 - 빠른 이탈 (negative)            - 오류 리포트
    ↓                                  ↓
[피드백 정규화 엔진]
    ↓
[피드백 DB] → [분석 파이프라인] → [개선 신호]
```

### E-2. 피드백 스키마

```python
class FeedbackRecord:
    id: str
    session_id: str
    turn_id: str
    feedback_type: Literal["implicit", "explicit"]
    signal: Literal["positive", "negative", "neutral"]
    score: Optional[float]            # 1.0~5.0
    text: Optional[str]               # 사용자 코멘트
    context: FeedbackContext           # 해당 턴의 입력/출력 스냅샷
    timestamp: datetime
    user_segment: str                 # 사용자 세그먼트

class FeedbackContext:
    user_message: str
    assistant_response: str
    model_version: str
    prompt_version: str
    tools_used: list[str]
    latency_ms: float
```

### E-3. RLHF-lite 파이프라인

> 전체 RLHF 대신, 수집된 피드백을 활용한 경량 개선 사이클

```
1. 피드백 집계 (주간)
   - negative 피드백 클러스터링 (실패 패턴 분류)
   - 고빈도 실패 패턴 Top-10 추출

2. 프롬프트 개선
   - 실패 패턴별 few-shot 예시 생성
   - 시스템 프롬프트에 가드레일 추가
   - A/B 테스트로 개선 검증

3. 도구 최적화
   - 도구 선택 정확도 분석
   - 도구별 성공/실패 패턴 리포트
   - 도구 설명(description) 개선

4. 데이터 큐레이션
   - 높은 점수(5점) 응답 → 골든 데이터셋 추가
   - 낮은 점수(1~2점) 응답 → 개선 대상 태깅
   - 평가 데이터셋 갱신 (분기별)
```

### E-4. 모델 개선 사이클

```
┌─────────────────────────────────────────────┐
│                                             │
│  [배포] → [모니터링] → [피드백 수집]          │
│    ↑                        ↓               │
│  [검증] ← [프롬프트 개선] ← [분석]           │
│                                             │
│  주기: 2주 스프린트                           │
│  목표: 스프린트당 QoD +0.1 개선              │
│                                             │
└─────────────────────────────────────────────┘
```

### E-5. 개선 추적 메트릭

| 메트릭 | 측정 주기 | 목표 |
|--------|----------|------|
| 부정 피드백 비율 | 주간 | < 5% (분기 목표) |
| Top-10 실패 패턴 해결률 | 스프린트 | >= 70% |
| 프롬프트 A/B 테스트 승률 | 월간 | >= 60% (새 버전 승리) |
| 사용자 만족도 (NPS) | 월간 | >= 50 |
| 반복 오류 발생률 | 월간 | 전월 대비 -20% |

---

## F. RLHF-lite 상세 알고리즘

### F-1 피드백 클러스터링
```python
# 주간 피드백 집계 파이프라인
class FeedbackClusterer:
    def __init__(self):
        self.min_samples = 5          # DBSCAN 최소 샘플
        self.eps = 0.2                # 코사인 거리 임계값
        self.embedding_model = "text-embedding-3-small"

    def cluster(self, feedbacks: list[FeedbackRecord]) -> list[FeedbackCluster]:
        """
        1. 부정 피드백 필터링 (signal < 0)
        2. 피드백 텍스트 임베딩 생성
        3. DBSCAN 클러스터링 (metric=cosine, eps=0.2, min_samples=5)
        4. 클러스터별 대표 피드백 + 빈도×심각도 가중 점수 산출
        5. 점수 내림차순 정렬 → Top-10 반환
        """
        negatives = [f for f in feedbacks if f.signal_score < 0]
        embeddings = self.embed(negatives)
        clusters = DBSCAN(eps=self.eps, min_samples=self.min_samples, metric="cosine").fit(embeddings)
        return self.rank_clusters(clusters, negatives)

    def rank_clusters(self, clusters, feedbacks) -> list[FeedbackCluster]:
        # 가중 점수 = count × avg(|signal_score|) × recency_weight
        # recency_weight = exp(-days_old / 30)
        ...
```

### F-2 Few-shot 생성 파이프라인
1. **패턴 식별**: Top-10 실패 클러스터에서 대표 사용자 입력 추출
2. **이상적 응답 생성**: LLM(Claude Sonnet)으로 개선된 응답 초안 생성
3. **인간 검토**: QA 팀이 초안 검토 + 수정 (SLA: 48시간 이내)
4. **Few-shot 등록**: 승인된 예시를 프롬프트 저장소에 추가 (`prompts/{domain}/few_shots/`)
5. **A/B 검증**: 기존 프롬프트 vs 개선 프롬프트 A/B 테스트 (min_sample=500, p<0.05)

### F-3 시스템 프롬프트 게이팅 규칙 추가
```yaml
# 새 게이팅 규칙 생성 워크플로우
gating_rule_workflow:
  trigger: "Top-10 패턴 중 반복 발생 (3회+/2주)"
  steps:
    1_draft: "규칙 초안 작성 (when: X, always: Y 형식)"
    2_test: "스테이징에서 100건 테스트 — 정밀도 ≥90%, 부작용 0건"
    3_review: "프롬프트 관리자 승인 (1인)"
    4_deploy: "프로덕션 프롬프트에 규칙 추가 (MINOR 버전 범프)"
    5_monitor: "7일간 모니터링 — 관련 부정 피드백 50%+ 감소 확인"
  rollback: "부작용 감지 시 즉시 규칙 제거 (PATCH 버전 범프)"
```

---

## G. 카나리 단계 운영 명세

### G-1 단계별 체류 시간 및 승격 조건

| 단계 | 트래픽 비율 | 최소 체류 시간 | 최소 샘플 | 자동 승격 조건 | 수동 개입 |
|------|-----------|-------------|---------|-------------|---------|
| Shadow | 0% (미러링) | 24시간 | 1,000 | 에러율 < 0.5%, QoD 차이 < 0.1 | 불필요 |
| Canary | 5% | 48시간 | 500 | Mann-Whitney p ≥ 0.05 (QoD, 에러율) | 이상 시 일시정지 |
| Partial | 25% | 72시간 | 2,000 | QoD ≥ 0.85 (0.0~1.0 DEC-010 정본 스케일 — 구 1.0~5.0 척도 "3.8" 표기는 LOCK-ML-05 0.85로 통일, CONF-ML-002 RESOLVED V1A-001 Phase 4 amendment), 에러율 < 1%, 사용자 불만 < 2% | 엔지니어 확인 |
| Majority | 75% | 48시간 | 5,000 | 전 지표 안정 (변동 < 5%) | 관리자 승인 |
| Full | 100% | — | — | — | 롤백 대기 모드 (48시간) |

### G-2 단계 일시정지 규칙
- 조건: 현재 단계에서 QoD 하락 ≥ 0.15 **또는** 에러율 상승 ≥ 50%
- 행동: 해당 단계에서 추가 데이터 수집 (체류 시간 2배 연장)
- 해제: 추가 데이터에서 조건 충족 → 승격, 미충족 → 자동 롤백

### G-3 사용자 세그먼트 배제
```python
# 카나리 대상 사용자 선정
def is_canary_eligible(user: User, stage: CanaryStage) -> bool:
    if stage.traffic_pct <= 25 and user.plan in ("pro", "enterprise"):
        return False  # 유료 사용자는 Partial(25%) 이후부터 포함
    if user.opted_out_canary:
        return False  # 사용자 명시적 거부
    # 결정적 해싱: hash(user_id + deployment_id) % 100 < traffic_pct
    return deterministic_hash(user.id, stage.deployment_id) < stage.traffic_pct
```

---

## H. 드리프트 메트릭 검증 근거

### H-1 임계값 산출 방법
| 메트릭 | 임계값 | 베이스라인 | 산출 근거 |
|--------|--------|----------|----------|
| QoD 이동평균 | base - 0.3 | 롤링 30일 평균 | 표준편차 2σ ≈ 0.3 (정상 분포 가정, 95% 신뢰구간) |
| 응답 길이 KL | > 0.1 | 프로덕션 7일 분포 | KL > 0.1은 "감지 가능한 분포 변화" (정보이론 관례) |
| 거부율 | > 5% | 롤링 7일 평균 × 5 | 정상 거부율 ~1%, 5배 이상 = 이상 징후 |
| 도구 실패율 | > 10% | 롤링 7일 평균 | 10%는 사용자 경험에 직접 영향 시작점 |
| 재시도율 | > 15% | 롤링 7일 평균 | 15%는 사용자 불만족 전환점 (내부 파일럿 기준) |
| 코사인 유사도 | < 0.85 | 골든 셋 평균 | 0.85 미만 = 의미 공간 15%+ 이탈 |
| 응답 지연 | > 5s | 롤링 7일 p95 | 5s 초과 시 사용자 체감 지연 (§C-4 기존 트리거 공식화) |

### H-2 샘플 크기 요건
- **최소 N**: 메트릭당 100 관측치/윈도우 (이하 → 알림 억제 "insufficient_data")
- **신뢰 수준**: 95% (z=1.96)
- **윈도우**: QoD 24h / 응답 길이 7d / 나머지 7d (주기별 노이즈 고려)

### H-3 복합 알림 규칙
- **단일 메트릭 위반**: WARN 등급 — 대시보드 표시 + Slack #mlops-alerts
- **2개+ 메트릭 동시 위반**: CRITICAL — on-call 알림 + 자동 카나리 일시정지
- **QoD CRITICAL (24h 평균 < 0.60, LOCK-ML-07)**: EMERGENCY — 즉시 이전 프롬프트 롤백 + 긴급 대응팀 소집
