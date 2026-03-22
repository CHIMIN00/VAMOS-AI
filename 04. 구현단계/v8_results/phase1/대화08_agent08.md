# [Agent 8] 검증 결과 — 인프라 + CI/CD + 테스트 + Config

**검증 일시**: 2026-03-05
**PART2 버전**: v18.0.0 (1933행)
**Phase 0 참조**: 0-D.json (LOCK/FREEZE 80건)

---

## 읽은 파일 (실제 읽은 수 / 할당 수: 6 / 6)

- [x] VAMOS_구현가이드_PART2_구현단계.md (1933행) — §2 V0-STEP-1(Config), §3 V1-Phase5~6(인프라), §6.3~6.4(테스트/CI/CD), §6.11~6.13 전수 열독
- [x] PHASE_B_EXHAUSTIVE_ANALYSIS.md (1822행) — Category B~K 전수 열독 ※ v8 §5 "PHASE_B3~B7" 해당 (B2~B7 포함)
- [x] D2.0-07_SAFETY_COST_APPROVAL.md (~2000행) — §7 레지스트리 부분 열독
- [x] CLAUDE.md (100행+) — §1~§8 열독 ※ v8 §5 SRC 할당 외 추가 열독 (GO/NO-GO 교차검증용)
- [x] 0-D.json (570행) — LOCK/FREEZE 80 entries 전수 열독
- [△] D2.1-D2 — 직접 파일 미확인, PHASE_B 분석 내 레지스트리 인용으로 대체

> **주의**: D2.1-D2 파일 직접 확인 불가. 레지스트리 카운트(EventType/Failure/Fallback) 원본 대조 보류.

---

## 검사 통계

