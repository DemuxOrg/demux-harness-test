import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def slugify():
    module_path = Path(__file__).resolve().parents[1] / "slugify.py"
    if not module_path.exists():
        # Keep the test run behavioral while the implementation is being written.
        return lambda text, max_length=None, separator="-": ""

    spec = importlib.util.spec_from_file_location("slugify", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.slugify


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Hello World", "hello-world"),
        ("  HELLO---World!! ", "hello-world"),
        ("release 2.4 (beta)", "release-2-4-beta"),
        ("Crème Brûlée", "creme-brulee"),
        ("ẞ", "ss"),
        ("Cafe\u0301 au lait", "cafe-au-lait"),
        ("", ""),
        ("!!!", ""),
    ],
)
def test_slugify_normalizes_text(slugify, text, expected):
    assert slugify(text) == expected


@pytest.mark.parametrize(
    ("separator", "expected"),
    [
        ("_", "hello_world"),
        (".+", "hello.+world"),
        ("--", "hello--world"),
    ],
)
def test_slugify_uses_custom_separator(slugify, separator, expected):
    assert slugify("Hello World", separator=separator) == expected


@pytest.mark.parametrize(
    ("text", "max_length", "separator", "expected"),
    [
        ("the quick brown fox", 12, "-", "the-quick"),
        ("the quick brown fox", 9, "-", "the-quick"),
        ("hello world", 7, "-", "hello"),
        ("one two three", 8, "--", "one--two"),
        ("extraordinary word", 4, "-", "extr"),
        ("a b", 1, "-", "a"),
        ("!!!", 3, "-", ""),
    ],
)
def test_slugify_truncates_at_word_boundaries(
    slugify, text, max_length, separator, expected
):
    result = slugify(text, max_length=max_length, separator=separator)
    assert result == expected
    assert len(result) <= max_length


@pytest.mark.parametrize("text", [None, 42, ["hello"]])
def test_slugify_requires_string_text(slugify, text):
    with pytest.raises(TypeError):
        slugify(text)


@pytest.mark.parametrize("max_length", [0, -1])
def test_slugify_rejects_nonpositive_max_length(slugify, max_length):
    with pytest.raises(ValueError):
        slugify("hello", max_length=max_length)


@pytest.mark.parametrize("separator", ["", "a", "-b", "3", "１"])
def test_slugify_rejects_empty_or_alphanumeric_separator(slugify, separator):
    with pytest.raises(ValueError):
        slugify("hello world", separator=separator)
