# VN info panels

2D comic-style info cards overlaid on the scene by VnDirector —
receipts, notes, diagrams. Triggered from scene scripts with
`[panel:<id>]` leading a narrate/say/think line; dismissed with
`[panel:off]`.

- Each panel is `<id>.json` in this directory, HeroImage schema
  (same as the slowstick hero images — see
  `godot/scenes/games/estuary_3/HeroImage.gd` for the op list).
- Author small (e.g. 120×90) — VnDirector integer-upscales with
  NEAREST into a bordered card in the upper field of the screen.
- Missing file → bordered text card showing the id (fallback
  discipline; a script must never crash the reader).

Grammar + voice rules: `lore/_VN_DIRECTION_PLAYBOOK.md`.
