# v9-F: 외부 의존성 실현성 검증 프롬프트

> **v13 Phase 4 재실행 — 세션 24 프롬프트 갱신**
> 원본: `v9_results/phase0/v9_prompt_F_feasibility.md`
> 변경 사항: GT 경로를 `phase4_v9/gt/`로 갱신, v13 강화 스킬 참조 추가
> 재실행일: 2026-03-22

> **Pipeline**: VAMOS v9.0.0 (v13 Phase 4 재실행)
> **관점 ID**: v9-F (External Dependency Feasibility)
> **작성일**: 2026-03-07 (원본) / 2026-03-22 (갱신)
> **대상 문서**: `VAMOS_구현가이드_PART2_구현단계.md` v20.4.0 (3,807줄)

---

## v13 강화 스킬 참조

Wave 실행 시 아래 v13 스킬을 활용하여 실현성 검증을 수행할 것:

| 스킬 | 용도 | 적용 체크 항목 |
|------|------|---------------|
| `/giskard-scan` | 외부 의존성의 취약점/호환성 자동 스캔 | F-1~F-3 (실재/버전/호환성), GT-5 연동 |
| `/prompt-test` | 검증 프롬프트의 자기 일관성 테스트 | F-4~F-7 (V 범위/라이선스/위치/§6.8 검증) |

---

## [1] HEADER

```
v9 SCOPE HEADER — Phase -1I 산출물
> v9 SCOPE: 문서 정합성/완전성/구현 가능성/수량 일관성/경로 정합성/의존성 순서/외부 의존성
> BOUNDARY: §7.5 중 "문서 검증 가능" 태그 항목만 범위 내
> OUT OF SCOPE: 코드 동작 검증, 성능 벤치마크, 보안 침투 테스트, 런타임 행위
> RULE-14: §7.5 "구현 후 검증" 항목 검출 시 → OUT_OF_SCOPE (FN 아님)
```

**관점**: v9-F — 외부 의존성 실현성 (External Dependency Feasibility)
**핵심 질문**: 지정된 라이브러리/도구가 실제로 존재하고 호환되며, 비용 범위 내인가?
**검출 대상**: 미존재 라이브러리, 버전 비호환, 라이선스 충돌, V버전 범위 오류

---

## [2] SCOPE — 검증 대상 범위

**포함 범위**:
- §2 V0 (line 59~1375): V0 기술 스택 (Python, Rust, Node 의존성)
- §3 V1 (line 1377~1711): V1 추가 의존성
- §4 V2 (line 1713~2099): V2 추가 의존성 (qdrant-client, neo4j 등)
- §5 V3 (line 2101~2697): V3 추가 의존성 (vllm, prometheus-client 등)
- §6.8 AI Investing (line ~3049): 전용 라이브러리 (yfinance, vectorbt 등)
- §6.10 Cloud Library: 크롤러/인프라 라이브러리
- SOT 참조: PHASE_B3 (의존성 정본)

**제외 범위**:
- 변경 이력 (line 3777~3807)
- 인프라 서비스의 실제 가용성 검증 (Docker, K8s 등은 문서 내 명세만 확인)

---

## [3] GT REFERENCE — 참조 Ground Truth

| GT | 파일 경로 | 용도 |
|----|----------|------|
| **GT-4** | `D:\VAMOS\04. 구현단계\v13_results\phase4_v9\gt\v9_dependency_registry.json` | 94개 라이브러리 + 14개 §6.8 전용 + 8개 인프라 서비스 |

**GT-4 핵심 구조**:
- `npm`: dependencies(14) + devDependencies(15) = 29개
- `cargo`: dependencies(14) + build(1) + dev(2) = 17개
- `python`: core~dev 그룹 = 48개
- `section6_ai_investing`: 14개 (§6.8 전용)
- `infra_services`: 8개
- 각 항목: `name`, `version_spec`, `v_scope`, `lock`, `license`, `purpose`, `phase_b3_listed`
- `v_scope` 값: `V0_ALL`, `V1_ALL`, `V1_ONLY`, `V2_PLUS`, `V3_ONLY` 등

