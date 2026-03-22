# -*- coding: utf-8 -*-
import json, re
from collections import Counter

# Load data
with open(r'D:/VAMOS/04. 구현단계/v10_results/phase1/v0_features_filtered.json', 'r', encoding='utf-8') as f:
    v0_features = json.load(f)

with open(r'D:/VAMOS/04. 구현단계/v10_results/phase1/m1_auto_mapping_raw.json', 'r', encoding='utf-8') as f:
    raw_mapping = json.load(f)

with open(r'D:/VAMOS/docs/guides/VAMOS_구현가이드_PART2_구현단계.md', 'r', encoding='utf-8') as f:
    part2_lines = f.readlines()

step_ranges = {
    "V0-STEP-1": (65, 437),
    "V0-STEP-2": (439, 646),
    "V0-STEP-3": (648, 810),
    "V0-STEP-4": (812, 1007),
    "V0-STEP-5": (1009, 1172),
    "V0-STEP-6": (1174, 1383),
}

# Reclassification overrides
reclassified_to_matched = {
    "CLAUDE-147", "CLAUDE-161", "CLAUDE-208", "P30-008", "P30-062",
    "IRGD-015", "IRRV-002", "D201-008", "D201-013", "D202-102",
    "D204-180", "DD1-003", "DQ1-001", "AINV-067", "CLAUDE-174", "CLAUDE-175"
}

reclassified_to_partial = {
    "P30-030": {"section": "S6", "lines": [3010], "note": "S6.3 VAL rules only. V0 Phase unassigned."},
    "P30-038": {"section": "S6", "lines": [3655], "note": "S6.11 FailureCodeRegistry only. V0 Phase unassigned."},
    "P30-047": {"section": "S6", "lines": [3349], "note": "S6.9 SDAR repair actions only. V0 Phase unassigned."},
}

final_missing = {
    "P30-032": {"severity": "LOW", "reason": "V0 6-area skeleton implicitly covered by STEP-1~6. No explicit assignment."},
    "P30-041": {"severity": "LOW", "reason": "File-level storage spec partially covered by STEP-5 MemoryRecord. No explicit item."},
    "P30-054": {"severity": "MEDIUM", "reason": "4-tier approval tree not in V0. Only P0/P1/P2 auto/hold in I-19 stub."},
    "P30-068": {"severity": "LOW", "reason": "14 goals A/B/C/D mapping is design-level. Not required as V0 implementation item."},
    "D204-179": {"severity": "HIGH", "reason": "Cost infra (weight table, 60/80/95% alerts) not in V0 STEP. I-9 stub only handles 80/100%."},
    "D204-182": {"severity": "MEDIUM", "reason": "Routing infra (4-axis decision tree) absent from V0. Likely V1+ scope but version_scope includes V0."},
    "DD1-002": {"severity": "LOW", "reason": "Glossary ownership validation is doc management tool. Not a V0 code item."},
    "CLIB-123": {"severity": "LOW", "reason": "YouTube collector is Cloud Library sub-feature. Inappropriate for V0 skeleton scope."},
}

still_partial = {
    "CLAUDE-150": {"section": "S7", "lines": [3761], "note": "S7.2 V1 GO/NO-GO only. V1 primary mapping target."},
    "P30-063": {"section": "S5-V3", "lines": [2327], "note": "V3 infra only. V0 Phase unassigned."},
    "P30-064": {"section": "S4-V2", "lines": [1799], "note": "V2 deliverables only. V0 Phase unassigned."},
    "CLIB-042": {"section": "OTHER", "lines": [33], "note": "TOC mention only. V0 Phase unassigned."},
}

# Build final mapping
final_results = []
for raw in raw_mapping:
    fid = raw["feature_id"]
    feat = next((f for f in v0_features if f["feature_id"] == fid), None)

    result = {
        "feature_id": fid,
        "feature_name": feat["feature_name"] if feat else raw["feature_name"],
        "version_scope": raw["version_scope"],
        "prev_status": raw["prev_status"],
    }

    if fid in final_missing:
        result["judgment"] = "MISSING"
        result["severity"] = final_missing[fid]["severity"]
        result["reason"] = final_missing[fid]["reason"]
        result["part2_phase"] = None
        result["part2_line"] = None
    elif fid in reclassified_to_partial:
        info = reclassified_to_partial[fid]
        result["judgment"] = "PARTIAL"
        result["part2_phase"] = info["section"]
        result["part2_line"] = info["lines"]
        result["note"] = info["note"]
    elif fid in still_partial:
        info = still_partial[fid]
        result["judgment"] = "PARTIAL"
        result["part2_phase"] = info["section"]
        result["part2_line"] = info["lines"]
        result["note"] = info["note"]
    elif fid in reclassified_to_matched:
        v0_secs = raw.get("v0_sections", [])
        if not v0_secs:
            result["judgment"] = "MATCHED"
            result["part2_phase"] = raw.get("part2_phase")
            result["part2_line"] = raw.get("part2_line")
        elif len(v0_secs) > 1:
            result["judgment"] = "SPREAD"
            result["part2_phases"] = v0_secs
            result["part2_line"] = raw.get("v0_lines", [])
        else:
            result["judgment"] = "MATCHED"
            result["part2_phase"] = v0_secs[0]
            result["part2_line"] = raw.get("v0_lines", [])
    elif raw["judgment"] in ("MATCHED", "SPREAD"):
        v0_secs = raw.get("v0_sections", [])
        if len(v0_secs) > 1:
            result["judgment"] = "SPREAD"
            result["part2_phases"] = v0_secs
        else:
            result["judgment"] = "MATCHED"
            result["part2_phase"] = v0_secs[0] if v0_secs else None
        result["part2_line"] = raw.get("v0_lines", [])
    else:
        result["judgment"] = raw["judgment"]
        result["part2_phase"] = raw.get("part2_phase")
        result["part2_line"] = raw.get("part2_line")

    # W-28: cross-version note
    vs = result.get("version_scope", "")
    versions = [v.strip() for v in vs.split(",")]
    if len(versions) > 1 and versions[0] != "V0":
        agent_map = {"V0": "M-1", "V1": "M-2", "V2": "M-3", "V3": "M-4"}
        primary = agent_map.get(versions[0], "?")
        result["cross_version_note"] = f"Primary mapper: {primary} ({versions[0]}). M-1 cross-check only."

    final_results.append(result)

