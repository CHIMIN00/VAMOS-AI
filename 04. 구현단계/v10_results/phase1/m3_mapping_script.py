"""
v10 Phase 1 M-3: V2 Feature → PART2 §4 Mapping Script
Maps V2 features from Feature Registry to PART2 §4 (V2 Phase 1~3)
"""
import json
import re
import os

# Paths
REGISTRY_PATH = r"D:\VAMOS\04. 구현단계\v10_results\phase0-f\v10_feature_registry_final.json"
PART2_PATH = r"D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md"
OUTPUT_DIR = r"D:\VAMOS\04. 구현단계\v10_results\phase1"

# V2 section range in PART2
V2_SECTION_START = 1747  # # 4. V2 구현
V2_SECTION_END = 2265    # before # 5. V3 구현

# §6 system details (V2 relevant)
S6_START = 2848
S6_END = 3722

# §7 GO/NO-GO
S7_START = 3722
S7_END = 3944

def load_part2():
    """Load PART2 and index all lines."""
    with open(PART2_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return lines

def load_registry():
    """Load feature registry and filter V2."""
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    features = data.get("features", [])
    v2_features = [f for f in features if "V2" in str(f.get("version_scope", ""))]
    return v2_features

def determine_role(version_scope):
    """Determine M-3's role based on cross-version rules."""
    scope = str(version_scope)
    # M-3 is primary mapper for features where V2 is the first version in scope
    if scope == "V2" or scope == "V2,V3":
        return "PRIMARY"
    else:
        # V1,V2 / V1,V2,V3 / V0,V1,V2,V3 / V0,V1,V2 → cross-check only
        return "CROSS_CHECK"

def extract_keywords(feature):
    """Extract search keywords from a feature."""
    keywords = set()

    # 1. feature_name tokens
    name = feature.get("feature_name", "")
    # Extract English words, Korean words, module IDs
    keywords.update(re.findall(r'[A-Za-z][\w\-\.]+', name))
    # Korean multi-char words
    korean = re.findall(r'[가-힣]{2,}', name)
    keywords.update(korean)

    # 2. module_id
    mid = feature.get("module_id", "")
    if mid:
        keywords.add(mid)

    # 3. tech_keywords
    for tk in feature.get("tech_keywords", []):
        if tk:
            keywords.add(tk)

    # 4. source_section reference
    src = feature.get("source_section", "")
    if src:
        # Extract D2.0-XX refs
        refs = re.findall(r'D\d[\.\d]*-\d+', src)
        keywords.update(refs)
        # Extract §X.X refs
        section_refs = re.findall(r'§[\d\.]+', src)
        keywords.update(section_refs)

    # 5. cross_ref
    for cr in feature.get("cross_ref", []):
        if cr:
            keywords.add(cr)

    # 6. feature_id itself (e.g., D206-015)
    fid = feature.get("feature_id", "")
    if fid:
        # Extract prefix pattern like D206, S7AE etc.
        keywords.add(fid)

    # Filter too short/common
    keywords = {k for k in keywords if len(k) >= 2}
    return keywords

def search_in_lines(lines, keyword, section_ranges=None):
    """Search for keyword in specified line ranges. Returns list of (line_no, line_text)."""
    matches = []
    kw_lower = keyword.lower()

    for i, line in enumerate(lines):
        line_no = i + 1  # 1-based
        if section_ranges:
            in_range = any(start <= line_no <= end for start, end in section_ranges)
            if not in_range:
                continue
        if kw_lower in line.lower():
            matches.append((line_no, line.strip()))
    return matches

def classify_section(line_no):
    """Classify which PART2 section a line belongs to."""
    if 1747 <= line_no <= 1754:
        return "V2-Header"
    elif 1756 <= line_no <= 1919:
        return "V2-Phase1"
    elif 1921 <= line_no <= 2104:
        return "V2-Phase2"
    elif 2106 <= line_no <= 2265:
        return "V2-Phase3"
    elif 2848 <= line_no <= 2960:
        return "§6.1-UI"
    elif 2961 <= line_no <= 2993:
        return "§6.2-Rust"
    elif 2994 <= line_no <= 3025:
        return "§6.3-Test"
    elif 3026 <= line_no <= 3048:
        return "§6.4-CICD"
    elif 3049 <= line_no <= 3070:
        return "§6.5-Security"
    elif 3071 <= line_no <= 3102:
        return "§6.6-MCP"
    elif 3103 <= line_no <= 3166:
        return "§6.7-AgentTeams"
    elif 3167 <= line_no <= 3288:
        return "§6.8-AIInvesting"
    elif 3289 <= line_no <= 3401:
        return "§6.9-SDAR"
    elif 3402 <= line_no <= 3629:
        return "§6.10-CloudLib"
    elif 3630 <= line_no <= 3694:
        return "§6.11-EventLog"
    elif 3695 <= line_no <= 3721:
        return "§6.12-OpDecision"
    elif 3722 <= line_no <= 3944:
        return "§7-GONOGO"
    elif 54 <= line_no <= 1383:
        return "§2-V0"
    elif 1384 <= line_no <= 1746:
        return "§3-V1"
    elif 2266 <= line_no <= 2847:
        return "§5-V3"
    else:
        return "OTHER"

def map_feature(feature, lines):
    """Map a single feature to PART2 sections."""
    keywords = extract_keywords(feature)
    role = determine_role(feature.get("version_scope", ""))

    # Search in V2 section (§4) first, then §6, then §7
    v2_ranges = [(V2_SECTION_START, V2_SECTION_END)]
    s6_ranges = [(S6_START, S6_END)]
    s7_ranges = [(S7_START, S7_END)]
    all_ranges = v2_ranges + s6_ranges + s7_ranges

    all_matches = {}
    best_matches_v2 = {}
    best_matches_s6 = {}
    best_matches_s7 = {}

    for kw in keywords:
        if len(kw) < 3 and not re.match(r'^[A-Z]-\d+$', kw):
            continue

        # Search V2 section
        v2_hits = search_in_lines(lines, kw, v2_ranges)
        for ln, txt in v2_hits:
            if ln not in best_matches_v2:
                best_matches_v2[ln] = {"line": ln, "text": txt, "keywords": [], "section": classify_section(ln)}
            best_matches_v2[ln]["keywords"].append(kw)

        # Search §6
        s6_hits = search_in_lines(lines, kw, s6_ranges)
        for ln, txt in s6_hits:
            if ln not in best_matches_s6:
                best_matches_s6[ln] = {"line": ln, "text": txt, "keywords": [], "section": classify_section(ln)}
            best_matches_s6[ln]["keywords"].append(kw)

        # Search §7
        s7_hits = search_in_lines(lines, kw, s7_ranges)
        for ln, txt in s7_hits:
            if ln not in best_matches_s7:
                best_matches_s7[ln] = {"line": ln, "text": txt, "keywords": [], "section": classify_section(ln)}
            best_matches_s7[ln]["keywords"].append(kw)

    # Determine verdict
    verdict = "MISSING"
    part2_phase = None
    part2_lines = []
    severity = None
    match_details = []

    if best_matches_v2:
        # Sort by keyword match count
        sorted_v2 = sorted(best_matches_v2.values(), key=lambda x: len(x["keywords"]), reverse=True)
        top = sorted_v2[0]

        # Check if it's in V2-Phase 1/2/3
        sections_found = set(m["section"] for m in sorted_v2)
        v2_phases = [s for s in sections_found if s.startswith("V2-Phase")]

        if len(v2_phases) > 1:
            verdict = "SPREAD"
            part2_phase = ", ".join(sorted(v2_phases))
            part2_lines = [m["line"] for m in sorted_v2[:5]]
        elif len(v2_phases) == 1:
            verdict = "MATCHED"
            part2_phase = v2_phases[0]
            part2_lines = [m["line"] for m in sorted_v2[:3]]
        else:
            verdict = "MATCHED"
            part2_phase = top["section"]
            part2_lines = [top["line"]]

        match_details = [{"line": m["line"], "section": m["section"], "keywords": m["keywords"][:3], "text": m["text"][:80]} for m in sorted_v2[:5]]

    elif best_matches_s6:
        # Found in §6 but not in §4
        sorted_s6 = sorted(best_matches_s6.values(), key=lambda x: len(x["keywords"]), reverse=True)
        top = sorted_s6[0]
        verdict = "PARTIAL"
        part2_phase = top["section"] + " (Phase 미배정)"
        part2_lines = [m["line"] for m in sorted_s6[:3]]
        match_details = [{"line": m["line"], "section": m["section"], "keywords": m["keywords"][:3], "text": m["text"][:80]} for m in sorted_s6[:3]]

    elif best_matches_s7:
        sorted_s7 = sorted(best_matches_s7.values(), key=lambda x: len(x["keywords"]), reverse=True)
        top = sorted_s7[0]
        verdict = "PARTIAL"
        part2_phase = top["section"] + " (Phase 미배정)"
        part2_lines = [top["line"]]
        match_details = [{"line": top["line"], "section": top["section"], "keywords": top["keywords"][:3], "text": top["text"][:80]}]

    else:
        verdict = "MISSING"
        # Determine severity
        cat = feature.get("category", "")
        notes = feature.get("notes", "")
        vs = feature.get("version_scope", "")

        if "BLOCKER" in str(notes).upper() or "priority=CRITICAL" in str(notes):
            severity = "BLOCKER"
        elif vs == "V2" and cat in ("FT-FUNC", "FT-MOD", "FT-INFRA"):
            severity = "HIGH"
        elif vs == "V2" and cat in ("FT-SEC", "FT-API"):
            severity = "HIGH"
        elif "priority=HIGH" in str(notes):
            severity = "HIGH"
        elif vs == "V2":
            severity = "MEDIUM"
        else:
            severity = "LOW"

    # Check NOT_APPLICABLE conditions
    notes_str = str(feature.get("notes", "")).upper()
    if "SUPERSEDED" in notes_str or "DEPRECATED" in notes_str or "설계 원칙" in str(feature.get("notes", "")):
        if verdict == "MISSING":
            verdict = "NOT_APPLICABLE"
            severity = None

    return {
        "feature_id": feature.get("feature_id"),
        "feature_name": feature.get("feature_name"),
        "version_scope": feature.get("version_scope"),
        "category": feature.get("category"),
        "m3_role": role,
        "verdict": verdict,
        "part2_phase": part2_phase,
        "part2_lines": part2_lines,
        "severity": severity,
        "match_details": match_details,
        "keywords_used": list(keywords)[:10],
        "source_section": feature.get("source_section"),
        "module_id": feature.get("module_id"),
        "notes": feature.get("notes")
    }


def main():
    print("Loading PART2...")
    lines = load_part2()
    print(f"PART2: {len(lines)} lines")

    print("Loading Feature Registry...")
    v2_features = load_registry()
    print(f"V2 features: {len(v2_features)}")

    # Classify by role
    primary = [f for f in v2_features if determine_role(f.get("version_scope","")) == "PRIMARY"]
    cross_check = [f for f in v2_features if determine_role(f.get("version_scope","")) == "CROSS_CHECK"]
    print(f"Primary (M-3 주 매핑): {len(primary)}")
    print(f"Cross-check (교차확인): {len(cross_check)}")

    # Map all features
    print("\nMapping features...")
    results = []
    for i, feat in enumerate(v2_features):
        result = map_feature(feat, lines)
        results.append(result)
        if (i+1) % 200 == 0:
            print(f"  Processed {i+1}/{len(v2_features)}")

    print(f"\nTotal mapped: {len(results)}")

    # Statistics
    from collections import Counter
    verdicts = Counter(r["verdict"] for r in results)
    print("\n=== Overall Verdicts ===")
    for v, c in verdicts.most_common():
        print(f"  {v}: {c}")

    # Primary only stats
    primary_results = [r for r in results if r["m3_role"] == "PRIMARY"]
    primary_verdicts = Counter(r["verdict"] for r in primary_results)
    print(f"\n=== Primary (M-3 주 매핑) Verdicts ({len(primary_results)}) ===")
    for v, c in primary_verdicts.most_common():
        print(f"  {v}: {c}")

    # Cross-check stats
    cc_results = [r for r in results if r["m3_role"] == "CROSS_CHECK"]
    cc_verdicts = Counter(r["verdict"] for r in cc_results)
    print(f"\n=== Cross-check Verdicts ({len(cc_results)}) ===")
    for v, c in cc_verdicts.most_common():
        print(f"  {v}: {c}")

    # MISSING by severity
    missing = [r for r in results if r["verdict"] == "MISSING"]
    if missing:
        sev = Counter(r["severity"] for r in missing)
        print(f"\n=== MISSING Severity ({len(missing)}) ===")
        for s, c in sev.most_common():
            print(f"  {s}: {c}")

    # MISSING BLOCKER/HIGH details
    critical_missing = [r for r in missing if r["severity"] in ("BLOCKER", "HIGH")]
    if critical_missing:
        print(f"\n=== MISSING BLOCKER/HIGH ({len(critical_missing)}) ===")
        for r in critical_missing[:30]:
            print(f"  [{r['severity']}] {r['feature_id']}: {r['feature_name'][:60]}")
            print(f"    version_scope={r['version_scope']}, category={r['category']}")

    # Save results
    output = {
        "_meta": {
            "agent": "M-3",
            "phase": "Phase 1",
            "version_filter": "V2",
            "part2_section": "§4 (V2 구현) + §6 (시스템별 상세) + §7 (GO/NO-GO)",
            "total_features": len(results),
            "primary_count": len(primary_results),
            "cross_check_count": len(cc_results)
        },
        "statistics": {
            "overall": dict(verdicts),
            "primary": dict(primary_verdicts),
            "cross_check": dict(cc_verdicts),
            "missing_severity": dict(Counter(r["severity"] for r in missing)) if missing else {}
        },
        "results": results
    }

    out_path = os.path.join(OUTPUT_DIR, "v10_m3_mapping_result.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\nSaved: {out_path}")

    # Save MISSING items separately
    missing_out = os.path.join(OUTPUT_DIR, "v10_m3_missing_items.json")
    with open(missing_out, "w", encoding="utf-8") as f:
        json.dump(missing, f, ensure_ascii=False, indent=2)
    print(f"Saved: {missing_out}")


if __name__ == "__main__":
    main()