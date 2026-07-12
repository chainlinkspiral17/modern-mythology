extends Control
## Character portrait layer — left / center / right slots.
##
## Portrait source preference, per character:
##   1. ASCII composition at  res://resources/substrates/compositions/portrait_<char>.json
##      — visualizer + image-ref + image_frames flicker + border, all
##      pinned to explicit w/h that fit the canvas. AsciiComposition
##      scales the canvas down into the slot via _fit_canvas, so the
##      whole layered look survives at 240×360.
##   2. PNG texture at  res://assets/characters/<char>/<char>_<expr>.png
##   3. PNG texture at  res://assets/characters/<char>/<char>_neutral.png
##                      (tinted via modulate to imply expression)
##   4. Animated placeholder silhouette

const ASCII_COMPOSITION_SCRIPT := preload("res://scenes/game/AsciiComposition.gd")
# Preloaded by path (not the global class name) so this script never
# depends on class_name scan order on a fresh project open.
const BUST_PORTRAIT := preload("res://scripts/vn/VnBustPortrait.gd")
const PORTRAIT_COMP_ROOT := "res://resources/substrates/compositions/"

# 3D portrait pipeline — when a character has a textured GLB in
# assets/3d/characters/heroes/, render it into a SubViewport-backed
# Portrait3D scene instead of falling through to PNG / composition.
# Mapping is from CharLayer.char_key() output to the canonical GLB
# filename (see godot/tools/hero_uploader/index.html HEROES array
# for the authoritative roster). The map exists because some scene
# JSONs use short names ("frasier") while the GLBs use full canon
# filenames ("frasier_temple.glb").
const PORTRAIT_3D_SCENE := preload("res://scenes/vn/Portrait3D.tscn")
const PORTRAIT_3D_GLB_ROOT := "res://assets/3d/characters/heroes/"

# Demons get their own GLB root + a SHARED Portrait3D scene with the
# digital-static shader pushed to strength=1 (via set_demon_mode).
# Canon: up to 8 demon slots; only `the_demon` is in ch1 (the man
# at the empty stool at DEVIL station). Add new entries as models
# arrive — keys must match the visitors.json id ("the_demon" etc.)
# so scene JSONs route correctly. Implicit `<key>.glb` lookup also
# works, so a model named `the_demon.glb` would resolve without an
# explicit entry here.
const PORTRAIT_3D_DEMON_ROOT := "res://assets/3d/characters/demons/"
const PORTRAIT_3D_DEMON_KEY_TO_GLB := {
	# ch1 — the only demon for The Magician's first scenarios
	"the_demon":         "the_demon.glb",
	# Reserved slots (placeholders — drop models in as they're built)
	# "the_drifter":     "the_drifter.glb",
	# "the_birdwatcher": "the_birdwatcher.glb",
	# "the_critic":      "the_critic.glb",
	# "the_superfan":    "the_superfan.glb",
	# "the_twins":       "the_twins.glb",
	# "drunk_uncle":     "drunk_uncle.glb",
	# "mackenzie_remote":"mackenzie_remote.glb",
}

const PORTRAIT_3D_KEY_TO_GLB := {
	# 0 The Fool
	"john":              "john_frank.glb",
	"john_frank":        "john_frank.glb",
	# I The Magician
	"frasier":           "frasier_temple.glb",
	"frasier_temple":    "frasier_temple.glb",
	# II The High Priestess
	"elicia":            "elicia_temple.glb",
	"elicia_temple":     "elicia_temple.glb",
	# III The Empress
	"nicola":            "nicola.glb",
	"nicola_greer":      "nicola.glb",
	# IV The Emperor
	"dante":             "dante_dambrosio.glb",
	"dante_dambrosio":   "dante_dambrosio.glb",
	# VII The Chariot
	"antonio":           "antonio.glb",
	"antonio_dambrosio": "antonio.glb",
	# Ensemble · Alberto
	"alberto":           "alberto.glb",
	# ── VOL 6 · PLANNED COMMUNITY (Harmony Creek Estates) ──
	# Scene JSONs use first-name keys ("char": "Sam", "Diego", etc.);
	# the slugifier lowercases + replaces spaces, so a "Sam Miller"
	# in dialogue still routes through the "sam" key here.
	"sam":               "sam_miller.glb",
	"sam_miller":        "sam_miller.glb",
	"diego":             "diego_ramos.glb",
	"diego_ramos":       "diego_ramos.glb",
	"maya":              "maya_daigle.glb",
	"maya_daigle":       "maya_daigle.glb",
	"rick":              "rick_cosmic.glb",
	"rick_cosmic":       "rick_cosmic.glb",
	"skip":              "skip_donnelly.glb",
	"skip_donnelly":     "skip_donnelly.glb",
	"tanya":             "tanya_horne.glb",
	"tanya_horne":       "tanya_horne.glb",
	"carl":              "carl_reno.glb",
	"carl_reno":         "carl_reno.glb",
	# ── VOL 7 · LAND OF MILK AND HONEY (Smolvud, Oregon coast) ──
	"lena":              "lena_vargas.glb",
	"lena_vargas":       "lena_vargas.glb",
	"wren":              "wren.glb",
	"tem":               "tem.glb",
	"gable":             "mrs_gable.glb",
	"mrs_gable":         "mrs_gable.glb",
	"marian_gable":      "mrs_gable.glb",
	"petra":             "petra.glb",
	"kai":               "kai.glb",
	"per":               "per.glb",
	"sal":               "sal_carratura.glb",
	"sal_carratura":     "sal_carratura.glb",
	"finn":              "finn.glb",
}
const PORTRAIT_TEX_ROOT  := "res://assets/characters/"

# Debug: overlay the resolved asset path on each portrait so you can
# see which file the engine loaded while playing through the game.
# OFF for play — flip on when debugging asset assignments.
const DEBUG_ASSET_OVERLAY: bool = false

# Expression tint multipliers applied to mono substrate portraits via modulate.
# Mirrors the table in tools/raster_substrate.py.
const EXPR_TINTS := {
	"neutral":   Color(1.00, 1.00, 1.00),
	"happy":     Color(1.00, 0.96, 0.80),
	"excited":   Color(1.00, 0.96, 0.80),
	"pleased":   Color(1.00, 0.96, 0.80),
	"warm":      Color(1.00, 0.96, 0.80),
	"sad":       Color(0.72, 0.82, 1.00),
	"melancholy":Color(0.72, 0.82, 1.00),
	"upset":     Color(0.72, 0.82, 1.00),
	"surprised": Color(1.00, 1.00, 0.78),
	"shocked":   Color(1.00, 1.00, 0.78),
	"wide":      Color(1.00, 1.00, 0.78),
	"angry":     Color(1.00, 0.55, 0.50),
	"furious":   Color(1.00, 0.55, 0.50),
	"frustrated":Color(1.00, 0.55, 0.50),
	"tired":     Color(0.78, 0.82, 0.92),
	"nervous":   Color(0.92, 0.95, 1.00),
	"scared":    Color(0.92, 0.95, 1.00),
	"uneasy":    Color(0.92, 0.95, 1.00),
}

# Modern-VN cutout mode (2026-07-12 redesign): portraits are clean
# 3/4 cutouts hovering over the full-bleed scene — no dark backdrop
# box, no scrim, no ASCII border. Larger and bottom-anchored so the
# figure rises from the bottom edge, lower body behind the dialogue.
# Flip false to restore the boxed-portrait look.
const CUTOUT_MODE := true

# Cutout portraits, enlarged ~2x (2026-07-12): each figure fills a
# tall slot that runs off the bottom edge, so the camera can frame
# more of the body (thigh-up, see Portrait3D). Left/right hug the
# screen edges (1280 wide); center sits between them. Slight overlap
# left↔right is fine — the active-speaker pop separates them, and two
# people at 3/4 facing inward reads naturally shoulder-to-shoulder.
const POSITIONS := {
	"left":   Vector2(-40, 10),
	"center": Vector2(280, -10),
	"right":  Vector2(600, 10),
}
const SPRITE_W    := 720.0
const SPRITE_H    := 760.0
const SCRIM_COLOR := Color(0.0, 0.0, 0.0, 0.10)
const IDLE_AMP    := 4.0
const IDLE_PERIOD := 2.5
const IDLE_PHASE  := {"left": 0.0, "center": 0.85, "right": 1.7}

