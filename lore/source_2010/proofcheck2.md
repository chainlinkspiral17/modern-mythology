# Proofcheck 2: independent spot-check against page scans

Each restored page was compared word by word against its 150-dpi render of orig.pdf. Running heads, page numbers, line wrapping, Markdown and the author's own spellings were ignored.

| page | words | errors | examples (scan → restored) |
|---|---|---|---|
| 62 | 187 | 0 | — |
| 74 | 139 | 0 | — |
| 118 | 374 | 0 | — (author spellings "recieved", "kaliedoscope", "minutae" and "programmer.The" are kept as printed) |
| 140 | 487 | 1 | paragraph break lost: "...if that makes any sense." / "We came upon the beach..." (the scan starts a new line flush-left after a short line) → the two are merged into one paragraph |
| 190 | 319 | 0 | — |
| 225 | 310 | 0 | — ("jackham-/mer," joined across the page break correctly) |
| 250 | 270 | 0 | — |
| 275 | 283 | 0 | — |
| 330 | 172 | 0 | — (en dash in sluglines → hyphen: not meaning-changing) |
| 350 | 373 | 0 | — |
| 375 | 320 | 0 | — (the "#" at the top is the section's running-head glyph; p.405 shows it mid-sentence) |
| 405 | 393 | 0 | — ("opppsite" and "prominient" are kept as printed) |
| **Total** | **3,627** | **1** | |

**Overall error rate: 1 / 3,627 ≈ 0.03% (≈ 0.28 errors per 1,000 words).**

The one error is structural and debatable: an unindented paragraph start in the scan. No wrong, missing, extra, split or fused words were found. Apostrophes and quotes are intact throughout. Screenplay structure (cues, dialogue, action, sluglines) is intact on pages 62, 74 and 330.
