"""
M-3 2차 정밀 매핑: MISSING 항목 재분류
1. 전체 PART2 범위 검색 (V2-only 기능이 다른 섹션에 있을 수 있음)
2. 모듈 ID 계층 매핑 (하위 기능이 상위 모듈로 매핑)
3. 용어 매핑 테이블 활용
"""
import json
import re
import os

PART2_PATH = r"D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md"
RESULT_PATH = r"D:\VAMOS\04. 구현단계\v10_results\phase1\v10_m3_mapping_result.json"
OUTPUT_DIR = r"D:\VAMOS\04. 구현단계\v10_results\phase1"

# Module ID to PART2 V2 section mapping (manually extracted from PART2 §4)
V2_MODULE_MAP = {
    # V2-Phase 1: 인프라 마이그레이션
    "SQLite": {"phase": "V2-Phase1", "lines": [1760, 1828]},
    "PostgreSQL": {"phase": "V2-Phase1", "lines": [1760, 1828]},
    "Qdrant": {"phase": "V2-Phase1", "lines": [1762, 1842]},
    "Neo4j": {"phase": "V2-Phase1", "lines": [1763, 1851]},
    "Docker": {"phase": "V2-Phase1", "lines": [1765, 1866]},
    "Chroma": {"phase": "V2-Phase1", "lines": [1762, 1842]},
    "Alembic": {"phase": "V2-Phase1", "lines": [1829]},
    "config.v2": {"phase": "V2-Phase1", "lines": [1764, 1858]},
    "마이그레이션": {"phase": "V2-Phase1", "lines": [1756]},
    "migration": {"phase": "V2-Phase1", "lines": [1756]},
    "VPS": {"phase": "V2-Phase1", "lines": [1766, 1810]},
    "Blue-Green": {"phase": "V2-Phase1", "lines": [1881]},
    "rollback": {"phase": "V2-Phase1", "lines": [1770, 1885]},
    "TimescaleDB": {"phase": "V2-Phase1", "lines": [1873]},

    # V2-Phase 2: COND 모듈
    "I-7": {"phase": "V2-Phase2", "lines": [1928, 1968]},
    "I-12": {"phase": "V2-Phase2", "lines": [1929, 1977]},
    "I-22": {"phase": "V2-Phase2", "lines": [1930, 1983]},
    "I-23": {"phase": "V2-Phase2", "lines": [1931, 1989]},
    "I-25": {"phase": "V2-Phase2", "lines": [1932, 1994]},
    "A-4": {"phase": "V2-Phase2", "lines": [1933, 2006]},
    "E-13": {"phase": "V2-Phase2", "lines": [1934, 2012]},
    "E-14": {"phase": "V2-Phase2", "lines": [1935, 2018]},
    "E-15": {"phase": "V2-Phase2", "lines": [1936, 2024]},
    "E-16": {"phase": "V2-Phase2", "lines": [1939, 2033]},
    "RT-BNP": {"phase": "V2-Phase2", "lines": [1937, 2026]},
    "DCL-GEO": {"phase": "V2-Phase2", "lines": [1938, 2029]},
    "COND": {"phase": "V2-Phase2", "lines": [1921]},
    "Calendar": {"phase": "V2-Phase2", "lines": [1934, 2012]},
    "Email": {"phase": "V2-Phase2", "lines": [1935, 2018]},
    "Cloud Collector": {"phase": "V2-Phase2", "lines": [1936, 2024]},
    "Cloud Storage": {"phase": "V2-Phase2", "lines": [1939, 2033]},
    "Project/Session": {"phase": "V2-Phase2", "lines": [1928, 1968]},
    "Workflow Builder": {"phase": "V2-Phase2", "lines": [1929, 1977]},
    "Task/Project": {"phase": "V2-Phase2", "lines": [1930, 1983]},
    "Doc/Code": {"phase": "V2-Phase2", "lines": [1931, 1989]},
    "SDAR": {"phase": "V2-Phase2", "lines": [1932, 1994]},
    "Debate": {"phase": "V2-Phase2", "lines": [1933, 2006]},
    "Bull": {"phase": "V2-Phase2", "lines": [2007]},
    "Bear": {"phase": "V2-Phase2", "lines": [2007]},

    # V2-Phase 3: Agent Teams V2 + 보안
    "Redis": {"phase": "V2-Phase3", "lines": [2110, 2147]},
    "MessageBus": {"phase": "V2-Phase3", "lines": [2110, 2147]},
    "HMAC": {"phase": "V2-Phase3", "lines": [2113, 2177]},
    "LlamaGuard": {"phase": "V2-Phase3", "lines": [2114, 2183]},
    "GDPR": {"phase": "V2-Phase3", "lines": [2115, 2193]},
    "Guardrails": {"phase": "V2-Phase3", "lines": [2114, 2183]},
    "Agent Teams": {"phase": "V2-Phase3", "lines": [2106]},
    "Sub-Agent": {"phase": "V2-Phase3", "lines": [2112, 2165]},
    "협업 패턴": {"phase": "V2-Phase3", "lines": [2111, 2155]},
    "Kafka": {"phase": "V2-Phase3", "lines": [2133, 2206]},
    "Quant Agent": {"phase": "V2-Phase3", "lines": [2170]},
    "Content Agent": {"phase": "V2-Phase3", "lines": [2171]},
    "Trading Agent": {"phase": "V2-Phase3", "lines": [2172]},
    "Productivity Agent": {"phase": "V2-Phase3", "lines": [2173]},
    "Critic Agent": {"phase": "V2-Phase3", "lines": [2174]},
    "SDAR Agent": {"phase": "V2-Phase3", "lines": [2175]},
    "7-Stage": {"phase": "V2-Phase3", "lines": [2202]},
    "Discovery": {"phase": "V2-Phase3", "lines": [2202]},
    "AR-L3": {"phase": "V2-Phase3", "lines": [2118, 2210]},
    "NeMo": {"phase": "V2-Phase3", "lines": [2185]},
    "GuardrailsAI": {"phase": "V2-Phase3", "lines": [2186]},
}

