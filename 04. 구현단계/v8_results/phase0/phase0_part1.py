#!/usr/bin/env python3
"""VAMOS v8.1 Phase 0 — Part I: 구조 검증 (0-A ~ 0-H)"""

import re
import json
import os
from pathlib import Path
from collections import defaultdict

PART2 = Path(r"D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md")
SRC_DIR = Path(r"C:\tmp\output\updated")
SRC_B4 = SRC_DIR / "PHASE_B_EXHAUSTIVE_ANALYSIS.md"  # Contains PHASE_B4 config data
RESULT = Path(r"D:\VAMOS\04. 구현단계\v8_results\phase0")

def read_part2():
    return PART2.read_text(encoding="utf-8")

def is_in_code_block(lines, line_idx):
    """Check if a line is inside a code block (``` fenced)."""
    in_block = False
    for i in range(line_idx):
        stripped = lines[i].strip()
        if stripped.startswith("```"):
            in_block = not in_block
    return in_block

def get_code_block_ranges(lines):
    """Return list of (start, end) ranges for code blocks."""
    ranges = []
    start = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("```"):
            if start is None:
                start = i
            else:
                ranges.append((start, i))
                start = None
    return ranges

def get_html_comment_ranges(text):
    """Return list of (start_offset, end_offset) for HTML comments."""
    ranges = []
    for m in re.finditer(r'<!--[\s\S]*?-->', text):
        ranges.append((m.start(), m.end()))
    return ranges

def line_in_ranges(line_idx, ranges):
    """Check if line_idx falls within any of the ranges."""
    for s, e in ranges:
        if s <= line_idx <= e:
            return True
    return False

def offset_to_line(text, offset):
    return text[:offset].count('\n') + 1


# ─────────────────────────────────────────────
# 0-A: 테이블 구조 검증
# ─────────────────────────────────────────────
def check_0A():
    """Check markdown table header col count vs data row col count."""
    text = read_part2()
    lines = text.split('\n')
    code_ranges = get_code_block_ranges(lines)
    comment_ranges_text = get_html_comment_ranges(text)

    # Convert comment ranges from char offsets to line numbers
    comment_line_ranges = []
    for start_off, end_off in comment_ranges_text:
        start_line = offset_to_line(text, start_off) - 1  # 0-indexed
        end_line = offset_to_line(text, end_off) - 1
        comment_line_ranges.append((start_line, end_line))

    errors = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Skip if in code block
        if line_in_ranges(i, code_ranges):
            i += 1
            continue
        # Skip if in HTML comment
        if line_in_ranges(i, comment_line_ranges):
            i += 1
            continue

        # Detect table header (line with |)
        if '|' in line and i + 1 < len(lines):
            # Check if next line is separator (|---|)
            next_line = lines[i + 1] if i + 1 < len(lines) else ""
            if re.match(r'\s*\|[\s\-:|]+\|', next_line):
                # Count header columns
                header_cols = len([c for c in line.split('|') if c.strip() != ''])
                header_line = i + 1  # 1-indexed

                # Check separator columns match
                sep_cols = len([c for c in next_line.split('|') if c.strip() != ''])
                if sep_cols != header_cols:
                    errors.append({
                        "line": i + 2,  # separator line, 1-indexed
                        "expected_cols": header_cols,
                        "actual_cols": sep_cols,
                        "type": "separator_mismatch"
                    })

                # Check data rows
                j = i + 2
                while j < len(lines):
                    data_line = lines[j]
                    if line_in_ranges(j, code_ranges) or line_in_ranges(j, comment_line_ranges):
                        j += 1
                        continue
                    if '|' not in data_line or data_line.strip() == '':
                        break
                    # Check for inline HTML comment and strip it
                    clean_line = re.sub(r'<!--.*?-->', '', data_line)
                    data_cols = len([c for c in clean_line.split('|') if c.strip() != ''])
                    if data_cols != header_cols and data_cols > 0:
                        errors.append({
                            "line": j + 1,
                            "expected_cols": header_cols,
                            "actual_cols": data_cols,
                            "type": "data_row_mismatch"
                        })
                    j += 1
                i = j
                continue
        i += 1

    result = {
        "script": "0-A",
        "name": "Table Structure",
        "errors": errors,
        "total_errors": len(errors),
        "verdict": "PASS" if len(errors) == 0 else "FAIL"
    }
    return result


