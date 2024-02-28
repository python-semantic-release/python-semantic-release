import pytest

from semantic_release.helpers import ParsedGitUrl, parse_git_url


@pytest.mark.parametrize(
    "url, expected",
    [
        (
            "http://git.mycompany.com/username/myproject.git",
            ParsedGitUrl("http", "git.mycompany.com", "username", "myproject"),
        ),
        (
            "http://subsubdomain.subdomain.company-net.com/username/myproject.git",
            ParsedGitUrl(
                "http",
                "subsubdomain.subdomain.company-net.com",
                "username",
                "myproject",
            ),
        ),
        (
            "https://github.com/username/myproject.git",
            ParsedGitUrl("https", "github.com", "username", "myproject"),
        ),
        (
            "https://gitlab.com/group/subgroup/myproject.git",
            ParsedGitUrl("https", "gitlab.com", "group/subgroup", "myproject"),
        ),
        (
            "https://git.mycompany.com:4443/username/myproject.git",
            ParsedGitUrl("https", "git.mycompany.com:4443", "username", "myproject"),
        ),
        (
            "https://subsubdomain.subdomain.company-net.com/username/myproject.git",
            ParsedGitUrl(
                "https",
                "subsubdomain.subdomain.company-net.com",
                "username",
                "myproject",
            ),
        ),
        (
            "git://host.xz/path/to/repo.git/",
            ParsedGitUrl("git", "host.xz", "path/to", "repo"),
        ),
        (
            "git://host.xz:9418/path/to/repo.git/",
            ParsedGitUrl("git", "host.xz:9418", "path/to", "repo"),
        ),
        (
            "git@github.com:username/myproject.git",
            ParsedGitUrl("ssh", "git@github.com", "username", "myproject"),
        ),
        (
            "git@subsubdomain.subdomain.company-net.com:username/myproject.git",
            ParsedGitUrl(
                "ssh",
                "git@subsubdomain.subdomain.company-net.com",
                "username",
                "myproject",
            ),
        ),
        (
            "first.last_test-1@subsubdomain.subdomain.company-net.com:username/myproject.git",
            ParsedGitUrl(
                "ssh",
                "first.last_test-1@subsubdomain.subdomain.company-net.com",
                "username",
                "myproject",
            ),
        ),
        (
            "ssh://git@github.com:3759/myproject.git",
            ParsedGitUrl("ssh", "git@github.com", "3759", "myproject"),
        ),
        (
            "ssh://git@github.com:username/myproject.git",
            ParsedGitUrl("ssh", "git@github.com", "username", "myproject"),
        ),
        (
            "ssh://git@bitbucket.org:7999/username/myproject.git",
            ParsedGitUrl("ssh", "git@bitbucket.org:7999", "username", "myproject"),
        ),
        (
            "ssh://git@subsubdomain.subdomain.company-net.com:username/myproject.git",
            ParsedGitUrl(
                "ssh",
                "git@subsubdomain.subdomain.company-net.com",
                "username",
                "myproject",
            ),
        ),
        (
            "git+ssh://git@github.com:username/myproject.git",
            ParsedGitUrl("ssh", "git@github.com", "username", "myproject"),
        ),
        (
            "/Users/username/dev/remote/myproject.git",
            ParsedGitUrl("file", "", "Users/username/dev/remote", "myproject"),
        ),
        (
            "file:///Users/username/dev/remote/myproject.git",
            ParsedGitUrl("file", "", "Users/username/dev/remote", "myproject"),
        ),
        (
            "C:/Users/username/dev/remote/myproject.git",
            ParsedGitUrl("file", "", "C:/Users/username/dev/remote", "myproject"),
        ),
        (
            "file:///C:/Users/username/dev/remote/myproject.git",
            ParsedGitUrl("file", "", "C:/Users/username/dev/remote", "myproject"),
        ),
    ],
)
def test_parse_valid_git_urls(url: str, expected: ParsedGitUrl):
    """Test that a valid given git remote url is parsed correctly."""
    assert expected == parse_git_url(url)


@pytest.mark.parametrize(
    "url",
    [
        "icmp://git",
        "abcdefghijklmnop.git",
        "../relative/path/to/repo.git",
        "http://domain/project.git",
    ],
)
def test_parse_invalid_git_urls(url: str):
    """Test that an invalid git remote url throws a ValueError."""
    with pytest.raises(ValueError):
        parse_git_url(url)
