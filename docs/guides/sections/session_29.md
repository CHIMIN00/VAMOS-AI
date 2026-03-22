---
session: 29
sections: [39, 40]
status: complete
---

# §39. 배포 전략 (Deployment Strategy)

> **비유**: VAMOS를 배포하는 것은 새 가게를 여는 것과 같습니다. V1은 집에서 시작하는 홈 비즈니스, V2는 가게를 임대해서 오픈하는 것, V3는 프랜차이즈를 확장하는 것과 비슷합니다.

**배포 (Deployment)** 란 개발이 끝난 소프트웨어를 실제로 사용할 수 있는 환경에 설치하고 실행하는 과정입니다. VAMOS는 버전에 따라 배포 방식이 단계적으로 진화합니다.

[근거: PART2 §1 버전별 핵심 차이 비교표, PHASE_B7 §1.1]

### 버전별 배포 방식 비교

| 항목 | V0 | V1 | V2 | V3 |
|------|-----|-----|-----|-----|
| **인프라** | 로컬 (Tauri) | 로컬 (Tauri) | VPS + Docker Compose (Hetzner 권장) | Hetzner Lite(권장) / K8s(선택) |
| **배포 방식** | 수동 (로컬 설치) | 수동 (로컬 설치) | Docker Compose 자동 | K8s 자동 (Helm) |
| **비용 상한** | ₩0 (로컬) | ₩40,000/월 **LOCK 🔒 변경 불가** | ₩93,000/월 **LOCK 🔒 변경 불가** | ₩266,000/월 **ABSOLUTE LOCK 🔒 변경 불가** |
| **DB** | SQLite + Chroma | SQLite + Chroma | PostgreSQL + Qdrant + Neo4j | 관리형 DB + PVC |

---

## §39.1 V1: 로컬 배포 (Windows/WSL)

> **비유**: V1 로컬 배포는 자기 방에서 컴퓨터를 켜고 프로그램을 실행하는 것과 같습니다. 별도의 서버 없이, 내 컴퓨터에서 바로 돌립니다.

V1은 **로컬 MVP (Minimum Viable Product, 최소 기능 제품)** 단계로, Windows 또는 WSL (Windows Subsystem for Linux, 윈도우에서 리눅스를 사용할 수 있게 해주는 기능) 환경에서 직접 실행합니다.

[근거: PART2 §1 버전별 핵심 차이 비교표]

### 필요 사양

| 항목 | 최소 사양 |
|------|----------|
| **OS** | Windows 10/11 또는 WSL2 (Ubuntu 22.04+) |
| **Python** | 3.11+ |
| **Node.js** | 18+ (pnpm 패키지 매니저) |
| **Rust** | 최신 stable (Tauri 빌드용) |
| **메모리** | 8GB+ (Ollama 로컬 LLM 실행 시 16GB 권장) |
| **디스크** | 20GB+ (모델 + 데이터) |

### 설치 방법

```
1. 저장소 클론:     git clone <repository-url> && cd vamos
2. Python 의존성:   pip install poetry && poetry install
3. Node 의존성:     pnpm install
4. Rust 빌드:       cd src-tauri && cargo build
5. Ollama 설치:     ollama pull llama3.2:3b && ollama pull llama3.1:8b
6. SQLite + Chroma: 자동 초기화 (첫 실행 시)
```

