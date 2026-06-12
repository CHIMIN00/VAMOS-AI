# PHASE4-DEC-005 (P4-0 ⑪): 저장소·스캐폴딩 방침 — D:\VAMOS 단일 repo + Phase 2 자산 승계 + ci.yml 단일 정본

> **결정일**: 2026-06-12 (P4-0) · **포맷**: A6 · **우선순위**: Must · **출처**: P4-PRE A-11+B-01a

## 결정

1. **단일 repo 확정 표면화**: VAMOS 코드 저장소 = `D:\VAMOS` 기존 repo(문서+코드 공존 monorepo). PART2 STEP-1 사용자 작업 "GitHub 리포 `vamos` 신설+clone"은 **불집행**(PART1 E.5 검증이 이미 D:\VAMOS git init을 PASS 기록 — 사실상 기결정의 표면화).
2. **Phase 2 자산 전건 승계**: `backend/pyproject.toml`(DEC-002 banned-api+ruff 13룰+mypy strict)·`backend/tests/`(conftest)·`.github/workflows/ci.yml`·Hook 18·`scripts/vamos_lint.py`·`scripts/check_config_lock.py` — V0-STEP-1(스캐폴딩)·STEP-6(CI)의 해당 산출물은 **신규 생성이 아니라 기존 자산 위 증분**.
3. **ci.yml 단일 통합 정본 재확인**: V0-STEP-6의 "quality-python.yml·test-python.yml 2종 분리"는 Phase 2 확정(PHASE_B6 §2 정본 중재 — quality/test/vamos-lint 3 job 단일 ci.yml)으로 **대체됨**. Stage Gate #1/#2(L1556-1557)는 "ci.yml의 해당 job PASS"로 읽는다.
4. **P4-0 스캐폴딩 생성 범위(4-1 타입 동기화 최소)**: `backend/vamos_core/{__init__.py, schemas/{__init__.py, contracts.py, registries.py}}` + `schemas/seed/`(경로 = DEC-009) + `scripts/generate_types.py` + `shared/types/` + `config/schema_registry.toml`. **`src/`(React)·`src-tauri/`(Rust)는 P4-2(IPC·프론트 세션)로 순연** — serde 생성 포함(하단). `config/config.v1.toml`은 P4-1(4-5).
5. **serde(Rust) 생성 = P4-2 순연**: A20 왕복 테스트는 Rust 컴파일 검증을 수반해야 의미가 있어 src-tauri 스캐폴딩+cargo 빌드와 동일 세션이 정합. 본 세션 왕복은 Python→JSON Schema→TS(Zod)→Python 성립까지(프롬프트 STEP 6c 허용 경로). generate_types.py에 serde 생성 슬롯을 자리표시(NotImplemented 명시)로 둔다.

## 근거
PART1 E.5(D:\VAMOS git init PASS 2026-03-02) · PROGRESS 2-4(ci.yml 단일 통합 정본 — PHASE_B6 §2 중재) · PART2 §6.4 XREF-V0-19(주석 기존재, STEP-6 본문 미중재 — 본 결정으로 중재 완성) · P4-PRE B-01a("실질 기결정 — 표면화만 필요").

## 기각 대안
- GitHub 리포 신설 분리 — 문서 SOT와 코드의 2-repo 분리는 CLAUDE.md 자동 로딩·Hook 18·CI 기배선 전부 재구축 유발, 이득 0. 기각.
- 본 세션 src-tauri 포함 — Rust 빌드 검증 없는 serde 생성물은 A20 "왕복 PASS 후 동시 커밋" 원칙 위반 소지(미검증 생성물 커밋). 기각.

## 집행
PART2 STEP-1 사용자 작업 2(L337)와 STEP-6 워크플로우 절(L1378-1380)에 reconcile 주석 부기(본 세션, CRLF 보존). 스캐폴딩 생성은 STEP 6.
