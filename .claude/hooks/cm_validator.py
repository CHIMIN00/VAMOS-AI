#!/usr/bin/env python3
"""
VAMOS v13 CM(크로스매칭) 결정론적 검증기 (Layer A)
===================================================
EA 검증기(deterministic_validator.py)와 별도로,
CM-1~CM-8 산출물의 구조적 무결성을 프로그래밍적으로 검증합니다.

사용법:
  python cm_validator.py <CM_JSON_PATH> [--ea-dir <EA_DIR>]

검증 항목:
  CM-DV1: JSON 스키마 무결성 (필수 필드 존재)
  CM-DV2: 메타데이터 카운트 정합성
  CM-DV3: source 참조 유효성 (ea_agent, item_id가 실제 EA에 존재하는지)
  CM-DV4: source_text SOT 원본 대조 (환각 판정 근거가 실제 존재하는지)
  CM-DV5: 판정 일관성 (result/severity 값 유효성)
  CM-DV6: 중복 비교 탐지 (동일 key 쌍 중복 비교)
"""

import json
import sys
import os
import re
import io
import hashlib
from pathlib import Path
from collections import defaultdict

# Windows 인코딩 대응
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ─── 설정 ───
EA_DIR = r"D:\VAMOS\04. 구현단계\v13_results\phase0\extraction"
SOT_DIR = r"D:\VAMOS\docs\sot"
CM_RESULTS_DIR = r"D:\VAMOS\04. 구현단계\v13_results\phase0\cross_match\validation"

REQUIRED_META_FIELDS = ["agent", "category", "version", "total_comparisons", "results", "severity"]
VALID_RESULTS = {"CONSISTENT", "INCONSISTENT", "SOURCE_CONFLICT", "SINGLE_SOURCE"}
VALID_SEVERITIES = {"CRITICAL", "WARNING", "INFO"}
REQUIRED_COMPARISON_FIELDS = ["comparison_id", "key", "result", "severity", "sources"]
REQUIRED_SOURCE_FIELDS = ["ea_agent", "item_id", "source_file", "source_line", "source_text", "value"]


class Finding:
    def __init__(self, rule, item_id, severity, message, expected=None, actual=None):
        self.rule = rule
        self.item_id = item_id
        self.severity = severity
        self.message = message
        self.expected = expected
        self.actual = actual

    def to_dict(self):
        d = {"rule": self.rule, "item_id": self.item_id,
             "severity": self.severity, "message": self.message}
        if self.expected is not None:
            d["expected"] = str(self.expected)
        if self.actual is not None:
            d["actual"] = str(self.actual)
        return d


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_ea_items(ea_dir):
    """EA-1~15의 모든 item_id를 로드하여 {item_id: item} 딕셔너리 반환"""
    all_items = {}
    ea_agents = set()
    if not os.path.isdir(ea_dir):
        return all_items, ea_agents
    for fname in os.listdir(ea_dir):
        if fname.startswith("v13_EA") and fname.endswith(".json"):
            try:
                data = load_json(os.path.join(ea_dir, fname))
                agent = data.get("metadata", {}).get("agent", "")
                ea_agents.add(agent)
                for item in data.get("items", []):
                    iid = item.get("item_id", "")
                    if iid:
                        all_items[iid] = item
            except (json.JSONDecodeError, IOError):
                pass
    return all_items, ea_agents


def load_sot_lines(sot_dir, filename):
    """SOT 파일 줄 단위 로드"""
    candidates = [os.path.join(sot_dir, filename)]
    if not filename.endswith(".md"):
        candidates.append(os.path.join(sot_dir, filename + ".md"))
    if os.path.isdir(sot_dir):
        for f in os.listdir(sot_dir):
            if filename.replace(".md", "") in f:
                candidates.append(os.path.join(sot_dir, f))
    for c in candidates:
        if os.path.exists(c):
            with open(c, "r", encoding="utf-8") as f:
                return f.readlines()
    return None


def cm_dv1_schema(data, findings):
    """CM-DV1: JSON 스키마 무결성"""
    meta = data.get("metadata", {})
    for field in REQUIRED_META_FIELDS:
        if field not in meta:
            findings.append(Finding("CM-DV1", "metadata", "CRITICAL",
                                    f"필수 메타데이터 필드 누락: {field}"))

    comparisons = data.get("comparisons", [])
    if not isinstance(comparisons, list):
        findings.append(Finding("CM-DV1", "comparisons", "CRITICAL",
                                "comparisons가 배열이 아님"))
        return

    for i, comp in enumerate(comparisons):
        cid = comp.get("comparison_id", f"comparisons[{i}]")
        for field in REQUIRED_COMPARISON_FIELDS:
            if field not in comp:
                findings.append(Finding("CM-DV1", cid, "CRITICAL",
                                        f"필수 비교 필드 누락: {field}"))

        sources = comp.get("sources", [])
        if isinstance(sources, list):
            for j, src in enumerate(sources):
                for sf in REQUIRED_SOURCE_FIELDS:
                    if sf not in src:
                        findings.append(Finding("CM-DV1", f"{cid}.sources[{j}]", "WARNING",
                                                f"source 필수 필드 누락: {sf}"))


