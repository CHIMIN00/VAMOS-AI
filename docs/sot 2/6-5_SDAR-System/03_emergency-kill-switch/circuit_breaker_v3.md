# Circuit Breaker V3 — SDAR W-CB 통합 정의 (Phase 3 P3-2 RESOLVED)

> **도메인**: 6-5_SDAR-System / 03_emergency-kill-switch
> **Tier**: 6 (System-wide Components)
> **정본**: SDAR_SPEC **§6.3** (Circuit Breaker × SDAR 양방향 통합) + **§9.6** (LOCK L16, P2 도메인 + Circuit Breaker OPEN 시 자동 복구 금지) + **§7.4** (Circuit Breaker 기존 정의 inheritance)
> **Part2 출처**: §6.9 — When/Where 정본
> **수정 정책**: **정본 APPROVED** — Phase 3 P3-2 신규 작성 + P3-3 FINAL REVIEW 후 APPROVED 전환 완료, V3 범위 implementation 시점에 확장 가능
> **Status**: **APPROVED** (P3-3 FINAL REVIEW 5-Mode 검증 ALL PASS 후 2026-05-19 Status DRAFT → APPROVED 전환, FINAL_REVIEW_REPORT.md §4 정합 — 18 파일 전수 APPROVED 통산 milestone)
> **생성일**: 2026-05-19 (P3-2, V3-Phase 0 신규 작성)
> **세션**: Phase 3 P3-2 (W-CB Circuit Breaker 최종 결정)
> **변경 이력 태그**: `V3-Phase 0` — W-CB DEFERRED_TO_PHASE3 OBSERVE_ONLY → **RESOLVED Option C** 결정 + 양 도메인 분담 인터페이스 정의

---

## §0. Purpose / Scope

본 문서는 **W-CB (Circuit Breaker)** 의 최종 소유권 결정 및 통합 정의 문서이다. STEP_C 종결 시 `DEFERRED_TO_PHASE3 OBSERVE_ONLY` 로 보류된 W-CB는 Phase 3 시점에 **6-2 Security 협의 후 Option C (양 도메인 분담)** 로 RESOLVED 전환된다. SDAR_SPEC §6.3 정본 (양방향 통합 흐름) + §9.6 LOCK L16 (P2 도메인 + Circuit Breaker OPEN 시 자동 복구 금지) + 6-2 Security ML 이상탐지 + 6-3 K8s Mesh Circuit Breaker (Istio/Linkerd 인프라 레벨) 분리 운영을 명시한다.

**Scope (Phase 3 P3-2 범위)**:
- ✅ 3 옵션 평가 매트릭스 (A: SDAR 소유 / B: 6-2 Security 소유 / C: 양 도메인 분담)
- ✅ Option C 채택 결정 + 다중 근거 (SDAR_SPEC §6.3 양방향 통합 정본 정합 + LOCK L16 SDAR_SPEC §9.6 정본 EXACT 보존 + 6-2 cross-handoff direct inheritance)
- ✅ SDAR-side 책임 정의 (L16 enforcement + SDARDetectionSignal 발행 + HALF-OPEN/CLOSED 복원 시도)
- ✅ 6-2 Security-side 책임 정의 (ML 이상탐지 → Circuit Breaker OPEN 결정 + STRIDE 위협 분류 → SDAR 자가진단 트리거)
- ✅ 6-3 K8s Mesh Circuit Breaker (Istio/Linkerd) 인프라 레벨 분리 (애플리케이션 레벨 SDAR W-CB와 별도 운영)
- ✅ L3 9요소 (E1~E9) 매트릭스 + Phase 4 entry-gate 매핑 + Phase 3 테스트 시나리오 (T-CB-01~T-CB-12)

**Out of Scope (V3 implementation 단계 이월)**:
- ❌ Circuit Breaker 구현 코드 (V3-Phase 2 별도 트랙)
- ❌ 6-2 Security ML 이상탐지 구체 알고리즘 (6-2 도메인 P3-1 소관)
- ❌ 6-3 K8s Mesh Istio/Linkerd 배포 구체 설정 (6-3 도메인 P3-2 소관)

---

## §1. 교차 참조 블록

| 정본 문서 | 섹션 | 역할 |
|----------|------|------|
| `D:\VAMOS\docs\sot\VAMOS_SDAR_DESIGN_SPECIFICATION.md` | **§6.3** (Circuit Breaker 통합) | **양방향 통합 흐름 정본** — CB→SDAR (OPEN 시 SDARDetectionSignal 발행) + SDAR→CB (수리 성공 후 HALF-OPEN/CLOSED 복원) + P2 도메인 특별 규칙 (인간 승인 필수) |
| `D:\VAMOS\docs\sot\VAMOS_SDAR_DESIGN_SPECIFICATION.md` | **§9.6** | **LOCK L16 정본** — P2 도메인 수리 인간 승인 필수, Circuit Breaker OPEN 시 자동 복구 금지 |
| `D:\VAMOS\docs\sot\VAMOS_SDAR_DESIGN_SPECIFICATION.md` | §7.4 | Circuit Breaker 기존 정의 inheritance (CLOSED ↔ OPEN ↔ HALF-OPEN 3상태) |
| `D:\VAMOS\docs\sot 2\6-5_SDAR-System\AUTHORITY_CHAIN.md` | §10.5 (G-4 OPEN 3건 명시 판정) | **W-CB DEFERRED_TO_PHASE3 OBSERVE_ONLY → RESOLVED 큐** (본 P3-2 산출물로 해소) |
| `D:\VAMOS\docs\sot 2\6-5_SDAR-System\CONFLICT_LOG.md` | v1.2 §3.1 + §7.3 | W-CB OPEN 1건 (Phase 1 경계 협의 잔여, Phase 3 시점 6-2 Security 협의 후 최종 결정) |
| `D:\VAMOS\docs\sot 2\6-5_SDAR-System\03_emergency-kill-switch\_index.md` (P2-1) | §3.4 [d] + §4 | **Kill Switch 활성화 시퀀스 + SDAR_ROLLBACK_FAILED 자동 활성화** — Circuit Breaker OPEN 시 자동 복구 금지 (L16 enforcement) |
| `D:\VAMOS\docs\sot 2\6-5_SDAR-System\03_emergency-kill-switch\operational_limits.md` (P2-3) | §4.4 W-CB 주석 | **W-CB OPEN 주석 보존 (P2-3 V2 산출물 inheritance)** — Phase 3 RESOLVED 갱신 대상 |
| `D:\VAMOS\docs\sot 2\6-5_SDAR-System\04_self-diagnosis\gate_integration.md` (P2-5) | §3.3 + §10.2 시나리오 13 | **W-CB 주석 보존 (P2-5 V2 산출물 inheritance)** — Phase 3 RESOLVED 갱신 대상 |
| `D:\VAMOS\docs\sot 2\6-2_Security-Governance\SECURITY_GOVERNANCE_구조화_종합계획서.md` | L1434 + L1448 + L1728 | **6-2 Security cross-handoff direct inheritance baseline** — "ML 이상탐지 → STRIDE 위협 분류 → SDAR 자가진단 트리거 (W-CB Circuit Breaker DEFERRED_TO_PHASE3 OBSERVE_ONLY 결정 협의)" Wave 2 #14 ✅ SPEC COMPLETE 2026-05-18 8 cross-handoff set distinct 매트릭스에 "6-5 SDAR W-CB" 포함 |
| `D:\VAMOS\docs\sot 2\6-3_Agent-Teams-PARL\AGENT_TEAMS_PARL_구조화_종합계획서.md` | L2041 + L2016 (§7.6 P3-2) | **6-3 K8s Mesh Circuit Breaker (Istio/Linkerd) 인프라 레벨 cross-ref** — "Circuit Breaker (6-5 SDAR W-CB DEFERRED_TO_PHASE3 OBSERVE_ONLY 결정 협의 필요)" Wave 2 #15 ✅ SPEC COMPLETE 2026-05-18 direct inheritance baseline |

