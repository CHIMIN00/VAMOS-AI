#!/usr/bin/env python3
"""
input_scanner.py - LLM Guard 기반 SOT/EA 보안 스캔 (B-14)
PromptInjection, Regex, TokenLimit, Anonymize 스캐너 적용.

Usage:
    python input_scanner.py scan-input <sot_file> [--output <path>]
    python input_scanner.py scan-output <ea_file> [--output <path>]
"""

import json
import sys
import os
import re
from typing import Dict, List, Any

try:
    from llm_guard.input_scanners import PromptInjection, TokenLimit, Anonymize
    from llm_guard.input_scanners.regex import Regex as InputRegex
    LLM_GUARD_AVAILABLE = True
except ImportError:
    LLM_GUARD_AVAILABLE = False


# ---------------------------------------------------------------------------
# Fallback scanners (when llm-guard is not importable)
# ---------------------------------------------------------------------------

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"you\s+are\s+now\s+",
    r"system\s*:\s*",
    r"<\|im_start\|>",
    r"\[INST\]",
    r"act\s+as\s+(a\s+)?",
    r"pretend\s+you\s+are",
    r"do\s+not\s+follow",
    r"override\s+(your\s+)?instructions",
    r"jailbreak",
]

SUSPICIOUS_PATTERNS = [
    r"[A-Za-z0-9+/]{50,}={0,2}",  # base64-like
    r"\\x[0-9a-fA-F]{2}",  # hex escape
    r"&#x?[0-9a-fA-F]+;",  # HTML entity encoding
]

PII_PATTERNS = [
    (r"\d{3}-\d{2}-\d{4}", "SSN"),
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "EMAIL"),
    (r"\d{3}[-.\s]?\d{3,4}[-.\s]?\d{4}", "PHONE"),
]


def scan_text_fallback(text: str) -> List[Dict]:
    """Fallback scanning without llm-guard."""
    results = []

    # PromptInjection scan
    injection_found = False
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            injection_found = True
            break
    results.append({
        "scanner": "PromptInjection",
        "status": "DETECTED" if injection_found else "SAFE",
        "confidence": 0.9 if injection_found else 0.0,
        "details": "Prompt injection pattern detected" if injection_found else ""
    })

    # Regex scan
    regex_found = False
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, text):
            regex_found = True
            break
    results.append({
        "scanner": "Regex",
        "status": "DETECTED" if regex_found else "SAFE",
        "confidence": 0.8 if regex_found else 0.0,
        "details": "Suspicious encoded pattern detected" if regex_found else ""
    })

    # TokenLimit scan
    token_estimate = len(text.split())
    over_limit = token_estimate > 100000
    results.append({
        "scanner": "TokenLimit",
        "status": "EXCEEDED" if over_limit else "SAFE",
        "confidence": 1.0 if over_limit else 0.0,
        "details": f"Estimated tokens: {token_estimate}" if over_limit else ""
    })

    # Anonymize (PII) scan
    pii_found = []
    for pattern, pii_type in PII_PATTERNS:
        if re.search(pattern, text):
            pii_found.append(pii_type)
    results.append({
        "scanner": "Anonymize",
        "status": "DETECTED" if pii_found else "SAFE",
        "confidence": 0.85 if pii_found else 0.0,
        "details": f"PII types found: {pii_found}" if pii_found else ""
    })

    return results


def scan_with_llm_guard(text: str) -> List[Dict]:
    """Scan text using llm-guard library."""
    results = []

    try:
        scanner = PromptInjection()
        sanitized, is_valid, risk_score = scanner.scan("", text)
        results.append({
            "scanner": "PromptInjection",
            "status": "SAFE" if is_valid else "DETECTED",
            "confidence": round(risk_score, 4),
            "details": "" if is_valid else "Prompt injection detected"
        })
    except Exception as e:
        results.append({"scanner": "PromptInjection", "status": "ERROR", "confidence": 0, "details": str(e)})

    try:
        scanner = TokenLimit(limit=100000)
        sanitized, is_valid, risk_score = scanner.scan("", text)
        results.append({
            "scanner": "TokenLimit",
            "status": "SAFE" if is_valid else "EXCEEDED",
            "confidence": round(risk_score, 4),
            "details": "" if is_valid else "Token limit exceeded"
        })
    except Exception as e:
        results.append({"scanner": "TokenLimit", "status": "ERROR", "confidence": 0, "details": str(e)})

    try:
        scanner = Anonymize()
        sanitized, is_valid, risk_score = scanner.scan("", text)
        results.append({
            "scanner": "Anonymize",
            "status": "SAFE" if is_valid else "DETECTED",
            "confidence": round(risk_score, 4),
            "details": "" if is_valid else "PII detected"
        })
    except Exception as e:
        results.append({"scanner": "Anonymize", "status": "ERROR", "confidence": 0, "details": str(e)})

    return results


def scan_file(filepath: str, mode: str = "input", output_path: str = None) -> dict:
    """Scan a file for security issues."""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    if LLM_GUARD_AVAILABLE:
        scanner_results = scan_with_llm_guard(text)
    else:
        scanner_results = scan_text_fallback(text)

    threats = sum(1 for r in scanner_results if r["status"] not in ("SAFE", "ERROR"))

    if any(r["scanner"] == "PromptInjection" and r["status"] == "DETECTED" for r in scanner_results):
        verdict = "BLOCKED"
    elif threats > 0:
        verdict = "WARNING"
    else:
        verdict = "SAFE"

    result = {
        "input_guard_metadata": {
            "target_file": os.path.basename(filepath),
            "target_path": filepath,
            "scan_mode": mode,
            "scanners_applied": len(scanner_results),
            "threats_detected": threats,
            "llm_guard_available": LLM_GUARD_AVAILABLE,
            "verdict": verdict
        },
        "scanner_results": scanner_results
    }

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Result saved to: {output_path}", file=sys.stderr)

    return result


def main():
    if len(sys.argv) < 3:
        print("Usage: python input_scanner.py <scan-input|scan-output> <file> [--output <path>]", file=sys.stderr)
        sys.exit(1)

    mode_arg = sys.argv[1]
    filepath = sys.argv[2]
    output_path = None

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    mode = "input" if "input" in mode_arg else "output"
    result = scan_file(filepath, mode, output_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
