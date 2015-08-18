# -*- coding: utf-8 -*-


class SemanticReleaseBaseError(Exception):
    pass


class ImproperConfigurationError(SemanticReleaseBaseError):
    pass


class UnknownCommitMessageStyle(SemanticReleaseBaseError):
    pass
