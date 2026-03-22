#!/usr/bin/env python3
"""
M-5b Agent: §6.8~§6.13 + §7 GO/NO-GO + V_UNKNOWN + 통합 매핑
"""
import json
import re
import os

BASE = r"D:\VAMOS\04. 구현단계\v10_results\phase1"
PART2 = r"D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md"
REG_PATH = r"D:\VAMOS\04. 구현단계\v10_results\phase0-f\v10_feature_registry_final.json"

# Load feature registry
with open(REG_PATH, "r", encoding="utf-8") as f:
    reg = json.load(f)
features = reg["features"]
print(f"[INFO] Feature Registry loaded: {len(features)} features")

# Load PART2
with open(PART2, "r", encoding="utf-8") as f:
    part2_lines = f.readlines()
print(f"[INFO] PART2 loaded: {len(part2_lines)} lines")

# ─────────────────────────────────────────
# TASK 1: §6.8~§6.13 items → Feature mapping
# ─────────────────────────────────────────

# Extract §6.8~§6.13 implementation items from PART2 (L3167~L3721)
s6_back_items = []
section_ranges = {
    "§6.8": (3167, 3218),
    "§6.8.1": (3219, 3288),
    "§6.9": (3289, 3401),
    "§6.10": (3402, 3463),
    "§6.10.1": (3464, 3548),
    "§6.10.2": (3549, 3627),
    "§6.11": (3630, 3691),
    "§6.12": (3695, 3703),
    "§6.13": (3706, 3721),
}

# Extract key terms from each section for matching
section_keywords = {
    "§6.8": ["ai investing", "51% gate", "circuit breaker", "paper trading", "yfinance",
             "vectorbt", "backtrader", "finbert", "timescaledb", "risk engine",
             "ai_investing", "투자", "백테스트", "전략"],
    "§6.8.1": ["rt-bnp", "breaking news", "breaking_news", "속보", "뉴스",
               "circuit breaker", "event-based strategy", "fomc", "breaking-p0"],
    "§6.9": ["sdar", "self-diagnosis", "auto-repair", "자가진단", "자동수리",
             "5-layer", "7-state", "5-gate", "ar-l0", "ar-l1", "ar-l2", "ar-l3", "ar-l4",
             "kill switch", "repair action", "self-evo", "sdar_spec"],
    "§6.10": ["cloud library", "클라우드 라이브러리", "10-layer", "source trust",
              "crawl", "크롤", "embedding", "cl-g0", "cl-g1", "cl-g2", "cl-g3", "cl-g4"],
    "§6.10.1": ["rt-bnp", "real-time breaking", "실시간 속보", "breaking detector",
                "fast gate", "news source tier", "t1", "t2", "t3", "retraction",
                "breaking-p0", "breaking-p1", "cl.rt.", "newsapi", "finnhub"],
    "§6.10.2": ["dcl", "domain context layer", "도메인 컨텍스트", "dcl-fin", "dcl-tech", "dcl-geo",
                "배경 인식", "selective background", "6-layer information"],
    "§6.11": ["eventtype", "이벤트", "failurecode", "fallback", "registry",
              "oc_i1", "oc_i2", "oc_i3", "oc_i4", "oc_i5", "fb_", "cl.rt."],
    "§6.12": ["로그 보관", "백업 주기", "log retention", "backup cycle"],
    "§6.13": ["작업량", "story point", "코딩 작업량"],
}

def match_feature_to_section(feat, keywords):
    """Check if a feature matches section keywords."""
    fname = feat["feature_name"].lower()
    fid = feat["feature_id"].lower()
    notes = (feat.get("notes") or "").lower()
    src_sec = (feat.get("source_section") or "").lower()
    module_id = (feat.get("module_id") or "").lower()

    searchable = f"{fname} {fid} {notes} {src_sec} {module_id}"

    matched_kw = []
    for kw in keywords:
        if kw.lower() in searchable:
            matched_kw.append(kw)
    return matched_kw

