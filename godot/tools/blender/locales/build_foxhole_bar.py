"""foxhole_bar — THE FOXHOLE, front of house. Vol 6 canon.

The Foxhole: music venue on the back side of the Live Oak Street
strip mall, New Auburn TX. Opened 2019, owner Pip Henson, $5 cover,
all-ages until 10 (lore/planned_community/music_strata.md, ERA IV).
Working Gulf Coast rock club, not glamorous: duct-taped cables,
sticker-crusted surfaces, a good PA.

Canon dressed into this room:
  · Bar in the back — Jesse drinks his not-technically-legal beer
    here during Chess's set (vol6_ch22_foxhole.json).
  · Ricky's sound board — at the board since 2009, Topo Chico in
    the cooler UNDER the board (vol6_ch22_foxhole.json).
  · Slice of the stage + the two vertical truss towers with six
    programmable LED fixtures at the stage lip, cycling deep blue →
    deep purple → small magenta (Ramón's rig, vol6_ch20_bridge.json).
  · The small DJ booth at the side of the stage — Chess's laptop +
    modular rig + estate-sale record crate (vol6_ch20/ch22,
    music_strata.md "DJ CHESS").
  · High-top to the left of the stage (vol6_ch22_foxhole.json).
  · Wall of mustard photocopied flyers — half-letter, two colours,
    hand-drawn 2019 block lettering nobody has updated
    (vol6_ch14_substation_nine.json); tonight's fresh SAT 8/22 print
    (vol6_ch20_bridge.json chalk-marquee bill).
  · Wall clock frozen at 6:20 — sound check (vol6_ch22_foxhole.json).
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling
from _props.store_fixtures import make_register
from _props.decor import make_wall_clock
from _props.safety import (make_smoke_detector, make_hvac_vent,
                            make_fluorescent_tube_fixture,
                            make_ceiling_speaker, make_emt_conduit_run,
                            make_bug_zapper)

# Shell footprint — KEPT from the scaffold; the Background3D camera
# preset ("foxhole_bar", entrance at the S door looking N) and the
# .tscn lights are tuned to it.
ROOM_W = 8.0; ROOM_D = 6.0; CEIL = 3.0

# ══ FOXHOLE SHARED PALETTE ═══════════════════════════════════════
# KEEP IN SYNC — declared identically in build_foxhole_bar.py /
# build_foxhole_stage.py / build_foxhole_dressing_room.py.
# One venue, three rooms: black-painted everything, beer-worn brown
# floor, silver duct tape, mustard flyer stock, fox-red accent, and
# Ramón's blue→purple→magenta LED cycle (vol6_ch20_bridge.json).
FOX_WALL        = (0.25, 0.21, 0.18, 1.0)   # scuffed charcoal-brown paint
FOX_BASEBOARD   = (0.13, 0.11, 0.09, 1.0)
FOX_FLOOR       = (0.27, 0.20, 0.14, 1.0)   # beer-worn brown plank
FOX_FLOOR_SEAM  = (0.15, 0.11, 0.08, 1.0)
FOX_FLOOR_SCUFF = (0.20, 0.15, 0.11, 1.0)
FOX_CEIL_TILE   = (0.20, 0.18, 0.16, 1.0)   # black-painted drop tile
FOX_CEIL_GRID   = (0.14, 0.13, 0.12, 1.0)
FOX_CEIL_STAIN  = (0.30, 0.26, 0.20, 1.0)
FOX_BLACK       = (0.10, 0.09, 0.09, 1.0)   # amps / PA / truss matte
FOX_STAGE_DECK  = (0.16, 0.13, 0.10, 1.0)   # scuffed black stage ply
FOX_STEEL       = (0.58, 0.60, 0.62, 1.0)
FOX_CHROME      = (0.78, 0.80, 0.82, 1.0)
FOX_WOOD        = (0.38, 0.27, 0.17, 1.0)   # bar top / table wood
FOX_TAPE_DUCT   = (0.56, 0.58, 0.61, 1.0)   # silver duct/gaff tape
FOX_TAPE_MASK   = (0.85, 0.79, 0.62, 1.0)   # Ricky's masking tape
FOX_FLYER       = (0.80, 0.66, 0.30, 1.0)   # faded mustard flyer stock
FOX_INK         = (0.16, 0.14, 0.12, 1.0)   # photocopy black
FOX_RED         = (0.70, 0.20, 0.16, 1.0)   # venue accent fox-red
FOX_CREAM       = (0.90, 0.86, 0.74, 1.0)
FOX_AMBER       = (0.92, 0.60, 0.24, 1.0)   # beer-sign warm
FOX_TOPO_GREEN  = (0.36, 0.55, 0.42, 1.0)   # Topo Chico glass
FOX_LED_BLUE    = (0.24, 0.34, 0.84, 1.0)   # Ramón's cue: deep blue…
FOX_LED_PURPLE  = (0.46, 0.24, 0.76, 1.0)   # …into deep purple…
FOX_LED_MAGENTA = (0.78, 0.26, 0.60, 1.0)   # …into a small magenta
FOX_STICKERS    = [(0.72, 0.28, 0.20, 1.0), (0.30, 0.46, 0.60, 1.0),
                   (0.86, 0.72, 0.30, 1.0), (0.42, 0.56, 0.36, 1.0),
                   (0.88, 0.86, 0.80, 1.0), (0.50, 0.30, 0.56, 1.0)]
PAL_WALL = {"wall": FOX_WALL, "baseboard": FOX_BASEBOARD}
PAL_CEIL = {"tile": FOX_CEIL_TILE, "grid": FOX_CEIL_GRID}
# ══ end shared palette ═══════════════════════════════════════════


# ── Shared venue micro-props (same helpers in all three files) ────
def _flyer(nm, pos, *, axis='X', face=-1, fresh=False, extra_line=False):
    """Photocopied Foxhole flyer — canon vol6_ch14_substation_nine:
    half-letter, two colours, black ink on faded mustard, hand-drawn
    block lettering unchanged since 2019. fresh=True = this week's
    print (whiter stock). axis='X' = flyer on an X-running (N/S)
    wall; axis='Y' = on an E/W wall. face pushes it off the wall."""
    stock = FOX_CREAM if fresh else FOX_FLYER
    x, y, z = pos
    w, h = 0.28, 0.42
    if axis == 'X':
        make_box(f"{nm}_Paper", (x, y + face * 0.012, z), (w, 0.006, h), stock)
        make_box(f"{nm}_Head", (x, y + face * 0.017, z + 0.13),
                 (w * 0.80, 0.002, 0.09), FOX_INK)
        make_box(f"{nm}_Body", (x, y + face * 0.017, z - 0.06),
                 (w * 0.70, 0.002, 0.16), FOX_INK)
        if extra_line:
            make_box(f"{nm}_Bill", (x, y + face * 0.017, z - 0.17),
                     (w * 0.60, 0.002, 0.03), FOX_INK)
    else:
        make_box(f"{nm}_Paper", (x + face * 0.012, y, z), (0.006, w, h), stock)
        make_box(f"{nm}_Head", (x + face * 0.017, y, z + 0.13),
                 (0.002, w * 0.80, 0.09), FOX_INK)
        make_box(f"{nm}_Body", (x + face * 0.017, y, z - 0.06),
                 (0.002, w * 0.70, 0.16), FOX_INK)
        if extra_line:
            make_box(f"{nm}_Bill", (x + face * 0.017, y, z - 0.17),
                     (0.002, w * 0.60, 0.03), FOX_INK)


def _sticker(nm, pos, i, *, axis='X', face=-1):
    """One gig sticker on a vertical surface. Deterministic tint/size
    from index i — sticker crust is the venue's wallpaper."""
    x, y, z = pos
    col = FOX_STICKERS[i % len(FOX_STICKERS)]
    w = 0.10 + (i % 3) * 0.03
    h = 0.06 + ((i + 1) % 3) * 0.02
    if axis == 'X':
        make_box(f"{nm}_Sticker_{i}", (x, y + face * 0.006, z), (w, 0.003, h), col)
    else:
        make_box(f"{nm}_Sticker_{i}", (x + face * 0.006, y, z), (0.003, w, h), col)


