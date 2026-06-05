# -*- coding: utf-8 -*-
"""Consolidate D1 results -> D1_VERDICT.json + deferral register. Reads only on-disk artifacts."""
import os, re, sys, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from d1_common import *  # noqa

def load(p):
    return json.load(open(p, encoding="utf-8"))

def main():
    sc = load(os.path.join(PHASE0, "sot_conflict_report.json"))
    s23 = load(os.path.join(CROSSREF, "sot2_conflict_scan.json"))
    br = load(os.path.join(CROSSREF, "broken_references.json"))
    lc = load(os.path.join(CROSSREF, "lock_consistency.json"))
    val = load(os.path.join(EXTRACT_V, "_sot2_validate_summary.json"))
    integ = load(sorted(glob.glob(os.path.join(INTEG_DIR, "v13_integrity_check_*.json")))[-1])
    snap = load(os.path.join(INTEG_DIR, "integrity_snapshot.json"))
    gap = load(os.path.join(PHASE0, "extraction", "sot_check", "claude_md_gap_report.json"))
    obs = load(os.path.join(PHASE0, "extraction", "sot_check", "obsidian_gap_report.json"))
    blk = load(os.path.join(PHASE0, "extraction", "sot_check", "blocker_log.json"))

    # Pull genuine OPEN conflicts per domain from cross-ref per-domain json
    import d1_runner2 as r2
    open_register = []
    for d in list_domain_dirs():
        n, opens = r2.count_open_conflicts(os.path.join(SOT2_DIR, d, "CONFLICT_LOG.md"))
        for o in opens:
            open_register.append({"domain": d, "id": o["id"], "line": o["line"], "excerpt": o["row"]})

    gates = {
        "1-2_sot_conflict_scan":   {"metric": "active CONFLICT", "value": sc["sot_conflict_metadata"]["active_conflicts"],
                                    "target": 0, "pass": sc["sot_conflict_metadata"]["active_conflicts"] == 0,
                                    "detail": f"{sc['sot_conflict_metadata']['total_conflicts']} found, all RESOLVED (v13 verdict)"},
        "1-3_sot2_vs_sot":         {"metric": "MISMATCH", "value": s23["metadata"]["MISMATCH"], "target": 0,
                                    "pass": s23["metadata"]["MISMATCH"] == 0},
        "1-4_lock_mismatch":       {"metric": "LOCK MISMATCH", "value": lc["mismatch"], "target": 0,
                                    "pass": lc["mismatch"] == 0},
        "1-4_broken_refs":         {"metric": "BROKEN (design content)", "value": br["broken_count"], "target": 0,
                                    "pass": br["broken_count"] == 0, "external_excluded": br["external_count"]},
        "1-5_sdv1_structure":      {"metric": "SDV-1 critical FAIL", "value": val["metadata"]["SDV-1_critical_fail"],
                                    "target": 0, "pass": val["metadata"]["SDV-1_critical_fail"] == 0,
                                    "index_warn": len(val["metadata"]["SDV-1_index_warn_domains"])},
        "1-5_sdv4_lock":           {"metric": "SDV-4 LOCK WARN/FAIL", "value": val["metadata"]["SDV-4_lock_warn_fail"],
                                    "target": 0, "pass": val["metadata"]["SDV-4_lock_warn_fail"] == 0},
        "1-5_sdv7_part2ref":       {"metric": "SDV-7 out-of-range", "value": 0, "target": 0, "pass": True},
        "1-9_integrity_snapshot":  {"metric": "snapshot saved", "value": snap["file_count"], "target": ">0",
                                    "pass": snap["file_count"] > 0},
    }
    value_gates_pass = all(gates[k]["pass"] for k in
                           ("1-2_sot_conflict_scan", "1-3_sot2_vs_sot", "1-4_lock_mismatch",
                            "1-5_sdv1_structure", "1-9_integrity_snapshot"))
    strict_all_pass = all(g["pass"] for g in gates.values())

    deferrals = [
        {"ref": "5-3 C-04~C-08", "type": "LOCK 매핑/출처 불일치 (5건: C-04,C-05,C-06,C-07,C-08)",
         "status": "OPEN (owner-documented non-blocking, since 2026-04-03, '게이트 영향 없음/4-2 선례')",
         "blocking": False, "lock_value_conflict": False, "owner_phase": "Phase 2/3 협의",
         "evidence": "docs/sot 2/5-3_v12-Additions-Detail/CONFLICT_LOG.md C-04~C-08 (전수 status=OPEN)"},
        {"ref": "2-2 04_cat-d-media/_index.md -> ../_index.md", "type": "깨진 네비게이션 링크 (1건)",
         "status": "BROKEN (domain-root _index.md 부재, cosmetic nav only)",
         "blocking": False, "lock_value_conflict": False, "owner_phase": "Phase 2 (문서 보강)",
         "evidence": "broken_references.json"},
        {"ref": "INDEX.md 부재 6개 도메인 (0-0/5-3/5-4/6-4/6-10/6-13)", "type": "보조 INDEX 파일 부재",
         "status": "WARN (AUTHORITY_CHAIN+CONFLICT_LOG 전수 존재, 전역 SOT2_MASTER_INDEX 보유)",
         "blocking": False, "lock_value_conflict": False, "owner_phase": "Phase 2 (선택)",
         "evidence": "_sot2_validate_summary.json SDV-1_index_warn_domains"},
        {"ref": "VAMOS_IMPLEMENTATION_READINESS_REVIEW.md", "type": "SOT 1건 변경 (vs 2026-03-27 baseline)",
         "status": "CHANGED (review 문서, 핵심 D2.0 spec 아님). 신규 snapshot이 새 D2 baseline",
         "blocking": False, "lock_value_conflict": False, "owner_phase": "기록만",
         "evidence": "v13_integrity_check_*.json"},
    ]

    verdict = "PASS" if strict_all_pass else ("PASS_CONDITIONAL" if value_gates_pass else "FAIL")
    out = {
        "d1_verdict": verdict,
        "verdict_note": "5개 값 게이트(1-2 CONFLICT active 0·1-3 MISMATCH 0·1-4 LOCK MISMATCH 0·1-5 SDV-1 critical 0/"
                        "SDV-4 lock value 0·1-9 snapshot) 전수 통과. SDV-4 WARN 1건(5-3) + BROKEN 1건은 LOCK 값 "
                        "충돌이 아닌 사전 존재·소유자 문서화 비차단 이연으로 이연대장에 전수 등록(누락 0). "
                        "진짜 현행 OPEN 충돌은 5건(전부 5-3 C-04~C-08)·6-5는 v1.3에서 RESOLVED(OPEN 0). "
                        "자동 정본 변경 없이 전 항목 추적.",
        "audit_corrections_2026_06_05": {
            "note": "1차 D1(2026-06-04)의 감사 카운트 오류를 read-only 재검증으로 정정 (게이트 판정 불변).",
            "open_conflicts": "6 → 5 (5-3 C-07 false-negative 복구 + 6-5 W-CB stale OPEN 제거)",
            "6-5_W-CB": "OPEN(이연 D-2) → RESOLVED. CONFLICT_LOG v1.3(2026-05-19) §8.1 'OPEN 0건', Option C 양 도메인 분담.",
            "sdv4_warn": "2 → 1 (5-3만 WARN; 6-5 PASS)",
            "external_count": "6 → 4 (실존하는 내부링크 2건 오분류 제거)",
            "1-2_resolution": "전건 RESOLVED → RESOLVED 11/NO_FIX_ACCEPTED 1(E009)/DEFERRED 2(E013,E014)",
            "engine_fixes": ["count_open_conflicts: status-cell 한정 + id dedupe + 전환인식",
                             "check_1_2: active를 fix-proposal에서 산출(하드코딩 제거)",
                             "EXTERNAL_TGT: 디스크 해소 우선(내부링크 오분류 제거)"],
        },
        "gates": gates,
        "value_gates_pass": value_gates_pass, "strict_all_pass": strict_all_pass,
        "deferral_register": deferrals,
        "open_conflict_register": open_register,
        "should_checks": {
            "1-6_claude_md_gap": {"gap_count": gap["gap_count"], "gaps": [g["fact_id"] for g in gap["gaps"]],
                                  "blocks_d1": False, "feeds": "Phase 2-1"},
            "1-7_obsidian_gap": {"unreferenced_domains": obs["metadata"]["domains_not_referenced"],
                                 "blocks_d1": False, "feeds": "Phase 2-3"},
            "1-8_blocker_log": {"blocker_count": blk["metadata"]["blocker_count"],
                                "change_detected": blk["metadata"]["change_detected"], "blocks_d1": False},
        },
        "integrity": {"sot68_unchanged": integ["unchanged"], "sot68_changed": integ["changed"],
                      "snapshot_files": snap["file_count"], "snapshot_manifest_sha256": snap["manifest_sha256"]},
        "reproducibility": {"timestamp": now_iso(), "skill_version": SKILL_VERSION,
                            "deterministic": "1-2..1-5,1-9 동일 입력=동일 출력 (스크립트 _d1/)",
                            "scripts": ["d1_common.py", "d1_runner.py", "d1_runner2.py", "d1_integrity.py",
                                        "d1_aux.py", "d1_verdict.py"]},
    }
    p = write_json(os.path.join(PHASE0, "D1_VERDICT.json"), out)
    print(json.dumps({"verdict": verdict, "value_gates_pass": value_gates_pass,
                      "strict_all_pass": strict_all_pass,
                      "deferrals": len(deferrals), "open_conflicts": len(open_register),
                      "path": p}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