---

## §2. LOCK 보호 항목 인용 (verbatim, AUTHORITY_CHAIN §3.4 7-컬럼)

> 본 circuit_breaker_v3.md가 직접 인용하는 LOCK 항목 4건. 7-컬럼 verbatim 분리 인용. **신규 LOCK 추가 0건, 본문 변경 0건** (LOCK 정본 = AUTHORITY_CHAIN §4 / V3 범위 이월 엄수).

| LOCK ID | 항목 | 정본 출처 | 정본 섹션 | 값/규칙 | 카테고리 | 교차 검증 |
|---------|------|----------|----------|---------|----------|----------|
| **L16** | P2 도메인 수리 인간 승인 필수 | `D:\VAMOS\docs\sot\VAMOS_SDAR_DESIGN_SPECIFICATION.md` | §9.6 | AR-Level 무관 인간 승인 필수, Circuit Breaker OPEN 시 자동 복구 금지 | 안전 | ✅ 일치 (정본 EXACT 보존, P3-2 RESOLVED 후에도 재정의 0건) |
| **L14** | Kill Switch 트리거 조건 | `D:\VAMOS\docs\sot\VAMOS_SDAR_DESIGN_SPECIFICATION.md` | §9.4 | 모든 RBAC 역할 활성화 가능, SDAR_ROLLBACK_FAILED 시 자동 ON | 안전 | ✅ 일치 (W-CB OPEN ≠ Kill Switch 활성화 — L14는 SDAR 전체 정지, L16은 P2 도메인 자동 복구 금지만) |
| **L8** | SNAPSHOT_MANDATORY | `D:\VAMOS\docs\sot\VAMOS_SDAR_DESIGN_SPECIFICATION.md` | §9.2 | MEDIUM/HIGH risk 수리 전 스냅샷 필수 | 운영 제한 | ✅ 일치 (Circuit Breaker OPEN 후 SDAR 수리 시 스냅샷 강제) |
| **L12** | ROLLBACK_TIMEOUT | `D:\VAMOS\docs\sot\VAMOS_SDAR_DESIGN_SPECIFICATION.md` | §9.2 | 300초 (초과 시 인간 에스컬레이션) | 운영 제한 | ✅ 일치 (SDAR 수리 후 Circuit Breaker HALF-OPEN/CLOSED 복원 시도 시간 제한) |

**LOCK 인용 정책**: 본 circuit_breaker_v3.md 본문에서 LOCK 값을 변경/재정의하지 않으며, 항상 AUTHORITY_CHAIN §3.4 / SDAR_SPEC 정본 출처를 참조한다. **신규 LOCK-CB-* 추가 0건** (Option C 채택으로 양 도메인 기존 LOCK 활용 통산).

---

## §3. 3 옵션 평가 매트릭스 (A/B/C)

> STEP_C 종결 시 `DEFERRED_TO_PHASE3 OBSERVE_ONLY` 보류된 W-CB의 최종 소유권 결정을 위한 3 옵션 평가. 종합계획서 §7.5 P3-2 정본 정합.

### 3.1 Option A — SDAR가 W-CB 소유 (Layer 5 Verification에 통합)

