import mock  # noqa
import pytest

import semantic_release


@pytest.fixture(autouse=True)
def reset_config():
    """This fixture will be used for every test here.
    Since some tests here edit the configuration, we want to reload it.
    We also need to reload the modules that use config.
    """
    yield
    from importlib import reload

    reload(semantic_release.settings)
    reload(semantic_release.vcs_helpers)
    reload(semantic_release.history)
    reload(semantic_release.history.logs)


def wrapped_config_get(**kwargs):
    from semantic_release.settings import config

    return lambda *args: {**config, **kwargs}.get(*args)
