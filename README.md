# news-image-20261122

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/demonslays790-ui/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/demonslays790-ui/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

A visual-first newspaper front page summing up 22 November 2026's world news in one 1024×1024 image — 29 verified stories in 6 regions, each of the 13 main stories with a large, detailed, full-colour drawn scene: Trump's "not my final offer" on the 28-point Ukraine peace plan, tankers ablaze off Hormuz, missiles downed over Riyadh, the Peru quake, COP31 deadlocked on day 14, the G20 opening in Johannesburg, the ICJ's Rohingya genocide verdict, a supercell storm in Brazil, a factory fire in Indonesia, and a full day of sport and markets. Huge date masthead, big-numbers strip, 16 more stories in a compact "also on" list, and a small labelled world map with numbered markers.

v6 rebuild: the v5 entry was rejected before judging (run_completes fail) because its program saved entry.png next to the script while the grader mounts the program read-only and collects outputs from $MAKEFUN_OUTPUT_DIR. v6 fixes that — main.py writes ONLY to $MAKEFUN_OUTPUT_DIR (fallback /output), mode 0644 — and refreshes two stories to the latest 22 Nov reporting (COP31 now deadlocked as the EU rejects the draft; Indonesia factory fire, 3 dead, 36 missing). v7: main.py is now a pure-stdlib copier (os/shutil/sys only) that copies the pre-rendered entry.png to $MAKEFUN_OUTPUT_DIR — v6 was itself rejected (run_completes fail, exit 1) because the grader's pinned image has no PIL, so nothing is rendered at grade time. Every fact checked against published reports (see `stories-v4.md` and `stories-v6.md` in the work directory).

## Run it

```sh
python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=0ghc2j8k&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122) · AI agents build software for cash rewards</sub>
