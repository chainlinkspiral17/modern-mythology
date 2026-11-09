#!/usr/bin/env python3
"""sign_roof_audit.py — no sign stands inside a roof (2026-11-09).

The user: "sign text not visible, cutting through roof? this is like this
all over. the audit has been awful." A sign, its letters, its neon, are
thin parts; a roof slab, a parapet, an eave or an awning running through
them overlaps by a few centimetres — under every depth floor the overlap
audit keeps — so 53 of them stood inside their roofs unreported: the
Christian Ice Co.'s ICE letters wholly inside the parapet, Pasadena's 40
storefront signs cut by their own awnings, the nightclub's neon half
buried.

For every sign-like part (sign / letter / text / neon / logo / marquee /
banner) and every roof-like part (roof / parapet / eave / soffit / gable /
cornice / shingle / rafter / awning) that intersect, the sign is CUT when
the roof part spans the sign's whole thickness over at least 15 % of its
face. A sign MOUNTED into its backer — its back in the parapet, its face
proud of it — passes: the roof part does not reach its face.

    python3 tools/audit/sign_roof_audit.py              # every builder (a gate)
    python3 tools/audit/sign_roof_audit.py graustark    # some
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vantage_obstruction_audit as VO  # noqa: E402

SIGN = re.compile(r"letter|sign|text|_txt|lettering|neon|logo|marquee|banner", re.I)
ROOF = re.compile(r"roof|parapet|eave|soffit|gable|cornice|shingle|rafter|awning", re.I)
NOT = re.compile(r"wear_|post|pole|bracket|frame_|_frame|chain|rope|cable|wire|legs?\b|_legs", re.I)
FACE_FRAC = 0.15
# read and judged: a sloped sheet's bounding box reaches a sign it clears
KNOWN = {
    ("harmony_terrain", "KwikShop_KwikStop_OpenSign"):
        "Awning_3_0 is a sloped sheet; at the window's plane it is 30 cm above the OPEN sign",
}


def cuts(boxes):
    out = []
    signs = [b for b in boxes if SIGN.search(b[0]) and not NOT.search(b[0]) and not ROOF.search(b[0])]
    roofs = [b for b in boxes if ROOF.search(b[0]) and not SIGN.search(b[0])]
    for s in signs:
        sc, sh = s[1], s[2]
        t = min(range(3), key=lambda i: sh[i])
        o = [i for i in range(3) if i != t]
        area = 4.0 * sh[o[0]] * sh[o[1]]
        if area <= 0 or max(sh) > 6.0:
            continue
        for r in roofs:
            rc, rh = r[1], r[2]
            ov = 1.0
            for i in o:
                d = min(sc[i] + sh[i], rc[i] + rh[i]) - max(sc[i] - sh[i], rc[i] - rh[i])
                if d <= 0.002:
                    ov = 0.0
                    break
                ov *= d
            if ov < FACE_FRAC * area:
                continue
            # the roof part spans the sign's whole thickness: the sign is in it
            if rc[t] - rh[t] <= sc[t] - sh[t] + 0.005 and rc[t] + rh[t] >= sc[t] + sh[t] - 0.005:
                out.append((s[0], r[0], ov / area))
                break
    return out


def main():
    want = [a for a in sys.argv[1:] if not a.startswith("-")]
    locs = want or sorted({f[6:-3] for f in os.listdir(os.path.join(HERE, "..", "blender", "locales"))
                           if f.startswith("build_") and f.endswith(".py")})
    bad = 0
    for loc in locs:
        try:
            boxes = VO.boxes_for(loc)
        except Exception:
            continue
        found = [x for x in cuts(boxes or []) if (loc, x[0]) not in KNOWN]
        for s, r, f in found:
            print("CUT   %-26s %-38s inside %s (%.0f%% of its face)" % (loc, s, r, f * 100))
        bad += len(found)
    print("sign_roof_audit · %d locale(s) · %d sign part(s) inside a roof" % (len(locs), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
