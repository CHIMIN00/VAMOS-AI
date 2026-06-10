# scaling_policy.md — V1 수직 / V2 Docker Swarm / V3 K8s HPA + 비용 관리

> **도메인**: 6-8_Cloud-Library / 03_cdn-scaling
> **역할**: 스케일링 임계값 + 비용 관리 + LOCK 운영 제약 매핑 + DH-CL-D1 verbatim 인용
> **수정 정책**: 정본 — Phase 변경 시 갱신
> **생성일**: 2026-04-28 (P2-3, STAGE 7 STEP_B)
> **변경 이력 태그**: V2-Phase 2
> **정본 참조**: AUTHORITY_CHAIN.md §3 LOCK (L9/L14/L15/L17/L21) + §4 DH-CL-D1 + 종합계획서 §6.2 ISS-2 + §6.1 P5 + §7.3 V1~V3 버전별 구현 의존성
> **ISS-2 + P5 (Phase 2 part) 해결**: 스케일링 임계값 전수 명세 + 배포/스케일링 전략 명세

---

## §0. Purpose / Scope

### §0.1 본 문서 목적

V1 수직 스케일링부터 V3 K8s HPA까지 단계별 스케일링 임계값·트리거 조건·비용 관리 전략을 정본화한다. LOCK L9 (동시 크롤러 = 5) / L14 (최대 저장 = 10,000) / L15 (임베딩 batch = 32) / L17 (동시 임베딩 워커 = 2) / L21 (일일 크롤링 쿼터 = 1,000) 운영 제약 내에서의 스케일링 한계를 명시한다.

### §0.2 Phase 3 제외 항목

- I-21 Source Evolution 자율 확장 (V3 자율 진화) — 본 문서 V3 K8s HPA까지 명세, 자기 진화 스케일링은 Phase 3 baseline
- 멀티 리전 분산 스케일링 (V3 globally distributed) — 본 문서 단일 리전 K8s 클러스터까지
- DR (Disaster Recovery) 자동 페일오버 — 6-13 Operations 정본 (cross-handoff)

---

## §1. 교차 참조 블록

| 정본 문서 | 섹션 | 참조 항목 |
|----------|------|----------|
| `../AUTHORITY_CHAIN.md` | §3 LOCK + §4 DH | L9 / L14 / L15 / L17 / L21 운영 제약 + DH-CL-D1 배포 전략 verbatim |
| `../CLOUD_LIBRARY_구조화_종합계획서.md` | §6.1 P5 + §6.2 ISS-2 + §7.3 | 배포/스케일링 전략 미정의 (P5) + 스케일링 정책 미상세 (ISS-2) + V1~V3 의존성 |
| `./_index.md` | §2 + §4.2 | 스케일링 전략 총괄 + 스케일링 관련 LOCK 5건 |
| `../01_cloud-deploy/deployment_strategy.md` | §4 + §5 + §7 | V2 Docker Swarm + V3 K8s HPA + LOCK 운영 제약 매핑 (정합 보존) |
| `../01_cloud-deploy/layer_pipeline.md` | §4 L6 EMBEDDING | 임베딩 워커 수평 스케일링 한계 (L15 batch = 32, L17 워커 = 2) |
| `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` | §6.10 | V2 (Docker Swarm 수평) + V3 (K8s HPA) 스케일링 가이드 |

---

## §2. LOCK 운영 제약 — DH-CL-D1 verbatim 인용 (5-field)

### §2.1 LOCK L9/L14/L15/L17/L21 (AUTHORITY §3 verbatim)

