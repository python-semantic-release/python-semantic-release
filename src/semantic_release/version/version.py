from __future__ import annotations

import re
from functools import wraps
from itertools import zip_longest
from typing import Callable, Union, overload

from semantic_release.const import SEMVER_REGEX
from semantic_release.enums import LevelBump
from semantic_release.errors import InvalidVersion
from semantic_release.globals import logger
from semantic_release.helpers import check_tag_format

# Very heavily inspired by semver.version:_comparator, I don't think there's
# a cleaner way to do this
# https://github.com/python-semver/python-semver/blob/b5317af9a7e99e6a86df98320e73be72d5adf0de/src/semver/version.py#L32
VersionComparable = Union["Version", str]
VersionComparator = Callable[["Version", "Version"], bool]


@overload
def _comparator(
    *,
    type_guard: bool,
) -> Callable[[VersionComparator], VersionComparator]: ...


@overload
def _comparator(
    method: VersionComparator, *, type_guard: bool = True
) -> VersionComparator: ...


def _comparator(
    method: VersionComparator | None = None, *, type_guard: bool = True
) -> VersionComparator | Callable[[VersionComparator], VersionComparator]:
    """
    wrap a `Version` binop method to guard types and try to parse strings into Versions.
    use `type_guard = False` for `__eq__` and `__neq__` to make them return False if the
    wrong type is used, instead of erroring.
    """
    if method is None:
        return lambda method: _comparator(method, type_guard=type_guard)

    @wraps(method)
    def _wrapper(self: Version, other: VersionComparable) -> bool:
        if not isinstance(other, (str, Version)):
            return False if not type_guard else NotImplemented
        if isinstance(other, str):
            try:
                other_v = self.parse(
                    other,
                    tag_format=self.tag_format,
                    prerelease_token=self.prerelease_token,
                )
            except InvalidVersion as ex:
                raise TypeError(str(ex)) from ex
        else:
            other_v = other

        return method(self, other_v)  # type: ignore[misc]

    return _wrapper


