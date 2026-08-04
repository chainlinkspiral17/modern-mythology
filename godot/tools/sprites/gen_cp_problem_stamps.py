#!/usr/bin/env python3
"""Generate Community Planned problem-type stamp HeroImages.

Deterministic — byte-identical output on every run. One 96x54 stamp
per problem_type, shown at the top of the dispatch picker and beside
problem rows: the picture of what the agent is being sent into.

Shared idiom: drafting-paper night field, cream ink line work, one
accent family per palette — tan for parish defense, steel for the
County Seat offense types, sickly violet for the demon events.

Output: godot/resources/games/community_planned/stamps/<type>.json
Rendered by HeroImage (estuary_3/HeroImage.gd schema).
"""
import json
import os

W, H = 96, 54
OUT = os.path.join(os.path.dirname(__file__), "..", "..",
                   "resources", "games", "community_planned", "stamps")

# palette shared by every stamp — indices are stable
NIGHT = "#141a22"     # 0 field
PAPER = "#1d2530"     # 1 raised paper / panel
INK = "#d8cfae"       # 2 cream ink
DIM = "#8a8570"       # 3 dim ink
TAN = "#c8a25a"       # 4 defense accent
STEEL = "#7c93a8"     # 5 offense accent
VIOLET = "#8a5aa8"    # 6 demon accent
DARK = "#0c1016"      # 7 deepest shadow
GREEN = "#5a7a52"     # 8 living green
RED = "#b06048"       # 9 alarm ember


class Stamp:
    def __init__(self, sid, notes):
        self.id = sid
        self.notes = notes
        self.palette = [NIGHT, PAPER, INK, DIM, TAN, STEEL, VIOLET,
                        DARK, GREEN, RED]
        self.layers = [{"op": "fill", "color": 0}]

    def add(self, op, **kw):
        d = {"op": op}
        d.update(kw)
        self.layers.append(d)

    def rect(self, x, y, w, h, c):
        self.add("rect", xywh=[x, y, w, h], color=c)

    def hline(self, y, x0, x1, c):
        self.add("hline", y=y, x_range=[x0, x1], color=c)

    def vline(self, x, y0, y1, c):
        self.add("vline", x=x, y_range=[y0, y1], color=c)

    def dot(self, x, y, s, c):
        self.add("dot", xy=[x, y], size=s, color=c)

    def poly(self, pts, c):
        self.add("poly", points=pts, color=c)

    def pline(self, pts, c):
        self.add("polyline", points=pts, color=c)

    def ground(self, y=44, c=3):
        self.hline(y, 4, W - 4, c)

    def doc(self):
        return {"id": self.id, "notes": self.notes, "w": W, "h": H,
                "palette": self.palette, "layers": self.layers}


STAMPS = []


def stamp(sid, notes):
    s = Stamp(sid, notes)
    STAMPS.append(s)
    return s


# ── parish defense ──────────────────────────────────────────────

s = stamp("infrastructure_failing",
          "The water tower with the seam letting go — three drips.")
s.ground()
s.rect(40, 10, 18, 12, 1)               # tank
s.pline([[40, 10], [58, 10], [58, 22], [40, 22], [40, 10]], 2)
s.vline(43, 22, 44, 2)                  # legs
s.vline(55, 22, 44, 2)
s.pline([[43, 30], [55, 36]], 3)        # cross-brace
s.pline([[55, 30], [43, 36]], 3)
s.vline(49, 14, 20, 9)                  # the seam
s.dot(49, 26, 1, 5)                     # drips
s.dot(50, 32, 1, 5)
s.dot(49, 39, 2, 5)
s.add("shade", xywh=[0, 0, W, H], color=7, strength=0.25)

s = stamp("hoa_action",
          "The letterhead clipboard over a row of identical mailboxes.")
s.ground()
for i in range(4):
    x = 12 + i * 20
    s.rect(x, 32, 10, 7, 1)
    s.pline([[x, 32], [x + 10, 32], [x + 10, 39], [x, 39], [x, 32]], 3)
    s.vline(x + 5, 39, 44, 3)
s.rect(30, 6, 36, 20, 1)                # the letter
s.pline([[30, 6], [66, 6], [66, 26], [30, 26], [30, 6]], 2)
s.hline(10, 34, 62, 4)                  # letterhead band
s.hline(15, 34, 58, 3)
s.hline(18, 34, 60, 3)
s.hline(21, 34, 52, 3)