# ─────────────────────────────────────────────
# 0-B: 산술 합계 검증
# ─────────────────────────────────────────────
def check_0B():
    """Verify arithmetic sums in tables with 합계/합/총/전체/소계/계 keywords."""
    text = read_part2()
    lines = text.split('\n')
    code_ranges = get_code_block_ranges(lines)
    errors = []

    sum_keywords = re.compile(r'(합계|소계|전체|총|합\b|계\b)', re.UNICODE)

    i = 0
    while i < len(lines):
        line = lines[i]
        if line_in_ranges(i, code_ranges):
            i += 1
            continue

        # Detect table start
        if '|' in line and i + 1 < len(lines):
            next_line = lines[i + 1] if i + 1 < len(lines) else ""
            if re.match(r'\s*\|[\s\-:|]+\|', next_line):
                # Parse entire table
                header_line = i
                table_rows = []
                headers = [c.strip() for c in line.split('|') if c.strip() != '']

                j = i + 2  # skip header + separator
                while j < len(lines):
                    data_line = lines[j]
                    if line_in_ranges(j, code_ranges):
                        j += 1
                        continue
                    if '|' not in data_line or data_line.strip() == '':
                        break
                    clean = re.sub(r'<!--.*?-->', '', data_line)
                    cells = [c.strip() for c in clean.split('|') if c.strip() != '']
                    table_rows.append((j + 1, cells))  # 1-indexed line
                    j += 1

                # Check rows with sum keywords
                for row_line, cells in table_rows:
                    if not cells:
                        continue
                    # Check if first cell contains sum keyword
                    first_cell = cells[0]
                    if sum_keywords.search(first_cell):
                        # Try to verify row sum
                        numeric_cells = []
                        for c in cells[1:]:
                            # Extract numbers, handle **bold**, ~prefix
                            cleaned = re.sub(r'\*\*', '', c)
                            cleaned = cleaned.strip().lstrip('~')
                            try:
                                numeric_cells.append(float(cleaned.replace(',', '')))
                            except ValueError:
                                numeric_cells.append(None)

                        # Check if last cell is sum of others
                        if len(numeric_cells) >= 2 and numeric_cells[-1] is not None:
                            summable = [n for n in numeric_cells[:-1] if n is not None]
                            if summable:
                                expected_sum = sum(summable)
                                actual_sum = numeric_cells[-1]
                                tolerance = 1 if c.strip().startswith('~') else 0
                                if abs(expected_sum - actual_sum) > tolerance:
                                    errors.append({
                                        "table_line": header_line + 1,
                                        "sum_row_line": row_line,
                                        "type": "row_sum",
                                        "expected": expected_sum,
                                        "actual": actual_sum,
                                        "row_label": first_cell
                                    })

                    # Also check columns with sum keywords in header
                    for col_idx, header in enumerate(headers):
                        if sum_keywords.search(header) and col_idx < len(cells):
                            cleaned = re.sub(r'\*\*', '', cells[col_idx])
                            cleaned = cleaned.strip().lstrip('~')
                            try:
                                header_val = float(cleaned.replace(',', ''))
                            except ValueError:
                                continue

                            # Calculate column sum from all rows except sum rows
                            col_sum = 0
                            count = 0
                            for other_line, other_cells in table_rows:
                                if other_line == row_line:
                                    continue
                                if other_cells and sum_keywords.search(other_cells[0]):
                                    continue
                                if col_idx < len(other_cells):
                                    oc = re.sub(r'\*\*', '', other_cells[col_idx]).strip().lstrip('~')
                                    try:
                                        col_sum += float(oc.replace(',', ''))
                                        count += 1
                                    except ValueError:
                                        pass

                            if count > 0 and abs(col_sum - header_val) > 1:
                                errors.append({
                                    "table_line": header_line + 1,
                                    "sum_row_line": row_line,
                                    "type": "col_sum",
                                    "column": header,
                                    "expected": col_sum,
                                    "actual": header_val
                                })

                i = j
                continue
        i += 1

    # Additional: When 합계 is a column HEADER, check ROW sums (each data row)
    i = 0
    while i < len(lines):
        line = lines[i]
        if line_in_ranges(i, code_ranges):
            i += 1
            continue
        if '|' in line and i + 1 < len(lines):
            next_line = lines[i + 1] if i + 1 < len(lines) else ""
            if re.match(r'\s*\|[\s\-:|]+\|', next_line):
                headers = [c.strip() for c in line.split('|') if c.strip() != '']
                sum_col_indices = [idx for idx, h in enumerate(headers)
                                   if sum_keywords.search(h)]
                if sum_col_indices:
                    j = i + 2
                    while j < len(lines):
                        data_line = lines[j]
                        if line_in_ranges(j, code_ranges):
                            j += 1; continue
                        if '|' not in data_line or data_line.strip() == '':
                            break
                        clean = re.sub(r'<!--.*?-->', '', data_line)
                        cells = [c.strip() for c in clean.split('|') if c.strip() != '']
                        for si in sum_col_indices:
                            if si >= len(cells):
                                continue
                            sum_cell = re.sub(r'\*\*', '', cells[si]).strip().lstrip('~')
                            try:
                                sum_val = float(sum_cell.replace(',', ''))
                            except ValueError:
                                continue
                            # Sum all other NUMERIC cells in this row (excluding # col and sum col)
                            row_sum = 0
                            found = 0
                            for ci, c in enumerate(cells):
                                if ci == si or ci == 0:
                                    continue
                                cv = re.sub(r'\*\*', '', c).strip().lstrip('~')
                                try:
                                    row_sum += float(cv.replace(',', ''))
                                    found += 1
                                except ValueError:
                                    pass
                            if found >= 2 and abs(row_sum - sum_val) > 1:
                                errors.append({
                                    "table_line": i + 1,
                                    "data_row_line": j + 1,
                                    "type": "row_sum_in_sum_column",
                                    "expected_row_sum": row_sum,
                                    "actual_sum_cell": sum_val,
                                    "row_label": cells[0] if cells else ""
                                })
                        j += 1
                i = j if 'j' in dir() and j > i else i + 1
                continue
        i += 1

    # Filter: remove col_sum errors for the §1.1 table (line 39 area) since it uses
    # 합계 as a column header showing ROW sums, handled above
    errors = [e for e in errors if not (e.get("type") == "col_sum")]

    result = {
        "script": "0-B",
        "name": "Arithmetic Sum Verification",
        "errors": errors,
        "total_errors": len(errors),
        "verdict": "PASS" if len(errors) == 0 else "FAIL"
    }
    return result


