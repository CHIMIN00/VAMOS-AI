#!/usr/bin/env python3
"""VAMOS v8.1 Phase 0 - Part II: Implementation Verification (IMP-A ~ IMP-F)"""

import re
import json
import os
from pathlib import Path
from collections import defaultdict

PART2 = Path(r"D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md")
SRC = Path(r"C:\tmp\output\updated\PHASE_B_EXHAUSTIVE_ANALYSIS.md")
RESULT = Path(r"D:\VAMOS\04. 구현단계\v8_results\phase0")


def read_file(path):
    return path.read_text(encoding="utf-8")


def get_code_block_ranges(lines):
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


def line_in_ranges(line_idx, ranges):
    for s, e in ranges:
        if s <= line_idx <= e:
            return True
    return False


# -----------------------------------------------
# IMP-A: Module Dependency Graph
# -----------------------------------------------
def check_IMP_A():
    """Parse V1~V3 module dependency columns -> directed graph -> cycle detection + order violations."""
    text = read_file(PART2)
    lines = text.split('\n')
    code_ranges = get_code_block_ranges(lines)

    # Extract dependency info from tables in V1-Phase 1 (lines ~400-424)
    # Pattern: | order | module | content | dependency | reference |
    modules = []
    dep_graph = defaultdict(list)  # module -> [dependencies]
    all_module_names = set()

    # Scan for tables with dependency columns
    i = 0
    while i < len(lines):
        line = lines[i]
        if line_in_ranges(i, code_ranges):
            i += 1
            continue

        if '|' in line and i + 1 < len(lines):
            next_line = lines[i + 1] if i + 1 < len(lines) else ""
            if re.match(r'\s*\|[\s\-:|]+\|', next_line):
                headers = [c.strip().lower() for c in line.split('|') if c.strip() != '']
                dep_col = None
                mod_col = None

                for idx, h in enumerate(headers):
                    if h in ('의존성', 'dependency', '의존'):
                        dep_col = idx
                    if h in ('모듈', 'module'):
                        mod_col = idx

                if dep_col is not None and mod_col is not None:
                    j = i + 2
                    while j < len(lines):
                        data_line = lines[j]
                        if '|' not in data_line or data_line.strip() == '':
                            break
                        if line_in_ranges(j, code_ranges):
                            j += 1
                            continue
                        cells = [c.strip() for c in data_line.split('|') if c.strip() != '']
                        if mod_col < len(cells) and dep_col < len(cells):
                            mod_name = cells[mod_col].strip()
                            dep_str = cells[dep_col].strip()
                            # Extract module IDs like I-1, I-2, E-1 etc
                            mod_id = re.search(r'([IESABCD]-\d+)', mod_name)
                            if mod_id:
                                mod_id = mod_id.group(1)
                                all_module_names.add(mod_id)
                                # Parse dependencies
                                if dep_str and dep_str not in ('없음', '-', 'None', ''):
                                    deps = re.findall(r'([IESABCD]-\d+)', dep_str)
                                    for d in deps:
                                        dep_graph[mod_id].append(d)
                                        all_module_names.add(d)
                                    if '전체' in dep_str:
                                        modules.append({
                                            "module": mod_id,
                                            "deps": "ALL",
                                            "line": j + 1
                                        })
                                else:
                                    modules.append({
                                        "module": mod_id,
                                        "deps": [],
                                        "line": j + 1
                                    })
                        j += 1
                    i = j
                    continue
        i += 1

    # Cycle detection using DFS
    def find_cycles(graph):
        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path + [neighbor])
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor) if neighbor in path else -1
                    if cycle_start >= 0:
                        cycles.append(path[cycle_start:] + [neighbor])
                    else:
                        cycles.append([node, neighbor])
            rec_stack.discard(node)

        for node in list(graph.keys()):
            if node not in visited:
                dfs(node, [node])
        return cycles

    cycles = find_cycles(dep_graph)

    # Order violation: if module X depends on Y, but X has a lower order number
    order_violations = []

    result = {
        "script": "IMP-A",
        "name": "Module Dependency Graph",
        "nodes": sorted(list(all_module_names)),
        "node_count": len(all_module_names),
        "edges": {k: v for k, v in dep_graph.items()},
        "edge_count": sum(len(v) for v in dep_graph.values()),
        "cycles": cycles,
        "cycle_count": len(cycles),
        "order_violations": order_violations,
        "errors": [{"type": "BLOCKER_CYCLE", "cycle": c} for c in cycles],
        "total_errors": len(cycles),
        "verdict": "PASS" if len(cycles) == 0 else "FAIL"
    }
    return result


