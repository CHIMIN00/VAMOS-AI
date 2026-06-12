"""P4-0 STEP 6a — schemas/seed/ 5종 생성 (SOT 정본 기계 추출, 창작 0).

추출원:
  decision_schema.json   ← D2.1-D2 §4.1 JSON 블록 (18필드) + PHASE3-DEC-010 confidence 2필드 = 20
  response_envelope.json ← CLAUDE.md §12 (5필드 LOCK — 본 스크립트 내 verbatim 전사)
  intent_frame.json      ← D2.0-02 I-1 상세 출력(L2632~2648 — 10필드, verbatim 전사)
  evidence_pack.json     ← D2.0-02 I-2 상세 출력(L2698~2709 — 6필드, verbatim 전사)
  registries.json        ← D2.1-D2 §5 JSON 블록 (EventType 123 / FailureCode 36 / Fallback 23 — 기계 파싱)

검증: 추출 카운트 != 기대 분모 → 비zero exit (§1.3.1 #1 — 임의 가감 금지).
사용: python scripts/extract_seeds.py
"""

import io
import json
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).resolve().parent.parent
D2 = ROOT / "docs" / "sot" / "D2.1-D2_D2_SCHEMA_ORANGE_CORE.md"
SEED = ROOT / "schemas" / "seed"
SEED.mkdir(parents=True, exist_ok=True)

text = io.open(D2, encoding="utf-8").read()
json_blocks = [m.group(1) for m in re.finditer(r"```json\n(.*?)```", text, re.DOTALL)]
parsed = []
for b in json_blocks:
    try:
        parsed.append(json.loads(b))
    except json.JSONDecodeError:
        continue


def find_schema(name: str) -> dict:
    for p in parsed:
        if isinstance(p, dict) and p.get("_meta", {}).get("schema_name") == name:
            return p
    raise SystemExit(f"FATAL: {name} JSON 블록 미발견 (D2.1-D2)")


def find_registry(name: str) -> dict:
    for p in parsed:
        if isinstance(p, dict) and p.get("registry") == name:
            return p
    raise SystemExit(f"FATAL: {name} 레지스트리 블록 미발견 (D2.1-D2)")


def check(label: str, actual: int, expected: int) -> None:
    if actual != expected:
        raise SystemExit(f"FATAL [§1.3.1 #1]: {label} 카운트 불일치 — 기대 {expected} != 실측 {actual}. 즉시 중단.")
    print(f"  {label}: {actual} == {expected} OK")


def write_seed(fname: str, obj: dict) -> None:
    path = SEED / fname
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"  → {path.relative_to(ROOT)}")


# ── 1. decision_schema.json — D2.1-D2 §4.1 기계 추출 + DEC-010 2필드 ──
dec = find_schema("DecisionSchema")
base_fields = dec["fields"]
check("DecisionSchema D2.1-D2 원본", len(base_fields), 18)
confidence_fields = [
    {
        "name": "confidence_score",
        "type": "number",
        "required": True,
        "example": 0.91,
        "description": "예측 신뢰도 산출값 0.0~1.0 (PHASE3-DEC-010 신규 — A25)",
    },
    {
        "name": "confidence_level",
        "type": "enum",
        "required": True,
        "example": "HIGH",
        "description": "임계값 적용 결과. 값: HIGH | MEDIUM | LOW | REFUSE (PHASE3-DEC-010 — 0.85/0.60/0.30 LOCK)",
    },
]
all_fields = base_fields + confidence_fields
check("DecisionSchema 확장(20)", len(all_fields), 20)
write_seed(
    "decision_schema.json",
    {
        "schema_name": "DecisionSchema",
        "source_document": "D2.1-D2 §4.1 (18, FREEZE) + PHASE3-DEC-010 (confidence 2)",
        "version": "v3.0.0",
        "freeze_status": "FREEZE+DEC-010",
        "field_count": 20,
        "required_count": 16,
        "optional_count": 4,
        "fields": all_fields,
    },
)

# ── 2. registries.json — D2.1-D2 §5 기계 추출 ──
ev = find_registry("EventTypeRegistry")
fc = find_registry("FailureCodeRegistry")
fb = find_registry("FallbackRegistry")
check("EventTypeRegistry", len(ev["values"]), 123)
check("EventTypeRegistry 선언 count", ev.get("count"), 123)
check("FailureCodeRegistry", len(fc["values"]), 36)
check("FallbackRegistry", len(fb["values"]), 23)
write_seed(
    "registries.json",
    {
        "source_document": "D2.1-D2 §5 (SOT) + D2.1-D4 §4.1(Tool seed 2) + D2.1-D3 §4.1(Node seed 1)",
        "registries": {
            "EventTypeRegistry": {"count": 123, "naming_rule": ev.get("naming_rule"), "values": ev["values"]},
            "FailureCodeRegistry": {"count": 36, "naming_rule": fc.get("naming_rule"), "values": fc["values"]},
            "FallbackRegistry": {"count": 23, "naming_rule": fb.get("naming_rule"), "values": fb["values"]},
            "ToolRegistry": {
                "count": 2,
                "seed_entries": [
                    {
                        "tool_id": "llm_openai_text", "category": "llm.text", "adapter_id": "llm_openai_text",
                        "risk_class": "low", "cost_class": "v1", "required_gates": ["policy", "cost"],
                        "outputs": ["signal", "log"], "notes": "seed example only (D2.1-D4 §4.1)",
                    },
                    {
                        "tool_id": "tool_playwright", "category": "browser.render", "adapter_id": "tool_playwright",
                        "risk_class": "high", "cost_class": "v2", "required_gates": ["policy", "cost", "approval"],
                        "outputs": ["artifact", "log"], "notes": "seed example only (D2.1-D4 §4.1)",
                    },
                ],
            },
            "NodeRegistry": {
                "count": 1,
                "entry_schema_lock": {"node_id": "string (required)", "domain": "string (required)",
                                      "capabilities": "object (optional)", "constraints": "object (optional)"},
                "seed_entries": [
                    {"node_id": "bn_web_research", "domain": "research", "capabilities": {}, "constraints": {}},
                ],
            },
        },
    },
)

