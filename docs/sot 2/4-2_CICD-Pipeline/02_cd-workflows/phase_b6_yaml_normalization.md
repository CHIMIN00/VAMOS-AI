# PHASE_B6 YAML 예시 → sot 2/ 정규화 통합 (P1-4)

> **파일**: `02_cd-workflows/phase_b6_yaml_normalization.md`
> **세션**: P1-4 (1-4 PHASE_B6 YAML 예시 → sot 2/ 정규화)
> **버전**: v1.3 (2026-04-24, STAGE 7 Phase 2 STEP_B step 7 — F-15 [LOCK_UNCHANGED] DEFERRED_TO_PHASE3 결정 반영)
> **상태**: ACTIVE
> **LOCK**: LOCK-CI-01, LOCK-CI-06, LOCK-CI-11, LOCK-CI-12
> **위치 근거**: §7 1-4 절차 5 "Docker Compose V2 배포 구조(LOCK-CI-12) YAML 정규화 → `02_cd-workflows/`에 반영". 본 문서는 14개 WF 전역을 아우르는 정규화 매트릭스이지만, 가장 큰 YAML 블록인 Docker Compose V2 배포 구조가 본 하위폴더 산출물이므로 02_cd-workflows/ 를 거처로 선정.

---

## 0. 교차 참조 블록

| 대상 | 경로 / 섹션 | 용도 |
|------|-----------|------|
| 전략 정본 (Level 2) | `D:\VAMOS\docs\sot\PHASE_B6_CICD_PIPELINE.md` §2~§8 | YAML 예시 원본 전수 |
| Part2 | `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §V1-Phase 6 | 14개 YAML 파일명 |
| 상세명세 | `CICD_PIPELINE_상세명세.md` §WF-1 ~ §WF-14 | Job/트리거/캐싱/시크릿 구현 정본 |
| 종합계획서 | `CICD_PIPELINE_구조화_종합계획서.md` §1.3 P-3/P-4, §6 ISS-04, §7 1-4, §9 우선순위 | 게이트 + 충돌 해결 |
| 권한 | `AUTHORITY_CHAIN.md` LOCK-CI-01, -06, -11, -12 | 14개 WF 목록 / 4플랫폼 / concurrency / 컨테이너 |
| P1-1 산출물 | `01_ci-workflows/WF-*.md`, `02_cd-workflows/WF-*.md`, `03_security-scanning/WF-*.md`, `05_release-management/WF-*.md` | 14개 WF 상세 파일 (2,666줄) |
| P1-2 산출물 | `03_security-scanning/secrets_mapping.md` | 32건 시크릿 매핑 정본 |
| P1-3 산출물 | `04_cache-strategy/cache_strategy_detail.md` | 캐시 키/경로/TTL 정본 |
| CONFLICT | `CONFLICT_LOG.md` C-01~C-04 | 기존 해소 4건 |

---

## 1. Purpose / Scope

### 1.1 목적
PHASE_B6 §2~§8 의 YAML 코드 블록 22건(`^```yaml` 코드 펜스 기준)을 sot 2/ 구조(14 WF 상세 파일 + 서브폴더 5개)에 **역매핑 + 정규화 + 편차 기록** 하여 §1.3 P-4 (PHASE_B6 내용 미통합) 과 §6 ISS-04 의 PHASE_B6 통합 누락을 해소한다. 본 문서는 각 PHASE_B6 YAML 블록의 **어디에 어떻게 반영되었는지** 의 역매핑 테이블이며, YAML 내용 자체는 P1-1 산출물(14 WF 상세 파일)이 정본이다.

