# RBAC 4레벨 접근 제어 상세 명세

> **Phase**: 1 (V1)
> **§7.3 항목**: #6 "RBAC 4레벨"
> **세션**: P1-1
> **작성일**: 2026-04-12
> **상태**: DRAFT

---

## 교차 참조 블록

| 정본 문서 | 섹션 | 참조 내용 |
|----------|------|----------|
| Part2 구현가이드 | §6.5 #5 | RBAC 구현 지침 |
| D2.0-07 | §13 | RBAC 접근 제어 정책 (정본) |
| AUTHORITY_CHAIN.md | §5 L8 | RBAC 4단계 LOCK |
| AUTHORITY_CHAIN.md | §5 L9 | P2 승인 타임아웃 LOCK |
| AUTHORITY_CHAIN.md | §5 L19 | DEC-003 도구 승인 LOCK |
| 03_stride-threat-model/_index.md | §C | 인증/인가/접근제어 |
| approval_timeout_10min.md | — | 승인 타임아웃 L9 연동 |
| dec003_tool_allowlist.md | — | DEC-003 L19 연동 |

---

## 1. LOCK L8 교차 검증

> LOCK (D2.0-07 §13): OWNER(시스템 소유자 — 모든 정책 변경, 비용 상한 변경, P2 도메인 승인 포함 전체 권한) / ADMIN(위임된 관리자 — 정책 조회, 일반 설정 변경, Agent 실행 허용. Constitution 편집/P2 승인은 OWNER만) / OPERATOR(일반 운영자 — 일반 Task 실행, 허용목록 내 Tool 호출, 비P2 도메인 작업) / VIEWER(읽기 전용 열람자 — 로그/이벤트 조회, 대시보드 열람, 실행/승인 불가)

> LOCK (Part2 §6.5): RBAC 역할별 접근 — OWNER(모든 화면, 제한 없음) / ADMIN(모든 화면, 시스템 삭제 불가) / OPERATOR(Dashboard·Chat·Workflow·Memory, Settings 읽기 전용) / VIEWER(Dashboard·Chat 읽기, 입력/실행 불가)

| 검증 항목 | LOCK L8 값 | 본 문서 | 일치 |
|----------|-----------|--------|:----:|
| 4레벨 명칭 | OWNER/ADMIN/OPERATOR/VIEWER | §2 전체 | OK |
| OWNER 권한 | 전체 권한, P2 승인 포함 | §2.1 | OK |
| ADMIN 권한 | 정책 조회, 설정 변경, Constitution/P2 제외 | §2.2 | OK |
| OPERATOR 권한 | 일반 Task, 허용 Tool, 비P2 | §2.3 | OK |
| VIEWER 권한 | 읽기 전용, 실행/승인 불가 | §2.4 | OK |

---

## 2. 4레벨 권한 모델 상세 설계

### 2.1 L3 Owner (시스템 소유자)

| 항목 | 값 |
|------|-----|
| **권한 범위** | 모든 정책 변경, 비용 상한 변경, P2 도메인 승인, 전체 권한 |
| **UI 접근** | 모든 화면, 제한 없음 |
| **특수 권한** | Constitution 편집, LOCK 변경 제안, 거버넌스 접근 |
| **기본 할당** | 시스템 초기 설정자 |
| **제한** | 없음 (최고 권한) |

### 2.2 L2 Admin (위임된 관리자)

| 항목 | 값 |
|------|-----|
| **권한 범위** | 정책 조회, 일반 설정 변경, Agent 실행 허용 |
| **UI 접근** | 모든 화면, 시스템 삭제 불가 |
| **특수 권한** | Allowlist 변경 승인, 보안 설정 조회 |
| **제한** | Constitution 편집 불가, P2 승인 불가 (OWNER만) |

### 2.3 L1 Operator (일반 운영자)

| 항목 | 값 |
|------|-----|
| **권한 범위** | 일반 Task 실행, 허용목록(Allowlist) 내 Tool 호출, 비P2 작업 |
| **UI 접근** | Dashboard, Chat, Workflow, Memory / Settings 읽기 전용 |
| **제한** | P2 도메인 작업 불가, 설정 변경 불가, Allowlist 수정 불가 |

### 2.4 L0 Viewer (읽기 전용 열람자)

| 항목 | 값 |
|------|-----|
| **권한 범위** | 로그/이벤트 조회, 대시보드 열람 |
| **UI 접근** | Dashboard, Chat 읽기 전용 |
| **제한** | 입력 불가, 실행 불가, 승인 불가 |

---

## 3. 권한 매트릭스

