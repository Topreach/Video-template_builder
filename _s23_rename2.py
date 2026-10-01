"""One-shot: disambiguate the Amendment Record v1.2 sub-headings in
stage2_source_description.md.

Amendment Records v1.1 and v1.2 use the same section shape ("3. Normative rules",
"4. What this does not do", "6. Execution"), so three titles collide. Only the v1.2
copies are rewritten -- v1.1 is the audited baseline and stays byte-identical.
Mirrors the same fix applied to S2.1.16 in stage2_1_contract_boundary.md.
"""
from __future__ import annotations

import io

PATH = "docs/specs/stage2_source_description.md"
START = "# Amendment Record — v1.1 → v1.2"

RENAMES = {
    "## 3. Normative rules": "## 3. Normative rules (v1.2)",
    "## 4. What this does not do": "## 4. What v1.2 does not do",
    "## 6. Execution": "## 6. Execution (v1.2)",
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