class Version:
    _VERSION_REGEX = SEMVER_REGEX

    def __init__(
        self,
        major: int,
        minor: int,
        patch: int,
        *,
        prerelease_token: str = "rc",  # noqa: S107
        prerelease_revision: int | None = None,
        build_metadata: str = "",
        tag_format: str = "v{version}",
    ) -> None:
        self.major = major
        self.minor = minor
        self.patch = patch
        self.prerelease_token = prerelease_token
        self.prerelease_revision = prerelease_revision
        self.build_metadata = build_metadata
        self._tag_format = tag_format

    @property
    def tag_format(self) -> str:
        return self._tag_format

    @tag_format.setter
    def tag_format(self, new_format: str) -> None:
        check_tag_format(new_format)
        self._tag_format = new_format

    # Maybe cache?
    @classmethod
    def parse(
        cls,
        version_str: str,
        tag_format: str = "v{version}",
        prerelease_token: str = "rc",  # noqa: S107
    ) -> Version:
        """
        Parse version string to a Version instance.
        Inspired by `semver.version:VersionInfo.parse`, this implementation doesn't
        allow optional minor and patch versions.

        :param prerelease_token: will be ignored if the version string is a prerelease,
            the parsed token from `version_str` will be used instead.
        """
        if not isinstance(version_str, str):
            raise InvalidVersion(f"{version_str!r} cannot be parsed as a Version")

        logger.debug("attempting to parse string %r as Version", version_str)
        match = cls._VERSION_REGEX.fullmatch(version_str)
        if not match:
            raise InvalidVersion(f"{version_str!r} is not a valid Version")

        prerelease = match.group("prerelease")
        if prerelease:
            pm = re.match(r"(?P<token>[a-zA-Z0-9-\.]+)\.(?P<revision>\d+)", prerelease)
            if not pm:
                raise NotImplementedError(
                    f"{cls.__qualname__} currently supports only prereleases "
                    r"of the format (-([a-zA-Z0-9-])\.\(\d+)), for example "
                    r"'1.2.3-my-custom-3rc.4'."
                )
            prerelease_token, prerelease_revision = pm.groups()
            logger.debug(
                "parsed prerelease_token %s, prerelease_revision %s from version "
                "string %s",
                prerelease_token,
                prerelease_revision,
                version_str,
            )
        else:
            prerelease_revision = None
            logger.debug("version string %s parsed as a non-prerelease", version_str)

        build_metadata = match.group("buildmetadata") or ""
        logger.debug(
            "parsed build metadata %r from version string %s",
            build_metadata,
            version_str,
        )

        return Version(
            int(match.group("major")),
            int(match.group("minor")),
            int(match.group("patch")),
            prerelease_token=prerelease_token,
            prerelease_revision=(
                int(prerelease_revision) if prerelease_revision else None
            ),
            build_metadata=build_metadata,
            tag_format=tag_format,
        )

    @property
    def is_prerelease(self) -> bool:
        return self.prerelease_revision is not None

    def __str__(self) -> str:
        full = f"{self.major}.{self.minor}.{self.patch}"
        prerelease = (
            f"-{self.prerelease_token}.{self.prerelease_revision}"
            if self.prerelease_revision
            else ""
        )
        build_metadata = f"+{self.build_metadata}" if self.build_metadata else ""
        return f"{full}{prerelease}{build_metadata}"

    def __repr__(self) -> str:
        prerelease_token_repr = (
            repr(self.prerelease_token) if self.prerelease_token is not None else None
        )
        prerelease_revision_repr = (
            repr(self.prerelease_revision)
            if self.prerelease_revision is not None
            else None
        )
        build_metadata_repr = (
            repr(self.build_metadata) if self.build_metadata is not None else None
        )
        return (
            f"{type(self).__qualname__}("
            + ", ".join(
                (
                    f"major={self.major}",
                    f"minor={self.minor}",
                    f"patch={self.patch}",
                    f"prerelease_token={prerelease_token_repr}",
                    f"prerelease_revision={prerelease_revision_repr}",
                    f"build_metadata={build_metadata_repr}",
                    f"tag_format={self.tag_format!r}",
                )
            )
            + ")"
        )

    def as_tag(self) -> str:
        return self.tag_format.format(version=str(self))

    def as_major_tag(self) -> str:
        return self.tag_format.format(version=f"{self.major}")

    def as_minor_tag(self) -> str:
        return self.tag_format.format(version=f"{self.major}.{self.minor}")

    def as_patch_tag(self) -> str:
        return self.tag_format.format(version=f"{self.major}.{self.minor}.{self.patch}")

    def as_semver_tag(self) -> str:
        return f"v{self!s}"

    def bump(self, level: LevelBump) -> Version:
        """
        Return a new Version instance according to the level specified to bump.
        Note this will intentionally drop the build metadata - that should be added
        elsewhere for the specific build producing this version.
        """
        if type(level) != LevelBump:
            raise TypeError(f"Unexpected level {level!r}: expected {LevelBump!r}")

        logger.debug("performing a %s level bump", level)
        if level is LevelBump.MAJOR:
            return Version(
                self.major + 1,
                0,
                0,
                prerelease_token=self.prerelease_token,
                prerelease_revision=1 if self.is_prerelease else None,
                tag_format=self.tag_format,
            )
        if level is LevelBump.MINOR:
            return Version(
                self.major,
                self.minor + 1,
                0,
                prerelease_token=self.prerelease_token,
                prerelease_revision=1 if self.is_prerelease else None,
                tag_format=self.tag_format,
            )
        if level is LevelBump.PATCH:
            return Version(
                self.major,
                self.minor,
                self.patch + 1,
                prerelease_token=self.prerelease_token,
                prerelease_revision=1 if self.is_prerelease else None,
                tag_format=self.tag_format,
            )
        if level is LevelBump.PRERELEASE_REVISION:
            return Version(
                self.major,
                self.minor,
                self.patch,
                prerelease_token=self.prerelease_token,
                prerelease_revision=1
                if not self.is_prerelease
                else (self.prerelease_revision or 0) + 1,
                tag_format=self.tag_format,
            )
        # for consistency, this creates a new instance regardless
        # only other option is level is LevelBump.NO_RELEASE
        return Version(
            self.major,
            self.minor,
            self.patch,
            prerelease_token=self.prerelease_token,
            prerelease_revision=self.prerelease_revision,
            tag_format=self.tag_format,
        )

    # Enables Version + LevelBump.<level>
    __add__ = bump

    def __hash__(self) -> int:
        # If we use str(self) we don't capture tag_format, so another
        # instance with a tag_format "special_{version}_format" would
        # collide with an instance using "v{version}"/other format
        return hash(self.__repr__())

    @_comparator(type_guard=False)
    def __eq__(self, other: Version) -> bool:  # type: ignore[override]
        # https://semver.org/#spec-item-11 -
        # build metadata is not used for comparison
        return all(
            getattr(self, attr) == getattr(other, attr)
            for attr in (
                "major",
                "minor",
                "patch",
                "prerelease_token",
                "prerelease_revision",
            )
        )

    @_comparator(type_guard=False)
    def __neq__(self, other: Version) -> bool:
        return not self.__eq__(other)

    # mypy wants to compare signature types with __lt__,
    # but can't because of the decorator
    @_comparator
    def __gt__(self, other: Version) -> bool:  # type: ignore[has-type]
        # https://semver.org/#spec-item-11 -
        # build metadata is not used for comparison

        # Note we only support the following versioning currently, which
        # is a subset of the full spec:
        # (\d+\.\d+\.\d+)(-\w+\.\d+)?(\+.*)?
        if self.major != other.major:
            return self.major > other.major
        if self.minor != other.minor:
            return self.minor > other.minor
        if self.patch != other.patch:
            return self.patch > other.patch
        # If just one is a prerelease, then self > other if other is the prerelease
        # If neither are prereleases then they're equal (so return False)
        if not (self.is_prerelease and other.is_prerelease):
            return other.is_prerelease
        # If both are prereleases...
        # According to the semver spec 11.4 there are many other rules for
        # comparing precedence of pre-release versions. Here we just compare
        # the prerelease tokens, and their revision numbers
        if self.prerelease_token != other.prerelease_token:
            for self_tk, other_tk in zip_longest(
                self.prerelease_token.split("."),
                other.prerelease_token.split("."),
                fillvalue=None,
            ):
                if self_tk == other_tk:
                    continue
                if (self_tk is None) ^ (other_tk is None):
                    # Longest token (i.e. non-None) is greater
                    return other_tk is None
                # Lexical sort, e.g. "rc" > "beta" > "alpha"
                # we have eliminated that one or both might be None above,
                # but mypy doesn't recognise this
                return self_tk > other_tk  # type: ignore[operator]
        # We have eliminated that one or both aren't prereleases by the above
        return self.prerelease_revision > other.prerelease_revision  # type: ignore[operator]  # noqa: E501

    # mypy wants to compare signature types with __le__,
    # but can't because of the decorator
    @_comparator
    def __ge__(self, other: Version) -> bool:  # type: ignore[has-type]
        return self.__gt__(other) or self.__eq__(other)

    @_comparator
    def __lt__(self, other: Version) -> bool:
        return not (self.__gt__(other) or self.__eq__(other))

    @_comparator
    def __le__(self, other: Version) -> bool:
        return not self.__gt__(other)

    def __sub__(self, other: Version) -> LevelBump:
        if not isinstance(other, Version):
            return NotImplemented

        if self.major != other.major:
            return LevelBump.MAJOR
        if self.minor != other.minor:
            return LevelBump.MINOR
        if self.patch != other.patch:
            return LevelBump.PATCH
        if self.is_prerelease ^ other.is_prerelease:
            return max(
                self.finalize_version() - other.finalize_version(),
                LevelBump.PRERELEASE_REVISION,
            )
        if self.prerelease_revision != other.prerelease_revision:
            return LevelBump.PRERELEASE_REVISION
        return LevelBump.NO_RELEASE

    def to_prerelease(
        self, token: str | None = None, revision: int | None = None
    ) -> Version:
        return Version(
            self.major,
            self.minor,
            self.patch,
            prerelease_token=token or self.prerelease_token,
            prerelease_revision=(revision or self.prerelease_revision) or 1,
            tag_format=self.tag_format,
        )

    def finalize_version(self) -> Version:
        return Version(
            self.major,
            self.minor,
            self.patch,
            prerelease_token=self.prerelease_token,
            tag_format=self.tag_format,
        )
