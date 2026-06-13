"""산출물 실존 검증 게이트 (R16 verify-only 착시 방어 — §4 III-1/III-2/III-4).

"보고서 ✅ ≠ 산출물 존재" 착시(로드맵 R16)를 기계적으로 차단한다.
매니페스트에 선언된 각 산출물이 (1) 디스크에 실존하고 (2) 비어있지 않으며
(3) 기대 SHA-256과 일치하고 (4) 필수 문자열을 포함하며 (5) 이를 참조하도록
지정된 테스트 파일이 실존하는지 검증한다 — 구현가의 서술이 아니라 디스크 상태로 판정.

매니페스트(JSON) 항목 스키마:
  {
    "path": "scripts/foo.py",            # 필수 (리포 루트 기준 상대경로)
    "min_bytes": 1,                        # 선택 (기본 1 — 비어있지 않음)
    "sha256": "abc...",                   # 선택 (동결 산출물 무결성 핀)
    "must_contain": ["def main"],          # 선택 (핵심 문자열 존재 — 부분 착시 방어)
    "referencing_test": "backend/tests/test_foo.py"  # 선택: 참조 테스트 파일 *실존* 확인
  }                                          #        (내용상 import/참조까지는 검사하지 않음)

빈/공허 매니페스트([], {"artifacts": []}, 'artifacts' 키 부재 dict)는 무검증 통과를
재생산하므로 명시적 FAIL 처리한다(안티착시 게이트의 자기무력화 방지).

사용: python scripts/verify_artifacts.py [매니페스트경로] [--root DIR] [--mode warn|error]
  기본 매니페스트 = 이 스크립트와 같은 디렉토리의 artifact_manifest.json (cwd 비의존),
  기본 root = 매니페스트 상위의 상위 = 리포 루트.
종료 코드: 0=전건 PASS(또는 warn 모드). 형식오류(잘못된 JSON·키 부재)=항상 1(mode 무관).
  산출물 FAIL/공허 매니페스트=error 모드 1 / warn 모드 0.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

# Windows cp949 콘솔 — 출력 UnicodeEncodeError 방지 (P4-0 도구 점검 수리 관례)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_MANIFEST = Path(__file__).resolve().parent / "artifact_manifest.json"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _within_root(target: Path, root: Path) -> bool:
    """target(심볼릭링크/'..' 해석 후)이 root 하위인가 — 게이트의 리포 밖 우회 차단."""
    try:
        target.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def verify_entry(root: Path, entry: object) -> list[str]:
    """단일 매니페스트 항목 검증 → 실패 사유 리스트(빈 리스트=PASS)."""
    if not isinstance(entry, dict):
        return [f"매니페스트 항목이 객체(dict)가 아님: {entry!r}"]

    fails: list[str] = []
    rel = entry.get("path")
    if not rel or not isinstance(rel, str):
        return ["매니페스트 항목에 유효한 'path' 누락"]
    # path는 root 기준 상대경로여야 함 — 절대경로/'..' 이탈은 게이트를 리포 밖으로 우회시킴
    if Path(rel).is_absolute():
        return [f"절대경로 불허 (path는 root 기준 상대경로): {rel}"]
    target = root / rel
    if not _within_root(target, root):
        return [f"root 이탈 경로 불허 ('..' 등): {rel}"]

    # (1) 실존
    if not target.exists():
        return [f"산출물 부재 (디스크에 없음): {rel}"]
    if not target.is_file():
        return [f"파일이 아님: {rel}"]

    # (2) 비어있지 않음 / 최소 크기
    size = target.stat().st_size
    try:
        min_bytes = int(entry.get("min_bytes", 1))
    except (TypeError, ValueError):
        fails.append(f"min_bytes 비수치: {rel} ({entry.get('min_bytes')!r}) — 1로 간주")
        min_bytes = 1
    if min_bytes < 1:
        # 비어있지 않음(size≥1) 불변식 무력화 방지 — 0바이트 거짓 PASS 차단
        fails.append(f"min_bytes < 1 불허 (비어있지않음 무력화): {rel} ({min_bytes})")
        min_bytes = 1
    if size < min_bytes:
        fails.append(f"크기 미달: {rel} ({size}B < min_bytes {min_bytes})")

    # (3) SHA-256 핀 (선택)
    expected_sha = entry.get("sha256")
    if expected_sha:
        actual = _sha256(target)
        exp = str(expected_sha)
        if actual.lower() != exp.lower():
            fails.append(f"SHA 불일치: {rel} (기대 {exp[:12]}… ≠ 실측 {actual[:12]}…)")

    # (4) 필수 문자열 (부분 착시 방어)
    must = entry.get("must_contain") or []
    if isinstance(must, str):
        must = [must]  # 단일 문자열 → 글자단위 순회(거짓 GREEN) 방지
    if must:
        try:
            text = target.read_text(encoding="utf-8-sig", errors="replace")
        except OSError as e:
            fails.append(f"읽기 실패: {rel} ({e})")
        else:
            for needle in must:
                if not isinstance(needle, str):
                    fails.append(f"must_contain 항목 비문자열: {rel} → {needle!r}")
                elif needle not in text:
                    fails.append(f"필수 문자열 부재: {rel} → '{needle}'")

    # (5) 참조 테스트 파일 실존 (III-4 — 파일 실존만; 내용 참조 정합은 검사 안 함)
    #     path와 동일하게 절대경로/root 이탈 차단 — 게이트를 리포 밖 파일로 우회 금지
    ref = entry.get("referencing_test")
    if ref:
        if Path(ref).is_absolute():
            fails.append(f"referencing_test 절대경로 불허: {rel} → '{ref}'")
        else:
            matches = list(root.glob(ref)) if any(c in ref for c in "*?[") else [root / ref]
            if not any(p.is_file() and _within_root(p, root) for p in matches):
                fails.append(f"참조 테스트 파일 부재(또는 root 이탈): {rel} → '{ref}'")

    return fails


def _load_entries(manifest_path: Path) -> tuple[list | None, str | None]:
    """→ (entries, error_msg). 형식오류면 (None, msg)."""
    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, OSError) as e:
        return None, f"매니페스트 파싱 실패: {e}"
    if isinstance(raw, dict):
        if "artifacts" not in raw:
            return None, "매니페스트 dict에 'artifacts' 키 부재 — 형식 오류"
        entries = raw["artifacts"]
    elif isinstance(raw, list):
        entries = raw
    else:
        return None, "매니페스트 형식 오류 — list 또는 {'artifacts': [...]} 필요"
    if not isinstance(entries, list):
        return None, "'artifacts' 가 list 가 아님 — 형식 오류"
    return entries, None


def main() -> int:
    ap = argparse.ArgumentParser(description="산출물 실존 검증 게이트 (R16 착시 방어)")
    ap.add_argument("manifest", nargs="?", default=str(DEFAULT_MANIFEST),
                    help="매니페스트 JSON 경로 (기본: 스크립트 옆 artifact_manifest.json)")
    ap.add_argument("--root", default=None,
                    help="산출물 경로 기준 루트 (기본: 매니페스트 상위의 상위 = 리포 루트)")
    ap.add_argument("--mode", choices=["warn", "error"], default="error",
                    help="warn: 실패를 경고만 (exit 0) / error: 실패 시 exit 1")
    args = ap.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"[verify_artifacts] 매니페스트 부재: {manifest_path} — 검증 불가 (FAIL)")
        return 1 if args.mode == "error" else 0

    root = Path(args.root) if args.root else manifest_path.resolve().parent.parent
    entries, err = _load_entries(manifest_path)
    if err or entries is None:
        print(f"[verify_artifacts] {err}")
        return 1
    # 공허 매니페스트 = 무검증 통과 재생산 → 명시적 FAIL (안티착시 자기무력화 방지)
    if len(entries) == 0:
        print("[verify_artifacts] 매니페스트에 검증 대상 0건 — 공허 통과 차단 (FAIL)")
        return 1 if args.mode == "error" else 0

    n_pass = 0
    n_fail = 0
    for entry in entries:
        try:
            fails = verify_entry(root, entry)
        except Exception as e:  # noqa: BLE001 — 항목 단위 실패를 fail로 집계(warn 계약 보전)
            fails = [f"검증 중 예외: {e!r}"]
        label = entry.get("path", "<unknown>") if isinstance(entry, dict) else repr(entry)
        if fails:
            n_fail += 1
            for f in fails:
                print(f"FAIL {label}: {f}")
        else:
            n_pass += 1
            print(f"PASS {label}")

    print(f"[verify_artifacts] root={root} — PASS {n_pass} / FAIL {n_fail} (mode={args.mode})")
    if n_fail and args.mode == "error":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
