#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VAMOS v10 Phase 1 M-2 Agent: V1 Feature -> PART2 Mapping Verification
"""
import json
import re
import os
from collections import Counter, defaultdict

# === Configuration ===
REGISTRY_PATH = "D:/VAMOS/04. 구현단계/v10_results/phase0-f/v10_feature_registry_final.json"
PART2_PATH = "D:/VAMOS/docs/guides/VAMOS_구현가이드_PART2_구현단계.md"
TERM_MAP_PATH = "D:/VAMOS/04. 구현단계/v10_results/phase0-b/v10_layer1_claude_features.json"
OUTPUT_DIR = "D:/VAMOS/04. 구현단계/v10_results/phase1/"

# PART2 section line ranges
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

V1_PHASE_SECTIONS = ["V1_Phase1", "V1_Phase2", "V1_Phase3",
                      "V1_Phase4", "V1_Phase5", "V1_Phase6"]
S6_SECTIONS = [k for k in SECTIONS if k.startswith("S6")]


def load_data():
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        reg_data = json.load(f)
    features = reg_data if isinstance(reg_data, list) else reg_data.get('features', [])

    with open(PART2_PATH, 'r', encoding='utf-8') as f:
        part2_lines = f.readlines()

    with open(TERM_MAP_PATH, 'r', encoding='utf-8') as f:
        term_data = json.load(f)
    term_map = term_data.get('terminology_mapping', [])

    return features, part2_lines, term_map


def get_section_for_line(line_num):
    for sec_name, (start, end) in SECTIONS.items():
        if start <= line_num <= end:
            return sec_name
    return "OTHER"


def build_search_terms(feature, term_map):
    terms = []
    fname = feature.get('feature_name', '') or ''
    if fname:
        terms.append(fname)
        words = re.findall(r'[A-Za-z가-힣][A-Za-z가-힣0-9_-]{2,}', fname)
        terms.extend(words)

    mid = feature.get('module_id', '') or ''
    if mid:
        terms.append(mid)
        m = re.match(r'([A-Za-z])-(\d+)', mid)
        if m:
            terms.append(f"{m.group(1)}-{m.group(2)}")
            terms.append(f"{m.group(1)}-{int(m.group(2)):02d}")
            # Also try lowercase/uppercase variants
            terms.append(f"{m.group(1).lower()}{m.group(2):>02}")

    tech = feature.get('tech_keywords', []) or []
    if tech:
        terms.extend([t for t in tech if t])

    src = feature.get('source_section', '') or ''
    if src:
        refs = re.findall(r'D2\.\d+-\d+|PHASE_B\d+|CLAUDE\.md', src)
        terms.extend(refs)

    # terminology mapping
    for tm in term_map:
        ct = tm.get('claude_md_term', '') or ''
        pt = tm.get('part2_term', '') or ''
        if ct and len(ct) > 3 and ct.lower() in fname.lower():
            if pt:
                for p in pt.split(' / '):
                    p = p.strip()
                    if len(p) > 2:
                        terms.append(p)

    seen = set()
    unique = []
    for t in terms:
        t = t.strip()
        if t and t.lower() not in seen and len(t) > 1:
            seen.add(t.lower())
            unique.append(t)
    return unique


def search_in_part2(terms, part2_lines, min_term_len=3):
    matches = []
    for term in terms:
        if len(term) < min_term_len:
            continue
        try:
            pattern = re.escape(term)
            for i, line in enumerate(part2_lines):
                if re.search(pattern, line, re.IGNORECASE):
                    ln = i + 1
                    sec = get_section_for_line(ln)
                    matches.append({
                        'line': ln,
                        'section': sec,
                        'term': term,
                        'text': line.strip()[:150]
                    })
        except re.error:
            continue
    return matches


def classify(matches, feature):
    if not matches:
        return "MISSING", None, None, []

    sec_groups = defaultdict(list)
    for m in matches:
        sec_groups[m['section']].append(m)

    # V1 Phase matches
    v1_matches = []
    v1_phases = set()
    for sec in V1_PHASE_SECTIONS:
        if sec in sec_groups:
            v1_matches.extend(sec_groups[sec])
            v1_phases.add(sec)

    # S6 matches
    s6_matches = []
    for sec in S6_SECTIONS:
        if sec in sec_groups:
            s6_matches.extend(sec_groups[sec])

    if len(v1_phases) > 1:
        best = v1_matches[0]
        return "SPREAD", sorted(v1_phases), best['line'], v1_matches
    elif len(v1_phases) == 1:
        best = v1_matches[0]
        return "MATCHED", list(v1_phases)[0], best['line'], v1_matches
    elif s6_matches:
        best = s6_matches[0]
        return "PARTIAL", best['section'], best['line'], s6_matches
    else:
        return "MISSING", None, None, matches


def severity_for(feature):
    cat = feature.get('category', '')
    is_lock = feature.get('is_lock', False)
    mid = feature.get('module_id', '') or ''

    if is_lock:
        return "BLOCKER"
    if mid and re.match(r'[IEA]-\d+', mid):
        return "BLOCKER"
    if cat in ('FT-FUNC', 'FT-SEC', 'FT-API'):
        return "HIGH"
    if cat in ('FT-SCHEMA', 'FT-CFG', 'FT-INFRA', 'FT-MOD'):
        return "MEDIUM"
    return "LOW"


def is_na(feature):
    notes = (feature.get('notes', '') or '').lower()
    fname = (feature.get('feature_name', '') or '').lower()
    for kw in ['superseded', 'deprecated', 'obsolete']:
        if kw in notes or kw in fname:
            return True
    return False


def main():
    print("Loading data...")
    features, part2_lines, term_map = load_data()

    v1_all = [f for f in features if 'V1' in str(f.get('version_scope', ''))]
    primary = [f for f in v1_all if str(f.get('version_scope', '')).startswith('V1')]
    crosscheck = [f for f in v1_all if not str(f.get('version_scope', '')).startswith('V1')]

    print(f"Total V1 features: {len(v1_all)}")
    print(f"  Primary (V1-first): {len(primary)}")
    print(f"  Cross-check: {len(crosscheck)}")

    results = []
    stats = Counter()
    missing_sev = defaultdict(list)

    for idx, feat in enumerate(v1_all):
        if idx % 500 == 0:
            print(f"  Processing {idx}/{len(v1_all)}...")

        fid = feat.get('feature_id', '')
        fname = feat.get('feature_name', '')
        vs = feat.get('version_scope', '')
        is_primary = vs.startswith('V1')

        if is_na(feat):
            results.append({
                'feature_id': fid,
                'feature_name': fname,
                'version_scope': vs,
                'category': feat.get('category', ''),
                'module_id': feat.get('module_id', ''),
                'mapping_role': 'PRIMARY' if is_primary else 'CROSS_CHECK',
                'verdict': 'NOT_APPLICABLE',
                'part2_phase': None,
                'part2_line': None,
                'severity': None,
                'evidence': 'SUPERSEDED/DEPRECATED',
                'match_count': 0,
            })
            stats['NOT_APPLICABLE'] += 1
            continue

        terms = build_search_terms(feat, term_map)
        matches = search_in_part2(terms, part2_lines)

        # De-noise: remove matches from very common short terms
        term_counts = Counter(m['term'] for m in matches)
        noisy_terms = {t for t, c in term_counts.items() if c > 50 and len(t) < 6}
        filtered = [m for m in matches if m['term'] not in noisy_terms]
        if not filtered:
            filtered = matches  # fallback

        verdict, phase, line, details = classify(filtered, feat)

        sev = None
        if verdict == "MISSING":
            sev = severity_for(feat)
            missing_sev[sev].append({
                'feature_id': fid,
                'feature_name': fname,
                'version_scope': vs,
                'category': feat.get('category', ''),
                'module_id': feat.get('module_id', ''),
                'source_section': feat.get('source_section', ''),
            })

        evidence = []
        seen_lines = set()
        for d in (details or [])[:5]:
            if d['line'] not in seen_lines:
                evidence.append(f"L{d['line']}({d['section']}): [{d['term']}]")
                seen_lines.add(d['line'])

        results.append({
            'feature_id': fid,
            'feature_name': fname,
            'version_scope': vs,
            'category': feat.get('category', ''),
            'module_id': feat.get('module_id', ''),
            'source_section': feat.get('source_section', ''),
            'mapping_role': 'PRIMARY' if is_primary else 'CROSS_CHECK',
            'verdict': verdict,
            'part2_phase': phase,
            'part2_line': line,
            'severity': sev,
            'evidence': '; '.join(evidence) if evidence else None,
            'match_count': len(filtered),
        })
        stats[verdict] += 1

    # === Print summary ===
    print(f"\n{'='*60}")
    print(f"M-2 MAPPING VERIFICATION RESULTS")
    print(f"{'='*60}")
    print(f"Total V1 features: {len(v1_all)}")
    print(f"  Primary: {len(primary)} | Cross-check: {len(crosscheck)}")
    print(f"\nVerdict Distribution:")
    for v in ['MATCHED', 'SPREAD', 'PARTIAL', 'MISSING', 'NOT_APPLICABLE']:
        print(f"  {v}: {stats.get(v, 0)}")

    print(f"\nMISSING by Severity:")
    for sev in ['BLOCKER', 'HIGH', 'MEDIUM', 'LOW']:
        print(f"  {sev}: {len(missing_sev.get(sev, []))}")

    # Print BLOCKER items
    blockers = missing_sev.get('BLOCKER', [])
    if blockers:
        print(f"\n--- BLOCKER MISSING Items ({len(blockers)}) ---")
        for b in blockers[:30]:
            print(f"  {b['feature_id']}: {b['feature_name']} [{b['module_id']}] ({b['category']})")

    # === Save outputs ===
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    output = {
        'meta': {
            'agent': 'M-2',
            'scope': 'V1 features -> PART2 mapping',
            'total_features': len(v1_all),
            'primary_count': len(primary),
            'crosscheck_count': len(crosscheck),
        },
        'statistics': dict(stats),
        'missing_severity': {s: len(missing_sev.get(s, [])) for s in ['BLOCKER', 'HIGH', 'MEDIUM', 'LOW']},
        'results': results,
    }

    out_path = os.path.join(OUTPUT_DIR, 'v10_m2_mapping_result.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\nSaved: {out_path}")

    # Save MISSING items
    missing_out = {'meta': {'agent': 'M-2'}, 'by_severity': {}}
    for sev in ['BLOCKER', 'HIGH', 'MEDIUM', 'LOW']:
        missing_out['by_severity'][sev] = missing_sev.get(sev, [])

    miss_path = os.path.join(OUTPUT_DIR, 'v10_m2_missing_items.json')
    with open(miss_path, 'w', encoding='utf-8') as f:
        json.dump(missing_out, f, ensure_ascii=False, indent=2)
    print(f"Saved: {miss_path}")


if __name__ == '__main__':
    main()