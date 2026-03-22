"""
Vectara HHEM Hallucination Scorer for VAMOS
환각 탐지 전용 학습 모델로 EA 항목의 사실 일관성 점수 산출
C-40 Cleanlab TLM 대체
"""

import json
import sys
import argparse
from datetime import datetime

def load_model():
    """HHEM 모델 로드 (첫 실행 시 ~600MB 다운로드)"""
    from transformers import AutoModelForSequenceClassification
    print("HHEM 모델 로딩 중 (첫 실행 시 다운로드 ~600MB)...")
    model = AutoModelForSequenceClassification.from_pretrained(
        'vectara/hallucination_evaluation_model',
        trust_remote_code=True
    )
    print("모델 로드 완료.")
    return model

def score_pairs(model, pairs_data, threshold=0.8):
    """(premise, hypothesis) 쌍을 HHEM으로 점수화"""
    results = []

    # 배치 처리를 위해 pairs 구성
    batch_size = 16
    for i in range(0, len(pairs_data), batch_size):
        batch = pairs_data[i:i + batch_size]
        text_pairs = [(p["premise"], p["hypothesis"]) for p in batch]

        print(f"[{i+1}~{min(i+batch_size, len(pairs_data))}/{len(pairs_data)}] 점수 산출 중...")

        try:
            scores = model.predict(text_pairs)

            for j, (pair, score) in enumerate(zip(batch, scores)):
                score_val = float(score)

                if score_val >= threshold:
                    verdict = "PASS"
                elif score_val >= 0.5:
                    verdict = "WARN"
                else:
                    verdict = "FAIL"

                results.append({
                    "ea_item": pair.get("ea_item", ""),
                    "field": pair.get("field", ""),
                    "hypothesis": pair["hypothesis"],
                    "score": round(score_val, 4),
                    "verdict": verdict
                })

        except Exception as e:
            for pair in batch:
                results.append({
                    "ea_item": pair.get("ea_item", ""),
                    "field": pair.get("field", ""),
                    "hypothesis": pair["hypothesis"],
                    "score": 0.0,
                    "verdict": "ERROR",
                    "error": str(e)
                })

    return results

def main():
    parser = argparse.ArgumentParser(description="HHEM hallucination scorer")
    parser.add_argument("--input", required=True, help="입력 (premise, hypothesis) 쌍 JSON")
    parser.add_argument("--threshold", type=float, default=0.8, help="PASS 판정 기준 점수 (기본: 0.8)")
    parser.add_argument("--output", required=True, help="출력 결과 JSON")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        pairs_data = json.load(f)

    if not pairs_data:
        print("입력 데이터가 비어있습니다.")
        sys.exit(1)

    model = load_model()
    results = score_pairs(model, pairs_data, args.threshold)

    # 통계
    pass_count = sum(1 for r in results if r["verdict"] == "PASS")
    warn_count = sum(1 for r in results if r["verdict"] == "WARN")
    fail_count = sum(1 for r in results if r["verdict"] == "FAIL")
    error_count = sum(1 for r in results if r["verdict"] == "ERROR")
    total = len(results)

    avg_score = sum(r["score"] for r in results) / total if total > 0 else 0

    output = {
        "timestamp": datetime.now().isoformat(),
        "model": "vectara/hallucination_evaluation_model (HHEM-2.1)",
        "threshold": args.threshold,
        "total": total,
        "pass": pass_count,
        "warn": warn_count,
        "fail": fail_count,
        "errors": error_count,
        "avg_score": round(avg_score, 4),
        "pass_rate": round(pass_count / total * 100, 1) if total > 0 else 0,
        "results": results
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n완료: PASS={pass_count}, WARN={warn_count}, FAIL={fail_count}, ERROR={error_count}")
    print(f"평균 점수: {avg_score:.4f}, PASS율: {output['pass_rate']}%")

if __name__ == "__main__":
    main()
