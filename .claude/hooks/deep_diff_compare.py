#!/usr/bin/env python3
"""
deep_diff_compare.py - DeepDiff 기반 JSON 깊은 구조적 비교 (B-34)
타입 변경, 리스트 순서 변경 vs 내용 변경 구분, 부동소수점 근사 비교.

Usage:
    python deep_diff_compare.py <fileA> <fileB> [--ignore-order] [--significant-digits N] [--output <path>]
"""

import json
import sys
import os
from typing import Dict, Any

try:
    from deepdiff import DeepDiff
    DEEPDIFF_AVAILABLE = True
except ImportError:
    DEEPDIFF_AVAILABLE = False


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def deep_compare(file_a: str, file_b: str, ignore_order: bool = False,
                 significant_digits: int = None, output_path: str = None) -> dict:
    """Compare two JSON files using DeepDiff."""
    obj_a = load_json(file_a)
    obj_b = load_json(file_b)

    if not DEEPDIFF_AVAILABLE:
        return {
            "deep_diff_metadata": {
                "file_a": os.path.basename(file_a),
                "file_b": os.path.basename(file_b),
                "error": "deepdiff not installed. Run: pip install deepdiff",
                "verdict": "ERROR"
            }
        }

    dd_kwargs = {
        "ignore_order": ignore_order,
        "verbose_level": 2,
        "report_repetition": True,
    }
    if significant_digits is not None:
        dd_kwargs["significant_digits"] = significant_digits

    dd = DeepDiff(obj_a, obj_b, **dd_kwargs)

    # Convert DeepDiff result to serializable dict
    changes = {}
    change_categories = [
        "type_changes", "values_changed",
        "dictionary_item_added", "dictionary_item_removed",
        "iterable_item_added", "iterable_item_removed",
        "repetition_change", "set_item_added", "set_item_removed",
    ]

    total_changes = 0
    summary = {}

    for cat in change_categories:
        raw = dd.get(cat, {})
        if isinstance(raw, set):
            changes[cat] = list(raw)
            count = len(raw)
        elif isinstance(raw, dict):
            # Convert keys/values to serializable form
            serializable = {}
            for k, v in raw.items():
                try:
                    json.dumps(v)
                    serializable[str(k)] = v
                except (TypeError, ValueError):
                    serializable[str(k)] = str(v)
            changes[cat] = serializable
            count = len(raw)
        else:
            changes[cat] = []
            count = 0

        summary[cat] = count
        total_changes += count

    if total_changes == 0:
        verdict = "IDENTICAL"
    elif total_changes <= 5:
        verdict = "MINOR_DIFF"
    else:
        verdict = "MAJOR_DIFF"

    result = {
        "deep_diff_metadata": {
            "file_a": os.path.basename(file_a),
            "file_b": os.path.basename(file_b),
            "file_a_path": file_a,
            "file_b_path": file_b,
            "ignore_order": ignore_order,
            "significant_digits": significant_digits,
            "total_changes": total_changes,
            "verdict": verdict
        },
        "changes": changes,
        "summary": summary
    }

    output = json.dumps(result, ensure_ascii=False, indent=2, default=str)
    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Result saved to: {output_path}", file=sys.stderr)

    return result


def main():
    if len(sys.argv) < 3:
        print("Usage: python deep_diff_compare.py <fileA> <fileB> [--ignore-order] [--significant-digits N] [--output <path>]", file=sys.stderr)
        sys.exit(1)

    file_a = sys.argv[1]
    file_b = sys.argv[2]
    ignore_order = "--ignore-order" in sys.argv
    significant_digits = None
    output_path = None

    if "--significant-digits" in sys.argv:
        idx = sys.argv.index("--significant-digits")
        if idx + 1 < len(sys.argv):
            significant_digits = int(sys.argv[idx + 1])

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    result = deep_compare(file_a, file_b, ignore_order, significant_digits, output_path)
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
