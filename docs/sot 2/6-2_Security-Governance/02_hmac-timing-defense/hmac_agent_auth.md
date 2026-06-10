# HMAC-SHA256 Agent 인증 운영 절차 (L3)

> **Phase**: 2 (V2)
> **§7.3 항목**: P2-1 HMAC-SHA256 Agent 인증 운영 절차
> **세션**: P2-1
> **작성일**: 2026-04-26
> **상태**: APPROVED
> **정본 출처**: Part2 §6.5.2 (HMAC 정본) + 종합계획서 부록 §D (HMAC 키 운영 매트릭스 D.1~D.3)
> **upstream_sot**: STEP7-E Part 8 인시던트 대응 (S7E-069~076) — 8건
> **LOCK 참조**: L3, L4, L5, L6, L11, L18, L20

---

## 1. 교차 참조 블록

| 정본 문서 | 섹션 | 참조 내용 |
|----------|------|----------|
| Part2 §6.5.2 | HMAC 타이밍 공격 방어 (4 LOCK 정본) | L3/L4/L5/L6 원문 |
| 종합계획서 부록 §D | HMAC 키 운영 절차 매트릭스 (D.1~D.3) | 7단계 라이프사이클 + Grace Period 24h + 실패 시나리오 4건 |
| 종합계획서 §4.3 R-62-4 | HMAC 구현 패턴 변경 금지 규칙 | `compare_digest`/`timingSafeEqual` 외 비교 금지 |
| AUTHORITY_CHAIN.md | §4 L3~L6 + §5.1 L3~L6 원문 | HMAC 4-LOCK verbatim |
| 02_hmac-timing-defense/_index.md | §A/§B/§C/§D | Phase 1 5 방어 항목 + 7단계 매트릭스 |
| api_key_management.md | §1~§4 | V1 키 저장 아키텍처 (.env+dotenv) — 본 V2 키 순환 운영의 기반 |
| 6-12 Event-Logging (cross-handoff) | audit_log 인터페이스 (W-1 RESOLVED) | `oc.security.key_rotation.{started\|completed}` 발행 |
| 6-3 Agent-Teams-PARL (cross-handoff) | LOCK-AT-012 Agent 메시지 HMAC 서명 필수 | Agent MessageBus 인증 인터페이스 |
| STEP7-E Part 8 | S7E-069~076 인시던트 대응 8건 | P0~P3 심각도 분류 + 자동 격리 + 롤백 + RCA |

---

## 2. LOCK 정본 인용 (4-field verbatim)

> **절대 규칙**: 본 V2 산출물은 아래 LOCK 값을 재정의하지 않는다. 인용은 5필드 verbatim (LOCK ID + 항목 + 정본 출처 + 값 + 원문) 형식을 따른다.

| LOCK | 항목 | 정본 출처 | 값 |
|------|------|----------|-----|
| **L3** | HMAC 알고리즘 | Part2 §6.5.2 | HMAC-SHA256 (상수 시간 비교 필수) |
| **L4** | HMAC 키 최소 길이 | Part2 §6.5.2 | 32바이트 |
| **L5** | HMAC 키 순환 주기 | Part2 §6.5.2 | 90일 |
| **L6** | 리플레이 방지 윈도우 | Part2 §6.5.2 | 5분(300초) |
| **L11** | 5-Gate System | D2.0-07 §5 | Policy→Approval→Cost→Evidence→SelfCheck |
| **L18** | trace_id 생성 | Part2 §6.5.1 | 서버 측 UUID v4 전용 (클라이언트 신뢰 금지) |
| **L20** | NEVER_AUTO 정책 | D2.0-07 §3 / Part2 §6.5.3 | P1 이상 자동승인 금지, Gate 순서 강제 |

### 2.1 L3 원문 (HMAC 알고리즘)

> LOCK (Part2 §6.5.2): 상수 시간 비교 — `hmac.compare_digest()` (Python) / `crypto.timingSafeEqual()` (Node.js) 사용. `==` 연산자로 HMAC 직접 비교 금지. 알고리즘: `hmac.new(key, payload, hashlib.sha256).hexdigest()`

