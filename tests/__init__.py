"""Shared test helpers."""

from __future__ import annotations

import json
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(filename: str) -> str:
    """Return the raw text of a fixture file."""
    return (FIXTURES_DIR / filename).read_text()


def load_fixture_json(filename: str) -> object:
    """Return the parsed JSON of a fixture file."""
    return json.loads(load_fixture(filename))
