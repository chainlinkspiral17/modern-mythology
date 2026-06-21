# godot/tools/blender/_props
# ════════════════════════════════════════════════════════════════
# Reusable Blender prop library — shared across all locale builders
# (build_kwik_stop.py, build_cosmic_comics.py, build_gas_and_go.py,
# build_daily_grind.py, future vol7 builders, etc.).
#
# Each module is a CATEGORY of props. All functions take:
#   - `prefix` (str)  — name prefix so multiple instances per scene
#                       don't collide ("KwikStop_Counter" vs
#                       "ElRancho_Counter").
#   - `anchor` (3-tuple) — Blender-frame (x, y, z) anchor point.
#                          Builders compute child positions relative
#                          to this so the same prop can be placed
#                          anywhere in a locale.
#   - `palette` (Dict[str, tuple], optional) — overrides for the
#                          prop's default colors. Lets a single
#                          fixture render in warm sunset for kwik
#                          stop or cool fluorescent for gas & go
#                          without forking the prop function.
#
# Locale builders are PLACEMENT SCRIPTS — they call library
# functions with specific anchors, palettes, and counts. They
# stay short (~100-200 lines) and tell the story of WHERE props
# go in that locale, not HOW each prop is constructed.
#
# Geometry helpers + palette constants live in geometry.py and
# palette.py. Categories that follow:
#   structure.py        — walls, floors, ceilings, doors, windows
#   store_fixtures.py   — counter, register, cig rack, lottery
#   coolers_drinks.py   — cooler doors, slurpee, ice machine, soda
#   food_service.py     — hot case, donut, coffee, pizza warmer
#   shelving.py         — aisles, end-caps, peg boards, OTC display
#   signage.py          — banners, neon, paper notices, pole sign
#   decor.py            — wall clock, calendar, plant, payphone
#   safety.py           — fire ext, cameras, smoke detector, conduit
#   cleaning.py         — broom, mop, wet floor, trash, butt urn
#   exterior.py         — canopy, pumps, vehicles, streetlamp
#
# When adding a new prop, prefer EXTRACTING from an existing locale
# builder rather than authoring from scratch — if it's worth library
# placement it's likely already canonised by an existing layout.
# ════════════════════════════════════════════════════════════════