| LOCK ID | 명칭 | 정본 출처 | 값/규칙 (verbatim) | 본 문서 인용 결과 |
|---------|------|----------|------------------|-----------------|
| **L9** | 최대 동시 크롤러 | SPEC §16.1 | 5 | §3.2 V1 / §4.2 V2 / §5.2 V3 노드당 5 적용 일치 |
| **L14** | 최대 저장 소스 수 | SPEC §16.6 | 10,000 | §3.2 / §4.2 / §5.2 저장 상한 일치 (V2+ 수평 확장 시에도 보존) |
| **L15** | 임베딩 배치 크기 | SPEC §16.7 | 32 | §3.4 / §4.4 / §5.4 batch 일치 |
| **L17** | 동시 임베딩 워커 | SPEC §16.9 | 2 | §3.2 V1 단일 노드 / §4.2 V2 노드당 2 / §5.2 V3 pod당 2 적용 일치 |
| **L21** | 일일 크롤링 쿼터 | SPEC §16.13 | 1,000 페이지 | §3.6 / §4.6 / §5.6 token bucket 적용 일치 (스케일 무관) |

### §2.2 DH-CL-D1 verbatim 5-field 인용 (AUTHORITY §4)

| DH-ID | 항목 | 값 (verbatim) | 근거 (verbatim) | 변경 조건 (verbatim) |
|-------|------|---------------|----------------|--------------------|
| **DH-CL-D1** | 배포 전략 | V1: Docker Compose (단일 서버, Hetzner CX31), V2: Docker Swarm (2-3 노드), V3: K8s (HPA auto-scaling, min=2, max=10, CPU>70% 트리거) | CLOUD_LIBRARY_SPEC·Part2에 배포 전략 미명시. 4-1 Rust-Tauri 인프라 참조 + LOCK L9(동시 크롤러=5), L17(동시 임베딩 워커=2) 리소스 요구 기반 도출 | 상위 정본(SPEC 또는 Part2)에서 배포 전략 명시 시 상위 정본 우선 적용 |

> **R-68-1 준수**: 본 문서는 L9/L14/L15/L17/L21 정본 출처 (SPEC §16) 가 유일 권한이며, 값 변경 0건. 정본 갱신 후에만 반영한다.
> **DH 보존**: DH-CL-D1 1 unique 보존. 신규 DH 추가 ❌ (V3 범위 이월).

---

## §3. V1 — 수직 스케일링 (Hetzner CX31 단일 서버, DH-CL-D1 V1)

### §3.1 인프라

- **서버**: Hetzner CX31 (4 vCPU, 8 GB RAM, 160 GB SSD) — DH-CL-D1 V1 (deployment_strategy.md §3.1 정합, Hetzner CX31 실사양 8 GB)
- **컨테이너 런타임**: Docker Compose v2.21+
- **서비스 구성** (단일 노드):
  - `cl-collector` (E-15 Cloud Collector, L1~L4) — 1 instance
  - `cl-extractor` (L6 EXTRACTION) — 1 instance
  - `cl-analyzer` (L7 ANALYSIS) — 1 instance
  - `cl-validator` (L8 VALIDATION CL-G0~G4) — 1 instance
  - `cl-embedder` (L10 OUTPUT, BGE-M3) — 1 instance, 동시 워커 = L17 = 2
  - `cl-vectorstore` (Chroma local) — 1 instance
  - `cl-postgres` (메타데이터, L18=10KB/소스) — 1 instance

### §3.2 LOCK 운영 제약 적용 (V1)

| LOCK | V1 적용 방식 |
|------|------------|
| **L9** 동시 크롤러 = 5 | `cl-collector` 단일 인스턴스 내 asyncio 5-concurrent semaphore |
| **L14** 최대 저장 소스 = 10,000 | `cl-postgres` 단일 DB capacity planning + cron archive policy |
| **L15** 임베딩 batch = 32 | `cl-embedder` BGE-M3 inference batch 32 고정 |
| **L17** 동시 임베딩 워커 = 2 | `cl-embedder` thread pool 2 고정 (단일 컨테이너) |
| **L21** 일일 쿼터 = 1,000 | `cl-collector` token bucket 1,000/day per source |

### §3.3 스케일 업 트리거 임계값

| 메트릭 | 임계값 | 트리거 액션 |
|--------|--------|-----------|
| CPU 사용률 (5분 평균) | > 70% | 스펙 단계 상향 권장 (CX31 → CX41) |
| RAM 사용률 (5분 평균) | > 80% | 스펙 단계 상향 권장 |
| 처리 큐 적체 | > 1,000 items 30분 이상 | V2 Docker Swarm 전환 권장 |
| 저장 소스 수 | > 8,000 (L14 80%) | V2 전환 권장 (DB 분산) |

