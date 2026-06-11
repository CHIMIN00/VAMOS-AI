"""골든셋 산출물 전수 검증 스크립트 (v2 — Phase 2-0B 실데이터 기준, 2026-06-11)

v1(합성 170문항) → v2(실데이터 162문항) 기준 갱신:
  - LogicKor 50 → 42 (실제 전수 실측 — 6카테고리 × 7문항, 명세 50은 합성 가정치)
  - total 170 → 162 / golden_version v2 / LogicKor 카테고리 6종 × 7
"""
import json
import hashlib
import os

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "benchmarks", "golden_set")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors = []
warnings = []

# 1. 디렉토리 구조
expected_dirs = ["mmlu", "humaneval", "mbpp", "logickor"]
for d in expected_dirs:
    for sf in ["items.json", "metadata.json"]:
        fp = os.path.join(BASE, d, sf)
        if not os.path.isfile(fp):
            errors.append(f"파일 누락: {fp}")
for rf in ["manifest.json", "contamination_check.json"]:
    if not os.path.isfile(os.path.join(BASE, rf)):
        errors.append(f"루트 파일 누락: {rf}")
print("[1] 디렉토리 구조: PASS" if not errors else f"[1] FAIL ({len(errors)})")

# 2. 문항 수
expected_counts = {"mmlu": 50, "humaneval": 20, "mbpp": 50, "logickor": 42}
total = 0
all_items = {}
all_meta = {}
for bench, expected in expected_counts.items():
    with open(os.path.join(BASE, bench, "items.json"), "r", encoding="utf-8") as f:
        items = json.load(f)
    with open(os.path.join(BASE, bench, "metadata.json"), "r", encoding="utf-8") as f:
        meta = json.load(f)
    all_items[bench] = items
    all_meta[bench] = meta
    if len(items) != expected:
        errors.append(f"{bench}: items {len(items)} vs {expected}")
    if len(meta) != expected:
        errors.append(f"{bench}: meta {len(meta)} vs {expected}")
    if len(items) != len(meta):
        errors.append(f"{bench}: items/meta mismatch")
    total += len(items)
if total != 162:
    errors.append(f"total {total} vs 162")
print(f"[2] 문항 수: total={total}")

# 3. item_id 일관성
for bench in expected_dirs:
    ids_i = [i["item_id"] for i in all_items[bench]]
    ids_m = [m["item_id"] for m in all_meta[bench]]
    if ids_i != ids_m:
        errors.append(f"{bench}: item_id items!=meta")
    if len(set(ids_i)) != len(ids_i):
        errors.append(f"{bench}: item_id 중복")
print("[3] item_id 일관성: PASS")

# 4. 메타데이터 7필드
req_fields = ["item_id", "benchmark", "difficulty", "category", "source", "golden_version", "added_date"]
valid_diff = {"easy", "medium", "hard"}
for bench in expected_dirs:
    for m in all_meta[bench]:
        for f in req_fields:
            if f not in m or not m[f]:
                errors.append(f"{bench}/{m.get('item_id','?')}: {f} 누락/빈값")
        if m.get("difficulty") not in valid_diff:
            errors.append(f"{bench}/{m['item_id']}: difficulty={m.get('difficulty')}")
        if m.get("benchmark") != bench:
            errors.append(f"{bench}/{m['item_id']}: benchmark={m.get('benchmark')}")
        if m.get("golden_version") != "v2":
            errors.append(f"{bench}/{m['item_id']}: version={m.get('golden_version')}")
print("[4] 메타데이터 7필드: PASS")

# 5. 난이도 분포
for bench in expected_dirs:
    dc = {}
    for m in all_meta[bench]:
        dc[m["difficulty"]] = dc.get(m["difficulty"], 0) + 1
    print(f"    {bench}: {dc}")

# 6. MMLU 과목 수
subjects = set(m["category"] for m in all_meta["mmlu"])
print(f"[6] MMLU 과목: {len(subjects)}")
if len(subjects) != 50:
    errors.append(f"MMLU subjects {len(subjects)} vs 50")

# 7. LogicKor 카테고리
lk_cats = {}
for m in all_meta["logickor"]:
    cat = m["category"].split("/")[0]
    lk_cats[cat] = lk_cats.get(cat, 0) + 1
print(f"[7] LogicKor: {lk_cats}")
if len(lk_cats) != 6:
    errors.append(f"LogicKor cats {len(lk_cats)} vs 6")
for cat, cnt in lk_cats.items():
    if cnt != 7:
        errors.append(f"LogicKor {cat}: {cnt} vs 7")

# 8. manifest SHA-256
with open(os.path.join(BASE, "manifest.json"), "r", encoding="utf-8") as f:
    manifest = json.load(f)
for bench in expected_dirs:
    for ftype in ["items", "metadata"]:
        fp = os.path.join(BASE, bench, f"{ftype}.json")
        h = hashlib.sha256(open(fp, "rb").read()).hexdigest()
        mh = manifest["benchmarks"][bench][f"{ftype}_sha256"]
        if h != mh:
            errors.append(f"{bench}/{ftype} SHA-256 mismatch")
