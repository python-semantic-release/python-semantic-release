import pytest
import tomlkit

from semantic_release.cli.config import RawConfig


def test_default_toml_config_valid(example_project):
    default_config_file = example_project / "default.toml"
    default_config_file.write_text(tomlkit.dumps(RawConfig().dict(exclude_none=True)))

    written = default_config_file.read_text(encoding="utf-8")
    loaded = tomlkit.loads(written)
    # Check that we can load it correctly
    parsed = RawConfig.parse_obj(loaded)
    assert parsed
    # Check the re-loaded internal representation is sufficient
    # There is an issue with BaseModel.__eq__ that means
    # comparing directly doesn't work with parsed.dict(); this
    # is because of how tomlkit parsed toml
