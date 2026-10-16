# Portrait3D.gd
# ════════════════════════════════════════════════════════════════
# Controller for Portrait3D.tscn — a SubViewport-backed VN portrait
# that renders a 3D character GLB to a ViewportTexture. CharLayer
# instantiates this scene when a matching GLB is available for the
# speaking character; otherwise it falls back to the existing
# PNG / ASCII-composition portrait path.
#
# Public API:
#   load_character(glb_path: String, expression: String = "")
#       Loads a GLB into CharacterAnchor; clears any previous load.
#       Re-runs the auto-orient + auto-scale heuristic the Graustark
#       hero placement uses, so heroes from different exporters
#       (Mixamo, Meshy, Ready Player Me) all frame consistently.
#
#   set_expression(expression: String)
#       Drives a per-mood camera + lighting + motion override on
#       top of the resting framing. Each mood has:
#           · camera position offset (zoom, side, tilt)
#           · key/fill light color + energy
#           · continuous motion (shake amplitude/frequency, bob
#             amplitude/frequency, drift)
#       See MOOD_TABLE below. Subtle by design — the goal is
#       'angry' reads as a tightening + tremor + warm-red light,
#       not a screen-pounding shake.
#
#   get_viewport_texture() -> ViewportTexture
#       Convenience accessor used by CharLayer when wrapping this
#       node inside a TextureRect.
# ════════════════════════════════════════════════════════════════
extends SubViewportContainer

const PORTRAIT_W: int = 300
const PORTRAIT_H: int = 320
const TARGET_HEIGHT_M: float = 1.80   # frame to roughly real-human

@onready var _viewport: SubViewport = $SubViewport
@onready var _anchor: Node3D = $SubViewport/CharacterAnchor
@onready var _placeholder: Node3D = $SubViewport/CharacterAnchor/Placeholder
@onready var _camera: Camera3D = $SubViewport/Camera3D
@onready var _key: DirectionalLight3D = $SubViewport/Key
@onready var _fill: DirectionalLight3D = $SubViewport/Fill
@onready var _back: DirectionalLight3D = $SubViewport/BackRim

var _loaded_glb_path: String = ""
var _current_character: Node3D = null

# Resting camera transform (read once at _ready), so per-mood
# offsets compose on top instead of accumulating
var _rest_cam_pos: Vector3
var _rest_cam_fov: float
var _rest_cam_rot: Vector3 = Vector3.ZERO
var _rest_key_color: Color
var _rest_key_energy: float
var _rest_fill_color: Color
var _rest_fill_energy: float
var _rest_back_color: Color
var _rest_back_energy: float

# Active mood state — _process() reads these to animate
var _mood_id: String = "neutral"
var _mood: Dictionary = {}
var _mood_t: float = 0.0     # time since the mood was set (drives motion)

# ── SHOTS (draft 1 · 2026-10-01) ─────────────────────────────────
# Real shot sizes framed from the figure itself (every model is scaled
# to TARGET_HEIGHT_M, feet at 0): the bottom and top of the frame as
# fractions of the figure's height, and the lens (vertical FOV) — longer
# for closer shots, the portrait photographer's 85-135 mm: faces flatten
# kindly and the A-pose arms of the Meshy models leave the frame. The
# PortraitDirector picks the size and angle per line; set_shot() cuts
# (the house grammar: cuts between held frames, never a dolly).
const SHOT_FRAMES := {
	"wide":   {"b": 0.36,  "t": 1.04,  "fov": 34.0},   # thigh-up — the old resting frame
	"medium": {"b": 0.55,  "t": 1.05,  "fov": 30.0},   # waist-up
	"mcu":    {"b": 0.70,  "t": 1.045, "fov": 26.0},   # chest-up — the dialogue single
	"cu":     {"b": 0.795, "t": 1.035, "fov": 22.0},   # head and shoulders
	"ecu":    {"b": 0.865, "t": 0.995, "fov": 19.0},   # the face; the crown leaves frame
}
const YAW_THREE_QUARTER: float = 0.40       # rad (~23°) — the old 3/4 offset (atan 1.15/2.7)
const ANGLE_ELEVATION := {"eye": 0.0, "low": -0.16, "high": 0.14, "dutch": 0.0}   # rad: camera below / above the frame centre
const DUTCH_ROLL: float = 0.105             # rad (~6°)
const WIDE_FRAME_H: float = 0.68 * TARGET_HEIGHT_M
# FACE-ANCHORED close shots (sheet 41, 2026-10-01): every model is scaled
# to TARGET_HEIGHT_M INCLUDING its hair and hats, so a frame placed as a
# fraction of height missed the face on a third of the cast (Frasier's
# locs, Aria's hair, the Frog's hat, the Stranger's hood filled the ECU;
# Jimmy and Diego cropped). The neck — the narrowest slice of the mesh
# between the shoulders and the head — is measured at load, and the cu
# and ecu are framed from it (metres above / below the neck).
#
# Sheet 43 (2026-10-01): the cu (0.53 m, neck-anchored) was barely tighter
# than the mcu (0.62 m, a fraction of height) — a push-in read as nothing —
# and the ecu sat low on some faces (Alice: eyes at the top edge). All
# three close sizes now hang off the neck in clear steps (0.64 → 0.38 →
# 0.18 m: ~0.6× then ~0.47×; the viewport is near-square, so the width
# matches) and aim at the measured head — Meshy heads sit 0-5 cm forward
# of the figure's axis (AIM: how far each size leans toward it).
# Each size: frame height h; its top sits `cap` over the crown (every
# figure is scaled so the crown — hair, hat — is at TARGET_HEIGHT_M) but
# never more than t_max over the neck (big hair would lift the face out),
# and its bottom never above b_max from the neck (the chin stays in).
# EYE-ANCHORED (sheet 43 read by eye, 2026-10-01). The neck is a poor
# proxy for the eyes: on a typical Meshy hero the eyes sit ~10 cm above
# the narrowest slice, but where that slice is really the jaw (Aria,
# Tanya, Alice, Graciela, Sam, Coach Guidry, Gloria) they sit 14-18 cm
# above it, and the Deck's Frasier — his locs count toward the 1.80 m —
# spoke from behind the dialogue text. Every close size now puts the
# EYES at `eye_at` of the frame from the top (the box covers the lower
# half of the screen), its top never more than `cap` over the crown.
#
# THE BOX (2026-10-13, the user: "lots don't line up right"). Those
# fractions ignored the dialogue box. A cut-out slot is 900 px tall and the
# screen 720, and the reading band (DialogueBox: 44 % of the screen, its
# fade starting 56 px over it) covers everything below ~380 px — 42 % of
# the slot. The cu put the eyes at 0.36 (333 px) and the mouth and chin
# under the text on every hero (PortraitCastSheet, cast0); the ecu showed
# eyes over a paragraph. Every close size now keeps the face in the clean
# top 42 %: the eyes at ~0.20 of the frame and the frame wide enough that
# the chin (≈ 12 cm under the eyes) clears the band — cu chin at ~0.41,
# ecu at the band's edge with the mouth clear (brow to mouth: Leone).
const FACE_FRAMES := {
	"mcu": {"h": 0.80, "eye_at": 0.20, "cap": 0.14},   # chest-up; the face high, the chest under the box
	"cu":  {"h": 0.56, "eye_at": 0.22, "cap": 0.03},   # the head fills the clean frame
	"ecu": {"h": 0.36, "eye_at": 0.20, "cap": 0.0},    # brow to mouth; the crown and chin leave
}
const EYES_OVER_NECK: float = 0.10     # the sheet-43 median, for a model not in the table
# Where the eye line sat in each hero's sheet-43 ecu frame (fraction
# from the top). That frame was centred 9.5 cm over the measured neck
# (or 10.5 cm under the crown when that was lower), at a known take
# (seed 7: +1.36 % frame, +0.9° lens), 0.21 m tall — so the eye height
# follows exactly from the same neck reading. Regenerate from a later
# sheet when a model is replaced. (The Stranger's hood has no eyes to read.)
const SHEET43_ECU_EYE := {
	"alberto": 0.55, "alice_newsom": 0.25, "anna_logue": 0.50, "antonio": 0.60,
	"aria_third": 0.12, "ben_kowalski": 0.62, "bianca_miller": 0.53, "carl_drummer": 0.50,
	"carl_reno": 0.48, "chief_miller": 0.55, "claire_moyer": 0.45, "coach_guidry": 0.27,
	"curtis": 0.50, "dante_dambrosio": 0.52, "david_jarvis": 0.48, "dickens_dean": 0.52,
	"diego_ramos": 0.42, "douglas_forte": 0.55, "elicia_temple": 0.46, "erica_campbell": 0.40,
	"father_amato": 0.40, "faust": 0.45, "frasier_temple": 0.53, "gloria_reyes": 0.30,
	"graciela_ramos": 0.20, "hector": 0.55, "jacob": 0.68, "jesse_henderson": 0.52,
	"jimmy_daigle": 0.62, "joan": 0.68, "joanna_lemoine": 0.45, "john_frank": 0.55,
	"linda_caldwell": 0.65, "mackenzie_roberts": 0.62, "maya_daigle": 0.45, "miriam": 0.40,
	"natalie_david": 0.72, "nicola": 0.47, "philip_roberts": 0.47, "quentin_paul": 0.55,
	"ramirez": 0.45, "rick_cosmic": 0.48, "sam_miller_apron": 0.25, "sammy": 0.45,
	"skip_donnelly": 0.48, "tanya_horne": 0.22, "the_frog": 0.50, "thomas_henderson": 0.65,
	"vince_kane": 0.73, "wagner": 0.58,
}
const AIM := {"mcu": 0.6, "cu": 1.0, "ecu": 1.0}
var _neck_y: float = -1.0                    # measured; < 0 = not found, fall back to fractions
var _head_xz: Vector2 = Vector2.ZERO         # the head's centre off the figure's axis (x, z)
var _eyes_measured: float = -1.0             # from the texture (_measure_eyes); < 0 = not read
var _eyes_cache: float = -1.0                # _eyes_y()'s answer for the loaded hero
var _albedo_cache: Dictionary = {}           # texture instance id → decompressed Image
var _eyes_debug: bool = OS.has_environment("PORTRAIT_EYES_DEBUG")
var _shot_size: String = "medium"
var _shot_angle: String = "eye"
var _motion_scale: float = 1.0               # mood push/bob/shake shrink with the frame

