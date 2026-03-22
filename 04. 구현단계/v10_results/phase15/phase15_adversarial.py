"""
VAMOS v10 Phase 1.5: 적대적 재검증 (Adversarial Re-verification)

Check A: MATCHED → 실제 MISSING? (False Positive 검사)
Check B: MISSING → 실제 MATCHED? (False Negative 검사)
Check C: PARTIAL 항목 재분류
"""

import json
import re
import random
import os
from collections import defaultdict

# ── Paths ──
BASE = "D:/VAMOS/04. 구현단계/v10_results"
PART2_PATH = "D:/VAMOS/docs/guides/VAMOS_구현가이드_PART2_구현단계.md"
REGISTRY_PATH = f"{BASE}/phase0-f/v10_feature_registry_final.json"
OUTPUT_DIR = f"{BASE}/phase15"

MAPPING_FILES = {
    "M-1": f"{BASE}/phase1/m1_v0_mapping_result.json",
    "M-2": f"{BASE}/phase1/v10_m2_mapping_result_v2.json",
    "M-3": f"{BASE}/phase1/v10_m3_mapping_result_final.json",
    "M-4": f"{BASE}/phase1/v10_m4_mapping_result.json",
}

M5A_PATH = f"{BASE}/phase1/v10_m5a_mapping_result.json"
M5B_PATH = f"{BASE}/phase1/v10_m5b_mapping_result.json"

random.seed(42)  # reproducibility

# ── Load PART2 ──
print("Loading PART2...")
with open(PART2_PATH, encoding="utf-8") as f:
    part2_lines = f.readlines()
print(f"  PART2: {len(part2_lines)} lines")

# ── Load Feature Registry ──
print("Loading Feature Registry...")
with open(REGISTRY_PATH, encoding="utf-8") as f:
    registry_data = json.load(f)
features_by_id = {}
for feat in registry_data["features"]:
    features_by_id[feat["feature_id"]] = feat
print(f"  Registry: {len(features_by_id)} features")

# ── Load all mapping results ──
print("Loading mapping results...")
all_items = []  # unified list with agent tag

def normalize_item(item, agent):
    """Normalize different JSON structures to a common format."""
    result = {
        "agent": agent,
        "feature_id": item.get("feature_id", ""),
        "feature_name": item.get("feature_name", ""),
        "version_scope": item.get("version_scope", ""),
        "category": item.get("category", ""),
        "judgment": item.get("judgment", item.get("verdict", "")),
    }
    # part2_line - various formats
    lines = item.get("part2_line", item.get("part2_lines", []))
    if lines is None:
        lines = []
    if isinstance(lines, int):
        lines = [lines]
    # Handle list of dicts like {"line": 123, "section": "...", "text": "..."}
    if isinstance(lines, list):
        normalized_lines = []
        for ln in lines:
            if isinstance(ln, dict):
                normalized_lines.append(ln.get("line", 0))
            elif isinstance(ln, int):
                normalized_lines.append(ln)
        lines = normalized_lines
    result["part2_line"] = lines

    # part2_phase
    phases = item.get("part2_phase", item.get("part2_phases", ""))
    if phases is None:
        phases = ""
    if isinstance(phases, list):
        phases = ", ".join(str(p) for p in phases)
    result["part2_phase"] = phases

    # severity (for MISSING items)
    result["severity"] = item.get("severity", "")

    # evidence/reason
    result["evidence"] = item.get("evidence", item.get("reason", item.get("match_details", "")))

    # source_section
    result["source_section"] = item.get("source_section", "")

    # module_id
    result["module_id"] = item.get("module_id", "")

    # Fill category from registry if missing
    if not result["category"] and result["feature_id"] in features_by_id:
        result["category"] = features_by_id[result["feature_id"]].get("category", "")

    return result

for agent, path in MAPPING_FILES.items():
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    # Find the results array
    items_key = None
    for k in ["mapping_results", "results", "mappings"]:
        if k in data and isinstance(data[k], list):
            items_key = k
            break

    if items_key:
        for item in data[items_key]:
            all_items.append(normalize_item(item, agent))

print(f"  Total items loaded: {len(all_items)}")

# ── Statistics ──
by_judgment = defaultdict(list)
for item in all_items:
    by_judgment[item["judgment"]].append(item)

