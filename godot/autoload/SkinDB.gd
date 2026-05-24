extends Node
## SkinDB — per-volume visual themes. Autoloaded as "SkinDB".

# ── Volume → skin name ────────────────────────────────────────────────────────
const VOL_TO_SKIN: Dictionary = {
	1: "literary", 2: "literary",
	3: "signal",
	4: "zine",
	5: "arcana",
	6: "suburban",
	7: "pastoral",
}

# ── Font paths ────────────────────────────────────────────────────────────────
const F_CINZEL    := "res://resources/fonts/Cinzel-Regular.ttf"
const F_IMFELL_I  := "res://resources/fonts/IMFellEnglish-Italic.ttf"
const F_IMFELL_R  := "res://resources/fonts/IMFellEnglish-Regular.ttf"
const F_SPACEMONO := "res://resources/fonts/SpaceMono-Regular.ttf"
const F_BEBAS     := "res://resources/fonts/BebasNeue-Regular.ttf"
const F_ELITE     := "res://resources/fonts/SpecialElite-Regular.ttf"
const F_COURIER   := "res://resources/fonts/CourierPrime-Regular.ttf"
const F_ANONPRO   := "res://resources/fonts/AnonymousPro-Regular.ttf"
const F_RAJDHANI  := "res://resources/fonts/Rajdhani-Medium.ttf"

# Dialogue box variants
const DLG_STANDARD := "standard"
const DLG_PAPER    := "paper"
const DLG_TERMINAL := "terminal"

var skins: Dictionary = {}


func _ready() -> void:
	_build()


func get_for_vol(vol: int) -> Dictionary:
	var name: String = VOL_TO_SKIN.get(vol, "literary")
	return skins.get(name, skins["literary"])


# ── Gradient texture helper ───────────────────────────────────────────────────

func make_rule_tex(stops: Array, width: int = 1280) -> GradientTexture2D:
	var g := Gradient.new()
	var offsets := PackedFloat32Array()
	var colors  := PackedColorArray()
	for s in stops:
		offsets.append(s[0])
		colors.append(s[1])
	g.offsets = offsets
	g.colors  = colors
	var t := GradientTexture2D.new()
	t.gradient = g
	t.width  = width
	t.height = 1
	return t


# ── Skin definitions ──────────────────────────────────────────────────────────

