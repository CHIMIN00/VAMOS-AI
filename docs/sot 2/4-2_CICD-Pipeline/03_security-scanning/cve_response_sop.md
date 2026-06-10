# CVE 대응 SOP — V3 (4-2 P4-2)

> **카테고리**: 03_security-scanning
> **세션**: P4-2 (Phase 4 RECOVERY Stage A+B 통합)
> **목적**: LOCK-CI-09 Critical/High CVE 즉시 머지 차단 정책 + LOCK-CI-08 5도구 100% + R-15-3 자동화의 운영 SOP를 정본화한다. 핫픽스 브랜치 절차 + CVE 분류 + 6-2 Security-Governance 정합.
> **버전**: v3.0 (NEW, 2026-06-01)
> **상태**: DRAFT → APPROVED (Phase 4 RECOVERY Stage B Gate 2 PROCEED, 2026-06-01)
> **LOCK**: LOCK-CI-08 (5도구), LOCK-CI-09 (CVE 즉시 실패)
> **ReadOnly**: FALSE

---

## §1. 교차 참조 블록

| 대상 | 경로 / 섹션 | 용도 |
|------|-----------|------|
| AUTHORITY | `AUTHORITY_CHAIN.md` LOCK-CI-08 + LOCK-CI-09 | CVE/스캔 정본 (verbatim) |
| WF | `03_security-scanning/WF-8_security-scan.md` + `WF-11_dependency-check.md` | 스캔 WF 구조 |
| Secrets | `03_security-scanning/secrets_mapping.md` §5.2/§5.3 | 스캔 시크릿 |
| 장애 대응 | `02_cd-workflows/incident_response_playbook.md` (P4-2) C3/C4 | CVE/유출 카테고리 |
| 시크릿 유출 | `03_security-scanning/runbook_secret_rotation.md` (P4-1) §5 | 긴급 로테이션 연계 |
| 횡단 | `6-2_Security-Governance/` CVE 대응 §9.4 | 보안 거버넌스 정합 |

---

## §2. LOCK 정본 (verbatim 인용)

> AUTHORITY_CHAIN.md 정본 verbatim (재정의 0):
> `LOCK-CI-08 | 보안 스캔 5도구 | 상세명세 WF-8 | pip-audit, cargo-audit, semgrep, trufflehog, trivy | 보안팀 승인`
> `LOCK-CI-09 | CVE 즉시 실패 정책 | 상세명세 WF-8 | Critical/High → 즉시 실패, Medium → 7일 해결 | 보안팀 승인`

---

## §3. LOCK-CI-08 5 도구 100% 통과율

| 도구 | 영역 | 시크릿 | 실패 정책 |
|------|------|--------|----------|
| pip-audit | Python 의존성 advisory | 불요 (public DB) | Critical/High 즉시 차단 |
| cargo-audit | Rust 의존성 advisory | 불요 | 동일 |
| semgrep | SAST (코드 패턴) | `SEMGREP_APP_TOKEN` (선택, Cloud) | Critical 차단 |
| trufflehog | 시크릿 유출 (커밋 히스토리) | 불요 | `SECRET_LEAK` Critical 차단 (P0) |
| trivy | 컨테이너 이미지 취약점 | `TRIVY_DB_REPOSITORY_TOKEN` (선택, GHCR mirror) | Critical/High 차단 |

> 5 도구 통과율 100% = WF-8 의 모든 도구가 게이트로 작동 (선택 시크릿 없으면 local-only/keyless fallback, 게이트는 유지).

---

## §4. LOCK-CI-09 CVE 분류 + 즉시 차단 SOP

| 심각도 | 정책 | 동작 | SLA |
|--------|------|------|-----|
| **Critical** | 즉시 실패 | PR 머지 차단 + P1 incident (PagerDuty P1) | 즉시 (MTTR ≤ 30min 핫픽스) |
| **High** | 즉시 실패 | PR 머지 차단 + P1 incident | ≤ 2h |
| **Medium** | 7일 해결 | 경고 + Issue 생성 | 7일 |
| **Low** | 기록 | backlog | best-effort |

### §4.1 즉시 머지 차단 흐름 (R-15-3 자동화)

1. WF-8 5도구 스캔 → SARIF 업로드 (`GITHUB_TOKEN`).
2. Critical/High finding → GitHub Status Check **fail** → **PR 머지 차단** (자동, R-15-3).
3. 보안팀 Slack `#security` 알림 + Critical 은 PagerDuty P1.
4. finding 해소(의존성 bump / 코드 수정) 전까지 머지 불가 (우회 금지).

---

## §5. 핫픽스 브랜치 절차

1. **분기**: `main` 에서 `hotfix/cve-<advisory-id>` 생성.
2. **수정**: 취약 의존성 버전 bump 또는 코드 패치.
3. **검증**: WF-8 재스캔 → Critical/High 0 확인 + WF-2 회귀 테스트.
4. **긴급 승인**: 프로덕션 영향 시 `runbook_prod_approval.md` §3.4 긴급 경로(롤백/핫픽스) 적용.
5. **머지·배포**: `main` 머지 → 핫픽스 릴리스(WF-5) → 프로덕션 배포(WF-7).
6. **백포트**: develop/release 브랜치 cherry-pick.
7. **사후**: `rca_template.md` + SBOM 갱신.

---

## §6. 시크릿 유출 (trufflehog) 연계

`SECRET_LEAK` Critical Finding → P0 → `runbook_secret_rotation.md` §5 긴급 로테이션 + `incident_response_playbook.md` C4 → CISO 통보.

---

## §7. 담당 / 에스컬레이션

- **1차**: 보안팀. **에스컬레이션**: L2 (보안팀 Slack) → L3 (보안팀 리드 + PagerDuty P2) → L4 (CISO + PagerDuty P1, Critical/유출).

---

## §8. LOCK 준수 선언

- **LOCK-CI-08 verbatim 보존**: §2/§3 5 도구 정본 인용, 재정의 0.
- **LOCK-CI-09 verbatim 보존**: §2/§4 즉시 실패 정책 정본 인용 (Critical/High 즉시 / Medium 7일).
- **R-15-3 자동화**: §4.1 PR 머지 차단 흐름 정합.

> **정본 선언**: 본 문서는 4-2 도메인 CVE 대응 SOP 정본(V3)이다. LOCK-CI-08/09 변경 시 보안팀 승인 필수.
