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
const PORTRAIT_COMP_ROOT := "res://resources/substrates/compositions/"
const PORTRAIT_TEX_ROOT  := "res://assets/characters/"

# Debug: overlay the resolved asset path on each portrait so you can
# see which file the engine loaded while playing through the game.
# Set to false to hide the overlay once you're done debugging.
const DEBUG_ASSET_OVERLAY: bool = true

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

const POSITIONS := {
	"left":   Vector2(100, 80),
	"center": Vector2(490, 80),
	"right":  Vector2(880, 80),
}
const SPRITE_W    := 300.0
const SPRITE_H    := 320.0
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


# Slugify a scene-supplied char name into the canonical key used for
# portrait composition lookups + CHAR_ACCENTS. "The Demon" → "the_demon",
# "oil exec" → "oil_exec". Spaces collapse to underscores so scenes can
# author display names with spaces without breaking file lookups.
func char_key(char_name: String) -> String:
	return char_name.strip_edges().to_lower().replace(" ", "_")


# Public lookup so DialogueBox / GameEngine / etc. can color speaker
# names and other chrome consistently with portrait accents.
func accent_for(char_name: String) -> Color:
	return CHAR_ACCENTS.get(char_key(char_name), ACCENT_DEFAULT)

# slot -> {name, expr, node: Control}
var _slots: Dictionary = {"left": null, "center": null, "right": null}
var _t:     float      = 0.0


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE


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
		var tint_holder: Control = node.get_meta("tint", null)
		if tint_holder != null:
			tint_holder.pivot_offset = tint_holder.size * 0.5
			tint_holder.scale = Vector2(breath_s, breath_s)
		# Blink overlay disabled — was a fixed-anchor dark band at
		# slot y=30-42%, which only aligned with eye-level when the
		# portrait was a tight face crop centered in the slot. With
		# the face-zoom + top-bias layout (which moves the face area
		# higher), the band landed below the eyes and read as a
		# random box flashing across the chest. Killing it is cleaner
		# than re-deriving eye position per asset shape.
		# ── Border redraw so ASCII frame tracks position + breath
		var border: Control = node.get_meta("border", null)
		if border != null:
			border.queue_redraw()


# Single-frame blink: a thin dark band at eye-level fades in/out
# over ~120 ms. Reads as a blink without any actual frame data on
# the portrait.
func _fire_blink(node: Control) -> void:
	var tint_holder: Control = node.get_meta("tint", null)
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

func show_character(char_name: String, expr: String, pos: String) -> void:
	if not POSITIONS.has(pos):
		pos = "center"
	# Store the slug, not the raw display name, so identity checks work
	# regardless of casing/spacing in scene JSON ("The Demon" vs "the demon").
	var key := char_key(char_name)
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
		_slots[pos] = {"name": key, "expr": expr, "node": node}
	else:
		# Same character in this slot — just update expression. No new
		# portrait node, no duplicate, no fade-in.
		_update_expr(slot["node"], char_name, expr)
		slot["expr"] = expr


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


