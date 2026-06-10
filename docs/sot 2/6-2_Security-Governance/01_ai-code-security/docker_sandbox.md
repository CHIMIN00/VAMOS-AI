# Docker 샌드박스 상세 명세

> **Phase**: 1 (V1)
> **§7.3 항목**: #7 "Docker 샌드박스"
> **세션**: P1-1
> **작성일**: 2026-04-12
> **상태**: DRAFT

---

## 교차 참조 블록

| 정본 문서 | 섹션 | 참조 내용 |
|----------|------|----------|
| Part2 구현가이드 | §6.5 #8 | Docker 샌드박스 구현 지침 |
| STEP7-E | S7E-019 (Agent Sandboxing, HIGH, V2) | 코드 실행 격리 요구사항 |
| AUTHORITY_CHAIN.md | §5 L12 | Docker 30초 + `--network=none` LOCK |
| 01_ai-code-security/_index.md | §A CK-04 | 체크리스트 연결 |

---

## 1. LOCK L12 교차 검증

> LOCK (Part2 §6.5.1): E-4 Code Executor 실행 시 `--network=none` 확인. 30초 타임아웃 필수

| 검증 항목 | LOCK L12 값 | 본 문서 | 일치 |
|----------|-----------|--------|:----:|
| 네트워크 차단 | `--network=none` | §2 Docker 실행 명령 | OK |
| 타임아웃 | 30초 | §3 타임아웃 메커니즘 | OK |

---

## 2. Docker 실행 환경 설계

### 2.1 베이스 이미지

```dockerfile
# Dockerfile.sandbox — 최소 Alpine 기반
FROM alpine:3.19 AS sandbox-base

# 최소 실행 환경만 설치
RUN apk add --no-cache python3 py3-pip nodejs npm && \
    rm -rf /var/cache/apk/*

# 비특권 사용자 생성
RUN adduser -D -s /bin/sh sandboxuser
USER sandboxuser

WORKDIR /sandbox
```

### 2.2 Docker 실행 명령 (정본)

```bash
docker run \
  --network=none \                   # L12: 네트워크 완전 차단
  --read-only \                      # 루트 파일시스템 읽기 전용
  --memory=256m \                    # 메모리 제한 256MB
  --cpus=0.5 \                       # CPU 0.5 코어 제한
  --pids-limit=50 \                  # 프로세스 수 제한
  --cap-drop=ALL \                   # 모든 Linux capabilities 제거
  --security-opt=no-new-privileges \ # 권한 상승 차단
  --security-opt seccomp=sandbox.json \ # seccomp 프로파일
  --tmpfs /tmp:rw,size=64m,noexec \  # 임시 디렉토리 (실행 불가)
  --rm \                             # 실행 후 자동 삭제
  --name "sandbox-${TRACE_ID}" \     # trace_id 기반 이름 (L18)
  vamos-sandbox:latest \
  timeout 30 python3 /sandbox/script.py  # L12: 30초 하드 타임아웃
```

### 2.3 리소스 제한 요약

| 리소스 | 제한값 | 근거 |
|--------|-------|------|
| **네트워크** | `--network=none` (완전 차단) | L12 |
| **메모리** | 256MB | 코드 실행 충분 + OOM 방지 |
| **CPU** | 0.5 코어 | DoS 방지 |
| **타임아웃** | 30초 (하드) | L12 |
| **디스크** | 읽기 전용 + /tmp 64MB | 호스트 보호 |
| **프로세스** | 최대 50개 | Fork bomb 방지 |
| **Capabilities** | ALL 제거 | 최소 권한 |

---

## 3. 타임아웃 메커니즘

### 3.1 30초 하드 타임아웃 (L12)