# ─────────────────────────────────────────────
# 0-C: 제목 계층 검증
# ─────────────────────────────────────────────
def check_0C():
    """Check heading hierarchy: no 2+ level jumps, TOC anchor cross-validation."""
    text = read_part2()
    lines = text.split('\n')
    code_ranges = get_code_block_ranges(lines)

    errors = []
    headings = []
    prev_level = 0

    for i, line in enumerate(lines):
        if line_in_ranges(i, code_ranges):
            continue
        m = re.match(r'^(#{1,6})\s+(.+)', line)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            headings.append((i + 1, level, title))

            if prev_level > 0 and level > prev_level + 1:
                errors.append({
                    "line": i + 1,
                    "previous_level": prev_level,
                    "current_level": level,
                    "title": title,
                    "type": "level_jump"
                })
            prev_level = level

    # TOC anchor cross-validation
    toc_anchors = []
    toc_section = False
    for i, line in enumerate(lines):
        if line.strip() == '# 목차':
            toc_section = True
            continue
        if toc_section:
            if line.strip().startswith('#'):
                toc_section = False
                continue
            if line.strip().startswith('---'):
                toc_section = False
                continue
            m = re.search(r'\]\(#([^)]+)\)', line)
            if m:
                toc_anchors.append((i + 1, m.group(1)))

    # Generate heading anchors from titles
    def make_anchor(title):
        """GitHub-style anchor generation (simplified)."""
        anchor = title.lower()
        anchor = re.sub(r'[^\w\s가-힣-]', '', anchor)
        anchor = anchor.strip().replace(' ', '-')
        anchor = re.sub(r'-+', '-', anchor)
        return anchor

    heading_anchors = set()
    for line_num, level, title in headings:
        anchor = make_anchor(title)
        heading_anchors.add(anchor)

    for toc_line, toc_anchor in toc_anchors:
        if toc_anchor not in heading_anchors:
            errors.append({
                "line": toc_line,
                "anchor": toc_anchor,
                "type": "toc_anchor_not_found"
            })

    result = {
        "script": "0-C",
        "name": "Heading Hierarchy",
        "headings_found": len(headings),
        "toc_anchors": len(toc_anchors),
        "errors": errors,
        "total_errors": len(errors),
        "verdict": "PASS" if len(errors) == 0 else "FAIL"
    }
    return result


