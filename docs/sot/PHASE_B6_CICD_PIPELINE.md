# PHASE_B6_CICD_PIPELINE (v1.0.2)

---

## 0. 문서 메타

| 항목 | 값 |
|------|-----|
| **문서 ID** | PHASE_B6 |
| **버전** | v1.0.2 |
| **작성일** | 2026-02-22 |
| **상태** | ACTIVE |
| **의존 문서** | D2.1-A1 (Tech Stack), D2.0-04 (Infra Core), PLAN-3.0 |
| **대상 독자** | DevOps 엔지니어, 개발팀 전원 |
| **기술 스택** | GitHub Actions, Tauri 2.0, Python 3.11+, Rust (stable), Node 20+, Docker |

---

## 1. 개요 (CI/CD 전략 -- GitHub Actions 기반)

### 1.1 전략 요약

VAMOS AI 에이전트 플랫폼은 **3개 언어(Python/Rust/TypeScript)** 로 구성된 폴리글랏 프로젝트이다. CI/CD는 **GitHub Actions**를 기본 플랫폼으로 사용하며, 버전별로 다음과 같이 진화한다.

| 단계 | V1 (로컬 MVP) | V2 (서버) | V3 (엔터프라이즈) |
|------|---------------|-----------|-------------------|
| **빌드** | 로컬 + CI | CI/CD 자동화 | CI/CD + 스테이징 |
| **테스트** | PR 트리거 | PR + merge 트리거 | PR + merge + nightly |
| **배포** | 수동 (로컬 설치) | Docker Compose 자동 | K8s 자동 (ArgoCD) |
| **릴리스** | GitHub Release | Release + Docker Registry | Release + Helm Chart |

### 1.2 파이프라인 흐름도

```
PR/Push ──► 코드 품질 ──► 테스트 ──► 빌드 ──► 릴리스 ──► 배포
  │           │             │          │          │          │
  │         ruff/mypy     pytest    Tauri     SemVer    Docker
  │         clippy      cargo test  wheel    Changelog  Compose
  │         eslint/tsc   vitest    Docker    Release     K8s
  │                                           │
  └────────── 보안 스캔 (병렬) ───────────────┘
```

### 1.3 브랜치 전략

| 브랜치 | 용도 | 트리거 |
|--------|------|--------|
| `main` | 프로덕션 릴리스 | tag push |
| `develop` | 통합 개발 | merge commit |
| `feature/*` | 기능 개발 | PR open/push |
| `hotfix/*` | 긴급 수정 | PR open/push |
| `release/*` | 릴리스 준비 | manual |

---

## 2. 코드 품질 파이프라인 (PR/Push 트리거)

### 2.1 Python 린트/타입체크

**도구**: `ruff` (린팅 + 포매팅) + `mypy` (타입체크)

```yaml
# .github/workflows/quality-python.yml (부분)
python-quality:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Set up Python 3.11
      uses: actions/setup-python@v5
      with:
        python-version: "3.11"
        cache: "pip"

    - name: Install dependencies
      run: |
        pip install --upgrade pip
        pip install ruff mypy pydantic[dotenv]
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Ruff lint
      run: ruff check backend/vamos_core/ --output-format=github

    - name: Ruff format check
      run: ruff format --check backend/vamos_core/

    - name: Mypy type check
      run: mypy backend/vamos_core/ --strict --ignore-missing-imports
```

**설정 파일** (`pyproject.toml`):

```toml
[tool.ruff]
target-version = "py311"
line-length = 100
select = ["E", "F", "W", "I", "N", "UP", "S", "B", "A", "C4", "DTZ", "T20", "ICN"]

[tool.ruff.per-file-ignores]
"tests/**" = ["S101"]  # assert 허용

[tool.mypy]
python_version = "3.11"
strict = true
plugins = ["pydantic.mypy"]

[tool.mypy.plugins.pydantic-mypy]
init_forbid_extra = true
init_typed = true
warn_required_dynamic_aliases = true
```

### 2.2 Rust 린트/빌드

**도구**: `clippy` (린팅) + `cargo build` (컴파일 검증) + `rustfmt` (포매팅)

```yaml
# .github/workflows/quality-rust.yml (부분)
rust-quality:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Install Rust toolchain
      uses: dtolnay/rust-toolchain@stable
      with:
        components: clippy, rustfmt

    - name: Cache cargo registry
      uses: actions/cache@v4
      with:
        path: |
          ~/.cargo/registry
          ~/.cargo/git
          src-tauri/target
        key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}
        restore-keys: ${{ runner.os }}-cargo-

    - name: Cargo fmt check
      run: cargo fmt --manifest-path src-tauri/Cargo.toml -- --check

    - name: Clippy lint
      run: |
        cargo clippy --manifest-path src-tauri/Cargo.toml \
          --all-targets --all-features \
          -- -D warnings -W clippy::pedantic

    - name: Cargo build (debug)
      run: cargo build --manifest-path src-tauri/Cargo.toml
```

### 2.3 React 린트/타입체크

**도구**: `eslint` (린팅) + `tsc` (타입체크) + `prettier` (포매팅)

```yaml
# .github/workflows/quality-react.yml (부분)
react-quality:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Set up Node.js 20
      uses: actions/setup-node@v4
      with:
        node-version: "20"
        cache: "npm"
        cache-dependency-path: package-lock.json

    - name: Install dependencies
      run: npm ci
      working-directory: .

    - name: ESLint
      run: npx eslint src/ --format=stylish --max-warnings=0
      working-directory: .

    - name: TypeScript type check
      run: npx tsc --noEmit --strict
      working-directory: .

    - name: Prettier format check
      run: npx prettier --check "src/**/*.{ts,tsx,css,json}"
      working-directory: .
```

