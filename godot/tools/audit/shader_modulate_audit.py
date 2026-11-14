#!/usr/bin/env python3
"""shader_modulate_audit — a canvas shader that throws the node's fade away
(2026-11-14, pass 381).

In a `canvas_item` fragment, `COLOR = …` discards the vertex colour, which is
where the node's modulate, its self_modulate and every ancestor's arrive. A
node drawn through such a shader cannot be faded, dimmed or tinted by
modulate: the tween runs and the picture does not change. The 3D cast's
portrait shader did this on all three of its paths — the cast never faded in
or out and never stepped back for an insert, through two passes that tuned
the tween (pass 380). The picture panels' halo did it too.

Every canvas shader that assigns COLOR must carry the vertex colour across

    varying vec4 v_mod;
    void vertex() { v_mod = COLOR; }
    …  COLOR = vec4(col, a) * v_mod;

or be listed in SCREEN_PASS with what it is drawn on: a full-screen pass that
reads the screen and that nothing fades by modulate.

    python3 godot/tools/audit/shader_modulate_audit.py
Nonzero exit on any shader that drops modulate and is not listed.
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GODOT = os.path.normpath(os.path.join(HERE, "..", ".."))

# shader file name: what it is drawn on, and why its modulate does not matter.
# Each was read (pass 381): a ColorRect over the whole view inside a locale's
# PostProcess layer or an autoload's own layer, switched by `visible` or by a
# uniform, never by modulate.
SCREEN_PASS = {
    "ascii_directional.gdshader": "locale PostProcess pass (full-rect ColorRect, uniform-driven)",
    "ascii_edges.gdshader": "locale PostProcess pass (unused today; same contract)",
    "ascii_render.gdshader": "locale PostProcess pass",
    "demoscene_post.gdshader": "locale PostProcess pass",
    "gauss_blur.gdshader": "locale PostProcess pass",
    "glyph_field.gdshader": "locale PostProcess pass (unused today; same contract)",
    "liminal_proximity.gdshader": "locale PostProcess pass",
    "motion_ascii.gdshader": "locale PostProcess pass",
    "neon_edge.gdshader": "locale PostProcess pass",
    "old_film.gdshader": "locale PostProcess pass",
    "painted_scene.gdshader": "Background3D's painted pass over its own viewport; `paint` is a uniform",
    "starscape.gdshader": "locale PostProcess pass",
    "trip_feedback.gdshader": "TripSync's feedback buffer (a SubViewport's own rect)",
    "trip_feedback_show.gdshader": "TripSync's full-screen show pass; strength is a uniform",
    "vn_transition.gdshader": "GameEngine's scene transition: `progress` is a uniform, the rect is shown and hidden",
}


def check(path):
    """None when fine, else the reason."""
    src = open(path, encoding="utf-8", errors="replace").read()
    code = re.sub(r"/\*.*?\*/", "", re.sub(r"//[^\n]*", "", src), flags=re.S)
    if not re.search(r"shader_type\s+canvas_item", code):
        return None
    m = re.search(r"void\s+fragment\s*\(\s*\)\s*\{", code)
    if not m:
        return None
    frag = code[m.end():]
    assigns = re.findall(r"\bCOLOR\s*=\s*([^;]+);", frag)
    if not assigns:
        return None
    # the vertex colour carried in a varying that vertex() fills from COLOR
    carried = set()
    vm = re.search(r"void\s+vertex\s*\(\s*\)\s*\{(.*?)\n\}", code, flags=re.S)
    if vm:
        for name in re.findall(r"\bvarying\s+\w+\s+(\w+)\s*;", code):
            if re.search(r"\b%s\s*=\s*[^;]*\bCOLOR\b" % re.escape(name), vm.group(1)):
                carried.add(name)
    dropped = 0
    for rhs in assigns:
        if re.search(r"\bCOLOR\b", rhs):
            continue                    # COLOR = f(COLOR): the incoming colour is in it
        if any(re.search(r"\b%s\b" % re.escape(n), rhs) for n in carried):
            continue
        dropped += 1
    if dropped:
        return "%d of %d COLOR assignment(s) drop the node's modulate" % (dropped, len(assigns))
    return None


def main():
    bad, seen, listed = [], 0, 0
    for path in sorted(glob.glob(os.path.join(GODOT, "**", "*.gdshader"), recursive=True)):
        rel = os.path.relpath(path, GODOT)
        if rel.startswith(".godot") or "addons" in rel.split(os.sep):
            continue
        why = check(path)
        seen += 1
        if why is None:
            continue
        if os.path.basename(path) in SCREEN_PASS:
            listed += 1
            continue
        bad.append((rel, why))
    stale = sorted(n for n in SCREEN_PASS
                   if not glob.glob(os.path.join(GODOT, "**", n), recursive=True))
    for rel, why in bad:
        print("DROPS MODULATE  %-52s %s — carry it (v_mod) or list it in SCREEN_PASS with what it is drawn on" % (rel, why))
    for n in stale:
        print("STALE  %s is listed in SCREEN_PASS and no longer exists" % n)
    print("shader_modulate_audit · %d shader(s) · %d drop modulate unlisted · %d screen pass(es) listed · %d stale"
          % (seen, len(bad), listed, len(stale)))
    return 1 if bad or stale else 0


if __name__ == "__main__":
    sys.exit(main())
