---
name: sot-cache
description: v6~v13 기존 산출물(JSON/MD/PY)을 SOT 참조 캐시로 활용. SOT 파일을 매번 처음부터 읽는 대신 이미 검증된 구조화 데이터를 참조 레이어로 로딩. 반드시 최신 SOT 반영 산출물만 사용.
---

# VAMOS SOT 캐시 스킬

> `/sot-cache [load|refresh|status|{SOT파일명}]` — 검증된 기존 산출물을 참조 캐시로 활용

## 핵심 원칙

```
AI가 SOT 68개 파일(89,000줄)을 직접 읽을 때 → 컨텍스트 한계로 누락 발생
v6~v13에서 이미 추출/검증된 구조화 산출물이 존재 → 이것을 "캐시"로 활용
단, 최신 SOT가 반영된 산출물만 사용 → 구버전 산출물 사용 금지
```

**절대 규칙**: SOT가 업데이트된 후 해당 산출물이 재생성되지 않았으면 **캐시 무효**

---

## 캐시 계층 (Tier 구조)

### Tier 1: 구조 인덱스 (PART2 기준) — 가장 자주 사용

최신 소스: **v12** (PART2 v26.0.0 기준)

| 캐시 파일 | 경로 | 내용 |
|----------|------|------|
| Section Map | `v12/v12_results/phase4/v12_final_section_map.json` | 274 headings + line numbers (v26.0.0) |
| Numeric Registry | `v12/v12_results/phase0/v12_numeric_registry.json` | 2,579 수치/LOCK/FREEZE 값 |
| Reference Map | `v12/v12_results/phase0/v12_reference_map.json` | 1,896 내부 참조 |
| Prompt Inventory | `v12/v12_results/phase0/v12_prompt_inventory.json` | 18 AI 프롬프트 |
| §6 Mapping | `v12/v12_results/phase0/v12_s6_mapping.json` | 67 §6 참조 해소 |

### Tier 2: 피처 레지스트리 — 전체 기능 목록

| 캐시 파일 | 경로 | 내용 |
|----------|------|------|
| v12 Registry | `v12/v12_results/phase0/v12_feature_registry_final.json` | 2,644 features (v12 최종) |
| v10 Registry | `v10_results/phase0-f/v10_feature_registry_final.json` | 3,940 features (v10 최종) |
| v12 Mapping | `v12/v12_results/phase1/v12_mapping_M01~M06.json` | Feature→PART2 매핑 |

### Tier 3: SOT 내부 정합성 — v13 추출 결과

| 캐시 파일 | 경로 | 내용 |
|----------|------|------|
| EA JSON 15개 | `v13_results/phase0/extraction/v13_EA*.json` | SOT 68파일 전수 추출 |
| CM JSON 8개 | `v13_results/phase0/cross_match/v13_CM*.json` | C1~C8 교차매칭 |
| 불일치 목록 | `v13_results/phase0/v13_sot_inconsistency_list.json` | 31개 불일치 |
| Delta | `v13_results/phase0/v13_sot_delta.json` | 20개 수정사항 |

### Tier 4: 검증 Ground Truth — v8/v9 구조적 사실

| 캐시 파일 | 경로 | 내용 |
|----------|------|------|
| LOCK 추출 | `v8_results/phase0/0-D.json` | 80 LOCK/FREEZE/ABSOLUTE 항목 |
| 모듈 의존성 | `v8_results/phase0/IMP-A.json` | 17 노드 의존성 그래프 |
| 스키마 검증 | `v8_results/phase0/IMP-B.json` | 24 Pydantic 모델 |
| API 엔드포인트 | `v8_results/phase0/IMP-C.json` | 13 IPC + 72 SRC 엔드포인트 |
| Config 섹션 | `v8_results/phase0/IMP-D.json` | 13 TOML 섹션 |
| 파일경로 GT | `v9_results/phase0/gt1_file_path_registry.json` | 111 정규화 경로 |
| 산출물체인 GT | `v9_results/phase0/gt2_artifact_chain.json` | 18 Stage + Go/No-Go |
| 수량 GT | `v9_results/phase0/gt3_quantity_index.json` | 248 수량 항목 |
| 의존성 GT | `v9_results/phase0/v9_dependency_registry.json` | 94 외부 의존성 |
| 구현가능성 GT | `v9_results/phase0/v9_implementability_checklist.json` | 구현 체크리스트 |

