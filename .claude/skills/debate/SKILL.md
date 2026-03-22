---
name: debate
description: 다수 에이전트 자유 토론을 통한 합의 도출. Scientific Debate 패턴으로 가설 제시 → 반증 시도 → 합의. /fact-audit의 고정 역할과 달리 동등한 에이전트가 자유 토론. EA 전용 + 범용 모드 지원.
---

# VAMOS 다수 에이전트 자유 토론 스킬 (Scientific Debate)

> `/debate [작업설명] --agents 3` — 동등한 에이전트들의 자유 토론으로 합의 도출

## 기반 기술

Claude Agent Teams 합의 패턴 — 여러 Agent를 spawn하여 독립 검증 후 상호 반박/합의를 통해 결론 도출.

---

## 기능

1. **독립 검증**: 여러 Agent를 spawn → 각자 독립적으로 같은 작업 수행
2. **상호 반박**: 결과를 공유하며 서로 반박/합의
3. **합의 채택**: 합의된 결과만 최종 채택
4. **Scientific Debate 패턴**: 가설 제시 → 반증 시도 → 합의 도출

---

## /fact-audit와의 차이

| 스킬 | 역할 구조 | 토론 방식 |
|------|----------|----------|
| `/fact-audit` | 역할 고정 (감사자/반박자/판정자) | 구조화된 역할 기반 검증 |
| `/debate` | 역할 없음, 동등한 에이전트 | 자유 토론, 누구나 반박/동의 가능 |

---

## 실행 절차

```
1. 작업 설명 파싱 (검증 대상, 검증 기준)
   ↓
2. Agent tool로 N개(기본 3) 동등한 에이전트 실행
   - 각 에이전트는 독립적으로 SOT 원본을 읽고 검증
   - 각자 결론 + 근거를 생성
   ↓
3. Round 1 — 독립 검증
   - 각 에이전트 결과 수집
   - 이 시점에서 에이전트 간 정보 공유 없음
   ↓
4. Round 2 — 반박
   - 각 에이전트에게 다른 에이전트의 결론을 제시
   - 반박 또는 동의 의견 수집
   ↓
5. Round 3 — 합의
   - 합의된 항목 → AGREED
   - 합의 불가 → DISPUTED
   ↓
6. DISPUTED 항목 → 수동 확인 대상으로 분류
   ↓
7. 결과 저장
```

---

## $ARGUMENTS 처리

- `작업설명` (자유 텍스트) → 토론 주제
- `--agents N` → 에이전트 수 (기본 3, 최대 5)
- 비어있음 → 가장 최근 EA에 대한 전체 검증 토론

---

## 출력

```json
{
  "debate_metadata": {
    "topic": "...",
    "num_agents": 3,
    "rounds": 3,
    "total_items": 0,
    "agreed": 0,
    "disputed": 0,
    "verdict": "CONSENSUS|PARTIAL_CONSENSUS|NO_CONSENSUS"
  },
  "debate_log": [
    {
      "round": 1,
      "agent_id": "agent-1",
      "position": "...",
      "evidence": ["..."]
    }
  ],
  "final_positions": [
    {
      "item": "...",
      "status": "AGREED|DISPUTED",
      "agreed_value": "...",
      "dissenting_agents": []
    }
  ]
}
```

**저장**:
- EA 모드: `v13_results/phase0/extraction/validation/{파일명}_debate.json`
- 범용 모드: `{대상파일_디렉토리}/{파일명}_debate.json`

**판정**: DISPUTED = 0 → CONSENSUS, DISPUTED <= 3 → PARTIAL_CONSENSUS, 나머지 → NO_CONSENSUS

---

## 범용 모드 (일반 파일 검증)

> EA/CM/SOT가 아닌 **모든 파일**에 대해 다수 에이전트 토론 검증을 수행합니다.

### 자동 모드 판별

```
$ARGUMENTS에 v13_EA / v13_CM / SOT 키워드 포함 → EA 모드 (기존)
$ARGUMENTS에 위 키워드 없음 → 범용 모드 (아래 절차)
```

### 범용 모드 실행 절차

```
1. 대상 파일 및 검증 주제 파싱
   - 파일 경로가 있으면 → 해당 파일을 대상으로 검증
   - 자유 텍스트만 있으면 → 주제에 대한 자유 토론
   ↓
2. 파일 유형별 검증 기준 자동 생성
   - .json → JSON 구조 유효성, 스키마 일관성, 값 정합성
   - .md → 마크다운 구문, 섹션 구조, 참조 링크, 내용 정확성
   - .py → 문법 오류, import 유효성, 로직 정확성, 내장 모듈 제한
   - .yaml/.yml → YAML 구문, 키 구조, 값 유효성
   - 기타 텍스트 → 내용 정확성, 내부 일관성, 누락 확인
   ↓
3. Agent tool로 N개(기본 3) 동등한 에이전트 실행
   - 각 에이전트는 독립적으로 대상 파일을 Read tool로 읽기
   - 자동 생성된 검증 기준 + 파일 내용 기반으로 검증
   - 각자 결론 + 근거 생성
   ↓
4. Round 1 — 독립 검증: 각 에이전트 결과 수집
   ↓
5. Round 2 — 반박: 다른 에이전트의 결론 제시 → 반박/동의
   ↓
6. Round 3 — 합의: AGREED / DISPUTED 판정
   ↓
7. 결과 저장
```

### 범용 모드 검증 항목 (파일 유형 공통)

```
[GD-01] 파일 구문 유효성 — 파일이 정상 파싱/로드 가능한가
[GD-02] 내부 일관성 — 파일 내 참조, 수치, 용어가 자체 모순 없는가
[GD-03] 내용 정확성 — 기술된 내용이 사실과 부합하는가
[GD-04] 완전성 — 명시된 범위 대비 누락된 항목이 없는가
[GD-05] 외부 참조 정합성 — 다른 파일을 참조하는 경우 해당 파일과 일치하는가
[GD-06] 포맷/스타일 준수 — 동일 디렉토리의 유사 파일과 포맷이 일관된가
```

### 범용 모드 사용 예시

```
/debate "이 SKILL.md가 TOOL_GUIDE 명세를 충실히 반영했는가?" --file D:/VAMOS/.claude/skills/consensus/SKILL.md
/debate "Python 훅이 내장 모듈만 사용하는가?" --file D:/VAMOS/.claude/hooks/symbolic_verifier.py
/debate "14개 파일 전체가 기존 스킬 포맷과 일관된가?" --file D:/VAMOS/.claude/skills/
/debate "이 설정 파일에 보안 문제가 없는가?" --file config.yaml
```

### 범용 모드 출력

```json
{
  "debate_metadata": {
    "mode": "general",
    "topic": "...",
    "target_file": "...",
    "file_type": ".md|.py|.json|...",
    "num_agents": 3,
    "rounds": 3,
    "auto_criteria": ["GD-01", "GD-02", "..."],
    "total_items": 0,
    "agreed": 0,
    "disputed": 0,
    "verdict": "CONSENSUS|PARTIAL_CONSENSUS|NO_CONSENSUS"
  },
  "debate_log": [...],
  "final_positions": [...]
}
```
