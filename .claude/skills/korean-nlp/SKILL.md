---
name: korean-nlp
description: kiwipiepy 기반 한국어 SOT 텍스트 정밀 형태소 분석. 핵심 명사/동사 자동 추출, 문장 분리, 띄어쓰기 보정, 복합 명사 분해 → 표준 키 후보 추천.
---

# VAMOS 한국어 NLP 스킬 (kiwipiepy)

> `/korean-nlp <서브커맨드> [파일]` — 한국어 SOT/EA 텍스트 정밀 형태소 분석

## 기존 스킬과의 차이

| 스킬 | 한국어 처리 |
|------|------------|
| `/validate` SV-2 | AI가 직접 한국어 텍스트 해석 (형태소 경계 부정확 가능) |
| `/korean-nlp` | **kiwipiepy 형태소 분석기로 정밀 분석 후 AI에게 구조화된 데이터 전달** |

> 기존 스킬의 한국어 처리를 보조하는 도구입니다.

---

## VAMOS 특화 가치

```
SOT 68개 파일 중 한국어 비율이 높음
→ 기존 AI는 한국어 형태소 경계를 정확히 못 자르는 경우 있음
→ kiwipiepy로 정밀 분석 후 AI에게 전달 → 추출 정확도 향상
```

---

## 선행 조건

```bash
pip install kiwipiepy
```

---

## 서브커맨드

| 커맨드 | 기능 |
|--------|------|
| `analyze [SOT파일]` | 형태소 분석 + 핵심어 추출 |
| `keywords [EA파일]` | EA 항목의 한국어 키워드 검증 |
| `fix-spacing [텍스트]` | 띄어쓰기 보정 |

---

## 실행 절차

```
1. $ARGUMENTS 파싱 → 서브커맨드 + 대상 결정
   ↓
2. Python 훅 실행:
   python "D:/VAMOS/.claude/hooks/korean_analyzer.py" <서브커맨드> <인자>
   ↓
3-A. analyze 모드:
   - SOT 텍스트 읽기
   - kiwipiepy 형태소 분석
   - 명사(NNG, NNP), 동사(VV) 추출
   - 빈도 기반 핵심어 목록 생성
   - 복합 명사 분해 → 표준 키 후보 추천
   ↓
3-B. keywords 모드:
   - EA JSON의 source_text 필드 추출
   - 각 source_text에서 핵심 명사 추출
   - key와 핵심 명사의 관련성 검증
   ↓
3-C. fix-spacing 모드:
   - 입력 텍스트 띄어쓰기 보정
   - 원본 vs 보정 결과 비교
   ↓
4. 결과 저장
```

---

## 출력

### analyze 모드
```json
{
  "korean_nlp_metadata": {
    "target_file": "D2.0-01_Overview.md",
    "mode": "analyze",
    "total_sentences": 150,
    "total_morphemes": 2300,
    "verdict": "COMPLETE"
  },
  "keywords": [
    {"word": "모듈", "pos": "NNG", "frequency": 45},
    {"word": "시스템", "pos": "NNG", "frequency": 32}
  ],
  "compound_nouns": [
    {"compound": "안전모듈", "decomposed": ["안전", "모듈"], "suggested_key": "SAFETY_MODULE"}
  ]
}
```

### keywords 모드
```json
{
  "korean_nlp_metadata": {
    "target_file": "v13_EA01_claude_md.json",
    "mode": "keywords",
    "items_checked": 85,
    "mismatches": 2,
    "verdict": "PASS|WARNING"
  },
  "mismatches": [
    {
      "item_id": 15,
      "key": "EXP_MODULE_COUNT",
      "source_keywords": ["조건부", "모듈"],
      "issue": "key에 'EXP'이지만 source에 '조건부'"
    }
  ]
}
```

**저장**: `v13_results/phase0/extraction/validation/{파일명}_korean_nlp.json`

---

## 판정 기준

| 모드 | 판정 | 조건 |
|------|------|------|
| analyze | **COMPLETE** | 분석 완료 (항상 COMPLETE) |
| keywords | **PASS** | 불일치 0건 |
| keywords | **WARNING** | 불일치 1건 이상 |

---

## $ARGUMENTS 처리

- `analyze SOT파일` → 해당 SOT 파일 형태소 분석
- `keywords EA파일` → EA 항목의 한국어 키워드 검증
- `fix-spacing "텍스트"` → 띄어쓰기 보정
- 비어있음 → 에러 (서브커맨드 필수)
