"""One-shot driver: emits gauntlet host scripts for the 16 new
Major-Arcana locales (batches A/B/C). Each host follows the
established convention (DinerGauntletHost / BungalowGauntletHost /
etc.): SPACE_MAP in Blender frame, position_player_at +
get_fp_camera_for_space with the Camera3D-yaw correction,
Ctrl+F12 launches the canonical scenario.

Run from anywhere — paths are resolved relative to the repo root.
"""
import os, sys
_HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(_HERE, "../../../.."))
SCRIPTS = os.path.join(REPO, "godot/scripts")


TEMPLATE = '''# {class_name}.gd
# ════════════════════════════════════════════════════════════════
# Host script that wires the Tarot Gauntlet for {arcana_label}
# ({hero_label} — {scenario_label}) into
# {locale_id}.tscn. Sister to DinerGauntletHost +
# CathedralGauntletHost + BungalowGauntletHost +
# RiverboatGauntletHost.
#
# Board-space positions match build_{locale_id}.py geometry.
# Camera-yaw convention: blender_yaw - 90 (Camera3D forward -Z,
# opposite of FPC body's +Z).
# ════════════════════════════════════════════════════════════════
extends Node3D

@export var player_path: NodePath = NodePath("../Player")
@export var auto_position_on_ready: bool = true
@export var launch_scene_path: String = "res://scenes/games/TarotGauntletGame.tscn"

const EYE_HEIGHT_CAMERA: float = 2.30

# Board-space ID → (Blender X, Blender Y, facing-yaw-degrees).
# Yaw: 0=+X east, 90=+Y north, 180=-X west, 270=-Y south.
const SPACE_MAP := {{
{space_map}
}}

var _player: CharacterBody3D = null
var _game: Node = null


func _ready() -> void:
\t_player = get_node_or_null(player_path) as CharacterBody3D
\tif _player == null or not is_instance_valid(_player):
\t\tpush_warning("[{class_name}] Player path '%s' not found" % player_path)
\tif auto_position_on_ready:
\t\tposition_player_at("{default_space}")


func _input(event: InputEvent) -> void:
\tif event is InputEventKey and event.pressed and not event.echo:
\t\tvar k := event as InputEventKey
\t\tif k.keycode == KEY_F12 and k.ctrl_pressed:
\t\t\t{launcher}()


# ── Public API ───────────────────────────────────────────────────
func position_player_at(space_id: String) -> void:
\tif _player == null or not is_instance_valid(_player):
\t\treturn
\tvar entry: Variant = SPACE_MAP.get(space_id, null)
\tif entry == null:
\t\tpush_warning("[{class_name}] Unknown space: %s" % space_id)
\t\treturn
\tvar b_x: float = entry[0]
\tvar b_y: float = entry[1]
\tvar yaw_deg: float = entry[2]
\tvar t := _player.global_transform
\tt.origin = Vector3(b_x, 0.0, -b_y)
\t_player.global_transform = t
\tvar godot_yaw_deg: float = 90.0 - yaw_deg
\t_player.rotation = Vector3(0.0, deg_to_rad(godot_yaw_deg), 0.0)


func sync_player_to_space(space_id: String) -> void:
\tposition_player_at(space_id)


# Per-space 3D FP camera vantage. See DinerGauntletHost docstring.
func get_fp_camera_for_space(space_id: String) -> Dictionary:
\tvar entry: Variant = SPACE_MAP.get(space_id, null)
\tif entry == null:
\t\treturn {{}}
\tvar b_x: float = entry[0]
\tvar b_y: float = entry[1]
\tvar yaw_deg: float = entry[2]
\tvar godot_yaw_deg: float = yaw_deg - 90.0
\treturn {{
\t\t"origin":   Vector3(b_x, EYE_HEIGHT_CAMERA, -b_y),
\t\t"rotation": Vector3(-0.05, deg_to_rad(godot_yaw_deg), 0.0),
\t\t"fov":      62.0,
\t}}


func {launcher}() -> void:
\tif _game != null and is_instance_valid(_game):
\t\tprint("[{class_name}] Gauntlet already running.")
\t\treturn
\tvar ps: PackedScene = load(launch_scene_path) as PackedScene
\tif ps == null:
\t\tpush_warning("[{class_name}] Could not load %s" % launch_scene_path)
\t\treturn
\t_game = ps.instantiate()
\tget_tree().root.add_child(_game)
\tif _game.has_method("start_scenario"):
\t\t_game.start_scenario("{arcana_key}", "{locale_id}", "{hero_id}",
\t\t                     "{scenario_id}", true)
\tif _game.has_signal("game_ended"):
\t\t_game.connect("game_ended",
\t\t              Callable(self, "_on_gauntlet_ended"))


func _on_gauntlet_ended(_outcome: String, _summary: Dictionary) -> void:
\tif _game != null and is_instance_valid(_game):
\t\t_game.queue_free()
\t_game = null
\tposition_player_at("{default_space}")
'''


