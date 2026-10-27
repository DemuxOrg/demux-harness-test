# demux-harness-test

## Semantic versions

`semver.py` parses Semantic Versioning strings, compares their precedence, and
bumps a core version component:

```python
from semver import bump, compare, parse

version = parse("1.4.2-rc.1+build.7")
print(version)  # 1.4.2-rc.1+build.7
print(compare("1.4.2-rc.1", "1.4.2"))  # -1
print(bump("1.4.2", "minor"))  # 1.5.0
```

The module uses only the Python standard library. Install `requirements-dev.txt`
to run its pytest suite.
