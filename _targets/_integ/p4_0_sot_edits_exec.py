# P4-0 SOT 수정 집행 (사용자 승인 2026-06-12) — p4_0_sot_edits_pending.md A/B/C 전건
# EOL 보존: newline='' 읽기/쓰기 (MASTER_SPEC=CRLF 디스크, 나머지=LF). 각 치환 기대 횟수 assert.
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"D:\VAMOS\docs\sot"

CONFIDENCE_SECTION = """### 3.16 [confidence] -- 예측 신뢰도 임계값 (LOCK)

> 신설: PHASE3-DEC-010 (R1-A25, LOCK-DECISION-REGISTRY §8) — P4-0 집행 (PHASE4-DEC-003, 사용자 승인 2026-06-12). V0부터 적용 (config LOCK 분모 20→23). 기존 §3.1~3.15 무변경 — 추가만.

| 키 | 타입 | V1 기본값 | V2 기본값 | V3 기본값 | 설명 | 연결 스키마 |
|----|------|----------|----------|----------|------|------------|
| `confidence_high_threshold` | `float` | `0.85` | `0.85` | `0.85` | HIGH 분기 임계값 (LOCK) — 이상 시 정상 답변 | D2 DecisionSchema (confidence_level, DEC-010) |
| `confidence_medium_threshold` | `float` | `0.60` | `0.60` | `0.60` | MEDIUM 분기 임계값 (LOCK) — 확신도 보통 표시 | D2 DecisionSchema (confidence_level, DEC-010) |
| `confidence_refuse_threshold` | `float` | `0.30` | `0.30` | `0.30` | REFUSE 분기 임계값 (LOCK) — 미만 시 답변 거부 | D2 DecisionSchema (confidence_level, DEC-010) |

```toml
[confidence]
confidence_high_threshold = 0.85     # LOCK
confidence_medium_threshold = 0.60   # LOCK
confidence_refuse_threshold = 0.30   # LOCK
```

---

## 4. 버전별 프리셋 (V1/V2/V3)"""

# 파일별 (old, new, expected) — 모든 old/new는 LF 기준으로 쓰고, CRLF 파일은 동적 변환
PLANS = {
    "VAMOS_MASTER_SPECIFICATION.md": [
        ("PHASE=구현단계가이드(B1~B7)",
         "PHASE=구현단계가이드(B1~B7, = IMPLEMENTATION 계층)", 1),
        ("| Gate 우회 불가 | Policy→Approval→Cost→Evidence 필수 |",
         "| Gate 우회 불가 | Policy→Approval→Cost→Evidence→SelfCheck 필수 |", 1),
    ],
    "D2.0-01_01. VAMOS_DESIGN_2_0_OVERVIEW.md": [
        ("모든 액션은 **Policy → Approval → Cost → Evidence** 게이트를 반드시 통과",
         "모든 액션은 **Policy → Approval → Cost → Evidence → SelfCheck** 게이트를 반드시 통과", 1),
    ],
    "VAMOS_BEGINNER_GUIDE.md": [
        ("| Gate 우회 불가 | Policy→Approval→Cost→Evidence 필수 |",
         "| Gate 우회 불가 | Policy→Approval→Cost→Evidence→SelfCheck 필수 |", 1),
        ("I-5: 게이트 검사 (Policy→Cost→Approval→Evidence)",
         "I-5: 게이트 검사 (Policy→Approval→Cost→Evidence; SelfCheck는 verify 노드 — D2.0-02 §8.1 LOCK)", 1),
    ],
    "PHASE_B4_CONFIG_SPEC.md": [
        # §3.16 신설 (§3.15 종료~§4 헤더 사이)
        ("ttl_sec = 3600\n```\n\n---\n\n## 4. 버전별 프리셋 (V1/V2/V3)",
         "ttl_sec = 3600\n```\n\n" + CONFIDENCE_SECTION, 1),
        # §4.1 V1 프리셋 toml에 [confidence] 추가 (동일 결정의 일관 반영 — 추가만)
        ("[semantic_cache]\nenabled = true\nsimilarity_threshold = 0.95\nmax_entries = 1000\nttl_sec = 3600\n```\n\n### 4.2",
         "[semantic_cache]\nenabled = true\nsimilarity_threshold = 0.95\nmax_entries = 1000\nttl_sec = 3600\n\n[confidence]                       # PHASE3-DEC-010 LOCK 3키 (§3.16) — P4-0 집행\nconfidence_high_threshold = 0.85\nconfidence_medium_threshold = 0.60\nconfidence_refuse_threshold = 0.30\n```\n\n### 4.2", 1),
    ],
}

failures = []
for fname, edits in PLANS.items():
    path = f"{ROOT}\\{fname}"
    with io.open(path, "r", encoding="utf-8", newline="") as f:
        text = f.read()
    crlf = "\r\n" in text
    pre_cr, pre_lf = text.count("\r"), text.count("\n")
    for old, new, expected in edits:
        o = old.replace("\n", "\r\n") if crlf else old
        n_str = new.replace("\n", "\r\n") if crlf else new
        cnt = text.count(o)
        if cnt != expected:
            failures.append((fname, old[:50], expected, cnt))
            continue
        text = text.replace(o, n_str)
    if failures and failures[-1][0] == fname:
        continue
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    post_cr, post_lf = text.count("\r"), text.count("\n")
    eol = "CRLF" if crlf else "LF"
    print(f"  ✅ {fname} ({eol}): CR {pre_cr}→{post_cr} / LF {pre_lf}→{post_lf}")

if failures:
    print("❌ 치환 횟수 불일치 (해당 파일 미기록):")
    for f, o, e, c in failures:
        print(f"  {f}: 기대 {e} != 실제 {c} :: {o}")
    sys.exit(1)
print("✅ SOT edits 전건 집행 완료")
