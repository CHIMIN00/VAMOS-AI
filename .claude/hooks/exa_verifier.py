"""
Exa Hallucination Verifier for VAMOS
EA 항목의 기술 용어/수치를 Exa 검색 엔진으로 외부 검증
"""

import json
import os
import sys
import argparse
from datetime import datetime

def get_exa_client():
    api_key = os.environ.get("EXA_API_KEY")
    if not api_key:
        print("ERROR: EXA_API_KEY 환경변수가 설정되지 않았습니다.", file=sys.stderr)
        sys.exit(1)
    from exa_py import Exa
    return Exa(api_key=api_key)

def verify_claim(exa, claim_text, num_results=3):
    """단일 claim을 Exa로 검증"""
    try:
        results = exa.search_and_contents(
            claim_text,
            type="neural",
            use_autoprompt=True,
            num_results=num_results,
            text=True
        )

        if not results.results:
            return {
                "verdict": "NOT_FOUND",
                "score": 0.0,
                "sources": [],
                "reason": "관련 소스를 찾지 못함"
            }

        sources = []
        max_score = 0.0
        for r in results.results:
            score = r.score if hasattr(r, 'score') and r.score else 0.0
            sources.append({
                "title": r.title or "",
                "url": r.url or "",
                "score": score,
                "snippet": (r.text or "")[:200]
            })
            if score > max_score:
                max_score = score

        if max_score >= 0.8:
            verdict = "VERIFIED"
        elif max_score >= 0.5:
            verdict = "UNVERIFIED"
        else:
            verdict = "NOT_FOUND"

        return {
            "verdict": verdict,
            "score": max_score,
            "sources": sources,
            "reason": f"최고 유사도: {max_score:.2f}"
        }

    except Exception as e:
        return {
            "verdict": "ERROR",
            "score": 0.0,
            "sources": [],
            "reason": str(e)
        }

def main():
    parser = argparse.ArgumentParser(description="Exa claim verifier")
    parser.add_argument("--input", required=True, help="입력 claims JSON 파일")
    parser.add_argument("--output", required=True, help="출력 결과 JSON 파일")
    parser.add_argument("--max-results", type=int, default=3, help="검색 결과 수")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        claims = json.load(f)

    exa = get_exa_client()
    results = []

    for i, claim in enumerate(claims):
        claim_text = claim.get("claim", claim.get("text", ""))
        if not claim_text:
            continue

        print(f"[{i+1}/{len(claims)}] 검증 중: {claim_text[:60]}...")
        result = verify_claim(exa, claim_text, args.max_results)
        result["claim"] = claim_text
        result["ea_item"] = claim.get("ea_item", "")
        result["field"] = claim.get("field", "")
        results.append(result)

    output = {
        "timestamp": datetime.now().isoformat(),
        "total": len(results),
        "verified": sum(1 for r in results if r["verdict"] == "VERIFIED"),
        "unverified": sum(1 for r in results if r["verdict"] == "UNVERIFIED"),
        "not_found": sum(1 for r in results if r["verdict"] == "NOT_FOUND"),
        "errors": sum(1 for r in results if r["verdict"] == "ERROR"),
        "results": results
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n완료: VERIFIED={output['verified']}, UNVERIFIED={output['unverified']}, "
          f"NOT_FOUND={output['not_found']}, ERROR={output['errors']}")

if __name__ == "__main__":
    main()
