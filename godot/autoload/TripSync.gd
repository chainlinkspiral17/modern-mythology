# TripSync.gd · AUTOLOAD
# ════════════════════════════════════════════════════════════════
# THE TRIP · the project-wide psychedelic layer, synced to the music.
#
# "Realism but trippy — I always wanted this running through the
# game at all times, in lines and backgrounds, synced to the music
# currently playing."  (2026-09-07)
#
# One node does four jobs:
#
#   1. LISTEN   · reads the BGM bus spectrum analyzer (AudioMgr owns
#                 one on the BGM bus; we attach one if it is missing)
#                 into eight log-spaced bands with an adaptive gain,
#                 so a quiet drone drives the picture as hard as a
#                 loud track. Detects beats on the low band (onset
#                 over a running average), keeps a tempo estimate
#                 from the median inter-beat interval, and runs the
#                 tempo-locked beat / bar phases the shader uses.
#   2. PAINT    · owns a global layer-60 CanvasLayer (above every
#                 scene's PostProcess stack at 50, below HUD at 100,
#                 below the slowstick look at 80) with one full-rect
#                 ColorRect running trip_sync.gdshader in screen
#                 mode. It is the PICTURE, not HUD: group
#                 "world_render", never "ui", name carries none of
#                 the F4 sweep's HUD substrings.
#   3. DELEGATE · surfaces that must keep their text clean (the VN)
#                 join the "trip_local" group and call attach() on
#                 their background CanvasItems; the same shader runs
#                 in texture mode on those and the global layer hides
#                 while any trip_local node is in the tree.
#   4. TRAIL    · the FEEDBACK buffer (2026-09-11), the Minter half.
#                 Two half-res SubViewports ping-pong: each frame the
#                 write buffer re-projects the read buffer slightly
#                 larger (or smaller) with a slow spin, decays it, and
#                 screens in the new light — the picture's highlights
#                 plus the register's aura. A show rect draws that
#                 back over the surface, additively. Light leaves a
#                 wake; the picture itself still never moves, and the
#                 beat only ever makes the wake BRIGHTER.
#
# Every attached material — global and local — receives the same
# music state each frame, so a VN background and a locale walk
# breathe to the same beat.
#
# Dial: Settings.trip_amount (0..1, PSYCHEDELIA in the settings
# overlay). 0 = the layer is an identity and hides itself.
# ════════════════════════════════════════════════════════════════
extends Node

const SHADER_PATH: String = "res://assets/shaders/trip_sync.gdshader"
const FEEDBACK_SHADER_PATH: String = "res://assets/shaders/trip_feedback.gdshader"
const FEEDBACK_SHOW_PATH: String = "res://assets/shaders/trip_feedback_show.gdshader"
const FEEDBACK_DIV: int = 2               # the buffer runs at half resolution
const LAYER_ORDER: int = 60
const BUS_NAME: String = "BGM"
const BANDS: int = 8
const FREQ_LO: float = 40.0
const FREQ_HI: float = 9000.0

# Beat detector
const BEAT_MIN_GAP: float = 0.22        # s · no two beats closer than this (~270 bpm)
const BEAT_RATIO: float = 1.32          # onset must clear the running average by this
const BEAT_FLOOR: float = 0.07          # ... plus this absolute margin (normalised units)
const INTERVAL_LO: float = 0.28         # s · accepted inter-beat range (215..46 bpm)
const INTERVAL_HI: float = 1.30
const INTERVALS_KEPT: int = 8
const PULSE_DECAY: float = 5.0          # base exp decay rate of the beat envelope (registers override)
const SILENCE_RAW: float = 0.0035       # raw analyzer sum below this = no music
const SILENCE_HOLD: float = 1.5         # s of quiet before the idle breath takes over

var _shader: Shader = null
var _global_layer: CanvasLayer = null
var _global_rect: ColorRect = null
var _materials: Array[ShaderMaterial] = []
var _analyzer: AudioEffectSpectrumAnalyzerInstance = null

# Music state (public read for anything else that wants to dance)
var amount: float = 0.75
var energy: float = 0.0
var bass: float = 0.0
var mid: float = 0.0
var high: float = 0.0
var pulse: float = 0.0
var _pulse_env: float = 0.0             # the raw envelope; `pulse` follows it with a 45 ms attack
var ring_t: float = 10.0
var beat_phase: float = 0.0
var bar_phase: float = 0.0
var hue_base: float = 0.0
var t_flow: float = 0.0
var bpm: float = 120.0
var music_present: bool = false
# Multipliers on `amount` (draft 1B). mood_scale is pushed by
# MoodCycler._apply — edge/ascii-heavy moods (neon 1.0, ascii ≥ 0.5)
# are already a stylization and the trip is dialled to 0.35 under
# them unless the preset carries its own "trip_scale". surface_scale
# is 0.45 while any node sits in "trip_soft" (the main menu — text-
# heavy surfaces the global layer still covers).
var mood_scale: float = 1.0
var surface_scale: float = 1.0
# The DIRECTOR's per-beat dial (draft 4): a `[trip:0.4]` / `[trip:1.3]`
# cue in a chapter sets it; `[trip:reset]` or a new scene clears it.
# Multiplied with the mood and surface scales. 0..1.5.
var scene_scale: float = 1.0
# The player's MIX (draft 3): four Settings dials multiplied into the
# shader — flow (the one dial that moves pixels), lines, colour, beat.
var mix_motion: float = 1.0
var mix_lines: float = 1.0
var mix_colour: float = 1.0
var mix_beat: float = 1.0
var mix_trails: float = 1.0
const SOFT_SURFACE_SCALE: float = 0.45

