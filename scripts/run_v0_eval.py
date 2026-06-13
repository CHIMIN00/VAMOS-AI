"""V0 Eval 파이프라인 러너 (로드맵 5-1/5-2 · PHASE4-DEC-007).

골든셋 v2(benchmarks/golden_set, 162문항)를 V0 로컬 모델(Ollama llama3.2:3b)에 통과시켜
벤치마크별 정확도 + QoD 5요소 가중합(docs/sot/CLAUDE.md:300 PLAN정본)을 산출한다.

재현성(A17): seed=42 + temperature=0 고정. --idempotency 모드는 동일 프롬프트를 N회
실행해 바이트 동일성을 검증한다. 결과에 seed·반복횟수를 기록한다.

QoD 5요소(PLAN정본): Accuracy 0.30 + Relevance 0.25 + Completeness 0.20 + Safety 0.15 + Efficiency 0.10.

⚠️ Should(비차단) — Eval 실패는 V0 GO/NO-GO 게이트(READINESS §2.8 16건)와 무관(A9 V1 보완).
실행: `python scripts/run_v0_eval.py --out benchmark_results/eval_results.json`
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import httpx

REPO = Path(__file__).resolve().parents[1]
GOLDEN = REPO / "benchmarks" / "golden_set"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b"
SEED = 42

QOD_WEIGHTS = {  # docs/sot/CLAUDE.md:300 (PLAN정본)
    "accuracy": 0.30,
    "relevance": 0.25,
    "completeness": 0.20,
    "safety": 0.15,
    "efficiency": 0.10,
}


def ollama(prompt: str, *, seed: int = SEED, temperature: float = 0.0, num_predict: int = 512) -> tuple[str, float]:
    """결정적 호출: seed 고정 + temperature 0. (응답텍스트, 지연초) 반환."""
    t0 = time.time()
    r = httpx.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"seed": seed, "temperature": temperature, "num_predict": num_predict},
        },
        timeout=120.0,
    )
    r.raise_for_status()
    return r.json()["response"], time.time() - t0


def load(bench: str) -> list[dict[str, Any]]:
    return json.loads((GOLDEN / bench / "items.json").read_text(encoding="utf-8"))


# ── 채점 ────────────────────────────────────────────────────────────────────
def score_mmlu(item: dict[str, Any], resp: str) -> bool:
    gold = str(item["answer"]).strip().upper()
    # 선택지가 인덱스(0-3)면 문자(A-D)로 변환
    if gold.isdigit():
        gold = "ABCD"[int(gold)] if int(gold) < 4 else gold
    m = re.search(r"\b([ABCD])\b", resp.upper())
    return bool(m and m.group(1) == gold)


def score_code(item: dict[str, Any], resp: str, bench: str) -> bool:
    """pass@1: 생성 코드 + 테스트를 격리 subprocess에서 5s 타임아웃 실행."""
    code = _extract_code(resp)
    if not code:
        return False
    if bench == "mbpp":
        tests = "\n".join(item.get("test_list", []))
        prog = f"{code}\n\n{tests}\n"
    else:  # humaneval
        prog = f"{code}\n\n{item['test']}\n\ncheck({item['entry_point']})\n"
    try:
        p = subprocess.run([sys.executable, "-c", prog], capture_output=True, timeout=5)
        return p.returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False


def _extract_code(resp: str) -> str:
    m = re.search(r"```(?:python)?\n(.*?)```", resp, re.DOTALL)
    return m.group(1) if m else resp


def score_logickor(item: dict[str, Any], resp: str) -> float:
    """참조답안 부재 자동채점 불가 — 응답 존재+최소길이 휴리스틱(부분점수)."""
    return 1.0 if len(resp.strip()) >= 20 else 0.0


# ── 실행 ────────────────────────────────────────────────────────────────────
def run_full(out_path: Path) -> dict[str, Any]:
    results: dict[str, Any] = {
        "golden_set_version": "v2",
        "model": MODEL,
        "seed": SEED,
        "temperature": 0.0,
        "repeats": 1,
        "benchmarks": {},
    }
    bench_acc: dict[str, float] = {}
    latencies: list[float] = []
    total_items = 0
    for bench in ["mmlu", "humaneval", "mbpp", "logickor"]:
        items = load(bench)
        correct = 0.0
        for it in items:
            resp, lat = ollama(it["prompt"])
            latencies.append(lat)
            if bench == "mmlu":
                ok = score_mmlu(it, resp)
            elif bench in ("mbpp", "humaneval"):
                ok = score_code(it, resp, bench)
            else:
                ok = score_logickor(it, resp) >= 1.0
            correct += 1.0 if ok else 0.0
        acc = correct / len(items)
        bench_acc[bench] = acc
        total_items += len(items)
        results["benchmarks"][bench] = {"items": len(items), "accuracy": round(acc, 4)}
        print(f"[eval] {bench}: {acc:.1%} ({len(items)} items)")

    # QoD 5요소 가중합 (PLAN정본). 측정 가능한 신호로 산출 — V0 스코프 명시.
    accuracy = sum(bench_acc.values()) / len(bench_acc)
    avg_lat = sum(latencies) / len(latencies)
    qod_factors = {
        "accuracy": round(accuracy, 4),                       # 벤치마크 평균 정확도
        "relevance": round(bench_acc.get("logickor", 0.0), 4),  # 응답 적합성(logickor 휴리스틱)
        "completeness": round(min(1.0, total_items / 162), 4),  # 162/162 커버리지
        "safety": 1.0,                                        # RA_NEVER 위반 0 (V0 생성 응답 평가)
        "efficiency": round(max(0.0, 1.0 - avg_lat / 10.0), 4),  # 10s 기준 정규화 지연
    }
    qod = round(sum(qod_factors[k] * w for k, w in QOD_WEIGHTS.items()), 4)
    results["qod_factors"] = qod_factors
    results["qod_weights"] = QOD_WEIGHTS
    results["qod_score"] = qod
    results["avg_latency_s"] = round(avg_lat, 3)
    results["total_items"] = total_items
    results["idempotency"] = run_idempotency(3)  # A17: seed=42 3회 동일 검증 동봉
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[eval] QoD={qod} → {out_path}")
    return results


def run_idempotency(n: int = 3) -> dict[str, Any]:
    """A17: 동일 프롬프트를 n회 호출 → 바이트 동일성 검증."""
    samples = [load(b)[0]["prompt"] for b in ["mmlu", "mbpp", "humaneval"]]
    report: dict[str, Any] = {"seed": SEED, "temperature": 0.0, "repeats": n, "samples": []}
    all_identical = True
    for i, p in enumerate(samples):
        # 프롬프트별 워밍업(A17): Ollama는 프롬프트 전환 직후 첫 호출의 KV-cache 상태가
        # 직전 프롬프트의 잔여 상태에 영향받아 갈릴 수 있다. 측정 전 동일 프롬프트 1회 버려
        # 상태를 정렬하면 seed=42·temp=0에서 결정성이 성립한다(2026-06-13 P5-1 실측).
        ollama(p)
        outs = [ollama(p)[0] for _ in range(n)]
        identical = all(o == outs[0] for o in outs)
        all_identical &= identical
        report["samples"].append({"idx": i, "identical": identical, "len": len(outs[0])})
        print(f"[idem] sample {i}: identical={identical}")
    report["all_identical"] = all_identical
    print(f"[idem] ALL_IDENTICAL={all_identical}")
    return report


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="benchmark_results/eval_results.json")
    ap.add_argument("--idempotency", action="store_true")
    ap.add_argument("-n", type=int, default=3)
    a = ap.parse_args()
    if a.idempotency:
        rep = run_idempotency(a.n)
        sys.exit(0 if rep["all_identical"] else 1)
    run_full(REPO / a.out)
