"""
Patronus Lynx Hallucination Checker for VAMOS
환각 탐지 전문 모델로 EA 항목의 충실성 검증
"""

import json
import os
import sys
import argparse
from datetime import datetime

def check_with_api(tuples_list):
    """Patronus API로 환각 탐지 (SDK v0.1.25+)"""
    if not os.environ.get("PATRONUS_API_KEY"):
        print("ERROR: PATRONUS_API_KEY 환경변수가 설정되지 않았습니다.", file=sys.stderr)
        sys.exit(1)

    import patronus
    from patronus import Patronus

    patronus.init(api_key=os.environ["PATRONUS_API_KEY"])
    client = Patronus()
    results = []

    for i, t in enumerate(tuples_list):
        print(f"[{i+1}/{len(tuples_list)}] 검증 중: {t.get('ea_item', '')} / {t.get('field', '')}")
        try:
            container = client.evaluate(
                evaluators=("lynx", "patronus:hallucination"),
                task_input=t["question"],
                task_output=t["answer"],
                task_context=t["context"]
            )

            r = container.results[0]
            pass_flag = r.pass_ if hasattr(r, 'pass_') else None
            explanation = r.explanation if hasattr(r, 'explanation') else ""

            results.append({
                "ea_item": t.get("ea_item", ""),
                "field": t.get("field", ""),
                "answer": t["answer"],
                "verdict": "FAITHFUL" if pass_flag else "NOT_FAITHFUL",
                "explanation": explanation or "",
                "score": r.score if hasattr(r, 'score') else None
            })

        except Exception as e:
            results.append({
                "ea_item": t.get("ea_item", ""),
                "field": t.get("field", ""),
                "answer": t["answer"],
                "verdict": "ERROR",
                "explanation": str(e),
                "score": None
            })

    return results

def check_with_local(tuples_list):
    """로컬 Patronus Lynx 모델로 환각 탐지 (GPU 필요)"""
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM
    except ImportError:
        print("ERROR: transformers, torch 설치 필요: pip install transformers torch", file=sys.stderr)
        sys.exit(1)

    model_name = "PatronusAI/Llama-3-Patronus-Lynx-8B-Instruct"
    print(f"모델 로딩 중: {model_name}...")

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto"
    )

    results = []
    for i, t in enumerate(tuples_list):
        print(f"[{i+1}/{len(tuples_list)}] 검증 중: {t.get('ea_item', '')} / {t.get('field', '')}")

        prompt = f"""Given the following context, question, and answer, determine if the answer is faithful to the context.

Context: {t['context'][:2000]}

Question: {t['question']}

Answer: {t['answer']}

Is the answer faithful to the context? Respond with FAITHFUL or NOT_FAITHFUL, followed by a brief explanation."""

        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=200, temperature=0.0)
        response = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)

        verdict = "FAITHFUL" if "FAITHFUL" in response and "NOT_FAITHFUL" not in response else "NOT_FAITHFUL"

        results.append({
            "ea_item": t.get("ea_item", ""),
            "field": t.get("field", ""),
            "answer": t["answer"],
            "verdict": verdict,
            "explanation": response.strip(),
            "score": None
        })

    return results

def main():
    parser = argparse.ArgumentParser(description="Patronus hallucination checker")
    parser.add_argument("--input", required=True, help="입력 3-튜플 JSON")
    parser.add_argument("--mode", choices=["api", "local"], default="api")
    parser.add_argument("--output", required=True, help="출력 결과 JSON")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        tuples_list = json.load(f)

    if args.mode == "api":
        results = check_with_api(tuples_list)
    else:
        results = check_with_local(tuples_list)

    # 통계
    faithful = sum(1 for r in results if r["verdict"] == "FAITHFUL")
    not_faithful = sum(1 for r in results if r["verdict"] == "NOT_FAITHFUL")
    errors = sum(1 for r in results if r["verdict"] == "ERROR")

    output = {
        "timestamp": datetime.now().isoformat(),
        "mode": args.mode,
        "total": len(results),
        "faithful": faithful,
        "not_faithful": not_faithful,
        "errors": errors,
        "faithfulness_rate": round(faithful / len(results) * 100, 1) if results else 0,
        "results": results
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n완료: FAITHFUL={faithful}, NOT_FAITHFUL={not_faithful}, ERROR={errors}")
    print(f"충실도: {output['faithfulness_rate']}%")

if __name__ == "__main__":
    main()

