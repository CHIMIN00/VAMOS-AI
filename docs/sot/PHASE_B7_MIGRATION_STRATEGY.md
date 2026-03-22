# PHASE_B7_MIGRATION_STRATEGY (v1.0.0)

---

## 0. 문서 메타

| 항목 | 값 |
|------|-----|
| **문서 ID** | PHASE_B7 |
| **버전** | v1.0.0 |
| **작성일** | 2026-02-22 |
| **상태** | ACTIVE |
| **의존 문서** | D2.1-D1~D8 (스키마), D2.1-A1 (Tech Stack), PHASE_B6 (CI/CD) |
| **대상 독자** | DevOps 엔지니어, 백엔드 개발자, DBA |
| **핵심 원칙** | 무중단, 롤백 가능, 데이터 무결성 보장 |

---

## 1. 개요 (마이그레이션 원칙)

### 1.1 마이그레이션 범위

VAMOS 플랫폼은 V1(로컬 MVP) -> V2(서버) -> V3(엔터프라이즈)로 진화하면서 아래 인프라가 전환된다.

| 구성 요소 | V1 (로컬) | V2 (서버) | V3 (엔터프라이즈) |
|-----------|-----------|-----------|-------------------|
| **메타/인덱스** | SQLite | Postgres | 매니지드 Postgres |
| **로그/이벤트** | JSONL + SQLite | Postgres + JSONL 압축 | Postgres + Loki |
| **벡터 DB** | Chroma (임베디드) | Qdrant (서버) | Qdrant Cloud |
| **그래프 DB** | JSON 파일 | Neo4j Community | Neo4j Aura |
| **임베딩 모델** | BGE-M3 (로컬) | text-embedding-3-small | text-embedding-3-small |
| **설정** | config.v1.toml | config.v2.toml | config.v3.toml + K8s ConfigMap |

### 1.2 핵심 원칙

1. **Zero Data Loss**: 마이그레이션 과정에서 데이터 손실 제로
2. **Rollback Always**: 모든 마이그레이션 단계는 롤백(downgrade) 함수를 포함
3. **Verify Before Commit**: 마이그레이션 후 데이터 무결성 검증을 통과해야 완료
4. **Backup First**: 마이그레이션 전 BackupConfigSchema 연동 자동 백업 필수
5. **Incremental Migration**: 대용량 데이터는 배치 단위 점진적 마이그레이션
6. **Schema Version Pinning**: 모든 스키마는 명시적 버전을 가지며, 하위 호환성 유지

### 1.3 마이그레이션 실행 흐름

```
사전 검증 ──► 자동 백업 ──► 마이그레이션 실행 ──► 사후 검증 ──► 정리
   │              │               │                  │            │
 무결성 체크   BackupConfig    Alembic + 커스텀     레코드 수 비교  아카이브
 스키마 버전   full backup     배치 마이그레이션     해시 비교      이전 데이터
 연결 확인     암호화 저장     트랜잭션 보장        샘플 검증      로그 보존
```

---

## 2. 스키마 버전 관리

### 2.1 Pydantic v2 모델 버전 관리 규칙

D2.1에서 정의된 37개 스키마는 **독립적 버전**을 가진다.

```python
"""스키마 버전 관리 기본 클래스."""
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class SchemaVersion(BaseModel):
    """모든 VAMOS 스키마의 버전 메타데이터."""
    major: int = Field(ge=0, description="주 버전 (하위 호환 깨지는 변경)")
    minor: int = Field(ge=0, description="부 버전 (하위 호환 기능 추가)")
    patch: int = Field(ge=0, description="패치 버전 (버그 수정)")

    def __str__(self) -> str:
        return f"v{self.major}.{self.minor}.{self.patch}"

    def is_compatible_with(self, other: "SchemaVersion") -> bool:
        """같은 major 버전이면 하위 호환."""
        return self.major == other.major


class VersionedSchema(BaseModel):
    """버전이 포함된 기본 스키마."""
    schema_version: SchemaVersion = Field(
        description="스키마 버전"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(json_schema_extra={"x-schema-registry": "vamos"})

```

**버전 관리 규칙**:

| 규칙 | 설명 | 예시 |
|------|------|------|
| MAJOR 증가 | 필드 삭제, 필드 타입 변경, 필수 필드 추가 | v2.2.0 -> v3.0.0 |
| MINOR 증가 | 선택 필드 추가, 새 enum 값 추가 | v2.2.0 -> v2.3.0 |
| PATCH 증가 | 설명 변경, 기본값 수정, 검증 로직 수정 | v2.2.0 -> v2.2.1 |

**현재 스키마 버전 현황**:

| 문서 | 스키마 | 현재 버전 |
|------|--------|----------|
| D2 | DecisionSchema | v2.2.1 |
| D2 | LogEventSchema | v2.2.1 |
| D3 | NodeCapabilityProfileSchema | v2.2.0 |
| D3 | NodeRequest/ResponseEnvelope | v2.2.0 |
| D3 | ToolCallRegistrySchema | v2.3.0 |
| D3 | MCPBridgeLayerSchema | v2.3.0 |
| D4 | ToolRegistryEntrySchema | v2.2.0 |
| D4 | BrainAdapterResponseSchema | v2.2.0 |
| D4 | InfraInvokeResultSchema | v2.2.0 |
| D4 | PromptCacheManagerSchema | v2.3.0 |
| D4 | RateLimitConfigSchema | v2.3.0 |
| D4 | BackupConfigSchema | v2.3.0 |
| D5 | WorkflowOutputEnvelopeSchema | v2.2.0 |
| D5 | FailureReportSchema | v2.2.0 |
| D5 | VerifyChainEntrySchema | v2.2.0 |
| D5 | WorkflowStageSchema | v2.2.0 |
| D5 | AgentMarketplaceSchema | v2.3.0 |
| D5 | CircuitBreakerSchema | v2.3.0 |
| D5 | GatePipelineMappingSchema | v2.3.0 |
| D5 | HITLRequestSchema | v2.3.0 |
| D6 | MemoryRecordSchema (19 fields) | v2.2.0 |
| D6 | SourceQoDSchema | v2.2.0 |
| D6 | VectorStoreAdapterSchema | v2.3.0 |
| D6 | GraphRAGConfigSchema | v2.3.0 |
| D6 | SemanticCacheSchema | v2.3.0 |
| D6 | KBEmbeddingRecordSchema | v2.3.0 |
| D7 | PolicyCheckSchema | v2.2.0 |
| D7 | ApprovalSchema | v2.2.0 |
| D7 | CostBudgetSchema | v2.2.0 |
| D7 | DownshiftSchema | v2.2.0 |
| D7 | GuardrailsCheckSchema | v2.3.0 |
| D7 | RBACRoleSchema | v2.3.0 |
| D7 | AutonomyLevelSchema | v2.3.0 |

### 2.2 스키마 변경 유형

#### Additive (비파괴적)

```python
# 기존: v2.2.0
class DecisionSchema(VersionedSchema):
    decision_id: str
    agent_id: str
    action: str

# 변경 후: v2.3.0 (선택 필드 추가 -- 하위 호환)
class DecisionSchema(VersionedSchema):
    decision_id: str
    agent_id: str
    action: str
    confidence_score: float | None = None  # 새로 추가된 선택 필드
    metadata: dict[str, Any] = Field(default_factory=dict)  # 새로 추가
```

#### Breaking (파괴적)

```python
# 기존: v2.x.x
class MemoryRecordSchema(VersionedSchema):
    content: str
    embedding: list[float]

# 변경 후: v3.0.0 (필드 타입 변경 -- 하위 호환 깨짐)
class MemoryRecordSchema(VersionedSchema):
    content: dict[str, str]  # str -> dict (BREAKING)
    embedding: bytes          # list[float] -> bytes (BREAKING)
```

#### Deprecation (점진적 제거)

```python
from warnings import warn
from pydantic import model_validator

class DecisionSchema(VersionedSchema):
    decision_id: str
    agent_id: str
    action: str
    # Deprecated: v2.4.0에서 제거 예정
    legacy_score: float | None = Field(
        default=None,
        deprecated="v2.4.0에서 제거 예정. confidence_score 사용"
    )
    confidence_score: float | None = None

    @model_validator(mode="after")
    def warn_deprecated_fields(self) -> "DecisionSchema":
        if self.legacy_score is not None:
            warn(
                "legacy_score는 v2.4.0에서 제거됩니다. confidence_score를 사용하세요.",
                DeprecationWarning,
                stacklevel=2,
            )
            if self.confidence_score is None:
                self.confidence_score = self.legacy_score
        return self
```

### 2.3 마이그레이션 스크립트 구조

```
migrations/
  env.py                          # Alembic 환경 설정
  alembic.ini                     # Alembic 설정 파일
  versions/
    001_initial_v1_schema.py      # V1 초기 스키마
    002_add_v2_tables.py          # V2 테이블 추가
    003_migrate_jsonl_to_postgres.py  # JSONL -> Postgres
    004_add_vector_metadata.py    # 벡터 메타데이터 추가
    005_add_rbac_tables.py        # RBAC 테이블 추가
  custom/
    chroma_to_qdrant.py           # Chroma -> Qdrant 벡터 마이그레이션
    json_to_neo4j.py              # JSON -> Neo4j 그래프 마이그레이션
    reembed_bge_to_openai.py      # 임베딩 모델 전환
    config_v1_to_v2.py            # 설정 파일 변환
  utils/
    validators.py                 # 마이그레이션 검증 유틸
    backup_integration.py         # BackupConfigSchema 연동
    batch_processor.py            # 배치 처리 유틸
```