### §3.4 권장 스펙 단계

| 단계 | 스펙 | 비용 (월) | 권장 시점 |
|------|------|----------|----------|
| Hetzner CX31 | 4 vCPU / 16 GB / 160 GB | ~₩20,000 | 초기 (V1 MVP, source ≤ 5,000) |
| Hetzner CX41 | 8 vCPU / 32 GB / 240 GB | ~₩40,000 | source 5,000~8,000 |
| Hetzner CX51 | 16 vCPU / 64 GB / 360 GB | ~₩80,000 | source 8,000~10,000 (V1 한계) |

### §3.5 단일 노드 운영 한계

- **L14 최대 저장 = 10,000** 도달 시 V1 → V2 전환 의무 (수직 스케일 한계)
- **L9 동시 크롤러 = 5 / L17 임베딩 워커 = 2** 단일 노드 충분, 노드 추가 불요
- **CDN ❌**: V1 은 로컬 캐시만 (TTL = L13 = 24h)

### §3.6 비용 관리 (V1)

- **월 비용 cap**: ~₩80,000 (CX51 기준)
- **알람 임계**: 80% 비용 cap 도달 시 운영자 통지
- **초과 시 액션**: V2 전환 또는 source archive 적극 적용

---

## §4. V2 — Docker Swarm 수평 스케일링 (DH-CL-D1 V2)

### §4.1 인프라

- **클러스터**: Docker Swarm 2-3 노드 — DH-CL-D1 V2 verbatim
- **노드 구성**:
  - Manager 1 (Hetzner CCX23: 4 vCPU / 16 GB)
  - Worker 2~3 (Hetzner CCX23 each)
- **서비스 replica 전략**:
  - `cl-collector` replicas = 2 (HA) — L9 적용 노드당 (총 노드 × 5 max)
  - `cl-extractor` replicas = 2
  - `cl-analyzer` replicas = 2
  - `cl-validator` replicas = 2
  - `cl-embedder` replicas = 2 — L17 적용 노드당 (총 노드 × 2 max)
  - `cl-vectorstore` (Qdrant 분산 모드) replicas = 3 (HA + 분산 인덱싱)
  - `cl-postgres` (Patroni HA) replicas = 3

### §4.2 LOCK 운영 제약 적용 (V2)

| LOCK | V2 적용 방식 |
|------|------------|
| **L9** 동시 크롤러 = 5 | **전역 합 = 5** (클러스터 전체 동시 크롤러 ≤ 5, Redis 분산 세마포어로 강제 — deployment_strategy.md §4.4 정합, 노드 수 무관) |
| **L14** 최대 저장 = 10,000 | **클러스터 전체 합계 10,000** (Postgres Patroni shard 분산, 노드별 ~3,333 = 10,000 ÷ 3, 3노드 합계 ≤ 10,000 보장) |
| **L15** 임베딩 batch = 32 | 각 `cl-embedder` replica 동일 batch 32 |
| **L17** 동시 임베딩 워커 = 2 | **노드당 2 워커** (총 = replica 수 × 2 = 4~6 max) |
| **L21** 일일 쿼터 = 1,000 | **클러스터 전체 합계 1,000/day** (Redis 분산 token bucket) |

### §4.3 스케일 아웃 트리거 임계값

| 메트릭 | 임계값 | 트리거 액션 |
|--------|--------|-----------|
| 클러스터 평균 CPU (5분) | > 80% | 노드 추가 (2 → 3) |
| 크롤링 큐 적체 | > 5,000 items 30분 이상 | replica 증설 (`cl-collector` 2 → 3) |
| 처리량 (sources/hour) | < 800 (peak load 1,000 의 80%) | 노드 추가 |
| 메모리 압박 노드 ≥ 1 | RAM > 85% | 해당 서비스 replica 다른 노드로 재분배 |

### §4.4 V2 → V3 전환 임계값

