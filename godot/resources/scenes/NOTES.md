# Scene data notes

## index.json is the playback registry

`SceneDataDB` resolves scene ids through `index.json`, and
`get_next_scene_id()` uses each volume's list **order** as the auto-advance
playback order for Vols 5–7 (a scene that ends without an explicit `jump`
flows to the next id in the list). Because of this, the order of ids inside a
volume is meaningful — inserting or appending an id changes the story flow.

`get_scene()` has a fallback that loads a `vol{N}_…` file directly from disk
even when it is absent from `index.json`, so a valid reference never
dead-ends. Drift is still reported by `tools/validate_scenes.py`.

Run `python3 tools/validate_scenes.py` (also enforced in CI) before
committing scene changes.

## Files intentionally absent from index.json

These are listed in `tools/scene_allowlist.txt` so the validator treats them
as known rather than as drift warnings.

### Vol 6 chapter stubs (`vol6_chN_stub`)

Intentional placeholders for not-yet-written scenes. Harmless; not reachable.

### Vol 7 ch6 / ch8 expanded draft (19 files) — DECISION NEEDED

An alternate, more detailed cut of Vol 7 chapters 6–8, e.g.
`vol7_ch6_cale_opening → vol7_ch6_tem_call → … → vol7_ch6_get_going` and
`vol7_ch8_six_oclock → vol7_ch8_kitchen → … → vol7_ch8_dark`.

The only entrance into this cluster is `vol7_ch7_bridge`, which **nothing
references**, so the whole cluster is currently unreachable. The canonical,
indexed flow uses the terser `vol7_ch6_sunday → vol7_ch6_cale`,
`vol7_ch7_six_oclock → vol7_ch7_night`, and `vol7_ch8_monday → vol7_ch8_aria`.

This was left as-is because wiring the draft in (or deleting it) is an
authoring decision, not an engineering one. To **adopt** the expanded cut,
replace the canonical ids in `index.json` `"7"` with the draft chain in
reading order (and update the draft `vol7_ch8_*` files, which currently carry
`"chapter": 7` / `"Ch 7 — …"` titles, to chapter 8 to match). To **drop** it,
delete the 19 files plus `vol7_ch7_bridge` and remove them from the allowlist.
