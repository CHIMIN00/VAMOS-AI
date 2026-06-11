"""
Phase 2-0B 골든셋 v2 재구축 스크립트 (D14 — 실데이터 전환)

v1(scripts/generate_golden_set.py, 합성 템플릿)을 실제 데이터셋으로 전량 교체한다.

원본 데이터 (라이선스 검증 2026-06-11):
  - MMLU:      cais/mmlu HF test split parquet (14,042문항, 57과목) — MIT (hendrycks/test)
  - HumanEval: openai/human-eval HumanEval.jsonl.gz (164문항) — MIT
  - MBPP:      google-research sanitized-mbpp.json (427문항) — CC BY 4.0 (HF google/mbpp card)
  - LogicKor:  instructkr/LogicKor questions.jsonl (42문항 전수) — CC BY-SA 4.0
               (원저자 maywell HF 정식 업로드 maywell/LogicKor, DOI 10.57967/hf/2440)

층화 추출 (R-18-1: seed=42 고정, 재현 가능):
  - MMLU 50:      57과목 중 50과목 무작위 선택(정렬 후 sample) → 과목당 1문항
  - HumanEval 20: 난이도 7 easy / 7 medium / 6 hard
  - MBPP 50:      난이도 17 easy / 17 medium / 16 hard (test_list 3개 항목으로 한정 — §A-3 채점 포맷)
  - LogicKor 42:  전수 (실측 42 = 6카테고리 × 7문항 — 명세 '50 전수'는 합성 가정치였음, 편차 기록)

난이도 PROXY (원본에 난이도 라벨 부재 — 결정론적 대리 지표, 문서화):
  - MMLU:      question 문자 길이 오름차순 3분위 (17/17/16)
  - HumanEval: canonical_solution 비공백 라인 수 오름차순 3분위
  - MBPP:      code 비공백 라인 수 오름차순 3분위
  - LogicKor:  turn-1 question 문자 길이 오름차순 3분위 (14/14/14)

실행: python scripts/rebuild_golden_set_v2.py
"""

import gzip
import hashlib
import json
import os
import random

rng = random.Random(42)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "benchmarks", "golden_set")
RAW = os.environ.get("GOLDEN_RAW_DIR", r"C:\tmp\golden_raw")
TODAY = "2026-06-11"
VERSION = "v2"


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def tertile_difficulty(values):
    """값 오름차순 3분위 → easy/medium/hard. 동률은 원 인덱스 순. 분할 17/17/16 형태."""
    n = len(values)
    order = sorted(range(n), key=lambda i: (values[i], i))
    cut1 = (n + 2) // 3          # ceil(n/3)
    cut2 = cut1 + (n + 1) // 3   # + ceil((n - cut1) / 2) 근사 — 아래 보정
    cut2 = cut1 + ((n - cut1) + 1) // 2
    diff = [None] * n
    for rank, idx in enumerate(order):
        diff[idx] = "easy" if rank < cut1 else ("medium" if rank < cut2 else "hard")
    return diff


# ============================================================
# 1. MMLU 50 — 실제 cais/mmlu test split, 과목 층화 (50/57, 과목당 1)
# ============================================================
import pandas as pd  # noqa: E402

df = pd.read_parquet(os.path.join(RAW, "mmlu_test.parquet"))
assert len(df) == 14042, f"MMLU rows {len(df)} != 14042"
subjects_all = sorted(df["subject"].unique().tolist())
assert len(subjects_all) == 57, f"MMLU subjects {len(subjects_all)} != 57"

selected_subjects = sorted(rng.sample(subjects_all, 50))
ANSWERS = ["A", "B", "C", "D"]

mmlu_rows = []
for subj in selected_subjects:
    sub_df = df[df["subject"] == subj]
    row_pos = rng.randrange(len(sub_df))
    row = sub_df.iloc[row_pos]
    mmlu_rows.append((subj, int(sub_df.index[row_pos]), row))

mmlu_difficulty = tertile_difficulty([len(str(r[2]["question"])) for r in mmlu_rows])