s = stamp("surveillance",
          "The pole camera and its cone of view over the cul-de-sac.")
s.ground()
s.vline(20, 12, 44, 2)                  # pole
s.hline(14, 14, 26, 2)                  # crossarm
s.rect(22, 16, 6, 4, 7)                 # camera housing
s.pline([[22, 16], [28, 16], [28, 20], [22, 20], [22, 16]], 5)
s.poly([[28, 18], [84, 8], [84, 40]], 1)   # view cone
s.pline([[28, 18], [84, 8]], 5)
s.pline([[28, 18], [84, 40]], 5)
s.dot(60, 24, 2, 5)                     # the watched house
s.rect(56, 28, 12, 8, 1)
s.pline([[56, 28], [62, 23], [68, 28]], 2)

s = stamp("memorial_grief",
          "Folding chairs, the flower stand, the easel with the photograph.")
s.ground()
for i in range(3):
    x = 12 + i * 13
    s.pline([[x, 34], [x + 8, 34], [x + 8, 44]], 2)
    s.vline(x, 34, 44, 2)
    s.hline(30, x, x + 8, 3)
s.pline([[62, 44], [68, 24], [74, 44]], 2)   # easel
s.rect(63, 24, 11, 9, 1)
s.pline([[63, 24], [74, 24], [74, 33], [63, 33], [63, 24]], 3)
s.dot(84, 34, 2, 8)                     # flowers
s.dot(87, 32, 2, 8)
s.dot(85, 30, 1, 4)
s.vline(85, 36, 44, 3)

s = stamp("ground_refuses_plant",
          "The bare mound, the wilted stakes, one green ring of refusal.")
s.ground()
s.poly([[30, 44], [48, 36], [66, 44]], 1)   # mound
s.pline([[30, 44], [48, 36], [66, 44]], 3)
for i, x in enumerate([20, 40, 58, 76]):
    top = 30 + (i % 2) * 3
    s.pline([[x, 44], [x + 2, top]], 3)     # leaning stakes
s.dot(48, 40, 6, 0)
s.dot(48, 40, 4, 8)                     # the ring
s.dot(48, 40, 2, 0)

s = stamp("seed_dying",
          "The seedling tray with the rows going brown from one end.")
s.ground()
s.rect(18, 30, 60, 10, 1)
s.pline([[18, 30], [78, 30], [78, 40], [18, 40], [18, 30]], 2)
for i in range(6):
    x = 23 + i * 10
    c = 8 if i < 2 else (3 if i < 4 else 9)
    s.vline(x, 24, 30, c)
    s.dot(x, 23, 1, c)

s = stamp("local_press_exposure",
          "The front page block with the flash burst over it.")
s.ground()
s.rect(28, 10, 32, 28, 1)               # the paper
s.pline([[28, 10], [60, 10], [60, 38], [28, 38], [28, 10]], 2)
s.hline(15, 31, 57, 2)                  # masthead
s.hline(19, 31, 50, 3)
s.rect(31, 22, 12, 10, 3)               # photo block
for y in (24, 27, 30, 33):
    s.hline(y, 46, 57, 3)
