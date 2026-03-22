import json
from pathlib import Path

merged_path = r"D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_merged_features.json"
delta_path  = r"D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_v10_delta.json"
output_path = r"D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_feature_registry_final.json"

with open(merged_path, "r", encoding="utf-8") as f:
    merged = json.load(f)

with open(delta_path, "r", encoding="utf-8") as f:
    delta = json.load(f)

features = merged["features"]
total = len(features)

# by_version
by_version = {"V0": 0, "V1": 0, "V2": 0, "V3": 0, "multi": 0}
for ft in features:
    vs = ft.get("version_scope", "")
    if vs in by_version:
        by_version[vs] += 1
    else:
        by_version[vs] = by_version.get(vs, 0) + 1

# by_category
cat_keys = ["orange_core", "blue_nodes", "storage", "safety", "agent", "infra", "mcp", "schemas", "ui", "benchmark", "business"]
by_category = {k: 0 for k in cat_keys}
for ft in features:
    cat = ft.get("category", "")
    if cat in by_category:
        by_category[cat] += 1
    else:
        by_category[cat] = by_category.get(cat, 0) + 1

# extractable
ext_true = sum(1 for ft in features if ft.get("extractable") == True)
ext_false = sum(1 for ft in features if ft.get("extractable") == False)

# vs_v10 from delta metadata
dm = delta["metadata"]
vs_v10 = {
    "v10_total": 3940,
    "v12_total": total,
    "new": dm["v12_only_new"],
    "removed": dm["v10_only_missing"],
    "changed": dm["both_changed"]
}

# sot info from merged metadata
mm = merged["metadata"]

result = {
    "metadata": {
        "version": "v12",
        "created": "2026-03-15",
        "sot_files": 68,
        "sot_lines": 89363,
        "total_features": total,
        "extractable_true": ext_true,
        "extractable_false": ext_false
    },
    "statistics": {
        "by_version": by_version,
        "by_category": by_category,
        "vs_v10": vs_v10
    },
    "features": features
}

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

# Print summary
print("=== v12 Feature Registry Final ===")
print(f"Total features: {total}")
print(f"Extractable true: {ext_true}, false: {ext_false}")
print(f"\nBy version: {json.dumps(by_version, indent=2)}")
print(f"\nBy category: {json.dumps(by_category, indent=2)}")
print(f"\nvs v10: {json.dumps(vs_v10, indent=2)}")
print(f"\nOutput written to: {output_path}")

# Verify
with open(output_path, "r", encoding="utf-8") as f:
    verify = json.load(f)
print(f"\nVerification: loaded {len(verify['features'])} features, keys={list(verify.keys())}")
