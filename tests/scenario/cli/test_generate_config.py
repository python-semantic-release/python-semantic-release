# TODO
# import logging
#
# import pytest
#
# from semantic_release.cli import version
#
#
# @pytest.mark.parametrize(
#     "args, log_level",
#     [([], logging.WARNING), (["-v"], logging.INFO), (["-vv"], logging.DEBUG)],
# )
# def test_logging_configured_correctly(runner, args, log_level):
#     # system exit 2 or exit 1 if no args - why?
#     result = runner.invoke(version, args + ["--print"])
#     assert result.exit_code == 0
#     assert logging.getLogger().getEffectiveLevel() == log_level
