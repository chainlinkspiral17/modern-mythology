MODERN MYTHOLOGY — substrate / composition / visualizer system
==============================================================

This zip is a full drop-in for the project. Unzip into a copy of the
modern_mythology Godot project root (the folder that contains
project.godot). Open in Godot 4.6, reload project once.

What's been added on top of the upstream project
------------------------------------------------

Scripts (scenes/game/)
  AsciiSubstrate.gd         Live BBCode renderer (scene engine layer).
  AsciiSubstrateRaster.gd   Same data, rendered once to a SubViewport
                            texture. Used for fullscreen gallery views of
                            single substrate items.
  AsciiWindow.gd            One piece of a composition. Pre-renders all
                            animation frames into per-frame SubViewports
                            so cycling is a texture swap (no re-parse).
                            Supports shadow_color/shadow_offset for
                            drop-shadow typography.
  AsciiVisualizer.gd        Live BGM-reactive spectrum window. Direct
                            Font.draw_string() per cell — no BBCode in
                            the hot path, holds 60fps. Sub-cell ▁▂▃▄▅▆▇█
                            for fluid tip motion, peak hold, density
                            characters, optional wave_smooth_passes for
                            wave-like rippling.
  AsciiComposition.gd       Multi-window canvas. Reads manifest at
                            resources/substrates/compositions/<id>.json.
                            Window kinds: static (AsciiWindow), visualizer
                            (AsciiVisualizer), image (raw PNG/JPG).
                            Supports per-window alpha/modulate/z.

Modified scripts
  scenes/game/GameEngine.gd  Adds AsciiSubstrate as a scene-engine layer
                             and the "substrate" scene-node dispatch.
                             Auto-loads scene/<scene_id>.json if present.
  scenes/menu/GalleryOverlay.gd  Adds an ASCII SUBSTRATES section to the
                             gallery overlay; click-to-fullscreen render;
                             DEBUG button on composition viewers opens
                             the live tuning overlay.
  autoload/AudioMgr.gd       Adds AudioEffectSpectrumAnalyzer to the BGM
                             bus and exposes get_bgm_magnitude(low, high).

Debug
  scenes/menu/SubstrateDebugOverlay.gd  Right-side panel that exposes
                             live-tunable window properties (position, z,
                             alpha; visualizer-only smoothing/magnitude/
                             peak_decay/bar_count/bar_height). Export to
                             clipboard or save composition manifest JSON.

Tools (tools/)
  img2ascii.py        Image → ASCII grid JSON. Charsets ascii/blocks
                      (do not use braille — font fallback hang).
                      CELL_ASPECT = 0.6 to match SpaceMono.
  text_render.py      Image rendered using narrative text as char
                      vocabulary, mapped by per-cell luminance.
                      --text accepts a scene JSON; pulls narrate/say/
                      think text. --shadow-bg adds per-cell drop shadow.
  build_substrates.py Hand-author composer (Grid class + glyph stamps).
                      Currently builds the diner scene substrate.
  preview.html        Browser preview of any substrate piece JSON.

Resources (resources/substrates/)
  gallery/_index.json                  gallery manifest (what's listed
                                       under ASCII SUBSTRATES)
  gallery/tarot_fool.json              v1 single-substrate dashboard
  gallery/fool_reference_*.json        pure img2ascii test pieces
  compositions/fool_arcana.json        textual Fool card composition
  compositions/tarot_fool_v2.json      windowed dashboard composition
  compositions/music_player.json       layered music player composition:
                                       PNG bg + shimmering ASCII overlay +
                                       wave-smoothed visualizer + title
  pieces/*.json                        individual windows
  scene/vol5_ch0_booth6.json           auto-loaded substrate for the
                                       Fool's diner scene in the engine
  vol5/diner_predawn.json              named substrate addressable by
                                       scene directive

Scenes
  resources/scenes/vol5/vol5_test_tarot_fool.json  test scene that loads
                                       gallery/tarot_fool inside the
                                       running game engine
  resources/scenes/index.json          index, with vol5_test_tarot_fool
                                       added to vol5

Assets
  assets/gallery/fool.png              source image for the Fool card

Docs at project root
  SUBSTRATE_README.txt          this file
  SUBSTRATE_STYLE_GUIDE.md      palette, character vocab, naming, layout
                                principles, glitch design, hand-off
                                checklist for new chats
  HANDOFF_ARCANA_CARDS.md       brief for an agent picking up cards 1-21
                                of the Major Arcana


Verification after unzip
------------------------

1. Open in Godot 4.6, Project → Reload Current Project.
2. Main Menu → GALLERY. Header should read "0 / 0   +5 ascii"
   (or however many gallery items are registered).
3. ASCII SUBSTRATES section lists:
     • 0 — THE FOOL (textual)         (fullscreen text-art composition)
     • MUSIC PLAYER (live visualizer)  (the layered composition)
     • 0 — THE FOOL (dashboard)        (windowed v2 composition)
     • 0 — THE FOOL (v1)               (single-substrate)
     • TEST — Reference (blocks @ 400) (raw img2ascii test)
4. Click MUSIC PLAYER, top-left has a DEBUG button to tweak windows live.
5. Start vol 5 → "TEST — Tarot 0: The Fool" at top runs the v1 dashboard
   inside the game engine. "A Fool Between Acts" auto-loads the diner
   substrate as a layer beneath the dialog box.


Known constraints
-----------------

- Braille charset (U+2800-28FF) is unsupported by SpaceMono → font
  fallback hangs the renderer. Use ascii or blocks.
- Live BBCode rendering caps around 50k cells. Use the rasterized path
  (AsciiSubstrateRaster / AsciiWindow's pre-render) for larger pieces.
- SubViewport texture limit is GPU-dependent, typically 4096×4096.
- High-cell-count compositions can be slow to first-load on lower-end
  hardware (Steam Deck) — keep shimmer frames small (~20k cells each)
  and frame count modest (2-4).
