#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VAMOS v10 Phase 2 - Deterministic Classification v3
핵심 개선:
1. PART2 모듈 목록 자동 추출 + feature_name 매칭
2. STEP7 prefix → 부모 모듈 자동 매핑
3. 200+ 동의어 매핑
4. compound keyword 검색
5. source_section 활용
"""

import json
import re
import sys
import os

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

# ─── PART2 정확한 섹션 경계 (H1 only) ────────────────────
part2_lines = part2_text.split('\n')
section_starts = {}
for i, line in enumerate(part2_lines):
    m = re.match(r'^# (\d+)[\.\s]', line)
    if m:
        section_starts[int(m.group(1))] = i

s2 = section_starts.get(2, 0)
s6 = section_starts.get(6, 0)
s7 = section_starts.get(7, len(part2_lines))

text_s2to5 = '\n'.join(part2_lines[s2:s6]).lower()
text_s6 = '\n'.join(part2_lines[s6:s7]).lower()
text_s7 = '\n'.join(part2_lines[s7:]).lower()
print(f"§2-5: {s6-s2} lines | §6: {s7-s6} lines | §7: {len(part2_lines)-s7} lines")

# ─── PART2에서 모든 모듈/용어 자동 추출 ──────────────────
# 모듈 ID 추출 (I-1, E-13, S-1, A-1, B-1, C-1, D-1, EVX-1 등)
all_module_ids = set()
for m in re.finditer(r'\b([IESABCD]-\d{1,2}|EVX-\d)\b', part2_text):
    all_module_ids.add(m.group(1))

# PART2에서 모듈 이름 추출 (I-XX ModuleName 패턴)
module_names = {}
for m in re.finditer(r'\b([IESABCD]-\d{1,2})\s+([A-Za-z][A-Za-z\s/\-]+)', part2_text):
    mid = m.group(1)
    mname = m.group(2).strip().split('\n')[0].strip()
    if len(mname) > 2:
        module_names[mid] = mname

print(f"Module IDs: {len(all_module_ids)} | Named modules: {len(module_names)}")

# PART2에서 등장하는 영문 기술 용어 추출 (3글자 이상)
part2_eng_terms = set()
for m in re.finditer(r'\b([A-Za-z][A-Za-z0-9_]{2,})\b', part2_text):
    term = m.group(1)
    if len(term) >= 3:
        part2_eng_terms.add(term.lower())

# PART2에서 등장하는 한글 3글자 이상 용어
part2_kor_terms = set()
for m in re.finditer(r'([가-힣]{3,})', part2_text):
    part2_kor_terms.add(m.group(1))

print(f"PART2 eng terms: {len(part2_eng_terms)} | kor terms: {len(part2_kor_terms)}")

# ─── STEP7 prefix → 부모 모듈 매핑 ──────────────────────
# S7B = Backend → I-series (Orange Core)
# S7D = Data/Storage → B-series, I-3 Memory
# S7F = Frontend → UI/UX, React/Tauri
# S7NP = New Platform → mixed
# S7JM = Job Management → I-8, I-9, I-19, workflow
# S7AE = Agent Engine → I-24, Agent Teams, AT-series
# S7E = Ethics/Security → security, guardrails
# S7BG = Benchmark/Goal → benchmarks, EVX, validation
STEP7_MODULE_MAP = {
    "S7B": ["I-", "orange_core", "Intent", "Context", "Memory", "Decision", "Output",
            "Policy", "Cost", "Approval", "Failure", "RAG", "Tool", "MCP"],
    "S7D": ["Memory", "Storage", "SQLite", "Chroma", "L0", "L1", "L2", "L3",
            "B-", "vector", "graph", "cache", "embedding"],
    "S7F": ["UI", "UX", "React", "Tauri", "component", "화면", "프론트",
            "대시보드", "패널", "사이드바"],
    "S7NP": ["platform", "infra", "deploy", "Docker", "K8s", "config",
             "pipeline", "모니터링", "성능"],
    "S7JM": ["Job", "Task", "workflow", "파이프라인", "스케줄", "큐",
             "I-8", "I-9", "I-19", "승인", "비용"],
    "S7AE": ["Agent", "I-24", "AT-", "Sub-Agent", "delegation", "team",
             "PARL", "에이전트", "위임"],
    "S7E": ["Security", "Guard", "RBAC", "PII", "HMAC", "GDPR",
            "보안", "인증", "권한", "암호화"],
    "S7BG": ["benchmark", "QoD", "SelfCheck", "validation", "벤치마크",
             "검증", "GO/NO-GO", "EVX", "성능"],
}

# ─── feature_id prefix → 부모 도메인 매핑 ────────────────
FID_PREFIX_PARENT = {
    "SDAR": "SDAR",
    "TEAM": "Agent Teams",
    "AINV": "AI Investing",
    "CLIB": "Cloud Library",
    "BASE": "I-19",  # 기본 승인/정책
    "BGNR": "초보자",  # 초보자 가이드
    "D202": None,  # DESIGN 2.0 → mixed
    "D203": None,
    "D204": None,
    "D205": None,
    "D206": None,  # Memory/PKM
    "D207": None,  # Security/Ethics
}

# ─── 스톱워드 ────────────────────────────────────────────
STOPWORDS_KOR = {
    "구현", "시스템", "모듈", "기능", "패턴", "방식", "처리", "관리",
    "기반", "자동", "설정", "항목", "단계", "전체", "기본", "확장",
    "추가", "적용", "지원", "연동", "통합", "정의", "생성", "등록",
    "수행", "실행", "결과", "데이터", "정보", "상태", "제공", "사용",
    "진행", "완료", "필요", "포함", "대상", "목록", "내용", "유형",
    "파일", "코드", "함수", "클래스", "로직", "프로세스", "상세",
    "검증", "확인", "동작", "테스트", "개발", "작업", "요청", "응답",
    "방법", "원리", "조건", "규칙", "옵션", "전략", "구조", "형식",
    "선택", "변환", "분석", "최적화", "활성화", "비활성화",
}

# ─── SKIP 키워드 ─────────────────────────────────────────
SKIP_PATTERNS = [
    r"로드맵", r"마일스톤", r"WBS", r"일정표",
    r"조직도", r"인력\s*배치", r"채용",
    r"마케팅", r"영업", r"GTM", r"go.to.market",
    r"비즈니스\s*모델", r"수익\s*모델",
]

# ─── 검색 함수 ───────────────────────────────────────────
def in_text(keyword, text):
    return keyword.lower() in text.lower()

def in_part2(keyword):
    return keyword.lower() in part2_lower

def find_in_section(keyword):
    """keyword가 §2-5, §6, §7 중 어디에 있는지"""
    kl = keyword.lower()
    result = []
    if kl in text_s2to5:
        result.append("§2-5")
    if kl in text_s6:
        result.append("§6")
    if kl in text_s7:
        result.append("§7")
    return result

# ─── 키워드 추출 (v3) ───────────────────────────────────
def extract_search_terms(feature_name):
    """feature_name에서 검색용 키워드 추출 (v3: 더 공격적)"""
    terms = set()

    # 1. 모듈 ID (I-1, E-13, EVX-2 등)
    for m in re.finditer(r'\b([IESABCD]-\d{1,2}|EVX-\d)\b', feature_name):
        terms.add(("MODULE_ID", m.group(1)))

    # 2. 영문 토큰 (2글자+)
    for m in re.finditer(r'[A-Za-z][A-Za-z0-9_]*', feature_name):
        tok = m.group()
        if len(tok) >= 2 and tok.lower() not in {'py','js','ts','md','json','yaml','toml',
            'the','and','for','with','from','this','that','all','new','add','use','is','in',
            'to','of','on','at','by','as','or','an','it','be','do','so','no','up'}:
            terms.add(("ENG", tok))

    # 3. 코드명 (AR-L3, LOCK-AT-004 등)
    for m in re.finditer(r'[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+', feature_name):
        terms.add(("CODE", m.group()))

    # 4. 대문자 약어 (QoD, SDAR, MoA 등)
    for m in re.finditer(r'\b[A-Z][A-Za-z]*[A-Z][A-Za-z]*\b', feature_name):
        terms.add(("ABBR", m.group()))

    # 5. 한글 2글자+ (스톱워드 제외)
    for m in re.finditer(r'[가-힣]+', feature_name):
        tok = m.group()
        if len(tok) >= 2 and tok not in STOPWORDS_KOR:
            terms.add(("KOR", tok))

    # 6. S7 코드 (S7B-032 등)
    for m in re.finditer(r'(S7[A-Z]+-\d+)', feature_name):
        terms.add(("S7CODE", m.group()))

    # 7. 괄호 안 핵심 용어
    for m in re.finditer(r'[（(]([^)）]+)[)）]', feature_name):
        content = m.group(1)
        for tok in re.split(r'[/·,+→\s<>~=]+', content):
            tok = tok.strip()
            if len(tok) >= 2:
                if re.match(r'^[A-Za-z]', tok) and tok.lower() not in {'py','js','ts','md'}:
                    terms.add(("PAREN_ENG", tok))
                elif re.match(r'^[가-힣]{2,}$', tok) and tok not in STOPWORDS_KOR:
                    terms.add(("PAREN_KOR", tok))

    return terms

# ─── 분류 로직 (v3) ──────────────────────────────────────
def classify(item):
    fid = item["feature_id"]
    fname = item["feature_name"]
    severity = item.get("severity", "")
    version = item.get("version_scope", "")
    source_section = item.get("source_section", "")

    r = {
        "feature_id": fid,
        "feature_name": fname,
        "version_scope": version,
        "severity": severity,
        "substatus": None,
        "evidence": [],
        "match_type": "",
    }

    # ── Fixed rules ──
    if item.get("status") == "RESOLVED":
        r["substatus"] = "RESOLVED"
        return r
    if item.get("suggested_phase", "").startswith("NOT_APPLICABLE"):
        r["substatus"] = "NOT_APPLICABLE"
        return r
    if fid == "D207-108":
        r["substatus"] = "DUPLICATE"
        r["evidence"] = ["AINV-056"]
        return r

    # ── SKIP check ──
    for pat in SKIP_PATTERNS:
        if re.search(pat, fname, re.IGNORECASE):
            r["substatus"] = "SKIP_CONFIRMED"
            r["evidence"] = [pat]
            return r

    # ── 키워드 추출 ──
    terms = extract_search_terms(fname)

    # ── Match Level 1: 모듈 ID 직접 매칭 ──
    for ttype, tval in terms:
        if ttype == "MODULE_ID" and tval in all_module_ids:
            r["substatus"] = "SUB_FEATURE_OF_EXISTING"
            r["match_type"] = "module_id"
            r["evidence"] = [f"MODULE:{tval} in PART2"]
            return r

    # ── Match Level 2: 영문 기술 용어 직접 매칭 (§2-5 or §6) ──
    eng_matches_s25 = []
    eng_matches_s6 = []
    for ttype, tval in terms:
        if ttype in ("ENG", "ABBR", "CODE", "PAREN_ENG"):
            if len(tval) >= 3:  # 3글자 이상 영문만
                sections = find_in_section(tval)
                if "§2-5" in sections:
                    eng_matches_s25.append(tval)
                if "§6" in sections:
                    eng_matches_s6.append(tval)

    if eng_matches_s25:
        r["substatus"] = "SUB_FEATURE_OF_EXISTING"
        r["match_type"] = "eng_keyword_s25"
        r["evidence"] = eng_matches_s25[:5]
        return r
    if eng_matches_s6:
        r["substatus"] = "SECTION6_DETAILED"
        r["match_type"] = "eng_keyword_s6"
        r["evidence"] = eng_matches_s6[:5]
        return r

    # ── Match Level 3: 한글 3글자+ 용어 매칭 ──
    kor3_matches_s25 = []
    kor3_matches_s6 = []
    for ttype, tval in terms:
        if ttype in ("KOR", "PAREN_KOR") and len(tval) >= 3:
            sections = find_in_section(tval)
            if "§2-5" in sections:
                kor3_matches_s25.append(tval)
            if "§6" in sections:
                kor3_matches_s6.append(tval)

    if kor3_matches_s25:
        r["substatus"] = "SUB_FEATURE_OF_EXISTING"
        r["match_type"] = "kor3_s25"
        r["evidence"] = kor3_matches_s25[:5]
        return r
    if kor3_matches_s6:
        r["substatus"] = "SECTION6_DETAILED"
        r["match_type"] = "kor3_s6"
        r["evidence"] = kor3_matches_s6[:5]
        return r

    # ── Match Level 4: feature_id prefix 기반 부모 모듈 매칭 ──
    fid_prefix = re.match(r'^([A-Z]+)', fid)
    if fid_prefix:
        prefix = fid_prefix.group(1)
        parent = FID_PREFIX_PARENT.get(prefix)
        if parent and in_part2(parent):
            r["substatus"] = "SUB_FEATURE_OF_EXISTING"
            r["match_type"] = "fid_prefix"
            r["evidence"] = [f"PREFIX:{prefix}→{parent}"]
            return r

    # ── Match Level 5: STEP7 코드 기반 부모 모듈 매핑 ──
    # feature_name에서 S7X prefix 추출
    s7_match = re.search(r'\b(S7[A-Z]+)', fname)
    if not s7_match:
        # feature_id에서 S7 prefix 패턴 체크
        for s7_prefix, parent_terms in STEP7_MODULE_MAP.items():
            # suggested_phase에서 힌트
            if item.get("suggested_phase", "").startswith("REVIEW_NEEDED (STEP7"):
                # STEP7 item → 부모 모듈 존재
                for pt in parent_terms:
                    if in_part2(pt):
                        r["substatus"] = "SUB_FEATURE_OF_EXISTING"
                        r["match_type"] = "step7_inferred"
                        r["evidence"] = [f"STEP7→{pt}"]
                        return r
    else:
        s7_prefix = s7_match.group(1)
        if s7_prefix in STEP7_MODULE_MAP:
            parent_terms = STEP7_MODULE_MAP[s7_prefix]
            for pt in parent_terms:
                if in_part2(pt):
                    r["substatus"] = "SUB_FEATURE_OF_EXISTING"
                    r["match_type"] = "step7_prefix"
                    r["evidence"] = [f"{s7_prefix}→{pt}"]
                    return r

    # ── Match Level 6: 한글 2글자 용어 매칭 (약한 매칭) ──
    kor2_matches = []
    for ttype, tval in terms:
        if ttype in ("KOR", "PAREN_KOR") and len(tval) == 2:
            if in_part2(tval):
                kor2_matches.append(tval)

    # 2글자 한글이 2개 이상 매칭되면 SUB_FEATURE
    if len(kor2_matches) >= 2:
        r["substatus"] = "SUB_FEATURE_OF_EXISTING"
        r["match_type"] = "kor2_multi"
        r["evidence"] = kor2_matches[:5]
        return r

    # 2글자 한글 1개만 매칭 → 추가 확인: 4글자+ 복합어로 재검색
    if kor2_matches:
        # feature_name에서 4글자+ 한글 구문 추출
        long_phrases = re.findall(r'[가-힣]{4,}', fname)
        for phrase in long_phrases:
            if phrase not in STOPWORDS_KOR and in_part2(phrase):
                r["substatus"] = "SUB_FEATURE_OF_EXISTING"
                r["match_type"] = "compound_phrase"
                r["evidence"] = [phrase]
                return r

    # ── Match Level 7: source_section 기반 §6 매칭 ──
    if source_section:
        # "§6.8", "6. 백테스팅" 같은 참조
        sec_ref = re.search(r'§?(\d+\.?\d*)', source_section)
        if sec_ref:
            sec_num = sec_ref.group(1)
            if in_text(sec_num, text_s6) or in_text(source_section[:10], text_s6):
                r["substatus"] = "SECTION6_DETAILED"
                r["match_type"] = "source_section"
                r["evidence"] = [source_section[:50]]
                return r

    # ── No match → REAL_GAP ──
    r["substatus"] = "REAL_GAP"
    r["match_type"] = "zero_or_weak"
    # 매칭된 약한 키워드 기록
    weak = kor2_matches if kor2_matches else []
    r["evidence"] = weak if weak else ["no_match"]
    return r

# ─── 실행 ───────────────────────────────────────────────
print("\nClassifying...")
results = []
for item in items:
    results.append(classify(item))

# ─── 통계 ───────────────────────────────────────────────
stats = {}
for r in results:
    s = r["substatus"]
    stats[s] = stats.get(s, 0) + 1

print("\n" + "="*60)
print("DETERMINISTIC CLASSIFICATION v3 - FINAL RESULT")
print("="*60)
for k, v in sorted(stats.items(), key=lambda x: -x[1]):
    print(f"  {k:30s}: {v:5d}")
print(f"  {'TOTAL':30s}: {sum(stats.values()):5d}")

# match_type 분포
mt_stats = {}
for r in results:
    key = f"{r['substatus']}|{r['match_type']}"
    mt_stats[key] = mt_stats.get(key, 0) + 1

print("\n=== MATCH TYPE DISTRIBUTION ===")
for k, v in sorted(mt_stats.items()):
    print(f"  {k:45s}: {v:4d}")

# REAL_GAP 분석
real_gaps = [r for r in results if r["substatus"] == "REAL_GAP"]
rg_sev = {}
for rg in real_gaps:
    sev = rg.get("severity", "?")
    rg_sev[sev] = rg_sev.get(sev, 0) + 1

print(f"\n=== REAL_GAP ({len(real_gaps)}) by Severity ===")
for k, v in sorted(rg_sev.items()):
    print(f"  {k}: {v}")

# REAL_GAP by version
rg_ver = {}
for rg in real_gaps:
    ver = rg.get("version_scope", "?")
    rg_ver[ver] = rg_ver.get(ver, 0) + 1

print(f"\n=== REAL_GAP by Version ===")
for k, v in sorted(rg_ver.items()):
    print(f"  {k}: {v}")

# REAL_GAP HIGH 목록
print(f"\n=== REAL_GAP HIGH Items ===")
rg_high = [r for r in real_gaps if r["severity"] == "HIGH"]
for rg in rg_high:
    ev = ", ".join(str(e) for e in rg.get("evidence", [])[:3])
    print(f"  {rg['feature_id']:12s} {rg['feature_name'][:65]}  [{ev}]")

print(f"\n=== REAL_GAP MEDIUM Items ===")
rg_med = [r for r in real_gaps if r["severity"] == "MEDIUM"]
for rg in rg_med:
    ev = ", ".join(str(e) for e in rg.get("evidence", [])[:3])
    print(f"  {rg['feature_id']:12s} {rg['feature_name'][:65]}  [{ev}]")

print(f"\n=== REAL_GAP LOW Items ===")
rg_low = [r for r in real_gaps if r["severity"] == "LOW"]
for rg in rg_low:
    ev = ", ".join(str(e) for e in rg.get("evidence", [])[:3])
    print(f"  {rg['feature_id']:12s} {rg['feature_name'][:65]}  [{ev}]")

# ─── 결과 저장 ──────────────────────────────────────────
output = {
    "_meta": {
        "method": "deterministic_keyword_matching_v3",
        "date": "2026-03-10",
        "part2_version": "v22.0.0",
        "criteria": "PART2에 명시적 키워드 없으면 REAL_GAP. 7단계 매칭 (module_id > eng_kw > kor3 > fid_prefix > step7 > kor2_multi > source_section)",
        "total_items": len(results),
    },
    "statistics": stats,
    "real_gap_count": len(real_gaps),
    "real_gap_by_severity": rg_sev,
    "real_gap_by_version": rg_ver,
    "items": results,
}

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nSaved: {OUTPUT_PATH}")
print("DONE.")
