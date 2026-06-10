# Secrets Mapping — CI/CD Pipeline 통합 시크릿 관리

> **도메인**: 4-2 CI/CD Pipeline
> **세션 산출물**: P1-2 (시크릿 매핑 완성)
> **정본 범위**: 14개 워크플로우(WF-1~WF-14)에서 참조되는 GitHub Actions 시크릿 전수 매핑
> **작성일**: 2026-04-11
> **버전**: v1.1 (P1-2 step2 미세 재검증 반영)
> **상태**: L2 (Phase 1 산출물)

---

## §0. Purpose / Scope

### 0.1 Purpose
이 문서는 VAMOS 14개 GitHub Actions 워크플로우(WF-1~WF-14)가 참조하는 모든 시크릿을 단일 장소에서 전수 관리하는 정본이다.
개별 WF 상세 파일(P1-1 산출물)에 산재된 시크릿 참조를 집계·정규화하여 다음을 보장한다.

- (a) **전수 매핑**: 각 시크릿이 어느 WF의 어느 Job에서 어떤 용도로 사용되는지 추적
- (b) **거버넌스 준수**: R-15-2 (하드코딩 금지), R-T4-2 (시크릿 하드코딩 금지, 접근 제어 명시) 준수 체크
- (c) **로테이션 정책**: 각 시크릿의 로테이션 주기 및 담당자 명시
- (d) **LOCK 충족**: LOCK-CI-07 (코드 서명 3종), LOCK-CI-09 (CVE 정책), LOCK-CI-10 (프로덕션 2인 승인) 관련 시크릿 명시
- (e) **게이트 충족**: Phase 1 G1 게이트 "시크릿 12+개 전수 매핑" 충족

### 0.2 Scope
- **포함**:
  - GitHub Actions `secrets.*` / `vars.*` 으로 참조되는 모든 식별자
  - V1(로컬 MVP) 단계에서 이미 사용되는 시크릿 + V2(서버) 확장 시크릿
  - 코드 서명, 배포, 모니터링, 알림, 보안 스캔, 릴리스 시크릿
- **제외**:
  - V3(K8s/ArgoCD) 전용 시크릿 상세(Phase 2에서 확정) — 본 문서에서는 `KUBECONFIG` 등 §A.3에서 언급된 V3 후보만 Stub 형태로 기재
  - Runtime 시크릿(애플리케이션 런타임) — 본 문서는 **CI/CD 빌드/배포 시점** 시크릿만 커버

---

## §1. 교차 참조 블록

| 정본 문서 | 섹션 | 참조 이유 |
|-----------|------|-----------|
| `CICD_PIPELINE_구조화_종합계획서.md` | §3.4 LOCK 보호 항목 | LOCK-CI-07/08/09/10 관련 시크릿 식별 |
| `CICD_PIPELINE_구조화_종합계획서.md` | §4.3 도메인 고유 규칙 (R-15-2) | 시크릿 하드코딩 금지 |
| `CICD_PIPELINE_구조화_종합계획서.md` | §A.3 시크릿 매핑 테이블 | 초기 시크릿 목록(23건) 정본 |
| `CICD_PIPELINE_상세명세.md` | WF-1~WF-14 | 기존 WF별 시크릿 참조 |
| `D:\VAMOS\docs\sot\PHASE_B6_CICD_PIPELINE.md` | 전체 | 전략 정본, 시크릿 정책 원본 |
| `01_ci-workflows/WF-1_ci.md` ~ `05_release-management/WF-14_version-bump.md` | 각 WF §시크릿 섹션 | P1-1 산출물, 집계 대상 |
| `_index.md` (03_security-scanning) | §시크릿 매핑 | Stub 시크릿 매핑 (본 문서로 대체) |
| `D:\VAMOS\docs\sot 2\0-0_Governance-Rules-Meta` | R1~R11 | 글로벌 거버넌스 규칙 |

---

## §2. 시크릿 전수 매핑 테이블

### 2.1 Master Table

각 시크릿의 정본 정의 (시크릿명 / 용도 / 사용 WF / Job / 로테이션 주기 / 필수 여부 / 카테고리 / LOCK 매핑).