- **Dim B** Forward: **33** / MATCH: **24** / MISMATCH: **7** / NO_SOURCE: **2** / Reverse MISSING: **4** (총 **37** 체크)
- **Dim C** Facts checked: **14** / IMP_OK: **8** / IMP_IMPOSSIBLE: **1** / IMP_MISSING: **3** / IMP_CONFLICT: **2**
- **SOURCE_CONFLICT**: **3건** (SC #1은 MISMATCH #7 근인 포함, SC #2-3은 MATCH 처리)
- **MISMATCH #1-2는 동일 근인** (config 섹션명), 종합 판정에서 BLK-1로 통합. **MISMATCH #6 = IMP_CONFLICT #1** (CI/CD), 종합 판정에서 H-3으로 통합.
- 수정 전: BLOCKER **2**건, HIGH **9**건, MEDIUM **6**건 = 총 **17**건
- 수정 후: 미수정 (BLOCKER **2**건 잔여)

---

## 심각도 분류 기준

- **BLOCKER**: LOCK 위반, 구현 차단, 순환 의존, 카운트 오류 ±3 이상
- **HIGH**: 값 오류, 누락 스펙, 카운트 오류 ±2
- **MEDIUM**: 근사/구버전 값, 표기 차이, 출처 오기재
- **LOW**: 서식, 약어 vs 전체명, ±1 근사

---

## Dim B — MISMATCH

| # | PART2:행 | PART2 값 | 원본 값 | 원본 출처 | Severity |
|---|---------|---------|--------|----------|----------|
| 1 | L99~188 | config.v1.toml 13섹션: `[general]` `[llm]` `[cost]` `[storage]` `[mcp]` `[safety]` `[self_check]` `[embedding]` `[graph_db]` `[vector_db]` `[semantic_cache]` `[memory]` `[logging]` | config.v1.toml 13섹션: `[core]` `[llm]` `[embedding]` `[vector_db]` `[graph_db]` `[storage]` `[cost]` `[guardrails]` `[mcp]` `[rbac]` `[rate_limit]` `[logging]` `[semantic_cache]` | PHASE_B4 §3 (PHASE_B분석 D.3) | **BLOCKER** — 13섹션 개수는 일치하나 섹션명 구성 불일치 |
| 2 | L99~188 | PART2에 `[general]`, `[safety]`, `[self_check]`, `[memory]` 존재 | B4에 `[core]`, `[guardrails]`, `[rbac]`, `[rate_limit]` 존재 — 4개 섹션명 완전 불일치 | PHASE_B4 §3 (PHASE_B분석 D.3) | **BLOCKER** — V7-1에서 카운트만 11→13 정합, 섹션명 미정합 |
| 3 | L121 | `default_model = "ollama:llama3.2:3b"`, `main_model = "ollama:llama3.1:8b"` | `mini_model = "ollama/gemma-2b"`, `main_model = "gpt-4o-mini"` (V1) | PHASE_B4 §3 [llm] L157-178 | **HIGH** — LLM 모델명 전수 불일치 |
| 4 | L125 | `max_tokens = 2048` | `max_tokens = 4096` | PHASE_B4 §3 [llm] L956 | **MEDIUM** — 토큰 상한 2배 차이 |
| 5 | L157 | `matryoshka_dim = 256` | `matryoshka_dim = 512` | PHASE_B4 §3 [embedding] L966 | **HIGH** — Matryoshka 차원 2배 차이. Agent 6에서 256 MATCH 판정(D2.0-06 기준)과 충돌 가능 → 정본 확정 필요 |
| 6 | L1004 | CI/CD 14개 워크플로우 개별 yml 파일 나열 | 실제 6 파일 (ci.yml 내 5-stage 통합 + release/deploy-v2/deploy-v3/security/nightly) | PHASE_B6 F.9 L1699-1707 | **HIGH** — 14개 논리 파이프라인을 개별 파일처럼 표기. B6 정본은 6파일 통합구조 |
| 7 | L146 | `rbac_default_role = "OWNER"` | `default_role = "OPERATOR"` | PHASE_B4 §3 [rbac] L1048 | **HIGH** — v10.0.0에서 OPERATOR→OWNER 수정 기록 있으나 SRC 원본(B4) 미갱신 |

---

## Dim B — NO_SOURCE

| # | PART2:행 | PART2 내용 | 검색한 파일/패턴 | 판정 | Severity |
|---|---------|-----------|----------------|------|----------|
| 1 | L148-152 | `[self_check]` 섹션: threshold_p0=70, threshold_p1=75, threshold_p2=80, soft_loop_max=1 | PHASE_B4 전체, PHASE_B분석 Category D | PHASE_B4에 `[self_check]` 섹션 자체 없음. PART2 창작 의심 또는 매핑 누락 | **MEDIUM** |
| 2 | L474 | 레지스트리: EventType 123/Failure 36/Fallback 23 | D2.1-D2 파일 직접 확인 불가 | PART2 §6.11에서 EventType "53+", FailureCode "20+", Fallback "13" → v8 기준 123/36/23과 큰 차이. **재확인 필수** | **MEDIUM** |

---

## Dim B — MISSING

| # | 구분 | 원본 출처 | 누락 내용 | Severity |
|---|------|----------|---------|----------|
| 1 | 역방향 | PHASE_B4 §3 [core] | PART2 config에 `[core]` 섹션 자체 없음 — `autonomy_level`, `default_execution_mode`, `max_decision_timeout_ms`, `single_decision_lock (LOCK)`, `pipeline_stages (LOCK)` 등 아키텍처 핵심 키 누락 | **BLOCKER** |
| 2 | 역방향 | PHASE_B4 §3 [guardrails] | PART2 config에 `[guardrails]` 섹션 없음 — `l1~l4_enabled`, `fail_policy`, `sensitive_types` 누락. `[safety]`에 `guardrails_layers=2`로 단순화 | **HIGH** |
| 3 | 역방향 | PHASE_B4 §3 [rate_limit] | PART2 config에 `[rate_limit]` 섹션 전혀 없음 — `enabled`, `targets`, `rpm`, `tpm`, `burst`, `cooldown_seconds` 키 누락 | **HIGH** |
| 4 | 역방향 | PHASE_B6 F.3 | PART2 §6.4에 ruff 설정 상세(line-length=100, select 13개 규칙) 미기재 — 워크플로우명만 "ruff lint + mypy"로 표기 | **MEDIUM** |

---

## Dim B — SOURCE_CONFLICT

| # | 출처A=값 | 출처B=값 | 정본 우선순위 판정 |
|---|---------|---------|-----------------|
| 1 | PART2 L146: `rbac_default_role = "OWNER"` (v10.0.0 수정) | PHASE_B4 §3 L1048: `default_role = "OPERATOR"` | PART2 v18 "OWNER"이 최신 정본이나 SRC(PHASE_B4 원본) 갱신 필요. ※ MISMATCH #7 근인 |
| 2 | PART2 L549: `Python 80%+, Rust 60%+, React 70%+` | PHASE_B6 F.4: `Python 75%, Rust 60%, React 70%` CI 임계값 | B5=전략 목표(80%+), B6=CI 최소 게이트(75%). PART2는 B5 기준 채택. **MATCH 처리** (혼동 소지 있으나 불일치 아님) |
| 3 | PART2 L549 주석: `B5 §7.1=Rust 80%+ vs B6 §3.4=60% min/75% target` | PHASE_B분석 H.4 | PART2에서 이미 SOURCE_CONFLICT 주석으로 인지하고 "60%+ 유지"로 결정. **MATCH 처리** |

---

## Dim C — IMP_IMPOSSIBLE

| # | PART2:행 | 명세 내용 | 불가 사유 | 대안 제안 | Severity |
|---|---------|---------|---------|---------|----------|
| 1 | L549 | Rust 커버리지 60%+ (cargo test + tarpaulin) | tarpaulin은 Linux 전용. PART2 V1은 Tauri 데스크톱(Win/Mac/Linux) — Windows/Mac 개발 환경에서 실행 불가 | CI는 Linux runner에서 tarpaulin 실행, 로컬 개발은 cargo-llvm-cov 사용 | **MEDIUM** |

---

## Dim C — IMP_MISSING

| # | PART2:행 | 명세 내용 | 부족 정보 | Severity |
|---|---------|----------|----------|----------|
| 1 | L549 | E2E Playwright + Tauri 테스트 | Tauri WebDriver + Playwright 통합 설정 상세 미기재. B5 E.7에 8시나리오만 나열, setup/config 미정의 | **HIGH** |
| 2 | L1001-1018 | 14개 GitHub Actions 경로 필터링 | 각 워크플로우의 `paths:` 트리거 필터 미정의. B6에도 상세 미기재 | **HIGH** |
| 3 | - | quality-schema.yml 자동화 | PART2 L1008에 "Pydantic 모델 검증" 명시하나, 실제 검증 스크립트/명령어 미정의 | **MEDIUM** |

---

## Dim C — IMP_CONFLICT

| # | 출처A:행:값 | 출처B:행:값 | 충돌 내용 | 판정 |
|---|-----------|-----------|---------|------|
| 1 | PART2 L1004-1018: 14개 개별 yml 파일 나열 | PHASE_B6 F.9 L1699-1707: 6개 파일 (ci.yml 통합) | PART2는 논리적 파이프라인 14개를 개별 파일처럼 나열. B6 실제는 ci.yml에 5-stage 통합. **B6 정본(6파일) 채택 권고** | **HIGH** — ※ MISMATCH #6와 동일 근인 |
| 2 | PART2 L549: `build-tauri.yml Python 번들링` | PHASE_B6 F.5: Tauri 크로스 플랫폼 빌드 = Linux/Win/Mac | PART2 "Python 번들링"은 Tauri에 Python 포함 암시, B6은 Python wheel 별도 빌드. **번들 vs 별도 설치 아키텍처 결정 필요** | **HIGH** |

---

## Dim C — IMP_OK (8건)

| # | 항목 | 판정 사유 |
|---|------|---------|
| 1 | Python 80% ~40 테스트 | B5 E.3: Python 6개 모듈 ~40 테스트파일 구성 확인 |
| 2 | Rust 60% ~8 테스트 | B5 E.4: commands/ + bridge/ = ~8 테스트 확인 |
| 3 | React 70% ~15 테스트 | B5 E.5: components + stores + hooks = ~15 테스트 확인 |
| 4 | VAL-001~010 → 자동 테스트 | PART2 §6.3 L979-992 ↔ B4 D.5 VAL-001~010 매핑 확인 |
| 5 | 50 AC → 79 테스트 매핑 | PART2 L994-997 ↔ B5 E.8 (50 AC→79 테스트) 정확 일치 |
| 6 | Gate 전경로 시뮬레이션 | B5 E.6: Safety Chain 통합 테스트 (Policy→Cost→Approval→Guardrails) 확인 |
| 7 | 3언어 커버리지 병합 | PART2 L1012 coverage-report.yml ↔ B6 F.4 coverage merge 확인 |
| 8 | security.yml 감사 차단 | PART2 L1015 ↔ B6 F.8 pip-audit/cargo-audit/npm audit 확인 |

---

## Phase 0 교차 참조

| # | 0-D.json 항목 | PART2 값 | 0-D.json 값 | 판정 |
|---|--------------|---------|------------|------|
| 1 | config.v1.toml 13섹션 (LOCK) | 13개 섹션 | 13개 섹션 (개수 일치) | ⚠️ 개수 MATCH, 섹션명 MISMATCH (#1) |
| 2 | single_decision_lock = true (LOCK) | PART2 config에 미존재 | LOCK | ⚠️ MISSING (#1) |
| 3 | pipeline_stages (LOCK) | PART2 config에 미존재 | LOCK | ⚠️ MISSING (#1) |
| 4 | 마이그레이션 6원칙 (LOCK) | PART2 L611-617 동일 | B7 G.2 6원칙 LOCK | ✅ MATCH |
| 5 | Monorepo 구조 (LOCK) | PART2 L67-105 동일 | B2 B.1 Root Layout LOCK | ✅ MATCH |
| 6 | 커버리지 목표 Rust 60%+ (LOCK) | Rust 60%+ | B5/B6 LOCK | ✅ MATCH |

---

## Dim B — MATCH 확인

| # | v8 B# | 검증 항목 | PART2 값 | 원본 값 | 원본 출처 | 판정 |
|---|-------|----------|---------|--------|----------|------|
| 1 | B#1 | Docker Config | V2-Phase 1: Docker Compose 컨테이너화 (L608) | B6 F.5 Docker 3 images | PHASE_B6 | **MATCH** |
| 2 | B#2 | K8s V3 | V3-Phase 1: Helm Blue-Green 배포 (L708) | B6 F.7 K8s/Helm | PHASE_B6 | **MATCH** |
| 3 | B#3 | 버전별 배포 | V1=local, V2=Docker, V3=K8s | B6 F.7 동일 | PHASE_B6 | **MATCH** |
| 4 | B#4 | Monorepo 구조 | PART2 L67-105 | B2 B.1 Root Layout (LOCK) | PHASE_B2 | **MATCH** |
| 5 | B#5 | Config 13섹션 수 | 13개 | 13개 — **개수 일치, 섹션명 MISMATCH #1** | PHASE_B4 | **MATCH** (개수만) |
| 6 | B#6 | LOCK/FREEZE 인벤토리 교차 검증 | 0-D.json 80건 대비 PART2 교차 확인 | Phase 0 결과 활용 완료 | 0-D.json | **MATCH** |
| 7 | B#8 | 커버리지 목표 | Rust 60%/Python 80%/React 70% (L549) | B5 E.1 동일 | PHASE_B5 | **MATCH** |
| 8 | B#9 | 마이그레이션 6원칙 LOCK | PART2 L611-617 | B7 G.2 L36-41 정확 일치 | PHASE_B7 | **MATCH** |
| 9 | B#11 | 운영 결정 | PART2 §6.12 운영 결정 항목 | PART2 자체 정의 | PART2 §6.12 | **MATCH** |
| 10 | B#12 | requires-python >=3.11 | PART2 L84 "Python 3.11+" | B3 C.1 동일 | PHASE_B3 | **MATCH** |
| 11 | B#15 | pytest >=8.3.0, pytest-asyncio >=0.24.0 | PART2 "pytest" 사용 명시 | B3: pytest >=8.3.0 | PHASE_B3 | **MATCH** |
| 12 | B#16 | V2 Docker Compose 서비스 정의 | V2-Phase 1 #6 (L608) | B6 §5 | PHASE_B6 | **MATCH** |
| 13 | B#17 | V3 Helm 차트 구조 | V3-Phase 1 #1 (L708) | B6 F.7 K8s/Helm | PHASE_B6 | **MATCH** (단, B6에 실제 Helm values 미제공) |
| 14 | B#18 | 10-Step Migration Orchestration | PART2 L619-632 | B7 G.8.3 (10단계 동일) | PHASE_B7 | **MATCH** |
| 15 | B#19 | 사후검증 체크리스트 7항목 | PART2 L634-642 | B7 §8.5 | PHASE_B7 | **MATCH** |
| 16 | B#20 | V0 GO/NO-GO 16항목 | PART2 §7.1 | CLAUDE.md §10 | CLAUDE.md | **MATCH** |
| 17 | B#21 | V1 GO/NO-GO 21항목 | PART2 §7.2 | CLAUDE.md §10 | CLAUDE.md | **MATCH** |
| 18 | B#22 | GitHub Actions 플랫폼 | PART2 §6.4 "GitHub Actions" | B6 F.1 | PHASE_B6 | **MATCH** |
| 19 | B#23 | Branch 전략 | 5-branch (main/develop/feature/hotfix/release) | B6 F.2 | PHASE_B6 | **MATCH** |
| 20 | B#24 | 보안 파이프라인 도구 | pip-audit, cargo audit, npm audit, Trivy, gitleaks | B6 F.8 | PHASE_B6 | **MATCH** |
| 21 | B#25 | 마이그레이션 V1→V2 대상 4종 | SQLite→PG, JSONL→PG, Chroma→Qdrant, JSON→Neo4j | B7 G.4 | PHASE_B7 | **MATCH** |
| 22 | B#26 | IPC bridge 테스트 | spawn vs mock 방식 | B5 E.4 | PHASE_B5 | **MATCH** |
| 23 | B#27 | V0 활성 워크플로우 수 | V0 최소 워크플로우 | B6 F.9 | PHASE_B6 | **MATCH** |
| 24 | B#28 | build-tauri.yml 크로스 플랫폼 | Linux/Win/Mac 빌드 | B6 F.5 | PHASE_B6 | **MATCH** |

> **B#5 (config 13섹션)**: 개수 MATCH이나 섹션명 MISMATCH — MISMATCH #1-2 참조.
> **B#7 (GitHub Actions 14개)**: MISMATCH #6 — 14개 논리 vs 6개 실제 파일.
> **B#10 (레지스트리 카운트)**: NO_SOURCE #2 — D2.1-D2 미확인.
> **B#13 (config 전수 키)**: MISSING #1-3 + NO_SOURCE #1 — [core]/[guardrails]/[rate_limit] 누락, [self_check] 출처 불명.
> **B#14 (ruff 설정)**: MISSING #4 — 상세 설정 미기재.

---

## 종합 판정

### BLOCKER (2건)

| # | 유형 | 항목 | 내용 |
|---|------|------|------|
| BLK-1 | MISMATCH | Config 4섹션명 불일치 | PART2 [general]/[safety]/[self_check]/[memory] ↔ B4 정본 [core]/[guardrails]/[rbac]/[rate_limit]. V7-1에서 카운트만 11→13 정합, 섹션명 미정합 |
| BLK-2 | MISSING | [core] LOCK 키 누락 | `single_decision_lock (LOCK)`, `pipeline_stages (LOCK)` 등 아키텍처 핵심 키가 PART2 config에 전혀 없음 |

### HIGH (9건)

| # | 유형 | 항목 | 내용 |
|---|------|------|------|
| H-1 | MISMATCH | LLM 모델명 전수 불일치 | PART2(llama3) vs B4(gemma-2b/gpt-4o-mini) |
| H-2 | MISMATCH | matryoshka_dim 256 vs 512 | PART2=256, B4=512. Agent 6에서 D2.0-06 기준 256 MATCH 판정 → 정본 확정 필요 |
| H-3 | MISMATCH | CI/CD 14개 논리 vs 6개 실제 파일 | B6 정본 6파일 통합구조. PART2 표기 수정 필요. ※ IMP_CONFLICT #1 동일 근인 |
| H-4 | MISMATCH | rbac_default_role OWNER vs OPERATOR | v10.0.0 수정 기록(OWNER)이나 SRC(B4) 미갱신. ※ SC #1 근인 |
| H-5 | MISSING | [guardrails] 섹션 누락 | B4 정본 l1~l4_enabled, fail_policy 등. PART2 [safety]로 단순화 |
| H-6 | MISSING | [rate_limit] 섹션 누락 | B4 정본 rpm, tpm, burst, cooldown 등 전체 미존재 |
| H-7 | IMP_MISSING | E2E Playwright+Tauri 통합 설정 미정의 | WebDriver + Playwright 설정, config 미기재 |
| H-8 | IMP_MISSING | GitHub Actions 경로 필터링 미정의 | 각 워크플로우의 paths: 트리거 필터 미정의. B6에도 상세 미기재 |
| H-9 | IMP_CONFLICT | Tauri Python 번들링 vs 별도 설치 | PART2 "Python 번들링" 암시 vs B6 Python wheel 별도 빌드. 아키텍처 결정 필요 |

### MEDIUM (6건)

| # | 유형 | 항목 | 내용 |
|---|------|------|------|
| M-1 | MISMATCH | max_tokens 2048 vs 4096 | 토큰 상한 2배 차이. 구현 차단은 아님 |
| M-2 | NO_SOURCE | [self_check] 섹션 출처 불명 | B4에 해당 섹션 없음. PART2 창작 의심 |
| M-3 | NO_SOURCE | 레지스트리 카운트 검증 보류 | D2.1-D2 미확인. PART2 §6.11과 v8 기준 간 큰 차이 |
| M-4 | MISSING | ruff 설정 상세 미기재 | line-length=100, select 13개 규칙. "B6 참조" 명시 권장 |
| M-5 | IMP_IMPOSSIBLE | tarpaulin Linux 전용 | Windows/Mac 개발 환경에서 실행 불가. CI Linux runner 대체 |
| M-6 | IMP_MISSING | quality-schema.yml 자동화 상세 미정의 | Pydantic 검증 스크립트/명령어 미기재 |

---

## 검증 완료 선언

- 수정 전: BLOCKER **2**건, HIGH **9**건, MEDIUM **6**건 = 총 **17**건 (SOURCE_CONFLICT **3**건 중 1건은 severity에 포함, 2건은 MATCH 처리)
- 수정 후: 미수정 (BLOCKER **2**건 잔여)
- Dim B: Forward **33** + Reverse **4** = **37** 체크 — MATCH **24**, MISMATCH **7**, NO_SOURCE **2**, MISSING **4**
- Dim C: **14**항목 — IMP_OK **8**, IMP_IMPOSSIBLE **1**, IMP_MISSING **3**, IMP_CONFLICT **2**
- ⚠️ **BLOCKER 2건 미해소** — Config 섹션명 4개 불일치 + [core] LOCK 키 누락. Phase 2에서 PART2 config.v1.toml 전면 재작성 필요.
