"""A-2 Preset Modularization 검증 — 결정론 프리셋 CRUD (PART2 §6, D5 owner).

register/get/list/apply/update/delete. apply 는 사용자 오버라이드 보존. 의미검색 = 6-4.
"""

from __future__ import annotations

from vamos_core.adapters.a2_preset_modularization import PresetBundle, PresetStore


def _preset() -> PresetBundle:
    return PresetBundle(id="p_fast_code", name="Fast Code", category="coding",
                        params={"temperature": 0.3, "sandbox": "docker"})


def test_register_and_get():
    s = PresetStore()
    s.register(_preset())
    got = s.get("p_fast_code")
    assert got is not None
    assert got.name == "Fast Code"


def test_list_category_filter():
    s = PresetStore()
    s.register(_preset())
    s.register(PresetBundle(id="p_research", name="Research", category="research"))
    assert len(s.list()) == 2
    assert [p.id for p in s.list(category="coding")] == ["p_fast_code"]


def test_apply_preserves_user_override():
    """프리셋 적용 — 사용자 오버라이드(기존 키) 보존, 신규 키만 주입."""
    s = PresetStore()
    s.register(_preset())
    merged = s.apply("p_fast_code", {"temperature": 0.9})
    assert merged["temperature"] == 0.9  # 사용자 우선
    assert merged["sandbox"] == "docker"  # 프리셋 주입


def test_apply_unknown_raises():
    s = PresetStore()
    try:
        s.apply("missing", {})
    except KeyError:
        pass
    else:
        raise AssertionError("미등록 프리셋은 KeyError")


def test_update_increments_version():
    s = PresetStore()
    s.register(_preset())
    assert s.update("p_fast_code", {"temperature": 0.1}) is True
    assert s.get("p_fast_code").version == "1.1"


def test_update_patch_version_no_crash():
    """patch 세그먼트(1.0.0) 버전도 크래시 없이 증가 (적대검증 수리)."""
    s = PresetStore()
    s.register(PresetBundle(id="p_v3", name="V3", version="1.0.0"))
    assert s.update("p_v3", {"k": 1}) is True
    assert s.get("p_v3").version == "1.0.1"


def test_delete():
    s = PresetStore()
    s.register(_preset())
    assert s.delete("p_fast_code") is True
    assert s.get("p_fast_code") is None
