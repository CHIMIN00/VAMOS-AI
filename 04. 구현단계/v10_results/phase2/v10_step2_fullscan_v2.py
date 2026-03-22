#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
v10 Step 2 전수 팩트 검증 스크립트 v2
- 키워드 점수 기반이 아닌 실제 줄 단위 증거(evidence) 기반 분류
- 각 항목마다: 모듈ID / 파일경로 / 기술용어 / feature_id를 PART2+STEP7에서 검색
- 매칭된 줄번호 + 원문 인용을 evidence로 기록
- 분류 기준 엄격화: evidence 없으면 분류 불가
"""

import json
import re
import os
import sys
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# ─── 경로 ───
BASE_DIR = "D:/VAMOS/04. 구현단계/v10_results/phase2"
PART2_PATH = "D:/VAMOS/docs/guides/VAMOS_구현가이드_PART2_구현단계.md"
STEP7_DIR = "D:/VAMOS/docs/sot"
STEP1_DIR = f"{BASE_DIR}/step1"

# ─── PART2 섹션 범위 (v22.0.0) ───
SECTIONS = {
    "§2_V0": (54, 1383),
    "§3_V1_Phase1": (1384, 1486), "§3_V1_Phase2": (1487, 1574),
    "§3_V1_Phase3": (1575, 1623), "§3_V1_Phase4": (1624, 1667),
    "§3_V1_Phase5": (1668, 1706), "§3_V1_Phase6": (1707, 1767),
    "§4_V2_Phase1": (1768, 1932), "§4_V2_Phase2": (1933, 2117),
    "§4_V2_Phase3": (2118, 2286),
    "§5_V3_Phase1": (2287, 2433), "§5_V3_Phase2": (2434, 2717),
    "§5_V3_Phase3": (2718, 2902),
    "§6_1_UI": (2908, 3012), "§6_2_Rust": (3013, 3047),
    "§6_3_Test": (3048, 3079), "§6_4_CICD": (3080, 3102),
    "§6_5_Security": (3103, 3136), "§6_6_MCP": (3137, 3156),
    "§6_7_Agent": (3157, 3282), "§6_8_AIInvest": (3283, 3404),
    "§6_9_SDAR": (3405, 3517), "§6_10_Cloud": (3518, 3745),
    "§6_11_Event": (3746, 3810), "§6_12_Ops": (3811, 3821),
    "§6_13_Workload": (3822, 3846), "§7": (3847, 4060),
}

VERSION_SECTIONS = {
    "V0": ["§2_V0"],
    "V1": ["§3_V1_Phase1","§3_V1_Phase2","§3_V1_Phase3","§3_V1_Phase4","§3_V1_Phase5","§3_V1_Phase6"],
    "V2": ["§4_V2_Phase1","§4_V2_Phase2","§4_V2_Phase3"],
    "V3": ["§5_V3_Phase1","§5_V3_Phase2","§5_V3_Phase3"],
}

AGENT_S6 = {
    "M-1": ["§6_1_UI","§6_2_Rust"],
    "M-2": ["§6_3_Test","§6_8_AIInvest"],
    "M-3": ["§6_5_Security","§6_9_SDAR","§6_11_Event"],
    "M-4": ["§6_7_Agent"],
    "M-5": ["§6_4_CICD","§6_6_MCP","§6_10_Cloud","§6_12_Ops"],
}

AGENT_STEP7 = {
    "M-1": ["STEP7-B","STEP7-C"],
    "M-2": ["STEP7-D","STEP7-E","STEP7-F"],
    "M-3": ["STEP7-G","STEP7-H"],
    "M-4": ["STEP7-I","STEP7-J","STEP7-K"],
    "M-5": ["STEP7-L","STEP7-M","STEP7-N","STEP7-O","STEP7-P"],
}


# ═══════════════════════════════════════════════════════
# 1. 인덱스 빌드
# ═══════════════════════════════════════════════════════

def build_part2_index(lines):
    """PART2 줄별 인덱스:
    - module_ids: {mod_id: [(line_no, text), ...]}
    - file_paths: {path_fragment: [(line_no, text), ...]}
    - all_lines: [(line_no, text, section_key)]
    """
    module_ids = defaultdict(list)   # "I-18" → [(1234, "...I-18 Self-evo...")]
    file_paths = defaultdict(list)   # "i18_self_evo" → [(1234, "...")]
    tech_terms = defaultdict(list)   # "langgraph" → [(1234, "...")]
    all_lines = []

    # 모듈 ID 패턴: I-1~I-25, S-2~S-8, A-3~A-7, B-1~B-6, C-4~C-7, D-3~D-6, E-7~E-16, EVX-1~EVX-6
    mod_pattern = re.compile(r'\b([ISABCDE]-\d{1,2}|EVX-\d)\b')
    # 파일 경로 패턴
    path_pattern = re.compile(r'(backend/\S+\.py|src-tauri/\S+\.rs|frontend/\S+\.tsx?|scripts/\S+\.py|deploy/\S+)')
    # 기술 용어 (소문자 비교)
    TECH_TERMS = [
        "langgraph","parl","shap","lime","rag","neo4j","qdrant","redis",
        "kubernetes","k8s","vllm","grafana","loki","hmac","llamaguard",
        "gdpr","pwa","tauri","pydantic","sqlalchemy","fastapi",
        "agent swarm","agent mesh","agent marketplace","self-evo",
        "sdar","circuit breaker","blue-green","canary",
        "mcp","a2a","federated","lazy generation",
        "knowledge graph","workflow builder","debate mode",
        "approval manager","failure manager","cost manager",
        "policy engine","context builder","intent detector",
        "rt-bnp","dcl-geo","dcl","cloud library",
        "backtest","backtesting","백테스트","백테스팅",
        "session memory","config loader","json-rpc",
        "state machine","statechart","stategraph",
        "decision engine","decision schema",
        "evidence pack","intent frame",
        "response envelope","kill switch",
        "rate limit","rate_limit","fallback chain",
        "checkpoint","ttl","tone adapter","toneadapter",
        "ambient intelligence","앰비언트",
        "carl rogers","empathic","공감 대화",
        "contributing.md","기여 가이드",
        "backupmanager","backup manager","백업 관리",
        "ssl","tls","certificate","인증서",
        "marketplace","mesh","specialization",
        "trace_id","trace id","슬리피지","slippage",
        "xai","explainability","설명 가능",
    ]

    for i, line in enumerate(lines):
        line_no = i + 1
        text = line.rstrip()
        if not text.strip():
            continue

        # 섹션 결정
        sec = "OTHER"
        for sk, (s, e) in SECTIONS.items():
            if s <= line_no <= e:
                sec = sk
                break

        all_lines.append((line_no, text, sec))

        # 모듈 ID 추출
        for m in mod_pattern.finditer(text):
            mid = m.group(1)
            module_ids[mid].append((line_no, text, sec))

        # 파일 경로 추출
        for m in path_pattern.finditer(text):
            fp = m.group(1)
            # 파일명만 추출 (경로의 마지막 부분)
            fname = fp.split('/')[-1].replace('.py','').replace('.rs','').replace('.tsx','').replace('.ts','')
            file_paths[fname].append((line_no, text, sec))
            file_paths[fp].append((line_no, text, sec))

        # 기술 용어 매칭
        text_lower = text.lower()
        for term in TECH_TERMS:
            if term in text_lower:
                tech_terms[term].append((line_no, text, sec))

    return module_ids, file_paths, tech_terms, all_lines


def build_step7_index():
    """STEP7 파일별 줄 인덱스: {prefix: [(line_no, text)]}
    + feature_id 인덱스: {feature_id_lower: [(prefix, line_no, text)]}
    """
    step7_lines = {}
    step7_fid_index = defaultdict(list)

    fid_pattern = re.compile(r'\b(S7[A-Z]{1,3}-\d{3})\b', re.IGNORECASE)

    for fn in sorted(os.listdir(STEP7_DIR)):
        if not (fn.startswith("STEP7-") and fn.endswith(".md")):
            continue
        prefix = fn.split("_")[0]  # "STEP7-B"
        path = os.path.join(STEP7_DIR, fn)
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        step7_lines[prefix] = [(i+1, l.rstrip()) for i, l in enumerate(lines)]

        # feature ID 인덱스
        for i, l in enumerate(lines):
            for m in fid_pattern.finditer(l):
                fid = m.group(1).upper()
                step7_fid_index[fid].append((prefix, i+1, l.rstrip()))

    return step7_lines, step7_fid_index


# ═══════════════════════════════════════════════════════
# 2. 항목별 식별자 추출
# ═══════════════════════════════════════════════════════

def extract_identifiers(item):
    """항목에서 검색용 식별자 추출:
    - module_ids: ["I-18", "S-2", ...]
    - file_hints: ["i18_self_evo_engine", ...]
    - tech_terms: ["self-evo", "langgraph", ...]
    - feature_id: "D202-130"
    - s7_ids: ["S7B-003", ...]  (feature_name에 포함된 S7x-xxx)
    """
    fname = item.get("feature_name", "")
    fid = item["feature_id"]

    ids = {
        "module_ids": [],
        "file_hints": [],
        "tech_terms": [],
        "feature_id": fid,
        "s7_ids": [],
        "core_terms": [],
    }

    # 모듈 ID 추출
    mod_pattern = re.compile(r'\b([ISABCDE]-\d{1,2}|EVX-\d)\b')
    for m in mod_pattern.finditer(fname):
        ids["module_ids"].append(m.group(1))

    # S7x-xxx ID 추출 (feature_name에 있는 경우)
    s7_pattern = re.compile(r'\b(S7[A-Z]{1,3}-\d{3})\b', re.IGNORECASE)
    for m in s7_pattern.finditer(fname):
        ids["s7_ids"].append(m.group(1).upper())
    # feature_id 자체가 S7 형식인 경우
    if re.match(r'^S7[A-Z]', fid):
        ids["s7_ids"].append(fid)

    # 파일명 힌트 추출 (snake_case 이름)
    # "I-18 Self-evo Engine" → "i18_self_evo_engine"
    for mid in ids["module_ids"]:
        prefix = mid.lower().replace("-", "")
        ids["file_hints"].append(prefix)

    # 기술 용어 추출
    fname_lower = fname.lower()
    TECH_MAP = {
        "langgraph": "langgraph", "parl": "parl", "shap": "shap", "lime": "lime",
        "rag": "rag", "neo4j": "neo4j", "qdrant": "qdrant", "redis": "redis",
        "kubernetes": "kubernetes", "k8s": "k8s", "vllm": "vllm",
        "grafana": "grafana", "loki": "loki", "hmac": "hmac",
        "llamaguard": "llamaguard", "gdpr": "gdpr", "pwa": "pwa",
        "agent swarm": "agent swarm", "agent mesh": "agent mesh",
        "self-evo": "self-evo", "sdar": "sdar",
        "circuit breaker": "circuit breaker", "kill switch": "kill switch",
        "mcp": "mcp", "a2a": "a2a", "federated": "federated",
        "knowledge graph": "knowledge graph", "debate": "debate mode",
        "workflow builder": "workflow builder",
        "rt-bnp": "rt-bnp", "dcl": "dcl", "cloud library": "cloud library",
        "backtest": "backtesting", "백테스트": "백테스팅",
        "json-rpc": "json-rpc", "state machine": "state machine",
        "rate limit": "rate limit", "rate_limit": "rate_limit",
        "fallback": "fallback chain", "checkpoint": "checkpoint",
        "ttl": "ttl", "toneadapter": "toneadapter", "tone adapter": "tone adapter",
        "ambient": "ambient intelligence", "앰비언트": "앰비언트",
        "carl rogers": "carl rogers", "공감 대화": "공감 대화",
        "contributing": "contributing.md",
        "backup": "backupmanager", "백업": "백업 관리",
        "ssl": "ssl", "tls": "tls", "인증서": "인증서",
        "marketplace": "marketplace", "specialization": "specialization",
        "trace_id": "trace_id", "슬리피지": "슬리피지", "slippage": "slippage",
        "xai": "xai", "explainability": "explainability",
        "lazy generation": "lazy generation",
        "approval": "approval manager", "cost manager": "cost manager",
    }
    for trigger, term in TECH_MAP.items():
        if trigger in fname_lower:
            ids["tech_terms"].append(term)

    # 핵심 용어 추출 (한/영 고유명사, 3글자 이상)
    tokens = re.split(r'[\s/\-_,()[\]{}:;+]+', fname)
    stopwords = {"구현","기반","관련","설정","시스템","모듈","엔진","매니저","통합","지원",
                 "기능","처리","관리","추가","확장","적용","자동","수동","전체","최소","최대",
                 "for","the","and","with","from","into","based","using","via",
                 "의","를","을","에","는","은","이","가","등","및","또는"}
    for t in tokens:
        t_clean = t.strip("·.!?#\"'")
        if len(t_clean) >= 3 and t_clean.lower() not in stopwords:
            ids["core_terms"].append(t_clean)

    return ids


# ═══════════════════════════════════════════════════════
# 3. 팩트 기반 검증
# ═══════════════════════════════════════════════════════

def verify_item(item, identifiers, p2_mod_idx, p2_fp_idx, p2_tech_idx, p2_all_lines,
                s7_lines, s7_fid_idx):
    """단일 항목 팩트 검증. 반환: (classification, evidence_list, reason)"""

    fid = item["feature_id"]
    vs = item["version_scope"]
    agent = item.get("agent", "")
    action = item.get("action", "")
    substatus = item.get("substatus", "")
    step7_note = item.get("step7_note", "")

    evidence = []

    # 관련 섹션 결정
    if "," in vs:
        versions = [v.strip() for v in vs.split(",")]
        order = {"V3":4,"V2":3,"V1":2,"V0":1}
        hi_v = max(versions, key=lambda v: order.get(v, 0))
    else:
        hi_v = vs

    relevant_phase_secs = VERSION_SECTIONS.get(hi_v, [])
    relevant_s6_secs = AGENT_S6.get(agent, [])
    relevant_secs = set(relevant_phase_secs + relevant_s6_secs)

    # ── 검색 A: feature_id 직접 검색 in PART2 ──
    fid_lower = fid.lower()
    for (ln, text, sec) in p2_all_lines:
        if fid_lower in text.lower():
            evidence.append({
                "source": "PART2",
                "section": sec,
                "line": ln,
                "text": text[:150],
                "match_type": "feature_id",
                "match_value": fid
            })

    # ── 검색 B: 모듈 ID (I-18 등) in PART2 ──
    for mid in identifiers["module_ids"]:
        if mid in p2_mod_idx:
            for (ln, text, sec) in p2_mod_idx[mid]:
                if sec in relevant_secs or sec.startswith("§6"):
                    evidence.append({
                        "source": "PART2",
                        "section": sec,
                        "line": ln,
                        "text": text[:150],
                        "match_type": "module_id",
                        "match_value": mid
                    })

    # ── 검색 C: 파일 경로 in PART2 ──
    for fhint in identifiers["file_hints"]:
        for fp_key, entries in p2_fp_idx.items():
            if fhint in fp_key.lower():
                for (ln, text, sec) in entries:
                    evidence.append({
                        "source": "PART2",
                        "section": sec,
                        "line": ln,
                        "text": text[:150],
                        "match_type": "file_path",
                        "match_value": fp_key
                    })

    # ── 검색 D: 기술 용어 in PART2 관련 섹션만 ──
    for term in identifiers["tech_terms"]:
        if term in p2_tech_idx:
            for (ln, text, sec) in p2_tech_idx[term]:
                if sec in relevant_secs or sec.startswith("§6"):
                    evidence.append({
                        "source": "PART2",
                        "section": sec,
                        "line": ln,
                        "text": text[:150],
                        "match_type": "tech_term",
                        "match_value": term
                    })

    # ── 검색 E: S7 ID in STEP7 index ──
    for s7id in identifiers["s7_ids"]:
        if s7id in s7_fid_idx:
            for (prefix, ln, text) in s7_fid_idx[s7id]:
                evidence.append({
                    "source": prefix,
                    "section": "",
                    "line": ln,
                    "text": text[:150],
                    "match_type": "s7_feature_id",
                    "match_value": s7id
                })

    # ── 검색 F: feature_id in STEP7 (S7AE-xxx 형식이 아닌 경우도) ──
    step7_prefixes = AGENT_STEP7.get(agent, [])
    if not step7_prefixes:
        step7_prefixes = [p for ps in AGENT_STEP7.values() for p in ps]

    for prefix in step7_prefixes:
        if prefix not in s7_lines:
            continue
        for (ln, text) in s7_lines[prefix]:
            if fid_lower in text.lower():
                evidence.append({
                    "source": prefix,
                    "section": "",
                    "line": ln,
                    "text": text[:150],
                    "match_type": "feature_id_in_step7",
                    "match_value": fid
                })

    # ── 검색 G: 핵심 용어 in STEP7 관련 파일 (개별 term이 아니라 feature_name 전체 핵심 조합) ──
    core = identifiers["core_terms"]
    if len(core) >= 2 and not evidence:
        # STEP7에서 핵심 용어 2개 이상 동시 존재하는 줄 찾기
        for prefix in step7_prefixes:
            if prefix not in s7_lines:
                continue
            for (ln, text) in s7_lines[prefix]:
                text_lower = text.lower()
                matched_core = [t for t in core[:4] if t.lower() in text_lower]
                if len(matched_core) >= 2:
                    evidence.append({
                        "source": prefix,
                        "section": "",
                        "line": ln,
                        "text": text[:150],
                        "match_type": "core_terms_combo",
                        "match_value": "+".join(matched_core)
                    })

    # ── 검색 H: 핵심 용어 in PART2 관련 섹션 (2개 이상 동시) ──
    if len(core) >= 2:
        for (ln, text, sec) in p2_all_lines:
            if sec not in relevant_secs and not sec.startswith("§6"):
                continue
            text_lower = text.lower()
            matched_core = [t for t in core[:4] if t.lower() in text_lower]
            if len(matched_core) >= 2:
                evidence.append({
                    "source": "PART2",
                    "section": sec,
                    "line": ln,
                    "text": text[:150],
                    "match_type": "core_terms_combo",
                    "match_value": "+".join(matched_core)
                })

    # ═══ 분류 결정 ═══
    # evidence 중복 제거 (같은 줄 + 같은 소스)
    seen = set()
    unique_evidence = []
    for e in evidence:
        key = (e["source"], e["line"])
        if key not in seen:
            seen.add(key)
            unique_evidence.append(e)
    evidence = unique_evidence

    # 분류
    p2_evidence = [e for e in evidence if e["source"] == "PART2"]
    s7_evidence = [e for e in evidence if e["source"].startswith("STEP7")]

    # PART2에서 feature_id 직접 발견
    p2_fid = [e for e in p2_evidence if e["match_type"] == "feature_id"]
    # PART2에서 모듈ID/파일경로 발견 (관련 섹션)
    p2_module = [e for e in p2_evidence if e["match_type"] in ("module_id", "file_path")]
    # PART2에서 기술용어 발견 (관련 섹션)
    p2_tech = [e for e in p2_evidence if e["match_type"] == "tech_term"]
    # PART2에서 핵심용어 조합 발견
    p2_core = [e for e in p2_evidence if e["match_type"] == "core_terms_combo"]
    # STEP7에서 발견
    s7_fid = [e for e in s7_evidence if e["match_type"] in ("s7_feature_id", "feature_id_in_step7")]
    s7_core = [e for e in s7_evidence if e["match_type"] == "core_terms_combo"]

    # ── EXACT_MATCH: PART2에 feature_id 또는 (모듈ID + 기술용어) 관련 섹션 발견 ──
    if p2_fid:
        in_relevant = [e for e in p2_fid if e["section"] in relevant_secs]
        reason = f"PART2 L{p2_fid[0]['line']}에 feature_id '{fid}' 직접 존재"
        if in_relevant:
            reason = f"PART2 {in_relevant[0]['section']} L{in_relevant[0]['line']}에 feature_id 직접 존재"
        return "EXACT_MATCH", evidence, reason

    if p2_module and p2_tech:
        best_mod = p2_module[0]
        best_tech = p2_tech[0]
        return "EXACT_MATCH", evidence, (
            f"PART2 {best_mod['section']} L{best_mod['line']}에 모듈 {best_mod['match_value']} 존재 + "
            f"L{best_tech['line']}에 기술용어 '{best_tech['match_value']}' 존재"
        )

    # ── UPPER_MODULE: 모듈ID 또는 파일경로가 관련 섹션에 존재 ──
    if p2_module:
        relevant_mod = [e for e in p2_module if e["section"] in relevant_secs]
        if relevant_mod:
            best = relevant_mod[0]
            return "UPPER_MODULE", evidence, (
                f"PART2 {best['section']} L{best['line']}에 상위 모듈 {best['match_value']} 정의 — "
                f"인용: \"{best['text'][:80]}\""
            )
        else:
            best = p2_module[0]
            return "UPPER_MODULE", evidence, (
                f"PART2 {best['section']} L{best['line']}에 모듈 {best['match_value']} 존재 (비관련 섹션)"
            )

    # ── UPPER_MODULE: 기술용어가 관련 §6 섹션에 존재 ──
    if p2_tech:
        s6_tech = [e for e in p2_tech if e["section"].startswith("§6")]
        if s6_tech:
            best = s6_tech[0]
            return "UPPER_MODULE", evidence, (
                f"PART2 {best['section']} L{best['line']}에 기술용어 '{best['match_value']}' 존재 — "
                f"인용: \"{best['text'][:80]}\""
            )
        phase_tech = [e for e in p2_tech if e["section"] in relevant_secs]
        if phase_tech:
            best = phase_tech[0]
            return "UPPER_MODULE", evidence, (
                f"PART2 {best['section']} L{best['line']}에 기술용어 '{best['match_value']}' 존재 — "
                f"인용: \"{best['text'][:80]}\""
            )

    # ── UPPER_MODULE: PART2 핵심용어 조합 발견 ──
    if p2_core:
        best = p2_core[0]
        return "UPPER_MODULE", evidence, (
            f"PART2 {best['section']} L{best['line']}에 핵심용어 조합 '{best['match_value']}' 발견 — "
            f"인용: \"{best['text'][:80]}\""
        )

    # ── STEP7 기반 판정 ──
    if s7_fid:
        best = s7_fid[0]
        return "UPPER_MODULE", evidence, (
            f"{best['source']} L{best['line']}에 S7 ID '{best['match_value']}' 직접 존재 — "
            f"PART2 §6→STEP7 참조 구조로 커버 — 인용: \"{best['text'][:80]}\""
        )

    if s7_core:
        best = s7_core[0]
        return "UPPER_MODULE", evidence, (
            f"{best['source']} L{best['line']}에 핵심용어 '{best['match_value']}' 발견 — "
            f"PART2 §6→STEP7 참조 구조로 커버 — 인용: \"{best['text'][:80]}\""
        )

    # ── RECLASSIFIED 후보: action/substatus 기반 (단, evidence 없는 경우의 fallback) ──
    if action == "RECLASSIFY_NA":
        return "RECLASSIFIED", evidence, f"action=RECLASSIFY_NA, substatus={substatus}"

    if action == "SKIP" and substatus != "MISSING_CONFIRMED":
        return "RECLASSIFIED", evidence, f"action=SKIP, PART2/STEP7 양쪽 증거 없음"

    if substatus == "NOT_APPLICABLE":
        return "RECLASSIFIED", evidence, f"substatus=NOT_APPLICABLE, PART2/STEP7 양쪽 증거 없음"

    # ── NOT_FOUND: 증거 없음 ──
    return "NOT_FOUND", evidence, "PART2+STEP7 양쪽 모두 해당 항목 증거 미발견"


# ═══════════════════════════════════════════════════════
# 4. 메인
# ═══════════════════════════════════════════════════════

def load_excluded_ids():
    """Step1 제외 67건"""
    with open(f"{BASE_DIR}/consolidated_missing.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    all_ids = set(d["feature_id"] for d in data["items"])
    excluded = set()
    for fn in os.listdir(STEP1_DIR):
        if fn.startswith("3-") and fn.endswith(".md"):
            with open(f"{STEP1_DIR}/{fn}", "r", encoding="utf-8") as f:
                content = f.read()
            for h in re.findall(r"^### (\S+)", content, re.MULTILINE):
                if h in all_ids:
                    excluded.add(h)
    return excluded


def main():
    print("=" * 70)
    print("v10 Step 2 전수 팩트 검증 v2 — 줄 단위 증거 기반")
    print("=" * 70)

    # 1. 데이터 로드
    print("\n[1] 데이터 로드...")
    with open(f"{BASE_DIR}/consolidated_missing.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    all_items = data["items"]

    excluded = load_excluded_ids()
    target = [d for d in all_items if d["feature_id"] not in excluded]
    print(f"  전체: {len(all_items)}, 제외: {len(excluded)}, 대상: {len(target)}")
    assert len(target) == 1001

    # 2. PART2 인덱스 빌드
    print("\n[2] PART2 인덱스 빌드...")
    with open(PART2_PATH, "r", encoding="utf-8") as f:
        p2_lines = f.readlines()
    p2_mod, p2_fp, p2_tech, p2_all = build_part2_index(p2_lines)
    print(f"  모듈ID: {len(p2_mod)}종, 파일경로: {len(p2_fp)}종, 기술용어: {len(p2_tech)}종, 전체줄: {len(p2_all)}")

    # 3. STEP7 인덱스 빌드
    print("\n[3] STEP7 인덱스 빌드...")
    s7_lines, s7_fid = build_step7_index()
    print(f"  파일: {len(s7_lines)}개, S7 ID: {len(s7_fid)}종")

    # 4. 전수 검증
    print("\n[4] 1,001건 전수 팩트 검증...")
    results = []
    for i, item in enumerate(target):
        if (i + 1) % 200 == 0:
            print(f"  진행: {i+1}/1001")

        identifiers = extract_identifiers(item)
        classification, evidence, reason = verify_item(
            item, identifiers, p2_mod, p2_fp, p2_tech, p2_all, s7_lines, s7_fid
        )

        results.append({
            "feature_id": item["feature_id"],
            "feature_name": item["feature_name"],
            "version_scope": item["version_scope"],
            "severity": item["severity"],
            "agent": item.get("agent", ""),
            "action": item.get("action", ""),
            "substatus": item.get("substatus", ""),
            "step7_note": item.get("step7_note", ""),
            "category": item.get("category", ""),
            "classification": classification,
            "evidence": evidence,
            "evidence_count": len(evidence),
            "reason": reason,
        })

    # 5. 통계
    print("\n" + "=" * 70)
    print("[5] 팩트 검증 결과 통계")
    print("=" * 70)

    cls_dist = Counter(r["classification"] for r in results)
    for cls in ["EXACT_MATCH", "UPPER_MODULE", "RECLASSIFIED", "NOT_FOUND"]:
        print(f"  {cls}: {cls_dist.get(cls, 0)}건")
    print(f"  합계: {sum(cls_dist.values())}건")

    # evidence 있는 vs 없는
    with_ev = sum(1 for r in results if r["evidence_count"] > 0)
    no_ev = sum(1 for r in results if r["evidence_count"] == 0)
    print(f"\n  증거 있음: {with_ev}건, 증거 없음: {no_ev}건")

    # NOT_FOUND 상세
    nf = [r for r in results if r["classification"] == "NOT_FOUND"]
    if nf:
        print(f"\n  NOT_FOUND {len(nf)}건 severity:")
        nf_sev = Counter(r["severity"] for r in nf)
        for s in ["BLOCKER","HIGH","MEDIUM","LOW"]:
            print(f"    {s}: {nf_sev.get(s, 0)}")
        nf_act = Counter(r["action"] for r in nf)
        print(f"  NOT_FOUND action: {dict(nf_act)}")

    # RECLASSIFIED 상세
    rc = [r for r in results if r["classification"] == "RECLASSIFIED"]
    if rc:
        rc_ev = sum(1 for r in rc if r["evidence_count"] > 0)
        print(f"\n  RECLASSIFIED {len(rc)}건 (증거있음: {rc_ev})")

    # 6. 저장
    output = {
        "_meta": {
            "version": "v2_fact_based",
            "total": len(results),
            "classification_dist": dict(cls_dist),
            "with_evidence": with_ev,
            "without_evidence": no_ev,
        },
        "items": results,
    }

    out_path = f"{BASE_DIR}/v10_step2_factcheck_result.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n→ {out_path} 저장 완료")

    print("\n" + "=" * 70)
    print("Phase A v2 완료 — 에이전트 병렬 검증 준비 완료")
    print("=" * 70)


if __name__ == "__main__":
    main()