### Tier 5: PART2 용어/구조 — v11 인덱스

| 캐시 파일 | 경로 | 내용 |
|----------|------|------|
| Terminology | `v11_results/phase0/v11_terminology_dict.json` | 200+ 정규 용어 |
| Codeblock | `v11_results/phase0/v11_codeblock_inventory.json` | 100+ 코드블록 |
| v6~v10 재사용 | `v11_results/phase0/v11_v6v10_reuse_index.json` | 버전간 재사용 매핑 |

### Tier 6: 검증 스크립트 — 재실행 가능

| 캐시 파일 | 경로 | 내용 |
|----------|------|------|
| v8 Part1 검증 | `v8_results/phase0/phase0_part1.py` | 0-A~0-H 검증 로직 |
| v8 Part2 검증 | `v8_results/phase0/phase0_part2.py` | IMP-A~IMP-F 검증 로직 |
| v9 검증 프롬프트 | `v9_results/phase0/v9_prompt_A~F.md` | 6개 관점 검증 프롬프트 |
| v11 레지스트리 빌더 | `v11_results/phase0/build_registry.py` | 레지스트리 구축 |
| v11 참조 파서 | `v11_results/phase0/parse_references.py` | 참조 추출 |
| v11 코드블록 파서 | `v11_results/phase0/parse_codeblocks.py` | 코드블록 추출 |

---

## 실행 모드

### `/sot-cache status` — 캐시 유효성 전체 확인

```
1. 각 Tier의 캐시 파일 존재 여부 확인
   ↓
2. /integrity 연동: SOT hash 변경 여부 확인
   ↓
3. 캐시 유효성 판정:
   - VALID: SOT 미변경, 캐시 최신
   - STALE: SOT 변경됨, 캐시 재생성 필요
   - MISSING: 캐시 파일 미존재
   ↓
4. 유효성 테이블 출력:

   | Tier | 캐시 | 상태 | SOT 변경일 | 캐시 생성일 |
   |------|------|------|-----------|-----------|
   | T1   | Section Map | VALID | 3/17 | 3/18 |
   | T1   | Numeric Registry | STALE | 3/18 | 3/16 |
   ...
```

### `/sot-cache load` — 유효한 캐시 로딩

```
1. status 실행 → VALID인 캐시만 선별
   ↓
2. 사용 용도별 캐시 조합 결정:
   - EA 추출 시: Tier 1 + Tier 2 + Tier 5
   - CM 교차매칭 시: Tier 3
   - Phase 재실행 시: Tier 1 + Tier 4
   - SOT 읽기 보조: Tier 1 + Tier 3 + Tier 5
   ↓
3. 핵심 캐시 내용을 컨텍스트에 요약 로딩:
   - Section Map: 주요 섹션 구조 (§1~§7)
   - Numeric Registry: LOCK/FREEZE 값 (변경 불가 항목)
   - Terminology: 정규 용어 ↔ 변형 매핑
   ↓
4. "이 캐시를 참조하면서 SOT를 읽으세요" 안내
```

### `/sot-cache refresh` — STALE 캐시 재생성

```
1. STALE 상태인 캐시 목록 확인
   ↓
2. 각 캐시 유형에 따라 재생성 방법 결정:
   - Section Map: v11 parse_references.py 재실행
   - Numeric Registry: v11 build_registry.py 재실행
   - Feature Registry: /extract all 재실행
   - EA/CM: /extract + /cross-match 재실행
   ↓
3. 재생성 실행 (사용자 확인 후)
   ↓
4. 새 hash 기록 → 캐시 상태 VALID로 갱신
```

### `/sot-cache {SOT파일명}` — 특정 SOT 파일의 캐시 조회

```
1. 해당 SOT 파일과 관련된 모든 캐시 수집:
   - 어떤 EA에서 추출했는지
   - 어떤 CM에서 비교했는지
   - Feature Registry에서 몇 개 feature가 매핑되었는지
   - 어떤 수치/LOCK/참조가 추출되었는지
   ↓
2. 캐시 유효성 확인 (hash 비교)
   ↓
3. 유효한 캐시 내용 요약 출력
```