- **클러스터 부하 지속**: 3 노드 + replicas 최대 + CPU > 80% 1주 지속 시 V3 K8s 전환 권장
- **저장 소스 수**: > 9,000 (L14 90%) 도달 시 V3 전환 권장 (분산 DB sharding 한계)
- **처리량 peak**: 일일 1,000 페이지 (L21) 처리 시간 > 8h 시 V3 전환

### §4.5 부하 시나리오 (V2)

| 시나리오 | peak load | V2 처리 시간 | scale-out 횟수 |
|---------|-----------|------------|--------------|
| 일반 운영 | 500 sources/h | 30분 | 0 (2 노드) |
| 피크 시간 | 1,000 sources/h | 60분 | 1 (3 노드) |
| 긴급 수집 | 2,000 sources/h | 90분 | 1 + replica 증설 |

### §4.6 비용 관리 (V2)

- **월 비용 cap**: ~₩200,000~₩300,000 (3 노드 + 로드밸런서 + 모니터링)
- **알람 임계**: 80% 도달 시 운영자 통지
- **초과 시 액션**:
  - **자동 scale-in**: peak 통과 후 30분 idle 시 노드 자동 축소 (3 → 2)
  - **야간 배치 집중**: 처리량 비-피크 시간대 (00:00~06:00 KST) 집중

### §4.7 scale-in 안전 조건

- 진행 중 작업 graceful drain (max 30s)
- 큐 잔여 < 10 확인 후 노드 종료
- VectorStore 데이터 안전성 보장 (Qdrant replication factor 2 유지)

---

## §5. V3 — Kubernetes HPA auto-scaling (DH-CL-D1 V3)

### §5.1 인프라

- **클러스터**: Kubernetes (managed K8s, 예: Hetzner / GKE / EKS)
- **HPA 설정** (DH-CL-D1 V3 verbatim):
  - `minReplicas: 2` (고가용성 보장)
  - `maxReplicas: 10` (L21 일일 쿼터 1,000 처리량 상한 정합)
  - `targetCPUUtilizationPercentage: 70` (CPU > 70% 트리거)
  - `behavior.scaleDown.stabilizationWindowSeconds: 300` (5분 cooldown)
  - `behavior.scaleUp.policies: [{type: Pods, value: 2, periodSeconds: 60}]` (1분당 max +2 pod)

### §5.2 LOCK 운영 제약 적용 (V3)

| LOCK | V3 적용 방식 |
|------|------------|
| **L9** 동시 크롤러 = 5 | **pod당 5** (HPA min=2 → 10 → max 동시 50 크롤러, 단 L21 1,000/day rate limiter 우선) |
| **L14** 최대 저장 = 10,000 | **클러스터 전체** (Qdrant shard 분산 + Postgres Citus sharding) |
| **L15** 임베딩 batch = 32 | 각 `cl-embedder` pod 동일 batch 32 |
| **L17** 동시 임베딩 워커 = 2 | **pod당 2 워커** (HPA = 2~10 pod = 총 4~20 워커) |
| **L21** 일일 쿼터 = 1,000 | **클러스터 전체** (Redis Cluster 분산 token bucket, atomic decrement) |

### §5.3 HPA 트리거 정책 상세

| Metric | targetValue | 적용 서비스 |
|--------|-------------|-----------|
| CPU utilization | 70% (DH-CL-D1 V3 verbatim) | 모든 deployment |
| Memory utilization | 75% | `cl-embedder` (BGE-M3 1024dim) |
| Custom metric `crawl_queue_depth` | > 500 items | `cl-collector` |
| Custom metric `embed_batch_pending` | > 100 items | `cl-embedder` |

### §5.4 minReplicas=2 / maxReplicas=10 설정 근거

- **min=2**:
  - 단일 pod 장애 시 가용성 보장 (Pod Disruption Budget = 1)
  - 무중단 배포 (rolling update with `maxUnavailable: 1`)
- **max=10**:
  - L21 일일 쿼터 1,000 처리량 상한 — pod 10 × L9 5 = 50 동시 크롤러 충분 (2~3시간 내 1,000 처리)
  - 비용 cap ~₩500,000 (10 pod × 평균 비용)
  - L14 저장 소스 10,000 분산 처리 가능