# Parallax: portraits counter-drift the bg sway (GameEngine drives the
# bg with the same SWAY_PERIOD). Small amplitude to sell depth without
# disorienting the figure.
const PARALLAX_PERIOD := 5.4
const PARALLAX_X_AMP  := 2.5
const PARALLAX_Y_AMP  := 1.2

# Active speaker pop: scale + alpha boost on the active portrait,
# desaturate + dim non-active. Non-active really pulls back so the
# focus reads strongly during back-and-forth dialogue.
const ACTIVE_SCALE   := 1.05
const ACTIVE_ALPHA   := 1.00
const INACTIVE_SCALE := 0.92
const INACTIVE_ALPHA := 0.55

# Character-keyed accent palette. Used for portrait border tint,
# dialog speaker name color, visualizer peak hint, and the active-
# speaker glow boost. Fall back to neutral when a character isn't
# registered yet.
const CHAR_ACCENTS := {
	"john":      Color("#9bc3ff"),
	"frasier":   Color("#ffa860"),
	"stranger":  Color("#c64878"),
	"elicia":    Color("#b89ad6"),
	"nicola":    Color("#e8a860"),
	"the_demon": Color("#7cffb0"),
}
const ACCENT_DEFAULT := Color("#d6c8a8")


# ── Facing / horizontal flip ─────────────────────────────────────────
# Auto-flip so portraits face inward toward the center of the screen.
# Default assumption: art is drawn facing RIGHT. Left slot stays
# unflipped (already faces right toward center); right slot mirrors
# (then faces left toward center); center stays unflipped.
const AUTO_FLIP_BY_POS := {
	"left":   false,
	"center": false,
	"right":  true,
}

# Per-character orientation override. Add entries here when a
# character's art is drawn facing LEFT by default, or "forward" when
# it's a symmetrical face crop where flipping looks wrong. Keys not
# listed default to "right" and follow AUTO_FLIP_BY_POS.
const CHAR_FACING := {
	# examples — uncomment + edit to match your art:
	# "frasier":  "forward",   # face crop, symmetrical
	# "antonio":  "left",      # art faces left → inverts the slot rule
}


func _compute_flip(key: String, pos: String, scene_facing: String) -> bool:
	# Scene-JSON `facing` field beats everything:
	#   "forward" → never flip (figure faces viewer)
	#   "left"    → force figure to face left
	#   "right"   → force figure to face right
	if scene_facing == "forward":
		return false
	if scene_facing == "left" or scene_facing == "right":
		# pos's effective facing AFTER auto-flip: left/center face
		# right (unflipped), right faces left (flipped).
		var natural_faces_right: bool = pos != "right"
		var want_right: bool = scene_facing == "right"
		return natural_faces_right != want_right
	# Per-char default
	var face: String = CHAR_FACING.get(key, "right")
	if face == "forward":
		return false
	var should_flip: bool = AUTO_FLIP_BY_POS.get(pos, false)
	if face == "left":
		# Art is mirrored relative to default — invert the slot rule.
		should_flip = not should_flip
	return should_flip


# Slugify a scene-supplied char name into the canonical key used for
# portrait composition lookups + CHAR_ACCENTS. "The Demon" → "the_demon",
# "oil exec" → "oil_exec". Spaces collapse to underscores so scenes can
# author display names with spaces without breaking file lookups.
func char_key(char_name: String) -> String:
	return char_name.strip_edges().to_lower().replace(" ", "_")


# Returns the absolute res:// path to a textured hero GLB for the
# given char_key(), or "" if no 3D portrait is available. Falls
# back to a "<key>.glb" filename lookup so future heroes can ship
# without needing a PORTRAIT_3D_KEY_TO_GLB entry — just drop the
# GLB into assets/3d/characters/heroes/ with the canonical name.
func _resolve_portrait_3d_glb(key: String) -> String:
	# Demons checked FIRST so a key listed in both registries
	# routes to the demon model (and triggers digital-static mode).
	if PORTRAIT_3D_DEMON_KEY_TO_GLB.has(key):
		var dpath: String = PORTRAIT_3D_DEMON_ROOT + PORTRAIT_3D_DEMON_KEY_TO_GLB[key]
		if FileAccess.file_exists(dpath) or ResourceLoader.exists(dpath):
			return dpath
	var ddirect: String = PORTRAIT_3D_DEMON_ROOT + key + ".glb"
	if FileAccess.file_exists(ddirect) or ResourceLoader.exists(ddirect):
		return ddirect
	# Heroes — explicit registry then implicit `<key>.glb`
	if PORTRAIT_3D_KEY_TO_GLB.has(key):
		var path: String = PORTRAIT_3D_GLB_ROOT + PORTRAIT_3D_KEY_TO_GLB[key]
		if FileAccess.file_exists(path) or ResourceLoader.exists(path):
			return path
	var direct: String = PORTRAIT_3D_GLB_ROOT + key + ".glb"
	if FileAccess.file_exists(direct) or ResourceLoader.exists(direct):
		return direct
	return ""


# Returns true when the resolved GLB path is inside the demons/
# folder — used to push the Portrait3D into demon_mode after load.
func _is_demon_glb(glb_path: String) -> bool:
	return glb_path.begins_with(PORTRAIT_3D_DEMON_ROOT)


# Public lookup so DialogueBox / GameEngine / etc. can color speaker
# names and other chrome consistently with portrait accents.
func accent_for(char_name: String) -> Color:
	return CHAR_ACCENTS.get(char_key(char_name), ACCENT_DEFAULT)

# Which slot ("left"/"center"/"right") the given character currently
# occupies, or "" if they have no on-screen portrait. DialogueBox uses
# this to slide the text column under whoever is speaking.
func slot_of(char_name: String) -> String:
	var key := char_key(char_name)
	if key == "":
		return ""
	for pos: String in _slots:
		var slot = _slots[pos]
		if slot != null and char_key(str(slot["name"])) == key:
			return pos
	return ""

# slot -> {name, expr, node: Control}
var _slots: Dictionary = {"left": null, "center": null, "right": null}
var _t:     float      = 0.0
# Keys whose full "tried:" path list has already been printed this
# session — repeat placeholder appearances log one line only.
static var _placeholder_logged: Dictionary = {}


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	# Spawn the per-portrait debug overlay (visible on Esc/mouse-
	# released). It introspects this CharLayer's slot table via
	# get_active_portrait3d_list, so attaching it as a child means
	# the lookup just needs get_parent().
	var overlay_script = load("res://scripts/vn/VnPortraitDebugOverlay.gd")
	if overlay_script != null:
		var overlay = overlay_script.new()
		overlay.name = "VnPortraitDebugOverlay"
		add_child(overlay)


func _process(delta: float) -> void:
	_t += delta
	# Counter-drift the bg sway. Negative sign so portraits move
	# opposite to the boat list, reading as figures floating *on* the
	# room rather than locked to it.
	var sway_phase: float = _t * TAU / PARALLAX_PERIOD
	var pdx: float = -sin(sway_phase) * PARALLAX_X_AMP
	var pdy: float = -cos(sway_phase * 0.7) * PARALLAX_Y_AMP
	for pos: String in _slots:
		var slot = _slots[pos]
		if slot == null:
			continue
		var node: Control = slot["node"]
		var phase: float  = IDLE_PHASE[pos]
		var idle_y: float = sin((_t + phase) * TAU / IDLE_PERIOD) * IDLE_AMP
		node.position = POSITIONS[pos] + Vector2(pdx, idle_y + pdy)
		# ── Subtle breath: ±1% scale on the tint_holder, longer period
		# than position sway so the two motions don't beat against each
		# other. Reads as the figure inhaling.
		var breath_phase: float = (_t + phase * 0.6) * TAU / (IDLE_PERIOD * 1.7)
		var breath_s: float = 1.0 + sin(breath_phase) * 0.010
		# Godot 4.6 emits an error from get_meta(name, default) when
		# the meta is missing even though the default is honoured —
		# guard with has_meta to keep the debugger quiet. Placeholder
		# wrappers explicitly remove_meta("tint"), so this branch is
		# expected to skip cleanly for them.
		if node.has_meta("tint"):
			var tint_holder: Control = node.get_meta("tint") as Control
			if tint_holder != null:
				# Combine breath scale with horizontal flip (set in
				# show_character via "flip_x" meta — -1 to mirror,
				# +1 to keep natural orientation).
				var flip_x: float = node.get_meta("flip_x") if node.has_meta("flip_x") else 1.0
				tint_holder.pivot_offset = tint_holder.size * 0.5
				tint_holder.scale = Vector2(flip_x * breath_s, breath_s)
		# Blink overlay disabled — was a fixed-anchor dark band at
		# slot y=30-42%, which only aligned with eye-level when the
		# portrait was a tight face crop centered in the slot.
		# ── Border redraw so ASCII frame tracks position + breath
		if node.has_meta("border"):
			var border: Control = node.get_meta("border") as Control
			if border != null:
				border.queue_redraw()


