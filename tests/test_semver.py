"""Behavioral acceptance tests for the root-level semantic version API."""

from dataclasses import dataclass
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest


@dataclass(frozen=True)
class _UnavailableVersion:
    """Small API-shaped fallback so an absent module fails behavior checks."""

    major: int
    minor: int
    patch: int
    prerelease: tuple[str, ...] = ()
    build: tuple[str, ...] = ()


@pytest.fixture(scope="module")
def semver():
    module_path = Path(__file__).resolve().parents[1] / "semver.py"
    if not module_path.is_file():
        return SimpleNamespace(
            Version=_UnavailableVersion,
            parse=lambda text: _UnavailableVersion(0, 0, 0),
            compare=lambda a, b: 0,
            bump=lambda text, part: "0.0.0",
        )

    spec = importlib.util.spec_from_file_location("semver_under_test", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    ("text", "expected", "canonical"),
    [
        ("1.4.2", (1, 4, 2, (), ()), "1.4.2"),
        ("v2.0.0", (2, 0, 0, (), ()), "2.0.0"),
        ("  1.4.2  ", (1, 4, 2, (), ()), "1.4.2"),
        (
            "1.4.2-rc.1+build.7",
            (1, 4, 2, ("rc", "1"), ("build", "7")),
            "1.4.2-rc.1+build.7",
        ),
        ("1.2.3-alpha-beta+build.001", (1, 2, 3, ("alpha-beta",), ("build", "001")), "1.2.3-alpha-beta+build.001"),
        ("1.2.3+build.7", (1, 2, 3, (), ("build", "7")), "1.2.3+build.7"),
    ],
)
def test_parse_valid_versions_and_canonical_string(semver, text, expected, canonical):
    version = semver.parse(text)
    assert (
        version.major,
        version.minor,
        version.patch,
        version.prerelease,
        version.build,
    ) == expected
    assert str(version) == canonical


def test_version_is_frozen_and_defaults_metadata_to_empty_tuples(semver):
    version = semver.parse("3.2.1")
    assert version == semver.Version(3, 2, 1)
    assert version.prerelease == ()
    assert version.build == ()
    with pytest.raises((AttributeError, TypeError)):
        version.major = 9


@pytest.mark.parametrize(
    "text",
    [
        "1.2",
        "1.2.3.4",
        "01.2.3",
        "1.02.3",
        "1.2.03",
        "1.x.3",
        "1.2.-3",
        "1.2.3-",
        "1.2.3+",
        "1.2.3-rc..1",
        "1.2.3+build..7",
        "1.2.3-01",
        "1.2.3-rc.01",
        "vv1.2.3",
        "1.2.3 extra",
        "1.2.3-rc_1",
        "١.2.3",
        "",
    ],
)
def test_parse_rejects_malformed_versions(semver, text):
    with pytest.raises(ValueError):
        semver.parse(text)


def test_parse_round_trips_prerelease_and_build_identifiers(semver):
    original = "7.8.9-alpha.2+ci.004"
    assert str(semver.parse(str(semver.parse(original)))) == original


@pytest.mark.parametrize(
    ("lower", "higher"),
    [
        ("1.9.0", "1.10.0"),
        ("1.0.0", "2.0.0"),
        ("1.0.0", "1.0.1"),
        ("1.0.0-alpha", "1.0.0"),
        ("1.0.0-alpha", "1.0.0-alpha.1"),
        ("1.0.0-alpha.1", "1.0.0-alpha.beta"),
        ("1.0.0-alpha.beta", "1.0.0-beta"),
        ("1.0.0-beta", "1.0.0-beta.2"),
        ("1.0.0-beta.2", "1.0.0-beta.11"),
        ("1.0.0-beta.11", "1.0.0-rc.1"),
        ("1.0.0-Alpha", "1.0.0-alpha"),
    ],
)
def test_compare_semver_precedence(semver, lower, higher):
    assert semver.compare(lower, higher) == -1
    assert semver.compare(higher, lower) == 1


def test_compare_equal_versions_and_ignore_build_metadata(semver):
    assert semver.compare("1.0.0", "1.0.0") == 0
    assert semver.compare("1.0.0+a", "1.0.0+b") == 0
    assert semver.compare("1.0.0-rc.1+a", "1.0.0-rc.1+b") == 0


@pytest.mark.parametrize(
    ("text", "part", "expected"),
    [
        ("1.4.2", "patch", "1.4.3"),
        ("1.4.2", "minor", "1.5.0"),
        ("1.4.2", "major", "2.0.0"),
        ("1.4.2-rc.1+build.7", "patch", "1.4.3"),
        ("  v1.4.2+build  ", "minor", "1.5.0"),
    ],
)
def test_bump_components_resets_and_discards_metadata(semver, text, part, expected):
    assert semver.bump(text, part) == expected


@pytest.mark.parametrize("part", ["", "pre", "release", "MAJOR"])
def test_bump_rejects_unknown_parts(semver, part):
    with pytest.raises(ValueError):
        semver.bump("1.2.3", part)


def test_bump_rejects_malformed_version(semver):
    with pytest.raises(ValueError):
        semver.bump("1.02.3", "patch")
