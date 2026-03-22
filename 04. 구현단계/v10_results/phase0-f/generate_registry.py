"""
Phase 0-F: 최종 Feature Registry 확정
- STEP 1: 통합 (merged_features + GAP항목 + 제외 판정 + SUPERSEDED)
- STEP 2: part2_mapping_status 초기 상태 부여
- STEP 3: 통계 산출
"""
import json
from collections import Counter
from datetime import date

BASE = r"D:\VAMOS\04. 구현단계\v10_results"

# ── Load inputs ──────────────────────────────────────────────────────
with open(f"{BASE}/phase0-d/v10_merged_features.json", encoding="utf-8") as f:
    merged = json.load(f)

with open(f"{BASE}/phase0-e/v10_v8_revalidation.json", encoding="utf-8") as f:
    v8_reval = json.load(f)

with open(f"{BASE}/phase0-e/v10_v9_revalidation.json", encoding="utf-8") as f:
    v9_reval = json.load(f)

with open(f"{BASE}/phase0-d/v10_step4_judgment_report.json", encoding="utf-8") as f:
    judgment = json.load(f)

features = merged["features"]
print(f"[INPUT] merged_features: {len(features)} features")

# ══════════════════════════════════════════════════════════════════════
# STEP 1: 통합
# ══════════════════════════════════════════════════════════════════════

# 1-a) 사용자 판정: 제외 확정 항목 삭제
exclude_ids = set()
for item in judgment["user_judgment_needed"]["recommend_exclude"]:
    fid = item["feature_id"]
    exclude_ids.add(fid)
    # id_remap으로 관련 ID도 추가
    if fid in judgment.get("id_remap_note", {}).get("mappings", {}):
        for mapped_id in judgment["id_remap_note"]["mappings"][fid]:
            exclude_ids.add(mapped_id)

# IRR-016 → IRRV-004 매핑도 처리
if "IRR-016" in judgment.get("id_remap_note", {}).get("mappings", {}):
    for mapped_id in judgment["id_remap_note"]["mappings"]["IRR-016"]:
        exclude_ids.add(mapped_id)

print(f"[STEP 1-a] Exclude IDs: {exclude_ids}")

before_count = len(features)
features = [f for f in features if f["feature_id"] not in exclude_ids]
excluded_count = before_count - len(features)
print(f"[STEP 1-a] Excluded {excluded_count} features (before={before_count}, after={len(features)})")

# 1-b) SUPERSEDED 기능 → NOT_APPLICABLE 자동 태깅
# Check for SUPERSEDED in notes or feature_name
superseded_count = 0
for f in features:
    notes = (f.get("notes") or "").upper()
    name = (f.get("feature_name") or "").upper()
    if "SUPERSEDED" in notes or "SUPERSEDED" in name:
        f["_superseded"] = True
        superseded_count += 1
    else:
        f["_superseded"] = False

print(f"[STEP 1-b] SUPERSEDED features: {superseded_count}")

# 1-c) Phase 0-E GAP_FOUND 항목 추가
# (a) Registry에 아예 없는 기능 → 새 feature_id (GAP-001~)
# (b) 기능은 있지만 Phase 배정 미확인 → PRE_GAP

# Phase 0-E에서 발견된 GAP들은 카테고리 수준의 구조적 갭이지
# 개별 신규 기능은 아님. 따라서:
# - CCG-1 (phase_assignment 전역 부재): 구조적 → 모든 기능에 영향
# - CCG-2 (V8 verdict 불일치): 정보성 → 개별 기능 추가 불필요
# - CCG-3 (module_id 미매핑): 구조적 → FT-MOD에 영향
# - GAP-SOT-2 (8개 SOT 미참조): STEP7 유래 기능이 이미 추출됨
# - GAP-PH1-1 (Feature Coverage 부재): V10이 해결 중
#
# 실제 "Registry에 아예 없는 기능"으로 추가해야 할 GAP은 없음.
# 모든 GAP은 기존 기능의 매핑 상태에 반영됨.

gap_features_added = 0
print(f"[STEP 1-c] New GAP features added: {gap_features_added} (모든 GAP은 구조적/카테고리 수준)")

# ══════════════════════════════════════════════════════════════════════
# STEP 2: part2_mapping_status 초기 상태 부여
# ══════════════════════════════════════════════════════════════════════

# V8/V9에서 검증 시도한 카테고리 → PRE_GAP (Phase 0-E에서 전부 GAP_FOUND)
v8_validated_categories = {"FT-MOD", "FT-API", "FT-SCHEMA", "FT-CFG"}

# V8 Agent 7이 검증한 특정 소스
v8_agent7_source = "D2.0-08"

# V9 SOT 매핑에서 PART2 미참조된 소스 (STEP7 계열)
v9_unreferenced_sources = {
    "STEP7_A-E", "STEP7_F-I", "STEP7_J-M", "STEP7_N-P", "STEP7_보강", "BGNR"
}

status_counts = Counter()

for f in features:
    cat = f.get("category", "")
    src = f.get("source_file", "")

    if f.get("_superseded"):
        f["part2_mapping_status"] = "NOT_APPLICABLE"
    elif cat in v8_validated_categories:
        # V8이 해당 카테고리를 검증했으나 Phase 0-E에서 GAP_FOUND
        f["part2_mapping_status"] = "PRE_GAP"
    elif src == v8_agent7_source and cat == "FT-UI":
        # V8 Agent 7이 D2.0-08 UI를 검증했으나 커버리지 부족
        f["part2_mapping_status"] = "PRE_GAP"
    elif src in v9_unreferenced_sources:
        # V9 SOT 매핑에서 PART2 미참조 소스
        f["part2_mapping_status"] = "PRE_GAP"
    else:
        f["part2_mapping_status"] = "UNKNOWN"

    # 공통 필드 추가
    f["part2_phase"] = None
    f["part2_line"] = None

    status_counts[f["part2_mapping_status"]] += 1

    # _superseded 임시 키 제거
    if "_superseded" in f:
        del f["_superseded"]