# Statistics
judgments = Counter(r["judgment"] for r in final_results)

print("=" * 60)
print("M-1 V0 -> PART2 S2 Mapping Verification Final Stats")
print("=" * 60)
print(f"Total V0 features: {len(final_results)}")
print(f"MATCHED:        {judgments.get('MATCHED', 0)}")
print(f"SPREAD:         {judgments.get('SPREAD', 0)}")
print(f"PARTIAL:        {judgments.get('PARTIAL', 0)}")
print(f"MISSING:        {judgments.get('MISSING', 0)}")
print(f"NOT_APPLICABLE: {judgments.get('NOT_APPLICABLE', 0)}")

missing_items = [r for r in final_results if r["judgment"] == "MISSING"]
sev_count = Counter(r.get("severity", "N/A") for r in missing_items)
print(f"\nMISSING severity distribution:")
for sev in ["BLOCKER", "HIGH", "MEDIUM", "LOW"]:
    print(f"  {sev}: {sev_count.get(sev, 0)}")

cross_v = [r for r in final_results if "cross_version_note" in r]
print(f"\nCross-version features (M-1 cross-check): {len(cross_v)}")

# Save final
output = {
    "meta": {
        "agent": "M-1",
        "phase": "Phase 1",
        "scope": "V0 features -> PART2 S2 (V0 STEP 1~6)",
        "feature_filter": "version_scope contains V0",
        "total_features": len(final_results),
        "generated_date": "2026-03-09",
        "part2_version": "v21.0.0",
        "part2_section": "S2 V0 (lines 54~1383) + S7.1 V0 GO/NO-GO (lines 3731~3754)"
    },
    "statistics": {
        "MATCHED": judgments.get("MATCHED", 0),
        "SPREAD": judgments.get("SPREAD", 0),
        "PARTIAL": judgments.get("PARTIAL", 0),
        "MISSING": judgments.get("MISSING", 0),
        "NOT_APPLICABLE": judgments.get("NOT_APPLICABLE", 0),
        "total": len(final_results),
        "cross_version_count": len(cross_v)
    },
    "missing_by_severity": {
        "BLOCKER": [{"feature_id": r["feature_id"], "feature_name": r["feature_name"], "reason": r.get("reason","")} for r in missing_items if r.get("severity") == "BLOCKER"],
        "HIGH": [{"feature_id": r["feature_id"], "feature_name": r["feature_name"], "reason": r.get("reason","")} for r in missing_items if r.get("severity") == "HIGH"],
        "MEDIUM": [{"feature_id": r["feature_id"], "feature_name": r["feature_name"], "reason": r.get("reason","")} for r in missing_items if r.get("severity") == "MEDIUM"],
        "LOW": [{"feature_id": r["feature_id"], "feature_name": r["feature_name"], "reason": r.get("reason","")} for r in missing_items if r.get("severity") == "LOW"],
    },
    "partial_items": [
        {"feature_id": r["feature_id"], "feature_name": r["feature_name"], "part2_phase": r.get("part2_phase"), "part2_line": r.get("part2_line"), "note": r.get("note", "")}
        for r in final_results if r["judgment"] == "PARTIAL"
    ],
    "mapping_results": final_results
}

with open(r'D:/VAMOS/04. 구현단계/v10_results/phase1/m1_v0_mapping_result.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("\nSaved: m1_v0_mapping_result.json")

# Print MISSING details
print("\n=== MISSING Items ===")
for r in missing_items:
    sev = r.get("severity", "N/A")
    print(f"[{sev}] {r['feature_id']}: {r['feature_name'][:70]}")
    print(f"  Reason: {r.get('reason', 'N/A')}")

# Print PARTIAL details
partial_items = [r for r in final_results if r["judgment"] == "PARTIAL"]
print(f"\n=== PARTIAL Items ({len(partial_items)}) ===")
for r in partial_items:
    print(f"{r['feature_id']}: {r['feature_name'][:70]}")
    print(f"  Location: {r.get('part2_phase', 'N/A')} L{r.get('part2_line', 'N/A')}")
    print(f"  Note: {r.get('note', 'N/A')}")
