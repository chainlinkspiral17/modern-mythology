"""tulsa_house — vol 3's "safari": Marty and Kathy's house in Tulsa, a party
night in the fall, mid-eighties (draft 1, 2026-10-18).

The user: "go ahead and start working on backgrounds for vol 1-4 as needed."
Scene sub "Tulsa, mid-eighties"; the slides' safari is "seventy-five" (the
slides' year, not the room's). Nothing in the room is later than the
mid-eighties: no screens but the slide screen.
  the slide show: "the projector with its dim bulb, its strange disembodied
   yet tethered outlet control wand"; "the pull down screen"; "At the bar
   his wife would have bottles of wine ready to pour"; old ports, "Dozens
   of cases acquired in travels"; "the hum of the projector alive, its
   empty contents illuminating in the air minute threads and particulate
   without rest"; Marty "beside the screen", "right hand casting shadow";
   "These slides have been in that spindle for years"; the children "ahide
   behind the bar"                          → tulsa_slideshow
  the patio, "Much later on": "the children's sawdust playground"; "The
   moon is there between tall skinny trees"; "the wooden fort Marty built
   for the children", inside "a play kitchen for his daughter, the faux
   sink thick with red dirt and twig"      → tulsa_patio
People (Marty, Kathy, the guests, the collie) are the VN's sprites, not set.

Blender: x east, y north, z up; Godot (x, z, -y). The living room x -6..6,
y 0..9 (the screen on the N wall); the patio and the yard run east.

DRAFT 2 targets: the slide on the screen as a real image (the open safari
car with bars); the beam's dust as a volumetric pass; the guests' chairs
filled by sprites' marks; the kitchen through the arch; Deck framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_chamfer_box, make_rot_box, make_blob, make_lathe,
                             join_stock, export_glb)
from _props.structure import make_floor, make_wall, make_wall_with_openings, make_window, make_curtains
from _props.furniture import make_chair, make_table

H, T = 3.0, 0.20
PANEL = (0.46, 0.32, 0.22, 1.0); PANEL_SEAM = (0.36, 0.24, 0.16, 1.0)
PAL = {"wall": (0.80, 0.74, 0.62, 1.0), "baseboard": (0.40, 0.28, 0.20, 1.0)}
CARPET = (0.56, 0.44, 0.30, 1.0); CARPET_SEAM = (0.50, 0.40, 0.28, 1.0)
BRASS = (0.78, 0.64, 0.34, 1.0); PLAID = (0.50, 0.34, 0.24, 1.0)
SAWDUST = (0.76, 0.62, 0.44, 1.0)
SHOW, PATIO = "__tulsa_slideshow", "__tulsa_patio"


def build_room():
    make_floor("Living_Floor", (0.0, 4.5, 0.0), size_x=12.0, size_y=9.0, palette={"vinyl": CARPET, "seam": CARPET_SEAM})
    make_box("Living_Ceil", (0.0, 4.5, H + 0.04), (12.4, 9.4, 0.08), (0.86, 0.82, 0.74, 1.0))
    for k in range(5):
        make_box(f"Ceil_Beam_{k}", (-4.8 + k * 2.4, 4.5, H - 0.10), (0.18, 9.0, 0.20), PANEL)
    make_wall("Wall_N", (0.0, 9.0, 0), length=12.4, height=H, thickness=T, axis='X', palette=PAL, baseboard_face_sign=-1)
    make_wall_with_openings("Wall_S", (0.0, 0.0, 0), length=12.4, height=H, thickness=T, axis='X', palette=PAL,
                            baseboard_face_sign=+1, openings=[(-2.0, 1.15, 2.2, 2.3)])
    # (2026-10-22, the Deck: "interiors need more windows") two windows in the
    # panelled W wall, their drapes drawn nearly shut for the show — a
    # sliver of the night yard between the panels
    WIN_W = [(2.4, 1.45, 1.60, 1.30), (6.6, 1.45, 1.60, 1.30)]
    make_wall_with_openings("Wall_W", (-6.0, 4.5, 0), length=9.0, height=H, thickness=T, axis='Y', palette=PAL,
                            baseboard_face_sign=+1, openings=WIN_W)
    for k, (wy, wz, ww, wh) in enumerate(WIN_W):
        anchor = (-6.0 + T / 2.0, wy, wz)
        make_window(f"Win_W_{k}", anchor, width=ww - 0.12, height=wh - 0.10, axis='Y', room_dir=+1, see_through=True,
                    palette={"frame": (0.30, 0.24, 0.18, 1.0), "casing": PANEL_SEAM})
        make_curtains(f"Win_W_{k}_Drape", anchor, width=ww - 0.12, height=wh - 0.10, axis='Y', room_dir=+1,
                      color=(0.60, 0.46, 0.28, 1.0), open_frac=0.46, drop=0.25, rod_col=BRASS)
    # the side yard past them: a privet hedge and the neighbour's fence
    make_box("W_Yard_Lawn", (-9.0, 4.5, -0.02), (6.0, 14.0, 0.04), (0.18, 0.24, 0.14, 1.0))
    make_box("W_Yard_Fence", (-11.6, 4.5, 0.9), (0.06, 14.0, 1.8), (0.34, 0.28, 0.22, 1.0))
    for k in range(6):
        make_blob(f"W_Yard_Privet_{k}", (-10.6, 0.5 + k * 1.6, 0.74), 0.85, (0.16, 0.24, 0.14, 1.0), noise=0.25, seed=30 + k, squash=0.9)
    make_wall_with_openings("Wall_E", (6.0, 4.5, 0), length=9.0, height=H, thickness=T, axis='Y', palette=PAL,
                            baseboard_face_sign=-1, openings=[(4.5, 1.1, 3.0, 2.2)])
    # wood panelling, board on board, on the W and S walls
    for k in range(12):
        py_ = 0.4 + k * 0.72
        col = (PANEL, PANEL_SEAM)[k % 2]
        if any(abs(py_ - wy) < ww / 2.0 + 0.35 for wy, _, ww, _ in WIN_W):
            # under and over the window: the boards stop at its casing
            make_box(f"Panel_W_{k}_Lo", (-5.9 + 0.01, py_, 0.335), (0.02, 0.70, 0.67), col)
            make_box(f"Panel_W_{k}_Hi", (-5.9 + 0.01, py_, 2.29), (0.02, 0.70, 0.22), col)
            continue
        make_box(f"Panel_W_{k}", (-5.9 + 0.01, py_, 1.2), (0.02, 0.70, 2.4), col)
    for k in range(15):
        x = -5.5 + k * 0.76
        if -3.1 < x < -0.9:
            continue                        # the arch to the hall
        make_box(f"Panel_S_{k}", (x, 0.11, 1.2), (0.74, 0.02, 2.4), (PANEL, PANEL_SEAM)[k % 2])
    make_box("Panel_Chair_Rail_W", (-5.88, 4.5, 2.42), (0.04, 8.8, 0.06), PANEL_SEAM)
    # the patio doors on the E wall, the drapes drawn for the show
    for s in (-1, 1):
        make_box(f"Patio_Door_Frame_Jamb_{s:+d}", (6.0, 4.5 + s * 1.47, 1.1), (T + 0.02, 0.06, 2.2), (0.30, 0.24, 0.18, 1.0))
    make_box("Patio_Door_Frame_Head", (6.0, 4.5, 2.17), (T + 0.02, 3.0, 0.06), (0.30, 0.24, 0.18, 1.0))
    make_box("Patio_Door_Frame_Mullion", (6.0, 4.5, 1.1), (T + 0.02, 0.05, 2.1), (0.30, 0.24, 0.18, 1.0))
    make_box("Drape_Rod_Mounted", (5.88, 4.5, 2.42), (0.04, 3.6, 0.04), BRASS)
    for k in range(6):
        y = 2.9 + k * 0.56 + (0.0 if k < 3 else 0.6)
        make_rot_box(f"Drape_Curtain_{k}" + SHOW, (5.82, y, 1.2), (0.06, 0.52, 2.4), (0.60, 0.46, 0.28, 1.0), yaw=((k % 2) - 0.5) * 0.3)
    for k in range(2):
        make_box(f"Drape_Curtain_Open_{k}" + PATIO, (5.82, 2.9 + k * 3.2, 1.2), (0.10, 0.36, 2.4), (0.60, 0.46, 0.28, 1.0))


def build_show():
    # the pull-down screen, down from its case for the night
    make_box("Screen_Case_Mounted", (0.0, 8.84, 2.78), (2.6, 0.14, 0.14), (0.20, 0.20, 0.22, 1.0))
    make_box("Screen_Sheet", (0.0, 8.86, 1.86), (2.40, 0.012, 1.70), (0.94, 0.94, 0.92, 1.0))
    make_box("Screen_Pull_Bar", (0.0, 8.84, 0.99), (2.44, 0.04, 0.04), (0.20, 0.20, 0.22, 1.0))
    # the slide on it: a hot plain, a long open car with bars, a sky
    make_box("Slide_Image_Sky" + SHOW, (0.0, 8.85, 2.30), (2.24, 0.004, 0.70), (0.86, 0.80, 0.62, 1.0))
    make_box("Slide_Image_Plain" + SHOW, (0.0, 8.85, 1.56), (2.24, 0.004, 0.82), (0.74, 0.60, 0.36, 1.0))
    make_box("Slide_Image_Car" + SHOW, (0.2, 8.848, 1.64), (0.90, 0.004, 0.26), (0.30, 0.30, 0.22, 1.0))
    for k in range(5):
        make_box(f"Slide_Image_Bar_{k}" + SHOW, (-0.18 + k * 0.19, 8.847, 1.86), (0.02, 0.004, 0.22), (0.20, 0.20, 0.16, 1.0))
    make_box("Slide_Image_Acacia" + SHOW, (-0.75, 8.848, 1.96), (0.42, 0.004, 0.10), (0.30, 0.34, 0.20, 1.0))
    make_box("Slide_Image_Hand_Shadow" + SHOW, (0.95, 8.847, 1.70), (0.16, 0.004, 0.30), (0.40, 0.36, 0.30, 1.0))
    # the projector on its stand among the guests, the spindle, the wand
    px, py = 0.0, 2.8
    make_table("Projector_Stand", px, py, w=0.50, d=0.50, h=0.72, wood=(0.36, 0.26, 0.18, 1.0))
    make_chamfer_box("Projector_Body", (px, py, 0.83), (0.30, 0.40, 0.20), (0.62, 0.60, 0.56, 1.0), chamfer=0.03)
    make_cyl("Projector_Lens", (px, py + 0.25, 0.85), 0.04, 0.12, (0.10, 0.10, 0.10, 1.0), axis='Y', segments=12)
    make_cyl("Projector_Spindle_Tray", (px, py - 0.02, 0.96), 0.15, 0.04, (0.22, 0.22, 0.24, 1.0), segments=20)
    make_cyl("Projector_Lens_Glow", (px, py + 0.315, 0.85), 0.03, 0.01, (1.0, 0.96, 0.84, 1.0), axis='Y', segments=12)
    make_box("Projector_Wand_Cord", (px + 0.10, py - 0.16, 0.725), (0.10, 0.01, 0.01), (0.10, 0.10, 0.10, 1.0))
    make_box("Projector_Wand", (px + 0.18, py - 0.18, 0.735), (0.06, 0.14, 0.03), (0.18, 0.18, 0.18, 1.0))
    # the dust in the beam, threads and particulate (non-solid motes)
    for k in range(24):
        t = (k + 0.5) / 24.0
        y = py + 0.4 + t * (8.8 - py - 0.4)
        spread = 0.04 + t * 0.7
        make_blob(f"Beam_Dust_Mote_{k}" + SHOW, (px + ((k * 7) % 5 - 2) * spread * 0.4, y, 0.86 + t * 1.0 + ((k * 3) % 5 - 2) * spread * 0.3),
                  0.008, (1.0, 0.96, 0.86, 1.0), noise=0.0, seed=k, squash=1.0)
    # the guests' seats: the plaid sofa, two chairs, the coffee table
    make_box("Sofa_Base", (0.0, 1.0, 0.24), (2.4, 0.90, 0.48), PLAID)
    make_box("Sofa_Back", (0.0, 0.62, 0.70), (2.4, 0.16, 0.50), PLAID)
    for s in (-1, 1):
        make_box(f"Sofa_Arm_{s:+d}", (s * 1.14, 1.0, 0.56), (0.14, 0.90, 0.20), PLAID)
    make_box("Coffee_Table_Glass_Top", (0.0, 1.9, 0.42), (1.2, 0.60, 0.02), (0.60, 0.66, 0.66, 1.0))
    for s in (-1, 1):
        make_box(f"Coffee_Table_Brass_Leg_{s:+d}", (s * 0.56, 1.9, 0.205), (0.04, 0.56, 0.41), BRASS)
    for k, (x, y, yaw) in enumerate(((3.2, 2.2, math.pi * 0.85), (-2.8, 2.6, -math.pi * 0.85), (3.4, 4.6, math.pi * 0.6))):
        make_chair(f"Guest_Chair_{k}", x, y, yaw=yaw, wood=(0.40, 0.30, 0.22, 1.0), seat_col=(0.62, 0.50, 0.30, 1.0))
    make_box("Glass_Wine_On_Table", (0.3, 1.8, 0.48), (0.06, 0.06, 0.10), (0.50, 0.10, 0.16, 1.0))
    make_box("Slide_Box", (-0.3, 1.95, 0.45), (0.20, 0.14, 0.04), (0.80, 0.70, 0.30, 1.0))
    # the bar on the W wall: the structural counter, the bottles, the ports
    bx = -6.0 + 0.10 + 1.6
    make_box("Bar_Counter", (bx, 4.6, 0.55), (0.60, 3.6, 1.10), (0.36, 0.24, 0.16, 1.0))
    make_box("Bar_Counter_Top", (bx, 4.6, 1.12), (0.70, 3.7, 0.04), (0.20, 0.14, 0.10, 1.0))
    make_box("Bar_Return", (bx - 0.75, 2.6, 0.55), (0.90, 0.50, 1.10), (0.36, 0.24, 0.16, 1.0))
    make_box("Bar_Return_Top", (bx - 0.75, 2.6, 1.12), (0.96, 0.56, 0.04), (0.20, 0.14, 0.10, 1.0))
    make_box("Bar_Foot_Rail_Mounted", (bx + 0.32, 4.6, 0.20), (0.04, 3.4, 0.04), BRASS)
    for k in range(3):
        make_cyl(f"Bar_Foot_Rail_Post_{k}", (bx + 0.32, 3.1 + k * 1.5, 0.09), 0.015, 0.18, BRASS, segments=6)
    for lvl in range(3):
        make_box(f"Bar_Back_Shelf_{lvl}", (-5.9 + 0.16, 4.6, 1.30 + lvl * 0.42), (0.30, 3.2, 0.03), (0.30, 0.20, 0.14, 1.0))
        for k in range(10):
            col = ((0.20, 0.06, 0.08, 1.0), (0.30, 0.30, 0.12, 1.0), (0.40, 0.20, 0.10, 1.0))[(k + lvl) % 3]
            make_lathe(f"Bar_Bottle_{lvl}_{k}", (-5.9 + 0.16, 3.2 + k * 0.30, 1.315 + lvl * 0.42),
                       [(0.0, 0.0), (0.04, 0.0), (0.04, 0.20), (0.015, 0.26), (0.015, 0.32), (0.0, 0.32)], col, segments=8)
    make_box("Bar_Back_Mirror_Mounted", (-5.9 + 0.01, 4.6, 2.40), (0.02, 3.0, 0.50), (0.60, 0.64, 0.64, 1.0))
    for k in range(4):
        make_lathe(f"Bar_Wine_Ready_{k}", (bx, 3.4 + k * 0.30, 1.14), [(0.0, 0.0), (0.04, 0.0), (0.04, 0.22), (0.014, 0.28),
                                                                   (0.014, 0.34), (0.0, 0.34)], (0.24, 0.06, 0.08, 1.0), segments=8)
    for k in range(3):
        make_box(f"Port_Case_{k}", (bx - 0.10, 6.9 + k * 0.10, 0.17 + k * 0.34), (0.50, 0.36, 0.34), (0.66, 0.54, 0.36, 1.0))
    make_box("Bar_Stool_Seat", (bx + 0.70, 5.4, 0.74), (0.36, 0.36, 0.06), (0.30, 0.20, 0.14, 1.0))
    make_cyl("Bar_Stool_Post", (bx + 0.70, 5.4, 0.355), 0.03, 0.71, BRASS, segments=8)
    make_cyl("Bar_Stool_Foot", (bx + 0.70, 5.4, 0.01), 0.20, 0.02, BRASS, segments=12)
    # Marty's cameras and the bag of lenses, set down on the bar's end
    for k in range(3):
        make_chamfer_box(f"Minolta_Camera_{k}", (bx, 6.0 + k * 0.18, 1.18), (0.14, 0.09, 0.09), (0.12, 0.12, 0.12, 1.0), chamfer=0.015)
    make_blob("Burlap_Lens_Bag", (bx + 0.05, 2.9, 1.24), 0.12, (0.62, 0.52, 0.36, 1.0), noise=0.25, seed=5, squash=0.8)
    # the lamp left on low at the room's far corner
    make_cyl("Floor_Lamp_Pole", (5.4, 8.4, 0.80), 0.02, 1.60, BRASS, segments=8)
    make_cyl("Floor_Lamp_Base", (5.4, 8.4, 0.015), 0.16, 0.03, BRASS, segments=12)
    make_lathe("Floor_Lamp_Shade_Glow", (5.4, 8.4, 1.50), [(0.18, 0.0), (0.12, 0.26), (0.0, 0.26)], (0.96, 0.84, 0.60, 1.0), segments=12)


def build_yard():
    # the patio slab, the yard, the sawdust playground, the fort, the trees
    make_box("Patio_Slab", (8.6, 4.5, -0.04), (5.0, 9.0, 0.10), (0.62, 0.58, 0.52, 1.0))
    for k in range(5):
        make_box(f"Patio_Seam_{k}", (6.6 + k * 1.0, 4.5, 0.012), (0.02, 9.0, 0.004), (0.50, 0.48, 0.44, 1.0))
    make_box("Back_Yard_Lawn", (26.0, 4.5, -0.07), (30.0, 60.0, 0.06), (0.28, 0.32, 0.20, 1.0))
    make_box("Side_Yard_Lawn_W", (-12.6, 4.5, -0.07), (13.0, 60.0, 0.06), (0.28, 0.32, 0.20, 1.0))
    make_box("Sawdust_Playground_Ground", (17.0, 4.5, -0.02), (10.0, 12.0, 0.04), SAWDUST)
    for k in range(4):
        make_box(f"Sawdust_Border_Timber_{k}", (17.0 + (0, 0, -5.06, 5.06)[k], 4.5 + (-6.06, 6.06, 0, 0)[k], 0.06),
                 ((10.2, 10.2, 0.12, 0.12)[k], (0.12, 0.12, 12.0, 12.0)[k], 0.12), (0.46, 0.34, 0.22, 1.0))
    # the wooden fort on posts, its ladder, the opening, the play kitchen
    fx, fy, fz = 19.6, 7.4, 1.2
    wood = (0.56, 0.42, 0.28, 1.0)
    for s in (-1, 1):
        for t in (-1, 1):
            make_box(f"Fort_Post_{s:+d}{t:+d}", (fx + s * 1.1, fy + t * 1.1, (fz + 2.0) / 2.0), (0.12, 0.12, fz + 2.0), (0.48, 0.36, 0.24, 1.0))
    make_box("Fort_Deck", (fx, fy, fz), (2.4, 2.4, 0.08), wood)
    make_box("Fort_Wall_N", (fx, fy + 1.16, fz + 0.60), (2.32, 0.06, 1.12), wood)
    make_box("Fort_Wall_E", (fx + 1.16, fy, fz + 0.60), (0.06, 2.20, 1.12), wood)
    make_box("Fort_Wall_S", (fx, fy - 1.16, fz + 0.60), (2.32, 0.06, 1.12), wood)
    make_box("Fort_Wall_W_Low", (fx - 1.16, fy + 0.70, fz + 0.60), (0.06, 0.80, 1.12), wood)
    make_box("Fort_Wall_W_Low_S", (fx - 1.16, fy - 0.70, fz + 0.60), (0.06, 0.80, 1.12), wood)
    make_rot_box("Fort_Roof_N", (fx, fy + 0.62, fz + 1.50), (2.6, 1.40, 0.06), (0.40, 0.30, 0.20, 1.0), roll=0.55)
    make_rot_box("Fort_Roof_S", (fx, fy - 0.62, fz + 1.50), (2.6, 1.40, 0.06), (0.40, 0.30, 0.20, 1.0), roll=-0.55)
    for k in range(5):
        make_box(f"Fort_Ladder_Rung_{k}", (fx - 1.6, fy, 0.24 + k * 0.24), (0.04, 0.50, 0.04), (0.48, 0.36, 0.24, 1.0))
    for s in (-1, 1):
        make_rot_box(f"Fort_Ladder_Rail_{s:+d}", (fx - 1.42, fy + s * 0.26, 0.62), (0.06, 0.06, 1.30), (0.48, 0.36, 0.24, 1.0), pitch=0.30)
    make_box("Play_Kitchen_Unit", (fx + 0.6, fy + 0.6, fz + 0.30), (0.70, 0.50, 0.52), (0.92, 0.88, 0.80, 1.0))
    make_box("Play_Kitchen_Sink_Dirt", (fx + 0.6, fy + 0.6, fz + 0.565), (0.30, 0.24, 0.01), (0.56, 0.24, 0.14, 1.0))
    for k in range(4):
        make_rot_box(f"Play_Sink_Twig_{k}", (fx + 0.56 + k * 0.03, fy + 0.6, fz + 0.575), (0.20, 0.008, 0.008), (0.36, 0.26, 0.18, 1.0), yaw=k * 0.7)
    # tall skinny trees round the yard, the moon between them
    for k in range(9):
        x, y = 27.0 + (k % 3) * 1.6, -4.0 + k * 2.2
        h = 12.0 + (k % 4) * 1.5
        make_cyl(f"Skinny_Tree_Trunk_{k}", (x, y, h / 2.0), 0.14, h, (0.30, 0.24, 0.20, 1.0), segments=8)
        make_blob(f"Skinny_Tree_Crown_{k}", (x, y, h - 1.4), 1.1, (0.18, 0.22, 0.16, 1.0), noise=0.35, seed=70 + k, squash=2.2)
    make_box("Back_Fence", (34.0, 4.5, 0.75), (0.06, 30.0, 1.5), (0.40, 0.32, 0.24, 1.0))
    make_blob("Sky_Moon_Disc" + PATIO, (150.0, 5.0, 19.0), 3.4, (0.96, 0.96, 0.88, 1.0), noise=0.0, seed=3, squash=1.0)
    make_box("Sky_Night_E" + PATIO, (170.0, 4.5, 60.0), (0.2, 900.0, 200.0), (0.04, 0.05, 0.10, 1.0))
    make_box("Far_Hill_Band", (120.0, 4.5, 4.0), (0.2, 600.0, 8.0), (0.06, 0.07, 0.08, 1.0))


def main():
    clear_scene()
    build_room()
    build_show()
    build_yard()
    try:
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/tulsa_house.glb"))
    print(f"\n[build_tulsa_house] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