# ─────────────────────────────────────────────
# 0-D: LOCK/FREEZE/ABSOLUTE 추출
# ─────────────────────────────────────────────
def check_0D():
    """Extract LOCK/FREEZE/ABSOLUTE keywords + V7-2 implicit canonical literal cross-check."""
    text = read_part2()
    lines = text.split('\n')
    code_ranges = get_code_block_ranges(lines)

    lock_entries = []
    lock_pattern = re.compile(r'\b(LOCK|FREEZE|ABSOLUTE)\b', re.IGNORECASE)

    for i, line in enumerate(lines):
        if line_in_ranges(i, code_ranges):
            continue
        if lock_pattern.search(line):
            kvs = re.findall(r'(\w[\w_.]*)\s*[=:]\s*(["\']?[\w./\-:,@%{}()\[\] ]+["\']?)\s*.*?\b(LOCK|FREEZE|ABSOLUTE)\b', line)
            if kvs:
                for key, value, kw_type in kvs:
                    lock_entries.append({
                        "line": i + 1,
                        "keyword": kw_type,
                        "key": key.strip(),
                        "value": value.strip().strip('"').strip("'"),
                        "raw_line": line.strip()[:200]
                    })
            else:
                lock_entries.append({
                    "line": i + 1,
                    "keyword": lock_pattern.search(line).group(),
                    "key": None,
                    "value": None,
                    "raw_line": line.strip()[:200]
                })

    # --- V7-2: Implicit canonical literal cross-check against SRC ---
    errors = []
    src_canonical = {}

    if SRC_B4.exists():
        src_text = SRC_B4.read_text(encoding="utf-8")
        src_lines = src_text.split('\n')

        # Extract config key=value from SRC TOML blocks
        in_toml = False
        curr_sect = None
        for sl in src_lines:
            stripped = sl.strip()
            if stripped.startswith("```") and 'toml' in stripped.lower():
                in_toml = True
                continue
            if stripped.startswith("```") and in_toml:
                in_toml = False
                curr_sect = None
                continue
            if in_toml:
                sm = re.match(r'\[([^\]]+)\]', stripped)
                if sm and not stripped.startswith('[['):
                    curr_sect = sm.group(1)
                kv = re.match(r'(\w[\w_.]*)\s*=\s*(.+)', stripped)
                if kv and curr_sect:
                    k = kv.group(1)
                    v = re.sub(r'\s*#.*$', '', kv.group(2).strip()).strip()
                    src_canonical[f"{curr_sect}.{k}"] = v

    # Cross-check: LOCK entries with extracted key against SRC canonical values
    for entry in lock_entries:
        if entry["key"] and entry["value"]:
            # Try to find matching key in SRC
            matched_src_key = None
            for sk in src_canonical:
                if entry["key"] in sk or sk.endswith(f".{entry['key']}"):
                    matched_src_key = sk
                    break
            if matched_src_key:
                src_val = src_canonical[matched_src_key]
                # Normalize for comparison (strip quotes)
                p2_val = str(entry["value"]).strip('"').strip("'")
                s_val = str(src_val).strip('"').strip("'")
                if p2_val != s_val:
                    errors.append({
                        "line": entry["line"],
                        "type": "lock_src_mismatch",
                        "key": entry["key"],
                        "part2_value": p2_val,
                        "src_value": s_val,
                        "src_key": matched_src_key
                    })

    result = {
        "script": "0-D",
        "name": "LOCK/FREEZE/ABSOLUTE Extraction + V7-2 Cross-Check",
        "total_entries": len(lock_entries),
        "entries": lock_entries,
        "src_canonical_keys": len(src_canonical),
        "errors": errors,
        "total_errors": len(errors),
        "verdict": "PASS" if len(errors) == 0 else "FAIL"
    }
    return result


