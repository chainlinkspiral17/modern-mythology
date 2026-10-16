# Proofcheck: restored text vs. original page scans

Source: /home/claude/mm_src/orig.pdf, rendered at 150 dpi. 16 pages compared word by word against the text under each `<!-- p.N -->` anchor. Running heads, page numbers, line wrapping and Markdown markup were ignored, as was the author's own spelling where the scan has it (e.g. "opppsite", "prominient", "aligned,and", "florescent", "to swept", "enough light enough").

| page | words (approx) | errors | examples (scan → restored) |
|---|---|---|---|
| 30 ✓ | 95 | 0 | none |
| 58 | 130 | 2 | WAGNER'S → WAGNERS; "air. The" → "air, The" |
| 74 | 150 | 4 | Paint → paint; 3 action lines ("John kisses her neck…", "Joan kisses Faust…", "She is gone…") merged into the preceding JOAN/FAUST dialogue with no blank line |
| 95 ✓ | 420 | 4 | "re-turn. She" → "return, She"; "A split" → "Asplit"; David's → Davids; "Whether" → "whether" (with a stray "Delores." before it) |
| 120 | 470 | 3 | "details that" → "details. that"; “Where do I go from here?” → quotes lost; miscommunication → "miscommunica-tion" |
| 140 | 520 | 4 | "trunk. I" → "trunk, I"; "water. The" → "water, The"; "Gnats and" → "Gnatsand"; "skin to birth" → "sk into birth" |
| 185 | 290 | 3 | "Andy sat" → "Andys at"; “The Earthman Chronicles” → "The Earthman Chronicles ."; “Science Fiction” → missing its opening quote |
| 210 | 330 | 2 | "Tick tock tick" → "Ticktock tick"; they'll → "they II" |
| 250 | 300 | 6 | Aaron → "Aar on" (2 times); confusing → "c onfusing"; mother's → mothers; instinctively → "inst inctively"; "wakes up on" → "wakes upon" |
| 275 | 400 | 10 | opinion → "op ini on"; I'm → "m"; must've → "must ve"; "on a" → "ona"; "grew up on" → "grew upon"; "friend's brother's" → "friends brothers"; “You wanna know…?” → quotes lost; kid's → "kid s"; a false paragraph break before "For years" |
| 300 | 120 | 0 | Verse text is correct. An editorial "[[RECOVERED…]]" note was added. |
| 330 | 150 | 3 | SISTER'S → SISTERS; ain't → "a in t"; "nothing out." is split by a blank line |
| 350 | 430 | 3 | "beat up" → "be at up"; main-stream → "ma in-stream"; a false paragraph break before "What pissed" |
| 375 | 380 | 6 | boy's → "boy s"; quotes lost 3 times ("Alex, here take this", "give it to…", "be good"); "Storm Cloud storybook" → "Storm Clouds torybook"; "Sea Shells" → "SeaShells" |
| 405 | 400 | 10 | extra junk "Ly / Ht" at the top; quotes lost 3 times (“Shut up for real.”, “Write in…”, “The Dead Zone”); "prominient" → "prom inient"; everyone → "every one"; "They don't" → "They'don't"; Another → another; "Purses and" → "Pursesand"; "is" → "Is" |
| 410 | 300 | 3 | doctor's → doctors; Everyone → "Every one"; Aria's → Arias |

## Overall

About 4,900 words checked and 63 errors found, so roughly **1.3%**, or 1 error per 78 words. Two pages are clean (30, 300). Page 95 is marked ✓ but still has 4 errors, so the ✓ mark should not be taken as verified. Error density varies a lot: pages 250, 275, 375 and 405 have 6 to 10 errors each.

## Most common error types and mechanical fixes

1. **Lost apostrophes and curly quotes (about 25).** Examples: "kid s", "must ve", "they II", "Davids", "WAGNERS", and dialogue with its “ ” stripped.
   - Fix: replace `\b(\w+) (s|ve|ll|re|m|t|d)\b` with `\1’\2`, and replace "II" after a pronoun with "'ll".
   - Flag `[A-Z]{3,}S\b` in sluglines and `\b[A-Z][a-z]+s\b` before a noun as likely possessives.
   - Diff each paragraph's quote count against `pdftotext` output for that page, and restore “ ” wherever the count differs.
2. **Spurious spaces inside words and fused words (about 17).** Examples: "Aar on", "inst inctively", "a in t", "ma in"; "Gnatsand", "Pursesand", "ona", "Asplit", "Andys at".
   - Fix: run a dictionary (hunspell) pass. Join two adjacent tokens when the joined form is a word and at least one part is not. Split a non-word token when it splits cleanly into two words.
   - Also catch "upon" and "every one" by comparing against the pdftotext token stream.
3. **Wrong sentence punctuation and case (about 10).** Examples: ". She" → ", She"; "Whether" → "whether"; "Paint" → "paint"; "details. that".
   - Fix: flag `, [A-Z][a-z]` (except before "I" and proper nouns), `\. [a-z]`, and lowercase letters at the start of a paragraph or speech. Also join `\w-\w` hyphenation leftovers ("miscommunica-tion") when the joined form is in the dictionary.

**Structure note:** in the screenplays, action lines are sometimes merged into dialogue blocks (p74) or a dialogue line is split by a blank line (p330). Fix: insert a blank line wherever a non-indented line follows dialogue, using x-offsets from `pdftotext -bbox`.
