# Tarot Gauntlet · Build Wiki

A digestion of the canonical mythology as it touches the Tarot Gauntlet
build. Working reference for keeping the gauntlet aligned to canon as it
gets rebuilt and extended. Updated as new lore lands.

Sources read for this synthesis:
- `_README.md`, `_COMPASS.md`, `_TAROT_LORE.md`
- `_TAROT_GAUNTLET.md`, `_TAROT_GAUNTLET_SCENARIOS.md`
- `_POMEGRANATE_HOUR.md` (full) and the 22 episode scripts in `pomegranate_hour/`
- `_DAMBROSIO_FAMILY.md`, `_DAMBROSIO_EMPLOYEES.md`
- `_SINKHOLE_NEXUS.md`
- `_UNLOCK_WEB.md` (skim)
- `pomegranate_hour/07_chariot.md` (full episode script)
- Plus the chapter VII narrative prose pasted in conversation (Antonio at Ember & Ash)

---

## The shape of vol 5

Vol 5 has 22 chapters — one per Major Arcana, ch0 through ch21. The
diegetic action moves between Graustark (the home town), New Orleans
(Antonio's restaurant), and other locations going forward. The
**sinkhole** is the central event the deck orbits — it happened off-page
in Graustark, swallowed much of it, and every chapter carries the echo.

Each arcana stacks three layers:
1. **The volume chapter** — narrative prose with a focal character
2. **The Pomegranate Hour episode** — Elicia's 22-episode Lynch-tonal
   web series, all drafted, uploaded to VEIL.tv between vol3 and vol5
3. **The Tarot Gauntlet artifact** — playable card-and-dice scenario

The gauntlet is a `HAND × LOCATION × SCENARIO` mix-and-match, derived
from Final Girl's chrome. Each major arcana provides a *hand* (its
character's upright reading + action cards) and a *location* (its
reversed reading + destiny deck + finales). Three scenario cards per
location.

---

## The D'Ambrosio family tree (canonical)

```
                          DANTE D'AMBROSIO
                          (IV THE EMPEROR)
                                 │
                          [void mother]
                          (unrendered; lost at the sinkhole)
                                 │
                    ┌────────────┴────────────┐
                  ANTONIO                   ALBERTO MARROQUÍN-D'AMBROSIO
                  (VII THE CHARIOT)         (X THE WHEEL OF FORTUNE)
                  the_charioteer            carries his mother's surname
                  elder son                 younger son
                  sysop of ember.ash.rest.bbs    the surviving brother
                  dies in scaffolding fall  the call-log keeper
                  Sunday morning            dialed Daigle 19× in 14m
                                              the night his brother died
```

**Antonio's partner is NICOLA (III THE EMPRESS).** The Nicola/Dante
lattice that the earlier deck pre-builds reads as succession-by-marriage,
not romance.

**John Frank** (0 THE FOOL) — runs D'Ambrosio's diner in Graustark. The
diner is the family business. Relation to Dante: not yet specified in
canon. Could be Dante's brother (Antonio's uncle), but the deck reserves
specifics.

**The void mother** is a structural absence. She is unrendered. Her name
is reserved. She was lost at the sinkhole. Her family is named only by
Alberto's surname (Marroquín).

---

## The sinkhole — the Nexus

A specific day, a specific place, in Graustark. Ground opened. People
fell or died. Property destroyed. The deck refuses to date it; every
character calls it "years ago." The deck reserves the date so vol6 / vol7
can fix it.

**Lives lost** (structurally unrendered):
- The void mother (Dante's wife, mother of Antonio + Alberto)
- Anna's father (Marta Romero's husband; died doing boat work for Dante)
- Daigle's father (the original bar destroyed; insurance claim + small
  piece of land became the new bar)
- Probably 6-10 others, vol6 hook

**Lives changed** (the working register):
- Frasier survived; came out painting workers as cosmic beings
- Elicia worked the D'Ambrosio archive at the time; her records are the
  closest the family has to a reckoning; she left the records office
- Antonio took on family management at 18 or 19; Alberto was 14 or 15
- The un-named woman (VIII Strength / IX Hermit / XVII Star) was a
  rescuer; pulled some out; not enough
- Father Quent officiated the mass memorial; has been the family's
  quiet handler of grief ever since
- Daigle inherited the insurance claim; built the new bar over a
  different, smaller sinkhole; tracks the settling with a level
