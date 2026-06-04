# -*- coding: utf-8 -*-
"""VAMOS D1 1-6 (sot-check method-c -> claude_md_gap_report) + 1-7 (obsidian gap)."""
import os, re, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from d1_common import *  # noqa

CLAUDE_SRC = os.path.join(SOT_DIR, "CLAUDE.md")
OBSIDIAN = os.path.join(ROOT, "VAMOS HOME", "OBSIDIAN-STRATEGY-v3.md")
SOT_CHECK_DIR = os.path.join(PHASE0, "extraction", "sot_check")

# Canonical design facts (Part2/SOT 정본 + LOCK registry) that an enhanced CLAUDE.md should cover.
# Each: (fact_id, description, presence_regex in CLAUDE.md, part2_regex for corroboration)
CANON_FACTS = [
    ("QOD_L2_BAN",   "QoD < 0.4 → L2 벡터 삽입 금지",                 r"QoD\s*[^\n]{0,12}0?\.4",                r"QoD\s*<\s*0?\.4"),
    ("QOD_HOLD",     "QoD < 0.7 → 출력 보류",                         r"QoD\s*[^\n]{0,12}0?\.7|출력\s*보류",     r"0?\.7\s*[^\n]{0,10}보류"),
    ("HYBRID_RATIO", "Hybrid Search α=0.3(BM25)/vector=0.7",          r"(?:Hybrid|하이브리드)[^\n]{0,30}0?\.[37]",r"하이브리드|Hybrid"),
    ("CONF_THRESH",  "confidence 임계값 0.85/0.60/0.30",              r"confidence|신뢰도",                      r"confidence|신뢰도"),
    ("COST_MONTHLY", "비용 상한 ₩40,000/월 (V1)",                     r"40[,.]?000|₩?\s*40\s*K",                 r"40[,.]?000"),
    ("COST_GATE",    "CostGate 80%/100% 2단",                         r"80\s*%[^\n]{0,8}100\s*%|CostGate",       r"80\s*%[^\n]{0,8}100\s*%"),
    ("FIVE_GATE",    "5-Gate 실행 순서 (Policy→Approval→Cost→Evidence→SelfCheck)", r"5-?Gate|PolicyGate|5\s*게이트", r"5-?Gate|PolicyGate"),
    ("NEVER_AUTO",   "NEVER_AUTO 10개 (자동 금지 영역)",              r"NEVER_AUTO|자동\s*금지",                 r"NEVER_AUTO"),
    ("MEMORY_L0L3",  "메모리 L0~L3 계층",                             r"L0[^\n]{0,30}L3|메모리\s*계층",          r"L0.{0,30}L3"),
    ("MAX_RETRIES",  "MCP max_retries (V1/V2=2, V3=3)",               r"max_retries|재시도\s*횟수",              r"max_retries"),
    ("STATE_MACHINE","S0~S8 상태 머신 (LangGraph DAG)",               r"S0[^\n]{0,40}S8|상태\s*머신|9-?State", r"S0.{0,40}S8|9-?State"),
    ("FIVE_FIELDS",  "ResponseEnvelope 5필드 LOCK",                   r"ResponseEnvelope|5\s*필드",              r"ResponseEnvelope"),
]

