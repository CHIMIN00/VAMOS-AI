#!/usr/bin/env python3
"""
json_semantic_diff.py - JSON/텍스트 시맨틱 Diff (A-7)
Python 내장 모듈만 사용. JSON 파일의 구조적 차이 + 텍스트 파일의 라인 기반 차이를 분석.

Usage:
    python json_semantic_diff.py <file_a> <file_b> [--output <output_path>]
    python json_semantic_diff.py <file_a> <file_b> --text [--output <output_path>]
"""

import json
import sys
import os
import difflib
from collections import OrderedDict
from typing import Any


def normalize_value(v: Any) -> Any:
    """Sort keys in dicts and sort lists of primitives for comparison."""
    if isinstance(v, dict):
        return {k: normalize_value(val) for k, val in sorted(v.items())}
    elif isinstance(v, list):
        return [normalize_value(item) for item in v]
    return v


def deep_diff(a: Any, b: Any, path: str = "") -> list:
    """Recursively diff two JSON values, returning list of change dicts."""
    changes = []

    if type(a) != type(b):
        changes.append({
            "path": path or "$",
            "type": "type_changed",
            "old_type": type(a).__name__,
            "new_type": type(b).__name__,
            "old_value": a,
            "new_value": b
        })
        return changes

    if isinstance(a, dict):
        all_keys = set(list(a.keys()) + list(b.keys()))
        for key in sorted(all_keys):
            child_path = f"{path}.{key}" if path else key
            if key not in a:
                changes.append({
                    "path": child_path,
                    "type": "added",
                    "value": b[key]
                })
            elif key not in b:
                changes.append({
                    "path": child_path,
                    "type": "removed",
                    "value": a[key]
                })
            else:
                changes.extend(deep_diff(a[key], b[key], child_path))

    elif isinstance(a, list):
        # Check for reordering: if sorted normalized versions match but originals don't
        if len(a) == len(b):
            try:
                norm_a = sorted([json.dumps(normalize_value(x), sort_keys=True, ensure_ascii=False) for x in a])
                norm_b = sorted([json.dumps(normalize_value(x), sort_keys=True, ensure_ascii=False) for x in b])
                if norm_a == norm_b and a != b:
                    changes.append({
                        "path": path or "$",
                        "type": "reordered",
                        "length": len(a)
                    })
                    return changes
            except (TypeError, ValueError):
                pass

        max_len = max(len(a), len(b))
        for i in range(max_len):
            child_path = f"{path}[{i}]"
            if i >= len(a):
                changes.append({
                    "path": child_path,
                    "type": "added",
                    "value": b[i]
                })
            elif i >= len(b):
                changes.append({
                    "path": child_path,
                    "type": "removed",
                    "value": a[i]
                })
            else:
                changes.extend(deep_diff(a[i], b[i], child_path))

    else:
        if a != b:
            changes.append({
                "path": path or "$",
                "type": "modified",
                "old_value": a,
                "new_value": b
            })

    return changes


def categorize_changes(changes: list) -> dict:
    """Categorize changes by type."""
    added = [c for c in changes if c["type"] == "added"]
    removed = [c for c in changes if c["type"] == "removed"]
    modified = [c for c in changes if c["type"] in ("modified", "type_changed")]
    reordered = [c for c in changes if c["type"] == "reordered"]
    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "reordered": reordered
    }


def items_diff(items_a: list, items_b: list) -> dict:
    """Special comparison for EA items arrays by item_id."""
    map_a = {}
    map_b = {}
    for item in items_a:
        if isinstance(item, dict) and "item_id" in item:
            map_a[item["item_id"]] = item
    for item in items_b:
        if isinstance(item, dict) and "item_id" in item:
            map_b[item["item_id"]] = item

    ids_a = set(map_a.keys())
    ids_b = set(map_b.keys())

    added_ids = ids_b - ids_a
    removed_ids = ids_a - ids_b
    common_ids = ids_a & ids_b

    modified_items = []
    for item_id in sorted(common_ids):
        item_changes = deep_diff(map_a[item_id], map_b[item_id], f"items[id={item_id}]")
        if item_changes:
            modified_items.append({
                "item_id": item_id,
                "changes": item_changes
            })

    return {
        "added_item_ids": sorted(added_ids),
        "removed_item_ids": sorted(removed_ids),
        "modified_items": modified_items,
        "unchanged_count": len(common_ids) - len(modified_items)
    }


