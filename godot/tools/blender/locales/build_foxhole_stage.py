"""foxhole_stage — THE FOXHOLE, the stage. Vol 6 canon.

Same venue as build_foxhole_bar.py / build_foxhole_dressing_room.py
(The Foxhole, Live Oak Street strip mall, New Auburn TX — opened
2019, music_strata.md ERA IV). This is the room the August 22 set
happens in (vol6_ch22_foxhole.json): Suburban Blight — Em's mic
front and center, Carl's kit (the high tom he hits too hard at
sound check), Nate's bass through the house DI, Jesse's Telecaster
and small amp stage right with the set list taped to the floor with
the masking tape Ricky put down at 6:48.

Canon dressed into this room:
  · Set list on the back of the Selma open-mic flyer, masking-taped
    at Jesse's position (vol6_ch22_foxhole.json).
  · House DI box at Nate's position (vol6_ch22: 'plugging the bass
    into the house DI').
  · Two vertical truss towers at the lip of the stage carrying six
    programmable LED fixtures — deep blue → deep purple → small
    magenta, Ramón Vargas Lighting (vol6_ch20_bridge.json).
  · The rail at the front — where the kid headbangs through Grid
    Failure and goes still for Substation Nine (vol6_ch22).
  · Small DJ booth at the side of the stage (vol6_ch20/ch22).
  · A good PA — the one thing this venue spends money on.
  · Stage door in the west wall — 'They walk down the small hallway
    to the stage door' (vol6_ch22_foxhole.json).
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling
from _props.safety import (make_smoke_detector, make_hvac_vent,
                            make_fluorescent_tube_fixture)

# Shell footprint — KEPT from the scaffold; the Background3D camera
# preset ("foxhole_stage") and the .tscn lights are tuned to it.
ROOM_W = 8.0; ROOM_D = 5.0; CEIL = 3.2

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

DECK_TOP = 0.48       # stage deck walking surface
DRUM_CREAM = (0.86, 0.80, 0.66, 1.0)   # aged wrap on Carl's kit
CYMBAL_GOLD = (0.76, 0.64, 0.30, 1.0)


# ── Shared venue micro-props (same helpers as build_foxhole_bar) ──
def _flyer(nm, pos, *, axis='X', face=-1, fresh=False, extra_line=False):
    """Photocopied Foxhole flyer — canon vol6_ch14_substation_nine:
    black ink on faded mustard, hand-drawn 2019 block lettering."""
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
    """One gig sticker on a vertical surface — deterministic tint."""
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


def _mic_stand(nm, x, y, base_z, *, pole_h=1.50):
    make_cyl(f"{nm}_Base", (x, y, base_z + 0.012), 0.15, 0.024, FOX_BLACK,
             segments=10)
    make_cyl(f"{nm}_Pole", (x, y, base_z + pole_h / 2.0 + 0.02), 0.012, pole_h,
             FOX_STEEL)
    make_cyl(f"{nm}_Mic", (x, y, base_z + pole_h + 0.06), 0.025, 0.08,
             (0.30, 0.30, 0.32, 1.0))
# ── end shared micro-props ────────────────────────────────────────


def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": FOX_FLOOR, "seam": FOX_FLOOR_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0,
              height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0,
              height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), FOX_WALL)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
                 palette=PAL_CEIL, with_stains=False)
    for si, (sx, sy) in enumerate([(2.6, 4.2), (-3.0, 0.9)]):
        make_box(f"Ceil_Stain_{si}", (sx, sy, CEIL - 0.006), (0.70, 0.70, 0.004),
                 FOX_CEIL_STAIN)
    # A hundred and ten people's worth of floor wear at the rail.
    make_box("Floor_Scuff_Pit", (0.0, 1.9, 0.007), (5.0, 0.9, 0.002), FOX_FLOOR_SCUFF)


def build_stage_platform():
    """0.45 m plywood riser across the N end, black-painted, sticker-
    crusted skirt, Ricky's masking-tape spikes at each position."""
    make_box("Stage_Deck", (0.0, 3.65, 0.225), (6.4, 2.3, 0.45), FOX_BLACK)
    make_box("Stage_DeckSheet", (0.0, 3.65, DECK_TOP - 0.015), (6.4, 2.3, 0.03),
             FOX_STAGE_DECK)
    make_box("Stage_Skirt", (0.0, 2.49, 0.225), (6.4, 0.02, 0.45), FOX_BLACK)
    for i in range(6):
        _sticker("StageSkirt", (-2.5 + i * 1.0, 2.48, 0.15 + (i % 2) * 0.18), i,
                 axis='X', face=-1)
    # Side step, stage right, abutting the deck's west edge — the
    # load-in path from the stage door.
    make_box("Stage_Step", (-3.5, 3.0, 0.11), (0.60, 0.45, 0.22), FOX_BLACK)
    # Deck scuff streaks — the deck has been danced on since 2019.
    for di, (dx, dy) in enumerate([(-1.4, 3.1), (0.6, 3.4), (1.8, 4.0)]):
        make_box(f"Deck_Scuff_{di}", (dx, dy, DECK_TOP + 0.002),
                 (0.55, 0.09, 0.002), (0.22, 0.18, 0.14, 1.0))
    # Masking-tape spike marks (Ricky, 6:48) at the three positions.
    for pi, (px, py) in enumerate([(-2.0, 3.35), (0.0, 2.95), (2.0, 3.35)]):
        make_box(f"Spike_{pi}_A", (px - 0.10, py - 0.16, DECK_TOP + 0.003),
                 (0.12, 0.03, 0.001), FOX_TAPE_MASK)
        make_box(f"Spike_{pi}_B", (px - 0.16, py - 0.10, DECK_TOP + 0.003),
                 (0.03, 0.12, 0.001), FOX_TAPE_MASK)