print("\n=== Judgment Distribution ===")
for j, items in sorted(by_judgment.items(), key=lambda x: -len(x[1])):
    print(f"  {j}: {len(items)}")

# ── Helper: Search PART2 for keywords ──
def search_part2(keywords, context_window=5):
    """Search PART2 lines for keywords. Returns list of (line_num, line_text, matched_keyword)."""
    results = []
    for kw in keywords:
        if not kw or len(kw) < 2:
            continue
        pattern = re.escape(kw)
        for i, line in enumerate(part2_lines):
            if re.search(pattern, line, re.IGNORECASE):
                results.append((i + 1, line.strip(), kw))
    return results

def get_part2_context(line_num, window=3):
    """Get PART2 lines around the given line number."""
    start = max(0, line_num - 1 - window)
    end = min(len(part2_lines), line_num + window)
    return [(i + 1, part2_lines[i].strip()) for i in range(start, end)]

def extract_keywords(feature_name, feature_id=""):
    """Extract search keywords from feature name."""
    keywords = []

    # Extract English terms - both multi-word AND individual words
    eng_terms = re.findall(r'[A-Za-z][A-Za-z0-9_]+', feature_name)
    keywords.extend(eng_terms)

    # Extract module IDs like I-1, E-7, S7AE-123, I-19
    mod_ids = re.findall(r'[A-Z]-\d+|[A-Z]\d+[A-Z]*-\d+', feature_name)
    keywords.extend(mod_ids)

    # Extract Korean key terms (2+ chars)
    kor_terms = re.findall(r'[가-힣]{2,}', feature_name)
    keywords.extend(kor_terms)

    # Key technical abbreviations
    abbrevs = re.findall(r'[A-Z]{2,}', feature_name)
    for a in abbrevs:
        if len(a) >= 3 and a not in ['THE', 'AND', 'FOR', 'NOT']:
            keywords.append(a)

    # Filter out very short/common terms
    filtered = []
    common_en = {'the', 'and', 'for', 'not', 'with', 'from', 'into', 'this', 'that', 'are', 'was',
                 'has', 'its', 'all', 'new', 'get', 'set', 'run', 'use', 'add', 'max', 'min',
                 'api', 'app', 'key', 'log', 'out', 'var', 'src', 'doc', 'dev'}
    # Very common Korean words in PART2 that are not discriminating
    common_kr = {'구현', '설정', '실행', '생성', '처리', '관리', '검증', '적용', '정의', '구성',
                 '시스템', '서비스', '데이터', '모듈', '기능', '단계', '작업', '항목', '테스트',
                 '배포', '통합', '인프라', '설계', '분석', '상태', '모델', '사용', '기본',
                 '환경', '파일', '코드', '타입', '등록', '변환', '저장', '전환', '버전',
                 '결과', '로그', '보안', '수행', '완료', '확인', '추가', '삭제', '수정',
                 '업데이트', '호출', '응답', '요청', '연결', '프로세스', '컴포넌트', '인터페이스',
                 '엔진', '클라이언트', '서버', '프레임워크', '플러그인', '리소스', '이벤트'}
    for kw in keywords:
        if kw.lower() in common_en:
            continue
        if kw in common_kr:
            continue
        if len(kw) < 3:
            continue
        filtered.append(kw)

    return list(dict.fromkeys(filtered))  # deduplicate preserving order

def is_implementation_item(line_text):
    """Check if a PART2 line describes an implementation item (not just a mention)."""
    # Implementation indicators
    impl_patterns = [
        r'구현', r'생성', r'설정', r'적용', r'배포', r'통합',
        r'빌드', r'설치', r'스캐폴딩', r'코드', r'테스트',
        r'STEP|Phase|단계', r'작업\s*\d', r'Task\s*\d',
        r'^\s*[-*]\s+', r'^\s*\d+\.', r'^\|',  # list/table items
    ]
    for p in impl_patterns:
        if re.search(p, line_text):
            return True
    return False


# ══════════════════════════════════════════════════════════════
# CHECK A: False Positive (MATCHED → actually MISSING?)
# ══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("CHECK A: False Positive 검사 (MATCHED → MISSING?)")
print("="*60)