def text_diff(file_a: str, file_b: str) -> dict:
    """Line-based semantic diff for non-JSON text files (.md, .py, .yaml, etc.)."""
    with open(file_a, "r", encoding="utf-8") as f:
        lines_a = f.readlines()
    with open(file_b, "r", encoding="utf-8") as f:
        lines_b = f.readlines()

    differ = difflib.unified_diff(lines_a, lines_b, fromfile=file_a, tofile=file_b, lineterm="")

    added = []
    removed = []
    modified = []
    current_hunk_line_a = 0
    current_hunk_line_b = 0

    for line in differ:
        if line.startswith("@@"):
            # Parse hunk header: @@ -start,count +start,count @@
            try:
                parts = line.split()
                old_range = parts[1]  # -start,count
                new_range = parts[2]  # +start,count
                current_hunk_line_a = int(old_range.split(",")[0].lstrip("-"))
                current_hunk_line_b = int(new_range.split(",")[0].lstrip("+"))
            except (IndexError, ValueError):
                pass
        elif line.startswith("-") and not line.startswith("---"):
            removed.append({
                "line": current_hunk_line_a,
                "content": line[1:].rstrip("\n")
            })
            current_hunk_line_a += 1
        elif line.startswith("+") and not line.startswith("+++"):
            added.append({
                "line": current_hunk_line_b,
                "content": line[1:].rstrip("\n")
            })
            current_hunk_line_b += 1
        elif line.startswith(" "):
            current_hunk_line_a += 1
            current_hunk_line_b += 1

    # Detect moved blocks: lines removed from one place and added in another (identical content)
    removed_contents = {r["content"]: r for r in removed if r["content"].strip()}
    moved_blocks = []
    remaining_added = []
    for a in added:
        if a["content"] in removed_contents:
            moved_blocks.append({
                "content": a["content"],
                "from_line": removed_contents[a["content"]]["line"],
                "to_line": a["line"]
            })
            del removed_contents[a["content"]]
        else:
            remaining_added.append(a)

    remaining_removed = [r for r in removed if r["content"] in removed_contents or not r["content"].strip()]

    # Detect modified lines via SequenceMatcher on close pairs
    seq = difflib.SequenceMatcher(None, [l.rstrip("\n") for l in lines_a], [l.rstrip("\n") for l in lines_b])
    for tag, i1, i2, j1, j2 in seq.get_opcodes():
        if tag == "replace":
            for k in range(min(i2 - i1, j2 - j1)):
                modified.append({
                    "line_a": i1 + k + 1,
                    "line_b": j1 + k + 1,
                    "old_content": lines_a[i1 + k].rstrip("\n"),
                    "new_content": lines_b[j1 + k].rstrip("\n")
                })

    changes = []
    for a in added:
        changes.append({"type": "added", "line": a["line"], "content": a["content"]})
    for r in removed:
        changes.append({"type": "removed", "line": r["line"], "content": r["content"]})
    for m in modified:
        changes.append({
            "type": "modified",
            "line_a": m["line_a"], "line_b": m["line_b"],
            "old_content": m["old_content"], "new_content": m["new_content"]
        })
    for mv in moved_blocks:
        changes.append({
            "type": "moved",
            "from_line": mv["from_line"], "to_line": mv["to_line"],
            "content": mv["content"]
        })

    ext_a = os.path.splitext(file_a)[1]
    ext_b = os.path.splitext(file_b)[1]
    file_type = ext_a if ext_a else ext_b if ext_b else ".txt"

    return {
        "diff_metadata": {
            "mode": "text",
            "file_a": os.path.basename(file_a),
            "file_b": os.path.basename(file_b),
            "file_a_path": file_a,
            "file_b_path": file_b,
            "file_type": file_type,
            "lines_a": len(lines_a),
            "lines_b": len(lines_b),
            "total_changes": len(added) + len(removed) + len(modified) + len(moved_blocks),
            "added": len(added),
            "removed": len(removed),
            "modified": len(modified),
            "moved_blocks": len(moved_blocks),
            "reordered": 0
        },
        "changes": changes
    }


