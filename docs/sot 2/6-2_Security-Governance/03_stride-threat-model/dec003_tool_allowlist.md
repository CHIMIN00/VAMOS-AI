# DEC-003 도구 승인 Allowlist 상세 명세

> **Phase**: 1 (V1)
> **§7.3 항목**: #11 "DEC-003 도구 승인 Allowlist"
> **세션**: P1-1
> **작성일**: 2026-04-12
> **상태**: DRAFT

---

## 교차 참조 블록

| 정본 문서 | 섹션 | 참조 내용 |
|----------|------|----------|
| Part2 구현가이드 | §6.5 #15 | DEC-003 Allowlist 구현 지침 |
| D2.0-07 | DEC-003 | 도구 승인 정책 |
| AUTHORITY_CHAIN.md | §5 L19 | DEC-003 도구 승인 LOCK |
| AUTHORITY_CHAIN.md | §5 L8 | RBAC 4단계 LOCK (연동) |
| AUTHORITY_CHAIN.md | §5 L9 | 승인 타임아웃 LOCK (연동) |
| 03_stride-threat-model/_index.md | §C | Tool 실행 권한 항목 |
| rbac_4level.md | §5.2 | RBAC-DEC-003 교차 검증 |
| approval_timeout_10min.md | §2 | P2 도구 승인 타임아웃 연동 |

---

## 1. LOCK L19 교차 검증

> LOCK (Part2 §6.5): DEC-003 도구 승인 Allowlist — 읽기전용=자동승인, 외부API/쓰기/코드실행=확인 필요

| 검증 항목 | LOCK L19 값 | 본 문서 | 일치 |
|----------|-----------|--------|:----:|
| 읽기전용 | 자동승인 | §3 P0 등급 | OK |
| 외부API/쓰기/코드실행 | 확인 필요 | §3 P1/P2 등급 | OK |

---

## 2. Allowlist 구조 설계

