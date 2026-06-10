# 브라우저 RPA 보안 정책 — L3 상세 명세

> **N-ID**: (보안) (NEW)
> **V단계**: V1
> **도메인**: 3-4_Workflow-RPA / 05_browser-rpa
> **정본**: sot 2/3-4_Workflow-RPA/05_browser-rpa/browser_security.md

---

## 1. 개요

브라우저 RPA 보안 정책은 05_browser-rpa 서브폴더 전체(N-011~N-016)에 적용되는 **통합 보안 프레임워크**이다. 샌드박스 실행 환경, 자격증명 AES-256 암호화, 파일시스템 접근 제한, 네트워크 정책, 감사 로깅을 정의하여 브라우저 자동화 과정에서의 보안 위협을 체계적으로 통제한다.

> LOCK (STEP7-N / 가이드 / LOCK-WF-10): 샌드박스 필수, 파일시스템 접근 제한, 자격증명 AES-256 암호화

---

## 2. 핵심 제약 (LOCK)

| # | LOCK 항목 | 값 |
|---|-----------|-----|
| LOCK-WF-10 | RPA 보안 정책 | 샌드박스 필수, 파일시스템 접근 제한, 자격증명 AES-256 암호화 |
| LOCK-WF-07 | 브라우저 액션 타입 | 10종 액션만 허용, 임의 시스템 명령 실행 차단 |

> LOCK (STEP7-N / 가이드 / LOCK-WF-10): 샌드박스 필수, 파일시스템 접근 제한, 자격증명 AES-256 암호화. 이하 전체 보안 정책은 이 LOCK 값을 세부 구현한 것이며, LOCK 값 자체를 재정의하지 않는다.

---

## 3. 보안 아키텍처 개요

```
[워크플로우 실행 요청]
    ↓
[보안 게이트웨이]
    ├─ 요청 검증 (사용자 권한, 워크플로우 서명)
    ├─ 자격증명 복호화 (AES-256 → 메모리 only)
    └─ 보안 정책 로딩
    ↓
[샌드박스 환경 생성]
    ├─ Playwright BrowserContext (격리)
    ├─ 파일시스템 제한 (chroot 상당)
    ├─ 네트워크 정책 적용 (도메인 화이트리스트)
    └─ 리소스 제한 (CPU/메모리/시간)
    ↓
[브라우저 액션 실행]
    ├─ 10종 액션만 허용 (LOCK-WF-07)
    ├─ 실시간 감사 로깅
    └─ 이상 행동 탐지
    ↓
[샌드박스 정리]
    ├─ 브라우저 컨텍스트 종료 (쿠키/캐시/세션 삭제)
    ├─ 메모리 내 자격증명 제로화
    └─ 임시 파일 삭제
```

---

## 4. 샌드박스 실행 환경

### 4.1 SandboxConfig

```typescript
interface BrowserSandboxConfig {
  // 파일시스템 격리
  filesystem: {
    root_dir: string;                  // "~/.vamos/sandbox/{execution_id}/"
    allowed_dirs: string[];            // 읽기/쓰기 허용 디렉터리
    max_disk_usage_mb: number;         // 최대 디스크 사용량 (기본 1024)
    blocked_extensions: string[];      // 차단 확장자 [".exe", ".bat", ".sh", ".ps1", ".dll", ".so"]
  };

  // 네트워크 정책
  network: {
    mode: "whitelist" | "blacklist" | "unrestricted";
    domain_list: string[];             // 화이트/블랙 리스트 도메인
    block_internal_ips: boolean;       // 내부 IP 차단 (기본 true, SSRF 방지)
    max_concurrent_connections: number; // 최대 동시 연결 (기본 10)
    max_request_size_mb: number;       // 최대 요청 크기 (기본 50)
    max_response_size_mb: number;      // 최대 응답 크기 (기본 100)
  };

  // 리소스 제한
  resources: {
    max_execution_time_sec: number;    // 최대 실행 시간 (기본 300)
    max_memory_mb: number;             // 최대 메모리 (기본 512)
    max_pages: number;                 // 최대 동시 탭 (기본 5)
    max_screenshots: number;           // 최대 스크린샷 수 (기본 50)
  };

  // 브라우저 격리
  browser: {
    headless: boolean;                 // 항상 true (프로덕션)
    disable_gpu: boolean;              // 기본 true
    disable_extensions: boolean;       // 기본 true
    disable_downloads_outside_sandbox: boolean;  // 기본 true
    block_popups: boolean;             // 기본 true
    block_notifications: boolean;      // 기본 true
  };
}
```

