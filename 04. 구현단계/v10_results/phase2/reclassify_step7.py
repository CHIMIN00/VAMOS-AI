#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""STEP7 ID 기반 Step 1/2 재분류 재검토

새로 추가된 STEP7 개별 카테고리 가이드 + R1/R2 라운드 파일 기반으로
기존 Step 1 분류(NOT_APPLICABLE, SUB_FEATURE)의 유효성을 검증한다.

재검토 기준:
1. R1(V1+CRITICAL) 또는 R2(V1+HIGH)에 구현 상세가 있는 항목이
   NOT_APPLICABLE 또는 SUB_FEATURE로 분류되어 있으면 → 재검토 대상
2. 개별 카테고리 가이드에서 PART2 키워드 커버 범위를 초과하는 구현 요구가 있으면 → 재검토 대상
"""

import re
import json
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

SOT = r"D:\VAMOS\docs\sot"
PHASE2 = r"D:\VAMOS\04. 구현단계\v10_results\phase2"

# --- 1) R1, R2 파일에서 STEP7 ID 추출 ---
def extract_r_ids(filepath):
    """R1/R2 파일에서 S7 관련 ID 추출"""
    ids = set()
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    # 패턴: S7-A-001, S7B-002, S7F-001, A-ADD-01 등
    for m in re.finditer(r'\bS7[A-Z]?-?[A-Z]*-?\d{2,3}[a-z]?\b', text):
        ids.add(m.group())
    # A-ADD 패턴
    for m in re.finditer(r'\bA-ADD-\d{2,3}[a-z]?\b', text):
        ids.add(m.group())
    return ids

# --- 2) Step 1 파일에서 STEP7 ID와 분류 추출 ---
def extract_step1_ids(filepath, classification):
    """Step 1 MD 파일에서 ### ID 패턴으로 추출"""
    items = {}
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    current_id = None
    current_data = {}
    for line in lines:
        # ### S7AE-307 형태
        m = re.match(r'^### (S7[A-Z]{2}-\d+)', line.strip())
        if m:
            if current_id and current_id.startswith("S7"):
                items[current_id] = current_data
            current_id = m.group(1)
            current_data = {"classification": classification, "file": filepath}
        if current_id:
            if line.strip().startswith("- **내용**:"):
                current_data["내용"] = line.strip().replace("- **내용**:", "").strip()
            if line.strip().startswith("- **Severity**:"):
                current_data["severity_version"] = line.strip().replace("- **Severity**:", "").strip()
            if line.strip().startswith("- **판정 사유**:"):
                current_data["판정사유"] = line.strip().replace("- **판정 사유**:", "").strip()
            if line.strip().startswith("- **Evidence**:"):
                current_data["evidence"] = line.strip().replace("- **Evidence**:", "").strip()

    if current_id and current_id.startswith("S7"):
        items[current_id] = current_data

    return items

# --- 3) Step 2 파일에서 STEP7 ID 추출 ---
def extract_step2_ids(filepath):
    """Step 2 MD에서 S7 ID 추출"""
    items = {}
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    current_id = None
    current_data = {}
    for line in lines:
        # ### S7AE-307 또는 | S7AE-307 | 형태
        m = re.match(r'^### (S7[A-Z]{2}-\d+)', line.strip())
        if not m:
            m = re.match(r'^\| (S7[A-Z]{2}-\d+) \|', line.strip())
        if m:
            if current_id and current_id.startswith("S7"):
                items[current_id] = current_data
            current_id = m.group(1)
            current_data = {"classification": "Step2_미분류", "file": filepath}
        if current_id:
            if line.strip().startswith("- **내용**:"):
                current_data["내용"] = line.strip().replace("- **내용**:", "").strip()
            elif line.strip().startswith("- **Severity**:"):
                current_data["severity_version"] = line.strip().replace("- **Severity**:", "").strip()

    if current_id and current_id.startswith("S7"):
        items[current_id] = current_data

    return items

