# -*- coding: utf-8 -*-
"""VAMOS D1 deterministic verification — common helpers.
Reproducible: same input files = same output. No network, no randomness.
"""
import os, re, json, hashlib, datetime

ROOT      = r"D:\VAMOS"
SOT_DIR   = os.path.join(ROOT, "docs", "sot")
SOT2_DIR  = os.path.join(ROOT, "docs", "sot 2")
PART2     = os.path.join(ROOT, "docs", "guides", "VAMOS_구현가이드_PART2_구현단계.md")
PHASE0    = os.path.join(ROOT, "04. 구현단계", "v13_results", "phase0")
CROSSREF  = os.path.join(SOT2_DIR, "_cross-ref")
EXTRACT_V = os.path.join(SOT2_DIR, "_extractions", "validation")
INTEG_DIR = os.path.join(PHASE0, "integrity")

SKILL_VERSION = "D1-deterministic-v1.0 (2026-06-04)"

# Domain folders = those holding AUTHORITY_CHAIN.md
META_ONLY = {"0-0_Governance-Rules-Meta", "6-10_EXP-Modules-Detail", "6-13_Operations"}

def utf8(s):
    return s if isinstance(s, str) else str(s)

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

def now_iso():
    return datetime.datetime.now().isoformat(timespec="seconds")

def ts_compact():
    return datetime.datetime.now().strftime("%Y%m%dT%H%M%S")

def list_sot_files():
    return sorted(p for p in os.listdir(SOT_DIR) if p.lower().endswith(".md"))

def list_domain_dirs():
    out = []
    for name in sorted(os.listdir(SOT2_DIR)):
        d = os.path.join(SOT2_DIR, name)
        if os.path.isdir(d) and os.path.exists(os.path.join(d, "AUTHORITY_CHAIN.md")):
            out.append(name)
    return out

def walk_md(base):
    for dirpath, _dirs, files in os.walk(base):
        for fn in files:
            if fn.lower().endswith(".md"):
                yield os.path.join(dirpath, fn)

# Scaffolding/automation path segments that are NOT SOT2 design content.
EXCLUDE_SEG = {"_automation", "_archive", "_verification", "archive", "checkpoints",
               "state", "logs", "__pycache__", "backup", "_deprecated_headless",
               "test_results", "_deprecated"}

def is_design_md(path):
    rel = os.path.relpath(path, SOT2_DIR)
    parts = rel.replace("/", os.sep).split(os.sep)
    if any(p in EXCLUDE_SEG for p in parts):
        return False
    low = path.lower()
    if low.endswith(".bak") or ".bak" in os.path.basename(low) or ".backup" in os.path.basename(low):
        return False
    return True

def list_design_md(base=None):
    base = base or SOT2_DIR
    return [p for p in walk_md(base) if is_design_md(p)]

def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    return path

def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path

# --- cross-cutting LOCK constants: TIGHTLY anchored so only the genuine LOCK usage matches ---
# Each regex captures a decimal/number; values are normalized to float and compared to canonical
# (with tolerance). Anchors require the specific concept keyword (e.g. "Hybrid" for α/β) to avoid
# homonym noise (statistical alpha, other-benchmark win-rates, etc. are different concepts).
# (concept_id, regex with one numeric capture group, [allowed_values], tolerance, note)
# allowed_values is a list: a value is consistent if within tolerance of ANY allowed value.
# Hybrid weights are a COMPLEMENTARY PAIR: canonical LOCK-AX-06 (D2.0-06 S7D-012) is
# alpha=0.3(BM25) + (1-alpha)=0.7(vector), alpha+(1-alpha)=1.0 — so both 0.3 and 0.7 are valid legs.
CONCEPTS = [
    ("QOD_L2_BAN",   r"QoD\s*<\s*(0?\.\d+)[^\n]{0,18}(?:L2|벡터)",                       [0.4],       0.001, "QoD < 0.4 → L2 벡터 삽입 금지 (0.40 표기 동일)"),
    ("HYBRID_ALPHA", r"(?:Hybrid|하이브리드)[^\n]{0,40}?(?:α|alpha)\s*=\s*(0?\.\d+)",      [0.3, 0.7], 0.001, "Hybrid 가중치 쌍 α=0.3(BM25)/vector=0.7 — LOCK-AX-06"),
    ("HYBRID_BETA",  r"(?:Hybrid|하이브리드)[^\n]{0,40}?(?:β|beta)\s*=\s*(0?\.\d+)",       [0.3, 0.7], 0.001, "Hybrid 가중치 쌍 (β=0.3 / 보완 0.7)"),
    ("CONF_HIGH",    r"(?:confidence|신뢰도)[^\n]{0,24}?(0?\.85)\b",                       [0.85],      0.001, "confidence HIGH 0.85"),
    ("CONF_LOW",     r"(?:confidence|신뢰도)[^\n]{0,24}?(0?\.30)\b",                       [0.30],      0.001, "confidence REFUSE 0.30"),
    ("COST_MONTHLY", r"(?:월|monthly)[^\n]{0,6}?₩?\s*(40)[,]?000",                        [40.0],      0.5,   "비용 상한 ₩40,000/월 (V1)"),
    ("COST_GATE",    r"(?:CostGate|비용\s*게이트|Cost\s*Gate)[^\n]{0,24}?(\d{2,3})\s*%\s*/\s*100\s*%", [80.0], 0.5, "CostGate 80%/100%"),
]