### 4.2 샌드박스 생명주기

| 단계 | 동작 | 실패 시 |
|------|------|---------|
| 생성 | 전용 디렉터리 생성, 정책 로딩, BrowserContext 초기화 | 실행 거부 |
| 실행 | 10종 액션 허용, 리소스 모니터링, 감사 로깅 | 리소스 초과 시 강제 종료 |
| 정리 | 쿠키/캐시 삭제, 임시 파일 제거, 메모리 제로화 | 강제 프로세스 kill + 디렉터리 삭제 |

### 4.3 파일시스템 접근 제어

| 경로 | 권한 | 용도 |
|------|------|------|
| `~/.vamos/sandbox/{execution_id}/` | 읽기/쓰기 | 실행 중 임시 파일 |
| `~/.vamos/downloads/` | 쓰기 전용 | 다운로드 파일 저장 |
| `~/.vamos/monitoring/snapshots/` | 쓰기 전용 | 모니터링 스냅샷 |
| 그 외 전체 | **차단** | — |

---

## 5. 자격증명 관리 (Credential Vault)

### 5.1 CredentialVault 스키마

```typescript
interface CredentialVault {
  storage_path: string;                // "~/.vamos/credentials/vault.enc"
  encryption: {
    algorithm: "AES-256-GCM";          // 암호화 알고리즘
    key_derivation: "PBKDF2";          // 키 유도 함수
    iterations: number;                // 기본 600000
    salt_length: number;               // 기본 32 바이트
  };
  master_key_source: "os_keychain" | "environment_variable" | "user_password";
}

interface StoredCredential {
  id: string;                          // 크리덴셜 ID (UUID)
  name: string;                        // 표시명 ("DART API 키")
  type: "api_key" | "login" | "oauth2" | "cookie" | "certificate";
  domain: string;                      // 연관 도메인
  encrypted_payload: string;           // AES-256-GCM 암호화된 데이터
  salt: string;                        // PBKDF2 솔트 (base64)
  iv: string;                          // 초기화 벡터
  auth_tag: string;                    // GCM 인증 태그
  created_at: string;
  last_used_at: string;
  expires_at?: string;                 // 만료 시각
  access_log_enabled: boolean;         // 접근 로그 기록 (기본 true)
}
```

### 5.2 자격증명 처리 규칙

| 규칙 | 설명 |
|------|------|
| 저장 | 평문 저장 절대 금지. AES-256-GCM으로 암호화 후 저장 |
| 복호화 | 실행 시점에만 메모리 내 복호화. 디스크에 평문 기록 금지 |
| 메모리 | 사용 후 즉시 제로화 (`memset(0)` / `SecureString`) |
| 로그 | 자격증명 값은 로그에서 자동 마스킹 (`***REDACTED***`) |
| 전송 | TLS 1.3+ 필수. HTTP 평문 전송 차단 |
| 만료 | OAuth 토큰 등 만료 시각 추적. 만료 전 자동 갱신 시도 |
| 삭제 | 삭제 시 파일 내용 덮어쓰기(0x00) 후 삭제 |

### 5.3 암호화/복호화 의사코드

```
function encrypt_credential(plaintext, master_key):
    salt = random_bytes(32)
    derived_key = PBKDF2(master_key, salt, iterations=600000, key_length=32)
    iv = random_bytes(12)  // GCM 권장 IV 크기
    ciphertext, auth_tag = AES_256_GCM_encrypt(derived_key, iv, plaintext)
    return StoredCredential(
        encrypted_payload=base64(ciphertext),
        iv=base64(iv),
        auth_tag=base64(auth_tag)
    )

function decrypt_credential(stored, master_key):
    derived_key = PBKDF2(master_key, stored.salt, iterations=600000, key_length=32)
    plaintext = AES_256_GCM_decrypt(
        derived_key, 
        base64_decode(stored.iv), 
        base64_decode(stored.encrypted_payload),
        base64_decode(stored.auth_tag)
    )
    return plaintext  // 메모리 내에서만 사용, 사용 후 즉시 제로화
```

---