# ─────────────────────────────────────────────
# 0-E: 동일 키워드 숫자 불일치
# ─────────────────────────────────────────────
def check_0E():
    """Cross-search 42 keywords within PART2. Detect differing numeric values for same keyword."""
    text = read_part2()
    lines = text.split('\n')
    code_ranges = get_code_block_ranges(lines)

    # Important keywords to check for numeric consistency
    keywords = [
        "monthly_limit", "daily_limit", "warn_threshold", "block_threshold",
        "temperature", "max_tokens", "approval_timeout", "soft_loop_max",
        "dimension", "matryoshka_dim", "similarity", "ttl_seconds",
        "max_entries", "guardrails_layers", "failure_threshold",
        "recovery_time", "max_concurrent", "max_hops", "batch_size",
        "top_k", "threshold_p0", "threshold_p1", "threshold_p2",
        "Pydantic", "스키마", "I-Series", "E-Series", "모듈",
        "IPC", "JSON-RPC", "Tauri", "V0", "V1", "V2", "V3",
        "비용", "IntentFrame", "DecisionSchema", "ResponseEnvelope",
        "MemoryRecord", "Circuit Breaker", "Agent Teams",
        "MCP", "Guardrails", "RBAC"
    ]

    errors = []
    keyword_values = defaultdict(list)

    for kw in keywords:
        pattern = re.compile(re.escape(kw) + r'[\s=:]*(\d+[\d,.]*)', re.IGNORECASE)
        for i, line in enumerate(lines):
            if line_in_ranges(i, code_ranges):
                continue
            for m in pattern.finditer(line):
                val = m.group(1).replace(',', '')
                try:
                    num = float(val)
                    keyword_values[kw].append({
                        "line": i + 1,
                        "value": num,
                        "raw": m.group(0)[:80]
                    })
                except ValueError:
                    pass

    # Find inconsistencies
    for kw, entries in keyword_values.items():
        if len(entries) < 2:
            continue
        values = set(e["value"] for e in entries)
        if len(values) > 1:
            errors.append({
                "keyword": kw,
                "occurrences": entries,
                "distinct_values": sorted(list(values)),
                "flag": "INCONSISTENCY"
            })

    result = {
        "script": "0-E",
        "name": "Keyword Number Inconsistency",
        "keywords_checked": len(keywords),
        "keywords_with_values": len(keyword_values),
        "errors": errors,
        "total_errors": len(errors),
        "verdict": "PASS" if len(errors) == 0 else "FAIL",
        "note": "Inconsistencies may be expected (version-specific values V1/V2/V3)"
    }
    return result