### 2.2 L4 원문 (HMAC 키 최소 길이)

> LOCK (Part2 §6.5.2): HMAC-SHA256 기준 최소 32바이트 키. 짧은 키 자동 거부 (`len(key) < 32 → raise SecurityError`)

### 2.3 L5 원문 (HMAC 키 순환 주기)

> LOCK (Part2 §6.5.2): 90일 주기 자동 키 순환. 이전 키는 grace period(24h) 후 폐기. `key_version` 필드로 다중 키 지원

### 2.4 L6 원문 (리플레이 방지 윈도우)

> LOCK (Part2 §6.5.2): 요청에 `timestamp` + `nonce` 포함. 5분(300초) 초과 타임스탬프 거부, nonce 중복 거부 (Redis/SQLite TTL 캐시). 코드: `max_age: int = 300`

---

## 3. R-62-4 규칙 (HMAC 비교 함수 변경 금지)

> **규칙 정본 (종합계획서 §4.3)**: HMAC 구현 패턴 변경 금지 — `hmac.compare_digest()` (Python) / `crypto.timingSafeEqual()` (Node.js) 외 비교 방법 사용 불가.

| 언어 | 정본 비교 함수 | 금지 패턴 | 위반 시 |
|------|--------------|----------|---------|
| Python 3.x | `hmac.compare_digest(expected, actual)` | `expected == actual` / `expected.startswith(actual)` / 직접 byte 순회 비교 | CK-04 SAST 차단, PR 머지 거부 |
| Node.js 18+ | `crypto.timingSafeEqual(Buffer, Buffer)` | `expected === actual` / `Buffer.compare()` (정렬 비교) | CK-04 SAST 차단, PR 머지 거부 |
| Rust | `subtle::ConstantTimeEq::ct_eq` | `==` / `slice::PartialEq` | CK-04 SAST 차단, PR 머지 거부 |

> **R-62-4 위반 탐지**: CI/CD 파이프라인 (4-2 cross-handoff)에서 정규식 SAST 룰 `hmac.*==|hmac.*!=` 매칭 (상수 시간 함수 `hmac.compare_digest`/`crypto.timingSafeEqual`은 COMPLIANT이므로 위반 패턴에서 제외). AST 검사로 비교 컨텍스트 확정.

---

## 4. HMAC 키 라이프사이클 7단계 (부록 §D D.1 정본 인용)

> **정본**: 종합계획서 부록 §D D.1 — 키 생성 → 저장 → 배포 → 순환 → Grace Period → 폐기 → 긴급 교체 7단계

### 4.1 단계별 운영 매트릭스

| 단계 | 절차 | 담당 | 자동화 | 검증 방법 | 관련 LOCK | audit_log 이벤트 (6-12 발행) |
|------|------|------|:---:|----------|----------|----------------------------|
| **1. 생성** | `crypto.randomBytes(32)` (Node.js) / `os.urandom(32)` (Python) → CSPRNG, 최소 32바이트, `key_id = uuid4()` | 시스템 (자동) | ✅ | 키 길이 ≥ 32 + 엔트로피 검증 | L4 | `oc.security.key.generated` |
| **2. 저장** | V1: `.env` + dotenv (`chmod 0600`, `.gitignore` 필수) / V2: HashiCorp Vault KV v2 + namespace 분리 | DevOps | V2 ✅ | gitleaks pre-commit hook + Vault audit log | — | `oc.security.key.stored` |
| **3. 배포** | 환경변수 주입 (Docker secrets / K8s SealedSecrets / Vault Agent sidecar) | CI/CD | ✅ | 배포 직후 키 SHA256 해시값 비교 (전체 키 노출 금지) | — | `oc.security.key.deployed` |
| **4. 순환** | 90일 주기 자동 (매일 실행 잡 + `last_rotated_at` 경과일 ≥90일 비교; cron DOM 91/181/271은 무효하여 금지) | 시스템 (스케줄러) | ✅ | 순환 이벤트 로그 + Grace 진입 트리거 확인 | **L5** | `oc.security.key_rotation.started` |
| **5. Grace Period** | 구 키 24시간 병행 (NEW + OLD 모두 `key_version`별 검증) | 시스템 (자동) | ✅ | 양쪽 키 모두 HMAC 검증 통과 + 우선순위 NEW>OLD 확인 | **L5** | `oc.security.key_rotation.grace_active` |
| **6. 폐기** | Grace 만료 후 OLD 완전 삭제 + 메모리 zeroize + 감사 로그 | 시스템 (자동) | ✅ | OLD 키 HMAC 검증 실패 (401) 확인 | — | `oc.security.key_rotation.completed` |
| **7. 긴급 교체** | 키 유출 시: 즉시 폐기 → 신규 생성 → Grace 없이 즉시 적용 → 영향 범위 식별 | DevOps + Oncall | ⬜ 수동 | S7E-005 인시던트 절차 (P0 즉시 대응) | — | `oc.security.key.emergency_rotated` |