- The Hermit (Dante's brother, or family lawyer) handled paperwork;
  packed a lantern and left
- The render farm (XVI Tower) sits on the sinkhole site's edge —
  engineering instability mirrors geological instability
- The PetroTex case (XI Justice) is the contracting entity at the
  sinkhole site; case is partly Anna recovering her father

**The sinkhole's tonal rule:** named everywhere, rendered nowhere. The
gauntlet's `world:sinkhole_open` injector should be the deck's biggest
event but is currently underweighted in the repo.

---

## Per-arcana canonical reference

For each arcana: chapter focus character, Pomegranate Hour episode,
sinkhole touch, gauntlet implications, and the state of my repo build.

### 0 — THE FOOL

- **Chapter focus:** John Frank · D'Ambrosio's diner · 3:47 AM
- **PH Ep. 0** — *"the boy who couldn't remember which diner"* —
  young man waking in a booth, the waiter is canonically John, 22 min
- **Sinkhole touch:** dark spot in the counter, sinkhole-shaped, wiped
  3,000 times
- **Gauntlet hand:** **John Frank**. Ultimate "Twelve Years" — once
  per game force the Gravity discard pile to be redrawn from
- **Gauntlet location:** D'Ambrosio's diner (Fool reversed). Inertia
  is the shadow.
- **Scenarios:** THE LEAP (canonical, easy, 3:47 AM), THE RUSH (medium,
  lunch service, 12:18 PM), FULL HOUSE (hard, evening service, 8:42 PM)
- **REPO STATUS:** ✅ Right. Canonical, well-aligned.

### I — THE MAGICIAN

- **Chapter focus:** Frasier Temple · Cathedral of Rust (warehouse) ·
  Graustark · paints workers as cosmic beings, post-sinkhole philosophy
- **PH Ep. I** — *"the trace"* — maintenance electrician traces a hum
  to a humming-but-unplugged server rack that is breathing. The
  electrician is canonically Frasier. The lemniscate-tracing gesture
  is learned from the breathing server.
- **Sinkhole touch:** the model city's EMPTY PLATFORM where the
  render farm sits — Frasier left it empty because the recursion
  problem is the geological problem
- **Gauntlet hand:** **Frasier Temple**. Ultimate: THE FIRST PAINTING
  (one currently-placed element counts as two for the win)
- **Gauntlet location:** Frasier's Warehouse (Magician reversed).
  DISORDER is the shadow. Components scatter overnight.
- **Scenarios:** THE STEAMBOAT ECHO (canonical), THE FIRE INSPECTION
  (alternate, Disorder 8 start, must drop to 3 before inspector), THE
  COMMISSION (alternate, patron's "thing" is one of 5 candidates)
- **REPO STATUS:** ✅ Right. Three scenarios built.

### II — THE HIGH PRIESTESS

- **Chapter focus:** **Elicia Temple** · gift shop / archive ·
  archivist of the D'Ambrosio family. She is the host of the
  Pomegranate Hour web series — directed it, uploaded all 22 episodes
  to VEIL.tv between vol3 and vol5. The series is *finished*. The
  domain registration lapsed in vol5; ripped copies circulate in a
  small private list.
- **PH Ep. II** — *"tape 11"* — a woman watches a VHS of herself two
  years younger watching a VHS, on which she takes a single note on
  yellow legal pad, the note is on her desk in her own handwriting.
  This is the meta-episode; Elicia is implicitly in it.
- **Sinkhole touch:** the sealed envelope in her archive labeled
  *"SINKHOLE — 17 untranscribed minutes (refused transcription by
  archivist)"*. She left the records office because what she had
  archived was unbearable to keep filing.
- **Gauntlet hand:** **Elicia**. Carries three items always: laptop,
  camera, lapel mic. Her win at any location is to film + record +
  edit a finished Pomegranate Hour episode about that location.
- **Gauntlet location:** Elicia's Archive (Priestess reversed).
  PRESSURE-TO-SPEAK is the shadow.
- **Scenarios:** THE TAPE (canonical), THE OPENING (alternate, deciding
  which tapes go on display), THE WIPE (alternate, a bag-man with a
  list of tapes to destroy)
- **REPO STATUS:** ⚠️ **MAJOR REBUILD NEEDED.** I built her as a
  41-year-old half-finished college show maker; canon: she is the
  archivist who *finished* all 22 episodes. My "Pomegranate Hour"
  with six invented episodes (Six Doors Down, etc.) is wrong. The
  real series is 22 episodes with specific canonical premises listed
  below. The suite/episode-spaces concept can stand structurally but
  needs to point at the actual canonical episodes.

### III — THE EMPRESS

- **Chapter focus:** **Nicola** (Antonio's wife / partner) + Aria
  (dual POV). The Nicola/Dante lattice is succession-by-marriage.
  Aria is the deck's interior consideration of inheritance.
- **PH Ep. III** — *"the garden under the floor"* — heavily pregnant
  woman in a maximalist Victorian sitting room hears growing sounds
  from beneath the floorboards. Sits on the rug for 19 minutes. The
  woman is canonically Nicola's mother (or Nicola herself; the deck
  reserves).
- **Sinkhole touch:** Nicola's tablecloth has a water stain from the
  sinkhole's groundwater
- **Gauntlet hand:** Nicola (or Aria split-POV)
- **Gauntlet location:** The Greenhouse (Empress reversed). ROT is
  the shadow. Garden rots faster than you can tend.
- **REPO STATUS:** ⚠️ **REBUILD NEEDED.** I built Nicola on a
  riverboat moored three doors down from Dante's office. Canon: she
  is Antonio's wife/partner. Her board may not be a riverboat; the
  riverboat is a vol5 Empress card image, not necessarily her chapter
  scenario's setting. The Greenhouse may be the right location.

### IV — THE EMPEROR

- **Chapter focus:** **Dante D'Ambrosio** · the sepia throne · father
  of Antonio and Alberto. The two upside-down faces in the floor
  mirror are his two sons. He has a recurring "alma (private)" slot
  in his calendar — sinkhole survivor he visits.
- **PH Ep. IV** — *"the chairman at the bbq"* — a retired businessman
  grills steaks; HOA neighbors arrive in succession, place wrapped
  dishes on the patio table, stand without sitting. Twenty-two
  minutes, no dialogue. The chairman is canonically Dante.
- **Sinkhole touch:** an unmarked photo frame on the throne-room
  wall, facing in; the alma slot weekly visits
- **Gauntlet hand:** **Dante**
- **Gauntlet location:** The Precinct (Emperor reversed). LEDGER is
  the shadow. Cases stack faster than you can close them.
- **Scenarios:** DOCKET, FIRST SESSION, APPEAL (in repo)
- **REPO STATUS:** ⚠️ **REFRAME NEEDED.** I built him as a small
  civic lawyer with brass clock and missing river-code volumes —
  the texture is fine, but his arcana is about the two-son
  inheritance and the void mother, not small civic rulings. His
  board can mostly stand; the *meaning* needs reorientation.

### V — THE HIEROPHANT

- **Chapter focus:** **Father Quent** — Acadian, Sunday sermons, a
  priest. Family friend of the D'Ambrosios. Officiated the mass
  memorial after the sinkhole. Has been the family's quiet handler
  of grief since. Wednesday-morning barge walkthroughs with Dante.
  Sunday booth calls: called Antonio (sent the elder son to die at
  Daigle's bar), called Natalie, called Carlie (the housekeeper).
- **PH Ep. V** — *"father on cable"* — a small-town priest hosts a
  public-access call-in show on Channel 14. The caller "from Beaumont"
  asks every week about a situation in 2002 the priest never
  describes. The priest says the same nine words: *"the door was
  locked. the door is still locked."* 9:09 PM cable interference.
  The priest is canonically Father Quent.
- **Sinkhole touch:** the carpet's three Latin lines gain a fourth in
  different ink — *"memorial — IV anniversary"*. Quent's annual mass.
- **Gauntlet hand:** **Father Quent** (a priest, not "sysop")
- **Gauntlet location:** Maya's Church (Hierophant reversed). DOCTRINE
  WEAR is the shadow. AUDI ET TACE inverted.
- **Scenarios:** THE VESTRY, THE WEDDING, THE FUNERAL
- **REPO STATUS:** ❌ **MISCAST.** I built the Hierophant as
  "Sysop's BBS room" — Sysop is Antonio's BBS handle (not a separate
  character), and the BBS is a *different artifact*. The Hierophant
  is Father Quent. The BBS room I built (`bbs_room.json`) can stay
  as the BBS *location* — Antonio runs it as sysop. But it's not the
  Hierophant's board.

### VI — THE LOVERS

- **Chapter focus:** "the cousin at the wedding" — two cousins meet
  at a third cousin's wedding, do not speak, the older cousin slides
  a VHS labeled ANYA_03 across the tablecloth. The Sanctuary on Cursed
  Ground.
- **PH Ep. VI** — *"the cousin at the wedding"* — same as chapter
  focus. The two cousins are played by actresses the deck reserves.
  One of them is canonically Anya (vol6 / vol7 hook).
- **Sinkhole touch:** the deck refuses to render Lovers directly —
  Lovers, Justice, Judgement are the three cards the deck refuses
  because they would require rendering the sinkhole. Lovers would
  require naming whose pair the sinkhole broke.
- **Gauntlet hand:** TBD (one of the cousins)
- **Gauntlet location:** The Bedroom (Lovers reversed). INDECISION
  is the shadow. Two visitors won't align on three choices.
- **REPO STATUS:** ❌ **WHOLLY WRONG CAST.** I built Sasha + Reed
  as the Lovers in an apartment above John's diner. Sasha and Reed
  are not canon. The Lovers is the cousin/Anya VHS pass. The
  apartment board can be repurposed as a different location (the
  Bedroom = Lovers reversed, possibly) but Sasha and Reed need to
  be demoted to visitors or removed.

### VII — THE CHARIOT

- **Chapter focus:** **Antonio D'Ambrosio** · Ember & Ash · New
  Orleans / Marigny · August hot office above the warehouse. Two
  speeds: gone and about to be gone. Q. Paul on the phone (silt of
  voicemails). Jimmy Daigle the foreman: *"option four... you don't
  ask me what it means."* Lila Bao the chef being courted away. The
  cypress beam from Lafayette. The window AC unit Jimmy installed.
  The man on the corner in the charcoal suit. **Antonio is dying.**
  Sysop of ember.ash.rest.bbs. Dies in a scaffolding fall Sunday
  morning. Father Quent's Sunday booth call sends Antonio to Daigle's
  bar to undo a scaffolding decision Quent made on Wednesday at the
  barge while Dante watched.
- **PH Ep. VII** — *"the black pickup"* — a single 22-minute take
  following a black pickup with Louisiana plates driving the
  perimeter of Harmony Creek Estates four times. The driver's
  watchless wrist is briefly visible on iteration 3. Elicia operates
  the camera from the passenger seat; she does not drive. The
  uncredited driver of the chase car is the un-named figure ("—")
  who comments "i was the driver" four months later.
- **Sinkhole touch:** Antonio's BBS handle "the_charioteer"
  originated at the sinkhole — he drove the recovery van. The
  handle is older than Daigle's bar.
- **Gauntlet hand:** **Antonio** (or, for the Chariot location's
  destiny side, the un-named driver of the chase car)
- **Gauntlet location:** The Long Road (Chariot reversed). FATIGUE
  is the shadow. Uses driving dice. Finales: DEAD AT THE WHEEL,
  WRONG CARGO, NEVER ARRIVED.
- **Scenarios:** THE LONG HAUL, THE SYSOP'S LAST LOG, RUN-AWAY CAB
- **REPO STATUS:** ❌ **WHOLLY WRONG.** I built Cora and the
  midnight bus. Cora is not canon. The Chariot is Antonio at Ember
  & Ash in New Orleans. **Full rebuild needed.** Cora can be
  demoted to a visitor (a passenger Antonio remembers, a phone call,
  etc.) elsewhere.

### VIII — STRENGTH

- **Chapter focus:** the un-named woman ("—"). Sinkhole rescuer.
  Pulled some out, not enough. Walks beside the river the sinkhole
  opened beside. Dash-signature.
- **PH Ep. VIII** — *"the woman at the fence"* — a woman feeds a
  stray dog through a chain-link fence at the back of a planned
  community lot, every evening at dusk, for ten evenings. Eleventh
  evening the dog is not there. She walks home through an orchard
  (Halsey).
- **Sinkhole touch:** the dash-signature is the signature she used
  on rescue reports for the family. She stopped writing reports.
- **Gauntlet hand:** the un-named figure ("—")
- **Gauntlet location:** The Vault (Strength reversed). STRAIN is
  the shadow. Hold what you can't hold.
- **REPO STATUS:** Not yet built.

### IX — THE HERMIT

- **Chapter focus:** the Hermit — Dante's brother, or a senior
  family lawyer/accountant. Handled paperwork for the sinkhole
  aftermath. Saw enough. Packed a lantern and left.
- **PH Ep. IX** — *"one lantern, no audience"* — a man with a
  six-sided lantern walks a country road at night. Twenty-two
  minutes of walking. The road ends at a closed wooden gate marked
  "HALSEY." He rests his hand on the latch. Does not open it.
- **Sinkhole touch:** the lantern's broken panel is broken at the
  sinkhole. He has not replaced it.
- **Gauntlet hand:** the Hermit (unnamed)
- **Gauntlet location:** The Cabin (Hermit reversed). LONELINESS
  is the shadow. The room empties of meaning around you.
- **REPO STATUS:** Not yet built.

### X — WHEEL OF FORTUNE

- **Chapter focus:** **Alberto Marroquín-D'Ambrosio** — younger
  son, carries his void mother's surname. Holds Dante's call log,
  Quent's call log, Daigle's call log. The night Antonio died,
  dialed Daigle 19 times in 14 minutes; Daigle did not pick up.
  Erica's Fortress Menu paperwork processes the Nexus.
- **PH Ep. X** — *"the phone tree"* — eleven strangers, each in a
  different domestic interior across one night, answering a beige
  push-button 1996 landline. Each says one word: "yes." Eleven
  yeses. Elicia's phone-tree diagram drawn by montage.
- **Sinkhole touch:** Erica's Fortress Menu has a fifth file no one
  has indexed: *"CASE PREDECESSOR"* (Settlement Grey). The Wheel is
  the deck's diegetic sinkhole-processor.
- **Gauntlet hand:** Alberto
- **Gauntlet location:** TBD (the call-center? the family office?)
- **REPO STATUS:** Not yet built.

### XI — JUSTICE

- **Chapter focus:** **Erica + Anna** (dual POV). The PetroTex case.
  Marta Romero's deposition. Anna recovering her father (lost at
  the sinkhole doing boat work for Dante).
