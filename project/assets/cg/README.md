# CG — Event Illustrations

Full-scene illustrations that unlock in the gallery after being seen in-game.

## Naming convention
`{vol}_{event_id}.jpg`

## Examples
```
vol1_diner_meeting.jpg
vol2_cemetery_goodbye.jpg
vol3_bay_seven_open.jpg
vol4_first_tag.jpg
```

## Specs
- JPEG or PNG, 1920×1080 recommended
- These are shown full-screen (letterboxed to fit)
- Higher quality than backgrounds — these are the "wow" moments

## In scenes (future node type)
```json
{ "t": "cg", "src": "assets/cg/vol2_cemetery_goodbye.jpg", "caption": "Briar Falls, October." }
```

## Gallery unlock
CG images unlock in the gallery the first time the player sees them.
Add them to the manifest in Asset Manager to register them for the gallery system.
