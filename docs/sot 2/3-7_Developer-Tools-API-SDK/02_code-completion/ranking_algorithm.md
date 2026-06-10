# 제안 랭킹 알고리즘

> **L-ID**: L-002
> **V 배정**: V1 (즉시 구현 가능)
> **Phase**: Phase 1 P1-2
> **수준**: L3 (D1~D8 전수 완성, P0 항목)
> **의존 LOCK**: LOCK-DT-04 (FIM fallback chain — 모델별 confidence 보정), LOCK-DT-07 (디바운스 150ms — 랭킹 지연 예산)
> **S번호**: S-DT-002-RANK

---

## 교차 참조 블록

| 정본 문서 | 참조 내용 |
|----------|----------|
| STEP7-L L-002 | 인라인 코드 자동완성 — 다중 제안 3~5개 후보, 컨텍스트 인식 |
| 종합계획서 §A.5 | 제안 랭킹 알고리즘 — rank_completions() 가중치 공식 |
| 종합계획서 §3.4 | LOCK-DT-04, LOCK-DT-07 |
| 종합계획서 §11.2 | FR-5 신뢰도 스코어링 공식 |
| 종합계획서 §13 | L3 전수 승급 기준 D1~D8 |
| fim_protocol.md | FIM 파이프라인 6단계에서 rank_completions() 호출 (세션간 인터페이스) |
| local_model_setup.md | 모델별 신뢰도 보정 계수 참조 (세션간 인터페이스) |

---

## D1. Input Schema

### 1.1 랭킹 입력

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Completion:
    """개별 자동완성 후보"""
    text: str                            # 생성된 코드 텍스트
    model_confidence: float              # 모델 출력 확률 (0.0 ~ 1.0)
    model_id: str                        # 생성 모델 ID
    tokens_generated: int                # 생성 토큰 수
    generation_latency_ms: float         # 생성 지연 (ms)
    score: float = 0.0                   # 랭킹 점수 (초기값 0, 알고리즘이 계산)

@dataclass
class UserHistory:
    """사용자 수락 이력"""
    accepted_completions: list[dict]     # 최근 수락된 완성 목록
    rejection_count: int                 # 최근 거부 횟수
    style_preferences: dict              # 들여쓰기, 네이밍 등 코딩 스타일
    session_accept_rate: float = 0.0     # 현재 세션 수락률

@dataclass
class Context:
    """랭킹 컨텍스트"""
    language: str                        # 프로그래밍 언어
    file_path: str                       # 현재 파일 경로
    cursor_position: int                 # 커서 위치
    surrounding_code: str                # 주변 코드 (±50행)
    project_symbols: list[str]           # 프로젝트 심볼 목록 (변수, 함수, 클래스)
    imported_modules: list[str]          # 임포트된 모듈 목록
    history: UserHistory                 # 사용자 수락 이력
    expected_type: Optional[str] = None  # 타입 추론으로 예상되는 반환 타입
    scope_variables: list[str] = field(default_factory=list)  # 현재 스코프 변수
```

---

## D2. Output Schema

### 2.1 랭킹 출력

```python
@dataclass
class RankedCompletion:
    """랭킹된 완성 후보"""
    text: str
    score: float                         # 최종 랭킹 점수 (0.0 ~ 1.0)
    rank: int                            # 순위 (1부터)
    model_id: str
    score_breakdown: dict                # 점수 분해 상세

@dataclass
class RankingResult:
    """랭킹 결과"""
    ranked_completions: list[RankedCompletion]  # 점수 내림차순 정렬
    top_completion: RankedCompletion            # 최고 점수 후보
    ranking_latency_ms: float                   # 랭킹 소요 시간
    candidates_evaluated: int                    # 평가된 후보 수
    filtering_applied: bool                      # 사전 필터링 적용 여부
```

---

## D3. Algorithm

### 3.1 메인 랭킹 함수 (§A.5 대응)

```python
def rank_completions(candidates: list[Completion], ctx: Context) -> list[Completion]:
    """
    §A.5 가중치 랭킹 알고리즘.
    5개 신호의 가중 합산으로 최종 점수 산출.

    가중치 (§A.5 정본):
      model_confidence: 0.35
      type_match:       0.25
      recency:          0.20
      length_penalty:   0.10
      frequency:        0.10

    Big-O: O(K * (S + H)) where K=후보 수, S=심볼 수, H=이력 수
    """
    for c in candidates:
        c.score = (
            0.35 * c.model_confidence +
            0.25 * compute_type_match_score(c, ctx) +
            0.20 * compute_recency_score(c, ctx.history) +
            0.10 * compute_length_penalty(c) +
            0.10 * compute_frequency_score(c, ctx.project_symbols)
        )
    return sorted(candidates, key=lambda c: c.score, reverse=True)