- **PH Ep. XI** — *"deposition room b"* — a court reporter sets up
  her stenotype, plays back a deposition that has not yet been
  transcribed, dated three years in the future. She transcribes it
  and files it. The court reporter is Erica.
- **Sinkhole touch:** Anna's wireframe carries small inscribed
  coordinates that pinpoint the sinkhole's location.
- **Gauntlet hand:** Erica or Anna
- **Gauntlet location:** TBD
- **REPO STATUS:** Not yet built.

### XII — THE HANGED MAN

- **Chapter focus:** **Natalie** — Simon's apartment. The actress
  in PH XII / XVIII. Forced suspension.
- **PH Ep. XII** — *"the vigil"* — a woman alone in an apartment
  reads tarot for herself. Shuffles, cuts, lays three: Hanged Man,
  Moon, Star. Does this for 22 minutes. Cards do not change.
- **Sinkhole touch:** Natalie's notebook has a sigil she sketched
  at the sinkhole age 12 (vol6 hook).
- **REPO STATUS:** Not yet built.

### XIII — DEATH

- **Chapter focus:** Ward C. Walpurgisnacht. Six beds, two empty.
  Mr. D in Bed 6 is Dante. The night nurse counts pulses, writes
  on the handover sheet, does not speak.
- **PH Ep. XIII** — *"ward c"* — same scene as the chapter; the
  series predicts the chapter directly.