**Alembic 마이그레이션 예시** (`migrations/versions/002_add_v2_tables.py`):

```python
"""V2 테이블 추가 -- Postgres 마이그레이션.

Revision ID: 002_add_v2
Revises: 001_initial
Create Date: 2026-02-22

D2.1 스키마 대상:
- DecisionSchema v2.2.1
- LogEventSchema v2.2.1
- MemoryRecordSchema v2.2.0
- PolicyCheckSchema v2.2.0
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID, ARRAY
from datetime import datetime

# revision identifiers
revision = "002_add_v2"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """V1 SQLite 스키마를 V2 Postgres 스키마로 확장."""

    # decisions 테이블 (DecisionSchema v2.2.1)
    op.create_table(
        "decisions",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("decision_id", sa.String(64), nullable=False, unique=True, index=True),
        sa.Column("agent_id", sa.String(64), nullable=False, index=True),
        sa.Column("action", sa.String(256), nullable=False),
        sa.Column("confidence_score", sa.Float, nullable=True),
        sa.Column("context", JSONB, nullable=True),
        sa.Column("result", JSONB, nullable=True),
        sa.Column("schema_version", sa.String(16), nullable=False, server_default="2.2.1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # log_events 테이블 (LogEventSchema v2.2.1)
    op.create_table(
        "log_events",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("event_id", sa.String(64), nullable=False, unique=True),
        sa.Column("event_type", sa.String(64), nullable=False, index=True),
        sa.Column("severity", sa.String(16), nullable=False, index=True),
        sa.Column("source", sa.String(128), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("payload", JSONB, nullable=True),
        sa.Column("trace_id", sa.String(64), nullable=True, index=True),
        sa.Column("schema_version", sa.String(16), nullable=False, server_default="2.2.1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    # 시계열 파티셔닝 (월별)
    op.execute("""
        CREATE INDEX idx_log_events_created_at ON log_events (created_at);
    """)

    # memory_records 테이블 (MemoryRecordSchema v2.2.0, 필드 19개)
    op.create_table(
        "memory_records",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("memory_id", sa.String(64), nullable=False, unique=True, index=True),
        sa.Column("agent_id", sa.String(64), nullable=False, index=True),
        sa.Column("memory_type", sa.String(32), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("source", sa.String(256), nullable=True),
        sa.Column("source_qod", JSONB, nullable=True),
        sa.Column("tags", ARRAY(sa.String), nullable=True),
        sa.Column("importance", sa.Float, server_default="0.5"),
        sa.Column("access_count", sa.Integer, server_default="0"),
        sa.Column("last_accessed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("embedding_model", sa.String(64), nullable=False),
        sa.Column("embedding_dim", sa.Integer, nullable=False),
        sa.Column("vector_id", sa.String(128), nullable=True),
        sa.Column("graph_node_id", sa.String(128), nullable=True),
        sa.Column("metadata", JSONB, nullable=True),
        sa.Column("schema_version", sa.String(16), nullable=False, server_default="2.2.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
    )

    # policy_checks 테이블 (PolicyCheckSchema v2.2.0)
    op.create_table(
        "policy_checks",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("check_id", sa.String(64), nullable=False, unique=True),
        sa.Column("policy_name", sa.String(128), nullable=False),
        sa.Column("agent_id", sa.String(64), nullable=False, index=True),
        sa.Column("action", sa.String(256), nullable=False),
        sa.Column("result", sa.String(16), nullable=False),  # PASS / FAIL / WARN
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("metadata", JSONB, nullable=True),
        sa.Column("schema_version", sa.String(16), nullable=False, server_default="2.2.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # RBAC 테이블 (RBACRoleSchema v2.3.0)
    op.create_table(
        "rbac_roles",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("role_name", sa.String(32), nullable=False, unique=True),
        sa.Column("permissions", ARRAY(sa.String), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("schema_version", sa.String(16), nullable=False, server_default="2.3.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 기본 RBAC 역할 삽입
    op.execute("""
        INSERT INTO rbac_roles (role_name, permissions, description, schema_version)
        VALUES
            ('OWNER', ARRAY['*'], 'Full system access', '2.3.0'),
            ('ADMIN', ARRAY['manage_agents', 'manage_users', 'view_logs', 'manage_config'], 'Administrative access', '2.3.0'),
            ('OPERATOR', ARRAY['run_agents', 'view_logs', 'manage_own_agents'], 'Operational access', '2.3.0'),
            ('VIEWER', ARRAY['view_agents', 'view_logs'], 'Read-only access', '2.3.0');
    """)


def downgrade() -> None:
    """V2 테이블 제거 (롤백)."""
    op.drop_table("rbac_roles")
    op.drop_table("policy_checks")
    op.drop_table("memory_records")
    op.drop_table("log_events")
    op.drop_table("decisions")
```

---

## 3. V1 -> V2 데이터 마이그레이션

### 3.1 SQLite -> Postgres 마이그레이션

**소스**: SQLite 데이터베이스 파일 (`~/.vamos/vamos.db`)
**대상**: Postgres 16 (`postgresql://user:pass@host:5432/vamos`)
**변환 로직**: 스키마 매핑 + 데이터 타입 변환

```python
"""SQLite -> Postgres 마이그레이션 스크립트."""
import sqlite3
import asyncio
from pathlib import Path
from datetime import datetime
from uuid import uuid4

import asyncpg
from pydantic import BaseModel

from vamos_core.schemas.d4 import BackupConfigSchema
from migrations.utils.backup_integration import execute_backup
from migrations.utils.validators import (
    validate_record_count,
    validate_sample_integrity,
)


class SQLiteToPostgresMigrator:
    """V1 SQLite -> V2 Postgres 마이그레이터."""

    # 테이블 매핑: SQLite 테이블명 -> Postgres 테이블명
    TABLE_MAP = {
        "decisions": "decisions",
        "log_events": "log_events",
        "memory_records": "memory_records",
        "policy_checks": "policy_checks",
        "approvals": "approvals",
        "cost_budgets": "cost_budgets",
    }

    # 타입 매핑: SQLite 타입 -> Postgres 타입
    TYPE_MAP = {
        "TEXT": "TEXT",
        "INTEGER": "BIGINT",
        "REAL": "DOUBLE PRECISION",
        "BLOB": "BYTEA",
        "JSON": "JSONB",
    }

    BATCH_SIZE = 1000  # 배치 단위

    def __init__(
        self,
        sqlite_path: Path,
        postgres_dsn: str,
        backup_config: BackupConfigSchema | None = None,
    ):
        self.sqlite_path = sqlite_path
        self.postgres_dsn = postgres_dsn
        self.backup_config = backup_config

    async def migrate(self) -> dict:
        """전체 마이그레이션 실행."""
        result = {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "tables": {},
            "status": "pending",
        }

        # 1. 사전 검증
        self._validate_sqlite_source()

        # 2. 백업 실행 (BackupConfigSchema 연동)
        if self.backup_config:
            await execute_backup(self.backup_config, source="sqlite")

        # 3. Postgres 연결
        pool = await asyncpg.create_pool(self.postgres_dsn, min_size=2, max_size=10)

        try:
            sqlite_conn = sqlite3.connect(str(self.sqlite_path))
            sqlite_conn.row_factory = sqlite3.Row

            for sqlite_table, pg_table in self.TABLE_MAP.items():
                table_result = await self._migrate_table(
                    sqlite_conn, pool, sqlite_table, pg_table
                )
                result["tables"][pg_table] = table_result

            # 4. 사후 검증
            await self._post_validate(sqlite_conn, pool)

            result["status"] = "completed"
            result["completed_at"] = datetime.now(timezone.utc).isoformat()

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            raise
        finally:
            sqlite_conn.close()
            await pool.close()

        return result

    async def _migrate_table(
        self,
        sqlite_conn: sqlite3.Connection,
        pool: asyncpg.Pool,
        sqlite_table: str,
        pg_table: str,
    ) -> dict:
        """개별 테이블 배치 마이그레이션."""
        cursor = sqlite_conn.execute(f"SELECT COUNT(*) FROM {sqlite_table}")
        total_count = cursor.fetchone()[0]

        migrated = 0
        offset = 0

        async with pool.acquire() as pg_conn:
            while offset < total_count:
                rows = sqlite_conn.execute(
                    f"SELECT * FROM {sqlite_table} LIMIT ? OFFSET ?",
                    (self.BATCH_SIZE, offset),
                ).fetchall()

                if not rows:
                    break

                # 배치 삽입
                values = [self._transform_row(dict(row), pg_table) for row in rows]
                columns = list(values[0].keys())
                placeholders = ", ".join(
                    f"${i+1}" for i in range(len(columns))
                )
                col_names = ", ".join(columns)

                await pg_conn.executemany(
                    f"INSERT INTO {pg_table} ({col_names}) VALUES ({placeholders}) "
                    f"ON CONFLICT DO NOTHING",
                    [tuple(v.values()) for v in values],
                )

                migrated += len(rows)
                offset += self.BATCH_SIZE

        return {
            "source_count": total_count,
            "migrated_count": migrated,
            "status": "ok" if migrated == total_count else "partial",
        }

    def _transform_row(self, row: dict, pg_table: str) -> dict:
        """SQLite 행을 Postgres 형식으로 변환."""
        import json

        transformed = {}
        for key, value in row.items():
            # UUID 필드 생성 (SQLite에 없는 경우)
            if key == "id" and value is None:
                transformed[key] = str(uuid4())
            # JSON 문자열 -> dict
            elif isinstance(value, str) and key in ("context", "payload", "metadata", "source_qod"):
                try:
                    transformed[key] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    transformed[key] = value
            else:
                transformed[key] = value

        # schema_version 기본값 보장
        if "schema_version" not in transformed:
            transformed["schema_version"] = "2.2.0"

        return transformed

    def _validate_sqlite_source(self) -> None:
        """SQLite 소스 파일 검증."""
        if not self.sqlite_path.exists():
            raise FileNotFoundError(f"SQLite DB not found: {self.sqlite_path}")

        conn = sqlite3.connect(str(self.sqlite_path))
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = {t[0] for t in tables}
        conn.close()

        missing = set(self.TABLE_MAP.keys()) - table_names
        if missing:
            raise ValueError(f"SQLite에 누락된 테이블: {missing}")

    async def _post_validate(
        self,
        sqlite_conn: sqlite3.Connection,
        pool: asyncpg.Pool,
    ) -> None:
        """마이그레이션 후 데이터 무결성 검증."""
        async with pool.acquire() as pg_conn:
            for sqlite_table, pg_table in self.TABLE_MAP.items():
                # 레코드 수 비교
                sqlite_count = sqlite_conn.execute(
                    f"SELECT COUNT(*) FROM {sqlite_table}"
                ).fetchone()[0]
                pg_count = await pg_conn.fetchval(
                    f"SELECT COUNT(*) FROM {pg_table}"
                )
                if sqlite_count != pg_count:
                    raise ValueError(
                        f"레코드 수 불일치: {pg_table} "
                        f"(SQLite: {sqlite_count}, Postgres: {pg_count})"
                    )
```

