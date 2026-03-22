#!/usr/bin/env python3
"""Parse codeblocks from VAMOS PART2 markdown and generate inventory JSON.

This parser handles:
1. Regular code blocks (``` to ```)
2. 4-backtick blocks (```` to ````) - AI prompts
3. Nested code blocks inside 4-backtick AI prompt blocks
"""
import json
import re

input_file = r"D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md"
output_file = r"D:\VAMOS\04. 구현단계\v11_results\phase0\v11_codeblock_inventory.json"

with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

total_lines = len(lines)


def get_parent_section(line_num, section_headers):
    """Get the parent section for a given line number."""
    best = "Unknown"
    for sec_line, sec_title in section_headers:
        if sec_line <= line_num:
            best = sec_title
        else:
            break
    return best


# First pass: collect all section headers
section_headers = []
for i, line in enumerate(lines):
    stripped = line.rstrip()
    m = re.match(r'^(#{1,6})\s+(.*)', stripped)
    if m:
        title = m.group(2).strip()
        title = re.sub(r'<!--.*?-->', '', title).strip()
        section_headers.append((i + 1, title))


def classify_language(lang_tag):
    """Classify a language tag into a standard category."""
    lang_lower = lang_tag.lower() if lang_tag else ""
    if lang_lower in ("python", "py"):
        return "python"
    elif lang_lower in ("rust", "rs"):
        return "rust"
    elif lang_lower in ("typescript", "ts", "tsx"):
        return "typescript"
    elif lang_lower == "toml":
        return "toml"
    elif lang_lower == "json":
        return "json"
    elif lang_lower in ("yaml", "yml"):
        return "yaml"
    elif lang_lower in ("bash", "sh", "shell", "zsh"):
        return "bash"
    elif lang_lower == "sql":
        return "sql"
    elif lang_lower == "text":
        return "text"
    elif lang_lower == "":
        return "none"
    else:
        return "other"


def extract_symbols(language, content_lines):
    """Extract imports and defined symbols from code block content."""
    imports = []
    defined_symbols = []

    if language == "python":
        for cl in content_lines:
            cl_stripped = cl.strip()
            if re.match(r'^(from\s+\S+\s+import\s+|import\s+)', cl_stripped):
                imports.append(cl_stripped)
            cm = re.match(r'^class\s+(\w+)', cl_stripped)
            if cm:
                defined_symbols.append("class " + cm.group(1))
            fm = re.match(r'^(?:async\s+)?def\s+(\w+)', cl_stripped)
            if fm:
                defined_symbols.append("def " + fm.group(1))
    elif language == "rust":
        for cl in content_lines:
            cl_stripped = cl.strip()
            if re.match(r'^use\s+', cl_stripped):
                imports.append(cl_stripped.rstrip(';'))
            fm = re.match(r'^(?:pub\s+)?(?:async\s+)?fn\s+(\w+)', cl_stripped)
            if fm:
                defined_symbols.append("fn " + fm.group(1))
            sm = re.match(r'^(?:pub\s+)?struct\s+(\w+)', cl_stripped)
            if sm:
                defined_symbols.append("struct " + sm.group(1))
            im_match = re.match(r'^impl\s+(\w+)', cl_stripped)
            if im_match:
                defined_symbols.append("impl " + im_match.group(1))
    elif language == "typescript":
        for cl in content_lines:
            cl_stripped = cl.strip()
            if re.match(r'^import\s+', cl_stripped):
                imports.append(cl_stripped)
            m2 = re.match(
                r'^(?:export\s+)?(?:const|let|var|function|class|interface|type)\s+(\w+)',
                cl_stripped,
            )
            if m2:
                defined_symbols.append(m2.group(1))
    elif language == "toml":
        for cl in content_lines:
            cl_stripped = cl.strip()
            tm = re.match(r'^\[([^\]]+)\]', cl_stripped)
            if tm:
                defined_symbols.append("[" + tm.group(1) + "]")
    elif language == "sql":
        for cl in content_lines:
            cl_stripped = cl.strip()
            cm = re.match(
                r'CREATE\s+(?:TABLE|INDEX)\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)',
                cl_stripped,
                re.IGNORECASE,
            )
            if cm:
                defined_symbols.append(cm.group(1))
    elif language == "json":
        content_text = "".join(content_lines)
        try:
            parsed = json.loads(content_text)
            if isinstance(parsed, dict):
                for key in parsed:
                    defined_symbols.append(key)
        except Exception:
            pass
    elif language == "yaml":
        for cl in content_lines:
            cl_stripped = cl.strip()
            ym = re.match(r'^(\w[\w-]*):', cl_stripped)
            if ym and not cl.startswith(" "):
                defined_symbols.append(ym.group(1))

    return imports, defined_symbols


# Second pass: find all code blocks (including nested ones inside 4-backtick blocks)
codeblocks = []
block_id = 0
i = 0

