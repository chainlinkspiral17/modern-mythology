# STYLE GUIDES · Drift Wood / ROFLCOPTER

Reference for drawing (or generating) the strip consistently across
thirty years. Everything here is derived from the scripts in
`godot/tools/comic/strips/`, the brief, and the concept sheet; when
a script and a guide disagree, the script is the fact and the guide
is out of date — fix the guide.

| file | what |
|---|---|
| `characters.md` | every recurring figure, by era and age: silhouette, costume, posture, expression range, what never changes, drawing rules, and a model-sheet prompt |
| `eras.md` | the four eras and the arc palettes: line, paper, color, lettering, grid, balloons, the margin mark, the strip's own devices (two-thirds, narrow panel, wide panel, from-behind, lamp on/off) |
| `locations.md` | the hero locations with their fixed details and their changes over time; prompt blocks |
| `objects.md` | visual concepts, products, items: the marks, the corner box, the crab flyer lineage, the corkboard inventory, the sign's letter timeline, the cars, the boxes, the food, the paper |

The machine-readable companion is `godot/tools/comic/style_sheets.json`;
`python3 godot/tools/comic/comic_tool.py sheets` turns it into one
prompt per reference sheet for the same generator the strips use.

Three rules that govern every sheet:

1. **Wood, not Arthur.** No sheet depicts the author. Wood is the
   character; his age-variants are how the strip drew him.
2. **Faces the strip never gives.** The mother is a hand and a
   voice. The father is a back in a mill jacket. Julian is a coat
   on a hook, then a pleasant printed face. The editor is unnamed.
   Sheets respect the withholding.
3. **The era decides the line.** A 1998 Wood on a 2020 line is
   wrong even if the costume is right. Every character prompt is
   paired with its era block from `eras.md`.
