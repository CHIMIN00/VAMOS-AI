# Kubernetes 풀 오토스케일링 — K-056 (V3 신규 L3, Phase 4 production-ready 정본)

> **STEP7-K**: K-056 Kubernetes 풀 오토스케일링 (L1101~L1111 원문 / `150720a3496f557d359a421dcbf0922ebe5b1e4fbaa06611eff40e0865177539`)
> **레벨**: L3 (V3-Phase 3 SPEC 완료 → Phase 4 production 승급)
> **정본 소유**: #13 Agent-Protocol-Interoperability / 04_deployment-scaling
> **V 스코프**: V3-Phase 3 (HPA/VPA/CA 3중 스케일 + custom metrics agent_rps + 리소스 클래스 + LOCK-AP-09 비용 가드)
> **Phase 4 태그**: V3-Phase 4 production-ready 정본 승급 (RECOVERY genuine write, P4-2)
> **Status**: APPROVED (DRAFT → APPROVED, 2026-06-03 Phase 4 production promotion)
> **Last-reviewed**: 2026-06-03
> **upstream baseline**: STEP7-K sha256 `150720a3496f557d359a421dcbf0922ebe5b1e4fbaa06611eff40e0865177539`

---

## §1. 교차 참조 블록

| 정본 문서 | 섹션 | 참조 내용 |
|----------|------|----------|
| STEP7-K (Level 2) | L1101~L1111 | K-056 원문 (HPA/VPA/Cluster Autoscaler/메트릭 기반 스케일) |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-04 | Streamable HTTP — 에이전트 엔드포인트 K8s Service |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-09 | 비용 상한 V1 ₩40K / V2 ₩93K / V3 ₩266K — 클러스터 총 비용 가드 |
| AUTHORITY_CHAIN.md | §4 | 에이전트 배포/스케일링 #13 정본 소유 |
| 구조화_종합계획서.md | §7.5 P3-2 L1476~L1513 | Phase 3 V3 K-056 K8s 풀 오토스케일링 |
| 04_deployment-scaling/container_spec.md (V2) | §2.2 | 컨테이너 이미지·리소스 정본 (K8s Pod 스펙 베이스) |
| 04_deployment-scaling/healthcheck_spec.md (V2) | §7.2 | liveness/readiness probe (HPA 입력) |
| 04_deployment-scaling/config_spec.md (V2) | §7.1 | Secret/ConfigMap (K8s 환경 변수) |
| 04_deployment-scaling/migration_guide.md (V2) | §11 MG-12 | 환경 승격 (K8s 배포 절차) |
| **4-1 Rust-Tauri Infrastructure** | IPC ↔ K8s | 클라이언트 IPC ↔ K8s 백엔드 통신 매핑 (cross-ref) |
| 6-13 Operations | K8s 운영 표준 | 운영 표준 inline (ARCHIVED inheritance) |
| 6-2 Security-Governance | K8s RBAC | 클러스터 RBAC 정책 정본 |

> **R6 준수**: What+How 전용. K8s 운영 표준은 6-13 Operations(ARCHIVED) inline 계승, RBAC 정책 정본은 6-2.

---

## §2. Purpose & Scope (E1 목표 / E2 범위)

### 2.1 K8s 오토스케일링 5대 요건 (STEP7-K L1101~L1111 원문)

| 요건 | 원문 | 본 문서 섹션 |
|------|------|-------------|
| HPA (Horizontal Pod Autoscaler) | L1102 | §4 HPA |
| VPA (Vertical Pod Autoscaler) | L1104 | §5 VPA |
| Cluster Autoscaler (CA) | L1106 | §6 CA |
| custom metrics (agent_rps) | L1108 | §4.2 custom metrics |
| 리소스 클래스 + 비용 가드 (LOCK-AP-09) | L1110 | §7 리소스/비용 |

### 2.2 범위 경계 (E2)

