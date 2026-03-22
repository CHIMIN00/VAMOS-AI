---
name: exa-verify
description: Exa 검색 엔진으로 EA 항목의 기술 용어/수치를 외부 소스에서 검증
triggers:
  - /exa-verify
args:
  - name: target
    description: EA 파일 경로 또는 "all"
  - name: --tech-terms
    description: 기술 용어만 검증
    optional: true
  - name: --all-claims
    description: 전체 claim 검증
    optional: true
---

# `/exa-verify` — Exa 외부 소스 검증

## 목적
EA JSON의 source_text에 포함된 **기술 용어, 버전 번호, 수치**를 Exa 검색 엔진으로 외부 소스에서 교차 검증한다.

## 전제 조건
- 환경변수 `EXA_API_KEY` 설정 완료
- `pip install exa-py` 설치 완료

## 실행 절차

### Step 1: 대상 파일 로드
```
target이 파일 경로 → 해당 EA JSON 로드
target이 "all" → D:\VAMOS\04. 구현단계\ 아래 모든 *_ea.json 수집
```

### Step 2: 검증 대상 claim 추출
```
--tech-terms 모드:
  각 EA 항목에서 기술 용어/버전/수치만 추출
  예: "Pydantic v2", "Tauri 2.0", "React 18", "PostgreSQL 15"

--all-claims 모드 (기본):
  source_text를 atomic claim으로 분해
```

### Step 3: Python 스크립트 실행
```bash
python D:\VAMOS\.claude\hooks\exa_verifier.py \
  --input <temp_claims.json> \
  --output <temp_results.json>
```

### Step 4: 결과 분석
각 claim에 대해:
- **VERIFIED**: Exa 검색 결과가 claim을 지지 (similarity > 0.8)
- **UNVERIFIED**: 관련 소스를 찾았으나 내용 불일치
- **NOT_FOUND**: 관련 소스 자체를 찾지 못함

### Step 5: 보고서 출력
```
## Exa 외부 검증 결과

| # | EA항목 | claim | 판정 | 근거 URL | 유사도 |
|---|--------|-------|------|----------|--------|
| 1 | EA-001.field_a | Pydantic v2 | VERIFIED | https://... | 0.95 |
| 2 | EA-003.field_b | Tauri 3.0 | UNVERIFIED | https://... | 0.42 |

### 요약
- 전체: N건
- VERIFIED: X건 (Y%)
- UNVERIFIED: Z건 → 수동 확인 필요
- NOT_FOUND: W건
```

## 판정 기준
- **PASS**: UNVERIFIED 비율 < 10% AND NOT_FOUND < 20%
- **WARN**: UNVERIFIED 10~20% 또는 NOT_FOUND 20~40%
- **FAIL**: UNVERIFIED > 20% 또는 NOT_FOUND > 40%

## 저장 위치
- 결과 JSON: `D:\VAMOS\04. 구현단계\{version}_results\{phase}\exa_verify_result.json`
- 보고서: 콘솔 출력 (Markdown 테이블)

## 비용 참고
- 검색 1건: $0.003, 콘텐츠 추출: $0.001
- 가입 시 무료 $5 크레딧 제공 → 약 1,250건 검증 가능
