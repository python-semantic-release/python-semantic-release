"""Custom Errors"""


class SemanticReleaseBaseError(Exception):
    """
    Base Exception from which all other custom Exceptions defined in semantic_release
    inherit
    """


class InvalidConfiguration(SemanticReleaseBaseError):
    """Raised when configuration is deemed invalid"""


class InvalidVersion(ValueError, SemanticReleaseBaseError):
    """
    Raised when Version.parse attempts to parse a string containing
    an invalid version.
    """


class NotAReleaseBranch(InvalidConfiguration):
    """
    Raised when semantic_release is invoked on a branch which isn't configured for
    releases
    """


class CommitParseError(SemanticReleaseBaseError):
    """
    Raised when a commit cannot be parsed by a commit parser. Custom commit parsers
    should also raise this Exception
    """


class MissingMergeBaseError(SemanticReleaseBaseError):
    """
    Raised when the merge base cannot be found with the current history. Generally
    because of a shallow git clone.
    """


class UnexpectedResponse(SemanticReleaseBaseError):
    """
    Raised when an HTTP response cannot be parsed properly or the expected structure
    is not found.
    """


class IncompleteReleaseError(SemanticReleaseBaseError):
    """
    Raised when there is a failure amongst one of the api requests when creating a
    release on a remote hvcs.
    """


class AssetUploadError(SemanticReleaseBaseError):
    """
    Raised when there is a failure uploading an asset to a remote hvcs's release artifact
    storage.
    """


class ParserLoadError(SemanticReleaseBaseError):
    """
    Raised when there is a failure to find, load, or instaniate a custom parser
    definition.
    """
