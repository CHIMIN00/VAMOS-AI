"""Alembic 마이그레이션 환경 — VAMOS V1 데이터 계층.

DB URL 해석 우선순위 (A23 config 키 호환):
  1. VAMOS_DB_PATH  — 명시(테스트/CI/배포). sqlite 파일 경로.
  2. config.storage.db_path  — 정본(config.v1.toml [storage], ${VAMOS_DATA_DIR} 치환).
  3. ./data/sqlite/vamos.db  — 최종 기본(config 로드 불가 환경).

V0 호환: baseline revision은 memory_store가 만드는 스키마와 동일(0001_v0_baseline).
기존 V0 vamos.db는 `alembic stamp <baseline>`로 무손실 등록(테이블 재생성 없음).
"""

from __future__ import annotations

import os
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool

from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 마이그레이션 대상 메타데이터 — V0/V1은 raw SQL 마이그레이션(op.execute)이라 None.
# (V2+ ORM 모델 도입 시 target_metadata = Base.metadata 로 전환 — autogenerate 활성화.)
target_metadata = None


def _resolve_db_path() -> str:
    explicit = os.environ.get("VAMOS_DB_PATH")
    if explicit:
        return explicit
    try:
        from vamos_core.infra.config_loader import get_config

        return get_config().storage.db_path
    except Exception:
        data_dir = os.environ.get("VAMOS_DATA_DIR", "./data")
        return str(Path(data_dir) / "sqlite" / "vamos.db")


def _db_url() -> str:
    path = _resolve_db_path()
    # sqlite 파일 디렉토리 보장(첫 마이그레이션 시 — logger.py mkdir 멱등 선례)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{path}"


def run_migrations_offline() -> None:
    context.configure(
        url=_db_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,  # sqlite ALTER 제약 회피(Expand/Contract 배치 모드, A23)
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    section = config.get_section(config.config_ini_section) or {}
    section["sqlalchemy.url"] = _db_url()
    connectable = engine_from_config(
        section, prefix="sqlalchemy.", poolclass=pool.NullPool
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
