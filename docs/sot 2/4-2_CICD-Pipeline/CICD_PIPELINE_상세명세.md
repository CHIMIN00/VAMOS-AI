# 4-2. CI/CD Pipeline 상세명세

> **Tier**: 4 - Infrastructure
> **Part2 상태**: PARTIAL (14 filenames only)
> **SOT 근거**: PHASE_B6
> **Part2 위치**: V1-Phase 6 DevOps 섹션

---

## 개요

VAMOS AI 프로젝트의 GitHub Actions 기반 CI/CD 파이프라인. Part2에는 14개 워크플로우 YAML 파일명만 나열되어 있으며, 각 워크플로우의 job 구성, 트리거 조건, 시크릿 설정, 캐싱 전략 등 구현 상세가 전무.

---

## 전체 워크플로우 의존성 그래프

```
push/PR → ci.yml ─→ lint.yml
                  ├→ test.yml ─→ e2e-test.yml
                  ├→ security-scan.yml
                  └→ build-tauri.yml ─→ release.yml ─→ deploy-staging.yml ─→ deploy-prod.yml

schedule → nightly.yml ─→ benchmark.yml
                        ├→ dependency-check.yml
                        └→ docs-build.yml

manual → version-bump.yml
```

---

## WF-1: ci.yml (메인 CI 오케스트레이터)

### 트리거 조건
```yaml
on:
  push:
    branches: [main, develop, "release/**"]
  pull_request:
    branches: [main, develop]
    types: [opened, synchronize, reopened]
```

### Job 구성

| Job | Runs-on | 의존성 | 설명 |
|-----|---------|--------|------|
| `setup` | ubuntu-latest | - | 체크아웃, 캐시 키 생성, 변경 파일 감지 |
| `lint` | ubuntu-latest | setup | lint.yml 호출 (reusable workflow) |
| `test-python` | ubuntu-latest | setup | test.yml 호출 (Python 매트릭스) |
| `test-rust` | ubuntu-latest | setup | Rust cargo test |
| `build-check` | ubuntu-latest | lint, test-* | build-tauri.yml 호출 (dry-run) |
| `security` | ubuntu-latest | setup | security-scan.yml 호출 |
| `status-check` | ubuntu-latest | all | 최종 상태 리포트, PR 코멘트 |

### 캐싱 전략
- **Python**: `~/.cache/pip` + `~/.cache/uv` (키: `python-{hash(pyproject.toml)}`)
- **Rust**: `~/.cargo/registry` + `target/` (키: `rust-{hash(Cargo.lock)}`)
- **Node**: `~/.pnpm-store` (키: `node-{hash(pnpm-lock.yaml)}`)
- **캐시 적중률 목표**: 80%+ (weekly 기준)

---

## WF-2: test.yml (테스트 실행)

### 트리거
```yaml
on:
  workflow_call:  # ci.yml에서 호출
  workflow_dispatch:
    inputs:
      test_scope:
        type: choice
        options: [all, unit, integration, smoke]
```

### 매트릭스 빌드
```yaml
strategy:
  matrix:
    python-version: ["3.11", "3.12"]
    os: [ubuntu-latest, windows-latest, macos-latest]
  fail-fast: false
```

### Job 구성
| Job | 설명 | 타임아웃 |
|-----|------|---------|
| `unit-tests` | pytest -m "not integration" --cov | 15분 |
| `integration-tests` | pytest -m integration (DB/API 필요) | 30분 |
| `rust-tests` | cargo test --workspace | 20분 |
| `coverage-report` | coverage 합산, Codecov 업로드 | 5분 |

### 커버리지 게이트
- **최소 라인 커버리지**: Python ≥ 75 %, Rust ≥ 80 %, React ≥ 80 % (LOCK-CI-03)
- **PR 커버리지 하락**: -2% 이상 하락 시 실패
- **리포트**: Codecov PR 코멘트 자동 생성

