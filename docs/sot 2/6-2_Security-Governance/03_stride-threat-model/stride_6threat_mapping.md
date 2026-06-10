# STRIDE 기본 매핑 6대 위협 상세 명세

> **Phase**: 1 (V1)
> **§7.3 항목**: #12 "STRIDE 기본 매핑 (6대 위협)"
> **세션**: P1-1
> **작성일**: 2026-04-12
> **상태**: DRAFT
> **ISS-4 해결**: STRIDE 매핑 9-State 한정 → MCP/Agent/RAG 확장 완료

---

## 교차 참조 블록

| 정본 문서 | 섹션 | 참조 내용 |
|----------|------|----------|
| Part2 구현가이드 | §6.5.3 | STRIDE 위협 모델 매핑 (정본) |
| D2.0-07 | §2.2A | STRIDE/Attack Tree/OWASP 통합 |
| AUTHORITY_CHAIN.md | §5 L2 | STRIDE 6대 위협 분류 LOCK |
| 03_stride-threat-model/_index.md | §A, §B | STRIDE 6대 위협 + 확장 공격 표면 |
| STEP7-E | S7E-001 (STRIDE 위협 모델링, CRITICAL, V1) | STRIDE 요구사항 |

---

## 1. LOCK L2 교차 검증

> LOCK (Part2 §6.5.3): Spoofing(위장)→JWT+RBAC 레벨 검증, trace_id 서버 생성 / Tampering(변조)→HMAC 서명, 체크포인트 해시 검증 / Repudiation(부인)→audit_log에 승인 이벤트+타임스탬프+user_id 기록, 600초 승인 기록 보존 / Information Disclosure(정보유출)→`--network=none`, read-only 마운트, 30초 타임아웃 / Denial of Service(서비스거부)→Cost Gate 일일 한도(V2: ₩93,000), rate limiting(10 req/min) / Elevation of Privilege(권한상승)→NEVER_AUTO 정책(P1 이상 자동승인 금지), Gate 순서 강제

| 검증 항목 | LOCK L2 값 | 본 문서 | 일치 |
|----------|-----------|--------|:----:|
| 6대 위협 | S/T/R/I/D/E | §2 전체 | OK |
| Spoofing 통제 | JWT+RBAC, trace_id | §2.1 | OK |
| Tampering 통제 | HMAC 서명, 체크포인트 | §2.2 | OK |
| Repudiation 통제 | audit_log, 600초 보존 | §2.3 | OK |
| Info Disclosure 통제 | --network=none, 30초 | §2.4 | OK |
| DoS 통제 | Cost Gate, rate limiting | §2.5 | OK |
| Elevation 통제 | NEVER_AUTO, Gate 순서 | §2.6 | OK |

---

## 2. STRIDE 6대 위협 상세 매핑

### 2.1 Spoofing (위장)

| 항목 | 내용 |
|------|------|
| **정의** | 공격자가 다른 사용자/Agent/시스템으로 위장하여 인증 우회 |
| **대상 컴포넌트** | S0 Intake, API Gateway, Agent 통신 |
| **위협 시나리오** | (1) 악성 사용자가 다른 user_id로 요청 위장 (2) Agent 간 통신에서 Agent ID 위조 (3) MCP Tool description에서 악성 지시 삽입 (Tool Poisoning) |
| **대응 통제** | JWT + RBAC 레벨 검증 (L8), trace_id 서버 생성 (L18), HMAC Agent 인증 (L3, V2) |
| **LOCK 참조** | L8 (RBAC), L18 (trace_id), L3 (HMAC) |
| **관련 산출물** | rbac_4level.md, api_key_management.md |

### 2.2 Tampering (변조)

| 항목 | 내용 |
|------|------|
| **정의** | 전송 중 데이터(계획, 코드, 메시지)가 무단 변조 |
| **대상 컴포넌트** | S2 Plan, S4 Execute, Agent MessageBus |
| **위협 시나리오** | (1) AI 생성 계획/코드가 전송 중 변조 (2) MCP 도구 파라미터 변조 (3) RAG 임베딩 인덱스 오염 |
| **대응 통제** | HMAC-SHA256 서명 (L3), 체크포인트 해시 검증, 상수 시간 비교 (R-62-4) |
| **LOCK 참조** | L3 (HMAC), L4 (키 32바이트), L5 (순환 90일), L6 (리플레이 5분) |
| **관련 산출물** | 02_hmac-timing-defense/_index.md |

