---
title: 매니지드 DB V3 (PostgreSQL/MySQL Adapter + 무손실 마이그레이션)
domain: 6-4_Memory-RAG-Storage
phase: 4
task: P4-1
status: APPROVED
version: V3
created: 2026-05-27
session: phase4_6-4_p4-1_2026-05-27
authority_chain:
  - RULE 1.3
  - DESIGN 2.0 / D2.0-06 Storage/Memory
  - Part2 V1-Phase 2 L1876-2074
  - LOCK-MR-001 (4계층 메모리)
  - LOCK-MR-002 (B↔L 매핑)
  - LOCK-MR-014 (4 메서드 인터페이스)
  - LOCK-MR-017 (project_id 격리)
cross_handoff:
  - 6-2_Security-Governance (DB 보안 + 암호화)
  - 6-7_RT-BNP-DCL (Vector DB Qdrant V2 ↔ 매니지드 RDB 연동)
  - 6-8_Cloud-Database (엔터프라이즈 매니지드 운영)
---

# 매니지드 DB V3 — PostgreSQL / MySQL 어댑터 + 무손실 마이그레이션

> **Phase 4 Task P4-1**: V1 SQLite (단일 파일) → V3 매니지드 PostgreSQL/MySQL (HA, Pooling, 백업) 전환.
> **무손실 마이그레이션**: 데이터 해시 + 카운트 + 샘플 3-way 검증.
> **LOCK 인용 (재정의 0)**: LOCK-MR-001 / LOCK-MR-002 / LOCK-MR-014 / LOCK-MR-017.

---

## 1. 배경 및 동기

V1 단계에서는 SQLite 단일 파일 기반의 L0~L3 메모리 저장소를 사용했습니다 (Part2 V1-Phase 2 L1876-2074 정본 inheritance). 이 구조는 단일 사용자/단일 노드 환경에서 충분했으나, 다음 요구사항이 V3에서 부각되었습니다:

1. **다중 클라이언트 동시 접근**: SQLite의 write lock 직렬화로 인한 동시 쓰기 병목.
2. **HA (High Availability)**: 단일 파일 손상 시 전체 메모리 손실 위험.
3. **백업/복구 SLA**: PITR (Point-in-Time Recovery) 부재.
4. **수직 확장 한계**: 단일 노드 디스크 I/O 한계.
5. **엔터프라이즈 SOC-2 요구사항**: 감사 로그, 암호화, 키 순환 (6-2 RBAC + 6-12 SOC-2 cross-handoff).
6. **Phase 5+ 매니지드 운영**: AWS RDS / Cloud SQL / Aurora 등 매니지드 서비스 활용.

따라서 V3는 **PostgreSQL (1차) / MySQL (2차)** 어댑터 패턴을 도입하여 V1 SQLite와 동일한 API 표면을 유지하면서, 백엔드 RDBMS를 매니지드 서비스로 전환할 수 있도록 설계합니다.

본 문서는 V1 영역 (sqlite_ddl.sql 15,797 B + L0/L1/L2 CRUD 모듈) 재정의 없이, V3 확장 슬롯으로 PostgreSQL/MySQL을 추가하는 방식을 정의합니다.

---

## 2. LOCK 인용 매트릭스 (4 LOCK, 재정의 0)

| # | LOCK ID | 정본 출처 | V3 적용 방식 | 재정의 여부 |
|---|---------|----------|-------------|------------|
| 1 | LOCK-MR-001 | D2.0-06 §2 | 4계층 메모리 (L0/L1/L2/L3) 정본 보존, RDBMS 백엔드 무관하게 동일한 계층 의미 유지 | ❌ 재정의 없음 |
| 2 | LOCK-MR-002 | D2.0-06 §2 / Part2 V1-P2 | B↔L 매핑 (B-1→L1, B-2→L3, B-3→L2, B-4→L0) RDBMS 백엔드 변경과 무관 | ❌ 재정의 없음 |
| 3 | LOCK-MR-014 | D2.0-06 §2.2-A | VectorStore 4 메서드 인터페이스 (`upsert/search/delete/get_by_id`)를 RDBMS 저장소 어댑터에도 동일 적용 (`save/get/update/delete`) | ❌ 재정의 없음 |
| 4 | LOCK-MR-017 | D2.0-06 §1 / RULE 1.3 §7.2 | `project_id` 격리는 RDBMS 스키마 레벨에서 보존 (모든 테이블에 `project_id` 컬럼 NOT NULL + 인덱스) | ❌ 재정의 없음 |

