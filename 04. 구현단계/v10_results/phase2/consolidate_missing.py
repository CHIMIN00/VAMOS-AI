"""
v10 Phase 2 대화 27: REAL_MISSING 전수 통합 + 심각도 정렬 + Phase 배정 제안
입력: M-1~M-4 missing items + Phase 1.5 adversarial report corrections
출력: consolidated_missing.json
"""
import json
import os

BASE = r"D:\VAMOS\04. 구현단계\v10_results"

# ── 1. Load M-1 mapping result (extract MISSING items) ──
with open(os.path.join(BASE, "phase1", "m1_v0_mapping_result.json"), "r", encoding="utf-8") as f:
    m1_data = json.load(f)

m1_missing = []
if isinstance(m1_data, dict):
    # Try to find missing items in various structures
    for key in ["missing", "MISSING", "items", "results"]:
        if key in m1_data:
            items = m1_data[key]
            if isinstance(items, list):
                m1_missing = [i for i in items if i.get("verdict", i.get("status", "")) == "MISSING" or True]
                break
    if not m1_missing:
        # Iterate all items and filter MISSING
        all_items = m1_data.get("items", m1_data.get("results", []))
        if isinstance(all_items, list):
            m1_missing = [i for i in all_items if i.get("verdict") == "MISSING" or i.get("status") == "MISSING"]
elif isinstance(m1_data, list):
    m1_missing = [i for i in m1_data if i.get("verdict") == "MISSING" or i.get("status") == "MISSING"]

# ── 2. Load M-2 missing items ──
with open(os.path.join(BASE, "phase1", "v10_m2_missing_items.json"), "r", encoding="utf-8") as f:
    m2_data = json.load(f)

m2_missing = []
if isinstance(m2_data, dict):
    by_sev = m2_data.get("by_severity", {})
    for sev, sev_data in by_sev.items():
        by_cat = sev_data.get("by_category", {})
        for cat, items in by_cat.items():
            for item in items:
                item["severity"] = sev
                item["category"] = cat
                item["agent"] = "M-2"
                m2_missing.append(item)

# ── 3. Load M-3 missing items ──
with open(os.path.join(BASE, "phase1", "v10_m3_missing_final.json"), "r", encoding="utf-8") as f:
    m3_data = json.load(f)

m3_missing = []
if isinstance(m3_data, list):
    for item in m3_data:
        item["agent"] = "M-3"
        m3_missing.append(item)

# ── 4. Load M-4 missing items ──
with open(os.path.join(BASE, "phase1", "v10_m4_missing_items.json"), "r", encoding="utf-8") as f:
    m4_data = json.load(f)

m4_missing = []
if isinstance(m4_data, dict):
    for item in m4_data.get("items", []):
        item["agent"] = "M-4"
        m4_missing.append(item)

# ── 5. Phase 1.5 corrections ──
# FP confirmed (remove from MATCHED → add to MISSING)
fp_confirmed = [
    {"feature_id": "S7AE-035", "feature_name": "Citation 시스템", "severity": "HIGH", "version_scope": "V2", "agent": "M-3", "source": "Phase1.5_FP"},
    {"feature_id": "AINV-003", "feature_name": "5-Agent 워크플로우 오케스트레이션", "severity": "HIGH", "version_scope": "V1", "agent": "M-2", "source": "Phase1.5_FP"},
    {"feature_id": "AINV-066", "feature_name": "Docker Compose 전체 스택 설정", "severity": "MEDIUM", "version_scope": "V0", "agent": "M-1", "source": "Phase1.5_FP"},
]

# FN confirmed (remove from MISSING → already MATCHED)
fn_confirmed_ids = set()
# ~38 confirmed FN items - we mark their IDs for exclusion
# D203-065 캘린더/태스크 관리 is a confirmed FN
fn_confirmed_ids.add("D203-065")
# V0RD-010 Multi-Brain Adapter was confirmed TP in Phase 1.5
fn_confirmed_ids.add("V0RD-010")

# ── 6. Consolidate all ──
all_missing = []
seen_ids = set()

def add_items(items, default_agent=""):
    for item in items:
        fid = item.get("feature_id", "")
        if fid in seen_ids or fid in fn_confirmed_ids:
            continue
        seen_ids.add(fid)
        all_missing.append({
            "feature_id": fid,
            "feature_name": item.get("feature_name", ""),
            "version_scope": item.get("version_scope", ""),
            "severity": item.get("severity", "MEDIUM"),
            "category": item.get("category", ""),
            "agent": item.get("agent", default_agent),
            "role": item.get("role", item.get("m3_role", item.get("mapping_role", ""))),
            "source_section": item.get("source_section", ""),
        })

add_items(m1_missing, "M-1")
add_items(m2_missing, "M-2")
add_items(m3_missing, "M-3")
add_items(m4_missing, "M-4")
add_items(fp_confirmed)