# Single-frame blink: a thin dark band at eye-level fades in/out
# over ~120 ms. Reads as a blink without any actual frame data on
# the portrait.
func _fire_blink(node: Control) -> void:
	if not node.has_meta("tint"):
		return
	var tint_holder: Control = node.get_meta("tint") as Control
	if tint_holder == null: return
	var blink := ColorRect.new()
	blink.color = Color(0.02, 0.02, 0.03, 0.0)
	blink.anchor_left = 0.10; blink.anchor_right = 0.90
	blink.anchor_top = 0.30;  blink.anchor_bottom = 0.42
	blink.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tint_holder.add_child(blink)
	var tw := blink.create_tween()
	tw.tween_property(blink, "color:a", 0.55, 0.06)
	tw.tween_property(blink, "color:a", 0.0,  0.08)
	tw.tween_callback(blink.queue_free)


# ── Public API ────────────────────────────────────────────────────────────────

# Set by GameEngine on every bg change. Over a LIVE 3D shot the
# picture's center is the subject (staged cast, authored inserts) —
# a 300x320 portrait card parked there covers exactly what the
# camera is framing. Comic-inset composition: portraits belong in
# the corners when the bg is a 3D camera, so "center" remaps to a
# free flank. Flat 2D bgs keep the center slot (backdrop, nothing
# to cover).
var bg_is_3d: bool = false


func show_character(char_name: String, expr: String, pos: String, facing: String = "") -> void:
	if not POSITIONS.has(pos):
		pos = "center"
	if bg_is_3d and pos == "center":
		var k := char_key(char_name)
		var right_slot: Variant = _slots.get("right")
		var left_slot: Variant = _slots.get("left")
		if right_slot == null or (right_slot is Dictionary and right_slot["name"] == k):
			pos = "right"
		elif left_slot == null or (left_slot is Dictionary and left_slot["name"] == k):
			pos = "left"
	# Store the slug, not the raw display name, so identity checks work
	# regardless of casing/spacing in scene JSON ("The Demon" vs "the demon").
	var key := char_key(char_name)
	# Compute horizontal flip — auto-inward by default, scene-JSON
	# `facing` field overrides if present.
	var should_flip: bool = _compute_flip(key, pos, facing)
	# If this character is already shown at a DIFFERENT position, free
	# that portrait first — the new show is the character moving, not a
	# second copy. Without this, scene JSONs that re-show the same
	# character at a new position (e.g. kai shown at "right" then later
	# at "center") leave both portraits on screen and the bug surfaces
	# as "the same character appears twice" or "portraits repeating
	# across scenes."
	for other_pos: String in _slots:
		if other_pos == pos:
			continue
		var other_slot = _slots[other_pos]
		if other_slot != null and other_slot["name"] == key:
			_fade_out_free(other_slot["node"])
			_slots[other_pos] = null
			break
	var slot = _slots[pos]
	if slot != null and slot["name"] != key:
		# Different character in this slot — replace.
		_fade_out_free(slot["node"])
		slot = null
	if slot == null:
		var node := _make_portrait(char_name, expr, pos)
		node.set_meta("flip_x", -1.0 if should_flip else 1.0)
		_slots[pos] = {"name": key, "expr": expr, "node": node}
	else:
		# Same character in this slot — just update expression. No new
		# portrait node, no duplicate, no fade-in.
		_update_expr(slot["node"], char_name, expr)
		slot["expr"] = expr
		# Allow scene-JSON facing to re-flip an existing portrait
		# without recreating it (char turns to face away mid-scene).
		slot["node"].set_meta("flip_x", -1.0 if should_flip else 1.0)


func update_expression(char_name: String, expr: String) -> void:
	var key := char_key(char_name)
	for pos: String in _slots:
		var slot = _slots[pos]
		if slot != null and slot["name"] == key:
			_update_expr(slot["node"], char_name, expr)
			slot["expr"] = expr


func hide_at(pos: String) -> void:
	var slot = _slots.get(pos)
	if slot != null:
		_fade_out_free(slot["node"])
		_slots[pos] = null


func hide_all() -> void:
	# Scene transitions hard-clear portraits + ghosts immediately.
	# Cross-fade (with ghost silhouette) is reserved for hide_at
	# during a scene; on scene/chapter change we drop everything
	# in the same frame so the next scene starts clean instead of
	# overlapping a half-faded prior portrait with new dialogue.
	for pos: String in _slots:
		var slot = _slots.get(pos)
		if slot != null:
			var node: Control = slot["node"]
			if is_instance_valid(node):
				node.queue_free()
			_slots[pos] = null
	for g in _ghosts:
		if is_instance_valid(g):
			g.queue_free()
	_ghosts.clear()


# Returns true if a portrait for this character is currently in
# any of the three slots. Used by GameEngine._ensure_portrait to
# auto-spawn a portrait the first time a say / think directive
# fires for a character that the scene never `show`d explicitly.
# (Pattern hits 100+ existing scenes where the POV character
# speaks via say/think but is never shown — the user's authorial
# intent is that the POV character is visible + idle.)
func has_character(char_name: String) -> bool:
	var key := char_key(char_name)
	for pos: String in _slots:
		var slot = _slots[pos]
		if slot != null and slot["name"] == key:
			return true
	return false


# Pick the first empty slot in center → right → left preference.
# Falls back to "center" if every slot is occupied (caller's
# show_character will then replace whatever is there).
func first_empty_slot() -> String:
	for pos in ["center", "right", "left"]:
		if _slots[pos] == null:
			return pos
	return "center"


# Snapshot of every active 3D-portrait slot — used by the VN
# portrait-debug overlay (Esc with a 3D bg active). Each entry:
#   { "pos": "center"|"left"|"right",
#     "name": canonical key (e.g. "sam"),
#     "expr": current expression,
#     "portrait3d": SubViewportContainer (Portrait3D instance),
#     "glb_path": String — the GLB the portrait was loaded from }
# Skips slots whose wrapper.kind != "portrait3d" — PNG/composition/
# placeholder portraits don't have 3D controls.
func get_active_portrait3d_list() -> Array:
	var out: Array = []
	for pos: String in _slots:
		var slot = _slots[pos]
		if slot == null:
			continue
		var wrapper: Node = slot.get("node")
		if wrapper == null or not is_instance_valid(wrapper):
			continue
		if not wrapper.has_meta("kind"):
			continue
		if wrapper.get_meta("kind") != "portrait3d":
			continue
		if not wrapper.has_meta("portrait3d"):
			continue
		var p3d: Node = wrapper.get_meta("portrait3d")
		if p3d == null or not is_instance_valid(p3d):
			continue
		var glb_path: String = ""
		if "_loaded_glb_path" in p3d:
			glb_path = p3d._loaded_glb_path
		out.append({
			"pos": pos,
			"name": slot["name"],
			"expr": slot.get("expr", ""),
			"portrait3d": p3d,
			"glb_path": glb_path,
		})
	return out


