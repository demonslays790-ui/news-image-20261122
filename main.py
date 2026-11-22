#!/usr/bin/env python3
"""Entry point for the make.fun news-image-20261122 bounty.

Copies the pre-rendered front-page image (entry.png, built by
generate_image.py from verified 22 November 2026 news) to the output
directory. No network access. Deterministic: the output bytes are
always identical to entry.png.
"""
import os
import shutil
import stat
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    os.chmod(dst, 0o644)
    print("wrote", dst)


if __name__ == "__main__":
    sys.exit(main())