# ── VARIATION + THE SCENE'S LIGHT (2026-10-01) ─────────────────────
# The user: "the camera doesn't have to be set for every shot, it can
# be randomly allowed within a set area, same with lighting and shader
# effects and post-processing on the portraits. contrast and work
# within the scene." Each new shot rolls the camera, the key light and
# the grade inside the ranges below (a held shot keeps its roll); the
# key takes the locale's light, the rim goes the other way so the
# figure separates from the room.
const VARY := {
	"yaw": 0.10,          # rad either side of the 3/4 angle
	"elev": 0.04,         # rad up/down on top of the shot's angle
	"frame_y": 0.04,      # fraction of the frame height the subject may sit off-centre
	"fov": 1.5,           # degrees of lens either way
	"dutch_min": 0.07, "dutch_max": 0.14,
	"key_yaw": 0.28, "key_pitch": 0.12,   # rad the key may swing round the head
	"energy": 0.10,       # ± fraction on key / fill / rim
	"contrast": [1.02, 1.16], "saturation": [0.90, 1.08],
}
const SCENE_MIX: float = 0.55                # how far the key/fill lean toward the room's light
var _scene: Dictionary = {}                  # {key, ambient, level} from Background3D
var _rng := RandomNumberGenerator.new()
var _key_rest_basis: Basis
# THE RIG (2026-10-13, the user: "lots look plain bad with lighting"). The
# .tscn's lights were authored by eye and never checked: read back, its
# FILL came from below and BEHIND the figure and its RIM from below — the
# face had one light, a key 45° up on the camera's side (flat on the near
# cheek, black sockets, a hard line under the lip) and ambient. Each light
# is now placed from where it shines (the figure faces +z; the camera sits
# YAW_THREE_QUARTER to +x):
#   key  — short lighting: on the far side of the nose from the camera,
#          low enough to reach the eyes;
#   fill — beside the lens, a touch under the eye line: opens the sockets
#          and the lip crease the textures paint dark;
#   rim  — behind and above, on the camera's side: separates the shadowed
#          cheek and the hair from the room.
# yaw / elev in radians; per character in CHARACTER_SHADING["rig"].
const RIG := {
	"key_yaw": -0.55, "key_elev": 0.36,
	"fill_yaw": 0.30, "fill_elev": -0.05,
	"rim_yaw": 2.45, "rim_elev": 0.55,
	"key_energy": 1.10, "fill_energy": 0.42, "rim_energy": 0.70,
	"fill_color": Color(0.92, 0.87, 0.80),
}
# The moods' and CHARACTER_LIGHTING's fill energies were tuned while the
# fill never reached a face; on the new fill (beside the lens) they are
# scaled to the rig's level (0.55 → 0.42).
const LEGACY_FILL_SCALE: float = 0.76
## Tools only (PortraitCastSheet --rig k=v,...): laid over RIG.
static var rig_override: Dictionary = {}
var _roll: Dictionary = {}                   # the current shot's rolled values

# Demon mode — when true, set_expression() routes to "demon_chaos"
# regardless of the requested expression (a demon doesn't perform
# moods, it leaks signal corruption), and the SubViewportContainer's
# portrait_demon_static shader gets pushed to strength=1.
var _demon_mode: bool = false

# ── Mood table ───────────────────────────────────────────────────
# Each mood entry is OPTIONAL — leaves missing keys mean "use rest
# value." Camera offsets are added to the resting transform; light
# tweaks REPLACE the resting color/energy when present.
#
#   pos_off      Vector3 added to resting camera position
#                (negative Z = closer to character / zoom in)
#   pitch_off    radians added to camera pitch
#   yaw_off      radians added to camera yaw
#   fov_off      degrees added to resting FOV (negative = zoom in)
#   key_color    Color to override key-light color
#   key_energy   float to override key-light energy
#   fill_color   ...
#   shake_amp    Vector3 amplitude in radians (camera rotational
#                jitter — small)
#   shake_freq   Hz; how fast the shake oscillates
#   bob_amp      meters; vertical positional sway amplitude
#   bob_freq     Hz; vertical sway frequency
#   drift_yaw    rad/sec; slow continuous yaw drift
#   sway_amp     radians; horizontal yaw sway amplitude
#   sway_freq    Hz
# MOTION (2026-10-01, the Deck: "start of volume 6 models are super
# shaky and motion sickness inducing" · "less motion"). The table's
# amplitudes were set for the old thigh-up 34° frame at portrait-box
# size; the heroes now fill half the screen on 19-26° lenses, where the
# same sway, drift and tremor read three to five times larger — and the
# sway and drift were never scaled to the frame at all. Every movement
# now runs at MOTION_GAIN, angular movement scaled by the lens against
# the old 34°, and a tremor is a STARTLE that dies in ~1.5 s (only the
# demon keeps shaking — that is its signal).
const MOTION_GAIN: float = 0.30
const MOTION_REF_FOV: float = 34.0
const STARTLE_DECAY: float = 2.5            # 1/s

# THE LOOK (2026-10-01, the Deck: "the models look kinda lame without
# post-processing and effects and mood direction"). The locale renders
# through its own post stack; the hero now gets a matched pass on its
# container (portrait_demon_static.gdshader's `look` path): lens fringe,
# grade, bloom, grain, a rim glow in the ROOM's key colour, a vignette,
# a fade at the base. LOOK_BASE is every hero at rest; MOOD_LOOK pushes
# it the way the line feels (deltas, added); the room sets temperature,
# the rim's colour and the shadows' tint. Eased, never cut.
# 2026-10-02, the Deck: "less plastic, more cartoon sketch, with
# watercolor vibe." The look became a painted pass: washes, soft cel
# bands, pigment pooling, paper grain, broken ink lines, hatching, a
# ragged bleed into the room (portrait_demon_static.gdshader), and the
# models' own materials are made MATTE on load (_matte_materials) — the
# plastic sheen was in the material before any shader saw it. The mood
# moves the medium: sorrow runs wetter and paler, anger inks harder and
# hatches deeper, joy is a bright clean wash.
const LOOK_BASE := {
	# draft 2 of the painted hero (2026-10-02, "doesn't look like watercolor
	# at all"): the wash and the paper carry the look; the ink is a pencil
	"look_contrast": 1.06, "look_sat": 1.10, "look_temp": 0.0,
	"look_grain": 0.20, "look_rim": 0.45, "look_vignette": 0.15, "look_fade": 0.6,
	"look_wash": 0.85, "look_cel": 0.25, "look_bands": 4.0, "look_matte": 0.85,
	"look_ink": 0.45, "look_ink_thr": 0.22, "look_hatch": 0.25, "look_paper": 0.80,
	"look_bleed": 0.80, "look_wobble": 1.0, "look_crush": 1.0, "look_pigment": 1.0,
}
const MOOD_LOOK := {
	"happy":     {"look_temp": 0.30, "look_sat": 0.12, "look_hatch": -0.30, "look_wash": 0.10},
	"sad":       {"look_sat": -0.30, "look_temp": -0.50, "look_bleed": 0.30, "look_wash": 0.15, "look_ink": -0.25, "look_vignette": 0.25},
	"tired":     {"look_sat": -0.30, "look_contrast": -0.08, "look_bleed": 0.20, "look_ink": -0.15},
	"angry":     {"look_contrast": 0.14, "look_temp": -0.10, "look_sat": -0.20, "look_ink": 0.20, "look_ink_thr": -0.04, "look_hatch": 0.35, "look_bands": -1.0},
	"nervous":   {"look_wobble": 0.8, "look_hatch": 0.20, "look_sat": -0.15},
	"surprised": {"look_contrast": 0.08, "look_ink": 0.10},
}
const LOOK_EASE: float = 4.0                # 1/s

