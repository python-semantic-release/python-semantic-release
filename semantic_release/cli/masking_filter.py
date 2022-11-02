from __future__ import annotations

import logging
import re
import sys
from collections import defaultdict
from typing import Iterable, Union

if sys.version_info >= (3, 9):
    from re import Pattern
else:
    from typing import Pattern

log = logging.getLogger(__name__)


# https://relaxdiego.com/2014/07/logging-in-python.html
# Updated/adapted for Python3
class MaskingFilter(logging.Filter):
    REPLACE_STR = "*" * 4
    _UNWANTED = [s for obj in ("", None) for s in (repr(obj), str(obj))]

    def __init__(
        self,
        _use_named_masks: bool = False,
        **patterns: Iterable[Union[str, Pattern[str]]],
    ) -> None:
        super().__init__()
        self._redact_patterns = defaultdict(set)
        for k, vs in patterns.items():
            self._redact_patterns[k] = {v for v in vs if v and v not in self._UNWANTED}
        self._use_named_masks = _use_named_masks

    def add_mask_for(self, data: str, name: str = "redacted") -> MaskingFilter:
        if data and data not in self._UNWANTED:
            self._redact_patterns[name].add(data)
        return self

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = self.mask(record.msg)
        if record.args is None:
            pass
        elif isinstance(record.args, dict):
            record.args = {k: self.mask(str(v)) for k, v in record.args.items()}
        else:
            record.args = tuple(self.mask(str(arg)) for arg in record.args)
        return True

    def mask(self, msg: str) -> str:
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
