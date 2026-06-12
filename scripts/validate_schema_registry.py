"""schema_registry.toml ↔ contracts.py 일관성 검증 (PART2 V0-STEP-2 #4).

검사:
  1. TOML 파싱 유효 + 필수 섹션(sqlite.tables/chroma.collections/jsonl.files) 존재
  2. chroma embedding 차원 = 1024 (config LOCK embedding.dimension — D13)
  3. jsonl trace_log의 trace_id 컬럼 존재 (LOCK trace_id_required와 정합)
  4. 참조 모델(MemoryRecord/LogEventSchema)이 contracts.py에 실재

사용: python scripts/validate_schema_registry.py  (종료 0=PASS)
"""

from __future__ import annotations

import pathlib
import sys
import tomllib

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from vamos_core.schemas import contracts as c  # noqa: E402


def main() -> int:
    path = ROOT / "config" / "schema_registry.toml"
    with open(path, "rb") as f:
        reg = tomllib.load(f)

    errors: list[str] = []

    for section, key in (("sqlite", "tables"), ("chroma", "collections"), ("jsonl", "files")):
        if key not in reg.get(section, {}):
            errors.append(f"[{section}.{key}] 섹션 부재")

    cols = reg.get("chroma", {}).get("collections", {}).get("memory_long", [])
    if not any("VECTOR(1024)" in col for col in cols):
        errors.append("chroma.memory_long embedding 차원 1024(LOCK) 불일치")

    trace_cols = reg.get("jsonl", {}).get("files", {}).get("trace_log", [])
    if not any(col.startswith("trace_id:") for col in trace_cols):
        errors.append("jsonl.trace_log에 trace_id 컬럼 부재 (LOCK trace_id_required)")

    for model_name in ("MemoryRecord", "LogEventSchema"):
        if not hasattr(c, model_name):
            errors.append(f"contracts.py에 {model_name} 부재")

    if errors:
        print("❌ schema_registry 일관성 위반:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("✅ schema_registry.toml ↔ contracts.py 일관성 PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
