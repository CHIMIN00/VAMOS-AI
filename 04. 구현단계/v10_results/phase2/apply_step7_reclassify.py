#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""STEP7 재분류 결과 적용: 3-1에서 24건 제거, Step 2로 이동"""

import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

PHASE2 = r"D:\VAMOS\04. 구현단계\v10_results\phase2"

# 이동 대상 24건 ID
MOVE_IDS = [
    "S7AE-490", "S7AE-493", "S7AE-495", "S7AE-497", "S7AE-498",
    "S7AE-501", "S7AE-502", "S7AE-503", "S7AE-505", "S7AE-506",
    "S7AE-508", "S7AE-510", "S7AE-511", "S7AE-512", "S7AE-513",
    "S7AE-514", "S7AE-520", "S7AE-521", "S7AE-524", "S7AE-527",
    "S7AE-529", "S7AE-530", "S7AE-532", "S7AE-535",
]

# ID → 이동 사유 매핑
MOVE_REASONS = {}
with open(f"{PHASE2}\\step7_reclassify_result.json", "r", encoding="utf-8") as f:
    result = json.load(f)
for item in result["후보_목록"]:
    MOVE_REASONS[item["id"]] = {
        "orig_id": item["orig_id"],
        "내용": item["내용"],
        "reason": item["reason"],
        "in_r1": item["in_r1"],
        "in_r2": item["in_r2"],
    }

# === 1) 3-1 파일에서 24건 제거 ===
na_path = f"{PHASE2}\\step1\\3-1_NOT_APPLICABLE.md"
with open(na_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# 각 항목의 시작/끝 인덱스 파악
sections = []  # [(start_idx, end_idx, item_id), ...]
i = 0
while i < len(lines):
    m = re.match(r'^### (S7AE-\d+)', lines[i].strip())
    if m:
        item_id = m.group(1)
        start = i
        # --- 구분선까지가 한 항목
        end = i + 1
        while end < len(lines):
            if lines[end].strip() == "---":
                end += 1  # --- 포함
                break
            end += 1
        sections.append((start, end, item_id))
        i = end
    else:
        i += 1

# 제거할 라인 범위 수집
remove_ranges = []
removed_items = []
for start, end, item_id in sections:
    if item_id in MOVE_IDS:
        remove_ranges.append((start, end))
        removed_items.append(item_id)

# 역순으로 제거 (인덱스 꼬임 방지)
remove_ranges.sort(reverse=True)
for start, end in remove_ranges:
    # 시작 전 빈 줄도 제거
    while start > 0 and lines[start-1].strip() == "":
        start -= 1
    del lines[start:end]

# 요약 건수 업데이트: "48건" → "24건"
new_count = 48 - len(removed_items)
for i, line in enumerate(lines):
    if "48건" in line:
        lines[i] = line.replace("48건", f"{new_count}건")
        break

with open(na_path, "w", encoding="utf-8") as f:
    f.writelines(lines)

print(f"3-1 NOT_APPLICABLE: {len(removed_items)}건 제거 → 남은 {new_count}건")

# === 2) Step 2 보고서에 이동 항목 추가 ===
step2_path = f"{PHASE2}\\step2_unclassified_report.md"

# Step 2 파일 끝에 추가
additions = []
additions.append("\n\n---\n\n")
additions.append("## 3차 재검토 이동분 (STEP7 SOT 보강 후 재분류)\n\n")
additions.append(f"> **재검토일**: 2026-03-10\n")
additions.append(f"> **사유**: AI기술보강 폴더의 STEP7 개별 카테고리 가이드 + R1/R2 라운드 파일 SOT 반영 후,\n")
additions.append(f"> R1(V1+CRITICAL) 또는 R2(V1+HIGH)에 구현 상세가 있는 항목이 NOT_APPLICABLE로 분류되어 있던 24건 이동\n\n")
additions.append(f"### 이동 항목: {len(removed_items)}건\n\n")
additions.append("| ID | 원래 ID | 내용 | R1/R2 | 이동 사유 |\n")
additions.append("|-----|---------|------|-------|----------|\n")

for sid in sorted(removed_items):
    info = MOVE_REASONS.get(sid, {})
    orig = info.get("orig_id", "-")
    desc = info.get("내용", "-")
    r_flag = "R1(CRITICAL)" if info.get("in_r1") else "R2(HIGH)"
    reason = "구현 상세 존재, NOT_APPLICABLE 부적절"
    additions.append(f"| {sid} | {orig} | {desc} | {r_flag} | {reason} |\n")

with open(step2_path, "a", encoding="utf-8") as f:
    f.writelines(additions)

print(f"Step 2 보고서: {len(removed_items)}건 추가 완료")

# === 3) 수치 요약 ===
print(f"\n=== 최종 수치 ===")
print(f"Step 1 NOT_APPLICABLE: 48 → {new_count}건 (-{len(removed_items)})")
print(f"Step 1 SUB_FEATURE: 102건 (변동 없음)")
print(f"Step 1 SKIP_CONFIRMED: 10건 (변동 없음)")
print(f"Step 1 RESOLVED: 10건 (변동 없음)")
print(f"Step 1 SECTION6: 1건 (변동 없음)")
print(f"Step 1 DUPLICATE: 1건 (변동 없음)")
step1_total = new_count + 102 + 10 + 10 + 1 + 1
print(f"Step 1 합계: {step1_total}건")
step2_total = 896 + len(removed_items)
print(f"Step 2 합계: 896 + {len(removed_items)} = {step2_total}건")
print(f"전체: {step1_total + step2_total}건 (1,068건 확인)")
