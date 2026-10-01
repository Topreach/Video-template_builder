"""T-R3b fixture builder: a real artifact-declared producer, by atom injection.

Why this exists
---------------
R3 measured that the muxer destroys any container-scope declaration at write time:
under every write instruction tried (default, +faststart, empty string, an explicit
'HandBrake 1.6.0', creation_time only) the bytes contain 'Lavf62.12.102' and never
contain 'HandBrake'. So no fixture built by writing tags can exercise T1 or T3 — the
declaration cannot be made to exist through the approved mechanism.

The only way to produce an artifact that *declares* a producer is to construct the
declaration in the bytes directly. That is what this does, and it is the reason T1/T3
were NOT-IMPLEMENTED rather than FAIL.

What it does
------------
Locates the mp4 `moov/udta/meta/ilst/too` atom — the iTunes "too" (encoder) field the
mov muxer writes — and replaces its payload with an arbitrary declared producer
string, repairing every structure the change touches:

  * the sizes of `too`, `ilst`, `meta`, `udta` and `moov` all grow by the delta;
  * every `stco`/`co64` chunk offset pointing past the end of `moov` is shifted by
    the same delta, because inserting bytes inside `moov` moves `mdat`.

Without the offset repair the file is subtly corrupt: PyAV may still open it, but
sample data would be read from the wrong byte positions. The build is validated by
re-probing and asserting the declaration reads back verbatim.
"""

from __future__ import annotations

import os
import re
import struct
from fractions import Fraction

import av

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURES = os.path.join(HERE, "_s23_fixtures")
TOO_TYPE = b"\xa9too"
CONTAINERS = {b"moov", b"trak", b"mdia", b"minf", b"stbl", b"udta", b"ilst"}


def build_base(path: str, seconds: float = 1.0, fps: int = 10,
               stream_tags: dict | None = None) -> str:
    """A plain, valid mp4 with a moving square — no metadata tags at all.

    `stream_tags` are written by PyAV's own writer. Measured: a stream-scope
    `encoder` tag written this way SURVIVES to probe time (it lands in the track's
    udta in the layout the mov demuxer expects). The first attempt at the two-scope
    fixture hand-injected a `©too` atom into the track udta instead, and the demuxer
    read it back as `encoder: ''` — an empty value, i.e. a silent loss. Route via the
    writer rather than against the demuxer's expectations.
    """
    import numpy as np
    c = av.open(path, "w")
    st = c.add_stream("libx264", rate=fps)
    st.width, st.height, st.pix_fmt = 160, 120, "yuv420p"
    st.time_base = Fraction(1, fps * 100)
    for k, v in (stream_tags or {}).items():
        st.metadata[k] = v
    c.start_encoding()
    for i in range(int(seconds * fps)):
        img = np.zeros((120, 160, 3), dtype=np.uint8)
        x = int((i / max(int(seconds * fps) - 1, 1)) * 100)
        img[30:50, x:x + 20] = 255
        vf = av.VideoFrame.from_ndarray(img, format="rgb24")
        vf.pts = i
        for packet in st.encode(vf):
            c.mux(packet)
    for packet in st.encode(None):
        c.mux(packet)
    c.close()
    return path


def _walk(buf: bytes, start: int, end: int, depth: int, hits: list,
          path: tuple = ()) -> None:
    """Record every `too` atom together with the chain of ancestor box positions.

    The ancestor chain is required, not incidental: inserting bytes inside the
    `too` atom makes every enclosing box (ilst, meta, udta, moov) wrong by the same
    delta, and a file whose `moov` size does not match its content is corrupt even
    when it still opens.
    """
    pos = start
    while pos + 8 <= end:
        size = struct.unpack(">I", buf[pos:pos + 4])[0]
        btype = buf[pos + 4:pos + 8]
        if size == 1:  # 64-bit size follows the type
            size = struct.unpack(">Q", buf[pos + 8:pos + 16])[0]
            header = 16
        else:
            header = 8
        if size < header or pos + size > end:
            return
        if btype == TOO_TYPE:
            hits.append((pos, size, header, depth, path))
        elif btype in CONTAINERS:
            _walk(buf, pos + header, pos + size, depth + 1, hits, path + (pos,))
        elif btype == b"meta":
            # `meta` is a FullBox: 4 bytes of version/flags precede its children.
            _walk(buf, pos + header + 4, pos + size, depth + 1, hits, path + (pos,))
        pos += size