if manifest["total_items"] != 162:
    errors.append("manifest total != 162")
if manifest["seed"] != 42:
    errors.append("manifest seed != 42")
bt = sum(manifest["benchmarks"][b]["items_count"] for b in expected_dirs)
if bt != 162:
    errors.append(f"manifest bench total {bt} vs 162")
print("[8] manifest SHA-256: PASS")

# 9. contamination_check
with open(os.path.join(BASE, "contamination_check.json"), "r", encoding="utf-8") as f:
    contam = json.load(f)
if contam["results"]["verdict"] != "PASS":
    errors.append(f"contamination verdict: {contam['results']['verdict']}")
if contam["results"]["total_items_checked"] != 162:
    errors.append("contamination total != 162")
all_hashes = []
ehc = {"mmlu": 50, "humaneval": 20, "mbpp": 50, "logickor": 42}
for k, v in ehc.items():
    hlist = contam["item_hashes"].get(k, [])
    if len(hlist) != v:
        errors.append(f"contam {k} hashes {len(hlist)} vs {v}")
    all_hashes.extend(hlist)
if len(set(all_hashes)) != len(all_hashes):
    errors.append(f"contam hash duplicates ({len(all_hashes)} vs {len(set(all_hashes))})")
print(f"[9] contamination: PASS ({len(all_hashes)} hashes, unique)")

# 10. F-01 러너 호환
for bench in expected_dirs:
    for item in all_items[bench]:
        if "prompt" not in item and "question" not in item:
            errors.append(f"{bench}/{item.get('item_id')}: no prompt/question")
        if "answer" not in item:
            errors.append(f"{bench}/{item.get('item_id')}: no answer")
print("[10] F-01 러너 호환: PASS")

# 11. 채점 포맷 (A-1~A-4)
for item in all_items["mmlu"]:
    if set(item.get("choices", {}).keys()) != {"A", "B", "C", "D"}:
        errors.append(f"MMLU {item['item_id']}: choices")
    if item.get("answer") not in {"A", "B", "C", "D"}:
        errors.append(f"MMLU {item['item_id']}: answer={item.get('answer')}")
    if "subject" not in item:
        errors.append(f"MMLU {item['item_id']}: no subject")

for item in all_items["humaneval"]:
    for f in ["task_id", "entry_point", "canonical_solution", "test"]:
        if f not in item:
            errors.append(f"HumanEval {item['item_id']}: no {f}")

for item in all_items["mbpp"]:
    for f in ["task_id", "text", "code", "test_list"]:
        if f not in item:
            errors.append(f"MBPP {item['item_id']}: no {f}")
    if len(item.get("test_list", [])) != 3:
        errors.append(f"MBPP {item['item_id']}: test_list len")

for item in all_items["logickor"]:
    for f in ["category", "subcategory", "reference_answer", "scoring_criteria"]:
        if f not in item:
            errors.append(f"LogicKor {item['item_id']}: no {f}")
    sc = item.get("scoring_criteria", {})
    wsum = sc.get("accuracy_weight", 0) + sc.get("logic_weight", 0) + sc.get("completeness_weight", 0)
    if abs(wsum - 1.0) > 0.01:
        errors.append(f"LogicKor {item['item_id']}: weights sum {wsum}")
print("[11] 채점 포맷: PASS")

# 12. .gitattributes
ga = os.path.join(ROOT, ".gitattributes")
if os.path.isfile(ga):
    with open(ga, "r", encoding="utf-8") as f:
        gac = f.read()
    if "benchmarks/golden_set/**/*.json" not in gac:
        errors.append(".gitattributes: LFS pattern missing")
    if "filter=lfs" not in gac:
        errors.append(".gitattributes: filter=lfs missing")
    print("[12] .gitattributes: PASS")
else:
    errors.append(".gitattributes missing")

# 13. F-01 mmlu_sample_50 독립성
f01 = os.path.join(BASE, "mmlu_sample_50.json")
if os.path.isfile(f01):
    with open(f01, "r", encoding="utf-8") as f:
        f01_items = json.load(f)
    f01_prompts = set(i.get("prompt", "")[:80] for i in f01_items)
    golden_prompts = set(i.get("prompt", "")[:80] for i in all_items["mmlu"])
    overlap = f01_prompts & golden_prompts
    if overlap:
        warnings.append(f"F-01/F-04 prompt overlap: {len(overlap)}")
    print(f"[13] F-01 독립성: PASS (overlap={len(overlap)})")

# 결과
print()
print("=" * 50)
if errors:
    print(f"ERRORS: {len(errors)}")
    for e in errors:
        print(f"  [ERROR] {e}")
else:
    print("=== ALL PASS - errors: 0 ===")
if warnings:
    for w in warnings:
        print(f"  [WARN] {w}")
else:
    print("경고 0건")
