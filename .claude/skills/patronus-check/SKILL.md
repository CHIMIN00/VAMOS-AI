---
name: patronus-check
description: Patronus Lynx 환각 탐지 전문 모델로 EA 항목의 충실성(faithfulness) 검증
triggers:
  - /patronus-check
args:
  - name: target
    description: EA 파일 경로 또는 "all"
  - name: --mode
    description: "api (Patronus API) 또는 local (로컬 모델)"
    optional: true
    default: api
---

# `/patronus-check` — Patronus Lynx 환각 탐지

## 목적
**환각 탐지 전문 LLM**(Patronus Lynx)으로 EA 항목이 SOT에 충실한지 검증.
범용 모델(Claude)과 다른 **환각 탐지 특화 모델**로 독립적 판정.

## 기존 도구와의 차이
```
A-1 /hallucination-check: Claude가 자체 환각 탐지 (범용 모델)
B-37 /minicheck: NLI 모델이 사실 검증 (NLI 특화)
C-41 /patronus-check: 환각 탐지 전문 LLM (환각 탐지 특화)
→ 3가지 서로 다른 접근법 → 합의 시 신뢰도 극대화
```

## 전제 조건
- **API 모드**: 환경변수 `PATRONUS_API_KEY` 설정 + `pip install patronus`
- **로컬 모드**: GPU(VRAM 16GB+) + `pip install transformers torch`

## 실행 절차

### Step 1: 대상 EA 로드 + SOT 매핑
```
EA JSON 로드 → 각 항목의 원본 SOT 파일 식별
(EA의 source_file 또는 metadata.sot_path 필드 활용)
```

### Step 2: 3-튜플 구성
각 EA 항목을 (context, question, answer) 형태로 변환:
```json
{
  "context": "SOT 원문 텍스트 (해당 항목 주변 ±500자)",
  "question": "이 문서에서 [field_name]의 값은 무엇인가?",
  "answer": "EA에서 추출된 값"
}
```

### Step 3: Python 스크립트 실행
```bash
python D:\VAMOS\.claude\hooks\patronus_checker.py \
  --input <temp_tuples.json> \
  --mode api \
  --output <temp_results.json>
```

### Step 4: 결과 분석
각 항목에 대해:
- **FAITHFUL**: 답변이 context에 충실함
- **NOT_FAITHFUL**: 답변이 context에서 뒷받침되지 않음 + 근거 설명
- **ERROR**: 검증 실패

### Step 5: 보고서 출력
```
## Patronus Lynx 환각 탐지 결과

| # | EA항목 | 필드 | 추출값 | 판정 | 근거 |
|---|--------|------|--------|------|------|
| 1 | EA-001 | name | "FastAPI" | FAITHFUL | context에 명시 |
| 2 | EA-003 | ver | "3.0" | NOT_FAITHFUL | context에 "2.1"로 기재 |

### 요약
- 전체: N건
- FAITHFUL: X건 (Y%)
- NOT_FAITHFUL: Z건 → 수동 확인 필요
```

## 판정 기준
- **PASS**: NOT_FAITHFUL 비율 < 5%
- **WARN**: NOT_FAITHFUL 5~15%
- **FAIL**: NOT_FAITHFUL > 15% → 해당 항목 재추출 필수

## 저장 위치
- 결과 JSON: `D:\VAMOS\04. 구현단계\{version}_results\{phase}\patronus_result.json`
- 보고서: 콘솔 출력 (Markdown 테이블)

## 비용 참고
- API: $0.005/호출, 750항목 = $3.75
- 로컬: $0 (GPU VRAM 16GB+ 필요)
