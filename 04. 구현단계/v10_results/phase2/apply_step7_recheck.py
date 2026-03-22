#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""4차 재검토: STEP7 작업가이드 대조 결과 적용
- 3-1 NOT_APPLICABLE 24건 전부 제거 → Step 2 이동
- 3-2 SUB_FEATURE 5건 제거 → Step 2 이동
"""

import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

PHASE2 = r"D:\VAMOS\04. 구현단계\v10_results\phase2"

# ============================================================
# 1) 3-1 NOT_APPLICABLE: 24건 전부 제거
# ============================================================
na_path = f"{PHASE2}\\step1\\3-1_NOT_APPLICABLE.md"
with open(na_path, "r", encoding="utf-8") as f:
    na_lines = f.readlines()

# 모든 ### 항목 ID 추출
na_sections = []
i = 0
while i < len(na_lines):
    m = re.match(r'^### (S7AE-\d+)', na_lines[i].strip())
    if m:
        item_id = m.group(1)
        start = i
        end = i + 1
        while end < len(na_lines):
            if na_lines[end].strip() == "---":
                end += 1
                break
            end += 1
        na_sections.append((start, end, item_id))
        i = end
    else:
        i += 1

print(f"3-1에서 발견된 항목: {len(na_sections)}건")
na_removed = [s[2] for s in na_sections]

# 3-1 내용 수집 (Step 2 이동용)
na_items_data = {}
for start, end, item_id in na_sections:
    block = na_lines[start:end]
    # 내용 추출
    content = ""
    severity = ""
    for line in block:
        if line.strip().startswith("- **내용**:"):
            content = line.strip().replace("- **내용**: ", "")
        if line.strip().startswith("- **Severity**:"):
            severity = line.strip().replace("- **Severity**: ", "")
    na_items_data[item_id] = {"내용": content, "severity": severity}

# 3-1 파일을 헤더만 남기고 비우기 (0건)
new_na = []
new_na.append("# Step 1 확정: 3-1 NOT_APPLICABLE (0건)\n")
new_na.append("\n")
new_na.append("> **Phase**: v10 Phase 2 Step 1 (4차 재검토 반영)\n")
new_na.append("> **생성일**: 2026-03-10\n")
new_na.append("> **4차 재검토**: STEP7-D 작업가이드 대조 결과, 24건 전부 구현 상세 존재 → Step 2 이동\n")
new_na.append("\n")
new_na.append("---\n")
new_na.append("\n")
new_na.append("## 결과\n")
new_na.append("\n")
new_na.append("4차 재검토(STEP7 카테고리별 작업가이드 대조)에서 잔여 24건 전부 이동 완료.\n")
new_na.append("\n")
new_na.append("- 원래 48건 중 24건: 3차 재검토(R1/R2 SOT 반영)에서 Step 2 이동\n")
new_na.append("- 나머지 24건: 4차 재검토(STEP7-D 작업가이드 대조)에서 Step 2 이동\n")
new_na.append("- **최종 NOT_APPLICABLE: 0건**\n")

with open(na_path, "w", encoding="utf-8") as f:
    f.writelines(new_na)

print(f"3-1 NOT_APPLICABLE: 24건 제거 → 0건")

# ============================================================
# 2) 3-2 SUB_FEATURE: 5건 제거
# ============================================================
sf_path = f"{PHASE2}\\step1\\3-2_SUB_FEATURE_OF_EXISTING.md"
with open(sf_path, "r", encoding="utf-8") as f:
    sf_lines = f.readlines()

MOVE_FROM_SF = ["S7AE-307", "S7AE-375", "S7FI-082", "S7JM-103", "S7JM-105"]

# 각 항목 섹션 파악
sf_sections = []
i = 0
while i < len(sf_lines):
    m = re.match(r'^### ([A-Z0-9][\w-]+)', sf_lines[i].strip())
    if m:
        item_id = m.group(1)
        start = i
        end = i + 1
        while end < len(sf_lines):
            if sf_lines[end].strip() == "---":
                end += 1
                break
            end += 1
        sf_sections.append((start, end, item_id))
        i = end
    else:
        i += 1

# 이동 대상 블록 수집 + 제거
sf_removed = []
sf_items_data = {}
remove_ranges = []
for start, end, item_id in sf_sections:
    if item_id in MOVE_FROM_SF:
        remove_ranges.append((start, end))
        sf_removed.append(item_id)
        block = sf_lines[start:end]
        content = ""
        severity = ""
        evidence = ""
        for line in block:
            if line.strip().startswith("- **내용**:"):
                content = line.strip().replace("- **내용**: ", "")
            if line.strip().startswith("- **Severity**:"):
                severity = line.strip().replace("- **Severity**: ", "")
            if line.strip().startswith("- **Evidence**:"):
                evidence = line.strip().replace("- **Evidence**: ", "")
        sf_items_data[item_id] = {"내용": content, "severity": severity, "evidence": evidence}

# 역순 제거
remove_ranges.sort(reverse=True)
for start, end in remove_ranges:
    while start > 0 and sf_lines[start-1].strip() == "":
        start -= 1
    del sf_lines[start:end]

# 건수 업데이트: "102건" → "97건"
new_sf_count = 102 - len(sf_removed)
for i, line in enumerate(sf_lines):
    if "102건" in line:
        sf_lines[i] = line.replace("102건", f"{new_sf_count}건")

# HIGH 건수 업데이트: 39건에서 이동 건수 차감
high_moved = sum(1 for sid in sf_removed if "HIGH" in sf_items_data.get(sid, {}).get("severity", ""))
for i, line in enumerate(sf_lines):
    if "39건" in line and "HIGH" in line:
        sf_lines[i] = line.replace("39건", f"{39 - high_moved}건")
        break

with open(sf_path, "w", encoding="utf-8") as f:
    f.writelines(sf_lines)

print(f"3-2 SUB_FEATURE: {len(sf_removed)}건 제거 → {new_sf_count}건")
for sid in sf_removed:
    print(f"  - {sid}: {sf_items_data[sid]['내용']}")

# ============================================================
# 3) Step 2 보고서에 이동 항목 추가
# ============================================================
step2_path = f"{PHASE2}\\step2_unclassified_report.md"

# S7D ID 매핑 (S7AE → D-xxx)
S7D_MAP = {
    "S7AE-491": ("S7D-036", "L1 단기 메모리"),
    "S7AE-492": ("S7D-037", "L2 프로젝트 메모리"),
    "S7AE-494": ("S7D-039", "L4 아카이브"),
    "S7AE-496": ("S7D-041", "강등/삭제 알고리즘"),
    "S7AE-499": ("S7D-044", "중복 제거"),
    "S7AE-500": ("S7D-045", "사용 통계"),
    "S7AE-504": ("S7D-049", "KV Cache vLLM"),
    "S7AE-507": ("S7D-052", "적중률 모니터링"),
    "S7AE-509": ("S7D-054", "캐시 프라이버시"),
    "S7AE-515": ("S7D-060", "Self-RAG 루프"),
    "S7AE-516": ("S7D-061", "CRAG 보정"),
    "S7AE-517": ("S7D-062", "4중 인덱스 융합"),
    "S7AE-518": ("S7D-063", "인덱스 자동 업데이트"),
    "S7AE-519": ("S7D-064", "RAGAS 품질 평가"),
    "S7AE-522": ("S7D-067", "로컬-클라우드 동기화"),
    "S7AE-523": ("S7D-068", "완전 삭제 GDPR"),
    "S7AE-525": ("S7D-070", "보존 정책"),
    "S7AE-526": ("S7D-071", "감사 로그 해시체인"),
    "S7AE-528": ("S7D-073", "멀티디바이스 E2EE"),
    "S7AE-531": ("S7D-076", "V2 예산 $40/월"),
    "S7AE-533": ("S7D-078", "V1→V2 마이그레이션"),
    "S7AE-534": ("S7D-079", "V2→V3 마이그레이션"),
    "S7AE-536": ("S7D-081", "불필요 데이터 정리"),
    "S7AE-537": ("S7D-082", "건강도 대시보드"),
}

# SUB_FEATURE 이동 사유 매핑
SF_GUIDE_MAP = {
    "S7AE-307": ("STEP7-D", "S7D-060", "Self-RAG 루프 구현 — 독립 구현 스펙 존재"),
    "S7AE-375": ("STEP7-E", "S7E-022", "OAuth2+MFA — 전용 보안 스펙 존재"),
    "S7FI-082": ("STEP7-F", "S7F-080", "SSL/TLS — Let's Encrypt+HSTS 전용 스펙"),
    "S7JM-103": ("STEP7-K", "K-005", "MCP Prompt 템플릿 — 전용 MCP 기능 스펙"),
    "S7JM-105": ("STEP7-K", "K-007", "MCP 보안 레이어 — 전용 MCP 보안 스펙"),
}

additions = []
additions.append("\n\n---\n\n")
additions.append("## 4차 재검토 이동분 (STEP7 카테고리별 작업가이드 대조)\n\n")
additions.append("> **재검토일**: 2026-03-10\n")
additions.append("> **사유**: STEP7 카테고리별 작업가이드(B~P) 파일에 구현 상세가 존재하는 항목이\n")
additions.append(">  NOT_APPLICABLE 또는 SUB_FEATURE로 분류되어 있던 건 이동\n\n")

# Part A: 3-1에서 이동한 24건
additions.append("### A. NOT_APPLICABLE → Step 2 이동: 24건\n\n")
additions.append("**근거**: STEP7-D_메모리_저장소_아키텍처_작업가이드.md에 24건 전부 구현 상세 존재\n\n")
additions.append("| S7AE ID | S7D ID | 내용 | STEP7-D 구현 상세 |\n")
additions.append("|---------|--------|------|-------------------|\n")

for sid in sorted(na_removed):
    info = na_items_data.get(sid, {})
    s7d = S7D_MAP.get(sid, ("-", "-"))
    desc = info.get("내용", "-")
    additions.append(f"| {sid} | {s7d[0]} | {desc} | {s7d[1]} |\n")

# Part B: 3-2에서 이동한 5건
additions.append(f"\n### B. SUB_FEATURE → Step 2 이동: {len(sf_removed)}건\n\n")
additions.append("**근거**: STEP7 카테고리별 작업가이드에 독립 구현 스펙 존재 (키워드 광범위 매칭으로 SUB_FEATURE 오분류)\n\n")
additions.append("| ID | 내용 | 가이드 파일 | 가이드 ID | 이동 사유 |\n")
additions.append("|-----|------|-----------|----------|----------|\n")

for sid in sorted(sf_removed):
    info = sf_items_data.get(sid, {})
    guide = SF_GUIDE_MAP.get(sid, ("-", "-", "-"))
    desc = info.get("내용", "-")
    additions.append(f"| {sid} | {desc} | {guide[0]} | {guide[1]} | {guide[2]} |\n")

with open(step2_path, "a", encoding="utf-8") as f:
    f.writelines(additions)

print(f"\nStep 2 보고서: {len(na_removed) + len(sf_removed)}건 추가 완료")

# ============================================================
# 4) 수치 요약
# ============================================================
print(f"\n=== 최종 수치 ===")
print(f"Step 1 NOT_APPLICABLE: 24 → 0건 (-24)")
print(f"Step 1 SUB_FEATURE: 102 → {new_sf_count}건 (-{len(sf_removed)})")
print(f"Step 1 SKIP_CONFIRMED: 10건 (변동 없음)")
print(f"Step 1 RESOLVED: 10건 (변동 없음)")
print(f"Step 1 SECTION6: 1건 (변동 없음)")
print(f"Step 1 DUPLICATE: 1건 (변동 없음)")
step1_total = 0 + new_sf_count + 10 + 10 + 1 + 1
print(f"Step 1 합계: {step1_total}건")
step2_total = 920 + len(na_removed) + len(sf_removed)
print(f"Step 2 합계: 920 + {len(na_removed)} + {len(sf_removed)} = {step2_total}건")
print(f"전체: {step1_total + step2_total}건 (1,068건 확인)")
