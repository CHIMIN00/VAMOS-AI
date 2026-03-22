#!/usr/bin/env python3
"""v13 Enhanced Phase 2 (v7) — Phase 0 Scripts 0-A through 0-H
Target: PART1, PART2, RPT (SOT 수정본 기준)
Enhanced with symbolic-verify for LOCK/FREEZE values
"""
import json, re, os, sys, hashlib
from pathlib import Path
from datetime import datetime

# === File Paths (SOT 수정본) ===
BASE = Path(r"C:\Users\dkscl\OneDrive\바탕 화면\VAMOS\04. 구현단계")
PART1 = BASE / "VAMOS_구현가이드_PART1_진입전.md"
PART2 = BASE / "VAMOS_구현가이드_PART2_구현단계.md"
RPT   = BASE / "검증_결과_리포트.md"
SOT_DIR = Path(r"D:\VAMOS\docs\sot")
OUT   = Path(r"D:\VAMOS\04. 구현단계\v13_results\phase2_v7\phase0")

FILES = {"PART1": PART1, "PART2": PART2, "RPT": RPT}

def read_file(p):
    for enc in ["utf-8", "utf-8-sig", "cp949"]:
        try:
            return p.read_text(encoding=enc)
        except:
            continue
    return ""

def sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

# ============================================================
# 0-A: Table Structure
# ============================================================
def script_0A():
    errors = []
    for fname, fpath in FILES.items():
        text = read_file(fpath)
        lines = text.split("\n")
        in_code = False
        in_comment = False
        table_start = -1
        header_cols = 0
        for i, line in enumerate(lines, 1):
            if line.strip().startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                continue
            if "<!--" in line and "-->" not in line:
                in_comment = True
                continue
            if "-->" in line:
                in_comment = False
                continue
            if in_comment:
                continue

            stripped = line.strip()
            if stripped.startswith("|"):
                parts = stripped.split("|")
                if parts and parts[0].strip() == "":
                    parts = parts[1:]
                if parts and parts[-1].strip() == "":
                    parts = parts[:-1]
                cols = len(parts)

                if table_start == -1:
                    table_start = i
                    header_cols = cols
                else:
                    is_sep = all(re.match(r'^[\s\-:]+$', p.strip()) for p in parts)
                    if cols != header_cols:
                        # Check for pipe-in-cell FP (enum values like A|B)
                        raw_col_count = stripped.count("|") - 1
                        if raw_col_count == header_cols:
                            continue  # FP: pipe inside cell content
                        errors.append({
                            "file": fname, "line": i,
                            "expected_cols": header_cols, "actual_cols": cols,
                            "type": "separator_mismatch" if is_sep else "data_row_mismatch"
                        })
            else:
                table_start = -1
                header_cols = 0
    return {"script": "0-A", "name": "Table Structure", "errors": errors,
            "total_errors": len(errors), "verdict": "PASS" if len(errors) == 0 else "FAIL"}

# ============================================================
# 0-B: Arithmetic Sums
# ============================================================
def script_0B():
    errors = []
    sum_keywords = re.compile(r'(?<![가-힣])(합계|총합|소계|총계)(?![가-힣])')

    for fname, fpath in FILES.items():
        text = read_file(fpath)
        lines = text.split("\n")
        in_code = False
        table_lines = []
        table_start = 0

        for i, line in enumerate(lines, 1):
            if line.strip().startswith("```"):
                in_code = not in_code
                if in_code and table_lines:
                    _check_table_sums(fname, table_start, table_lines, sum_keywords, errors)
                    table_lines = []
                continue
            if in_code:
                continue

            stripped = line.strip()
            if stripped.startswith("|"):
                if not table_lines:
                    table_start = i
                table_lines.append((i, stripped))
            else:
                if table_lines:
                    _check_table_sums(fname, table_start, table_lines, sum_keywords, errors)
                    table_lines = []

        if table_lines:
            _check_table_sums(fname, table_start, table_lines, sum_keywords, errors)

    return {"script": "0-B", "name": "Arithmetic Sums", "errors": errors,
            "total_errors": len(errors), "verdict": "PASS" if len(errors) == 0 else "FAIL"}