---

## WF-3: lint.yml (코드 품질)

### Job 구성
| Job | 도구 | 설정 |
|-----|------|------|
| `python-lint` | ruff check + ruff format --check | `ruff.toml` |
| `python-type` | mypy --strict | `mypy.ini` |
| `rust-lint` | cargo clippy -- -D warnings | `clippy.toml` |
| `rust-fmt` | cargo fmt --check | `rustfmt.toml` |
| `frontend-lint` | eslint + prettier --check | `.eslintrc.js` |
| `markdown-lint` | markdownlint-cli2 | `.markdownlint.yaml` |
| `yaml-lint` | yamllint | `.yamllint.yml` |

---

## WF-4: build-tauri.yml (Tauri 빌드)

### 매트릭스
```yaml
strategy:
  matrix:
    include:
      - os: ubuntu-latest
        target: x86_64-unknown-linux-gnu
        artifact: vamos_amd64.AppImage
      - os: windows-latest
        target: x86_64-pc-windows-msvc
        artifact: vamos_x64.msi
      - os: macos-latest
        target: aarch64-apple-darwin
        artifact: vamos_arm64.dmg
      - os: macos-latest
        target: x86_64-apple-darwin
        artifact: vamos_x64.dmg
```

### 빌드 단계
1. 시스템 의존성 설치 (Linux: libgtk-3-dev, libwebkit2gtk-4.1-dev 등)
2. Rust 툴체인 설치 (stable, target 추가)
3. Node/pnpm 설치, 프론트엔드 빌드
4. Python venv 생성, 의존성 설치, wheel 빌드
5. `pnpm tauri build --target {target}`
6. 아티팩트 업로드 (retention: 30일)

### 코드 서명
- **macOS**: Apple Developer ID (시크릿: `APPLE_CERTIFICATE`, `APPLE_CERTIFICATE_PASSWORD`, `APPLE_ID`, `APPLE_TEAM_ID`)
- **Windows**: EV 코드 서명 (시크릿: `WINDOWS_PFX`, `WINDOWS_PFX_PASSWORD`)
- **Linux**: GPG 서명 (`GPG_PRIVATE_KEY`)

---

## WF-5: release.yml (릴리스)

### 트리거
```yaml
on:
  push:
    tags: ["v*.*.*"]
```

### Job 구성
1. **validate-tag**: 시맨틱 버전 형식 검증, CHANGELOG 존재 확인
2. **build**: build-tauri.yml 매트릭스 빌드 호출
3. **create-release**: GitHub Release 생성, 아티팩트 첨부, CHANGELOG 본문 추출
4. **notify**: Slack/Discord 릴리스 알림

### 아티팩트 체크섬
- 각 바이너리에 대해 SHA256 체크섬 생성
- `checksums.txt` 릴리스 첨부
- Sigstore cosign 서명 (선택)

---

## WF-6: deploy-staging.yml (스테이징 배포)

### 트리거
```yaml
on:
  workflow_run:
    workflows: ["Release"]
    types: [completed]
    branches: [main]
  workflow_dispatch:
```

### 배포 대상
- **Update Server**: S3/R2에 업데이트 매니페스트 업로드
- **Docs**: Vercel/Cloudflare Pages 배포
- **API Gateway**: 스테이징 엔드포인트 업데이트

### 배포 후 검증
- 스모크 테스트 자동 실행 (5분)
- 업데이트 서버 응답 확인
- Slack 알림 (성공/실패)

---

## WF-7: deploy-prod.yml (프로덕션 배포)

### 트리거
```yaml
on:
  workflow_dispatch:
    inputs:
      version:
        required: true
        description: "배포할 버전 태그 (예: v1.2.3)"
      confirm:
        type: boolean
        required: true
        description: "프로덕션 배포를 확인합니다"
```