[근거: PART2 V0 Stage Gate #3~#4, PHASE_B6 §1]

### 시작 명령어

```bash
# 개발 모드 (Tauri + React + Python)
pnpm tauri dev

# 또는 Python 백엔드만 실행
python -m vamos_core.main
```

### V1 스토리지 구성

| 구성 요소 | 기술 | 위치 |
|-----------|------|------|
| 메타/인덱스 | SQLite | `~/.vamos/vamos.db` |
| 로그/이벤트 | JSONL + SQLite | `~/.vamos/logs/*.jsonl` |
| 벡터 DB | Chroma (임베디드) | `~/.vamos/chroma/` |
| 그래프 DB | JSON 파일 | `~/.vamos/graph/*.json` |
| 임베딩 모델 | BGE-M3 (로컬) | Ollama 내장 |

[근거: PHASE_B7 §1.1 마이그레이션 범위 표]

### 핵심 요약 (3줄)
1. V1은 내 컴퓨터(Windows/WSL)에서 직접 실행하는 로컬 배포 방식입니다.
2. Python + Node.js + Rust + Ollama가 필요하며, `pnpm tauri dev`로 시작합니다.
3. 데이터는 SQLite + Chroma + JSONL로 로컬에 저장되며, 비용 상한은 ₩40,000/월 (LOCK 🔒)입니다.

---

## §39.2 V2: Docker Compose 배포

> **비유**: Docker Compose 배포는 이사짐을 컨테이너 박스에 넣어서 옮기는 것과 같습니다. 각 서비스(앱, DB, 벡터DB 등)를 별도의 컨테이너에 담아 한 번에 실행합니다.

**Docker** 는 소프트웨어를 격리된 환경(컨테이너)에서 실행하는 기술이고, **Docker Compose** 는 여러 컨테이너를 한꺼번에 관리하는 도구입니다.

[근거: PHASE_B6 §6.1, PART2 V2-Phase 1]

### VPS 선택 가이드 (V2→V3 확장 고려) <!-- v26 메이커에반 개선안 7 반영 -->

> V2부터 VPS 서버가 필요합니다. V3 확장을 고려하면 **Hetzner CX31을 1순위로 권장**합니다.

| VPS | 스펙 | 월 비용 | V3 확장성 | 비고 |
|-----|------|--------|----------|------|
| **Hetzner CX31 (권장)** | 2vCPU / 8GB / 80GB SSD (독일 Falkenstein) | ~$8 | V3 Hetzner Lite 직접 호환 | DDoS 20Tbps, VM 회수 리스크 0%, x86 100% |
| Oracle Cloud Free | 4vCPU / 24GB / 200GB (서울) | $0 | 낮음 (ARM, VM 회수 위험) | 무료이나 비활성화/회수 리스크 |
| Vultr | 4vCPU / 8GB / 100GB (서울) | ~$48 | 중간 | 한국 리전 가용 |
| DigitalOcean | 4vCPU / 8GB / 100GB (싱가포르) | ~$48 | 중간 | 표준 VPS |

> **권장 이유**: Hetzner CX31은 $8/월로 V2 Docker Compose 운영에 충분하며, V3 전환 시 동일 서버에서 RunPod Serverless GPU만 추가하면 $200 이내로 Enterprise 구성 가능 (§39.5 "V3 인프라 대안: Hetzner CX31 + RunPod Serverless" 참조).

[근거: PART2 V2-Phase 1 VPS 선택 가이드, v26 메이커에반 개선안 7]

### VPS 프로비저닝

1. **VPS 서버 프로비저닝**: Hetzner CX31 권장 (Ubuntu 22.04+), Docker Engine 24+ / Docker Compose v2 설치. Hetzner Console에서 CX31 생성 → SSH 키 설정 → 방화벽(3000/5432/6333/6379/7687 허용)

### docker-compose.yml 구성

```
┌─────────────────────────────────────────────────┐
│                Docker Compose                    │
│                                                  │
│  ┌─────────────┐  ┌─────────────┐               │
│  │ orange-core  │  │ blue-nodes  │  ← 앱 서비스  │
│  │  (포트 8080) │  │             │               │
│  └──────┬──────┘  └──────┬──────┘               │
│         │                │                       │
│  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────────┐ │
│  │  postgres   │  │   qdrant    │  │  neo4j   │ │
│  │ (포트 5432) │  │ (포트 6333) │  │(포트 7687)│ │
│  └─────────────┘  └─────────────┘  └──────────┘ │
│                                                  │
│  볼륨: postgres_data, qdrant_data, neo4j_data    │
└─────────────────────────────────────────────────┘
```

### 서비스 목록

| 서비스 | 이미지 | 포트 | 역할 |
|--------|--------|------|------|
| **orange-core** | `ghcr.io/vamos-ai/vamos-orange-core` | 8080 | 메인 AI 앱 (오렌지 코어) |
| **blue-nodes** | `ghcr.io/vamos-ai/vamos-blue-nodes` | - | 블루 노드 (도구 실행) |
| **postgres** | `postgres:16` | 5432 | 관계형 DB (데이터 저장) |
| **qdrant** | `qdrant/qdrant:v1.9.0` | 6333 | 벡터 DB (의미 검색) |
| **neo4j** | `neo4j:5-community` | 7474, 7687 | 그래프 DB (관계 저장) |
| **redis** | `redis:7+` | 6379 | 캐시 (빠른 임시 저장) |

[근거: PHASE_B6 §6.1 Docker Compose 파일, PART2 V2 §6]

### 각 서비스 헬스체크 (Healthcheck, 건강 확인)

모든 서비스는 자동 헬스체크가 설정됩니다 (interval: 30초, timeout: 10초, retries: 3).

| 서비스 | 헬스체크 방식 |
|--------|-------------|
| orange-core | `curl -f http://localhost:8080/health` |
| postgres | `pg_isready -U <user>` |
| qdrant | `curl -f http://localhost:6333/healthz` |

### 시작/중지 명령어

```bash
# 시작 (모든 서비스를 백그라운드에서 실행)
docker compose -f docker-compose.v2.yml up -d

# 상태 확인
docker compose ps

# 로그 확인
docker compose logs -f orange-core

# 중지 (모든 서비스 정지)
docker compose down

# 중지 + 데이터 삭제 (주의! 데이터가 모두 삭제됩니다)
docker compose down -v
```

### 환경변수 설정

환경변수는 `.env.v2` 파일에서 관리합니다. 시크릿(비밀번호 등)은 Docker Secrets를 권장합니다.

[근거: PART2 V2 §6, §7]

### 핵심 요약 (3줄)
1. V2는 Docker Compose로 6개 서비스(앱, PostgreSQL, Qdrant, Neo4j, Redis 등)를 컨테이너로 묶어 배포합니다.
2. `docker compose up -d`로 시작, `docker compose down`으로 중지하며, 각 서비스는 자동 헬스체크를 포함합니다.
3. VPS(가상 서버)에 SSH로 원격 배포하며, 비용 상한은 ₩93,000/월 (LOCK 🔒)입니다.

---

## §39.3 V3 배포 — 경로 A/B 이원화

> **배포 경로 선택**: V3는 두 가지 배포 경로 중 택 1합니다. 비용 $200/월 이내라면 **경로 B(Hetzner Lite) 권장**.

| 경로 | 방식 | 월 비용 | 적합 대상 |
|------|------|--------|----------|
| **경로 A** | AWS/GCP/Azure K8s (풀스펙) | ~$500+ | 팀/프로덕션, $500+ 예산 |
| **경로 B (권장)** | Hetzner CX31 + RunPod Serverless | ~$123-142 | 개인, $200 예산 이내 |

[근거: PART2 V3-Phase 1 사용자 직접 작업, v26 메이커에반 개선안 7]

### 경로 A: AWS/GCP/Azure K8s (풀스펙)

> **비유**: Kubernetes(줄여서 K8s)는 대형 물류센터의 자동 관리 시스템과 같습니다. 수십~수백 개의 컨테이너를 자동으로 배치하고, 고장 나면 자동으로 교체하며, 트래픽이 몰리면 자동으로 늘려줍니다.

**Kubernetes (K8s)** 는 컨테이너 오케스트레이션 (Container Orchestration, 컨테이너 자동 관리) 플랫폼이고, **Helm Chart** 는 K8s 애플리케이션을 패키지로 묶어 쉽게 배포하는 도구입니다.

[근거: PART2 V3-Phase 1, PHASE_B6 §6.2]

### Helm Chart 구성

```
deploy/k8s/helm/vamos/
├── Chart.yaml              ← 차트 메타 (name: vamos, version: 3.0.0)
├── values.yaml             ← 설정값 (환경별 오버라이드)
└── templates/
    ├── deployment.yaml     ← vamos-app (replicas: 2, rolling update)
    ├── deployment-gpu.yaml ← vamos-vllm (GPU 전용, NVIDIA GPU 1장)
    ├── service.yaml        ← ClusterIP + LoadBalancer
    ├── ingress.yaml        ← nginx-ingress + TLS (HTTPS)
    ├── configmap.yaml      ← config.v3.toml 마운트
    ├── secret.yaml         ← DB 비밀번호, API 키
    ├── pvc.yaml            ← 영속 볼륨 (모델 캐시, 로그)
    └── hpa.yaml            ← HPA (CPU 70% 초과 시 자동 확장, min 2 → max 10)
```

[근거: PART2 V3-Phase 1 §1]

### values.yaml 주요 설정

| 설정 카테고리 | 주요 키 | 값 / 설명 |
|-------------|---------|----------|
| **배포 모드** | `activeColor` | `blue` 또는 `green` (Blue-Green 배포) |
| **앱 리소스** | `app.resources` | CPU: 2, Memory: 4Gi |
| **GPU 리소스** | `vllm.resources` | CPU: 4, Memory: 16Gi, GPU: 1 |
| **스케일링** | `hpa.minReplicas` / `maxReplicas` | 2 / 10 |
| **환경 오버라이드** | `profiles` | dev / staging / prod |
| **인프라 티어** | `infra_tier` | `"hetzner-lite"` (경량 대안 경로) |
| **DB 연결** | `postgresql.host`, `qdrant.host` | 관리형 DB 엔드포인트 |

### 배포/롤백 명령어

```bash
# 배포 (Helm install)
helm upgrade --install vamos deploy/k8s/helm/vamos/ \
  --set activeColor=green \
  --namespace vamos-prod

# 상태 확인
kubectl rollout status deployment/vamos-orange-core -n vamos-prod

# 롤백 (이전 버전으로)
helm rollback vamos [REVISION]

# Canary 배포 (10% 트래픽만 새 버전으로)
helm upgrade vamos deploy/k8s/helm/vamos/ \
  --set canary.enabled=true --set canary.weight=10
```

[근거: PART2 V3 §6]

### 핵심 요약 (3줄)
1. V3는 Kubernetes + Helm Chart로 자동화된 컨테이너 오케스트레이션 배포를 수행합니다.
2. GPU 전용 노드(vLLM), 자동 스케일링(HPA), Blue-Green 배포를 지원합니다.
3. `helm upgrade --install`로 배포하고 `helm rollback`으로 즉시 롤백하며, 비용 상한은 ₩266,000/월 (ABSOLUTE LOCK 🔒)입니다.

---

## §39.4 Blue-Green 배포 (무중단 배포)

> **비유**: Blue-Green 배포는 **무대 교체**와 같습니다. 현재 공연 중인 무대(Blue)가 있고, 뒤편에서 새 무대(Green)를 준비합니다. 새 무대가 완벽히 준비되면 관객의 시선을 새 무대로 전환합니다. 만약 새 무대에 문제가 생기면 즉시 원래 무대로 돌아갑니다. 관객(사용자)은 전환 과정을 느끼지 못합니다.

**Blue-Green 배포** 는 두 개의 동일한 환경(Blue/Green)을 번갈아 사용하여 **다운타임 제로 (Downtime Zero, 서비스 중단 없는)** 배포를 달성하는 전략입니다.

[근거: PHASE_B7 §5.3, PART2 V3 §6]

### 다운타임 제로 배포 절차

```
[1단계] 현재 상태
   Blue (현재 버전) ←──── 트래픽 100%
   Green (비어 있음)

[2단계] 새 버전 배포
   Blue (현재 버전) ←──── 트래픽 100%
   Green (새 버전 배포 + 헬스체크)

[3단계-A] 헬스체크 통과 → 트래픽 전환
   Blue (이전 버전) ──── 대기 (최소 1시간 유지, 즉시 롤백 가능)
   Green (새 버전) ←──── 트래픽 100%

[3단계-B] 헬스체크 실패 → 배포 중단
   Blue (현재 버전) ←──── 트래픽 100% (그대로 유지)
   Green (실패) ──── 제거
```

### V2 (Docker Compose) Blue-Green

```yaml
# deploy/docker-compose.blue-green.yml
services:
  orange-core-blue:
    image: ghcr.io/vamos-ai/vamos-orange-core:${BLUE_VERSION}
    profiles: ["blue"]

  orange-core-green:
    image: ghcr.io/vamos-ai/vamos-orange-core:${GREEN_VERSION}
    profiles: ["green"]

  nginx:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./nginx/upstream.conf:/etc/nginx/conf.d/upstream.conf
```

Nginx (엔진엑스, 트래픽을 분배하는 웹 서버)가 Blue/Green 사이의 트래픽을 전환합니다.

[근거: PHASE_B7 §5.3]

### V3 (K8s) Blue-Green

```bash
# Green으로 전환
helm upgrade vamos deploy/k8s/helm/vamos/ --set activeColor=green

# 이상 발견 시 즉시 Blue로 복귀
helm upgrade vamos deploy/k8s/helm/vamos/ --set activeColor=blue
```

| 버전 | Blue-Green 방식 | 전환 시간 |
|------|----------------|----------|
| V2 | Docker Compose + Nginx upstream 전환 | 2-3분 |
| V3 | K8s Helm --set activeColor 변경 | **30초** |

**규칙**: Blue-Green 배포 시 이전 버전은 **최소 1시간** 유지하여 즉시 롤백이 가능하도록 합니다. [근거: PART2 V3 규칙]

### 핵심 요약 (3줄)
1. Blue-Green 배포는 두 환경을 번갈아 사용하여 서비스 중단 없이 새 버전을 배포하는 전략입니다.
2. V2는 Docker Compose + Nginx로 2-3분, V3는 K8s Helm으로 30초 만에 전환합니다.
3. 헬스체크 실패 시 자동으로 이전 버전을 유지하며, 이전 버전은 최소 1시간 대기합니다.

---

## §39.5 V3 인프라 대안: Hetzner + RunPod

> **비유**: AWS/GCP 같은 대형 클라우드가 백화점이라면, Hetzner + RunPod 조합은 **합리적인 가격의 동네 가게 + 필요할 때만 빌리는 전문 장비 대여점**입니다. 평소 작업은 저렴한 서버에서, GPU가 필요한 AI 추론만 필요할 때 빌려서 씁니다.

V3의 비용 상한은 ₩266,000/월 ≈ **$200 (ABSOLUTE LOCK 🔒 변경 불가)** 입니다. AWS/GCP의 본격 K8s 클러스터 대신, **Docker Compose + Serverless GPU** 조합으로 V3 기능을 비용 효율적으로 운영할 수 있습니다.

[근거: PART2 V3-Phase 1 "V3 인프라 대안: Hetzner CX31 + RunPod Serverless"]

### 비용 구성

| 항목 | 스펙 | 월 비용 |
|------|------|--------|
| **Hetzner CX31** (CPU/Storage) | 2vCPU / 8GB RAM / 80GB SSD (독일 Falkenstein) | ~$8 |
| **RunPod Serverless GPU** (GPU) | A4000/L4 on-demand (임베딩/추론 전용) | ~$6-15 |
| **Polygon Pro** (실시간 데이터) | 실시간 시세 데이터 | $79 |
| **LLM API** (Claude/GPT) | Mini 중심 + Main 간헐적 | ~$20-30 |
| **합계** | | **~$123-142/월** ($200 이내 ✅) |

### Hetzner (CPU/Storage 담당)

- **역할**: VAMOS 앱, PostgreSQL, Qdrant, Neo4j 등 상시 실행 서비스 호스팅
- **장점**: VM 회수 리스크 0% (Oracle Free Tier 대비), x86 호환성 100%, DDoS 방어 20Tbps, 투명한 과금
- **제약**: 8GB RAM (Swap 2GB 추가 권장)

### RunPod (GPU 담당)

- **역할**: AI 임베딩 생성, LLM 추론 등 GPU가 필요한 작업만 온디맨드 (on-demand, 필요할 때만) 실행
- **장점**: 사용한 만큼만 과금, Cold Start(콜드 스타트, 처음 시작 지연) ~2-5초
- **제약**: GPU Cold Start 지연 (Circuit Breaker 선작동으로 실질 영향 없음)

### 적용 방법

```yaml
# values.yaml에 인프라 티어 오버라이드 추가
infra_tier: "hetzner-lite"
# → Docker Compose 기반 배포 경로가 활성화됩니다
```

> **LOCK 위반 없음**: 인프라 선택은 LOCK 대상이 아닙니다. K8s LOCK은 배포 방식이며 특정 벤더에 종속되지 않습니다. 비용 상한 $200/월 ABSOLUTE LOCK을 준수합니다.

[근거: PART2 V3-Phase 1 인프라 대안]

### Oracle Cloud Free Tier 대비 Hetzner 장점

| 비교 항목 | Oracle Cloud Free | Hetzner CX31 |
|----------|-------------------|-------------|
| 비용 | $0 | ~$8/월 |
| VM 회수 리스크 | **높음** (비활성화/회수 사례 다수) | **0%** (유료 서비스, SLA 99.9%) |
| CPU 아키텍처 | ARM (호환성 이슈 빈번) | **x86** (100% 호환) |
| DDoS 방어 | 기본 | **20Tbps 포함** |
| 과금 투명성 | 숨겨진 비용 존재 가능 | **투명 과금** (월정액) |
| 서울 리전 | 가용 | 미가용 (독일 Falkenstein) |

### VAMOS AI + AI Investing 통합 아키텍처 (Hetzner CX31)

```
┌─────────── Hetzner CX31 (2vCPU/8GB/80GB) ───────────┐
│                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │
│  │ ORANGE CORE  │  │  BLUE NODE   │  │ AI Invest  │  │
│  │  (0.5 CPU)   │←→│  (0.3 CPU)   │←→│ (0.3 CPU)  │  │
│  │  (1.5Gi RAM) │  │  (1Gi RAM)   │  │ (1.5Gi RAM)│  │
│  └──────┬───────┘  └──────┬───────┘  └─────┬──────┘  │
│         │                 │                 │         │
│  ┌──────┴────────────────┴─────────────────┴──────┐  │
│  │  Docker Network: vamos-network (localhost ~0ms)  │  │
│  └──┬──────────┬──────────┬──────────┬────────────┘  │
│     │          │          │          │               │
│  ┌──┴───┐  ┌──┴───┐  ┌──┴───┐  ┌──┴───┐           │
│  │ PG   │  │Qdrant│  │Redis │  │Neo4j │           │
│  │(5432)│  │(6333)│  │(6379)│  │(7687)│           │
│  └──────┘  └──────┘  └──────┘  └──────┘           │
│                                                       │
│  공유: PG(스키마분리), Redis(DB번호분리), LLM API키   │
└───────────────────────────────────────────────────────┘
         ↕ RunPod Serverless GPU (A4000/L4, ~$6-15/월)
         ↕ Polygon Pro API ($79/월)
         ↕ LLM API: Claude/GPT (~$20-30/월)
```

### 로컬 PC 의존성 제거 비교

| 항목 | V0~V1 (로컬) | V2 (VPS 서버) | V3 Hetzner Lite (클라우드) |
|------|-------------|-------------|-------------------------|
| 실행 환경 | 로컬 PC Tauri 앱 | VPS Docker Compose | Hetzner 24/7 자동 운영 |
| PC 종료 시 | 서비스 중단 | 영향 없음 (서버 운영) | **영향 없음** (서버 독립 운영) |
| 접근 방식 | 로컬 앱 실행 필수 | SSH + 원격 접근 | 웹 브라우저/API 원격 접근 |
| 모니터링 | 로컬 React 대시보드 | Grafana (Docker) | Grafana 원격 대시보드 |
| 알림 | Tauri notification | Webhook (V2+) | Webhook → Telegram/Discord |
| AI Investing | PC 켜져 있어야 분석 | 서버에서 24/7 | 24/7 자동 분석 + 알림 |

### 성능 트레이드오프 (한국→독일 Hetzner)

| 항목 | 수치 | VAMOS 운영 영향 | 완화 방법 |
|------|------|---------------|---------|
| 네트워크 지연 | ~250ms | LLM 응답 시간 ±250ms 증가 | Circuit Breaker timeout 3초로 이미 보정 |
| GPU Cold Start (RunPod) | ~2-5초 | 첫 GPU 추론 요청 지연 | CPU Circuit Breaker 선작동 → 체감 영향 <1초 |
| 메모리 제약 | 8GB (실효 6GB + Swap 2GB) | BGE-M3 + 전략 엔진 동시 시 압박 | 배치 1000건 제한, 야간 스케줄링 |
| 스토리지 | 80GB SSD | 모델 캐시 + DB + 로그 | 로그 로테이션 30일, 캐시 정리 |

### 경로 B 사용자 직접 작업 (Hetzner CX31 + RunPod, ~$123-142/월)

1. **Hetzner CX31 프로비저닝**: Hetzner Console → CX31 생성 (Falkenstein, Ubuntu 22.04), SSH 키 설정, UFW 방화벽(3000/5432/6333/6379/7687 허용)
2. **Swap 설정**: `fallocate -l 2G /swapfile && mkswap /swapfile && swapon /swapfile` (8GB RAM 보강)
3. **Docker 환경**: Docker Engine 24+ / Docker Compose v2 설치, V2에서 사용하던 `docker-compose.v2.yml` 기반 확장
4. **RunPod Serverless 계정**: RunPod 가입 → Serverless Endpoint 생성 (A4000/L4 GPU) → API 키 발급 → `config.v3.toml [llm.inference]` 등록
5. **AI Investing 내부 통신 구성**: Docker 네트워크 `vamos-network`에서 ORANGE CORE + BLUE NODE + AI Investing 모듈 간 localhost 통신 설정
6. **Polygon Pro API 키**: Polygon.io Pro 가입 ($79/월) → `config.v3.toml [modules.ai_investing]` 등록
7. **비용 모니터링**: Grafana 대시보드에서 Hetzner($8 고정) + RunPod(종량) + Polygon($79 고정) + LLM API(종량) 통합 추적 → 합계 $160 경고 / $190 심각 알림 (예상 $123-142 대비 여유 확보, $200 ABSOLUTE LOCK 초과 방지)
8. **V2→V3 전환 조건 확인**: QoD ≥ 0.90, LLM 최적화, 테스트 통과, 승인

### deploy_mode 분기

```toml
# config.v3.toml
[deployment]
deploy_mode = "kubernetes"      # 경로 A (K8s 풀스펙)
# 또는
deploy_mode = "docker-compose"  # 경로 B (Hetzner Lite)
helm_release = "vamos"
namespace = "vamos-prod"
```

### Hetzner Lite 배포 4-STEP 체크리스트

> **STEP 1**: VPS 프로비저닝 (SSH, UFW, Docker, Swap 2GB)
> **STEP 2**: Docker Compose 프로필 (hetzner-lite, values.yaml 오버라이드)
> **STEP 3**: RunPod Serverless GPU 엔드포인트 등록 (config.v3.toml, I-10 Tool Router)
> **STEP 4**: AI Investing Stream Gateway 내부 통신 (vamos-network, Redis Pub/Sub)

### 경로 B 완료 검증

| # | 검증 항목 | 확인 방법 | 필수 |
|---|----------|----------|:---:|
| 1 | Hetzner CX31 서버 가동 | SSH 접속 + `docker compose ps` 전체 서비스 Running | ✅ |
| 2 | Swap 활성화 | `free -h`에서 Swap 2GB 확인 | ✅ |
| 3 | Docker Compose 전체 서비스 | PostgreSQL + Qdrant + Redis + VAMOS App 컨테이너 정상 가동 | ✅ |
| 4 | RunPod Serverless GPU 연결 | config.v3.toml RunPod 엔드포인트 → 추론 응답 확인 | ✅ |
| 5 | AI Investing 내부 통신 | ORANGE CORE ↔ AI Investing ↔ BLUE NODE 간 localhost 통신 정상 | ✅ |
| 6 | Polygon Pro 데이터 수신 | 실시간 시세 데이터 수신 + Redis 캐시 저장 확인 | ✅ |
| 7 | Grafana 모니터링 | 대시보드 접근 + Hetzner/RunPod/LLM API 비용 추적 동작 | ✅ |
| 8 | 비용 합계 검증 | 실제 운영 1주일 비용 ≤ $35 (월 $142 기준 주간 환산) | ✅ |
| 9 | 메모리 안정성 | 48시간 연속 운영 후 OOM 미발생 + 메모리 사용량 < 7GB | ✅ |
| 10 | 롤백 테스트 | `docker compose down && up -d` 정상 복구 (3분 이내) | ✅ |

> ⛔ 선택한 경로의 필수 항목 전체 통과 전 Phase 2 진입 금지

[근거: PART2 V3-Phase 1 완료 검증, v26 메이커에반 개선안 7]

### 핵심 요약 (3줄)
1. Hetzner(~$8/월)는 상시 서비스, RunPod(~$6-15/월)는 GPU 작업만 담당하는 비용 효율적 조합입니다.
2. 전체 인프라 비용 ~$123-142/월로 V3 비용 상한 $200/월 (ABSOLUTE LOCK 🔒) 이내입니다.
3. 경로 A(K8s 풀스펙)와 경로 B(Hetzner Lite) 중 예산에 맞는 경로를 선택하며, `deploy_mode` 설정으로 분기합니다.

---

---

# §40. 운영 가이드 (Operations Guide)

> **비유**: 배포가 '가게 오픈'이라면, 운영은 가게를 매일 관리하는 일입니다. CCTV(모니터링)로 매장을 감시하고, 금고에 정기 백업하고, 문제가 생기면 신속히 대응하는 모든 활동을 포함합니다.

**운영 (Operations)** 이란 배포된 시스템이 안정적으로 작동하도록 모니터링, 백업, 장애 대응 등을 수행하는 지속적인 활동입니다.

[근거: PART2 §6.12 운영 (버전별 전략)]

---

## §40.1 모니터링 전략 (V0/V1/V2/V3)

> **비유**: 모니터링은 환자의 생체 신호를 지켜보는 것과 같습니다. V0-V1은 체온계 하나로 확인하고, V2는 가정용 건강 모니터, V3는 병원의 종합 모니터링 장비와 같습니다.

**모니터링 (Monitoring)** 이란 시스템의 상태(CPU 사용률, 에러율, 응답 시간 등)를 실시간으로 관찰하고 이상을 감지하는 활동입니다.

[근거: PART2 §6.12.1]

### 버전별 모니터링 비교

| 버전 | 모니터링 방식 | 주요 메트릭 (측정 지표) | 도구 |
|------|------------|----------------------|------|
| **V0** | JSONL 로그 + 콘솔 출력 | 파이프라인 성공률, 응답 시간, 에러율 | 수동 tail/grep |
| **V1** | structlog JSON + SQLite 메트릭 테이블 | 32모듈 상태, Gate 통과율, 비용 추적, 메모리 사용량 | 로컬 대시보드 (React) |
| **V2** | Docker 로그 드라이버 + PostgreSQL 메트릭 | COND 모듈 활성화율, SDAR 해결율, API 레이턴시 P95/P99 | Grafana (Docker) |
| **V3** | Loki + Grafana + Prometheus | 전 모듈 분산 추적, K8s 리소스, GPU 활용률, Self-evo 성능 | Observability 스택 |

### V1: 로컬 로그 + JSONL

```
# V1 로그 구조
~/.vamos/logs/
├── 2026-03-15.jsonl    ← 당일 로그 (JSON Lines 형식)
├── 2026-03-14.jsonl    ← 전일 로그
└── ...

# 로그 확인 (수동)
tail -f ~/.vamos/logs/2026-03-15.jsonl | jq .
```

- 각 로그 라인은 JSON 형식 (시간, 모듈, 심각도, 메시지 포함)
- structlog 라이브러리로 구조화된 로깅

### V2: Docker 로그 + Grafana

- Docker 로그 드라이버 (json-file, max-size=50m, max-file=5)
- PostgreSQL에 메트릭 저장
- Grafana 대시보드로 시각화

### V3: Prometheus + Grafana + Loki + AlertManager

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Promtail │────▶│   Loki   │────▶│ Grafana  │
│(로그 수집)│     │(로그 저장)│     │(시각화)  │
└──────────┘     └──────────┘     └──────────┘

┌──────────────┐     ┌──────────────┐
│  Prometheus  │────▶│ AlertManager │
│(메트릭 수집) │     │(알림 발송)   │
└──────────────┘     └──────────────┘
```

V3 Grafana 대시보드 (5개):
1. **시스템 상태**: CPU/Memory/GPU 사용률, Pod 상태
2. **비용 모니터링**: ₩266,000/월 상한 추적
3. **LLM 추론 메트릭**: 토큰/초, 지연시간, 에러율
4. **5-Phase 파이프라인**: 각 Phase 처리 시간, 성공률
5. **Agent Teams**: 활성 에이전트 수, 메시지 처리량

[근거: PART2 V3-Phase 1 §4, §6.12.1]

### 핵심 요약 (3줄)
1. V0-V1은 로컬 JSONL 로그, V2는 Docker+Grafana, V3는 Prometheus+Grafana+Loki 풀 스택입니다.
2. 모니터링 대상은 버전이 올라갈수록 확장됩니다 (V1: 32모듈 → V3: 전 모듈 + GPU + K8s).
3. V3에서는 5개 대시보드로 시스템, 비용, LLM, 파이프라인, Agent를 종합 관찰합니다.

---

## §40.1.5 Hetzner Lite 리소스 관리 전략 (V3 경로 B)

> V3 경로 B(Hetzner CX31)를 선택한 경우의 리소스 분배 가이드라인입니다.

### 리소스 분배

| 리소스 | 총량 | ORANGE CORE | AI Investing | BLUE NODE (Trading) | 시스템/예비 |
|--------|------|-------------|-------------|-------------------|-----------|
| **CPU** | 2vCPU | 0.5 | 0.3 | 0.3 | 0.9 |
| **메모리** | 6Gi (8GB - Swap 2GB) | 1.5Gi | 1.5Gi | 1Gi | 2Gi (DB+Redis+OS) |
| **디스크 (80GB 총)** | 80GB | 10GB (core) | 10GB (investing) | 5GB (trading) | 55GB (로그/캐시/Swap/OS) |
| **Redis** | 512MB | DB0 (캐시 200MB) | DB2 (200MB) | DB1 (100MB) | DB3 (MessageBus) |

### 운영 원칙 (5건)

1. **메모리 부족 대응**: Swap 2GB 필수, OOM 시 BLUE NODE 우선 정지
2. **CPU 부하 분산**: 고부하 배치 야간 cron 예약
3. **디스크 관리**: 로그 30일 로테이션, `docker system prune` 주 1회
4. **월 1회 재시작**: Docker Compose 전체 재시작 (메모리 누수 방지)
5. **비용 알림**: $160 경고 / $190 심각

### Hetzner Lite vs K8s 풀스펙 운영 비교

| 항목 | Hetzner Lite (경로 B) | K8s 풀스펙 (경로 A) |
|------|----------------------|-------------------|
| 월 비용 | ~$123-142 | ~$500+ |
| 자동 스케일링 | 수동 | HPA 자동 |
| 롤백 | docker compose (2-3분) | Helm rollback (30초) |
| 가용성 | 단일 서버 (SLA 99.9%) | 멀티 노드 (SLA 99.95%+) |
| GPU | RunPod Serverless | 전용 GPU 24/7 |
| 적합 시나리오 | 개인, $200 예산 | 팀/프로덕션, $500+ |

[근거: PART2 §6.12.1.5 Hetzner Lite 리소스 관리 전략]

---

## §40.2 백업 & 복구 (RPO/RTO)

> **비유**: RPO는 "최대 몇 시간 전의 데이터까지 잃어도 괜찮은가?"이고, RTO는 "장애 발생 후 최대 몇 시간 안에 복구해야 하는가?"입니다. 은행은 RPO 0분/RTO 5분이지만, 개인 블로그는 RPO 1일/RTO 1일이어도 괜찮습니다.

- **RPO (Recovery Point Objective, 복구 시점 목표)**: 장애 발생 시 최대로 허용 가능한 데이터 손실 시간
- **RTO (Recovery Time Objective, 복구 시간 목표)**: 장애 발생부터 서비스가 복구되기까지의 최대 허용 시간

[근거: PART2 §6.12.2]

### 버전별 RPO/RTO

| 버전 | 데이터 | RPO | RTO | 백업 방식 |
|------|--------|-----|-----|----------|
| **V0-V1** | SQLite + Chroma + JSONL | 1일 (커밋 주기) | 30분 (git restore) | git 커밋 + SQLite `.backup` 명령 |
| **V2** | PostgreSQL + Qdrant + Neo4j | 1시간 | 2시간 | pg_dump cron(6h), Qdrant snapshot API, Neo4j backup |
| **V3** | 관리형 DB + PVC | **15분** | **30분** | RDS 자동 백업 + PVC 스냅샷 + Velero K8s 백업 |

### 백업 관련 LOCK 값

| 항목 | 값 | LOCK |
|------|-----|------|
| 마이그레이션 백업 보존 | 90일 | 마이그레이션 전 필수 **LOCK 🔒 변경 불가** |
| V2 백업 스케줄 | 매일 02:00 (cron) | 설정 기본값 |
| V2 백업 암호화 | AES-256-CBC | 필수 |

### BackupConfigSchema 연동

모든 마이그레이션과 정기 백업은 `BackupConfigSchema` (D2.1-D4)와 연동됩니다.

- **full**: 전체 백업 (Postgres pg_dump + Qdrant snapshot + Neo4j dump)
- **incremental**: 증분 백업 (WAL 기반)
- **snapshot**: 스냅샷 백업 (파일시스템 레벨)

[근거: PHASE_B7 §5.2, §6.2]

### 핵심 요약 (3줄)
1. RPO는 최대 데이터 손실 허용량, RTO는 최대 복구 시간으로, V3는 RPO 15분/RTO 30분입니다.
2. V0-V1은 git 커밋, V2는 pg_dump(6시간 주기), V3는 관리형 DB 자동 백업을 사용합니다.
3. 모든 백업은 BackupConfigSchema와 연동되며, 마이그레이션 전 반드시 전체 백업을 실행합니다 (LOCK 🔒).

---

## §40.3 인시던트 대응 프로세스

> **비유**: 인시던트 대응은 소방서 출동 체계와 같습니다. 화재(장애)가 감지되면 → 규모 파악(분류) → 출동/진화(대응) → 현장 복구 → 원인 조사(사후분석) 순서로 진행합니다.

**인시던트 (Incident)** 란 시스템의 정상적인 서비스를 방해하는 모든 사건을 말합니다.

[근거: PART2 §6.12.3]

### 5단계 대응 프로세스

```
[1] 탐지           [2] 분류           [3] 대응           [4] 복구           [5] 사후분석
모니터링 알림   →   심각도 분류   →   즉시 조치    →   서비스 복원   →   포스트모템
사용자 보고         P0/P1/P2/P3       롤백/폴백         정상 확인         재발 방지
```

### 심각도별 대응

| 심각도 | 의미 | 대응 | 목표 복구 시간 |
|--------|------|------|--------------|
| **P0** | 서비스 불가 (전체 장애) | 즉시 롤백 + 원인 분석 | **15분** |
| **P1** | 주요 기능 장애 | Fallback 활성화 + 원인 분석 | **1시간** |
| **P2** | 부분 장애 | 다음 배포에 수정 포함 | **24시간** |
| **P3** | 성능 저하 | 백로그 등록 | 다음 스프린트 |

### 사후분석 (포스트모템, Post-mortem)

P0/P1 인시던트는 **반드시** 포스트모템(사후 분석 보고서)을 작성해야 합니다. 포함 항목:
- 무엇이 발생했는가?
- 영향 범위는?
- 근본 원인은?
- 재발 방지 조치는?

[근거: PART2 §6.12.3]

### 핵심 요약 (3줄)
1. 인시던트 대응은 탐지 → 분류 → 대응 → 복구 → 사후분석의 5단계로 진행됩니다.
2. P0(전체 장애)은 15분 내 즉시 롤백, P1(주요 장애)은 1시간 내 복구가 목표입니다.
3. P0/P1 인시던트는 반드시 포스트모템(사후분석 보고서)을 작성하여 재발을 방지합니다.

---

## §40.4 알림 체계

> **비유**: 알림 체계는 건물의 화재 경보 시스템과 같습니다. 화재 심각도에 따라 자동으로 다른 알림이 울립니다 — 연기 감지기(Info) → 스프링클러(Warning) → 소방서 자동 신고(Critical).

[근거: PART2 §6.12.4]

### 심각도별 알림 채널

| 채널 | 대상 | 조건 | 시작 버전 |
|------|------|------|----------|
| **콘솔 로그** | 개발자 | 모든 에러 레벨 | V0+ |
| **로컬 알림** (Tauri notification) | 사용자 | 비용 70%/85%/95% 도달, P0/P1 에러 | V1+ |
| **Webhook** (Discord/Slack) | 운영팀 | P0/P1 인시던트, 배포 실패, 비용 초과 | V2+ |
| **PagerDuty/OpsGenie** | 온콜 (당직 담당자) | P0 서비스 불가 | V3+ |

### 알림 흐름도

```
[Info]     → 대시보드 표시만          (V0+)
[Warning]  → Slack/Discord 알림       (V2+)
[Critical] → SMS + PagerDuty 호출     (V3+)
```

### 핵심 요약 (3줄)
1. 알림은 심각도에 따라 콘솔(Info) → Slack(Warning) → SMS/PagerDuty(Critical)로 확대됩니다.
2. V1부터 비용 임계값(70%/85%/95%) 도달 시 사용자에게 로컬 알림을 보냅니다.
3. V3에서는 P0 장애 시 PagerDuty/OpsGenie로 온콜 담당자에게 즉시 연락합니다.

---

## §40.5 롤백 프로세스 (Rollback Process)

> **비유**: 롤백은 게임의 "이전 세이브 포인트로 돌아가기"와 같습니다. 새로 저장한 것에 문제가 있으면, 이전의 안전한 상태로 즉시 복귀합니다.

**롤백 (Rollback)** 이란 문제가 발생한 새 버전을 이전의 안정적인 버전으로 되돌리는 것입니다.

[근거: PART2 §6.12.5]

### 버전별 롤백 방식

| 버전 | 롤백 방식 | 소요 시간 | 자동화 수준 |
|------|----------|----------|-----------|
| **V0-V1** | `git revert` + 재빌드 | 5-10분 | 수동 |
| **V2** | Docker Compose 이전 이미지 태그로 재배포 | 2-3분 | CI/CD 트리거 |
| **V3** | K8s Blue-Green 스위치백 | **30초** | `helm rollback` 자동 |

### 즉시 롤백 vs 점진적 롤백

| 유형 | 설명 | 사용 시나리오 |
|------|------|-------------|
| **즉시 롤백** | 전체 트래픽을 이전 버전으로 한 번에 전환 | P0 장애, 데이터 손상 우려 |
| **점진적 롤백** | Canary 비율을 단계적으로 줄여 이전 버전으로 전환 | 부분 장애, 성능 저하 |

### V3 롤백 명령어

```bash
# 즉시 롤백 (이전 Helm 릴리스로)
helm rollback vamos [REVISION]

# Blue-Green 스위치백
helm upgrade vamos deploy/k8s/helm/vamos/ --set activeColor=blue
```

[근거: PHASE_B7 §5.1, §5.3]

### 핵심 요약 (3줄)
1. 롤백은 V0-V1(git revert, 5-10분), V2(Docker 재배포, 2-3분), V3(Helm rollback, 30초)로 점점 빨라집니다.
2. P0 장애 시 즉시 롤백, 부분 장애 시 Canary 비율 조정으로 점진적 롤백을 수행합니다.
3. V3에서는 `helm rollback` 한 줄로 30초 만에 이전 안정 버전으로 복귀할 수 있습니다.

---

## §40.6 헬스체크 (Health Check)

> **비유**: 헬스체크는 의사가 환자의 맥박을 주기적으로 확인하는 것과 같습니다. "아직 살아있나요? 정상인가요?"를 일정 간격으로 물어보고, 응답이 없으면 조치를 취합니다.

**헬스체크 (Health Check)** 란 서비스가 정상적으로 작동하는지 주기적으로 확인하는 메커니즘입니다. 보통 `/health` 엔드포인트 (URL 경로)에 HTTP 요청을 보내 `200 OK` 응답을 확인합니다.

[근거: PART2 §6.12.6]

### 버전별 헬스체크

| 버전 | 대상 | 방식 | 주기 | 실패 시 조치 |
|------|------|------|------|-------------|
| **V0-V1** | Python 프로세스 | `/health` HTTP 엔드포인트 (200 OK) | 30초 | 프로세스 재시작 |
| **V2** | Docker 컨테이너 | `HEALTHCHECK CMD curl -f http://localhost:8000/health` | 15초 | Docker restart policy |
| **V3** | K8s Pod | `livenessProbe` + `readinessProbe` (HTTP/TCP) | 10초 | Pod 재시작 + 자동 재스케줄링 |

### K8s Probe 유형 (V3)

| Probe | 목적 | 실패 시 |
|-------|------|--------|
| **livenessProbe** (생존 확인) | "프로세스가 살아있는가?" | Pod 재시작 |
| **readinessProbe** (준비 확인) | "트래픽을 받을 준비가 되었는가?" | 서비스에서 제외 (트래픽 차단) |

### 핵심 요약 (3줄)
1. 모든 버전에서 `/health` 엔드포인트로 서비스 상태를 주기적으로 확인합니다.
2. 주기는 V0-V1(30초) → V2(15초) → V3(10초)로 점점 빨라져 장애를 더 빠르게 감지합니다.
3. V3에서는 livenessProbe(생존 확인)와 readinessProbe(준비 확인) 두 가지로 세밀하게 관리합니다.

---

## §40.7 로그 보존 정책

> **비유**: 로그 보존은 CCTV 녹화 보관과 같습니다. 법적 기준에 따라 일정 기간 보관하고, 오래된 것은 삭제합니다.

[근거: PART2 §6.12.7, §6.12.12]

### 버전별 로그 보존 기간

| 버전 | 로그 유형 | 보존 기간 | 저장소 |
|------|----------|----------|--------|
| **V0-V1** | JSONL 파일 | 90일 (로컬) | `data/logs/` 디렉토리, logrotate |
| **V2** | Docker 로그 + PostgreSQL audit | 180일 | Docker log driver (json-file, max-size=50m, max-file=5) |
| **V3** | Loki 인덱스 | 365일 | Loki retention policy, S3/MinIO cold storage |

### 구현 시 결정 항목 (§6.12.12)

| 항목 | V0-V1 | V2 | V3 |
|------|-------|-----|-----|
| **로그 보관 기간** | 30일 | 90일 | 1년 |
| **백업 주기** | git 커밋 | 6시간 | 자동 |
| **헬스체크 주기** | 60초 | 30초 | 15초 |

[근거: PART2 §6.12.12 구현 중 결정 항목]

### 핵심 요약 (3줄)
1. 로그 보존 기간은 V0-V1(90일) → V2(180일) → V3(365일)으로 확장됩니다.
2. V2는 Docker 로그 드라이버(max-size=50m), V3는 Loki + S3 cold storage로 장기 보관합니다.
3. 구현 시 결정 항목으로 정확한 보관 기간은 실측 후 확정합니다 (V0-V1: 30일, V2: 90일, V3: 1년).

---

## §40.8 비용 초과 대응

> **비유**: 비용 초과 대응은 가계부의 예산 관리와 같습니다. 예산의 70%를 쓰면 노란불, 85%면 주의보, 95%면 경고, 100%를 넘으면 지출을 막습니다.

VAMOS는 각 버전의 **비용 상한 (LOCK 🔒)** 을 초과하지 않도록 단계적 대응 시스템을 갖추고 있습니다.

[근거: PART2 §6.12.8]

### 5단계 비용 대응

| 단계 | 임계값 | 대응 | 알림 |
|------|--------|------|------|
| **1. 경고** | 70% | 대시보드 노란색 표시, 로그 경고 | 대시보드 |
| **2. 주의** | 85% | Webhook 알림 발송, 비용 높은 모듈 자동 throttle (속도 제한) | Slack/Discord |
| **3. 위험** | 95% | 사용자 알림 + P2 이상 요청 일시 정지 대기 | 사용자 알림 |
| **4. 초과** | 100% | 모든 유료 API 호출 차단, P0/P1만 Ollama 로컬로 전환 | 긴급 알림 |
| **5. 월 초** | 리셋 | daily_limit 기준 일일 배분 자동 리셋 | - |

### 비용 상한 (LOCK 값)

| 버전 | 비용 상한 | LOCK 상태 |
|------|----------|----------|
| V1 | ₩40,000/월 | **LOCK 🔒 변경 불가** |
| V2 | ₩93,000/월 | **LOCK 🔒 변경 불가** |
| V3 | ₩266,000/월 ≈ $200 | **ABSOLUTE LOCK 🔒 변경 불가** |

- 월 초 자동 리셋: daily_limit 기준 일일 배분 **(LOCK 🔒)**

[근거: PART2 §6.12.8, §1 버전별 핵심 차이]

### 핵심 요약 (3줄)
1. 비용이 70% → 85% → 95% → 100%에 도달할 때마다 점점 강력한 조치가 자동 발동됩니다.
2. 100% 초과 시 유료 API가 전면 차단되고, P0/P1 요청만 Ollama 로컬 모델로 전환됩니다.
3. 각 버전의 비용 상한 (V1: ₩40K, V2: ₩93K, V3: ₩266K)은 LOCK 🔒으로 변경이 불가합니다.

---

## §40.9 SDAR 수동 폴백

> **비유**: SDAR (Self-Diagnosis and Auto-Repair, 자가진단/자동수리)는 차량의 자가진단 시스템과 같습니다. 보통은 자동으로 수리(Auto-Repair)하지만, 자동 수리가 실패하면 정비사(운영자)가 직접 수리해야 합니다. 이것이 **수동 폴백 (Manual Fallback)** 입니다.

[근거: PART2 §6.12.9]

### AR 레벨별 수동 폴백 절차

| AR 레벨 | 심각도 | 수동 폴백 방법 | 절차 |
|---------|--------|--------------|------|
| **AR-L1** (LOW) | 낮음 | 수동 재시작 | `systemctl restart vamos` 또는 Docker restart |
| **AR-L2** (MEDIUM) | 중간 | 수동 config 수정 | 문제 config 키 확인 → TOML 수정 → 재시작 |
| **AR-L3** (MEDIUM+) | 중상 | 수동 롤백 | `git revert` 또는 Docker 이전 이미지로 전환 |
| **AR-L4** (HIGH) | 높음 | DBA/DevOps 개입 | 스키마 수동 마이그레이션 + 데이터 무결성 검증 |

### 버전별 SDAR 활성 상태

| 버전 | SDAR 상태 |
|------|----------|
| V0 | **OFF** (비활성) |
| V1 | **OFF** (비활성) |
| V2 | AR-L2 ~ AR-L3 |
| V3 | AR-L4 + Self-evo (자가진화) |

- V0-V1에서는 SDAR가 비활성이므로 **모든 장애를 수동으로 대응**해야 합니다.
- V2에서 AR-L2~L3 자동 수리가 시작되고, 실패 시 수동 폴백을 적용합니다.
- V3에서는 AR-L4까지 자동 수리 + Self-evo로 시스템이 스스로 진화합니다.

[근거: PART2 §1 버전별 핵심 차이, §6.12.9]

### 수동 폴백 흐름

```
SDAR 자동 수리 시도
        │
        ├── 성공 → 정상 운영 계속
        │
        └── 실패 → AR 레벨에 따른 수동 폴백 실행
                │
                ├── AR-L1: 재시작
                ├── AR-L2: config 수정 + 재시작
                ├── AR-L3: 롤백 (git revert / Docker)
                └── AR-L4: DBA/DevOps 전문가 개입
```

### 핵심 요약 (3줄)
1. SDAR 자동 수리가 실패하면 AR 레벨에 따라 수동 폴백(재시작/config 수정/롤백/전문가 개입)을 실행합니다.
2. V0-V1은 SDAR OFF이므로 모든 장애를 수동 대응, V2부터 AR-L2~L3 자동 수리가 활성화됩니다.
3. AR-L4(HIGH) 수준의 장애는 DBA/DevOps 전문가가 스키마 마이그레이션 + 데이터 무결성 검증을 직접 수행합니다.

---

## 검증 체크리스트

- [x] V1/V2/V3 배포 모두 포함
- [x] Blue-Green 배포 (무대 교체 비유)
- [x] Hetzner + RunPod (비용 효율적 대안)
- [x] 모니터링 V0/V1/V2/V3 (단계별 비교)
- [x] RPO/RTO (백업/복구 목표)
- [x] 인시던트 5단계 (탐지→분류→대응→복구→사후분석)
- [x] 알림 체계 (심각도별 채널)
- [x] 롤백 프로세스 (즉시/점진적)
- [x] 헬스체크 (/health, livenessProbe/readinessProbe)
- [x] 로그 보존 (V0-V1: 90일, V2: 180일, V3: 365일)
- [x] 비유 설명 포함 (모든 섹션)
- [x] 근거 SOT 참조 표기 (PART2, PHASE_B7, PHASE_B6)