### 2.4 스키마 검증 (Pydantic v2 모델 임포트 테스트)

D2.1에서 정의된 **37개 스키마**가 정상적으로 임포트되고 인스턴스화되는지 검증한다.

```yaml
# .github/workflows/quality-schema.yml (부분)
schema-validation:
  runs-on: ubuntu-latest
  needs: [python-quality]
  steps:
    - uses: actions/checkout@v4

    - name: Set up Python 3.11
      uses: actions/setup-python@v5
      with:
        python-version: "3.11"
        cache: "pip"

    - name: Install dependencies
      run: |
        pip install --upgrade pip
        pip install -r requirements.txt

    - name: Validate all Pydantic schemas
      run: python -m pytest tests/schemas/ -v --tb=short -q
```

**스키마 검증 테스트 예시** (`tests/schemas/test_schema_import.py`):

```python
"""D2.1 스키마 전체 임포트 및 기본 인스턴스화 검증."""
import pytest
from pydantic import ValidationError

# D2 스키마
from vamos_core.schemas.d2 import DecisionSchema, LogEventSchema

# D3 스키마
from vamos_core.schemas.d3 import (
    NodeCapabilityProfileSchema,
    NodeRequestEnvelope,
    NodeResponseEnvelope,
    ToolCallRegistrySchema,
    MCPBridgeLayerSchema,
)

# D4 스키마
from vamos_core.schemas.d4 import (
    ToolRegistryEntrySchema,
    BrainAdapterResponseSchema,
    InfraInvokeResultSchema,
    PromptCacheManagerSchema,
    RateLimitConfigSchema,
    BackupConfigSchema,
)

# D5, D6, D7 스키마... (동일 패턴)

SCHEMA_CLASSES = [
    DecisionSchema, LogEventSchema,
    NodeCapabilityProfileSchema, NodeRequestEnvelope,
    NodeResponseEnvelope, ToolCallRegistrySchema,
    MCPBridgeLayerSchema, ToolRegistryEntrySchema,
    BrainAdapterResponseSchema, InfraInvokeResultSchema,
    PromptCacheManagerSchema, RateLimitConfigSchema,
    BackupConfigSchema,
    # ... 나머지 스키마
]

@pytest.mark.parametrize("schema_cls", SCHEMA_CLASSES)
def test_schema_has_model_fields(schema_cls):
    """각 스키마가 Pydantic v2 모델 필드를 보유하는지 확인."""
    assert hasattr(schema_cls, "model_fields")
    assert len(schema_cls.model_fields) > 0

@pytest.mark.parametrize("schema_cls", SCHEMA_CLASSES)
def test_schema_json_schema_export(schema_cls):
    """JSON Schema 내보내기가 정상 동작하는지 확인."""
    json_schema = schema_cls.model_json_schema()
    assert "properties" in json_schema
    assert "title" in json_schema
```

---

## 3. 테스트 파이프라인

### 3.1 Python 단위/통합 테스트

```yaml
# .github/workflows/test-python.yml (부분)
python-test:
  runs-on: ubuntu-latest
  services:
    postgres:
      image: postgres:16
      env:
        POSTGRES_USER: vamos_test
        POSTGRES_PASSWORD: test_password
        POSTGRES_DB: vamos_test
      ports:
        - 5432:5432
      options: >-
        --health-cmd pg_isready
        --health-interval 10s
        --health-timeout 5s
        --health-retries 5

  steps:
    - uses: actions/checkout@v4

    - name: Set up Python 3.11
      uses: actions/setup-python@v5
      with:
        python-version: "3.11"
        cache: "pip"

    - name: Install dependencies
      run: |
        pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run unit tests with coverage
      run: |
        pytest tests/unit/ \
          --cov=vamos \
          --cov-report=xml:coverage-python-unit.xml \
          --cov-report=html:htmlcov-python-unit \
          --junitxml=junit-python-unit.xml \
          -v --tb=short
      env:
        VAMOS_ENV: test

    - name: Run integration tests
      run: |
        pytest tests/integration/ \
          --cov=vamos \
          --cov-append \
          --cov-report=xml:coverage-python-all.xml \
          --junitxml=junit-python-integration.xml \
          -v --tb=short -m "not slow"
      env:
        VAMOS_ENV: test
        DATABASE_URL: postgresql://vamos_test:test_password@localhost:5432/vamos_test

    - name: Upload coverage artifact
      uses: actions/upload-artifact@v4
      with:
        name: coverage-python
        path: coverage-python-all.xml
```

**pytest 설정** (`pyproject.toml`):

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "slow: 느린 테스트 (CI에서 선택적 실행)",
    "integration: 통합 테스트 (외부 서비스 필요)",
    "schema: 스키마 검증 테스트",
]
addopts = "--strict-markers -ra"
filterwarnings = ["error", "ignore::DeprecationWarning"]
```

### 3.2 Rust 테스트

```yaml
# .github/workflows/test-rust.yml (부분)
rust-test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Install Rust toolchain
      uses: dtolnay/rust-toolchain@stable

    - name: Cache cargo
      uses: actions/cache@v4
      with:
        path: |
          ~/.cargo/registry
          ~/.cargo/git
          src-tauri/target
        key: ${{ runner.os }}-cargo-test-${{ hashFiles('**/Cargo.lock') }}

    - name: Install Tauri system dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y \
          libwebkit2gtk-4.1-dev \
          libappindicator3-dev \
          librsvg2-dev \
          patchelf \
          libssl-dev

    - name: Run Rust tests
      run: |
        cargo test --manifest-path src-tauri/Cargo.toml \
          --all-targets --all-features -- --nocapture
      env:
        RUST_LOG: debug

    - name: Install cargo-tarpaulin for coverage
      run: cargo install cargo-tarpaulin

    - name: Generate Rust coverage
      run: |
        cargo tarpaulin --manifest-path src-tauri/Cargo.toml \
          --out xml --output-dir coverage-rust/
      continue-on-error: true

    - name: Upload coverage artifact
      uses: actions/upload-artifact@v4
      with:
        name: coverage-rust
        path: coverage-rust/