# ── PER-CHARACTER SHADING (2026-10-13) ─────────────────────────────────────
# The user: "character lighting and shading needs to be figured out per
# character, the models look splotchy and have weird ugly visual artifacts
# that look like misshapen lips or facial features." Three causes, read off
# John / Dante / Elicia renders over the diner:
#   1. Meshy BAKES shading into the albedo (dark sockets, lip creases), and
#      the rig shades it again — raccoon eyes, a dark gash for a mouth.
#      → portrait_skin.gdshader: a curve that LIFTS the darkest albedo and
#        leaves the highlights (`lift`, `lift_knee`); a plain contrast cut
#        could not open John's near-black sockets without washing his skin.
#   2. Meshy's normal maps are full strength and noisy at portrait range,
#      and its emission map lights random patches → splotches.
#      → normal_scale 0.35, emission off, a wrap diffuse for a soft
#        terminator.
#   3. The look's ink pass traced every texture edge (eyelids, lip lines)
#      at threshold 0.22 and the 4-band cel step + hatching cut the skin
#      into patches → `look` overrides: less ink, a higher threshold,
#      finer bands, almost no hatching on faces.
# SHADING_DEFAULT applies to every hero; CHARACTER_SHADING overrides per
# character (keys as in CHARACTER_LIGHTING: the GLB's basename).
const SKIN_SHADER := preload("res://assets/shaders/portrait_skin.gdshader")
const SHADING_DEFAULT := {
	# look_amount (2026-10-13): the painted pass at full strength smeared
	# the eyes and dulled their whites on every face (cast sheet, look on vs
	# off); the face keeps a measure of the paint, not all of it
	"look_amount": 0.6,
	"skin_shader": true, "lift": 0.45, "lift_knee": 0.45, "sat": 1.0, "tint": Color(1, 1, 1),
	"specular": 0.10, "normal_scale": 0.35, "emission": false, "wrap": true,
	# look_rim / look_bleed (2026-10-13): softer — the rig's real rim light
	# separates the figure now
	"look": {"look_ink": 0.20, "look_ink_thr": 0.34, "look_hatch": 0.06, "look_cel": 0.10,
			 "look_bands": 6.0, "look_wobble": 0.6, "look_bleed": 0.30, "look_rim": 0.12,
			 # the dark-crush and the wash's smear made sockets into smudges
			 # (cast sheet halo_g vs halo_f, 2026-10-13)
			 # and the pigment darkened at every detail edge: the eyes most
			 "look_crush": 0.25, "look_wash": 0.55, "look_pigment": 0.30},
}
const CHARACTER_SHADING := {
	# near-black painted sockets and a hard mouth line in his texture; the
	# lens-side fill a notch up opens the sockets (cast sheet, 2026-10-13)
	"john_frank": {"lift": 0.85, "lift_knee": 0.50, "rig": {"fill_energy": 0.55}},
	# deep skin went to mud in the night and sad frames (cast3): more key
	# and fill, and a little sheen so the planes of the face read
	"frasier_temple": {"lift": 0.50, "specular": 0.22, "rig": {"key_energy": 1.30, "fill_energy": 0.60}},
	# the age lines are the character: lift less, keep a little more ink
	"dante_dambrosio": {"lift": 0.35, "look": {"look_ink": 0.26}},
	"elicia_temple": {"lift": 0.55},
}
var _shading: Dictionary = {}               # the resolved shading for the loaded hero
## A tuning override laid over the resolved shading (tools/PortraitLookTest
## --lift/--knee/...); empty in the game.
var shading_override: Dictionary = {}
var _look_on: bool = true
var _look_now: Dictionary = {}
var _look_target: Dictionary = {}
var _rim_now: Color = Color(0.70, 0.85, 1.0)
var _rim_target: Color = Color(0.70, 0.85, 1.0)
var _shadow_target: Color = Color(0.10, 0.09, 0.14)

const MOOD_TABLE := {
	"neutral": {
		"pos_off":  Vector3(0, 0, -0.15),     # subtle zoom-in
		"fov_off":  -1.0,
		"key_color":  Color(0.74, 0.82, 0.96),
		"key_energy": 1.05,
		"bob_amp":  0.005, "bob_freq": 0.30,  # gentle breathing
	},
	"happy": {
		"pos_off":  Vector3(0, 0.04, -0.08),
		"key_color":  Color(0.98, 0.92, 0.74),   # warm boost
		"key_energy": 1.35,
		"fill_color": Color(1.00, 0.85, 0.58),
		"fill_energy": 0.70,
		"bob_amp":  0.020, "bob_freq": 0.60,  # bouncy
		"sway_amp": 0.012, "sway_freq": 0.35, # CCW/CW lilt
	},
	"sad": {
		"pos_off":  Vector3(0, -0.06, -0.05),
		"pitch_off": -0.05,
		"key_color":  Color(0.66, 0.78, 0.96),   # cooler
		"key_energy": 0.85,
		"fill_color": Color(0.62, 0.74, 0.88),
		"fill_energy": 0.38,
		"bob_amp":  0.004, "bob_freq": 0.20,  # slow droop
		"drift_yaw": -0.02,
	},
	"surprised": {
		"pos_off":  Vector3(0, 0, -0.25),     # snap zoom-in
		"fov_off":  -3.0,
		"key_color":  Color(0.92, 0.95, 1.00),
		"key_energy": 1.30,
		"shake_amp": Vector3(0.004, 0.004, 0),
		"shake_freq": 14.0,                   # quick jitter
	},
	"angry": {
		"pos_off":  Vector3(0.02, 0, -0.20),  # tight on the face
		"fov_off":  -2.0,
		"key_color":  Color(1.00, 0.62, 0.46),  # warm red wash
		"key_energy": 1.25,
		"fill_color": Color(0.92, 0.42, 0.34),
		"fill_energy": 0.55,
		"shake_amp": Vector3(0.0065, 0.0065, 0),
		"shake_freq": 22.0,                   # subtle "angry tremor"
	},
	"tired": {
		"pos_off":  Vector3(0, -0.08, -0.05),
		"pitch_off": -0.04,
		"key_color":  Color(0.70, 0.78, 0.92),
		"key_energy": 0.75,
		"fill_color": Color(0.62, 0.70, 0.84),
		"fill_energy": 0.35,
		"bob_amp":  0.010, "bob_freq": 0.14,  # slow heavy drift
	},
	"nervous": {
		"pos_off":  Vector3(-0.04, 0.02, -0.06),
		"key_color":  Color(0.88, 0.92, 1.00),
		"key_energy": 0.95,
		"shake_amp": Vector3(0.003, 0.003, 0),
		"shake_freq": 8.0,                    # tremor
		"sway_amp": 0.010, "sway_freq": 0.7,  # uneasy sway
	},
	# ── Demon ────────────────────────────────────────────────────
	# Auto-selected by set_demon_mode(). Pairs with the digital-
	# static shader overlay (portrait_demon_static.gdshader) for
	# the "high-energy chaos" read — the camera does the spatial
	# unease, the shader does the signal corruption.
	"demon_chaos": {
		"pos_off":  Vector3(0.0, 0.0, -0.10),  # subtle zoom-in
		"fov_off":  -1.5,
		"key_color":  Color(0.62, 1.00, 0.66),  # sickly cathode green
		"key_energy": 1.45,
		"fill_color": Color(1.00, 0.36, 0.42),  # red signal-burn fill
		"fill_energy": 0.85,
		"back_color": Color(0.34, 0.92, 0.66),
		"back_energy": 0.70,
		"shake_amp": Vector3(0.014, 0.014, 0),
		"shake_freq": 28.0,                     # frantic jitter
		"bob_amp":  0.030, "bob_freq": 1.10,    # quick lurch
		"sway_amp": 0.025, "sway_freq": 1.30,
		"drift_yaw": 0.04,
	},
}

