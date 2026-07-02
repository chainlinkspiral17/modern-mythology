# Hero character GLBs

Drop hero-character meshes in this folder. They get picked up by
`build_graustark.py` Phase 5 via the `HERO_GLB_PATHS` table and
instanced at the canonical spawn label they're mapped to.

## File-naming convention

| Spawn label (in build_graustark) | Expected file | Canon |
|----------------------------------|---------------|-------|
| `Cath_Frasier`                   | `frasier_temple.glb` | Magician — Cathedral of Rust |
| `Church_priest`                  | `father_amato.glb`   | Hierophant — St Jude's |
| `Hermit_keeper`                  | `hermit_keeper.glb`  | Hermit — Bayou Lighthouse |
| `Frog_owner`                     | `frog_shop_owner.glb` | World |
| `Sun_Garden_old`                 | `frank_sun.glb`      | Sun |
| `Carnival_caretaker`             | `carnival_caretaker.glb` | Strength |
| `Cane_field_1`                   | `cane_worker.glb`    | Strength labour |
| `Cemetery_mourner1`              | `cemetery_mourner_1.glb` | Judgement |
| `Cemetery_mourner2`              | `cemetery_mourner_2.glb` | Judgement |
| `FQ_restaurant_door`             | `fq_restaurant_patron.glb` | (Bourbon Quarter) |
| `Casino_doorman`                 | `casino_doorman.glb` | Wheel |
| `Cath_apprentice`                | `maya_apprentice.glb` | Magician — Maya |

Anchor characters who appear at the riverfront (D'Ambrosio's diner)
aren't in the Graustark NPC_SPAWNS list because the riverfront is
preserved verbatim from `build_riverfront.py`. The classic
"hero John" would belong inside the riverboat interior scene.
When you build John, save him as `john_frank.glb` here anyway —
he'll be used when we move into the diner interior or any vol7
flashback.

## Mixamo workflow (per the user directive 2026-06-16)

For each hero:

1. Open <https://www.mixamo.com> (free Adobe login).
2. Pick the closest base character. Mixamo's bench is light on
   appearance variation — for Frasier (young Black male with
   locs) consider building base appearance in **Ready Player Me**
   (<https://readyplayer.me>) first since RPM has locs and
   clothing presets Mixamo doesn't.
3. Export the model:
   - Format: FBX 7.4 binary
   - Pose: T-pose (or A-pose; doesn't matter — re-pose in Blender)
   - Without animation if just the base mesh, or pick a single
     idle animation if you want it riding the model
   - Skin: include skin
4. On the Deck, drop the FBX into Blender, scale to 1.80m total
   height, then `File → Export → glTF 2.0 (.glb)` into this
   folder using the filename above.

If a hero GLB is missing, Phase 5 falls back to dacancino's
planar reference for that spawn — never breaks the build.

## Appearance reference

Canon-anchored visual specs live in
`lore/_CHARACTER_MODELING_NOTES.md` (the "Frasier — canonical
concept" block has the locs / olive bomber / GEARING CORP tee
detail; add similar blocks for John and Elicia when they're
ready).

## License

Mixamo characters and Ready Player Me avatars are licensed for
unlimited use in commercial projects per their respective TOS.
Document the source per hero in a `CREDITS.md` here if their
license requires attribution.