mmlu_items, mmlu_meta = [], []
for idx, (subj, src_idx, row) in enumerate(mmlu_rows):
    q = str(row["question"]).strip()
    choices = [str(c) for c in row["choices"]]
    assert len(choices) == 4
    answer = ANSWERS[int(row["answer"])]
    subj_label = subj.replace("_", " ")
    item = {
        "item_id": f"mmlu_{idx+1:03d}",
        "question": q,
        "choices": {k: v for k, v in zip(ANSWERS, choices)},
        "answer": answer,
        "subject": subj,
        "prompt": (
            f"The following is a multiple choice question about {subj_label}.\n\n"
            f"{q}\n"
            f"A. {choices[0]}\nB. {choices[1]}\nC. {choices[2]}\nD. {choices[3]}\n\n"
            f"Answer:"
        ),
    }
    mmlu_items.append(item)
    mmlu_meta.append({
        "item_id": f"mmlu_{idx+1:03d}",
        "benchmark": "mmlu",
        "difficulty": mmlu_difficulty[idx],
        "category": subj,
        "source": f"mmlu/{subj}/test_row_{src_idx}",
        "golden_version": VERSION,
        "added_date": TODAY,
    })

# ============================================================
# 2. HumanEval 20 — 실제 164문항, 난이도 7/7/6 (solution 라인 수 3분위)
# ============================================================
with gzip.open(os.path.join(RAW, "HumanEval.jsonl.gz"), "rt", encoding="utf-8") as f:
    he_all = [json.loads(line) for line in f if line.strip()]
assert len(he_all) == 164, f"HumanEval {len(he_all)} != 164"
he_all.sort(key=lambda x: int(x["task_id"].split("/")[1]))

he_diff_all = tertile_difficulty(
    [sum(1 for ln in x["canonical_solution"].splitlines() if ln.strip()) for x in he_all]
)
he_strata = {"easy": [], "medium": [], "hard": []}
for i, x in enumerate(he_all):
    he_strata[he_diff_all[i]].append(i)
he_pick = (
    sorted(rng.sample(he_strata["easy"], 7))
    + sorted(rng.sample(he_strata["medium"], 7))
    + sorted(rng.sample(he_strata["hard"], 6))
)
he_pick_sorted = sorted(he_pick)  # 최종 정렬: task_id 순

humaneval_items, humaneval_meta = [], []
for idx, i in enumerate(he_pick_sorted):
    x = he_all[i]
    item = {
        "item_id": f"humaneval_{idx+1:03d}",
        "task_id": x["task_id"],
        "question": f"Complete the Python function `{x['entry_point']}` to satisfy its docstring.",
        "prompt": x["prompt"],
        "canonical_solution": x["canonical_solution"],
        "test": x["test"],
        "entry_point": x["entry_point"],
        "answer": x["canonical_solution"],
    }
    humaneval_items.append(item)
    humaneval_meta.append({
        "item_id": f"humaneval_{idx+1:03d}",
        "benchmark": "humaneval",
        "difficulty": he_diff_all[i],
        "category": "python_function",
        "source": f"humaneval/{x['task_id']}",
        "golden_version": VERSION,
        "added_date": TODAY,
    })

# ============================================================
# 3. MBPP 50 — sanitized 427 중 test_list==3 (397) 한정, 17/17/16
# ============================================================
with open(os.path.join(RAW, "sanitized-mbpp.json"), encoding="utf-8") as f:
    mbpp_all = json.load(f)
assert len(mbpp_all) == 427, f"MBPP sanitized {len(mbpp_all)} != 427"
mbpp_cand = [x for x in mbpp_all if len(x["test_list"]) == 3]
mbpp_cand.sort(key=lambda x: int(x["task_id"]))

mbpp_diff_all = tertile_difficulty(
    [sum(1 for ln in x["code"].splitlines() if ln.strip()) for x in mbpp_cand]
)
mbpp_strata = {"easy": [], "medium": [], "hard": []}
for i, x in enumerate(mbpp_cand):
    mbpp_strata[mbpp_diff_all[i]].append(i)