def _shift_chunk_offsets(buf: bytes, delta: int, moov_end: int) -> tuple:
    """Add `delta` to every stco/co64 entry pointing past the end of `moov`."""
    patched = 0
    if delta == 0:
        return buf, 0
    for m in re.finditer(rb"stco|co64", buf):
        step, fmt = (8, ">Q") if m.group() == b"co64" else (4, ">I")
        table = m.start()
        count = struct.unpack(">I", buf[table + 8:table + 12])[0]
        base = table + 12
        for i in range(count):
            off = base + i * step
            if off + step > len(buf):
                break
            value = struct.unpack(fmt, buf[off:off + step])[0]
            if value >= moov_end:
                buf = buf[:off] + struct.pack(fmt, value + delta) + buf[off + step:]
                patched += 1
    return buf, patched


def _grow_sizes(buf: bytes, hits, delta: int) -> bytes:
    """Grow the size field of each ANCESTOR box of every `too` atom.

    **Ancestors only -- NOT the `too` box itself.**

    That exclusion is the whole point and it was wrong until R1.1 caught it.
    `inject_declaration` splices a replacement box whose header already carries the
    exact new size (`header + len(payload)`). When this function also added `delta`
    to that same box, the leaf was counted twice: a 50-byte box was written as 63.
    FFmpeg tolerates the resulting overrun, so the file still opened, the value
    still read back and the frames still decoded -- the `ilst` chain simply no longer
    closed. Every fixture check written so far tested DECODABILITY and none tested
    STRUCTURE, which is why it survived from the T-R3b injector onward.

    `pos` in a hit is ALREADY the first byte of the box's size field, so the size
    lives at `pos` -- not at `pos - header`. An earlier version patched eight bytes
    too early and corrupted the enclosing atom. Ancestors were also missing from an
    even earlier attempt: fixing only the leaf leaves `moov` shorter than its content.
    """
    for pos, _size, _header, _depth, path in hits:
        for box in path:                      # ancestors only; leaf already sized
            old = struct.unpack(">I", buf[box:box + 4])[0]
            buf = buf[:box] + struct.pack(">I", old + delta) + buf[box + 4:]
    return buf


def assert_box_chain(path: str) -> list:
    """Verify that every mp4 box's declared size closes inside its parent.

    Returns the list of problems found (empty means the chain is sound). This is a
    STRUCTURAL check and is deliberately separate from "the file decodes": FFmpeg
    tolerates an overrunning box, so a decode-only verification cannot detect the
    class of defect this catches.
    """
    raw = open(path, "rb").read()
    problems: list = []
    containers = {b"moov", b"udta", b"ilst", b"trak", b"mdia"}

    def walk(start, end, prefix=""):
        pos = start
        while pos + 8 <= end:
            size = struct.unpack(">I", raw[pos:pos + 4])[0]
            btype = raw[pos + 4:pos + 8]
            if size < 8 or pos + size > end:
                problems.append({
                    "path": f"{prefix}/{btype.decode('latin-1', 'replace')}",
                    "offset": pos, "declared_size": size,
                    "ends_at": pos + size, "parent_ends": end,
                    "overrun": (pos + size) - end,
                })
                return
            name = btype.decode("latin-1", "replace")
            if btype in containers:
                walk(pos + 8, pos + size, f"{prefix}/{name}")
            elif btype == b"meta":
                walk(pos + 12, pos + size, f"{prefix}/{name}")
            pos += size

    walk(0, len(raw))
    return problems



