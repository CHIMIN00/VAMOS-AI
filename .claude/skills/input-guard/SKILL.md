---
name: input-guard
description: LLM Guard 기반 SOT 파일 prompt injection 사전 스캔 + EA 출력 유해 콘텐츠 검사. PromptInjection, Regex, TokenLimit, Anonymize 스캐너 적용.
---

# VAMOS 입력/출력 보안 스캔 스킬 (LLM Guard)

> `/input-guard [SOT파일|all]` — SOT 파일의 prompt injection 사전 스캔 + EA 출력 안전성 검사

## 기존 스킬과의 차이

| 스킬 | 대상 |
|------|------|
| `/validate` | EA JSON 구조/값 정확성 |
| `/audit` | EA 환각/변조 탐지 |
| `/input-guard` | **SOT 입력 보안** + **EA 출력 안전성** |

> `/validate`가 "정확성 검사"라면, `/input-guard`는 "보안 검사"입니다.

---

## 선행 조건

```bash
pip install llm-guard
```

---

## 사용 시점

```
SOT 파일이 외부 기여자에 의해 수정될 때
→ 악의적 프롬프트가 SOT에 삽입되면
→ AI가 추출 시 오동작 가능
→ /input-guard로 사전 스캔
```

---

## 스캐너 종류

| 스캐너 | 기능 |
|--------|------|
| PromptInjection | 악의적 프롬프트 삽입 탐지 |
| Regex | 비정상 패턴 탐지 (base64, 인코딩 텍스트) |
| TokenLimit | 입력 크기 초과 방지 |
| Anonymize | PII(개인정보) 자동 감지 |

---

## 실행 절차

```
1. $ARGUMENTS 파싱 → 스캔 대상 결정 (SOT 입력 / EA 출력)
   ↓
2. Python 훅 실행:
   - 입력 스캔: python "D:/VAMOS/.claude/hooks/input_scanner.py" scan-input "<SOT_파일>"
   - 출력 스캔: python "D:/VAMOS/.claude/hooks/input_scanner.py" scan-output "<EA_파일>"
   ↓
3. 4개 스캐너 순차 실행:
   a. PromptInjection → 악성 프롬프트 탐지
   b. Regex → 비정상 패턴 탐지
   c. TokenLimit → 크기 초과 확인
   d. Anonymize → PII 감지
   ↓
4. 결과 집계 및 저장
```

---

## 출력

```json
{
  "input_guard_metadata": {
    "target_file": "D2.0-01_Overview.md",
    "scan_mode": "input|output",
    "scanners_applied": 4,
    "threats_detected": 0,
    "verdict": "SAFE|WARNING|BLOCKED"
  },
  "scanner_results": [
    {
      "scanner": "PromptInjection",
      "status": "SAFE|DETECTED",
      "confidence": 0.0,
      "details": ""
    }
  ]
}
```

**저장**: `v13_results/phase0/extraction/validation/{파일명}_input_guard.json`

---

## 판정 기준

| 판정 | 조건 |
|------|------|
| **SAFE** | 모든 스캐너 통과 |
| **WARNING** | PII 감지 또는 TokenLimit 초과 |
| **BLOCKED** | PromptInjection 탐지 → 추출 진행 차단 권고 |

---

## $ARGUMENTS 처리

- `$ARGUMENTS`가 SOT 파일 경로면 → 해당 파일 입력 스캔
- `$ARGUMENTS`가 `scan-output EA파일`이면 → EA 출력 스캔
- `$ARGUMENTS`가 `all`이면 → SOT 디렉토리 전체 스캔
- `$ARGUMENTS`가 `mask-pii EA파일`이면 → EA 출력 PII/민감정보 자동 마스킹
- `$ARGUMENTS`가 비어있으면 → 가장 최근 수정된 SOT 파일 스캔

---

## CAT-32 확장: EA 출력 PII/민감정보 자동 마스킹

### `/input-guard mask-pii [EA파일|all]` — EA 출력에서 PII 자동 탐지 및 마스킹

SOT 원본에 포함된 PII(개인정보)가 EA 추출 결과에 그대로 노출되는 것을 방지합니다.

```
1. EA JSON 로딩
   ↓
2. 각 item의 value/source_text에서 PII 패턴 탐지:
   - 이메일: xxx@xxx.xxx → [EMAIL_MASKED]
   - 전화번호: 010-XXXX-XXXX, +82-XX-XXXX-XXXX → [PHONE_MASKED]
   - 주민등록번호: XXXXXX-XXXXXXX → [RRN_MASKED]
   - IP 주소: XXX.XXX.XXX.XXX → [IP_MASKED]
   - 사번/ID: 정규식 패턴 매칭 → [ID_MASKED]
   - 계좌번호: 은행 계좌 패턴 → [ACCOUNT_MASKED]
   ↓
3. 마스킹 모드 선택:
   - DETECT: 탐지만 하고 리포트 (기본값)
   - MASK: 탐지 + 자동 마스킹 후 새 파일 저장
   - REDACT: 탐지 + 해당 항목 전체 제거
   ↓
4. 마스킹 결과 저장:
   - 원본 EA는 보존
   - 마스킹된 EA는 {파일명}_masked.json으로 별도 저장
   - 마스킹 로그에 원본↔마스킹 매핑 기록 (감사 추적)
```

### PII 마스킹 출력 형식

```json
{
  "pii_masking_metadata": {
    "target_file": "v13_EA01.json",
    "mode": "DETECT|MASK|REDACT",
    "total_items_scanned": 0,
    "pii_detected": 0,
    "pii_masked": 0,
    "timestamp": "2026-03-20T10:00:00"
  },
  "detections": [
    {
      "item_id": "item_042",
      "field": "value",
      "pii_type": "EMAIL",
      "original_snippet": "담당자: kim@company.com",
      "masked_snippet": "담당자: [EMAIL_MASKED]",
      "confidence": 0.98
    }
  ],
  "summary": {
    "EMAIL": 2,
    "PHONE": 1,
    "RRN": 0,
    "IP": 3,
    "ID": 0,
    "ACCOUNT": 0
  },
  "verdict": "CLEAN|PII_FOUND|PII_MASKED"
}
```

### 판정 기준

| 판정 | 조건 |
|------|------|
| CLEAN | PII 탐지 0건 |
| PII_FOUND | PII 탐지됨 (DETECT 모드) → 사람 확인 필요 |
| PII_MASKED | PII 탐지 + 마스킹 완료 (MASK 모드) |

### 저장 위치
- 마스킹 리포트: `v13_results/phase0/extraction/validation/{파일명}_pii_masking.json`
- 마스킹된 EA: `v13_results/phase0/extraction/{파일명}_masked.json`