# ── Per-character resting-light overrides ────────────────────────
# Some characters live under a specific lighting palette that we
# want the portrait to inherit by default — e.g. Sam works the
# 11:47 PM register at the Kwik Stop, so her key/fill should read
# as sodium-buzz warmth against a cool-night back-rim, not the
# default daylight-neutral wash. Keyed by GLB basename (without
# extension). Each entry overrides the resting state captured
# in _ready, so mood offsets still compose on top.
const CHARACTER_LIGHTING := {
	"sam_miller": {
		"key_color":   Color(1.00, 0.78, 0.50),   # sodium-warm
		"key_energy":  1.20,
		"fill_color":  Color(0.96, 0.66, 0.38),   # amber bounce off counter formica
		"fill_energy": 0.55,
		"back_color":  Color(0.42, 0.58, 0.88),   # cool night through front windows
		"back_energy": 0.65,
	},
	"skip_donnelly": {
		"key_color":   Color(0.94, 0.96, 0.84),   # fluorescent canopy
		"key_energy":  1.15,
		"fill_color":  Color(0.74, 0.86, 0.92),
		"fill_energy": 0.50,
		"back_color":  Color(0.50, 0.60, 0.72),
		"back_energy": 0.55,
	},
	"rick_cosmic": {
		"key_color":   Color(0.86, 0.92, 1.00),   # CRT-blue back-issue store
		"key_energy":  1.05,
		"fill_color":  Color(0.92, 0.80, 0.66),   # incandescent shop-lamp
		"fill_energy": 0.55,
		"back_color":  Color(0.60, 0.50, 0.80),   # purple comic-rack glow
		"back_energy": 0.50,
	},
	"diego_ramos": {
		"key_color":   Color(0.98, 0.86, 0.68),   # 6:15 AM field sun
		"key_energy":  1.25,
		"fill_color":  Color(0.78, 0.82, 0.74),
		"fill_energy": 0.55,
		"back_color":  Color(0.62, 0.74, 0.92),
		"back_energy": 0.55,
	},
	"maya_daigle": {
		"key_color":   Color(0.96, 0.78, 0.82),   # bedside-lamp warm pink
		"key_energy":  0.95,
		"fill_color":  Color(0.70, 0.72, 0.92),   # screen-glow blue fill
		"fill_energy": 0.60,
		"back_color":  Color(0.40, 0.40, 0.66),
		"back_energy": 0.45,
	},
	# ── Vol 7 — Smolvud pastoral ─────────────────────────────────
	"werner": {
		"key_color":   Color(1.00, 0.84, 0.62),   # bakery firelight
		"key_energy":  1.20,
		"fill_color":  Color(0.86, 0.72, 0.56),
		"fill_energy": 0.55,
		"back_color":  Color(0.56, 0.66, 0.76),
		"back_energy": 0.50,
	},
	"aria": {
		"key_color":   Color(0.92, 0.94, 1.00),   # bell-tower morning
		"key_energy":  1.10,
		"fill_color":  Color(0.80, 0.86, 0.92),
		"fill_energy": 0.55,
		"back_color":  Color(0.74, 0.80, 0.92),
		"back_energy": 0.60,
	},
}


# Aliases collapse the EXPR_TINTS expression vocabulary down to the
# canonical 7 moods above.
const MOOD_ALIASES := {
	"excited":    "happy",
	"pleased":    "happy",
	"warm":       "happy",
	"melancholy": "sad",
	"upset":      "sad",
	"shocked":    "surprised",
	"wide":       "surprised",
	"furious":    "angry",
	"frustrated": "angry",
	"scared":     "nervous",
	"uneasy":     "nervous",
	# orphan tokens (2026-08 audit) · nearest camera/light mood
	"worried":    "nervous",
	"hurt":       "sad",
	"amused":     "happy",
	"softening":  "happy",
	"serious":    "neutral",
	"focused":    "neutral",
	"calculating": "neutral",
	"cold":       "neutral",
	"thinking":   "neutral",
	"considering": "neutral",
	"thoughtful": "neutral",
	"patient":    "neutral",
	"impressed":  "surprised",
}


func _ready() -> void:
	custom_minimum_size = Vector2(PORTRAIT_W, PORTRAIT_H)
	# Placeholder capsule lives in the .tscn so the scene is visible
	# in-editor when nothing's loaded. At runtime we always call
	# load_character() right after instancing, so hide the placeholder
	# from frame 0 — otherwise it flashes for one frame before the
	# deferred GLB load lands.
	if _placeholder != null:
		_placeholder.visible = false
	# Belt-and-suspenders: explicitly write the demon-static
	# strength to 0 on every fresh instance. The .tscn already
	# specifies this and the material is local-to-scene, but if
	# either of those guarantees breaks, this catches it before
	# the first frame renders — heroes never inherit a stale
	# strength from a sibling portrait.
	var mat: ShaderMaterial = material as ShaderMaterial
	if mat != null:
		mat.set_shader_parameter("strength", 0.0)
	# Snapshot resting state so per-mood offsets compose on top
	_rest_cam_pos = _camera.position
	_rest_cam_fov = _camera.fov
	# Aim the 3/4 hip-height camera UP at lower-chest so the figure
	# reads thigh-up at a slight heroic upward angle; bake that as the
	# resting rotation (mood pitch/yaw offsets layer on top of it).
	_camera.look_at(Vector3(0.0, 1.20, 0.0), Vector3.UP)
	_rest_cam_rot = _camera.rotation
	_rest_key_color  = _key.light_color
	_rest_key_energy = _key.light_energy
	_rest_fill_color  = _fill.light_color
	_rest_fill_energy = _fill.light_energy
	_rest_back_color  = _back.light_color
	_rest_back_energy = _back.light_energy
	_key_rest_basis = _key.transform.basis
	_apply_rig()
	# Default mood
	set_expression("neutral")
	set_process(true)


func _process(delta: float) -> void:
	_push_look(delta)
	# Continuous mood motion. We rebuild the camera transform every
	# frame from rest + mood offset + time-driven animation, so the
	# state stays clean (no drift accumulation across mood changes).
	_mood_t += delta
	var pos: Vector3 = _rest_cam_pos
	if _mood.has("pos_off"):
		var po: Vector3 = _mood["pos_off"]
		pos += po * _motion_scale
	# Bob (vertical sway)
	if _mood.has("bob_amp") and _mood.has("bob_freq"):
		var amp: float = _mood["bob_amp"]
		var freq: float = _mood["bob_freq"]
		pos.y += sin(_mood_t * freq * TAU) * amp * _motion_scale * MOTION_GAIN
	_camera.position = pos
	# Pitch + yaw — start from defaults, layer offsets + animation
	# The old moods tilted the camera down for sad/tired — built for the
	# wide frame; in a tighter shot it cropped the head off (the 2026-10-01
	# sheet). The director owns the angle now: the mood's tilt fades out
	# as the shot tightens (full at wide, none from the medium close-up in).
	var tilt_keep: float = clampf((_motion_scale - 0.5) * 2.0, 0.0, 1.0)
	var pitch: float = float(_mood.get("pitch_off", 0.0)) * tilt_keep
	var yaw: float = _mood.get("yaw_off", 0.0)
	# angular motion reads against the lens: the same radian is twice the
	# screen on half the field of view
	var ang: float = MOTION_GAIN * _rest_cam_fov / MOTION_REF_FOV
	# Sway (horizontal yaw)
	if _mood.has("sway_amp") and _mood.has("sway_freq"):
		yaw += sin(_mood_t * float(_mood["sway_freq"]) * TAU) * float(_mood["sway_amp"]) * ang
	# Drift (continuous slow yaw)
	if _mood.has("drift_yaw"):
		yaw += sin(_mood_t * 0.4) * float(_mood["drift_yaw"]) * 4.0 * ang
	# Shake: a startle that dies away — only the demon keeps trembling
	if _mood.has("shake_amp") and _mood.has("shake_freq"):
		var sa: Vector3 = _mood["shake_amp"]
		var sf: float = _mood["shake_freq"]
		var env: float = 1.0 if _mood_id == "demon_chaos" else exp(-_mood_t * STARTLE_DECAY)
		# Lissajous-ish jitter so the shake doesn't look periodic
		pitch += sin(_mood_t * sf * TAU * 1.07) * sa.x * ang * env
		yaw   += sin(_mood_t * sf * TAU * 0.93) * sa.y * ang * env
	_camera.rotation = Vector3(_rest_cam_rot.x + pitch, _rest_cam_rot.y + yaw, _rest_cam_rot.z)
	# FOV
	var fov_off: float = float(_mood.get("fov_off", 0.0))
	var fov: float = _rest_cam_fov + fov_off * _motion_scale
	if fov < 5.0:
		fov = 5.0
	_camera.fov = fov


# ── Public API ────────────────────────────────────────────────────
func load_character(glb_path: String, expression: String = "") -> bool:
	if glb_path == _loaded_glb_path and _current_character != null:
		if expression != "":
			set_expression(expression)
		return true
	# Tear down any previously-loaded model
	if _current_character != null and is_instance_valid(_current_character):
		_current_character.queue_free()
	_current_character = null
	# Hide placeholder (the editor-default capsule) once we actually
	# have something to render
	if _placeholder != null:
		_placeholder.visible = false
	var ps: PackedScene = load(glb_path) as PackedScene
	if ps == null:
		push_warning("[Portrait3D] Could not load GLB at %s" % glb_path)
		return false
	var inst: Node = ps.instantiate()
	if inst == null:
		return false
	_anchor.add_child(inst)
	_current_character = inst as Node3D
	if _current_character == null:
		# Top node wasn't a Node3D — wrap it
		var wrap := Node3D.new()
		_anchor.add_child(wrap)
		inst.reparent(wrap)
		_current_character = wrap
	_loaded_glb_path = glb_path
	# Auto-orient + auto-scale to the portrait's target framing
	_orient_and_scale_character(_current_character)
	_shading = _resolve_shading(glb_path)
	_apply_rig()
	_matte_materials(_current_character)
	_neck_y = _measure_neck(_current_character)
	_head_xz = _measure_head(_current_character, _neck_y) if _neck_y > 0.0 else Vector2.ZERO
	_eyes_cache = -1.0
	_eyes_measured = _measure_eyes(_current_character, _neck_y) if _neck_y > 0.0 else -1.0
	_albedo_cache.clear()
	# Per-character lighting palette (e.g. Sam under sodium-buzz
	# Kwik Stop fluorescents). Rewrites the resting key/fill/back
	# state so all mood deltas compose on top of the right palette.
	_apply_character_lighting(glb_path)
	# Frame the new figure with the current shot (the director's last
	# order, or the medium a portrait opens on)
	set_shot(_shot_size, _shot_angle)
	# Re-apply the current mood so any "use rest value" fallback
	# picks up the freshly-installed character resting palette
	# instead of the previous character's leftover lights.
	var reapply: String = expression if expression != "" else _mood_id
	if reapply == "":
		reapply = "neutral"
	set_expression(reapply)
	return true


