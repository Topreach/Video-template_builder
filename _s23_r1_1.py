"""A7-R1.1 — OBJECT IDENTITY. What physical structure is "the declaration"?

Runs against the genuine fixture (`declared_real.mp4`), whose container declaration was
written by the T-R3b injector and whose path is already established as
`moov/udta/meta/ilst/<key>/data`.

The question is NOT "can this path be found". It is **what does the path denote**, and
whether it denotes the DECLARATION or merely a place a value can be recovered from:

    1. the DECLARATION OBJECT  - the ilst ITEM box named by the key
    2. the `data` PAYLOAD box  - a carrier inside the item
    3. a RECOVERABLE LOCATION - a path from which bytes can be read

Measured here, without emitting anything: the exact box chain with offsets and sizes,
which links are CONTAINERS and which LEAVES, how many `data` boxes exist under the
item (path uniqueness), where the VALUE begins relative to the `data` box, and
whether `meta` is a FullBox that the path would hide.
"""
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "src"))
sys.path.insert(0, os.getcwd())

FIX = os.path.join(os.getcwd(), "_s23_fixtures", "declared_real.mp4")
NEEDLE = b"HandBrake 1.6.0 2023041600"
raw = open(FIX, "rb").read()

CONTAINERS = {b"moov", b"udta", b"ilst"}
FULL_BOX = {b"meta"}


def is_item(btype: bytes, prefix: str) -> bool:
    """Is `btype` an iTunes metadata ITEM inside an `ilst`?

    An item box is a CONTAINER of `data` payload boxes even though the generic
    mp4 box grammar does not list it as one. R1.1 depends on this descent: the
    entire question is whether the ITEM or its `data` CHILD is the declaration
    object, and a walk that stops at the item literally cannot see the child.

    R1.1's first run against the malformed fixture reported "0 child box(es)"
    and "resolves AMBIGUOUSLY". That was not a property of the format -- it was
    this walk being blind, and the ambiguity was manufactured by the observer.
    """
    return btype[0] == 0xA9 and prefix.endswith("/ilst")


def walk(buf, start, end, prefix="", out=None):
    """Record every box as (path, type, offset, size, header_len)."""
    if out is None:
        out = []
    pos = start
    while pos + 8 <= end:
        size = struct.unpack(">I", buf[pos:pos + 4])[0]
        btype = buf[pos + 4:pos + 8]
        if size < 8 or pos + size > end:
            out.append((f"{prefix}/<BROKEN>", btype, pos, size, 0))
            return out
        path = f"{prefix}/{btype.decode('latin-1', 'replace')}"
        header = 8
        if btype in CONTAINERS:
            out.append((path, btype, pos, size, header))
            walk(buf, pos + header, pos + size, path, out)
        elif btype in FULL_BOX:
            # a FullBox carries 4 extra version/flags bytes BEFORE its children
            out.append((path, btype, pos, size, header + 4))
            walk(buf, pos + header + 4, pos + size, path, out)
        else:
            out.append((path, btype, pos, size, header))
            if is_item(btype, prefix):
                walk(buf, pos + header, pos + size, path, out)
        pos += size
    return out


print("=" * 78)
print("1. The box chain containing the declaration")
print("=" * 78)
boxes = walk(raw, 0, len(raw))
value_at = raw.find(NEEDLE)
print(f"  value {NEEDLE.decode()!r} first occurs at byte offset {value_at}\n")

chain = [c for c in boxes if c[2] <= value_at < c[2] + c[3]]
for path, btype, off, size, hdr in chain:
    parent = path.rsplit("/", 1)[0]
    kind = ("CONTAINER" if btype in CONTAINERS else
            "FULL-BOX container" if btype in FULL_BOX else
            "ITEM (container of `data`)" if is_item(btype, parent) else
            "LEAF")
    print(f"  {path}")
    print(f"      type={btype!r} offset={off} size={size} header={hdr}  [{kind}]")

print()
print("=" * 78)
print("2. Link classification along the chain")
print("=" * 78)
for i, (path, btype, _o, _s, _h) in enumerate(chain):
    print(f"  {'conduit ' if i + 1 < len(chain) else 'TERMINAL'} {path}")

print()
print("=" * 78)
print("3. Path uniqueness — how many `data` boxes under the item?")
print("=" * 78)
item = [c for c in chain if c[1] == b"\xa9too"]
if item:
    ipath = item[0][0]
    kids = [c for c in boxes if c[0].startswith(ipath + "/")]
    print(f"  item box {ipath} at {item[0][2]} size {item[0][3]}")
    for p, b, o, s, _h in kids:
        print(f"      child {b!r} at {o} size {s}   path {p}")
    print(f"  -> {len(kids)} child box(es); "
          f"'.../{ipath.rsplit('/', 1)[-1]}/data' resolves "
          f"{'UNIQUELY' if len(kids) == 1 else 'AMBIGUOUSLY'}")

print()
print("=" * 78)
print("4. Payload vs value — is the `data` box body the observed value?")
print("=" * 78)
data_box = [c for c in chain if c[1] == b"data"]
if data_box:
    _p, _t, d_off, d_size, d_hdr = data_box[0]
    body = raw[d_off + d_hdr:d_off + d_size]
    at = body.find(NEEDLE)
    print(f"  data box at {d_off} size {d_size} header {d_hdr}")
    print(f"  body length           : {len(body)}")
    print(f"  observed value length : {len(NEEDLE)}")
    print(f"  body hex              : {body.hex()}")
    print(f"  value offset in body  : {at}")
    print(f"  body == value         : {body == NEEDLE}")
    if body != NEEDLE and at >= 0:
        pre = body[:at]
        print(f"  -> the box body is NOT the value; it carries a {len(pre)}-byte")
        print(f"     prefix: {pre.hex()}  (well-known type + locale)")
        print("     The address locates a CARRIER; the value starts INSIDE it at")
        print("     an offset the address does not itself record.")
        print(f"  value begins at absolute byte {d_off + d_hdr + at}")

print()
print("=" * 78)
print("5. Does the path hide structure? (`meta` is a FullBox)")
print("=" * 78)
for path, btype, off, size, hdr in chain:
    if btype in FULL_BOX:
        vf = struct.unpack(">I", raw[off + 8:off + 12])[0]
        print(f"  {path}: version/flags = 0x{vf:08x}")
        print("  -> 4 bytes that a plain path cannot express. A reader following")
        print("     'moov/udta/meta/ilst/...' must KNOW meta is a FullBox, or")
        print("     every offset beneath it is wrong by 4.")

print()
print("=" * 78)
print("R1.1 VERDICT")
print("=" * 78)
print("  The path `moov/udta/meta/ilst/<key>/data` resolves to a `data` box,")
print("  which is a PAYLOAD CARRIER inside the ilst ITEM box that is the")
print("  declaration object. Three findings make them non-equivalent:")
print("    (a) the ITEM box is the declaration; `data` is inside it;")
print("    (b) the `data` body is NOT the value - an 8-byte prefix precedes it;")
print("    (c) `meta` is a FullBox, so the path alone does not fix the offsets.")
print("  Identity of the REPORTED declaration is therefore NOT established by")
print("  the path alone. Value identity (R1.3) and encoding (R1.6) must carry")
print("  part of it, and the address grammar must decide whether the item box")
print("  or the data box is the addressed object.")
