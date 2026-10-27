"""Parsing and precedence comparison for Semantic Versioning 2.0.0."""

from dataclasses import dataclass
import re


_VERSION_PATTERN = re.compile(
    r"(?P<major>0|[1-9][0-9]*)\."
    r"(?P<minor>0|[1-9][0-9]*)\."
    r"(?P<patch>0|[1-9][0-9]*)"
    r"(?:-(?P<prerelease>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+(?P<build>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
)
_NUMERIC_IDENTIFIER = re.compile(r"[0-9]+\Z")


@dataclass(frozen=True)
class Version:
    """A parsed semantic version, including its optional metadata."""

    major: int
    minor: int
    patch: int
    prerelease: tuple[str, ...] = ()
    build: tuple[str, ...] = ()

    def __str__(self) -> str:
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version += "-" + ".".join(self.prerelease)
        if self.build:
            version += "+" + ".".join(self.build)
        return version


def parse(text: str) -> Version:
    """Parse a semantic version string, allowing whitespace and one ``v``."""
    if not isinstance(text, str):
        raise ValueError("version must be a string")

    text = text.strip()
    if text.startswith("v"):
        text = text[1:]

    match = _VERSION_PATTERN.fullmatch(text)
    if match is None:
        raise ValueError(f"invalid semantic version: {text!r}")

    prerelease_text = match.group("prerelease")
    prerelease = tuple(prerelease_text.split(".")) if prerelease_text else ()
    for identifier in prerelease:
        if _NUMERIC_IDENTIFIER.fullmatch(identifier) and len(identifier) > 1 and identifier.startswith("0"):
            raise ValueError(f"numeric prerelease identifier has a leading zero: {identifier!r}")

    build_text = match.group("build")
    build = tuple(build_text.split(".")) if build_text else ()
    return Version(
        int(match.group("major")),
        int(match.group("minor")),
        int(match.group("patch")),
        prerelease,
        build,
    )


def _compare_prerelease(left: tuple[str, ...], right: tuple[str, ...]) -> int:
    if not left:
        return 0 if not right else 1
    if not right:
        return -1

    for left_id, right_id in zip(left, right):
        left_numeric = _NUMERIC_IDENTIFIER.fullmatch(left_id) is not None
        right_numeric = _NUMERIC_IDENTIFIER.fullmatch(right_id) is not None
        if left_numeric and right_numeric:
            left_value, right_value = int(left_id), int(right_id)
            if left_value != right_value:
                return -1 if left_value < right_value else 1
        elif left_numeric != right_numeric:
            return -1 if left_numeric else 1
        elif left_id != right_id:
            return -1 if left_id < right_id else 1

    if len(left) == len(right):
        return 0
    return -1 if len(left) < len(right) else 1


def compare(a: str, b: str) -> int:
    """Compare two versions by SemVer precedence, ignoring build metadata."""
    left = parse(a)
    right = parse(b)

    left_core = (left.major, left.minor, left.patch)
    right_core = (right.major, right.minor, right.patch)
    if left_core != right_core:
        return -1 if left_core < right_core else 1
    return _compare_prerelease(left.prerelease, right.prerelease)


def bump(text: str, part: str) -> str:
    """Increment one core component and discard prerelease/build metadata."""
    version = parse(text)
    if part == "major":
        return f"{version.major + 1}.0.0"
    if part == "minor":
        return f"{version.major}.{version.minor + 1}.0"
    if part == "patch":
        return f"{version.major}.{version.minor}.{version.patch + 1}"
    raise ValueError(f"unknown version part: {part!r}")
