"""
KR-SBERT Embedder for VAMOS
한국어 특화 문장 임베딩 모델 (snunlp/KR-SBERT-V40K-klueNLI-augSTS)
D-22 sot-search / D-24 sot-rag의 임베딩 품질을 한국어 최적화로 업그레이드

사용법:
  python kr_sbert_embedder.py encode "안전 승인 모듈"
  python kr_sbert_embedder.py similarity "모듈 개수" "MODULE_COUNT"
  python kr_sbert_embedder.py batch --input chunks.json --output embeddings.json
"""

import json
import sys
import argparse
import numpy as np
from datetime import datetime

MODEL_NAME = "snunlp/KR-SBERT-V40K-klueNLI-augSTS"
_model = None


def get_model():
    """싱글톤 패턴으로 모델 로드 (최초 1회만)"""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def encode(texts):
    """텍스트 리스트를 벡터로 변환"""
    model = get_model()
    if isinstance(texts, str):
        texts = [texts]
    embeddings = model.encode(texts, normalize_embeddings=True)
    return embeddings


def cosine_similarity(vec_a, vec_b):
    """코사인 유사도 계산"""
    return float(np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b)))


def compute_similarity(text_a, text_b):
    """두 텍스트 간 의미 유사도 계산"""
    embeddings = encode([text_a, text_b])
    return cosine_similarity(embeddings[0], embeddings[1])


def batch_encode(input_path, output_path):
    """JSON 파일의 텍스트를 일괄 임베딩"""
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    texts = [item["text"] for item in data]
    embeddings = encode(texts)

    for i, item in enumerate(data):
        item["embedding"] = embeddings[i].tolist()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return len(data)


def main():
    parser = argparse.ArgumentParser(description="KR-SBERT Embedder for VAMOS")
    subparsers = parser.add_subparsers(dest="command")

    # encode
    enc = subparsers.add_parser("encode", help="텍스트를 벡터로 변환")
    enc.add_argument("text", help="임베딩할 텍스트")

    # similarity
    sim = subparsers.add_parser("similarity", help="두 텍스트 유사도 계산")
    sim.add_argument("text_a", help="텍스트 A")
    sim.add_argument("text_b", help="텍스트 B")

    # batch
    bat = subparsers.add_parser("batch", help="JSON 파일 일괄 임베딩")
    bat.add_argument("--input", required=True, help="입력 JSON 경로")
    bat.add_argument("--output", required=True, help="출력 JSON 경로")

    args = parser.parse_args()

    if args.command == "encode":
        emb = encode(args.text)
        result = {
            "model": MODEL_NAME,
            "dimension": len(emb[0]),
            "text": args.text,
            "embedding_preview": emb[0][:5].tolist()
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "similarity":
        score = compute_similarity(args.text_a, args.text_b)
        result = {
            "model": MODEL_NAME,
            "text_a": args.text_a,
            "text_b": args.text_b,
            "similarity": round(score, 4)
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "batch":
        count = batch_encode(args.input, args.output)
        print(json.dumps({
            "model": MODEL_NAME,
            "processed": count,
            "output": args.output
        }, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
