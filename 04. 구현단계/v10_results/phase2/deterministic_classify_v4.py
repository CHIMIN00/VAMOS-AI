#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VAMOS v10 Phase 2 - Deterministic Classification v4 (FINAL)

확정 기준:
- PART2에 해당 feature의 '고유 키워드'가 명시적으로 존재하면 SUB_FEATURE
- 고유 키워드 = 영문 3글자+, 한글 3글자+, 코드명, 약어
- 일반적 2글자 한글은 매칭 불인정 (맥락 없는 일치 방지)
- 부모 모듈만 존재하고 해당 feature 미언급 → REAL_GAP
- step7_inferred 제거 (암묵적 커버 불인정)
- kor2_multi 제거 (맥락 없는 일반어 매칭 불인정)
"""

import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

PART2_PATH = r"D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md"
CONSOLIDATED_PATH = r"D:\VAMOS\04. 구현단계\v10_results\phase2\consolidated_missing.json"
OUTPUT_PATH = r"D:\VAMOS\04. 구현단계\v10_results\phase2\deterministic_result.json"

with open(PART2_PATH, "r", encoding="utf-8") as f:
    part2_text = f.read()
    part2_lower = part2_text.lower()

with open(CONSOLIDATED_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

items = data["items"]
print(f"Total items: {len(items)}")

# ─── PART2 섹션 경계 ────────────────────────────────────
part2_lines = part2_text.split('\n')
sec_starts = {}
for i, line in enumerate(part2_lines):
    m = re.match(r'^# (\d+)[\.\s]', line)
    if m:
        sec_starts[int(m.group(1))] = i

s2 = sec_starts.get(2, 0)
s6 = sec_starts.get(6, 0)
s7 = sec_starts.get(7, len(part2_lines))

text_s25 = '\n'.join(part2_lines[s2:s6]).lower()
text_s6 = '\n'.join(part2_lines[s6:s7]).lower()
print(f"§2-5: {s6-s2} lines | §6: {s7-s6} lines")

# ─── 모듈 ID 추출 ────────────────────────────────────────
module_ids = set()
for m in re.finditer(r'\b([IESABCD]-\d{1,2}|EVX-\d)\b', part2_text):
    module_ids.add(m.group(1))
print(f"Module IDs in PART2: {len(module_ids)}")

# ─── 스톱워드 ────────────────────────────────────────────
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

STOP_ENG = {
    'py','js','ts','md','json','yaml','toml','the','and','for','with','from',
    'this','that','all','new','add','use','is','in','to','of','on','at','by',
    'as','or','an','it','be','do','so','no','up','api','app','get','set',
    'run','log','max','min','key','src','cfg','err','msg','req','res','url',
    'env','cmd','arg','val','len','str','int','obj','def','cls','init',
}

# ─── SKIP 패턴 ──────────────────────────────────────────
SKIP_PATS = [r"로드맵",r"마일스톤",r"WBS",r"일정표",r"조직도",r"인력\s*배치",
             r"채용",r"마케팅",r"영업",r"GTM",r"비즈니스\s*모델",r"수익\s*모델"]

# ─── 검색 ───────────────────────────────────────────────
def in_s25(kw): return kw.lower() in text_s25
def in_s6(kw): return kw.lower() in text_s6
def in_part2(kw): return kw.lower() in part2_lower

# ─── 키워드 추출 ────────────────────────────────────────
def extract_specific_keywords(fname):
    """고유 키워드만 추출 (일반어 제외)"""
    kws = set()

    # 모듈 ID
    for m in re.finditer(r'\b([IESABCD]-\d{1,2}|EVX-\d)\b', fname):
        kws.add(("MID", m.group(1)))

    # 코드명 (AR-L3, LOCK-AT-004, VAMOS-XXXX 등)
    for m in re.finditer(r'[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+', fname):
        kws.add(("CODE", m.group()))

    # 대문자 약어 3글자+ (QoD, SDAR, MoA, SHAP, LIME, OAuth 등)
    for m in re.finditer(r'\b([A-Z][A-Za-z]*[A-Z][A-Za-z]*)\b', fname):
        if len(m.group()) >= 3:
            kws.add(("ABBR", m.group()))

    # 영문 3글자+ (스톱워드 제외)
    for m in re.finditer(r'\b([A-Za-z][A-Za-z0-9_]{2,})\b', fname):
        tok = m.group()
        if tok.lower() not in STOP_ENG and len(tok) >= 3:
            kws.add(("ENG", tok))

    # 한글 3글자+ (스톱워드 제외)
    for m in re.finditer(r'([가-힣]+)', fname):
        tok = m.group()
        if len(tok) >= 3 and tok not in STOP_KOR:
            kws.add(("KOR3", tok))

    # 괄호 안 고유 용어
    for m in re.finditer(r'[（(]([^)）]+)[)）]', fname):
        for tok in re.split(r'[/·,+→\s<>~=]+', m.group(1)):
            tok = tok.strip()
            if re.match(r'^[A-Za-z]{3,}', tok) and tok.lower() not in STOP_ENG:
                kws.add(("PENG", tok))
            elif re.match(r'^[가-힣]{3,}$', tok) and tok not in STOP_KOR:
                kws.add(("PKOR", tok))

    return kws

# ─── 분류 ───────────────────────────────────────────────
def classify(item):
    fid = item["feature_id"]
    fname = item["feature_name"]

    r = {
        "feature_id": fid,
        "feature_name": fname,
        "version_scope": item.get("version_scope", ""),
        "severity": item.get("severity", ""),
        "substatus": None,
        "match_type": "",
        "evidence": [],
    }

    # Fixed rules
    if item.get("status") == "RESOLVED":
        r["substatus"] = "RESOLVED"; return r
    if item.get("suggested_phase","").startswith("NOT_APPLICABLE"):
        r["substatus"] = "NOT_APPLICABLE"; return r
    if fid == "D207-108":
        r["substatus"] = "DUPLICATE"; r["evidence"]=["=AINV-056"]; return r

    # SKIP
    for p in SKIP_PATS:
        if re.search(p, fname, re.IGNORECASE):
            r["substatus"] = "SKIP_CONFIRMED"; r["evidence"]=[p]; return r

    # 키워드 추출
    kws = extract_specific_keywords(fname)

    if not kws:
        r["substatus"] = "REAL_GAP"
        r["match_type"] = "no_keywords"
        r["evidence"] = ["feature_name에서 고유 키워드 추출 불가"]
        return r

    # Level 1: 모듈 ID 직접 매칭
    for typ, val in kws:
        if typ == "MID" and val in module_ids:
            r["substatus"] = "SUB_FEATURE_OF_EXISTING"
            r["match_type"] = "module_id"
            r["evidence"] = [val]
            return r

    # Level 2: 고유 키워드 §2-5 매칭
    matched_s25 = []
    for typ, val in kws:
        if typ in ("ENG","ABBR","CODE","PENG","KOR3","PKOR"):
            if in_s25(val):
                matched_s25.append(val)

    if matched_s25:
        r["substatus"] = "SUB_FEATURE_OF_EXISTING"
        r["match_type"] = "keyword_s25"
        r["evidence"] = matched_s25[:5]
        return r

    # Level 3: 고유 키워드 §6 매칭
    matched_s6 = []
    for typ, val in kws:
        if typ in ("ENG","ABBR","CODE","PENG","KOR3","PKOR"):
            if in_s6(val):
                matched_s6.append(val)

    if matched_s6:
        r["substatus"] = "SECTION6_DETAILED"
        r["match_type"] = "keyword_s6"
        r["evidence"] = matched_s6[:5]
        return r

    # Level 4: §7 매칭
    matched_s7 = []
    for typ, val in kws:
        if typ in ("ENG","ABBR","CODE","PENG","KOR3","PKOR"):
            if in_part2(val) and not in_s25(val) and not in_s6(val):
                matched_s7.append(val)

    if matched_s7:
        r["substatus"] = "SUB_FEATURE_OF_EXISTING"
        r["match_type"] = "keyword_s7"
        r["evidence"] = matched_s7[:5]
        return r

    # Level 5: source_section 기반 §6 참조
    src = item.get("source_section", "")
    if src and len(src) > 3:
        # source_section에서 참조하는 내용이 §6에 있는지
        src_terms = re.findall(r'[A-Za-z]{3,}|[가-힣]{3,}', src)
        for st in src_terms:
            if st not in STOP_KOR and st.lower() not in STOP_ENG:
                if in_s6(st):
                    r["substatus"] = "SECTION6_DETAILED"
                    r["match_type"] = "source_section"
                    r["evidence"] = [src[:50]]
                    return r

    # No match → REAL_GAP
    r["substatus"] = "REAL_GAP"
    r["match_type"] = "no_specific_match"
    unmatched = [val for typ, val in kws][:5]
    r["evidence"] = unmatched
    return r

# ─── 실행 ───────────────────────────────────────────────
print("\nClassifying...")
results = []
for item in items:
    results.append(classify(item))

# ─── 통계 출력 ──────────────────────────────────────────
stats = {}
for r in results:
    stats[r["substatus"]] = stats.get(r["substatus"], 0) + 1

print("\n" + "="*60)
print("v4 FINAL DETERMINISTIC CLASSIFICATION")
print("="*60)
for k, v in sorted(stats.items(), key=lambda x: -x[1]):
    print(f"  {k:30s}: {v:5d}")
print(f"  {'TOTAL':30s}: {sum(stats.values()):5d}")

# match_type 분포
mt = {}
for r in results:
    key = f"{r['substatus']}|{r['match_type']}"
    mt[key] = mt.get(key, 0) + 1

print("\n=== MATCH TYPE ===")
for k, v in sorted(mt.items()):
    print(f"  {k:50s}: {v:4d}")

# REAL_GAP 분석
rgs = [r for r in results if r["substatus"] == "REAL_GAP"]
sev_cnt = {}
ver_cnt = {}
for rg in rgs:
    sev_cnt[rg["severity"]] = sev_cnt.get(rg["severity"], 0) + 1
    ver_cnt[rg["version_scope"]] = ver_cnt.get(rg["version_scope"], 0) + 1

print(f"\n=== REAL_GAP ({len(rgs)}) by Severity ===")
for k in ["BLOCKER","HIGH","MEDIUM","LOW"]:
    if k in sev_cnt:
        print(f"  {k}: {sev_cnt[k]}")

print(f"\n=== REAL_GAP by Version ===")
for k, v in sorted(ver_cnt.items()):
    print(f"  {k}: {v}")

# REAL_GAP 전체 목록
sev_order = {"BLOCKER":0,"HIGH":1,"MEDIUM":2,"LOW":3}
rgs_sorted = sorted(rgs, key=lambda x: (sev_order.get(x["severity"],9), x["feature_id"]))

print(f"\n=== ALL REAL_GAP ITEMS ({len(rgs)}) ===")
for rg in rgs_sorted:
    ev = ", ".join(str(e) for e in rg["evidence"][:3])
    print(f"  [{rg['severity']:7s}] [{rg['version_scope']:6s}] {rg['feature_id']:12s} {rg['feature_name'][:60]}  unmatched:[{ev}]")

# ─── 결과 저장 ──────────────────────────────────────────
output = {
    "_meta": {
        "method": "deterministic_v4_FINAL",
        "date": "2026-03-10",
        "part2_version": "v22.0.0",
        "criteria": {
            "core_rule": "PART2에 feature의 고유 키워드(영문3+/한글3+/코드명/약어) 0건 → REAL_GAP",
            "match_levels": [
                "L1: module_id (I-XX, E-XX 등)",
                "L2: 고유 키워드 §2-§5",
                "L3: 고유 키워드 §6",
                "L4: 고유 키워드 §7",
                "L5: source_section §6 참조"
            ],
            "excluded": "step7_inferred(부모 모듈 추론), kor2_multi(2글자 일반어), compound_phrase",
            "stopwords_excluded": "2글자 한글 일반어 86개 + 영문 스톱워드 60개"
        },
    },
    "statistics": stats,
    "real_gap_count": len(rgs),
    "real_gap_by_severity": sev_cnt,
    "real_gap_by_version": ver_cnt,
    "real_gap_items": [
        {"feature_id": r["feature_id"], "feature_name": r["feature_name"],
         "severity": r["severity"], "version_scope": r["version_scope"],
         "unmatched_keywords": r["evidence"]}
        for r in rgs_sorted
    ],
    "items": results,
}

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nSaved: {OUTPUT_PATH}")
print("DONE.")