def build_drum_kit():
    """Carl's kit, center-rear — kick, snare, hi-hat, the high tom
    ('hit it like you want to be married to it'), floor tom, crash,
    ride, throne (vol6_ch22 sound check runs the whole kit)."""
    # Kick drum faces the audience; aged cream wrap, stencil bars.
    make_cyl("Kick_Shell", (0.0, 4.30, DECK_TOP + 0.28), 0.28, 0.42, DRUM_CREAM,
             axis='Y', segments=12)
    make_cyl("Kick_Head", (0.0, 4.085, DECK_TOP + 0.28), 0.27, 0.015, FOX_CREAM,
             axis='Y', segments=12)
    make_box("Kick_Stencil_A", (0.0, 4.072, DECK_TOP + 0.34), (0.30, 0.005, 0.06),
             FOX_INK)
    make_box("Kick_Stencil_B", (0.0, 4.072, DECK_TOP + 0.24), (0.22, 0.005, 0.05),
             FOX_INK)
    # Snare on its stand.
    make_cyl("Snare_Stand", (-0.42, 4.05, DECK_TOP + 0.27), 0.015, 0.54, FOX_STEEL,
             segments=6)
    make_cyl("Snare_Shell", (-0.42, 4.05, DECK_TOP + 0.60), 0.17, 0.14, DRUM_CREAM,
             segments=12)
    make_cyl("Snare_Rim", (-0.42, 4.05, DECK_TOP + 0.675), 0.175, 0.01, FOX_STEEL,
             segments=12)
    # Hi-hat — two discs with the working gap.
    make_cyl("HiHat_Stand", (-0.80, 4.15, DECK_TOP + 0.47), 0.012, 0.94, FOX_STEEL,
             segments=6)
    make_cyl("HiHat_Bottom", (-0.80, 4.15, DECK_TOP + 0.945), 0.17, 0.008,
             CYMBAL_GOLD, segments=12)
    make_cyl("HiHat_Top", (-0.80, 4.15, DECK_TOP + 0.975), 0.17, 0.008,
             CYMBAL_GOLD, segments=12)
    # High tom (the one Carl hits too hard), mounted over the kick.
    make_cyl("HighTom_Shell", (0.25, 4.42, DECK_TOP + 0.68), 0.14, 0.16, DRUM_CREAM,
             segments=12)
    make_box("HighTom_Mount", (0.12, 4.36, DECK_TOP + 0.56), (0.04, 0.04, 0.14),
             FOX_STEEL)
    # Floor tom on its three legs.
    make_cyl("FloorTom_Shell", (0.55, 4.12, DECK_TOP + 0.48), 0.18, 0.28, DRUM_CREAM,
             segments=12)
    for li, (lx, ly) in enumerate([(0.40, 3.98), (0.70, 3.98), (0.55, 4.28)]):
        make_cyl(f"FloorTom_Leg_{li}", (lx, ly, DECK_TOP + 0.17), 0.008, 0.34,
                 FOX_STEEL, segments=6)
    # Crash + ride.
    make_cyl("Crash_Stand", (-1.10, 4.45, DECK_TOP + 0.65), 0.012, 1.30, FOX_STEEL,
             segments=6)
    make_cyl("Crash_Cymbal", (-1.10, 4.45, DECK_TOP + 1.32), 0.19, 0.008,
             CYMBAL_GOLD, segments=12)
    make_cyl("Ride_Stand", (0.95, 4.52, DECK_TOP + 0.58), 0.012, 1.16, FOX_STEEL,
             segments=6)
    make_cyl("Ride_Cymbal", (0.95, 4.52, DECK_TOP + 1.18), 0.22, 0.008,
             CYMBAL_GOLD, segments=12)
    # Throne.
    make_cyl("Throne_Post", (0.0, 4.70, DECK_TOP + 0.22), 0.03, 0.44, FOX_STEEL,
             segments=8)
    make_cyl("Throne_Seat", (0.0, 4.70, DECK_TOP + 0.47), 0.16, 0.06, FOX_BLACK,
             segments=12)


