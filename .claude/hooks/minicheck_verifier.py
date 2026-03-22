#!/usr/bin/env python3
"""
minicheck_verifier.py - MiniCheck NLI 기반 사실 검증 (B-37)
EA의 각 claim을 SOT 원문과 1:1 대조, Supported/Not Supported 판정.

Usage:
    python minicheck_verifier.py <ea_json_file> [--mode api|local] [--output <path>]
"""

import json
import sys
import os
from typing import Dict, List, Any

try:
    from minicheck import MiniCheck
    MINICHECK_AVAILABLE = True
except ImportError:
    MINICHECK_AVAILABLE = False


def load_ea(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_source_context(filepath: str, line: int, window: int = 5) -> str:
    """Read SOT source context around a line."""
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


def generate_claims(item: dict) -> List[dict]:
    """Generate claims from an EA item."""
    claims = []
    key = item.get("key", "")
    value = item.get("value", "")
    source_text = item.get("source_text", "")

    # Claim 1: value correctness
    if value is not None:
        claims.append({
            "claim": f"{key}의 값은 {value}이다",
            "type": "value"
        })

    # Claim 2: source attribution
    if source_text:
        claims.append({
            "claim": f"이 정보의 출처는 '{source_text[:100]}'이다",
            "type": "source"
        })

    return claims


def verify_with_minicheck(documents: List[str], claims: List[str], mode: str = "api") -> List[dict]:
    """Verify claims using MiniCheck."""
    if not MINICHECK_AVAILABLE:
        return [{"result": "ERROR", "confidence": 0, "error": "minicheck not installed"} for _ in claims]

    try:
        checker = MiniCheck(model_name="Bespoke-MiniCheck-7B", enable_prefix_caching=False)
        pred_labels, raw_probs, _, _ = checker.score(docs=documents, claims=claims)

        results = []
        for label, prob in zip(pred_labels, raw_probs):
            results.append({
                "result": "Supported" if label == 1 else "Not Supported",
                "confidence": round(float(prob), 4)
            })
        return results
    except Exception as e:
        return [{"result": "ERROR", "confidence": 0, "error": str(e)} for _ in claims]


def verify_ea(ea_path: str, mode: str = "api", output_path: str = None) -> dict:
    """Verify all items in an EA file using MiniCheck."""
    ea = load_ea(ea_path)
    items = ea.get("items", [])

    all_claims = []
    claim_items = []
    documents = []

    for item in items:
        source_file = item.get("source_file", "")
        source_line = item.get("source_line", 0)
        source_text = item.get("source_text", "")

        context = read_source_context(source_file, source_line)
        if not context:
            context = source_text

        item_claims = generate_claims(item)
        for claim in item_claims:
            all_claims.append(claim["claim"])
            claim_items.append({
                "item_id": item.get("item_id", "?"),
                "claim_type": claim["type"],
                "claim": claim["claim"]
            })
            documents.append(context[:2000])

    # Run verification
    if all_claims:
        verification_results = verify_with_minicheck(documents, all_claims, mode)
    else:
        verification_results = []

    # Combine results
    claims_output = []
    supported = 0
    not_supported = 0

    for claim_info, ver_result in zip(claim_items, verification_results):
        result_label = ver_result.get("result", "ERROR")
        if result_label == "Supported":
            supported += 1
        elif result_label == "Not Supported":
            not_supported += 1

        claims_output.append({
            "item_id": claim_info["item_id"],
            "claim_type": claim_info["claim_type"],
            "claim": claim_info["claim"],
            "result": result_label,
            "confidence": ver_result.get("confidence", 0)
        })

    total = len(all_claims)
    support_rate = round(supported / total, 4) if total > 0 else 0
    verdict = "PASS" if support_rate >= 0.95 else "FAIL"

    result = {
        "minicheck_metadata": {
            "target_file": os.path.basename(ea_path),
            "target_path": ea_path,
            "mode": mode,
            "minicheck_available": MINICHECK_AVAILABLE,
            "total_claims": total,
            "supported": supported,
            "not_supported": not_supported,
            "support_rate": support_rate,
            "verdict": verdict
        },
        "claims": claims_output[:50]  # Limit output size
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
        print("Usage: python minicheck_verifier.py <ea_json> [--mode api|local] [--output <path>]", file=sys.stderr)
        sys.exit(1)

    ea_path = sys.argv[1]
    mode = "api"
    output_path = None

    if "--mode" in sys.argv:
        idx = sys.argv.index("--mode")
        if idx + 1 < len(sys.argv):
            mode = sys.argv[idx + 1]

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    result = verify_ea(ea_path, mode, output_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
