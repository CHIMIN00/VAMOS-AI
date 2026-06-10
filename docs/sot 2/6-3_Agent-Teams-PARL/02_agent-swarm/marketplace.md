# marketplace -- Agent Marketplace 4 컴포넌트 거버넌스 (Registry + Installer + Discovery + Review/Retire)

> **도메인**: 6-3_Agent-Teams-PARL / 02_agent-swarm
> **Part2 출처**: V3-P3 L4336-L4548 (Marketplace 정본) + §6.7 L5096-L5123 (Agent Specialization Protocol + Marketplace 통합)
> **DESIGN 정본**: D2.0-05 §12.19 (Agent Specialization Protocol) + D2.0-07 §3 (Safety) + Part2 V3-P3 (Marketplace 거버넌스)
> **Phase 배정**: Phase 4 P4-3 (V3 implementation production-ready 정본 승급, 2026-05-27)
> **상위 인덱스**: `02_agent-swarm/_index.md` (Swarm 총괄, Phase 0 baseline)
> **AUTHORITY 정본**: `AUTHORITY_CHAIN.md` LOCK-AT-005 (07 Gate 필수) + LOCK-AT-012 (HMAC 서명 필수) + R-63-6 (등록 보안 검증)
> **관련 V3 산출물**: `parl_security.md` §4.3 IsolationPolicy.marketplace.deactivate() (격리 시 비활성화 forward-link)
> **Status**: APPROVED (Phase 4 P4-3 production-ready 정본 승급 완료, 2026-05-27)
> **chain**: phase4_6-3_p4-3_2026-05-27

---

## 1. 목적

본 문서는 V3 Agent Marketplace의 **4 핵심 컴포넌트 (Registry + Installer + Discovery + Review/Retire)** + **AT-005/AT-012 LOCK 정합** + **R-63-6 등록 보안 검증** + **§9.2 L2025 retire vs marketplace 퇴출 분리 운영** + **E2E 시나리오 ≥ 3 (정상 등록 / 서명 위반 / 보안 위반 퇴출)** + **6-2 보안 통합 (LlamaGuard + Zero-Trust + OWASP)** + **3-7 Plugin SDK 경계**를 production-ready 정본으로 확정한다.

본 문서는 §7.5 P3-3 forward-defined 명세 (§7.5 L2066~L2113)를 Phase 4 V3 implementation으로 정본 승급하며, E2E 통합 5 항목 3 "Marketplace 등록/검증" PASS 베이스라인을 영구 확립한다.

## 2. 범위

| 핵심 관심사 | 본 문서 정의 |
|------------|-------------|
| **Registry** | Agent 메타데이터 스키마 + 카탈로그 검색 API + 버전 관리 semver (E1 아키텍처) |
| **Installer** | AT-012 HMAC 서명 검증 + 의존성 그래프 + Docker 샌드박스 + AT-005 Gate + 롤백 (E5 보안) |
| **Discovery** | 키워드 검색 + 카테고리 + capability 매칭 + 추천 (reputation_score) + TOP-N (E4 인터페이스) |
| **Review/Retire** | 사용자 리뷰 + 자동 품질 평가 + 보안 위반 신고 + P0 인간 승인 (E8 운영) |
| **R-63-6** | 등록 시 보안 검증 (HMAC + 07 Gate + P2 분류) 필수 (E5 보안) |
| **§9.2 L2025 분리** | retire (성과 기반 자동 7일) vs marketplace 퇴출 (보안/품질 관리자 판단) 독립 운영 (E2 알고리즘) |
| **E2E 시나리오 ≥ 3** | 정상 등록 / 서명 위반 / 보안 위반 퇴출 (E7 테스트) |

---

## 3. E1 — 4 컴포넌트 아키텍처

