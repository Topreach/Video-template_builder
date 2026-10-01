"""One-shot: prefix §2.1.16's three ambiguous sub-headings.

§2.1.15 and §2.1.16 both use a 1..10 heading shape, so three titles collide. Only
the §2.1.16 copies are rewritten; the §2.1.15 ones are the audited baseline and are
left byte-identical.
"""
from __future__ import annotations

import io

PATH = "docs/specs/stage2_1_contract_boundary.md"
START = "## 2.1.16 Controlled Amendment Record"

RENAMES = {
    "### 1. The finding (evidence, not preference)":
        "### 2.1.16.1 The finding (evidence, not preference)",
    "### 2. Why the existing vocabulary cannot absorb it":
        "### 2.1.16.2 Why the existing vocabulary cannot absorb it",
    "### 3. The amended vocabulary (normative)":
        "### 2.1.16.3 The amended vocabulary (normative)",
}

lines = io.open(PATH, encoding="utf-8").read().split("\n")
boundary = next(i for i, l in enumerate(lines) if l.startswith(START))

changed = 0
for i in range(boundary, len(lines)):
    s = lines[i].rstrip()
    if s in RENAMES:
        lines[i] = RENAMES[s]
        changed += 1
        print(f"  line {i + 1}: {s!r} -> {RENAMES[s]!r}")

io.open(PATH, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print(f"renamed {changed} heading(s) below {START!r} (line {boundary + 1})")
assert changed == len(RENAMES), f"expected {len(RENAMES)}, renamed {changed}"