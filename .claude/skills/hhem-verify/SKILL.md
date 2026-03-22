---
name: hhem-verify
description: Vectara HHEM 환각 탐지 전용 모델로 EA 항목의 사실 일관성(factual consistency) 점수 산출
triggers:
  - /hhem-verify
args:
  - name: target
    description: EA 파일 경로 또는 "all"
  - name: --threshold
    description: "이 점수 미만만 표시 (기본: 0.8)"
    optional: true
    default: "0.8"
---

# `/hhem-verify` — Vectara HHEM 환각 탐지

## 목적
**환각 탐지 전용 학습 모델**(Vectara HHEM-2.1)로 EA 항목이 SOT 원문과 사실적으로 일관되는지 점수화.
API 키 불필요, GPU 불필요, CPU에서 로컬 실행.

## C-40 대체 근거
```
원래 C-40 (Cleanlab TLM): 학습된 신뢰도 모델 → 서비스 접속 불가로 대체
대체 C-40 (Vectara HHEM): 환각 탐지 전용 학습 모델 (flan-t5-base 기반)
→ 동일한 "학습 기반 신뢰도 판정" 접근법
```

## 기존 도구와의 차이
```
C-17 cross-model:  GPT가 판정 (LLM-as-a-judge)
C-18 confidence:   반복 추출 일치율 (통계적)
B-37 minicheck:    NLI 모델 (사실 검증 특화)
C-40 hhem-verify:  환각 탐지 전용 모델 (환각 판정 특화, flan-t5 기반)
→ 4가지 서로 다른 접근법 → 합의 시 신뢰도 극대화
```

## 전제 조건
- `pip install transformers torch` 설치 완료
- API 키 불필요
- GPU 불필요 (CPU, RAM 600MB)

## 실행 절차

### Step 1: 대상 EA 로드 + SOT 매핑
```
EA JSON 로드 → 각 항목의 원본 SOT 파일 식별
(EA의 source_file 또는 metadata.sot_path 필드 활용)
```

### Step 2: (premise, hypothesis) 쌍 구성
각 EA 항목을 HHEM 입력 형태로 변환:
```json
{
  "premise": "SOT 원문 텍스트 (해당 항목 주변 ±500자)",
  "hypothesis": "EA에서 추출된 key: value 정보를 자연어 문장으로 변환",
  "ea_item": "EA-001",
  "field": "field_name"
}
```

### Step 3: Python 스크립트 실행
```bash
python D:\VAMOS\.claude\hooks\hhem_scorer.py \
  --input <temp_pairs.json> \
  --threshold 0.8 \
  --output <temp_results.json>
```

### Step 4: 결과 분석
각 항목에 대해 0~1 점수:
- **0.8~1.0**: SOT와 일관됨 → PASS
- **0.5~0.8**: 부분 일관 → 수동 확인 권장
- **0.0~0.5**: 불일관 → 환각 의심 → 재추출 대상

### Step 5: 보고서 출력
```
## HHEM 환각 탐지 결과

| # | EA항목 | 필드 | 추출값 | HHEM 점수 | 판정 |
|---|--------|------|--------|-----------|------|
| 1 | EA-001 | name | "FastAPI" | 0.95 | PASS |
| 2 | EA-003 | ver | "3.0" | 0.32 | FAIL (환각 의심) |

### 요약
- 전체: N건
- PASS (≥ threshold): X건 (Y%)
- WARN (0.5~threshold): Z건
- FAIL (< 0.5): W건 → 재추출 대상
```

## 판정 기준
- **PASS**: FAIL(< 0.5) 항목 비율 < 5%
- **WARN**: FAIL 5~15%
- **FAIL**: FAIL > 15% → 해당 항목 재추출 필수

## 저장 위치
- 결과 JSON: `D:\VAMOS\04. 구현단계\{version}_results\{phase}\hhem_result.json`
- 보고서: 콘솔 출력 (Markdown 테이블)

## 비용
- **$0** (완전 무료, 로컬 실행)
- 모델 크기: ~600MB (첫 실행 시 자동 다운로드, 이후 캐시)
- 처리 속도: ~1.5초/건 (CPU)
