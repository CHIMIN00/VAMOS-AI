---
name: sot-conflict
description: SOT 파일들 사이의 모순/불일치 자동 탐지. /cross-match가 EA 간 불일치를 잡는다면, 이것은 SOT 간 불일치를 잡음. 추출 전 원본 품질 검증.
---

# VAMOS SOT 교차 모순 탐지 스킬

> `/sot-conflict [scan|파일A 파일B|numbers|terms]` — SOT 원본 간 모순/불일치 자동 탐지

## 목적

SOT 68개 파일 사이에서 동일 개념에 대한 모순/불일치를 추출 전에 탐지합니다.
"원본이 모순이면 AI가 뭘 추출해도 틀린다" — 원본 품질부터 검증합니다.

**기반 기술**: SOT 간 교차 모순 탐지

---

## 기존 스킬과의 차이

| 스킬 | 대상 | 시점 | 방법 |
|------|------|------|------|
| `/cross-match` | EA 결과물 간 비교 | 추출 후 | EA JSON 키 매칭 |
| `/integrity` | SOT 파일 변경 여부 | 추출 후 | SHA-256 해시 비교 |
| `/sot-conflict` | SOT 원본 내용 간 모순 | 추출 전 | 수치/용어/날짜 교차 비교 |

---

## 탐지 유형

| 유형 | 설명 | 예시 |
|------|------|------|
| 수치 모순 | 동일 개념의 숫자값 불일치 | D2.0-01에서 "81개 모듈" vs D2.0-07에서 "79개 모듈" |
| 용어 불일치 | 같은 개념을 다른 이름으로 사용 | "안전 모듈" vs "Safety Module" vs "보호 모듈" |
| 날짜/버전 충돌 | 문서 간 일정/버전 불일치 | 문서 A의 일정과 문서 B의 일정이 다름 |
| LOCK 값 분산 | LOCK 관련 값이 여러 SOT에 산재 | LOCK 값 일관성 확인 |

---

## 핵심 로직

```
1. SOT 68개 파일에서 핵심 수치/용어/날짜 추출
   ↓
2. 동일 개념이 여러 파일에 등장하는 경우 수집
   - 숫자 + 단위 패턴 매칭 (예: "81개 모듈", "79개 모듈")
   - 용어 정규화 후 동의어 그룹핑
   - 날짜/버전 문자열 추출
   - LOCK/FREEZE 키워드 주변 값 추출
   ↓
3. 값 비교 → 불일치 발견 시 CONFLICT 리포트
   ↓
4. 불일치 항목에 대해 "어느 파일이 정본인가?" 판단은 사람에게 위임
```

---

## $ARGUMENTS 처리

- `scan` → 전체 SOT 교차 모순 스캔 (68개 파일)
- `{SOT파일A} {SOT파일B}` → 두 파일 간 모순 확인
- `numbers` → 수치 불일치만 스캔
- `terms` → 용어 불일치만 스캔
- 비어있음 → `scan` (전체 스캔)

---

## 실행 절차

### `/sot-conflict scan` — 전체 SOT 교차 모순 스캔

```
1. D:/VAMOS/docs/sot/ 전체 68개 파일 로딩
   ↓
2. 각 파일에서 핵심 팩트 추출:
   - 수치: 숫자 + 단위 패턴 (예: "81개", "200ms", "v2.3")
   - 용어: 정의된 개념명, 모듈명, 컴포넌트명
   - 날짜: 일정, 마일스톤, 기한
   - LOCK: LOCK/FREEZE 관련 값
   ↓
3. 동일 개념 그룹핑:
   - 동일 키워드가 2개 이상 파일에 등장하는 경우 수집
   - 유사 문맥에서 다른 값을 사용하는 경우 탐지
   ↓
4. 유형별 비교:
   - 수치: 값 직접 비교
   - 용어: 정규화 후 동의어 여부 판단
   - 날짜: 파싱 후 비교
   - LOCK: 여러 SOT에 산재된 LOCK 값 일관성 확인
   ↓
5. CONFLICT 리포트 생성
   ↓
6. JSON 저장
```

### `/sot-conflict {파일A} {파일B}` — 쌍 비교

```
1. 두 SOT 파일 로딩
   ↓
2. 양쪽에서 팩트 추출
   ↓
3. 교집합 개념 식별
   ↓
4. 값 비교 → CONFLICT 여부 판정
```

### `/sot-conflict numbers` — 수치 불일치만 스캔

```
전체 scan과 동일하나 수치 모순만 탐지
```

### `/sot-conflict terms` — 용어 불일치만 스캔

```
전체 scan과 동일하나 용어 불일치만 탐지
```

---

## 출력 예시

```
CONFLICT-001: MODULE_COUNT
  D2.0-01.md line 45: "81개 모듈"
  D2.0-07.md line 12: "79개 모듈"
  → 사람 확인 필요

CONFLICT-002: SAFETY_TERM
  D3.0-02.md line 88: "안전 모듈"
  D3.0-05.md line 23: "보호 모듈"
  → 동일 개념 여부 사람 확인 필요

CONFLICT-003: MILESTONE_DATE
  D1.0-01.md line 120: "2026-04-15"
  D1.0-03.md line 67: "2026-04-30"
  → 사람 확인 필요
```

---

## 출력 JSON 스키마