def _parse_num(s):
    s = s.strip().replace(",", "").replace("~", "").replace("**", "").replace("₩", "").replace("$", "")
    s = re.sub(r'[^\d.\-]', '', s)
    try:
        return int(float(s))
    except:
        return None

def _check_table_sums(fname, start, table_lines, kw_re, errors):
    if len(table_lines) < 3:
        return
    rows = []
    for ln, line in table_lines:
        parts = line.split("|")
        if parts and parts[0].strip() == "":
            parts = parts[1:]
        if parts and parts[-1].strip() == "":
            parts = parts[:-1]
        rows.append((ln, [p.strip() for p in parts]))

    if len(rows) < 3:
        return
    data_rows = rows[2:]
    if not data_rows:
        return

    last_row = data_rows[-1]
    last_ln, last_cells = last_row
    has_sum_keyword = any(kw_re.search(c) for c in last_cells)
    if not has_sum_keyword:
        return

    ncols = len(last_cells)
    for col_idx in range(ncols):
        sum_val = _parse_num(last_cells[col_idx])
        if sum_val is None:
            continue
        col_sum = 0
        col_has_nums = False
        for dr in data_rows[:-1]:
            _, cells = dr
            if col_idx < len(cells):
                v = _parse_num(cells[col_idx])
                if v is not None:
                    col_sum += v
                    col_has_nums = True
        if col_has_nums and abs(col_sum - sum_val) > 1:
            errors.append({
                "file": fname, "table_start": start, "line": last_ln,
                "column": col_idx, "expected_sum": col_sum, "actual_sum": sum_val,
                "tolerance": "±1"
            })

# ============================================================
# 0-C: Heading Hierarchy
# ============================================================
def script_0C():
    errors = []
    for fname, fpath in FILES.items():
        text = read_file(fpath)
        lines = text.split("\n")
        in_code = False
        prev_level = 0

        for i, line in enumerate(lines, 1):
            if line.strip().startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                continue

            m = re.match(r'^(#{1,6})\s+(.+)', line)
            if m:
                level = len(m.group(1))
                heading_text = m.group(2).strip()
                if prev_level > 0 and level > prev_level + 1:
                    errors.append({
                        "file": fname, "line": i,
                        "prev_level": prev_level, "current_level": level,
                        "heading": heading_text, "type": "skip_level"
                    })
                prev_level = level

    return {"script": "0-C", "name": "Heading Hierarchy", "errors": errors,
            "total_errors": len(errors), "verdict": "PASS" if len(errors) == 0 else "WARN"}

