extends RefCounted
## PortraitDirector — picks the SHOT for a 3D hero portrait on every line
## (draft 1 · 2026-10-01).
##
## The user, after the recovered heroes landed: "going to need direction
## passes on them, facial/bust close-ups for dialogue, director precedence
## for best shots and psychology of the shots and visual design." Until
## now every hero was framed one way — a three-quarter thigh-up at a
## heroic upward angle — whoever spoke and whatever was said; the Meshy
## models' A-pose arms filled half the frame.
##
## The grammar, and where each rule comes from:
##
##   SIZE — "the size of an object in the frame should equal its
##   importance in the story at that moment" (Hitchcock to Truffaut).
##   Dialogue lives in the medium close-up — the coverage default of
##   every shot/reverse-shot scene since the studio era — and pushes in
##   as the line's charge rises: close-up for feeling, extreme close-up
##   for the turn (Leone's eyes, Bergman's faces). Narration rests on
##   the bust; nothing automatic goes wider than the medium close-up
##   (the generated models stand in A-pose — the arms are not a shot).
##
##   LISTENER — the reaction shot is a size WIDER than the speaker's
##   (coverage practice: the scene's weight sits on whoever talks; the
##   listener is context), never tighter than the speaker, never wider
##   than the bust; CharLayer's dim-and-shrink does the rest.
##
##   ANGLE — eye level is neutral and is the default (Ozu built a whole
##   cinema on the level lens). Low angle grants power (Welles shooting
##   Kane from the floor): used for figures with authority in the story,
##   when they speak hard or level. High angle takes it away: sorrow,
##   exhaustion, hurt. A dutch tilt is unease (The Third Man): nerves,
##   and the demons.
##
##   CONTINUITY — no creeping: a shot changes by a whole size or not at
##   all; a speaker who keeps talking at the same pitch holds the frame
##   (the 30° / jump-cut rule, applied to size). After a peak the shot
##   breathes back out ONE step a line, not all at once.
##
##   LENS — longer lenses for closer shots (the portrait photographer's
##   85-135 mm): faces flatten kindly and the background drops away.
##   Portrait3D maps each size to its own field of view.
##
## A writer's [portrait:…] directive on the line wins over all of it.

const SIZES := ["wide", "medium", "mcu", "cu", "ecu"]

# Figures whose word carries weight in their scenes — the low angle is
# theirs when they speak level or hard. Keyed by hero GLB basename.
const AUTHORITY := {
	"quentin_paul": true, "dante_dambrosio": true, "dickens_dean": true,
	"vince_kane": true, "chief_miller": true, "tanya_horne": true,
	"coach_guidry": true, "coach_k": true, "judge_halverson": true,
	"erica_campbell": true, "the_demon": true, "father_amato": true,
}

# Models whose face is not a face in an extreme close-up: the Frog's is
# all eye, the Stranger's all hood (sheet 42). The director tops out at
# the close-up for them.
const NO_ECU := {"the_frog": true, "the_stranger": true}

const INTENSE := {"angry": 2, "surprised": 2, "nervous": 1, "sad": 1, "tired": 0, "happy": 0, "neutral": 0, "demon_chaos": 2}
const VULNERABLE := {"sad": true, "tired": true}
const UNEASY := {"nervous": true, "demon_chaos": true}


static func size_index(size: String) -> int:
	return SIZES.find(size)


## How charged the line is: the mood, then what the text itself does.
static func intensity(mood: String, text: String) -> int:
	var score: int = int(INTENSE.get(mood, 0))
	var t: String = text.strip_edges()
	var bangs: int = t.count("!")
	if bangs > 0:
		score += 1
	if t.contains("…") or t.contains("..."):
		score += 1                      # hesitation is intimate
	var words: int = t.split(" ", false).size()
	if words > 0 and words <= 6 and score >= 2:
		score += 1                      # the short hard line: the punch
	return score


## ctx: role ("speaker" | "listener" | "narration"), mood, text,
## glb (basename), prev_size, prev_score, same_speaker (bool: this
## character also spoke the previous line), speaker_size (for a
## listener), override ({size, angle} from a [portrait:] directive).
## Returns {size, angle, why}.
static func choose(ctx: Dictionary) -> Dictionary:
	var role: String = String(ctx.get("role", "speaker"))
	var mood: String = String(ctx.get("mood", "neutral"))
	var glb: String = String(ctx.get("glb", ""))
	var ov: Dictionary = ctx.get("override", {})
	if not ov.is_empty() and role == "speaker":
		return {"size": String(ov.get("size", "mcu")), "angle": String(ov.get("angle", "eye")), "why": "directive"}
	# The floor is the medium close-up: wider frames show the generated
	# models' A-pose arms (the Deck screenshot, 2026-10-01). Wide and
	# medium stay available to a writer's [portrait:] directive.
	if role == "narration":
		return {"size": "mcu", "angle": "eye", "why": "narration rests on the bust"}
	if role == "listener":
		var si: int = size_index(String(ctx.get("speaker_size", "mcu")))
		var li: int = clampi(si - 1, size_index("mcu"), size_index("cu"))
		return {"size": SIZES[li], "angle": "eye", "why": "reaction, a size wider than the speaker"}
	# the speaker
	var score: int = intensity(mood, String(ctx.get("text", "")))
	var want: int = size_index("mcu")
	if score >= 3:
		want = size_index("ecu")
	elif score >= 1:
		want = size_index("cu")
	var prev: int = size_index(String(ctx.get("prev_size", "")))
	var why: String = "dialogue single"
	if bool(ctx.get("same_speaker", false)) and prev >= 0:
		var prev_score: int = int(ctx.get("prev_score", 0))
		if want < prev:
			want = prev - 1             # breathe out one step a line
			why = "breathing back out"
		elif want == prev or score == prev_score:
			want = prev                 # same pitch holds the frame
			why = "holding"
		else:
			why = "pushing in"
	elif score >= 1:
		why = "charged line"
	if want == size_index("ecu") and NO_ECU.has(glb):
		want = size_index("cu")
	var angle: String = "eye"
	if UNEASY.has(mood):
		angle = "dutch"
	elif VULNERABLE.has(mood):
		angle = "high"
	elif AUTHORITY.has(glb) and (mood == "neutral" or mood == "angry"):
		angle = "low"
	return {"size": SIZES[want], "angle": angle, "why": why, "score": score}


## "[portrait:cu]", "[portrait:ecu low]", "[portrait:medium dutch]".
static func parse_override(arg: String) -> Dictionary:
	var out: Dictionary = {}
	for tok_v: Variant in arg.to_lower().split(" ", false):
		var tok: String = String(tok_v)
		if SIZES.has(tok):
			out["size"] = tok
		elif tok in ["eye", "low", "high", "dutch"]:
			out["angle"] = tok
	return out
