"""bg_resolve.py — the engine's own reading of a `bg` node's src
(GameEngine.resolve_bg), for every audit that asks what the player SEES.

Most of vols 1–4 name a painting that resources/vn/bg_places.json swaps
for a 3D set at load ({"places": {"<stem>": {"to": "3d:<preset>",
"by_scene": {"<scene_id>": "3d:<preset>"}}}}). An audit that read `src`
literally counted those chapters as 2D and never checked their cues
(2026-11-06, pass 300: 98 chapters, the wrong_room and shot_marker gates
among the blind)."""
import json, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_PLACES = None


def _places():
    global _PLACES
    if _PLACES is None:
        try:
            bp = json.load(open(os.path.join(ROOT, "resources", "vn", "bg_places.json"), encoding="utf-8"))
            _PLACES = bp.get("places", {}) if isinstance(bp, dict) else {}
        except Exception:
            _PLACES = {}
    return _PLACES


def resolve_bg(src, scene_id=""):
    """src as GameEngine.resolve_bg returns it: "3d:<preset>" or the path."""
    src = str(src or "")
    if src == "" or src.startswith("3d:"):
        return src
    entry = _places().get(os.path.splitext(os.path.basename(src))[0])
    if not isinstance(entry, dict):
        return src
    by_scene = entry.get("by_scene")
    if scene_id and isinstance(by_scene, dict) and by_scene.get(scene_id):
        return str(by_scene[scene_id])
    to = entry.get("to")
    return str(to) if to else src


def preset_of(src, scene_id=""):
    """The 3D preset a bg node plays on, or None for a painting."""
    s = resolve_bg(src, scene_id)
    return s[3:] if s.startswith("3d:") else None
