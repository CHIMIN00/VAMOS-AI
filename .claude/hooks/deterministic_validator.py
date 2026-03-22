#!/usr/bin/env python3
"""
VAMOS v13 결정론적 검증기 (Layer A)
====================================
AI 판단 없이 프로그래밍적으로만 검증합니다.
이 스크립트의 판정은 100% 결정론적입니다 — 동일 입력이면 항상 동일 출력.

사용법:
  python deterministic_validator.py <EA_JSON_PATH> [--sot-dir <SOT_DIR>]

검증 항목:
  DV-1: JSON 스키마 무결성 (필수 필드 존재 여부)
  DV-2: 메타데이터 카운트 정합성 (합계 = items 수)
  DV-3: source_line 범위 확인 (0 < line <= 파일 총 줄 수)
  DV-4: source_text 원본 매칭 (해당 줄에 텍스트가 실제 존재하는가)
  DV-5: item_id 연속성 (건너뛴 번호 없는지)
  DV-6: value_type vs value 실제 타입 일치
  DV-7: COUNT key vs LIST key 길이 교차 검증
  DV-8: 표준 키 목록 대조 (비표준 키 네이밍, 유사 키 오타 탐지)
  DV-9: source_file_hash 변경 감지 (SOT 파일 변경 시 EA 무효화)
  DV-10: 후반부 커버리지 검증 (파일 70% 이후 추출 비율 확인)
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
SOT_DIR = r"D:\VAMOS\docs\sot"
RESULTS_DIR = r"D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\validation"

REQUIRED_METADATA_FIELDS = [
    "agent", "version", "created", "source_files",
    "total_lines_read", "total_items_extracted", "categories"
]

REQUIRED_ITEM_FIELDS = [
    "item_id", "category", "source_file", "source_line",
    "source_text", "key", "value", "value_type"
]

VALID_CATEGORIES = {"C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"}
VALID_VALUE_TYPES = {"number", "string", "list", "boolean"}

# ─── DV-8: 표준 키 목록 (약점 G 대응) ───
STANDARD_KEYS = {
    # 수치/카운트
    "TOTAL_MODULE_COUNT", "CORE_MODULE_COUNT", "COND_MODULE_COUNT",
    "EXP_MODULE_COUNT", "READD_MODULE_COUNT", "IMMUTABLE_ZONE_COUNT",
    "NEVER_AUTO_COUNT", "COND_PRIORITY_CRITICAL", "COND_PRIORITY_HIGH",
    "COND_PRIORITY_MEDIUM", "COND_PRIORITY_LOW", "STAGE_GATE_COUNT",
    "AI_PROMPT_COUNT", "API_ENDPOINT_COUNT",
    # 목록
    "IMMUTABLE_ZONE_LIST", "NEVER_AUTO_LIST", "CORE_MODULE_LIST",
    "COND_MODULE_LIST", "EXP_MODULE_LIST", "READD_MODULE_LIST",
    "GUARDRAILS_LAYER_LIST", "V0_STEP_LIST", "V1_PHASE_LIST",
    # 분류 체계
    "MODULE_TIER_SYSTEM", "MODULE_TIER_COUNT", "GUARDRAILS_LAYER_COUNT",
    # 수식/임계값
    "COST_CEILING_DAILY", "COST_CEILING_MONTHLY", "TIMEOUT_DEFAULT",
}

# 표준 키 접두사 패턴 (LOCK_{대상}, VERSION_SCOPE_{모듈ID})
STANDARD_KEY_PREFIXES = ["LOCK_", "VERSION_SCOPE_"]

# 비표준 키 허용 패턴: {카테고리}_{대상}_{속성} (최소 2개 언더스코어 구분)
NON_STANDARD_KEY_PATTERN = re.compile(r'^[A-Z][A-Z0-9]*(_[A-Z][A-Z0-9]*){1,}$')

# COUNT ↔ LIST 키 매핑 (자동 교차 검증용)
COUNT_LIST_PAIRS = {
    "TOTAL_MODULE_COUNT": "TOTAL_MODULE_LIST",
    "CORE_MODULE_COUNT": "CORE_MODULE_LIST",
    "COND_MODULE_COUNT": "COND_MODULE_LIST",
    "EXP_MODULE_COUNT": "EXP_MODULE_LIST",
    "READD_MODULE_COUNT": "READD_MODULE_LIST",
    "IMMUTABLE_ZONE_COUNT": "IMMUTABLE_ZONE_LIST",
    "NEVER_AUTO_COUNT": "NEVER_AUTO_LIST",
    "STAGE_GATE_COUNT": "STAGE_GATE_LIST",
    "AI_PROMPT_COUNT": "AI_PROMPT_LIST",
    "API_ENDPOINT_COUNT": "API_ENDPOINT_LIST",
    "GUARDRAILS_LAYER_COUNT": "GUARDRAILS_LAYER_LIST",
}


class Finding:
    def __init__(self, rule, item_id, severity, message, expected=None, actual=None):
        self.rule = rule
        self.item_id = item_id
        self.severity = severity
        self.message = message
        self.expected = expected
        self.actual = actual

    def to_dict(self):
        d = {
            "rule": self.rule,
            "item_id": self.item_id,
            "severity": self.severity,
            "message": self.message,
        }
        if self.expected is not None:
            d["expected"] = str(self.expected)
        if self.actual is not None:
            d["actual"] = str(self.actual)
        return d


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_sot_lines(sot_dir, filename):
    """SOT 파일을 줄 단위로 로드. 여러 경로 시도."""
    candidates = [
        os.path.join(sot_dir, filename),
    ]
    # 파일명에 확장자가 없으면 .md 추가
    if not filename.endswith(".md"):
        candidates.append(os.path.join(sot_dir, filename + ".md"))

    # sot 디렉토리에서 파일명 포함하는 파일 검색
    if os.path.isdir(sot_dir):
        for f in os.listdir(sot_dir):
            if filename.replace(".md", "") in f:
                candidates.append(os.path.join(sot_dir, f))

    for candidate in candidates:
        if os.path.exists(candidate):
            with open(candidate, "r", encoding="utf-8") as f:
                return f.readlines()
    return None


def dv1_schema(data, findings):
    """DV-1: JSON 스키마 무결성"""
    # 메타데이터 필드
    meta = data.get("metadata", {})
    for field in REQUIRED_METADATA_FIELDS:
        if field not in meta:
            findings.append(Finding(
                "DV-1", "metadata", "CRITICAL",
                f"필수 메타데이터 필드 누락: {field}"
            ))

    # categories 하위 필드
    cats = meta.get("categories", {})
    for c in ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"]:
        if c not in cats:
            findings.append(Finding(
                "DV-1", "metadata.categories", "WARNING",
                f"카테고리 필드 누락: {c}"
            ))

    # items 배열
    items = data.get("items", [])
    if not isinstance(items, list):
        findings.append(Finding(
            "DV-1", "items", "CRITICAL",
            "items가 배열이 아님", "array", type(items).__name__
        ))
        return

    if len(items) == 0:
        findings.append(Finding(
            "DV-1", "items", "CRITICAL",
            "items 배열이 비어있음"
        ))
        return

    # 각 item 필수 필드
    for i, item in enumerate(items):
        for field in REQUIRED_ITEM_FIELDS:
            if field not in item:
                findings.append(Finding(
                    "DV-1", item.get("item_id", f"items[{i}]"), "CRITICAL",
                    f"필수 항목 필드 누락: {field}"
                ))

        # category 유효성
        cat = item.get("category", "")
        if cat not in VALID_CATEGORIES:
            findings.append(Finding(
                "DV-1", item.get("item_id", f"items[{i}]"), "WARNING",
                f"유효하지 않은 category: {cat}",
                "C1~C8 중 하나", cat
            ))

        # value_type 유효성
        vt = item.get("value_type", "")
        if vt not in VALID_VALUE_TYPES:
            findings.append(Finding(
                "DV-1", item.get("item_id", f"items[{i}]"), "WARNING",
                f"유효하지 않은 value_type: {vt}",
                "number|string|list|boolean", vt
            ))


def dv2_count_integrity(data, findings):
    """DV-2: 메타데이터 카운트 정합성"""
    meta = data.get("metadata", {})
    items = data.get("items", [])
    cats = meta.get("categories", {})

    # total_items_extracted vs items 길이
    total = meta.get("total_items_extracted", -1)
    actual_len = len(items)
    if total != actual_len:
        findings.append(Finding(
            "DV-2", "metadata", "CRITICAL",
            f"total_items_extracted({total}) != items 배열 길이({actual_len})",
            total, actual_len
        ))

    # categories 합계 vs total
    cat_sum = sum(cats.get(c, 0) for c in ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"])
    if cat_sum != total and total != -1:
        findings.append(Finding(
            "DV-2", "metadata.categories", "CRITICAL",
            f"카테고리 합계({cat_sum}) != total_items_extracted({total})",
            total, cat_sum
        ))

    # 실제 카테고리별 카운트
    actual_cats = defaultdict(int)
    for item in items:
        actual_cats[item.get("category", "UNKNOWN")] += 1

    for c in ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"]:
        declared = cats.get(c, 0)
        actual = actual_cats.get(c, 0)
        if declared != actual:
            findings.append(Finding(
                "DV-2", f"category.{c}", "WARNING",
                f"metadata.categories.{c}({declared}) != 실제 {c} 항목 수({actual})",
                declared, actual
            ))


def dv3_source_line_range(data, sot_dir, findings):
    """DV-3: source_line이 파일 줄 수 범위 내인지"""
    items = data.get("items", [])
    file_line_cache = {}

    for item in items:
        sf = item.get("source_file", "")
        sl = item.get("source_line", 0)
        iid = item.get("item_id", "?")

        if sl <= 0:
            findings.append(Finding(
                "DV-3", iid, "CRITICAL",
                f"source_line이 0 이하: {sl}",
                "> 0", sl
            ))
            continue

        # 파일 줄 수 캐시
        if sf not in file_line_cache:
            lines = load_sot_lines(sot_dir, sf)
            file_line_cache[sf] = len(lines) if lines else None

        total_lines = file_line_cache[sf]
        if total_lines is None:
            findings.append(Finding(
                "DV-3", iid, "WARNING",
                f"SOT 파일을 찾을 수 없음: {sf}"
            ))
        elif sl > total_lines:
            findings.append(Finding(
                "DV-3", iid, "CRITICAL",
                f"source_line({sl})이 파일 총 줄 수({total_lines})를 초과",
                f"<= {total_lines}", sl
            ))


def dv4_source_text_match(data, sot_dir, findings):
    """DV-4: source_text가 해당 줄에 실제 존재하는지 (±3줄 허용)"""
    items = data.get("items", [])
    file_cache = {}

    for item in items:
        sf = item.get("source_file", "")
        sl = item.get("source_line", 0)
        st = item.get("source_text", "")
        iid = item.get("item_id", "?")

        if not st or sl <= 0:
            continue

        if sf not in file_cache:
            file_cache[sf] = load_sot_lines(sot_dir, sf)

        lines = file_cache[sf]
        if lines is None:
            continue

        # 핵심 키워드 추출 (15자 이상 연속 문자열)
        # 짧은 source_text는 전체를 키워드로 사용
        keywords = []
        if len(st) <= 30:
            keywords = [st.strip()]
        else:
            # 숫자+단위, 영문 키워드, 한글 키워드 추출
            keywords = re.findall(r'[\w가-힣]{4,}', st)
            if not keywords:
                keywords = [st[:20].strip()]

        # ±3줄 범위에서 키워드 매칭
        start = max(0, sl - 4)  # 0-indexed: sl-1 기준 ±3
        end = min(len(lines), sl + 3)
        window = "".join(lines[start:end])

        matched = False
        for kw in keywords:
            if kw in window:
                matched = True
                break

        if not matched:
            # ±10줄로 확장
            start_wide = max(0, sl - 11)
            end_wide = min(len(lines), sl + 10)
            window_wide = "".join(lines[start_wide:end_wide])

            for kw in keywords:
                if kw in window_wide:
                    findings.append(Finding(
                        "DV-4", iid, "INFO",
                        f"source_text 키워드가 ±3줄이 아닌 ±10줄에서 발견 (행 번호 오차 가능)",
                        f"line {sl} ±3", f"found in ±10"
                    ))
                    matched = True
                    break

        if not matched:
            # 전체 파일에서 검색
            full_text = "".join(lines)
            found_anywhere = False
            for kw in keywords:
                if kw in full_text:
                    found_anywhere = True
                    break

            if found_anywhere:
                findings.append(Finding(
                    "DV-4", iid, "WARNING",
                    f"source_text 키워드가 line {sl} 근처가 아닌 파일 다른 위치에서 발견",
                    f"near line {sl}", "found elsewhere"
                ))
            else:
                findings.append(Finding(
                    "DV-4", iid, "CRITICAL",
                    f"source_text 키워드가 파일 전체에서 발견되지 않음 — 환각 의심",
                    f"keywords: {keywords[:3]}", "NOT FOUND"
                ))


def dv5_item_id_continuity(data, findings):
    """DV-5: item_id 연속성"""
    items = data.get("items", [])
    ids = []
    for item in items:
        iid = item.get("item_id", "")
        match = re.match(r'EA-(\d+)_(\d+)', iid)
        if match:
            ids.append((int(match.group(1)), int(match.group(2))))

    if not ids:
        return

    # 에이전트별 그룹핑
    by_agent = defaultdict(list)
    for agent_num, seq in ids:
        by_agent[agent_num].append(seq)

    for agent_num, seqs in by_agent.items():
        seqs_sorted = sorted(seqs)
        if seqs_sorted[0] != 1:
            findings.append(Finding(
                "DV-5", f"EA-{agent_num:02d}", "WARNING",
                f"시작 번호가 1이 아님: {seqs_sorted[0]}"
            ))

        for i in range(1, len(seqs_sorted)):
            if seqs_sorted[i] != seqs_sorted[i-1] + 1:
                gap_start = seqs_sorted[i-1] + 1
                gap_end = seqs_sorted[i] - 1
                findings.append(Finding(
                    "DV-5", f"EA-{agent_num:02d}", "INFO",
                    f"번호 건너뜀: {gap_start}~{gap_end}"
                ))


def dv6_value_type_match(data, findings):
    """DV-6: value_type vs 실제 value 타입 일치"""
    items = data.get("items", [])
    for item in items:
        vt = item.get("value_type", "")
        val = item.get("value")
        iid = item.get("item_id", "?")

        if val is None:
            continue  # null은 모든 타입에 허용 (명시되지 않음)

        actual_type = type(val).__name__
        mismatch = False

        if vt == "number" and not isinstance(val, (int, float)):
            mismatch = True
        elif vt == "string" and not isinstance(val, str):
            mismatch = True
        elif vt == "list" and not isinstance(val, list):
            mismatch = True
        elif vt == "boolean" and not isinstance(val, bool):
            mismatch = True

        if mismatch:
            findings.append(Finding(
                "DV-6", iid, "WARNING",
                f"value_type '{vt}' vs 실제 타입 '{actual_type}' 불일치",
                vt, actual_type
            ))


def dv7_count_list_cross(data, findings):
    """DV-7: COUNT key와 LIST key 길이 교차 검증"""
    items = data.get("items", [])
    key_values = {}
    for item in items:
        key = item.get("key", "")
        val = item.get("value")
        if key:
            key_values[key] = val

    for count_key, list_key in COUNT_LIST_PAIRS.items():
        if count_key in key_values and list_key in key_values:
            count_val = key_values[count_key]
            list_val = key_values[list_key]

            if isinstance(count_val, (int, float)) and isinstance(list_val, list):
                if int(count_val) != len(list_val):
                    findings.append(Finding(
                        "DV-7", f"{count_key}↔{list_key}", "CRITICAL",
                        f"{count_key}={int(count_val)} but {list_key} 길이={len(list_val)}",
                        int(count_val), len(list_val)
                    ))


def dv8_standard_key_check(data, findings):
    """DV-8: 표준 키 목록 대조 — 비표준 키 사용 시 WARNING, 유사 키 존재 시 CRITICAL"""
    items = data.get("items", [])

    for item in items:
        key = item.get("key", "")
        iid = item.get("item_id", "?")
        if not key:
            findings.append(Finding(
                "DV-8", iid, "WARNING",
                "key가 비어있음"
            ))
            continue

        # 표준 키 또는 표준 접두사 매칭이면 OK
        if key in STANDARD_KEYS:
            continue
        if any(key.startswith(prefix) for prefix in STANDARD_KEY_PREFIXES):
            continue

        # 비표준 키: 네이밍 컨벤션 확인
        if not NON_STANDARD_KEY_PATTERN.match(key):
            findings.append(Finding(
                "DV-8", iid, "WARNING",
                f"비표준 키 '{key}'가 네이밍 규칙 미준수 (UPPER_SNAKE_CASE 필요)",
                "CATEGORY_TARGET_ATTRIBUTE", key
            ))

        # 유사 표준 키 탐지 (오타/키 통일 실패)
        for std_key in STANDARD_KEYS:
            common = set(key.split("_")) & set(std_key.split("_"))
            parts_count = max(len(key.split("_")), len(std_key.split("_")))
            if parts_count > 0 and len(common) / parts_count >= 0.6 and key != std_key:
                findings.append(Finding(
                    "DV-8", iid, "CRITICAL",
                    f"비표준 키 '{key}'가 표준 키 '{std_key}'와 유사 — 오타 또는 키 통일 필요",
                    std_key, key
                ))
                break

    # 동일 EA 내 동일 key + 다른 value 탐지
    key_values = defaultdict(list)
    for item in items:
        k = item.get("key", "")
        v = item.get("value")
        if k:
            key_values[k].append((v, item.get("item_id", "?")))

    for k, entries in key_values.items():
        if len(entries) > 1:
            values = [str(e[0]) for e in entries]
            if len(set(values)) > 1:
                ids = [e[1] for e in entries]
                findings.append(Finding(
                    "DV-8", f"{ids[0]}~{ids[-1]}", "WARNING",
                    f"동일 키 '{k}'가 {len(entries)}회 등장하며 값이 다름",
                    "unique value per key", f"{len(set(values))} distinct values"
                ))


def dv9_source_file_hash(data, sot_dir, findings):
    """DV-9: source_file_hash 검증 — EA 생성 시점과 현재 SOT 파일 동일성 확인"""
    meta = data.get("metadata", {})
    file_hashes = meta.get("source_file_hashes", {})

    if not file_hashes:
        findings.append(Finding(
            "DV-9", "metadata", "INFO",
            "source_file_hashes 필드 없음 — SOT 변경 감지 불가. "
            "EA 재생성 시 metadata.source_file_hashes 포함 권장."
        ))
        return

    for filename, expected_hash in file_hashes.items():
        lines = load_sot_lines(sot_dir, filename)
        if lines is None:
            findings.append(Finding(
                "DV-9", f"hash:{filename}", "WARNING",
                f"SOT 파일을 찾을 수 없어 해시 비교 불가: {filename}"
            ))
            continue

        content = "".join(lines)
        current_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        if current_hash != expected_hash:
            findings.append(Finding(
                "DV-9", f"hash:{filename}", "CRITICAL",
                f"SOT 파일 '{filename}'이 EA 생성 이후 변경됨 — "
                f"source_line/source_text 무효화 가능. EA 재추출 필요.",
                expected_hash[:16] + "...", current_hash[:16] + "..."
            ))


def dv10_rear_coverage(data, sot_dir, findings):
    """DV-10: 후반부 커버리지 검증 — 파일 70% 이후 구간에서 추출된 항목 비율 확인"""
    items = data.get("items", [])
    if not items:
        return

    # 파일별 총 줄 수 캐시
    file_line_cache = {}
    for item in items:
        sf = item.get("source_file", "")
        if sf and sf not in file_line_cache:
            lines = load_sot_lines(sot_dir, sf)
            file_line_cache[sf] = len(lines) if lines else None

    # 파일별 후반부 커버리지 계산
    for sf, total_lines in file_line_cache.items():
        if total_lines is None or total_lines < 100:
            continue  # 짧은 파일은 검사 불필요

        threshold_line = int(total_lines * 0.7)
        file_items = [i for i in items if i.get("source_file", "") == sf]
        rear_items = [i for i in file_items if i.get("source_line", 0) > threshold_line]

        if len(file_items) == 0:
            continue

        rear_ratio = len(rear_items) / len(file_items)

        if rear_ratio < 0.1 and total_lines > 500:
            findings.append(Finding(
                "DV-10", f"coverage:{sf}", "CRITICAL",
                f"파일 '{sf}'({total_lines}줄)의 후반부(70% 이후) 추출 항목이 "
                f"{len(rear_items)}/{len(file_items)}건 ({rear_ratio:.0%}) — "
                f"후반부 누락 강력 의심. 파일 뒷부분 재읽기 필요.",
                ">= 10%", f"{rear_ratio:.0%}"
            ))
        elif rear_ratio < 0.2 and total_lines > 500:
            findings.append(Finding(
                "DV-10", f"coverage:{sf}", "WARNING",
                f"파일 '{sf}'({total_lines}줄)의 후반부 추출 비율이 낮음: "
                f"{len(rear_items)}/{len(file_items)}건 ({rear_ratio:.0%})",
                ">= 20%", f"{rear_ratio:.0%}"
            ))


def run_validation(ea_json_path, sot_dir=SOT_DIR):
    """전체 검증 실행"""
    findings = []

    # JSON 로드
    try:
        data = load_json(ea_json_path)
    except json.JSONDecodeError as e:
        return {
            "validation_metadata": {
                "target_file": os.path.basename(ea_json_path),
                "result": "FAIL",
                "error": f"JSON 파싱 실패: {str(e)}"
            },
            "findings": [],
            "summary": {"CRITICAL": 1, "WARNING": 0, "INFO": 0}
        }

    # DV-1 ~ DV-9 실행
    dv1_schema(data, findings)
    dv2_count_integrity(data, findings)
    dv3_source_line_range(data, sot_dir, findings)
    dv4_source_text_match(data, sot_dir, findings)
    dv5_item_id_continuity(data, findings)
    dv6_value_type_match(data, findings)
    dv7_count_list_cross(data, findings)
    dv8_standard_key_check(data, findings)
    dv9_source_file_hash(data, sot_dir, findings)
    dv10_rear_coverage(data, sot_dir, findings)

    # 집계
    summary = {"CRITICAL": 0, "WARNING": 0, "INFO": 0}
    for f in findings:
        summary[f.severity] = summary.get(f.severity, 0) + 1

    # 판정
    if summary["CRITICAL"] > 0:
        result = "FAIL"
    elif summary["WARNING"] > 3:
        result = "WARN"
    else:
        result = "PASS"

    items_count = len(data.get("items", []))

    output = {
        "validation_metadata": {
            "target_file": os.path.basename(ea_json_path),
            "total_items_checked": items_count,
            "pass_count": items_count - len(findings),
            "fail_count": len(findings),
            "result": result,
            "validator": "deterministic_validator.py (Layer A — NO AI judgment)"
        },
        "findings": [f.to_dict() for f in findings],
        "summary": summary,
        "rules_applied": [
            "DV-1: JSON 스키마 무결성",
            "DV-2: 메타데이터 카운트 정합성",
            "DV-3: source_line 범위 확인",
            "DV-4: source_text 원본 매칭",
            "DV-5: item_id 연속성",
            "DV-6: value_type vs value 타입 일치",
            "DV-7: COUNT↔LIST 교차 검증",
            "DV-8: 표준 키 목록 대조 (약점 G 대응)",
            "DV-9: source_file_hash 변경 감지 (약점 I 대응)",
            "DV-10: 후반부 커버리지 검증 (약점 E 대응)"
        ]
    }

    return output


def main():
    if len(sys.argv) < 2:
        print("사용법: python deterministic_validator.py <EA_JSON_PATH> [--sot-dir <SOT_DIR>]")
        sys.exit(1)

    ea_path = sys.argv[1]
    sot_dir = SOT_DIR

    if "--sot-dir" in sys.argv:
        idx = sys.argv.index("--sot-dir")
        if idx + 1 < len(sys.argv):
            sot_dir = sys.argv[idx + 1]

    result = run_validation(ea_path, sot_dir)

    # 결과 출력 (stdout → JSON)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 결과 파일 저장
    os.makedirs(RESULTS_DIR, exist_ok=True)
    basename = os.path.splitext(os.path.basename(ea_path))[0]
    out_path = os.path.join(RESULTS_DIR, f"{basename}_dv_result.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # 판정 결과를 stderr로 출력 (hook용)
    r = result["validation_metadata"]["result"]
    s = result["summary"]
    print(
        f"[DV] {r} — CRITICAL:{s['CRITICAL']} WARNING:{s['WARNING']} INFO:{s['INFO']}",
        file=sys.stderr
    )

    # exit code: FAIL이면 2 (hook에서 차단용)
    if r == "FAIL":
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