def _cable_x(nm, x0, x1, y, *, taped=True):
    """Floor cable running E-W, duct-taped down every ~80 cm."""
    make_box(f"{nm}_Run", ((x0 + x1) / 2.0, y, 0.012),
             (abs(x1 - x0), 0.05, 0.022), FOX_BLACK)
    if taped:
        n = max(2, int(abs(x1 - x0) / 0.8))
        for t in range(n):
            tx = min(x0, x1) + (t + 0.5) * abs(x1 - x0) / n
            make_box(f"{nm}_Tape_{t}", (tx, y, 0.026),
                     (0.08, 0.14, 0.004), FOX_TAPE_DUCT)


def _cable_y(nm, y0, y1, x, *, taped=True):
    """Floor cable running N-S, duct-taped down every ~80 cm."""
    make_box(f"{nm}_Run", (x, (y0 + y1) / 2.0, 0.012),
             (0.05, abs(y1 - y0), 0.022), FOX_BLACK)
    if taped:
        n = max(2, int(abs(y1 - y0) / 0.8))
        for t in range(n):
            ty = min(y0, y1) + (t + 0.5) * abs(y1 - y0) / n
            make_box(f"{nm}_Tape_{t}", (x, ty, 0.026),
                     (0.14, 0.08, 0.004), FOX_TAPE_DUCT)