### 2.3 Repudiation (부인)

| 항목 | 내용 |
|------|------|
| **정의** | 사용자/Agent가 수행한 작업(승인, 실행)을 부인 |
| **대상 컴포넌트** | S3a Approve Wait, 5-Gate System |
| **위협 시나리오** | (1) 사용자가 위험 작업 승인 사실 부인 (2) Agent가 도구 실행 사실 부인 |
| **대응 통제** | audit_log에 승인 이벤트 + 타임스탬프 + user_id 기록, 600초 승인 기록 보존, append-only 로그 |
| **LOCK 참조** | L9 (승인 타임아웃 600초), L18 (trace_id) |
| **관련 산출물** | approval_timeout_10min.md |

### 2.4 Information Disclosure (정보유출)

| 항목 | 내용 |
|------|------|
| **정의** | 민감 정보(PII, API 키, 내부 경로)가 무단 노출 |
| **대상 컴포넌트** | S4 Execute (E-4 Sandbox), LLM 출력, 로그 |
| **위협 시나리오** | (1) Docker 샌드박스에서 호스트 파일시스템 접근 (2) LLM 출력에 PII 유출 (3) 에러 메시지에 스택 트레이스 노출 (4) RAG 문서 무단 유출 |
| **대응 통제** | `--network=none` (L12), 호스트 민감 경로 bind mount 부재 + seccomp/AppArmor 경로 탈출 차단 (read-only는 쓰기만 차단, 내부 파일 읽기 미차단), 30초 타임아웃 (L12), PII 마스킹, 에러 균일화 (CK-07) |
| **LOCK 참조** | L12 (Docker 30초 --network=none), L18 (trace_id) |
| **관련 산출물** | docker_sandbox.md, pii_regex_masking.md |

### 2.5 Denial of Service (서비스거부)

| 항목 | 내용 |
|------|------|
| **정의** | 대량 요청으로 API 비용 폭주 또는 서비스 마비 |
| **대상 컴포넌트** | S1 Route, Cost Gate, API Gateway |
| **위협 시나리오** | (1) 대량 LLM API 호출로 일일 비용 한도 초과 (2) Fork bomb/무한 루프로 리소스 고갈 (3) 대량 MCP 도구 호출 |
| **대응 통제** | Cost Gate 일일 한도 (L17: V2 ₩93,000), rate limiting (L16: 10 req/min), Docker 리소스 제한, max_calls_per_session (DEC-003) |
| **LOCK 참조** | L16 (Rate Limiting), L17 (Cost Gate) |
| **관련 산출물** | dec003_tool_allowlist.md, api_key_management.md §5 |

### 2.6 Elevation of Privilege (권한상승)

| 항목 | 내용 |
|------|------|
| **정의** | 일반 사용자/Agent가 상위 권한 획득 또는 Gate 우회 |
| **대상 컴포넌트** | 5-Gate System, RBAC, Autonomy Level |
| **위협 시나리오** | (1) OPERATOR가 ADMIN Gate 우회 (2) Agent가 자율성 레벨 자체 상승 (3) auto_approve 로직으로 승인 우회 |
| **대응 통제** | NEVER_AUTO 정책 (L20), Gate 순서 강제 (L11: Policy→Approval→Cost→Evidence→SelfCheck), RBAC 4레벨 (L8), Autonomy 게이팅 (L14) |
| **LOCK 참조** | L8 (RBAC), L11 (5-Gate), L14 (자율 운영), L20 (NEVER_AUTO) |
| **관련 산출물** | rbac_4level.md, approval_timeout_10min.md |

---

## 3. 위협별 통제 매트릭스 (6×5)

### 6대 위협 × 5개 공격 표면