func activate_speaker(char_name: String) -> void:
	# Empty char_name (called from narrate) → nobody is the active
	# speaker, so all portraits recede to the inactive state. This
	# lets the camera pull back during third-person narration instead
	# of leaving the last speaker on the screen as "main".
	var key := char_key(char_name)
	# Find which slot the active speaker occupies so a centre portrait
	# can turn to face them (left/right slots keep their fixed inward
	# facing, set at show time).
	var active_pos: String = ""
	if key != "":
		for pos: String in _slots:
			var slot = _slots[pos]
			if slot != null and char_key(str(slot["name"])) == key:
				active_pos = pos
				break
	_reface_center(active_pos)
	for pos: String in _slots:
		var slot = _slots[pos]
		if slot == null:
			continue
		# Skip portraits that are currently fading out — their fade
		# tween writes modulate:a, and overlaying a modulate (rgba)
		# tween here resurrects them visibly before queue_free fires,
		# producing ghost portraits in the next scene.
		var node: Control = slot["node"]
		if node.has_meta("fading"):
			continue
		var is_active: bool   = (key != "" and char_key(str(slot["name"])) == key)
		# Active: full color, +5% scale, full alpha
		# Inactive: deeper desat (cool gray), -8% scale, ~30% alpha — recedes
		# noticeably so the active speaker reads as "the camera is on them"
		var target_mod: Color
		var target_scale: float
		if is_active:
			target_mod   = Color(1.0, 1.0, 1.0, ACTIVE_ALPHA)
			target_scale = ACTIVE_SCALE
		else:
			target_mod   = Color(0.48, 0.50, 0.55, INACTIVE_ALPHA)
			target_scale = INACTIVE_SCALE
		node.pivot_offset = Vector2(SPRITE_W * 0.5, SPRITE_H * 0.5)
		# Target figure_holder (not the wrapper) so the dimming only
		# affects the figure — the static backdrop and scrim behind it
		# stay at full strength, giving the inactive speaker a solid
		# visual ground instead of bleeding through to the scene bg.
		var target: Node = node.get_meta("figure_holder") if node.has_meta("figure_holder") else node
		var tw := node.create_tween()
		tw.set_parallel(true)
		tw.tween_property(target, "modulate", target_mod, 0.25)
		tw.tween_property(node, "scale", Vector2(target_scale, target_scale), 0.25)


# A centre portrait turns to face whoever is speaking: speaker on the
# left → centre faces left; speaker on the right → centre faces right;
# speaker IS the centre, or narration (no speaker) → centre faces
# forward. Left/right slots keep the fixed inward facing set at show
# time. Reuses _compute_flip so the natural-orientation + CHAR_FACING
# rules stay consistent with the scene-JSON `facing` path. The flip is
# read every frame in _process via the "flip_x" meta, so just updating
# the meta re-orients the figure next frame.
func _reface_center(active_pos: String) -> void:
	var center = _slots.get("center")
	if center == null:
		return
	var node: Control = center["node"]
	if not is_instance_valid(node) or node.has_meta("fading"):
		return
	var desired: String
	match active_pos:
		"left":  desired = "left"
		"right": desired = "right"
		_:       desired = "forward"
	var flip: bool = _compute_flip(char_key(str(center["name"])), "center", desired)
	node.set_meta("flip_x", -1.0 if flip else 1.0)


func get_pos_for_char(char_name: String) -> String:
	var key := char_key(char_name)
	for pos: String in _slots:
		var slot = _slots[pos]
		if slot != null and slot["name"] == key:
			return pos
	return "center"


# ── Portrait construction ─────────────────────────────────────────────────────

# Fuzzy-static backdrop — dark warm noise that sits behind every
# portrait so the scene bg doesn't bleed through when the figure's
# alpha drops (inactive speaker, fading out, etc.). 64×64 tile of
# per-pixel random luminance in the 0.06-0.22 range with a slight
# warm tint, tiled across the slot. The tile is fixed once at
# instantiation — no per-frame work.
const _STATIC_TILE_SIZE: int = 64
const _STATIC_LUM_MIN: float = 0.06
const _STATIC_LUM_MAX: float = 0.22
const _STATIC_WARM_TINT: Color = Color(1.08, 0.96, 0.84)

func _make_static_backdrop() -> TextureRect:
	return _make_backdrop("static")


# Per-portrait backdrop registry — Debug overlay swaps via
# set_portrait_backdrop(char_key, kind). Each branch returns a
# TextureRect anchored to the wrapper's full rect so it sits
# BEHIND the figure_holder.
func _make_backdrop(kind: String) -> TextureRect:
	var tr := TextureRect.new()
	tr.stretch_mode  = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	tr.expand_mode   = TextureRect.EXPAND_IGNORE_SIZE
	tr.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	tr.mouse_filter  = Control.MOUSE_FILTER_IGNORE
	var size: int = _STATIC_TILE_SIZE
	var img: Image = Image.create(size, size, false, Image.FORMAT_RGBA8)
	match kind:
		"void":
			img.fill(Color(0.02, 0.02, 0.03, 1.0))
		"warm_glow":
			# Radial warm sodium falloff
			for y in size:
				for x in size:
					var dx: float = (float(x) / size - 0.5) * 2.0
					var dy: float = (float(y) / size - 0.5) * 2.0
					var r: float = clamp(1.0 - sqrt(dx*dx + dy*dy), 0.0, 1.0)
					img.set_pixel(x, y, Color(
						0.10 + r * 0.85, 0.06 + r * 0.55, 0.04 + r * 0.20, 1.0))
		"cool_blue":
			for y in size:
				for x in size:
					var dx2: float = (float(x) / size - 0.5) * 2.0
					var dy2: float = (float(y) / size - 0.5) * 2.0
					var r2: float = clamp(1.0 - sqrt(dx2*dx2 + dy2*dy2), 0.0, 1.0)
					img.set_pixel(x, y, Color(
						0.05 + r2 * 0.18, 0.08 + r2 * 0.32, 0.18 + r2 * 0.62, 1.0))
		"crt_scanlines":
			# Dark with horizontal alternating bands — reads as a CRT
			for y in size:
				var band: float = 0.06 if (y % 2 == 0) else 0.14
				for x in size:
					var jitter: float = (randf() - 0.5) * 0.04
					img.set_pixel(x, y, Color(
						band + jitter * 0.4,
						band + jitter * 0.6,
						band + jitter * 0.2,
						1.0))
		"gradient_sunset":
			for y in size:
				var t: float = float(y) / float(size - 1)
				var rr: float = lerp(0.62, 0.18, t)
				var gg: float = lerp(0.32, 0.14, t)
				var bb: float = lerp(0.20, 0.30, t)
				for x in size:
					img.set_pixel(x, y, Color(rr, gg, bb, 1.0))
		"neon_grid":
			img.fill(Color(0.04, 0.04, 0.06, 1.0))
			# Draw faint magenta + cyan grid lines every 8 px
			for i in range(0, size, 8):
				for j in size:
					img.set_pixel(i, j, Color(0.62, 0.20, 0.74, 1.0))
					img.set_pixel(j, i, Color(0.20, 0.62, 0.74, 1.0))
		_: # "static" — the original fuzzy-warm noise (default)
			var span: float = _STATIC_LUM_MAX - _STATIC_LUM_MIN
			for y in size:
				for x in size:
					var n: float = _STATIC_LUM_MIN + randf() * span
					img.set_pixel(x, y, Color(
						n * _STATIC_WARM_TINT.r,
						n * _STATIC_WARM_TINT.g,
						n * _STATIC_WARM_TINT.b,
						1.0))
			tr.stretch_mode = TextureRect.STRETCH_TILE
	tr.texture = ImageTexture.create_from_image(img)
	return tr


# Swap THIS portrait's backdrop in place. Walks the wrapper for the
# matching slot and replaces the first TextureRect child (the backdrop
# is added BEFORE figure_holder in show_character).
func set_portrait_backdrop(char_name: String, kind: String) -> void:
	var key := char_key(char_name)
	for pos: String in _slots:
		var slot = _slots[pos]
		if slot == null or slot.get("name") != key:
			continue
		var wrapper: Node = slot.get("node")
		if wrapper == null or not is_instance_valid(wrapper):
			continue
		# Find existing backdrop (first TextureRect child without
		# the "figure" or "tint" meta).
		for child in wrapper.get_children():
			if child is TextureRect and not child.has_meta("frame"):
				child.queue_free()
				break
		var new_bd := _make_backdrop(kind)
		wrapper.add_child(new_bd)
		wrapper.move_child(new_bd, 0)
		print("[CharLayer] backdrop %s → %s" % [key, kind])
		return


