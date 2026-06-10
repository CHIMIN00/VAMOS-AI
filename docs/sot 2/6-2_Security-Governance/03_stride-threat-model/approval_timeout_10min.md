# 승인 타임아웃 10분 상세 명세

> **Phase**: 1 (V1)
> **§7.3 항목**: #8 "승인 타임아웃 (10분)"
> **세션**: P1-1
> **작성일**: 2026-04-12
> **상태**: DRAFT

---

## 교차 참조 블록

| 정본 문서 | 섹션 | 참조 내용 |
|----------|------|----------|
| Part2 구현가이드 | §6.5 #9 | 승인 타임아웃 구현 지침 |
| D2.0-07 | §3.1 | 승인 정책 타임아웃 + NEVER_AUTO (정본) |
| AUTHORITY_CHAIN.md | §5 L9 | P2 승인 타임아웃 LOCK |
| AUTHORITY_CHAIN.md | §5 L20 | NEVER_AUTO 정책 LOCK |
| 03_stride-threat-model/_index.md | §C | 승인 타임아웃 항목 |
| rbac_4level.md | §4 | 권한 상승 프로토콜 연동 |

---

## 1. LOCK L9 / L20 교차 검증

> LOCK (D2.0-07 §3): P2 HITL 타임아웃: 5분 내 미응답 시 자동 deny (정본: 일반 승인 10분 / HITL 고위험 5분)

> LOCK (D2.0-07 §3): P1 이상 자동승인 금지. 승인 없이는 실행 금지 (deny 기본)

> LOCK (Part2 §6.5.3): NEVER_AUTO 정책 (P1 이상 자동승인 금지), Gate 순서 강제 (Policy→Approval→Cost→Evidence→SelfCheck)

| 검증 항목 | LOCK 값 | 본 문서 | 일치 |
|----------|--------|--------|:----:|
| 일반 승인 타임아웃 | 10분 (600초) | §2 승인 흐름 | OK |
| HITL(P2) 타임아웃 | 5분 (300초) | §2.2 P2 위험 작업 | OK |
| 타임아웃 초과 행동 | 자동 deny | §3 타임아웃 처리 | OK |
| NEVER_AUTO | P1 이상 자동승인 금지 | §4 NEVER_AUTO 강제 | OK |
| Gate 순서 | Policy→Approval→Cost→Evidence→SelfCheck | §2.1 흐름 내 연동 | OK |

---

## 2. 승인 흐름 설계

### 2.1 전체 흐름

```
[위험 작업 감지]
  → Gate 1: PolicyGate (정책 검증 — L11)
  → Gate 2: ApprovalGate (승인 요청)
    → 승인 요청 생성 (trace_id L18 포함)
    → 사용자 알림 (UI 토스트 + 배지)
    → 타이머 시작:
        일반 작업: 600초 (L9)
        P2 HITL: 300초 (L9)
    → 응답 대기
      ├─ [승인] → Gate 3: CostGate (비용 검증)
      │          → Gate 4: EvidenceGate (근거 검증)
      │          → Gate 5: SelfCheckGate (자기 검증)
      │          → 작업 실행
      ├─ [거부] → 작업 취소 + 감사 로그 ("USER_REJECTED")
      └─ [타임아웃] → 자동 거부 + 감사 로그 ("TIMEOUT_REJECTED")
```

### 2.2 타임아웃 분류

| 작업 유형 | 위험 등급 | 타임아웃 | 근거 |
|----------|---------|:-------:|------|
| 일반 승인 (P1) | MEDIUM | 600초 (10분) | L9 |
| HITL 고위험 (P2) | HIGH | 300초 (5분) | L9 |
| 권한 상승 요청 | MEDIUM | 600초 (10분) | rbac_4level.md §4 연동 |

### 2.3 승인 요청 구조

