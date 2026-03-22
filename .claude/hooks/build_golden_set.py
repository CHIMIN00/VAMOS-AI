#!/usr/bin/env python3
"""
build_golden_set.py - Golden Dataset 자동 구축 및 평가 (A-8)
Python 내장 모듈만 사용.

Usage:
    python build_golden_set.py build [--results-dir <dir>]
    python build_golden_set.py eval <ea_file> [--golden <golden_set.json>]
    python build_golden_set.py status [--golden <golden_set.json>]
"""

import json
import sys
import os
import glob
from datetime import datetime


# Default paths
DEFAULT_RESULTS_DIR = "D:/VAMOS/04. 구현단계/v13_results/phase0/extraction"
DEFAULT_GOLDEN_PATH = "D:/VAMOS/04. 구현단계/v13_results/golden_set.json"
DEFAULT_VALIDATION_DIR = "D:/VAMOS/04. 구현단계/v13_results/phase0/extraction/validation"


def find_quality_gate_results(results_dir: str) -> list:
    """Find all quality gate result files."""
    validation_dir = os.path.join(results_dir, "validation")
    if not os.path.exists(validation_dir):
        return []

    pattern = os.path.join(validation_dir, "*_quality_gate.json")
    return glob.glob(pattern)


def find_audit_results(results_dir: str) -> list:
    """Find all audit result files."""
    audit_dir = os.path.join(results_dir, "audit")
    if not os.path.exists(audit_dir):
        # Try validation dir
        audit_dir = os.path.join(results_dir, "validation")

    if not os.path.exists(audit_dir):
        return []

    pattern = os.path.join(audit_dir, "*_audit.json")
    return glob.glob(pattern)


def is_gold_and_clean(ea_basename: str, results_dir: str) -> bool:
    """Check if an EA has GOLD quality gate and CLEAN audit."""
    validation_dir = os.path.join(results_dir, "validation")
    audit_dir = os.path.join(results_dir, "audit")

    # Check quality gate
    qg_file = os.path.join(validation_dir, f"{ea_basename}_quality_gate.json")
    if os.path.exists(qg_file):
        try:
            with open(qg_file, "r", encoding="utf-8") as f:
                qg = json.load(f)
            verdict = qg.get("gate_metadata", {}).get("verdict", "")
            if verdict != "GOLD":
                return False
        except Exception:
            return False
    else:
        return False

    # Check audit
    audit_file = os.path.join(audit_dir, f"{ea_basename}_audit.json")
    if not os.path.exists(audit_file):
        audit_file = os.path.join(validation_dir, f"{ea_basename}_audit.json")

    if os.path.exists(audit_file):
        try:
            with open(audit_file, "r", encoding="utf-8") as f:
                audit = json.load(f)
            verdict = audit.get("audit_metadata", {}).get("verdict", "")
            if verdict != "CLEAN":
                return False
        except Exception:
            return False
    else:
        return False

    return True


