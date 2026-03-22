"""
Confidence Calibrator for VAMOS
EA 항목별 신뢰도를 반복 추출 일치율 또는 교차 모델로 보정
"""

import json
import sys
import argparse
from datetime import datetime
from collections import Counter

def calibrate_self(ea_items, extractions_list):
    """방법 A: 반복 추출 일치율로 보정"""
    results = []
    num_runs = len(extractions_list)

    for item in ea_items:
        item_id = item.get("item_id", item.get("id", ""))
        fields = {k: v for k, v in item.items()
                  if k not in ("item_id", "id", "confidence", "source_text", "metadata")}

        for field, original_value in fields.items():
            # 각 추출 결과에서 동일 항목/필드 값 수집
            extracted_values = []
            for extraction in extractions_list:
                for ext_item in extraction:
                    ext_id = ext_item.get("item_id", ext_item.get("id", ""))
                    if str(ext_id) == str(item_id):
                        ext_val = ext_item.get(field)
                        if ext_val is not None:
                            extracted_values.append(str(ext_val).strip())
                        break

            if not extracted_values:
                continue

            # 최빈값과 일치율 계산
            counter = Counter(extracted_values)
            most_common_val, most_common_count = counter.most_common(1)[0]
            agreement_rate = most_common_count / len(extracted_values)

            original_conf = item.get("confidence", 0.9)

            results.append({
                "item_id": item_id,
                "field": field,
                "original_value": str(original_value),
                "original_confidence": original_conf,
                "calibrated_confidence": round(agreement_rate, 2),
                "delta": round(agreement_rate - original_conf, 2),
                "num_extractions": len(extracted_values),
                "agreement_count": most_common_count,
                "action": "재추출 필요" if agreement_rate < 0.7 else ""
            })

    return results

def calibrate_cross(ea_items, cross_results):
    """방법 B: 교차 모델 비교 결과로 보정"""
    verdict_to_conf = {
        "MATCH": 1.0,
        "PARTIAL": 0.7,
        "MISMATCH": 0.3,
        "CLAUDE_ONLY": 0.5,
        "GPT_ONLY": 0.5
    }

    comparisons = cross_results.get("comparisons", [])
    comp_map = {c["key"]: c for c in comparisons}

    results = []
    for item in ea_items:
        item_id = item.get("item_id", item.get("id", ""))
        fields = {k: v for k, v in item.items()
                  if k not in ("item_id", "id", "confidence", "source_text", "metadata")}

        for field, original_value in fields.items():
            key = f"{item_id}.{field}"
            comp = comp_map.get(key)
            if not comp:
                continue

            verdict = comp.get("verdict", "")
            calibrated = verdict_to_conf.get(verdict, 0.5)
            original_conf = item.get("confidence", 0.9)

            results.append({
                "item_id": item_id,
                "field": field,
                "original_value": str(original_value),
                "original_confidence": original_conf,
                "calibrated_confidence": calibrated,
                "delta": round(calibrated - original_conf, 2),
                "cross_verdict": verdict,
                "action": "재추출 필요" if calibrated < 0.7 else ""
            })

    return results

def main():
    parser = argparse.ArgumentParser(description="Confidence calibrator")
    parser.add_argument("--ea", required=True, help="EA JSON 파일")
    parser.add_argument("--extractions", help="반복 추출 결과 JSON (method=self)")
    parser.add_argument("--cross-result", help="교차 모델 결과 JSON (method=cross)")
    parser.add_argument("--method", choices=["self", "cross"], default="self")
    parser.add_argument("--output", required=True, help="출력 JSON 파일")
    parser.add_argument("--recalibrate", action="store_true",
                        help="보정된 confidence를 EA 원본에 직접 반영 (원본은 _backup으로 백업)")
    args = parser.parse_args()

    with open(args.ea, "r", encoding="utf-8") as f:
        ea_data = json.load(f)

    ea_items = ea_data if isinstance(ea_data, list) else ea_data.get("items", [])

    if args.method == "self":
        if not args.extractions:
            print("ERROR: --extractions 필요 (method=self)", file=sys.stderr)
            sys.exit(1)
        with open(args.extractions, "r", encoding="utf-8") as f:
            extractions = json.load(f)
        results = calibrate_self(ea_items, extractions)
    else:
        if not args.cross_result:
            print("ERROR: --cross-result 필요 (method=cross)", file=sys.stderr)
            sys.exit(1)
        with open(args.cross_result, "r", encoding="utf-8") as f:
            cross_data = json.load(f)
        results = calibrate_cross(ea_items, cross_data)

    # 통계
    need_reextract = sum(1 for r in results if r.get("action"))
    up = sum(1 for r in results if r["delta"] > 0)
    down = sum(1 for r in results if r["delta"] < 0)

    output = {
        "timestamp": datetime.now().isoformat(),
        "method": args.method,
        "total_calibrated": len(results),
        "upward_adjusted": up,
        "downward_adjusted": down,
        "need_reextract": need_reextract,
        "results": results
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # --recalibrate: 보정된 confidence를 EA 원본에 직접 반영
    if args.recalibrate:
        import shutil
        backup_path = args.ea.replace(".json", "_backup.json")
        shutil.copy2(args.ea, backup_path)
        print(f"백업 생성: {backup_path}")

        # 보정 결과를 item_id+field → calibrated_confidence 맵으로 변환
        cal_map = {}
        for r in results:
            key = f"{r['item_id']}.{r['field']}"
            cal_map[key] = r["calibrated_confidence"]

        # EA 원본에 반영
        items = ea_data if isinstance(ea_data, list) else ea_data.get("items", [])
        updated_count = 0
        for item in items:
            item_id = item.get("item_id", item.get("id", ""))
            for field in item:
                key = f"{item_id}.{field}"
                if key in cal_map:
                    item["confidence"] = cal_map[key]
                    updated_count += 1
                    break

        with open(args.ea, "w", encoding="utf-8") as f:
            json.dump(ea_data, f, ensure_ascii=False, indent=2)

        print(f"EA 원본 업데이트: {updated_count}건 confidence 반영 완료")

    print(f"\n완료: 보정={len(results)}건, 상향={up}, 하향={down}, 재추출필요={need_reextract}")

if __name__ == "__main__":
    main()