# Additional keyword synonyms from terminology mapping
TERM_SYNONYMS = {
    "자가진단": "SDAR",
    "자동수리": "SDAR",
    "자기진화": "I-18",  # but I-18 is V3
    "워크플로우": "Workflow Builder",
    "태스크 관리": "I-22",
    "프로젝트 관리": "I-7",
    "세션 관리": "I-7",
    "캘린더": "Calendar",
    "이메일": "Email",
    "클라우드": "Cloud",
    "에이전트 팀": "Agent Teams",
    "보안": "Security",
    "인증": "HMAC",
    "뉴스": "RT-BNP",
    "RSS": "RT-BNP",
    "지정학": "DCL-GEO",
    "마이그레이션": "migration",
    "데이터베이스": "PostgreSQL",
    "벡터": "Qdrant",
    "그래프": "Neo4j",
    "컨테이너": "Docker",
    "배포": "Docker",
}

def classify_section(line_no):
    if 1756 <= line_no <= 1919:
        return "V2-Phase1"
    elif 1921 <= line_no <= 2104:
        return "V2-Phase2"
    elif 2106 <= line_no <= 2265:
        return "V2-Phase3"
    elif 2848 <= line_no <= 3721:
        return "§6"
    elif 3722 <= line_no <= 3944:
        return "§7"
    elif 54 <= line_no <= 1383:
        return "§2-V0"
    elif 1384 <= line_no <= 1746:
        return "§3-V1"
    elif 2266 <= line_no <= 2847:
        return "§5-V3"
    return "OTHER"

def refine_missing(results, lines):
    """Re-examine MISSING items with broader search and module hierarchy."""
    refined = []
    reclassified = 0

    for r in results:
        if r["verdict"] != "MISSING":
            refined.append(r)
            continue

        fname = r.get("feature_name", "")
        fid = r.get("feature_id", "")
        notes = r.get("notes", "") or ""
        src_section = r.get("source_section", "") or ""
        keywords = r.get("keywords_used", [])

        # Strategy 1: Module ID hierarchy matching
        matched_module = None
        for mod_key, mod_info in V2_MODULE_MAP.items():
            if mod_key.lower() in fname.lower():
                matched_module = mod_info
                break
            if mod_key.lower() in notes.lower():
                matched_module = mod_info
                break
            # Check in keywords
            for kw in keywords:
                if mod_key.lower() in kw.lower():
                    matched_module = mod_info
                    break

        if matched_module:
            r["verdict"] = "MATCHED"
            r["part2_phase"] = matched_module["phase"]
            r["part2_lines"] = matched_module["lines"]
            r["match_details"] = [{"method": "module_hierarchy", "module_key": mod_key}]
            reclassified += 1
            refined.append(r)
            continue

        # Strategy 2: Term synonym matching
        for term, target in TERM_SYNONYMS.items():
            if term in fname:
                if target in V2_MODULE_MAP:
                    mod_info = V2_MODULE_MAP[target]
                    r["verdict"] = "MATCHED"
                    r["part2_phase"] = mod_info["phase"]
                    r["part2_lines"] = mod_info["lines"]
                    r["match_details"] = [{"method": "term_synonym", "term": term, "target": target}]
                    reclassified += 1
                    break

        if r["verdict"] != "MISSING":
            refined.append(r)
            continue

        # Strategy 3: Full PART2 search (wider scope)
        found_anywhere = False
        for kw in keywords:
            if len(kw) < 4:
                continue
            for i, line in enumerate(lines):
                line_no = i + 1
                if kw.lower() in line.lower():
                    section = classify_section(line_no)
                    if section.startswith("V2-Phase"):
                        r["verdict"] = "MATCHED"
                        r["part2_phase"] = section
                        r["part2_lines"] = [line_no]
                        r["match_details"] = [{"method": "full_search", "keyword": kw, "line": line_no}]
                        reclassified += 1
                        found_anywhere = True
                        break
                    elif section.startswith("§6") or section.startswith("§7"):
                        r["verdict"] = "PARTIAL"
                        r["part2_phase"] = section + " (Phase 미배정)"
                        r["part2_lines"] = [line_no]
                        r["match_details"] = [{"method": "full_search_s6s7", "keyword": kw, "line": line_no}]
                        reclassified += 1
                        found_anywhere = True
                        break
            if found_anywhere:
                break

        # Strategy 4: Check if feature is actually for V3 (misclassified)
        if r["verdict"] == "MISSING" and r.get("version_scope") == "V2":
            # Some V2 features might only have detail in §5 (V3) or §6
            # Check source section for V3 indicators
            if "V3" in str(src_section) or "EXP" in str(notes):
                r["verdict"] = "NOT_APPLICABLE"
                r["severity"] = None
                r["notes"] = (r.get("notes", "") or "") + " [M-3: V3/EXP 영역 추정, V2 Phase 미배정 가능]"
                reclassified += 1

        refined.append(r)

    return refined, reclassified