func _apply_character_lighting(glb_path: String) -> void:
	var base: String = glb_path.get_file().get_basename().to_lower()
	# GNM-generated portrait variants ("<name>_gnm.glb", from
	# tools/portraits/gnm_portrait.py) inherit their character's rig.
	if base.ends_with("_gnm"):
		base = base.substr(0, base.length() - 4)
	if not CHARACTER_LIGHTING.has(base):
		return
	var lp: Dictionary = CHARACTER_LIGHTING[base]
	if lp.has("key_color"):   _rest_key_color  = lp["key_color"]
	if lp.has("key_energy"):  _rest_key_energy = float(lp["key_energy"])
	if lp.has("fill_color"):  _rest_fill_color  = lp["fill_color"]
	if lp.has("fill_energy"): _rest_fill_energy = float(lp["fill_energy"]) * LEGACY_FILL_SCALE
	if lp.has("back_color"):  _rest_back_color  = lp["back_color"]
	if lp.has("back_energy"): _rest_back_energy = float(lp["back_energy"])
	print("[Portrait3D] character lighting applied for %s" % base)


## A DirectionalLight3D's basis shining FROM (yaw, elev) toward the figure.
static func _light_basis(yaw: float, elev: float) -> Basis:
	var from := Vector3(sin(yaw) * cos(elev), sin(elev), cos(yaw) * cos(elev))
	# a light shines down its -Z: +Z points back at where it stands
	var z: Vector3 = from.normalized()
	var x: Vector3 = Vector3.UP.cross(z).normalized()
	var y: Vector3 = z.cross(x).normalized()
	return Basis(x, y, z)


## Place the three lights (RIG, the character's "rig", a tool override)
## and make them the resting state the moods and the takes compose on.
func _apply_rig() -> void:
	var r: Dictionary = RIG.duplicate()
	var sh: Dictionary = _shading if not _shading.is_empty() else {}
	var cr: Dictionary = sh.get("rig", {})
	for k: String in cr:
		r[k] = cr[k]
	for k: String in rig_override:
		r[k] = rig_override[k]
	_key.transform.basis = _light_basis(float(r["key_yaw"]), float(r["key_elev"]))
	_fill.transform.basis = _light_basis(float(r["fill_yaw"]), float(r["fill_elev"]))
	_back.transform.basis = _light_basis(float(r["rim_yaw"]), float(r["rim_elev"]))
	_key_rest_basis = _key.transform.basis
	_rest_key_energy = float(r["key_energy"])
	_rest_fill_energy = float(r["fill_energy"])
	_rest_fill_color = r["fill_color"]
	_rest_back_energy = float(r["rim_energy"])


func set_expression(expression: String) -> void:
	# Drive a per-mood camera + lighting + motion override on top
	# of the resting framing. Normalizes via MOOD_ALIASES (so
	# "furious" / "frustrated" both map to "angry", etc.), then
	# applies lights immediately and stores motion state for
	# _process() to animate.
	var normalized: String = expression.strip_edges().to_lower()
	if normalized == "":
		normalized = "neutral"
	if MOOD_ALIASES.has(normalized):
		normalized = MOOD_ALIASES[normalized]
	# Demons don't perform moods — they leak. Any incoming expression
	# is collapsed to the chaos preset (the signal-corruption shader
	# does the actual emotional read).
	if _demon_mode:
		normalized = "demon_chaos"
	# Reset mood timer ONLY on actual change — same-mood updates
	# preserve the existing animation phase so a re-trigger doesn't
	# snap the camera
	if normalized != _mood_id:
		_mood_t = 0.0
	_mood_id = normalized
	_mood = MOOD_TABLE.get(normalized, {})
	# Apply light overrides immediately. Missing keys fall back to
	# the resting values (so e.g. surprised doesn't override fill).
	var kc: Color = _mood.get("key_color",  _rest_key_color)
	var ke: float = float(_mood.get("key_energy", _rest_key_energy))
	var fc: Color = _mood.get("fill_color",  _rest_fill_color)
	var fe: float = float(_mood.get("fill_energy", _rest_fill_energy / LEGACY_FILL_SCALE)) * LEGACY_FILL_SCALE
	var bc: Color = _mood.get("back_color",  _rest_back_color)
	var be: float = float(_mood.get("back_energy", _rest_back_energy))
	if not _scene.is_empty() and not _demon_mode:
		var sk: Color = _scene.get("key", kc)
		var sa: Color = _scene.get("ambient", fc)
		var lvl: float = float(_scene.get("level", 1.0))
		kc = kc.lerp(sk, SCENE_MIX)
		fc = fc.lerp(sa, SCENE_MIX)
		# the rim CONTRASTS: cool against a warm room, warm against a cool one
		bc = Color(0.52, 0.70, 0.92) if sk.r > sk.b else Color(0.98, 0.74, 0.46)
		var lv: float = clampf(lvl, 0.7, 1.25)
		ke *= lv
		fe *= lv
		be *= clampf(1.6 - lvl * 0.5, 0.7, 1.3)   # dim rooms want more rim, not less
	_key.light_color  = kc
	_key.light_energy = ke * float(_roll.get("key_e", 1.0))
	_fill.light_color  = fc
	_fill.light_energy = fe * float(_roll.get("fill_e", 1.0))
	_back.light_color  = bc
	_back.light_energy = be * float(_roll.get("back_e", 1.0))
	_compute_look()


## The look the current mood + room ask for (eased toward in _process).
func _compute_look() -> void:
	var t: Dictionary = LOOK_BASE.duplicate()
	# (2026-10-13) the character's face-friendly look, under the mood's deltas
	var sh: Dictionary = _shading if not _shading.is_empty() else SHADING_DEFAULT
	var shl: Dictionary = sh.get("look", {})
	for k: String in shl:
		t[k] = float(shl[k])
	var md: Dictionary = MOOD_LOOK.get(_mood_id, {})
	for k: String in md:
		t[k] = float(t.get(k, 0.0)) + float(md[k])
	var rim := Color(0.70, 0.85, 1.0)
	var shadow := Color(0.10, 0.09, 0.14)
	if not _scene.is_empty():
		var sk: Color = _scene.get("key", Color(1, 1, 1))
		var sa: Color = _scene.get("ambient", Color(0.4, 0.4, 0.4))
		# the room's warmth carries onto the face; its key lights the rim
		t["look_temp"] = float(t["look_temp"]) + (sk.r - sk.b) * 0.6
		rim = sk.lerp(Color(1, 1, 1), 0.35)
		shadow = Color(sa.r * 0.35, sa.g * 0.35, sa.b * 0.40)
	# a warm room AND an angry line must not burn the face orange (the
	# first render did): the temperature stays inside ±0.55
	t["look_temp"] = clampf(float(t["look_temp"]), -0.55, 0.55)
	_look_target = t
	_rim_target = rim
	_shadow_target = shadow
	if _look_now.is_empty():
		_look_now = t.duplicate()
		_rim_now = rim


func _push_look(delta: float) -> void:
	var mat: ShaderMaterial = material as ShaderMaterial
	if mat == null or _look_target.is_empty():
		return
	if _demon_mode or not _look_on:
		mat.set_shader_parameter("look", 0.0)
		return
	var k: float = 1.0 - exp(-LOOK_EASE * delta)
	for key: String in _look_target:
		var now: float = float(_look_now.get(key, _look_target[key]))
		now = lerpf(now, float(_look_target[key]), k)
		_look_now[key] = now
		mat.set_shader_parameter(key, now)
	_rim_now = _rim_now.lerp(_rim_target, k)
	mat.set_shader_parameter("look_rim_color", _rim_now)
	mat.set_shader_parameter("look_shadow", _shadow_target)
	var sh: Dictionary = _shading if not _shading.is_empty() else SHADING_DEFAULT
	mat.set_shader_parameter("look", float(sh.get("look_amount", 1.0)))


## Jump the eased look straight to its target (a still capture).
func snap_look() -> void:
	_look_now = _look_target.duplicate()
	_rim_now = _rim_target
	_push_look(0.0)


## Clean renders (a tool, a debug comparison): the look off.
func set_look_enabled(on: bool) -> void:
	_look_on = on


func set_demon_mode(enabled: bool) -> void:
	# Flip the SubViewportContainer's demon-static shader on/off and
	# pin the mood to demon_chaos. Heroes get strength=0 (pass-
	# through); demons get strength=1 (full digital-static + RGB
	# tear + scanline glitch + signal-drop bands).
	_demon_mode = enabled
	var mat: ShaderMaterial = material as ShaderMaterial
	if mat != null:
		mat.set_shader_parameter("strength", 1.0 if enabled else 0.0)
	# Re-apply expression so the demon_chaos route fires immediately
	set_expression(_mood_id)


