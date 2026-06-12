"""config.v1.toml + config_loader 검증 (V0-STEP-5 Stage Gate #8/#9/#10)."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from vamos_core.infra.config_loader import (
    VamosConfig,
    get_config,
    load_config,
    reset_config_cache,
)

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "config.v1.toml"


@pytest.fixture(autouse=True)
def _fresh_cache():
    reset_config_cache()
    yield
    reset_config_cache()


def test_config_file_exists():
    assert CONFIG_PATH.is_file()


def test_load_14_sections():
    cfg = load_config(CONFIG_PATH)
    assert len(VamosConfig.model_fields) == 14  # B4 13 + confidence (PHASE4-DEC-003)
    assert set(VamosConfig.model_fields) == {
        "core", "llm", "embedding", "vector_db", "graph_db", "storage", "cost",
        "self_check", "approval", "mcp", "rbac", "logging", "semantic_cache", "confidence",
    }
    assert isinstance(cfg, VamosConfig)


def test_lock_values_loaded():
    """Stage Gate #9: LOCK 값 정확성."""
    cfg = load_config(CONFIG_PATH)
    assert cfg.embedding.model == "bge-m3"
    assert cfg.embedding.dimension == 1024
    assert cfg.cost.daily_limit == 1300
    assert cfg.cost.monthly_limit == 40000
    assert cfg.cost.warn_threshold == 80  # DEC-005 게이트
    assert cfg.cost.block_threshold == 100
    assert cfg.cost.alert_thresholds == [70, 85, 95]  # DEC-002 경보(비-LOCK)
    assert cfg.semantic_cache.similarity_threshold == 0.95
    assert cfg.self_check.soft_loop_max == 1
    assert cfg.approval.timeout_s == 600
    assert cfg.approval.p2_timeout_s == 300
    assert cfg.mcp.transport == "streamable_http"
    assert cfg.logging.trace_id_required is True
    assert cfg.core.single_decision_lock is True
    # PHASE3-DEC-010 confidence 3키 (LOCK)
    assert cfg.confidence.confidence_high_threshold == 0.85
    assert cfg.confidence.confidence_medium_threshold == 0.60
    assert cfg.confidence.confidence_refuse_threshold == 0.30


def test_core_ipc_keys():
    """PHASE4-DEC-009: [core] ipc 2키 (비-LOCK)."""
    cfg = load_config(CONFIG_PATH)
    assert cfg.core.ipc_max_restart == 3
    assert cfg.core.ipc_timeout_s == 30


def test_frozen_runtime_mutation_rejected():
    """R5: LOCK 값 런타임 변경 시 에러 (frozen — Defense Layer 1)."""
    cfg = load_config(CONFIG_PATH)
    with pytest.raises(ValidationError):
        cfg.cost.monthly_limit = 99999  # type: ignore[misc]
    with pytest.raises(ValidationError):
        cfg.confidence.confidence_refuse_threshold = 0.0  # type: ignore[misc]


def test_lock_tamper_in_toml_rejected(tmp_path):
    """§1.3.1 #2: TOML 자체의 LOCK 변조도 ValidationError."""
    tampered = CONFIG_PATH.read_text(encoding="utf-8").replace(
        "monthly_limit = 40000", "monthly_limit = 99999"
    )
    p = tmp_path / "config.v1.toml"
    p.write_text(tampered, encoding="utf-8")
    with pytest.raises(ValidationError, match="LOCK"):
        load_config(p)


def test_env_override_non_lock(monkeypatch):
    """M-6 ② ENV 오버라이드 — 비-LOCK 키 허용."""
    monkeypatch.setenv("VAMOS_LLM_TEMPERATURE", "0.7")
    cfg = load_config(CONFIG_PATH)
    assert cfg.llm.temperature == 0.7


def test_env_override_underscore_section(monkeypatch):
    """섹션명 최장 일치 — vector_db 등 언더스코어 섹션."""
    monkeypatch.setenv("VAMOS_VECTOR_DB_COLLECTION_NAME", '"alt_collection"')
    cfg = load_config(CONFIG_PATH)
    assert cfg.vector_db.collection_name == "alt_collection"


def test_env_override_lock_rejected(monkeypatch):
    """M-6: LOCK 값은 어떤 단계에서도 변경 불가 — ENV 시도 거부."""
    monkeypatch.setenv("VAMOS_COST_BLOCK_THRESHOLD", "95")
    with pytest.raises(ValueError, match="LOCK"):
        load_config(CONFIG_PATH)


def test_cli_override_beats_env(monkeypatch):
    """M-6 우선순위: CLI > ENV > TOML."""
    monkeypatch.setenv("VAMOS_LLM_TEMPERATURE", "0.7")
    cfg = load_config(CONFIG_PATH, cli_args=["llm.temperature=0.9"])
    assert cfg.llm.temperature == 0.9


def test_cli_override_lock_rejected():
    with pytest.raises(ValueError, match="LOCK"):
        load_config(CONFIG_PATH, cli_args=["approval.timeout_s=10"])


def test_data_dir_expansion(monkeypatch):
    """${VAMOS_DATA_DIR} 치환 — ENV 우선, 부재 시 .env.example 기본 ./data."""
    monkeypatch.delenv("VAMOS_DATA_DIR", raising=False)
    cfg = load_config(CONFIG_PATH)
    assert cfg.storage.db_path == "./data/sqlite/vamos.db"
    monkeypatch.setenv("VAMOS_DATA_DIR", "/srv/vamos")
    cfg2 = load_config(CONFIG_PATH)
    assert cfg2.vector_db.persist_directory == "/srv/vamos/chroma"


def test_get_config_singleton(monkeypatch):
    monkeypatch.setenv("VAMOS_CONFIG_PATH", str(CONFIG_PATH))
    a = get_config()
    b = get_config()
    assert a is b


def test_rbac_roles_loaded():
    cfg = load_config(CONFIG_PATH)
    assert set(cfg.rbac.roles) == {"OWNER", "ADMIN", "OPERATOR", "VIEWER"}
    assert cfg.rbac.roles["OWNER"].max_autonomy == "L3"
    assert cfg.rbac.roles["VIEWER"].can_execute is False