# ── THE FEEDBACK (2026-09-11) ─────────────────────────────────────
# The bible listed this as the missing half of the Minter register:
# "No feedback-trail buffer yet ... the real thing is a SubViewport
# with a decay quad, driven by the same pulse." Two half-resolution
# SubViewports ping-pong: each frame the write buffer re-projects the
# read buffer a hair larger (or smaller) with a slow spin, decays it,
# and screens in the bright part of a SOURCE TEXTURE. A show rect
# draws the result back over that surface, additively.
#
# The source is a texture, never the screen. In the VN that texture
# is the background image, so the dialogue box and every glyph of
# type are outside the buffer by construction and cannot smear —
# which is the same reason the trip shader runs in texture mode
# there. A screen-sourced feedback layer is draft 2 and needs a
# UI-free source first.
var _fb_shader: Shader = null
var _fb_show_shader: Shader = null
var _fb_vp: Array[SubViewport] = []
var _fb_mat: Array[ShaderMaterial] = []
var _fb_shows: Array[Dictionary] = []      # [{rect, mat, srcs}]
var _fb_write: int = 0
var _fb_size: Vector2i = Vector2i.ZERO

# ── REGISTERS · the per-pillar look (2026-09-07, user direction) ──
# "Major Arcana is swampy and arcade inspired; Planned Community is
# retro video games and zines and stoner sludge meta punk rock; Land
# of Milk and Honey is SCUMM-game inspired, psychedelic wall-of-sound
# classic rock but sci-fi. Slowsticks: Jeff Minter design and
# visuals, only using current hardware." Each register is a set of
# shader dials (colour and light only — THE IMAGE NEVER MOVES, see
# the bible's motion rule); hosts push one with themselves as owner and it pops
# when the owner leaves the tree (the VN's volume, a gauntlet run, a
# slowstick under the shelf). Float dials lerp over REGISTER_FADE;
# the palette snaps at the midpoint. See lore/_PSYCHEDELIC_DESIGN_BIBLE.md.
const REGISTERS: Dictionary = {
	# the base look · rainbow aura, moderate everything (menus, vols 1-4)
	# fb_* · THE FEEDBACK (2026-09-11). fb_amount is how much light
	# enters the buffer; fb_decay is the wake's length in e-folds per
	# second (LOW = it hangs); fb_zoom is the re-projection rate in
	# screens/second — POSITIVE blooms outward, NEGATIVE falls inward;
	# fb_spin is radians/second. All three are rates, never beat-
	# driven: the beat only brightens what enters (bible rule 0).
	"base": {
		"palette_mode": 0, "line_amount": 1.0, "flow_amount": 1.0, "hue_amount": 1.0,
		"ripple_amount": 1.0, "spark_amount": 0.0, "grain_amount": 0.0, "pulse_decay": 4.0,
		"fb_amount": 0.50, "fb_decay": 6.5, "fb_zoom": 0.10, "fb_spin": 0.00,
	},
	# vol 5 · MAJOR ARCANA · swampy + arcade: a bayou-water colour
	# wash, phosphor-green lines with sodium amber on the kick, little
	# hue drift (the noir stays noir)
	"arcana": {
		"palette_mode": 1, "line_amount": 1.25, "flow_amount": 1.35, "hue_amount": 0.55,
		"ripple_amount": 0.9, "spark_amount": 0.0, "grain_amount": 0.0, "pulse_decay": 3.5,
		# the cabinet: light SINKS into the screen (negative zoom), a slow
		# clockwise crawl, a short wake — an arcade monitor, not a lava lamp
		"fb_amount": 0.55, "fb_decay": 6.0, "fb_zoom": -0.09, "fb_spin": 0.05,
	},
	# vol 6 · PLANNED COMMUNITY · zines + sludge: two risograph inks
	# on the lines (no rainbow), photocopy grain, the flow is slow and
	# heavy (sludge tempo — the pulse hangs), hue drift almost off
	"community": {
		"palette_mode": 2, "line_amount": 1.15, "flow_amount": 0.75, "hue_amount": 0.35,
		"ripple_amount": 0.7, "spark_amount": 0.0, "grain_amount": 1.0, "pulse_decay": 2.4,
		# sludge: the wake HANGS (the longest decay of the five) and barely
		# travels — a smear in place, the photocopier's ghost, not a bloom
		"fb_amount": 0.45, "fb_decay": 2.6, "fb_zoom": 0.02, "fb_spin": 0.00,
	},
	# vol 7 · LAND OF MILK AND HONEY · liquid light show + sci-fi:
	# oil-projector palette, the densest colour wash and drift (the
	# wall of sound), a sparse slow starfield in the dark
	"milk_honey": {
		"palette_mode": 3, "line_amount": 0.95, "flow_amount": 1.45, "hue_amount": 1.35,
		"ripple_amount": 1.2, "spark_amount": 0.6, "grain_amount": 0.0, "pulse_decay": 3.0,
		# the oil projector: the densest feedback of the five — light BLOOMS
		# outward and turns slowly, which is what a liquid light show is
		"fb_amount": 0.90, "fb_decay": 3.8, "fb_zoom": 0.17, "fb_spin": 0.10,
	},
	# slowsticks · the quietest register (draft 2B Deck verdict on the
	# full neon overlay: "ugly and strobey"; draft 3: "stripped
	# completely" — so a middle). A 2D game screen has UI edges
	# everywhere and no lit flats: a moderate neon breath on the lines,
	# nothing moving on the flats, no sparks. The full Minter register
	# belongs INSIDE the sticks (their own particles and glow).
	"slowstick": {
		"palette_mode": 4, "line_amount": 0.65, "flow_amount": 0.0, "hue_amount": 0.15,
		"ripple_amount": 0.5, "spark_amount": 0.0, "grain_amount": 0.0, "pulse_decay": 3.0,
		# the register where feedback belongs MOST and shows LEAST: the
		# overlay stays faint ("ugly and strobey" was the verdict on a loud
		# one) because Minter lives inside each stick's own rendering
		"fb_amount": 0.22, "fb_decay": 5.5, "fb_zoom": 0.11, "fb_spin": 0.00,
	},
}
const REGISTER_FADE: float = 0.9          # s · float dials cross-fade
const REGISTER_FLOATS: Array[String] = [
	"line_amount", "flow_amount", "hue_amount", "ripple_amount",
	"spark_amount", "grain_amount",
]
# The feedback dials cross-fade with the rest but are read by the
# buffer rig rather than pushed to the trip material.
const FEEDBACK_FLOATS: Array[String] = [
	"fb_amount", "fb_decay", "fb_zoom", "fb_spin",
]
var _register_stack: Array[Dictionary] = []   # [{"name": String, "owner": Node}]
var register_name: String = "base"
var _reg_from: Dictionary = {}
var _reg_to: Dictionary = {}
var _reg_t: float = 1.0
var _pulse_decay: float = 5.0