```

### 3.3 React 테스트

```yaml
# .github/workflows/test-react.yml (부분)
react-test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Set up Node.js 20
      uses: actions/setup-node@v4
      with:
        node-version: "20"
        cache: "npm"
        cache-dependency-path: package-lock.json

    - name: Install dependencies
      run: npm ci
      working-directory: .

    - name: Run vitest with coverage
      run: |
        npx vitest run \
          --coverage \
          --coverage.reporter=json-summary \
          --coverage.reporter=lcov \
          --reporter=junit \
          --outputFile=junit-react.xml
      working-directory: .
      env:
        CI: true

    - name: Upload coverage artifact
      uses: actions/upload-artifact@v4
      with:
        name: coverage-react
        path: coverage/
```

**vitest 설정** (`vitest.config.ts`):

```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json-summary', 'lcov'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.d.ts',
        '**/*.config.*',
      ],
      thresholds: {
        statements: 80,
        branches: 75,
        functions: 80,
        lines: 80,
      },
    },
  },
});
```

### 3.4 커버리지 리포트 합산

```yaml
# .github/workflows/coverage-report.yml (부분)
coverage-report:
  runs-on: ubuntu-latest
  needs: [python-test, rust-test, react-test]
  steps:
    - uses: actions/checkout@v4

    - name: Download all coverage artifacts
      uses: actions/download-artifact@v4
      with:
        path: coverage-artifacts/

    - name: Set up Python 3.11
      uses: actions/setup-python@v5
      with:
        python-version: "3.11"

    - name: Merge and report coverage
      run: |
        pip install coverage
        # Python 커버리지 합산
        python scripts/ci/merge_coverage.py \
          --python coverage-artifacts/coverage-python/coverage-python-all.xml \
          --rust coverage-artifacts/coverage-rust/cobertura.xml \
          --react coverage-artifacts/coverage-react/coverage-final.json \
          --output coverage-summary.json

    - name: Comment PR with coverage
      if: github.event_name == 'pull_request'
      uses: marocchino/sticky-pull-request-comment@v2
      with:
        header: coverage
        path: coverage-summary.md

    - name: Check minimum coverage thresholds
      run: |
        python scripts/ci/check_coverage_thresholds.py \
          --summary coverage-summary.json \
          --min-python 75 \
          --min-rust 60 \
          --min-react 80
```

**커버리지 임계값**:

| 언어 | 최소 커버리지 | 목표 커버리지 |
|------|-------------|-------------|
| Python | 75% | 85% |
| Rust | 80% | 80% |
| React | 80% | 80% |

---

## 4. 빌드 파이프라인

### 4.1 Tauri 빌드 (Windows/macOS/Linux)

```yaml
# .github/workflows/build-tauri.yml
name: "Build Tauri App"

