#!/usr/bin/env python3
"""
Phase 0-D: STEP 0, 1, 2 — CLAUDE.md ↔ SRC 교차 검증 (Delta)
- STEP 0: JSON 키 정규화 검증
- STEP 1: Layer 1 only (CLAUDE.md에 있지만 SRC에 없는 항목)
- STEP 2: Layer 2 only (SRC에 있지만 CLAUDE.md에 없는 항목)
"""

import json
import os
import re
import sys
import io
from difflib import SequenceMatcher
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ── 경로 설정 ──
PHASE0B = r"D:\VAMOS\04. 구현단계\v10_results\phase0-b"
PHASE0C = r"D:\VAMOS\04. 구현단계\v10_results\phase0-c"
OUTPUT  = r"D:\VAMOS\04. 구현단계\v10_results\phase0-d"

LAYER1_FILE = os.path.join(PHASE0B, "v10_layer1_claude_features.json")

SRC_FILES = [
    "v10_src_C01a.json",
    "v10_src_C01b.json",
    "v10_src_C02_overview_orange.json",
    "v10_src_C03_blue_infra_wf.json",
    "v10_src_C04.json",
    "v10_src_C05.json",
    "v10_src_C06.json",
    "v10_src_C07.json",
    "v10_src_C08.json",
    "v10_src_C09a.json",
    "v10_src_C09b.json",
    "v10_src_C10_beginner_claude.json",
]

# ── 필수 feature 키 (snake_case 공통 템플릿) ──
REQUIRED_KEYS = [
    "feature_id",
    "source_file",
    "source_line",
    "source_section",
    "feature_name",
    "version_scope",
    "category",
    "implementation_type",
    "dependencies",
    "extractable",
    "confidence",
    "notes",
]

# ── 키 이름 매핑 (흔한 오타/변형 → 표준) ──
KEY_ALIASES = {
    "featureId": "feature_id",
    "feature-id": "feature_id",
    "id": "feature_id",
    "sourceFile": "source_file",
    "source-file": "source_file",
    "sourceLine": "source_line",
    "source-line": "source_line",
    "sourceSection": "source_section",
    "source-section": "source_section",
    "featureName": "feature_name",
    "feature-name": "feature_name",
    "name": "feature_name",
    "versionScope": "version_scope",
    "version-scope": "version_scope",
    "implementationType": "implementation_type",
    "implementation-type": "implementation_type",
    "impl_type": "implementation_type",
}


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def normalize_key(k):
    """키를 snake_case 표준으로 변환"""
    if k in KEY_ALIASES:
        return KEY_ALIASES[k]
    # camelCase → snake_case
    s1 = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', k)
    result = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', s1).lower()
    result = result.replace("-", "_")
    return result