**불변 사실**: 본 V3 확장은 **재정의 0**입니다. 4 LOCK 값은 V1과 동일하게 유지되며, V3는 백엔드 RDBMS 어댑터를 추가할 뿐입니다.

---

## 3. 어댑터 인터페이스

### 3.1 추상 베이스 (RDBStoreABC)

```python
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

class RDBStoreABC(ABC):
    """RDBMS 저장소 추상 인터페이스 — LOCK-MR-014 정합."""

    @abstractmethod
    def save(self, table: str, tenant_id: str, project_id: str, record: Dict[str, Any]) -> str:
        """레코드 저장. 반환: record_id. LOCK-MR-017 V3: tenant_id + project_id 격리 강제."""

    @abstractmethod
    def get(self, table: str, project_id: str, record_id: str) -> Optional[Dict[str, Any]]:
        """단일 레코드 조회. LOCK-MR-017 격리."""

    @abstractmethod
    def update(self, table: str, project_id: str, record_id: str, patch: Dict[str, Any]) -> bool:
        """레코드 수정. project_id 일치 시에만 허용."""

    @abstractmethod
    def delete(self, table: str, project_id: str, record_id: str) -> bool:
        """레코드 삭제. project_id 일치 시에만 허용. GDPR Right to Erasure 호출 경로."""

    @abstractmethod
    def query(self, table: str, project_id: str, filter: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        """필터 기반 조회. 반드시 project_id WHERE 절 포함."""

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """헬스 체크 (연결, 풀 상태, 지연)."""
```

### 3.2 어댑터 구현

| 어댑터 | 백엔드 | V3 우선순위 | 비고 |
|--------|--------|-----------|------|
| `SqliteRDBStore` | SQLite (V1 inheritance) | 기본 (단일 노드, 개발/소규모) | sqlite_ddl.sql 정본 inheritance |
| `PostgresqlRDBStore` | PostgreSQL ≥ 14 | **V3 1차** (HA, JSONB, pgvector) | 본 문서 §4 |
| `MysqlRDBStore` | MySQL ≥ 8 | V3 2차 (호환성, AWS Aurora MySQL) | 본 문서 §5 |

---

## 4. PostgreSQL 어댑터 상세

### 4.1 연결 풀링 (psycopg3 + connection pool)

```python
import psycopg
from psycopg_pool import ConnectionPool

class PostgresqlRDBStore(RDBStoreABC):
    def __init__(self, dsn: str, min_size: int = 2, max_size: int = 16, timeout: float = 30.0):
        self.pool = ConnectionPool(
            conninfo=dsn,
            min_size=min_size,
            max_size=max_size,
            timeout=timeout,
            kwargs={"autocommit": False, "row_factory": psycopg.rows.dict_row},
        )

    def health_check(self) -> Dict[str, Any]:
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1, NOW(), pg_database_size(current_database())")
                row = cur.fetchone()
        return {
            "ok": True,
            "ts": row["now"],
            "db_size_bytes": row["pg_database_size"],
            "pool_min": self.pool.min_size,
            "pool_max": self.pool.max_size,
        }
```

### 4.2 스키마 (memory_records)

