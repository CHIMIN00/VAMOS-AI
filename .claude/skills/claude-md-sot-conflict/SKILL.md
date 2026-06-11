---
name: claude-md-sot-conflict
description: CLAUDE.md 검증 Step 1 — SOT 원본(docs/sot 68개) 간 수치/용어 모순 사전 탐지. CLAUDE.md에 넣을 정답의 일관성 확보.
---

# /claude-md-sot-conflict — SOT 원본 모순 탐지 (Step 1)

> 기반: TOOL GUIDE A-49 `/sot-conflict` 의 CLAUDE.md 검증 전용 확장 (보강전략 V1.0 §6.4)

## 대상
- `D:\VAMOS\docs\sot\*.md` (68개 — 읽기 전용, 수정 금지)

## 방법
1. 핵심 수치 추출: 모듈 수(81/106/187), 비용 한도(₩40K/93K/266K), 임계값(Self-check 70/75/80, QoD 0.4/0.7, cosine 0.95), Gate 정의(5-Gate), 동시성 한도(3/5), max_retries, Hybrid Search 파라미터
2. 동일 개념이 2개+ 파일에 등장하는 경우 수집
3. 값 비교 → 불일치 시 CONFLICT 리포트 (정본 우선순위 RULE 1.3 > PLAN 3.0 > DESIGN LOCK > 본문 > 스키마로 정본 판정 병기)

## 출력
- `CONFLICT-001 ~ N`: 파일명 + 라인 + 값 + 차이 + 정본 판정
- 저장: `D:\VAMOS\04. 구현단계\claude-md-verification\step1_sot_conflict.md`

## 규칙
- RULE-C3: SOT 원본 수정 금지 (읽기만)
- RULE-C4: 발견 오류 즉시 수정 금지 — 기록만
- RULE-C5: 모든 판정에 파일명+라인번호 근거 필수
