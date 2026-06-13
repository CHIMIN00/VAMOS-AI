"""명세→테스트 추적 매트릭스 & 누락 탐지기 (§4 IV-3).

잠긴 test_strategy.md §2.1 "AC 완전 매핑"(D2~D8 모든 AC는 최소 1 TC) 원칙을
기계적 *갭 탐지기*로 격상한다. 요구사항(명세 항목)이 어떤 테스트에 매핑됐는지
선언한 매핑 파일을 읽어, (1) 테스트가 0개인 요구사항(미커버 갭)과
(2) 매핑됐으나 실제 .py 테스트 파일이 없는 테스트(허위 매핑)를 보고한다.

매핑 파일(JSON):
  {
    "requirements": [
      {"id": "DEC-006", "source": "PART2 §2 V0-STEP-3",
       "tests": ["backend/tests/test_roundtrip.py"]},
      ...
    ]
  }
  · tests 항목은 리포 루트 기준 .py 파일 경로(또는 glob). 디렉터리 경로는
    허위매핑으로 분류된다(파일이 아니므로). 빈 리스트 = 미커버 갭.

이 도구는 *메커니즘*을 제공한다. 요구사항 전수 모집단(PART2 V0~V3 STEP)의
완전 채움은 각 Phase 진행과 함께 증분된다(ADR PHASE4-DEC-011 §C 참조).

사용: python scripts/trace_matrix.py [매핑경로] [--root DIR] [--mode warn|error]
  기본 매핑 = 이 스크립트와 같은 디렉토리의 trace_matrix.map.json (cwd 비의존).
종료 코드: 0=갭 없음(또는 warn), 1=미커버/허위매핑/형식오류 존재(error 모드).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_MAPPING = Path(__file__).resolve().parent / "trace_matrix.map.json"


def _test_files(root: Path, spec: str) -> list[Path]:
    """매핑 항목 → 실존하는 .py 테스트 파일 목록.

    디렉터리/비.py/절대경로/root 이탈('..')은 제외 — 경로는 리포 루트 기준 상대여야 하며
    root 밖 파일로 '커버됨'을 위조하지 못하게 한다(verify_artifacts와 동일 불변식).
    """
    if Path(spec).is_absolute():
        return []
    matches = list(root.glob(spec)) if any(c in spec for c in "*?[") else [root / spec]
    root_resolved = root.resolve()
    out: list[Path] = []
    for p in matches:
        if not (p.is_file() and p.suffix.lower() == ".py"):
            continue
        try:
            p.resolve().relative_to(root_resolved)
        except ValueError:
            continue  # root 이탈 → 제외
        out.append(p)
    return out


def analyze(root: Path, reqs: list) -> tuple[list[str], list[str], int]:
    """→ (uncovered, phantom, n_mapped)."""
    uncovered: list[str] = []
    phantom: list[str] = []
    n_mapped = 0
    for req in reqs:
        if not isinstance(req, dict):
            phantom.append(f"요구사항 항목이 객체(dict)가 아님: {req!r}")
            continue
        rid = req.get("id", "<no-id>")
        tests = req.get("tests") or []
        if not isinstance(tests, list):
            phantom.append(f"{rid} → 'tests' 필드는 리스트여야 함 (got {type(tests).__name__})")
            continue
        if not tests:
            uncovered.append(f"{rid} ({req.get('source', '?')}) — 매핑된 테스트 0개")
            continue
        for t in tests:
            if not isinstance(t, str):
                phantom.append(f"{rid} → 테스트 경로가 문자열이 아님: {t!r}")
                continue
            if _test_files(root, t):
                n_mapped += 1
            else:
                phantom.append(f"{rid} → '{t}' (.py 테스트 파일 부재 — 허위 매핑)")
    return uncovered, phantom, n_mapped


def main() -> int:
    ap = argparse.ArgumentParser(description="명세→테스트 추적 매트릭스 누락 탐지기")
    ap.add_argument("mapping", nargs="?", default=str(DEFAULT_MAPPING),
                    help="매핑 JSON 경로 (기본: 스크립트 옆 trace_matrix.map.json)")
    ap.add_argument("--root", default=".", help="리포 루트 (기본 현재 디렉토리)")
    ap.add_argument("--mode", choices=["warn", "error"], default="error")
    args = ap.parse_args()

    mapping_path = Path(args.mapping)
    root = Path(args.root).resolve()
    if not mapping_path.exists():
        print(f"[trace_matrix] 매핑 파일 부재: {mapping_path} — 추적 불가 (FAIL)")
        return 1 if args.mode == "error" else 0
    try:
        data = json.loads(mapping_path.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"[trace_matrix] 매핑 파싱 실패: {e}")
        return 1

    reqs = data.get("requirements", data) if isinstance(data, dict) else data
    if not isinstance(reqs, list):
        print("[trace_matrix] 매핑 형식 오류 — list 또는 {'requirements': [...]} 필요")
        return 1
    if len(reqs) == 0:
        print("[trace_matrix] 요구사항 0건 — 추적 대상 없음 (FAIL)")
        return 1 if args.mode == "error" else 0

    uncovered, phantom, n_mapped = analyze(root, reqs)
    for u in uncovered:
        print(f"GAP  {u}")
    for p in phantom:
        print(f"PHANTOM {p}")
    print(f"[trace_matrix] 요구사항 {len(reqs)}개 · 유효매핑(테스트항목) {n_mapped} · "
          f"미커버 {len(uncovered)} · 허위매핑 {len(phantom)} (mode={args.mode})")
    if (uncovered or phantom) and args.mode == "error":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