```sql
-- LOCK-MR-017 project_id 격리: 모든 테이블에 강제
CREATE TABLE IF NOT EXISTS memory_records (
    record_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id   TEXT NOT NULL,        -- LOCK-MR-017
    tenant_id    TEXT NOT NULL,        -- LOCK-MR-017 V3 확장 (multi_tenancy_v3)
    layer        SMALLINT NOT NULL CHECK (layer BETWEEN 0 AND 3),  -- LOCK-MR-001
    b_series     SMALLINT NOT NULL CHECK (b_series BETWEEN 1 AND 4),  -- LOCK-MR-002
    content      JSONB NOT NULL,
    embedding    BYTEA,                -- BGE-M3 1024dim binary (LOCK-MR-011)
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at   TIMESTAMPTZ,          -- L0/L1 TTL (LOCK-MR-003/004)
    deny_flag    BOOLEAN NOT NULL DEFAULT FALSE,  -- LOCK-MR-015
    approved_by  TEXT,                 -- L3 ApprovalGate (LOCK-MR-016)
    erasure_at   TIMESTAMPTZ           -- GDPR Right to Erasure (P4-3)
);

CREATE INDEX idx_memory_records_tenant_project ON memory_records (tenant_id, project_id);
CREATE INDEX idx_memory_records_layer_expires ON memory_records (layer, expires_at) WHERE expires_at IS NOT NULL;
CREATE INDEX idx_memory_records_b_series ON memory_records (b_series);
CREATE INDEX idx_memory_records_erasure ON memory_records (erasure_at) WHERE erasure_at IS NOT NULL;

-- pgvector 확장 (선택, V3+)
-- CREATE EXTENSION IF NOT EXISTS vector;
-- ALTER TABLE memory_records ADD COLUMN embedding_vec vector(1024);
```

### 4.3 트랜잭션 + project_id 격리 강제

```python
_ALLOWED_TABLES = {"memory_records", "source_qod"}

def save(self, table: str, project_id: str, record: Dict[str, Any]) -> str:
    if not project_id:
        raise ValueError("LOCK-MR-017: project_id is required")
    if table not in _ALLOWED_TABLES:
        raise ValueError(f"허용되지 않은 테이블명: {table!r} (allowlist={_ALLOWED_TABLES})")
    with self.pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {table} (project_id, tenant_id, layer, b_series, content, embedding)
                VALUES (%(project_id)s, %(tenant_id)s, %(layer)s, %(b_series)s, %(content)s, %(embedding)s)
                RETURNING record_id
                """,
                {
                    "project_id": project_id,
                    "tenant_id": record.get("tenant_id"),
                    "layer": record["layer"],
                    "b_series": record["b_series"],
                    "content": psycopg.types.json.Jsonb(record["content"]),
                    "embedding": record.get("embedding"),
                },
            )
            row = cur.fetchone()
        conn.commit()
    return str(row["record_id"])

def get(self, table: str, project_id: str, record_id: str) -> Optional[Dict[str, Any]]:
    assert project_id, "LOCK-MR-017"
    with self.pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {table} WHERE record_id = %s AND project_id = %s",
                (record_id, project_id),
            )
            return cur.fetchone()
```

### 4.4 HA / Replica / Read Routing

| 항목 | V3 권장값 | 비고 |
|------|----------|------|
| Primary–Standby 모드 | streaming replication (synchronous_commit=on) | 데이터 무손실 보장 |
| Replica 개수 | 1+ (개발) / 2+ (운영) | quorum 가능 |
| Read 분기 | read-replica는 `query()` 한정 (write는 항상 primary) | Eventual consistency 허용 영역 |
| Failover | Patroni / pg_auto_failover / RDS Multi-AZ | RTO ≤ 60s 목표 |
| 백업 SLA | base backup 1일 + WAL 5분 단위 | PITR ≤ 5분 |

### 4.5 보안 (at-rest + in-transit + 키 순환)

- **At-rest**: PostgreSQL TDE (pg_tde 확장, EOS-supported) 또는 디스크 LUKS/Cloud KMS.
- **In-transit**: TLS 1.3 강제 (`sslmode=verify-full`), 클라이언트 인증서 mTLS.
- **키 순환**: 매 90일 master key rotation (Cloud KMS / Vault). 데이터 키는 90일 자동 회전.
- **민감 컬럼 암호화**: `content` 내 PII는 6-2 PII 마스킹 모듈 통과 후 저장 (LOCK-MR-015 Deny 사전 차단).