on:
  push:
    branches: [main, release/*]
  pull_request:
    branches: [main, develop]

jobs:
  build-tauri:
    strategy:
      fail-fast: false
      matrix:
        include:
          - platform: "ubuntu-22.04"
            target: "x86_64-unknown-linux-gnu"
            artifact-name: "vamos-linux-x64"
          - platform: "windows-latest"
            target: "x86_64-pc-windows-msvc"
            artifact-name: "vamos-windows-x64"
          - platform: "macos-latest"
            target: "aarch64-apple-darwin"
            artifact-name: "vamos-macos-arm64"
          - platform: "macos-latest"
            target: "x86_64-apple-darwin"
            artifact-name: "vamos-macos-x64"

    runs-on: ${{ matrix.platform }}

    steps:
      - uses: actions/checkout@v4

      - name: Install Rust toolchain
        uses: dtolnay/rust-toolchain@stable
        with:
          targets: ${{ matrix.target }}

      - name: Set up Node.js 20
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"
          cache-dependency-path: package-lock.json

      - name: Install Linux dependencies
        if: matrix.platform == 'ubuntu-22.04'
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            libwebkit2gtk-4.1-dev \
            libappindicator3-dev \
            librsvg2-dev \
            patchelf \
            libssl-dev \
            libgtk-3-dev

      - name: Cache cargo
        uses: actions/cache@v4
        with:
          path: |
            ~/.cargo/registry
            ~/.cargo/git
            src-tauri/target
          key: ${{ runner.os }}-${{ matrix.target }}-cargo-${{ hashFiles('**/Cargo.lock') }}
          restore-keys: ${{ runner.os }}-${{ matrix.target }}-cargo-

      - name: Install frontend dependencies
        run: npm ci
        working-directory: .

      - name: Build frontend
        run: npm run build
        working-directory: .

      - name: Build Tauri app
        uses: tauri-apps/tauri-action@v0
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          TAURI_SIGNING_PRIVATE_KEY: ${{ secrets.TAURI_SIGNING_PRIVATE_KEY }}
          TAURI_SIGNING_PRIVATE_KEY_PASSWORD: ${{ secrets.TAURI_SIGNING_PRIVATE_KEY_PASSWORD }}
        with:
          tauriScript: npx tauri
          args: --target ${{ matrix.target }}

      - name: Upload build artifact
        uses: actions/upload-artifact@v4
        with:
          name: ${{ matrix.artifact-name }}
          path: |
            src-tauri/target/${{ matrix.target }}/release/bundle/**/*.msi
            src-tauri/target/${{ matrix.target }}/release/bundle/**/*.dmg
            src-tauri/target/${{ matrix.target }}/release/bundle/**/*.deb
            src-tauri/target/${{ matrix.target }}/release/bundle/**/*.AppImage
          retention-days: 7
```

### 4.2 Python 패키지 빌드

```yaml
# .github/workflows/build-python.yml (부분)
build-python:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Set up Python 3.11
      uses: actions/setup-python@v5
      with:
        python-version: "3.11"

    - name: Install build tools
      run: pip install build twine

    - name: Build wheel and sdist
      run: python -m build

    - name: Check package
      run: twine check dist/*

    - name: Upload artifacts
      uses: actions/upload-artifact@v4
      with:
        name: python-dist
        path: dist/
```

### 4.3 Docker 이미지 빌드 (V2+)

```yaml
# .github/workflows/build-docker.yml
name: "Build Docker Images (V2+)"

on:
  push:
    branches: [main, release/*]
    tags: ["v*"]

jobs:
  build-docker:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service:
          - name: "vamos-orange-core"
            dockerfile: "docker/orange-core/Dockerfile"
            context: "."
          - name: "vamos-blue-nodes"
            dockerfile: "docker/blue-nodes/Dockerfile"
            context: "."
          - name: "vamos-api-gateway"
            dockerfile: "docker/api-gateway/Dockerfile"
            context: "."

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}/${{ matrix.service.name }}
          tags: |
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha,prefix=
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: ${{ matrix.service.context }}
          file: ${{ matrix.service.dockerfile }}
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          build-args: |
            PYTHON_VERSION=3.11
            RUST_VERSION=stable
```

---

## 5. 릴리스 파이프라인

### 5.1 Semantic Versioning

VAMOS는 [Semantic Versioning 2.0.0](https://semver.org/) 규격을 따른다.

```
MAJOR.MINOR.PATCH[-pre.N]
```

| 변경 유형 | 버전 증가 | 예시 |
|-----------|----------|------|
| 하위 호환 깨지는 변경 | MAJOR | 1.0.0 → 2.0.0 |
| 새 기능 (하위 호환) | MINOR | 1.0.0 → 1.1.0 |
| 버그 수정 | PATCH | 1.0.0 → 1.0.1 |
| 프리릴리스 | pre suffix | 1.1.0-beta.1 |

**커밋 메시지 컨벤션** (Conventional Commits):

```
feat: 새 기능 추가 → MINOR
fix: 버그 수정 → PATCH
feat!: 또는 BREAKING CHANGE: → MAJOR
chore: 빌드/도구 관련 (릴리스 노트 제외)
docs: 문서 변경 (릴리스 노트 제외)
refactor: 리팩토링 (릴리스 노트 제외)
test: 테스트 추가/수정 (릴리스 노트 제외)
```

### 5.2 Changelog 자동 생성

```yaml
# .github/workflows/release.yml (부분)
changelog:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: Generate changelog
      uses: orhun/git-cliff-action@v3
      with:
        config: cliff.toml
        args: --verbose
      env:
        OUTPUT: CHANGELOG.md

    - name: Commit changelog
      run: |
        git config user.name "github-actions[bot]"
        git config user.email "github-actions[bot]@users.noreply.github.com"
        git add CHANGELOG.md
        git diff --staged --quiet || git commit -m "chore: update changelog"
        git push
```

**git-cliff 설정** (`cliff.toml`):

```toml
[changelog]
header = "# VAMOS Changelog\n\n"
body = """
{% for group, commits in commits | group_by(attribute="group") %}
### {{ group | upper_first }}
{% for commit in commits %}
- {{ commit.message | upper_first }} ({{ commit.id | truncate(length=7, end="") }})\
{% endfor %}
{% endfor %}\n
"""
trim = true

[git]
conventional_commits = true
filter_unconventional = true
commit_parsers = [
    { message = "^feat", group = "Features" },
    { message = "^fix", group = "Bug Fixes" },
    { message = "^perf", group = "Performance" },
    { message = "^refactor", group = "Refactoring" },
    { message = "^doc", group = "Documentation" },
    { message = "^test", group = "Testing" },
    { message = "^chore", skip = true },
]
```

### 5.3 GitHub Release + Tauri 바이너리 업로드

```yaml
# .github/workflows/release.yml
name: "Release"

on:
  push:
    tags: ["v*"]

permissions:
  contents: write

jobs:
  # 1) 품질 + 테스트 (재사용 워크플로우)
  quality:
    uses: ./.github/workflows/quality-all.yml

  test:
    uses: ./.github/workflows/test-all.yml
    needs: [quality]

  # 2) Tauri 크로스 플랫폼 빌드
  build-tauri:
    needs: [test]
    strategy:
      fail-fast: false
      matrix:
        include:
          - platform: "ubuntu-22.04"
            target: "x86_64-unknown-linux-gnu"
          - platform: "windows-latest"
            target: "x86_64-pc-windows-msvc"
          - platform: "macos-latest"
            target: "aarch64-apple-darwin"
          - platform: "macos-latest"
            target: "x86_64-apple-darwin"
    runs-on: ${{ matrix.platform }}
    steps:
      - uses: actions/checkout@v4

      - name: Install Rust toolchain
        uses: dtolnay/rust-toolchain@stable
        with:
          targets: ${{ matrix.target }}

      - name: Set up Node.js 20
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"
          cache-dependency-path: package-lock.json

      - name: Install Linux deps
        if: runner.os == 'Linux'
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            libwebkit2gtk-4.1-dev libappindicator3-dev \
            librsvg2-dev patchelf libssl-dev libgtk-3-dev

      - name: Install frontend deps & build
        run: |
          npm ci && npm run build

      - name: Build and release Tauri
        uses: tauri-apps/tauri-action@v0
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          TAURI_SIGNING_PRIVATE_KEY: ${{ secrets.TAURI_SIGNING_PRIVATE_KEY }}
          TAURI_SIGNING_PRIVATE_KEY_PASSWORD: ${{ secrets.TAURI_SIGNING_PRIVATE_KEY_PASSWORD }}
        with:
          tagName: ${{ github.ref_name }}
          releaseName: "VAMOS ${{ github.ref_name }}"
          releaseBody: "See [CHANGELOG.md](CHANGELOG.md) for details."
          releaseDraft: true
          prerelease: false
          args: --target ${{ matrix.target }}

  # 3) Changelog 및 Release 노트 최종화
  finalize-release:
    needs: [build-tauri]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Generate release notes
        uses: orhun/git-cliff-action@v3
        id: cliff
        with:
          config: cliff.toml
          args: --latest --strip header

      - name: Update release body
        uses: softprops/action-gh-release@v2
        with:
          tag_name: ${{ github.ref_name }}
          body: ${{ steps.cliff.outputs.content }}
          draft: false
```

### 5.4 Docker Registry Push (V2+)

```yaml
# release.yml 에 추가되는 V2+ 전용 Job
  push-docker:
    needs: [test]
    if: startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [vamos-orange-core, vamos-blue-nodes, vamos-api-gateway]
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract version from tag
        id: version
        run: echo "VERSION=${GITHUB_REF_NAME#v}" >> $GITHUB_OUTPUT

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          file: docker/${{ matrix.service }}/Dockerfile
          push: true
          tags: |
            ghcr.io/${{ github.repository }}/${{ matrix.service }}:${{ steps.version.outputs.VERSION }}
            ghcr.io/${{ github.repository }}/${{ matrix.service }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
          platforms: linux/amd64,linux/arm64
```

---

## 6. 배포 파이프라인 (V2+)

### 6.1 Docker Compose 배포 (V2)

```yaml
# .github/workflows/deploy-v2.yml
name: "Deploy V2 (Docker Compose)"

on:
  workflow_dispatch:
    inputs:
      environment:
        description: "배포 환경"
        required: true
        default: "staging"
        type: choice
        options:
          - staging
          - production
      version:
        description: "배포 버전 (e.g., 1.2.0)"
        required: true
        type: string

concurrency:
  group: deploy-${{ inputs.environment }}
  cancel-in-progress: false

jobs:
  deploy-v2:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - uses: actions/checkout@v4

      - name: Configure SSH
        uses: webfactory/ssh-agent@v0.9.0
        with:
          ssh-private-key: ${{ secrets.DEPLOY_SSH_KEY }}

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

      - name: Deploy via Docker Compose
        run: |
          ssh ${{ secrets.DEPLOY_HOST }} << 'ENDSSH'
            cd /opt/vamos
            docker compose pull
            docker compose up -d --remove-orphans
            docker compose ps
            # 헬스체크 대기
            sleep 10
            curl -f http://localhost:8080/health || exit 1
          ENDSSH

      - name: Post-deploy smoke test
        run: |
          ssh ${{ secrets.DEPLOY_HOST }} << 'ENDSSH'
            curl -sf http://localhost:8080/api/v1/health | jq .
            curl -sf http://localhost:8080/api/v1/schemas/version | jq .
          ENDSSH

      - name: Notify deployment
        if: always()
        uses: slackapi/slack-github-action@v1.26.0
        with:
          payload: |
            {
              "text": "VAMOS V2 ${{ inputs.version }} 배포 ${{ job.status }} (${{ inputs.environment }})"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

**Docker Compose 파일** (`deploy/docker-compose.yml`) 구조:

```yaml
# deploy/docker-compose.yml
version: "3.9"

services:
  orange-core:
    image: ghcr.io/vamos-ai/vamos-orange-core:${VAMOS_VERSION}
    ports:
      - "8080:8080"
    depends_on:
      postgres:
        condition: service_healthy
      qdrant:
        condition: service_healthy
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/vamos
      - QDRANT_URL=http://qdrant:6333
      - NEO4J_URL=bolt://neo4j:7687
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 15s
      timeout: 5s
      retries: 3

  blue-nodes:
    image: ghcr.io/vamos-ai/vamos-blue-nodes:${VAMOS_VERSION}
    depends_on:
      - orange-core
    environment:
      - ORANGE_CORE_URL=http://orange-core:8080

  postgres:
    image: postgres:16
    volumes:
      - postgres_data:/var/lib/postgresql/data
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
    volumes:
      - qdrant_data:/qdrant/storage
    ports:
      - "6333:6333"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/healthz"]
      interval: 10s
      timeout: 5s
      retries: 5

  neo4j:
    image: neo4j:5-community
    volumes:
      - neo4j_data:/data
    environment:
      NEO4J_AUTH: ${NEO4J_AUTH}
    ports:
      - "7474:7474"
      - "7687:7687"

volumes:
  postgres_data:
  qdrant_data:
  neo4j_data:
```

### 6.2 K8s 배포 (V3)

```yaml
# .github/workflows/deploy-v3.yml
name: "Deploy V3 (Kubernetes)"

on:
  workflow_dispatch:
    inputs:
      environment:
        description: "배포 환경"
        required: true
        type: choice
        options:
          - staging
          - production
      version:
        description: "배포 버전"
        required: true
        type: string

jobs:
  deploy-k8s:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - uses: actions/checkout@v4

      - name: Set up Helm
        uses: azure/setup-helm@v4
        with:
          version: "v3.14.0"

      - name: Configure kubectl
        uses: azure/setup-kubectl@v4
        with:
          version: "v1.29.0"

      - name: Set kubeconfig
        run: |
          mkdir -p $HOME/.kube
          echo "${{ secrets.KUBECONFIG }}" | base64 -d > $HOME/.kube/config

      - name: Helm upgrade (Blue-Green)
        run: |
          NAMESPACE="vamos-${{ inputs.environment }}"

          helm upgrade --install vamos \
            deploy/helm/vamos/ \
            --namespace $NAMESPACE \
            --create-namespace \
            --set global.image.tag=${{ inputs.version }} \
            --set global.environment=${{ inputs.environment }} \
            --set orangeCore.replicas=3 \
            --set blueNodes.replicas=5 \
            --set postgres.managed=true \
            --set qdrant.cloud=true \
            --set neo4j.aura=true \
            --wait \
            --timeout 10m

      - name: Verify rollout
        run: |
          NAMESPACE="vamos-${{ inputs.environment }}"
          kubectl rollout status deployment/vamos-orange-core -n $NAMESPACE --timeout=300s
          kubectl rollout status deployment/vamos-blue-nodes -n $NAMESPACE --timeout=300s

      - name: Run E2E smoke tests
        run: |
          NAMESPACE="vamos-${{ inputs.environment }}"
          ENDPOINT=$(kubectl get svc vamos-api-gateway -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
          python scripts/ci/e2e_smoke.py --endpoint "https://$ENDPOINT" --timeout 60

      - name: Rollback on failure
        if: failure()
        run: |
          NAMESPACE="vamos-${{ inputs.environment }}"
          helm rollback vamos -n $NAMESPACE
          echo "::warning::배포 실패 -- 자동 롤백 실행됨"
```

---

## 7. 보안 파이프라인

### 7.1 의존성 취약점 스캔

```yaml
# .github/workflows/security.yml
name: "Security Scan"

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: "0 9 * * 1"  # 매주 월요일 09:00 UTC

jobs:
  python-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install pip-audit
        run: pip install pip-audit

      - name: Run pip-audit
        run: |
          pip install -r requirements.txt
          pip-audit --strict --desc on --output pip-audit-report.json --format json
        continue-on-error: true

      - name: Upload audit report
        uses: actions/upload-artifact@v4
        with:
          name: pip-audit-report
          path: pip-audit-report.json

  rust-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install cargo-audit
        run: cargo install cargo-audit

      - name: Run cargo audit
        run: cargo audit --file src-tauri/Cargo.lock --json > cargo-audit-report.json
        continue-on-error: true

      - name: Upload audit report
        uses: actions/upload-artifact@v4
        with:
          name: cargo-audit-report
          path: cargo-audit-report.json

  npm-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js 20
        uses: actions/setup-node@v4
        with:
          node-version: "20"

      - name: Run npm audit
        run: |
          npm ci
          npm audit --json > npm-audit-report.json || true
        continue-on-error: true

      - name: Upload audit report
        uses: actions/upload-artifact@v4
        with:
          name: npm-audit-report
          path: npm-audit-report.json

  docker-scan:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: "fs"
          scan-ref: "."
          format: "sarif"
          output: "trivy-results.sarif"
          severity: "CRITICAL,HIGH"

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: "trivy-results.sarif"
```

### 7.2 비밀 키 노출 검사

```yaml
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Custom secret patterns check
        run: |
          # VAMOS 프로젝트 특화 비밀 키 패턴 검사
          PATTERNS=(
            "OPENAI_API_KEY\s*=\s*sk-"
            "ANTHROPIC_API_KEY\s*="
            "POSTGRES_PASSWORD\s*=\s*[^$]"
            "NEO4J_AUTH\s*=\s*neo4j/"
            "QDRANT_API_KEY\s*="
            "TAURI_SIGNING_PRIVATE_KEY\s*="
          )
          FOUND=0
          for pattern in "${PATTERNS[@]}"; do
            if grep -rn "$pattern" --include="*.py" --include="*.ts" \
                 --include="*.toml" --include="*.yaml" --include="*.yml" \
                 --exclude-dir=".git" --exclude-dir="node_modules" .; then
              echo "::error::비밀 키 패턴 감지: $pattern"
              FOUND=1
            fi
          done
          exit $FOUND
```

**`.gitleaks.toml`** 설정:

```toml
[extend]
useDefault = true

[[rules]]
id = "vamos-openai-key"
description = "OpenAI API Key"
regex = '''sk-[a-zA-Z0-9]{20,}'''
tags = ["key", "openai"]

[[rules]]
id = "vamos-db-password"
description = "Database password in config"
regex = '''(?i)(password|passwd|pwd)\s*[=:]\s*[^\s$\{]{8,}'''
tags = ["password", "database"]

[allowlist]
paths = [
    '''tests/fixtures/.*''',
    '''.*_test\.py''',
    '''.*\.example''',
]
```

### 7.3 라이선스 검사

```yaml
  license-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Python license check
        run: |
          pip install pip-licenses
          pip install -r requirements.txt
          pip-licenses --format=json --output-file=python-licenses.json
          # 금지 라이선스 검사
          pip-licenses --fail-on="GPL-3.0;AGPL-3.0;SSPL-1.0" \
            --allow-only="MIT;Apache-2.0;BSD-2-Clause;BSD-3-Clause;ISC;PSF-2.0;LGPL-2.1;LGPL-3.0;MPL-2.0" \
            || echo "::warning::허용되지 않은 라이선스 감지"

      - name: Set up Node.js 20
        uses: actions/setup-node@v4
        with:
          node-version: "20"

      - name: NPM license check
        run: |
          npm ci
          npx license-checker --json --out npm-licenses.json
          npx license-checker \
            --failOn "GPL-3.0;AGPL-3.0;SSPL-1.0" \
            --onlyAllow "MIT;Apache-2.0;BSD-2-Clause;BSD-3-Clause;ISC;0BSD;CC-BY-4.0;Unlicense;CC0-1.0"

      - name: Rust license check
        run: |
          cargo install cargo-deny
          cargo deny --manifest-path src-tauri/Cargo.toml check licenses
```

**`deny.toml`** (Rust):

```toml
[licenses]
unlicensed = "deny"
allow = [
    "MIT",
    "Apache-2.0",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "ISC",
    "Zlib",
    "Unicode-DFS-2016",
]
deny = [
    "GPL-3.0",
    "AGPL-3.0",
]
copyleft = "warn"
```

---

## 8. GitHub Actions 워크플로우 파일 예시 (통합 YAML)

아래는 PR 트리거로 실행되는 **통합 CI 워크플로우**이다. 개별 워크플로우를 하나의 파일에서 오케스트레이션한다.

```yaml
# .github/workflows/ci.yml
name: "VAMOS CI"

on:
  pull_request:
    branches: [main, develop]
    paths-ignore:
      - "docs/**"
      - "*.md"
      - ".github/ISSUE_TEMPLATE/**"
  push:
    branches: [develop]

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

env:
  PYTHON_VERSION: "3.11"
  NODE_VERSION: "20"
  RUST_TOOLCHAIN: "stable"
  CARGO_TERM_COLOR: always

jobs:
  # ============================================================
  # Stage 1: 코드 품질 (병렬 실행)
  # ============================================================
  python-quality:
    name: "Python Quality"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip
      - run: pip install ruff mypy pydantic[dotenv] -r requirements.txt -r requirements-dev.txt
      - run: ruff check backend/vamos_core/ --output-format=github
      - run: ruff format --check backend/vamos_core/
      - run: mypy backend/vamos_core/ --strict --ignore-missing-imports

  rust-quality:
    name: "Rust Quality"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: clippy, rustfmt
      - uses: actions/cache@v4
        with:
          path: |
            ~/.cargo/registry
            ~/.cargo/git
            src-tauri/target
          key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}
      - run: cargo fmt --manifest-path src-tauri/Cargo.toml -- --check
      - run: cargo clippy --manifest-path src-tauri/Cargo.toml --all-targets -- -D warnings

  react-quality:
    name: "React Quality"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm
          cache-dependency-path: package-lock.json
      - run: npm ci
        working-directory: .
      - run: npx eslint src/ --max-warnings=0
        working-directory: .
      - run: npx tsc --noEmit --strict
        working-directory: .

  schema-validation:
    name: "Schema Validation"
    runs-on: ubuntu-latest
    needs: [python-quality]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest tests/schemas/ -v --tb=short

  # ============================================================
  # Stage 2: 테스트 (병렬 실행, 품질 통과 후)
  # ============================================================
  python-test:
    name: "Python Tests"
    runs-on: ubuntu-latest
    needs: [python-quality, schema-validation]
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: vamos_test
          POSTGRES_PASSWORD: test_pass
          POSTGRES_DB: vamos_test
        ports: ["5432:5432"]
        options: --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - name: Run tests
        run: |
          pytest tests/ \
            --cov=vamos --cov-report=xml:coverage.xml \
            --junitxml=junit.xml -v --tb=short -m "not slow"
        env:
          DATABASE_URL: postgresql://vamos_test:test_pass@localhost:5432/vamos_test
      - uses: actions/upload-artifact@v4
        with:
          name: coverage-python
          path: coverage.xml

  rust-test:
    name: "Rust Tests"
    runs-on: ubuntu-latest
    needs: [rust-quality]
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - name: Install system deps
        run: |
          sudo apt-get update
          sudo apt-get install -y libwebkit2gtk-4.1-dev libappindicator3-dev \
            librsvg2-dev patchelf libssl-dev libgtk-3-dev
      - uses: actions/cache@v4
        with:
          path: |
            ~/.cargo/registry
            ~/.cargo/git
            src-tauri/target
          key: ${{ runner.os }}-cargo-test-${{ hashFiles('**/Cargo.lock') }}
      - run: cargo test --manifest-path src-tauri/Cargo.toml --all-targets

  react-test:
    name: "React Tests"
    runs-on: ubuntu-latest
    needs: [react-quality]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm
          cache-dependency-path: package-lock.json
      - run: npm ci
        working-directory: .
      - run: npx vitest run --coverage
        working-directory: .
      - uses: actions/upload-artifact@v4
        with:
          name: coverage-react
          path: coverage/

  # ============================================================
  # Stage 3: 보안 스캔 (병렬)
  # ============================================================
  security:
    name: "Security Scan"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      - run: |
          pip install pip-audit
          pip install -r requirements.txt
          pip-audit --strict || true

  # ============================================================
  # Stage 4: 빌드 확인 (테스트 통과 후, PR에서는 빌드만)
  # ============================================================
  build-check:
    name: "Build Check (${{ matrix.platform }})"
    runs-on: ${{ matrix.platform }}
    needs: [python-test, rust-test, react-test]
    strategy:
      fail-fast: false
      matrix:
        include:
          - platform: ubuntu-22.04
            target: x86_64-unknown-linux-gnu
          - platform: windows-latest
            target: x86_64-pc-windows-msvc
          - platform: macos-latest
            target: aarch64-apple-darwin
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          targets: ${{ matrix.target }}
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm
          cache-dependency-path: package-lock.json
      - name: Install Linux deps
        if: runner.os == 'Linux'
        run: |
          sudo apt-get update
          sudo apt-get install -y libwebkit2gtk-4.1-dev libappindicator3-dev \
            librsvg2-dev patchelf libssl-dev libgtk-3-dev
      - run: npm ci && npm run build
      - run: |
          cargo build --manifest-path src-tauri/Cargo.toml \
            --target ${{ matrix.target }} --release

  # ============================================================
  # Stage 5: CI 결과 요약
  # ============================================================
  ci-summary:
    name: "CI Summary"
    runs-on: ubuntu-latest
    needs: [build-check, security]
    if: always()
    steps:
      - name: Check all job results
        run: |
          echo "Python Test: ${{ needs.python-test.result }}"
          echo "Rust Test: ${{ needs.rust-test.result }}"
          echo "React Test: ${{ needs.react-test.result }}"
          echo "Security: ${{ needs.security.result }}"
          echo "Build Check: ${{ needs.build-check.result }}"

          if [[ "${{ needs.build-check.result }}" == "failure" ]]; then
            echo "::error::빌드 실패"
            exit 1
          fi
```

### 워크플로우 파일 구조 요약

```
.github/
  workflows/
    ci.yml                    # 통합 CI (PR/Push 트리거)
    release.yml               # 릴리스 (tag push 트리거)
    deploy-v2.yml             # V2 배포 (수동 트리거)
    deploy-v3.yml             # V3 배포 (수동 트리거)
    security.yml              # 보안 스캔 (주간 스케줄)
    nightly.yml               # 나이틀리 전체 테스트 (V2+)
```

### nightly.yml 워크플로우 스텁 (V3 구현 예정, PH-10)

> **NOTE**: nightly.yml은 V3에서 구현 예정. 아래는 구조 스텁이며, V2+에서 점진 확장한다.

```yaml
# .github/workflows/nightly.yml (V3 구현 예정 — 스텁)
name: "Nightly Full Test Suite"

on:
  schedule:
    - cron: '0 3 * * *'   # 매일 03:00 UTC (한국 12:00 KST)
  workflow_dispatch:       # 수동 트리거 허용

# TODO (V3): 아래 job 정의를 V3 구현 시 완성
# - full-unit-tests: Python + Rust + React 전체 단위 테스트
# - full-integration-tests: Pipeline/IPC/Storage/Safety 통합 테스트
# - full-e2e-tests: Playwright + Tauri WebDriver E2E
# - performance-benchmarks: 성능 벤치마크 (응답 시간, 메모리, 토큰 처리량)
# - security-audit: 보안 전체 스캔 (Snyk, npm audit, pip-audit, gitleaks)
# - report: Slack 알림 + 대시보드 업데이트
```

### 필수 GitHub Secrets

| Secret 이름 | 용도 | 버전 |
|-------------|------|------|
| `TAURI_SIGNING_PRIVATE_KEY` | Tauri 앱 서명 | V1+ |
| `TAURI_SIGNING_PRIVATE_KEY_PASSWORD` | 서명 키 패스워드 | V1+ |
| `DEPLOY_SSH_KEY` | 배포 서버 SSH | V2+ |
| `DEPLOY_HOST` | 배포 서버 호스트 | V2+ |
| `POSTGRES_USER` | DB 사용자 | V2+ |
| `POSTGRES_PASSWORD` | DB 패스워드 | V2+ |
| `QDRANT_API_KEY` | Qdrant API 키 | V2+ |
| `NEO4J_AUTH` | Neo4j 인증 | V2+ |
| `OPENAI_API_KEY` | OpenAI API 키 | V2+ |
| `KUBECONFIG` | K8s kubeconfig (base64) | V3 |
| `SLACK_WEBHOOK_URL` | 알림 Webhook | V2+ |

---

## 9. 문서 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| v1.0.0 | 2026-02-22 | 최초 작성 -- B6 CI/CD 파이프라인 설계 전체 | VAMOS Team |
| v1.0.1 | 2026-03-01 | PH-03: React 경로 `src/frontend/` → 프로젝트 루트(`.`)로 전체 정정 (B2 정본 `src/` 정합). 28개소 수정. | VAMOS Team |
| v1.0.2 | 2026-03-01 | PART1 LOW — PH-11: vitest threshold 70→80 정합 (B5 80%+ 목표와 일치), --min-react 70→80, 커버리지 임계값 표 React 70%→80%. PH-10: nightly.yml 스텁 YAML 추가 (V3 구현 예정). | VAMOS Team |

---

<\!-- END OF DOCUMENT -->