func activate_speaker(char_name: String) -> void:
	# Empty char_name (called from narrate) → nobody is the active
	# speaker, so all portraits recede to the inactive state. This
	# lets the camera pull back during third-person narration instead
	# of leaving the last speaker on the screen as "main".
	var key := char_key(char_name)
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
		var target: Node = node.get_meta("figure_holder", node)
		var tw := node.create_tween()
		tw.set_parallel(true)
		tw.tween_property(target, "modulate", target_mod, 0.25)
		tw.tween_property(node, "scale", Vector2(target_scale, target_scale), 0.25)


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
	var img := Image.create(_STATIC_TILE_SIZE, _STATIC_TILE_SIZE, false, Image.FORMAT_RGBA8)
	var span: float = _STATIC_LUM_MAX - _STATIC_LUM_MIN
	for y in _STATIC_TILE_SIZE:
		for x in _STATIC_TILE_SIZE:
			var n: float = _STATIC_LUM_MIN + randf() * span
			img.set_pixel(x, y, Color(
				n * _STATIC_WARM_TINT.r,
				n * _STATIC_WARM_TINT.g,
				n * _STATIC_WARM_TINT.b,
				1.0))
	var tex := ImageTexture.create_from_image(img)
	var tr := TextureRect.new()
	tr.texture       = tex
	tr.stretch_mode  = TextureRect.STRETCH_TILE
	tr.expand_mode   = TextureRect.EXPAND_IGNORE_SIZE
	tr.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	tr.mouse_filter  = Control.MOUSE_FILTER_IGNORE
	return tr


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
	lbl.add_theme_font_size_override("font_size", 9)
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

	# Fuzzy-static backdrop — opaque dark warm noise. Lives BEHIND
	# everything else in the slot so when the figure dims (inactive
	# speaker, alpha 0.55) the scene bg doesn't bleed through. Lives
	# outside `figure_holder` so activate_speaker's modulate doesn't
	# also dim the backdrop.
	wrapper.add_child(_make_static_backdrop())

	# Subtle dark scrim above the static, below the figure — keeps the
	# figure popping against the noise without burying the noise entirely.
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
	if not has_face and FileAccess.file_exists(comp_path):
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
			# Nothing matched — log every path we tried so the author can
			# see which name / location to use.
			print("[CharLayer] %s (key=%s): PLACEHOLDER  no asset found" % [char_name, key])
			for tried in resolved["tried"]:
				print("    tried: %s" % tried)
			tint_holder.queue_free()
			wrapper.remove_meta("tint")
			wrapper.add_child(_make_placeholder(char_name, expr))
			wrapper.set_meta("kind", "placeholder")
			resolved_path = "PLACEHOLDER (no asset)"

	# Asset-path overlay — a small label at the bottom of the slot
	# showing the file path the engine loaded. Sits ABOVE everything
	# else so it stays visible while debugging asset assignments.
	# Toggle via DEBUG_ASSET_OVERLAY (top of file) once you're done.
	if DEBUG_ASSET_OVERLAY:
		_add_asset_overlay(wrapper, resolved_path)

	# ── ASCII frame around the portrait — drawn last so it sits on
	# top of the texture / composition. Tracks the breath scale by
	# being a sibling of tint_holder (also breathes via wrapper position).
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
	var kind: String = wrapper.get_meta("kind", "placeholder")
	var key  := char_key(char_name)
	if kind == "composition":
		_apply_texture_tint(wrapper, expr)
	elif kind == "texture":
		var tint_holder: Control = wrapper.get_meta("tint", null) as Control
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
		var ph: Control = wrapper.get_child(0)
		if ph.has_meta("expr_lbl"):
			(ph.get_meta("expr_lbl") as Label).text = "[ %s ]" % expr
		if ph.has_meta("border"):
			_apply_expr_tint(ph.get_meta("border") as Panel, _char_color(char_name), expr)


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
	var tried := [
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
		"%s%s.png" % [PORTRAIT_TEX_ROOT, key],
		"res://assets/portraits/%s.png" % [key],
	]
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
	var dir := DirAccess.open(PORTRAIT_GALLERY_ROOT)
	if dir == null:
		return
	dir.list_dir_begin()
	var fn := dir.get_next()
	while fn != "":
		if not dir.current_is_dir():
			var lower := fn.to_lower()
			if lower.ends_with(".png") or lower.ends_with(".jpg") or lower.ends_with(".jpeg"):
				var stem := lower.get_basename()
				_gallery_index[stem] = PORTRAIT_GALLERY_ROOT + fn
		fn = dir.get_next()
	print("[CharLayer] gallery index built · %d entries" % _gallery_index.size())


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
	var tint_holder: Control = wrapper.get_meta("tint", null) as Control
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
	# z above the portrait so the frame sits on top of the texture
	b.z_index = 5
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
	var pos: String = node.get_meta("pos", "center")
	var char_name: String = node.get_meta("char", "")
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
	var col := _char_color(char_name)
	var ph  := Control.new()
	ph.custom_minimum_size = Vector2(SPRITE_W, SPRITE_H)

	# Background fill
	var bg := Panel.new()
	bg.size = Vector2(SPRITE_W, SPRITE_H)
	var bg_st := StyleBoxFlat.new()
	bg_st.bg_color = Color(col.r * 0.10, col.g * 0.10, col.b * 0.10, 0.92)
	bg_st.border_color = Color(col.r, col.g, col.b, 0.0)
	bg_st.set_border_width_all(0)
	bg.add_theme_stylebox_override("panel", bg_st)
	ph.add_child(bg)

	# Colored border panel (expression-tinted)
	var border := Panel.new()
	border.size = Vector2(SPRITE_W, SPRITE_H)
	_apply_expr_tint(border, col, expr)
	ph.add_child(border)
	ph.set_meta("border", border)

	# Head oval
	var hw := 96.0
	var hh := 118.0
	var head := Panel.new()
	head.position           = Vector2((SPRITE_W - hw) * 0.5, 74.0)
	head.custom_minimum_size = Vector2(hw, hh)
	var h_st := StyleBoxFlat.new()
	h_st.bg_color = Color(col.r * 0.42, col.g * 0.42, col.b * 0.42, 0.95)
	var r := int(hw * 0.5)
	h_st.corner_radius_top_left     = r
	h_st.corner_radius_top_right    = r
	h_st.corner_radius_bottom_left  = r
	h_st.corner_radius_bottom_right = r
	head.add_theme_stylebox_override("panel", h_st)
	ph.add_child(head)

	# Body shape
	var bw := 164.0
	var body := Panel.new()
	body.position            = Vector2((SPRITE_W - bw) * 0.5, 214.0)
	body.custom_minimum_size = Vector2(bw, 234.0)
	var b_st := StyleBoxFlat.new()
	b_st.bg_color = Color(col.r * 0.30, col.g * 0.30, col.b * 0.30, 0.90)
	b_st.corner_radius_top_left  = 20
	b_st.corner_radius_top_right = 20
	body.add_theme_stylebox_override("panel", b_st)
	ph.add_child(body)

	# Name label
	var name_lbl := Label.new()
	name_lbl.text                = char_name.capitalize()
	name_lbl.position            = Vector2(0.0, SPRITE_H - 90.0)
	name_lbl.size                = Vector2(SPRITE_W, 32.0)
	name_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	name_lbl.add_theme_color_override("font_color", col)
	name_lbl.add_theme_font_size_override("font_size", 15)
	if ResourceLoader.exists(SkinDB.F_CINZEL):
		name_lbl.add_theme_font_override("font", load(SkinDB.F_CINZEL) as Font)
	ph.add_child(name_lbl)

	# Expression label
	var expr_lbl := Label.new()
	expr_lbl.text                = "[ %s ]" % expr
	expr_lbl.position            = Vector2(0.0, SPRITE_H - 54.0)
	expr_lbl.size                = Vector2(SPRITE_W, 22.0)
	expr_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	expr_lbl.add_theme_color_override("font_color", Color(col.r, col.g, col.b, 0.5))
	expr_lbl.add_theme_font_size_override("font_size", 10)
	ph.add_child(expr_lbl)
	ph.set_meta("expr_lbl", expr_lbl)

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
