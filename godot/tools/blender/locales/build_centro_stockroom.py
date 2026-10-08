"""Centro Groceries stockroom + loading dock — vol6 placement script.

Diego's night-shift back-of-house. Canon (vol6 ch18): "the room at
the back of the store with the high ceiling and the bare fluorescent
tubes and the small dead-quiet of a room that has no customers in it
at any hour." Canon (ch10/ch16): the dock door he steps out of for
his second break at five/six AM — "The dock is empty. The truck has
not come yet."

One GLB serves two Background3D presets:
  centro_stockroom — interior among the racks under the tubes
  centro_dock      — outside on the empty dock apron, pre-dawn, the
                     open roll-up door spilling fluorescent light

Hero features: two steel pallet-rack rows with boxed stock, a pallet
of shrink-wrapped cases mid-floor with a pallet jack parked in it, a
hand truck, the OPEN roll-up dock door (coil above) with rubber dock
bumpers outside, bare twin-tube fluorescent fixtures (emissive — the
tscn Omnis sit under them), the swing door to the store with its
porthole, a time-clock + punch-card rack by it.

Coordinate frame: Blender Z-up. y=0 is the store-side (south) wall
with the swing door; +Y runs toward the dock; the dock wall is at
y=ROOM_D with the apron beyond. Walls at x=±ROOM_W/2. glTF export
remaps to Godot (x, z, -y).
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, make_taper_cyl, make_blob, export_glb
from _props.structure import make_floor, make_wall, make_ceiling

# ── High back-of-house footprint ──
ROOM_W = 7.0      # x ∈ [-3.5, 3.5]
ROOM_D = 8.0      # y ∈ [0, 8.0]  (dock wall at y=8.0)
CEIL = 4.6

COL_WALL = (0.52, 0.53, 0.50, 1.0)      # painted CMU grey-green
COL_BASE = (0.34, 0.35, 0.33, 1.0)
COL_FLOOR = (0.46, 0.46, 0.47, 1.0)     # sealed concrete
COL_SEAM = (0.36, 0.36, 0.38, 1.0)
COL_STRIPE = (0.72, 0.62, 0.16, 1.0)    # safety-yellow floor stripe
COL_RACK = (0.20, 0.30, 0.48, 1.0)      # blue rack uprights
COL_BEAM = (0.72, 0.42, 0.14, 1.0)      # orange rack beams
COL_DECK = (0.46, 0.36, 0.24, 1.0)      # particle-board decking
COL_BOX = (0.55, 0.42, 0.28, 1.0)       # kraft cardboard
COL_BOX_DK = (0.44, 0.33, 0.22, 1.0)
COL_TAPE = (0.62, 0.58, 0.50, 1.0)
COL_WRAP = (0.66, 0.70, 0.74, 0.55)     # shrink wrap
COL_PALLET = (0.48, 0.38, 0.24, 1.0)
COL_STEEL = (0.34, 0.35, 0.38, 1.0)
COL_STEEL_DK = (0.17, 0.17, 0.19, 1.0)
COL_JACK = (0.62, 0.16, 0.12, 1.0)      # pallet-jack red
COL_DOOR = (0.58, 0.58, 0.56, 1.0)      # roll-up door galvanized
COL_RUBBER = (0.10, 0.10, 0.11, 1.0)
COL_TUBE = (0.92, 0.96, 0.94, 1.0)      # lit fluorescent — blooms
COL_FIXTURE = (0.60, 0.60, 0.58, 1.0)
COL_SWING = (0.44, 0.48, 0.44, 1.0)     # store swing door
COL_APRON = (0.40, 0.40, 0.42, 1.0)     # dock apron concrete (night)
COL_CARD = (0.80, 0.76, 0.66, 1.0)


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4,
               size_y=ROOM_D + 0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    # Safety stripe lane from swing door to dock
    make_box("Floor_Stripe_W", (-1.35, ROOM_D / 2.0, 0.004), (0.08, ROOM_D - 0.6, 0.004), COL_STRIPE)
    make_box("Floor_Stripe_E", (0.55, ROOM_D / 2.0, 0.004), (0.08, ROOM_D - 0.6, 0.004), COL_STRIPE)
    pal = {"wall": COL_WALL, "baseboard": COL_BASE}
    for nm, x, bb in [("Wall_W", -ROOM_W / 2.0, +1), ("Wall_E", +ROOM_W / 2.0, -1)]:
        make_wall(nm, (x, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL,
                  axis='Y', palette=pal, baseboard_face_sign=bb)
    # South wall split around the swing door to the store
    make_wall("Wall_S_W", (-(ROOM_W / 4.0 + 0.55), 0.0, 0),
              length=ROOM_W / 2.0 - 1.10, height=CEIL, axis='X', palette=pal, baseboard_face_sign=+1)
    make_wall("Wall_S_E", (+(ROOM_W / 4.0 + 0.55), 0.0, 0),
              length=ROOM_W / 2.0 - 1.10, height=CEIL, axis='X', palette=pal, baseboard_face_sign=+1)
    make_box("Wall_S_Above", (0.0, 0.0, CEIL - 0.65), (2.4, 0.20, 1.30), COL_WALL)
    # North (dock) wall split around the big roll-up opening
    dock_w = 3.0
    side = (ROOM_W - dock_w) / 2.0
    make_wall("Wall_N_W", (-(dock_w / 2.0 + side / 2.0), ROOM_D, 0),
              length=side, height=CEIL, axis='X', palette=pal, baseboard_face_sign=-1)
    make_wall("Wall_N_E", (+(dock_w / 2.0 + side / 2.0), ROOM_D, 0),
              length=side, height=CEIL, axis='X', palette=pal, baseboard_face_sign=-1)
    make_box("Wall_N_Above", (0.0, ROOM_D, CEIL - 0.55), (dock_w + 0.4, 0.20, 1.10), COL_WALL)
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4,
                 size_y=ROOM_D + 0.4, with_grid=False, with_stains=True)


def build_dock():
    """The OPEN roll-up door, its coil, the bumpers, and the empty
    apron outside — 'The dock is empty. The truck has not come yet.'"""
    dock_w = 3.0
    # Rolled coil above the opening
    make_cyl("Dock_Coil", (0.0, ROOM_D - 0.10, CEIL - 1.32), 0.22, dock_w,   # ends inside the tracks; under the header (2026-09-22: 7 cm into it)
             COL_DOOR, segments=14, axis='X')
    # Door tracks
    for sgn in (-1, 1):
        make_box(f"Dock_Track_{sgn:+d}", (sgn * (dock_w / 2.0 + 0.08), ROOM_D - 0.06,
                 (CEIL - 1.1) / 2.0 + 0.2), (0.06, 0.10, CEIL - 1.1), COL_STEEL_DK)
    # Slab edge: interior floor is dock-height; apron drops 1.1 m
    make_box("Dock_EdgeGuard", (0.0, ROOM_D + 0.06, 0.03), (dock_w, 0.10, 0.06), COL_STRIPE)
    make_box("Dock_Face", (0.0, ROOM_D + 0.25, -0.55), (dock_w + 2.4, 0.5, 1.10), COL_BASE)
    for sgn in (-1, 1):
        make_box(f"Dock_Bumper_{sgn:+d}", (sgn * (dock_w / 2.0 - 0.25), ROOM_D + 0.55,
                 -0.35), (0.45, 0.16, 0.5), COL_RUBBER)
    # Apron pad + a painted truck-lane stripe, otherwise EMPTY
    make_box("Apron", (0.0, ROOM_D + 3.6, -1.12), (ROOM_W + 6.0, 6.4, 0.06), COL_APRON)
    for k in range(2):
        make_box(f"Apron_Lane_{k}", (-1.5 + k * 3.0, ROOM_D + 3.6, -1.088),
                 (0.10, 5.8, 0.006), COL_STRIPE)
    # Dock light on the outside wall over the door
    make_box("DockLamp_Arm", (1.2, ROOM_D + 0.16, 3.6), (0.06, 0.30, 0.06), COL_STEEL_DK)
    make_cyl("DockLamp_Head", (1.2, ROOM_D + 0.34, 3.52), 0.10, 0.14, COL_STEEL_DK,
             segments=10, axis='Y')
    make_cyl("DockLamp_Lens", (1.2, ROOM_D + 0.42, 3.52), 0.075, 0.02,
             (0.95, 0.80, 0.50, 1.0), segments=10, axis='Y')
    # A stack of empty pallets waiting outside, right of the door
    for k in range(4):
        make_box(f"Apron_Pallet_{k}", (2.9, ROOM_D + 1.4, -1.02 + k * 0.14),
                 (1.1, 1.1, 0.12), COL_PALLET)


def _rack_row(prefix, x, y0, y1):
    """A pallet-rack row along Y at fixed x: blue uprights, orange
    beams at two levels, particle decking, kraft boxes."""
    levels = [1.15, 2.45]
    bays = int((y1 - y0) / 2.4)
    for b in range(bays + 1):
        yy = y0 + b * 2.4
        for dx in (-0.55, 0.55):
            make_box(f"{prefix}_Up_{b}_{dx:+.1f}", (x + dx, yy, 1.7),
                     (0.09, 0.09, 3.4), COL_RACK)
    for b in range(bays):
        cy = y0 + b * 2.4 + 1.2
        for lz in levels:
            for dx in (-0.55, 0.55):
                make_box(f"{prefix}_Beam_{b}_{lz:.1f}_{dx:+.1f}", (x + dx, cy, lz),
                         (0.07, 2.25, 0.10), COL_BEAM)
            make_box(f"{prefix}_Deck_{b}_{lz:.1f}", (x, cy, lz + 0.07),
                     (1.10, 2.25, 0.03), COL_DECK)
        # ground level + both shelf levels get box loads
        for lz, dz in ((0.0, 0.0), (levels[0], 0.085), (levels[1], 0.085)):
            for bx_i in range(3):
                for by_i in range(2):
                    if (b * 7 + bx_i * 3 + by_i + int(lz * 10)) % 5 == 4:
                        continue  # a picked slot
                    h = 0.42 + 0.10 * ((bx_i + by_i + b) % 3)
                    make_box(f"{prefix}_Box_{b}_{lz:.1f}_{bx_i}_{by_i}",
                             (x - 0.33 + bx_i * 0.33, cy - 0.5 + by_i * 1.0,
                              lz + dz + h / 2.0 + 0.005),   # on the floor / the deck (2026-09-22: 2 cm up, 58 boxes)
                             (0.30, 0.42, h),
                             COL_BOX if (bx_i + by_i) % 2 == 0 else COL_BOX_DK)
                    make_box(f"{prefix}_Tape_{b}_{lz:.1f}_{bx_i}_{by_i}",
                             (x - 0.33 + bx_i * 0.33, cy - 0.5 + by_i * 1.0,
                              lz + dz + h + 0.009),   # on the box's lid
                             (0.30, 0.06, 0.008), COL_TAPE)


def build_racks():
    _rack_row("RackW", -2.55, 0.8, 7.2)
    _rack_row("RackE", 2.55, 2.2, 7.2)


def build_floor_stock():
    """Mid-floor: pallet of shrink-wrapped cases with the jack parked
    in it, a hand truck against the east rack, a broom leaning."""
    px, py = -0.45, 5.2
    make_box("Pallet", (px, py, 0.07), (1.1, 1.1, 0.13), COL_PALLET)
    for r in range(2):
        for c in range(2):
            for lv in range(3):
                make_box(f"PalBox_{r}_{c}_{lv}",
                         (px - 0.26 + c * 0.52, py - 0.26 + r * 0.52, 0.34 + lv * 0.40),
                         (0.48, 0.48, 0.38), COL_BOX if (r + c + lv) % 2 else COL_BOX_DK)
    make_box("Pallet_Wrap", (px, py, 0.75), (1.06, 1.06, 1.25), COL_WRAP)
    # Pallet jack, forks in
    make_box("Jack_Fork_L", (px - 0.18, py - 0.9, 0.05), (0.16, 1.0, 0.06), COL_JACK)
    make_box("Jack_Fork_R", (px + 0.18, py - 0.9, 0.05), (0.16, 1.0, 0.06), COL_JACK)
    make_box("Jack_Body", (px, py - 1.45, 0.28), (0.44, 0.24, 0.44), COL_JACK)
    make_box("Jack_Handle", (px, py - 1.60, 0.75), (0.06, 0.06, 0.60), COL_STEEL_DK)   # against the body
    make_box("Jack_Grip", (px, py - 1.60, 1.06), (0.30, 0.05, 0.05), COL_RUBBER)
    # Hand truck against the east rack
    make_box("HandTruck_Frame", (1.75, 6.9, 0.65), (0.42, 0.06, 1.3), COL_STEEL)
    make_box("HandTruck_Toe", (1.75, 6.78, 0.04), (0.42, 0.30, 0.03), COL_STEEL_DK)
    for sgn in (-1, 1):
        make_cyl(f"HandTruck_Wheel_{sgn:+d}", (1.75 + sgn * 0.20, 6.95, 0.12),
                 0.11, 0.05, COL_RUBBER, segments=10, axis='X')
    # Broom leaning by the swing door
    make_cyl("Broom_Handle", (-2.0, 0.35, 0.735), 0.016, 1.45, COL_DECK, segments=6)   # on the floor
    make_box("Broom_Head", (-2.0, 0.42, 0.06), (0.30, 0.08, 0.12), COL_BOX_DK)


def build_store_door():
    """The swing door to the store (porthole window), the time clock
    and punch-card rack beside it — Diego's shift furniture."""
    make_box("SwingDoor", (0.0, 0.06, 1.05), (2.0, 0.08, 2.10), COL_SWING)
    make_box("SwingDoor_Seam", (0.0, 0.05, 1.05), (0.03, 0.10, 2.05), COL_STEEL_DK)
    for sgn in (-1, 1):
        make_cyl(f"SwingDoor_Port_{sgn:+d}", (sgn * 0.5, 0.055, 1.55), 0.16, 0.10,
                 (0.55, 0.62, 0.66, 0.5), segments=12, axis='Y')
        make_box(f"SwingDoor_Plate_{sgn:+d}", (sgn * 0.5, 0.055, 0.85),
                 (0.30, 0.10, 0.30), COL_STEEL)
    # Time clock + card rack (east of the door)
    make_box("TimeClock", (1.75, 0.10, 1.55), (0.30, 0.14, 0.36), COL_STEEL_DK)
    make_box("TimeClock_Face", (1.75, 0.18, 1.62), (0.20, 0.02, 0.16), COL_CARD)
    make_box("CardRack", (2.35, 0.08, 1.50), (0.44, 0.06, 0.60), COL_STEEL)
    for r in range(3):
        for c in range(4):
            make_box(f"PunchCard_{r}_{c}", (2.20 + c * 0.10, 0.12, 1.68 - r * 0.20),
                     (0.075, 0.02, 0.16), COL_CARD)