| 영역 | 본 문서 | 정본 소유 |
|------|--------|----------|
| HPA/VPA/CA + custom metrics + 리소스 클래스 | ✅ | — |
| 컨테이너 이미지·베이스 리소스 | 참조 | container_spec.md (V2) |
| K8s 운영 표준 (배포/롤백/모니터링) | 참조 inline | 6-13 Operations (ARCHIVED) |
| 클러스터 RBAC 보안 | 참조 | 6-2 Security-Governance |
| 클라이언트 IPC | ❌ | 4-1 Rust-Tauri Infrastructure |

### 2.3 VAMOS 독자 혁신 포지셔닝

| 비교 대상 | 기존 | VAMOS K8s 오토스케일 |
|----------|------|---------------------|
| 일반 웹 서비스 HPA (CPU만) | CPU 기반 단순 스케일 | 에이전트 RPS custom metrics + 리소스 클래스(light/standard/heavy) + LOCK-AP-09 비용 상한 통합 가드 |

---

## §3. 공통 자료 구조 Import (E3)

```python
from sot2_domain.agent_protocol_interoperability.types import (
    VamosMessage,        # LOCK-AP-01 6필드
)
from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, List
```

---

## §4. HPA (Horizontal Pod Autoscaler) (D1 / E4)

### 4.1 HPA config (YAML schema)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: vamos-agent-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: vamos-agent
  minReplicas: 2
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70        # HPA target CPU 70%
    - type: Pods
      pods:
        metric:
          name: agent_rps                # custom metrics
        target:
          type: AverageValue
          averageValue: "50"
```

### 4.2 custom metrics (agent_rps)

에이전트 초당 요청 수(`agent_rps`)를 Prometheus Adapter 경유로 노출. HPA 가 CPU 70% 와 agent_rps 50 중 더 높은 스케일 신호 채택. 엔드포인트는 LOCK-AP-04 Streamable HTTP.

---

## §5. VPA (Vertical Pod Autoscaler) (E5)

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: vamos-agent-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: vamos-agent
  updatePolicy:
    updateMode: "Auto"                   # recommendation + 자동 적용
  resourcePolicy:
    containerPolicies:
      - containerName: agent
        controlledResources: ["memory"]            # VPA 는 memory 만 (CPU 는 HPA 전담, §5 동시제어 금지)
        minAllowed: { memory: "512Mi" }
        maxAllowed: { memory: "4Gi" }              # heavy 클래스 상한
```

> VPA `updateMode: Auto` 와 HPA 는 동일 리소스(CPU) 동시 제어 금지 — VPA 는 memory + recommendation, HPA 는 CPU/RPS 스케일로 역할 분리.

---

## §6. Cluster Autoscaler (CA) (E6)

| 설정 | 값 | 비고 |
|------|-----|------|
| node pool min/max | 1 / 8 | 비용 가드 연동 |
| scale-down delay | 10분 | 플래핑 방지 |
| utilization threshold | 50% | 노드 축소 기준 |
| expander | least-waste | 비용 최적 노드 선택 |

CA 는 Pending Pod 발생 시 노드 증설, utilization < 50% 지속 시 축소. 총 노드 비용은 §7.2 LOCK-AP-09 상한 내 제한.

---

## §7. 리소스 클래스 + 비용 가드 (E7 — R-13-5 + LOCK-AP-09)

### 7.1 리소스 클래스 매핑 (R-13-5 verbatim)

> **R-13-5**: 에이전트 배포 시 리소스 클래스 light/standard/heavy 명시 필수 (K-055~K-056).

| 클래스 | requests (CPU/Mem) | limits (CPU/Mem) | 용도 |
|--------|:------------------:|:----------------:|------|
| `light` | 0.5 / 1Gi | 0.5 / 1Gi | 단순 대화/조회 에이전트 |
| `standard` | 1 / 2Gi | 1 / 2Gi | 일반 작업 에이전트 |
| `heavy` | 2 / 4Gi | 2 / 4Gi | 멀티스텝/도구 집약 에이전트 |

