# SQLCipher AES-256 상세 명세

> **Phase**: 1 (V1)
> **§7.3 항목**: #9 "SQLCipher AES-256"
> **세션**: P1-1
> **작성일**: 2026-04-12
> **상태**: DRAFT

---

## 교차 참조 블록

| 정본 문서 | 섹션 | 참조 내용 |
|----------|------|----------|
| Part2 구현가이드 | §6.5 #10 | SQLCipher AES-256 구현 지침 |
| D2.0-07 | S7E-032 (CRITICAL, V1) | 로컬 데이터 암호화 요구사항 |
| AUTHORITY_CHAIN.md | §5 L13 | SQLCipher AES-256-CBC LOCK |
| 02_hmac-timing-defense/_index.md | §D | 암호화 인프라 |

---

## 1. LOCK L13 교차 검증

> LOCK (Part2 §6.5): SQLCipher 암호화 — AES-256-CBC

| 검증 항목 | LOCK L13 값 | 본 문서 | 일치 |
|----------|-----------|--------|:----:|
| 암호화 알고리즘 | AES-256-CBC | §2.1 암호화 설정 | OK |

---

## 2. SQLCipher 설정 설계

### 2.1 암호화 구성

| 항목 | 설정 | 근거 |
|------|------|------|
| **암호화 알고리즘** | AES-256-CBC | L13 (정본) |
| **키 파생 함수** | PBKDF2-HMAC-SHA512 | SQLCipher 4.x 기본 |
| **KDF iterations** | 256,000 | OWASP 권장 최소값 이상 |
| **페이지 크기** | 4096 bytes | SQLCipher 기본, 성능 최적 |
| **호환성** | cipher_compatibility=4 | SQLCipher 4.x 호환 |

### 2.2 PRAGMA 설정

```sql
-- SQLCipher 초기화 PRAGMA (연결 시 매번 실행)
PRAGMA key = 'x''<32바이트_마스터_키_hex>';  -- 64자 hex
PRAGMA cipher_compatibility = 4;
PRAGMA cipher_page_size = 4096;
PRAGMA kdf_iter = 256000;
PRAGMA cipher_hmac_algorithm = HMAC_SHA512;
PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA512;

-- 무결성 검증
PRAGMA cipher_integrity_check;
```

### 2.3 의사코드 — DB 초기화

```python
import sqlite3
import os

def init_encrypted_db(db_path: str, master_key: bytes) -> sqlite3.Connection:
    """SQLCipher 암호화 DB 초기화
    시간복잡도: O(1) — 연결 + PRAGMA 실행
    LOCK 참조: L13 (AES-256-CBC)
    """
    assert len(master_key) >= 32, f"Key must be ≥32 bytes (got {len(master_key)})"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 마스터 키 적용 (hex 형식)
    key_hex = master_key.hex()
    cursor.execute(f"PRAGMA key = '{key_hex}'")  # passphrase 형식 — PBKDF2 KDF(kdf_iter, PBKDF2_HMAC_SHA512) 가동 (raw x'...' hex는 KDF 우회하므로 금지)
    cursor.execute("PRAGMA cipher_compatibility = 4")
    cursor.execute("PRAGMA cipher_page_size = 4096")
    cursor.execute("PRAGMA kdf_iter = 256000")
    
    # 무결성 검증
    result = cursor.execute("PRAGMA cipher_integrity_check").fetchone()
    if result[0] != 'ok':
        raise SecurityError("DB integrity check failed")
    
    return conn
```

---

## 3. 키 관리

### 3.1 마스터 키 생성

```python
import os

def generate_master_key() -> bytes:
    """32바이트 마스터 키 생성 (CSPRNG)
    LOCK 참조: L4 (HMAC 키 최소 32바이트 — 동일 원칙 적용)
    """
    key = os.urandom(32)  # 256비트 CSPRNG
    assert len(key) == 32
    return key
```

### 3.2 키 저장

