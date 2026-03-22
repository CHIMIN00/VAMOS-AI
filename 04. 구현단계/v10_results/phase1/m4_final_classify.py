#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
M-4 최종 분류: SPREAD → 주 매핑 Phase 결정
SPREAD는 §5 내 2개 이상 Phase에 분산된 경우에만 유지.
대부분은 주 Phase를 특정하여 MATCHED로 전환.
"""
import json
import sys
import os
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

BASE = r"D:\VAMOS\04. 구현단계\v10_results"

with open(os.path.join(BASE, "phase1", "v10_m4_mapping_result.json"), "r", encoding="utf-8") as f:
    data = json.load(f)

results = data["mapping_results"]

V3P1_S, V3P1_E = 2275, 2420
V3P2_S, V3P2_E = 2422, 2680
V3P3_S, V3P3_E = 2682, 2845

def get_v3_phase(ln):
    if V3P1_S <= ln <= V3P1_E:
        return "V3-Phase1"
    elif V3P2_S <= ln <= V3P2_E:
        return "V3-Phase2"
    elif V3P3_S <= ln <= V3P3_E:
        return "V3-Phase3"
    return None

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

    lines = r.get("part2_lines", [])

    # Count hits per V3-Phase
    phase_counter = Counter()
    phase_lines = {}
    other_lines = []

    for hit in lines:
        ln = hit["line"]
        ph = get_v3_phase(ln)
        if ph:
            phase_counter[ph] += 1
            phase_lines.setdefault(ph, []).append(hit)
        else:
            other_lines.append(hit)

    # also check also_in field
    for ai in r.get("also_in", []):
        ln = ai.get("line", 0)
        ph = get_v3_phase(ln)
        if ph:
            phase_counter[ph] += 1

    distinct_phases = list(phase_counter.keys())

    if len(distinct_phases) == 0:
        # No §5 V3 Phase hits — should not happen for SPREAD, but handle
        r["verdict"] = "PARTIAL"
        r["reason"] = "SPREAD에서 재분류: §5 V3 Phase 히트 없음"
        new_stats["PARTIAL"] += 1
    elif len(distinct_phases) == 1:
        # Single phase → MATCHED
        r["verdict"] = "MATCHED"
        r["part2_phase"] = distinct_phases[0]
        r["part2_lines"] = phase_lines.get(distinct_phases[0], lines)[:5]
        r.pop("part2_phases", None)
        new_stats["MATCHED"] += 1
    elif len(distinct_phases) == 2:
        # 2개 Phase → SPREAD 유지 but 주 Phase 표시
        most_common = phase_counter.most_common(1)[0][0]
        r["verdict"] = "SPREAD"
        r["primary_phase"] = most_common
        r["part2_phases"] = sorted(distinct_phases)
        r["hit_counts"] = dict(phase_counter)
        new_stats["SPREAD"] += 1
    else:
        # 3개 Phase 모두 → SPREAD
        most_common = phase_counter.most_common(1)[0][0]
        r["verdict"] = "SPREAD"
        r["primary_phase"] = most_common
        r["part2_phases"] = sorted(distinct_phases)
        r["hit_counts"] = dict(phase_counter)
        new_stats["SPREAD"] += 1

# Update
data["statistics"] = new_stats
data["statistics_final"] = True

data["missing_by_severity"] = {
    sev: {"count": len(items), "items": items}
    for sev, items in missing_items.items()
}

role_stats = {"PRIMARY": {}, "CROSSCHECK": {}}
for r in results:
    role = r.get("role", "UNKNOWN")
    verdict = r["verdict"]
    if role in role_stats:
        role_stats[role][verdict] = role_stats[role].get(verdict, 0) + 1
data["statistics_by_role"] = role_stats

# Save final
outpath = os.path.join(BASE, "phase1", "v10_m4_mapping_result.json")
with open(outpath, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Also generate summary report
print(f"[DONE] Final classification complete.")
print(f"\n{'='*60}")
print(f"  VAMOS v10 Phase 1 M-4 매핑 결과 (최종)")
print(f"{'='*60}")
print(f"  전체 V3 기능: {len(results)}건")
print(f"  PRIMARY (M-4 주 매핑): {sum(1 for r in results if r.get('role')=='PRIMARY')}건")
print(f"  CROSSCHECK (교차확인): {sum(1 for r in results if r.get('role')=='CROSSCHECK')}건")
print(f"{'='*60}")
print(f"\n  [판정 통계]")
for k, v in new_stats.items():
    pct = v / len(results) * 100
    print(f"    {k:18s}: {v:4d}건 ({pct:5.1f}%)")
print(f"\n  [Role별 통계]")
for role, rs in role_stats.items():
    print(f"    {role}:")
    for k, v in sorted(rs.items()):
        print(f"      {k}: {v}")
print(f"\n  [MISSING 심각도별]")
total_missing = sum(len(v) for v in missing_items.values())
print(f"    전체 MISSING: {total_missing}건")
for sev in ["BLOCKER", "HIGH", "MEDIUM", "LOW"]:
    items = missing_items[sev]
    print(f"\n    [{sev}] {len(items)}건:")
    for item in items:
        print(f"      {item['feature_id']:12s} | {item['role']:11s} | {item['feature_name'][:70]}")

# SPREAD 분포
spread_items = [r for r in results if r["verdict"] == "SPREAD"]
print(f"\n  [SPREAD 분포] {len(spread_items)}건")
phase_dist = Counter()
for r in spread_items:
    phases = tuple(sorted(r.get("part2_phases", [])))
    phase_dist[phases] += 1
for phases, cnt in phase_dist.most_common():
    print(f"    {' + '.join(phases)}: {cnt}건")
