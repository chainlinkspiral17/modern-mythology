class_name Moods
extends RefCounted
## Naturalistic lighting/time-of-day moods applied to the sun + WorldEnvironment.
## Opening = open-air bright clear day → evening (neutral, not golden/orange);
## finale = overcast night; disaster = dusty/smoky daylight (neutral grey, not
## red). Drop an equirect sky at res://assets/sky/<id>.(hdr|exr|png|jpg) to
## override the procedural sky for a mood (e.g. sky/night.png for a cloudy night).

static func ids() -> Array:
	return ["dusk", "night", "disaster"]


static func get_mood(id: String) -> Dictionary:
	match id:
		"night":
			return {
				"label": "Overcast night — Zonk finale",
				"sun_rot": Vector3(-55.0, -60.0, 0.0),
				"sun_color": Color(0.7, 0.76, 0.9),
				"sun_energy": 0.35,
				"sky_top": Color(0.1, 0.12, 0.17),
				"sky_horizon": Color(0.17, 0.19, 0.23),
				"ground": Color(0.06, 0.06, 0.07),
				"ambient": 0.4,
				"fog_color": Color(0.16, 0.18, 0.22),
				"fog_density": 0.002,
				"vfog": 0.035,
				"glow": true,
			}
		"disaster":
			return {
				"label": "Dust & chaos — helicopter",
				"sun_rot": Vector3(-28.0, -100.0, 0.0),
				"sun_color": Color(0.95, 0.92, 0.85),
				"sun_energy": 0.9,
				"sky_top": Color(0.24, 0.25, 0.27),
				"sky_horizon": Color(0.36, 0.35, 0.33),
				"ground": Color(0.11, 0.1, 0.09),
				"ambient": 0.5,
				"fog_color": Color(0.5, 0.49, 0.46),
				"fog_density": 0.008,
				"vfog": 0.055,
				"glow": true,
			}
		_:
			return {
				"label": "Open-air, clear day → evening — NoNo",
				"sun_rot": Vector3(-32.0, -115.0, 0.0),
				"sun_color": Color(1.0, 0.97, 0.92),
				"sun_energy": 1.5,
				"sky_top": Color(0.32, 0.52, 0.82),
				"sky_horizon": Color(0.72, 0.8, 0.86),
				"ground": Color(0.3, 0.28, 0.25),
				"ambient": 0.75,
				"fog_color": Color(0.8, 0.84, 0.88),
				"fog_density": 0.001,
				"vfog": 0.018,
				"glow": true,
			}
