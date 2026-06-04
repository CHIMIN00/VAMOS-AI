# -*- coding: utf-8 -*-
"""VAMOS D1 1-9: /integrity all (SOT68 vs EA recorded hashes) + SOT2 SHA-256 snapshot baseline."""
import os, re, sys, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from d1_common import *  # noqa

def find_recorded_hashes():
    """Scan EA01..15 for any recorded SOT source_file hashes (key contains 'hash')."""
    recorded = {}
    for ea in sorted(glob.glob(os.path.join(PHASE0, "extraction", "v13_EA*.json"))):
        try:
            d = json.load(open(ea, encoding="utf-8"))
        except Exception:
            continue
        def walk(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    if "hash" in k.lower() and isinstance(v, dict):
                        for fk, fv in v.items():
                            if isinstance(fv, str) and re.fullmatch(r"[0-9a-fA-F]{64}", fv):
                                recorded.setdefault(os.path.basename(fk), set()).add(fv.lower())
                    walk(v)
            elif isinstance(o, list):
                for x in o:
                    walk(x)
        walk(d)
    return recorded

def integrity_all():
    sot_files = list_sot_files()
    current = {fn: sha256_file(os.path.join(SOT_DIR, fn)) for fn in sot_files}
    recorded = find_recorded_hashes()
    # also compare against the pre-existing baseline manifest if present
    baseline_path = os.path.join(CROSSREF, "integrity_baseline.json")
    baseline = {}
    if os.path.exists(baseline_path):
        b = json.load(open(baseline_path, encoding="utf-8"))
        baseline = {os.path.basename(k): v.lower() for k, v in b.get("sot_hashes", {}).items()}

    details = []
    changed = unchanged = no_ref = 0
    for fn in sot_files:
        cur = current[fn].lower()
        refs = recorded.get(fn, set())
        ref_base = baseline.get(fn)
        if ref_base:
            refs = set(refs) | {ref_base}
        if not refs:
            status = "NO_RECORDED_HASH"; no_ref += 1
        elif cur in refs:
            status = "OK"; unchanged += 1
        else:
            status = "CHANGED"; changed += 1
        details.append({"sot_file": fn, "status": status, "hash_current": cur,
                        "hash_recorded": sorted(refs)[:2], "in_baseline": bool(ref_base)})
    ts = ts_compact()
    out = {
        "check_timestamp": now_iso(), "sot_total": len(sot_files),
        "changed": changed, "unchanged": unchanged, "no_recorded_hash": no_ref,
        "verdict": "STABLE" if changed == 0 else "CHANGED_DETECTED",
        "baseline_used": os.path.relpath(baseline_path, ROOT) if baseline else None,
        "note": "Compares current SOT-68 SHA-256 against hashes recorded at v13 extraction time "
                "(EA01..15 source_file hashes + _cross-ref/integrity_baseline.json 2026-03-27). "
                "CHANGED = file edited since extraction (e.g. v13e fix backups). "
                "NO_RECORDED_HASH = no recorded reference for that file.",
        "skill_version": SKILL_VERSION, "details": details,
    }
    p = write_json(os.path.join(INTEG_DIR, f"v13_integrity_check_{ts}.json"), out)
    return p, out

def sot2_snapshot():
    files = sorted(walk_md(SOT2_DIR))
    manifest = []
    for path in files:
        manifest.append({"path": path, "rel": os.path.relpath(path, SOT2_DIR),
                         "sha256": sha256_file(path), "bytes": os.path.getsize(path)})
    combined = sha256_text("|".join(f"{m['rel']}:{m['sha256']}" for m in manifest))
    out = {
        "snapshot_timestamp": now_iso(), "root": SOT2_DIR,
        "file_count": len(manifest), "manifest_sha256": combined,
        "purpose": "D1 baseline for D2 continuous integrity monitoring (SOT2 design corpus).",
        "skill_version": SKILL_VERSION, "files": manifest,
    }
    p = write_json(os.path.join(INTEG_DIR, "integrity_snapshot.json"), out)
    return p, {"file_count": len(manifest), "manifest_sha256": combined, "path": p}

if __name__ == "__main__":
    pa, oa = integrity_all()
    ps, os_ = sot2_snapshot()
    print(json.dumps({
        "integrity_all": {"path": pa, "changed": oa["changed"], "unchanged": oa["unchanged"],
                          "no_recorded_hash": oa["no_recorded_hash"], "verdict": oa["verdict"]},
        "snapshot": os_,
    }, ensure_ascii=False, indent=2))