def verify_source_text(item: dict) -> bool:
    """Verify that source_text exists in the source file at source_line."""
    source_file = item.get("source_file", "")
    source_line = item.get("source_line", 0)
    source_text = item.get("source_text", "")

    if not source_file or not source_text:
        return False

    if not os.path.exists(source_file):
        # Try relative to VAMOS root
        alt_path = os.path.join("D:/VAMOS", source_file)
        if os.path.exists(alt_path):
            source_file = alt_path
        else:
            return False

    try:
        with open(source_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if source_line < 1 or source_line > len(lines):
            return False

        # Check ±3 lines around source_line
        start = max(0, source_line - 4)
        end = min(len(lines), source_line + 3)
        context = "".join(lines[start:end])

        # Check if key parts of source_text exist in context
        keywords = [w for w in source_text.split() if len(w) > 2]
        if not keywords:
            return True

        matched = sum(1 for kw in keywords if kw in context)
        return matched / len(keywords) >= 0.5
    except Exception:
        return False


def build_golden_set(results_dir: str, golden_path: str):
    """Build golden set from GOLD + CLEAN EA results."""
    extraction_dir = results_dir

    # Find all EA JSON files
    ea_files = glob.glob(os.path.join(extraction_dir, "v13_EA*.json"))
    if not ea_files:
        print(json.dumps({"error": "No EA files found", "search_dir": extraction_dir}))
        sys.exit(1)

    golden_items = []
    source_eas = []
    skipped_eas = []

    for ea_file in sorted(ea_files):
        ea_basename = os.path.splitext(os.path.basename(ea_file))[0]

        # Check GOLD + CLEAN status
        if not is_gold_and_clean(ea_basename, results_dir):
            skipped_eas.append(ea_basename)
            continue

        # Load EA
        try:
            with open(ea_file, "r", encoding="utf-8") as f:
                ea_data = json.load(f)
        except Exception:
            skipped_eas.append(ea_basename)
            continue

        items = ea_data.get("items", [])
        source_eas.append(ea_basename)
        verified_count = 0

        for item in items:
            # Extract golden fields
            golden_item = {
                "key": item.get("key", ""),
                "value": item.get("value"),
                "value_type": item.get("value_type", ""),
                "category": item.get("category", ""),
                "source_file": item.get("source_file", ""),
                "source_line": item.get("source_line", 0),
                "source_text": item.get("source_text", ""),
                "origin_ea": ea_basename
            }

            # Deterministic verification
            if verify_source_text(item):
                golden_item["sot_verified"] = True
                verified_count += 1
            else:
                golden_item["sot_verified"] = False

            golden_items.append(golden_item)

    # Only keep SOT-verified items
    verified_items = [g for g in golden_items if g.get("sot_verified", False)]

    result = {
        "golden_set_metadata": {
            "total_golden_items": len(verified_items),
            "total_candidates": len(golden_items),
            "sot_verified_count": len(verified_items),
            "source_eas": source_eas,
            "skipped_eas": skipped_eas,
            "build_date": datetime.now().isoformat(),
            "results_dir": results_dir
        },
        "items": verified_items
    }

    # Save
    os.makedirs(os.path.dirname(golden_path) or ".", exist_ok=True)
    with open(golden_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(json.dumps({
        "action": "build",
        "golden_path": golden_path,
        "total_golden_items": len(verified_items),
        "source_eas": source_eas,
        "skipped_eas": skipped_eas
    }, ensure_ascii=False, indent=2))


def eval_against_golden(ea_file: str, golden_path: str):
    """Evaluate an EA file against the golden set."""
    # Load golden set
    if not os.path.exists(golden_path):
        print(json.dumps({"error": f"Golden set not found: {golden_path}. Run 'build' first."}))
        sys.exit(1)

    with open(golden_path, "r", encoding="utf-8") as f:
        golden = json.load(f)

    golden_items = golden.get("items", [])

    # Load EA
    with open(ea_file, "r", encoding="utf-8") as f:
        ea_data = json.load(f)

    ea_items = ea_data.get("items", [])

    # Build lookup maps
    golden_map = {}
    for g in golden_items:
        key = g.get("key", "")
        sf = os.path.basename(g.get("source_file", ""))
        golden_map[(key, sf)] = g

    ea_map = {}
    for e in ea_items:
        key = e.get("key", "")
        sf = os.path.basename(e.get("source_file", ""))
        ea_map[(key, sf)] = e

    golden_keys = set(golden_map.keys())
    ea_keys = set(ea_map.keys())

    # True positives: in both and values match
    tp = 0
    fp = 0
    fn = 0
    matches = []
    mismatches = []
    missing = []
    extra = []

    for k in golden_keys & ea_keys:
        g_val = golden_map[k].get("value")
        e_val = ea_map[k].get("value")
        if str(g_val) == str(e_val):
            tp += 1
            matches.append({"key": k[0], "source_file": k[1], "value": e_val})
        else:
            fp += 1
            mismatches.append({
                "key": k[0], "source_file": k[1],
                "golden_value": g_val, "extracted_value": e_val
            })

    # False positives: in EA but not in golden
    for k in ea_keys - golden_keys:
        fp += 1
        extra.append({"key": k[0], "source_file": k[1], "value": ea_map[k].get("value")})

    # False negatives: in golden but not in EA
    for k in golden_keys - ea_keys:
        fn += 1
        missing.append({"key": k[0], "source_file": k[1], "golden_value": golden_map[k].get("value")})

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    result = {
        "eval_metadata": {
            "ea_file": os.path.basename(ea_file),
            "golden_set": golden_path,
            "golden_items_count": len(golden_items),
            "ea_items_count": len(ea_items),
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4)
        },
        "matches": matches[:10],
        "mismatches": mismatches,
        "missing_from_ea": missing,
        "extra_in_ea": extra[:10]
    }

    # Save eval result
    ea_basename = os.path.splitext(os.path.basename(ea_file))[0]
    eval_path = os.path.join(DEFAULT_VALIDATION_DIR, f"{ea_basename}_golden_eval.json")
    os.makedirs(os.path.dirname(eval_path) or ".", exist_ok=True)
    with open(eval_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(json.dumps(result, ensure_ascii=False, indent=2))


def show_status(golden_path: str):
    """Show golden set statistics."""
    if not os.path.exists(golden_path):
        print(json.dumps({
            "status": "NOT_BUILT",
            "message": "Golden set not found. Run 'build' first.",
            "expected_path": golden_path
        }, indent=2))
        return

    with open(golden_path, "r", encoding="utf-8") as f:
        golden = json.load(f)

    meta = golden.get("golden_set_metadata", {})
    items = golden.get("items", [])

    # Category distribution
    categories = {}
    value_types = {}
    source_files = {}

    for item in items:
        cat = item.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1

        vt = item.get("value_type", "unknown")
        value_types[vt] = value_types.get(vt, 0) + 1

        sf = os.path.basename(item.get("source_file", "unknown"))
        source_files[sf] = source_files.get(sf, 0) + 1

    result = {
        "status": "BUILT",
        "golden_set_path": golden_path,
        "build_date": meta.get("build_date", "unknown"),
        "total_items": len(items),
        "source_eas": meta.get("source_eas", []),
        "category_distribution": categories,
        "value_type_distribution": value_types,
        "source_file_distribution": source_files
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    if len(sys.argv) < 2:
        print("Usage: python build_golden_set.py <build|eval|status> [args]", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]

    results_dir = DEFAULT_RESULTS_DIR
    golden_path = DEFAULT_GOLDEN_PATH

    # Parse optional flags
    if "--results-dir" in sys.argv:
        idx = sys.argv.index("--results-dir")
        if idx + 1 < len(sys.argv):
            results_dir = sys.argv[idx + 1]

    if "--golden" in sys.argv:
        idx = sys.argv.index("--golden")
        if idx + 1 < len(sys.argv):
            golden_path = sys.argv[idx + 1]

    if command == "build":
        build_golden_set(results_dir, golden_path)
    elif command == "eval":
        if len(sys.argv) < 3:
            print("Usage: python build_golden_set.py eval <ea_file>", file=sys.stderr)
            sys.exit(1)
        ea_file = sys.argv[2]
        eval_against_golden(ea_file, golden_path)
    elif command == "status":
        show_status(golden_path)
    else:
        print(f"Unknown command: {command}. Use build, eval, or status.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
