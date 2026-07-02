# Gobos & gels (light filters)

The rig ships **procedural** gobos (shape/pattern projected in the beam) and
gels (colour filters) — cycle them live with **F9** (gobo), **F11** (gel), and
**F10** to scatter a *mix* of different gobos+gels across the rig.

- Procedural gobos: `open, dots, stripes, spokes, grid, breakup, ring`
- Gels: `open, deep blue, amber, congo, rose, green, lavender, red`

## Custom gobos

Drop your own gobo textures here (`.png / .jpg / .webp / .exr`) and they're
appended to the F9 list (shown as `* name`). A gobo is a **grayscale** image:
**white passes light, black blocks it** — so a white pattern on black projects
that shape through the beam. 256–1024 px square works well.

The 3D Asset Manager can write these in for you (tag an image as a **gobo**),
or just copy files into this folder. They load on the next previz launch.