while i < total_lines:
    line = lines[i].rstrip()

    # Check for 4-backtick block opening (AI prompts): ````text
    m4 = re.match(r'^(`{4,})(\w*)\s*$', line)
    if m4:
        backtick_count = len(m4.group(1))
        lang_tag = m4.group(2) if m4.group(2) else ""
        start_line = i + 1  # 1-indexed
        language = classify_language(lang_tag)
        parent_section = get_parent_section(start_line, section_headers)

        # Find closing 4-backtick
        j = i + 1
        found_end = False
        while j < total_lines:
            end_line_text = lines[j].rstrip()
            end_m = re.match(r'^(`{4,})\s*$', end_line_text)
            if end_m and len(end_m.group(1)) >= backtick_count:
                end_line = j + 1
                found_end = True
                break
            j += 1

        if found_end:
            # Record the outer 4-backtick block
            block_id += 1
            outer_block_id = block_id
            content_lines_outer = [lines[k] for k in range(i + 1, j)]

            imports_outer, symbols_outer = extract_symbols(language, content_lines_outer)
            codeblocks.append({
                "id": block_id,
                "start_line": start_line,
                "end_line": end_line,
                "line_count": end_line - start_line + 1,
                "language": language,
                "language_tag": lang_tag,
                "parent_section": parent_section,
                "imports": imports_outer,
                "defined_symbols": symbols_outer,
                "referenced_symbols": [],
                "_content_lines": content_lines_outer,
                "is_ai_prompt": True,
            })

            # Now scan for nested 3-backtick blocks inside this 4-backtick block
            ni = i + 1  # start scanning inside the block
            while ni < j:
                nline = lines[ni].rstrip()
                nm = re.match(r'^(`{3})(\w*)\s*$', nline)
                if nm:
                    nested_backtick_count = len(nm.group(1))
                    nested_lang_tag = nm.group(2) if nm.group(2) else ""
                    nested_start = ni + 1  # 1-indexed

                    # Find closing nested backtick
                    nj = ni + 1
                    nested_found = False
                    while nj < j:
                        nend_text = lines[nj].rstrip()
                        nend_m = re.match(r'^(`{3})\s*$', nend_text)
                        if nend_m:
                            nested_end = nj + 1
                            nested_found = True
                            break
                        nj += 1

                    if nested_found:
                        block_id += 1
                        nested_language = classify_language(nested_lang_tag)
                        nested_content = [lines[k] for k in range(ni + 1, nj)]
                        nested_imports, nested_symbols = extract_symbols(nested_language, nested_content)
                        nested_parent = get_parent_section(nested_start, section_headers)

                        codeblocks.append({
                            "id": block_id,
                            "start_line": nested_start,
                            "end_line": nested_end,
                            "line_count": nested_end - nested_start + 1,
                            "language": nested_language,
                            "language_tag": nested_lang_tag,
                            "parent_section": nested_parent + " (nested in AI prompt)",
                            "imports": nested_imports,
                            "defined_symbols": nested_symbols,
                            "referenced_symbols": [],
                            "_content_lines": nested_content,
                            "nested_in_prompt_block": outer_block_id,
                        })
                        ni = nj + 1
                        continue
                ni += 1

            i = j + 1
            continue

    # Check for regular 3-backtick code block opening
    m3 = re.match(r'^(>\s*)*(`{3})(\w*)\s*$', line)
    if m3:
        backtick_count = len(m3.group(2))
        lang_tag = m3.group(3) if m3.group(3) else ""
        start_line = i + 1
        language = classify_language(lang_tag)
        parent_section = get_parent_section(start_line, section_headers)

        j = i + 1
        found_end = False
        while j < total_lines:
            end_line_text = lines[j].rstrip()
            end_m = re.match(r'^(>\s*)*(`{3})\s*$', end_line_text)
            if end_m and len(end_m.group(2)) >= backtick_count:
                end_line = j + 1
                found_end = True
                break
            j += 1

        if found_end:
            block_id += 1
            content_lines_block = [lines[k] for k in range(i + 1, j)]
            imports_b, symbols_b = extract_symbols(language, content_lines_block)

            codeblocks.append({
                "id": block_id,
                "start_line": start_line,
                "end_line": end_line,
                "line_count": end_line - start_line + 1,
                "language": language,
                "language_tag": lang_tag,
                "parent_section": parent_section,
                "imports": imports_b,
                "defined_symbols": symbols_b,
                "referenced_symbols": [],
                "_content_lines": content_lines_block,
            })

            i = j + 1
            continue

    i += 1


# Build language summary
lang_summary = {
    "python": 0,
    "rust": 0,
    "typescript": 0,
    "toml": 0,
    "json": 0,
    "yaml": 0,
    "bash": 0,
    "sql": 0,
    "text": 0,
    "other": 0,
    "none": 0,
}
for cb in codeblocks:
    lang = cb["language"]
    if lang in lang_summary:
        lang_summary[lang] += 1
    else:
        lang_summary[lang] = lang_summary.get(lang, 0) + 1


