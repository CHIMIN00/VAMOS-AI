import json
import re
import sys

input_file = r"D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md"
output_file = r"D:\VAMOS\04. 구현단계\v11_results\phase0\v11_reference_map.json"

# Read the file
with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

total_lines = len(lines)

# 1. Extract section references
section_references = []
section_ref_pattern = re.compile(r'§(\d+(?:\.\d+)*)')

# 2. Extract cross-references
cross_references = []

# 3. Extract HTML comments
html_comments = []

# =====================================================================
# Build actual_sections map from headings
# =====================================================================
actual_sections = {}

# Patterns for markdown headings containing section numbers:
#   "# 1. 전체 구현 로드맵"  -> section "1"
#   "## 1.1 버전별"         -> section "1.1"
#   "## 6.10 Cloud Library" -> section "6.10"
#   "### 6.10.1 Real-Time"  -> section "6.10.1"
#   "## V0-STEP-1: ..."     -> not a numbered section (skip)
# Match: start of line, one or more #, space, then digits with dots
heading_sec_pattern = re.compile(r'^(#+)\s+(\d+(?:\.\d+)*)\b')

for i, line in enumerate(lines, 1):
    m = heading_sec_pattern.match(line)
    if m:
        sec_num = m.group(2)
        # Remove trailing period if present (e.g., "1." -> "1")
        sec_num = sec_num.rstrip('.')
        if sec_num not in actual_sections:
            actual_sections[sec_num] = i

# =====================================================================
# Patterns for cross-references
# =====================================================================
v0_step_pattern = re.compile(r'\b(V0-STEP-(\d+))\b')
v1_phase_pattern = re.compile(r'\b(V1-Phase\s+(\d+))\b', re.IGNORECASE)
v2_phase_pattern = re.compile(r'\b(V2-Phase\s+(\d+))\b', re.IGNORECASE)
v3_phase_pattern = re.compile(r'\b(V3-Phase\s+(\d+))\b', re.IGNORECASE)
step_pattern = re.compile(r'\b(STEP[-\s](\d+))\b', re.IGNORECASE)
phase_pattern_generic = re.compile(r'\b(Phase\s+(\d+[A-Za-z]?))\b', re.IGNORECASE)

# HTML comment patterns:
#   <!-- SOURCE_CONFLICT: ... -->
#   <!-- NOTE (XREF-V0-10): ... -->
#   <!-- PATCH-H02 ... -->
#   <!-- XREF ... -->
html_comment_pattern_single = re.compile(r'<!--\s*(SOURCE_CONFLICT|XREF|NOTE|PATCH)\b(.*?)-->')
# Also match XREF inside NOTE: <!-- NOTE (XREF-...) ... -->
xref_inside_note_pattern = re.compile(r'<!--\s*NOTE\s*\(XREF[-_]([^)]+)\)\s*:\s*(.*?)-->')