### 7.2 LOCK-AP-09 비용 가드 정본 전재 (verbatim)

> **LOCK (§3.4 LOCK-AP-09)**: 비용 상한 = V1: ₩40K, V2: ₩93K, V3: ₩266K (Part2 §비용 + 가이드 부록 D, STEP7-H 참조) — 변경 금지.

```python
def enforce_cost_guard(monthly_cluster_krw: float, tier: str) -> bool:
    cap = {"V1": 40_000, "V2": 93_000, "V3": 266_000}[tier]   # LOCK-AP-09
    if monthly_cluster_krw > cap:
        emit_escalation("cost_cap_exceeded", monthly_cluster_krw, cap)
        return False        # 스케일아웃 차단 + HITL
    return True
```

클러스터 총 비용(노드 + 컴퓨트)이 LOCK-AP-09 V3 ₩266K 상한 초과 시 HPA/CA 스케일아웃 동결 + HITL 보고.

---

## §8. Phase 별 복구 흐름 + Confidence Penalty (E8)

| 이벤트 | Confidence Penalty | HITL (< 0.50) |
|--------|:-----------------:|:-------------:|
| 클러스터 비용 LOCK-AP-09 상한 초과 | -0.30 | ✅ (스케일아웃 동결) |
| HPA ↔ VPA CPU 동시 제어 충돌 | -0.20 | ✅ |
| CA 노드 플래핑 (10분 내 증설/축소 반복) | -0.15 | 누적 기준 |
| 리소스 클래스 미지정 배포 | -0.25 | ✅ (R-13-5 위반) |
| maxReplicas 도달 + RPS 지속 상승 | -0.10 | 용량 알람 |

> LOCK-AP-10 재정의 없음 — 06_autonomy-safety/guardrail_rules.md (P2-6 정본) cumulative 기준.

---

## §9. 에스컬레이션 + LOCK 매핑 5필드 표 (E9 / E10)

```python
class K8sScalingEscalation(BaseModel):
    trace_id: str
    event_class: Literal[
        "cost_cap_exceeded",
        "hpa_vpa_conflict",
        "node_flapping",
        "resource_class_missing",
        "max_replicas_saturated",
    ]
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    confidence_delta: float = Field(..., le=0.0, ge=-1.0)
    cluster_id: str
    recommended_action: Literal["freeze_scaleout", "escalate_hitl_L3", "rebalance", "capacity_alert"]
    occurred_at: datetime
```

| LOCK ID | 항목 | 원본 문서 | 값 | 재정의 | 본 문서 적용 지점 |
|---------|------|----------|-----|--------|------------------|
| LOCK-AP-04 | MCP 전송 방식 | Part2 §6.6 | Streamable HTTP (V1), WebSocket 아님 | 금지 | §4.2 agent_rps 엔드포인트 HTTP |
| LOCK-AP-09 | 비용 상한 | Part2 §비용 + 가이드 부록 D (STEP7-H 참조) | V1: ₩40K, V2: ₩93K, V3: ₩266K | 금지 | §7.2 정본 전재 + 비용 가드 enforce |
| LOCK-AP-10 | Confidence 임계값 | DEFINED-HERE (06_autonomy-safety 정본) | HITL 트리거 < 50% | 금지 | §8 penalty (참조자, 재정의 없음) |

---

## §10. Phase 3 테스트 시나리오 (≥ 10건)