```

> **§A.5 정합성**: 종합계획서 부록 §A.5의 `rank_completions()` 함수와 가중치, 신호 5종, 정렬 방식 모두 1:1 대응.

### 3.2 개별 스코어링 함수

#### 3.2.1 타입 매칭 점수

```python
def compute_type_match_score(completion: Completion, ctx: Context) -> float:
    """
    생성 코드의 타입 정합성 평가.
    컨텍스트에서 추론된 expected_type과 생성 코드의 반환 타입 비교.

    Big-O: O(T) where T = len(completion.text) for AST 파싱
    """
    if not ctx.expected_type:
        return 0.5  # 타입 정보 없으면 중립

    inferred_type = infer_return_type(completion.text, ctx.language)

    if inferred_type == ctx.expected_type:
        return 1.0  # 완전 일치
    elif is_compatible_type(inferred_type, ctx.expected_type):
        return 0.7  # 호환 타입 (예: int → float)
    elif inferred_type is None:
        return 0.4  # 타입 추론 불가
    else:
        return 0.1  # 타입 불일치
```

#### 3.2.2 최근성 점수 (사용자 수락 이력)

```python
def compute_recency_score(completion: Completion, history: UserHistory) -> float:
    """
    사용자 수락 이력 기반 최근성 점수.
    최근 수락된 패턴과 유사할수록 높은 점수.

    Big-O: O(H * T) where H=이력 수, T=텍스트 유사도 계산
    """
    if not history.accepted_completions:
        return 0.5  # 이력 없으면 중립

    max_similarity = 0.0
    for accepted in history.accepted_completions[-20:]:  # 최근 20건
        similarity = compute_text_similarity(completion.text, accepted["text"])
        # 시간 감쇠: 최근일수록 높은 가중치
        time_decay = math.exp(-0.1 * accepted.get("age_minutes", 0))
        weighted_sim = similarity * time_decay
        max_similarity = max(max_similarity, weighted_sim)

    return min(max_similarity, 1.0)
```

#### 3.2.3 길이 패널티

```python
def compute_length_penalty(completion: Completion) -> float:
    """
    생성 코드 길이 페널티.
    너무 짧거나 너무 긴 완성은 페널티.
    최적 구간: 10~50 토큰.

    Big-O: O(1)
    """
    tokens = completion.tokens_generated
    if tokens < 3:
        return 0.2  # 너무 짧음
    elif tokens <= 10:
        return 0.6  # 짧음
    elif tokens <= 50:
        return 1.0  # 최적
    elif tokens <= 100:
        return 0.7  # 약간 김
    else:
        return 0.4  # 너무 김
```

#### 3.2.4 빈도 점수 (프로젝트 심볼)

```python
def compute_frequency_score(completion: Completion, project_symbols: list[str]) -> float:
    """
    생성 코드에서 프로젝트 심볼 사용 빈도 평가.
    프로젝트 내 변수/함수/클래스명을 사용할수록 높은 점수.

    Big-O: O(T * S) where T=토큰 수, S=심볼 수 (Trie 최적화 시 O(T * L))
    """
    if not project_symbols:
        return 0.5

    project_symbols_set = set(project_symbols)
    project_symbols_set = set(project_symbols)
    symbols_in_code = extract_identifiers(completion.text)
    matched = sum(1 for s in symbols_in_code if s in project_symbols_set)
    total = len(symbols_in_code) if symbols_in_code else 1

    return min(matched / total, 1.0)
```

### 3.3 사전 필터링

```python
def pre_filter_candidates(
    candidates: list[Completion],
    ctx: Context,
    min_confidence: float = 0.1
) -> list[Completion]:
    """
    랭킹 전 명백히 부적절한 후보 제거.
    Big-O: O(K) where K=후보 수
    """
    filtered = []
    for c in candidates:
        # 최소 신뢰도 미달
        if c.model_confidence < min_confidence:
            continue
        # 빈 완성
        if not c.text.strip():
            continue
        # 구문 오류 (빠른 검사)
        if has_obvious_syntax_error(c.text, ctx.language):
            continue
        filtered.append(c)
    return filtered if filtered else candidates[:1]  # 최소 1개 유지
```

### 3.4 사용자 스타일 학습 반영

```python
def adjust_for_user_style(
    ranked: list[Completion],
    style: dict
) -> list[Completion]:
    """
    사용자 코딩 스타일 선호도 반영 (STEP7-L L-002: 코딩 스타일 학습).
    들여쓰기, 네이밍 컨벤션, 중괄호 위치 등.

    Big-O: O(K) where K=후보 수
    """
    for c in ranked:
        style_bonus = 0.0
        if matches_indent_style(c.text, style.get("indent")):
            style_bonus += 0.03
        if matches_naming_convention(c.text, style.get("naming")):
            style_bonus += 0.02
        c.score = min(c.score + style_bonus, 1.0)

    return sorted(ranked, key=lambda c: c.score, reverse=True)