### 2.1 JSON 스키마

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "version": { "type": "string", "pattern": "^v\\d+\\.\\d+$" },
    "updated_at": { "type": "string", "format": "date-time" },
    "updated_by": { "type": "string" },
    "tools": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["tool_id", "name", "risk_level", "allowed_roles"],
        "properties": {
          "tool_id": {
            "type": "string",
            "description": "고유 도구 식별자",
            "pattern": "^tool-[a-z0-9-]+$"
          },
          "name": {
            "type": "string",
            "maxLength": 128
          },
          "description": {
            "type": "string",
            "maxLength": 512
          },
          "risk_level": {
            "type": "string",
            "enum": ["P0", "P1", "P2", "P3"]
          },
          "allowed_roles": {
            "type": "array",
            "items": {
              "type": "string",
              "enum": ["OWNER", "ADMIN", "OPERATOR"]
            }
          },
          "max_calls_per_session": {
            "type": "integer",
            "minimum": 1,
            "maximum": 1000,
            "default": 100
          },
          "requires_confirmation": {
            "type": "boolean"
          },
          "timeout_override_ms": {
            "type": "integer",
            "description": "P2 전용: 승인 타임아웃 오버라이드 (최대 600000)"
          },
          "tags": {
            "type": "array",
            "items": { "type": "string" }
          }
        }
      }
    }
  }
}
```

### 2.2 Allowlist 예시

```json
{
  "version": "v1.0",
  "updated_at": "2026-04-12T00:00:00Z",
  "updated_by": "OWNER:system-admin",
  "tools": [
    {
      "tool_id": "tool-file-read",
      "name": "File Read",
      "description": "로컬 파일 읽기 (프로젝트 스코프 내)",
      "risk_level": "P0",
      "allowed_roles": ["OWNER", "ADMIN", "OPERATOR"],
      "max_calls_per_session": 500,
      "requires_confirmation": false,
      "tags": ["filesystem", "read-only"]
    },
    {
      "tool_id": "tool-web-search",
      "name": "Web Search",
      "description": "외부 웹 검색 API 호출",
      "risk_level": "P1",
      "allowed_roles": ["OWNER", "ADMIN", "OPERATOR"],
      "max_calls_per_session": 50,
      "requires_confirmation": true,
      "tags": ["external-api", "search"]
    },
    {
      "tool_id": "tool-code-execute",
      "name": "Code Execute",
      "description": "Docker 샌드박스 내 코드 실행",
      "risk_level": "P2",
      "allowed_roles": ["OWNER", "ADMIN"],
      "max_calls_per_session": 20,
      "requires_confirmation": true,
      "timeout_override_ms": 300000,
      "tags": ["code-execution", "sandbox"]
    },
    {
      "tool_id": "tool-system-modify",
      "name": "System Modify",
      "description": "시스템 설정 변경 (금지)",
      "risk_level": "P3",
      "allowed_roles": [],
      "requires_confirmation": false,
      "tags": ["system", "blocked"]
    }
  ]
}
```

### 2.3 저장 위치 및 로딩

| 항목 | 값 |
|------|-----|
| **저장 위치** | `<project-root>/config/tool_allowlist.json` |
| **로딩 시점** | 앱 시작 시 + 핫 리로드 지원 (파일 감시) |
| **캐시** | 메모리 캐시, 파일 변경 시 자동 갱신 |
| **검증** | JSON 스키마 검증 후 로딩 (스키마 불일치 시 거부) |

---

## 3. 도구 분류 체계

| 등급 | 분류 | 승인 방식 | RBAC 최소 레벨 | 예시 |
|------|------|---------|:-------------:|------|
| **P0** (안전) | 읽기전용 | 자동 승인 (L19) | L1 Operator | 파일 읽기, 검색, 조회 |
| **P1** (일반) | 외부 API, 일반 쓰기 | 사용자 확인 (CONFIRM) | L1 Operator | 웹 검색, 파일 생성 |
| **P2** (위험) | 코드 실행, 시스템 변경 | 명시적 승인 + 타임아웃 (L9) | L2 Admin | 코드 실행, DB 변경 |
| **P3** (금지) | 시스템 파괴, 네트워크 공격 | 실행 차단 (절대) | — (차단) | 시스템 삭제, 네트워크 스캔 |

---

## 4. 실행 시 검증 흐름

```
[Agent 도구 호출 요청]
  → 1. Allowlist 조회
    ├─ [미등록 도구] → 즉시 차단 + 감사 로그
    └─ [등록 도구]
  → 2. 위험 등급 확인
    ├─ P3 → 즉시 차단
    └─ P0/P1/P2
  → 3. RBAC 권한 확인 (L8 연동)
    ├─ [권한 부족] → 403 + 상승 안내
    └─ [권한 충족]
  → 4. 세션 호출 횟수 확인
    ├─ [max_calls_per_session 초과] → 차단 + 알림
    └─ [한도 내]
  → 5. 승인 처리
    ├─ P0 → 자동 실행
    ├─ P1 → CONFIRM (사용자 확인 대기)
    └─ P2 → TIMEOUT 승인 (L9: 5분/10분)
  → 6. 실행 + 결과 반환
  → 7. 감사 로그 기록
```

### 4.1 검증 의사코드

```typescript
async function validateToolCall(
  agentId: string,
  toolId: string,
  userRole: RBACLevel,
  sessionId: string,
  traceId: string
): Promise<ToolCallResult> {
  // 시간복잡도: O(n) — n=Allowlist 도구 수 (Map 사용 시 O(1))
  // LOCK 참조: L19 (DEC-003), L8 (RBAC), L9 (타임아웃)
  
  // 1. Allowlist 조회
  const tool = allowlistMap.get(toolId);
  if (!tool) {
    logSecurityEvent('tool_not_in_allowlist', { toolId, traceId });
    throw new ForbiddenError('Tool not in allowlist');
  }
  
  // 2. P3 즉시 차단
  if (tool.risk_level === 'P3') {
    logSecurityEvent('tool_blocked_p3', { toolId, traceId });
    throw new ForbiddenError('Tool is permanently blocked');
  }
  
  // 3. RBAC 권한 확인 (L8)
  if (!tool.allowed_roles.includes(userRole)) {
    throw new ForbiddenError(`Role ${userRole} not allowed for ${toolId}`);
  }
  
  // 4. 세션 호출 횟수 확인
  const callCount = getSessionCallCount(sessionId, toolId);
  if (callCount >= tool.max_calls_per_session) {
    throw new RateLimitError(`Max calls exceeded for ${toolId}`);
  }
  
  // 5. 승인 처리
  switch (tool.risk_level) {
    case 'P0':
      return { approved: true, method: 'auto' };
    case 'P1':
      return await requestConfirmation(tool, traceId);
    case 'P2':
      return await requestTimedApproval(tool, traceId,
        tool.timeout_override_ms || 300_000); // L9: 5분 기본
  }
}
```

---

## 5. Allowlist 변경 거버넌스

### 5.1 변경 절차

```
[변경 요청]
  → 요청자: 최소 L1 Operator
  → 승인자: L2 Admin 이상
  → 변경 내용 검토: 도구 추가/제거/등급 변경
  → 승인 → Allowlist JSON 갱신
  → CONFLICT_LOG 기록 (도구 등급 변경 시)
  → 핫 리로드 → 즉시 적용
  → 감사 로그
