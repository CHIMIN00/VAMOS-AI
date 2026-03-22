#!/usr/bin/env python3
"""
VAMOS v12 Task 0-I-C: Extract ALL numeric values from PART2 implementation guide.
Categories: LOCK/FREEZE, quantities, costs, percentages, time, sizes.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

SOURCE = Path(r"D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md")
OUTPUT = Path(r"D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_numeric_registry.json")

def truncate_context(line_text, max_len=80):
    t = line_text.strip()
    if len(t) <= max_len:
        return t
    return t[:max_len] + "..."

def extract_numerics(filepath):
    text = filepath.read_text(encoding="utf-8")
    lines = text.split("\n")

    entries = []
    seen = set()  # (line_no, raw_text, type) dedup

    # ---- Pattern definitions ----

    # LOCK/FREEZE patterns: lines containing LOCK/FREEZE/고정/불변 with numeric values
    lock_freeze_keywords = re.compile(r'(LOCK|FREEZE|고정|불변)', re.IGNORECASE)

    # Numeric patterns by category
    patterns = {
        # Percentages: 99.9%, 100%, 0.1% etc.
        "percentage": [
            (re.compile(r'(\d+(?:\.\d+)?)\s*(%|퍼센트)'), None),
        ],
        # Costs: ₩ values, 원, 만원, 억원
        "cost": [
            (re.compile(r'₩\s*([\d,]+(?:\.\d+)?)'), "₩"),
            (re.compile(r'([\d,]+(?:\.\d+)?)\s*(원|만원|억원|천원|백만원)'), None),
        ],
        # Time: ms, s, sec, 초, 분, 시간, hour, min, day, 일, 주, 개월, 년
        "time": [
            (re.compile(r'(\d+(?:\.\d+)?)\s*(ms|밀리초)(?![A-Za-z])'), None),
            (re.compile(r'(\d+(?:\.\d+)?)\s*(초|sec|seconds?)(?![A-Za-z])'), None),
            (re.compile(r'(\d+(?:\.\d+)?)\s*s(?![a-zA-Z가-힣])'), "s"),
            (re.compile(r'(\d+(?:\.\d+)?)\s*(분|min|minutes?)(?![A-Za-z])'), None),
            (re.compile(r'(\d+(?:\.\d+)?)\s*(시간|hour|hours?|h)(?![a-zA-Z])'), None),
            (re.compile(r'(\d+(?:\.\d+)?)\s*(일|days?|d)(?![a-zA-Z])'), None),
            (re.compile(r'(\d+(?:\.\d+)?)\s*(주|weeks?|w)(?![a-zA-Z])'), None),
            (re.compile(r'(\d+(?:\.\d+)?)\s*(개월|months?)(?![A-Za-z])'), None),
            (re.compile(r'(\d+(?:\.\d+)?)\s*(년|years?)(?![A-Za-z])'), None),
        ],
        # Sizes: KB, MB, GB, TB (not standalone B which causes false positives)
        "size": [
            (re.compile(r'(\d+(?:\.\d+)?)\s*(TB|GB|MB|KB|tb|gb|mb|kb)(?![a-zA-Z])'), None),
        ],
        # Quantities: N개, N건, N줄, N개월 is time, N명, N회, N단계, N레벨, N종, N개 etc.
        "quantity": [
            (re.compile(r'(\d+(?:,\d+)*)\s*(개|건|줄|명|회|단계|레벨|종|벌|항목|모듈|파일|테이블|컬럼|필드|문서|페이지|요소|리소스|노드|서버|인스턴스|토큰|글자|자|바이트|비트|포트|엔드포인트|API|이벤트|타입|카테고리|세트|쌍|쿼리|요청|응답|시도|횟수|가지|곳|군데|점|부|편|장|매|권|케이스|테스트|시나리오|룰|규칙|조건|액션|워크플로우|채널|슬롯|큐|쓰레드|프로세스|커넥션|세션|클래스|메서드|함수|패키지)(?![가-힣])'), None),
        ],
    }

    # Generic number-with-unit for LOCK/FREEZE lines
    generic_num = re.compile(r'(\d+(?:[.,]\d+)*)\s*([A-Za-z가-힣%₩]+)?')

    for line_no, line in enumerate(lines, 1):
        ctx = truncate_context(line)

        # Check LOCK/FREEZE lines
        is_lock_freeze = bool(lock_freeze_keywords.search(line))

        if is_lock_freeze:
            # Determine type
            upper_line = line.upper()
            if "LOCK" in upper_line or "불변" in line:
                lf_type = "LOCK"
            else:
                lf_type = "FREEZE"

            # Find all numbers on this line
            for m in re.finditer(r'(\d+(?:[.,]\d+)*)', line):
                raw = m.group(0)
                # Skip things that look like version numbers in certain contexts
                # but include all numeric values
                val_str = raw.replace(",", "")
                try:
                    val = float(val_str) if "." in val_str else int(val_str)
                except ValueError:
                    continue

                # Get surrounding unit if any
                after = line[m.end():m.end()+15]
                unit_m = re.match(r'\s*(%|ms|s|초|분|시간|MB|GB|KB|TB|개|건|줄|명|회|원|만원|억원|천원)', after)
                unit = unit_m.group(1) if unit_m else ""

                raw_text = raw + (unit_m.group(0).strip() if unit_m else "")
                key = (line_no, raw_text, lf_type)
                if key not in seen:
                    seen.add(key)
                    entries.append({
                        "line": line_no,
                        "type": lf_type,
                        "value": val,
                        "unit": unit,
                        "context": ctx,
                        "raw_text": raw_text
                    })

        # Now extract by category patterns (always, even on LOCK/FREEZE lines)
        for cat, pat_list in patterns.items():
            for pat, forced_unit in pat_list:
                for m in pat.finditer(line):
                    if forced_unit:
                        # Pattern has group(1) as value
                        val_str = m.group(1).replace(",", "")
                        unit = forced_unit
                        raw_text = m.group(0)
                    else:
                        val_str = m.group(1).replace(",", "")
                        unit = m.group(2) if m.lastindex >= 2 else ""
                        raw_text = m.group(0)

                    try:
                        val = float(val_str) if "." in val_str else int(val_str)
                    except ValueError:
                        continue

                    key = (line_no, raw_text, cat)
                    if key not in seen:
                        seen.add(key)
                        entries.append({
                            "line": line_no,
                            "type": cat,
                            "value": val,
                            "unit": unit,
                            "context": ctx,
                            "raw_text": raw_text
                        })

    # Sort by line number, then type
    type_order = {"LOCK": 0, "FREEZE": 1, "quantity": 2, "cost": 3, "percentage": 4, "time": 5, "size": 6}
    entries.sort(key=lambda e: (e["line"], type_order.get(e["type"], 99)))

    # Build metadata
    by_type = defaultdict(int)
    for e in entries:
        by_type[e["type"]] += 1

    result = {
        "metadata": {
            "task": "0-I-C",
            "source": "VAMOS_구현가이드_PART2_구현단계.md",
            "created": "2026-03-15",
            "total_entries": len(entries),
            "by_type": {
                "LOCK": by_type.get("LOCK", 0),
                "FREEZE": by_type.get("FREEZE", 0),
                "quantity": by_type.get("quantity", 0),
                "cost": by_type.get("cost", 0),
                "percentage": by_type.get("percentage", 0),
                "time": by_type.get("time", 0),
                "size": by_type.get("size", 0),
            }
        },
        "entries": entries
    }

    return result

if __name__ == "__main__":
    result = extract_numerics(SOURCE)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Total entries: {result['metadata']['total_entries']}")
    print(f"By type: {json.dumps(result['metadata']['by_type'], indent=2)}")
    print(f"Output: {OUTPUT}")