| # | 시크릿명 | 카테고리 | 용도 | 사용 WF | 사용 Job | 로테이션 주기 | 필수 | LOCK |
|---|----------|----------|------|---------|---------|--------------|------|------|
| 1 | `GITHUB_TOKEN` | Platform | GitHub API (checkout/PR comment/status/artifact/issue/SARIF) | WF-1,2,3,5,8,9,10,11,12,13,14 | 전체 대부분 | 자동 (per-run) | ✅ | - |
| 2 | `CODECOV_TOKEN` | Monitoring | Codecov 커버리지 업로드 | WF-1 (호출체인), WF-2 | coverage-report | 180일 | ✅ | LOCK-CI-03 |
| 3 | `SLACK_WEBHOOK_URL` | Notification | Slack 알림 (빌드/배포/회귀/실패/주간 요약) | WF-6, WF-7, WF-9, WF-11, WF-13 | notify, deploy-compose, weekly-summary | 365일 | ✅ | - |
| 4 | `APPLE_CERTIFICATE` | CodeSign-macOS | Developer ID Application 인증서 (Base64 .p12) | WF-4 | build (macOS) | 365일 (인증서 만료일) | ✅ | LOCK-CI-07 |
| 5 | `APPLE_CERTIFICATE_PASSWORD` | CodeSign-macOS | .p12 비밀번호 | WF-4 | build (macOS) | 365일 (인증서 교체 시) | ✅ | LOCK-CI-07 |
| 6 | `APPLE_ID` | CodeSign-macOS | Notarization Apple ID | WF-4 | build (macOS notarize) | 365일 | ✅ | LOCK-CI-07 |
| 7 | `APPLE_TEAM_ID` | CodeSign-macOS | Notarization Team ID | WF-4 | build (macOS notarize) | 변경 없음 (조직 ID) | ✅ | LOCK-CI-07 |
| 8 | `APPLE_INSTALLER_CERT` | CodeSign-macOS | Installer 서명 인증서 | WF-4 | build (macOS installer) | 365일 | 선택 | LOCK-CI-07 |
| 9 | `WINDOWS_PFX` | CodeSign-Windows | EV Code Signing (Base64 .pfx) | WF-4 | build (Windows) | 365일 (EV 인증서 만료일) | ✅ | LOCK-CI-07 |
| 10 | `WINDOWS_PFX_PASSWORD` | CodeSign-Windows | .pfx 비밀번호 | WF-4 | build (Windows) | 365일 | ✅ | LOCK-CI-07 |
| 11 | `GPG_PRIVATE_KEY` | CodeSign-Linux | Linux GPG 서명 키 | WF-4, WF-5 | build (Linux), release build | 730일 | ✅ | LOCK-CI-07 |
| 12 | `AWS_ACCESS_KEY_ID` | Deploy-V2 | S3/Registry Access Key (업데이트 서버, Docker registry) | WF-6, WF-7 | deploy-update-server, deploy-compose, canary-deploy, full-deploy | 90일 | ✅ | LOCK-CI-10 |
| 13 | `AWS_SECRET_ACCESS_KEY` | Deploy-V2 | S3/Registry Secret Key | WF-6, WF-7 | 동일 (12번) | 90일 | ✅ | LOCK-CI-10 |
| 14 | `AWS_REGION` | Deploy-V2 | AWS 리전 (설정 값) | WF-6 | deploy-update-server, deploy-compose | 변경 없음 | ✅ | - |
| 15 | `STAGING_SSH_KEY` | Deploy-V2 | Staging host SSH private key | WF-6 | deploy-compose (host SSH) | 90일 | ✅ | - |
| 16 | `STAGING_HOST` | Deploy-V2 | Staging host FQDN | WF-6 | deploy-compose | 변경 없음 | ✅ | - |
| 17 | `PROD_SSH_KEY` | Deploy-V2 | Production host SSH private key | WF-7 | compose deploy (canary, full) | 90일 | ✅ | LOCK-CI-10 |
| 18 | `PROD_HOST_LIST` | Deploy-V2 | Production host 리스트 (canary 노드 선택) | WF-7 | compose deploy | 변경 없음 | ✅ | LOCK-CI-10 |
| 19 | `TF_API_TOKEN` | Deploy-V2 | Terraform Cloud API Token (인프라 적용) | WF-6, WF-7 | deploy-api-gateway, terraform apply | 180일 | ✅ | LOCK-CI-10 |
| 20 | `CLOUDFLARE_API_TOKEN` | Deploy-Docs | Cloudflare Pages 배포 (docs) | WF-6, WF-10 | deploy-docs-staging, deploy-pages | 180일 | ✅ | - |
| 21 | `DATADOG_API_KEY` | Monitoring | Datadog 메트릭 전송 (canary 모니터링) | WF-7 | canary-monitor, monitor-30min | 365일 | ✅ | LOCK-CI-10 |
| 22 | `PAGERDUTY_INTEGRATION_KEY` | Monitoring | PagerDuty 알림 (롤백/장애) | WF-7 | notify (롤백 시) | 365일 | ✅ | LOCK-CI-10 |
| 23 | `SEMGREP_APP_TOKEN` | Security-Scan | Semgrep Cloud 연동 (SAST) | WF-8 | sast | 365일 | 선택 | LOCK-CI-08 |
| 24 | `TRIVY_DB_REPOSITORY_TOKEN` | Security-Scan | GHCR trivy DB mirror (rate limit 회피) | WF-8 | container-scan | 180일 | 선택 | LOCK-CI-08 |
| 25 | `COSIGN_KEY` | Release-Sign | Cosign private key (keyless 사용 시 불필요) | WF-5 | cosign-sign | 365일 | 선택 | LOCK-CI-07 |
| 26 | `COSIGN_PASSWORD` | Release-Sign | Cosign key password | WF-5 | cosign-sign | 365일 | 선택 | LOCK-CI-07 |
| 27 | `BOT_SIGNING_KEY` | Release-Sign | version-bump 커밋 GPG 서명 (선택) | WF-14 | commit signing | 730일 | 선택 | - |
| 28 | `E2E_TEST_API_KEY` | Test-E2E | 테스트 API mock 서버 인증 | WF-12 | e2e-test | 180일 | 선택 | - |
| 29 | `TAURI_SIGNING_PRIVATE_KEY` | App-Update | Tauri 앱 서명 (auto-updater) | WF-4, WF-5 | build (release_mode), create-release | 730일 | ✅ | LOCK-CI-07 |
| 30 | `TAURI_SIGNING_PRIVATE_KEY_PASSWORD` | App-Update | Tauri 앱 서명 키 비밀번호 | WF-4, WF-5 | 동일 (29번) | 730일 | ✅ | LOCK-CI-07 |
| 31 | `DISCORD_WEBHOOK_URL` | Notification | Discord 릴리스 알림 (선택, Slack 보조 채널) | WF-5 | notify | 365일 | 선택 | - |
| 32 | `CLOUDFLARE_ACCOUNT_ID` | Deploy-Docs | Cloudflare Pages 계정 식별자 (배포 context 분리) | WF-10 | deploy-pages | 변경 없음 (조직 ID) | ✅ | - |