func _build() -> void:

	skins["literary"] = {
		"variant":    DLG_STANDARD,
		"scene_bg":   Color(0.051, 0.043, 0.035),
		"dlg_bg":     Color(0.039, 0.031, 0.020, 0.97),
		"dlg_border": Color(0.706, 0.549, 0.235, 0.35),
		"dlg_min_h":  210.0,
		"dlg_pad":    [28.0, 44.0, 24.0, 44.0],  # top right bottom left
		"rule": [
			[0.00, Color(0.706, 0.549, 0.235, 0.0)],
			[0.05, Color(0.706, 0.549, 0.235, 0.35)],
			[0.40, Color(0.706, 0.549, 0.235, 0.6)],
			[0.50, Color(0.863, 0.769, 0.314, 0.8)],
			[0.60, Color(0.706, 0.549, 0.235, 0.6)],
			[0.95, Color(0.706, 0.549, 0.235, 0.35)],
			[1.00, Color(0.706, 0.549, 0.235, 0.0)],
		],
		"spk_font":   F_CINZEL, "spk_size": 11,
		"spk_color":  Color(0.784, 0.659, 0.290),
		"txt_font":   F_IMFELL_I, "txt_size": 18,
		"txt_color":  Color(0.831, 0.788, 0.690),
		"ch_font":    F_CINZEL,  "ch_size":  13,
		"ch_color":   Color(0.722, 0.659, 0.533),
		"ch_border":  Color(0.706, 0.549, 0.235, 0.2),
		"ch_bg":      Color(0.706, 0.549, 0.235, 0.05),
		"ch_hborder": Color(0.706, 0.549, 0.235, 0.5),
		"ch_hbg":     Color(0.706, 0.549, 0.235, 0.1),
		"ch_hcolor":  Color(0.831, 0.788, 0.690),
		"cursor_col": Color(0.784, 0.659, 0.290),
		"hud_font":   F_CINZEL,
		"hud_color":  Color(0.784, 0.659, 0.290, 0.75),
		"hud_bg":     Color(0.051, 0.043, 0.035, 0.88),
		"hud_border": Color(0.706, 0.549, 0.235, 0.35),
		"ov_bg":      Color(0.024, 0.016, 0.008, 0.97),
		"ov_border":  Color(0.706, 0.549, 0.235, 0.2),
		"ov_txt":     Color(0.831, 0.788, 0.690),
		"scanlines":  false, "halftone": false,
	}

	skins["signal"] = {
		"variant":    DLG_TERMINAL,
		"scene_bg":   Color(0.024, 0.031, 0.063),
		"dlg_bg":     Color(0.024, 0.031, 0.063, 0.97),
		"dlg_border": Color(0.0, 0.706, 1.0, 0.25),
		"dlg_min_h":  220.0,
		"dlg_pad":    [20.0, 40.0, 20.0, 40.0],
		"rule": [
			[0.00, Color(0.0, 0.706, 1.0, 0.0)],
			[0.05, Color(0.0, 0.706, 1.0, 0.3)],
			[0.50, Color(0.0, 0.706, 1.0, 0.5)],
			[0.75, Color(0.392, 0.314, 1.0, 0.3)],
			[1.00, Color(0.392, 0.314, 1.0, 0.0)],
		],
		"spk_font":   F_SPACEMONO, "spk_size": 11,
		"spk_color":  Color(0.0, 0.784, 1.0, 0.85),
		"txt_font":   F_SPACEMONO, "txt_size": 13,
		"txt_color":  Color(0.784, 0.843, 0.941, 0.85),
		"ch_font":    F_SPACEMONO, "ch_size":  12,
		"ch_color":   Color(0.0, 0.706, 1.0, 0.7),
		"ch_border":  Color(0.0, 0.706, 1.0, 0.12),
		"ch_bg":      Color(0.0, 0.706, 1.0, 0.04),
		"ch_hborder": Color(0.0, 0.706, 1.0, 0.35),
		"ch_hbg":     Color(0.0, 0.706, 1.0, 0.08),
		"ch_hcolor":  Color(0.784, 0.843, 0.941),
		"cursor_col": Color(0.0, 0.784, 1.0),
		"hud_font":   F_SPACEMONO,
		"hud_color":  Color(0.0, 0.784, 1.0, 0.7),
		"hud_bg":     Color(0.024, 0.031, 0.063, 0.9),
		"hud_border": Color(0.0, 0.706, 1.0, 0.25),
		"ov_bg":      Color(0.008, 0.012, 0.031, 0.97),
		"ov_border":  Color(0.0, 0.706, 1.0, 0.2),
		"ov_txt":     Color(0.784, 0.843, 0.941),
		"scanlines":  true, "halftone": false,
	}

	skins["zine"] = {
		"variant":    DLG_PAPER,
		"scene_bg":   Color(0.039, 0.039, 0.039),
		"dlg_bg":     Color(0.941, 0.922, 0.878),
		"dlg_border": Color(0.0, 0.0, 0.0, 0.08),
		"dlg_min_h":  240.0,
		"dlg_pad":    [24.0, 36.0, 24.0, 36.0],
		"rule": [],  # no rule for paper variant
		"spk_font":   F_BEBAS, "spk_size": 28,
		"spk_color":  Color(0.039, 0.039, 0.039),
		"txt_font":   F_ELITE, "txt_size": 15,
		"txt_color":  Color(0.102, 0.102, 0.102),
		"ch_font":    F_ELITE,  "ch_size":  14,
		"ch_color":   Color(0.941, 0.922, 0.878),
		"ch_border":  Color(0.039, 0.039, 0.039, 0.0),
		"ch_bg":      Color(0.039, 0.039, 0.039),
		"ch_hborder": Color(1.0, 0.176, 0.0, 0.0),
		"ch_hbg":     Color(1.0, 0.176, 0.0),
		"ch_hcolor":  Color(0.941, 0.922, 0.878),
		"cursor_col": Color(0.039, 0.039, 0.039),
		"hud_font":   F_BEBAS,
		"hud_color":  Color(0.941, 0.922, 0.878, 0.8),
		"hud_bg":     Color(0.039, 0.039, 0.039, 0.92),
		"hud_border": Color(0.941, 0.922, 0.878, 0.2),
		"ov_bg":      Color(0.039, 0.039, 0.039, 0.97),
		"ov_border":  Color(0.941, 0.922, 0.878, 0.2),
		"ov_txt":     Color(0.941, 0.922, 0.878),
		"scanlines":  false, "halftone": true,
		"tape_color": Color(1.0, 0.863, 0.392, 0.5),
	}

	skins["arcana"] = {
		"variant":    DLG_STANDARD,
		"scene_bg":   Color(0.039, 0.016, 0.055),
		"dlg_bg":     Color(0.031, 0.016, 0.055, 0.97),
		"dlg_border": Color(0.627, 0.392, 0.863, 0.35),
		"dlg_min_h":  210.0,
		"dlg_pad":    [28.0, 44.0, 24.0, 44.0],
		"rule": [
			[0.00, Color(0.627, 0.392, 0.863, 0.0)],
			[0.05, Color(0.627, 0.392, 0.863, 0.35)],
			[0.40, Color(0.627, 0.392, 0.863, 0.6)],
			[0.50, Color(0.863, 0.706, 0.314, 0.8)],
			[0.60, Color(0.627, 0.392, 0.863, 0.6)],
			[0.95, Color(0.627, 0.392, 0.863, 0.35)],
			[1.00, Color(0.627, 0.392, 0.863, 0.0)],
		],
		"spk_font":   F_CINZEL, "spk_size": 11,
		"spk_color":  Color(0.784, 0.643, 0.910),
		"txt_font":   F_IMFELL_I, "txt_size": 18,
		"txt_color":  Color(0.831, 0.784, 0.910),
		"ch_font":    F_CINZEL,  "ch_size":  13,
		"ch_color":   Color(0.706, 0.588, 0.831),
		"ch_border":  Color(0.627, 0.392, 0.863, 0.2),
		"ch_bg":      Color(0.627, 0.392, 0.863, 0.05),
		"ch_hborder": Color(0.627, 0.392, 0.863, 0.5),
		"ch_hbg":     Color(0.627, 0.392, 0.863, 0.12),
		"ch_hcolor":  Color(0.831, 0.784, 0.910),
		"cursor_col": Color(0.784, 0.643, 0.910),
		"hud_font":   F_CINZEL,
		"hud_color":  Color(0.784, 0.643, 0.910, 0.75),
		"hud_bg":     Color(0.039, 0.016, 0.055, 0.88),
		"hud_border": Color(0.627, 0.392, 0.863, 0.35),
		"ov_bg":      Color(0.020, 0.008, 0.031, 0.97),
		"ov_border":  Color(0.627, 0.392, 0.863, 0.2),
		"ov_txt":     Color(0.831, 0.784, 0.910),
		"scanlines":  false, "halftone": false,
	}

	skins["suburban"] = {
		"variant":    DLG_STANDARD,
		"scene_bg":   Color(0.847, 0.827, 0.808),
		"dlg_bg":     Color(0.988, 0.980, 0.973, 0.98),
		"dlg_border": Color(0.0, 0.0, 0.0, 0.1),
		"dlg_min_h":  200.0,
		"dlg_pad":    [24.0, 40.0, 20.0, 40.0],
		"rule": [],  # no rule for suburban
		"spk_font":   F_RAJDHANI, "spk_size": 14,
		"spk_color":  Color(0.165, 0.141, 0.125),
		"txt_font":   F_COURIER,  "txt_size": 15,
		"txt_color":  Color(0.227, 0.204, 0.188),
		"ch_font":    F_COURIER,  "ch_size":  14,
		"ch_color":   Color(0.361, 0.325, 0.298),
		"ch_border":  Color(0.0, 0.0, 0.0, 0.12),
		"ch_bg":      Color(0.0, 0.0, 0.0, 0.03),
		"ch_hborder": Color(0.0, 0.0, 0.0, 0.3),
		"ch_hbg":     Color(0.0, 0.0, 0.0, 0.07),
		"ch_hcolor":  Color(0.165, 0.141, 0.125),
		"cursor_col": Color(0.784, 0.353, 0.227),
		"hud_font":   F_RAJDHANI,
		"hud_color":  Color(0.165, 0.141, 0.125, 0.75),
		"hud_bg":     Color(0.847, 0.827, 0.808, 0.9),
		"hud_border": Color(0.0, 0.0, 0.0, 0.15),
		"ov_bg":      Color(0.847, 0.827, 0.808, 0.97),
		"ov_border":  Color(0.0, 0.0, 0.0, 0.1),
		"ov_txt":     Color(0.165, 0.141, 0.125),
		"scanlines":  false, "halftone": false,
	}

	skins["pastoral"] = {
		"variant":    DLG_STANDARD,
		"scene_bg":   Color(0.055, 0.078, 0.031),
		"dlg_bg":     Color(0.031, 0.047, 0.016, 0.98),
		"dlg_border": Color(0.471, 0.627, 0.235, 0.3),
		"dlg_min_h":  280.0,
		"dlg_pad":    [32.0, 60.0, 28.0, 60.0],
		"rule": [
			[0.00, Color(0.471, 0.627, 0.235, 0.0)],
			[0.05, Color(0.471, 0.627, 0.235, 0.3)],
			[0.40, Color(0.471, 0.627, 0.235, 0.5)],
			[0.50, Color(0.706, 0.627, 0.235, 0.7)],
			[0.60, Color(0.471, 0.627, 0.235, 0.5)],
			[0.95, Color(0.471, 0.627, 0.235, 0.3)],
			[1.00, Color(0.471, 0.627, 0.235, 0.0)],
		],
		"spk_font":   F_CINZEL, "spk_size": 10,
		"spk_color":  Color(0.659, 0.784, 0.392),
		"txt_font":   F_IMFELL_I, "txt_size": 20,
		"txt_color":  Color(0.831, 0.878, 0.722),
		"ch_font":    F_CINZEL,  "ch_size":  13,
		"ch_color":   Color(0.549, 0.659, 0.345),
		"ch_border":  Color(0.471, 0.627, 0.235, 0.2),
		"ch_bg":      Color(0.471, 0.627, 0.235, 0.05),
		"ch_hborder": Color(0.471, 0.627, 0.235, 0.5),
		"ch_hbg":     Color(0.471, 0.627, 0.235, 0.1),
		"ch_hcolor":  Color(0.831, 0.878, 0.722),
		"cursor_col": Color(0.659, 0.784, 0.392),
		"hud_font":   F_CINZEL,
		"hud_color":  Color(0.659, 0.784, 0.392, 0.75),
		"hud_bg":     Color(0.055, 0.078, 0.031, 0.88),
		"hud_border": Color(0.471, 0.627, 0.235, 0.3),
		"ov_bg":      Color(0.016, 0.024, 0.008, 0.97),
		"ov_border":  Color(0.471, 0.627, 0.235, 0.2),
		"ov_txt":     Color(0.831, 0.878, 0.722),
		"scanlines":  false, "halftone": false,
	}