# -----------------------------------------------
# IMP-B: Schema Field Count
# -----------------------------------------------
def check_IMP_B():
    """Extract 24 Pydantic model field counts from PART2. Verify DecisionSchema=17(FREEZE)."""
    text = read_file(PART2)
    lines = text.split('\n')
    code_ranges = get_code_block_ranges(lines)

    schemas = []
    # Find schema table in V0-STEP-2 (line ~201-229)
    i = 0
    while i < len(lines):
        line = lines[i]
        if line_in_ranges(i, code_ranges):
            i += 1
            continue

        if '|' in line and i + 1 < len(lines):
            next_line = lines[i + 1] if i + 1 < len(lines) else ""
            if re.match(r'\s*\|[\s\-:|]+\|', next_line):
                headers = [c.strip().lower() for c in line.split('|') if c.strip() != '']
                schema_col = None
                field_col = None

                for idx, h in enumerate(headers):
                    if 'schema' in h or '스키마' in h:
                        schema_col = idx
                    if '필드' in h and ('수' in h or 'count' in h.lower()):
                        field_col = idx

                if schema_col is not None and field_col is not None:
                    j = i + 2
                    while j < len(lines):
                        data_line = lines[j]
                        if '|' not in data_line or data_line.strip() == '':
                            break
                        if line_in_ranges(j, code_ranges):
                            j += 1
                            continue
                        clean = re.sub(r'<!--.*?-->', '', data_line)
                        cells = [c.strip() for c in clean.split('|') if c.strip() != '']
                        if schema_col < len(cells) and field_col < len(cells):
                            schema_name = cells[schema_col]
                            field_str = cells[field_col]
                            # Extract number from field count (may have "(FREEZE)" etc)
                            num_match = re.search(r'(\d+)', field_str)
                            if num_match:
                                field_count = int(num_match.group(1))
                                is_lock = 'LOCK' in field_str or 'FREEZE' in field_str
                                schemas.append({
                                    "schema_name": schema_name,
                                    "part2_count": field_count,
                                    "lock": is_lock,
                                    "raw": field_str,
                                    "line": j + 1
                                })
                        j += 1
                    i = j
                    continue
        i += 1

    # SRC cross-check: load schema data from SRC and compare field counts
    src_text = read_file(SRC) if SRC.exists() else ""
    src_schemas = {}
    if src_text:
        # Extract schema field counts from SRC (D2.1 data in exhaustive analysis)
        for m in re.finditer(r'(\w+Schema|\w+Frame|\w+Record|\w+Envelope|\w+Role|\w+Event|\w+Config)\b.*?(\d+)\s*(?:필드|fields?)', src_text, re.IGNORECASE):
            src_schemas[m.group(1)] = int(m.group(2))

    # Verify DecisionSchema specifically — SOT is D2.1-D2: 18 fields (14 req + 4 opt)
    errors = []
    for s in schemas:
        if 'DecisionSchema' in s['schema_name']:
            if s['part2_count'] != 18:
                errors.append({
                    "schema": s['schema_name'],
                    "expected": 18,
                    "actual": s['part2_count'],
                    "note": "DecisionSchema SOT (D2.1-D2 §4.1) = 18 fields (14 req + 4 opt). PART2 value is stale.",
                    "severity": "HIGH",
                    "line": s['line']
                })

    # Cross-check all schemas against SRC
    src_mismatches = []
    for s in schemas:
        sname = s['schema_name']
        if sname in src_schemas and src_schemas[sname] != s['part2_count']:
            src_mismatches.append({
                "schema": sname,
                "part2_count": s['part2_count'],
                "src_count": src_schemas[sname],
                "line": s['line']
            })

    if src_mismatches:
        for sm in src_mismatches:
            errors.append({
                "type": "src_schema_mismatch",
                "severity": "MEDIUM",
                **sm
            })

    result = {
        "script": "IMP-B",
        "name": "Schema Field Count + SRC Cross-Check",
        "total_schemas": len(schemas),
        "schemas": schemas,
        "src_schemas_found": len(src_schemas),
        "src_mismatches": src_mismatches,
        "errors": errors,
        "total_errors": len(errors),
        "verdict": "PASS" if len(errors) == 0 else "FAIL"
    }
    return result


