# HCE · Rough Layout Inventory

Captured 2026-06-15 after the long uninterrupted build session
that populated the district end-to-end.

Status: **Rough-layout phase complete.** Buildings are still
primitive (boxes + simple geometry). Refinement comes later in
waves.

## Settlement zones (defined in `SETTLEMENTS`)

Format: (zone, x range, y range, target z, flatness)

- **CountryClub** (-460..440, 340..420, +22.0, 0.85) — top of
  hill, the most prosperous tier
- **NorthRanch**  (-460..-200, 20..260, +12.0, 0.80) — second
  tier
- **EastCDS**     (180..440, 20..260, +8.0, 0.80) — east ridge
- **Phase2**      (40..240, -260..-100, +1.0, 0.75) — mid tier
- **WestEstates** (-460..-120, -340..-40, -3.0, 0.78) — modest
  lowland
- **Phase3**      (-460..-340, -260..-180, -8.0, 0.70) — Norman
  Lott's abandoned dev
- **HarmonyPark** (-120..180, -40..200, +1.0, 0.55) — central
  park
- **HighSchoolField** (200..480, -130..110, +3.0, 0.88) — school
  + field
- **NexCorpHQPad** (-35..35, 255..335, +14.0, 0.95) — tighter
  pad for HQ
- **NightClubPad** (-530..-490, -22..20, -2.0, 0.95) — SCRATCH
- **OliverTreeMemPark** (-300..-220, 60..180, +2.0, 0.80)
- **OTSkatePark** (-300..-260, 65..100, -0.5, 0.90)
- **KwikShopPad / NexCorpGGPad / DinerPad / CosmicCPad** — tight
  chapter-1 pads
- **NorthComm** (-460..260, 260..340, +14.0, 0.75) — north
  commercial belt
- **EastComm**  (440..540, -340..260, +5.0, 0.80) — east
  commercial strip
- **WestComm**  (-560..-460, -340..260, -2.0, 0.85) — Highway 9
  lowland
- **SouthComm** (-460..440, -400..-340, -9.0, 0.85) — truck
  route + chapter-1

## What's built (population view)

### Residential

- **Phase 2** (south-central) · winding cul-de-sac + bulb · 11
  houses (6 arterial + 5 around the cul-de-sac)
- **West Estates** (south-west) · Magnolia Lane arterial + loop
  branch · 7 houses · plus 6-unit townhouse row at (-260, -100)
- **North Ranch** (north-west) · Aspen / Birch / Cedar parallel
  streets with N-S spur · 18 houses
- **East CDS Estates** (east) · Ridge Crest Dr collector +
  cul-de-sac spur · 12 houses
- **Phase 3** (south-west, ABANDONED) · 2 dilapidated houses +
  2 framed-only slabs + debris pile + STOP CONSTRUCTION sign +
  rusted construction crane

### Civic / institutional

- **Country Club** (0, 370) · clubhouse + portico + 2 tennis
  courts + golf fairway + putting green
- **Harmony Park** (30, 60) · community pool (around
  HarmonyPond) + change rooms + lounge chairs + lifeguard +
  playground (sandbox / swings / slide) + benches + bike racks
- **Elementary School** (-90, 160) · brick building + entry
  doors + classroom windows + flagpole + bike racks +
  playground south of school (climber / slide / monkey bars /
  sand pit / fence)
- **High School** (340, 50) · main brick building + name plaque
  + flagpoles + student lot
- **Football Field** (340, -50) · field + mowing stripes + yard
  lines + end zones + red oval track + HOME + VISIT bleachers +
  goalposts + scoreboard + overflow lot + ticket booths
- **Little League Field** (-150, 200) · diamond + dugouts +
  backstop
- **Library** (60, 80) · brick building + storefront windows +
  sign
- **Church** (-30, 140) · white clapboard + steeple + cross +
  rose window + cemetery beside
- **Cemetery** (-15, 140) · 20 headstones + family monument +
  iron fence + gate arch
- **Fire Station** (-200, -30) · red building + 3 garage bays +
  white stripe + hydrant