### 4.2 5-Gate 정합 (L11 5-Gate System)

| Gate | HMAC 운영과의 관계 |
|------|-------------------|
| **PolicyGate** | 키 순환 정책 위반 (만료 키 사용) 시 차단 |
| **ApprovalGate** | 7단계 긴급 교체 시 P2 oncall 승인 필수 (NEVER_AUTO L20 적용) |
| **CostGate** | Vault 호출 비용 일일 한도 내 (V2: ₩93,000 L17) |
| **EvidenceGate** | `oc.security.key.*` 이벤트 6-12 audit_log에 영구 저장 (W-1) |
| **SelfCheckGate** | 매 키 순환 후 dual-key 검증 dry-run 통과 후 운영 모드 전환 |

---

## 5. Grace Period 24시간 운영 상세 (부록 §D D.2 정본 인용)

> **정본**: 종합계획서 부록 §D D.2 — Grace Period 24시간 동안 신·구 키 병행 검증.

### 5.1 정본 흐름 (verbatim)

```
[순환 시작]
  → 신규 키 생성 (crypto.randomBytes(32))
  → 환경변수에 NEW_KEY + OLD_KEY 모두 등록
  → Agent HMAC 검증: NEW_KEY 우선 → 실패 시 OLD_KEY 검증
  → 24시간 경과 후 OLD_KEY 삭제
  → 감사 로그: oc.security.key_rotation.{started|completed}
```

### 5.2 키 버전 매니페스트 스키마

```typescript
interface HmacKeyManifest {
  key_id: string;            // UUID v4 (L18 패턴 동일)
  key_version: number;       // 단조 증가 (1, 2, 3, ...)
  algorithm: "HMAC-SHA256";  // L3 고정
  key_length_bytes: 32;      // L4 최소
  generated_at: string;      // ISO 8601 UTC
  rotated_at?: string;       // 다음 순환 시각
  grace_until?: string;      // generated_at + 24h
  status: "active" | "grace" | "expired" | "emergency_revoked";
  parent_key_id?: string;    // 이전 키 추적 (감사용)
}
```

### 5.3 Dual-Key 검증 의사코드 (R-62-4 준수)

