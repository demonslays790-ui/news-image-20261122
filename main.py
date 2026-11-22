#!/usr/bin/env python3
"""Publish the v4 front page for make.fun news-image-20261122.

This entry's image (entry.png: 35 verified 22 November 2026 stories
in 6 regions, drawn by generate_image.py) is bundled in the repo, so
publishing is just copying that file to the grader's output folder.
The program touches no network and always writes the same bytes as
entry.png, so repeated runs are identical.
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))


def run():
    src = os.path.join(HERE, "entry.png")
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    dst = os.path.join(outdir, "entry.png")
    shutil.copyfile(src, dst)
    os.chmod(dst, 0o644)
    print("wrote " + dst)


if __name__ == "__main__":
    run()