def build_guitar_side():
    """Stage right — Jesse: the small amp from the Civic's trunk,
    the Telecaster, and the set list masking-taped at his feet on
    the back of the Selma open-mic flyer (vol6_ch22)."""
    make_box("GtrAmp_Body", (-2.5, 4.30, DECK_TOP + 0.21), (0.55, 0.30, 0.42),
             FOX_BLACK)
    make_box("GtrAmp_Grille", (-2.5, 4.14, DECK_TOP + 0.17), (0.46, 0.012, 0.26),
             (0.24, 0.22, 0.20, 1.0))
    make_box("GtrAmp_Panel", (-2.5, 4.14, DECK_TOP + 0.36), (0.46, 0.012, 0.06),
             FOX_STEEL)
    # Telecaster on its A-stand (butterscotch — the 1994 Whitfield
    # pair, lore/planned_community/music_strata.md).
    make_box("Tele_Body", (-2.95, 4.25, DECK_TOP + 0.26), (0.30, 0.06, 0.40),
             (0.85, 0.62, 0.30, 1.0))
    make_box("Tele_Pickguard", (-3.0, 4.215, DECK_TOP + 0.24), (0.13, 0.005, 0.20),
             FOX_CREAM)
    make_box("Tele_Neck", (-2.95, 4.25, DECK_TOP + 0.72), (0.05, 0.04, 0.52),
             FOX_WOOD)
    make_box("Tele_Head", (-2.95, 4.25, DECK_TOP + 1.04), (0.08, 0.03, 0.13),
             FOX_WOOD)
    for si, sx in enumerate([-3.05, -2.85]):
        make_cyl(f"Tele_StandLeg_{si}", (sx, 4.32, DECK_TOP + 0.17), 0.010, 0.34,
                 FOX_BLACK, segments=6)
    # The set list at Jesse's feet.
    make_box("SetList_Paper", (-2.0, 3.10, DECK_TOP + 0.004), (0.11, 0.15, 0.002),
             FOX_CREAM)
    for li in range(5):
        make_box(f"SetList_Line_{li}", (-2.0, 3.155 - li * 0.026, DECK_TOP + 0.006),
                 (0.08, 0.012, 0.001), FOX_INK)
    make_box("SetList_TapeN", (-2.0, 3.19, DECK_TOP + 0.007), (0.12, 0.03, 0.001),
             FOX_TAPE_MASK)
    make_box("SetList_TapeS", (-2.0, 3.01, DECK_TOP + 0.007), (0.12, 0.03, 0.001),
             FOX_TAPE_MASK)
    _mic_stand("Mic_Jesse", -2.0, 3.35, DECK_TOP, pole_h=1.45)
    # Amp cord — 'the cord is at his left' (vol6_ch22).
    make_box("GtrCord", (-2.25, 3.70, DECK_TOP + 0.006), (0.04, 0.85, 0.012),
             FOX_BLACK)


