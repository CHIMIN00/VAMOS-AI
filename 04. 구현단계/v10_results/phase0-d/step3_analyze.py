import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('v10_layer1_layer2_delta.json','r',encoding='utf-8') as f:
    d = json.load(f)

s1 = d['step1_layer1_only']

l2_dict = {}
l2_files = [f for f in os.listdir('../phase0-c') if f.endswith('.json')]
for fname in l2_files:
    with open(f'../phase0-c/{fname}','r',encoding='utf-8') as f2:
        data = json.load(f2)
    feats = data.get('features', data.get('data', []))
    if isinstance(feats, list):
        for feat in feats:
            fid = feat.get('feature_id','')
            if fid:
                l2_dict[fid] = feat
                l2_dict[fid]['_src_file'] = fname

mismatches = []
for m in s1['matched'] + s1['partial_matches']:
    l1_id = m['feature_id']
    l2_id = m.get('best_match_l2_id','')
    l1_ver = m.get('version_scope','')
    if l2_id in l2_dict:
        l2_ver = l2_dict[l2_id].get('version_scope','')
        if l1_ver != l2_ver:
            mismatches.append({
                'l1_id': l1_id, 'l2_id': l2_id,
                'l1_ver': l1_ver, 'l2_ver': l2_ver,
                'l1_name': m['feature_name'],
                'l2_name': l2_dict[l2_id].get('feature_name',''),
                'score': m.get('best_match_score',0),
                'l2_src': l2_dict[l2_id].get('_src_file',''),
            })

print(f"Total mismatches: {len(mismatches)}\n")
for i, mm in enumerate(mismatches):
    print(f"{i+1:3d}. {mm['l1_id']:12s} L1=({mm['l1_ver']:20s}) vs {mm['l2_id']:12s} L2=({mm['l2_ver']:20s}) score={mm['score']:.3f}")
    print(f"     L1: {mm['l1_name'][:70]}")
    print(f"     L2: {mm['l2_name'][:70]} [{mm['l2_src']}]")
    print()

# Also find V_UNKNOWN items
print("=" * 80)
print("V_UNKNOWN items in L2:")
for fid, feat in l2_dict.items():
    vs = feat.get('version_scope','')
    if 'UNKNOWN' in vs.upper():
        print(f"  {fid}: {feat.get('feature_name','')[:60]} | version={vs} | src={feat.get('_src_file','')}")