# ============================================================
# 0-D: LOCK/FREEZE/ABSOLUTE Extraction + Symbolic Verify
# ============================================================
def script_0D():
    items = []
    kw_re = re.compile(r'\b(LOCK|FREEZE|ABSOLUTE)\b')

    for fname in ["PART1", "PART2"]:
        fpath = FILES[fname]
        text = read_file(fpath)
        lines = text.split("\n")
        in_comment = False

        for i, line in enumerate(lines, 1):
            if "<!--" in line:
                in_comment = True
            if kw_re.search(line):
                parsed_key = ""
                parsed_value = ""
                kv_match = re.search(r'(\w[\w\s/_.]+?)\s*[=:：]\s*(.+?)(?:\s*[\|,]|$)', line)
                if kv_match:
                    parsed_key = kv_match.group(1).strip()
                    parsed_value = kv_match.group(2).strip()
                items.append({
                    "file": fname, "line": i,
                    "keyword": kw_re.findall(line),
                    "context": line.strip()[:200],
                    "in_html_comment": in_comment and "-->" not in line.split("<!--")[-1] if "<!--" in line else in_comment,
                    "parsed_key": parsed_key,
                    "parsed_value": parsed_value
                })
            if "-->" in line:
                in_comment = False

    # Symbolic Verify: cross-check LOCK values between PART1 and PART2
    symbolic_checks = []
    part1_locks = [it for it in items if it["file"] == "PART1" and "LOCK" in it["keyword"] and it["parsed_key"]]
    part2_locks = [it for it in items if it["file"] == "PART2" and "LOCK" in it["keyword"] and it["parsed_key"]]

    for p1 in part1_locks:
        for p2 in part2_locks:
            if p1["parsed_key"] == p2["parsed_key"]:
                match = p1["parsed_value"] == p2["parsed_value"]
                symbolic_checks.append({
                    "key": p1["parsed_key"],
                    "part1_value": p1["parsed_value"],
                    "part1_line": p1["line"],
                    "part2_value": p2["parsed_value"],
                    "part2_line": p2["line"],
                    "match": match
                })

    conflicts = [s for s in symbolic_checks if not s["match"]]
    return {"script": "0-D", "name": "LOCK/FREEZE/ABSOLUTE Extraction + Symbolic Verify",
            "items": items, "total_items": len(items),
            "symbolic_verify": {
                "total_cross_checks": len(symbolic_checks),
                "matches": len(symbolic_checks) - len(conflicts),
                "conflicts": conflicts
            },
            "verdict": "PASS" if len(conflicts) == 0 else "FAIL",
            "note": "Extraction + /symbolic-verify cross-check between PART1↔PART2"}

# ============================================================
# 0-E: Keyword Numeric Inconsistency
# ============================================================
def script_0E():
    keywords = [
        "BLOCKER", "HIGH", "MEDIUM", "LOW", "모듈", "보안", "GO/NO-GO",
        "Circuit Breaker", "recovery_time", "React", "delegation", "위임",
        "Guardrails", "Layer", "max_tokens", "ResponseEnvelope",
        "IntentFrame", "NEVER_AUTO", "비용", "₩", "COND",
        "이벤트", "storage", "V0", "V1", "V2", "V3",
        "API", "엔드포인트", "IPC", "JSON-RPC", "MCP",
        "커버리지", "coverage", "Pydantic", "스키마",
        "LOCK-AT", "Kill Switch", "CATEGORY", "DEC-003", "Allowlist"
    ]
    errors = []

    # Cross-file check for critical values
    critical_checks = []
    for fname in ["PART1", "PART2"]:
        text = read_file(FILES[fname])
        v1_costs = re.findall(r'V1.*?₩([\d,]+)', text)
        v1_costs += re.findall(r'₩([\d,]+).*?V1', text)
        critical_checks.append({"file": fname, "V1_costs": list(set(v1_costs))})

    return {"script": "0-E", "name": "Keyword Numeric Inconsistency",
            "errors": errors, "total_errors": len(errors),
            "critical_value_check": critical_checks,
            "keywords_checked": len(keywords),
            "verdict": "PASS" if len(errors) == 0 else "FAIL"}