mbpp_pick = (
    sorted(rng.sample(mbpp_strata["easy"], 17))
    + sorted(rng.sample(mbpp_strata["medium"], 17))
    + sorted(rng.sample(mbpp_strata["hard"], 16))
)
mbpp_pick_sorted = sorted(mbpp_pick)

mbpp_items, mbpp_meta = [], []
for idx, i in enumerate(mbpp_pick_sorted):
    x = mbpp_cand[i]
    text = x["prompt"].strip()
    item = {
        "item_id": f"mbpp_{idx+1:03d}",
        "task_id": int(x["task_id"]),
        "question": text,
        "text": text,
        "prompt": f'"""{text}\n{x["test_list"][0]}\n"""',
        "code": x["code"],
        "test_list": x["test_list"],
        "answer": x["code"],
    }
    mbpp_items.append(item)
    mbpp_meta.append({
        "item_id": f"mbpp_{idx+1:03d}",
        "benchmark": "mbpp",
        "difficulty": mbpp_diff_all[i],
        "category": "python_programming",
        "source": f"mbpp/sanitized/{x['task_id']}",
        "golden_version": VERSION,
        "added_date": TODAY,
    })

# ============================================================
# 4. LogicKor 42 전수 — 실측 42 (6카테고리 × 7) · turn-1 채점, turn-2 보존
# ============================================================
with open(os.path.join(RAW, "logickor_questions.jsonl"), encoding="utf-8") as f:
    lk_all = [json.loads(line) for line in f if line.strip()]
assert len(lk_all) == 42, f"LogicKor {len(lk_all)} != 42 (전수 실측)"
lk_all.sort(key=lambda x: int(x["id"]))

lk_difficulty = tertile_difficulty([len(x["questions"][0]) for x in lk_all])

logickor_items, logickor_meta = [], []
for idx, x in enumerate(lk_all):
    q1, q2 = x["questions"][0], x["questions"][1]
    r1 = x["references"][0] if x.get("references") else None
    r2 = x["references"][1] if x.get("references") and len(x["references"]) > 1 else None
    item = {
        "item_id": f"logickor_{idx+1:03d}",
        "question": q1,
        "category": x["category"],
        "subcategory": "turn_1",
        "reference_answer": r1 if r1 is not None else "",
        "scoring_criteria": {
            "accuracy_weight": 0.4,
            "logic_weight": 0.3,
            "completeness_weight": 0.3,
        },
        "prompt": f"다음 문제에 대해 정확하고 논리적으로 답변해 주세요.\n\n{q1}",
        "answer": r1 if r1 is not None else "",
        "question_turn2": q2,
        "reference_answer_turn2": r2 if r2 is not None else "",
        "reference_status": "provided" if r1 is not None else "judge_only",
    }
    logickor_items.append(item)
    logickor_meta.append({
        "item_id": f"logickor_{idx+1:03d}",
        "benchmark": "logickor",
        "difficulty": lk_difficulty[idx],
        "category": f"{x['category']}/turn_1",
        "source": f"logickor/{x['id']}",
        "golden_version": VERSION,
        "added_date": TODAY,
    })

TOTAL = len(mmlu_items) + len(humaneval_items) + len(mbpp_items) + len(logickor_items)

# ============================================================
# 5. 파일 저장
# ============================================================
for subdir in ["mmlu", "humaneval", "mbpp", "logickor"]:
    os.makedirs(os.path.join(BASE, subdir), exist_ok=True)

write_json(os.path.join(BASE, "mmlu", "items.json"), mmlu_items)
write_json(os.path.join(BASE, "mmlu", "metadata.json"), mmlu_meta)
write_json(os.path.join(BASE, "humaneval", "items.json"), humaneval_items)
write_json(os.path.join(BASE, "humaneval", "metadata.json"), humaneval_meta)
write_json(os.path.join(BASE, "mbpp", "items.json"), mbpp_items)
write_json(os.path.join(BASE, "mbpp", "metadata.json"), mbpp_meta)
write_json(os.path.join(BASE, "logickor", "items.json"), logickor_items)
write_json(os.path.join(BASE, "logickor", "metadata.json"), logickor_meta)