| # | ID | 설명 | 기대 결과 |
|---|----|------|----------|
| 1 | KA-01 | CPU 70% 도달 → HPA scale-out | ✅ §4.1 |
| 2 | KA-02 | agent_rps 50 초과 → HPA scale-out (CPU보다 우선) | ✅ §4.2 |
| 3 | KA-03 | VPA recommendation → memory 자동 조정 | ✅ §5 |
| 4 | KA-04 | Pending Pod → CA 노드 증설 | ✅ §6 |
| 5 | KA-05 | utilization < 50% 10분 → 노드 축소 | ✅ §6 |
| 6 | KA-06 | 클러스터 비용 ₩270K → LOCK-AP-09 상한 초과 동결 | ✅ §7.2 |
| 7 | KA-07 | 리소스 클래스 미지정 배포 → R-13-5 거부 | ✅ §8 |
| 8 | KA-08 | HPA+VPA CPU 동시 제어 시도 → 충돌 차단 | ✅ §5 |
| 9 | KA-09 | heavy 클래스 (2/4Gi) limits 적용 | ✅ §7.1 |
| 10 | KA-10 | maxReplicas 20 도달 + RPS 상승 → 용량 알람 | ✅ §8 |
| 11 | KA-11 | 4-1 IPC ↔ K8s Service 통신 매핑 정합 | ✅ §1 cross-ref |
| 12 | KA-12 | Langfuse trace `k8s.scale.*` span 기록 | ✅ logging_spec.md §5.1 |

---

## §11. 세션 간 인터페이스 Cross-check 표

| 인터페이스 | 대상 파일 | 검증 기준 |
|-----------|----------|----------|
| 컨테이너 베이스 리소스 | `container_spec.md §2.2` | Pod 스펙 baseline |
| probe (HPA 입력) | `healthcheck_spec.md §7.2` | liveness/readiness |
| Secret/ConfigMap | `config_spec.md §7.1` | K8s 환경 변수 |
| 환경 승격 절차 | `migration_guide.md §11 MG-12` | 배포 절차 |
| IPC ↔ K8s | `4-1 Rust-Tauri Infrastructure` | 클라이언트↔백엔드 통신 |
| K8s RBAC | `6-2 Security-Governance` | 클러스터 RBAC 정본 |

---

## §12. 검증 자가 체크리스트 (L3 D1~D8 + E1~E10)

- [x] STEP7-K L1101~L1111 K-056 5대 요건 전수 구현 (HPA/VPA/CA/custom metrics/비용가드)
- [x] HPA target CPU 70% + custom metrics agent_rps (§4)
- [x] VPA Auto + CA least-waste expander (§5/§6)
- [x] R-13-5 리소스 클래스 light(0.5/1Gi)/standard(1/2Gi)/heavy(2/4Gi) verbatim (§7.1)
- [x] LOCK-AP-09 비용 가드 ₩40K/₩93K/₩266K verbatim 전재 + enforce (§7.2)
- [x] LOCK-AP-04/09/10 5필드 분리 인용 (§9)
- [x] LOCK-AP-10 재정의 없음 (§8 참조자)
- [x] 4-1 IPC ↔ K8s + 6-13 + 6-2 cross-handoff reference (§11)
- [x] Phase 3 테스트 12건 (≥ 10 요건 충족, §10)
- [x] 멀티 클러스터·멀티 클라우드 Phase 4+ 이월 명시 (§13)
- [x] Status DRAFT → APPROVED 전환 (Phase 4 production 승급)

---

## §13. Phase 4+ 이월

- 멀티 클러스터 (federation) + 멀티 클라우드 (AWS/GCP/Azure 분산) 오토스케일링은 **Phase 4+ 이월**.
- 본 V3 는 단일 클러스터 HPA/VPA/CA + custom metrics + 비용 가드까지 production-ready.

---

*정본 소유: #13 Agent-Protocol-Interoperability (에이전트 배포/스케일링 — K8s 오토스케일)*
*LOCK-AP-09 비용 상한 ₩40K/₩93K/₩266K + R-13-5 리소스 클래스 verbatim 보존*
*K8s 운영 표준은 6-13 Operations(ARCHIVED) inline, 클러스터 RBAC 정본은 6-2 Security-Governance*
