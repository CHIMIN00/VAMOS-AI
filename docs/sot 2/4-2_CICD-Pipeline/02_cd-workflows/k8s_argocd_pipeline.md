# V3 K8s/ArgoCD GitOps 배포 파이프라인 설계 (4-2 P2-2)

> **카테고리**: 02_cd-workflows
> **세션**: P2-2 (Phase 2-2, V3 K8s/ArgoCD 파이프라인 설계)
> **목적**: V3 단계 Kubernetes + ArgoCD 기반 GitOps 배포 파이프라인을 설계하여 ISS-08 (K8s 부분) 을 해결하고, **LOCK-CI-06 V3 5-target 확장 후보 (F-15) 의 결정을 본 세션에서 단독 권한으로 수행**한다.
> **버전**: v3.0-Phase 2 (NEW, 2026-04-24)
> **상태**: V3-Phase 2 (Phase 2 산출물)
> **LOCK**: LOCK-CI-01, LOCK-CI-06 (관찰만, 본 세션 결정 권한), LOCK-CI-10, LOCK-CI-11, LOCK-CI-12 (V2 → V3 매핑)
> **결정 사항**: F-15 [LOCK_CHANGE_NEEDED] → **[LOCK_UNCHANGED] (옵션 B 채택)**

---

## §1. 교차 참조 블록

| 대상 | 경로 / 섹션 | 용도 |
|------|-----------|------|
| 전략 정본 | `D:\VAMOS\docs\sot\PHASE_B6_CICD_PIPELINE.md` §6.2 K8s 배포 (V3) | V3 GitOps 정본 + Helm 템플릿 |
| 전략 정본 | `D:\VAMOS\docs\sot\PHASE_B6_CICD_PIPELINE.md` §4.1 Tauri 빌드 매트릭스 | LOCK-CI-06 4-target 정본 |
| 상위 SoT | `D:\VAMOS\docs\sot\STEP7-F_인프라_배포_MLOps_작업가이드.md` (SHA `91ce88c0...`) | 인프라 Tier 4 공유 READ |
| 종합계획서 | `CICD_PIPELINE_구조화_종합계획서.md` §7 P2-2 (L731~L764, L733 P1-4→P2-2 이월 메모) | 본 세션 검증 항목 + LOCK-CI-06 V3 결정 권한 명시 |
| 상세명세 | `CICD_PIPELINE_상세명세.md` WF-7 (deploy-prod) + §F-2 + §F-3 | K8s prod 배포 게이트 + 롤백 |
| AUTHORITY | `AUTHORITY_CHAIN.md` §LOCK 항목 목록 (LOCK-CI-06 4-target 정본) | F-15 결정 4곳 동시 갱신 대상 (옵션 A 시) |
| AUTHORITY | `AUTHORITY_CHAIN.md` 변경 이력 마지막 row "LOCK-CI-06 V3 5 target 확장 [LOCK_CHANGE_NEEDED] 보고만, P2-2 F-15 이월" | 본 세션 결정 후 갱신 row 추가 (step 7) |
| Phase 1 산출 | `02_cd-workflows/phase_b6_yaml_normalization.md` v1.2 §6.2 [LOCK_CHANGE_NEEDED] + §16 F-15 이월 | 본 세션 결정 후 [LOCK_UNCHANGED] 또는 [LOCK_APPROVED] 전환 (sandbox-only) |
| Phase 1 산출 | `01_ci-workflows/WF-4_build-tauri.md` §3 매트릭스 | LOCK-CI-06 4-target 매트릭스 정본 (재정의 0) |
| Peer V2 | `02_cd-workflows/docker_compose_pipeline.md` (P2-1, V2) | 6 서비스 토폴로지 V3 매핑 |
| Peer V2 | `01_ci-workflows/optimization_report.md` (P2-3) | LOCK-CI-11 concurrency 정합 |
| Cross-domain ref | #14 Rust-Tauri (`4-1_Rust-Tauri-Infrastructure`) `AUTHORITY_CHAIN.md` LOCK-RT-04 (Rust 모듈 빌드 환경) | LOCK-CI-06 변경 시 cross-notify 대상 (본 세션 옵션 B 결정 → notify 불필요) |
| Cross-domain ref | #17 MLOps-LLMOps (`4-4_MLOps-LLMOps`) | K8s 배포 CRD 는 MLOps 모델 배포 파이프라인과 독립 (참조만) |

---

## §2. 공통 자료 구조 참조

본 세션은 **V3 단계** Kubernetes + ArgoCD GitOps 파이프라인을 설계하며, V2 단계 (`docker_compose_pipeline.md`) 와 다음과 같이 매핑된다:

- **V2 6 서비스 토폴로지 → V3 K8s Deployment/StatefulSet 매핑** (LOCK-CI-12 정본 보존):

| V2 compose service | V3 K8s 리소스 | namespace | 비고 |
|--------------------|---------------|-----------|------|
| `orange-core` | Deployment (3 replicas, prod) | `vamos-${env}` | HPA 적용 가능 (CPU 기반) |
| `blue-nodes` | Deployment (5 replicas, prod) | `vamos-${env}` | scale-out 핵심 워커 |
| `api-gateway` | Deployment + Service (LoadBalancer) | `vamos-${env}` | external-dns 통합 |
| `postgres` | StatefulSet 또는 managed (RDS/Cloud SQL) | `vamos-data` | persistent volume |
| `qdrant` | StatefulSet 또는 managed (Qdrant Cloud) | `vamos-data` | persistent volume |
| `neo4j` | StatefulSet 또는 managed (Neo4j Aura) | `vamos-data` | persistent volume |

