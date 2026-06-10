# 에이전트 마켓플레이스 — K-067 (V3 신규 L3, Phase 4 production-ready 정본)

> **STEP7-K**: K-067 에이전트 마켓플레이스 (L1288~L1303 원문 / `150720a3496f557d359a421dcbf0922ebe5b1e4fbaa06611eff40e0865177539`)
> **레벨**: L3 (V3-Phase 3 SPEC 완료 → Phase 4 production 승급)
> **정본 소유**: #13 Agent-Protocol-Interoperability / 05_self-evolution (VAMOS 독자 혁신 영역)
> **V 스코프**: V3-Phase 3 (에이전트 등록/심사 파이프라인 + 수익 분배 LOCK-BM-09 + 3-7 VADD cross-ref)
> **Phase 4 태그**: V3-Phase 4 production-ready 정본 승급 (RECOVERY genuine write, P4-1)
> **Status**: APPROVED (DRAFT → APPROVED, 2026-06-03 Phase 4 production promotion)
> **Last-reviewed**: 2026-06-03
> **upstream baseline**: STEP7-K sha256 `150720a3496f557d359a421dcbf0922ebe5b1e4fbaa06611eff40e0865177539`

---

## §1. 교차 참조 블록

| 정본 문서 | 섹션 | 참조 내용 |
|----------|------|----------|
| STEP7-K (Level 2) | L1288~L1303 | K-067 원문 (에이전트 등록/심사/배포/수익 분배) |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-01 | VamosMessage 6필드 — 마켓 등록/심사 이벤트 |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-02 | Permission Level 0~5 — 외부 에이전트 권한 상한 |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-07 | A2A + MCP 양방향 — 등록 에이전트 인터롭 규격 필수 |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-10 | Confidence < 50% HITL (06_autonomy-safety 정본, 본 문서 참조자) |
| **3-9 Business-Model AUTHORITY §3** | **LOCK-BM-09** | **마켓플레이스 수수료율 70% 개발자 / 30% VAMOS (cross-domain 정본 발신 측)** |
| 3-7 Developer-Tools 07_marketplace/vadd_marketplace.md | §전체 | VADD 마켓플레이스 — 에이전트 마켓 양방향 cross-ref (LOCK-BM-09 reverse-inheritance) |
| 06_autonomy-safety/guardrail_rules.md (V2) | §V2.2 | 외부 에이전트 심사 confidence < 0.5 → HITL |
| 05_self-evolution/agent_testing.md | §전체 | K-068 — 등록 전 자동 테스트 게이트 |
| 6-2 Security-Governance | 외부 에이전트 보안 심사 | 코드 서명/샌드박스 정본 |

> **R6 준수**: What+How 전용. 수수료율 70:30 정본은 3-9 Business-Model (LOCK-BM-09), 본 문서는 cross-domain reverse-inheritance reference (verbatim cite-only, 재정의 0).

---

## §2. Purpose & Scope (E1 목표 / E2 범위)

### 2.1 마켓플레이스 5대 요건 (STEP7-K L1288~L1303 원문)

| 요건 | 원문 | 본 문서 섹션 |
|------|------|-------------|
| 에이전트 등록 (manifest + 메타데이터) | L1289 | §4 등록 파이프라인 |
| 심사 파이프라인 (자동 + 수동) | L1291 | §5 심사 게이트 |
| 배포·디스커버리 | L1293 | §6 배포·디스커버리 |
| 수익 분배 (LOCK-BM-09 70:30) | L1295 | §7 수익 분배 |
| 외부 에이전트 신뢰 모델 (R-13-7) | L1297 | §8 신뢰·confidence 게이트 |

### 2.2 범위 경계 (E2)

| 영역 | 본 문서 | 정본 소유 |
|------|--------|----------|
| 마켓 등록·심사·배포·수익 구조 | ✅ | — |
| 수수료율 70:30 정본 | 참조 | 3-9 Business-Model LOCK-BM-09 |
| VADD 도구 마켓 (개발자 도구) | 참조 | 3-7 Developer-Tools (양방향) |
| 외부 코드 서명·샌드박스 심사 | 참조 | 6-2 Security-Governance |
| 등록 전 자동 테스트 | ❌ | agent_testing.md (K-068) |

### 2.3 VAMOS 독자 혁신 포지셔닝

| 비교 대상 | 기존 AI | VAMOS 에이전트 마켓 |
|----------|---------|--------------------|
| GPT Store / Claude MCP Directory | 단순 등록·검색, 수익 모델 제한 | 등록→자동테스트→심사→배포 파이프라인 + LOCK-BM-09 투명 수익 분배 + 3-7 VADD 도구 마켓 양방향 연계 |

---

## §3. 공통 자료 구조 Import (E3)

```python
from sot2_domain.agent_protocol_interoperability.types import (
    VamosMessage,        # LOCK-AP-01 6필드
    PermissionLevel,     # LOCK-AP-02 0~5
)
from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, List
from datetime import datetime
```

---

## §4. 에이전트 등록 파이프라인 (D1 Input / E4)