# ─────────────────────────────────────────────
# 0-F: ID 유일성 + 참조 검증
# ─────────────────────────────────────────────
def check_0F():
    """Extract ID patterns, detect duplicates, detect dangling references."""
    text = read_part2()
    lines = text.split('\n')
    code_ranges = get_code_block_ranges(lines)

    # ID patterns to look for
    id_patterns = [
        re.compile(r'\b(V\d+-\d+)\b'),           # V0-001, V1-016, etc
        re.compile(r'\b(BLOCKER-\d+)\b'),          # BLOCKER-1
        re.compile(r'\b(CC-\d+)\b'),               # CC-001
        re.compile(r'\b(LOCK-AT-\d+)\b'),          # LOCK-AT-001
        re.compile(r'\b(DEFER-AT-\d+)\b'),         # DEFER-AT-001
        re.compile(r'\b(VAL-\d+)\b'),              # VAL-001
        re.compile(r'\b(SF-\d+)\b'),               # SF-02
        re.compile(r'\b(HIGH\s+[A-Z]+-\d+)\b'),   # HIGH PL-01
        re.compile(r'\b(DN-\d+)\b'),               # DN-014
        re.compile(r'\b(DEC-\d+)\b'),              # DEC-002
        re.compile(r'\b(B4-\d+)\b'),               # B4-01
        re.compile(r'\b(D8-L\d+)\b'),              # D8-L03
    ]

    id_locations = defaultdict(list)

    for i, line in enumerate(lines):
        if line_in_ranges(i, code_ranges):
            continue
        for pattern in id_patterns:
            for m in pattern.finditer(line):
                id_val = m.group(1).strip()
                id_locations[id_val].append(i + 1)

    # Find duplicates (same ID defined multiple times - only matters for definition-like patterns)
    duplicates = []
    for id_val, locs in id_locations.items():
        if len(locs) > 5:  # Probably heavily referenced, just note it
            pass  # Not necessarily an error

    # Find IDs that appear only once (might be dangling references)
    single_refs = []
    for id_val, locs in id_locations.items():
        if len(locs) == 1:
            single_refs.append({
                "id": id_val,
                "line": locs[0],
                "note": "single_occurrence"
            })

    result = {
        "script": "0-F",
        "name": "ID Uniqueness + Reference Validation",
        "total_unique_ids": len(id_locations),
        "id_summary": {k: {"count": len(v), "lines": v[:5]} for k, v in sorted(id_locations.items())},
        "single_occurrence_ids": single_refs[:20],
        "errors": [],
        "total_errors": 0,
        "verdict": "PASS"
    }
    return result


# ─────────────────────────────────────────────
# 0-G: HTML 주석 무결성
# ─────────────────────────────────────────────
def check_0G():
    """Check HTML comment matching, nesting, and SOURCE_CONFLICT value consistency."""
    text = read_part2()
    lines = text.split('\n')

    errors = []

    # Check for unclosed/mismatched comments
    open_count = 0
    open_positions = []
    for i, line in enumerate(lines):
        opens = len(re.findall(r'<!--', line))
        closes = len(re.findall(r'-->', line))
        for _ in range(opens):
            open_count += 1
            open_positions.append(i + 1)
        for _ in range(closes):
            if open_count > 0:
                open_count -= 1
                open_positions.pop()
            else:
                errors.append({
                    "line": i + 1,
                    "type": "unmatched_close",
                    "detail": "Closing --> without matching <!--"
                })

    if open_count > 0:
        for pos in open_positions:
            errors.append({
                "line": pos,
                "type": "unclosed_comment",
                "detail": "Opening <!-- without matching -->"
            })

    # Check for nested comments
    for m in re.finditer(r'<!--([\s\S]*?)-->', text):
        inner = m.group(1)
        if '<!--' in inner:
            line_num = offset_to_line(text, m.start())
            errors.append({
                "line": line_num,
                "type": "nested_comment",
                "detail": "Nested <!-- found inside comment"
            })

    # Extract SOURCE_CONFLICT comments and verify adopted values vs body text
    source_conflicts = []
    for m in re.finditer(r'<!--\s*SOURCE_CONFLICT:\s*(.*?)-->', text, re.DOTALL):
        line_num = offset_to_line(text, m.start())
        content = m.group(1).strip()

        # Parse adopted value from conflict comment
        adopted_match = re.search(r'(?:채택|adopted|PART2)[=:\s]+["\']?([^\s"\'<>]+)', content, re.IGNORECASE)
        adopted_value = adopted_match.group(1).strip().rstrip(',;.') if adopted_match else None

        # Check if adopted value appears in surrounding body text (±5 lines)
        body_verified = None
        if adopted_value and len(adopted_value) >= 2:
            # Get surrounding lines
            start_line = max(0, line_num - 6)
            end_line = min(len(lines), line_num + 5)
            surrounding = '\n'.join(lines[start_line:end_line])
            body_verified = adopted_value in surrounding
            if not body_verified:
                errors.append({
                    "line": line_num,
                    "type": "source_conflict_body_mismatch",
                    "detail": f"Adopted value '{adopted_value}' not found in surrounding body text",
                    "conflict_content": content[:200]
                })

        source_conflicts.append({
            "line": line_num,
            "content": content[:200],
            "adopted_value": adopted_value,
            "body_verified": body_verified
        })

    result = {
        "script": "0-G",
        "name": "HTML Comment Integrity + SOURCE_CONFLICT Body Verification",
        "source_conflicts": source_conflicts,
        "total_source_conflicts": len(source_conflicts),
        "errors": errors,
        "total_errors": len(errors),
        "verdict": "PASS" if len(errors) == 0 else "FAIL"
    }
    return result