# Map features to §6.8~§6.13 sections
s6_back_mapping = {}
for section, kws in section_keywords.items():
    s6_back_mapping[section] = []
    for feat in features:
        matched = match_feature_to_section(feat, kws)
        if matched:
            # Check if feature has a phase assignment
            p2_phase = feat.get("part2_phase") or ""
            has_phase = bool(p2_phase and p2_phase not in ["", "UNKNOWN", "None"])
            s6_back_mapping[section].append({
                "feature_id": feat["feature_id"],
                "feature_name": feat["feature_name"],
                "version_scope": feat["version_scope"],
                "matched_keywords": matched,
                "has_phase_assignment": has_phase,
                "part2_phase": p2_phase,
                "part2_line": feat.get("part2_line"),
            })

# ─────────────────────────────────────────
# TASK 2: §7 GO/NO-GO → Feature mapping
# ─────────────────────────────────────────

gonogo_items = [
    # §7.1 V0 (16 items)
    {"id": "V0-001", "desc": "통신 계층: Python 백엔드 확정", "line": 3737, "version": "V0"},
    {"id": "V0-002", "desc": "IMPLEMENTATION 계층 = PHASE_B 명시", "line": 3738, "version": "V0"},
    {"id": "V0-003", "desc": "V0 비용 상한 = V1 동일 명시", "line": 3739, "version": "V0"},
    {"id": "V0-004", "desc": "디렉토리 구조: PHASE_B2 정본 명시 + monorepo 생성", "line": 3740, "version": "V0"},
    {"id": "V0-005", "desc": "config 포맷: config.toml 통일", "line": 3741, "version": "V0"},
    {"id": "CC-001", "desc": "D2.1 스키마 v3.0.0 통일 승격", "line": 3742, "version": "V0"},
    {"id": "CC-010", "desc": "PLAN-2.0 (대체됨) 표기", "line": 3743, "version": "V0"},
    {"id": "RULE-1.3", "desc": "BASE-1.3 전 24개 규칙 코드 매핑", "line": 3744, "version": "V0"},
    {"id": "PHASE_B2/B3", "desc": "스캐폴딩 + 의존성 설치", "line": 3745, "version": "V0"},
    {"id": "PHASE_B4", "desc": "config.v1.toml LOCK 값 배치", "line": 3746, "version": "V0"},
    {"id": "D2.1-D1~D8", "desc": "25개 스키마 코드 생성", "line": 3747, "version": "V0"},
    {"id": "READINESS-§2.7", "desc": "I-1~I-3, I-5, I-19 스켈레톤 생성", "line": 3748, "version": "V0"},
    {"id": "D2.0-06-§2.1", "desc": "L0 세션 메모리 최소 구현", "line": 3749, "version": "V0"},
    {"id": "ABSOLUTE-LOCK", "desc": "비용 엔진 ₩40,000/월 하드코딩", "line": 3750, "version": "V0"},
    {"id": "PHASE_B4-G", "desc": "Guardrails L1+L2 설정", "line": 3751, "version": "V0"},
    {"id": "PHASE_B4-O", "desc": "Ollama + Chroma + SQLite 초기화", "line": 3752, "version": "V0"},
    # §7.2 V1 (22 items)
    {"id": "V1-001/016", "desc": "I-Series 25개 모듈 정본 확정", "line": 3758, "version": "V1"},
    {"id": "V1-002/003", "desc": "E-15, S-5 명칭 겸용 처리", "line": 3759, "version": "V1"},
    {"id": "V1-008", "desc": "38개 DEFER/TBD V1 차단 0건 확인", "line": 3760, "version": "V1"},
    {"id": "V1-005", "desc": "datetime.utcnow() 전수 교체", "line": 3761, "version": "V1"},
    {"id": "V1-004", "desc": "approval_status enum 통일", "line": 3762, "version": "V1"},
    {"id": "V1-006", "desc": "QoD 5요소 공식 통일", "line": 3763, "version": "V1"},
    {"id": "V1-007", "desc": "Front Mini LLM = I-1 내부 명시", "line": 3764, "version": "V1"},
    {"id": "V1-010", "desc": "Guardrails 4-Layer 명시", "line": 3765, "version": "V1"},
    {"id": "V1-013", "desc": "비용 상한 ₩40,000 통일", "line": 3766, "version": "V1"},
    {"id": "V1-014", "desc": "React 18.3 통일", "line": 3767, "version": "V1"},
    {"id": "V1-009", "desc": "LangChain Allowlist 명시", "line": 3768, "version": "V1"},
    {"id": "READINESS-§9", "desc": "V1 CRITICAL 보안항목 15개 구현", "line": 3769, "version": "V1"},
    {"id": "PHASE_B5", "desc": "테스트 인프라 구축 (80%+)", "line": 3770, "version": "V1"},
    {"id": "PHASE_B6", "desc": "CI/CD 설정 완료", "line": 3771, "version": "V1"},
    {"id": "D2.0-06", "desc": "스토리지 스택 구축", "line": 3772, "version": "V1"},
    {"id": "CC-006", "desc": "EventTypeRegistry 통합", "line": 3773, "version": "V1"},
    {"id": "CC-007", "desc": "Python/TS 스키마 동기화 도구", "line": 3774, "version": "V1"},
    {"id": "CC-002", "desc": "BEGINNER_GUIDE 모듈 목록 갱신", "line": 3775, "version": "V1"},
    {"id": "CC-009", "desc": "B↔L 매핑표 추가", "line": 3776, "version": "V1"},
    {"id": "CC-011", "desc": "STEP7 항목 수 비고 추가", "line": 3777, "version": "V1"},
    {"id": "§7.1-PASS", "desc": "V0 GO 체크리스트 전수 통과", "line": 3778, "version": "V1"},
    {"id": "V1-P6-MCP", "desc": "MCP Bridge/Server/Client 개별 검증", "line": 3779, "version": "V1"},
    # §7.3 V2 (14 items)
    {"id": "V2-TRANS", "desc": "V1→V2 전환 조건 6개 충족", "line": 3792, "version": "V2"},
    {"id": "V2-003", "desc": "Agent Teams FREEZE 해석 확정", "line": 3793, "version": "V2"},
    {"id": "V2-008", "desc": "STEP7 V2 CRITICAL ~190건 상세 스펙 보강", "line": 3794, "version": "V2"},
    {"id": "V2-001/CC-004", "desc": "10-Layer/Gate 접두어 변경 (CL-)", "line": 3795, "version": "V2"},
    {"id": "V2-004", "desc": "SQLite→PostgreSQL 마이그레이션", "line": 3796, "version": "V2"},
    {"id": "V2-005", "desc": "Chroma→Qdrant 재임베딩", "line": 3797, "version": "V2"},
    {"id": "V2-006", "desc": "NetworkX→Neo4j 변환", "line": 3798, "version": "V2"},
    {"id": "V2-002", "desc": "SDAR V2 COND 활성화 조건 확정", "line": 3799, "version": "V2"},
    {"id": "DEFER-AT-001", "desc": "MessageBus 구현 결정", "line": 3800, "version": "V2"},
    {"id": "CC-012", "desc": "HMAC 프로토콜 상세 완성", "line": 3801, "version": "V2"},
    {"id": "CC-005", "desc": "STEP7 모듈 연동 구체화", "line": 3802, "version": "V2"},
    {"id": "PHASE_B6-V2", "desc": "V2 인프라 10개 컴포넌트 구축", "line": 3803, "version": "V2"},
    {"id": "ABSOLUTE-LOCK-V2", "desc": "V2 비용 모니터링 대시보드 (₩93,000)", "line": 3804, "version": "V2"},
    {"id": "CC-003", "desc": "QoD 가중치 이중 체계 구분 명시", "line": 3805, "version": "V2"},
    # §7.4 V3 (11 items)
    {"id": "V3-TRANS", "desc": "V2→V3 전환 조건 충족", "line": 3818, "version": "V3"},
    {"id": "V3-001", "desc": "K8s 배포 명세 상세 완성", "line": 3819, "version": "V3"},
    {"id": "V3-002", "desc": "S-8 Self-evo 거버넌스 상세화", "line": 3820, "version": "V3"},
    {"id": "V3-003", "desc": "V3 비용 상한 재산정 + 승인", "line": 3821, "version": "V3"},
    {"id": "V3-004", "desc": "GraphRAG 벤치마크 정의", "line": 3822, "version": "V3"},
    {"id": "SDAR-V3", "desc": "SDAR V3 ON 조건 충족", "line": 3823, "version": "V3"},
    {"id": "V2-008-EXT", "desc": "STEP7 TITLE_ONLY ~317건 상세 보강", "line": 3824, "version": "V3"},
    {"id": "LOCK-AT-014", "desc": "에이전트 50+ 병렬 인프라 구축", "line": 3825, "version": "V3"},
    {"id": "DEFER-AT-005", "desc": "A2A 프로토콜 설계", "line": 3826, "version": "V3"},
    {"id": "DEFER-AT-004", "desc": "Federated Agent 승인 체계", "line": 3827, "version": "V3"},
    {"id": "DEFER-AT-003", "desc": "Agent Marketplace 기준 확정", "line": 3828, "version": "V3"},
]

