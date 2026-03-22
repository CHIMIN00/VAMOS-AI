#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VAMOS v10 Phase 2 - Deterministic Classification v2
개선: 모듈ID 매칭, 동의어 매핑, 더 나은 토크나이저, feature_id prefix 활용
"""

import json
import re
import sys
import os

# stdout 인코딩 강제 설정
sys.stdout.reconfigure(encoding='utf-8')

PART2_PATH = r"D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md"
CONSOLIDATED_PATH = r"D:\VAMOS\04. 구현단계\v10_results\phase2\consolidated_missing.json"
OUTPUT_PATH = r"D:\VAMOS\04. 구현단계\v10_results\phase2\deterministic_result.json"

with open(PART2_PATH, "r", encoding="utf-8") as f:
    part2_text = f.read()
    part2_lower = part2_text.lower()
    part2_lines = part2_text.split('\n')

with open(CONSOLIDATED_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

items = data["items"]
print(f"Total items: {len(items)}")

# ─── PART2 라인 인덱스 구축 ──────────────────────────────
# 각 라인의 텍스트를 소문자로 저장
line_index = [(i+1, line.lower()) for i, line in enumerate(part2_lines)]

# ─── §섹션 경계 찾기 (H1 `# N.` 패턴만 사용) ─────────────
section_boundaries = {}
for i, line in enumerate(part2_lines):
    m = re.match(r'^# (\d+)[\.\s]', line)  # H1 only (single #)
    if m:
        sec_num = int(m.group(1))
        if sec_num not in section_boundaries:
            section_boundaries[sec_num] = i

print(f"Section boundaries: {section_boundaries}")

s2_start = section_boundaries.get(2, 0)
s6_start = section_boundaries.get(6, 0)
s7_start = section_boundaries.get(7, len(part2_lines))

section_2to5_text = '\n'.join(part2_lines[s2_start:s6_start]).lower()
section_6_text = '\n'.join(part2_lines[s6_start:s7_start]).lower()
section_7_text = '\n'.join(part2_lines[s7_start:]).lower()

print(f"§2-5: {s2_start}-{s6_start} ({s6_start-s2_start} lines)")
print(f"§6: {s6_start}-{s7_start} ({s7_start-s6_start} lines)")
print(f"§7: {s7_start}-end ({len(part2_lines)-s7_start} lines)")

# ─── 모듈 ID → PART2 존재 여부 매핑 ─────────────────────
# PART2에 명시적으로 등장하는 모듈 ID 목록 추출
MODULE_IDS_IN_PART2 = set()
module_pattern = re.compile(r'\b([IESABCD]-\d{1,2}|EVX-\d|PARL|SDAR|I-\d{1,2}|E-\d{1,2}|S-\d|A-\d|B-\d|C-\d|D-\d)\b')
for line in part2_lines:
    matches = module_pattern.findall(line)
    MODULE_IDS_IN_PART2.update(matches)

print(f"Module IDs in PART2: {len(MODULE_IDS_IN_PART2)} (sample: {sorted(list(MODULE_IDS_IN_PART2))[:20]})")

# ─── feature_id prefix → 부모 모듈 매핑 ─────────────────
PREFIX_TO_MODULE = {
    "SDAR": ["SDAR", "I-25", "S-1"],
    "TEAM": ["Agent Teams", "I-24", "AT-", "LOCK-AT"],
    "AINV": ["AI Investing", "§6.8", "RSI", "backtest", "portfolio"],
    "CLIB": ["Cloud Library", "C-1", "C-2", "C-3"],
    "BASE": ["승인", "approval", "Soft Loop", "Hard Loop", "I-19", "I-8"],
    "BGNR": ["초보자", "온보딩", "가이드"],
}

# ─── PART2 핵심 키워드 사전 (feature_name → PART2 용어 동의어) ───
SYNONYM_MAP = {
    # 한글 → PART2에서 사용하는 용어
    "백테스팅": ["backtest", "RSI_BB", "백테스트"],
    "승인": ["approval", "Soft Loop", "Hard Loop", "I-19"],
    "감정": ["emotion", "감정", "IntentFrame"],
    "비용": ["cost", "I-9", "CostGate", "monthly_limit"],
    "메모리": ["Memory", "I-3", "L0", "L1", "L2", "L3", "메모리"],
    "보안": ["Security", "Guardrails", "RBAC", "PII", "HMAC"],
    "에이전트": ["Agent", "I-24", "AT-", "Sub-Agent"],
    "자율": ["autonomy", "AutonomyLevel", "L0", "L1", "L2", "L3"],
    "성능": ["Performance", "S-4", "벤치마크", "benchmark"],
    "로그": ["log", "JSONL", "이벤트", "trace"],
    "캐시": ["cache", "SemanticCache", "PromptCache", "LRU"],
    "워크플로": ["workflow", "pipeline", "파이프라인"],
    "RAG": ["RAG", "Retrieval", "검색", "Chroma", "벡터"],
    "LLM": ["LLM", "모델", "llama", "ollama", "gpt"],
    "UI": ["UI", "UX", "React", "Tauri", "컴포넌트"],
    "테스트": ["test", "검증", "GO/NO-GO", "벤치마크"],
    "배포": ["deploy", "Docker", "K8s", "Kubernetes"],
    "마이그레이션": ["migration", "마이그레이션", "V1→V2"],
    "스키마": ["Schema", "Pydantic", "스키마"],
    "설정": ["config", "toml", "설정"],
    "MCP": ["MCP", "streamable_http"],
    "도구": ["Tool", "I-10", "ToolRegistry"],
    "결정": ["Decision", "I-5", "DecisionEngine"],
    "의도": ["Intent", "I-1", "IntentDetector"],
    "컨텍스트": ["Context", "I-2", "ContextBuilder"],
    "출력": ["Output", "I-11", "OutputComposer"],
    "폴백": ["Fallback", "I-20", "FailureManager"],
    "정책": ["Policy", "I-8", "PolicyEngine", "Non-goal"],
    "QoD": ["QoD", "품질", "SelfCheck"],
    "SDAR": ["SDAR", "I-25", "Self-Diagnosis", "AR-L"],
    "투자": ["AI Investing", "투자", "포트폴리오", "portfolio", "RSI"],
    "그래프": ["Graph", "Neo4j", "json_file"],
    "벡터": ["vector", "Chroma", "qdrant", "embedding", "bge-m3"],
    "프롬프트": ["Prompt", "프롬프트", "PromptTemplate"],
    "페르소나": ["Persona", "D-4", "Personality"],
    "Self-evo": ["Self-evo", "S-1", "S-2", "S-3", "S-4", "자기진화"],
    "vLLM": ["vLLM", "GPU", "self-hosting"],
    "연합학습": ["Federated", "연합학습"],
    "실험": ["EVX", "Experimental", "실험"],
}

# ─── 스톱워드 (검색에서 제외) ─────────────────────────────
STOPWORDS = {
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

# ─── SKIP 대상 키워드 ─────────────────────────────────────
SKIP_PATTERNS = [
    r"로드맵", r"마일스톤", r"WBS", r"일정표", r"KPI\s*대시보드",
    r"조직도", r"인력\s*배치", r"채용", r"온보딩\s*가이드",
    r"마케팅", r"영업", r"GTM", r"go.to.market",
    r"비즈니스\s*모델", r"수익\s*모델", r"pricing",
]

# ─── 키워드 추출 (개선) ──────────────────────────────────
def extract_keywords(feature_name):
    """feature_name에서 의미 있는 검색 키워드 추출"""
    keywords = set()

    # 1. 영문 토큰 추출 (_, ., - 로 분리)
    eng_tokens = re.findall(r'[A-Za-z][A-Za-z0-9]*', feature_name)
    for tok in eng_tokens:
        if len(tok) >= 2 and tok.lower() not in {'py', 'js', 'ts', 'md', 'json', 'yaml', 'toml',
                                                    'the', 'and', 'for', 'with', 'from', 'this',
                                                    'that', 'all', 'new', 'add', 'use', 'is', 'in',
                                                    'to', 'of', 'on', 'at', 'by', 'as', 'or', 'an'}:
            keywords.add(tok)

    # 2. 코드명 패턴 (I-1, E-13, AR-L3, EVX-2, LOCK-AT-004 등)
    code_patterns = re.findall(r'[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+', feature_name)
    keywords.update(code_patterns)

    # 3. 한글 토큰 추출 (2글자 이상, 스톱워드 제외)
    kor_tokens = re.findall(r'[가-힣]+', feature_name)
    for tok in kor_tokens:
        if len(tok) >= 2 and tok not in STOPWORDS:
            keywords.add(tok)

    # 4. 약어 패턴 (대문자 연속: QoD, SDAR, MoA, LLM 등)
    abbrevs = re.findall(r'\b[A-Z][A-Za-z]*[A-Z][A-Za-z]*\b', feature_name)
    keywords.update(abbrevs)

    # 5. 특수 용어 (괄호 안의 영문/약어)
    paren_contents = re.findall(r'[（(]([^)）]+)[)）]', feature_name)
    for pc in paren_contents:
        for tok in re.split(r'[/·,+→\s<>~]+', pc):
            tok = tok.strip()
            if len(tok) >= 2:
                # 영문이면 추가
                if re.match(r'^[A-Za-z]', tok):
                    keywords.add(tok)
                # 한글 3글자 이상이면 추가
                elif re.match(r'^[가-힣]{3,}$', tok):
                    keywords.add(tok)

    return keywords

# ─── PART2 검색 (개선) ───────────────────────────────────
def search_keyword_in_text(keyword, text):
    """대소문자 무시하고 keyword가 text에 있는지"""
    return keyword.lower() in text.lower()

def find_lines(keyword):
    """PART2에서 keyword가 등장하는 라인 번호 리스트"""
    kw_low = keyword.lower()
    return [ln for ln, text in line_index if kw_low in text]

# ─── 모듈 ID 매칭 ────────────────────────────────────────
def find_module_ids_in_name(feature_name):
    """feature_name에서 모듈 ID 추출 (I-1, E-13 등)"""
    ids = set()
    # I-XX, E-XX, S-X, A-X, B-X, C-X, D-X
    patterns = re.findall(r'\b([IESABCD]-\d{1,2})\b', feature_name)
    ids.update(patterns)
    # EVX-X
    evx = re.findall(r'\b(EVX-\d)\b', feature_name)
    ids.update(evx)
    # SDAR, PARL
    if 'SDAR' in feature_name:
        ids.add('SDAR')
    if 'PARL' in feature_name:
        ids.add('PARL')
    return ids

# ─── 분류 메인 로직 ──────────────────────────────────────
def classify_item(item):
    fid = item["feature_id"]
    fname = item["feature_name"]
    result = {
        "feature_id": fid,
        "feature_name": fname,
        "version_scope": item.get("version_scope", ""),
        "severity": item.get("severity", ""),
        "substatus": None,
        "matched_keywords": [],
        "matched_in": "",  # "§2-5", "§6", "both"
        "confidence": "",
    }

    # ── Rule 1: RESOLVED 유지 ──
    if item.get("status") == "RESOLVED":
        result["substatus"] = "RESOLVED"
        result["confidence"] = "FIXED"
        return result

    # ── Rule 2: NOT_APPLICABLE 유지 ──
    if item.get("suggested_phase", "").startswith("NOT_APPLICABLE"):
        result["substatus"] = "NOT_APPLICABLE"
        result["confidence"] = "FIXED"
        return result

    # ── Rule 3: DUPLICATE 하드코딩 ──
    if fid == "D207-108":
        result["substatus"] = "DUPLICATE"
        result["confidence"] = "FIXED"
        result["matched_keywords"] = ["AINV-056 (SHAP/LIME)"]
        return result

    # ── Rule 4: SKIP 체크 ──
    for pat in SKIP_PATTERNS:
        if re.search(pat, fname, re.IGNORECASE):
            result["substatus"] = "SKIP_CONFIRMED"
            result["confidence"] = "HIGH"
            result["matched_keywords"] = [pat]
            return result

    # ── 키워드 추출 ──
    keywords = extract_keywords(fname)

    # ── 모듈 ID 매칭 (가장 강력한 증거) ──
    module_ids = find_module_ids_in_name(fname)
    for mid in module_ids:
        if mid in MODULE_IDS_IN_PART2:
            lines = find_lines(mid)
            result["substatus"] = "SUB_FEATURE_OF_EXISTING"
            result["confidence"] = "HIGH"
            result["matched_keywords"] = [f"MODULE:{mid}"]
            result["matched_in"] = "module_id"
            return result

    # ── feature_id prefix 매칭 ──
    fid_prefix = re.match(r'^([A-Z]+)', fid)
    if fid_prefix:
        prefix = fid_prefix.group(1)
        if prefix in PREFIX_TO_MODULE:
            parent_terms = PREFIX_TO_MODULE[prefix]
            for term in parent_terms:
                if search_keyword_in_text(term, part2_text):
                    result["substatus"] = "SUB_FEATURE_OF_EXISTING"
                    result["confidence"] = "MEDIUM"
                    result["matched_keywords"] = [f"PREFIX:{prefix}→{term}"]
                    result["matched_in"] = "prefix"
                    return result

    # ── 동의어 확장 검색 ──
    synonym_matches = []
    for kw in keywords:
        # 직접 동의어 매핑 확인
        for syn_key, syn_values in SYNONYM_MAP.items():
            if kw.lower() == syn_key.lower() or kw in syn_values:
                for sv in syn_values:
                    if search_keyword_in_text(sv, part2_text):
                        synonym_matches.append((kw, sv))
                        break

    # ── 직접 키워드 매칭 ──
    matched_s25 = []
    matched_s6 = []
    matched_s7 = []

    for kw in keywords:
        if len(kw) < 2:
            continue
        in_s25 = search_keyword_in_text(kw, section_2to5_text)
        in_s6 = search_keyword_in_text(kw, section_6_text)
        in_s7 = search_keyword_in_text(kw, section_7_text)

        if in_s25:
            matched_s25.append(kw)
        if in_s6:
            matched_s6.append(kw)
        if in_s7:
            matched_s7.append(kw)

    # ── 핵심 키워드 필터 (일반 단어 제외) ──
    def is_specific_keyword(kw):
        """특정적인(고유한) 키워드인지 판단"""
        # 영문 3글자 이상 → specific
        if re.match(r'^[A-Za-z]{3,}', kw):
            return True
        # 한글 3글자 이상 → specific
        if re.match(r'^[가-힣]{3,}$', kw):
            return True
        # 코드명 → specific
        if re.match(r'^[A-Z]+-', kw):
            return True
        # 대문자 약어 → specific
        if re.match(r'^[A-Z]{2,}$', kw):
            return True
        return False

    specific_s25 = [kw for kw in matched_s25 if is_specific_keyword(kw)]
    specific_s6 = [kw for kw in matched_s6 if is_specific_keyword(kw)]

    # ── 분류 결정 ──
    if specific_s25:
        result["substatus"] = "SUB_FEATURE_OF_EXISTING"
        result["confidence"] = "HIGH"
        result["matched_keywords"] = specific_s25[:5]
        result["matched_in"] = "§2-5"
    elif specific_s6:
        result["substatus"] = "SECTION6_DETAILED"
        result["confidence"] = "HIGH"
        result["matched_keywords"] = specific_s6[:5]
        result["matched_in"] = "§6"
    elif synonym_matches:
        result["substatus"] = "SUB_FEATURE_OF_EXISTING"
        result["confidence"] = "MEDIUM"
        result["matched_keywords"] = [f"{k}→{v}" for k, v in synonym_matches[:5]]
        result["matched_in"] = "synonym"
    elif matched_s25 or matched_s6:
        # 일반 키워드만 매칭 - PART2에 해당 2글자 한글이 있지만 고유하지 않음
        # 이 경우 feature_name의 핵심 구문(4글자 이상 한글)으로 재검색
        long_kor = re.findall(r'[가-힣]{4,}', fname)
        phrase_found = False
        for phrase in long_kor:
            if phrase in STOPWORDS:
                continue
            if search_keyword_in_text(phrase, part2_text):
                phrase_found = True
                result["matched_keywords"].append(phrase)

        if phrase_found:
            result["substatus"] = "SUB_FEATURE_OF_EXISTING"
            result["confidence"] = "LOW"
            result["matched_in"] = "phrase"
        else:
            result["substatus"] = "REAL_GAP"
            result["confidence"] = "MEDIUM"
            result["matched_keywords"] = matched_s25 + matched_s6
            result["matched_in"] = "generic_only"
    else:
        result["substatus"] = "REAL_GAP"
        result["confidence"] = "HIGH"
        result["matched_in"] = "zero_match"

    return result

# ─── 전체 분류 실행 ──────────────────────────────────────
print("Classifying all items...")
results = []
for item in items:
    r = classify_item(item)
    results.append(r)

# ─── 통계 ────────────────────────────────────────────────
stats = {}
for r in results:
    s = r["substatus"]
    stats[s] = stats.get(s, 0) + 1

print("\n=== DETERMINISTIC CLASSIFICATION v2 ===")
for k, v in sorted(stats.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")
print(f"  TOTAL: {sum(stats.values())}")

# confidence 분포
conf_stats = {}
for r in results:
    key = f"{r['substatus']}|{r['confidence']}"
    conf_stats[key] = conf_stats.get(key, 0) + 1

print("\n=== CONFIDENCE DISTRIBUTION ===")
for k, v in sorted(conf_stats.items()):
    print(f"  {k}: {v}")

# REAL_GAP by severity
rg_sev = {}
real_gaps = [r for r in results if r["substatus"] == "REAL_GAP"]
for rg in real_gaps:
    sev = rg.get("severity", "UNKNOWN")
    rg_sev[sev] = rg_sev.get(sev, 0) + 1

print(f"\n=== REAL_GAP ({len(real_gaps)}) by Severity ===")
for k, v in sorted(rg_sev.items()):
    print(f"  {k}: {v}")

# REAL_GAP 목록 (severity별 정렬)
print(f"\n=== REAL_GAP Items ===")
for rg in sorted(real_gaps, key=lambda x: {"BLOCKER":0,"HIGH":1,"MEDIUM":2,"LOW":3}.get(x.get("severity","LOW"),4)):
    mi = rg.get("matched_in", "")
    mk = ", ".join(rg.get("matched_keywords", [])[:3])
    info = f" [{mi}: {mk}]" if mk else f" [{mi}]"
    print(f"  [{rg['severity']:7s}] {rg['feature_id']}: {rg['feature_name'][:70]}{info}")

# ─── 결과 저장 ──────────────────────────────────────────
output = {
    "_meta": {
        "method": "deterministic_keyword_matching_v2",
        "criteria": {
            "rule": "PART2에 명시적 키워드 없으면 REAL_GAP",
            "module_id_match": "feature_name에 I-XX/E-XX 등 모듈ID가 있고 PART2에 해당 ID 존재 → SUB_FEATURE",
            "prefix_match": "feature_id prefix(SDAR/TEAM/AINV 등)의 부모 모듈이 PART2에 존재 → SUB_FEATURE",
            "synonym_match": "동의어 사전으로 확장 검색",
            "specific_keyword": "영문 3자+, 한글 3자+, 코드명, 약어만 유효 매칭으로 인정",
            "generic_only": "2글자 일반 한글만 매칭 → REAL_GAP (4글자+ 구문 재검색 통과 시 SUB_FEATURE)",
        },
        "date": "2026-03-10",
        "part2_version": "v22.0.0",
    },
    "statistics": stats,
    "real_gap_count": len(real_gaps),
    "real_gap_ids": [r["feature_id"] for r in real_gaps],
    "real_gap_by_severity": rg_sev,
    "items": results,
}

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nResults saved to: {OUTPUT_PATH}")
print("DONE.")