**추가 참조**:
- `D:\VAMOS\04. 구현단계\v13_results\phase4_v9\phase-1\v9_allowlist.json` — XREF/NOTE 참조

---

## [4] RULES — 적용 방어 규칙

| RULE | 규칙 요약 | 적용 이유 |
|------|----------|----------|
| **RULE-2** | V0/V1/V2/V3 범위 한정자 먼저 확인 | V1-ONLY 라이브러리를 V2에서 사용하면 범위 오류 |
| **RULE-6** | 코드 주석 내 기술명은 참고/예고 분류 | 주석 내 라이브러리명을 현재 사용으로 오인 방지 |
| **RULE-10** | 버전 범위 표기(`>=x,<y`) 기준 판정. 범위 내 최소 1개 버전 존재 시 PASS | 단일 버전 미존재도 범위 내 존재면 정상 |
| **RULE-11** | §6 포함 필수 | §6.8 AI Investing 전용 라이브러리 검증 |
| **RULE-14** | v9 범위 = 문서 정합성 | 실제 설치/런타임 동작 검증 제외 |

---

## [5] ALLOWLIST — 허용 목록

| 항목 | 허용 사유 |
|------|----------|
| vectorbt 조건부 ADOPT | FIX-05에서 정정 완료. 조건부 채택 (백테스팅 전용) |
| langchain-community | PHASE_B3 기준 Ollama 래퍼(ChatOllama) 필수 |
| FlagEmbedding (bge-m3) | BAAI 공식 라이브러리. L-3 태그로 채택 확정 |

---

## [6] CHECK ITEMS — 구체적 검증 항목

### [F-1] 라이브러리 실재 확인
GT-4의 모든 라이브러리가 실제로 존재하는지 확인 (PyPI/npm/crates.io 기준).

**절차**:
1. GT-4의 npm(29) + cargo(17) + python(48) + §6.8(14) = 108개 항목 순회
2. 각 라이브러리에 대해:
   - npm: npmjs.com에 패키지 존재 여부
   - cargo: crates.io에 패키지 존재 여부
   - python: PyPI에 패키지 존재 여부
   - §6.8: 해당 레지스트리에 존재 여부
3. 미존재 시: `BLOCKER` (구현 불가)
4. 존재 확인: PASS

**주의**: 패키지명 변경(rename) 케이스 확인 (예: `pydantic-settings`는 `pydantic` v2에서 분리)

### [F-2] 버전 범위 유효성 확인
지정된 버전 범위 내에 실제 릴리스가 존재하는지 확인.

**절차**:
1. GT-4에서 `version_spec`이 있는 항목 순회
2. 각 버전 범위(`>=x,<y`, `^x.y.z`, `~x.y`) 내에:
   - 최소 1개의 실제 릴리스 버전이 존재하는가? (RULE-10)
   - 존재하면: PASS
   - 미존재 시: `HIGH` (지정 범위에 릴리스 없음)
3. 버전 범위가 미지정인 항목: 최신 안정 버전 존재 확인

**예시**: `chromadb >=0.5.23,<1.0` — 0.5.23 이상 1.0 미만 릴리스 존재 확인

### [F-3] 상호 호환성 확인
동일 런타임(Python/Node/Rust)의 라이브러리 간 충돌이 없는지 확인.

**절차**:
1. **Python 그룹**: 48개 + §6.8 14개 = 62개 라이브러리
   - 주요 충돌 후보:
     - `pydantic` v2 vs `langchain` 호환성
     - `chromadb` (V1) vs `qdrant-client` (V2) 동시 설치 (V 범위 다르므로 OK)
     - `torch` vs `vllm` 버전 호환
   - 동일 V 범위 내 라이브러리의 의존성 트리 충돌 여부
2. **npm 그룹**: 29개
   - React 18.3 + Zustand + Recharts 호환성
   - @tauri-apps/api 버전과 Tauri Rust 버전 호환
3. **Cargo 그룹**: 17개
   - tauri + serde + tokio 호환성 (일반적으로 호환)
4. 충돌 발견 시: `HIGH`
5. 호환 확인: PASS

