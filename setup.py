from setuptools import find_packages, setup

# According to setuptools docs, support for a [tool.setuptools] table
# in pyproject.toml is still in beta. So things which would have needed
# to go in that table are still specified here.
# https://setuptools.pypa.io/en/stable/userguide/pyproject_config.html#setuptools-specific-configuration
setup(
    packages=[*find_packages(exclude=("tests",)), "semantic_release.data.templates"],
    include_package_data=True,
)