### 1.2 범위 (포함)
- PHASE_B6 §2 (코드 품질 4건 Y-01..Y-04) / §3 (테스트 4건 Y-05..Y-08) / §4 (빌드 3건 Y-09..Y-11) / §5 (릴리스 3건 Y-12..Y-14) / §6 (배포 3건 Y-15 workflow + Y-15b compose + Y-16 K8s) / §7 (보안 3건 Y-17..Y-19) / §8 (통합 ci.yml 1건 Y-20 + nightly.yml 스텁 1건 Y-21) — **총 22개 YAML 블록** (`^```yaml` 코드 펜스 카운트 22와 정확히 일치)
- V1(로컬) / V2(Docker Compose) / V3(K8s/ArgoCD) 버전별 적용 범위
- LOCK-CI-06 (Tauri 4플랫폼 매트릭스) YAML 정규화
- LOCK-CI-12 (Docker Compose V2 6 서비스 — app tier 3 + data tier 3) YAML 정규화
- 의도된 변형(variant) 전수 기록 및 근거

### 1.3 범위 (제외)
- 각 WF 파일의 세부 job/step 재작성 (P1-1 정본 유지, 본 문서는 매핑만 제공)
- K8s/ArgoCD 실제 Helm chart/Kustomize 작성 → Phase 2 (P2-2)
- docker-compose.staging.yml / docker-compose.prod.yml 완전체 작성 → Phase 2 (P2-1)
- V3 nightly.yml 완전체 구현 → Phase 2 (P2-4)
- 시크릿 로테이션 린터 / 캐시 퍼지 자동화 → Phase 2 (P2-3)

---

## 2. PHASE_B6 YAML 블록 인벤토리 (총 22건)

| # | PHASE_B6 위치 | YAML 블록 주제 | 줄 범위 | 적용 버전 | 대상 WF / 산출물 |
|---|--------------|---------------|--------|----------|-----------------|
| Y-01 | §2.1 | Python 린트/타입체크 (ruff + mypy) | 62–90 | V1+ | `01_ci-workflows/WF-3_lint.md` §(Python 파트) + `WF-1_ci.md` 통합 ci.yml 중 `python-quality` job |
| Y-02 | §2.2 | Rust 린트/빌드 (clippy + fmt + build) | 118–151 | V1+ | `01_ci-workflows/WF-3_lint.md` §(Rust 파트) + `WF-1_ci.md` 통합 ci.yml 중 `rust-quality` job |
| Y-03 | §2.3 | React 린트/타입체크 (eslint + tsc + prettier) | 157–186 | V1+ | `01_ci-workflows/WF-3_lint.md` §(Frontend 파트) + `WF-1_ci.md` 통합 ci.yml 중 `react-quality` job |
| Y-04 | §2.4 | Pydantic 스키마 검증 (schema-validation) | 192–213 | V1+ | `01_ci-workflows/WF-2_test.md` §(schema 파트) + `WF-1_ci.md` 통합 ci.yml 중 `schema-validation` job |
| Y-05 | §3.1 | Python 단위/통합 테스트 (pytest + Postgres service) | 277–339 | V1+ | `01_ci-workflows/WF-2_test.md` §Job 구성 `unit-tests` / `integration-tests` |
| Y-06 | §3.2 | Rust 테스트 (cargo test) | 357–407 | V1+ | `01_ci-workflows/WF-2_test.md` §Job 구성 `rust-tests` |
| Y-07 | §3.3 | React 테스트 (vitest) | 411–446 | V1+ | `01_ci-workflows/WF-2_test.md` §Job 구성 `frontend-tests` |
| Y-08 | §3.4 | 커버리지 리포트 합산 (Codecov 업로드) | 482–524 | V1+ | `01_ci-workflows/WF-2_test.md` §5 커버리지 게이트 (LOCK-CI-03) |
| Y-09 | §4.1 | Tauri 멀티플랫폼 빌드 (4 target matrix) | 540–636 | V1+ | `01_ci-workflows/WF-4_build-tauri.md` §2/§3/§4 (LOCK-CI-06 정본) |
| Y-10 | §4.2 | Python 패키지 빌드 (wheel + sdist + twine check) | 640–666 | V1+ | `05_release-management/WF-5_release.md` §(Python dist) 부속 |
| Y-11 | §4.3 | Docker 이미지 빌드 (GHCR matrix: app tier 3 이미지 `vamos-orange-core`/`vamos-blue-nodes`/`vamos-api-gateway`) | 670–732 | V2+ | `05_release-management/WF-5_release.md` §(Docker push 부속) + 본 문서 §5 (LOCK-CI-12 app tier 연결) |
| Y-12 | §5.2 | Changelog 자동 생성 (git-cliff) | 767–791 | V1+ | `05_release-management/WF-14_version-bump.md` §(changelog 파트) + `WF-5_release.md` §(finalize) |
| Y-13 | §5.3 | GitHub Release + Tauri 바이너리 업로드 | 824–923 | V1+ | `05_release-management/WF-5_release.md` §(release job 전수) |
| Y-14 | §5.4 | Docker Registry Push (GHCR V2+) | 927–965 | V2+ | `05_release-management/WF-5_release.md` §(push-docker job) |
| Y-15 | §6.1 (YAML) | Docker Compose V2 배포 워크플로 | 973–1050 | V2 | `02_cd-workflows/WF-6_deploy-staging.md` §3 `deploy-compose` job + `WF-7_deploy-prod.md` 동일 + 본 문서 §5 |
| Y-15b | §6.1 (compose) | `deploy/docker-compose.yml` 다중 서비스 구조체 (PHASE_B6 원본 5 서비스 → LOCK-CI-12 정본 6 서비스) | 1054–1125 | V2 | 본 문서 §5 (LOCK-CI-12 정본 전개) |
| Y-16 | §6.2 | K8s Helm 배포 (V3) | 1129–1206 | V3 | `02_cd-workflows/WF-7_deploy-prod.md` §(K8s 파트 — 스텁만) → 완전체는 Phase 2 (P2-2) |
| Y-17 | §7.1 | 의존성 취약점 스캔 (pip-audit / cargo-audit / npm audit / trivy) | 1214–1311 | V1+ | `03_security-scanning/WF-11_dependency-check.md` §(도구별 job) + `WF-8_security-scan.md` §(trivy 파트) |
| Y-18 | §7.2 | 비밀 키 노출 검사 (trufflehog) | 1315–1349 | V1+ | `03_security-scanning/WF-8_security-scan.md` §(trufflehog 파트) |
| Y-19 | §7.3 | 라이선스 검사 (pip-licenses / license-checker / cargo-deny) | 1379–1417 | V1+ | `03_security-scanning/WF-8_security-scan.md` §(license 파트) |
| Y-20 | §8 | 통합 ci.yml (Stage 1~5 오케스트레이션) | 1446–1692 | V1+ | `01_ci-workflows/WF-1_ci.md` §2/§3 (reusable workflow 호출형으로 변형) |
| Y-21 | §8 부록 | nightly.yml 스텁 (V3 예정) | 1711–1727 | V3 | `01_ci-workflows/WF-13_nightly.md` §(스텁만) → 완전체는 Phase 2 (P2-4) |

**총 22개 YAML 블록** — 내역: §2 코드품질 4 (Y-01..Y-04) + §3 테스트 4 (Y-05..Y-08) + §4 빌드 3 (Y-09..Y-11) + §5 릴리스 3 (Y-12..Y-14) + §6 배포 3 (Y-15, Y-15b, Y-16) + §7 보안 3 (Y-17..Y-19) + §8 통합·부록 2 (Y-20, Y-21) = **22**. PHASE_B6 ` ```yaml ` 코드 펜스 22개 전수 식별 (2026-04-11 재검증, `grep -c '^\`\`\`yaml'` = 22), sot 2/ 구조에 100% 매핑 완료.

---

## 3. 정규화 매핑 상세 (WF 파일별 역매핑)

### 3.1 01_ci-workflows/ (8 WF)

| WF 파일 | PHASE_B6 블록 | 반영 위치 (WF §) | 정규화 변형 | 변형 근거 |
|---------|--------------|----------------|------------|----------|
| `WF-1_ci.md` | Y-20 (통합 ci.yml) | §2 트리거 / §3 Job 구성 / §3.1 mermaid | **reusable workflow 호출형으로 재구성** (stage-직렬 `python-quality→schema-validation→python-test→build-check→ci-summary` 를 `setup→(lint/test-*/security)→build-check→status-check` 7-job 구조로 변환) | PHASE_B6 ci.yml 은 단일 파일 오케스트레이션 예시, sot 2/ 는 workflow_call 재사용 구조 채택 (LOCK-CI-01 14 WF 구조와 정합). 기능 동치. |
| `WF-1_ci.md` | Y-20 env block | §2 트리거 블록 | env 전역 블록 생략 (각 호출대상 WF 가 자체 env 선언) | reusable workflow 별 독립 env 관리가 더 안전 |
| `WF-2_test.md` | Y-04/Y-05/Y-06/Y-07/Y-08 | §3 매트릭스 + §4 Job 구성 + §5 커버리지 | Python 매트릭스 `["3.11","3.12"]` × OS 3종 (PHASE_B6 은 단일 3.11 + ubuntu 고정). frontend-tests 는 `npx vitest run --coverage` 대신 `pnpm run test` 사용 | 상세명세 WF-2 가 매트릭스 확장 정본, pnpm 은 C-02 해결 (PHASE_B6 `npm` → sot 2/ `pnpm` 전환) |
| `WF-2_test.md` | Y-05 Postgres service | §4 `integration-tests` | Postgres service 블록 **유지** (PHASE_B6 값 그대로) | 변경 불필요 |
| `WF-3_lint.md` | Y-01/Y-02/Y-03 | §(Python/Rust/Frontend 3 파트) | Y-01 `cache: "pip"` → sot 2/ `cache: "pip" + uv cache` 병행. Y-03 `cache: "npm"` → `cache: "pnpm"` (C-02 해결) | P1-3 §3 "Python `.venv` 변형" + "Node `pnpm-e2e-` 변형" 정본 준수 |
| `WF-4_build-tauri.md` | Y-09 (4 target matrix) | §2 트리거 + §3 매트릭스 + §4 빌드 단계 + §5 코드 서명 | **4 target 전수 유지** (LOCK-CI-06 정본). artifact 파일명은 `vamos_<arch>.<ext>` 단형 (예: `vamos_amd64.AppImage`, `vamos_x64.msi`, `vamos_arm64.dmg`, `vamos_x64.dmg`), `sign` 필드 추가 (gpg/authenticode/apple). 매트릭스 키명은 `os:` 통일, `ubuntu-22.04` → `ubuntu-latest` 정규화 | sot 2/ 는 runs-on 버전 고정 해제(상시 최신, webkit2gtk-4.1 은 `apt-get` 단계에서 별도 보장), `sign` 필드 추가는 LOCK-CI-07 서명 정책 명시화 |
| `WF-4_build-tauri.md` | Y-09 retention-days | §4 단계 8 | `retention-days: 7` → `release_mode ? 30 : 7` (조건부) | C-03 해결 연장 — PR 빌드 7일, release 빌드 30일로 분리 (PHASE_B6 C-03 판정 "PHASE_B6 우선 + 릴리스는 GitHub Release 첨부" 반영) |
| `WF-4_build-tauri.md` | Y-09 TAURI_SIGNING_* | §2 secrets 블록 | **본문 누락** (P1-2 cross-check 지적) → 본 세션에서 **반영 예정 변경 후보** (아래 §7 CONFLICT 후보 참조) | P1-2 불일치 #29/#30 |
| `WF-9_benchmark.md` | (PHASE_B6 에 독립 YAML 없음) | N/A | 상세명세 WF-9 + ISS-05 로 자체 구성 | PHASE_B6 는 nightly.yml 스텁(Y-21)에서 "performance-benchmarks" 언급만, 정본 없음 |
| `WF-10_docs-build.md` | (PHASE_B6 에 독립 YAML 없음) | N/A | 상세명세 WF-10 로 자체 구성 | PHASE_B6 는 docs 별도 워크플로 정의 없음 |
| `WF-12_e2e-test.md` | (PHASE_B6 에 독립 YAML 없음, Y-21 nightly 스텁에서 언급) | §트리거 + §job | Playwright + Tauri WebDriver (ISS-06) 로 자체 구성 | PHASE_B6 §V3 전용, V1 은 상세명세 §WF-12 기반 |
| `WF-13_nightly.md` | Y-21 (스텁) | §2 트리거 + §(향후 확장) | cron `'0 3 * * *'` 유지, job 정의는 스텁만 (완전체는 Phase 2 P2-4) | PHASE_B6 명시적 V3 유예 |

### 3.2 02_cd-workflows/ (2 WF)

| WF 파일 | PHASE_B6 블록 | 반영 위치 | 정규화 변형 | 변형 근거 |
|---------|--------------|----------|------------|----------|
| `WF-6_deploy-staging.md` | Y-15 (deploy-v2.yml) | §2 트리거 + §3 Job + §4 대상 + §7 롤백 | trigger `workflow_dispatch` → `workflow_run(Release completed) + workflow_dispatch` 병용. environment input → `inputs.version` 만 유지 (환경은 staging 고정, prod 는 WF-7). SSH via `webfactory/ssh-agent@v0.9.0` → 직접 `STAGING_SSH_KEY`+`STAGING_HOST` (상세명세 WF-6 정본) | WF-6 는 staging 전용, WF-7 은 prod 전용으로 분리 (LOCK-CI-10 프로덕션 승인 요건 + F-1 게이트 분리) |
| `WF-6_deploy-staging.md` | Y-15b (docker-compose.yml) | §4 배포 대상 `deploy-compose` | **구조체 전체는 본 문서 §5 에 전개** (상세명세 §WF-6 링크), WF-6 본문은 "SSH → `docker compose up -d`" 요약만 | 본 문서가 LOCK-CI-12 정본 전개 위치 (§7 1-4 절차 5) |
| `WF-7_deploy-prod.md` | Y-15 (deploy-v2.yml environment=prod) | §2 트리거 + §(수동 승인 게이트) | prod 경로는 workflow_dispatch 만 허용 + `environment: production` (GitHub Environment Protection Rules) 필수 | LOCK-CI-10 프로덕션 수동 승인 |
| `WF-7_deploy-prod.md` | Y-16 (K8s Helm) | §(K8s 파트 스텁) | **스텁만** — 완전체 Helm chart / ArgoCD Application CRD 는 Phase 2 (P2-2) | §7 2-2 참조 |

### 3.3 03_security-scanning/ (2 WF)

| WF 파일 | PHASE_B6 블록 | 반영 위치 | 정규화 변형 | 변형 근거 |
|---------|--------------|----------|------------|----------|
| `WF-8_security-scan.md` | Y-17 docker-scan (trivy) | §(trivy 파트) | `scan-type: "fs"` + `severity: "CRITICAL,HIGH"` 유지, `if: github.ref == 'refs/heads/main'` 조건 완화 → main + release/** 추가 | release 브랜치도 보안 스캔 필요 |
| `WF-8_security-scan.md` | Y-18 (trufflehog + custom patterns) | §(trufflehog 파트) | custom PATTERNS 목록 **전수 유지** (OPENAI/ANTHROPIC/POSTGRES/NEO4J/QDRANT/TAURI_SIGNING_PRIVATE_KEY 6건) | 변경 불필요 |
| `WF-8_security-scan.md` | Y-19 (pip-licenses / license-checker / cargo-deny) | §(license 파트) | allow-list / deny-list **전수 유지** (deny.toml 구조 동일) | 변경 불필요 |
| `WF-11_dependency-check.md` | Y-17 python-audit/rust-audit/npm-audit | §Job 구성 | `continue-on-error: true` → `false` + 임계값 기반 게이트 (HIGH/CRITICAL 0 건) 로 전환 | LOCK-CI-08 보안 스캔 도구 게이트 강화 (상세명세 WF-11 정본) |

### 3.4 05_release-management/ (2 WF)

| WF 파일 | PHASE_B6 블록 | 반영 위치 | 정규화 변형 | 변형 근거 |
|---------|--------------|----------|------------|----------|
| `WF-5_release.md` | Y-13 (release.yml) | §2 트리거 + §3 Job (quality/test/build-tauri/finalize) | **reusable workflow 호출형으로 재구성** (`uses: ./.github/workflows/quality-all.yml` → `uses: ./.github/workflows/ci.yml` 또는 WF-1 체인 재사용) | LOCK-CI-01 14 WF 재사용 구조 |
| `WF-5_release.md` | Y-10 (build-python) | §(Python dist 부속) | wheel + sdist + twine check **전수 유지** | 변경 불필요 |
| `WF-5_release.md` | Y-14 (push-docker V2+) | §(push-docker job) | matrix app tier 3 서비스 이미지 (orange-core/blue-nodes/api-gateway) **전수 유지**, `platforms: linux/amd64,linux/arm64` 유지 | LOCK-CI-12 컨테이너 레지스트리 요건 |
| `WF-5_release.md` | Y-09 TAURI_SIGNING_* | §(build-tauri 호출부) | **본문 누락** (P1-2 cross-check 지적 #29/#30) → 변경 후보 (§7) | P1-2 불일치 연장 |
| `WF-14_version-bump.md` | Y-12 (changelog) | §(changelog 파트) + cliff.toml | git-cliff action **전수 유지**, cliff.toml 설정 (commit_parsers) 본문에 삽입 | 변경 불필요 |

---

## 4. V1 / V2 / V3 버전별 진화 경로 (§1.3 P-3 해결)

### 4.1 버전별 YAML 적용 범위

| WF / 블록 | V1 (로컬 Tauri) | V2 (Docker Compose) | V3 (K8s + ArgoCD) | 진화 방향 |
|----------|----------------|--------------------|--------------------|----------|
| Y-01 Python 린트 | ✅ | ✅ (동일) | ✅ (동일) | 무변화 |
| Y-02 Rust 린트 | ✅ | ✅ (동일) | ✅ (동일) | 무변화 |
| Y-03 React 린트 | ✅ | ✅ (동일) | ✅ (동일) | 무변화 |
| Y-04 Schema 검증 | ✅ (37 스키마) | ✅ (+ D4/D5 추가) | ✅ (+ D6/D7) | 스키마 개수 증가 |
| Y-05 Python 테스트 | ✅ (Postgres service) | ✅ (+ Qdrant/Neo4j service) | ✅ (Testcontainer GHCR mirror) | service 추가, F-03 이월 |
| Y-06 Rust 테스트 | ✅ | ✅ (cargo-nextest) | ✅ (target 구조 최적화) | F-04 이월 |
| Y-07 React 테스트 | ✅ (vitest) | ✅ (+ Storybook snapshot) | ✅ | V2+ Storybook |
| Y-08 커버리지 합산 | ✅ (Codecov) | ✅ | ✅ (+ 대시보드) | V3 대시보드 |
| Y-09 Tauri 빌드 (LOCK-CI-06) | ✅ 4 target | ✅ 4 target (동일) | ✅ 4 target + Linux ARM64 확장 후보 | LOCK 확장 [LOCK_CHANGE_NEEDED] 후보 |
| Y-10 Python 패키지 빌드 | ✅ | ✅ | ✅ (PyPI 자동 업로드) | V3 PyPI |
| Y-11 Docker 이미지 빌드 | ❌ | ✅ (app tier 3 이미지) | ✅ (app tier 3 이미지 + sidecar) | V2 도입 |
| Y-12 Changelog | ✅ | ✅ | ✅ | 무변화 |
| Y-13 GitHub Release + Tauri 업로드 | ✅ | ✅ | ✅ | 무변화 |
| Y-14 Docker Registry Push | ❌ | ✅ (GHCR) | ✅ (GHCR + cosign 서명) | V3 cosign 도입 |
| Y-15 Docker Compose 배포 (LOCK-CI-12) | ❌ | ✅ staging + prod | ⏳ deprecated (→ K8s 전환) | V3 전환 |
| Y-15b docker-compose.yml | ❌ | ✅ 6 서비스 (orange-core/blue-nodes/api-gateway/postgres/qdrant/neo4j, LOCK-CI-12 정본) | ⏳ deprecated | V3 전환 |
| Y-16 K8s Helm 배포 | ❌ | ❌ | ✅ | V3 신규 |
| Y-17 의존성 스캔 (pip-audit / cargo-audit / npm audit / trivy) | ✅ | ✅ | ✅ (+ Snyk) | V3 Snyk |
| Y-18 Trufflehog | ✅ | ✅ | ✅ | 무변화 |
| Y-19 라이선스 검사 | ✅ | ✅ | ✅ | 무변화 |
| Y-20 통합 ci.yml | ✅ | ✅ | ✅ | 무변화 (재사용 구조 유지) |
| Y-21 nightly.yml 스텁 | ❌ | ⏳ 부분 | ✅ 완전체 | V3 완성 |

### 4.2 버전 전환 주의 사항

- **V1 → V2**: Y-11/Y-14/Y-15/Y-15b/Y-17(trivy) 이 신규 도입. 시크릿 `DEPLOY_SSH_KEY`, `DEPLOY_HOST`, `POSTGRES_PASSWORD`, `QDRANT_API_KEY`, `NEO4J_AUTH`, `OPENAI_API_KEY` 추가 필요 (P1-2 secrets_mapping.md §6 V1→V2 전환 테이블 참조).
- **V2 → V3**: Y-16 K8s Helm 배포 도입, Y-15/Y-15b 는 deprecated, 시크릿 `KUBECONFIG` + ArgoCD 토큰 추가 (P1-2 §6 V2→V3 전환 테이블 참조). Y-09 Linux ARM64 target 추가는 LOCK-CI-06 확장을 요구 → [LOCK_CHANGE_NEEDED] 후보.
- **각 WF 파일**: 버전별 세부 차이는 해당 WF `§11 LOCK 위반 체크` 다음에 선택 `§V1/V2/V3 변화` 섹션을 Phase 2 에서 추가하는 것을 권고 (본 문서는 역매핑만).

---

## 5. LOCK-CI-12 Docker Compose V2 정본 전개

### 5.1 워크플로 YAML (정규화)

아래는 PHASE_B6 §6.1 Y-15 를 sot 2/ 구조(WF-6/WF-7 분리, staging/prod 게이트 분리)에 맞춰 정규화한 **정본 YAML 템플릿** 이다. WF-6_deploy-staging.md / WF-7_deploy-prod.md 는 본 블록을 참조하되, **WF-6 은 `workflow_run` 자동 체인 + `workflow_dispatch` 수동 병용** / **WF-7 은 `workflow_dispatch` 전용 (GitHub Environment Protection 필수)** 으로 분기된다. 아래 단일 블록은 WF-6 기준으로 작성되었고, WF-7 에서는 `workflow_run` 섹션을 제거한 변형을 사용한다.

```yaml
# 02_cd-workflows/ 정본 — WF-6 (staging) / WF-7 (prod) 공통 구조
name: "Deploy V2 (Docker Compose)"

on:
  workflow_run:
    workflows: ["Release"]
    types: [completed]
    branches: [main]           # staging 자동 체인 (WF-6 전용)
  workflow_dispatch:
    inputs:
      environment:
        description: "배포 환경"
        required: true
        type: choice
        options: [staging, production]
      version:
        description: "배포 버전 (예: v1.2.3)"
        required: true
        type: string

concurrency:
  group: deploy-${{ inputs.environment || 'staging' }}
  cancel-in-progress: false     # LOCK-CI-11 동시 배포 금지

jobs:
  deploy-v2:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment || 'staging' }}   # LOCK-CI-10 prod 수동 승인 (GitHub Environment Protection)
    if: >-
      github.event_name == 'workflow_dispatch' ||
      github.event.workflow_run.conclusion == 'success'
    steps:
      - uses: actions/checkout@v4

      - name: Configure SSH
        uses: webfactory/ssh-agent@v0.9.0
        with:
          ssh-private-key: ${{ inputs.environment == 'production' && secrets.PROD_SSH_KEY || secrets.STAGING_SSH_KEY }}

      - name: Generate .env file
        run: |
          cat > deploy/.env <<EOF
          VAMOS_VERSION=${{ inputs.version }}
          POSTGRES_USER=${{ secrets.POSTGRES_USER }}
          POSTGRES_PASSWORD=${{ secrets.POSTGRES_PASSWORD }}
          QDRANT_API_KEY=${{ secrets.QDRANT_API_KEY }}
          NEO4J_AUTH=${{ secrets.NEO4J_AUTH }}
          OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}
          GHCR_TOKEN=${{ secrets.GITHUB_TOKEN }}
          EOF

      - name: Copy .env to remote host
        run: |
          scp deploy/.env ${{ inputs.environment == 'production' && secrets.PROD_HOST_LIST || secrets.STAGING_HOST }}:/opt/vamos/.env

      - name: Deploy via Docker Compose
        run: |
          ssh ${{ inputs.environment == 'production' && secrets.PROD_HOST_LIST || secrets.STAGING_HOST }} << 'ENDSSH'
            cd /opt/vamos
            docker compose pull
            docker compose up -d --remove-orphans
            docker compose ps
            sleep 10
            curl -f http://localhost:8080/health || exit 1
          ENDSSH

      - name: Post-deploy smoke test
        run: |
          ssh ${{ inputs.environment == 'production' && secrets.PROD_HOST_LIST || secrets.STAGING_HOST }} << 'ENDSSH'
            curl -sf http://localhost:8080/api/v1/health | jq .
            curl -sf http://localhost:8080/api/v1/schemas/version | jq .
          ENDSSH

      - name: Rollback on failure
        if: failure()
        run: |
          ssh ${{ inputs.environment == 'production' && secrets.PROD_HOST_LIST || secrets.STAGING_HOST }} << 'ENDSSH'
            cd /opt/vamos
            # 이전 VAMOS_VERSION 복원 (S3 manifest 버전 관리에서 추출)
            PREV=$(cat .env.prev | grep VAMOS_VERSION | cut -d= -f2)
            sed -i "s/^VAMOS_VERSION=.*/VAMOS_VERSION=$PREV/" .env
            docker compose pull
            docker compose up -d --remove-orphans
          ENDSSH

      - name: Notify deployment
        if: always()
        uses: slackapi/slack-github-action@v1.26.0
        with:
          payload: |
            {
              "text": "VAMOS V2 ${{ inputs.version }} 배포 ${{ job.status }} (${{ inputs.environment || 'staging' }})"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

**PHASE_B6 대비 변형**:
1. trigger 에 `workflow_run` 추가 (release 완료 시 staging 자동 체인)
2. `if:` 조건으로 manual + auto 병용 분기
3. `Rollback on failure` step **신규 추가** (PHASE_B6 없음, 상세명세 §F-1 F-01 게이트 정합)
4. `.env.prev` 매커니즘 도입 (이전 버전 보존)

> **운영 주의**: `workflow_run` 이벤트는 `inputs.version` 을 제공하지 않는다. WF-6 본문(prepare job)에서는 `github.event.workflow_run.head_branch` 또는 직전 release tag 를 조회하여 VAMOS_VERSION 을 도출해야 한다 (예: `gh release view --json tagName`). 위 YAML 은 `workflow_dispatch` 경로 기준 템플릿이며, `workflow_run` 경로용 prepare job 은 WF-6 본문 §3 `prepare` job 이 담당한다.

### 5.2 docker-compose.yml 구조체 (정본, LOCK-CI-12 6 서비스 = app tier 3 + data tier 3)

PHASE_B6 §6.1 Y-15b 를 **LOCK-CI-12 정본**으로 전개한다. PHASE_B6 원본은 `orange-core + blue-nodes + postgres + qdrant + neo4j` **5 서비스**만 포함하며 `api-gateway` 가 누락되어 있다. LOCK-CI-12 (AUTHORITY_CHAIN.md) 는 `orange-core, blue-nodes, api-gateway, postgres, qdrant, neo4j` **6 서비스** (app tier 3 + data tier 3) 로 정의되어 있으므로, 본 §5.2 는 PHASE_B6 Y-15b 에 누락된 `api-gateway` 를 **복원**하여 LOCK 정본 6 서비스를 완전 전개한다. 또한 PHASE_B6 §4.3 Y-11 / §5.4 Y-14 / §8 Y-20 모두 `vamos-api-gateway` 이미지 빌드·푸시를 정의하므로, compose 누락은 PHASE_B6 내부 모순으로 판정된다 (CONFLICT 후보 C-05, §7 참조).

```yaml
# deploy/docker-compose.yml — LOCK-CI-12 정본
version: "3.9"

services:
  # ---------- Application Tier (LOCK-CI-12 app tier 3 서비스) ----------
  orange-core:
    image: ghcr.io/vamos-ai/vamos-orange-core:${VAMOS_VERSION}
    ports: ["8080:8080"]
    depends_on:
      postgres: { condition: service_healthy }
      qdrant:   { condition: service_healthy }
      neo4j:    { condition: service_started }
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/vamos
      - QDRANT_URL=http://qdrant:6333
      - QDRANT_API_KEY=${QDRANT_API_KEY}
      - NEO4J_URL=bolt://neo4j:7687
      - NEO4J_AUTH=${NEO4J_AUTH}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 15s
      timeout: 5s
      retries: 3
    restart: unless-stopped

  blue-nodes:
    image: ghcr.io/vamos-ai/vamos-blue-nodes:${VAMOS_VERSION}
    depends_on:
      orange-core: { condition: service_healthy }
    environment:
      - ORANGE_CORE_URL=http://orange-core:8080
    restart: unless-stopped

  api-gateway:
    image: ghcr.io/vamos-ai/vamos-api-gateway:${VAMOS_VERSION}
    ports: ["80:80", "443:443"]
    depends_on:
      orange-core: { condition: service_healthy }
      blue-nodes:  { condition: service_started }
    environment:
      - UPSTREAM_ORANGE=http://orange-core:8080
      - UPSTREAM_BLUE=http://blue-nodes:9000
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 15s
      timeout: 5s
      retries: 3
    restart: unless-stopped

  # ---------- Data Tier ----------
  postgres:
    image: postgres:16
    volumes: ["postgres_data:/var/lib/postgresql/data"]
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: vamos
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  qdrant:
    image: qdrant/qdrant:v1.9.0
    volumes: ["qdrant_data:/qdrant/storage"]
    ports: ["6333:6333"]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/healthz"]
      interval: 10s
      timeout: 5s
      retries: 5

  neo4j:
    image: neo4j:5-community
    volumes: ["neo4j_data:/data"]
    environment:
      NEO4J_AUTH: ${NEO4J_AUTH}
    ports: ["7474:7474", "7687:7687"]

volumes:
  postgres_data:
  qdrant_data:
  neo4j_data:
```

**PHASE_B6 대비 변형**:
1. `api-gateway` 서비스 **복원** (PHASE_B6 §6.1 Y-15b 에는 누락되어 있으나, LOCK-CI-12 정본은 app tier 3 서비스 `orange-core/blue-nodes/api-gateway` + data tier 3 서비스 `postgres/qdrant/neo4j` 합계 6 서비스를 요구하므로 PHASE_B6 내부 모순을 LOCK 우선으로 해소)
2. 모든 app 서비스에 `restart: unless-stopped` 추가
3. `api-gateway` 에 healthcheck 추가
4. QDRANT_API_KEY 환경 변수 전파 (orange-core 에서 누락되어 있던 부분 보강)

[CONFLICT_CANDIDATE: Y-15b 는 PHASE_B6 원본에서 app tier 3 서비스 중 `api-gateway` 정의가 누락 (5 서비스만 정의). LOCK-CI-12 정본("orange-core + blue-nodes + api-gateway + postgres + qdrant + neo4j 6 서비스, app tier 3 + data tier 3")과 불일치. 본 문서 §5.2 에서 api-gateway 를 복원하여 6 서비스로 전개함. CONFLICT_LOG C-05 등재 후보.]

### 5.3 환경별 overlay

| 환경 | 파일 | 차이 |
|------|------|------|
| staging | `deploy/docker-compose.staging.yml` (Phase 2 P2-1 산출물) | orange-core replicas=1, 로그 레벨 debug, healthcheck interval 5s |
| production | `deploy/docker-compose.prod.yml` (Phase 2 P2-1 산출물) | orange-core replicas=3, 로그 레벨 info, healthcheck interval 15s, `restart: always` |

> 본 P1-4 세션은 base `docker-compose.yml` 정본만 전개. overlay 완전체는 Phase 2 (P2-1) 에서 작성.

---

## 6. LOCK-CI-06 Tauri 4플랫폼 정본 전개

### 6.1 매트릭스 정본

PHASE_B6 §4.1 Y-09 를 sot 2/ WF-4_build-tauri.md §3 에 정규화한 최종 매트릭스:

```yaml
# 01_ci-workflows/WF-4_build-tauri.md §3 정본 (P1-1 본문과 정확 일치)
strategy:
  fail-fast: false   # 한 target 실패 시 나머지 계속 (LOCK-CI-06)
  matrix:
    include:
      - os: ubuntu-latest
        target: x86_64-unknown-linux-gnu
        artifact: vamos_amd64.AppImage
        sign: gpg                             # LOCK-CI-07
      - os: windows-latest
        target: x86_64-pc-windows-msvc
        artifact: vamos_x64.msi
        sign: authenticode                    # LOCK-CI-07
      - os: macos-latest
        target: aarch64-apple-darwin
        artifact: vamos_arm64.dmg
        sign: apple                           # LOCK-CI-07
      - os: macos-latest
        target: x86_64-apple-darwin
        artifact: vamos_x64.dmg
        sign: apple                           # LOCK-CI-07
```

**PHASE_B6 대비 변형**:
1. `artifact-name` → `artifact` 필드명 단축, 파일명은 `vamos_<arch>.<ext>` 로 축약 (PHASE_B6 예시 `vamos-linux-x64.AppImage` 등 장형 → WF-4 본문 `vamos_amd64.AppImage` 단형 정본)
2. `sign` 필드 **신규 추가** (LOCK-CI-07 서명 정책 명시화) — PHASE_B6 Y-09 는 tauri-action 에 위임, sot 2/ 는 단계 분리
3. `runs-on`/`platform` 키명 → WF-4 본문은 `os:` 키로 통일, `ubuntu-22.04` 고정 → `ubuntu-latest` 로 정규화 (webkit2gtk-4.1 정합은 `apt-get install webkit2gtk-4.1-dev` 로 별도 보장)

### 6.2 V3 확장 후보 (LOCK 변경 필요)

[LOCK_UNCHANGED] **2026-04-24 P2-2 결정 (옵션 B 채택)**: LOCK-CI-06 V3 5 target 확장 (`aarch64-unknown-linux-gnu` 추가) 후보를 검토한 결과, V3 도 4 target 유지 결정 (DEFERRED_TO_PHASE3). 사유 5건: (1) Linux ARM64 desktop 사용자 수요 미확인, (2) GitHub-hosted runner ARM64 Linux 제한적 지원, (3) CI/CD 비용 vs ROI 불균형, (4) LOCK 변경 cascade 부담 회피, (5) 자동 RESOLVE 금지 원칙 — Phase 3 사용자 베타 후 재평가 권고. 본 결정 근거: `02_cd-workflows/k8s_argocd_pipeline.md` (P2-2 V2 산출물) §6.2 + AUTHORITY_CHAIN.md v1.1 변경 이력 row 2026-04-24 + plan §7 P2-2 검증 항목 12/12 충족. 이전 [LOCK_CHANGE_NEEDED] 마커 철회. WF-4_build-tauri.md §11 Q2 동일 후보 마커도 본 결정에 따라 [LOCK_UNCHANGED] 판정 적용 (sandbox-only narrative; WF-4 본문 메타데이터 변경 0).

---

## 7. CONFLICT 후보 (신규 — step 7 에서 정식 등재 예정)

본 세션(P1-4) 에서 발견된 PHASE_B6 ↔ sot 2/ 불일치는 다음과 같다. CONFLICT_LOG 직접 편집 금지 규칙에 따라 후보만 보고한다.

[CONFLICT_CANDIDATE: C-05 — PHASE_B6 §6.1 Y-15b `docker-compose.yml` 구조체에 `api-gateway` 서비스 정의 누락 (PHASE_B6 원본 5 서비스: orange-core/blue-nodes/postgres/qdrant/neo4j). LOCK-CI-12 정본 "orange-core + blue-nodes + api-gateway + postgres + qdrant + neo4j 6 서비스 (app tier 3 + data tier 3)" 와 불일치. PHASE_B6 §4.3 Y-11 / §5.4 Y-14 / §8 Y-20 모두 `vamos-api-gateway` 를 빌드·푸시하므로 PHASE_B6 내부 모순. 본 문서 §5.2 에서 api-gateway 복원하여 LOCK 정본 6 서비스 전개. 판정 후보: sot 2/ LOCK-CI-12 우선 (Level 4 > Level 2 예외 — LOCK 이 더 권위).]

[CONFLICT_CANDIDATE: C-06 — PHASE_B6 §4.1 Y-09 `TAURI_SIGNING_PRIVATE_KEY` / `TAURI_SIGNING_PRIVATE_KEY_PASSWORD` 를 tauri-action env 에서 참조하지만, WF-4_build-tauri.md 본문 §5.1 시크릿 매핑 테이블에서 해당 2건 누락. P1-2 cross-check (secrets_mapping.md #29/#30) 에서 이미 탐지. 판정 후보: PHASE_B6 우선 + WF-4/WF-5 본문 보강 필요 (P1-1 step 7 이월 연동).]

[CONFLICT_CANDIDATE: C-07 — PHASE_B6 §8 통합 ci.yml (Y-20) 의 `cache: "npm"` vs sot 2/ `cache: "pnpm"` (C-02 기연장). Y-20 전체 블록은 아직 개별 충돌 항목으로 등재되지 않았으므로 C-02 와 연결된 명시적 범위 확장 후보. 판정 후보: C-02 연장 (sot 2/ 우선).]

[CONFLICT_CANDIDATE: C-08 — PHASE_B6 §3.1 Y-05 Postgres service `POSTGRES_USER: vamos_test / POSTGRES_PASSWORD: test_password` vs §8 Y-20 `POSTGRES_USER: vamos_test / POSTGRES_PASSWORD: test_pass` (마지막 `_password` → `_pass` 축약). PHASE_B6 내부 모순. 판정 후보: PHASE_B6 §8 (통합 예시) 우선 → sot 2/ WF-2 에는 `test_password` 유지 (보안 관점 긴 문자열 선호). 또는 PHASE_B6 수정 권고.]

[CONFLICT_CANDIDATE: C-09 — PHASE_B6 §4.3 Y-11 `build-docker` 의 matrix service name `vamos-orange-core / vamos-blue-nodes / vamos-api-gateway` 과 §6.1 Y-15b compose 의 service key `orange-core / blue-nodes` 명명 차이 (`vamos-` prefix 유무). sot 2/ 정본은 image name 에 `vamos-` prefix 유지 + compose service key 는 prefix 없음 (PHASE_B6 Y-15b 형태) 조합. 판정 후보: 명명 규칙 이원화 유지 (image name 과 compose key 는 별개).]

**총 5건 CONFLICT 후보** (C-05/C-06/C-07/C-08/C-09). 모두 step 7 에서 정식 등재 + 판정 예정.

---

## 8. 호출 방향 정합성 (Sequence diagram)

sot 2/ 에서 reusable workflow 호출 방향은 "진입점 WF (WF-1, WF-5) → 재사용 WF (WF-2/3/4/8/11) → 산출물(artifact / cache / secret)" 이며, PHASE_B6 의 단일 파일 오케스트레이션과 기능 동치이다. 호출 규칙은 §9.1 우선순위 (PHASE_B6 Level 2 > sot 2/ Level 4) 를 따르되, LOCK-CI-01 14 WF 구조 유지를 위해 재사용형으로 변형한다.

```mermaid
sequenceDiagram
    actor Dev as Developer
    participant GH as GitHub
    participant W1 as WF-1 ci.yml
    participant W3 as WF-3 lint.yml
    participant W2 as WF-2 test.yml
    participant W8 as WF-8 security.yml
    participant W4 as WF-4 build-tauri.yml
    participant W5 as WF-5 release.yml
    participant W6 as WF-6 deploy-staging.yml
    participant W7 as WF-7 deploy-prod.yml
    participant W14 as WF-14 version-bump.yml
    participant Compose as Docker Compose (LOCK-CI-12)

    Dev->>GH: PR / push
    GH->>W1: trigger ci.yml
    par Stage 1 병렬
        W1->>W3: workflow_call lint.yml
        W1->>W2: workflow_call test.yml
        W1->>W8: workflow_call security.yml
    end
    W3-->>W1: lint result
    W2-->>W1: test + coverage
    W8-->>W1: security result
    W1->>W4: workflow_call build-tauri.yml (dry-run)
    W4-->>W1: build-check result
    W1-->>GH: status-check aggregated
    Dev->>GH: tag v1.2.3 push
    GH->>W5: trigger release.yml
    W5->>W14: changelog (git-cliff)
    W5->>W4: workflow_call build-tauri.yml (release_mode=true)
    W4-->>W5: signed artifacts (4 targets)
    W5-->>GH: GitHub Release + Tauri binaries upload
    W5-->>GH: GHCR push (V2+)
    GH->>W6: workflow_run(Release completed) → auto chain
    W6->>Compose: SSH docker compose up -d
    Compose-->>W6: health OK
    W6-->>Dev: Slack notify (staging)
    Dev->>GH: workflow_dispatch WF-7 (manual approval)
    GH->>W7: environment:production gate
    W7->>Compose: docker compose up -d (prod)
    Compose-->>W7: health OK
    W7-->>Dev: Slack notify (prod)
```

---

## 9. End-to-end 파이프라인 데이터 흐름도 (Mermaid)

```mermaid
flowchart LR
    subgraph Source["Source Tier"]
        PR[PR / push] --> B[브랜치 / 태그 판별]
    end

    subgraph CI["CI Tier — 01_ci-workflows/"]
        B --> W1(WF-1 ci.yml)
        W1 --> W3(WF-3 lint)
        W1 --> W2(WF-2 test)
        W1 --> W4(WF-4 build-tauri dry)
        W1 --> W10(WF-10 docs)
        W1 --> W12(WF-12 e2e)
        W1 --> W9(WF-9 benchmark)
        W13(WF-13 nightly) -.cron.-> W2
        W13 -.cron.-> W9
    end

    subgraph Security["Security Tier — 03_security-scanning/"]
        W1 --> W8(WF-8 security)
        W8 --> W11(WF-11 dep-check)
    end

    subgraph Release["Release Tier — 05_release-management/"]
        T[tag v*] --> W14(WF-14 version-bump)
        W14 --> W5(WF-5 release)
        W5 --> W4R(WF-4 build-tauri release)
        W4R --> ART[Tauri signed artifacts 4 targets]
        W5 --> GHCR[GHCR Docker push V2+]
    end

    subgraph CD["CD Tier — 02_cd-workflows/"]
        W5 --> W6(WF-6 deploy-staging)
        W6 --> Compose1[Docker Compose staging]
        W6 -.smoke pass.-> W7(WF-7 deploy-prod)
        W7 --> Compose2[Docker Compose prod V2]
        W7 -.V3.-> K8s[Helm / ArgoCD prod V3]
    end

    Compose1 --> S1[orange-core + blue-nodes + api-gateway + postgres + qdrant + neo4j (6 서비스)]
    Compose2 --> S2[동일 6 서비스 prod app tier replicas=3]
    K8s --> S3[vamos-* Deployments + HPA]

    style W1 fill:#ffe4b5
    style W5 fill:#ffb6c1
    style Compose1 fill:#98fb98
    style Compose2 fill:#98fb98
    style K8s fill:#87ceeb
```

---

## 10. Phase별 복구 전략 (정규화 충돌 시)

본 문서 자체가 매핑 문서이므로 런타임 에러는 없으나, **정규화 재검증 시** 발생할 수 있는 정합성 손실에 대한 복구 경로를 정의한다.

```mermaid
flowchart TD
  P1[Phase 1: PHASE_B6 YAML 블록 추출] -->|블록 누락 탐지| P1R[grep '^```yaml' 재실행, 라인 오프셋 재계산]
  P1 -->|PHASE_B6 버전 변경| P1E[CONFLICT_LOG 신규 등재 → 재정규화]
  P2[Phase 2: WF 파일 매핑] -->|WF 파일 누락| P2R[P1-1 산출물 재확인, 14 WF 존재 검증]
  P2 -->|변형 근거 불명| P2R2[상세명세 ↔ PHASE_B6 대조 후 §9.1 우선순위 재적용]
  P3[Phase 3: 변형 기록] -->|변형 미기록| P3R[본 문서 §3 테이블에 행 추가]
  P3 -->|LOCK 위반 탐지| P3E[LOCK_CHANGE_NEEDED 마커 → 사람 결정 대기]
  P4[Phase 4: CONFLICT 등재] -->|후보 누락| P4R[§7 재검토, step 7 에서 정식 등재]
  P4 -->|판정 불가| P4E[OPEN 상태 유지, Phase 2 재검토]
```

### 10.1 다운그레이드 confidence penalty 표

| 사례 | penalty | 게이트 영향 |
|------|---------|------------|
| PHASE_B6 YAML 블록 매핑 누락 (≤2건) | −5% | 게이트 통과 (경고) |
| PHASE_B6 YAML 블록 매핑 누락 (>2건) | −15% | G1 게이트 재검증 필요 |
| CONFLICT 등재 누락 (≤1건) | −5% | 게이트 통과 |
| CONFLICT 등재 누락 (>1건) | −15% | step 7 전 수동 검토 |
| LOCK-CI-06 / LOCK-CI-12 변형 근거 불명 | −20% | LOCK_CHANGE_NEEDED 필수 |
| WF 본문과 본 문서 §3 테이블 불일치 | −10% | 재정규화 필요 |
| V1/V2/V3 진화 테이블 오류 | −5% | 경고, Phase 2 에서 보강 |

---

## 11. 에스컬레이션 페이로드 구조 (R-01-8 / I-20 경유)

본 문서가 CI/CD 런타임 에러를 포함하지 않으므로, **정규화 재검증 실패 시** (예: step 6 재검증에서 매핑 누락 탐지) 에스컬레이션 데이터 구조만 정의한다. 실제 에스컬레이션 수신자는 Phase 2 (P2-1/P2-2) 의 담당 세션이다.

```python
# 정규화 재검증 에스컬레이션 페이로드
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Any

@dataclass
class NormalizationEscalationPayload:
    source_engine: Literal["phase_b6_yaml_normalization.md"]
    error_code: Literal[
        "PHASE_B6_BLOCK_MISSING",          # PHASE_B6 YAML 블록 매핑 누락
        "WF_MAPPING_MISMATCH",             # WF 파일 본문과 §3 테이블 불일치
        "LOCK_VARIANT_UNJUSTIFIED",        # LOCK-CI-06/12 변형 근거 불명
        "CONFLICT_UNDOCUMENTED",           # CONFLICT 후보 누락
        "VERSION_EVOLUTION_ERROR"          # V1/V2/V3 진화 테이블 오류
    ]
    original_request: dict[str, Any] = field(default_factory=dict)
    partial_result: dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    affected_wf: list[str] = field(default_factory=list)          # 예: ["WF-4", "WF-6"]
    affected_lock: list[str] = field(default_factory=list)        # 예: ["LOCK-CI-06"]
    confidence_penalty: float = 0.0
    recovery_strategy: Literal[
        "regrep", "reread_wf", "reload_phase_b6",
        "conflict_register", "lock_change_request",
        "escalate_human"
    ] = "regrep"
```

---

## 12. 로깅 포맷 (R-01-7 structured JSON)

본 문서는 정적 매핑 문서이므로 런타임 로그는 없으나, **정규화 재검증 스크립트** (예: `scripts/verify_normalization.py` — Phase 2 P2-0 이월 후보) 가 생성할 로그 포맷을 정의한다.

```json
{
  "trace_id": "norm-verify-<yyyymmdd>-<seq>",
  "error": {
    "code": "PHASE_B6_BLOCK_MISSING|WF_MAPPING_MISMATCH|LOCK_VARIANT_UNJUSTIFIED|CONFLICT_UNDOCUMENTED|VERSION_EVOLUTION_ERROR",
    "source_block": "Y-09",
    "target_wf": "WF-4_build-tauri.md",
    "line_range": "540-636",
    "severity": "HIGH|MEDIUM|LOW"
  },
  "context": {
    "document": "02_cd-workflows/phase_b6_yaml_normalization.md",
    "session": "P1-4",
    "phase_b6_version": "v1.0.2",
    "wf_files_scanned": 14,
    "yaml_blocks_expected": 22,
    "yaml_blocks_matched": 22,
    "lock_affected": ["LOCK-CI-06"]
  },
  "recovery": {
    "retry_count": 0,
    "strategy": "reread_wf",
    "confidence_penalty": 0.10,
    "escalated": false,
    "fallback_action": "manual_review"
  }
}
```

---

## 13. Phase 2 통합 테스트 시나리오 (14건)

| # | 시나리오 | 주입 방법 | 기대 결과 |
|---|---------|---------|----------|
| T-1 | PHASE_B6 YAML 블록 22건 전수 존재 | `grep -cn '^```yaml' PHASE_B6_CICD_PIPELINE.md` | 22 (§2 인벤토리 일치) |
| T-2 | 통합 ci.yml (Y-20) 이 WF-1 에 반영 | WF-1 §2 트리거 diff PHASE_B6 §8 | reusable 변형 근거 §3.1 에 기록, 기능 동치 |
| T-3 | LOCK-CI-06 Tauri 4 target 일치 | WF-4 §3 매트릭스 vs §6.1 정본 매트릭스 | 4/4 target 일치, platform/target/sign 필드 동일 |
| T-4 | LOCK-CI-12 6 서비스 (app tier: orange-core/blue-nodes/api-gateway + data tier: postgres/qdrant/neo4j) 존재 | §5.2 docker-compose.yml service key 전수 추출 | 6 서비스 존재, api-gateway 복원 확인 |
| T-5 | TAURI_SIGNING_* 본문 누락 탐지 | WF-4 §5.1 시크릿 테이블 grep | 누락 확인 → C-06 후보 보고 |
| T-6 | V1 → V2 전환 시 신규 YAML 정합 | §4.1 V1 컬럼 '❌' 행 vs V2 컬럼 '✅' 행 diff | Y-11/Y-14/Y-15/Y-15b/Y-17(trivy) 5건 진화 포인트 |
| T-7 | V2 → V3 전환 시 deprecated 탐지 | §4.1 V3 컬럼 '⏳ deprecated' 행 | Y-15/Y-15b deprecated, Y-16 신규 |
| T-8 | pnpm vs npm 변형 (C-02 연장) | WF-2/WF-3 `pnpm-lock.yaml` hash vs PHASE_B6 `npm` | sot 2/ 우선, §3.1/§7 C-07 후보 기록 |
| T-9 | Postgres test 비밀번호 불일치 (C-08) | PHASE_B6 §3.1 `test_password` vs §8 `test_pass` | 내부 모순 확인, C-08 후보 기록 |
| T-10 | Docker 서비스명 접두사 차이 (C-09) | PHASE_B6 §4.3 `vamos-*` vs §6.1 `orange-core` | 명명 규칙 이원화 유지, C-09 후보 기록 |
| T-11 | workflow_run auto-chain (§5.1) 동작 | release 성공 시 WF-6 auto trigger | WF-6 실행, `conclusion='success'` 분기 |
| T-12 | prod 수동 승인 게이트 (LOCK-CI-10) | WF-7 workflow_dispatch + environment:production | GitHub Environment Protection Rules 적용, 수동 승인 대기 |
| T-13 | rollback step 동작 (§5.1 Rollback on failure) | smoke test 실패 주입 | `.env.prev` 에서 이전 VAMOS_VERSION 복원, 재배포 |
| T-14 | V3 nightly.yml 스텁 vs 완전체 diff | WF-13 §2 트리거 vs Phase 2 P2-4 산출물 | cron 일치, job 정의는 스텁 (Phase 2 예정) |

---

## 14. 세션 간 인터페이스 cross-check

| 선행 세션 | 산출물 | 본 세션 참조 | 불일치 |
|---------|--------|------------|-------|
| P1-1 | `01~05_*/WF-*.md` (14개) | §2 인벤토리 / §3 매핑 전수 | 0 건 |
| P1-2 | `03_security-scanning/secrets_mapping.md` | §4.2 V1→V2/V2→V3 시크릿 진화 | 0 건 (secrets_mapping.md §6 전환 테이블 준수) |
| P1-3 | `04_cache-strategy/cache_strategy_detail.md` | §3.1 캐시 변형 3건 (`.venv` / `uv-` / `pnpm-e2e-`) | 0 건 (변형 3건 유지) |

### 14.1 P1-1 cross-check 상세

| WF 파일 | 본 문서 §3 행 | P1-1 파일 실제 상태 | 정합 |
|---------|-------------|------------------|------|
| WF-1_ci.md | §3.1 Y-20 (reusable 변형) | 7-job 구조 (setup/lint/test-python/test-rust/security/build-check/status-check) | ✅ |
| WF-2_test.md | §3.1 Y-04~Y-08 (매트릭스 확장 + pnpm) | 매트릭스 Python 3.11/3.12 × OS 3종, pnpm 기반 frontend-tests | ✅ |
| WF-3_lint.md | §3.1 Y-01~Y-03 (Python/Rust/Frontend 3파트) | 3 파트 분리 존재, pnpm/uv 병행 | ✅ |
| WF-4_build-tauri.md | §3.1 Y-09 (4 target + sign + artifact 필드명 단축) | 4 target 매트릭스, sign 필드 존재, artifact 필드 존재 | ✅ (TAURI_SIGNING_* 본문 누락만 C-06) |
| WF-5_release.md | §3.4 Y-10/Y-13/Y-14 (reusable 변형 + push-docker) | release job + python dist + push-docker 존재 | ✅ |
| WF-6_deploy-staging.md | §3.2 Y-15 (workflow_run + staging 전용) | workflow_run(Release completed) + deploy-compose job 존재 | ✅ |
| WF-7_deploy-prod.md | §3.2 Y-15/Y-16 (prod 수동 승인 + K8s 스텁) | workflow_dispatch + environment:production + K8s 스텁 | ✅ |
| WF-8_security-scan.md | §3.3 Y-17/Y-18/Y-19 (trivy/trufflehog/license) | 3 파트 존재 | ✅ |
| WF-9_benchmark.md | §3.1 (독립 구성) | 상세명세 WF-9 기반 자체 구성 | ✅ |
| WF-10_docs-build.md | §3.1 (독립 구성) | 상세명세 WF-10 기반 자체 구성 | ✅ |
| WF-11_dependency-check.md | §3.3 Y-17 (continue-on-error 강화) | HIGH/CRITICAL 0건 게이트 존재 | ✅ |
| WF-12_e2e-test.md | §3.1 (독립 구성, Y-21 언급만) | Playwright + Tauri WebDriver 구성 | ✅ |
| WF-13_nightly.md | §3.1 Y-21 (스텁) | cron '0 3 * * *' + 스텁 | ✅ |
| WF-14_version-bump.md | §3.4 Y-12 (changelog + cliff.toml) | git-cliff + cliff.toml 존재 | ✅ |

**총 14/14 WF 정합 확인, 불일치 0 건** (C-06 TAURI_SIGNING_* 본문 누락은 기존 P1-2 탐지건으로 본 세션 CONFLICT_CANDIDATE 연장).

---

## 15. LOCK 준수 체크리스트

- [x] LOCK-CI-01 (14개 WF 목록) — 본 문서 §3 에서 14 WF 전수 매핑 ✅
- [x] LOCK-CI-06 (Tauri 4플랫폼) — §6 정본 전개 완료 ✅
- [x] LOCK-CI-11 (concurrency) — §5.1 `cancel-in-progress: false` + WF-1 `cancel-in-progress: true` 분리 준수 ✅
- [x] LOCK-CI-12 (Docker Compose V2 6 서비스 — app tier 3 + data tier 3) — §5.2 api-gateway 복원 후 6 서비스 전개 완료 ✅
- [ ] LOCK-CI-07 (코드 서명) — §6.1 `sign` 필드 명시, 본문 TAURI_SIGNING_* 누락은 C-06 후보 (step 7 처리)
- [x] LOCK-CI-10 (프로덕션 승인) — §5.1 `environment: production` 게이트 유지 ✅

---

## 16. Phase 2 이월 항목

| # | 항목 | 담당 세션 | 근거 |
|---|------|---------|------|
| F-11 | `deploy/docker-compose.staging.yml` / `.prod.yml` overlay 완전체 작성 | P2-1 | §5.3 |
| F-12 | V3 K8s Helm chart + ArgoCD Application CRD 완전체 | P2-2 | §2 Y-16, §3.2 |
| F-13 | nightly.yml (V3) 완전체 (full-unit/integration/e2e/benchmark/security-audit jobs) | P2-4 | §2 Y-21, §3.1 |
| F-14 | `scripts/verify_normalization.py` 자동 재검증 스크립트 | P2-0 (재검증 자동화) | §10, §12 |
| F-15 | LOCK-CI-06 V3 5 target 확장 (aarch64-linux-gnu 추가) | P2-2 | §6.2 **[LOCK_UNCHANGED] DEFERRED_TO_PHASE3** (2026-04-24 P2-2 결정 옵션 B 채택, 4-target 보존, 사유 5건 — Linux ARM64 desktop 수요 미확인 + GitHub runner 제약 + ROI + cascade 부담 + 자동 RESOLVE 금지 원칙) |
| F-16 | WF-4/WF-5 본문에 TAURI_SIGNING_* 참조 보강 | P1-1 step 7 (C-06) | §7 C-06 후보 |
| F-17 | CONFLICT_LOG 에 C-05~C-09 정식 등재 | P1-4 step 7 | §7 |
| F-18 | PHASE_B6 §8 Y-20 통합 ci.yml 내부 모순 (test_pass vs test_password) 상류 PR | PHASE_B6 상류 수정 (sot 정본) | §7 C-08 |

---

## 17. 이력

| 버전 | 날짜 | 변경 내용 | 작성 |
|------|------|---------|------|
| v1 | 2026-04-11 | P1-4 초기 작성 (step 1). PHASE_B6 YAML 인벤토리, 14 WF 역매핑, V1/V2/V3 진화 경로, LOCK-CI-06/12 정본 전개, CONFLICT 후보 5건 (C-05~C-09), Phase 2 테스트 14건, P1-1/P1-2/P1-3 cross-check 0건 불일치, F-11~F-18 이월 8건 | P1-4 세션 |
| v1.1 | 2026-04-11 | P1-4 step 2 재검증 1차. (a) PHASE_B6 yaml 코드 펜스 정확 카운트 **21→22** 보정 (§1.1 목적 / §1.2 범위 / §2 header / §2 footer / §13 T-1 / §12 log 예시, `yaml_blocks_matched` 20→22). (b) §1.2 §5 (릴리스 4건→3건) §6 (배포 2건→3건) 카테고리 카운트 실제 인벤토리와 정렬. (c) LOCK-CI-12 정본 서비스 수 혼선 수정 — "3서비스" 모호한 표현을 **"6 서비스 = app tier 3 + data tier 3"** 으로 명확화 (§1.2, §2 Y-11/Y-15b, §3.4 Y-14, §4.1 Y-11/Y-15b, §5.2 header/narrative/변형 근거, §7 C-05, §8 Compose1/Compose2, §13 T-4, §15 LOCK 체크리스트). (d) Y-05/Y-06/Y-07/Y-08 PHASE_B6 라인 범위 오차 수정 (277–354→277–339, 357–408→357–407, 411–479→411–446, 482–535→482–524, `.toml` 블록이 끼어 있던 범위를 yaml 종료 펜스로 재계산). (e) §5.2 `api-gateway 가 blue-nodes 로 대체` 모순 서술 삭제, PHASE_B6 내부 모순 (§4.3/§5.4/§8 에서 api-gateway 빌드·푸시 vs §6.1 compose 누락) 근거 추가. 변경 라인 수 ≈22, 내용 의미 변경 없음 (정합성 강화) | P1-4 step 2 재검증 1차 |
| v1.2 | 2026-04-11 | P1-4 step 2 재검증 2차. (a) §6.1 Tauri 매트릭스 정본을 WF-4_build-tauri.md §3 실제 본문과 정확 일치시킴 — `platform:` → `os:` 키명 통일, artifact 파일명을 `vamos_amd64.AppImage` / `vamos_x64.msi` / `vamos_arm64.dmg` / `vamos_x64.dmg` (WF-4 정본 단형) 로 정정. (b) §3.1 WF-4 행의 artifact 필드 서술을 `vamos_<arch>.<ext>` 단형으로 정렬, `os:` 키 통일 명시 추가. (c) §5.1 정본 YAML 블록 앞에 WF-6(자동 체인+수동) / WF-7(수동 전용) 분기 명시 + `workflow_run` 이벤트에서 `inputs.version` 부재 시 prepare job 에서 도출해야 함을 운영 주의사항으로 추가. 변경 라인 수 ≈12, 내용 의미 변경 없음 (WF-4 정본과 정확 정합). | P1-4 step 2 재검증 2차 |
| v1.3 | 2026-04-24 | **STAGE 7 Phase 2 STEP_B step 7 갱신**. (a) §6.2 [LOCK_CHANGE_NEEDED] → **[LOCK_UNCHANGED] DEFERRED_TO_PHASE3** 마커 전환 (P2-2 결정 옵션 B 채택, 4-target 보존, 사유 5건). (b) §16 F-15 row 상태 필드 `[LOCK_CHANGE_NEEDED]` → **[LOCK_UNCHANGED] DEFERRED_TO_PHASE3** 동기화. (c) F-11 (overlay 완전체) 는 P2-1 V2 `02_cd-workflows/docker_compose_pipeline.md` §3.4 + §4.1 deploy-v2.yml 환경별 분기로 **실체화 완료** (별도 status 필드 갱신 없음, 실체화는 P2-1 V2 산출물에서 확인). 변경 라인 수 ≈3, LOCK-CI-06 정본 변경 0, V1 본문 의미 변경 없음 (sandbox-only narrative 메타데이터 갱신). | Phase 2 STEP_B step 7 (parent-executed) |

---
