"""schemas/seed/registries.json → backend/vamos_core/schemas/registries.py 기계 생성 (P4-0).

값 목록은 seed(= D2.1-D2 SOT 기계 추출)에서 그대로 임베드 — 수동 전사 0.
사용: python scripts/gen_registries_py.py
"""

import io
import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).resolve().parent.parent
seed = json.loads((ROOT / "schemas" / "seed" / "registries.json").read_text(encoding="utf-8"))
regs = seed["registries"]

ev = regs["EventTypeRegistry"]["values"]
fc = regs["FailureCodeRegistry"]["values"]
fb = regs["FallbackRegistry"]["values"]
tools = regs["ToolRegistry"]["seed_entries"]
nodes = regs["NodeRegistry"]["seed_entries"]

assert len(ev) == 123 and len(fc) == 36 and len(fb) == 23, "레지스트리 분모 불일치 — 중단"


def tup(values: list[str], indent: str = "    ") -> str:
    return "\n".join(f'{indent}"{v}",' for v in values)


ev_lines = tup(ev)
fc_lines = tup(fc)
fb_lines = tup(fb)
def entry_lines(entries: list[dict]) -> str:
    """E501 방지 — dict를 4-space 들여쓴 멀티라인 리터럴로 임베드."""
    blocks = []
    for e in entries:
        dumped = json.dumps(e, ensure_ascii=False, indent=4)
        dumped = dumped.replace(": true", ": True").replace(": false", ": False").replace(": null", ": None")
        blocks.append("    " + dumped.replace("\n", "\n    "))
    return ",\n".join(blocks)


tool_lines = entry_lines(tools)
node_lines = entry_lines(nodes)

content = f'''"""VAMOS 레지스트리 5종 (V0) — D2.1-D2 §5 SOT + D2.1-D4 §4.1 + D2.1-D3 §4.1.

자동 생성: scripts/gen_registries_py.py (P4-0, 2026-06-12) — 직접 수정 금지.
값 변경은 SOT(D2.1) 개정 + seed 재추출 + 본 파일 재생성으로만 수행 (A20 준용).
분모: EventType 123 / FailureCode 36 / Fallback 23 / Tool seed 2 / Node seed 1.
네이밍: event=lower.dot / failure=UPPER_SNAKE / fallback=FB_UPPER_SNAKE (VL-005).
"""

from __future__ import annotations

from typing import Any, Final

#: EventTypeRegistry — D2.1-D2 §5.1 (123, lower.dot)
EVENT_TYPES: Final[tuple[str, ...]] = (
{ev_lines}
)

#: FailureCodeRegistry — D2.1-D2 §5.2 (36, UPPER_SNAKE)
FAILURE_CODES: Final[tuple[str, ...]] = (
{fc_lines}
)

#: FallbackRegistry — D2.1-D2 §5.3 (23, FB_UPPER_SNAKE)
FALLBACK_IDS: Final[tuple[str, ...]] = (
{fb_lines}
)

#: ToolRegistry seed — D2.1-D4 §4.1 (2 seed entries; 정본 목록 확정은 G2 이후)
TOOL_REGISTRY_SEED: Final[tuple[dict[str, Any], ...]] = (
{tool_lines},
)

#: NodeRegistry seed — D2.1-D3 §4.1 (1 seed entry; node_id/domain 필수 LOCK)
NODE_REGISTRY_SEED: Final[tuple[dict[str, Any], ...]] = (
{node_lines},
)

EVENT_TYPE_SET: Final[frozenset[str]] = frozenset(EVENT_TYPES)
FAILURE_CODE_SET: Final[frozenset[str]] = frozenset(FAILURE_CODES)
FALLBACK_ID_SET: Final[frozenset[str]] = frozenset(FALLBACK_IDS)


def is_valid_event_type(value: str) -> bool:
    """EventTypeRegistry 등재 여부 (LogEventSchema.event_type 검증용)."""
    return value in EVENT_TYPE_SET


def is_valid_failure_code(value: str) -> bool:
    """FailureCodeRegistry 등재 여부."""
    return value in FAILURE_CODE_SET


def is_valid_fallback_id(value: str) -> bool:
    """FallbackRegistry 등재 여부."""
    return value in FALLBACK_ID_SET
'''

out = ROOT / "backend" / "vamos_core" / "schemas" / "registries.py"
with io.open(out, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)
print(f"✅ {out.relative_to(ROOT)} 생성 (EventType {len(ev)} / FailureCode {len(fc)} / Fallback {len(fb)} / Tool {len(tools)} / Node {len(nodes)})")
