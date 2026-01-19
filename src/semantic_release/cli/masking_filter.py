from __future__ import annotations

import re
from collections import defaultdict
from logging import Filter as LoggingFilter
from typing import TYPE_CHECKING

from semantic_release.globals import logger

if TYPE_CHECKING:  # pragma: no cover
    from logging import LogRecord
    from typing import Iterable


# https://relaxdiego.com/2014/07/logging-in-python.html
# Updated/adapted for Python3
class MaskingFilter(LoggingFilter):
    REPLACE_STR = "*" * 4
    _UNWANTED = frozenset([s for obj in ("", None) for s in (repr(obj), str(obj))])

    def __init__(
        self,
        _use_named_masks: bool = False,
        **patterns: Iterable[str | re.Pattern[str]],
    ) -> None:
        super().__init__()
        self._redact_patterns = defaultdict(set)
        for k, vs in patterns.items():
            self._redact_patterns[k] = {v for v in vs if v and v not in self._UNWANTED}
        self._use_named_masks = _use_named_masks

    def add_mask_for(self, data: str, name: str = "redacted") -> MaskingFilter:
        if data and data not in self._UNWANTED:
            logger.debug("Adding redact pattern '%r' to redact_patterns", name)
            self._redact_patterns[name].add(data)
        return self

    def filter(self, record: LogRecord) -> bool:
        # Note if we blindly mask all types, we will actually cast arguments to
        # log functions from external libraries to strings before they are
        # formatted into the message - for example, a dependency calling
        # log.debug("%d", 15) will raise a TypeError as this filter would
        # otherwise convert 15 to "15", and "%d" % "15" raises the error.
        # One may find a specific example of where this issue could manifest itself
        # here: https://github.com/urllib3/urllib3/blob/a5b29ac1025f9bb30f2c9b756f3b171389c2c039/src/urllib3/connectionpool.py#L1003
        # Anything which could reasonably be expected to be logged without being
        # cast to a string should be excluded from the cast here.
        record.msg = self.mask(record.msg)
        if record.args is None:
            pass
        elif isinstance(record.args, dict):
            record.args = {
                k: v if type(v) in (bool, int, float) else self.mask(str(v))
                for k, v in record.args.items()
            }
        else:
            record.args = tuple(
                arg if type(arg) in (bool, int, float) else self.mask(str(arg))
                for arg in record.args
            )
        return True

    def mask(self, msg: str) -> str:
        if not isinstance(msg, str):
            logger.debug("cannot mask object of type %s", type(msg))
            return msg
        for mask, values in self._redact_patterns.items():
            repl_string = (
                self.REPLACE_STR
                if not self._use_named_masks
                else f"<{mask!r} (value removed)>"
            )
            for data in values:
                if isinstance(data, str):
                    msg = msg.replace(data, repl_string)
                elif isinstance(data, re.Pattern):
                    msg = data.sub(repl_string, msg)
        return msg