```
┌──────────────────────────────────────────────────────────────────────┐
│                     Agent Marketplace V3 (Phase 4)                    │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ ① Registry (메타데이터 + 카탈로그 + 버전 관리)                  │   │
│  │   ├─ Agent 메타데이터 스키마 (id, version, capabilities, sig)  │   │
│  │   ├─ 카탈로그 검색 API (RESTful)                              │   │
│  │   ├─ 버전 관리 semver (major.minor.patch)                     │   │
│  │   └─ 등록 ledger (immutable history)                          │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│                              ▼                                          │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ ② Installer (HMAC + 의존성 + 샌드박스 + Gate + 롤백)             │   │
│  │   ├─ Layer 1: AT-012 HMAC 서명 검증 (변조 감지 시 거부)        │   │
│  │   ├─ Layer 2: 의존성 그래프 해결 (cycle 방지 AT-003)           │   │
│  │   ├─ Layer 3: Docker 샌드박스 설치 (6-2 LOCK L12 정합)         │   │
│  │   ├─ Layer 4: AT-005 07 Gate 통과 강제                        │   │
│  │   └─ Layer 5: 롤백 가능 (checkpoint + revert)                 │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│                              ▼                                          │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ ③ Discovery (검색 + 추천 + TOP-N)                              │   │
│  │   ├─ 키워드 검색 (full-text BM25)                             │   │
│  │   ├─ 카테고리 + capability 매칭 (taxonomy)                    │   │
│  │   ├─ 추천 (사용 빈도 + reputation_score)                      │   │
│  │   └─ TOP-N 필터링 (default N=10)                              │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│                              ▼                                          │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ ④ Review/Retire (리뷰 + 자동 품질 + 보안 위반 + P0 승인)        │   │
│  │   ├─ 사용자 리뷰 (별점 + 코멘트)                              │   │
│  │   ├─ 자동 품질 평가 (오류율 + 응답 시간 + 리소스)             │   │
│  │   ├─ 보안 위반 신고 (red flag → 즉시 검토 큐)                 │   │
│  │   └─ 관리자 판단 (P0 인간 승인 필수)                          │   │
│  │   §9.2 L2025: retire (성과 자동 7일) ≠ marketplace 퇴출       │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ R-63-6 등록 보안 검증 (HMAC + 07 Gate + P2 분류) 필수          │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 4. ① Registry (E1 아키텍처 + E4 인터페이스)

### 4.1 Agent 메타데이터 스키마

```python
@dataclass
class AgentManifest:
    """
    Marketplace Registry에 등록되는 Agent 메타데이터.
    """
    id: str                          # uuid v4 (관리자 발급)
    name: str                        # 사람이 읽을 수 있는 이름
    version: str                     # semver (e.g., "1.2.3")
    capabilities: list[str]          # ["code_gen", "research", "trading_p2"]
    requirements: list[Dependency]   # [(name, version_constraint)]
    signature: str                   # HMAC-SHA256 hex (LOCK-AT-012)
    publisher_id: str                # 발행자 (검증된 OWNER)
    p_level: PrivacyLevel            # P0 / P1 / P2 (자동 분류)
    reputation_score: float          # 0.0 ~ 5.0 (초기 0.0)
    download_count: int              # 사용 통계
    last_updated: datetime
    sbom_url: str                    # Software Bill of Materials
    cosign_signature: str | None     # Sigstore cosign 서명 (옵션)
```

### 4.2 Registry API

```python
class AgentRegistry:
    """V3 Agent Marketplace Registry — 메타데이터 + 카탈로그 + 버전 관리."""

    def register(self, manifest: AgentManifest) -> RegistrationResult:
        """
        R-63-6 보안 검증 강제: HMAC 서명 + 07 Gate + P2 분류 통과 필수.
        """
        # Step 1: AT-012 HMAC 서명 검증
        if not self._verify_hmac(manifest.signature, manifest):
            return RegistrationResult.REJECTED_SIGNATURE_INVALID
        # Step 2: AT-005 07 Gate 통과
        if not gate_check(manifest_to_context(manifest)):
            return RegistrationResult.REJECTED_GATE_FAILED
        # Step 3: P2 분류 자동 검증 (Trading Agent는 P2 + 명시적 승인)
        if manifest.p_level == PrivacyLevel.P2 and not self._has_p2_approval(manifest):
            return RegistrationResult.REJECTED_P2_APPROVAL_REQUIRED
        # Step 4: 6-2 통합 보안 검증 위임 (§7 cross-handoff)
        sec_result = call_security_validation(manifest)
        if not sec_result.passed:
            return RegistrationResult.REJECTED_SECURITY_FAILED
        # Step 5: 등록 ledger append-only
        self._ledger.append(manifest)
        return RegistrationResult.REGISTERED

    def get(self, agent_id: str, version: str | None = None) -> AgentManifest:
        """semver 호환 버전 자동 선택 (version 미지정 시 latest)"""

    def list(self, filters: dict = {}) -> list[AgentManifest]:
        """카탈로그 검색 API (RESTful)"""

    def get_ledger(self) -> list[LedgerEntry]:
        """등록 ledger immutable history"""
