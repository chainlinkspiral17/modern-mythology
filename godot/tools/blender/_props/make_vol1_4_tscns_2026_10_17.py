"""One-shot: locale tscns for the vols 1-4 sets built 2026-10-17 (draft 1).

The user: "go ahead and start working on backgrounds for vol 1-4 as needed."
Same contract as make_vol1_4_tscns_2026_10_16.py: write_locale_tscn with
full parity; light positions come from the builder's geometry (blender
(x, y, z) -> godot (x, z, -y)); a light named `<name>__<preset>` plays only
in that preset (Background3D drops it everywhere else). Run with plain
python3 from the repo root.
"""
import os, sys
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
from _props.make_locale_tscn import write_locale_tscn

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "..", "..", "scenes", "locales"))

I = "Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {}, {}, {})"
B_FILL = "Transform3D(-0.707, -0.354, -0.612, 0, 0.866, -0.5, 0.707, -0.354, -0.612, {}, {}, {})"
B_BACK = "Transform3D(0.707, -0.5, 0.5, 0, 0.707, 0.707, -0.707, -0.5, 0.5, {}, {}, {})"
# travels SOUTH (godot +z, in from north windows), 45 deg down — checked by light_direction_audit
B_KEY_FROM_N = "Transform3D(-1, 0, 0, 0, 0.707, 0.707, 0, 0.707, -0.707, {}, {}, {})"
# travels NORTH (godot -z, in through south windows), 45 deg down
B_SUN_FROM_S = "Transform3D(1, 0, 0, 0, 0.707, 0.707, 0, -0.707, 0.707, {}, {}, {})"


def c(r, g, b):
    return "Color({}, {}, {}, 1)".format(r, g, b)


SLEEP_WORK = ("sleep_lab_entry", "sleep_lab_desk")
NOT_BEAM = "__sleep_lab_entry__sleep_lab_desk__sleep_lab_night__four_screens_wide__four_screens_show"
COURT = "__dabney_courtyard__dabney_courtyard_1945__dabney_side_yard"
GAME = "__dabney_game_room__dabney_couch__dabney_couch_carving"
TUN_LIT = "__caltech_tunnels__caltech_hallway_1945__caltech_bare_room"
LAX = "__lax_gate__lax_store__lax_seat_close"
CABIN = "__plane_night__plane_day__plane_vol4"
ONEI = "__onei_office__onei_office_desk__onei_office_door"
CLUBO = "__club_office__club_office_after"
CHAU = "__chau_hall_noon__chau_entry_morning__chau_living__chau_bath__chau_game_room"
AMANDA = "__amanda_hot_tub__amanda_fort__amanda_fort_close"
SHOP = "__copy_shop_floor__copy_shop_wastebasket__copy_shop_copier"
P45 = "__street_day__park_chess__hollywood_shoot"
SUITE = "__suite_wide__suite_tide__suite_4am"
NIGHT_BED = ("andy_house_bedroom_night", "andy_house_bedroom_lamp")