> **주의 (TAURI #29/#30 출처 정합성)**: `TAURI_SIGNING_PRIVATE_KEY` / `TAURI_SIGNING_PRIVATE_KEY_PASSWORD` 는 §A.3 (계획서) 및 `05_release-management/_index.md` §코드 서명 섹션에서 `build-tauri.yml` + `release.yml` 용도로 지정된 정본이다. 그러나 P1-1 에서 생성된 `01_ci-workflows/WF-4_build-tauri.md` 및 `05_release-management/WF-5_release.md` 본문 §시크릿 섹션에는 현재 이 두 시크릿이 명시되지 않았다. 본 문서는 §A.3 정본 및 LOCK-CI-07 (코드 서명 정책) 준수를 우선하여 master table 에 유지하며, P1-1 WF-4/WF-5 본문에 누락된 참조는 §10.1 CONFLICT 후보로 보고한다 (P1-1 step 7 보강 대상).

### 2.2 §A.3 정본 Diff 및 이월 정리

계획서 §A.3 최초 정본 23건 대비 본 문서에서 확정된 32건 (v1.1) 의 차이와 이유를 전수 정리한다.

| § | 이월 유형 | §A.3 항목 | 본 문서 처리 | 근거 |
|---|-----------|-----------|--------------|------|
| a | **세부화(+5)** | `APPLE_CERTIFICATE` (1건) | macOS 서명 5종으로 세부화 (#4~#8, `APPLE_INSTALLER_CERT` 추가) | WF-4 §5.1 |
| b | **세부화(+1)** | `WINDOWS_CERTIFICATE` | `WINDOWS_PFX`(파일) + `WINDOWS_PFX_PASSWORD` 로 명명 변경/분리 | WF-4 §5.1 |
| c | **신규(+1)** | 없음 | `PROD_HOST_LIST` 추가 (WF-7 canary 노드 선택) | WF-7 §7 |
| d | **신규(+1)** | 없음 | `AWS_REGION` 추가 (WF-6 설정 값) | WF-6 §6 |
| e | **신규(+1)** | 없음 | `STAGING_HOST` 추가 (WF-6 FQDN) | WF-6 §6 |
| f | **신규(+1)** | 없음 | `TF_API_TOKEN` 추가 (WF-6/7 Terraform apply) | WF-6 §6, WF-7 §7 |
| g | **신규(+1)** | 없음 | `DATADOG_API_KEY` 추가 (WF-7 canary 모니터링) | WF-7 §7 |
| h | **신규(+1)** | 없음 | `PAGERDUTY_INTEGRATION_KEY` 추가 (WF-7 롤백 알림) | WF-7 §7 |
| i | **신규(+1)** | 없음 | `TRIVY_DB_REPOSITORY_TOKEN` 추가 (WF-8 container-scan) | WF-8 §6 |
| j | **신규(+1)** | 없음 | `COSIGN_KEY` / `COSIGN_PASSWORD` 추가 (WF-5 cosign-sign) | WF-5 §7 |
| k | **신규(+1)** | 없음 | `BOT_SIGNING_KEY` 추가 (WF-14 커밋 서명) | WF-14 §4 |
| l | **신규(+1)** | 없음 | `E2E_TEST_API_KEY` 추가 (WF-12 mock API) | WF-12 §6 |
| m | **신규(+1)** | 없음 | `GITHUB_TOKEN` 추가 (플랫폼 제공 시크릿, R-T4-2 접근 제어 명시 목적) | WF-1/2/3/5/8/9/10/11/12/13/14 |
| m-1 | **신규(+1)** | 없음 | `DISCORD_WEBHOOK_URL` 추가 (WF-5 notify job, Slack 보조) | WF-5 §7 |
| m-2 | **신규(+1)** | 없음 | `CLOUDFLARE_ACCOUNT_ID` 추가 (WF-10 deploy-pages, Cloudflare API 필수 context) | WF-10 §5 |
| m-3 | **커버리지 확장** | 없음 | `SLACK_WEBHOOK_URL` 사용 WF 에 WF-11 (주간 요약) 포함 — P1-1 WF-11 §5 반영 | WF-11 §5 |
| n | **V2+ 보류** | `POSTGRES_USER` / `POSTGRES_PASSWORD` | 본 문서 v1 에서는 **런타임 시크릿** 으로 분류되어 Scope 제외 (§0.2) — V2 deploy YAML 정규화(1-4) 시 Stub 검토 | §A.3, WF-6/7 |
| o | **V2+ 보류** | `QDRANT_API_KEY` / `NEO4J_AUTH` / `OPENAI_API_KEY` | 동일 (런타임 시크릿, Scope 제외) — V2 deploy Phase 2-1 에서 재평가 | §A.3 |
| p | **V3 Stub** | `KUBECONFIG` (deploy-v3) | 본 문서 v1 에서는 §7 V3 Stub 섹션으로만 기재, 상세화는 Phase 2-2 V3 K8s 설계 세션에서 확정 | §A.3 |
| q | **Tauri 승격** | (§A.3 에 존재) `TAURI_SIGNING_PRIVATE_KEY` / `TAURI_SIGNING_PRIVATE_KEY_PASSWORD` | 본 문서 #29/#30 에서 유지, LOCK-CI-07 매핑 승격 | §A.3, WF-4/5 |

이월 합계:
- §A.3 원본 23건 → v1 에서 `POSTGRES_USER/PW`, `QDRANT_API_KEY`, `NEO4J_AUTH`, `OPENAI_API_KEY`, `KUBECONFIG` 5건을 **Scope 제외 / V2+ 보류**로 분리 → 잔여 18건.
- 잔여 18건에 WF 상세 파일(P1-1)에서 발견된 신규 시크릿을 포함 → **v1 정본 30건**.
- v1.1 (step2 재검증) 에서 누락 탐지 2건 (`DISCORD_WEBHOOK_URL`, `CLOUDFLARE_ACCOUNT_ID`) 추가 → **v1.1 정본 32건**.
- 보류 6건(POSTGRES/QDRANT/NEO4J/OPENAI/KUBECONFIG) 은 §7 V2+/V3 Stub 섹션에서 별도 관리.

> **주의**: §A.3 정본은 **계획서 문서**이므로 Phase 1 세션은 §A.3 자체를 수정하지 않는다. 본 문서 §2.1 은 §A.3 을 **WF 상세 산출물 기반으로 보강**하여 L2 정본화한 것이며, 향후 §A.3 과 본 문서 간 불일치가 해소될 필요가 있으면 CONFLICT 후보로 보고한다 (§10 참조).

---

## §3. 카테고리별 분류

### 3.1 Platform
- `GITHUB_TOKEN` — GitHub가 자동 주입, 수동 로테이션 없음

### 3.2 Monitoring
- `CODECOV_TOKEN`, `DATADOG_API_KEY`, `PAGERDUTY_INTEGRATION_KEY`

### 3.3 Notification
- `SLACK_WEBHOOK_URL`, `DISCORD_WEBHOOK_URL` (선택, WF-5 보조)

### 3.4 Code Signing (LOCK-CI-07)
- **macOS**: `APPLE_CERTIFICATE`, `APPLE_CERTIFICATE_PASSWORD`, `APPLE_ID`, `APPLE_TEAM_ID`, `APPLE_INSTALLER_CERT`
- **Windows**: `WINDOWS_PFX`, `WINDOWS_PFX_PASSWORD`
- **Linux**: `GPG_PRIVATE_KEY`
- **Tauri Updater**: `TAURI_SIGNING_PRIVATE_KEY`, `TAURI_SIGNING_PRIVATE_KEY_PASSWORD`
- **Release Cosign (선택)**: `COSIGN_KEY`, `COSIGN_PASSWORD`

### 3.5 Deploy V2 (LOCK-CI-10)
- **AWS**: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`
- **SSH**: `STAGING_SSH_KEY`, `STAGING_HOST`, `PROD_SSH_KEY`, `PROD_HOST_LIST`
- **Terraform**: `TF_API_TOKEN`
- **Docs (Cloudflare)**: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`

### 3.6 Security Scan (LOCK-CI-08/09)
- `SEMGREP_APP_TOKEN`, `TRIVY_DB_REPOSITORY_TOKEN`

### 3.7 Release
- `COSIGN_KEY`, `COSIGN_PASSWORD`, `BOT_SIGNING_KEY`, `TAURI_SIGNING_PRIVATE_KEY`, `TAURI_SIGNING_PRIVATE_KEY_PASSWORD`

### 3.8 Test
- `E2E_TEST_API_KEY`

---

## §4. WF → 시크릿 역매핑 (전수 커버리지)

각 워크플로우에서 참조되는 시크릿 목록 — 14개 WF 전수 커버 확인용.

| WF | 파일 | 참조 시크릿 | 개수 |
|----|------|-------------|------|
| WF-1 | `01_ci-workflows/WF-1_ci.md` | `GITHUB_TOKEN`, `CODECOV_TOKEN` (호출체인) | 2 |
| WF-2 | `01_ci-workflows/WF-2_test.md` | `GITHUB_TOKEN`, `CODECOV_TOKEN` | 2 |
| WF-3 | `01_ci-workflows/WF-3_lint.md` | `GITHUB_TOKEN` | 1 |
| WF-4 | `01_ci-workflows/WF-4_build-tauri.md` | `APPLE_CERTIFICATE`, `APPLE_CERTIFICATE_PASSWORD`, `APPLE_ID`, `APPLE_TEAM_ID`, `APPLE_INSTALLER_CERT`(선택), `WINDOWS_PFX`, `WINDOWS_PFX_PASSWORD`, `GPG_PRIVATE_KEY`, `TAURI_SIGNING_PRIVATE_KEY`★, `TAURI_SIGNING_PRIVATE_KEY_PASSWORD`★ | 10 |
| WF-5 | `05_release-management/WF-5_release.md` | `GITHUB_TOKEN`, `GPG_PRIVATE_KEY`, `COSIGN_KEY`(선택), `COSIGN_PASSWORD`(선택), `SLACK_WEBHOOK_URL`, `DISCORD_WEBHOOK_URL`(선택), `TAURI_SIGNING_PRIVATE_KEY`★, `TAURI_SIGNING_PRIVATE_KEY_PASSWORD`★ (+ WF-4 build 재사용 시 `APPLE_*` / `WINDOWS_PFX*` 상속) | 8 직접 / + 재사용 |
| WF-6 | `02_cd-workflows/WF-6_deploy-staging.md` | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `CLOUDFLARE_API_TOKEN`, `STAGING_SSH_KEY`, `STAGING_HOST`, `TF_API_TOKEN`, `SLACK_WEBHOOK_URL` | 8 |
| WF-7 | `02_cd-workflows/WF-7_deploy-prod.md` | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `PROD_SSH_KEY`, `PROD_HOST_LIST`, `TF_API_TOKEN`, `DATADOG_API_KEY`, `PAGERDUTY_INTEGRATION_KEY`, `SLACK_WEBHOOK_URL` | 8 |
| WF-8 | `03_security-scanning/WF-8_security-scan.md` | `SEMGREP_APP_TOKEN`, `GITHUB_TOKEN`, `TRIVY_DB_REPOSITORY_TOKEN` | 3 |
| WF-9 | `01_ci-workflows/WF-9_benchmark.md` | `GITHUB_TOKEN`, `SLACK_WEBHOOK_URL` | 2 |
| WF-10 | `01_ci-workflows/WF-10_docs-build.md` | `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`, `GITHUB_TOKEN` | 3 |
| WF-11 | `03_security-scanning/WF-11_dependency-check.md` | `GITHUB_TOKEN`, `SLACK_WEBHOOK_URL`(선택) | 2 |
| WF-12 | `01_ci-workflows/WF-12_e2e-test.md` | `GITHUB_TOKEN`, `E2E_TEST_API_KEY` | 2 |
| WF-13 | `01_ci-workflows/WF-13_nightly.md` | `SLACK_WEBHOOK_URL`, `GITHUB_TOKEN` | 2 |
| WF-14 | `05_release-management/WF-14_version-bump.md` | `GITHUB_TOKEN`, `BOT_SIGNING_KEY` | 2 |

**합계**: 고유 시크릿 **32건** (v1.1) / 총 직접 참조 55회 (WF-5 상속 분 별도) / 14 WF 전수 커버 (100%).

> **표기 규칙**: 이름 뒤 `★` 는 §A.3 (계획서) 정본에서 해당 WF 에 매핑되어 있으나 P1-1 WF 상세 파일 본문에는 명시 참조가 누락된 항목. §10.1 CONFLICT 후보로 보고 (P1-1 본문 보강 대상).

---

## §5. LOCK 매핑 검증

### 5.1 LOCK-CI-07 (코드 서명 정책 macOS/Windows/Linux)
- ✅ macOS: `APPLE_CERTIFICATE`, `APPLE_CERTIFICATE_PASSWORD`, `APPLE_ID`, `APPLE_TEAM_ID` (+ 선택 `APPLE_INSTALLER_CERT`) — 필수 4종 + 선택 1종
- ✅ Windows: `WINDOWS_PFX`, `WINDOWS_PFX_PASSWORD` — 필수 2종
- ✅ Linux: `GPG_PRIVATE_KEY` — 필수 1종
- ✅ Tauri Updater 승격: `TAURI_SIGNING_PRIVATE_KEY`, `TAURI_SIGNING_PRIVATE_KEY_PASSWORD` — 필수 2종
- ✅ Release Cosign: `COSIGN_KEY`, `COSIGN_PASSWORD` — 선택 2종

**결론**: LOCK-CI-07 시크릿 요구(3 플랫폼) 충족.

### 5.2 LOCK-CI-08 (보안 스캔 5도구)
- ✅ pip-audit / cargo-audit: 외부 시크릿 불필요 (public advisory DB)
- ✅ semgrep: `SEMGREP_APP_TOKEN` (선택, Cloud 연동 시)
- ✅ trufflehog: 외부 시크릿 불필요 (public)
- ✅ trivy: `TRIVY_DB_REPOSITORY_TOKEN` (선택, GHCR mirror 시)
- ✅ license-check: 외부 시크릿 불필요

**결론**: LOCK-CI-08 5도구 전수 매핑 완료.

### 5.3 LOCK-CI-09 (Critical/High CVE 즉시 실패)
- CVE 정책 자체는 로직이며 전용 시크릿 없음
- 연관: `SEMGREP_APP_TOKEN` (SAST), `GITHUB_TOKEN` (SARIF 업로드)

**결론**: 정책 집행에 필요한 시크릿 충족.

### 5.4 LOCK-CI-10 (프로덕션 배포 2인 승인)
- ✅ 승인 자체는 GitHub Environment Protection Rules 사용 (시크릿 아님)
- ✅ 배포 실행 시크릿: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `PROD_SSH_KEY`, `PROD_HOST_LIST`, `TF_API_TOKEN`, `DATADOG_API_KEY`, `PAGERDUTY_INTEGRATION_KEY`

**결론**: 2인 승인 후 집행에 필요한 시크릿 충족.

---

## §6. 로테이션 정책

### 6.1 로테이션 주기 정본

| 주기 | 대상 시크릿 | 근거 |
|------|------------|------|
| **자동 (per-run)** | `GITHUB_TOKEN` | GitHub 플랫폼 자동 주입 |
| **90일** | `AWS_*`, `STAGING_SSH_KEY`, `PROD_SSH_KEY` | 인프라 접근 키 — 빠른 로테이션 |
| **180일** | `CODECOV_TOKEN`, `TF_API_TOKEN`, `CLOUDFLARE_API_TOKEN`, `TRIVY_DB_REPOSITORY_TOKEN`, `E2E_TEST_API_KEY` | 3rd-party API 토큰 |
| **365일** | `SLACK_WEBHOOK_URL`, `DISCORD_WEBHOOK_URL`, `APPLE_*`, `WINDOWS_PFX*`, `DATADOG_API_KEY`, `PAGERDUTY_INTEGRATION_KEY`, `SEMGREP_APP_TOKEN`, `COSIGN_*` | 인증서/웹훅 (1년) |
| **730일** | `GPG_PRIVATE_KEY`, `TAURI_SIGNING_PRIVATE_KEY*`, `BOT_SIGNING_KEY` | 장기 서명 키 (2년) |
| **변경 없음** | `APPLE_TEAM_ID`, `AWS_REGION`, `STAGING_HOST`, `PROD_HOST_LIST`, `CLOUDFLARE_ACCOUNT_ID` | 조직/인프라 식별자 |

### 6.2 로테이션 담당자
- **Platform / GitHub**: 플랫폼 관리자 (자동)
- **AWS / SSH / Terraform**: DevOps / Infra 팀 (90일 주기 Calendar reminder)
- **Apple / Windows / GPG / Cosign 서명**: 릴리스 매니저 (만료 60일 전 교체)
- **Monitoring / Notification**: 운영 팀
- **Tauri Updater**: 릴리스 매니저 (만료 시 업데이터 무효화 위험 → 교체 전 migration plan 필수)

### 6.3 만료 알림 프로세스
1. 만료 60일 전: `dependency-check.yml` (WF-11) 주간 실행에서 GitHub Secret 메타데이터 점검 (created_at) → Issue 자동 생성
2. 만료 30일 전: Slack `#ops-alerts` 채널 알림
3. 만료 7일 전: PagerDuty P2 알림
4. 만료 1일 전: PagerDuty P1 알림 + 릴리스 차단 (`release.yml` pre-flight check)

---

## §7. 버전별 (V1/V2/V3) 적용 범위

| 시크릿 | V1 (로컬 MVP) | V2 (서버) | V3 (엔터프라이즈) |
|--------|--------------|-----------|-------------------|
| `GITHUB_TOKEN` | ✅ | ✅ | ✅ |
| `CODECOV_TOKEN` | ✅ | ✅ | ✅ |
| `SLACK_WEBHOOK_URL` | ✅ | ✅ | ✅ |
| `APPLE_*`, `WINDOWS_PFX*`, `GPG_PRIVATE_KEY` | ✅ (릴리스 시) | ✅ | ✅ |
| `TAURI_SIGNING_PRIVATE_KEY*` | ✅ | ✅ | ✅ |
| `AWS_*`, `STAGING_*`, `PROD_*`, `TF_API_TOKEN`, `DATADOG_API_KEY`, `PAGERDUTY_INTEGRATION_KEY` | ❌ | ✅ | ✅ |
| `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID` | ❌ (선택) | ✅ | ✅ |
| `DISCORD_WEBHOOK_URL` | 선택 | 선택 | 선택 |
| `COSIGN_*` | ❌ (선택) | ✅ | ✅ |
| `SEMGREP_APP_TOKEN`, `TRIVY_DB_REPOSITORY_TOKEN` | 선택 | 선택 | ✅ (필수) |
| `BOT_SIGNING_KEY` | 선택 | 선택 | ✅ (권장) |
| `E2E_TEST_API_KEY` | 선택 | ✅ | ✅ |

### 7.1 V2+/V3 Stub 시크릿 (본 문서 Scope 제외, 차기 세션 확정)

> **Scope 결정 근거**: §0.2. 본 문서는 **CI/CD 빌드/배포 시점** 시크릿만 커버. 아래는 Phase 2 (1-4 PHASE_B6 YAML 정규화, 2-1 V2 Docker Compose 파이프라인, 2-2 V3 K8s 설계) 에서 재평가/확정.

| Stub 시크릿 | 분류 | 유래 | 확정 세션 | 비고 |
|-------------|------|------|-----------|------|
| `POSTGRES_USER` | V2 Runtime | §A.3 | 2-1 | Docker Compose 환경변수 — 런타임 시크릿 |
| `POSTGRES_PASSWORD` | V2 Runtime | §A.3 | 2-1 | 동일 |
| `QDRANT_API_KEY` | V2 Runtime | §A.3 | 2-1 | Qdrant 서비스 인증 |
| `NEO4J_AUTH` | V2 Runtime | §A.3 | 2-1 | Neo4j 서비스 인증 |
| `OPENAI_API_KEY` | V2 Runtime | §A.3 | 2-1 | LLM 외부 API — 런타임 |
| `KUBECONFIG` | V3 Deploy | §A.3 | 2-2 | K8s 클러스터 접근 — V3 `deploy-v3.yml` |
| `ARGOCD_AUTH_TOKEN` | V3 Deploy | k8s_argocd_pipeline.md L378 | 2-2 | ArgoCD CLI 인증 (`argocd login --auth-token`) — V3 `deploy-v3.yml` argocd-sync job. 로테이션 90일, owner: platform team, scope: production |
| `ARGOCD_AUTH_TOKEN` | V3 Deploy | k8s_argocd_pipeline.md L378 | 2-2 | ArgoCD CLI 인증 (`argocd login --auth-token`) — V3 `deploy-v3.yml` argocd-sync job. 로테이션 90일, owner: platform team, scope: production |

> 본 Stub 시크릿들은 v1.1 master table(§2.1) 32건에 포함하지 않는다. Phase 2 확정 시 본 문서 v2 에서 승격 또는 별도 `runtime_secrets_mapping.md` 로 분리할지 결정한다.

---

## §8. 거버넌스 준수 체크리스트

### 8.1 R-15-2 (시크릿 하드코딩 절대 금지)
- [x] 모든 시크릿이 `secrets.*` 또는 `vars.*` 로만 참조
- [x] 평문 값이 WF YAML / md 파일에 포함되지 않음
- [x] `.env` 파일이 Git에 커밋되지 않음 (`.gitignore` 필수)
- [x] `trufflehog` (WF-8 secret-scan job) 가 커밋 히스토리 전수 스캔

### 8.2 R-T4-2 (보안 정책 준수)
- [x] 시크릿 접근 제어 명시: 각 시크릿에 사용 Job 명시
- [x] 최소 권한 원칙: WF 별 `permissions:` 블록 명시 (WF-9, WF-10, WF-14 확인)
- [x] 프로덕션 시크릿 분리: `PROD_*` 는 `environment: production` 에서만 접근

### 8.3 LOCK 충족 검증
- [x] LOCK-CI-07: 3 플랫폼 코드 서명 시크릿 전수 매핑 (§5.1)
- [x] LOCK-CI-08: 5 도구 관련 시크릿 매핑 (§5.2)
- [x] LOCK-CI-09: CVE 정책 집행 시크릿 식별 (§5.3)
- [x] LOCK-CI-10: 프로덕션 배포 시크릿 매핑 (§5.4)

### 8.4 R-15-2 위반 탐지 자동화
- `WF-8 secret-scan` Job (trufflehog) — 매 PR 실행
- `WF-11 dependency-check` — 주간 심화 스캔
- 위반 시 Critical Finding → PR 머지 차단 (R-15-3)

---

## §9. 로깅 포맷 (R-01-7 / R-T4-3 확장)

시크릿 접근/사용 실패 시 구조화 로깅 양식. (R-01-7 의 중첩 구조 3 블록 + `trace_id`)

```json
{
  "trace_id": "wf-7-prod-deploy-20260411-001",
  "timestamp": "2026-04-11T14:23:10Z",
  "level": "ERROR",
  "workflow": "deploy-prod.yml",
  "job": "canary-deploy",
  "step": "aws-credentials-setup",
  "error": {
    "code": "MISSING_SECRET",
    "message": "Required secret AWS_ACCESS_KEY_ID not found in environment 'production'",
    "type": "SecretResolutionError"
  },
  "context": {
    "secret_name": "AWS_ACCESS_KEY_ID",
    "required_by": "canary-deploy",
    "environment": "production",
    "lock_policy": "LOCK-CI-10",
    "rotation_cycle_days": 90,
    "last_rotated_at": "2026-01-08T00:00:00Z",
    "expires_at": "2026-04-08T00:00:00Z"
  },
  "recovery": {
    "action": "escalate_to_ops_pager",
    "fallback": "block_deployment",
    "manual_steps": [
      "Rotate AWS_ACCESS_KEY_ID via IAM",
      "Update GitHub Environment secret",
      "Re-run deployment workflow"
    ],
    "escalation_target": "PagerDuty (PAGERDUTY_INTEGRATION_KEY)"
  }
}
```

> **주의**: 로그 본문에 실제 시크릿 값을 절대 포함하지 않는다. `secret_name` 식별자만 기록.

---

## §10. CONFLICT 후보 / LOCK 변경 후보 보고

본 문서 작성 중 발견된 정본 간 불일치는 자동 등재하지 않고 보고만 한다 (step 7 정식 등재).

### 10.1 CONFLICT 후보
`[CONFLICT_CANDIDATE: §A.3 시크릿 매핑 테이블 v0 (23건) 과 본 문서 §2.1 v1.1 (32건) 간 항목 수 및 명명 차이. §A.3 은 `WINDOWS_CERTIFICATE` 라고 표기하나 실제 WF-4 구현은 `WINDOWS_PFX` / `WINDOWS_PFX_PASSWORD` 로 표기. 또한 §A.3 에는 `POSTGRES_*`, `QDRANT_API_KEY`, `NEO4J_AUTH`, `OPENAI_API_KEY`, `KUBECONFIG` 등 runtime 시크릿이 포함되나 본 문서는 scope 제외. §A.3 표 갱신 또는 본 문서 scope 확장 결정 필요.]`

`[CONFLICT_CANDIDATE: WF-5 `GPG_PRIVATE_KEY` 참조 — WF-4 와 동일 시크릿을 공유하는데 로테이션 주기 (730일) 가 WF-4 매트릭스에서는 명시되지 않았음. 로테이션 정책 단일화 필요.]`

`[CONFLICT_CANDIDATE: P1-1 산출물 `01_ci-workflows/WF-4_build-tauri.md` §5.1 및 `05_release-management/WF-5_release.md` §7 시크릿 테이블에 `TAURI_SIGNING_PRIVATE_KEY` / `TAURI_SIGNING_PRIVATE_KEY_PASSWORD` 명시 참조가 누락됨. §A.3 (계획서) 및 `05_release-management/_index.md` §코드 서명 섹션에서는 `build-tauri.yml` + `release.yml` 용 정본으로 지정됨. LOCK-CI-07 (Tauri 업데이트 서명 포함) 정합성을 위해 P1-1 WF-4/WF-5 본문 시크릿 섹션 보강 필요. (본 문서 §2.1 #29/#30 에서는 §A.3 정본 우선 원칙에 따라 유지.)]`

`[CONFLICT_CANDIDATE: P1-1 `WF-5_release.md` §7 에 `DISCORD_WEBHOOK_URL` (선택) 이 존재하나 §A.3 에는 정의되지 않음. 본 문서 §2.1 #31 에 v1.1 신규 등재. §A.3 갱신 여부 step 7 논의.]`

`[CONFLICT_CANDIDATE: P1-1 `WF-10_docs-build.md` §5 에 `CLOUDFLARE_ACCOUNT_ID` 가 필수로 지정되어 있으나 §A.3 에는 `CLOUDFLARE_API_TOKEN` 만 존재. 본 문서 §2.1 #32 에 v1.1 신규 등재. §A.3 갱신 여부 step 7 논의.]`

### 10.2 LOCK 변경 후보
`[LOCK_CHANGE_NEEDED: 없음]` — 본 세션은 LOCK-CI-01~12 중 어떤 항목도 위반/추가 제안하지 않는다. LOCK-CI-07 (코드 서명) 에 Tauri 서명 키 (`TAURI_SIGNING_PRIVATE_KEY`) 포함 여부를 명확히 하고 싶으나, 명시적 LOCK 변경이 아닌 문서 해석 수준이므로 step 7 논의 대상.

---

## §11. Phase 2 테스트 시나리오 (14건)

Phase 2 통합 테스트에서 시크릿 관리 로직을 검증할 시나리오.

| # | 시나리오 | 주입 방법 | 기대 결과 |
|---|----------|----------|----------|
| T-01 | 필수 시크릿 누락 (`AWS_ACCESS_KEY_ID`) | GitHub Environment 에서 삭제 후 `deploy-prod.yml` 실행 | `canary-deploy` job 즉시 실패, `MISSING_SECRET` 구조화 로그 출력, PagerDuty P1 알림 |
| T-02 | 시크릿 하드코딩 커밋 시도 | `SK_TEST_KEY=sk-xxxxx` 를 소스에 포함 후 PR | `trufflehog` (WF-8 secret-scan) 탐지, PR 머지 차단, `SECRET_LEAK` Critical Finding |
| T-03 | 만료된 Apple 인증서 | `APPLE_CERTIFICATE` 를 만료된 .p12 로 교체 후 WF-4 실행 | macOS build job 서명 단계 실패, `SIGNING_CERT_EXPIRED` 에러 코드, 릴리스 차단 |
| T-04 | 잘못된 `CODECOV_TOKEN` | 무효 토큰 주입 후 WF-2 실행 | `coverage-report` job 업로드 실패 → Codecov API 401, Slack 알림, PR 상태 체크 warning (머지 차단은 아님) |
| T-05 | `GITHUB_TOKEN` Rate Limit | Mock rate-limit 응답 주입 (WF-1 `T-11` 기존 시나리오 확장) | status job success 유지, `PR_COMMENT_RATE_LIMIT` 로그만 기록 |
| T-06 | 로테이션 만료 60일 전 알림 | Mock `last_rotated_at` 를 156일 전으로 설정 후 WF-11 실행 | `dependency-check.yml` 이 GitHub Issue 자동 생성, Slack 알림 |
| T-07 | 프로덕션 환경 격리 위반 시도 | `deploy-staging.yml` 에서 `PROD_SSH_KEY` 참조 시도 | GitHub Environment Protection Rules 에 의해 접근 거부, workflow 실패 |
| T-08 | Tauri 서명 키 누락 (release mode) | `TAURI_SIGNING_PRIVATE_KEY` 삭제 후 `release.yml` 실행 | build job `release_mode && !skip_sign` 경로에서 실패, release 차단 |
| T-09 | Cosign keyless fallback | `COSIGN_KEY` 삭제 (keyless 모드 활성화) 후 WF-5 실행 | cosign-sign job 이 OIDC 기반 keyless 경로로 전환 성공, 릴리스 진행 |
| T-10 | 시크릿 명명 오타 탐지 | YAML 에 `secrets.AWS_ACCESSKEY_ID` (오타) 사용 | Pre-flight lint 단계에서 탐지, `UNKNOWN_SECRET_REFERENCE` 에러, PR 머지 차단 |
| T-11 | Semgrep Cloud 선택 시크릿 없음 | `SEMGREP_APP_TOKEN` 없이 WF-8 실행 | sast job 이 local-only 모드로 동작, `SEMGREP_CLOUD_DISABLED` 로그, 성공 |
| T-12 | 로테이션 후 이전 키 즉시 무효화 검증 | 새 `AWS_*` 배포 후 이전 키로 재요청 | IAM 에서 401, `STALE_SECRET` 로그 — 로테이션 정책 동작 검증 |
| T-13 | `CLOUDFLARE_ACCOUNT_ID` 누락 | WF-10 에서 account id 만 삭제 후 `docs-build.yml` 실행 | `deploy-pages` job 이 Cloudflare API 에서 `invalid_account_context` 반환 → 구조화 로그 `MISSING_SECRET` + CI failure |
| T-14 | `DISCORD_WEBHOOK_URL` 선택 시크릿 없음 | WF-5 `notify` job 에서 시크릿 미설정 | notify-slack 은 성공, notify-discord 는 skip 처리 (`OPTIONAL_SECRET_SKIPPED` 로그), release 진행 |

**합계**: 14건 (요구 10건 초과 충족, v1.1 에서 T-13/T-14 추가).

---

## §12. 세션 간 인터페이스 cross-check

### 12.1 P1-1 (워크플로우 상세 파일) ↔ P1-2 (본 문서)
- **인터페이스**: P1-1 각 WF 파일의 `## 시크릿` 섹션 (시크릿명 / 사용 Job / 필수 여부) → 본 문서 §2.1 / §4
- **정합성 검증**: §4 역매핑 테이블 작성 시 각 WF 파일을 직접 읽고 전수 집계 (§0.2 방법론)
- **불일치 v1.1 재검증 결과**:
  - (a) `TAURI_SIGNING_PRIVATE_KEY` / `PASSWORD`: §A.3 및 `05_release-management/_index.md` 에 존재하나 P1-1 `WF-4_build-tauri.md` §5.1 + `WF-5_release.md` §7 본문에 명시 참조 누락 → 본 문서 #29/#30 유지, §10.1 CONFLICT 후보 #3 으로 보고.
  - (b) `DISCORD_WEBHOOK_URL`: P1-1 `WF-5_release.md` §7 에 존재하나 §A.3 미정의 → v1.1 에서 #31 로 추가, §10.1 CONFLICT 후보 #4.
  - (c) `CLOUDFLARE_ACCOUNT_ID`: P1-1 `WF-10_docs-build.md` §5 에 필수로 존재하나 §A.3 미정의 → v1.1 에서 #32 로 추가, §10.1 CONFLICT 후보 #5.
  - (d) `SLACK_WEBHOOK_URL` 사용 WF 커버리지: P1-1 `WF-11_dependency-check.md` §5 에서 주간 요약용 선택 시크릿으로 참조되나 v1 에서 누락 → v1.1 §2.1 #3 사용 WF 에 WF-11 포함.
- **주의**: `CODECOV_TOKEN` 은 WF-1 본문에서 "호출체인" 으로만 언급되고 실제 사용은 WF-2 `coverage-report` job 에서 발생 — 본 문서 §2.1 에서는 양쪽 WF 를 모두 사용 WF 컬럼에 기재

### 12.2 P1-3 (캐시 전략 상세) ↔ P1-2
- **인터페이스**: 캐시 전략 문서가 시크릿을 참조하지 않음 (캐시 키는 공개 hash 기반)
- **정합성 검증**: 해당 없음

### 12.3 P1-4 (PHASE_B6 YAML 정규화) ↔ P1-2
- **인터페이스**: P1-4 가 WF YAML 에 시크릿 참조를 삽입/정규화할 때 본 문서 §2.1 시크릿명을 정본으로 사용해야 함
- **주의**: P1-4 에서 §A.3 (계획서) 과 본 문서 §2.1 (v1.1) 간 불일치 발견 시 CONFLICT_LOG 등재 (§10.1 기록된 5건을 step 7 에서 정식 등재 예정)

### 12.4 03_security-scanning/_index.md
- **현재 상태**: _index.md 는 공통 산출물 보호 대상 (step 1/2/3/4/6 수정 금지). 본 문서가 `시크릿 매핑` 섹션의 정본을 대체하며, _index.md 의 해당 섹션은 도메인 마감 step 5/7/8 에서 본 문서 링크로 갱신한다.
- **처리 방침**: 본 세션 step1/step2 에서는 _index.md 수정하지 않음. 대신 본 문서 내 §1 교차 참조 블록에서 _index.md 를 명시.

---

## §13. 검증 체크리스트 (Phase 1 G1 게이트)

- [x] 시크릿 **12+개** 전수 매핑 완료 → **32건** 매핑 (267% 초과 달성)
- [x] 각 시크릿에 **사용 WF 목록** 명시 → §2.1 master table
- [x] **코드 서명 시크릿 (macOS/Windows/Linux) 3종 포함** → §5.1 LOCK-CI-07 매핑
- [x] **LOCK-CI-09 Critical/High CVE 정책 시크릿** 반영 → §5.3
- [x] **R-15-2 (하드코딩 금지) 준수 체크항목** 포함 → §8.1
- [x] **14개 WF 전수 커버** → §4 역매핑 (WF-1~WF-14 100%)
- [x] 로테이션 정책 정의 → §6
- [x] V1/V2/V3 버전별 적용 범위 정의 → §7
- [x] Phase 2 테스트 시나리오 10건+ → §11 (14건)
- [x] 세션 간 인터페이스 cross-check → §12

---

## §14. 변경 이력

| 버전 | 일자 | 변경 내용 | 세션 |
|------|------|----------|------|
| v1 | 2026-04-11 | 초기 작성 — 30건 시크릿 전수 매핑, LOCK-CI-07/08/09/10 검증, R-15-2 준수 체크 | P1-2 step1 |
| v1.1 | 2026-04-11 | 미세 재검증: 누락 시크릿 2건(`DISCORD_WEBHOOK_URL` WF-5, `CLOUDFLARE_ACCOUNT_ID` WF-10) 추가, `SLACK_WEBHOOK_URL` 사용 WF 에 WF-11 포함, TAURI_SIGNING 정본 출처(§A.3/_index.md) 주석 추가, §10.1 CONFLICT 후보 3건으로 확장 (총 32건) | P1-2 step2 |

---

## §15. 후속 작업 (Backlog)

| ID | 작업 | 대상 세션 |
|----|------|-----------|
| BL-01 | §A.3 (계획서) v1 매핑과 동기화 or 부록 업데이트 | Phase 1 step 7 / Phase 2 |
| BL-02 | V2 Runtime 시크릿(`POSTGRES_*`, `QDRANT_*`, `NEO4J_*`, `OPENAI_*`) 별도 문서 분리 검토 | P2-1 |
| BL-03 | V3 `KUBECONFIG` + ArgoCD 토큰 매핑 | P2-2 |
| BL-04 | Secret manager(HashiCorp Vault / AWS Secrets Manager) 도입 검토 | Phase 3 |
| BL-05 | 로테이션 자동화(WF-11 확장) 구현 | Phase 2-3 |
| BL-06 | Pre-flight `UNKNOWN_SECRET_REFERENCE` 린터 도입 (T-10 기반) | Phase 2-3 |

---

**정본 선언**: 본 문서는 4-2 CI/CD Pipeline 도메인의 시크릿 매핑 정본(L2)이다. 변경 시 AUTHORITY_CHAIN.md 에 따라 DevOps 팀 승인 필요.