```python
import hmac, hashlib, time
from typing import Optional

def verify_hmac_dual_key(
    payload: bytes,
    signature: str,
    key_new: bytes,
    key_old: Optional[bytes] = None,
    max_age: int = 300,  # L6: 5분
) -> tuple[bool, str]:
    """
    Grace Period 동안 Dual-Key HMAC 검증.

    LOCK 준수:
    - L3: hmac.compare_digest() 상수 시간 비교 (R-62-4)
    - L4: 키 길이 ≥ 32 검증
    - L5: 90일 순환 → grace 24h 동안 dual key
    - L6: 5분 윈도우 리플레이 방지

    Returns: (검증 성공 여부, 사용된 key_version)
    """
    # L4 강제: 짧은 키 즉시 거부
    if len(key_new) < 32:
        raise SecurityError("HMAC key too short (L4: ≥32 bytes required)")

    # L6 강제: 타임스탬프 윈도우
    ts = extract_timestamp(payload)
    if abs(time.time() - ts) > max_age:
        return False, "timestamp_out_of_window"

    # L3 + R-62-4: NEW 우선 상수 시간 비교
    expected_new = hmac.new(key_new, payload, hashlib.sha256).hexdigest()
    if hmac.compare_digest(expected_new, signature):
        return True, "NEW"

    # OLD 폴백 (Grace Period 내에서만)
    if key_old is not None and len(key_old) >= 32:
        expected_old = hmac.new(key_old, payload, hashlib.sha256).hexdigest()
        if hmac.compare_digest(expected_old, signature):
            return True, "OLD"

    return False, "signature_mismatch"
```

### 5.4 nonce 캐시 정책 (L6 보강)

| 항목 | 값 | 비고 |
|------|----|------|
| 저장소 | Redis (V2 운영) / SQLite TTL 캐시 (V1) | 캐시 미스 = 새 nonce 인정 |
| TTL | 600초 (윈도우 5분 × 2 안전 마진) | L6 윈도우보다 길게 |
| 키 패턴 | `hmac:nonce:{key_id}:{nonce}` | namespace 분리 |
| 충돌 시 응답 | HTTP 401 + `WWW-Authenticate: HMAC error="replay_detected"` | 메시지 균일화 (Phase 1 §A 5번) |

---

## 6. 실패 시나리오 4건 + 롤백 (부록 §D D.3 정본 인용)

> **정본**: 종합계획서 부록 §D D.3 — 실패 시나리오 4건 및 롤백 절차.

### 6.1 시나리오 매트릭스 (정본 verbatim)

| # | 시나리오 | 탐지 방법 | 대응 | 에스컬레이션 | 6-12 audit_log 이벤트 |
|---|----------|----------|------|-------------|----------------------|
| 1 | **신규 키 배포 실패** | 키 해시 미일치 알림 | 구 키로 자동 롤백 | P2 oncall 통보 | `oc.security.key.deploy_failed` |
| 2 | **Grace 기간 인증 실패 급증** | 6-12 이벤트 모니터링 (1분 이내 100+ 401) | 듀얼 키 검증 로직 확인 + 임시 Grace 연장 (최대 +24h, 1회) | P1 oncall 통보 | `oc.security.key.grace_anomaly` |
| 3 | **키 유출 감지** | gitleaks/Vault audit/외부 보안 스캔 | 긴급 교체 즉시 발동 (4.1 단계 7) + 영향 범위 자동 격리 (S7E-070) | **P0 즉시 대응** | `oc.security.key.compromised` |
| 4 | **Vault 접근 불가 (V2)** | 헬스체크 실패 (Vault `/v1/sys/health` 503) | 로컬 캐시 키 사용 (최대 1시간) + 신규 발급 차단 | P1 인프라 팀 | `oc.security.vault.unavailable` |

### 6.2 STEP7-E Part 8 인시던트 대응 매핑

| STEP7-E ID | 제목 | 우선순위 | HMAC 운영과의 연계 |
|-----------|------|---------|-------------------|
| **S7E-069** | 인시던트 분류 체계 — 심각도 4단계 | HIGH (V1) | 시나리오 1=P2, 2=P1, 3=**P0**, 4=P1 매핑 |
| **S7E-070** | 자동 격리 — 위협 자동 차단 | HIGH (V1) | 키 유출 시 영향 범위 식별 후 해당 Agent/세션 자동 격리 |
| **S7E-071** | 롤백 시스템 — 상태 복구 | HIGH (V2) | 시나리오 1: 구 키로 즉시 롤백, 시나리오 4: 1시간 캐시 폴백 |
| **S7E-072** | Root Cause Analysis — 5 Whys | HIGH (V2) | 시나리오 2/3 발생 후 RCA 보고서 작성 (24h 이내) |
| **S7E-073** | 긴급 연락 체계 — 30분/60분 에스컬레이션 | MED (V1) | 시나리오 3 P0: 즉시 → 30분 미응답 시 안전 모드 전환 |
| **S7E-074** | 안전 모드 — 외부 API 차단, 로컬 읽기전용 | MED (V1) | 시나리오 3: 키 교체 완료까지 신규 발급 차단 |
| **S7E-075** | 인시던트 대응 훈련 — 분기 1회 | MED (V2) | 시나리오 1~4 시뮬레이션 분기 1회 정기 훈련 |
| **S7E-076** | 보안 인시던트 DB — 추세 분석 | MED (V2) | 시나리오 발생 이력을 DB 적재 → 갱신 패턴 분석 |