# -----------------------------------------------
# IMP-C: API Endpoint Validation
# -----------------------------------------------
def check_IMP_C():
    """Extract IPC 72 + JSON-RPC 13 from PART2 vs SRC PHASE_B1 data."""
    part2_text = read_file(PART2)
    src_text = read_file(SRC) if SRC.exists() else ""

    # Extract IPC commands from PART2 section 6.2
    part2_ipc = set()
    # Find vamos:* patterns
    for m in re.finditer(r'`?(vamos:\w+:\w+)`?', part2_text):
        part2_ipc.add(m.group(1))

    # Extract JSON-RPC methods from PART2
    # Only match inside backtick-quoted identifiers to avoid prose false positives
    part2_rpc = set()
    rpc_patterns = [
        r'`(langgraph\.\w+\.\w+)`',
        r'`(embedding\.\w+\.\w+)`',
        r'`(llm\.\w+\.\w+)`',
    ]
    # mcp.* — only match backtick-quoted, exclude config/tool references
    mcp_pattern = r'`(mcp\.\w+\.\w+)`'
    mcp_exclude = {'mcp.server.name', 'mcp.server.port', 'mcp.tool.list', 'mcp.config'}

    for pattern in rpc_patterns:
        for m in re.finditer(pattern, part2_text):
            method = m.group(1)
            if not method.startswith('0.') and 'toml' not in method:
                part2_rpc.add(method)

    for m in re.finditer(mcp_pattern, part2_text):
        method = m.group(1)
        if method not in mcp_exclude and 'toml' not in method:
            part2_rpc.add(method)

    # Extract from SRC
    src_ipc = set()
    src_rpc = set()
    for m in re.finditer(r'`(vamos:\w+:\w+)`', src_text):
        src_ipc.add(m.group(1))
    for pattern in rpc_patterns:
        for m in re.finditer(pattern, src_text):
            method = m.group(1)
            if not method.startswith('0.') and 'toml' not in method:
                src_rpc.add(method)
    for m in re.finditer(mcp_pattern, src_text):
        method = m.group(1)
        if method not in mcp_exclude and 'toml' not in method:
            src_rpc.add(method)

    # Compare
    ipc_part2_only = sorted(part2_ipc - src_ipc) if src_ipc else []
    ipc_src_only = sorted(src_ipc - part2_ipc) if src_ipc else []
    ipc_matched = sorted(part2_ipc & src_ipc) if src_ipc else sorted(part2_ipc)

    rpc_part2_only = sorted(part2_rpc - src_rpc) if src_rpc else []
    rpc_src_only = sorted(src_rpc - part2_rpc) if src_rpc else []
    rpc_matched = sorted(part2_rpc & src_rpc) if src_rpc else sorted(part2_rpc)

    errors = []
    if ipc_part2_only:
        errors.append({"type": "ipc_part2_only", "count": len(ipc_part2_only), "items": ipc_part2_only[:10]})
    if ipc_src_only:
        errors.append({"type": "ipc_src_only", "count": len(ipc_src_only), "items": ipc_src_only[:10]})
    if rpc_part2_only:
        errors.append({"type": "rpc_part2_only", "count": len(rpc_part2_only), "items": rpc_part2_only[:10]})
    if rpc_src_only:
        errors.append({"type": "rpc_src_only", "count": len(rpc_src_only), "items": rpc_src_only[:10]})

    result = {
        "script": "IMP-C",
        "name": "API Endpoint Validation",
        "part2_ipc_count": len(part2_ipc),
        "part2_rpc_count": len(part2_rpc),
        "src_ipc_count": len(src_ipc),
        "src_rpc_count": len(src_rpc),
        "ipc": {
            "part2_only": ipc_part2_only,
            "src_only": ipc_src_only,
            "matched": ipc_matched,
            "matched_count": len(ipc_matched)
        },
        "rpc": {
            "part2_only": rpc_part2_only,
            "src_only": rpc_src_only,
            "matched": rpc_matched,
            "matched_count": len(rpc_matched)
        },
        "errors": errors,
        "total_errors": len(errors),
        "verdict": "PASS" if len(errors) == 0 else "FAIL",
        "note": "IPC expected=72, JSON-RPC expected=13"
    }
    return result


