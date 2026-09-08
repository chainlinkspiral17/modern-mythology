#!/usr/bin/env python3
"""mood_clock_audit.py — a mood is a claim about time and light; audit it
against the fiction (2026-09-11).

The 2026-08-30 back-to-front pass found ch23_sleep — five bedrooms,
cicadas, midnight — running under `dawn_warm` end to end, and the 1:15
AM porch vigil doing the same. One mood held across a whole chapter is
the shape the bug takes: it was placed once, early, and never revisited
when the chapter's clock moved.

This reads each chapter's prose for TIME EVIDENCE (clock times, hour
words, meals, light words) and compares it with the time each [mood:]
cue claims. A mood governs from its cue to the next one, so the
evidence counted for a cue is the prose of ITS passage, not the
chapter's.

Moods that make no time claim (raw, studio, linework, the arcana
looks, dream_blur…) are never flagged — they are style, not hour.

    python3 godot/tools/audit/mood_clock_audit.py           # every volume
    python3 godot/tools/audit/mood_clock_audit.py vol6      # one
    python3 godot/tools/audit/mood_clock_audit.py --all     # show agreements too
    python3 godot/tools/audit/mood_clock_audit.py --soft    # adjacent hours too (noisy)

Informational, and a taste call: the tool knows what the prose says,
not what the scene means. A deliberate dawn over a midnight vigil is a
choice; this only makes sure it was one.
"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SCENES = os.path.join(ROOT, "godot", "resources", "scenes")

MOOD_RX = re.compile(r"\[mood:([a-z0-9_]+)\]")

# ── what hour each mood claims ────────────────────────────────────
MOOD_HOUR = {}
for _name in ("dawn", "dawn_warm", "dawn_diner", "smallwood_dawn", "morning_bright",
              "kitchen_clean", "dambrosios_brunch", "pomegranate_hour",
              "pomegranate_hour_open"):
    MOOD_HOUR[_name] = "morning"
for _name in ("midday", "texas_noon", "day_bright", "lunch", "overcast_day",
              "texas_bleach_day", "hce_texas_day", "hce_overcast", "bindery_day",
              "riverfront_clean", "road_clean"):
    MOOD_HOUR[_name] = "day"
for _name in ("golden_hour", "sunset", "dusk", "blue_hour", "garage_dusk",
              "bungalow_dusk", "rf_blue_hour", "hce_golden_porch"):
    MOOD_HOUR[_name] = "dusk"
for _name in ("night", "midnight", "3_47_am", "liminal_night", "sodium_streetlamp",
              "convenience_night", "bungalow_late", "dambrosios_3am",
              "hce_liminal_night", "candlelight", "candlelight_low", "tv_glow",
              "tv_glow_blue", "smoky_bar", "rf_linework_night", "night_vision_green",
              "bar_pendant_amber", "card_room_pendant"):
    MOOD_HOUR[_name] = "night"

# ── what hour the prose says ──────────────────────────────────────
WORDS = {
    # "pre-dawn" is the hinge, the way dusk is: dark, but a dawn mood over
    # it is a choice, not an error. It counts for neither side.
    "morning": (r"\bmorning\b", r"\bsunrise\b", r"(?<!pre-)(?<!pre )\bdawn\b",
                r"\bbreakfast\b", r"\bfirst light\b"),
    "day": (r"\bnoon\b", r"\bmidday\b", r"\bafternoon\b", r"\blunch(?:time)?\b",
            r"\bdaylight\b", r"\bmid-?afternoon\b"),
    "dusk": (r"\bdusk\b", r"\bsunset\b", r"\bevening\b", r"\btwilight\b",
             r"\bgolden hour\b", r"\bsundown\b"),
    "night": (r"\bmidnight\b", r"\btonight\b", r"\bnightfall\b", r"\bmoonlight\b",
              r"\bthe moon\b", r"\bstars?\b", r"\basleep\b", r"\bin the dark\b",
              r"\bat night\b", r"\bthat night\b", r"\bthe night\b"),
}
# a clock reading is the strongest evidence there is
CLOCK_DIGITS = re.compile(r"\b([0-2]?\d)[:.]([0-5]\d)\s*(a\.?m\.?|p\.?m\.?)?", re.I)
CLOCK_AMPM = re.compile(r"\b([0-2]?\d)\s*(a\.?m\.?|p\.?m\.?)", re.I)
HOUR_WORD = r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)"
CLOCK_SPELLED = re.compile(HOUR_WORD + r"[- ](?:o'?clock|thirty|fifteen|forty|fifty|twenty|ten|eleven|"
                           r"oh-?\w+|" + HOUR_WORD + r")?\s*(in the (morning|afternoon|evening)|"
                           r"a\.?m\.?|p\.?m\.?|at night)", re.I)
SPELLED = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
           "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}


def bucket_for_hour(h):
    # 4 and 5 AM are DARK: the hour a person is awake at is not the hour
    # the sun is up. Morning light starts at six.
    if 6 <= h < 11:
        return "morning"
    if 11 <= h < 16:
        return "day"
    if 16 <= h < 20:
        return "dusk"
    return "night"


# "awake since seven AM", "until four", "from nine" — a clock in one of
# these is a span the scene REMEMBERS, not the hour it is happening in
NOT_NOW = re.compile(r"(since|until|till|from|before|after|by)\s*$", re.I)


def clock_hits(text):
    """Every clock reading in the passage → hour buckets."""
    out = []
    for m in CLOCK_DIGITS.finditer(text):
        if NOT_NOW.search(text[max(0, m.start() - 12):m.start()]):
            continue
        h = int(m.group(1))
        ap = (m.group(3) or "").lower().replace(".", "")
        if ap.startswith("p") and h < 12:
            h += 12
        elif ap.startswith("a") and h == 12:
            h = 0
        elif not ap and h > 23:
            continue
        out.append(bucket_for_hour(h % 24))
    for m in CLOCK_AMPM.finditer(text):
        if NOT_NOW.search(text[max(0, m.start() - 12):m.start()]):
            continue
        h = int(m.group(1))
        ap = m.group(2).lower().replace(".", "")
        if ap.startswith("p") and h < 12:
            h += 12
        elif ap.startswith("a") and h == 12:
            h = 0
        out.append(bucket_for_hour(h % 24))
    for m in CLOCK_SPELLED.finditer(text):
        if NOT_NOW.search(text[max(0, m.start() - 12):m.start()]):
            continue
        h = SPELLED.get(m.group(1).lower())
        if h is None:
            continue
        tail = (m.group(2) or "").lower()
        if "afternoon" in tail or "p" == tail[:1]:
            h = h + 12 if h < 12 else h
        elif "evening" in tail:
            h = h + 12 if h < 12 else h
        elif "at night" in tail:
            h = h + 12 if 5 < h < 12 else h
        out.append(bucket_for_hour(h % 24))
    return out


def word_hits(text):
    out = []
    for bucket, pats in WORDS.items():
        for p in pats:
            out += [bucket] * len(re.findall(p, text, re.I))
    return out


OPENING_NODES = 3          # lines that describe the PRESENT scene


def passages(nodes):
    """[(mood, opening prose)] — each mood cue governs until the next, but
    only its OPENING lines are evidence. A chapter set at night narrates
    the morning it is about in past tense on every second line; counting
    the whole passage makes every night scene read as morning. The lines
    right after the cue are the ones describing the room you are in."""
    out = []
    cur = None
    buf = []
    for nd in nodes:
        t = nd.get("text")
        if not isinstance(t, str):
            continue
        m = MOOD_RX.search(t[:120])
        if m:
            if cur is not None:
                out.append((cur, " ".join(buf[:OPENING_NODES])))
            cur = m.group(1)
            buf = []
        if cur is not None:
            buf.append(t)
    if cur is not None:
        out.append((cur, " ".join(buf[:OPENING_NODES])))
    return out


# Read by hand and kept (2026-09-11): the prose disagrees and the mood is
# the CHOICE. Death arrives at 4:06 AM under a warm dawn because the card
# says "the sun rises in the distance"; the painting's cabin is pre-dawn
# under the dawn it is waiting for; booth 6 at 3:47 AM is night and the
# word "morning" in its opening is the diner's all-night shift talking.
DELIBERATE = {
    ("vol5_ch13_death", "dawn_warm"),
    ("vol7_ch14_painting", "dawn_warm"),
    ("vol5_ch0_booth6", "night"),
}


def main():
    show_all = "--all" in sys.argv
    soft = "--soft" in sys.argv          # every hour disagreement, not just light vs dark
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    flagged = 0
    checked = 0
    for dirpath, _d, files in os.walk(SCENES):
        vol = os.path.basename(dirpath)
        if only and vol not in only:
            continue
        for fn in sorted(files):
            if not fn.endswith(".json"):
                continue
            try:
                j = json.load(open(os.path.join(dirpath, fn)))
            except Exception:
                continue
            for mood, prose in passages(j.get("nodes", [])):
                claim = MOOD_HOUR.get(mood)
                if claim is None:
                    continue          # a style, not an hour
                checked += 1
                clocks = clock_hits(prose)
                words = word_hits(prose)
                # a clock beats a word; three of a kind beats one
                tally = collections.Counter(clocks * 3 + words)
                if not tally:
                    continue
                said, n = tally.most_common(1)[0]
                mine = tally.get(claim, 0)
                if n < 2:
                    continue          # one word in three lines is not a clock
                # A mood is a LIGHT. morning↔day and dusk↔night are the same
                # light an hour apart; only light-against-dark is a mood that
                # lies. Dusk is the hinge and never contradicts anything.
                lit = {"morning": "light", "day": "light", "night": "dark"}
                if not soft and lit.get(said) is not None and lit.get(claim) is not None \
                        and lit[said] == lit[claim]:
                    continue
                if not soft and (lit.get(said) is None or lit.get(claim) is None):
                    continue
                if said == claim or n < mine * 2:
                    if show_all:
                        print("ok      %-28s %-18s prose says %-8s (%d vs %d)"
                              % (fn[:-5], mood, said, n, mine))
                    continue
                if (fn[:-5], mood) in DELIBERATE:
                    continue
                flagged += 1
                ev = ", ".join("%s×%d" % (k, v) for k, v in tally.most_common(3))
                print("MOOD    %-28s [mood:%-16s] prose says %-8s  (%s)"
                      % (fn[:-5], mood + "]", said, ev))
    print("\nmood_clock_audit · %d timed mood cue(s) checked · %d contradicted by the prose"
          % (checked, flagged))


if __name__ == "__main__":
    main()
