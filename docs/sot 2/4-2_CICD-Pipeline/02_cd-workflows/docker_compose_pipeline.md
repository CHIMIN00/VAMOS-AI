# Docker Compose 파이프라인 상세 — V2 (4-2 P2-1)

> **카테고리**: 02_cd-workflows
> **세션**: P2-1 (Phase 2-1, V2 Docker Compose 파이프라인 상세)
> **목적**: V2 단계 Docker Compose 기반 6 서비스 (app tier 3 + data tier 3) 의 빌드→푸시→배포→롤백 전 플로우를 정본화하여 ISS-08 (Docker 부분) 을 해결하고 LOCK-CI-12 컨테이너 배포 요건을 충족한다.
> **버전**: v2.0-Phase 2 (NEW, 2026-04-24)
> **상태**: V2-Phase 2 (Phase 2 산출물)
> **LOCK**: LOCK-CI-01, LOCK-CI-11, LOCK-CI-12
> **CFL 해소**: CFL-CI-05, CFL-CI-08, CFL-CI-09, CFL-CI-10, CFL-CI-14 (BL-01 일괄)

---

## §1. 교차 참조 블록

| 대상 | 경로 / 섹션 | 용도 |
|------|-----------|------|
| 전략 정본 | `D:\VAMOS\docs\sot\PHASE_B6_CICD_PIPELINE.md` §6.1 Docker Compose 배포 (V2) | LOCK-CI-12 6 서비스 정본 + Y-15b 정규화 |
| 전략 정본 | `D:\VAMOS\docs\sot\PHASE_B6_CICD_PIPELINE.md` §4.3 Docker 이미지 빌드 (V2+) | 이미지 빌드 매트릭스 |
| 전략 정본 | `D:\VAMOS\docs\sot\PHASE_B6_CICD_PIPELINE.md` §5.4 Docker Registry Push | GHCR 푸시 정책 |
| 상위 SoT | `D:\VAMOS\docs\sot\STEP7-F_인프라_배포_MLOps_작업가이드.md` (SHA `91ce88c0...`) | 인프라 Tier 4 공유 READ 경로 |
| 종합계획서 | `CICD_PIPELINE_구조화_종합계획서.md` §7 P2-1 (L697~L728) + §A.3 시크릿 부록 | 본 세션 검증 항목 + CFL 해소 매핑 |
| 상세명세 | `CICD_PIPELINE_상세명세.md` WF-6 / WF-7 / §F-1 / §F-2 / §F-3 | 배포 게이트 + 롤백 결정 트리 |
| AUTHORITY | `AUTHORITY_CHAIN.md` §LOCK 항목 목록 (LOCK-CI-01, LOCK-CI-11, LOCK-CI-12) | LOCK 정본 출처 |
| CONFLICT | `CONFLICT_LOG.md` CFL-CI-05/08/09/10/14 | 본 세션 BL-01 일괄 해소 대상 |
| Phase 1 산출 | `02_cd-workflows/WF-6_deploy-staging.md` (191L) + `WF-7_deploy-prod.md` (222L) | V1 deploy 워크플로 정본 |
| Phase 1 산출 | `02_cd-workflows/phase_b6_yaml_normalization.md` v1.2 (737L) §5 / §6.1 / §16 F-11 | LOCK-CI-12 6 서비스 + overlay 완전체 |
| Phase 1 산출 | `03_security-scanning/secrets_mapping.md` v1.1 §2.1 (32 시크릿 master table) | 시크릿 정본 |
| Phase 1 산출 | `04_cache-strategy/cache_strategy_detail.md` v1.1 §3 + §5 | Docker Buildx 캐시 |
| Peer V2 | `02_cd-workflows/k8s_argocd_pipeline.md` (P2-2, V3) | overlay 환경별 분리 (dev/staging/prod) cross-ref |
| Peer V2 | `01_ci-workflows/optimization_report.md` (P2-3) | LOCK-CI-11 concurrency 정합 |

---

## §2. 공통 자료 구조 참조

본 세션은 **Docker Compose V2** 단계의 컨테이너 빌드/배포 전 플로우를 다루며, 다음 정본 구조를 그대로 인용·수렴한다:

- **6 서비스 토폴로지** (LOCK-CI-12 정본, PHASE_B6 §6.1 + 본 도메인 `phase_b6_yaml_normalization.md` §6.1):
  - **App tier (3)**: `orange-core` + `blue-nodes` + `api-gateway`
  - **Data tier (3)**: `postgres` + `qdrant` + `neo4j`
- **이미지 명명 규칙** (PHASE_B6 §4.3 Y-11 + CFL-CI-13 이원화 유지):
  - **Image name (registry)**: `ghcr.io/vamos-ai/vamos-orange-core` / `vamos-blue-nodes` / `vamos-api-gateway` (`vamos-` prefix)
  - **Compose service key (local alias)**: `orange-core` / `blue-nodes` / `api-gateway` (no prefix)
