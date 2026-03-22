---
name: cross-model
description: Claude + GPT 교차 추출로 모델 간 불일치 = 환각 후보 탐지
triggers:
  - /cross-model
args:
  - name: target
    description: SOT 파일 경로, EA 번호, 또는 "all"
  - name: --model
    description: "GPT 모델 선택 (기본: gpt-4o-mini)"
    optional: true
    default: gpt-4o-mini
---

# `/cross-model` — 교차 모델 일관성 검증

## 목적
동일 SOT를 **Claude + GPT로 각각 독립 추출**하여 비교. 불일치 항목 = 환각 후보로 분류.

## 전제 조건
- 환경변수 `OPENAI_API_KEY` 설정 완료
- `pip install openai` 설치 완료

## 실행 절차

### Step 1: 대상 결정
```
target이 SOT 파일 → 해당 SOT에서 추출
target이 EA 번호 → 해당 EA의 원본 SOT를 찾아서 사용
target이 "all" → 전체 SOT 순회
```

### Step 2: Claude 추출 (기존 EA 결과 활용)
```
이미 존재하는 EA JSON을 Claude 추출 결과로 사용
```

### Step 3: GPT 추출 실행
```bash
python D:\VAMOS\.claude\hooks\cross_model_compare.py \
  --sot <SOT파일> \
  --claude-ea <기존EA.json> \
  --model gpt-4o-mini \
  --output <temp_comparison.json>
```

GPT에게 동일한 추출 프롬프트를 전달하여 독립적으로 EA 추출.

### Step 4: 항목별 비교
각 필드에 대해:
- **MATCH**: Claude와 GPT 결과 동일 → 높은 신뢰도
- **PARTIAL**: 의미는 같으나 표현 차이 → 정상 (동의어, 포맷 차이)
- **MISMATCH**: 내용 불일치 → 환각 후보 → 수동 확인 필요
- **GPT_ONLY**: GPT만 추출, Claude 누락 → 누락 후보
- **CLAUDE_ONLY**: Claude만 추출, GPT 누락 → GPT 누락 (참고)

### Step 5: 보고서 출력
```
## 교차 모델 검증 결과 (Claude vs GPT-4o-mini)

| # | EA항목 | 필드 | Claude 값 | GPT 값 | 판정 |
|---|--------|------|-----------|--------|------|
| 1 | EA-001 | name | "FastAPI" | "FastAPI" | MATCH |
| 2 | EA-003 | version | "3.0" | "2.1" | MISMATCH |

### 요약
- 전체 비교: N 필드
- MATCH: X건 (Y%) — 신뢰도 높음
- MISMATCH: Z건 — 수동 확인 필요
- 합의율: Y%
```

## 판정 기준
- **PASS**: 합의율(MATCH+PARTIAL) ≥ 90%
- **WARN**: 합의율 70~89%
- **FAIL**: 합의율 < 70% → MISMATCH 항목 수동 확인 필수

## 저장 위치
- 비교 결과 JSON: `D:\VAMOS\04. 구현단계\{version}_results\{phase}\cross_model_result.json`
- 보고서: 콘솔 출력 (Markdown 테이블)

## 비용 참고
- GPT-4o-mini: 입력 $0.15/1M, 출력 $0.60/1M → 전체 약 $0.60
- GPT-4o: 입력 $2.50/1M, 출력 $10.00/1M → 전체 약 $10
