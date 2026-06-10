# 마켓플레이스 보안 검증 SOP — 스캔 통과율 100% (V3)

> **도메인**: 4-3 MCP-Server-Client (#16, Tier 4 Infrastructure)
> **Phase**: V3 (Phase 4 production-ready 정본 승급) — P4-2
> **Status**: **APPROVED** (2026-06-03, DRAFT→APPROVED, Phase 4 RECOVERY Stage B genuine write)
> **정본**: sot 2/4-3_MCP-Server-Client/02_external-servers/marketplace_security_sop.md
> **상속**: P3-2 forward-defined — 마켓플레이스 4종 프로세스(등록/검증/평가/평판) 중 보안 검증
> **LOCK 인용**: LOCK-MCP-02 (네임스페이스 `{server}.{tool}`) / LOCK-MCP-09 (도구 스키마 정본 sot 2/4-3) — verbatim 인용, 재정의 0
> **횡단**: 6-2 Security-Governance (OWASP LLM05/LLM07) / 6-12 Event-Logging / #11 Conversation-A2A
> **ReadOnly**: FALSE

---

## §0. 목적

VAMOS MCP 마켓플레이스에 외부 개발자가 MCP 서버/도구를 등재할 때, **자동 보안 검증 통과율 100%**를 강제하는 운영 표준 절차(SOP)를 확립한다. 마켓플레이스 등재 ≥ 5건 운영을 위해 등록 → 검증 → 승인 게이트에 보안 스캔을 필수 단계로 삽입한다.

---

## §1. 등재 보안 게이트 (R-16-3 강제)

마켓플레이스 신규 등재 시 R-16-3 "인증/Rate Limit/Fallback 3종 필수 정의" + 보안 스캔 통과를 **차단형(blocking) 게이트**로 적용한다.

```
등재 요청
  → ① 메타데이터 검증 (네임스페이스 LOCK-MCP-02 `{server}.{tool}` 충돌 검사)
  → ② R-16-3 3종 정의 확인 (인증 / Rate Limit / Fallback)
  → ③ 자동 보안 스캔 5종 (§2) — 통과율 100% 미달 시 REJECT
  → ④ 도구 스키마 검증 (LOCK-MCP-09 정본 정합)
  → ⑤ 서명 검증 (6-2 OWASP LLM05/LLM07)
  → 승인 (APPROVED) / 반려 (REJECTED + 사유)
```

> **LOCK-MCP-02 인용 (verbatim, 재정의 0)**: "네임스페이스 접두사 필수 = 중복 도구명 시 `{server}.{tool}`" (AUTHORITY §4).
> **LOCK-MCP-09 인용 (verbatim, 재정의 0)**: "도구 스키마 정본 소유 = sot 2/4-3 (구현), D2.0-04 (아키텍처)" (AUTHORITY §4).

---

## §2. 자동 보안 스캔 5종 (OWASP LLM Top 10 기반)

| # | 스캔 | 대상 | 차단 조건 (OWASP) |
|---|------|------|------------------|
| 1 | 프롬프트 인젝션 | 도구 description / 응답 템플릿 | LLM01 — 간접 인젝션 패턴 탐지 |
| 2 | 공급망 위변조 | 패키지 무결성 / 서명 | LLM05 — 미서명 / 변조 패키지 |
| 3 | 과도 권한 | 요청 스코프 / 파일·네트워크 접근 | LLM07 — Insecure Plugin Design / 최소권한·권한 스코프 위반 |
| 4 | 민감정보 노출 | 하드코딩 시크릿 / PII 유출 | LLM06 — `${secrets.XXX}` 미사용 (R-16-5) |
| 5 | SSRF / 데이터 유출 | 외부 호출 엔드포인트 | LLM02 — 임의 URL / 내부망 접근 |

**통과율 100% 정의**: 5종 스캔 전수 PASS여야 등재 승인. 1종이라도 FAIL → REJECT + 사유 리포트.

> 6-2 Security-Governance가 OWASP LLM05(공급망)/LLM07(과도 권한) 정본 소유. 본 SOP는 6-2 정본을 마켓플레이스 등재 게이트에 적용하는 횡단 참조이며 재정의 0.

---

## §3. 서명 검증 (6-2 OWASP LLM05)

| 단계 | 내용 |
|------|------|
| 패키지 서명 | 게시자 키로 서명된 패키지만 허용 |
| 무결성 해시 | SHA-256 매니페스트 검증 |
| 게시자 신원 | 검증된 게시자(verified publisher) 배지 |
| 취소 목록 | 폐기된 서명(CRL) 차단 |

미서명 / 검증 실패 패키지는 §2 #2 스캔에서 자동 REJECT.

---

## §4. 운영 SOP 단계

### §4.1 신규 등재 처리
1. 등재 요청 수신 → 메타데이터 + R-16-3 3종 검증.
2. 자동 보안 스캔 5종 실행 → 통과율 100% 확인.
3. 서명 검증 → 게시자 신원 확인.
4. 도구 스키마 LOCK-MCP-09 정합 검증.
5. 승인 → 마켓플레이스 등재 + 6-12 등록 이벤트 발행.

### §4.2 사후 모니터링 (등재 후)
1. 등재 서버의 런타임 행위 모니터링 (이상 호출 패턴).
2. 신규 CVE 발생 시 영향 패키지 재스캔.
3. 평판 하락(`marketplace_revenue_share.md` 평판 연계) + 보안 인시던트 시 일시 정지(suspend) / 폐기(delist).

### §4.3 인시던트 대응
1. 악성 패키지 발견 → 즉시 delist + 사용 인스턴스 알림.
2. 6-2 Security-Governance 인시던트 채널 에스컬레이션.
3. RCA + 스캔 룰 업데이트.

---

## §5. 횡단 cross-handoff

| 도메인 | 적용 |
|--------|------|
| 6-2 Security-Governance | OWASP LLM05/LLM07 정본 (서명 검증 / 과도 권한) — 본 SOP가 적용 |
| 6-12 Event-Logging | 등록/평가/반려 이벤트 표준 |
| #11 Conversation-A2A | 마켓플레이스 도구의 A2A 위임 시 보안 컨텍스트 전파 |

---

## §6. staging 7일 측정 baseline (forward-defined)

| 측정 항목 | 목표 |
|----------|------|
| 마켓플레이스 등재 | ≥ 5건 |
| 보안 스캔 통과율 | 100% (승인된 등재 전수) |
| 악성 패키지 차단 | 주입 테스트 100% 탐지 |
| 등재 처리 지연 | 자동 스캔 P95 < 30s |

> production 실측은 staging 배포 시점 실계측 위임.

---

## §7. LOCK 정합 요약 (재정의 0)

LOCK-MCP-02 (네임스페이스) / LOCK-MCP-09 (도구 스키마 정본) verbatim 인용, 재정의 0건. R-16-3 (3종 강제) + R-16-5 (시크릿 마스킹) 정합. 31 도구 DEFINED-HERE 무손상.

---

*P4-2 V3 production .md 정본. 수익 분배는 `marketplace_revenue_share.md` 참조. CLF-MCP-001~005 OPEN 0 inheritance, 신규 CONFLICT 0건.*