def _too_payload(declared: str) -> bytes:
    """A well-formed iTunes `data` payload: [size][data][type=1 UTF-8][locale][value].

    The field ORDER was the first bug in this builder: an earlier version emitted
    [type][size][data][value] and omitted the locale entirely, which produced a file
    that still opened but reported no `encoder` at all. The layout below was read
    from the real muxer output, not assumed:
        0000001d 64617461 00000001 00000000 4c617666...
        size=29  'data'   type=UTF-8 locale=0  "Lavf..."
    """
    raw = declared.encode("utf-8")
    return (struct.pack(">I", 16 + len(raw)) + b"data"
            + struct.pack(">I", 1) + struct.pack(">I", 0) + raw)


def inject_stream_declaration(src: str, dst: str, declared: str) -> dict:
    """Add a VIDEO-STREAM-scoped encoder tag that the muxer will not overwrite.

    The container-scope route is `inject_declaration`, which replaces the atom FFmpeg
    always writes. This function instead injects a *new* `©too` atom into the stream's
    `udta` box, so the finished file carries TWO declarations at DIFFERENT scopes that
    disagree — the T-C1/T-C2 and Stage 2.3 T7 fixture.

    Stream `udta` boxes are found by walking to the video track's `trak` -> `udta`;
    when none exists one is appended to the `trak` and the enclosing size chain is
    repaired. A `udta` carrying a tag is left in place and extended instead.
    """
    buf = bytes(open(src, "rb").read())

    # Locate the first video trak: moov -> trak -> mdia (hdlr 'vide').
    def find_video_trak(b, start, end):
        pos = start
        while pos + 8 <= end:
            size = struct.unpack(">I", b[pos:pos + 4])[0]
            btype = b[pos + 4:pos + 8]
            if size < 8 or pos + size > end:
                return None
            if btype == b"trak":
                hit = b.find(b"vide", pos, pos + size)
                if hit != -1:
                    return pos
            pos += size
        return None

    moov_start = buf.find(b"moov") - 4
    moov_size = struct.unpack(">I", buf[moov_start:moov_start + 4])[0]
    trak = find_video_trak(buf, moov_start + 8, moov_start + moov_size)
    if trak is None:
        raise RuntimeError("no video trak found")

    # Does this trak already have a udta?
    def find_child(b, start, end, want):
        pos = start
        while pos + 8 <= end:
            size = struct.unpack(">I", b[pos:pos + 4])[0]
            if size < 8 or pos + size > end:
                return None
            if b[pos + 4:pos + 8] == want:
                return (pos, size)
            pos += size
        return None

    trak_size = struct.unpack(">I", buf[trak:trak + 4])[0]
    udta = find_child(buf, trak + 8, trak + trak_size, b"udta")

    atom = struct.pack(">I", 8 + len(_too_payload(declared))) + TOO_TYPE + \
        _too_payload(declared)

    if udta is not None:
        pos, size = udta
        out = buf[:pos + size] + atom + buf[pos + size:]
        grown = [(pos, delta := len(atom))]
    else:
        udta_payload = atom
        udta_size = 8 + len(udta_payload)
        udta_box = struct.pack(">I", udta_size) + b"udta" + udta_payload
        out = buf[:trak + trak_size] + udta_box + buf[trak + trak_size:]
        grown = [(trak, udta_size)]

    # Grow trak and moov by the inserted bytes; moov grows with everything inside it.
    total = sum(d for _p, d in grown)
    for pos, _d in grown:
        cur = struct.unpack(">I", out[pos:pos + 4])[0]
        out = out[:pos] + struct.pack(">I", cur + total) + out[pos + 4:]
    cur_moov = struct.unpack(">I", out[moov_start:moov_start + 4])[0]
    out = out[:moov_start] + struct.pack(">I", cur_moov + total) + out[moov_start + 4:]

    out, patched = _shift_chunk_offsets(out, total, moov_start + moov_size + total)
    open(dst, "wb").write(out)
    return {"declared": declared, "delta": total, "chunk_offsets_patched": patched,
            "path": dst, "injected_udta": udta is None}