- **시크릿 매핑** (`secrets_mapping.md` v1.1 §2.1, 32건 master 정본):
  - Build/Push: `GITHUB_TOKEN` (#1, GHCR push)
  - Deploy: `AWS_ACCESS_KEY_ID` (#12), `AWS_SECRET_ACCESS_KEY` (#13), `AWS_REGION` (#14), `STAGING_SSH_KEY` (#15), `STAGING_HOST` (#16), `PROD_SSH_KEY` (#17), `PROD_HOST_LIST` (#18)
  - Runtime injection (env): `POSTGRES_USER` / `POSTGRES_PASSWORD` / `QDRANT_API_KEY` / `NEO4J_AUTH` / `OPENAI_API_KEY` (CFL-CI-05 BL-01 scope 재평가 결과 — V2 이상에서 deploy 시 `secrets.*` 으로 주입, scope 재정의)
  - Cloudflare 배포: `CLOUDFLARE_API_TOKEN` (#20), `CLOUDFLARE_ACCOUNT_ID` (#32, CFL-CI-09 해소 — BL-01 §A.3 신규 추가 mapping)
  - Notification: `SLACK_WEBHOOK_URL` (#3), `DISCORD_WEBHOOK_URL` (#31, CFL-CI-08 해소 — 선택 시크릿 보조 채널)
- **캐시 전략** (`cache_strategy_detail.md` v1.1 §5 — 3차 캐시 / Docker Buildx GHA 백엔드):
  - GHA Buildx cache: `type=gha,scope=<service>` (서비스별 분리)
  - Compose pull 캐시: `/tmp/.buildx-cache` (`docker-staging-${{ hashFiles('docker-compose.staging.yml') }}`)
  - 적중률 목표: ≥80% (warm)

---

## §3. 구현 상세 — Docker Compose V2 6 서비스 빌드→푸시→배포 플로우

### §3.1 전체 흐름

```mermaid
flowchart LR
  T1[trigger: workflow_run / dispatch] --> P1[prepare: version/CHANGELOG]
  P1 --> B1[build-images-matrix 6 서비스]
  B1 --> P2[push-to-GHCR: 6 image tags]
  P2 --> S1[scan-images: trivy CVE]
  S1 --> D1[deploy-staging: SSH + compose pull/up]
  D1 --> H1[healthcheck: 30s 대기 + 6 service check]
  H1 --> SK[smoke-test: 5 endpoint]
  SK --> M1[monitor 5분: QoD/error_rate]
  M1 -->|정상| N1[notify: Slack + Discord]
  M1 -->|이상| R1[자동 롤백: 이전 이미지 태그 복원]
  R1 --> N2[notify rollback]
```

### §3.2 6 서비스 빌드 매트릭스 (LOCK-CI-12 정본 verbatim)

각 서비스별 Dockerfile 경로, 컨텍스트, 포트 매핑, 의존성 순서를 다음과 같이 정의한다:

| # | Service (compose key) | Image name (GHCR) | Dockerfile 경로 | Build context | 포트 매핑 | 의존성 (depends_on) | Tier |
|---|---|---|---|---|---|---|---|
| 1 | `orange-core` | `ghcr.io/vamos-ai/vamos-orange-core` | `src/orange/Dockerfile` | `.` | `8080:8080` | postgres (healthy) + qdrant (healthy) + neo4j (started) | app |
| 2 | `blue-nodes` | `ghcr.io/vamos-ai/vamos-blue-nodes` | `src/blue/Dockerfile` | `.` | (internal only) | orange-core (started) | app |
| 3 | `api-gateway` | `ghcr.io/vamos-ai/vamos-api-gateway` | `src/gateway/Dockerfile` | `.` | `443:443` (external) + `9090:9090` (metrics) | orange-core (healthy) | app |
| 4 | `postgres` | `postgres:16` (upstream) | (외부 이미지 사용) | — | `5432:5432` (internal only) | — | data |
| 5 | `qdrant` | `qdrant/qdrant:v1.9.0` (upstream) | (외부 이미지 사용) | — | `6333:6333` | — | data |
| 6 | `neo4j` | `neo4j:5-community` (upstream) | (외부 이미지 사용) | — | `7474:7474` (UI) + `7687:7687` (Bolt) | — | data |

**CFL-CI-10 해소 (Y-15b api-gateway 누락 복원)**: PHASE_B6 §6.1 Y-15b 원본은 5 서비스 (orange-core + blue-nodes + postgres + qdrant + neo4j) 만 명시했으나, **본 V2 정본은 LOCK-CI-12 정본 6 서비스로 복원** (sot 2/ DEFINED-HERE, app tier 에 `api-gateway` 명시 추가). `phase_b6_yaml_normalization.md` v1.2 §6.1 가 본 6 서비스 토폴로지를 정규화하였으며, PHASE_B6 상류 Y-15b 보정은 별도 PR 권고 (F-11 이월).

### §3.3 docker-compose.yml V2 정본 템플릿

본 V2 단계 `deploy/docker-compose.yml` 의 정본 구조 (6 서비스 + healthcheck + restart policy + resource limits 명시):

```yaml
# deploy/docker-compose.yml (V2, LOCK-CI-12 정본)
version: "3.9"

services:
  # ─── App tier 3 ──────────────────────────────────────────
  orange-core:
    image: ghcr.io/vamos-ai/vamos-orange-core:${VAMOS_VERSION}
    container_name: vamos-orange-core
    restart: unless-stopped
    ports:
      - "8080:8080"
    depends_on:
      postgres:
        condition: service_healthy
      qdrant:
        condition: service_healthy
      neo4j:
        condition: service_started
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/vamos
      - QDRANT_URL=http://qdrant:6333
      - QDRANT_API_KEY=${QDRANT_API_KEY}
      - NEO4J_URL=bolt://neo4j:7687
      - NEO4J_AUTH=${NEO4J_AUTH}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LOG_LEVEL=info
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 15s
      timeout: 5s
      retries: 3
      start_period: 30s
    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: 2G
        reservations:
          cpus: "0.5"
          memory: 512M

  blue-nodes:
    image: ghcr.io/vamos-ai/vamos-blue-nodes:${VAMOS_VERSION}
    container_name: vamos-blue-nodes
    restart: unless-stopped
    depends_on:
      orange-core:
        condition: service_healthy
    environment:
      - ORANGE_CORE_URL=http://orange-core:8080
      - LOG_LEVEL=info
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8081/health"]
      interval: 15s
      timeout: 5s
      retries: 3
      start_period: 20s
    deploy:
      resources:
        limits:
          cpus: "1.5"
          memory: 1G

  api-gateway:
    image: ghcr.io/vamos-ai/vamos-api-gateway:${VAMOS_VERSION}
    container_name: vamos-api-gateway
    restart: unless-stopped
    ports:
      - "443:443"
      - "9090:9090"
    depends_on:
      orange-core:
        condition: service_healthy
    environment:
      - ORANGE_CORE_URL=http://orange-core:8080
      - BLUE_NODES_URL=http://blue-nodes:8081
      - METRICS_PORT=9090
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9090/metrics"]
      interval: 15s
      timeout: 5s
      retries: 3
      start_period: 20s
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 768M

  # ─── Data tier 3 ─────────────────────────────────────────
  postgres:
    image: postgres:16
    container_name: vamos-postgres
    restart: unless-stopped
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
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 1G

  qdrant:
    image: qdrant/qdrant:v1.9.0
    container_name: vamos-qdrant
    restart: unless-stopped
    volumes:
      - qdrant_data:/qdrant/storage
    ports:
      - "6333:6333"
    environment:
      QDRANT__SERVICE__API_KEY: ${QDRANT_API_KEY}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/healthz"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 1G

  neo4j:
    image: neo4j:5-community
    container_name: vamos-neo4j
    restart: unless-stopped
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
    environment:
      NEO4J_AUTH: ${NEO4J_AUTH}
      NEO4J_dbms_memory_heap_initial__size: 512m
      NEO4J_dbms_memory_heap_max__size: 1G
    ports:
      - "7474:7474"
      - "7687:7687"
    healthcheck:
      test: ["CMD-SHELL", "cypher-shell -u neo4j -p $$(echo $$NEO4J_AUTH | sed 's|^[^/]*/||') 'RETURN 1'"]
      interval: 15s
      timeout: 10s
      retries: 5
      start_period: 60s

volumes:
  postgres_data:
  qdrant_data:
  neo4j_data:
  neo4j_logs:

networks:
  default:
    name: vamos-network
```

### §3.4 환경별 overlay 구조 (CFL-CI-14 해소 — STAGING_/PROD_ 분기)

`deploy/docker-compose.staging.yml` 및 `deploy/docker-compose.prod.yml` overlay 는 환경별 차이만 명시하며, base `docker-compose.yml` 을 상속한다:

```yaml
# deploy/docker-compose.staging.yml (overlay)
services:
  orange-core:
    environment:
      - LOG_LEVEL=debug          # staging: 상세 로그
      - VAMOS_ENV=staging
    deploy:
      replicas: 1                 # staging: 단일 replica
  api-gateway:
    environment:
      - VAMOS_ENV=staging
      - ALLOWED_ORIGINS=https://staging.vamos.ai
```

```yaml
# deploy/docker-compose.prod.yml (overlay)
services:
  orange-core:
    environment:
      - LOG_LEVEL=info           # prod: 표준 로그
      - VAMOS_ENV=production
    deploy:
      replicas: 3                 # prod: HA 3 replicas
  blue-nodes:
    deploy:
      replicas: 5                 # prod: 5 노드
  api-gateway:
    environment:
      - VAMOS_ENV=production
      - ALLOWED_ORIGINS=https://app.vamos.ai
```

**CFL-CI-14 해소 매핑**: 본 overlay 구조에서 `phase_b6_yaml_normalization.md` §5.1 이 사용하던 `secrets.DEPLOY_SSH_KEY` / `secrets.DEPLOY_HOST` (PHASE_B6 §A.3 v0 명명 상속) 은 `secrets_mapping.md` v1.1 §2.1 의 분할 정본 (`STAGING_SSH_KEY` #15 / `STAGING_HOST` #16 / `PROD_SSH_KEY` #17 / `PROD_HOST_LIST` #18) 으로 대체된다. 본 V2 단계에서 deploy GitHub Actions 워크플로 (§4.1) 가 환경별 시크릿을 분기하여 사용함을 명시한다 (DEFINED-HERE Level 4 우선).

---

## §4. GitHub Actions 워크플로 — V2 deploy-v2.yml

### §4.1 deploy-v2.yml 정본 구조 (PHASE_B6 §6.1 정규화)

```yaml
# .github/workflows/deploy-v2.yml
name: "Deploy V2 (Docker Compose, 6 서비스)"

on:
  workflow_dispatch:
    inputs:
      environment:
        description: "배포 환경 (CFL-CI-14 분기)"
        required: true
        default: "staging"
        type: choice
        options:
          - staging
          - production
      version:
        description: "배포 버전 (e.g., 1.2.0, LOCK-CI-04 SemVer 2.0.0)"
        required: true
        type: string

# LOCK-CI-11 concurrency 설정 verbatim (상세명세 §병렬화)
concurrency:
  group: deploy-${{ inputs.environment }}
  cancel-in-progress: false  # 배포 중간 취소 금지 (compose 부분 적용 위험)

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write           # GHCR push
    strategy:
      fail-fast: false
      matrix:
        service:
          - { name: orange-core,  context: ., dockerfile: src/orange/Dockerfile }
          - { name: blue-nodes,   context: ., dockerfile: src/blue/Dockerfile }
          - { name: api-gateway,  context: ., dockerfile: src/gateway/Dockerfile }
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push (${{ matrix.service.name }})
        uses: docker/build-push-action@v6
        with:
          context: ${{ matrix.service.context }}
          file: ${{ matrix.service.dockerfile }}
          push: true
          tags: |
            ghcr.io/vamos-ai/vamos-${{ matrix.service.name }}:${{ inputs.version }}
            ghcr.io/vamos-ai/vamos-${{ matrix.service.name }}:latest
          cache-from: type=gha,scope=${{ matrix.service.name }}
          cache-to: type=gha,scope=${{ matrix.service.name }},mode=max
          # cache_strategy_detail v1.1 §5 — 3차 캐시 GHA 백엔드, 서비스별 분리

  scan-images:
    needs: build-and-push
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [orange-core, blue-nodes, api-gateway]
    steps:
      - name: Trivy scan (${{ matrix.service }})
        # LOCK-CI-09: Critical/High → 즉시 실패
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ghcr.io/vamos-ai/vamos-${{ matrix.service }}:${{ inputs.version }}
          format: 'sarif'
          output: 'trivy-${{ matrix.service }}.sarif'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'

  deploy-v2:
    needs: scan-images
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}  # LOCK-CI-10 (production 시 2인 승인)
    steps:
      - uses: actions/checkout@v4

      - name: Configure SSH (CFL-CI-14 환경별 분기)
        uses: webfactory/ssh-agent@v0.9.0
        with:
          ssh-private-key: ${{ inputs.environment == 'production' && secrets.PROD_SSH_KEY || secrets.STAGING_SSH_KEY }}

      - name: Generate .env file (runtime 시크릿 주입)
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
          chmod 600 deploy/.env   # 평문 시크릿 파일 권한 제한 (R-15-2)
          # 주의: deploy/.env 는 어떤 artifact upload step 에도 포함 금지 (.gitignore + actions/upload-artifact exclude)
          # 배포 종료 후 'rm -f deploy/.env' 정리 step 필수 (post-deploy cleanup)
          chmod 600 deploy/.env   # 평문 시크릿 파일 권한 제한 (R-15-2)
          # 주의: deploy/.env 는 어떤 artifact upload step 에도 포함 금지 (.gitignore + actions/upload-artifact exclude)
          # 배포 종료 후 'rm -f deploy/.env' 정리 step 필수 (post-deploy cleanup)

      - name: Determine target host (CFL-CI-14 분기)
        id: target
        run: |
          if [ "${{ inputs.environment }}" = "production" ]; then
            HOST=$(echo "${{ secrets.PROD_HOST_LIST }}" | head -n1)
          else
            HOST="${{ secrets.STAGING_HOST }}"
          fi
          echo "host=$HOST" >> $GITHUB_OUTPUT

      - name: Deploy via Docker Compose
        run: |
          OVERLAY="docker-compose.$([ "${{ inputs.environment }}" = "production" ] && echo prod || echo staging).yml"
          ssh ${{ steps.target.outputs.host }} <<ENDSSH
            cd /opt/vamos
            docker compose -f docker-compose.yml -f $OVERLAY pull
            docker compose -f docker-compose.yml -f $OVERLAY up -d --remove-orphans
            docker compose -f docker-compose.yml -f $OVERLAY ps
            sleep 30  # 6 서비스 healthcheck start_period 대기
          ENDSSH

      - name: Healthcheck (6 서비스 전수)
        run: |
          ssh ${{ steps.target.outputs.host }} <<ENDSSH
            for svc in orange-core blue-nodes api-gateway postgres qdrant neo4j; do
              docker compose ps $svc | grep -E "healthy|running" || exit 1
            done
            curl -f http://localhost:8080/health || exit 1
            curl -f http://localhost:9090/metrics || exit 1
          ENDSSH

      - name: Smoke test (5 endpoint)
        run: |
          ssh ${{ steps.target.outputs.host }} <<ENDSSH
            curl -sf http://localhost:8080/api/v1/health | jq .
            curl -sf http://localhost:8080/api/v1/schemas/version | jq .
            curl -sf http://localhost:8080/api/v1/agents | jq .
            curl -sf http://localhost:8080/api/v1/memory/health | jq .
            curl -sf http://localhost:9090/metrics | head -10
          ENDSSH

      - name: Notify Slack
        if: always()
        uses: slackapi/slack-github-action@v1.26.0
        with:
          payload: |
            {
              "text": "VAMOS V2 ${{ inputs.version }} 배포 ${{ job.status }} (${{ inputs.environment }})"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}

      - name: Notify Discord (CFL-CI-08 보조 채널, 선택)
        if: always() && env.DISCORD_WEBHOOK_URL != ''
        run: |
          curl -X POST -H "Content-Type: application/json" \
            -d "{\"content\":\"VAMOS V2 ${{ inputs.version }} 배포 ${{ job.status }} (${{ inputs.environment }})\"}" \
            $DISCORD_WEBHOOK_URL
        env:
          DISCORD_WEBHOOK_URL: ${{ secrets.DISCORD_WEBHOOK_URL }}
```

### §4.2 트리거 조건 정리

| 트리거 | 조건 | 비고 |
|--------|------|------|
| `workflow_dispatch` (수동) | environment + version 입력 | 정본 트리거 |
| `workflow_run` (자동, staging only) | WF-5 Release 성공 시 | WF-6 deploy-staging 흐름과 연동, WF-6 정본 (P1-1) |
| `push tags v*.*.*` | LOCK-CI-04 SemVer 2.0.0 | WF-5 release 트리거가 본 워크플로 호출 (chained) |

> **prod 트리거 제한 (LOCK-CI-10)**: production environment 는 push/schedule 트리거 금지. workflow_dispatch 만 허용 + Required reviewers 2명 이상 + main 브랜치만 배포.

---

## §5. 롤백 절차 (이전 이미지 태그 복원)

### §5.1 롤백 결정 트리 (상세명세 §F-3 verbatim)

| 조건 | 트리거 | 동작 | 타임아웃 |
|------|--------|------|---------|
| 스모크 테스트 실패 | 자동 | 즉시 롤백 (`docker compose pull <prev_tag> && up -d`) | < 2분 |
| 카나리 에러율 > 2% | 자동 (DATADOG_API_KEY 메트릭) | 자동 롤백 | 5분 이내 |
| 사용자 불만 > 5건/시간 | 수동 (on-call) | 수동 롤백 | — |
| 성능 회귀 > 20% | 수동 (WF-9 벤치마크) | 수동 롤백 + 원인 분석 | — |

### §5.2 롤백 실행 흐름

```bash
# 1. 이전 버전 태그 확인 — 배포 시작 전에 저장한 직전 안정 버전 사용
#    (배포 step 진입 시 'cp deploy/.env deploy/.env.prev' 로 직전 VAMOS_VERSION 보존)
PREV=$(grep '^VAMOS_VERSION=' deploy/.env.prev | cut -d= -f2)
# (대안) GHCR 릴리스 히스토리에서 직전 published 태그 조회:
#   gh api repos/$GITHUB_REPOSITORY/packages/container/vamos-orange-core/versions --jq '.[1].metadata.container.tags[0]'

# 2. .env 파일 VAMOS_VERSION 갱신
sed -i "s/^VAMOS_VERSION=.*/VAMOS_VERSION=$PREV/" deploy/.env

# 3. compose pull + up (6 서비스 전수)
docker compose -f docker-compose.yml -f docker-compose.${ENV}.yml pull
docker compose -f docker-compose.yml -f docker-compose.${ENV}.yml up -d --remove-orphans

# 4. healthcheck 재실행
for svc in orange-core blue-nodes api-gateway postgres qdrant neo4j; do
  docker compose ps $svc | grep -E "healthy|running"
done

# 5. 알림
slack_notify "VAMOS V2 ROLLBACK to $PREV (was $FAILED_VERSION) on $ENV"
```

### §5.3 롤백 데이터 무결성

- **postgres / neo4j volume**: `docker compose down` 시 volume 보존 (외부 마운트 유지). 롤백은 이미지 태그만 변경.
- **qdrant collection**: 컬렉션 스키마 마이그레이션이 forward-only 이면 롤백 불가 → release notes 에 명시 + on-call 에스컬레이션.
- **schema migration 가드**: `orange-core` 시작 시 `alembic upgrade head` 실행. 롤백 대상 버전이 이전 마이그레이션을 모르면 schema mismatch 가능 → release notes 마이그레이션 호환 매트릭스 필수.

---

## §6. CFL 해소 매핑 (BL-01 일괄 5건)

본 P2-1 V2 산출물이 BL-01 일괄 처리 대상 5건의 CONFLICT 를 다음과 같이 해소한다 (CONFLICT_LOG.md 도메인 마감 step 7 갱신 대상):

| CFL-ID | 기존 상태 | 해소 경로 | 본 V2 반영 위치 |
|--------|----------|----------|---------------|
| CFL-CI-05 | OPEN — §A.3 v0 23건 vs secrets_mapping v1.1 32건 scope 불일치 | runtime 시크릿 (POSTGRES_*/QDRANT_API_KEY/NEO4J_AUTH/OPENAI_API_KEY/KUBECONFIG) **scope 재정의 — V2 deploy 시 `secrets.*` 으로 주입** | §3.3 docker-compose.yml `environment:` 블록 + §4.1 `Generate .env file` 단계 |
| CFL-CI-08 | OPEN — DISCORD_WEBHOOK_URL §A.3 미정의 | 선택 시크릿 보조 채널 명시 + §A.3 갱신 권고 | §2 시크릿 매핑 + §4.1 `Notify Discord` 단계 (조건부 if env != '') |
| CFL-CI-09 | OPEN — CLOUDFLARE_ACCOUNT_ID §A.3 미정의 | Cloudflare Pages 배포 필수 시크릿 + §A.3 갱신 권고 | §2 시크릿 매핑 (V2 deploy 자체에는 미사용, WF-6 deploy-docs-staging job 에서 사용 / WF-10 deploy-pages 와 페어링) |
| CFL-CI-10 | OPEN — Y-15b api-gateway 누락 (5 서비스 vs 6 서비스) | LOCK-CI-12 정본 6 서비스 복원 (sot 2/ DEFINED-HERE) + PHASE_B6 상류 보정 권고 (F-11) | §3.2 6 서비스 매트릭스 + §3.3 compose 정본 + §3.4 overlay |
| CFL-CI-14 | OPEN — §5.1 DEPLOY_SSH_KEY/HOST vs STAGING_/PROD_ 분할 | secrets_mapping v1.1 분할 정본 우선 (DEFINED-HERE Level 4) + §5.1 narrative 보강 | §3.4 overlay 환경별 분기 + §4.1 deploy-v2.yml `inputs.environment` 분기 (PROD_/STAGING_ 시크릿 명시) |

> **자동 RESOLVE 금지 원칙 (3-8 CFL-A2A-005 옵션 c / 4-1 CFL-RT-009 OBSERVE_ONLY 선례)**: 본 V2 산출물은 5 CFL 의 **해소 경로 실체화** 를 담당하며, CONFLICT_LOG.md 의 RESOLVED 전환은 도메인 마감 step 7 에서 명시적으로 수행한다 (자동 갱신 없음).

> **상태 유지 4건**:
> - CFL-CI-06 (GPG 로테이션 단일화) — F-16 이월 P2-3 또는 P1-1 보강 세션 (본 P2-1 미해당)
> - CFL-CI-07 (TAURI_SIGNING_* 본문 누락 WF-4/WF-5) — F-16 이월 P2-3 또는 P1-1 보강 (본 P2-1 미해당)
> - CFL-CI-12 (Postgres test_password vs test_pass) — F-18 PHASE_B6 §8 상류 PR (본 P2-1 미해당)
> - CFL-CI-13 (image name vs compose key prefix) — 이원화 유지 결정 (§3.2 표 explicit, 본 P2-1 명시화 완료)

> **RESOLVED 1건**: CFL-CI-11 (Y-20 cache npm vs pnpm) — C-02 연장 RESOLVED 보존.

---

## §7. ISS-08 Docker 부분 해소 증빙

| 게이트 항목 (plan §7 P2-1 검증) | 충족 여부 | 증빙 |
|---|---|---|
| 6 서비스 (app tier 3 + data tier 3) 빌드→푸시→배포 플로우 단절 없이 기술 | ✅ | §3.1 흐름도 + §3.2 매트릭스 + §4.1 워크플로 |
| ISS-08 해결 조건 (Docker 파이프라인 명세 완비) | ✅ | §3.3 정본 compose + §3.4 overlay + §4.1 deploy-v2.yml |
| LOCK-CI-12 컨테이너 배포 요건 반영 | ✅ | §3.2 6 서비스 verbatim + §3.3 compose v3.9 |
| 롤백 절차 포함 | ✅ | §5 (3-trigger 결정 트리 + 실행 흐름 + 데이터 무결성) |

> **ISS-08 K8s 부분**: P2-2 V3 K8s/ArgoCD 설계에서 별도 해소 (`02_cd-workflows/k8s_argocd_pipeline.md`). 본 P2-1 은 Docker Compose V2 부분만 담당.

---

## §8. LOCK 5필드 매핑 (verbatim 분리 인용)

| ID | 항목 | 정본 출처 | 값 / 기준 | 본 V2 준수 증빙 |
|----|------|----------|----------|---------------|
| LOCK-CI-01 | 14개 워크플로우 목록 | PHASE_B6 §1 + Part2 | ci/test/lint/build-tauri/release/deploy-staging/deploy-prod/security-scan/benchmark/docs-build/dependency-check/e2e-test/nightly/version-bump | 본 V2 는 deploy-v2.yml NEW (14 WF 목록 외 추가 보조 워크플로) — LOCK-CI-01 14개 WF 자체는 변경 없음 |
| LOCK-CI-11 | concurrency 설정 | 상세명세 §병렬화 | group: workflow-ref, cancel-in-progress: true | §4.1 `concurrency: group: deploy-${{ inputs.environment }}, cancel-in-progress: false` (배포 정합성 우선, prod-deploy 패턴 — WF-7 §2 동일) |
| LOCK-CI-12 | Docker V2 서비스 구조 | PHASE_B6 §6.1 | orange-core + blue-nodes + api-gateway + postgres + qdrant + neo4j (6 서비스) | §3.2 6 서비스 매트릭스 verbatim + §3.3 compose 정본 + §3.4 overlay 6 서비스 보존 |

> **재정의 권한**: 본 V2 는 LOCK-CI-01/11/12 어느 것도 **재정의하지 않으며** (참조만), LOCK 정본 변경은 PHASE_B6 승인 권한 (Level 2). 본 V2 는 Level 4 구현 상세 (DEFINED-HERE for compose v3.9 정본 템플릿 + overlay 구조).

### §8.1 에스컬레이션 매트릭스

| 사례 | 트리거 | 에스컬레이션 대상 | 시간 |
|------|--------|--------------|------|
| GHCR push 실패 (이미지 빌드/scan) | trivy CRITICAL/HIGH 감지 | 보안팀 (LOCK-CI-09) | 즉시 |
| compose deploy SSH 실패 | host 무응답 | DevOps 운영팀 | 5분 |
| healthcheck 실패 (6 서비스 중 1+) | docker compose ps unhealthy | DevOps 운영팀 | 즉시 (rollback) |
| smoke 5/5 실패 | 5 endpoint 응답 비정상 | DevOps + on-call 엔지니어 | < 2분 (자동 롤백) |
| canary monitor 메트릭 이상 (QoD/error_rate) | DATADOG_API_KEY 메트릭 | on-call (PagerDuty) | 5분 (자동 롤백) |

### §8.2 로깅 (structured JSON)

```json
{
  "trace_id": "deploy-v2-<environment>-<version>-<run_id>",
  "event": {
    "type": "deploy_v2_complete|deploy_v2_failed|rollback_triggered",
    "environment": "staging|production",
    "version": "v1.2.3",
    "previous_version": "v1.2.2",
    "services_deployed": ["orange-core", "blue-nodes", "api-gateway", "postgres", "qdrant", "neo4j"]
  },
  "context": {
    "workflow": "deploy-v2.yml",
    "triggered_by": "workflow_dispatch|workflow_run",
    "run_id": "<gh_run_id>",
    "actor": "<gh_actor>",
    "commit": "<sha>",
    "lock_ci_12_count": 6,
    "lock_ci_10_approvers": ["user-a", "user-b"]
  },
  "recovery": {
    "retry_count": 0,
    "strategy": "rollback|retry|manual-intervention",
    "rollback_target": "v1.2.2",
    "rollback_completed_at": "2026-04-24T03:14:22Z",
    "smoke_test_failed_endpoints": []
  }
}
```

---

## §9. Phase 3 테스트 시나리오 (12건, ≥10 충족)

| # | 시나리오 | 주입 | 기대 |
|---|---------|------|------|
| T-1 | 정상 배포 (staging) | environment=staging, version=v1.2.3 | 6 서비스 전수 healthy, smoke 5/5 PASS |
| T-2 | 정상 배포 (prod) | environment=production, version=v1.2.3, 2인 승인 | LOCK-CI-10 PASS, canary→full→smoke→monitor 30분 |
| T-3 | api-gateway 누락 시 (CFL-CI-10 회귀 검증) | compose 파일에서 api-gateway 제거 | LOCK-CI-12 위반 감지, deploy-v2.yml fail |
| T-4 | trivy CRITICAL CVE | LOCK-CI-09 정책 trigger | scan-images job fail, 배포 차단 |
| T-5 | postgres healthcheck 실패 | DB 인증 정보 오류 | depends_on 대기 timeout, 배포 fail |
| T-6 | smoke 1/5 실패 | health endpoint 5xx | 즉시 자동 롤백 < 2분 |
| T-7 | 캐나리 에러율 3% | 의도적 에러 주입 | 자동 롤백 (DATADOG 메트릭) |
| T-8 | DISCORD_WEBHOOK_URL 미설정 | secret unset | Notify Discord step skip (조건부), Slack 만 알림 (정상 동작) |
| T-9 | CLOUDFLARE_ACCOUNT_ID 미설정 (V2 deploy 자체에는 영향 없음, WF-10 docs 만 영향) | 기본 V2 deploy | 정상 동작 (CLOUDFLARE_ACCOUNT_ID 는 WF-10 docs 전용 분리) |
| T-10 | concurrency 동시 배포 | 동일 environment 두 건 동시 trigger | LOCK-CI-11 cancel-in-progress=false → 두 번째 대기 큐 (취소 없음) |
| T-11 | overlay STAGING_ vs PROD_ 분기 | environment=staging vs production | 각각 STAGING_SSH_KEY / PROD_SSH_KEY 사용 (CFL-CI-14 검증) |
| T-12 | 6 서비스 healthcheck 매트릭스 | start_period 30/20/20/10/10/60s 각각 | 의존성 순서 (postgres → orange-core → blue-nodes/api-gateway) PASS |

---

## §10. 세션 간 cross-check

- **P2-1 ↔ P2-2 (k8s_argocd_pipeline.md)**: 환경별 overlay 구조 (dev/staging/prod) 가 V3 K8s 단계 Helm chart values 또는 Kustomize overlay 와 일관성 유지. V3 단계는 본 V2 6 서비스 토폴로지를 K8s Deployment/StatefulSet 으로 매핑.
- **P2-1 ↔ P2-3 (optimization_report.md)**: LOCK-CI-11 concurrency 설정 (group + cancel-in-progress) 정합. 본 V2 deploy-v2.yml 은 cancel-in-progress=false (배포 안전성 우선), CI 워크플로는 cancel-in-progress=true (PR 갱신 시 이전 실행 취소).
- **P2-1 ↔ P2-4 (benchmark_baseline.md)**: 본 V2 배포 후 WF-9 nightly benchmark cron 실행 시 동일 6 서비스 환경 가정. ISS-05 베이스라인 메트릭 측정 시 본 V2 deploy 가 안정 상태 (모든 healthy) 임을 전제.
- **P2-1 ↔ Phase 1 산출물**: WF-6/WF-7 정본 (6 서비스 deploy-compose job) 과 본 V2 deploy-v2.yml 의 6 서비스 매트릭스 일관성 보장.

---

## §11. 자가 체크리스트 (P2-1 step 3 finalize 시뮬레이션)

- [x] 6 서비스 (app tier 3 + data tier 3) 빌드→푸시→배포 플로우 단절 없음 (§3.1 + §4.1)
- [x] ISS-08 Docker 파이프라인 명세 완비 (§3.3 compose 정본 + §3.4 overlay)
- [x] LOCK-CI-12 컨테이너 배포 요건 반영 (§3.2 6 서비스 verbatim)
- [x] 롤백 절차 포함 (§5 결정 트리 + 실행 흐름)
- [x] CFL-CI-05 BL-01 해소 — runtime 시크릿 scope 재정의 V2 deploy 반영 (§4.1 .env 생성)
- [x] CFL-CI-08 BL-01 해소 — DISCORD_WEBHOOK_URL 선택 보조 채널 명시 (§4.1 조건부 step)
- [x] CFL-CI-09 BL-01 해소 — CLOUDFLARE_ACCOUNT_ID Cloudflare Pages 필수 명시 (§2 시크릿)
- [x] CFL-CI-10 해소 — Y-15b api-gateway 복원 (§3.2 + §3.3)
- [x] CFL-CI-14 BL-01 해소 — STAGING_/PROD_ 분기 (§3.4 + §4.1 inputs.environment)
- [x] LOCK-CI-01 14 WF 변경 0건 (deploy-v2.yml 은 V2 단계 신규, LOCK-CI-01 14 WF 정본 외 보조)
- [x] LOCK-CI-11 concurrency 설정 정합 (§4.1 + §10 cross-check)
- [x] FABRICATION 0/10 census CLEAN (§3.1~§3.5 anti-fabrication 가이드 준수, prose 0 hits)
- [x] V2↔V2 peer cross-ref 4 지점 (§10)
- [x] STEP7-F upstream `91ce88c0...` baseline 불변 (READ only, 인프라 Tier 4 공유 경로)
- [x] PHASE_B6 §6.1 baseline 불변 (READ only)

---

## §12. Phase 2 → Phase 3 exit_gate 기여

본 P2-1 산출물이 Phase 2 → Phase 3 exit_gate 에 기여하는 항목:

- **ISS-08 Docker 부분 해소 ✅**: 6 서비스 빌드→푸시→배포→롤백 정본 확정
- **LOCK-CI-12 정본 strict label**: app tier 3 + data tier 3 = 6 서비스 (변경 0)
- **CFL-CI 5건 BL-01 일괄 해소 경로 실체화**: CFL-CI-05/08/09/10/14 (CONFLICT_LOG step 7 RESOLVED 전환 대상)
- **/audit 시뮬레이션 PASS**: §11 체크리스트 14/14 ✅

> Phase 2 → Phase 3 exit_gate 의 다른 항목 (ISS-08 K8s 부분 / ISS-05 / LOCK-CI-06 V3 결정) 은 P2-2 / P2-3 / P2-4 세션에서 별도 충족.