# --- 4) 카테고리 가이드에서 개별 항목 상세 추출 ---
def extract_category_detail(filepath, prefix):
    """카테고리 가이드에서 개별 항목 ID와 설명 추출"""
    items = {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        return items

    # S7F-001, S7G-001 등의 패턴
    pattern = re.compile(rf'\b({prefix}-\d{{3}})\b')
    for m in pattern.finditer(text):
        item_id = m.group(1)
        # ID 주변 컨텍스트 추출 (±200자)
        start = max(0, m.start() - 50)
        end = min(len(text), m.end() + 200)
        context = text[start:end].replace("\n", " ").strip()
        items[item_id] = context

    return items

# --- 5) consolidated_missing.json에서 S7 ID 매핑 확인 ---
def load_consolidated():
    """consolidated_missing.json에서 전체 STEP7 항목 로드"""
    cpath = os.path.join(PHASE2, "consolidated_missing.json")
    if not os.path.exists(cpath):
        # 대안 경로
        cpath = os.path.join(r"D:\VAMOS\04. 구현단계\v10_results\phase0-e", "consolidated_missing.json")

    items = {}
    try:
        with open(cpath, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            for item in data:
                fid = item.get("feature_id", "")
                if fid.startswith("S7"):
                    items[fid] = item
        elif isinstance(data, dict):
            for fid, item in data.items():
                if fid.startswith("S7"):
                    items[fid] = item
    except Exception as e:
        print(f"Warning: Could not load consolidated_missing.json: {e}")

    return items

# === MAIN ===
print("=" * 70)
print("STEP7 ID 재분류 재검토 스크립트")
print("=" * 70)

# R1, R2 ID 추출
r1_ids = extract_r_ids(os.path.join(SOT, "STEP7_R1_V1_CRITICAL.md"))
r2_ids = extract_r_ids(os.path.join(SOT, "STEP7_R2_V1_HIGH.md"))
print(f"\nR1 (V1+CRITICAL) IDs: {len(r1_ids)}건")
print(f"R2 (V1+HIGH) IDs: {len(r2_ids)}건")

# Step 1 STEP7 ID 추출
step1_files = {
    "NOT_APPLICABLE": os.path.join(PHASE2, "step1", "3-1_NOT_APPLICABLE.md"),
    "SUB_FEATURE": os.path.join(PHASE2, "step1", "3-2_SUB_FEATURE_OF_EXISTING.md"),
    "SKIP_CONFIRMED": os.path.join(PHASE2, "step1", "3-3_SKIP_CONFIRMED.md"),
    "RESOLVED": os.path.join(PHASE2, "step1", "3-4_RESOLVED.md"),
    "SECTION6": os.path.join(PHASE2, "step1", "3-5_SECTION6_DETAILED.md"),
    "DUPLICATE": os.path.join(PHASE2, "step1", "3-6_DUPLICATE.md"),
}

all_step1 = {}
for cls, fpath in step1_files.items():
    if os.path.exists(fpath):
        ids = extract_step1_ids(fpath, cls)
        all_step1.update(ids)
        print(f"Step 1 {cls}: {len(ids)}건 (S7 only)")

# Step 2 추출
step2_path = os.path.join(PHASE2, "step2_unclassified_report.md")
step2_ids = {}
if os.path.exists(step2_path):
    step2_ids = extract_step2_ids(step2_path)
    print(f"Step 2 미분류: {len(step2_ids)}건 (S7 only)")

# 카테고리별 가이드 상세 로드
category_guides = {
    "S7B": os.path.join(SOT, "STEP7-B_대화프로세스_작업가이드.md"),
    "S7C": os.path.join(SOT, "STEP7-C_UI_UX_전수비교_작업가이드.md"),
    "S7D": os.path.join(SOT, "STEP7-D_메모리_저장소_아키텍처_작업가이드.md"),
    "S7E": os.path.join(SOT, "STEP7-E_보안_안전_거버넌스_작업가이드.md"),
    "S7F": os.path.join(SOT, "STEP7-F_인프라_배포_MLOps_작업가이드.md"),
    "S7G": os.path.join(SOT, "STEP7-G_벤치마크_평가_품질보증_작업가이드.md"),
    "S7H": os.path.join(SOT, "STEP7-H_비즈니스모델_시장전략_작업가이드.md"),
    "S7I": os.path.join(SOT, "STEP7-I_AI_Investing_보강_작업가이드.md"),
    "S7J": os.path.join(SOT, "STEP7-J_멀티모달_생성처리_작업가이드.md"),
    "S7K": os.path.join(SOT, "STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md"),
    "S7L": os.path.join(SOT, "STEP7-L_개발자도구_API_SDK_작업가이드.md"),
    "S7M": os.path.join(SOT, "STEP7-M_PKM_지식관리_작업가이드.md"),
    "S7N": os.path.join(SOT, "STEP7-N_워크플로우자동화_RPA_작업가이드.md"),
    "S7O": os.path.join(SOT, "STEP7-O_교육_학습_자기개발_작업가이드.md"),
    "S7P": os.path.join(SOT, "STEP7-P_건강_웰니스_감성AI_작업가이드.md"),
}

guide_details = {}
for prefix, fpath in category_guides.items():
    details = extract_category_detail(fpath, prefix)
    guide_details.update(details)
    if details:
        print(f"카테고리 {prefix} 가이드: {len(details)}건 개별 항목")

# === 재검토 로직 ===
print("\n" + "=" * 70)
print("재검토 결과")
print("=" * 70)

# 매핑: S7AE -> S7C/S7D/S7E 등 (A-E 통합파일의 원래 카테고리)
# S7AE 접두사는 A-E 통합 파일에서 온 것으로, 내용의 S7C/S7D 접두사로 원래 카테고리 추정
def get_original_category_id(item_id, item_data):
    """S7AE-xxx 형태에서 원래 카테고리 ID 추출 (내용에서)"""
    desc = item_data.get("내용", "")
    # "S7C-045 음성 모드" → S7C-045
    m = re.search(r'(S7[A-Z]-\d{3})', desc)
    if m:
        return m.group(1)
    # "D-035 데이터설계" → S7D (STEP7-D 카테고리)
    m = re.search(r'D-(\d{3})', desc)
    if m:
        return f"S7D-{m.group(1)}"
    return None

# R1/R2에 있는데 Step 1 NOT_APPLICABLE인 항목 체크
reclassify_candidates = []

for sid, data in all_step1.items():
    cls = data.get("classification", "")
    desc = data.get("내용", "")

    # 원래 카테고리 ID 추출
    orig_id = get_original_category_id(sid, data)

    # R1/R2 교차 확인 (원래 ID 기반)
    in_r1 = False
    in_r2 = False
    if orig_id:
        # R1/R2의 ID 형태는 S7D-001, S7C-045 등이 아니라
        # S7-D-001, S7C-045 등 다양할 수 있음
        for rid in r1_ids:
            if orig_id.replace("S7", "S7-") == rid or orig_id == rid:
                in_r1 = True
                break
        for rid in r2_ids:
            if orig_id.replace("S7", "S7-") == rid or orig_id == rid:
                in_r2 = True
                break

    # 카테고리 가이드에 상세 있는지 확인
    has_guide_detail = orig_id in guide_details if orig_id else False

    # 재분류 판단
    reason = None
    if cls == "NOT_APPLICABLE":
        if in_r1:
            reason = f"R1(V1+CRITICAL)에 구현 상세 존재. NOT_APPLICABLE 부적절 → Step 2 이동 권고"
        elif in_r2:
            reason = f"R2(V1+HIGH)에 구현 상세 존재. NOT_APPLICABLE 부적절 → Step 2 이동 권고"

    elif cls == "SUB_FEATURE":
        # SUB_FEATURE는 PART2에 키워드가 있어서 상위 구현에 포함된다고 판정
        # 그러나 카테고리 가이드에 PART2 범위를 초과하는 상세 구현이 있으면 재검토
        if in_r1:
            reason = f"R1(V1+CRITICAL)에 독립 구현 항목으로 등재. SUB_FEATURE가 아닌 독립 구현 → Step 2 이동 권고"

    if reason:
        reclassify_candidates.append({
            "id": sid,
            "orig_id": orig_id,
            "classification": cls,
            "내용": desc,
            "severity": data.get("severity_version", ""),
            "reason": reason,
            "in_r1": in_r1,
            "in_r2": in_r2,
        })

# 결과 출력
print(f"\n### 재분류 후보: {len(reclassify_candidates)}건")
print()

if reclassify_candidates:
    # NOT_APPLICABLE → Step 2
    na_to_step2 = [c for c in reclassify_candidates if c["classification"] == "NOT_APPLICABLE"]
    sub_to_step2 = [c for c in reclassify_candidates if c["classification"] == "SUB_FEATURE"]

    if na_to_step2:
        print(f"## NOT_APPLICABLE → Step 2 이동 후보: {len(na_to_step2)}건")
        for c in na_to_step2:
            print(f"  {c['id']} ({c['orig_id']}) | {c['내용']} | {c['reason']}")
        print()

    if sub_to_step2:
        print(f"## SUB_FEATURE → Step 2 이동 후보: {len(sub_to_step2)}건")
        for c in sub_to_step2:
            print(f"  {c['id']} ({c['orig_id']}) | {c['내용']} | {c['reason']}")
        print()
else:
    print("재분류 대상 없음 — 기존 분류 유지")

# 추가: Step 2의 S7 항목 중 새 가이드로 분류 가능한 항목
print(f"\n### Step 2 미분류 S7 항목 재검토: {len(step2_ids)}건")
step2_classifiable = []
for sid, data in step2_ids.items():
    orig_id = get_original_category_id(sid, data)
    has_guide = orig_id in guide_details if orig_id else False

    # 직접 매핑 시도
    if not has_guide:
        # S7AE-456 → S7D-001 같은 매핑
        desc = data.get("내용", "")
        for gid in guide_details:
            if gid in desc:
                has_guide = True
                orig_id = gid
                break

    if has_guide:
        step2_classifiable.append({
            "id": sid,
            "orig_id": orig_id,
            "내용": data.get("내용", ""),
            "guide_context": guide_details.get(orig_id, "")[:100]
        })

if step2_classifiable:
    print(f"카테고리 가이드에 상세 존재하는 항목: {len(step2_classifiable)}건")
    for c in step2_classifiable[:20]:  # 처음 20건만 출력
        print(f"  {c['id']} ({c['orig_id']}) | {c['내용']}")
else:
    print("카테고리 가이드로 추가 분류 가능한 항목 없음")

# === 최종 요약 ===
print("\n" + "=" * 70)
print("최종 요약")
print("=" * 70)
total_s7 = len(all_step1) + len(step2_ids)
print(f"전체 STEP7 ID: {total_s7}건")
print(f"  Step 1: {len(all_step1)}건")
print(f"  Step 2: {len(step2_ids)}건")
print(f"  재분류 후보: {len(reclassify_candidates)}건")
print(f"    NOT_APPLICABLE → Step 2: {len([c for c in reclassify_candidates if c['classification'] == 'NOT_APPLICABLE'])}건")
print(f"    SUB_FEATURE → Step 2: {len([c for c in reclassify_candidates if c['classification'] == 'SUB_FEATURE'])}건")

# 결과를 JSON으로도 저장
output = {
    "재검토일": "2026-03-10",
    "전체_STEP7_ID": total_s7,
    "Step1_S7": len(all_step1),
    "Step2_S7": len(step2_ids),
    "재분류_후보": len(reclassify_candidates),
    "후보_목록": reclassify_candidates
}

outpath = os.path.join(PHASE2, "step7_reclassify_result.json")
with open(outpath, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print(f"\n결과 저장: {outpath}")