# Debug overlay: small monospace label at the bottom of the portrait
# wrapper showing the resolved asset path. Lives above ALL other slot
# children (including the ASCII border) so it stays readable while
# debugging. Disabled by setting DEBUG_ASSET_OVERLAY=false at top.
func _add_asset_overlay(wrapper: Control, path: String) -> void:
	# Shorten the path — strip res:// and the long common prefix
	# so the label fits in the 300-wide slot.
	var short := path
	short = short.replace("res://assets/", "")
	short = short.replace("res://resources/substrates/compositions/", "comp/")
	# Bg backing so the text is legible over any portrait color.
	var bg := ColorRect.new()
	bg.color = Color(0.0, 0.0, 0.0, 0.72)
	bg.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	bg.offset_top = -18.0
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	bg.z_index = 200   # above border + figure
	wrapper.add_child(bg)
	var lbl := Label.new()
	lbl.text = short
	lbl.add_theme_font_size_override("font_size", 12)
	lbl.add_theme_color_override("font_color", Color(0.95, 0.85, 0.55))
	lbl.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.9))
	lbl.add_theme_constant_override("outline_size", 2)
	lbl.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	lbl.offset_top = -16.0
	lbl.offset_left = 4.0
	lbl.offset_right = -4.0
	lbl.clip_text = true
	lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
	lbl.z_index = 201
	wrapper.add_child(lbl)


func _make_portrait(char_name: String, expr: String, pos: String) -> Control:
	var wrapper := Control.new()
	wrapper.clip_contents        = true
	wrapper.custom_minimum_size  = Vector2(SPRITE_W, SPRITE_H)
	wrapper.size                 = Vector2(SPRITE_W, SPRITE_H)
	wrapper.position             = POSITIONS[pos]
	wrapper.modulate.a           = 0.0

	var key       := char_key(char_name)
	var comp_path := PORTRAIT_COMP_ROOT + "portrait_" + key + ".json"
	# Clean face crop is the canonical "portrait slot" image. When it
	# exists we use it directly — face + torso, no card chrome around
	# the figure. Composition with full card art is a fallback for
	# characters that don't have a face crop yet.
	var face_png  := "%s%s_face.png" % [PORTRAIT_GALLERY_ROOT, key]
	var has_face  := FileAccess.file_exists(face_png) or ResourceLoader.exists(face_png)

	# Fuzzy-static backdrop — opaque dark warm noise (default). The
	# debug overlay can stamp a different backdrop kind into
	# VnDebugState.portrait_state — honour that here so the override
	# survives portrait respawn (advance / rewind doesn't reset it).
	# Lives BEHIND everything else in the slot so when the figure
	# dims (inactive speaker, alpha 0.55) the scene bg doesn't bleed
	# through. Lives outside `figure_holder` so activate_speaker's
	# modulate doesn't also dim the backdrop.
	var saved_backdrop_kind: String = ""
	var debug_state := get_node_or_null("/root/VnDebugState")
	if debug_state != null and debug_state.has_method("get_portrait_backdrop"):
		saved_backdrop_kind = String(debug_state.get_portrait_backdrop(key))
	# CUTOUT_MODE: skip the opaque backdrop + scrim so the figure is a
	# clean cutout over the scene. A debug-stamped backdrop still wins.
	if not CUTOUT_MODE or saved_backdrop_kind != "":
		if saved_backdrop_kind == "":
			wrapper.add_child(_make_static_backdrop())
		else:
			wrapper.add_child(_make_backdrop(saved_backdrop_kind))
		var scrim := ColorRect.new()
		scrim.color = SCRIM_COLOR
		scrim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		scrim.mouse_filter = Control.MOUSE_FILTER_IGNORE
		wrapper.add_child(scrim)

	# figure_holder is the layer activate_speaker modulates. Splitting
	# it from wrapper means the static backdrop stays full-strength
	# even when the figure recedes — visual ground for the dimmed
	# silhouette instead of bg bleed-through.
	var figure_holder := Control.new()
	figure_holder.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	figure_holder.mouse_filter = Control.MOUSE_FILTER_IGNORE
	wrapper.add_child(figure_holder)
	wrapper.set_meta("figure_holder", figure_holder)

	# tint_holder isolates expression tint from figure_holder.modulate
	# (which activate_speaker writes). They compose multiplicatively.
	# clip_contents so manually-positioned textures (face-zoom layout)
	# don't bleed outside the slot bounds.
	var tint_holder := Control.new()
	tint_holder.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	tint_holder.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tint_holder.clip_contents = true
	figure_holder.add_child(tint_holder)
	wrapper.set_meta("tint", tint_holder)

	var resolved_path := ""
	# ── PRIORITY 1: 3D GLB model (Portrait3D SubViewport) ──
	# When the character has a textured hero GLB, render it in 3D.
	# The viewport returns a Texture2D that we layout exactly like
	# any other portrait texture — drop-in compatible with the
	# expression-tint + face-bias-crop machinery below.
	var glb_path: String = _resolve_portrait_3d_glb(key)
	if glb_path != "":
		var is_demon: bool = _is_demon_glb(glb_path)
		print("[CharLayer] %s (key=%s): 3D PORTRAIT  %s%s" %
			[char_name, key, glb_path, "  [DEMON]" if is_demon else ""])
		var p3d: SubViewportContainer = PORTRAIT_3D_SCENE.instantiate()
		p3d.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		p3d.mouse_filter = Control.MOUSE_FILTER_IGNORE
		tint_holder.add_child(p3d)
		# Defer the load so the SubViewport is in-tree first. For
		# demons, also flip the digital-static shader on AFTER the
		# load (the static lays on TOP of the rendered figure).
		p3d.call_deferred("load_character", glb_path, expr)
		if is_demon:
			p3d.call_deferred("set_demon_mode", true)
		# Restore any user-stamped debug overrides for THIS char from
		# VnDebugState. Queued AFTER load_character so the material,
		# light nodes, and camera all exist before we write to them.
		# Godot's deferred queue preserves call order within a frame.
		var dbg := get_node_or_null("/root/VnDebugState")
		if dbg != null and dbg.has_method("apply_portrait_state"):
			dbg.call_deferred("apply_portrait_state", key, p3d)
		wrapper.set_meta("kind", "portrait3d")
		wrapper.set_meta("portrait3d", p3d)
		# Subtle expression tint compositions on top of the 3D
		# render — same EXPR_TINTS table the PNG path uses
		_apply_texture_tint(wrapper, expr)
		resolved_path = glb_path
	elif not has_face and FileAccess.file_exists(comp_path):
		print("[CharLayer] %s (key=%s): COMPOSITION  %s" % [char_name, key, comp_path])
		var comp := Control.new()
		comp.set_script(ASCII_COMPOSITION_SCRIPT)
		comp.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		comp.mouse_filter = Control.MOUSE_FILTER_IGNORE
		tint_holder.add_child(comp)
		comp.call_deferred("load_composition", "portrait_" + key)
		wrapper.set_meta("kind", "composition")
		_apply_texture_tint(wrapper, expr)
		resolved_path = comp_path
	else:
		var resolved := _resolve_portrait_texture_verbose(key, expr)
		var tex: Texture2D = resolved["texture"]
		var path: String   = resolved["path"]
		if tex != null:
			print("[CharLayer] %s (key=%s): TEXTURE      %s  [%dx%d]" %
				[char_name, key, path, int(tex.get_size().x), int(tex.get_size().y)])
			var tr := TextureRect.new()
			tr.texture       = tex
			tr.mouse_filter  = Control.MOUSE_FILTER_IGNORE
			tint_holder.add_child(tr)
			# Manually compute scale + position to fill the slot with
			# the source — always COVER (no letterbox), with a face-bias
			# vertical alignment so tall full-body images show head +
			# torso instead of cropping the head off. See
			# _layout_portrait_texture for the math.
			_layout_portrait_texture(tr, tex)
			wrapper.set_meta("kind", "texture")
			if not _has_expr_png(key, expr):
				_apply_texture_tint(wrapper, expr)
			resolved_path = path
		else:
			# Nothing matched — log the full tried-list ONCE per key per
			# session (the list is ~40 lines; repeating it every time the
			# same asset-less character re-enters buried real errors in
			# the playtest log). Later appearances get the one-liner.
			print("[CharLayer] %s (key=%s): PLACEHOLDER  no asset found" % [char_name, key])
			if not _placeholder_logged.has(key):
				_placeholder_logged[key] = true
				for tried in resolved["tried"]:
					print("    tried: %s" % tried)
			tint_holder.queue_free()
			wrapper.remove_meta("tint")
			var bust_ph := _make_placeholder(char_name, expr)
			wrapper.add_child(bust_ph)
			wrapper.set_meta("bust_ph", bust_ph)
			wrapper.set_meta("kind", "placeholder")
			resolved_path = "PLACEHOLDER (procedural bust)"

	# Asset-path overlay — a small label at the bottom of the slot
	# showing the file path the engine loaded. Sits ABOVE everything
	# else so it stays visible while debugging asset assignments.
	# Toggle via DEBUG_ASSET_OVERLAY (top of file) once you're done.
	if DEBUG_ASSET_OVERLAY:
		_add_asset_overlay(wrapper, resolved_path)

	# ── ASCII frame around the portrait — skipped in CUTOUT_MODE
	# (the modern-VN look has no box/border around the figure).
	if not CUTOUT_MODE:
		_make_border(wrapper, char_name)

	# Tag the wrapper with pos + char so the ghost spawner on
	# dismiss can place + tint the silhouette correctly.
	wrapper.set_meta("pos", pos)
	wrapper.set_meta("char", char_name)

	add_child(wrapper)
	var tw := wrapper.create_tween()
	tw.tween_property(wrapper, "modulate:a", 1.0, 0.3)
	return wrapper