## 6. 네트워크 보안 정책

### 6.1 도메인 정책

```typescript
interface NetworkPolicy {
  // SSRF 방지: 내부 IP 대역 차단
  blocked_ip_ranges: string[];
  // 기본 차단: 127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 169.254.0.0/16

  // TLS 필수
  require_tls: boolean;                // 기본 true (HTTP 차단)
  min_tls_version: "1.3";             // 기본 "1.3" (§5.2 자격증명 규칙 'TLS 1.3+ 필수' 정합)

  // 도메인 화이트리스트 (기본 모드)
  default_policy: "allow" | "deny";    // 기본 "deny" (화이트리스트 모드)
  allowed_domains: string[];           // 사용자가 등록한 허용 도메인
  
  // Rate Limiting (도메인별)
  per_domain_rps: Record<string, number>;  // 도메인별 초당 요청 제한
  global_rps: number;                  // 전체 초당 요청 제한 (기본 10)
}
```

### 6.2 콘텐츠 보안

| 항목 | 정책 |
|------|------|
| JavaScript 실행 | execute_js 액션으로만 허용, eval() 직접 호출 차단 |
| 파일 다운로드 | 허용 확장자 화이트리스트만 저장 (§7 참조) |
| 리다이렉트 | 최대 5회까지 허용, 화이트리스트 외 도메인 리다이렉트 차단 |
| 쿠키 | 세션 종료 시 전체 삭제, 제3자 쿠키 차단 |

---

## 7. 파일 보안 정책

### 7.1 허용/차단 파일 타입

| 카테고리 | 확장자 | 정책 |
|----------|--------|------|
| 문서 | pdf, docx, xlsx, csv, json, txt, xml, md, html | **허용** |
| 이미지 | png, jpg, jpeg, gif, svg, webp | **허용** |
| 압축 | zip, tar.gz, 7z | **허용** (내부 파일 재검사) |
| 실행 파일 | exe, bat, sh, ps1, cmd, com, msi | **차단** (즉시 삭제 + 경고) |
| 라이브러리 | dll, so, dylib | **차단** |
| 스크립트 | js, py, rb, php (독립 파일) | **차단** |

### 7.2 파일 검증 파이프라인

```
function validate_downloaded_file(file_path):
    // 1단계: 확장자 검사
    if extension(file_path) in BLOCKED_EXTENSIONS:
        delete(file_path)
        log_security_event("blocked_file_type", file_path)
        return REJECTED
    
    // 2단계: MIME 타입 실제 검사 (확장자 위변조 방지)
    actual_mime = detect_mime_type(file_path)  // magic bytes 기반
    if actual_mime != expected_mime_for_extension(file_path):
        delete(file_path)
        log_security_event("mime_mismatch", file_path, actual_mime)
        return REJECTED
    
    // 3단계: 파일 크기 검사
    if file_size(file_path) > MAX_FILE_SIZE:
        delete(file_path)
        return REJECTED
    
    // 4단계: 압축 파일 내부 검사
    if is_archive(file_path):
        for inner_file in list_archive(file_path):
            if extension(inner_file) in BLOCKED_EXTENSIONS:
                delete(file_path)
                log_security_event("blocked_archive_content", inner_file)
                return REJECTED
    
    return ACCEPTED
```

---

## 8. 감사 로깅

### 8.1 AuditLog 스키마

```typescript
interface BrowserAuditLog {
  id: string;                          // 로그 ID
  execution_id: string;                // 워크플로우 실행 ID
  workflow_id: string;
  user_id: string;
  timestamp: string;                   // ISO 8601
  event_type: AuditEventType;
  details: Record<string, any>;
  severity: "info" | "warning" | "critical";
}

type AuditEventType =
  | "sandbox_created"
  | "sandbox_destroyed"
  | "browser_action_executed"
  | "credential_accessed"
  | "credential_decrypted"
  | "file_downloaded"
  | "file_uploaded"
  | "file_blocked"
  | "network_request"
  | "network_blocked"
  | "resource_limit_warning"
  | "resource_limit_exceeded"
  | "security_violation"
  | "human_escalation";
```

### 8.2 로깅 규칙