---

## 다른 스킬과의 연동

```
/extract    → 추출 전 /sot-cache load로 캐시 참조 레이어 활성화
/cross-match → 비교 시 Tier 3 캐시로 이전 결과 참조
/phase-run  → Phase 실행 전 /sot-cache status로 유효성 확인
/integrity  → SOT 변경 감지 → /sot-cache status에 STALE 반영
/audit      → 감사 시 Tier 4 Ground Truth 참조
/validate   → 검증 시 Tier 1 인덱스로 SOT 구조 참조
```

---

## 캐시 사용 시 핵심 규칙

```
규칙 1: 캐시는 "참조"이지 "대체"가 아님
  → 캐시에 있는 내용이라도 의심되면 SOT 원본에서 직접 확인

규칙 2: STALE 캐시는 절대 사용 금지
  → SOT가 업데이트되면 해당 캐시는 반드시 refresh 후 사용

규칙 3: 캐시 간 충돌 시 최신 버전 우선
  → v12 > v11 > v10 > v9 > v8 순서로 우선

규칙 4: 새로운 내용은 캐시에 없음
  → 캐시는 "기존에 추출된 것"만 포함
  → delta 적용 후 추가된 내용은 SOT 원본에서 직접 읽기

규칙 5: 캐시 자체도 AI가 생성한 것 — 오류 가능
  → 캐시를 맹신하지 않고 교차 검증 (Tier 간 비교)
```

## 출력

**캐시 상태 파일**: `v13_results/cache/v13_cache_status.json`

```json
{
  "check_timestamp": "2026-03-18T...",
  "tiers": {
    "T1": {"total": 5, "valid": 4, "stale": 1, "missing": 0},
    "T2": {"total": 3, "valid": 3, "stale": 0, "missing": 0},
    ...
  },
  "details": [
    {
      "tier": "T1",
      "name": "Section Map",
      "path": "v12/v12_results/phase4/v12_final_section_map.json",
      "status": "VALID",
      "sot_hash_match": true,
      "cache_date": "2026-03-17",
      "sot_modified": "2026-03-17"
    }
  ]
}
```

---

## [SOT 2 확장] SOT 2 참조 캐시 (v2 추가)

> 기존 SOT 68파일 + Part2 캐시를 유지한 채, SOT 2 파일 세트를 추가 캐시 레이어로 등록합니다.

### Tier 4: SOT 2 구조 인덱스 (신규)

| 캐시 파일 | 경로 | 내용 |
|----------|------|------|
| SOT 2 Master Index | `docs/sot 2/SOT2_MASTER_INDEX.md` | 5 Tier / 19 대분류 / 107건 + COND 106개 |
| 도메인별 상세명세 | `docs/sot 2/*/*.md` | ~18개 상세명세 (총 ~10,000줄) |
| 방식 C 요약 | `docs/sot 2/_method-c-summaries/*.md` | Part2 FULL 7개 영역 요약 |
| 계획서 | `docs/sot 2/*/*_구조화_종합계획서.md` | 도메인별 실행 계획 |
| COND 종합명세 | `docs/sot 2/2-2_COND-Modules-Detail/COND_MODULES_종합명세.md` | 106개 모듈 카탈로그 |

### 추가 명령어

- `/sot-cache sot2` → SOT 2 전체 캐시 로딩
- `/sot-cache sot2-refresh` → SOT 2 캐시 갱신 (파일 변경 감지)
- `/sot-cache sot2-status` → SOT 2 캐시 상태 + 파일별 해시

### 캐시 무효화 규칙 (SOT 2 전용)

```
SOT 2 파일 수정 → 해당 파일 캐시 무효
Part2 정본 수정 → 방식 C 요약 캐시 무효 (sot2-method-c 재실행 필요)
계획서 Phase 전환 → 해당 도메인 캐시 갱신
```

### 로딩 우선순위

```
기존: Tier 1 (Part2 섹션맵) > Tier 2 (Feature Registry) > Tier 3 (Consistency)
추가: Tier 4 (SOT 2 인덱스) — 기존 Tier와 병렬 로딩 가능
```