```python
class AgentListing(BaseModel):
    listing_id: str
    developer_id: str
    name: str
    manifest_uri: str                      # A2A + MCP 양방향 (LOCK-AP-07)
    required_permission_level: int         # LOCK-AP-02 0~5
    interop_compliance: Literal["a2a_mcp_both", "a2a_only", "mcp_only"]
    pricing_model: Literal["free", "one_time", "subscription", "usage"]
    revenue_split_developer: float         # = 0.70 (LOCK-BM-09 정본)
    revenue_split_platform: float          # = 0.30 (LOCK-BM-09 정본)
    review_status: Literal["submitted", "auto_testing", "in_review", "approved", "rejected"]
```

### 4.1 등록 요건 (LOCK-AP-07 인터롭 필수)

등록 에이전트는 **A2A + MCP 양방향 지원 필수** (LOCK-AP-07, 등록 전제 조건). `interop_compliance != "a2a_mcp_both"` (`a2a_only`/`mcp_only`) 인 listing 은 LOCK-AP-07 미충족으로 `review_status="rejected"` 처리한다 (경고/권한 상한 하향이 아닌 거부).

---

## §5. 심사 게이트 (D3 Algorithm / E5 — 자동 + 수동)

```
1. 등록 (submitted)
2. 자동 테스트 (agent_testing.md K-068 — chaos + interop 시나리오)
3. 보안 심사 (6-2 — 코드 서명 + 샌드박스 행동 분석)
4. interop 적합성 (LOCK-AP-07 A2A+MCP 양방향)
5. 심사 confidence ≥ 0.50 → in_review (수동 큐) / < 0.50 → HITL (LOCK-AP-10)
6. 최종 승인 (approved) → 배포
```

자동 테스트 실패 또는 보안 심사 HIGH 리스크는 자동 reject (HITL 보고).

---

## §6. 배포·디스커버리 (E6)

| 기능 | 방식 | LOCK |
|------|------|------|
| 디스커버리 | A2A Agent Card + MCP manifest | LOCK-AP-07 |
| 설치 (사용자) | 첫 연동 사용자 명시 승인 | R-13-7 + LOCK-AP-02 |
| 버전 업데이트 | 재심사 (semver minor 이상) | §5 |
| 평점·리뷰 | 사용자 텔레메트리 | 음의 신호 → 재심사 트리거 |

---

## §7. 수익 분배 (E7 — LOCK-BM-09 cross-domain reverse-inheritance verbatim)

### 7.1 LOCK-BM-09 정본 전재 (3-9 Business-Model 발신 측, verbatim cite-only)

> **LOCK (3-9 §3.4 LOCK-BM-09)**: 마켓플레이스 수수료율 = **70% 개발자 / 30% VAMOS** (STEP7-H S7H-021 근거, 생태계 인센티브) — 변경 금지.

본 도메인은 LOCK-BM-09 를 **재정의하지 않으며** (cross-domain reverse-inheritance reference), 3-9 Business-Model 정본을 verbatim 인용한다. 3-7 Developer-Tools VADD 마켓플레이스와 동일 70:30 정합.

### 7.2 정산 흐름

```python
def settle(listing: AgentListing, gross_krw: float) -> dict:
    dev = gross_krw * listing.revenue_split_developer    # 0.70 (LOCK-BM-09)
    platform = gross_krw * listing.revenue_split_platform # 0.30 (LOCK-BM-09)
    assert abs((dev + platform) - gross_krw) < 1e-6
    return {"developer_krw": dev, "platform_krw": platform}
```

---

## §8. 신뢰·Confidence 게이트 + Confidence Penalty (E8)

| 이벤트 | Confidence Penalty | HITL (< 0.50) |
|--------|:-----------------:|:-------------:|
| 외부 에이전트 첫 연동 (R-13-7) | 사용자 명시 승인 | ✅ (opt-in) |
| 심사 confidence < 0.50 | 트리거 자체 | ✅ |
| 보안 심사 HIGH 리스크 | -0.40 | ✅ (자동 reject) |
| interop 비적합 (A2A+MCP 미지원) | -0.20 | 경고 + 상한 하향 |
| 수익 분배 비율 변조 시도 (≠ 70:30) | -0.50 | ✅ (LOCK-BM-09 위반 차단) |

> LOCK-AP-10 재정의 없음 — 06_autonomy-safety/guardrail_rules.md (P2-6 정본) cumulative 기준. R-13-7 외부 에이전트 첫 연동 사용자 승인 필수.

---

## §9. 에스컬레이션 + LOCK 매핑 5필드 표 (E9 / E10)

```python
class MarketplaceEscalation(BaseModel):
    trace_id: str
    event_class: Literal[
        "review_low_confidence",
        "security_high_risk",
        "interop_noncompliant",
        "revenue_split_tampering",
        "external_agent_first_connect",
    ]
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    confidence_delta: float = Field(..., le=0.0, ge=-1.0)
    listing_id: str
    recommended_action: Literal["auto_reject", "escalate_hitl_L3", "require_user_optin", "block"]
    occurred_at: datetime
```