# ── 3. response_envelope.json — CLAUDE.md §12 verbatim (5 LOCK) ──
write_seed(
    "response_envelope.json",
    {
        "schema_name": "ResponseEnvelope",
        "source_document": "CLAUDE.md §12 (LOCK, L559-565)",
        "version": "v1.0",
        "freeze_status": "LOCK",
        "field_count": 5,
        "required_count": 5,
        "optional_count": 0,
        "fields": [
            {"name": "answer", "type": "object", "required": True,
             "description": "answer{summary, details, next_actions[]}"},
            {"name": "evidence", "type": "object", "required": True,
             "description": "evidence{coverage(0~1), items[], qod(0~1)}"},
            {"name": "self_check", "type": "object", "required": True,
             "description": "self_check{score(0~1), verdict(PASS|WARN|FAIL), reasons[], retry_allowed}"},
            {"name": "decision_ref", "type": "object", "required": True,
             "description": "decision_ref{decision_id, gates{}}"},
            {"name": "audit", "type": "object", "required": True,
             "description": "audit{event_ids[], failure_codes[], fallback_ids[]}"},
        ],
    },
)

# ── 4. intent_frame.json — D2.0-02 I-1 상세 출력 verbatim (10) ──
# ※ 정본 확정 기록(P4-0): D2.0-02 §7.3 요약(9, timestamp 무)과 후반 I-1 상세(L2632~2648, 10)가 병존 —
#   상세 섹션이 풍부·후행 정본이며 PART2 분모 10과 정확 일치. §11.12.1 Signature 8필드는 V1+ I-1 확장(V0 제외).
write_seed(
    "intent_frame.json",
    {
        "schema_name": "IntentFrame",
        "source_document": "D2.0-02 I-1 상세 출력(L2632-2648; §7.3 요약은 timestamp 누락 구판 — P4-0 판정) ",
        "version": "v1.0",
        "freeze_status": "CANONICAL",
        "field_count": 10,
        "required_count": 10,
        "optional_count": 0,
        "fields": [
            {"name": "intent_id", "type": "string", "required": True, "description": "Intent 레코드 고유 식별자"},
            {"name": "trace_id", "type": "string", "required": True, "description": "Trace 레코드 식별자(추적 연계)"},
            {"name": "timestamp", "type": "string", "required": True, "description": "생성 시각 (ISO 8601)"},
            {"name": "user_goal", "type": "string", "required": True, "description": "사용자 최종 목표/의도"},
            {"name": "task_type", "type": "enum", "required": True,
             "description": "explain|plan|code|research|summarize|design|debug|etc"},
            {"name": "domain_hint", "type": "object", "required": True,
             "description": "P0/P1/P2 + 후보 리스트"},
            {"name": "constraints", "type": "object", "required": True,
             "description": "format_constraints + must_include[] / must_not_include[]"},
            {"name": "risk_flags", "type": "object", "required": True,
             "description": "safety_sensitive(bool) + approval_maybe_required(bool) + cost_sensitive(bool)"},
            {"name": "ambiguity", "type": "object", "required": True,
             "description": "is_ambiguous(bool) + missing_slots[](0..N) + clarification_questions[](0..3)"},
            {"name": "required_artifacts", "type": "array", "required": True,
             "description": "doc|pdf|ppt|sheet|code|diagram|etc"},
        ],
    },
)

# ── 5. evidence_pack.json — D2.0-02 I-2 상세 출력 verbatim (6) ──
write_seed(
    "evidence_pack.json",
    {
        "schema_name": "EvidencePack",
        "source_document": "D2.0-02 I-2 상세 출력(L2698-2709; §7.13 요약은 timestamp 누락 구판 — P4-0 판정)",
        "version": "v1.0",
        "freeze_status": "CANONICAL",
        "field_count": 6,
        "required_count": 6,
        "optional_count": 0,
        "fields": [
            {"name": "evidence_pack_id", "type": "string", "required": True, "description": "EvidencePack 고유 식별자"},
            {"name": "trace_id", "type": "string", "required": True, "description": "Trace 레코드 식별자(추적 연계)"},
            {"name": "timestamp", "type": "string", "required": True, "description": "생성 시각 (ISO 8601)"},
            {"name": "items", "type": "array", "required": True,
             "description": "근거 항목: source_type(memory|doc|web|code|log|tool) + source_ref + excerpt_or_summary + qod_score + captured_at/recency_hint"},
            {"name": "coverage", "type": "object", "required": True,
             "description": "sufficient(bool) + gaps[]"},
            {"name": "citations_ready", "type": "boolean", "required": True, "description": "인용 준비 여부"},
        ],
    },
)

print("✅ seed 5종 생성 완료 (카운트 검증 전건 PASS)")
