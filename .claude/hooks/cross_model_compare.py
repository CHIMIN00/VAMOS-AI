"""
Cross-Model Consistency Checker for VAMOS
동일 SOT를 GPT로 추출하여 Claude EA와 비교
"""

import json
import os
import sys
import argparse
from datetime import datetime

def get_openai_client():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY 환경변수가 설정되지 않았습니다.", file=sys.stderr)
        sys.exit(1)
    from openai import OpenAI
    return OpenAI(api_key=api_key)

def extract_with_gpt(client, sot_text, model="gpt-4o-mini"):
    """GPT로 SOT에서 EA 항목 추출"""
    prompt = f"""아래 문서에서 핵심 정보를 JSON 형태로 추출하세요.
각 항목은 다음 필드를 포함합니다:
- item_id: 항목 식별자
- field: 필드명
- value: 추출된 값
- source_text: 원본에서 해당 값이 나온 문장

문서:
{sot_text[:8000]}

JSON 배열로 응답하세요. 마크다운 코드블록 없이 순수 JSON만 출력하세요."""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "당신은 문서에서 정보를 정확히 추출하는 전문가입니다. JSON만 출력하세요."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=4000
    )

    text = response.choices[0].message.content.strip()
    # Remove markdown code blocks if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return [{"error": "GPT 응답 파싱 실패", "raw": text[:500]}]

def compare_items(claude_items, gpt_items):
    """Claude EA와 GPT 추출 결과 비교"""
    results = []

    # Claude 항목을 dict로 변환
    claude_map = {}
    for item in claude_items:
        key = f"{item.get('item_id', '')}.{item.get('field', '')}"
        claude_map[key] = item

    # GPT 항목을 dict로 변환
    gpt_map = {}
    for item in gpt_items:
        key = f"{item.get('item_id', '')}.{item.get('field', '')}"
        gpt_map[key] = item

    all_keys = set(list(claude_map.keys()) + list(gpt_map.keys()))

    for key in sorted(all_keys):
        c_item = claude_map.get(key)
        g_item = gpt_map.get(key)

        if c_item and g_item:
            c_val = str(c_item.get("value", ""))
            g_val = str(g_item.get("value", ""))

            if c_val == g_val:
                verdict = "MATCH"
            elif c_val.lower().strip() == g_val.lower().strip():
                verdict = "PARTIAL"
            elif c_val in g_val or g_val in c_val:
                verdict = "PARTIAL"
            else:
                verdict = "MISMATCH"

            results.append({
                "key": key,
                "claude_value": c_val,
                "gpt_value": g_val,
                "verdict": verdict
            })
        elif c_item and not g_item:
            results.append({
                "key": key,
                "claude_value": str(c_item.get("value", "")),
                "gpt_value": None,
                "verdict": "CLAUDE_ONLY"
            })
        else:
            results.append({
                "key": key,
                "claude_value": None,
                "gpt_value": str(g_item.get("value", "")),
                "verdict": "GPT_ONLY"
            })

    return results

def main():
    parser = argparse.ArgumentParser(description="Cross-model comparison")
    parser.add_argument("--sot", required=True, help="SOT 파일 경로")
    parser.add_argument("--claude-ea", required=True, help="Claude EA JSON 파일")
    parser.add_argument("--model", default="gpt-4o-mini", help="GPT 모델")
    parser.add_argument("--output", required=True, help="출력 JSON 파일")
    args = parser.parse_args()

    # SOT 읽기
    with open(args.sot, "r", encoding="utf-8") as f:
        sot_text = f.read()

    # Claude EA 읽기
    with open(args.claude_ea, "r", encoding="utf-8") as f:
        claude_data = json.load(f)

    claude_items = claude_data if isinstance(claude_data, list) else claude_data.get("items", [])

    # GPT 추출
    print(f"GPT ({args.model}) 추출 중...")
    client = get_openai_client()
    gpt_items = extract_with_gpt(client, sot_text, args.model)

    # 비교
    print("Claude vs GPT 비교 중...")
    comparisons = compare_items(claude_items, gpt_items)

    # 통계
    stats = {
        "MATCH": sum(1 for c in comparisons if c["verdict"] == "MATCH"),
        "PARTIAL": sum(1 for c in comparisons if c["verdict"] == "PARTIAL"),
        "MISMATCH": sum(1 for c in comparisons if c["verdict"] == "MISMATCH"),
        "CLAUDE_ONLY": sum(1 for c in comparisons if c["verdict"] == "CLAUDE_ONLY"),
        "GPT_ONLY": sum(1 for c in comparisons if c["verdict"] == "GPT_ONLY"),
    }
    total = len(comparisons)
    agreement = stats["MATCH"] + stats["PARTIAL"]
    agreement_rate = (agreement / total * 100) if total > 0 else 0

    output = {
        "timestamp": datetime.now().isoformat(),
        "model": args.model,
        "sot_file": args.sot,
        "total_comparisons": total,
        "agreement_rate": round(agreement_rate, 1),
        "stats": stats,
        "comparisons": comparisons
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n완료: 합의율={agreement_rate:.1f}%, "
          f"MATCH={stats['MATCH']}, MISMATCH={stats['MISMATCH']}, "
          f"GPT_ONLY={stats['GPT_ONLY']}")

if __name__ == "__main__":
    main()
