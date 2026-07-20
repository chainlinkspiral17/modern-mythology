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
		"oneironautics":
			# Field-guide gouache — warm olive-gold line, soft
			# corners, paper-toned lettering.
			accent = Color("#a89050")
			text = Color("#e2d8c0")
			text_hover = Color("#f2ecd8")
			wash = Color(0.66, 0.56, 0.31, 0.07)
			radius = 3
		"pdp_toys":
			# Injection-molded toy-bright — chunky rounded corners,
			# primary red line, the friendliest chrome on the shelf.
			accent = Color("#d84840")
			text = Color("#f0ece4")
			text_hover = Color("#ffffff")
			wash = Color(0.85, 0.28, 0.25, 0.10)
			radius = 8
		"ranch":
			# Laminate-and-signage — crisp neutral steel line, white
			# lettering, minimal wash. Commercial and clean.
			accent = Color("#9aa4aa")
			text = Color("#e8ecee")
			text_hover = Color("#ffffff")
			wash = Color(0.60, 0.64, 0.67, 0.05)
			radius = 2
		"homebrew":
			# One ink, one duplicator — a single pale-green line,
			# square corners, nothing else. The crudeness is in the
			# drawing, not the display.
			accent = Color("#8aa88a")
			text = Color("#d8e0d4")
			text_hover = Color("#eef4ea")
			wash = Color(0.54, 0.66, 0.54, 0.05)
			radius = 0
		"sagebrush":
			# Pulp-paperback cover inks — dusty red-brown line with
			# the reserve violet on hover.
			accent = Color("#a85838")
			text = Color("#e4d4c0")
			text_hover = Color("#d8c8ec")
			wash = Color(0.66, 0.35, 0.22, 0.08)
			radius = 2
		"yumemi":
			# Inked line on paper tones — warm gray-brown hairline,
			# generous quiet. A hanging scroll's patience.
			accent = Color("#8a7a68")
			text = Color("#e6ded0")
			text_hover = Color("#f4eee2")
			wash = Color(0.54, 0.48, 0.41, 0.06)
			radius = 3
		"meridian":
			# 2048 heritage-product chrome — pale teal hairline on
			# near-white lettering, wide radius, no wash to speak
			# of. Frictionless. That is the criticism.
			accent = Color("#7ac8c0")
			text = Color("#f2f6f6")
			text_hover = Color("#ffffff")
			wash = Color(0.48, 0.78, 0.75, 0.03)
			radius = 10
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