# ── end shared micro-props ────────────────────────────────────────


def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": FOX_FLOOR, "seam": FOX_FLOOR_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    # South wall with the entrance gap x ∈ [-1, +1] (camera doorway).
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0,
              height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0,
              height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), FOX_WALL)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
                 palette=PAL_CEIL, with_stains=False)
    # Water stains hung BELOW the tile plane so they actually read.
    for si, (sx, sy) in enumerate([(-1.6, 4.8), (2.2, 1.6)]):
        make_box(f"Ceil_Stain_{si}", (sx, sy, CEIL - 0.006), (0.75, 0.75, 0.004),
                 FOX_CEIL_STAIN)
    # Wear paths: in front of the bar rail and through the door.
    make_box("Floor_Scuff_Bar", (2.35, 3.2, 0.007), (0.55, 3.6, 0.002), FOX_FLOOR_SCUFF)
    make_box("Floor_Scuff_Door", (0.0, 0.45, 0.007), (1.6, 0.80, 0.002), FOX_FLOOR_SCUFF)


def build_stage_corner():
    """West slice of the stage as seen from FOH, with Ramón's two
    truss towers at the lip (vol6_ch20_bridge.json: six programmable
    LED fixtures on two vertical truss towers, blue→purple→magenta)."""
    deck_top = 0.47
    make_box("Stage_Deck", (-3.3, 3.4, 0.225), (1.2, 4.0, 0.45), FOX_STAGE_DECK)
    make_box("Stage_DeckSheet", (-3.3, 3.4, deck_top - 0.01), (1.2, 4.0, 0.02), FOX_BLACK)
    make_box("Stage_Skirt", (-2.69, 3.4, 0.225), (0.02, 4.0, 0.45), FOX_BLACK)
    for i in range(5):
        _sticker("StageSkirt", (-2.68, 1.9 + i * 0.75, 0.16 + (i % 2) * 0.16), i,
                 axis='Y', face=+1)
    # Monitor wedge on the deck lip.
    make_box("StgWedge_Body", (-3.0, 2.4, deck_top + 0.13), (0.45, 0.32, 0.26), FOX_BLACK)
    make_box("StgWedge_Grille", (-2.77, 2.4, deck_top + 0.13), (0.012, 0.26, 0.18),
             (0.24, 0.22, 0.20, 1.0))
    # Em's mic stand, parked from load-in (vol6_ch22).
    make_cyl("StgMic_Base", (-3.2, 3.4, deck_top + 0.012), 0.15, 0.024, FOX_BLACK,
             segments=10)
    make_cyl("StgMic_Pole", (-3.2, 3.4, deck_top + 0.74), 0.012, 1.44, FOX_STEEL)
    make_cyl("StgMic_Head", (-3.2, 3.4, deck_top + 1.50), 0.025, 0.08,
             (0.30, 0.30, 0.32, 1.0))
    # Backline amp silhouette at the rear of the slice.
    make_box("StgAmp_Body", (-3.5, 4.7, deck_top + 0.21), (0.55, 0.30, 0.42), FOX_BLACK)
    make_box("StgAmp_Grille", (-3.5, 4.54, deck_top + 0.17), (0.46, 0.012, 0.26),
             (0.24, 0.22, 0.20, 1.0))
    # Two truss towers, three par cans each, aimed west at the stage.
    for ti, ty in enumerate([2.0, 4.8]):
        make_box(f"Truss_{ti}_Base", (-2.45, ty, 0.025), (0.48, 0.48, 0.05), FOX_STEEL)
        make_cyl(f"Truss_{ti}_Post", (-2.45, ty, 1.35), 0.05, 2.60, FOX_BLACK)
        for ci, (cz, lens) in enumerate([(1.50, FOX_LED_BLUE),
                                          (1.95, FOX_LED_PURPLE),
                                          (2.40, FOX_LED_MAGENTA)]):
            make_box(f"Truss_{ti}_Clamp_{ci}", (-2.52, ty, cz), (0.08, 0.06, 0.06),
                     FOX_STEEL)
            make_cyl(f"Truss_{ti}_Can_{ci}", (-2.66, ty, cz), 0.09, 0.20, FOX_BLACK,
                     axis='X')
            make_cyl(f"Truss_{ti}_Lens_{ci}", (-2.77, ty, cz), 0.072, 0.02, lens,
                     axis='X')


