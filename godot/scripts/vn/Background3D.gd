# Background3D.gd
# ════════════════════════════════════════════════════════════════
# Controller for Background3D.tscn — a SubViewport-backed VN bg
# that loads a location scene (diner.tscn, riverfront.tscn) into
# its own World3D and frames an establishing-shot Camera3D per a
# named preset.
#
# Public API:
#   load_location(location_id: String)
#       location_id is a key into CAMERA_PRESETS below. Loads the
#       matching scene into LocationAnchor and positions the
#       Background3D's own Camera3D for the establishing shot.
#       Drop-in: subsequent calls swap the location seamlessly.
#
#   get_viewport_texture() -> Texture2D
#       Convenience accessor used by GameEngine when wrapping this
#       node inside the bg TextureRect.
# ════════════════════════════════════════════════════════════════
extends SubViewportContainer

# Each preset specifies:
#   scene          : res:// path of the location to instantiate
#   camera_origin  : Vector3 in the location's world coords
#                    (Godot frame — X right, Y up, Z-forward = into
#                     the scene; remember Blender Y north = Godot -Z)
#   camera_rotation: Vector3 of euler radians (rotates the camera)
#   fov            : optional override (degrees)
#   suppress_input : if true, the location's interactable Player
#                    node is removed so it doesn't compete for
#                    input or move while the VN bg is on screen
const CAMERA_PRESETS := {
	"diner_interior": {
		"scene": "res://scenes/locales/diner.tscn",
		"requires_glb": "res://assets/3d/locales/diner.glb",
		# RAY-VERIFIED establish (the 4x-reported 'beige wall' was
		# this preset: the old NE vantage sat 0.9m from the private
		# dining room's north partition — survey ray: first hit
		# PD_NorthWall). New vantage: NE open floor by the vestibule
		# arch looking SSW down the dining floor — 9.2m of clear air
		# to the counter, staged John at cast_counter_post ~3 deg
		# off frame center, west booth row at right.
		"camera_origin": Vector3(2.0, 2.0, -4.8),
		"camera_rotation": Vector3(-0.10, 2.787, 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"diner_exterior_porch": {
		"scene": "res://scenes/locales/diner.tscn",
		"requires_glb": "res://assets/3d/locales/diner.glb",
		# Standing on the new portside porch, looking south down the
		# riverboat hull.
		"camera_origin": Vector3(-16.5, 2.20, -2.0),
		"camera_rotation": Vector3(-0.05, deg_to_rad(160.0), 0.0),
		"fov": 65.0,
		"suppress_input": true,
	},
	"riverfront_exterior": {
		"scene": "res://scenes/locales/riverfront.tscn",
		"requires_glb": "res://assets/3d/locales/riverfront.glb",
		# THE RIVERBOAT is the establishing shot. Elevated from the
		# parking-lot side, southwest of the boat, looking NE along
		# the moored hull — clapboard, brass rails, paddlewheel, the
		# dock in the foreground. (The old vantage at x=-30 yaw 75°
		# faced AWAY from the boat entirely.)
		"camera_origin": Vector3(-22.0, 5.5, 18.0),
		"camera_rotation": Vector3(-0.02, deg_to_rad(-51.0), 0.0),
		"fov": 50.0,
		"suppress_input": true,
	},
	"chapel_exterior": {
		# Hierophant §I — Maya outside St. Jude's. SURVEYED: chapel
		# building blender x -3..+3, y 0..+7, front wall + steps at
		# y=0 facing the southern grounds/road. Camera on the asphalt
		# SE of the steps looking NNW at the facade.
		"scene": "res://scenes/locales/roadside_chapel.tscn",
		"requires_glb": "res://assets/3d/locales/roadside_chapel.glb",
		"camera_origin": Vector3(2.5, 1.6, 4.5),
		"camera_rotation": Vector3(0.03, 0.507, 0.0),
		"fov": 55.0,
		"suppress_input": true,
	},
	"dambrosios_formal": {
		# The Empress chapter's side of D'Ambrosio's: the NE formal
		# dining annex (blender X+5..+9, Y+1..+6) + the vestibule
		# hostess stand (7.0,-0.7). Camera at the main-floor archway
		# looking NE across the long formal table. The chapter was
		# establishing on the lunch counter before — the wrong room
		# entirely for Friday-night service.
		"scene": "res://scenes/locales/diner.tscn",
		"requires_glb": "res://assets/3d/locales/diner.glb",
		"camera_origin": Vector3(5.3, 2.0, -1.4),
		"camera_rotation": Vector3(-0.08, deg_to_rad(-39.0), 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"kwik_stop_godseye": {
		"scene": "res://scenes/locales/kwik_stop.tscn",
		"requires_glb": "res://assets/3d/locales/kwik_stop.glb",
		# Diagnostic vantage. Straight-down god's-eye 8m above
		# floor-center. Use when debugging whether the build/GLB
		# actually contains the geometry it should — point a scene
		# at "3d:kwik_stop_godseye" and the floor + counter outline
		# read unambiguously.
		"camera_origin": Vector3(0.0, 8.0, -4.5),
		"camera_rotation": Vector3(-PI / 2.0, 0.0, 0.0),
		"fov": 70.0,
		"suppress_input": true,
	},
	# ── VOL 5 — Priestess chapter ─────────────────────────────────
	"bungalow_interior": {
		"scene": "res://scenes/locales/bungalow.tscn",
		"requires_glb": "res://assets/3d/locales/bungalow.glb",
		# SURVEYED 2026-07-11 (scratchpad survey.py): the bungalow's
		# center is the STORAGE CLOSET (blender x -1..+1.4, y 1..3) —
		# the previous vantage stared into its south wall from 0.5m
		# (the all-black establish). The living room is the narrow
		# west strip (x -2.4..-1, chair + side table); boxes hide in
		# the pocket north of the closet. Establish from just inside
		# the front door looking NW up the living strip.
		"camera_origin": Vector3(-0.35, 1.85, -0.45),
		"camera_rotation": Vector3(-0.06, 0.69, 0.0),
		"fov": 66.0,
		"suppress_input": true,
	},
	# ── VOL 5 — Empress / Emperor — riverboat interior ───────────
	"riverboat_interior": {
		"scene": "res://scenes/locales/riverboat_interior.tscn",
		"requires_glb": "res://assets/3d/locales/riverboat_interior.glb",
		# Dante's helm office — UPPER deck. build_riverboat_interior.py
		# is the floor oracle: UPPER_FLOOR_Z=5.10 (the gauntlet table
		# carried a stale 3.2 — cameras keyed to it sat in the void
		# between decks and rendered black). Eye 5.10+1.75, standing
		# at the north side of the office looking SOUTH: mahogany
		# desk (blender y=-1.5) in the foreground, the leaded window
		# over the dining floor (y=-3) beyond.
		"camera_origin": Vector3(0.0, 6.85, -1.6),
		"camera_rotation": Vector3(-0.10, deg_to_rad(180.0), 0.0),
		"fov": 58.0,
		"suppress_input": true,
	},
	# ── VOL 5 — Magician — Cathedral of Rust and Code ─────────────
	"cathedral_interior": {
		# THE FULL SET, not the bare locale shell. scenes/cathedral.tscn
		# carries the workbench props (steamboat fragment, soldering
		# iron, notebook), the regional dioramas (Frasier's model
		# city), the demon figurines, the 22-light rig and HeroFrasier.
		# The old locales/cathedral.tscn pointed at a GLB path the
		# builder never writes (assets/3d/locales/ vs assets/3d/
		# cathedral/) — requires_glb always failed → the Magician
		# chapter rendered the 2D-black fallback.
		"scene": "res://scenes/cathedral.tscn",
		"requires_glb": "res://assets/3d/cathedral/cathedral_interior.glb",
		# South of the workbench looking NORTH: bench (blender y=-3)
		# in the foreground, dioramas at frame right (x=+5), the nave
		# beyond.
		"camera_origin": Vector3(0.0, 2.30, 5.5),
		"camera_rotation": Vector3(-0.06, 0.0, 0.0),
		"fov": 64.0,
		"suppress_input": true,
	},
	# ── VOL 5 — Lovers + various cameos — Graustark ruins ────────
	"graustark_ruins": {
		"scene": "res://scenes/locales/graustark.tscn",
		"requires_glb": "res://assets/3d/locales/graustark.glb",
		# Establishing vantage looking across the ruins. Texas late-
		# afternoon, warm bleached light, prairie sky beyond.
		"camera_origin": Vector3(-5.0, 2.30, +6.0),
		"camera_rotation": Vector3(-0.06, deg_to_rad(120.0), 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	# ── VOL 5 — Lovers — Roberts house kitchen ───────────────────
	"roberts_kitchen": {
		"scene": "res://scenes/locales/roberts_kitchen.tscn",
		"requires_glb": "res://assets/3d/locales/roberts_kitchen.glb",
		# SURVEYED: the old yaw-180 vantage faced the SOUTH wall from
		# 1.5m (comment said north; rotation said south). Now from
		# the SE open floor looking NW across the island to the sink
		# corner (faucet blender (-2.0,5.4)) — the Lovers chapter's
		# whole geography (sink, island, doorway) in one wide.
		"camera_origin": Vector3(3.3, 1.75, -1.3),
		"camera_rotation": Vector3(-0.10, 0.912, 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	# ── VOL 5 — Empress — Natalie's San Francisco apartment ──────
	"natalie_apartment": {
		"scene": "res://scenes/locales/natalie_apartment.tscn",
		"requires_glb": "res://assets/3d/locales/natalie_apartment.glb",
		# Hanged Man / Moon. Room 7×5.5 (godot x∈[-3.5,3.5], z∈[0,-5.5],
		# ceil 2.6). Teal sofa in the S-centre living area (blender
		# -0.3,1.2 → godot -0.3,-1.2), tall afternoon window on the W
		# wall (x=-3.5), bookshelf E wall, bed nook NE (godot 2.2,-4.5),
		# kitchenette NW. Camera in the SW corner (by the window/door)
		# looking ENE across the whole apartment: sofa in the near
		# foreground, bookshelf + bed nook receding to the far NE, the
		# W window backlighting the frame. One wide that reads the whole
		# geography where "John and Natalie made the choice."
		"camera_origin": Vector3(-2.6, 1.62, -0.7),
		"camera_rotation": Vector3(-0.05, deg_to_rad(-60.7), 0.0),
		"fov": 62.0,
		"suppress_input": true,
	},
	# ── VOL 5 — Lovers cameos — Elicia's apartment ───────────────
	"elicia_apartment": {
		"scene": "res://scenes/locales/elicia_apartment.tscn",
		"requires_glb": "res://assets/3d/locales/elicia_apartment.glb",
		# SW corner looking NE across the sofa + coffee table toward
		# the vinyl shelf (east wall) and the recording nook (NE
		# corner). Room is 7×5.5m, ceiling 2.6 — eye 1.85 keeps the
		# crown molding out of frame. The old default yaw-180 vantage
		# faced the entry wall (the "abstract corners" complaint).
		"camera_origin": Vector3(-2.6, 1.85, -0.8),
		"camera_rotation": Vector3(-0.06, deg_to_rad(-57.0), 0.0),
		"fov": 62.0,
		"suppress_input": true,
	},
	# ── VOL 5 — Emperor — Houston office ─────────────────────────
	"houston_office": {
		"scene": "res://scenes/locales/houston_office.tscn",
		"requires_glb": "res://assets/3d/locales/houston_office.glb",
		# Wheel / Justice. Room 10×7 (godot x∈[-5,5], z∈[0,-7], ceil
		# 2.8 — low). Cubicle row across the centre (blender y=3.5 →
		# godot z=-3.5), manager's glass-walled office SW corner (godot
		# -3.5,-1.5), big mullioned downtown window on the N wall
		# (z=-7). Camera in the SE quadrant just inside the door looking
		# WNW: cubicle row centre-frame, the N window's light upper
		# right, the glass office at far left. Near-level pitch keeps
		# the low drop-ceiling from crowding the top of frame; wide FOV
		# for the big floorplate.
		"camera_origin": Vector3(3.8, 1.68, -1.0),
		"camera_rotation": Vector3(-0.04, deg_to_rad(58.0), 0.0),
		"fov": 64.0,
		"suppress_input": true,
	},
	"houston_design_studio": {
		"scene": "res://scenes/locales/houston_design_studio.tscn",
		"requires_glb": "res://assets/3d/locales/houston_design_studio.glb",
		# Emperor cameo. Room 10×7 (godot x∈[-5,5], z∈[0,-7], ceil 3.2).
		# Three drafting tables in a row mid-room (blender y=3.5 → godot
		# z=-3.5, x∈[-2.8,+2.8]), brick west wall, mullioned N window
		# (z=-7). Camera in the SE quadrant just inside the door looking
		# WNW across the drafting row: tables mid-frame, brick wall left,
		# N window light beyond. Wide FOV for the big open studio.
		"camera_origin": Vector3(3.8, 1.70, -1.0),
		"camera_rotation": Vector3(-0.05, deg_to_rad(59.8), 0.0),
		"fov": 64.0,
		"suppress_input": true,
	},
	# ── VOL 5 — Cameos — Montreal + Olimpico ─────────────────────
	"montreal_apartment": {
		"scene": "res://scenes/locales/montreal_apartment.tscn",
		"requires_glb": "res://assets/3d/locales/montreal_apartment.glb",
		# Temperance. Room 6×5 (godot x∈[-3,3], z∈[0,-5], ceil 2.8).
		# Mile-End winter apartment: sofa S-centre (blender -0.5,1.3 →
		# godot -0.5,-1.3), overflowing bookshelf E wall (godot
		# 2.5,-2.5), tall N window with snow-light + cast-iron radiator
		# under it (z=-4.8/-5), corner kitchenette NE with the French
		# press. Camera in the SW corner looking NE: sofa near-left, the
		# book wall at right, the cold N window glow centre-back. Cozy,
		# contained — the whole cluttered room in one frame.
		"camera_origin": Vector3(-2.0, 1.60, -0.7),
		"camera_rotation": Vector3(-0.04, deg_to_rad(-41.9), 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"cafe_olimpico": {
		"scene": "res://scenes/locales/cafe_olimpico.tscn",
		"requires_glb": "res://assets/3d/locales/cafe_olimpico.glb",
		# The Sun. Room 8×6 (godot x∈[-4,4], z∈[0,-6], ceil 3.0).
		# Espresso bar along the N wall (blender y=5 → godot z=-5) with
		# the chrome 2-group machine dead-centre, pastry case at the E
		# end, two marble round tables mid-room (godot ±2,-1.8), vinyl
		# booth E wall, soccer pennants over the bar, bright SW/SE
		# windows. Camera just inside the S door, west of centre,
		# looking NNE: west marble table in the foreground, the bar +
		# espresso machine centre-back, pastry case + booth at right.
		# The brightest, most welcoming room of the eight.
		"camera_origin": Vector3(-2.0, 1.65, -0.8),
		"camera_rotation": Vector3(-0.04, deg_to_rad(-29.9), 0.0),
		"fov": 62.0,
		"suppress_input": true,
	},
	# ── VOL 5 — New Orleans cameos ───────────────────────────────
	"new_orleans_bar": {
		"scene": "res://scenes/locales/new_orleans_bar.tscn",
		"requires_glb": "res://assets/3d/locales/new_orleans_bar.glb",
		# Strength. Room 9×6 (godot x∈[-4.5,4.5], z∈[0,-6], ceil 3.2).
		# Long mahogany bar along the N wall (blender y=4.5 → godot
		# z=-4.5), bottle wall + mirror behind (z=-5.4), Wurlitzer
		# jukebox SE corner (godot +3.8,-1.2). Camera just inside the
		# S door, west of centre, looking NNE across the room: bar +
		# bottle wall centre-back, jukebox at frame right, pendant lamps
		# and ceiling fan overhead. Wide FOV for the big jazz-club room.
		"camera_origin": Vector3(-2.5, 1.70, -0.8),
		"camera_rotation": Vector3(-0.05, deg_to_rad(-34.0), 0.0),
		"fov": 64.0,
		"suppress_input": true,
	},
	"new_orleans_office": {
		"scene": "res://scenes/locales/new_orleans_office.tscn",
		"requires_glb": "res://assets/3d/locales/new_orleans_office.glb",
		# The Chariot. Room 7×6 (godot x∈[-3.5,3.5], z∈[0,-6], ceil 3.2).
		# Heavy oak desk dead-centre (blender 0,3.5 → godot 0,-3.5),
		# tall afternoon window on the E wall (x=+3.5), bookcase W wall,
		# filing cabinet NE. Camera in the SW quadrant just inside the
		# door looking NE across the desk toward the window — 3/4 angle
		# so the oak desk + banker's lamp read with depth, not a flat
		# head-on stare.
		"camera_origin": Vector3(-2.2, 1.65, -0.6),
		"camera_rotation": Vector3(-0.06, deg_to_rad(-37.7), 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"new_orleans_apartment": {
		"scene": "res://scenes/locales/new_orleans_apartment.tscn",
		"requires_glb": "res://assets/3d/locales/new_orleans_apartment.glb",
		# The Devil. Room 7×6 (godot x∈[-3.5,3.5], z∈[0,-6], ceil 3.4).
		# Four-poster canopy bed at the N end (blender 0,4.8 → godot
		# 0,-4.8, canopy top ~2.05), exposed-brick E wall (x=+3.5),
		# armoire W wall, ceiling fan centre. Camera in the SE quadrant
		# just inside the door looking NNW at the bed: canopy + brick
		# wall (frame right) with the tall room's headroom above. Eye
		# lifted to 1.80 for the 3.4m ceiling grandeur.
		"camera_origin": Vector3(2.2, 1.80, -0.8),
		"camera_rotation": Vector3(-0.05, deg_to_rad(32.3), 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"new_orleans_room": {
		"scene": "res://scenes/locales/new_orleans_room.tscn",
		"requires_glb": "res://assets/3d/locales/new_orleans_room.glb",
		# Spare boarding-house room 4×5 (godot x∈[-2,2], z∈[0,-5], ceil
		# 2.8). Single bed centre-north (blender 0,3.5 → godot 0,-3.5),
		# porcelain washbasin NE corner (godot 1.6,-4.5), nightstand NW,
		# sash window N wall, bare bulb on a cord. Camera in the SW corner
		# just inside the door looking NE across the room: bed centre-back,
		# washbasin at frame right, the worn geography in one contained wide.
		"camera_origin": Vector3(-1.3, 1.55, -0.7),
		"camera_rotation": Vector3(-0.05, deg_to_rad(-28.7), 0.0),
		"fov": 58.0,
		"suppress_input": true,
	},
	"hospice_room": {
		"scene": "res://scenes/locales/hospice_room.tscn",
		"requires_glb": "res://assets/3d/locales/hospice_room.glb",
		# Death. Room 6×5.5 (godot x∈[-3,3], z∈[0,-5.5], ceil 2.8).
		# Adjustable bed centre-north (blender 0,3.2 → godot 0,-3.2,
		# head raised toward the N window), soft-lit N window behind it
		# (z=-5.5), IV stand at the bed's right (godot 1,-4.2), vitals
		# cart at its left, the visitor's upholstered armchair south of
		# the bed (godot -1.2,-1.8), bedside table with flowers.
		# Camera in the SE quadrant looking NNW: the empty visitor chair
		# in the near foreground, the bed with the window's gentle glow
		# behind it — the vantage of the one who stays.
		"camera_origin": Vector3(1.8, 1.60, -0.8),
		"camera_rotation": Vector3(-0.05, deg_to_rad(36.2), 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"louisiana_road": {
		"scene": "res://scenes/locales/louisiana_road.tscn",
		"requires_glb": "res://assets/3d/locales/louisiana_road.glb",
		# Standing in the breakdown lane looking north up the road.
		"camera_origin": Vector3(-1.0, 2.30, -3.0),
		"camera_rotation": Vector3(-0.04, deg_to_rad(180.0), 0.0),
		"fov": 64.0,
		"suppress_input": true,
	},
	# ── VOL 6 — Planned Community / Harmony Creek Estates ─────────
	# All vol6 presets use the same default cinematographic vantage:
	# entrance-looking-in at eye-height 2.30, north-facing, ~60° FOV.
	# Per-scene refinements via the gauntlet/VN debug overlay.
	"miller_kitchen": {
		"scene": "res://scenes/locales/miller_kitchen.tscn",
		"requires_glb": "res://assets/3d/locales/miller_kitchen.glb",
		# Sam's family kitchen 7×6 (godot x∈[-3.5,3.5], z∈[0,-6], ceil
		# 2.6). Round pedestal table dead-centre (godot 0,-3), sink+counter
		# NW (godot -1.75,-5), stove centre-N (1.75,-5), fridge NE
		# (3.0,-5), E window. Camera in the SE quadrant just inside the
		# door looking NW across the table toward the sink corner — the
		# whole working kitchen in one 3/4 wide.
		"camera_origin": Vector3(2.4, 1.60, -0.8),
		"camera_rotation": Vector3(-0.05, deg_to_rad(48.6), 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"centro_grocery_aisle": {
		"scene": "res://scenes/locales/centro_grocery_aisle.tscn",
		"requires_glb": "res://assets/3d/locales/centro_grocery_aisle.glb",
		# Grocery sales floor 10×8 (godot x∈[-5,5], z∈[0,-8], ceil 3.0).
		# Two snack aisles run E-W across the room (blender y=2.8 & 5.2 →
		# godot z=-2.8 & -5.2, each 6m along X), endcaps at x=±3.5, chest
		# freezer E wall, hanging aisle sign centre. Camera in the SE
		# quadrant just inside the entrance looking NW down the aisles:
		# both shelf rows recede to the far NW, freezer at right. Eye
		# lifted to 1.85 and wide FOV for the big floorplate.
		"camera_origin": Vector3(3.2, 1.85, -0.8),
		"camera_rotation": Vector3(-0.06, deg_to_rad(52.7), 0.0),
		"fov": 66.0,
		"suppress_input": true,
	},
	"centro_break_room": {
		"scene": "res://scenes/locales/centro_break_room.tscn",
		"requires_glb": "res://assets/3d/locales/centro_break_room.glb",
		# Employee break room 5×4 (godot x∈[-2.5,2.5], z∈[0,-4], ceil 2.6).
		# Round pedestal table centre (godot 0,-2), vending machine E
		# (godot 2.2,-3), galley kitchenette + sink along the W wall,
		# fridge NW corner, bulletin board N wall. Camera in the SE
		# quadrant just inside the door looking NW across the table toward
		# the kitchenette — table, vending (right), board all in frame.
		"camera_origin": Vector3(1.7, 1.58, -0.7),
		"camera_rotation": Vector3(-0.05, deg_to_rad(52.8), 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"kowalski_kitchen": {
		"scene": "res://scenes/locales/kowalski_kitchen.tscn",
		"requires_glb": "res://assets/3d/locales/kowalski_kitchen.glb",
		# Family kitchen 6×5 (godot x∈[-3,3], z∈[0,-5], ceil 2.6). Table
		# dead-centre (godot 0,-2.5), sink+counter NW (godot -1.5,-4),
		# stove centre-N (1.5,-4), fridge on the E wall (godot 2.45,-1),
		# E window. Camera in the SE quadrant just inside the door looking
		# NW across the table toward the sink corner — a 3/4 wide of the
		# whole kitchen.
		"camera_origin": Vector3(2.1, 1.58, -0.8),
		"camera_rotation": Vector3(-0.05, deg_to_rad(51.3), 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"henderson_kitchen": {
		"scene": "res://scenes/locales/henderson_kitchen.tscn",
		"requires_glb": "res://assets/3d/locales/henderson_kitchen.glb",
		# Family kitchen 6.5×5.5 (godot x∈[-3.25,3.25], z∈[0,-5.5], ceil
		# 2.6). Table centre (godot 0,-2.75), sink+counter NW (godot
		# -1.625,-4.5), stove centre-N (1.625,-4.5), fridge NE (godot
		# 2.75,-4.5). Camera in the SE quadrant just inside the door
		# looking NW across the table toward the sink corner — the whole
		# kitchen in one 3/4 wide.
		"camera_origin": Vector3(2.2, 1.58, -0.8),
		"camera_rotation": Vector3(-0.05, deg_to_rad(50.0), 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"cosmic_comics_interior": {
		"scene": "res://scenes/locales/cosmic_comics_interior.tscn",
		"requires_glb": "res://assets/3d/locales/cosmic_comics_interior.glb",
		# Comic-shop back-issue floor 10×8 (godot x∈[-5,5], z∈[0,-8], ceil
		# 2.8, purple walls). Two long back-issue bins run E-W mid-room
		# (blender y=2.8 & 5.2 → godot z=-2.8 & -5.2, x∈[-2.5,2.5]),
		# register counter NE (blender 2.5,6.5 → godot 2.5,-6.5), revolving
		# spinner rack NW corner, action-figure pegwall E wall. Camera in
		# the SE quadrant just inside the door looking NW across the bins
		# toward the spinner: bins mid-frame, register at right, wide FOV.
		"camera_origin": Vector3(3.5, 1.68, -0.9),
		"camera_rotation": Vector3(-0.05, deg_to_rad(40.9), 0.0),
		"fov": 64.0,
		"suppress_input": true,
	},
	"cosmic_comics_back_office": {
		"scene": "res://scenes/locales/cosmic_comics_back_office.tscn",
		"requires_glb": "res://assets/3d/locales/cosmic_comics_back_office.glb",
		# SURVEYED 2026-07-12: the old vantage sat at blender y=-0.5,
		# OUTSIDE the south door, 0.4m from the door lintel. Now just
		# inside the door looking N across the room: filing cabinets
		# at frame-left, Maya's desk + monitor at the far (north) end,
		# long-boxes down the east wall. Eye 1.70 (ceiling 2.6).
		"camera_origin": Vector3(1.5, 1.60, -0.6),
		"camera_rotation": Vector3(-0.05, deg_to_rad(43.7), 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"maya_bedroom": {
		"scene": "res://scenes/locales/maya_bedroom.tscn",
		"requires_glb": "res://assets/3d/locales/maya_bedroom.glb",
		# Teen-girl bedroom 4×5 (godot x∈[-2,2], z∈[0,-5], ceil 2.6). Bed
		# along the W side (blender -1,2.5 → godot -1,-2.5), desk+lamp E
		# (godot 1,-1.5), vanity dresser E wall (godot 1.7,-3.8), rug
		# centre, N window, fairy lights. Camera in the SE corner just
		# inside the door looking NW across to the bed: bed centre-back,
		# window light beyond, vanity at frame right. Tight FOV, small room.
		"camera_origin": Vector3(1.4, 1.55, -0.7),
		"camera_rotation": Vector3(-0.05, deg_to_rad(43.7), 0.0),
		"fov": 58.0,
		"suppress_input": true,
	},
	"grandmother_kitchen_morning": {
		"scene": "res://scenes/locales/grandmother_kitchen_morning.tscn",
		"requires_glb": "res://assets/3d/locales/grandmother_kitchen_morning.glb",
		# Abuela's warm kitchen 5×5 (godot x∈[-2.5,2.5], z∈[0,-5], ceil
		# 2.6). Round pedestal table centre with pie+fruit (godot 0,-2.5),
		# sink+counter NW (godot -1.25,-4), stove centre-N (1.25,-4) with
		# kettle, china hutch W wall, braided rug under the table. Camera
		# in the SE quadrant just inside the door looking NW across the
		# table toward the counter — the whole cozy kitchen in one wide.
		"camera_origin": Vector3(1.7, 1.58, -0.8),
		"camera_rotation": Vector3(-0.05, deg_to_rad(47.3), 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"miller_back_porch": {
		"scene": "res://scenes/locales/miller_back_porch.tscn",
		"requires_glb": "res://assets/3d/locales/miller_back_porch.glb",
		# Covered back porch 6×4 (godot x∈[-3,3], z∈[0,-4], ceil 2.8).
		# Two rockers face the S railing (godot ±1.5,-2.0) with a round
		# side table between them (godot 0,-2.0); balustrade + screen door
		# along the S edge (godot z≈-0.1), firewood stack E wall, hanging
		# planter, house wall to the N. Camera in the NE corner (by the
		# house wall) looking SW across the rockers toward the railing: the
		# porch furniture in the fore, the open railing beyond.
		"camera_origin": Vector3(2.3, 1.62, -3.4),
		"camera_rotation": Vector3(-0.05, deg_to_rad(118.9), 0.0),
		"fov": 62.0,
		"suppress_input": true,
	},
	"jesse_bedroom": {
		"scene": "res://scenes/locales/jesse_bedroom.tscn",
		"requires_glb": "res://assets/3d/locales/jesse_bedroom.glb",
		# Kid's bedroom 4×4.5 (godot x∈[-2,2], z∈[0,-4.5], ceil 2.6). Bed
		# along the W side (blender -1,2.25 → godot -1,-2.25), desk+lamp E
		# (godot 1,-1.5), dresser E wall (godot 1.7,-3.2), posters W wall,
		# N window. Camera in the SE corner just inside the door looking
		# NW across to the bed: bed centre-back, window beyond, dresser at
		# frame right. Tight FOV for the small room.
		"camera_origin": Vector3(1.4, 1.55, -0.7),
		"camera_rotation": Vector3(-0.05, deg_to_rad(46.3), 0.0),
		"fov": 58.0,
		"suppress_input": true,
	},
	"diego_bedroom": {
		"scene": "res://scenes/locales/diego_bedroom.tscn",
		"requires_glb": "res://assets/3d/locales/diego_bedroom.glb",
		# Kid's bedroom 4×4.5 (godot x∈[-2,2], z∈[0,-4.5], ceil 2.6).
		# Same shell as jesse_bedroom: bed W side (godot -1,-2.25),
		# desk+lamp E (godot 1,-1.5), dresser E wall (godot 1.7,-3.2),
		# soccer ball on the floor, N window. Camera in the SE corner just
		# inside the door looking NW across to the bed: bed centre-back,
		# window beyond, dresser at frame right. Tight FOV for the small room.
		"camera_origin": Vector3(1.4, 1.55, -0.7),
		"camera_rotation": Vector3(-0.05, deg_to_rad(46.3), 0.0),
		"fov": 58.0,
		"suppress_input": true,
	},
	# ── VOL 6/7/8 — batch 2 additions ────────────────────
	"caldwell_porch_night": {
		"scene": "res://scenes/locales/caldwell_porch_night.tscn",
		"requires_glb": "res://assets/3d/locales/caldwell_porch_night.glb",
		# Covered porch at NIGHT 6×4 (godot x∈[-3,3], z∈[0,-4], ceil 2.8).
		# Two rockers face the S railing (godot ±1.5,-2.0) with a side
		# table between them (godot 0,-2.0); balustrade + screen door along
		# the S edge (godot z≈-0.1), cordwood stack NW, wall-mounted
		# carriage lamp (warm), hanging planter, house wall N. Camera in
		# the NE corner (by the house wall) looking SW across the rockers
		# toward the railing: furniture lit warm in the fore, night beyond.
		"camera_origin": Vector3(2.3, 1.62, -3.4),
		"camera_rotation": Vector3(-0.05, deg_to_rad(118.9), 0.0),
		"fov": 62.0,
		"suppress_input": true,
	},
	"caldwell_kitchen_night": {
		"scene": "res://scenes/locales/caldwell_kitchen_night.tscn",
		"requires_glb": "res://assets/3d/locales/caldwell_kitchen_night.glb",
		# Family kitchen at NIGHT 6×5 (godot x∈[-3,3], z∈[0,-5], ceil 2.6).
		# Table dead-centre (godot 0,-2.5), sink+counter NW (godot
		# -1.5,-4), stove centre-N (1.5,-4), fridge on the E wall (godot
		# 2.45,-1). Camera in the SE quadrant just inside the door looking
		# NW across the table toward the sink corner — the whole kitchen
		# in one 3/4 wide.
		"camera_origin": Vector3(2.1, 1.58, -0.8),
		"camera_rotation": Vector3(-0.05, deg_to_rad(51.3), 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"caldwell_radio_room_night": {
		"scene": "res://scenes/locales/caldwell_radio_room_night.tscn",
		"requires_glb": "res://assets/3d/locales/caldwell_radio_room_night.glb",
		# Late-night radio booth 4.5×5 (godot x∈[-2.25,2.25], z∈[0,-5],
		# ceil 2.6). Broadcast console desk + mixing board against the N
		# wall (blender 0,3.9 → godot 0,-3.9), on-air mic on a boom,
		# CRT monitors, equipment rack on the W wall (godot -1.875,-1.3),
		# ON AIR sign over the S door. Camera in the SE quadrant just
		# inside the door looking NW across to the console: mixing board
		# centre-back, equipment rack at frame left, warm gear glow.
		"camera_origin": Vector3(1.4, 1.58, -0.7),
		"camera_rotation": Vector3(-0.05, deg_to_rad(29.5), 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"foxhole_bar": {
		"scene": "res://scenes/locales/foxhole_bar.tscn",
		"requires_glb": "res://assets/3d/locales/foxhole_bar.glb",
		# Music-venue bar 8×6 (godot x∈[-4,4], z∈[0,-6], ceil 3.0). Long
		# bar counter along the N wall (blender y=5 → godot z=-5, x∈[-3,3]),
		# back-bar bottle shelves + mirror behind (z=-5.85), draft-tap
		# tower, five stools (godot z=-4.1), two high-tops mid-room, neon
		# signs on the N wall, warm pendants over the bar. Camera in the SW
		# quadrant just inside the door looking NE along the bar: counter
		# runs diagonally across frame, bottles + neon centre-back. Eye
		# lifted to 1.90 and wide FOV for the big moody venue.
		"camera_origin": Vector3(-2.8, 1.90, -0.9),
		"camera_rotation": Vector3(-0.06, deg_to_rad(-42.8), 0.0),
		"fov": 64.0,
		"suppress_input": true,
	},
	"foxhole_stage": {
		"scene": "res://scenes/locales/foxhole_stage.tscn",
		"requires_glb": "res://assets/3d/locales/foxhole_stage.glb",
		# Music-venue stage 8×5 (godot x∈[-4,4], z∈[0,-5], ceil 3.2). Raised
		# stage deck along the N wall (blender y=4.2 → godot z=-4.2, 7.4m
		# wide), drum kit centre (godot 0,-4.6), amp stacks flanking (godot
		# ±1.9,-4.6), two mic stands downstage (z=-3.6), PA towers at the
		# corners (godot ±3.3,-3.4). Camera from the audience floor (SW
		# quadrant) looking NE at the stage: drums centre, amps + PA
		# framing. Eye 1.95 and wide FOV for the tall venue.
		"camera_origin": Vector3(-2.6, 1.95, -0.8),
		"camera_rotation": Vector3(-0.06, deg_to_rad(-41.6), 0.0),
		"fov": 65.0,
		"suppress_input": true,
	},
	"foxhole_dressing_room": {
		"scene": "res://scenes/locales/foxhole_dressing_room.tscn",
		"requires_glb": "res://assets/3d/locales/foxhole_dressing_room.glb",
		# Backstage dressing room 4×4 (godot x∈[-2,2], z∈[0,-4], ceil 2.6).
		# Bulb-framed vanity mirror against the N wall (blender 0,3.6 →
		# godot 0,-3.6), beat-up couch along the W wall (godot -1.52,-2),
		# clothing rack E side (godot 1.62,-1.9), guitar cases on the floor,
		# mini-fridge NE, taped setlist E wall. Camera in the SE quadrant
		# just inside the door looking NW: vanity + lit mirror centre-back,
		# couch at frame left. Tight FOV for the small backstage room.
		"camera_origin": Vector3(1.3, 1.58, -0.7),
		"camera_rotation": Vector3(-0.05, deg_to_rad(29.7), 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"pit_stop_interior": {
		"scene": "res://scenes/locales/pit_stop_interior.tscn",
		"requires_glb": "res://assets/3d/locales/pit_stop_interior.glb",
		"camera_origin": Vector3(0.0, 1.55, -0.6),
		"camera_rotation": Vector3(-0.04, 0.0, 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"pit_stop_office": {
		"scene": "res://scenes/locales/pit_stop_office.tscn",
		"requires_glb": "res://assets/3d/locales/pit_stop_office.glb",
		"camera_origin": Vector3(0.0, 1.55, -0.6),
		"camera_rotation": Vector3(-0.04, 0.0, 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"nexcorp_fueling_station": {
		"scene": "res://scenes/locales/nexcorp_fueling_station.tscn",
		"requires_glb": "res://assets/3d/locales/nexcorp_fueling_station.glb",
		"camera_origin": Vector3(0.0, 1.55, -0.6),
		"camera_rotation": Vector3(-0.04, 0.0, 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"sam_bedroom": {
		"scene": "res://scenes/locales/sam_bedroom.tscn",
		"requires_glb": "res://assets/3d/locales/sam_bedroom.glb",
		"camera_origin": Vector3(0.0, 1.55, -0.6),
		"camera_rotation": Vector3(-0.04, 0.0, 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"school_field_evening": {
		"scene": "res://scenes/locales/school_field_evening.tscn",
		"requires_glb": "res://assets/3d/locales/school_field_evening.glb",
		"camera_origin": Vector3(0.0, 1.55, -0.6),
		"camera_rotation": Vector3(-0.04, 0.0, 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"ramos_kitchen_morning": {
		"scene": "res://scenes/locales/ramos_kitchen_morning.tscn",
		"requires_glb": "res://assets/3d/locales/ramos_kitchen_morning.glb",
		"camera_origin": Vector3(0.0, 1.55, -0.6),
		"camera_rotation": Vector3(-0.04, 0.0, 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"bianca_kitchen_morning": {
		"scene": "res://scenes/locales/bianca_kitchen_morning.tscn",
		"requires_glb": "res://assets/3d/locales/bianca_kitchen_morning.glb",
		"camera_origin": Vector3(0.0, 1.55, -0.6),
		"camera_rotation": Vector3(-0.04, 0.0, 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"hospital_room": {
		"scene": "res://scenes/locales/hospital_room.tscn",
		"requires_glb": "res://assets/3d/locales/hospital_room.glb",
		"camera_origin": Vector3(0.0, 1.55, -0.6),
		"camera_rotation": Vector3(-0.04, 0.0, 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"safehouse_bedroom": {
		"scene": "res://scenes/locales/safehouse_bedroom.tscn",
		"requires_glb": "res://assets/3d/locales/safehouse_bedroom.glb",
		"camera_origin": Vector3(0.0, 1.55, -0.6),
		"camera_rotation": Vector3(-0.04, 0.0, 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"el_rancho_taqueria": {
		"scene": "res://scenes/locales/el_rancho_taqueria.tscn",
		"requires_glb": "res://assets/3d/locales/el_rancho_taqueria.glb",
		"camera_origin": Vector3(0.0, 1.55, -0.6),
		"camera_rotation": Vector3(-0.04, 0.0, 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"board_lords_interior": {
		"scene": "res://scenes/locales/board_lords_interior.tscn",
		"requires_glb": "res://assets/3d/locales/board_lords_interior.glb",
		"camera_origin": Vector3(0.0, 1.55, -0.6),
		"camera_rotation": Vector3(-0.04, 0.0, 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"salty_tome_interior": {
		"scene": "res://scenes/locales/salty_tome_interior.tscn",
		"requires_glb": "res://assets/3d/locales/salty_tome_interior.glb",
		"camera_origin": Vector3(0.0, 1.55, -0.6),
		"camera_rotation": Vector3(-0.04, 0.0, 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"hans_bakery_back_kitchen": {
		"scene": "res://scenes/locales/hans_bakery_back_kitchen.tscn",
		"requires_glb": "res://assets/3d/locales/hans_bakery_back_kitchen.glb",
		"camera_origin": Vector3(0.0, 1.55, -0.6),
		"camera_rotation": Vector3(-0.04, 0.0, 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"daily_grind_interior": {
		"scene": "res://scenes/locales/daily_grind_interior.tscn",
		"requires_glb": "res://assets/3d/locales/daily_grind_interior.glb",
		"camera_origin": Vector3(0.0, 1.55, -0.6),
		"camera_rotation": Vector3(-0.04, 0.0, 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"chillwave_interior": {
		"scene": "res://scenes/locales/chillwave_interior.tscn",
		"requires_glb": "res://assets/3d/locales/chillwave_interior.glb",
		"camera_origin": Vector3(0.0, 1.55, -0.6),
		"camera_rotation": Vector3(-0.04, 0.0, 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"lena_apartment": {
		"scene": "res://scenes/locales/lena_apartment.tscn",
		"requires_glb": "res://assets/3d/locales/lena_apartment.glb",
		"camera_origin": Vector3(0.0, 1.55, -0.6),
		"camera_rotation": Vector3(-0.04, 0.0, 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"missing_link_interior": {
		"scene": "res://scenes/locales/missing_link_interior.tscn",
		"requires_glb": "res://assets/3d/locales/missing_link_interior.glb",
		"camera_origin": Vector3(0.0, 1.55, -0.6),
		"camera_rotation": Vector3(-0.04, 0.0, 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"cabin_interior": {
		"scene": "res://scenes/locales/cabin_interior.tscn",
		"requires_glb": "res://assets/3d/locales/cabin_interior.glb",
		# SURVEYED 2026-07-12: old vantage sat blender y=-0.5 OUTSIDE
		# the south door, 0.4m from the lintel. Now just inside the
		# door looking N across the table + rockers to the kitchenette
		# counter (west) and the wood stove. Eye 1.70 (ceiling 2.8).
		"camera_origin": Vector3(2.0, 1.62, -0.7),
		"camera_rotation": Vector3(-0.05, deg_to_rad(54.5), 0.0),
		"fov": 62.0,
		"suppress_input": true,
	},
	"finn_apartment": {
		"scene": "res://scenes/locales/finn_apartment.tscn",
		"requires_glb": "res://assets/3d/locales/finn_apartment.glb",
		"camera_origin": Vector3(0.0, 1.55, -0.6),
		"camera_rotation": Vector3(-0.04, 0.0, 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"kai_apartment": {
		"scene": "res://scenes/locales/kai_apartment.tscn",
		"requires_glb": "res://assets/3d/locales/kai_apartment.glb",
		"camera_origin": Vector3(0.0, 1.55, -0.6),
		"camera_rotation": Vector3(-0.04, 0.0, 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"kwik_stop_interior": {
		"scene": "res://scenes/locales/kwik_stop.tscn",
		"requires_glb": "res://assets/3d/locales/kwik_stop.glb",
		# SAM'S POV — behind the east-wall counter looking west into
		# the store. Counter is at Blender X=+5, Y∈[3,7]; Sam stands
		# at X≈+5.5 (just east of counter), Y≈+5 (mid-run), 1.65m
		# eye-level. Looking west (-X) sees: register edge in the
		# near foreground, aisles running E-W down the middle, the
		# coffee/slurpee station on the far west wall, and the front
		# door at south-left framing in some streetlight.
		# Counter front box spans Blender X∈[+4.5,+5.5] — camera must
		# sit EAST of that edge (clerk-side aisle, X∈[+5.5,+6.0]) or
		# we render from inside the counter geometry. Use +5.78 so
		# we're firmly in Sam's stance band but still ~12cm from the
		# east wall at +5.9 (WALL_THICK=0.20, wall centered at +6.0).
		# Camera height 2.05m — Sam-on-a-rubber-mat eye level, lifted
		# so she looks DOWN over the counter top (top at Z≈1.0)
		# instead of having the counter-front face fill mid-frame
		# (that was the "pink box" — counter formica catching warm
		# ambient + saturation adjustment, reading as a flat panel).
		# Pitch is positive-ish (+0.04 rad slight UP) so the gaze
		# clears the counter top and lands on the aisles + west wall.
		# Blender (+5.78, +5.0, 2.05) → Godot (+5.78, 2.05, -5.0).
		# +90° Y rotation swings default -Z gaze to -X (west, into
		# the store). (Right-hand rule around +Y: -Z → -X under +π/2.
		# The diner_interior preset uses -π/2 because its "front
		# door" actually faces +X-out; the kwik_stop east wall is a
		# solid backing for Sam, so the camera looks the OTHER way.)
		"camera_origin": Vector3(5.78, 2.05, -5.0),
		"camera_rotation": Vector3(0.04, deg_to_rad(90.0), 0.0),
		"fov": 64.0,
		"suppress_input": true,
	},
}

const BG_W: int = 1280
const BG_H: int = 720

@onready var _viewport: SubViewport = $SubViewport
@onready var _anchor: Node3D = $SubViewport/LocationAnchor
@onready var _camera: Camera3D = $SubViewport/Camera3D

var _loaded_preset: String = ""
var _location_instance: Node = null


func _ready() -> void:
	custom_minimum_size = Vector2(BG_W, BG_H)


# ── Public API ────────────────────────────────────────────────────
# GameEngine calls this instead of call_deferred("load_location"):
# a [shot:]/[stage:] directive on the first text node after a bg
# node must NOT resolve against the PREVIOUS locale. Marking the
# load pending makes has_locale_loaded() gate the director's
# pending-retry loop until the deferred load actually lands.
func queue_load(preset_id: String) -> void:
	_pending_preset = preset_id
	call_deferred("load_location", preset_id)


var _pending_preset: String = ""


func load_location(preset_id: String) -> bool:
	_pending_preset = ""
	if preset_id == _loaded_preset and _location_instance != null:
		return true
	if not CAMERA_PRESETS.has(preset_id):
		push_warning("[Background3D] Unknown preset: %s" % preset_id)
		return false
	var spec: Dictionary = CAMERA_PRESETS[preset_id]
	# Pre-check the required GLB BEFORE asking Godot to parse the
	# .tscn — locale .glb files are build artifacts (not committed),
	# so a fresh checkout that hasn't run the Blender builders yet
	# will hit a parse-error cascade if we let the .tscn load. The
	# explicit check turns it into a single actionable warning.
	var req_glb: String = spec.get("requires_glb", "")
	if req_glb != "" and not FileAccess.file_exists(req_glb):
		push_warning("[Background3D] GLB missing: %s — build it with `cd godot/tools/blender && ./run_cathedral.sh build_<name>.py`. Falling back to 2D bg." % req_glb)
		return false
	# Tear down the previously-loaded location
	if _location_instance != null and is_instance_valid(_location_instance):
		_location_instance.queue_free()
	_location_instance = null
	_staged_cast.clear()   # staged cast dies with the locale instance
	# Load + instantiate the new location
	var ps: PackedScene = load(spec.get("scene", "")) as PackedScene
	if ps == null:
		push_warning("[Background3D] Could not load scene %s" % spec.get("scene", ""))
		return false
	_location_instance = ps.instantiate()
	# CRITICAL: suppress interactive nodes BEFORE adding to tree.
	# Once added, every script in the locale's _ready cascade caches
	# references to the Player / HUD / etc — and the queue_free that
	# follows turns those caches into "previously freed" errors every
	# frame, eventually freezing the engine. Detaching pre-attach
	# means the doomed children's _ready never fires.
	if spec.get("suppress_input", false):
		_suppress_interactive_nodes(_location_instance)
	_anchor.add_child(_location_instance)
	# Position our SubViewport's own Camera3D + make it the current
	# camera for the World3D. The location's own Camera3D node (if
	# any) is overridden because make_current() pushes onto the
	# camera stack.
	_camera.position = spec.get("camera_origin", Vector3.ZERO)
	_camera.rotation = spec.get("camera_rotation", Vector3.ZERO)
	if spec.has("fov"):
		_camera.fov = float(spec["fov"])
	_camera.make_current()
	_loaded_preset = preset_id
	# Re-apply any user-stamped MoodCycler overrides for this preset.
	# Deferred a frame so the locale's PostProcess _ready has run and
	# index properties / apply methods are ready to be called.
	if Engine.has_singleton("VnDebugState") or get_node_or_null("/root/VnDebugState") != null:
		call_deferred("_reapply_locale_state")
	return true


func _reapply_locale_state() -> void:
	var state := get_node_or_null("/root/VnDebugState")
	if state == null:
		return
	var mc: Node = get_locale_mood_cycler()
	if mc == null:
		return
	state.apply_locale_state(_loaded_preset, mc)


func get_viewport_texture() -> Texture2D:
	return _viewport.get_texture()


# Move the SubViewport's camera live without going through a full
# load_location preset. Used by TarotGauntletGame to dial in
# per-board-space vantages in the gauntlet's FP view — the locale
# was loaded once via load_location("diner_interior"), then this
# method gets called per space change without re-instantiating
# anything.
func set_camera_vantage(origin: Vector3, rotation: Vector3, fov: float) -> void:
	if _camera == null or not is_instance_valid(_camera):
		return
	_camera.position = origin
	_camera.rotation = rotation
	_camera.fov = fov
	_camera.make_current()


# ── VnDirector hooks ─────────────────────────────────────────────
# The VN's shot system (lore/_VN_DIRECTION_PLAYBOOK.md): locale
# scenes carry Marker3D nodes named shot_<type>_<id> in group
# "vn_shot"; VnDirector cuts the SubViewport camera between them.

func get_camera() -> Camera3D:
	return _camera


func has_locale_loaded() -> bool:
	if _pending_preset != "":
		return false   # a queued load hasn't landed — director must wait
	return _location_instance != null and is_instance_valid(_location_instance)


func find_shot_marker(marker_name: String) -> Node3D:
	if not has_locale_loaded():
		return null
	return _location_instance.find_child(marker_name, true, false) as Node3D


# ── VN cast staging ──────────────────────────────────────────────
# [stage:<char> <spot>] places a character's hero GLB at the locale
# Marker3D named cast_<spot>; [stage:<char> off] removes them. The
# hero models are STATIC standing meshes — blocking for wide shots;
# faces stay on the 2D portrait layer (CharLayer). Missing GLB or
# missing spot marker = silent no-op (fallback discipline).
const CAST_GLB_ROOT := "res://assets/3d/characters/heroes/"
const CAST_KEY_TO_GLB := {
	"john": "john_frank.glb",       "john_frank": "john_frank.glb",
	"frasier": "frasier_temple.glb","frasier_temple": "frasier_temple.glb",
	"elicia": "elicia_temple.glb",  "elicia_temple": "elicia_temple.glb",
	"dante": "dante_dambrosio.glb", "dante_dambrosio": "dante_dambrosio.glb",
	"nicola": "nicola.glb",
	"alberto": "alberto.glb",
	"antonio": "antonio.glb",
	# Deck-only asset (not in the repo) — mapping is harmless when
	# the file is absent (stage_character no-ops on a missing GLB).
	"sam": "sam_miller.glb", "sam_miller": "sam_miller.glb",
}
# Asset-alignment table (audited 2026-07-11, corrected same day).
# ALL hero GLBs import UPRIGHT: five carry a node-level +90° X
# rotation over Z-up mesh data (verified against Portrait3D's live
# AABB logs — the raw mesh-space accessors lie about orientation),
# the other two are plain Y-up. Origin is body-center. "feet" =
# distance origin→soles; "scale" normalizes short exports to human
# height (dante's model is 1.08 m tall raw); "yaw" is a per-model
# facing nudge (radians) for exports whose front axis disagrees —
# dial in from playtest reports.
const CAST_MODEL_ALIGN := {
	"john_frank.glb":      {"feet": 0.96, "scale": 1.0, "yaw": 0.0},
	"frasier_temple.glb":  {"feet": 0.95, "scale": 1.0, "yaw": 0.0},
	"alberto.glb":         {"feet": 0.85, "scale": 1.0, "yaw": 0.0},
	"antonio.glb":         {"feet": 0.95, "scale": 1.0, "yaw": 0.0},
	"dante_dambrosio.glb": {"feet": 0.54, "scale": 1.6, "yaw": 0.0},
	"elicia_temple.glb":   {"feet": 0.95, "scale": 1.0, "yaw": 0.0},
	"nicola.glb":          {"feet": 0.95, "scale": 1.0, "yaw": 0.0},
	"sam_miller.glb":      {"feet": 0.95, "scale": 1.0, "yaw": 0.0},
}

var _staged_cast: Dictionary = {}   # char key -> {node, spawned}

# 2026-07-12 user direction: "remove characters from scenes for now,
# they don't look right — feature the setting and the props." The
# [stage:] grammar stays parsed (scene tags keep their blocking
# intent on record) but staging is a silent no-op until the
# character models earn their place. Flip to re-enable.
const CAST_ENABLED := false


func stage_character(char_id: String, spot: String) -> bool:
	if not CAST_ENABLED:
		return false
	if not has_locale_loaded():
		return false
	var key := char_id.to_lower()
	if spot == "off":
		if not _staged_cast.has(key):
			return false
		var rec: Dictionary = _staged_cast[key]
		var old: Variant = rec.get("node")
		if old is Node3D and is_instance_valid(old):
			if bool(rec.get("spawned", false)):
				(old as Node3D).queue_free()
			else:
				(old as Node3D).visible = false
		_staged_cast.erase(key)
		return true
	var marker := _location_instance.find_child("cast_" + spot, true, false) as Node3D
	if marker == null:
		push_warning("[Background3D] cast spot missing: cast_%s" % spot)
		return false
	var glb_file: String = String(CAST_KEY_TO_GLB.get(key, key + ".glb"))
	var node: Node3D = null
	var spawned := false
	if _staged_cast.has(key):
		var rec: Dictionary = _staged_cast[key]
		var cand: Variant = rec.get("node")
		if cand is Node3D and is_instance_valid(cand):
			node = cand
			spawned = bool(rec.get("spawned", false))
	if node == null:
		# Prefer the locale's own hidden Hero<FirstName> stand-in so
		# we don't double-load a GLB the scene already instanced.
		var hero_name := "Hero" + key.get_slice("_", 0).capitalize()
		node = _location_instance.find_child(hero_name, true, false) as Node3D
	if node == null:
		var path := CAST_GLB_ROOT + glb_file
		if not FileAccess.file_exists(path):
			push_warning("[Background3D] cast model missing: %s" % path)
			return false
		var ps := load(path) as PackedScene
		if ps == null:
			return false
		node = ps.instantiate() as Node3D
		if node == null:
			return false
		_location_instance.add_child(node)
		spawned = true
	_staged_cast[key] = {"node": node, "spawned": spawned}
	var align: Dictionary = CAST_MODEL_ALIGN.get(glb_file, {"feet": 0.95, "scale": 1.0, "yaw": 0.0})
	var s := float(align.get("scale", 1.0))
	node.visible = true
	node.global_rotation = Vector3(0.0, marker.global_rotation.y + float(align.get("yaw", 0.0)), 0.0)
	node.scale = Vector3(s, s, s)
	node.global_position = marker.global_position + Vector3(0, float(align.get("feet", 0.95)) * s, 0)
	return true


# The loaded preset's authored vantage — VnDirector derives its
# marker-free punch-in shots from this (never from the live camera,
# so repeated shots can't compound).
func get_preset_vantage() -> Dictionary:
	if _loaded_preset == "" or not CAMERA_PRESETS.has(_loaded_preset):
		return {}
	var spec: Dictionary = CAMERA_PRESETS[_loaded_preset]
	return {
		"origin": spec.get("camera_origin", Vector3.ZERO),
		"rotation": spec.get("camera_rotation", Vector3.ZERO),
		"fov": float(spec.get("fov", 60.0)),
	}


# Re-apply the loaded preset's authored vantage — the "establish"
# fallback and the director's release() restore.
func restore_preset_vantage() -> void:
	if _loaded_preset == "" or not CAMERA_PRESETS.has(_loaded_preset):
		return
	var spec: Dictionary = CAMERA_PRESETS[_loaded_preset]
	set_camera_vantage(
		spec.get("camera_origin", Vector3.ZERO),
		spec.get("camera_rotation", Vector3.ZERO),
		float(spec.get("fov", 60.0)))


# ── Internal ─────────────────────────────────────────────────────
func _suppress_interactive_nodes(root: Node) -> void:
	# Only KILL the Player CharacterBody3D (it'd compete for input
	# and move during VN dialogue). KEEP the locale's CanvasLayers
	# in the tree, but pre-hide the debug-flavoured ones so they
	# don't pop up uninvited every VN scene:
	# - PostProcess: stays VISIBLE. The bg-3D needs the same shader
	#   treatment the walkable locale gets (palette dither, ASCII,
	#   neon, etc).
	# - HUD: stays in the tree but starts HIDDEN. Contains
	#   DebugHUD label + DebugMenu — opt-in via F4 (HUD goes from
	#   hidden → visible on the next F4 sweep when hud_visible
	#   flips back to true). Default-off honours the user's
	#   "clean VN scenes" expectation.
	# Called BEFORE the locale instance is added to the SceneTree so
	# the removed Player's script never _ready()s and no sibling
	# script caches a reference to it that'd dangle when freed.
	var to_remove: Array[Node] = []
	for n: Node in _walk_tree(root):
		if n is CharacterBody3D and n.is_in_group("player"):
			to_remove.append(n)
		elif n is CanvasLayer:
			# Hide every debug-flavoured CanvasLayer by default in VN.
			# PostProcess (and any other non-HUD canvas) stays visible.
			var nm: String = n.name
			var is_debug_canvas: bool = (
				"HUD" in nm or "Hud" in nm or
				"Debug" in nm or "Menu" in nm or
				n.is_in_group("ui")
			)
			if is_debug_canvas:
				(n as CanvasLayer).visible = false
	for n in to_remove:
		var parent: Node = n.get_parent()
		if parent != null:
			parent.remove_child(n)
		n.queue_free()


func _walk_tree(node: Node, out: Array[Node] = []) -> Array[Node]:
	out.append(node)
	for child in node.get_children():
		_walk_tree(child, out)
	return out


# ── Public: hand the loaded locale's MoodCycler back to GameEngine
# so it can wire a per-VN-scene debug overlay without re-walking
# the SubViewport tree. Returns null until load_location has run.
func get_locale_mood_cycler() -> Node:
	if _location_instance == null or not is_instance_valid(_location_instance):
		return null
	return _location_instance.get_node_or_null("PostProcess")