# ── 7. Sort by severity ──
sev_order = {"BLOCKER": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
all_missing.sort(key=lambda x: (sev_order.get(x["severity"], 9), x["feature_id"]))

# ── 8. Phase assignment suggestion ──
def suggest_phase(item):
    vs = item.get("version_scope", "")
    fid = item.get("feature_id", "")
    fname = item.get("feature_name", "")
    sev = item.get("severity", "")

    # BLOCKER: must go to specific phase
    if "PARL" in fname or "Agent Swarm" in fname:
        return "§5.2 V3-Phase 2"
    if "Agent Specialization" in fname:
        return "§5.3 V3-Phase 3"

    # STEP7 estimated items (S7*) - mostly NOT_APPLICABLE candidates
    if fid.startswith("S7"):
        if "TITLE_ONLY" in fname or "시스템설계" in fname or "데이터설계" in fname:
            return "NOT_APPLICABLE (STEP7 TITLE_ONLY)"
        return "REVIEW_NEEDED (STEP7 추정)"

    # Version-based assignment
    if "V0" in vs and "V1" not in vs:
        return "§2 V0"

    primary_version = vs.split(",")[0] if vs else ""
    if primary_version == "V1":
        return "§3 V1 (Phase TBD)"
    elif primary_version == "V2":
        return "§4 V2 (Phase TBD)"
    elif primary_version == "V3":
        return "§5 V3 (Phase TBD)"

    # Multi-version: assign to earliest primary
    if "V1" in vs:
        return "§3 V1 (Phase TBD)"
    elif "V2" in vs:
        return "§4 V2 (Phase TBD)"
    elif "V3" in vs:
        return "§5 V3 (Phase TBD)"

    return "REVIEW_NEEDED"

# Classify items
for item in all_missing:
    item["suggested_phase"] = suggest_phase(item)

    # Determine action
    role = item.get("role", "")
    sev = item["severity"]

    if sev == "BLOCKER":
        item["action"] = "PART2_ADD"  # Must add to PART2
    elif sev == "HIGH" and role == "PRIMARY":
        item["action"] = "PART2_ADD"  # Should add
    elif sev == "HIGH" and role in ("CROSSCHECK", "CROSS_CHECK"):
        item["action"] = "REVIEW"  # Review needed - may be covered by primary version
    elif "NOT_APPLICABLE" in item["suggested_phase"]:
        item["action"] = "RECLASSIFY_NA"
    elif "STEP7" in item["suggested_phase"]:
        item["action"] = "REVIEW"
    elif sev in ("MEDIUM", "LOW") and role in ("CROSSCHECK", "CROSS_CHECK"):
        item["action"] = "SKIP"  # Low priority crosscheck
    elif sev == "MEDIUM" and role == "PRIMARY":
        item["action"] = "PART2_ADD"
    else:
        item["action"] = "SKIP"

# ── 9. Statistics ──
stats = {
    "total_missing": len(all_missing),
    "by_severity": {},
    "by_action": {},
    "by_suggested_phase": {},
}

for item in all_missing:
    sev = item["severity"]
    stats["by_severity"][sev] = stats["by_severity"].get(sev, 0) + 1
    action = item["action"]
    stats["by_action"][action] = stats["by_action"].get(action, 0) + 1
    phase = item["suggested_phase"]
    stats["by_suggested_phase"][phase] = stats["by_suggested_phase"].get(phase, 0) + 1

# ── 10. Save ──
output = {
    "_meta": {
        "phase": "Phase 2 - Conversation 27",
        "purpose": "REAL_MISSING 전수 통합 + 심각도 정렬 + Phase 배정 제안",
        "generated_date": "2026-03-09",
        "inputs": [
            "m1_v0_mapping_result.json",
            "v10_m2_missing_items.json",
            "v10_m3_missing_final.json",
            "v10_m4_missing_items.json",
            "v10_adversarial_report.md (FP/FN corrections)"
        ],
        "fn_excluded_count": len(fn_confirmed_ids),
        "fp_added_count": len(fp_confirmed),
    },
    "statistics": stats,
    "items": all_missing
}

out_path = os.path.join(BASE, "phase2", "consolidated_missing.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

# Print summary
print(f"=== v10 Phase 2 Consolidated MISSING ===")
print(f"Total: {stats['total_missing']}")
print(f"\nBy Severity:")
for sev in ["BLOCKER", "HIGH", "MEDIUM", "LOW"]:
    print(f"  {sev}: {stats['by_severity'].get(sev, 0)}")
print(f"\nBy Action:")
for action, count in sorted(stats["by_action"].items(), key=lambda x: -x[1]):
    print(f"  {action}: {count}")
print(f"\nBy Phase (top 10):")
for phase, count in sorted(stats["by_suggested_phase"].items(), key=lambda x: -x[1])[:10]:
    print(f"  {phase}: {count}")

# BLOCKER items detail
print(f"\n=== BLOCKER Items ===")
for item in all_missing:
    if item["severity"] == "BLOCKER":
        print(f"  {item['feature_id']}: {item['feature_name']} → {item['suggested_phase']}")
