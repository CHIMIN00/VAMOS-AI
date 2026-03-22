#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VAMOS v10 Phase 2 - Step 2: UNCLASSIFIED 721건 상세 리포트

각 미분류 항목에 대해:
1. 왜 분류가 안 됐는지 (키워드 추출 실패? 매칭 실패?)
2. 추출된 키워드 목록
3. PART2에서 가장 가까운 관련 내용
4. 분류 불가 사유 카테고리
"""

import json
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

PART2_PATH = r"D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md"
STEP1_PATH = r"D:\VAMOS\04. 구현단계\v10_results\phase2\step1_result.json"
REPORT_PATH = r"D:\VAMOS\04. 구현단계\v10_results\phase2\step2_unclassified_report.json"
REPORT_TXT_PATH = r"D:\VAMOS\04. 구현단계\v10_results\phase2\step2_unclassified_report.md"

# ─── 파일 로드 ──────────────────────────────────────────
with open(PART2_PATH, "r", encoding="utf-8") as f:
    part2_text = f.read()
    part2_lines = part2_text.split('\n')
    part2_lower = part2_text.lower()

with open(STEP1_PATH, "r", encoding="utf-8") as f:
    step1 = json.load(f)

unclassified = step1["unclassified_items"]
print(f"Unclassified items: {len(unclassified)}")

# ─── PART2 섹션 경계 ────────────────────────────────────
sec_starts = {}
for i, line in enumerate(part2_lines):
    m = re.match(r'^# (\d+)[\.\s]', line)
    if m:
        sec_num = int(m.group(1))
        if sec_num not in sec_starts:
            sec_starts[sec_num] = i

s2 = sec_starts.get(2, 0)
s6 = sec_starts.get(6, 0)
s7 = sec_starts.get(7, len(part2_lines))

text_s25 = '\n'.join(part2_lines[s2:s6]).lower()
text_s6 = '\n'.join(part2_lines[s6:s7]).lower()
text_s7 = '\n'.join(part2_lines[s7:]).lower()

# ─── 일반 스톱워드 ──────────────────────────────────────
STOP_KOR = {
    "구현","시스템","모듈","기능","패턴","방식","처리","관리","기반","자동",
    "설정","항목","단계","전체","기본","확장","추가","적용","지원","연동",
    "통합","정의","생성","등록","수행","실행","결과","데이터","정보","상태",
    "제공","사용","진행","완료","필요","포함","대상","목록","내용","유형",
    "파일","코드","함수","클래스","로직","프로세스","상세","검증","확인",
    "동작","테스트","개발","작업","요청","응답","방법","원리","조건","규칙",
    "옵션","전략","구조","형식","선택","변환","분석","최적화","활성화","비활성화",
    "가이드","보강","추정","다국어","표준","명시","명령","권한","수준","엔진",
}

# ─── 분류 불가 사유 분석 ─────────────────────────────────
def analyze_unclassified(item):
    """왜 분류 안 됐는지 상세 분석"""
    fname = item["feature_name"]
    match_type = item["match_type"]
    evidence = item["evidence"]

    analysis = {
        "feature_id": item["feature_id"],
        "feature_name": fname,
        "severity": item["severity"],
        "version_scope": item["version_scope"],
        "source_section": item.get("source_section", ""),
        "action": item.get("action", ""),
        "failure_reason": "",
        "failure_category": "",
        "extracted_keywords": [],
        "all_kor_tokens": [],
        "kor2_tokens": [],       # 2글자 한글 (Step1에서 제외됨)
        "kor3_tokens": [],       # 3글자 한글 (Step1에서 제외됨)
        "kor2_in_part2": [],     # 2글자 한글 중 PART2에 있는 것
        "kor3_in_part2": [],     # 3글자 한글 중 PART2에 있는 것
        "nearest_context": "",
    }

    # 한글 토큰 전수 추출
    kor_all = re.findall(r'[가-힣]+', fname)
    analysis["all_kor_tokens"] = kor_all

    kor2 = [k for k in kor_all if len(k) == 2 and k not in STOP_KOR]
    kor3 = [k for k in kor_all if len(k) == 3 and k not in STOP_KOR]
    analysis["kor2_tokens"] = kor2
    analysis["kor3_tokens"] = kor3

    # 한글 2-3글자 중 PART2에 실제로 있는 것
    kor2_found = []
    for k in kor2:
        sections = []
        if k in text_s25: sections.append("§2-5")
        if k in text_s6: sections.append("§6")
        if k in text_s7: sections.append("§7")
        if sections:
            kor2_found.append(f"{k}({','.join(sections)})")
    analysis["kor2_in_part2"] = kor2_found

    kor3_found = []
    for k in kor3:
        sections = []
        if k in text_s25: sections.append("§2-5")
        if k in text_s6: sections.append("§6")
        if k in text_s7: sections.append("§7")
        if sections:
            kor3_found.append(f"{k}({','.join(sections)})")
    analysis["kor3_in_part2"] = kor3_found

    analysis["extracted_keywords"] = evidence

    if match_type == "no_strong_keywords":
        analysis["failure_reason"] = "feature_name에서 고유 키워드를 추출할 수 없음 (영문3+자/한글4+자 없음)"
        if kor2_found or kor3_found:
            analysis["failure_category"] = "KOR_SHORT_ONLY"
            analysis["failure_reason"] += f" | 한글 2-3글자 {len(kor2_found)+len(kor3_found)}개가 PART2에 존재하나 Step1 기준 미충족"
        elif kor2 or kor3:
            analysis["failure_category"] = "KOR_SHORT_NO_MATCH"
            analysis["failure_reason"] += f" | 한글 2-3글자 {len(kor2)+len(kor3)}개 추출했으나 PART2에 없음"
        else:
            analysis["failure_category"] = "PURE_GENERIC"
            analysis["failure_reason"] += " | 스톱워드만으로 구성된 feature_name"
    elif match_type == "no_match":
        analysis["failure_reason"] = f"키워드 {len(evidence)}개 추출했으나 PART2 §2-6에서 매칭 안 됨"
        # §7에는 있는지 확인
        s7_found = []
        for ev in evidence:
            typ_val = ev.split(":", 1)
            if len(typ_val) == 2:
                val = typ_val[1]
                if val.lower() in text_s7:
                    s7_found.append(val)
        if s7_found:
            analysis["failure_category"] = "S7_ONLY"
            analysis["failure_reason"] += f" | §7에서 {len(s7_found)}개 발견: {s7_found[:3]}"
        elif kor2_found or kor3_found:
            analysis["failure_category"] = "KOR_SHORT_SUPPLEMENT"
            analysis["failure_reason"] += f" | 한글 2-3글자 {len(kor2_found)+len(kor3_found)}개가 PART2에 존재"
        else:
            analysis["failure_category"] = "TRUE_GAP"
            analysis["failure_reason"] += " | PART2 전체에서 관련 키워드 미발견"

    return analysis

# ─── 전체 분석 ──────────────────────────────────────────
print("Analyzing unclassified items...")
analyses = []
for item in unclassified:
    analyses.append(analyze_unclassified(item))

# ─── 카테고리별 통계 ────────────────────────────────────
cat_cnt = Counter(a["failure_category"] for a in analyses)
print("\n" + "=" * 60)
print("UNCLASSIFIED FAILURE CATEGORIES")
print("=" * 60)
for k, v in cat_cnt.most_common():
    print(f"  {k:25s}: {v:5d}")
print(f"  {'TOTAL':25s}: {len(analyses):5d}")

# severity별
print("\n=== By Severity ===")
for sev in ["BLOCKER", "HIGH", "MEDIUM", "LOW"]:
    items_sev = [a for a in analyses if a["severity"] == sev]
    if items_sev:
        cats = Counter(a["failure_category"] for a in items_sev)
        print(f"\n  {sev} ({len(items_sev)}):")
        for k, v in cats.most_common():
            print(f"    {k}: {v}")

# ─── MD 리포트 생성 ─────────────────────────────────────
print("\nGenerating markdown report...")

lines = []
lines.append("# VAMOS v10 Phase 2 - Step 2: 미분류 항목 상세 리포트")
lines.append("")
lines.append(f"- 일시: 2026-03-10")
lines.append(f"- 전체 항목: 1,068건")
lines.append(f"- Step 1 분류 완료: {1068 - len(analyses)}건")
lines.append(f"- 미분류(UNCLASSIFIED): {len(analyses)}건")
lines.append("")

lines.append("## 1. 미분류 사유 카테고리")
lines.append("")
lines.append("| 카테고리 | 건수 | 설명 |")
lines.append("|---------|------|------|")

cat_desc = {
    "KOR_SHORT_ONLY": "영문/한글4+자 키워드 없지만, 한글 2-3글자가 PART2에 존재",
    "KOR_SHORT_NO_MATCH": "한글 2-3글자만 추출됐으나 PART2에도 없음",
    "PURE_GENERIC": "스톱워드만으로 구성 (고유 키워드 추출 불가)",
    "KOR_SHORT_SUPPLEMENT": "영문 키워드 매칭 실패했으나, 한글 2-3글자가 PART2에 존재",
    "S7_ONLY": "키워드가 §7(마무리)에만 존재",
    "TRUE_GAP": "PART2 전체에서 관련 키워드 미발견 (진짜 GAP 가능성 높음)",
}

for k, v in cat_cnt.most_common():
    desc = cat_desc.get(k, "")
    lines.append(f"| {k} | {v} | {desc} |")
lines.append(f"| **TOTAL** | **{len(analyses)}** | |")
lines.append("")

# 카테고리별 상세
sev_order = {"BLOCKER": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}

for cat_name in ["TRUE_GAP", "S7_ONLY", "PURE_GENERIC", "KOR_SHORT_ONLY", "KOR_SHORT_SUPPLEMENT", "KOR_SHORT_NO_MATCH"]:
    cat_items = [a for a in analyses if a["failure_category"] == cat_name]
    if not cat_items:
        continue

    cat_items.sort(key=lambda x: (sev_order.get(x["severity"], 9), x["feature_id"]))

    lines.append(f"## 2. {cat_name} ({len(cat_items)}건)")
    lines.append("")
    lines.append(f"> {cat_desc.get(cat_name, '')}")
    lines.append("")

    for a in cat_items:
        lines.append(f"### {a['feature_id']}")
        lines.append(f"- **Feature**: {a['feature_name']}")
        lines.append(f"- **Severity**: {a['severity']} | **Version**: {a['version_scope']}")
        lines.append(f"- **Action**: {a['action']}")
        lines.append(f"- **사유**: {a['failure_reason']}")

        if a["extracted_keywords"]:
            kw_str = ", ".join(str(k) for k in a["extracted_keywords"][:8])
            lines.append(f"- **추출 키워드**: {kw_str}")

        if a["kor2_in_part2"]:
            lines.append(f"- **한글2자(PART2 존재)**: {', '.join(a['kor2_in_part2'])}")
        if a["kor3_in_part2"]:
            lines.append(f"- **한글3자(PART2 존재)**: {', '.join(a['kor3_in_part2'])}")

        if a["kor2_tokens"] and not a["kor2_in_part2"]:
            lines.append(f"- **한글2자(미매칭)**: {', '.join(a['kor2_tokens'][:5])}")
        if a["kor3_tokens"] and not a["kor3_in_part2"]:
            lines.append(f"- **한글3자(미매칭)**: {', '.join(a['kor3_tokens'][:5])}")

        lines.append("")

report_text = "\n".join(lines)

with open(REPORT_TXT_PATH, "w", encoding="utf-8") as f:
    f.write(report_text)

# ─── JSON 저장 ──────────────────────────────────────────
output = {
    "_meta": {
        "method": "step2_unclassified_analysis",
        "date": "2026-03-10",
        "total_unclassified": len(analyses),
    },
    "category_statistics": dict(cat_cnt),
    "severity_breakdown": {},
    "items": analyses,
}

for sev in ["BLOCKER", "HIGH", "MEDIUM", "LOW"]:
    items_sev = [a for a in analyses if a["severity"] == sev]
    if items_sev:
        output["severity_breakdown"][sev] = {
            "count": len(items_sev),
            "categories": dict(Counter(a["failure_category"] for a in items_sev)),
        }

with open(REPORT_PATH, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nJSON: {REPORT_PATH}")
print(f"MD:   {REPORT_TXT_PATH}")
print("DONE.")