### 배포 전략
- **Required Approvals**: 2명 이상 승인 (GitHub Environment protection rules)
- **Canary**: 스테이징 검증 통과 확인
- **Rollback**: 이전 버전 매니페스트로 즉시 복원 가능
- **Post-deploy**: 프로덕션 스모크 테스트 + 모니터링 대시보드 링크 공유

---

## WF-8: security-scan.yml (보안 스캔)

### Job 구성
| Job | 도구 | 대상 |
|-----|------|------|
| `dependency-audit` | pip-audit + cargo-audit | Python/Rust 의존성 |
| `sast` | semgrep --config=auto | Python/Rust/TS 소스 |
| `secret-scan` | trufflehog | 전체 커밋 히스토리 |
| `license-check` | license-checker | 전체 의존성 라이선스 |
| `container-scan` | trivy image | Docker 이미지 (해당 시) |

### 임계치
- **Critical/High CVE**: 즉시 실패, PR 머지 차단
- **Medium CVE**: 경고, 7일 내 해결 필요
- **SARIF 업로드**: GitHub Security 탭에 결과 표시

---

## WF-9: benchmark.yml (성능 벤치마크)

### 트리거
```yaml
on:
  workflow_call:
  schedule:
    - cron: "0 3 * * 1"  # 매주 월요일 3AM UTC
```

### 벤치마크 항목
| 항목 | 도구 | 임계치 |
|------|------|--------|
| Python 응답 시간 | pytest-benchmark | p95 < 2s |
| Rust IPC 지연 | criterion | p99 < 10ms |
| 메모리 사용량 | memory_profiler | < 500MB (idle) |
| 검색 지연 | custom bench | p95 < 200ms (10K docs) |
| 스트리밍 TTFB | custom bench | < 500ms |

### 결과 저장
- `gh-pages` 브랜치에 JSON 히스토리 저장
- 성능 회귀 10%+ 시 알림
- GitHub Actions 벤치마크 커멘트 (이전 대비 비교표)

---

## WF-10: docs-build.yml (문서 빌드)

### 트리거
```yaml
on:
  push:
    paths: ["docs/**", "*.md", "src/**/*.py"]
    branches: [main]
```

### 빌드
- **API Docs**: Sphinx (Python) + rustdoc (Rust)
- **User Guide**: MkDocs Material
- **Deploy**: Cloudflare Pages
- **Link Check**: lychee (깨진 링크 감지)

---

## WF-11: dependency-check.yml (의존성 점검)

### 트리거
```yaml
on:
  schedule:
    - cron: "0 6 * * 1"  # 매주 월요일 6AM
```

### 점검 항목
- Dependabot PR 자동 생성 여부 확인
- Python 의존성 최신 버전 대비 diff
- Rust 의존성 최신 버전 대비 diff
- 라이선스 변경 감지 (GPL 침투 방지)

---

## WF-12: e2e-test.yml (E2E 테스트)

### 트리거
```yaml
on:
  workflow_call:
  workflow_dispatch:
```

### 테스트 환경
- **드라이버**: Playwright + WebDriver (Tauri WebView)
- **시나리오**: 20개 핵심 사용자 시나리오 (세션 생성→대화→메모리 저장→검색→에이전트 실행)
- **Headless**: CI에서 Xvfb (Linux), 네이티브 (macOS/Windows)
- **타임아웃**: 시나리오당 120초, 전체 30분

---

## WF-13: nightly.yml (나이틀리 빌드)

### 트리거
```yaml
on:
  schedule:
    - cron: "0 0 * * *"  # 매일 자정 UTC
```

### 포함 작업
1. develop 브랜치 전체 테스트 (매트릭스)
2. 벤치마크 실행
3. 의존성 취약점 스캔
4. 나이틀리 빌드 아티팩트 생성 (alpha 태그)
5. 실패 시 팀 Slack 채널 알림

---

## WF-14: version-bump.yml (버전 업데이트)