---

## 7. Agent MessageBus HMAC 서명 (6-3 cross-handoff)

> **6-3 Agent-Teams-PARL LOCK-AT-012 cross-handoff**: 모든 Agent 메시지에 HMAC 서명 필수. 본 V2 산출물은 인터페이스 명세만 제공하며, PARL 패턴 정본은 6-3에 위치 (재정의 ❌).

### 7.1 메시지 봉투 스키마

```typescript
interface AgentSignedMessage {
  // 메시지 본문
  body: object;

  // HMAC 메타 (L3/L4/L5/L6/L18 정합)
  hmac_meta: {
    key_id: string;            // 서명 시점의 key_id (5.2 매니페스트 참조)
    key_version: number;       // 단조 증가
    algorithm: "HMAC-SHA256";  // L3 고정
    timestamp: string;         // ISO 8601 UTC (L6 5분 윈도우 적용)
    nonce: string;             // UUID v4 (L18 패턴, 서버 검증 시 캐시)
    trace_id: string;          // 서버 측 UUID v4 (L18, 클라이언트 신뢰 금지)
  };

  // 서명 (hex 문자열)
  signature: string;
}
```

### 7.2 서명 대상 (canonical form)

```
canonical_payload = sha256(
  utf8(json_canonicalize(body))
  || utf8(hmac_meta.key_id)
  || utf8(hmac_meta.timestamp)
  || utf8(hmac_meta.nonce)
)
signature = hmac_sha256(active_key, canonical_payload)
```

### 7.3 검증 흐름 (수신 측)

1. **타임스탬프 윈도우 검증** (L6): `|now - timestamp| ≤ 300s`
2. **nonce 중복 검증** (L6): Redis/SQLite TTL 캐시 조회 → 중복 시 401
3. **키 매니페스트 조회**: `key_id` → 활성/grace 상태 확인 (5.2)
4. **Dual-Key 검증** (5.3 의사코드): NEW 우선 → OLD 폴백
5. **trace_id 검증** (L18): 클라이언트 trace_id 무시, 서버 생성 값으로 교체
6. **6-12 audit_log 발행**: `oc.security.hmac.{verified|rejected}` 이벤트

---

## 8. Phase 3 이월 (P2→P3 게이트 충족)

| 항목 | Phase 2 결과 | Phase 3 잔여 |
|------|-------------|-------------|
| L3 상수 시간 비교 (R-62-4) | ✅ 의사코드 완료 (5.3) | 실제 코드 구현 + AST SAST 룰 작성 |
| L4 키 길이 검증 | ✅ 의사코드 완료 | 라이브러리 wrapper 구현 |
| L5 90일 순환 + Grace 24h | ✅ 매트릭스 + 의사코드 + 매니페스트 스키마 | cron 잡 배포 + Vault 정책 |
| L6 5분 윈도우 + nonce 캐시 | ✅ 정책 명시 | Redis 클러스터 + TTL 동작 검증 |
| 7단계 라이프사이클 | ✅ 매트릭스 완료 (4.1) | 자동화 ⬜ 단계(7) 수동 절차 runbook 작성 |
| 4건 실패 시나리오 | ✅ 매트릭스 완료 (6.1) | 분기 훈련 시나리오 (S7E-075) 실시 |
| 6-12 audit_log 통합 (W-1) | ✅ 이벤트 ID 정의 (4.1, 6.1) | 6-12에 LOCK-EL-* 등록 (NEVER_AUTO 동기) |
| 6-3 Agent MessageBus | ✅ 인터페이스 (7.1~7.3) | PARL 패턴 통합 (6-3 정본) |

