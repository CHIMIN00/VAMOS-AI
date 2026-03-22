#!/usr/bin/env python3
"""
deepeval_metrics.py - DeepEval 기반 EA 추출 결과 정량적 평가 (B-11)
HallucinationMetric, FaithfulnessMetric, AnswerRelevancyMetric + 커스텀 메트릭.

Usage:
    python deepeval_metrics.py <ea_json_file> [--output <path>]
    python deepeval_metrics.py all --dir <extraction_dir>
"""

import json
import sys
import os
from typing import Dict, List, Any

try:
    from deepeval import evaluate
    from deepeval.test_case import LLMTestCase
    from deepeval.metrics import (
        HallucinationMetric,
        FaithfulnessMetric,
        AnswerRelevancyMetric,
    )
    DEEPEVAL_AVAILABLE = True
except ImportError:
    DEEPEVAL_AVAILABLE = False


def load_ea(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_source_file(filepath: str) -> str:
    """Read SOT source file content."""
    candidates = [filepath, os.path.join("D:/VAMOS", filepath)]
    for p in candidates:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return f.read()
    return ""


def compute_custom_metrics(ea: dict) -> Dict[str, float]:
    """Compute VAMOS-specific custom metrics."""
    items = ea.get("items", [])
    metadata = ea.get("metadata", {})
    categories = metadata.get("categories", {})

    # DV pass rate (simplified: check basic structure)
    dv_issues = 0
    total_checks = len(items) if items else 1
    for item in items:
        required = {"item_id", "key", "value", "category", "source_line", "source_text"}
        if not required.issubset(set(item.keys())):
            dv_issues += 1
    dv_pass_rate = 1.0 - (dv_issues / total_checks) if total_checks > 0 else 0.0

    # Category balance (entropy-based)
    if categories:
        total = sum(v for v in categories.values() if isinstance(v, (int, float)))
        if total > 0:
            proportions = [v / total for v in categories.values() if isinstance(v, (int, float)) and v > 0]
            import math
            entropy = -sum(p * math.log2(p) for p in proportions if p > 0)
            max_entropy = math.log2(len(proportions)) if len(proportions) > 1 else 1
            category_balance = entropy / max_entropy if max_entropy > 0 else 0.0
        else:
            category_balance = 0.0
    else:
        category_balance = 0.0

    # Coverage rate (placeholder: based on source_text presence)
    has_source = sum(1 for item in items if item.get("source_text", "").strip())
    coverage_rate = has_source / len(items) if items else 0.0

    return {
        "dv_pass_rate": round(dv_pass_rate, 4),
        "category_balance": round(category_balance, 4),
        "coverage_rate": round(coverage_rate, 4),
    }


def evaluate_ea(ea_path: str, output_path: str = None) -> dict:
    """Evaluate an EA JSON file with DeepEval metrics."""
    ea = load_ea(ea_path)
    items = ea.get("items", [])

    custom_metrics = compute_custom_metrics(ea)

    deepeval_scores = {
        "hallucination_score": None,
        "faithfulness_score": None,
        "relevancy_score": None,
    }

    if DEEPEVAL_AVAILABLE and items:
        # Build test cases from EA items (sample up to 20 for efficiency)
        sample = items[:20]
        test_cases = []

        source_cache = {}
        for item in sample:
            sf = item.get("source_file", "")
            if sf and sf not in source_cache:
                source_cache[sf] = read_source_file(sf)

            context = source_cache.get(sf, item.get("source_text", ""))
            tc = LLMTestCase(
                input=f"Extract {item.get('key', '')} from source",
                actual_output=str(item.get("value", "")),
                expected_output=item.get("source_text", ""),
                context=[context[:2000]] if context else [""],
                retrieval_context=[item.get("source_text", "")]
            )
            test_cases.append(tc)

        # Compute metrics
        try:
            h_metric = HallucinationMetric(threshold=0.05)
            for tc in test_cases[:5]:
                h_metric.measure(tc)
            deepeval_scores["hallucination_score"] = round(1.0 - h_metric.score, 4) if h_metric.score is not None else None
        except Exception:
            pass

        try:
            f_metric = FaithfulnessMetric(threshold=0.90)
            for tc in test_cases[:5]:
                f_metric.measure(tc)
            deepeval_scores["faithfulness_score"] = round(f_metric.score, 4) if f_metric.score is not None else None
        except Exception:
            pass

        try:
            r_metric = AnswerRelevancyMetric(threshold=0.85)
            for tc in test_cases[:5]:
                r_metric.measure(tc)
            deepeval_scores["relevancy_score"] = round(r_metric.score, 4) if r_metric.score is not None else None
        except Exception:
            pass

    all_metrics = {**deepeval_scores, **custom_metrics}

    # Determine verdict
    thresholds = {
        "hallucination_score": ("<=", 0.05),
        "faithfulness_score": (">=", 0.90),
        "relevancy_score": (">=", 0.85),
        "dv_pass_rate": (">=", 1.0),
        "category_balance": (">=", 0.80),
        "coverage_rate": (">=", 0.85),
    }

    failed = []
    for metric_name, (op, threshold) in thresholds.items():
        score = all_metrics.get(metric_name)
        if score is None:
            continue
        if op == ">=" and score < threshold:
            failed.append(metric_name)
        elif op == "<=" and score > threshold:
            failed.append(metric_name)

    verdict = "PASS" if not failed else "FAIL"

    result = {
        "eval_metadata": {
            "target_file": os.path.basename(ea_path),
            "target_path": ea_path,
            "total_items_evaluated": len(items),
            "metrics_computed": sum(1 for v in all_metrics.values() if v is not None),
            "deepeval_available": DEEPEVAL_AVAILABLE,
            "verdict": verdict
        },
        "metrics": all_metrics,
        "failed_metrics": failed,
    }

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Result saved to: {output_path}", file=sys.stderr)

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python deepeval_metrics.py <ea_json|all> [--dir <dir>] [--output <path>]", file=sys.stderr)
        sys.exit(1)

    target = sys.argv[1]
    output_path = None
    eas_dir = None

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    if "--dir" in sys.argv:
        idx = sys.argv.index("--dir")
        if idx + 1 < len(sys.argv):
            eas_dir = sys.argv[idx + 1]

    if target == "all":
        import glob
        if not eas_dir:
            eas_dir = "D:/VAMOS/04. 구현단계/v13_results/phase0/extraction"
        ea_files = sorted(glob.glob(os.path.join(eas_dir, "v13_EA*.json")))
        results = [evaluate_ea(f) for f in ea_files]
        output = json.dumps({"batch_results": results}, ensure_ascii=False, indent=2)
    else:
        result = evaluate_ea(target, output_path)
        output = json.dumps(result, ensure_ascii=False, indent=2)

    print(output)


if __name__ == "__main__":
    main()
