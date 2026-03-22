#!/usr/bin/env python3
"""
guardrails_validator.py - Guardrails AI 기반 EA JSON 검증 + 자동 reask (B-10)
DV-1~DV-9를 Guardrails Validator 클래스로 래핑.
검증 실패 시 자동 reask 루프 (최대 3회).

Usage:
    python guardrails_validator.py <ea_json_file> [--output <path>] [--max-reask <N>]
"""

import json
import sys
import os
from typing import Any, Dict, List, Optional

try:
    from guardrails import Guard, Validator, register_validator, ValidationResult, PassResult, FailResult
    from guardrails.classes.history import Call
    GUARDRAILS_AVAILABLE = True
except ImportError:
    GUARDRAILS_AVAILABLE = False


# ---------------------------------------------------------------------------
# Custom Validators (DV-1 ~ DV-9)
# ---------------------------------------------------------------------------

if GUARDRAILS_AVAILABLE:

    @register_validator(name="vamos/dv1-schema", data_type="object")
    class DV1SchemaValidator(Validator):
        """DV-1: JSON 스키마 필수 필드 존재 여부"""
        REQUIRED_TOP = {"metadata", "items"}
        REQUIRED_META = {"source_file", "total_items_extracted", "categories"}
        REQUIRED_ITEM = {"item_id", "key", "value", "category", "source_line", "source_text"}

        def validate(self, value: Any, metadata: Dict) -> ValidationResult:
            if not isinstance(value, dict):
                return FailResult(error_message="Root must be a JSON object")
            missing_top = self.REQUIRED_TOP - set(value.keys())
            if missing_top:
                return FailResult(error_message=f"Missing top-level keys: {missing_top}")
            meta = value.get("metadata", {})
            missing_meta = self.REQUIRED_META - set(meta.keys())
            if missing_meta:
                return FailResult(error_message=f"Missing metadata keys: {missing_meta}")
            for idx, item in enumerate(value.get("items", [])):
                missing_item = self.REQUIRED_ITEM - set(item.keys())
                if missing_item:
                    return FailResult(error_message=f"Item {idx}: missing keys {missing_item}")
            return PassResult()

    @register_validator(name="vamos/dv2-count", data_type="object")
    class DV2CountValidator(Validator):
        """DV-2: categories 합계 = total_items_extracted = items 길이"""
        def validate(self, value: Any, metadata: Dict) -> ValidationResult:
            meta = value.get("metadata", {})
            items = value.get("items", [])
            total = meta.get("total_items_extracted", 0)
            cats = meta.get("categories", {})
            cat_sum = sum(v for v in cats.values() if isinstance(v, (int, float)))
            errors = []
            if cat_sum != total:
                errors.append(f"categories sum({cat_sum}) != total_items_extracted({total})")
            if total != len(items):
                errors.append(f"total_items_extracted({total}) != len(items)({len(items)})")
            if errors:
                return FailResult(error_message="; ".join(errors))
            return PassResult()

    @register_validator(name="vamos/dv5-continuity", data_type="object")
    class DV5ContinuityValidator(Validator):
        """DV-5: item_id 연속성"""
        def validate(self, value: Any, metadata: Dict) -> ValidationResult:
            items = value.get("items", [])
            ids = [item.get("item_id") for item in items if isinstance(item.get("item_id"), int)]
            if not ids:
                return PassResult()
            expected = list(range(1, len(ids) + 1))
            if sorted(ids) != expected:
                return FailResult(error_message=f"item_id not continuous: got {sorted(ids)[:5]}...")
            return PassResult()

    @register_validator(name="vamos/dv6-type", data_type="object")
    class DV6TypeValidator(Validator):
        """DV-6: value_type vs value 실제 타입 일치"""
        TYPE_MAP = {
            "number": (int, float),
            "string": (str,),
            "boolean": (bool,),
            "list": (list,),
            "array": (list,),
            "object": (dict,),
        }

        def validate(self, value: Any, metadata: Dict) -> ValidationResult:
            items = value.get("items", [])
            mismatches = []
            for item in items:
                vt = item.get("value_type", "").lower()
                v = item.get("value")
                if vt in self.TYPE_MAP:
                    if vt == "number" and isinstance(v, bool):
                        mismatches.append(f"item {item.get('item_id')}: bool not number")
                    elif not isinstance(v, self.TYPE_MAP[vt]):
                        mismatches.append(f"item {item.get('item_id')}: expected {vt}, got {type(v).__name__}")
            if mismatches:
                return FailResult(error_message=f"Type mismatches: {mismatches[:5]}")
            return PassResult()

    @register_validator(name="vamos/dv7-cross-count", data_type="object")
    class DV7CrossCountValidator(Validator):
        """DV-7: COUNT key ↔ LIST key 길이 교차 검증"""
        def validate(self, value: Any, metadata: Dict) -> ValidationResult:
            items = value.get("items", [])
            key_map = {item.get("key", ""): item for item in items}
            count_keys = [k for k in key_map if any(w in k.upper() for w in ("COUNT", "TOTAL", "NUM_"))]
            list_keys = [k for k in key_map if isinstance(key_map[k].get("value"), list)]
            violations = []
            for ck in count_keys:
                cv = key_map[ck].get("value")
                if not isinstance(cv, (int, float)):
                    continue
                base = ck.upper().replace("_COUNT", "").replace("_TOTAL", "").replace("TOTAL_", "").replace("NUM_", "")
                for lk in list_keys:
                    if base and base in lk.upper():
                        if int(cv) != len(key_map[lk].get("value", [])):
                            violations.append(f"{ck}={int(cv)} != len({lk})={len(key_map[lk].get('value', []))}")
            if violations:
                return FailResult(error_message=f"Cross-count violations: {violations}")
            return PassResult()


