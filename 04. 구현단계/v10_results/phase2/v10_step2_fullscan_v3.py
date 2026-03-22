#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
v10 Step 2 전수 팩트 검증 v3 — 강화 검색
개선점:
1. STEP7: feature_name 핵심어 전문 검색 (단일 term도 매칭)
2. PART2: 동적 용어 인덱스 (사전 정의가 아닌 항목 feature_name 기반)
3. 각 항목에 가장 가까운 PART2/STEP7 줄을 찾아 evidence로 기록
4. evidence 없는 항목은 NOT_FOUND 유지 (거짓 분류 방지)
"""

import json, re, os, sys
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = "D:/VAMOS/04. 구현단계/v10_results/phase2"
PART2_PATH = "D:/VAMOS/docs/guides/VAMOS_구현가이드_PART2_구현단계.md"
STEP7_DIR = "D:/VAMOS/docs/sot"
STEP1_DIR = f"{BASE_DIR}/step1"

SECTIONS = {
    "§2_V0": (54, 1383),
    "§3_V1_P1": (1384, 1486), "§3_V1_P2": (1487, 1574),
    "§3_V1_P3": (1575, 1623), "§3_V1_P4": (1624, 1667),
    "§3_V1_P5": (1668, 1706), "§3_V1_P6": (1707, 1767),
    "§4_V2_P1": (1768, 1932), "§4_V2_P2": (1933, 2117),
    "§4_V2_P3": (2118, 2286),
    "§5_V3_P1": (2287, 2433), "§5_V3_P2": (2434, 2717),
    "§5_V3_P3": (2718, 2902),
    "§6_1": (2908, 3012), "§6_2": (3013, 3047),
    "§6_3": (3048, 3079), "§6_4": (3080, 3102),
    "§6_5": (3103, 3136), "§6_6": (3137, 3156),
    "§6_7": (3157, 3282), "§6_8": (3283, 3404),
    "§6_9": (3405, 3517), "§6_10": (3518, 3745),
    "§6_11": (3746, 3810), "§6_12": (3811, 3821),
    "§6_13": (3822, 3846), "§7": (3847, 4060),
}

VS_SECS = {
    "V0": ["§2_V0"],
    "V1": ["§3_V1_P1","§3_V1_P2","§3_V1_P3","§3_V1_P4","§3_V1_P5","§3_V1_P6"],
    "V2": ["§4_V2_P1","§4_V2_P2","§4_V2_P3"],
    "V3": ["§5_V3_P1","§5_V3_P2","§5_V3_P3"],
}

AGENT_S6 = {
    "M-1": ["§6_1","§6_2"], "M-2": ["§6_3","§6_8"],
    "M-3": ["§6_5","§6_9","§6_11"], "M-4": ["§6_7"],
    "M-5": ["§6_4","§6_6","§6_10","§6_12"],
}

AGENT_S7 = {
    "M-1": ["STEP7-B","STEP7-C"], "M-2": ["STEP7-D","STEP7-E","STEP7-F"],
    "M-3": ["STEP7-G","STEP7-H"], "M-4": ["STEP7-I","STEP7-J","STEP7-K"],
    "M-5": ["STEP7-L","STEP7-M","STEP7-N","STEP7-O","STEP7-P"],
}

STOPWORDS = frozenset([
    "구현","기반","관련","설정","시스템","모듈","엔진","매니저","통합","지원",
    "기능","처리","관리","추가","확장","적용","자동","수동","전체","최소","최대",
    "정의","검증","구조","방식","타입","규칙","정책","상태","프로세스","파이프라인",
    "for","the","and","with","from","into","based","using","via","this","that",
    "의","를","을","에","는","은","이","가","등","및","또는","부터","까지","대한",
])


def get_section(line_no):
    for sk, (s, e) in SECTIONS.items():
        if s <= line_no <= e:
            return sk
    return "OTHER"


def extract_search_terms(feature_name):
    """feature_name에서 검색 가능한 핵심 단어/구 추출
    반환: [(term, weight)] — weight: 3=고유명사/영문기술, 2=한국어기술, 1=일반
    """
    terms = []
    if not feature_name:
        return terms

    # 1) 괄호 안 내용 추출 (파일명, 기술명 등)
    parens = re.findall(r'\(([^)]+)\)', feature_name)
    for p in parens:
        p_clean = p.strip()
        if p_clean:
            # 파일명(.py 등)은 최고 가중치
            if re.search(r'\.\w{2,3}$', p_clean):
                terms.append((p_clean, 4))
            else:
                terms.append((p_clean, 3))

    # 2) 전체를 토큰화
    # 괄호 제거 후 토큰화
    clean = re.sub(r'\([^)]*\)', ' ', feature_name)
    tokens = re.split(r'[\s/\-_,;:+→←↔·]+', clean)

    seen = set()
    for t in tokens:
        t = t.strip('()[]{}#"\'!?.·')
        if not t or len(t) < 2:
            continue
        t_lower = t.lower()
        if t_lower in STOPWORDS:
            continue
        if t_lower in seen:
            continue
        seen.add(t_lower)

        # 가중치 결정
        if re.match(r'^[A-Z][A-Z0-9_\-]+$', t):  # 약어/상수 (PARL, HMAC, LSTM)
            terms.append((t, 3))
        elif re.match(r'^[A-Z]', t) and len(t) >= 3:  # CamelCase 기술용어
            terms.append((t, 3))
        elif re.match(r'^[a-z]', t) and len(t) >= 4:  # 영문 소문자 (langgraph)
            terms.append((t, 2))
        elif len(t) >= 2:  # 한국어
            terms.append((t, 2))

    # 정렬: 가중치 높은 순
    terms.sort(key=lambda x: -x[1])
    return terms


def search_lines(lines_with_meta, search_terms, relevant_sections=None, max_results=5):
    """줄 목록에서 검색어 매칭. 반환: [(line_no, text, section, matched_terms, score)]"""
    results = []

    for (ln, text, sec) in lines_with_meta:
        if relevant_sections and sec not in relevant_sections and sec != "OTHER":
            continue

        text_lower = text.lower()
        matched = []
        score = 0

        for (term, weight) in search_terms:
            term_lower = term.lower()
            if term_lower in text_lower:
                matched.append(term)
                score += weight

        if score >= 3:  # 최소 threshold
            results.append((ln, text, sec, matched, score))

    results.sort(key=lambda x: -x[4])
    return results[:max_results]


def search_step7_lines(s7_data, search_terms, prefixes, max_results=3):
    """STEP7 파일에서 검색. 반환: [(prefix, ln, text, matched, score)]"""
    results = []
    for prefix in prefixes:
        if prefix not in s7_data:
            continue
        for (ln, text) in s7_data[prefix]:
            text_lower = text.lower()
            matched = []
            score = 0
            for (term, weight) in search_terms:
                if term.lower() in text_lower:
                    matched.append(term)
                    score += weight
            if score >= 3:
                results.append((prefix, ln, text, matched, score))

    results.sort(key=lambda x: -x[4])
    return results[:max_results]


def verify_item(item, p2_lines, s7_data):
    """단일 항목 검증. evidence 기반 분류."""
    fid = item["feature_id"]
    fname = item["feature_name"]
    vs = item["version_scope"]
    agent = item.get("agent", "")
    action = item.get("action", "")
    substatus = item.get("substatus", "")

    # 관련 섹션
    if "," in vs:
        versions = [v.strip() for v in vs.split(",")]
        hi_v = max(versions, key=lambda v: {"V3":4,"V2":3,"V1":2,"V0":1}.get(v, 0))
    else:
        hi_v = vs

    relevant = set(VS_SECS.get(hi_v, []) + AGENT_S6.get(agent, []))
    s7_prefixes = AGENT_S7.get(agent, list(set(p for ps in AGENT_S7.values() for p in ps)))

    search_terms = extract_search_terms(fname)
    # feature_id도 검색 term에 추가 (최고 가중치)
    search_terms.insert(0, (fid, 5))

    evidence = []

    # ── PART2 검색 ──
    # A) 관련 섹션 우선 검색
    p2_hits = search_lines(p2_lines, search_terms, relevant_sections=relevant)
    for (ln, text, sec, matched, score) in p2_hits:
        evidence.append({
            "source": "PART2", "section": sec, "line": ln,
            "text": text[:200], "matched": matched, "score": score,
            "relevant": sec in relevant,
        })

    # B) 관련 섹션 미발견 시 전체 검색
    if not p2_hits:
        p2_hits_all = search_lines(p2_lines, search_terms, relevant_sections=None)
        for (ln, text, sec, matched, score) in p2_hits_all:
            evidence.append({
                "source": "PART2", "section": sec, "line": ln,
                "text": text[:200], "matched": matched, "score": score,
                "relevant": sec in relevant,
            })

    # ── STEP7 검색 ──
    s7_hits = search_step7_lines(s7_data, search_terms, s7_prefixes)
    for (prefix, ln, text, matched, score) in s7_hits:
        evidence.append({
            "source": prefix, "section": "", "line": ln,
            "text": text[:200], "matched": matched, "score": score,
            "relevant": True,
        })

    # ── 분류 결정 ──
    p2_ev = [e for e in evidence if e["source"] == "PART2"]
    s7_ev = [e for e in evidence if e["source"].startswith("STEP7")]
    p2_relevant = [e for e in p2_ev if e["relevant"]]

    # EXACT_MATCH: PART2 관련 섹션에서 score>=6 (고품질 매칭)
    if p2_relevant and p2_relevant[0]["score"] >= 6:
        best = p2_relevant[0]
        return "EXACT_MATCH", evidence, (
            f"PART2 {best['section']} L{best['line']} — 매칭: {best['matched']} — "
            f"인용: \"{best['text'][:100]}\""
        )

    # EXACT_MATCH: PART2 어디서든 feature_id 직접 발견
    fid_ev = [e for e in p2_ev if fid in e.get("matched", [])]
    if fid_ev:
        best = fid_ev[0]
        return "EXACT_MATCH", evidence, (
            f"PART2 {best['section']} L{best['line']}에 feature_id '{fid}' 직접 존재 — "
            f"인용: \"{best['text'][:100]}\""
        )

    # UPPER_MODULE: PART2 관련 섹션에서 score>=4
    if p2_relevant and p2_relevant[0]["score"] >= 4:
        best = p2_relevant[0]
        return "UPPER_MODULE", evidence, (
            f"PART2 {best['section']} L{best['line']} — 매칭: {best['matched']} — "
            f"인용: \"{best['text'][:100]}\""
        )

    # UPPER_MODULE: PART2 비관련 섹션이지만 score>=5
    if p2_ev and p2_ev[0]["score"] >= 5:
        best = p2_ev[0]
        return "UPPER_MODULE", evidence, (
            f"PART2 {best['section']} L{best['line']} (비관련섹션) — 매칭: {best['matched']} — "
            f"인용: \"{best['text'][:100]}\""
        )

    # UPPER_MODULE: STEP7에서 score>=4
    if s7_ev and s7_ev[0]["score"] >= 4:
        best = s7_ev[0]
        return "UPPER_MODULE", evidence, (
            f"{best['source']} L{best['line']} — 매칭: {best['matched']} — "
            f"PART2 §6→STEP7 참조 구조로 커버 — 인용: \"{best['text'][:100]}\""
        )

    # UPPER_MODULE: PART2 관련섹션 score>=3 + STEP7 score>=3 (교차확인)
    if p2_relevant and p2_relevant[0]["score"] >= 3 and s7_ev and s7_ev[0]["score"] >= 3:
        p_best = p2_relevant[0]
        s_best = s7_ev[0]
        return "UPPER_MODULE", evidence, (
            f"PART2 {p_best['section']} L{p_best['line']} + {s_best['source']} L{s_best['line']} "
            f"교차 확인 — PART2 매칭: {p_best['matched']}, STEP7 매칭: {s_best['matched']}"
        )

    # STEP7만 score>=3
    if s7_ev and s7_ev[0]["score"] >= 3:
        best = s7_ev[0]
        return "UPPER_MODULE", evidence, (
            f"{best['source']} L{best['line']} — 매칭: {best['matched']} — "
            f"PART2 §6→STEP7 참조 구조로 커버 — 인용: \"{best['text'][:100]}\""
        )

    # PART2 관련섹션 score>=3 (단독)
    if p2_relevant and p2_relevant[0]["score"] >= 3:
        best = p2_relevant[0]
        return "UPPER_MODULE", evidence, (
            f"PART2 {best['section']} L{best['line']} — 매칭: {best['matched']} — "
            f"인용: \"{best['text'][:100]}\""
        )

    # RECLASSIFIED: action/substatus 기반 (evidence 없지만 의미상 비대상)
    if action == "RECLASSIFY_NA":
        return "RECLASSIFIED", evidence, f"action=RECLASSIFY_NA, substatus={substatus}, PART2/STEP7 증거 없음"
    if action == "SKIP" and substatus != "MISSING_CONFIRMED":
        return "RECLASSIFIED", evidence, f"action=SKIP, substatus={substatus}, PART2/STEP7 증거 없음"
    if substatus == "NOT_APPLICABLE":
        return "RECLASSIFIED", evidence, f"substatus=NOT_APPLICABLE, PART2/STEP7 증거 없음"

    # NOT_FOUND: 모든 검색 실패
    best_info = ""
    if p2_ev:
        best_info += f"PART2 최고점: {p2_ev[0]['section']} L{p2_ev[0]['line']} score={p2_ev[0]['score']} "
    if s7_ev:
        best_info += f"STEP7 최고점: {s7_ev[0]['source']} L{s7_ev[0]['line']} score={s7_ev[0]['score']} "
    if not best_info:
        best_info = "검색 결과 없음"

    return "NOT_FOUND", evidence, f"PART2+STEP7 증거 미달 ({best_info})"


def main():
    print("=" * 70)
    print("v10 Step 2 전수 팩트 검증 v3 — 강화 검색")
    print("=" * 70)

    # 데이터 로드
    with open(f"{BASE_DIR}/consolidated_missing.json", "r", encoding="utf-8") as f:
        cdata = json.load(f)

    # 제외 ID
    all_ids = set(d["feature_id"] for d in cdata["items"])
    excluded = set()
    for fn in os.listdir(STEP1_DIR):
        if fn.startswith("3-") and fn.endswith(".md"):
            with open(f"{STEP1_DIR}/{fn}", "r", encoding="utf-8") as f:
                content = f.read()
            for h in re.findall(r"^### (\S+)", content, re.MULTILINE):
                if h in all_ids:
                    excluded.add(h)

    target = [d for d in cdata["items"] if d["feature_id"] not in excluded]
    assert len(target) == 1001, f"대상 {len(target)} != 1001"
    print(f"대상: {len(target)}건")

    # PART2 로드 + 인덱스
    with open(PART2_PATH, "r", encoding="utf-8") as f:
        raw_lines = f.readlines()
    p2_lines = []
    for i, l in enumerate(raw_lines):
        ln = i + 1
        text = l.rstrip()
        if text.strip():
            sec = get_section(ln)
            p2_lines.append((ln, text, sec))
    print(f"PART2: {len(p2_lines)}줄 (비공백)")

    # STEP7 로드
    s7_data = {}
    for fn in sorted(os.listdir(STEP7_DIR)):
        if not (fn.startswith("STEP7-") and fn.endswith(".md")):
            continue
        prefix = fn.split("_")[0]
        with open(os.path.join(STEP7_DIR, fn), "r", encoding="utf-8") as f:
            lines = f.readlines()
        s7_data[prefix] = [(i+1, l.rstrip()) for i, l in enumerate(lines) if l.strip()]
    print(f"STEP7: {len(s7_data)}파일")

    # 전수 검증
    print(f"\n검증 시작...")
    results = []
    for i, item in enumerate(target):
        if (i + 1) % 200 == 0:
            print(f"  진행: {i+1}/1001")
        cls, ev, reason = verify_item(item, p2_lines, s7_data)
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
            "classification": cls,
            "evidence": ev,
            "evidence_count": len(ev),
            "reason": reason,
        })

    # 통계
    cls_dist = Counter(r["classification"] for r in results)
    with_ev = sum(1 for r in results if r["evidence_count"] > 0)

    print(f"\n{'='*70}")
    print("검증 결과:")
    for c in ["EXACT_MATCH","UPPER_MODULE","RECLASSIFIED","NOT_FOUND"]:
        print(f"  {c}: {cls_dist.get(c,0)}건")
    print(f"  합계: {sum(cls_dist.values())}건")
    print(f"  증거 있음: {with_ev}건, 증거 없음: {sum(cls_dist.values())-with_ev}건")

    nf = [r for r in results if r["classification"] == "NOT_FOUND"]
    if nf:
        nf_sev = Counter(r["severity"] for r in nf)
        print(f"\n  NOT_FOUND severity: {dict(nf_sev)}")
        # NOT_FOUND 중 부분 증거 있는 것
        nf_partial = [r for r in nf if r["evidence_count"] > 0]
        print(f"  NOT_FOUND 중 부분증거 있음: {nf_partial and len(nf_partial) or 0}건")

    # 저장
    output = {
        "_meta": {
            "version": "v3_enhanced",
            "total": len(results),
            "dist": dict(cls_dist),
            "with_evidence": with_ev,
        },
        "items": results,
    }
    out_path = f"{BASE_DIR}/v10_step2_factcheck_v3.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n→ {out_path}")


if __name__ == "__main__":
    main()
