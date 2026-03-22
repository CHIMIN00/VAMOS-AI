"""
SOT Vector Search for VAMOS
Milvus 벡터 검색으로 SOT 관련 구절 검색
"""

import json
import sys
import argparse
from datetime import datetime

def search_sot(query, collection_name="vamos_sot", top_k=5, host="localhost", port=19530):
    """벡터 유사도 검색"""
    from pymilvus import connections, Collection
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_embedding = model.encode([query]).tolist()

    connections.connect(host=host, port=str(port))
    collection = Collection(collection_name)
    collection.load()

    results = collection.search(
        data=query_embedding,
        anns_field="embedding",
        param={"metric_type": "COSINE", "params": {"nprobe": 10}},
        limit=top_k,
        output_fields=["text", "file_name", "start_line", "end_line"]
    )

    search_results = []
    for hits in results:
        for hit in hits:
            search_results.append({
                "file_name": hit.entity.get("file_name"),
                "start_line": hit.entity.get("start_line"),
                "end_line": hit.entity.get("end_line"),
                "text": hit.entity.get("text"),
                "score": round(hit.score, 4)
            })

    collection.release()
    connections.disconnect("default")
    return search_results

def main():
    parser = argparse.ArgumentParser(description="SOT vector search")
    parser.add_argument("--query", required=True, help="검색어")
    parser.add_argument("--collection", default="vamos_sot")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=19530)
    parser.add_argument("--output", help="출력 JSON 파일")
    args = parser.parse_args()

    results = search_sot(args.query, args.collection, args.top_k, args.host, args.port)

    output = {
        "timestamp": datetime.now().isoformat(),
        "query": args.query,
        "total": len(results),
        "results": results
    }

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

    for i, r in enumerate(results):
        print(f"[{i+1}] {r['file_name']} (line {r['start_line']}~{r['end_line']}) score={r['score']}")
        print(f"    {r['text'][:100]}...")

if __name__ == "__main__":
    main()
