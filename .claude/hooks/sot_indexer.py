"""
SOT Vector Indexer for VAMOS
SOT 파일을 벡터 임베딩으로 Milvus에 인덱싱
"""

import json
import os
import sys
import argparse
import glob
from datetime import datetime

def chunk_text(text, chunk_size=500, overlap=100):
    """텍스트를 청크 단위로 분할"""
    chunks = []
    lines = text.split("\n")
    current_chunk = []
    current_size = 0

    for i, line in enumerate(lines):
        current_chunk.append(line)
        current_size += len(line)

        if current_size >= chunk_size:
            chunk_text = "\n".join(current_chunk)
            chunks.append({
                "text": chunk_text,
                "start_line": i - len(current_chunk) + 2,
                "end_line": i + 1
            })
            # 오버랩 처리
            overlap_lines = []
            overlap_size = 0
            for l in reversed(current_chunk):
                if overlap_size + len(l) > overlap:
                    break
                overlap_lines.insert(0, l)
                overlap_size += len(l)
            current_chunk = overlap_lines
            current_size = overlap_size

    if current_chunk:
        chunks.append({
            "text": "\n".join(current_chunk),
            "start_line": max(1, len(lines) - len(current_chunk) + 1),
            "end_line": len(lines)
        })

    return chunks

def index_sot(sot_dir, collection_name="vamos_sot", host="localhost", port=19530):
    """SOT 파일을 Milvus에 인덱싱"""
    from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
    from sentence_transformers import SentenceTransformer

    print("임베딩 모델 로딩 중...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    dim = model.get_sentence_embedding_dimension()

    print(f"Milvus 연결 중 ({host}:{port})...")
    connections.connect(host=host, port=str(port))

    # 기존 컬렉션 삭제
    if utility.has_collection(collection_name):
        utility.drop_collection(collection_name)
        print(f"기존 컬렉션 '{collection_name}' 삭제")

    # 스키마 정의
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=4096),
        FieldSchema(name="file_name", dtype=DataType.VARCHAR, max_length=256),
        FieldSchema(name="start_line", dtype=DataType.INT64),
        FieldSchema(name="end_line", dtype=DataType.INT64),
    ]
    schema = CollectionSchema(fields, description="VAMOS SOT Vector Index")
    collection = Collection(collection_name, schema)

    # SOT 파일 수집
    sot_files = []
    for ext in ["*.md", "*.txt", "*.hwpx"]:
        sot_files.extend(glob.glob(os.path.join(sot_dir, "**", ext), recursive=True))

    print(f"SOT 파일 {len(sot_files)}개 발견")

    total_chunks = 0
    for filepath in sot_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except (UnicodeDecodeError, PermissionError):
            continue

        if not content.strip():
            continue

        file_name = os.path.basename(filepath)
        chunks = chunk_text(content)

        if not chunks:
            continue

        texts = [c["text"][:4000] for c in chunks]
        embeddings = model.encode(texts).tolist()

        collection.insert([
            embeddings,
            texts,
            [file_name] * len(chunks),
            [c["start_line"] for c in chunks],
            [c["end_line"] for c in chunks],
        ])

        total_chunks += len(chunks)
        print(f"  {file_name}: {len(chunks)} 청크")

    # 인덱스 생성
    index_params = {"index_type": "IVF_FLAT", "metric_type": "COSINE", "params": {"nlist": 128}}
    collection.create_index("embedding", index_params)
    collection.flush()

    print(f"\n인덱싱 완료: {len(sot_files)}파일, {total_chunks}청크")
    connections.disconnect("default")

def main():
    parser = argparse.ArgumentParser(description="SOT vector indexer")
    parser.add_argument("--sot-dir", required=True, help="SOT 디렉토리")
    parser.add_argument("--collection", default="vamos_sot", help="컬렉션 이름")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=19530)
    args = parser.parse_args()

    index_sot(args.sot_dir, args.collection, args.host, args.port)

if __name__ == "__main__":
    main()
