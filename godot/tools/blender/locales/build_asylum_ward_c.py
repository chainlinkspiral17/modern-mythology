"""XIII · DEATH — Graustark Parish Hospital, Asylum Wing (Ward C).
The older wing in faded green tile. A long corridor with five
patient-room doors on the W wall, two large window bays on the
E wall looking onto the courtyard, a nurses' station midpoint,
broken-paned cupola at the N end. Walpurgisnacht setting.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding
from _props.decor import make_wall_clock, make_faded_poster
from _props.safety import (make_smoke_detector, make_sprinkler,
                            make_fluorescent_tube_fixture, make_security_camera)

PAL = {"wall": (0.62, 0.72, 0.62, 1.0), "baseboard": (0.32, 0.42, 0.30, 1.0)}
COL_FLOOR_TILE = (0.78, 0.82, 0.74, 1.0); COL_FLOOR_SEAM = (0.42, 0.50, 0.42, 1.0)
COL_WALL_TILE_GREEN = (0.52, 0.68, 0.56, 1.0); COL_WALL_GROUT = (0.42, 0.52, 0.42, 1.0)
COL_DOOR = (0.42, 0.36, 0.28, 1.0); COL_DOOR_GLASS = (0.62, 0.74, 0.68, 0.55)
COL_NURSE_DESK = (0.78, 0.78, 0.72, 1.0); COL_FILE_CAB = (0.62, 0.62, 0.58, 1.0)
COL_CHART = (0.92, 0.86, 0.74, 1.0); COL_WHEELCHAIR = (0.62, 0.62, 0.58, 1.0)
COL_GURNEY = (0.86, 0.86, 0.82, 1.0); COL_CUPOLA_GLASS = (0.74, 0.84, 0.86, 0.55)

ROOM_W = 5.0; ROOM_D = 14.0; CEIL = 3.40


def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR_TILE, "seam": COL_FLOOR_SEAM})
    # W wall split by 5 patient-room door openings
    for di in range(5):
        dy = 1.40 + di * 2.40
        # Wall segment between doors
        if di == 0:
            make_wall(f"Wall_W_{di}_a", (-ROOM_W/2.0, 0.70, 0), length=1.40, height=CEIL,
                      axis='Y', palette=PAL, baseboard_face_sign=+1)
        seg_y_start = dy + 0.80
        seg_y_end = (1.40 + (di+1)*2.40 - 0.80) if di < 4 else (ROOM_D - 0.20)
        seg_len = seg_y_end - seg_y_start
        if seg_len > 0.05:
            make_wall(f"Wall_W_{di}_b", (-ROOM_W/2.0, (seg_y_start+seg_y_end)/2.0, 0),
                      length=seg_len, height=CEIL, axis='Y',
                      palette=PAL, baseboard_face_sign=+1)
        # Door
        make_box(f"Door_{di}", (-ROOM_W/2.0 + 0.04, dy, 1.05), (0.08, 1.20, 2.10), COL_DOOR)
        # Small wire-glass window in each door
        make_box(f"Door_Glass_{di}", (-ROOM_W/2.0 + 0.02, dy, 1.60),
                 (0.005, 0.30, 0.40), COL_DOOR_GLASS)
        # Room number plate
        make_box(f"Door_Plate_{di}", (-ROOM_W/2.0 + 0.06, dy-0.70, 2.00),
                 (0.005, 0.20, 0.10), (0.32, 0.42, 0.30, 1.0))
    # E wall — two large window bays + wall segments
    make_wall("Wall_E_S", (+ROOM_W/2.0, 1.40, 0), length=2.40, height=CEIL,
              axis='Y', palette=PAL, baseboard_face_sign=-1)
    make_wall("Wall_E_Mid", (+ROOM_W/2.0, 7.00, 0), length=2.40, height=CEIL,
              axis='Y', palette=PAL, baseboard_face_sign=-1)
    make_wall("Wall_E_N", (+ROOM_W/2.0, 12.60, 0), length=2.40, height=CEIL,
              axis='Y', palette=PAL, baseboard_face_sign=-1)
    # Window bay glass
    for bi, by in enumerate([4.20, 9.80]):
        make_box(f"WindowBay_{bi}_Frame", (+ROOM_W/2.0-0.04, by, 1.60),
                 (0.04, 2.20, 1.40), (0.42, 0.32, 0.22, 1.0))
        make_box(f"WindowBay_{bi}_Glass", (+ROOM_W/2.0-0.06, by, 1.60),
                 (0.005, 2.00, 1.20), COL_CUPOLA_GLASS)
    # N + S end walls
    make_wall("Wall_S", (0.0, 0.0, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL, baseboard_face_sign=+1)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL, baseboard_face_sign=-1)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [("Crown_W",'Y',ROOM_D,-ROOM_W/2.0+0.10,ROOM_D/2.0),
                                    ("Crown_E",'Y',ROOM_D,+ROOM_W/2.0-0.10,ROOM_D/2.0),
                                    ("Crown_N",'X',ROOM_W,0.0,ROOM_D-0.10),
                                    ("Crown_S",'X',ROOM_W,0.0,+0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": COL_WALL_GROUT})
    # Wall-tile band on both long walls (chest height)
    for sgn, wx in [(+1, -ROOM_W/2.0 + 0.06), (-1, +ROOM_W/2.0 - 0.06)]:
        make_box(f"WallTile_{sgn:+d}", (wx, ROOM_D/2.0, 1.10),
                 (0.08, ROOM_D, 1.20), COL_WALL_TILE_GREEN)


def build_nurses_station():
    # Mid-corridor nurses' station — a chest-high counter with desk behind
    ny = 7.00
    make_box("Nurse_Counter_Top", (0.0, ny - 0.40, 1.10), (2.40, 0.60, 0.06), COL_NURSE_DESK)
    make_box("Nurse_Counter_Body", (0.0, ny - 0.40, 0.55), (2.40, 0.60, 1.10), COL_NURSE_DESK)
    # Desk behind (lower)
    make_box("Nurse_Desk", (0.0, ny + 0.40, 0.74), (2.20, 0.60, 0.04), COL_NURSE_DESK)
    # Chart binder + clipboard
    make_box("Chart_Binder", (-0.40, ny - 0.40, 1.16), (0.30, 0.40, 0.04), COL_CHART)
    make_box("Chart_Stack", (+0.40, ny - 0.40, 1.16), (0.30, 0.40, 0.06), COL_CHART)
    # File cabinet to the N
    make_box("FileCab", (-1.00, ny + 0.50, 0.70), (0.50, 0.50, 1.40), COL_FILE_CAB)
    for di in range(3):
        make_box(f"FileCab_Drawer_{di}", (-1.00, ny + 0.26, 0.30 + di*0.46),
                 (0.50, 0.005, 0.40), (0.42, 0.42, 0.40, 1.0))
        make_box(f"FileCab_Handle_{di}", (-1.00, ny + 0.25, 0.30 + di*0.46),
                 (0.10, 0.005, 0.04), (0.62, 0.62, 0.58, 1.0))


def build_gurney_and_wheelchair():
    # An abandoned gurney parked diagonally
    gx, gy = +0.40, 11.00
    make_box("Gurney_Mattress", (gx, gy, 0.74), (0.70, 1.80, 0.10), COL_GURNEY)
    make_box("Gurney_Frame", (gx, gy, 0.62), (0.74, 1.84, 0.10), (0.42, 0.42, 0.42, 1.0))
    # Side rail
    make_box("Gurney_Rail_E", (gx + 0.40, gy, 1.00), (0.04, 1.40, 0.30), (0.62, 0.62, 0.58, 1.0))
    # Wheels
    for sgn_x in (-1, +1):
        for sgn_y in (-1, +1):
            make_cyl(f"Gurney_Wheel_{sgn_x:+d}_{sgn_y:+d}",
                     (gx + sgn_x*0.30, gy + sgn_y*0.80, 0.10), 0.08, 0.06,
                     P.METAL_BLACK, axis='X')
    # Wheelchair near the S end
    wx, wy = -1.20, 1.50
    make_box("WC_Seat", (wx, wy, 0.46), (0.50, 0.50, 0.06), COL_WHEELCHAIR)
    make_box("WC_Back", (wx, wy-0.22, 0.96), (0.50, 0.06, 0.70), COL_WHEELCHAIR)
    for ari, (sgn) in enumerate([-1, +1]):
        make_box(f"WC_Arm_{ari}", (wx+sgn*0.27, wy, 0.66), (0.04, 0.40, 0.20), COL_WHEELCHAIR)
    # Big wheels
    for sgn in (-1, +1):
        make_cyl(f"WC_BigWheel_{sgn:+d}", (wx + sgn*0.30, wy, 0.30), 0.28, 0.04,
                 P.METAL_BLACK, axis='X', segments=14)
    # Small front wheels
    for sgn in (-1, +1):
        make_cyl(f"WC_SmallWheel_{sgn:+d}", (wx + sgn*0.20, wy+0.30, 0.08), 0.08, 0.04,
                 P.METAL_BLACK, axis='X')


def build_cupola():
    # Broken-paned cupola at the N end — a small square skylight
    # tower above the ceiling, visible through a hatch
    cx, cy = 0.0, ROOM_D - 0.80
    make_box("Cupola_Hatch", (cx, cy, CEIL-0.04), (1.80, 1.80, 0.04), (0.10, 0.10, 0.10, 1.0))
    # Cupola tower above
    make_box("Cupola_Walls_N", (cx, cy+0.80, CEIL+0.80), (1.80, 0.10, 1.40), COL_WALL_GROUT)
    make_box("Cupola_Walls_S", (cx, cy-0.80, CEIL+0.80), (1.80, 0.10, 1.40), COL_WALL_GROUT)
    make_box("Cupola_Walls_W", (cx-0.80, cy, CEIL+0.80), (0.10, 1.80, 1.40), COL_WALL_GROUT)
    make_box("Cupola_Walls_E", (cx+0.80, cy, CEIL+0.80), (0.10, 1.80, 1.40), COL_WALL_GROUT)
    # Broken panes — three glass squares, one missing
    panes = [(0.0, +0.85, COL_CUPOLA_GLASS),
             (0.0, -0.85, COL_CUPOLA_GLASS),
             (-0.85, 0.0, COL_CUPOLA_GLASS)]  # E pane missing — Death enters here
    for pi, (px, py, pc) in enumerate(panes):
        make_box(f"Cupola_Pane_{pi}", (cx+px, cy+py, CEIL+0.80),
                 (0.04 if abs(px) > 0.5 else 1.60,
                  0.04 if abs(py) > 0.5 else 1.60,
                  1.20), pc)
    # Cupola peaked roof (low-poly)
    make_box("Cupola_Roof", (cx, cy, CEIL+1.60), (1.80, 1.80, 0.30), (0.32, 0.42, 0.30, 1.0))


def build_ceiling_infra():
    # Fluorescent strip every ~3m down the corridor (some flickering)
    for j, ypos in enumerate([2.0, 5.0, 8.0, 11.0]):
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL),
                                       length=1.40, width=0.32,
                                       palette={"diffuser": (0.86, 0.96, 0.86, 1.0)})
    make_smoke_detector("Smoke_S", (0.0, 3.0, CEIL))
    make_smoke_detector("Smoke_N", (0.0, 10.0, CEIL))
    make_sprinkler("Spr_S", (0.0, 4.0, CEIL))
    make_sprinkler("Spr_N", (0.0, 10.0, CEIL))
    make_security_camera("Cam", (+ROOM_W/2.0-0.10, 7.0, CEIL-0.10))


def build_decor():
    make_wall_clock("Clock", (-ROOM_W/2.0+0.05, 7.0, 2.50), frozen_hour=4, frozen_min=15)
    make_faded_poster("PSA_Notice", (-ROOM_W/2.0+0.05, 12.5, 1.80))


def build_death_dressing():
    """Scene-description specifics from setup_walpurgisnacht.json:
      · "chart binder closed for the first time in three decades"
        at the nurses' station (Pearl's chart binder, closed)
      · "cupola has had a missing pane since the '92 storm" —
        boarded-up gap in the existing cupola
      · A small votive candle Sister Beatrice brought for the
        vigil · on the nurses' station counter
      · A row of empty patient charts on the wall mount (the
        five patients transferred Wednesday — names visible
        but the slots empty)
    """
    # Nurses' station is at roughly (0, 0). Counter top approx z=1.05.
    # The CHART BINDER closed on the counter.
    binder_x = +0.40
    binder_y = -0.10
    binder_z = 1.06
    # Binder body (oxblood leather, three-ring style)
    make_box("ChartBinder_Body",
             (binder_x, binder_y, binder_z + 0.025),
             (0.32, 0.26, 0.05),
             (0.42, 0.20, 0.16, 1.0))
    # Spine label (off-white sticker)
    make_box("ChartBinder_Label",
             (binder_x, binder_y - 0.131, binder_z + 0.025),
             (0.20, 0.001, 0.025),
             (0.92, 0.88, 0.78, 1.0))
    # Three darker lines on the label simulating handwritten "WARD C"
    for li in range(3):
        make_box("ChartBinder_LabelLine_%d" % li,
                 (binder_x - 0.04 + li * 0.04, binder_y - 0.132, binder_z + 0.025),
                 (0.020, 0.0005, 0.012),
                 (0.18, 0.14, 0.10, 1.0))
    # Top edge of pages visible (sliver of cream paper)
    make_box("ChartBinder_PagesEdge",
             (binder_x, binder_y, binder_z + 0.052),
             (0.30, 0.24, 0.002),
             (0.94, 0.90, 0.80, 1.0))

    # Sister Beatrice's votive candle on the counter
    votive_x = -0.10
    votive_y = -0.08
    # Glass jar
    make_cyl("BeatriceVotive_Jar",
             (votive_x, votive_y, binder_z + 0.05),
             0.030, 0.10,
             (0.86, 0.86, 0.92, 0.6),
             segments=10, axis='Z')
    # Wax inside (cream, partial level)
    make_cyl("BeatriceVotive_Wax",
             (votive_x, votive_y, binder_z + 0.025),
             0.026, 0.05,
             (0.92, 0.88, 0.74, 1.0),
             segments=10, axis='Z')
    # Wick
    make_box("BeatriceVotive_Wick",
             (votive_x, votive_y, binder_z + 0.06),
             (0.002, 0.002, 0.020),
             (0.18, 0.14, 0.10, 1.0))
    # Tiny flame above (warm amber)
    make_box("BeatriceVotive_Flame",
             (votive_x, votive_y, binder_z + 0.085),
             (0.008, 0.008, 0.022),
             (0.96, 0.74, 0.32, 1.0))

    # Row of empty patient charts on the wall mount behind the
    # station — five wall pockets, names visible, the actual chart
    # papers missing (the five patients were transferred Wednesday)
    wall_mount_y = +0.80   # behind the station, against the back wall
    wall_mount_z = 1.40
    for ci in range(5):
        cx = -0.80 + ci * 0.30
        # Pocket frame
        make_box("ChartPocket_%d_Frame" % ci,
                 (cx, wall_mount_y, wall_mount_z),
                 (0.22, 0.04, 0.30),
                 (0.62, 0.62, 0.58, 1.0))
        # Name plate at the top (cream sticker with a dark name line)
        make_box("ChartPocket_%d_NamePlate" % ci,
                 (cx, wall_mount_y - 0.022, wall_mount_z + 0.12),
                 (0.18, 0.005, 0.04),
                 (0.92, 0.88, 0.78, 1.0))
        make_box("ChartPocket_%d_NameLine" % ci,
                 (cx, wall_mount_y - 0.024, wall_mount_z + 0.12),
                 (0.14, 0.001, 0.012),
                 (0.20, 0.18, 0.16, 1.0))
        # Empty slot below (a darker recess where the chart used to be)
        make_box("ChartPocket_%d_EmptySlot" % ci,
                 (cx, wall_mount_y - 0.022, wall_mount_z - 0.06),
                 (0.18, 0.005, 0.18),
                 (0.18, 0.20, 0.18, 1.0))

    # The missing cupola pane — find the cupola geometry's center,
    # add a boarded-up gap (a darker rectangle + two horizontal
    # cross-board planks)
    # build_cupola() built the cupola at some location; without
    # cracking its code we approximate via standard ward dims —
    # cupola at (0, 0, ceiling_z+1.0) facing south.
    cup_cz = 4.20   # approximate cupola pane height
    cup_y = +0.0
    # Boarded gap on the SE pane of the cupola
    make_box("Cupola_MissingPane_Board",
             (+0.80, cup_y - 0.74, cup_cz),
             (0.05, 0.04, 0.60),
             (0.16, 0.14, 0.10, 1.0))   # dark void where pane is missing
    # Two horizontal boards nailed across the gap
    for bi in range(2):
        make_box("Cupola_MissingPane_Board_H_%d" % bi,
                 (+0.80, cup_y - 0.76, cup_cz + 0.10 - bi * 0.20),
                 (0.05, 0.05, 0.04),
                 (0.42, 0.30, 0.20, 1.0))   # boards
    # Wind-streak from the gap (a thin diagonal of dust/light below)
    make_box("Cupola_WindStreak",
             (+0.65, cup_y - 0.50, cup_cz - 0.40),
             (0.36, 0.04, 0.04),
             (0.62, 0.62, 0.62, 0.4))


def main():
    clear_scene()
    build_shell()
    build_nurses_station()
    build_gurney_and_wheelchair()
    build_cupola()
    build_ceiling_infra()
    build_decor()
    build_death_dressing()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "../../../assets/3d/locales/asylum_ward_c.glb"))
    print(f"\n[build_asylum_ward_c] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