- **Sinkhole touch:** ward's east window faces the sinkhole site;
  dusk-pink light is partly the site's evening reflection. The bed
  census has no Mrs. D.
- **REPO STATUS:** Not yet built.

### XIV — TEMPERANCE

- **Chapter focus:** **Frank** — Tuesday observation. Two cups, the
  one not drunk.
- **PH Ep. XIV** — *"two cups"* — a man at his kitchen table at 5
  PM Tuesday, two cups (cold black coffee, warm chamomile), does
  not drink either. The man is canonically Frank.
- **Sinkhole touch:** Frank's retainer began the month after the
  sinkhole. He has been on observation since.
- **REPO STATUS:** Not yet built.

### XV — THE DEVIL

- **Chapter focus:** **Jimmy Daigle** — Gumbo Limbo, Daigle's bar.
  Bartender. Friend of Antonio's. Did not pick up the phone the
  night Antonio died because he could not bear to confirm to the
  brother (Alberto) that Antonio was already dead.
- **PH Ep. XV** — *"the HOA meeting"* — Harmony Creek HOA meeting
  about a noise complaint nobody on the board has heard. Three
  residents describe it differently (hum, tone, knocking). Board
  votes unanimous: *"silenced."* The Handsome Triumvirate (vol1)
  appear as audience members; Faust takes two honey jars.
