"""BLUE NODE 디렉토리 스캐폴딩 검증 (4-6) — 구현 0 + seed 충돌 없음."""

from __future__ import annotations

from vamos_core import blue_nodes
from vamos_core.blue_nodes import content, dev, research
from vamos_core.schemas import registries


def test_v0_domains_are_dev_research_content() -> None:
    assert blue_nodes.V0_BLUE_NODE_DOMAINS == ("dev", "research", "content")
    assert dev.DOMAIN == "dev"
    assert research.DOMAIN == "research"
    assert content.DOMAIN == "content"


def test_node_registry_seed_no_conflict_with_scaffold() -> None:
    """seed 노드 도메인이 V0 스캐폴딩 3 도메인 부분집합 — 충돌 없음(registries 수정 0)."""
    seed_domains = {n["domain"] for n in registries.NODE_REGISTRY_SEED}
    assert seed_domains <= set(blue_nodes.V0_BLUE_NODE_DOMAINS)
    assert "research" in seed_domains  # bn_web_research