```typescript
interface ApprovalRequest {
  id: string;                 // UUID v4
  trace_id: string;           // 서버 생성 (L18)
  action: string;             // 실행할 작업 설명
  risk_level: 'P0' | 'P1' | 'P2';   // 위험 등급 (P0=안전/자동, P1/P2=승인 필요)
  requester: {
    agent_id?: string;        // Agent 요청 시
    user_id: string;
    role: RBACLevel;          // 현재 RBAC 레벨 (L8)
  };
  resources: string[];        // 영향받는 리소스 목록
  timeout_ms: number;         // 600000 (P1) | 300000 (P2)
  requested_at: string;       // ISO 8601
  expires_at: string;         // ISO 8601
  gate_context: {
    policy_gate: 'PASSED';    // L11: Gate 1 통과 확인
    cost_estimate_krw: number; // 예상 비용
  };
}
```

---

## 3. 타임아웃 처리

### 3.1 자동 거부 흐름

```typescript
async function handleApprovalTimeout(request: ApprovalRequest): Promise<void> {
  // 시간복잡도: O(1)
  // LOCK 참조: L9 (타임아웃), L20 (NEVER_AUTO)
  
  // 1. 작업 취소
  await cancelPendingAction(request.id);
  
  // 2. 감사 로그 기록
  const auditEntry = {
    event: "security.approval.timeout_rejected",
    trace_id: request.trace_id,
    timestamp: new Date().toISOString(),
    error: {
      code: "APR-TIMEOUT",
      message: `Approval timed out after ${request.timeout_ms / 1000}s`,
      severity: request.risk_level === 'P2' ? 'HIGH' : 'MEDIUM',
    },
    context: {
      request_id: request.id,
      action: request.action,
      risk_level: request.risk_level,
      timeout_seconds: request.timeout_ms / 1000,
      requester_role: request.requester.role,
    },
    recovery: {
      action: "auto_denied",
      retry_allowed: true,
      consecutive_timeouts: getConsecutiveTimeoutCount(request.requester.user_id),
    },
  };
  await logSecurityEvent(auditEntry);
  
  // 3. 사용자 알림
  await notifyUser(request.requester.user_id, {
    type: 'approval_timeout',
    message: `승인 요청이 ${request.timeout_ms / 1000}초 타임아웃으로 자동 거부되었습니다.`,
    trace_id: request.trace_id,
  });
}
```

### 3.2 감사 로그 — "TIMEOUT_REJECTED"

```json
{
  "event": "security.approval.timeout_rejected",
  "trace_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
  "timestamp": "2026-04-12T13:10:00Z",
  "error": {
    "code": "APR-TIMEOUT",
    "message": "Approval timed out after 600s",
    "severity": "MEDIUM"
  },
  "context": {
    "request_id": "req-uuid",
    "action": "execute_external_api_call",
    "risk_level": "P1",
    "timeout_seconds": 600,
    "requester_role": "OPERATOR",
    "gate_position": "ApprovalGate (2/5)"
  },
  "recovery": {
    "action": "auto_denied",
    "retry_allowed": true,
    "consecutive_timeouts": 1,
    "session_warning_threshold": 3
  }
}
```

---

## 4. NEVER_AUTO (L20) 강제

### 4.1 자동 승인 완전 차단

```typescript
// NEVER_AUTO 강제 구현
// LOCK (D2.0-07 §3): P1 이상 자동승인 금지

class ApprovalGate {
  // auto_approve 파라미터 완전 제거
  // 코드 레벨에서 자동 승인 경로 차단
  
  async evaluate(request: ApprovalRequest): Promise<ApprovalResult> {
    // P0 (안전) — Allowlist 내 읽기전용 도구만 자동 통과 (L19)
    if (request.risk_level === 'P0' && this.isInAllowlist(request)) {
      return { approved: true, method: 'allowlist_auto' };
    }
    
    // P1 이상 — 반드시 사용자 수동 승인 (L20: NEVER_AUTO)
    // auto_approve 플래그 무시 (존재해도 작동하지 않음)
    if (request.risk_level >= 'P1') {
      // 절대 자동 승인하지 않음
      return await this.requestUserApproval(request);
    }
  }
  
  // 자동 승인 경로 차단 어설션
  private assertNeverAuto(): void {
    // 코드 내 auto_approve 관련 로직이 존재하면 빌드 실패
    // CI/CD에서 Semgrep rule로 강제 (ISS-7)
  }
}
```

