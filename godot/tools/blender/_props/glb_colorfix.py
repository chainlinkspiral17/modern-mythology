# _props/glb_colorfix.py
# ════════════════════════════════════════════════════════════════
# Post-export COLOR_0 check + correction. Pure Python (no bpy).
#
# 2026-09-24: after a Blender update on the Deck, every rebuilt GLB
# rendered washed toward white — the colours were there but lifted. glTF
# COLOR_0 is LINEAR; the old exporter wrote srgb_to_linear(our colour).
# The new chain writes our colour unconverted (either the colour layer
# now takes linear input, or the exporter stopped converting — the GLB
# is the same either way). Godot reads it as linear: 0.5 shows as 0.73.
#
# fix_glb(path, probes) reads the exported file back, compares COLOR_0
# of the probe objects (name -> the RGBA the builder asked for) with
# both readings, and only when the values are UNCONVERTED rewrites every
# COLOR_0 in the file through srgb_to_linear. A correct export (the old
# Blender) is left untouched. Version-proof by measurement, not by
# guessing the version.
# ════════════════════════════════════════════════════════════════
import json
import struct

FMT = {5126: ("f", 4, None), 5121: ("B", 1, 255.0), 5123: ("H", 2, 65535.0)}
NCOMP = {"VEC3": 3, "VEC4": 4}


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _chunks(data):
    off, out = 12, []
    while off + 8 <= len(data):
        clen, ctype = struct.unpack_from("<II", data, off)
        out.append((ctype, off + 8, clen))
        off += 8 + clen
    return out


def _color_accessors(j):
    seen = set()
    for m in j.get("meshes", []):
        for p in m.get("primitives", []):
            a = p.get("attributes", {}).get("COLOR_0")
            if a is not None and a not in seen:
                seen.add(a)
                yield a


def _read(j, binb, bin_off, ai):
    acc = j["accessors"][ai]
    bv = j["bufferViews"][acc["bufferView"]]
    code, size, norm = FMT[acc["componentType"]]
    n = NCOMP.get(acc["type"])
    if n is None:
        return None
    stride = bv.get("byteStride") or size * n
    base = bin_off + bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    out = []
    for k in range(acc["count"]):
        vals = struct.unpack_from("<%d%s" % (n, code), binb, base + k * stride)
        out.append([v / norm for v in vals] if norm else list(vals))
    return out, (code, size, norm, n, stride, base)


def fix_glb(path, probes, verbose=True):
    """Returns 'ok' (already linear), 'fixed' (rewritten), or a reason
    it could not judge ('no-probes', 'no-colour', 'ambiguous')."""
    try:
        data = bytearray(open(path, "rb").read())
    except OSError:
        return "no-file"
    ch = {t: (o, l) for t, o, l in _chunks(data)}
    if 0x4E4F534A not in ch or 0x004E4942 not in ch:
        return "no-colour"
    jo, jl = ch[0x4E4F534A]
    j = json.loads(bytes(data[jo:jo + jl]))
    bin_off = ch[0x004E4942][0]
    # probe: node name -> first COLOR_0 value of its mesh
    raw_err, lin_err, n = 0.0, 0.0, 0
    for node in j.get("nodes", []):
        want = probes.get(node.get("name", ""))
        if want is None or "mesh" not in node:
            continue
        ai = j["meshes"][node["mesh"]]["primitives"][0].get("attributes", {}).get("COLOR_0")
        if ai is None:
            continue
        got = _read(j, data, bin_off, ai)
        if not got:
            continue
        v = got[0][0]
        for c in range(3):
            w = float(want[c])
            if 0.15 < w < 0.9:           # where the two readings differ most
                raw_err += abs(v[c] - w)
                lin_err += abs(v[c] - srgb_to_linear(w))
                n += 1
        if n >= 60:
            break
    if n == 0:
        return "no-probes"
    raw_err, lin_err = raw_err / n, lin_err / n
    if lin_err <= raw_err:
        return "ok"
    if raw_err > 0.02 or lin_err < 0.05:
        return "ambiguous"
    fixed = 0
    for ai in _color_accessors(j):
        got = _read(j, data, bin_off, ai)
        if not got:
            continue
        rows, (code, size, norm, ncomp, stride, base) = got
        for k, row in enumerate(rows):
            new = [srgb_to_linear(x) for x in row[:3]] + row[3:]
            if norm:
                new = [int(round(max(0.0, min(1.0, x)) * norm)) for x in new]
            struct.pack_into("<%d%s" % (ncomp, code), data, base + k * stride, *new)
            fixed += 1
    open(path, "wb").write(bytes(data))
    if verbose:
        print("[glb_colorfix] %s: COLOR_0 was written UNCONVERTED (raw err %.3f vs linear %.3f over %d samples)"
              " — converted %d colours to linear" % (path.rsplit("/", 1)[-1], raw_err, lin_err, n, fixed))
    return "fixed"


def probes_from_bpy(bpy, limit=300):
    """name -> the colour each mesh's first corner holds, read back from
    Blender. The layer returns what the builder WROTE whichever way the
    running version stores it, so this is the intended colour."""
    out = {}
    for obj in list(bpy.data.objects):
        if len(out) >= limit:
            break
        me = getattr(obj, "data", None)
        if me is None or getattr(obj, "type", "MESH") != "MESH":
            continue
        try:
            layer = None
            if hasattr(me, "vertex_colors") and len(me.vertex_colors):
                layer = me.vertex_colors[0]
            elif hasattr(me, "color_attributes") and len(me.color_attributes):
                layer = me.color_attributes[0]
            if layer is None or not len(layer.data):
                continue
            out[obj.name] = tuple(layer.data[0].color)
        except Exception:
            continue
    return out


CALLS = 0      # the dry-run gate checks every export reached postfix


def postfix(path, bpy):
    """Call right after bpy.ops.export_scene.gltf(filepath=path, …)."""
    global CALLS
    CALLS += 1
    try:
        r = fix_glb(path, probes_from_bpy(bpy))
        if r not in ("ok", "fixed"):
            print("[glb_colorfix] %s: %s" % (path.rsplit("/", 1)[-1], r))
        return r
    except Exception as e:      # never fail a build over the check
        print("[glb_colorfix] %s: check failed (%s)" % (path.rsplit("/", 1)[-1], e))
        return "error"