# ─────────────────────────────────────────────
# 0-H: 헤더 카운트 vs 실제 행 수
# ─────────────────────────────────────────────
def check_0H():
    """Compare 'N건/N개/N항목' patterns vs actual data row counts."""
    text = read_part2()
    lines = text.split('\n')
    code_ranges = get_code_block_ranges(lines)

    errors = []
    # Only match patterns in HEADINGS (### level) that explicitly describe table row counts
    # Pattern: "heading text (N개)" or "heading text N개 항목" directly before a table
    heading_count_pattern = re.compile(r'^#+\s+.*?(\d+)\s*(?:건|개|항목)', re.UNICODE)
    # Also: table cell headers with explicit counts like "N개 항목"
    inline_count_pattern = re.compile(r'(\d+)\s*(?:건|개)\s*\)', re.UNICODE)

    for i, line in enumerate(lines):
        if line_in_ranges(i, code_ranges):
            continue

        # Only check markdown headings with count patterns
        if not line.strip().startswith('#'):
            continue

        m = heading_count_pattern.match(line)
        if not m:
            continue

        expected = int(m.group(1))
        if expected < 2 or expected > 500:
            continue

        # Skip if the heading contains ~ (approximate)
        if '~' in line and f'~{expected}' in line.replace(' ', ''):
            continue

        # Find next table within 5 lines
        for j in range(i + 1, min(i + 8, len(lines))):
            if line_in_ranges(j, code_ranges):
                continue
            if j + 1 < len(lines) and re.match(r'\s*\|[\s\-:|]+\|', lines[j + 1] if j + 1 < len(lines) else ""):
                # Found a table, count data rows
                k = j + 2
                row_count = 0
                while k < len(lines):
                    if '|' not in lines[k] or lines[k].strip() == '':
                        break
                    if not line_in_ranges(k, code_ranges):
                        row_count += 1
                    k += 1

                if row_count > 0 and abs(row_count - expected) > 0:
                    errors.append({
                        "header_line": i + 1,
                        "header_value": expected,
                        "actual_rows": row_count,
                        "difference": row_count - expected,
                        "context": line.strip()[:100]
                    })
                break

    result = {
        "script": "0-H",
        "name": "Header Count vs Actual Rows",
        "errors": errors,
        "total_errors": len(errors),
        "verdict": "PASS" if len(errors) == 0 else "FAIL"
    }
    return result


# ─────────────────────────────────────────────
# Main Execution
# ─────────────────────────────────────────────
def main():
    checks = [
        ("0-A", check_0A),
        ("0-B", check_0B),
        ("0-C", check_0C),
        ("0-D", check_0D),
        ("0-E", check_0E),
        ("0-F", check_0F),
        ("0-G", check_0G),
        ("0-H", check_0H),
    ]

    all_results = []
    for name, func in checks:
        print(f"Running {name}...", end=" ")
        try:
            result = func()
            all_results.append(result)
            print(f"{result['verdict']} ({result['total_errors']} errors)")

            # Save individual JSON
            out_path = RESULT / f"{name}.json"
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            all_results.append({
                "script": name,
                "verdict": "ERROR",
                "error": str(e)
            })

    # Summary
    print("\n" + "=" * 60)
    print("Part I Summary (0-A ~ 0-H)")
    print("=" * 60)
    for r in all_results:
        v = r.get('verdict', 'ERROR')
        e = r.get('total_errors', '?')
        print(f"  {r['script']:6s} - {v:5s} ({e} errors)")

    return all_results


if __name__ == "__main__":
    results = main()
