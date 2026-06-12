# P4-0 STEP 7 R3 — Stage Gate #8: seed JSON ↔ contracts.py 필드명/필수성 교차 검증
import json
import pathlib
import sys

ROOT = pathlib.Path(r"D:\VAMOS")
sys.path.insert(0, str(ROOT / "backend"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from vamos_core.schemas import contracts as c  # noqa: E402

PAIRS = {
    "decision_schema.json": c.DecisionSchema,
    "response_envelope.json": c.ResponseEnvelope,
    "intent_frame.json": c.IntentFrame,
    "evidence_pack.json": c.EvidencePack,
}
fail = 0
for fname, model in PAIRS.items():
    seed = json.loads((ROOT / "schemas" / "seed" / fname).read_text(encoding="utf-8"))
    seed_fields = [(f["name"], bool(f["required"])) for f in seed["fields"]]
    model_fields = [(n, f.is_required()) for n, f in model.model_fields.items()]
    if seed_fields == model_fields:
        print(f"  {fname} ↔ {model.__name__}: {len(seed_fields)}필드 이름·순서·필수성 일치 OK")
    else:
        fail += 1
        print(f"  ❌ {fname} 불일치:")
        print(f"     seed : {seed_fields}")
        print(f"     model: {model_fields}")

reg = json.loads((ROOT / "schemas" / "seed" / "registries.json").read_text(encoding="utf-8"))["registries"]
from vamos_core.schemas import registries as r  # noqa: E402

checks = [
    ("EventType", tuple(reg["EventTypeRegistry"]["values"]), r.EVENT_TYPES),
    ("FailureCode", tuple(reg["FailureCodeRegistry"]["values"]), r.FAILURE_CODES),
    ("Fallback", tuple(reg["FallbackRegistry"]["values"]), r.FALLBACK_IDS),
]
for name, seed_vals, py_vals in checks:
    if seed_vals == py_vals:
        print(f"  registries.json ↔ registries.py {name}: {len(py_vals)} 전건 일치 OK")
    else:
        fail += 1
        print(f"  ❌ {name} 불일치")

sys.exit(1 if fail else 0)