### 3.2 JSONL -> Postgres 로그 마이그레이션

**소스**: JSONL 로그 파일 (`~/.vamos/logs/*.jsonl`)
**대상**: Postgres `log_events` 테이블
**변환**: JSONL 라인 -> LogEventSchema v2.2.1 검증 -> INSERT

```python
"""JSONL -> Postgres 로그 마이그레이션."""
import json
import gzip
from pathlib import Path
from datetime import datetime

import asyncpg
from pydantic import ValidationError

from vamos_core.schemas.d2 import LogEventSchema


class JSONLToPostgresMigrator:
    """V1 JSONL 로그 -> V2 Postgres 마이그레이터."""

    BATCH_SIZE = 5000
    MAX_RETRIES = 3

    def __init__(self, log_dir: Path, postgres_dsn: str):
        self.log_dir = log_dir
        self.postgres_dsn = postgres_dsn
        self.errors: list[dict] = []

    async def migrate(self) -> dict:
        """전체 JSONL 파일 마이그레이션."""
        jsonl_files = sorted(self.log_dir.glob("*.jsonl"))
        gz_files = sorted(self.log_dir.glob("*.jsonl.gz"))
        all_files = jsonl_files + gz_files

        pool = await asyncpg.create_pool(self.postgres_dsn, min_size=2, max_size=10)
        total_migrated = 0
        total_skipped = 0

        try:
            for file_path in all_files:
                result = await self._migrate_file(pool, file_path)
                total_migrated += result["migrated"]
                total_skipped += result["skipped"]
        finally:
            await pool.close()

        return {
            "files_processed": len(all_files),
            "total_migrated": total_migrated,
            "total_skipped": total_skipped,
            "errors": self.errors[:100],  # 최대 100개 에러만 보고
        }

    async def _migrate_file(self, pool: asyncpg.Pool, file_path: Path) -> dict:
        """개별 JSONL 파일 처리."""
        open_fn = gzip.open if file_path.suffix == ".gz" else open
        batch = []
        migrated = 0
        skipped = 0

        with open_fn(file_path, "rt", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    raw = json.loads(line)
                    # Pydantic v2 스키마 검증
                    event = LogEventSchema.model_validate(raw)
                    batch.append(event)
                except (json.JSONDecodeError, ValidationError) as e:
                    self.errors.append({
                        "file": str(file_path),
                        "line": line_num,
                        "error": str(e)[:200],
                    })
                    skipped += 1
                    continue

                if len(batch) >= self.BATCH_SIZE:
                    await self._insert_batch(pool, batch)
                    migrated += len(batch)
                    batch = []

        # 남은 배치 처리
        if batch:
            await self._insert_batch(pool, batch)
            migrated += len(batch)

        return {"migrated": migrated, "skipped": skipped}

    async def _insert_batch(
        self, pool: asyncpg.Pool, events: list[LogEventSchema]
    ) -> None:
        """배치 INSERT."""
        async with pool.acquire() as conn:
            await conn.executemany(
                """
                INSERT INTO log_events (
                    event_id, event_type, severity, source,
                    message, payload, trace_id, schema_version, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (event_id) DO NOTHING
                """,
                [
                    (
                        e.event_id, e.event_type, e.severity, e.source,
                        e.message, json.dumps(e.payload) if e.payload else None,
                        e.trace_id, str(e.schema_version), e.created_at,
                    )
                    for e in events
                ],
            )
```

### 3.3 Chroma -> Qdrant 벡터 마이그레이션

**소스**: Chroma 임베디드 DB (`~/.vamos/chroma/`)
**대상**: Qdrant 서버 (`http://qdrant:6333`)
**변환**: Chroma Collection -> Qdrant Collection (메타데이터 보존)

```python
"""Chroma -> Qdrant 벡터 DB 마이그레이션."""
import chromadb
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    CollectionInfo,
)
from pathlib import Path
from uuid import uuid4


class ChromaToQdrantMigrator:
    """V1 Chroma -> V2 Qdrant 벡터 마이그레이터."""

    BATCH_SIZE = 500

    # Chroma collection -> Qdrant collection 매핑
    COLLECTION_MAP = {
        "vamos_memory": {
            "qdrant_name": "vamos_memory",
            "vector_size": 1024,  # BGE-M3 차원
            "distance": Distance.COSINE,
        },
        "vamos_knowledge": {
            "qdrant_name": "vamos_knowledge",
            "vector_size": 1024,
            "distance": Distance.COSINE,
        },
    }

    def __init__(self, chroma_path: Path, qdrant_url: str, qdrant_api_key: str | None = None):
        self.chroma_client = chromadb.PersistentClient(path=str(chroma_path))
        self.qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

    def migrate(self) -> dict:
        """전체 컬렉션 마이그레이션."""
        results = {}

        for chroma_name, config in self.COLLECTION_MAP.items():
            # 1. Qdrant 컬렉션 생성
            self._create_qdrant_collection(config)

            # 2. Chroma -> Qdrant 데이터 이동
            result = self._migrate_collection(chroma_name, config)
            results[chroma_name] = result

        return results

    def _create_qdrant_collection(self, config: dict) -> None:
        """Qdrant 컬렉션 생성 (존재하지 않는 경우)."""
        collections = [c.name for c in self.qdrant_client.get_collections().collections]

        if config["qdrant_name"] not in collections:
            self.qdrant_client.create_collection(
                collection_name=config["qdrant_name"],
                vectors_config=VectorParams(
                    size=config["vector_size"],
                    distance=config["distance"],
                ),
            )

    def _migrate_collection(self, chroma_name: str, config: dict) -> dict:
        """개별 컬렉션 마이그레이션."""
        chroma_col = self.chroma_client.get_collection(chroma_name)
        total = chroma_col.count()
        migrated = 0

        offset = 0
        while offset < total:
            # Chroma에서 배치 조회
            results = chroma_col.get(
                limit=self.BATCH_SIZE,
                offset=offset,
                include=["embeddings", "metadatas", "documents"],
            )

            if not results["ids"]:
                break

            # Qdrant 포인트 변환
            points = []
            for i, doc_id in enumerate(results["ids"]):
                embedding = results["embeddings"][i]
                metadata = results["metadatas"][i] if results["metadatas"] else {}
                document = results["documents"][i] if results["documents"] else ""

                points.append(
                    PointStruct(
                        id=str(uuid4()),
                        vector=embedding,
                        payload={
                            "original_chroma_id": doc_id,
                            "document": document,
                            "embedding_model": "bge-m3",  # V1 임베딩 모델
                            "needs_reembedding": True,  # V2 재임베딩 플래그
                            **metadata,
                        },
                    )
                )

            # Qdrant에 배치 삽입
            self.qdrant_client.upsert(
                collection_name=config["qdrant_name"],
                points=points,
            )

            migrated += len(points)
            offset += self.BATCH_SIZE

        return {
            "source_count": total,
            "migrated_count": migrated,
            "status": "ok" if migrated == total else "partial",
        }

    def validate(self) -> dict:
        """마이그레이션 후 검증."""
        validation = {}

        for chroma_name, config in self.COLLECTION_MAP.items():
            chroma_col = self.chroma_client.get_collection(chroma_name)
            chroma_count = chroma_col.count()

            qdrant_info = self.qdrant_client.get_collection(config["qdrant_name"])
            qdrant_count = qdrant_info.points_count

            validation[chroma_name] = {
                "chroma_count": chroma_count,
                "qdrant_count": qdrant_count,
                "match": chroma_count == qdrant_count,
            }

        return validation
```