def cm_dv2_count_integrity(data, findings):
    """CM-DV2: 메타데이터 카운트 정합성"""
    meta = data.get("metadata", {})
    comparisons = data.get("comparisons", [])

    total = meta.get("total_comparisons", -1)
    actual = len(comparisons)
    if total != actual:
        findings.append(Finding("CM-DV2", "metadata", "CRITICAL",
                                f"total_comparisons({total}) != comparisons 배열 길이({actual})",
                                total, actual))

    # results 카운트 검증
    results_meta = meta.get("results", {})
    actual_results = defaultdict(int)
    for comp in comparisons:
        r = comp.get("result", "UNKNOWN")
        actual_results[r] += 1

    for r in VALID_RESULTS:
        declared = results_meta.get(r, 0)
        actual_count = actual_results.get(r, 0)
        if declared != actual_count:
            findings.append(Finding("CM-DV2", f"results.{r}", "WARNING",
                                    f"metadata.results.{r}({declared}) != 실제({actual_count})",
                                    declared, actual_count))

    # severity 카운트 검증
    sev_meta = meta.get("severity", {})
    actual_sev = defaultdict(int)
    for comp in comparisons:
        s = comp.get("severity", "UNKNOWN")
        actual_sev[s] += 1

    for s in VALID_SEVERITIES:
        declared = sev_meta.get(s, 0)
        actual_count = actual_sev.get(s, 0)
        if declared != actual_count:
            findings.append(Finding("CM-DV2", f"severity.{s}", "WARNING",
                                    f"metadata.severity.{s}({declared}) != 실제({actual_count})",
                                    declared, actual_count))


def cm_dv3_source_reference(data, ea_items, ea_agents, findings):
    """CM-DV3: source 참조가 실제 EA에 존재하는지"""
    comparisons = data.get("comparisons", [])

    for comp in comparisons:
        cid = comp.get("comparison_id", "?")
        for j, src in enumerate(comp.get("sources", [])):
            ea_agent = src.get("ea_agent", "")
            item_id = src.get("item_id", "")

            # EA 에이전트 존재 확인
            if ea_agent and ea_agents and ea_agent not in ea_agents:
                findings.append(Finding("CM-DV3", f"{cid}.sources[{j}]", "WARNING",
                                        f"ea_agent '{ea_agent}'가 EA 산출물에 없음"))

            # item_id 존재 확인
            if item_id and ea_items and item_id not in ea_items:
                findings.append(Finding("CM-DV3", f"{cid}.sources[{j}]", "CRITICAL",
                                        f"item_id '{item_id}'가 EA 산출물에 없음 — 환각 참조 의심"))


def cm_dv4_source_text_sot(data, sot_dir, findings):
    """CM-DV4: INCONSISTENT 항목의 source_text가 SOT 원본에 실제 존재하는지"""
    comparisons = data.get("comparisons", [])
    file_cache = {}

    for comp in comparisons:
        if comp.get("result") not in ("INCONSISTENT", "SOURCE_CONFLICT"):
            continue

        cid = comp.get("comparison_id", "?")
        for j, src in enumerate(comp.get("sources", [])):
            sf = src.get("source_file", "")
            st = src.get("source_text", "")
            sl = src.get("source_line", 0)

            if not st or not sf:
                continue

            if sf not in file_cache:
                file_cache[sf] = load_sot_lines(sot_dir, sf)

            lines = file_cache[sf]
            if lines is None:
                continue

            # 키워드 추출 후 파일에서 검색
            keywords = re.findall(r'[\w가-힣]{4,}', st)
            if not keywords:
                keywords = [st[:20].strip()]

            full_text = "".join(lines)
            found = any(kw in full_text for kw in keywords[:5])

            if not found:
                findings.append(Finding(
                    "CM-DV4", f"{cid}.sources[{j}]", "CRITICAL",
                    f"INCONSISTENT 판정 근거 source_text가 SOT에서 발견 안됨 — 환각 판정 의심",
                    f"keywords: {keywords[:3]}", "NOT FOUND"
                ))


