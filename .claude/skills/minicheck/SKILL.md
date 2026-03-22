---
name: minicheck
description: MiniCheck NLI 모델 기반 사실 검증. EA의 각 claim을 SOT 원문과 1:1 대조하여 Supported/Not Supported 판정. AI 판단이 아닌 NLI 모델의 결정론적 판단.
---

# VAMOS NLI 사실 검증 스킬 (MiniCheck)

> `/minicheck [EA파일|all]` — NLI 기반 사실 검증 (Supported / Not Supported)

## 기존 스킬과의 차이

| 스킬 | 검증 방식 |
|------|----------|
| `/hallucination-check` (A-1) | claim 분해 → SOT 텍스트 매칭 (AI 기반) |
| `/fact-audit` (A-2) | 3-에이전트 토론 구조 (AI 기반) |
| `/minicheck` (B-37) | **NLI 전용 모델의 결정론적 판단** (학습된 모델) |

> AI 판단이 아닌 NLI 모델의 결정론적 판단 → **Layer A 수준의 신뢰도**

---

## 선행 조건

```bash
pip install minicheck                          # API 모드 (경량)
# 또는 로컬 모델 사용 시:
pip install minicheck[local] torch transformers
```

---

## 실행 절차

```
1. $ARGUMENTS 파싱 → 대상 EA + 모드(api/local) 결정
   ↓
2. Python 훅 실행:
   python "D:/VAMOS/.claude/hooks/minicheck_verifier.py" "<EA_JSON_경로>" [--mode api|local]
   ↓
3. 훅 동작:
   a. EA JSON 로딩
   b. 각 항목에서 claim 생성:
      - "{key}의 값은 {value}이다"
      - "이 정보의 출처는 {source_text}이다"
   c. SOT 원본에서 해당 줄 ±5줄 추출 (document)
   d. MiniCheck 모델로 (document, claim) 판정
   e. Supported / Not Supported 분류
   ↓
4. 결과 집계 및 저장
```

---

## 출력

```json
{
  "minicheck_metadata": {
    "target_file": "v13_EA01_claude_md.json",
    "mode": "api|local",
    "total_claims": 170,
    "supported": 165,
    "not_supported": 5,
    "support_rate": 0.97,
    "verdict": "PASS|FAIL"
  },
  "claims": [
    {
      "item_id": 1,
      "claim": "TOTAL_MODULE_COUNT의 값은 81이다",
      "document_excerpt": "전체 모듈 수는 81개로 구성...",
      "result": "Supported|Not Supported",
      "confidence": 0.95
    }
  ]
}
```

**저장**: `v13_results/phase0/extraction/validation/{파일명}_minicheck_result.json`

---

## 판정 기준

| 판정 | 조건 |
|------|------|
| **PASS** | support_rate ≥ 0.95 |
| **FAIL** | support_rate < 0.95 |

---

## $ARGUMENTS 처리

- `$ARGUMENTS`가 파일 경로면 → 해당 EA만 검증
- `$ARGUMENTS`가 `all`이면 → 전체 EA 검증
- `$ARGUMENTS`가 `--mode api`이면 → API 모드 (경량, 네트워크 필요)
- `$ARGUMENTS`가 `--mode local`이면 → 로컬 모델 (GPU 권장)
- `$ARGUMENTS`가 비어있으면 → 가장 최근 EA 파일 검증 (api 모드 기본)
