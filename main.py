"""Vercel ASGI entrypoint with a discoverable generated Vite frontend."""

from backend.app.main import app as app
from ml.data import ROOT

app.frontend("/", directory=ROOT / "public", fallback="index.html", check_dir=False)