```

---

## D4. Error Handling

### 4.1 에러 코드 체계

| 에러 코드 | 이름 | 설명 | 복구 전략 |
|-----------|------|------|----------|
| RANK-001 | NO_CANDIDATES | 후보 목록 비어 있음 | 빈 결과 반환 (자동완성 비표시) |
| RANK-002 | TYPE_INFERENCE_FAILURE | 타입 추론 실패 | type_match 점수 0.5로 fallback |
| RANK-003 | HISTORY_CORRUPTION | 사용자 이력 손상 | 이력 초기화 + 중립 점수 사용 |
| RANK-004 | SYMBOL_INDEX_STALE | 심볼 인덱스 오래됨 | 비동기 재인덱싱 트리거 |
| RANK-005 | SCORING_OVERFLOW | 점수 계산 오버플로 | 0.0~1.0 범위로 클램핑 |

### 4.2 Phase별 복구 전략

```
Phase 0 (초기화):
  - 심볼 인덱스 로드 실패 → 빈 심볼 목록으로 진행 (frequency 0.5)

Phase 1 (스코어링):
  - 개별 신호 계산 실패 → 해당 신호 중립값(0.5) 대체
  - 전체 스코어링 실패 → model_confidence 단일 기준으로 정렬

Phase 2 (후처리):
  - 스타일 학습 오류 → 스타일 보정 건너뜀
