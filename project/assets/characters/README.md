# Characters

Each character gets their own subfolder. Sprites are PNG with transparency.

## Folder structure
```
characters/
  ruth/
    ruth_neutral.png
    ruth_tired.png
    ruth_cold.png
    ruth_softening.png
    ruth_hurt.png
    ruth_warm.png
  jo/
    jo_neutral.png
    jo_cold.png
    jo_hurt.png
    jo_surprised.png
  stranger/
    stranger_neutral.png
    stranger_warm.png
    stranger_amused.png
    stranger_surprised.png
    stranger_impressed.png
  oracle/
    oracle_neutral.png
    oracle_calculating.png
    oracle_patient.png
    oracle_surprised.png
    oracle_worried.png
    oracle_thoughtful.png
  casper/
    casper_neutral.png
    casper_cold.png
    casper_considering.png
    casper_amused.png
  deja/
    deja_neutral.png
    deja_cold.png
    deja_warm.png
```

## Naming convention
`{character_name}_{expression}.png`

All lowercase, underscores only. Character name must match exactly what's used in scene scripts.

## Expressions (standard set)
neutral, happy, sad, angry, surprised, worried, cold, warm, amused, calculating,
impressed, thoughtful, hurt, softening, tired, excited, confused

## Specs
- PNG with transparency (alpha channel required)
- Recommended height: 800–1200px, width varies by character
- Engine centers and scales to ~440px display height automatically
- Keep the character roughly centered horizontally in the image
- Consistent canvas size per character recommended (e.g. 600×1000px for all Ruth sprites)

## In scenes
```json
{ "t": "show", "char": "ruth", "expr": "tired", "pos": "left" }
{ "t": "say", "char": "Ruth", "expr": "cold", "text": "You're late." }
```
Note: `show` uses lowercase char name (filename); `say` uses display name (any case).