def build_fluorescents():
    """Bare twin-tube fixtures in two rows — the canon 'bare
    fluorescent tubes'. Emissive-bright so the env glow lifts them;
    the tscn Omnis hang just under the fixtures."""
    for row_x in (-1.6, 1.4):
        for fy in (1.6, 4.0, 6.4):
            make_box(f"Fix_{row_x:+.1f}_{fy:.1f}", (row_x, fy, CEIL - 0.10),
                     (0.32, 1.30, 0.07), COL_FIXTURE)
            for dx in (-0.08, 0.08):
                make_cyl(f"Tube_{row_x:+.1f}_{fy:.1f}_{dx:+.2f}",
                         (row_x + dx, fy, CEIL - 0.16), 0.022, 1.24,
                         COL_TUBE, segments=8, axis='Y')
            # conduit drop
            make_box(f"Conduit_{row_x:+.1f}_{fy:.1f}", (row_x, fy, CEIL - 0.035),
                     (0.04, 0.04, 0.07), COL_STEEL_DK)


def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    THE BALE ("He is at the bale at the eighth pallet's lid when
    his hands stop."): a cardboard baler against the east wall by
    the swing door and the strapped bale on the floor beside it;
    THE HANDS as two grip-worn patches on the bale's top; and for
    the dock preset THE SMEAR ("the rust-colored thermal smear is
    visible" above the cedar on the far horizon) — a dark cedar
    band and a translucent rust band far north of the dock."""
    make_box("Baler_Body", (2.95, 1.5, 0.95), (0.90, 0.80, 1.90), (0.30, 0.34, 0.40, 1.0))
    make_box("Baler_Mouth", (2.50, 1.5, 1.20), (0.02, 0.70, 0.50), (0.12, 0.12, 0.14, 1.0))
    make_box("Cardboard_Bale", (2.90, 0.40, 0.35), (0.90, 0.70, 0.70), (0.66, 0.54, 0.38, 1.0))
    for si, sy in enumerate((0.22, 0.58)):
        # three faces of a strap ON the bale (2026-09-22: one slab
        # through it) — top run + the two side drops
        make_box(f"Bale_Strap_{si}_Top", (2.90, sy, 0.7075), (0.92, 0.04, 0.015), (0.20, 0.20, 0.22, 1.0))
        make_box(f"Bale_Strap_{si}_W", (2.4425, sy, 0.35), (0.015, 0.04, 0.70), (0.20, 0.20, 0.22, 1.0))
        make_box(f"Bale_Strap_{si}_E", (3.3575, sy, 0.35), (0.015, 0.04, 0.70), (0.20, 0.20, 0.22, 1.0))
    make_box("Hands_Bale_Grip_A", (2.75, 0.40, 0.7015), (0.12, 0.08, 0.003), (0.56, 0.46, 0.32, 1.0))
    make_box("Hands_Bale_Grip_B", (3.05, 0.40, 0.7015), (0.12, 0.08, 0.003), (0.56, 0.46, 0.32, 1.0))
    # (2026-10-05: the cedar slab and the hard orange smear bar are
    # build_dawn_east_2026_10 now — scattered cedars, a sky, a haze)
    # The dock view is an EXTERIOR now (stump-hunt horizon rule):
    # ground past the apron and receding treeline bands north.
    from _props.detail import make_far_bands
    make_box("Ground_Far_N", (0.0, 120.0, -0.03), (400.0, 220.0, 0.02), (0.15, 0.20, 0.13, 1.0))
    make_far_bands("FarTrees", (0.13, 0.20, 0.11),
                   # (2026-10-06: were 8-17 m — a wall over the horizon that hid
                   # the dawn and the smear; Texas cedar scrub is low and flat)
                   [(60.0, 90.0, 4.0, 0.90), (120.0, 150.0, 5.0, 0.70),
                    (220.0, 240.0, 6.0, 0.52), (400.0, 380.0, 7.0, 0.40)],
                   sides="N", cy=8.0, profile="treeline")


def build_dawn_east_2026_10():
    """THE VIEW FROM THE DOCK, pre-dawn (ch 10 / ch 16, 2026-10-05). "The
    cedar scrub is, at five oh-six, beginning to register as scrub rather
    than as dark. The sky behind it, to the east, is doing the particular
    pre-dawn thing the Texas sky does — not yet light, no longer dark ...
    Above the cedar, on the far horizon, the rust-colored thermal smear
    is visible." The contact sheet's darkest frame: outside the roll-up
    there was a navy background the grade crushed to black, one slab of
    'cedar' and a hard orange bar. The dock faces +Y (the story's east).

      · THE SKY as the scene's ProceduralSkyMaterial — deep blue overhead
        easing to a warm horizon where the sun will come;
      · THE SMEAR as a haze in that sky: three soft translucent rust bands,
        widest and faintest on top, over the cedar line;
      · THE CEDAR SCRUB as scattered dark cedars past the apron — near,
        then thicker, then the treeline bands.
    """
    # THE SKY itself is the scene's ProceduralSkyMaterial now (2026-10-06):
    # band boxes out past the fog were lit only by ambient and read black.
    # a haze, not a bar: seven thin overlapping veils, ragged ends, the
    # densest low and off-centre, fading upward. A sky CARD 55 m out,
    # scaled to subtend the far horizon's angle from the dock (it stands
    # over the 60 m treeline band, inside the insert audit's 40 m reach
    # of shot_insert_smear and well inside the fog)
    smear_y = 55.0
    for k, (dx, z, h, a, w) in enumerate(((2.3, 4.5, 0.7, 0.40, 23.0), (6.8, 4.85, 0.9, 0.32, 33.0),
                                          (-3.4, 5.15, 1.0, 0.24, 28.0), (5.1, 5.55, 1.5, 0.18, 48.0),
                                          (-8.0, 5.9, 1.25, 0.14, 26.0), (3.4, 6.45, 2.0, 0.10, 62.0),
                                          (11.4, 7.1, 1.7, 0.07, 40.0))):
        make_box(f"Sky_Thermal_Smear_{k}", (dx, smear_y + k * 0.5, z), (w, 0.3, h), (0.84, 0.52, 0.36, a))
    # the cedar scrub past the apron: near, then thicker
    for k in range(48):
        cx = -26.0 + (k * 7.3) % 52.0
        cy = 16.0 + (k * 11.7) % 34.0 + (k // 16) * 6.0
        if abs(cx) < 4.0 and cy < 22.0:
            continue                                   # keep the truck lane clear
        h = 1.6 + 1.6 * ((k * 37) % 10) / 10.0
        r = 0.6 + 0.5 * ((k * 13) % 7) / 7.0
        # (2026-10-08) Ashe juniper is a lumpy bush, not a cone (the contact
        # sheet read a field of party hats): three noise blobs stacked and
        # narrowing, a trunk up to the lowest
        col = ((0.14, 0.20, 0.14, 1.0), (0.17, 0.22, 0.15, 1.0), (0.12, 0.18, 0.13, 1.0))[k % 3]
        z0 = max(0.25, 0.35 * h - 0.80 * r)
        make_cyl(f"Cedar_{k}_Trunk", (cx, cy, (z0 + 0.10) / 2.0), 0.08, z0 + 0.10, (0.24, 0.18, 0.14, 1.0), segments=6)
        for bi, (fz, fr) in enumerate(((0.35, 1.0), (0.64, 0.74), (0.88, 0.46))):
            make_blob(f"Cedar_{k}_Crown_{bi}", (cx + 0.08 * ((k + bi) % 3 - 1), cy, h * fz), r * fr, col,
                      noise=0.30, seed=k * 3 + bi, squash=0.85)



def build_back_of_house_2026_10():
    """THE STOCKROOM'S WALLS (2026-10-08; "too bare and empty" — 12 % of the
    walls held anything at eye height). Back of house: the workbench with
    "the stockroom drawer" where Jessa keeps the canvas gloves, the empty
    pallets stacked by the dock, a stretch-wrap roll, the mop sink and its
    bucket by the swing doors, yellow bollards at the dock door, a dock
    board, the electrical panel and its conduit, a high wall fan, the
    extinguisher, the first-aid box and the eyewash, the safety posters."""
    from _props.geometry import make_chamfer_box, make_tube
    WF, EF, SF, NF = -ROOM_W/2.0 + 0.10, ROOM_W/2.0 - 0.10, 0.10, ROOM_D - 0.10
    steel = (0.56, 0.58, 0.60, 1.0); steel_dk = (0.34, 0.36, 0.38, 1.0)
    yellow = (0.94, 0.78, 0.16, 1.0); red = (0.80, 0.16, 0.14, 1.0); white = (0.94, 0.94, 0.90, 1.0)
    # the workbench on the W wall north of the rack, its drawer, the gloves
    bx, by = WF + 0.25, 6.55
    make_box("Workbench_Top", (bx, by, 0.90), (0.50, 1.50, 0.05), (0.56, 0.44, 0.30, 1.0))
    for e in (-1, 1):
        for f in (-1, 1):
            make_box(f"Workbench_Leg_{e:+d}_{f:+d}", (bx + e * 0.20, by + f * 0.68, 0.44), (0.05, 0.05, 0.88), steel_dk)
    make_box("Workbench_Drawer", (bx + 0.21, by - 0.30, 0.80), (0.08, 0.50, 0.14), steel)
    make_box("Workbench_Drawer_Pull", (bx + 0.255, by - 0.30, 0.80), (0.01, 0.16, 0.02), steel_dk)
    make_box("Workbench_Shelf", (bx, by, 0.20), (0.35, 1.31, 0.03), (0.56, 0.44, 0.30, 1.0))
    for gi in range(2):
        make_box(f"Canvas_Gloves_{gi}", (bx - 0.05 + gi * 0.10, by + 0.30, 0.935), (0.10, 0.20, 0.02), (0.86, 0.78, 0.58, 1.0))
    make_box("Box_Cutter", (bx - 0.10, by + 0.05, 0.93), (0.03, 0.14, 0.015), yellow)
    make_box("Tape_Gun", (bx + 0.05, by - 0.20, 0.97), (0.10, 0.22, 0.10), red)
    make_box("Receiving_Clipboard", (WF + 0.008, by, 1.45), (0.015, 0.24, 0.32), (0.60, 0.46, 0.30, 1.0))
    make_box("Receiving_Clipboard_Sheet", (WF + 0.017, by, 1.42), (0.002, 0.21, 0.26), white)
    # the empty pallets stacked against the dock wall, west of the door
    for k in range(6):
        make_box(f"Empty_Pallet_{k}", (-2.35, NF - 0.62, 0.075 + k * 0.15), (1.00, 1.20, 0.14), (0.62, 0.50, 0.34, 1.0))
    make_cyl("Stretch_Wrap", (-2.35, NF - 0.62, 0.90 + 0.25), 0.06, 0.50, (0.80, 0.86, 0.90, 0.7), segments=10)
    # the mop sink and the bucket by the swing doors
    make_box("Mop_Sink", (-2.95, SF + 0.30, 0.25), (0.70, 0.60, 0.50), (0.86, 0.86, 0.84, 1.0))
    make_box("Mop_Sink_Basin", (-2.95, SF + 0.30, 0.49), (0.58, 0.48, 0.02), (0.56, 0.58, 0.60, 1.0))
    make_tube("Mop_Sink_Faucet", [(-2.95, SF + 0.01, 0.90), (-2.95, SF + 0.18, 0.92), (-2.95, SF + 0.22, 0.80)], 0.015, steel)
    make_cyl("Mop_Bucket", (-1.55, 0.62, 0.20), 0.20, 0.40, yellow, segments=12)
    make_box("Mop_Bucket_Wringer", (-1.55, 0.62, 0.46), (0.24, 0.20, 0.12), (0.30, 0.30, 0.32, 1.0))
    make_cyl("Mop_Handle", (-1.48, 0.62, 0.95), 0.014, 1.00, (0.62, 0.48, 0.30, 1.0), segments=6)
    # yellow bollards either side of the dock door; the dock board leaning
    for e in (-1, 1):
        make_cyl(f"Dock_Bollard_{e:+d}", (e * 1.70, NF - 0.25, 0.55), 0.10, 1.10, yellow, segments=12)
        make_cyl(f"Dock_Bollard_{e:+d}_Cap", (e * 1.70, NF - 0.25, 1.12), 0.11, 0.04, (0.20, 0.20, 0.22, 1.0), segments=12)
    make_box("Dock_Board", (2.45, NF - 0.06, 0.70), (0.90, 0.06, 1.40), steel)
    make_box("Dock_Board_Stripe", (2.45, NF - 0.095, 1.25), (0.90, 0.01, 0.10), yellow)
    # the electrical panel on the W wall, its conduit to the ceiling; a wall fan high
    make_box("Electrical_Panel", (WF + 0.08, 7.55, 1.55), (0.16, 0.60, 0.90), (0.62, 0.64, 0.64, 1.0))
    make_box("Electrical_Panel_Label", (WF + 0.162, 7.55, 1.85), (0.002, 0.20, 0.06), yellow)
    make_cyl("Electrical_Panel_Conduit", (WF + 0.05, 7.55, (2.00 + CEIL) / 2.0), 0.02, CEIL - 2.00, steel_dk, segments=6)
    make_cyl("Wall_Fan_Bracket", (WF + 0.08, 4.40, 3.35), 0.03, 0.16, steel_dk, axis='X', segments=8)
    make_cyl("Wall_Fan_Cage", (WF + 0.28, 4.40, 3.35), 0.32, 0.18, (0.30, 0.32, 0.34, 1.0), axis='X', segments=16)
    # the safety corner on the S wall west of the doors
    make_cyl("Extinguisher", (-1.25, SF + 0.09, 0.70), 0.08, 0.50, red, segments=10)
    make_box("Extinguisher_Bracket", (-1.25, SF + 0.01, 0.80), (0.10, 0.02, 0.12), steel_dk)
    make_box("Extinguisher_Sign", (-1.25, SF + 0.005, 1.70), (0.30, 0.01, 0.30), red)
    make_box("FirstAid_Box", (-1.75, SF + 0.06, 1.40), (0.32, 0.12, 0.26), white)
    make_box("FirstAid_Cross_H", (-1.75, SF + 0.121, 1.40), (0.14, 0.002, 0.04), red)
    make_box("FirstAid_Cross_V", (-1.75, SF + 0.121, 1.40), (0.04, 0.002, 0.14), red)
    make_box("Eyewash_Station", (-2.25, SF + 0.08, 1.30), (0.30, 0.16, 0.36), (0.20, 0.52, 0.30, 1.0))
    for pi, (px, col) in enumerate(((-3.10, (0.94, 0.86, 0.30, 1.0)), (-2.70, (0.30, 0.50, 0.74, 1.0)))):
        make_box(f"Safety_Poster_{pi}", (px, SF + 0.005, 1.75), (0.34, 0.01, 0.46), col)
        make_box(f"Safety_Poster_{pi}_Text", (px, SF + 0.011, 1.70), (0.26, 0.002, 0.24), white)

def main():
    clear_scene()
    build_shell()
    build_dock()
    build_racks()
    build_floor_stock()
    build_store_door()
    build_fluorescents()
    build_hero_props_2026_09()
    build_dawn_east_2026_10()
    build_back_of_house_2026_10()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/centro_stockroom.glb"))
    print(f"\n[build_centro_stockroom] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