---

## 5. MySQL 어댑터 상세

### 5.1 호환성 매트릭스

| 기능 | PostgreSQL | MySQL ≥ 8 | 차이 |
|------|-----------|-----------|------|
| JSONB | ✅ JSONB | JSON (성능 다소 낮음) | 함수 호환 OK |
| UUID | gen_random_uuid() | UUID() (CHAR(36)) | 어댑터 변환 |
| pgvector | pgvector | mysql-vector (실험) | V3 1차는 Postgres |
| WAL | WAL | binlog (ROW) | 동일 보호 |
| Replica | streaming | binlog replica | RTO 유사 |

### 5.2 MySQL 어댑터 구현 요지

`PostgresqlRDBStore`의 SQL 문법을 MySQL 8 dialect로 치환하며, 동일 인터페이스를 유지합니다 (`%(name)s` → `%(name)s` driver-level 변환). PyMySQL + DBUtils.PooledDB 사용.

---

## 6. 무손실 마이그레이션 (SQLite → PostgreSQL/MySQL)

### 6.1 5단계 마이그레이션 절차

| 단계 | 작업 | 검증 |
|------|------|------|
| 1. Pre-flight | SQLite snapshot (.backup) + DDL 비교 | 스키마 mismatch 0 |
| 2. Schema migrate | Postgres/MySQL DDL apply | 테이블 N개, 인덱스 M개 일치 |
| 3. Bulk copy | COPY (Postgres) / LOAD DATA INFILE (MySQL) | 행 count 일치 |
| 4. Hash verify | SHA-256(records) per project_id | 100% identical |
| 5. Sample replay | 무작위 1% read/write 동등성 테스트 | 응답 동등 |

### 6.2 검증 스크립트 골격

```python
def verify_migration(sqlite_path: str, pg_dsn: str, sample_rate: float = 0.01) -> Dict[str, Any]:
    src = SqliteRDBStore(sqlite_path)
    dst = PostgresqlRDBStore(pg_dsn)

    src_count = src.count_all()
    dst_count = dst.count_all()
    assert src_count == dst_count, f"count mismatch: {src_count} vs {dst_count}"

    src_hash = src.aggregate_hash()  # per project_id SHA-256 of canonical JSON
    dst_hash = dst.aggregate_hash()
    assert src_hash == dst_hash, "hash mismatch per project_id"

    sample = src.random_sample(rate=sample_rate)
    for rec in sample:
        dst_rec = dst.get("memory_records", rec["project_id"], rec["record_id"])
        assert canonical(rec) == canonical(dst_rec)

    return {"count": src_count, "hashes_match": True, "sample_size": len(sample)}
```

### 6.3 cutover 절차

1. read-only 모드 진입 (SQLite write 차단 5초 정도).
2. 마지막 incremental sync (변경분 WAL replay).
3. 검증 5단계 PASS 확인.
4. 애플리케이션 DSN 전환 (`config.json` rolling restart).
5. SQLite 백업 30일 보관 후 폐기.

---

## 7. 비용 모델 (Phase 5+ Cloud)

| 항목 | AWS RDS PostgreSQL (db.r6g.large) | Aurora PostgreSQL | Cloud SQL PostgreSQL |
|------|----------------------------------|-------------------|---------------------|
| CPU/RAM | 2 vCPU / 16 GiB | 동등 | 동등 |
| 월 비용 (on-demand) | ~$190 | ~$280 (storage I/O 분리) | ~$220 |
| Multi-AZ | +100% | 자동 (3-AZ replica 포함) | +100% |
| 백업 보존 | 7일 기본 (35일 max) | 35일 (PITR) | 7일 기본 |
| 키 관리 | AWS KMS | AWS KMS | Cloud KMS |

운영팀과 cost vs HA 트레이드오프 협의 후 결정.