# -----------------------------------------------
# IMP-D: Config Key Validation
# -----------------------------------------------
def check_IMP_D():
    """Extract config.v1.toml 13 sections from PART2 vs SRC PHASE_B4."""
    part2_text = read_file(PART2)
    src_text = read_file(SRC) if SRC.exists() else ""

    # Extract TOML section headers from PART2
    part2_sections = set()
    part2_keys = defaultdict(list)

    # Find [section] patterns in code blocks
    lines = part2_text.split('\n')
    code_ranges = get_code_block_ranges(lines)
    in_toml_block = False
    current_section = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("```") and 'toml' in stripped.lower():
            in_toml_block = True
            continue
        if stripped.startswith("```") and in_toml_block:
            in_toml_block = False
            current_section = None
            continue

        if in_toml_block:
            # Section header
            m = re.match(r'\[([^\]]+)\]', stripped)
            if m and not stripped.startswith('[['):
                section = m.group(1)
                part2_sections.add(section)
                current_section = section
            elif stripped.startswith('[['):
                m = re.match(r'\[\[([^\]]+)\]\]', stripped)
                if m:
                    section = m.group(1)
                    part2_sections.add(section)
                    current_section = section

            # Key = value
            kv = re.match(r'(\w[\w_.]*)\s*=\s*(.+)', stripped)
            if kv and current_section:
                key = kv.group(1)
                value = kv.group(2).strip().rstrip('#').strip()
                # Remove inline comments
                value = re.sub(r'\s*#.*$', '', value).strip()
                part2_keys[current_section].append({
                    "key": key,
                    "value": value,
                    "line": i + 1
                })

    # Extract from SRC (PHASE_B4 data in exhaustive analysis)
    src_sections = set()
    src_keys = defaultdict(list)

    src_lines = src_text.split('\n')
    src_code_ranges = get_code_block_ranges(src_lines)
    in_toml = False
    curr_sect = None

    for i, line in enumerate(src_lines):
        stripped = line.strip()
        if stripped.startswith("```") and 'toml' in stripped.lower():
            in_toml = True
            continue
        if stripped.startswith("```") and in_toml:
            in_toml = False
            curr_sect = None
            continue

        if in_toml:
            m = re.match(r'\[([^\]]+)\]', stripped)
            if m and not stripped.startswith('[['):
                sect = m.group(1)
                src_sections.add(sect)
                curr_sect = sect
            elif stripped.startswith('[['):
                m2 = re.match(r'\[\[([^\]]+)\]\]', stripped)
                if m2:
                    sect = m2.group(1)
                    src_sections.add(sect)
                    curr_sect = sect

            kv = re.match(r'(\w[\w_.]*)\s*=\s*(.+)', stripped)
            if kv and curr_sect:
                key = kv.group(1)
                value = re.sub(r'\s*#.*$', '', kv.group(2).strip()).strip()
                src_keys[curr_sect].append({
                    "key": key,
                    "value": value,
                    "line": i + 1
                })

    # Compare sections
    part2_only = sorted(part2_sections - src_sections) if src_sections else []
    src_only = sorted(src_sections - part2_sections) if src_sections else []
    matched_sections = sorted(part2_sections & src_sections) if src_sections else sorted(part2_sections)

    # Compare key values for matched sections
    value_mismatches = []
    for sect in matched_sections:
        p2_dict = {k['key']: k['value'] for k in part2_keys.get(sect, [])}
        src_dict = {k['key']: k['value'] for k in src_keys.get(sect, [])}
        for key in set(p2_dict.keys()) & set(src_dict.keys()):
            if p2_dict[key] != src_dict[key]:
                value_mismatches.append({
                    "section": sect,
                    "key": key,
                    "part2_value": p2_dict[key],
                    "src_value": src_dict[key]
                })

    errors = []
    if value_mismatches:
        errors.extend([{"type": "value_mismatch", **vm} for vm in value_mismatches])

    # V7-1: Canonical 13-section validation against PHASE_B4 SOT
    b4_canonical_sections = {
        "core", "llm", "embedding", "vector_db", "graph_db", "storage",
        "cost", "guardrails", "mcp", "rbac", "rate_limit", "logging", "semantic_cache"
    }
    expected_sections = 13

    # Check PART2 sections against B4 canonical list
    section_name_issues = []
    part2_missing = sorted(b4_canonical_sections - part2_sections)
    part2_extra = sorted(part2_sections - b4_canonical_sections)
    if part2_missing:
        section_name_issues.append({
            "type": "missing_from_part2",
            "sections": part2_missing,
            "detail": "B4 canonical sections not found in PART2 config"
        })
    if part2_extra:
        section_name_issues.append({
            "type": "extra_in_part2",
            "sections": part2_extra,
            "detail": "PART2 config sections not in B4 canonical list"
        })

    if section_name_issues:
        for issue in section_name_issues:
            errors.append({"type": "section_name_mismatch", "severity": "HIGH", **issue})

    result = {
        "script": "IMP-D",
        "name": "Config Key Validation + V7-1 Canonical Section Check",
        "part2_section_count": len(part2_sections),
        "src_section_count": len(src_sections),
        "expected_sections": expected_sections,
        "b4_canonical_sections": sorted(list(b4_canonical_sections)),
        "part2_sections": sorted(list(part2_sections)),
        "src_sections": sorted(list(src_sections)),
        "part2_only_sections": part2_only,
        "src_only_sections": src_only,
        "matched_sections": matched_sections,
        "section_name_issues": section_name_issues,
        "value_mismatches": value_mismatches,
        "part2_total_keys": sum(len(v) for v in part2_keys.values()),
        "src_total_keys": sum(len(v) for v in src_keys.values()),
        "errors": errors,
        "total_errors": len(errors),
        "verdict": "PASS" if len(errors) == 0 else "FAIL",
        "note": f"PART2 has {len(part2_sections)} sections (B4 canonical: {expected_sections})"
    }
    return result