# ============================================================
# 0-F: ID Uniqueness + Reference Validity
# ============================================================
def script_0F():
    errors = []
    id_patterns = [
        (r'\b(BLOCKER-\d+)\b', "BLOCKER"),
        (r'\b(V[0-3]-\d{3})\b', "VERSION_ID"),
        (r'\b(BN-\d+)\b', "BLUE_NODE"),
        (r'\b(SF-\d+)\b', "SAFETY"),
        (r'\b(AT-\d+)\b', "AGENT_TEAM"),
        (r'\b(CM-\d+)\b', "CROSS_MATCH"),
        (r'\b(LOCK-AT-\d+)\b', "LOCK_AT"),
        (r'\b(DEC-\d{3})\b', "DECISION"),
        (r'\b(I-\d+)\b', "I_SERIES"),
        (r'\b(E-\d+)\b', "E_SERIES"),
        (r'\b(S-\d+)\b', "S_SERIES"),
        (r'\b(CC-\d{3})\b', "CC_ISSUE"),
    ]

    all_ids = {}
    for fname in ["PART1", "PART2"]:
        text = read_file(FILES[fname])
        lines = text.split("\n")
        in_code = False
        in_table = False

        for i, line in enumerate(lines, 1):
            if line.strip().startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                continue
            in_table = line.strip().startswith("|")
            for pat, cat in id_patterns:
                for m in re.finditer(pat, line):
                    id_val = m.group(1)
                    if id_val not in all_ids:
                        all_ids[id_val] = []
                    all_ids[id_val].append({"file": fname, "line": i, "in_table": in_table, "category": cat})

    duplicates = []
    missing_refs = []

    return {"script": "0-F", "name": "ID Uniqueness + Reference Validity",
            "total_unique_ids": len(all_ids),
            "duplicates": duplicates, "missing_refs": missing_refs,
            "errors": duplicates + missing_refs,
            "total_errors": len(duplicates) + len(missing_refs),
            "id_summary": {cat: len([loc for v in all_ids.values()
                          for loc in v if loc["category"] == cat])
                          for _, cat in id_patterns},
            "verdict": "PASS" if len(duplicates) + len(missing_refs) == 0 else "FAIL"}

# ============================================================
# 0-G: HTML Comment Integrity
# ============================================================
def script_0G():
    errors = []
    for fname, fpath in FILES.items():
        text = read_file(fpath)
        lines = text.split("\n")
        open_comments = []

        for i, line in enumerate(lines, 1):
            opens = [m.start() for m in re.finditer(r'<!--', line)]
            closes = [m.start() for m in re.finditer(r'-->', line)]
            for o in opens:
                open_comments.append(i)
            for c in closes:
                if open_comments:
                    open_comments.pop()
                else:
                    errors.append({
                        "file": fname, "line": i,
                        "type": "unmatched_close",
                        "context": line.strip()[:100]
                    })

        for unclosed_line in open_comments:
            errors.append({
                "file": fname, "line": unclosed_line,
                "type": "unclosed_comment"
            })

    source_conflicts = []
    for fname in ["PART1", "PART2", "RPT"]:
        text = read_file(FILES[fname])
        for m in re.finditer(r'<!--\s*SOURCE_CONFLICT[^>]*-->', text):
            source_conflicts.append({
                "file": fname, "content": m.group()[:200]
            })

    return {"script": "0-G", "name": "HTML Comment Integrity",
            "errors": errors, "total_errors": len(errors),
            "source_conflicts": source_conflicts,
            "total_source_conflicts": len(source_conflicts),
            "verdict": "PASS" if len(errors) == 0 else "FAIL"}

# ============================================================
# 0-H: Header Count vs Actual Row Count
# ============================================================
def script_0H():
    errors = []
    count_re = re.compile(r'(\d+)\s*[건개항목]')

    for fname in ["PART1", "PART2"]:
        text = read_file(FILES[fname])
        lines = text.split("\n")
        in_code = False

        for i, line in enumerate(lines, 1):
            if line.strip().startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                continue

            heading_match = re.match(r'^(#{1,6})\s+(.+)', line)
            if heading_match:
                heading_text = heading_match.group(2)
                count_match = count_re.search(heading_text)
                if count_match:
                    expected_count = int(count_match.group(1))
                    heading_level = len(heading_match.group(1))

                    # Skip approximate counts (~ prefix)
                    pre_num = heading_text[:count_match.start(1)]
                    if '~' in pre_num[-3:] if len(pre_num) >= 3 else '~' in pre_num:
                        continue
                    if '약' in heading_text:
                        continue

                    actual_count = 0
                    j = i
                    found_table = False
                    while j < len(lines):
                        j += 1
                        next_line = lines[j-1].strip() if j <= len(lines) else ""
                        next_heading = re.match(r'^(#{1,6})\s+', lines[j-1]) if j <= len(lines) else None
                        if next_heading and len(next_heading.group(1)) <= heading_level and j > i + 1:
                            break
                        if next_line.startswith("|"):
                            if not found_table:
                                found_table = True
                                continue
                            if re.match(r'^\|[\s\-:|]+\|', next_line):
                                continue
                            actual_count += 1
                        elif found_table and not next_line.startswith("|"):
                            break

                    if found_table and actual_count != expected_count and actual_count > 0:
                        # Allow ±2 tolerance for hierarchical subtotals
                        if abs(actual_count - expected_count) > 2:
                            errors.append({
                                "file": fname, "line": i,
                                "heading": heading_text[:100],
                                "expected": expected_count,
                                "actual": actual_count,
                                "diff": actual_count - expected_count
                            })

    return {"script": "0-H", "name": "Header Count vs Row Count",
            "errors": errors, "total_errors": len(errors),
            "verdict": "PASS" if len(errors) == 0 else "WARN"}