### 트리거
```yaml
on:
  workflow_dispatch:
    inputs:
      bump_type:
        type: choice
        options: [patch, minor, major]
      prerelease:
        type: choice
        options: [none, alpha, beta, rc]
```

### 동작
1. 현재 버전 읽기 (`Cargo.toml`, `pyproject.toml`, `package.json`)
2. 시맨틱 버전 범프 적용
3. CHANGELOG.md 업데이트 (conventional commits 기반)
4. 모든 버전 파일 동기화
5. 커밋 + 태그 생성 + push

---

## 환경 시크릿 구성

| 시크릿 | 사용 워크플로우 | 설명 |
|--------|----------------|------|
| `CODECOV_TOKEN` | test.yml | Codecov 업로드 |
| `APPLE_CERTIFICATE` | build-tauri.yml | macOS 코드 서명 |
| `APPLE_CERTIFICATE_PASSWORD` | build-tauri.yml | 인증서 비밀번호 |
| `APPLE_ID` | build-tauri.yml | Apple ID |
| `APPLE_TEAM_ID` | build-tauri.yml | Apple 팀 ID |
| `APPLE_INSTALLER_CERT` | build-tauri.yml | macOS Installer 코드 서명 (Base64) |
| `WINDOWS_PFX` | build-tauri.yml | Windows 코드 서명 |
| `WINDOWS_PFX_PASSWORD` | build-tauri.yml | 인증서 비밀번호 |
| `GPG_PRIVATE_KEY` | build-tauri.yml | Linux GPG 서명 |
| `SLACK_WEBHOOK_URL` | 다수 | Slack 알림 |
| `AWS_ACCESS_KEY_ID` | deploy-*.yml | S3 업로드 |
| `AWS_SECRET_ACCESS_KEY` | deploy-*.yml | S3 업로드 |
| `CLOUDFLARE_API_TOKEN` | docs-build.yml | Pages 배포 |
| `SEMGREP_APP_TOKEN` | security-scan.yml | Semgrep 분석 |

---

## 병렬화 및 최적화

### 병렬 실행 규칙
- lint, test, security는 상호 독립 → 병렬 실행
- build는 lint + test 통과 후 실행
- deploy는 build 완료 후 실행

### 실행 시간 목표
| 워크플로우 | 목표 시간 | 비고 |
|-----------|----------|------|
| ci.yml (PR) | < 10분 | 캐시 적중 시 |
| build-tauri.yml | < 20분 | 4-platform 병렬 (Linux x64, Windows x64, macOS ARM64, macOS x64; LOCK-CI-06) |
| e2e-test.yml | < 30분 | - |
| nightly.yml | < 60분 | 전체 포함 |