def build_dj_booth():
    """Chess's small DJ booth at the side of the stage: laptop, the
    small modular rig, estate-sale record crate (vol6_ch20/ch22,
    music_strata.md 'records and a small modular rig')."""
    for li, (lx, ly) in enumerate([(-2.35, 5.1), (-1.55, 5.1), (-2.35, 5.55),
                                    (-1.55, 5.55)]):
        make_cyl(f"DJ_Leg_{li}", (lx, ly, 0.47), 0.018, 0.94, FOX_STEEL, segments=6)
    make_box("DJ_TableTop", (-1.95, 5.32, 0.96), (0.95, 0.55, 0.04), FOX_BLACK)
    make_box("DJ_Laptop_Base", (-2.15, 5.25, 0.99), (0.28, 0.20, 0.016),
             (0.22, 0.22, 0.24, 1.0))
    make_box("DJ_Laptop_Screen", (-2.15, 5.36, 1.09), (0.26, 0.015, 0.19),
             (0.22, 0.22, 0.24, 1.0))
    make_box("DJ_Laptop_Glow", (-2.15, 5.35, 1.09), (0.22, 0.004, 0.15),
             (0.32, 0.42, 0.46, 1.0))
    make_box("DJ_Modular_Case", (-1.70, 5.32, 1.03), (0.36, 0.28, 0.10), FOX_BLACK)
    for ki in range(6):
        make_cyl(f"DJ_Modular_Knob_{ki}", (-1.84 + ki * 0.056, 5.19, 1.085),
                 0.009, 0.012, FOX_STICKERS[ki % len(FOX_STICKERS)], segments=6)
    make_box("DJ_Crate", (-1.95, 5.32, 0.17), (0.36, 0.36, 0.30), FOX_WOOD)
    for ri in range(3):
        make_box(f"DJ_Record_{ri}", (-2.05 + ri * 0.09, 5.32, 0.34),
                 (0.012, 0.31, 0.31), FOX_INK if ri != 1 else FOX_RED)