## Cut to a shot: size in SHOT_FRAMES, angle eye | low | high | dutch.
## Rebuilds the resting camera; mood motion layers on top, scaled to
## the frame so a close-up does not shake like a wide.
func set_shot(size: String, angle: String = "eye", seed: int = -1) -> void:
	if not SHOT_FRAMES.has(size):
		size = "medium"
	if not ANGLE_ELEVATION.has(angle):
		angle = "eye"
	var changed: bool = size != _shot_size or angle != _shot_angle or _roll.is_empty()
	_shot_size = size
	_shot_angle = angle
	if _camera == null:
		return
	# a new shot (or an asked-for new take) rolls inside VARY; a held
	# shot keeps its roll, so the frame does not twitch line to line
	if changed or seed >= 0:
		_roll_take(seed)
	var f: Dictionary = SHOT_FRAMES[size]
	var h: float = TARGET_HEIGHT_M
	var b: float = float(f["b"]) * h
	var t: float = float(f["t"]) * h
	if _neck_y > 0.0 and FACE_FRAMES.has(size):
		var ff: Dictionary = FACE_FRAMES[size]
		var fh: float = float(ff["h"])
		# the eyes at eye_at from the top; never air over the crown (sheet
		# 42: Jimmy and Thomas sat low under a band of empty headroom)
		t = minf(_eyes_y() + float(ff["eye_at"]) * fh, TARGET_HEIGHT_M + float(ff["cap"]))
		b = t - fh
	var frame_h: float = t - b
	var fov: float = float(f["fov"]) + float(_roll.get("fov", 0.0))
	var dist: float = (frame_h * 0.5) / tan(deg_to_rad(fov * 0.5))
	var aim: float = float(AIM.get(size, 0.0)) if _neck_y > 0.0 else 0.0
	var target := Vector3(_head_xz.x * aim, (b + t) * 0.5 + float(_roll.get("frame_y", 0.0)) * frame_h, _head_xz.y * aim)
	var elev: float = float(ANGLE_ELEVATION[angle]) + float(_roll.get("elev", 0.0))
	var yaw: float = YAW_THREE_QUARTER + float(_roll.get("yaw", 0.0))
	var dir := Vector3(sin(yaw) * cos(elev), sin(elev), cos(yaw) * cos(elev))
	_camera.position = target + dir * dist
	_camera.fov = fov
	_camera.look_at(target, Vector3.UP)
	if angle == "dutch":
		_camera.rotate_object_local(Vector3(0, 0, 1), float(_roll.get("dutch", DUTCH_ROLL)))
	# the key swings round the head with the take
	_key.transform.basis = Basis(Vector3.UP, float(_roll.get("key_yaw", 0.0))) * Basis(Vector3.RIGHT, float(_roll.get("key_pitch", 0.0))) * _key_rest_basis
	_apply_grade()
	set_expression(_mood_id)
	_rest_cam_pos = _camera.position
	_rest_cam_rot = _camera.rotation
	_rest_cam_fov = fov
	_motion_scale = frame_h / WIDE_FRAME_H


func get_shot() -> String:
	return _shot_size


## Where the face lands in the frame (tools/PortraitCastSheet): the eye
## line and the neck as fractions of the viewport's height from the top,
## and the head's height (crown to neck) as a fraction of it.
func frame_report() -> Dictionary:
	if _camera == null or _neck_y <= 0.0:
		return {}
	var vh: float = float(_viewport.size.y)
	if vh <= 0.0:
		return {}
	var hx: float = _head_xz.x
	var hz: float = _head_xz.y
	var eye: Vector2 = _camera.unproject_position(Vector3(hx, _eyes_y(), hz))
	var neck: Vector2 = _camera.unproject_position(Vector3(hx, _neck_y, hz))
	var crown: Vector2 = _camera.unproject_position(Vector3(hx, TARGET_HEIGHT_M, hz))
	return {
		"eye": snappedf(eye.y / vh, 0.001), "neck": snappedf(neck.y / vh, 0.001),
		"head": snappedf((neck.y - crown.y) / vh, 0.001), "eye_x": snappedf(eye.x / float(_viewport.size.x), 0.001),
	}


## The locale's light (Background3D.get_scene_light): the portrait's key
## leans toward it, the rim contrasts with it, the grade follows its level.
func set_scene_light(light: Dictionary) -> void:
	_scene = light
	_apply_grade()
	set_expression(_mood_id)


func _roll_take(seed: int) -> void:
	if seed >= 0:
		_rng.seed = seed
	else:
		_rng.randomize()
	var dsign: float = 1.0 if _rng.randf() < 0.5 else -1.0
	_roll = {
		"yaw": _rng.randf_range(-VARY["yaw"], VARY["yaw"]),
		"elev": _rng.randf_range(-VARY["elev"], VARY["elev"]),
		"frame_y": _rng.randf_range(-VARY["frame_y"], VARY["frame_y"]),
		"fov": _rng.randf_range(-VARY["fov"], VARY["fov"]),
		"dutch": dsign * _rng.randf_range(VARY["dutch_min"], VARY["dutch_max"]),
		"key_yaw": _rng.randf_range(-VARY["key_yaw"], VARY["key_yaw"]),
		"key_pitch": _rng.randf_range(-VARY["key_pitch"], VARY["key_pitch"]),
		"key_e": 1.0 + _rng.randf_range(-VARY["energy"], VARY["energy"]),
		"fill_e": 1.0 + _rng.randf_range(-VARY["energy"], VARY["energy"]),
		"back_e": 1.0 + _rng.randf_range(-VARY["energy"], VARY["energy"]),
		"contrast": _rng.randf_range(VARY["contrast"][0], VARY["contrast"][1]),
		"saturation": _rng.randf_range(VARY["saturation"][0], VARY["saturation"][1]),
	}


## The portrait's grade: the take's contrast and saturation, brightness
## following the room (a dark locale does not get a bright face).
func _apply_grade() -> void:
	var we: WorldEnvironment = get_node_or_null("SubViewport/WorldEnvironment") as WorldEnvironment
	if we == null or we.environment == null:
		return
	var env: Environment = we.environment
	env.adjustment_enabled = true
	env.adjustment_contrast = float(_roll.get("contrast", 1.05))
	env.adjustment_saturation = float(_roll.get("saturation", 1.05))
	var lvl: float = float(_scene.get("level", 1.0))
	env.adjustment_brightness = clampf(0.86 + lvl * 0.12, 0.9, 1.06)
	if _scene.has("ambient"):
		var amb: Color = _scene["ambient"]
		env.ambient_light_color = Color(0.42, 0.38, 0.34).lerp(amb, SCENE_MIX)


func get_viewport_texture() -> Texture2D:
	return _viewport.get_texture()


# ── Internal: orient + scale the loaded GLB ──────────────────────
func _orient_and_scale_character(root: Node3D) -> void:
	# Measure the bounding box, figure out which axis is "up,"
	# ROTATE the model if it isn't Y-up already, then scale so the
	# height axis hits TARGET_HEIGHT_M, then drop so feet land at
	# the anchor's Y=0 plane.
	var mesh_objs: Array[Node] = _collect_mesh_instances(root)
	if mesh_objs.is_empty():
		return
	# First-pass AABB measurement in root-local space
	var aabb_min: Vector3 = Vector3.INF
	var aabb_max: Vector3 = -Vector3.INF
	for n: Node in mesh_objs:
		var mi: MeshInstance3D = n as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		var local_aabb: AABB = mi.mesh.get_aabb()
		var xform: Transform3D = root.global_transform.affine_inverse() * mi.global_transform
		var world_aabb: AABB = xform * local_aabb
		aabb_min = aabb_min.min(world_aabb.position)
		aabb_max = aabb_max.max(world_aabb.position + world_aabb.size)
	if aabb_min == Vector3.INF:
		return
	var ext: Vector3 = aabb_max - aabb_min
	# Pick the largest extent — that's the "height" axis. If it's
	# not already Y, rotate the model so it stands upright.
	var max_axis: int = 1
	if ext.x > ext.y and ext.x > ext.z: max_axis = 0
	elif ext.z > ext.y and ext.z > ext.x: max_axis = 2
	print("[Portrait3D] orient — initial AABB ext=(%.2f, %.2f, %.2f) " % [ext.x, ext.y, ext.z]
		+ "longest axis=%s" % ["X", "Y", "Z"][max_axis])
	# Rotate if needed. We rotate the root node, then re-measure
	# the AABB in the new orientation before scaling + translating.
	if max_axis == 2:
		# Z-up → Y-up: rotate -90° about X (tip the head from +Z to +Y)
		root.rotation = Vector3(-PI / 2.0, 0, 0)
		print("[Portrait3D] orient — Z-up detected, rotated -90° about X")
	elif max_axis == 0:
		# X-up (lying sideways on +X): rotate +90° about Z
		root.rotation = Vector3(0, 0, PI / 2.0)
		print("[Portrait3D] orient — X-up detected, rotated +90° about Z")
	# Re-measure post-rotation
	aabb_min = Vector3.INF
	aabb_max = -Vector3.INF
	for n in mesh_objs:
		var mi2: MeshInstance3D = n as MeshInstance3D
		if mi2 == null or mi2.mesh == null:
			continue
		var local_aabb2: AABB = mi2.mesh.get_aabb()
		var xform2: Transform3D = root.transform.affine_inverse() * (root.transform * mi2.transform)
		# Actually simpler: combine the rotation into the AABB transform
		var world_aabb2: AABB = (root.transform * mi2.transform) * local_aabb2
		# Re-root by undoing root.position (which is still zero at this point)
		aabb_min = aabb_min.min(world_aabb2.position)
		aabb_max = aabb_max.max(world_aabb2.position + world_aabb2.size)
	if aabb_min == Vector3.INF:
		return
	ext = aabb_max - aabb_min
	# After rotation, Y should be the long axis
	var current_h: float = ext.y
	if current_h < 0.001:
		# Fall back to longest if rotation didn't land cleanly
		current_h = max(ext.x, max(ext.y, ext.z))
	var s: float = TARGET_HEIGHT_M / current_h
	root.scale = Vector3(s, s, s)
	# Drop so feet land at anchor Y=0; centre horizontally on X/Z
	var bot_y: float = aabb_min.y * s
	root.position = Vector3(-((aabb_min.x + aabb_max.x) / 2.0) * s,
	                         -bot_y,
	                         -((aabb_min.z + aabb_max.z) / 2.0) * s)
	print("[Portrait3D] orient — scale=%.3f, position=(%.2f, %.2f, %.2f)"
		% [s, root.position.x, root.position.y, root.position.z])