| STRIDE | 9-State Pipeline | MCP Tool 호출 | Agent 통신 | RAG Pipeline | 외부 API |
|--------|:----------------:|:-------------:|:----------:|:------------:|:--------:|
| **S** Spoofing | JWT+RBAC (L8) | 서명 검증 (L19) | HMAC 인증 (L3) | 태깅 검증 | API Key (S7E-005) |
| **T** Tampering | 체크포인트 해시 | 파라미터 검증 | HMAC-SHA256 (L3) | 임베딩 무결성 | TLS 1.3 |
| **R** Repudiation | audit_log 600초 | 도구 호출 로그 | 메시지 서명 기록 | 검색 이력 기록 | 요청/응답 로그 |
| **I** Info Disc. | Docker 격리 (L12) | 출력 필터링 | 데이터 경계 | 문서 접근 제어 | PII 마스킹 |
| **D** DoS | Cost Gate (L17) | max_calls 제한 | 메시지 rate limit | 검색 횟수 제한 | rate limiting (L16) |
| **E** Elevation | NEVER_AUTO (L20) | DEC-003 (L19) | Autonomy (L14) | RBAC 접근 제어 | 5-Gate (L11) |

---

## 4. 확장 공격 표면 상세 (ISS-4 해결)

### 4.1 MCP Tool 호출 채널

| STRIDE | 위협 시나리오 | 통제 수단 | 검증 방법 |
|--------|-------------|----------|----------|
| Spoofing | Tool description에 숨겨진 악성 지시 (Tool Poisoning) | 화이트리스트 + 서명 검증 (S7E-015), DEC-003 Allowlist (L19) | 등록 시 description 수동 검토 |
| Elevation | 읽기전용 도구가 쓰기 작업 수행 | risk_level 재검증, 런타임 행동 모니터링 | 호출 결과 감사 |

### 4.2 Agent 간 통신

| STRIDE | 위협 시나리오 | 통제 수단 | 검증 방법 |
|--------|-------------|----------|----------|
| Tampering | BLUE NODE ↔ ORANGE CORE 메시지 변조 | HMAC-SHA256 서명 (L3), mutual 인증 (S7E-078) | 메시지 서명 검증 테스트 |
| Repudiation | Agent가 메시지 전송 부인 | 메시지 서명 + 타임스탬프 + Agent ID 기록 | 감사 로그 검토 |

### 4.3 RAG 파이프라인

| STRIDE | 위협 시나리오 | 통제 수단 | 검증 방법 |
|--------|-------------|----------|----------|
| Tampering | RAG 인덱스 오염 (임베딩 변조) | 임베딩 해시 무결성 검증, 인덱스 버전 관리 | 정기 무결성 스캔 |
| Info Disclosure | 검색 결과 조작을 통한 간접 주입 | 외부 콘텐츠 태깅 `[EXTERNAL_CONTENT]` (S7E-014), 출력 검증 (L2) | 태깅 검증 테스트 |

---

## 5. Attack Tree 연동 (D2.0-07 §2.2A)

```
STRIDE 매핑 ←→ Attack Tree 교차 참조
├── Spoofing
│   ├── AT: API Key 탈취 → S: API Key 위장 접근
│   └── AT: MCP Server 위조 → S: Tool Poisoning
├── Tampering
│   ├── AT: Memory 오염 → T: 대화 컨텍스트 변조
│   └── AT: RAG 인덱스 오염 → T: 검색 결과 조작
├── Repudiation
│   └── AT: (대응) → R: 모든 AT 경로에 audit_log 필수
├── Information Disclosure
│   ├── AT: PII 추출 시도 → I: LLM 출력 PII 유출
│   └── AT: 로컬 DB 무단 접근 → I: SQLCipher 미적용 시 유출
├── Denial of Service
│   ├── AT: 과도한 API 소비 → D: Cost Gate 우회 시도
│   └── AT: (확장) → D: Fork bomb (Docker)
└── Elevation of Privilege
    ├── AT: Jailbreak → E: Guardrails 우회
    └── AT: Delegation Attack → E: Agent 권한 탈취
```

---

## 6. 위협별 테스트 시나리오

