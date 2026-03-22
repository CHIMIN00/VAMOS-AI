#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v12 vs v10 교차 대사 스크립트"""

import json
import sys
import re
import os

sys.stdout.reconfigure(encoding='utf-8')
os.chdir(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')

###############################################
# 1. Build v12 REAL_MISSING
###############################################
phase1_missing = {}
phase1_all = {}

for fname in ['v12_mapping_M01_v0.json', 'v12_mapping_M02_v1.json',
              'v12_mapping_M03_v2.json', 'v12_mapping_M04_v3.json']:
    fpath = os.path.join('phase1', fname)
    with open(fpath, 'r', encoding='utf-8') as fh:
        data = json.load(fh)
    for item in data.get('results', []):
        fid = item['feature_id']
        phase1_all[fid] = item
        if item.get('status') == 'MISSING':
            phase1_missing[fid] = item

print(f"Phase 1 MISSING unique: {len(phase1_missing)}")

# Load v12 Feature Registry
with open('phase0/v12_feature_registry_final.json', 'r', encoding='utf-8') as fh:
    v12_reg = {f['feature_id']: f for f in json.load(fh)['features']}

# Adversarial corrections
fp_ids = {'v12_C09a_004', 'v12_C12_103'}
partial_to_missing = {'v12_C11_151', 'v12_C13_034', 'v12_C08_047'}

real_missing = {}
for fid, item in phase1_missing.items():
    if fid not in fp_ids:
        real_missing[fid] = item

for fid in partial_to_missing:
    if fid not in real_missing:
        real_missing[fid] = phase1_all.get(fid, {'feature_id': fid})

# Enrich with registry
for fid in real_missing:
    if fid in v12_reg:
        real_missing[fid]['_reg'] = v12_reg[fid]

print(f"v12 REAL_MISSING: {len(real_missing)}")

# v12 non-MISSING
v12_matched_ids = set(phase1_all.keys()) - set(real_missing.keys())

###############################################
# 2. Load v10 consolidated_missing
###############################################
v10_path = os.path.join(BASE, 'v10_results', 'phase2', 'consolidated_missing.json')
with open(v10_path, 'r', encoding='utf-8') as fh:
    v10_cons = json.load(fh)
v10_items = v10_cons['items']
print(f"v10 consolidated_missing: {len(v10_items)}")

###############################################
# 3. Load v10 integrated result
###############################################
v10_integ_path = os.path.join(BASE, 'v10_results', 'phase2', 'v10_step2_integrated_result.json')
with open(v10_integ_path, 'r', encoding='utf-8') as fh:
    v10_integ = json.load(fh)
v10_integ_by_id = {item['feature_id']: item for item in v10_integ['items']}
print(f"v10 integrated result: {len(v10_integ_by_id)}")

###############################################
# 4. Content-based matching helpers
###############################################
def normalize(text):
    if not text:
        return ''
    t = text.lower().strip()
    t = re.sub(r'[_\-/()]', ' ', t)
    t = re.sub(r'\s+', ' ', t)
    return t

def get_keywords(text):
    if not text:
        return set()
    t = normalize(text)
    words = set(re.findall(r'[a-z]{3,}|[가-힣]{2,}', t))
    stop = {'the', 'and', 'for', 'with', 'from', 'this', 'that',
            '구현', '시스템', '모듈', '기능', '관리', '처리', '데이터', '자동'}
    return words - stop

# Prepare v10 items
v10_match_data = []
for item in v10_items:
    fid = item['feature_id']
    fname = item.get('feature_name', '')
    integ = v10_integ_by_id.get(fid, {})
    classification = integ.get('final_classification', 'UNKNOWN')
    if classification == 'UNKNOWN':
        # Check consolidated_missing status/action for fallback
        status = item.get('status', '')
        if status == 'RESOLVED':
            classification = 'RESOLVED'
    v10_match_data.append({
        'feature_id': fid,
        'feature_name': fname,
        'classification': classification,
        'severity': item.get('severity', ''),
        'version_scope': item.get('version_scope', ''),
        'keywords': get_keywords(fname),
        'norm_name': normalize(fname),
        'action': item.get('action', ''),
    })

###############################################
# 5. Match v12 REAL_MISSING against v10
###############################################
matches = []
v12_unmatched = []

for fid in sorted(real_missing.keys()):
    item = real_missing[fid]
    reg = item.get('_reg', v12_reg.get(fid, {}))
    v12_name = reg.get('feature_name', item.get('feature_name', ''))
    v12_desc = reg.get('feature_description', '')
    v12_source = reg.get('source_text', '')

    v12_norm = normalize(v12_name)
    v12_kw = get_keywords(v12_name) | get_keywords(v12_desc) | get_keywords(v12_source)

    best_match = None
    best_score = 0

    for v10_item in v10_match_data:
        score = 0

        # Exact normalized name match
        if v12_norm and v10_item['norm_name'] and v12_norm == v10_item['norm_name']:
            score = 100

        # Strong substring match
        elif len(v12_norm) > 8 and v12_norm in v10_item['norm_name']:
            score = 85
        elif len(v10_item['norm_name']) > 8 and v10_item['norm_name'] in v12_norm:
            score = 80

        # Shorter substring
        elif len(v12_norm) > 5 and v12_norm in v10_item['norm_name']:
            score = 70
        elif len(v10_item['norm_name']) > 5 and v10_item['norm_name'] in v12_norm:
            score = 65

        # Keyword overlap
        elif v12_kw and v10_item['keywords']:
            overlap = v12_kw & v10_item['keywords']
            union_size = len(v12_kw | v10_item['keywords'])
            if len(overlap) >= 4:
                score = min(60, len(overlap) / union_size * 80)
            elif len(overlap) >= 3:
                score = min(50, len(overlap) / union_size * 70)
            elif len(overlap) >= 2 and len(v12_kw) <= 4 and len(v10_item['keywords']) <= 4:
                score = min(40, len(overlap) / union_size * 60)

        if score > best_score:
            best_score = score
            best_match = v10_item

    v12_sev = item.get('severity', '')
    if not v12_sev:
        v12_sev = reg.get('priority', '')

    if best_match and best_score >= 30:
        matches.append({
            'v12_id': fid,
            'v12_name': v12_name,
            'v12_severity': v12_sev,
            'v10_id': best_match['feature_id'],
            'v10_name': best_match['feature_name'],
            'v10_classification': best_match['classification'],
            'v10_severity': best_match['severity'],
            'match_score': round(best_score, 1),
        })
    else:
        v12_unmatched.append({
            'v12_id': fid,
            'v12_name': v12_name,
            'v12_severity': v12_sev,
        })

print(f"\nMatched v12->v10: {len(matches)}")
print(f"Unmatched v12 (new): {len(v12_unmatched)}")

# Classify matches into categories
both_missing = []    # v12 MISSING + v10 TRUE_MISSING
v12_only = []        # v12 MISSING + v10 non-TRUE_MISSING
for m in matches:
    if m['v10_classification'] == 'TRUE_MISSING':
        both_missing.append(m)
    else:
        v12_only.append(m)

print(f"Both MISSING: {len(both_missing)}")
print(f"v12 MISSING + v10 matched: {len(v12_only)}")
print(f"v12 MISSING + v10 absent: {len(v12_unmatched)}")

###############################################
# 6. v10 TRUE_MISSING check (v10-only missing)
###############################################
v10_true_missing = [x for x in v10_match_data if x['classification'] == 'TRUE_MISSING']
print(f"\nv10 TRUE_MISSING total: {len(v10_true_missing)}")

v10_matched_in_cross = set(m['v10_id'] for m in matches)

v10_only_missing = []
v10_resolved_in_v12 = []

for v10_item in v10_true_missing:
    if v10_item['feature_id'] in v10_matched_in_cross:
        continue  # already cross-matched to v12 MISSING

    # Check against v12 non-MISSING features
    v10_norm = v10_item['norm_name']
    v10_kw = v10_item['keywords']
    found = False

    for v12_fid in v12_matched_ids:
        v12_r = v12_reg.get(v12_fid, {})
        v12_name = v12_r.get('feature_name', '')
        v12_norm2 = normalize(v12_name)
        v12_kw2 = get_keywords(v12_name)

        match = False
        if v10_norm and v12_norm2:
            if v10_norm == v12_norm2:
                match = True
            elif len(v10_norm) > 8 and v10_norm in v12_norm2:
                match = True
            elif len(v12_norm2) > 8 and v12_norm2 in v10_norm:
                match = True

        if not match and v10_kw and v12_kw2:
            overlap = v10_kw & v12_kw2
            if len(overlap) >= 3:
                match = True

        if match:
            found = True
            v10_resolved_in_v12.append({
                'v10_id': v10_item['feature_id'],
                'v10_name': v10_item['feature_name'],
                'v12_id': v12_fid,
                'v12_name': v12_name,
            })
            break

    if not found:
        v10_only_missing.append({
            'v10_id': v10_item['feature_id'],
            'v10_name': v10_item['feature_name'],
            'v10_severity': v10_item['severity'],
        })

print(f"v10 TRUE_MISSING -> v12 MATCHED: {len(v10_resolved_in_v12)}")
print(f"v10 TRUE_MISSING only (v10 only): {len(v10_only_missing)}")

###############################################
# 7. v12 MATCHED + v10 MATCHED (harmony check)
# Not enumerable without full v10 feature registry,
# but we can estimate from v10 non-TRUE_MISSING
###############################################
v10_non_missing_matched_to_v12 = len(v12_only)  # v12 MISSING but v10 resolved
# For "v12 MATCHED + v10 MATCHED": this is the bulk of features
# We note it as the remainder

###############################################
# 8. Save results
###############################################
results = {
    'summary': {
        'v12_real_missing_total': len(real_missing),
        'v10_consolidated_total': len(v10_items),
        'v10_true_missing_total': len(v10_true_missing),
        'both_missing': len(both_missing),
        'v12_only_missing': len(v12_only),
        'v12_new_missing': len(v12_unmatched),
        'v10_only_missing': len(v10_only_missing),
        'v10_resolved_in_v12': len(v10_resolved_in_v12),
    },
    'both_missing': both_missing,
    'v12_only_missing': v12_only,
    'v12_new_missing': v12_unmatched,
    'v10_only_missing': v10_only_missing,
    'v10_resolved_in_v12': v10_resolved_in_v12,
}

with open('_crosscheck_results.json', 'w', encoding='utf-8') as fh:
    json.dump(results, fh, ensure_ascii=False, indent=2)

print("\nResults saved to _crosscheck_results.json")

###############################################
# 9. Detail printout
###############################################
print("\n=== BOTH MISSING (v12 MISSING + v10 TRUE_MISSING) ===")
for m in both_missing:
    print(f"  {m['v12_id']} ({m['v12_name']}) <-> {m['v10_id']} ({m['v10_name']}) [score={m['match_score']}]")

print("\n=== v12 MISSING + v10 MATCHED (v12 only) ===")
for m in v12_only[:30]:
    print(f"  {m['v12_id']} ({m['v12_name']}) <-> {m['v10_id']} ({m['v10_name']}) [{m['v10_classification']}] [score={m['match_score']}]")
if len(v12_only) > 30:
    print(f"  ... and {len(v12_only)-30} more")

print("\n=== v12 MISSING + v10 ABSENT (new) ===")
for m in v12_unmatched[:30]:
    print(f"  {m['v12_id']} ({m['v12_name']})")
if len(v12_unmatched) > 30:
    print(f"  ... and {len(v12_unmatched)-30} more")

print("\n=== v10 TRUE_MISSING only ===")
for m in v10_only_missing[:30]:
    print(f"  {m['v10_id']} ({m['v10_name']})")
if len(v10_only_missing) > 30:
    print(f"  ... and {len(v10_only_missing)-30} more")