# =====================================================================
# Process each line
# =====================================================================
for i, line in enumerate(lines, 1):
    # --- Section references (§N.N) ---
    for m in section_ref_pattern.finditer(line):
        ref = m.group(1)
        exists = ref in actual_sections
        section_references.append({
            "line": i,
            "pattern": f"§{ref}",
            "target_section": f"§{ref}",
            "target_exists": exists
        })

    # --- Cross-references ---
    # V0-STEP-N
    for m in v0_step_pattern.finditer(line):
        cross_references.append({
            "line": i,
            "pattern": m.group(1),
            "type": "V0-STEP",
            "target": f"V0-STEP-{m.group(2)}"
        })

    # V1-Phase N
    for m in v1_phase_pattern.finditer(line):
        cross_references.append({
            "line": i,
            "pattern": m.group(1),
            "type": "V1-Phase",
            "target": f"V1-Phase {m.group(2)}"
        })

    # V2-Phase N
    for m in v2_phase_pattern.finditer(line):
        cross_references.append({
            "line": i,
            "pattern": m.group(1),
            "type": "V2-Phase",
            "target": f"V2-Phase {m.group(2)}"
        })

    # V3-Phase N
    for m in v3_phase_pattern.finditer(line):
        cross_references.append({
            "line": i,
            "pattern": m.group(1),
            "type": "V3-Phase",
            "target": f"V3-Phase {m.group(2)}"
        })

    # Generic STEP-N (exclude V0-STEP-N already captured)
    for m in step_pattern.finditer(line):
        full = m.group(1)
        start_pos = m.start()
        prefix = line[max(0, start_pos - 3):start_pos]
        if 'V0-' not in prefix:
            cross_references.append({
                "line": i,
                "pattern": full,
                "type": "STEP",
                "target": f"STEP {m.group(2)}"
            })

    # Generic Phase N (exclude VN-Phase already captured)
    for m in phase_pattern_generic.finditer(line):
        full = m.group(1)
        start_pos = m.start()
        prefix = line[max(0, start_pos - 3):start_pos]
        if not re.search(r'V[0-3]-\s*$', prefix):
            cross_references.append({
                "line": i,
                "pattern": full,
                "type": "Phase",
                "target": f"Phase {m.group(2)}"
            })

    # --- HTML comments ---
    # Standard patterns: SOURCE_CONFLICT, NOTE, PATCH
    for m in html_comment_pattern_single.finditer(line):
        comment_type = m.group(1)
        content = m.group(2).strip()
        content = re.sub(r'\s+', ' ', content)
        if content.startswith(':'):
            content = content[1:].strip()
        html_comments.append({
            "line": i,
            "type": comment_type,
            "content": content
        })

    # XREF embedded in NOTE: <!-- NOTE (XREF-V0-10): ... -->
    for m in xref_inside_note_pattern.finditer(line):
        xref_id = m.group(1)
        content = m.group(2).strip()
        content = re.sub(r'\s+', ' ', content)
        html_comments.append({
            "line": i,
            "type": "XREF",
            "content": f"XREF-{xref_id}: {content}"
        })

# =====================================================================
# Multi-line HTML comments (scan full text)
# =====================================================================
full_text = ''.join(lines)
for m in re.finditer(r'<!--\s*(SOURCE_CONFLICT|XREF|NOTE|PATCH)\b([\s\S]*?)-->', full_text):
    comment_type = m.group(1)
    content = m.group(2).strip()
    content = re.sub(r'\s+', ' ', content)
    if content.startswith(':'):
        content = content[1:].strip()
    pos = m.start()
    line_num = full_text[:pos].count('\n') + 1
    already_found = any(
        e["line"] == line_num and e["type"] == comment_type
        for e in html_comments
    )
    if not already_found:
        html_comments.append({
            "line": line_num,
            "type": comment_type,
            "content": content
        })

# Multi-line XREF inside NOTE
for m in re.finditer(r'<!--\s*NOTE\s*\(XREF[-_]([^)]+)\)\s*:\s*([\s\S]*?)-->', full_text):
    xref_id = m.group(1)
    content = m.group(2).strip()
    content = re.sub(r'\s+', ' ', content)
    pos = m.start()
    line_num = full_text[:pos].count('\n') + 1
    already_found = any(
        e["line"] == line_num and e["type"] == "XREF"
        for e in html_comments
    )
    if not already_found:
        html_comments.append({
            "line": line_num,
            "type": "XREF",
            "content": f"XREF-{xref_id}: {content}"
        })

# =====================================================================
# Deduplicate
# =====================================================================

# Deduplicate html_comments
seen_comments = set()
unique_comments = []
for c in sorted(html_comments, key=lambda x: x["line"]):
    key = (c["line"], c["type"], c["content"][:80])
    if key not in seen_comments:
        seen_comments.add(key)
        unique_comments.append(c)
html_comments = unique_comments

# Deduplicate section references
seen_refs = set()
unique_refs = []
for r in section_references:
    key = (r["line"], r["pattern"])
    if key not in seen_refs:
        seen_refs.add(key)
        unique_refs.append(r)
section_references = unique_refs

# Deduplicate cross references
seen_cross = set()
unique_cross = []
for r in cross_references:
    key = (r["line"], r["pattern"], r["type"])
    if key not in seen_cross:
        seen_cross.add(key)
        unique_cross.append(r)
cross_references = unique_cross

