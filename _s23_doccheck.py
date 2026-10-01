"""Structural check over docs/specs/*.md after the §2.1.16 / V.7.1 edits.

Reports only what is mechanically decidable: duplicate headings, unbalanced code
fences, and obviously ragged table rows. It cannot judge whether prose agrees with
the gate output -- that is what reading the register rows is for.
"""
from __future__ import annotations

import io
import os

D = os.path.join("docs", "specs")
FENCE = "```"

total_headings = 0
problems = 0

for name in sorted(os.listdir(D)):
    if not name.endswith(".md"):
        continue
    path = os.path.join(D, name)
    lines = io.open(path, encoding="utf-8").read().split("\n")
    fences = sum(1 for l in lines if l.strip().startswith(FENCE))
    heads = [l.rstrip() for l in lines if l.startswith("#")]
    dup = sorted({h for h in heads if heads.count(h) > 1})
    # Track fence state: a `|` inside a code block is grammar/ASCII, not a table row.
    # Without this the grammar alternatives in 2.1.17.3 were reported as ragged tables.
    ragged, in_fence = [], False
    for i, l in enumerate(lines):
        if l.strip().startswith(FENCE):
            in_fence = not in_fence
            continue
        if not in_fence and l.strip().startswith("|") and l.count("|") < 3:
            ragged.append(i + 1)
    # Column-count consistency across a CONTIGUOUS table block. The previous version
    # only looked per line, so a table whose header and body were separated by an
    # inserted section (V.7.5 split by the V.7.6 insert) reported CLEAN while
    # rendering as two broken tables. Rows are grouped by adjacency and every row in
    # a block must agree on column count.
    blocks, cur = [], []
    for i, l in enumerate(lines):
        if l.strip().startswith(FENCE):
            in_fence = not in_fence
            cur = []
            continue
        if not in_fence and l.strip().startswith("|"):
            # Count UNESCAPED pipes only. `\|` inside a code span is a legitimate
            # markdown escape for a literal pipe (e.g. `extracted \| absent \|
            # uncertain`) and must not be read as an extra column boundary. Three
            # such tables were reported as mismatched before this was handled.
            cur.append((i, l.replace("\\|", "").count("|")))
            continue
        if cur:
            blocks.append(cur)
        cur = []
    if cur:
        blocks.append(cur)
    split = []
    for blk in blocks:
        widths = {w for _i, w in blk}
        if len(widths) > 1:
            split.append((blk[0][0] + 1, sorted(widths)))

    total_headings += len(heads)
    if len(dup) or fences % 2 or ragged or split:
        problems += 1
    print(f"{name:38s} lines={len(lines):5d} headings={len(heads):4d} "
          f"fences={fences:3d}({'OK' if fences % 2 == 0 else 'UNBALANCED'}) "
          f"dup={len(dup)} ragged={len(ragged)} split={len(split)}")
    for h in dup:
        print(f"    DUPLICATE HEADING: {h}")
    for r in ragged:
        print(f"    RAGGED TABLE ROW at line {r}")
    for ln, widths in split:
        print(f"    SPLIT/MISMATCHED TABLE at line {ln}: pipe counts {widths}")


md = [f for f in os.listdir(D) if f.endswith(".md")]
print(f"\n{total_headings} headings across {len(md)} files; "
      f"{problems} file(s) with structural problems")