CONFIGS = [
    {
        # VOL 3's LINK HOUSE (build_link_house.py): a ranch house in Texas
        # after dark — every room on its own lamps. The day presets
        # (bathroom, bedroom) add their window light by name and lift the
        # environment in Background3D.
        "out_path": os.path.join(ROOT, "link_house.tscn"),
        "uid": "uid://link_house_v3",
        "root_node": "LinkHouse",
        "glb": "res://assets/3d/locales/link_house.glb",
        "env": {"bg": (0.04, 0.05, 0.08, 1), "amb": (0.40, 0.42, 0.52, 1),
                "amb_e": 0.40, "fog": (0.16, 0.17, 0.22, 1), "fog_e": 0.25,
                "fog_d": 0.003, "sat": 0.94, "glow_i": 0.65, "glow_b": 0.12},
        "shader": {"warm": (0.94, 0.84, 0.64, 1), "bg": (0.08, 0.08, 0.10, 1),
                   "neon_edge": (0.74, 0.64, 0.44, 1), "neon_lo": (0.30, 0.24, 0.18, 1),
                   "neon_hi": (0.08, 0.08, 0.10, 1), "lim_tint": (0.70, 0.58, 0.42, 1)},
        "lights": [
            ("Key_Night", "DirectionalLight3D", B_KEY_FROM_N.format(0, 6, -12), c(0.52, 0.58, 0.80), 0.22),
            ("Fill_Room", "DirectionalLight3D", B_FILL.format(0, 3, -5), c(0.70, 0.62, 0.52), 0.14),
            ("Back", "DirectionalLight3D", B_BACK.format(0, 3, 0), c(0.40, 0.42, 0.56), 0.10),
            # the living room's end-table lamp (blender (-3.30, 4.25, 1.03))
            ("Practical_LivingLamp", "OmniLight3D", I.format(-3.30, 1.03, -4.25), c(1.0, 0.84, 0.58), 1.3,
             {"omni_range": 4.5}),
            # the TV's screen, on in the living-room night (the scary movie marathon)
            ("TV_Glow__andy_house_living", "OmniLight3D", I.format(-5.70, 0.95, -2.80), c(0.56, 0.70, 1.0), 1.6,
             {"omni_range": 4.2}),
            # the pendant over the dining table (blender (4.10, 2.20, 1.75))
            ("Practical_Pendant", "OmniLight3D", I.format(4.10, 1.70, -2.20), c(1.0, 0.82, 0.56), 1.6,
             {"omni_range": 4.5}),
            ("Practical_KitchenCeiling", "OmniLight3D", I.format(3.40, 2.40, -3.80), c(1.0, 0.94, 0.84), 0.9,
             {"omni_range": 5.0}),
            ("Practical_Hall", "OmniLight3D", I.format(0.0, 2.40, -6.10), c(1.0, 0.92, 0.78), 0.7,
             {"omni_range": 4.0}),
            # the vanity's light bar (blender (1.39, 8.35, 1.95))
            ("Practical_Vanity", "OmniLight3D", I.format(1.25, 1.95, -8.35), c(1.0, 0.94, 0.82), 1.4,
             {"omni_range": 3.6}),
            # Andy's room at night: the bedside lamp (blender (6.16, 9.45, 0.97)), the desk lamp
            *[("Lamp_Bed__" + p, "OmniLight3D", I.format(6.10, 1.0, -9.40), c(1.0, 0.82, 0.54), 1.2,
               {"omni_range": 3.8}) for p in NIGHT_BED],
            *[("Lamp_Desk__" + p, "OmniLight3D", I.format(4.48, 1.06, -10.10), c(0.96, 0.92, 0.80), 0.6,
               {"omni_range": 2.6}) for p in NIGHT_BED],
            # the day presets: window light by name
            ("Sky_N__andy_house_bedroom", "DirectionalLight3D", B_KEY_FROM_N.format(4, 4, -12), c(0.90, 0.92, 1.0), 0.75),
            ("Window_N__andy_house_bedroom", "OmniLight3D", I.format(4.0, 1.6, -9.9), c(0.92, 0.94, 1.0), 1.6,
             {"omni_range": 5.5}),
            ("Window_N__andy_house_bath", "OmniLight3D", I.format(-0.30, 1.8, -10.0), c(0.96, 0.96, 0.98), 2.2,
             {"omni_range": 4.5}),
            ("Sun_S__andy_house_kitchen", "DirectionalLight3D", B_SUN_FROM_S.format(2, 6, 6), c(1.0, 0.70, 0.46), 0.35),
        ],
        "mood_strata": ["raw", "memory_warm", "lithograph", "noir",
                        "candlelight", "silent_film_18"],
    },
    {
        # VOL 2's SMALL WOOD RANCH (build_small_wood_ranch.py): the
        # narrator's room at night — the reading lamp and the moon through
        # the plank blinds; the second house (x 30..34) on its kerosene
        # lamp. "The same afternoon" (Dean's rebuilt room) is the day
        # preset: its sky and window light by name.
        "out_path": os.path.join(ROOT, "small_wood_ranch.tscn"),
        "uid": "uid://small_wood_ranch_v2",
        "root_node": "SmallWoodRanch",
        "glb": "res://assets/3d/locales/small_wood_ranch.glb",
        "env": {"bg": (0.03, 0.04, 0.07, 1), "amb": (0.36, 0.40, 0.52, 1),
                "amb_e": 0.38, "fog": (0.14, 0.16, 0.22, 1), "fog_e": 0.3,
                "fog_d": 0.004, "sat": 0.90, "glow_i": 0.7, "glow_b": 0.12},
        "shader": {"warm": (0.92, 0.82, 0.62, 1), "bg": (0.07, 0.08, 0.10, 1),
                   "neon_edge": (0.70, 0.62, 0.44, 1), "neon_lo": (0.28, 0.24, 0.18, 1),
                   "neon_hi": (0.07, 0.08, 0.10, 1), "lim_tint": (0.62, 0.58, 0.48, 1)},
        "lights": [
            ("Key_Moon", "DirectionalLight3D", B_KEY_FROM_N.format(0, 6, -8), c(0.60, 0.68, 0.92), 0.28),
            ("Fill_Room", "DirectionalLight3D", B_FILL.format(0, 3, -2), c(0.62, 0.58, 0.54), 0.12),
            ("Back", "DirectionalLight3D", B_BACK.format(0, 3, 1), c(0.40, 0.44, 0.58), 0.10),
            # the reading lamp on the nightstand (blender (-0.45, 3.92, 0.91)), the night presets
            *[("Lamp_Reading__" + p, "OmniLight3D", I.format(-0.45, 0.92, -3.90), c(1.0, 0.82, 0.54), 1.3,
               {"omni_range": 3.6}) for p in ("ranch_bedroom_night", "ranch_bedroom_lamp")],
            # the moon at the N window
            *[("Moon_Window__" + p, "OmniLight3D", I.format(0.20, 1.5, -3.95), c(0.62, 0.70, 0.96), 0.8,
               {"omni_range": 3.4}) for p in ("ranch_bedroom_night", "ranch_bedroom_lamp")],
            # the afternoon: sky through the N window
            ("Sky_N__ranch_bedroom_day", "DirectionalLight3D", B_KEY_FROM_N.format(0, 6, -8), c(0.92, 0.94, 1.0), 0.7),
            ("Window_N__ranch_bedroom_day", "OmniLight3D", I.format(0.20, 1.5, -3.85), c(0.92, 0.94, 1.0), 1.8,
             {"omni_range": 5.0}),
            # the second house: the kerosene lamp on its crate (blender (31.95, 1.70, 0.55)),
            # the cold through the gone E window
            ("Kerosene_Lamp", "OmniLight3D", I.format(31.95, 0.62, -1.70), c(1.0, 0.70, 0.36), 1.8,
             {"omni_range": 4.6}),
            ("Window_Gone_E", "OmniLight3D", I.format(33.70, 1.40, -1.80), c(0.56, 0.64, 0.90), 0.5,
             {"omni_range": 2.6}),
        ],
        "mood_strata": ["raw", "memory_warm", "noir", "candlelight",
                        "lithograph", "silent_film_18"],
    },
    {
        # VOL 3's SLEEP LAB (build_sleep_lab.py): a windowless basement
        # office at Caltech — at work on its floor lamp, desk lamp and the
        # CRT; after lights-out only the glow from behind the black curtain
        # and the corridor's light under the shut door. The four-screen
        # room (x 31..49) shares the file: dim house cans, the four lit
        # walls, or the dark and one slanting beam (meld_seam_2_3).
        "out_path": os.path.join(ROOT, "sleep_lab.tscn"),
        "uid": "uid://sleep_lab_v3",
        "root_node": "SleepLab",
        "glb": "res://assets/3d/locales/sleep_lab.glb",
        "env": {"bg": (0.02, 0.02, 0.03, 1), "amb": (0.34, 0.34, 0.40, 1),
                "amb_e": 0.30, "fog": (0.10, 0.10, 0.12, 1), "fog_e": 0.2,
                "fog_d": 0.004, "sat": 0.92, "glow_i": 0.75, "glow_b": 0.12},
        "shader": {"warm": (0.92, 0.82, 0.62, 1), "bg": (0.05, 0.05, 0.07, 1),
                   "neon_edge": (0.62, 0.66, 0.78, 1), "neon_lo": (0.22, 0.22, 0.26, 1),
                   "neon_hi": (0.05, 0.05, 0.07, 1), "lim_tint": (0.52, 0.56, 0.70, 1)},
        "lights": [
            # the foundation plays everywhere but the beam (meld_seam_2_3 is black)
            ("Key_Room" + NOT_BEAM, "DirectionalLight3D", B_KEY_FROM_N.format(0, 6, -8), c(0.70, 0.70, 0.80), 0.08),
            ("Fill_Room" + NOT_BEAM, "DirectionalLight3D", B_FILL.format(0, 3, -3), c(0.66, 0.60, 0.54), 0.06),
            ("Back" + NOT_BEAM, "DirectionalLight3D", B_BACK.format(0, 3, 1), c(0.40, 0.42, 0.56), 0.05),
            # at work: the floor lamp by Bed_A (blender (-2.55, 4.55, 1.40)), the
            # desk lamp on the test desk, the test CRT's screen
            *[("Lamp_Floor__" + p, "OmniLight3D", I.format(-2.55, 1.40, -4.55), c(1.0, 0.80, 0.52), 1.4,
               {"omni_range": 5.0}) for p in SLEEP_WORK],
            *[("Lamp_Desk__" + p, "OmniLight3D", I.format(2.74, 1.15, -1.32), c(1.0, 0.86, 0.62), 0.9,
               {"omni_range": 2.8}) for p in SLEEP_WORK],
            *[("CRT_Glow__" + p, "OmniLight3D", I.format(2.30, 0.98, -2.20), c(0.62, 0.74, 0.86), 0.5,
               {"omni_range": 1.8}) for p in SLEEP_WORK],
            # the corridor's tubes through the open door (work) or under it (night)
            *[("Fluor_Corr_1__" + p, "OmniLight3D", I.format(-1.0, 2.45, 1.35), c(0.92, 0.96, 0.92), 1.2,
               {"omni_range": 5.0}) for p in SLEEP_WORK],
            ("Door_Spill__sleep_lab_night", "OmniLight3D", I.format(-1.30, 0.05, -0.25), c(0.86, 0.92, 0.88), 0.45,
             {"omni_range": 1.3}),
            # behind the curtain, always: the Sun's CRT (blender (2.09, 4.64, 1.03))
            ("Curtain_Glow", "OmniLight3D", I.format(2.10, 1.05, -4.30), c(0.56, 0.66, 0.92), 0.9,
             {"omni_range": 4.2}),
            # the four-screen room: the house cans (wide), the four lit walls (show)
            *[("House_Light_{}__four_screens_wide".format(k), "OmniLight3D", I.format(x, 6.4, -y), c(1.0, 0.86, 0.66), 2.4,
               {"omni_range": 15.0}) for k, (x, y) in enumerate(((35.0, 5.0), (45.0, 5.0), (35.0, 13.0), (45.0, 13.0)))],
            ("Screen_N_Glow__four_screens_show", "OmniLight3D", I.format(40.0, 3.5, -15.6), c(0.96, 0.80, 0.60), 1.8,
             {"omni_range": 15.0}),
            ("Screen_E_Glow__four_screens_show", "OmniLight3D", I.format(46.6, 3.5, -9.0), c(0.96, 0.62, 0.46), 1.2,
             {"omni_range": 12.0}),
            ("Screen_W_Glow__four_screens_show", "OmniLight3D", I.format(33.4, 3.5, -9.0), c(0.56, 0.80, 0.66), 1.0,
             {"omni_range": 12.0}),
            ("Screen_S_Glow__four_screens_show", "OmniLight3D", I.format(40.0, 3.5, -2.4), c(0.56, 0.66, 0.96), 1.0,
             {"omni_range": 12.0}),
            # (a Transform3D's nine basis numbers are ROWS: x.x, y.x, z.x, x.y, …)
            # meld_seam_2_3: the beam at a slant from the stalk's head (blender (43.6, 13.5, 5.7))
            # to the open floor north of the island (40.0, 15.6); its eyes, lit from
            # the camera's side of the head so they read as points
            ("Stalk_Beam__four_screens_beam", "SpotLight3D", "Transform3D(0.505, -0.680, 0.531, 0.000, 0.615, 0.788, -0.863, -0.399, 0.311, 43.500, 5.200, -13.550)",
             c(1.0, 0.94, 0.80), 9.0, {"spot_range": 10.0, "spot_angle": 12.0}),
            ("Stalk_Eyes__four_screens_beam", "OmniLight3D", I.format(43.0, 5.0, -13.8), c(1.0, 0.90, 0.66), 1.6,
             {"omni_range": 1.5}),
        ],
        "mood_strata": ["raw", "noir", "memory_warm", "lithograph",
                        "candlelight", "silent_film_18"],
    },
    {
        # VOL 3's CALTECH (build_caltech_dabney.py): Dabney's courtyard and
        # side yard by afternoon sun (2003 and 1945, one camera); the
        # basement game room lit only by its screens, fridges and the
        # cabinet's attract mode; Spencer's room by its window; the tunnels
        # under fluorescent tubes, the racquetball room's red and blue
        # lanterns spilling out (2003); the bare room's one bulb, or only
        # the light under its door. Each area's lights carry its presets.
        "out_path": os.path.join(ROOT, "caltech_dabney.tscn"),
        "uid": "uid://caltech_dabney_v3",
        "root_node": "CaltechDabney",
        "glb": "res://assets/3d/locales/caltech_dabney.glb",
        "env": {"bg": (0.56, 0.72, 0.92, 1), "amb": (0.82, 0.84, 0.90, 1),
                "amb_e": 0.65, "fog": (0.80, 0.84, 0.90, 1), "fog_e": 0.4,
                "fog_d": 0.002, "sat": 0.98, "glow_i": 0.6, "glow_b": 0.14},
        "shader": {"warm": (0.96, 0.88, 0.70, 1), "bg": (0.10, 0.10, 0.12, 1),
                   "neon_edge": (0.80, 0.70, 0.52, 1), "neon_lo": (0.30, 0.26, 0.20, 1),
                   "neon_hi": (0.10, 0.10, 0.12, 1), "lim_tint": (0.76, 0.66, 0.50, 1)},
        "lights": [
            # the courtyard and side yard: Pasadena afternoon, the sun from the south-west
            ("Key_Sun" + COURT, "DirectionalLight3D", B_SUN_FROM_S.format(0, 12, 10), c(1.0, 0.92, 0.78), 1.4),
            ("Fill_Sky" + COURT, "DirectionalLight3D", B_FILL.format(0, 8, -4), c(0.66, 0.76, 0.96), 0.35),
            ("Back" + COURT, "DirectionalLight3D", B_BACK.format(0, 8, 4), c(0.90, 0.86, 0.80), 0.25),
            # the game room (blender x 60..72): the wall of screens, the fridges, the cabinet, the PC
            ("Key_Game" + GAME, "DirectionalLight3D", B_KEY_FROM_N.format(66, 4, -6), c(0.56, 0.60, 0.80), 0.06),
            ("Screen_Wall_Glow_L" + GAME, "OmniLight3D", I.format(63.6, 1.3, -8.9), c(0.56, 0.66, 0.96), 2.2,
             {"omni_range": 8.0}),
            ("Screen_Wall_Glow_R" + GAME, "OmniLight3D", I.format(67.8, 1.5, -8.9), c(0.70, 0.60, 0.92), 2.0,
             {"omni_range": 8.0}),
            # the screens' light falling back on the couches
            ("Screen_Bounce" + GAME, "OmniLight3D", I.format(66.0, 1.3, -6.0), c(0.56, 0.62, 0.92), 0.8, {"omni_range": 4.8}),
            ("Fridge_Glow" + GAME, "OmniLight3D", I.format(70.9, 1.3, -3.0), c(0.86, 0.92, 1.0), 0.9,
             {"omni_range": 3.6}),
            ("Arcade_Glow" + GAME, "OmniLight3D", I.format(61.4, 1.3, -2.7), c(0.80, 0.46, 0.96), 0.8,
             {"omni_range": 2.6}),
            ("PC_Glow" + GAME, "OmniLight3D", I.format(60.9, 1.1, -8.6), c(0.56, 0.86, 0.76), 0.4,
             {"omni_range": 1.8}),
            # Spencer's room (x 80..84.6): the afternoon through the E window
            ("Key_Spencer__spencer_room", "DirectionalLight3D", B_KEY_FROM_N.format(82, 4, -4), c(0.92, 0.90, 0.84), 0.30),
            ("Window_E__spencer_room", "OmniLight3D", I.format(84.1, 1.6, -2.4), c(1.0, 0.94, 0.82), 1.8,
             {"omni_range": 5.5}),
            # the tunnels (x 100..103.2): a tube every 6 m, for both years and the lit bare room
            *[("Fluor_Tun_{}".format(k) + TUN_LIT, "OmniLight3D", I.format(101.6, 2.62, -(3.0 + k * 6.0)),
               c(0.90, 0.96, 0.90), 1.0, {"omni_range": 5.0}) for k in range(10)],
            ("Key_Tun" + TUN_LIT, "DirectionalLight3D", B_KEY_FROM_N.format(101, 3, -10), c(0.80, 0.84, 0.80), 0.06),
            ("Lantern_Red__caltech_tunnels", "OmniLight3D", I.format(93.0, 4.5, -18.5), c(1.0, 0.24, 0.20), 2.2,
             {"omni_range": 9.0}),
            ("Lantern_Blue__caltech_tunnels", "OmniLight3D", I.format(97.2, 4.5, -23.5), c(0.26, 0.38, 1.0), 2.2,
             {"omni_range": 9.0}),
            ("Clean_Room_Glow__caltech_tunnels", "OmniLight3D", I.format(98.5, 2.3, -34.0), c(0.92, 0.96, 1.0), 1.2,
             {"omni_range": 4.0}),
            # the bare room (x 103.2..106.4): its one bulb (lit), or the corridor's light under the shut door
            ("Bare_Bulb__caltech_bare_room", "OmniLight3D", I.format(104.8, 2.24, -7.6), c(1.0, 0.92, 0.76), 2.0,
             {"omni_range": 5.0}),
            ("Door_Spill__caltech_bare_room_dark", "OmniLight3D", I.format(103.36, 0.04, -7.6), c(0.82, 0.94, 0.84), 0.6,
             {"omni_range": 1.4}),
        ],
        "mood_strata": ["raw", "memory_warm", "lithograph", "noir",
                        "candlelight", "silent_film_18"],
    },
    {
        # VOL 3's AIRPORT (build_airport_cabin.py): the gate at LAX under
        # its ceiling panels, the convenience store lit across the
        # concourse; the economy cabin (x 56..64) at night (the cove low,
        # Andy's reading lamp, the headrest monitor), by day (the windows),
        # and vol 4's November flight (dim and warm, the shades down).
        "out_path": os.path.join(ROOT, "airport_cabin.tscn"),
        "uid": "uid://airport_cabin_v3",
        "root_node": "AirportCabin",
        "glb": "res://assets/3d/locales/airport_cabin.glb",
        "env": {"bg": (0.03, 0.03, 0.05, 1), "amb": (0.70, 0.72, 0.78, 1),
                "amb_e": 0.40, "fog": (0.30, 0.30, 0.34, 1), "fog_e": 0.2,
                "fog_d": 0.002, "sat": 0.94, "glow_i": 0.6, "glow_b": 0.14},
        "shader": {"warm": (0.94, 0.88, 0.74, 1), "bg": (0.08, 0.08, 0.10, 1),
                   "neon_edge": (0.70, 0.70, 0.66, 1), "neon_lo": (0.26, 0.26, 0.28, 1),
                   "neon_hi": (0.08, 0.08, 0.10, 1), "lim_tint": (0.66, 0.66, 0.70, 1)},
        "lights": [
            ("Key_Gate" + LAX, "DirectionalLight3D", B_KEY_FROM_N.format(0, 8, -20), c(0.90, 0.92, 0.96), 0.25),
            ("Fill_Gate" + LAX, "DirectionalLight3D", B_FILL.format(0, 5, -20), c(0.80, 0.80, 0.84), 0.15),
            ("Back" + LAX, "DirectionalLight3D", B_BACK.format(0, 5, -10), c(0.70, 0.72, 0.80), 0.10),
            # the ceiling's light panels, three rows of three
            *[("Gate_Overhead_{}_{}".format(i, j) + LAX, "OmniLight3D", I.format(x, 5.1, -y), c(0.96, 0.96, 0.92), 1.3,
               {"omni_range": 11.0}) for i, x in enumerate((-8.0, 0.0, 8.0)) for j, y in enumerate((8.5, 20.0, 31.5))],
            # the store: bright inside, spilling out through its glass
            ("Store_Glow_S" + LAX, "OmniLight3D", I.format(8.0, 2.8, -19.5), c(1.0, 0.96, 0.86), 2.0, {"omni_range": 7.5}),
            ("Store_Glow_N" + LAX, "OmniLight3D", I.format(8.0, 2.8, -26.5), c(1.0, 0.96, 0.86), 2.0, {"omni_range": 7.5}),
            # the cabin (aisle x 60)
            ("Key_Cabin" + CABIN, "DirectionalLight3D", B_KEY_FROM_N.format(60, 4, -6), c(0.80, 0.82, 0.90), 0.08),
            *[("Cove_Night_{}__plane_night".format(k), "OmniLight3D", I.format(60.0, 2.0, -y), c(0.50, 0.56, 0.90), 0.35,
               {"omni_range": 5.0}) for k, y in enumerate((3.5, 8.0, 12.5))],
            # Andy's "satellite lamp" (blender (61.57, 7.97, 1.73)), straight down onto his seat
            ("Reading_Lamp__plane_night", "SpotLight3D", "Transform3D(1, 0, 0, 0, 0, 1, 0, -1, 0, 61.57, 1.72, -7.97)",
             c(1.0, 0.92, 0.74), 3.0, {"spot_range": 2.2, "spot_angle": 24.0}),
            ("Monitor_Glow__plane_night", "OmniLight3D", I.format(61.3, 1.02, -8.2), c(0.62, 0.74, 1.0), 0.6,
             {"omni_range": 1.8}),
            *[("Window_Day_{}_{}__plane_day".format(s, k), "OmniLight3D", I.format(60.0 + s * 1.55, 1.25, -y), c(0.92, 0.95, 1.0), 0.9,
               {"omni_range": 3.2}) for s in (-1, 1) for k, y in enumerate((3.4, 7.6, 11.8))],
            *[("Cove_Warm_{}__plane_vol4".format(k), "OmniLight3D", I.format(60.0, 2.0, -y), c(1.0, 0.82, 0.60), 0.45,
               {"omni_range": 5.0}) for k, y in enumerate((3.5, 8.0, 12.5))],
        ],
        "mood_strata": ["raw", "memory_warm", "noir", "lithograph",
                        "candlelight", "silent_film_18"],
    },
    {
        # DICKENS DEAN's rooms (build_dean_offices.py): the trio's Office by
        # day (the sun through the front glass); the imagined lobby, bright
        # and hazy; the club's back office at night on its desk lamp, the
        # club's pink spilling through the open door; the glass house's ring
        # of monitors (x 100..107); the tower corridor and its city (x 140..146).
        "out_path": os.path.join(ROOT, "dean_offices.tscn"),
        "uid": "uid://dean_offices_v1",
        "root_node": "DeanOffices",
        "glb": "res://assets/3d/locales/dean_offices.glb",
        "env": {"bg": (0.03, 0.03, 0.05, 1), "amb": (0.60, 0.62, 0.70, 1),
                "amb_e": 0.30, "fog": (0.20, 0.20, 0.24, 1), "fog_e": 0.2,
                "fog_d": 0.003, "sat": 0.94, "glow_i": 0.7, "glow_b": 0.12},
        "shader": {"warm": (0.94, 0.86, 0.70, 1), "bg": (0.07, 0.07, 0.09, 1),
                   "neon_edge": (0.80, 0.56, 0.74, 1), "neon_lo": (0.26, 0.22, 0.26, 1),
                   "neon_hi": (0.07, 0.07, 0.09, 1), "lim_tint": (0.70, 0.60, 0.70, 1)},
        "lights": [
            # the Office: the street's daylight through the S glass
            ("Key_Sun" + ONEI, "DirectionalLight3D", B_SUN_FROM_S.format(0, 6, 6), c(1.0, 0.94, 0.82), 1.0),
            ("Fill_Office" + ONEI, "DirectionalLight3D", B_FILL.format(0, 4, -4), c(0.82, 0.86, 0.94), 0.30),
            ("Back" + ONEI, "DirectionalLight3D", B_BACK.format(0, 4, 0), c(0.86, 0.86, 0.90), 0.20),
            ("Front_Glass_Day" + ONEI, "OmniLight3D", I.format(0.0, 1.6, -0.8), c(0.96, 0.96, 0.94), 1.6, {"omni_range": 8.0}),
            ("Office_Overhead" + ONEI, "OmniLight3D", I.format(0.0, 2.8, -5.0), c(0.96, 0.96, 0.92), 0.7, {"omni_range": 7.0}),
            # the lobby: soft light from everywhere
            ("Key_Lobby__tutorial_lobby", "DirectionalLight3D", B_KEY_FROM_N.format(37, 4, -5), c(1.0, 1.0, 0.98), 0.40),
            *[("Lobby_Glow_{}__tutorial_lobby".format(k), "OmniLight3D", I.format(x, 3.6, -5.0), c(1.0, 0.98, 0.96), 1.3,
               {"omni_range": 10.0}) for k, x in enumerate((32.5, 37.0, 41.5))],
            # the club office: the desk lamp (blender (66.2, 5.54, 1.17)), the club through the door
            ("Lamp_Desk_Club" + CLUBO, "OmniLight3D", I.format(66.2, 1.15, -5.5), c(1.0, 0.76, 0.50), 1.3, {"omni_range": 5.0}),
            ("Club_Door_Spill" + CLUBO, "OmniLight3D", I.format(62.0, 1.8, 0.4), c(0.98, 0.34, 0.70), 1.4, {"omni_range": 4.5}),
            ("Club_Floor_Glow" + CLUBO, "OmniLight3D", I.format(62.6, 2.4, 6.5), c(0.98, 0.30, 0.66), 2.0, {"omni_range": 6.0}),
            ("Club_Off_Overhead" + CLUBO, "OmniLight3D", I.format(64.0, 2.8, -3.0), c(0.96, 0.82, 0.70), 1.6, {"omni_range": 7.0}),
            ("Key_Club" + CLUBO, "DirectionalLight3D", B_KEY_FROM_N.format(64, 3, -3), c(0.60, 0.56, 0.70), 0.05),
            # the monitor ring (centre blender (104.0, 3.2)), the text game, the night through the glass
            ("Monitor_Ring_Glow__dean_monitor_room", "OmniLight3D", I.format(104.0, 1.2, -3.2), c(0.56, 0.66, 0.96), 1.6,
             {"omni_range": 4.5}),
            ("Text_Game_Glow__dean_monitor_room", "OmniLight3D", I.format(102.9, 1.0, -3.2), c(0.50, 0.96, 0.56), 0.5,
             {"omni_range": 1.6}),
            ("Key_Night_Glass__dean_monitor_room", "DirectionalLight3D", B_KEY_FROM_N.format(103, 4, -3), c(0.46, 0.54, 0.80), 0.10),
            # the tower corridor: the city through the glass, the downlights, the door's light under it
            *[("City_Glow_{}__dean_tower_corridor".format(k), "OmniLight3D", I.format(145.4, 1.6, -y), c(1.0, 0.80, 0.56), 1.4,
               {"omni_range": 7.0}) for k, y in enumerate((5.0, 15.0, 25.0))],
            *[("Tower_Downlight_{}__dean_tower_corridor".format(k), "OmniLight3D", I.format(142.4, 3.1, -y), c(0.86, 0.90, 1.0), 0.9,
               {"omni_range": 6.0}) for k, y in enumerate((3.0, 9.0, 15.0, 21.0, 27.0))],
            ("Door_Spill_Tower__dean_tower_corridor", "OmniLight3D", I.format(142.4, 0.05, -29.8), c(1.0, 0.94, 0.80), 0.8,
             {"omni_range": 1.6}),
            ("Key_Tower__dean_tower_corridor", "DirectionalLight3D", B_KEY_FROM_N.format(143, 4, -10), c(0.56, 0.60, 0.80), 0.08),
        ],
        "mood_strata": ["raw", "noir", "memory_warm", "lithograph",
                        "candlelight", "silent_film_18"],
    },
    {
        # VOL 3's BALLFIELD (build_little_league.py): Texas, August, "well
        # past 110 degrees" — a hard high sun, the dugout's shade.
        "out_path": os.path.join(ROOT, "little_league.tscn"),
        "uid": "uid://little_league_v3",
        "root_node": "LittleLeague",
        "glb": "res://assets/3d/locales/little_league.glb",
        "env": {"bg": (0.66, 0.78, 0.92, 1), "amb": (0.90, 0.88, 0.82, 1),
                "amb_e": 0.75, "fog": (0.90, 0.86, 0.76, 1), "fog_e": 0.4,
                "fog_d": 0.0015, "sat": 0.96, "glow_i": 0.6, "glow_b": 0.16},
        "shader": {"warm": (0.98, 0.88, 0.66, 1), "bg": (0.12, 0.11, 0.10, 1),
                   "neon_edge": (0.84, 0.70, 0.48, 1), "neon_lo": (0.34, 0.28, 0.20, 1),
                   "neon_hi": (0.12, 0.11, 0.10, 1), "lim_tint": (0.80, 0.68, 0.48, 1)},
        "lights": [
            ("Key_Sun", "DirectionalLight3D", B_SUN_FROM_S.format(0, 20, 10), c(1.0, 0.94, 0.80), 1.7),
            ("Fill_Sky", "DirectionalLight3D", B_FILL.format(0, 10, -10), c(0.70, 0.80, 0.96), 0.40),
            ("Back", "DirectionalLight3D", B_BACK.format(0, 10, 0), c(0.96, 0.90, 0.80), 0.30),
        ],
        "mood_strata": ["raw", "memory_warm", "lithograph", "noir",
                        "candlelight", "silent_film_18"],
    },
    {
        # VOL 3's "PASSENGERS" (build_chau_house.py): the Chau house by day
        # (its windows, Steven's blinds, the bathroom's vanity light, the
        # game room's TV); Amanda's (x 40..56) at night: the TV through the
        # sheet, the water's light on the deck.
        "out_path": os.path.join(ROOT, "chau_house.tscn"),
        "uid": "uid://chau_house_v3",
        "root_node": "ChauHouse",
        "glb": "res://assets/3d/locales/chau_house.glb",
        "env": {"bg": (0.02, 0.03, 0.06, 1), "amb": (0.80, 0.80, 0.78, 1),
                "amb_e": 0.45, "fog": (0.30, 0.30, 0.32, 1), "fog_e": 0.2,
                "fog_d": 0.002, "sat": 0.94, "glow_i": 0.7, "glow_b": 0.12},
        "shader": {"warm": (0.94, 0.88, 0.74, 1), "bg": (0.08, 0.08, 0.10, 1),
                   "neon_edge": (0.72, 0.68, 0.60, 1), "neon_lo": (0.28, 0.26, 0.24, 1),
                   "neon_hi": (0.08, 0.08, 0.10, 1), "lim_tint": (0.66, 0.62, 0.56, 1)},
        "lights": [
            ("Key_Sun" + CHAU, "DirectionalLight3D", B_SUN_FROM_S.format(0, 8, 6), c(1.0, 0.94, 0.84), 0.70),
            ("Fill_House" + CHAU, "DirectionalLight3D", B_FILL.format(0, 5, -7), c(0.86, 0.88, 0.94), 0.30),
            ("Back" + CHAU, "DirectionalLight3D", B_BACK.format(0, 5, 0), c(0.90, 0.88, 0.84), 0.20),
            ("Window_Living_S" + CHAU, "OmniLight3D", I.format(2.5, 1.5, -0.6), c(1.0, 0.98, 0.92), 1.4, {"omni_range": 7.0}),
            ("Window_Living_N" + CHAU, "OmniLight3D", I.format(-1.5, 1.5, -13.4), c(0.94, 0.96, 1.0), 1.2, {"omni_range": 7.0}),
            ("Window_Kitchen_S" + CHAU, "OmniLight3D", I.format(-7.0, 1.5, -0.6), c(1.0, 0.98, 0.92), 1.0, {"omni_range": 6.0}),
            ("Blinds_Steven" + CHAU, "OmniLight3D", I.format(11.6, 1.5, -6.0), c(1.0, 0.96, 0.86), 1.2, {"omni_range": 5.0}),
            ("Window_Mom" + CHAU, "OmniLight3D", I.format(11.6, 1.5, -11.2), c(1.0, 0.96, 0.86), 0.6, {"omni_range": 4.0}),
            # the living room's TV left on (the morning's looping intro; noon's distant din)
            ("Living_TV_Glow__chau_hall_noon__chau_entry_morning", "OmniLight3D", I.format(1.0, 1.45, -13.5), c(0.60, 0.70, 1.0), 0.9,
             {"omni_range": 4.5}),
            ("Bath_Vanity_Light__chau_bath", "OmniLight3D", I.format(11.7, 2.0, -1.4), c(1.0, 0.94, 0.80), 1.4, {"omni_range": 4.0}),
            ("Game_TV_Glow__chau_game_room", "OmniLight3D", I.format(-7.0, 1.5, -6.4), c(0.56, 0.62, 1.0), 1.0, {"omni_range": 5.0}),
            # Amanda's, at night
            ("Key_Moon" + AMANDA, "DirectionalLight3D", B_KEY_FROM_N.format(48, 8, -3), c(0.56, 0.62, 0.86), 0.12),
            ("Am_TV_Glow__amanda_fort", "OmniLight3D", I.format(40.7, 1.25, -3.2), c(0.56, 0.52, 1.0), 1.6, {"omni_range": 6.0}),
            ("Am_Lamp_Dim__amanda_fort__amanda_fort_close", "OmniLight3D", I.format(45.2, 1.6, -3.2), c(1.0, 0.82, 0.56), 0.5, {"omni_range": 3.2}),
            ("Am_TV_Glow_Close__amanda_fort_close", "OmniLight3D", I.format(41.2, 1.2, -3.2), c(0.40, 0.52, 1.0), 2.2, {"omni_range": 5.0}),
            ("Tub_Light__amanda_hot_tub", "OmniLight3D", I.format(51.4, 1.4, -3.6), c(0.46, 0.86, 1.0), 1.8, {"omni_range": 4.5}),
            ("House_Spill__amanda_hot_tub", "OmniLight3D", I.format(47.4, 1.8, -3.2), c(1.0, 0.84, 0.62), 1.4, {"omni_range": 7.0}),
        ],
        "mood_strata": ["raw", "memory_warm", "noir", "lithograph",
                        "candlelight", "silent_film_18"],
    },
    {
        # VOL 2's COPY SHOP (build_copy_shop.py): the graveyard shift under
        # the failing tubes, a greenish cast; the copier view adds its pink
        # scan light. Vol 4's office (x 34..52) after hours: dim panels, the
        # bright corner where the walls meet.
        "out_path": os.path.join(ROOT, "copy_shop.tscn"),
        "uid": "uid://copy_shop_v2",
        "root_node": "CopyShop",
        "glb": "res://assets/3d/locales/copy_shop.glb",
        "env": {"bg": (0.03, 0.03, 0.04, 1), "amb": (0.64, 0.70, 0.64, 1),
                "amb_e": 0.32, "fog": (0.16, 0.18, 0.16, 1), "fog_e": 0.2,
                "fog_d": 0.003, "sat": 0.88, "glow_i": 0.7, "glow_b": 0.12},
        "shader": {"warm": (0.86, 0.90, 0.78, 1), "bg": (0.06, 0.07, 0.06, 1),
                   "neon_edge": (0.62, 0.70, 0.60, 1), "neon_lo": (0.22, 0.26, 0.22, 1),
                   "neon_hi": (0.06, 0.07, 0.06, 1), "lim_tint": (0.56, 0.64, 0.54, 1)},
        "lights": [
            ("Key_Shop" + SHOP, "DirectionalLight3D", B_KEY_FROM_N.format(0, 4, -6), c(0.80, 0.86, 0.80), 0.08),
            ("Fill_Shop" + SHOP, "DirectionalLight3D", B_FILL.format(0, 3, -3), c(0.70, 0.76, 0.70), 0.06),
            ("Back" + SHOP, "DirectionalLight3D", B_BACK.format(0, 3, 1), c(0.60, 0.66, 0.62), 0.05),
            # the tubes (blender rows y 3.0 / 6.2); the dying ones left dark
            *[("Fluor_Shop_{}_{}".format(r, k) + SHOP, "OmniLight3D", I.format(x, 2.9, -y), c(0.86, 0.96, 0.86), 1.0,
               {"omni_range": 5.0}) for r, y in enumerate((3.0, 6.2)) for k, x in enumerate((-3.6, 0.0, 3.6)) if (r * 3 + k) % 3 != 2],
            ("Copier_Scan_Glow__copy_shop_copier", "OmniLight3D", I.format(0.0, 1.22, -5.1), c(1.0, 0.50, 0.70), 0.9,
             {"omni_range": 1.4}),
            ("Back_Bulb_Glow" + SHOP, "OmniLight3D", I.format(3.6, 2.8, -11.0), c(1.0, 0.86, 0.62), 0.6, {"omni_range": 3.5}),
            # the office
            ("Key_Office__office_after_hours", "DirectionalLight3D", B_KEY_FROM_N.format(43, 4, -7), c(0.80, 0.82, 0.90), 0.10),
            *[("Office_Panel_{}__office_after_hours".format(k), "OmniLight3D", I.format(x, 2.7, -7.0), c(0.92, 0.94, 0.96), 0.6,
               {"omni_range": 6.0}) for k, x in enumerate((37.0, 43.0, 49.0))],
            ("Bright_Corner__office_after_hours", "OmniLight3D", I.format(51.4, 2.0, -13.4), c(1.0, 1.0, 0.96), 2.6,
             {"omni_range": 6.0}),
        ],
        "mood_strata": ["raw", "noir", "memory_warm", "lithograph",
                        "candlelight", "silent_film_18"],
    },
    {
        # VOL 3's 1945 (build_pasadena_1945.py): the Pasadena street, the
        # park and Hollywood under a clear sun; the street again in the
        # meld's rain (grey, the marquee lit); the clinic on its ceiling
        # light and its window.
        "out_path": os.path.join(ROOT, "pasadena_1945.tscn"),
        "uid": "uid://pasadena_1945_v3",
        "root_node": "Pasadena1945",
        "glb": "res://assets/3d/locales/pasadena_1945.glb",
        "env": {"bg": (0.62, 0.76, 0.92, 1), "amb": (0.88, 0.88, 0.84, 1),
                "amb_e": 0.70, "fog": (0.86, 0.86, 0.82, 1), "fog_e": 0.4,
                "fog_d": 0.0015, "sat": 0.92, "glow_i": 0.6, "glow_b": 0.14},
        "shader": {"warm": (0.96, 0.88, 0.70, 1), "bg": (0.10, 0.10, 0.10, 1),
                   "neon_edge": (0.80, 0.70, 0.54, 1), "neon_lo": (0.30, 0.26, 0.22, 1),
                   "neon_hi": (0.10, 0.10, 0.10, 1), "lim_tint": (0.76, 0.68, 0.54, 1)},
        "lights": [
            ("Key_Sun" + P45, "DirectionalLight3D", B_SUN_FROM_S.format(0, 20, 10), c(1.0, 0.94, 0.82), 1.5),
            ("Fill_Sky" + P45, "DirectionalLight3D", B_FILL.format(0, 10, -10), c(0.72, 0.80, 0.96), 0.40),
            ("Back" + P45, "DirectionalLight3D", B_BACK.format(0, 10, 0), c(0.94, 0.90, 0.82), 0.30),
            ("Key_Rain__street_rain", "DirectionalLight3D", B_KEY_FROM_N.format(0, 20, -20), c(0.70, 0.74, 0.80), 0.40),
            ("Fill_Rain__street_rain", "DirectionalLight3D", B_FILL.format(0, 10, -10), c(0.62, 0.66, 0.72), 0.25),
            ("Marquee_Glow__street_rain__street_day", "OmniLight3D", I.format(7.0, 4.3, -46.0), c(1.0, 0.86, 0.56), 1.6,
             {"omni_range": 7.0}),
            ("Key_Clinic__clinic_1945", "DirectionalLight3D", B_KEY_FROM_N.format(202, 3, -2), c(0.92, 0.94, 0.90), 0.20),
            ("Clinic_Ceiling__clinic_1945", "OmniLight3D", I.format(202.5, 2.6, -2.2), c(1.0, 0.98, 0.92), 1.4, {"omni_range": 5.0}),
            ("Clinic_Window__clinic_1945", "OmniLight3D", I.format(200.3, 1.6, -2.2), c(0.96, 0.96, 0.92), 1.0, {"omni_range": 4.0}),
        ],
        "mood_strata": ["raw", "memory_warm", "lithograph", "silent_film_18",
                        "noir", "candlelight"],
    },
    {
        # THE EDITING SUITE (build_editing_suite.py): the four's suite at
        # Aud's on its screens, per view (the frozen frame; the tide; the
        # 4 a.m. coffee); vol 3's night edit station (x 40..44) on its lamp.
        "out_path": os.path.join(ROOT, "editing_suite.tscn"),
        "uid": "uid://editing_suite_v1",
        "root_node": "EditingSuite",
        "glb": "res://assets/3d/locales/editing_suite.glb",
        "env": {"bg": (0.03, 0.03, 0.04, 1), "amb": (0.50, 0.52, 0.60, 1),
                "amb_e": 0.30, "fog": (0.10, 0.10, 0.12, 1), "fog_e": 0.2,
                "fog_d": 0.003, "sat": 0.92, "glow_i": 0.75, "glow_b": 0.12},
        "shader": {"warm": (0.90, 0.84, 0.70, 1), "bg": (0.06, 0.06, 0.08, 1),
                   "neon_edge": (0.64, 0.68, 0.78, 1), "neon_lo": (0.22, 0.22, 0.26, 1),
                   "neon_hi": (0.06, 0.06, 0.08, 1), "lim_tint": (0.58, 0.62, 0.72, 1)},
        "lights": [
            ("Key_Suite" + SUITE, "DirectionalLight3D", B_KEY_FROM_N.format(0, 4, -4), c(0.80, 0.82, 0.90), 0.07),
            ("Fill_Suite" + SUITE, "DirectionalLight3D", B_FILL.format(0, 3, -3), c(0.70, 0.72, 0.80), 0.05),
            ("Back" + SUITE, "DirectionalLight3D", B_BACK.format(0, 3, 0), c(0.60, 0.62, 0.70), 0.04),
            ("Monitor_Glow__suite_wide", "OmniLight3D", I.format(0.0, 1.8, -5.8), c(1.0, 0.86, 0.66), 1.4, {"omni_range": 5.5}),
            ("Monitor_Glow__suite_tide", "OmniLight3D", I.format(0.0, 1.6, -5.8), c(0.74, 0.82, 0.88), 1.6, {"omni_range": 6.0}),
            ("Monitor_Glow__suite_4am", "OmniLight3D", I.format(0.0, 1.6, -5.8), c(0.86, 0.80, 0.70), 1.2, {"omni_range": 5.0}),
            ("Suite_Overhead__suite_wide", "OmniLight3D", I.format(0.0, 2.6, -3.0), c(1.0, 0.90, 0.74), 2.0, {"omni_range": 8.0}),
            ("Suite_Overhead_Dim__suite_4am", "OmniLight3D", I.format(0.0, 2.6, -3.0), c(1.0, 0.90, 0.74), 0.6, {"omni_range": 6.0}),
            ("Suite_Window_Grey__suite_wide", "OmniLight3D", I.format(-3.4, 1.6, -3.6), c(0.80, 0.82, 0.84), 0.5, {"omni_range": 3.5}),
            ("Key_Edit__edit_station", "DirectionalLight3D", B_KEY_FROM_N.format(42, 3, -2), c(0.60, 0.64, 0.80), 0.06),
            ("Lamp_Edit__edit_station", "OmniLight3D", I.format(42.8, 1.15, -3.0), c(1.0, 0.84, 0.58), 1.1, {"omni_range": 3.5}),
            ("Edit_CRT_Glow__edit_station", "OmniLight3D", I.format(41.7, 1.0, -2.9), c(0.50, 0.62, 1.0), 0.7, {"omni_range": 2.2}),
        ],
        "mood_strata": ["raw", "noir", "memory_warm", "lithograph", "candlelight", "silent_film_18"],
    },
    {
        # VOL 2's APPLE PEDDLER (build_apple_peddler.py): the diner on its
        # tubes against the rain, the pie case, the line under its hood.
        "out_path": os.path.join(ROOT, "apple_peddler.tscn"),
        "uid": "uid://apple_peddler_v2",
        "root_node": "ApplePeddler",
        "glb": "res://assets/3d/locales/apple_peddler.glb",
        "env": {"bg": (0.03, 0.04, 0.06, 1), "amb": (0.74, 0.72, 0.66, 1),
                "amb_e": 0.40, "fog": (0.18, 0.20, 0.24, 1), "fog_e": 0.3,
                "fog_d": 0.004, "sat": 0.92, "glow_i": 0.7, "glow_b": 0.12},
        "shader": {"warm": (0.96, 0.86, 0.66, 1), "bg": (0.07, 0.08, 0.10, 1),
                   "neon_edge": (0.78, 0.66, 0.50, 1), "neon_lo": (0.28, 0.24, 0.20, 1),
                   "neon_hi": (0.07, 0.08, 0.10, 1), "lim_tint": (0.72, 0.62, 0.48, 1)},
        "lights": [
            ("Key_Diner", "DirectionalLight3D", B_KEY_FROM_N.format(0, 4, -5), c(0.84, 0.86, 0.90), 0.10),
            ("Fill_Diner", "DirectionalLight3D", B_FILL.format(0, 3, -4), c(0.80, 0.76, 0.70), 0.08),
            ("Back", "DirectionalLight3D", B_BACK.format(0, 3, 0), c(0.60, 0.64, 0.72), 0.06),
            *[("AP_Fluor_{}".format(k), "OmniLight3D", I.format(-4.5 + k * 4.5, 2.9, -4.0), c(0.96, 0.98, 0.92), 1.2,
               {"omni_range": 6.0}) for k in range(3)],
            ("Pie_Case_Glow", "OmniLight3D", I.format(-3.2, 1.3, -5.3), c(1.0, 0.92, 0.70), 0.5, {"omni_range": 1.8}),
            ("Line_Light", "OmniLight3D", I.format(4.3, 2.0, -8.0), c(1.0, 0.92, 0.80), 1.2, {"omni_range": 4.0}),
            ("Depot_Canopy_Glow", "OmniLight3D", I.format(14.0, 3.0, 1.0), c(0.86, 0.90, 1.0), 1.0, {"omni_range": 8.0}),
        ],
        "mood_strata": ["raw", "memory_warm", "noir", "lithograph", "candlelight", "silent_film_18"],
    },
    {
        # VOL 4's BUS STATION (build_bus_station.py): the city by day, the
        # overhang's shade; the bus (x 60..62.6) lit through its windows.
        "out_path": os.path.join(ROOT, "bus_station.tscn"),
        "uid": "uid://bus_station_v4",
        "root_node": "BusStation",
        "glb": "res://assets/3d/locales/bus_station.glb",
        "env": {"bg": (0.66, 0.76, 0.88, 1), "amb": (0.86, 0.86, 0.84, 1),
                "amb_e": 0.65, "fog": (0.82, 0.84, 0.86, 1), "fog_e": 0.4,
                "fog_d": 0.002, "sat": 0.92, "glow_i": 0.6, "glow_b": 0.14},
        "shader": {"warm": (0.94, 0.88, 0.74, 1), "bg": (0.10, 0.10, 0.11, 1),
                   "neon_edge": (0.74, 0.70, 0.60, 1), "neon_lo": (0.28, 0.27, 0.25, 1),
                   "neon_hi": (0.10, 0.10, 0.11, 1), "lim_tint": (0.70, 0.66, 0.58, 1)},
        "lights": [
            ("Key_Sun", "DirectionalLight3D", B_SUN_FROM_S.format(0, 20, 10), c(1.0, 0.95, 0.84), 1.4),
            ("Fill_Sky", "DirectionalLight3D", B_FILL.format(0, 10, -10), c(0.74, 0.82, 0.96), 0.40),
            ("Back", "DirectionalLight3D", B_BACK.format(0, 10, 0), c(0.92, 0.90, 0.84), 0.30),
            *[("Bus_Window_Day_{}_{}".format(s, k), "OmniLight3D", I.format(61.3 + s * 1.05, 1.7, -(2.0 + k * 3.4)),
               c(0.94, 0.96, 1.0), 0.8, {"omni_range": 3.2}) for s in (-1, 1) for k in range(3)],
            ("Bus_Ceiling_Light", "OmniLight3D", I.format(61.3, 2.5, -5.5), c(0.96, 0.96, 0.92), 0.6, {"omni_range": 6.0}),
        ],
        "mood_strata": ["raw", "memory_warm", "lithograph", "noir", "candlelight", "silent_film_18"],
    },
    {
        # VOL 3's 1945 HOUSE (build_parsonage_1945.py): Ron's room upstairs
        # at first light (the streetlamp still burning), by day, and at night
        # on his lamp; the hall on its sconces. The window's sky is a card
        # per view.
        "out_path": os.path.join(ROOT, "parsonage_1945.tscn"),
        "uid": "uid://parsonage_1945_v3",
        "root_node": "Parsonage1945",
        "glb": "res://assets/3d/locales/parsonage_1945.glb",
        "env": {"bg": (0.04, 0.05, 0.08, 1), "amb": (0.70, 0.66, 0.60, 1),
                "amb_e": 0.32, "fog": (0.14, 0.14, 0.16, 1), "fog_e": 0.2,
                "fog_d": 0.002, "sat": 0.90, "glow_i": 0.7, "glow_b": 0.12},
        "shader": {"warm": (0.94, 0.84, 0.64, 1), "bg": (0.07, 0.07, 0.08, 1),
                   "neon_edge": (0.76, 0.64, 0.46, 1), "neon_lo": (0.28, 0.24, 0.18, 1),
                   "neon_hi": (0.07, 0.07, 0.08, 1), "lim_tint": (0.70, 0.60, 0.44, 1)},
        "lights": [
            ("Key_House", "DirectionalLight3D", B_KEY_FROM_N.format(0, 4, -4), c(0.76, 0.76, 0.84), 0.07),
            ("Fill_House", "DirectionalLight3D", B_FILL.format(0, 3, -3), c(0.74, 0.70, 0.64), 0.05),
            ("Back", "DirectionalLight3D", B_BACK.format(0, 3, 0), c(0.60, 0.60, 0.68), 0.04),
            ("Streetlamp__ron_dawn", "OmniLight3D", I.format(-8.2, 0.8, 4.6), c(1.0, 0.86, 0.56), 2.0, {"omni_range": 7.0}),
            ("Window_First_Light__ron_dawn", "OmniLight3D", I.format(0.9, 1.6, -0.4), c(0.86, 0.84, 0.90), 0.7, {"omni_range": 4.0}),
            ("Sun_Day__ron_day", "DirectionalLight3D", B_SUN_FROM_S.format(0, 8, 6), c(1.0, 0.94, 0.82), 0.9),
            ("Window_Day__ron_day", "OmniLight3D", I.format(0.9, 1.6, -0.4), c(1.0, 0.98, 0.92), 1.6, {"omni_range": 5.5}),
            ("Lamp_Desk__ron_night_floor__ron_night_bed", "OmniLight3D", I.format(-2.24, 1.2, -2.77), c(1.0, 0.82, 0.54), 1.4,
             {"omni_range": 4.6}),
            ("Window_Night_Open__ron_night_bed", "OmniLight3D", I.format(0.9, 1.6, -0.3), c(0.56, 0.62, 0.86), 0.4, {"omni_range": 2.6}),
            *[("Hall_Sconce_{}__parsonage_hall".format(k), "OmniLight3D", I.format(-4.5 + k * 3.5, 2.0, -8.0), c(1.0, 0.84, 0.58), 1.1,
               {"omni_range": 4.5}) for k in range(3)],
        ],
        "mood_strata": ["raw", "memory_warm", "lithograph", "silent_film_18", "noir", "candlelight"],
    },
]


def main():
    for cfg in CONFIGS:
        path = write_locale_tscn(cfg)
        print("wrote", os.path.relpath(path))


if __name__ == "__main__":
    main()
