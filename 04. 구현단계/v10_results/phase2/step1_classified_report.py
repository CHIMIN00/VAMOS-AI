#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VAMOS v10 Phase 2 - Step 1: 확실한 분류 347건 상세 리포트 생성
"""

import json
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

STEP1_PATH = r"D:\VAMOS\04. 구현단계\v10_results\phase2\step1_result.json"
REPORT_PATH = r"D:\VAMOS\04. 구현단계\v10_results\phase2\step1_classified_report.md"

with open(STEP1_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

classified = data["classified_items"]
print(f"Classified items: {len(classified)}")

# 그룹별 분류
groups = {}
for item in classified:
    s = item["substatus"]
    if s not in groups:
        groups[s] = []
    groups[s].append(item)

sev_order = {"BLOCKER": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}

lines = []
lines.append("# VAMOS v10 Phase 2 - Step 1: 확실한 분류 상세 리포트")
lines.append("")
lines.append(f"- 일시: 2026-03-10")
lines.append(f"- 전체 항목: 1,068건")
lines.append(f"- Step 1 분류 완료: {len(classified)}건")
lines.append(f"- 미분류(→Step 2): {1068 - len(classified)}건")
lines.append("")

# 요약 테이블
lines.append("## 1. 분류 요약")
lines.append("")
lines.append("| 분류(substatus) | 건수 | 분류 기준 | 신뢰도 |")
lines.append("|----------------|------|----------|--------|")

desc_map = {
    "NOT_APPLICABLE": ("suggested_phase=NOT_APPLICABLE (STEP7 TITLE_ONLY)", "100%"),
    "SUB_FEATURE_OF_EXISTING": ("PART2 §2-5에 고유 키워드 직접 매칭", "100%"),
    "SKIP_CONFIRMED": ("원본 데이터 action=SKIP 필드", "100%"),
    "RESOLVED": ("원본 데이터 status=RESOLVED 필드", "100%"),
    "SECTION6_DETAILED": ("PART2 §6에 고유 키워드 직접 매칭", "100%"),
    "DUPLICATE": ("D207-108 = AINV-056 하드코딩", "100%"),
}

order = ["NOT_APPLICABLE", "SUB_FEATURE_OF_EXISTING", "SKIP_CONFIRMED",
         "RESOLVED", "SECTION6_DETAILED", "DUPLICATE"]

for s in order:
    items = groups.get(s, [])
    desc, conf = desc_map.get(s, ("", ""))
    lines.append(f"| {s} | {len(items)} | {desc} | {conf} |")
lines.append(f"| **TOTAL** | **{len(classified)}** | | |")
lines.append("")

# match_type 상세
lines.append("## 2. Match Type 상세 분포")
lines.append("")
mt_cnt = Counter(item["match_type"] for item in classified)
lines.append("| Match Type | 건수 | 설명 |")
lines.append("|-----------|------|------|")
mt_desc = {
    "suggested_phase": "suggested_phase 필드가 NOT_APPLICABLE으로 시작",
    "action_reclassify": "action 필드가 RECLASSIFY_NA",
    "status_field": "status 필드가 RESOLVED",
    "action_skip": "action 필드가 SKIP",
    "hardcoded": "하드코딩 규칙 (D207-108=AINV-056)",
    "module_id_exact": "feature_name에 모듈 ID(I-XX, E-XX 등)가 있고 PART2에 동일 ID 존재",
    "eng_keyword_s25": "영문 3+자 고유 키워드가 PART2 §2-5에 word-boundary 매칭",
    "kor4_keyword_s25": "한글 4+자 고유 키워드가 PART2 §2-5에 매칭",
    "eng_keyword_s6": "영문 3+자 고유 키워드가 PART2 §6에 word-boundary 매칭",
    "kor4_keyword_s6": "한글 4+자 고유 키워드가 PART2 §6에 매칭",
}
for mt, cnt in sorted(mt_cnt.items(), key=lambda x: -x[1]):
    desc = mt_desc.get(mt, "")
    lines.append(f"| {mt} | {cnt} | {desc} |")
lines.append("")

# 각 그룹별 전수 목록
for s in order:
    items = groups.get(s, [])
    if not items:
        continue

    items.sort(key=lambda x: (sev_order.get(x.get("severity",""), 9), x["feature_id"]))

    lines.append(f"## 3-{order.index(s)+1}. {s} ({len(items)}건)")
    lines.append("")

    if s == "NOT_APPLICABLE":
        lines.append("> 구현 범위 밖 항목 (STEP7 TITLE_ONLY 등). PART2 반영 불필요.")
    elif s == "SUB_FEATURE_OF_EXISTING":
        lines.append("> PART2에 이미 존재하는 모듈/기능의 하위 기능. 별도 추가 불필요.")
    elif s == "SKIP_CONFIRMED":
        lines.append("> 원본 검토 시 SKIP으로 판정된 항목. 구현 범위 밖.")
    elif s == "RESOLVED":
        lines.append("> 이전 단계에서 이미 해결 완료된 항목.")
    elif s == "SECTION6_DETAILED":
        lines.append("> §6(시스템 횡단 상세)에 이미 기술된 항목.")
    elif s == "DUPLICATE":
        lines.append("> 다른 항목과 중복.")
    lines.append("")

    for item in items:
        lines.append(f"### {item['feature_id']}")
        lines.append(f"- **Feature**: {item['feature_name']}")
        sev = item.get('severity', '')
        ver = item.get('version_scope', '')
        if sev or ver:
            lines.append(f"- **Severity**: {sev} | **Version**: {ver}")
        lines.append(f"- **Match Type**: {item['match_type']}")
        if item.get("evidence"):
            ev_str = ", ".join(str(e) for e in item["evidence"][:5])
            lines.append(f"- **Evidence**: {ev_str}")
        lines.append("")

report_text = "\n".join(lines)

with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write(report_text)

print(f"Report saved: {REPORT_PATH}")
print(f"Total lines: {len(lines)}")
print("DONE.")
