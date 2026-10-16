#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Recover build/gen/felucca_font.h (X0X's tools/gen_font.py output) from an upstream x0x.wasm.

X0X's font tables are rendered from TTFs with Pillow + FreeType + libraqm (OpenType tnum). Rather
than depend on that stack (and on FreeType's exact version), this lifts the six finished tables out
of the upstream web build's data segment, so a rebuild draws byte-for-byte the same screen.

  python3 -I font_from_wasm.py x0x.wasm build/gen/felucca_font.h

The tables are found as felucca_font_t records {h, pad=2, first=32, last, adv*, bw*, off*, data*}
(firmware/src/app/ui.c); faces are told apart by line height, range and advance width:
T 32..95, XS / S / B 32..126 (B has the most ink of the two 16-px faces), M 32..95 h 24, L 32..57.
"""
import struct
import sys


def uleb(b, i):
    r = s = 0
    while True:
        x = b[i]
        i += 1
        r |= (x & 0x7F) << s
        s += 7
        if x < 0x80:
            return r, i


def sleb(b, i):
    r = s = 0
    while True:
        x = b[i]
        i += 1
        r |= (x & 0x7F) << s
        s += 7
        if x < 0x80:
            return (r - (1 << s) if x & 0x40 else r), i


def data_image(b):
    if b[:4] != b"\0asm":
        raise SystemExit("not a wasm module")
    mem = bytearray(8 << 20)
    i = 8
    while i < len(b):
        sid = b[i]
        n, i = uleb(b, i + 1)
        end = i + n
        if sid == 11:
            cnt, a = uleb(b, i)
            for _ in range(cnt):
                mode, a = uleb(b, a)
                if mode != 0 or b[a] != 0x41:
                    raise SystemExit("unexpected data segment form")
                off, a = sleb(b, a + 1)
                a += 1                                   # end
                ln, a = uleb(b, a)
                mem[off:off + ln] = b[a:a + ln]
                a += ln
        i = end
    return mem


def fonts(mem):
    out = []
    for p in range(0, len(mem) - 20, 4):
        h, pad, first, last, adv, bw, off, data = struct.unpack_from("<BBBBIIII", mem, p)
        if pad != 2 or first != 32 or last not in (57, 95, 126) or not 6 <= h <= 48:
            continue
        if not all(0 < x < len(mem) for x in (adv, bw, off, data)):
            continue
        n = last - first + 1
        o = struct.unpack_from("<%dH" % n, mem, off)
        if o[0] != 0 or any(o[k] > o[k + 1] for k in range(n - 1)):
            continue
        w = bytes(mem[bw:bw + n])
        size = o[-1] + h * ((w[-1] + 1) // 2)
        d = bytes(mem[data:data + size])
        ink = sum((x >> 4) + (x & 15) for x in d) / max(1, len(d))
        out.append(dict(h=h, first=first, last=last, adv=bytes(mem[adv:adv + n]), bw=w, off=o, data=d, ink=ink))
    return out


def name(fs):
    by = {}
    wide = sorted([f for f in fs if f["last"] == 126], key=lambda f: (f["h"], f["ink"]))
    if len(wide) != 3:
        raise SystemExit("expected three 32..126 faces, found %d" % len(wide))
    by["XS"], by["S"], by["B"] = wide
    for f in fs:
        if f["last"] == 57:
            by["L"] = f
        elif f["last"] == 95:
            by["M" if f["h"] >= 20 else "T"] = f
    if sorted(by) != ["B", "L", "M", "S", "T", "XS"]:
        raise SystemExit("could not tell the six faces apart: %s" % sorted(by))
    return by


def main(src, dst):
    by = name(fonts(data_image(open(src, "rb").read())))
    lines = ["/* recovered by font_from_wasm.py from the upstream x0x.wasm: tools/gen_font.py's tables, font set barlow */",
             "#pragma once", "#include <stdint.h>", "#define FONT_PAD 2  /* x scale for L, see below */", ""]
    for nm in ("T", "XS", "S", "B", "M", "L"):
        f = by[nm]
        d = f["data"]
        lines.append(f"static const uint8_t FONT_{nm}_DATA[{len(d)}] = {{")
        for k in range(0, len(d), 24):
            lines.append("    " + ", ".join(f"0x{x:02x}" for x in d[k:k + 24]) + ",")
        lines.append("};")
        lines.append(f"static const uint16_t FONT_{nm}_OFF[{len(f['off'])}] = {{" + ", ".join(map(str, f["off"])) + "};")
        lines.append(f"static const uint8_t FONT_{nm}_ADV[{len(f['adv'])}] = {{" + ", ".join(map(str, f["adv"])) + "};")
        lines.append(f"static const uint8_t FONT_{nm}_BW[{len(f['bw'])}] = {{" + ", ".join(map(str, f["bw"])) + "};")
        lines.append(f"static const felucca_font_t FONT_{nm} = {{ {f['h']}, 2, {f['first']}, {f['last']}, "
                     f"FONT_{nm}_ADV, FONT_{nm}_BW, FONT_{nm}_OFF, FONT_{nm}_DATA }};")
        lines.append("")
        print(f"font {nm}: h {f['h']}, {f['first']}..{f['last']}, {len(d)} B")
    open(dst, "w").write("\n".join(lines))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2])