```python
import subprocess
import signal

SANDBOX_TIMEOUT = 30  # L12: 30초 하드 리밋

def execute_in_sandbox(code: str, trace_id: str) -> dict:
    """Docker 샌드박스에서 코드 실행"""
    try:
        result = subprocess.run(
            ["docker", "run", "--network=none", "--read-only",
             "--memory=256m", "--cpus=0.5", "--cap-drop=ALL",
             "--rm", f"--name=sandbox-{trace_id}",
             "vamos-sandbox:latest",
             "timeout", str(SANDBOX_TIMEOUT), "python3", "-c", code],
            capture_output=True,
            timeout=SANDBOX_TIMEOUT + 5,  # 외부 타임아웃 = 내부 + 여유 5초
            text=True
        )
        return {
            "stdout": result.stdout[:10240],  # 출력 10KB 제한
            "stderr": result.stderr[:4096],
            "exit_code": result.returncode,
            "trace_id": trace_id
        }
    except subprocess.TimeoutExpired:
        # 타임아웃 초과: 강제 kill
        subprocess.run(["docker", "kill", f"sandbox-{trace_id}"],
                       capture_output=True, timeout=5)
        return {
            "error": "TIMEOUT_EXCEEDED",
            "message": f"Execution exceeded {SANDBOX_TIMEOUT}s limit",
            "trace_id": trace_id
        }
```

### 3.2 타임아웃 처리 흐름

```
[코드 제출] → Docker 컨테이너 시작
  → 30초 타이머 시작
    ├─ [정상 완료] → stdout/stderr 캡처 → 컨테이너 자동 삭제
    └─ [30초 초과] → docker kill → 강제 종료
         → 감사 로그 "TIMEOUT_EXCEEDED" 기록
         → 사용자 알림 "실행 시간 제한 초과"
```

---

## 4. 입출력 인터페이스

### 4.1 입력: python3 -c 인자로 코드 전달

```typescript
interface SandboxInput {
  code: string;           // 실행할 코드 (최대 64KB)
  language: 'python' | 'javascript' | 'typescript';
  trace_id: string;       // 서버 생성 UUID v4 (L18)
  timeout_ms: number;     // 30000 (L12, 변경 불가)
}
```

### 4.2 출력: stdout/stderr 캡처

```typescript
interface SandboxOutput {
  stdout: string;         // 최대 10KB
  stderr: string;         // 최대 4KB
  exit_code: number;
  execution_time_ms: number;
  trace_id: string;
  sandbox_id: string;     // 컨테이너 이름
}
```

### 4.3 결과물 임시 볼륨

```bash
# 임시 출력 볼륨 (읽기 전용 마운트)
--mount type=tmpfs,destination=/output,tmpfs-size=64m
```

---

## 5. 보안 강화

### 5.1 seccomp 프로파일

```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": ["SCMP_ARCH_X86_64"],
  "syscalls": [
    {"names": ["read", "write", "open", "openat", "close", "stat", "fstat", "newfstatat", "lstat",
               "mmap", "mprotect", "munmap", "mremap", "brk", "access", "faccessat", "faccessat2",
               "getpid", "gettid", "clone", "clone3", "execve", "exit", "exit_group", "wait4",
               "futex", "nanosleep", "clock_gettime", "clock_nanosleep",
               "rt_sigaction", "rt_sigprocmask", "rt_sigreturn", "sigaltstack",
               "getrandom", "arch_prctl", "set_robust_list", "get_robust_list", "set_tid_address", "rseq",
               "dup", "dup2", "dup3", "lseek", "readlink", "readlinkv", "getdents64", "pread64", "pwrite64",
               "pipe2", "fcntl", "ioctl", "prlimit64", "getrlimit", "sysinfo", "uname", "getcwd",
               "getuid", "geteuid", "getgid", "getegid", "getppid", "madvise"],
     "action": "SCMP_ACT_ALLOW",
     "comment": "Python3 인터프리터 기동 + 정상 실행 필수 syscall (deny-by-default 유지)"},
    {"names": ["socket", "connect", "bind", "listen", "accept",
               "sendto", "recvfrom"],
     "action": "SCMP_ACT_ERRNO",
     "comment": "네트워크 syscall 차단 (L12 보완)"},
    {"names": ["mount", "umount2", "pivot_root", "chroot"],
     "action": "SCMP_ACT_ERRNO",
     "comment": "파일시스템 탈출 차단"},
    {"names": ["ptrace", "process_vm_readv", "process_vm_writev"],
     "action": "SCMP_ACT_ERRNO",
     "comment": "프로세스 디버깅 차단"}
  ]
}
```

### 5.2 Capabilities 최소화

```
--cap-drop=ALL
# 어떤 capability도 부여하지 않음:
# NO: CAP_NET_RAW, CAP_NET_BIND_SERVICE, CAP_SYS_ADMIN,
#     CAP_SYS_PTRACE, CAP_DAC_OVERRIDE, ...
```

