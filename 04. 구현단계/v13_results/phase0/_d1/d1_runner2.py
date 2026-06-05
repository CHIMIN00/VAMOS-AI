# -*- coding: utf-8 -*-
"""VAMOS D1 — 1-4 (sot2-cross-ref all), 1-5 (validate sot2-all), 1-9 (integrity)."""
import os, re, sys, json, collections
from urllib.parse import unquote
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from d1_common import *  # noqa

SUMMARY = {}
MD_LINK = re.compile(r"\]\(([^)\s]+?\.md)(?:#[^)]*)?\)")
OPEN_CELL = re.compile(r"^\*{0,2}OPEN\*{0,2}$")
# A status-valued cell STARTS with a status keyword (handles "RESOLVED (Option C ...)" / "OPEN 유지 (DEFERRED)").
STATUS_CELL = re.compile(r"^\*{0,2}\s*(OPEN|RESOLVED|WONTFIX|CLOSED)\b", re.I)
LOCK_ID = re.compile(r"LOCK-[A-Z0-9]{2,5}-\d+")
# A genuine conflict row's first cell is a conflict ID (CONF-/CFL-/CF-/CL-/XREF-/W-CB/W-n/C-n/ISS-/SC-/#n ...)
CONFLICT_ID = re.compile(r"^\*{0,2}(W-CB|#\d+|[A-Z]{1,6}-[A-Z0-9]{0,8}-?\d+|[A-Z]{1,4}-\d+)\*{0,2}$")
HEADER_WORDS = {"구분", "ID", "상태", "유형", "충돌 유형", "OPEN", "RESOLVED", "WONTFIX", "합계", "필드", "설명"}
# Targets that point at the external memory system / clearly outside SOT2 (NOT intra-SOT2 design links).
# Note: a bare 'feedback_*'/'user_*' filename can be a legit intra-SOT2 file, so existence on disk is
# checked FIRST (see check_1_4); EXTERNAL is only assigned to UNRESOLVED targets matching this pattern.
EXTERNAL_TGT = re.compile(r"(^|/)(memory/|project_[\w-]+_status\.md|feedback_|user_|reference_)", re.I)
# Lines that intentionally demonstrate a broken link (link-checker test fixtures) — not real refs.
NEG_LINK = re.compile(r"깨진|broken|lychee|nope|존재하지\s*않|invalid\s*link|❌\s*\[")

def domain_of(path):
    rel = os.path.relpath(path, SOT2_DIR)
    parts = rel.split(os.sep)
    return parts[0] if parts else None

# ---------------------------------------------------------------------
# 1-4  /sot2-cross-ref all
# ---------------------------------------------------------------------
def count_open_conflicts(conflict_log_path):
    """Count genuine, CURRENTLY-open conflicts by conflict ID (deduped, transition-aware).

    Robust against the two prior bugs:
      (a) cross-row false-negative: RESOLVED/WONTFIX is judged ONLY on a row's *status cell*
          (a cell that STARTS with the status keyword), never on description cells that merely
          *cite* another conflict's resolution (e.g. 5-3 C-07 text "... W-05 RESOLVED ...").
      (b) stale/duplicate over-count: results are aggregated PER conflict id across all its rows;
          an id is OPEN only if it has >=1 OPEN status cell and 0 RESOLVED/WONTFIX/CLOSED status
          cell anywhere (so a later transition row "W-CB | OPEN | RESOLVED (Option C)" resolves it).
    Returns (distinct_open_count, [{id, line, row}, ...])."""
    if not os.path.exists(conflict_log_path):
        return 0, []
    per_id = {}  # id -> {"has_open": bool, "has_resolved": bool, "first_open_line": int, "row": str}
    order = []
    for ln, line in enumerate(read_text(conflict_log_path).splitlines(), 1):
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells:
            continue
        cid = cells[0].strip("* ")
        if cells[0] in HEADER_WORDS or not CONFLICT_ID.match(cells[0]):
            continue  # skip header / legend / stat rows
        status_cells = [c for c in cells[1:] if STATUS_CELL.match(c)]
        if not status_cells:
            continue
        is_open = any(re.match(r"^\*{0,2}\s*OPEN\b", c, re.I) for c in status_cells)
        is_res = any(re.match(r"^\*{0,2}\s*(RESOLVED|WONTFIX|CLOSED)\b", c, re.I) for c in status_cells)
        if cid not in per_id:
            per_id[cid] = {"has_open": False, "has_resolved": False, "first_open_line": None, "row": None}
            order.append(cid)
        rec = per_id[cid]
        if is_res:
            rec["has_resolved"] = True
        if is_open:
            rec["has_open"] = True
            if rec["first_open_line"] is None:
                rec["first_open_line"] = ln
                rec["row"] = line.strip()[:220]
    opens = [{"id": cid, "line": per_id[cid]["first_open_line"], "row": per_id[cid]["row"]}
             for cid in order
             if per_id[cid]["has_open"] and not per_id[cid]["has_resolved"]]
    return len(opens), opens

