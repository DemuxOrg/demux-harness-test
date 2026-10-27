# demux-harness-test

## Slugify

`slugify.py` converts text to a lowercase, ASCII slug, including transliteration
of accented Latin characters:

```python
from slugify import slugify

slugify("Crème Brûlée")  # "creme-brulee"
slugify("Hello World", separator="_")  # "hello_world"
slugify("the quick brown fox", max_length=12)  # "the-quick"
```

Install the development requirements with `python -m pip install -r requirements-dev.txt`
to run the pytest suite.