### §5.5 파드별 리소스 요청·제한

```yaml
resources:
  requests:
    cpu: "500m"      # 0.5 vCPU
    memory: "1Gi"
  limits:
    cpu: "2000m"     # 2 vCPU
    memory: "4Gi"    # BGE-M3 모델 로드 충분
```

### §5.6 CDN 연동 스케일링

> 정합: `./_index.md` §1.4 V3 멀티 CDN (Cloudflare + Fastly 이중화)

| 컴포넌트 | V3 설정 |
|---------|--------|
| **Cloudflare CDN** | 엣지 캐시 TTL = L13 = 24h, 캐시 키 `{source_url_hash}:{content_hash}` |
| **Fastly 이중화** | 지역별 라우팅 (KR/US/EU), failover automatic |
| **L16 재크롤링 7일** | CDN 무효화 webhook (Cloudflare Workers) |
| **K8s HPA + CDN** | CDN cache miss 비율 > 30% 시 `cl-collector` 우선 scale-up |

### §5.7 부하 시나리오 (V3)

| 시나리오 | peak load | HPA 동작 | 처리 시간 |
|---------|-----------|---------|---------|
| 일반 | 500 sources/h | 2 pod 유지 (CPU 30%) | 30분 |
| 피크 | 1,000 sources/h | 2 → 4 pod (CPU 70%+ 5분) | 45분 |
| 긴급 | 5,000 sources/h | 2 → 10 pod (1분당 +2) | 2시간 |
| 폭주 | > L21 한계 | rate limiter 차단 + scale-out | 24h 분할 |

### §5.8 scale-in 안전 조건 (V3)

- pod 종료 전 graceful shutdown (max 60s, `terminationGracePeriodSeconds: 60` — drain 윈도우 ≤ grace period 정합)
- 진행 중 임베딩 작업 완료 대기 (PreStop hook)
- Qdrant replica drain 후 종료
- 큐 적체 확인 (Redis Cluster zero items)

### §5.9 비용 관리 (V3)

- **월 비용 cap**: ~₩500,000~₩1,000,000 (10 pod max + 멀티 CDN + Qdrant 클러스터)
- **알람 임계**: 80% 도달 시 운영자 통지 + DPO 통지 (예산 초과 GDPR 영향 검토)
- **초과 시 액션**:
  - **자동 scale-in fallback**: peak 통과 후 5분 cooldown 후 자동 축소
  - **dry-run scale-up**: 비용 시뮬레이션 후 운영자 승인 시에만 maxReplicas 일시 상향 가능

---

## §6. V1 → V2 → V3 전환 게이트

| 전환 | 트리거 조건 | 의사 결정자 | 소요 시간 |
|------|-----------|-----------|----------|
| V1 → V2 | source > 8,000 (L14 80%) OR CPU > 80% 1주 지속 | 운영자 + DPO 승인 | 1~2일 (Swarm 클러스터 구축) |
| V2 → V3 | source > 9,000 (L14 90%) OR 처리 시간 > 8h/day | 운영자 + 운영팀 검토 | 3~5일 (K8s 클러스터 구축 + 데이터 마이그레이션) |

---

## §7. 4-1 Rust-Tauri 인프라 참조 (cross-handoff, LOCK 재정의 ❌)

> 본 §7 은 4-1 Rust-Tauri 인프라를 *참조* 하며, 4-1 도메인 LOCK / 인프라 본문은 본 문서에서 변경 ❌.

| 컴포넌트 | 4-1 정본 | 본 V3 적용 |
|---------|---------|-----------|
| **데스크톱 앱 컨테이너** | Tauri (단일 클라이언트) | 백엔드 K8s 클러스터와 분리 운영 |
| **IPC 커맨드** | `vamos:cloud:*` | 6-8 → 4-1 IPC, K8s ingress 경유 |
| **로컬 캐시** | Tauri SQLite | V1 로컬 모드와 동등 (V2/V3은 백엔드 분리) |