def main():
    print("Loading results...")
    with open(RESULT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = data["results"]
    print(f"Total results: {len(results)}")

    missing_count = sum(1 for r in results if r["verdict"] == "MISSING")
    print(f"MISSING before refine: {missing_count}")

    print("\nLoading PART2...")
    with open(PART2_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    print("Refining MISSING items...")
    refined, reclassified = refine_missing(results, lines)
    print(f"Reclassified: {reclassified}")

    new_missing = sum(1 for r in refined if r["verdict"] == "MISSING")
    print(f"MISSING after refine: {new_missing}")

    # Recompute stats
    from collections import Counter

    all_verdicts = Counter(r["verdict"] for r in refined)
    print("\n=== Refined Overall Verdicts ===")
    for v, c in all_verdicts.most_common():
        print(f"  {v}: {c}")

    primary_results = [r for r in refined if r["m3_role"] == "PRIMARY"]
    primary_verdicts = Counter(r["verdict"] for r in primary_results)
    print(f"\n=== Primary Verdicts ({len(primary_results)}) ===")
    for v, c in primary_verdicts.most_common():
        print(f"  {v}: {c}")

    cc_results = [r for r in refined if r["m3_role"] == "CROSS_CHECK"]
    cc_verdicts = Counter(r["verdict"] for r in cc_results)
    print(f"\n=== Cross-check Verdicts ({len(cc_results)}) ===")
    for v, c in cc_verdicts.most_common():
        print(f"  {v}: {c}")

    # MISSING details
    still_missing = [r for r in refined if r["verdict"] == "MISSING"]
    if still_missing:
        sev = Counter(r["severity"] for r in still_missing)
        print(f"\n=== Remaining MISSING Severity ({len(still_missing)}) ===")
        for s, c in sev.most_common():
            print(f"  {s}: {c}")

        # Primary MISSING BLOCKER/HIGH
        pm_critical = [r for r in still_missing if r["m3_role"] == "PRIMARY" and r["severity"] in ("BLOCKER", "HIGH")]
        print(f"\n=== Primary MISSING BLOCKER/HIGH ({len(pm_critical)}) ===")
        for r in pm_critical[:50]:
            print(f"  [{r['severity']}] {r['feature_id']}: {r['feature_name'][:60]}")
            print(f"    vs={r['version_scope']}, cat={r['category']}, src={r.get('source_section','')[:40]}")

    # Update data
    data["results"] = refined
    data["statistics"] = {
        "overall": dict(all_verdicts),
        "primary": dict(primary_verdicts),
        "cross_check": dict(cc_verdicts),
        "missing_severity": dict(Counter(r["severity"] for r in still_missing if r.get("severity"))) if still_missing else {}
    }

    # Save v2
    out_path = os.path.join(OUTPUT_DIR, "v10_m3_mapping_result_v2.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\nSaved: {out_path}")

    # Save remaining missing
    missing_out = os.path.join(OUTPUT_DIR, "v10_m3_missing_items_v2.json")
    with open(missing_out, "w", encoding="utf-8") as f:
        json.dump(still_missing, f, ensure_ascii=False, indent=2)
    print(f"Saved: {missing_out}")

if __name__ == "__main__":
    main()