```json
{
  "sot_conflict_metadata": {
    "scan_type": "full|numbers|terms|pair",
    "sot_files_scanned": 0,
    "total_conflicts": 0,
    "numeric_conflicts": 0,
    "term_conflicts": 0,
    "date_conflicts": 0,
    "lock_conflicts": 0,
    "verdict": "CLEAN|CONFLICTS_FOUND"
  },
  "conflicts": [
    {
      "conflict_id": "CONFLICT-001",
      "type": "numeric|term|date|lock",
      "concept": "MODULE_COUNT",
      "occurrences": [
        {
          "sot_file": "D2.0-01.md",
          "line": 45,
          "text": "81개 모듈",
          "value": 81
        },
        {
          "sot_file": "D2.0-07.md",
          "line": 12,
          "text": "79개 모듈",
          "value": 79
        }
      ],
      "severity": "CRITICAL|WARNING|INFO",
      "resolution": "HUMAN_REVIEW_REQUIRED"
    }
  ]
}
```

## 저장 위치

`v13_results/phase0/sot_conflict_report.json`

## 사용 시점

- `/extract` 실행 전 SOT 원본 품질 사전 검증
- SOT 파일 대량 업데이트 후 일관성 확인
- Phase 0 시작 시 원본 상태 점검
- 새로운 SOT 파일 추가 시 기존 파일과의 모순 확인

---

## CAT-27 확장: 용어/개념 표준화 (온톨로지 매핑)

### `/sot-conflict ontology` — 동의어/이의어 매핑 구축

SOT 68개 파일에서 동일 개념에 다른 용어를 사용하는 경우를 체계적으로 매핑합니다.

```
1. SOT 전체에서 정의된 용어 추출:
   - 모듈명, 컴포넌트명, 기능명, 약어
   ↓
2. 의미적 유사도 분석 (KR-SBERT 임베딩 활용):
   - cosine similarity > 0.85 → 동의어 후보
   - 예: "사용자 인증" ↔ "로그인 검증" → 유사도 0.91
   ↓
3. 동의어 그룹 생성:
   - GROUP-001: {"사용자 인증", "로그인 검증", "User Authentication"}
   - GROUP-002: {"안전 모듈", "Safety Module", "보호 모듈"}
   ↓
4. 이의어 탐지 (동일 용어, 다른 의미):
   - "모듈"이 문서 A에서는 "소프트웨어 모듈", 문서 B에서는 "하드웨어 모듈"
   - 문맥 분석으로 의미 차이 탐지
   ↓
5. 온톨로지 맵 저장
```

### 온톨로지 맵 출력 형식

```json
{
  "ontology_metadata": {
    "total_terms": 0,
    "synonym_groups": 0,
    "homonyms_detected": 0,
    "timestamp": "2026-03-20T10:00:00"
  },
  "synonym_groups": [
    {
      "group_id": "GROUP-001",
      "canonical_term": "사용자 인증",
      "synonyms": ["로그인 검증", "User Authentication"],
      "sot_files": ["D2.0-01.md", "D3.0-05.md"],
      "similarity_scores": [0.91, 0.88]
    }
  ],
  "homonyms": [
    {
      "term": "모듈",
      "meanings": [
        {"context": "소프트웨어 모듈", "sot_file": "D2.0-01.md"},
        {"context": "하드웨어 모듈", "sot_file": "D4.0-03.md"}
      ]
    }
  ]
}
```

### 저장 위치
`v13_results/phase0/sot_ontology_map.json`

### $ARGUMENTS 추가
- `ontology` → 용어/개념 표준화 매핑 구축

---

## [SOT 2 확장] SOT 2 교차 충돌 탐지 (v2 추가)

> 아래 내용은 기존 SOT 68파일 스캔 기능을 **유지한 채** SOT 2 파일 세트를 추가 스캔하는 확장입니다.

### 추가 스캔 대상

| 대상 | 경로 | 파일 수 |
|------|------|--------|
| SOT 2 상세명세 | `D:/VAMOS/docs/sot 2/*/` | ~18개 .md |
| SOT 2 방식 C 요약 | `D:/VAMOS/docs/sot 2/_method-c-summaries/` | ~7개 .md |
| SOT 2 계획서 | `D:/VAMOS/docs/sot 2/*/*_구조화_종합계획서.md` | ~18개 .md |

### 추가 명령어

- `/sot-conflict sot2-scan` → SOT 2 전체 파일 내부 충돌 스캔
- `/sot-conflict sot2-vs-part2` → SOT 2 ↔ Part2 LOCK 값 불일치 탐지
- `/sot-conflict sot2-vs-sot` → SOT 2 ↔ SOT 원본 68파일 불일치 탐지
- `/sot-conflict sot2-numbers` → SOT 2 내 숫자/임계값 수집 + 전수 비교
- `/sot-conflict sot2-terms` → SOT 2 내 용어 불일치 탐지 (한글/영문 혼용 등)

### SOT 2 특화 충돌 패턴

```
패턴 1: LOCK 값 분산 (SOT 2 ↔ Part2)
  SOT 2 파일 A에서 "α=0.7" → Part2 L2030에서 "α=0.7" → CONSISTENT
  SOT 2 파일 B에서 "α=0.8" → Part2 L2030에서 "α=0.7" → MISMATCH

패턴 2: 방식 C 요약 stale
  방식 C 요약에서 "7-State" → Part2 정본에서 "9-State" → STALE

패턴 3: 도메인 간 중복 정의
  3-3_PKM에서 "SM-2 알고리즘" 정의 → 3-5_Education에서도 "SM-2" 정의
  → canonical owner 확인 필요 → OVERLAP

패턴 4: Authority Chain 위반
  SOT 2에서 DESIGN 레벨 값 재정의 → Authority Chain 위반 → OVERRIDE
```

### 저장 위치
- `D:/VAMOS/docs/sot 2/_cross-ref/sot2_conflict_scan.json`
- 기존 v13_results 경로와 **별도** 관리
