"""IRRV-004 (GO/NO-GO 체크리스트) 제외 판정 반영"""
import json
from pathlib import Path

BASE = Path(r"D:\VAMOS\04. 구현단계\v10_results\phase0-d")
merged_path = BASE / "v10_merged_features.json"

with open(merged_path, "r", encoding="utf-8") as f:
    merged = json.load(f)

found = False
for feat in merged["features"]:
    if feat.get("feature_id") == "IRRV-004":
        feat["judgment_needed"] = False
        feat["judgment_result"] = "EXCLUDE"
        feat["extractable"] = False
        if "판단필요" in feat.get("notes", ""):
            feat["notes"] = feat["notes"].replace("판단필요", "판정완료(제외)")
        found = True
        print(f"IRRV-004 updated: judgment_result=EXCLUDE, extractable=False")
        break

if not found:
    print("ERROR: IRRV-004 not found!")
else:
    # 통계 보정: exclude 1건 추가
    merged["statistics"]["extractable_true"] -= 1
    merged["statistics"]["extractable_false"] += 1
    merged["meta"]["step4_exclude"] = 2  # 원래 1이었던 것을 2로 보정

    with open(merged_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    # judgment_report도 보정
    report_path = BASE / "v10_step4_judgment_report.json"
    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    # IRR-016 → IRRV-004로 ID 수정
    for item in report["user_judgment_needed"]["recommend_exclude"]:
        if item.get("feature_id") == "IRR-016":
            item["feature_id"] = "IRRV-004"
            item["source_file"] = "VAMOS_IMPLEMENTATION_READINESS_REVIEW"
            print("judgment_report: IRR-016 → IRRV-004 corrected")

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"extractable_true:  {merged['statistics']['extractable_true']}")
    print(f"extractable_false: {merged['statistics']['extractable_false']}")