```

### 4.3 버전 관리 semver

| 변경 유형 | semver 증가 | 인스톨러 자동 업그레이드 |
|---------|-----------|-------------------|
| Major (호환 깨짐) | 1.x.x → 2.0.0 | ❌ 명시적 사용자 승인 필수 (P0 인간 승인) |
| Minor (기능 추가) | 1.2.x → 1.3.0 | ✅ AT-005 Gate + AT-012 HMAC 통과 시 자동 |
| Patch (버그 fix) | 1.2.3 → 1.2.4 | ✅ AT-005 Gate + AT-012 HMAC 통과 시 자동 |

---

## 5. ② Installer (E5 보안 + E4 인터페이스)

### 5.1 5-Layer 설치 파이프라인

```python
class AgentInstaller:
    """
    V3 Agent Marketplace Installer — 5-Layer 설치 파이프라인.
    LOCK 인용:
    - LOCK-AT-012 (Part2 §6.7 L5050): HMAC 무결성 서명 (Layer 1)
    - LOCK-AT-003 (Part2 §6.7 L5041): 의존성 cycle 방지 (Layer 2)
    - 6-2 LOCK L12: Docker 샌드박스 (Layer 3)
    - LOCK-AT-005 (Part2 §6.7 L5043): 07 Gate 통과 (Layer 4)
    """
    def install(self, agent_id: str, version: str) -> InstallResult:
        manifest = self.registry.get(agent_id, version)

        # Layer 1: AT-012 HMAC 서명 검증
        if not self._verify_hmac(manifest.signature, manifest):
            return InstallResult.REJECTED_SIGNATURE_INVALID

        # Layer 2: 의존성 그래프 해결 (AT-003 cycle 방지)
        deps = self._resolve_dependencies(manifest.requirements)
        if self._has_cycle(deps):
            return InstallResult.REJECTED_DEPENDENCY_CYCLE

        # Layer 3: Docker 샌드박스 설치 (6-2 LOCK L12 정합)
        sandbox = self.sandbox_client.create_quarantine(
            agent_id=agent_id,
            timeout_sec=30,                  # 6-2 LOCK L12 30s
            network="none",                  # 6-2 LOCK L12 --network=none
        )
        try:
            sandbox.install(manifest, deps)
        except SandboxFailure as e:
            return InstallResult.REJECTED_SANDBOX_FAILED

        # Layer 4: AT-005 07 Gate 통과 강제
        gate_token = self.gate.enforce(agent_id, install_context(manifest))
        if not gate_token:
            sandbox.cleanup()
            return InstallResult.REJECTED_GATE_FAILED

        # Layer 5: 활성화 (checkpoint + rollback 가능)
        checkpoint = self._create_checkpoint(agent_id, version)
        try:
            self._activate(agent_id, sandbox, gate_token)
        except ActivationFailure as e:
            self._rollback(checkpoint)
            return InstallResult.ROLLED_BACK

        return InstallResult.INSTALLED

    def uninstall(self, agent_id: str) -> UninstallResult:
        """제거 (격리된 agent의 marketplace 퇴출 시 호출)"""

    def rollback(self, agent_id: str, checkpoint_id: str) -> RollbackResult:
        """Layer 5 checkpoint로 복구"""
```

### 5.2 Docker 샌드박스 설정 (6-2 LOCK L12 정합)

```yaml
# Installer 설치 시 적용되는 Docker 샌드박스 spec
sandbox_spec:
  image: "alpine:3.20"               # 최소 이미지
  network: "none"                    # 6-2 LOCK L12 verbatim
  timeout: "30s"                     # 6-2 LOCK L12 verbatim
  read_only_root_fs: true
  cap_drop: ["ALL"]
  security_opt: ["no-new-privileges:true"]
  cgroup_constraints:
    memory: "256Mi"
    cpu: "0.5"
