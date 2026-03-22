#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VAMOS v10 Phase 1 M-4: V3 Feature → PART2 매핑 검증 스크립트
"""
import json
import re
import sys
import os

# UTF-8 출력
sys.stdout.reconfigure(encoding='utf-8')

###############################################################################
# 1. 파일 로드
###############################################################################
BASE = r"D:\VAMOS\04. 구현단계\v10_results"

with open(os.path.join(BASE, "phase0-f", "v10_feature_registry_final.json"), "r", encoding="utf-8") as f:
    registry = json.load(f)
features_all = registry if isinstance(registry, list) else registry.get("features", [])

with open(os.path.join(BASE, "phase0-b", "v10_layer1_claude_features.json"), "r", encoding="utf-8") as f:
    layer1 = json.load(f)
term_map = layer1.get("terminology_mapping", [])

with open(r"D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md", "r", encoding="utf-8") as f:
    part2_lines = f.readlines()

part2_text = "".join(part2_lines)

###############################################################################
# 2. V3 기능 필터
###############################################################################
v3_features = [f for f in features_all if "V3" in str(f.get("version_scope", ""))]
print(f"[INFO] Total features: {len(features_all)}, V3 features: {len(v3_features)}")

###############################################################################
# 3. PART2 섹션 경계 식별
###############################################################################
# §5 V3 구현: line 2266~2845
# §6 시스템별 상세: 이후
# §7 GO/NO-GO: 마지막

S5_START = 2266
S5_END = 2845
S6_START = 2846
S7_START = None

for i, line in enumerate(part2_lines, 1):
    if re.match(r"^#\s+7\.\s+", line) or "GO/NO-GO" in line:
        if i > S6_START:
            S7_START = i
            break

if S7_START is None:
    # fallback: search for §7 marker
    for i, line in enumerate(part2_lines, 1):
        if "7.1 V0 GO/NO-GO" in line or "## 7.1" in line:
            S7_START = i - 5
            break
    if S7_START is None:
        S7_START = len(part2_lines)

print(f"[INFO] §5: {S5_START}-{S5_END}, §6: {S6_START}-{S7_START-1}, §7: {S7_START}-{len(part2_lines)}")

###############################################################################
# 4. V3-Phase 세부 범위 (§5 내)
###############################################################################
V3_PHASE1_START = 2275  # V3-Phase 1
V3_PHASE1_END = 2420
V3_PHASE2_START = 2422  # V3-Phase 2
V3_PHASE2_END = 2680
V3_PHASE3_START = 2682  # V3-Phase 3
V3_PHASE3_END = 2845

###############################################################################
# 5. 검색 유틸리티
###############################################################################
def search_part2(keywords, section_start=1, section_end=None):
    """PART2에서 키워드 검색 → [(line_no, line_text), ...]"""
    if section_end is None:
        section_end = len(part2_lines)
    results = []
    for kw in keywords:
        if not kw or len(kw) < 2:
            continue
        kw_lower = kw.lower().strip()
        for i in range(max(0, section_start - 1), min(section_end, len(part2_lines))):
            line_lower = part2_lines[i].lower()
            if kw_lower in line_lower:
                results.append((i + 1, part2_lines[i].strip()))
    # deduplicate by line number
    seen = set()
    deduped = []
    for ln, txt in results:
        if ln not in seen:
            seen.add(ln)
            deduped.append((ln, txt))
    return sorted(deduped, key=lambda x: x[0])


def get_section_id(line_no):
    """행번호로 섹션 ID 반환"""
    if S5_START <= line_no <= S5_END:
        if V3_PHASE1_START <= line_no <= V3_PHASE1_END:
            return "§5 V3-Phase 1"
        elif V3_PHASE2_START <= line_no <= V3_PHASE2_END:
            return "§5 V3-Phase 2"
        elif V3_PHASE3_START <= line_no <= V3_PHASE3_END:
            return "§5 V3-Phase 3"
        return "§5 V3 구현"
    elif S6_START <= line_no < S7_START:
        return "§6 시스템별 상세"
    elif line_no >= S7_START:
        return "§7 GO/NO-GO"
    else:
        # Before §5
        if line_no < 500:
            return "§2 V0"
        elif line_no < 1200:
            return "§3 V1"
        elif line_no < 2266:
            return "§4 V2"
    return f"line {line_no}"


def extract_keywords(feat):
    """Feature에서 검색 키워드 추출"""
    keywords = []

    fname = feat.get("feature_name", "")
    # feature_name에서 주요 키워드
    keywords.append(fname)

    # 모듈 ID 추출 (I-1, E-7, S-2 등)
    module_ids = re.findall(r'[ISEABCDEVX]+-\d+', fname)
    keywords.extend(module_ids)

    # 기술명 추출
    tech_terms = re.findall(r'(?:K8s|Kubernetes|vLLM|Qdrant|Neo4j|Helm|Grafana|Loki|GraphRAG|FinBERT|Redis|Kafka|WebSocket|Playwright|DSPy|SDAR|HITL|MoE|A2A|RBAC|Blue-Green|HPA|FFmpeg|Whisper|TTS|STT)', fname, re.IGNORECASE)
    keywords.extend(tech_terms)

    # 영문 핵심어 추출
    eng_words = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', fname)
    for w in eng_words:
        if len(w) > 3:
            keywords.append(w)

    # module_id 필드
    mid = feat.get("module_id", "")
    if mid:
        keywords.append(mid)

    # source_section 참조
    src = feat.get("source_section", "")
    if src:
        # SRC 참조명 추출
        refs = re.findall(r'D\d+\.\d+-\d+\s*§[\d.]+', src)
        keywords.extend(refs)

    # 한글 핵심어
    kr_words = re.findall(r'[가-힣]{2,}', fname)
    for w in kr_words:
        if len(w) >= 3 and w not in ["기능의", "전체", "구현", "기능", "단계", "확장", "관련"]:
            keywords.append(w)

    return list(set(keywords))


def determine_mapping(feat, s5_hits, s6_hits, s7_hits, all_hits):
    """매핑 판정"""
    vs = feat.get("version_scope", "")
    versions = [v.strip() for v in vs.split(",")]
    is_primary = versions[0] == "V3" if versions else False
    role = "PRIMARY" if is_primary else "CROSSCHECK"

    fname = feat.get("feature_name", "")
    status_field = feat.get("status", "")

    # NOT_APPLICABLE 판정
    if "SUPERSEDED" in str(status_field).upper():
        return {
            "verdict": "NOT_APPLICABLE",
            "reason": "SUPERSEDED",
            "role": role
        }

    # §5에 직접 매칭
    if s5_hits:
        # Phase 분류
        phases = set()
        lines = []
        for ln, txt in s5_hits:
            sid = get_section_id(ln)
            phases.add(sid)
            lines.append({"line": ln, "section": sid, "text": txt[:100]})

        if len(phases) > 1:
            return {
                "verdict": "SPREAD",
                "part2_phases": sorted(phases),
                "part2_lines": lines[:10],
                "role": role
            }
        else:
            return {
                "verdict": "MATCHED",
                "part2_phase": sorted(phases)[0],
                "part2_lines": lines[:5],
                "role": role
            }

    # §6에만 존재
    if s6_hits and not s5_hits:
        lines = [{"line": ln, "section": get_section_id(ln), "text": txt[:100]} for ln, txt in s6_hits[:5]]
        return {
            "verdict": "PARTIAL",
            "reason": "§6에만 존재, §5 V3 Phase 미배정",
            "part2_lines": lines,
            "role": role
        }

    # §7에만 존재
    if s7_hits and not s5_hits and not s6_hits:
        lines = [{"line": ln, "section": get_section_id(ln), "text": txt[:100]} for ln, txt in s7_hits[:5]]
        return {
            "verdict": "PARTIAL",
            "reason": "§7 GO/NO-GO에만 존재, §5 V3 Phase 미배정",
            "part2_lines": lines,
            "role": role
        }

    # 다른 버전 섹션(§2~§4)에 존재
    other_hits = [h for h in all_hits if h[0] < S5_START]
    if other_hits:
        lines = [{"line": ln, "section": get_section_id(ln), "text": txt[:100]} for ln, txt in other_hits[:5]]
        return {
            "verdict": "PARTIAL",
            "reason": f"다른 버전 섹션에 존재 ({get_section_id(other_hits[0][0])}), §5 V3에는 미반영",
            "part2_lines": lines,
            "role": role
        }

    # MISSING
    severity = determine_severity(feat, is_primary)
    return {
        "verdict": "MISSING",
        "severity": severity,
        "role": role
    }


def determine_severity(feat, is_primary):
    """MISSING 항목 심각도 판정"""
    fname = feat.get("feature_name", "")
    vs = feat.get("version_scope", "")

    # V3-only + 핵심 기능 = BLOCKER
    if vs.strip() == "V3":
        # 인프라/핵심 모듈
        if any(kw in fname for kw in ["K8s", "Kubernetes", "vLLM", "Helm", "배포", "인프라"]):
            return "BLOCKER"
        if any(kw in fname for kw in ["Self-evo", "Governance", "SDAR", "Agent"]):
            return "BLOCKER"
        # EXP 모듈
        if re.search(r'[SABCDEVX]+-\d+', fname):
            return "HIGH"
        return "MEDIUM"

    # 다중 버전 + V3 포함
    if is_primary:
        return "HIGH"

    # CROSSCHECK 대상
    return "LOW"


###############################################################################
# 6. 매핑 실행
###############################################################################
results = []
stats = {"MATCHED": 0, "PARTIAL": 0, "MISSING": 0, "SPREAD": 0, "NOT_APPLICABLE": 0}
missing_items = {"BLOCKER": [], "HIGH": [], "MEDIUM": [], "LOW": []}

for feat in v3_features:
    fid = feat.get("feature_id", "")
    fname = feat.get("feature_name", "")
    vs = feat.get("version_scope", "")

    keywords = extract_keywords(feat)

    # §5 검색
    s5_hits = search_part2(keywords, S5_START, S5_END)
    # §6 검색
    s6_hits = search_part2(keywords, S6_START, S7_START)
    # §7 검색
    s7_hits = search_part2(keywords, S7_START)
    # 전체 검색
    all_hits = search_part2(keywords)

    mapping = determine_mapping(feat, s5_hits, s6_hits, s7_hits, all_hits)

    result = {
        "feature_id": fid,
        "feature_name": fname[:120],
        "version_scope": vs,
        **mapping
    }
    results.append(result)

    verdict = mapping["verdict"]
    stats[verdict] = stats.get(verdict, 0) + 1

    if verdict == "MISSING":
        sev = mapping.get("severity", "MEDIUM")
        missing_items[sev].append({
            "feature_id": fid,
            "feature_name": fname[:120],
            "version_scope": vs,
            "severity": sev,
            "role": mapping.get("role", "")
        })

###############################################################################
# 7. 출력
###############################################################################
output = {
    "meta": {
        "agent": "M-4",
        "scope": "V3 features → PART2 §5 (V3 Phase 1~3)",
        "total_v3_features": len(v3_features),
        "primary_count": sum(1 for r in results if r.get("role") == "PRIMARY"),
        "crosscheck_count": sum(1 for r in results if r.get("role") == "CROSSCHECK"),
        "part2_section": "§5 (lines 2266-2845)"
    },
    "statistics": stats,
    "statistics_by_role": {
        "PRIMARY": {},
        "CROSSCHECK": {}
    },
    "missing_by_severity": {
        sev: {"count": len(items), "items": items}
        for sev, items in missing_items.items()
    },
    "mapping_results": results
}

# Role별 통계
for r in results:
    role = r.get("role", "UNKNOWN")
    verdict = r.get("verdict", "UNKNOWN")
    if role in output["statistics_by_role"]:
        output["statistics_by_role"][role][verdict] = output["statistics_by_role"][role].get(verdict, 0) + 1

outpath = os.path.join(BASE, "phase1", "v10_m4_mapping_result.json")
with open(outpath, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n[DONE] Results saved to: {outpath}")
print(f"\n=== 통계 ===")
print(f"Total V3 features: {len(v3_features)}")
for k, v in stats.items():
    print(f"  {k}: {v}")
print(f"\n=== Role별 통계 ===")
for role, rstats in output["statistics_by_role"].items():
    print(f"  {role}: {rstats}")
print(f"\n=== MISSING 심각도별 ===")
for sev in ["BLOCKER", "HIGH", "MEDIUM", "LOW"]:
    items = missing_items[sev]
    print(f"  {sev}: {len(items)}건")
    for item in items[:5]:
        print(f"    - {item['feature_id']}: {item['feature_name'][:60]}")
    if len(items) > 5:
        print(f"    ... 외 {len(items)-5}건")