matched_items = by_judgment.get("MATCHED", [])
print(f"\nTotal MATCHED: {len(matched_items)}")

# Stratified sampling by category
by_cat = defaultdict(list)
for item in matched_items:
    cat = item["category"] or "UNKNOWN"
    by_cat[cat].append(item)

print("\nMATCHED by category:")
for cat, items in sorted(by_cat.items(), key=lambda x: -len(x[1])):
    print(f"  {cat}: {len(items)}")

# Sample: min 30, max 60, proportional to category size
total_matched = len(matched_items)
target_sample = min(60, max(30, total_matched // 20))  # ~5% but at least 30
print(f"\nTarget sample size: {target_sample}")

sampled_matched = []
# Ensure at least 1 per category, rest proportional
cats_sorted = sorted(by_cat.keys())
remaining = target_sample - len(cats_sorted)  # 1 per category first

for cat in cats_sorted:
    items = by_cat[cat]
    # At least 1 per category
    n = max(1, int(remaining * len(items) / total_matched) + 1)
    n = min(n, len(items))
    sampled = random.sample(items, n)
    sampled_matched.extend(sampled)

# Cap at target
if len(sampled_matched) > target_sample:
    sampled_matched = random.sample(sampled_matched, target_sample)

print(f"Actual sample size: {len(sampled_matched)}")

# Verify each sampled MATCHED item
false_positives = []
verified_matched = []
fp_check_details = []

for item in sampled_matched:
    fid = item["feature_id"]
    fname = item["feature_name"]
    lines = item["part2_line"]
    phase = item["part2_phase"]

    detail = {
        "feature_id": fid,
        "feature_name": fname,
        "agent": item["agent"],
        "category": item["category"],
        "claimed_part2_lines": lines,
        "claimed_phase": phase,
        "verification": "",
        "result": "",
    }

    if not lines:
        # No line reference → suspicious
        detail["verification"] = "NO_LINE_REF: MATCHED but no PART2 line reference"
        detail["result"] = "SUSPECT_FP"
        false_positives.append(detail)
    else:
        # Check actual PART2 content at claimed lines
        found_impl = False
        checked_lines_text = []

        for ln in lines[:5]:  # check up to 5 lines
            if 1 <= ln <= len(part2_lines):
                line_text = part2_lines[ln - 1].strip()
                checked_lines_text.append(f"L{ln}: {line_text[:120]}")

                # Check if the feature's keywords appear in or near this line
                keywords = extract_keywords(fname)
                context = get_part2_context(ln, window=3)
                context_text = " ".join(t for _, t in context)

                for kw in keywords[:5]:
                    if kw and len(kw) >= 2 and kw.lower() in context_text.lower():
                        found_impl = True
                        break
            else:
                checked_lines_text.append(f"L{ln}: OUT_OF_RANGE")

        detail["checked_lines"] = checked_lines_text

        if found_impl:
            detail["verification"] = "CONFIRMED: keyword found at/near claimed PART2 line"
            detail["result"] = "TRUE_POSITIVE"
            verified_matched.append(detail)
        else:
            detail["verification"] = "KEYWORD_MISMATCH: feature keywords not found near claimed lines"
            detail["result"] = "SUSPECT_FP"
            false_positives.append(detail)

    fp_check_details.append(detail)

print(f"\n  TRUE_POSITIVE (confirmed): {len(verified_matched)}")
print(f"  SUSPECT_FP (may be false positive): {len(false_positives)}")

if false_positives:
    print("\n  False Positive suspects:")
    for fp in false_positives[:10]:
        print(f"    {fp['feature_id']}: {fp['feature_name'][:60]}")
        print(f"      Reason: {fp['verification']}")


# ══════════════════════════════════════════════════════════════
# CHECK B: False Negative (MISSING → actually MATCHED?)
# ══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("CHECK B: False Negative 검사 (MISSING → MATCHED?)")
print("="*60)

missing_items = by_judgment.get("MISSING", [])
print(f"\nTotal MISSING: {len(missing_items)}")

# Severity distribution
by_sev = defaultdict(list)
for item in missing_items:
    sev = item.get("severity", "UNKNOWN") or "UNKNOWN"
    by_sev[sev].append(item)

print("\nMISSING by severity:")
for sev in ["BLOCKER", "HIGH", "MEDIUM", "LOW", "UNKNOWN"]:
    if sev in by_sev:
        print(f"  {sev}: {len(by_sev[sev])}")

# Re-search ALL missing items in PART2
false_negatives = []
real_missing = []
fn_check_details = []

# Build PART2 section map for efficient search
section_map = {}  # line_num -> section_id
current_section = ""
for i, line in enumerate(part2_lines):
    m = re.match(r'^#+\s*(§[\d.]+|STEP\s*\d|Phase\s*\d|V\d)', line)
    if m:
        current_section = m.group(1)
    section_map[i + 1] = current_section

print(f"\nRe-searching {len(missing_items)} MISSING items in PART2...")
search_count = 0
for item in missing_items:
    fid = item["feature_id"]
    fname = item["feature_name"]

    detail = {
        "feature_id": fid,
        "feature_name": fname,
        "agent": item["agent"],
        "category": item["category"],
        "severity": item.get("severity", ""),
        "original_reason": str(item.get("evidence", ""))[:200],
        "research_result": "",
        "found_lines": [],
        "verdict": "",
    }

    keywords = extract_keywords(fname, fid)

    # Also get keywords from registry if available
    if fid in features_by_id:
        reg_feat = features_by_id[fid]
        tech_kw = reg_feat.get("tech_keywords", [])
        if tech_kw:
            keywords.extend(tech_kw)

    # Search PART2 with all keywords
    all_hits = []
    matched_kws = set()

    for kw in keywords:
        if not kw or len(kw) < 2:
            continue
        hits = search_part2([kw])
        for ln, text, mkw in hits:
            # Filter: only §2~§5 (implementation phases) lines 54~3165
            if 54 <= ln <= 3165:
                all_hits.append((ln, text, mkw))
                matched_kws.add(mkw)

    # Deduplicate hits by line
    unique_hits = {}
    for ln, text, mkw in all_hits:
        if ln not in unique_hits:
            unique_hits[ln] = (text, mkw)

    # Evaluate: need SPECIFIC keywords (not common ones) co-located in same line/region
    # Check for co-location: at least 2 different keywords within 10 lines of each other
    colocated = False
    hit_lines = sorted(unique_hits.keys())
    if len(hit_lines) >= 2 and len(matched_kws) >= 2:
        # Check if any two hits with different keywords are within 10 lines
        for i in range(len(hit_lines)):
            for j in range(i + 1, len(hit_lines)):
                if abs(hit_lines[i] - hit_lines[j]) <= 10:
                    kw_i = unique_hits[hit_lines[i]][1]
                    kw_j = unique_hits[hit_lines[j]][1]
                    if kw_i != kw_j:
                        colocated = True
                        break
            if colocated:
                break

    if colocated and len(matched_kws) >= 2:
        # Strong signal: multiple specific keywords co-located
        detail["research_result"] = f"COLOCATED_MATCH: {len(matched_kws)} keywords co-located at {len(unique_hits)} lines"
        detail["found_lines"] = [
            {"line": ln, "text": text[:100], "keyword": mkw}
            for ln, (text, mkw) in sorted(unique_hits.items())[:5]
        ]
        detail["verdict"] = "FALSE_NEGATIVE"
        false_negatives.append(detail)
    elif len(matched_kws) >= 2 and len(unique_hits) >= 3:
        # Moderate signal: multiple keywords found but not co-located
        detail["research_result"] = f"DISPERSED_MATCH: {len(matched_kws)} keywords at {len(unique_hits)} lines (not co-located)"
        detail["found_lines"] = [
            {"line": ln, "text": text[:100], "keyword": mkw}
            for ln, (text, mkw) in sorted(unique_hits.items())[:5]
        ]
        detail["verdict"] = "POSSIBLE_FN"
        false_negatives.append(detail)
    elif len(matched_kws) == 1 and len(unique_hits) >= 1:
        # Weak signal: single keyword match
        detail["research_result"] = f"SINGLE_KW: 1 keyword '{list(matched_kws)[0]}' at {len(unique_hits)} lines"
        detail["found_lines"] = [
            {"line": ln, "text": text[:100], "keyword": mkw}
            for ln, (text, mkw) in sorted(unique_hits.items())[:3]
        ]
        detail["verdict"] = "WEAK_MATCH"
        # Don't add to false_negatives, keep as REAL_MISSING with note
        real_missing.append(detail)
    else:
        detail["research_result"] = f"NOT_FOUND: {len(matched_kws)} kw, {len(unique_hits)} hits in §2~§5"
        detail["verdict"] = "REAL_MISSING"
        real_missing.append(detail)

    fn_check_details.append(detail)
    search_count += 1
    if search_count % 200 == 0:
        print(f"  ... searched {search_count}/{len(missing_items)}")

print(f"\n  FALSE_NEGATIVE (found in PART2): {len([d for d in fn_check_details if d['verdict'] == 'FALSE_NEGATIVE'])}")
print(f"  POSSIBLE_FN (weak match): {len([d for d in fn_check_details if d['verdict'] == 'POSSIBLE_FN'])}")
print(f"  REAL_MISSING (confirmed): {len(real_missing)}")

# Break down FALSE_NEGATIVE by severity
fn_by_sev = defaultdict(int)
for d in fn_check_details:
    if d["verdict"] == "FALSE_NEGATIVE":
        fn_by_sev[d["severity"] or "UNKNOWN"] += 1
print("\n  FALSE_NEGATIVE by severity:")
for sev in ["BLOCKER", "HIGH", "MEDIUM", "LOW", "UNKNOWN"]:
    if sev in fn_by_sev:
        print(f"    {sev}: {fn_by_sev[sev]}")


# ══════════════════════════════════════════════════════════════
# CHECK C: PARTIAL 재분류
# ══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("CHECK C: PARTIAL 항목 재분류")
print("="*60)

partial_items = by_judgment.get("PARTIAL", [])
print(f"\nTotal PARTIAL: {len(partial_items)}")

# For PARTIAL items: check if they have §6-only presence (no Phase assignment)
partial_reclassified = []
for item in partial_items:
    fid = item["feature_id"]
    fname = item["feature_name"]
    lines = item["part2_line"]

    detail = {
        "feature_id": fid,
        "feature_name": fname,
        "agent": item["agent"],
        "category": item["category"],
        "original_lines": lines,
        "reclassification": "",
        "reason": "",
    }

    if not lines:
        # No line reference at all
        detail["reclassification"] = "→ MISSING"
        detail["reason"] = "PARTIAL with no PART2 line reference"
        partial_reclassified.append(detail)
        continue

    # Check if all lines are in §6+ (line ~2848+) rather than §2~§5 (line ~54~2847)
    in_phase = False
    in_ref_only = False

    for ln in lines:
        if isinstance(ln, int):
            if 54 <= ln <= 2847:
                in_phase = True
            elif ln >= 2848:
                in_ref_only = True

    if in_ref_only and not in_phase:
        detail["reclassification"] = "→ MISSING(HIGH)"
        detail["reason"] = "§6 only, no Phase(§2~§5) assignment"
        partial_reclassified.append(detail)
    elif in_phase:
        detail["reclassification"] = "KEEP_PARTIAL"
        detail["reason"] = "Has Phase assignment, genuinely partial"
    else:
        detail["reclassification"] = "KEEP_PARTIAL"
        detail["reason"] = "Line range unclear"

reclassed_to_missing = [d for d in partial_reclassified if "MISSING" in d["reclassification"]]
print(f"\n  Reclassified to MISSING: {len(reclassed_to_missing)}")
print(f"  Kept as PARTIAL: {len(partial_items) - len(reclassed_to_missing)}")


# ══════════════════════════════════════════════════════════════
# FINAL STATISTICS
# ══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("FINAL STATISTICS")
print("="*60)

total_fp = len(false_positives)
total_fn_strong = len([d for d in fn_check_details if d["verdict"] == "FALSE_NEGATIVE"])
total_fn_weak = len([d for d in fn_check_details if d["verdict"] == "POSSIBLE_FN"])
total_real_missing = len(real_missing)
total_partial_to_missing = len(reclassed_to_missing)

fp_rate = total_fp / len(sampled_matched) * 100 if sampled_matched else 0
fn_rate = total_fn_strong / len(missing_items) * 100 if missing_items else 0

print(f"\nCheck A (FP): {total_fp}/{len(sampled_matched)} sampled MATCHED are suspect ({fp_rate:.1f}%)")
print(f"  Extrapolated FP in all MATCHED: ~{int(fp_rate * len(matched_items) / 100)} / {len(matched_items)}")
print(f"\nCheck B (FN): {total_fn_strong} definite + {total_fn_weak} possible FN out of {len(missing_items)} MISSING ({fn_rate:.1f}% definite)")
print(f"  REAL_MISSING confirmed: {total_real_missing}")
print(f"\nCheck C (PARTIAL): {total_partial_to_missing} reclassified to MISSING")
print(f"\nAdjusted totals:")
print(f"  MATCHED (after FP removal): ~{len(matched_items) - int(fp_rate * len(matched_items) / 100)}")
print(f"  MISSING (after FN removal + PARTIAL reclass): ~{total_real_missing + total_partial_to_missing}")
print(f"  FALSE_NEGATIVE recovered: {total_fn_strong}")


# ══════════════════════════════════════════════════════════════
# SAVE RESULTS
# ══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("Saving results...")
print("="*60)

output = {
    "_meta": {
        "phase": "Phase 1.5",
        "purpose": "적대적 재검증 (Adversarial Re-verification)",
        "generated_date": "2026-03-09",
        "part2_version": "v21.0.0",
        "feature_registry_version": "v10.1.0",
        "random_seed": 42,
    },
    "check_a_false_positive": {
        "total_matched": len(matched_items),
        "sample_size": len(sampled_matched),
        "true_positive_confirmed": len(verified_matched),
        "suspect_false_positive": total_fp,
        "fp_rate_percent": round(fp_rate, 1),
        "extrapolated_fp_count": int(fp_rate * len(matched_items) / 100),
        "details": fp_check_details,
    },
    "check_b_false_negative": {
        "total_missing": len(missing_items),
        "false_negative_definite": total_fn_strong,
        "false_negative_possible": total_fn_weak,
        "real_missing_confirmed": total_real_missing,
        "fn_rate_percent": round(fn_rate, 1),
        "blocker_status": {
            "total_blocker": len(by_sev.get("BLOCKER", [])),
            "blocker_fn": fn_by_sev.get("BLOCKER", 0),
            "blocker_real": len(by_sev.get("BLOCKER", [])) - fn_by_sev.get("BLOCKER", 0),
        },
        "real_missing_by_severity": {},
        "false_negative_list": [d for d in fn_check_details if d["verdict"] == "FALSE_NEGATIVE"],
        "possible_fn_list": [d for d in fn_check_details if d["verdict"] == "POSSIBLE_FN"],
    },
    "check_c_partial_reclass": {
        "total_partial": len(partial_items),
        "reclassified_to_missing": total_partial_to_missing,
        "kept_as_partial": len(partial_items) - total_partial_to_missing,
        "reclassified_items": reclassed_to_missing,
    },
    "final_statistics": {
        "original": {
            "MATCHED": len(matched_items),
            "SPREAD": len(by_judgment.get("SPREAD", [])),
            "PARTIAL": len(partial_items),
            "MISSING": len(missing_items),
            "NOT_APPLICABLE": len(by_judgment.get("NOT_APPLICABLE", [])),
        },
        "adjusted": {
            "MATCHED_adjusted": len(matched_items) - int(fp_rate * len(matched_items) / 100),
            "FALSE_NEGATIVE_recovered": total_fn_strong,
            "REAL_MISSING": total_real_missing,
            "PARTIAL_to_MISSING": total_partial_to_missing,
        },
        "fp_rate": round(fp_rate, 1),
        "fn_rate": round(fn_rate, 1),
        "overkill_threshold_10pct": fp_rate <= 10.0,
    },
}

# Fill real_missing by severity
rm_by_sev = defaultdict(int)
for d in real_missing:
    rm_by_sev[d["severity"] or "UNKNOWN"] += 1
output["check_b_false_negative"]["real_missing_by_severity"] = dict(rm_by_sev)

result_path = f"{OUTPUT_DIR}/v10_phase15_result.json"
with open(result_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print(f"  Saved: {result_path}")

print("\nDone!")