| 리소스/액션 | L0 Viewer | L1 Operator | L2 Admin | L3 Owner |
|------------|:---------:|:-----------:|:--------:|:--------:|
| 대화 읽기 | READ | READ | READ | READ |
| 대화 입력 | DENY | ALLOW | ALLOW | ALLOW |
| 도구 실행 (P0 안전) | DENY | ALLOW | ALLOW | ALLOW |
| 도구 실행 (P1 일반) | DENY | CONFIRM | ALLOW | ALLOW |
| 도구 실행 (P2 위험) | DENY | DENY | DENY | ALLOW+TIMEOUT |
| 설정 조회 | DENY | READ | READ | READ |
| 설정 변경 | DENY | DENY | ALLOW | ALLOW |
| 감사 로그 조회 | READ | READ | READ | READ |
| 감사 로그 삭제 | DENY | DENY | DENY | ALLOW |
| Allowlist 변경 | DENY | DENY | ALLOW | ALLOW |
| LOCK 변경 제안 | DENY | DENY | DENY | ALLOW |
| Constitution 편집 | DENY | DENY | DENY | ALLOW |
| P2 도메인 승인 | DENY | DENY | DENY | ALLOW |
| 시스템 삭제 | DENY | DENY | DENY | ALLOW |
| 사용자 역할 변경 | DENY | DENY | ALLOW (L0/L1만) | ALLOW |

---

## 4. 권한 상승 프로토콜

### 4.1 상승 흐름

```
[상승 요청] → 인증 확인 (현재 역할 검증)
  → 대상 역할 검증 (L0→L1, L1→L2만 허용; L2→L3은 OWNER 직접 할당만)
  → 승인 요청 생성 (trace_id L18 포함)
  → L2 Admin 이상 승인 대기 (L1→L2 상승은 L3 Owner만)
  → 타임아웃 600초 (L9 연동)
    ├─ [승인] → 역할 변경 + 감사 로그
    └─ [타임아웃/거부] → 원래 역할 유지 + 감사 로그
```

### 4.2 상승 제약

| 상승 경로 | 승인 권한 | 타임아웃 | 비고 |
|----------|----------|---------|------|
| L0 → L1 | L2 Admin | 600초 (L9) | 기본 상승 |
| L1 → L2 | L3 Owner | 600초 (L9) | OWNER 직접 승인 필수 |
| L2 → L3 | 불가 | — | L3 Owner는 시스템 초기 설정 시에만 할당 |
| 임시 상승 | L2 Admin | 3600초 (1시간) | 세션 레벨 임시 상승, 자동 복귀 |

### 4.3 의사코드

```typescript
async function requestRoleElevation(
  userId: string,
  currentRole: RBACLevel,
  targetRole: RBACLevel,
  traceId: string
): Promise<ElevationResult> {
  // 시간복잡도: O(1) — 권한 체크 + 승인 요청
  // LOCK 참조: L8 (RBAC 4단계), L9 (타임아웃)
  
  // 1. 상승 경로 유효성 검증
  // 명시적 허용 전이 테이블 (enum 정수 순서 비의존 — VIEWER→OPERATOR, OPERATOR→ADMIN만 허용)
  const VALID_ELEVATIONS: Partial<Record<RBACLevel, RBACLevel>> = {
    [RBACLevel.VIEWER]: RBACLevel.OPERATOR,
    [RBACLevel.OPERATOR]: RBACLevel.ADMIN,
  };
  if (VALID_ELEVATIONS[currentRole] !== targetRole) {
    throw new ForbiddenError('Only single-level elevation allowed');
  }
  if (targetRole === RBACLevel.OWNER) {
    throw new ForbiddenError('OWNER role cannot be elevated to');
  }
  
  // 2. 승인 요청 생성
  const approvalRequest = {
    id: crypto.randomUUID(),
    userId,
    currentRole,
    targetRole,
    traceId,
    requestedAt: new Date().toISOString(),
    expiresAt: new Date(Date.now() + 600_000).toISOString(), // L9: 10분
  };
  
  // 3. 승인 대기 (L9 타임아웃 연동)
  const result = await waitForApproval(approvalRequest, 600_000);
  
  // 4. 감사 로그
  logSecurityEvent('rbac.elevation', {
    traceId,
    userId,
    from: currentRole,
    to: targetRole,
    result: result.approved ? 'APPROVED' : 'DENIED',
  });
  
  return result;
}
```

---

## 5. Agent 권한 제어

### 5.1 Agent별 기본 레벨 할당

