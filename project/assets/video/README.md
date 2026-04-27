# Video — Cutscene Clips

Full-motion video cutscenes played between scenes or during key moments.

## Naming convention
`{vol}_{scene_id}.mp4`

## Examples
```
vol1_opening.mp4
vol3_launch_sequence.mp4
vol4_rooftop_reveal.mp4
```

## Specs
- MP4 (H.264), 1280×720 or 1920×1080
- Include audio in the video file (BGM/SFX baked in)
- Engine pauses game audio during video playback
- Keep under 100MB per clip for web delivery

## In scenes (future node type)
```json
{ "t": "video", "src": "assets/video/vol1_opening.mp4", "skip": true }
```

`skip: true` allows the player to skip with a keypress.
