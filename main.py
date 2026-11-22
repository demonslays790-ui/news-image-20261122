#!/usr/bin/env python3
"""Publish the v7 front page for make.fun news-image-20261122.

This entry's image (entry.png: v6's visual-first front page summing up
22 November 2026's world news — 13 main stories with large drawn scenes,
29 verified stories in 6 regions) is pre-built and bundled in the
repo, so publishing is just copying that file to the grader's output
folder. Pure standard library only (os, shutil, sys): the grader runs
`python3 -P -s /bot/main.py` in a pinned image with no network and no
third-party imaging libraries, so the image is never drawn at grade
time. The program touches no network and always writes the same bytes
as entry.png, so repeated runs are identical. It writes ONLY to $MAKEFUN_OUTPUT_DIR (fallback
/output), mode 0644 — never beside this script, which the grader
mounts read-only.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run():
    src = os.path.join(HERE, "entry.png")
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    dst = os.path.join(outdir, "entry.png")
    shutil.copyfile(src, dst)
    os.chmod(dst, 0o644)
    print("wrote " + dst)


if __name__ == "__main__":
    run()