## The neck's height in the anchor's space: the narrowest horizontal slice
## of the mesh (its X extent) between 74 % and 90 % of the figure's
## height, below the head. -1 when it cannot be read (no mesh data).
func _measure_neck(root: Node3D) -> float:
	var h: float = TARGET_HEIGHT_M
	# 74-90 %: below the crown's taper (which would read as "narrow"), above
	# the A-pose arms' shoulder line
	var lo: float = 0.74 * h
	var hi: float = 0.90 * h
	var bins: int = 36
	var mins: PackedFloat32Array = PackedFloat32Array()
	var maxs: PackedFloat32Array = PackedFloat32Array()
	var counts: PackedInt32Array = PackedInt32Array()
	mins.resize(bins)
	maxs.resize(bins)
	counts.resize(bins)
	for i in bins:
		mins[i] = INF
		maxs[i] = -INF
	var seen: int = 0
	for n: Node in _collect_mesh_instances(root):
		var mi: MeshInstance3D = n as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		var xf: Transform3D = _anchor.global_transform.affine_inverse() * mi.global_transform
		for si in mi.mesh.get_surface_count():
			var arrays: Array = mi.mesh.surface_get_arrays(si)
			if arrays.size() <= Mesh.ARRAY_VERTEX:
				continue
			var verts: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			var stride: int = maxi(1, verts.size() / 60000)
			var vi: int = 0
			while vi < verts.size():
				var p: Vector3 = xf * verts[vi]
				vi += stride
				if p.y < lo or p.y >= hi:
					continue
				var bi: int = int((p.y - lo) / (hi - lo) * bins)
				mins[bi] = minf(mins[bi], p.x)
				maxs[bi] = maxf(maxs[bi], p.x)
				counts[bi] += 1
				seen += 1
	if seen < 200:
		return -1.0
	# the narrowest slice below the head: search from the shoulders up and
	# stop once the width has grown again past the minimum (the head)
	var best_i: int = -1
	var best_w: float = INF
	for i in bins:
		# a slice needs enough samples to have a width, and a neck is never
		# under 5 cm (a lone vertex read as "0 m wide" — john_frank, 2026-10-01)
		if counts[i] < 12:
			continue
		var w: float = maxs[i] - mins[i]
		if w < 0.05:
			continue
		if w < best_w:
			best_w = w
			best_i = i
	if best_i < 0:
		return -1.0
	var neck: float = lo + (float(best_i) + 0.5) / bins * (hi - lo)
	print("[Portrait3D] neck at %.2f m (width %.2f m)" % [neck, best_w])
	return neck


## The eye line's height for the loaded hero. The sheet-43 table was read
## by eye and wins while the model is the one it was read from; a hero
## not in it (most of the Drive cast, 2026-10-13: "lots don't line up
## right"), or one whose model was replaced since (the measured eyes sit
## > 3 cm from the table's), takes the eyes measured from its texture.
func _eyes_y() -> float:
	if _eyes_cache > 0.0:
		return _eyes_cache
	var key: String = _loaded_glb_path.get_file().get_basename()
	var y: float = _neck_y + EYES_OVER_NECK
	if SHEET43_ECU_EYE.has(key):
		var centre: float = minf(_neck_y + 0.095, TARGET_HEIGHT_M - 0.105) + 0.0029
		y = centre + (0.5 - float(SHEET43_ECU_EYE[key])) * 0.21
		if _eyes_measured > 0.0 and absf(_eyes_measured - y) > 0.03:
			print("[Portrait3D] %s: measured eyes %.3f m, table %.3f m — the model changed; using the measure" % [key, _eyes_measured, y])
			y = _eyes_measured
	elif _eyes_measured > 0.0:
		y = _eyes_measured
	_eyes_cache = y
	return y


## The eye line read from the face's own texture (2026-10-13): the white
## of the eyes. Face-front vertices either side of the nose, in the band
## from just over the neck to the brow, are binned by height; the bin
## with the most sclera (bright, unsaturated against the face's own skin)
## is the eye line. Sunglasses have no sclera — the darkest band there is
## the lenses. -1 when the texture or the band cannot be read.
func _measure_eyes(root: Node3D, neck: float) -> float:
	var lo: float = neck + 0.03
	var hi: float = neck + 0.21
	var bins: int = 36                       # ~5 mm
	var hx: float = _head_xz.x
	# pass 1: the face's front (max z) per bin, near the centre line
	var front := PackedFloat32Array()
	front.resize(bins)
	front.fill(-INF)
	var pts: Array = []                      # [bin, z, dx, uv, image]
	for n: Node in _collect_mesh_instances(root):
		var mi: MeshInstance3D = n as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		var xf: Transform3D = _anchor.global_transform.affine_inverse() * mi.global_transform
		for si in mi.mesh.get_surface_count():
			var img: Image = _albedo_image(mi, si)
			if img == null:
				continue
			var arrays: Array = mi.mesh.surface_get_arrays(si)
			if arrays.size() <= Mesh.ARRAY_TEX_UV or arrays[Mesh.ARRAY_TEX_UV] == null:
				continue
			var verts: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			var uvs: PackedVector2Array = arrays[Mesh.ARRAY_TEX_UV]
			if uvs.size() != verts.size():
				continue
			for vi in verts.size():
				var p: Vector3 = xf * verts[vi]
				if p.y < lo or p.y >= hi:
					continue
				var dx: float = absf(p.x - hx)
				if dx > 0.06:
					continue
				var bi: int = int((p.y - lo) / (hi - lo) * bins)
				front[bi] = maxf(front[bi], p.z)
				pts.append([bi, p.z, dx, uvs[vi], img])
	if pts.size() < 150:
		return -1.0
	# per bin: the lateral band (where the eyes are, 1.4-5 cm either side
	# of the centre line) and the centre (the nose bridge, under 1 cm)
	var lat_n := PackedFloat32Array()
	var lat_w := PackedFloat32Array()
	var lat_d := PackedFloat32Array()
	var mid_n := PackedFloat32Array()
	var mid_w := PackedFloat32Array()
	var mid_d := PackedFloat32Array()
	for arr: PackedFloat32Array in [lat_n, lat_w, lat_d, mid_n, mid_w, mid_d]:
		arr.resize(bins)
		arr.fill(0.0)
	var lums: Array[float] = []
	var samples: Array = []
	for pv: Variant in pts:
		var pt: Array = pv
		var bi: int = int(pt[0])
		if float(pt[1]) < front[bi] - 0.03:
			continue                         # behind the face's front: hair, ear, the far cheek
		var img: Image = pt[4]
		var uv: Vector2 = pt[3]
		var px := Vector2i(clampi(int(fposmod(uv.x, 1.0) * img.get_width()), 0, img.get_width() - 1),
				clampi(int(fposmod(uv.y, 1.0) * img.get_height()), 0, img.get_height() - 1))
		var c: Color = img.get_pixelv(px)
		samples.append([bi, float(pt[2]), c])
		if float(pt[2]) < 0.05:
			lums.append(c.get_luminance())
	if samples.size() < 100 or lums.is_empty():
		return -1.0
	lums.sort()
	var skin: float = lums[lums.size() / 2]  # the face's own skin, its median
	for sv: Variant in samples:
		var s: Array = sv
		var bi: int = int(s[0])
		var dx: float = float(s[1])
		var c: Color = s[2]
		var l: float = c.get_luminance()
		var is_w: float = 1.0 if (c.s < 0.25 and l > maxf(skin * 1.15, 0.30)) else 0.0
		var is_d: float = 1.0 if l < skin * 0.40 else 0.0
		if dx >= 0.014 and dx <= 0.05:
			lat_n[bi] += 1.0
			lat_w[bi] += is_w
			lat_d[bi] += is_d
		elif dx < 0.01:
			mid_n[bi] += 1.0
			mid_w[bi] += is_w
			mid_d[bi] += is_d
	# a 3-bin (15 mm) window. An eye is white AND dark beside the nose —
	# sclera against iris and lashes — and not white on the bridge: grey
	# hair, a forehead highlight, a hat brim are white with no dark, or
	# white all the way across. Dark beside the nose AND on the bridge is
	# a pair of shades.
	var best_i: int = -1
	var best: float = 0.0
	var shade_i: int = -1
	var shade: float = 0.0
	for i in range(1, bins - 1):
		var ln: float = lat_n[i - 1] + lat_n[i] + lat_n[i + 1]
		var mn: float = mid_n[i - 1] + mid_n[i] + mid_n[i + 1]
		if ln < 6.0:
			continue
		var lw: float = (lat_w[i - 1] + lat_w[i] + lat_w[i + 1]) / ln
		var ld: float = (lat_d[i - 1] + lat_d[i] + lat_d[i + 1]) / ln
		var mw: float = (mid_w[i - 1] + mid_w[i] + mid_w[i + 1]) / mn if mn >= 2.0 else 0.0
		var md: float = (mid_d[i - 1] + mid_d[i] + mid_d[i + 1]) / mn if mn >= 2.0 else 0.0
		var score: float = sqrt(lw * ld) - mw * 1.5
		# where eyes can be: 6-19 cm over the narrowest slice (the mouth
		# sits under it, the hairline over it); shades 6-15 cm (the hair)
		var over: float = lo + (float(i) + 0.5) / bins * (hi - lo) - neck
		if over < 0.06 or over > 0.19:
			score = 0.0
		if _eyes_debug:
			print("   eyes bin %.3f  lat n%3d w%.2f d%.2f | mid n%3d w%.2f d%.2f | score %.2f" % [lo + (i + 0.5) / bins * (hi - lo) - neck, int(ln), lw, ld, int(mn), mw, md, score])
		if score > best:
			best = score
			best_i = i
		var sd: float = minf(ld, md) if over <= 0.15 else 0.0
		if sd > shade:
			shade = sd
			shade_i = i
	var pick: int = -1
	if best_i >= 0 and best >= 0.05:
		pick = best_i
	elif shade_i >= 0 and shade >= 0.4:
		pick = shade_i                       # sunglasses
	if pick < 0:
		return -1.0
	var y: float = lo + (float(pick) + 0.5) / bins * (hi - lo)
	print("[Portrait3D] eyes at %.3f m (%.2f over the neck; sclera %.2f, shades %.2f)" % [y, y - neck, best, shade])
	return y


