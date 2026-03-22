---
name: giskard-scan
description: Giskard로 EA 추출 파이프라인의 취약점(환각/편향/견고성) 자동 스캔
triggers:
  - /giskard-scan
args:
  - name: target
    description: "EA 번호, all, 또는 report"
  - name: --category
    description: "C1~C8 특정 카테고리 집중 스캔"
    optional: true
---

# `/giskard-scan` — Giskard 취약점 자동 스캔

## 목적
EA 추출 파이프라인의 **취약점을 사전 스캔/발견**.

## D-21 Evidently와의 차이
```
D-21 Evidently: 결과 모니터링/회귀 탐지 (사후 평가)
D-43 Giskard: 취약점 사전 스캔/발견 (사전 평가)
→ Giskard로 약점 발견 → 수정 → Evidently로 모니터링
```

## 전제 조건
- `pip install giskard`

## 스캔 항목
- **환각 취약점**: 어떤 입력 유형에서 환각이 잘 발생하는지
- **편향 취약점**: 특정 카테고리/도메인에서 성능이 떨어지는지
- **견고성 취약점**: 입력 변형(오타, 줄바꿈, 인코딩)에 얼마나 민감한지
- **성능 취약점**: 긴 문서/복잡한 구조에서 정확도 하락 패턴

## 실행 절차

### `/giskard-scan [EA번호|all]`
```bash
python D:\VAMOS\.claude\hooks\giskard_scanner.py \
  --ea <EA파일> \
  --sot <SOT파일> \
  --output <scan_result.json>
```

### `/giskard-scan report`
이전 스캔 결과를 종합 리포트로 출력

### `/giskard-scan category [C1~C8]`
특정 카테고리 집중 스캔

### 보고서 출력
```
## Giskard 취약점 스캔 결과

### 발견된 취약점
| # | 유형 | 심각도 | 설명 | 영향 범위 |
|---|------|--------|------|----------|
| 1 | 환각 | HIGH | 긴 문서(>5000자)에서 수치 환각 발생 | EA-07, EA-12 |
| 2 | 견고성 | MEDIUM | 줄바꿈이 많은 표에서 파싱 실패 | EA-03 |

### 권장 조치
1. 긴 문서는 청크 분할 후 추출
2. 표 형태 SOT는 전처리 후 추출
```

## 판정 기준
- **PASS**: HIGH 심각도 취약점 0개
- **WARN**: HIGH 0개이나 MEDIUM ≥ 3개
- **FAIL**: HIGH 심각도 취약점 ≥ 1개 → 권장 조치 수행 후 재스캔 필요

## 저장 위치
- 스캔 결과 JSON: `D:\VAMOS\04. 구현단계\{version}_results\{phase}\giskard_scan_result.json`
- 보고서: 콘솔 출력 (Markdown 테이블)
