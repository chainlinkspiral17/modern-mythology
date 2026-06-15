# ANDY LINK

andylink@gmail.com · LinkedIn: [in/chainlinkspiral](https://www.linkedin.com/in/chainlinkspiral/) · GitHub: [chainlinkspiral17](https://github.com/chainlinkspiral17)

---

## SUMMARY

Senior-track narrative designer and prose writer applying for the **Senior Game Writer** post at **CD Projekt Red**. I write character-driven, morally-complex genre fiction across long-form formats — novel-scale cross-volume world-building, branching gallery puzzles, episodic teleplay, in-fiction zines, and game-engine integration in Godot 4. My current ongoing project, *Modern Mythology*, is a seven-volume narrative cycle with a working gallery game and a procedurally-generated 3D suburb that I author end-to-end: lore, screenplay, character files, gameplay scripting, and Blender pipeline.

What I bring to CDPR's writing room:

- **Tone fluency** across operator-noir, clipped suburban paranoia, slow PNW grunge, and high-stakes occult procedural — all in the same canon, each tonal register held distinct.
- **Restraint with mature material.** I have written hospital-night, addiction, grief, and substrate-horror chapters that earn their weight through specificity, never through shock.
- **Branching narrative discipline.** Cross-card hooks, gated reveals, save-state-aware dialogue, and a 22-node tarot graph wired to the Godot save system.
- **Pipeline-aware writing.** I have shipped the script, the playable scene, the 3D locale, and the post-process shader pass on the same week.

---

## SELECTED PROJECT — *MODERN MYTHOLOGY* (2024 – present)

A seven-volume narrative cycle. Two volumes drafted in full, four in outline, one in pre-production. Companion gallery game (*Tarot Gauntlet*) shipping playable. ~284,000 words of in-universe prose to date. Self-published lore corpus at [github.com/chainlinkspiral17/modern-mythology](https://github.com/chainlinkspiral17/modern-mythology).

### Volume map

| Vol | Title | Setting | Tonal register |
|---|---|---|---|
| 5 | **Major Arcana** | Graustark, Texas/Louisiana, late-90s | operator-noir warm |
| 6 | **Planned Community** | Harmony Creek Estates, Gulf Coast, summer | clipped suburban paranoia |
| 7 | **Land of Milk and Honey** | Smolvud, Oregon coast, 2025 | slow PNW grunge |

Volumes are linked by a stable cast (the **Demon Roster** — eight bound programs that survive across decades) and a single non-human phenomenon, **the substrate**, that has been stable for thirty-seven years and is — in 2025 — becoming a request.

### Writing samples

#### 1. Cold open of *The Pomegranate Hour · S01E00 — "The Boy Who Couldn't Remember Which Diner"* (Vol 5 framing show)

> Black.
>
> A burgundy serif title fades in: **THE POMEGRANATE HOUR.** Below it: **0 — THE FOOL.**
>
> Cut to interior of a halftone-monochrome room. ELICIA — mid-thirties, dark hair tied back, no makeup — sits in a wooden chair, her hands folded in her lap. She looks at the camera. She does not smile. She nods, once.
>
> Cut to black. The faint hum of a 60 Hz refrigerator compressor enters and does not leave.
>
> *— [lore/pomegranate_hour/00_fool.md](lore/pomegranate_hour/00_fool.md), full episode 22 minutes, 375 lines*

#### 2. Voice of an eighteen-year-old gas-station cashier writing her own zine (Vol 6)

> She has been making this for fourteen months. It is photocopied at the Kinko's that closed in March (she has a small stockpile of pre-made copies in the storeroom under the cleaning supplies). She has never sold one. She has given six away. Three of them to Diego. One to Maya Daigle. One to Jen the day manager. One to a regular customer she likes named ROY who buys a single Lone Star tallboy every Friday at 5:48 PM.
>
> *— [lore/planned_community/sam_miller.md](lore/planned_community/sam_miller.md)*

#### 3. The opening editorial of Lena Vargas's in-fiction zine *Static Truths* (Vol 7)

> *I woke this morning with charcoal on my thigh. Three letters. S U N. I have not used charcoal. The charcoal is not in my apartment. The charcoal is from a wall somewhere — I do not know where — and the charcoal also will not, by the time of this writing, wash off. It has been on me for three days.*
>
> *I have decided to start a zine. The zine is going to be about the small things the coast does not, in its own voice, get to record.*
>
> *— [lore/milk_and_honey/static_truths.md](lore/milk_and_honey/static_truths.md)*

#### 4. Research-driven night-shift procedural — *The Pomegranate Hour · S01E13 "Ward C"* (XIII · DEATH)

A 23-minute episode set in an overnight hospital ward, anchored on a Vietnamese-American charge nurse, Chị Huyền, and the **cô hồn** wandering-souls altar she has kept at the nurses' station for eleven years. The episode's production note negotiates filming consent on behalf of sedated and deceased patients. The card's classical iconography (Death the harvester, the rose, the river) appears only in working details: the peeled orange segments, the held basil sprig, the river stone weighting a folded note.

> *— [lore/pomegranate_hour/13_death.md](lore/pomegranate_hour/13_death.md)*

#### 5. Branching-narrative architecture — the *Compass* in-fiction artifact

A 22-node tarot graph wired to the project's Godot save system. Every Major Arcana card is a node; cross-references between cards form the edges (Magician's iron-sigil wakes the bookshelf on Priestess's card; Fool's polaroid pins to the Priestess's archive; etc.). The compass has **two unlock tiers**: a menu tier triggered by hotspot encounter or by reading the RUST_CODE.BBS header three times across different cards, and an in-game tier strictly puzzle-gated with no test override.

> *— [lore/_COMPASS.md](lore/_COMPASS.md)*

#### 6. Genre register — operator-noir vs. suburban paranoia (single-line specimen)

From Vol 5 (operator-noir):

> The bell over the door does not chime. THE WAITER walks into frame from the kitchen. Sixty, soft-spoken, hair clipped close, white button-up tucked into black trousers, an apron tied at the waist. He moves the way a person moves through a room he has been responsible for for a long time.

From Vol 6 (suburban paranoia):

> Mrs. P. brings the cookies on the day. she does not say who they are from. I have, however, identified the paper. some chapters get themselves told by the wrapping.

---

## SHIPPING-CRAFT NOTES

- **Authored a playable companion game.** *Tarot Gauntlet* is a Godot 4 gallery puzzle game that consumes the Vol-5 puzzle-hooks JSON, awakens cross-card hotspots as the player resolves prerequisites, and pulls the same canonical character art used in the book. See [godot/scenes/games/TarotGauntletGame.gd](godot/scenes/games/TarotGauntletGame.gd) for the gameplay loop.
- **Built a procedural 3D suburb pipeline** for Vol 6's Harmony Creek Estates. Blender Python emits the entire district — terrain, roads, parking lots, ~30 buildings, NPCs — from a single 12,000-line build script. The script reads canon character locations from the prose files and emits matching geometry. See [godot/tools/blender/locales/build_harmony_terrain.py](godot/tools/blender/locales/build_harmony_terrain.py).
- **Wrote and maintain a craft playbook** capturing hard-won rules across modeling, lighting, screen-space shaders, and infrastructure alignment. The playbook style ("Recent lessons" entries graduated to "Core rules") is the working memory I would bring to a writing team. See [lore/_3D_MODELING_PLAYBOOK.md](lore/_3D_MODELING_PLAYBOOK.md), [lore/_SHADER_VISUALS_PLAYBOOK.md](lore/_SHADER_VISUALS_PLAYBOOK.md), [lore/_LIGHTING_PLAYBOOK.md](lore/_LIGHTING_PLAYBOOK.md).

---

## CRAFT VOCABULARY

- **Prose style** — clipped, specific, present-tense observational; aversion to expository dialogue.
- **Worldbuilding** — non-human phenomena treated as load-bearing infrastructure; cult and folklore detail researched and applied without ethnographic shorthand.
- **Branching narrative** — gated reveals, cross-referenced hotspots, save-state-aware dialogue, no false choice.
- **Tonal control** — three distinct registers across the same canon; tonal seams are scene transitions, not chapter breaks.
- **Toolchain** — Godot 4 (GDScript), Blender Python, Markdown-first lore corpus, Git-as-canon (every commit message a working note).

---

## RELEVANT REPO LINKS

- **Project canon + working code:** [github.com/chainlinkspiral17/modern-mythology](https://github.com/chainlinkspiral17/modern-mythology)
- **Vol 5 wiki (synthesizing entry):** [lore/_VOL5_WIKI.md](lore/_VOL5_WIKI.md)
- **Vol 6 wiki:** [lore/_VOL6_WIKI.md](lore/_VOL6_WIKI.md)
- **Vol 7 wiki:** [lore/_VOL7_WIKI.md](lore/_VOL7_WIKI.md)
- **Per-arcana scene treatments:** [lore/pitches/](lore/pitches/)
- **The Pomegranate Hour episode scripts:** [lore/pomegranate_hour/](lore/pomegranate_hour/)
- **Planned Community character files (Vol 6):** [lore/planned_community/](lore/planned_community/)
- **Land of Milk and Honey artifacts (Vol 7):** [lore/milk_and_honey/](lore/milk_and_honey/)

---

## WHY CDPR

The Witcher's commitment to consequence — choices that hold across a 60-hour campaign without erasure — and Cyberpunk's commitment to texture — every shard, every braindance, every ripperdoc's office told its own short story — are the two writing disciplines I have been independently practicing in *Modern Mythology*'s gallery + book + procedural-suburb pipeline. I would bring that same discipline to a CDPR quest line: a scene that reads, a choice that holds, a city block that has been someone's home long enough that the wear pattern on its kitchen linoleum tells the truth.

I would be grateful to discuss.

— Andy
