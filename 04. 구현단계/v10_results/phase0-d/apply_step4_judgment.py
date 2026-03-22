"""
Phase 0-D STEP 4: 사용자 판정 결과 반영 스크립트
- 확신도 높음 1건 (CROSS-001): 기능 → 자동 반영
- 기능 추천 18건: 기능 확정
- 제외 추천 2건 (IRR-016, BGNR-030): 제외 확정
"""
import json
from pathlib import Path

BASE = Path(r"D:\VAMOS\04. 구현단계\v10_results\phase0-d")

# 판정 결과 정의
INCLUDE_IDS = {
    "CROSS-001",  # 자동 반영 (높음)
    "D203-089", "D203-120", "D208-040",
    "DD1-002", "DD1-003", "DQ1-007",
    "PB1-021", "AINV-028", "AINV-079", "AINV-121",
    "CLIB-098", "TEAM-087", "TEAM-088", "TEAM-089", "TEAM-103",
    "SDAR-120", "SDAR-121", "BGNR-019"
}
EXCLUDE_IDS = {"IRR-016", "BGNR-030"}
ALL_JUDGMENT_IDS = INCLUDE_IDS | EXCLUDE_IDS

# 1. v10_merged_features.json 업데이트
merged_path = BASE / "v10_merged_features.json"
with open(merged_path, "r", encoding="utf-8") as f:
    merged = json.load(f)

include_count = 0
exclude_count = 0
not_found = set(ALL_JUDGMENT_IDS)

for feat in merged["features"]:
    fid = feat.get("feature_id", "")
    if fid in INCLUDE_IDS:
        feat["judgment_needed"] = False
        feat["judgment_result"] = "INCLUDE"
        # notes에서 "판단필요" 제거하고 판정 결과 추가
        if "판단필요" in feat.get("notes", ""):
            feat["notes"] = feat["notes"].replace("판단필요", "판정완료(기능)")
        include_count += 1
        not_found.discard(fid)
    elif fid in EXCLUDE_IDS:
        feat["judgment_needed"] = False
        feat["judgment_result"] = "EXCLUDE"
        feat["extractable"] = False
        if "판단필요" in feat.get("notes", ""):
            feat["notes"] = feat["notes"].replace("판단필요", "판정완료(제외)")
        exclude_count += 1
        not_found.discard(fid)

# 통계 업데이트
if "extractable_true" in merged.get("statistics", {}):
    merged["statistics"]["extractable_true"] -= exclude_count
    merged["statistics"]["extractable_false"] += exclude_count

# 메타에 판정 기록 추가
merged["meta"]["step4_judgment_applied"] = True
merged["meta"]["step4_date"] = "2026-03-09"
merged["meta"]["step4_include"] = include_count
merged["meta"]["step4_exclude"] = exclude_count

with open(merged_path, "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

# 2. judgment_report에 사용자 확정 기록
report_path = BASE / "v10_step4_judgment_report.json"
with open(report_path, "r", encoding="utf-8") as f:
    report = json.load(f)

report["user_decision"] = {
    "decision": "추천대로 전건 확정",
    "decision_date": "2026-03-09",
    "auto_resolved_applied": 1,
    "include_confirmed": 18,
    "exclude_confirmed": 2,
    "total_resolved": 21
}
report["meta"]["status"] = "COMPLETED"

with open(report_path, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

# 3. delta.json에도 step4 완료 기록
delta_path = BASE / "v10_layer1_layer2_delta.json"
with open(delta_path, "r", encoding="utf-8") as f:
    delta = json.load(f)

delta["statistics"]["step4"] = {
    "total_judgment_items": 21,
    "auto_resolved_high": 1,
    "user_confirmed_include": 18,
    "user_confirmed_exclude": 2,
    "status": "COMPLETED"
}
# steps 목록에 STEP 4 추가
if "STEP 4" not in delta["meta"]["steps"]:
    delta["meta"]["steps"].append("STEP 4")

with open(delta_path, "w", encoding="utf-8") as f:
    json.dump(delta, f, ensure_ascii=False, indent=2)

print(f"=== STEP 4 판정 결과 반영 완료 ===")
print(f"기능 포함 확정: {include_count}건")
print(f"제외 확정:      {exclude_count}건")
print(f"미발견 ID:      {not_found if not_found else '없음'}")
print(f"extractable_true:  {merged['statistics'].get('extractable_true', 'N/A')}")
print(f"extractable_false: {merged['statistics'].get('extractable_false', 'N/A')}")
