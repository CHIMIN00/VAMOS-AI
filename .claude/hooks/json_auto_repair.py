#!/usr/bin/env python3
"""
json_auto_repair.py - json-repair 기반 깨진 JSON 자동 복구 (B-33)
파싱 실패 시 자동 복구 → DV 재검증.

Usage:
    python json_auto_repair.py <json_file> [--output <path>] [--no-backup]
"""

import json
import sys
import os
import shutil
from typing import Dict, Any

try:
    from json_repair import repair_json
    JSON_REPAIR_AVAILABLE = True
except ImportError:
    JSON_REPAIR_AVAILABLE = False


def attempt_repair(filepath: str, no_backup: bool = False, output_path: str = None) -> dict:
    """Attempt to repair a broken JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        raw_text = f.read()

    # Step 1: Try normal parse
    try:
        parsed = json.loads(raw_text)
        result = {
            "repair_metadata": {
                "target_file": os.path.basename(filepath),
                "target_path": filepath,
                "original_valid": True,
                "repair_attempted": False,
                "repair_success": True,
                "changes_made": 0,
                "dv_revalidation": "N/A",
                "verdict": "ALREADY_VALID"
            },
            "repairs": []
        }
        output = json.dumps(result, ensure_ascii=False, indent=2)
        if output_path:
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(output)
        return result
    except json.JSONDecodeError as original_err:
        pass

    if not JSON_REPAIR_AVAILABLE:
        return {
            "repair_metadata": {
                "target_file": os.path.basename(filepath),
                "original_valid": False,
                "repair_attempted": False,
                "error": "json-repair not installed. Run: pip install json-repair",
                "verdict": "ERROR"
            }
        }

    # Step 2: Attempt repair
    repairs = []
    try:
        repaired_str = repair_json(raw_text, return_objects=False)
        repaired_obj = json.loads(repaired_str)

        # Identify what changed
        changes = 0
        if len(repaired_str) != len(raw_text):
            changes += 1
            repairs.append({
                "type": "length_change",
                "original_length": len(raw_text),
                "repaired_length": len(repaired_str),
                "description": f"길이 변경: {len(raw_text)} → {len(repaired_str)}"
            })

        # Check common repairs
        if raw_text.count("{") != raw_text.count("}"):
            repairs.append({"type": "bracket_fix", "description": "중괄호 불균형 수정"})
            changes += 1
        if raw_text.count("[") != raw_text.count("]"):
            repairs.append({"type": "bracket_fix", "description": "대괄호 불균형 수정"})
            changes += 1
        if ",\n}" in raw_text or ",\n]" in raw_text or ",}" in raw_text or ",]" in raw_text:
            repairs.append({"type": "trailing_comma", "description": "후행 쉼표 제거"})
            changes += 1

        # Step 3: Save repaired file
        if not no_backup:
            backup_path = filepath + ".bak"
            shutil.copy2(filepath, backup_path)
            repairs.append({"type": "backup", "description": f"백업 저장: {backup_path}"})

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(json.dumps(repaired_obj, ensure_ascii=False, indent=2))

        # Step 4: Run DV revalidation
        dv_result = "SKIPPED"
        dv_script = "D:/VAMOS/.claude/hooks/deterministic_validator.py"
        if os.path.exists(dv_script):
            import subprocess
            try:
                proc = subprocess.run(
                    [sys.executable, dv_script, filepath],
                    capture_output=True, text=True, timeout=60
                )
                if proc.returncode == 0:
                    dv_output = json.loads(proc.stdout)
                    dv_result = dv_output.get("dv_metadata", {}).get("result", "UNKNOWN")
                else:
                    dv_result = "ERROR"
            except Exception:
                dv_result = "ERROR"

        result = {
            "repair_metadata": {
                "target_file": os.path.basename(filepath),
                "target_path": filepath,
                "original_valid": False,
                "repair_attempted": True,
                "repair_success": True,
                "changes_made": max(changes, 1),
                "dv_revalidation": dv_result,
                "verdict": "REPAIRED"
            },
            "repairs": repairs
        }

    except Exception as e:
        result = {
            "repair_metadata": {
                "target_file": os.path.basename(filepath),
                "target_path": filepath,
                "original_valid": False,
                "repair_attempted": True,
                "repair_success": False,
                "changes_made": 0,
                "dv_revalidation": "N/A",
                "verdict": "UNREPAIRABLE"
            },
            "repairs": [],
            "error": str(e)
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
        print("Usage: python json_auto_repair.py <json_file> [--output <path>] [--no-backup]", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]
    output_path = None
    no_backup = "--no-backup" in sys.argv

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    result = attempt_repair(filepath, no_backup, output_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