- **Police Station** (-170, -60) · navy brick + gold badge +
  flag + 4-cruiser lot
- **Post Office** (180, -30) · grey + USPS blue + red + 2 drop
  boxes + sign stripes
- **Hospital** (180, 300) · 3-story + giant red cross sign +
  ambulance bay + ambulance

### Commercial

- **Chapter-1 cluster** (-90..70, -360) — NexCorp Gas & Go +
  Kwik Shop strip (Arcade + Kwik Stop + Laundromat) + Diner +
  Cosmic Comics — proper 2-row parking lots with cars-in-stalls,
  handicap spaces, awnings, NPCs at counters
- **D'Ambrosio's Holdover** (-150, -360) · dark-wood bar + patio
  tables + hanging sign
- **Truck Stop** (200, -380) · big-rig fuel canopy + repair
  garage + truck lot + pylon
- **East Commercial big-box** (480, 60) · dept store + fast-food
  drive-thru + signage
- **Halsey Studios** (480, -100) · recording studio with big
  plate-glass control booth window + parking
- **NexCorp HQ** (0, 300) · 3-story corporate + glass curtain
  wall + reflecting pool + hedges + flagpoles + visitor lot
- **SCRATCH nightclub** (-510, 0) · windowless + neon sign +
  velvet rope + bouncers + parking
- **Auto dealership** (480, -260) · 16-car inventory lot +
  showroom + pylon
- **Self-storage** (480, -180) · 3 rows of orange roll-up units
- **Mini-mart** (-260, -50) · plate glass + single fuel pump
  under small canopy
- **Horizon Plaza** (-100, 30) · 3-bay strip (Pizza + DryClean +
  Salon) with lot

### Atmosphere / outdoor

- **Drive-in movie theatre** (150, -300) · 32 m screen + 48
  parked cars in concentric arcs + concession stand
- **Water tower** (220, 380) · 22 m steel-leg tower + red beacon
- **Transmission lines** · 3 high-voltage towers crossing south
  HCE w/ wires

### Infrastructure

- **Harmony Boulevard** (N-S arterial) · runs from (0, 340)
  Country Club entry south to (12, -392) chapter-1 commercial
  road · 8 m two-lane with dashed yellow centreline + sidewalks
  + lamps + street trees
- **Horizon Drive** (E-W arterial) · runs from (-460, -20) at
  WestComm east to (440, 0) at EastComm · same treatment
- **5 connector roads** · Phase 2 → Horizon, West Estates →
  Horizon, North Ranch → Harmony Blvd, East CDS → Horizon,
  Country Club → Harmony
- **OT Park access road** · from Horizon Dr north to OT Park
  south entry beacon + visitor parking with 2 HC stalls
- **EastComm collector** · north + south branches from Horizon
  Dr east end touching Halsey, big-box, self-storage, auto
- **WestComm link** · branch from Horizon west end to SCRATCH
- **5 bus stops** · at major arterial intersections
- **Streetlamps + street trees** · alternating along both
  arterials at 25–40 m spacing
- **Arterial sidewalks** · both sides of Harmony Blvd + Horizon
- **Crosswalks + stop signs** · 4 zebras + 10 stop signs at the
  major intersections
- **Street-name signs** · 7 green-and-white plaques at major
  intersections

### Back-alley details

- 12 trash dumpsters behind the chapter-1 cluster + EastComm
  buildings

## Where to look in code

- **Build script:**
  `godot/tools/blender/locales/build_harmony_terrain.py`
  (~7400 lines)
- **Scene + setup:**
  `godot/scenes/locales/harmony_terrain.tscn` +
  `godot/scenes/locales/LocaleSetup.gd`
- **Playbooks:**
  `lore/_3D_MODELING_PLAYBOOK.md` (rules + lessons),
  `lore/_SHADER_VISUALS_PLAYBOOK.md`,
  `lore/_LIGHTING_PLAYBOOK.md`
- **Performance plan (deferred):**
  `lore/_HCE_PERFORMANCE_PLAN.md`