def similarity(a, b):
    """두 문자열의 유사도 (0~1)"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def normalize_feature_name(name):
    """비교용 정규화: 공백/특수문자 제거, 소문자"""
    n = name.lower().strip()
    n = re.sub(r'[^\w가-힣]', ' ', n)
    n = re.sub(r'\s+', ' ', n).strip()
    return n


# ══════════════════════════════════════════════════════════════
# STEP 0: JSON 키 정규화 검증
# ══════════════════════════════════════════════════════════════
print("=" * 70)
print("STEP 0: JSON 키 정규화 검증 (W-24 방어)")
print("=" * 70)

step0_report = {
    "step": "STEP 0",
    "description": "JSON 키 정규화 검증",
    "files_checked": [],
    "issues": [],
    "auto_fixes": [],
    "missing_fields": [],
}

all_files_to_check = [(LAYER1_FILE, "Layer1")] + [
    (os.path.join(PHASE0C, f), f) for f in SRC_FILES
]

all_layer1_features = []
all_layer2_features = []

for filepath, label in all_files_to_check:
    data = load_json(filepath)
    features = data.get("features", [])

    file_report = {
        "file": label,
        "total_features": len(features),
        "key_issues": [],
        "missing_required": [],
        "fixes_applied": [],
    }

    for i, feat in enumerate(features):
        fid = feat.get("feature_id", f"UNKNOWN-{i}")

        # 키 정규화 확인
        original_keys = list(feat.keys())
        normalized_feat = {}
        for k, v in feat.items():
            nk = normalize_key(k)
            if nk != k:
                issue = {
                    "feature_id": fid,
                    "original_key": k,
                    "normalized_to": nk,
                }
                file_report["key_issues"].append(issue)
                file_report["fixes_applied"].append(issue)
            normalized_feat[nk] = v

        # 필수 키 누락 확인
        for rk in REQUIRED_KEYS:
            if rk not in normalized_feat:
                file_report["missing_required"].append({
                    "feature_id": fid,
                    "missing_key": rk,
                })

        # 정규화된 feature로 교체
        features[i] = normalized_feat

    # 파일에 반영 (자동 수정)
    if any(file_report["key_issues"]) or any(file_report["missing_required"]):
        data["features"] = features
        save_json(data, filepath)

    step0_report["files_checked"].append(file_report)

    if file_report["key_issues"]:
        step0_report["auto_fixes"].extend(file_report["key_issues"])
    if file_report["missing_required"]:
        step0_report["missing_fields"].extend(file_report["missing_required"])

    # features 수집
    if label == "Layer1":
        all_layer1_features = features
    else:
        for feat in features:
            feat["_src_agent_file"] = label
        all_layer2_features.extend(features)

    print(f"  [{label}] features={len(features)}, "
          f"key_issues={len(file_report['key_issues'])}, "
          f"missing={len(file_report['missing_required'])}")

print(f"\n  총 Layer1 features: {len(all_layer1_features)}")
print(f"  총 Layer2 features: {len(all_layer2_features)}")
print(f"  키 이슈 수: {len(step0_report['auto_fixes'])}")
print(f"  필수 필드 누락 수: {len(step0_report['missing_fields'])}")

if step0_report["missing_fields"]:
    print("\n  [경고] 필수 필드 누락 항목:")
    for mf in step0_report["missing_fields"][:20]:
        print(f"    - {mf['feature_id']}: {mf['missing_key']}")
    if len(step0_report["missing_fields"]) > 20:
        print(f"    ... 외 {len(step0_report['missing_fields'])-20}건")


# ══════════════════════════════════════════════════════════════
# STEP 1: Layer 1에만 있고 Layer 2에 없는 항목
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("STEP 1: Layer 1 only (CLAUDE.md에 있지만 SRC에 없는 항목)")
print("=" * 70)

# Layer 2 feature_name 정규화 목록 생성
l2_names_normalized = []
l2_features_map = {}
for feat in all_layer2_features:
    fn = feat.get("feature_name", "")
    nn = normalize_feature_name(fn)
    l2_names_normalized.append(nn)
    l2_features_map[nn] = feat

# 유사도 임계값
EXACT_THRESHOLD = 0.90   # 이 이상이면 "일치"로 판단
PARTIAL_THRESHOLD = 0.60  # 이 이상이면 "부분 일치 후보"

step1_results = {
    "step": "STEP 1",
    "description": "Layer 1 only — CLAUDE.md에서 추출했지만 SRC 어디에서도 추출되지 않은 기능",
    "layer1_only": [],       # SRC 추출 누락 후보
    "matched": [],           # Layer 2에서 대응 항목 발견
    "partial_matches": [],   # 부분 일치 (수동 확인 필요)
    "excluded_abbreviations": [],  # CLAUDE.md 축약 기능으로 제외
}

# 축약 기능 판별용 키워드
ABBREVIATION_INDICATORS = [
    "전체", "모든", "각종", "등", "기타", "포함",
    "구현 (", "V0,V1,V2,V3",
]

for l1_feat in all_layer1_features:
    l1_name = l1_feat.get("feature_name", "")
    l1_norm = normalize_feature_name(l1_name)
    l1_id = l1_feat.get("feature_id", "")

    # 축약 기능 판별: 매우 포괄적 이름 + 버전 범위가 전체
    is_abbreviation = False
    # 너무 짧은 이름은 축약이 아님
    if len(l1_name) > 5:
        for ind in ABBREVIATION_INDICATORS:
            if ind in l1_name and len(l1_name) < 20:
                is_abbreviation = True
                break

    best_score = 0
    best_match = None
    top_candidates = []

    for l2_feat in all_layer2_features:
        l2_name = l2_feat.get("feature_name", "")
        l2_norm = normalize_feature_name(l2_name)

        score = similarity(l1_norm, l2_norm)

        if score > best_score:
            best_score = score
            best_match = l2_feat

        if score >= PARTIAL_THRESHOLD:
            top_candidates.append({
                "l2_feature_id": l2_feat.get("feature_id", ""),
                "l2_feature_name": l2_name,
                "l2_source_file": l2_feat.get("source_file", ""),
                "l2_agent_file": l2_feat.get("_src_agent_file", ""),
                "similarity": round(score, 3),
            })

    top_candidates.sort(key=lambda x: x["similarity"], reverse=True)
    top_candidates = top_candidates[:5]  # 상위 5개만

    entry = {
        "feature_id": l1_id,
        "feature_name": l1_name,
        "source_section": l1_feat.get("source_section", ""),
        "version_scope": l1_feat.get("version_scope", ""),
        "category": l1_feat.get("category", ""),
        "best_match_score": round(best_score, 3),
        "best_match_l2_id": best_match.get("feature_id", "") if best_match else "",
        "best_match_l2_name": best_match.get("feature_name", "") if best_match else "",
    }

    if best_score >= EXACT_THRESHOLD:
        entry["top_candidates"] = top_candidates[:1]
        step1_results["matched"].append(entry)
    elif best_score >= PARTIAL_THRESHOLD:
        entry["top_candidates"] = top_candidates
        step1_results["partial_matches"].append(entry)
    else:
        if is_abbreviation:
            entry["exclusion_reason"] = "CLAUDE.md 축약 기능 (포괄적 표현)"
            step1_results["excluded_abbreviations"].append(entry)
        else:
            entry["top_candidates"] = top_candidates
            step1_results["layer1_only"].append(entry)

print(f"  Layer 1 총 항목: {len(all_layer1_features)}")
print(f"  ├─ Layer 2와 일치 (≥{EXACT_THRESHOLD}): {len(step1_results['matched'])}")
print(f"  ├─ 부분 일치 ({PARTIAL_THRESHOLD}~{EXACT_THRESHOLD}): {len(step1_results['partial_matches'])}")
print(f"  ├─ Layer 1 only (SRC 누락 후보): {len(step1_results['layer1_only'])}")
print(f"  └─ 축약 기능 제외: {len(step1_results['excluded_abbreviations'])}")

if step1_results["layer1_only"]:
    print(f"\n  [Layer 1 only — SRC 추출 누락 후보]")
    for item in step1_results["layer1_only"]:
        print(f"    {item['feature_id']}: {item['feature_name'][:60]}")
        if item.get("top_candidates"):
            best = item["top_candidates"][0]
            print(f"      └ 가장 유사: {best['l2_feature_id']} ({best['similarity']}) "
                  f"{best['l2_feature_name'][:50]}")


# ══════════════════════════════════════════════════════════════
# STEP 2: Layer 2에만 있고 Layer 1에 없는 항목
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("STEP 2: Layer 2 only (SRC에 있지만 CLAUDE.md에 없는 항목)")
print("=" * 70)

# Layer 1 feature_name 정규화 목록
l1_names_normalized = []
for feat in all_layer1_features:
    fn = feat.get("feature_name", "")
    nn = normalize_feature_name(fn)
    l1_names_normalized.append(nn)

step2_results = {
    "step": "STEP 2",
    "description": "Layer 2 only — SRC에서 추출했지만 CLAUDE.md에 없는 기능",
    "layer2_only": [],
    "layer2_only_lock": [],  # LOCK 관련 → CLAUDE.md 미기재 플래그
    "matched": [],
    "partial_matches": [],
}

for l2_feat in all_layer2_features:
    l2_name = l2_feat.get("feature_name", "")
    l2_norm = normalize_feature_name(l2_name)
    l2_id = l2_feat.get("feature_id", "")
    l2_notes = l2_feat.get("notes", "")

    is_lock = "LOCK" in str(l2_notes).upper() or "LOCK" in str(l2_name).upper()

    best_score = 0
    best_match = None
    top_candidates = []

    for l1_feat in all_layer1_features:
        l1_name = l1_feat.get("feature_name", "")
        l1_norm = normalize_feature_name(l1_name)

        score = similarity(l2_norm, l1_norm)

        if score > best_score:
            best_score = score
            best_match = l1_feat

        if score >= PARTIAL_THRESHOLD:
            top_candidates.append({
                "l1_feature_id": l1_feat.get("feature_id", ""),
                "l1_feature_name": l1_name,
                "similarity": round(score, 3),
            })

    top_candidates.sort(key=lambda x: x["similarity"], reverse=True)
    top_candidates = top_candidates[:3]

    entry = {
        "feature_id": l2_id,
        "feature_name": l2_name,
        "source_file": l2_feat.get("source_file", ""),
        "agent_file": l2_feat.get("_src_agent_file", ""),
        "version_scope": l2_feat.get("version_scope", ""),
        "category": l2_feat.get("category", ""),
        "best_match_score": round(best_score, 3),
        "best_match_l1_id": best_match.get("feature_id", "") if best_match else "",
        "best_match_l1_name": best_match.get("feature_name", "") if best_match else "",
        "is_lock": is_lock,
    }

    if best_score >= EXACT_THRESHOLD:
        step2_results["matched"].append(entry)
    elif best_score >= PARTIAL_THRESHOLD:
        entry["top_candidates"] = top_candidates
        step2_results["partial_matches"].append(entry)
    else:
        entry["top_candidates"] = top_candidates
        if is_lock:
            entry["flag"] = "CLAUDE.md 미기재 LOCK 항목"
            step2_results["layer2_only_lock"].append(entry)
        else:
            step2_results["layer2_only"].append(entry)

print(f"  Layer 2 총 항목: {len(all_layer2_features)}")
print(f"  ├─ Layer 1과 일치 (≥{EXACT_THRESHOLD}): {len(step2_results['matched'])}")
print(f"  ├─ 부분 일치 ({PARTIAL_THRESHOLD}~{EXACT_THRESHOLD}): {len(step2_results['partial_matches'])}")
print(f"  ├─ Layer 2 only (정상 — SRC가 더 상세): {len(step2_results['layer2_only'])}")
print(f"  └─ Layer 2 only + LOCK (CLAUDE.md 미기재): {len(step2_results['layer2_only_lock'])}")

if step2_results["layer2_only_lock"]:
    print(f"\n  [LOCK 항목 — CLAUDE.md 미기재 플래그]")
    for item in step2_results["layer2_only_lock"]:
        print(f"    {item['feature_id']}: {item['feature_name'][:60]}")


# ══════════════════════════════════════════════════════════════
# 결과 저장
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("결과 저장")
print("=" * 70)

# _src_agent_file 키 제거 (내부용)
def clean_internal_keys(obj):
    if isinstance(obj, dict):
        return {k: clean_internal_keys(v) for k, v in obj.items() if k != "_src_agent_file"}
    elif isinstance(obj, list):
        return [clean_internal_keys(item) for item in obj]
    return obj

delta_output = {
    "meta": {
        "phase": "0-D",
        "steps": ["STEP 0", "STEP 1", "STEP 2"],
        "generated_date": "2026-03-08",
        "generator": "v10 Phase 0-D Agent (대화 14)",
        "layer1_source": LAYER1_FILE,
        "layer2_sources": SRC_FILES,
        "thresholds": {
            "exact_match": EXACT_THRESHOLD,
            "partial_match": PARTIAL_THRESHOLD,
        },
    },
    "statistics": {
        "layer1_total": len(all_layer1_features),
        "layer2_total": len(all_layer2_features),
        "step1": {
            "matched": len(step1_results["matched"]),
            "partial_matches": len(step1_results["partial_matches"]),
            "layer1_only": len(step1_results["layer1_only"]),
            "excluded_abbreviations": len(step1_results["excluded_abbreviations"]),
        },
        "step2": {
            "matched": len(step2_results["matched"]),
            "partial_matches": len(step2_results["partial_matches"]),
            "layer2_only": len(step2_results["layer2_only"]),
            "layer2_only_lock": len(step2_results["layer2_only_lock"]),
        },
    },
    "step0_normalization": step0_report,
    "step1_layer1_only": clean_internal_keys(step1_results),
    "step2_layer2_only": clean_internal_keys(step2_results),
}

output_path = os.path.join(OUTPUT, "v10_layer1_layer2_delta.json")
save_json(delta_output, output_path)
print(f"  → {output_path}")

# STEP 0 상세 리포트 별도 저장
step0_path = os.path.join(OUTPUT, "v10_step0_normalization_report.json")
save_json(step0_report, step0_path)
print(f"  → {step0_path}")

print("\n✓ Phase 0-D STEP 0, 1, 2 완료")