```

---

## 6. ③ Discovery (E4 인터페이스 + E6 성능)

### 6.1 검색 API

```python
class AgentDiscovery:
    """V3 Agent Marketplace Discovery — 검색 + 추천 + TOP-N."""

    def search(self, query: str,
               category: str | None = None,
               capability: list[str] | None = None,
               top_n: int = 10) -> list[AgentManifest]:
        """
        검색 우선순위:
          1. 키워드 일치 (full-text BM25 + title boost x2)
          2. 카테고리 + capability 매칭
          3. reputation_score (DESC) + download_count (DESC) tie-breaker
        """

    def recommend(self, agent_id: str, top_n: int = 5) -> list[AgentManifest]:
        """현재 설치된 agent와 호환되는 추천 (collaborative filtering)"""

    def categories(self) -> list[Category]:
        """카테고리 taxonomy 전수"""

    def capabilities(self) -> list[str]:
        """등록된 모든 capabilities union"""
```

### 6.2 검색 성능 목표

| 메트릭 | 목표 | 측정 방법 |
|-------|------|----------|
| search latency P50 | < 50 ms (10,000 agents 대상) | Elasticsearch query timer |
| search latency P95 | < 200 ms | Elasticsearch query timer |
| recommend latency | < 100 ms (collaborative filtering) | profile timer |
| 카탈로그 인덱스 갱신 | < 5 sec (등록 후) | indexer log |

---

## 7. ④ Review/Retire (E8 운영 + E2 알고리즘)

### 7.1 사용자 리뷰

```python
@dataclass
class AgentReview:
    agent_id: str
    user_id: str                     # OWNER 인증 필수
    rating: int                      # 1~5
    comment: str
    timestamp: datetime
    verified: bool                   # 실 사용 검증 (download log + 7일 사용)
```

### 7.2 자동 품질 평가 (4 메트릭)

| 메트릭 | 목표 | 알림 임계값 | 대응 |
|-------|------|----------|------|
| 모듈 오류율 | < 1% | > 5% | 등록 비활성화 + 검토 큐 |
| 평균 응답 시간 | < target × 1.5 | > target × 3 | reputation_score -0.5 |
| 리소스 사용률 | < 80% | > 95% | Marketplace 카탈로그 경고 표시 |
| 사용자 평균 별점 | > 3.5 | < 2.0 (10+ reviews) | 검토 큐 |

### 7.3 보안 위반 신고 + P0 인간 승인

```python
class MarketplaceReviewBoard:
    """
    Review/Retire 관리 — 보안 위반 신고 + P0 인간 승인.
    """
    def report_security_violation(self, agent_id: str, reporter_id: str,
                                   evidence: dict) -> ReportResult:
        """
        red flag → 즉시 검토 큐 enqueue + 6-2 cross-handoff Red Team 감사.
        """
        # Step 1: 즉시 Marketplace 카탈로그 일시 비활성화 (회전 가능)
        self.registry.disable(agent_id, reason="security_violation_reported")
        # Step 2: 검토 큐 enqueue (P0 인간 승인 필수)
        self.review_queue.enqueue({
            "type": "security_violation",
            "agent_id": agent_id,
            "reporter_id": reporter_id,
            "evidence": evidence,
        })
        # Step 3: 6-2 Red Team Agent 감사 트리거 (parl_security §6.1 패턴 직계)
        red_team_queue.enqueue({
            "type": "marketplace_security_audit",
            "agent_id": agent_id,
        })
        return ReportResult.QUEUED

    def admin_decision(self, agent_id: str, decision: AdminDecision,
                       admin_id: str) -> DecisionResult:
        """
        P0 인간 승인 필수 — 관리자가 명시적으로 marketplace 퇴출 결정.
        §9.2 L2025: marketplace 퇴출 ≠ Specialization Protocol retire (분리 운영).
        """
        if not is_owner_admin(admin_id):
            raise PermissionError("P0 인간 승인 필수 — OWNER+ADMIN만 가능")
        if decision == AdminDecision.MARKETPLACE_REMOVE:
            self.registry.permanent_remove(agent_id)
            self.installer.uninstall(agent_id)
        return DecisionResult.APPLIED