---

## §8. 모듈 카탈로그 (산출물 품질 §11.a)

| 모듈 | 역할 | 정본 파일 | V1 / V2 / V3 |
|------|------|----------|-------------|
| `cl-collector` | E-15 Cloud Collector (L1~L4) | layer_pipeline.md §L1~§L4 | V1: 1 inst / V2: replicas=2~3 / V3: HPA min=2 max=10 |
| `cl-extractor` | L6 EXTRACTION | layer_pipeline.md §L6 | V1: 1 / V2: 2 / V3: HPA |
| `cl-analyzer` | L7 ANALYSIS | layer_pipeline.md §L7 | V1: 1 / V2: 2 / V3: HPA |
| `cl-validator` | L8 VALIDATION CL-G0~G4 | gate_details.md §3 | V1: 1 / V2: 2 / V3: HPA |
| `cl-embedder` | L10 OUTPUT (BGE-M3, L15 batch=32) | layer_pipeline.md §L10 | V1: 1 / V2: 2 / V3: HPA (pod당 L17=2 워커) |
| `cl-vectorstore` | Chroma (V1) / Qdrant (V2/V3) | layer_pipeline.md §L10 | V1: local / V2: 분산 3 / V3: cluster |
| `cl-postgres` | 메타데이터 + L18 10KB/소스 | deployment_strategy.md §6 | V1: 1 / V2: Patroni 3 / V3: Citus shard |

---

## §9. 의존성 매트릭스 (산출물 품질 §11.c, NxN)

| → | collector | extractor | analyzer | validator | embedder | vectorstore | postgres |
|---|----------|-----------|---------|-----------|---------|-------------|---------|
| **collector** | — | ▲ produces | — | — | — | — | ▲ writes |
| **extractor** | ▼ consumes | — | ▲ produces | — | — | — | ▼ reads |
| **analyzer** | — | ▼ consumes | — | ▲ produces | — | — | ▼ reads |
| **validator** | — | — | ▼ consumes | — | ▲ triggers | — | ▼ reads |
| **embedder** | — | — | — | ▼ triggered | — | ▲ writes | ▼ reads |
| **vectorstore** | — | — | — | — | ▼ writes | — | — |
| **postgres** | ▼ reads | ▲ produces | ▲ produces | ▲ produces | ▲ produces | — | — |

> ▲ = produce / write / trigger to target. ▼ = consume / read / receive from source.

---

## §10. 비용 매트릭스 종합 (V1 / V2 / V3 비교)

| Phase | 인프라 | 월 비용 cap | source 처리량/일 | 한계 source 수 | 권장 적용 시점 |
|-------|-------|------------|----------------|--------------|--------------|
| **V1** | Hetzner CX31~CX51 단일 | ~₩20,000~₩80,000 | < 1,000 (L21 한계) | < 10,000 (L14) | source 수 < 5,000, MVP |
| **V2** | Docker Swarm 2~3노드 | ~₩200,000~₩300,000 | 1,000 (L21, 2~3 노드 분산) | 9,000~10,000 | source 5,000~8,000, V1 한계 도달 |
| **V3** | K8s HPA 2~10 pod | ~₩500,000~₩1,000,000 | 1,000+ (L21 분산 token bucket) | 10,000 (L14, 분산 sharding) | source 9,000~10,000, V2 한계 도달 |

---

## §11. SoT 검증 섹션 (산출물 품질 §11.d)

