"""
Arize Phoenix Tracer for VAMOS
Phoenix Docker에 HTTP API로 trace/eval 데이터 전송
"""

import json
import os
import sys
import argparse
import urllib.request
import urllib.error
from datetime import datetime

PHOENIX_URL = "http://localhost:6006"

def check_phoenix():
    """Phoenix 서버 상태 확인"""
    try:
        req = urllib.request.urlopen(f"{PHOENIX_URL}", timeout=5)
        return req.status == 200
    except (urllib.error.URLError, Exception):
        return False

def send_trace(phase, input_data, phoenix_url=PHOENIX_URL):
    """Phoenix에 trace 데이터 전송"""
    trace_data = {
        "name": f"phase_{phase}",
        "timestamp": datetime.now().isoformat(),
        "phase": phase,
        "data": input_data
    }

    # Phoenix OTLP endpoint로 전송
    payload = json.dumps(trace_data).encode("utf-8")
    req = urllib.request.Request(
        f"{phoenix_url}/v1/traces",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        response = urllib.request.urlopen(req, timeout=10)
        return {"status": "ok", "code": response.status}
    except urllib.error.HTTPError as e:
        return {"status": "error", "code": e.code, "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def send_eval(ea_file, phoenix_url=PHOENIX_URL):
    """EA 평가 데이터를 Phoenix에 전송"""
    with open(ea_file, "r", encoding="utf-8") as f:
        ea_data = json.load(f)

    items = ea_data if isinstance(ea_data, list) else ea_data.get("items", [])

    eval_data = {
        "name": f"eval_{os.path.basename(ea_file)}",
        "timestamp": datetime.now().isoformat(),
        "total_items": len(items),
        "items": items[:50]  # 최대 50개만 전송
    }

    payload = json.dumps(eval_data, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"{phoenix_url}/v1/evaluations",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        response = urllib.request.urlopen(req, timeout=10)
        return {"status": "ok", "items": len(items)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Phoenix tracer")
    parser.add_argument("--action", choices=["start", "trace", "eval", "status"], required=True)
    parser.add_argument("--phase", help="Phase 번호")
    parser.add_argument("--input", help="입력 JSON")
    parser.add_argument("--ea", help="EA 파일")
    parser.add_argument("--phoenix-url", default=PHOENIX_URL)
    args = parser.parse_args()

    if args.action == "status" or args.action == "start":
        alive = check_phoenix()
        print(f"Phoenix: {'정상' if alive else '연결 실패'}")
        print(f"UI: {args.phoenix_url}")

    elif args.action == "trace":
        input_data = {}
        if args.input:
            with open(args.input, "r", encoding="utf-8") as f:
                input_data = json.load(f)
        result = send_trace(args.phase or "0", input_data, args.phoenix_url)
        print(f"Trace 전송: {result['status']}")

    elif args.action == "eval":
        if not args.ea:
            print("ERROR: --ea 필요", file=sys.stderr)
            sys.exit(1)
        result = send_eval(args.ea, args.phoenix_url)
        print(f"Eval 전송: {result}")

if __name__ == "__main__":
    main()
