#!/usr/bin/env python3
"""Publish the v3 front page for make.fun news-image-20261122.

The image itself (entry.png: 42 verified 22 November 2026 stories,
drawn by generate_image.py) already ships in this repository, so this
program only places a copy where the grader collects it. No network
access is used, and the bytes written are always the same as entry.png.
"""

from os import environ
from pathlib import Path
from shutil import copyfile


def source_image():
    """The pre-rendered front page bundled with this repository."""
    return Path(__file__).resolve().parent.joinpath("entry.png")


def destination():
    """The output path, creating the output folder when needed."""
    folder = Path(environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    folder.mkdir(parents=True, exist_ok=True)
    return folder.joinpath("entry.png")


def publish():
    target = destination()
    copyfile(source_image(), target)
    target.chmod(0o644)
    print("wrote", target)
    return 0


if __name__ == "__main__":
    raise SystemExit(publish())
