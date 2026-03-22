---
name: phoenix-observe
description: Arize Phoenix로 LLM 관측/평가 올인원 (traces, evals, datasets, experiments)
triggers:
  - /phoenix-observe
args:
  - name: command
    description: "start | trace [phase번호] | eval [EA파일] | rag-analysis"
---

# `/phoenix-observe` — Arize Phoenix LLM 관측

## 목적
**오픈소스 LLM 관측/평가 올인원 플랫폼**. Traces, Evals, Datasets, Experiments를 하나의 UI에서.

## 전제 조건
- Phoenix Docker 컨테이너 실행 중 (localhost:6006)
- HTTP API로 연동 (pip import 불필요)

## D-19 Langfuse와의 차이
```
D-19 Langfuse: Docker 필수, 웹 대시보드 중심, 프로덕션 로깅
D-42 Phoenix: 평가 메트릭 내장 (RAGAS/DeepEval 연동), 실험 비교
→ Langfuse = 로깅/추적, Phoenix = 평가/실험
```

## 실행 절차

### `/phoenix-observe start`
Phoenix UI URL 출력: http://localhost:6006

### `/phoenix-observe trace [phase번호]`
Phase 실행을 Phoenix에 기록

```bash
python D:\VAMOS\.claude\hooks\phoenix_tracer.py \
  --action trace \
  --phase 0 \
  --input <실행결과.json>
```

### `/phoenix-observe eval [EA파일]`
EA 파일에 대한 평가 메트릭 시각화

```bash
python D:\VAMOS\.claude\hooks\phoenix_tracer.py \
  --action eval \
  --input <EA파일.json>
```

### `/phoenix-observe rag-analysis`
RAG 파이프라인 검색 품질 분석 (D-24 sot-rag 연동)

```bash
python D:\VAMOS\.claude\hooks\phoenix_tracer.py \
  --action rag-analysis \
  --input <검색결과.json>
```

---

## D-19 Langfuse `/trace`와의 차이

| 항목 | `/trace` (Langfuse) | `/phoenix-observe` (Phoenix) |
|------|---------------------|------------------------------|
| 목적 | 실행 로깅/추적 | 평가/실험 비교 |
| UI | Langfuse 대시보드 (localhost:3000) | Phoenix UI (localhost:6006) |
| 강점 | 프로덕션 로깅, 비용 추적 | RAGAS/DeepEval 내장, 실험 A/B 비교 |
| 사용 시점 | Phase 실행 중 자동 로깅 | Phase 완료 후 품질 분석 |

---

## 출력 형식

```json
{
  "phoenix_metadata": {
    "ui_url": "http://localhost:6006",
    "action": "trace|eval|rag-analysis",
    "timestamp": "2026-03-20T10:00:00"
  },
  "summary": {
    "total_traces": 0,
    "avg_latency_sec": 0.0,
    "total_tokens": 0,
    "estimated_cost_usd": 0.0
  },
  "eval_metrics": {
    "faithfulness": 0.0,
    "relevance": 0.0,
    "correctness": 0.0,
    "hallucination_rate": 0.0
  },
  "experiments": [
    {
      "name": "phase0_v13",
      "metrics": {},
      "comparison_to_baseline": "improved|degraded|stable"
    }
  ]
}
```

## 저장 위치

`v13_results/phase0/observability/{phase번호}_phoenix_report.json`

---

## $ARGUMENTS 처리

- `$ARGUMENTS`가 `start`이면 → Phoenix UI URL 출력
- `$ARGUMENTS`가 `trace [phase번호]`이면 → Phase 실행을 Phoenix에 기록
- `$ARGUMENTS`가 `eval [EA파일]`이면 → 평가 메트릭 시각화
- `$ARGUMENTS`가 `rag-analysis`이면 → RAG 검색 품질 분석
- `$ARGUMENTS`가 비어있으면 → 현재 Phoenix 상태 출력