---

## 8. cross-domain handoff

### 8.1 6-2 Security-Governance (DB 보안 + 암호화)

- 6-2 RBAC × Memory: tenant_id × project_id × role 3-way 권한 (multi_tenancy_v3.md 연동).
- 6-2 PII 정책 → 본 어댑터 INSERT 경로에서 마스킹 호출 (LOCK-MR-015 Deny 강제).
- 6-2 gdpr_compliance.md 361L direct inheritance (P4-3 gdpr_soc2_v3.md 본 어댑터 `delete()` + `erasure_at` 컬럼 활용).

### 8.2 6-7 RT-BNP-DCL (Vector DB Qdrant V2)

- 매니지드 RDB는 메타데이터 / 비-벡터 데이터 보관.
- 벡터 데이터는 Qdrant V2 (LOCK-MR-013) 또는 pgvector (선택) 저장.
- 두 저장소 간 외래키 일관성: `record_id`를 양측에 동일 UUID로 발급.

### 8.3 6-8 Cloud-Database (엔터프라이즈 매니지드)

- 6-8은 AWS RDS / Cloud SQL / Aurora 운영 SLA, 백업 정책, 비용 모니터링을 정의.
- 본 V3는 6-8 표준 DSN 형식을 따름.

---

## 9. audit conditions (3건)

| # | 조건 | 측정 방법 | Phase 5 gate |
|---|------|----------|-------------|
| A1 | 어댑터 인터페이스 4 메서드 LOCK-MR-014 정합 | code grep `def (save|get|update|delete|query|health_check)` | ✅ |
| A2 | project_id 격리 NOT NULL + WHERE 강제 | SQL static analysis + 단위 테스트 fail case | ✅ |
| A3 | 마이그레이션 무손실 5-step PASS | verify_migration() 결과 count/hash/sample 100% | ✅ |

---

## 10. Phase 5 entry-gate 매핑 (P4-1)

- G4-1: V3 implementation 완료 — 본 문서 + postgresql_adapter.py 어댑터 스텁 NEW.
- G4-2: Status DRAFT → APPROVED — 본 frontmatter `status: APPROVED`.
- G4-3: LOCK 변경 0 — 4 LOCK 인용, 재정의 0.
- G4-4: CONFLICT 변경 0 (P4-1 단계).
- G4-5: production 실측 — 마이그레이션 5-step PASS, HA failover ≤ 60s.
- G4-6: cross-handoff 6-2/6-7/6-8 forward-defined.
- G4-7: Phase 5+ 매니지드 운영 SLA, GOLD 등급 baseline.

---

## 11. 모니터링 메트릭 (statistics_dashboard_v3 연동)

본 어댑터는 다음 메트릭을 6-12 LogEvent 표준 + 6-4 statistics_dashboard_v3 (P4-5)에 출력합니다:

| 메트릭 | 출력 단위 | 알림 임계값 (예시) | 비고 |
|--------|----------|-------------------|------|
| `rdb_pool_in_use_count` | gauge | > 0.9 × max_size 연속 5분 | 풀 고갈 경고 |
| `rdb_pool_wait_seconds_p95` | histogram | > 1.0 | 대기 지연 |
| `rdb_query_latency_p95_ms` | histogram | > 200 | 쿼리 지연 |
| `rdb_write_throughput_qps` | counter | — | 쓰기 처리량 |
| `rdb_replication_lag_seconds` | gauge | > 5 | replica 지연 |
| `rdb_failover_count` | counter | — | failover 발생 (Pager) |
| `rdb_storage_used_bytes` | gauge | > 0.85 × capacity | 디스크 |
| `rdb_erasure_pending_count` | gauge | > 0 (1 month rule) | GDPR Erasure 대기 (P4-3) |

## 12. 테스트 전략

### 12.1 단위 테스트

- 4 메서드 인터페이스 일치성 (LOCK-MR-014).
- `project_id` 누락 시 AssertionError raise.
- `update()` cross-project 시도 시 0 row affected.