def build_bass_side():
    """Stage left — Nate: bass stack and the house DI box."""
    make_box("BassCab_Body", (2.4, 4.35, DECK_TOP + 0.375), (0.55, 0.40, 0.75),
             FOX_BLACK)
    make_box("BassCab_Grille", (2.4, 4.14, DECK_TOP + 0.34), (0.46, 0.012, 0.58),
             (0.24, 0.22, 0.20, 1.0))
    make_box("BassHead", (2.4, 4.35, DECK_TOP + 0.83), (0.55, 0.35, 0.16),
             FOX_BLACK)
    make_box("BassHead_Face", (2.4, 4.16, DECK_TOP + 0.83), (0.46, 0.012, 0.10),
             FOX_STEEL)
    make_box("DI_Box", (1.75, 3.85, DECK_TOP + 0.03), (0.16, 0.12, 0.06),
             FOX_BLACK)
    make_box("DI_TapeLabel", (1.75, 3.78, DECK_TOP + 0.045), (0.10, 0.006, 0.03),
             FOX_TAPE_MASK)
    make_box("DI_Cable", (1.75, 3.30, DECK_TOP + 0.006), (0.03, 1.00, 0.012),
             FOX_BLACK)
    _mic_stand("Mic_Em", 0.0, 2.95, DECK_TOP, pole_h=1.52)
    # Em's mic cord, coiled at the base (she checks it at load-in).
    make_cyl("EmCord_Coil", (0.28, 2.92, DECK_TOP + 0.012), 0.10, 0.022, FOX_BLACK,
             segments=10)


def build_pa_and_lights():
    """The good PA — mains flanking the stage, wedges on the lip —
    and Ramón's two truss towers with the six LED fixtures cycling
    deep blue → deep purple → small magenta (vol6_ch20_bridge)."""
    for si, sx in enumerate([-3.55, 3.55]):
        make_box(f"PA_{si}_Sub", (sx, 2.05, 0.375), (0.62, 0.55, 0.75), FOX_BLACK)
        make_box(f"PA_{si}_Top", (sx, 2.05, 1.10), (0.55, 0.48, 0.70), FOX_BLACK)
        make_box(f"PA_{si}_Horn", (sx, 1.80, 1.22), (0.30, 0.012, 0.12),
                 (0.24, 0.22, 0.20, 1.0))
        make_box(f"PA_{si}_DuctTape", (sx - 0.22, 1.80, 0.55), (0.14, 0.012, 0.10),
                 FOX_TAPE_DUCT)
    for wi, wx in enumerate([-1.2, 1.2]):
        make_box(f"Wedge_{wi}_Body", (wx, 2.72, DECK_TOP + 0.13), (0.50, 0.34, 0.26),
                 FOX_BLACK)
        make_box(f"Wedge_{wi}_Grille", (wx, 2.54, DECK_TOP + 0.13),
                 (0.44, 0.012, 0.18), (0.24, 0.22, 0.20, 1.0))
    # Truss towers at the lip (just clear of the deck front), cans
    # aimed upstage (+Y).
    for ti, tx in enumerate([-2.85, 2.85]):
        make_box(f"Truss_{ti}_Base", (tx, 2.20, 0.025), (0.45, 0.45, 0.05), FOX_STEEL)
        make_cyl(f"Truss_{ti}_Post", (tx, 2.20, 1.475), 0.05, 2.90, FOX_BLACK)
        for ci, (cz, lens) in enumerate([(1.60, FOX_LED_BLUE),
                                          (2.05, FOX_LED_PURPLE),
                                          (2.50, FOX_LED_MAGENTA)]):
            make_box(f"Truss_{ti}_Clamp_{ci}", (tx, 2.27, cz), (0.06, 0.08, 0.06),
                     FOX_STEEL)
            make_cyl(f"Truss_{ti}_Can_{ci}", (tx, 2.41, cz), 0.09, 0.20, FOX_BLACK,
                     axis='Y')
            make_cyl(f"Truss_{ti}_Lens_{ci}", (tx, 2.52, cz), 0.072, 0.02, lens,
                     axis='Y')