# ============================================================
# 6. contamination_check v2 — 해시 중복 + 5-gram 중복률 (셋 내부 교차)
# ============================================================
all_texts, hash_map = [], {"mmlu": [], "humaneval": [], "mbpp": [], "logickor": []}
for bench, items in [("mmlu", mmlu_items), ("humaneval", humaneval_items),
                     ("mbpp", mbpp_items), ("logickor", logickor_items)]:
    for item in items:
        text = item.get("question", "") + item.get("prompt", "")
        all_texts.append(text)
        hash_map[bench].append(hashlib.sha256(text.encode()).hexdigest())

all_hashes = [h for b in ["mmlu", "humaneval", "mbpp", "logickor"] for h in hash_map[b]]
dup_count = len(all_hashes) - len(set(all_hashes))


def fivegrams(text):
    toks = text.split()
    return set(tuple(toks[i:i + 5]) for i in range(max(0, len(toks) - 4)))


gram_sets = [fivegrams(t) for t in all_texts]
max_overlap, overlap_items = 0.0, 0
for i in range(len(gram_sets)):
    if not gram_sets[i]:
        continue
    for j in range(i + 1, len(gram_sets)):
        if not gram_sets[j]:
            continue
        inter = len(gram_sets[i] & gram_sets[j])
        rate = inter / min(len(gram_sets[i]), len(gram_sets[j]))
        if rate > max_overlap:
            max_overlap = rate
        if rate > 0.5:
            overlap_items += 1

contamination = {
    "check_date": TODAY,
    "check_method": {
        "hash_comparison": "SHA-256 해시 비교 (문항 텍스트 = question + prompt)",
        "ngram_analysis": "5-gram 중복률 분석 (골든셋 내부 전쌍 교차)",
        "threshold": "5-gram 중복률 > 50% 시 오염 판정",
    },
    "target_models": [
        "VAMOS AI v1 (학습 데이터 미확정 — 배포 전 재검사 필요)"
    ],
    "results": {
        "total_items_checked": TOTAL,
        "hash_duplicates_found": dup_count,
        "ngram_overlap_items": overlap_items,
        "ngram_max_overlap_rate": round(max_overlap, 4),
        "contaminated_items": [],
        "verdict": "PASS" if dup_count == 0 and overlap_items == 0 else "FAIL",
    },
    "item_hashes": hash_map,
    "notes": (
        "v2 실데이터 재검사 (2026-06-11). 공개 벤치마크 원본이므로 대상 모델(API LLM)의 "
        "사전학습 노출 가능성은 상존 — 모델 학습 데이터 확정 후 재검사 필수 (W-01 절차). "
        "분기별 교체 시마다 재실행."
    ),
}
write_json(os.path.join(BASE, "contamination_check.json"), contamination)

# ============================================================
# 7. manifest v2 — data_status 실데이터 전환 + change_log v2
# ============================================================
with open(os.path.join(BASE, "manifest.json"), encoding="utf-8") as f:
    prev_manifest = json.load(f)
# 멱등성: 재실행 시 v2 entry 중복 append 방지 (v2 이전 이력만 보존)
prev_log = [e for e in prev_manifest.get("change_log", []) if e.get("version") != "v2"]

