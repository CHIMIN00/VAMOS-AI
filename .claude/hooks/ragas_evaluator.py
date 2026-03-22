#!/usr/bin/env python3
"""
ragas_evaluator.py - RAGAS 기반 RAG 파이프라인 품질 평가 (B-35)
Faithfulness, Answer Relevancy, Context Precision, Context Recall 4대 메트릭.

Usage:
    python ragas_evaluator.py <ea_json_file> [--output <path>]
    python ragas_evaluator.py all --dir <extraction_dir>
    python ragas_evaluator.py pipeline
"""

import json
import sys
import os
from typing import Dict, List, Any

try:
    from ragas import evaluate as ragas_evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    )
    from datasets import Dataset
    RAGAS_AVAILABLE = True
except ImportError:
    RAGAS_AVAILABLE = False


def load_ea(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_source_context(filepath: str, line: int, window: int = 5) -> str:
    """Read source file context around a specific line."""
    candidates = [filepath, os.path.join("D:/VAMOS", filepath)]
    for p in candidates:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                start = max(0, line - window - 1)
                end = min(len(lines), line + window)
                return "".join(lines[start:end])
            except Exception:
                return ""
    return ""


def evaluate_ea_ragas(ea_path: str, output_path: str = None) -> dict:
    """Evaluate an EA file using RAGAS metrics."""
    ea = load_ea(ea_path)
    items = ea.get("items", [])

    if not RAGAS_AVAILABLE:
        # Fallback: compute simplified metrics
        metrics = compute_fallback_metrics(ea)
        return build_result(ea_path, items, metrics, ragas_available=False, output_path=output_path)

    # Build RAGAS dataset
    questions = []
    answers = []
    contexts = []
    ground_truths = []

    for item in items[:30]:  # Sample for efficiency
        key = item.get("key", "")
        value = str(item.get("value", ""))
        source_text = item.get("source_text", "")
        source_file = item.get("source_file", "")
        source_line = item.get("source_line", 0)

        context = read_source_context(source_file, source_line)
        if not context:
            context = source_text

        questions.append(f"What is the value of {key}?")
        answers.append(value)
        contexts.append([context[:3000]])
        ground_truths.append([source_text])

    if not questions:
        return build_result(ea_path, items, {}, output_path=output_path)

    dataset = Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": [gt[0] for gt in ground_truths],
    })

    try:
        result = ragas_evaluate(
            dataset,
            metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        )
        metrics = {
            "faithfulness": round(float(result["faithfulness"]), 4),
            "answer_relevancy": round(float(result["answer_relevancy"]), 4),
            "context_precision": round(float(result["context_precision"]), 4),
            "context_recall": round(float(result["context_recall"]), 4),
        }
    except Exception as e:
        metrics = compute_fallback_metrics(ea)
        metrics["ragas_error"] = str(e)

    return build_result(ea_path, items, metrics, ragas_available=True, output_path=output_path)


def compute_fallback_metrics(ea: dict) -> dict:
    """Simplified metrics when RAGAS is not available."""
    items = ea.get("items", [])
    if not items:
        return {"faithfulness": 0, "answer_relevancy": 0, "context_precision": 0, "context_recall": 0}

    has_source = sum(1 for i in items if i.get("source_text", "").strip())
    has_value = sum(1 for i in items if i.get("value") is not None)

    return {
        "faithfulness": round(has_source / len(items), 4),
        "answer_relevancy": round(has_value / len(items), 4),
        "context_precision": round(has_source / len(items), 4),
        "context_recall": round(has_source / len(items), 4),
    }


def build_result(ea_path: str, items: list, metrics: dict,
                 ragas_available: bool = False, output_path: str = None) -> dict:
    """Build the result JSON."""
    thresholds = {
        "faithfulness": 0.85,
        "answer_relevancy": 0.80,
        "context_precision": 0.80,
        "context_recall": 0.75,
    }

    failed = [k for k, thresh in thresholds.items()
              if k in metrics and isinstance(metrics[k], (int, float)) and metrics[k] < thresh]
    verdict = "PASS" if not failed else "FAIL"

    result = {
        "ragas_metadata": {
            "target_file": os.path.basename(ea_path),
            "target_path": ea_path,
            "total_items_evaluated": len(items),
            "ragas_available": ragas_available,
            "verdict": verdict
        },
        "metrics": metrics,
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
        print("Usage: python ragas_evaluator.py <ea_json|all|pipeline> [--dir <dir>] [--output <path>]", file=sys.stderr)
        sys.exit(1)

    target = sys.argv[1]
    output_path = None

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    if target == "all":
        import glob
        eas_dir = "D:/VAMOS/04. 구현단계/v13_results/phase0/extraction"
        if "--dir" in sys.argv:
            idx = sys.argv.index("--dir")
            if idx + 1 < len(sys.argv):
                eas_dir = sys.argv[idx + 1]
        ea_files = sorted(glob.glob(os.path.join(eas_dir, "v13_EA*.json")))
        results = [evaluate_ea_ragas(f) for f in ea_files]
        output = json.dumps({"batch_results": results}, ensure_ascii=False, indent=2)
    elif target == "pipeline":
        output = json.dumps({"note": "Pipeline evaluation requires all EAs + RAG config"}, ensure_ascii=False, indent=2)
    else:
        result = evaluate_ea_ragas(target, output_path)
        output = json.dumps(result, ensure_ascii=False, indent=2)

    print(output)


if __name__ == "__main__":
    main()