### 3.4 JSON 파일 -> Neo4j 그래프 마이그레이션

**소스**: JSON 그래프 파일 (`~/.vamos/graph/*.json`)
**대상**: Neo4j Community (`bolt://neo4j:7687`)
**변환**: JSON 노드/엣지 -> Cypher CREATE 문

```python
"""JSON 그래프 -> Neo4j 마이그레이션."""
import json
from pathlib import Path
from neo4j import GraphDatabase


class JSONToNeo4jMigrator:
    """V1 JSON 그래프 -> V2 Neo4j 마이그레이터."""

    BATCH_SIZE = 200

    def __init__(self, graph_dir: Path, neo4j_uri: str, neo4j_auth: tuple[str, str]):
        self.graph_dir = graph_dir
        self.driver = GraphDatabase.driver(neo4j_uri, auth=neo4j_auth)

    def migrate(self) -> dict:
        """전체 그래프 마이그레이션."""
        json_files = sorted(self.graph_dir.glob("*.json"))
        results = {"files": [], "total_nodes": 0, "total_edges": 0}

        # 인덱스 생성
        self._create_indexes()

        for file_path in json_files:
            file_result = self._migrate_file(file_path)
            results["files"].append(file_result)
            results["total_nodes"] += file_result["nodes"]
            results["total_edges"] += file_result["edges"]

        return results

    def _create_indexes(self) -> None:
        """Neo4j 인덱스 및 제약조건 생성."""
        with self.driver.session() as session:
            # Agent 노드 고유성 제약
            session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (a:Agent) "
                "REQUIRE a.agent_id IS UNIQUE"
            )
            # Memory 노드 고유성 제약
            session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (m:Memory) "
                "REQUIRE m.memory_id IS UNIQUE"
            )
            # Concept 노드 인덱스
            session.run(
                "CREATE INDEX IF NOT EXISTS FOR (c:Concept) ON (c.name)"
            )
            # 관계 인덱스
            session.run(
                "CREATE INDEX IF NOT EXISTS FOR ()-[r:RELATES_TO]-() ON (r.weight)"
            )

    def _migrate_file(self, file_path: Path) -> dict:
        """개별 JSON 그래프 파일 마이그레이션."""
        with open(file_path, "r", encoding="utf-8") as f:
            graph_data = json.load(f)

        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])

        # 노드 배치 삽입
        node_count = 0
        with self.driver.session() as session:
            for i in range(0, len(nodes), self.BATCH_SIZE):
                batch = nodes[i:i + self.BATCH_SIZE]
                session.execute_write(self._create_nodes_tx, batch)
                node_count += len(batch)

        # 엣지 배치 삽입
        edge_count = 0
        with self.driver.session() as session:
            for i in range(0, len(edges), self.BATCH_SIZE):
                batch = edges[i:i + self.BATCH_SIZE]
                session.execute_write(self._create_edges_tx, batch)
                edge_count += len(batch)

        return {
            "file": str(file_path.name),
            "nodes": node_count,
            "edges": edge_count,
        }

    @staticmethod
    def _create_nodes_tx(tx, nodes: list[dict]) -> None:
        """노드 배치 생성 트랜잭션."""
        for node in nodes:
            label = node.get("label", "Entity")
            props = {k: v for k, v in node.items() if k != "label"}
            tx.run(
                f"MERGE (n:{label} {{id: $id}}) SET n += $props",
                id=node["id"],
                props=props,
            )

    @staticmethod
    def _create_edges_tx(tx, edges: list[dict]) -> None:
        """엣지 배치 생성 트랜잭션."""
        for edge in edges:
            rel_type = edge.get("type", "RELATES_TO")
            props = {k: v for k, v in edge.items()
                     if k not in ("source", "target", "type")}
            tx.run(
                f"""
                MATCH (a {{id: $source}})
                MATCH (b {{id: $target}})
                MERGE (a)-[r:{rel_type}]->(b)
                SET r += $props
                """,
                source=edge["source"],
                target=edge["target"],
                props=props,
            )

    def validate(self) -> dict:
        """마이그레이션 후 검증."""
        with self.driver.session() as session:
            node_count = session.run("MATCH (n) RETURN count(n) AS cnt").single()["cnt"]
            edge_count = session.run("MATCH ()-[r]->() RETURN count(r) AS cnt").single()["cnt"]

        # 소스 JSON 파일에서 총 노드/엣지 수 집계
        source_nodes = 0
        source_edges = 0
        for f in self.graph_dir.glob("*.json"):
            with open(f, "r") as fh:
                data = json.load(fh)
                source_nodes += len(data.get("nodes", []))
                source_edges += len(data.get("edges", []))

        return {
            "source_nodes": source_nodes,
            "source_edges": source_edges,
            "neo4j_nodes": node_count,
            "neo4j_edges": edge_count,
            "nodes_match": source_nodes == node_count,
            "edges_match": source_edges == edge_count,
        }

    def close(self) -> None:
        self.driver.close()
```

### 3.5 설정 파일 마이그레이션 (config.v1.toml -> config.v2.toml)

**소스**: `~/.vamos/config.v1.toml`
**대상**: `~/.vamos/config.v2.toml`

```python
"""V1 -> V2 설정 파일 변환."""
import tomllib
import tomli_w
from pathlib import Path
from pydantic import BaseModel, Field


class V1Config(BaseModel):
    """V1 설정 스키마 — PART2 config.v1.toml 13섹션 nested 구조 정렬 (H-8).

    PHASE_B4 §3 정본 기준. 키 이름은 B4 정본 그대로 사용.
    기존 flat 구조에서 nested 구조로 변경하여 PART2와 일치시킴.
    """
    class CoreConfig(BaseModel):
        autonomy_level: str = "L2"
        pipeline_stages: int = 5
        active_modules: int = 5
        mini_model: str = "ollama/llama3.2:3b"
        main_model: str = "ollama/llama3.1:8b"

    class LLMConfig(BaseModel):
        provider: str = "ollama/"
        max_tokens: int = 2048
        temperature: float = 0.7
        timeout_s: int = 30

    class EmbeddingConfig(BaseModel):
        model: str = "bge-m3"
        dim: int = 1024
        matryoshka_dim: int = 256

    class StorageConfig(BaseModel):
        backend: str = "sqlite"
        db_path: str = "${VAMOS_DATA_DIR}/sqlite/vamos.db"
        memory_ttl_L0: str = "session_end"

    class CostConfig(BaseModel):
        daily_limit: int = 1300
        monthly_limit: int = 40000
        warn_threshold: int = 80
        block_threshold: int = 100

    core: CoreConfig = CoreConfig()
    llm: LLMConfig = LLMConfig()
    embedding: EmbeddingConfig = EmbeddingConfig()
    storage: StorageConfig = StorageConfig()
    cost: CostConfig = CostConfig()
    # 전체 13섹션은 PART2 config.v1.toml 참조 (여기서는 마이그레이션 필수 섹션만 표기)


class V2Config(BaseModel):
    """V2 설정 스키마."""
    # LLM
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"

    # Embedding (V2 전환)
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 1536
    legacy_embedding_model: str = "bge-m3"
    legacy_embedding_dim: int = 1024

    # Database
    database_url: str = "postgresql://vamos:password@localhost:5432/vamos"

    # Vector DB
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None

    # Graph DB
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"

    # Logging
    log_dir: str = "~/.vamos/logs"
    log_to_postgres: bool = True
    jsonl_archive: bool = True

    # Cost
    max_monthly_cost_krw: int = 93000

    # Backup
    backup_type: str = "incremental"
    backup_schedule: str = "0 2 * * *"  # 매일 02:00
    backup_retention_days: int = 30
    backup_encryption: bool = True

    # MCP
    mcp_transport: str = "streamable-http"


def migrate_config(v1_path: Path, v2_path: Path) -> V2Config:
    """V1 설정을 V2로 변환."""
    with open(v1_path, "rb") as f:
        v1_raw = tomllib.load(f)

    v1 = V1Config.model_validate(v1_raw)

    # V1 -> V2 매핑 (H-8: nested 구조 반영)
    v2 = V2Config(
        llm_provider=v1.llm.provider,
        llm_model=v1.core.main_model,
        # 임베딩: V2 기본 모델로 전환, 레거시 보존
        embedding_model="text-embedding-3-small",
        embedding_dim=1536,
        legacy_embedding_model=v1.embedding.model,
        legacy_embedding_dim=v1.embedding.dim,
        # 로그 경로 유지
        log_dir=str(v1.storage.db_path).replace("sqlite/vamos.db", "logs"),
        # 비용 한도 V2 업그레이드
        max_monthly_cost_krw=93000,
    )

    # V2 TOML 저장
    v2_dict = v2.model_dump()
    with open(v2_path, "wb") as f:
        tomli_w.dump(v2_dict, f)

    return v2
```

---

## 4. V2 -> V3 데이터 마이그레이션

### 4.1 Postgres -> 매니지드 Postgres

**전략**: `pg_dump` / `pg_restore` 기반 논리적 마이그레이션

