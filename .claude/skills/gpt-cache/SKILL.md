---
name: gpt-cache
description: LLM 응답 시맨틱 캐싱. 동일/유사 질문에 이전 응답 반환으로 비용 절감 + 속도 향상. /consensus 반복 추출 시 활용.
---

# VAMOS E-46 GPT-Cache 스킬 (Semantic Caching)

> `/gpt-cache [enable|disable|stats|clear]` — LLM 응답 시맨틱 캐싱

## 기반 기술

- **GPTCache** (Zilliz): LLM 응답을 시맨틱 유사도 기반으로 캐싱
- 동일/유사한 질문에 대해 이전 응답을 캐시에서 반환

---

## 기능

1. 동일 SOT 반복 추출 시 캐시 히트 → 비용 0
2. `/consensus` 3~5회 반복 추출 시 1회만 실제 호출
3. Phase 재실행 시 변경되지 않은 SOT는 캐시 활용
4. 시맨틱 유사도 기반 → 완전 동일하지 않아도 캐시 히트 가능

---

## E-32 deterministic과의 차이

| 스킬 | 목적 | 방식 |
|------|------|------|
| `/deterministic` | **품질/재현성** | 동일 입력 → 동일 출력 보장, drift 감지 |
| `/gpt-cache` | **비용/속도** | 유사 입력 → 이전 출력 반환 (캐싱) |

---

## 실행 절차

### `/gpt-cache enable` — 캐싱 활성화

```
1. GPTCache 초기화
   - 캐시 저장소: D:\VAMOS\.cache\gptcache\
   - 유사도 임계값: 0.92 (기본)
2. 이후 모든 LLM 호출에 캐시 레이어 적용
3. 캐시 히트 시 → 저장된 응답 반환 (API 호출 없음)
4. 캐시 미스 시 → API 호출 후 응답 캐시에 저장
```

### `/gpt-cache disable` — 캐싱 비활성화

```
1. 캐시 레이어 해제
2. 모든 LLM 호출이 실제 API로 전달
3. 캐시 데이터는 유지 (clear로 삭제 가능)
```

### `/gpt-cache stats` — 통계 조회

```
캐시 히트율, 절감 비용, 총 호출 수, 캐시 크기 등 표시
```

### `/gpt-cache clear` — 캐시 초기화

```
캐시 전체 삭제. SOT가 변경된 경우 사용 권장.
```

---

## 출력 형식

### stats 출력
```json
{
  "gptcache_stats": {
    "enabled": true,
    "total_calls": 0,
    "cache_hits": 0,
    "cache_misses": 0,
    "hit_rate": "0%",
    "estimated_savings": "$0.00",
    "cache_size_mb": 0,
    "similarity_threshold": 0.92
  }
}
```

## 저장 위치

`D:\VAMOS\.cache\gptcache\`

---

## $ARGUMENTS 처리

- `$ARGUMENTS`가 `enable`이면 → 캐싱 활성화
- `$ARGUMENTS`가 `disable`이면 → 캐싱 비활성화
- `$ARGUMENTS`가 `stats`이면 → 통계 조회
- `$ARGUMENTS`가 `clear`이면 → 캐시 초기화
- `$ARGUMENTS`가 비어있으면 → 현재 상태 표시