# Build package registry
package_map = {}
for cb in codeblocks:
    for imp in cb["imports"]:
        lang = cb["language"]
        pkg = None
        if lang == "python":
            m2 = re.match(r'from\s+(\w+)', imp)
            if m2:
                pkg = m2.group(1)
            else:
                m2 = re.match(r'import\s+(\w+)', imp)
                if m2:
                    pkg = m2.group(1)
        elif lang == "rust":
            m2 = re.match(r'use\s+(\w+)', imp)
            if m2:
                pkg = m2.group(1)
        elif lang == "typescript":
            m2 = re.search(r'from\s+["\']([^"\']+)["\']', imp)
            if m2:
                pkg = m2.group(1)
            else:
                m2 = re.match(r'import\s+(\w+)', imp)
                if m2:
                    pkg = m2.group(1)
        if pkg:
            key = (pkg, lang)
            if key not in package_map:
                package_map[key] = []
            package_map[key].append(cb["id"])

package_registry = []
for (pkg, lang), blocks in sorted(package_map.items()):
    package_registry.append({
        "package": pkg,
        "language": lang,
        "used_in_blocks": sorted(set(blocks)),
    })


# Build cross-references
symbol_map = {}
for cb in codeblocks:
    for sym in cb["defined_symbols"]:
        parts = sym.split(" ", 1)
        if len(parts) == 2:
            stype, sname = parts
        else:
            stype = "symbol"
            sname = sym
        if sname not in symbol_map:
            symbol_map[sname] = {"type": stype, "defined_in": [], "referenced_in": []}
        symbol_map[sname]["defined_in"].append(cb["id"])

for cb in codeblocks:
    content = "".join(cb.get("_content_lines", []))
    for sname, sinfo in symbol_map.items():
        if cb["id"] in sinfo["defined_in"]:
            continue
        if len(sname) > 2 and sname in content:
            sinfo["referenced_in"].append(cb["id"])

cross_references = []
for sname, sinfo in sorted(symbol_map.items()):
    if sinfo["referenced_in"]:
        cross_references.append({
            "symbol": sname,
            "type": sinfo["type"],
            "defined_in_blocks": sorted(set(sinfo["defined_in"])),
            "referenced_in_blocks": sorted(set(sinfo["referenced_in"])),
        })


# Calculate totals
total_codeblocks = len(codeblocks)
total_lines_of_code = sum(cb["line_count"] for cb in codeblocks)
unique_packages = len(package_registry)
cross_referenced_symbols = len(cross_references)

# Remove internal fields for output
output_blocks = []
for cb in codeblocks:
    block_out = {
        "id": cb["id"],
        "start_line": cb["start_line"],
        "end_line": cb["end_line"],
        "line_count": cb["line_count"],
        "language": cb["language"],
        "language_tag": cb["language_tag"],
        "parent_section": cb["parent_section"],
        "imports": cb["imports"],
        "defined_symbols": cb["defined_symbols"],
        "referenced_symbols": cb["referenced_symbols"],
    }
    if cb.get("is_ai_prompt"):
        block_out["is_ai_prompt"] = True
    if cb.get("nested_in_prompt_block"):
        block_out["nested_in_prompt_block"] = cb["nested_in_prompt_block"]
    output_blocks.append(block_out)


# Build final output
output = {
    "meta": {
        "source": "VAMOS_\uad6c\ud604\uac00\uc774\ub4dc_PART2_\uad6c\ud604\ub2e8\uacc4.md",
        "version": "v24.0.0",
        "total_lines": total_lines,
        "generated_at": "2026-03-12",
        "task_id": "0-G",
    },
    "codeblocks": output_blocks,
    "language_summary": lang_summary,
    "package_registry": package_registry,
    "cross_references": cross_references,
    "summary": {
        "total_codeblocks": total_codeblocks,
        "total_lines_of_code": total_lines_of_code,
        "unique_packages": unique_packages,
        "cross_referenced_symbols": cross_referenced_symbols,
    },
}

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Done! Wrote {output_file}")
print(f"Total codeblocks: {total_codeblocks}")
print(f"Total lines of code: {total_lines_of_code}")
print(f"Language summary: {json.dumps(lang_summary, indent=2)}")
print(f"Unique packages: {unique_packages}")
print(f"Cross-referenced symbols: {cross_referenced_symbols}")
print()

# Print detailed breakdown
ai_prompts = [cb for cb in codeblocks if cb.get("is_ai_prompt")]
nested = [cb for cb in codeblocks if cb.get("nested_in_prompt_block")]
regular = [cb for cb in codeblocks if not cb.get("is_ai_prompt") and not cb.get("nested_in_prompt_block")]
print(f"AI prompt blocks (````text): {len(ai_prompts)}")
print(f"Nested code blocks (inside AI prompts): {len(nested)}")
print(f"Regular code blocks: {len(regular)}")
print()
print("Regular blocks by language:")
for cb in regular:
    print(f"  #{cb['id']:3d} L{cb['start_line']:4d}-{cb['end_line']:4d} ({cb['line_count']:3d} lines) [{cb['language']:10s}] {cb['parent_section'][:60]}")
print()
print("Nested blocks by language:")
for cb in nested:
    print(f"  #{cb['id']:3d} L{cb['start_line']:4d}-{cb['end_line']:4d} ({cb['line_count']:3d} lines) [{cb['language']:10s}] {cb['parent_section'][:60]}")
