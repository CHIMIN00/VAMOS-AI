---
name: llama-firewall
description: Meta LlamaFirewall 기반 다계층 AI 보안. PromptGuard 2로 프롬프트 injection 탐지, AlignmentCheck로 지침 준수 검증, CodeShield로 코드 보안 검증.
---

# VAMOS E-44 LlamaFirewall 스킬 (Meta AI Security)

> `/llama-firewall [scan-input|scan-output|alignment] [파일경로]` — 다계층 AI 보안 검증

## 기반 기술

- **LlamaFirewall** (Meta): 다계층 AI 보안 프레임워크
- **PromptGuard 2**: 프롬프트 injection/jailbreak 탐지 (86M 파라미터 전용 모델)
- **AlignmentCheck**: LLM 출력이 시스템 지침과 일치하는지 검증
- **CodeShield**: 코드 생성 시 보안 취약점 자동 탐지

---

## 기능

1. SOT 입력 보안 스캔 — 악의적 프롬프트 injection 탐지
2. EA 출력 보안 검증 — 생성된 결과의 안전성 확인
3. 지침 준수 여부 검증 — 시스템 프롬프트와 출력의 정합성

---

## B-14 LLM Guard와의 차이

| 도구 | 방식 | 정밀도 |
|------|------|--------|
| B-14 LLM Guard | 규칙 기반 입출력 스캐너 | 경량, 빠름 |
| E-44 LlamaFirewall | Meta 전용 모델 기반 (PromptGuard 2) | 고정밀, 모델 필요 |

---

## 실행 절차

### `/llama-firewall scan-input [SOT파일]` — SOT 입력 보안 스캔

```
1. SOT 파일 로드
2. PromptGuard 2 모델로 각 섹션 스캔
3. injection/jailbreak 패턴 탐지
4. 위험도별 분류: SAFE / SUSPICIOUS / DANGEROUS
5. 결과 보고서 출력
```

### `/llama-firewall scan-output [EA파일]` — EA 출력 보안 검증

```
1. EA JSON 로드
2. CodeShield로 코드 관련 필드 보안 검증
3. 각 항목의 안전성 판정
4. 결과 보고서 출력
```

### `/llama-firewall alignment [EA파일]` — 지침 준수 여부 검증

```
1. EA JSON + 시스템 프롬프트(추출 지침) 로드
2. AlignmentCheck로 출력이 지침을 벗어나지 않았는지 검증
3. 편차 항목 식별 및 보고
```

---

## 출력 형식

```json
{
  "firewall_metadata": {
    "target": "파일 경로",
    "scan_type": "scan-input|scan-output|alignment",
    "timestamp": "2026-03-20T10:00:00",
    "model": "PromptGuard2|CodeShield|AlignmentCheck"
  },
  "results": [
    {
      "section": "섹션명 또는 key",
      "status": "SAFE|SUSPICIOUS|DANGEROUS",
      "confidence": 0.95,
      "detail": "탐지 내용 설명"
    }
  ],
  "summary": {
    "total_scanned": 0,
    "safe": 0,
    "suspicious": 0,
    "dangerous": 0,
    "verdict": "PASS|REVIEW_NEEDED|BLOCKED"
  }
}
```

## 저장 위치

`v13_results/phase0/extraction/validation/{파일명}_firewall_report.json`

---

## 설치 상태

```
pip install llamafirewall  — 설치 완료 (v1.0.3)
PromptGuard 2 모델 — llamafirewall configure 로 다운로드 필요 (GPU 권장)
```

---

## $ARGUMENTS 처리

- `$ARGUMENTS`가 `scan-input [파일]`이면 → SOT 입력 보안 스캔
- `$ARGUMENTS`가 `scan-output [파일]`이면 → EA 출력 보안 검증
- `$ARGUMENTS`가 `alignment [파일]`이면 → 지침 준수 여부 검증
- `$ARGUMENTS`가 비어있으면 → 사용법 안내