```bash
#!/bin/bash
# scripts/migrate_v2_to_v3_postgres.sh

set -euo pipefail

# 변수
V2_PG_HOST="v2-postgres.internal"
V3_PG_HOST="v3-managed.provider.com"
V2_PG_DB="vamos"
V3_PG_DB="vamos_v3"
BACKUP_DIR="/tmp/vamos_migration"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "[1/5] 사전 검증..."
psql -h "$V2_PG_HOST" -d "$V2_PG_DB" -c "SELECT count(*) FROM decisions;"
psql -h "$V2_PG_HOST" -d "$V2_PG_DB" -c "SELECT count(*) FROM memory_records;"

echo "[2/5] V2 Postgres 덤프..."
mkdir -p "$BACKUP_DIR"
pg_dump -h "$V2_PG_HOST" -d "$V2_PG_DB" \
    --format=custom \
    --compress=9 \
    --verbose \
    --file="$BACKUP_DIR/vamos_v2_${TIMESTAMP}.dump"

echo "[3/5] V3 매니지드 Postgres 복원..."
pg_restore -h "$V3_PG_HOST" -d "$V3_PG_DB" \
    --verbose \
    --clean --if-exists \
    --no-owner \
    --no-privileges \
    "$BACKUP_DIR/vamos_v2_${TIMESTAMP}.dump"

echo "[4/5] V3 스키마 마이그레이션 적용..."
cd /opt/vamos && alembic upgrade head

echo "[5/5] 사후 검증..."
V2_DECISIONS=$(psql -h "$V2_PG_HOST" -d "$V2_PG_DB" -t -c "SELECT count(*) FROM decisions;")
V3_DECISIONS=$(psql -h "$V3_PG_HOST" -d "$V3_PG_DB" -t -c "SELECT count(*) FROM decisions;")

if [ "$V2_DECISIONS" != "$V3_DECISIONS" ]; then
    echo "ERROR: decisions 레코드 수 불일치 (V2: $V2_DECISIONS, V3: $V3_DECISIONS)"
    exit 1
fi

echo "마이그레이션 완료: V2 ($V2_DECISIONS) -> V3 ($V3_DECISIONS)"
```

### 4.2 Qdrant -> Qdrant Cloud

**전략**: Qdrant Snapshot API 활용

```python
"""Qdrant -> Qdrant Cloud 마이그레이션."""
from qdrant_client import QdrantClient


class QdrantCloudMigrator:
    """V2 Qdrant 자체호스팅 -> V3 Qdrant Cloud."""

    BATCH_SIZE = 500

    def __init__(
        self,
        source_url: str,
        cloud_url: str,
        cloud_api_key: str,
    ):
        self.source = QdrantClient(url=source_url)
        self.cloud = QdrantClient(url=cloud_url, api_key=cloud_api_key)

    def migrate_collection(self, collection_name: str) -> dict:
        """컬렉션 마이그레이션 (스냅샷 방식 또는 포인트 전송)."""
        # 1. 소스 컬렉션 정보 조회
        info = self.source.get_collection(collection_name)

        # 2. 클라우드에 동일 컬렉션 생성
        self.cloud.recreate_collection(
            collection_name=collection_name,
            vectors_config=info.config.params.vectors,
        )

        # 3. 포인트 배치 전송
        offset = None
        total_migrated = 0

        while True:
            points, next_offset = self.source.scroll(
                collection_name=collection_name,
                limit=self.BATCH_SIZE,
                offset=offset,
                with_payload=True,
                with_vectors=True,
            )

            if not points:
                break

            self.cloud.upsert(
                collection_name=collection_name,
                points=points,
            )

            total_migrated += len(points)
            offset = next_offset

            if offset is None:
                break

        return {
            "collection": collection_name,
            "source_count": info.points_count,
            "migrated_count": total_migrated,
            "match": info.points_count == total_migrated,
        }
```

### 4.3 Neo4j Community -> Neo4j Aura

**전략**: `neo4j-admin dump` + Aura Import 또는 APOC 기반 스트리밍

```python
"""Neo4j Community -> Neo4j Aura 마이그레이션."""
from neo4j import GraphDatabase


class Neo4jAuraMigrator:
    """V2 Neo4j Community -> V3 Neo4j Aura."""

    BATCH_SIZE = 500

    def __init__(
        self,
        source_uri: str,
        source_auth: tuple[str, str],
        aura_uri: str,
        aura_auth: tuple[str, str],
    ):
        self.source_driver = GraphDatabase.driver(source_uri, auth=source_auth)
        self.aura_driver = GraphDatabase.driver(aura_uri, auth=aura_auth)

    def migrate(self) -> dict:
        """전체 그래프 마이그레이션."""
        # 1. 제약조건 및 인덱스 복제
        self._migrate_constraints()

        # 2. 노드 마이그레이션
        node_count = self._migrate_nodes()

        # 3. 관계 마이그레이션
        edge_count = self._migrate_edges()

        return {
            "nodes_migrated": node_count,
            "edges_migrated": edge_count,
        }

    def _migrate_constraints(self) -> None:
        """제약조건 및 인덱스를 Aura에 복제."""
        with self.source_driver.session() as session:
            constraints = session.run("SHOW CONSTRAINTS").data()

        with self.aura_driver.session() as session:
            for constraint in constraints:
                try:
                    # 제약조건 이름으로 재생성
                    cypher = constraint.get("createStatement", "")
                    if cypher:
                        session.run(cypher)
                except Exception:
                    pass  # 이미 존재하는 경우 무시

    def _migrate_nodes(self) -> int:
        """노드 배치 마이그레이션."""
        total = 0

        with self.source_driver.session() as src:
            # 라벨별로 처리
            labels_result = src.run("CALL db.labels() YIELD label RETURN label")
            labels = [r["label"] for r in labels_result]

        for label in labels:
            skip = 0
            while True:
                with self.source_driver.session() as src:
                    nodes = src.run(
                        f"MATCH (n:{label}) RETURN n SKIP $skip LIMIT $limit",
                        skip=skip,
                        limit=self.BATCH_SIZE,
                    ).data()

                if not nodes:
                    break

                with self.aura_driver.session() as dst:
                    for record in nodes:
                        node = record["n"]
                        props = dict(node)
                        dst.run(
                            f"MERGE (n:{label} {{id: $id}}) SET n = $props",
                            id=props.get("id", props.get("agent_id", "")),
                            props=props,
                        )

                total += len(nodes)
                skip += self.BATCH_SIZE

        return total

    def _migrate_edges(self) -> int:
        """관계 배치 마이그레이션."""
        total = 0

        with self.source_driver.session() as src:
            types_result = src.run(
                "CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType"
            )
            rel_types = [r["relationshipType"] for r in types_result]

        for rel_type in rel_types:
            skip = 0
            while True:
                with self.source_driver.session() as src:
                    rels = src.run(
                        f"""
                        MATCH (a)-[r:{rel_type}]->(b)
                        RETURN a.id AS src, b.id AS tgt, properties(r) AS props
                        SKIP $skip LIMIT $limit
                        """,
                        skip=skip,
                        limit=self.BATCH_SIZE,
                    ).data()

                if not rels:
                    break

                with self.aura_driver.session() as dst:
                    for rel in rels:
                        dst.run(
                            f"""
                            MATCH (a {{id: $src}})
                            MATCH (b {{id: $tgt}})
                            MERGE (a)-[r:{rel_type}]->(b)
                            SET r = $props
                            """,
                            src=rel["src"],
                            tgt=rel["tgt"],
                            props=rel["props"],
                        )

                total += len(rels)
                skip += self.BATCH_SIZE

        return total

    def close(self) -> None:
        self.source_driver.close()
        self.aura_driver.close()
```

---

## 5. 롤백 전략

### 5.1 마이그레이션 롤백 (downgrade 함수)

모든 Alembic 마이그레이션은 `downgrade()` 함수를 필수로 포함한다.

```python
"""롤백 실행 모듈."""
from alembic import command
from alembic.config import Config


def rollback_migration(target_revision: str = "-1") -> None:
    """지정된 리비전으로 롤백.

    Args:
        target_revision: 롤백 대상 리비전.
            "-1": 한 단계 전으로 롤백
            "base": 초기 상태로 롤백
            "002_add_v2": 특정 리비전으로 롤백
    """
    alembic_cfg = Config("alembic.ini")
    command.downgrade(alembic_cfg, target_revision)
```

**Alembic downgrade 예시**:

```python
# migrations/versions/002_add_v2_tables.py 의 downgrade()
def downgrade() -> None:
    """V2 테이블 제거 -- V1 상태로 복원."""
    # 역순으로 제거 (외래 키 의존성 고려)
    op.drop_table("rbac_roles")
    op.drop_table("policy_checks")
    op.drop_table("memory_records")
    op.drop_table("log_events")
    op.drop_table("decisions")
```

### 5.2 데이터 복원 (BackupConfigSchema 연동)

