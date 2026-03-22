#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
v10 Step 2 Phase B: 정밀 검토
- Phase A 결과 + substatus + STEP7 대조로 최종 분류 결정
- 최종 분류: EXACT_MATCH / UPPER_MODULE / TRUE_MISSING / RECLASSIFIED
"""

import json
import re
import os
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = "D:/VAMOS/04. 구현단계/v10_results/phase2"
STEP7_DIR = "D:/VAMOS/docs/sot"

# agent → STEP7 파일 매핑
AGENT_TO_STEP7_FILES = {
    "M-1": ["STEP7-B", "STEP7-C"],
    "M-2": ["STEP7-D", "STEP7-E", "STEP7-F"],
    "M-3": ["STEP7-G", "STEP7-H"],
    "M-4": ["STEP7-I", "STEP7-J", "STEP7-K"],
    "M-5": ["STEP7-L", "STEP7-M", "STEP7-N", "STEP7-O", "STEP7-P"],
}

# STEP7 파일 캐시
_step7_cache = {}


def load_step7_file(prefix):
    """STEP7 파일 로드 (캐시)"""
    if prefix in _step7_cache:
        return _step7_cache[prefix]
    for fn in os.listdir(STEP7_DIR):
        if fn.startswith(prefix) and fn.endswith(".md"):
            path = os.path.join(STEP7_DIR, fn)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            _step7_cache[prefix] = content
            return content
    _step7_cache[prefix] = ""
    return ""


def search_step7(item, keywords):
    """STEP7 파일에서 키워드 검색"""
    agent = item.get("agent", "")
    prefixes = AGENT_TO_STEP7_FILES.get(agent, [])

    # agent로 특정 안 되면 전체 STEP7 검색
    if not prefixes:
        prefixes = list(AGENT_TO_STEP7_FILES.values())
        prefixes = [p for sublist in AGENT_TO_STEP7_FILES.values() for p in sublist]

    best_score = 0
    best_file = ""

    for prefix in prefixes:
        text = load_step7_file(prefix)
        if not text:
            continue
        text_lower = text.lower()

        score = 0
        # feature_id 검색
        if item["feature_id"].lower() in text_lower:
            score += 2
        # 키워드 검색
        for kw in keywords:
            if kw.lower() in text_lower:
                score += 1

        if score > best_score:
            best_score = score
            best_file = prefix

    return best_score, best_file


def extract_keywords(feature_name):
    """feature_name에서 핵심 키워드 추출"""
    if not feature_name:
        return []

    STOPWORDS = {"의", "를", "을", "에", "는", "은", "이", "가", "와", "과", "도", "로", "으로",
                 "에서", "까지", "부터", "및", "또는", "등", "기반", "관련", "위한", "통한", "대한",
                 "시", "후", "전", "중", "내", "간", "별", "형", "용", "화",
                 "the", "a", "an", "for", "of", "in", "on", "at", "to", "with", "by", "and", "or",
                 "is", "are", "be", "based", "using", "via", "from", "into"}

    tokens = re.split(r"[\s/\-_,]+", feature_name)
    keywords = []
    seen = set()
    for t in tokens:
        t_clean = t.strip("()[]{}·:;,.!?#")
        if t_clean.lower() in STOPWORDS or len(t_clean) < 2 or t_clean.lower() in seen:
            continue
        seen.add(t_clean.lower())
        keywords.append(t_clean)

    tech = [k for k in keywords if re.search(r"[A-Z]", k) or re.match(r"^[a-zA-Z]", k)]
    ko = [k for k in keywords if k not in tech]
    result = tech[:3] + ko[:1]
    return result if result else keywords[:3]


def classify_final(item):
    """최종 분류 결정"""
    fid = item["feature_id"]
    phase_a_cls = item["classification"]
    substatus = item.get("substatus", "") or ""
    action = item.get("action", "")
    severity = item.get("severity", "")
    step7_note = item.get("step7_note", "") or ""
    keywords = extract_keywords(item.get("feature_name", ""))

    # ──── Rule 1: EXACT_MATCH from Phase A (high confidence) ────
    if phase_a_cls == "EXACT_MATCH":
        return "EXACT_MATCH", "Phase A에서 PART2 정확 매칭 확인"

    # ──── Rule 2: action=RECLASSIFY_NA → RECLASSIFIED ────
    if action == "RECLASSIFY_NA":
        return "RECLASSIFIED", f"action=RECLASSIFY_NA, substatus={substatus}"

    # ──── Rule 3: action=SKIP (no substatus or substatus=none) → RECLASSIFIED ────
    if action == "SKIP" and substatus not in ("MISSING_CONFIRMED", "COVERED_BY_UPPER_MODULE"):
        return "RECLASSIFIED", f"action=SKIP, 구현 가이드 범위 외"

    # ──── Rule 4: substatus=COVERED_BY_UPPER_MODULE → UPPER_MODULE ────
    if substatus == "COVERED_BY_UPPER_MODULE":
        return "UPPER_MODULE", "사전 분석에서 상위 모듈 커버 확인"

    # ──── Rule 5: substatus=NOT_APPLICABLE → check deeper ────
    if substatus == "NOT_APPLICABLE":
        # STEP7 TITLE_ONLY → RECLASSIFIED
        if "TITLE_ONLY" in step7_note:
            return "RECLASSIFIED", f"STEP7 TITLE_ONLY: {step7_note}"
        # STEP7에서 검색
        s7_score, s7_file = search_step7(item, keywords)
        if s7_score >= 2:
            return "UPPER_MODULE", f"STEP7 {s7_file}에서 발견 (score={s7_score})"
        # NA + STEP7 미발견 → RECLASSIFIED
        return "RECLASSIFIED", f"NOT_APPLICABLE 유지, STEP7 미발견"

    # ──── Rule 6: substatus=MISSING_CONFIRMED → STEP7 교차 검증 ────
    if substatus == "MISSING_CONFIRMED":
        s7_score, s7_file = search_step7(item, keywords)
        if s7_score >= 2:
            return "UPPER_MODULE", f"STEP7 {s7_file}에서 발견 (score={s7_score}), PART2 §6→STEP7 참조 구조로 커버"
        if s7_score == 1:
            # 약한 매칭 → Phase A 결과도 고려
            if phase_a_cls in ("PARTIAL_MATCH", "UPPER_MODULE") and item.get("score", 0) >= 1:
                return "UPPER_MODULE", f"STEP7 약한 매칭 + PART2 부분 매칭, 상위 모듈 커버 판정"
        # STEP7에도 없음 → TRUE_MISSING
        return "TRUE_MISSING", f"PART2+STEP7 양쪽 모두 미발견, 진짜 누락"

    # ──── Rule 7: No substatus → action별 처리 ────
    if not substatus:
        if action == "SKIP":
            return "RECLASSIFIED", "action=SKIP, substatus 미지정"

        # STEP7 검색
        s7_score, s7_file = search_step7(item, keywords)
        if s7_score >= 2:
            return "UPPER_MODULE", f"STEP7 {s7_file}에서 발견 (score={s7_score})"

        # Phase A 매칭 결과 활용
        if phase_a_cls in ("PARTIAL_MATCH", "UPPER_MODULE") and item.get("score", 0) >= 2:
            return "UPPER_MODULE", f"PART2 강한 부분 매칭 (score={item.get('score', 0)})"

        if s7_score == 1 and phase_a_cls in ("PARTIAL_MATCH", "UPPER_MODULE"):
            return "UPPER_MODULE", f"STEP7 약한 매칭 + PART2 부분 매칭"

        # 나머지 → TRUE_MISSING
        return "TRUE_MISSING", f"PART2+STEP7 불충분, 진짜 누락"

    # Fallback
    return "TRUE_MISSING", f"미분류 fallback (substatus={substatus}, action={action})"


def main():
    print("=" * 60)
    print("v10 Step 2 Phase B: 정밀 검토")
    print("=" * 60)

    # Load Phase A results
    with open(f"{BASE_DIR}/v10_step2_phase_a_result.json", "r", encoding="utf-8") as f:
        phase_a = json.load(f)

    items = phase_a["items"]
    print(f"대상: {len(items)}건\n")

    # Phase B 분류
    results = []
    for item in items:
        final_cls, reason = classify_final(item)
        results.append({
            **item,
            "final_classification": final_cls,
            "final_reason": reason,
        })

    # 통계
    cls_dist = Counter(r["final_classification"] for r in results)
    print("Phase B 최종 분류 통계:")
    for cls in ["EXACT_MATCH", "UPPER_MODULE", "RECLASSIFIED", "TRUE_MISSING"]:
        print(f"  {cls}: {cls_dist.get(cls, 0)}건")
    print(f"  합계: {sum(cls_dist.values())}건")

    # TRUE_MISSING severity 분포
    tm = [r for r in results if r["final_classification"] == "TRUE_MISSING"]
    tm_sev = Counter(r["severity"] for r in tm)
    print(f"\nTRUE_MISSING severity 분포:")
    for sev in ["BLOCKER", "HIGH", "MEDIUM", "LOW"]:
        print(f"  {sev}: {tm_sev.get(sev, 0)}건")

    # TRUE_MISSING action 분포
    tm_act = Counter(r["action"] for r in tm)
    print(f"\nTRUE_MISSING action 분포: {dict(tm_act)}")

    # TRUE_MISSING version_scope 분포
    tm_vs = Counter(r["version_scope"] for r in tm)
    print(f"\nTRUE_MISSING version_scope 분포: {dict(tm_vs)}")

    # BLOCKER TRUE_MISSING 상세
    blocker_tm = [r for r in tm if r["severity"] == "BLOCKER"]
    if blocker_tm:
        print(f"\n⛔ BLOCKER TRUE_MISSING ({len(blocker_tm)}건):")
        for r in blocker_tm:
            print(f"  {r['feature_id']}: {r['feature_name']}")

    # 저장
    output = {
        "_meta": {
            "phase": "B",
            "total": len(results),
            "classification_dist": dict(cls_dist),
        },
        "items": results,
    }
    with open(f"{BASE_DIR}/v10_step2_phase_b_result.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n→ v10_step2_phase_b_result.json 저장 완료")

    # Phase C 필요성 판단
    if cls_dist.get("TRUE_MISSING", 0) == 0:
        print("\n✅ TRUE_MISSING = 0건 → Phase C 스킵, Phase D 직행")
    else:
        print(f"\n⚠ TRUE_MISSING = {cls_dist['TRUE_MISSING']}건 → Phase C 필요")

    print("\n" + "=" * 60)
    print("Phase B 완료")
    print("=" * 60)


if __name__ == "__main__":
    main()
