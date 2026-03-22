#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
v10 Step 2 전수 자동 검증 스크립트 (Phase A)
- consolidated_missing.json에서 Step1 제외 67건 빼고 1,001건 추출
- 각 항목의 feature_name에서 키워드 추출
- PART2 v22.0.0에서 키워드/ID 검색
- 4단계 분류: EXACT_MATCH / PARTIAL_MATCH / UPPER_MODULE / NOT_FOUND
- Phase TBD 304건 확정 (방법 a/b/c)
- 필드 정규화 (role, category)
"""

import json
import re
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# ─── 경로 설정 ───
BASE_DIR = "D:/VAMOS/04. 구현단계/v10_results/phase2"
PART2_PATH = "D:/VAMOS/docs/guides/VAMOS_구현가이드_PART2_구현단계.md"
STEP7_DIR = "D:/VAMOS/docs/sot"
STEP1_DIR = f"{BASE_DIR}/step1"

# ─── PART2 섹션 범위 (v22.0.0 기준) ───
PART2_SECTIONS = {
    "§1": (22, 53),
    "§2_V0": (54, 1383),
    "§3_V1_Phase1": (1384, 1486),
    "§3_V1_Phase2": (1487, 1574),
    "§3_V1_Phase3": (1575, 1623),
    "§3_V1_Phase4": (1624, 1667),
    "§3_V1_Phase5": (1668, 1706),
    "§3_V1_Phase6": (1707, 1767),
    "§4_V2_Phase1": (1768, 1932),
    "§4_V2_Phase2": (1933, 2117),
    "§4_V2_Phase3": (2118, 2286),
    "§5_V3_Phase1": (2287, 2433),
    "§5_V3_Phase2": (2434, 2717),
    "§5_V3_Phase3": (2718, 2902),
    "§6_1_UI": (2908, 3012),
    "§6_2_Rust": (3013, 3047),
    "§6_3_Test": (3048, 3079),
    "§6_4_CICD": (3080, 3102),
    "§6_5_Security": (3103, 3136),
    "§6_6_MCP": (3137, 3156),
    "§6_7_Agent": (3157, 3282),
    "§6_8_AIInvest": (3283, 3404),
    "§6_9_SDAR": (3405, 3517),
    "§6_10_Cloud": (3518, 3745),
    "§6_11_Event": (3746, 3810),
    "§6_12_Ops": (3811, 3821),
    "§6_13_Workload": (3822, 3846),
    "§7_GONOGO": (3847, 4060),
}

# version_scope → suggested_phase 매핑용 Phase 섹션
VERSION_TO_PHASES = {
    "V0": ["§2_V0"],
    "V1": ["§3_V1_Phase1", "§3_V1_Phase2", "§3_V1_Phase3", "§3_V1_Phase4", "§3_V1_Phase5", "§3_V1_Phase6"],
    "V2": ["§4_V2_Phase1", "§4_V2_Phase2", "§4_V2_Phase3"],
    "V3": ["§5_V3_Phase1", "§5_V3_Phase2", "§5_V3_Phase3"],
}

# agent → §6 매핑
AGENT_TO_S6 = {
    "M-1": ["§6_1_UI", "§6_2_Rust"],
    "M-2": ["§6_8_AIInvest", "§6_3_Test"],
    "M-3": ["§6_5_Security", "§6_9_SDAR", "§6_11_Event"],
    "M-4": ["§6_7_Agent"],
    "M-5": ["§6_4_CICD", "§6_6_MCP", "§6_10_Cloud", "§6_12_Ops"],
}

# agent → STEP7 파일 매핑
AGENT_TO_STEP7 = {
    "M-1": ["STEP7-B", "STEP7-C"],
    "M-2": ["STEP7-D", "STEP7-E", "STEP7-F"],
    "M-3": ["STEP7-G", "STEP7-H"],
    "M-4": ["STEP7-I", "STEP7-J", "STEP7-K"],
    "M-5": ["STEP7-L", "STEP7-M", "STEP7-N", "STEP7-O", "STEP7-P"],
}

# ─── 한국어 불용어 ───
STOPWORDS_KO = {"의", "를", "을", "에", "는", "은", "이", "가", "와", "과", "도", "로", "으로",
                "에서", "까지", "부터", "및", "또는", "등", "기반", "관련", "위한", "통한", "대한",
                "시", "후", "전", "중", "내", "간", "별", "형", "용", "화"}
STOPWORDS_EN = {"the", "a", "an", "for", "of", "in", "on", "at", "to", "with", "by", "and", "or",
                "is", "are", "be", "was", "were", "has", "have", "had", "this", "that", "these",
                "based", "using", "via", "from", "into"}


def load_part2():
    """PART2 전문 로드 (라인 배열)"""
    with open(PART2_PATH, "r", encoding="utf-8") as f:
        return f.readlines()


def load_part2_section(lines, section_key):
    """PART2 특정 섹션만 추출"""
    if section_key not in PART2_SECTIONS:
        return ""
    start, end = PART2_SECTIONS[section_key]
    return "".join(lines[start - 1:end])


def load_step1_excluded_ids():
    """Step1 제외 67건 ID 추출"""
    # 먼저 전체 feature_id 셋 로드
    with open(f"{BASE_DIR}/consolidated_missing.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    all_ids = set(d["feature_id"] for d in data["items"])

    excluded = set()
    for fn in os.listdir(STEP1_DIR):
        if fn.startswith("3-") and fn.endswith(".md"):
            with open(f"{STEP1_DIR}/{fn}", "r", encoding="utf-8") as f:
                content = f.read()
            headers = re.findall(r"^### (\S+)", content, re.MULTILINE)
            for h in headers:
                if h in all_ids:
                    excluded.add(h)
    return excluded


def extract_keywords(feature_name):
    """feature_name에서 핵심 키워드 1~3개 추출"""
    if not feature_name:
        return []

    # 괄호 안 내용도 키워드 후보
    parens = re.findall(r"\(([^)]+)\)", feature_name)

    # 전체 토큰화 (공백, /, -, _ 기준)
    tokens = re.split(r"[\s/\-_,]+", feature_name)
    # 괄호 내용도 추가
    for p in parens:
        tokens.extend(re.split(r"[\s/\-_,]+", p))

    # 불용어 제거 + 길이 필터
    keywords = []
    seen = set()
    for t in tokens:
        t_clean = t.strip("()[]{}·:;,.!?#")
        t_lower = t_clean.lower()
        if t_lower in STOPWORDS_KO or t_lower in STOPWORDS_EN:
            continue
        if len(t_clean) < 2:
            continue
        if t_lower in seen:
            continue
        seen.add(t_lower)
        keywords.append(t_clean)

    # 기술용어/고유명사 우선 (대문자 포함 또는 영문)
    tech = [k for k in keywords if re.search(r"[A-Z]", k) or re.match(r"^[a-zA-Z]", k)]
    ko = [k for k in keywords if k not in tech]

    # 최대 4개 (기술용어 우선)
    result = tech[:3] + ko[:1]
    if not result and keywords:
        result = keywords[:3]
    return result


def normalize_fields(items):
    """필드 정규화: role, category"""
    for item in items:
        # role 정규화
        if item.get("role") == "CROSSCHECK":
            item["role"] = "CROSS_CHECK"
        if not item.get("role", "").strip():
            item["role"] = "PRIMARY"
    return items


def resolve_highest_version(version_scope):
    """Multi-version에서 최고 버전 추출"""
    versions = [v.strip() for v in version_scope.split(",")]
    order = {"V3": 4, "V2": 3, "V1": 2, "V0": 1}
    best = max(versions, key=lambda v: order.get(v, 0))
    return best


def get_phase_sections(version_scope):
    """version_scope에서 검색할 Phase 섹션들 반환"""
    if "," in version_scope:
        v = resolve_highest_version(version_scope)
    else:
        v = version_scope
    return VERSION_TO_PHASES.get(v, [])


def get_s6_sections(agent):
    """agent에서 검색할 §6 섹션들 반환"""
    return AGENT_TO_S6.get(agent, [])


def search_in_text(text, keywords, feature_id):
    """텍스트에서 키워드/ID 검색, 매칭 점수 반환"""
    if not text:
        return 0, []

    text_lower = text.lower()
    matches = []

    # feature_id 직접 검색
    if feature_id and feature_id.lower() in text_lower:
        matches.append(("ID", feature_id))

    # 키워드 검색
    for kw in keywords:
        kw_lower = kw.lower()
        if kw_lower in text_lower:
            matches.append(("KW", kw))

    return len(matches), matches


def classify_item(item, part2_lines):
    """단일 항목 분류"""
    fid = item["feature_id"]
    fname = item["feature_name"]
    vs = item["version_scope"]
    agent = item.get("agent", "")
    sp = item.get("suggested_phase", "")

    keywords = extract_keywords(fname)

    # 검색 대상 섹션 결정
    phase_sections = get_phase_sections(vs)
    s6_sections = get_s6_sections(agent)
    all_sections = phase_sections + s6_sections

    best_score = 0
    best_matches = []
    best_section = ""
    all_section_results = {}

    for sec in all_sections:
        text = load_part2_section(part2_lines, sec)
        score, matches = search_in_text(text, keywords, fid)
        all_section_results[sec] = {"score": score, "matches": matches}
        if score > best_score:
            best_score = score
            best_matches = matches
            best_section = sec

    # §1~§7 전체도 확인 (다른 섹션에서 참조될 수 있음)
    if best_score == 0:
        # 전체 검색 (특정 안 나오면)
        full_text = "".join(part2_lines)
        score, matches = search_in_text(full_text, keywords, fid)
        if score > 0:
            best_score = score
            best_matches = matches
            best_section = "OTHER"

    # 분류
    has_id_match = any(m[0] == "ID" for m in best_matches)
    kw_count = sum(1 for m in best_matches if m[0] == "KW")

    if has_id_match or (kw_count >= 2 and best_score >= 3):
        classification = "EXACT_MATCH"
    elif kw_count >= 1 and best_score >= 1:
        classification = "PARTIAL_MATCH"
    elif best_score == 0 and any(sec.startswith("§6") for sec in all_sections):
        # §6 시스템 상세에서 상위 모듈 존재 여부 확인
        for sec in s6_sections:
            text = load_part2_section(part2_lines, sec)
            if text and len(text) > 100:
                # 상위 모듈 존재 = 시스템 상세가 있음
                classification = "UPPER_MODULE"
                best_section = sec
                break
        else:
            classification = "NOT_FOUND"
    else:
        classification = "NOT_FOUND" if best_score == 0 else "PARTIAL_MATCH"

    return {
        "feature_id": fid,
        "classification": classification,
        "score": best_score,
        "matched_section": best_section,
        "matches": [(m[0], m[1]) for m in best_matches],
        "keywords_used": keywords,
    }


def resolve_phase_tbd(item, part2_lines):
    """Phase TBD 항목의 Phase 확정"""
    sp = item.get("suggested_phase", "")
    if "TBD" not in sp:
        return None

    fname = item["feature_name"]
    agent = item.get("agent", "")
    vs = item["version_scope"]
    keywords = extract_keywords(fname)

    # 방법 a: feature_name 키워드가 특정 Phase 테이블에 있는지 확인
    if "," in vs:
        v = resolve_highest_version(vs)
    else:
        v = vs

    phase_sections = VERSION_TO_PHASES.get(v, [])
    best_phase = None
    best_score = 0

    for sec in phase_sections:
        text = load_part2_section(part2_lines, sec)
        score, matches = search_in_text(text, keywords, item["feature_id"])
        if score > best_score:
            best_score = score
            best_phase = sec

    if best_phase and best_score >= 1:
        return {
            "resolved_phase": best_phase,
            "method": "a",
            "detail": f"feature_name 키워드가 {best_phase}에서 발견 (score={best_score})"
        }

    # 방법 b: agent 필드로 §6.x 매핑 → 참조 Phase 확인
    s6_sections = get_s6_sections(agent)
    for sec in s6_sections:
        text = load_part2_section(part2_lines, sec)
        score, matches = search_in_text(text, keywords, item["feature_id"])
        if score >= 1:
            # §6에서 발견 → 해당 §6이 참조하는 Phase를 추정
            # V별 기본 Phase: V1→Phase1, V2→Phase2, V3→Phase2
            default_phases = {"V0": "§2_V0", "V1": "§3_V1_Phase1", "V2": "§4_V2_Phase2", "V3": "§5_V3_Phase2"}
            resolved = default_phases.get(v, phase_sections[0] if phase_sections else None)
            if resolved:
                return {
                    "resolved_phase": resolved,
                    "method": "b",
                    "detail": f"agent={agent} → {sec}에서 키워드 발견, {v} 기본 Phase 배정"
                }

    # 방법 c: 미정 → ESCALATED
    return {
        "resolved_phase": "ESCALATED",
        "method": "c",
        "detail": "Phase TBD 방법 a/b로 확정 불가"
    }


def main():
    print("=" * 60)
    print("v10 Step 2 전수 자동 검증 (Phase A)")
    print("=" * 60)

    # 1. 입력 로드
    print("\n[1] consolidated_missing.json 로드...")
    with open(f"{BASE_DIR}/consolidated_missing.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    all_items = data["items"]
    print(f"  총 항목: {len(all_items)}")

    # 스키마 검증
    required_fields = ["feature_id", "feature_name", "version_scope", "severity", "agent", "suggested_phase", "action"]
    for field in required_fields:
        missing = sum(1 for d in all_items if field not in d)
        if missing > 0:
            print(f"  ⛔ 필수 필드 '{field}' 누락: {missing}건")
            sys.exit(1)
    # status는 RESOLVED 항목에만 존재 (optional)
    status_count = sum(1 for d in all_items if d.get("status") == "RESOLVED")
    print(f"  status=RESOLVED: {status_count}건 (나머지는 미지정=정상)")

    valid_vs = {"V0", "V1", "V2", "V3", "V_UNKNOWN"}
    valid_sev = {"BLOCKER", "HIGH", "MEDIUM", "LOW"}
    for item in all_items:
        vs_parts = [v.strip() for v in item["version_scope"].split(",")]
        for vp in vs_parts:
            if vp not in valid_vs:
                print(f"  ⚠ 비표준 version_scope: {item['feature_id']} = {item['version_scope']}")
                break
        if item["severity"] not in valid_sev:
            print(f"  ⛔ 비표준 severity: {item['feature_id']} = {item['severity']}")
            sys.exit(1)

    # ID 중복 검사
    ids = [d["feature_id"] for d in all_items]
    if len(ids) != len(set(ids)):
        print(f"  ⛔ feature_id 중복 발견")
        sys.exit(1)
    print("  ✅ 스키마 검증 통과")

    # 2. Step1 제외
    print("\n[2] Step1 제외 ID 추출...")
    excluded = load_step1_excluded_ids()
    print(f"  제외: {len(excluded)}건")

    target_items = [d for d in all_items if d["feature_id"] not in excluded]
    print(f"  대상: {len(target_items)}건")
    assert len(target_items) == 1001, f"대상 건수 불일치: {len(target_items)} != 1001"

    # 3. 필드 정규화
    print("\n[3] 필드 정규화...")
    target_items = normalize_fields(target_items)

    # 4. PART2 로드
    print("\n[4] PART2 v22.0.0 로드...")
    part2_lines = load_part2()
    print(f"  총 행: {len(part2_lines)}")

    # 5. Phase TBD 확정 (A-1)
    print("\n[5] Phase TBD 확정...")
    tbd_items = [d for d in target_items if "TBD" in str(d.get("suggested_phase", ""))]
    print(f"  Phase TBD 대상: {len(tbd_items)}건")

    tbd_results = []
    for item in tbd_items:
        result = resolve_phase_tbd(item, part2_lines)
        if result:
            tbd_results.append({
                "feature_id": item["feature_id"],
                "original_suggested_phase": item["suggested_phase"],
                "resolved_phase": result["resolved_phase"],
                "resolution_method": result["method"],
                "resolution_detail": result["detail"],
                "final_classification": ""  # Phase B/C 후 확정
            })

    tbd_escalated = sum(1 for r in tbd_results if r["resolved_phase"] == "ESCALATED")
    print(f"  확정: {len(tbd_results) - tbd_escalated}건, ESCALATED: {tbd_escalated}건")

    # Phase TBD 결과 저장
    tbd_output = {
        "resolved_count": len(tbd_results),
        "escalated_count": tbd_escalated,
        "items": tbd_results
    }
    with open(f"{BASE_DIR}/v10_phase_tbd_resolved.json", "w", encoding="utf-8") as f:
        json.dump(tbd_output, f, ensure_ascii=False, indent=2)
    print(f"  → v10_phase_tbd_resolved.json 저장 완료")

    # 6. action 필드 사전 분류 (A-3)
    print("\n[6] action 필드 사전 분류...")
    from collections import Counter
    action_dist = Counter(d["action"] for d in target_items)
    for act, cnt in action_dist.items():
        print(f"  {act}: {cnt}건")

    # 7. 자동 커버리지 검증 (A-2~A-4)
    print("\n[7] PART2 자동 키워드 검색 + 분류...")
    results = []
    for i, item in enumerate(target_items):
        if (i + 1) % 100 == 0:
            print(f"  진행: {i+1}/1001")
        result = classify_item(item, part2_lines)
        result["version_scope"] = item["version_scope"]
        result["severity"] = item["severity"]
        result["agent"] = item.get("agent", "")
        result["action"] = item["action"]
        result["suggested_phase"] = item.get("suggested_phase", "")
        result["feature_name"] = item["feature_name"]
        result["role"] = item.get("role", "")
        result["category"] = item.get("category", "")
        result["source_section"] = item.get("source_section", "")
        result["substatus"] = item.get("substatus", "")
        result["step7_note"] = item.get("step7_note", "")
        results.append(result)

    # 8. 분류 통계
    print("\n[8] Phase A 분류 통계:")
    cls_dist = Counter(r["classification"] for r in results)
    for cls in ["EXACT_MATCH", "PARTIAL_MATCH", "UPPER_MODULE", "NOT_FOUND"]:
        print(f"  {cls}: {cls_dist.get(cls, 0)}건")
    print(f"  합계: {sum(cls_dist.values())}건")

    # severity별 NOT_FOUND
    print("\n  NOT_FOUND severity 분포:")
    nf_items = [r for r in results if r["classification"] == "NOT_FOUND"]
    nf_sev = Counter(r["severity"] for r in nf_items)
    for sev in ["BLOCKER", "HIGH", "MEDIUM", "LOW"]:
        print(f"    {sev}: {nf_sev.get(sev, 0)}건")

    # 9. 결과 저장
    output = {
        "_meta": {
            "phase": "A",
            "total": len(results),
            "classification_dist": dict(cls_dist),
        },
        "items": results,
    }
    with open(f"{BASE_DIR}/v10_step2_phase_a_result.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n→ v10_step2_phase_a_result.json 저장 완료")

    # 10. Phase B 대상 추출
    phase_b_targets = [r for r in results if r["classification"] in ("NOT_FOUND", "PARTIAL_MATCH")]
    print(f"\n[Phase B 대상] NOT_FOUND + PARTIAL_MATCH: {len(phase_b_targets)}건")

    print("\n" + "=" * 60)
    print("Phase A 완료")
    print("=" * 60)


if __name__ == "__main__":
    main()
