"""VAMOS 커스텀 린터 (Layer 1 — STRATEGY_09 §8.2, Phase 2-5).

PART2 §1.3 R1~R11 + CLAUDE.md §7 LOCK 결정사항 중 ruff로 검사 불가능한 규칙 검증.

검사 항목:
  VL-001: class Config: 사용 금지 (R2 — Pydantic v2는 model_config = ConfigDict(...))
  VL-002: S-#(모듈 ID, 하이픈) vs S#_(상태, 언더스코어) 네이밍 혼동 검사
  VL-003: CORE→COND 역방향 import 금지 (R7 — orange_core가 COND 모듈 import 불가)
  VL-004: LOCK/FREEZE 상수 재할당 검사 (R5 — LOCK config 키 런타임 덮어쓰기 금지)
  VL-005: 파일명/상수 네이밍 규칙 (event=lower.dot, failure=UPPER_SNAKE, fallback=FB_UPPER_SNAKE)

사용: python scripts/vamos_lint.py <검사 루트 디렉토리> [--mode warn|error]
  - 기본 mode=error. 오탐 발생 시(A1, 리스크 R05) --mode warn으로 시작 → 안정화 후 error 전환.
종료 코드: 0=위반 없음(또는 warn 모드), 1=위반 존재(error 모드)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------- 규칙 정의

# VL-001: Pydantic v1 스타일 class Config (모델 내부 들여쓰기 1단 이상)
RE_CLASS_CONFIG = re.compile(r"^\s+class\s+Config\s*[:(]", re.M)
RE_PYDANTIC_HINT = re.compile(r"\bpydantic\b|\bBaseModel\b", re.I)

# VL-002: 상태 표기는 S#_ (S0_RECEIVED), 모듈 ID는 S-# (S-1)
RE_STATE_AS_MODULE = re.compile(r"""["']S-\d+_[A-Z]""")          # S-1_RECEIVED 같은 혼동
RE_MODULE_AS_STATE = re.compile(r"""["']S\d+-[A-Za-z]""")        # S1-... 같은 혼동

# VL-003: orange_core(CORE) → COND 모듈 import 금지 (R7)
RE_COND_IMPORT = re.compile(r"^\s*(?:from|import)\s+(?:\S*\.)?(cond_modules|cond)\b", re.M)

# VL-004: LOCK config 키 재할당 (semantic_cache.similarity_threshold = ... 등 코드 내 덮어쓰기)
LOCK_KEY_TAILS = [
    "single_decision_lock", "daily_limit", "monthly_limit", "warn_threshold",
    "block_threshold", "similarity_threshold", "trace_id_required",
    "threshold_p0", "threshold_p1", "threshold_p2", "soft_loop_max",
    "timeout_s", "p2_timeout_s", "active_node_cap", "min_width",
]
RE_LOCK_ASSIGN = re.compile(
    r"^\s*(?:config|cfg|settings)\s*(?:\.|\[)[^=\n]*(?:" + "|".join(LOCK_KEY_TAILS) + r")[^=\n]*=\s*[^=]",
    re.M,
)

# VL-005: 네이밍 상수 규칙
RE_EVENT_BAD = re.compile(r"""(?:EVENT|event_type)\s*=\s*["']([A-Z][A-Z0-9_.]*)["']""")     # event는 lower.dot
RE_FAILURE_BAD = re.compile(r"""(?:FAILURE|failure_code)\s*=\s*["']([a-z][a-z0-9_.]*)["']""")  # failure는 UPPER_SNAKE
RE_FALLBACK_BAD = re.compile(r"""(?:FALLBACK|fallback_id)\s*=\s*["'](?!FB_)([A-Za-z0-9_.]+)["']""")  # FB_ 접두 필수


def lint_file(path: Path, text: str) -> list[tuple[str, int, str]]:
    """단일 파일 검사 → [(rule_id, line_no, message)]."""
    findings: list[tuple[str, int, str]] = []

    def line_of(pos: int) -> int:
        return text.count("\n", 0, pos) + 1

    # VL-001 — Pydantic 맥락 파일에서만
    if RE_PYDANTIC_HINT.search(text):
        for m in RE_CLASS_CONFIG.finditer(text):
            findings.append(("VL-001", line_of(m.start()),
                             "class Config: 금지 — Pydantic v2 model_config = ConfigDict(...) 사용 (R2)"))

    # VL-002
    for m in RE_STATE_AS_MODULE.finditer(text):
        findings.append(("VL-002", line_of(m.start()),
                         "S-#는 모듈 ID(하이픈) — 상태는 S#_(언더스코어) 사용 (CLAUDE.md §7.1)"))
    for m in RE_MODULE_AS_STATE.finditer(text):
        findings.append(("VL-002", line_of(m.start()),
                         "S#-는 잘못된 표기 — 모듈 ID는 S-#, 상태는 S#_ (CLAUDE.md §7.1)"))

    # VL-003 — orange_core 하위 파일에서만
    parts = {p.lower() for p in path.parts}
    if "orange_core" in parts:
        for m in RE_COND_IMPORT.finditer(text):
            findings.append(("VL-003", line_of(m.start()),
                             "CORE→COND 역방향 import 금지 (R7) — COND는 CORE 소비만 가능"))

    # VL-004
    for m in RE_LOCK_ASSIGN.finditer(text):
        findings.append(("VL-004", line_of(m.start()),
                         "LOCK config 키 런타임 재할당 금지 (R5/D13) — config.v1.toml LOCK 값은 불변"))

    # VL-005
    for m in RE_EVENT_BAD.finditer(text):
        findings.append(("VL-005", line_of(m.start()),
                         f"event 이름 '{m.group(1)}'은 lower.dot 형식이어야 함 (예: oc.intent.parsed)"))
    for m in RE_FAILURE_BAD.finditer(text):
        findings.append(("VL-005", line_of(m.start()),
                         f"failure 코드 '{m.group(1)}'은 UPPER_SNAKE 형식이어야 함 (예: INTENT_PARSE_FAILED)"))
    for m in RE_FALLBACK_BAD.finditer(text):
        findings.append(("VL-005", line_of(m.start()),
                         f"fallback ID '{m.group(1)}'은 FB_ 접두 UPPER_SNAKE 형식이어야 함 (예: FB_COST_DOWNSHIFT)"))

    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description="VAMOS custom linter (VL-001~005)")
    ap.add_argument("root", nargs="?", default="backend", help="검사 루트 디렉토리")
    ap.add_argument("--mode", choices=["warn", "error"], default="error",
                    help="warn: 위반을 경고만 (exit 0) / error: 위반 시 exit 1")
    args = ap.parse_args()

    root = Path(args.root)
    if not root.exists():
        print(f"[vamos_lint] 루트 '{root}' 부재 — 검사 대상 없음 (OK)")
        return 0

    total: list[tuple[Path, str, int, str]] = []
    n_files = 0
    for py in sorted(root.rglob("*.py")):
        # 가상환경/캐시 제외
        sparts = {p.lower() for p in py.parts}
        if sparts & {".venv", "venv", "__pycache__", "node_modules", ".git"}:
            continue
        n_files += 1
        try:
            text = py.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError) as e:
            print(f"[vamos_lint] 읽기 실패 {py}: {e}")
            continue
        for rule, line, msg in lint_file(py, text):
            total.append((py, rule, line, msg))

    for py, rule, line, msg in total:
        print(f"{py}:{line}: {rule} {msg}")
    print(f"[vamos_lint] 파일 {n_files}개 검사 — 위반 {len(total)}건 (mode={args.mode})")
    if total and args.mode == "error":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
