# 02_hetzner-resource — Hetzner Lite 리소스 관리

> **도메인**: 6-13_Operations / 02_hetzner-resource
> **Part2 출처**: §6.12.1.5 (L5987-6020)
> **LOCK**: LOCK-OP-08 ($200 월간 상한), LOCK-OP-13 (CX31 2vCPU/8GB/80GB)

---

## Part2 원문 (When/Where)

### 리소스 분배 가이드라인

| 리소스 | 총량 | ORANGE CORE | AI Investing | BLUE NODE | 시스템/예비 |
|--------|------|-------------|-------------|-----------|-----------|
| CPU | 2vCPU | 0.5 | 0.3 | 0.3 | 0.9 |
| 메모리 | 6Gi (8GB-Swap 2GB) | 1.5Gi | 1.5Gi | 1Gi | 2Gi |
| 디스크 | 80GB | 10GB | 10GB | 5GB | 55GB |
| Redis | 512MB | DB0 200MB | DB2 200MB | DB1 100MB | DB3 MessageBus |

### 운영 원칙

1. Swap 2GB 활성화 필수. OOM 시 BLUE NODE 우선 정지
2. 고부하 배치: 야간(UTC 02:00~06:00) cron 예약
3. 로그 로테이션 30일, docker system prune 주 1회
4. 월 1회 Docker Compose 재시작 (메모리 누수 정리)
5. Grafana 합계 비용 알림 — $140 경고(70%) / $170 주의(85%) / $190 위험(95%) / $200 초과(100%) (LOCK-OP-07, $200 LOCK-OP-08 초과 방지)

### Hetzner Lite vs K8s 풀스펙

| 항목 | Hetzner Lite | K8s 풀스펙 |
|------|-------------|----------|
| 월 비용 | ~$123-142 | ~$500+ |
| 자동 스케일링 | 수동 | HPA 자동 |
| 롤백 | docker compose (2-3분) | Helm rollback (30초) |
| GPU | RunPod Serverless | 전용 GPU 노드 |

## SOT2 상세 (What/How)

### Hetzner→K8s 전환 판단 기준

| 조건 | 기준 | 조치 |
|------|------|------|
| 월 비용 $180+ 3개월 연속 | 비용 효율성 역전 | K8s 전환 검토 시작 |
| CPU 사용률 > 80% 상시 | 리소스 부족 | GPU 워크로드 분리 후 재평가 |
| 사용자 2인+ 동시 사용 | 단일 서버 한계 | K8s 멀티 노드 전환 |
| SLA 99.95%+ 요구 | 단일 서버 SLA 99.9% 한계 | K8s HA 구성 |

### 구현 시 결정 (§6.12.12 관련)

- Swap 크기: 2GB 기본, OOM 빈도에 따라 4GB 확대 고려
- cron 배치 시간: UTC 02:00~06:00 기본, 사용 패턴에 따라 조정

## 하위 파일 (Phase 예정)

| 파일 | 내용 | 상태 |
|------|------|------|
| `resource_allocation.md` | 리소스 분배 상세 + 모니터링 스크립트 | 예정 |
| `migration_criteria.md` | Hetzner→K8s 전환 판단 기준 상세 | 예정 |