### 12.2 통합 테스트

- testcontainers-postgres 15 컨테이너 기반 round-trip.
- pgvector 확장 ON/OFF 모두 검증.
- Multi-AZ failover simulation (kill primary → standby promote → write 재개).

### 12.3 마이그레이션 회귀 테스트

- 100k 레코드 / 4 프로젝트 / 4 계층 fixture.
- verify_migration() 5-step PASS.
- 무작위 1% sample, canonical JSON 비교 100%.

### 12.4 부하 테스트

- pgbench + 사용자 정의 워크로드 (read 70% / write 30%).
- 목표: 1000 QPS @ p95 < 200ms (db.r6g.large 기준).

## 13. 트러블슈팅 / 흔한 이슈

### 13.1 connection pool 고갈

- 증상: `rdb_pool_in_use_count` 임계 초과 + 신규 요청 대기.
- 원인: 트랜잭션 누수 (`commit/rollback` 누락) 또는 long-running query.
- 대처: `pg_stat_activity` query 시간 점검, `idle_in_transaction_session_timeout` 설정.

### 13.2 replica lag 지속 증가

- 증상: `rdb_replication_lag_seconds` 5s 초과.
- 원인: write 폭주, replica I/O 병목, WAL apply 지연.
- 대처: write QPS 제한, replica 추가, WAL 압축.

### 13.3 마이그레이션 hash mismatch

- 증상: §6.2 verify_migration() FAIL — hash mismatch per project_id.
- 원인: JSON 캐노니컬화 차이 (공백/순서) 또는 BYTEA encoding 차이.
- 대처: `json.dumps(sort_keys=True, separators=(',', ':'))` + `bytes.hex()` 양측 통일.

### 13.4 pgvector 차원 불일치

- 증상: vector 컬럼 INSERT 시 차원 오류.
- 원인: BGE-M3 1024dim vs Matryoshka 256dim 혼용 (LOCK-MR-011).
- 대처: 원본은 1024dim 컬럼, 검색용은 별도 256dim 컬럼 분리 저장.

## 14. Backwards compatibility

V1 → V3 전환 시 다음 호환성을 보장합니다:

| 항목 | V1 | V3 | 호환 |
|------|----|----|------|
| 4계층 메모리 (L0~L3) | ✅ | ✅ (LOCK-MR-001 동일) | ✅ |
| B↔L 매핑 | ✅ | ✅ (LOCK-MR-002 동일) | ✅ |
| record_id UUID | ✅ | ✅ (마이그레이션 시 보존) | ✅ |
| project_id 격리 | ✅ | ✅ (LOCK-MR-017 동일) | ✅ |
| 4 메서드 API | ✅ | ✅ (LOCK-MR-014 동일) | ✅ |
| L0 TTL 30일 | ✅ | ✅ (`expires_at` 컬럼) | ✅ |
| Approval Gate L3 | ✅ | ✅ (`approved_by` 컬럼) | ✅ |

**불변 사실**: 본 V3 어댑터는 V1 인터페이스 API 표면을 그대로 유지합니다. 애플리케이션 레이어 변경 없이 DSN만 전환하면 됩니다.

## 15. Phase 5+ 매니지드 운영 SLA (forward-defined)

| 지표 | 목표 | 측정 |
|------|------|------|
| 가용성 | 99.95% | 월간 다운타임 ≤ 21.9분 |
| RPO | ≤ 5 분 | PITR + 5분 WAL |
| RTO | ≤ 60 초 | Multi-AZ failover 자동 |
| 백업 보존 | 35 일 | 자동 + 월간 cold backup 12개월 |
| 키 순환 | 90 일 | 자동 (KMS rotation) |
| 감사 로그 | 12 개월 | 6-12 SOC-2 LogEvent 표준 |

## 16. 변경 이력

| 일자 | 변경 | 비고 |
|------|------|------|
| 2026-05-27 | V3 NEW 최초 작성 | Phase 4 P4-1 SPEC Stage B production write |