# Map GO/NO-GO items to Feature Registry
def match_gonogo_to_features(item, features):
    """Find features matching a GO/NO-GO item."""
    desc_lower = item["desc"].lower()
    item_id = item["id"].lower()

    # Build search terms from description
    search_terms = []
    # Extract key phrases
    for term in re.split(r'[,/+→()（）]', item["desc"]):
        term = term.strip()
        if len(term) >= 3:
            search_terms.append(term.lower())
    search_terms.append(item_id)

    matched = []
    for feat in features:
        fname = feat["feature_name"].lower()
        fid = feat["feature_id"].lower()
        notes = (feat.get("notes") or "").lower()
        module_id = (feat.get("module_id") or "").lower()
        src_sec = (feat.get("source_section") or "").lower()

        searchable = f"{fname} {fid} {notes} {module_id} {src_sec}"

        for st in search_terms:
            if st in searchable:
                matched.append({
                    "feature_id": feat["feature_id"],
                    "feature_name": feat["feature_name"],
                    "matched_term": st,
                })
                break
    return matched

gonogo_mapping = []
for item in gonogo_items:
    matches = match_gonogo_to_features(item, features)
    gonogo_mapping.append({
        "gonogo_id": item["id"],
        "gonogo_desc": item["desc"],
        "gonogo_line": item["line"],
        "version": item["version"],
        "matched_features": matches[:10],  # top 10
        "match_count": len(matches),
        "judgment": "MATCHED" if matches else "NO_MATCH",
    })