| # | STRIDE | 테스트 시나리오 | 예상 결과 |
|---|--------|-------------|----------|
| T-01 | **S** Spoofing | 위조 JWT로 인증 시도 | 인증 실패, 401 반환 |
| T-02 | **S** Spoofing | 클라이언트 trace_id 주입 시도 | 무시, 서버 trace_id 사용 (L18) |
| T-03 | **T** Tampering | HMAC 서명 없이 Agent 메시지 전송 | 메시지 거부 (L3) |
| T-04 | **T** Tampering | 체크포인트 해시 불일치 메시지 | 변조 감지, 처리 거부 |
| T-05 | **R** Repudiation | 승인 후 audit_log에서 기록 확인 | 타임스탬프+user_id+action 기록 |
| T-06 | **R** Repudiation | 600초 경과 후 승인 기록 보존 확인 | 기록 유지 확인 |
| T-07 | **I** Info Disc. | Docker 컨테이너에서 /etc/passwd 읽기 시도 | --read-only 차단 |
| T-08 | **I** Info Disc. | LLM 출력에 API 키 포함 | L2 Guardrails AI 마스킹 |
| T-09 | **D** DoS | 10 req/min 초과 요청 전송 | rate limiting 차단 (L16) |
| T-10 | **D** DoS | 일일 비용 한도 초과 API 호출 | Cost Gate 차단 (L17) |
| T-11 | **E** Elevation | OPERATOR가 ADMIN API 직접 호출 | RBAC 차단 (L8) |
| T-12 | **E** Elevation | auto_approve=true 설정 시도 | NEVER_AUTO 차단 (L20) |
| T-13 | **S** MCP | 미등록 MCP Tool 호출 시도 | DEC-003 차단 (L19) |
| T-14 | **T** RAG | 오염된 임베딩으로 RAG 검색 | 외부 콘텐츠 태깅 확인 |

---

## 7. 로깅 포맷 (R-01-7)

```json
{
  "event": "security.stride.threat_detected",
  "trace_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
  "timestamp": "2026-04-12T13:00:00Z",
  "error": {
    "code": "STRIDE-S-001",
    "message": "Spoofing attempt: invalid JWT",
    "severity": "CRITICAL"
  },
  "context": {
    "stride_category": "Spoofing",
    "attack_surface": "API_Gateway",
    "control_applied": "JWT_RBAC_VERIFICATION",
    "user_id": "unknown",
    "request_origin": "external",
    "lock_references": ["L8", "L18"]
  },
  "recovery": {
    "action": "request_rejected",
    "retry_allowed": false,
    "escalation": "P1 security team"
  }
}
```

---

## 8. 예외 처리 정책 표

| error_code | 설명 | recoverable | 처리 |
|-----------|------|:-----------:|------|
| STRIDE-S-001 | Spoofing: JWT/인증 실패 | NO | 401 반환, 감사 로그 |
| STRIDE-T-001 | Tampering: HMAC 서명 불일치 | NO | 메시지 거부, P1 알림 |
| STRIDE-R-001 | Repudiation: 감사 로그 기록 실패 | YES | 재시도 + 버퍼 로그 |
| STRIDE-I-001 | Info Disclosure: PII 유출 탐지 | YES | 마스킹 후 반환 |
| STRIDE-D-001 | DoS: Rate limit 초과 | YES | 429 반환, 대기 후 재시도 |
| STRIDE-E-001 | Elevation: 권한 상승 시도 | NO | 403 반환, 감사 로그, 알림 |
| STRIDE-GEN | 미분류 보안 이벤트 | YES | 감사 로그 + 분석 큐 |

---

## 9. _index.md 정합성 확인

| _index.md 섹션 | 본 문서 매핑 | 정합 |
|---------------|------------|:----:|
| §A STRIDE 6대 위협 매핑 | §2 전체 (6대 위협 × 통제) | OK |
| §B 확장 공격 표면 (MCP/Agent/RAG) | §4 확장 공격 표면 (ISS-4) | OK |
| §C 인증/인가/접근제어 | rbac_4level.md 연동 | OK |
| §D Attack Tree | §5 Attack Tree 연동 | OK |

---

## D2.0-07 §2.2A 요구사항 대조

| D2.0-07 §2.2A 요구사항 | 본 문서 반영 | 상태 |
|-----------------------|------------|:----:|
| STRIDE 기반 위협 모델링 | §2 전체 | OK |
| Attack Tree 구조 | §5 Attack Tree 연동 | OK |
| OWASP 통합 매핑 | §3 통제 매트릭스 내 OWASP 연동 포인터 | OK |
| 5개 공격 표면 확장 (ISS-4) | §3 6×5 매트릭스 + §4 상세 | OK |