| Agent 유형 | 기본 RBAC 레벨 | 근거 |
|-----------|:-------------:|------|
| 보조 Agent (분석, 요약) | L1 Operator | 안전 작업만 수행 |
| 코드 실행 Agent | L1 Operator + Docker 격리 | L12 샌드박스 연동 |
| 시스템 관리 Agent | L2 Admin | 설정 변경 필요 시 |
| 자율 Agent (V2+ L2/L3) | L1 → Autonomy L14 게이팅 | L14 자율 운영 수준 연동 |

### 5.2 DEC-003 (L19) 연동

> LOCK (Part2 §6.5): DEC-003 도구 승인 Allowlist — 읽기전용=자동승인, 외부API/쓰기/코드실행=확인 필요

```
Agent 도구 호출
  → 1. Allowlist 조회 (L19)
  → 2. 도구 위험 등급 확인 (P0/P1/P2/P3)
  → 3. Agent RBAC 레벨 확인 (L8)
  → 4. 교차 검증:
       P0(안전) + L1 이상 → 자동 실행
       P1(일반) + L1 이상 → CONFIRM (사용자 확인)
       P2(위험) + L3 Owner → TIMEOUT 승인 (L9)
       P3(금지) → 항상 차단
  → 5. 실행 + 감사 로그
```

---

## 6. 로깅 포맷 (R-01-7)

```json
{
  "event": "security.rbac.access_check",
  "trace_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
  "timestamp": "2026-04-12T13:00:00Z",
  "error": {
    "code": "RBAC-DENY",
    "message": "Access denied: insufficient role level",
    "severity": "MEDIUM"
  },
  "context": {
    "user_id": "user-uuid",
    "role": "OPERATOR",
    "required_role": "ADMIN",
    "resource": "settings.update",
    "action": "WRITE"
  },
  "recovery": {
    "action": "request_denied",
    "elevation_hint": "Request role elevation to ADMIN",
    "retry_allowed": false
  }
}
```

---

## 7. 예외 처리 정책 표

| error_code | 설명 | recoverable | 처리 |
|-----------|------|:-----------:|------|
| RBAC-001 | 권한 부족 (접근 거부) | YES | 403 응답, 상승 안내 |
| RBAC-002 | 역할 정보 로딩 실패 | YES | 기본 L0(VIEWER) 폴백, P1 알림 |
| RBAC-003 | 권한 상승 타임아웃 | YES | 원래 역할 유지, 재요청 가능 |
| RBAC-004 | 잘못된 역할 값 | NO | 요청 거부, 감사 로그 |
| RBAC-005 | Agent RBAC 검증 실패 | NO | Agent 작업 차단, 감사 로그 |
| RBAC-006 | 임시 상승 만료 | YES | 자동 복귀, 사용자 알림 |

---

## 8. Phase 2 통합 테스트 시나리오

| # | 시나리오 | 예상 결과 |
|---|---------|----------|
| T-01 | VIEWER 역할로 Chat 입력 시도 | DENY — 입력 불가 |
| T-02 | OPERATOR 역할로 P0 도구 실행 | ALLOW — 자동 실행 |
| T-03 | OPERATOR 역할로 P2 도구 실행 시도 | DENY — 권한 부족 |
| T-04 | OPERATOR → ADMIN 상승 요청 → OWNER 승인 | 역할 변경 + 감사 로그 |
| T-05 | 상승 요청 600초 타임아웃 | 원래 역할 유지 (L9) |
| T-06 | ADMIN 역할로 Constitution 편집 시도 | DENY — OWNER만 가능 |
| T-07 | Agent가 Allowlist 외 도구 호출 시도 | 차단 (L19) |
| T-08 | 임시 상승 1시간 후 자동 복귀 | L1 Operator로 복귀 |
| T-09 | 권한 매트릭스 전체 경로 검증 (4×15) | 60개 경로 모두 정합 |
| T-10 | RBAC 모듈 장애 시 폴백 동작 | L0 VIEWER 폴백, P1 알림 |

---

## D2.0-07 §13 요구사항 대조

| D2.0-07 §13 요구사항 | 본 문서 반영 | 상태 |
|-------------------|------------|:----:|
| 4레벨 RBAC | §2 전체 | OK |
| OWNER 전체 권한 | §2.1 + §3 매트릭스 | OK |
| ADMIN Constitution/P2 제외 | §2.2 + §3 매트릭스 | OK |
| OPERATOR 허용목록 내 Tool | §5.2 DEC-003 연동 | OK |
| VIEWER 읽기 전용 | §2.4 + §3 매트릭스 | OK |