- **Sinkhole touch:** the bar rests on the sinkhole's eastern lip.
  Daigle has tracked settling with a level for years. His father's
  original bar was lost at the sinkhole.
- **Gauntlet hand:** Daigle
- **Gauntlet location:** Daigle's bar (Devil reversed)
- **REPO STATUS:** Not yet built.

### XVI — THE TOWER

- **Chapter focus:** **Evangeline** — render queue. The Tower's
  collapse is the render farm's recursion problem. The farm sits on
  the sinkhole site's edge.
- **PH Ep. XVI** — *"the collapse of the water tower"* — town's old
  water tower collapses on a Thursday morning. Seven amateur cameras
  cut into a 22-minute composite. Collapse takes nine seconds. The
  episode is the only one to come close to naming the sinkhole; it
  refuses (collapse is a water tower, date wrong, location wrong).
- **Sinkhole touch:** the render farm's recursion problem ECHOES
  the sinkhole's geological problem. Job 47: *"the engine is
  trying to render the chapter that is the engine failing."*
- **REPO STATUS:** Not yet built. (scene file exists: vol5_ch16_tower.json)

### XVII — THE STAR

- **Chapter focus:** the un-named figure ("—"). Glass Skin, Christian
  Ice. The river offering.
- **PH Ep. XVII** — *"the river offering"* — un-named woman walks to
  a riverbank at night with two clay vessels, pours both into the
  river, signs a folded page with a dash, refolds it. The page is
  on D'AMBROSIO INDUSTRIAL — RECOVERED PERSONS LOG letterhead.
