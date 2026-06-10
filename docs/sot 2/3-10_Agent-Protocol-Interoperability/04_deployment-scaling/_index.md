# 04. Deployment & Scaling — 에이전트 배포/스케일링

> **서브도메인**: D — 에이전트 배포 및 확장
> **STEP7-K 범위**: K-055 ~ K-060 (6항목)
> **현재 레벨**: L0
> **목표 레벨**: L3
> **Part2 상태**: ABSENT — 0 반영 / 6 미반영 전체. 해결: 전면 신규.

---

## 담당 K-ID 목록

| STEP7-K | 항목명 | Part2 상태 | 현재 레벨 | 목표 | V 스코프 |
|---------|--------|-----------|----------|------|---------|
| K-055 | 에이전트 패키징 | ABSENT | L0 | L3 | V2 |
| K-056 | 에이전트 스케일링 | ABSENT | L0 | L2 | V3 (K8s 오토스케일링) |
| K-057 | 에이전트 헬스체크 | ABSENT | L0 | L3 | V2 |
| K-058 | 에이전트 로깅/트레이싱 | ABSENT | L0 | L3 | V2 |
| K-059 | 에이전트 설정 관리 | ABSENT | L0 | L3 | V2 |
| K-060 | 에이전트 마이그레이션 | ABSENT | L0 | L2 | V2 |

## 리소스 클래스 정의 (R-13-5)

| 클래스 | CPU | Memory | GPU | 용도 |
|--------|-----|--------|-----|------|
| light | 0.5 | 1Gi | - | 텍스트 처리, 간단한 도구 호출 |
| standard | 1 | 2Gi | - | 코드 생성, 멀티턴 대화 |
| heavy | 2 | 4Gi | - | 로컬 LLM 추론, 멀티모달 |

## 계획 파일 목록

| 파일 | 내용 | 상태 |
|------|------|------|
| `_index.md` | 본 인덱스 | 생성 완료 |
| `container_spec.md` | Docker 컨테이너 표준, 라벨, 헬스 프로브 | 생성 예정 (§11.1 FR-1) |

---

*정본 소유: #13 Agent-Protocol-Interoperability*
*배포 파이프라인: #15 CI/CD 정본 참조*

---

## V2-Phase 2 상태 (2026-04-22, STAGE 7 STEP_B #2b)

**V2 파일 수 = 5 NEW** (K-055 / K-057~K-060, K-056 K8s V3 제외)

| # | 파일 | V2 상태 | line (wc -l) | K-ID |
|---|------|:-------:|-----------:|------|
| 1 | `container_spec.md` | NEW | 479 | K-055 (STEP7-K L1089~L1099) |
| 2 | `healthcheck_spec.md` | NEW | 425 | K-057 (L1113~L1123) |
| 3 | `logging_spec.md` | NEW | 410 | K-058 (L1125~L1141) |
| 4 | `config_spec.md` | NEW | 471 | K-059 (L1143~L1153) |
| 5 | `migration_guide.md` | NEW | 388 | K-060 (L1155~L1165) |

K-056 Kubernetes (STEP7-K L1101~L1111) V3 이관 명시 (5 파일 헤더 + container §2.2 + migration §11 MG-12 전수). 5-way cross-check PASS (container↔healthcheck↔logging↔config↔migration).

---

## V3-Phase 4 상태 (2026-06-03, Phase 4 production promotion RECOVERY)

**V3 파일 수 = 1 NEW** (K-056 K8s 풀 오토스케일링)

| # | 파일 | V3 상태 | line (wc -l) | K-ID | Status |
|---|------|:-------:|-----------:|------|:------:|
| 1 | `k8s_autoscaling.md` | NEW | — | K-056 (STEP7-K L1101~L1111) | **APPROVED** |

K-056 HPA/VPA/CA 3중 + custom metrics(agent_rps) + R-13-5 리소스 클래스 (k8s_autoscaling §7.1: light 0.5/1Gi / standard 1/2Gi / heavy 2/4Gi, plan §7.5 L1499 정본) + LOCK-AP-09 비용 가드 ₩40K/₩93K/₩266K verbatim. 4-1 IPC↔K8s + 6-13 Operations + 6-2 RBAC cross-handoff. 멀티 클러스터·멀티 클라우드 Phase 4+ 이월. Status DRAFT→APPROVED.