## A surface's albedo as a readable Image (decompressed; cached per texture).
func _albedo_image(mi: MeshInstance3D, si: int) -> Image:
	var mat: Material = mi.mesh.surface_get_material(si)
	var bm: BaseMaterial3D = mat as BaseMaterial3D
	if bm == null or bm.albedo_texture == null:
		return null
	var tex: Texture2D = bm.albedo_texture
	var rid_key: int = tex.get_instance_id()
	if _albedo_cache.has(rid_key):
		return _albedo_cache[rid_key] as Image
	var img: Image = tex.get_image()
	if img == null or img.is_empty():
		return null
	if img.is_compressed():
		if img.decompress() != OK:
			return null
	# a quarter of the texture is plenty for a 5 mm bin
	if img.get_width() > 1024:
		img.resize(img.get_width() / 2, img.get_height() / 2, Image.INTERPOLATE_BILINEAR)
	_albedo_cache[rid_key] = img
	return img


## Where the head is off the figure's vertical axis, in the anchor's x/z:
## the middle of the x extent and the face's front less half a head's
## depth (the back of the head is hair, and long hair would drag a
## mid-depth point behind the skull). Read in the band from just over the
## neck to the brow. Clamped to 15 cm; zero when the band is too sparse.
func _measure_head(root: Node3D, neck: float) -> Vector2:
	var lo: float = neck + 0.06
	var hi: float = neck + 0.20
	var min_x: float = INF
	var max_x: float = -INF
	var max_z: float = -INF
	var seen: int = 0
	for n: Node in _collect_mesh_instances(root):
		var mi: MeshInstance3D = n as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		var xf: Transform3D = _anchor.global_transform.affine_inverse() * mi.global_transform
		for si in mi.mesh.get_surface_count():
			var arrays: Array = mi.mesh.surface_get_arrays(si)
			if arrays.size() <= Mesh.ARRAY_VERTEX:
				continue
			var verts: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			var stride: int = maxi(1, verts.size() / 60000)
			var vi: int = 0
			while vi < verts.size():
				var p: Vector3 = xf * verts[vi]
				vi += stride
				if p.y < lo or p.y >= hi:
					continue
				min_x = minf(min_x, p.x)
				max_x = maxf(max_x, p.x)
				max_z = maxf(max_z, p.z)
				seen += 1
	if seen < 60:
		return Vector2.ZERO
	var head := Vector2((min_x + max_x) * 0.5, max_z - 0.10)
	head = head.limit_length(0.15)
	print("[Portrait3D] head at x %.3f z %.3f m off the axis" % [head.x, head.y])
	return head


## The Meshy models arrive glossy — roughness and specular read as
## plastic before any post pass sees them (the Deck, 2026-10-02: "less
## plastic"). Each surface gets a matte copy of its material: full
## roughness, no metal, a whisper of specular. Colour and texture keep.
func _resolve_shading(glb_path: String) -> Dictionary:
	var base: String = glb_path.get_file().get_basename().to_lower()
	if base.ends_with("_gnm"):
		base = base.substr(0, base.length() - 4)
	var sh: Dictionary = SHADING_DEFAULT.duplicate(true)
	if CHARACTER_SHADING.has(base):
		var over: Dictionary = CHARACTER_SHADING[base]
		for k: String in over:
			if k == "look":
				var lk: Dictionary = sh["look"]
				var lo: Dictionary = over["look"]
				for kk: String in lo:
					lk[kk] = lo[kk]
			else:
				sh[k] = over[k]
	for k: String in shading_override:
		sh[k] = shading_override[k]
	return sh


func _matte_materials(root: Node3D) -> void:
	var sh: Dictionary = _shading if not _shading.is_empty() else SHADING_DEFAULT
	for n: Node in _collect_mesh_instances(root):
		var mi: MeshInstance3D = n as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		for si in mi.mesh.get_surface_count():
			var src: Material = mi.get_active_material(si)
			var bm: BaseMaterial3D = src as BaseMaterial3D
			if bm == null:
				continue
			var m: BaseMaterial3D = bm.duplicate() as BaseMaterial3D
			m.roughness = 1.0
			m.metallic = 0.0
			m.metallic_specular = 0.12
			m.clearcoat_enabled = false
			# (2026-10-13) per-character shading: see SHADING_DEFAULT
			if m.normal_enabled:
				m.normal_scale = float(sh.get("normal_scale", 0.35))
			if not bool(sh.get("emission", false)):
				m.emission_enabled = false
			if bool(sh.get("wrap", true)):
				m.diffuse_mode = BaseMaterial3D.DIFFUSE_LAMBERT_WRAP
			if bool(sh.get("skin_shader", true)) and m.albedo_texture != null:
				mi.set_surface_override_material(si, _skin_material(m, sh))
				continue
			mi.set_surface_override_material(si, m)


## The portrait skin material (portrait_skin.gdshader) from the GLB's own
## textures and this character's shading values.
func _skin_material(src: BaseMaterial3D, sh: Dictionary) -> ShaderMaterial:
	var sm := ShaderMaterial.new()
	sm.shader = SKIN_SHADER
	sm.set_shader_parameter("albedo_tex", src.albedo_texture)
	var has_n: bool = src.normal_enabled and src.normal_texture != null
	sm.set_shader_parameter("has_normal", has_n)
	if has_n:
		sm.set_shader_parameter("normal_tex", src.normal_texture)
	sm.set_shader_parameter("normal_depth", float(sh.get("normal_scale", 0.35)))
	sm.set_shader_parameter("lift", float(sh.get("lift", 0.45)))
	sm.set_shader_parameter("lift_knee", float(sh.get("lift_knee", 0.45)))
	sm.set_shader_parameter("sat", float(sh.get("sat", 1.0)))
	var tint: Color = sh.get("tint", Color(1, 1, 1))
	sm.set_shader_parameter("tint", Color(tint.r * src.albedo_color.r, tint.g * src.albedo_color.g, tint.b * src.albedo_color.b, 1.0))
	sm.set_shader_parameter("specular_amt", float(sh.get("specular", 0.10)))
	return sm


func _collect_mesh_instances(node: Node, out: Array[Node] = []) -> Array[Node]:
	if node is MeshInstance3D:
		out.append(node)
	for child in node.get_children():
		_collect_mesh_instances(child, out)
	return out
