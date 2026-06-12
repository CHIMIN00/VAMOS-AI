# P4-0 SOT 수정 집행 2차 — MASTER_SPEC 잔여 2건 (L78 원문 재실측 반영: "구현직접가이드")
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
PATH = r"D:\VAMOS\docs\sot\VAMOS_MASTER_SPECIFICATION.md"

EDITS = [
    ("PHASE=구현직접가이드(B1~B7)",
     "PHASE=구현직접가이드(B1~B7, = IMPLEMENTATION 계층)", 1),
    ("| Gate 우회 불가 | Policy→Approval→Cost→Evidence 필수 |",
     "| Gate 우회 불가 | Policy→Approval→Cost→Evidence→SelfCheck 필수 |", 1),
]

with io.open(PATH, "r", encoding="utf-8", newline="") as f:
    text = f.read()
pre_cr, pre_lf = text.count("\r"), text.count("\n")

for old, new, expected in EDITS:
    cnt = text.count(old)
    if cnt != expected:
        print(f"❌ 기대 {expected} != 실제 {cnt} :: {old[:60]} — 미기록 중단")
        sys.exit(1)
    text = text.replace(old, new)

with io.open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write(text)
print(f"✅ MASTER_SPEC 2건 집행 (CRLF): CR {pre_cr}→{text.count(chr(13))} / LF {pre_lf}→{text.count(chr(10))}")
