"""
Langfuse Logger for VAMOS
LLM 호출 자동 로깅 + Phase별 추적
"""

import json
import os
import sys
import argparse
from datetime import datetime

def get_langfuse_client():
    public_key = os.environ.get("LANGFUSE_PUBLIC_KEY")
    secret_key = os.environ.get("LANGFUSE_SECRET_KEY")
    host = os.environ.get("LANGFUSE_HOST", "http://localhost:3000")

    if not public_key or not secret_key:
        print("ERROR: LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY 환경변수 필요", file=sys.stderr)
        sys.exit(1)

    from langfuse import Langfuse
    return Langfuse(public_key=public_key, secret_key=secret_key, host=host)

def log_trace(client, phase, skill_name, input_data, output_data, metadata=None):
    """단일 스킬 실행을 trace로 기록 (Langfuse SDK v4+)"""
    trace_id = client.create_trace_id()
    with client.start_as_current_observation(
        name=f"phase{phase}_{skill_name}",
        as_type="span",
        input=input_data,
        output=output_data,
        metadata={
            "phase": phase,
            "skill": skill_name,
            "timestamp": datetime.now().isoformat(),
            "trace_id": trace_id,
            **(metadata or {})
        }
    ) as span:
        pass  # span auto-ends on exit
    return trace_id

def log_generation(client, trace_id, model, prompt, completion, usage=None):
    """LLM 생성 호출 기록 (Langfuse SDK v4+)"""
    with client.start_as_current_observation(
        name="llm_call",
        as_type="generation",
        model=model,
        input=prompt,
        output=completion,
        usage_details=usage
    ) as gen:
        pass  # generation auto-ends on exit

def get_session_stats(client, session_id=None):
    """세션 통계 조회"""
    return {
        "dashboard_url": os.environ.get("LANGFUSE_HOST", "http://localhost:3000"),
        "status": "active"
    }

def main():
    parser = argparse.ArgumentParser(description="Langfuse logger")
    parser.add_argument("--action", choices=["start", "stop", "status", "log"], required=True)
    parser.add_argument("--phase", help="Phase 번호")
    parser.add_argument("--skill", help="스킬 이름")
    parser.add_argument("--input", help="입력 JSON 파일")
    parser.add_argument("--output", help="출력 JSON 파일")
    args = parser.parse_args()

    client = get_langfuse_client()

    if args.action == "start":
        print(f"Langfuse 로깅 시작 (Phase {args.phase or 'all'})")
        print(f"대시보드: {os.environ.get('LANGFUSE_HOST', 'http://localhost:3000')}")

    elif args.action == "stop":
        client.flush()
        print("Langfuse 로깅 중단, 버퍼 플러시 완료")

    elif args.action == "status":
        stats = get_session_stats(client)
        print(f"상태: {stats['status']}")
        print(f"대시보드: {stats['dashboard_url']}")

    elif args.action == "log":
        if not args.input:
            print("ERROR: --input 필요", file=sys.stderr)
            sys.exit(1)
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
        trace_id = log_trace(
            client,
            phase=args.phase or "0",
            skill_name=args.skill or "unknown",
            input_data=data.get("input", {}),
            output_data=data.get("output", {})
        )
        print(f"Trace 기록 완료: {trace_id}")

    client.flush()

if __name__ == "__main__":
    main()
