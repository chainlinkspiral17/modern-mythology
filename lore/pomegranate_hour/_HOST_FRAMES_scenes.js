// THE POMEGRANATE HOUR · host frames as dialogue-tool scenes
//
// Format matches vol5/vol6 chapter scenes in project/vn-scenes.jsx.
// 44 scenes: 22 intros (ph_s01eXX_intro) + 22 outros (ph_s01eXX_outro).
// Each frame chains forward via { t: 'jump', scene: '<next>' } so the
// host frames can be walked as a sequence by the HTML tool, or each
// can be invoked standalone.
//
// Narration (`t: 'narrate'`) is Elicia (stage direction is hers).
// Spoken lines (`t: 'say', char: 'Elicia'`) are her on-air voice.
// Character expression `veiled` is the cassette-tape veil persona.
// Backgrounds + bgm are placeholder paths the tool can re-resolve.

export const scenes = {

  // ──────────────────────────────────────────────────────────────────
  // 0 — THE FOOL
  // ──────────────────────────────────────────────────────────────────

  ph_s01e00_intro: {
    id: 'ph_s01e00_intro', vol: 'pomegranate_hour', episode: 0, type: 'host_intro',
    title: 'INTRO — 0 — THE FOOL',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_tower_exterior_night.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/ph_60hz_hum.mp3' },
      { t: 'interlude', text: 'THE POMEGRANATE HOUR', sub: "0 — THE FOOL · 'the boy who couldn't remember which diner'", duration: 3000 },
      { t: 'narrate', text: "Exterior. The radio tower at night. Two red FAA warning lights blinking in slow alternation. A small lit room at the tower's top." },
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'narrate', text: "Interior. The booth. Elicia at the console, the cassette-tape veil falling to her chest. Her hands rest at the board's edge." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "A diner. A morning. A waiter who has been carrying the same tray for so long that he has stopped feeling its weight, and a young man with a pressed wildflower in his wallet he cannot account for." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The tarot's Fool, in the painted card, steps toward a cliff with his face to the sun. In our chapter, he sits in a booth and tries to remember the name of a place he has never quite arrived at. The menu, you'll find, is from somewhere else. The dog, watching from across the road, has not been given a name yet." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Submitted for your attention: the chapter of the first morning, in which the only thing missing from the diner is the diner's own name." },
      { t: 'jump', scene: 'ph_s01e00_episode' }
    ]
  },

  ph_s01e00_outro: {
    id: 'ph_s01e00_outro', vol: 'pomegranate_hour', episode: 0, type: 'host_outro',
    title: 'OUTRO — 0 — THE FOOL',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'narrate', text: 'Back to the booth. Elicia at the console.' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "He drank the coffee that was poured for him without his having to ask. He took the napkin with the small drawing of a cup whose steam loops back into itself. He left the wildflower on the table for the next arrival." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The clock continued to read 9:09. The dog continued to sit." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Beginnings, our chapter has suggested, are not events. They are the small inventories we take before the doors close softly behind us." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The chapter has been held." },
      { t: 'narrate', text: 'Slow pull-back through the booth window. The tower recedes. The warning lights, smaller. Black.' },
      { t: 'hide', pos: 'center' },
      { t: 'jump', scene: 'ph_s01e01_intro' }
    ]
  },

  // ──────────────────────────────────────────────────────────────────
  // I — THE MAGICIAN
  // ──────────────────────────────────────────────────────────────────

  ph_s01e01_intro: {
    id: 'ph_s01e01_intro', vol: 'pomegranate_hour', episode: 1, type: 'host_intro',
    title: 'INTRO — I — THE MAGICIAN',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_tower_exterior_night.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/ph_60hz_hum.mp3' },
      { t: 'interlude', text: 'THE POMEGRANATE HOUR', sub: "I — THE MAGICIAN · 'the trace'", duration: 3000 },
      { t: 'narrate', text: "Exterior. The tower. The warning lights. The booth's small lit window." },
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "An empty office building at three in the morning. A maintenance contractor named Jim with a clipboard, a voltage detector, and a lunchbox marked PROPERTY OF HALSEY FARM. A hum at a pitch the engineering schematics do not account for." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The Magician, in the painted card, draws power from the air. Our chapter offers a small revision: sometimes the power draws back. Sometimes the chassis you find at the end of the hum is not on any circuit you can read with a meter, and yet is warm. Sometimes it knows your name." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Submitted for your attention: the chapter of the trace, in which the man with the clipboard discovers that what he was looking for has been looking for him." },
      { t: 'jump', scene: 'ph_s01e01_episode' }
    ]
  },

  ph_s01e01_outro: {
    id: 'ph_s01e01_outro', vol: 'pomegranate_hour', episode: 1, type: 'host_outro',
    title: 'OUTRO — I — THE MAGICIAN',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The building has since been demolished. The chassis was taken away by a vendor who did not give his name. The foundation, at the southwest corner where the basement server room used to be, has subsided. The subsidence is in the chassis's footprint." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Jim continues his maintenance route on a different block. He carries a different lunchbox now. The new one is empty." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The chapter has been held." },
      { t: 'narrate', text: 'Pull back through the booth window. The tower, the lights, the dark scrub.' },
      { t: 'hide', pos: 'center' },
      { t: 'jump', scene: 'ph_s01e02_intro' }
    ]
  },

  // ──────────────────────────────────────────────────────────────────
  // II — THE HIGH PRIESTESS
  // ──────────────────────────────────────────────────────────────────

  ph_s01e02_intro: {
    id: 'ph_s01e02_intro', vol: 'pomegranate_hour', episode: 2, type: 'host_intro',
    title: 'INTRO — II — THE HIGH PRIESTESS',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_tower_exterior_night.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/ph_60hz_hum.mp3' },
      { t: 'interlude', text: 'THE POMEGRANATE HOUR', sub: "II — THE HIGH PRIESTESS · 'tape 11'", duration: 3000 },
      { t: 'narrate', text: 'Exterior. The tower. The warning lights.' },
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "A woman, alone in an archive, watches a tape of herself watching a tape." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The Priestess, on her card, guards the door between what is known and what waits behind a veil. In our chapter, she does not guard the door. She is the door. She is also, by some arithmetic the chapter does not resolve, the visitor." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "A note, in her own hand, has been on her desk for two years. She does not remember writing it. The note's instructions are clear. We will, in the next twenty minutes, watch her consider following them." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Submitted for your attention: the chapter of the woman who is, somehow, both the page and the reader." },
      { t: 'jump', scene: 'ph_s01e02_episode' }
    ]
  },

  ph_s01e02_outro: {
    id: 'ph_s01e02_outro', vol: 'pomegranate_hour', episode: 2, type: 'host_outro',
    title: 'OUTRO — II — THE HIGH PRIESTESS',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The cards on the tape did not change. They will not change the next time, or the next." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The Priestess card, in the deck I keep here at the booth, sits in its sleeve unconsulted. I have not asked it for a reading in eleven years. I have decided that some questions are better not asked at the door." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The chapter has been held." },
      { t: 'narrate', text: 'Pull back. Black.' },
      { t: 'hide', pos: 'center' },
      { t: 'jump', scene: 'ph_s01e03_intro' }
    ]
  },

  // ──────────────────────────────────────────────────────────────────
  // III — THE EMPRESS
  // ──────────────────────────────────────────────────────────────────

  ph_s01e03_intro: {
    id: 'ph_s01e03_intro', vol: 'pomegranate_hour', episode: 3, type: 'host_intro',
    title: 'INTRO — III — THE EMPRESS',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_tower_exterior_night.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/ph_60hz_hum.mp3' },
      { t: 'interlude', text: 'THE POMEGRANATE HOUR', sub: "III — THE EMPRESS · 'the garden under the floor'", duration: 3000 },
      { t: 'narrate', text: 'Exterior. The tower at night.' },
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "A model home in a planned community. A Victorian floor plan. A maximalist parlor. A woman, heavily pregnant, who has been pregnant — by her own account — for some thirty-four years." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Outsider artists know the rule that other people sometimes forget: the work is not what you make. The work is what you tend. The Empress, in our chapter, has been tending a small chamber beneath her kitchen floorboard for a long time. The chamber's depth is, on a tape measure, fourteen inches. The chamber's depth, to the eye, is much more." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Submitted for your attention: the chapter of the woman who has refused to let the deck finish what she did not get to finish herself." },
      { t: 'jump', scene: 'ph_s01e03_episode' }
    ]
  },

  ph_s01e03_outro: {
    id: 'ph_s01e03_outro', vol: 'pomegranate_hour', episode: 3, type: 'host_outro',
    title: 'OUTRO — III — THE EMPRESS',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The figure beneath the kitchen floorboard remains where it is. Its stitched mouth has opened a fraction since filming. Its stitched eyes have not closed." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Somebody, every month, pays the utility bills on the model home. The staging team has not returned. The wreath, you'll find later, comes from a hand the chapter has not yet named for you." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The chapter has been held." },
      { t: 'narrate', text: 'Pull back. Black.' },
      { t: 'hide', pos: 'center' },
      { t: 'jump', scene: 'ph_s01e04_intro' }
    ]
  },

  // ──────────────────────────────────────────────────────────────────
  // IV — THE EMPEROR
  // ──────────────────────────────────────────────────────────────────

  ph_s01e04_intro: {
    id: 'ph_s01e04_intro', vol: 'pomegranate_hour', episode: 4, type: 'host_intro',
    title: 'INTRO — IV — THE EMPEROR',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_tower_exterior_night.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/ph_60hz_hum.mp3' },
      { t: 'interlude', text: 'THE POMEGRANATE HOUR', sub: "IV — THE EMPEROR · 'the chairman at the bbq'", duration: 3000 },
      { t: 'narrate', text: 'Exterior. The tower at night.' },
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "A patio. A grill. A retired man in a Creole-restaurant apron from 1970, working slowly at a fire he is the only one who will eat from. The kitchen table he was raised at has been reset for twelve, and twelve are coming, and none of them will lift a fork." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The Emperor, in his painted card, holds the throne. In our chapter, he holds the tongs. He holds them well. He holds them as a man holds something he is not certain he has permission to put down." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Submitted for your attention: the chapter of the chairman whose empire began as a small fine-dining restaurant in a parish whose name nobody uses now." },
      { t: 'jump', scene: 'ph_s01e04_episode' }
    ]
  },

  ph_s01e04_outro: {
    id: 'ph_s01e04_outro', vol: 'pomegranate_hour', episode: 4, type: 'host_outro',
    title: 'OUTRO — IV — THE EMPEROR',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The meal was not eaten. The guests took the dishes home cold. The chairman ate one of the steaks the next morning off a paper plate. Hélène took the étouffée. The patio remembered." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Authority, our chapter has suggested, is sometimes the discipline of setting a table you do not expect to share." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The chapter has been held." },
      { t: 'narrate', text: 'Pull back. Black.' },
      { t: 'hide', pos: 'center' },
      { t: 'jump', scene: 'ph_s01e05_intro' }
    ]
  },

  // ──────────────────────────────────────────────────────────────────
  // V — THE HIEROPHANT
  // ──────────────────────────────────────────────────────────────────

  ph_s01e05_intro: {
    id: 'ph_s01e05_intro', vol: 'pomegranate_hour', episode: 5, type: 'host_intro',
    title: 'INTRO — V — THE HIEROPHANT',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_tower_exterior_night.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/ph_60hz_hum.mp3' },
      { t: 'interlude', text: 'THE POMEGRANATE HOUR', sub: "V — THE HIEROPHANT · 'father on cable'", duration: 3000 },
      { t: 'narrate', text: 'Exterior. The tower.' },
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "A converted feed store on a back road in Westport, Louisiana. A studio camera. A telephone with a long curled cord. A priest who has been answering the same call from the same caller every Tuesday and Thursday for nineteen years." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The Hierophant, in his painted card, sits in robes between two kneelers. In our chapter, he sits in a black shirt and a starched collar and takes calls from people whose names are not in any directory. He says the same nine words to one of them every time. We will, this evening, find out what the tenth word would have been." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Submitted for your attention: the chapter of the public access show, the locked door, and the gentleman from Beaumont." },
      { t: 'jump', scene: 'ph_s01e05_episode' }
    ]
  },

  ph_s01e05_outro: {
    id: 'ph_s01e05_outro', vol: 'pomegranate_hour', episode: 5, type: 'host_outro',
    title: 'OUTRO — V — THE HIEROPHANT',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The line was hung up three times. The door, we are told, is still locked. The black pickup on the gravel shoulder drove off in the opposite direction the priest drove home." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Faith, our chapter has suggested, is sometimes the labor of keeping a number in service whether or not anyone is going to call." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The chapter has been held." },
      { t: 'narrate', text: 'Pull back. Black.' },
      { t: 'hide', pos: 'center' },
      { t: 'jump', scene: 'ph_s01e06_intro' }
    ]
  },

  // ──────────────────────────────────────────────────────────────────
  // VI — THE LOVERS
  // ──────────────────────────────────────────────────────────────────

  ph_s01e06_intro: {
    id: 'ph_s01e06_intro', vol: 'pomegranate_hour', episode: 6, type: 'host_intro',
    title: 'INTRO — VI — THE LOVERS',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_tower_exterior_night.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/ph_60hz_hum.mp3' },
      { t: 'interlude', text: 'THE POMEGRANATE HOUR', sub: "VI — THE LOVERS · 'the cousin at the wedding'", duration: 3000 },
      { t: 'narrate', text: 'Exterior. The tower.' },
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "A wedding hall. Four hundred and thirteen guests. Two kitchens — Acadian and Vietnamese — that have, over the course of eleven years of courtship, learned each other's sauces. Two cousins at a back table who have been writing each other one letter every nineteen months for as long as they have been adults, by a postal route they did not design." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The Lovers, in their painted card, stand beneath an angel. In our chapter, they sit across an empty chair. The chair is the chapter's third lover. The boats on the altars at the head of the room are the chapter's fourth." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Submitted for your attention: the chapter of the long patient love that does not require romance and the candle that stayed lit." },
      { t: 'jump', scene: 'ph_s01e06_episode' }
    ]
  },

  ph_s01e06_outro: {
    id: 'ph_s01e06_outro', vol: 'pomegranate_hour', episode: 6, type: 'host_outro',
    title: 'OUTRO — VI — THE LOVERS',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The cousins exchanged the tapes. The basket-boats drifted to the pond's far shore. The bride and groom danced. Anya, who could not come, was named once by a four-year-old at the table and named, again, by the boats themselves on the water." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Love, our chapter has suggested, is sometimes the discipline of holding the seat for the person who could not be in it." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The chapter has been held." },
      { t: 'narrate', text: 'Pull back. Black.' },
      { t: 'hide', pos: 'center' },
      { t: 'jump', scene: 'ph_s01e07_intro' }
    ]
  },

  // ──────────────────────────────────────────────────────────────────
  // VII — THE CHARIOT
  // ──────────────────────────────────────────────────────────────────

  ph_s01e07_intro: {
    id: 'ph_s01e07_intro', vol: 'pomegranate_hour', episode: 7, type: 'host_intro',
    title: 'INTRO — VII — THE CHARIOT',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_tower_exterior_night.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/ph_60hz_hum.mp3' },
      { t: 'interlude', text: 'THE POMEGRANATE HOUR', sub: "VII — THE CHARIOT · 'the black pickup'", duration: 3000 },
      { t: 'narrate', text: 'Exterior. The tower.' },
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "A black pickup truck with Louisiana plates. A two-lane state highway. A passenger seat. Forty-three minutes of patient following, edited here to twenty-two. A wrist with a faded band of skin where a watch was recently removed." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The Chariot, in its painted card, advances with two horses, one black and one white, in opposite directions. In our chapter, the chariot does the perimeter of a planned community, four times, and our camera follows for three of them, and then our driver — not me — decides she has gone around in enough circles for one Thursday evening." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Submitted for your attention: the chapter of the long-take dread, the iteration, and the side-mirror." },
      { t: 'jump', scene: 'ph_s01e07_episode' }
    ]
  },

  ph_s01e07_outro: {
    id: 'ph_s01e07_outro', vol: 'pomegranate_hour', episode: 7, type: 'host_outro',
    title: 'OUTRO — VII — THE CHARIOT',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The pickup continued without us into the curve. The driver, we have not named. The wrist, we have not identified." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Motion, our chapter has suggested, is sometimes the discipline of going in a circle whose center we have decided not to look at directly." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The chapter has been held." },
      { t: 'narrate', text: 'Pull back. Black.' },
      { t: 'hide', pos: 'center' },
      { t: 'jump', scene: 'ph_s01e08_intro' }
    ]
  },

  // ──────────────────────────────────────────────────────────────────
  // VIII — STRENGTH
  // ──────────────────────────────────────────────────────────────────

  ph_s01e08_intro: {
    id: 'ph_s01e08_intro', vol: 'pomegranate_hour', episode: 8, type: 'host_intro',
    title: 'INTRO — VIII — STRENGTH',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_tower_exterior_night.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/ph_60hz_hum.mp3' },
      { t: 'interlude', text: 'THE POMEGRANATE HOUR', sub: "VIII — STRENGTH · 'the woman at the fence'", duration: 3000 },
      { t: 'narrate', text: 'Exterior. The tower.' },
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "A chain-link fence at the back of a planned-community lot. A bowl of food. A woman in a brown work coat. A stray dog that three adjacent counties have been photographing for nine years, by various names, none of which she uses." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Strength, in the painted card, is a bare hand on a hot lion's jaw. In our chapter, strength is a bare hand offering food through the wire on eleven consecutive evenings, the eleventh of which is the evening the dog does not arrive, and the woman waits anyway, and changes the offering to three pomegranate seeds in a saucer set inside the fence, for whatever the field decides is hungry tonight." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Submitted for your attention: the chapter of the gentle hand and the absent recipient." },
      { t: 'jump', scene: 'ph_s01e08_episode' }
    ]
  },

  ph_s01e08_outro: {
    id: 'ph_s01e08_outro', vol: 'pomegranate_hour', episode: 8, type: 'host_outro',
    title: 'OUTRO — VIII — STRENGTH',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The saucer was gone by 8:21 PM. The dog was sighted, two weeks later, at a different fence in a different development. The woman has not been seen feeding any animal at any fence since. She has, however, been seen with the saucer in her own yard." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Strength, our chapter has suggested, is sometimes the willingness to keep the offering going past the recipient." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The chapter has been held." },
      { t: 'narrate', text: 'Pull back. Black.' },
      { t: 'hide', pos: 'center' },
      { t: 'jump', scene: 'ph_s01e09_intro' }
    ]
  },

  // ──────────────────────────────────────────────────────────────────
  // IX — THE HERMIT
  // ──────────────────────────────────────────────────────────────────

  ph_s01e09_intro: {
    id: 'ph_s01e09_intro', vol: 'pomegranate_hour', episode: 9, type: 'host_intro',
    title: 'INTRO — IX — THE HERMIT',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_tower_exterior_night.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/ph_60hz_hum.mp3' },
      { t: 'interlude', text: 'THE POMEGRANATE HOUR', sub: "IX — THE HERMIT · 'one lantern, no audience'", duration: 3000 },
      { t: 'narrate', text: 'Exterior. The tower.' },
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "A back parish road in lower Westport. A six-sided lantern with one cracked panel. A woman in an eighteenth-century Acadian dress, walking a road her grandmother walked and her grandmother's grandmother walked." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Longfellow's Evangeline is, you may remember, the founding text of the Acadian diaspora. It is also, if you read it carefully and at the right hour, a horror poem. A woman walks for thirty-three years, looking for a man who has been displaced on a different boat to a different place, and finds him only as he is dying." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Submitted for your attention: the chapter of the walker whose grandmother carried this same lantern at this same hour on a much earlier night, in 1979, on the Gulf, when a piece of debris cracked the panel and the panel was not replaced." },
      { t: 'jump', scene: 'ph_s01e09_episode' }
    ]
  },

  ph_s01e09_outro: {
    id: 'ph_s01e09_outro', vol: 'pomegranate_hour', episode: 9, type: 'host_outro',
    title: 'OUTRO — IX — THE HERMIT',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "She walked the road five times, as her grandmother taught her. She stopped, on the fifth pass, in front of the camera for nine seconds, raised her hand briefly to her sternum, and walked on." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Solitude, our chapter has suggested, is sometimes the chosen form of an inheritance that was not chosen." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The chapter has been held." },
      { t: 'narrate', text: 'Pull back. Black.' },
      { t: 'hide', pos: 'center' },
      { t: 'jump', scene: 'ph_s01e10_intro' }
    ]
  },

  // ──────────────────────────────────────────────────────────────────
  // X — THE WHEEL OF FORTUNE
  // ──────────────────────────────────────────────────────────────────

  ph_s01e10_intro: {
    id: 'ph_s01e10_intro', vol: 'pomegranate_hour', episode: 10, type: 'host_intro',
    title: 'INTRO — X — THE WHEEL OF FORTUNE',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_tower_exterior_night.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/ph_60hz_hum.mp3' },
      { t: 'interlude', text: 'THE POMEGRANATE HOUR', sub: "X — THE WHEEL OF FORTUNE · 'the phone tree'", duration: 3000 },
      { t: 'narrate', text: 'Exterior. The tower.' },
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Eleven phone calls, on one Saturday night, between the hours of eleven PM and five AM, placed by me, in person, from eleven separate phone booths, to eleven separate residences across two states." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The question I asked was the same question. The question is not in the recording. What you will hear, and see, is what the eleven called parties answered. The answer, in each case, after due consideration, was yes." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The Wheel, in its painted card, turns. The Wheel, in our chapter, has hands. Fortune, you will discover, is not chance. Fortune is a phone tree someone is dialing. Each yes is its own small consent." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Submitted for your attention: the chapter of the tree." },
      { t: 'jump', scene: 'ph_s01e10_episode' }
    ]
  },

  ph_s01e10_outro: {
    id: 'ph_s01e10_outro', vol: 'pomegranate_hour', episode: 10, type: 'host_outro',
    title: 'OUTRO — X — THE WHEEL OF FORTUNE',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Eleven yeses. One night. One question. One phone tree." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Fortune, our chapter has suggested, is the consent we give before we have finished comprehending what we have been asked." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The eleventh room, you will have noticed, was the room I cannot account for. The receiver lifted itself. The voice was a child's. The child laughed." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The chapter has been held." },
      { t: 'narrate', text: 'Pull back. Black.' },
      { t: 'hide', pos: 'center' },
      { t: 'jump', scene: 'ph_s01e11_intro' }
    ]
  },

  // ──────────────────────────────────────────────────────────────────
  // XI — JUSTICE
  // ──────────────────────────────────────────────────────────────────

  ph_s01e11_intro: {
    id: 'ph_s01e11_intro', vol: 'pomegranate_hour', episode: 11, type: 'host_intro',
    title: 'INTRO — XI — JUSTICE',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_tower_exterior_night.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/ph_60hz_hum.mp3' },
      { t: 'interlude', text: 'THE POMEGRANATE HOUR', sub: "XI — JUSTICE · 'deposition room b'", duration: 3000 },
      { t: 'narrate', text: 'Exterior. The tower.' },
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "A small law office in a Harmony Creek strip mall, between the Sally Beauty and the Great Clips. A solo-practitioner attorney named Erica Campbell, in on a Sunday for an unrelated filing. A deposition-room audio console that has, for the first time in her tenure, activated on its own." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The console contains the audio of a deposition that has not yet been conducted, in a matter not yet opened, of a witness not yet sworn. The voice asking the questions is, in some sense, the attorney's own — slightly older, slightly more tired, considerably kinder." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Justice, in her painted card, holds a scale and a sword. In our chapter, she holds a stenotype machine and the patience to transcribe what she will need to say four years from now." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Submitted for your attention: the chapter in which the records precede the trials." },
      { t: 'jump', scene: 'ph_s01e11_episode' }
    ]
  },

  ph_s01e11_outro: {
    id: 'ph_s01e11_outro', vol: 'pomegranate_hour', episode: 11, type: 'host_outro',
    title: 'OUTRO — XI — JUSTICE',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The cassettes were filed. The cabinet was seeded. The seal in the unnumbered cabinet — P interlocked with H — remains to be identified." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Justice, our chapter has suggested, is sometimes the rehearsal a person performs in private of the gentleness she intends to bring to a room she has not yet entered." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The chapter has been held." },
      { t: 'narrate', text: 'Pull back. Black.' },
      { t: 'hide', pos: 'center' },
      { t: 'jump', scene: 'ph_s01e12_intro' }
    ]
  },

  // ──────────────────────────────────────────────────────────────────
  // XII — THE HANGED MAN
  // ──────────────────────────────────────────────────────────────────

  ph_s01e12_intro: {
    id: 'ph_s01e12_intro', vol: 'pomegranate_hour', episode: 12, type: 'host_intro',
    title: 'INTRO — XII — THE HANGED MAN',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_tower_exterior_night.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/ph_60hz_hum.mp3' },
      { t: 'interlude', text: 'THE POMEGRANATE HOUR', sub: "XII — THE HANGED MAN · 'the vigil'", duration: 3000 },
      { t: 'narrate', text: 'Exterior. The tower.' },
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "A small studio apartment. A coffee table. A maroon-backed tarot deck that arrived in a brown envelope eleven years ago, with no return address, postmarked from Beaumont. A single white pillar candle. A transistor radio on a shortwave carrier between stations." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The cards keep coming up the same. The Hanged Man. The Moon. The Star. The woman in the chair has been shuffling for two hours and the cards have refused to organize any other way." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The Hanged Man, in his painted card, hangs upside-down by one foot. In our chapter, he is the chapter the deck is holding. The woman is not the deck. The woman is its reader." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Submitted for your attention: the chapter of the vigil, the candle, and the wall above the kitchen counter." },
      { t: 'jump', scene: 'ph_s01e12_episode' }
    ]
  },

  ph_s01e12_outro: {
    id: 'ph_s01e12_outro', vol: 'pomegranate_hour', episode: 12, type: 'host_outro',
    title: 'OUTRO — XII — THE HANGED MAN',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The cards did not change. The candle, on the back of three of them, were marked by a hand we will name in another chapter." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Suspension, our chapter has suggested, is not punishment. It is sometimes the chapter's gentlest acknowledgment that the room you are in is the room you are in." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The chapter has been held." },
      { t: 'narrate', text: 'Pull back. Black.' },
      { t: 'hide', pos: 'center' },
      { t: 'jump', scene: 'ph_s01e13_intro' }
    ]
  },

  // ──────────────────────────────────────────────────────────────────
  // XIII — DEATH
  // ──────────────────────────────────────────────────────────────────

  ph_s01e13_intro: {
    id: 'ph_s01e13_intro', vol: 'pomegranate_hour', episode: 13, type: 'host_intro',
    title: 'INTRO — XIII — DEATH',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_tower_exterior_night.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/ph_60hz_hum.mp3' },
      { t: 'interlude', text: 'THE POMEGRANATE HOUR', sub: "XIII — DEATH · 'ward c'", duration: 3000 },
      { t: 'narrate', text: 'Exterior. The tower.' },
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "A hospital ward at three in the morning. Six beds, four occupied, two empty. A night nurse with eleven years on the floor and a small altar at her station, lit by one stick of incense and refreshed on her shift's hourly rounds." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Death, in its painted card, rides a white horse across a field of fallen kings. In our chapter, death is a small arithmetic performed quietly between the hours of three and four. Two have gone tonight. Four remain. The count is the count." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The wandering souls, where the night nurse comes from, are called cô hồn. They are fed rice. Tonight they will be fed rice. The chapter is the chapter of the rice." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Submitted for your attention: the chapter of the count, the incense, and the gentle reading aloud of those who have just gone." },
      { t: 'jump', scene: 'ph_s01e13_episode' }
    ]
  },

  ph_s01e13_outro: {
    id: 'ph_s01e13_outro', vol: 'pomegranate_hour', episode: 13, type: 'host_outro',
    title: 'OUTRO — XIII — DEATH',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The incense bent toward the empty doorway at fifty-eight seconds after the nurse left her station. The rice was set. The names were spoken. The night continues." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Death, our chapter has suggested, is sometimes the small work of accurate gentleness. If you are hungry, eat the rice. If you have already eaten, go in peace." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The chapter has been held." },
      { t: 'narrate', text: 'Pull back. Black.' },
      { t: 'hide', pos: 'center' },
      { t: 'jump', scene: 'ph_s01e14_intro' }
    ]
  },

  // ──────────────────────────────────────────────────────────────────
  // XIV — TEMPERANCE
  // ──────────────────────────────────────────────────────────────────

  ph_s01e14_intro: {
    id: 'ph_s01e14_intro', vol: 'pomegranate_hour', episode: 14, type: 'host_intro',
    title: 'INTRO — XIV — TEMPERANCE',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_tower_exterior_night.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/ph_60hz_hum.mp3' },
      { t: 'interlude', text: 'THE POMEGRANATE HOUR', sub: "XIV — TEMPERANCE · 'two cups'", duration: 3000 },
      { t: 'narrate', text: 'Exterior. The tower.' },
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "A small kitchen-and-living room in the southern arm of a planned-community professional district. A square oak table. Two mugs. One contains cold black morning coffee. The other contains warm chamomile and a small spoonful of Halsey wildflower honey. A man in a soft grey shirt, sixty-three years old, sitting between them." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Temperance, in her painted card, pours water from a vessel in her right hand to a vessel in her left, balancing the two. In our chapter, the pour has not happened. The man has been sitting between the two cups for forty Tuesday afternoons a year for forty years. He places his hands beside each mug the way one would place a hand on the shoulder of a friend sitting down beside them." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Submitted for your attention: the chapter of the moderate temperature of Tuesday." },
      { t: 'jump', scene: 'ph_s01e14_episode' }
    ]
  },

  ph_s01e14_outro: {
    id: 'ph_s01e14_outro', vol: 'pomegranate_hour', episode: 14, type: 'host_outro',
    title: 'OUTRO — XIV — TEMPERANCE',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "He drank the chamomile. He poured the cold coffee down the drain. He wrote one line in his notebook. He set the pencil across the napkin." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Moderation, our chapter has suggested, is the discipline of being a person who can sit between two states without collapsing toward either." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The chapter has been held." },
      { t: 'narrate', text: 'Pull back. Black.' },
      { t: 'hide', pos: 'center' },
      { t: 'jump', scene: 'ph_s01e15_intro' }
    ]
  },

  // ──────────────────────────────────────────────────────────────────
  // XV — THE DEVIL
  // ──────────────────────────────────────────────────────────────────

  ph_s01e15_intro: {
    id: 'ph_s01e15_intro', vol: 'pomegranate_hour', episode: 15, type: 'host_intro',
    title: 'INTRO — XV — THE DEVIL',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_tower_exterior_night.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/ph_60hz_hum.mp3' },
      { t: 'interlude', text: 'THE POMEGRANATE HOUR', sub: "XV — THE DEVIL · 'the HOA meeting'", duration: 3000 },
      { t: 'narrate', text: 'Exterior. The tower.' },
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The Harmony Creek Estates Homeowners' Association, Tuesday evening, in the multipurpose room of the clubhouse on Linden. A welcome table with twenty-four jars of complimentary Halsey wildflower honey, one per household. A noise complaint from Lot 47. A board that has not, in eleven years, recorded a non-unanimous vote." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The Devil, in his painted card, sits on a stone block with two figures chained at its base. In our chapter, the Devil is the contract the room is signing without articulating. The chain is the chain of voluntary participation in a community that requires, of its members, the silencing of certain sounds." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Three young men have wandered in from out of town. One of them will, before the night is out, take three jars by signing his name three times." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Submitted for your attention: the chapter of the meeting." },
      { t: 'jump', scene: 'ph_s01e15_episode' }
    ]
  },

  ph_s01e15_outro: {
    id: 'ph_s01e15_outro', vol: 'pomegranate_hour', episode: 15, type: 'host_outro',
    title: 'OUTRO — XV — THE DEVIL',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The vote was unanimous. The matter was silenced. The map of highlighted lots, on closer inspection, traced a corridor from the south of the development to the eastern fence of Halsey's wildflower meadow." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Contracts, our chapter has suggested, are sometimes the things we sign by accepting what the welcome table offers. The rule was always negotiable." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The chapter has been held." },
      { t: 'narrate', text: 'Pull back. Black.' },
      { t: 'hide', pos: 'center' },
      { t: 'jump', scene: 'ph_s01e16_intro' }
    ]
  },

  // ──────────────────────────────────────────────────────────────────
  // XVI — THE TOWER
  // ──────────────────────────────────────────────────────────────────

  ph_s01e16_intro: {
    id: 'ph_s01e16_intro', vol: 'pomegranate_hour', episode: 16, type: 'host_intro',
    title: 'INTRO — XVI — THE TOWER',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_tower_exterior_night.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/ph_60hz_hum.mp3' },
      { t: 'interlude', text: 'THE POMEGRANATE HOUR', sub: "XVI — THE TOWER · 'the collapse of the water tower'", duration: 3000 },
      { t: 'narrate', text: 'Exterior. The tower.' },
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Seven amateur cameras, by chance, were rolling within sight of the Natchitoches Parish auxiliary water tower at nine-oh-nine on a Thursday morning. The footage agrees on nine seconds of collapse. The footage does not agree on what those nine seconds contained." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The Tower, in its painted card, is struck by lightning, with figures falling from its windows. In our chapter, the tower is not the chapter. The tower is the cover story." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "What is in the tower, what came down inside the cover of the falling, and who came to drive up from a French Quarter venue at the same hour to recognize her when she returned — that is the chapter." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Submitted for your attention: the chapter of the eighth camera." },
      { t: 'jump', scene: 'ph_s01e16_episode' }
    ]
  },

  ph_s01e16_outro: {
    id: 'ph_s01e16_outro', vol: 'pomegranate_hour', episode: 16, type: 'host_outro',
    title: 'OUTRO — XVI — THE TOWER',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The girl came home safe. The Evergreen Company drove her to their venue and gave her tea and a chair and a binder. The binder gained, that night, the chapter's contribution: the deeper amber is the return." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Collapse, our chapter has suggested, is sometimes the thing that has to happen on the outside so that something else can finish happening on the inside." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The chapter has been held." },
      { t: 'narrate', text: 'Pull back. Black.' },
      { t: 'hide', pos: 'center' },
      { t: 'jump', scene: 'ph_s01e17_intro' }
    ]
  },

  // ──────────────────────────────────────────────────────────────────
  // XVII — THE STAR
  // ──────────────────────────────────────────────────────────────────

  ph_s01e17_intro: {
    id: 'ph_s01e17_intro', vol: 'pomegranate_hour', episode: 17, type: 'host_intro',
    title: 'INTRO — XVII — THE STAR',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_tower_exterior_night.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/ph_60hz_hum.mp3' },
      { t: 'interlude', text: 'THE POMEGRANATE HOUR', sub: "XVII — THE STAR · 'the river offering'", duration: 3000 },
      { t: 'narrate', text: 'Exterior. The tower.' },
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "A riverbank, at night, in the lower parishes. Eight stars overhead. A woman in a brown coat, alone, with two clay vessels. The stones are flat. The current is even. The camera, on the opposite bank, is in a blind she does not know is there." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The Star, in her painted card, pours water from two vessels by the light of one bright star and seven smaller ones. In our chapter, she has been performing the same offering for four consecutive years. The vessels' inner rims, which the camera cannot read at this distance, are inscribed plus-four and dash. She knows which is which without looking." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Submitted for your attention: the chapter of the offering conducted without permission, witnessed without thanks, and received by the river without comment." },
      { t: 'jump', scene: 'ph_s01e17_episode' }
    ]
  },

  ph_s01e17_outro: {
    id: 'ph_s01e17_outro', vol: 'pomegranate_hour', episode: 17, type: 'host_outro',
    title: 'OUTRO — XVII — THE STAR',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The eight rings on the river matched the eight stars overhead. The long ring on the second pour drifted downstream and did not disperse. The dash signature was made by the woman's thumbnail. She walked home the north road. The blind on the opposite bank she has, so far as I can tell, never noticed." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Hope, our chapter has suggested, is sometimes the residue of an act already completed by someone whose name we have agreed not to use." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The chapter has been held." },
      { t: 'narrate', text: 'Pull back. Black.' },
      { t: 'hide', pos: 'center' },
      { t: 'jump', scene: 'ph_s01e18_intro' }
    ]
  },

  // ──────────────────────────────────────────────────────────────────
  // XVIII — THE MOON
  // ──────────────────────────────────────────────────────────────────

  ph_s01e18_intro: {
    id: 'ph_s01e18_intro', vol: 'pomegranate_hour', episode: 18, type: 'host_intro',
    title: 'INTRO — XVIII — THE MOON',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_tower_exterior_night.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/ph_60hz_hum.mp3' },
      { t: 'interlude', text: 'THE POMEGRANATE HOUR', sub: "XVIII — THE MOON · 'static'", duration: 3000 },
      { t: 'narrate', text: 'Exterior. The tower.' },
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "A small upstairs apartment in Mauriceville, Texas. Fourteen miles west of the Sabine. A CRT television showing static. A transistor radio tuned to the WUFR pirate carrier between AM stations. A second carrier, riding 1.7 kilohertz above the first, pulsing every nine minutes." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The Moon, in her painted card, illuminates a path between two towers, with a dog and a wolf howling beneath. In our chapter, the moon is the medium-between, and the medium-between is broadcasting, and the broadcast resolves into handwriting in your own hand if you bring your face within eight inches of the screen." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Submitted for your attention: the chapter of the medium, the kettle, and the network of one hundred and forty attentive people across Texas and Louisiana and the lower delta who keep, in their own kitchens, the broadcasts the licensed stations do not carry." },
      { t: 'jump', scene: 'ph_s01e18_episode' }
    ]
  },

  ph_s01e18_outro: {
    id: 'ph_s01e18_outro', vol: 'pomegranate_hour', episode: 18, type: 'host_outro',
    title: 'OUTRO — XVIII — THE MOON',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The medium signed off. The kettle whistled. Three weeks later, a letter from a sixteen-year-old in Belle Chasse arrived under the door without a stamp, by a postal route the medium routes itself." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Illusion, our chapter has suggested, is sometimes only the word the unrouted use for what the routed receive in their own hand." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The chapter has been held." },
      { t: 'narrate', text: 'Pull back. Black.' },
      { t: 'hide', pos: 'center' },
      { t: 'jump', scene: 'ph_s01e19_intro' }
    ]
  },

  // ──────────────────────────────────────────────────────────────────
  // XIX — THE SUN
  // ──────────────────────────────────────────────────────────────────

  ph_s01e19_intro: {
    id: 'ph_s01e19_intro', vol: 'pomegranate_hour', episode: 19, type: 'host_intro',
    title: 'INTRO — XIX — THE SUN',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_tower_exterior_night.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/ph_60hz_hum.mp3' },
      { t: 'interlude', text: 'THE POMEGRANATE HOUR', sub: "XIX — THE SUN · 'four motes'", duration: 3000 },
      { t: 'narrate', text: 'Exterior. The tower.' },
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "A small white-walled office on a Saturday morning. An east-facing window. A man at a desk, sixty-three, watching the slant of light. In the slant: four dust motes, consistently four, in the same general arrangement, every Saturday morning for the past eleven years." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The Sun, in his painted card, rises over a walled garden with a child on horseback beneath. In our chapter, the sun is a slant of light through a washed window, and the man at the desk has been counting the small things in the slant until the small things acknowledge that he has been counting." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Today the motes contract. This has not happened before." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Submitted for your attention: the chapter of the count, the phone call, and the four who have begun to find each other." },
      { t: 'jump', scene: 'ph_s01e19_episode' }
    ]
  },

  ph_s01e19_outro: {
    id: 'ph_s01e19_outro', vol: 'pomegranate_hour', episode: 19, type: 'host_outro',
    title: 'OUTRO — XIX — THE SUN',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The motes contracted. The phone call lasted forty-two seconds. Casserole called at 9:21. The four had begun to gather. The fourth will identify herself within the year." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Warmth, our chapter has suggested, is the discipline of paying attention to small things long enough that the small things turn back." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The chapter has been held." },
      { t: 'narrate', text: 'Pull back. Black.' },
      { t: 'hide', pos: 'center' },
      { t: 'jump', scene: 'ph_s01e20_intro' }
    ]
  },

  // ──────────────────────────────────────────────────────────────────
  // XX — JUDGEMENT
  // ──────────────────────────────────────────────────────────────────

  ph_s01e20_intro: {
    id: 'ph_s01e20_intro', vol: 'pomegranate_hour', episode: 20, type: 'host_intro',
    title: 'INTRO — XX — JUDGEMENT',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_tower_exterior_night.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/ph_60hz_hum.mp3' },
      { t: 'interlude', text: 'THE POMEGRANATE HOUR', sub: "XX — JUDGEMENT · 'the ensemble gesture'", duration: 3000 },
      { t: 'narrate', text: 'Exterior. The tower.' },
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "A deconsecrated tabernacle on the back roads east of Westport. Twelve folding chairs in a wide circle. A mason jar of water at the circle's center. Twelve people I have cast on the basis of a private list — twelve survivors of an event that occurred on the Gulf in March of 1979." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Judgement, in its painted card, shows an angel above a field of figures rising from coffins. In our chapter, judgement is the chapter of the gesture they will, in five cycles, learn from each other without speaking. Each will bring one small addition. By the fifth cycle the gesture will have thirteen components instead of the original four." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Submitted for your attention: the chapter of the call." },
      { t: 'jump', scene: 'ph_s01e20_episode' }
    ]
  },

  ph_s01e20_outro: {
    id: 'ph_s01e20_outro', vol: 'pomegranate_hour', episode: 20, type: 'host_outro',
    title: 'OUTRO — XX — JUDGEMENT',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "They performed the gesture once together. They lowered their hands. They agreed it will travel. They have not performed it on any subsequent camera. They have, however, been recognized at small crossings by strangers who had begun, on their own, to perform it." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Call, our chapter has suggested, is sometimes the small work twelve people do quietly in a deconsecrated tabernacle while the rest of the world is at lunch." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The chapter has been held." },
      { t: 'narrate', text: 'Pull back. Black.' },
      { t: 'hide', pos: 'center' },
      { t: 'jump', scene: 'ph_s01e21_intro' }
    ]
  },

  // ──────────────────────────────────────────────────────────────────
  // XXI — THE WORLD (season closer)
  // ──────────────────────────────────────────────────────────────────

  ph_s01e21_intro: {
    id: 'ph_s01e21_intro', vol: 'pomegranate_hour', episode: 21, type: 'host_intro',
    title: 'INTRO — XXI — THE WORLD',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_tower_exterior_night.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/ph_60hz_hum_cypress.mp3' },
      { t: 'interlude', text: 'THE POMEGRANATE HOUR', sub: "XXI — THE WORLD · 'the swamp park' · season finale", duration: 3000 },
      { t: 'narrate', text: "Exterior. The tower. The two warning lights blink alternately. Beyond the tower, to the east, the silver of a Louisiana coastal dawn." },
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "A defunct Cajun-themed family park sixteen acres on Highway 90 west of Houma, Louisiana. Closed since 2003. Held in trust by a small parish foundation that has, since its founding, quietly hosted exactly one feral child at a time, between the ages of seven and twelve, until each child is ready to leave." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The current child is eight. Her name is Marelle. She has built her nest in the gift shop. She rides a bicycle on the cracked promenade. She knows the projector." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The World, in her painted card, dances at the center of four creatures within a wreath. In our chapter, the four creatures are the procession of every chapter that has come before, projected as holograms by a 1981 Fresnel rig that has not been powered by any human hand since 2003. The child sits in the second ring of seats. She listens. She is the world that will be." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Submitted for your attention: our final chapter — the world that has come before, and the world that will be, and the giant frog at the center who has been waiting for her in the lagoon." },
      { t: 'jump', scene: 'ph_s01e21_episode' }
    ]
  },

  ph_s01e21_outro: {
    id: 'ph_s01e21_outro', vol: 'pomegranate_hour', episode: 21, type: 'host_outro',
    title: 'OUTRO — XXI — THE WORLD',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_sedan_highway_dusk.jpg' },
      { t: 'narrate', text: "A small grey sedan on Highway 90 northbound. Late dusk. Elicia at the wheel — without the veil. Her face, for the first and only time in the series, is bare. Marelle in the passenger seat, the tin lunchbox on her lap, her backpack between her feet, the cassette inside the lunchbox." },
      { t: 'bg', src: 'assets/backgrounds/ph_booth_interior.jpg' },
      { t: 'show', char: 'elicia', expr: 'veiled', pos: 'center' },
      { t: 'narrate', text: "And: a later night at the booth. Elicia in the veil. Behind her, in the steel rack, a third unlabeled unit — the chassis — breathes at fourteen breaths per minute, slightly faster than usual." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The void mother delivered her chapter from the platform. Hélène taught the trinity by feel. Anya spoke from the boat. Father told her what doors are for. The wedding arbor lit two basket-boats. The dash pour was honored. The Triumvirate offered her the jars. The Evergreen Company kept a chair. The chairman performed the gesture in silence. The night nurse lifted the rice. Frank smiled. I appeared, briefly, as my own hologram on a platform at the back of the park, and signed her off." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "Then Grenouille rose. The frog the size of a small car at the lagoon's center. She told him she will go. He gave her the cassette in her name. She walked through the gap in the fence onto Highway 90. I picked her up in my sedan. She is in the passenger seat. The kettle, in Mauriceville, is on." },
      { t: 'narrate', text: "Elicia raises her right hand. Slowly. From the console to the level of her veil-covered eye. She holds. She lowers it to the level of her heart. She holds. She raises both hands briefly at the level of her stomach — palms up — for a single beat. She lowers them. She performs the gesture once. She is wearing the gesture." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "I am Elicia Duchane. I have hosted twenty-two chapters. The chapter has been held. The chapter is also open. There is room at the door. There is, in particular, room at the table I am setting tomorrow morning for the ninth child the chapter has decided to give me." },
      { t: 'say', char: 'Elicia', expr: 'veiled', text: "The chapter has been held." },
      { t: 'narrate', text: "Slow pull-back through the booth window. The tower recedes. The two warning lights, smaller. Beyond the tower, the dawn is becoming proper morning. Black." },
      { t: 'hide', pos: 'center' },
      { t: 'jump', scene: 'ph_series_end' }
    ]
  },

  // ──────────────────────────────────────────────────────────────────
  // SERIES END (terminal scene, no further jump)
  // ──────────────────────────────────────────────────────────────────

  ph_series_end: {
    id: 'ph_series_end', vol: 'pomegranate_hour', episode: 22, type: 'series_end',
    title: 'THE POMEGRANATE HOUR · SEASON 1 · END',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/ph_tower_exterior_dawn.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/ph_closing_chord.mp3' },
      { t: 'interlude', text: 'a pomegranate hour · veil.tv', sub: 'the host does not speak, by choice — except, once, at the close.', duration: 5000 },
      { t: 'narrate', text: "The wreath was the door's last courtesy. The door is open. There is room at the door. The chapter has been held." },
      { t: 'narrate', text: "The season closes here. The medium will continue to broadcast. The medium will continue to route the letters. The kettle is still on. — Elicia Duchane" }
    ]
  }

};

export default scenes;
