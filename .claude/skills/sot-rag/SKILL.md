---
name: sot-rag
description: 다른 스킬 실행 시 자동으로 관련 SOT 구절을 컨텍스트에 주입 (RAG)
triggers:
  - /sot-rag
args:
  - name: command
    description: "enable | disable | status"
---

# `/sot-rag` — SOT RAG 컨텍스트 자동 주입

## 목적
다른 스킬(extract, audit 등) 실행 시 **관련 SOT 구절을 자동으로 컨텍스트에 주입**.
D-22 /sot-search가 "명시적 검색"이라면, 이것은 "자동 주입".

## 전제 조건
- D-22 /sot-search의 인덱스 구축 완료 (Milvus)
- `pip install pymilvus sentence-transformers`

## D-22와의 차이
```
D-22 /sot-search: 사용자가 명시적으로 검색 요청
D-24 /sot-rag: 다른 스킬 실행 시 자동으로 관련 SOT 구절을 컨텍스트에 주입
```

## 실행 절차

### `/sot-rag enable`
RAG 자동 주입 활성화. 이후 EA 추출/검증 시:

```
1. 현재 작업 중인 항목의 key/value에서 쿼리 생성
   ↓
2. Milvus에서 관련 SOT 구절 top-3 검색
   - E-45 KR-SBERT 설치 시 한국어 의미 검색 정확도 향상
   - 기본 모델 대비 한국어 SOT에서 검색 품질 대폭 개선
   ↓
3. 검색된 구절을 컨텍스트에 자동 추가
   - 토큰 예산 내에서 관련성 높은 구절 우선 주입
   - 최대 주입량: 3,000 토큰 (설정 변경 가능)
   ↓
4. 추출/검증 스킬이 주입된 컨텍스트와 함께 실행
   - 환각 감소: SOT 원문이 직접 컨텍스트에 존재
   - 누락 감소: 관련 구절이 프롬프트에 포함됨
```

### `/sot-rag disable`
자동 주입 비활성화. 캐시된 인덱스는 유지됨.

### `/sot-rag status`
현재 RAG 상태 + 인덱스 통계 출력

---

## D-22 `/sot-search`와의 차이

| 항목 | `/sot-search` | `/sot-rag` |
|------|--------------|------------|
| 방식 | 사용자가 명시적으로 검색 요청 | 다른 스킬 실행 시 자동 주입 |
| 트리거 | `/sot-search "검색어"` | extract/audit 등 스킬 실행 시 자동 |
| 결과 | 검색 결과를 사용자에게 표시 | 검색 결과를 스킬 컨텍스트에 주입 |
| 용도 | 탐색/조사 | 추출/검증 정확도 향상 |

---

## 성능 영향

```
토큰 증가: 요청당 약 1,000~3,000 토큰 추가
비용 증가: 요청당 약 $0.003~$0.009 (Claude 기준)
정확도 향상: source_text 매칭률 +15~25% (추정)
```

---

## Python 스크립트

```bash
python D:\VAMOS\.claude\hooks\rag_context_injector.py \
  --query "검색할 내용" \
  --top-k 3 \
  --max-tokens 3000 \
  --output context.json
```

---

## 출력 형식

```json
{
  "rag_metadata": {
    "enabled": true,
    "index_status": "ready|not_built",
    "total_chunks": 0,
    "embedding_model": "snunlp/KR-SBERT-V40K-klueNLI-augSTS"
  },
  "injected_context": [
    {
      "source_file": "SOT 파일명",
      "chunk": "관련 구절 텍스트...",
      "similarity_score": 0.92,
      "start_line": 100,
      "end_line": 120
    }
  ],
  "stats": {
    "total_queries": 0,
    "avg_similarity": 0.0,
    "tokens_injected": 0
  }
}
```

## 저장 위치

`v13_results/phase0/extraction/rag_injection_log.json`

---

## $ARGUMENTS 처리

- `$ARGUMENTS`가 `enable`이면 → RAG 자동 주입 활성화
- `$ARGUMENTS`가 `disable`이면 → RAG 자동 주입 비활성화
- `$ARGUMENTS`가 `status`이면 → 현재 상태 + 인덱스 통계 출력
- `$ARGUMENTS`가 비어있으면 → 현재 상태 출력
