"""
GPTCache Manager for VAMOS
LLM 응답 시맨틱 캐싱으로 비용 절감 + 속도 향상

사용법:
  python gptcache_manager.py enable
  python gptcache_manager.py disable
  python gptcache_manager.py stats
  python gptcache_manager.py clear
  python gptcache_manager.py query "검색할 질문"
"""

import json
import os
import sys
import argparse
import hashlib
from datetime import datetime

CACHE_DIR = r"D:\VAMOS\.cache\gptcache"
STATS_FILE = os.path.join(CACHE_DIR, "stats.json")
CONFIG_FILE = os.path.join(CACHE_DIR, "config.json")

DEFAULT_CONFIG = {
    "enabled": False,
    "similarity_threshold": 0.92,
    "max_cache_size_mb": 500
}

DEFAULT_STATS = {
    "total_calls": 0,
    "cache_hits": 0,
    "cache_misses": 0,
    "estimated_savings_usd": 0.0
}


def ensure_cache_dir():
    """캐시 디렉토리 생성"""
    os.makedirs(CACHE_DIR, exist_ok=True)


def load_json(path, default):
    """JSON 파일 로드, 없으면 기본값 반환"""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default.copy()


def save_json(path, data):
    """JSON 파일 저장"""
    ensure_cache_dir()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def enable():
    """캐싱 활성화"""
    ensure_cache_dir()
    config = load_json(CONFIG_FILE, DEFAULT_CONFIG)
    config["enabled"] = True
    config["enabled_at"] = datetime.now().isoformat()
    save_json(CONFIG_FILE, config)

    try:
        from gptcache import cache
        from gptcache.embedding import Onnx
        from gptcache.similarity_evaluation import OnnxModelEvaluation

        cache.init(pre_embedding_func=lambda x: x.get("prompt", ""))
        print(json.dumps({
            "status": "enabled",
            "similarity_threshold": config["similarity_threshold"],
            "cache_dir": CACHE_DIR,
            "gptcache_initialized": True
        }, ensure_ascii=False, indent=2))
    except ImportError:
        # gptcache 기본 모드로 초기화
        print(json.dumps({
            "status": "enabled",
            "similarity_threshold": config["similarity_threshold"],
            "cache_dir": CACHE_DIR,
            "gptcache_initialized": False,
            "note": "기본 설정으로 활성화. 고급 임베딩은 추가 패키지 필요."
        }, ensure_ascii=False, indent=2))


def disable():
    """캐싱 비활성화"""
    config = load_json(CONFIG_FILE, DEFAULT_CONFIG)
    config["enabled"] = False
    config["disabled_at"] = datetime.now().isoformat()
    save_json(CONFIG_FILE, config)
    print(json.dumps({"status": "disabled", "cache_preserved": True}, ensure_ascii=False, indent=2))


def stats():
    """통계 조회"""
    config = load_json(CONFIG_FILE, DEFAULT_CONFIG)
    stat = load_json(STATS_FILE, DEFAULT_STATS)

    total = stat["total_calls"]
    hits = stat["cache_hits"]
    hit_rate = f"{(hits / total * 100):.1f}%" if total > 0 else "0%"

    cache_size = 0
    if os.path.exists(CACHE_DIR):
        for f in os.listdir(CACHE_DIR):
            fp = os.path.join(CACHE_DIR, f)
            if os.path.isfile(fp):
                cache_size += os.path.getsize(fp)

    result = {
        "enabled": config.get("enabled", False),
        "total_calls": total,
        "cache_hits": hits,
        "cache_misses": stat["cache_misses"],
        "hit_rate": hit_rate,
        "estimated_savings": f"${stat['estimated_savings_usd']:.2f}",
        "cache_size_mb": round(cache_size / (1024 * 1024), 2),
        "similarity_threshold": config.get("similarity_threshold", 0.92)
    }
    print(json.dumps({"gptcache_stats": result}, ensure_ascii=False, indent=2))


def clear():
    """캐시 초기화"""
    if os.path.exists(CACHE_DIR):
        count = 0
        for f in os.listdir(CACHE_DIR):
            fp = os.path.join(CACHE_DIR, f)
            if os.path.isfile(fp) and f not in ("config.json",):
                os.remove(fp)
                count += 1
        save_json(STATS_FILE, DEFAULT_STATS)
        print(json.dumps({"status": "cleared", "files_removed": count}, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"status": "no_cache_found"}, ensure_ascii=False, indent=2))


def record_call(hit):
    """호출 기록 (다른 스크립트에서 import하여 사용)"""
    stat = load_json(STATS_FILE, DEFAULT_STATS)
    stat["total_calls"] += 1
    if hit:
        stat["cache_hits"] += 1
        stat["estimated_savings_usd"] += 0.003  # 평균 API 호출 비용 추정
    else:
        stat["cache_misses"] += 1
    save_json(STATS_FILE, stat)


def main():
    parser = argparse.ArgumentParser(description="GPTCache Manager for VAMOS")
    parser.add_argument("command", choices=["enable", "disable", "stats", "clear"],
                        help="실행할 명령")
    args = parser.parse_args()

    if args.command == "enable":
        enable()
    elif args.command == "disable":
        disable()
    elif args.command == "stats":
        stats()
    elif args.command == "clear":
        clear()


if __name__ == "__main__":
    main()