```python
"""BackupConfigSchema 연동 백업/복원 모듈."""
import subprocess
from datetime import datetime
from pathlib import Path

from vamos_core.schemas.d4 import BackupConfigSchema


class BackupManager:
    """BackupConfigSchema 기반 백업 관리."""

    def __init__(self, config: BackupConfigSchema):
        self.config = config
        self.backup_dir = Path("~/.vamos/backups").expanduser()
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def execute_backup(self) -> Path:
        """설정에 따른 백업 실행."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        if self.config.backup_type == "full":
            return self._full_backup(timestamp)
        elif self.config.backup_type == "incremental":
            return self._incremental_backup(timestamp)
        elif self.config.backup_type == "snapshot":
            return self._snapshot_backup(timestamp)
        else:
            raise ValueError(f"Unknown backup type: {self.config.backup_type}")

    def _full_backup(self, timestamp: str) -> Path:
        """전체 백업 (Postgres pg_dump + Qdrant snapshot + Neo4j dump)."""
        backup_path = self.backup_dir / f"full_{timestamp}"
        backup_path.mkdir()

        # Postgres
        pg_dump_file = backup_path / "postgres.dump"
        subprocess.run([
            "pg_dump",
            "--format=custom",
            "--compress=9",
            f"--file={pg_dump_file}",
            self.config.database_url,
        ], check=True)

        # 암호화 (설정에 따라)
        if self.config.encryption:
            self._encrypt_file(pg_dump_file)

        return backup_path

    def _incremental_backup(self, timestamp: str) -> Path:
        """증분 백업 (WAL 기반)."""
        backup_path = self.backup_dir / f"incr_{timestamp}"
        backup_path.mkdir()

        subprocess.run([
            "pg_basebackup",
            "-D", str(backup_path / "pg_base"),
            "--wal-method=stream",
            "--checkpoint=fast",
            "--compress=gzip",
        ], check=True)

        return backup_path

    def _snapshot_backup(self, timestamp: str) -> Path:
        """스냅샷 백업 (파일시스템 레벨)."""
        backup_path = self.backup_dir / f"snap_{timestamp}"
        backup_path.mkdir()
        # 구현은 인프라에 따라 상이 (EBS snapshot, ZFS snapshot 등)
        return backup_path

    def restore_from_backup(self, backup_path: Path) -> None:
        """백업으로부터 복원."""
        pg_dump_file = backup_path / "postgres.dump"

        if self.config.encryption:
            self._decrypt_file(pg_dump_file)

        if pg_dump_file.exists():
            subprocess.run([
                "pg_restore",
                "--clean",
                "--if-exists",
                "--no-owner",
                f"--dbname={self.config.database_url}",
                str(pg_dump_file),
            ], check=True)

    def cleanup_old_backups(self) -> int:
        """보존 기간 초과 백업 정리."""
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.config.retention_days)
        removed = 0

        for backup_dir in self.backup_dir.iterdir():
            if backup_dir.is_dir():
                # 타임스탬프 추출 (디렉토리명에서)
                try:
                    parts = backup_dir.name.split("_", 1)
                    ts_str = parts[1] if len(parts) > 1 else parts[0]
                    ts = datetime.strptime(ts_str, "%Y%m%d_%H%M%S")
                    if ts < cutoff:
                        import shutil
                        shutil.rmtree(backup_dir)
                        removed += 1
                except (ValueError, IndexError):
                    continue

        return removed

    def _encrypt_file(self, file_path: Path) -> None:
        """AES-256 파일 암호화."""
        subprocess.run([
            "openssl", "enc", "-aes-256-cbc",
            "-salt", "-pbkdf2",
            "-in", str(file_path),
            "-out", str(file_path.with_suffix(".enc")),
            "-pass", "env:VAMOS_BACKUP_KEY",
        ], check=True)
        file_path.unlink()
        file_path.with_suffix(".enc").rename(file_path)

    def _decrypt_file(self, file_path: Path) -> None:
        """AES-256 파일 복호화."""
        decrypted = file_path.with_suffix(".dec")
        subprocess.run([
            "openssl", "enc", "-d", "-aes-256-cbc",
            "-pbkdf2",
            "-in", str(file_path),
            "-out", str(decrypted),
            "-pass", "env:VAMOS_BACKUP_KEY",
        ], check=True)
        decrypted.rename(file_path)
```

### 5.3 블루-그린 배포 롤백 (V2+)

```
기존 버전 (Blue) ──────────────────────────── 트래픽 100%
                    │
새 버전 (Green) ────┤ 배포 + 헬스체크
                    │
                    ├── 헬스체크 OK ──► 트래픽 전환 (Green 100%)
                    │                   │
                    │                   └── 이상 감지 ──► 즉시 롤백 (Blue 100%)
                    │
                    └── 헬스체크 FAIL ──► 배포 중단, Blue 유지
```

**Docker Compose 블루-그린**:

```yaml
# deploy/docker-compose.blue-green.yml
services:
  orange-core-blue:
    image: ghcr.io/vamos-ai/vamos-orange-core:${BLUE_VERSION}
    profiles: ["blue"]
    # ... (설정 동일)

  orange-core-green:
    image: ghcr.io/vamos-ai/vamos-orange-core:${GREEN_VERSION}
    profiles: ["green"]
    # ... (설정 동일)

  nginx:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./nginx/upstream.conf:/etc/nginx/conf.d/upstream.conf
```

**롤백 스크립트**:

```bash
#!/bin/bash
# scripts/rollback.sh

set -euo pipefail

ENVIRONMENT=$1  # blue 또는 green
CURRENT=$(cat deploy/.current-env)

if [ "$CURRENT" == "blue" ]; then
    ROLLBACK_TO="green"
else
    ROLLBACK_TO="blue"
fi

echo "롤백: $CURRENT -> $ROLLBACK_TO"

# Nginx upstream 전환
sed -i "s/orange-core-${CURRENT}/orange-core-${ROLLBACK_TO}/" deploy/nginx/upstream.conf
docker compose exec nginx nginx -s reload

echo "$ROLLBACK_TO" > deploy/.current-env
echo "롤백 완료: 현재 활성 환경 = $ROLLBACK_TO"
```

---

## 6. 마이그레이션 실행 절차

### 6.1 사전 검증 (데이터 무결성 체크)

```python
"""마이그레이션 사전 검증 모듈."""
from dataclasses import dataclass
from pathlib import Path
import sqlite3
import hashlib
import json


@dataclass
class PreValidationResult:
    """사전 검증 결과."""
    source_accessible: bool
    target_accessible: bool
    schema_compatible: bool
    record_counts: dict[str, int]
    sample_hashes: dict[str, str]
    errors: list[str]

    @property
    def passed(self) -> bool:
        return (
            self.source_accessible
            and self.target_accessible
            and self.schema_compatible
            and len(self.errors) == 0
        )


class PreValidator:
    """마이그레이션 사전 검증."""

    def validate_v1_to_v2(self, sqlite_path: Path, postgres_dsn: str) -> PreValidationResult:
        """V1 -> V2 사전 검증."""
        errors = []
        record_counts = {}
        sample_hashes = {}

        # 1. SQLite 접근성
        source_ok = sqlite_path.exists()
        if not source_ok:
            errors.append(f"SQLite 파일 없음: {sqlite_path}")

        # 2. Postgres 접근성
        target_ok = self._check_postgres(postgres_dsn)
        if not target_ok:
            errors.append("Postgres 연결 실패")

        # 3. SQLite 레코드 수 확인
        if source_ok:
            conn = sqlite3.connect(str(sqlite_path))
            for table in ["decisions", "log_events", "memory_records", "policy_checks"]:
                try:
                    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                    record_counts[table] = count
                except sqlite3.OperationalError:
                    errors.append(f"SQLite 테이블 없음: {table}")
                    record_counts[table] = -1

            # 4. 샘플 데이터 해시 (검증용)
            for table in record_counts:
                if record_counts[table] > 0:
                    rows = conn.execute(
                        f"SELECT * FROM {table} ORDER BY rowid LIMIT 10"
                    ).fetchall()
                    hash_input = json.dumps([list(r) for r in rows], sort_keys=True)
                    sample_hashes[table] = hashlib.sha256(hash_input.encode()).hexdigest()
            conn.close()

        # 5. 스키마 호환성 (Alembic head vs current)
        schema_ok = self._check_schema_compatibility()
        if not schema_ok:
            errors.append("스키마 버전 불일치")

        return PreValidationResult(
            source_accessible=source_ok,
            target_accessible=target_ok,
            schema_compatible=schema_ok,
            record_counts=record_counts,
            sample_hashes=sample_hashes,
            errors=errors,
        )

    def _check_postgres(self, dsn: str) -> bool:
        try:
            import psycopg
            with psycopg.connect(dsn) as conn:
                conn.execute("SELECT 1")
            return True
        except Exception:
            return False

    def _check_schema_compatibility(self) -> bool:
        try:
            from alembic.config import Config
            from alembic.script import ScriptDirectory
            cfg = Config("alembic.ini")
            script = ScriptDirectory.from_config(cfg)
            head = script.get_current_head()
            return head is not None
        except Exception:
            return False
```

**사전 검증 체크리스트**:

| 항목 | 검증 내용 | 실패 시 조치 |
|------|----------|-------------|
| 소스 접근성 | SQLite 파일 존재, 읽기 가능 | 경로 확인, 권한 수정 |
| 대상 접근성 | Postgres 연결, 쓰기 권한 | DSN 확인, 권한 부여 |
| 스키마 호환 | Alembic 현재 리비전 확인 | alembic upgrade head |
| 디스크 공간 | 대상에 충분한 공간 (소스 2배 이상) | 디스크 확보 |
| 레코드 수 | 각 테이블 레코드 수 기록 | - (기준선) |
| 샘플 해시 | 상위 10건 해시 기록 | - (기준선) |
| 백업 존재 | 최신 백업 확인 | 백업 실행 |