def check_1_4():
    domains = list_domain_dirs()
    design_md = list_design_md()                 # SOT2 design content only (no scaffolding)
    all_md = list(walk_md(SOT2_DIR))             # full set for existence resolution
    existing = set(os.path.normcase(os.path.abspath(p)) for p in all_md)

    broken = []
    external = []
    ref_links = 0
    matrix = collections.defaultdict(lambda: collections.Counter())  # src_domain -> Counter(dst_domain)
    per_domain = {d: {"references": 0, "broken": 0, "external": 0, "lock_ids": 0, "open_conflicts": 0} for d in domains}
    SOT2_ABS = os.path.normcase(os.path.abspath(SOT2_DIR))

    for path in design_md:
        src_dom = domain_of(path)
        base = os.path.dirname(path)
        txt = read_text(path)
        lines = txt.splitlines()
        for m in MD_LINK.finditer(txt):
            raw = m.group(1)
            if raw.startswith(("http://", "https://", "mailto:")):
                continue
            line_no = txt.count("\n", 0, m.start())
            line_txt = lines[line_no] if 0 <= line_no < len(lines) else ""
            if NEG_LINK.search(line_txt):
                continue   # skip link-checker negative-test fixtures (e.g. "[bad](./nope.md) lychee fail")
            target = unquote(raw)            # decode %20 etc.
            ref_links += 1
            if src_dom in per_domain:
                per_domain[src_dom]["references"] += 1
            # --- resolve disk existence FIRST (a 'feedback_*'/'user_*' filename can be a valid
            #     intra-SOT2 file; only UNRESOLVED targets are classified external/broken) ---
            cand = os.path.normcase(os.path.abspath(os.path.join(base, target)))
            ok = cand in existing
            if not ok:
                for root_try in ([os.path.join(SOT2_DIR, src_dom)] if src_dom else []) + [SOT2_DIR]:
                    c2 = os.path.normcase(os.path.abspath(os.path.join(root_try, target)))
                    if c2 in existing:
                        ok = True; cand = c2; break
            if not ok:
                # UNRESOLVED: external if it points at the memory system / clearly outside SOT2,
                # otherwise a genuine broken design reference.
                outside = not os.path.abspath(os.path.join(base, target)).lower().startswith(SOT2_ABS.lower())
                if EXTERNAL_TGT.search(target.replace("\\", "/")) or outside:
                    external.append({"source": os.path.relpath(path, SOT2_DIR), "target": target, "domain": src_dom})
                    if src_dom in per_domain:
                        per_domain[src_dom]["external"] += 1
                    continue
            if ok:
                dst_dom = domain_of(cand) if cand.startswith(SOT2_ABS) else None
                if src_dom and dst_dom and dst_dom != src_dom:
                    matrix[src_dom][dst_dom] += 1
            else:
                broken.append({"source": os.path.relpath(path, SOT2_DIR),
                               "line_target": target, "domain": src_dom})
                if src_dom in per_domain:
                    per_domain[src_dom]["broken"] += 1

    # LOCK ids + open conflicts per domain
    total_open = 0
    open_detail = {}
    for d in domains:
        ac = os.path.join(SOT2_DIR, d, "AUTHORITY_CHAIN.md")
        if os.path.exists(ac):
            ids = set(LOCK_ID.findall(read_text(ac)))
            per_domain[d]["lock_ids"] = len(ids)
        n_open, opens = count_open_conflicts(os.path.join(SOT2_DIR, d, "CONFLICT_LOG.md"))
        per_domain[d]["open_conflicts"] = n_open
        total_open += n_open
        if n_open:
            open_detail[d] = opens

    # LOCK consistency = reuse cross-cutting constants over SOT2 only
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import d1_runner as r1
    sot2_found = r1._scan_corpus_concepts(design_md)
    lock_rows = []
    lock_mismatch = 0
    for cid, rx, allowed, tol, note in CONCEPTS:
        vals = dict(sot2_found[cid])
        bad = sorted(v for v in vals if not any(abs(float(v) - a) <= tol for a in allowed if _isnum(v)))
        if bad:
            lock_mismatch += 1
        lock_rows.append({"concept": cid, "allowed": allowed, "values": {k: len(v) for k, v in vals.items()},
                          "noncanonical": bad, "status": "MISMATCH" if bad else "CONSISTENT", "note": note})

    combined_in = sha256_text("".join(sorted(os.path.relpath(p, SOT2_DIR) for p in all_md)))
    verdict = "CLEAN" if (len(broken) == 0 and lock_mismatch == 0 and total_open == 0) else "ISSUES_FOUND"

    # --- write per-domain json ---
    for d in domains:
        write_json(os.path.join(CROSSREF, f"{d}.json"), {
            "domain": d, "scan_date": now_iso(),
            "results": per_domain[d],
            "skill_version": SKILL_VERSION,
        })

    # --- matrix.md ---
    mlines = ["# SOT 2 교차 참조 매트릭스 (cross_ref_matrix)", "",
              f"> 생성: {now_iso()} · 도메인 {len(domains)}개 · 총 참조 링크 {ref_links} · 도메인간 참조 합계 "
              f"{sum(sum(c.values()) for c in matrix.values())}", "",
              "| src \\ dst | " + " | ".join(d.split('_')[0] for d in domains) + " |",
              "|" + "---|" * (len(domains) + 1)]
    for s in domains:
        row = [s.split('_')[0]]
        for t in domains:
            n = matrix[s][t]
            row.append(str(n) if n else ".")
        mlines.append("| " + " | ".join(row) + " |")
    write_text(os.path.join(CROSSREF, "cross_ref_matrix.md"), "\n".join(mlines) + "\n")
    write_json(os.path.join(CROSSREF, "cross_ref_matrix.json"),
               {"domains": domains, "matrix": {s: dict(matrix[s]) for s in domains},
                "total_ref_links": ref_links, "timestamp": now_iso(), "input_hash": combined_in,
                "skill_version": SKILL_VERSION})

    # --- lock_consistency ---
    write_json(os.path.join(CROSSREF, "lock_consistency.json"),
               {"mismatch": lock_mismatch, "concepts": lock_rows,
                "domain_lock_ids": {d: per_domain[d]["lock_ids"] for d in domains},
                "timestamp": now_iso(), "skill_version": SKILL_VERSION})
    llines = ["# SOT 2 LOCK 일관성 (lock_consistency)", "", f"> 생성: {now_iso()} · MISMATCH={lock_mismatch}", "",
              "| 개념 | 허용값 | 관측값 | 상태 |", "|---|---|---|---|"]
    for r in lock_rows:
        llines.append(f"| {r['concept']} | {r['allowed']} | {r['values']} | {r['status']} |")
    llines += ["", "## 도메인별 LOCK ID 수 (AUTHORITY_CHAIN)", "", "| 도메인 | LOCK ID 수 | CONFLICT OPEN |", "|---|---|---|"]
    for d in domains:
        llines.append(f"| {d} | {per_domain[d]['lock_ids']} | {per_domain[d]['open_conflicts']} |")
    write_text(os.path.join(CROSSREF, "lock_consistency.md"), "\n".join(llines) + "\n")

    # --- broken_references ---
    blines = ["# SOT 2 깨진 참조 (broken_references)", "",
              f"> 생성: {now_iso()} · 범위: SOT2 설계 콘텐츠({len(design_md)} .md, 스캐폴딩 제외)",
              f"> BROKEN={len(broken)} · EXTERNAL(메모리/외부, 비대상)={len(external)} · 총 .md 링크 {ref_links}", ""]
    if broken:
        blines += ["## BROKEN (해소 필요)", "", "| 소스 | 깨진 대상 | 도메인 |", "|---|---|---|"]
        for b in broken[:500]:
            blines.append(f"| {b['source']} | {b['line_target']} | {b['domain']} |")
    else:
        blines.append("BROKEN 0건 — 모든 SOT2 설계 콘텐츠 내부 .md 링크가 디스크에서 해소됨.")
    write_text(os.path.join(CROSSREF, "broken_references.md"), "\n".join(blines) + "\n")
    write_json(os.path.join(CROSSREF, "broken_references.json"),
               {"broken_count": len(broken), "external_count": len(external),
                "total_md_links": ref_links, "design_md_files": len(design_md),
                "broken": broken, "external_sample": external[:50],
                "scope_note": "Design content only; scaffolding dirs (_automation/_verification/_archive/...) "
                              "excluded; %-encoding decoded; out-of-SOT2 targets (memory/project_*_status) "
                              "classified EXTERNAL, not BROKEN.",
                "timestamp": now_iso(), "input_hash": combined_in, "skill_version": SKILL_VERSION})

    SUMMARY["1-4"] = {"BROKEN": len(broken), "EXTERNAL": len(external), "LOCK_MISMATCH": lock_mismatch,
                      "total_open_conflicts": total_open, "open_detail_domains": list(open_detail),
                      "domains": len(domains), "design_md": len(design_md), "total_md_links": ref_links,
                      "verdict": verdict, "out_dir": CROSSREF}
    return SUMMARY["1-4"]


