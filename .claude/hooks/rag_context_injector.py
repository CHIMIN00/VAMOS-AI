"""
RAG Context Injector for VAMOS
스킬 실행 시 관련 SOT 구절을 자동으로 컨텍스트에 주입
"""

import json
import sys
import argparse
from datetime import datetime

def inject_context(query, collection_name="vamos_sot", top_k=3, host="localhost", port=19530):
    """쿼리에 관련된 SOT 구절을 검색하여 컨텍스트 생성"""
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

    context_chunks = []
    for hits in results:
        for hit in hits:
            context_chunks.append({
                "file_name": hit.entity.get("file_name"),
                "start_line": hit.entity.get("start_line"),
                "end_line": hit.entity.get("end_line"),
                "text": hit.entity.get("text"),
                "score": round(hit.score, 4)
            })

    collection.release()
    connections.disconnect("default")

    # 컨텍스트 텍스트 조합
    context_text = "\n\n---\n\n".join([
        f"[{c['file_name']} line {c['start_line']}~{c['end_line']}]\n{c['text']}"
        for c in context_chunks
    ])

    return {
        "query": query,
        "context": context_text,
        "chunks": context_chunks,
        "total_chunks": len(context_chunks)
    }

def main():
    parser = argparse.ArgumentParser(description="RAG context injector")
    parser.add_argument("--query", required=True, help="검색 쿼리")
    parser.add_argument("--collection", default="vamos_sot")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=19530)
    parser.add_argument("--output", required=True, help="출력 JSON")
    args = parser.parse_args()

    result = inject_context(args.query, args.collection, args.top_k, args.host, args.port)
    result["timestamp"] = datetime.now().isoformat()

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"컨텍스트 주입: {result['total_chunks']}개 청크 검색됨")

if __name__ == "__main__":
    main()