def inject_declaration(src: str, dst: str, declared: str) -> dict:
    """Copy `src` to `dst` with its container-scope encoder atom set to `declared`."""
    buf = bytes(open(src, "rb").read())
    hits: list = []
    _walk(buf, 0, len(buf), 0, hits)
    if not hits:
        raise RuntimeError("no encoder atom in the source; nothing to inject")

    pos, size, header, _depth, _path = hits[0]
    payload = _too_payload(declared)
    new_size = header + len(payload)
    delta = new_size - size
    new_header = struct.pack(">I", new_size) + TOO_TYPE

    moov_start = buf.find(b"moov") - 4
    moov_size = struct.unpack(">I", buf[moov_start:moov_start + 4])[0]
    moov_end = moov_start + moov_size

    # The replacement MUST include the box header. An earlier version spliced the
    # payload over `buf[pos:pos+size]`, which deleted the size field AND the
    # `too` type along with it: the file still opened, the brand keys still read,
    # and the encoder tag silently vanished. Same failure shape as the defect this
    # whole audit exists to catch — a loss that leaves a plausible-looking record.
    out = buf[:pos] + new_header + payload + buf[pos + size:]

    # `moov_end + delta`, not `moov_end`. The splice has ALREADY grown moov, so the
    # original end is stale by exactly `delta` and every chunk offset sitting in that
    # window is left unpatched. Every other call site in this project passes the
    # POST-growth value; this one was the outlier. It was latent here only because
    # this fixture's mdat precedes moov, so no offset ever crossed the threshold.
    out, patched = _shift_chunk_offsets(out, delta, moov_end + delta)

    # Ancestors only -- the leaf's size is already exact in `new_header`.
    out = _grow_sizes(out, hits, delta)
    open(dst, "wb").write(out)

    # STRUCTURAL gate. The file decodes even when this fails, which is precisely
    # why the double-count went unnoticed for the whole T-R3b cycle (R1.1).
    problems = assert_box_chain(dst)
    return {"declared": declared, "delta": delta,
            "chunk_offsets_patched": patched, "path": dst,
            "declared_box_size": new_size,
            "structural_problems": problems}


def inspect_too(path: str) -> list:
    """Print the exact bytes of each `too` atom, so the payload can be modelled
    on the real structure rather than on an assumed one."""
    buf = bytes(open(path, "rb").read())
    hits: list = []
    _walk(buf, 0, len(buf), 0, hits)
    out = []
    for pos, size, header, depth, _path in hits:
        out.append({
            "depth": depth,
            "box_start": pos,
            "box_size_field": struct.unpack(">I", buf[pos:pos + 4])[0],
            "atom_size": size,
            "header": header,
            "payload_hex": bytes(buf[pos + header:pos + size]).hex(),
            "payload_repr": repr(bytes(buf[pos + header:pos + size])),
        })
    return out


def verify(path: str, expected: str) -> dict:
    """Re-probe the injected file and report what the mechanism now reads."""
    c = av.open(path, "r")
    container = dict(c.metadata)
    streams = {s.index: dict(s.metadata) for s in c.streams}
    c.close()
    raw = open(path, "rb").read()
    return {
        "container": container,
        "streams": streams,
        "bytes_contain_declared": expected.encode("utf-8") in raw,
        "matches_expected": any(v == expected for v in container.values()),
    }


def _frames_match(base: str, injected: str) -> dict:
    """Decode both files fully and compare frame data, byte for byte.

    This is the integrity check the offset rewrite deserves. A wrong stco adjustment
    produces a file that opens, reports the right metadata, and decodes to garbage —
    so metadata alone cannot validate this fixture.
    """
    def frames(path):
        c = av.open(path, "r")
        out = [bytes(f.planes[0]) for f in c.decode(video=0)]
        c.close()
        return out

    a, b = frames(base), frames(injected)
    return {"base_frames": len(a), "injected_frames": len(b),
            "identical": bool(a) and a == b}