### concurrency 설정
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true  # 동일 브랜치 중복 실행 취소
```

---

## F. 배포 게이트 명세

### F-1 스테이징 배포 게이트
| 조건 | 유형 | 실패 시 행동 |
|------|------|-----------|
| 전 테스트 통과 (unit + integration) | 자동 | 배포 차단 |
| 보안 스캔 Critical/High 0건 | 자동 | 배포 차단 |
| 커버리지 게이트 충족 (LOCK-CI-03) | 자동 | 배포 차단 |
| 벤치마크 회귀 < 10% | 자동 | 경고 + 수동 승인 요구 |

### F-2 프로덕션 배포 게이트
| 조건 | 유형 | 실패 시 행동 |
|------|------|-----------|
| 스테이징 E2E 전부 통과 | 자동 | 배포 차단 |
| 2인 승인 (GitHub Environment Protection) | 수동 | 48시간 대기 → 자동 취소 |
| 카나리 메트릭 정상 (QoD ≥ 0.85, 에러율 < 2%) | 자동 | 자동 롤백 |
| 스모크 테스트 통과 (5개 핵심 엔드포인트) | 자동 | 즉시 롤백 |

### F-3 롤백 결정 트리
1. 스모크 테스트 실패 → **즉시 롤백** (자동, < 2분)
2. 카나리 에러율 > 2% → **자동 롤백** (5분 이내)
3. 사용자 불만 급증 (> 5건/시간) → **수동 롤백** (on-call 엔지니어 판단)
4. 성능 회귀 > 20% → **수동 롤백** + 원인 분석

---

## G. 코드 서명 플레이북

### G-1 인증서 관리
| 플랫폼 | 인증서 유형 | 저장 위치 | 갱신 주기 |
|--------|-----------|----------|----------|
| macOS | Apple Developer ID (Application) | `APPLE_CERTIFICATE` secret (Base64) | 연간 |
| macOS | Apple Developer ID (Installer) | `APPLE_INSTALLER_CERT` secret | 연간 |
| Windows | EV Code Signing (DigiCert) | `WINDOWS_PFX` secret (Base64) | 1년 |
| Linux | GPG Signing Key | `GPG_PRIVATE_KEY` secret | 2년 |

### G-2 CI 환경 서명 프로세스
**macOS**:
```yaml
- name: Import Certificate
  env:
    CERTIFICATE: ${{ secrets.APPLE_CERTIFICATE }}
    CERTIFICATE_PASSWORD: ${{ secrets.APPLE_CERTIFICATE_PASSWORD }}
  run: |
    echo "$CERTIFICATE" | base64 --decode > certificate.p12
    security create-keychain -p "" build.keychain
    security import certificate.p12 -k build.keychain -P "$CERTIFICATE_PASSWORD" -T /usr/bin/codesign
    security set-key-partition-list -S apple-tool:,apple: -s -k "" build.keychain
```

**Windows**:
```yaml
- name: Sign Windows Binary
  env:
    PFX: ${{ secrets.WINDOWS_PFX }}
    PFX_PASSWORD: ${{ secrets.WINDOWS_PFX_PASSWORD }}
  run: |
    echo "$PFX" | base64 --decode > certificate.pfx
    signtool sign /f certificate.pfx /p "$PFX_PASSWORD" /tr http://timestamp.digicert.com /td sha256 target/release/*.exe
```

### G-3 서명 실패 복구
1. 인증서 만료 → 빌드 실패 + on-call 알림 → 인증서 갱신 SOP 실행
2. Keychain 접근 오류 (macOS) → 런너 캐시 삭제 + Keychain 재생성
3. Timestamp 서버 장애 → 대체 서버(`http://timestamp.sectigo.com`) 자동 전환

---

## H. 캐시 전략 상세

### H-1 키 생성 규칙
| 대상 | 기본 키 | 복원 키 | 해시 대상 |
|------|---------|---------|----------|
| Python | `python-${{ runner.os }}-${{ hashFiles('pyproject.toml', 'uv.lock') }}` | `python-${{ runner.os }}-` | pyproject.toml + uv.lock |
| Rust | `rust-${{ runner.os }}-${{ hashFiles('Cargo.lock') }}` | `rust-${{ runner.os }}-` | Cargo.lock |
| Node | `node-${{ runner.os }}-${{ hashFiles('pnpm-lock.yaml') }}` | `node-${{ runner.os }}-` | pnpm-lock.yaml |
| Tauri | `tauri-target-${{ runner.os }}-${{ matrix.target }}-${{ hashFiles('Cargo.lock') }}` | `tauri-target-${{ runner.os }}-${{ matrix.target }}-` | Cargo.lock (플랫폼+아키텍처별 분리) |

### H-2 캐시 정책
- **TTL**: 7일 (GitHub Actions 기본)
- **최대 크기**: 10GB (저장소당 GitHub 제한)
- **퍼지 주기**: 매주 일요일 nightly 빌드에서 전체 캐시 삭제 + 워밍
- **부분 매칭**: restore-keys 패턴으로 이전 버전 캐시 활용 (Cargo.lock 일부 변경 시)