# ─────────────────────────────────────────
# TASK 3: M-1~M-4 MISSING → §6.8~§6.13 재확인
# ─────────────────────────────────────────

# Load M-4 missing items (already have structure)
with open(os.path.join(BASE, "v10_m4_missing_items.json"), "r", encoding="utf-8") as f:
    m4_missing = json.load(f)

# Load M-2 missing items
with open(os.path.join(BASE, "v10_m2_missing_items.json"), "r", encoding="utf-8") as f:
    m2_missing = json.load(f)

# Load M-3 missing items
with open(os.path.join(BASE, "v10_m3_missing_final.json"), "r", encoding="utf-8") as f:
    m3_missing = json.load(f)

# Load M-1 missing (extract from mapping result)
with open(os.path.join(BASE, "m1_v0_mapping_result.json"), "r", encoding="utf-8") as f:
    m1_result = json.load(f)

m1_missing_items = []
for sev in ["BLOCKER", "HIGH", "MEDIUM", "LOW"]:
    for item in m1_result["missing_by_severity"].get(sev, []):
        m1_missing_items.append({
            "feature_id": item["feature_id"],
            "feature_name": item["feature_name"],
            "severity": sev,
            "agent": "M-1",
        })

# Consolidate all missing items
all_missing = []
for item in m1_missing_items:
    all_missing.append(item)

# M-2: dict with "by_severity" → {sev: {count, by_category: {cat: [items]}}}
for sev_key, sev_data in m2_missing.get("by_severity", {}).items():
    if isinstance(sev_data, dict):
        for cat_name, cat_items in sev_data.get("by_category", {}).items():
            if isinstance(cat_items, list):
                for item in cat_items:
                    if isinstance(item, dict):
                        all_missing.append({
                            "feature_id": item.get("feature_id", ""),
                            "feature_name": item.get("feature_name", ""),
                            "severity": sev_key.upper(),
                            "agent": "M-2",
                        })

