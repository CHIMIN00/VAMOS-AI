"""
Generic CM (Cross-Match) rebuilder for v13 Enhanced Pipeline.
Reads current EA extractions and rebuilds CM JSON files by category.
Usage: python rebuild_cm.py [C1|C2|C3|C4|C5|C6|C7|C8|all]
"""
import json, sys, os, io
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE = r"D:\VAMOS\04. 구현단계\v13_results\phase0\extraction"
OUT_DIR = r"D:\VAMOS\04. 구현단계\v13_results\phase0\cross_match"

EA_MAP = {
    'v13_EA01_claude_md.json': 'EA-1',
    'v13_EA02_base_plan.json': 'EA-2',
    'v13_EA03_master_spec.json': 'EA-3',
    'v13_EA04_d20_01_02.json': 'EA-4',
    'v13_EA05_d20_03_04.json': 'EA-5',
    'v13_EA06_d20_05_06.json': 'EA-6',
    'v13_EA07_d20_07_08.json': 'EA-7',
    'v13_EA08_d21_schemas.json': 'EA-8',
    'v13_EA09_phase_b1_b3.json': 'EA-9',
    'v13_EA10_phase_b4_b7.json': 'EA-10',
    'v13_EA11_spec_4.json': 'EA-11',
    'v13_EA12_step7_spec.json': 'EA-12',
    'v13_EA13_step7_guides.json': 'EA-13',
    'v13_EA14_step7_rest.json': 'EA-14',
    'v13_EA15_etc.json': 'EA-15',
}

CM_NAMES = {
    'C1': ('v13_CM01_values.json', 'values'),
    'C3': ('v13_CM03_taxonomy.json', 'taxonomy'),
    'C4': ('v13_CM04_names.json', 'names'),
    'C6': ('v13_CM06_versions.json', 'versions'),
}


def load_all_items_by_category(category):
    """Load all items of a given category from all EA files."""
    groups = defaultdict(list)
    for fname, ea_agent in EA_MAP.items():
        fpath = os.path.join(BASE, fname)
        if not os.path.exists(fpath):
            continue
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for item in data.get('items', []):
            if item.get('category') == category:
                groups[item.get('key', '')].append({
                    'ea_agent': ea_agent,
                    'item_id': item.get('item_id', ''),
                    'source_file': item.get('source_file', ''),
                    'source_line': item.get('source_line'),
                    'source_text': item.get('source_text', ''),
                    'value': item.get('value'),
                    'value_type': item.get('value_type', ''),
                    'context': item.get('context', ''),
                })
    return groups


def compare_values(sources):
    """Determine result and severity for a set of sources with the same key."""
    if len(sources) <= 1:
        return 'SINGLE_SOURCE', 'INFO'

    values = [s['value'] for s in sources]
    str_values = [str(v).strip().lower() for v in values]
    unique_str = set(str_values)

    if len(unique_str) == 1:
        return 'CONSISTENT', 'INFO'

    # Check if differences are just type (e.g., 83 vs "83")
    try:
        num_values = [float(v) if v not in (None, '', 'null') else None for v in values]
        non_null = [v for v in num_values if v is not None]
        if len(non_null) >= 2 and len(set(non_null)) == 1:
            return 'CONSISTENT', 'INFO'
    except (ValueError, TypeError):
        pass

    # Check unique EA agents
    ea_agents = set(s['ea_agent'] for s in sources)
    unique_sources = set(s['source_file'] for s in sources)

    if len(unique_sources) > 1 and len(unique_str) > 1:
        return 'SOURCE_CONFLICT', 'CRITICAL'

    return 'INCONSISTENT', 'WARNING'


def build_cm(category):
    """Build a CM JSON for the given category."""
    if category not in CM_NAMES:
        print(f"Skipping {category} — no output mapping defined")
        return

    out_fname, desc = CM_NAMES[category]
    groups = load_all_items_by_category(category)

    comparisons = []
    cmp_id = 1
    stats = defaultdict(int)
    severity_stats = defaultdict(int)

    for key in sorted(groups.keys()):
        sources = groups[key]
        result, severity = compare_values(sources)
        stats[result] += 1
        severity_stats[severity] += 1

        # Build analysis text
        if result == 'SINGLE_SOURCE':
            analysis = f"단일 소스({sources[0]['ea_agent']})에서만 발견. 교차 비교 불가."
        elif result == 'CONSISTENT':
            vals = ', '.join(f"{s['ea_agent']}({s['value']})" for s in sources)
            analysis = f"값 일치: {vals}"
        elif result == 'INCONSISTENT':
            vals = ', '.join(f"{s['ea_agent']}({s['value']})" for s in sources)
            analysis = f"값 불일치: {vals}"
        else:  # SOURCE_CONFLICT
            vals = ', '.join(f"{s['ea_agent']}({s['value']}, {s['source_file']})" for s in sources)
            analysis = f"소스 간 충돌: {vals}"

        comparisons.append({
            'comparison_id': f'CM-{category[1]}_{cmp_id:03d}',
            'key': key,
            'result': result,
            'severity': severity,
            'sources': [{
                'ea_agent': s['ea_agent'],
                'item_id': s['item_id'],
                'source_file': s['source_file'],
                'source_line': s['source_line'],
                'source_text': s['source_text'],
                'value': s['value'],
            } for s in sources],
            'analysis': analysis,
            'recommendation': '',
        })
        cmp_id += 1

    cm = {
        'metadata': {
            'agent': f'CM-{category[1]}',
            'category': category,
            'version': 'v13',
            'created': '2026-03-21',
            'total_comparisons': len(comparisons),
            'results': {
                'CONSISTENT': stats.get('CONSISTENT', 0),
                'INCONSISTENT': stats.get('INCONSISTENT', 0),
                'SOURCE_CONFLICT': stats.get('SOURCE_CONFLICT', 0),
                'SINGLE_SOURCE': stats.get('SINGLE_SOURCE', 0),
            },
            'severity': {
                'CRITICAL': severity_stats.get('CRITICAL', 0),
                'WARNING': severity_stats.get('WARNING', 0),
                'INFO': severity_stats.get('INFO', 0),
            },
        },
        'comparisons': comparisons,
    }

    out_path = os.path.join(OUT_DIR, out_fname)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(cm, f, ensure_ascii=False, indent=2)

    print(f"Built {out_fname}: {len(comparisons)} comparisons")
    print(f"  CONSISTENT={stats['CONSISTENT']}, INCONSISTENT={stats['INCONSISTENT']}, "
          f"SOURCE_CONFLICT={stats['SOURCE_CONFLICT']}, SINGLE_SOURCE={stats['SINGLE_SOURCE']}")
    return out_path


if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else 'all'

    if target == 'all':
        categories = list(CM_NAMES.keys())
    else:
        categories = [target.upper()]

    for cat in categories:
        path = build_cm(cat)
        if path:
            print(f"  → Saved: {path}")