var _bands: PackedFloat32Array = PackedFloat32Array()
var _band_lo: PackedFloat32Array = PackedFloat32Array()
var _band_hi: PackedFloat32Array = PackedFloat32Array()
var _peak_track: float = 0.05           # slow-tracking loudness ceiling for the auto-gain
var _bass_avg: float = 0.0
var _last_beat_at: float = -10.0
var _beat_interval: float = 0.5
var _intervals: Array[float] = []
var _silence_t: float = 0.0
var _clock: float = 0.0
var _ring_c: Vector2 = Vector2(0.5, 0.5)
var _ring_target: Vector2 = Vector2(0.5, 0.5)
var _rng: RandomNumberGenerator = RandomNumberGenerator.new()


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_rng.seed = 0x7121F
	_bands.resize(BANDS)
	_band_lo.resize(BANDS)
	_band_hi.resize(BANDS)
	var lo_log: float = log(FREQ_LO) / log(10.0)
	var hi_log: float = log(FREQ_HI) / log(10.0)
	for i in range(BANDS):
		_band_lo[i] = pow(10.0, lerpf(lo_log, hi_log, float(i) / float(BANDS)))
		_band_hi[i] = pow(10.0, lerpf(lo_log, hi_log, float(i + 1) / float(BANDS)))
	_shader = load(SHADER_PATH) as Shader
	if _shader == null:
		push_warning("[TripSync] shader missing at %s — layer disabled" % SHADER_PATH)
		return
	amount = clampf(Settings.trip_amount, 0.0, 1.0)
	mix_motion = clampf(Settings.trip_flow, 0.0, 1.0)
	mix_lines = clampf(Settings.trip_lines, 0.0, 1.0)
	mix_colour = clampf(Settings.trip_colour, 0.0, 1.0)
	mix_beat = clampf(Settings.trip_beat, 0.0, 1.0)
	mix_trails = clampf(Settings.trip_trails, 0.0, 1.0)
	_reg_from = REGISTERS["base"]
	_reg_to = REGISTERS["base"]
	Settings.settings_changed.connect(_on_setting)
	_spawn_global_layer()
	_spawn_feedback()
	print("[TripSync] on · amount %.2f · layer %d · PSYCHEDELIA slider in settings" % [amount, LAYER_ORDER])