# ── Per-host configs ─────────────────────────────────────────────
# Each entry's space_map is a list of (id, blender_x, blender_y, yaw_deg)
# tuples. Positions were chosen to match the build_*.py geometry —
# stations sit AT the prop with a yaw aimed at its iconic face.

HOSTS = [
    {
        "class_name": "ChapelGauntletHost",
        "arcana_label": "THE LOVERS",
        "arcana_key": "6_lovers",
        "hero_label": "Sanctuary scenarios",
        "hero_id": "tbd_lovers",
        "scenario_label": "Sanctuary on Cursed Ground",
        "scenario_id": "sanctuary_on_cursed_ground",
        "locale_id": "roadside_chapel",
        "launcher": "launch_sanctuary_on_cursed_ground",
        "default_space": "altar",
        "space_map": [
            ("altar",        0.00, 5.80, 270.0),  # at the altar facing congregants S
            ("pew_front",    0.00, 2.00,  90.0),  # forward pew, facing altar N
            ("pew_rear",     0.00, 3.80,  90.0),  # rear pew, facing altar N
            ("votive_rack",  1.40, 5.60, 180.0),  # at the rack facing W to altar
            ("statue_niche", 2.20, 3.40, 180.0),  # turned to statue (W)
            ("bell_pull",   -2.10, 0.60,   0.0),  # SW corner, facing E
            ("narthex",      0.00, 0.40,  90.0),  # threshold at entry, facing N
        ],
    },
    {
        "class_name": "RoulantCasinoGauntletHost",
        "arcana_label": "THE WHEEL OF FORTUNE",
        "arcana_key": "10_wheel_of_fortune",
        "hero_label": "TBD",
        "hero_id": "tbd_wheel",
        "scenario_label": "The House Edge",
        "scenario_id": "the_house_edge",
        "locale_id": "le_roulant_casino",
        "launcher": "launch_the_house_edge",
        "default_space": "roulette_table",
        "space_map": [
            ("roulette_table", 0.00, 4.50,  90.0),
            ("slot_bank",     -4.50, 3.20,   0.0),  # facing E
            ("cashier_cage",   3.50, 8.50,  90.0),  # facing the brass bars
            ("neon_sign",      0.00, 3.00,  90.0),  # under the hanging sign
            ("plaza_center",   0.00, 6.00,  90.0),
            ("front_door",     0.00, 0.40,  90.0),
        ],
    },
    {
        "class_name": "MixingGlassGauntletHost",
        "arcana_label": "TEMPERANCE",
        "arcana_key": "14_temperance",
        "hero_label": "Frank — Tuesday observation",
        "hero_id": "frank",
        "scenario_label": "Tuesday Observation",
        "scenario_id": "tuesday_observation",
        "locale_id": "mixing_glass",
        "launcher": "launch_tuesday_observation",
        "default_space": "bar_stool_mid",
        "space_map": [
            ("bar_stool_mid",  1.05, 5.60,   0.0),
            ("bar_stool_w",   -1.05, 5.60, 180.0),
            ("backbar",        0.00, 8.40, 270.0),  # behind the bar facing S
            ("booth_1",       -1.60, 1.20,   0.0),  # at table 1
            ("booth_2",       -1.60, 3.00,   0.0),
            ("booth_3",       -1.60, 4.80,   0.0),
            ("booth_4",       -1.60, 6.60,   0.0),
            ("neon_open",     -1.40, 7.80, 270.0),
            ("alley_door",     0.00, 0.40,  90.0),
        ],
    },
    {
        "class_name": "RoadhouseGauntletHost",
        "arcana_label": "THE DEVIL",
        "arcana_key": "15_devil",
        "hero_label": "TBD (Gumbo Limbo, Daigle's)",
        "hero_id": "tbd_devil",
        "scenario_label": "Gumbo Limbo Night",
        "scenario_id": "gumbo_limbo_night",
        "locale_id": "daigles_roadhouse",
        "launcher": "launch_gumbo_limbo_night",
        "default_space": "bar",
        "space_map": [
            ("bar",           0.00, 5.40,  90.0),   # bar-side, facing N
            ("bar_stool",     0.00, 5.60, 270.0),   # customer stool, facing S
            ("pool_table",    1.50, 3.20,  90.0),
            ("jukebox",      -4.10, 4.20,   0.0),
            ("gator_head",    2.30, 6.80,  90.0),
            ("schlitz_neon",  0.00, 6.80,  90.0),
            ("front_door",    0.00, 0.40,  90.0),
        ],
    },
    {
        "class_name": "DriveInGauntletHost",
        "arcana_label": "THE MOON",
        "arcana_key": "18_moon",
        "hero_label": "Natalie — Sigils in Static",
        "hero_id": "natalie",
        "scenario_label": "Sigils in Static",
        "scenario_id": "sigils_in_static",
        "locale_id": "static_drive_in",
        "launcher": "launch_sigils_in_static",
        "default_space": "counter",
        "space_map": [
            ("counter",        -1.60, 3.20, 270.0),  # behind register facing S
            ("popcorn",         1.00, 3.20, 270.0),
            ("soda_fountain",  -0.80, 3.10, 270.0),
            ("candy_case",      0.20, 3.20, 270.0),
            ("picture_window",  0.00, 4.60,  90.0),  # at glass facing screen
            ("lot_porch",       0.00, 0.40,  90.0),  # entry threshold
        ],
    },
    {
        "class_name": "ServiceGarageGauntletHost",
        "arcana_label": "THE CHARIOT",
        "arcana_key": "7_chariot",
        "hero_label": "TBD (the drive)",
        "hero_id": "tbd_chariot",
        "scenario_label": "Old Lacombe",
        "scenario_id": "old_lacombe",
        "locale_id": "lacombe_service_garage",
        "launcher": "launch_old_lacombe",
        "default_space": "bay_lift",
        "space_map": [
            ("bay_lift",      -2.50, 4.50,   0.0),   # facing E into bay
            ("tow_truck",      2.50, 4.50, 180.0),
            ("pegboard",       0.00, 7.80, 270.0),   # at workbench facing S
            ("toolbox",       -1.40, 8.20, 270.0),
            ("pump_island",    0.00,-1.20,  90.0),   # at island facing N into bays
            ("vending",        4.30, 1.00,   0.0),
        ],
    },
    {
        "class_name": "CarnivalLotGauntletHost",
        "arcana_label": "STRENGTH",
        "arcana_key": "8_strength",
        "hero_label": "TBD (the gentle tamer)",
        "hero_id": "tbd_strength",
        "scenario_label": "The Lion Cage Open",
        "scenario_id": "lion_cage_open",
        "locale_id": "carnival_lot",
        "launcher": "launch_lion_cage_open",
        "default_space": "merry_go_round",
        "space_map": [
            ("merry_go_round",   6.00,  0.00,   0.0),   # at center of carousel
            ("big_top",         -6.00,  0.00,   0.0),   # under tent center
            ("ticket_booth",     0.00,  7.00, 270.0),
            ("lion_cage",       -1.50, -5.50,  90.0),
            ("banner_posts",    -3.50, -7.00,  90.0),
            ("front_gate",       0.00, -9.00,  90.0),
        ],
    },
    {
        "class_name": "LighthouseGauntletHost",
        "arcana_label": "THE HERMIT",
        "arcana_key": "9_hermit",
        "hero_label": "TBD (the keeper)",
        "hero_id": "tbd_hermit",
        "scenario_label": "Watch Kept",
        "scenario_id": "watch_kept",
        "locale_id": "bayou_lighthouse",
        "launcher": "launch_watch_kept",
        "default_space": "writing_desk",
        "space_map": [
            ("writing_desk",   1.60, -0.20, 180.0),   # at desk facing the wall
            ("bunk",           0.00, -1.60,  90.0),
            ("spiral_stair",  -0.60, -0.60,   0.0),   # at base of stairs
            ("n_window",       0.00,  2.30,  90.0),
            ("lens_hatch",     0.00,  0.80,  90.0),   # under hatch, looking up
            ("door",           0.00, -2.30,  90.0),
        ],
    },
    {
        "class_name": "CourthouseGauntletHost",
        "arcana_label": "JUSTICE",
        "arcana_key": "11_justice",
        "hero_label": "Erica + Anna",
        "hero_id": "erica_anna",
        "scenario_label": "Motion to Dismiss",
        "scenario_id": "motion_to_dismiss",
        "locale_id": "courthouse_chamber",
        "launcher": "launch_motion_to_dismiss",
        "default_space": "plaintiff_table",
        "space_map": [
            ("judge_bench",      0.00, 9.80, 270.0),   # judge facing S to room
            ("witness_stand",    2.40, 9.60, 180.0),
            ("jury_box",        -3.70, 6.00,   0.0),
            ("plaintiff_table", -1.50, 5.50,  90.0),
            ("defense_table",    1.50, 5.50,  90.0),
            ("pew_front",        0.00, 1.50,  90.0),
            ("bar_rail",         0.00, 4.20,  90.0),
            ("flag_us",          3.20, 11.40,180.0),
            ("flag_state",      -3.20, 11.40,  0.0),
            ("rear_door",        0.00, 0.40,  90.0),
        ],
    },
    {
        "class_name": "SimonApartmentGauntletHost",
        "arcana_label": "THE HANGED MAN",
        "arcana_key": "12_hanged_man",
        "hero_label": "Natalie — at Simon's",
        "hero_id": "natalie",
        "scenario_label": "After Simon",
        "scenario_id": "after_simon",
        "locale_id": "simon_apartment",
        "launcher": "launch_after_simon",
        "default_space": "armchair",
        "space_map": [
            ("armchair",      0.50, 2.40, 180.0),     # facing TV W
            ("bed",           1.40, 5.70, 180.0),
            ("kitchenette", -1.80, 2.40,   0.0),
            ("tv",           -0.50, 2.20,   0.0),     # at TV facing chair E
            ("tipped_chair",-1.20, 3.20,  90.0),
            ("hanging_boot",-2.30, 5.50,   0.0),      # at the coat peg
            ("front_window", 0.00, 0.80, 270.0),      # at glass facing fire escape S
            ("front_door",   1.80, 0.40,  90.0),
        ],
    },
    {
        "class_name": "AsylumWardCGauntletHost",
        "arcana_label": "DEATH",
        "arcana_key": "13_death",
        "hero_label": "Ward C — Walpurgisnacht",
        "hero_id": "tbd_death",
        "scenario_label": "Walpurgisnacht",
        "scenario_id": "walpurgisnacht",
        "locale_id": "asylum_ward_c",
        "launcher": "launch_walpurgisnacht",
        "default_space": "nurses_station",
        "space_map": [
            ("nurses_station", 0.00, 7.00,  90.0),
            ("ward_1",        -2.40, 1.40,   0.0),   # at door, facing into room
            ("ward_2",        -2.40, 3.80,   0.0),
            ("ward_3",        -2.40, 6.20,   0.0),
            ("ward_4",        -2.40, 8.60,   0.0),
            ("ward_5",        -2.40, 11.00,  0.0),
            ("gurney",         0.40, 11.00, 180.0),
            ("wheelchair",    -1.20, 1.50,  90.0),
            ("cupola_below",   0.00, 13.20,  90.0),   # under cupola, looking up
            ("corridor_s",     0.00, 0.40,  90.0),
        ],
    },
    {
        "class_name": "WgurShackGauntletHost",
        "arcana_label": "THE TOWER",
        "arcana_key": "16_tower",
        "hero_label": "Evangeline — render queue",
        "hero_id": "evangeline",
        "scenario_label": "Render Queue",
        "scenario_id": "render_queue",
        "locale_id": "wgur_transmitter_shack",
        "launcher": "launch_render_queue",
        "default_space": "operator_desk",
        "space_map": [
            ("operator_desk", -0.40, 1.40,  90.0),
            ("rack_a",        -2.20, 1.20,   0.0),
            ("rack_b",        -2.20, 2.00,   0.0),
            ("rack_c",        -2.20, 2.80,   0.0),
            ("patch_panel",    2.20, 2.20, 180.0),
            ("mic_stand",     -0.70, 1.40,  90.0),
            ("n_window",       0.00, 3.80,  90.0),
            ("door",           0.00, 0.40,  90.0),
        ],
    },
    {
        "class_name": "ChristianIceGauntletHost",
        "arcana_label": "THE STAR",
        "arcana_key": "17_star",
        "hero_label": "Glass Skin / Christian Ice",
        "hero_id": "tbd_star",
        "scenario_label": "Glass Skin",
        "scenario_id": "glass_skin",
        "locale_id": "christian_ice_co",
        "launcher": "launch_glass_skin",
        "default_space": "retail_counter",
        "space_map": [
            ("retail_counter", 0.00, 2.40, 270.0),   # behind counter facing S
            ("block_freezer",  0.00, 3.80,  90.0),   # at freezer facing N
            ("chest_freezer_a", -3.90, 4.50,   0.0),
            ("chest_freezer_b", -3.90, 6.30,   0.0),
            ("chest_freezer_c", -3.90, 8.10,   0.0),
            ("compressor_1",    1.80, 6.50, 180.0),
            ("brine_tank",      1.80, 8.50, 180.0),
            ("dock_door",       0.00, 10.60, 270.0),
            ("storefront",      0.00, 0.40,  90.0),
        ],
    },
    {
        "class_name": "SolenadeGardenGauntletHost",
        "arcana_label": "THE SUN",
        "arcana_key": "19_sun",
        "hero_label": "Frank — dust motes",
        "hero_id": "frank",
        "scenario_label": "Dust Motes",
        "scenario_id": "dust_motes",
        "locale_id": "solenade_garden",
        "launcher": "launch_dust_motes",
        "default_space": "central_oak",
        "space_map": [
            ("central_oak",   0.00,  0.00,  90.0),
            ("sundial",       0.00, -3.40,  90.0),
            ("bench_n",       0.00,  7.40, 270.0),
            ("bench_s",       0.00, -7.40,  90.0),
            ("bench_e",       7.40,  0.00, 180.0),
            ("bench_w",      -7.40,  0.00,   0.0),
            ("pergola_arch",  0.00,  7.80, 270.0),
            ("flowerbed_ne",  3.00,  3.00,   0.0),
            ("flowerbed_nw", -3.00,  3.00,   0.0),
            ("gate",          0.00, -7.80,  90.0),
        ],
    },
    {
        "class_name": "ParishCemeteryGauntletHost",
        "arcana_label": "JUDGEMENT",
        "arcana_key": "20_judgement",
        "hero_label": "Ensemble — dust notes",
        "hero_id": "ensemble",
        "scenario_label": "Everyone Stays",
        "scenario_id": "everyone_stays",
        "locale_id": "parish_cemetery",
        "launcher": "launch_everyone_stays",
        "default_space": "central_mausoleum",
        "space_map": [
            ("central_mausoleum", 0.00,  0.00, 270.0),  # at door facing S
            ("path_spine_n",      0.00,  5.00, 270.0),
            ("path_spine_s",      0.00, -5.00,  90.0),
            ("vault_row_w",      -7.00,  0.00,   0.0),
            ("vault_row_e",       7.00,  0.00, 180.0),
            ("vault_row_n",       0.00,  7.00, 270.0),
            ("lamp_central",      1.20,  0.00, 180.0),
            ("oak_sw",           -8.50, -8.00,   0.0),
            ("gate",              0.00, -9.00,  90.0),
        ],
    },
    {
        "class_name": "FrogKnowsBestGauntletHost",
        "arcana_label": "THE WORLD",
        "arcana_key": "21_world",
        "hero_label": "Frog Knows Best",
        "hero_id": "tbd_world",
        "scenario_label": "Loop Completed",
        "scenario_id": "loop_completed",
        "locale_id": "frog_knows_best",
        "launcher": "launch_loop_completed",
        "default_space": "retail_counter",
        "space_map": [
            ("retail_counter",  0.00, 2.20, 270.0),
            ("minnow_tank",    -1.70, 6.50,  90.0),
            ("catfish_tank",    0.00, 6.50,  90.0),
            ("frog_tank",       1.70, 6.50,  90.0),
            ("nightcrawler",    2.40, 2.20, 180.0),
            ("pegboard_w",     -2.90, 3.50,   0.0),
            ("pegboard_e",      2.90, 3.50, 180.0),
            ("porch",           0.00,-1.60,  90.0),
            ("front_door",      0.00, 0.40,  90.0),
        ],
    },
]


def fmt_space_map(entries):
    longest = max(len(e[0]) for e in entries)
    lines = []
    for sid, bx, by, yaw in entries:
        pad = " " * (longest - len(sid))
        lines.append(f'\t"{sid}":{pad} [{bx:+.2f}, {by:+.2f}, {yaw:>5.1f}],')
    return "\n".join(lines)


def main():
    written = []
    for cfg in HOSTS:
        body = TEMPLATE.format(
            class_name=cfg["class_name"],
            arcana_label=cfg["arcana_label"],
            arcana_key=cfg["arcana_key"],
            hero_label=cfg["hero_label"],
            hero_id=cfg["hero_id"],
            scenario_label=cfg["scenario_label"],
            scenario_id=cfg["scenario_id"],
            locale_id=cfg["locale_id"],
            launcher=cfg["launcher"],
            default_space=cfg["default_space"],
            space_map=fmt_space_map(cfg["space_map"]),
        )
        out = os.path.join(SCRIPTS, cfg["class_name"] + ".gd")
        with open(out, "w") as f:
            f.write(body)
        written.append(out)
        print(f"  ✓ {out}")
    print(f"\nwrote {len(written)} gauntlet host scripts")


if __name__ == "__main__":
    main()