### [F-4] V 범위 정확성 검증
V1-ONLY 라이브러리가 V2에서 사용되지 않는지, V2_PLUS가 V0에서 참조되지 않는지 확인.

**절차**:
1. GT-4에서 `v_scope` 별 라이브러리 분류:
   - `V0_ALL`: V0 이상 모든 버전
   - `V1_ALL`: V1 이상 모든 버전
   - `V1_ONLY`: V1에서만 사용 (V2에서 대체됨)
   - `V2_PLUS`: V2 이상
   - `V3_ONLY`: V3에서만 사용
2. PART2에서 각 라이브러리가 언급되는 위치의 V 범위 확인:
   - V1-ONLY 라이브러리가 §4(V2) 또는 §5(V3)에서 사용되면: `HIGH`
   - V2_PLUS 라이브러리가 §2(V0)에서 사용되면: `HIGH`
3. 범위 정확: PASS

**예시**: `chromadb (V1_ONLY)` — V2에서는 `qdrant-client`로 대체. §4에서 chromadb 참조 시 오류

### [F-5] 라이선스 충돌 확인
프로젝트에서 사용하는 라이브러리의 라이선스 간 충돌이 없는지 확인.

**절차**:
1. GT-4에서 `license` 필드 확인
2. 주요 주의 대상:
   - GPL-3.0: `neo4j` (V2+ 사용) — 프로젝트 라이선스와의 호환성
   - AGPL: 존재 시 즉시 플래그
   - 상용 라이선스: 비용 발생 여부
3. GPL-3.0 neo4j의 경우:
   - neo4j Python driver(`neo4j`)는 Apache-2.0
   - neo4j 서버는 Community Edition (GPL-3.0) vs Enterprise (상용)
   - Community Edition 사용이면 제약 확인
4. 라이선스 충돌 발견 시: `MEDIUM` (법적 리스크, 기술적 구현 자체는 가능)
5. 충돌 없음: PASS

### [F-6] PART2 라이브러리 언급 위치 ↔ GT-4 V 범위 일치
PART2에서 라이브러리를 언급하는 위치와 GT-4의 `v_scope`가 일치하는지 확인.

**절차**:
1. GT-4의 `part2_lines` (또는 PART2에서 라이브러리명 grep)
2. 각 언급 위치가 해당 라이브러리의 `v_scope`와 일치하는 섹션에 있는가?
   - V0_ALL 라이브러리가 §2(V0)에서 언급: 정상
   - V2_PLUS 라이브러리가 §2(V0)에서 언급: `HIGH`
   - V1_ONLY 라이브러리가 §6(횡단)에서 언급: V 범위 명시 여부 확인
3. §6 횡단 섹션은 모든 V 범위에 걸칠 수 있으므로:
   - §6에서 V 범위를 명시하고 있으면: PASS
   - V 범위 미명시면: `MEDIUM`

### [F-7] §6.8 AI Investing 전용 라이브러리 실현성
§6.8에서 명시된 전용 라이브러리(yfinance, vectorbt, backtrader, TimescaleDB 등)의 실현성 확인.

**절차**:
1. GT-4의 `section6_ai_investing` 14개 항목 순회
2. 각 항목에 대해:
   - F-1 (실재 확인): PyPI/npm 존재?
   - F-2 (버전 유효성): 명시된 버전 범위에 릴리스 존재?
   - 특수 확인:
     - `vectorbt`: 조건부 ADOPT (FIX-05). Pro 버전 불필요 확인
     - `yfinance`: API 안정성/데이터 제한
     - `TimescaleDB`: PostgreSQL 확장. 별도 설치 필요
     - `backtrader`: 유지보수 상태 (마지막 릴리스 확인)
3. 실현 불가 시: `HIGH`
4. 조건부 실현 (추가 설정 필요): `MEDIUM`
5. 실현 가능: PASS

---

## [7] OUTPUT FORMAT — 결과 JSON 스키마

