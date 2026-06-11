"""VAMOS 테스트 공통 Fixture (STRATEGY_09 §7.4 — PART2 L1541~1545 기반)."""

import os

import pytest

# Ollama 의존 테스트 스킵 (M-10)
OLLAMA_AVAILABLE = bool(os.getenv("OLLAMA_HOST"))


@pytest.fixture
def skip_without_ollama() -> None:
    if not OLLAMA_AVAILABLE:
        pytest.skip("Ollama not available")