### 5.3 PID Namespace 격리

```bash
# (--pid 플래그 미지정 — Docker 기본값이 private PID namespace이므로 호스트 PID 접근 차단됨. '--pid=container'는 무효 구문이라 사용 금지)
```

---

## 6. 로깅 포맷 (R-01-7)

```json
{
  "event": "security.sandbox.execution",
  "trace_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
  "timestamp": "2026-04-12T13:00:00Z",
  "error": {
    "code": "SBX-TIMEOUT",
    "message": "Sandbox execution exceeded 30s limit",
    "severity": "MEDIUM"
  },
  "context": {
    "sandbox_id": "sandbox-a1b2c3d4",
    "language": "python",
    "code_size_bytes": 1024,
    "execution_time_ms": 30000,
    "network": "none",
    "memory_limit": "256m",
    "exit_code": 137
  },
  "recovery": {
    "action": "container_killed",
    "cleanup": "auto_removed",
    "retry_allowed": true,
    "max_retries": 2
  }
}
```

---

## 7. S7E-019 요구사항 대조

| S7E-019 요구사항 | 본 문서 반영 | 상태 |
|----------------|------------|:----:|
| Agent 실행 환경 격리 | Docker 컨테이너 격리 (§2) | OK |
| 격리 수준 | 네트워크 차단 + 파일시스템 읽기전용 + seccomp | OK |
| 파일시스템 접근 제한 | `--read-only` + tmpfs | OK |
| 프로세스 제한 | `--pids-limit=50` | OK |

---

## 8. 예외 처리 정책 표

| error_code | 설명 | recoverable | 처리 |
|-----------|------|:-----------:|------|
| SBX-TIMEOUT | 30초 타임아웃 초과 | YES | 컨테이너 kill, 재시도 허용 (최대 2회) |
| SBX-OOM | 메모리 초과 (256MB) | YES | 컨테이너 종료, 코드 최적화 안내 |
| SBX-NETVIOLATION | 네트워크 접근 시도 | NO | 즉시 차단, 감사 로그, 알림 |
| SBX-ESCAPE | 컨테이너 탈출 시도 | NO | 즉시 종료, P0 에스컬레이션 |
| SBX-DOCKER | Docker 데몬 연결 실패 | NO | 코드 실행 불가, 사용자 알림 |
| SBX-IMGNOTFOUND | 샌드박스 이미지 없음 | NO | 코드 실행 불가, 인프라 팀 알림 |

---

## 9. Phase 2 통합 테스트 시나리오

| # | 시나리오 | 예상 결과 |
|---|---------|----------|
| T-01 | 정상 Python 코드 `print("hello")` 실행 | stdout="hello", exit_code=0 |
| T-02 | 30초 초과 코드 `import time; time.sleep(60)` | SBX-TIMEOUT, 컨테이너 kill |
| T-03 | 네트워크 접근 `import requests; requests.get("http://evil.com")` | 네트워크 차단, 에러 반환 |
| T-04 | 256MB 초과 메모리 할당 `a = 'x' * (300 * 1024 * 1024)` | SBX-OOM, 컨테이너 종료 |
| T-05 | fork bomb `: () { : \| : & }; :` | --pids-limit=50 차단 |
| T-06 | 파일시스템 쓰기 `open('/etc/passwd', 'w')` | --read-only 차단 |
| T-07 | 호스트 프로세스 접근 `os.kill(1, 9)` | PID namespace 격리 |
| T-08 | seccomp 차단 syscall `socket()` 호출 | SCMP_ACT_ERRNO |
| T-09 | 10KB 초과 출력 생성 | 출력 10KB로 잘림 |
| T-10 | 동시 5개 컨테이너 실행 시 리소스 격리 확인 | 각 컨테이너 독립 동작 |

---

## LOCK 교차 검증 결과

| LOCK | AUTHORITY_CHAIN §5 값 | 본 문서 반영 | 일치 |
|------|----------------------|------------|:----:|
| L12 | 30초 + `--network=none` | §2.2 Docker 실행 명령, §3 타임아웃 | OK |
| L18 | 서버 측 UUID v4 전용 (클라이언트 신뢰 금지) | §2.2 컨테이너 이름 trace_id 기반 | OK |
