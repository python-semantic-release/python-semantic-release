# -*- coding: utf-8 -*-
"""Custom Errors
"""


class SemanticReleaseBaseError(Exception):
    pass


class InvalidConfiguration(SemanticReleaseBaseError):
    pass


class NotAReleaseBranch(InvalidConfiguration):
    pass


# ImproperConfigurationError = InvalidConfiguration


class CommitParseError(SemanticReleaseBaseError):
    pass


# TODO: backwards-compat
# UnknownCommitMessageStyleError = CommitParseError


class GitError(SemanticReleaseBaseError):
    pass


class CiVerificationError(SemanticReleaseBaseError):
    pass


class HvcsRepoParseError(SemanticReleaseBaseError):
    pass


class UploadFailed(SemanticReleaseBaseError):
    pass