func _update_expr(wrapper: Control, char_name: String, expr: String) -> void:
	var kind: String = wrapper.get_meta("kind") if wrapper.has_meta("kind") else "placeholder"
	var key  := char_key(char_name)
	if kind == "portrait3d":
		# Forward the new expression to Portrait3D — the mood table
		# inside Portrait3D.gd drives the camera + lighting + motion
		# response. We still layer the subtle EXPR_TINTS modulate on
		# top of the 3D render so colour reads stay consistent with
		# the PNG path.
		var p3d: SubViewportContainer = null
		if wrapper.has_meta("portrait3d"):
			p3d = wrapper.get_meta("portrait3d") as SubViewportContainer
		if p3d != null and p3d.has_method("set_expression"):
			p3d.set_expression(expr)
		_apply_texture_tint(wrapper, expr)
	elif kind == "composition":
		_apply_texture_tint(wrapper, expr)
	elif kind == "texture":
		var tint_holder: Control = (wrapper.get_meta("tint") if wrapper.has_meta("tint") else null) as Control
		if tint_holder != null:
			var tr := tint_holder.get_child(0) as TextureRect
			var new_tex := _resolve_portrait_texture(key, expr)
			if new_tex != null and tr != null:
				tr.texture = new_tex
				# Relayout — new texture may be a different aspect.
				_layout_portrait_texture(tr, new_tex)
		if _has_expr_png(key, expr):
			if tint_holder != null:
				tint_holder.modulate = Color.WHITE
		else:
			_apply_texture_tint(wrapper, expr)
	else:
		# Procedural bust — swap in the face for the new expression.
		# (The old code read wrapper.get_child(0), which is the static
		# backdrop, so placeholder expressions silently never updated.)
		if wrapper.has_meta("bust_ph"):
			var ph: Control = wrapper.get_meta("bust_ph") as Control
			if ph != null and is_instance_valid(ph) and ph.has_meta("bust_tex"):
				var btr: TextureRect = ph.get_meta("bust_tex") as TextureRect
				var bcol: Color = ph.get_meta("bust_col") if ph.has_meta("bust_col") else _char_color(char_name)
				btr.texture = BUST_PORTRAIT.texture(key, expr, bcol)


const PORTRAIT_GALLERY_ROOT := "res://assets/gallery/"


# Texture lookup chain — every plausible path the user might have
# placed art at, in preference order. Diagnostic mode is on (verbose
# resolver below) so the Godot console shows exactly which path was
# chosen per character — if a char shows up as PLACEHOLDER, the
# console lists every path that was tried so you know what to name
# the asset.
#
# Order, most-canonical first:
#   1.  gallery/<char>_face.png            ← face+torso crop, ideal slot
#   2.  gallery/portrait_<char>_face.png   ← card-style face frame
#   3.  gallery/portrait_<char>_0.png      ← first animation frame
#   4.  gallery/<char>.png                 ← gallery card (canonical)
#   5.  gallery/<char>.jpg                 ← gallery card jpg variant
#   6.  gallery/<char>_portrait.png        ← alternative naming
#   7.  gallery/<char>_clean.png           ← already-used "clean" suffix
#   8.  gallery/<char>_neutral.png         ← matches scene expr default
#   9.  characters/<char>/<char>_<expr>.png ← old per-expression
#  10.  characters/<char>/<char>_neutral.png ← old neutral
#  11.  characters/<char>.png              ← flat alternative
#  12.  portraits/<char>.png               ← if you keep a separate dir
#
# Stretch logic moved into _layout_portrait_texture below — always
# COVER (no letterbox), top-biased vertically so tall body shots show
# head + torso instead of cropping the face off.
func _resolve_portrait_texture_verbose(key: String, expr: String) -> Dictionary:
	var tried: Array[String] = [
		"%s%s_face.png" % [PORTRAIT_GALLERY_ROOT, key],
		"%sportrait_%s_face.png" % [PORTRAIT_GALLERY_ROOT, key],
		"%sportrait_%s_0.png" % [PORTRAIT_GALLERY_ROOT, key],
		"%s%s.png" % [PORTRAIT_GALLERY_ROOT, key],
		"%s%s.jpg" % [PORTRAIT_GALLERY_ROOT, key],
		"%s%s_portrait.png" % [PORTRAIT_GALLERY_ROOT, key],
		"%s%s_clean.png" % [PORTRAIT_GALLERY_ROOT, key],
		"%s%s_neutral.png" % [PORTRAIT_GALLERY_ROOT, key],
		"%s%s/%s_%s.png" % [PORTRAIT_TEX_ROOT, key, key, expr],
		"%s%s/%s_neutral.png" % [PORTRAIT_TEX_ROOT, key, key],
		"%s%s/%s_happy.png" % [PORTRAIT_TEX_ROOT, key, key],
		"%s%s/%s_serious.png" % [PORTRAIT_TEX_ROOT, key, key],
		"%s%s/%s_tired.png" % [PORTRAIT_TEX_ROOT, key, key],
		"%s%s/%s_sad.png" % [PORTRAIT_TEX_ROOT, key, key],
		"%s%s/%s_surprised.png" % [PORTRAIT_TEX_ROOT, key, key],
		"%s%s.png" % [PORTRAIT_TEX_ROOT, key],
		"res://assets/portraits/%s.png" % [key],
	]
	# bulk_intake puts disambiguation per-volume subdirs:
	# assets/characters/vol5/<char>/<char>_<expr>.png etc. The engine
	# doesn't know the current scene's vol, so try all of them.
	for v in [5, 6, 7, 1, 2]:
		tried.append("%svol%d/%s/%s_%s.png" % [PORTRAIT_TEX_ROOT, v, key, key, expr])
		tried.append("%svol%d/%s/%s_neutral.png" % [PORTRAIT_TEX_ROOT, v, key, key])
		tried.append("%svol%d/%s/%s_happy.png" % [PORTRAIT_TEX_ROOT, v, key, key])
		tried.append("%svol%d/%s/%s_serious.png" % [PORTRAIT_TEX_ROOT, v, key, key])
		tried.append("%svol%d/%s/%s.png" % [PORTRAIT_TEX_ROOT, v, key, key])
	for path: String in tried:
		var t := _load_texture_with_fallback(path)
		if t != null:
			return {"texture": t, "path": path, "tried": tried}
	# Fuzzy fallback — scan gallery/ for any file whose stem contains the
	# key (case-insensitive). Catches naming variants like
	# johnfrank_face.png when key=john, sam_miller_neutral.png when
	# key=sam_miller, etc.
	var fuzzy := _find_in_gallery_index(key)
	if fuzzy["texture"] != null:
		tried.append(fuzzy["path"] + "  (fuzzy)")
		return {"texture": fuzzy["texture"], "path": fuzzy["path"], "tried": tried}
	return {"texture": null, "path": "", "tried": tried}


