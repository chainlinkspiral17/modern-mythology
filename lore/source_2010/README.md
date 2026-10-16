# Modern Mythology (2010) — restored source text, Volumes I–IV

The source for adapting the rest of the 2010 book into the visual novel. Each volume is one Markdown file:

| File | Volume | Book pages | Already in the Godot build |
|---|---|---|---|
| `vol1_faust.md` | I — Faust 3 (intro dialogue + Faust/Jacob/Wagner screenplay) | 1–87 | pp 3–52 ✓ |
| `vol2_small_wood.md` | II — Small Wood Volumes, by D.N. Dean | 88–176 | pp 88–102 ✓ |
| `vol3_earthman.md` | III — The Earthman Chronicles, by Lafayette Hubbard | 177–291 | none |
| `vol4_back_matter.md` | IV — scraps, the *weep (FOR THE FUTURE!)* zine, Charlie & Caroline, stories, "vii. daddy" | 292–413 | none |

Page numbers are PDF page indexes. The printed folio is the index + 1.

## How the text was restored

1. **Base:** `MODERN_MYTHOLOGY_CLEANED_v2.txt`, the visual-OCR pass from May 2026. It keeps the fi/fl ligatures but splits words ("r are", "be fore", "nightm are").
2. **Reconciled against the PDF's own text layer** (Drive's extraction, pp 1–248). That layer gets word boundaries right but drops ligatures. Each mismatch keeps whichever reading is real English: 557 fixes, all logged in `merge_log.tsv`.
3. **Reconciled against Andy's typed text in *Egretta Society*** (2013–15) on the 61 pages the two share (Small Wood, early Earthman, poems): 98 conservative fixes. Variant wording was not imported, and the Alsea River was kept.
4. **Rule-based pass** over everything else. It strips running heads, mends line-end hyphens, joins split words (a frequency dictionary plus the PDF's vocabulary decide), restores dropped apostrophes, and reflows wrapped prose. Verse and screenplay keep their lineation.
5. **Hand transcription from page images** for the pages missing from v2 or reduced to OCR soup. These are marked `[[RECOVERED from page image]]`.
6. **Known find-and-replace scar:** the original manuscript had a global Matt → Nathaniel swap, which produced "Nathanielress" and "Nathanieler". Those are fixed back to "mattress" and "matter". The character name Nathaniel is unchanged.

7. **Proofread page by page against the scans** for every page the game hasn't adapted yet (291 pages, 1,741 fixes; log in `tools/proof_log.tsv`). An independent check of 12 random pages afterwards found 1 debatable paragraph break in 3,627 words, about 0.03% (`proofcheck2.md`; the pre-proofread check is `proofcheck.md`).

The pages the game has already adapted (pp 3–52, 88–102) got the automatic passes only.

About 0.1–0.2% of lowercase words are still not in the dictionary. They are almost all Andy's own spellings and coinages as printed (couchmobile, wordnerds, idears, concieved), kept on purpose; `residue.txt` lists them.

## Image sections

- **Painted plates** (`images/plates/`): the cover, the title plate, the Small Wood, Earthman and back-matter section paintings, extracted at native resolution (~700 px). Upscale before using them as CGs.
- **driftwood (pp 157–176):** to be replaced by strips from the high-school run of the new **DRIFT WOOD** comic. Andy is editing those and will send them as a PDF. The block in `vol2_small_wood.md` is a placeholder; `driftwood/catalog.md` catalogs all 184 strips.
- **weep (FOR THE FUTURE!) zine (pp 309–316):** reproduced as new page images in `images/zine/`, with the transcribed text alongside in `vol4_back_matter.md`.

## Expansions (light, marked, removable)

New material sits only inside `:::expansion` fences. Each fence names its source and says why it's placed there. E2 and E5 are Andy's own older writing pulled from Drive. E3 is a new draft for Andy's review.

- **E3** (after p.132): **vii. SCUMM**, new writing that fills the empty chapter seven of Small Wood Volumes. It's Dickens Dean's high school dream journal, spring 1994: the nightmare Small Wood graphic adventure (woodgrain minivans, the giant crab, the faceless theater) that leads him to the slow stick. It previews and sets up the SCUMM volume.
- **E2** (after p.156, optional): *The Mircocosmographer*, an Oregon-coast clipping for the Small Wood scrapbook.
- **E5** (after p.35, optional): *Land of Milk & Honey* (2018), an echo of the Triumvirate's declaration.

Not used: the *Egretta* D. Nathaniel Dean bio (Andy: not canon); *paper cuts & the star key* (already in the book at pp 368–370, now recovered); *Egretta*'s Alan Wake framing (third-party IP); personal pieces (*You Don't Get to Have Nice Things*, the *da convo* chat); *macauscifinovel* (authorship unclear); *picking up the pieces* (graphic violence against children); *hometown something?* (real politicians and actors as characters).

## In the game (scene JSON)

The rest of Vols I–IV is now in `godot/resources/scenes/vol1–vol4`. There are about 6,900 nodes and 129K words. `index.json` lists the scenes in play order, and `validate_scenes.py` reports 0 errors and 0 warnings. The adaptation is faithful: all of the book's text is reached on every path. Added choices are "linger" or reading-order forks that always rejoin. The authoring brief is `SCENE_AUTHORING.md`.

- **Vol I:** `vol1_ch4_interstitial` (the skipped p.48), then Act Two, `vol1_ch5_*`–`vol1_ch8_*`, then `vol1_finale`. Chapters 2→3→4 now chain straight through.
- **Vol II:** `vol2_ch3_*`–`vol2_ch12_*`, including **vii. SCUMM** (`vol2_ch7_scumm_a–d`). Then `vol2_drift_wood`, a **placeholder** for Andy's DRIFT WOOD strips, then `vol2_finale`.
- **Vol III:** `vol3_title` (Earthman plate), then `vol3_ch1_*`–`vol3_ch14_*`, then `vol3_finale`. The placeholder ORACLE-7 demo is moved to `scenes/_demo/`.
- **Vol IV:** a scrapbook desk, `vol4_hub`, opens Scraps, Poems, the Zine, Charlie & Caroline, and Stories in any order. **vii. daddy** appears only after all five have been opened; this uses the new `requires` choice gating in `GameEngine.gd`. The placeholder Casper demo is moved to `scenes/_demo/`.

`ASSET_WORKLIST.tsv` lists every new background, CG, music track and portrait the scenes reference (220 bg, 35 cg, 34 bgm, 18 portraits), with one painter-ready line each. It's ready for bulk_intake.

Open questions for Andy, as flagged by the batches:
- p.283 (blank in the PDF render) was supplied by Andy as a screenshot and is now in both the source text and the uncle nick scene.
- The chapter numerals in Earthman repeat (two v.s and two vi.s). The game numbers them 1–14.
- In Vol I, "Dicken's Phone vibrates" is printed where the line seems to be Faust's. It's kept as printed.
- In "ps." (p.393), the blog postscript after SCUMM plays as its own story.