# =====================================================================
# Section 6.x verification
# =====================================================================
section6_refs = [r for r in section_references if r["pattern"].startswith("§6")]
section6_verification = []
seen_s6 = set()
for ref in section6_refs:
    sec_num = ref["pattern"][1:]  # remove §
    if sec_num in seen_s6:
        continue
    seen_s6.add(sec_num)
    exists = sec_num in actual_sections
    actual_line = actual_sections.get(sec_num, None)
    section6_verification.append({
        "reference": ref["pattern"],
        "referenced_from_line": ref["line"],
        "exists": exists,
        "actual_location_line": actual_line
    })

# =====================================================================
# Section 7 mapping: checklist items referencing §2~§6
# =====================================================================
section7_mapping = []
in_section7 = False
for i, line in enumerate(lines, 1):
    stripped = line.strip()
    if re.match(r'^#\s+7\.\s', line):
        in_section7 = True
        continue
    # End of section 7 if we hit a new top-level heading that is not 7.x
    if in_section7 and re.match(r'^#\s+\d+\.\s', line) and not re.match(r'^#\s+7', line):
        in_section7 = False

    if in_section7:
        refs_in_line = section_ref_pattern.findall(line)
        for ref in refs_in_line:
            parts = ref.split('.')
            try:
                ref_num = int(parts[0])
            except ValueError:
                continue
            if 2 <= ref_num <= 6:
                # Extract item text
                table_match = re.match(r'\|\s*\d+\s*\|(.+?)\|', line)
                if table_match:
                    item_text = table_match.group(1).strip()
                else:
                    item_text = stripped.lstrip('#').lstrip('-').lstrip('> ').strip()
                if item_text and len(item_text) > 3:
                    section7_mapping.append({
                        "checklist_item": item_text[:200],
                        "line": i,
                        "maps_to_section": f"§{ref}"
                    })

# =====================================================================
# Summary
# =====================================================================
broken_refs = [r for r in section_references if not r["target_exists"]]
broken_refs_unique_patterns = list({r["pattern"] for r in broken_refs})

comment_type_counts = {"SOURCE_CONFLICT": 0, "XREF": 0, "NOTE": 0, "PATCH": 0}
for c in html_comments:
    if c["type"] in comment_type_counts:
        comment_type_counts[c["type"]] += 1

# =====================================================================
# Build output JSON
# =====================================================================
output = {
    "meta": {
        "source": "VAMOS_구현가이드_PART2_구현단계.md",
        "version": "v24.0.0",
        "total_lines": total_lines,
        "generated_at": "2026-03-12",
        "task_id": "0-B"
    },
    "section_references": section_references,
    "cross_references": cross_references,
    "section6_verification": section6_verification,
    "section7_mapping": section7_mapping,
    "html_comments": html_comments,
    "summary": {
        "total_section_refs": len(section_references),
        "total_cross_refs": len(cross_references),
        "broken_refs": [{"pattern": r["pattern"], "line": r["line"]} for r in broken_refs],
        "broken_ref_unique_patterns": sorted(broken_refs_unique_patterns),
        "total_html_comments": len(html_comments),
        "html_comment_types": comment_type_counts
    }
}

# Write output
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Generated reference map at: {output_file}")
print(f"  Total lines: {total_lines}")
print(f"  Total section refs: {len(section_references)}")
print(f"  Total cross refs: {len(cross_references)}")
print(f"  Section 6 verifications: {len(section6_verification)}")
print(f"  Section 7 mappings: {len(section7_mapping)}")
print(f"  HTML comments: {len(html_comments)}")
print(f"    SOURCE_CONFLICT: {comment_type_counts['SOURCE_CONFLICT']}")
print(f"    XREF: {comment_type_counts['XREF']}")
print(f"    NOTE: {comment_type_counts['NOTE']}")
print(f"    PATCH: {comment_type_counts['PATCH']}")
print(f"  Broken refs (unique patterns): {len(broken_refs_unique_patterns)}")
print(f"  Broken ref patterns: {sorted(broken_refs_unique_patterns)[:20]}...")
print(f"  Actual sections found ({len(actual_sections)}): {sorted(actual_sections.keys())}")