# Lazy-built case-insensitive index of every PNG/JPG in assets/gallery/.
# Used by the fuzzy fallback in _resolve_portrait_texture_verbose. Keyed
# by lowercase filename stem; value is the full res:// path.
static var _gallery_index: Dictionary = {}
static var _gallery_index_built: bool = false

func _build_gallery_index() -> void:
	if _gallery_index_built:
		return
	_gallery_index_built = true
	# Scan gallery/ flat, then characters/ recursively up to 2 levels
	# deep (catches characters/<char>/ AND characters/vol<N>/<char>/).
	_scan_dir_for_index(PORTRAIT_GALLERY_ROOT, 0, 1)
	_scan_dir_for_index(PORTRAIT_TEX_ROOT, 0, 2)
	print("[CharLayer] asset index built · %d entries" % _gallery_index.size())


func _scan_dir_for_index(path: String, depth: int, max_depth: int) -> void:
	var dir := DirAccess.open(path)
	if dir == null:
		return
	dir.list_dir_begin()
	var fn := dir.get_next()
	while fn != "":
		var full := path + fn
		if dir.current_is_dir():
			if depth < max_depth and fn != "." and fn != "..":
				_scan_dir_for_index(full + "/", depth + 1, max_depth)
		else:
			var lower := fn.to_lower()
			if lower.ends_with(".png") or lower.ends_with(".jpg") or lower.ends_with(".jpeg"):
				var stem := lower.get_basename()
				# Don't overwrite earlier hits — first match (gallery) wins.
				if not _gallery_index.has(stem):
					_gallery_index[stem] = full
		fn = dir.get_next()


func _find_in_gallery_index(key: String) -> Dictionary:
	_build_gallery_index()
	var k := key.to_lower()
	# Prefer canonical suffixes if any stem matches them exactly.
	var preferred := [k + "_face", k + "_portrait", k + "_clean",
					k, "portrait_" + k + "_face", "portrait_" + k + "_0",
					"portrait_" + k, k + "_neutral"]
	for stem: String in preferred:
		if stem in _gallery_index:
			var path: String = _gallery_index[stem]
			var t := _load_texture_with_fallback(path)
			if t != null:
				return {"texture": t, "path": path}
	# Substring fallback — any filename whose stem CONTAINS the key.
	# Sorted by stem length asc so the closest match wins (e.g.
	# "john" matches "johnfrank" before "johnfrank_face_cutout").
	var candidates: Array = []
	for stem in _gallery_index:
		if k in stem:
			candidates.append(stem)
	candidates.sort_custom(func(a, b): return a.length() < b.length())
	for stem: String in candidates:
		var path: String = _gallery_index[stem]
		var t := _load_texture_with_fallback(path)
		if t != null:
			return {"texture": t, "path": path}
	return {"texture": null, "path": ""}


# Back-compat: callers (update_expr) still use the old resolver name.
func _resolve_portrait_texture(key: String, expr: String) -> Texture2D:
	return _resolve_portrait_texture_verbose(key, expr)["texture"]


# Manual layout that always fills the slot. Compute scale to COVER
# the slot, then position with horizontal-center, vertical-top-bias.
# Wrapper has clip_contents so anything outside the slot bounds is
# cropped away. Net behavior:
#   · square face crops (~slot aspect) → fills tight, centered
#   · square card portraits → fills tight, centered
#   · landscape gallery cards → fills width, top-biased so head shows
#   · tall full-body images  → fills height, head shows (legs crop)
# No letterbox bars. No tiny figures floating in empty slots.
const _SLOT_ASPECT: float       = SPRITE_W / SPRITE_H
const _TOP_BIAS_RATIO: float    = 0.85   # if src_aspect / slot_aspect < this, top-align
# Face-zoom past pure cover for near-slot / landscape sources. Pulls
# in 15% past cover so the face dominates the slot instead of sitting
# at the slot's natural framing distance. (Tall sources skip this —
# they're already filling the height; further zoom would crop the head.)
const _FACE_ZOOM: float         = 1.15
# Vertical bias for near-slot / landscape sources. Subtracted from the
# centered y_off, which shifts the visible content up — the face area
# of the source lands in the upper third of the slot instead of the
# middle. 0.08 = 8% of slot height of upward shift.
const _FACE_Y_BIAS: float       = 0.08

func _layout_portrait_texture(tr: TextureRect, tex: Texture2D) -> void:
	var sz := tex.get_size()
	if sz.x <= 0.0 or sz.y <= 0.0:
		# Defensive — fall back to full-rect cover.
		tr.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
		tr.expand_mode  = TextureRect.EXPAND_IGNORE_SIZE
		return
	var src_aspect: float = sz.x / sz.y
	var ratio: float = src_aspect / _SLOT_ASPECT
	# Scale: for tall sources, pure COVER (filling slot is enough; further
	# zoom would crop the face). For near-slot / landscape sources, apply
	# _FACE_ZOOM past cover so the face dominates instead of floating at
	# the source's natural framing distance.
	var cover_s: float = maxf(SPRITE_W / sz.x, SPRITE_H / sz.y)
	var s: float = cover_s if ratio < _TOP_BIAS_RATIO else cover_s * _FACE_ZOOM
	var disp_w: float = sz.x * s
	var disp_h: float = sz.y * s
	# Horizontal: center (figures usually centered in their crops).
	var x_off: float = (SPRITE_W - disp_w) * 0.5
	# Vertical: for tall sources, top-align (head already at the top of
	# the source). For near-slot / landscape, center then bias UPWARD by
	# _FACE_Y_BIAS — the face area lands in the upper third of the slot.
	var y_off: float
	if ratio < _TOP_BIAS_RATIO:
		y_off = 0.0
	else:
		y_off = (SPRITE_H - disp_h) * 0.5 - SPRITE_H * _FACE_Y_BIAS
	tr.expand_mode  = TextureRect.EXPAND_IGNORE_SIZE
	tr.stretch_mode = TextureRect.STRETCH_SCALE
	tr.size = Vector2(disp_w, disp_h)
	tr.position = Vector2(x_off, y_off)


func _load_texture_with_fallback(path: String) -> Texture2D:
	if ResourceLoader.exists(path):
		return ResourceLoader.load(path) as Texture2D
	var img := Image.load_from_file(ProjectSettings.globalize_path(path))
	if img:
		return ImageTexture.create_from_image(img)
	return null


func _has_expr_png(key: String, expr: String) -> bool:
	var path := "%s%s/%s_%s.png" % [PORTRAIT_TEX_ROOT, key, key, expr]
	if ResourceLoader.exists(path):
		return true
	return FileAccess.file_exists(path)


func _apply_texture_tint(wrapper: Control, expr: String) -> void:
	# Writes to the tint_holder child, not wrapper.modulate — leaves the
	# wrapper free for fade-in (alpha) and activate_speaker (rgb dim).
	if not wrapper.has_meta("tint"):
		return
	var tint_holder: Control = wrapper.get_meta("tint") as Control
	if tint_holder == null:
		return
	tint_holder.modulate = EXPR_TINTS.get(expr, EXPR_TINTS["neutral"])


func _fade_out_free(node: Control) -> void:
	# Mark the node as fading so activate_speaker (which writes the
	# full modulate Color) doesn't race the alpha-only fade we're
	# starting here. Without this, narration after a hide can
	# resurrect the dimmed-but-visible portrait into the next scene.
	node.set_meta("fading", true)
	node.mouse_filter = Control.MOUSE_FILTER_IGNORE
	# Spawn an ASCII silhouette ghost at the dismiss position before
	# the live portrait fades out. The ghost lingers on the scene as
	# a faded after-image of the character.
	_spawn_ghost(node)
	var tw := node.create_tween()
	tw.tween_property(node, "modulate:a", 0.0, 0.35)
	tw.tween_callback(node.queue_free)


