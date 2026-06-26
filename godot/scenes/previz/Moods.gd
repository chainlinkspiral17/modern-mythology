class_name Moods
extends RefCounted
## Naturalistic lighting/time-of-day moods applied to the sun + WorldEnvironment.
## Opening = open-air clear evening (warm daylight → golden hour); finale =
## overcast night; disaster = dusty/smoky daylight gone wrong (not red).
## Drop an equirect sky at res://assets/sky/<id>.(hdr|exr|png|jpg) to override the
## procedural sky for that mood (e.g. sky/night.png for a cloudy night).

static func ids() -> Array:
	return ["dusk", "night", "disaster"]


static func get_mood(id: String) -> Dictionary:
	match id:
		"night":
			return {
				"label": "Overcast night — Zonk finale",
				"sun_rot": Vector3(-55.0, -60.0, 0.0),
				"sun_color": Color(0.62, 0.7, 0.88),
				"sun_energy": 0.25,
				"sky_top": Color(0.07, 0.09, 0.13),
				"sky_horizon": Color(0.13, 0.14, 0.17),
				"ground": Color(0.04, 0.04, 0.05),
				"ambient": 0.28,
				"fog_color": Color(0.11, 0.13, 0.17),
				"fog_density": 0.003,
				"vfog": 0.04,
				"glow": true,
			}
		"disaster":
			return {
				"label": "Dust & chaos — helicopter",
				"sun_rot": Vector3(-22.0, -105.0, 0.0),
				"sun_color": Color(0.92, 0.86, 0.74),
				"sun_energy": 0.7,
				"sky_top": Color(0.2, 0.21, 0.23),
				"sky_horizon": Color(0.4, 0.36, 0.3),
				"ground": Color(0.09, 0.08, 0.07),
				"ambient": 0.35,
				"fog_color": Color(0.42, 0.38, 0.32),
				"fog_density": 0.01,
				"vfog": 0.1,
				"glow": true,
			}
		_:
			return {
				"label": "Open-air, clear evening — NoNo",
				"sun_rot": Vector3(-20.0, -118.0, 0.0),
				"sun_color": Color(1.0, 0.93, 0.8),
				"sun_energy": 1.7,
				"sky_top": Color(0.26, 0.46, 0.76),
				"sky_horizon": Color(0.92, 0.82, 0.66),
				"ground": Color(0.22, 0.2, 0.17),
				"ambient": 0.6,
				"fog_color": Color(0.82, 0.82, 0.8),
				"fog_density": 0.0015,
				"vfog": 0.02,
				"glow": true,
			}
