# HANDOFF · The 15 missing character models (vols 6–7)

**Why this matters:** the VN presentation survey found that nearly every
vol 6–7 character renders as a 60×64-pixel procedural bust upscaled 5×
— the single biggest visual gap left in the visual novel. The engine
side is DONE: `CharLayer.PORTRAIT_3D_KEY_TO_GLB` already maps every one
of these characters to a GLB filename, and `Portrait3D` (SubViewport,
three-point lighting, per-mood camera) renders any GLB that exists.
**Drop a correctly-named file in the folder and that character upgrades
to a lit 3D portrait with zero code changes.**

Per your directive (2026-06-16, `lore/_CHARACTER_MODELING_NOTES.md`):
character appearance is built externally in **Mixamo / Ready Player
Me** — so this is your paint-by-numbers session list.

## The mechanical steps (per character)

1. Build appearance in **Ready Player Me** (better hair/clothing
   variety) or **Mixamo** (better rigs). Export GLB (RPM) or FBX
   (Mixamo).
2. On the Deck, in Blender: import → scale to **1.80 m total height**
   → export glTF Binary as the EXACT filename below into
   `godot/assets/3d/locales/../characters/heroes/`
   (full path: `godot/assets/3d/characters/heroes/`).
3. Boot any vol 6/7 chapter with that character — the bust should be
   replaced by the 3D portrait automatically.

## VOL 7 · LAND OF MILK AND HONEY (priority — the current volume)

| file | keys | canon (from `lore/_VOL7_WIKI.md`) |
|---|---|---|
| `lena_vargas.glb` | lena | THE PROTAGONIST. Late 20s · morning barista at the Daily Grind · publishes the *Static Truths* zine · Vargas-Quintana family (delivered to Smolvud in CP canon) · lives above the Salty Tome. Highest screen-time model in the volume. |
| `wren.glb` | wren | Lena's friend · brings the SCUMM machine's message about the substrate leaking. |
| `tem.glb` | tem | The friend from *Static Truths* Issues 1–3 · reads John Frank's *The Frequency Beneath* aloud on Sundays · keeper of Olaf's cabin + the slowstick shelf (the frame story's hands). |
| `mrs_gable.glb` | gable, mrs_gable, marian_gable | Marian Gable · RETIRED TOWN LIBRARIAN (read: older) · morning seat at the Daily Grind · tends the anomalous-frequency archive · nine years of the same crow at the lighthouse. |
| `petra.glb` | petra | Proprietor of the Salty Tome bookstore · Lena's landlord · copier-host for Issue 1 · sells tide charts to zines. |
| `kai.glb` | kai | Runs Board Lords skate shop · skater since fourteen (read: 30s-40s now, skater dress) · the cannery is his secondary cathedral. |
| `per.glb` | per | Daily Grind regular · POV of chapter 14 · SCUMM-machine relationship is load-bearing. Canon is deliberately spare — your call on look. |
| `sal_carratura.glb` | sal, sal_carratura | **64** · proprietor of Pizza Pirate on Cypress St since 1991 · custodian of the SCUMM Machine since 2007. Pizzaiolo of thirty years — dress him like it. |
| `finn.glb` | finn | Carries the radio that picks up unallocated bands · inspects the cannery pilings at low tide · portable UV light. Field-coat / waders energy. |

## VOL 6 · PLANNED COMMUNITY (Harmony Creek Estates)

Richer per-character canon exists in `lore/planned_community/*.md`
(diego_ramos.md, maya_daigle.md, …) — skim before building.

| file | keys | canon (from `lore/_VOL6_WIKI.md`) |
|---|---|---|
| `diego_ramos.glb` | diego, diego_ramos | 19 · Gallatin Band drummer · NexCorp badge-clip collector · *missing* (his absence drives the volume — the model appears in flashback/memory scenes). |
| `maya_daigle.glb` | maya, maya_daigle | 16 · Cosmic Comics weekends · publishes the *NEWS FROM HARMONY CREEK* zine · F.T.'s correspondent. |
| `rick_cosmic.glb` | rick, rick_cosmic | Cosmic Comics' Rick — the shop's proprietor. |
| `skip_donnelly.glb` | skip, skip_donnelly | 39 · NexCorp Gas & Go shift supervisor · Diego's chosen witness · the reluctant. |
| `tanya_horne.glb` | tanya, tanya_horne | See `lore/planned_community/` for her file. |
| `carl_reno.glb` | carl, carl_reno | See `lore/planned_community/` for his file. |

## Notes

- **Sam Miller** intentionally stays a pixel bust (the GNM experiment
  was shelved 2026-07-16; `sam_miller_gnm.glb` is on disk if you ever
  want to resume — uncomment her two lines in the map).
- Priority order if you do these in batches: **lena → gable → petra →
  wren → tem** (vol 7 core cast, most screen time), then kai/per/sal/
  finn, then the vol 6 six.
- Models are static standing meshes (no skeleton needed for the
  portrait path) — Portrait3D's camera does the life (breath bob,
  mood framing).
- When a model lands, tell Claude — per-character lighting overrides
  (`Portrait3D.CHARACTER_LIGHTING`) can be tuned to flatter each one.