def check_1_6():
    claude = read_text(CLAUDE_SRC)
    part2 = read_text(PART2) if os.path.exists(PART2) else ""
    facts = []
    gaps = []
    for fid, desc, crx, prx in CANON_FACTS:
        in_claude = bool(re.search(crx, claude, re.I))
        in_part2 = bool(re.search(prx, part2, re.I))
        status = "PRESENT" if in_claude else ("GAP" if in_part2 else "GAP_NO_PART2")
        facts.append({"fact_id": fid, "desc": desc, "in_claude_md": in_claude,
                      "in_part2": in_part2, "status": status})
        if not in_claude:
            gaps.append({"fact_id": fid, "desc": desc, "in_part2": in_part2,
                         "recommendation": "Phase 2-1 CLAUDE.md 보강 시 반드시 포함"})
    out = {
        "metadata": {
            "mode": "method-c", "target": "CLAUDE.md",
            "claude_md_source": os.path.relpath(CLAUDE_SRC, ROOT),
            "canonical_facts_checked": len(CANON_FACTS),
            "present": sum(1 for f in facts if f["in_claude_md"]),
            "gap_count": len(gaps),
            "note": "방식 C 요약 파일이 별도 존재하지 않으므로, method-c의 목적(Phase 2-1 CLAUDE.md 보강 GAP 도출)에 맞춰 "
                    "현 CLAUDE.md(docs/sot/CLAUDE.md) ↔ Part2 정본 + 핵심 LOCK 상수 대조로 GAP을 산출. "
                    "GAP은 D1 PASS를 차단하지 않으며 Phase 2-1 입력이다.",
            "timestamp": now_iso(), "input_hash": sha256_file(CLAUDE_SRC), "skill_version": SKILL_VERSION,
        },
        "facts": facts, "claude_md_gaps": gaps,
    }
    write_json(os.path.join(SOT_CHECK_DIR, "CLAUDE_md_sot_check.json"), out)
    p = write_json(os.path.join(SOT_CHECK_DIR, "claude_md_gap_report.json"),
                   {"gap_count": len(gaps), "gaps": gaps, "phase": "input to Phase 2-1",
                    "timestamp": now_iso(), "input_hash": sha256_file(CLAUDE_SRC),
                    "skill_version": SKILL_VERSION})
    return {"present": out["metadata"]["present"], "gap_count": len(gaps),
            "gaps": [g["fact_id"] for g in gaps], "path": p}

def check_1_7():
    domains = list_domain_dirs()
    impl_domains = [d for d in domains if d not in META_ONLY and d != "Ai-investing-detail"]
    obs = read_text(OBSIDIAN) if os.path.exists(OBSIDIAN) else ""
    obs_exists = os.path.exists(OBSIDIAN)
    # count how many SOT2 domains are referenced in the Obsidian strategy (by id prefix like 6-4 / name)
    referenced = []
    missing = []
    for d in domains:
        did = d.split("_")[0]                       # e.g. 6-4
        name_core = d.split("_", 1)[1] if "_" in d else d
        if obs and (re.search(r"\b" + re.escape(did) + r"\b", obs) or name_core.split("-")[0] in obs):
            referenced.append(d)
        else:
            missing.append(d)
    # rough module/domain counts mentioned in obsidian
    m_domain = re.findall(r"(\d{2,3})\s*개?\s*도메인", obs)
    m_module = re.findall(r"(\d{2,3})\s*개?\s*모듈", obs)
    out = {
        "metadata": {
            "obsidian_strategy": os.path.relpath(OBSIDIAN, ROOT) if obs_exists else None,
            "obsidian_exists": obs_exists,
            "sot2_domains_total": len(domains), "sot2_impl_domains": len(impl_domains),
            "domains_referenced_in_obsidian": len(referenced),
            "domains_not_referenced": len(missing),
            "domain_counts_mentioned": m_domain, "module_counts_mentioned": m_module,
            "note": "Obsidian 전략(설계 시점)은 SOT2 30개 도메인 다단계 확장 이전 작성 → 도메인/모듈 수 차이는 "
                    "예상된 GAP(Phase 2-3 Obsidian 노트 생성 입력). D1 PASS 차단 안 함.",
            "timestamp": now_iso(),
            "input_hash": sha256_file(OBSIDIAN) if obs_exists else None, "skill_version": SKILL_VERSION,
        },
        "referenced_domains": referenced, "unreferenced_domains": missing,
    }
    p = write_json(os.path.join(SOT_CHECK_DIR, "obsidian_gap_report.json"), out)
    return {"obsidian_exists": obs_exists, "referenced": len(referenced),
            "unreferenced": len(missing), "path": p}

if __name__ == "__main__":
    r6 = check_1_6(); r7 = check_1_7()
    print(json.dumps({"1-6": r6, "1-7": r7}, ensure_ascii=False, indent=2))