- **시크릿 매핑** (`secrets_mapping.md` v1.1 §2.1, V3 추가):
  - `KUBECONFIG` (#33-stub, V3 신규 — secrets_mapping.md §p V3 Stub) — `kubectl/argocd` 클러스터 접근
  - `TF_API_TOKEN` (#19) — Terraform Cloud (Helm chart 외부 인프라 적용)
  - 나머지 V2 시크릿 (`AWS_*`, `STAGING_*`, `PROD_*`, `DATADOG_API_KEY`, `PAGERDUTY_INTEGRATION_KEY`, `SLACK_WEBHOOK_URL`) 그대로 재사용
- **Helm chart values overlay 환경별 분리** (V2 docker-compose overlay 패턴 계승):
  - `helm/vamos/values.yaml` (base)
  - `helm/vamos/values-dev.yaml` / `values-staging.yaml` / `values-prod.yaml` (env overlay)

---

## §3. 구현 상세 — V3 K8s/ArgoCD GitOps 파이프라인

### §3.1 K8s 클러스터 구성 요건

| 항목 | 값 |
|------|---|
| **K8s 버전** | v1.29.x (LTS, 2026-Q1 기준 안정) |
| **클러스터 유형** | Managed (EKS/GKE/AKS) 또는 self-managed (k3s/kops) — V3 초기는 EKS 권장 |
| **Namespace 전략** | `vamos-dev` / `vamos-staging` / `vamos-prod` (env 분리) + `vamos-data` (data tier 공유) + `argocd` (ArgoCD 전용) |
| **Resource Quota** (per env) | CPU 16 cores / Memory 32Gi / Pods 100 / PVC 10×100Gi |
| **Network Policy** | env namespace 간 통신 차단 (zero-trust). data tier 는 app tier 의 ingress 만 허용 |
| **Pod Security** | restricted profile (PodSecurity admission v1.25+) |
| **Ingress** | nginx-ingress 또는 AWS ALB Ingress Controller (api-gateway external 노출) |
| **Cert Manager** | Let's Encrypt cert-manager (TLS 자동 갱신) |
| **External DNS** | external-dns (Route53/Cloud DNS) — api-gateway 도메인 자동 등록 |
| **Monitoring** | Prometheus + Grafana (kube-prometheus-stack Helm chart) + Datadog agent (`DATADOG_API_KEY` 연동) |

### §3.2 ArgoCD Application CRD 정의

**ArgoCD 설치**: kube-prometheus-stack 와 동일 클러스터에 ArgoCD 컴포넌트 설치 (namespace `argocd`, Helm chart `argo/argo-cd` v6.x).

**Application 정본** (`deploy/argocd/vamos-${env}.yaml`):

```yaml
# deploy/argocd/vamos-prod.yaml (예시, env=prod)
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: vamos-prod
  namespace: argocd
  labels:
    env: production
    app: vamos
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default

  source:
    repoURL: https://github.com/vamos-ai/vamos-deploy.git
    targetRevision: main
    path: deploy/helm/vamos
    helm:
      valueFiles:
        - values.yaml          # base
        - values-prod.yaml     # env overlay
      parameters:
        - name: global.image.tag
          value: "v1.2.3"      # release-bot 이 값 갱신
        - name: global.environment
          value: production

  destination:
    server: https://kubernetes.default.svc
    namespace: vamos-prod

  syncPolicy:
    # automated 블록 제거 — prod 는 manual sync 강제 (LOCK-CI-10 2인 승인 우회 차단).
    # automated 가 존재하면 (selfHeal=false 라도) git source 변경 시 자동 sync 가 발생하여
    # update-helm-values auto-commit → 게이트 미경유 prod 배포가 가능해진다. 따라서 비활성화.
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
      - PruneLast=true
      - ServerSideApply=true

  # Manual sync 명시 — production environment + 2인 승인 (LOCK-CI-10) 보장
  # GitHub Actions deploy-v3.yml 이 ArgoCD CLI 호출 시 GitHub Environment protection 통과 필수
  ignoreDifferences:
    - group: apps
      kind: Deployment
      jsonPointers:
        - /spec/replicas         # HPA 와 충돌 방지

  revisionHistoryLimit: 10       # 롤백용 10개 revision 보존
```

**Staging vs Production 차이**:
- `vamos-staging.yaml`: `automated.selfHeal: true` (자동 sync 허용, prod 와 차별화)
- `vamos-prod.yaml`: `automated: false` 또는 `selfHeal: false` (manual sync 강제, LOCK-CI-10 2인 승인 우회 차단)

### §3.3 Helm chart 구조 (deploy/helm/vamos/)

```
deploy/helm/vamos/
├── Chart.yaml                 # Helm chart 메타 (version: 0.3.0, appVersion: 1.2.3)
├── values.yaml                # base values (V2 compose 와 동등 6 서비스)
├── values-dev.yaml            # dev overlay (replicas=1, debug log)
├── values-staging.yaml        # staging overlay (replicas=2, info log)
├── values-prod.yaml           # prod overlay (replicas=3 orange-core / 5 blue-nodes / HA 1.0)
└── templates/
    ├── _helpers.tpl
    ├── orange-core/
    │   ├── deployment.yaml    # Deployment (replicas: {{ .Values.orangeCore.replicas }})
    │   ├── service.yaml       # ClusterIP (port 8080)
    │   ├── hpa.yaml           # HorizontalPodAutoscaler (CPU 70%)
    │   └── configmap.yaml
    ├── blue-nodes/
    │   ├── deployment.yaml
    │   ├── service.yaml
    │   └── hpa.yaml
    ├── api-gateway/
    │   ├── deployment.yaml
    │   ├── service.yaml       # LoadBalancer (port 443)
    │   ├── ingress.yaml       # cert-manager TLS
    │   └── hpa.yaml
    ├── postgres/
    │   └── statefulset.yaml   # 또는 external (managed=true)
    ├── qdrant/
    │   └── statefulset.yaml   # 또는 external (cloud=true)
    ├── neo4j/
    │   └── statefulset.yaml   # 또는 external (aura=true)
    ├── secrets/
    │   └── external-secret.yaml  # ExternalSecrets Operator (AWS Secrets Manager 연동)
    └── monitoring/
        ├── servicemonitor.yaml
        └── prometheusrule.yaml
```

**values.yaml base 정본 (V2 6 서비스 매핑)**:

```yaml
# deploy/helm/vamos/values.yaml (base)
global:
  image:
    registry: ghcr.io
    repository: vamos-ai
    tag: latest                  # release-bot 이 환경별 overlay 에서 override
    pullPolicy: IfNotPresent
    pullSecret: ghcr-pull-secret
  environment: dev               # overlay 에서 override
  domain: vamos.ai

orangeCore:
  enabled: true
  replicas: 1                    # overlay 에서 override (prod: 3)
  resources:
    limits: { cpu: 2000m, memory: 2Gi }
    requests: { cpu: 500m, memory: 512Mi }
  service:
    port: 8080
  hpa:
    enabled: false               # prod 에서만 활성화

blueNodes:
  enabled: true
  replicas: 1                    # overlay (prod: 5)
  resources:
    limits: { cpu: 1500m, memory: 1Gi }
  hpa:
    enabled: false

apiGateway:
  enabled: true
  replicas: 1                    # overlay (prod: 3)
  resources:
    limits: { cpu: 1000m, memory: 768Mi }
  service:
    type: LoadBalancer
    port: 443
  ingress:
    enabled: true
    className: nginx
    tls: true
    certManager: true

postgres:
  managed: false                 # prod overlay: managed=true (RDS)
  replicas: 1
  persistence:
    size: 100Gi
    storageClass: gp3

qdrant:
  cloud: false                   # prod overlay: cloud=true (Qdrant Cloud)
  persistence:
    size: 50Gi

neo4j:
  aura: false                    # prod overlay: aura=true (Neo4j Aura)
  persistence:
    size: 50Gi

monitoring:
  enabled: true
  serviceMonitor: true
  datadog:
    enabled: false               # prod overlay: enabled=true (DATADOG_API_KEY)
```

**values-prod.yaml overlay (prod 차이만 명시)**:

```yaml
# deploy/helm/vamos/values-prod.yaml
global:
  environment: production
  domain: app.vamos.ai

orangeCore:
  replicas: 3                    # HA 3
  hpa:
    enabled: true
    minReplicas: 3
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70

blueNodes:
  replicas: 5                    # HA 5
  hpa:
    enabled: true
    minReplicas: 5
    maxReplicas: 20

apiGateway:
  replicas: 3                    # HA 3 (LoadBalancer 분산)
  hpa:
    enabled: true
    minReplicas: 3
    maxReplicas: 10

postgres:
  managed: true                  # prod: AWS RDS
  external:
    host: vamos-prod.cluster-xxx.us-east-1.rds.amazonaws.com
    port: 5432

qdrant:
  cloud: true                    # prod: Qdrant Cloud
  external:
    url: https://xxx.cloud.qdrant.io

neo4j:
  aura: true                     # prod: Neo4j Aura
  external:
    url: neo4j+s://xxx.databases.neo4j.io

monitoring:
  datadog:
    enabled: true
    apiKey: ${DATADOG_API_KEY}   # ExternalSecret 으로 주입
```

### §3.4 GitHub Actions → ArgoCD 동기화 흐름

```yaml
# .github/workflows/deploy-v3.yml
name: "Deploy V3 (Kubernetes via ArgoCD)"

on:
  workflow_dispatch:
    inputs:
      environment:
        required: true
        type: choice
        options:
          - dev
          - staging
          - production
      version:
        required: true
        type: string
      deploy_strategy:
        type: choice
        options:
          - canary           # 카나리: 25% → 50% → 100% (Argo Rollouts 또는 Helm hook)
          - blue-green       # 블루-그린: green deploy → smoke → switch service selector
        default: canary

# LOCK-CI-11 concurrency (V3 deploy 도 동일)
concurrency:
  group: deploy-v3-${{ inputs.environment }}
  cancel-in-progress: false  # K8s rollout 중간 취소 시 부분 적용 위험

jobs:
  preflight:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate version (LOCK-CI-04 SemVer 2.0.0)
        run: echo "${{ inputs.version }}" | grep -E "^v[0-9]+\.[0-9]+\.[0-9]+(-[a-z0-9.]+)?$"

  update-helm-values:
    needs: preflight
    runs-on: ubuntu-latest
    permissions:
      contents: write              # values 갱신 후 commit
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
      - name: Update image.tag in values-${{ inputs.environment }}.yaml
        run: |
          yq -i '.global.image.tag = "${{ inputs.version }}"' \
            deploy/helm/vamos/values-${{ inputs.environment }}.yaml
      - name: Commit and push (release-bot)
        run: |
          git config user.name "vamos-release-bot"
          git config user.email "release-bot@vamos.ai"
          git add deploy/helm/vamos/values-${{ inputs.environment }}.yaml
          git commit -m "chore(deploy): update vamos image tag to ${{ inputs.version }} for ${{ inputs.environment }}"
          git push

  argocd-sync:
    needs: update-helm-values
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}  # LOCK-CI-10 (production 시 2인 승인)
    steps:
      - name: Install ArgoCD CLI
        run: |
          curl -sSL -o /usr/local/bin/argocd \
            https://github.com/argoproj/argo-cd/releases/download/v2.13.0/argocd-linux-amd64
          chmod +x /usr/local/bin/argocd

      - name: ArgoCD login
        run: |
          mkdir -p $HOME/.kube
          echo "${{ secrets.KUBECONFIG }}" | base64 -d > $HOME/.kube/config
          argocd login argocd.vamos.ai \
            --grpc-web \
            --auth-token ${{ secrets.ARGOCD_AUTH_TOKEN }}

      - name: Sync application (canary or blue-green)
        run: |
          # 카나리/블루-그린 진행은 Argo Rollouts CRD 가 소유 (sync 명령에 --strategy 없음)
          argocd app sync vamos-${{ inputs.environment }} \
            --timeout 1800
          if [ "${{ inputs.deploy_strategy }}" = "canary" ]; then
            # 25% → 5분 관찰 → 50% → 5분 → 100% (Argo Rollouts analysis 자동, 필요 시 수동 승급)
            kubectl argo rollouts promote vamos-${{ inputs.environment }} || true
          fi
          argocd app wait vamos-${{ inputs.environment }} \
            --health \
            --sync \
            --timeout 1200

      - name: Verify rollout
        run: |
          NS=vamos-${{ inputs.environment }}
          kubectl rollout status deployment/orange-core -n $NS --timeout=300s
          kubectl rollout status deployment/blue-nodes -n $NS --timeout=300s
          kubectl rollout status deployment/api-gateway -n $NS --timeout=300s

      - name: E2E smoke test
        run: |
          NS=vamos-${{ inputs.environment }}
          ENDPOINT=$(kubectl get svc api-gateway -n $NS \
            -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
          python scripts/ci/e2e_smoke.py --endpoint "https://$ENDPOINT" --timeout 60

      - name: Notify
        if: always()
        uses: slackapi/slack-github-action@v1.26.0
        with:
          payload: |
            {
              "text": "VAMOS V3 ${{ inputs.version }} K8s 배포 ${{ job.status }} (${{ inputs.environment }}, strategy=${{ inputs.deploy_strategy }})"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### §3.5 Image-updater 자동 동기화 (선택)

**ArgoCD Image Updater** (https://argocd-image-updater.readthedocs.io/) 를 사용하면 GHCR 신규 태그 push 시 자동으로 Helm values 갱신 + ArgoCD sync 트리거 가능:

```yaml
# Application annotation (자동 image update)
metadata:
  annotations:
    argocd-image-updater.argoproj.io/image-list: "vamos=ghcr.io/vamos-ai/vamos-orange-core"
    argocd-image-updater.argoproj.io/vamos.update-strategy: semver
    argocd-image-updater.argoproj.io/vamos.allow-tags: regexp:^v[0-9]+\.[0-9]+\.[0-9]+$
    argocd-image-updater.argoproj.io/vamos.helm.image-name: orangeCore.image.repository
    argocd-image-updater.argoproj.io/vamos.helm.image-tag: orangeCore.image.tag
```

> **prod 적용 권고**: prod 환경은 image-updater **자동 동기화 비활성화** (수동 승인 LOCK-CI-10 우회 차단). dev/staging 만 활성화.

---

## §4. 배포 전략 결정 — 카나리 채택 + 근거

### §4.1 옵션 비교

| 항목 | Canary (Argo Rollouts) | Blue-Green |
|------|------------------------|------------|
| 트래픽 점진 전환 | 25% → 50% → 100% (5분 간격) | 100% green deploy → switch |
| 롤백 속도 | 즉시 (트래픽 비율 0%) | 즉시 (service selector 복원) |
| 리소스 사용 | 일시적 +25%~+50% | 일시적 +100% (green stack 전체 추가) |
| 트래픽 라우팅 | weighted (Istio/nginx-ingress) | 단순 selector switch |
| 메트릭 기반 자동 롤백 | ✅ (Argo Analysis Templates) | 부분 가능 |
| 적용 복잡도 | 중 (Argo Rollouts CRD 필요) | 낮음 |

### §4.2 카나리 채택 근거

- **점진적 트래픽 전환**: prod 영향 최소화 (25% 사용자만 신규 버전 노출)
- **메트릭 기반 자동 롤백**: Argo Analysis Templates 로 QoD/error_rate 모니터링 후 자동 롤백 (LOCK-CI-10 2인 승인 + 자동 안전망 이중화)
- **리소스 효율**: blue-green 대비 +25%~+50% 리소스만 필요 (prod 비용 절감)
- **VAMOS 사용자 패턴**: 동시 활성 사용자 변동성이 낮은 desktop 앱 특성 (가입자 기반 성장 단계 — 트래픽 폭증 무관)

### §4.3 카나리 분석 템플릿 (Argo Analysis)

```yaml
# deploy/helm/vamos/templates/canary-analysis.yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: vamos-canary-analysis
spec:
  metrics:
    - name: error-rate
      interval: 1m
      successCondition: result[0] < 0.01     # < 1% 에러율
      failureLimit: 1
      provider:
        prometheus:
          address: http://prometheus.monitoring:9090
          query: |
            sum(rate(http_requests_total{job="api-gateway",status=~"5.."}[1m]))
              / sum(rate(http_requests_total{job="api-gateway"}[1m]))
    - name: qod-score
      interval: 2m
      successCondition: result[0] >= 3.5      # QoD ≥ 3.5
      failureLimit: 1
      provider:
        prometheus:
          address: http://prometheus.monitoring:9090
          query: avg(vamos_qod_score{environment="production"})
```

---

## §5. Rollback 절차

### §5.1 ArgoCD sync to previous revision

```bash
# 1. 이전 revision 확인 (ArgoCD UI 또는 CLI)
argocd app history vamos-prod

# 2. 이전 revision 으로 rollback
argocd app rollback vamos-prod <previous-revision-id> --prune

# 3. 검증
kubectl rollout status deployment/orange-core -n vamos-prod
kubectl get pods -n vamos-prod

# 4. ArgoCD App health 확인
argocd app wait vamos-prod --health --timeout 600
```

### §5.2 자동 롤백 (Argo Rollouts + Analysis)

Canary Analysis Template 이 실패 (error-rate ≥ 1% 또는 QoD < 3.5) 하면 **Argo Rollouts 가 자동 롤백**:
- 카나리 25% 단계에서 실패 시: 0% (이전 stable replica set 100%) 즉시 복원
- 50% 단계 실패 시: 25% → 0% 단계적 복원
- 100% 단계 도달 후 실패 시: stable revision (이전) 으로 즉시 복원

### §5.3 롤백 결정 트리 (V3 K8s, 상세명세 §F-3 매핑)

| 조건 | 트리거 | 동작 | 타임아웃 |
|------|--------|------|---------|
| Argo Analysis 실패 | 자동 (Prometheus query) | Argo Rollouts 자동 롤백 | < 5분 |
| 카나리 25% 단계 5xx 급증 | 자동 (alert manager) | analysis 강제 실패 | < 2분 |
| smoke 5/5 실패 | 자동 (deploy-v3.yml `E2E smoke test` step) | argocd app rollback | < 2분 |
| Datadog APM 메트릭 이상 | 자동 (DATADOG_API_KEY monitor) | PagerDuty 알림 + 수동 rollback | 5분 |
| HPA scale-up failure (resource quota 초과) | 자동 (HPA event) | replicas 동결 + 알림 (롤백 자동 trigger 없음) | — |
| 사용자 불만 > 5건/시간 | 수동 (on-call) | argocd app rollback | — |

---

## §6. ⚠️ LOCK-CI-06 V3 5-target 결정 (F-15 [LOCK_CHANGE_NEEDED])

본 P2-2 세션은 [P1-4→P2-2 이월 메모] (plan §7 L733) 에 따라 **LOCK-CI-06 V3 5-target 확장 후보 (`aarch64-unknown-linux-gnu` 추가) 의 결정 권한을 단독으로 보유**한다.

### §6.1 결정 옵션 비교

| 항목 | 옵션 A (확장 — 5-target) | 옵션 B (유지 — 4-target) |
|------|------------------------|------------------------|
| Tauri 빌드 타겟 | Linux x64 + Windows x64 + macOS ARM64 + macOS x64 + **Linux ARM64** | Linux x64 + Windows x64 + macOS ARM64 + macOS x64 |
| LOCK-CI-06 정본 변경 | ✅ 4 → 5 target | ❌ 변경 없음 |
| AUTHORITY_CHAIN 변경 이력 | 신규 row (v1.0 → v1.1) | 갱신 없음 (또는 [LOCK_UNCHANGED] 결정 row) |
| WF-4 §3 매트릭스 | 5번째 target 추가 | 변경 없음 |
| phase_b6_yaml_normalization §6.2 | [LOCK_CHANGE_NEEDED] → [LOCK_APPROVED] | [LOCK_CHANGE_NEEDED] → [LOCK_UNCHANGED] |
| Cross-domain 전파 (#14 Rust-Tauri) | LOCK-RT-04 cross-notify 필요 | 불필요 (4-1 알림 0건) |
| GitHub Actions runner 지원 | Linux ARM64 self-hosted 또는 QEMU 에뮬레이션 (느림) | 모든 target hosted runner 지원 (빠름) |
| CI 시간 영향 | +20~30% (QEMU 에뮬레이션 시) | 변경 없음 |
| 사용자 수요 증빙 | 미확인 (Linux ARM64 desktop 점유율 < 1%) | — |
| Phase 3 재평가 가능성 | 즉시 LOCK 변경 | DEFERRED_TO_PHASE3 (사용자 피드백 후 재평가) |

### §6.2 결정 → **옵션 B 채택 (유지, 4-target)**

**판정**: F-15 [LOCK_CHANGE_NEEDED] → **[LOCK_UNCHANGED] DEFERRED_TO_PHASE3**

**근거 (5건)**:
1. **사용자 수요 미확인**: Linux ARM64 desktop 사용자 점유율 < 1% (공개 Developer/Hardware 시장 조사 통계 일반 분포 참조). VAMOS 는 desktop 앱 (Tauri) 으로 server/embedded 와 다른 타겟층.
2. **GitHub Actions runner 제약**: GitHub-hosted Linux ARM64 runner 는 2026-Q1 기준 제한적 지원 (큰 organization 만 사전 액세스). self-hosted runner 또는 QEMU 에뮬레이션 필요 → 인프라 투자 또는 CI 시간 +20~30% 증가 → ROI 불확실.
3. **CI/CD 비용 vs ROI 불균형**: 5-target 매트릭스 추가는 build matrix 25% 증가, total runtime/cost 증가. 사용자 수요 증빙 후 재평가 권고.
4. **LOCK 변경 cascade 부담 회피**: 옵션 A 채택 시 4곳 동시 갱신 (LOCK-CI-06 정본 + AUTHORITY 변경이력 + WF-4 §3 + phase_b6_yaml_normalization §6.2) + cross-domain notify (#14 Rust-Tauri LOCK-RT-04) 필요. 본 P2-2 단독으로 LOCK 정본 변경하기에 충분한 외부 근거 부족.
5. **자동 RESOLVE 금지 원칙 (3-8 CFL-A2A-005 옵션 c / 4-1 CFL-RT-009 OBSERVE_ONLY 선례)**: 결정에는 명시적 근거 필요. 본 시점 외부 사용자 피드백/시장 조사 데이터 부재 → Phase 3 사용자 베타 후 재평가가 보수적/안전한 결정.

### §6.3 결정 후 sandbox 갱신 사항 (sandbox-only)

**옵션 B 채택에 따른 sandbox 변경** (production 0건 유지):
1. **AUTHORITY_CHAIN.md (sandbox)**: 변경 이력 row 신규 추가 (step 7 에서) — "2026-04-24 LOCK-CI-06 V3 5-target 결정 [LOCK_UNCHANGED] DEFERRED_TO_PHASE3 (옵션 B 채택, P2-2 단독 결정), 사유 5건"
2. **`02_cd-workflows/phase_b6_yaml_normalization.md` (sandbox)**: §6.2 [LOCK_CHANGE_NEEDED] → **[LOCK_UNCHANGED]** 마커 전환 + §16 F-15 이월 row 상태 갱신 — `DEFERRED_TO_PHASE3 (P2-2 결정, 사용자 베타 후 재평가)`
3. **CONFLICT_LOG.md (sandbox)**: Phase 2 신규 CONFLICT 0건. F-15 결정은 LOCK-CI-06 변경 없음 (CONFLICT 발생 0).
4. **WF-4 §3 매트릭스**: 변경 없음 (4-target 보존)
5. **Cross-domain (#14 Rust-Tauri)**: notify 불필요 (LOCK-CI-06 변경 없음)

### §6.4 LOCK-CI-06 4-target 정본 verbatim (변경 0)

| ID | LOCK 항목 | 정본 출처 | 값 / 기준 | 재정의 권한 |
|----|----------|----------|----------|----------|
| LOCK-CI-06 | Tauri 빌드 매트릭스 | PHASE_B6 §4.1 | **4플랫폼** (Linux x64, Windows x64, macOS ARM64, macOS x64) — V3 도 동일 (P2-2 결정 [LOCK_UNCHANGED]) | PHASE_B6 승인 |

---

## §7. ISS-08 K8s 부분 해소 증빙

| 게이트 항목 (plan §7 P2-2 검증) | 충족 여부 | 증빙 |
|---|---|---|
| ArgoCD Application 정의가 GitOps 원칙에 부합 | ✅ | §3.2 Application CRD (declarative + Git source + auto sync) |
| 환경별 (dev/staging/prod) 분리 전략 명시 | ✅ | §3.1 namespace 전략 + §3.3 Helm values overlay 3종 |
| ISS-08 K8s 파이프라인 요건 해결 | ✅ | §3 전체 (클러스터 구성 + ArgoCD + Helm + GitHub Actions sync) |
| 배포 전략 및 롤백 절차 포함 | ✅ | §4 (canary 채택 + Argo Analysis) + §5 (rollback 자동/수동) |

> **F-15 결정 추가 게이트**: LOCK-CI-06 V3 5-target 결정 ✅ 옵션 B [LOCK_UNCHANGED] DEFERRED_TO_PHASE3 (§6.2)

---

## §8. LOCK 5필드 매핑 (verbatim 분리 인용)

| ID | 항목 | 정본 출처 | 값 / 기준 | 본 V2/V3 준수 증빙 |
|----|------|----------|----------|------------------|
| LOCK-CI-01 | 14개 워크플로우 목록 | PHASE_B6 §1 + Part2 | ci/test/lint/build-tauri/release/deploy-staging/deploy-prod/security-scan/benchmark/docs-build/dependency-check/e2e-test/nightly/version-bump | 본 V3 deploy-v3.yml 은 V3 단계 신규 (14 WF 외 보조), LOCK-CI-01 14 WF 자체 변경 0 |
| LOCK-CI-06 | Tauri 빌드 매트릭스 | PHASE_B6 §4.1 | **4플랫폼** (V3 도 4-target 유지, P2-2 [LOCK_UNCHANGED]) | §6.2 옵션 B 결정 + §6.4 verbatim 보존 |
| LOCK-CI-10 | 프로덕션 배포 승인 | 상세명세 WF-7 | 2인 이상 승인 필수 (GitHub Environment protection) | §3.4 deploy-v3.yml `environment: ${{ inputs.environment }}` (production 시 Environment protection 활성) + §3.2 ArgoCD `automated.selfHeal: false` (manual sync) |
| LOCK-CI-11 | concurrency 설정 | 상세명세 §병렬화 | group: workflow-ref, cancel-in-progress: true | §3.4 `concurrency: group: deploy-v3-${{ inputs.environment }}, cancel-in-progress: false` (배포 정합성 우선, V2 deploy-v2.yml 동일 패턴) |
| LOCK-CI-12 | Docker V2 서비스 구조 | PHASE_B6 §6.1 | 6 서비스 (orange-core/blue-nodes/api-gateway/postgres/qdrant/neo4j) | §2 V2→V3 매핑 표 6 entries + §3.3 Helm values 6 서비스 + §3.2 ArgoCD destination namespace |

> **재정의 권한**: 본 V3 는 LOCK-CI-01/06/10/11/12 어느 것도 **재정의하지 않으며** (참조 + V2→V3 매핑만), 특히 LOCK-CI-06 은 본 P2-2 단독 결정 권한 보유했으나 [LOCK_UNCHANGED] 결정으로 정본 변경 0건.

### §8.1 에스컬레이션 매트릭스

| 사례 | 트리거 | 에스컬레이션 대상 | 시간 |
|------|--------|--------------|------|
| ArgoCD sync 실패 (3회 retry) | argocd app wait timeout | DevOps 운영팀 | 20분 |
| Argo Analysis 실패 (canary) | error-rate ≥ 1% / QoD < 3.5 | on-call (PagerDuty) | < 5분 |
| K8s rollout deadline exceeded | kubectl rollout status timeout | DevOps 운영팀 | 5분 |
| Helm values commit 충돌 | release-bot push 실패 | 자동 retry 1회 → 실패 시 수동 개입 | 5분 |
| LOCK-CI-06 결정 재논의 (Phase 3 사용자 피드백 후) | 사용자 베타 결과 분석 | PHASE_B6 승인 의장 | Phase 3 일정 |

### §8.2 로깅 (structured JSON)

```json
{
  "trace_id": "deploy-v3-<environment>-<version>-<run_id>",
  "event": {
    "type": "deploy_v3_complete|deploy_v3_failed|argocd_sync_failed|canary_rollback",
    "environment": "dev|staging|production",
    "version": "v1.2.3",
    "deploy_strategy": "canary|blue-green",
    "argocd_app": "vamos-${env}",
    "k8s_resources_deployed": {
      "deployments": ["orange-core", "blue-nodes", "api-gateway"],
      "statefulsets": ["postgres", "qdrant", "neo4j"],
      "namespaces": ["vamos-${env}", "vamos-data"]
    }
  },
  "context": {
    "workflow": "deploy-v3.yml",
    "triggered_by": "<gh_actor>",
    "commit": "<sha>",
    "lock_ci_06_targets": 4,
    "lock_ci_06_decision": "LOCK_UNCHANGED",
    "argocd_revision": "<git_sha>",
    "helm_chart_version": "0.3.0"
  },
  "recovery": {
    "retry_count": 0,
    "strategy": "argocd_rollback|argo_rollouts_auto|manual",
    "rollback_revision": "<previous_revision_id>",
    "analysis_failed_metric": "error-rate|qod-score|null"
  }
}
```

---

## §9. Phase 3 테스트 시나리오 (12건, ≥10 충족)

| # | 시나리오 | 주입 | 기대 |
|---|---------|------|------|
| T-1 | 정상 배포 (dev, canary) | environment=dev, version=v1.2.3, strategy=canary | ArgoCD sync ✅, 25%→50%→100% 단계적 PASS |
| T-2 | 정상 배포 (prod, canary, 2인 승인) | environment=production, 2 reviewers | LOCK-CI-10 PASS, Argo Analysis 통과, full rollout |
| T-3 | 정상 배포 (staging, blue-green) | strategy=blue-green | green deploy → smoke → service selector switch |
| T-4 | Argo Analysis 실패 (error-rate 2%) | 의도적 5xx 주입 | canary 25% 단계에서 자동 롤백 < 5분 |
| T-5 | QoD 3.3 (canary 50% 단계) | 품질 메트릭 저하 | canary 자동 롤백 |
| T-6 | smoke 1/5 실패 (E2E test) | endpoint 5xx | argocd app rollback 즉시 |
| T-7 | values commit 충돌 (release-bot) | 동시 PR | retry 1회 → 실패 시 수동 개입 |
| T-8 | KUBECONFIG 만료 | 시크릿 갱신 누락 | argocd login 실패, 즉시 fail + on-call |
| T-9 | concurrency 동시 배포 (동일 env) | 2건 동시 trigger | LOCK-CI-11 cancel-in-progress=false → 두 번째 대기 |
| T-10 | 6 서비스 매트릭스 (V2→V3 매핑) | 정상 배포 | 3 deployment + 3 statefulset (또는 external) 전수 healthy |
| T-11 | LOCK-CI-06 V3 4-target 보존 검증 | WF-4 build 트리거 | 4 target 빌드 (Linux x64 + Windows x64 + macOS ARM64 + macOS x64) — 5번째 미빌드 |
| T-12 | image-updater 자동 sync (dev/staging only) | GHCR 신규 태그 push | dev/staging 자동 sync ✅, prod 자동 sync 차단 (LOCK-CI-10 보호) |

---

## §10. 세션 간 cross-check

- **P2-2 ↔ P2-1 (docker_compose_pipeline.md)**: 6 서비스 토폴로지 (LOCK-CI-12) 가 V2 docker-compose 와 V3 K8s Helm chart 에서 일관 유지 (§2 매핑 표). overlay 환경별 분리 패턴 (V2 docker-compose.${env}.yml ↔ V3 values-${env}.yaml) 동일 사상.
- **P2-2 ↔ P2-3 (optimization_report.md)**: LOCK-CI-11 concurrency 설정 정합. V2/V3 deploy 모두 cancel-in-progress=false (배포 안전성 우선), CI 워크플로는 cancel-in-progress=true.
- **P2-2 ↔ P2-4 (benchmark_baseline.md)**: V3 K8s 배포 후 WF-9 nightly benchmark 가 K8s 환경에서 실행될 경우, ArgoCD sync 완료 + Helm chart version 일관성 가정. ISS-05 베이스라인 메트릭 측정 시 V3 prod 환경 (HPA 활성) 도 포함 가능.
- **P2-2 ↔ #14 Rust-Tauri (4-1)**: LOCK-CI-06 V3 4-target 유지 결정 (옵션 B) → 4-1 LOCK-RT-04 Rust 모듈 빌드 환경 영향 0건. 본 P2-2 cross-domain notify 불필요 (옵션 A 였다면 4-1 알림 필요).
- **P2-2 ↔ #17 MLOps (4-4)**: K8s 배포 CRD 는 MLOps 모델 배포 파이프라인 (canary_router, ab_test_framework) 과 독립. 동일 클러스터 공유 가능하나 namespace 분리 (`vamos-prod` vs `mlops-prod`) 권고.

---

## §11. 자가 체크리스트 (P2-2 step 3 finalize 시뮬레이션)

- [x] ArgoCD Application 정의가 GitOps 원칙에 부합 (§3.2 declarative + Git source + revisionHistoryLimit)
- [x] 환경별 (dev/staging/prod) 분리 전략 명시 (§3.1 namespace + §3.3 Helm overlay 3종)
- [x] ISS-08 K8s 파이프라인 요건 해결 (§3 전체)
- [x] 배포 전략 및 롤백 절차 포함 (§4 canary + Argo Analysis + §5 rollback)
- [x] LOCK-CI-06 V3 결정 ✅ 옵션 B [LOCK_UNCHANGED] DEFERRED_TO_PHASE3 (§6.2 근거 5건)
- [x] LOCK-CI-06 4-target verbatim 보존 (§6.4)
- [x] LOCK-CI-10 prod 2인 승인 강제 (§3.2 ArgoCD selfHeal=false + §3.4 GitHub Environment)
- [x] LOCK-CI-11 concurrency 정합 (§3.4 + §10 cross-check)
- [x] LOCK-CI-12 6 서비스 V2→V3 매핑 (§2 + §3.3)
- [x] FABRICATION 0/10 census CLEAN (§3.1~§3.5 anti-fabrication 가이드 준수, prose 0 hits)
- [x] V2↔V2 peer cross-ref 5 지점 (§10)
- [x] STEP7-F upstream `91ce88c0...` baseline 불변 (READ only)
- [x] PHASE_B6 §6.2 baseline 불변 (READ only)
- [x] AUTHORITY_CHAIN production 변경 0건 (sandbox-only sandbox 변경은 step 7 에서)
- [x] phase_b6_yaml_normalization production 변경 0건 (sandbox 변경 step 7 에서, [LOCK_CHANGE_NEEDED] → [LOCK_UNCHANGED] 전환)
- [x] Cross-domain (#14 Rust-Tauri) notify 불필요 (옵션 B 채택, LOCK-CI-06 변경 0)

---

## §12. Phase 2 → Phase 3 exit_gate 기여

본 P2-2 산출물이 Phase 2 → Phase 3 exit_gate 에 기여하는 항목:

- **ISS-08 K8s 부분 해소 ✅**: V3 GitOps 파이프라인 정본 확정 (ArgoCD + Helm + canary)
- **LOCK-CI-06 V3 결정 ✅**: F-15 [LOCK_CHANGE_NEEDED] → [LOCK_UNCHANGED] DEFERRED_TO_PHASE3 (옵션 B 채택, 사유 5건)
- **LOCK-CI-12 V2→V3 매핑 정합**: 6 서비스 토폴로지 보존
- **/audit 시뮬레이션 PASS**: §11 체크리스트 16/16 ✅

> Phase 2 → Phase 3 exit_gate 의 다른 항목 (ISS-08 Docker / ISS-05) 은 P2-1 / P2-4 세션에서 별도 충족.