### 6.2 백업 실행

```python
"""마이그레이션 전 자동 백업 실행."""
from vamos_core.schemas.d4 import BackupConfigSchema
from migrations.utils.backup_integration import BackupManager


def pre_migration_backup(config_path: str = "~/.vamos/config.v1.toml") -> Path:
    """마이그레이션 전 자동 백업.

    BackupConfigSchema 기반으로 full 백업 실행.
    마이그레이션 전에는 항상 full 백업.
    """
    backup_config = BackupConfigSchema(
        backup_type="full",
        schedule="manual",  # 마이그레이션 시에는 수동
        retention_days=90,  # 마이그레이션 백업은 90일 보존
        encryption=True,
    )

    manager = BackupManager(backup_config)
    backup_path = manager.execute_backup()

    print(f"백업 완료: {backup_path}")
    return backup_path
```

### 6.3 마이그레이션 실행

```python
"""V1 -> V2 통합 마이그레이션 오케스트레이터."""
import asyncio
from pathlib import Path
from datetime import datetime


class MigrationOrchestrator:
    """V1 -> V2 마이그레이션 통합 실행."""

    def __init__(
        self,
        v1_data_dir: Path = Path("~/.vamos").expanduser(),
        postgres_dsn: str = "postgresql://vamos:password@localhost:5432/vamos",
        qdrant_url: str = "http://localhost:6333",
        neo4j_uri: str = "bolt://localhost:7687",
        neo4j_auth: tuple = ("neo4j", "password"),
    ):
        self.v1_data_dir = v1_data_dir
        self.postgres_dsn = postgres_dsn
        self.qdrant_url = qdrant_url
        self.neo4j_uri = neo4j_uri
        self.neo4j_auth = neo4j_auth

    async def run(self) -> dict:
        """전체 마이그레이션 실행 (순서 보장)."""
        report = {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "steps": [],
        }

        steps = [
            ("1. 사전 검증", self._step_pre_validate),
            ("2. 백업 실행", self._step_backup),
            ("3. Alembic 스키마 마이그레이션", self._step_alembic),
            ("4. SQLite -> Postgres", self._step_sqlite_to_postgres),
            ("5. JSONL -> Postgres", self._step_jsonl_to_postgres),
            ("6. Chroma -> Qdrant", self._step_chroma_to_qdrant),
            ("7. JSON -> Neo4j", self._step_json_to_neo4j),
            ("8. 설정 파일 변환", self._step_config_migration),
            ("9. 사후 검증", self._step_post_validate),
            ("10. 정리", self._step_cleanup),
        ]

        for step_name, step_fn in steps:
            print(f"\n{'='*60}")
            print(f"[실행 중] {step_name}")
            print(f"{'='*60}")

            try:
                result = await step_fn()
                report["steps"].append({
                    "name": step_name,
                    "status": "completed",
                    "result": result,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
                print(f"[완료] {step_name}")
            except Exception as e:
                report["steps"].append({
                    "name": step_name,
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
                print(f"[실패] {step_name}: {e}")
                report["status"] = "failed"
                report["failed_at_step"] = step_name
                # 실패 시 롤백 안내
                print("\n[롤백 안내] alembic downgrade -1 실행 후 백업에서 복원하세요.")
                break
        else:
            report["status"] = "completed"

        report["completed_at"] = datetime.now(timezone.utc).isoformat()
        return report

    async def _step_pre_validate(self) -> dict:
        from migrations.utils.validators import PreValidator
        validator = PreValidator()
        result = validator.validate_v1_to_v2(
            self.v1_data_dir / "vamos.db",
            self.postgres_dsn,
        )
        if not result.passed:
            raise ValueError(f"사전 검증 실패: {result.errors}")
        return {"record_counts": result.record_counts}

    async def _step_backup(self) -> dict:
        from migrations.utils.backup_integration import BackupManager
        from vamos_core.schemas.d4 import BackupConfigSchema
        config = BackupConfigSchema(
            backup_type="full",
            schedule="manual",
            retention_days=90,
            encryption=True,
        )
        manager = BackupManager(config)
        path = manager.execute_backup()
        return {"backup_path": str(path)}

    async def _step_alembic(self) -> dict:
        from alembic.config import Config
        from alembic import command
        cfg = Config("alembic.ini")
        command.upgrade(cfg, "head")
        return {"status": "upgraded to head"}

    async def _step_sqlite_to_postgres(self) -> dict:
        migrator = SQLiteToPostgresMigrator(
            sqlite_path=self.v1_data_dir / "vamos.db",
            postgres_dsn=self.postgres_dsn,
        )
        return await migrator.migrate()

    async def _step_jsonl_to_postgres(self) -> dict:
        migrator = JSONLToPostgresMigrator(
            log_dir=self.v1_data_dir / "logs",
            postgres_dsn=self.postgres_dsn,
        )
        return await migrator.migrate()

    async def _step_chroma_to_qdrant(self) -> dict:
        migrator = ChromaToQdrantMigrator(
            chroma_path=self.v1_data_dir / "chroma",
            qdrant_url=self.qdrant_url,
        )
        return migrator.migrate()

    async def _step_json_to_neo4j(self) -> dict:
        migrator = JSONToNeo4jMigrator(
            graph_dir=self.v1_data_dir / "graph",
            neo4j_uri=self.neo4j_uri,
            neo4j_auth=self.neo4j_auth,
        )
        result = migrator.migrate()
        migrator.close()
        return result

    async def _step_config_migration(self) -> dict:
        v1_path = self.v1_data_dir / "config.v1.toml"
        v2_path = self.v1_data_dir / "config.v2.toml"
        v2_config = migrate_config(v1_path, v2_path)
        return {"config_path": str(v2_path)}

    async def _step_post_validate(self) -> dict:
        """사후 검증: 소스 vs 대상 레코드 수, 샘플 해시 비교."""
        # 상세 검증 로직 (생략 -- PreValidator와 동일 패턴)
        return {"status": "validated"}

    async def _step_cleanup(self) -> dict:
        """이전 데이터 아카이브."""
        import shutil
        archive_dir = self.v1_data_dir / "archive" / "v1"
        archive_dir.mkdir(parents=True, exist_ok=True)

        # SQLite 아카이브
        sqlite_src = self.v1_data_dir / "vamos.db"
        if sqlite_src.exists():
            shutil.move(str(sqlite_src), str(archive_dir / "vamos.db"))

        # JSONL 아카이브 (압축)
        import tarfile
        log_dir = self.v1_data_dir / "logs"
        if log_dir.exists():
            with tarfile.open(str(archive_dir / "logs.tar.gz"), "w:gz") as tar:
                tar.add(str(log_dir), arcname="logs")

        return {"archive_dir": str(archive_dir)}
```

### 6.4 사후 검증

```python
"""마이그레이션 사후 검증."""


class PostValidator:
    """마이그레이션 완료 후 데이터 무결성 검증."""

    def __init__(self, pre_result: "PreValidationResult", postgres_dsn: str):
        self.pre_result = pre_result
        self.postgres_dsn = postgres_dsn

    async def validate(self) -> dict:
        """사후 검증 실행."""
        import asyncpg

        pool = await asyncpg.create_pool(self.postgres_dsn)
        results = {}

        try:
            async with pool.acquire() as conn:
                for table, expected_count in self.pre_result.record_counts.items():
                    actual_count = await conn.fetchval(
                        f"SELECT COUNT(*) FROM {table}"
                    )
                    results[table] = {
                        "expected": expected_count,
                        "actual": actual_count,
                        "match": expected_count == actual_count,
                    }
        finally:
            await pool.close()

        all_match = all(r["match"] for r in results.values())
        return {
            "tables": results,
            "all_match": all_match,
            "status": "PASS" if all_match else "FAIL",
        }
```

**사후 검증 체크리스트**:

| 항목 | 검증 내용 | 허용 범위 |
|------|----------|----------|
| 레코드 수 | 소스 vs 대상 테이블별 COUNT | 완전 일치 (0% 차이) |
| 샘플 해시 | 상위 10건 데이터 해시 비교 | 완전 일치 |
| 스키마 버전 | 모든 레코드의 schema_version 값 | 유효한 버전 형식 |
| 벡터 수 | Chroma count vs Qdrant count | 완전 일치 |
| 그래프 노드/엣지 | JSON 파일 vs Neo4j | 완전 일치 |
| 설정 파일 | config.v2.toml 파싱 가능 | 파싱 성공 |
| API 헬스체크 | /health 엔드포인트 응답 | 200 OK |

### 6.5 정리 (이전 데이터 아카이브)

마이그레이션 완료 후 V1 데이터는 **즉시 삭제하지 않고** 아카이브한다.

```
~/.vamos/
  archive/
    v1/
      vamos.db                  # SQLite 원본
      logs.tar.gz               # JSONL 로그 압축
      chroma.tar.gz             # Chroma DB 압축
      graph.tar.gz              # JSON 그래프 압축
      config.v1.toml            # V1 설정 원본
      migration_report.json     # 마이그레이션 리포트
```

**보존 정책**:
- 아카이브 보존 기간: 90일 (BackupConfigSchema.retention_days 연동)
- 90일 후 자동 삭제 (cron job 또는 BackupManager.cleanup_old_backups)