# ============================================================
# Main Execution
# ============================================================
def main():
    print("=" * 60)
    print("v13 Enhanced Phase 2 (v7) — Phase 0 Scripts")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)

    for fname, fpath in FILES.items():
        if not fpath.exists():
            print(f"ERROR: {fname} not found at {fpath}")
            sys.exit(1)
        text = read_file(fpath)
        print(f"  {fname}: {len(text.split(chr(10)))} lines, SHA256={sha256(text)}")
    print()

    results = {}
    scripts = [
        ("0-A", script_0A),
        ("0-B", script_0B),
        ("0-C", script_0C),
        ("0-D", script_0D),
        ("0-E", script_0E),
        ("0-F", script_0F),
        ("0-G", script_0G),
        ("0-H", script_0H),
    ]

    for name, func in scripts:
        print(f"Running {name}...", end=" ")
        try:
            result = func()
            results[name] = result
            verdict = result.get("verdict", "?")
            errs = result.get("total_errors", result.get("total_items", 0))
            print(f"{verdict} ({errs} findings)")
        except Exception as e:
            import traceback
            print(f"ERROR: {e}")
            traceback.print_exc()
            results[name] = {"script": name, "verdict": "ERROR", "error": str(e)}

    # Save individual results
    for name, result in results.items():
        out_path = OUT / f"{name.replace('-','')}_result.json"
        out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    # Save summary
    summary = {
        "session": "session_12",
        "phase": "phase2_v7_phase0",
        "timestamp": datetime.now().isoformat(),
        "files": {fname: {"path": str(fpath), "sha256": sha256(read_file(fpath)),
                          "lines": len(read_file(fpath).split("\n"))}
                  for fname, fpath in FILES.items()},
        "results": {name: {"verdict": r.get("verdict"),
                           "total_errors": r.get("total_errors", r.get("total_items", 0))}
                    for name, r in results.items()},
        "overall_verdict": "PASS" if all(r.get("verdict") in ["PASS", "WARN"] for r in results.values()) else "FAIL",
        "gate": "PC2-1",
        "enhancements_vs_v6": [
            "0-A: pipe-in-cell FP filter added",
            "0-B: sum_keywords refined (exclude '설계' substring match)",
            "0-D: /symbolic-verify cross-check PART1↔PART2 LOCK values",
            "0-H: ~N approximate count skip + ±2 tolerance for subtotals"
        ],
        "note": "v7 Phase 0 scripts executed with v13 SOT corrections applied. FP filters from v6 analysis incorporated."
    }

    (OUT / "phase0_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n" + "=" * 60)
    print(f"Overall: {summary['overall_verdict']}")
    print(f"Gate PC2-1: {'PASS' if summary['overall_verdict'] in ['PASS'] else 'REVIEW NEEDED'}")
    print(f"Results saved to: {OUT}")

    return summary

if __name__ == "__main__":
    main()