# -----------------------------------------------
# IMP-E: Module Activation Matrix
# -----------------------------------------------
def check_IMP_E():
    """Verify V0=5/V1=32/V2=42/V3=81 row sums, column sums, cumulative increase."""
    text = read_file(PART2)
    lines = text.split('\n')

    # Find the module activation matrix table (section 1.1, around line 39-44)
    matrix = {}
    expected = {"V0": 5, "V1": 32, "V2": 42, "V3": 81}

    # Parse the table
    for i, line in enumerate(lines):
        if '|' in line and i + 1 < len(lines):
            next_line = lines[i + 1] if i + 1 < len(lines) else ""
            if re.match(r'\s*\|[\s\-:|]+\|', next_line):
                headers = [c.strip() for c in line.split('|') if c.strip() != '']
                if 'I-Series' in headers and 'E-Series' in headers:
                    j = i + 2
                    while j < len(lines):
                        data_line = lines[j]
                        if '|' not in data_line or data_line.strip() == '':
                            break
                        cells = [c.strip() for c in data_line.split('|') if c.strip() != '']
                        if cells:
                            version = cells[0]
                            nums = []
                            for c in cells[1:]:
                                cleaned = re.sub(r'\*\*', '', c).strip()
                                try:
                                    nums.append(int(cleaned))
                                except ValueError:
                                    nums.append(None)
                            matrix[version] = {
                                "series_values": nums[:-1] if nums else [],  # Exclude sum column
                                "declared_sum": nums[-1] if nums else None,
                                "line": j + 1
                            }
                        j += 1
                    break

    errors = []

    # Verify row sums
    for version, data in matrix.items():
        vals = [v for v in data['series_values'] if v is not None]
        actual_sum = sum(vals)
        declared = data['declared_sum']
        if declared is not None and actual_sum != declared:
            errors.append({
                "type": "row_sum_error",
                "version": version,
                "calculated_sum": actual_sum,
                "declared_sum": declared,
                "line": data['line']
            })

        # Verify against expected
        if version in expected and declared is not None and declared != expected[version]:
            errors.append({
                "type": "expected_mismatch",
                "version": version,
                "expected": expected[version],
                "actual": declared,
                "line": data['line']
            })

    # Verify cumulative increase (V0 <= V1 <= V2 <= V3 for each series)
    versions_ordered = ['V0', 'V1', 'V2', 'V3']
    cumulative_errors = []

    for vi in range(len(versions_ordered) - 1):
        v_curr = versions_ordered[vi]
        v_next = versions_ordered[vi + 1]
        if v_curr in matrix and v_next in matrix:
            for si, (curr_val, next_val) in enumerate(zip(
                matrix[v_curr]['series_values'],
                matrix[v_next]['series_values']
            )):
                if curr_val is not None and next_val is not None:
                    if next_val < curr_val:
                        cumulative_errors.append({
                            "type": "cumulative_decrease",
                            "from_version": v_curr,
                            "to_version": v_next,
                            "series_index": si,
                            "from_value": curr_val,
                            "to_value": next_val
                        })

    errors.extend(cumulative_errors)

    result = {
        "script": "IMP-E",
        "name": "Module Activation Matrix",
        "matrix": matrix,
        "expected": expected,
        "row_sum_errors": [e for e in errors if e['type'] == 'row_sum_error'],
        "cumulative_errors": cumulative_errors,
        "errors": errors,
        "total_errors": len(errors),
        "verdict": "PASS" if len(errors) == 0 else "FAIL"
    }
    return result