def main() -> int:
    os.makedirs(FIXTURES, exist_ok=True)
    base = build_base(os.path.join(FIXTURES, "t1_base.mp4"))
    declared = "HandBrake 1.6.0 2023041600"
    out = os.path.join(FIXTURES, "declared_real.mp4")
    info = inject_declaration(base, out, declared)
    result = verify(out, declared)

    print("T-R3b fixture build")
    for atom in inspect_too(base):
        print(f"  base too atom   depth={atom['depth']} "
              f"size_field={atom['box_size_field']} atom_size={atom['atom_size']}")
        print(f"  base payload    {atom['payload_repr']}")
    print(f"  base            {base}")
    print(f"  injected        {out}")
    print(f"  delta           {info['delta']} bytes")
    print(f"  declared box    {info['declared_box_size']} bytes")
    print(f"  chunk offsets   {info['chunk_offsets_patched']} patched")
    print(f"  bytes contain   {result['bytes_contain_declared']}")
    print(f"  container meta  {result['container']}")
    print(f"  stream meta     {result['streams']}")

    # STRUCTURAL assertion. A decode check cannot catch an overrunning box, and the
    # previous builder proved it: the file decoded, the value read back, and the
    # frames matched -- while `ilst` did not close (A7-R1.1). These fixtures are
    # evidence for byte-level research, so an artifact that is not structurally
    # sound is not evidence.
    structural_ok = True
    for label, path in (("t1_base", base), ("declared_real", out)):
        probs = assert_box_chain(path)
        print(f"  box chain {label:14s} {'OK' if not probs else 'BROKEN'}")
        for p in probs:
            structural_ok = False
            print(f"      !! {p['path']} overruns by {p['overrun']} "
                  f"(declared {p['declared_size']}, parent ends {p['parent_ends']})")

    ok = result["matches_expected"] and result["bytes_contain_declared"]
    integrity = _frames_match(base, out)
    ok = ok and integrity["identical"]
    print(f"  frames decode   {integrity['base_frames']} base / "
          f"{integrity['injected_frames']} injected")
    print(f"  frames identical {integrity['identical']}")

    # The two-scope conflict fixture. Route: PyAV writes the STREAM-scope tag (it
    # survives), then the injector sets the CONTAINER-scope one (the muxer
    # overwrites that, so tags alone cannot set it). The two then disagree.
    conflict_base = build_base(os.path.join(FIXTURES, "conflict_base.mp4"),
                                stream_tags={"encoder": "SomeOtherTool 9.9.9"})
    conflict = os.path.join(FIXTURES, "conflict_two_scope.mp4")
    cinfo = inject_declaration(conflict_base, conflict, declared)
    cres = verify(conflict, declared)
    cstream = cres["streams"].get(0, {})
    cframe = _frames_match(conflict_base, conflict)
    print("")
    print("two-scope conflict fixture")
    print(f"  injected        {conflict}")
    print(f"  delta           {cinfo['delta']} bytes")
    print(f"  container meta  {cres['container']}")
    print(f"  stream meta     {cres['streams']}")
    print(f"  frames identical {cframe['identical']}")
    two_scopes = (cres["container"].get("encoder") != cstream.get("encoder")
                  and cstream.get("encoder") is not None)
    conflict_ok = two_scopes and cframe["identical"]
    print(f"  two scopes disagree {two_scopes} "
          f"(container={cres['container'].get('encoder')!r} "
          f"stream={cstream.get('encoder')!r})")

    for label, path in (("conflict_base", conflict_base), ("conflict", conflict)):
        probs = assert_box_chain(path)
        print(f"  box chain {label:14s} {'OK' if not probs else 'BROKEN'}")
        for p in probs:
            structural_ok = False
            print(f"      !! {p['path']} overruns by {p['overrun']} "
                  f"(declared {p['declared_size']}, parent ends {p['parent_ends']})")

    ok = ok and conflict_ok and structural_ok
    print(f"  VERDICT         {'OK' if ok else 'FAILED'}")
    if not structural_ok:
        print("\n  STRUCTURAL FAILURE: a box chain does not close.")
        print("  These fixtures are evidence for byte-level address research")
        print("  (A7-R1); an artifact whose box tree is inconsistent is not")
        print("  evidence, however well it decodes.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
