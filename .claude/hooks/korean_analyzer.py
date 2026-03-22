#!/usr/bin/env python3
"""
korean_analyzer.py - kiwipiepy 기반 한국어 형태소 분석 (B-36)
핵심 명사/동사 추출, 문장 분리, 띄어쓰기 보정, 복합 명사 분해.

Usage:
    python korean_analyzer.py analyze <sot_file> [--output <path>]
    python korean_analyzer.py keywords <ea_file> [--output <path>]
    python korean_analyzer.py fix-spacing "<text>"
"""

import json
import sys
import os
from collections import Counter
from typing import Dict, List, Any

try:
    from kiwipiepy import Kiwi
    KIWI_AVAILABLE = True
except ImportError:
    KIWI_AVAILABLE = False


def get_kiwi():
    """Get or create Kiwi instance."""
    if not KIWI_AVAILABLE:
        return None
    return Kiwi()


def analyze_file(filepath: str, output_path: str = None) -> dict:
    """Analyze a SOT file for Korean morphemes and keywords."""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    kiwi = get_kiwi()
    if not kiwi:
        return {
            "korean_nlp_metadata": {
                "target_file": os.path.basename(filepath),
                "mode": "analyze",
                "error": "kiwipiepy not installed. Run: pip install kiwipiepy",
                "verdict": "ERROR"
            }
        }

    # Sentence splitting
    sentences = list(kiwi.split_into_sents(text))

    # Morpheme analysis
    tokens = kiwi.tokenize(text)

    # Extract nouns (NNG=일반명사, NNP=고유명사) and verbs (VV)
    noun_counter = Counter()
    verb_counter = Counter()
    all_morphemes = 0

    for token in tokens:
        all_morphemes += 1
        tag = token.tag
        form = token.form
        if tag in ("NNG", "NNP"):
            noun_counter[form] += 1
        elif tag == "VV":
            verb_counter[form] += 1

    # Top keywords
    top_nouns = [{"word": w, "pos": "NNG/NNP", "frequency": c} for w, c in noun_counter.most_common(50)]
    top_verbs = [{"word": w, "pos": "VV", "frequency": c} for w, c in verb_counter.most_common(20)]

    # Compound noun detection (consecutive nouns)
    compound_nouns = []
    prev_noun = None
    for token in tokens:
        if token.tag in ("NNG", "NNP"):
            if prev_noun:
                compound = prev_noun + token.form
                if len(compound) >= 3:
                    compound_nouns.append({
                        "compound": compound,
                        "decomposed": [prev_noun, token.form],
                        "suggested_key": (prev_noun + "_" + token.form).upper()
                    })
            prev_noun = token.form
        else:
            prev_noun = None

    # Deduplicate compounds
    seen = set()
    unique_compounds = []
    for cn in compound_nouns:
        if cn["compound"] not in seen:
            seen.add(cn["compound"])
            unique_compounds.append(cn)

    result = {
        "korean_nlp_metadata": {
            "target_file": os.path.basename(filepath),
            "target_path": filepath,
            "mode": "analyze",
            "total_sentences": len(sentences),
            "total_morphemes": all_morphemes,
            "unique_nouns": len(noun_counter),
            "unique_verbs": len(verb_counter),
            "compound_nouns_found": len(unique_compounds),
            "verdict": "COMPLETE"
        },
        "keywords": top_nouns + top_verbs,
        "compound_nouns": unique_compounds[:30],
    }

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Result saved to: {output_path}", file=sys.stderr)

    return result


def verify_keywords(ea_path: str, output_path: str = None) -> dict:
    """Verify EA item keywords against source text Korean analysis."""
    with open(ea_path, "r", encoding="utf-8") as f:
        ea = json.load(f)

    kiwi = get_kiwi()
    if not kiwi:
        return {
            "korean_nlp_metadata": {
                "target_file": os.path.basename(ea_path),
                "mode": "keywords",
                "error": "kiwipiepy not installed",
                "verdict": "ERROR"
            }
        }

    items = ea.get("items", [])
    mismatches = []

    for item in items:
        source_text = item.get("source_text", "")
        key = item.get("key", "")
        item_id = item.get("item_id", "?")

        if not source_text:
            continue

        # Extract nouns from source_text
        tokens = kiwi.tokenize(source_text)
        source_nouns = [t.form for t in tokens if t.tag in ("NNG", "NNP")]

        # Check if key parts relate to source nouns
        key_parts = key.upper().replace("_", " ").split()

        # Simple relevancy check: at least one key part should relate to source nouns
        if source_nouns and key_parts:
            # Check for obvious mismatches
            has_match = False
            for noun in source_nouns:
                for part in key_parts:
                    if noun.upper() in part or part in noun.upper():
                        has_match = True
                        break
                if has_match:
                    break

            if not has_match and len(source_nouns) > 0:
                mismatches.append({
                    "item_id": item_id,
                    "key": key,
                    "source_keywords": source_nouns[:5],
                    "issue": f"key '{key}'와 source 핵심어 {source_nouns[:3]} 간 관련성 미확인"
                })

    verdict = "PASS" if not mismatches else "WARNING"

    result = {
        "korean_nlp_metadata": {
            "target_file": os.path.basename(ea_path),
            "target_path": ea_path,
            "mode": "keywords",
            "items_checked": len(items),
            "mismatches": len(mismatches),
            "verdict": verdict
        },
        "mismatches": mismatches[:20],
    }

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output)

    return result


def fix_spacing(text: str) -> dict:
    """Fix Korean spacing using Kiwi."""
    kiwi = get_kiwi()
    if not kiwi:
        return {"error": "kiwipiepy not installed", "original": text}

    corrected = kiwi.space(text)
    return {
        "korean_nlp_metadata": {
            "mode": "fix-spacing",
            "verdict": "COMPLETE"
        },
        "original": text,
        "corrected": corrected,
        "changed": text != corrected
    }


def main():
    if len(sys.argv) < 3:
        print("Usage: python korean_analyzer.py <analyze|keywords|fix-spacing> <file|text> [--output <path>]", file=sys.stderr)
        sys.exit(1)

    subcmd = sys.argv[1]
    target = sys.argv[2]
    output_path = None

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    if subcmd == "analyze":
        result = analyze_file(target, output_path)
    elif subcmd == "keywords":
        result = verify_keywords(target, output_path)
    elif subcmd == "fix-spacing":
        result = fix_spacing(target)
    else:
        print(f"Unknown subcommand: {subcmd}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