```

### 5.2 변경 권한

| 변경 유형 | 필요 권한 | CONFLICT_LOG |
|----------|---------|:------------:|
| P0 도구 추가 | L2 Admin | 불필요 |
| P1 도구 추가 | L2 Admin | 불필요 |
| P2 도구 추가 | L3 Owner | 필요 |
| P3→P2 등급 변경 (차단 해제) | L3 Owner | 필요 |
| 도구 제거 | L2 Admin | 불필요 |
| max_calls 변경 | L2 Admin | 불필요 |

---

## 6. 로깅 포맷 (R-01-7)

```json
{
  "event": "security.tool_allowlist.validation",
  "trace_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
  "timestamp": "2026-04-12T13:00:00Z",
  "error": {
    "code": "DEC-003-DENY",
    "message": "Tool not in allowlist",
    "severity": "HIGH"
  },
  "context": {
    "tool_id": "tool-unknown",
    "agent_id": "agent-uuid",
    "user_role": "OPERATOR",
    "risk_level": null,
    "session_call_count": 0,
    "allowlist_version": "v1.0"
  },
  "recovery": {
    "action": "tool_blocked",
    "retry_allowed": false,
    "escalation": "ADMIN approval needed to add tool"
  }
}
```

---

## 7. 예외 처리 정책 표

| error_code | 설명 | recoverable | 처리 |
|-----------|------|:-----------:|------|
| DEC-001 | 도구 미등록 (Allowlist 외) | NO | 차단 + 등록 요청 안내 |
| DEC-002 | P3 도구 실행 시도 | NO | 즉시 차단 + 감사 로그 |
| DEC-003 | RBAC 권한 부족 | YES | 403 + 역할 상승 안내 |
| DEC-004 | 세션 호출 한도 초과 | YES | 차단 + 새 세션 안내 |
| DEC-005 | Allowlist 파일 로딩 실패 | NO | 모든 도구 차단 (안전 모드), P0 알림 |
| DEC-006 | Allowlist 스키마 불일치 | NO | 이전 버전 유지, P1 알림 |
| DEC-007 | P2 승인 타임아웃 | YES | 자동 거부 (L9) |

---

## 8. Phase 2 통합 테스트 시나리오

| # | 시나리오 | 예상 결과 |
|---|---------|----------|
| T-01 | P0 도구(파일 읽기) OPERATOR가 호출 | 자동 실행 (L19) |
| T-02 | P1 도구(웹 검색) 사용자 확인 후 실행 | CONFIRM → 실행 |
| T-03 | P2 도구(코드 실행) OPERATOR 호출 시도 | RBAC 거부 (ADMIN 필요) |
| T-04 | P3 도구 호출 시도 | 즉시 차단 |
| T-05 | 미등록 도구 호출 시도 | DEC-001 차단 |
| T-06 | max_calls_per_session 초과 시 | DEC-004 차단 |
| T-07 | Allowlist 핫 리로드 후 신규 도구 즉시 사용 | 정상 동작 |
| T-08 | Allowlist JSON 스키마 불일치 파일 로딩 | 이전 버전 유지 |
| T-09 | P2 도구 승인 5분 타임아웃 | 자동 거부 (L9) |
| T-10 | Allowlist 파일 삭제 시 안전 모드 | 모든 도구 차단, P0 알림 |
| T-11 | ADMIN이 P0 도구 추가 → 즉시 사용 가능 | Allowlist 갱신 + 핫 리로드 |
| T-12 | OPERATOR가 P3→P2 등급 변경 시도 | 거부 (OWNER 필요) |
