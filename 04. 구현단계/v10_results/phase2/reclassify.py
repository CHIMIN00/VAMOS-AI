#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Step 1 → Step 2 재분류 스크립트
재검토 필요 항목을 Step 1에서 제거하고 Step 2로 이동
"""

import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

CONSOLIDATED = r"D:\VAMOS\04. 구현단계\v10_results\phase2\consolidated_missing.json"
STEP1_RESULT = r"D:\VAMOS\04. 구현단계\v10_results\phase2\step1_result.json"

with open(CONSOLIDATED, "r", encoding="utf-8") as f:
    cons = json.load(f)
cons_map = {it["feature_id"]: it for it in cons["items"]}

with open(STEP1_RESULT, "r", encoding="utf-8") as f:
    step1 = json.load(f)

classified = step1["classified_items"]
unclassified = step1["unclassified_items"]

# ─── 재검토 대상 ID 목록 ─────────────────────────────────

# 3-1 NOT_APPLICABLE 재검토 92건 (S7AE-396~489 범위 = C-045~C-104, D-001~D-034)
na_review_ids = set()
for item in classified:
    if item["substatus"] == "NOT_APPLICABLE":
        fid = item["feature_id"]
        if fid.startswith("S7AE-"):
            num = int(fid.split("-")[1])
            if 396 <= num <= 489:
                na_review_ids.add(fid)

# 3-2 SUB_FEATURE 재검토 30건
sub_review_ids = {
    # 키워드 PART2 미존재 3건
    "D203-082", "AINV-056", "S7NP-173",
    # 범용어 우연한 매칭 15건
    "D203-008", "D205-057", "D206-066", "D207-045", "D207-100",
    "S7NP-022", "S7BG-003", "AINV-025", "AINV-136", "AINV-143",
    "AINV-141", "D203-070", "D206-222", "AINV-052", "AINV-070",
    # 독립 기능 상세 부족 12건
    "D206-115", "D206-199", "D205-025", "S7JM-257", "D205-001",
    "DD4-011", "D204-105", "AINV-080", "S7NP-029", "S7NP-032",
    "S7JM-158", "PB2-006", "S7FI-286",
}

# 3-3 SKIP 재검토 46건 (유지 14건 제외한 나머지)
skip_keep_ids = {
    "AINV-003", "AINV-066", "CLAUDE-053", "D204-005", "D204-040",
    "D207-081", "D202-097", "D204-125", "D206-155", "D206-210",
    "D208-056", "CLAUDE-247", "D208-001", "DD8-005",
}
skip_review_ids = set()
for item in classified:
    if item["substatus"] == "SKIP_CONFIRMED":
        if item["feature_id"] not in skip_keep_ids:
            skip_review_ids.add(item["feature_id"])

# 3-5 SECTION6 재검토 2건
s6_review_ids = {"S7AE-035", "D208-090"}

# 전체 이동 대상
all_move_ids = na_review_ids | sub_review_ids | skip_review_ids | s6_review_ids

print(f"=== 재분류 요약 ===")
print(f"3-1 NOT_APPLICABLE 재검토 → Step2: {len(na_review_ids)}건")
print(f"3-2 SUB_FEATURE 재검토 → Step2: {len(sub_review_ids)}건")
print(f"3-3 SKIP 재검토 → Step2: {len(skip_review_ids)}건")
print(f"3-5 SECTION6 재검토 → Step2: {len(s6_review_ids)}건")
print(f"총 Step2 이동: {len(all_move_ids)}건")

# ─── Step 1 유지 항목 분리 ─────────────────────────────────
step1_keep = []
step1_move = []
for item in classified:
    if item["feature_id"] in all_move_ids:
        step1_move.append(item)
    else:
        step1_keep.append(item)

print(f"\nStep 1 유지: {len(step1_keep)}건")
print(f"Step 2 이동: {len(step1_move)}건")
print(f"Step 2 기존: {len(unclassified)}건")
print(f"Step 2 합계: {len(step1_move) + len(unclassified)}건")

# 유지 항목 분포
keep_stats = {}
for item in step1_keep:
    s = item["substatus"]
    keep_stats[s] = keep_stats.get(s, 0) + 1
print(f"\nStep 1 유지 분포:")
for k, v in sorted(keep_stats.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

# ─── 이동 항목에 consolidated 정보 보강 ───────────────────
move_enriched = []
for item in step1_move:
    fid = item["feature_id"]
    cons_item = cons_map.get(fid, {})
    enriched = {
        "feature_id": fid,
        "feature_name": item["feature_name"],
        "severity": item.get("severity", cons_item.get("severity", "")),
        "version_scope": item.get("version_scope", cons_item.get("version_scope", "")),
        "category": cons_item.get("category", ""),
        "agent": cons_item.get("agent", ""),
        "source_section": cons_item.get("source_section", ""),
        "action": cons_item.get("action", item.get("action", "")),
        "step7_note": cons_item.get("step7_note", ""),
        "original_substatus": item["substatus"],
        "original_match_type": item.get("match_type", ""),
        "original_evidence": item.get("evidence", []),
        "move_reason": "",
    }

    if fid in na_review_ids:
        enriched["move_reason"] = "NOT_APPLICABLE 재검토: D2.0 설계문서에 상세 스펙 존재하나 PART2 미반영"
    elif fid in sub_review_ids:
        enriched["move_reason"] = "SUB_FEATURE 재검토: 키워드 매칭이 의미적으로 불일치하거나 PART2에 상세 구현 없음"
    elif fid in skip_review_ids:
        enriched["move_reason"] = "SKIP 재검토: SOT에 구체적 구현 내용 존재, PART2 추가 필요"
    elif fid in s6_review_ids:
        enriched["move_reason"] = "SECTION6 재검토: §6에서 충분히 커버되지 않음"

    move_enriched.append(enriched)

# ─── JSON 출력 (다른 스크립트에서 활용) ───────────────────
output = {
    "_meta": {
        "date": "2026-03-10",
        "step1_keep_count": len(step1_keep),
        "step2_move_count": len(move_enriched),
        "step2_existing_count": len(unclassified),
        "step2_total_count": len(move_enriched) + len(unclassified),
    },
    "step1_keep": step1_keep,
    "step2_move_from_step1": move_enriched,
    "step2_existing": unclassified,
    "move_ids": {
        "from_na": sorted(na_review_ids),
        "from_sub": sorted(sub_review_ids),
        "from_skip": sorted(skip_review_ids),
        "from_s6": sorted(s6_review_ids),
    }
}

OUT_PATH = r"D:\VAMOS\04. 구현단계\v10_results\phase2\reclassify_result.json"
with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nSaved: {OUT_PATH}")
print("DONE.")