def build_bar():
    """The bar in the back — E wall run. Jesse's spot during Chess's
    set; the bartender who knows and does not ask (vol6_ch22)."""
    bar_top = 1.13
    # Bar body pulled 0.5 m off the backbar — the bartender who
    # knows and does not ask needs somewhere to stand.
    make_box("Bar_Body", (2.95, 3.2, 0.55), (0.60, 4.2, 1.10), FOX_WOOD)
    make_box("Bar_Top", (2.95, 3.2, bar_top), (0.80, 4.4, 0.06),
             (0.22, 0.15, 0.10, 1.0))
    make_box("Bar_Kick", (2.64, 3.2, 0.10), (0.02, 4.2, 0.20), FOX_BLACK)
    make_cyl("Bar_FootRail", (2.55, 3.2, 0.24), 0.03, 4.0, FOX_CHROME, axis='Y')
    for bi, by in enumerate([1.6, 3.2, 4.8]):
        make_box(f"Bar_RailBracket_{bi}", (2.61, by, 0.17), (0.10, 0.04, 0.14),
                 FOX_STEEL)
    # Backbar: ledge + two bottle shelves on the E wall.
    make_box("Backbar_Ledge", (3.82, 3.2, 1.00), (0.16, 4.0, 0.05), FOX_WOOD)
    for si, sz in enumerate([1.45, 1.85]):
        make_box(f"Backbar_Shelf_{si}", (3.84, 3.2, sz), (0.12, 3.8, 0.03), FOX_WOOD)
        for bi in range(12):
            by = 1.70 + bi * 0.26
            col = [FOX_AMBER, FOX_CREAM, FOX_TOPO_GREEN,
                   (0.34, 0.22, 0.14, 1.0)][(si + bi) % 4]
            make_cyl(f"Bottle_{si}_{bi}_Body", (3.84, by, sz + 0.115),
                     0.034, 0.20, col, segments=8)
            make_cyl(f"Bottle_{si}_{bi}_Neck", (3.84, by, sz + 0.26),
                     0.013, 0.09, col, segments=6)
    # Three taps on the bar top.
    for ti, ty in enumerate([2.7, 3.2, 3.7]):
        make_cyl(f"Tap_{ti}_Stem", (3.15, ty, bar_top + 0.17), 0.022, 0.28,
                 FOX_CHROME)
        make_box(f"Tap_{ti}_Handle", (3.15, ty, bar_top + 0.39), (0.05, 0.05, 0.16),
                 [FOX_RED, FOX_CREAM, FOX_BLACK][ti])
    make_register("Register", (2.95, 1.45, bar_top + 0.03))
    make_cyl("TipJar", (2.80, 1.90, bar_top + 0.10), 0.05, 0.14,
             (0.86, 0.86, 0.82, 1.0), segments=10)
    # Four stools, the venue's mismatched-but-matching fox-red seats.
    for si, sy in enumerate([2.2, 3.0, 3.8, 4.6]):
        make_cyl(f"Stool_{si}_Base", (2.17, sy, 0.015), 0.19, 0.03, FOX_BLACK,
                 segments=10)
        make_cyl(f"Stool_{si}_Post", (2.17, sy, 0.40), 0.035, 0.78, FOX_BLACK)
        make_cyl(f"Stool_{si}_Ring", (2.17, sy, 0.25), 0.12, 0.02, FOX_STEEL,
                 segments=10)
        make_cyl(f"Stool_{si}_Seat", (2.17, sy, 0.81), 0.17, 0.05, FOX_RED,
                 segments=12)
    # THE FOXHOLE over the backbar — the hand-drawn 2019 block
    # lettering nobody has updated (vol6_ch14): cream blocks with a
    # deliberate hand wobble on a black board, fox-red underline.
    make_box("FoxSign_Board", (3.88, 3.2, 2.35), (0.04, 2.60, 0.55), FOX_BLACK)
    for li in range(7):
        ly = 2.24 + li * 0.32
        lz = 2.38 + (0.02 if li % 2 == 0 else -0.02)
        make_box(f"FoxSign_Letter_{li}", (3.855, ly, lz), (0.02, 0.24, 0.34),
                 FOX_CREAM)
    make_box("FoxSign_Underline", (3.855, 3.2, 2.11), (0.02, 2.30, 0.04), FOX_RED)
    # Sticker crust on the bar front panel.
    for i in range(7):
        _sticker("BarFront", (2.635, 1.7 + i * 0.5, 0.55 + (i % 3) * 0.18), i,
                 axis='Y', face=-1)