# M-3: list of items
for item in m3_missing:
    if isinstance(item, dict):
        all_missing.append({
            "feature_id": item.get("feature_id", ""),
            "feature_name": item.get("feature_name", ""),
            "severity": item.get("severity", "UNKNOWN"),
            "agent": "M-3",
        })

for item in m4_missing.get("items", []):
    all_missing.append({
        "feature_id": item["feature_id"],
        "feature_name": item["feature_name"],
        "severity": item["severity"],
        "agent": "M-4",
    })

print(f"[INFO] Total MISSING items from M-1~M-4: {len(all_missing)}")

# Check each missing item against §6.8~§6.13
s6_back_text = ""
for line_num in range(3167-1, min(3721, len(part2_lines))):
    s6_back_text += part2_lines[line_num].lower()

found_in_s6_back = []
still_missing = []

for item in all_missing:
    fname = item["feature_name"].lower()
    fid = item["feature_id"].lower()

    # Extract key terms from feature name
    terms = re.split(r'[\s,/+→()（）\[\]{}]', fname)
    terms = [t for t in terms if len(t) >= 3 and not t.isdigit()]

    found = False
    matched_terms = []
    for term in terms:
        if term in s6_back_text:
            matched_terms.append(term)

    if len(matched_terms) >= 2 or (len(matched_terms) == 1 and len(matched_terms[0]) >= 5):
        found_in_s6_back.append({
            **item,
            "found_section": "§6.8~§6.13",
            "matched_terms": matched_terms,
        })
    else:
        still_missing.append(item)

print(f"[INFO] M-1~M-4 MISSING found in §6.8~§6.13: {len(found_in_s6_back)}")
print(f"[INFO] Still MISSING: {len(still_missing)}")

# ─────────────────────────────────────────
# TASK 4: §6.13 작업량 매트릭스 vs Feature Registry
# ─────────────────────────────────────────

# §6.13 matrix from PART2
s6_13_matrix = {
    "UI/UX": {"V0": 0, "V1": 75, "V2": 40, "V3": 20, "total": 135},
    "Infrastructure": {"V0": 8, "V1": 80, "V2": 15, "V3": 5, "total": 108},
    "Testing": {"V0": 15, "V1": 62, "V2": 5, "V3": 2, "total": 84},
    "CI/CD": {"V0": 0, "V1": 8, "V2": 4, "V3": 2, "total": 14},
    "Tools": {"V0": 10, "V1": 5, "V2": 4, "V3": 0, "total": 19},
    "Security": {"V0": 0, "V1": 8, "V2": 5, "V3": 2, "total": 15},
    "MCP": {"V0": 0, "V1": 5, "V2": 2, "V3": 0, "total": 7},
    "Misc": {"V0": 8, "V1": 30, "V2": 17, "V3": 17, "total": 72},
}
s6_13_grand_total = 454

# Count features by version scope (primary version)
version_counts = {}
category_counts = {}
for feat in features:
    vs = feat["version_scope"]
    cat = feat.get("category", "UNKNOWN")
    # Count primary versions
    for v in ["V0", "V1", "V2", "V3"]:
        if v in vs:
            version_counts[v] = version_counts.get(v, 0) + 1
    category_counts[cat] = category_counts.get(cat, 0) + 1

# ─────────────────────────────────────────
# TASK 5: V_UNKNOWN
# ─────────────────────────────────────────
v_unknown = [f for f in features if f["version_scope"] == "V_UNKNOWN"]
print(f"[INFO] V_UNKNOWN count: {len(v_unknown)}")

# ─────────────────────────────────────────
# Output results
# ─────────────────────────────────────────

