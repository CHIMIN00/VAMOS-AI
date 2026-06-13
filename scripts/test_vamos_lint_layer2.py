"""vamos_lint Layer 2 (VL-006~008) 단위 테스트 — 세션 P6-1a (6-2 B1').

⚠️ 본 파일은 *고의로* 잘못된 모듈 ID·bare 교차용어 픽스처를 포함한다. 하네스 vamos_lint는
`backend`만 스캔하므로(scripts 미스캔) 자기 오탐 없음. 실행:
  cd backend && poetry run python -m pytest ../scripts/test_vamos_lint_layer2.py -q

검증:
  - VL-006: 유효 범위 base ID 통과 / 범위 초과 ID flag.
  - VL-007: CORE/일반 파일에서 inert(교차용어 미강제) / COND·도메인 모듈 파일에서 강제.
  - VL-008: SOT 2 정본 등재 COND 통과 / 미등재 COND flag.
  - Layer 1(VL-001~005) 의미 무변경(회귀).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vamos_lint as vl  # noqa: E402


def _rules(text: str, path: str = "vamos_core/orange_core/x.py") -> list[str]:
    """lint_file 결과에서 rule_id 목록만 추출."""
    return [rule for rule, _line, _msg in vl.lint_file(Path(path), text)]


# ── VL-006 모듈 ID 형식·범위 ──────────────────────────────────────────────

def test_vl006_valid_base_ids_pass():
    text = 'a = "I-25"\nb = "B-6"\nc = "EVX-6"\nd = "S-8"'
    assert "VL-006" not in _rules(text)


def test_vl006_out_of_range_flagged():
    text = 'a = "I-99"\nb = "C-10"\nc = "EVX-7"'  # I>25, C>7, EVX>6 — 전부 범위 초과
    assert _rules(text).count("VL-006") == 3


def test_vl006_i_over_25_flagged():
    assert "VL-006" in _rules('x = "I-26"')
    assert "VL-006" not in _rules('x = "I-1"')


# ── VL-008 COND 모듈 참조 무결성 (SOT 2 연동) ──────────────────────────────

@pytest.mark.skipif(vl._load_cond_ids() is None, reason="SOT 2 COND 정본 부재")
def test_vl008_valid_cond_passes():
    assert "VL-008" not in _rules('ref = "COND-011"')  # 정본 등재


@pytest.mark.skipif(vl._load_cond_ids() is None, reason="SOT 2 COND 정본 부재")
def test_vl008_unknown_cond_flagged():
    assert "VL-008" in _rules('ref = "COND-200"')  # 미등재
    assert "VL-008" in _rules('ref = "COND-12"')   # 비정규(3자리 아님)


# ── VL-007 교차용어 접두사 (도메인/COND 모듈 한정) ─────────────────────────

def test_vl007_inert_on_core_file():
    # CORE 파일: bare 교차용어 써도 미강제 (V0 CORE 회귀 0의 근거)
    text = 'qod = 0.5\nx = "qod"\ngate = "open"\nscore = "high"'
    assert "VL-007" not in _rules(text, path="vamos_core/orange_core/i5.py")


def test_vl007_enforced_on_domain_module():
    text = 'MODULE_ID = "COND-011"\nmetric = "qod"\n'
    rules = _rules(text, path="cond_modules/cat_a/c011.py")
    assert "VL-007" in rules


def test_vl007_enforced_via_cond_modules_path():
    text = 'label = "gate"\n'
    assert "VL-007" in _rules(text, path="backend/cond_modules/x.py")


def test_vl007_prefixed_term_ok_on_domain():
    text = 'MODULE_ID = "COND-011"\nmetric = "aux_qod"\n'  # 접두사 있음
    assert "VL-007" not in _rules(text, path="cond_modules/cat_a/c011.py")


# ── Layer 1 회귀 (의미 무변경) ────────────────────────────────────────────

def test_vl001_still_active():
    text = 'from pydantic import BaseModel\nclass M(BaseModel):\n    class Config:\n        pass\n'
    assert "VL-001" in _rules(text)


def test_vl005_still_active():
    assert "VL-005" in _rules('EVENT = "BAD_UPPER"')  # event는 lower.dot 이어야


def test_layer1_clean_text_no_findings():
    assert _rules('x = 1\ny = "ok"') == []
