"""EA JSON schema normalizer - fixes DV-1 CRITICAL issues"""
import json, hashlib, os, sys, glob, re

SOT_DIR = r"D:\VAMOS\docs\sot"
EA_DIR = r"D:\VAMOS\04. 구현단계\v13_results\phase0\extraction"

REQUIRED_META = ["agent", "version", "created", "source_files", "source_file_hashes", "total_lines_read", "total_items_extracted", "categories"]
REQUIRED_ITEM = ["item_id", "category", "source_file", "source_line", "source_text", "key", "value", "value_type", "context"]
CATEGORIES = ["C1","C2","C3","C4","C5","C6","C7","C8"]

def compute_hash(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return hashlib.sha256(f.read().encode("utf-8")).hexdigest()
    except:
        return "FILE_NOT_FOUND"

def count_lines(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)
    except:
        return 0

def find_sot_file(name):
    path = os.path.join(SOT_DIR, name)
    if os.path.exists(path):
        return path
    for fn in os.listdir(SOT_DIR):
        if name.lower() in fn.lower():
            return os.path.join(SOT_DIR, fn)
    return None

def infer_value_type(value):
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, list):
        return "list"
    if isinstance(value, dict):
        return "list"
    return "string"

def normalize_ea(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    basename = os.path.basename(filepath)
    m = re.search(r'EA(\d+)', basename)
    ea_num = int(m.group(1)) if m else 0

    meta = data.get("metadata", {})
    items = data.get("items", [])
    changes = 0

    if "agent" not in meta:
        meta["agent"] = f"EA-{ea_num}"
        changes += 1

    if "version" not in meta:
        meta["version"] = meta.get("agent_version", "v13")
        changes += 1

    if "created" not in meta:
        meta["created"] = meta.get("created_at", meta.get("extraction_date", "2026-03-21"))
        changes += 1

    if "source_files" not in meta:
        src_files = meta.get("sources", [])
        if isinstance(src_files, list) and src_files:
            if isinstance(src_files[0], dict):
                src_files = [s.get("file","") for s in src_files]
        if not src_files:
            sf_key = "source_file" if items and "source_file" in items[0] else "source_doc"
            src_files = sorted(set(it.get(sf_key, "") for it in items if it.get(sf_key)))
        meta["source_files"] = src_files
        changes += 1
    else:
        # Normalize source_files if it contains dicts
        sf = meta["source_files"]
        if isinstance(sf, list) and sf and isinstance(sf[0], dict):
            meta["source_files"] = [s.get("file","") for s in sf]
            changes += 1

    if "source_file_hashes" not in meta:
        hashes = {}
        for sf in meta.get("source_files", []):
            sot_path = find_sot_file(sf)
            if sot_path:
                hashes[sf] = compute_hash(sot_path)
            else:
                hashes[sf] = "NOT_FOUND"
        meta["source_file_hashes"] = hashes
        changes += 1

    if "total_lines_read" not in meta:
        total = 0
        for sf in meta.get("source_files", []):
            sot_path = find_sot_file(sf)
            if sot_path:
                total += count_lines(sot_path)
        meta["total_lines_read"] = total
        changes += 1

    actual_cats = {c: 0 for c in CATEGORIES}
    for it in items:
        cat = it.get("category", "")
        if cat in actual_cats:
            actual_cats[cat] += 1
    meta["categories"] = actual_cats
    meta["total_items_extracted"] = len(items)

    standard_meta = {}
    for k in REQUIRED_META:
        standard_meta[k] = meta.get(k)

    for i, item in enumerate(items):
        if "item_id" not in item:
            if "id" in item:
                item["item_id"] = item.pop("id")
            else:
                item["item_id"] = f"EA-{ea_num:02d}_{i+1:03d}"
            changes += 1

        if "source_file" not in item:
            item["source_file"] = item.get("source_doc", item.get("file", ""))
            changes += 1

        if "key" not in item:
            item["key"] = item.get("field", item.get("label", item.get("name", f"UNKEYED_{i}")))
            changes += 1

        if "value" not in item:
            item["value"] = item.get("lock", item.get("content", None))
            changes += 1

        if "value_type" not in item:
            item["value_type"] = infer_value_type(item.get("value"))
            changes += 1

        if "context" not in item:
            item["context"] = item.get("description", item.get("sub_type", item.get("unit", "")))
            changes += 1

        for field in REQUIRED_ITEM:
            if field not in item:
                if field == "source_line":
                    item[field] = 0
                elif field == "source_text":
                    item[field] = ""
                else:
                    item[field] = None
                changes += 1

        normalized = {}
        for k in REQUIRED_ITEM:
            normalized[k] = item[k]
        for k in ["confidence", "note", "unit"]:
            if k in item:
                normalized[k] = item[k]
        items[i] = normalized

    output = {"metadata": standard_meta, "items": items}

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    return basename, len(items), changes


ea_files = sorted(glob.glob(os.path.join(EA_DIR, "v13_EA*.json")))
print(f"Processing {len(ea_files)} EA files...")

for fp in ea_files:
    name, items, nchanges = normalize_ea(fp)
    print(f"  {name}: {items} items, {nchanges} fixes")

print(f"Done. {len(ea_files)} files normalized.")
