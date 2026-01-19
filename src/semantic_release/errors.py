"""Custom Errors"""


class SemanticReleaseBaseError(Exception):
    """
    Base Exception from which all other custom Exceptions defined in semantic_release
    inherit
    """


class InternalError(SemanticReleaseBaseError):
    """Raised when an internal error occurs, which should never happen"""


class InvalidConfiguration(SemanticReleaseBaseError):
    """Raised when configuration is deemed invalid"""


class InvalidParserOptions(InvalidConfiguration):
    """Raised when the parser options are invalid"""


class MissingGitRemote(SemanticReleaseBaseError):
    """Raised when repository is missing the configured remote origin or upstream"""


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


class DetachedHeadGitError(SemanticReleaseBaseError):
    """Raised when the git repository is in a detached HEAD state"""


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
    Raised when there is a failure to find, load, or instantiate a custom parser
    definition.
    """


class BuildDistributionsError(SemanticReleaseBaseError):
    """Raised when there is a failure to build the distribution files."""


class GitAddError(SemanticReleaseBaseError):
    """Raised when there is a failure to add files to the git index."""


class GitCommitError(SemanticReleaseBaseError):
    """Raised when there is a failure to commit the changes."""


class GitCommitEmptyIndexError(SemanticReleaseBaseError):
    """Raised when there is an attempt to commit an empty index."""


class GitTagError(SemanticReleaseBaseError):
    """Raised when there is a failure to tag the release."""


class GitPushError(SemanticReleaseBaseError):
    """Raised when there is a failure to push to the git remote."""


class GitFetchError(SemanticReleaseBaseError):
    """Raised when there is a failure to fetch from the git remote."""


class LocalGitError(SemanticReleaseBaseError):
    """Raised when there is a failure with local git operations."""


class UnknownUpstreamBranchError(SemanticReleaseBaseError):
    """Raised when the upstream branch cannot be determined."""


class UpstreamBranchChangedError(SemanticReleaseBaseError):
    """Raised when the upstream branch has changed before pushing."""
