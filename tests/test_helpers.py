from semantic_release.helpers import trim_csv_str


def test_trim_csv_str():
    csv_str = "Apple,banana, mango, pineapple"
    assert trim_csv_str(csv_str) == ["Apple", "banana", "mango", "pineapple"]
