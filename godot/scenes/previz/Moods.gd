class_name Moods
extends RefCounted
## Lighting/time-of-day moods for the previz stage. Each mood is a plain
## Dictionary the Previz scene applies to the sun + WorldEnvironment.
## Values are concrete Godot types (Vector3 / Color) so no parsing is needed.

static func ids() -> Array:
	return ["dusk", "night", "disaster"]


static func get_mood(id: String) -> Dictionary:
	match id:
		"night":
			return {
				"label": "Night — Zonk finale",
				"sun_rot": Vector3(-32.0, -110.0, 0.0),
				"sun_color": Color(0.5, 0.6, 0.95),
				"sun_energy": 0.35,
				"sky_top": Color(0.02, 0.03, 0.08),
				"sky_horizon": Color(0.08, 0.07, 0.16),
				"ground": Color(0.02, 0.02, 0.04),
				"ambient": 0.15,
				"fog_color": Color(0.06, 0.07, 0.14),
				"fog_density": 0.006,
				"glow": true,
			}
		"disaster":
			return {
				"label": "Disaster — helicopter / emergency",
				"sun_rot": Vector3(-12.0, -95.0, 0.0),
				"sun_color": Color(0.85, 0.32, 0.2),
				"sun_energy": 0.5,
				"sky_top": Color(0.06, 0.04, 0.04),
				"sky_horizon": Color(0.22, 0.1, 0.08),
				"ground": Color(0.04, 0.03, 0.03),
				"ambient": 0.2,
				"fog_color": Color(0.16, 0.11, 0.09),
				"fog_density": 0.02,
				"glow": true,
			}
		_:
			return {
				"label": "Dusk — NoNo opens",
				"sun_rot": Vector3(-14.0, -128.0, 0.0),
				"sun_color": Color(1.0, 0.55, 0.32),
				"sun_energy": 1.2,
				"sky_top": Color(0.2, 0.26, 0.46),
				"sky_horizon": Color(0.95, 0.52, 0.36),
				"ground": Color(0.12, 0.1, 0.1),
				"ambient": 0.4,
				"fog_color": Color(0.6, 0.45, 0.4),
				"fog_density": 0.004,
				"glow": true,
			}
