#!/usr/bin/env python3
"""
Task 0-I-B: 내부 참조 매핑 (Internal Reference Mapping)
Scans VAMOS_구현가이드_PART2_구현단계.md for all internal cross-references
and maps them to their target lines.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

INPUT_FILE = Path(r"D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md")
OUTPUT_FILE = Path(r"D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_reference_map.json")


def read_file(path: Path) -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        return f.readlines()


def build_target_index(lines: list[str]) -> dict:
    """Build indices for resolving references to target lines."""
    index = {
        "sections": {},      # §N.N.N -> line number (from markdown headings)
        "steps": {},         # STEP-N -> line number (from heading definitions)
        "phases": {},        # Phase N -> line number
        "tables": {},        # 표 N -> line number
        "rules": {},         # R1~R11 -> line number (from definition table)
        "headings": {},      # All headings for fuzzy matching
    }

    # Section number pattern from markdown headings: ## 1.2, ### 1.3.1, # 1., etc.
    heading_re = re.compile(r'^(#{1,6})\s+((\d+(?:\.\d+)*)\s*.*)$')
    # V0-STEP-N heading pattern
    step_heading_re = re.compile(r'^#+\s+V0-STEP-(\d+)', re.IGNORECASE)
    # Phase heading pattern: ## V1-Phase N or similar
    phase_heading_re = re.compile(r'^#+\s+.*(?:Phase|PHASE)[\s\-]*([\-]?\d+(?:\.\d+)?)', re.IGNORECASE)
    # Rule definition in table: | **R1** |
    rule_def_re = re.compile(r'^\|\s*\*\*R(\d+)\*\*\s*\|')

    for i, line in enumerate(lines, start=1):
        # Section headings -> § references
        m = heading_re.match(line)
        if m:
            sec_num = m.group(3)  # e.g. "1.2", "1.3.1"
            # Keep first occurrence: the document's primary section definition
            # (avoids sub-numbered items inside V3 etc. overwriting main TOC sections)
            if sec_num not in index["sections"]:
                index["sections"][sec_num] = i
                index["headings"][sec_num] = i

        # STEP headings
        m = step_heading_re.match(line)
        if m:
            step_num = m.group(1)
            index["steps"][step_num] = i
            # Also store as "STEP-N"
            index["steps"][f"STEP-{step_num}"] = i

        # Phase headings
        m = phase_heading_re.match(line)
        if m:
            phase_val = m.group(1)
            index["phases"][phase_val] = i

        # Rule definitions
        m = rule_def_re.match(line)
        if m:
            rule_num = m.group(1)
            index["rules"][rule_num] = i

    return index


def resolve_target(ref_type: str, ref_value: str, target_index: dict) -> int | None:
    """Try to resolve a reference to a target line number."""
    if ref_type == "§":
        # Extract the numeric part: §3.2 -> "3.2"
        m = re.search(r'§(\d+(?:\.\d+)*)', ref_value)
        if m:
            key = m.group(1)
            return target_index["sections"].get(key)

    elif ref_type == "STEP":
        # Extract step number: STEP-1 -> "1", V0-STEP-3 -> "3"
        m = re.search(r'STEP[\s\-]*(\d+)', ref_value, re.IGNORECASE)
        if m:
            key = m.group(1)
            return target_index["steps"].get(key)

    elif ref_type == "Phase":
        # Extract phase number: Phase 2 -> "2", Phase -1 -> "-1", Phase 1.5 -> "1.5"
        m = re.search(r'Phase[\s\-]*([\-]?\d+(?:\.\d+)?)', ref_value, re.IGNORECASE)
        if m:
            key = m.group(1)
            return target_index["phases"].get(key)

    elif ref_type == "R":
        # Extract rule number: R1 -> "1"
        m = re.search(r'R(\d+)', ref_value)
        if m:
            key = m.group(1)
            return target_index["rules"].get(key)

    # L references, 표 references: typically line-number or external, hard to resolve
    return None


def scan_references(lines: list[str], target_index: dict) -> list[dict]:
    """Scan all lines for internal reference patterns."""
    references = []

    # Reference patterns - order matters for overlapping matches
    patterns = [
        # §N, §N.N, §N.N.N patterns
        ("§", re.compile(r'§(\d+(?:\.\d+)*)')),
        # V0-STEP-N, STEP-N, STEP N patterns
        ("STEP", re.compile(r'(?:V\d[_\-])?STEP[\s\-]*(\d+)', re.IGNORECASE)),
        # Phase N, Phase-N, V1-Phase N patterns (N can be -1, 0, 1, 1.5, 2, 3, 4, 5, 6)
        ("Phase", re.compile(r'(?:V\d[_\-])?Phase[\s\-]*([\-]?\d+(?:\.\d+)?)', re.IGNORECASE)),
        # R1~R11 rule references (standalone, not part of AR-L or other compound)
        ("R", re.compile(r'(?<![A-Za-z\-])R(\d{1,2})(?!\d)(?!\.)')),
        # L숫자 patterns (line number references like L768, L2124)
        ("L", re.compile(r'(?<![A-Za-z])L(\d{3,5})(?!\d)')),
        # PHASE_B references
        ("PHASE_B", re.compile(r'PHASE_B(\d+)')),
        # D2.0-NN or D2.1-DN document references
        ("D2.x", re.compile(r'D2\.\d[\-_][A-Z]?\d+')),
    ]

    for i, line in enumerate(lines, start=1):
        # Skip lines inside code blocks for certain patterns? No - scan everything.
        for ref_type, pattern in patterns:
            for match in pattern.finditer(line):
                full_match = match.group(0)

                # Filter out false positives for R references
                if ref_type == "R":
                    r_num = int(match.group(1))
                    if r_num < 1 or r_num > 11:
                        continue
                    # Check surrounding context to avoid AR-L, SDAR, etc.
                    start = match.start()
                    prefix = line[max(0, start-3):start]
                    if re.search(r'[A-Za-z\-]$', prefix):
                        continue

                # Get context snippet (surrounding ~40 chars on each side)
                start = max(0, match.start() - 40)
                end = min(len(line), match.end() + 40)
                context = line[start:end].strip()

                target_line = resolve_target(ref_type, full_match, target_index)

                references.append({
                    "source_line": i,
                    "reference_type": ref_type,
                    "reference_value": full_match,
                    "context": context,
                    "target_line": target_line,
                })

    return references


def main():
    lines = read_file(INPUT_FILE)
    print(f"Read {len(lines)} lines from {INPUT_FILE.name}")

    # Build target index
    target_index = build_target_index(lines)
    print(f"Indexed sections: {len(target_index['sections'])}, "
          f"steps: {len(target_index['steps'])}, "
          f"phases: {len(target_index['phases'])}, "
          f"rules: {len(target_index['rules'])}")

    # Scan all references
    references = scan_references(lines, target_index)
    print(f"Found {len(references)} total references")

    # Count by type
    by_type = defaultdict(int)
    for ref in references:
        by_type[ref["reference_type"]] += 1

    # Build output
    output = {
        "metadata": {
            "task": "0-I-B",
            "source": INPUT_FILE.name,
            "created": "2026-03-15",
            "total_references": len(references),
            "by_type": dict(sorted(by_type.items())),
            "resolvable": sum(1 for r in references if r["target_line"] is not None),
            "unresolvable": sum(1 for r in references if r["target_line"] is None),
        },
        "target_index": {
            "sections": target_index["sections"],
            "steps": {k: v for k, v in target_index["steps"].items() if k.startswith("STEP")},
            "phases": target_index["phases"],
            "rules": target_index["rules"],
        },
        "references": references,
    }

    # Write output
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nOutput written to {OUTPUT_FILE}")
    print(f"\nSummary by type:")
    for t, c in sorted(by_type.items()):
        print(f"  {t}: {c}")
    print(f"\n  Resolvable: {output['metadata']['resolvable']}")
    print(f"  Unresolvable: {output['metadata']['unresolvable']}")

    # Show some sample references
    print(f"\nSample references (first 10):")
    for ref in references[:10]:
        target = ref['target_line'] if ref['target_line'] else "?"
        print(f"  L{ref['source_line']}: {ref['reference_type']}={ref['reference_value']} -> target L{target}")


if __name__ == "__main__":
    main()
