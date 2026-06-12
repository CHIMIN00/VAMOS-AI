# P4-0 STEP 7 적대 라운드 R1 발견 정정 (PART2 잔존 6건 — CRLF 보존, 카운트 assert)
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
PATH = r"D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md"
with io.open(PATH, "r", encoding="utf-8", newline="") as f:
    text = f.read()
orig_cr = text.count("\r")

EDITS = [
    # 1. seed 트리 주석 (L530)
    ("├── decision_schema.json        # DecisionSchema 18필드 (14필수+4선택) — D2.1-D2 §4.1 FREEZE",
     "├── decision_schema.json        # DecisionSchema 20필드 (16필수+4선택) — D2.1-D2 §4.1 FREEZE 18 + DEC-010 confidence 2", 1),
    # 2. 약기 #11 CostBudget → D2.1-D7 §4.3 SOT 실필드
    ("| 11 | CostBudget | budget_id(str), daily_limit(int), monthly_limit(int), current_daily/monthly(float), warn_threshold(int), escalate_threshold(int), block_threshold(int), last_updated(datetime) |",
     "| 11 | CostBudget | budget_id(str), mode(V1\\|V2\\|V3), daily_limit(int), monthly_limit(int), used_today(int), used_month(int), forecast(number?), actual(number?), block_on_exceed(bool?) — **D2.1-D7 §4.3 정본**(threshold 필드 없음 — 게이트 임계는 DownshiftSchema, PHASE4-DEC-002) |", 1),
    # 3. 약기 #12 Downshift → D2.1-D7 §4.4 SOT 실필드
    ("| 12 | DownshiftSchema | from_model(str), to_model(str), reason(Enum), cost_saved(float), quality_delta(float), triggered_at(datetime) |",
     "| 12 | DownshiftSchema | warn_threshold_percent(int=80 LOCK), block_threshold_percent(int=100 LOCK), trigger_type(daily\\|monthly), near_action(warn\\|force_mini), exceed_action(block), main_requires_approval(bool) — **D2.1-D7 §4.4 정본** |", 1),
    # 4. 참조 문서 리스트 (L817)
    ("- **D2.1-D2 §4.1** (DecisionSchema 18필드 FREEZE 정본)",
     "- **D2.1-D2 §4.1** (DecisionSchema FREEZE 18필드 정본 + PHASE3-DEC-010 confidence 2 = 20)", 1),
    # 5. XREF-V0-18 주석 (L1346)
    ("<!-- NOTE (XREF-V0-18): V0는 B4 17섹션 중 13섹션만 활성. [blue_nodes],[ui],[rate_limit],[guardrails]는 V1+ 에서 추가. memory TTL은 [storage]에 포함 (별도 [memory] 섹션 없음). -->",
     "<!-- NOTE (XREF-V0-18): V0는 B4 17섹션 중 13섹션 + [confidence](DEC-010) = 14섹션 활성. [blue_nodes],[ui],[rate_limit],[guardrails]는 V1+ 에서 추가. memory TTL은 [storage]에 포함 (별도 [memory] 섹션 없음). (PHASE4-DEC-003) -->", 1),
    # 6. V2 구간 (L2827)
    ("- 13섹션 구조 유지 + V2 전용 키 추가:",
     "- 14섹션 구조(13+[confidence], PHASE4-DEC-003) 유지 + V2 전용 키 추가:", 1),
]

failures = []
for old, new, expected in EDITS:
    n = text.count(old)
    if n != expected:
        failures.append((old[:70], expected, n))
        continue
    text = text.replace(old, new)

if failures:
    print("❌ 치환 횟수 불일치 — 미기록 중단:")
    for o, e, n in failures:
        print(f"  기대 {e} != 실제 {n} :: {o}")
    sys.exit(1)

with io.open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write(text)
print(f"✅ R2 6건 치환 완료. CR {orig_cr} → {text.count(chr(13))} / LF {text.count(chr(10))}")