def build_sound_station():
    """Ricky's board — at it since 2009. Folding table, console with
    a masking-tape label strip, rack unit, and the Topo Chico cooler
    UNDER the board (vol6_ch22_foxhole.json)."""
    for li, (lx, ly) in enumerate([(0.60, 2.05), (1.60, 2.05), (0.60, 2.55),
                                    (1.60, 2.55)]):
        make_cyl(f"FOH_TableLeg_{li}", (lx, ly, 0.36), 0.02, 0.72, FOX_STEEL,
                 segments=6)
    make_box("FOH_TableTop", (1.1, 2.3, 0.74), (1.15, 0.60, 0.04),
             (0.30, 0.28, 0.26, 1.0))
    make_box("FOH_Console", (1.1, 2.3, 0.80), (0.85, 0.42, 0.08), FOX_BLACK)
    for fi in range(8):
        make_box(f"FOH_Fader_{fi}", (0.79 + fi * 0.09, 2.20, 0.845),
                 (0.014, 0.045, 0.006), FOX_CREAM)
    for ki in range(8):
        make_cyl(f"FOH_Knob_{ki}", (0.79 + ki * 0.09, 2.40, 0.848),
                 0.008, 0.012, [FOX_RED, FOX_CREAM, FOX_STEEL][ki % 3], segments=6)
    make_box("FOH_TapeLabel", (1.1, 2.085, 0.81), (0.60, 0.006, 0.035),
             FOX_TAPE_MASK)
    make_box("FOH_Rack", (1.38, 2.3, 0.19), (0.45, 0.40, 0.36), FOX_BLACK)
    for ri in range(2):
        make_box(f"FOH_RackFace_{ri}", (1.38, 2.095, 0.12 + ri * 0.14),
                 (0.40, 0.006, 0.03), FOX_STEEL)
    # The cooler under the board + Topo Chico bottles.
    make_box("FOH_Cooler_Body", (0.78, 2.3, 0.20), (0.50, 0.36, 0.38), FOX_CREAM)
    make_box("FOH_Cooler_Lid", (0.78, 2.3, 0.42), (0.52, 0.38, 0.06), FOX_RED)
    make_box("FOH_Cooler_Handle", (0.78, 2.10, 0.30), (0.16, 0.02, 0.04), FOX_CREAM)
    for ti in range(2):
        make_cyl(f"FOH_Topo_{ti}_Body", (0.46, 2.10 + ti * 0.10, 0.10),
                 0.030, 0.18, FOX_TOPO_GREEN, segments=8)
        make_cyl(f"FOH_Topo_{ti}_Neck", (0.46, 2.10 + ti * 0.10, 0.23),
                 0.012, 0.08, FOX_TOPO_GREEN, segments=6)
    make_cyl("FOH_Topo_OnTable_Body", (1.55, 2.52, 0.85), 0.030, 0.18,
             FOX_TOPO_GREEN, segments=8)
    make_cyl("FOH_Topo_OnTable_Neck", (1.55, 2.52, 0.98), 0.012, 0.08,
             FOX_TOPO_GREEN, segments=6)
    make_cyl("FOH_Stool_Post", (1.1, 1.72, 0.36), 0.03, 0.72, FOX_BLACK)
    make_cyl("FOH_Stool_Seat", (1.1, 1.72, 0.745), 0.15, 0.045, FOX_BLACK,
             segments=10)
    # The snake, duct-taped across the floor to the stage.
    _cable_x("Snake", 0.50, -2.60, 2.55)
    _cable_y("Snake_StageTail", 2.55, 3.10, -2.60)


def build_high_tops():
    """High-tops to the left of the stage — where the kid who was at
    the rail tells his friend about the song (vol6_ch22)."""
    for hi, (hx, hy) in enumerate([(-1.3, 3.3), (0.2, 4.7)]):
        make_cyl(f"HT_{hi}_Base", (hx, hy, 0.018), 0.24, 0.035, FOX_BLACK,
                 segments=10)
        make_cyl(f"HT_{hi}_Post", (hx, hy, 0.53), 0.045, 1.02, FOX_BLACK)
        make_cyl(f"HT_{hi}_Top", (hx, hy, 1.06), 0.30, 0.04, FOX_WOOD, segments=12)
        for si, (ox, oy) in enumerate([(0.45, -0.15), (-0.45, 0.15)]):
            make_cyl(f"HT_{hi}_Stool_{si}_Post", (hx + ox, hy + oy, 0.37),
                     0.028, 0.74, FOX_BLACK, segments=6)
            make_cyl(f"HT_{hi}_Stool_{si}_Seat", (hx + ox, hy + oy, 0.76),
                     0.15, 0.04, FOX_RED, segments=10)


