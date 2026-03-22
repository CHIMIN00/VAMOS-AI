"""
Evidently AI Evaluator for VAMOS
EA 추출 품질 모니터링 + 회귀 탐지
"""

import json
import sys
import argparse
from datetime import datetime

def evaluate_quality(ea_file, baseline_file=None):
    """EA 품질 평가 및 회귀 탐지"""
    from evidently.report import Report
    from evidently.metric_preset import TextEvals
    import pandas as pd

    with open(ea_file, "r", encoding="utf-8") as f:
        ea_data = json.load(f)

    items = ea_data if isinstance(ea_data, list) else ea_data.get("items", [])

    # EA 항목을 DataFrame으로 변환
    rows = []
    for item in items:
        rows.append({
            "item_id": item.get("item_id", item.get("id", "")),
            "key": item.get("key", ""),
            "value": str(item.get("value", "")),
            "source_text": item.get("source_text", ""),
            "confidence": item.get("confidence", 0.0)
        })

    current_df = pd.DataFrame(rows)

    # 기본 통계 리포트
    results = {
        "total_items": len(rows),
        "avg_confidence": round(current_df["confidence"].mean(), 4) if rows else 0,
        "low_confidence_count": int((current_df["confidence"] < 0.7).sum()) if rows else 0,
        "empty_source_count": int((current_df["source_text"] == "").sum()) if rows else 0,
    }

    # 베이스라인 비교 (회귀 탐지)
    if baseline_file:
        with open(baseline_file, "r", encoding="utf-8") as f:
            baseline_data = json.load(f)
        baseline_items = baseline_data if isinstance(baseline_data, list) else baseline_data.get("items", [])
        baseline_rows = [{"confidence": item.get("confidence", 0.0)} for item in baseline_items]
        baseline_df = pd.DataFrame(baseline_rows)

        results["baseline_avg_confidence"] = round(baseline_df["confidence"].mean(), 4)
        results["confidence_delta"] = round(
            results["avg_confidence"] - results["baseline_avg_confidence"], 4
        )
        results["regression"] = results["confidence_delta"] < -0.05

    return results

def main():
    parser = argparse.ArgumentParser(description="Evidently evaluator")
    parser.add_argument("--ea", required=True, help="EA JSON 파일")
    parser.add_argument("--baseline", help="베이스라인 EA JSON (회귀 탐지용)")
    parser.add_argument("--output", required=True, help="출력 JSON")
    args = parser.parse_args()

    results = evaluate_quality(args.ea, args.baseline)
    results["timestamp"] = datetime.now().isoformat()

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"평가 완료: {results['total_items']}항목, 평균 conf={results['avg_confidence']}")
    if "regression" in results:
        status = "⚠ 회귀 감지!" if results["regression"] else "정상"
        print(f"회귀 탐지: {status} (delta={results['confidence_delta']})")

if __name__ == "__main__":
    main()
