"""
OpenLineage Tracker for VAMOS
EA 값의 데이터 계보를 Marquez에 기록
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone
import uuid

def get_openlineage_client(marquez_url="http://localhost:5000"):
    from openlineage.client import OpenLineageClient
    from openlineage.client.transport.http import HttpConfig, HttpTransport

    http_config = HttpConfig(
        url=marquez_url,
        endpoint="api/v1/lineage"
    )
    transport = HttpTransport(http_config)
    return OpenLineageClient(transport=transport)

def track_ea(client, ea_file, namespace="vamos"):
    """EA 파일의 계보를 Marquez에 기록"""
    from openlineage.client.run import (
        RunEvent, Run, Job, Dataset,
        InputDataset, OutputDataset
    )
    from openlineage.client.facet_v2 import (
        job_type_job,
        nominal_time_run,
    )

    with open(ea_file, "r", encoding="utf-8") as f:
        ea_data = json.load(f)

    items = ea_data if isinstance(ea_data, list) else ea_data.get("items", [])
    metadata = ea_data.get("metadata", {}) if isinstance(ea_data, dict) else {}

    # 입력 데이터셋 (SOT 파일)
    source_file = metadata.get("source_file", os.path.basename(ea_file).replace("_ea.json", ""))
    input_dataset = InputDataset(
        namespace=namespace,
        name=f"sot/{source_file}"
    )

    # 출력 데이터셋 (EA 파일)
    output_dataset = OutputDataset(
        namespace=namespace,
        name=f"ea/{os.path.basename(ea_file)}"
    )

    # Run 이벤트 생성
    run_id = str(uuid.uuid4())
    job_name = f"extract_{os.path.basename(ea_file).replace('.json', '')}"

    run_event = RunEvent(
        eventType="COMPLETE",
        eventTime=datetime.now(timezone.utc).isoformat(),
        run=Run(runId=run_id),
        job=Job(namespace=namespace, name=job_name),
        inputs=[input_dataset],
        outputs=[output_dataset]
    )

    client.emit(run_event)
    print(f"계보 기록: {job_name} (run={run_id[:8]}...)")
    print(f"  입력: sot/{source_file}")
    print(f"  출력: ea/{os.path.basename(ea_file)}")
    print(f"  항목: {len(items)}개")

    return run_id

def main():
    parser = argparse.ArgumentParser(description="Lineage tracker")
    parser.add_argument("--action", choices=["track", "trace", "status"], required=True)
    parser.add_argument("--ea", help="EA JSON 파일")
    parser.add_argument("--item-id", help="추적할 항목 ID")
    parser.add_argument("--marquez-url", default="http://localhost:5000")
    parser.add_argument("--output", help="출력 JSON")
    args = parser.parse_args()

    if args.action == "track":
        if not args.ea:
            print("ERROR: --ea 필요", file=sys.stderr)
            sys.exit(1)
        client = get_openlineage_client(args.marquez_url)
        run_id = track_ea(client, args.ea)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump({"run_id": run_id, "timestamp": datetime.now().isoformat()}, f)

    elif args.action == "status":
        print(f"Marquez 대시보드: {args.marquez_url}")

if __name__ == "__main__":
    main()
