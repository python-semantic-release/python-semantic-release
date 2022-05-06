MAJOR = (
    "221",
    "feat(x): Add super-feature\n\n"
    "BREAKING CHANGE: Uses super-feature as default instead of dull-feature.",
    "Alice <alice@example.com>",
)
MAJOR2 = (
    "222",
    "feat(x): Add super-feature\n\nSome explanation\n\n"
    "BREAKING CHANGE: Uses super-feature as default instead of dull-feature.",
    "Alice <alice@example.com>",
)
MAJOR_MENTIONING_1_0_0 = (
    "223",
    "feat(x): Add super-feature\n\nSome explanation\n\n"
    "BREAKING CHANGE: Uses super-feature as default instead of dull-feature from v1.0.0.",
    "Alice <alice@example.com>",
)
MAJOR_MULTIPLE_FOOTERS = (
    "244",
    "feat(x): Lots of breaking changes\n\n"
    "BREAKING CHANGE: Breaking change 1\n\n"
    "Not a BREAKING CHANGE\n\n"
    "BREAKING CHANGE: Breaking change 2",
    "Alice <alice@example.com>",
)
MAJOR_EXCL_WITH_FOOTER = (
    "231",
    "feat(x)!: Add another feature\n\n"
    "BREAKING CHANGE: Another feature, another breaking change",
    "Alice <alice@example.com>",
)
MAJOR_EXCL_NOT_FOOTER = (
    "232",
    "fix!: Fix a big bug that everyone exploited\n\nThis is the reason you should not exploit bugs",
    "Alice <alice@example.com>",
)
MINOR = ("111", "feat(x): Add non-breaking super-feature", "Bob <bob@example.com>")
PATCH = ("24", "fix(x): Fix bug in super-feature", "Bob <bob@example.com>")
NO_TAG = ("191", "docs(x): Add documentation for super-feature", "John <john@example.com>")
UNKNOWN_STYLE = ("7", "random commits are the worst", "John <john@example.com>")

ALL_KINDS_OF_COMMIT_MESSAGES = [MINOR, MAJOR, MINOR, PATCH]
MINOR_AND_PATCH_COMMIT_MESSAGES = [MINOR, PATCH]
PATCH_COMMIT_MESSAGES = [PATCH, PATCH]
MAJOR_LAST_RELEASE_MINOR_AFTER = [MINOR, ("22", "1.1.0", "Doe <doe@example.com>"), MAJOR]
MAJOR_MENTIONING_LAST_VERSION = [MAJOR_MENTIONING_1_0_0, ("22", "1.0.0", "Doe <doe@example.com>"), MAJOR]
