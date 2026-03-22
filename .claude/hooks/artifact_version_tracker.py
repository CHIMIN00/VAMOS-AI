#!/usr/bin/env python3
"""
artifact_version_tracker.py - llm-diff 기반 EA/CM 버전 간 시맨틱 diff + 이력 추적 (B-13)

Usage:
    python artifact_version_tracker.py diff <fileA> <fileB> [--output <path>]
    python artifact_version_tracker.py history <ea_file>
    python artifact_version_tracker.py regression <phase_number>
"""

import json
import sys
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Any

try:
    from llm_diff import diff as llm_diff_compare
    LLM_DIFF_AVAILABLE = True
except ImportError:
    LLM_DIFF_AVAILABLE = False

try:
    from deepdiff import DeepDiff
    DEEPDIFF_AVAILABLE = True
except ImportError:
    DEEPDIFF_AVAILABLE = False

HISTORY_FILE = "D:/VAMOS/04. 구현단계/v13_results/phase0/extraction/validation/artifact_history.json"


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def file_hash(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def compute_diff(obj_a: dict, obj_b: dict) -> dict:
    """Compute structural diff between two JSON objects."""
    if DEEPDIFF_AVAILABLE:
        dd = DeepDiff(obj_a, obj_b, ignore_order=False, verbose_level=2)
        return {
            "type_changes": list(dd.get("type_changes", {}).keys()),
            "values_changed": list(dd.get("values_changed", {}).keys()),
            "dictionary_item_added": list(dd.get("dictionary_item_added", set())),
            "dictionary_item_removed": list(dd.get("dictionary_item_removed", set())),
            "iterable_item_added": list(dd.get("iterable_item_added", {}).keys()),
            "iterable_item_removed": list(dd.get("iterable_item_removed", {}).keys()),
        }

    # Fallback: simple key comparison
    added = set(obj_b.keys()) - set(obj_a.keys())
    removed = set(obj_a.keys()) - set(obj_b.keys())
    modified = []
    for k in set(obj_a.keys()) & set(obj_b.keys()):
        if obj_a[k] != obj_b[k]:
            modified.append(k)
    return {
        "added": list(added),
        "removed": list(removed),
        "modified": modified,
    }


def load_history() -> list:
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_history(history: list):
    os.makedirs(os.path.dirname(HISTORY_FILE) or ".", exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def do_diff(file_a: str, file_b: str, output_path: str = None) -> dict:
    """Compare two EA/CM JSON files and record in history."""
    obj_a = load_json(file_a)
    obj_b = load_json(file_b)

    changes = compute_diff(obj_a, obj_b)
    total = sum(len(v) if isinstance(v, list) else 0 for v in changes.values())

    if total <= 0:
        verdict = "IDENTICAL"
    elif total <= 5:
        verdict = "MINOR_DIFF"
    else:
        verdict = "MAJOR_DIFF"

    result = {
        "artifact_diff_metadata": {
            "mode": "diff",
            "file_a": os.path.basename(file_a),
            "file_b": os.path.basename(file_b),
            "file_a_hash": file_hash(file_a),
            "file_b_hash": file_hash(file_b),
            "total_changes": total,
            "timestamp": datetime.now().isoformat(),
            "verdict": verdict
        },
        "changes": changes,
    }

    # Append to history
    history = load_history()
    history.append({
        "timestamp": datetime.now().isoformat(),
        "file_a": os.path.basename(file_a),
        "file_b": os.path.basename(file_b),
        "total_changes": total,
        "verdict": verdict,
    })
    save_history(history)

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Result saved to: {output_path}", file=sys.stderr)

    return result


def do_history(ea_file: str) -> dict:
    """Show version history for an EA file."""
    basename = os.path.basename(ea_file)
    history = load_history()
    relevant = [h for h in history if basename in h.get("file_a", "") or basename in h.get("file_b", "")]
    return {
        "artifact_diff_metadata": {
            "mode": "history",
            "target": basename,
            "entries": len(relevant),
        },
        "version_history": relevant
    }


def main():
    if len(sys.argv) < 3:
        print("Usage: python artifact_version_tracker.py <diff|history|regression> <args...>", file=sys.stderr)
        sys.exit(1)

    mode = sys.argv[1]
    output_path = None
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    if mode == "diff":
        if len(sys.argv) < 4:
            print("Usage: python artifact_version_tracker.py diff <fileA> <fileB>", file=sys.stderr)
            sys.exit(1)
        result = do_diff(sys.argv[2], sys.argv[3], output_path)
    elif mode == "history":
        result = do_history(sys.argv[2])
    elif mode == "regression":
        phase = sys.argv[2] if len(sys.argv) > 2 else "0"
        result = {"artifact_diff_metadata": {"mode": "regression", "phase": phase, "note": "Run diff for each EA between phases"}}
    else:
        print(f"Unknown mode: {mode}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