func _on_setting(key: String, value: Variant) -> void:
	match key:
		"trip_amount": amount = clampf(float(value), 0.0, 1.0)
		"trip_flow": mix_motion = clampf(float(value), 0.0, 1.0)
		"trip_lines": mix_lines = clampf(float(value), 0.0, 1.0)
		"trip_colour": mix_colour = clampf(float(value), 0.0, 1.0)
		"trip_beat": mix_beat = clampf(float(value), 0.0, 1.0)
		"trip_trails": mix_trails = clampf(float(value), 0.0, 1.0)


# ── Layer ─────────────────────────────────────────────────────────
func _spawn_global_layer() -> void:
	_global_layer = CanvasLayer.new()
	_global_layer.name = "TripSync"
	_global_layer.layer = LAYER_ORDER
	_global_layer.add_to_group("world_render")   # the picture, not HUD — F4 leaves it
	add_child(_global_layer)
	_global_rect = ColorRect.new()
	_global_rect.name = "TripRect"
	_global_rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_global_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE   # never eat input
	var mat: ShaderMaterial = ShaderMaterial.new()
	mat.shader = _shader
	mat.set_shader_parameter("use_screen", true)
	_global_rect.material = mat
	_global_layer.add_child(_global_rect)
	_materials.append(mat)


# Run the trip on a CanvasItem's own texture (a TextureRect or a
# SubViewportContainer) instead of the screen. The caller's root
# should also join "trip_local" so the global layer steps aside.
func attach(item: CanvasItem) -> ShaderMaterial:
	if _shader == null or item == null:
		return null
	var existing: Material = item.material
	if existing is ShaderMaterial and (existing as ShaderMaterial).shader == _shader:
		return existing as ShaderMaterial
	var mat: ShaderMaterial = ShaderMaterial.new()
	mat.shader = _shader
	mat.set_shader_parameter("use_screen", false)
	item.material = mat
	_materials.append(mat)
	item.tree_exiting.connect(func() -> void: _materials.erase(mat))
	_push_to(mat)
	return mat


func detach(item: CanvasItem) -> void:
	if item == null:
		return
	var existing: Material = item.material
	if existing is ShaderMaterial and (existing as ShaderMaterial).shader == _shader:
		_materials.erase(existing as ShaderMaterial)
		item.material = null


# ── The feedback buffer ───────────────────────────────────────────
func _spawn_feedback() -> void:
	_fb_shader = load(FEEDBACK_SHADER_PATH) as Shader
	_fb_show_shader = load(FEEDBACK_SHOW_PATH) as Shader
	if _fb_shader == null or _fb_show_shader == null:
		push_warning("[TripSync] feedback shaders missing — trails disabled")
		return
	for i in range(2):
		var vp: SubViewport = SubViewport.new()
		vp.name = "TripFeedback%d" % i
		vp.disable_3d = true
		vp.transparent_bg = false
		vp.gui_disable_input = true
		vp.size = Vector2i(4, 4)
		# UPDATE_DISABLED until something asks for trails: an idle rig
		# must cost nothing on the Deck.
		vp.render_target_update_mode = SubViewport.UPDATE_DISABLED
		vp.render_target_clear_mode = SubViewport.CLEAR_MODE_ALWAYS
		var rect: ColorRect = ColorRect.new()
		rect.name = "Accumulate"
		rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
		var m: ShaderMaterial = ShaderMaterial.new()
		m.shader = _fb_shader
		rect.material = m
		vp.add_child(rect)
		add_child(vp)
		_fb_vp.append(vp)
		_fb_mat.append(m)
	_resize_feedback()
	var vport: Viewport = get_viewport()
	if vport != null and not vport.size_changed.is_connected(_resize_feedback):
		vport.size_changed.connect(_resize_feedback)


func _resize_feedback() -> void:
	var vport: Viewport = get_viewport()
	if vport == null or _fb_vp.size() < 2:
		return
	var vis: Vector2 = vport.get_visible_rect().size
	var want: Vector2i = Vector2i(
		maxi(8, int(vis.x) / FEEDBACK_DIV),
		maxi(8, int(vis.y) / FEEDBACK_DIV))
	if want == _fb_size:
		return
	_fb_size = want
	for vp in _fb_vp:
		vp.size = want


# Mount the feedback over a surface. `src_item` is the CanvasItem the
# buffer catches light from — it must carry a `texture` (a TextureRect
# in practice). Returns a full-rect Control the CALLER inserts into
# its own tree directly above that surface and below its type, so the
# trail lands on the picture and nowhere near the dialogue box.
func attach_feedback(src_item: CanvasItem) -> Control:
	if _fb_show_shader == null or src_item == null or _fb_vp.size() < 2:
		return null
	var rect: ColorRect = ColorRect.new()
	rect.name = "TripFeedbackRect"
	rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	rect.color = Color(0.0, 0.0, 0.0, 0.0)
	# The picture, not HUD — F4 must not take the trail out of a
	# screenshot any more than it takes the aura out (the global layer
	# carries the same group for the same reason).
	rect.add_to_group("world_render")
	var m: ShaderMaterial = ShaderMaterial.new()
	m.shader = _fb_show_shader
	rect.material = m
	rect.visible = false
	var srcs: Array = [src_item]
	_fb_shows.append({"rect": rect, "mat": m, "srcs": srcs})
	rect.tree_exiting.connect(func() -> void: detach_feedback(rect))
	return rect