- **Sinkhole touch:** the river is the river the sinkhole opened
  beside. The vessels are the annual offering for the lost.
- **REPO STATUS:** Not yet built.

### XVIII — THE MOON

- **Chapter focus:** **Natalie** — sigils in static.
- **PH Ep. XVIII** — *"static"* — a woman watches analog static;
  at minute 11, the static resolves briefly into her own handwriting
  reading three sigils she once drew in a notebook but did not
  finish. The sigils are complete on screen; not in the notebook.
- **Sinkhole touch:** Natalie's static may carry the sinkhole's
  geological signature in its deep grain.
- **REPO STATUS:** Not yet built.

### XIX — THE SUN

- **Chapter focus:** **Frank** — dust motes. Saturday call to
  Elicia.
- **PH Ep. XIX** — *"four motes"* — Frank at a desk by an
  east-facing window in the early morning notices four dust motes
  in the slant of light. Counts them. Waits five minutes. Counts
  again. Four. Picks up phone, dials Elicia, nods twice, hangs up.
- **Sinkhole touch:** the four motes are the four survivors Frank
  counted out of fourteen.
- **REPO STATUS:** Not yet built.

### XX — JUDGEMENT

- **Chapter focus:** ensemble. Twelve survivors. *"we are doing
  this without him"* — Frasier's first line at 00:33 (Antonio is
  absent). Alberto is in the ensemble.
- **PH Ep. XX** — *"the ensemble gesture"* — community theater
  company rehearses a single gesture (right hand raised to eye
  level, held 3 seconds, lowered to heart). The twelve ensemble
  members are the actual sinkhole survivors. Elicia cast them
  years before vol5 named them.
- **Sinkhole touch:** the ensemble is the ensemble of those who
  were not lost. The unrendered verdict is the verdict on the
  lost.
- **REPO STATUS:** Not yet built.

### XXI — THE WORLD

- **Chapter focus:** the Frog Knows Best closing. The wreath. The
  gap.
- **PH Ep. XXI** — *"the wreath"* — wildflower wreath on a front
  door; slow 22-minute zoom. The gap in the wreath is the void
  mother's silhouette. Wreath rotates almost imperceptibly to
  center the gap by the end.
- **Sinkhole touch:** the wreath closes around a hole. The dancer
  is not coming; the wreath holds the absence; the absence is the
  sinkhole.
- **REPO STATUS:** Not yet built.

---

## Pomegranate Hour — series-level structure

The 22 episodes are Elicia's web series, uploaded to VEIL.tv between
vol3 and vol5. Domain registration lapsed in vol5; ripped copies
circulate in a private list (Frasier "FT", Frank, Anya "—", RES_SOL_VERIFY).

**Series-level rules:**
- **Cold open:** Elicia in halftone B&W chair, nods once, does not
  speak. Identical across all 22.
- **60 Hz hum** under every episode.
- **9:09 PM cable interference** in the diegesis of every episode.
- **Recurring visual elements:** Kwik Stop sign (in 14/22), HARMONY
  CREEK ESTATES sign (in all 22), black pickup with Louisiana plates
  (in 8), Halsey Farms delivery van or label (in 11).
- **Closing card:** *"a pomegranate hour · veil.tv / the host does
  not speak, by choice."*
- **Filming claim:** *"All episodes filmed within a 60-mile radius
  of one unnamed Texas exurb."* (The exurb is Harmony Creek.)

**Vol6 / vol7 foreshadows:** Each episode contains specific advance
signals. NexCorp Residential Solutions, Harmony Creek Estates (vol6),
Halsey Farms / Halsey Apiaries (vol7). The series is the deck's
primary advance organ.

**Comment-thread canon:** FT (Frasier — three-word phrases),
RES_SOL_VERIFY (compliance auditor), lostchild (Natalie — comments
under XII, XVIII, XIX), "—" (the un-named woman — comments under
VIII, IX, XVII).

---

## What my repo has wrong, by file

### Catastrophic miscasts (rebuild)

