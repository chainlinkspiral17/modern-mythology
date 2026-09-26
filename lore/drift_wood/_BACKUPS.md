# The Backups · outside the canon

Everything in `godot/tools/comic/strips/bk_*.json`. Not *Drift Wood*,
not *ROFLCOPTER*: the pages the catalogue doesn't count. The
phantom graphic novels the corner boxes promised, the genre weeks
that ran once and got a second week that didn't, the private
experiments, and the pages where the strip looks sideways at the
rest of *Modern Mythology* and draws what it sees without saying so.

The book can print any of these as backup features between the
volumes' parts, or in the digital edition's apparatus. None of them
changes the canon. All of them are Wood's hand, in the era of the
year they were drawn.

## Rules

1. **The author is never on the page.** Same rule as the canon
   (`_AUTHORIAL_RULE.md`). A backup's protagonist is a character
   with an `extra_` id, or Wood, or the dog.
2. **Other volumes are quoted as objects, never as plot.** A boat's
   registration, a card in a drawer, a BBS banner, a talk-show on a
   motel TV, a woman in a yellow slicker from behind. The page draws
   the thing; the `image.notes` names the volume; the page never
   does. A reader of Vol 10 alone must lose nothing.
3. **One form, one device per series.** SLASH is rain-hatched noir
   pages; THE CARD IN THE DRAWER is one card per page as one Small
   Wood object; THE SCUMM STICK has a verb bar. A device used by one
   series is closed to the others.
4. **No series redraws a canon page.** The redundancy check: grep
   the canon for the backup's central image before writing it. If the
   canon has it, the backup needs a different image or a different
   series.
5. **Reserved stays reserved.** The tavern's name, whether 2020 is
   2020, the hardships, the mill's name, what the second key opens.
   A backup may circle a reserved fact more freely than the canon
   (SLASH puts a name on a boat), but the canon's reserved facts stay
   blank on a backup page too.
6. **Marks.** Backups Wood signed carry the era's mark (`gull`);
   experiments and found pages carry `none`; nothing carries the
   crab, the scruff or ROFLCOPTER — those are the canon's.

## The series

| series | drawn | form | genre | what it quotes | pages |
|---|---|---|---|---|---|
| **SLASH** | 2001–03 (Box 4B) | era1 pages, rain in vertical hatching | neo-noir · a crime story of the Oregon coast | a boat registered in Graustark; a clipping about a sinkhole; a card in an evidence bag | 10 |
| **THE LONG WAY BACK** | 2009–10 (the sabbatical) | era2 Sundays, watercolor | esoteric travelogue · 101 as twenty-two stops | the Major Arcana as motels, diners and a hole in the road | 8 |
| **CEDAR** | 2016–17 | era3 Sundays, wet-on-wet | magical realism · a novel of the timber country | the glow explained wrong three ways; a woman who was a tree | 8 |
| **THE SINKHOLE** | 2003 (The Unprinted) | era1 pages | weird · a Sunday from a paper he never drew for | a riverboat, a diner, a man smoothing his lapels at Table 14 | 4 |
| **THE FREQUENCY BENEATH** | 2022–23 (private) | pages that are graphs, waveforms, spectrograms | paranormal · the hum line as a frequency | a book by John Frank; 47 Hz; "a request" | 8 |
| **THE SCUMM STICK** | 2024–25 (private) | pages with a verb bar and an inventory strip | playful · the strip as a point-and-click | the machine in the pizza window; LOOK AT / PICK UP / USE | 8 |
| **THE BACKWARD DIGEST** | 2021–27 (private) | pages read right-to-left, overlays, a moebius, a tide table | experimental | the print tech's misfold of 1999 | 6 |
| **THE CARD IN THE DRAWER** | 2011–13 (the motel) | era3 pages, one card each | occult · a guest leaves a card each month | the Major Arcana as Small Wood things | 8 |
| **NOIR WEEK II · THE DOG DETECTIVE** | 2002 (unrun) | era1 dailies | pulp detective · the dog in the trench coat | the missing digest; a dame's postcard | 6 |
| **THE HALLOWEEN ISSUE** | 1998 (unpublished) | era1 biweeklies | pulp horror · the cafeteria at night | the lunch lady; the stone head walks; the sign spells | 4 |
| **RUST_CODE.BBS** | 2006–07 | era2 dailies | weird · the stick chorus gets handles | a banner; ACTIVE NODES: 64; a sysop named vagrant | 6 |
| **THE POMEGRANATE HOUR, 3 AM** | 2012–14 (the motel TV) | era3 dailies | occult talk-show · recaps | a host; a cassette archive; a voice named Anya | 5 |
| **THE RENDER WEEK** | 2008 (posted once, taken down) | era2 dailies with a progress bar under every panel | science fiction · the town as a render in progress | a watermark; a node count as a frame counter; a scrolling log | 6 |
| **THE FRONTIER WEEK** | 2000 (the editor cut it) | era1 dailies; the ridge closes every strip with one more thing on it | western · Small Wood in 1871 | a stranger whose name is the town's; a riverboat gambler with a lapel habit; a card face down on a stump | 6 |
| **POSTCARDS FROM THE OTHER TOWN** | 2019–20 (never ran) | spreads: a postcard's front and back; one legible word per card | romance · a lighthouse keeper's daughter and a northbound driver | the stamps numbered like a deck; eight words that end in the one the canon never says | 8 |

## Redundancy guard

Before a new backup page: grep `strips/` for its central noun. The
canon already has the jukebox in the plaster, the lamp on the beach,
the bird on most things, the flats in most lights, the sign's
letters, the corkboards, the box lids, the mailbox flag. A backup
that needs one of those must use it as a *quotation* inside its own
device (a card that is the lamp; a verb bar under the dock), not as
the image.

The shingle check: six-word shingles of each backup prompt against
every canon prompt, era prefix stripped. Anything above five shared
shingles that is not stock phrasing or a declared quotation is a page
to rewrite. Fifteen series, 101 pages, as of the last run: none.