```

### 4.3 예외 처리 정책 표

| 계층 | 예외 유형 | 처리 방식 | 에스컬레이션 조건 |
|------|----------|----------|-----------------|
| Input | 빈 후보 목록 | 즉시 빈 결과 반환 | N/A |
| Scoring | 개별 신호 오류 | 중립값 대체 | 3개 이상 신호 실패 |
| History | 이력 DB 접근 오류 | 캐시된 이력 사용 | 24시간 이상 동기화 불가 |
| Output | 정렬 실패 | 입력 순서 유지 | N/A |

### 4.4 EscalationPayload

```json
{
  "type": "RANKING_ESCALATION",
  "severity": "WARNING",
  "source": "ranking_algorithm",
  "timestamp": "2026-04-10T09:54:00Z",
  "error_code": "RANK-003",
  "context": {
    "candidates_count": 5,
    "failed_signals": ["type_match", "recency", "frequency"],
    "fallback_mode": "model_confidence_only",
    "user_impact": "랭킹 정확도 저하, 기본 신뢰도 기반 정렬"
  },
  "recommended_action": "사용자 이력 DB 무결성 확인",
  "escalation_target": "ml-ops-team"
}
```

---

## D5. Dependencies

### 5.1 외부 의존성

| 의존성 | 버전 | 용도 | 필수 여부 |
|--------|------|------|----------|
| tree-sitter | ≥ 0.20 | 타입 추론, 식별자 추출 | 권장 |
| rapidfuzz | ≥ 3.0 | 텍스트 유사도 계산 (recency) | 권장 (없으면 difflib) |
| numpy | ≥ 1.24 | 벡터 연산 (대량 후보 배치 스코어링) | 선택 |

### 5.2 내부 의존성 (세션간 인터페이스)

| 모듈 | 방향 | 인터페이스 |
|------|------|----------|
| fim_protocol.md | ← 호출됨 | `rank_completions(candidates, ctx) → list[Completion]` |
| local_model_setup.md | → 참조 | 모델별 confidence 보정 계수 |

### 5.3 의존성 그래프

```
ranking_algorithm.md
├── fim_protocol.md           (호출자)
├── local_model_setup.md      (모델 보정 계수)
├── [ext] tree-sitter ≥ 0.20  (타입 추론)
├── [ext] rapidfuzz ≥ 3.0     (유사도)
└── [내부] user_history_store  (수락 이력 DB)
```

---

## D6. Performance

### 6.1 지연 예산

| 단계 | 목표 지연 | 최대 지연 |
|------|----------|----------|
| 사전 필터링 | < 1ms | 2ms |
| 5개 신호 스코어링 (K=5 후보) | < 3ms | 5ms |
| 정렬 | < 0.1ms | 0.5ms |
| 스타일 보정 | < 1ms | 2ms |
| **전체 랭킹** | **< 5ms** | **10ms** |

> LOCK-DT-07 관련: 디바운스 150ms 이후 FIM 파이프라인 내에서 랭킹에 할당된 지연 예산은 10ms 이내.

### 6.2 Big-O 요약

| 연산 | 시간 복잡도 | 공간 복잡도 |
|------|-----------|-----------|
| 사전 필터링 | O(K) | O(K) |
| type_match | O(K * T) T=AST 파싱 | O(T) |
| recency | O(K * H * T) | O(H) |
| length_penalty | O(K) | O(1) |
| frequency | O(K * S) (Trie: O(K * L)) | O(S) |
| 정렬 | O(K log K) | O(K) |
| **전체** | **O(K * (S + H))** | **O(K + S + H)** |

---

## D7. Test Spec

### 7.1 단위 테스트

| TC-ID | 시나리오 | 입력 | 기대 결과 |
|-------|---------|------|----------|
| RANK-T01 | 기본 5신호 랭킹 | 3 후보, 풀 컨텍스트 | score 내림차순 정렬 |
| RANK-T02 | model_confidence 우세 | 1후보 conf=0.95 | 해당 후보 1위 |
| RANK-T03 | type_match 우세 | 1후보 완전 타입 일치 | type_match=1.0 반영 |
| RANK-T04 | 사용자 이력 반영 | 최근 수락 패턴 유사 | recency 점수 상승 |
| RANK-T05 | 길이 패널티 | 1토큰 완성 | length_penalty=0.2 |
| RANK-T06 | 프로젝트 심볼 | 모든 식별자가 프로젝트 심볼 | frequency=1.0 |
| RANK-T07 | 빈 후보 목록 | [] | 빈 결과 반환 |
| RANK-T08 | 사전 필터링 | 3 후보 중 2개 빈 텍스트 | 1개만 랭킹 |
| RANK-T09 | 스타일 보정 | 스타일 일치 후보 | 보너스 +0.05 |
| RANK-T10 | 점수 경계값 | score > 1.0 시도 | 1.0으로 클램핑 |
| RANK-T11 | 가중치 합 검증 | 0.35+0.25+0.20+0.10+0.10 | = 1.00 |
| RANK-T12 | 동점 처리 | 2 후보 동일 점수 | model_confidence 우선 |

### 7.2 Phase 2 테스트 케이스 (사전 정의)

| TC-ID | 시나리오 | 검증 항목 |
|-------|---------|----------|
| RANK-P2T01 | 대량 후보 (100개) 랭킹 | < 50ms |
| RANK-P2T02 | 수락률 A/B: 현재 가중치 vs 대안 | 통계적 유의성 p < 0.05 |
| RANK-P2T03 | 장기 이력 (1000건) recency | 메모리 ≤ 10MB |
| RANK-P2T04 | 다국어 프로젝트 | 혼합 언어 심볼 인식 |
| RANK-P2T05 | 가중치 자동 튜닝 | online learning 수렴 |

---

## D8. Security

### 8.1 보안 고려사항

| 위협 | 설명 | 대응 |
|------|------|------|
| 이력 데이터 조작 | 수락 이력 위변조로 랭킹 조작 | 이력 DB 무결성 해시 + 접근 제어 |
| 심볼 인덱스 오염 | 악성 파일 심볼로 frequency 조작 | .gitignore 패턴 심볼 제외 + 허용 목록 |
| 점수 노출 | 랭킹 점수/가중치 외부 유출 | 내부 API만 노출, 클라이언트에 순위만 전달 |

---

## 로깅 중첩 JSON

```json
{
  "event": "ranking_completed",
  "timestamp": "2026-04-10T09:54:00.085Z",
  "level": "DEBUG",
  "trace_id": "tr-abc123",
  "input": {
    "candidates_count": 5,
    "language": "python",
    "history_size": 42,
    "symbols_count": 128
  },
  "scoring": {
    "pre_filtered": 4,
    "scores": [
      {
        "rank": 1,
        "text_preview": "def calculate_total(items)...",
        "total_score": 0.92,
        "breakdown": {
          "model_confidence": 0.332,
          "type_match": 0.250,
          "recency": 0.180,
          "length_penalty": 0.088,
          "frequency": 0.070
        }
      }
    ],
    "style_adjustment_applied": true
  },
  "performance": {
    "filter_ms": 0.5,
    "scoring_ms": 2.8,
    "sort_ms": 0.1,
    "total_ms": 3.4
  }
}
```

---

## 통합 산출물 체크리스트

- [x] §A.5 rank_completions() 가중치 공식 정확히 반영 (0.35/0.25/0.20/0.10/0.10)
- [x] D1~D8 8차원 전수 작성 (P0 항목 L-002 기준)
- [x] 세션간 인터페이스: fim_protocol.md → rank_completions() 호출 명시
- [x] 사용자 수락 이력 반영 로직 (recency_score) 포함
- [x] 컨텍스트 유사도 (type_match + frequency) 포함
- [x] ABC 시그니처: S-DT-002-RANK

---

*Phase 1 P1-2 산출물 | L-002 Ranking Algorithm | ABC: S-DT-002-RANK*
