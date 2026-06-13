"""5-7a 검증 드라이버 — Tauri 셸 Python 스폰(IPC) 통합 테스트 실행 (V0-STEP-3).

vamos_core를 import 가능한 인터프리터(= 본 스크립트를 실행한 poetry venv python)를
`VAMOS_PYTHON`으로 주입하고, Rust 브릿지 스폰 테스트(src-tauri/tests/bridge_spawn.rs)를
`cargo test`로 구동한다. cargo 부재 시 보류(비차단).

사용: poetry run python scripts/ipc_spawn_check.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import sysconfig

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND = os.path.join(ROOT, "backend")
SRC_TAURI = os.path.join(ROOT, "src-tauri")

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]


def main() -> int:
    cargo = shutil.which("cargo")
    if not cargo or not os.path.exists(os.path.join(SRC_TAURI, "Cargo.toml")):
        print("PENDING: cargo 또는 src-tauri 부재 — 5-7a 스폰 검증 보류(비차단)")
        return 0

    env = dict(os.environ)
    env["VAMOS_PYTHON"] = sys.executable          # 현재 venv python(vamos_core import 가능)
    env["VAMOS_BACKEND_DIR"] = BACKEND
    # site-packages를 PYTHONPATH로 보강(자식이 venv 밖 cwd라도 의존성 import 가능)
    purelib = sysconfig.get_paths().get("purelib", "")
    env["VAMOS_PYTHONPATH"] = os.pathsep.join(p for p in (BACKEND, purelib) if p)

    print(f"VAMOS_PYTHON={sys.executable}")
    print(f"VAMOS_BACKEND_DIR={BACKEND}")
    proc = subprocess.run(  # noqa: S603
        [cargo, "test", "--manifest-path", os.path.join(SRC_TAURI, "Cargo.toml"),
         "--test", "bridge_spawn", "--", "--nocapture"],
        env=env, text=True, encoding="utf-8", errors="replace",
    )
    if proc.returncode != 0:
        print("FAIL: 5-7a Python 스폰(IPC) 통합 테스트 실패")
        return 1
    print("✅ 5-7a PASS — Python 스폰 + ready + ping/pong + 디스패치 + 자동 재시작")
    return 0


if __name__ == "__main__":
    sys.exit(main())