manifest = {
    "golden_set_version": "v2",
    "created_date": TODAY,
    "created_by": "Phase 2-0B 골든셋 v2 재구축 (scripts/rebuild_golden_set_v2.py — D14 실데이터 전환)",
    "data_status": (
        "REAL_DATA — 4개 벤치마크 전체가 실제 공개 데이터셋에서 층화 추출됨 (2026-06-11, D14 선행과업 완료). "
        "합성 placeholder 전량 교체. LOCK-BE-01/02/03 게이트 판정에 유효 (VALID_FOR_GATES)"
    ),
    "seed": 42,
    "total_items": TOTAL,
    "benchmarks": {
        "mmlu": {
            "items_count": len(mmlu_items),
            "source": "cais/mmlu (HuggingFace) test split 14,042문항 — 57과목 중 50과목 층화, 과목당 1문항",
            "license": "MIT (hendrycks/test)",
            "sampling_method": "stratified (50/57 subjects, 1 per subject, seed=42); difficulty=question-length tertile PROXY",
            "items_sha256": file_sha256(os.path.join(BASE, "mmlu", "items.json")),
            "metadata_sha256": file_sha256(os.path.join(BASE, "mmlu", "metadata.json")),
        },
        "humaneval": {
            "items_count": len(humaneval_items),
            "source": "openai/human-eval HumanEval.jsonl.gz 164문항 — 난이도 3분위 층화 20문항",
            "license": "MIT",
            "sampling_method": "difficulty-stratified (7 easy, 7 medium, 6 hard, seed=42); difficulty=solution-line tertile PROXY",
            "items_sha256": file_sha256(os.path.join(BASE, "humaneval", "items.json")),
            "metadata_sha256": file_sha256(os.path.join(BASE, "humaneval", "metadata.json")),
        },
        "mbpp": {
            "items_count": len(mbpp_items),
            "source": "google-research sanitized-mbpp.json 427문항 — test_list 3개 한정(397) 후 난이도 층화 50문항",
            "license": "CC BY 4.0 (HF google/mbpp card; repo Apache-2.0)",
            "sampling_method": "difficulty-stratified (17 easy, 17 medium, 16 hard, seed=42); difficulty=code-line tertile PROXY",
            "items_sha256": file_sha256(os.path.join(BASE, "mbpp", "items.json")),
            "metadata_sha256": file_sha256(os.path.join(BASE, "mbpp", "metadata.json")),
        },
        "logickor": {
            "items_count": len(logickor_items),
            "source": (
                "instructkr/LogicKor questions.jsonl 전수 — 실측 42문항(6카테고리 × 7, 각 2턴; turn-1 채점 대상, "
                "turn-2 본문 보존). ⚠️ 편차 기록: 구 명세 '50 전수'는 합성 v1 가정치 — 실제 전수=42"
            ),
            "license": "CC BY-SA 4.0 (maywell/LogicKor HF, DOI 10.57967/hf/2440)",
            "sampling_method": "full (all 42 items, seed 불요); difficulty=question-length tertile PROXY",
            "items_sha256": file_sha256(os.path.join(BASE, "logickor", "items.json")),
            "metadata_sha256": file_sha256(os.path.join(BASE, "logickor", "metadata.json")),
        },
    },
    "raw_source_sha256": {
        "mmlu_test.parquet": file_sha256(os.path.join(RAW, "mmlu_test.parquet")),
        "HumanEval.jsonl.gz": file_sha256(os.path.join(RAW, "HumanEval.jsonl.gz")),
        "sanitized-mbpp.json": file_sha256(os.path.join(RAW, "sanitized-mbpp.json")),
        "logickor_questions.jsonl": file_sha256(os.path.join(RAW, "logickor_questions.jsonl")),
    },
    "governance": {
        "R-18-1": "seed=42 고정, 층화 추출 재현 가능 (rebuild_golden_set_v2.py 재실행 = 동일 결과)",
        "R-18-4": "Git LFS + 암호화, 접근 권한 제한, 분기별 갱신 기록",
    },
    "next_update": (
        "Phase 2+ — ARC-AGI 30문항 추가 + 분기별 20% 교체(LOCK-BE 게이트 절차). "
        "LogicKor 정본 갱신 시 전수 동기화"
    ),
    "change_log": prev_log + [
        {
            "version": "v2",
            "date": TODAY,
            "action": "실데이터 재구축 (D14 Phase 2-0 선행과업)",
            "items_added": TOTAL,
            "items_removed": 170,
            "description": (
                "합성 placeholder 170문항 전량 제거 → 실데이터 162문항 재구축: "
                "MMLU 50(실제 cais/mmlu, 50과목 층화) + HumanEval 20(실제 164→7/7/6) + "
                "MBPP 50(실제 sanitized 427→17/17/16) + LogicKor 42(실제 전수 — 명세 50은 "
                "합성 가정치, 실측 42로 편차 기록). 라이선스 4종 검증 완료. SHA 재계산 + "
                "contamination_check 재수행. data_status SYNTHETIC_PLACEHOLDER 해제 → "
                "REAL_DATA(VALID_FOR_GATES) — LOCK-BE-01/02 게이트 유효화"
            ),
        }
    ],
}
write_json(os.path.join(BASE, "manifest.json"), manifest)

