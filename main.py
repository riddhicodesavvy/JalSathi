"""Vercel ASGI entrypoint. Static Vite files are served separately by the CDN."""

from backend.app.main import app as app
