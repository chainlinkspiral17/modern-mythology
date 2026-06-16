# Hero GLB Uploader

A self-contained HTML tool for installing textured hero GLBs into
`godot/assets/3d/characters/heroes/` with the right canonical
filenames.

## What it does

- Lists every canonical hero slot (mirrors `HERO_GLB_PATHS` in
  `godot/tools/blender/locales/build_graustark.py`) with a status dot
  showing whether each slot is currently filled.
- Drag-and-drop a `.glb` (or browse for one), preview it rotating in
  3D, then click **Install** to write the file with the canonical
  filename to the repo.
- Generates the matching `git add && git commit && git push`
  command to paste afterward.

## Two modes

The tool uses the browser's [File System Access
API](https://developer.mozilla.org/en-US/docs/Web/API/File_System_Access_API)
when available so it can write straight into the repo with no
download round-trip.

- **Direct-install mode** (Chromium-family browsers — Chrome, Edge,
  Brave, Vivaldi): click **Pick repo directory**, navigate to
  `godot/assets/3d/characters/heroes/`, grant write access once, and
  every subsequent install writes that file directly to disk.

- **Download mode** (Firefox, Safari): the tool downloads the GLB
  with the canonical filename. Move the downloaded file into
  `godot/assets/3d/characters/heroes/` yourself, then run the
  displayed git command.

## How to open it

It's a static page — no server, no build step.

On the Steam Deck:

```bash
xdg-open /home/deck/Downloads/modern-mythology/godot/tools/hero_uploader/index.html
```

Or just navigate Files → that folder → double-click `index.html`.

For direct-install mode on the Deck you'll need a Chromium browser
(Chrome / Edge / Brave installed via Flatpak). Firefox is fine for
download mode.

## Workflow

1. Open `index.html` in a browser.
2. (Chromium only) Click **Pick repo directory** → select
   `godot/assets/3d/characters/heroes/`.
3. Drag a `.glb` onto the page (or click **browse**).
4. The tool auto-selects the matching hero slot if the filename
   already matches a canonical (e.g. dragging `frasier_temple.glb`
   selects `Cath_Frasier`). Otherwise click the right slot in the
   list on the left.
5. Click **Install**.
6. Copy the displayed git command, paste it in a terminal, push.

## Adding a new hero slot

If you're adding a brand-new hero that doesn't exist in
`HERO_GLB_PATHS` yet, add the entry to BOTH:

- `godot/tools/blender/locales/build_graustark.py` (the
  `HERO_GLB_PATHS` dict)
- `godot/tools/hero_uploader/index.html` (the `HEROES` array near
  the top of the inline script)

Keep them in sync.
