from typing import Generator

import pytest
from click.testing import CliRunner


@pytest.fixture
def cli_runner() -> Generator[CliRunner, None, None]:
    return CliRunner(mix_stderr=False)