# ============================================================
# 8. 스모크 서브셋 v2 재생성 (F-06 동일 방법, seed=42)
# ============================================================
rng_smoke = random.Random(42)
mmlu_smoke_idx = sorted(rng_smoke.sample(range(len(mmlu_items)), 10))
he_by_diff = {"easy": [], "medium": [], "hard": []}
for i, m in enumerate(humaneval_meta):
    he_by_diff[m["difficulty"]].append(i)
he_smoke_idx = sorted(
    rng_smoke.sample(he_by_diff["easy"], 4)
    + rng_smoke.sample(he_by_diff["medium"], 3)
    + rng_smoke.sample(he_by_diff["hard"], 3)
)

smoke_mmlu = [mmlu_items[i] for i in mmlu_smoke_idx]
smoke_he = [humaneval_items[i] for i in he_smoke_idx]
write_json(os.path.join(BASE, "smoke", "mmlu_items.json"), smoke_mmlu)
write_json(os.path.join(BASE, "smoke", "humaneval_items.json"), smoke_he)

smoke_benchmarks = {
    "mmlu": {
        "count": 10,
        "method": "과목(category) 균등 추출 — 50과목 중 10과목 선택, 각 1문항",
        "item_ids": [mmlu_items[i]["item_id"] for i in mmlu_smoke_idx],
        "details": [
            {"item_id": mmlu_meta[i]["item_id"], "category": mmlu_meta[i]["category"],
             "difficulty": mmlu_meta[i]["difficulty"]}
            for i in mmlu_smoke_idx
        ],
    },
    "humaneval": {
        "count": 10,
        "method": "난이도(difficulty) 비율 보존 추출 — easy 4 + medium 3 + hard 3",
        "item_ids": [humaneval_items[i]["item_id"] for i in he_smoke_idx],
        "details": [
            {"item_id": humaneval_meta[i]["item_id"], "difficulty": humaneval_meta[i]["difficulty"]}
            for i in he_smoke_idx
        ],
    },
}
smoke_subset = {
    "smoke_subset_version": "v2",
    "created_date": TODAY,
    "created_by": "Phase 2-0B 골든셋 v2 재구축 — rebuild_golden_set_v2.py (F-06 방법 동일 재생성)",
    "seed": 42,
    "total_items": 20,
    "selection_method": "stratified sampling (seed-deterministic)",
    "benchmarks": smoke_benchmarks,
    "governance": {
        "R-18-1": "seed=42 고정, 동일 골든셋에서 동일 서브셋 재현 보장",
        "R-18-4": "item_id만 저장, 정답 데이터 미포함 (오염 방지)",
    },
    "sot_references": [
        "S7G-072 (promptfoo CI 통합)",
        "S7G-078 (골든 데이터셋 관리)",
        "T-025 (골든셋 스모크 테스트)",
    ],
    "content_sha256": hashlib.sha256(
        json.dumps(smoke_benchmarks, ensure_ascii=False, sort_keys=True).encode()
    ).hexdigest(),
}
write_json(os.path.join(BASE, "smoke_subset.json"), smoke_subset)

# ============================================================
# 결과 요약
# ============================================================
print("=== Phase 2-0B 골든셋 v2 재구축 완료 (실데이터) ===")
print(f"MMLU:      {len(mmlu_items)} 문항 ({len(selected_subjects)} 과목)")
print(f"HumanEval: {len(humaneval_items)} 문항 (7/7/6)")
print(f"MBPP:      {len(mbpp_items)} 문항 (17/17/16, test_list==3 한정 {len(mbpp_cand)} 후보)")
print(f"LogicKor:  {len(logickor_items)} 문항 (전수 42 — 편차 기록)")
print(f"합계:      {TOTAL} 문항 (v1 170 → v2 {TOTAL})")
print(f"오염 검사:  hash dup={dup_count}, 5-gram>50%={overlap_items}, max_rate={max_overlap:.4f}")
print(f"스모크:     mmlu 10 + humaneval 10 재생성")