```

### 7.4 §9.2 L2025 retire vs marketplace 퇴출 분리

> **§9.2 L2025 정본 직계**: retire 판단 = 성과 기반 자동 (7일 관찰) ≠ Marketplace 퇴출 = 보안/품질 위반 관리자 판단 (P0 인간 승인). 독립 운영.

| 차원 | retire (Specialization Protocol) | marketplace 퇴출 (Review/Retire) |
|------|-------------------------------|------------------------------|
| **트리거** | 성과 메트릭 7일 관찰 (자동) | 보안 위반 신고 또는 품질 위반 (수동) |
| **결정자** | 알고리즘 (자동) | P0 인간 (OWNER+ADMIN 승인) |
| **타임라인** | 7일 observation window | 즉시 (긴급 신고 시) |
| **복구 가능** | 자동 재학습 후 reactivate 가능 | 영구 (permanent_remove) |
| **운영 도메인** | P4-4 specialization_protocol.md (forward-defined) | 본 §7 marketplace.md |

---

## 8. E2 — R-63-6 등록 보안 검증

> **R-63-6** (`종합계획서` §4.3): Marketplace 등록 시 보안 검증 (HMAC 서명 + 07 Gate + P2 분류) 필수.

```python
def r_63_6_security_validation(manifest: AgentManifest) -> ValidationResult:
    """
    Marketplace 등록 시 강제 보안 검증 — Registry.register() 진입점에 위치.
    """
    # 1. AT-012 HMAC 서명 검증
    if not verify_hmac(manifest.signature, manifest):
        return ValidationResult.REJECTED_HMAC_INVALID
    # 2. AT-005 07 Gate 통과 강제
    if not gate_check(manifest_to_context(manifest)):
        return ValidationResult.REJECTED_GATE_FAILED
    # 3. P2 분류 자동 검증 (Trading 등 P2 도메인 = OWNER+ADMIN 명시적 승인 필요)
    if manifest.p_level == PrivacyLevel.P2:
        if not has_p2_explicit_approval(manifest):
            return ValidationResult.REJECTED_P2_APPROVAL_REQUIRED
    return ValidationResult.PASSED
```

---

## 9. E7 — E2E 시나리오 ≥ 3 (정상 등록 / 서명 위반 / 보안 위반 퇴출)

### 9.1 E2E-MP-01: 정상 등록 시나리오

```python
def test_e2e_mp_01_normal_registration():
    """정상 Agent 등록 → Registry + Installer + Discovery 정상 동작 검증."""
    manifest = create_valid_manifest(name="ResearchAgent", version="1.0.0")
    # Step 1: 정상 HMAC 서명
    sign_manifest(manifest, key=publisher_key)
    # Step 2: 등록
    result = registry.register(manifest)
    assert result == RegistrationResult.REGISTERED
    # Step 3: 설치
    install_result = installer.install(manifest.id, manifest.version)
    assert install_result == InstallResult.INSTALLED
    # Step 4: 검색 → TOP-N 결과 포함
    search_results = discovery.search("research", top_n=10)
    assert manifest.id in [m.id for m in search_results]
```

### 9.2 E2E-MP-02: 서명 위반 시나리오

```python
def test_e2e_mp_02_signature_violation():
    """잘못된 HMAC 서명 → Registry 등록 거부 (Step 1 차단)."""
    manifest = create_valid_manifest(name="MaliciousAgent", version="1.0.0")
    # 변조된 서명 첨부
    manifest.signature = "invalid_hmac_signature"
    result = registry.register(manifest)
    assert result == RegistrationResult.REJECTED_SIGNATURE_INVALID
    # 카탈로그 미등재 검증
    assert manifest.id not in registry.list()
```

### 9.3 E2E-MP-03: 보안 위반 퇴출 시나리오

```python
def test_e2e_mp_03_security_violation_removal():
    """등록된 Agent 보안 위반 발견 → ReviewBoard → P0 인간 승인 → permanent_remove."""
    # 기 등록된 Agent (E2E-MP-01 패턴)
    agent_id = "agent-uuid-123"
    # 보안 위반 신고
    report = review_board.report_security_violation(
        agent_id=agent_id,
        reporter_id="security-team",
        evidence={"type": "data_exfiltration", "log_ref": "incident-789"},
    )
    assert report == ReportResult.QUEUED
    # 즉시 카탈로그 비활성화 확인
    assert registry.get(agent_id).disabled
    # 6-2 Red Team 감사 발화 검증
    assert red_team_queue.has_pending(agent_id, "marketplace_security_audit")
    # P0 인간 (OWNER+ADMIN) 승인 → permanent_remove
    decision = review_board.admin_decision(
        agent_id=agent_id,
        decision=AdminDecision.MARKETPLACE_REMOVE,
        admin_id="owner-admin-uuid",
    )
    assert decision == DecisionResult.APPLIED
    # Marketplace + Installer 양쪽 제거 확인
    assert agent_id not in registry.list()
    assert not installer.is_installed(agent_id)