| 항목 | 정본 출처 | 본 §X 인용 결과 |
|------|----------|----------------|
| L9 동시 크롤러 = 5 | SPEC §16.1 | §2 / §3.2 / §4.2 / §5.2 정합 ✅ |
| L14 최대 저장 = 10,000 | SPEC §16.6 | §2 / §3.2 / §4.2 / §5.2 / §10 정합 ✅ |
| L15 임베딩 batch = 32 | SPEC §16.7 | §2 / §3.4 / §4.4 / §5.5 정합 ✅ |
| L17 동시 임베딩 워커 = 2 | SPEC §16.9 | §2 / §3.2 / §4.2 / §5.2 / §5.5 정합 ✅ |
| L21 일일 쿼터 = 1,000 | SPEC §16.13 | §2 / §3.6 / §4.6 / §5.7 정합 ✅ |
| DH-CL-D1 V1 Docker Compose Hetzner CX31 | AUTHORITY §4 verbatim | §3 정합 ✅ |
| DH-CL-D1 V2 Docker Swarm 2-3 노드 | AUTHORITY §4 verbatim | §4 정합 ✅ |
| DH-CL-D1 V3 K8s HPA min=2 max=10 CPU>70% | AUTHORITY §4 verbatim | §5 정합 ✅ |
| 4-1 Rust-Tauri 인프라 | 4-1 정본 (read-only) | §7 read-only 인용 ✅ |

---

## §12. Phase 3 테스트 시나리오 (≥ 10건)

| # | 시나리오 | 주입 | 기대 결과 |
|---|---------|------|----------|
| 1 | V1 CPU > 70% 5분 | stress-ng load | 운영자 통지 + CX31 → CX41 권장 |
| 2 | V1 source > 8,000 | DB seed 8,001 entries | V2 전환 권장 알람 |
| 3 | V1 → V2 마이그레이션 | manual ops | Postgres dump → Patroni 복원 + Swarm deploy |
| 4 | V2 클러스터 CPU > 80% 5분 | stress-ng 3 노드 | scale-out 트리거, Manager 노드 추가 |
| 5 | V2 → V3 마이그레이션 | manual ops | K8s 클러스터 구축 + 데이터 마이그레이션 |
| 6 | V3 HPA scale-up (peak load 1,000) | load test 1k sources/h | pod 2 → 4 (CPU 70%+ 5분) |
| 7 | V3 HPA scale-up max | load test 5k sources/h | pod 2 → 10 (max), L21 rate limiter 작동 |
| 8 | V3 HPA scale-down idle | idle 30min | pod 4 → 2 (cooldown 5분) |
| 9 | V3 graceful shutdown | rolling update | 진행 중 작업 완료 대기 (terminationGrace 60s) |
| 10 | V3 비용 cap 80% 도달 | mock cost increase | DPO 알림 + scale-in fallback |
| 11 | L17 임베딩 워커 OOM | batch=64 강제 (L15 위반 시뮬) | error_fallback.md S8_EMBED_OOM 트리거 + SDAR Repair → batch 16 분할 |
| 12 | L21 1,000 초과 시도 | 1,001번째 페이지 요청 | rate limiter 차단 + 24h 후 retry schedule |

---

## §13. CONFLICT 상태

본 §13 은 신규 [CONFLICT_CANDIDATE] 발화 0건. CL-C001/C002 + W-1/W-2/W-3 RESOLVED 5건 통산 보존 (gate_details.md §10 / error_fallback.md §13 인용 정합).

---

## §14. ISS-2 + P5 해결 표기

- **ISS-2 해결**: 스케일링 정책 미상세 (MEDIUM) → V1 수직 / V2 Docker Swarm 2-3노드 / V3 K8s HPA min=2 max=10 CPU>70% 트리거 + LOCK L9/L14/L15/L17/L21 운영 제약 매핑 + 비용 관리 + 12건 테스트 시나리오 = ISS-2 ✅ 완료 (Phase 2 P2-3 산출물).
- **P5 (Phase 2 part) 해결**: 배포/스케일링 전략 미정의 (MEDIUM) → DH-CL-D1 verbatim (V1/V2/V3) + 인프라 + 비용 매트릭스 = P5 ✅ Phase 2 part 완료. 자기 진화 자동 확장은 V3 자율 진화 범위로 Phase 3 이월.

---

## §15. 변경 이력

| 일자 | 버전 | 변경 | 근거 |
|------|------|------|------|
| 2026-04-28 | V2-Phase 2 P2-3 | NEW — STAGE 7 STEP_B P2-3 V2 신규 작성 | ISS-2 + P5 (Phase 2 part) 해결, exit_gate 4/4 산출물 3번째 |

---

<!-- END OF DOCUMENT -->