def cm_dv5_result_validity(data, findings):
    """CM-DV5: result/severity 값 유효성"""
    comparisons = data.get("comparisons", [])
    for comp in comparisons:
        cid = comp.get("comparison_id", "?")
        r = comp.get("result", "")
        s = comp.get("severity", "")

        if r not in VALID_RESULTS:
            findings.append(Finding("CM-DV5", cid, "WARNING",
                                    f"유효하지 않은 result: '{r}'",
                                    "|".join(VALID_RESULTS), r))
        if s not in VALID_SEVERITIES:
            findings.append(Finding("CM-DV5", cid, "WARNING",
                                    f"유효하지 않은 severity: '{s}'",
                                    "|".join(VALID_SEVERITIES), s))

        # CONSISTENT인데 CRITICAL이면 논리 오류
        if r == "CONSISTENT" and s == "CRITICAL":
            findings.append(Finding("CM-DV5", cid, "CRITICAL",
                                    "CONSISTENT인데 CRITICAL — 논리적 모순"))


def cm_dv6_duplicate_check(data, findings):
    """CM-DV6: 동일 key 쌍 중복 비교 탐지"""
    comparisons = data.get("comparisons", [])
    seen_keys = set()
    for comp in comparisons:
        key = comp.get("key", "")
        sources = comp.get("sources", [])
        source_ids = tuple(sorted(s.get("item_id", "") for s in sources))
        pair = (key, source_ids)

        if pair in seen_keys:
            findings.append(Finding("CM-DV6", comp.get("comparison_id", "?"), "WARNING",
                                    f"중복 비교 탐지: key='{key}', sources={source_ids}"))
        seen_keys.add(pair)


def run_cm_validation(cm_json_path, ea_dir=EA_DIR, sot_dir=SOT_DIR):
    """전체 CM 검증 실행"""
    findings = []

    try:
        data = load_json(cm_json_path)
    except json.JSONDecodeError as e:
        return {
            "validation_metadata": {
                "target_file": os.path.basename(cm_json_path),
                "result": "FAIL",
                "error": f"JSON 파싱 실패: {str(e)}"
            },
            "findings": [],
            "summary": {"CRITICAL": 1, "WARNING": 0, "INFO": 0}
        }

    # EA 데이터 로드 (참조 검증용)
    ea_items, ea_agents = load_ea_items(ea_dir)

    # CM-DV1 ~ CM-DV6 실행
    cm_dv1_schema(data, findings)
    cm_dv2_count_integrity(data, findings)
    cm_dv3_source_reference(data, ea_items, ea_agents, findings)
    cm_dv4_source_text_sot(data, sot_dir, findings)
    cm_dv5_result_validity(data, findings)
    cm_dv6_duplicate_check(data, findings)

    # 집계
    summary = {"CRITICAL": 0, "WARNING": 0, "INFO": 0}
    for f in findings:
        summary[f.severity] = summary.get(f.severity, 0) + 1

    result = "FAIL" if summary["CRITICAL"] > 0 else ("WARN" if summary["WARNING"] > 3 else "PASS")
    comp_count = len(data.get("comparisons", []))

    output = {
        "validation_metadata": {
            "target_file": os.path.basename(cm_json_path),
            "total_comparisons_checked": comp_count,
            "pass_count": comp_count - len(findings),
            "fail_count": len(findings),
            "result": result,
            "validator": "cm_validator.py (Layer A — NO AI judgment)"
        },
        "findings": [f.to_dict() for f in findings],
        "summary": summary,
        "rules_applied": [
            "CM-DV1: JSON 스키마 무결성",
            "CM-DV2: 메타데이터 카운트 정합성",
            "CM-DV3: source 참조 EA 존재 확인",
            "CM-DV4: source_text SOT 원본 대조",
            "CM-DV5: result/severity 유효성",
            "CM-DV6: 중복 비교 탐지"
        ]
    }

    return output


def main():
    if len(sys.argv) < 2:
        print("사용법: python cm_validator.py <CM_JSON_PATH> [--ea-dir <EA_DIR>] [--sot-dir <SOT_DIR>]")
        sys.exit(1)

    cm_path = sys.argv[1]
    ea_dir = EA_DIR
    sot_dir = SOT_DIR

    if "--ea-dir" in sys.argv:
        idx = sys.argv.index("--ea-dir")
        if idx + 1 < len(sys.argv):
            ea_dir = sys.argv[idx + 1]

    if "--sot-dir" in sys.argv:
        idx = sys.argv.index("--sot-dir")
        if idx + 1 < len(sys.argv):
            sot_dir = sys.argv[idx + 1]

    result = run_cm_validation(cm_path, ea_dir, sot_dir)

    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 결과 파일 저장
    os.makedirs(CM_RESULTS_DIR, exist_ok=True)
    basename = os.path.splitext(os.path.basename(cm_path))[0]
    out_path = os.path.join(CM_RESULTS_DIR, f"{basename}_cm_dv_result.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    r = result["validation_metadata"]["result"]
    s = result["summary"]
    print(f"[CM-DV] {r} — CRITICAL:{s['CRITICAL']} WARNING:{s['WARNING']} INFO:{s['INFO']}",
          file=sys.stderr)

    if r == "FAIL":
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()