def is_json_file(filepath: str) -> bool:
    """Check if file is JSON by extension."""
    return os.path.splitext(filepath)[1].lower() == ".json"


def main():
    if len(sys.argv) < 3:
        print("Usage: python json_semantic_diff.py <file_a> <file_b> [--text] [--output <path>]", file=sys.stderr)
        sys.exit(1)

    file_a = sys.argv[1]
    file_b = sys.argv[2]
    output_path = None
    force_text = "--text" in sys.argv

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    # Mode detection: JSON or text
    use_json_mode = not force_text and is_json_file(file_a) and is_json_file(file_b)

    if use_json_mode:
        # JSON semantic diff (existing logic)
        try:
            with open(file_a, "r", encoding="utf-8") as f:
                data_a = json.load(f)
        except Exception as e:
            print(json.dumps({"error": f"Failed to load {file_a}: {str(e)}"}))
            sys.exit(1)

        try:
            with open(file_b, "r", encoding="utf-8") as f:
                data_b = json.load(f)
        except Exception as e:
            print(json.dumps({"error": f"Failed to load {file_b}: {str(e)}"}))
            sys.exit(1)

        # Structural diff
        all_changes = deep_diff(data_a, data_b)
        categorized = categorize_changes(all_changes)

        # Detect EA/CM vs generic JSON
        is_ea_cm = False
        if isinstance(data_a, dict) and isinstance(data_b, dict):
            a_name = os.path.basename(file_a)
            b_name = os.path.basename(file_b)
            if ("v13_EA" in a_name or "v13_CM" in a_name or
                "v13_EA" in b_name or "v13_CM" in b_name):
                is_ea_cm = True

        # Special items diff if both have "items" arrays
        ea_items_diff = None
        if isinstance(data_a, dict) and isinstance(data_b, dict):
            if "items" in data_a and "items" in data_b:
                if isinstance(data_a["items"], list) and isinstance(data_b["items"], list):
                    ea_items_diff = items_diff(data_a["items"], data_b["items"])

        mode = "json_ea_cm" if is_ea_cm else "json_generic"
        result = {
            "diff_metadata": {
                "mode": mode,
                "file_a": os.path.basename(file_a),
                "file_b": os.path.basename(file_b),
                "file_a_path": file_a,
                "file_b_path": file_b,
                "file_type": ".json",
                "total_changes": len(all_changes),
                "added": len(categorized["added"]),
                "removed": len(categorized["removed"]),
                "modified": len(categorized["modified"]),
                "reordered": len(categorized["reordered"]),
                "moved_blocks": 0
            },
            "changes": all_changes
        }

        if ea_items_diff:
            result["items_diff"] = ea_items_diff

    else:
        # Text diff mode (general files: .md, .py, .yaml, .txt, etc.)
        try:
            result = text_diff(file_a, file_b)
        except Exception as e:
            print(json.dumps({"error": f"Text diff failed: {str(e)}"}))
            sys.exit(1)

    output = json.dumps(result, ensure_ascii=False, indent=2)

    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Diff result saved to: {output_path}", file=sys.stderr)

    print(output)


if __name__ == "__main__":
    main()