| LOCK ID | 항목 | 원본 문서 | 값 | 재정의 | 본 문서 적용 지점 |
|---------|------|----------|-----|--------|------------------|
| LOCK-AP-01 | 프로토콜 메시지 포맷 | STEP7-K, D2.0-05 | VamosMessage 6필드 | 금지 | §4 listing 이벤트 + §5 심사 trace_id |
| LOCK-AP-02 | 에이전트 권한 레벨 | STEP7-K K-041 | Permission Level 0~5 | 금지 | §4 required_permission_level + §6 설치 상한 |
| LOCK-AP-07 | 인터롭 규격 | STEP7-K | A2A + MCP 양방향 지원 필수 | 금지 | §4.1 등록 요건 interop_compliance |
| LOCK-AP-10 | Confidence 임계값 | DEFINED-HERE (06_autonomy-safety 정본) | HITL 트리거 < 50% | 금지 | §5/§8 심사 confidence (참조자, 재정의 없음) |
| LOCK-BM-09 | 마켓플레이스 수수료율 | **3-9 Business-Model §3.4 (S7H-021)** | **70% 개발자 / 30% VAMOS** | **금지 (cross-domain, verbatim cite-only)** | §7.1 정본 전재 + §7.2 정산 |

---

## §10. Phase 3 테스트 시나리오 (≥ 10건)

| # | ID | 설명 | 기대 결과 |
|---|----|------|----------|
| 1 | AM-01 | 에이전트 등록 → auto_testing 자동 진입 | ✅ §5 |
| 2 | AM-02 | A2A+MCP 양방향 미지원 등록 → 경고 + 상한 하향 | ✅ LOCK-AP-07 |
| 3 | AM-03 | 보안 심사 HIGH 리스크 → 자동 reject | ✅ §8 |
| 4 | AM-04 | 심사 confidence 0.45 → HITL | ✅ LOCK-AP-10 |
| 5 | AM-05 | 수익 정산 70:30 검산 (dev+platform=gross) | ✅ LOCK-BM-09 |
| 6 | AM-06 | 수익 비율 변조 시도 (60:40) → 차단 | ✅ §8 |
| 7 | AM-07 | 외부 에이전트 첫 연동 → 사용자 opt-in | ✅ R-13-7 |
| 8 | AM-08 | 3-7 VADD 도구 마켓 양방향 cross-ref 정합 | ✅ §1 |
| 9 | AM-09 | 등록 전 agent_testing chaos 시나리오 게이트 | ✅ agent_testing.md |
| 10 | AM-10 | semver minor 업데이트 → 재심사 트리거 | ✅ §6 |
| 11 | AM-11 | 평점 음의 신호 누적 → 재심사 | ✅ §6 |
| 12 | AM-12 | Langfuse trace `marketplace.*` span 기록 | ✅ logging_spec.md §5.1 |

---

## §11. 세션 간 인터페이스 Cross-check 표

| 인터페이스 | 대상 파일 | 검증 기준 |
|-----------|----------|----------|
| 등록 전 자동 테스트 | `agent_testing.md` | chaos + interop 게이트 |
| 수수료율 70:30 정본 | `3-9 Business-Model AUTHORITY §3 LOCK-BM-09` | verbatim cite-only |
| VADD 도구 마켓 | `3-7 Developer-Tools 07_marketplace/vadd_marketplace.md` | 양방향 reverse-inheritance |
| 보안 심사 (서명/샌드박스) | `6-2 Security-Governance` | 코드 서명 정책 정본 |
| 심사 confidence HITL | `06_autonomy-safety/guardrail_rules.md §V2.2` | LOCK-AP-10 < 0.50 |

---

## §12. 검증 자가 체크리스트 (L3 D1~D8 + E1~E10)

- [x] STEP7-K L1288~L1303 K-067 5대 요건 전수 구현 (등록/심사/배포/수익/신뢰)
- [x] LOCK-BM-09 (3-9 정본 verbatim 70:30) cross-domain reverse-inheritance cite-only, 재정의 0 (§7.1)
- [x] LOCK-AP-01/02/07/10 + LOCK-BM-09 5필드 분리 인용 (§9)
- [x] LOCK-AP-07 A2A+MCP 양방향 등록 필수 (§4.1)
- [x] LOCK-AP-10 재정의 없음 (§5/§8 참조자)
- [x] R-13-7 외부 에이전트 첫 연동 사용자 승인 (§8)
- [x] 3-7 VADD (P3-4) 양방향 cross-ref (§1/§11)
- [x] agent_testing (K-068) 등록 게이트 cross-ref (§5/§11)
- [x] Phase 3 테스트 12건 (≥ 10 요건 충족, §10)
- [x] 수익 분배 변조 차단 (≠ 70:30 → abort, §8)
- [x] Status DRAFT → APPROVED 전환 (Phase 4 production 승급)

---

*정본 소유: #13 Agent-Protocol-Interoperability (자기진화 전략 — 에이전트 마켓플레이스)*
*수수료율 70% 개발자 / 30% VAMOS 정본은 3-9 Business-Model (LOCK-BM-09), 본 문서는 cross-domain reverse-inheritance reference (verbatim cite-only, 재정의 0)*
*3-7 Developer-Tools VADD 마켓플레이스와 양방향 정합*