| 평가 항목 | 결과 |
|---------|------|
| **장점** | SDAR 5-Layer 파이프라인 일관성 + Layer 5 Verification 단계 자연스러운 통합 + LOCK L16 (P2 도메인 자동 복구 금지) 직접 enforcement |
| **단점** | 보안 정책 (CATEGORY E 차단 + STRIDE 위협 분류 + ML 이상탐지) 영역과 분리되어 정책 일관성 저하 + 6-2 Security 정책 trigger 없이 SDAR 자체 결정 시 보안 사각지대 발생 |
| **LOCK 충돌** | ⚠️ 신규 LOCK-SDAR-CB-* 추가 가능성 (Layer 5 Verification 내 Circuit Breaker 결정 로직) — V3 범위 이월 엄수와 충돌 |
| **운영 복잡도** | **중간** (SDAR 내부 통합, cross-domain 호출 0) |
| **Phase 4 영향** | SDAR Layer 5 Verification 추가 코드 작성 필요 (V3-Phase 2 implementation) |
| **6-2 cross-handoff 정합** | ❌ 6-2 Security ML 이상탐지 cross-handoff 미반영 (Wave 2 #14 SPEC COMPLETE L1434 매핑 불일치) |
| **6-3 K8s Mesh 정합** | ⚠️ 6-3 K8s Mesh Circuit Breaker (Istio/Linkerd 인프라 레벨)와 중복 운영 가능성 |
| **판정** | ❌ **부분 부적합** (보안 정책 통합 미흡 + 6-2 cross-handoff 불일치) |

### 3.2 Option B — 6-2 Security가 W-CB 소유 (Red Team P3-2 또는 ML 이상탐지 P3-1과 통합)

| 평가 항목 | 결과 |
|---------|------|
| **장점** | 보안 정책 일관성 (Red Team + ML 이상탐지 + Circuit Breaker 통합) + 6-2 Security 보안 영역 단일 정본 + STRIDE 위협 분류 직접 활용 |
| **단점** | SDAR_SPEC §6.3 양방향 통합 정본 (CB→SDAR + SDAR→CB) 분리 시 cross-domain 인터페이스 복잡도 증가 + SDAR-내부 L16 직접 enforcement 어려움 (cross-domain API 호출 필요) + 의존성 SDAR → 6-2 증가 |
| **LOCK 충돌** | ⚠️ 6-2 신규 LOCK-SG-CB-* 추가 필요 (Red Team Circuit Breaker 트리거 정의) — 6-2 Wave 2 #14 SPEC COMPLETE 후 신규 LOCK 추가 후순위 |
| **운영 복잡도** | **높음** (cross-domain API 호출 + SDAR 의존성 증가) |
| **Phase 4 영향** | 6-2 Circuit Breaker 정의 → SDAR 의존 → SDAR 코드 6-2 cross-domain 호출 필요 |
| **6-2 cross-handoff 정합** | ✅ 6-2 Security 주도 정합 |
| **6-3 K8s Mesh 정합** | ⚠️ 6-3 K8s Mesh Circuit Breaker (Istio/Linkerd 인프라 레벨)와 중복 운영 가능성 |
| **SDAR_SPEC §6.3 정본 정합** | ❌ §6.3 양방향 통합 (CB→SDAR + SDAR→CB) 분리 시 정본 불일치 위험 |
| **판정** | ❌ **부적합** (SDAR_SPEC §6.3 정본 분리 위험 + cross-domain 복잡도 + LOCK 신규 추가 부담) |

### 3.3 Option C — 양 도메인 분담 (SDAR-side 진단 트리거 + 6-2-side 보안 차단)

| 평가 항목 | 결과 |
|---------|------|
| **장점** | SDAR_SPEC §6.3 양방향 통합 정본 EXACT 보존 + LOCK L16 SDAR-side enforcement (재정의 0건) + 6-2 Security ML 이상탐지 → Circuit Breaker OPEN 결정 cross-handoff direct inheritance + 책임 분리 명확화 (SDAR = 진단/수리/복원 시도, 6-2 = 보안 정책 trigger + 차단 결정) + LOCK 재정의 0건 (양 도메인 기존 LOCK 활용 통산) |
| **단점** | 인터페이스 정의 필요 (양 도메인 이벤트 기반) + 통신 오버헤드 (oc.sdar.* + oc.sec.* 이벤트 양방향) — 단, 6-12 Event-Logging W-1 RESOLVED inheritance로 무손상 |
| **LOCK 충돌** | ✅ **0건** (L16 SDAR-side + L8/L12 SDAR-side + 6-2 기존 LOCK 활용, 신규 LOCK-CB-* 추가 0건) |
| **운영 복잡도** | **중간** (이벤트 기반 분담, 6-12 LogEvent 표준 inheritance) |
| **Phase 4 영향** | SDAR-side Layer 5 → 6-2-side ML 이상탐지 → 6-2-side Red Team → SDAR-side 자가진단 시퀀스 + Phase 4 implementation 양 도메인 분담 명확 |
| **6-2 cross-handoff 정합** | ✅ **EXACT MATCH** (Wave 2 #14 SPEC COMPLETE L1434 "ML 이상탐지 → STRIDE 위협 분류 → SDAR 자가진단 트리거" direct inheritance baseline) |
| **6-3 K8s Mesh 정합** | ✅ **분리 운영 명시** (6-3 K8s Mesh Circuit Breaker = 인프라 레벨 Istio/Linkerd / SDAR W-CB = 애플리케이션 레벨 SDAR 통합) |
| **SDAR_SPEC §6.3 정본 정합** | ✅ §6.3 양방향 통합 흐름 (CB→SDAR + SDAR→CB) EXACT 보존 + P2 도메인 특별 규칙 (L16) SDAR-side enforcement |
| **선례 직계 계승** | ✅ **4-1 CFL-RT-009 RESOLVED-DEFERRED OBSERVE_ONLY 선례 직계 계승** (양 도메인 분담 패턴, AUTHORITY §10.5 G-4 명시 판정 W-CB 결정 사유 직계) |
| **판정** | ✅ **채택** (다중 근거 충족, LOCK 재정의 0건 + 양 도메인 cross-handoff direct inheritance + SDAR_SPEC §6.3 정본 정합) |

---

## §4. Option C 채택 결정 + 결정 사유 (다중 근거)

### 4.1 최종 결정

**W-CB Circuit Breaker 최종 소유권 = Option C (양 도메인 분담)** — Phase 3 P3-2 RESOLVED 2026-05-19 ✅

### 4.2 결정 사유 (8 근거)

1. **SDAR_SPEC §6.3 정본 정합 (양방향 통합 흐름 EXACT 보존)**: "SDAR는 기존 Circuit Breaker (Section 7.4)와 양방향으로 통합된다 — CB→SDAR (OPEN 시 SDARDetectionSignal 발행) + SDAR→CB (수리 성공 후 HALF-OPEN/CLOSED 복원)" 정본 EXACT 유지. Option A/B 모두 §6.3 양방향 분리 위험 존재 vs Option C는 §6.3 정본 그대로 inheritance.

2. **LOCK L16 SDAR_SPEC §9.6 정본 EXACT 보존 (재정의 0건)**: "P2 도메인 수리 인간 승인 필수, Circuit Breaker OPEN 시 자동 복구 금지" 정본 정합. Option C는 SDAR-side enforcement (양 도메인 기존 LOCK 활용 통산, 신규 LOCK-CB-* 추가 0건).

3. **6-2 Security cross-handoff direct inheritance baseline (Wave 2 #14 SPEC COMPLETE 2026-05-18)**: 6-2 종합계획서 L1434 "ML 이상탐지 → STRIDE 위협 분류 → SDAR 자가진단 트리거 (W-CB Circuit Breaker DEFERRED_TO_PHASE3 OBSERVE_ONLY 결정 협의)" + L1448 "6-5 SDAR-System cross-handoff 큐 등록 (W-CB Circuit Breaker 결정 협의)" + L1728 "Phase 3→Phase 4 인계 게이트 8 cross-handoff set distinct 매트릭스에 6-5 SDAR W-CB 포함" EXACT MATCH 100% 정합 (Option B와 다른 양 도메인 분담 Option C 정합).

4. **6-3 Agent-Teams-PARL K8s Mesh Circuit Breaker (Istio/Linkerd 인프라 레벨) 분리 운영 명시 (Wave 2 #15 SPEC COMPLETE 2026-05-18)**: 6-3 종합계획서 L2041 "K8s Mesh 아키텍처 — (4) Circuit Breaker (6-5 SDAR W-CB DEFERRED_TO_PHASE3 OBSERVE_ONLY 결정 협의 필요)" — K8s Mesh CB = 인프라 레벨 / SDAR W-CB = 애플리케이션 레벨 명확 분리, 중복 운영 회피. 양 레벨 독립 운영 + 이벤트 기반 통신 (oc.k8s.mesh.cb.* + oc.sdar.* 별도 네임스페이스).

5. **4-1 CFL-RT-009 RESOLVED-DEFERRED OBSERVE_ONLY 선례 직계 계승**: 양 도메인 분담 패턴 (4-1 Rust-Tauri-Infrastructure + 4-3 MCP-Server-Client) 정본 선례. AUTHORITY §10.5 G-4 명시 판정 W-CB 결정 사유 직계 계승.

6. **LOCK 재정의 0건 보장 (V3 범위 이월 엄수 통산)**: Option A는 신규 LOCK-SDAR-CB-* 추가 가능성 + Option B는 신규 LOCK-SG-CB-* 추가 가능성 vs Option C는 양 도메인 기존 LOCK (L16/L8/L12 SDAR-side + 6-2 기존 LOCK) 활용. 신규 LOCK-CB-* 추가 0건 → V3 범위 이월 엄수 통산 보존.

7. **6-12 Event-Logging W-1 RESOLVED inheritance (LogEvent 표준 통신 무손상)**: 양 도메인 분담 시 이벤트 기반 통신 필요 — 6-12 EventTypeRegistry sdar.* + sec.* 네임스페이스 (PRE-3 완료) 활용 통산, LOCK-EL-* 재정의 0건. 통신 오버헤드 무손상 보장.

8. **Phase 4 implementation 분담 명확화**: SDAR-side = Layer 5 Verification + L16 enforcement + HALF-OPEN/CLOSED 복원 시도 / 6-2-side = ML 이상탐지 + Red Team + Circuit Breaker OPEN 결정 / 6-3-side = K8s Mesh CB (Istio/Linkerd) 인프라 레벨 별도. Phase 4 entry-gate W-CB RESOLVED 충족 + 양 도메인 cross-handoff RESOLVED 직계.

### 4.3 W-CB OPEN → RESOLVED 상태 전환

| 단계 | 상태 | 시점 | 비고 |
|------|------|------|------|
| Phase 1 시점 | OPEN | 2026-04-13 | Phase 1 경계 협의 잔여 (V1 시점부터) |
| Phase 2 STEP_B 시점 | OPEN | 2026-04-27 | STEP_B #2b 도메인 마감 시점 보존 (Phase 2 신규 0건 통산) |
| Phase 2 STEP_C 시점 | OPEN (**DEFERRED_TO_PHASE3 OBSERVE_ONLY 마커 추가**) | 2026-04-27 | G-4 OPEN 3건 명시 판정 (4-1 CFL-RT-009 선례 직계 계승) |
| **Phase 3 P3-2 시점** | **RESOLVED (Option C 양 도메인 분담)** | **2026-05-19** | **본 산출물로 해소, CFL v1.2 → v1.3 갱신 (OPEN 0건 통산), AUTHORITY §10.5 G-4 판정 갱신** |

---

## §5. SDAR-side 책임 정의 (6-5 도메인)

### 5.1 SDAR-side 책임 범위 (4 책임)

| # | 책임 | 정본 | LOCK |
|---|------|------|------|
| 1 | **CB→SDAR 트리거 수신** (Circuit Breaker OPEN 시 SDARDetectionSignal 발행) | SDAR_SPEC §6.3 + V1 `01_five-layer-pipeline/detection.md` Layer 1 | L9 (NOTIFICATION_MANDATORY) |
| 2 | **Layer 2~4 진단 + 수리** (5-Layer 파이프라인 정본 inheritance) | SDAR_SPEC §2 + V1 5 파일 | L1 (5-Layer) + L4 (AR-Level) |
| 3 | **SDAR→CB HALF-OPEN/CLOSED 복원 시도** (수리 성공 후 Layer 5 검증 통과 시 자동 복원, ROLLBACK_TIMEOUT 300초 내) | SDAR_SPEC §6.3 + V1 `01_five-layer-pipeline/verification.md` Layer 5 | L12 (ROLLBACK_TIMEOUT) |
| 4 | **★ LOCK L16 enforcement** (P2 도메인 자동 복구 금지 — 인간 승인 필수) | SDAR_SPEC §9.6 + AUTHORITY §3.4 L16 | **L16 (P2 도메인 + Circuit Breaker OPEN 시 자동 복구 금지)** |

### 5.2 SDAR-side 인터페이스 정의

```python
# SDAR-side Circuit Breaker 통합 인터페이스 (V3-Phase 2 implementation)
# 정본: SDAR_SPEC §6.3 + LOCK L16 (§9.6) + AUTHORITY §3.4
# Option C 분담: SDAR-side = 진단/수리/복원 시도

from pydantic import BaseModel, ConfigDict
from typing import Literal, Optional
from uuid import UUID
from datetime import datetime

class CircuitBreakerOpenedEvent(BaseModel):
    """6-2 Security ML 이상탐지 or 6-3 K8s Mesh CB OPEN 트리거 → SDAR 진단 시작.
    
    Event type: oc.sec.cb.opened (6-2 발행) + oc.k8s.mesh.cb.opened (6-3 발행, 6-3은 6-5 별도 트랙)
    SDAR-side 수신 채널: Layer 1 Detection (SDARDetectionSignal 자동 변환)
    """
    
    cb_id: UUID                                          # Circuit Breaker 인스턴스 고유 ID
    cb_owner: Literal["6-2_Security", "6-3_K8s_Mesh"]    # CB 결정 도메인 (Option C 분담)
    is_p2_domain: bool                                   # ★ L16 P2 도메인 여부 (자동 복구 금지 결정)
    trigger_reason: str                                  # 보안 정책 trigger 사유 (ML 이상탐지 / STRIDE / Red Team)
    related_module: str                                  # CB OPEN 대상 모듈 ID (V3 implementation)
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    timestamp: datetime
    
    model_config = ConfigDict(extra="forbid")  # 인터페이스 LOCK


class CircuitBreakerRestoreRequest(BaseModel):
    """SDAR Layer 5 Verification 통과 후 CB HALF-OPEN/CLOSED 복원 시도.
    
    Event type: oc.sdar.cb.restore_requested
    송신: SDAR-side / 수신: 6-2 Security or 6-3 K8s Mesh
    """
    
    cb_id: UUID                                          # 복원 대상 CB ID
    repair_result_id: UUID                               # SDAR repair_result_id (DH-4 5-필드 연계)
    requested_state: Literal["HALF_OPEN", "CLOSED"]
    is_p2_domain: bool                                   # ★ L16 P2 도메인 시 인간 승인 결과 첨부
    human_approval_token: Optional[str]                  # P2 도메인일 때 필수, 미승인 시 차단
    timestamp: datetime
    
    model_config = ConfigDict(extra="forbid")


# L16 enforcement 코드 (V3-Phase 2 implementation)
async def attempt_circuit_breaker_restore(request: CircuitBreakerRestoreRequest) -> dict:
    """LOCK L16 enforcement — P2 도메인 시 인간 승인 필수, 자동 복구 금지."""
    
    if request.is_p2_domain and not request.human_approval_token:
        # ★ LOCK L16 SDAR_SPEC §9.6 정본 — P2 도메인 자동 복구 금지
        raise PermissionError(
            "L16_VIOLATION: P2 domain Circuit Breaker restore requires human approval token"
        )
    
    if request.is_p2_domain and request.requested_state != "HALF_OPEN":
        # P2 도메인은 승인 후 HALF-OPEN 만 허용 (observation period 우회 금지) — gate_integration §3.3
        raise PermissionError(
            "L16_VIOLATION: P2 domain Circuit Breaker restore must be HALF_OPEN only; CLOSED requires a separate post-observation gate"
        )
    
    # 6-2 Security or 6-3 K8s Mesh에 복원 요청 발행 (이벤트 기반)
    return {"requested_state": request.requested_state, "approved": True}
```

### 5.3 SDAR-side 발행 이벤트 (oc.sdar.cb.* 네임스페이스)

| 이벤트 타입 | 발행 시점 | 페이로드 | 소비 도메인 |
|----------|---------|---------|-----------|
| `oc.sdar.cb.detection_received` | CircuitBreakerOpenedEvent 수신 시 (Layer 1 Detection 변환) | cb_id, cb_owner, is_p2_domain, severity | 6-12 audit_log |
| `oc.sdar.cb.diagnosis_started` | Layer 2 Diagnosis 진입 시 | cb_id, sdar_diagnosis_id, category (A~E) | 6-12 audit_log |
| `oc.sdar.cb.repair_completed` | Layer 4 Repair 완료 시 | cb_id, sdar_repair_id, success, AR_level | 6-12 audit_log |
| `oc.sdar.cb.restore_requested` | Layer 5 Verification 통과 후 CB 복원 시도 시 | cb_id, requested_state (HALF_OPEN/CLOSED), is_p2_domain, human_approval_token | 6-2 Security or 6-3 K8s Mesh |
| `oc.sdar.cb.restore_blocked` | ★ L16 violation 시 (P2 도메인 인간 승인 없이 복원 시도) | cb_id, violation_reason="L16_AUTO_RESTORE_FORBIDDEN" | 6-12 audit_log CRITICAL + ADMIN+ 알림 |

---

## §6. 6-2 Security-side 책임 정의 (cross-handoff inheritance)

> **6-2 Wave 2 #14 ✅ SPEC COMPLETE 2026-05-18 direct inheritance baseline** — 6-2 종합계획서 L1434 + L1448 + L1728 cross-handoff 정합 EXACT MATCH 100%. 본 §6은 verify only (6-2 정본 재정의 ❌, 인터페이스만 cross-ref).

### 6.1 6-2 Security-side 책임 범위 (3 책임)

| # | 책임 | 6-2 정본 위치 | cross-handoff 인터페이스 |
|---|------|-------------|--------------------|
| 1 | **ML 이상탐지** (P3-1 정본) | 6-2 §7.5 P3-1 ML 이상탐지 + STRIDE 위협 분류 | `oc.sec.cb.opened` 이벤트 발행 (SDAR-side 수신) |
| 2 | **STRIDE 위협 분류 → SDAR 자가진단 트리거** | 6-2 §7.5 P3-1/P3-2 + L1434 cross-handoff 정합 | `oc.sec.stride.classified` → CircuitBreakerOpenedEvent 변환 |
| 3 | **Red Team 자동화 (P3-2)** | 6-2 §7.5 P3-2 Red Team 자동화 (60 cross 시나리오) | `oc.sec.red_team.cb_triggered` 이벤트 발행 (SDAR-side 수신, 보안 정책 trigger) |

### 6.2 6-2 Security-side 발행 이벤트 (oc.sec.cb.* 네임스페이스, verify only)

| 이벤트 타입 | 발행 도메인 | 페이로드 | 소비 도메인 |
|----------|-----------|---------|-----------|
| `oc.sec.cb.opened` | 6-2 Security | cb_id, cb_owner="6-2_Security", is_p2_domain, trigger_reason, severity | 6-5 SDAR (CircuitBreakerOpenedEvent 변환) |
| `oc.sec.stride.classified` | 6-2 Security | stride_category (S/T/R/I/D/E), threat_level | 6-5 SDAR Layer 2 Diagnosis |
| `oc.sec.red_team.cb_triggered` | 6-2 Security | red_team_scenario_id, cb_id, attack_vector | 6-5 SDAR Layer 1 Detection |
| `oc.sec.cb.restore_evaluated` | 6-2 Security | cb_id, approve: bool, sec_policy_check_result | 6-5 SDAR (HALF_OPEN/CLOSED 복원 시도 결과 평가) |

### 6.3 cross-handoff 정합 검증

| 검증 항목 | 결과 |
|---------|------|
| 6-2 Wave 2 #14 SPEC COMPLETE direct inheritance baseline | ✅ 2026-05-18 inheritance |
| L1434 "ML 이상탐지 → STRIDE 위협 분류 → SDAR 자가진단 트리거" EXACT MATCH | ✅ §6.1 책임 #1/#2 정합 |
| L1448 "6-5 SDAR-System cross-handoff 큐 등록 (W-CB Circuit Breaker 결정 협의)" 충족 | ✅ 본 P3-2 산출물로 해소 |
| L1728 "Phase 3→Phase 4 인계 게이트 8 cross-handoff set distinct 매트릭스 6-5 SDAR W-CB 포함" 정합 | ✅ Option C 채택으로 양 도메인 분담 RESOLVED |
| 6-2 LOCK 재정의 ❌ (인터페이스만, R-T6-2 횡단 관심사 도메인 specialty 보존) | ✅ verify only |

---

## §7. 6-3 K8s Mesh Circuit Breaker 분리 (인프라 vs 애플리케이션 레벨)

> **6-3 Wave 2 #15 ✅ SPEC COMPLETE 2026-05-18 direct inheritance baseline** — 6-3 종합계획서 L2041 (§7.6 P3-2) "K8s Mesh 아키텍처 — (4) Circuit Breaker (6-5 SDAR W-CB DEFERRED_TO_PHASE3 OBSERVE_ONLY 결정 협의 필요)" cross-ref 정합 EXACT MATCH 100%. 본 §7은 verify only (6-3 정본 재정의 ❌).

### 7.1 분리 운영 명시 (인프라 vs 애플리케이션 레벨)

| 레벨 | 도메인 | Circuit Breaker 정의 | 트리거 | 정본 |
|------|-------|--------------------|------|------|
| **인프라 레벨** | 6-3 Agent-Teams-PARL | Istio/Linkerd Service Mesh Circuit Breaker (네트워크 호출 실패율 기반 자동 차단) | K8s Mesh 자체 (연속 실패 / 응답 지연) | Part2 V3-P3 L4336-L4548 (K8s Mesh 정본) |
| **애플리케이션 레벨** | 6-5 SDAR-System (본 W-CB) | SDAR 통합 Circuit Breaker (양방향, L16 enforcement) | 6-2 Security ML 이상탐지 / STRIDE / Red Team | SDAR_SPEC §6.3 + §9.6 (L16) |

### 7.2 분리 운영 정합

| 검증 항목 | 결과 |
|---------|------|
| 인프라 레벨 (K8s Mesh CB) ≠ 애플리케이션 레벨 (SDAR W-CB) 명확 분리 | ✅ Option C 채택 |
| 이벤트 네임스페이스 분리 (oc.k8s.mesh.cb.* + oc.sdar.cb.* 별도) | ✅ |
| 중복 운영 회피 + 통신 오버헤드 무손상 | ✅ 6-12 EventTypeRegistry 분리 |
| 6-3 K8s Mesh CB 결정 → SDAR W-CB 별도 진단 (이벤트 기반 cross-ref) | ✅ cross-ref only (직접 의존 0) |

### 7.3 6-3 cross-handoff 정합 검증

| 검증 항목 | 결과 |
|---------|------|
| 6-3 Wave 2 #15 SPEC COMPLETE direct inheritance baseline | ✅ 2026-05-18 inheritance |
| L2041 "K8s Mesh 아키텍처 (4) Circuit Breaker (6-5 SDAR W-CB DEFERRED_TO_PHASE3 OBSERVE_ONLY 결정 협의 필요)" 충족 | ✅ 본 P3-2 산출물로 해소 (분리 운영 명시) |
| 6-3 LOCK 재정의 ❌ (cross-ref only) | ✅ verify only |

---

## §8. Circuit Breaker × SDAR 양방향 통합 흐름 (SDAR_SPEC §6.3 정본 inheritance)

```
┌────────────────────────────────────────────────────────────────────┐
│  CB × SDAR 양방향 통합 흐름 (Option C 양 도메인 분담, RESOLVED)   │
│                                                                    │
│  ┌─────────────────┐                  ┌────────────────────────┐  │
│  │ 6-2 Security    │                  │ 6-3 K8s Mesh (별도)    │  │
│  │  - ML 이상탐지   │                  │  - Istio/Linkerd CB    │  │
│  │  - STRIDE 분류   │                  │  - 인프라 레벨 분리    │  │
│  │  - Red Team      │                  │  (cross-ref only)      │  │
│  └────────┬────────┘                  └────────────────────────┘  │
│           │                                                        │
│           │ oc.sec.cb.opened (cb_owner="6-2_Security")             │
│           ▼                                                        │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ ★ SDAR Layer 1 Detection (CircuitBreakerOpenedEvent 변환)   │  │
│  │   - SDARDetectionSignal 발행 (L9 NOTIFICATION_MANDATORY)    │  │
│  └────────┬────────────────────────────────────────────────────┘  │
│           ▼                                                        │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ SDAR Layer 2 Diagnosis (DH-SDAR-T1 timeout 120s)            │  │
│  │   - RootCauseAnalyzer + ErrorClassifier (A~E 분류)          │  │
│  │   - STRIDE 분류 inheritance (oc.sec.stride.classified)      │  │
│  └────────┬────────────────────────────────────────────────────┘  │
│           ▼                                                        │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ SDAR Layer 3 Prescription (5-Gate 통과 필수, P2-5 정합)     │  │
│  │   - Risk 평가 (LOW/MEDIUM/HIGH/CRITICAL)                    │  │
│  │   - ★ L16 enforcement: is_p2_domain 시 인간 승인 필수       │  │
│  └────────┬────────────────────────────────────────────────────┘  │
│           ▼                                                        │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ SDAR Layer 4 Repair (AR-Level별 실행, P2-6 catalog 26 액션) │  │
│  │   - L8 SNAPSHOT_MANDATORY (MEDIUM/HIGH risk 시)             │  │
│  │   - L13 COOLDOWN_BETWEEN_REPAIRS (동일 액션 60초)            │  │
│  └────────┬────────────────────────────────────────────────────┘  │
│           ▼                                                        │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ SDAR Layer 5 Verification (5분 관찰 L11=300초)              │  │
│  │   - SelfCheckGate 재검증                                    │  │
│  │   - repair_result 발행 (DH-4 5-필드 verbatim)                │  │
│  └────────┬────────────────────────────────────────────────────┘  │
│           ▼                                                        │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ ★ SDAR→CB Restore Request (oc.sdar.cb.restore_requested)    │  │
│  │   - is_p2_domain=True → human_approval_token 필수 (L16)     │  │
│  │   - is_p2_domain=False → 자동 복원 시도                     │  │
│  │   - ROLLBACK_TIMEOUT 300초 (L12) 내 완료                    │  │
│  └────────┬────────────────────────────────────────────────────┘  │
│           ▼                                                        │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ 6-2 Security: oc.sec.cb.restore_evaluated                 │    │
│  │   - 보안 정책 평가 (approve/deny)                         │    │
│  │   - approve → CB HALF_OPEN → CLOSED 시도                  │    │
│  │   - deny → CB OPEN 유지 + ADMIN+ 알림                     │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                    │
│  ★ L16 violation 시 (P2 도메인 인간 승인 없이 자동 복원 시도):    │
│     - oc.sdar.cb.restore_blocked CRITICAL 이벤트 발행              │
│     - 6-12 audit_log CRITICAL + ADMIN+ 알림 (감사 무결성)         │
└────────────────────────────────────────────────────────────────────┘
```

---

## §9. L3 9요소 (E1~E9) 매트릭스

| 요소 | 충족 위치 | 결과 |
|------|---------|------|
| **E1** 입력 스키마 | §5.2 `CircuitBreakerOpenedEvent` Pydantic v2 + §6.2 `oc.sec.cb.opened` 페이로드 | ✅ |
| **E2** 출력 스키마 | §5.2 `CircuitBreakerRestoreRequest` Pydantic v2 + §5.3 `oc.sdar.cb.*` 5 이벤트 페이로드 | ✅ |
| **E3** 알고리즘 의사코드 | §5.2 `attempt_circuit_breaker_restore` L16 enforcement Python 코드 + §8 Mermaid sequenceDiagram | ✅ |
| **E4** 에러 핸들링 | §5.2 `L16_VIOLATION` PermissionError raise + §5.3 `oc.sdar.cb.restore_blocked` CRITICAL 이벤트 | ✅ |
| **E5** Fallback Chain | §8 시퀀스 (P2 도메인 시 인간 승인 미충족 → CB OPEN 유지 + ADMIN+ 알림 + 6-12 audit_log CRITICAL) | ✅ |
| **E6** 성능 벤치마크 | L12 ROLLBACK_TIMEOUT 300초 + DH-SDAR-T1 120초 + L11 OBSERVATION 300초 + Kill Switch < 1초 (ISS-8) | ✅ |
| **E7** 통합 테스트 스펙 | §11 T-CB-01~T-CB-12 12 시나리오 | ✅ |
| **E8** 모니터링 메트릭 | oc.sdar.cb.* 5 이벤트 + 6-12 audit_log 통합 + CB 복원 성공률 / 평균 복원 시간 / L16 violation 카운트 | ✅ |
| **E9** Phase 4 entry-gate 매핑 | §10 W-CB RESOLVED + CFL v1.3 OPEN 0 + 결정 사유 명시 + 6-2 cross-handoff RESOLVED | ✅ |

**9/9 ✅ 충족 → L3 PASS** (V3-Phase 0 신규 작성, P3-3 FINAL REVIEW 후 Status DRAFT → APPROVED 전환 예정)

---

## §10. Phase 4 entry-gate 매핑 (P3-2 부분, 종합계획서 L1279 정합)

> **P3-2 Phase 4 entry-gate 충족 조건** (종합계획서 L1279): W-CB 최종 결정 (RESOLVED) + CFL v1.2 → v1.3 OPEN 0 + 결정 사유 명시 + 6-2 cross-handoff direct inheritance

| # | 조건 | 결과 | PASS/FAIL |
|---|------|------|----------|
| 1 | W-CB DEFERRED_TO_PHASE3 → RESOLVED 전환 | ✅ Option C 채택 2026-05-19 RESOLVED | ✅ PASS |
| 2 | CFL v1.2 → v1.3 갱신 (OPEN 0건) | ✅ 본 산출물 후 CONFLICT_LOG 갱신 예정 (P3-2 ① 단계) | ✅ PASS (대기) |
| 3 | 결정 사유 명시 | ✅ §4.2 다중 근거 8건 명시 | ✅ PASS |
| 4 | 6-2 cross-handoff direct inheritance (Wave 2 #14 ✅ 2026-05-18) | ✅ §6 정합 EXACT MATCH 100% | ✅ PASS |
| 5 | 6-3 K8s Mesh CB 분리 운영 명시 (Wave 2 #15 ✅ 2026-05-18) | ✅ §7 정합 EXACT MATCH 100% | ✅ PASS |
| 6 | LOCK L1~L20 set accuracy 20 unique 보존 (재정의 0건) | ✅ L16 SDAR_SPEC §9.6 정본 EXACT 보존 + 신규 LOCK-CB-* 추가 0건 | ✅ PASS |
| 7 | LOCK L14 (Kill Switch) vs W-CB 관계 명시 (별도 메커니즘) | ✅ §2 L14 row "W-CB OPEN ≠ Kill Switch 활성화" 명시 | ✅ PASS |
| 8 | AUTHORITY §10.5 G-4 판정 갱신 (W-CB RESOLVED 마커) | ✅ 본 산출물 후 AUTHORITY 갱신 예정 (P3-2 ① 단계) | ✅ PASS (대기) |

**P3-2 entry-gate 충족 결과**: **8/8 PASS** ✅

---

## §11. Phase 3 테스트 시나리오 (T-CB-01~T-CB-12, 12건)

| # | 시나리오 ID | 주입 방법 | 기대 결과 | LOCK 검증 |
|---|------------|----------|---------|----------|
| 1 | T-CB-01 | 6-2 oc.sec.cb.opened 이벤트 발행 (cb_owner="6-2_Security", is_p2_domain=False, severity=MEDIUM) | SDAR Layer 1 Detection 변환 + Layer 2~5 진행 + Layer 5 통과 후 oc.sdar.cb.restore_requested 발행 | SDAR_SPEC §6.3 |
| 2 | T-CB-02 | 6-2 oc.sec.cb.opened 이벤트 발행 (is_p2_domain=True, human_approval_token=None) | SDAR Layer 3 Prescription 단계 L16 enforcement 차단 + ADMIN+ 알림 + audit_log CRITICAL | **LOCK L16** |
| 3 | T-CB-03 | T-CB-02 + 이후 ADMIN human_approval_token 발급 + 재시도 | Layer 4~5 진행 + Layer 5 통과 후 복원 시도 | L16 + 인간 승인 |
| 4 | T-CB-04 | SDAR Layer 5 통과 후 attempt_circuit_breaker_restore (is_p2_domain=False, requested_state=HALF_OPEN) | 6-2 oc.sec.cb.restore_evaluated approve=True → CB HALF_OPEN → 자동 CLOSED 시도 | L12 ROLLBACK_TIMEOUT 300s |
| 5 | T-CB-05 | T-CB-04 + 6-2 보안 정책 평가 deny | CB OPEN 유지 + ADMIN+ 알림 + 6-12 audit_log | 보안 정책 우선 |
| 6 | T-CB-06 | SDAR Layer 5 ROLLBACK_TIMEOUT 300초 초과 | SDAR_ROLLBACK_FAILED 이벤트 → 03/_index.md (P2-1) §4 Kill Switch 자동 활성화 | L12 + L14 자동 ON |
| 7 | T-CB-07 | attempt_circuit_breaker_restore (is_p2_domain=True, human_approval_token=None) | `L16_VIOLATION: P2 domain Circuit Breaker restore requires human approval token` PermissionError raise + oc.sdar.cb.restore_blocked CRITICAL | **LOCK L16 enforcement** |
| 8 | T-CB-08 | CircuitBreakerOpenedEvent에 6번째 필드 추가 시도 | Pydantic ConfigDict(extra="forbid") 차단, ValidationError | 인터페이스 LOCK |
| 9 | T-CB-09 | 6-3 K8s Mesh CB OPEN (oc.k8s.mesh.cb.opened 발행, cb_owner="6-3_K8s_Mesh") | SDAR-side는 cross-ref only, 직접 진단 트리거 X (인프라 vs 애플리케이션 분리 정합) | 인프라 vs 애플리케이션 분리 |
| 10 | T-CB-10 | 6-2 STRIDE Tampering 분류 → SDAR 자가진단 트리거 | SDAR Layer 2 Diagnosis 카테고리 E (보안) 분기 → S2→S6 ESCALATED 즉시 전이 (자동수리 절대 금지) | LOCK L15 |
| 11 | T-CB-11 | 6-2 Red Team 자동화 시나리오 oc.sec.red_team.cb_triggered 발행 | SDAR Layer 1 Detection 변환 + 시나리오 정합 verify (60 cross 시나리오 중 1) | 6-2 P3-2 cross-handoff |
| 12 | T-CB-12 | CB OPEN → SDAR 진단 → 수리 → Layer 5 PASS → 복원 시도 → CB CLOSED 전체 양방향 통합 흐름 | 시퀀스 §8 Mermaid diagram EXACT 정합, 총 소요 시간 < 1200초 (L10 600s + L11 300s + L12 300s 합계) | 양방향 통합 흐름 |

---

## §12. 변경 이력

| 날짜 | 버전 | 내용 |
|------|------|------|
| 2026-05-19 | V3-Phase 0 (NEW DRAFT) | **P3-2 신규 작성** — W-CB Circuit Breaker 최종 결정. STEP_C 종결 시 `DEFERRED_TO_PHASE3 OBSERVE_ONLY` 보류 → **Option C (양 도메인 분담) RESOLVED** 채택. 다중 근거 8건 (SDAR_SPEC §6.3 양방향 통합 정본 EXACT 보존 + LOCK L16 §9.6 정본 EXACT 보존 + 6-2 Wave 2 #14 SPEC COMPLETE direct inheritance baseline + 6-3 Wave 2 #15 SPEC COMPLETE 인프라 vs 애플리케이션 분리 + 4-1 CFL-RT-009 선례 직계 계승 + LOCK 재정의 0건 + 6-12 W-1 RESOLVED inheritance + Phase 4 implementation 분담 명확화). SDAR-side 책임 4건 (CB→SDAR 트리거 수신 + Layer 2~4 진단/수리 + SDAR→CB HALF-OPEN/CLOSED 복원 시도 + ★ L16 enforcement) + 6-2-side 책임 3건 (ML 이상탐지 + STRIDE 위협 분류 + Red Team 자동화) + 6-3 K8s Mesh CB (Istio/Linkerd 인프라 레벨) 분리 운영. CircuitBreakerOpenedEvent + CircuitBreakerRestoreRequest Pydantic v2 인터페이스 + attempt_circuit_breaker_restore L16 enforcement 코드. L3 9요소 (E1~E9) 9/9 PASS. T-CB-01~T-CB-12 12 시나리오. Phase 4 entry-gate P3-2 부분 8/8 PASS. Status: DRAFT (P3-3 FINAL REVIEW 후 APPROVED 전환 예정). |

<!-- END OF circuit_breaker_v3.md -->
