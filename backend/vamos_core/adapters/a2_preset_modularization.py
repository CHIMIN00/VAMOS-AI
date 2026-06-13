"""A-2 Preset Modularization (프리셋 모듈화) — V1 CORE 6-3 결정론 프리셋 CRUD.

정본: D2.0-01 §5.9 (A-2 CORE, V1:ON, owner D5, builder/panel, ties I-13 + 03/05) +
docs/guides/VAMOS_구현가이드_PART2_구현단계.md §6 (프리셋 = 재사용 설정 번들).

6-3 범위(결정론): 프리셋 번들 등록/조회/목록/적용(파라미터 병합)/수정/삭제 — JSON 직렬화,
정확매칭·카테고리 필터(의미검색·RAG 없음 = 6-4/V2+). I-13(출력 렌더) 템플릿 조합. 결과는
모듈 내부 dataclass(D5 owner, 계약 25 무변경). 프리셋은 모듈 설정 묶음(임계/도구선택 등).
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PresetBundle:
    """프리셋 번들 — PART2 §6 (id/name/category/params/version, D5 owner, 모듈 내부)."""

    id: str
    name: str
    category: str = "general"
    params: dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"


class PresetStore:
    """A-2 — 결정론 프리셋 레지스트리(인메모리). 영속화(JSON/DB)·의미검색 = 6-4/V2+."""

    def __init__(self) -> None:
        self._presets: dict[str, PresetBundle] = {}

    def register(self, preset: PresetBundle) -> str:
        """프리셋 등록 (id 중복 = 덮어쓰기 — 갱신). 반환 = preset id."""
        self._presets[preset.id] = preset
        return preset.id

    def get(self, preset_id: str) -> PresetBundle | None:
        return self._presets.get(preset_id)

    def list(self, category: str | None = None) -> list[PresetBundle]:
        """전체 또는 카테고리 필터 (정확매칭 — 의미검색 6-4)."""
        items = list(self._presets.values())
        if category is not None:
            items = [p for p in items if p.category == category]
        return items

    def apply(self, preset_id: str, context: dict[str, Any]) -> dict[str, Any]:
        """프리셋 params 를 context 에 병합 (프리셋 우선, 사용자 오버라이드 보존 — 결정론)."""
        preset = self._presets.get(preset_id)
        if preset is None:
            raise KeyError(f"미등록 프리셋: {preset_id!r}")
        merged = copy.deepcopy(context)
        for key, value in preset.params.items():
            merged.setdefault(key, value)  # 사용자 오버라이드(기존 키) 보존
        return merged

    def update(self, preset_id: str, params: dict[str, Any]) -> bool:
        """params 갱신 + version 증가 (semver minor)."""
        preset = self._presets.get(preset_id)
        if preset is None:
            return False
        preset.params = params
        # 마지막 숫자 세그먼트 증가 (1.0→1.1, 1.0.0→1.0.1, 비정형→append) — 크래시 방지
        parts = preset.version.split(".")
        try:
            parts[-1] = str(int(parts[-1]) + 1)
        except (ValueError, IndexError):
            parts.append("1")
        preset.version = ".".join(parts)
        return True

    def delete(self, preset_id: str) -> bool:
        return self._presets.pop(preset_id, None) is not None
