extends RefCounted
class_name StickTheme
## Per-studio control Themes for slowstick hosts.
##
## The aesthetic bible gives each studio a design culture;
## SlowstickLook carries it in the post-process. This carries it in
## the CONTROLS: a Theme applied at the host cascades to every child
## scene, so the dozens of stock-gray Buttons across a stick pick up
## the studio's chrome from one call in the host's _ready:
##
##   theme = preload("res://scenes/games/StickTheme.gd").make("rocha_faire")
##
## Flat buttons (used as clickable text) stay flat — Godot draws no
## stylebox for them — and any control with an explicit override
## keeps it. This only replaces the default gray.

static func make(preset: String) -> Theme:
	var t := Theme.new()
	var accent: Color
	var text: Color
	var text_hover: Color
	var wash: Color
	var radius: int
	match preset:
		"rocha_faire":
			# Hand-inked cel over cream stock — a mauve line, soft
			# corners, warm cream lettering.
			accent = Color("#b087b8")
			text = Color("#e8dcc8")
			text_hover = Color("#f6eedd")
			wash = Color(0.69, 0.53, 0.72, 0.07)
			radius = 4
		"astro_cortex":
			# Precision-instrument glass — hairline cyan-steel,
			# hard corners, cool lettering. The most machine-like.
			accent = Color("#6fa8b8")
			text = Color("#cfe0e6")
			text_hover = Color("#eaf6fa")
			wash = Color(0.42, 0.66, 0.74, 0.06)
			radius = 0
		_:
			# House neutral (the shelf's warm gold).
			accent = Color(0.78, 0.66, 0.29)
			text = Color(0.83, 0.79, 0.69)
			text_hover = Color(0.95, 0.92, 0.84)
			wash = Color(0.78, 0.66, 0.29, 0.06)
			radius = 3

	var normal := StyleBoxFlat.new()
	normal.bg_color = wash
	normal.border_color = Color(accent.r, accent.g, accent.b, 0.45)
	normal.set_border_width_all(1)
	normal.set_corner_radius_all(radius)
	normal.content_margin_left = 12.0
	normal.content_margin_right = 12.0
	normal.content_margin_top = 6.0
	normal.content_margin_bottom = 6.0
	var hover: StyleBoxFlat = normal.duplicate() as StyleBoxFlat
	hover.bg_color = Color(accent.r, accent.g, accent.b, 0.16)
	hover.border_color = Color(accent.r, accent.g, accent.b, 0.9)
	var pressed: StyleBoxFlat = hover.duplicate() as StyleBoxFlat
	pressed.bg_color = Color(accent.r, accent.g, accent.b, 0.26)
	var disabled: StyleBoxFlat = normal.duplicate() as StyleBoxFlat
	disabled.bg_color = Color(0, 0, 0, 0)
	disabled.border_color = Color(accent.r, accent.g, accent.b, 0.15)

	t.set_stylebox("normal", "Button", normal)
	t.set_stylebox("hover", "Button", hover)
	t.set_stylebox("pressed", "Button", pressed)
	t.set_stylebox("focus", "Button", hover)
	t.set_stylebox("disabled", "Button", disabled)
	t.set_color("font_color", "Button", text)
	t.set_color("font_hover_color", "Button", text_hover)
	t.set_color("font_pressed_color", "Button", text_hover)
	t.set_color("font_focus_color", "Button", text_hover)
	t.set_color("font_disabled_color", "Button",
		Color(text.r, text.g, text.b, 0.35))
	return t