| File | What it is | Canon |
|---|---|---|
| `chariot/*` | Cora's midnight bus | Antonio at Ember & Ash, New Orleans |
| `lovers/*` | Sasha + Reed in apartment | "the cousin at the wedding," ANYA_03 VHS |
| `hierophant/*` | Sysop's BBS room | Father Quent on Channel 14 |
| `locations/the_midnight_bus.json` | invented | not canon — retire or repurpose |
| `locations/apartment_above_diner.json` | invented | not canon — could be the Bedroom (VI reversed) |
| `locations/bbs_room.json` | invented | exists in canon (Antonio's BBS) but is not the Hierophant's board |

### Reframes (texture mostly OK, focus wrong)

| File | What it is | Canon |
|---|---|---|
| `priestess/*` | Elicia, half-finished show | Elicia, *finished* 22-episode series |
| `locations/recording_booth.json` (Pomegranate Hour suite) | six invented episodes | canonical 22 episodes with specific premises |
| `empress/*` | Nicola on a riverboat | Nicola is Antonio's wife/partner |
| `locations/riverboat_interior.json` | invented | Empress reversed is The Greenhouse, ROT-tracked |
| `emperor/*` | Dante in a small civic office | Dante is a kingmaker father with two-son inheritance and void mother |

### Right and intact

| File | What it is |
|---|---|
| `fool/*` | John Frank, D'Ambrosio's, three scenarios — canonical |
| `magician/*` | Frasier, Cathedral of Rust, three scenarios — canonical |
| `framework/action_tableau_core.json` | Shared verbs — canonical |
| `achievements.json` | Most entries valid; some reference invented scenarios that need replacement |
| `world_state.json` | Sinkhole injector valid; needs amplification (sinkhole is THE event) |
| Engine code | `_episode_states`, `_hand_id`, `hand_overrides`, `advance_episode()`, `verb_labels`, the achievement evaluator — all sound infrastructure |

### Invented characters to demote to visitors (per user direction)

These remain as flavor/visitors in canonical scenarios; they were
authored as hands but should be NPCs:

- Cora (the midnight bus driver)
- Sasha (apartment dweller)
- Reed (their partner; Reed could remain as the cousin's bag, the
  painting subject, etc.)
- The bus kid (already a helper in Fool scenarios — keep)
- The late-shift worker, the lost traveler, the old regular (bus
  passengers — could become Antonio's New Orleans memory cast, or
  Daigle's bar regulars)
- The "Two-Chairs Women" subjects in Pomegranate Hour — could
  remain as PH episode subjects under the canonical episode list
- Hen, Marisol, Davey, Reggie, Prof. Kang, the New Collaborator —
  these were invented as Elicia's college collaborators; canon has
  her as a solo archivist who completed the show. Whether the
  collaborators stay depends on whether the gauntlet wants to add
  a fiction layer beneath canon. If kept, they're visitors only.

---

## Gauntlet framework — what's settled

Per `_TAROT_GAUNTLET_SCENARIOS.md`:

- **HAND × LOCATION × SCENARIO** mix-and-match
- Each hand has an action card set + ultimate
- Each location has a board + destiny deck + finales + visitor
  roster + scenario cards (3 per location)
- Hands unlock by clearing locations; the gallery picker is a
  3-column chooser; preview reveals titles but not effects
- Cross-arcana unlocks per (HAND × LOCATION) combo
- The Frasier reshade table is the model: every hand × location
  combo should produce *"a sentence that explains how the run
  feels"*

---

## What to build next, in priority

### Surgery (clean what's wrong)
1. Retire Cora-Chariot wholesale. Move salvageable visitor prose
   to other arcanas where it fits.
2. Reassign Sasha/Reed to visitors elsewhere. The
   apartment-above-diner location can become the Lovers Bedroom
   (VI reversed) if a Bedroom is wanted; otherwise it retires.
3. Mark `hierophant/*` as deprecated. Build Father Quent on the
   actual Hierophant arcana with a church board. Antonio's BBS
   becomes a Chariot location element.
4. Update `priestess/visitors.json` to remove the
   Hen/Marisol/Davey/young-Elicia cast OR demote them clearly to
   visitor flavor — but the Pomegranate Hour is *finished* in canon,
   so the half-done framing must go.
5. Update the recording_booth location to point at the canonical
   22 episodes with their actual premises (or a subset).

### Build (the canonical Chariot)
6. Author the new Chariot:
   - Location: Ember & Ash hot office + warehouse + sidewalk in New
     Orleans (and/or "The Long Road" per the gauntlet scenarios doc)
   - Hand: Antonio (the_charioteer)
   - Doom-clock: SILT (Q. Paul voicemails) or FATIGUE (per scenarios
     doc); both work
   - Visitors: Jimmy Daigle (helper), Q. Paul (off-board), the older
     man in charcoal (silent menace), the foreman, Lila Bao (phone
     only), Antonio's father DANTE (next-even-month phone voice),
     Alberto (the surviving brother; only one whose connection
     extends Antonio's life), the un-named driver of the chase car
     ("—" from PH VII)
   - Three scenarios: per `_TAROT_GAUNTLET_SCENARIOS.md` —
     THE LONG HAUL, THE SYSOP'S LAST LOG, RUN-AWAY CAB
7. Author the canonical Hierophant (Father Quent's church)
8. Reassess Empress location (probably Greenhouse, not Riverboat)
9. Reframe Emperor with the two-son inheritance + void mother spine

### Long-game (the rest of the 22)
10. Build the Lovers (cousin at the wedding)
11. Build remaining arcanas as the chapters surface

---

## Reading queue (when more lore lands)

- All vol5 chapter scenes in `godot/resources/scenes/vol5/*.json`
  (the actual VN scripts)
- `lore/_PITCHES.md` and `lore/pitches/*` (per-card pitches)
- `lore/_DEMONIC_DOMAIN.md` (electronic domain reframe)
- `lore/_DAMBROSIO_EMPLOYEES.md` (employment register)
- `lore/_UNLOCK_WEB.md` (per-card edges, in full)
- `lore/pomegranate_hour/_HOST_FRAMES.md` (host structure)
- `lore/planned_community/*` (vol6 lore)
- `lore/milk_and_honey/*` (vol7 lore)

---

## Working method going forward

1. **Read canon first.** Before building any new arcana, read the
   relevant vol5 chapter scene + Pomegranate Hour episode + any
   pitch file. The deck has its own vocabulary; my fabrications
   drift from it.
2. **Demote, don't delete.** The invented characters/locations
   remain as visitors/flavor inside canonical scenarios.
3. **Track misalignment in this wiki.** When canon and my build
   conflict, log it here. The user is feeding canon in pieces;
   the wiki is the running ledger.
4. **The sinkhole is everywhere.** Every arcana touches it. The
   `world:sinkhole_open` injector should be the deck's most
   pervasive ambient.

## Tonal rule · dream logic stays in the Priestess

Per user direction:

> *I don't mind dream logic with the high priestess, but most of
> the other levels have a root in reality with only small
> indulgences into the make believe or madness.*

**The Priestess is the dream-logic chapter.** Recursive tapes, the
room reading back, the static resolving into her handwriting, the
woman watching herself watch — these belong to her and only to her.
Pomegranate Hour episodes are Elicia's filmed interpretations of the
other chapters; they are Lynch-tonal because she is. But the
*chapters themselves* — and the gauntlet scenarios that mirror them —
are grounded.

**The other arcanas earn weight through specificity, not animism.**

- ✅ The cypress beam needs to be straight, not straight enough.
- ✅ The brass clock has been ticking since '62.
- ✅ The carpet has a path worn from six thousand paces.
- ✅ The window AC unit Jimmy installed runs "in the particular way
  that things installed by Jimmy run — at half capacity, with a
  faint smell of melting plastic, and with a personality."
- ✅ Quent pauses for the 9:09 PM cable interference and resumes.
- ✅ Frasier's "warehouse demons" — they're his electrical mood, a
  named mechanic he carries, not the room haunting him.

- ❌ "The bus has been remembering since 1991."
- ❌ "The kettle finds itself."
- ❌ "The painting glances at you."
- ❌ "The room remembers."
- ❌ "The clock corrects itself on its own."
- ❌ "The floppy wall serves up the right floppy."

The line: specificity yes, animism no — except in Elicia's room.

**What needs walked back in the existing repo (surgery list):**

- `empress/gravity_deck.json` — "the rosebush has put out a new bud
  overnight that it shouldn't have"
- `emperor/gravity_deck.json` — "the clock corrects itself,"
  "the stamp wears thin" (with agency)
- `hierophant/gravity_deck.json` — "the floppy wall serves up the
  right floppy," "the BBS is doing the thing it does when the night
  settles into it"
- `lovers/gravity_deck.json` — "the kettle finds itself," "the
  painting glances at you," the record changing side without
  agency
- `chariot/gravity_deck.json` — "the wipers move once without
  being asked," "the door's pneumatics hiss without being asked"
  (also: this whole arcana is being rebuilt around Antonio, so the
  walkback is moot for Chariot specifically)
- Various visitor lore_text and step text across the same arcanas

The Priestess gets a *deliberate boost*: since dream logic is hers
alone, it should land harder in her arcana than my prose currently
has it. The recursive logic of Pomegranate Hour II's "tape 11"
(the woman watching herself watch herself; the note she finds in
her own handwriting she does not remember writing) is the tier.

This wiki updates as the canon surfaces.
