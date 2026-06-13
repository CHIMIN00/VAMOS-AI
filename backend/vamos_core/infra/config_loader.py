"""config.v1.toml 로더 — VamosConfig + 서브모델 14종 (V0-STEP-5 / 로드맵 4-5).

정본: PHASE_B4_CONFIG_SPEC §3 (V0 = 14섹션: B4 13 + [confidence] — PHASE4-DEC-003).
3단계 로딩 (M-6): ① TOML → ② ENV(VAMOS_{SECTION}_{KEY}) → ③ CLI. 우선순위 CLI > ENV > TOML.
LOCK 23키(D13 20 + DEC-010 confidence 3)는 어떤 단계에서도 변경 불가 — 정본 값과 다르면
ValidationError, 인스턴스는 frozen(런타임 변경 시 에러 — Defense Layer 1, PHASE3-DEC-008).
"""

from __future__ import annotations

import os
import re
import tomllib
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator

#: 리포 루트 (backend/vamos_core/infra/ → 3단계 상위)
_REPO_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_CONFIG_PATH = _REPO_ROOT / "config" / "config.v1.toml"

#: ${VAR} 치환 기본값 — .env.example 정본 (PHASE4-DEC-009)
_ENV_DEFAULTS = {"VAMOS_DATA_DIR": "./data"}

#: LOCK 23키 정본 값 (D13 20 + PHASE3-DEC-010 3 — scripts/check_config_lock.py와 동일 분모).
#: blue_nodes.active_node_cap / ui.min_width 2키는 V1+ 섹션 — V0 물리 21키만 검증 대상.
_LOCK_VALUES: dict[tuple[str, str], Any] = {
    ("core", "single_decision_lock"): True,
    ("embedding", "model"): "bge-m3",
    ("embedding", "dimension"): 1024,
    ("vector_db", "backend"): "chroma",
    ("graph_db", "backend"): "json_file",
    ("cost", "daily_limit"): 1300,  # ABSOLUTE LOCK
    ("cost", "monthly_limit"): 40000,  # ABSOLUTE LOCK
    ("cost", "warn_threshold"): 80,
    ("cost", "block_threshold"): 100,
    ("semantic_cache", "similarity_threshold"): 0.95,
    ("logging", "trace_id_required"): True,
    ("mcp", "transport"): "streamable_http",
    ("self_check", "threshold_p0"): 70,
    ("self_check", "threshold_p1"): 75,
    ("self_check", "threshold_p2"): 80,
    ("self_check", "soft_loop_max"): 1,
    ("approval", "timeout_s"): 600,
    ("approval", "p2_timeout_s"): 300,
    ("blue_nodes", "active_node_cap"): 3,
    ("ui", "min_width"): 1280,
    ("confidence", "confidence_high_threshold"): 0.85,
    ("confidence", "confidence_medium_threshold"): 0.60,
    ("confidence", "confidence_refuse_threshold"): 0.30,
}


