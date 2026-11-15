"""Load an explicitly selected, git-ignored Vercel env file without logging values."""

import json
import os
from pathlib import Path


def load(path):
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line or line.lstrip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if value.startswith('"') and value.endswith('"'):
            value = json.loads(value)
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        os.environ[key] = value
