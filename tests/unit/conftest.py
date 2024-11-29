from __future__ import annotations

from pathlib import Path

import pytest


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Apply the unit marker to all tests in the unit test directory."""
    unit_test_directory = Path(__file__).parent
    for item in items:
        if unit_test_directory in item.path.parents:
            item.add_marker(pytest.mark.unit)
            if "order" not in [mark.name for mark in item.own_markers]:
                item.add_marker(pytest.mark.order("first"))
