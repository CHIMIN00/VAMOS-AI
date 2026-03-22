---
name: lineage
description: OpenLineage + Marquez로 EA 값의 출처 역추적 (데이터 계보)
triggers:
  - /lineage
args:
  - name: command
    description: "track [EA파일] | trace [항목ID] | dashboard"
---

# `/lineage` — 데이터 계보 추적

## 목적
전체 파이프라인의 **데이터 계보(lineage) 추적**. "이 값이 어디서 왔는지" 역추적.

## 전제 조건
- Marquez 서버 실행 중 (localhost:5000)
- `pip install openlineage-python`

## 실행 절차

### `/lineage track [EA파일]`
EA 파일의 각 항목에 대해 계보 메타데이터 기록:
```
EA-07 item 12의 value=7
  ← D2.0-07_Safety.md line 234
  ← CM-C7에서 EA-01 item 5와 비교됨
  ← Phase 0 verdict에서 PASS 판정
```

```bash
python D:\VAMOS\.claude\hooks\lineage_tracker.py \
  --action track \
  --ea <EA파일> \
  --marquez-url http://localhost:5000
```

### `/lineage trace [항목ID]`
특정 항목의 출처 역추적

### `/lineage dashboard`
Marquez 대시보드: http://localhost:5000

### 출력 형식
```json
{
  "item_id": "EA-07.item_12",
  "value": 7,
  "lineage": [
    {"stage": "source", "ref": "D2.0-07_Safety.md", "line": 234},
    {"stage": "cross_match", "ref": "CM-C7", "compared_with": "EA-01.item_5"},
    {"stage": "verdict", "ref": "Phase 0", "result": "PASS"}
  ]
}
```

## 판정 기준
- 추적 스킬이므로 PASS/FAIL 판정 없음 (계보 기록 목적)
- 계보가 끊긴 항목(source 단계 없음)이 있으면 **WARNING** 표시

## 저장 위치
- 계보 메타데이터: Marquez DB (http://localhost:5000)
- 추적 결과: 콘솔 출력 (Markdown). Marquez API로도 조회 가능