### 4.2 코드 레벨 보호

```yaml
# Semgrep rule: never-auto-approval
rules:
  - id: never-auto-approval
    patterns:
      - pattern: auto_approve = true
      - pattern: autoApprove: true
      - pattern: skip_approval
      - pattern: bypass_approval
    message: "NEVER_AUTO (L20): P1 이상 자동승인 금지"
    severity: ERROR
    metadata:
      lock: L20
      reference: "D2.0-07 §3"
```

---

## 5. 재요청 정책

| 조건 | 처리 |
|------|------|
| 타임아웃 후 동일 작업 재요청 | 허용 (새 trace_id 발급) |
| 연속 타임아웃 2회 | 경고 메시지 |
| 연속 타임아웃 3회 | 세션 레벨 경고 + 감사 로그 "CONSECUTIVE_TIMEOUT_WARNING" |
| 거부 후 재요청 | 허용 (10분 쿨다운 후) |
| P2 작업 연속 거부 3회 | 해당 작업 유형 30분 차단 |

---

## 6. 예외 처리 정책 표

| error_code | 설명 | recoverable | 처리 |
|-----------|------|:-----------:|------|
| APR-TIMEOUT | 승인 타임아웃 (10분/5분) | YES | 자동 거부, 재요청 가능 |
| APR-REJECTED | 사용자 명시 거부 | YES | 작업 취소, 재요청 가능 (쿨다운 후) |
| APR-NEVERAUTO | NEVER_AUTO 위반 시도 | NO | 요청 차단, 감사 로그 |
| APR-CONSECUTIVE | 연속 타임아웃 3회 | YES | 세션 경고, 30분 재시도 불가 |
| APR-GATEORDER | Gate 순서 위반 (L11) | NO | 요청 차단, 시스템 에러 |
| APR-NOTIFY | 알림 전송 실패 | YES | 폴링 모드 폴백, P2 알림 |

---

## 7. Phase 2 통합 테스트 시나리오

| # | 시나리오 | 예상 결과 |
|---|---------|----------|
| T-01 | P1 작업 승인 요청 → 5분 후 승인 | 정상 실행, 감사 로그 |
| T-02 | P1 작업 승인 요청 → 10분 초과 | TIMEOUT_REJECTED, 자동 거부 |
| T-03 | P2 HITL 작업 → 5분 초과 | TIMEOUT_REJECTED (300초) |
| T-04 | P2 HITL 작업 → 3분 후 승인 | 정상 실행 |
| T-05 | auto_approve=true 설정 시도 | NEVER_AUTO 차단 (L20) |
| T-06 | 연속 타임아웃 3회 | 세션 경고 + 감사 로그 |
| T-07 | 타임아웃 후 동일 작업 재요청 | 허용 (새 trace_id) |
| T-08 | Gate 순서 위반 (CostGate 전 실행 시도) | APR-GATEORDER 차단 (L11) |
| T-09 | 감사 로그에 승인/거부/타임아웃 전체 기록 | 3종 이벤트 모두 기록 확인 |
| T-10 | 동시 5건 승인 요청 시 독립 타이머 동작 | 각 요청 독립 타임아웃 |

---

## D2.0-07 §3.1 요구사항 대조

| D2.0-07 §3.1 요구사항 | 본 문서 반영 | 상태 |
|---------------------|------------|:----:|
| P2 위험 작업 승인 필수 | §2 승인 흐름 | OK |
| 일반 10분 타임아웃 | §2.2 P1: 600초 | OK |
| HITL 5분 타임아웃 | §2.2 P2: 300초 | OK |
| 타임아웃 시 자동 deny | §3 TIMEOUT_REJECTED | OK |
| NEVER_AUTO | §4 자동 승인 완전 차단 | OK |
| 5-Gate 순서 강제 | §2.1 Gate 1~5 순서 | OK |