| 환경 | 저장 방식 | 보안 수준 |
|------|----------|----------|
| **V1 개발** | `.env` 환경 변수 (`SQLCIPHER_MASTER_KEY`) | 기본 |
| **V1 프로덕션** | OS 키체인 (macOS: Keychain, Windows: DPAPI, Linux: libsecret) | 높음 |
| **V2+** | HashiCorp Vault | 최고 |

```bash
# .env 예시 (V1 개발 환경)
SQLCIPHER_MASTER_KEY=<64자_hex>
# .gitignore에 반드시 등록 (CK-05)
```

### 3.3 키 순환 (PRAGMA rekey)

```python
def rotate_db_key(conn: sqlite3.Connection, new_key: bytes) -> None:
    """DB 마스터 키 순환
    시간복잡도: O(n) — n=DB 페이지 수 (전체 재암호화)
    """
    assert len(new_key) >= 32
    new_key_hex = new_key.hex()
    conn.execute(f"PRAGMA rekey = \"x'{new_key_hex}'\"")
    conn.execute("PRAGMA cipher_integrity_check")
    # 감사 로그
    log_security_event("db_key_rotation", {
        "db_path": conn.database,
        "new_key_hash": hashlib.sha256(new_key).hexdigest()[:16],
        "timestamp": datetime.utcnow().isoformat()
    })
```

**키 순환 주기**: API Key 순환(90일, L5)과 동기화 권장

---

## 4. 대상 DB 식별

| DB | 용도 | 암호화 적용 | 성능 영향 |
|----|------|:-----------:|----------|
| **사용자 설정 DB** | 사용자 선호도, 테마, 단축키 | YES | ~5% (소규모) |
| **대화 이력 DB** | 대화 세션, 메시지 이력 | YES | ~10% (중규모, 빈번한 읽기/쓰기) |
| **감사 로그 DB** | 보안 이벤트, 접근 기록 | YES | ~8% (append-only, 쓰기 위주) |
| **캐시 DB** | 임시 캐시, 세션 토큰 | NO | 불필요 (일시 데이터) |

> **성능 영향 평가**: AES-256-CBC + PBKDF2 256K iterations 기준, 초기 키 파생 ~200ms, 이후 읽기/쓰기 ~5-10% 오버헤드.

---

## 5. 마이그레이션 절차

### 5.1 평문 DB → SQLCipher 암호화 변환

```python
def migrate_plaintext_to_encrypted(
    plaintext_db: str,
    encrypted_db: str,
    master_key: bytes
) -> None:
    """평문 DB를 SQLCipher 암호화 DB로 변환
    시간복잡도: O(n) — n=DB 크기
    """
    # 1. 평문 DB 열기
    plain_conn = sqlite3.connect(plaintext_db)
    
    # 2. 암호화 DB 생성 + 키 설정
    enc_conn = init_encrypted_db(encrypted_db, master_key)
    
    # 3. 데이터 복사
    plain_conn.execute(f"ATTACH DATABASE '{encrypted_db}' AS enc KEY ...")
    plain_conn.execute("SELECT sqlcipher_export('enc')")
    plain_conn.execute("DETACH DATABASE enc")
    
    # 4. 무결성 검증
    checksum_plain = compute_data_checksum(plaintext_db)
    checksum_enc = compute_data_checksum_encrypted(encrypted_db, master_key)
    assert checksum_plain == checksum_enc, "Migration integrity check failed"
    
    # 5. 원본 백업 후 삭제 (안전 삭제)
    shutil.copy2(plaintext_db, f"{plaintext_db}.bak")
    secure_delete(plaintext_db)  # 물리적 덮어쓰기
    
    # 6. 감사 로그
    log_security_event("db_migration", {
        "source": plaintext_db,
        "target": encrypted_db,
        "checksum_match": True
    })
```

### 5.2 무결성 검증 (SHA-256 체크섬)