class _FrozenSection(BaseModel):
    """서브모델 공통 — frozen(R5: LOCK 런타임 변경 시 ValidationError) + extra='forbid'(R2)."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class CoreConfig(_FrozenSection):
    """PHASE_B4 §3.1 + [core] ipc 2키 (PHASE4-DEC-009/FIX-027)."""

    autonomy_level: str
    default_execution_mode: str
    max_decision_timeout_ms: int
    single_decision_lock: bool
    pipeline_stages: list[str]
    ipc_max_restart: int
    ipc_timeout_s: int


class LLMConfig(_FrozenSection):
    """PHASE_B4 §3.2."""

    mini_model: str
    main_model: str
    fallback_model: str
    temperature: float
    max_tokens: int
    streaming_enabled: bool
    prompt_cache_enabled: bool
    prompt_cache_ttl_sec: int


class EmbeddingConfig(_FrozenSection):
    """PHASE_B4 §3.3."""

    model: str
    dimension: int
    matryoshka_dim: int
    batch_size: int
    local_enabled: bool


class VectorDBConfig(_FrozenSection):
    """PHASE_B4 §3.4."""

    backend: str
    mode: str
    collection_name: str
    persist_directory: str
    similarity_metric: str


class GraphDBConfig(_FrozenSection):
    """PHASE_B4 §3.5."""

    backend: str
    json_path: str
    max_hops: int
    scope: str
    cache_enabled: bool


class StorageConfig(_FrozenSection):
    """PHASE_B4 §3.6 — memory TTL 포함 (별도 [memory] 섹션 없음)."""

    backend: str
    db_path: str
    log_format: str
    log_path: str
    backup_enabled: bool
    backup_schedule: str
    backup_retain_count: int
    memory_ttl_L0: str  # noqa: N815 — B4 §3.6 정본 키명 그대로 (창작 금지)
    memory_ttl_L1: str  # noqa: N815
    memory_ttl_L2: str  # noqa: N815
    memory_ttl_L3: str  # noqa: N815


class CostConfig(_FrozenSection):
    """PHASE_B4 §3.7 + alert_thresholds (PHASE4-DEC-002 병존)."""

    daily_limit: int
    monthly_limit: int
    warn_threshold: int
    block_threshold: int
    alert_thresholds: list[int]
    downshift_model: str
    currency: str
    tracking_enabled: bool


class SelfCheckConfig(_FrozenSection):
    """PHASE_B4 §3.8a (LOCK 4키)."""

    threshold_p0: int
    threshold_p1: int
    threshold_p2: int
    soft_loop_max: int


class ApprovalConfig(_FrozenSection):
    """PHASE_B4 §3.8b (LOCK 2키)."""

    timeout_s: int
    p2_timeout_s: int


class MCPConfig(_FrozenSection):
    """PHASE_B4 §3.9."""

    transport: str
    default_timeout_ms: int
    max_retries: int
    bridges: list[dict[str, Any]]


class RBACRoleEntry(_FrozenSection):
    """PHASE_B4 §3.10 역할 항목."""

    description: str
    can_configure: bool
    can_approve: bool
    can_execute: bool
    can_view: bool
    max_autonomy: str


class RBACConfig(_FrozenSection):
    """PHASE_B4 §3.10."""

    default_role: str
    roles: dict[str, RBACRoleEntry]


class LoggingConfig(_FrozenSection):
    """PHASE_B4 §3.12."""

    level: str
    format: str
    trace_id_required: bool
    sinks: list[str]


class SemanticCacheConfig(_FrozenSection):
    """PHASE_B4 §3.15."""

    enabled: bool
    similarity_threshold: float
    max_entries: int
    ttl_sec: int


class ConfidenceConfig(_FrozenSection):
    """PHASE_B4 §3.16 — PHASE3-DEC-010 LOCK 3키 (R1-A25)."""

    confidence_high_threshold: float
    confidence_medium_threshold: float
    confidence_refuse_threshold: float


class VamosConfig(_FrozenSection):
    """V0 활성 14섹션 (B4 13 + confidence — PART2 V0-STEP-5/XREF-V0-18, PHASE4-DEC-003)."""

    core: CoreConfig
    llm: LLMConfig
    embedding: EmbeddingConfig
    vector_db: VectorDBConfig
    graph_db: GraphDBConfig
    storage: StorageConfig
    cost: CostConfig
    self_check: SelfCheckConfig
    approval: ApprovalConfig
    mcp: MCPConfig
    rbac: RBACConfig
    logging: LoggingConfig
    semantic_cache: SemanticCacheConfig
    confidence: ConfidenceConfig

    @model_validator(mode="after")
    def _enforce_lock_values(self) -> VamosConfig:
        """LOCK 키가 정본 값과 다르면 거부 (R5 / §1.3.1 #2 — Defense Layer 1)."""
        violations = []
        for (section, key), expected in _LOCK_VALUES.items():
            sec = getattr(self, section, None)
            if sec is None:  # blue_nodes/ui — V1+ 섹션, V0 부재 정상
                continue
            actual = getattr(sec, key)
            if actual != expected:
                violations.append(f"{section}.{key}: LOCK {expected!r} != {actual!r}")
        if violations:
            raise ValueError("LOCK 위반(변경 불가 — D13/DEC-010): " + "; ".join(violations))
        return self


def _expand_vars(value: Any) -> Any:
    """문자열 내 ${VAR} 치환 — ENV 우선, 부재 시 .env.example 기본값."""
    if isinstance(value, str):
        return re.sub(
            r"\$\{(\w+)\}",
            lambda m: os.environ.get(m.group(1), _ENV_DEFAULTS.get(m.group(1), m.group(0))),
            value,
        )
    if isinstance(value, dict):
        return {k: _expand_vars(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand_vars(v) for v in value]
    return value


def _coerce(raw: str) -> Any:
    """ENV/CLI 문자열 값을 TOML 리터럴로 해석 (실패 시 문자열 그대로)."""
    try:
        return tomllib.loads(f"v = {raw}")["v"]
    except tomllib.TOMLDecodeError:
        return raw


_SECTIONS = tuple(sorted(VamosConfig.model_fields, key=len, reverse=True))


def _apply_override(data: dict[str, Any], section: str, key: str, raw: str, origin: str) -> None:
    """단일 오버라이드 적용 — LOCK 키는 어떤 단계에서도 변경 불가 (M-6)."""
    value = _coerce(raw)
    lock_expected = _LOCK_VALUES.get((section, key))
    if (section, key) in _LOCK_VALUES and value != lock_expected:
        raise ValueError(
            f"{origin} 오버라이드 거부 — {section}.{key}는 LOCK(정본 {lock_expected!r}, R5/M-6)"
        )
    data.setdefault(section, {})[key] = value


def _env_overrides(data: dict[str, Any]) -> None:
    """② 환경변수 VAMOS_{SECTION}_{KEY} — 섹션명 최장 일치(vector_db 등 언더스코어 섹션 대응)."""
    for name, raw in os.environ.items():
        if not name.startswith("VAMOS_"):
            continue
        body = name[len("VAMOS_") :].lower()
        for section in _SECTIONS:
            if body.startswith(section + "_"):
                _apply_override(data, section, body[len(section) + 1 :], raw, f"ENV {name}")
                break
        # 섹션 불일치(VAMOS_DATA_DIR 등 비-config 변수)는 오버라이드 아님 — 무시


def _cli_overrides(data: dict[str, Any], cli_args: list[str]) -> None:
    """③ CLI 인자 'section.key=value' 형식."""
    for arg in cli_args:
        target, _, raw = arg.partition("=")
        section, _, key = target.partition(".")
        if not (section and key and raw):
            raise ValueError(f"CLI 인자 형식 오류(section.key=value): {arg!r}")
        _apply_override(data, section, key, raw, f"CLI {arg}")


def load_config(
    config_path: str | os.PathLike[str] | None = None,
    cli_args: list[str] | None = None,
) -> VamosConfig:
    """3단계 로딩 (M-6): TOML → ENV → CLI. LOCK은 전 단계 변경 불가."""
    path = Path(config_path or os.environ.get("VAMOS_CONFIG_PATH") or _DEFAULT_CONFIG_PATH)
    with open(path, "rb") as f:
        data: dict[str, Any] = tomllib.load(f)
    _env_overrides(data)
    _cli_overrides(data, cli_args or [])
    return VamosConfig.model_validate(_expand_vars(data))


_CONFIG_CACHE: VamosConfig | None = None


def get_config() -> VamosConfig:
    """싱글톤 — 캐시된 VamosConfig 반환 (M-6)."""
    global _CONFIG_CACHE  # noqa: PLW0603 — 싱글톤 캐시
    if _CONFIG_CACHE is None:
        _CONFIG_CACHE = load_config()
    return _CONFIG_CACHE


def reset_config_cache() -> None:
    """테스트 전용 — 싱글톤 캐시 초기화."""
    global _CONFIG_CACHE  # noqa: PLW0603
    _CONFIG_CACHE = None
