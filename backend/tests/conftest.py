import json
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def lakefilter_json() -> dict:
    return json.loads((FIXTURES_DIR / "lakefilter_response.json").read_text())


@pytest.fixture
def lakeglimpse_html() -> str:
    return (FIXTURES_DIR / "lakeglimpse_response.html").read_text()
