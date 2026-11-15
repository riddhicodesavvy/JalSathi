"""Copy Vite's verified build to Vercel's CDN asset directory, without mutating source."""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = ROOT / "frontend/dist"
    if not (source / "index.html").is_file():
        raise RuntimeError("Build the Vite frontend before packaging CDN assets.")
    destination = ROOT / "public"
    # Copy only build output; this directory is ignored and never contains source/user data.
    shutil.copytree(source, destination, dirs_exist_ok=True)
    print("Prepared Vite assets for the CDN.")


if __name__ == "__main__":
    main()