# A surface may be painted by more than one node over a scene's life.
# The VN's background is a TextureRect for PNG scenes and a
# SubViewportContainer for `3d:` ones — and the 3D path sets
# `_bg.texture = null`, so a rig bound to the TextureRect alone goes
# dark on exactly the scenes that carry the most light. Register every
# candidate; the rig takes the last one that is visible and has a
# texture to give.
func add_feedback_source(rect: Control, item: CanvasItem) -> void:
	if rect == null or item == null:
		return
	for e in _fb_shows:
		if e["rect"] == rect:
			var srcs: Array = e["srcs"]
			if not srcs.has(item):
				srcs.append(item)
			return


# TextureRect → its texture. SubViewportContainer → the viewport it
# shows. Anything else → nothing, and the rig sleeps.
func _feedback_tex_of(item: CanvasItem) -> Texture2D:
	if item == null or not item.is_inside_tree() or not item.is_visible_in_tree():
		return null
	if item is SubViewportContainer:
		for child in item.get_children():
			if child is SubViewport:
				return (child as SubViewport).get_texture()
		return null
	var tex_v: Variant = item.get("texture")
	if tex_v is Texture2D:
		return tex_v as Texture2D
	return null


func detach_feedback(rect: Control) -> void:
	for i in range(_fb_shows.size() - 1, -1, -1):
		if _fb_shows[i]["rect"] == rect:
			_fb_shows.remove_at(i)


func _feedback_floats() -> Dictionary:
	var out: Dictionary = {}
	var k: float = smoothstep(0.0, 1.0, _reg_t)
	var cur: Dictionary = REGISTERS[register_name]
	for key in FEEDBACK_FLOATS:
		var a: float = float(_reg_from.get(key, cur.get(key, 0.0)))
		var b: float = float(_reg_to.get(key, cur.get(key, 0.0)))
		out[key] = lerpf(a, b, k)
	return out


# The hue the trail leans toward, per register — the same palettes the
# aura uses, as a single colour (the buffer is light, not a gradient).
func _feedback_tint() -> Vector3:
	var pal: int = int(REGISTERS[register_name].get("palette_mode", 0))
	match pal:
		1: return Vector3(0.55, 1.00, 0.78)   # swamp phosphor
		2: return Vector3(1.00, 0.45, 0.75)   # riso pink
		3: return Vector3(1.00, 0.62, 0.35)   # oil projector amber
		4: return Vector3(0.75, 0.95, 1.00)   # neon vector
	return Vector3(1.0, 1.0, 1.0)


func _update_feedback(dt: float) -> void:
	if _fb_vp.size() < 2 or _fb_shows.is_empty():
		return
	var reg: Dictionary = _feedback_floats()
	var fb_amount: float = float(reg.get("fb_amount", 0.0))
	var gain: float = effective_amount() * mix_trails * fb_amount
	# The source must be a texture that is actually on screen.
	var src_tex: Texture2D = null
	for e in _fb_shows:
		var srcs: Array = e["srcs"]
		for i in range(srcs.size() - 1, -1, -1):
			# Read as Variant: a source can be freed between frames (the
			# 3D container is torn down whenever a scene goes back to a
			# PNG background) and typing the element first would throw
			# on the freed instance instead of skipping it.
			var item_v: Variant = srcs[i]
			if not (item_v is CanvasItem) or not is_instance_valid(item_v):
				continue
			var t: Texture2D = _feedback_tex_of(item_v as CanvasItem)
			if t != null:
				src_tex = t
				break
	var live: bool = gain > 0.002 and src_tex != null
	for e in _fb_shows:
		var r: Control = e["rect"] as Control
		if r != null:
			r.visible = live
	if not live:
		for vp in _fb_vp:
			vp.render_target_update_mode = SubViewport.UPDATE_DISABLED
		return
	_resize_feedback()
	var read_i: int = 1 - _fb_write
	var wm: ShaderMaterial = _fb_mat[_fb_write]
	wm.set_shader_parameter("prev", _fb_vp[read_i].get_texture())
	wm.set_shader_parameter("src", src_tex)
	# Rates × delta, so the wake is the same length at any frame rate —
	# and so none of the three is touched by the music (bible rule 0:
	# the beat is light, never motion).
	wm.set_shader_parameter("decay", exp(-dt * float(reg.get("fb_decay", 6.0))))
	wm.set_shader_parameter("zoom", float(reg.get("fb_zoom", 0.1)) * dt)
	wm.set_shader_parameter("spin", float(reg.get("fb_spin", 0.0)) * dt)
	wm.set_shader_parameter("drift_x", sin(t_flow * 0.11) * 0.0009)
	wm.set_shader_parameter("drift_y", cos(t_flow * 0.083) * 0.0007)
	wm.set_shader_parameter("aspect",
		float(_fb_size.x) / maxf(1.0, float(_fb_size.y)))
	wm.set_shader_parameter("thresh", 0.60)
	wm.set_shader_parameter("gain", gain)
	wm.set_shader_parameter("pulse", pulse * mix_beat)
	wm.set_shader_parameter("tint", _feedback_tint())
	wm.set_shader_parameter("tint_mix", 0.35)
	# The aura is fed back at the register's line weight × the player's
	# LINES dial, so TRAILS and LINES agree about how much line there is.
	wm.set_shader_parameter("edge_amount",
		float(reg.get("fb_amount", 0.5)) * mix_lines * 1.2)
	var stex_size: Vector2 = src_tex.get_size()
	wm.set_shader_parameter("src_px", Vector2(
		1.0 / maxf(1.0, stex_size.x), 1.0 / maxf(1.0, stex_size.y)))
	_fb_vp[_fb_write].render_target_update_mode = SubViewport.UPDATE_ONCE
	_fb_vp[read_i].render_target_update_mode = SubViewport.UPDATE_DISABLED
	var buf: ViewportTexture = _fb_vp[_fb_write].get_texture()
	for e in _fb_shows:
		var sm: ShaderMaterial = e["mat"] as ShaderMaterial
		if sm == null:
			continue
		sm.set_shader_parameter("buf", buf)
		sm.set_shader_parameter("gain", 1.0)
		sm.set_shader_parameter("soft", 1.35)
		sm.set_shader_parameter("dark_bias", 0.55)
	_fb_write = read_i