```

### 9.4 추가 E2E (보강)

| Test ID | 시나리오 | 검증 |
|---------|---------|------|
| E2E-MP-04 | semver Major 업그레이드 (P0 인간 승인 필수) | 자동 업그레이드 차단 + 명시적 승인 후 진행 |
| E2E-MP-05 | 의존성 cycle 감지 (AT-003) | Installer Layer 2 REJECTED_DEPENDENCY_CYCLE |
| E2E-MP-06 | Docker 샌드박스 실패 (6-2 LOCK L12) | Installer Layer 3 REJECTED_SANDBOX_FAILED |
| E2E-MP-07 | 07 Gate 미통과 (AT-005) | Installer Layer 4 REJECTED_GATE_FAILED |
| E2E-MP-08 | 롤백 (Layer 5 활성화 실패) | checkpoint → ROLLED_BACK |
| E2E-MP-09 | retire vs marketplace 퇴출 분리 (§9.2 L2025) | Specialization retire 자동 ≠ marketplace permanent_remove (P0) |
| E2E-MP-10 | Marketplace 등재 ≥ 5건 staging 부하 | 5건 동시 등록 + 검색 정상 |

---

## 10. E5 — 6-2 Security-Governance cross-handoff (LlamaGuard + Zero-Trust + OWASP 통합)

### 10.1 6-2 통합 보안 검증 인터페이스

```python
def call_security_validation(manifest: AgentManifest) -> SecurityValidationResult:
    """
    6-2 Security-Governance 통합 검증 — Registry.register() Step 4 위임.
    """
    # 6-2 P2-2 LlamaGuard L2 출력 검증 (Marketplace 메타데이터)
    if not llamaguard_validate(manifest.description, manifest.capabilities):
        return SecurityValidationResult.REJECTED_LLAMAGUARD
    # 6-2 P2-4 Zero-Trust STRIDE 매트릭스 검증 (84 매트릭스 직계)
    stride_result = zero_trust_stride_validate(manifest)
    if stride_result.has_high_severity():
        return SecurityValidationResult.REJECTED_ZERO_TRUST
    # 6-2 P2-5 OWASP V2.6 검증 (Top 10 위반 사항)
    owasp_result = owasp_validate(manifest.sbom_url)
    if owasp_result.has_critical():
        return SecurityValidationResult.REJECTED_OWASP
    return SecurityValidationResult.PASSED