---

## 7. Embedding 모델 전환 (BGE-M3 -> text-embedding-3-small)

### 7.1 재임베딩 전략

V1에서 사용한 **BGE-M3** (1024차원, 로컬)에서 V2의 **text-embedding-3-small** (1536차원, OpenAI API)로 전환할 때, 기존 벡터를 재임베딩해야 한다.

**핵심 과제**:
- BGE-M3 벡터 (1024D)와 text-embedding-3-small 벡터 (1536D)는 **호환 불가**
- 같은 벡터 공간에서 검색하려면 동일 모델로 임베딩해야 함
- 대량 재임베딩 시 API 비용 발생

**재임베딩 비용 예상**:

| 데이터 규모 | 토큰 수 (예상) | API 비용 (text-embedding-3-small) |
|------------|---------------|----------------------------------|
| 1,000 문서 | ~500K 토큰 | ~$0.01 |
| 10,000 문서 | ~5M 토큰 | ~$0.10 |
| 100,000 문서 | ~50M 토큰 | ~$1.00 |
| 1,000,000 문서 | ~500M 토큰 | ~$10.00 |

### 7.2 점진적 전환 (새 데이터부터 + 배치 재임베딩)

**전환 전략: Dual-Collection 방식**

```
Phase 1: 마이그레이션 직후
  ┌─────────────────┐    ┌──────────────────────┐
  │ vamos_memory_v1  │    │ vamos_memory_v2      │
  │ (BGE-M3, 1024D) │    │ (empty, 1536D)       │
  │ needs_reembedding│    │                      │
  │ = true           │    │                      │
  └─────────────────┘    └──────────────────────┘

Phase 2: 새 데이터 유입 + 배치 재임베딩
  ┌─────────────────┐    ┌──────────────────────┐
  │ vamos_memory_v1  │    │ vamos_memory_v2      │
  │ (점점 줄어듦)     │    │ (새 데이터 + 재임베딩)  │
  │                  │◄───│ 검색 시 양쪽 조회     │
  └─────────────────┘    └──────────────────────┘

Phase 3: 재임베딩 완료
  ┌─────────────────┐    ┌──────────────────────┐
  │ vamos_memory_v1  │    │ vamos_memory_v2      │
  │ (삭제)            │    │ (모든 데이터)          │
  └─────────────────┘    └──────────────────────┘
```

```python
"""BGE-M3 -> text-embedding-3-small 점진적 재임베딩."""
import asyncio
from datetime import datetime

from openai import AsyncOpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)


class EmbeddingMigrator:
    """점진적 임베딩 모델 전환."""

    BATCH_SIZE = 100  # OpenAI API 배치 크기
    TARGET_MODEL = "text-embedding-3-small"
    TARGET_DIM = 1536

    def __init__(self, qdrant_url: str, openai_api_key: str):
        self.qdrant = QdrantClient(url=qdrant_url)
        self.openai = AsyncOpenAI(api_key=openai_api_key)

    async def setup_v2_collection(self, collection_name: str) -> None:
        """V2 컬렉션 생성 (text-embedding-3-small 차원)."""
        v2_name = f"{collection_name}_v2"
        collections = [c.name for c in self.qdrant.get_collections().collections]

        if v2_name not in collections:
            self.qdrant.create_collection(
                collection_name=v2_name,
                vectors_config=VectorParams(
                    size=self.TARGET_DIM,
                    distance=Distance.COSINE,
                ),
            )

    async def reembed_batch(self, collection_name: str, batch_size: int = None) -> dict:
        """배치 재임베딩 실행.

        V1 컬렉션에서 needs_reembedding=True인 포인트를 가져와
        text-embedding-3-small로 재임베딩 후 V2 컬렉션에 삽입.
        """
        batch_size = batch_size or self.BATCH_SIZE
        v1_name = collection_name
        v2_name = f"{collection_name}_v2"

        # needs_reembedding=True인 포인트 조회
        points, _ = self.qdrant.scroll(
            collection_name=v1_name,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="needs_reembedding",
                        match=MatchValue(value=True),
                    )
                ]
            ),
            limit=batch_size,
            with_payload=True,
            with_vectors=False,  # 기존 벡터는 불필요
        )

        if not points:
            return {"processed": 0, "remaining": 0}

        # 텍스트 추출
        texts = [p.payload.get("document", "") for p in points]

        # OpenAI API 재임베딩
        response = await self.openai.embeddings.create(
            model=self.TARGET_MODEL,
            input=texts,
        )

        # V2 컬렉션에 삽입
        v2_points = []
        for i, point in enumerate(points):
            new_payload = {**point.payload}
            new_payload["needs_reembedding"] = False
            new_payload["embedding_model"] = self.TARGET_MODEL
            new_payload["reembedded_at"] = datetime.now(timezone.utc).isoformat()

            v2_points.append(
                PointStruct(
                    id=point.id,
                    vector=response.data[i].embedding,
                    payload=new_payload,
                )
            )

        self.qdrant.upsert(
            collection_name=v2_name,
            points=v2_points,
        )

        # V1 컬렉션에서 플래그 업데이트
        for point in points:
            self.qdrant.set_payload(
                collection_name=v1_name,
                payload={"needs_reembedding": False, "migrated_to_v2": True},
                points=[point.id],
            )

        # 남은 건수 조회
        remaining = self.qdrant.count(
            collection_name=v1_name,
            count_filter=Filter(
                must=[
                    FieldCondition(
                        key="needs_reembedding",
                        match=MatchValue(value=True),
                    )
                ]
            ),
        ).count

        return {
            "processed": len(points),
            "remaining": remaining,
            "api_tokens_used": response.usage.total_tokens,
        }

    async def run_full_reembedding(
        self,
        collection_name: str,
        max_api_calls: int = 1000,
        delay_seconds: float = 0.5,
    ) -> dict:
        """전체 재임베딩 (속도 제한 준수)."""
        await self.setup_v2_collection(collection_name)

        total_processed = 0
        total_tokens = 0
        api_calls = 0

        while api_calls < max_api_calls:
            result = await self.reembed_batch(collection_name)

            if result["processed"] == 0:
                break

            total_processed += result["processed"]
            total_tokens += result.get("api_tokens_used", 0)
            api_calls += 1

            # 속도 제한 준수
            await asyncio.sleep(delay_seconds)

            if result["remaining"] == 0:
                break

        return {
            "total_processed": total_processed,
            "total_tokens": total_tokens,
            "api_calls": api_calls,
            "completed": result.get("remaining", 0) == 0,
        }
```

**하이브리드 검색 (전환 기간 중)**:

```python
"""전환 기간 중 V1+V2 하이브리드 검색."""
from qdrant_client import QdrantClient


class HybridSearcher:
    """BGE-M3 + text-embedding-3-small 하이브리드 검색.

    전환 기간 동안 양쪽 컬렉션에서 검색하여 결과를 병합.
    """

    def __init__(self, qdrant: QdrantClient, openai_client, bge_model):
        self.qdrant = qdrant
        self.openai = openai_client
        self.bge = bge_model

    async def search(
        self,
        query: str,
        collection_name: str,
        limit: int = 10,
    ) -> list[dict]:
        """하이브리드 검색 실행."""
        results = []

        # V2 컬렉션 검색 (text-embedding-3-small)
        v2_name = f"{collection_name}_v2"
        v2_embedding = await self._embed_openai(query)
        v2_results = self.qdrant.search(
            collection_name=v2_name,
            query_vector=v2_embedding,
            limit=limit,
        )
        results.extend([
            {"score": r.score, "payload": r.payload, "source": "v2"}
            for r in v2_results
        ])

        # V1 컬렉션 잔여분 검색 (BGE-M3, 아직 재임베딩 안 된 것)
        v1_embedding = self._embed_bge(query)
        v1_results = self.qdrant.search(
            collection_name=collection_name,
            query_vector=v1_embedding,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="needs_reembedding",
                        match=MatchValue(value=True),
                    )
                ]
            ),
            limit=limit,
        )
        results.extend([
            {"score": r.score * 0.9, "payload": r.payload, "source": "v1"}
            for r in v1_results
        ])  # V1 결과는 약간 페널티

        # 점수 기준 정렬 후 상위 N개 반환
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    async def _embed_openai(self, text: str) -> list[float]:
        response = await self.openai.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        return response.data[0].embedding

    def _embed_bge(self, text: str) -> list[float]:
        return self.bge.encode(text).tolist()
```

**점진적 전환 스케줄**:

| 단계 | 기간 | 작업 | 비고 |
|------|------|------|------|
| Phase 1 | V2 배포 직후 | V2 컬렉션 생성, 새 데이터는 V2에만 적재 | 하이브리드 검색 활성화 |
| Phase 2 | +1~7일 | 야간 배치 재임베딩 (하루 10,000건씩) | API Rate Limit 준수 |
| Phase 3 | +7~14일 | 재임베딩 완료 확인, V1 컬렉션 비활성화 | 모니터링 강화 |
| Phase 4 | +30일 | V1 컬렉션 삭제 | 최종 정리 |

---

## 8. 문서 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| v1.0.0 | 2026-02-22 | 최초 작성 -- B7 스키마 마이그레이션 + V1->V2 전환 전략 전체 | VAMOS Team |

---

<\!-- END OF DOCUMENT -->