s.dot(70, 14, 2, 2)                     # the flash
for dx, dy in ((5, 0), (-5, 0), (0, 5), (0, -5), (4, 4), (-4, -4), (4, -4), (-4, 4)):
    s.pline([[70 + dx // 2, 14 + dy // 2], [70 + dx, 14 + dy]], 4)

s = stamp("lease_and_licensing",
          "The storefront with the notice taped inside the glass.")
s.ground()
s.rect(24, 14, 48, 30, 1)               # storefront
s.pline([[24, 14], [72, 14], [72, 44], [24, 44], [24, 14]], 2)
s.hline(20, 24, 72, 4)                  # awning band
s.rect(30, 24, 18, 14, 7)               # window
s.pline([[30, 24], [48, 24], [48, 38], [30, 38], [30, 24]], 3)
s.rect(36, 27, 8, 9, 2)                 # the taped notice
s.hline(29, 37, 43, 3)
s.hline(31, 37, 42, 3)
s.rect(56, 26, 10, 18, 7)               # door
s.pline([[56, 26], [66, 26], [66, 44]], 3)

s = stamp("model_home_feel",
          "The too-perfect house and its mirrored twin, no windows lit.")
s.ground()
for x0 in (16, 54):
    s.rect(x0, 26, 26, 18, 1)
    s.poly([[x0 - 2, 26], [x0 + 13, 16], [x0 + 28, 26]], 1)
    s.pline([[x0 - 2, 26], [x0 + 13, 16], [x0 + 28, 26]], 2)
    s.pline([[x0, 26], [x0, 44]], 2)
    s.pline([[x0 + 26, 26], [x0 + 26, 44]], 2)
    s.rect(x0 + 4, 30, 6, 5, 7)         # dark windows
    s.rect(x0 + 16, 30, 6, 5, 7)
s.vline(48, 12, 46, 3)                  # the mirror seam

s = stamp("town_meeting_pushback",
          "Raised hands over the chair rows, the lectern holding.")
s.ground()
s.vline(76, 22, 44, 2)                  # lectern
s.rect(72, 18, 10, 6, 1)
s.pline([[72, 18], [82, 18], [82, 24], [72, 24], [72, 18]], 2)
for i in range(4):
    x = 12 + i * 14
    s.hline(38, x, x + 9, 3)            # chair backs
    s.vline(x, 38, 44, 3)
    s.dot(x + 4, 33, 2, 2)              # heads
for x in (16, 44, 58):                  # raised hands
    s.vline(x + 2, 24, 31, 4)
    s.dot(x + 2, 23, 1, 4)

s = stamp("community_meeting",
          "The circle of chairs with the coffee urn — the parish's own room.")
s.ground()
for i, (x, y) in enumerate([(24, 30), (38, 24), (56, 24), (70, 30),
                            (62, 38), (32, 38)]):
    s.dot(x, y, 2, 2 if i % 2 == 0 else 3)
    s.vline(x, y + 3, y + 8, 3)
s.rect(44, 32, 8, 8, 1)                 # the urn table
s.pline([[44, 32], [52, 32], [52, 40], [44, 40], [44, 32]], 4)
s.dot(48, 29, 1, 3)

s = stamp("wake_problem",
          "The covered table, the dishes, the one empty chair.")
s.ground()
s.rect(24, 28, 40, 4, 2)                # table top
s.rect(26, 32, 36, 10, 1)               # cloth fall
s.vline(26, 32, 42, 3)
s.vline(62, 32, 42, 3)
for x in (32, 44, 56):
    s.dot(x, 27, 1, 3)                  # dishes
s.pline([[74, 44], [74, 34], [82, 34], [82, 44]], 2)   # empty chair
s.hline(37, 74, 82, 2)
s.add("shade", xywh=[0, 0, W, H], color=7, strength=0.2)

s = stamp("missing_kid",
          "The flier on the pole — staples, curled corner.")
s.ground()
s.vline(30, 8, 44, 2)                   # pole
s.rect(36, 12, 26, 22, 1)               # flier
s.pline([[36, 12], [62, 12], [62, 34], [36, 34], [36, 12]], 2)
s.rect(43, 15, 12, 9, 3)                # the photo
s.hline(27, 39, 59, 3)
s.hline(30, 39, 55, 3)
s.dot(37, 13, 1, 5)                     # staples
s.dot(61, 13, 1, 5)
s.poly([[62, 34], [58, 34], [62, 30]], 0)   # curled corner
s.pline([[58, 34], [62, 30]], 3)

s = stamp("family_succession",
          "The big gable and the two small ones — one of them dim.")
s.ground()
s.poly([[26, 30], [42, 16], [58, 30]], 1)
s.pline([[26, 30], [42, 16], [58, 30]], 2)
s.rect(28, 30, 28, 14, 1)
s.pline([[28, 30], [28, 44]], 2)
s.pline([[56, 30], [56, 44]], 2)
s.rect(38, 34, 8, 6, 4)                 # lit heart window
s.poly([[8, 38], [15, 32], [22, 38]], 1)     # small gable, lit
s.pline([[8, 38], [15, 32], [22, 38]], 2)
s.dot(15, 40, 1, 4)
s.poly([[64, 38], [71, 32], [78, 38]], 1)    # small gable, dim
s.pline([[64, 38], [71, 32], [78, 38]], 3)
s.dot(71, 40, 1, 7)

s = stamp("diner_threshold",
          "Booth six under the hanging lamp, the door ajar with spill.")
s.ground()
s.vline(48, 6, 14, 3)                   # lamp drop
s.poly([[42, 14], [54, 14], [50, 18], [46, 18]], 4)
s.add("vgrad", y_range=[18, 34], stops=[4, 1, 0])
s.pline([[28, 44], [28, 30], [40, 30], [40, 44]], 2)   # booth backs
s.pline([[56, 44], [56, 30], [68, 30], [68, 44]], 2)
s.hline(36, 28, 68, 3)                  # table line
s.vline(84, 20, 44, 2)                  # door edge
s.poly([[84, 44], [92, 44], [84, 24]], 1)   # light spill
s.pline([[84, 24], [92, 44]], 3)

s = stamp("cathedral_visitor",
          "The nave arch, the tall lit slit, the visitor at the door.")
s.ground()
s.pline([[24, 44], [24, 20], [48, 8], [72, 20], [72, 44]], 2)
s.vline(48, 12, 30, 4)                  # lit window slit
s.dot(48, 12, 1, 4)
s.rect(44, 34, 8, 10, 7)                # doorway
s.pline([[44, 34], [52, 34]], 3)
s.dot(48, 38, 2, 3)                     # the visitor
s.vline(48, 40, 44, 3)
s.add("shade", xywh=[0, 0, W, H], color=7, strength=0.25)

s = stamp("contact_going_dark",
          "The line of streetlights with the far one out.")
s.ground()
for i, x in enumerate((16, 40, 64, 86)):
    s.vline(x, 20, 44, 2 if i < 3 else 3)
    s.hline(20, x - 3, x + 3, 2 if i < 3 else 3)
    if i < 3:
        s.dot(x, 23, 2, 4)
        s.add("shade", xywh=[x - 5, 24, 10, 8], color=4, strength=0.15)
    else:
        s.dot(x, 23, 2, 7)              # the dark one
s.pline([[10, 18], [92, 14]], 3)        # the wire

s = stamp("newsletter_item",
          "The stapled newsletter with the masthead band and the item circled.")
s.ground()
s.rect(30, 8, 36, 32, 1)
s.pline([[30, 8], [66, 8], [66, 40], [30, 40], [30, 8]], 2)
s.hline(12, 33, 63, 4)                  # masthead
s.hline(13, 33, 63, 4)
for y in (18, 21, 24, 30, 33, 36):
    s.hline(y, 33, 63, 3)
s.dot(31, 9, 1, 5)                      # staple
s.pline([[40, 27], [58, 27], [58, 31], [40, 31], [40, 27]], 9)   # circled item

# ── the county seat · offense ───────────────────────────────────

s = stamp("records_request",
          "The file boxes and the microfiche reel — paper as a weapon.")
s.ground()
for i in range(3):
    x = 14 + i * 17
    y = 30 - i * 7
    s.rect(x, y, 15, 9, 1)
    s.pline([[x, y], [x + 15, y], [x + 15, y + 9], [x, y + 9], [x, y]], 5)
    s.hline(y + 3, x + 2, x + 12, 3)
s.dot(74, 30, 6, 1)                     # the reel
s.dot(74, 30, 6, 0)
s.dot(74, 30, 5, 5)
s.dot(74, 30, 2, 7)
s.pline([[80, 30], [90, 30]], 3)        # fed film

s = stamp("filing_deadline",
          "Their motion, our response clock — the late angle.")
s.ground()
s.rect(20, 12, 28, 28, 1)               # the filing
s.pline([[20, 12], [48, 12], [48, 40], [20, 40], [20, 12]], 5)
for y in (17, 20, 23, 26, 29):
    s.hline(y, 23, 45, 3)
s.rect(38, 32, 8, 6, 9)                 # red stamp corner
s.dot(68, 26, 9, 1)                     # the clock
s.dot(68, 26, 9, 0)
s.dot(68, 26, 8, 2)
s.dot(68, 26, 7, 0)
s.pline([[68, 26], [68, 19]], 2)        # hands at 11:55
s.pline([[68, 26], [63, 23]], 2)

s = stamp("countersuit",
          "Two stacks of paper facing off across the bar.")
s.ground()
s.vline(48, 14, 44, 3)                  # the bar
for i in range(3):                      # our stack
    s.rect(14, 34 - i * 6, 22, 5, 1)
    s.pline([[14, 34 - i * 6], [36, 34 - i * 6], [36, 39 - i * 6],
             [14, 39 - i * 6], [14, 34 - i * 6]], 5)
for i in range(2):                      # theirs
    s.rect(60, 34 - i * 6, 22, 5, 1)
    s.pline([[60, 34 - i * 6], [82, 34 - i * 6], [82, 39 - i * 6],
             [60, 39 - i * 6], [60, 34 - i * 6]], 3)
s.hline(16, 40, 56, 2)                  # gavel bar
s.rect(52, 12, 6, 6, 2)

s = stamp("public_comment_period",
          "The podium mic and the sign-in sheet, the room packed politely.")
s.ground()
s.vline(24, 24, 44, 2)                  # podium
s.rect(18, 20, 12, 6, 1)
s.pline([[18, 20], [30, 20], [30, 26], [18, 26], [18, 20]], 5)
s.pline([[24, 20], [24, 14], [27, 12]], 2)   # mic
s.dot(28, 12, 1, 2)
s.rect(40, 26, 16, 12, 1)               # sign-in sheet
s.pline([[40, 26], [56, 26], [56, 38], [40, 38], [40, 26]], 2)
for y in (29, 32, 35):
    s.hline(y, 42, 54, 3)
for i in range(5):                      # the queue
    s.dot(66 + i * 6, 32 + (i % 2), 2, 3)
    s.vline(66 + i * 6, 34 + (i % 2), 40, 3)

s = stamp("registry_pull",
          "Who owns Fairway Meadows LLC — the matryoshka boxes.")
s.ground()
s.rect(18, 10, 60, 32, 1)
s.pline([[18, 10], [78, 10], [78, 42], [18, 42], [18, 10]], 5)
s.rect(26, 15, 44, 22, 0)
s.pline([[26, 15], [70, 15], [70, 37], [26, 37], [26, 15]], 3)
s.rect(34, 20, 28, 12, 1)
s.pline([[34, 20], [62, 20], [62, 32], [34, 32], [34, 20]], 5)
s.dot(48, 26, 2, 9)                     # the name at the center
s.pline([[78, 26], [88, 26]], 2)        # the pull
s.pline([[85, 23], [88, 26], [85, 29]], 2)

# ── the demon events ────────────────────────────────────────────

s = stamp("demon_corruption_event",
          "The clean sine with the violet spike tearing through it.")
s.ground(46)
s.pline([[6, 27], [16, 22], [26, 32], [36, 22], [44, 30]], 2)   # clean carrier
s.pline([[44, 30], [48, 8], [52, 44], [56, 27]], 6)             # the spike
s.pline([[56, 27], [66, 22], [76, 32], [86, 26]], 2)
s.dot(48, 8, 1, 6)
s.dot(52, 44, 1, 6)
s.add("noise", xywh=[42, 6, 16, 40], color=6, density=0.08, seed=7)

s = stamp("turned_demon_active",
          "The sigil half out of its broken binding ring.")
s.ground(46)
s.dot(48, 26, 14, 0)
s.dot(48, 26, 13, 2)                    # the ring
s.dot(48, 26, 11, 0)
s.poly([[44, 10], [60, 18], [48, 26]], 0)    # the break
s.pline([[40, 14], [56, 34]], 6)        # the sigil strokes
s.pline([[56, 18], [44, 38]], 6)
s.vline(48, 12, 40, 6)
s.dot(48, 26, 2, 6)
s.add("noise", xywh=[30, 8, 36, 36], color=6, density=0.05, seed=11)

# ── write ───────────────────────────────────────────────────────

os.makedirs(OUT, exist_ok=True)
for st in STAMPS:
    path = os.path.join(OUT, st.id + ".json")
    with open(path, "w") as fh:
        json.dump(st.doc(), fh, indent=1)
        fh.write("\n")
print("wrote %d stamps to %s" % (len(STAMPS), os.path.normpath(OUT)))