```

### 10.2 6-2 cross-handoff 분담

| 6-2 검증 | 6-3 Marketplace 통합 위치 | 6-2 정본 문서 |
|--------|---------------------|-------------|
| LlamaGuard L2 출력 | Step 4 호출 | 6-2 `01_ai-code-security/llamaguard_integration.md` |
| Zero-Trust STRIDE 84 매트릭스 | Step 4 호출 | 6-2 `03_stride-threat-model/zero_trust_stride_v2.md` |
| OWASP V2.6 Top 10 | Step 4 호출 | 6-2 `04_owasp-llm-top10/owasp_v2_review.md` |
| Red Team 감사 (위반 신고 시) | §7.3 report_security_violation | 6-2 P4-2 `red_team_automation_v3.md` |

---

## 11. E5 — 3-7 Developer-Tools-API-SDK cross-handoff (Plugin SDK 경계)

| 경계 | 3-7 Plugin SDK 정본 | 6-3 Marketplace 위치 |
|------|----------------|-----------------|
| Plugin 메타데이터 스키마 정의 | 3-7 정본 (편집 ❌) | Registry §4.1 AgentManifest는 Plugin 스키마 확장 |
| Plugin 인증 (publisher_id 검증) | 3-7 정본 (편집 ❌) | Registry §4.2 register() publisher 검증 |
| Plugin 설치 (Marketplace 인스톨러) | 6-3 본 §5 Installer | 3-7 Plugin Slot 호출 시 Marketplace.install() 위임 |
| Plugin Hot-Reload | 3-7 정본 (편집 ❌) | Marketplace는 활성화/비활성화만 (Hot-Reload는 3-7 측) |

---

## 12. LOCK-AT 매트릭스

| LOCK-AT | 항목 | 본 문서 적용 | 정본 위치 |
|---------|------|------------|----------|
| **AT-005** | 07 Gate 필수 | §5.1 Installer Layer 4 강제 + §4.2 Registry Step 2 R-63-6 적용 | Part2 §6.7 L5043 |
| **AT-012** | HMAC 서명 필수 | §5.1 Installer Layer 1 강제 + §4.2 Registry Step 1 + §8 R-63-6 | Part2 §6.7 L5050 |
| **AT-003** | 무한 루프 금지 | §5.1 Installer Layer 2 의존성 cycle 방지 | Part2 §6.7 L5041 |
| AT-008 (보조) | P2 Trading OFF | §4.2 Registry Step 3 P2 분류 + §8 R-63-6 명시적 승인 강제 | Part2 §6.7 L5046 |
| 6-2 LOCK L12 (인접) | Docker 샌드박스 30초 + `--network=none` | §5.1 Installer Layer 3 + §5.2 sandbox_spec yaml | 6-2 plan §10 |
| R-63-6 | 등록 보안 검증 | §8 r_63_6_security_validation() — Registry 진입점 강제 | 종합계획서 §4.3 |

---

## 13. cross-handoff 매트릭스 (P4-3 spec G4-6 직계, 2 cross-handoff RESOLVED)

| # | cross-domain | Wave | 인터페이스 / cross-ref | RESOLVED 상태 |
|---|-------------|------|---------------------|------------|
| 1 | **6-2 Security-Governance** | Wave 2 #14 ✅ | §10 통합 보안 검증 (LlamaGuard + Zero-Trust + OWASP) + Red Team 감사 (§7.3 보안 위반 신고 시) | ✅ RESOLVED (§10 분담 매트릭스) |
| 2 | **3-7 Developer-Tools-API-SDK** | Wave 1 #9 ✅ | §11 Plugin SDK 경계 (3-7 정의 정본 + 6-3 Marketplace 인스톨러 경계 명시) | ✅ RESOLVED (경계 명시) |
| 보조 1 | **parl_security.md** (V3 P4-1 내부) | P4-1 ✅ | §7.3 IsolationPolicy.marketplace.deactivate() (격리 시 비활성화 forward-link inheritance) | ✅ RESOLVED |
| 보조 2 | **02_agent-swarm/specialization_protocol.md** (P4-4 forward) | P4-4 forward | §7.4 retire vs marketplace 퇴출 분리 운영 (§9.2 L2025) | ✅ RESOLVED (forward-link) |

---

## 14. Phase 5 entry-gate forward-defined

| 조건 | 충족 방법 |
|------|----------|
| Marketplace 등재 ≥ 5건 staging 7일 측정 | §9.4 E2E-MP-10 + Registry.list() ≥ 5 + staging 7일 운영 PASS |
| 4 컴포넌트 운영 | Registry + Installer + Discovery + Review/Retire ALL ACTIVE staging 7일 |
| E2E ≥ 3 시나리오 | §9 E2E-MP-01/02/03 ALL PASS (정상 + 서명 위반 + 보안 위반 퇴출) |
| **Marketplace 평판 시스템 v12_C09b_467 Phase 5+ 별도 트랙** | 4-3 P4-2 패턴 직계 — Marketplace reputation_score는 v12_C09b_467 평판 시스템 통합 시점에 정합 (Phase 5+ 별도 트랙 forward-defined) |

---

## 15. E6 — 성능 목표 (요약)

| 메트릭 | 목표 | 측정 방법 |
|-------|------|----------|
| `Registry.register` latency | < 200 ms (R-63-6 5-step 포함) | profile timer |
| `Installer.install` latency | < 30 sec (Docker 샌드박스 포함) | profile timer |
| `Discovery.search` latency P95 | < 200 ms (10,000 agents) | Elasticsearch query timer |
| Marketplace 카탈로그 인덱스 갱신 | < 5 sec (등록 후) | indexer log |
| HMAC 검증 latency | < 0.5 ms | hashlib timer |

---

## 16. E8 — 운영 (메트릭 + 알림)

### 16.1 운영 메트릭

| 메트릭 | 목표 | 알림 임계값 | 대응 |
|-------|------|----------|------|
| `marketplace_registration_count_daily` | 정상 | 0 (24h, 비정상) | 운영자 알림 |
| `marketplace_signature_invalid_count` | 0 | > 5 (1h) | 6-2 Red Team 긴급 감사 |
| `marketplace_install_failure_rate` | < 5% | > 10% | Installer 5-Layer 로그 분석 |
| `marketplace_security_violation_reports` | 0 | > 0 (즉시) | ReviewBoard 검토 큐 + 6-2 Red Team |
| `marketplace_reputation_score_avg` | > 3.5 | < 2.5 (전체 평균) | 품질 검토 |
| `marketplace_p0_admin_decisions` | 정상 | 0 (30d, 비정상 if violations exist) | OWNER+ADMIN 검토 |

### 16.2 staging 7일 측정 게이트

> Phase 4 entry-gate 충족: staging 환경 7일 측정 데이터 baseline + Marketplace 등재 ≥ 5건 + E2E-MP-01/02/03 ALL PASS + P0 인간 승인 워크플로 검증.

---

## 17. 산출물 매트릭스 (L3 9요소 매핑)

| L3 요소 | 본 문서 섹션 | PASS |
|--------|------------|:----:|
| E1 (아키텍처) | §3 (4 컴포넌트 다이어그램) + §4 Registry | ✅ |
| E2 (알고리즘) | §7.4 §9.2 L2025 retire vs marketplace 분리 + §8 R-63-6 | ✅ |
| E3 (구현패턴) | §4.2 Registry + §5.1 Installer 5-Layer + §6.1 Discovery + §7 Review/Retire | ✅ |
| E4 (인터페이스) | §4.2 + §5.1 + §6.1 + §7.3 API 정의 | ✅ |
| E5 (보안) | §5.1 5-Layer + §8 R-63-6 + §10 6-2 통합 + §12 LOCK 매트릭스 | ✅ |
| E6 (성능) | §6.2 + §15 (latency + throughput) | ✅ |
| E7 (테스트) | §9 (E2E ≥ 3 핵심 + 7 보강 = 10 시나리오) | ✅ |
| E8 (운영) | §16 (6 메트릭 + staging 7일 측정) | ✅ |
| E9 (확장성) | §13 4 cross-handoff + §14 Phase 5 entry-gate v12_C09b_467 평판 시스템 통합 | ✅ |

**L3 9/9 PASS** (≥7 요건 충족).

---

## 18. 변경 이력

| 일자 | 변경 내용 | 세션 |
|------|----------|------|
| 2026-05-27 | Phase 4 P4-3 production-ready 정본 승급 — 본 문서 NEW (4 컴포넌트 Registry + Installer 5-Layer + Discovery + Review/Retire + R-63-6 등록 보안 검증 + §9.2 L2025 retire vs marketplace 퇴출 분리 + E2E 10 시나리오 (핵심 3 + 보강 7) + 6-2 통합 (LlamaGuard P2-2 + Zero-Trust P2-4 + OWASP P2-5) + 3-7 Plugin SDK 경계 + cross-handoff 4 RESOLVED (6-2 + 3-7 + parl_security forward-link + specialization_protocol forward-link)). Status DRAFT → APPROVED. ReadOnly FALSE 유지. | P4-3 |

---

> **문서 끝**
> 본 문서는 6-3_Agent-Teams-PARL Phase 4 P4-3 production-ready 정본이며, Part2 V3-P3 L4336-L4548 Marketplace 정본 + §6.7 L5096-L5123 Agent Specialization Protocol을 기반으로 작성되었습니다.
> LOCK-AT-005 (07 Gate) + AT-012 (HMAC 서명) + AT-003 (cycle 방지) verbatim + R-63-6 (등록 보안 검증) + §9.2 L2025 retire vs marketplace 분리 + 6-2 LOCK L12 (Docker 샌드박스 30s/--network=none) 정합.
> E2E ≥ 3 (정상 + 서명 위반 + 보안 위반 퇴출) + 보강 7 = 10 시나리오 + L3 9/9 PASS.
> LOCK 변경 0 / DEFINED-HERE 변경 0 / FABRICATION 0 통산.