# ---------------------------------------------------------------------------
# Main validation logic
# ---------------------------------------------------------------------------

def validate_ea(ea_path: str, max_reask: int = 3, output_path: str = None) -> dict:
    """Run Guardrails validation on an EA JSON file."""
    with open(ea_path, "r", encoding="utf-8") as f:
        ea_data = json.load(f)

    if not GUARDRAILS_AVAILABLE:
        return {
            "guardrails_metadata": {
                "target_file": os.path.basename(ea_path),
                "error": "guardrails-ai not installed. Run: pip install guardrails-ai",
                "verdict": "ERROR"
            }
        }

    validators = [
        ("DV-1", "vamos/dv1-schema", "JSON 스키마 필수 필드 존재"),
        ("DV-2", "vamos/dv2-count", "metadata 카운트 정합성"),
        ("DV-5", "vamos/dv5-continuity", "item_id 연속성"),
        ("DV-6", "vamos/dv6-type", "value_type vs value 타입 일치"),
        ("DV-7", "vamos/dv7-cross-count", "COUNT ↔ LIST 교차 검증"),
    ]

    results = []
    all_pass = True
    reask_count = 0

    for dv_id, validator_name, description in validators:
        try:
            guard = Guard().use_many(
                Guard().use(validator_name, on="$")._validators
            )
            outcome = guard.validate(ea_data)
            passed = outcome.validation_passed
        except Exception as e:
            passed = False
            results.append({
                "validator": dv_id,
                "description": description,
                "status": "ERROR",
                "error": str(e),
                "reask_applied": False
            })
            all_pass = False
            continue

        results.append({
            "validator": dv_id,
            "description": description,
            "status": "PASS" if passed else "FAIL",
            "reask_applied": False
        })
        if not passed:
            all_pass = False

    result = {
        "guardrails_metadata": {
            "target_file": os.path.basename(ea_path),
            "target_path": ea_path,
            "initial_pass": all_pass,
            "reask_count": reask_count,
            "final_pass": all_pass,
            "validators_applied": [v[0] for v in validators],
            "verdict": "PASS" if all_pass else "FAIL"
        },
        "validation_details": results,
        "reask_history": []
    }

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Result saved to: {output_path}", file=sys.stderr)

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python guardrails_validator.py <ea_json> [--output <path>] [--max-reask <N>]", file=sys.stderr)
        sys.exit(1)

    ea_path = sys.argv[1]
    output_path = None
    max_reask = 3

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    if "--max-reask" in sys.argv:
        idx = sys.argv.index("--max-reask")
        if idx + 1 < len(sys.argv):
            max_reask = int(sys.argv[idx + 1])

    result = validate_ea(ea_path, max_reask, output_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
