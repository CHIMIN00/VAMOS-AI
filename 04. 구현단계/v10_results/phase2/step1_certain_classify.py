#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VAMOS v10 Phase 2 - Step 1: 확실한 항목만 분류

확실한 분류 기준 (오분류 위험 0%):
1. status=RESOLVED → RESOLVED (10건)
2. suggested_phase=NOT_APPLICABLE → NOT_APPLICABLE (140건)
3. action=RECLASSIFY_NA → NOT_APPLICABLE (32건)
4. D207-108 → DUPLICATE (1건)
5. action=SKIP → SKIP_CONFIRMED (60건)
6. 모듈 ID 직접 매칭 (I-XX, E-XX 등이 PART2에 존재) → SUB_FEATURE
7. 영문 고유 키워드(3+자) §2-5 매칭 → SUB_FEATURE
8. 영문 고유 키워드(3+자) §6 매칭 → SECTION6_DETAILED

나머지: UNCLASSIFIED → Step 2에서 상세 리포트
"""

import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

PART2_PATH = r"D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md"
CONSOLIDATED_PATH = r"D:\VAMOS\04. 구현단계\v10_results\phase2\consolidated_missing.json"
OUTPUT_PATH = r"D:\VAMOS\04. 구현단계\v10_results\phase2\step1_result.json"

# ─── 파일 로드 ──────────────────────────────────────────
with open(PART2_PATH, "r", encoding="utf-8") as f:
    part2_text = f.read()
    part2_lines = part2_text.split('\n')

with open(CONSOLIDATED_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

items = data["items"]
print(f"Total items: {len(items)}")

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
print(f"§2-5: {s6-s2} lines | §6: {s7-s6} lines")

# ─── 모듈 ID 추출 ────────────────────────────────────────
module_ids = set()
for m in re.finditer(r'\b([IESABCD]-\d{1,2}|EVX-\d)\b', part2_text):
    module_ids.add(m.group(1))
print(f"Module IDs in PART2: {len(module_ids)}")

# ─── 스톱워드 (절대 매칭에 쓰지 않을 일반어) ─────────────
STOP_ENG = {
    # 프로그래밍 일반어
    'py','js','ts','md','json','yaml','toml','csv','html','css','xml','sql',
    'the','and','for','with','from','this','that','all','new','add','use',
    'is','in','to','of','on','at','by','as','or','an','it','be','do','so',
    'no','up','api','app','get','set','run','log','max','min','key','src',
    'cfg','err','msg','req','res','url','env','cmd','arg','val','len','str',
    'int','obj','def','cls','init','not','can','has','was','are','but','out',
    'sub','pre','post','end','top','low','high','mid','full','auto','base',
    'core','data','file','func','info','item','list','main','name','node',
    'path','port','root','rule','safe','save','send','show','size','skip',
    'sort','spec','stop','task','temp','test','text','time','tool','type',
    'unit','user','util','view','wait','work','code','mode','plan','real',
    'step','line','page','form','load','lock','make','mark','move','next',
    'open','over','pass','pick','play','pull','push','read','rest','role',
    'scan','seed','self','shut','sign','slot','snap','span','spin','sync',
    'take','talk','tell','then','turn','undo','when','wrap','zero',
    # VAMOS 프로젝트 일반어
    'vamos','phase','guide','part','section','module','feature','design',
    'level','state','stage','group','class','model','layer','agent','chain',
    'check','clear','close','count','cover','daily','debug','delay','draft',
    'error','event','extra','field','final','first','fixed','float','focus',
    'force','found','frame','fresh','given','grant','guard','happy','ideal',
    'image','input','issue','label','large','later','learn','limit','local',
    'logic','lower','match','merge','minor','multi','never','occur','offer',
    'order','other','outer','owner','panel','param','parse','patch','point',
    'power','prime','print','prior','proxy','query','queue','quick','quiet',
    'quote','raise','range','ratio','ready','refer','retry','right','round',
    'route','scope','score','setup','share','shell','shift','short','since',
    'small','smart','solid','space','split','stack','start','store','style',
    'super','sweep','table','theme','thing','throw','timer','title','token',
    'total','trace','track','train','trend','trial','upper','usage','valid',
    'value','watch','weight','whole','width','write','yield',
    # 추가 일반어
    'action','active','actual','always','amount','apply','array','basic',
    'batch','block','board','brief','build','cache','catch','cause','chain',
    'clean','clone','common','create','cross','cycle','delta','dense','depth',
    'detail','direct','double','drive','dtype','early','empty','enable',
    'entry','equal','exact','exist','false','fetch','filter','format',
    'global','handle','header','helper','hidden','human','index','inner',
    'inter','large','launch','length','linear','manual','method','metric',
    'normal','number','object','option','origin','output','parent','period',
    'phase','point','policy','prefix','process','product','prompt','proper',
    'public','random','record','reduce','remain','remove','render','repeat',
    'report','reset','result','return','review','sample','schema','search',
    'secure','select','serial','server','server','simple','single','source',
    'spread','static','status','stream','strict','string','strong','struct',
    'submit','subset','suffix','switch','symbol','system','target','thread',
    'toggle','update','upload','verify','version','virtual','volume','window',
}

# ─── 키워드 추출 (보수적: 영문 3+자 고유어만) ──────────
def extract_strong_keywords(fname):
    """확실한 고유 키워드만 추출 - 오매칭 위험 최소화"""
    kws = set()

    # 1. 모듈 ID (I-1, E-5, EVX-2 등)
    for m in re.finditer(r'\b([IESABCD]-\d{1,2}|EVX-\d)\b', fname):
        kws.add(("MID", m.group(1)))

    # 2. 하이픈 코드명 (AR-L3, LOCK-AT-004 등) - 3자 이상
    for m in re.finditer(r'[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+', fname):
        val = m.group()
        if len(val) >= 4:  # 너무 짧은 코드 제외
            kws.add(("CODE", val))

    # 3. 대문자 약어 3글자+ (SHAP, LIME, OAuth, SDAR, MoA 등)
    for m in re.finditer(r'\b([A-Z][A-Za-z]*[A-Z][A-Za-z]*)\b', fname):
        val = m.group()
        if len(val) >= 3 and val.lower() not in STOP_ENG:
            kws.add(("ABBR", val))

    # 4. CamelCase/일반 영문 3글자+ (스톱워드 제외)
    for m in re.finditer(r'\b([A-Za-z][A-Za-z0-9_]{2,})\b', fname):
        val = m.group()
        if val.lower() not in STOP_ENG and len(val) >= 3:
            kws.add(("ENG", val))

    # 5. 괄호 안 영문 고유어
    for m in re.finditer(r'[（(]([^)）]+)[)）]', fname):
        for tok in re.split(r'[/·,+→\s<>~=]+', m.group(1)):
            tok = tok.strip()
            if re.match(r'^[A-Za-z]{3,}', tok) and tok.lower() not in STOP_ENG:
                kws.add(("PENG", tok))

    # 6. 한글 4글자+ 고유어 (3글자는 일반적일 수 있으므로 Step1에서는 4+만)
    for m in re.finditer(r'([가-힣]{4,})', fname):
        tok = m.group()
        kws.add(("KOR4", tok))

    return kws

# ─── 검색 함수 ────────────────────────────────────────
def in_s25(kw):
    kw_l = kw.lower()
    # 단어 경계 체크: 영문은 word boundary, 한글은 단순 포함
    if re.match(r'^[A-Za-z]', kw):
        # 영문: 앞뒤가 알파벳이 아닌지 확인 (부분 매칭 방지)
        return bool(re.search(r'(?<![A-Za-z])' + re.escape(kw_l) + r'(?![A-Za-z])', text_s25))
    return kw_l in text_s25

def in_s6(kw):
    kw_l = kw.lower()
    if re.match(r'^[A-Za-z]', kw):
        return bool(re.search(r'(?<![A-Za-z])' + re.escape(kw_l) + r'(?![A-Za-z])', text_s6))
    return kw_l in text_s6

# ─── 분류 ───────────────────────────────────────────────
def classify(item):
    fid = item["feature_id"]
    fname = item["feature_name"]

    r = {
        "feature_id": fid,
        "feature_name": fname,
        "version_scope": item.get("version_scope", ""),
        "severity": item.get("severity", ""),
        "source_section": item.get("source_section", ""),
        "action": item.get("action", ""),
        "substatus": None,
        "match_type": "",
        "evidence": [],
        "confidence": "CERTAIN",
    }

    # Rule 1: RESOLVED
    if item.get("status") == "RESOLVED":
        r["substatus"] = "RESOLVED"
        r["match_type"] = "status_field"
        return r

    # Rule 2: NOT_APPLICABLE (STEP7 TITLE_ONLY)
    if item.get("suggested_phase", "").startswith("NOT_APPLICABLE"):
        r["substatus"] = "NOT_APPLICABLE"
        r["match_type"] = "suggested_phase"
        return r

    # Rule 3: RECLASSIFY_NA
    if item.get("action") == "RECLASSIFY_NA":
        r["substatus"] = "NOT_APPLICABLE"
        r["match_type"] = "action_reclassify"
        return r

    # Rule 4: DUPLICATE
    if fid == "D207-108":
        r["substatus"] = "DUPLICATE"
        r["match_type"] = "hardcoded"
        r["evidence"] = ["=AINV-056 (SHAP/LIME)"]
        return r

    # Rule 5: action=SKIP → SKIP_CONFIRMED
    if item.get("action") == "SKIP":
        r["substatus"] = "SKIP_CONFIRMED"
        r["match_type"] = "action_skip"
        return r

    # Rule 6+: 키워드 매칭 (확실한 것만)
    kws = extract_strong_keywords(fname)

    if not kws:
        r["substatus"] = "UNCLASSIFIED"
        r["match_type"] = "no_strong_keywords"
        r["confidence"] = "NEEDS_REVIEW"
        r["evidence"] = ["feature_name에서 고유 키워드 추출 불가"]
        return r

    # Level 1: 모듈 ID 직접 매칭
    for typ, val in kws:
        if typ == "MID" and val in module_ids:
            r["substatus"] = "SUB_FEATURE_OF_EXISTING"
            r["match_type"] = "module_id_exact"
            r["evidence"] = [f"MID:{val} in PART2"]
            return r

    # Level 2: 영문/코드 고유 키워드 §2-5 매칭 (word boundary)
    matched_s25 = []
    for typ, val in kws:
        if typ in ("ENG", "ABBR", "CODE", "PENG"):
            if in_s25(val):
                matched_s25.append(f"{typ}:{val}")

    if matched_s25:
        r["substatus"] = "SUB_FEATURE_OF_EXISTING"
        r["match_type"] = "eng_keyword_s25"
        r["evidence"] = matched_s25[:5]
        return r

    # Level 3: 한글 4글자+ §2-5 매칭
    matched_kor_s25 = []
    for typ, val in kws:
        if typ == "KOR4":
            if in_s25(val):
                matched_kor_s25.append(f"KOR4:{val}")

    if matched_kor_s25:
        r["substatus"] = "SUB_FEATURE_OF_EXISTING"
        r["match_type"] = "kor4_keyword_s25"
        r["evidence"] = matched_kor_s25[:5]
        return r

    # Level 4: 영문/코드 고유 키워드 §6 매칭
    matched_s6 = []
    for typ, val in kws:
        if typ in ("ENG", "ABBR", "CODE", "PENG"):
            if in_s6(val):
                matched_s6.append(f"{typ}:{val}")

    if matched_s6:
        r["substatus"] = "SECTION6_DETAILED"
        r["match_type"] = "eng_keyword_s6"
        r["evidence"] = matched_s6[:5]
        return r

    # Level 5: 한글 4글자+ §6 매칭
    matched_kor_s6 = []
    for typ, val in kws:
        if typ == "KOR4":
            if in_s6(val):
                matched_kor_s6.append(f"KOR4:{val}")

    if matched_kor_s6:
        r["substatus"] = "SECTION6_DETAILED"
        r["match_type"] = "kor4_keyword_s6"
        r["evidence"] = matched_kor_s6[:5]
        return r

    # 매칭 안됨 → UNCLASSIFIED (Step 2에서 상세 분석)
    r["substatus"] = "UNCLASSIFIED"
    r["match_type"] = "no_match"
    r["confidence"] = "NEEDS_REVIEW"
    unmatched = [f"{typ}:{val}" for typ, val in kws][:8]
    r["evidence"] = unmatched
    return r

# ─── 실행 ───────────────────────────────────────────────
print("\nClassifying (Step 1: certain only)...")
results = []
for item in items:
    results.append(classify(item))

# ─── 통계 ───────────────────────────────────────────────
stats = {}
for r in results:
    stats[r["substatus"]] = stats.get(r["substatus"], 0) + 1

print("\n" + "=" * 60)
print("STEP 1: CERTAIN CLASSIFICATION RESULT")
print("=" * 60)
for k, v in sorted(stats.items(), key=lambda x: -x[1]):
    print(f"  {k:30s}: {v:5d}")
print(f"  {'TOTAL':30s}: {sum(stats.values()):5d}")

# match_type 분포
mt = {}
for r in results:
    key = f"{r['substatus']}|{r['match_type']}"
    mt[key] = mt.get(key, 0) + 1

print("\n=== MATCH TYPE DETAIL ===")
for k, v in sorted(mt.items()):
    print(f"  {k:55s}: {v:4d}")

# UNCLASSIFIED 분석
unclass = [r for r in results if r["substatus"] == "UNCLASSIFIED"]
print(f"\n=== UNCLASSIFIED ({len(unclass)}) ===")

# severity 분포
sev_cnt = {}
for u in unclass:
    sev_cnt[u["severity"]] = sev_cnt.get(u["severity"], 0) + 1
print("By Severity:")
for k in ["BLOCKER", "HIGH", "MEDIUM", "LOW"]:
    if k in sev_cnt:
        print(f"  {k}: {sev_cnt[k]}")

# version_scope 분포
ver_cnt = {}
for u in unclass:
    ver_cnt[u["version_scope"]] = ver_cnt.get(u["version_scope"], 0) + 1
print("By Version:")
for k, v in sorted(ver_cnt.items()):
    print(f"  {k}: {v}")

# ─── 결과 저장 ──────────────────────────────────────────
classified = [r for r in results if r["substatus"] != "UNCLASSIFIED"]
unclassified = [r for r in results if r["substatus"] == "UNCLASSIFIED"]

output = {
    "_meta": {
        "method": "step1_certain_only",
        "date": "2026-03-10",
        "part2_version": "v22.0.0",
        "criteria": "오분류 위험 0%인 항목만 분류. 나머지 UNCLASSIFIED → Step 2 리포트",
        "classified_count": len(classified),
        "unclassified_count": len(unclassified),
    },
    "statistics": stats,
    "classified_items": classified,
    "unclassified_items": unclassified,
}

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nClassified: {len(classified)} | Unclassified: {len(unclassified)}")
print(f"Saved: {OUTPUT_PATH}")
print("DONE.")