```json
{
  "perspective": "v9-F",
  "perspective_name": "외부 의존성 실현성",
  "timestamp": "2026-MM-DDTHH:mm:ssZ",
  "target_doc": "VAMOS_구현가이드_PART2_구현단계.md v20.4.0",
  "gt_version": "v9_dependency_registry.json",
  "rules_applied": ["RULE-2", "RULE-6", "RULE-10", "RULE-11", "RULE-14"],

  "summary": {
    "total_libraries": 108,
    "by_ecosystem": {
      "npm": {"total": 29, "pass": 0, "fail": 0},
      "cargo": {"total": 17, "pass": 0, "fail": 0},
      "python": {"total": 48, "pass": 0, "fail": 0},
      "s6_ai_investing": {"total": 14, "pass": 0, "fail": 0}
    },
    "pass": 0,
    "real_error": 0,
    "false_positive": 0,
    "style_concern": 0,
    "out_of_scope": 0,
    "blocker": 0,
    "high": 0,
    "medium": 0,
    "low": 0
  },

  "license_summary": {
    "MIT": 0,
    "Apache-2.0": 0,
    "BSD": 0,
    "GPL-3.0": 0,
    "other": 0,
    "conflicts": []
  },

  "v_scope_violations": [
    {
      "library": "",
      "v_scope": "V1_ONLY | V2_PLUS | ...",
      "found_in_section": "§N",
      "expected_section": "§N"
    }
  ],

  "findings": [
    {
      "id": "F-xxx-nnn",
      "check_item": "F-1 ~ F-7",
      "library": "라이브러리명",
      "ecosystem": "npm | cargo | python",
      "version_spec": ">=x,<y",
      "v_scope": "V0_ALL | V1_ONLY | ...",
      "line": 0,
      "description": "발견 내용 상세 기술",
      "expected": "GT-4 기준",
      "actual": "PART2 / 레지스트리 실제 상태",
      "severity": "BLOCKER | HIGH | MEDIUM | LOW",
      "classification": "REAL_ERROR | FALSE_POSITIVE | STYLE_CONCERN | OUT_OF_SCOPE",
      "rule_applied": "RULE-N (해당 시)"
    }
  ]
}
```

---

## [8] SEVERITY — 판정 기준

| 등급 | 기준 | 이 관점의 예시 |
|------|------|--------------|
| **BLOCKER** | 라이브러리 미존재로 구현 불가 | 가상의 패키지명 `phantom-ml`, 삭제된 패키지 |
| **HIGH** | 버전 비호환 또는 V 범위 오류 | 지정 범위에 릴리스 없음, V1-ONLY를 V2에서 사용 |
| **MEDIUM** | 라이선스 충돌 또는 조건부 실현 | GPL-3.0 충돌, TimescaleDB 별도 설치 필요, §6 V 범위 미명시 |
| **LOW** | 유지보수 상태 우려, 표기 불통일 | backtrader 마지막 릴리스 오래됨, 패키지명 대소문자 차이 |

---

## 실행 지시

1. GT-4 로드 후 108개 라이브러리 목록 확인
2. F-1 (실재 확인)은 웹 검색 또는 레지스트리 API 활용:
   - PyPI: `https://pypi.org/pypi/{name}/json`
   - npm: `https://registry.npmjs.org/{name}`
   - crates.io: `https://crates.io/api/v1/crates/{name}`
3. F-2 (버전 유효성)는 F-1에서 얻은 릴리스 목록으로 판정
4. F-3 (호환성)은 주요 충돌 후보만 집중 검증 (전수 의존성 해석은 범위 외)
5. F-4 (V 범위)는 PART2 grep으로 라이브러리명 출현 위치 확인
6. F-5 (라이선스)는 GT-4의 `license` 필드 기반 + 주의 대상 심화 확인
7. F-6은 F-4와 연동하여 실행
8. F-7 (§6.8 전용)은 별도 집중 검증
9. RULE-10 주의: 범위 내 1개 버전이라도 존재하면 PASS
10. `/giskard-scan` 스킬로 GT-5 연동 외부 의존성 취약점/호환성 자동 스캔 실행
11. `/prompt-test` 스킬로 F-4~F-7 검증 프롬프트의 자기 일관성 사전 테스트 수행