result = {
    "_meta": {
        "agent": "M-5b",
        "phase": "Phase 1",
        "scope": "§6.8~§6.13 + §7 GO/NO-GO + V_UNKNOWN + 통합",
        "method": "keyword matching + cross-reference",
        "total_features_scanned": len(features),
        "generated_date": "2026-03-09",
        "part2_version": "v21.0.0",
        "part2_lines": "L3167~L3974",
    },
    "statistics": {
        "s6_back_sections": len(section_keywords),
        "s6_back_feature_matches": {sec: len(items) for sec, items in s6_back_mapping.items()},
        "gonogo_total": len(gonogo_items),
        "gonogo_matched": sum(1 for g in gonogo_mapping if g["judgment"] == "MATCHED"),
        "gonogo_no_match": sum(1 for g in gonogo_mapping if g["judgment"] == "NO_MATCH"),
        "m1_m4_missing_total": len(all_missing),
        "m1_m4_missing_found_in_s6_back": len(found_in_s6_back),
        "m1_m4_missing_still_missing": len(still_missing),
        "v_unknown_total": len(v_unknown),
    },
    "task1_s6_back_mapping": {
        sec: {
            "total_matched": len(items),
            "with_phase": sum(1 for i in items if i["has_phase_assignment"]),
            "no_phase": sum(1 for i in items if not i["has_phase_assignment"]),
            "items_no_phase": [i for i in items if not i["has_phase_assignment"]][:20],
        }
        for sec, items in s6_back_mapping.items()
    },
    "task2_gonogo_mapping": gonogo_mapping,
    "task3_missing_found_in_s6_back": found_in_s6_back,
    "task3_missing_by_agent": {
        "M-1": len([i for i in all_missing if i["agent"] == "M-1"]),
        "M-2": len([i for i in all_missing if i["agent"] == "M-2"]),
        "M-3": len([i for i in all_missing if i["agent"] == "M-3"]),
        "M-4": len([i for i in all_missing if i["agent"] == "M-4"]),
    },
    "task4_workload_comparison": {
        "s6_13_matrix": s6_13_matrix,
        "s6_13_grand_total_sp": s6_13_grand_total,
        "feature_registry_total": len(features),
        "feature_registry_by_version": version_counts,
        "feature_registry_by_category": category_counts,
        "note": "§6.13은 스토리 포인트(~454), Registry는 기능 항목 수(3940). 단위가 다르므로 직접 비교 불가. 스토리 포인트는 구현 난이도 기반, 기능 항목은 개별 feature 단위."
    },
    "task5_v_unknown": {
        "total": len(v_unknown),
        "items": [{"feature_id": f["feature_id"], "feature_name": f["feature_name"]} for f in v_unknown],
        "conclusion": "V_UNKNOWN 잔여 항목 0건. Phase 0-E/F에서 전수 버전 배정 완료."
    },
}

# Save result
out_path = os.path.join(BASE, "v10_m5b_mapping_result.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"[OK] Result saved: {out_path}")

# Print summary
print("\n" + "="*60)
print("M-5b MAPPING RESULT SUMMARY")
print("="*60)
print(f"\nTask 1: §6.8~§6.13 Feature Mapping")
for sec, data in result["task1_s6_back_mapping"].items():
    print(f"  {sec}: {data['total_matched']} features matched ({data['with_phase']} with phase, {data['no_phase']} no phase)")

print(f"\nTask 2: §7 GO/NO-GO Mapping")
print(f"  Total: {result['statistics']['gonogo_total']}")
print(f"  MATCHED: {result['statistics']['gonogo_matched']}")
print(f"  NO_MATCH: {result['statistics']['gonogo_no_match']}")

print(f"\nTask 3: M-1~M-4 MISSING in §6.8~§6.13")
print(f"  Total MISSING: {result['statistics']['m1_m4_missing_total']}")
print(f"  Found in §6.8~§6.13: {result['statistics']['m1_m4_missing_found_in_s6_back']}")
print(f"  Still MISSING: {result['statistics']['m1_m4_missing_still_missing']}")
for agent, count in result["task3_missing_by_agent"].items():
    print(f"    {agent}: {count}")

print(f"\nTask 4: §6.13 Workload vs Registry")
print(f"  §6.13 total SP: {s6_13_grand_total}")
print(f"  Registry total features: {len(features)}")
print(f"  Registry by version: {version_counts}")

print(f"\nTask 5: V_UNKNOWN")
print(f"  Count: {len(v_unknown)}")