```python
def compute_data_checksum(db_path: str) -> str:
    """DB 전체 데이터 SHA-256 체크섬 계산"""
    import hashlib
    conn = sqlite3.connect(db_path)
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    
    hasher = hashlib.sha256()
    for (table,) in sorted(tables):
        rows = conn.execute(f"SELECT * FROM {table} ORDER BY rowid").fetchall()
        for row in rows:
            hasher.update(str(row).encode())
    
    return hasher.hexdigest()
```

---

## 6. 로깅 포맷 (R-01-7)

```json
{
  "event": "security.sqlcipher.operation",
  "trace_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
  "timestamp": "2026-04-12T13:00:00Z",
  "error": {
    "code": "SCE-001",
    "message": "SQLCipher key rotation completed",
    "severity": "INFO"
  },
  "context": {
    "db_name": "conversation_history",
    "operation": "key_rotation",
    "cipher": "AES-256-CBC",
    "kdf_iterations": 256000,
    "integrity_check": "passed"
  },
  "recovery": {
    "action": "rotation_completed",
    "rollback_available": true,
    "backup_path": "encrypted"
  }
}
```

---

## 7. 예외 처리 정책 표

| error_code | 설명 | recoverable | 처리 |
|-----------|------|:-----------:|------|
| SCE-001 | 키 파생 실패 | NO | DB 접근 불가, P0 알림 |
| SCE-002 | 무결성 검증 실패 | NO | DB 손상 의심, 백업 복원, P0 알림 |
| SCE-003 | 키 순환 중 장애 | YES | 이전 키로 롤백, 재시도 |
| SCE-004 | 마이그레이션 체크섬 불일치 | NO | 마이그레이션 중단, 원본 보존 |
| SCE-005 | 키 저장소 접근 실패 | YES | 환경변수 폴백 (V1), P1 알림 |
| SCE-006 | DB 파일 권한 오류 | YES | 권한 재설정 (0600) |

---

## 8. Phase 2 통합 테스트 시나리오

| # | 시나리오 | 예상 결과 |
|---|---------|----------|
| T-01 | 올바른 키로 암호화 DB 열기 | 정상 접근 |
| T-02 | 잘못된 키로 암호화 DB 열기 | "file is not a database" 에러 |
| T-03 | 키 없이 암호화 DB 열기 | "file is not a database" 에러 |
| T-04 | PRAGMA rekey로 키 순환 후 신규 키 접근 | 정상 접근 |
| T-05 | 키 순환 후 이전 키 접근 시도 | 접근 거부 |
| T-06 | 평문→암호화 마이그레이션 후 데이터 무결성 | 체크섬 일치 |
| T-07 | 256MB DB의 암호화 성능 측정 | 쓰기 <15% 오버헤드 |
| T-08 | cipher_integrity_check 실행 | "ok" 반환 |
| T-09 | KDF iterations 256000 미만 설정 시도 | 거부 (최소값 강제) |
| T-10 | 동시 5개 연결에서 암호화 DB 읽기/쓰기 | 정상 동작, 데이터 일관성 |

---

## S7E-032 요구사항 대조

| S7E-032 요구사항 | 본 문서 반영 | 상태 |
|----------------|------------|:----:|
| 로컬 데이터 암호화 (CRITICAL, V1) | AES-256-CBC SQLCipher | OK |
| SQLite 암호화 | SQLCipher 4.x | OK |
| 키 저장은 OS Keychain | §3.2 V1 프로덕션 | OK |

---

## LOCK 교차 검증 결과

| LOCK | AUTHORITY_CHAIN §5 값 | 본 문서 반영 | 일치 |
|------|----------------------|------------|:----:|
| L13 | SQLCipher 암호화 — AES-256-CBC | §2.1 암호화 구성 | OK |
| L4 | HMAC-SHA256 기준 최소 32바이트 키 | §3.1 마스터 키 32바이트 (동일 원칙) | OK |
| L5 | 90일 주기 자동 키 순환 | §3.3 키 순환 90일 동기화 권장 | OK |
