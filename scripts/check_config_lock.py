"""config.v1.toml LOCK 값 검증 (Phase 2-4 코드 생산 Hook — STRATEGY_10 §4 4-V4).

CLAUDE.md §20 / PHASE_B4_CONFIG_SPEC 정본 LOCK 20키 (D13 확정 분모).
config.v1.toml 수정 시 Hook이 호출 — LOCK 값이 정본과 다르면 위반 보고.
파일 부재 시(V0-STEP 이전) 정상 종료.

사용: python scripts/check_config_lock.py [config 경로]
"""

import sys
import os

# Windows cp949 콘솔에서 — / ✅ 출력 UnicodeEncodeError 방지 (P4-0 도구 점검 수리)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    import tomllib  # Python 3.11+
except ImportError:  # pragma: no cover
    print("[LOCK-CHECK] tomllib 불가(Python<3.11) — 검증 스킵")
    sys.exit(0)

# CLAUDE.md §20 정본 — LOCK 20키 (D13: PHASE_B4 §3 LOCK 10 ∪ BASE-1.3/DESIGN 2.0 LOCK 12, 중복 2 제외)
LOCK_KEYS = {
    ("core", "single_decision_lock"): True,
    ("embedding", "model"): "bge-m3",
    ("embedding", "dimension"): 1024,
    ("vector_db", "backend"): "chroma",
    ("graph_db", "backend"): "json_file",
    ("cost", "daily_limit"): 1300,        # ABSOLUTE LOCK
    ("cost", "monthly_limit"): 40000,     # ABSOLUTE LOCK
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
}


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join("config", "config.v1.toml")
    if not os.path.isfile(path):
        print(f"[LOCK-CHECK] {path} 부재 — V0-STEP 이전 단계, 검증 스킵 (OK)")
        return 0
    with open(path, "rb") as f:
        cfg = tomllib.load(f)
    violations = []
    missing = []
    for (section, key), expected in LOCK_KEYS.items():
        sec = cfg.get(section)
        if not isinstance(sec, dict) or key not in sec:
            missing.append(f"{section}.{key}")
            continue
        actual = sec[key]
        if actual != expected:
            violations.append(f"{section}.{key}: 기대 {expected!r} != 실제 {actual!r}")
    if violations:
        print(f"[LOCK-CHECK] ❌ LOCK 위반 {len(violations)}건 — LOCK 값 변경 절대 금지 (D13/R5):")
        for v in violations:
            print(f"  - {v}")
        return 2
    msg = f"[LOCK-CHECK] ✅ LOCK 20키 위반 0건 ({path})"
    if missing:
        msg += f" · 미정의 {len(missing)}키(스캐폴딩 단계 허용): {', '.join(missing[:5])}..."
    print(msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