# ── ASCII border ──────────────────────────────────────────────────────
# Tall thin Control that draws a 1-char-wide frame around the portrait
# using box-drawing glyphs in the character's accent color. Re-renders
# each frame via _process triggering queue_redraw, so it tracks the
# breath scale + parallax sway.
class _AsciiBorder extends Control:
	var accent: Color = Color.WHITE
	var char_name: String = ""
	var t: float = 0.0
	func _process(d: float) -> void:
		t += d
	func _draw() -> void:
		var s := size
		if s.x < 8 or s.y < 8: return
		var font := ThemeDB.fallback_font
		var fpx := 14
		var cell_x := 7
		var cell_y := 16
		var cols := int(s.x / cell_x)
		var rows := int(s.y / cell_y)
		if cols < 4 or rows < 4: return
		# Corners + edges
		var c_bright := Color(accent.r * 1.0, accent.g * 1.0,
							accent.b * 1.0, 0.85)
		var c_dim := Color(accent.r * 0.55, accent.g * 0.55,
						accent.b * 0.55, 0.65)
		# Pulse — corners brighten in a wave
		var pulse: float = (sin(t * 1.4) + 1.0) * 0.5
		var c_pulse := c_bright.lerp(c_dim, pulse)
		var corners := [
			Vector2(0, 0),                       # top-left
			Vector2((cols - 1) * cell_x, 0),     # top-right
			Vector2(0, (rows - 1) * cell_y),     # bot-left
			Vector2((cols - 1) * cell_x,
				(rows - 1) * cell_y),          # bot-right
		]
		var corner_glyphs := ["╔", "╗", "╚", "╝"]
		for i in 4:
			draw_string(font, corners[i] + Vector2(0, cell_y - 2),
						corner_glyphs[i],
						HORIZONTAL_ALIGNMENT_LEFT, -1, fpx, c_pulse)
		# Top + bottom edges
		for c in range(1, cols - 1):
			var x = c * cell_x
			var glyph := "═"
			if c == cols / 2:
				glyph = "╦"   # subtle middle tee
			draw_string(font, Vector2(x, cell_y - 2), glyph,
						HORIZONTAL_ALIGNMENT_LEFT, -1, fpx, c_dim)
			var glyph2 := "═"
			if c == cols / 2:
				glyph2 = "╩"
			draw_string(font, Vector2(x, (rows - 1) * cell_y + cell_y - 2),
						glyph2, HORIZONTAL_ALIGNMENT_LEFT, -1, fpx, c_dim)
		# Left + right edges
		for r in range(1, rows - 1):
			var y = r * cell_y
			draw_string(font, Vector2(0, y + cell_y - 2), "║",
						HORIZONTAL_ALIGNMENT_LEFT, -1, fpx, c_dim)
			draw_string(font, Vector2((cols - 1) * cell_x, y + cell_y - 2),
						"║", HORIZONTAL_ALIGNMENT_LEFT, -1, fpx, c_dim)
		# Speaker name on the portrait used to duplicate the dialogue
		# box's name label; removed so the portrait reads as a clean
		# framed figure without text competing for attention.


func _make_border(wrapper: Control, char_name: String) -> Control:
	var b := _AsciiBorder.new()
	b.accent = accent_for(char_name)
	b.char_name = char_name
	b.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	b.mouse_filter = Control.MOUSE_FILTER_IGNORE
	# NO z_index: the border is the wrapper's last child, which
	# already draws it above the portrait texture. A relative
	# z_index here stacks on CharLayer's UI_Z and floats the frame
	# over the in-game menu / interludes / choices (all at UI_Z).
	wrapper.add_child(b)
	wrapper.set_meta("border", b)
	return b


# ── ASCII silhouette ghost on dismiss ──────────────────────────────
# When a portrait fades out, we spawn a Control containing a Label
# of ASCII-block characters in the shape of a generic figure, at low
# alpha, in the character's accent color. The ghost lingers on the
# scene until cleared by hide_all (scene end / chapter change).
const _GHOST_ASCII := """    ▄▄▄▄▄
   ▐█████▌
   ▐██▀██▌
	▐████▌
   ▐██████▌
  ▐████████▌
   ▐██████▌
	██████
	██▌▐██
	██▌▐██
"""

var _ghosts: Array = []

func _spawn_ghost(node: Control) -> void:
	var pos: String = node.get_meta("pos") if node.has_meta("pos") else "center"
	var char_name: String = node.get_meta("char") if node.has_meta("char") else ""
	var ghost := Label.new()
	ghost.text = _GHOST_ASCII
	ghost.add_theme_font_size_override("font_size", 14)
	ghost.modulate = Color(0.0, 0.0, 0.0, 0.0)
	var accent := accent_for(char_name)
	ghost.add_theme_color_override("font_color",
		Color(accent.r, accent.g, accent.b, 1.0))
	ghost.position = POSITIONS.get(pos, Vector2(490, 80)) + Vector2(40, 30)
	ghost.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(ghost)
	# fade IN as the live portrait fades OUT — they cross-fade
	var tw_g: Tween = ghost.create_tween()
	tw_g.tween_property(ghost, "modulate:a", 0.30, 0.40)
	# subtle slow drift upward
	tw_g.parallel().tween_property(ghost, "position:y",
		ghost.position.y - 8, 1.2)
	_ghosts.append(ghost)


func _clear_ghosts() -> void:
	for g in _ghosts:
		if is_instance_valid(g):
			var tw_c: Tween = g.create_tween()
			tw_c.tween_property(g, "modulate:a", 0.0, 0.30)
			tw_c.tween_callback(g.queue_free)
	_ghosts.clear()


# ── Placeholder portrait ──────────────────────────────────────────────────────

func _make_placeholder(char_name: String, expr: String) -> Control:
	# Procedural pixel bust (VnBustPortrait) — deterministic from the
	# character key, expression-aware, dressed in the accent color.
	# Replaces the old oval-and-rectangle silhouette with a face.
	var key := char_key(char_name)
	var col := accent_for(char_name) if CHAR_ACCENTS.has(key) else _char_color(char_name)
	var ph  := Control.new()
	ph.custom_minimum_size = Vector2(SPRITE_W, SPRITE_H)

	var tr := TextureRect.new()
	tr.texture = BUST_PORTRAIT.texture(key, expr, col)
	tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	tr.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	tr.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	tr.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ph.add_child(tr)
	ph.set_meta("bust_tex", tr)
	ph.set_meta("bust_col", col)

	# Name plate — kept, since a procedural face still needs naming
	# the first time a character appears.
	var name_lbl := Label.new()
	name_lbl.text                = char_name.capitalize()
	name_lbl.position            = Vector2(0.0, SPRITE_H - 34.0)
	name_lbl.size                = Vector2(SPRITE_W, 26.0)
	name_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	name_lbl.add_theme_color_override("font_color", col)
	name_lbl.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.9))
	name_lbl.add_theme_constant_override("shadow_offset_x", 1)
	name_lbl.add_theme_constant_override("shadow_offset_y", 1)
	name_lbl.add_theme_font_size_override("font_size", 15)
	if ResourceLoader.exists(SkinDB.F_CINZEL):
		name_lbl.add_theme_font_override("font", load(SkinDB.F_CINZEL) as Font)
	ph.add_child(name_lbl)

	return ph


func _apply_expr_tint(border: Panel, base: Color, expr: String) -> void:
	var c := base
	match expr:
		"happy", "excited", "pleased", "warm":
			c = Color(minf(base.r + 0.12, 1.0), base.g, base.b * 0.75)
		"sad", "melancholy", "upset", "tired":
			c = Color(base.r * 0.65, base.g * 0.75, minf(base.b + 0.18, 1.0))
		"angry", "furious", "frustrated":
			c = Color(minf(base.r + 0.35, 1.0), base.g * 0.45, base.b * 0.45)
		"surprised", "shocked", "wide":
			c = Color(minf(base.r + 0.15, 1.0), minf(base.g + 0.15, 1.0), base.b * 0.6)
		"nervous", "scared", "uneasy":
			c = Color(minf(base.r + 0.08, 1.0), base.g * 0.9, minf(base.b + 0.08, 1.0))
	var st := StyleBoxFlat.new()
	st.bg_color = Color(0, 0, 0, 0)
	st.border_color = Color(c.r, c.g, c.b, 0.45)
	st.set_border_width_all(1)
	border.add_theme_stylebox_override("panel", st)


func _char_color(name: String) -> Color:
	var h := (name.hash() % 360 + 360) % 360
	return Color.from_hsv(h / 360.0, 0.52, 0.84)