def _isnum(v):
    try:
        float(v); return True
    except Exception:
        return False


# ---------------------------------------------------------------------
# 1-5  /validate sot2-all  (SDV-1..7; 2/5/6 need _extractions -> N/A)
# ---------------------------------------------------------------------
PART2_LINEREF = re.compile(r"Part2\s*L(\d+)")
def check_1_5():
    domains = list_domain_dirs()
    part2_lines = len(read_text(PART2).splitlines()) if os.path.exists(PART2) else 0

    results = {}
    agg = collections.Counter()
    for d in domains:
        ddir = os.path.join(SOT2_DIR, d)
        files = {f: os.path.join(ddir, f) for f in os.listdir(ddir) if f.endswith(".md")}
        # SDV-1: required structural files. Critical = AUTHORITY_CHAIN + CONFLICT_LOG (LOCK authority +
        # conflict ledger). INDEX.md is a SECONDARY per-domain nav file (global SOT2_MASTER_INDEX.md
        # covers all) -> its absence is WARN, not FAIL.
        critical = ["AUTHORITY_CHAIN.md", "CONFLICT_LOG.md"]
        secondary = ["INDEX.md"]
        has_plan = any(f.endswith("_구조화_종합계획서.md") for f in files)
        has_spec = any(f.endswith("_상세명세.md") for f in files)
        crit_missing = [r for r in critical if r not in files]
        sec_missing = [r for r in secondary if r not in files]
        sdv1_missing = crit_missing + sec_missing
        sdv1 = "FAIL" if crit_missing else ("WARN" if sec_missing else "PASS")
        # SDV-3: source_line range -> needs extraction JSON -> N/A
        # SDV-4: LOCK gate = CONFLICT OPEN == 0  (PASS/WARN/FAIL)
        n_open, _ = count_open_conflicts(os.path.join(ddir, "CONFLICT_LOG.md"))
        sdv4 = "PASS" if n_open == 0 else "WARN"
        # SDV-7: Part2 L{n} references within file count
        bad_refs = []
        for fn, fp in files.items():
            for m in PART2_LINEREF.finditer(read_text(fp)):
                n = int(m.group(1))
                if part2_lines and n > part2_lines:
                    bad_refs.append({"file": fn, "lineref": n})
        sdv7 = "PASS" if not bad_refs else "SHIFTED"
        res = {
            "domain": d,
            "SDV-1_structure": {"status": sdv1, "missing": sdv1_missing, "has_plan": has_plan, "has_spec": has_spec},
            "SDV-2_category_sum": {"status": "N/A", "reason": "_extractions/ (SC JSON) absent — no extraction inputs"},
            "SDV-3_source_line": {"status": "N/A", "reason": "_extractions/ (SC JSON) absent"},
            "SDV-4_lock": {"status": sdv4, "open_conflicts": n_open},
            "SDV-5_schema_types": {"status": "N/A", "reason": "_extractions/ (SC JSON) + Pydantic models absent"},
            "SDV-6_canonical_owner": {"status": "N/A", "reason": "_extractions/ (SC JSON) absent"},
            "SDV-7_part2_lineref": {"status": sdv7, "out_of_range": bad_refs[:20], "part2_lines": part2_lines},
            "verdict": "PASS" if (sdv1 in ("PASS", "WARN") and sdv4 == "PASS" and sdv7 == "PASS") else "ATTENTION",
            "timestamp": now_iso(), "skill_version": SKILL_VERSION,
        }
        write_json(os.path.join(EXTRACT_V, f"{d}_validation.json"), res)
        results[d] = res
        agg[res["verdict"]] += 1
        for k in ("SDV-1_structure", "SDV-4_lock", "SDV-7_part2_lineref"):
            agg[k + ":" + res[k]["status"]] += 1

    lock_warn_fail = sum(1 for d in results if results[d]["SDV-4_lock"]["status"] in ("WARN", "FAIL"))
    crit_fail = sum(1 for d in results if results[d]["SDV-1_structure"]["status"] == "FAIL")
    index_warn = [d for d in results if results[d]["SDV-1_structure"]["status"] == "WARN"]
    # aggregate index
    summary = {
        "metadata": {
            "domains": len(domains), "part2_lines": part2_lines,
            "verdict_breakdown": {k: v for k, v in agg.items() if not k.startswith("SDV")},
            "sdv_breakdown": {k: v for k, v in agg.items() if k.startswith("SDV")},
            "SDV-4_lock_warn_fail": lock_warn_fail,
            "SDV-1_critical_fail": crit_fail,
            "SDV-1_index_warn_domains": index_warn,
            "structural_critical_pass": len(results) - crit_fail,
            "structural_pass": agg.get("SDV-1_structure:PASS", 0),
            "note": "SDV-2/5/6 are N/A: the SOT2 SC-JSON extraction layer (_extractions/) does not exist, "
                    "so extraction-count/schema-type/canonical-owner checks have no input. SDV-1/4/7 run "
                    "directly on the .md domain files. SDV-4 (LOCK gate) PASS == CONFLICT OPEN 0.",
            "timestamp": now_iso(), "skill_version": SKILL_VERSION,
        },
        "domains": {d: results[d]["verdict"] for d in results},
    }
    write_json(os.path.join(EXTRACT_V, "_sot2_validate_summary.json"), summary)
    SUMMARY["1-5"] = {"domains": len(domains), "SDV4_warn_fail": lock_warn_fail,
                      "structural_pass": agg.get("SDV-1_structure:PASS", 0),
                      "sdv7_shifted": sum(1 for d in results if results[d]["SDV-7_part2_lineref"]["status"] != "PASS"),
                      "verdict_breakdown": summary["metadata"]["verdict_breakdown"], "out_dir": EXTRACT_V}
    return SUMMARY["1-5"]


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("1-4", "all"):
        check_1_4()
    if which in ("1-5", "all"):
        check_1_5()
    print(json.dumps(SUMMARY, ensure_ascii=False, indent=2))