print(f"[STEP 2] Mapping status distribution: {dict(status_counts)}")

# ══════════════════════════════════════════════════════════════════════
# STEP 3: 통계 산출
# ══════════════════════════════════════════════════════════════════════

total = len(features)
ext_true = sum(1 for f in features if f.get("extractable") is True)
ext_false = sum(1 for f in features if f.get("extractable") is False)

# 버전별 분포 (단일 버전으로 정규화)
version_counter = Counter()
for f in features:
    vs = f.get("version_scope", "")
    for v in vs.split(","):
        v = v.strip()
        if v:
            version_counter[v] += 1

# 단순 버전 분포 (원본 scope 그대로)
version_scope_counter = Counter()
for f in features:
    version_scope_counter[f.get("version_scope", "")] += 1

# 카테고리별 분포
cat_counter = Counter()
for f in features:
    cat_counter[f.get("category", "")] += 1

# confidence 분포
conf_explicit = sum(1 for f in features if f.get("confidence") == "명시적")
conf_inferred = sum(1 for f in features if f.get("confidence") == "추론")

# implementation_type 분포
impl_counter = Counter()
for f in features:
    impl_counter[f.get("implementation_type", "")] += 1

# lock_count (is_lock 필드 기준)
lock_count = sum(1 for f in features if f.get("is_lock") is True)

stats = {
    "total_features": total,
    "extractable_true": ext_true,
    "extractable_false": ext_false,
    "by_version_inclusive": dict(sorted(version_counter.items())),
    "by_version_scope": dict(sorted(version_scope_counter.items(), key=lambda x: -x[1])),
    "by_category": dict(sorted(cat_counter.items())),
    "by_implementation_type": dict(sorted(impl_counter.items(), key=lambda x: -x[1])),
    "by_mapping_status": dict(sorted(status_counts.items(), key=lambda x: -x[1])),
    "confidence_explicit": conf_explicit,
    "confidence_inferred": conf_inferred,
    "confidence_inferred_ratio": f"{conf_inferred / total * 100:.1f}%",
    "lock_count": lock_count
}

print(f"\n[STEP 3] === 통계 ===")
print(f"  총 기능 항목: {total}")
print(f"  extractable: true={ext_true}, false={ext_false}")
print(f"  버전별(inclusive): {dict(sorted(version_counter.items()))}")
print(f"  카테고리별: {dict(sorted(cat_counter.items()))}")
print(f"  매핑 상태: {dict(status_counts)}")
print(f"  confidence 추론 비율: {conf_inferred}/{total} = {conf_inferred/total*100:.1f}%")
print(f"  LOCK: {lock_count}")

# ══════════════════════════════════════════════════════════════════════
# Output: v10_feature_registry_final.json
# ══════════════════════════════════════════════════════════════════════

output = {
    "_meta": {
        "version": "v10.1.0",
        "generated": str(date.today()),
        "pipeline_phase": "Phase 0-F",
        "conversation": 19,
        "description": "V10 최종 Feature Registry - Phase 1의 유일한 입력",
        "inputs": {
            "merged_features": "phase0-d/v10_merged_features.json (3943 → 제외 후 입력)",
            "v8_revalidation": "phase0-e/v10_v8_revalidation.json (5 targets, 17 gaps)",
            "v9_revalidation": "phase0-e/v10_v9_revalidation.json (4 targets, 10 gaps)",
            "user_judgment": "phase0-d/v10_step4_judgment_report.json (include=19, exclude=2)"
        },
        "processing": {
            "step1_exclude_count": excluded_count,
            "step1_exclude_ids": sorted(exclude_ids),
            "step1_superseded_count": superseded_count,
            "step1_gap_features_added": gap_features_added,
            "step1_gap_note": "Phase 0-E GAP은 모두 구조적/카테고리 수준이므로 개별 기능 추가 불필요. 매핑 상태로 반영",
            "step2_mapping_rules": {
                "PRE_GAP": "V8 검증 카테고리(FT-MOD/API/SCHEMA/CFG) + V8 Agent7(D2.0-08 FT-UI) + V9 미참조 소스(STEP7/BGNR) → Phase 0-E에서 전부 GAP_FOUND",
                "NOT_APPLICABLE": "SUPERSEDED 기능",
                "UNKNOWN": "나머지 전체 (Phase 1에서 PART2 매핑 확인 필요)"
            }
        },
        "statistics": stats,
        "phase0e_gaps_summary": {
            "v8_gaps": 17,
            "v9_gaps": 10,
            "total_gaps": 27,
            "critical_cross_cutting": [
                "CCG-1: phase_assignment 전역 부재 (3943개)",
                "CCG-2: V8 상위 보고-verdict 불일치 (IMP-C/D)",
                "CCG-3: module_id 매핑 부재 (FT-MOD 244개)",
                "V9-CCG-1: Feature Coverage 검증 전면 부재",
                "V9-CCG-2: SOT→PART2 역방향 검증 미수행 (STEP7 1544개)",
                "V9-CCG-3: V9 REAL_ERROR 미해결 항목의 V10 영향",
                "V9-CCG-4: PART2 v21.0.0 changelog 미존재"
            ]
        }
    },
    "features": features
}

out_path = f"{BASE}/phase0-f/v10_feature_registry_final.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n[OUTPUT] {out_path}")
print(f"[OUTPUT] {total} features written")
