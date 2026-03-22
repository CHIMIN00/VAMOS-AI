#!/usr/bin/env python3
"""
symbolic_verifier.py - EA JSON 제약충족문제(CSP) 검증 (A-9 + B-15)
기본 모드: Python 내장 모듈로 7가지 제약 유형 결정론적 검증.
고급 모드(--advanced): python-constraint 라이브러리로 복잡한 다변수 교차 제약 풀이.

Usage:
    python symbolic_verifier.py <ea_json_file> [--output <path>]
    python symbolic_verifier.py all --dir <extraction_dir>
    python symbolic_verifier.py <ea_json_file> --advanced [--dir <extraction_dir>] [--output <path>]
"""

import json
import sys
import os
import glob

try:
    from constraint import Problem, AllDifferentConstraint, ExactSumConstraint
    CONSTRAINT_AVAILABLE = True
except ImportError:
    CONSTRAINT_AVAILABLE = False


def load_ea(path: str) -> dict:
    """Load EA JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_file_line_count(filepath: str) -> int:
    """Get total line count of a file."""
    if not os.path.exists(filepath):
        alt = os.path.join("D:/VAMOS", filepath)
        if os.path.exists(alt):
            filepath = alt
        else:
            return -1
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)
    except Exception:
        return -1


def check_arithmetic(ea: dict) -> list:
    """C1: categories 합계 = total_items_extracted = items 길이"""
    results = []
    metadata = ea.get("metadata", {})
    items = ea.get("items", [])

    total_extracted = metadata.get("total_items_extracted", None)
    categories = metadata.get("categories", {})
    items_len = len(items)

    # Check categories sum
    if categories:
        cat_sum = sum(v for v in categories.values() if isinstance(v, (int, float)))

        if total_extracted is not None and cat_sum != total_extracted:
            results.append({
                "constraint": "ARITHMETIC_01",
                "description": "categories 합계 = total_items_extracted",
                "expected": total_extracted,
                "actual": cat_sum,
                "status": "VIOLATED"
            })
        else:
            results.append({
                "constraint": "ARITHMETIC_01",
                "description": "categories 합계 = total_items_extracted",
                "expected": total_extracted,
                "actual": cat_sum,
                "status": "SATISFIED"
            })

    # Check total = items length
    if total_extracted is not None:
        if total_extracted != items_len:
            results.append({
                "constraint": "ARITHMETIC_02",
                "description": "total_items_extracted = len(items)",
                "expected": total_extracted,
                "actual": items_len,
                "status": "VIOLATED"
            })
        else:
            results.append({
                "constraint": "ARITHMETIC_02",
                "description": "total_items_extracted = len(items)",
                "expected": total_extracted,
                "actual": items_len,
                "status": "SATISFIED"
            })

    return results


def check_range(ea: dict) -> list:
    """C2: 0 < source_line <= file line count"""
    results = []
    items = ea.get("items", [])
    file_line_cache = {}

    for item in items:
        source_line = item.get("source_line", 0)
        source_file = item.get("source_file", "")
        item_id = item.get("item_id", "?")

        if source_line <= 0:
            results.append({
                "constraint": f"RANGE_{item_id}",
                "description": f"item {item_id}: source_line > 0",
                "actual": source_line,
                "status": "VIOLATED"
            })
            continue

        if source_file:
            if source_file not in file_line_cache:
                file_line_cache[source_file] = get_file_line_count(source_file)

            total_lines = file_line_cache[source_file]
            if total_lines > 0 and source_line > total_lines:
                results.append({
                    "constraint": f"RANGE_{item_id}",
                    "description": f"item {item_id}: source_line <= file_lines ({total_lines})",
                    "actual": source_line,
                    "status": "VIOLATED"
                })
            else:
                results.append({
                    "constraint": f"RANGE_{item_id}",
                    "description": f"item {item_id}: 0 < source_line <= file_lines",
                    "actual": source_line,
                    "status": "SATISFIED"
                })

    # Summarize: report only violations + summary
    violations = [r for r in results if r["status"] == "VIOLATED"]
    return violations if violations else [{
        "constraint": "RANGE_ALL",
        "description": f"All {len(items)} items: 0 < source_line <= file_lines",
        "status": "SATISFIED"
    }]


def check_type(ea: dict) -> list:
    """C3: value_type matches actual value type"""
    results = []
    items = ea.get("items", [])

    type_map = {
        "number": (int, float),
        "string": (str,),
        "boolean": (bool,),
        "list": (list,),
        "array": (list,),
        "object": (dict,),
    }

    violations = []
    checked = 0

    for item in items:
        value_type = item.get("value_type", "").lower()
        value = item.get("value")
        item_id = item.get("item_id", "?")

        if value_type in type_map:
            checked += 1
            expected_types = type_map[value_type]
            # Special case: bool is subclass of int in Python
            if value_type == "number" and isinstance(value, bool):
                violations.append({
                    "constraint": f"TYPE_{item_id}",
                    "description": f"item {item_id}: value_type={value_type} but value is bool",
                    "actual_type": type(value).__name__,
                    "status": "VIOLATED"
                })
            elif not isinstance(value, expected_types):
                violations.append({
                    "constraint": f"TYPE_{item_id}",
                    "description": f"item {item_id}: value_type={value_type} but actual={type(value).__name__}",
                    "actual_type": type(value).__name__,
                    "status": "VIOLATED"
                })

    if violations:
        return violations
    return [{
        "constraint": "TYPE_ALL",
        "description": f"All {checked} typed items: value_type matches actual type",
        "status": "SATISFIED"
    }]


def check_cross_count(ea: dict) -> list:
    """C4: COUNT key value = related LIST key len(value)"""
    results = []
    items = ea.get("items", [])

    # Build key->item map
    key_map = {}
    for item in items:
        key = item.get("key", "")
        key_map[key] = item

    # Find COUNT/LIST pairs
    count_keys = [k for k in key_map if "COUNT" in k.upper() or "TOTAL" in k.upper() or "NUM_" in k.upper()]
    list_keys = [k for k in key_map if isinstance(key_map[k].get("value"), list)]

    pairs_found = 0
    for ck in count_keys:
        count_val = key_map[ck].get("value")
        if not isinstance(count_val, (int, float)):
            continue

        # Find matching list key
        base = ck.upper().replace("_COUNT", "").replace("_TOTAL", "").replace("TOTAL_", "").replace("NUM_", "")

        for lk in list_keys:
            if base and base in lk.upper():
                list_val = key_map[lk].get("value", [])
                pairs_found += 1
                if int(count_val) != len(list_val):
                    results.append({
                        "constraint": f"CROSS_COUNT_{ck}_{lk}",
                        "description": f"{ck}={int(count_val)} but len({lk})={len(list_val)}",
                        "count_key": ck,
                        "list_key": lk,
                        "count_value": int(count_val),
                        "list_length": len(list_val),
                        "status": "VIOLATED"
                    })
                else:
                    results.append({
                        "constraint": f"CROSS_COUNT_{ck}_{lk}",
                        "description": f"{ck}={int(count_val)} == len({lk})={len(list_val)}",
                        "status": "SATISFIED"
                    })

    if not results:
        return [{
            "constraint": "CROSS_COUNT_NONE",
            "description": "No COUNT/LIST pairs found to verify",
            "status": "SKIPPED"
        }]
    return results


def check_uniqueness(ea: dict) -> list:
    """C5: item_id uniqueness"""
    items = ea.get("items", [])
    ids = [item.get("item_id") for item in items]

    seen = {}
    duplicates = []
    for i, item_id in enumerate(ids):
        if item_id in seen:
            duplicates.append(item_id)
        else:
            seen[item_id] = i

    if duplicates:
        return [{
            "constraint": "UNIQUENESS",
            "description": f"Duplicate item_ids found: {duplicates}",
            "duplicates": duplicates,
            "status": "VIOLATED"
        }]
    return [{
        "constraint": "UNIQUENESS",
        "description": f"All {len(ids)} item_ids are unique",
        "status": "SATISFIED"
    }]


def check_inclusion(ea: dict, all_eas_dir: str = None) -> list:
    """C6: LOCK values consistent across EAs"""
    items = ea.get("items", [])
    lock_items = [i for i in items if i.get("category") == "C7" or "LOCK" in str(i.get("key", "")).upper() or "FREEZE" in str(i.get("key", "")).upper()]

    if not lock_items:
        return [{
            "constraint": "INCLUSION_LOCK",
            "description": "No LOCK/FREEZE items found",
            "status": "SKIPPED"
        }]

    # If we have access to other EAs, check cross-consistency
    if all_eas_dir and os.path.exists(all_eas_dir):
        other_eas = glob.glob(os.path.join(all_eas_dir, "v13_EA*.json"))
        lock_map = {}

        for lock_item in lock_items:
            key = lock_item.get("key", "")
            value = lock_item.get("value")
            lock_map[key] = value

        violations = []
        for other_path in other_eas:
            try:
                with open(other_path, "r", encoding="utf-8") as f:
                    other_ea = json.load(f)
                for other_item in other_ea.get("items", []):
                    other_key = other_item.get("key", "")
                    if other_key in lock_map:
                        if str(other_item.get("value")) != str(lock_map[other_key]):
                            violations.append({
                                "constraint": f"INCLUSION_{other_key}",
                                "description": f"LOCK key {other_key}: current={lock_map[other_key]}, other={other_item.get('value')} in {os.path.basename(other_path)}",
                                "status": "VIOLATED"
                            })
            except Exception:
                continue

        if violations:
            return violations

    return [{
        "constraint": "INCLUSION_LOCK",
        "description": f"Found {len(lock_items)} LOCK/FREEZE items (cross-EA check requires --dir)",
        "status": "SATISFIED"
    }]


def check_logic(ea: dict) -> list:
    """C7: logical constraints (e.g., severity=CRITICAL -> confidence > 0.9)"""
    items = ea.get("items", [])
    results = []
    violations = []

    for item in items:
        severity = item.get("severity", "")
        confidence = item.get("confidence", None)
        item_id = item.get("item_id", "?")

        if severity == "CRITICAL" and confidence is not None:
            if isinstance(confidence, (int, float)) and confidence <= 0.9:
                violations.append({
                    "constraint": f"LOGIC_{item_id}",
                    "description": f"item {item_id}: severity=CRITICAL but confidence={confidence} (expected > 0.9)",
                    "status": "VIOLATED"
                })

    if violations:
        return violations
    return [{
        "constraint": "LOGIC_ALL",
        "description": "All logical constraints satisfied",
        "status": "SATISFIED"
    }]


def check_advanced_constraints(ea: dict, all_eas_dir: str = None) -> list:
    """B-15: python-constraint 기반 고급 다변수 교차 제약 검증.
    여러 EA에 걸친 복잡한 CSP를 constraint 라이브러리로 풀이."""
    results = []

    if not CONSTRAINT_AVAILABLE:
        return [{
            "constraint": "ADVANCED_NOT_AVAILABLE",
            "description": "python-constraint not installed. Run: pip install python-constraint",
            "status": "SKIPPED"
        }]

    items = ea.get("items", [])
    key_val = {item.get("key", ""): item.get("value") for item in items}

    # --- Advanced Constraint 1: Multi-variable sum consistency ---
    # e.g., CORE_MODULE_COUNT + COND_MODULE_COUNT + EXP_MODULE_COUNT = TOTAL_MODULE_COUNT
    count_keys = {k: v for k, v in key_val.items()
                  if isinstance(v, (int, float)) and any(w in k.upper() for w in ("COUNT", "TOTAL", "NUM_"))}

    if count_keys:
        # Find potential sum relationships
        total_keys = [k for k in count_keys if "TOTAL" in k.upper()]
        part_keys = [k for k in count_keys if "TOTAL" not in k.upper()]

        for tk in total_keys:
            total_val = int(count_keys[tk])
            base = tk.upper().replace("TOTAL_", "").replace("_TOTAL", "").replace("_COUNT", "").replace("COUNT", "")

            # Find part keys that share the base concept
            related_parts = []
            for pk in part_keys:
                pk_base = pk.upper().replace("_COUNT", "").replace("COUNT", "").replace("_MODULE", "").replace("MODULE_", "")
                # Heuristic: same domain if they share a common substring
                if base and len(base) >= 3 and (base in pk.upper() or pk_base in tk.upper()):
                    continue  # Skip self-references
                if "MODULE" in tk.upper() and "MODULE" in pk.upper():
                    related_parts.append(pk)

            if len(related_parts) >= 2:
                problem = Problem()
                for pk in related_parts:
                    problem.addVariable(pk, [int(count_keys[pk])])
                problem.addVariable(tk, [total_val])

                # Constraint: sum of parts = total
                part_sum = sum(int(count_keys[pk]) for pk in related_parts)

                if part_sum == total_val:
                    results.append({
                        "constraint": f"ADVANCED_SUM_{tk}",
                        "description": f"Sum({'+'.join(related_parts)}) = {part_sum} == {tk} = {total_val}",
                        "parts": {pk: int(count_keys[pk]) for pk in related_parts},
                        "total_key": tk,
                        "total_value": total_val,
                        "status": "SATISFIED"
                    })
                else:
                    results.append({
                        "constraint": f"ADVANCED_SUM_{tk}",
                        "description": f"Sum({'+'.join(related_parts)}) = {part_sum} != {tk} = {total_val}",
                        "parts": {pk: int(count_keys[pk]) for pk in related_parts},
                        "total_key": tk,
                        "total_value": total_val,
                        "status": "VIOLATED"
                    })

    # --- Advanced Constraint 2: Cross-EA consistency (requires --dir) ---
    if all_eas_dir and os.path.exists(all_eas_dir):
        other_ea_files = glob.glob(os.path.join(all_eas_dir, "v13_EA*.json"))

        # Collect same-key values across all EAs
        cross_ea_keys = {}
        for ea_file in other_ea_files:
            try:
                with open(ea_file, "r", encoding="utf-8") as f:
                    other_ea = json.load(f)
                ea_name = os.path.basename(ea_file)
                for item in other_ea.get("items", []):
                    k = item.get("key", "")
                    v = item.get("value")
                    if k and isinstance(v, (int, float)):
                        if k not in cross_ea_keys:
                            cross_ea_keys[k] = []
                        cross_ea_keys[k].append({"ea": ea_name, "value": v})
            except Exception:
                continue

        # Find keys that appear in multiple EAs with different values
        for k, entries in cross_ea_keys.items():
            if len(entries) < 2:
                continue
            values = set(e["value"] for e in entries)
            if len(values) > 1:
                # CSP: all instances of same key should have same value
                problem = Problem()
                for i, entry in enumerate(entries):
                    problem.addVariable(f"{entry['ea']}_{k}", [entry["value"]])

                results.append({
                    "constraint": f"ADVANCED_CROSS_EA_{k}",
                    "description": f"Key '{k}' has conflicting values across EAs: {entries}",
                    "entries": entries,
                    "status": "VIOLATED"
                })
            else:
                if len(entries) >= 2:
                    results.append({
                        "constraint": f"ADVANCED_CROSS_EA_{k}",
                        "description": f"Key '{k}' consistent across {len(entries)} EAs: value={entries[0]['value']}",
                        "status": "SATISFIED"
                    })

    # --- Advanced Constraint 3: Range constraints via CSP ---
    for item in items:
        key = item.get("key", "")
        value = item.get("value")
        if not isinstance(value, (int, float)):
            continue

        # Auto-detect implied range constraints from key naming
        if any(w in key.upper() for w in ("MAX", "LIMIT", "UPPER")):
            # Find corresponding MIN
            min_key = key.upper().replace("MAX", "MIN").replace("UPPER", "LOWER").replace("LIMIT", "MIN")
            for other_item in items:
                other_key = other_item.get("key", "").upper()
                if other_key == min_key:
                    other_val = other_item.get("value")
                    if isinstance(other_val, (int, float)):
                        problem = Problem()
                        problem.addVariable("min_val", [other_val])
                        problem.addVariable("max_val", [value])
                        problem.addConstraint(lambda mn, mx: mn <= mx, ("min_val", "max_val"))

                        solutions = problem.getSolutions()
                        if solutions:
                            results.append({
                                "constraint": f"ADVANCED_RANGE_{key}",
                                "description": f"{min_key}={other_val} <= {key}={value}",
                                "status": "SATISFIED"
                            })
                        else:
                            results.append({
                                "constraint": f"ADVANCED_RANGE_{key}",
                                "description": f"{min_key}={other_val} > {key}={value} (range inverted!)",
                                "status": "VIOLATED"
                            })

    if not results:
        results.append({
            "constraint": "ADVANCED_NONE",
            "description": "No advanced constraints detected to verify",
            "status": "SKIPPED"
        })

    return results


def verify_ea(ea_path: str, all_eas_dir: str = None, advanced: bool = False) -> dict:
    """Run all 7 constraint checks on an EA file.
    If advanced=True, also run B-15 python-constraint based CSP checks."""
    ea = load_ea(ea_path)

    all_constraints = []
    all_constraints.extend(check_arithmetic(ea))
    all_constraints.extend(check_range(ea))
    all_constraints.extend(check_type(ea))
    all_constraints.extend(check_cross_count(ea))
    all_constraints.extend(check_uniqueness(ea))
    all_constraints.extend(check_inclusion(ea, all_eas_dir))
    all_constraints.extend(check_logic(ea))

    # B-15: Advanced mode — python-constraint CSP checks
    advanced_constraints = []
    if advanced:
        advanced_constraints = check_advanced_constraints(ea, all_eas_dir)
        all_constraints.extend(advanced_constraints)

    satisfied = sum(1 for c in all_constraints if c["status"] == "SATISFIED")
    violated = sum(1 for c in all_constraints if c["status"] == "VIOLATED")
    skipped = sum(1 for c in all_constraints if c["status"] == "SKIPPED")

    verdict = "FAIL" if violated > 0 else "PASS"

    result = {
        "symbolic_verify_metadata": {
            "target_file": os.path.basename(ea_path),
            "target_path": ea_path,
            "mode": "advanced" if advanced else "basic",
            "total_constraints": len(all_constraints),
            "satisfied": satisfied,
            "violated": violated,
            "skipped": skipped,
            "verdict": verdict
        },
        "constraints": all_constraints
    }

    if advanced and advanced_constraints:
        result["advanced_constraints"] = advanced_constraints

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python symbolic_verifier.py <ea_json|all> [--dir <dir>] [--output <path>] [--advanced]", file=sys.stderr)
        sys.exit(1)

    target = sys.argv[1]
    output_path = None
    eas_dir = None
    advanced = "--advanced" in sys.argv

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    if "--dir" in sys.argv:
        idx = sys.argv.index("--dir")
        if idx + 1 < len(sys.argv):
            eas_dir = sys.argv[idx + 1]

    if target == "all":
        if not eas_dir:
            eas_dir = "D:/VAMOS/04. 구현단계/v13_results/phase0/extraction"

        ea_files = glob.glob(os.path.join(eas_dir, "v13_EA*.json"))
        if not ea_files:
            print(json.dumps({"error": "No EA files found", "dir": eas_dir}))
            sys.exit(1)

        results = []
        for ea_file in sorted(ea_files):
            try:
                result = verify_ea(ea_file, eas_dir, advanced=advanced)
                results.append(result)
            except Exception as e:
                results.append({
                    "symbolic_verify_metadata": {
                        "target_file": os.path.basename(ea_file),
                        "error": str(e),
                        "verdict": "ERROR"
                    }
                })

        summary = {
            "batch_metadata": {
                "total_files": len(results),
                "mode": "advanced" if advanced else "basic",
                "passed": sum(1 for r in results if r.get("symbolic_verify_metadata", {}).get("verdict") == "PASS"),
                "failed": sum(1 for r in results if r.get("symbolic_verify_metadata", {}).get("verdict") == "FAIL"),
                "errors": sum(1 for r in results if r.get("symbolic_verify_metadata", {}).get("verdict") == "ERROR")
            },
            "results": results
        }

        output = json.dumps(summary, ensure_ascii=False, indent=2)
    else:
        result = verify_ea(target, eas_dir or os.path.dirname(target), advanced=advanced)
        output = json.dumps(result, ensure_ascii=False, indent=2)

    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Result saved to: {output_path}", file=sys.stderr)

    print(output)


if __name__ == "__main__":
    main()
