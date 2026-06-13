"""락파일 정합 게이트 (§4 V-2 — 환경 drift발 실패를 모델 탓으로 오인 방지).

3-스택 의존성 락파일이 매니페스트(pyproject/package.json/Cargo.toml)와
정합하는지 검증한다. 대상 스택의 매니페스트가 아직 없으면(예: 프론트/Tauri 미생성)
'보류(deferred)'로 표시하고 통과시킨다 — 없는 것을 실패로 처리하지 않는다.

검사:
  Python: backend/pyproject.toml [tool.poetry.dependencies] + 모든 group.*.dependencies
          (ruff/mypy/pytest 등 dev 포함)의 각 패키지가 backend/poetry.lock에
          등장하는가. 패키지명은 PEP 503 정규화([-_.]→'-', lower) 후 대조.
  Node  : package.json 존재 시 같은 디렉토리의 pnpm-lock.yaml 필수 (없으면 보류).
  Rust  : Cargo.toml(또는 src-tauri/Cargo.toml) 존재 시 같은 디렉토리의 Cargo.lock 필수.

사용: python scripts/check_lockfiles.py [--root DIR] [--mode warn|error]
종료 코드: 0=drift 없음(보류 허용), 1=drift 존재(error 모드).
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_NORM_RE = re.compile(r"[-_.]+")
_LOCK_NAME_RE = re.compile(r'(?m)^name\s*=\s*"([^"]+)"')


def _norm(name: str) -> str:
    """PEP 503 정규화: 소문자 + 연속 [-_.]를 단일 '-'로."""
    return _NORM_RE.sub("-", name.lower())


def _collect_deps(data: dict) -> dict:
    """[tool.poetry.dependencies] + 모든 group.*.dependencies 병합 (python 제외)."""
    poetry = data.get("tool", {}).get("poetry", {})
    deps: dict = dict(poetry.get("dependencies", {}))
    for grp in poetry.get("group", {}).values():
        if isinstance(grp, dict):
            deps.update(grp.get("dependencies", {}))
    deps.pop("python", None)
    return deps


def check_python(root: Path) -> tuple[list[str], list[str]]:
    """→ (fails, notes)."""
    fails: list[str] = []
    notes: list[str] = []
    pyproject = root / "backend" / "pyproject.toml"
    lock = root / "backend" / "poetry.lock"
    if not pyproject.exists():
        notes.append("Python: backend/pyproject.toml 부재 — 보류")
        return fails, notes
    if not lock.exists() or lock.stat().st_size == 0:
        fails.append("Python: poetry.lock 부재/빈 파일 — 의존성 락 없음 (drift)")
        return fails, notes
    try:
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, OSError) as e:
        fails.append(f"Python: pyproject 파싱 실패 ({e})")
        return fails, notes
    deps = _collect_deps(data)
    lock_text = lock.read_text(encoding="utf-8", errors="replace")
    lock_names = {_norm(n) for n in _LOCK_NAME_RE.findall(lock_text)}
    for name in deps:
        if _norm(name) not in lock_names:
            fails.append(f"Python: '{name}' 가 poetry.lock에 없음 — lock 재생성 필요 (drift)")
    if not fails:
        notes.append(f"Python: pyproject 의존성(main+dev) {len(deps)}개 전건 lock 정합")
    return fails, notes


def check_pair(root: Path, manifest_rel: list[str], lock_name: str,
               stack: str) -> tuple[list[str], list[str]]:
    """존재하는 *모든* 매니페스트 각각에 대해 같은 디렉토리의 락파일 필수.

    없으면 보류 (Node/Rust 공통). monorepo(루트+하위 동시 존재) 시 누락 없이 전수 검사.
    """
    fails: list[str] = []
    notes: list[str] = []
    manifests = [root / m for m in manifest_rel if (root / m).exists()]
    if not manifests:
        notes.append(f"{stack}: 매니페스트 부재 — 보류 (대상 스택 미생성)")
        return fails, notes
    for manifest in manifests:
        lock = manifest.parent / lock_name
        rel = lock.relative_to(root) if lock.is_relative_to(root) else lock
        loc = manifest.parent.name or "."
        if not lock.exists() or lock.stat().st_size == 0:
            fails.append(f"{stack}: {manifest.name}({loc}) 존재하나 {rel} 부재 — 락 누락 (drift)")
        else:
            notes.append(f"{stack}: {manifest.name} ↔ {rel} 정합")
    return fails, notes


def main() -> int:
    ap = argparse.ArgumentParser(description="락파일 정합 게이트 (3-스택, 보류 허용)")
    ap.add_argument("--root", default=".", help="리포 루트 (기본 현재 디렉토리)")
    ap.add_argument("--mode", choices=["warn", "error"], default="error")
    args = ap.parse_args()
    root = Path(args.root).resolve()

    all_fails: list[str] = []
    all_notes: list[str] = []
    for fn in (
        check_python(root),
        check_pair(root, ["package.json", "frontend/package.json"], "pnpm-lock.yaml", "Node"),
        check_pair(root, ["Cargo.toml", "src-tauri/Cargo.toml"], "Cargo.lock", "Rust"),
    ):
        all_fails.extend(fn[0])
        all_notes.extend(fn[1])

    for n in all_notes:
        print(f"  · {n}")
    for f in all_fails:
        print(f"FAIL {f}")
    print(f"[check_lockfiles] drift {len(all_fails)}건 (mode={args.mode})")
    if all_fails and args.mode == "error":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