| 이벤트 | 심각도 | 기록 항목 |
|--------|--------|----------|
| 액션 실행 | info | 액션 타입, URL, 선택자 (값 마스킹) |
| 자격증명 접근 | warning | 크리덴셜 ID, 접근 시각 (값 미기록) |
| 파일 다운로드 | info | 파일명, 크기, URL |
| 파일 차단 | critical | 파일명, 차단 사유, MIME 타입 |
| 네트워크 차단 | warning | 대상 URL, 차단 사유 |
| 리소스 초과 | critical | 리소스 유형, 한도, 실제 사용량 |
| 보안 위반 | critical | 위반 유형, 상세 컨텍스트 |

### 8.3 로그 보관

| 항목 | 값 |
|------|-----|
| 보관 기간 | 90일 |
| 저장 위치 | `~/.vamos/logs/browser_audit/` |
| 포맷 | JSON Lines (.jsonl) |
| 로테이션 | 일별 로테이션, gzip 압축 |

---

## 9. 이상 행동 탐지

### 9.1 탐지 규칙

| 규칙 | 조건 | 동작 |
|------|------|------|
| 과도한 요청 | 단일 도메인 10 rps 초과 | Rate Limit 적용 + 경고 |
| 대량 다운로드 | 1시간 내 100파일 또는 1GB 초과 | 일시정지 + 사용자 확인 |
| 비정상 리다이렉트 | 화이트리스트 외 도메인 리다이렉트 | 차단 + 경고 |
| 세션 탈취 시도 | 크리덴셜 사용 후 비정상 도메인 접근 | 즉시 종료 + critical 로그 |
| 장시간 실행 | max_execution_time 80% 도달 | 경고 알림 |
| 메모리 누수 | 메모리 사용량 지속 증가 | 500MB 초과 시 강제 종료 |

---

## 10. 보안 정책 적용 대상 매핑

| 모듈 | 적용 보안 정책 |
|------|--------------|
| browser_agent.md (N-011) | 샌드박스, 자격증명, 네트워크, 감사 로깅 전체 |
| web_scraping.md (N-012) | 샌드박스, Rate Limiting, robots.txt, 감사 로깅 |
| web_monitoring.md (N-013) | 샌드박스, 스냅샷 암호화, 네트워크 정책 |
| form_autofill.md (N-014) | 샌드박스, 자격증명(프로필 AES-256), 민감 정보 차단 |
| file_download_upload.md (N-015) | 샌드박스, 파일 검증, 허용/차단 확장자, 크기 제한 |
| nocode_api.md (N-016) | 자격증명(API 키 AES-256), 네트워크 정책, TLS 필수 |

---

## 11. REST API

```
GET    /api/v1/security/policy                   // 현재 보안 정책 조회
PUT    /api/v1/security/policy                   // 보안 정책 업데이트
GET    /api/v1/security/audit-logs               // 감사 로그 조회 (필터: 기간, 심각도, 이벤트 타입)
GET    /api/v1/security/audit-logs/:id           // 감사 로그 상세
GET    /api/v1/security/credentials              // 크리덴셜 목록 (메타데이터만, 값 미노출)
POST   /api/v1/security/credentials              // 크리덴셜 등록
DELETE /api/v1/security/credentials/:id          // 크리덴셜 삭제 (안전 삭제)
GET    /api/v1/security/sandbox/:id/status       // 샌드박스 상태 조회
DELETE /api/v1/security/sandbox/:id              // 샌드박스 강제 종료
GET    /api/v1/security/network/whitelist        // 도메인 화이트리스트 조회
PUT    /api/v1/security/network/whitelist        // 도메인 화이트리스트 수정
```

---

## 12. 교차참조

| 참조 모듈 | 연관 항목 | 참조 방향 |
|----------|---------|----------|
| browser_agent.md (N-011) | 샌드박스 실행 환경 | → 제공 |
| web_scraping.md (N-012) | Rate Limiting, robots.txt | → 제공 |
| web_monitoring.md (N-013) | 스냅샷 보안 | → 제공 |
| form_autofill.md (N-014) | 프로필 데이터 암호화 | → 제공 |
| file_download_upload.md (N-015) | 파일 검증/차단 정책 | → 제공 |
| nocode_api.md (N-016) | API 키 암호화 | → 제공 |
| 06_desktop-rpa/rpa_security_sandbox.md | 데스크톱 RPA 보안 (상위 통합) | ↔ 공유 |

---

*끝 — browser_security.md L3 v1.0*
