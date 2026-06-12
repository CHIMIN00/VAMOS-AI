# P4-0 SOT edits 집행 후 integrity 신규 체크 — 직전 기준(20260612T175049, GATE-07 신규 참조) 대비
# 기대: changed = 정확히 4 (MASTER_SPEC/D2.0-01/BEGINNER/PHASE_B4 — 승인 집행분) — 그 외 변경 0
import hashlib
import io
import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(r"D:\VAMOS")
PREV = ROOT / "04. 구현단계" / "v13_results" / "phase0" / "integrity" / "v13_integrity_check_20260612T175049.json"
STAMP = "20260612T230000"  # P4-0 SOT edits 집행 시점 (세션 기록 기준)

prev = json.load(io.open(PREV, encoding="utf-8"))
EXPECTED_CHANGED = {
    "VAMOS_MASTER_SPECIFICATION.md",
    "D2.0-01_01. VAMOS_DESIGN_2_0_OVERVIEW.md",
    "VAMOS_BEGINNER_GUIDE.md",
    "PHASE_B4_CONFIG_SPEC.md",
    # 기지 변경: 175049 체크 직후 PHASE3-DEC-011 F1 해소(루트→sot byte 재복사, 2026-06-12 기집행·기록)
    "CLAUDE.md",
}
# CLAUDE.md는 DEC-011 확정 SHA와 일치해야 함 (45120F11… — P4-0 STEP 2에서도 루트 일치 재확인)
CLAUDE_EXPECTED_SHA = "45120f11d35299422693109e97c95bef1594a8fdbe3c6634f464c971c67f5386"

details = []
changed, unchanged = [], 0
for entry in prev["details"]:
    name = entry["sot_file"]
    path = ROOT / "docs" / "sot" / name
    cur = hashlib.sha256(path.read_bytes()).hexdigest()
    ref = entry["hash_current"]  # 직전 체크의 현재값 = 본 체크의 기준값
    status = "OK" if cur == ref else "CHANGED"
    if status == "CHANGED":
        changed.append(name)
    else:
        unchanged += 1
    details.append({"sot_file": name, "status": status, "hash_current": cur,
                    "hash_recorded": [ref], "in_baseline": True})

out = {
    "check_timestamp": "2026-06-12T23:00:00",
    "sot_total": len(details),
    "changed": len(changed),
    "unchanged": unchanged,
    "no_recorded_hash": 0,
    "verdict": ("CHANGED_AS_APPROVED"
                if set(changed) == EXPECTED_CHANGED
                and hashlib.sha256((ROOT / "docs" / "sot" / "CLAUDE.md").read_bytes()).hexdigest() == CLAUDE_EXPECTED_SHA
                else "UNEXPECTED_CHANGE"),
    "baseline_used": "v13_integrity_check_20260612T175049.json (GATE-07b 신규 참조 기준)",
    "note": "P4-0 SOT edits 사용자 승인 집행(2026-06-12, _targets/p4_0_sot_edits_pending.md A/B/C) 후 체크. "
            "기대 변경 5파일 한정: MASTER_SPEC(L78 IMPLEMENTATION+L1512 5-Gate)/D2.0-01(L208 5-Gate)/"
            "BEGINNER(L1376 5-Gate+L1813 순서 정정)/PHASE_B4(§3.16 [confidence] 신설+§4.1 프리셋) "
            "+ CLAUDE.md(175049 체크 직후 PHASE3-DEC-011 F1 루트→sot 재복사 — SHA 45120F11 검증, 본 세션 수정 아님). "
            "이외 변경 0. 백업 _targets/_integ/backup_p4_0/*.pre-sot-edit.md",
    "skill_version": "D1-deterministic-v1.0 (P4-0 재실행 2026-06-12)",
    "details": details,
}

dst = PREV.parent / f"v13_integrity_check_{STAMP}.json"
with io.open(dst, "w", encoding="utf-8", newline="\n") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print(f"changed={len(changed)} unchanged={unchanged} verdict={out['verdict']}")
for c in changed:
    print(f"  CHANGED: {c}")
if out["verdict"] != "CHANGED_AS_APPROVED":
    print("❌ 승인 범위 밖 변경 감지!")
    sys.exit(1)
print(f"✅ integrity 신규 체크 기록: {dst.name}")
