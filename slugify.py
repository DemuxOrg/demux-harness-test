"""Convert text into lowercase, ASCII URL slugs."""

import re
import unicodedata


_LATIN_TRANSLITERATION = str.maketrans(
    {
        "Æ": "AE",
        "æ": "ae",
        "Ð": "D",
        "ð": "d",
        "Đ": "D",
        "đ": "d",
        "Ħ": "H",
        "ħ": "h",
        "ı": "i",
        "Ł": "L",
        "ł": "l",
        "Ø": "O",
        "ø": "o",
        "Œ": "OE",
        "œ": "oe",
        "ẞ": "SS",
        "ß": "ss",
        "Þ": "TH",
        "þ": "th",
        "Ŧ": "T",
        "ŧ": "t",
    }
)
_NON_ALPHANUMERIC = re.compile(r"[^a-z0-9]+")


def slugify(text: str, max_length: int | None = None, separator: str = "-") -> str:
    """Return a lowercase ASCII slug for *text*.

    If ``max_length`` is set, the result is shortened at a word boundary when
    possible. A first word longer than the limit is truncated directly.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if max_length is not None:
        if isinstance(max_length, bool) or not isinstance(max_length, int):
            raise TypeError("max_length must be an integer or None")
        if max_length < 1:
            raise ValueError("max_length must be at least 1")
    if not isinstance(separator, str):
        raise TypeError("separator must be a string")
    if not separator or any(character.isalnum() for character in separator):
        raise ValueError("separator must be nonempty and contain no letters or digits")

    normalized = unicodedata.normalize("NFKD", text.translate(_LATIN_TRANSLITERATION))
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    words = _NON_ALPHANUMERIC.sub(" ", ascii_text).split()
    if not words:
        return ""
    if max_length is None:
        return separator.join(words)

    if len(words[0]) > max_length:
        return words[0][:max_length]

    result = words[0]
    for word in words[1:]:
        candidate = result + separator + word
        if len(candidate) > max_length:
            break
        result = candidate
    return result.rstrip(separator)