# ── Listen ────────────────────────────────────────────────────────
func _find_analyzer() -> AudioEffectSpectrumAnalyzerInstance:
	if _analyzer != null:
		return _analyzer
	var bus_idx: int = AudioServer.get_bus_index(BUS_NAME)
	if bus_idx == -1:
		return null
	for i in range(AudioServer.get_bus_effect_count(bus_idx)):
		if AudioServer.get_bus_effect(bus_idx, i) is AudioEffectSpectrumAnalyzer:
			_analyzer = AudioServer.get_bus_effect_instance(bus_idx, i) as AudioEffectSpectrumAnalyzerInstance
			return _analyzer
	var spec: AudioEffectSpectrumAnalyzer = AudioEffectSpectrumAnalyzer.new()
	spec.fft_size = AudioEffectSpectrumAnalyzer.FFT_SIZE_2048
	AudioServer.add_bus_effect(bus_idx, spec)
	var new_idx: int = AudioServer.get_bus_effect_count(bus_idx) - 1
	_analyzer = AudioServer.get_bus_effect_instance(bus_idx, new_idx) as AudioEffectSpectrumAnalyzerInstance
	return _analyzer


func _process(delta: float) -> void:
	if _shader == null:
		return
	_clock += delta
	var dt: float = minf(delta, 0.1)

	# ── bands · raw magnitudes → adaptive gain → asymmetric smoothing
	var raw_sum: float = 0.0
	var raw: PackedFloat32Array = PackedFloat32Array()
	raw.resize(BANDS)
	var inst: AudioEffectSpectrumAnalyzerInstance = _find_analyzer()
	if inst != null:
		for i in range(BANDS):
			var m: float = inst.get_magnitude_for_frequency_range(_band_lo[i], _band_hi[i]).length()
			# the high bands carry far less amplitude than the lows; tilt them up
			m *= 1.0 + 0.55 * float(i)
			raw[i] = m
			raw_sum += m
	if raw_sum < SILENCE_RAW:
		_silence_t += dt
	else:
		_silence_t = 0.0
	music_present = _silence_t < SILENCE_HOLD

	# auto-gain: the ceiling follows the loudest recent moment and sinks slowly
	_peak_track = maxf(_peak_track * (1.0 - 0.10 * dt), raw_sum * 0.5)
	_peak_track = maxf(_peak_track, 0.02)
	var gain: float = 1.0 / _peak_track
	for i in range(BANDS):
		var target: float = clampf(raw[i] * gain * 2.6, 0.0, 1.0)
		var prev: float = _bands[i]
		var k: float = 0.35 if target > prev else 0.12
		_bands[i] = lerpf(prev, target, k)

	var bass_now: float = clampf((raw[0] + raw[1]) * gain * 1.4, 0.0, 1.5)
	var t_bass: float = (_bands[0] + _bands[1]) * 0.5
	var t_mid: float = (_bands[2] + _bands[3] + _bands[4]) / 3.0
	var t_high: float = (_bands[5] + _bands[6] + _bands[7]) / 3.0
	var t_energy: float = clampf(t_bass * 0.45 + t_mid * 0.35 + t_high * 0.20, 0.0, 1.0)

	if not music_present:
		# Idle breath: no music, the picture still lives, gently.
		var lfo: float = 0.5 + 0.5 * sin(_clock * 0.45)
		t_energy = 0.14 + 0.10 * lfo
		t_bass = 0.10 + 0.08 * lfo
		t_mid = 0.10
		t_high = 0.06
		bass_now = 0.0
		_bass_avg = 0.0
	bass = lerpf(bass, t_bass, 0.25)
	mid = lerpf(mid, t_mid, 0.25)
	high = lerpf(high, t_high, 0.25)
	energy = lerpf(energy, t_energy, 0.18)

	# ── beats · onset on the low band over its ~1 s running average
	_bass_avg = lerpf(_bass_avg, bass_now, clampf(dt * 1.6, 0.0, 1.0))
	if music_present and bass_now > _bass_avg * BEAT_RATIO + BEAT_FLOOR and _clock - _last_beat_at > BEAT_MIN_GAP:
		var interval: float = _clock - _last_beat_at
		_last_beat_at = _clock
		if interval > INTERVAL_LO and interval < INTERVAL_HI:
			_intervals.append(interval)
			while _intervals.size() > INTERVALS_KEPT:
				_intervals.pop_front()
			var sorted: Array[float] = []
			sorted.assign(_intervals)
			sorted.sort()
			_beat_interval = sorted[sorted.size() >> 1]
			bpm = 60.0 / _beat_interval
		_pulse_env = 1.0
		ring_t = 0.0
		beat_phase = 0.0
		_ring_target = Vector2(0.5 + _rng.randf_range(-0.18, 0.18), 0.5 + _rng.randf_range(-0.12, 0.12))

	# ── clocks
	# The beat envelope decays per register; `pulse` follows it through a
	# short attack so a hit swells in over ~45 ms instead of popping
	# (draft 2 · "rough").
	_pulse_env *= exp(-dt * _pulse_decay)
	pulse = lerpf(pulse, _pulse_env, clampf(dt * 22.0, 0.0, 1.0))
	ring_t += dt
	beat_phase = fposmod(beat_phase + dt / _beat_interval, 1.0)
	bar_phase = fposmod(bar_phase + dt / (_beat_interval * 4.0), 1.0)
	# Slow clocks (draft 2): the colour field and the hue rotation drift
	# at a fraction of draft 1's rates — fast hue cycling over large
	# areas is its own motion-sickness trigger.
	hue_base = fposmod(hue_base + dt * (0.007 + 0.035 * energy), 1.0)
	t_flow += dt * (0.22 + 0.55 * energy)
	_ring_c = _ring_c.lerp(_ring_target, clampf(dt * 2.5, 0.0, 1.0))

	# ── register fade + owner pruning (a freed host pops itself)
	if _reg_t < 1.0:
		_reg_t = minf(1.0, _reg_t + dt / REGISTER_FADE)
	if not _register_stack.is_empty():
		_resolve_register()

	# ── paint · the global layer steps aside for trip_local surfaces
	var local_active: bool = not get_tree().get_nodes_in_group("trip_local").is_empty()
	var soft_active: bool = not get_tree().get_nodes_in_group("trip_soft").is_empty()
	surface_scale = SOFT_SURFACE_SCALE if soft_active else 1.0
	if _global_layer != null:
		_global_layer.visible = effective_amount() > 0.001 and not local_active
	for mat in _materials:
		_push_to(mat)
	_update_feedback(dt)


