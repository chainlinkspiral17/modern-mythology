# Hero art — pictures on the world's surfaces

Hero Studio's `art` kind (roster: `godot/tools/meshy_roster.json`). An art
entry is generated like any concept image, then **installed as the picture
itself** in this folder, as `<slug>.png` (or `.jpg` / `.webp` if the provider returned
one). No Meshy step.

When a locale loads, `godot/scripts/vn/HeroArt.gd` reads every art entry's
`apply` rows for that locale and lays the picture on that surface as a matte
quad, hiding the box stand-in the row names. If the picture is not installed
(a fresh checkout before `drive-pull`), the stand-in stays.

## Adding one

1. Add an entry to the roster:

```json
{"slug": "my_poster", "kind": "art", "name": "the band poster in Nate's garage",
 "file": "my_poster.png", "vol": [6], "aspect": "2:3",
 "prompt": "what the picture shows, in its own medium",
 "canon": [{"src": "vol6/...json", "text": "the sentence that describes it"}],
 "apply": [{"locale": "nate_garage", "label": "over the loveseat",
            "center": [x, y, z], "size": [w, h], "facing": "-y",
            "hide": ["Wedding_Band_Poster"]}]}
```

   - `center` is in **Blender coordinates** (the builder's frame), `size` in
     metres, `facing` the side the viewer stands on: `+x`, `-x`, `+y`, `-y`
     or `up`. Read the stand-in's position from the builder or from
     `marker_aim_audit.geometry_godot(locale)` (Godot → Blender: `(x, -z, y)`).
   - Put the quad a millimetre or two in front of the surface.
   - `hide` lists name prefixes of the box stand-in to hide once the picture
     is installed.
   - Pick an `aspect` close to `size`'s ratio.

2. In Hero Studio: Generate image → pick the best → **Install picture**.
3. SAVE uploads it to the Drive with the models.

## On another machine

```bash
python3 godot/tools/meshy_pipeline.py drive-pull && bash godot/tools/reimport_models.sh
```
