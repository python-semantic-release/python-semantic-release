# -*- coding: utf-8 -*-
"""Custom Errors
"""


class SemanticReleaseBaseError(Exception):
    pass


class ImproperConfigurationError(SemanticReleaseBaseError):
    pass


class UnknownCommitMessageStyleError(SemanticReleaseBaseError):
    pass


class CommitParseError(SemanticReleaseBaseError):
    pass


class GitError(SemanticReleaseBaseError):
    pass


class CiVerificationError(SemanticReleaseBaseError):
    pass


class HvcsRepoParseError(SemanticReleaseBaseError):
    pass


class UploadFailed(SemanticReleaseBaseError):
    pass
