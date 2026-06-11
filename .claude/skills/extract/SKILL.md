---
name: extract
description: SOT 파일에서 EA JSON 자동 추출. C1~C8 카테고리 분류, 표준 키 56개 매핑, source_file_hash 계산 포함. Phase 재실행 시 반복 추출 자동화.
---

# VAMOS EA 추출 스킬

> `/extract [SOT파일경로|EA번호|all]` — SOT 파일에서 EA JSON 자동 추출

## 목적

SOT 원본 파일을 읽어 구조화된 EA(Extraction Agent) JSON을 생성합니다.
Phase 0-A에서 15개 EA를 수동 프롬프트로 추출했던 작업을 자동화합니다.

---

## 선행 조건

1. `/sot-cache`가 최신 상태인지 확인 (가능한 경우)
2. 추출 대상 SOT 파일이 `D:/VAMOS/docs/sot/`에 존재

---

## 추출 규칙

### 카테고리 분류 (C1~C8)

| 코드 | 카테고리 | 탐지 패턴 |
|------|---------|----------|
| C1 | 수치 (Numeric) | 숫자, "N개", "N건", "N%" |
| C2 | 카운트 (Count) | "총 N개", 목록 길이 |
| C3 | 목록 (List) | 열거형, 불릿 리스트 |
| C4 | 상태/단계 (State) | S0~S8, Phase, Stage |
| C5 | 설정값 (Config) | key=value, TOML, JSON |
| C6 | 제약조건 (Constraint) | "반드시", "필수", "금지" |
| C7 | 잠금값 (Lock) | LOCK, FREEZE, ABSOLUTE, NEVER_AUTO |
| C8 | 참조 (Reference) | "§", "참조", 문서 ID |

### 표준 키 매핑

`D:/VAMOS/04. 구현단계/v13/prompts/phase0_A_extraction_prompt.md`의
56개 표준 키 목록을 참조하여 매핑합니다.

### JSON 스키마 필수 필드

```json
{
  "metadata": {
    "ea_id": "EA-XX",
    "source_files": ["파일명"],
    "source_file_hashes": {"파일명": "SHA-256"},
    "total_items_extracted": 0,
    "categories": {"C1": 0, "C2": 0, ...},
    "extraction_version": "v13"
  },
  "items": [
    {
      "item_id": 1,
      "source_file": "파일명",
      "source_line": 123,
      "source_text": "원문 그대로",
      "key": "STANDARD_KEY_NAME",
      "value": "추출된 값",
      "value_type": "number|string|list|boolean",
      "category": "C1",
      "context": "맥락 설명",
      "confidence": 0.95
    }
  ]
}
```

---

## 실행 절차

```
1. $ARGUMENTS 파싱 → 대상 SOT 파일 결정
   ↓
2. /sot-cache 최신 여부 확인 (캐시 있으면 참조 레이어로 활용)
   ↓
3. SOT 파일 전체 읽기 (2000줄 초과 시 분할 읽기)
   ↓
4. C1~C8 패턴 탐지 + 표준 키 매핑
   ↓
5. source_file_hash (SHA-256) 계산
   python -c "import hashlib; print(hashlib.sha256(open('파일경로','rb').read()).hexdigest())"
   ↓
6. metadata.categories 합계 검증 (= total_items_extracted = items 길이)
   ↓
7. EA JSON 저장 (Write tool 사용 → Hook이 자동으로 DV 검증)
   ↓
8. DV 검증 PASS 확인 → FAIL 시 오류 수정 후 재저장
```

---

## $ARGUMENTS 처리

- `$ARGUMENTS`가 SOT 파일 경로 → 해당 파일에서 추출
- `$ARGUMENTS`가 `EA-01` 등 EA 번호 → v13 EA 번호에 해당하는 SOT 파일 그룹 추출
- `$ARGUMENTS`가 `all` → 전체 68개 SOT 파일에서 15개 EA 추출 (Agent tool로 병렬)
- `$ARGUMENTS` 비어있음 → 가장 최근 수정된 SOT 파일 1개 추출

## 출력

**저장 위치**: `D:/VAMOS/04. 구현단계/v13_results/phase0/extraction/v13_EA{번호}_{파일그룹}.json`

## 주의사항

- SOT 파일은 반드시 **전체** 읽기 (2000줄 초과 시 offset으로 분할)
- source_text는 원문 **그대로** 복사 (의역/요약 금지)
- source_line은 Read tool의 행 번호 기준
- confidence < 0.7인 항목은 `[LOW_CONF]` 태그 부착
- 파일 후반부(70% 이후) 추출률이 30% 미만이면 WARNING

---

## [SOT 2 확장] SOT 2 명세 구조화 추출 (v2 추가)

> 기존 SOT 원본 EA 추출 기능을 유지한 채, SOT 2 상세명세에서 구현 항목을 구조화 추출하는 확장입니다.

### SOT 2 추출 카테고리 (SC1~SC8, 기존 C1~C8과 별도)

| 코드 | 카테고리 | 탐지 패턴 |
|------|---------|----------|
| SC1 | 스키마 (Schema) | Pydantic/TypeScript 모델, JSON 스키마 |
| SC2 | 알고리즘 (Algorithm) | "Phase 1:", "Step N:", 파이프라인 |
| SC3 | LOCK 값 (Lock) | "LOCK", 숫자+단위+임계값 |
| SC4 | 상태 머신 (StateMachine) | "→", "IDLE", "ACTIVE", 상태 전이 |
| SC5 | API/인터페이스 (Interface) | "async def", "class", "endpoint" |
| SC6 | 의존성 (Dependency) | "의존", "requires", 모듈 참조 |
| SC7 | 매핑 (Mapping) | "→", 테이블, 코드→동작 |
| SC8 | 기술스택 (TechStack) | 라이브러리명, 버전, "V1/V2/V3" |

### 추가 명령어

- `/extract sot2 {상세명세파일}` → SOT 2 상세명세에서 SC1~SC8 추출
- `/extract sot2-all` → SOT 2 전체 18개 상세명세 일괄 추출
- `/extract sot2-schema {도메인}` → 특정 도메인 스키마만 추출
- `/extract sot2-locks` → SOT 2 전체 LOCK 값 추출

### SOT 2 추출 JSON 스키마

```json
{
  "source_file": "sot 2/3-2_Multimodal-Processing/MULTIMODAL_상세명세.md",
  "domain": "3-2_Multimodal-Processing",
  "extraction_date": "2026-03-22",
  "items": [
    {
      "item_id": "SC1-001",
      "category": "SC1_Schema",
      "key": "MultimodalRequest",
      "value": {
        "modalities": "list[ModalityInput]",
        "task": "str",
        "fusion_strategy": "Literal['early','late','hybrid']"
      },
      "source_line": 45,
      "source_text": "class MultimodalRequest:",
      "confidence": 0.95,
      "part2_reference": "V1-Phase 3 L2147"
    }
  ],
  "metadata": {
    "total_items": 0,
    "by_category": {"SC1": 0, "SC2": 0, "SC3": 0, "SC4": 0, "SC5": 0, "SC6": 0, "SC7": 0, "SC8": 0}
  }
}
```

### 저장 위치
- `D:/VAMOS/docs/sot 2/_extractions/{도메인}_extraction.json`
- 기존 v13_results EA와 **별도** 경로