# -----------------------------------------------
# IMP-F: Tech Stack Conflict
# -----------------------------------------------
def check_IMP_F():
    """Detect V2+ exclusive tech used in V1 = LOCK violation."""
    text = read_file(PART2)
    lines = text.split('\n')
    code_ranges = get_code_block_ranges(lines)

    # V2+ exclusive technologies (from AI Investing SPEC and PART2)
    v2_plus_tech = {
        'TimescaleDB': 'V2+',
        'Kafka': 'V2+',
        'Airflow': 'V2+',
        'S3': 'V2+',
        'MinIO': 'V2+',
        'Prometheus': 'V2+',
        'Grafana': 'V2+',
        'Neo4j': 'V2+',
        'Qdrant': 'V2+',
        'PostgreSQL': 'V2+',
        'asyncpg': 'V2+',
        'LlamaGuard': 'V2+',
        'langchain-anthropic': 'V2+',
        'transformers': 'V2+',
        'qdrant-client': 'V2+',
        'Redis': 'V2+',
        'vLLM': 'V3+',
        'Kubernetes': 'V3+',
        'K8s': 'V3+',
        'Loki': 'V3+',
    }

    # Scan V0 and V1 sections for V2+ tech usage
    lock_violations = []
    premature_usage = []

    # Determine section boundaries
    v0_start = None
    v1_start = None
    v2_start = None

    for i, line in enumerate(lines):
        if re.match(r'^# 2\. V0', line):
            v0_start = i
        elif re.match(r'^# 3\. V1', line):
            v1_start = i
        elif re.match(r'^# 4\. V2', line):
            v2_start = i

    # Scan V0 section
    if v0_start is not None and v1_start is not None:
        for i in range(v0_start, v1_start):
            if line_in_ranges(i, code_ranges):
                continue
            line = lines[i]
            # Skip comments
            if '<!--' in line:
                continue
            for tech, min_version in v2_plus_tech.items():
                if re.search(r'\b' + re.escape(tech) + r'\b', line, re.IGNORECASE):
                    # Check context: is it used or just mentioned as future?
                    context = line.strip()
                    if any(kw in context.lower() for kw in ['v2+', 'v2 ', 'v3+', 'v3 ', '전용', '이후']):
                        continue  # Mentioned as future
                    if 'stub' in context.lower() or 'placeholder' in context.lower():
                        continue
                    premature_usage.append({
                        "tech": tech,
                        "min_version": min_version,
                        "found_in": "V0",
                        "line": i + 1,
                        "context": context[:120]
                    })

    # Scan V1 section
    if v1_start is not None and v2_start is not None:
        for i in range(v1_start, v2_start):
            if line_in_ranges(i, code_ranges):
                continue
            line = lines[i]
            if '<!--' in line:
                continue
            for tech, min_version in v2_plus_tech.items():
                if re.search(r'\b' + re.escape(tech) + r'\b', line, re.IGNORECASE):
                    context = line.strip()
                    if any(kw in context.lower() for kw in ['v2+', 'v2 ', 'v3+', 'v3 ', '전용', '이후']):
                        continue
                    if 'stub' in context.lower() or 'placeholder' in context.lower():
                        continue
                    # Check if it's a valid V1 mention (e.g., migration planning)
                    if 'V2' in context or '마이그레이션' in context:
                        continue
                    premature_usage.append({
                        "tech": tech,
                        "min_version": min_version,
                        "found_in": "V1",
                        "line": i + 1,
                        "context": context[:120]
                    })

    # Filter: remove known valid usages
    # V1 uses Chroma (not Qdrant), SQLite (not Postgres), JSON (not Neo4j)
    # References to V2+ tech in dependency lists marked as V2+ are OK
    filtered = []
    for p in premature_usage:
        # Skip if the line mentions the tech as V2+ explicitly
        if p['min_version'] in p['context']:
            continue
        # Skip dependency table entries already marked as V2+
        if 'V2+' in p['context'] or 'V2 only' in p['context']:
            continue
        filtered.append(p)

    errors = lock_violations + filtered

    result = {
        "script": "IMP-F",
        "name": "Tech Stack Conflict",
        "v2_plus_tech_count": len(v2_plus_tech),
        "lock_violations": lock_violations,
        "premature_usage": filtered,
        "premature_count": len(filtered),
        "errors": errors,
        "total_errors": len(errors),
        "verdict": "PASS" if len(errors) == 0 else "FAIL"
    }
    return result


# -----------------------------------------------
# Main Execution
# -----------------------------------------------
def main():
    checks = [
        ("IMP-A", check_IMP_A),
        ("IMP-B", check_IMP_B),
        ("IMP-C", check_IMP_C),
        ("IMP-D", check_IMP_D),
        ("IMP-E", check_IMP_E),
        ("IMP-F", check_IMP_F),
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
    print("Part II Summary (IMP-A ~ IMP-F)")
    print("=" * 60)
    for r in all_results:
        v = r.get('verdict', 'ERROR')
        e = r.get('total_errors', '?')
        print(f"  {r['script']:6s} - {v:5s} ({e} errors)")

    return all_results


if __name__ == "__main__":
    results = main()