def build_foh_floor():
    """The rail the kid headbangs at, the taped floor snake, and the
    small DJ booth at the side of the stage (vol6_ch20/ch22)."""
    for ui, ux in enumerate([-2.4, -1.2, 0.0, 1.2, 2.4]):
        make_box(f"Rail_Foot_{ui}", (ux, 1.55, 0.015), (0.30, 0.30, 0.03), FOX_STEEL)
        make_cyl(f"Rail_Upright_{ui}", (ux, 1.55, 0.55), 0.024, 1.02, FOX_STEEL,
                 segments=8)
    make_cyl("Rail_Top", (0.0, 1.55, 1.06), 0.030, 5.10, FOX_STEEL, axis='X',
             segments=8)
    make_cyl("Rail_Mid", (0.0, 1.55, 0.60), 0.020, 5.10, FOX_STEEL, axis='X',
             segments=8)
    # Floor snake out the S door toward the board in the front room.
    _cable_y("Snake", 0.30, 2.45, 1.9)
    _cable_x("PA_CrossCable", -3.30, 1.90, 0.60)
    # DJ booth at the (east) side of the stage.
    for li, (lx, ly) in enumerate([(3.05, 1.15), (3.70, 1.15), (3.05, 1.60),
                                    (3.70, 1.60)]):
        make_cyl(f"DJ_Leg_{li}", (lx, ly, 0.47), 0.018, 0.94, FOX_STEEL, segments=6)
    make_box("DJ_TableTop", (3.37, 1.37, 0.96), (0.75, 0.52, 0.04), FOX_BLACK)
    make_box("DJ_Laptop_Base", (3.30, 1.30, 0.99), (0.28, 0.20, 0.016),
             (0.22, 0.22, 0.24, 1.0))
    make_box("DJ_Laptop_Screen", (3.30, 1.41, 1.09), (0.26, 0.015, 0.19),
             (0.22, 0.22, 0.24, 1.0))
    make_box("DJ_Crate", (3.37, 1.37, 0.17), (0.36, 0.36, 0.30), FOX_WOOD)


def build_walls_dressing():
    """Backdrop lettering, flyers, and the stage door to the hallway."""
    wall_face = ROOM_D - 0.10
    # FOXHOLE painted behind the kit — same hand-drawn block letters
    # as the flyers (vol6_ch14), cream on a fox-red board.
    make_box("Backdrop_Board", (0.0, wall_face - 0.02, 2.45), (3.40, 0.04, 0.62),
             FOX_RED)
    for li in range(7):
        lx = -1.32 + li * 0.44
        lz = 2.47 + (0.02 if li % 2 == 0 else -0.02)
        make_box(f"Backdrop_Letter_{li}", (lx, wall_face - 0.05, lz),
                 (0.26, 0.02, 0.36), FOX_CREAM)
    # Stage door, west wall, south of the platform — taped label.
    door_x = -(ROOM_W/2.0 - 0.13)
    make_box("StageDoor_Slab", (door_x, 1.40, 1.02), (0.06, 0.95, 2.04),
             (0.20, 0.16, 0.13, 1.0))
    make_cyl("StageDoor_Knob", (door_x + 0.06, 1.05, 1.02), 0.024, 0.05, FOX_STEEL,
             axis='X', segments=8)
    make_box("StageDoor_TapeLabel", (door_x + 0.045, 1.40, 1.72),
             (0.006, 0.32, 0.08), FOX_TAPE_MASK)
    make_box("StageDoor_TapeInk", (door_x + 0.049, 1.40, 1.72),
             (0.004, 0.24, 0.035), FOX_INK)
    # Two old flyers by the stage door (bands who played this room).
    _flyer("Flyer_W0", (-ROOM_W/2.0 + 0.10, 0.65, 1.55), axis='Y', face=+1)
    _flyer("Flyer_W1", (ROOM_W/2.0 - 0.10, 0.80, 1.50), axis='Y', face=-1,
           fresh=True, extra_line=True)
    for i in range(4):
        _sticker("DoorJamb", (-(ROOM_W/2.0 - 0.10),
                              1.98 + (i % 2) * 0.14, 0.8 + i * 0.25),
                 i + 1, axis='Y', face=+1)


def build_ceiling_infra():
    # House lights over the crowd only — the stage runs on Ramón's rig.
    for j, xpos in enumerate([-1.6, 1.6]):
        make_fluorescent_tube_fixture(f"Fluor_{j}", (xpos, 1.10, CEIL),
                                       length=1.20, width=0.30,
                                       palette={"tube": (0.55, 0.50, 0.44, 1.0),
                                                "diffuser": (0.72, 0.58, 0.40, 1.0)})
    make_smoke_detector("Smoke", (0.0, 2.4, CEIL))
    make_hvac_vent("HVAC", (2.6, 1.0, CEIL), width=1.0, depth=0.5)


def main():
    clear_scene()
    build_shell()
    build_stage_platform()
    build_drum_kit()
    build_guitar_side()
    build_bass_side()
    build_pa_and_lights()
    build_foh_floor()
    build_walls_dressing()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/foxhole_stage.glb"))
    print(f"\n[build_foxhole_stage] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