func _push_to(mat: ShaderMaterial) -> void:
	if mat == null:
		return
	mat.set_shader_parameter("amount", effective_amount())
	mat.set_shader_parameter("mix_motion", mix_motion)
	mat.set_shader_parameter("mix_lines", mix_lines)
	mat.set_shader_parameter("mix_colour", mix_colour)
	mat.set_shader_parameter("mix_beat", mix_beat)
	mat.set_shader_parameter("energy", energy)
	mat.set_shader_parameter("bass", bass)
	mat.set_shader_parameter("mid", mid)
	mat.set_shader_parameter("high", high)
	mat.set_shader_parameter("pulse", pulse)
	mat.set_shader_parameter("ring_t", ring_t)
	mat.set_shader_parameter("beat_phase", beat_phase)
	mat.set_shader_parameter("bar_phase", bar_phase)
	mat.set_shader_parameter("hue_base", hue_base)
	mat.set_shader_parameter("t_flow", t_flow)
	mat.set_shader_parameter("ring_cx", _ring_c.x)
	mat.set_shader_parameter("ring_cy", _ring_c.y)
	_push_register_to(mat)


# ── Public helpers ────────────────────────────────────────────────
func effective_amount() -> float:
	return clampf(amount * mood_scale * surface_scale * scene_scale, 0.0, 1.0)


# GameEngine's `[trip:X]` directive (X = 0..1.5, "reset", "off", "full").
func set_scene_scale(v: float) -> void:
	scene_scale = clampf(v, 0.0, 1.5)


