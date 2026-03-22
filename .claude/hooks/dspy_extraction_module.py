#!/usr/bin/env python3
"""
dspy_extraction_module.py - DSPy 기반 프롬프트 자동 최적화 (B-39)
Golden Set 기준 BootstrapFewShot/MIPRO/BayesianSignatureOptimizer로 최적 프롬프트 탐색.

Usage:
    python dspy_extraction_module.py <ea_number> --metric <accuracy|coverage> [--output <path>]
    python dspy_extraction_module.py compare [--output <path>]
"""

import json
import sys
import os
from typing import Dict, List, Any

try:
    import dspy
    from dspy import Signature, InputField, OutputField, Module, Predict
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False


# ---------------------------------------------------------------------------
# DSPy Signature & Module for EA Extraction
# ---------------------------------------------------------------------------

if DSPY_AVAILABLE:

    class ExtractFromSOT(Signature):
        """Extract structured data from a Source of Truth (SOT) document."""
        sot_text: str = InputField(desc="Source of Truth document text")
        category: str = InputField(desc="Extraction category (C1-C8)")
        extracted_items: str = OutputField(desc="JSON array of extracted items with key, value, source_text, source_line")

    class EAExtractionModule(Module):
        """DSPy Module for EA extraction optimization."""

        def __init__(self):
            super().__init__()
            self.extractor = Predict(ExtractFromSOT)

        def forward(self, sot_text: str, category: str) -> dict:
            result = self.extractor(sot_text=sot_text, category=category)
            return result


def load_golden_set(ea_number: str) -> List[dict]:
    """Load golden set for evaluation."""
    golden_dir = "D:/VAMOS/04. 구현단계/v13_results/phase0/extraction/golden"
    golden_file = os.path.join(golden_dir, f"golden_EA{ea_number}.json")

    if os.path.exists(golden_file):
        with open(golden_file, "r", encoding="utf-8") as f:
            return json.load(f).get("items", [])

    # Fallback: use current EA as reference
    import glob
    ea_files = glob.glob(f"D:/VAMOS/04. 구현단계/v13_results/phase0/extraction/v13_EA{ea_number}*.json")
    if ea_files:
        with open(ea_files[0], "r", encoding="utf-8") as f:
            return json.load(f).get("items", [])

    return []


def accuracy_metric(example, prediction, trace=None) -> float:
    """Metric: extraction accuracy against golden set."""
    try:
        predicted_items = json.loads(prediction.extracted_items)
        golden_items = example.get("golden_items", [])
        if not golden_items:
            return 0.0

        # Match by key
        golden_keys = {item.get("key") for item in golden_items}
        predicted_keys = {item.get("key") for item in predicted_items}

        if not golden_keys:
            return 0.0

        correct = len(golden_keys & predicted_keys)
        return correct / len(golden_keys)
    except Exception:
        return 0.0


def coverage_metric(example, prediction, trace=None) -> float:
    """Metric: extraction coverage."""
    try:
        predicted_items = json.loads(prediction.extracted_items)
        golden_items = example.get("golden_items", [])
        if not golden_items:
            return 0.0

        return min(1.0, len(predicted_items) / len(golden_items))
    except Exception:
        return 0.0


def optimize(ea_number: str, metric: str = "accuracy", output_path: str = None) -> dict:
    """Run DSPy optimization for an EA extraction task."""
    if not DSPY_AVAILABLE:
        return {
            "dspy_metadata": {
                "target_ea": f"EA-{ea_number}",
                "error": "dspy not installed. Run: pip install dspy",
                "verdict": "ERROR"
            }
        }

    golden_items = load_golden_set(ea_number)
    if not golden_items:
        return {
            "dspy_metadata": {
                "target_ea": f"EA-{ea_number}",
                "error": "No golden set found for evaluation",
                "verdict": "ERROR"
            }
        }

    # Build training examples
    metric_fn = accuracy_metric if metric == "accuracy" else coverage_metric

    # Create module
    module = EAExtractionModule()

    # Attempt optimization with BootstrapFewShot
    try:
        from dspy.teleprompt import BootstrapFewShot

        trainset = []
        for item in golden_items[:10]:
            trainset.append(dspy.Example(
                sot_text=item.get("source_text", ""),
                category=item.get("category", "C1"),
                golden_items=[item]
            ).with_inputs("sot_text", "category"))

        optimizer = BootstrapFewShot(metric=metric_fn, max_bootstrapped_demos=3)
        optimized_module = optimizer.compile(module, trainset=trainset)

        # Evaluate baseline vs optimized
        baseline_scores = []
        optimized_scores = []

        for ex in trainset[:5]:
            try:
                base_pred = module(sot_text=ex.sot_text, category=ex.category)
                base_score = metric_fn(ex, base_pred)
                baseline_scores.append(base_score)
            except Exception:
                baseline_scores.append(0.0)

            try:
                opt_pred = optimized_module(sot_text=ex.sot_text, category=ex.category)
                opt_score = metric_fn(ex, opt_pred)
                optimized_scores.append(opt_score)
            except Exception:
                optimized_scores.append(0.0)

        baseline_avg = sum(baseline_scores) / len(baseline_scores) if baseline_scores else 0
        optimized_avg = sum(optimized_scores) / len(optimized_scores) if optimized_scores else 0

        verdict = "IMPROVED" if optimized_avg > baseline_avg else "NO_IMPROVEMENT"

        result = {
            "dspy_metadata": {
                "target_ea": f"EA-{ea_number}",
                "metric": metric,
                "optimizer": "BootstrapFewShot",
                "iterations": len(trainset),
                "verdict": verdict
            },
            "results": {
                "baseline_score": round(baseline_avg, 4),
                "optimized_score": round(optimized_avg, 4),
                "improvement": round(optimized_avg - baseline_avg, 4),
            }
        }

    except Exception as e:
        result = {
            "dspy_metadata": {
                "target_ea": f"EA-{ea_number}",
                "metric": metric,
                "optimizer": "BootstrapFewShot",
                "error": str(e),
                "verdict": "ERROR"
            }
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
        print("Usage: python dspy_extraction_module.py <ea_number|compare> [--metric accuracy|coverage] [--output <path>]", file=sys.stderr)
        sys.exit(1)

    target = sys.argv[1]
    metric = "accuracy"
    output_path = None

    if "--metric" in sys.argv:
        idx = sys.argv.index("--metric")
        if idx + 1 < len(sys.argv):
            metric = sys.argv[idx + 1]

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    if target == "compare":
        result = {"note": "Run with EA number first, then compare results"}
    else:
        ea_number = target.replace("EA-", "").replace("EA", "").zfill(2)
        result = optimize(ea_number, metric, output_path)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
