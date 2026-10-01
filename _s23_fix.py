"""Relocate the misplaced location-check block to the end of _s23_g13t.py.

`insert_line=108` landed the block INSIDE the encoding loop, before `buf` and
`entries` exist, so it raised NameError. It is cut out and appended after the
analysis that defines the names it uses.
"""
from __future__ import annotations

import io

PATH = "_s23_g13t.py"
lines = io.open(PATH, encoding="utf-8").read().split("\n")

start = next(i for i, l in enumerate(lines)
             if l.startswith('print("Where do the two literals'))
end = next(i for i, l in enumerate(lines)
           if "DOWNGRADED to UNLOCATED" in l)
block = lines[start:end + 1]
print(f"cut block: lines {start + 1}..{end + 1} ({len(block)} lines)")

rest = lines[:start] + lines[end + 1:]
while rest and not rest[-1].strip():
    rest.pop()

drop = ("placeholder removed below", "tagged = any(",
        "for _p, (_i, s, e) in enumerate(entries)",
        "for _i2, s2, e2 in []")
block = [l for l in block if not any(d in l for d in drop)]

io.open(PATH, "w", encoding="utf-8", newline="\n").write(
    "\n".join(rest + ["", ""] + block))
compile(io.open(PATH, encoding="utf-8").read(), PATH, "exec")
print("relocated and compiles OK")