func apply_trip_cue(arg: String) -> void:
	var a: String = arg.strip_edges().to_lower()
	if a == "reset" or a == "":
		set_scene_scale(1.0)
	elif a == "off":
		set_scene_scale(0.0)
	elif a == "full":
		set_scene_scale(1.5)
	elif a.is_valid_float():
		set_scene_scale(float(a))


func set_amount(v: float) -> void:
	Settings.trip_amount = clampf(v, 0.0, 1.0)


# MoodCycler._apply pushes this on every mood change.
func set_mood_scale(v: float) -> void:
	mood_scale = clampf(v, 0.0, 1.0)


# ── Registers ─────────────────────────────────────────────────────
static func register_for_volume(vol: int) -> String:
	match vol:
		5: return "arcana"
		6: return "community"
		7: return "milk_honey"
	return "base"


# Push a register for as long as `owner` is in the tree. Hosts call
# this from _ready with themselves; the VN calls it with its volume.
func push_register(reg: String, owner: Node) -> void:
	if not REGISTERS.has(reg) or owner == null:
		return
	for i in range(_register_stack.size()):
		if _register_stack[i]["owner"] == owner:
			_register_stack.remove_at(i)
			break
	# "seen" flips once the owner has been inside the tree; a host that
	# pushes from a static builder before add_child (SlowstickLook)
	# must not be pruned on the very next resolve.
	_register_stack.append({"name": reg, "owner": owner, "seen": owner.is_inside_tree()})
	_resolve_register()


func pop_register(owner: Node) -> void:
	for i in range(_register_stack.size()):
		if _register_stack[i]["owner"] == owner:
			_register_stack.remove_at(i)
			break
	_resolve_register()


func _resolve_register() -> void:
	var i: int = _register_stack.size() - 1
	while i >= 0:
		var entry: Dictionary = _register_stack[i]
		var owner_v: Variant = entry["owner"]
		if not is_instance_valid(owner_v):
			_register_stack.remove_at(i)
		else:
			var owner: Node = owner_v as Node
			if owner.is_inside_tree():
				entry["seen"] = true
			elif bool(entry.get("seen", false)):
				_register_stack.remove_at(i)
		i -= 1
	var target: String = "base"
	if not _register_stack.is_empty():
		target = String(_register_stack[_register_stack.size() - 1]["name"])
	if target == register_name:
		return
	_reg_from = _current_register_floats()
	_reg_to = REGISTERS[target]
	_reg_t = 0.0
	register_name = target
	_pulse_decay = float(_reg_to.get("pulse_decay", 5.0))
	print("[TripSync] register → %s" % target)


func _current_register_floats() -> Dictionary:
	var out: Dictionary = {}
	var k: float = smoothstep(0.0, 1.0, _reg_t)
	var base: Dictionary = REGISTERS[register_name]
	for key in REGISTER_FLOATS + FEEDBACK_FLOATS:
		var a: float = float(_reg_from.get(key, base.get(key, 0.0)))
		var b: float = float(_reg_to.get(key, base.get(key, 0.0)))
		out[key] = lerpf(a, b, k)
	return out


func _push_register_to(mat: ShaderMaterial) -> void:
	var k: float = smoothstep(0.0, 1.0, _reg_t)
	var cur: Dictionary = REGISTERS[register_name]
	for key in REGISTER_FLOATS:
		var a: float = float(_reg_from.get(key, cur.get(key, 0.0)))
		var b: float = float(_reg_to.get(key, cur.get(key, 0.0)))
		mat.set_shader_parameter(key, lerpf(a, b, k))
	# the palette snaps at the midpoint of the fade
	var pal_src: Dictionary = _reg_to if k >= 0.5 else _reg_from
	mat.set_shader_parameter("palette_mode", int(pal_src.get("palette_mode", cur.get("palette_mode", 0))))


func status_line() -> String:
	var fb: Dictionary = _feedback_floats()
	var fb_live: String = "off"
	if not _fb_shows.is_empty():
		var r0: Control = _fb_shows[0]["rect"] as Control
		if r0 != null and r0.visible:
			fb_live = "%dx%d" % [_fb_size.x, _fb_size.y]
	return "TRIP %d%% (dial %d%% · mood ×%.2f · surface ×%.2f · scene ×%.2f · mix f%.1f l%.1f c%.1f b%.1f t%.1f) · %s · %s · %.0f bpm · e%.2f b%.2f p%.2f · trail %s a%.2f d%.1f z%+.2f" % [
		int(effective_amount() * 100.0), int(amount * 100.0), mood_scale, surface_scale, scene_scale, mix_motion, mix_lines, mix_colour, mix_beat, mix_trails,
		register_name, "music" if music_present else "idle", bpm, energy, bass, pulse,
		fb_live, float(fb.get("fb_amount", 0.0)), float(fb.get("fb_decay", 0.0)), float(fb.get("fb_zoom", 0.0))]
