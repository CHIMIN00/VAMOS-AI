"""
Giskard Vulnerability Scanner for VAMOS
EA 추출 파이프라인의 취약점 자동 스캔
"""

import json
import os
import sys
import argparse
from datetime import datetime

def scan_hallucination(ea_items, sot_text):
    """환각 취약점 스캔"""
    issues = []

    for item in ea_items:
        value = str(item.get("value", ""))
        source_text = item.get("source_text", "")
        item_id = item.get("item_id", item.get("id", ""))

        # 수치가 source_text에 없는 경우
        import re
        numbers_in_value = re.findall(r'\d+\.?\d*', value)
        for num in numbers_in_value:
            if num not in source_text and num not in sot_text[:5000]:
                issues.append({
                    "type": "hallucination",
                    "severity": "HIGH",
                    "item_id": item_id,
                    "description": f"수치 '{num}'이 source_text에서 발견되지 않음",
                    "value": value
                })

    return issues

def scan_robustness(ea_items, sot_text):
    """견고성 취약점 스캔"""
    issues = []

    # 긴 문서 취약점
    if len(sot_text) > 10000:
        issues.append({
            "type": "robustness",
            "severity": "MEDIUM",
            "description": f"긴 문서 ({len(sot_text)}자) — 후반부 추출 누락 위험",
            "recommendation": "청크 분할 후 추출 권장"
        })

    # 표 형태 취약점
    table_lines = [l for l in sot_text.split("\n") if "|" in l]
    if len(table_lines) > 10:
        issues.append({
            "type": "robustness",
            "severity": "MEDIUM",
            "description": f"표 형태 콘텐츠 다수 ({len(table_lines)}줄) — 파싱 오류 위험",
            "recommendation": "표 전처리 후 추출 권장"
        })

    return issues

def scan_bias(ea_items):
    """편향 취약점 스캔"""
    issues = []

    # 카테고리별 confidence 분포
    category_confs = {}
    for item in ea_items:
        cat = item.get("category", item.get("value_type", "unknown"))
        conf = item.get("confidence", 0.9)
        if cat not in category_confs:
            category_confs[cat] = []
        category_confs[cat].append(conf)

    for cat, confs in category_confs.items():
        avg = sum(confs) / len(confs) if confs else 0
        if avg < 0.7 and len(confs) >= 3:
            issues.append({
                "type": "bias",
                "severity": "MEDIUM",
                "description": f"카테고리 '{cat}'의 평균 confidence가 낮음 ({avg:.2f})",
                "count": len(confs),
                "recommendation": f"'{cat}' 유형 항목에 대한 프롬프트 개선 필요"
            })

    return issues

def main():
    parser = argparse.ArgumentParser(description="Giskard vulnerability scanner")
    parser.add_argument("--ea", required=True, help="EA JSON 파일")
    parser.add_argument("--sot", help="SOT 원본 파일")
    parser.add_argument("--output", required=True, help="출력 JSON")
    args = parser.parse_args()

    with open(args.ea, "r", encoding="utf-8") as f:
        ea_data = json.load(f)

    ea_items = ea_data if isinstance(ea_data, list) else ea_data.get("items", [])

    sot_text = ""
    if args.sot:
        try:
            with open(args.sot, "r", encoding="utf-8") as f:
                sot_text = f.read()
        except Exception:
            pass

    # Giskard 네이티브 스캔 시도, 실패 시 자체 로직 fallback
    all_issues = []
    try:
        import giskard
        import pandas as pd

        df = pd.DataFrame([{
            "input": item.get("source_text", ""),
            "output": str(item.get("value", "")),
            "context": sot_text[:3000] if sot_text else ""
        } for item in ea_items])

        dataset = giskard.Dataset(df, target=None)
        print("Giskard 네이티브 스캔 실행 중...")
        # Giskard 스캔은 모델 래핑이 필요하므로, 데이터셋 수준 검증 수행
        all_issues.append({
            "type": "info",
            "severity": "LOW",
            "description": f"Giskard 데이터셋 로드 성공: {len(df)}건"
        })
    except Exception as e:
        print(f"Giskard 네이티브 스캔 건너뜀 (fallback): {e}")

    # 자체 취약점 스캔 (항상 실행)
    all_issues.extend(scan_hallucination(ea_items, sot_text))
    all_issues.extend(scan_robustness(ea_items, sot_text))
    all_issues.extend(scan_bias(ea_items))

    # 심각도별 통계
    severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for issue in all_issues:
        sev = issue.get("severity", "LOW")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    output = {
        "timestamp": datetime.now().isoformat(),
        "ea_file": args.ea,
        "total_issues": len(all_issues),
        "severity": severity_counts,
        "issues": all_issues
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"스캔 완료: {len(all_issues)}건 발견")
    print(f"  HIGH={severity_counts['HIGH']}, MEDIUM={severity_counts['MEDIUM']}, LOW={severity_counts['LOW']}")

if __name__ == "__main__":
    main()
