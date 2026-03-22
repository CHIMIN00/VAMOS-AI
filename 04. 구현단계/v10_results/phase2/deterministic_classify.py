#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VAMOS v10 Phase 2 - Deterministic Classification
확정 기준으로 1,068건 1회 일괄 분류.
규칙: PART2에 명시적 키워드가 없으면 REAL_GAP (암묵적 커버 불인정)
"""

import json
import re
import sys
import os

# ─── 파일 로드 ──────────────────────────────────────────
PART2_PATH = r"D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md"
CONSOLIDATED_PATH = r"D:\VAMOS\04. 구현단계\v10_results\phase2\consolidated_missing.json"
OUTPUT_PATH = r"D:\VAMOS\04. 구현단계\v10_results\phase2\deterministic_result.json"

with open(PART2_PATH, "r", encoding="utf-8") as f:
    part2_text = f.read()
    part2_lower = part2_text.lower()

with open(CONSOLIDATED_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

items = data["items"]
print(f"Total items: {len(items)}")

# ─── §6 영역 분리 ────────────────────────────────────────
# §6 starts at "# 6." or "## 6." and ends at "# 7."
s6_match = re.search(r'^#{1,2}\s+6[\.\s]', part2_text, re.MULTILINE)
s7_match = re.search(r'^#{1,2}\s+7[\.\s]', part2_text, re.MULTILINE)
if s6_match and s7_match:
    section6_text = part2_text[s6_match.start():s7_match.start()].lower()
    section2to5_text = part2_text[:s6_match.start()].lower()
else:
    section6_text = ""
    section2to5_text = part2_lower
    print("WARNING: Could not split §6 / §2-§5")

# ─── 스톱워드 (검색에서 제외할 일반 단어) ────────────────
STOPWORDS = {
    "구현", "시스템", "모듈", "기능", "패턴", "방식", "처리", "관리",
    "기반", "자동", "설정", "항목", "단계", "전체", "기본", "확장",
    "추가", "적용", "지원", "연동", "통합", "정의", "생성", "등록",
    "수행", "실행", "결과", "데이터", "정보", "상태", "제공", "사용",
    "진행", "완료", "필요", "포함", "대상", "목록", "내용", "유형",
    "파일", "코드", "함수", "클래스", "로직", "프로세스",
    "implementation", "system", "module", "function", "pattern",
    "based", "auto", "config", "step", "phase", "the", "and", "for",
    "with", "from", "this", "that", "all", "new", "add", "use",
}

# ─── 도메인 범위 밖 키워드 (SKIP 대상) ────────────────────
SKIP_KEYWORDS = {
    "로드맵", "마일스톤", "WBS", "일정표", "KPI 대시보드",
    "조직도", "인력 배치", "채용", "온보딩 가이드",
    "마케팅", "영업", "GTM", "go-to-market",
    "비즈니스 모델", "수익 모델", "pricing",
}

# ─── 키워드 추출 ──────────────────────────────────────────
def extract_keywords(feature_name):
    """feature_name에서 검색용 키워드 추출"""
    keywords = set()

    # 괄호 안 내용 분리
    paren_contents = re.findall(r'[（(]([^)）]+)[)）]', feature_name)
    for pc in paren_contents:
        for tok in re.split(r'[/·,+→\s]+', pc):
            tok = tok.strip()
            if len(tok) >= 2 and tok.lower() not in STOPWORDS:
                keywords.add(tok)

    # 괄호 제거 후 메인 텍스트
    main_text = re.sub(r'[（(][^)）]+[)）]', '', feature_name)

    # 영문 단어/약어 추출
    eng_words = re.findall(r'[A-Za-z][A-Za-z0-9_\-\.]{1,}', main_text)
    for w in eng_words:
        if w.lower() not in STOPWORDS and len(w) >= 2:
            keywords.add(w)

    # 한글 단어 추출 (2글자 이상)
    kor_words = re.findall(r'[가-힣]{2,}', main_text)
    for w in kor_words:
        if w not in STOPWORDS and len(w) >= 2:
            keywords.add(w)

    # 특수 패턴: 하이픈 연결 코드명 (AR-L3, EVX-2 등)
    codes = re.findall(r'[A-Z][A-Z0-9]*-[A-Z0-9]+', feature_name)
    keywords.update(codes)

    # 숫자+단위 패턴 (40K, 93K 등) - 제거 (너무 일반적)
    keywords = {k for k in keywords if not re.match(r'^\d+[KkMm]?$', k)}

    return keywords

# ─── PART2 검색 ──────────────────────────────────────────
def search_part2(keyword, text=None):
    """keyword가 PART2에 존재하는지 확인. 매치된 라인 번호 반환."""
    if text is None:
        text = part2_text
    kw_lower = keyword.lower()
    matches = []
    for i, line in enumerate(text.split('\n'), 1):
        if kw_lower in line.lower():
            matches.append(i)
    return matches

def search_in_section(keyword, section_text):
    """특정 섹션에서 검색"""
    kw_lower = keyword.lower()
    return kw_lower in section_text

# ─── 분류 로직 ──────────────────────────────────────────
def classify_item(item):
    """
    확정 기준에 따른 분류:
    1. RESOLVED → 유지
    2. NOT_APPLICABLE (TITLE_ONLY) → 유지
    3. action=SKIP이고 SKIP 키워드 매칭 → SKIP_CONFIRMED
    4. PART2 §2-§5에 명시적 키워드 존재 → SUB_FEATURE_OF_EXISTING
    5. PART2 §6에만 명시적 키워드 존재 → SECTION6_DETAILED
    6. PART2 어디에도 키워드 없음 → REAL_GAP
    """
    result = {
        "feature_id": item["feature_id"],
        "feature_name": item["feature_name"],
        "substatus": None,
        "matched_keywords": [],
        "matched_lines": [],
        "search_keywords": [],
    }

    # Rule 1: RESOLVED 유지
    if item.get("status") == "RESOLVED":
        result["substatus"] = "RESOLVED"
        return result

    # Rule 2: NOT_APPLICABLE 유지 (STEP7 TITLE_ONLY)
    if item.get("suggested_phase", "").startswith("NOT_APPLICABLE"):
        result["substatus"] = "NOT_APPLICABLE"
        return result

    feature_name = item["feature_name"]
    keywords = extract_keywords(feature_name)
    result["search_keywords"] = sorted(keywords)

    # Rule 3: SKIP 체크 - 도메인 범위 밖
    for sk in SKIP_KEYWORDS:
        if sk.lower() in feature_name.lower():
            result["substatus"] = "SKIP_CONFIRMED"
            result["matched_keywords"] = [sk]
            return result

    # feature_id 기반 DUPLICATE 체크
    # D207-108 = AINV-056 (SHAP/LIME) - 하드코딩
    if item["feature_id"] == "D207-108":
        result["substatus"] = "DUPLICATE"
        result["matched_keywords"] = ["AINV-056"]
        return result

    # 키워드가 없으면 (feature_name이 너무 일반적) → REAL_GAP
    if not keywords:
        result["substatus"] = "REAL_GAP"
        return result

    # Rule 4-6: PART2 키워드 매칭
    matched_in_s25 = []
    matched_in_s6 = []
    all_matched_lines = []

    for kw in keywords:
        # §2-§5 검색
        if search_in_section(kw, section2to5_text):
            matched_in_s25.append(kw)
            lines = search_part2(kw)
            all_matched_lines.extend(lines[:3])  # 첫 3개만

        # §6 검색
        if search_in_section(kw, section6_text):
            matched_in_s6.append(kw)
            lines = search_part2(kw)
            all_matched_lines.extend(lines[:3])

    result["matched_lines"] = sorted(set(all_matched_lines))[:5]

    # 매칭 비율 계산
    total_kw = len(keywords)
    matched_s25_count = len(set(matched_in_s25))
    matched_s6_count = len(set(matched_in_s6))
    total_matched = len(set(matched_in_s25 + matched_in_s6))

    # 분류 규칙:
    # - 핵심 키워드(영문 약어, 고유명사) 중 1개라도 §2-§5에 있으면 SUB_FEATURE
    # - §6에만 있으면 SECTION6_DETAILED
    # - 매칭 0건 → REAL_GAP
    # - 매칭은 있지만 일반 한글 단어만 매칭 → 추가 판단 필요

    # 핵심 키워드 = 영문 단어, 코드명, 3글자 이상 고유 한글 단어
    core_keywords = set()
    for kw in keywords:
        if re.match(r'^[A-Za-z]', kw):  # 영문으로 시작
            core_keywords.add(kw)
        elif len(kw) >= 3:  # 한글 3글자 이상
            core_keywords.add(kw)

    core_matched_s25 = [kw for kw in core_keywords if kw in matched_in_s25]
    core_matched_s6 = [kw for kw in core_keywords if kw in matched_in_s6]

    if core_matched_s25:
        result["substatus"] = "SUB_FEATURE_OF_EXISTING"
        result["matched_keywords"] = sorted(set(matched_in_s25))
    elif core_matched_s6:
        result["substatus"] = "SECTION6_DETAILED"
        result["matched_keywords"] = sorted(set(matched_in_s6))
    elif matched_in_s25 or matched_in_s6:
        # 일반 키워드만 매칭 - 2글자 한글 등
        # 이 경우 실질적 커버가 아닐 수 있으므로 WEAK_MATCH로 표시 후
        # feature_name 전체를 다시 검색
        full_name_clean = re.sub(r'[（(][^)）]+[)）]', '', feature_name).strip()
        # 4글자 이상 연속 한글 구문으로 재검색
        long_phrases = re.findall(r'[가-힣]{4,}', full_name_clean)
        phrase_matched = False
        for phrase in long_phrases:
            if phrase.lower() in part2_lower:
                phrase_matched = True
                result["matched_keywords"].append(phrase)

        if phrase_matched:
            result["substatus"] = "SUB_FEATURE_OF_EXISTING"
        else:
            result["substatus"] = "REAL_GAP"
            result["matched_keywords"] = sorted(set(matched_in_s25 + matched_in_s6))
            # WEAK_MATCH 표시: 일반 키워드만 매칭됨
            result["weak_match_note"] = f"Only generic keywords matched: {sorted(set(matched_in_s25 + matched_in_s6))}"
    else:
        result["substatus"] = "REAL_GAP"

    return result

# ─── 전체 분류 실행 ──────────────────────────────────────
print("Classifying all items...")
results = []
for item in items:
    r = classify_item(item)
    results.append(r)

# ─── 통계 집계 ──────────────────────────────────────────
stats = {}
for r in results:
    s = r["substatus"]
    stats[s] = stats.get(s, 0) + 1

print("\n=== DETERMINISTIC CLASSIFICATION RESULT ===")
for k, v in sorted(stats.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")
print(f"  TOTAL: {sum(stats.values())}")

# REAL_GAP 목록 출력
real_gaps = [r for r in results if r["substatus"] == "REAL_GAP"]
print(f"\n=== REAL_GAP Items ({len(real_gaps)}) ===")
for rg in real_gaps:
    kw_info = f" [weak: {rg.get('weak_match_note', '')}]" if rg.get('weak_match_note') else ""
    print(f"  {rg['feature_id']}: {rg['feature_name'][:60]}{kw_info}")

# SKIP_CONFIRMED 목록
skips = [r for r in results if r["substatus"] == "SKIP_CONFIRMED"]
print(f"\n=== SKIP_CONFIRMED Items ({len(skips)}) ===")
for s in skips:
    print(f"  {s['feature_id']}: {s['feature_name'][:60]}")

# 결과 저장
output = {
    "_meta": {
        "method": "deterministic_keyword_matching",
        "criteria": "PART2에 명시적 키워드가 없으면 REAL_GAP (암묵적 커버 불인정)",
        "date": "2026-03-10",
        "part2_version": "v22.0.0",
        "total_items": len(results),
    },
    "statistics": stats,
    "real_gap_count": len(real_gaps),
    "real_gap_ids": [r["feature_id"] for r in real_gaps],
    "items": results,
}

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nResults saved to: {OUTPUT_PATH}")