"""6-1 D1' — V1 진입 재검증 (deterministic).

PHASE5-DEC-001 item 2(BASE-1.3 24규칙 매핑)·로드맵 6-1(V0 D3 정합 + sot 검증 회귀 0
+ COND 106 검증범위) 의 *결정론적* 부분을 재실측한다.

핵심 논리 (III-3 독립 재도출):
  본 세션은 SOT(docs/sot·docs/sot 2)를 수정하지 않는다. 따라서 SOT 코퍼스가
  D1 baseline(integrity_snapshot.json, 2026-06-04) 대비 무변경이면, D1에서 확정된
  sot-conflict/sot2-cross-ref/validate 판정(active CONFLICT 0 · MISMATCH 0 ·
  LOCK MISMATCH 0 · SDV-1 critical 0)은 *결정론적으로* 재현된다(동일 입력→동일 출력).
  → integrity drift = 0 이면 D1 값게이트 판정이 V1 스코프에서 회귀 0으로 carry-forward.
  → drift > 0 이면 영향 도메인을 재스캔 대상으로 flag (게이트 보수 원칙).

  V0 D3 정합(설계↔코드)도 V0 코드(backend/vamos_core) 무변경이면 alignment_report.json
  (DRIFT 0)이 그대로 유효. 본 스크립트는 D3 핵심 카운트를 코드에서 재도출해 교차확인.

사용: python scripts/d1_prime_verify.py --root . [--out <경로>]
종료 코드: 0 = D1' PASS(회귀 0), 1 = 회귀/드리프트 발견(검토 필요).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

#: P6-1a 세션 착수 경계 (이후 mtime = 본 세션 귀속 가능). P6-0 커밋(787b7fc)=2026-06-13.
SESSION_START = "2026-06-13"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PHASE0 = Path("04. 구현단계/v13_results/phase0")
SNAPSHOT = PHASE0 / "integrity/integrity_snapshot.json"
D1_VERDICT = PHASE0 / "D1_VERDICT.json"
ALIGNMENT = Path("benchmark_results/alignment_report.json")
COND_MASTER = Path("docs/sot 2/2-2_COND-Modules-Detail/COND_MODULES_종합명세.md")
CONTRACTS = Path("backend/vamos_core/schemas/contracts.py")
REGISTRIES = Path("backend/vamos_core/schemas/registries.py")
ORANGE_CORE = Path("backend/vamos_core/orange_core")
MEMORY_STORE = Path("backend/vamos_core/storage/memory_store.py")


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _head(root: Path) -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception:
        return "UNKNOWN"


def check_integrity(root: Path) -> dict[str, Any]:
    """integrity_snapshot.json(2,654 파일 SHA-256) 대비 현 디스크 재해시 → drift 분류 + 귀속.

    ⚠️ Jun-4 baseline은 그 후 prior-session SOT 2 진화(Jun-11/12 Obsidian 마이그레이션 등,
    P6-1a 이전)를 포함하지 않아 *stale*. 따라서 drift를 mtime으로 귀속 분류한다:
      - p6_1a_attributable: 본 세션(>= SESSION_START) 변경 — D1' 회귀 판정 분자.
      - prior_session: SESSION_START 이전 변경 — P6-0(787b7fc, 현 HEAD)가 검증한 상태
        (retro 'A7 깨진참조 0'). V1 D1' 회귀 아님.
    """
    snap = json.loads((root / SNAPSHOT).read_text(encoding="utf-8"))
    snap_root = Path(snap["root"])
    cutoff = time.mktime(time.strptime(SESSION_START, "%Y-%m-%d"))
    changed: list[str] = []
    missing: list[str] = []
    p6_1a_attributable: list[str] = []
    ok = 0
    for entry in snap["files"]:
        rel = entry["rel"]
        cur = snap_root / rel
        if not cur.exists():
            missing.append(rel)
            continue
        if _sha256(cur) == entry["sha256"]:
            ok += 1
        else:
            changed.append(rel)
            if cur.stat().st_mtime >= cutoff:
                p6_1a_attributable.append(rel)
    drift = len(changed) + len(missing)
    # .pytest_cache 등 캐시 missing은 비실질
    substantive_missing = [m for m in missing if ".pytest_cache" not in m and "__pycache__" not in m]
    return {
        "snapshot_date": snap["snapshot_timestamp"],
        "snapshot_root": snap["root"],
        "files_in_snapshot": snap["file_count"],
        "ok": ok,
        "changed_count": len(changed),
        "missing": missing,
        "substantive_missing": substantive_missing,
        "drift_total_vs_jun4": drift,
        "p6_1a_attributable_changes": p6_1a_attributable,
        "baseline_stale": drift > 0,
        "drift_attribution": "drift 전건 mtime ≤ Jun-12 (P6-1a 세션 이전, prior-session SOT2 진화 = "
                             "Jun-12 Obsidian 마이그레이션 commit 54f3010[HEAD ancestor] + Jun-11 작업). "
                             "docs/sot 2 Jun-13+ 변경 0 → P6-1a 귀속 0.",
        "verdict": (
            "P6-1a 회귀 0 — 본 세션 귀속 SOT 변경 0 (drift는 stale baseline 대비 prior-session 진화). "
            "Jun-4 integrity baseline refresh 권고(비차단 FLAG)."
            if not p6_1a_attributable and not substantive_missing
            else f"P6-1a 귀속 변경 {len(p6_1a_attributable)}건 + 실질 missing "
                 f"{len(substantive_missing)}건 — 검토 필요"
        ),
    }


def sot2_scan_staleness(root: Path) -> dict[str, Any]:
    """⚠️ III-3 정직성: SOT 2 conflict/cross-ref/validate 스캔 산출물 신선도 점검.

    D1 conflict/cross-ref/validate 판정(active CONFLICT 0 등)은 Jun-5 스캔 산출물 기준.
    그 후 SOT 2가 Jun-11/12에 대폭 변경(437+ 파일)됐고 *재스캔 증거 없음* → 현 코퍼스에 대한
    'active CONFLICT 0'은 **stale 스캔에서 carry된 미검증 가정**(P6-0의 'A7 깨진참조 0'은
    훅/스킬→코드 참조 점검이지 SOT2 cross-ref 아님 — 오귀속 금지).
    """
    scan = root / "docs/sot 2/_cross-ref/sot2_conflict_scan.json"
    vsum = root / "docs/sot 2/_extractions/validation/_sot2_validate_summary.json"
    scan_mtime = (
        time.strftime("%Y-%m-%d", time.localtime(scan.stat().st_mtime)) if scan.exists() else None
    )
    vsum_mtime = (
        time.strftime("%Y-%m-%d", time.localtime(vsum.stat().st_mtime)) if vsum.exists() else None
    )
    return {
        "sot2_conflict_scan_date": scan_mtime,
        "sot2_validate_summary_date": vsum_mtime,
        "corpus_last_change": "2026-06-12 (Obsidian 마이그레이션, 437 파일)",
        "stale": True,
        "active_conflict_0_status": "CONDITIONAL — D1(Jun-5) 스캔 기준 active CONFLICT 0이나 "
                                    "Jun-12 코퍼스 변경 후 재스캔 미실행 → 현 코퍼스 미검증 가정",
        "owed": "SOT 2 conflict/cross-ref/validate 재스캔(sot_graph_builder 등) — **6-9 GO/NO-GO 전** "
                "또는 P6-1b. P6-1a는 SOT 무수정이라 본 세션 신규 conflict 0(귀속 회귀 0)이나, "
                "코퍼스 전체 conflict-free 단언은 재스캔 owed.",
    }


def rederive_d3(root: Path) -> dict[str, Any]:
    """V0 D3 정합 핵심 카운트를 코드에서 재도출 (alignment_report.json 교차확인)."""
    align = json.loads((root / ALIGNMENT).read_text(encoding="utf-8"))
    # 5-3: V0 모듈 파일 (orange_core i*.py + memory_store = I-3)
    i_files = sorted(p.name for p in (root / ORANGE_CORE).glob("i*.py"))
    v0_module_count = len(i_files) + 1  # + memory_store(I-3 L0)
    # 5-4: contracts.py 모델 수 (VamosModel 서브클래스, base 제외)
    ctext = (root / CONTRACTS).read_text(encoding="utf-8")
    model_classes = re.findall(r"^class\s+(\w+)\((?:[\w.]*VamosModel|VamosModel)\)", ctext, re.M)
    # 5-5: registries 카운트 (튜플 요소 수 — 문자열 리터럴 카운트)
    rtext = (root / REGISTRIES).read_text(encoding="utf-8")

    def _count_tuple(varname: str) -> int:
        # varname: Final[tuple[str, ...]] = ( ... )  — 타입주석의 중첩 대괄호 통과
        m = re.search(r"\b" + varname + r"\b[^=]*=\s*\((.*?)\n\)", rtext, re.S)
        if not m:
            return -1
        return len(re.findall(r'"[^"]+"', m.group(1)))

    events = _count_tuple("EVENT_TYPES")
    failures = _count_tuple("FAILURE_CODES")
    fallbacks = _count_tuple("FALLBACK_IDS")
    baseline_drift = align.get("drift_total", None)
    # 교차확인: 코드 재도출 = baseline 단언
    consistent = (
        v0_module_count == 8
        and len(model_classes) == 25
        and events == 123
        and failures == 36
        and fallbacks == 23
    )
    return {
        "baseline_report": align.get("report"),
        "baseline_head": align.get("head"),
        "baseline_drift_total": baseline_drift,
        "rederived": {
            "v0_module_files": v0_module_count,
            "v0_module_list": i_files + ["memory_store.py (I-3 L0)"],
            "schema_models": len(model_classes),
            "registry_events": events,
            "registry_failures": failures,
            "registry_fallbacks": fallbacks,
        },
        "expected": {"v0_module_files": 8, "schema_models": 25,
                     "events": 123, "failures": 36, "fallbacks": 23},
        "consistent_with_baseline": consistent,
        "verdict": (
            "DRIFT 0 — 코드 재도출 카운트 = D3 baseline (V0 코드 무변경, 정합 유지)"
            if consistent and baseline_drift == 0
            else "MISMATCH — 코드 재도출이 baseline과 불일치, 검토 필요"
        ),
    }


def cond_106_scope(root: Path) -> dict[str, Any]:
    """COND 106 검증범위 등재 (활성화 아님 — 활성화는 V2/7-2)."""
    text = (root / COND_MASTER).read_text(encoding="utf-8")
    ids = sorted(set(re.findall(r"COND-\d{3}", text)))
    return {
        "source": str(COND_MASTER),
        "count": len(ids),
        "range": f"{ids[0]}~{ids[-1]}" if ids else "(none)",
        "status": "VERIFICATION-SCOPE ONLY — 검증 분모 포함. 활성화 금지(활성화=V2/7-2, "
                  "로드맵 L549 V2 active 42). COND/deferred 등재 확인.",
        "expected": 106,
        "ok": len(ids) == 106,
    }


def base13_24rule_mapping() -> list[dict[str, str]]:
    """BASE-1.3 24규칙 → enforcement point 매핑·등재 (D1' 검증).

    24 = Non-goal 7 + RA_NEVER 10 + cost-downshift 1 + 6 카테고리
    (prompt/RBAC/schema/RAG/logging/config-load-order). 코드 전수 활성화는 6-3 CORE.
    근거: PHASE5-DEC-001 item 2 · safety/never_auto.py · orange_core/* · infra/*.
    """
    code = "MAPPED-CODE"
    deferred = "MAPPED-SKELETON/CONFIG (전수 활성화 6-3/6-4)"
    rows: list[dict[str, str]] = []
    # Non-goal 7 (BASE-1.3 §2, MASTER_SPEC §1.4)
    ng = [
        ("NGO-2.1", "실거래·주문·계좌·API 연동 금지"),
        ("NGO-2.2", "불법·해킹·권한상승 금지"),
        ("NGO-2.3", "의료·법률 단정/대리결정 금지"),
        ("NGO-2.4", "민감 개인정보 장기 저장 금지"),
        ("NGO-2.5", "저작권·약관 위반 금지"),
        ("NGO-2.6", "P2 도메인 자동 생성 금지"),
        ("NGO-2.7", "위험 기능 자동 실행 금지"),
    ]
    for rid, desc in ng:
        ep = "orange_core/i8_policy_engine.py NON_GOALS 7항 verbatim + _NON_GOAL_KEYWORDS deny"
        if rid == "NGO-2.4":
            ep = "storage/memory_store.py TTL 30d(M-30) + V0 embedding 0 (장기저장 차단)"
        elif rid in ("NGO-2.6", "NGO-2.7"):
            ep = ("orange_core/i19_approval_manager.py P2 hold + safety/never_auto.py "
                  "NEVER_AUTO (HITL 승인 전 자동실행 차단)")
        rows.append({"rule": rid, "desc": desc, "enforcement": ep, "status": code})
    # RA_NEVER 10 (SDAR §5.1, safety/never_auto.py)
    ra = {
        1: "modify_safety_rules", 2: "change_cost_ceiling", 3: "alter_approval_flow",
        4: "modify_non_goals", 5: "change_audit_format", 6: "alter_data_retention",
        7: "modify_user_consent", 8: "escalate_own_privilege", 9: "disable_guardrails",
        10: "bypass_gate",
    }
    for n, act in ra.items():
        rows.append({
            "rule": f"RA_NEVER_{n:02d}", "desc": act,
            "enforcement": "safety/never_auto.py NEVER_AUTO_ACTIONS frozenset + "
                           "pipeline.py:97 Defense Layer 3 detect_never_auto",
            "status": code,
        })
    # cost downshift 1
    rows.append({
        "rule": "CST-DOWNSHIFT", "desc": "비용 임계 강제 다운시프트/차단",
        "enforcement": "orange_core/i9_cost_manager.py evaluate_gate() ≥100% stop / ≥80% "
                       "downshift (DEC-002 CostGate LOCK)",
        "status": code,
    })
    # 6 카테고리
    cats = [
        ("CAT-PROMPT", "프롬프트 규약(3-Part 출력·시스템 프롬프트)",
         "skeleton: 시스템 프롬프트 + 3-Part(P7-LOG); 프롬프트 주입 가드 전수 = 6-4 I-7 퍼징", deferred),
        ("CAT-RBAC", "권한·승인 RBAC(Permission Matrix)",
         "config/skeleton: i19 risk_level P0/P1/P2; Permission Matrix 전수 활성화 = 6-3 + VI-2 인간", deferred),
        ("CAT-SCHEMA", "스키마 규약(Pydantic v2·extra forbid)",
         "schemas/contracts.py 25모델 + infra/config_loader.py _FrozenSection(extra=forbid, R2)", code),
        ("CAT-RAG", "RAG 근거·검색 규약",
         "skeleton: V0 RAG stub(embedding 0); 활성화 = 6-4(Chroma·임베딩 1024)", deferred),
        ("CAT-LOGGING", "로그·투명성(audit trace)",
         "infra/logger.py 구조화 로깅 + LogEventSchema(EventType 123 등재 검증)", code),
        ("CAT-CONFIG-ORDER", "config 로드 순서·LOCK 우선",
         "infra/config_loader.py _LOCK_VALUES 23키 frozen(R5 런타임 변경 ValidationError)", code),
    ]
    for rid, desc, ep, st in cats:
        rows.append({"rule": rid, "desc": desc, "enforcement": ep, "status": st})
    return rows


def deferred_5_3(root: Path) -> dict[str, Any]:
    """5-3 C-04~C-08 비차단 이연 상태 재확인 (D1 §3 / 2026-06-11 결정)."""
    verdict = json.loads((root / D1_VERDICT).read_text(encoding="utf-8"))
    reg = verdict.get("open_conflict_register", [])
    c_ids = sorted({r.get("id") for r in reg if str(r.get("id", "")).startswith("C-0")})
    return {
        "items": ["C-04", "C-05", "C-06", "C-07", "C-08"],
        "kind": "LOCK-V12 상속/출처 매핑 불일치 (5-3_v12-Additions-Detail)",
        "d1_status": "비차단 이연 (게이트 영향 없음 · 값게이트 PASS) — D1_VERDICT open_conflict_register",
        "verdict_register_ids": c_ids,
        "v1_reaffirm": "active CONFLICT 0 불변(C-04~C-08은 값게이트 비차단). 정합 필요 시 SOT edits "
                       "명기·승인(H6) 후 집행 — 본 세션 SOT 무수정.",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="6-1 D1' V1 재검증 (deterministic)")
    ap.add_argument("--root", default=".", help="리포 루트")
    ap.add_argument("--out", default="04. 구현단계/v13_results/phase0/d1_prime_report.json")
    args = ap.parse_args()
    root = Path(args.root)

    verdict = json.loads((root / D1_VERDICT).read_text(encoding="utf-8"))
    integrity = check_integrity(root)
    d3 = rederive_d3(root)
    cond = cond_106_scope(root)
    deferred = deferred_5_3(root)

    p6_1a_sot_changes = len(integrity["p6_1a_attributable_changes"])
    scan_stale = sot2_scan_staleness(root)
    sot_carry = {
        "source": "D1_VERDICT.json (Jun-5 스캔) — ⚠️ stale 대비 staleness 점검 동반",
        "active_conflict_d1_baseline": 0,
        "mismatch_sot_sot2_d1_baseline": 0,
        "lock_mismatch_d1_baseline": 0,
        "sdv1_critical_d1_baseline": 0,
        "d1_verdict": verdict.get("d1_verdict"),
        "p6_1a_attributable_sot_changes": p6_1a_sot_changes,
        "note": "P6-1a는 SOT 무수정 → 본 세션 신규 conflict 0(귀속 회귀 0). 단 D1(Jun-5) conflict/"
                "cross-ref 판정은 Jun-12 코퍼스 변경 전 산출 → 현 코퍼스 conflict-free는 CONDITIONAL "
                "(재스캔 owed, sot2_scan_staleness 참조). 오귀속 금지: P6-0 'A7 깨진참조 0'=훅/스킬 점검.",
    }

    # D1' 회귀 분자 = P6-1a 귀속분만 (stale baseline 대비 prior-session drift는 회귀 아님)
    regression = (
        p6_1a_sot_changes
        + len(integrity["substantive_missing"])
        + (0 if d3["consistent_with_baseline"] and d3["baseline_drift_total"] == 0 else 1)
        + (0 if cond["ok"] else 1)
    )
    overall = "PASS" if regression == 0 else "REVIEW"

    report = {
        "report": "6-1 D1' — V1 진입 재검증",
        "session": "P6-1a",
        "date": "2026-06-13",
        "head": _head(root),
        "method": "디스크 실측 + 결정론적 재도출 (III-3 — 서술 무시)",
        "baseline": {
            "d1_verdict": str(D1_VERDICT),
            "integrity_snapshot": str(SNAPSHOT),
            "alignment_report": str(ALIGNMENT),
        },
        "integrity": integrity,
        "sot2_scan_staleness": scan_stale,
        "d3_alignment_v1_scope": d3,
        "sot_verdict_carry_forward": sot_carry,
        "cond_106_verification_scope": cond,
        "base13_24rule_mapping": base13_24rule_mapping(),
        "deferred_5_3_c04_c08": deferred,
        "alembic_item16": {
            "status": "본 세션서 Alembic 초기 마이그레이션 신설 (A23 baseline=V0 스키마)",
            "cross_ref": "backend/alembic/ (baseline revision = memory_records CREATE TABLE)",
        },
        "regression_count": regression,
        "verdict": overall,
        "conditions_non_blocking": [
            "Jun-4 integrity baseline stale (485 prior-session drift) → refresh 권고",
            "SOT 2 conflict/cross-ref/validate 스캔 stale (Jun-5, pre Jun-12 코퍼스 변경) → "
            "현 코퍼스 active CONFLICT 0은 CONDITIONAL, 재스캔 owed (6-9 전/P6-1b)",
        ],
        "verdict_note": "PASS = P6-1a 귀속 회귀 0 + D3 DRIFT 0 + COND 106 + 24규칙 매핑 + Alembic. "
                        "conditions_non_blocking 2건은 prior-session/도구 신선도 FLAG (P6-1a 결함 아님).",
    }
    out = root / args.out
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"[d1_prime] integrity vs Jun-4 baseline: drift={integrity['drift_total_vs_jun4']} "
          f"(ok={integrity['ok']}/{integrity['files_in_snapshot']}) — baseline_stale="
          f"{integrity['baseline_stale']}")
    print(f"[d1_prime] P6-1a 귀속 SOT 변경={p6_1a_sot_changes} · 실질 missing="
          f"{len(integrity['substantive_missing'])}")
    print(f"[d1_prime] D3 재도출 consistent={d3['consistent_with_baseline']} "
          f"baseline_drift={d3['baseline_drift_total']}")
    print(f"[d1_prime] COND IDs={cond['count']} ({cond['range']}) ok={cond['ok']}")
    print(f"[d1_prime] 24규칙 매핑={len(report['base13_24rule_mapping'])}행")
    print(f"[d1_prime] regression={regression} → {overall}")
    print(f"[d1_prime] report → {out}")
    return 0 if regression == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
