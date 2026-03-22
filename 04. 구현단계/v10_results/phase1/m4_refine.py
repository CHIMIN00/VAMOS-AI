#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
M-4 정밀 재분류: SPREAD 항목을 §5 중심으로 재판정
"""
import json
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

BASE = r"D:\VAMOS\04. 구현단계\v10_results"

with open(os.path.join(BASE, "phase1", "v10_m4_mapping_result.json"), "r", encoding="utf-8") as f:
    data = json.load(f)

results = data["mapping_results"]

# SPREAD 재분류:
# - §5에 주요 매핑이 있으면 → MATCHED (§5 Phase 기재, §6/§7은 보조 참조)
# - §5에 없고 §6+§7에만 분산 → PARTIAL
# - §5 내 여러 Phase에 분산 → SPREAD 유지 (진짜 분산)

S5_START = 2266
S5_END = 2845
V3P1_S, V3P1_E = 2275, 2420
V3P2_S, V3P2_E = 2422, 2680
V3P3_S, V3P3_E = 2682, 2845

def classify_line(ln):
    if V3P1_S <= ln <= V3P1_E:
        return "V3-Phase1"
    elif V3P2_S <= ln <= V3P2_E:
        return "V3-Phase2"
    elif V3P3_S <= ln <= V3P3_E:
        return "V3-Phase3"
    elif S5_START <= ln <= S5_END:
        return "§5-other"
    elif 2846 <= ln < 3722:
        return "§6"
    elif ln >= 3722:
        return "§7"
    elif ln < 500:
        return "§2"
    elif ln < 1200:
        return "§3"
    elif ln < 2266:
        return "§4"
    return "other"


new_stats = {"MATCHED": 0, "PARTIAL": 0, "MISSING": 0, "SPREAD": 0, "NOT_APPLICABLE": 0}
missing_items = {"BLOCKER": [], "HIGH": [], "MEDIUM": [], "LOW": []}

for r in results:
    if r["verdict"] != "SPREAD":
        new_stats[r["verdict"]] += 1
        if r["verdict"] == "MISSING":
            sev = r.get("severity", "MEDIUM")
            missing_items[sev].append({
                "feature_id": r["feature_id"],
                "feature_name": r["feature_name"],
                "version_scope": r["version_scope"],
                "severity": sev,
                "role": r.get("role", "")
            })
        continue

    # Re-analyze SPREAD items
    lines = r.get("part2_lines", [])
    if not lines:
        r["verdict"] = "MISSING"
        r["severity"] = "MEDIUM"
        new_stats["MISSING"] += 1
        missing_items["MEDIUM"].append({
            "feature_id": r["feature_id"],
            "feature_name": r["feature_name"],
            "version_scope": r["version_scope"],
            "severity": "MEDIUM",
            "role": r.get("role", "")
        })
        continue

    # Classify each hit line
    sections = {}
    s5_phases = set()
    s5_lines = []
    non_s5_lines = []

    for hit in lines:
        ln = hit["line"]
        cat = classify_line(ln)
        sections[cat] = sections.get(cat, 0) + 1
        if cat.startswith("V3-Phase"):
            s5_phases.add(cat)
            s5_lines.append(hit)
        elif cat.startswith("§5"):
            s5_phases.add(cat)
            s5_lines.append(hit)
        else:
            non_s5_lines.append(hit)

    # Decision
    if s5_lines:
        if len(s5_phases) > 1:
            # 진짜 §5 내 다중 Phase 분산
            r["verdict"] = "SPREAD"
            r["part2_phases"] = sorted(s5_phases)
            r["part2_lines"] = s5_lines[:10]
            if non_s5_lines:
                r["also_in"] = [{"line": h["line"], "section": classify_line(h["line"])} for h in non_s5_lines[:5]]
            new_stats["SPREAD"] += 1
        else:
            # §5 단일 Phase에 매칭
            r["verdict"] = "MATCHED"
            r["part2_phase"] = sorted(s5_phases)[0]
            r["part2_lines"] = s5_lines[:5]
            if non_s5_lines:
                r["also_in"] = [{"line": h["line"], "section": classify_line(h["line"])} for h in non_s5_lines[:5]]
            # Remove SPREAD-specific keys
            r.pop("part2_phases", None)
            new_stats["MATCHED"] += 1
    else:
        # §5에 없음 → PARTIAL (§6/§7에만 존재)
        sec_summary = ", ".join(f"{k}({v}건)" for k, v in sorted(sections.items()))
        r["verdict"] = "PARTIAL"
        r["reason"] = f"§5 V3 Phase 미배정. 존재 위치: {sec_summary}"
        r["part2_lines"] = non_s5_lines[:5]
        r.pop("part2_phases", None)
        new_stats["PARTIAL"] += 1

# Update stats
data["statistics"] = new_stats
data["statistics_refined"] = True

# Rebuild missing_by_severity
data["missing_by_severity"] = {
    sev: {"count": len(items), "items": items}
    for sev, items in missing_items.items()
}

# Role별 통계 재계산
role_stats = {"PRIMARY": {}, "CROSSCHECK": {}}
for r in results:
    role = r.get("role", "UNKNOWN")
    verdict = r["verdict"]
    if role in role_stats:
        role_stats[role][verdict] = role_stats[role].get(verdict, 0) + 1
data["statistics_by_role"] = role_stats

outpath = os.path.join(BASE, "phase1", "v10_m4_mapping_result.json")
with open(outpath, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"[DONE] Refined results saved.")
print(f"\n=== 정밀 재분류 통계 ===")
print(f"Total: {len(results)}")
for k, v in new_stats.items():
    print(f"  {k}: {v}")
print(f"\n=== Role별 ===")
for role, rs in role_stats.items():
    print(f"  {role}: {rs}")
print(f"\n=== MISSING 심각도별 ===")
total_missing = sum(len(v) for v in missing_items.values())
for sev in ["BLOCKER", "HIGH", "MEDIUM", "LOW"]:
    items = missing_items[sev]
    print(f"  {sev}: {len(items)}건")
    for item in items[:3]:
        print(f"    - {item['feature_id']}: {item['feature_name'][:60]}")
    if len(items) > 3:
        print(f"    ... 외 {len(items)-3}건")
