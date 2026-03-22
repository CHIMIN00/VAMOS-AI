#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
M-2 Refinement: Improve SPREAD classification by using primary match location.
For SPREAD items, identify the primary implementation phase based on:
- Where the feature is listed in a table row (|...|)
- Strongest/most specific term match
- Module ID match takes priority
"""
import json
import re
from collections import Counter, defaultdict

INPUT = "D:/VAMOS/04. 구현단계/v10_results/phase1/v10_m2_mapping_result.json"
PART2_PATH = "D:/VAMOS/docs/guides/VAMOS_구현가이드_PART2_구현단계.md"
OUTPUT = "D:/VAMOS/04. 구현단계/v10_results/phase1/v10_m2_mapping_result_v2.json"

SECTIONS = {
    "V0_S2": (54, 1382),
    "V1_Phase1": (1393, 1472),
    "V1_Phase2": (1475, 1559),
    "V1_Phase3": (1563, 1609),
    "V1_Phase4": (1612, 1652),
    "V1_Phase5": (1656, 1691),
    "V1_Phase6": (1695, 1745),
    "V2_S4": (1747, 2264),
    "V3_S5": (2266, 2846),
    "S6.1_UI": (2854, 2957),
    "S6.2_Rust": (2959, 2993),
    "S6.3_Test": (2994, 3024),
    "S6.4_CICD": (3026, 3047),
    "S6.5_Security": (3049, 3071),
    "S6.6_MCP": (3071, 3103),
    "S6.7_AgentTeams": (3103, 3167),
    "S6.8_AIInvest": (3167, 3289),
    "S6.9_SDAR": (3289, 3402),
    "S6.10_CloudLib": (3402, 3630),
    "S6.11_Event": (3630, 3706),
    "S6.12_Decision": (3695, 3706),
    "S6.13_Summary": (3706, 3722),
    "S7_Review": (3722, 3974),
}

V1_PHASES = ["V1_Phase1", "V1_Phase2", "V1_Phase3",
             "V1_Phase4", "V1_Phase5", "V1_Phase6"]


def get_section(ln):
    for name, (s, e) in SECTIONS.items():
        if s <= ln <= e:
            return name
    return "OTHER"


def is_table_row(line):
    """Check if line is a markdown table row with content"""
    return '|' in line and not line.strip().startswith('|---')


def main():
    with open(INPUT, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with open(PART2_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    results = data['results']
    stats = Counter()
    missing_sev = defaultdict(list)

    refined = []
    for r in results:
        verdict = r['verdict']
        evidence_str = r.get('evidence', '') or ''

        if verdict == 'SPREAD':
            # Parse evidence to find which lines are in table rows
            # Evidence format: "L1399(V1_Phase1): [I-1]; L1573(V1_Phase3): [I-1]"
            ev_matches = re.findall(r'L(\d+)\(([^)]+)\):\s*\[([^\]]+)\]', evidence_str)

            table_matches = []
            non_table_matches = []
            for ln_str, sec, term in ev_matches:
                ln = int(ln_str)
                if 0 < ln <= len(lines) and is_table_row(lines[ln - 1]):
                    table_matches.append((ln, sec, term))
                else:
                    non_table_matches.append((ln, sec, term))

            # Determine primary phase
            if table_matches:
                # Primary = first table row match in a V1 Phase
                v1_table = [(ln, sec, term) for ln, sec, term in table_matches if sec in V1_PHASES]
                if v1_table:
                    primary_ln, primary_sec, primary_term = v1_table[0]
                    # If table matches span multiple phases, keep as SPREAD
                    v1_table_phases = set(sec for _, sec, _ in v1_table)
                    if len(v1_table_phases) > 1:
                        r['verdict'] = 'SPREAD'
                        r['part2_phase'] = sorted(v1_table_phases)
                        r['part2_line'] = primary_ln
                        r['spread_note'] = f"Table rows in {sorted(v1_table_phases)}"
                    else:
                        r['verdict'] = 'MATCHED'
                        r['part2_phase'] = primary_sec
                        r['part2_line'] = primary_ln
                else:
                    # Table match but not in V1 phases
                    r['verdict'] = 'PARTIAL'
                    r['part2_phase'] = table_matches[0][1]
                    r['part2_line'] = table_matches[0][0]
            else:
                # No table matches - likely incidental keyword mentions
                # Downgrade from SPREAD to MATCHED (best V1 phase) or PARTIAL
                phases = r.get('part2_phase', [])
                if isinstance(phases, list) and phases:
                    # Keep as MATCHED at earliest phase
                    r['verdict'] = 'MATCHED'
                    r['part2_phase'] = phases[0]

        # Update stats
        v = r['verdict']
        stats[v] += 1
        if v == 'MISSING':
            sev = r.get('severity', 'MEDIUM')
            missing_sev[sev].append(r)

        refined.append(r)

    # === Print updated summary ===
    print("=" * 60)
    print("M-2 REFINED MAPPING RESULTS (v2)")
    print("=" * 60)
    print(f"Total: {len(refined)}")
    for v in ['MATCHED', 'SPREAD', 'PARTIAL', 'MISSING', 'NOT_APPLICABLE']:
        print(f"  {v}: {stats.get(v, 0)}")

    print(f"\nMISSING by Severity:")
    for sev in ['BLOCKER', 'HIGH', 'MEDIUM', 'LOW']:
        print(f"  {sev}: {len(missing_sev.get(sev, []))}")

    # Phase distribution for MATCHED
    matched = [r for r in refined if r['verdict'] == 'MATCHED']
    phase_dist = Counter(r['part2_phase'] for r in matched)
    print(f"\nMATCHED by phase:")
    for p, c in sorted(phase_dist.items()):
        print(f"  {p}: {c}")

    # Phase distribution for SPREAD
    spread = [r for r in refined if r['verdict'] == 'SPREAD']
    print(f"\nSPREAD items: {len(spread)} (genuinely multi-phase)")

    # PARTIAL section distribution
    partial = [r for r in refined if r['verdict'] == 'PARTIAL']
    partial_secs = Counter(
        r['part2_phase'] if isinstance(r['part2_phase'], str) else str(r['part2_phase'])
        for r in partial
    )
    print(f"\nPARTIAL by section:")
    for s, c in partial_secs.most_common(15):
        print(f"  {s}: {c}")

    # Save v2
    data['results'] = refined
    data['statistics'] = dict(stats)
    data['missing_severity'] = {s: len(missing_sev.get(s, [])) for s in ['BLOCKER', 'HIGH', 'MEDIUM', 'LOW']}
    data['meta']['version'] = 'v2_refined'

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\nSaved: {OUTPUT}")


if __name__ == '__main__':
    main()