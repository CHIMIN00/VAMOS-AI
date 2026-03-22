---
name: sot-graph
description: Neo4j로 SOT 68개 파일 간 관계를 그래프로 시각화 + 영향 분석
triggers:
  - /sot-graph
args:
  - name: command
    description: "build | impact [문서ID] | deps [모듈ID] | visualize"
---

# `/sot-graph` — SOT Knowledge Graph

## 목적
SOT 68개 파일 간의 **관계를 그래프로 시각화**. 문서 수정 시 영향 범위, 모듈 의존성 트리 등 구조적 분석.

## 전제 조건
- Neo4j 서버 실행 중 (localhost:7474, bolt://localhost:7687)
- 인증: neo4j/password
- `pip install neo4j`

## 실행 절차

### `/sot-graph build`
SOT 파일을 파싱하여 그래프 구축:
- 노드: 문서, 모듈, 개념, 수치
- 엣지: 참조, 의존, 포함, 제약

```bash
python D:\VAMOS\.claude\hooks\sot_graph_builder.py \
  --sot-dir "D:\VAMOS\03. 분석단계" \
  --neo4j-uri bolt://localhost:7687
```

### `/sot-graph impact [문서ID]`
"이 문서를 수정하면 어떤 문서가 영향받는지?"

### `/sot-graph deps [모듈ID]`
"이 모듈이 의존하는 모든 모듈은?"

### `/sot-graph visualize`
Neo4j 브라우저 URL 출력: http://localhost:7474

### 보고서 출력
```
## SOT 관계 그래프

### 통계
- 노드: N개 (문서 X, 모듈 Y, 개념 Z)
- 엣지: M개 (참조 A, 의존 B, 포함 C)

### 영향 분석: D2.0-07
- 직접 영향: D2.0-03, D2.0-05
- 간접 영향: D2.0-01 (D2.0-03 경유)
```

## 판정 기준
- 탐색/시각화 스킬이므로 PASS/FAIL 판정 없음 (구조 분석 목적)
- `impact` 명령 실행 시 영향 범위 0개 = 고립된 문서 (참고 사항)

## 저장 위치
- 그래프 데이터: Neo4j DB (bolt://localhost:7687)
- 영향 분석 결과: 콘솔 출력 (Markdown). 필요시 `--output` 옵션으로 JSON 저장 가능