def build_flyer_wall():
    """N wall: seven years of mustard flyers plus tonight's fresh
    print (SAT 8/22 — DOORS 8 — SUBURBAN BLIGHT 9 — DJ CHESS 11,
    vol6_ch20_bridge.json), the beer neon, and the taped-label door
    to the backstage hallway (vol6_ch22: 'small hallway to the
    stage door')."""
    wall_face = ROOM_D - 0.10
    fi = 0
    for row_z in (1.85, 1.35):
        for col_x in (-1.4, -0.6, 0.2, 1.0):
            fresh = (row_z == 1.85 and col_x == 1.0)
            _flyer(f"Flyer_{fi}", (col_x, wall_face, row_z), axis='X', face=-1,
                   fresh=fresh, extra_line=fresh)
            fi += 1
    # Beer neon — warm amber block over the DJ end of the room.
    make_box("Neon_Beer_Board", (-2.6, wall_face - 0.02, 2.35), (0.90, 0.04, 0.32),
             FOX_BLACK)
    make_box("Neon_Beer_Tube", (-2.6, wall_face - 0.05, 2.35), (0.70, 0.02, 0.16),
             FOX_AMBER)
    # Backstage door: dark slab, masking-tape label, kick scuffs.
    make_box("BackstageDoor_Slab", (2.1, wall_face - 0.04, 1.02), (0.95, 0.08, 2.04),
             (0.20, 0.16, 0.13, 1.0))
    make_cyl("BackstageDoor_Knob", (2.48, wall_face - 0.11, 1.02), 0.024, 0.05,
             FOX_STEEL, axis='Y', segments=8)
    make_box("BackstageDoor_TapeLabel", (2.1, wall_face - 0.085, 1.72),
             (0.32, 0.006, 0.08), FOX_TAPE_MASK)
    make_box("BackstageDoor_TapeInk", (2.1, wall_face - 0.089, 1.72),
             (0.24, 0.004, 0.035), FOX_INK)
    make_box("BackstageDoor_KickScuff", (2.1, wall_face - 0.085, 0.18),
             (0.60, 0.006, 0.22), FOX_BLACK)
    for i in range(4):
        _sticker("DoorFrame", (2.72 + (i % 2) * 0.12, wall_face, 0.9 + i * 0.28),
                 i + 2, axis='X', face=-1)
    # House clock frozen at sound check — 6:20 (vol6_ch22).
    make_wall_clock("Clock", (2.95, wall_face - 0.02, 2.42), frozen_hour=6,
                    frozen_min=20)


def build_ceiling_infra():
    for j, ypos in enumerate([2.2, 4.2]):
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL),
                                       length=1.40, width=0.34,
                                       palette={"tube": (0.55, 0.50, 0.44, 1.0),
                                                "diffuser": (0.72, 0.58, 0.40, 1.0)})
    make_smoke_detector("Smoke", (0.0, 3.0, CEIL))
    make_hvac_vent("HVAC", (-0.5, 5.2, CEIL), width=1.0, depth=0.5)
    make_ceiling_speaker("HouseSpeaker", (-1.6, 1.6, CEIL))
    make_emt_conduit_run("Conduit_E", wall_x=ROOM_W/2.0 - 0.10, wall_face_sign=+1,
                         vert_y=5.0, vert_z_top=CEIL, ceil_z=CEIL, horiz_y_end=3.0)
    make_bug_zapper("BugZap", (-3.0, ROOM_D - 0.16, 2.45))


def main():
    clear_scene()
    build_shell()
    build_stage_corner()
    build_dj_booth()
    build_bar()
    build_sound_station()
    build_high_tops()
    build_flyer_wall()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/foxhole_bar.glb"))
    print(f"\n[build_foxhole_bar] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