> **P2→P3 전환 게이트 "HMAC 운영 절차 확정" ✅ 충족** — 본 V2 산출물 + Phase 1 `_index.md` §A~§F + AUTHORITY §4 L3~L6 + 부록 §D D.1~D.3 통합 명세 완료.

---

## 9. cross-handoff 도메인 (재정의 0건 엄수)

| 도메인 | 인터페이스 | 본 V2 영향 | 재정의 여부 |
|--------|----------|-----------|-----------|
| **6-12 Event-Logging** | audit_log 이벤트 발행 (W-1 RESOLVED) | 4.1 + 6.1에 7+4=11개 이벤트 ID 정의 | ❌ LOCK-EL-* 재정의 없음, 이벤트 발행자 측 인터페이스만 |
| **6-3 Agent-Teams-PARL** | LOCK-AT-012 Agent 메시지 HMAC 서명 | §7 메시지 봉투 + 검증 흐름 인터페이스 | ❌ PARL 패턴 정본 6-3 재정의 없음 |
| **4-2 CI/CD-Pipeline** | R-62-4 SAST 룰 (W-3 RESOLVED) | §3 정규식 + AST 룰 정의 | ❌ CI/CD 파이프라인 LOCK-CI-* 재정의 없음, 정책 정의만 |
| **4-3 MCP-Server-Client** | MCP Tool HMAC 서명 (선택, V3 범위) | 본 V2에서는 Agent MessageBus만 다룸 | ❌ Phase 3 이월 |
| **3-7 Developer-Tools-API-SDK** | API Key 관리 (cross-ref) | V1 `api_key_management.md` 와 §1.1 통합 | ❌ 본 도메인 V1 산출물 그대로 활용 |
| **4-1 Rust-Tauri-Infrastructure** | IPC HMAC 서명 (cross-ref) | §7 Agent MessageBus 인터페이스 활용 | ❌ Tauri IPC 4-1 LOCK-RT-* 재정의 없음 |

---

## 10. 검증 체크리스트 (P2-1 exit_gate)

- [x] P2→P3 게이트 "HMAC 운영 절차 확정" 충족 (§8)
- [x] L3 (HMAC-SHA256 + 상수 시간 비교) verbatim 인용 (§2.1, §3, §5.3)
- [x] L4 (32바이트) verbatim 인용 (§2.2, §5.3 코드)
- [x] L5 (90일) verbatim 인용 (§2.3, §4.1 단계 4)
- [x] L6 (5분/300초) verbatim 인용 (§2.4, §5.3 코드, §5.4)
- [x] R-62-4 규칙 명시 (§3, §5.3 코드 주석)
- [x] 부록 §D D.1 7단계 매트릭스 정본 인용 (§4.1)
- [x] 부록 §D D.2 Grace Period 흐름 verbatim (§5.1)
- [x] 부록 §D D.3 실패 시나리오 4건 정본 인용 (§6.1)
- [x] STEP7-E Part 8 S7E-069~076 8건 ID 매핑 (§6.2)
- [x] 6-12 audit_log 이벤트 ID 정의 (§4.1 7건 + §6.1 4건 + §7.3 2건 = 13개)
- [x] 6-3 Agent MessageBus HMAC 인터페이스 (§7)
- [x] cross-handoff 6 도메인 경계 명시 + 재정의 0건 (§9)
- [x] LOCK 신규 추가 0건 (V3 범위 이월)
- [x] [CONFLICT_CANDIDATE:*] 발화 0건

---

## 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-04-26 | v1.0 P2-1 V2 신규 작성 (STAGE 7 STEP_B 세션 P2-1, plan §7.3 L1194~L1231 정본) |
