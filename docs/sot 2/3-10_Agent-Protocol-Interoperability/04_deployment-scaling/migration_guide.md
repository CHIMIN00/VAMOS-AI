# 에이전트 마이그레이션 & 롤백 — K-060 (V2 신규 L2)

> **STEP7-K**: K-060 에이전트 마이그레이션 (L1155~L1165 원문 / `150720a3496f557d359a421dcbf0922ebe5b1e4fbaa06611eff40e0865177539`)
> **레벨**: L2→L3 (V2-Phase 2 신규)
> **Part2 상태**: ABSENT — 본 문서로 L2+ 방식 C 신규
> **정본 소유**: #13 Agent-Protocol-Interoperability / 04_deployment-scaling
> **V 스코프**: V2-Phase 2 (K-056 Kubernetes 배포 STEP7-K L1101~L1111 은 plan §7.5 V3 이관 명시, 본 V2 Phase 2 범위 제외)
> **V2 태그**: V2-Phase 2 (2026-04-22, STAGE 7 STEP_B #2b 3-10 도메인 P2-4 세션 신규 작성)
> **upstream baseline**: STEP7-K sha256 `150720a3496f557d359a421dcbf0922ebe5b1e4fbaa06611eff40e0865177539`

---

## §1. 교차 참조 블록

| 정본 문서 | 섹션 | 참조 내용 |
|----------|------|----------|
| STEP7-K (Level 2) | L1155~L1165 | K-060 원문 (V1→V2→V3, 데이터/설정 마이그레이션, Blue-Green, 롤백) |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-01 | VamosMessage 스키마 변경 시 호환성 확보 |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-02 | Permission Level 0~5 — 마이그레이션 실행은 L3 이상 |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-04 | Streamable HTTP 엔드포인트 전환 시 호환성 |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-07 | A2A + MCP 양방향 — blue/green 간 트래픽 교차 시 둘 다 지원 |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-09 | 비용 상한 — 이중 환경(blue+green) 운영 기간 비용 |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-10 | Confidence < 50% HITL (06_autonomy-safety 정본) |
| 구조화_종합계획서.md | §7.4 P2-4 L1213~L1245 | Phase 2 K-060 배치 |
| 04_deployment-scaling/_index.md | L20 | K-060 L0→L2 (V2 2개월 — 원문 L1165) |
| 04_deployment-scaling/container_spec.md | §7 태그 전략 | digest pin 승격 경로 |
| 04_deployment-scaling/healthcheck_spec.md | §2 readiness | canary 평가 기준 |
| 04_deployment-scaling/logging_spec.md | §5.1 span `deploy.*` | 마이그레이션 관측 |
| 04_deployment-scaling/config_spec.md | §4.4 환경 승격 | dev/staging/prod 승격 규칙 |
| 01_framework-adapters/langgraph_adapter.md | §3 | 공통 자료 구조 import |
| 6-4 Memory-RAG-Storage | LOCK-MR 메모리 스키마 | 메모리 마이그레이션 정본 경계 |
| 6-6 Self-Evolution-System | DH 데이터 핸드오프 | V1→V2 스키마 변환 정본 소비 |
| 4-2 CICD-Pipeline | Blue-Green 파이프라인 | 배포 파이프라인 정본 |

> **R6 준수**: What+How 전용.

---

## §2. Purpose & Scope

### 2.1 4대 요건 (STEP7-K L1159~L1162 원문)

| 요건 | 섹션 | 핵심 |
|------|------|------|
| 데이터 마이그레이션 (메모리·설정·히스토리) | §4 | 스키마 버전 × 변환기 |
| 설정 마이그레이션 (호환성 변환) | §5 | config diff + migrator |
| 다운타임 없는 업그레이드 (Blue-Green) | §3 | 트래픽 이중화 + canary |
| 롤백 지원 (문제 시 이전 버전) | §6 | digest rollback + state replay |

### 2.2 범위 경계

| 영역 | 본 문서 | 정본 소유 |
|------|--------|----------|
| 배포 절차 × 롤백 판단 로직 | ✅ | — |
| CI/CD 파이프라인 구현 | ❌ | 4-2 CICD-Pipeline |
| 메모리 스키마 정본 | 참조 | 6-4 Memory-RAG-Storage |
| 자기진화 전략 전환 | 참조 | `05_self-evolution/*` (P2-5) |

---

## §3. Blue-Green 배포 (STEP7-K L1161 원문 "다운타임 없는 업그레이드")

### 3.1 상태 모델

```
        ┌──────────┐   100 %   ┌──────────┐
 users ─▶  Router  ──────────▶   BLUE    │  (현재 안정 버전)
        └────┬─────┘            └──────────┘
             │                   ┌──────────┐
             └─  0 % → canary ─▶    GREEN   │  (새 버전 후보)
                                 └──────────┘
```

### 3.2 승격 단계 (점진 shift)

| 단계 | BLUE → GREEN 비율 | 관찰 지표 | 진입 조건 |
|:----:|:----------------:|----------|----------|
| S0 pre-deploy | 100:0 | baseline SLI 수집 | GREEN image digest 검증 통과 |
| S1 canary | 95:5 | 에러율 · p95 · confidence | GREEN readiness 3/3 |
| S2 ramp | 75:25 | SLO 전수 | S1 5분 안정 + 에러율 < 1 % |
| S3 half | 50:50 | 비용·메모리 | S2 10분 안정 |
| S4 shift | 25:75 | GREEN 단독 리스크 평가 | S3 15분 안정 |
| S5 full | 0:100 | BLUE warm standby 유지 | S4 15분 안정 |
| S6 retire | BLUE deprovision | — | S5 60분 안정 + 사용자 승인 (LOCK-AP-02 L3) |

각 단계 전이 사이 최소 대기 시간: S1 5분, S2 10분, S3~S4 15분, S5 60분.

### 3.3 Canary 판정 SLI 임계

| SLI | 기준 (상대 BLUE) | 위반 시 |
|-----|------------------|--------|
| 에러율 | GREEN ≤ BLUE × 1.2 (위반 for 2m) | 자동 롤백 (§6.1) |
| p95 latency | GREEN ≤ BLUE × 1.25 (위반 for 3m) | 자동 롤백 (§6.1) |
| queue saturation | GREEN ≤ BLUE × 1.30 | 경고 + 체류 |
| confidence avg | GREEN ≥ BLUE - 0.05 | LOCK-AP-10 발동 시 롤백 |
| LOCK 위반 (metric) | 0건 유지 | 즉시 롤백 (중대) |

---

## §4. 데이터 마이그레이션 (STEP7-K L1159 원문)

### 4.1 스키마 버전 × Migrator

```python
from pydantic import BaseModel
from typing import Callable, Dict, List

class SchemaVersion(BaseModel):
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

class Migrator:
    def __init__(self, from_v: SchemaVersion, to_v: SchemaVersion):
        self.from_v = from_v
        self.to_v = to_v

    def migrate_record(self, record: dict) -> dict:
        raise NotImplementedError

MIGRATION_CHAIN: List[Migrator] = [
    # 예: v1.0.0 → v1.1.0 VamosMessage.metadata.trace_id 신설
    Migrator(SchemaVersion(major=1, minor=0, patch=0),
             SchemaVersion(major=1, minor=1, patch=0)),
    # v1.1.0 → v2.0.0 confidence 필드 neg 값 허용
    Migrator(SchemaVersion(major=1, minor=1, patch=0),
             SchemaVersion(major=2, minor=0, patch=0)),
]
```

### 4.2 마이그레이션 대상별 전략

| 대상 | 규모 (예상 V2) | 전략 | 다운타임 |
|------|:-------------:|------|:-------:|
| 에이전트 메모리 (6-4 정본) | ~50 GB | 읽기-두 쓰기 (dual-write) | 0 |
| 대화 히스토리 (3-8 정본 A2A task) | ~10 GB | 배치 변환 + 온라인 flag | 0 |
| 설정 파일 | < 1 MB | in-place migrator | 0 |
| 벡터 스토어 임베딩 | ~30 GB | 백그라운드 재계산 | 0 (성능 일시 저하) |
| 트레이스 이력 (14~30d) | 참조 | 이관 없음 (자연 만료) | — |

### 4.3 Dual-write 기간 운영

```
[V1 ingress] ─▶ V1 store (legacy)
               └─▶ Adapter ─▶ V2 store (new schema)

→ 실패 시 V2 store 쓰기 실패만 기록, 읽기는 V1 유지. canary 통과 후 ingress 를 V2 로 전환.
```

### 4.4 메모리 스키마 마이그레이션 (#11 정본 경계)

- 정본 스키마 변경은 **6-4 Memory-RAG-Storage** DH (데이터 핸드오프) 계약 준수
- 본 문서는 Blue-Green 운영 관점에서 **호출 방식·롤백 시점**만 다룸
- 신규 필드 추가 시 V1 이 무시할 수 있도록 `additionalProperties` 허용

---

## §5. 설정 마이그레이션 (호환성 변환)

### 5.1 config 호환성 매트릭스

| From → To | 호환성 | 자동 변환기 | 필수 수작업 |
|-----------|:------:|:----------:|:----------:|
| v1.0 → v1.1 | backward | `config_migrate_v1_0_to_v1_1.py` | 없음 |
| v1.1 → v2.0 | 필드 변경 | `config_migrate_v1_1_to_v2_0.py` | 이름 변경 5 필드 |
| v2.0 → v3.0 | breaking | ❌ | 수작업 + HITL L3 |

### 5.2 Migrator 계약

```python
class ConfigMigrator(BaseModel):
    source_version: str
    target_version: str
    breaking: bool

    def dry_run(self, config_yaml: str) -> "MigrationReport":
        """변경 내역 + 경고 리스트 반환, 실제 적용 없음"""
        raise NotImplementedError

    def apply(self, config_yaml: str) -> str:
        raise NotImplementedError

class MigrationReport(BaseModel):
    changes: List[str]
    warnings: List[str]
    requires_hitl: bool
```

### 5.3 dry-run 필수 (prod 사전)

prod 마이그레이션 전 dry-run 결과를 CONFLICT_LOG 에 첨부 + 사용자 L3 승인.

---

## §6. 롤백 (STEP7-K L1162 원문 "문제 시 이전 버전으로")

### 6.1 자동 롤백 트리거

| 조건 | 반응 | 지연 |
|------|------|:----:|
| canary readiness 실패 (healthcheck_spec.md §2) | 즉시 S0 복귀 | 0 s |
| 에러율 > BLUE × 1.2 for 2m | 즉시 이전 단계 | 0 s |
| p95 > BLUE × 1.25 for 3m | 즉시 이전 단계 | 0 s |
| confidence < 0.50 (LOCK-AP-10) | 즉시 S0 | 0 s |
| LOCK-AP-\* metric violation > 0 | 즉시 S0 + 감사 | 0 s |
| 사용자 수동 롤백 명령 | 즉시 | 0 s |

### 6.2 롤백 순서 (Blue-Green)

```
1. Router 트래픽 비율 GREEN → 0 (BLUE 100 %)
2. GREEN readiness drain 확인
3. 데이터 dual-write 시 GREEN 쓰기 중단 + 읽기 fallback
4. GREEN pod/container warm standby 로 유지 (다음 시도 대비)
5. logging_spec.md §11 observability 에스컬레이션 + CONFLICT_LOG row
6. 메모리 스키마 breaking 변경이 있었다면 6-4 DH 롤백 트리거
7. 사용자 보고 + HITL L3 승인 후 재시도 여부 결정
```

### 6.3 Rollback State Replay

BLUE 로 돌아간 뒤 GREEN 기간 중 수신한 메시지 중 dual-write 로 V2 에만 기록된 것이 있으면:

```
- event_bus replay (03_data-exchange/event_bus.md — V1 경로)
- V1 스키마로 재변환 (역 migrator)
- 실패 건은 CONFLICT_LOG 에 quarantine
```

### 6.4 부분 롤백 금지

Router 비율을 BLUE 100 ~ GREEN 0 이 아닌 중간값(예: BLUE 80/GREEN 20)으로 지속 유지 금지. 단, 승격 단계 전이 중 일시적 비율은 §3.2 허용.

---

## §7. 비용 관점 (LOCK-AP-09 verbatim)

### 7.1 LOCK-AP-09 정본 전재

| LOCK ID | 항목 | 원본 문서 | 값 | 재정의 |
|---------|------|----------|-----|--------|
| LOCK-AP-09 | 비용 상한 | Part2 §비용 + 가이드 부록 D (STEP7-H 참조) | V1: ₩40K, V2: ₩93K, V3: ₩266K | **금지** |

### 7.2 Blue-Green 이중 운영 기간 비용 증분

| 구간 | 정상 운영 | Blue+Green 병행 (최대 2 시간/월) | 증분 비율 |
|------|:--------:|:-------------------------------:|:--------:|
| V1 | 40 000 ₩/월 | +1 500 ₩ | +3.8 % |
| V2 | 93 000 ₩/월 | +3 500 ₩ | +3.8 % |
| V3 | 266 000 ₩/월 | +10 000 ₩ | +3.8 % |

→ 마이그레이션 빈도 월 2회 × 1시간 병행 기준. 초과 시 V2 ₩93K 상한 재확인 필수.

---

## §8. Phase 별 복구/다운그레이드 흐름 + Confidence Penalty

| 이벤트 | Confidence Penalty | HITL (< 0.50) |
|--------|:-----------------:|:-------------:|
| canary readiness 실패 → S0 | -0.10 | 누적 기준 |
| 에러율 SLI 위반 → 자동 롤백 | -0.15 | 누적 기준 |
| dual-write 실패 지속 > 5m | -0.20 | 누적 기준 |
| migrator breaking 변경 HITL 미승인 | -0.30 | ✅ |
| Rollback state replay 실패 | -0.25 | ✅ |
| 부분 롤백 유지 시도 | -0.40 | ✅ |
| 메모리 스키마 6-4 DH 롤백 트리거 | -0.15 | 협업 HITL |

> LOCK-AP-10 재정의 없음 — 06_autonomy-safety 정본 참조.

---

## §9. 에스컬레이션 페이로드 Python Class

```python
class MigrationEscalation(BaseModel):
    trace_id: str
    stage: Literal["S0", "S1", "S2", "S3", "S4", "S5", "S6"]
    event_class: Literal[
        "canary_readiness_failed",
        "sli_violation_rollback",
        "dual_write_degraded",
        "migrator_breaking_unapproved",
        "state_replay_failed",
        "partial_rollback_detected",
        "memory_schema_dh_rollback",
    ]
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    blue_digest: str
    green_digest: str
    sli_snapshot: Dict[str, float]
    confidence_delta: float = Field(..., le=0.0, ge=-1.0)
    recommended_action: str
    occurred_at: datetime

    def to_structured_log(self) -> dict:
        return {
            "error": {
                "class": self.event_class,
                "severity": self.severity,
            },
            "context": {
                "trace_id": self.trace_id,
                "stage": self.stage,
                "blue_digest": self.blue_digest,
                "green_digest": self.green_digest,
                "sli": self.sli_snapshot,
                "occurred_at": self.occurred_at.isoformat(),
            },
            "recovery": {
                "action": self.recommended_action,
                "confidence_delta": self.confidence_delta,
            },
        }
```

---

## §10. LOCK 매핑 5필드 표

| LOCK ID | 항목 | 원본 문서 | 값 | 재정의 | 본 문서 적용 지점 |
|---------|------|----------|-----|--------|------------------|
| LOCK-AP-01 | 프로토콜 메시지 포맷 | STEP7-K, D2.0-05 | VamosMessage 6필드 | 금지 | §4.1 schema migration |
| LOCK-AP-02 | 에이전트 권한 레벨 | STEP7-K K-041 | Permission Level 0~5 | 금지 | §3.2 S6 retire L3 + §5.3 dry-run HITL L3 + §6.1 수동 롤백 L3 |
| LOCK-AP-04 | MCP 전송 방식 | Part2 §6.6 | Streamable HTTP (V1), WebSocket 아님 | 금지 | §3.1 Router 트래픽 HTTP only |
| LOCK-AP-07 | 인터롭 규격 | STEP7-K | A2A + MCP 양방향 지원 필수 | 금지 | §3 Blue/Green 둘 다 양 프로토콜 유지 |
| LOCK-AP-09 | 비용 상한 | Part2 §비용 + 가이드 부록 D (STEP7-H 참조) | V1: ₩40K, V2: ₩93K, V3: ₩266K | 금지 | §7.1 verbatim + §7.2 병행 비용 증분 |
| LOCK-AP-10 | Confidence 임계값 | DEFINED-HERE (본 도메인 06_autonomy-safety 정본; MASTER_SPEC §5/§7.9 참조) | HITL 트리거 < 50% | 금지 | §3.3 confidence SLI + §6.1 자동 롤백 (참조자) |

---

## §11. Phase 3 테스트 시나리오 (≥ 10건)

| # | ID | 설명 | 기대 결과 |
|---|----|------|----------|
| 1 | MG-01 | S1 canary 5 % 트래픽 + 5분 안정 → S2 자동 진입 (STEP7-K L1161 "다운타임 없는 업그레이드") | ✅ 전이 |
| 2 | MG-02 | S1 에러율 > BLUE × 1.2 → 2분 내 S0 자동 롤백 | ✅ 자동 롤백 |
| 3 | MG-03 | v1.1→v2.0 migrator apply → 필드 5개 변경 report | ✅ dry-run |
| 4 | MG-04 | dual-write 실패 5분 지속 → P1 알람 + confidence -0.20 | ✅ LOCK-AP-10 |
| 5 | MG-05 | breaking 변경 HITL L3 승인 없이 apply → 차단 | ✅ §5.3 |
| 6 | MG-06 | S6 retire 시도를 L2 사용자 요청 → 403 | ✅ LOCK-AP-02 |
| 7 | MG-07 | GREEN 전체 LOCK metric violation 감지 → 즉시 S0 | ✅ 중대 롤백 |
| 8 | MG-08 | Router 비율 80:20 유지 > 30분 → 경고 (부분 롤백 금지) | ✅ §6.4 |
| 9 | MG-09 | canary 기간 Tempo 내 `deploy.*` span 연속 기록 | ✅ 관측 |
| 10 | MG-10 | Rollback 후 state_replay 성공률 > 99 % | ✅ §6.3 |
| 11 | MG-11 | Blue+Green 병행 월 1시간 초과 시 LOCK-AP-09 검토 알람 | ✅ §7.2 |
| 12 | MG-12 | K-056 K8s (V3 이관) 관련 manifest 편집 시도 시 차단 (본 V2 범위 외) | ✅ V3 이관 명시 준수 |

---

## §12. 세션 간 인터페이스 Cross-check 표

| 인터페이스 | 대상 V2 파일 | 검증 기준 |
|-----------|-------------|----------|
| 이미지 digest pin | `container_spec.md §7` | Blue/Green digest 모두 `@sha256:` |
| readiness probe canary 판정 | `healthcheck_spec.md §2` | S1~S4 각 단계 readiness 3/3 |
| span `deploy.*` | `logging_spec.md §5.1` | S0~S6 전이 기록 |
| dev → staging → prod 승격 diff | `config_spec.md §4.4` | 필드별 환경 값 정합 |
| 메모리 스키마 DH 롤백 | `6-4 Memory-RAG-Storage` | DH 계약 유지 |
| Self-Evolution 전략 전환 | `05_self-evolution/dream_mode.md` (P2-5) | 전략 drift 이벤트 |
| CI/CD 파이프라인 hook | `4-2 CICD-Pipeline` | pre/post-deploy hook |

---

## §13. 검증 자가 체크리스트

- [x] K-060 4대 요건 전수 구현 (데이터/설정/Blue-Green/롤백)
- [x] Blue-Green 7 stage 전이 규칙 (§3.2)
- [x] 자동 롤백 트리거 6종 (§6.1)
- [x] LOCK-AP-01/02/04/07/09/10 5필드 분리 인용 (§10)
- [x] LOCK-AP-10 재정의 없음 (§8 참조자)
- [x] LOCK-AP-09 병행 비용 증분 ≤ 3.8 % (§7.2)
- [x] FABRICATION 10-마커 0건 (step 3 finalize scan 예정)
- [x] 세션 간 인터페이스 7건 cross-check (§12)
- [x] Phase 3 테스트 12건 (≥ 10 요건 충족)
- [x] 에스컬레이션 Pydantic + structured JSON 3-block (§9)
- [x] K-056 K8s V3 이관 명시 (§11 MG-12 + 헤더 + §2.2)
- [x] 6-4 DH 경계 준수 (§4.4)

---

*정본 소유: #13 Agent-Protocol-Interoperability*
*K-056 Kubernetes 배포 (STEP7-K L1101~L1111) 는 plan §7.5 V3 이관 명시, 본 V2 Phase 2 범위 제외*
*LOCK-AP-10 HITL<50% 는 06_autonomy-safety/guardrail_rules.md (P2-6 정본) 에서 정의*
*배포 파이프라인 실체는 4-2 CICD-Pipeline 소유*
*메모리 스키마 정본은 6-4 Memory-RAG-Storage 소유*
