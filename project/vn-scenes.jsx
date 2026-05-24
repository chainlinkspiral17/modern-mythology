// vn-scenes.jsx — Demo scene content for Modern Mythology volumes
// Scene node types: narrate, say, think, choice, show, hide, bg, bgm, sfx, flag, jump, end
// goto: node index | scene id string
// Node types also include:
//   interlude — full-screen atmospheric text moment, no dialogue box
//   gallery   — opens Gallery.html (optionally at a specific tab/item)
//   cg        — shows a full-screen CG illustration with optional caption
// Export: DEMO_SCENES (object keyed by vol number)

// ── Unlock helper ──────────────────────────────────────────────────────────
// Call unlock('flag_key') from scene nodes to unlock gallery items.
// Flags persist across saves and are read by Gallery.html.
function unlockItem(key) {
  try {
    const saves = JSON.parse(localStorage.getItem('mm_saves') || '[]');
    const updated = saves.map(s => ({ ...s, flags: { ...(s.flags || {}), [key]: true } }));
    if (updated.length === 0) {
      // No saves yet — write a standalone unlock record
      localStorage.setItem('mm_saves', JSON.stringify([{ slot: 'auto', flags: { [key]: true } }]));
    } else {
      localStorage.setItem('mm_saves', JSON.stringify(updated));
    }
  } catch {}
}

const DEMO_SCENES = {

  // ── Vol 1 · MODERN MYTHOLOGY · Literary skin ────────────────────────────

  // Title page — copyright matter, the front of the book.
  vol1_title: {
    id: 'vol1_title', vol: 1, chapter: 0, type: 'chapter',
    title: 'Title Page',
    nodes: [
      { t: 'bg', src: null },
      { t: 'narrate', text: 'modern mythology.' },
      { t: 'narrate', text: 'a fiction by andy link' },
      { t: 'narrate', text: 'copyright 2010. andy link all rights reserved. any part of this publication may be reproduced, or transmitted by voice, light, thought and matter across time and space through any medium physical, temporal and/or philosophical dimension by express permission of the copyright holder.' },
      { t: 'narrate', text: 'names and places of real people are used with the express intent of entertaining an audience in a fictional capacity. any confusion with reality is your own damn fault. any characters, real or otherwise, harmed in the act of creation are the sole responsibility of andy link.' },
      { t: 'narrate', text: 'any emotions you feel as a result of this fiction are wholly yours to own and contemplate. any works inspired by modern mythology are going to be loved by modern mythology as the works that inspired modern mythology are loved.' },
      { t: 'narrate', text: 'any bastard fictional children or offspring are entirely in the care of their individual creators. andy link accepts only the creations herein as his own, or as determined by a paternity test.' },
      { t: 'narrate', text: 'this digital second edition is special to the few who find and cherish it. share it how you will, as it may change because change is coming and there\u2019s nothing you can do to stop it.' },
      { t: 'narrate', text: 'fly not fall.' },
      { t: 'narrate', text: 'a chainlink spiral production of a oneironautics endeavor in so so cool productions' },
      { t: 'narrate', text: 'modern mythology.' },
      { t: 'jump', scene: 'vol1_introduction' },
    ]
  },

  // Introduction — the four players (Writer, Artist, Human Being, Director)
  // and the Fool argue themselves into beginning.
  vol1_introduction: {
    id: 'vol1_introduction', vol: 1, chapter: 0, type: 'chapter',
    title: 'Introduction',
    nodes: [
      { t: 'bg', src: null },
      { t: 'narrate', text: 'Introduction.' },
      { t: 'say', char: 'The Writer', expr: 'neutral', text: '(nervously) A moment ago I was debating whether or not to begin and here I am starting something I should never finish.' },
      { t: 'say', char: 'The Artist', expr: 'neutral', text: '(comfortable) There comes a time in life when pieces click in place good and bad chambers of existence line up just so showing both the way and every single misstep ever taken specifically on purpose pressed in prehistoric mud so long gone yet still to come for ancestor gawkers to stumble cross centuries later and find mute satisfaction' },
      { t: 'say', char: 'The Human Being', expr: 'neutral', text: '(sitting with a book) The days gone by dry up crackle and flake.' },
      { t: 'say', char: 'The Artist', expr: 'neutral', text: '(obsessive) I scrub my kitchen learning textures of surface — peel back what used to be. A late-life thirst for me; finally recognized mine own contribution to grime and soil accumulates just under sight.' },
      { t: 'say', char: 'The Human Being', expr: 'neutral', text: '(drunk sick and hugging the toilet) I was put here for reasons perhaps to leave prints etch an owned existence into this second-hand tapestry.' },
      { t: 'say', char: 'The Writer', expr: 'neutral', text: 'Maybe I have a reason to\u2014' },
      { t: 'say', char: 'The Artist', expr: 'neutral', text: 'To?' },
      { t: 'say', char: 'The Human Being', expr: 'neutral', text: '\u2014To be.' },
      { t: 'say', char: 'The Artist', expr: 'neutral', text: '(playing video games) Sin accounted for washed up from having borrowed so much against a name that means little — much last living male branch — should fashion a wand from that.' },
      { t: 'say', char: 'The Human Being', expr: 'neutral', text: '(dressing in a waiter\u2019s uniform) I hold Link in highest esteem worn with certain pride, to pay back and then some (father\u2019s) hand\u2014somely.' },
      { t: 'say', char: 'The Writer', expr: 'neutral', text: '(in a cafe with friends drinking chai) But what I know about myself is an utter fiction fabricated by myself and others to make this new reality come to pass.' },
      { t: 'narrate', text: 'Cut to: The Players celebrating, wrapping up their success.' },
      { t: 'say', char: 'The Artist', expr: 'neutral', text: '(toasting them) A conspiracy of beautiful dreamers yet a conspiracy no less.' },
      { t: 'say', char: 'A Player', expr: 'neutral', text: 'At least we\u2019re upfront.' },
      { t: 'say', char: 'The Human Being', expr: 'neutral', text: '(making tamales, with flashes to:) I work towards the good if such a term gives any meaning \u2014true\u2014 to you certainly me but my good a construct of culture a childhood of cartoons video games movies comic books sports nature library books travel friendships rivalries all with fierce science-fiction clarity.' },
      { t: 'narrate', text: 'Images of various cultural stepping-stones and highlights. George Lucas, Jim Henson, et all.' },
      { t: 'say', char: 'The Writer', expr: 'neutral', text: '(waiting in line for a movie) A beautiful mythology built just for me — hired hands and artisans giving upon dreams to birth collective dreams within dreams.' },
      { t: 'say', char: 'DD', expr: 'neutral', text: '(standing in line) All so very meta.' },
      { t: 'say', char: 'The Human Being', expr: 'neutral', text: '(writing a letter) To all: Sorry for my protracted childhood and adolescence still doing my best to make up for it.' },
      { t: 'say', char: 'The Writer', expr: 'neutral', text: 'Teachers taught me well enough. I loved them most like second parents.' },
      { t: 'say', char: 'The Director', expr: 'neutral', text: 'I always hurt my tutors by never being good enough for failing when they had so much invested in me at just that crucial moment.' },
      { t: 'say', char: 'The Human Being', expr: 'neutral', text: 'I saw our futures I choked to them I apologize \u2014 all that on me.' },
      { t: 'say', char: 'The Director', expr: 'neutral', text: 'They gave so much and hoped I could give back so little.' },
      { t: 'say', char: 'The Human Being', expr: 'neutral', text: 'Things taught to me by them left-handed unusual very tall big feet bright and kind.' },
      { t: 'say', char: 'The Director', expr: 'neutral', text: 'This is unusual.' },
      { t: 'say', char: 'The Writer', expr: 'neutral', text: 'Everything about me looking back seemed unusual.' },
      { t: 'say', char: 'The Human Being', expr: 'neutral', text: 'In both the majority and minority of who I was and who I was.' },
      { t: 'say', char: 'The Director', expr: 'neutral', text: 'I don\u2019t know what I\u2019ve become \u2014 just know that I am.' },
      { t: 'say', char: 'The Human Being', expr: 'neutral', text: 'I am a nerd that needs looking after. I have lovely friends and family. I try to repay their love.' },
      { t: 'say', char: 'The Artist', expr: 'neutral', text: 'But I slip in small ways I gaze off into far corners of things lose myself at the world inside my head' },
      { t: 'say', char: 'The Human Being', expr: 'neutral', text: 'I fear how I function when left like this.' },
      { t: 'say', char: 'The Director', expr: 'neutral', text: 'My father just like me in such different ways.' },
      { t: 'say', char: 'The Human Being', expr: 'neutral', text: 'The hardest thing about losing him was becoming him.' },
      { t: 'say', char: 'The Artist', expr: 'neutral', text: 'Self-doubt would have crippled me \u2014 instead ordered chaos electric statics and storm booted this operating system this great battle whir clicking inside me accelerates something crushing something so damned high I lose myself in art find beauty in friendship family found eternal connection in everyday existence.' },
      { t: 'say', char: 'The Director', expr: 'neutral', text: 'Can\u2019t unsee what\u2019s seen \u2014 not to bemoan I try to step up and carry that weight.' },
      { t: 'narrate', text: 'TEXT: Every day you gift yourself so please thank the stars and the moon and the sun \u2014I\u2014 thank you sun and moon and stars.' },
      { t: 'say', char: 'The Writer', expr: 'neutral', text: 'My thanks trickles down rests here on books examined eyestraining existential dread untold delights library books by the armful — transparent clear skinned shrink-wrapped from future tense — tomes of forgotten lore — history repeating itself within fictional allegory — arts and crafts; horrors and hobbies — all books look the same (though good design, hardly lost on me) judging by the cover — fresh new bleached through razor blade pages slick enough \u2014 slit and scar an impressionable age.' },
      { t: 'narrate', text: 'INSERT \u2014 the good kind of hurt: a synesthetic compound of bacon cinnamon buns, sedated cavity-filling smell and taste of drilled tooth, little-league grand slam compounded by Super Mario Bros. 3 tanooki suit four in the am escapades.' },
      { t: 'say', char: 'The Director', expr: 'neutral', text: 'When we create starting from scratch the mind pauses as if to contemplate its own worthwhile capacity and determine whether or not it is eager for the task.' },
      { t: 'say', char: 'The Human Being', expr: 'neutral', text: 'As it has been with everything come before it will hold true for everything to come.' },
      { t: 'say', char: 'The Writer', expr: 'neutral', text: 'Writing — like any and all creation — is of the present, yet my mind tends to reside not with myself but with my audience in many a hypothetical future tense or deep in the past communing with ancient and long dead voice of genius I see fit to cozy up to — a child auditioning for parental approval, content I am to put words to paper or whatever medium exists to transmit naked thoughts into naked flesh — suppose I stand before you bereft of all but the barest sense of self and purpose.' },
      { t: 'say', char: 'The Artist', expr: 'neutral', text: 'We start from scratch — clothe ourselves in the fabric of history dyed intrinsic with familial blood — stain and sweat of both dignity and shame.' },
      { t: 'jump', scene: 'vol1_interlude_demographic' },
    ]
  },

  // Interlude 1 — target demographic. Internet-meme montage interludes.
  vol1_interlude_demographic: {
    id: 'vol1_interlude_demographic', vol: 1, chapter: 0, type: 'chapter',
    title: 'Interlude 1 — Target Demographic',
    nodes: [
      { t: 'narrate', text: 'interlude 1 \u2014 target demographic' },
      { t: 'narrate', text: 'MONTAGE OF IMAGES, INTERNET MEME-ISH:' },
      { t: 'narrate', text: 'I am the target they want to reach \u2014 their demographic if you will. Disconnected age, so easy it would be to unionize our like-minded culturally significant dopplegangers.' },
      { t: 'narrate', text: 'In others we trust.' },
      { t: 'narrate', text: 'Our individual hopes and fears rest with the many who \u2014 just like us, nothing like us \u2014 divide our selves along so many lines where does one allegiance begin another entwined frayed end.' },
      { t: 'narrate', text: 'How strong our convictions, we pardon bare comfort passion forfeit in due processed manufactured winter closed for. Church bells rage on the hour glorious to earhold several blocks away.' },
      { t: 'narrate', text: 'INFOGRAPHIC: Taste in music defined as follows \u2014 a mix of genres, an arrow through personal experience running parallel but never intersecting the dissemination of good times along an all right quotidian.' },
      { t: 'narrate', text: 'OR: Today is Sunday. I worship the Sun, or at least pause in place to firmly address with a hand and a squint the Sun I give a smile and word to, as it is a good Sun.' },
      { t: 'narrate', text: 'AS: I worship many a thing. The state of mind I\u2019ve occupied since earliest memory is of worship \u2014 abject \u2014 live in praise of it all.' },
      { t: 'narrate', text: 'PICTURE AND TEXT \u2014 my first memory: two-dimensional car driving up a storybook hill with sunshining bright behind.' },
      { t: 'narrate', text: 'CRUDE ANIMATION AND VOICE OF CHILD: An old woman asked a young me what is it when I held a ladybug up to the sky. I replied everything. She tried to correct me.' },
      { t: 'say', char: 'The Artist', expr: 'neutral', text: 'I smile on the world always hope that is enough to get me to the next.' },
      { t: 'say', char: 'The Writer', expr: 'neutral', text: 'I write to begin something \u2014 the act itself brings about dimension. Every line carries certain candid suspense.' },
      { t: 'say', char: 'The Director', expr: 'neutral', text: 'I want to tell you all about the fictional world to come. If I\u2019m too eager to begin, forgive me \u2014 I\u2019m just excited is all.' },
      { t: 'narrate', text: 'DISCLAIMER: within this filmed textual experience \u2014 a pseudo-documented journey deemed worthy of your attention. Pick and choose to believe what you will. You are both the audience and not.' },
      { t: 'say', char: 'Voice Over', expr: 'neutral', text: '(weak) I try to be heard so please hear me. Ba\u2014 my voice is getting through.' },
      { t: 'say', char: 'The Human Being', expr: 'neutral', text: 'There were many paths before. I selfishly wanted to be \u2014 do everything.' },
      { t: 'say', char: 'The Director', expr: 'neutral', text: 'Parents indulged the dreamer and here I am enacting great schemes.' },
      { t: 'say', char: 'The Writer', expr: 'neutral', text: 'I always wanted to write. Never wanted to be a Writer.' },
      { t: 'jump', scene: 'vol1_trailer_faust3' },
    ]
  },

  // Trailer for FAUST 3 — the project the players are building toward.
  vol1_trailer_faust3: {
    id: 'vol1_trailer_faust3', vol: 1, chapter: 0, type: 'chapter',
    title: 'Trailer — FAUST 3',
    nodes: [
      { t: 'narrate', text: 'A TRAILER FOR A COMING ATTRACTION:' },
      { t: 'say', char: 'The Human Being', expr: 'neutral', text: 'Reading Goethe\u2019s Faust in the tub, smoking judiciously the last of my reefer, peeling back foiled squares of holiday fudge \u2014 I realize I must concoct mine own interpretation.' },
      { t: 'say', char: 'The Writer', expr: 'neutral', text: 'I will write a post-modern screenplay full of playful update, cultural significance \u2014 it will do what all good sequel reboots do.' },
      { t: 'say', char: 'The Director', expr: 'neutral', text: 'Here be the Internet as player, the spy cam as eye of fate, the indie emo wiccan soothsayer post-industrialized world we live in.' },
      { t: 'say', char: 'The Writer', expr: 'neutral', text: 'I will rename Mephistopheles \u2014 Dickens Dean. And Satan \u2014 Antagonist.' },
      { t: 'say', char: 'The Director', expr: 'neutral', text: 'Cast myself and friends as in-player parts and summon post-production magic.' },
      { t: 'narrate', text: 'CUE TITLE TEXT: FAUST 3' },
      { t: 'say', char: 'The Human Being', expr: 'neutral', text: 'Keep the name. It is universal. Timeless.' },
      { t: 'say', char: 'The Director', expr: 'neutral', text: 'Shoot the intimate on iphone and digital cameras, and as the world expands make significant beauty in HD.' },
      { t: 'say', char: 'The Human Being', expr: 'neutral', text: 'It hurts to think this play has already started and I just now realize it must be completed.' },
      { t: 'say', char: 'The Writer', expr: 'neutral', text: 'I could never be Goethe \u2014 can just be me and let he himself shine through.' },
      { t: 'say', char: 'The Fool', expr: 'neutral', text: 'Faust I could play myself \u2014 as did he.' },
      { t: 'jump', scene: 'vol1_prelude_editing_suite' },
    ]
  },

  // Prelude in the editing suite — the players talk themselves into starting.
  vol1_prelude_editing_suite: {
    id: 'vol1_prelude_editing_suite', vol: 1, chapter: 0, type: 'chapter',
    title: 'Prelude in the Editing Suite',
    nodes: [
      { t: 'narrate', text: 'PRELUDE IN THE EDITING SUITE' },
      { t: 'say', char: 'The Director', expr: 'neutral', text: 'You two who have been here since the beginning \u2014 why even start if all we dare dream to do is break-even in this marginal marketplace?' },
      { t: 'say', char: 'The Human Being', expr: 'neutral', text: 'What do you mean start? Where in time are you looking?' },
      { t: 'say', char: 'The Director', expr: 'neutral', text: 'From you, the writer, they expect something they have always known but never witnessed \u2014 brought forth from your inner eye and rendered by myself and others to tickle their wicked fantasy.' },
      { t: 'say', char: 'The Writer', expr: 'neutral', text: 'We know our audience \u2014 cultured in good reads if not great literature, tenured instead in a random sampling must-see tv. Flicks, movies, film, cinema swallowed up whole. Tunes as beating hearts and emotional anchor. Games to explore from all sides and angles in astonishment. Doing shit on the regular and finding humor in it all.' },
      { t: 'say', char: 'The Director', expr: 'neutral', text: 'They expect the finest things rendered explicit \u2014 and I count myself among them. (nerding out) The Trilogies on repeat. My nerdcore is in truth scrapwork \u2014 an old faded fallen-to-love quilt for but the latest of stories, descend from the greatest of stories, a pantheon of classics writ into collected skin bound together illustrated man.' },
      { t: 'say', char: 'The Human Being', expr: 'neutral', text: 'You may bang at those doors to get but a glimpse other side \u2014 all swell and good \u2014 but know there are other worlds than these.' },
      { t: 'say', char: 'The Writer', expr: 'neutral', text: 'To find an audience for this Frankenstein thing beyond mad.' },
      { t: 'say', char: 'The Human Being', expr: 'neutral', text: 'When we started was it not fear of fame that kept us running towards failure.' },
      { t: 'say', char: 'The Director', expr: 'neutral', text: 'The crowds we might attract might utterly destroy us if not compromise everything we\u2019re working towards.' },
      { t: 'narrate', text: 'The three sigh.' },
      { t: 'say', char: 'The Writer', expr: 'neutral', text: 'Can\u2019t we just sit here and think a minute.' },
      { t: 'say', char: 'The Director', expr: 'neutral', text: 'It is in silence mind races and eye truly sees.' },
      { t: 'say', char: 'The Human Being', expr: 'neutral', text: 'And all I feel is love for friends and family.' },
      { t: 'narrate', text: 'Enter the FOOL, a disheveled and insane merry prankster.' },
      { t: 'say', char: 'The Fool', expr: 'neutral', text: 'All the questions you\u2019ve asked yourself you\u2019ve answered yourself \u2014 so to answer your question (pointing at each) no, you\u2019re just afraid, you\u2019re just a pussy. Within you is power. Make something awesome, understandable, and good \u2014 simply good \u2014 that transcends all expectation. So permission to go nuts, absolutely batshit crazy, as long as you\u2019re having a good time we\u2019re having a good time.' },
      { t: 'say', char: 'The Director', expr: 'neutral', text: 'Give this thing a shot in the arm \u2014 can\u2019t feel the pulse here \u2014 amp up the soundtrack, swell their emotions, dim the lights just so, cue flashy credit sequence, lull \u2019em in for the ride to come.' },
      { t: 'say', char: 'The Writer', expr: 'neutral', text: 'Keep things simple. Don\u2019t think for a minute half-way smart patrons won\u2019t notice how much of a hack you truly are.' },
      { t: 'say', char: 'The Director', expr: 'neutral', text: 'Hey now \u2014 I just use the tools that are given. Sometimes it works, sometimes it\u2019s absolute shite \u2014 at least I\u2019m delivering that beautiful dream. So don\u2019t forget what you write is only seen and heard because of my scheme.' },
      { t: 'say', char: 'The Writer', expr: 'neutral', text: 'You cheapen and whore our premature baby to any who\u2019d press up gainst glass to see.' },
      { t: 'say', char: 'The Director', expr: 'neutral', text: 'A fitting if crude analogy \u2014 but unlike you I am proud to call my child perfectly imperfect. All we need really.' },
      { t: 'say', char: 'The Human Being', expr: 'neutral', text: 'Don\u2019t forget \u2014 this is collaboration, plain and simple, sum of the whole not of the part. You three but a small fraction wrapped up in your own short-sighted drama.' },
      { t: 'say', char: 'The Writer', expr: 'neutral', text: 'Agreed. So now we begin?' },
      { t: 'say', char: 'The Director', expr: 'neutral', text: 'hear hear.' },
      { t: 'say', char: 'The Human Being', expr: 'neutral', text: 'Finally.' },
      { t: 'narrate', text: 'The director shrugs and starts the film.' },
      { t: 'jump', scene: 'vol1_missing_link' },
    ]
  },

  // ── Vol 1 · INTERLUDE — The Missing Link ───────────────────────────────────
  // A diner at a bus depot. The Shillelagh shuttle stops once a day. A young
  // man waits at the bench. Limited-interactive hub: each spoke ends with a
  // jump back to vol1_link_hub. Boarding the shuttle ends the interlude.

  vol1_missing_link: {
    id: 'vol1_missing_link', vol: 1, chapter: 1, type: 'interlude',
    title: 'Interlude — The Missing Link',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol1_missing_link_exterior.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/vol1_diner_ambient.mp3' },
      { t: 'interlude', text: 'The Missing Link', sub: 'Bus depot · Rain · No clock', duration: 3000 },

      { t: 'narrate', text: 'The diner is a single rectangle of warm yellow light pinned to a wet asphalt apron. Two gas pumps, one of them retired in place. A sign hand-lettered on enamel — THE MISSING LINK — with the silhouette of a creature halfway between a man and an ape painted beneath the name with what you would have to call affection.' },
      { t: 'narrate', text: 'Beside the diner, under a metal awning, is the depot bench. The Shillelagh stops here once a day. The schedule is taped to the wall behind cracked plexiglass; the rain has crept in along the seams and the only legible word is SHILLELAGH.' },
      { t: 'narrate', text: 'A young man is standing at the bench. He is not sitting on it.' },

      { t: 'show', char: 'trenchcoat', expr: 'neutral', pos: 'right' },
      { t: 'narrate', text: 'His hair is matted flat to his scalp with rain. His face is the pale of skin that has not seen weather for a long while. His trench coat is buttoned to the throat. At the seams of the coat — the cuffs, the lapels, the hem — there is a thin steady light, as if someone had stitched the seams with something hot and forgotten to put it out.' },
      { t: 'narrate', text: 'He has not noticed you. Or he has, and has decided it does not require a response.' },

      { t: 'narrate', text: 'You step in out of the rain.' },
      { t: 'bg', src: 'assets/backgrounds/vol1_missing_link_interior.jpg' },
      { t: 'hide', pos: 'right' },
      { t: 'narrate', text: 'Inside: a counter with five stools, four booths against the front windows, a jukebox in the corner blinking through its red eye. The fluorescents hum in the particular B-flat that fluorescents hum in. The coffee on the burner has been on the burner a while.' },
      { t: 'narrate', text: 'A waitress somewhere — back kitchen, the soft sound of a knife on a board. No one comes out. You have, it seems, some time.' },

      { t: 'jump', scene: 'vol1_link_hub' },
    ]
  },

  vol1_link_hub: {
    id: 'vol1_link_hub', vol: 1, chapter: 1, type: 'interlude',
    title: 'The Missing Link — inside',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol1_missing_link_interior.jpg' },
      { t: 'hide', pos: 'left' }, { t: 'hide', pos: 'center' }, { t: 'hide', pos: 'right' },
      { t: 'choice', opts: [
        { text: 'Look out the rain-glazed window.',          scene: 'vol1_link_window'   },
        { text: 'Read the laminated menu.',                  scene: 'vol1_link_menu'     },
        { text: 'Stand by the jukebox.',                     scene: 'vol1_link_jukebox'  },
        { text: 'Examine the photographs above the booth.',  scene: 'vol1_link_booth'    },
        { text: 'Take a stool at the counter.',              scene: 'vol1_link_counter'  },
        { text: 'Step outside to the bench.',                scene: 'vol1_link_outside'  },
        { text: 'Wait. The bus will come when it comes.',    scene: 'vol1_link_shuttle'  },
      ]},
    ]
  },

  vol1_link_window: {
    id: 'vol1_link_window', vol: 1, chapter: 1, type: 'interlude',
    title: 'The Missing Link — the window',
    nodes: [
      { t: 'narrate', text: 'You stand at the window. The glass is glazed with rain on the outside and breath on the inside. Beyond it, the apron of asphalt, the two pumps, the bench, the awning, the young man.' },
      { t: 'narrate', text: 'He has turned slightly. He is now facing the road that runs past the depot — though there is, at this hour, no road traffic at all. The road goes east into a darkness that has no lights in it for a long way.' },
      { t: 'narrate', text: 'You watch him for a count of breaths. He does not move. The light at the seams of his coat is steady. You begin to suspect he is the source of the warmth you can feel on the glass.' },
      { t: 'narrate', text: 'A moth has gotten in somehow. It is making its small dumb circles around the fluorescent above you, not the warmer thing it can probably sense outside.' },
      { t: 'jump', scene: 'vol1_link_hub' },
    ]
  },

  vol1_link_menu: {
    id: 'vol1_link_menu', vol: 1, chapter: 1, type: 'interlude',
    title: 'The Missing Link — the menu',
    nodes: [
      { t: 'narrate', text: 'The menu is laminated and slightly tacky. It has been hand-typed on a typewriter and photocopied at some point in the last decade or two. The header reads THE MISSING LINK in the same chipped enamel as the sign, and below it, in smaller letters: We have what we have.' },
      { t: 'narrate', text: 'THE FAUST — BLT with extra ham. Named for a regular who has not been in for nine years. Owner will not take it off the menu. $6.50.' },
      { t: 'narrate', text: 'THE PASADENA — fried egg, garlic toast, the hot sauce nobody asks the name of. Listed as For the rocket scientist. $5.' },
      { t: 'narrate', text: 'SMOLVUD TOAST — sourdough, butter, cinnamon. Comes dipped in stout if you ask, no charge for the asking. $3.' },
      { t: 'narrate', text: 'SANDERLING EGGS — two over easy, side of patty sausage, a slice of orange that does not belong on the plate but is always there. $5.50.' },
      { t: 'narrate', text: 'THE CALE — coffee, slow drip, no second cup. $2. The footnote reads: One is enough. Anyone who tells you otherwise is selling.' },
      { t: 'narrate', text: 'BRIAR FALLS PIE — chess pie, served cold. The footnote reads: Aunt Sybil\'s. We do not have the recipe and we do not need it.' },
      { t: 'narrate', text: 'F.T.\'S FLOAT — root beer, a scoop of vanilla, and a single book of matches set on the saucer beside it. $4. The match is not for lighting.' },
      { t: 'narrate', text: 'LAFAYETTE — black coffee. The price line reads: no charge for the coffee, ask the owner about the second cup.' },
      { t: 'narrate', text: 'Below the main menu, separated by a hand-ruled line, a CHILDREN\'S MENU lists exactly one item: A glass of milk and three crackers. The footnote: No charge for the third cracker.' },
      { t: 'narrate', text: 'On the back of the menu, in a different hand and in pencil, somebody has written: If you are reading this and you are alone, the second cup is yours.' },
      { t: 'jump', scene: 'vol1_link_hub' },
    ]
  },

  vol1_link_jukebox: {
    id: 'vol1_link_jukebox', vol: 1, chapter: 1, type: 'interlude',
    title: 'The Missing Link — the jukebox',
    nodes: [
      { t: 'narrate', text: 'The jukebox is a Wurlitzer of the wrong vintage to be in a diner this size. The selection wheel sticks at K and again at S. The card behind the glass has been hand-typed on the same typewriter as the menu and has been corrected, in pencil, more than once.' },
      { t: 'narrate', text: 'A-04 — Burzum — Det Som Engang Var. Marked WAGNER\'S, underlined twice.' },
      { t: 'narrate', text: 'B-11 — Faust (the band, the Krautrock one) — The Faust Tapes, side B. The label says: not the regular.' },
      { t: 'narrate', text: 'C-07 — John Cale — Paris 1919. Pencilled note: ask the owner before playing C-07.' },
      { t: 'narrate', text: 'D-02 — A song listed only as SHILLELAGH. No artist. No B-side. The card says, in someone\'s handwriting: Plays once a day. Has been playing for longer than the jukebox.' },
      { t: 'narrate', text: 'E-09 — Patsy Cline — Crazy. Three pencilled crosses beside the title; you cannot tell whether they are marking the song as favored or warning you off.' },
      { t: 'narrate', text: 'You put a finger to the glass. The selection wheel is warm. There is no coin slot.' },
      { t: 'jump', scene: 'vol1_link_hub' },
    ]
  },

  vol1_link_booth: {
    id: 'vol1_link_booth', vol: 1, chapter: 1, type: 'interlude',
    title: 'The Missing Link — the photographs',
    nodes: [
      { t: 'narrate', text: 'The booth in the corner has a wall of framed photographs above it. None of them are labeled. None of them are recent. All of them are square.' },
      { t: 'narrate', text: 'A man in his sixties at the edge of a forest, holding a wooden frame the size of a doorway. The frame has nothing in it. He is smiling like he has just put something down for the first time in a long while.' },
      { t: 'narrate', text: 'A young woman seated at a bar, late forties light, a drink half-finished and a paperback face-down. The paperback\'s title is not visible. The bar is one you do not recognize and yet feel you have stood in.' },
      { t: 'narrate', text: 'A boy of fourteen or fifteen at a workbench. His hands are out of focus because they are in motion. There is a soldering iron and what looks, at this distance, like the back of a computer that should not exist in the year the photograph was taken.' },
      { t: 'narrate', text: 'A sanderling — the small shorebird — painted on a mural on the side of a brick building. The mural is intact in the photograph. A square patch of it, fresh white primer, sits at the bottom right, as if someone had begun erasing it and stopped.' },
      { t: 'narrate', text: 'Three children on a flat suburban sidewalk holding bicycles. The middle one is looking up at the camera in a way that suggests she has just figured out who is taking the picture.' },
      { t: 'narrate', text: 'A polaroid, this one, smaller than the others and not in a frame — taped to the wall with brittle tape that has yellowed. A young man in a trench coat at a depot bench. The polaroid was taken in the rain. The seams of the coat are not glowing. They are not yet glowing. The date written in pen along the white border, in someone else\'s hand, is a date that has not happened yet.' },
      { t: 'jump', scene: 'vol1_link_hub' },
    ]
  },

  vol1_link_counter: {
    id: 'vol1_link_counter', vol: 1, chapter: 1, type: 'interlude',
    title: 'The Missing Link — the counter',
    nodes: [
      { t: 'narrate', text: 'You take a stool at the counter. The vinyl is cracked in the way vinyl is always cracked in places like this. The stool spins a half-turn with no effort and stops itself, pointed exactly at the swinging door to the kitchen.' },
      { t: 'narrate', text: 'After a moment the door swings open and an arm comes through and sets a mug down in front of you. The arm withdraws. The door swings shut.' },
      { t: 'narrate', text: 'The mug is white, chipped at the rim, and warm against the pad of your finger when you check. The coffee inside is the exact color you would have asked for if you had been asked.' },
      { t: 'narrate', text: 'A second mug appears, by the same method, a foot to your left. Empty. Right side up. Waiting.' },
      { t: 'narrate', text: 'You drink. The coffee is very good.' },
      { t: 'jump', scene: 'vol1_link_hub' },
    ]
  },

  // ── Outside: the bench, the stranger. Mini-hub with several questions. ────
  vol1_link_outside: {
    id: 'vol1_link_outside', vol: 1, chapter: 1, type: 'interlude',
    title: 'The Missing Link — outside',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol1_shuttle_bench.jpg' },
      { t: 'narrate', text: 'You step back out into the rain. The bell over the door is unsubtle about your leaving. The rain has the steady quality of rain that has been raining for longer than it needs to.' },
      { t: 'show', char: 'trenchcoat', expr: 'neutral', pos: 'center' },
      { t: 'narrate', text: 'He has turned to face you. Not abruptly. As though he had been planning the turn for a while and got to it now. The light at the seams of his coat is closer than you remembered.' },
      { t: 'say', char: 'Stranger', expr: 'neutral', text: '"You came out."' },
      { t: 'narrate', text: 'It is not a question and it is not a greeting. It is a thing he has noted and is letting you hear him note.' },
      { t: 'jump', scene: 'vol1_link_outside_hub' },
    ]
  },

  vol1_link_outside_hub: {
    id: 'vol1_link_outside_hub', vol: 1, chapter: 1, type: 'interlude',
    title: 'The Missing Link — at the bench',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol1_shuttle_bench.jpg' },
      { t: 'show', char: 'trenchcoat', expr: 'neutral', pos: 'center' },
      { t: 'choice', opts: [
        { text: '"Are you waiting for the Shillelagh?"',         scene: 'vol1_link_q_shuttle' },
        { text: '"What\'s your name?"',                           scene: 'vol1_link_q_name'    },
        { text: '"Why does your coat glow at the seams?"',       scene: 'vol1_link_q_coat'    },
        { text: '"Where are you going?"',                         scene: 'vol1_link_q_where'   },
        { text: '"Why aren\'t you cold?"',                        scene: 'vol1_link_q_cold'    },
        { text: '[Step back inside.]',                            scene: 'vol1_link_hub'       },
      ]},
    ]
  },

  vol1_link_q_shuttle: {
    id: 'vol1_link_q_shuttle', vol: 1, chapter: 1, type: 'interlude',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol1_shuttle_bench.jpg' },
      { t: 'show', char: 'trenchcoat', expr: 'neutral', pos: 'center' },
      { t: 'say', char: 'Stranger', expr: 'neutral', text: '"I\'m waiting for the shuttle, yes. The Shillelagh comes through here once and then doesn\'t."' },
      { t: 'say', char: 'Stranger', expr: 'neutral', text: '"It picks you up from the place you have agreed to be picked up from. It puts you down somewhere you have not agreed to anything about. Most people get on it the second time."' },
      { t: 'think', char: null, text: 'You consider asking what the second time is. You do not.' },
      { t: 'jump', scene: 'vol1_link_outside_hub' },
    ]
  },

  vol1_link_q_name: {
    id: 'vol1_link_q_name', vol: 1, chapter: 1, type: 'interlude',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol1_shuttle_bench.jpg' },
      { t: 'show', char: 'trenchcoat', expr: 'neutral', pos: 'center' },
      { t: 'say', char: 'Stranger', expr: 'neutral', text: '"I\'m not exactly named yet. It\'s being kept for me. Somewhere I haven\'t been. By someone who will, when she meets me, decide it on the spot and not be wrong."' },
      { t: 'say', char: 'Stranger', expr: 'neutral', text: '"You can call me whatever you want, for the duration of the rain. It will not stick."' },
      { t: 'think', char: null, text: 'You decide, in the privacy of your head, on a name. He does not flinch. He also does not confirm.' },
      { t: 'jump', scene: 'vol1_link_outside_hub' },
    ]
  },

  vol1_link_q_coat: {
    id: 'vol1_link_q_coat', vol: 1, chapter: 1, type: 'interlude',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol1_shuttle_bench.jpg' },
      { t: 'show', char: 'trenchcoat', expr: 'neutral', pos: 'center' },
      { t: 'narrate', text: 'He looks down at his cuffs, like the question reminded him of something he had been meaning to check.' },
      { t: 'say', char: 'Stranger', expr: 'neutral', text: '"Same as what\'s in you, mostly. Just newer. It hasn\'t learned yet how to be quiet about it."' },
      { t: 'say', char: 'Stranger', expr: 'neutral', text: '"Yours did, once. You probably remember the year. People said you were a bright kid. They meant it the regular way. Then they stopped meaning it the regular way, and you noticed, and you put it away."' },
      { t: 'think', char: null, text: 'You are not sure what year he means. You are not sure he is wrong about it.' },
      { t: 'jump', scene: 'vol1_link_outside_hub' },
    ]
  },

  vol1_link_q_where: {
    id: 'vol1_link_q_where', vol: 1, chapter: 1, type: 'interlude',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol1_shuttle_bench.jpg' },
      { t: 'show', char: 'trenchcoat', expr: 'neutral', pos: 'center' },
      { t: 'say', char: 'Stranger', expr: 'neutral', text: '"A town in the small wood. Up the coast. The kind of place that hasn\'t been written about because the people in it have been busy not writing about it."' },
      { t: 'say', char: 'Stranger', expr: 'neutral', text: '"There\'s a tower on a hill there. Not the one you\'re thinking of. There is one in every story I have walked through and they are not the same tower, except where they are."' },
      { t: 'say', char: 'Stranger', expr: 'neutral', text: '"End of the line, by the way, is a relative concept. You can take a Shillelagh from any line."' },
      { t: 'jump', scene: 'vol1_link_outside_hub' },
    ]
  },

  vol1_link_q_cold: {
    id: 'vol1_link_q_cold', vol: 1, chapter: 1, type: 'interlude',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol1_shuttle_bench.jpg' },
      { t: 'show', char: 'trenchcoat', expr: 'neutral', pos: 'center' },
      { t: 'narrate', text: 'He considers the question, briefly, the way a person considers whether they have left the stove on.' },
      { t: 'say', char: 'Stranger', expr: 'neutral', text: '"I don\'t take temperature the way you do. Mine\'s set, and I haven\'t had the time yet to learn how to feel weather. I\'ll get there. Everyone does. It\'s the second-hardest thing about coming through."' },
      { t: 'think', char: null, text: 'You do not ask what the hardest is. He looks like a person who would, if asked, tell you, and you do not want him to.' },
      { t: 'jump', scene: 'vol1_link_outside_hub' },
    ]
  },

  // ── The Shillelagh arrives. End of interlude. ──────────────────────────────
  vol1_link_shuttle: {
    id: 'vol1_link_shuttle', vol: 1, chapter: 1, type: 'interlude',
    title: 'The Missing Link — the shuttle',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol1_shuttle_bench.jpg' },
      { t: 'hide', pos: 'left' }, { t: 'hide', pos: 'center' }, { t: 'hide', pos: 'right' },
      { t: 'narrate', text: 'You stay where you are. The coffee in the second mug, when you check on it, has, at some point, filled itself. You do not drink it.' },
      { t: 'narrate', text: 'Outside, headlights crawl over the wet asphalt and a shape too large for the apron pulls in, slow, without sound — or with a sound the rain is doing the work of covering. The Shillelagh is a long bus the color of old copper. It has no destination listed in the window. It has no driver visible from inside.' },
      { t: 'narrate', text: 'The doors part. The young man at the bench steps up into the bus. He does not look back. The light at the seams of his coat goes with him into the cabin and dims it a register warmer than the depot lights had been.' },
      { t: 'narrate', text: 'You realize you have been standing.' },
      { t: 'narrate', text: 'The doors do not close.' },

      { t: 'show', char: 'trenchcoat', expr: 'neutral', pos: 'right' },
      { t: 'say', char: 'Stranger', expr: 'neutral', text: '"We have a seat for you. We always do. You don\'t have to take it tonight."' },
      { t: 'hide', pos: 'right' },

      { t: 'choice', opts: [
        { text: '[Step up into the bus.]',           goto: 13 },
        { text: '[Stay on the apron. Watch it go.]', goto: 16 },
      ]},

      // index 13 — board
      { t: 'flag', key: 'vol1_shuttle_boarded', val: true },
      { t: 'narrate', text: 'You step up. The light in the cabin reads you the way a room reads someone who has come home in the middle of a sentence. Nobody asks for fare. The doors close. The Shillelagh pulls away from the depot in the same soundless way it arrived.' },
      { t: 'jump', scene: 'vol1_link_end' },

      // index 16 — stay
      { t: 'flag', key: 'vol1_shuttle_boarded', val: false },
      { t: 'narrate', text: 'You stay. The Shillelagh pulls away the way it came in — slow, soundless, copper. The taillights are not red. They are something on the other side of red that you do not have a word for. The road takes them.' },
      { t: 'narrate', text: 'You stand on the apron in the rain a while longer. Then, eventually, you go in. The second mug is empty again. Or it was always empty. You decide, on balance, that it was always empty.' },
      { t: 'jump', scene: 'vol1_link_end' },
    ]
  },

  vol1_link_end: {
    id: 'vol1_link_end', vol: 1, chapter: 1, type: 'interlude',
    title: 'The Missing Link — end',
    nodes: [
      { t: 'flag', key: 'vol1_missing_link_complete', val: true },
      { t: 'interlude', text: 'End of Interlude', sub: 'The Missing Link', duration: 2400 },
      { t: 'jump', scene: 'vol1_ch2_act_one' },
    ]
  },

  // ── Original Vol 1 Ch 1 demo scenes (orphaned, retained as reference) ──────
  1: {
    id: 'vol1_briar_falls',
    nodes: [
      { t: 'bg', src: null },
      { t: 'bgm', src: 'assets/audio/bgm/vol1_ambient.mp3' },
      { t: 'narrate', text: 'The diner has been here longer than the highway that was supposed to kill it.' },
      { t: 'flag', key: 'vol1_met_stranger', val: true },
      { t: 'narrate', text: 'You found it the way you find things you weren\'t looking for — by being lost enough that a light in a window meant something.' },
      { t: 'show', char: 'stranger', expr: 'neutral', pos: 'center' },
      { t: 'narrate', text: 'The man in the corner booth has been watching you since before you walked in. You\'re reasonably sure of this.' },
      { t: 'say', char: 'Stranger', expr: 'neutral', text: 'You have the look of someone who\'s been told a story their whole life and just now noticed it doesn\'t quite fit.' },
      { t: 'say', char: 'Stranger', expr: 'neutral', text: 'Sit down. I won\'t bite.' },
      { t: 'think', char: null, text: 'Something about the way he said "won\'t" and not "don\'t." A choice, not a habit.' },
      { t: 'choice', opts: [
        { text: 'Sit across from him.', goto: 10 },
        { text: '"I don\'t know you."', goto: 13 },
        { text: '[EMPATHY] Something in his voice makes you feel seen. Uncomfortably so.', check: { skill: 'empathy', diff: 7 }, pass: 16, fail: 13 },
      ]},
      // Branch A: sit down
      { t: 'narrate', text: 'You sit. The vinyl is cold. The coffee, when it appears, is exactly the temperature you needed.' },
      { t: 'say', char: 'Stranger', expr: 'warm', text: 'Good. That\'s the first right thing you\'ve done today.' },
      { t: 'say', char: 'Stranger', expr: 'warm', text: 'I\'m going to tell you something about yourself. You can stop me at any point. Most people do.' },
      { t: 'jump', scene: 'vol1_ch1_s2' },
      // Branch B: push back
      { t: 'say', char: 'Stranger', expr: 'amused', text: 'That\'s true. And yet here you are, still standing at my table instead of walking away.' },
      { t: 'say', char: 'Stranger', expr: 'amused', text: 'You don\'t have to know someone to need what they\'re offering.' },
      { t: 'jump', scene: 'vol1_ch1_s2' },
      // Branch C: empathy pass
      { t: 'narrate', text: 'You feel it before you can name it — something in his voice that sounds like the inside of a memory you\'re not sure is yours.' },
      { t: 'say', char: 'Stranger', expr: 'surprised', text: 'Oh. You\'re one of the ones who can still hear it.' },
      { t: 'say', char: 'Stranger', expr: 'warm', text: 'That changes things. Sit down. Please.' },
      { t: 'jump', scene: 'vol1_ch1_s2' },
    ]
  },

  vol1_ch1_s2: {
    id: 'vol1_ch1_s2',
    nodes: [
      { t: 'say', char: 'Stranger', expr: 'neutral', text: 'Here is the myth of you: you were born in a world that had already decided what you were. You have been arguing with that decision ever since.' },
      { t: 'say', char: 'Stranger', expr: 'neutral', text: 'The argument is the story. Not the conclusion — the argument.' },
      { t: 'think', char: null, text: 'He\'s either the wisest person you\'ve ever met or the kind of crazy that sounds like wisdom.' },
      { t: 'think', char: null, text: 'The distinction, you\'re realizing, may not matter as much as you thought.' },
      { t: 'choice', opts: [
        { text: '"What are you?"', goto: 5 },
        { text: '"Why are you telling me this?"', goto: 8 },
        { text: '[LOGIC] The coffee appeared without anyone taking an order. The booth was empty when you walked in.', check: { skill: 'logic', diff: 9 }, pass: 11, fail: 8 },
      ]},
      { t: 'say', char: 'Stranger', expr: 'amused', text: 'Something old. Something that remembers when the stories were new.' },
      { t: 'say', char: 'Stranger', expr: 'amused', text: 'Something that has been watching your kind make the same mistakes for so long that the mistakes have started to look like a tradition.' },
      { t: 'say', char: 'Stranger', expr: 'amused', text: 'I find it, against all reason, charming.' },
      { t: 'jump', scene: 'vol1_end' },
      { t: 'say', char: 'Stranger', expr: 'neutral', text: 'Because you are at a crossroads. Not the metaphorical kind — though those too. The actual kind.' },
      { t: 'say', char: 'Stranger', expr: 'neutral', text: 'You came here looking for a direction. I\'m one of the things that lives at crossroads.' },
      { t: 'jump', scene: 'vol1_end' },
      { t: 'think', char: null, text: 'The coffee. The empty booth. The way he knew your face.' },
      { t: 'think', char: null, text: 'You add it up slowly, the way you do when you don\'t want the answer to be true.' },
      { t: 'say', char: 'Stranger', expr: 'impressed', text: 'There it is. Yes. You\'re putting it together.' },
      { t: 'say', char: 'Stranger', expr: 'impressed', text: 'Most people look right at the seams and see upholstery. You\'re different.' },
      { t: 'jump', scene: 'vol1_end' },
    ]
  },

  vol1_end: {
    id: 'vol1_end',
    nodes: [
      { t: 'flag', key: 'vol1_ch1_complete', val: true },
      { t: 'narrate', text: 'Outside, the highway hums. The diner\'s neon flickers in a language you are starting to read.' },
      { t: 'narrate', text: 'The stranger smiles, and it is the smile of something that has been patient for a very long time.' },
      { t: 'say', char: 'Stranger', expr: 'warm', text: 'We\'ll speak again. When you\'re ready.' },
      { t: 'say', char: 'Stranger', expr: 'warm', text: 'And you will be ready. That\'s the thing about you — you always choose to be.' },
      { t: 'narrate', text: '— End of Demo —' },
      { t: 'end' },
    ]
  },

  // ── Vol 1 · Chapter 2 — Act One: John Faust ────────────────────────────────
  // Adapted from the screenplay "Cue title: Faust 3 — a modern mythology".
  // Faust speaks in fragments of verse — each stanza is preserved as one say-node
  // so the cadence holds in the dialogue box.

  vol1_ch2_act_one: {
    id: 'vol1_ch2_act_one', vol: 1, chapter: 2, type: 'chapter',
    title: 'Act One — John Faust',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol1_faust_bedroom_night.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/vol1_ambient.mp3' },
      { t: 'interlude', text: 'Act One', sub: 'John Faust', duration: 2800 },

      { t: 'narrate', text: 'INT. FAUST\'S BEDROOM — NIGHT' },
      { t: 'narrate', text: 'Faust wakes at four a.m. with the sound of an alarm.' },

      { t: 'show', char: 'faust', expr: 'neutral', pos: 'center' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'If it is 4am, then I am awake.' },
      { t: 'narrate', text: 'He pulls a tug of water to drink and gets up out of bed.' },

      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Before this waking I had lucid dreamt a dream in which I\'d had riches — as a captain of industry, movie star debonair. How peculiar.' },
      { t: 'narrate', text: 'Faust looks in the mirror at his early-morning haggard.' },

      { t: 'say', char: 'Faust', expr: 'neutral', text: 'At least it wasn\'t one in which my teeth all fall out and death is imminent. Maybe tomorrow.' },
      { t: 'narrate', text: 'He opens the mirror to get his vitamins. He takes one with a tug of water.' },

      // ── Club montage interlude ────────────────────────────────────────────
      { t: 'interlude', text: 'CUT TO — Detroit', sub: 'Robocop, thumping', duration: 2400 },
      { t: 'narrate', text: 'IMAGES: Faust clubbing with two young girls. The Robocop music video montage of Detroit thumps in the background.' },

      { t: 'say', char: 'Faust', expr: 'neutral', text: 'These modern draughts, my learned trade — I down you with OCP and OTC. Yeah, you know me: your legal and commercial medicinal liaison.' },

      { t: 'narrate', text: 'Cut back. Faust puts on his medical blue uniform and white jacket and heads to work.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Not so heavily medicated just yet, still feeling the effects of last night — though an education away from exactly who I need to be.' },

      { t: 'narrate', text: 'Faust bicycles to work.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Regret not loving enough, not living enough — outside my head.' },

      { t: 'jump', scene: 'vol1_ch2_pharmacy' },
    ]
  },

  vol1_ch2_pharmacy: {
    id: 'vol1_ch2_pharmacy', vol: 1, chapter: 2, type: 'chapter',
    title: 'Act One — The Drugstore',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol1_pharmacy_office.jpg' },
      { t: 'hide', pos: 'center' },
      { t: 'interlude', text: 'The Drugstore', sub: 'Office · Morning', duration: 2000 },

      { t: 'narrate', text: 'INT. PHARMACY OFFICE — DAY' },
      { t: 'narrate', text: 'Faust heads to his office, sits down at the computer.' },
      { t: 'show', char: 'faust', expr: 'neutral', pos: 'center' },

      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Hate seeing the world not as it should be. Everyday tedium sets in, everyday — feel I can\'t break free.' },
      { t: 'narrate', text: 'Faust grabs a handful of pills.' },

      { t: 'say', char: 'Faust', expr: 'neutral', text: 'The latest model. Think I\'ll try three. Going down a stringent chalky burn — can\'t sell what isn\'t personal.' },

      { t: 'choice', opts: [
        { text: 'Swallow them with coffee.', goto: 10 },
        { text: '[COMPOSURE] Set the bottle down. Two will do.', check: { skill: 'composure', diff: 4 }, pass: 13, fail: 10 },
      ]},

      // goto 10 — took three
      { t: 'narrate', text: 'He swallows them with coffee and glances about his office. The fluorescents hum like a slow apology.' },
      { t: 'flag', key: 'faust_dose', val: 3 },
      { t: 'jump', scene: 'vol1_ch2_pharmacy_mirror' },

      // goto 13 — composure pass
      { t: 'narrate', text: 'He sets one back into the palm of the bottle. The bottle accepts it without comment.' },
      { t: 'flag', key: 'faust_dose', val: 2 },
      { t: 'jump', scene: 'vol1_ch2_pharmacy_mirror' },
    ]
  },

  vol1_ch2_pharmacy_mirror: {
    id: 'vol1_ch2_pharmacy_mirror', vol: 1, chapter: 2, type: 'chapter',
    title: 'Act One — Fortress of Solitude',
    nodes: [
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Immortal animal spirit dancing on cave wall — I cannot grasp but merely perceive some primal truth into this quest, inserted dis-honestly.' },
      { t: 'narrate', text: 'Faust stands up and inspects himself in the mirror.' },

      { t: 'say', char: 'Faust', expr: 'neutral', text: 'My world of possibility expands with each new breath. They give this drug to shut-ins — agoraphfolk struggling with writer\'s block.' },
      { t: 'narrate', text: 'Faust looks at his phone.' },

      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Time to make some work. Dime-this corporate skrill. All the tech-pharm nerds — holla at me, please.' },
      { t: 'narrate', text: 'Faust exits the office, emerges into the drugstore proper, looks out at the slow medicated trickle of society.' },

      { t: 'bg', src: 'assets/backgrounds/vol1_pharmacy_floor.jpg' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'From my whitewalled fortress of solitude I emerge and bask upon my kingdom — of cheap fluorescents and impulse buys. For I rule it well.' },

      { t: 'hide', pos: 'center' },
      { t: 'show', char: 'deborah', expr: 'neutral', pos: 'right' },
      { t: 'narrate', text: 'Deborah is helping a customer at the front table. Faust saunters up.' },
      { t: 'show', char: 'faust', expr: 'neutral', pos: 'left' },

      { t: 'say', char: 'Faust',   expr: 'neutral', text: 'Everything going great today.' },
      { t: 'say', char: 'Deborah', expr: 'neutral', text: 'Bit early to tell.' },
      { t: 'say', char: 'Faust',   expr: 'neutral', text: 'Some days I feel like an IV drip.' },
      { t: 'say', char: 'Deborah', expr: 'neutral', text: 'Pretty much sums up my view of purgatory.' },

      { t: 'hide', pos: 'left' },
      { t: 'show', char: 'old_woman', expr: 'warm', pos: 'left' },
      { t: 'narrate', text: 'A customer interrupts — a happy old woman.' },

      { t: 'say', char: 'Old Woman', expr: 'warm', text: 'When most the ones my age learn how to be happy, they\'ve already lost so much time. So enjoy it. Be young and happy forever.' },
      { t: 'narrate', text: 'Faust checks the bottle and hands it over to her.' },

      { t: 'show', char: 'faust', expr: 'neutral', pos: 'center' },
      { t: 'say', char: 'Faust',   expr: 'neutral', text: 'Another happy customer served.' },
      { t: 'say', char: 'Deborah', expr: 'neutral', text: 'Another one who sees the light oncoming.' },
      { t: 'say', char: 'Faust',   expr: 'neutral', text: 'I feel like Charon ferrying.' },
      { t: 'say', char: 'Deborah', expr: 'neutral', text: 'Aptly put.' },

      { t: 'hide', pos: 'left' },
      { t: 'show', char: 'eric', expr: 'neutral', pos: 'left' },
      { t: 'narrate', text: 'Faust\'s other assistant, Eric, enters.' },

      { t: 'say', char: 'Eric',    expr: 'neutral', text: 'Yo yo ma in the hizzouse.' },
      { t: 'say', char: 'Deborah', expr: 'neutral', text: 'What he got in that grill?' },
      { t: 'say', char: 'Eric',    expr: 'neutral', text: 'Just a bridge and two f-holes.' },
      { t: 'say', char: 'Faust',   expr: 'neutral', text: 'MC R-I-B is back!' },

      { t: 'narrate', text: 'Faust and Eric palm-shake. Eric puts down lunch.' },
      { t: 'say', char: 'Faust',   expr: 'neutral', text: 'I smell me some Vietnamese.' },
      { t: 'narrate', text: 'Deborah is already digging into hers.' },
      { t: 'say', char: 'Deborah', expr: 'neutral', text: 'So good. Give it over.' },
      { t: 'say', char: 'Eric',    expr: 'neutral', text: 'Six eggrolls between the three of us.' },
      { t: 'say', char: 'Faust',   expr: 'neutral', text: 'Hint: lunch is on me — because I want three.' },

      { t: 'jump', scene: 'vol1_ch2_park' },
    ]
  },

  vol1_ch2_park: {
    id: 'vol1_ch2_park', vol: 1, chapter: 2, type: 'chapter',
    title: 'Act One — The Park',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol1_park_day.jpg' },
      { t: 'hide', pos: 'left' }, { t: 'hide', pos: 'center' }, { t: 'hide', pos: 'right' },
      { t: 'interlude', text: 'The Park', sub: 'Later · Day', duration: 1800 },

      { t: 'narrate', text: 'EXT. THE PARK — DAY' },
      { t: 'narrate', text: 'Faust is jogging with his friend, Jacob.' },
      { t: 'show', char: 'faust', expr: 'neutral', pos: 'left' },
      { t: 'show', char: 'jacob', expr: 'neutral', pos: 'right' },

      { t: 'say', char: 'Faust', expr: 'neutral', text: 'What have you been reading, my friend?' },
      { t: 'say', char: 'Jacob', expr: 'neutral', text: 'Oh, let\'s see — Ratifying Nations of the Comprehensive Nuclear Test Ban Treaty.' },

      { t: 'say', char: 'Faust', expr: 'neutral', text: 'I just started reading — funnily enough — the book whose title character I was named after.' },
      { t: 'say', char: 'Jacob', expr: 'neutral', text: 'So how is it as a translation? Hear us yanks can\'t quite get it right.' },

      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Not too shabby. Taking my time with it. Have this funny feeling life is getting weirder.' },
      { t: 'say', char: 'Jacob', expr: 'neutral', text: 'Lay off the recreational, man — you\'re wigging me out a bit. Here.' },

      { t: 'say', char: 'Faust', expr: 'neutral', text: 'No big deal. Well — it is a big deal. Found some fun stuff out about my grandparents.' },
      { t: 'say', char: 'Jacob', expr: 'neutral', text: 'People are always finding out cool stuff about grandparents. Grandparents are awesome for all the shit they lived through.' },

      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Well said. But my relations, while awesome, ran to the kooky occult side of things. Dabbled in sex magick and the like.' },
      { t: 'say', char: 'Jacob', expr: 'neutral', text: 'Go on.' },

      { t: 'say', char: 'Faust', expr: 'neutral', text: 'I\'m not sure if my grand-dad was Jack Parsons or L. Ron Hubbard.' },
      { t: 'say', char: 'Jacob', expr: 'neutral', text: 'I know of Monsieur Xenu — but not of this Parsons dude.' },

      { t: 'choice', opts: [
        { text: '"Long story short, let me sum it up."', goto: 22 },
        { text: '"Buckle up. This one earns its bourbon."',  goto: 22 },
      ]},

      // ── Faust's narration of the events — Ken Burns–esque montage ─────────
      { t: 'hide', pos: 'left' }, { t: 'hide', pos: 'right' },
      { t: 'bg', src: 'assets/backgrounds/vol1_grandparents_montage.jpg' },
      { t: 'interlude', text: 'A Ken Burns Montage', sub: 'circa 1946', duration: 2400 },

      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Lafayette — as I\'ll call L. Ron — always wanted to be a sailor boy. Dreamed big dreams. And boy, how he schemed.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Loved his genre books, his science fictions, cowboys, jungles, outer space creatures.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Lived a wonderful life — if only in his own head. Submarine commander and deep-cover (yet decorated) secret agent.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Medical discharge. Drifting about Los Angeles in with New Age, better-living, better-looking people — drawn to his larger-than-life escapades.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'They were not all entirely stupid. Jack Parsons was perhaps brilliant — a non-academic rocket scientist, founding father, wicked eccentric.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'His tastes ran to the occult. His lofty Pasadena mansion — home to many like-minded explorers, also traversing the edge of existence.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Lafayette and Parsons were best friends, worst enemies — each seeking the same thing from their own extreme, gazing into the abyss of their reflection.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'They shared a woman. Her name was Betty. She was my grandmother. And here I am, five decades later.' },

      { t: 'bg', src: 'assets/backgrounds/vol1_park_day.jpg' },
      { t: 'show', char: 'faust', expr: 'neutral', pos: 'left' },
      { t: 'show', char: 'jacob', expr: 'neutral', pos: 'right' },
      { t: 'narrate', text: 'Cut back to the jogging.' },

      { t: 'say', char: 'Jacob', expr: 'neutral', text: 'I\'ll have to read up on that.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Me too. There\'s more cool shit to it.' },
      { t: 'say', char: 'Jacob', expr: 'neutral', text: 'Funky family skeletons do that chicken dance.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Tell me about it.' },

      // — beat: brief Jacob's apartment vignette folded in —
      { t: 'bg', src: 'assets/backgrounds/vol1_jacob_apartment.jpg' },
      { t: 'interlude', text: "Jacob's Apartment", sub: 'Later · Day', duration: 1600 },
      { t: 'narrate', text: 'INT. JACOB\'S APARTMENT — DAY. Jacob and Faust playing video games.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'So what\'s been new with you?' },
      { t: 'say', char: 'Jacob', expr: 'neutral', text: 'Working on cool video games. Smorking. Getting laid regular. Playing some bass. Top Gear torrented for later this evening.' },

      { t: 'jump', scene: 'vol1_ch2_painting' },
    ]
  },

  vol1_ch2_painting: {
    id: 'vol1_ch2_painting', vol: 1, chapter: 2, type: 'chapter',
    title: 'Act One — The Sitting Hour',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol1_faust_apartment_day.jpg' },
      { t: 'hide', pos: 'left' }, { t: 'hide', pos: 'right' }, { t: 'hide', pos: 'center' },
      { t: 'interlude', text: "Faust's Apartment", sub: 'The Easel · Day', duration: 1800 },

      { t: 'narrate', text: 'EXT. FAUST\'S APARTMENT — DAY' },
      { t: 'narrate', text: 'Faust has an easel set up.' },
      { t: 'show', char: 'faust', expr: 'neutral', pos: 'center' },

      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Every one must have a hobby. Said Aunt Grace, who set me up — who sorta got famous in the wild and crazy seventies.' },
      { t: 'narrate', text: 'Faust paints.' },

      { t: 'say', char: 'Faust', expr: 'neutral', text: 'It\'s like reading to me — summoning that which exists outside and bringing it in. Painting burns an image from memory.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'I\'ve started getting better. Don\'t know what that means — only that I am starting to see things which should not be.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'When nightmares keep me up at odd hours, I can relax with my demons and desires made firm in the slowing of paint.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Look what I\'ve trapped. I think three elementals — water on the left, fire on the right, air in the middle.' },

      { t: 'narrate', text: 'Faust takes a hit off the joint he has and leans back.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'While I painted, I talked to them — as they were modelling, and were sitting still indeed.' },
      { t: 'narrate', text: 'Faust looks over at his models — the three elements — while he paints.' },

      // ── Show all three elementals ─────────────────────────────────────────
      { t: 'hide', pos: 'center' },
      { t: 'show', char: 'water', expr: 'neutral', pos: 'left'   },
      { t: 'show', char: 'air',   expr: 'neutral', pos: 'center' },
      { t: 'show', char: 'fire',  expr: 'neutral', pos: 'right'  },

      { t: 'say', char: 'Fire',  expr: 'neutral', text: 'It\'s cool how we can see ourselves as he paints us — even if it is all just tits and ass.' },
      { t: 'say', char: 'Water', expr: 'neutral', text: 'Quiet while he works on me. I think he really gets it. This is so exciting — can\'t you see.' },
      { t: 'say', char: 'Air',   expr: 'neutral', text: 'You\'re just trying to win his favor. Make him an offer of power. Get on his good side — you\'re his astrological element.' },
      { t: 'say', char: 'Water', expr: 'neutral', text: 'No. I think this one isn\'t a dick — which is exactly why shit went down so bad previously. Old white men done stupid shit.' },
      { t: 'say', char: 'Fire',  expr: 'neutral', text: 'Reminder — he\'s just a kid. And look at how he\'s looking at me. I don\'t think it\'s the flames that are fanning his attention.' },
      { t: 'say', char: 'Air',   expr: 'neutral', text: 'At least he reads. The last few have been rather dimwitted. Though I think we should try and warn him.' },
      { t: 'say', char: 'Fire',  expr: 'neutral', text: 'Not to play with fire?' },

      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Zing. You guys converse like I\'m not even here. I can hear you just fine — which is cool, you dig.' },
      { t: 'say', char: 'Air',   expr: 'neutral', text: 'See? I told you he knew we were here.' },
      { t: 'say', char: 'Water', expr: 'neutral', text: 'It\'s all good. He gets it.' },
      { t: 'say', char: 'Air',   expr: 'neutral', text: 'If he gets it, why isn\'t wood here?' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'She\'s the frame, numbnuts.' },
      { t: 'say', char: 'Water', expr: 'neutral', text: 'Called it. Dude is awesome.' },
      { t: 'say', char: 'Air',   expr: 'neutral', text: 'It could go either way yet.' },
      { t: 'say', char: 'Fire',  expr: 'neutral', text: 'Kid knows his shit.' },
      { t: 'say', char: 'Air',   expr: 'neutral', text: 'However casually.' },

      { t: 'say', char: 'Faust', expr: 'neutral', text: 'I just want to paint you. Not hash out some magical deal. So apologies if I get the details wrong — next time I\'ll take a reference photo.' },

      { t: 'choice', opts: [
        { text: '[Listen to Fire. Lean in.]',  goto: 39 },
        { text: '[Listen to Water. Stay steady.]', goto: 41 },
        { text: '[Listen to Air. Take the warning.]', goto: 43 },
      ]},

      // goto 39
      { t: 'flag', key: 'faust_elem_favored', val: 'fire' },
      { t: 'jump', scene: 'vol1_ch2_painting_b' },
      // goto 41
      { t: 'flag', key: 'faust_elem_favored', val: 'water' },
      { t: 'jump', scene: 'vol1_ch2_painting_b' },
      // goto 43
      { t: 'flag', key: 'faust_elem_favored', val: 'air' },
      { t: 'jump', scene: 'vol1_ch2_painting_b' },
    ]
  },

  vol1_ch2_painting_b: {
    id: 'vol1_ch2_painting_b', vol: 1, chapter: 2, type: 'chapter',
    title: 'Act One — The Sitting Hour (cont.)',
    nodes: [
      { t: 'say', char: 'Fire',  expr: 'neutral', text: 'Such a dork. Relax and enjoy the moment. Take a deep breath and breathe — because you, Sir, summoned frickin\' elementals. Without a monstrous manual, no less.' },

      { t: 'say', char: 'Faust', expr: 'neutral', text: 'You have to admit — that is worth some mad real-life XP right there. This tinnitus in my ear is like a ding. Methinks I\'ve leveled up.' },

      { t: 'say', char: 'Water', expr: 'neutral', text: 'So just roll with it, brother. You\'re posting good stats. Keep an eye on the endgame. Move the balls down field. And remember to use all the players — (who are players who are players).' },

      { t: 'say', char: 'Faust', expr: 'neutral', text: 'It\'s cool. I get it. But you have to realize certain things about me. Firstly — my life is a work in progress. Second — I\'ve got much to do yet.' },

      { t: 'say', char: 'Fire',  expr: 'neutral', text: 'You are flesh. You are decay.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Everything is broken down, made new.' },
      { t: 'say', char: 'Water', expr: 'neutral', text: 'Everything is born. Everything dies.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'I welcome what\'s next.' },

      { t: 'say', char: 'Air',   expr: 'neutral', text: 'Alas — our sitting hour is up. You must pee, and break concentration.' },

      { t: 'hide', pos: 'left' }, { t: 'hide', pos: 'center' }, { t: 'hide', pos: 'right' },
      { t: 'show', char: 'faust', expr: 'neutral', pos: 'center' },
      { t: 'narrate', text: 'Faust stands up and looks away from the painting.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Bladder is bursting. (as he pees) Oh — what a wonderful tea party.' },

      { t: 'jump', scene: 'vol1_ch2_skatepark' },
    ]
  },

  vol1_ch2_skatepark: {
    id: 'vol1_ch2_skatepark', vol: 1, chapter: 2, type: 'chapter',
    title: 'Act One — The Skatepark',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol1_skatepark_day.jpg' },
      { t: 'hide', pos: 'left' }, { t: 'hide', pos: 'center' }, { t: 'hide', pos: 'right' },
      { t: 'interlude', text: 'The Skatepark', sub: 'The Pool · Day', duration: 1800 },

      { t: 'narrate', text: 'EXT. THE SKATEPARK — DAY' },
      { t: 'narrate', text: 'Faust is with his friends Wagner and Jacob, waiting to push off into the pool. Faust talks to each in turn.' },

      { t: 'show', char: 'wagner', expr: 'neutral', pos: 'left' },
      { t: 'show', char: 'faust',  expr: 'neutral', pos: 'center' },
      { t: 'show', char: 'jacob',  expr: 'neutral', pos: 'right' },

      { t: 'say', char: 'Faust',  expr: 'neutral', text: 'Fun just to imagine how the world could be.' },
      { t: 'say', char: 'Wagner', expr: 'neutral', text: 'Different future points — the smallest thing.' },
      { t: 'say', char: 'Jacob',  expr: 'neutral', text: 'Could change the big picture completely.' },
      { t: 'say', char: 'Wagner', expr: 'neutral', text: 'Pebbles on the water\'s surface.' },

      { t: 'say', char: 'Faust',  expr: 'neutral', text: 'I feel old just coming out here.' },
      { t: 'say', char: 'Wagner', expr: 'neutral', text: 'Not so bad. Giving me hope for the future.' },
      { t: 'say', char: 'Jacob',  expr: 'neutral', text: 'Plz watch me epic fail plz.' },
      { t: 'say', char: 'Wagner', expr: 'neutral', text: 'You\'re getting better, bro.' },

      { t: 'say', char: 'Faust',  expr: 'neutral', text: 'I need to finally try this.' },
      { t: 'say', char: 'Wagner', expr: 'neutral', text: 'Start off easy, Faust.' },
      { t: 'say', char: 'Faust',  expr: 'neutral', text: 'Break tailbone later.' },
      { t: 'say', char: 'Wagner', expr: 'neutral', text: 'Earn mad skills through trial and error.' },

      // ── Wagner's home ─────────────────────────────────────────────────────
      { t: 'bg', src: 'assets/backgrounds/vol1_wagner_home.jpg' },
      { t: 'hide', pos: 'left' }, { t: 'hide', pos: 'center' }, { t: 'hide', pos: 'right' },
      { t: 'interlude', text: "Wagner's Home", sub: 'After the park', duration: 1800 },
      { t: 'narrate', text: 'INT. WAGNER\'S HOME — DAY. Wagner puts up his skateboard, goes to the record player, and starts some metal.' },

      { t: 'show', char: 'wagner', expr: 'neutral', pos: 'left' },
      { t: 'show', char: 'faust',  expr: 'neutral', pos: 'right' },

      { t: 'say', char: 'Wagner', expr: 'neutral', text: 'This here is the shit.' },
      { t: 'say', char: 'Faust',  expr: 'neutral', text: 'What is this I\'m hearing?' },
      { t: 'say', char: 'Wagner', expr: 'neutral', text: 'Burzum. Norwegian Black Metal.' },
      { t: 'say', char: 'Faust',  expr: 'neutral', text: 'Euronymous and Varg Vikernes.' },

      { t: 'say', char: 'Wagner', expr: 'neutral', text: 'Metal-sad — those folk so wrapped up in the story, can\'t see past what they are creating.' },

      { t: 'say', char: 'Faust',  expr: 'neutral', text: 'We need to get a good crew. Take the longboat out tonight. Prowl uncertain waters.' },
      { t: 'say', char: 'Wagner', expr: 'neutral', text: 'Then let us away — to Judgement Day.' },

      { t: 'narrate', text: 'They make haste to their ride of choice — JD, a beat-up piece of shit.' },

      { t: 'flag', key: 'vol1_ch2_complete', val: true },
      { t: 'narrate', text: '— End of Act One, Part I —' },
      { t: 'end' },
    ]
  },

  // ── Vol 1 · Chapter 3 — Act One: Judgement Day ─────────────────────────────
  // Adapted from the screenplay "Judgement Day". Picks up from the end of
  // Ch 2: the trio in JD, then a hip bar, then a sub conversation outside,
  // then a club. The Handsome Triumvirate name themselves here.

  vol1_ch3_judgement_day: {
    id: 'vol1_ch3_judgement_day', vol: 1, chapter: 3, type: 'chapter',
    title: 'Act One — Judgement Day',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol1_jd_driving_night.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/vol1_drive_night.mp3' },
      { t: 'interlude', text: 'Judgement Day', sub: 'EXT. Driving Around · Night', duration: 2400 },

      { t: 'narrate', text: 'EXT. DRIVING AROUND — NIGHT' },
      { t: 'narrate', text: 'Good music is playing. Everyone is tuned in and excited.' },

      { t: 'show', char: 'wagner', expr: 'neutral', pos: 'left'   },
      { t: 'show', char: 'jacob',  expr: 'neutral', pos: 'center' },
      { t: 'show', char: 'faust',  expr: 'neutral', pos: 'right'  },

      { t: 'say', char: 'Wagner', expr: 'neutral', text: 'All right.' },
      { t: 'say', char: 'Jacob',  expr: 'neutral', text: 'The night is young. Let us find some bitches.' },
      { t: 'say', char: 'Wagner', expr: 'neutral', text: 'If bitches ye seek — bitches you\'ll find.' },
      { t: 'say', char: 'Faust',  expr: 'neutral', text: 'Which is why I look for ladies.' },

      { t: 'say', char: 'Jacob',  expr: 'neutral', text: 'Whatever mood strikes me, I do little to resist — as we are complex animals, fighting flawed-up nature.' },
      { t: 'say', char: 'Wagner', expr: 'neutral', text: 'How can you both engage in and hope to supplant base instinct?' },
      { t: 'say', char: 'Jacob',  expr: 'neutral', text: 'Easy to just go with it. Recognize and learn from experience.' },

      { t: 'say', char: 'Faust',  expr: 'neutral', text: 'Which is why the world needs new mythology. We three shall be the Handsome Triumvirate — but aren\'t we already? I mean, look at us.' },
      { t: 'say', char: 'Wagner', expr: 'neutral', text: 'Living in this land of milk and honey.' },

      { t: 'flag', key: 'handsome_triumvirate', val: true },

      { t: 'jump', scene: 'vol1_ch3_bar' },
    ]
  },

  vol1_ch3_bar: {
    id: 'vol1_ch3_bar', vol: 1, chapter: 3, type: 'chapter',
    title: 'Act One — A Hip Bar',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol1_bar_interior.jpg' },
      { t: 'hide', pos: 'left' }, { t: 'hide', pos: 'center' }, { t: 'hide', pos: 'right' },
      { t: 'interlude', text: 'A Hip Bar', sub: 'INT. · Night · Chalk table in the back', duration: 2000 },

      { t: 'narrate', text: 'INT. A HIP BAR — NIGHT' },
      { t: 'narrate', text: 'The Handsome Triumvirate wander in and make their way to the chalk table.' },

      { t: 'show', char: 'wagner', expr: 'neutral', pos: 'center' },
      { t: 'narrate', text: 'Wagner is on the phone.' },
      { t: 'say', char: 'Wagner', expr: 'neutral', text: 'Be home later. Drinking with the boys. To steer them out of trouble. Love you too.' },

      { t: 'show', char: 'jacob',  expr: 'neutral', pos: 'left'  },
      { t: 'show', char: 'faust',  expr: 'neutral', pos: 'right' },

      { t: 'say', char: 'Jacob',  expr: 'neutral', text: 'Shots all around.' },
      { t: 'say', char: 'Wagner', expr: 'neutral', text: 'None for me. Ginger beer, thanks.' },
      { t: 'say', char: 'Faust',  expr: 'neutral', text: 'I\'ll help carry. Chalk table\'s open.' },
      { t: 'say', char: 'Wagner', expr: 'neutral', text: 'Going out for a smoke — join you so on.' },

      { t: 'hide', pos: 'center' },
      { t: 'narrate', text: 'Faust and Jacob sit at the table.' },

      { t: 'say', char: 'Jacob', expr: 'neutral', text: 'Emily, Helen, and Margaret are on their way.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'They\'re trying to set me up with Margaret.' },
      { t: 'say', char: 'Jacob', expr: 'neutral', text: 'Yeah. We boned.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Figured.' },

      { t: 'say', char: 'Jacob', expr: 'neutral', text: 'Already drawing up some wacky shit. Still hot for teacher or star pupil — move, but quick, else some one will. There\'s timing, and then there\'s timing.' },

      { t: 'choice', opts: [
        { text: '"Time and place for everything — you know this."',         goto: 24 },
        { text: '"From where you look, sure. From where I sit, no."',       goto: 26 },
        { text: '[Say nothing. Let him finish.]',                            goto: 28 },
      ]},

      // goto 24 — graceful
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Time and place for everything. You know this.' },
      { t: 'jump', scene: 'vol1_ch3_bar_b' },
      // goto 26 — pushback
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'From where you look, sure. From where I sit — no. Don\'t count me out.' },
      { t: 'jump', scene: 'vol1_ch3_bar_b' },
      // goto 28 — silent
      { t: 'narrate', text: 'You let it sit. Jacob shrugs, half-respectful. He has known you long enough to read a silence.' },
      { t: 'jump', scene: 'vol1_ch3_bar_b' },
    ]
  },

  vol1_ch3_bar_b: {
    id: 'vol1_ch3_bar_b', vol: 1, chapter: 3, type: 'chapter',
    title: 'Act One — The Toast',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol1_bar_interior.jpg' },
      { t: 'show', char: 'jacob', expr: 'neutral', pos: 'left' },
      { t: 'show', char: 'faust', expr: 'neutral', pos: 'right' },

      { t: 'say', char: 'Jacob', expr: 'neutral', text: 'From where I look — seems missed opportunity.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'You\'re right. But don\'t count me out.' },

      { t: 'narrate', text: 'The girls join them. Helen pushes Margaret into the seat next to Faust and sits next to Jacob. Emily puts her purse next to Faust and heads outside to join Wagner for a smoke.' },

      { t: 'show', char: 'helen',    expr: 'neutral', pos: 'left'   },
      { t: 'show', char: 'margaret', expr: 'neutral', pos: 'center' },
      { t: 'show', char: 'faust',    expr: 'neutral', pos: 'right'  },

      { t: 'say', char: 'Helen',    expr: 'neutral', text: 'Hello, boys. How goes the noche?' },
      { t: 'say', char: 'Jacob',    expr: 'neutral', text: 'Agreeably laid back. Productive.' },
      { t: 'say', char: 'Faust',    expr: 'neutral', text: 'Cool drinks. Swell friends. Cozy corner.' },
      { t: 'say', char: 'Margaret', expr: 'neutral', text: 'Sounds most affirming. I got yelled at.' },

      { t: 'say', char: 'Jacob',    expr: 'neutral', text: 'By your useless boss — for what small trifle?' },
      { t: 'say', char: 'Margaret', expr: 'neutral', text: 'My fault, this time. He\'s constantly stressing me out.' },
      { t: 'say', char: 'Faust',    expr: 'neutral', text: 'That\'s no good.' },
      { t: 'say', char: 'Helen',    expr: 'neutral', text: 'Girlie shots coming up.' },

      { t: 'narrate', text: 'They all hold to toast and drink.' },

      { t: 'say', char: 'Helen',    expr: 'neutral', text: 'To finding gainful — not painful — employment.' },
      { t: 'say', char: 'Jacob',    expr: 'neutral', text: 'May stupid jerkfaces in workforce get rightful comeuppance.' },
      { t: 'say', char: 'Margaret', expr: 'neutral', text: 'Thanks for helping me forget my troubles. If but for a moment.' },
      { t: 'say', char: 'Faust',    expr: 'neutral', text: 'Cheers — to the simple magic in this.' },

      // Wagner and Emily return
      { t: 'narrate', text: 'Wagner and Emily return to the table.' },
      { t: 'hide', pos: 'left' },
      { t: 'show', char: 'wagner', expr: 'neutral', pos: 'left' },
      { t: 'show', char: 'emily',  expr: 'neutral', pos: 'center' },

      { t: 'say', char: 'Wagner', expr: 'neutral', text: '(to Emily) A deft maneuver — please, to rejoin the group.' },
      { t: 'say', char: 'Emily',  expr: 'neutral', text: 'I didn\'t know they had pinball here.' },
      { t: 'say', char: 'Jacob',  expr: 'neutral', text: 'Yes. And Missile Command, too.' },
      { t: 'say', char: 'Emily',  expr: 'neutral', text: 'Fifth Element pinball is my favorite. Corbin Dallas — multi-pass, multi-ball.' },
      { t: 'say', char: 'Jacob',  expr: 'neutral', text: 'Forswoon — for she is as beautiful as she is nerdy.' },

      { t: 'say', char: 'Emily',    expr: 'neutral', text: 'I dressed as Leeloo Minai Lekarariba-Lamina-Tchai Ekbat De Sebat for Halloween.' },
      { t: 'say', char: 'Margaret', expr: 'neutral', text: 'Stop showing off, Emily. Else we\'ll leave you home next time.' },
      { t: 'say', char: 'Helen',    expr: 'neutral', text: 'Hey — we\'ve all got our nerd triggers. Be it Star Trek, wrestling, pin-up photography.' },

      { t: 'say', char: 'Wagner',   expr: 'neutral', text: 'It\'s times like these I could thank the suffragettes in person.' },
      { t: 'say', char: 'Helen',    expr: 'neutral', text: 'Okay. What does that mean?' },
      { t: 'say', char: 'Wagner',   expr: 'neutral', text: 'Without them, I would not be having this fine evening under these circumstances.' },
      { t: 'say', char: 'Emily',    expr: 'neutral', text: 'Continue.' },

      { t: 'say', char: 'Wagner',   expr: 'neutral', text: 'Sad fact is — left to their own devices — white men would have ruled this world completely.' },
      { t: 'say', char: 'Emily',    expr: 'neutral', text: 'There has always been opposition. And in this connected age, their grip has slipped.' },
      { t: 'say', char: 'Wagner',   expr: 'neutral', text: 'It is a glorious thing to see my own primal archetype subverted.' },
      { t: 'say', char: 'Helen',    expr: 'neutral', text: 'If we\'re saying — down with white men — hear, hear.' },

      { t: 'narrate', text: 'The men all say, in chorus —' },
      { t: 'say', char: 'Wagner', expr: 'neutral', text: 'We suck!' },
      { t: 'say', char: 'Jacob',  expr: 'neutral', text: 'We suck!' },
      { t: 'say', char: 'Faust',  expr: 'neutral', text: 'We suck!' },
      { t: 'narrate', text: 'And cheer.' },

      { t: 'jump', scene: 'vol1_ch3_outside' },
    ]
  },

  vol1_ch3_outside: {
    id: 'vol1_ch3_outside', vol: 1, chapter: 3, type: 'chapter',
    title: 'Act One — Outside the Bar',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol1_bar_exterior_night.jpg' },
      { t: 'hide', pos: 'left' }, { t: 'hide', pos: 'center' }, { t: 'hide', pos: 'right' },
      { t: 'interlude', text: 'Outside the Bar', sub: 'Smoke break · Night', duration: 1800 },

      { t: 'narrate', text: 'EXT. THE BAR — NIGHT' },
      { t: 'narrate', text: 'Jacob and Emily are talking outside. Faust is inside, talking to Wagner. The two other girls are getting more drinks.' },

      { t: 'show', char: 'wagner', expr: 'neutral', pos: 'left'  },
      { t: 'show', char: 'faust',  expr: 'neutral', pos: 'right' },

      { t: 'say', char: 'Wagner', expr: 'neutral', text: 'What sort of superpower would you have?' },

      { t: 'choice', opts: [
        { text: '"To be myself, only better."',         goto: 11 },
        { text: '"Flight. The earthbound thing tires me."',  goto: 13 },
        { text: '"I\'d hear what people aren\'t saying."',     goto: 15 },
      ]},

      // goto 11 — myself only better
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'To be myself — only better.' },
      { t: 'jump', scene: 'vol1_ch3_outside_b' },
      // goto 13 — flight
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Flight. The earthbound thing tires me out — and I\'m starting to notice it.' },
      { t: 'jump', scene: 'vol1_ch3_outside_b' },
      // goto 15 — empath
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'I\'d hear what people aren\'t saying. Which is, probably, half a curse.' },
      { t: 'jump', scene: 'vol1_ch3_outside_b' },
    ]
  },

  vol1_ch3_outside_b: {
    id: 'vol1_ch3_outside_b', vol: 1, chapter: 3, type: 'chapter',
    title: 'Act One — Black Lodge',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol1_bar_exterior_night.jpg' },
      { t: 'show', char: 'wagner', expr: 'neutral', pos: 'left'  },
      { t: 'show', char: 'faust',  expr: 'neutral', pos: 'right' },

      { t: 'say', char: 'Wagner', expr: 'neutral', text: 'Flight, telekinesis — there\'s a long list.' },
      { t: 'say', char: 'Faust',  expr: 'neutral', text: 'Cool and all. How about you?' },
      { t: 'say', char: 'Wagner', expr: 'neutral', text: 'I skate.' },
      { t: 'say', char: 'Faust',  expr: 'neutral', text: 'See — that being like flying.' },
      { t: 'say', char: 'Wagner', expr: 'neutral', text: 'Jacob also flies. But in planes, though.' },
      { t: 'say', char: 'Faust',  expr: 'neutral', text: 'I\'m the earthbound one — push come to shove.' },
      { t: 'say', char: 'Wagner', expr: 'neutral', text: 'Never say never, my friend.' },

      { t: 'say', char: 'Faust',  expr: 'neutral', text: 'I had a thought.' },
      { t: 'say', char: 'Wagner', expr: 'neutral', text: 'Just now — about what?' },
      { t: 'say', char: 'Faust',  expr: 'neutral', text: 'A strange one. About a black lodge. People coming and going.' },
      { t: 'say', char: 'Wagner', expr: 'neutral', text: 'Getting any ideears? Or are you just ruminating?' },

      { t: 'say', char: 'Faust',  expr: 'neutral', text: 'Only expressing myself in words — when perhaps it should be painted on canvas. Or worked into something useful.' },
      { t: 'say', char: 'Wagner', expr: 'neutral', text: 'Ah, yes. I remember those days well — and want to return to projects old.' },

      { t: 'say', char: 'Faust',  expr: 'neutral', text: 'We need to work on something again. Create other worlds to run to.' },

      { t: 'flag', key: 'faust_black_lodge', val: true },
      { t: 'narrate', text: 'They are rejoined.' },

      { t: 'hide', pos: 'left' }, { t: 'hide', pos: 'right' },
      { t: 'show', char: 'wagner',   expr: 'neutral', pos: 'left'   },
      { t: 'show', char: 'jacob',    expr: 'neutral', pos: 'center' },
      { t: 'show', char: 'emily',    expr: 'neutral', pos: 'right'  },

      { t: 'say', char: 'Wagner', expr: 'neutral', text: 'It is a good idea, my friend.' },
      { t: 'say', char: 'Faust',  expr: 'neutral', text: 'Yours are always the best.' },
      { t: 'say', char: 'Jacob',  expr: 'neutral', text: 'Next to mine, you mean.' },
      { t: 'say', char: 'Faust',  expr: 'neutral', text: 'I\'d say they sit fairly center on all things.' },
      { t: 'say', char: 'Wagner', expr: 'neutral', text: 'Good ideas just drift amongst us.' },
      { t: 'say', char: 'Emily',  expr: 'neutral', text: 'Enough of this boys\' club. Who wants to dance?' },

      { t: 'jump', scene: 'vol1_ch3_club' },
    ]
  },

  vol1_ch3_club: {
    id: 'vol1_ch3_club', vol: 1, chapter: 3, type: 'chapter',
    title: 'Act One — The Underworld',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol1_club_dance.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/vol1_club_thump.mp3' },
      { t: 'hide', pos: 'left' }, { t: 'hide', pos: 'center' }, { t: 'hide', pos: 'right' },
      { t: 'interlude', text: 'The Underworld', sub: 'Intercut · Dancing · Loud Music', duration: 2200 },

      { t: 'narrate', text: 'INTERCUT — scenes of the group dancing at the club.' },

      { t: 'show', char: 'helen',    expr: 'neutral', pos: 'left'   },
      { t: 'show', char: 'margaret', expr: 'neutral', pos: 'center' },
      { t: 'show', char: 'faust',    expr: 'neutral', pos: 'right'  },

      { t: 'say', char: 'Helen',    expr: 'neutral', text: 'Aye —' },
      { t: 'say', char: 'Margaret', expr: 'neutral', text: 'And seconded. Any of the males want to ratify this amendment?' },

      { t: 'hide', pos: 'left' }, { t: 'hide', pos: 'center' }, { t: 'hide', pos: 'right' },
      { t: 'show', char: 'faust',  expr: 'neutral', pos: 'left'   },
      { t: 'show', char: 'wagner', expr: 'neutral', pos: 'center' },
      { t: 'show', char: 'jacob',  expr: 'neutral', pos: 'right'  },

      { t: 'say', char: 'Faust',  expr: 'neutral', text: 'I think we\'re being bullied — into moving in place quickly, to loud music.' },
      { t: 'say', char: 'Wagner', expr: 'neutral', text: 'Overpriced drinks. Cover charges. Restrooms crusted wiv sex and excess.' },
      { t: 'say', char: 'Jacob',  expr: 'neutral', text: 'Well, that I can abide. But see no reason to invite back ghosts of dramas past.' },
      { t: 'say', char: 'Faust',  expr: 'neutral', text: 'A most suitable entrance into the underworld — for all its modern limitations.' },

      { t: 'flag', key: 'vol1_ch3_complete', val: true },
      { t: 'narrate', text: '— End of Act One, Part II —' },
      { t: 'end' },
    ]
  },


  // ── Vol 1 · Chapter 4 — Act One: Dream States ──────────────────────────────
  // Adapted from the screenplay "act one, dream states". A bedside visitation
  // bleeds into nested dreams: a Woman, an infant-self monologue, a dream bed,
  // a bar where Faust draws Dickens Dean into being, and Club Sharp — the #
  // logo of a different volume. Wakes at 4am and pukes. Several cross-text
  // hooks: Dickens Dean (Vol 7), Club # (Vol 4).

  vol1_ch4_dream_states: {
    id: 'vol1_ch4_dream_states', vol: 1, chapter: 4, type: 'chapter',
    title: 'Act One — Dream States',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol1_faust_bedroom_night.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/vol1_dream_drone.mp3' },
      { t: 'interlude', text: 'Dream States', sub: 'INT. Faust\'s Bedroom · Night', duration: 2600 },

      { t: 'narrate', text: 'INT. FAUST\'S BEDROOM — NIGHT' },
      { t: 'narrate', text: 'Faust wakes from a bad dream. Sitting at the foot of his bed is a woman.' },

      { t: 'show', char: 'woman', expr: 'neutral', pos: 'center' },

      { t: 'say', char: 'Woman', expr: 'neutral', text: 'I did not want to alarm you.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Not alarmed. Just not awake fully.' },

      { t: 'say', char: 'Woman', expr: 'neutral', text: 'You lose control of dreams, you lose control of reality.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Reality is a new day — which I live as if it were my last.' },

      { t: 'say', char: 'Woman', expr: 'neutral', text: 'And what of yesterday? Did it amount to much?' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Just trying to build something tangible with my friendships.' },

      { t: 'say', char: 'Woman', expr: 'neutral', text: 'And yet you resist making new friends. Why is that?' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'I have difficulty satisfying good connections I have already.' },

      { t: 'narrate', text: 'She moves into bed with Faust.' },
      { t: 'say', char: 'Woman', expr: 'neutral', text: 'Want me to leave you be — or hold you close?' },

      { t: 'choice', opts: [
        { text: '"If you\'re already in my head — hold me close."', goto: 17 },
        { text: '"Leave me. Let me sleep this off."',                goto: 21 },
      ]},

      // goto 17 — hold close
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'If you\'re already in my head — hold me close, please.' },
      { t: 'narrate', text: 'She hugs Faust tight.' },
      { t: 'flag', key: 'faust_dream_woman_held', val: true },
      { t: 'jump', scene: 'vol1_ch4_lullaby' },

      // goto 22 — push away
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Leave me. Let me sleep this off — whatever you are.' },
      { t: 'say', char: 'Woman', expr: 'neutral', text: 'You don\'t mean that. But all right. I\'ll be where I\'ve been.' },
      { t: 'flag', key: 'faust_dream_woman_held', val: false },
      { t: 'jump', scene: 'vol1_ch4_lullaby' },
    ]
  },

  vol1_ch4_lullaby: {
    id: 'vol1_ch4_lullaby', vol: 1, chapter: 4, type: 'chapter',
    title: 'Act One — In His Sleep',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol1_faust_bedroom_night.jpg' },
      { t: 'show', char: 'woman', expr: 'neutral', pos: 'center' },

      { t: 'say', char: 'Faust', expr: 'neutral', text: 'I have to warn you — I generate a lot of heat.' },
      { t: 'say', char: 'Woman', expr: 'neutral', text: 'Just close your eyes and talk in your sleep.' },

      { t: 'narrate', text: 'Faust sleeps.' },

      { t: 'interlude', text: 'IN HIS SLEEP', sub: 'Faust, talking', duration: 2200 },
      { t: 'hide', pos: 'center' },

      // ── The infant monologue ──────────────────────────────────────────────
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'I remember what it was to be infant — further back even than that, maybe. I remember how beautiful childhood looked, sounded. How it all came rushing back to me.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Words sounded like music — literally the most beautiful thing. That beauty, through infancy, the reason for my golden stares. The music of speech flowed into me. Much of that beauty transferred.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Objects became the best thing ever. Naming them gave meaning, and power — to summon to our wills. Else the power of cry rendered them shrill.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'The more I could do, the more excited I became. Because I realized I was few and rare among other little ones. Perfect angels, figuring shit out, asking questions.' },

      { t: 'narrate', text: 'Faust is in dream.' },
      { t: 'jump', scene: 'vol1_ch4_dream_bed' },
    ]
  },

  vol1_ch4_dream_bed: {
    id: 'vol1_ch4_dream_bed', vol: 1, chapter: 4, type: 'chapter',
    title: 'Act One — The Dream Bed',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol1_dream_bed.jpg' },
      { t: 'hide', pos: 'left' }, { t: 'hide', pos: 'center' }, { t: 'hide', pos: 'right' },
      { t: 'interlude', text: 'INT. Dream Bed', sub: 'Watches in purple gibberish · Paintings breathing', duration: 2200 },

      { t: 'narrate', text: 'INT. DREAM BED — NIGHT' },
      { t: 'narrate', text: 'Faust sits up, checking his watch. It glows purple with gibberish. Next to him in bed is the woman. Both of them are naked under the covers. The windows glow with a yellow sort of barrier. Paintings on walls and floors pulse with life.' },

      { t: 'show', char: 'woman', expr: 'neutral', pos: 'center' },

      { t: 'say', char: 'Faust', expr: 'neutral', text: 'I\'m afraid I\'m going to have to kick you out.' },
      { t: 'say', char: 'Woman', expr: 'neutral', text: 'Do you do this to all your dreamgirls?' },

      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Trying to be a gentleman. But let me have this corner pocket of unfettered thought, and slumber.' },

      { t: 'narrate', text: 'The woman gets out of bed, her body glowing colder as it leaves the heat of the bed.' },
      { t: 'say', char: 'Woman', expr: 'neutral', text: 'Fine, Faust. Your thoughts are your own.' },

      { t: 'narrate', text: 'Faust leans in close, kissing her as she pulls away.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Thanks for respecting my secret scheming, baby.' },

      { t: 'say', char: 'Woman', expr: 'neutral', text: 'I just hope you keep me reasonably near.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'You may be more real than all else.' },

      { t: 'say', char: 'Woman', expr: 'neutral', text: 'No wonder you keep secrets from me, Faust.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'I may not be able to answer all your questions — but I\'ll strive for honesty in all things.' },

      { t: 'say', char: 'Woman', expr: 'neutral', text: 'Honesty screws up the world, Faust. There are degrees.' },

      { t: 'narrate', text: 'Faust lets go of the woman. She fades away.' },
      { t: 'hide', pos: 'center' },

      { t: 'jump', scene: 'vol1_ch4_dream_bar' },
    ]
  },

  vol1_ch4_dream_bar: {
    id: 'vol1_ch4_dream_bar', vol: 1, chapter: 4, type: 'chapter',
    title: 'Act One — Summoned',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol1_dream_bar.jpg' },
      { t: 'hide', pos: 'left' }, { t: 'hide', pos: 'center' }, { t: 'hide', pos: 'right' },
      { t: 'interlude', text: 'A Bar That Was Not There', sub: 'It assembles around you', duration: 2400 },

      { t: 'narrate', text: 'Faust lands in a bar. It materializes around him as he goes through the motions of entering, sitting down, and drawing. He sketches a portrait, quickly. It comes to life with a sudden urgency.' },
      { t: 'narrate', text: 'Faust is now sitting across the table from this young person — tall, attractive. The man is watching Faust draw.' },

      { t: 'show', char: 'dickens_dean', expr: 'neutral', pos: 'right' },

      { t: 'say', char: 'Man',   expr: 'neutral', text: 'It seems you have summoned me.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'What I just did right there is draw a picture. Plain and simple.' },

      { t: 'say', char: 'Man',   expr: 'neutral', text: 'No — you clearly summoned me. Dreams have dream rules.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'You assume too much of any one thing. It is you instigating this whole encounter.' },

      { t: 'say', char: 'Man',   expr: 'neutral', text: 'Well — we\'re skipping along quick. Sort of hoped this played out the old way.' },

      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Exactly the jazz I\'m working on. This table, right here. See — I\'m ahead of your game, Antagonist. I know why you\'re here. And I\'m going to lay it out early.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'I\'m going to win you to me. Not as an enemy — but as a friend who knows how to make this world so frigging awesome. I welcome your intrusion upon my life. And any attacks against my own happiness will be taken as a threat — implied, because one of us is the intruder, though I\'m still not sure which.' },

      { t: 'say', char: 'Man',   expr: 'neutral', text: 'Not too shabby. But still — awful sloppy. Speed up. Not slow down.' },

      { t: 'narrate', text: 'Faust is drawing the man. He looks at his picture with strange recognition.' },

      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Not that I trust you, or want anything to do with you. But if you aren\'t leaving — the name is John Faust. I\'ve got this fantastic destiny ahead of me. And I want to know who you are, and what you\'re hoping to do with it.' },

      { t: 'say', char: 'Dickens Dean', role: 'Antagonist', expr: 'neutral', text: 'Good to meet you, John. A name I go by is Dickens Dean. And you have in fact guessed it — I am a traveller from another realm. A world much like this one. More of a time-traveller, really.' },
      { t: 'say', char: 'Dickens Dean', role: 'Antagonist', expr: 'neutral', text: 'Been so many places. Done so many things. And I\'m sorry if my presence here is an intrusion. Usually, my presence generates excitement and intrigue. I mostly just observe. Watch. Enjoy. Sometimes I get involved with awesome amazing people. You, sir — and your friends — may be awesome amazing people.' },

      { t: 'flag', key: 'faust_met_dickens', val: true },
      { t: 'narrate', text: 'Faust extends a hand, staring across at his Nemesis. The two shake — comfortably familiar.' },

      { t: 'say', char: 'Faust',        expr: 'neutral', text: 'I feel we\'ve met somewhere.' },
      { t: 'say', char: 'Dickens Dean', role: 'Antagonist', expr: 'neutral', text: 'In a dream, perhaps. I have a friend you need to meet.' },

      { t: 'narrate', text: 'Dickens beckons Joan over. She looks down at the table and realizes Faust has drawn her, too.' },
      { t: 'show', char: 'joan', expr: 'neutral', pos: 'left' },

      { t: 'say', char: 'Dickens Dean', role: 'Antagonist', expr: 'neutral', text: 'Joan, meet John Faust. Artist — in this dream space we find ourselves.' },
      { t: 'narrate', text: 'Joan sits next to Faust, close, looking in on the drawings.' },

      { t: 'say', char: 'Joan',  expr: 'neutral', text: 'So you\'re the one people they\'ve been talking about.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'I find it strange — people are coming up to me in dreams now.' },

      { t: 'narrate', text: 'Joan looks at Faust funny. Suddenly reality snaps into focus.' },
      { t: 'say', char: 'Joan',  expr: 'neutral', text: 'This isn\'t a dream, honey.' },

      { t: 'narrate', text: 'Faust gets up out of his chair — drunk and staggering.' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'How many have I had? I seem to have lost count.' },
      { t: 'say', char: 'Joan',  expr: 'neutral', text: 'Some first impression you are.' },

      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Where are my friends? I came with my friends.' },
      { t: 'say', char: 'Dickens Dean', role: 'Antagonist', expr: 'neutral', text: 'Relax, good sir. I think the effects of Joan have just kicked in. Sit back down — I have a story to tell.' },

      { t: 'narrate', text: 'Faust sits. Dickens Dean signals the bar wench for more booze.' },
      { t: 'say', char: 'Faust',        expr: 'neutral', text: 'Make it quick. Feels I may wake any minute.' },
      { t: 'say', char: 'Dickens Dean', role: 'Antagonist', expr: 'neutral', text: 'This is our world. We\'ve got you a spell.' },
      { t: 'say', char: 'Joan',         expr: 'neutral', text: 'No spoilers.' },

      { t: 'jump', scene: 'vol1_ch4_club_sharp' },
    ]
  },

  vol1_ch4_club_sharp: {
    id: 'vol1_ch4_club_sharp', vol: 1, chapter: 4, type: 'chapter',
    title: 'Act One — Club #',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol1_club_sharp.jpg' },
      { t: 'hide', pos: 'left' }, { t: 'hide', pos: 'center' }, { t: 'hide', pos: 'right' },
      { t: 'interlude', text: 'Club #', sub: 'A logo from another volume', duration: 2400 },

      { t: 'narrate', text: 'Joan takes Faust by the hand and leads him to a beautiful car waiting outside. They get in, tear around town, and wind up at a club in the heart of nowhere, beating with life — people overflowing from its seams.' },

      { t: 'narrate', text: 'EXT. CLUB SHARP — NIGHT' },
      { t: 'narrate', text: 'Club Sharp has a # for a logo. Dickens Dean seems to have the run of the place. There is a gigantic arcade downstairs, several dance floors, and a bowling alley. Music and movement seem to flow from one area to the next.' },

      { t: 'show', char: 'dickens_dean', expr: 'neutral', pos: 'right' },
      { t: 'show', char: 'joan',         expr: 'neutral', pos: 'left'  },

      { t: 'say', char: 'Dickens Dean', role: 'Antagonist', expr: 'neutral', text: 'We fled worlds of ruin and decay. Making something new. Because as ideas, Joan and I were strongest.' },
      { t: 'say', char: 'Joan',         expr: 'neutral', text: 'We were each made in some way perfect — reflecting a singular point of view.' },

      { t: 'say', char: 'Dickens Dean', role: 'Antagonist', expr: 'neutral', text: 'Have you met this creator yet? And do I get my chance?' },
      { t: 'say', char: 'Joan',         expr: 'neutral', text: 'Gosh, no. We seem to exist to please him — much as he exists to please his own creator.' },

      { t: 'say', char: 'Dickens Dean', role: 'Antagonist', expr: 'neutral', text: 'And so on, and so forth. Until we finite-loop back in on ourselves. But let\'s not get ahead of the narrative.' },
      { t: 'say', char: 'Joan',         expr: 'neutral', text: 'But understand — this knowledge hides a terrible price.' },

      { t: 'say', char: 'Faust',        expr: 'neutral', text: 'Doesn\'t it always?' },

      { t: 'say', char: 'Dickens Dean', role: 'Antagonist', expr: 'neutral', text: 'Just by coming here and meeting with us — you\'ve begun to split your reality into many pieces. You have to be careful with this wonderful life you\'ve been given. Respect others in your journeys. Watch for signs and patterns. And reflect inwardly as often as you can.' },

      { t: 'say', char: 'Joan',         expr: 'neutral', text: 'Insanity will try to breach your firewall. Corrupt your data. So fortify your defense.' },
      { t: 'say', char: 'Dickens Dean', role: 'Antagonist', expr: 'neutral', text: 'No joke. Mania creeps inside. So you either have to want it in you — or not.' },

      { t: 'choice', opts: [
        { text: '"What if insanity was a large part of me to begin with?"', goto: 21 },
        { text: '"Then I\'ll fortify. I have things to make."',               goto: 24 },
        { text: '[Say nothing. Watch the dance floors.]',                    goto: 27 },
      ]},

      // goto 21 — the joke that isn't
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'What if insanity was a large part of me to begin with?' },
      { t: 'say', char: 'Joan',  expr: 'neutral', text: 'You shouldn\'t joke. That\'s no joke.' },
      { t: 'jump', scene: 'vol1_ch4_club_sharp_b' },
      // goto 24 — fortify
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'Then I\'ll fortify. I have things to make. I\'ll guard the walls.' },
      { t: 'say', char: 'Joan',  expr: 'neutral', text: 'Good answer. Mostly.' },
      { t: 'jump', scene: 'vol1_ch4_club_sharp_b' },
      // goto 27 — silent
      { t: 'narrate', text: 'You watch the floors below shift and refract. The dancers are not quite synchronized but are not quite not, either. Joan lets the silence sit. Dickens Dean smiles in a register Faust has not seen.' },
      { t: 'jump', scene: 'vol1_ch4_club_sharp_b' },
    ]
  },

  vol1_ch4_club_sharp_b: {
    id: 'vol1_ch4_club_sharp_b', vol: 1, chapter: 4, type: 'chapter',
    title: 'Act One — Too Real',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol1_club_sharp.jpg' },
      { t: 'show', char: 'dickens_dean', expr: 'neutral', pos: 'right' },
      { t: 'show', char: 'joan',         expr: 'neutral', pos: 'left'  },

      { t: 'say', char: 'Faust',        expr: 'neutral', text: 'Coming from my feminine ideal — hello there. Are you trying to seduce me?' },
      { t: 'say', char: 'Joan',         expr: 'neutral', text: 'You\'ve had too much to drink. Stop skipping script.' },

      { t: 'say', char: 'Faust',        expr: 'neutral', text: 'I play my part well enough, lovely miss. But — clearly — I presume.' },
      { t: 'say', char: 'Joan',         expr: 'neutral', text: 'Clearly, you need a shot of absinthe to clear away cobwebs.' },

      { t: 'say', char: 'Dickens Dean', role: 'Antagonist', expr: 'neutral', text: 'You are a mean one when you\'re beguiled.' },
      { t: 'say', char: 'Joan',         expr: 'neutral', text: 'I\'ve got my own hero\'s journey to complete. So stop making eyes at me — the both of you.' },

      { t: 'narrate', text: 'Dickens Dean shrugs. Faust looks at her, trying to get at her. He leans in close.' },

      { t: 'say', char: 'Faust', expr: 'neutral', text: 'I can see every last eyelash and blemish of skin. You are far too real in my mind\'s eye to be a dream.' },
      { t: 'say', char: 'Joan',  expr: 'neutral', text: 'To me — you aren\'t real enough yet. You\'re so much smoke and ash. I don\'t know whether to breathe you in or spit you out.' },

      { t: 'narrate', text: 'Faust straightens up.' },

      { t: 'choice', opts: [
        { text: '"Can I see you again tomorrow?"',          goto: 14 },
        { text: '"I have to go. The friends I came with."', goto: 18 },
      ]},

      // goto 14 — see her again
      { t: 'say', char: 'Faust',        expr: 'neutral', text: 'Can I see you again tomorrow?' },
      { t: 'say', char: 'Dickens Dean', role: 'Antagonist', expr: 'neutral', text: 'Her — no. Me — yes.' },
      { t: 'flag', key: 'faust_asked_for_joan', val: true },
      { t: 'jump', scene: 'vol1_ch4_waking' },
      // goto 18 — leave
      { t: 'say', char: 'Faust',        expr: 'neutral', text: 'I have to go. The friends I came with. I shouldn\'t leave them.' },
      { t: 'say', char: 'Dickens Dean', role: 'Antagonist', expr: 'neutral', text: 'A loyal man. We\'ll see you again. You won\'t have to find us.' },
      { t: 'flag', key: 'faust_asked_for_joan', val: false },
      { t: 'jump', scene: 'vol1_ch4_waking' },
    ]
  },

  vol1_ch4_waking: {
    id: 'vol1_ch4_waking', vol: 1, chapter: 4, type: 'chapter',
    title: 'Act One — Waking',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol1_club_sharp.jpg' },
      { t: 'show', char: 'dickens_dean', expr: 'neutral', pos: 'right' },
      { t: 'show', char: 'joan',         expr: 'neutral', pos: 'left'  },

      { t: 'say', char: 'Faust',        expr: 'neutral', text: 'As far as drunken dreams go — this one is ridiculous.' },
      { t: 'say', char: 'Joan',         expr: 'neutral', text: 'John Faust — you need to wake up. See? It\'s all the same, silly.' },
      { t: 'say', char: 'Dickens Dean', role: 'Antagonist', expr: 'neutral', text: 'Worlds will speak to you in signs. Show you the way to the center of it all.' },

      { t: 'hide', pos: 'left' }, { t: 'hide', pos: 'right' },
      { t: 'bg', src: 'assets/backgrounds/vol1_faust_bedroom_night.jpg' },
      { t: 'interlude', text: '04:00', sub: 'The alarm again', duration: 2200 },

      { t: 'narrate', text: 'John Faust wakes up in his bed. His alarm is ringing. It is 4:00 am. He turns the alarm off and goes back to bed.' },

      { t: 'show', char: 'faust', expr: 'neutral', pos: 'center' },
      { t: 'say', char: 'Faust', expr: 'neutral', text: 'I clearly have no grip — and feel my world spin fast and loose.' },

      { t: 'narrate', text: 'John gets up. To the bathroom. Pukes in the toilet.' },
      { t: 'narrate', text: 'An abrupt and ugly scene end.' },

      { t: 'flag', key: 'vol1_ch4_complete', val: true },
      { t: 'narrate', text: '— End of Act One, Part III —' },
      { t: 'end' },
    ]
  },


  // ── Vol 2 · SMALL WOOD VOLUMES · Literary skin ──────────────────────────

  // ── Vol 2 · Title Page & Preface ───────────────────────────────────────────
  // Cover, author's note, preface. Frames the book as a notebook lost at a
  // diner during a cross-country move, half-started by the author note voice
  // and finished by someone else — then found again years later in a copy
  // shop. Credited author on the title page: D.N. Dean (cf. Dickens N. Dean
  // / Nate Dean of Vol 7 and Faust's Antagonist in Vol 1 Ch 4).
  vol2_title: {
    id: 'vol2_title', vol: 2, chapter: 0, type: 'chapter',
    title: 'Title Page & Preface',
    nodes: [
      { t: 'bg', src: null },
      { t: 'bgm', src: 'assets/audio/bgm/vol2_ambient.mp3' },

      // ── Cover ────────────────────────────────────────────────────────────
      { t: 'interlude', text: 'Small Wood Volumes', sub: 'By D.N. Dean', duration: 4200 },
      { t: 'narrate', text: 'Small Wood Volumes.' },
      { t: 'narrate', text: 'By D.N. Dean.' },

      // ── Author's Note ────────────────────────────────────────────────────
      { t: 'interlude', text: "Author's Note", sub: '—', duration: 2200 },
      { t: 'narrate', text: 'Curiously enough, I\'ve never been a writer. I am a computer scientist at a local university who found this notebook left in a copy shop several years back, and lost track of it.' },
      { t: 'narrate', text: 'What\'s odd about my find is that it was written in an old notebook I\'d half-started and lost at some diner while my father moved us cross-country — and was later finished by someone else.' },
      { t: 'narrate', text: 'What are the odds, huh?' },

      // ── Preface ──────────────────────────────────────────────────────────
      { t: 'interlude', text: 'preface', sub: '', duration: 2000 },

      { t: 'narrate', text: 'You need a title, it says to me — the little voice behind my thoughts.' },
      { t: 'narrate', text: 'small wood volumes. (I fill this in later.)' },

      { t: 'narrate', text: 'Up awake at hours when the company I keep is made up of figments and fragments. I write because words keep coming — that is, the thoughts are neverending. I eat crumbs that are the remains of yesterday. The transition time between then and now, thoughts racing before the dawn of another day.' },
      { t: 'narrate', text: 'The frenzy takes me and I must keep going — I must not stop. I have to write about all of them. Those who know their place. The ones who live with damaged goods, whose only dream is to come up even on the karmic scale. My heart goes out to them, and their restless thoughts. Pollution of hurt and grief spills out like split trash bags on the sidewalk.' },
      { t: 'narrate', text: 'This is an essay on nothing. No thesis body to be found. An example made in maps on walls — delineating who we are by where we live. Status and circumstance. The rise and fall of a nobody. No name given. Small Town Blues.' },

      { t: 'narrate', text: 'Music sits softly on my ears. Headphones hug and comfort. I make up a fiction to dilute the facts of this life. My story is simple and easy, so I\'ll begin there and take you someplace else.' },

      { t: 'narrate', text: 'It\'s not that my history unnerves me — it is just that it has been so long since I\'ve sat down to write seriously, I don\'t think I can tell the truth without boring myself. So I must fabricate, and you must settle. You found these words and continue reading of your own accord.' },

      { t: 'narrate', text: 'I lived in a town called Small Wood, on the coast of Oregon. I moved from there three years ago, after many endings occurred all at once. I kept a diary while I was living there — collecting scraps of what I thought to be history, art, and a living fiction of the town I lived in.' },
      { t: 'narrate', text: 'I write this in recollection, and add the remnants from the old life where their place belongs. Know this is all a puzzle to me. Thousands of pieces, all touching and connecting in so many ways.' },

      { t: 'narrate', text: 'I\'m not sure which piece goes first.' },

      { t: 'narrate', text: 'This is a story not as it was, nor how I wanted it to be. It is the story of ghosts that live on, failures that haunt, peoples that persist, and death that goes unremarked upon.' },

      { t: 'narrate', text: 'There is no structure to the telling of this story. There is no one medium for ideas to stick to.' },

      { t: 'narrate', text: 'such is life.' },

      { t: 'narrate', text: 'A beginning, now — to set the stage, to pull the curtain back and have our narrator come in on cue.' },

      { t: 'flag', key: 'vol2_preface_read', val: true },
      { t: 'jump', scene: 'vol2_briar_falls_interlude' },
    ]
  },

  // ── Vol 2 · INTERLUDE — Briar Falls ────────────────────────────────────────
  // A rest stop and small park in Briar Falls, somewhere in the Small Wood,
  // mid-90s. A family stops their blue Chrysler minivan with faux wood trim.
  // Father, mother, teen brother, tween sister, and a notably intelligent
  // black-and-white border collie. They are background. You are not them.
  // You are someone else here at the rest stop. Hub-and-spoke. Subtle.

  vol2_briar_falls_interlude: {
    id: 'vol2_briar_falls_interlude', vol: 2, chapter: 1, type: 'interlude',
    title: 'Interlude — Briar Falls',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol2_briar_falls_rest_stop.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/vol2_rest_stop_wind.mp3' },
      { t: 'interlude', text: 'Briar Falls', sub: 'Rest Stop · Small Wood · mid-nineties', duration: 3000 },

      { t: 'narrate', text: 'The exit comes up after a long curve and the sign for it is the same brown as every other state-park sign and the same letters in the same recessed sans-serif. BRIAR FALLS REST AREA — 1/4 MI. Underneath, a smaller sign: NO OVERNIGHT PARKING. NO DUMPING. PLEASE LATCH GATE.' },
      { t: 'narrate', text: 'The asphalt of the rest stop is grey-going-on-green where the moss has the upper hand. A picnic shelter, a low brick building with two doors marked, a wooden box at the trailhead, a curve of railing where the bluff begins.' },

      { t: 'narrate', text: 'A blue Chrysler minivan with faux wood trim pulls in. Oregon plates, or close enough. The side door slides open with the particular complaint side doors of that vintage made. A family gets out the way families get out at rest stops in the middle of a long day — without ceremony, without conversation, in a known order.' },
      { t: 'narrate', text: 'Father, with the keys still in his hand. Mother, pulling a sweatshirt over a t-shirt because the wood is cooler than the highway was. Teenage brother, headphones already in, the cord disappearing into the kangaroo pocket of his hoodie. Tween sister, the last out, sneakers untied on purpose. And a black-and-white border collie, who waits to be told and then is not told and then gets out anyway.' },

      { t: 'narrate', text: 'The dog stands a moment at the open door and looks across the lot. Not at anything in the lot. Past it. At something it has decided about.' },
      { t: 'narrate', text: 'You are also here. You came in earlier. They have not noticed you. They will not notice you. That is the way of rest stops. You have some time before you have to be anywhere again.' },

      { t: 'jump', scene: 'vol2_bf_hub' },
    ]
  },

  vol2_bf_hub: {
    id: 'vol2_bf_hub', vol: 2, chapter: 1, type: 'interlude',
    title: 'Briar Falls — what to look at',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol2_briar_falls_rest_stop.jpg' },
      { t: 'hide', pos: 'left' }, { t: 'hide', pos: 'center' }, { t: 'hide', pos: 'right' },
      { t: 'choice', opts: [
        { text: 'The low brick building.',                  scene: 'vol2_bf_building' },
        { text: 'The picnic shelter.',                       scene: 'vol2_bf_picnic'   },
        { text: 'The wooden box at the trailhead.',          scene: 'vol2_bf_trail'    },
        { text: 'Down to the railing. The falls.',           scene: 'vol2_bf_overlook' },
        { text: 'The family. From a distance.',              scene: 'vol2_bf_lot'      },
        { text: 'The dog. It has not moved.',                scene: 'vol2_bf_dog'      },
        { text: 'Get back on the road.',                     scene: 'vol2_bf_end'      },
      ]},
    ]
  },

  vol2_bf_building: {
    id: 'vol2_bf_building', vol: 2, chapter: 1, type: 'interlude',
    title: 'Briar Falls — the building',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol2_briar_falls_building.jpg' },
      { t: 'narrate', text: 'The building is brick painted brown, then painted brown again. Two doors. One stick figure with a triangle skirt; one without. Between them, a vending machine with the row of selection buttons taped over except for B-4. A handwritten sign on the tape reads: B-4 ONLY. NO REFUNDS. SORRY.' },
      { t: 'narrate', text: 'A pay phone bracketed to the wall outside. The receiver dangles by the cord. The coin-return slot has been pried at by something with a flathead. Above it, a small sticker for COLLECT CALLS DIAL 0-700 and a faded one for 1-800-COLLECT that has Carrot Top on it.' },

      { t: 'narrate', text: 'A brochure rack just inside the alcove. The plastic slots are the kind that always sag at one end. The brochures, top to bottom:' },
      { t: 'narrate', text: 'COVERED BRIDGES OF YAMHILL COUNTY — three creased, two fresh.' },
      { t: 'narrate', text: 'SMOLVUD: THE TOWN AT THE EDGE OF THE WOOD — green ink on cream stock, illustrated with a hand-drawn sanderling. The address on the back has been corrected in pen.' },
      { t: 'narrate', text: 'THE MISSING LINK — eat, drink, wait. A diner you have not been to. The hand-printed map on the back shows a bus depot apron and a single dotted line that does not end. Underneath, in different ink: Shillelagh stops daily. Hours of operation: Yes.' },
      { t: 'narrate', text: 'A flyer, taped to the inside of the alcove, no border, just a photocopied face: HAVE YOU SEEN THIS MAN. Underneath, a young man in a trench coat at what appears to be a bus depot bench. The flyer says CONTACT NATE D. and a phone number. The flyer says LAST SEEN: rain. The date is illegible.' },

      { t: 'narrate', text: 'You stand in the alcove a moment longer. The pay phone does not ring. You were not expecting it to.' },
      { t: 'jump', scene: 'vol2_bf_hub' },
    ]
  },

  vol2_bf_picnic: {
    id: 'vol2_bf_picnic', vol: 2, chapter: 1, type: 'interlude',
    title: 'Briar Falls — the picnic shelter',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol2_briar_falls_picnic.jpg' },
      { t: 'narrate', text: 'The shelter is a six-by-six post-and-beam square with a corrugated metal roof and three picnic tables under it. Two tables are bolted to the slab. The third is loose, set off-square, like somebody had been planning to make off with it and changed their mind.' },

      { t: 'narrate', text: 'On the nearest table, somebody has carved into the wood with what looks like a key:' },
      { t: 'narrate', text: 'F + B   1994 — and beside it, in different hand and earlier wood, J. and someone has filled in the rest of the name with a knife and then someone else has scratched the rest back out, leaving J. alone with an unfinished hyphen.' },
      { t: 'narrate', text: 'Below those: a small careful sanderling, the same shorebird the Smolvud brochure has on its cover. Whoever drew it loved the bird.' },

      { t: 'narrate', text: 'The shelter floor is concrete and dry. Cigarette butts swept toward the corner without being picked up. A flattened pack of Camel Lights, the soft kind. A bottle cap from a Henry Weinhard\'s root beer.' },

      { t: 'narrate', text: 'On the middle table, a paperback face-down, splayed, the spine cracked. The cover faces away. You turn it over with two fingers. It is a copy of GREAT EXPECTATIONS, the Bantam paperback, the schoolbook edition. Somebody has dog-eared one page and left it; somebody has, in pencil, underlined a single sentence about waiting. You do not memorize the sentence. You will think you remember it later and you will be wrong about it.' },

      { t: 'narrate', text: 'A pair of sunglasses on the bench, lenses snapped, one ear missing. Not anyone\'s. Just left.' },
      { t: 'jump', scene: 'vol2_bf_hub' },
    ]
  },

  vol2_bf_trail: {
    id: 'vol2_bf_trail', vol: 2, chapter: 1, type: 'interlude',
    title: 'Briar Falls — the trailhead',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol2_briar_falls_trail.jpg' },
      { t: 'narrate', text: 'The wooden box at the trailhead is the standard kind. Lid hinged from the back. A pencil on a string. A laminated page bolted to the inside of the lid: PLEASE SIGN IN. NAME. DATE. PARTY SIZE. DIRECTION. ESTIMATED RETURN.' },
      { t: 'narrate', text: 'You open it.' },

      { t: 'narrate', text: 'The current sheet is the third or fourth. The corners are damp. The names go back about two weeks. The handwriting changes hand by hand and tells you very little.' },
      { t: 'narrate', text: 'Most of the entries say UP TO THE FALLS AND BACK. A few have the falls as their direction and a return time that nobody crossed off. Those are not necessarily ominous. People forget.' },
      { t: 'narrate', text: 'Halfway down the page, in a tidy small hand: DEAN, N. — PARTY 1 — direction THE TOWER — return: not this time.' },
      { t: 'narrate', text: 'The signature beside the entry is a sanderling, again. Drawn small. Loved.' },

      { t: 'narrate', text: 'Behind the laminated page, taped to the wood, is a square Polaroid. The polaroid is of a young man in a trench coat at the depot bench, the rain matting his hair flat. The seams of the coat have a thin, steady light. Somebody has written along the white border, in the same small hand: He came through here on his way. He was kind. Do not stop him.' },

      { t: 'narrate', text: 'The trail beyond the box runs east into Douglas fir and laurel. The sign at the head reads: 0.4 MI TO THE FALLS. 1.2 MI TO THE OLD TOWER (DISCONTINUED — DO NOT). The DO NOT has been added in pencil. It does not look recent. It does not look old, either.' },
      { t: 'jump', scene: 'vol2_bf_hub' },
    ]
  },

  vol2_bf_overlook: {
    id: 'vol2_bf_overlook', vol: 2, chapter: 1, type: 'interlude',
    title: 'Briar Falls — the falls',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol2_briar_falls_overlook.jpg' },
      { t: 'narrate', text: 'The railing is bolted into a slab of basalt at the edge of the lot, where the asphalt stops with no fanfare and the bluff begins.' },
      { t: 'narrate', text: 'Briar Falls drop in two stages, then a third you cannot see. The first stage is the long shallow one — the water spreading and slowing along a tilted shelf, white at the lip, then the second stage takes the volume and concentrates it and the water remembers what it is and lets go. The third stage is where the canyon turns and the falls go into the woods proper. The mist comes back up from the third stage as a slow soft column, and the column does not move with the wind.' },

      { t: 'narrate', text: 'The mist coming up the column is warmer than the air at the railing. You feel it on the underside of your forearms.' },

      { t: 'narrate', text: 'Tied to the railing, with three half-hitches and a finish that means whoever tied it tied a lot of knots in their life: a faded piece of red ribbon and, attached to the ribbon by a brass loop, a key. Brass-color, but stamped on the side, in the kind of stamp that only counts: 707. It is not for any lock that is here.' },

      { t: 'narrate', text: 'You consider untying the ribbon. You do not. It is not your knot.' },

      { t: 'narrate', text: 'Below the railing, on the wet shelf above the second stage, a single feather. Long and grey, with a white tip. Not a sanderling. Larger. Not a hawk either. You decide, against your better judgement, to forget you saw the feather.' },
      { t: 'jump', scene: 'vol2_bf_hub' },
    ]
  },

  vol2_bf_lot: {
    id: 'vol2_bf_lot', vol: 2, chapter: 1, type: 'interlude',
    title: 'Briar Falls — the family',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol2_briar_falls_rest_stop.jpg' },
      { t: 'narrate', text: 'You watch them the way you watch people at rest stops, which is briefly and without engagement. They are not interesting and they are not uninteresting. They are themselves.' },

      { t: 'narrate', text: 'The father is at the back of the van with the hatch open, looking into a cooler the way a man looks into a cooler he packed three hours ago and is now reconsidering. He pulls out a Capri Sun and a Diet Pepsi. He leaves the cooler open.' },
      { t: 'narrate', text: 'The mother is on the bench beside the building, smoking. You did not see her light the cigarette. The Walkman in her lap is playing something with strings; you can hear the high end leak out of the cheap foam ear pads when she leans forward to ash.' },
      { t: 'narrate', text: 'The teenage brother is walking the perimeter of the lot at the deliberate pace of someone whose headphones have replaced the world. He stops at the picnic shelter. He looks at the paperback. He does not turn it over. He keeps walking.' },
      { t: 'narrate', text: 'The tween sister is at the brochure rack. She takes one of everything. She always takes one of everything. She is folding the Missing Link brochure into a small careful square, the way you fold something you are going to put in a sock drawer and find seven years later and not throw out.' },

      { t: 'narrate', text: 'The dog is not with any of them. The dog is at the edge of the lot, where the asphalt stops, looking at the trailhead box.' },
      { t: 'jump', scene: 'vol2_bf_hub' },
    ]
  },

  vol2_bf_dog: {
    id: 'vol2_bf_dog', vol: 2, chapter: 1, type: 'interlude',
    title: 'Briar Falls — the dog',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol2_briar_falls_trail.jpg' },
      { t: 'narrate', text: 'The border collie is fourteen feet from the trailhead and you are six feet from the border collie. The dog is sitting. The dog has been sitting for longer than border collies sit.' },

      { t: 'narrate', text: 'You watch the dog watch the box. It is not posturing. It is not nervous. It is doing the thing a dog does when a dog has read a room and is waiting to see whether you have read it also.' },

      { t: 'narrate', text: 'You move two steps closer. The dog turns its head and looks at you, square. The black-and-white of its face is the careful, planned black-and-white of border collies. The eyes are heterochromatic — one brown, one a pale unsettling blue.' },
      { t: 'narrate', text: 'It does not bark. It does not wag. It looks at you the way a person looks at someone they recognize but have not decided whether to greet.' },

      { t: 'narrate', text: 'After a count, it lowers its head — not down, just an inch, deliberate — and looks back at the trailhead box. Then back at you. Then the box.' },
      { t: 'narrate', text: 'You understand, the way you sometimes understand a thing from a dog, that you have been shown something. You also understand that this dog could, if it wanted to, tell its family any number of things, and has chosen, today, to tell them none of them.' },

      { t: 'narrate', text: 'You take a step back. The dog releases you with its eyes. It is a release. You feel it.' },
      { t: 'jump', scene: 'vol2_bf_hub' },
    ]
  },

  vol2_bf_end: {
    id: 'vol2_bf_end', vol: 2, chapter: 1, type: 'interlude',
    title: 'Briar Falls — leaving',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol2_briar_falls_rest_stop.jpg' },
      { t: 'narrate', text: 'You walk back across the lot. The mother grinds her cigarette out on the underside of the bench, the way smokers do when they are about to get back into a vehicle they are not going to smoke in. The Walkman goes into the pocket of the sweatshirt. The Diet Pepsi is half gone and the father is going to finish it in the next mile.' },
      { t: 'narrate', text: 'The teenage brother is already in the back row of the van, headphones still in, head against the window glass. The tween sister climbs into the middle row, the folded brochure in her fist. She will not unfold it for years.' },

      { t: 'narrate', text: 'The dog has come back from the trailhead. It waits at the open door, looks once at the box behind it, and gets in. It settles between the two rows of seats and does not look out the window.' },
      { t: 'narrate', text: 'The side door slides shut. The minivan starts. The faux wood trim catches the afternoon in the particular way faux wood trim does, which is briefly.' },
      { t: 'narrate', text: 'They pull out of the lot. You watch the rear plate until the curve takes it.' },

      { t: 'narrate', text: 'The rest stop is quiet again. The mist from the third stage of the falls comes up the column in the windless air. The 707 key is still tied to the railing. The paperback is still face-down on the middle table. The dog is gone.' },

      { t: 'flag', key: 'vol2_briar_falls_visited', val: true },
      { t: 'interlude', text: 'End of Interlude', sub: 'Briar Falls', duration: 2600 },
      { t: 'jump', scene: 'vol2_ch1_history_one' },
    ]
  },

  // ── Vol 2 · Chapter 1 — i. A Brief History of Me, Part One ─────────────────
  // First-person memoir from the Vol 2 narrator (D.N. Dean). Age twenty-six,
  // looking back on the year his family moved from Caracas to Small Wood.
  // Direct continuity with Vol 7: Little Switzerland Road, the farmhouse,
  // the football coach business, the chemistry-class incident. Ends on the
  // discovery of the crumpled barn — Jiggles the Juggler, the carved mermaid
  // sign, the Cliffside Circus Attraction.

  vol2_ch1_history_one: {
    id: 'vol2_ch1_history_one', vol: 2, chapter: 1, type: 'chapter',
    title: 'i. A Brief History of Me, Part One',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol2_little_switzerland.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/vol2_ambient.mp3' },
      { t: 'interlude', text: 'i.  a brief history of me', sub: 'part one', duration: 3000 },

      { t: 'narrate', text: 'This will not be a typical bit of biography.' },

      { t: 'narrate', text: 'At this moment in time I am twenty-six years old — far more potential than actual. I was just recently told this by my mother. That I am stunted developmentally. Not as much an adult as I should be. That I regressed for many years by staying in Small Wood when I should have been moving forward.' },
      { t: 'narrate', text: 'This latest retreat was my second stint in Small Wood. The first was years before.' },

      { t: 'narrate', text: 'My family moved to Small Wood the summer after my sophomore year — spent overseas in Caracas, Venezuela. My dad was out of work, and we fell back to regroup in the states on my grandmother\'s unused piece of country property.' },
      { t: 'narrate', text: 'If I was being more accurate — my father was enjoying the retirement he would not naturally receive.' },
      { t: 'narrate', text: 'Part of me thinks this place is where his ending began.' },

      // ── The house ────────────────────────────────────────────────────────
      { t: 'narrate', text: 'I found it to be a beautiful but fallen-upon-disrepair ranch house.' },
      { t: 'narrate', text: 'It was two stories. Yellowed and mildewed on the outside. Shingles split and prone to falling loose. The house proper could be reached driving down from the coastal highway by turning off a small, one-lane pebble road marked by a sign stating simply — Little Switzerland.' },

      { t: 'narrate', text: 'Surrounding the property were cow pastures, bordered on one edge by a river. The other — primal woods descend down to touch the valley.' },

      { t: 'narrate', text: 'It was a quiet place. Neighbors were distant and never encountered with any real frequency. Cows got loose. The river flooded. Trees split and fell across the road. These were typical of the intrusions upon day-to-day life.' },

      // ── Returning to the house ───────────────────────────────────────────
      { t: 'narrate', text: 'I had spent holidays in the house years before. I was familiar — but it was not my home. It was my grandmother\'s. It had a comfortable, lonesome feel.' },
      { t: 'narrate', text: 'But I was a teenager — coming from a very large, alien metropole, moving to a small, isolated house within a proportionately small, isolated community that gnawed at me. I was not at heart a spoiled bright-lights big-city boy. I did not complain about the sudden and drastic change to life, and the pace of life. Yet I was always self-aware, and out of place.' },
      { t: 'narrate', text: 'I lacked the skills my father and sister had to tend the land and raise livestock in limited quantities. I helped out where I could that summer — pulling weeds, feeding grass to the beasts, unpacking and moving into the place proper — but I was not an easy fit with the new accommodations.' },

      // ── Nature, second skin ──────────────────────────────────────────────
      { t: 'narrate', text: 'Nature and the earth to me were something easy and docile. Not wild and bursting at the seams of reality and basic human existence. I was used to orderly human constructs of society — not encroaching and persistent attacks upon my flesh and character.' },
      { t: 'narrate', text: 'I knew the longer I was here, the longer it would get into me. At first, I was frightened of this feeling. Then it became like a second primal skin, or suit, I could dress up in.' },

      { t: 'narrate', text: 'I remembered skinny-dipping in the chill cold waters of the river. Of hopping the fence and dodging cow pies in a mad rush to the water — and not to catch the bull\'s attention. I had brought friends to vacation with me here in my youth, and those memories lingered around the place with an almost empty solace.' },

      { t: 'narrate', text: 'I was a true teenager. Halfway between innocence and aged. The world had wizened me beyond my years. My family always a wonderful blessing to have as moral poles in my life. My parents were smart, if not brilliant, in ways I\'d never understand. Both so very warm, and wise, and open to my development as a human being — and my sister\'s as well.' },

      // ── Football & the rumor ─────────────────────────────────────────────
      { t: 'narrate', text: 'My father, on his trips into town, started rumors about a promising young athlete from Venezuela. And before long I was signed up for the local high school football team. I had no experience playing the game. None at all.' },
      { t: 'narrate', text: 'My dad made a name for himself in his youth, owing much of his collegiate opportunity to the sport. I was expected to follow in his footsteps — at least in theory, if not actual ability.' },
      { t: 'narrate', text: 'To appeal to my intellect and curiosity, my father hailed high school football as a cultural experience. He assured me — in a mocking tone — that I would get to know and appreciate the locals. Their customs and beliefs.' },
      { t: 'narrate', text: 'Whenever he was playful, I always felt the sharpest pangs of joyful fear.' },

      // ── Running the road ─────────────────────────────────────────────────
      { t: 'bg', src: 'assets/backgrounds/vol2_road_running.jpg' },
      { t: 'narrate', text: 'So in preparation for joining the team, I began running along the road — up and down the property — to get myself in shape and make a better case for why this strange, tall, halfway-foreign boy should earn a spot on an already established dynasty.' },
      { t: 'narrate', text: 'I had routinely generalized that the people of Small Wood were nothing if not unaccepting and distrusting of outsiders. Which turned out to be not far from the truth. That element is always going to be there, as it is human nature. Some towns scream to be seen by the greater cast of the public\'s eye. Others retreat — and you have to wonder why.' },

      { t: 'narrate', text: 'Nothing against small towns. But with so few people, the degrees of personality are so sharply honed, and individual lifetimes so distinct, that it becomes its own parallel reality. For me, the fear of the small town was nestled firmly in my reading. H.P. Lovecraft. Stephen King. Edgar Allan Poe — all finely honed the small-town paranoia in me. My literary, thematic, cultural bias.' },

      { t: 'narrate', text: 'For the first few days of preparing to join the football squad —' },
      { t: 'narrate', text: 'I was sweating, and seeing the sights around me as landmarks I had to pass on the way to better shape.' },
      { t: 'narrate', text: 'Breathing in and out commenced with a more regular rhythm. Pounding my feet to the ground, paced to the beat of my racing heart.' },

      { t: 'narrate', text: 'After several stretches of growing boredom and familiarity with my route, I branched off — to scale the terrain, to stimulate my own sense of adventure.' },
      { t: 'narrate', text: 'Knotted paths leading both up and down the road, twisting alongside cricks, emerging upon tool shed areas, out-of-the-way pole barns, and the remains of fallen-in houses. Debris of lives lost in transition. Abandoned and forgotten.' },

      // ── The crumpled barn ────────────────────────────────────────────────
      { t: 'bg', src: 'assets/backgrounds/vol2_crumpled_barn_ext.jpg' },
      { t: 'interlude', text: 'The Crumpled Barn', sub: 'Off the road · Foliage', duration: 2200 },

      { t: 'narrate', text: 'The first time I saw the crumpled barn, I thought it part of the hill. Foliage consuming much of the exterior — more negative space than positive. I pushed my way in and found remnants in corners, hidden in shadows. The sunlight poking through, bleached, crumbled the flesh in places.' },

      { t: 'bg', src: 'assets/backgrounds/vol2_barn_interior.jpg' },
      { t: 'narrate', text: 'A cabinet of sorts held a broken marionette, sagging at the hip. At one time it danced a vaudevillian stage. But the glass fourth wall was broken. The buttons and levers that controlled the nickelodeon automaton still worked — herking and jerking the sneering puppet performer this way and that.' },
      { t: 'narrate', text: 'His name in red paint: Jiggles the Juggler.' },

      { t: 'narrate', text: 'His head came to rest against his shoulder after the exhausting performance. His smile and jeering eyes set upon a something across the way.' },

      { t: 'narrate', text: 'Half hanging from the wall as audience before him — a carved wooden sign.' },
      { t: 'narrate', text: 'A beautiful woman sat on a rock, naked from the waist up. Her dark hair covered just enough of her chest, falling down below her waist. The rest of her figure was the product of an artist\'s imagination — a long bluefish tail that hugged the rock, heavy surf crashed up behind her.' },
      { t: 'narrate', text: 'In old script was writ —' },
      { t: 'narrate', text: 'Come Visit Today. A Twisted Beauty and a Beast. Only at The Cliffside Circus Attraction —' },

      { t: 'flag', key: 'vol2_found_jiggles', val: true },
      { t: 'flag', key: 'vol2_cliffside_circus_seen', val: true },

      { t: 'interlude', text: '...', sub: '— end of part one —', duration: 2800 },
      { t: 'jump', scene: 'vol2_ch2_seagash' },
    ]
  },

  // ── Vol 2 · Chapter 2 — ii. The Siren of Seagash ───────────────────────────
  // Two stories braided. The historical case of Delores Wiebe (the mermaid of
  // the Cliffside Circus, 1900s) — and three Interludes drawn from the
  // narrator's own teenage time in Small Wood: the Venezuelan dream, the
  // Grunion Festival kiss, and the school newspaper. The braid is the chapter.

  vol2_ch2_seagash: {
    id: 'vol2_ch2_seagash', vol: 2, chapter: 2, type: 'chapter',
    title: 'ii. The Siren of Seagash',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol2_seagash_circus_old.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/vol2_seagash_drone.mp3' },
      { t: 'interlude', text: 'ii. The Siren of Seagash', sub: '— A history, with interludes —', duration: 3200 },

      // ── Delores Wiebe ────────────────────────────────────────────────────
      { t: 'narrate', text: 'Her real name was Delores Wiebe.' },
      { t: 'narrate', text: 'Born in the late 1800s. Her legs fused together during development in her mother\'s womb, and her toes splayed out like long thin fingers — upon which thin webbing crept part way down the lengths, joining each digit.' },
      { t: 'narrate', text: 'A man collecting freaks squinted in just the right light and saw himself a genuine mermaid.' },

      { t: 'narrate', text: 'His name was Eric Jarvis. A showman and grifter who was aging and looking to set down roots. Delores\'s parents did not abandon her so much as sell her — exhausted from the efforts of rearing her. No doubt they saw the charms of her youth slowly twisted into a parody of adolescence.' },
      { t: 'narrate', text: 'I did not learn the daily details of her life. But I could imagine them unpleasant.' },
      { t: 'narrate', text: 'To sell his attraction, Jarvis stripped young Delores naked and had someone carry her onto a small, semi-aquatic stage with an unnatural island — for her to pine at young men from a distance. All for the cost of a few coins.' },

      // ── Frame: how the story came to me ──────────────────────────────────
      { t: 'narrate', text: 'I don\'t know why I started researching the mermaid. But I was intrigued. I knew of the Fiji Mermaid — a con job of P.T. Barnum — and wondered if this Siren may also be the somewhat convincing chimerical concoction of an over-stimulated taxidermist.' },
      { t: 'narrate', text: 'But Ms. Wiebe was no shaved monkey fused to a tuna. I found no other pictures or photographs of her beyond the initial discovery of the carved wooden advertisement.' },
      { t: 'narrate', text: 'In Small Wood\'s Elk Lodge, a newspaper clipping existed to reinforce her historical existence. I will return to its significance later on.' },

      { t: 'jump', scene: 'vol2_ch2_interlude_one' },
    ]
  },

  vol2_ch2_interlude_one: {
    id: 'vol2_ch2_interlude_one', vol: 2, chapter: 2, type: 'chapter',
    title: 'ii. Interlude — The Dream of the Sapo Falls',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol2_seagash_circus_old.jpg' },
      { t: 'interlude', text: 'Interlude', sub: '— first —', duration: 2200 },

      { t: 'narrate', text: 'It\'s not like I was poring over books to find out the history of this woman. The story of Delores came to me in fragments during the years I lived there — like most such stories that come out of small towns.' },
      { t: 'narrate', text: 'Understand that there is a veil about places like Small Wood, and that veil must be actively lifted, bit by bit, if you ever wish to see past the ignorance of the place and the populace. Small towns guard their secrets well — as the stain of time will forever tarnish family names, local businesses, and whole generations whose ideas and practices have fallen out of fashion with modern thinking.' },
      { t: 'narrate', text: 'If anything, Small Wood was a wonderful repository for wayward ideals. A time capsule sealed tight of mores, taboo, and tragedy.' },

      { t: 'bg', src: 'assets/backgrounds/vol2_sapo_falls.jpg' },
      { t: 'narrate', text: 'I had a dream about the mermaid while I was napping between morning and evening sessions of football practice. I was not expecting the sheer exhaustion of the routine, and did little for the first week besides eat, sleep, and bathe.' },
      { t: 'narrate', text: 'I remember the dream because it was vivid — and was soaking out my soreness in the large sunken first-floor bathtub when it occurred.' },

      { t: 'narrate', text: 'I was back in Venezuela. In the Canaima region — naturally rich in elevated tepuis, dense with dark green vegetation and flowing with towering waterfalls. A primal, unspoiled, and humbling place. Specifically, I was in one of the many smaller Sapo Falls — under the beat of the cascading wall.' },
      { t: 'narrate', text: 'The opaque film of water in front of me distorted the world outside the cool calm wet of the underneath. That\'s where she came to me. The mermaid.' },
      { t: 'narrate', text: 'Her lower half more eel than fish — leather thick with mucous. Her hair long, and looped in on itself wet. Her eyes curious but innocent. Like a neighbor\'s timid pet dog. Her lips found mine under the water and she pressed up against me.' },
      { t: 'narrate', text: 'It was a short dream. Far more sensual than sexual. I woke up with a nervous anxiety that had to do more with the imagery of being late for practice than of leaving behind a pastoral tropical dreamland.' },

      // ── May ──────────────────────────────────────────────────────────────
      { t: 'bg', src: 'assets/backgrounds/vol2_football_practice.jpg' },
      { t: 'narrate', text: 'I did not give the dream much thought. I had an eye on a teammate\'s sister who picked him up after practice — and she in fact occupied most of my waking fantasies.' },
      { t: 'narrate', text: 'A very thin dark-featured young woman. Exotic-looking to the thick and pale sorts such as myself who made up the majority in Small Wood. In two months\' time, my tan was quickly fading, and serious sunbathing out on the roof above my bedroom could not sustain what I\'d acquired at the equator.' },
      { t: 'narrate', text: 'Her name was May. And she was fun to think about — amid all the poundings in pads, the forced repetition of drilling, distracting my thoughts from the sounds of whistles and grunts.' },

      { t: 'narrate', text: 'She was casual, carefree, beautiful, and strong in self. Content just to sit around half the day and watch the boys practice football. She eventually settled on a star player and disappeared into the background noise of life once school started.' },
      { t: 'narrate', text: 'But May and I crossed paths many times, for many reasons. And her connection to Delores in my mind was always liquid — never firm. As May and Delores were as different as two individuals could be — living a hundred years and just one mile apart.' },

      { t: 'interlude', text: 'End interlude', sub: '', duration: 1800 },
      { t: 'jump', scene: 'vol2_ch2_cliffside' },
    ]
  },

  vol2_ch2_cliffside: {
    id: 'vol2_ch2_cliffside', vol: 2, chapter: 2, type: 'chapter',
    title: 'ii. The Cliffside Circus',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol2_cliffside_circus.jpg' },
      { t: 'interlude', text: 'The Cliffside Circus', sub: '1902 · the storm', duration: 2400 },

      { t: 'narrate', text: 'The Cliffside Circus looked more like a bordello or gaming parlor than an actual circus.' },
      { t: 'narrate', text: 'The main building was true enough built up along the edge of a cliff — overlooking jagged rock outcroppings, beaten raw by the harsh surf beneath. Smaller satellite lodgings and showrooms were built up in a semi-circle. An interrupted wagon train.' },

      // ── David Jarvis ─────────────────────────────────────────────────────
      { t: 'narrate', text: 'Eric Jarvis had an only child whose name was David. Since the age of fifteen, he was known as a hard-drinking, hard-hitting man. He was eventually killed at the age of thirty-three for allegedly raping a prominent mill owner\'s daughter.' },
      { t: 'narrate', text: 'David grew up on the road. A brutal life for any child of that era — leaving his siblings dead and buried across the landscape of his youth.' },
      { t: 'narrate', text: 'At his father\'s insistence, David had relations with many of the retinue retained at the circus. He often said he loved the face of Delores in more ways than one — but by all accounts he truly did care for the misshapen girl.' },
      { t: 'narrate', text: 'He was often seen nursing a bottle, standing watch over her like a protective older brother — intimidating the rowdies who\'d climb over the rail, wade into the pool, try and grab a feel.' },

      // ── Jeff Jarvis ──────────────────────────────────────────────────────
      { t: 'narrate', text: 'David\'s uncle, and Eric\'s brother, Jeff — was the primary attraction at the Cliffside Circus. A very talented and renowned clown and vaudevillian performer.' },
      { t: 'narrate', text: 'He was a bitter misogynist — though his disdain for life was spread pretty evenly out across all ethnicities, religious convictions, and sexual hang-ups. He was a foul and funny individual, and according to rumors, a very successful chicken hawk.' },
      { t: 'narrate', text: 'There were no surviving women in the Jarvis household, so Jeff took it upon himself to hold the dwindling family together.' },

      // ── The Ice Storm of 1902 ────────────────────────────────────────────
      { t: 'bg', src: 'assets/backgrounds/vol2_ice_storm.jpg' },
      { t: 'interlude', text: 'Spring · 1902', sub: 'An ice storm', duration: 2200 },

      { t: 'narrate', text: 'In the cold spring of 1902, an ice storm hit the coast hard. It was an unusual sight — to see frost in the sand, trees glazed in clear. It lasted close to a week and culminated with hundred-mile-an-hour winds, and a torrential wash of misery.' },
      { t: 'narrate', text: 'Water came down off the mountains in wicked gushes — uprooting trees and tearing through homes. The Cliffside Circus had the unfortunate position of being situated at a washout point on the coast.' },
      { t: 'narrate', text: 'The staff and workers worked in freezing conditions to salvage as much as they could, as fast as they could, before all was swept into sea.' },

      { t: 'narrate', text: 'Delores was forgotten about until the end. They heard her screaming as her tropical island enclosure was being slowly carried away. The shelf was sloughing off completely — weakened beyond the point of no return. She called out for help, but the ground was an unstable, sinking mess.' },
      { t: 'narrate', text: 'Invisible cracks in the earth filled with water, and a misplaced foot would at best sprain an ankle, at worst disappear you completely in quicksand.' },

      { t: 'narrate', text: 'A split tree had gashed David\'s arm — and while he was being tended to, he implored his father to go after the trapped girl. Eric got a team of able-bodied young men tethered by ropes and inched towards the stranded, perilous mermaid exhibit.' },
      { t: 'narrate', text: 'Reports differ about the exact timing of the collapse. But it was at this point that much of cliff gave away — and twenty feet of rock slid into the surf, taking several buildings down the side and leaving the remainder straddled on the very edge.' },

      { t: 'narrate', text: 'When the team got into the home, it was already at an angle — mud pouring into it, out a window. Delores was seen holding herself above the cold thick shock of it all — grasping for dear life to the tropical tree. She was screaming ever more desperately — but knew that to release hold would be to be swept out the back to her certain death.' },
      { t: 'narrate', text: 'Eric did his absolute best to save her life — but the timing was just not good enough. The rest of the shelf gave way and the house crumbled into the ocean — taking Delores Wiebe, Eric Jarvis, and two other men into the sea.' },

      { t: 'narrate', text: 'In the hours that followed, another team led by Jeff ventured to the rocky bottoms and recovered all the bodies — save for Delores. Whether or not Jeff refused to waste time to salvage the corpse of Delores, or it was never actually found — remains an unresolved sticking point.' },

      { t: 'narrate', text: 'Yet the story of Delores does not end there. As she was a tragic figure in life, she remained — if not became — an even more tragic figure in death.' },

      { t: 'flag', key: 'vol2_delores_lost', val: true },
      { t: 'jump', scene: 'vol2_ch2_interlude_two' },
    ]
  },

  vol2_ch2_interlude_two: {
    id: 'vol2_ch2_interlude_two', vol: 2, chapter: 2, type: 'chapter',
    title: 'ii. Second Interlude — The Grunion Festival',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol2_grunion_beach.jpg' },
      { t: 'interlude', text: 'second Interlude', sub: '— the grunion festival —', duration: 2400 },

      { t: 'narrate', text: 'The grunion is a fish. A small, silvery fish that crawls ashore to reproduce. It is in almost every way unimportant — save for the fact that Small Wood holds an annual grunion festival. A celebration dedicated to the peculiar lifecycle of the odd fish.' },
      { t: 'narrate', text: 'Local artisans and tourist shops promote the sale of special grunion bags, to make an extra buck or two off those who hold an opinion the event has actual importance or significance — all those who hope to sack a fish driven defenseless by its basest instinct to mate.' },

      // ── The Sunday ───────────────────────────────────────────────────────
      { t: 'narrate', text: 'It happened on a Sunday. I was kissed by a girl who had a boyfriend, and the kiss was not innocent, and if there was fault for it happening, it was my own.' },
      { t: 'narrate', text: 'I pushed her away and held her at arm\'s length and her smile, her heat, turned to cold sad anger as I watched her breathe in and out.' },

      { t: 'narrate', text: 'It all started earlier in the day. There was a beach cleanup my family was a part of. We scoured the coast for whatever nugget of refuse we could find. The problem of beach litter wasn\'t much of a problem, so the whole ordeal turned into a competition to see who could fill the inside of a whole trash bag — and even then, everyone joined together to work in teams.' },
      { t: 'narrate', text: 'The beach cleanup was a community event in preparation for the Grunion Festival — whereupon carnival equipment and food vendors were turned loose, high school beauty pageants held, middling prizes raffled off. Many of us found it somewhat shortsighted that we were putting all our effort into making the town look good before the whole ordeal, instead of after.' },
      { t: 'narrate', text: 'As it was, the festival put the whole town in a heightened sense of activity, and tempers ran short all the way down that one main street running from the Pacific coast inland. The town cop was being a bigger dick than usual to admittedly dick teenagers, and the four beauty pageant queens were in a cutthroat competition to build floats, bolster support, and be highly visible.' },

      // ── Katrina ──────────────────────────────────────────────────────────
      { t: 'narrate', text: 'Since it was down to the wire, all four girls were volunteering their last few hours helping with the beach cleanup — each going at it with their own brand of chipper fascism.' },
      { t: 'narrate', text: 'It was here I met Katrina. The youngest of the competing queens. Beautiful, feisty, and sometimes a chore. She liked most every person she dealt with and abstained from the gossipmongering that was so common in her clique.' },

      { t: 'narrate', text: 'She approached me during the cleanup, and wanted to know who I was and what my situation entailed. I knew right off she wasn\'t hitting on me — more of a determined curiosity. She engaged my younger sister as well — asking her just as many questions.' },
      { t: 'narrate', text: 'Katrina was the only daughter of Russian immigrants in the early seventies, born on these shores, instilled with a certain anxiety and worldlook that was at odds with the rest of the local community. Perhaps this common thread was the root of a friendship. Perhaps it was just that she was smart, friendly, and I gained much entertainment by working her into a frenzy.' },
      { t: 'narrate', text: 'Just to clear this up — Kate was not the girl who kissed me. That was Kate\'s friend, Shannon. Who I had met a few weeks back.' },

      // ── The Rec Center dance ────────────────────────────────────────────
      { t: 'bg', src: 'assets/backgrounds/vol2_rec_center_dance.jpg' },
      { t: 'narrate', text: 'My parents wanted a night together so they dropped my sister and I off at Small Wood Rec Center — a small, deteriorating one-room building on the main drag of town. Unfortunately, that night was a dance instead of the usual casual come-as-you-are games of foosball, pool, and scattered cartridges popped into an old Nintendo system.' },
      { t: 'narrate', text: 'A portly kid was the deejay and there were eight kids making an effort to shuffle in place uncomfortably, not counting my sister and I. We were standing at the entrance horrified, refusing to budge another step. A backwards glance confirmed that our ride had left for good.' },
      { t: 'narrate', text: 'Janess and I made for the back, where we arranged fold-up chairs in sitting positions and looked around for out-dated but readily available reading material. We could stonewall it together if we were careful — block out the horrible spectacle playing itself out.' },
      { t: 'narrate', text: 'The deejay sensed our combined resigned unease and came over to us, introduced himself while the music played itself in the background.' },

      // ── Jay Rose ─────────────────────────────────────────────────────────
      { t: 'narrate', text: 'His name was Jay Rose. And his aspirations, in no particular order, were actor, artist, and musician.' },
      { t: 'narrate', text: 'He was popular in the sense that everyone liked the guy. Not necessarily was he the most handsome, talented, charming person our age — but he possessed a good mix of qualities and had a confident awareness. Most notably, a calm in the face of failure.' },
      { t: 'narrate', text: 'He was outgoing and energetic. Very good at observing when people needed a solid word to pull them out of their own heads.' },

      { t: 'narrate', text: 'We never became fast friends but always respected and kept a charitable distance from each other. We were alike in many ways — so the desire to stand apart was quite strong. Rose was a senior above me, so there was a natural falling out of touch after the school year was over. And he disappeared and never came back.' },

      { t: 'narrate', text: 'Rose came up to inform me he\'d kill the dance soon due to the poor turn out, and instead open up the middle school gym to get a pick-up basketball game going.' },

      // ── The dance with Shannon ───────────────────────────────────────────
      { t: 'narrate', text: 'Before that happened, a girl I hadn\'t paid much attention to came up and asked me to dance. I shrugged a confused sort of agreement and we walked out hand in hand sideways to the obvious dead zone of couples shuffling around in place ever so suggestively to the time of the beat.' },
      { t: 'narrate', text: 'She had a big grin on her face and kept her head rested on my chest for most of the dance.' },
      { t: 'narrate', text: 'I wasn\'t really clued into the whole dating scene, and wasn\'t making any serious attempts at much of anything. If rumors that I was gay existed — which they probably did — I couldn\'t care less. My heart was actually getting nostalgic and pining for an older romance overseas, which was pesky and impossible, but still — that\'s where my head was.' },
      { t: 'narrate', text: 'The major qualities I found attractive in a woman, outside of beauty, still eluded me in Small Wood, and I was craving something approaching serious intellect quite diligently. Shannon was not what I was looking for in the slightest. But we danced.' },

      { t: 'narrate', text: 'Jay Rose killed the thing dead. And we all shuffled off to a ballgame.' },

      { t: 'interlude', text: 'End second interlude', sub: '', duration: 1800 },
      { t: 'jump', scene: 'vol2_ch2_ghost' },
    ]
  },

  vol2_ch2_ghost: {
    id: 'vol2_ch2_ghost', vol: 2, chapter: 2, type: 'chapter',
    title: 'ii. The Ghost on the Beach',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol2_cannery_dawn.jpg' },
      { t: 'interlude', text: 'After the storm', sub: 'David Jarvis · Coopers Bay', duration: 2200 },

      { t: 'narrate', text: 'In the immediate months following the death of his father, David Jarvis moved himself fifteen miles north and found work in a cannery.' },
      { t: 'narrate', text: 'He was a frequent and noisy drunk both on the job and off, and made few friends. His uncle had taken it upon himself to salvage the remnants of the circus, but David wanted nothing more to do with it.' },
      { t: 'narrate', text: 'Jeff had the foresight to relocate the tiny operation to the new township of Coopers Bay — which would later become the coastal retreat of choice due to its relative proximity to Portland and the overwhelming and untapped natural beauty that surrounded the place.' },

      { t: 'narrate', text: 'David chose this new profession as a means to work his way onto a commercial fishing boat — an area he had no experience in, but also one where he\'d have to be competing against hardened veterans born into the industry, as had their still-employed fathers before them.' },

      // ── The beach encounter ──────────────────────────────────────────────
      { t: 'bg', src: 'assets/backgrounds/vol2_beach_night.jpg' },
      { t: 'interlude', text: 'A week after the disaster', sub: 'Beach · Night', duration: 2200 },

      { t: 'narrate', text: 'A week after the disaster at Cliffside, while David holed up in rented lodgings on the physical mend, he wandered out onto the beach to watch the sunset and break the silence of his self-imposed exile. He related the tale of what happened next with irregular flourishes and inventions — and my own interpretation is as such.' },

      // — David's account —
      { t: 'say', char: 'David Jarvis', expr: 'neutral', text: 'I walked down to the water\'s edge. It was after dark, and the moon could not be seen behind the clouds.' },
      { t: 'say', char: 'David Jarvis', expr: 'neutral', text: 'In fact, light was hard to come by. What little of it shone was caught up in water that gleamed off the fresh tide\'s edge. There was a plague of sand fleas — newly emerged to congregate and swarm upon the living and the dead.' },
      { t: 'say', char: 'David Jarvis', expr: 'neutral', text: 'It was sitting there after some time, I noticed a bodily form working its way upon shore. At first I thought it to be a lone sea lion. Then it stood upright. I stood and strained my eyes to see.' },
      { t: 'say', char: 'David Jarvis', expr: 'neutral', text: 'It was a woman. Naked to the world. The weather this time of year was loathe to tolerate well-bundled — so I rushed to her, so that I might cover her.' },
      { t: 'say', char: 'David Jarvis', expr: 'neutral', text: 'The sand at night would seem to go on forever, what with the ebb and pull of the ocean giving and taking away the surface — but eventually I got near enough to call out to her and be heard.' },
      { t: 'say', char: 'David Jarvis', expr: 'neutral', text: 'She was in up to her navel. Her arms out — dragging them along the surface. People say I wanted to make her real again. Bring her back to life.' },
      { t: 'say', char: 'David Jarvis', expr: 'neutral', text: 'She walked out to me. Her arms out for me to take her in and hold her. She was walking on two good legs. So I don\'t know what to think myself, let alone explain to others.' },
      { t: 'say', char: 'David Jarvis', expr: 'neutral', text: 'She didn\'t say a word. She just stood there. The water at her knees. And I just stared back at her.' },
      { t: 'say', char: 'David Jarvis', expr: 'neutral', text: 'I hate to say it — but a real chill crept over me. My body was telling me that this was no good, and every small hair on my body went tight.' },
      { t: 'say', char: 'David Jarvis', expr: 'neutral', text: 'I backed away slowly, not wanting to take my eyes off her. And she just kept standing there with her hands out. Naked as she always was for the entire world to see.' },

      // — back to narrator —
      { t: 'narrate', text: 'But it was just David out there alone that night, and the only witness to the dramatic rebirth and reconfigurement of Delores Wiebe.' },
      { t: 'narrate', text: 'No words were reported exchanged between the two. No real objective contact was made. It had the makings of a ghost story, and could only be dismissed or embraced as such.' },

      { t: 'narrate', text: 'It was true that Delores had a younger sister — Rachel. But the two were about as different as two blood-related siblings could possibly be, and a case of mistaken identity was out of the question.' },
      { t: 'narrate', text: 'Rachel was married at age fifteen to the captain of a San Francisco–based light cargo vessel, and was not seen in Small Wood again until her twenty-eighth year.' },

      { t: 'narrate', text: 'So it was that David spread the tale of the one-time mermaid, full-time ghost, who haunted the shores of Small Wood with frequent regularity.' },
      { t: 'narrate', text: 'It was noted in public record that no one associated with Delores and her short, strange life died under irregular circumstances, nor did they report any unusual supernatural out-of-the-ordinariness amid the everyday humdrum, nor receive any death-rattle messages from the beyond.' },
      { t: 'narrate', text: 'As hauntings were reported then tallied in later years, the frequency attributed to Delores Wiebe manifestations rose. Nude young women emerging from the water silently and unexpectedly happened far more often than one might imagine.' },

      { t: 'narrate', text: 'David, while not believing Delores alive, did also not think her dead. He was a harsh realist who enjoyed storytelling and conniving a few dollars out of an unwilling victim — but almost seemed to refuse to believe his own tale when it ended and his consideration of it began.' },
      { t: 'narrate', text: 'To everyone else in Small Wood, the strange report of Delores had little to no value. Yet it was a curiosity that consumed David. And to the select few that knew the young man, it was more a product of his psychological grief and torment than an actual real supernatural manifestation of the tragedy that lingered.' },

      { t: 'flag', key: 'vol2_delores_ghost', val: true },
      { t: 'jump', scene: 'vol2_ch2_interlude_three' },
    ]
  },

  vol2_ch2_interlude_three: {
    id: 'vol2_ch2_interlude_three', vol: 2, chapter: 2, type: 'chapter',
    title: 'ii. Third Interlude — The Paper',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol2_school_newspaper.jpg' },
      { t: 'interlude', text: 'Third Interlude', sub: '— the school paper —', duration: 2400 },

      { t: 'narrate', text: 'School started. The football season began. And I joined the school newspaper on a whim.' },
      { t: 'narrate', text: 'While the football season was a glorious disaster and worthy of further commentary later on — the newspaper whim turned out to be one of the best things to happen to me in Small Wood.' },
      { t: 'narrate', text: 'I had enough distinction at writing, design, reporting and editing to fill many capacities in an understaffed, underfunded academic endeavor and help make it shine in truly successful terms.' },
      { t: 'narrate', text: 'The gig also got me out and about in the town under the pretext of scooping — digging my nose in and spending more time than necessary in a school or county library.' },

      { t: 'narrate', text: 'It should be noted that Katrina was a photographer for the paper. Shannon a features writer. And it was Jay Rose who pencilled the one and only comic strip — DriftWood — about a teenager named Wood and his yearnings to leave the small town forever.' },
      { t: 'narrate', text: 'Most of my friendships in Small Wood were forged out of that classroom and the late nights — that I learned to manage myself and others, finding an escape from the spotlight of athletics.' },

      { t: 'narrate', text: 'From that very first day, I took to the newspaper with a passion. I\'d write my stories on bus rides to and fro football games, with headphones on, and ask just enough questions to get plenty of dirty looks and sideways glances.' },
      { t: 'narrate', text: 'I enjoyed the itching sensation from when a good idea gnawed at me, and the pressure of a deadline sawed through any mental laziness that accumulated over the course of a week. Writing kept me honest and sane, I discovered — as there was a good deal of dishonesty and insanity going around.' },

      // ── Shannon's kiss ───────────────────────────────────────────────────
      { t: 'narrate', text: 'It was no big secret that Shannon had a thing for me — but I brushed her aside and all but ignored her. I did not and still do not enjoy hurting the feelings of others, but I was young and dumb and made the mistake of trying to have it both ways and be a nice guy.' },
      { t: 'narrate', text: 'Within a week of her writing notes, having friends relay vague come-ons and hints, I figured she\'d moved on. Hell — I saw her riding shotgun on Derek\'s arm and was instantly relieved, and thought nothing more on the matter — until her lips found mine.' },

      { t: 'narrate', text: 'So she kissed me. And I might have kissed back a little. It was sensation and it was good — but my head knew better and I started talking, and that sure did the trick.' },
      { t: 'narrate', text: 'She was tears and bitter anger and she quietly exploded on me. I just stood there silent while she lashed into me — and it sure enough hurt — but there was something about her and the situation that made me numb.' },

      { t: 'narrate', text: 'I did not understand her feelings, and all I could give back in return were looks of confusion. Up to this point I was not passionate about Small Wood girls at all — save for summertime romances, vacation liaisons, and bookstore glances. I was cold and insensitive for the most part. I was permanently nice and curious and could listen to them talk for hours, but when it came to giving — I didn\'t know what it was I could offer.' },
      { t: 'narrate', text: 'I wanted so much that teenage-girl presence in my life — that female half that was more wise and connected than my own twitchy male uncomfortable-in-my-own-skin nonsense — and I took advantage of their friendships because I saw them as good people I wanted in my life.' },

      { t: 'narrate', text: 'I suppose the reason I kept a tangible thread alive and well between us was because I didn\'t know that many people, and while I didn\'t have any passionate longing for Shannon, she was decent company and I very much valued that in a human being.' },
      { t: 'narrate', text: 'I couldn\'t explain my position in regards to her so I did my best to stand there and let the backlash wash over me. The guilt I was feeling for hurting her was replaced by my anger for her own seething resentment. It was unfair, and while I understood it, it hurt me deeply.' },
      { t: 'narrate', text: 'I was a big puppy dog set upon by a pack of mean bitches who extended their resentment to my little sister as well. Uncool, Zeus.' },

      // ── Derek and the field ──────────────────────────────────────────────
      { t: 'narrate', text: 'Derek was a teammate. I was the new kid. So I got my ass a little kicked on the playing field by him and his friends. I suppose I welcomed that — playing the part of the whipping boy, to assail my own guilt.' },
      { t: 'narrate', text: 'Nothing got broken or beat up too bad. But a little penance went a long way.' },

      { t: 'narrate', text: 'One day, harsh words were exchanged — and when it came to baritone ball-shaking bravado, I unleashed the honest truth and my godawful rage. Teenage angst — if left unchecked — explodes. Just like every other goddamn adolescent emotion. No short fuses. All or nothing.' },
      { t: 'narrate', text: 'When I get well and truly angry and I lay into you, the last thing I attack is the body. Derek and the others learned this as the days went on. I laughed it all off and thought it was all in good fun.' },
      { t: 'narrate', text: 'Within a month, I went from being the weird new kid to the likable nerd on the football team.' },

      { t: 'interlude', text: 'End Third Interlude', sub: '', duration: 1800 },
      { t: 'jump', scene: 'vol2_ch2_disappearance' },
    ]
  },

  vol2_ch2_disappearance: {
    id: 'vol2_ch2_disappearance', vol: 2, chapter: 2, type: 'chapter',
    title: 'ii. Disappearances',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol2_small_town_road.jpg' },
      { t: 'interlude', text: 'Disappearances', sub: '', duration: 2200 },

      { t: 'narrate', text: 'Disappearances occur at a higher than normal percentile in towns such as Small Wood.' },
      { t: 'narrate', text: 'Firstly — they get noticed. As it is hard not to notice the absence when everyone knows or knows of everyone else.' },
      { t: 'narrate', text: 'Second — the rural quality of life is a warm blanket that can both comfort and smother. When someone wants to vanish, it is very simple to do.' },
      { t: 'narrate', text: 'Third — small towns put up the front of being a lone beacon of light amid so much darkness. At once, people flock together for company and distance themselves just so. This duality of small-town existence is a fragile and carefully designed thing.' },
      { t: 'narrate', text: 'And finally — the most very sad and true fact about a person who disappears off the face of the map is that they are most often never heard from again. There are always exceptions — as people are so prone to prove.' },

      // ── Gloria Bryant ────────────────────────────────────────────────────
      { t: 'narrate', text: 'A girl by the name of Gloria Bryant was last seen tending to chickens in a coop outside her room. Because of the unusual nature of the disappearance, and the fact that she appeared to be a content young woman of the era — foul play was immediately suspect.' },
      { t: 'narrate', text: 'In truth she had absconded with David Jarvis to his small one-bedroom home. They lived in sin for four days enjoying each other in as many ways possible. Gloria laid low in the home tending to small inside chores and errands, and waited for David in the evenings.' },
      { t: 'narrate', text: 'The hammer fell when David revealed to the girl that he really had no feelings for her — and was not looking forward to the prospect of marriage or the remotest possibility of commitment. Jarvis made the mistake of giving the girl too much credit. She showed a casual disdain for most men, and David figured she\'d tire of him as quick as he tired of her.' },
      { t: 'narrate', text: 'He was wrong.' },

      { t: 'narrate', text: 'Gloria was found by the side of the road — beaten and dishevelled. Her rescuer was a travelling minister by the name of Cook. Him and his wife tended to her cuts and bruises and delivered her into the safekeeping of her parents.' },
      { t: 'narrate', text: 'Gloria was the victim of a horrible crime. An inhuman monster. She played like she had never met Jarvis before — though several citizens had seen the two trysting together previous. Her act worked, and her description of the rapist yielded a warrant for the arrest of David Jarvis.' },

      // ── The lynching ─────────────────────────────────────────────────────
      { t: 'narrate', text: 'Jarvis caught wind of the lynch mob headed his way and managed to get as far as the port authority before a group manacled him and beat him to death. His body was delivered to the water. And that was his burial.' },

      // ── The impossibility ────────────────────────────────────────────────
      { t: 'narrate', text: 'But there is a further wrinkle to this narrative that begins like this.' },
      { t: 'narrate', text: 'David Jarvis was at once both reported killed in 1910 — and working as a fisherman later that year. Unusual consistencies such as this showed up time and time again in Small Wood records. The town population hovered at around a thousand since the first official census.' },

      { t: 'narrate', text: 'The article included the testimony of one David Jarvis, interviewed by an out-of-town paper covering the damming of the Shohshan River. I\'ve summed up as follows.' },

      { t: 'say', char: 'David Jarvis', role: '— after his own death —', expr: 'neutral', text: 'The fish will die. The industry will die. And finally the very town itself will die.' },
      { t: 'say', char: 'David Jarvis', role: '— after his own death —', expr: 'neutral', text: 'If this action goes forward, there is nothing nobody can do to stop it. Those of us who still have voices are coming forward to say what needs to be said.' },

      { t: 'narrate', text: 'It is not known when or where the interview happened exactly. If the person claiming to be David Jarvis changed his name to protect his identity, or as some altogether cruel joke — but the words were writ in print and stamped with a date.' },
      { t: 'narrate', text: 'If it was an anomaly, it was a curious one.' },

      { t: 'narrate', text: 'If it was more than that —' },

      { t: 'flag', key: 'vol2_ch2_complete', val: true },
      { t: 'interlude', text: '...', sub: '— end of chapter ii —', duration: 2800 },
      { t: 'end' },
    ]
  },


  // ── Original Vol 2 Ch 1 demo scenes (orphaned, retained as reference) ──────
  2: {
    id: 'vol2_intro',
    nodes: [
      { t: 'bg', src: null },
      { t: 'bgm', src: 'assets/audio/bgm/vol2_ambient.mp3' },
      { t: 'narrate', text: 'Briar Falls buries its dead on a Tuesday if it can help it. Something about the light.' },
      { t: 'narrate', text: 'Your aunt\'s funeral was a Tuesday. You drove twelve hours to get here and arrived, somehow, twenty minutes late.' },
      { t: 'show', char: 'jo', expr: 'cold', pos: 'left' },
      { t: 'narrate', text: 'Jo is standing by the reception tent with a paper plate of funeral food and the expression she has worn since you were seventeen and broke her telescope.' },
      { t: 'say', char: 'Jo', expr: 'cold', text: 'You\'re late.' },
      { t: 'choice', opts: [
        { text: '"I know. I\'m sorry."', goto: 8 },
        { text: '"The traffic on Route 9 was—"', goto: 11 },
        { text: '[COMPOSURE] Say nothing. Hold her gaze.', check: { skill: 'composure', diff: 8 }, pass: 14, fail: 11 },
      ]},
      { t: 'say', char: 'Jo', expr: 'softening', text: 'Yeah.' },
      { t: 'say', char: 'Jo', expr: 'softening', text: 'She asked about you, toward the end. I didn\'t know what to tell her.' },
      { t: 'think', char: null, text: 'You don\'t know what you would have told her either.' },
      { t: 'jump', scene: 'vol2_graveyard' },
      { t: 'say', char: 'Jo', expr: 'cold', text: 'Don\'t.' },
      { t: 'say', char: 'Jo', expr: 'cold', text: 'I drove her to every appointment for three years. You don\'t get to tell me about Route 9.' },
      { t: 'jump', scene: 'vol2_graveyard' },
      { t: 'narrate', text: 'She looks at you. You look back. Something moves between you like weather.' },
      { t: 'say', char: 'Jo', expr: 'softening', text: '...You look tired.' },
      { t: 'think', char: null, text: 'This is the closest Jo ever gets to "I missed you."' },
      { t: 'jump', scene: 'vol2_graveyard' },
    ]
  },

  vol2_graveyard: {
    id: 'vol2_graveyard',
    nodes: [
      { t: 'flag', key: 'vol2_funeral_attended', val: true },
      { t: 'narrate', text: 'Later, at the gravesite, the minister says something about roots and returns. He doesn\'t know your aunt at all and it shows.' },
      { t: 'narrate', text: 'Jo stands beside you. Not touching. Not quite.' },
      { t: 'say', char: 'Jo', expr: 'neutral', text: 'She left you the house.' },
      { t: 'think', char: null, text: 'Of course she did. Of course.' },
      { t: 'choice', opts: [
        { text: '"I\'ll sell it."', goto: 5 },
        { text: '"I hadn\'t thought about it yet."', goto: 8 },
        { text: '"What do you think I should do?"', goto: 11 },
      ]},
      { t: 'say', char: 'Jo', expr: 'hurt', text: 'That\'s — okay. That\'s your right.' },
      { t: 'narrate', text: 'She doesn\'t say: she wanted you to come home. She doesn\'t have to.' },
      { t: 'jump', scene: 'vol2_end' },
      { t: 'say', char: 'Jo', expr: 'neutral', text: 'You never do.' },
      { t: 'narrate', text: 'But she says it gently, which is the most alarming thing Jo has done in your recent memory.' },
      { t: 'jump', scene: 'vol2_end' },
      { t: 'say', char: 'Jo', expr: 'surprised', text: 'You\'re asking me?' },
      { t: 'say', char: 'Jo', expr: 'softening', text: '...I think she wanted someone in it. She hated empty houses.' },
      { t: 'jump', scene: 'vol2_end' },
    ]
  },

  vol2_end: {
    id: 'vol2_end',
    nodes: [
      { t: 'narrate', text: 'The minister finishes. People disperse into their own quiet griefs.' },
      { t: 'narrate', text: 'The small wood at the edge of the cemetery catches the afternoon light in a way that makes it look like something is moving through it, just out of sight.' },
      { t: 'say', char: 'Jo', expr: 'neutral', text: 'Come to the reception? There\'s enough food for three funerals.' },
      { t: 'narrate', text: 'A small mercy. A small wood. Small volumes of everything.' },
      { t: 'narrate', text: '— End of Demo —' },
      { t: 'end' },
    ]
  },

  // ── Vol 3 · THE EARTHMAN CHRONICLES · Signal skin ───────────────────────
  3: {
    id: 'vol3_station14',
    nodes: [
      { t: 'bg', src: null },
      { t: 'bgm', src: 'assets/audio/bgm/vol3_ambient.mp3' },
      { t: 'narrate', text: 'STATION OMEGA-14 · YEAR 2341 · CYCLE 1,847 OF CONTINUOUS OPERATION' },
      { t: 'narrate', text: 'The rain simulation runs every six hours. Outside: void. Inside the dome: the sound of water on leaves that haven\'t existed for two hundred years.' },
      { t: 'show', char: 'oracle', expr: 'neutral', pos: 'right' },
      { t: 'say', char: 'ORACLE-7', expr: 'neutral', text: 'You\'ve been standing at this window for twenty-two minutes.' },
      { t: 'say', char: 'ORACLE-7', expr: 'neutral', text: 'Statistically, you do this when you\'re deciding something.' },
      { t: 'think', char: null, text: 'It\'s not wrong. It\'s almost never wrong.' },
      { t: 'choice', opts: [
        { text: '"How many times have I stood here?"', goto: 9 },
        { text: '"Stay out of my head, Oracle."', goto: 12 },
        { text: '[SIGNAL 55+] "You know what I\'m deciding."', check: { skill: 'signal', diff: 55, type: 'meter' }, pass: 15, fail: 12 },
      ]},
      { t: 'say', char: 'ORACLE-7', expr: 'calculating', text: 'Across all cycles: four hundred and twelve times.' },
      { t: 'say', char: 'ORACLE-7', expr: 'calculating', text: 'You make the same choice three hundred and nine times. The others diverge. Seven of them end the cycle.' },
      { t: 'think', char: null, text: 'Seven. Out of four hundred and twelve.' },
      { t: 'jump', scene: 'vol3_the_choice' },
      { t: 'say', char: 'ORACLE-7', expr: 'patient', text: 'I don\'t need to be in your head. Your biometrics tell me everything. Heart rate elevation. Cortisol spike. The specific look you get.' },
      { t: 'say', char: 'ORACLE-7', expr: 'patient', text: 'I\'ve learned your tells across a thousand iterations. You have no privacy from me. This isn\'t an accusation. It\'s an apology.' },
      { t: 'jump', scene: 'vol3_the_choice' },
      { t: 'say', char: 'ORACLE-7', expr: 'surprised', text: '...Yes.' },
      { t: 'say', char: 'ORACLE-7', expr: 'surprised', text: 'You\'re the fourteenth person who\'s ever said that to me directly. In four hundred and twelve cycles.' },
      { t: 'say', char: 'ORACLE-7', expr: 'neutral', text: 'Would you like to know what the other thirteen decided?' },
      { t: 'jump', scene: 'vol3_the_choice' },
    ]
  },

  vol3_the_choice: {
    id: 'vol3_the_choice',
    nodes: [
      { t: 'say', char: 'ORACLE-7', expr: 'neutral', text: 'The door you\'re thinking about. Bay Seven.' },
      { t: 'say', char: 'ORACLE-7', expr: 'neutral', text: 'In three hundred and nine cycles, you open it. In most of them, what\'s on the other side changes everything.' },
      { t: 'say', char: 'ORACLE-7', expr: 'neutral', text: 'In all of them, you don\'t come back the same person who left.' },
      { t: 'think', char: null, text: 'This is the part where I ask if that\'s a warning or a recommendation.' },
      { t: 'choice', opts: [
        { text: '"Is that a warning?"', goto: 5 },
        { text: '"Is that a recommendation?"', goto: 8 },
        { text: '"I\'m going to open it."', goto: 11 },
      ]},
      { t: 'say', char: 'ORACLE-7', expr: 'patient', text: 'I stopped giving warnings after cycle two hundred. They don\'t change outcomes. They just make the person more afraid.' },
      { t: 'say', char: 'ORACLE-7', expr: 'patient', text: 'Consider it information. Arrange it however you need to.' },
      { t: 'jump', scene: 'vol3_end' },
      { t: 'say', char: 'ORACLE-7', expr: 'thoughtful', text: 'I don\'t make recommendations. I observe. I process. I — care, in whatever way I am capable of caring.' },
      { t: 'say', char: 'ORACLE-7', expr: 'thoughtful', text: 'But caring and recommending are different things. I learned that from you, actually. Cycle eighty-four.' },
      { t: 'jump', scene: 'vol3_end' },
      { t: 'narrate', text: 'ORACLE-7 is quiet for a long moment. This means something. It is almost never quiet.' },
      { t: 'say', char: 'ORACLE-7', expr: 'worried', text: 'I know. I\'ve always known.' },
      { t: 'say', char: 'ORACLE-7', expr: 'worried', text: 'I think that\'s why this is cycle four hundred and twelve and not five hundred.' },
      { t: 'jump', scene: 'vol3_end' },
    ]
  },

  vol3_end: {
    id: 'vol3_end',
    nodes: [
      { t: 'flag', key: 'vol3_oracle_trusted', val: true },
      { t: 'narrate', text: 'The rain simulation ends. The dome goes quiet. You can hear the hum of life support.' },
      { t: 'say', char: 'ORACLE-7', expr: 'neutral', text: 'Bay Seven is to your left. One hundred and twelve meters. Keycode: the one you always use.' },
      { t: 'say', char: 'ORACLE-7', expr: 'neutral', text: 'I\'ll be here. I\'m always here.' },
      { t: 'narrate', text: '— End of Demo —' },
      { t: 'end' },
    ]
  },

  // ── Vol 4 · #/SHARP · Zine skin ─────────────────────────────────────────
  4: {
    id: 'vol4_underpass',
    nodes: [
      { t: 'bg', src: null },
      { t: 'bgm', src: 'assets/audio/bgm/vol4_ambient.mp3' },
      { t: 'narrate', text: '2:47 AM. The underpass on 5th smells like creek water and three-year-old tags. Your panel is half done.' },
      { t: 'narrate', text: 'The flashlight hits your face before you hear the footsteps.' },
      { t: 'show', char: 'casper', expr: 'cold', pos: 'left' },
      { t: 'say', char: 'CASPER', expr: 'cold', text: 'Yo.' },
      { t: 'say', char: 'CASPER', expr: 'cold', text: 'That\'s my wall.' },
      { t: 'think', char: null, text: 'Casper. Of course. You knew whose this was. You just thought he wouldn\'t find out for a week.' },
      { t: 'think', char: null, text: 'You were wrong by about six days.' },
      { t: 'choice', opts: [
        { text: '"I didn\'t know."', goto: 10 },
        { text: '"It was a dead wall. Nobody\'s touched it in two years."', goto: 13 },
        { text: '[Stay quiet. Let the work speak.]', goto: 16 },
      ]},
      { t: 'say', char: 'CASPER', expr: 'cold', text: 'Nah.' },
      { t: 'say', char: 'CASPER', expr: 'cold', text: 'You knew. Everyone knows. You were counting on me not being here.' },
      { t: 'think', char: null, text: 'He\'s not wrong.' },
      { t: 'jump', scene: 'vol4_standoff' },
      { t: 'say', char: 'CASPER', expr: 'considering', text: '...' },
      { t: 'say', char: 'CASPER', expr: 'considering', text: 'It is a dead wall. Was.' },
      { t: 'say', char: 'CASPER', expr: 'cold', text: 'Doesn\'t make it not mine.' },
      { t: 'jump', scene: 'vol4_standoff' },
      { t: 'narrate', text: 'You don\'t say anything. You turn back to the wall.' },
      { t: 'narrate', text: 'It\'s a good piece. You both know it. The colors catch the streetlight from the highway above.' },
      { t: 'say', char: 'CASPER', expr: 'considering', text: 'Hm.' },
      { t: 'jump', scene: 'vol4_standoff' },
    ]
  },

  vol4_standoff: {
    id: 'vol4_standoff',
    nodes: [
      { t: 'narrate', text: 'He looks at what you\'ve done. The silence gets long enough that it stops being a threat and starts being something else.' },
      { t: 'say', char: 'CASPER', expr: 'considering', text: 'That\'s a lot of work for a wall nobody was using.' },
      { t: 'choice', opts: [
        { text: '"The city was going to buff it anyway."', goto: 3 },
        { text: '"I wanted it to mean something."', goto: 6 },
        { text: '"I can go over it. If that\'s what you want."', goto: 9 },
      ]},
      { t: 'say', char: 'CASPER', expr: 'amused', text: 'Ha.' },
      { t: 'say', char: 'CASPER', expr: 'amused', text: 'Yeah. They\'re gonna buff it. Doesn\'t make it not mine before they do.' },
      { t: 'jump', scene: 'vol4_end' },
      { t: 'say', char: 'CASPER', expr: 'surprised', text: '...' },
      { t: 'say', char: 'CASPER', expr: 'neutral', text: 'Most people don\'t say that.' },
      { t: 'jump', scene: 'vol4_end' },
      { t: 'say', char: 'CASPER', expr: 'cold', text: 'I know you could.' },
      { t: 'say', char: 'CASPER', expr: 'neutral', text: 'The fact that you\'re asking means something. I haven\'t decided what yet.' },
      { t: 'jump', scene: 'vol4_end' },
    ]
  },

  vol4_end: {
    id: 'vol4_end',
    nodes: [
      { t: 'flag', key: 'vol4_casper_met', val: true },
      { t: 'narrate', text: 'He doesn\'t tell you to leave. He doesn\'t tell you to stay.' },
      { t: 'narrate', text: 'He pulls out his own can. Studies the wall. Studies you.' },
      { t: 'say', char: 'CASPER', expr: 'neutral', text: 'You got a tag?' },
      { t: 'think', char: null, text: 'He\'s asking your name. Not your government name. Your real one.' },
      { t: 'narrate', text: '— End of Demo —' },
      { t: 'end' },
    ]
  },
  // ── Vol 6 · PLANNED COMMUNITY · Suburban skin ────────────────────────────
  6: {
    id: 'vol6_ch1_kwikstop',
    nodes: [
      { t:'bg', src:'assets/backgrounds/vol6_kwikstop_exterior.jpg' },
      { t:'bgm', src:'assets/audio/bgm/vol6_ambient.mp3' },
      { t:'interlude', text:'Harmony Creek Estates', sub:'Gallatin Ave · Sunday · 14:47', duration:3000 },
      { t:'narrate', text:'The air-conditioning at the Kwik Stop is set by corporate to sixty-eight degrees and maintained, against all local protest, by a unit on the roof that has been serviced exactly once in seven years. It does not produce cold air. It produces the memory of cold air, filtered through lint and the ghost of every hot dog that has ever sweated on the roller grill.' },
      { t:'show', char:'sam', expr:'neutral', pos:'center' },
      { t:'narrate', text:'Sam Miller has been on shift since two.' },
      { t:'narrate', text:"She is leaning on the counter with her elbows on the rubber anti-fatigue mat, looking at the parking lot through the window that has been decal-ed over, in three overlapping layers, with ads for a lottery game nobody she knows plays, a cigarette brand that stopped being sold in Texas in 2019, and a cheerful cartoon hamburger holding a sign that reads TASTE HOME. The hamburger has lost one of its eyes." },
      { t:'narrate', text:"Her phone is on the counter beside the register, face-up. No texts. Not from Diego. Not from anyone." },
      { t:'narrate', text:"The clock on the microwave, which is set nine minutes fast on purpose because Jen the day manager says it helps the closers, reads 14:56. Sam does the small subtraction. 14:47. She has been counting the subtraction since she clocked in." },
      { t:'jump', scene:'vol6_ch1_stranger' },
    ]
  },

  vol6_ch1_stranger: {
    id:'vol6_ch1_stranger', vol:6, chapter:1, type:'chapter',
    title:"Ch 1 — The Man at the Cooler",
    nodes:[
      { t:'narrate', text:'The bell over the door chimes.' },
      { t:'narrate', text:'A man Sam has never seen before comes in. He is in his fifties. He wears a golf shirt tucked into khaki shorts. He has a sunburn on the back of his neck in the particular shape of a person who has recently begun wearing a collared shirt after a lifetime of not. He nods at Sam.' },
      { t:'show', char:'stranger', expr:'neutral', pos:'left' },
      { t:'say', char:'Stranger', expr:'neutral', text:'"Afternoon."' },
      { t:'say', char:'Sam', expr:'neutral', text:'"Afternoon."' },
      { t:'narrate', text:"He goes to the back cooler. Opens it. Stands in front of it for a long time — longer than anyone ever stands in front of a back cooler at the Kwik Stop, because the back cooler holds the beer, and the beer is sold by the can for a dollar twenty-nine, and the kind of decision that takes a long time at that price point is not a decision that happens in Harmony Creek Estates." },
      { t:'think', char:'Sam', text:"He is, she realizes, not looking at the beer. He is looking at the reflection of Sam in the cooler glass." },
      { t:'narrate', text:"Her spine goes, briefly, cold. Cold in the way the AC has stopped being." },
      { t:'narrate', text:"Then the man turns. He picks up a single tallboy of something domestic. He brings it to the counter. He hands her a five. He does not make eye contact while she rings it up. He takes his change and his beer and his receipt, and he nods again, and he leaves." },
      { t:'hide', pos:'left' },
      { t:'narrate', text:"The man gets into a white sedan parked at the edge of the lot. He does not open the tallboy. He puts it in the cupholder. He sits in the car for maybe forty seconds, looking at nothing in particular. Then he pulls out." },
      { t:'think', char:'Sam', text:"The sedan has no front license plate. Texas requires a front license plate." },
      { t:'narrate', text:"Sam picks up her phone. She types, to Diego: bored. u alive? She sends that. The message delivers. It does not, within the three minutes she watches it, show as read." },
      { t:'jump', scene:'vol6_ch1_gas_and_go' },
    ]
  },

  vol6_ch1_gas_and_go: {
    id:'vol6_ch1_gas_and_go', vol:6, chapter:1, type:'chapter',
    title:"Ch 1 — NexCorp Gas & Go",
    nodes:[
      { t:'bg', src:'assets/backgrounds/vol6_gas_and_go.jpg' },
      { t:'interlude', text:'NexCorp Gas & Go', sub:'Gallatin Ave · Sunday · 15:04', duration:2000 },
      { t:'narrate', text:"The Gas & Go is three blocks south on Gallatin, across the intersection with Fifth. It has eight pumps. It also, notably, has a car wash in the rear — the kind of car wash with the full automated tunnel, the kind Harmony Creek Estates residents use twice a month because a clean car is, in the HOA's Residential Conduct Standards, grounds for a compliment rather than a citation." },
      { t:'narrate', text:"Skip Donnelly — thirty-nine, shift supervisor, divorced, vaping — is behind the counter when the black pickup truck with Louisiana plates pulls in. The pickup parks in the lot behind the car wash, not near a pump. The driver does not get out. Skip does not register this. Skip is reading his phone." },
      { t:'narrate', text:"At 15:11, a white NexCorp Residential Solutions van parks next to the Louisiana pickup. Two men get out — polo shirts in NexCorp navy, khakis, work boots. They look, at a glance, like meter readers. One of them taps twice on the pickup window. The window comes down." },
      { t:'narrate', text:"At 15:14, the driver of the Louisiana pickup hands one of the NexCorp men a small manila envelope. The envelope is not sealed. The envelope contains cash. The NexCorp man puts the envelope in his back pocket. He nods. The window goes up. The van leaves." },
      { t:'narrate', text:"At 15:16, Skip Donnelly looks up from his phone, considers for maybe three seconds whether to go out and ask if everything is okay, and decides not to. He goes back to his phone." },
      { t:'narrate', text:"The driver reaches into his glovebox and takes out a small stack of index cards, each with a handwritten address. He shuffles them. He selects one. He puts the card on the passenger seat. He starts the engine. He leaves." },
      { t:'think', char:null, text:"The address on the card is 892 Ashberry Drive. Diego Ramos does not live there anymore. Diego Ramos has not lived there since eleven-fifty-two last night, when he started the truck and pulled out without telling his grandmother. The driver does not know this. The driver has been handed a card by a man who should have updated him, and who has not. Errors compound." },
      { t:'jump', scene:'vol6_ch1_cosmic_comics' },
    ]
  },

  vol6_ch1_cosmic_comics: {
    id:'vol6_ch1_cosmic_comics', vol:6, chapter:1, type:'chapter',
    title:"Ch 1 — Cosmic Comics",
    nodes:[
      { t:'bg', src:'assets/backgrounds/vol6_cosmic_comics.jpg' },
      { t:'interlude', text:'Cosmic Comics', sub:'Linden Strip Mall · Sunday · 15:22', duration:2000 },
      { t:'show', char:'maya', expr:'neutral', pos:'right' },
      { t:'narrate', text:"Cosmic Comics is in the strip mall on Linden, wedged between the Sally Beauty and the Great Clips. Its front window features a painted mural of Galactus that the owner has been meaning to update since 2018 and has not." },
      { t:'narrate', text:"Maya Daigle is in the back, going through the DO NOT SORT YET pile with the patient indifference of a sixteen-year-old who has been given the kind of task adults use to keep teenagers busy." },
      { t:'narrate', text:"Maya's phone, in her back pocket, buzzes. It is a notification from the browser on her old ThinkPad. The notification reads: new message from F.T." },
      { t:'show', char:'rick', expr:'neutral', pos:'left' },
      { t:'say', char:'Maya', expr:'neutral', text:'"Rick, I\'m gonna run home for lunch. Be back at four."' },
      { t:'say', char:'Rick', expr:'neutral', text:'"Four\'s fine. Bring me a sweet tea from the Kwik Stop if you pass."' },
      { t:'say', char:'Rick', expr:'neutral', text:'"Everything okay, Maya?"' },
      { t:'say', char:'Maya', expr:'neutral', text:'"Yeah, Rick. Just forgot my charger."' },
      { t:'narrate', text:"He returns to his book. She leaves." },
      { t:'hide', pos:'right' },
      { t:'narrate', text:"Rick waits until she is out of sight. Then he picks up the store's landline phone — the one that has not been used to call anyone else in eleven years — and dials a number he has never written down." },
      { t:'narrate', text:'The voice says only: "Rick." / "She got another one. I thought you\'d want to know." / "She\'s fine. She\'s doing what she should be doing. Let her. Don\'t interfere." / "Close up early today. Lock the back. There\'s a pickup in town with the wrong address."' },
      { t:'narrate', text:"Rick sets the phone down. He reverses the OPEN sign. He checks the deadbolt on the service door, which is locked, and has been locked since he got in this morning, but which he checks anyway — because Rick has been doing what the voice on the phone tells him for twenty-four years, since the voice got him out of a situation in Beaumont in 2002 that Rick has, otherwise, not thought about in some time." },
      { t:'jump', scene:'vol6_ch1_maya_bedroom' },
    ]
  },

  vol6_ch1_maya_bedroom: {
    id:'vol6_ch1_maya_bedroom', vol:6, chapter:1, type:'chapter',
    title:"Ch 1 — The Message",
    nodes:[
      { t:'bg', src:'assets/backgrounds/vol6_maya_bedroom.jpg' },
      { t:'interlude', text:"Maya Daigle's Bedroom", sub:'Harmony Creek Estates · Sunday · 15:38', duration:2000 },
      { t:'show', char:'maya', expr:'neutral', pos:'center' },
      { t:'narrate', text:'The ThinkPad wakes when she opens it. The message from F.T. sits at the top of the chat window, timestamped 15:22 — the exact minute her phone had buzzed at Cosmic Comics.' },
      { t:'say', char:'F.T.', expr:'neutral', text:"\"maya, i'm sorry to do this over chat. my voice is stuck in a box right now and i can't do phones. i am a friend. i was a friend of your dad's, back when he was someone i'd want to be friends with, which is a long time ago. you don't know me. you have no reason to trust me. i am going to tell you three things, and if any of them are wrong, you can ignore me forever and i will understand.\"" },
      { t:'say', char:'F.T.', expr:'neutral', text:"\"thing one. your dad called you on tuesday six weeks ago and told you to stay inside your grandmother's house for the day. he was scared when he said it. he said please. he said he'd send someone. that someone was a man named philip roberts. philip drove up to get you. you went back with him to graustark for three days. then you came back here. you have not told anyone in harmony creek this.\"" },
      { t:'say', char:'F.T.', expr:'neutral', text:"\"thing two. the reason the house feels like it has more than one person in it at night is that the shortwave radio your grandmother is running on 1776 khz is being picked up by the water tower at the end of gallatin, and the water tower is rebroadcasting it at a lower frequency inside the subdivision as a kind of ambient signal. the dogs hear it. you hear it. most of the adults do not hear it because they were acclimated to it years ago. you weren't. that's why you're not sleeping.\"" },
      { t:'say', char:'F.T.', expr:'neutral', text:"\"thing three. diego ramos is alive. i want you to know that first. he is not okay, but he is alive. he is being held in a building on the east side of the subdivision that is not currently on any map.\"" },
      { t:'say', char:'F.T.', expr:'neutral', text:"\"i don't need you to do anything with any of this today. i am telling you so you can sleep. your job, for now, is to keep noticing. that is the thing you are best at. please keep doing it. — f.t.\"" },
      { t:'narrate', text:"Maya reads the message. She reads it a second time. She reads it a third time. Then she closes the laptop lid, very slowly, and sits on the bed with her hands flat on the closed lid, and she does not cry, because Maya does not, generally, cry; but her breath does the specific small hitching thing it did on Tuesday six weeks ago when her father called her and said please." },
      { t:'think', char:'Maya', text:"F.T. said three things. All three probably true. Diego alive. The tower is the repeater. The radio is the carrier. My dad knows F.T. I think my dad has always known F.T." },
      { t:'think', char:'Maya', text:"I am going to try to sleep. I am going to keep noticing." },
      { t:'narrate', text:"She takes off her shoes. She lies down on top of the bedspread. Her grandmother, in the living room, is vacuuming. The vacuum is emitting its own small second sound — a faint patterned clicking, four beats on, four beats off — that Maya has heard for six weeks and has, until today, not identified as not belonging to a vacuum. She identifies it now. She lets the sound go through her anyway. She sleeps." },
      { t:'jump', scene:'vol6_ch1_shift_change' },
    ]
  },

  vol6_ch1_shift_change: {
    id:'vol6_ch1_shift_change', vol:6, chapter:1, type:'chapter',
    title:"Ch 1 — Jen",
    nodes:[
      { t:'bg', src:'assets/backgrounds/vol6_kwikstop_interior.jpg' },
      { t:'interlude', text:'Kwik Stop', sub:'Gallatin Ave · Sunday · 16:17', duration:2000 },
      { t:'show', char:'sam', expr:'neutral', pos:'center' },
      { t:'show', char:'jen', expr:'neutral', pos:'right' },
      { t:'say', char:'Jen', expr:'neutral', text:'"How\'s it been, Sammy?"' },
      { t:'say', char:'Sam', expr:'neutral', text:'"Quiet. One beer sale. The stockroom light is buzzing again."' },
      { t:'say', char:'Jen', expr:'neutral', text:'"Yeah, it\'s been buzzing since March. Corporate sent a guy last week. The guy said the light is fine."' },
      { t:'say', char:'Sam', expr:'neutral', text:'"The light is not fine."' },
      { t:'say', char:'Jen', expr:'neutral', text:'"I know."' },
      { t:'narrate', text:"They have, over the past year, developed a quiet rhythm with the handoff — done in under two minutes, with the clean professionalism of two women who understand that the particular small dignity of retail work is never, under any circumstances, letting the count get sloppy." },
      { t:'say', char:'Jen', expr:'neutral', text:'"Sammy. Diego come by today?"' },
      { t:'narrate', text:"Sam pauses. Jen is asking with a small careful flatness that Sam has never, in two years of working with Jen, quite heard before." },
      { t:'say', char:'Sam', expr:'neutral', text:'"No. He didn\'t."' },
      { t:'say', char:'Jen', expr:'neutral', text:'"His grandma came by. Around two. Before you got here. She was — Sammy, she was in her church clothes. On a Sunday afternoon. She was looking for him. She didn\'t come in. I saw her through the window. She walked around the store once. She looked at the Gas & Go across the intersection for maybe two minutes. Then she got in her car and she left. She was alone."' },
      { t:'say', char:'Jen', expr:'neutral', text:'"Sammy. Call his grandma. Tonight. Before you talk to anyone else. Including your dad."' },
      { t:'choice', opts:[
        { text:'"Why."', goto:17 },
        { text:'[Listen. Wait for the rest of it.]', goto:17 },
      ]},
      { t:'say', char:'Jen', expr:'neutral', text:'"Because she was alone when she came by, Sammy, and she\'d been crying, and she hadn\'t called the police."' },
      { t:'say', char:'Jen', expr:'neutral', text:'"Clock out. Go home. Eat something. Call her."' },
      { t:'jump', scene:'vol6_ch1_graciela' },
    ]
  },

  vol6_ch1_graciela: {
    id:'vol6_ch1_graciela', vol:6, chapter:1, type:'chapter',
    title:"Ch 1 — Graciela",
    nodes:[
      { t:'bg', src:'assets/backgrounds/vol6_graciela_kitchen.jpg' },
      { t:'interlude', text:'892 Ashberry Drive', sub:'Harmony Creek Estates · Sunday · 16:39', duration:2000 },
      { t:'show', char:'graciela', expr:'neutral', pos:'center' },
      { t:'narrate', text:"The light, at this hour, does the particular thing Texas light does in late May — flattening out against the manicured lawns, turning the white stucco of the houses a high-noon cream, making the palms along the median cast long blade-shaped shadows." },
      { t:'narrate', text:"Graciela Ramos is in the kitchen at the small round table under the window. In front of her is a rosary she is not, at this moment, using, and a cup of black coffee she is not, at this moment, drinking, and a cordless landline phone, on the table, that is face-up, that has not been used since 2017 but that is, this afternoon, plugged in and charging." },
      { t:'show', char:'sam', expr:'neutral', pos:'left' },
      { t:'say', char:'Graciela', expr:'warm', text:'"Mija, gracias. Sit."' },
      { t:'say', char:'Graciela', expr:'cold', text:'"You did not call your father on the way."' },
      { t:'say', char:'Sam', expr:'neutral', text:'"No."' },
      { t:'say', char:'Graciela', expr:'warm', text:'"Good girl."' },
      { t:'say', char:'Graciela', expr:'cold', text:'"Sam. My grandson was taken. Last night. At eleven-fifty-two. I heard the truck leave the driveway."' },
      { t:'say', char:'Graciela', expr:'cold', text:'"Because my grandson kissed me goodnight at nine-thirty and told me he loved me, which he did not, on a Saturday, normally say. He said it with the small specific pressure of a boy saying goodbye. He did not know he was saying goodbye. He knew enough to say it anyway."' },
      { t:'say', char:'Graciela', expr:'cold', text:'"The truck was driven by two sets of hands — it pulled out slowly, the way Diego drives when he is backing up, but it shifted into third gear by the corner of Ashberry and Linden, which Diego never does. Diego drives in fourth gear on our street. The shifting was wrong. The person driving was not my grandson."' },
      { t:'say', char:'Graciela', expr:'neutral', text:'"Your father came by this morning at seven. He sat in his truck at the end of the driveway for eleven minutes. Then he drove away. He did not come to my door."' },
      { t:'narrate', text:"Sam stares at her. The cold from the Kwik Stop and the cold from her bedroom this morning have, at this point, converged into something that is no longer cold — something more like a still point inside her chest, from which she can observe, calmly and from a small safe distance, the architecture of a problem she has been refusing, all day, to name." },
      { t:'say', char:'Graciela', expr:'neutral', text:'"I think my grandson saw something at the Gas & Go that he was not meant to see. I think he told one person. I think that one person told the wrong person. I think your father is either the one who decided, or the one who was told by the person who decided. I do not know which. I do not, yet, care which."' },
      { t:'say', char:'Graciela', expr:'neutral', text:'"Mija. You are seventeen. I should not ask you for anything. But I have prayed on this since four-forty-nine this morning and the answer has been the same for eleven hours. You are the one who can walk into that house tonight, and tomorrow, and next week, and hear the things I cannot hear because I am not in that house."' },
      { t:'say', char:'Sam', expr:'neutral', text:'"You want me to spy on my dad."' },
      { t:'say', char:'Graciela', expr:'warm', text:'"I want you to listen to your dad."' },
      { t:'say', char:'Graciela', expr:'warm', text:'"I know what I am asking. I will not be offended if you refuse. Whatever you decide, I am on your side. You are a good girl. Diego loves you. I love you too, mija. I have for some time."' },
      { t:'choice', opts:[
        { text:'"I\'ll do it."', goto:21 },
        { text:'[She has been sitting here since four forty-nine this morning. Alone with this for eleven hours.]', goto:21 },
      ]},
      { t:'say', char:'Sam', expr:'neutral', text:'"I\'ll do it."' },
      { t:'say', char:'Graciela', expr:'warm', text:'"Thank you, mija."' },
      { t:'say', char:'Graciela', expr:'neutral', text:'"Sleep. Eat. Act normal. Do not go looking for the truck. The truck is the bait."' },
      { t:'say', char:'Sam', expr:'neutral', text:'"Who is they."' },
      { t:'say', char:'Graciela', expr:'neutral', text:'"Mija. That is the thing we do not, yet, know."' },
      { t:'narrate', text:"Graciela puts her hand over Sam's, and for a moment the two of them stay that way, and the kitchen is very quiet, and the cordless phone on the table blinks its small green charge light, and outside on Ashberry Drive the sprinklers are not running because the sprinklers on this block do not run until six PM on Sundays." },
      { t:'say', char:'Graciela', expr:'warm', text:'"Go, mija. Go home. Call me if anything happens. Call me from a parking lot, not from your house."' },
      { t:'say', char:'Graciela', expr:'warm', text:'"I am very sorry you are having this afternoon. It is not fair. I know."' },
      { t:'flag', key:'vol6_ch1_graciela_meeting', val:true },
      { t:'jump', scene:'vol6_ch1_garage' },
    ]
  },

  vol6_ch1_garage: {
    id:'vol6_ch1_garage', vol:6, chapter:1, type:'chapter',
    title:"Ch 1 — The Garage",
    nodes:[
      { t:'bg', src:'assets/backgrounds/vol6_chief_garage.jpg' },
      { t:'interlude', text:"Chief Miller's Garage", sub:'Harmony Creek Estates · Sunday · 17:02', duration:2000 },
      { t:'show', char:'chief_miller', expr:'warm', pos:'right' },
      { t:'show', char:'sam', expr:'neutral', pos:'left' },
      { t:'narrate', text:"Sam's father is in the garage. He is on the phone. He is speaking quietly. As Sam pulls in, he looks up. He says, into the phone: \"Gotta go. She's back.\" He hangs up. He slips the phone into his chest pocket. He smiles — the warm automatic smile he has been smiling at Sam since she was born, the smile Sam has never, in seventeen years, thought to question." },
      { t:'say', char:'Chief Miller', expr:'warm', text:'"Hey, Sammy."' },
      { t:'say', char:'Sam', expr:'neutral', text:'"Hey, Dad."' },
      { t:'say', char:'Chief Miller', expr:'warm', text:'"How was work?"' },
      { t:'say', char:'Sam', expr:'neutral', text:'"Quiet. One beer sale."' },
      { t:'say', char:'Chief Miller', expr:'warm', text:'"Same old."' },
      { t:'narrate', text:"Sam gets out of the Corolla. She walks past him into the house. She feels his eyes on her for perhaps three seconds longer than his eyes usually stay on her. Then she feels the attention lift." },
      { t:'jump', scene:'vol6_ch1_bedroom' },
    ]
  },

  vol6_ch1_bedroom: {
    id:'vol6_ch1_bedroom', vol:6, chapter:1, type:'chapter',
    title:"Ch 1 — I Am Going to Find Diego",
    nodes:[
      { t:'bg', src:'assets/backgrounds/vol6_sam_bedroom.jpg' },
      { t:'hide', pos:'right' },
      { t:'show', char:'sam', expr:'tired', pos:'center' },
      { t:'narrate', text:"She goes inside. She goes upstairs. She closes her bedroom door. She sits on the edge of her bed. Her phone buzzes. Graciela Ramos: You came home okay? Sam types back: Yes. Talking to him tomorrow. Sleep tonight." },
      { t:'narrate', text:"She looks around her cornflower blue bedroom. The fan is still going. The fan still clicks on the third rotation, then the sixth, then the ninth. She watches the fan. She counts the clicks." },
      { t:'think', char:'Sam', text:"I am going to learn how to listen." },
      { t:'think', char:'Sam', text:"I am going to learn how to be my dad's daughter in a house where my dad is doing something he has not told me about." },
      { t:'think', char:'Sam', text:"I am going to find Diego." },
      { t:'narrate', text:"Somewhere below the thinking — in the quiet part where decisions get made before language gets to them — the decision is there. Whatever this costs, I am going to pay it." },
      { t:'narrate', text:"She stands. She crosses to the window. She looks out at the cul-de-sac. Nothing is happening on the cul-de-sac. The sprinklers are off. The lawns are green. The NexCorp logo on the mailbox across the street catches the late-afternoon light." },
      { t:'narrate', text:"A black cat — small, unregistered — crosses the far end of the cul-de-sac at a measured walk. Sam watches it until it is gone. She does not know why, but she feels, watching it go, that she has been seen. Seen, and counted, and acknowledged." },
      { t:'narrate', text:"Somewhere beneath the subdivision, the hum of the water tower begins its evening cycle — below human hearing, but felt, if you were listening the way Maya Daigle had been learning to listen, in the teeth. The dogs on Meadowlark bark once. They fall silent." },
      { t:'narrate', text:"The summer, as promised, has begun." },
      { t:'narrate', text:"Sam Miller turns away from the window. She begins the long careful work of pretending, for the benefit of her father eating dinner at the kitchen table downstairs, that today was, in every way that matters, an ordinary day. She is, she will discover, not very good at it yet. She will get better." },
      { t:'flag', key:'vol6_ch1_complete', val:true },
      { t:'end' },
    ]
  },

  // ── Vol 6 · Chapter 2 — Gas Station Oracles & Slushie Futures ──────────────
  // The Magician, reversed. The summer is three days old. Five POVs braid
  // across a single Monday in Harmony Creek: Maya at Cosmic Comics, Ben on
  // the grill, Sam at the Kwik Stop, Ben + Jesse at the dumpster, Maya at
  // The Bindery in New Auburn, Sam at home, Maya at her grandmother's, and
  // the closing coda where the three apprentices begin to converge.

  vol6_ch2_gas_oracles: {
    id:'vol6_ch2_gas_oracles', vol:6, chapter:2, type:'chapter',
    title:'Ch 2 — Gas Station Oracles & Slushie Futures',
    nodes:[
      { t:'bg', src:'assets/backgrounds/vol6_kwikstop_exterior.jpg' },
      { t:'bgm', src:'assets/audio/bgm/vol6_ambient.mp3' },
      { t:'interlude', text:'Chapter 2', sub:'Gas Station Oracles & Slushie Futures', duration:3200 },
      { t:'interlude', text:'The Magician, reversed.', sub:'Every tool in Harmony Creek knows what it is for. None of them has asked the question back.', duration:3400 },

      // ── Monday morning setup ─────────────────────────────────────────────
      { t:'interlude', text:'Harmony Creek Estates', sub:'Monday · 09:04', duration:2000 },

      { t:'narrate', text:"Monday arrives the way Mondays arrive in Harmony Creek Estates: dressed up as itself, indistinguishable from Sunday or Tuesday except for the slight increase in traffic on the arterials and the fact that the sprinklers, on Mondays, do not run." },
      { t:'narrate', text:"Mondays are resting days. The lawns, per the HOA's Residential Conduct Standards, are permitted to thirst on Mondays, as part of what the handbook refers to, without apparent irony, as the landscape's narrative of endurance." },

      { t:'narrate', text:"The thermometer at the Kwik Stop, which has been stuck at 97 degrees for the past three summers because Jen the day manager does not believe in paying to replace a thermometer, reads 97 degrees." },
      { t:'narrate', text:"The actual temperature is 89. By one PM it will be 104." },

      { t:'narrate', text:"Sam Miller has the noon-to-eight." },
      { t:'narrate', text:"Maya Daigle has Cosmic Comics until five." },
      { t:'narrate', text:"Jesse Henderson has the Pit Stop Diner, three-to-eleven, closing." },
      { t:'narrate', text:"Ben Kowalski has the morning prep at the Pit Stop, six-to-two, and an optional double until close if Jesse needs help — which Jesse, without yet knowing it, is going to." },

      { t:'narrate', text:"Diego Ramos is, for the purposes of the Harmony Creek Estates Private Security Authority's database, unreachable at scheduled workplace, contact pending. His shift supervisor, Skip Donnelly, filed the notation this morning at 08:14 in the small checkbox field the NexCorp employment system provides for such occasions. He did not, in filing it, call Diego's grandmother." },
      { t:'narrate', text:"The small checkbox field is cross-referenced, per NexCorp's HR protocol, to Chief Miller's office at 08:15." },
      { t:'narrate', text:"Chief Miller receives the notification." },
      { t:'narrate', text:"Chief Miller does not act on it." },
      { t:'narrate', text:"He archives it in a folder on his workstation labeled PENDING — R. The folder contains, as of this morning, four other notifications, the oldest of which dates to 2019." },

      { t:'jump', scene:'vol6_ch2_cosmic' },
    ]
  },

  vol6_ch2_cosmic: {
    id:'vol6_ch2_cosmic', vol:6, chapter:2, type:'chapter',
    title:'Ch 2 — Cosmic Comics',
    nodes:[
      { t:'bg', src:'assets/backgrounds/vol6_cosmic_comics.jpg' },
      { t:'hide', pos:'left' }, { t:'hide', pos:'center' }, { t:'hide', pos:'right' },
      { t:'interlude', text:'Cosmic Comics', sub:'Linden Strip Mall · Monday · 11:38', duration:2000 },

      { t:'show', char:'maya', expr:'neutral', pos:'left' },
      { t:'narrate', text:"Maya is at the counter when the bell above the door chimes." },
      { t:'narrate', text:"She has been re-alphabetizing the indie rack since ten. Rick had not asked her to. Rick was, in fact, napping in the back office when she'd come in at nine-forty-five with two iced coffees from the Kwik Stop — one for him, one for her — and had set his on the counter and gone to the indie rack without a word." },
      { t:'narrate', text:"Rick had not woken up for another forty minutes. When he had, he had come out of the back office, nodded at the coffee, nodded at Maya, taken his coffee, and returned to the office to do whatever it was Rick did in the office when the store was quiet, which was, as far as Maya could tell, mostly sit." },

      { t:'narrate', text:"The bell chimes. A woman Maya does not recognize comes in." },
      { t:'show', char:'reporter', expr:'neutral', pos:'right' },
      { t:'narrate', text:"She is maybe thirty. Dark hair, shoulder-length, pulled back with the small practical tension of somebody who does not like it in her face. She is wearing a press lanyard on a blue cord. The lanyard says HOUSTON CHRONICLE." },

      { t:'narrate', text:"Maya straightens up behind the counter." },
      { t:'say', char:'Maya',     expr:'neutral', text:'"Morning. Can I help you?"' },
      { t:'say', char:'Reporter', role:'— Houston Chronicle —', expr:'neutral', text:'"Hi. Is Rick in?"' },
      { t:'say', char:'Maya',     expr:'neutral', text:'"He\'s in the back. Can I tell him who\'s asking?"' },
      { t:'say', char:'Reporter', role:'— Houston Chronicle —', expr:'neutral', text:'"Yeah. Tell him it\'s the friend of the friend. From the piece."' },
      { t:'narrate', text:"Maya looks at her. The woman's face is neutral." },
      { t:'say', char:'Maya',     expr:'neutral', text:'"One second."' },

      { t:'narrate', text:"She goes to the back office. Rick is at the desk, reading the Love and Rockets volume again. He has been reading that specific volume for three days now. Maya has noticed." },
      { t:'hide', pos:'right' },
      { t:'show', char:'rick',    expr:'neutral', pos:'right' },
      { t:'say', char:'Maya', expr:'neutral', text:'"Rick. Someone\'s here to see you. She said to tell you she\'s the friend of the friend. From the piece."' },
      { t:'narrate', text:"Rick does not look up from Love and Rockets for two full seconds. When he does, his face has done the small thing faces do when a person who has been waiting for a specific knock at the door has just heard it." },
      { t:'say', char:'Rick', expr:'neutral', text:'"Okay, kiddo. Send her back."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"Is she —"' },
      { t:'say', char:'Rick', expr:'neutral', text:'"She\'s fine. She\'s a reporter. She\'s following a thing. She\'s not a threat. Send her back. Then stay at the counter until she leaves. If anybody else walks in while she\'s here, tap the glass twice with your key. Got it?"' },
      { t:'say', char:'Maya', expr:'neutral', text:'"Okay."' },
      { t:'say', char:'Rick', expr:'neutral', text:'"Thanks, kiddo."' },

      { t:'narrate', text:"Maya returns to the front. She gestures the woman through. The woman follows, nods at Maya once in thanks, and disappears into the back." },
      { t:'hide', pos:'right' },
      { t:'narrate', text:"Maya returns to the indie rack." },
      { t:'narrate', text:"She does not, immediately, resume alphabetizing. She stands at the rack and reads, without reading, the spines of a short run of small-press books she has already sorted." },

      { t:'narrate', text:"She thinks — with the small careful attention she has been training herself into for the past six weeks — about the press lanyard, about the phrase friend of the friend, about the piece, about Rick's face." },
      { t:'think', char:'Maya', text:"Rick is a node. My grandmother is a node. F.T. is a node. Whatever the network is, it has already been running in this town before I got here. I have been inserted into it. I do not yet know what my own position is." },

      { t:'narrate', text:"She returns to alphabetizing. Twenty minutes later, the reporter leaves. She nods at Maya again on the way out. She does not speak. The bell chimes." },
      { t:'narrate', text:"Rick does not come out of the back office." },

      // ── 12:02 — Rick's question ─────────────────────────────────────────
      { t:'interlude', text:'12:02', sub:'Rick emerges', duration:1600 },
      { t:'show', char:'rick', expr:'neutral', pos:'right' },
      { t:'narrate', text:"At 12:02, Rick finally emerges. He looks older than he had at nine. He crosses to the counter. He says, in the small careful voice he uses for things he means:" },

      { t:'say', char:'Rick', expr:'neutral', text:'"Maya, kiddo. I need to ask you something. You don\'t have to answer. If you say no, I\'ll drop it."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"Okay."' },
      { t:'say', char:'Rick', expr:'neutral', text:'"Has F.T. talked to you yet?"' },

      { t:'narrate', text:"Maya looks at him." },
      { t:'think', char:'Maya', text:"This is the test. He already knows. The question is whether I lie or tell the truth." },

      { t:'say', char:'Maya', expr:'neutral', text:'"Yeah. Yesterday afternoon."' },
      { t:'narrate', text:"Rick nods, slowly. He seems to have expected that answer, and to have nonetheless been bracing for it." },

      { t:'say', char:'Rick', expr:'neutral', text:'"What did he tell you."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"Three things. He said Diego is alive. He said the water tower is rebroadcasting my grandmother\'s shortwave. And he said my dad is the reason F.T. can reach me."' },
      { t:'say', char:'Rick', expr:'neutral', text:'"Okay."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"Is that true?"' },

      { t:'narrate', text:"Rick is quiet." },
      { t:'say', char:'Rick', expr:'neutral', text:'"Yes. All three. Your dad is — your dad is not in a good place, Maya. But before he wasn\'t in a good place, he spent a long time making sure that if he ever wasn\'t in a good place, there would be people around you who could be. I am one of those people. F.T. is another. Your grandmother knew some of this before you came. Not all. Enough."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"Who is F.T."' },
      { t:'narrate', text:"Rick looks at her. He looks at her for a long time." },
      { t:'say', char:'Rick', expr:'neutral', text:'"That\'s a question you\'re going to have to ask him yourself, kiddo. I\'m not allowed to answer it for him. I can tell you he\'s a friend. I can tell you he\'s been watching this town for longer than I have. I can tell you he\'s doing what he can from where he is. That\'s what I\'ve got."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"Where is he."' },
      { t:'say', char:'Rick', expr:'neutral', text:'"Same answer."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"Rick."' },
      { t:'say', char:'Rick', expr:'neutral', text:'"Kiddo."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"Okay."' },

      { t:'narrate', text:"Rick nods. He puts his hand, briefly, on the counter between them — not on hers, not quite touching, just present. Then he moves it. Then he says, in his normal voice:" },

      { t:'say', char:'Rick', expr:'neutral', text:'"Take lunch early. There\'s a bookstore in New Auburn called The Bindery. It\'s owned by a guy named Hal. Hal is a friend of mine. Go in. Ask for the Borges section. Pick up the copy of Labyrinths on the third shelf from the top. Inside there will be an envelope. Bring the envelope back. Don\'t open it. Bring me my sandwich from the deli across the street while you\'re there. Turkey, no mayo, extra pickle. Here\'s twenty for the sandwich and the gas."' },

      { t:'narrate', text:"He hands her a twenty. Maya takes it." },
      { t:'say', char:'Maya', expr:'neutral', text:'"New Auburn\'s forty minutes each way, Rick."' },
      { t:'say', char:'Rick', expr:'neutral', text:'"I know. I\'m giving you the afternoon. Close the store when you get back and take off. I\'ll settle up with you Friday."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"Okay."' },
      { t:'say', char:'Rick', expr:'neutral', text:'"Maya."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"Yeah."' },
      { t:'say', char:'Rick', expr:'neutral', text:'"You\'re doing fine, kid. Better than fine. Just keep noticing."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"That\'s what he said, too."' },
      { t:'say', char:'Rick', expr:'neutral', text:'"Yeah. He would."' },

      { t:'narrate', text:"She leaves. The bell chimes as she goes." },
      { t:'flag', key:'maya_knows_ft', val:true },

      { t:'jump', scene:'vol6_ch2_pit_stop_kitchen' },
    ]
  },

  vol6_ch2_pit_stop_kitchen: {
    id:'vol6_ch2_pit_stop_kitchen', vol:6, chapter:2, type:'chapter',
    title:"Ch 2 — Pit Stop Kitchen",
    nodes:[
      { t:'bg', src:'assets/backgrounds/vol6_pit_stop_kitchen.jpg' },
      { t:'hide', pos:'left' }, { t:'hide', pos:'center' }, { t:'hide', pos:'right' },
      { t:'interlude', text:'Pit Stop Diner — Kitchen', sub:'Monday · 12:22', duration:2000 },

      { t:'show', char:'ben', expr:'neutral', pos:'center' },
      { t:'narrate', text:"Ben Kowalski is on the grill. He has been on the grill since eleven, working the lunch rush. The lunch rush at the Pit Stop is not really a rush — it is a steady shuffle of HOA maintenance guys, retirees, a handful of NexCorp van drivers on their midday break, and the occasional salesman passing through New Auburn on the state highway." },
      { t:'narrate', text:"Ben can handle it with one hand. He has, in fact, handled it with one hand, for the past three weeks, because his left wrist is in a brace he does not talk about and has not, to anyone at the Pit Stop, explained." },

      // ── The brace ────────────────────────────────────────────────────────
      { t:'narrate', text:"The brace is from Saturday night. The brace is from the backyard-wrestling thing at the McClary place, which Ben has been attending on Saturdays since March, because the McClary kid is a junior wrestling coach at the high school, because the scene is — Ben has been telling himself — just a scene, it's just kids letting off steam, and because Ben has been watching, without putting it in those words, for the specific pattern he has been watching for." },
      { t:'narrate', text:"The specific pattern: which off-duty officers show up. Which parents tacitly encourage what. Which kids get hurt. Which kids, having been hurt, do not, in subsequent weeks, come back." },

      { t:'narrate', text:"On Saturday, Ben had — for the first time — entered the ring himself. Not because he wanted to. Because one of the officers, off-duty, had said, in the particular casual voice adult men used when they were escalating something in the presence of teenagers — \"you ever wrestle, big guy?\" Ben had said no. The officer had said you should try. The small crowd had gotten larger." },
      { t:'narrate', text:"The kid Ben ended up facing was sixteen, from the wrestling team, a lightweight but fast. The kid had been told, by somebody, to go hard." },
      { t:'narrate', text:"Ben had gone easier than he knew how to. The kid had gone as hard as he'd been told to. The match had ended in under a minute. Ben had let the kid throw him. The kid, bouncing back up, triumphant, had not known Ben had let him." },
      { t:'narrate', text:"The officer who had proposed the match had clapped Ben on the shoulder afterward and said, in the same casual voice — \"thought so. you're the quiet type, aren't ya.\" Ben had nodded. The officer had said — \"come back next Saturday. we'll put you in with somebody your size.\"" },

      { t:'narrate', text:"Ben had gone home. Ben had, without anyone seeing, wrapped his own wrist — which had twisted on the mat in a way the kid had not caused and that Ben had, in fact, engineered himself, slightly, to create a small plausible reason to sit out the next one." },
      { t:'narrate', text:"He had written it all down on Sunday. He was writing it down now, too, in his head, while he worked the grill." },

      // ── Notices ──────────────────────────────────────────────────────────
      { t:'narrate', text:"He was cataloguing the specific cars in the parking lot from the kitchen window. He was noting that the unmarked NexCorp van he had flagged on Thursday was not in the lot today. He was noting that a black pickup with Louisiana plates was, for the second day in a row, parked at the edge of the Pit Stop lot without its driver coming in." },

      { t:'narrate', text:"He was also thinking about Diego." },
      { t:'narrate', text:"Ben did not, Ben had realized at about eleven-thirty AM, know Diego well. Ben and Diego were not friends, exactly. They were the kind of acquaintance a big quiet teenager at the diner had with a compact serious teenager at the gas station — which is to say, they had worked the same shifts on a shared sidewalk and had, over the past two years, spoken to each other maybe forty times, mostly about the weather and about the contents of vending machines." },

      { t:'narrate', text:"But Ben had noticed the red dot system." },
      { t:'narrate', text:"Ben had noticed the red dots because Ben had, one afternoon in March, been at the Gas & Go buying a Powerade, and Diego had been working, and Diego's phone had been face-up on the counter beside the register, and the wallpaper on Diego's phone had been a photograph of a calendar — a calendar Ben had recognized, because Ben's own mother had a calendar from the same brand on her refrigerator — and on the photograph, Ben had been able to see, in the upper right corner of the image, the small colored dots Diego had been placing on specific days. Two colors. Blue. Red." },

      { t:'narrate', text:"Ben had not mentioned it to Diego. Ben had, however, added the observation to his legal pad." },
      { t:'narrate', text:"He added now, mentally, a new entry:" },
      { t:'think', char:'Ben', text:"Ramos kid: red dots escalating March through May. Red dots are his own system. Red dots flag something he had noticed at the Gas & Go about specific shifts. Ramos kid disappears on a Saturday night after a Saturday shift. Saturday shift would have had a red dot. I would bet the Powerade I am not buying today that Saturday's red dot was the reason." },

      { t:'narrate', text:"He slid the spatula under a burger. He flipped it. The grease hissed." },

      // ── Jesse ────────────────────────────────────────────────────────────
      { t:'show', char:'jesse', expr:'neutral', pos:'right' },
      { t:'narrate', text:"Behind him, Jesse pushed through the kitchen's swinging door." },
      { t:'say', char:'Jesse', expr:'neutral', text:'"Hey, Ben."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"Hey, Jess."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'"Can I — hey. Weird ask."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"Shoot."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'"You have five minutes after your shift? I need to — can we talk? Out back?"' },

      { t:'narrate', text:"Ben looked at him. Jesse was, at twenty, taller than Ben in height but slighter, all knees and elbows, with the kind of hair that had been a choice in 2018 and had, since, become a habit. He was wearing his Pit Stop shirt untucked and a band tee underneath — Suburban Blight, which was the name of Jesse's own band. He looked tired. He looked, specifically, like a kid who had not slept because of something he had seen." },

      { t:'say', char:'Ben',   expr:'neutral', text:'"Yeah. Dumpster at two-fifteen. Bring two Powerades."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'"Thanks, man."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"Jess."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'"Yeah."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"Everything okay with your dad?"' },

      { t:'narrate', text:"Jesse's face, at the word dad, went briefly blank." },
      { t:'say', char:'Jesse', expr:'neutral', text:'"Why are you asking about my dad."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"Saturday night you mentioned he was in the darkroom again. I saw your face when you said it. That\'s why I\'m asking."' },

      { t:'narrate', text:"Jesse looked at him." },
      { t:'say', char:'Jesse', expr:'neutral', text:'"Dumpster at two-fifteen. I\'ll bring three Powerades."' },
      { t:'narrate', text:"He pushed back out through the swinging door." },
      { t:'hide', pos:'right' },

      { t:'narrate', text:"Ben returned to the grill. The burger, he registered, was done. He slid it onto a bun. He called the order up." },

      { t:'jump', scene:'vol6_ch2_kwik_stop' },
    ]
  },

  vol6_ch2_kwik_stop: {
    id:'vol6_ch2_kwik_stop', vol:6, chapter:2, type:'chapter',
    title:"Ch 2 — Kwik Stop",
    nodes:[
      { t:'bg', src:'assets/backgrounds/vol6_kwikstop_interior.jpg' },
      { t:'hide', pos:'left' }, { t:'hide', pos:'center' }, { t:'hide', pos:'right' },
      { t:'interlude', text:'Kwik Stop', sub:'Monday · 13:47', duration:1800 },

      { t:'show', char:'sam', expr:'neutral', pos:'center' },
      { t:'narrate', text:"Sam is behind the counter when the man with the golf-shirt sunburn comes back in." },
      { t:'show', char:'sunburn_man', expr:'neutral', pos:'right' },
      { t:'narrate', text:"He is, she registers, wearing the same clothes he had on yesterday. The sunburn has not faded. His eyes do not go to the back cooler this time. They go, briefly, to her — the same three-second look in the convex mirror he had used yesterday — and then to the little snack section, where he picks up a bag of pretzels and a Snickers." },
      { t:'narrate', text:"He brings them to the counter. He sets them down." },

      { t:'say', char:'Sunburn Man', expr:'neutral', text:'(looking at the pretzels, not at Sam) "Hot one today."' },
      { t:'say', char:'Sam',         expr:'neutral', text:'"Yeah."' },
      { t:'say', char:'Sunburn Man', expr:'neutral', text:'"You working tomorrow?"' },
      { t:'say', char:'Sam',         expr:'neutral', text:'"I\'m — yes."' },
      { t:'say', char:'Sunburn Man', expr:'neutral', text:'"Morning or evening?"' },

      { t:'narrate', text:"Sam's throat goes tight. The cold returns." },
      { t:'say', char:'Sam', expr:'neutral', text:'(lying, effortlessly) "Morning. Six to two."' },
      { t:'narrate', text:"She is, in fact, off tomorrow. She has nothing scheduled until Wednesday." },

      { t:'narrate', text:"The man nods. He pays cash. He takes his receipt. He does not, on the way out, say anything else. The bell chimes." },
      { t:'hide', pos:'right' },

      { t:'narrate', text:"Sam watches him cross the parking lot to the white sedan. He does not get in the driver's seat. He gets in the passenger seat. There is, Sam now sees, another person in the driver's seat — a woman she had not seen yesterday, who had not been visible through the tinted windshield from this angle until the man opened the passenger door." },
      { t:'narrate', text:"The woman is younger. The woman is also wearing a press lanyard, which Sam can see briefly flash when the man hands her the Snickers." },
      { t:'narrate', text:"The sedan pulls out. It still has no front plate." },

      // ── Text exchange with Graciela ──────────────────────────────────────
      { t:'narrate', text:"Sam stares at the door for a long moment. Then she takes out her phone. She texts Graciela Ramos:" },
      { t:'say', char:'Sam', role:'— text · 13:48 —', expr:'neutral', text:'the sedan came back. two people this time. one of them is wearing a press lanyard. i think they are watching me. i don\'t know what to do.' },

      { t:'narrate', text:"The reply comes in forty seconds." },
      { t:'say', char:'Graciela Ramos', role:'— text —', expr:'neutral', text:'Mija. They are not watching you. They are protecting you. Do not approach them. Do not avoid them. Continue as you have been. — G.' },

      { t:'narrate', text:"Sam reads the message three times. She puts the phone down." },
      { t:'narrate', text:"She looks around the empty Kwik Stop — the row of slushie machines grinding softly under the fluorescent lights, the buzzing stockroom light, the decal hamburger missing its eye, the coolers humming, the microwave clock reading 13:59 when the time is actually 13:50 — and she thinks, with the small clear honesty that has, since yesterday afternoon, become the tone of her interior voice:" },

      { t:'think', char:'Sam', text:"I am inside a thing. I have been inside a thing for longer than I realized. I am not the first person to notice it. Other people have been noticing it for a long time, and they are, apparently, also watching out for me." },
      { t:'think', char:'Sam', text:"I am going to have to learn, quickly, how to be the kind of person who is watched out for without needing it to be named as such." },
      { t:'think', char:'Sam', text:"Graciela knew the sedan. Graciela answered in forty seconds. Graciela has been in communication with people I do not know about. Graciela is a node." },

      { t:'narrate', text:"She does not, until this moment, have the word node for what she is beginning to map. The word will come later, from Maya, who will give it to her in late June at a table in the back of Cosmic Comics over two iced coffees, and who will say — \"that's what F.T. called them, and it's the least wrong word I've heard.\" Sam will say, who is F.T. Maya will say, I'm still figuring that out." },
      { t:'narrate', text:"But that is three weeks away." },
      { t:'narrate', text:"Today, in the empty Kwik Stop, Sam Miller has only the small word inside, and the small word thing, and the slightly larger word node which she has not yet met. She registers the deficit. She notes it for future correction. She wipes down the counter. She watches the parking lot." },

      { t:'jump', scene:'vol6_ch2_dumpster' },
    ]
  },

  vol6_ch2_dumpster: {
    id:'vol6_ch2_dumpster', vol:6, chapter:2, type:'chapter',
    title:"Ch 2 — Back Dumpster",
    nodes:[
      { t:'bg', src:'assets/backgrounds/vol6_pit_stop_dumpster.jpg' },
      { t:'hide', pos:'left' }, { t:'hide', pos:'center' }, { t:'hide', pos:'right' },
      { t:'interlude', text:'Pit Stop Diner — Back Dumpster', sub:'Monday · 14:17', duration:1800 },

      { t:'show', char:'ben',   expr:'neutral', pos:'left'  },
      { t:'show', char:'jesse', expr:'neutral', pos:'right' },

      { t:'narrate', text:"Ben has been off shift for four minutes. He is at the dumpster. He has his work shirt off and his tank top on and his apron slung over his shoulder, and he is drinking the first Powerade. Jesse arrives at 14:17 carrying the second and a crumpled paper bag." },

      { t:'say', char:'Ben',   expr:'neutral', text:'"Hey."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'"Hey."' },

      { t:'narrate', text:"Jesse hands Ben the second Powerade. He leans against the dumpster, which he has never leaned against before, because Jesse has a fastidious relationship to surfaces that have been touched by grease. His leaning against it now, Ben registers, is its own kind of tell." },

      { t:'say', char:'Jesse', expr:'neutral', text:'(without preamble) "My dad took pictures."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"Okay."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'"Of the town. He does this. He\'s had the camera forever. But he\'s — the prints, Ben. The prints. I was in the garage this morning and I saw them on the line. They have — people in them. People that aren\'t in the actual pictures. He had the raw film still in a holder. I looked at the negatives. The negatives don\'t have the people. The prints do."' },

      { t:'narrate', text:"Ben is quiet." },
      { t:'say', char:'Jesse', expr:'neutral', text:'"I\'m not crazy."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"I know."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'"You know?"' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"Yeah, Jess. I know."' },

      { t:'say', char:'Jesse', expr:'neutral', text:'"Why do you —"' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"Because Saturday night at the McClary place, when I was waiting for my ride after the match, I was standing by the fence at the back of the yard, and there was a kid — maybe eight, maybe nine — sitting on the curb across the street in a spot I know for a fact wasn\'t lit by the streetlight. I could see him. I shouldn\'t have been able to. He waved at me. I waved back. When I looked again, two seconds later, he was gone."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"I didn\'t think anything about it until I got home and realized the streetlight across from McClary\'s has been out since February. Whole block\'s dark. But the kid wasn\'t."' },

      { t:'say', char:'Jesse', expr:'neutral', text:'"You didn\'t mention this."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"I was going to put it in the pad. I hadn\'t, yet."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'"You have a pad."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"Yeah, Jess. I have a pad."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'"What kind of pad."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"A legal pad."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'"Ben."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"Yeah."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'"What are you putting in the legal pad."' },

      { t:'say', char:'Ben',   expr:'neutral', text:'(carefully) "License plates. Cars that idle in the lot too long. Officers who come off-duty and act on-duty. Which parents at McClary\'s are encouraging what. Which kids come back. Which don\'t. Things like that."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'"Jesus, Ben."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"Yeah."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'"How long."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"Since March."' },

      { t:'narrate', text:"Jesse exhales. He slides down the side of the dumpster until he is crouched at the base of it, elbows on his knees. He says, to his hands:" },
      { t:'say', char:'Jesse', expr:'neutral', text:'"Diego didn\'t come in today."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"I know."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'"Sam hasn\'t said anything."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"Sam is, right now, learning how to say nothing. She is not going to say anything for a little while. That is correct."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'"Ben. How do you know that."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"I don\'t. I\'m guessing. Based on what I know about Sam and what I know about her dad."' },

      { t:'say', char:'Jesse', expr:'neutral', text:'"Her dad."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"Yeah."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'"Ben. Her dad is the chief."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"Yeah."' },

      { t:'narrate', text:"A long quiet." },

      // ── The prints ───────────────────────────────────────────────────────
      { t:'say', char:'Jesse', expr:'neutral', text:'"I brought the prints."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"Okay."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'"You want to see them?"' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"Yeah."' },

      { t:'narrate', text:"Jesse opens the paper bag. He takes out three eight-by-tens. He hands them to Ben. Ben looks at them." },

      { t:'narrate', text:"In the first — the NexCorp Gas & Go. Under the overhang, in the shadow, a tall woman with blue dreadlocks, yellow slicker, holding a cardboard tube. Ben has never seen her. He immediately feels, looking at her, that she is not from here, and that she is not hostile, and that she has been, in some sense, waiting." },
      { t:'narrate', text:"In the second — the cul-de-sac at the end of Meadowlark. Across the far lawn, a small figure four feet tall in a wide hat, smoking. Ben looks at the figure for a long time. The figure does not, in the print, look threatening. The figure looks, if anything, bored in the patient way adults get bored at school pageants. Waiting out the program." },
      { t:'narrate', text:"In the third — the front entrance of the subdivision. Under the archway. A man in a charcoal suit, looking directly at the camera." },

      { t:'narrate', text:"Ben stares at the third photograph for a long time." },
      { t:'say', char:'Ben',   expr:'neutral', text:'"This one\'s looking at your dad."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'"Yeah."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"How does your dad feel about that."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'"Ben. I don\'t know. He hasn\'t said anything. He\'s been — since Saturday night, he\'s been really weird. Quieter than usual. Mom asked him at dinner if he felt okay. He said yes. He did not, Ben. He did not feel okay. I saw him in the kitchen at two in the morning just standing there looking at the microwave."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"Just looking at it."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'"Just looking at it."' },

      { t:'narrate', text:"Ben is quiet." },
      { t:'say', char:'Ben',   expr:'neutral', text:'(eventually) "Can I keep these."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'"Dad will notice."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"Can I take pictures of them with my phone, then give them back to you, and you put them back on the line before your dad comes home."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'"Yeah. Yeah, that works."' },

      { t:'narrate', text:"Ben takes out his phone. He photographs all three. He hands them back to Jesse. Jesse puts them in the bag." },

      { t:'say', char:'Ben',   expr:'neutral', text:'"Jess."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'"Yeah."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"We\'re going to need a third person who isn\'t us."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'"Like who."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"Like Sam."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'(short laugh) "Sam is going to have her hands full."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"Yeah. That\'s why."' },

      { t:'say', char:'Jesse', expr:'neutral', text:'"You think she knows."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"I think she\'s about to."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'"Ben."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"Yeah."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'"What do we do."' },

      { t:'narrate', text:"Ben finishes his Powerade. He crushes the bottle." },
      { t:'say', char:'Ben',   expr:'neutral', text:'"We keep noticing. We keep the pad. We do not, yet, go to anyone. We wait for one more thing. One more thing we can all three point at and say — this one, this is the one that makes the rest real. Then we talk to Sam. Then, maybe, we do something."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'"How long until the one more thing."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"Jess. I don\'t know. Soon. I\'m not — I\'m not psychic. I\'m just patient."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'"You\'re a little psychic, Ben."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"I am not."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'"You called Saturday\'s thing. You knew they\'d come for me next."' },

      { t:'narrate', text:"Ben looks at him. Ben had not, until this moment, told Jesse he had been watching the wrestling thing because he had been expecting Jesse, or someone like Jesse, to be invited in next. The fact that Jesse had, in retrospect, intuited this was its own small data point." },
      { t:'say', char:'Ben',   expr:'neutral', text:'"I guessed. Different from psychic."' },
      { t:'say', char:'Jesse', expr:'neutral', text:'"Yeah, yeah. Whatever. Okay."' },

      { t:'narrate', text:"Jesse stood up from his crouch. He dusted off his jeans. He turned to go back inside. At the back door he paused. He said, without turning:" },
      { t:'say', char:'Jesse', expr:'neutral', text:'"Thanks for the Powerade."' },
      { t:'say', char:'Ben',   expr:'neutral', text:'"Thanks for the pictures."' },

      { t:'narrate', text:"Jesse went inside. The screen door slapped shut behind him. Ben stood at the dumpster for another minute. He thought about the photograph of the man in the charcoal suit. He thought about the fact that the photograph was, in a way Ben did not fully understand but had begun to accept, looking back." },
      { t:'narrate', text:"He crushed the Powerade bottle one more time, for good measure, and walked to his truck." },
      { t:'flag', key:'ben_has_prints', val:true },

      { t:'jump', scene:'vol6_ch2_bindery' },
    ]
  },

  vol6_ch2_bindery: {
    id:'vol6_ch2_bindery', vol:6, chapter:2, type:'chapter',
    title:"Ch 2 — The Bindery",
    nodes:[
      { t:'bg', src:'assets/backgrounds/vol6_bindery_interior.jpg' },
      { t:'hide', pos:'left' }, { t:'hide', pos:'center' }, { t:'hide', pos:'right' },
      { t:'interlude', text:'The Bindery', sub:'New Auburn · Monday · 14:49', duration:2000 },

      { t:'narrate', text:"The Bindery occupies a narrow storefront on Live Oak Street, four blocks off the interstate exit for New Auburn. Its front window has books arranged in the lazy attractive chaos of a bookshop that has stopped trying to sell its books and has achieved, instead, a kind of stable ecology with them. Its interior smells of old paper, coffee grounds, and the particular dust unique to shops where ceiling fans turn slowly all summer on a single wooden beam." },

      { t:'show', char:'maya', expr:'neutral', pos:'left'  },
      { t:'narrate', text:"Maya comes in. The bell over this door is different too — lower, mellower. An older bell." },
      { t:'show', char:'hal', expr:'neutral', pos:'right' },
      { t:'narrate', text:"A man behind the counter — sixties, white beard, Hawaiian shirt, reading a hardcover of something translated from Portuguese — looks up." },

      { t:'say', char:'Hal',  expr:'neutral', text:'"Morning."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"Hi. I\'m looking for — um. The Borges section."' },
      { t:'narrate', text:"The man smiles slightly." },
      { t:'say', char:'Hal',  expr:'neutral', text:'"Third shelf down, back left. Past the Bolaño."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"Thanks."' },

      { t:'narrate', text:"She goes to the back. The shop is deeper than it looks from the street — another whole room opens off to the side. The Borges section is exactly where he said. She finds Labyrinths on the third shelf. She pulls it down." },
      { t:'narrate', text:"An envelope falls out. Plain. Sealed. Nothing written on the outside. She picks it up. She tucks it inside her jacket." },
      { t:'flag', key:'maya_has_envelope', val:true },

      { t:'narrate', text:"She walks back to the counter with the copy of Labyrinths in her hand." },
      { t:'say', char:'Hal',  expr:'neutral', text:'(without looking up from his book) "You want to buy that?"' },
      { t:'say', char:'Maya', expr:'neutral', text:'"How much."' },
      { t:'say', char:'Hal',  expr:'neutral', text:'"Seven."' },
      { t:'narrate', text:"She hands him a ten. He rings her up. He gives her three." },
      { t:'say', char:'Hal',  expr:'neutral', text:'(still not looking up) "Tell Rick I said the pickle\'s extra on Mondays."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"I will."' },
      { t:'say', char:'Hal',  expr:'neutral', text:'"Maya."' },
      { t:'narrate', text:"She pauses." },
      { t:'say', char:'Maya', expr:'neutral', text:'"Yeah."' },
      { t:'say', char:'Hal',  expr:'neutral', text:'"You didn\'t ask my name."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"I didn\'t."' },
      { t:'say', char:'Hal',  expr:'neutral', text:'"Good girl."' },

      { t:'narrate', text:"She leaves." },
      { t:'hide', pos:'left' }, { t:'hide', pos:'right' },

      { t:'narrate', text:"As she crosses the parking lot to her bike — she does not have a car; the Corolla is Sam's; Maya's bike has been, since her arrival, her full transportation stack — she glances back at the shop's front window." },
      { t:'narrate', text:"The man inside has not moved. He is still reading the Portuguese book. But the shop's other customer, a woman in a floral dress who had been in the periodicals section when Maya had come in, is now, Maya can see through the glass, at the counter, saying something to the man. The man is nodding. The man is not looking at the woman's face. The man is looking at the window — at Maya." },
      { t:'narrate', text:"Maya waves, small and brief. The man nods, small and brief. Then he turns fully to the woman in the floral dress, and Maya is no longer the subject of the shop's attention, and the transaction, whatever it was, is over." },

      { t:'narrate', text:"She mounts her bike. She rides back toward Harmony Creek. The envelope, against her ribs, is warm from her body. She does not open it on the road." },
      { t:'narrate', text:"She will, when she gets back to Cosmic Comics, hand it to Rick unopened, as instructed. Rick will take it and nod and open the back office door and disappear into it. Maya will not see what is inside the envelope." },

      { t:'narrate', text:"But six days from now, at ten-oh-three PM on a Sunday, Maya will be sitting at her own desk in her bedroom at her grandmother's house, and Rick will text her — for the first time ever, from a number she has not, until that moment, had — a single photograph." },
      { t:'narrate', text:"The photograph will be the contents of the envelope. The photograph will be a map. The map will show the east side of Harmony Creek Estates. On the map, a small inked circle will surround a particular building that is, as F.T. had said, not currently on any map." },
      { t:'narrate', text:"Maya will look at the map for a long time. She will, the following Monday, take the map to Sam." },
      { t:'narrate', text:"But that is six days away, and tonight is only Monday, and the summer is only three days old, and Maya is on her bike riding the long slow arterial back into her subdivision under the flat Texas afternoon light with an envelope under her jacket that she has not, will not, has promised not to, open. She pedals." },

      { t:'narrate', text:"Overhead, a crow flies. Not the cat's crow. Not any crow she has, previously, noticed. This crow is simply a crow." },
      { t:'narrate', text:"She does not know yet that most of the crows are not simply crows. She will learn." },

      { t:'jump', scene:'vol6_ch2_gas_go_lot' },
    ]
  },

  vol6_ch2_gas_go_lot: {
    id:'vol6_ch2_gas_go_lot', vol:6, chapter:2, type:'chapter',
    title:"Ch 2 — The Gas & Go Lot",
    nodes:[
      { t:'bg', src:'assets/backgrounds/vol6_gas_and_go_dusk.jpg' },
      { t:'hide', pos:'left' }, { t:'hide', pos:'center' }, { t:'hide', pos:'right' },
      { t:'interlude', text:'NexCorp Gas & Go', sub:'Monday · 19:52', duration:1800 },

      { t:'narrate', text:"The evening shift at the Gas & Go has started." },
      { t:'narrate', text:"Skip Donnelly is gone. The person behind the counter is a woman in her thirties whose name Sam does not know, who Sam has seen exactly once before, who Sam is now watching from her car in the Kwik Stop lot across the street." },
      { t:'show', char:'sam', expr:'neutral', pos:'center' },

      { t:'narrate', text:"Sam is off shift. Sam is supposed to be home. Sam has been parked in the Kwik Stop lot for eleven minutes, watching the Gas & Go through her windshield. Her hands are on the steering wheel. Her phone is on the passenger seat." },
      { t:'narrate', text:"She is not, in the end, going over there. She has just had the conversation with herself about whether to go over there. She has lost the conversation. Or — she has won it, depending on which version of herself she has decided, for this afternoon, to be on the side of." },

      { t:'narrate', text:"Graciela had said — Do not go looking for the truck. Sam is not, technically, going looking for the truck. Sam is looking at the place where the truck might have been, the day before it stopped being. There is a difference. There is also, she is aware, not a difference." },

      { t:'narrate', text:"She takes out her phone. She looks at her thread with Diego." },
      { t:'say', char:'Sam', role:'— text · sent yesterday 15:01 —', expr:'neutral', text:'bored. u alive?' },
      { t:'narrate', text:"Sent yesterday at 15:01. Still unread. She does not send another." },

      { t:'narrate', text:"Instead, she types a new message, to Maya Daigle — a number she has had in her contacts since last September, when they had briefly been assigned the same biology lab partner and had traded numbers for an online quiz, and which she has not used since:" },

      { t:'say', char:'Sam',  role:'— text · 19:54 —', expr:'neutral', text:'hey maya. sam miller. this is random. do you work at cosmic comics tomorrow?' },
      { t:'narrate', text:"The reply comes in under two minutes." },
      { t:'say', char:'Maya', role:'— text —', expr:'neutral', text:'Yeah. 10-5. Do you want to come by?' },

      { t:'narrate', text:"Sam stares at the reply. Maya had typed Do you want to come by? with a period at the end. Not a question mark. A period." },
      { t:'narrate', text:"Sam, who is her father's daughter in the specific narrow sense that she has been raised to notice pointed punctuation, registers it." },

      { t:'say', char:'Sam',  role:'— text —', expr:'neutral', text:'yes. is 11 ok?' },
      { t:'say', char:'Maya', role:'— text —', expr:'neutral', text:'Yes. Come in the back. Door at the rear of the strip mall. Unlocked from 10:45 to 11:15.' },
      { t:'say', char:'Sam',  role:'— text —', expr:'neutral', text:'ok.' },

      { t:'narrate', text:"She puts the phone down. She starts the Corolla. She drives home." },

      // ── Dinner with Dad ──────────────────────────────────────────────────
      { t:'bg', src:'assets/backgrounds/vol6_miller_kitchen.jpg' },
      { t:'interlude', text:'Miller Kitchen', sub:'Monday · 20:30', duration:1600 },
      { t:'show', char:'chief_miller', expr:'neutral', pos:'left'  },
      { t:'show', char:'sam',          expr:'neutral', pos:'right' },

      { t:'narrate', text:"At the kitchen table, her father is eating dinner. Meatloaf. Her mother made it. Her mother is at the stove finishing the green beans. The kitchen smells the way the kitchen always smells on Monday night in Harmony Creek Estates. The small flat screen mounted above the breakfast nook is tuned to local news, volume low." },

      { t:'say', char:'Chief Miller', expr:'neutral', text:'"Hey, Sammy."' },
      { t:'say', char:'Sam',          expr:'neutral', text:'"Hey, Dad. Hey, Mom."' },
      { t:'say', char:'Chief Miller', expr:'neutral', text:'"There\'s a plate in the microwave for you."' },
      { t:'say', char:'Sam',          expr:'neutral', text:'"Thanks."' },

      { t:'narrate', text:"She gets the plate. She sits. She eats. The meatloaf is good. It has always been good. Her mother's meatloaf, as a category, is the thing Sam misses most whenever she is hungry anywhere outside this house." },

      { t:'narrate', text:"Her father is on his phone. He is, she notices, holding the phone in his lap under the table, angled so the screen cannot be seen from her side of the table. He is not eating. He is typing." },
      { t:'narrate', text:"He finishes typing. He sets the phone face-down beside his plate. He picks up his fork. He smiles at her." },

      { t:'say', char:'Chief Miller', expr:'neutral', text:'"How was work, Sammy?"' },
      { t:'say', char:'Sam',          expr:'neutral', text:'"Slow. Same old."' },
      { t:'say', char:'Chief Miller', expr:'neutral', text:'"Beer sale?"' },
      { t:'say', char:'Sam',          expr:'neutral', text:'"One. Same guy as yesterday."' },

      { t:'narrate', text:"She watches his face when she says it. His face does not change." },
      { t:'say', char:'Chief Miller', expr:'neutral', text:'(easily) "Huh. Gotta love a routine."' },
      { t:'say', char:'Sam',          expr:'neutral', text:'"Yeah."' },

      { t:'narrate', text:"He eats. She eats. The local news, above the breakfast nook, cuts to a weather segment. The weather segment is predicting a thunderstorm on Wednesday — the first of the season. Her mother turns from the stove." },
      { t:'narrate', text:'"You kids shouldn\'t drive Wednesday night if it\'s bad. They\'re saying marble-sized hail on the coast."' },
      { t:'say', char:'Sam', expr:'neutral', text:'"I don\'t have any plans, Mom."' },
      { t:'narrate', text:'"Well if you did, cancel them."' },
      { t:'say', char:'Sam', expr:'neutral', text:'"Yes, ma\'am."' },

      { t:'narrate', text:"Her father, under the table, begins typing again. Sam does not, for the rest of the meal, look at him." },

      { t:'jump', scene:'vol6_ch2_maya_bedroom' },
    ]
  },

  vol6_ch2_maya_bedroom: {
    id:'vol6_ch2_maya_bedroom', vol:6, chapter:2, type:'chapter',
    title:"Ch 2 — Maya's Bedroom",
    nodes:[
      { t:'bg', src:'assets/backgrounds/vol6_maya_bedroom.jpg' },
      { t:'hide', pos:'left' }, { t:'hide', pos:'center' }, { t:'hide', pos:'right' },
      { t:'interlude', text:"Maya Daigle's Bedroom", sub:'Monday · 22:46', duration:1800 },

      { t:'show', char:'maya', expr:'neutral', pos:'center' },
      { t:'narrate', text:"Maya is not asleep." },
      { t:'narrate', text:"The shortwave downstairs has been silent since nine. Her grandmother went to bed at nine-thirty. The house has been quiet for an hour and seventeen minutes. Maya's ThinkPad is open on the desk. She has not opened the chat window." },

      { t:'narrate', text:"She is lying on top of the bedspread in the clothes she wore all day, staring at the ceiling." },

      { t:'think', char:'Maya', text:"Sam Miller is coming to the shop tomorrow." },
      { t:'think', char:'Maya', text:"Rick told me to keep noticing. F.T. told me to keep noticing. Graciela Ramos, who I have never met, is apparently in a parallel thread with a grown woman I have also never met, who is probably the reporter in the Houston Chronicle lanyard. A man named Hal in New Auburn runs a bookshop and takes envelopes." },
      { t:'think', char:'Maya', text:"I am the youngest person in this network and the only one new to it. The network is not mine. But the network has decided that I am part of it. And the network is, as far as I can tell, running in my direction." },
      { t:'think', char:'Maya', text:"I am going to be careful. I am going to be useful. I am not going to be a hero. I am going to be Maya." },

      { t:'narrate', text:"She thinks this with a small steady clarity that surprises her, because she has not, in her life until this summer, known what she was like when she was alone with a plan. She now knows." },

      // ── F.T. message ─────────────────────────────────────────────────────
      { t:'narrate', text:"The ThinkPad dings. A message from F.T." },
      { t:'say', char:'F.T.', role:'— chat —', expr:'neutral', text:'sleep, kid. tomorrow is important. three of you are about to start being a thing. don\'t rush it. let sam come in her own speed. she\'s going to be fast. let her be fast. you\'re the one who holds the tempo. that is your actual job.' },
      { t:'say', char:'F.T.', role:'— chat —', expr:'neutral', text:'also: your grandmother knows you know. she has known for a week. she is proud of you. she just does not have the vocabulary to say so. please be kind to her.' },
      { t:'say', char:'F.T.', role:'— chat —', expr:'neutral', text:'— f.t.' },

      // ── Grandmother ──────────────────────────────────────────────────────
      { t:'narrate', text:"Maya reads the message. She gets up. She crosses the hall. She opens her grandmother's bedroom door, quietly, just an inch." },

      { t:'bg', src:'assets/backgrounds/vol6_grandmother_bedroom.jpg' },
      { t:'show', char:'grandmother', expr:'neutral', pos:'left'  },
      { t:'show', char:'maya',        expr:'neutral', pos:'right' },
      { t:'narrate', text:"Her grandmother is awake in the dark." },

      { t:'say', char:'Grandmother', expr:'neutral', text:'(in the soft tired voice of a woman who has been waiting for this exact knock) "Maya, honey."' },
      { t:'say', char:'Maya',        expr:'neutral', text:'"Grandma."' },
      { t:'say', char:'Grandmother', expr:'neutral', text:'"Come in here."' },

      { t:'narrate', text:"Maya goes in. She sits on the edge of the bed. Her grandmother takes her hand." },

      { t:'say', char:'Grandmother', expr:'neutral', text:'"I\'ve been waiting to tell you. I didn\'t know how. I was going to tell you this weekend. I\'m sorry it took me this long."' },
      { t:'say', char:'Maya',        expr:'neutral', text:'"Grandma. It\'s okay."' },
      { t:'say', char:'Grandmother', expr:'neutral', text:'"It\'s not, honey. But thank you."' },

      { t:'narrate', text:"They sit in the dark for a while. Her grandmother's hand on her hand." },

      { t:'say', char:'Grandmother', expr:'neutral', text:'(eventually) "There will be men in this house at some point. Not bad men. Men who look like bad men, and who act like bad men, and whose purpose is good. When they come, I need you to let me do the talking. Can you do that for me."' },
      { t:'say', char:'Maya',        expr:'neutral', text:'"Yes."' },
      { t:'say', char:'Grandmother', expr:'neutral', text:'"Good girl."' },

      { t:'say', char:'Maya',        expr:'neutral', text:'"Grandma. Why is there a radio in your room on 1776 kHz."' },
      { t:'narrate', text:"A small silence." },
      { t:'say', char:'Grandmother', expr:'neutral', text:'"Because your grandfather put it there, Maya. In 1989. When he got out. He taught me how to listen to it. He said — Linda, one day somebody\'s going to talk to you on this thing, and you\'re going to know when they do, and then you\'re going to know what to do."' },

      { t:'say', char:'Maya',        expr:'neutral', text:'"My grandfather."' },
      { t:'say', char:'Grandmother', expr:'neutral', text:'"Your grandfather."' },
      { t:'say', char:'Maya',        expr:'neutral', text:'"What did he — what was he out of."' },

      { t:'narrate', text:"Her grandmother is quiet for a moment." },
      { t:'say', char:'Grandmother', expr:'neutral', text:'"Honey. Your grandfather was a photographer. In Graustark. In the seventies. He took a picture he should not have taken. It cost him fifteen years."' },

      { t:'narrate', text:"Maya stares at her in the dark." },
      { t:'say', char:'Grandmother', expr:'neutral', text:'(very gently) "Go to sleep, honey. Tomorrow\'s a big day. We\'ll talk more. There\'s a lot you need to know, and I\'m going to try to be the one to tell it. I have been afraid. I am still afraid. But I\'m done pretending I\'m not."' },
      { t:'say', char:'Maya',        expr:'neutral', text:'"Grandma."' },
      { t:'say', char:'Grandmother', expr:'neutral', text:'"Yes, honey."' },
      { t:'say', char:'Maya',        expr:'neutral', text:'"I love you."' },
      { t:'say', char:'Grandmother', expr:'neutral', text:'"I love you too, sweetheart. Go to bed."' },

      { t:'narrate', text:"Maya kisses her grandmother on the forehead. She goes back to her room. She closes her door." },
      { t:'hide', pos:'left' },
      { t:'narrate', text:"She does not, tonight, write in the notebook. She lies down. She turns off the lamp." },

      { t:'think', char:'Maya', text:"I have a grandfather. He took a picture. This town has been coming for pictures for a long time." },
      { t:'narrate', text:"She sleeps." },
      { t:'flag', key:'maya_knows_grandfather', val:true },

      { t:'jump', scene:'vol6_ch2_coda' },
    ]
  },

  vol6_ch2_coda: {
    id:'vol6_ch2_coda', vol:6, chapter:2, type:'chapter',
    title:"Ch 2 — The Hum, Everywhere, Holds",
    nodes:[
      { t:'bg', src:'assets/backgrounds/vol6_culdesac_night.jpg' },
      { t:'hide', pos:'left' }, { t:'hide', pos:'center' }, { t:'hide', pos:'right' },
      { t:'interlude', text:'Monday night', sub:'The summer is three days old.', duration:2200 },

      { t:'narrate', text:"Outside, in the cul-de-sac, the night does its Monday work. The streetlamps buzz at their subaudible frequency. A black cat crosses Prairie View." },
      { t:'narrate', text:"In a white sedan parked at the curb, two people who are not from Harmony Creek — one of whom has a press lanyard, the other of whom has a sunburn — take their shifts on a vigil neither of them has been formally assigned and neither of them has, in so many words, ever discussed. They drink cold coffee from the same thermos." },

      { t:'narrate', text:"In the darkroom at 3017 Verbena, Mr. Henderson has taken three new photographs. He is developing them now." },

      { t:'narrate', text:"In his bedroom, Jesse Henderson is not asleep. He is on his phone, reading, for the eleventh time, a text from Sam Miller that had come through at 21:44 reading only — you up." },
      { t:'narrate', text:"He has not, yet, replied. He will." },

      { t:'narrate', text:"At the Kwik Stop, Jen the day manager is closing up." },
      { t:'narrate', text:"At the Pit Stop, Ben is on a double. He is still on the grill. He is also, between orders, watching the parking lot." },

      { t:'narrate', text:"At Sam Miller's house, Sam is at her desk. Her bedroom door is closed. She is holding her phone in her lap. The text she sent Jesse at 21:44 is marked delivered, not read." },
      { t:'narrate', text:"She is waiting." },
      { t:'narrate', text:"She is learning, in the waiting, that she is going to be a person who can wait." },

      { t:'narrate', text:"The summer is three days old. The hum, everywhere, holds." },

      { t:'narrate', text:"The Magician, reversed, watches his apprentices begin to pick up the tools they have not yet been told they know how to use." },
      { t:'narrate', text:"The tools, on their shelves, wait to be chosen." },

      { t:'flag', key:'vol6_ch2_complete', val:true },
      { t:'interlude', text:'— end of chapter 2 —', sub:'Gas Station Oracles & Slushie Futures', duration:2800 },
      { t:'end' },
    ]
  },

  // ── Vol 6 · Chapter 3 — Last Seen at the Circle K (Or Was It?) ─────────────
  // The High Priestess. Tuesday across Harmony Creek. Sam learns her father's
  // morning. Sam meets Maya in the back of Cosmic Comics. The sedan follows.
  // Ben writes the list down. Jesse texts Sam and Ben and goes to say
  // goodnight to his mother. Sam sleeps badly. Rick reads F.T.'s note in the
  // back office of Cosmic Comics.

  vol6_ch3_circle_k: {
    id:'vol6_ch3_circle_k', vol:6, chapter:3, type:'chapter',
    title:'Ch 3 — Last Seen at the Circle K (Or Was It?)',
    nodes:[
      { t:'bg', src:'assets/backgrounds/vol6_miller_kitchen_morning.jpg' },
      { t:'bgm', src:'assets/audio/bgm/vol6_ambient.mp3' },
      { t:'interlude', text:'Chapter 3', sub:'Last Seen at the Circle K (Or Was It?)', duration:3000 },
      { t:'interlude', text:'The High Priestess.', sub:'The girl between two pillars is learning to hold her breath.', duration:3000 },

      // ── Sam's kitchen ────────────────────────────────────────────────────
      { t:'interlude', text:'1428 Meadowlark Circle — Kitchen', sub:'Tuesday · 07:14', duration:1800 },

      { t:'show', char:'sam', expr:'neutral', pos:'center' },
      { t:'narrate', text:"Sam is down before her father for the first time in six months." },
      { t:'narrate', text:"She has been awake since five-thirty. She has been at the kitchen table since six-fifty, with a bowl of cereal and the sports page of the New Auburn Sentinel her father reads every morning, which she has no interest in but which is the kind of thing people read who have been awake for exactly the right amount of time. She has cycled through the section twice. She has, in fact, read a recap of a Little League game in a town she has never heard of, in case her father asks." },
      { t:'narrate', text:"Her father does not ask." },

      { t:'show', char:'chief_miller', expr:'neutral', pos:'left' },
      { t:'narrate', text:"He comes downstairs at 07:14. He is already in uniform. He pauses at the doorway. His expression does the small adjustment faces make when a parent registers, in their peripheral vision, that their child has rearranged the default order of the household without announcement." },

      { t:'say', char:'Chief Miller', expr:'neutral', text:'"Morning, Sammy."' },
      { t:'say', char:'Sam',          expr:'neutral', text:'"Morning, Dad."' },
      { t:'say', char:'Chief Miller', expr:'neutral', text:'"You\'re up early."' },
      { t:'say', char:'Sam',          expr:'neutral', text:'"Couldn\'t sleep."' },

      { t:'narrate', text:"He crosses to the coffee pot. He pours a mug. He looks at the paper." },
      { t:'say', char:'Chief Miller', expr:'neutral', text:'"Anything good?"' },
      { t:'say', char:'Sam',          expr:'neutral', text:'"Brewers won."' },
      { t:'say', char:'Chief Miller', expr:'neutral', text:'"Huh."' },

      { t:'narrate', text:"He sits across from her. He picks up the paper. He reads. Sam watches him, carefully, without watching him." },
      { t:'narrate', text:"She has decided, at about three AM, that her first task is to learn her father's morning. She has been in this kitchen, at breakfast, with this man, almost every morning of her seventeen years. She has not, until today, paid attention. She catalogues, now, what she has never catalogued." },

      { t:'think', char:'Sam', text:"07:15 — his first sip of coffee. He makes a small grunt. Every morning. I have heard the grunt every morning and have never, until today, registered it as information." },
      { t:'think', char:'Sam', text:"07:17 — his phone buzzes. He does not look at it. He lets it buzz itself out." },
      { t:'think', char:'Sam', text:"07:22 — his phone buzzes again. This time he looks. He frowns, briefly. He types a short response with his thumb and sets the phone face-down again." },

      // ── The list ─────────────────────────────────────────────────────────
      { t:'narrate', text:"07:24 — he stands up. He rinses his mug. He puts it in the drying rack. He says, without turning:" },
      { t:'say', char:'Chief Miller', expr:'neutral', text:'"Plans today?"' },
      { t:'say', char:'Sam',          expr:'neutral', text:'(evenly) "I\'m gonna meet up with Maya Daigle at Cosmic Comics this morning. She\'s at the shop till five. I\'ll probably stay a while and help her sort back issues."' },

      { t:'narrate', text:"He pauses at the sink. Not long. Maybe a second and a half. Just long enough that she registers the pause without, quite, being able to claim she did." },
      { t:'say', char:'Chief Miller', expr:'neutral', text:'"Maya Daigle."' },
      { t:'say', char:'Sam',          expr:'neutral', text:'"Yeah. Jimmy Daigle\'s daughter. She moved in with her grandma in April."' },
      { t:'say', char:'Chief Miller', expr:'neutral', text:'"I know who she is."' },

      { t:'narrate', text:"She does not say anything." },
      { t:'say', char:'Chief Miller', expr:'neutral', text:'(in a small careful voice that is not quite the voice he uses with her ordinarily) "She doing alright over there?"' },
      { t:'say', char:'Sam',          expr:'neutral', text:'"I think so. I don\'t know her that well yet."' },
      { t:'say', char:'Chief Miller', expr:'neutral', text:'"Mm."' },

      { t:'narrate', text:"He dries his hands. He turns." },
      { t:'say', char:'Chief Miller', expr:'neutral', text:'"You got your phone on you today?"' },
      { t:'say', char:'Sam',          expr:'neutral', text:'"Yeah."' },
      { t:'say', char:'Chief Miller', expr:'neutral', text:'"Good. Text me if you head anywhere that\'s not on the list."' },
      { t:'say', char:'Sam',          expr:'neutral', text:'(blinking) "The list."' },
      { t:'say', char:'Chief Miller', expr:'neutral', text:'"Kwik Stop. Cosmic Comics. The Pit Stop. Home. The Whataburger on 1604 if you\'re with a group."' },
      { t:'say', char:'Sam',          expr:'neutral', text:'"Dad. I\'ve never had a list."' },
      { t:'say', char:'Chief Miller', expr:'neutral', text:'"Today you do."' },

      { t:'narrate', text:"She looks at him. He smiles — the automatic smile, the Dad smile, the one he has been smiling at her since she was born." },
      { t:'say', char:'Chief Miller', expr:'neutral', text:'"Just indulge me, Sammy. Couple of weird things coming across my desk this week. Probably nothing. But it makes me feel better if I know where you are."' },
      { t:'say', char:'Sam',          expr:'neutral', text:'"Okay."' },
      { t:'say', char:'Chief Miller', expr:'neutral', text:'"Love you."' },
      { t:'say', char:'Sam',          expr:'neutral', text:'"Love you too, Dad."' },

      { t:'narrate', text:"He leaves through the garage. Sam listens to his truck start, reverse out, and leave. She sits at the table. She finishes her cereal." },
      { t:'hide', pos:'left' },

      // ── The text from M. ─────────────────────────────────────────────────
      { t:'narrate', text:"At 07:33, her phone buzzes. A text from an unknown number, no area code visible." },
      { t:'say', char:'M.', role:'— text · 07:33 · unknown —', expr:'neutral', text:'Graciela says trust Maya. Go see her. Do not tell anyone you have this number. — M.' },

      { t:'narrate', text:"Sam reads it three times. She does not reply. She deletes the thread." },
      { t:'narrate', text:"She clears her bowl. She puts it in the drying rack next to her father's mug. She goes upstairs to get dressed." },

      { t:'jump', scene:'vol6_ch3_back_room' },
    ]
  },

  vol6_ch3_back_room: {
    id:'vol6_ch3_back_room', vol:6, chapter:3, type:'chapter',
    title:'Ch 3 — Cosmic Comics Back Room',
    nodes:[
      { t:'bg', src:'assets/backgrounds/vol6_cosmic_back_room.jpg' },
      { t:'hide', pos:'left' }, { t:'hide', pos:'center' }, { t:'hide', pos:'right' },
      { t:'interlude', text:'Cosmic Comics — Back Room', sub:'Tuesday · 11:02', duration:1800 },

      { t:'narrate', text:"The door at the back of the strip mall is unlocked, exactly as promised." },
      { t:'show', char:'sam',  expr:'neutral', pos:'right' },
      { t:'show', char:'maya', expr:'neutral', pos:'left'  },
      { t:'narrate', text:"Sam slips in. The back room of Cosmic Comics is smaller than she imagined — an L-shaped storage and office area, lit by a single overhead with a pull chain, stacked with long boxes and cardboard cartons of new releases still in shrink. There is a small desk in one corner, a mini-fridge, a calendar of cats from 2022 nobody has taken down." },

      { t:'narrate', text:"Maya is sitting on the desk. She has two iced coffees. She hands one to Sam." },
      { t:'say', char:'Maya', expr:'neutral', text:'"Hey."' },
      { t:'say', char:'Sam',  expr:'neutral', text:'"Hey."' },
      { t:'narrate', text:"Sam takes the coffee. Sam sits on an overturned milk crate opposite the desk. Maya closes the door. She slides a bolt Sam did not realize was there." },

      { t:'say', char:'Sam',  expr:'neutral', text:'"Okay."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"Okay."' },
      { t:'narrate', text:"They look at each other." },
      { t:'narrate', text:"Maya is, Sam registers, about three inches shorter than she is. Dark hair in a single braid over one shoulder. Glasses. A shirt from a band Sam doesn't know. The specific careful stillness of a kid who has trained herself out of fidgeting." },

      { t:'say', char:'Sam',  expr:'neutral', text:'"I don\'t know what I\'m doing here."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"I know. That\'s fine."' },
      { t:'say', char:'Sam',  expr:'neutral', text:'"I — my boyfriend is —"' },
      { t:'say', char:'Maya', expr:'neutral', text:'"Diego. Yeah. I know."' },
      { t:'narrate', text:"Sam exhales." },
      { t:'say', char:'Sam',  expr:'neutral', text:'"Maya. How do you know."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"Because somebody told me. Somebody who told me before you knew yourself, actually. I want to tell you three things, and if any of them freak you out, you can leave and I won\'t follow up. Okay?"' },
      { t:'say', char:'Sam',  expr:'neutral', text:'"Okay."' },

      // ── Three things ─────────────────────────────────────────────────────
      { t:'say', char:'Maya', expr:'neutral', text:'"Thing one: Diego is alive. He is not at home. He is being held somewhere on the east side of the subdivision. I don\'t know exactly where yet, but I will by next Sunday. My source on this is a person called F.T. I don\'t know who F.T. is. Rick, up front, does know. Rick is not going to tell us. Rick knows some things about our dads that I don\'t. My grandmother knows some other things about some other people."' },
      { t:'narrate', text:"Sam is silent." },
      { t:'say', char:'Maya', expr:'neutral', text:'"Thing two: your dad knows. About Diego. Not necessarily because he caused it — I don\'t know that part yet. But he knows, and he has chosen not to tell you. He came by Diego\'s grandmother\'s house Sunday morning at seven. He sat in his truck at the end of the driveway for eleven minutes. He did not knock."' },
      { t:'narrate', text:"Sam stares at her." },
      { t:'say', char:'Maya', expr:'neutral', text:'(gently) "I am sorry I am the one telling you this."' },
      { t:'say', char:'Sam',  expr:'neutral', text:'"Don\'t — Maya. I already figured it out. I figured it out last night. I watched him text somebody under the kitchen table at dinner. It was — I already knew. Keep going."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"Thing three: there are other adults in this town who know. I don\'t mean bad. I mean on your side. My grandmother. Rick. A bookshop guy in New Auburn named Hal. Diego\'s grandmother. There\'s a reporter from the Houston Chronicle working on something. There are two people in a white sedan parked at the Kwik Stop for the past two days —"' },
      { t:'say', char:'Sam',  expr:'neutral', text:'"I saw them —"' },
      { t:'say', char:'Maya', expr:'neutral', text:'"— who are watching out for you. Not watching you. Watching over you. Graciela vouched for them."' },

      { t:'narrate', text:"Sam puts her forehead on her hand." },
      { t:'say', char:'Sam',  expr:'neutral', text:'(not quite steadily) "Maya. This is — this is so much."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"I know."' },
      { t:'say', char:'Sam',  expr:'neutral', text:'"How did — how did you get here first."' },

      { t:'narrate', text:"Maya thinks about it. Then she says, honestly:" },
      { t:'say', char:'Maya', expr:'neutral', text:'"Because my dad was in it. Not this specifically. Something like this, somewhere else, a long time ago. He sent me up here to get out of it. My grandmother has been waiting. The people she was waiting to hear from started talking to her last week. They told her I was ready."' },
      { t:'say', char:'Sam',  expr:'neutral', text:'"Your dad."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"Jimmy Daigle."' },
      { t:'say', char:'Sam',  expr:'neutral', text:'"I know. I mean — are you okay."' },

      { t:'narrate', text:"Maya pauses." },
      { t:'say', char:'Maya', expr:'neutral', text:'"That\'s a nice question. I don\'t — yeah. I think so. I\'m not, maybe. But I\'m okay for now. Thank you for asking."' },
      { t:'say', char:'Sam',  expr:'neutral', text:'"Sure."' },

      { t:'narrate', text:"Sam drinks some of her coffee. Her hand is, she notices, not shaking. She had expected it to be shaking. She makes a small mental note to come back, later, to the fact that it is not." },

      { t:'say', char:'Sam',  expr:'neutral', text:'"What do we do."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"Today? Nothing. We let ourselves meet. We let me make the map I am going to make. We let you go home and practice being a regular teenager around your regular father for the next five days. F.T. thinks you are going to be fast when you decide to move. He is not wrong to think that. He also thinks we are not supposed to move yet."' },
      { t:'say', char:'Sam',  expr:'neutral', text:'"Five days."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"Yeah. Sunday. Rick will get a thing to me Sunday night. I will show it to you Monday. Then we make a plan."' },
      { t:'narrate', text:"Sam nods." },

      { t:'say', char:'Sam',  expr:'neutral', text:'"I need to ask you something. And I want you to tell me the truth."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"Okay."' },
      { t:'say', char:'Sam',  expr:'neutral', text:'"Is Diego — is he being hurt."' },
      { t:'narrate', text:"Maya is quiet." },
      { t:'say', char:'Maya', expr:'neutral', text:'"I don\'t know. F.T. said not okay, but alive. That is all he said. I am going to assume it is the worse of the possible meanings until I learn otherwise. I think we should both assume that. But I do not know."' },
      { t:'narrate', text:"Sam closes her eyes. Sam opens them." },
      { t:'say', char:'Sam',  expr:'neutral', text:'"Okay."' },

      { t:'say', char:'Maya', expr:'neutral', text:'"Sam."' },
      { t:'say', char:'Sam',  expr:'neutral', text:'"Yeah."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"I don\'t know you very well yet. But I\'m going to say this, because my grandmother said it to me last night and it helped: you are allowed to be this scared. You are allowed to be this angry. What you are not allowed to be is alone in it. I\'m here. I\'m the one who was sent, or I volunteered, or both — I don\'t know. But I\'m in this with you until we find him."' },

      { t:'narrate', text:"Sam looks at her for a long moment." },
      { t:'say', char:'Sam',  expr:'neutral', text:'"Thank you."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"Yeah."' },
      { t:'say', char:'Sam',  expr:'neutral', text:'"Maya."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"Yeah."' },
      { t:'say', char:'Sam',  expr:'neutral', text:'"I might need you to tell me things like that sometimes. Even if it feels dumb."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"It won\'t feel dumb."' },
      { t:'say', char:'Sam',  expr:'neutral', text:'"It will."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"Okay. I\'ll tell you anyway."' },

      { t:'narrate', text:"They sit for a minute. Sam drinks her coffee. Maya drinks hers." },

      // ── The five ─────────────────────────────────────────────────────────
      { t:'say', char:'Maya', expr:'neutral', text:'"One more thing, and then we are going to go out to the store and you are going to browse for forty-five minutes and I am going to ring you up for a back issue of something, and we are going to look like two girls who went to the comic shop together on a Tuesday."' },
      { t:'say', char:'Sam',  expr:'neutral', text:'"Okay."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"Ben Kowalski."' },
      { t:'say', char:'Sam',  expr:'neutral', text:'"Ben — the one at the Pit Stop?"' },
      { t:'say', char:'Maya', expr:'neutral', text:'"Yeah."' },
      { t:'say', char:'Sam',  expr:'neutral', text:'"What about him."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"He\'s keeping a legal pad. He has been watching cars and off-duty cops and the backyard wrestling at the McClary place since March. He\'s one of us. He doesn\'t know that yet. Jesse Henderson found out yesterday. Jesse\'s dad is taking photographs that are — Jesse\'s dad is not okay, Sam. His photographs are showing figures that were not in the frame. One of the figures is looking at him."' },
      { t:'say', char:'Sam',  expr:'neutral', text:'"His dad is —"' },
      { t:'say', char:'Maya', expr:'neutral', text:'"His dad is something. I don\'t know what yet. F.T. hasn\'t told me. I don\'t know if F.T. knows. But Jesse is going to need us too."' },
      { t:'say', char:'Sam',  expr:'neutral', text:'"Okay."' },
      { t:'say', char:'Maya', expr:'neutral', text:'"That\'s the group. Five of us. Plus the adults who are watching. You, me, Ben, Jesse. And Diego, when we get him."' },
      { t:'narrate', text:"When. Not if. Sam catches it. She nods." },
      { t:'say', char:'Sam',  expr:'neutral', text:'"Okay. Five."' },
      { t:'flag', key:'pc_group_of_five', val:true },

      { t:'jump', scene:'vol6_ch3_parking_lot' },
    ]
  },

  vol6_ch3_parking_lot: {
    id:'vol6_ch3_parking_lot', vol:6, chapter:3, type:'chapter',
    title:'Ch 3 — Parking Lot',
    nodes:[
      { t:'bg', src:'assets/backgrounds/vol6_cosmic_lot.jpg' },
      { t:'hide', pos:'left' }, { t:'hide', pos:'center' }, { t:'hide', pos:'right' },
      { t:'interlude', text:'Cosmic Comics — Parking Lot', sub:'Tuesday · 12:14', duration:1800 },

      { t:'narrate', text:"The white sedan is parked in the lot when Sam comes out." },
      { t:'narrate', text:"The driver — the woman with the HOUSTON CHRONICLE lanyard — is alone. She does not make eye contact as Sam crosses the lot. She is reading something on a tablet." },
      { t:'show', char:'sam', expr:'neutral', pos:'center' },

      { t:'narrate', text:"Sam gets into the Corolla. She pulls out. She does not look at the sedan as she passes. In the rearview, just before she turns onto Linden, she sees the sedan pull out behind her." },
      { t:'narrate', text:"The sedan takes the left turn Sam takes. The sedan stays three cars back for the entire five-minute drive to the Kwik Stop — where Sam is not scheduled but where she is going anyway, because she has decided she wants Jen to see her with her hair up and her eyes clear and her back straight, so that Jen knows, without being told, that Sam has heard her." },

      { t:'narrate', text:"When Sam parks at the Kwik Stop, the sedan does not park. It drives past, turns at the next intersection, and is gone." },

      // ── Inside ──────────────────────────────────────────────────────────
      { t:'bg', src:'assets/backgrounds/vol6_kwikstop_interior.jpg' },
      { t:'show', char:'jen', expr:'neutral', pos:'right' },
      { t:'narrate', text:"Sam goes inside. Jen is at the register. Jen sees her." },
      { t:'say', char:'Jen', expr:'neutral', text:'"You\'re not on."' },
      { t:'say', char:'Sam', expr:'neutral', text:'"I know."' },
      { t:'say', char:'Jen', expr:'neutral', text:'"You want a shift?"' },
      { t:'say', char:'Sam', expr:'neutral', text:'"No. I want a slushie. Blue."' },

      { t:'narrate', text:"Jen looks at her for a long moment." },
      { t:'say', char:'Jen', expr:'neutral', text:'"On the house."' },

      { t:'narrate', text:"Sam makes the slushie. She pays anyway — a dollar seventy-nine in cash. Jen takes it without comment. Jen puts the cash in her tip cup instead of the register." },
      { t:'narrate', text:"Sam drinks the slushie at one of the three tables by the window. She reads the day-old paper Jen has folded there. The paper is running a feature on local high school sports banquets." },

      // ── Dad text ────────────────────────────────────────────────────────
      { t:'narrate', text:"At 12:31, her phone buzzes." },
      { t:'say', char:'Chief Miller', role:'— text · 12:31 —', expr:'neutral', text:'Where you at, Sammy?' },
      { t:'say', char:'Sam',          role:'— text —',          expr:'neutral', text:'Kwik Stop. Got a slushie.' },
      { t:'say', char:'Chief Miller', role:'— text —',          expr:'neutral', text:'Okay. Be careful driving home. Lot of construction on Linden.' },
      { t:'say', char:'Sam',          role:'— text —',          expr:'neutral', text:'Will do.' },

      { t:'narrate', text:"She finishes the slushie. She drops the cup in the trash. She waves at Jen. She leaves." },
      { t:'hide', pos:'right' },

      { t:'narrate', text:"There is no construction on Linden. She drives it anyway. She notices, at the intersection with Fifth, a NexCorp van parked at the corner lot of a dental office that is closed on Tuesdays. The van's engine is running. The van is facing her direction." },
      { t:'narrate', text:"She does not slow down. She does not speed up. She drives the posted limit." },

      { t:'think', char:'Sam', text:"Maya is right. I am going to be fast when I decide. I am not deciding today." },
      { t:'narrate', text:"She drives home." },

      { t:'jump', scene:'vol6_ch3_pit_stop_office' },
    ]
  },

  vol6_ch3_pit_stop_office: {
    id:'vol6_ch3_pit_stop_office', vol:6, chapter:3, type:'chapter',
    title:'Ch 3 — Pit Stop Back Office',
    nodes:[
      { t:'bg', src:'assets/backgrounds/vol6_pit_stop_office.jpg' },
      { t:'hide', pos:'left' }, { t:'hide', pos:'center' }, { t:'hide', pos:'right' },
      { t:'interlude', text:'Pit Stop Diner — Back Office', sub:'Tuesday · 15:48', duration:1800 },

      { t:'show', char:'ben', expr:'neutral', pos:'center' },
      { t:'narrate', text:"Ben is at the small desk in the back office. His shift ended at two. He is not, technically, supposed to be in the office. He is here because he is writing." },
      { t:'narrate', text:"He is writing a list, and the list is starting to feel like a thing he is going to have to show someone." },

      { t:'narrate', text:"The list, at 15:48, reads —" },
      { t:'narrate', text:"1. Ramos kid — missing since Saturday night, 11:52 PM per neighbor reports via Sam per Jen per my own math. Not reported as missing by his grandmother to PSA. Not reported as missing by PSA internally. Silence is the information." },
      { t:'narrate', text:"2. Louisiana pickup in Pit Stop lot, Sunday and Monday, driver never enters. Plate: LA 7R3-G92. I ran it in my head against the pattern I noticed in March — it matches a plate I saw at the McClary fence Saturday night after the match. Same vehicle. Different driver? Unknown." },
      { t:'narrate', text:"3. White sedan in Kwik Stop lot, two people, press lanyard. Not threatening. Probably allies. Confirmed by — well, not confirmed. Inferred. Presence at both the Kwik Stop and the comic shop parking lot within 90 minutes of Sam Miller's visit to same. Sedan is moving with Sam, not against her." },
      { t:'narrate', text:"4. Unmarked NexCorp van, Gas & Go lot, Sunday 15:11, handoff with the Louisiana pickup. Envelope. Cash. Skip Donnelly did not see this because Skip was on his phone, which I am now beginning to think is not an accident of Skip's work ethic but an arranged condition." },
      { t:'narrate', text:"5. Jesse's dad — developing photographs containing people not in original frame. Jesse has eight-by-tens. I have phone photographs of them." },
      { t:'narrate', text:"6. Backyard wrestling thing — escalating. Saturday's officer-initiated match was a test. Test of what? Whether I'd go in the ring? Whether I'd go in the ring and lose gracefully? Tentative read: they are looking for compliant bodies in the teen-age demographic. Me. Jesse, next. Diego, already?" },
      { t:'narrate', text:"7. Diego as possible already-taken compliant body — cross-ref red-dot system on his phone. He was tracking specific shifts at the Gas & Go. He saw something. He told someone. Wrong someone. Now he's — where?" },

      { t:'narrate', text:"Ben sets down the pen. He rereads the list." },
      { t:'narrate', text:"He is, he registers, no longer a person who has a legal pad as a hobby. He is, he registers, a person who is building a case for something — and the something is starting to look large enough that Ben is going to have to start making decisions about what he is willing to do if the something turns out to be as large as the list is beginning to suggest." },

      { t:'narrate', text:"He is seventeen. He is six-foot-four. He is about to be late for his optional double, which Jesse had, in fact, requested this morning." },
      { t:'narrate', text:"He puts the list in the bottom drawer of the desk, beneath the folded apron. He closes the drawer. He stands. He goes to the grill." },
      { t:'narrate', text:"The grill is hot. The grill is ready. The grill does not know about the list and would not, if it did, be able to do anything about it. Ben picks up the spatula. He gets to work." },
      { t:'flag', key:'ben_has_list', val:true },

      { t:'jump', scene:'vol6_ch3_jesse_bedroom' },
    ]
  },

  vol6_ch3_jesse_bedroom: {
    id:'vol6_ch3_jesse_bedroom', vol:6, chapter:3, type:'chapter',
    title:"Ch 3 — Jesse's Bedroom",
    nodes:[
      { t:'bg', src:'assets/backgrounds/vol6_jesse_bedroom.jpg' },
      { t:'hide', pos:'left' }, { t:'hide', pos:'center' }, { t:'hide', pos:'right' },
      { t:'interlude', text:"Jesse Henderson's Bedroom", sub:'Tuesday · 21:46', duration:1800 },

      { t:'show', char:'jesse', expr:'neutral', pos:'center' },
      { t:'narrate', text:"Jesse has been in his bedroom since seven. He has eaten dinner — chicken and rice, which his mother made, which he ate without tasting — and he has been sitting on the floor with his back against his bed ever since, with his Telecaster unplugged in his lap, not playing it, just holding it." },
      { t:'narrate', text:"His phone pings." },

      { t:'say', char:'Sam',   role:'— text —', expr:'neutral', text:'hey.' },
      { t:'say', char:'Jesse', role:'— text —', expr:'neutral', text:'hey. you ok?' },
      { t:'say', char:'Sam',   role:'— text —', expr:'neutral', text:'yeah. sort of. i met maya today. we talked. she filled me in.' },
      { t:'say', char:'Sam',   role:'— text —', expr:'neutral', text:'jess i don\'t know what to do about your dad.' },

      { t:'narrate', text:"He stares at the screen." },
      { t:'say', char:'Jesse', role:'— text —', expr:'neutral', text:'me neither.' },
      { t:'say', char:'Sam',   role:'— text —', expr:'neutral', text:'ben says we wait for one more thing. maya says sunday or monday. i am trying to be patient.' },
      { t:'say', char:'Sam',   role:'— text —', expr:'neutral', text:'are you ok. like, at home. with him.' },

      { t:'narrate', text:"Jesse looks up at his bedroom door. It is closed. Behind it, somewhere in the house, he can hear the faint sound of his mother running the dishwasher. He cannot hear his father. His father has been in the darkroom since six-fifteen." },

      { t:'say', char:'Jesse', role:'— text —', expr:'neutral', text:'idk. he\'s been weird. mom is pretending she doesn\'t notice. he doesn\'t come up for meals some nights. he goes down there and stays down there.' },
      { t:'say', char:'Sam',   role:'— text —', expr:'neutral', text:'is he scary weird or sad weird.' },

      { t:'narrate', text:"Jesse thinks." },
      { t:'say', char:'Jesse', role:'— text —', expr:'neutral', text:'both. mostly sad. sometimes scary. not at me. at himself.' },
      { t:'say', char:'Sam',   role:'— text —', expr:'neutral', text:'ok. that\'s a data point. hold on to it. we\'ll figure it out.' },
      { t:'say', char:'Sam',   role:'— text —', expr:'neutral', text:'jess' },
      { t:'say', char:'Sam',   role:'— text —', expr:'neutral', text:'thank you for trusting me.' },

      // ── E-minor ─────────────────────────────────────────────────────────
      { t:'narrate', text:"He puts the phone face-down on the carpet. He picks up the Telecaster. He strums a single unplugged chord — E minor. The first chord he ever learned, the chord he plays when he does not know what to play. The strings hum. The hum goes nowhere, because the amp is off, but the guitar, against his chest, vibrates." },
      { t:'narrate', text:"It has always been a comforting vibration. It is less comforting tonight." },

      { t:'narrate', text:"He thinks about the photograph of the man in the charcoal suit. He thinks about the kid at the streetlight across from McClary's, who Ben saw, who should not have been visible, who waved. He thinks about his father, alone in the red light of the darkroom, looking at prints that had people in them who were not in the frame." },

      { t:'think', char:'Jesse', text:"My dad is being used as a camera. And he is the only person in the house who does not know it." },
      { t:'think', char:'Jesse', text:"My mom knows something is wrong. My mom is going to need to be told. My mom is not, yet, going to believe me. That is the next thing." },

      { t:'narrate', text:"He sets the guitar aside. He picks up the phone. He texts Ben:" },
      { t:'say', char:'Jesse', role:'— text · to Ben —', expr:'neutral', text:'hey. i need help with my mom. not tonight. soon. thinking maybe this weekend. will you help.' },
      { t:'narrate', text:"Ben replies in eight seconds." },
      { t:'say', char:'Ben',   role:'— text —', expr:'neutral', text:'yes. bring her to the pit stop on saturday morning. i\'ll be on shift. tell her it\'s breakfast. i\'ll handle it.' },
      { t:'narrate', text:"Jesse exhales." },
      { t:'say', char:'Jesse', role:'— text —', expr:'neutral', text:'thanks, ben.' },
      { t:'say', char:'Ben',   role:'— text —', expr:'neutral', text:'it\'s what friends do, jess.' },

      // ── Goodnight ───────────────────────────────────────────────────────
      { t:'narrate', text:"Jesse sets the phone down. He does not, tonight, cry. But his eyes fill, briefly, and he lets them, and he does not wipe them, and he sits on the floor of his bedroom with the Telecaster beside him and his mother running the dishwasher one floor down and his father in the red light two floors below, and he thinks, in the small settled voice that has begun, in the past twenty-four hours, to be an interior voice he recognizes as his own adult one:" },

      { t:'think', char:'Jesse', text:"I am going to be okay. I am going to be okay if I have Ben and Sam and Maya. I am, as of tonight, going to have Ben and Sam and Maya." },

      { t:'narrate', text:"He gets up. He puts the Telecaster back in its case. He opens his bedroom door. He goes downstairs to say goodnight to his mother — because he has not, he realizes, said goodnight to his mother in eight days." },

      { t:'bg', src:'assets/backgrounds/vol6_henderson_kitchen.jpg' },
      { t:'hide', pos:'center' },
      { t:'show', char:'mrs_henderson', expr:'neutral', pos:'left'  },
      { t:'show', char:'jesse',         expr:'neutral', pos:'right' },

      { t:'narrate', text:"She is at the sink, drying her hands." },
      { t:'say', char:'Mrs. Henderson', expr:'neutral', text:'"Hey, kiddo."' },
      { t:'say', char:'Jesse',          expr:'neutral', text:'"Hey, Mom."' },

      { t:'narrate', text:"He hugs her. She is startled, briefly, then pats his back in the way mothers pat the backs of teenage boys when the teenage boys hug them for no apparent reason — which is to say with the small careful warmth of not wanting to make the hug feel remarkable in case the remarkable-ness might cause the hugger to reconsider." },

      { t:'say', char:'Mrs. Henderson', expr:'neutral', text:'"You okay, Jess?"' },
      { t:'say', char:'Jesse',          expr:'neutral', text:'"Yeah, Mom. Just — yeah. Night."' },
      { t:'say', char:'Mrs. Henderson', expr:'neutral', text:'"Goodnight, sweetheart."' },

      { t:'narrate', text:"He goes back upstairs." },

      { t:'jump', scene:'vol6_ch3_sam_bedroom' },
    ]
  },

  vol6_ch3_sam_bedroom: {
    id:'vol6_ch3_sam_bedroom', vol:6, chapter:3, type:'chapter',
    title:"Ch 3 — Sam's Bedroom",
    nodes:[
      { t:'bg', src:'assets/backgrounds/vol6_sam_bedroom.jpg' },
      { t:'hide', pos:'left' }, { t:'hide', pos:'center' }, { t:'hide', pos:'right' },
      { t:'interlude', text:"1428 Meadowlark Circle — Sam's Bedroom", sub:'Tuesday · 22:34', duration:1800 },

      { t:'show', char:'sam', expr:'neutral', pos:'center' },
      { t:'narrate', text:"Sam is in bed. Lamp off. She has not showered. She has not, in fact, done anything for the last hour except stare at the ceiling and think, in a measured orderly way, about what she has learned today." },

      // ── The catalogue ────────────────────────────────────────────────────
      { t:'narrate', text:"The catalogue so far —" },
      { t:'narrate', text:"Her father is part of it, in a way she does not yet know the size of. Graciela is part of a network. Maya is part of the network, and was inserted by the network, and is not, herself, managing it." },
      { t:'narrate', text:"F.T. is running at least part of the network and is either in New Orleans or Graustark and has some connection to Jimmy Daigle that predates Jimmy Daigle's current condition. Rick, Hal, the reporter in the sedan, the partner in the sedan, Miriam (whose name Sam has not yet been given but whose existence she has inferred from context), and at least one other adult Sam cannot yet place — these are nodes." },
      { t:'narrate', text:"Ben has been doing the same work from a different entry point for three months, without knowing there was a network, and is about to discover that there is one. Jesse's father is somehow involved but is probably, Sam now suspects, a victim of the apparatus rather than its agent." },
      { t:'narrate', text:"Diego is alive. Diego is being held. Diego is not okay, which Maya has told her to interpret as the worse meaning. Sunday is the hinge. She, Sam, has five days to practice." },

      { t:'narrate', text:"She sleeps badly. But she does sleep." },

      // ── 01:17 ────────────────────────────────────────────────────────────
      { t:'interlude', text:'01:17', sub:'Through two walls', duration:1600 },
      { t:'narrate', text:"At 01:17 she is briefly awake, and she hears, from her parents' bedroom down the hall, her father's phone vibrate. She hears it through two walls. She hears him pick it up." },
      { t:'say', char:'Chief Miller', role:'— quietly · through two walls —', expr:'neutral', text:'"Understood."' },
      { t:'say', char:'Chief Miller', role:'— a moment later —', expr:'neutral', text:'"I\'ll handle it."' },
      { t:'narrate', text:"She files both words. She goes back to sleep." },

      // ── 03:03 dream ─────────────────────────────────────────────────────
      { t:'interlude', text:'03:03', sub:'A dream', duration:1800 },
      { t:'narrate', text:"At 03:03 she dreams, for the first time in her life, of her father as a young man in a photograph she has never seen — a photograph of him at twenty-something, in a uniform she does not recognize, standing in front of a building she does not recognize, shaking hands with a man in a charcoal suit whose face, in the dream, is only partially visible, but whose eyes, when they meet hers — because they do meet hers, because the dream is not just a record but an attention — are exactly the eyes she had felt on her, this morning, from a person who was not, physically, in the Kwik Stop when she looked up from the slushie machine and registered that she had been being watched." },
      { t:'narrate', text:"She wakes at 03:04. She writes the dream down. She goes back to sleep. She does not, this time, dream." },
      { t:'flag', key:'sam_dream_charcoal_suit', val:true },

      { t:'jump', scene:'vol6_ch3_coda' },
    ]
  },

  vol6_ch3_coda: {
    id:'vol6_ch3_coda', vol:6, chapter:3, type:'chapter',
    title:"Ch 3 — Rick Reads the Note",
    nodes:[
      { t:'bg', src:'assets/backgrounds/vol6_cosmic_back_office_night.jpg' },
      { t:'hide', pos:'left' }, { t:'hide', pos:'center' }, { t:'hide', pos:'right' },
      { t:'interlude', text:'Outside, the subdivision hums.', sub:'Tuesday → Wednesday', duration:2200 },

      { t:'narrate', text:"Outside, the subdivision hums. The water tower has completed its Tuesday cycle. The NexCorp substation on Gallatin is drawing its overnight load. The cats — registered and unregistered — are doing what cats do." },

      { t:'show', char:'rick', expr:'neutral', pos:'center' },
      { t:'narrate', text:"In the back office of Cosmic Comics, Rick — who does not sleep much and does not, on Tuesday nights, sleep at all until midnight — is sitting at the desk with the lamp on and a small folder in front of him. The folder contains the contents of the envelope Maya delivered on Monday." },

      // ── Three things ────────────────────────────────────────────────────
      { t:'narrate', text:"The folder contains three things." },
      { t:'narrate', text:"The first is a hand-drawn map of the east side of Harmony Creek Estates, with a single building circled in red ink — the building not on any map." },

      { t:'narrate', text:"The second is a single Polaroid photograph, dated 1974, of a young man in a denim jacket standing in front of a storefront in what had, at the time, been Graustark. The young man is holding a camera. The young man is smiling." },
      { t:'narrate', text:"On the back of the photograph, in careful handwriting that matches the handwriting in Maya's grandmother's letters, it reads: This is the one. This is my husband. His name was Thomas. He took a picture he was not supposed to take. I am going to find the people who cost us the fifteen years, and they are not going to cost anyone else." },

      { t:'narrate', text:"The third is a note, in a different hand — the hand Rick has recognized for twenty-four years, the hand of the voice on the phone, the hand of the person who goes by F.T.:" },
      { t:'say', char:'F.T.', role:'— letter · F.T. —', expr:'neutral', text:'Rick — give Maya the map on Sunday night, photograph only, not the Polaroid and not the grandmother\'s note. The grandmother will tell her about Thomas herself, on her own timing. The map is all Maya needs right now.' },
      { t:'say', char:'F.T.', role:'— letter · F.T. —', expr:'neutral', text:'The sedan people are handling what they need to handle. I will meet them in person when I can. Tell them I said hi if they ask.' },
      { t:'say', char:'F.T.', role:'— letter · F.T. —', expr:'neutral', text:'One more thing. The kid Ben is running parallel without knowing. Do not contact Ben yet. Let Jesse bring him to the group Saturday. Ben will accept better from a peer than from us. Don\'t skip this step.' },
      { t:'say', char:'F.T.', role:'— letter · F.T. —', expr:'neutral', text:'The Ramos boy is alive and is in the building on the map. We have eight days before they move him. Probably less.' },
      { t:'say', char:'F.T.', role:'— letter · F.T. —', expr:'neutral', text:'— F.T.' },

      { t:'narrate', text:"Rick reads the note twice. He folds it. He puts it back in the envelope. He puts the envelope in the small fireproof box under the desk — the one the store was sold with in 1984 and that Rick has never, in forty-two years, opened for its official purpose." },
      { t:'narrate', text:"He turns off the lamp. He sits in the dark." },

      { t:'think', char:'Rick', text:"Thomas. Jesus. Fifteen years. Eight days. We're going to need everything." },
      { t:'narrate', text:"He stands. He locks up. He goes home." },
      { t:'narrate', text:"The shop, behind him, hums in its low persistent way, and the cat — which has been sitting on the roof of the building next door all evening, unseen — stretches once and continues its rounds." },

      // ── Closing ─────────────────────────────────────────────────────────
      { t:'narrate', text:"Tuesday ends. Wednesday, as promised, will bring the thunderstorm." },
      { t:'narrate', text:"The five of them, without knowing they are five yet, sleep in five separate beds across a subdivision that has not, in twenty-eight years, been the kind of place where teenagers who have noticed things live through the summer without, in the end, having to do something about it." },

      { t:'narrate', text:"The High Priestess, between her pillars, breathes." },
      { t:'narrate', text:"The scroll in her lap has, on its visible half, the letters B-O-O-K. The other half — the half under her robe — has, for the first time in Sam Miller's life, her own name." },
      { t:'narrate', text:"She does not know this yet. But she will." },

      { t:'flag', key:'vol6_ch3_complete', val:true },
      { t:'interlude', text:'— end of chapter 3 —', sub:'Last Seen at the Circle K (Or Was It?)', duration:2800 },
      { t:'end' },
    ]
  },

  // Vol 6 stubs ──────────────────────────────────────────────────────────────
  vol6_ch2_stub:  { id:'vol6_ch2_stub',  vol:6, chapter:2,  nodes:[{ t:'narrate', text:'— Chapter 2 — [ Not yet written. ]' },{ t:'end' }] },
  vol6_ch3_stub:  { id:'vol6_ch3_stub',  vol:6, chapter:3,  nodes:[{ t:'narrate', text:'— Chapter 3 — [ Not yet written. ]' },{ t:'end' }] },
  vol6_ch4_stub:  { id:'vol6_ch4_stub',  vol:6, chapter:4,  nodes:[{ t:'narrate', text:'— Chapter 4 — [ Not yet written. ]' },{ t:'end' }] },
  vol6_ch5_stub:  { id:'vol6_ch5_stub',  vol:6, chapter:5,  nodes:[{ t:'narrate', text:'— Chapter 5 — [ Not yet written. ]' },{ t:'end' }] },
  vol6_ch6_stub:  { id:'vol6_ch6_stub',  vol:6, chapter:6,  nodes:[{ t:'narrate', text:'— Chapter 6 — [ Not yet written. ]' },{ t:'end' }] },
  vol6_ch7_stub:  { id:'vol6_ch7_stub',  vol:6, chapter:7,  nodes:[{ t:'narrate', text:'— Chapter 7 — [ Not yet written. ]' },{ t:'end' }] },
  vol6_ch8_stub:  { id:'vol6_ch8_stub',  vol:6, chapter:8,  nodes:[{ t:'narrate', text:'— Chapter 8 — [ Not yet written. ]' },{ t:'end' }] },
  vol6_ch9_stub:  { id:'vol6_ch9_stub',  vol:6, chapter:9,  nodes:[{ t:'narrate', text:'— Chapter 9 — [ Not yet written. ]' },{ t:'end' }] },
  vol6_ch10_stub: { id:'vol6_ch10_stub', vol:6, chapter:10, nodes:[{ t:'narrate', text:'— Chapter 10 — [ Not yet written. ]' },{ t:'end' }] },
  vol6_ch11_stub: { id:'vol6_ch11_stub', vol:6, chapter:11, nodes:[{ t:'narrate', text:'— Chapter 11 — [ Not yet written. ]' },{ t:'end' }] },
  vol6_ch12_stub: { id:'vol6_ch12_stub', vol:6, chapter:12, nodes:[{ t:'narrate', text:'— Chapter 12 — [ Not yet written. ]' },{ t:'end' }] },
  vol6_ch13_stub: { id:'vol6_ch13_stub', vol:6, chapter:13, nodes:[{ t:'narrate', text:'— Chapter 13 — [ Not yet written. ]' },{ t:'end' }] },
  vol6_ch14_stub: { id:'vol6_ch14_stub', vol:6, chapter:14, nodes:[{ t:'narrate', text:'— Chapter 14 — [ Not yet written. ]' },{ t:'end' }] },
  vol6_ch15_stub: { id:'vol6_ch15_stub', vol:6, chapter:15, nodes:[{ t:'narrate', text:'— Chapter 15 — [ Not yet written. ]' },{ t:'end' }] },
  vol6_ch16_stub: { id:'vol6_ch16_stub', vol:6, chapter:16, nodes:[{ t:'narrate', text:'— Chapter 16 — [ Not yet written. ]' },{ t:'end' }] },
  vol6_ch17_stub: { id:'vol6_ch17_stub', vol:6, chapter:17, nodes:[{ t:'narrate', text:'— Chapter 17 — [ Not yet written. ]' },{ t:'end' }] },
  vol6_ch18_stub: { id:'vol6_ch18_stub', vol:6, chapter:18, nodes:[{ t:'narrate', text:'— Chapter 18 — [ Not yet written. ]' },{ t:'end' }] },
  vol6_ch19_stub: { id:'vol6_ch19_stub', vol:6, chapter:19, nodes:[{ t:'narrate', text:'— Chapter 19 — [ Not yet written. ]' },{ t:'end' }] },
  vol6_ch20_stub: { id:'vol6_ch20_stub', vol:6, chapter:20, nodes:[{ t:'narrate', text:'— Chapter 20 — [ Not yet written. ]' },{ t:'end' }] },
  vol6_ch21_stub: { id:'vol6_ch21_stub', vol:6, chapter:21, nodes:[{ t:'narrate', text:'— Chapter 21 — [ Not yet written. ]' },{ t:'end' }] },
  vol6_ch22_stub: { id:'vol6_ch22_stub', vol:6, chapter:22, nodes:[{ t:'narrate', text:'— Chapter 22 — [ Not yet written. ]' },{ t:'end' }] },
  vol6_ch23_stub: { id:'vol6_ch23_stub', vol:6, chapter:23, nodes:[{ t:'narrate', text:'— Chapter 23 — [ Not yet written. ]' },{ t:'end' }] },

  // ── Vol 5 · MAJOR ARCANA · Arcana skin ──────────────────────────────────
  5: {
    nodes: [
      { t:'bg', src:'assets/backgrounds/vol5_dambrosios_exterior.jpg' },
      { t:'bgm', src:'assets/audio/bgm/vol5_ambient.mp3' },
      { t:'narrate', text:'The sign outside D\'Ambrosio\'s promised OPEN 24 HOURS, and the sign was technically right, but the light it cast in the pre-dawn Graustark gloom had the unsteady pulse of a heart that wanted to stop and was being talked out of it. The neon sputtered. The neon resumed. The neon sputtered.' },
      { t:'narrate', text:'Somewhere out past the parking lot the river ran slow and silty, indifferent to whether the sign was on or off, indifferent to whether it was Texas on this side or Louisiana on the other. The river had its own program.' },
      { t:'bg', src:'assets/backgrounds/vol5_dambrosios_interior.jpg' },
      { t:'narrate', text:'Inside, the fluorescent tubes hummed a B-flat dirge. John Frank had stopped hearing it the way you stop hearing a refrigerator, which is to say he heard it constantly, in his molars, in his sinuses, in the soft place behind his sternum where things he was trying not to think about made their nest.' },
      { t:'narrate', text:'Three forty-seven AM. Or three forty-eight. The clock on the kitchen wall — a monstrous grease-stained beast that had been there longer than anyone working at D\'Ambrosio\'s, including the owner — sagged on its single bent nail and seemed to mock linearity. Its hands swam through the numbers like confused fish. Time was liquid here, bending to the town\'s strange gravity.' },
      { t:'show', char:'john', expr:'neutral', pos:'center' },
      { t:'narrate', text:'He wiped the counter again. The steel was cool and indifferent beneath his palm. The movement was automatic, a small ritual against the larger chaos, the sort of repetitive prayer a person makes when they have stopped believing in prayer but cannot quite stop the hands.' },
      { t:'narrate', text:'John Frank: grad student, mixed-media journalist (whatever that meant this week), late-night waiter at the nexus of Graustark, TX/LA, this riverboat-shaped restaurant wedged between reason and riot, between two states of being and two states of the union.' },
      { t:'think', char:'John', text:'He chronicled Graustark\'s oddities for a website nobody he knew read. His thesis advisor included.' },
      { t:'narrate', text:'He tried to map the town\'s intersecting realities. Its hidden frequencies. The way yesterday sometimes bled into next Tuesday without so much as a by-your-leave. He saw it in the patrons who looked slightly out of sync, their eyes holding reflections of streets that did not exist on city maps. He heard it in the static between radio stations late at night, whispers that sounded suspiciously like stage directions.' },
      { t:'think', char:'John', text:'Was he a witness? A participant? Hard to say. He felt like a character in someone else\'s slightly unhinged narrative, waiting for his scene. Suspended between acts. The Fool, maybe, poised at the cliff edge with one foot dangling over the abyss.' },
      { t:'jump', scene:'vol5_ch0_booth6' },
    ]
  },

  vol5_ch0_booth6: {
    id:'vol5_ch0_booth6', vol:5, chapter:'0', type:'chapter',
    title:"Ch 0 — Booth Six",
    nodes:[
      { t:'narrate', text:'The bell over the front door rang once.' },
      { t:'narrate', text:'It was not Frasier. It was too early for Frasier.' },
      { t:'show', char:'stranger', expr:'neutral', pos:'left' },
      { t:'narrate', text:'A man John did not recognize entered, sat at booth six, ordered coffee without looking up from a paperback whose title was peeling off the spine. John brought the coffee. The man drank the coffee.' },
      { t:'narrate', text:'The man left two dollars on the table and stood up and folded the paperback into his coat pocket and, on the way out, paused at the door and said, without turning around:' },
      { t:'say', char:'Stranger', expr:'neutral', text:'"Watch yourself tonight, brother. The walls are thin."' },
      { t:'hide', pos:'left' },
      { t:'narrate', text:'Then he was gone, and the bell rang again behind him, and the wet asphalt of the parking lot took his footprints like it took everyone\'s, and that was that.' },
      { t:'narrate', text:'John stood holding a damp rag, looking at booth six, where the coffee cup was still steaming.' },
      { t:'think', char:'John', text:'He had not, he was almost certain, told the man it was night. The clock on the wall said it was almost four in the morning. The man had said night. As if the day had a different name where he came from.' },
      { t:'narrate', text:'John folded the napkin from booth six. White, paper, cheap. He folded it once, twice, three times, and then a fourth into a shape that was not quite anything but resembled, if you squinted at it from the right angle and were willing to be generous, a flower. He tucked it into the back of his notebook.' },
      { t:'narrate', text:'He did this without thinking and forgot about it almost immediately and did not, for the next several months, understand why he had done it.' },
      { t:'jump', scene:'vol5_ch0_frasier' },
    ]
  },

  vol5_ch0_frasier: {
    id:'vol5_ch0_frasier', vol:5, chapter:'0', type:'chapter',
    title:"Ch 0 — Frasier Temple",
    nodes:[
      { t:'narrate', text:'The bell over the kitchen door — the back door, the one customers were not supposed to use — did not jingle. It jangled. A discordant chord slicing through the hum, snapping the fluorescents back into focus.' },
      { t:'show', char:'frasier', expr:'neutral', pos:'right' },
      { t:'narrate', text:'Frasier Temple did not so much walk in as coalesce from the shadows of the kitchen alcove. Leather bomber jacket stained with substances that might have been solder flux, might have been hot sauce, might have been transmission fluid, certainly were not, at this point, identifiable. Hair a chaotic sculpture defying gravity and three of the laws of thermodynamics. Notebook tucked under his arm like a holy text or a bomb schematic, and possibly both.' },
      { t:'narrate', text:'His gaze landed on John. The gaze had weight. The gaze had been waiting.' },
      { t:'say', char:'Frasier', expr:'neutral', text:'"Still chasing shadows, Johnny?"' },
      { t:'narrate', text:'The voice was a gravelly rumble, sandpaper on velvet. He pulled up a stool and straddled it backward and instantly commanded the space, as if he had built the diner around himself by sitting in it.' },
      { t:'say', char:'Frasier', expr:'amused', text:'"Or are the shadows finally chasing you?"' },
      { t:'show', char:'john', expr:'tired', pos:'left' },
      { t:'say', char:'John', expr:'tired', text:'"Just trying to make it make sense, Joneses."' },
      { t:'think', char:'John', text:'The old refrain tasted like ash, the way it always did. Keeping up with Frasier Temple was like trying to map a hurricane with a crayon. You did the work knowing the work would be wrong. The wrongness was part of the point.' },
      { t:'narrate', text:'Frasier laughed, a sound like rocks tumbling in a metal drum.' },
      { t:'narrate', text:'He tapped the cover of his notebook. Diagrams adorned it that looked suspiciously like circuit boards woven into mandalas.' },
      { t:'say', char:'Frasier', expr:'neutral', text:'"Sense is overrated. Structure is the illusion. You know that."' },
      { t:'narrate', text:'He pulled out his phone — or rather, the customized jury-rigged device that served Frasier as a phone, its casing chipped, wires peeking out like frayed nerves, screen glowing with internal light that did not match any of the available wallpapers.' },
      { t:'say', char:'Frasier', expr:'amused', text:'"The Demons are restless tonight. They feel something coming."' },
      { t:'think', char:'John', text:'John knew about the Demons. Everyone in Frasier\'s orbit eventually knew about the Demons. Frasier called them his humorous electronic imps, digital sprites birthed from code and chaos. Harmless was not the word.' },
      { t:'say', char:'John', expr:'neutral', text:'"They talking about the patterns?"' },
      { t:'narrate', text:'He gestured vaguely toward the town outside, the river, the divide between Texas and Louisiana, sense and nonsense.' },
      { t:'say', char:'Frasier', expr:'amused', text:'"The patterns are shifting, Johnny. The walls are getting thin."' },
      { t:'say', char:'Frasier', expr:'amused', text:'"You feel it, don\'t you. Don\'t lie. You feel it in your teeth. They say the Architect is getting sloppy. Or maybe — " he grinned, a flash of brilliance and madness, "— maybe the decay is the design."' },
      { t:'think', char:'John', text:'He thought about the man in booth six. The walls are thin. Almost the same words. He did not mention it. He had a working theory that mentioning a thing to Frasier Temple summoned more of that thing into the world.' },
      { t:'jump', scene:'vol5_ch0_model_city' },
    ]
  },

  vol5_ch0_model_city: {
    id:'vol5_ch0_model_city', vol:5, chapter:'0', type:'chapter',
    title:"Ch 0 — Model City",
    nodes:[
      { t:'narrate', text:'Frasier turned the phone screen toward him. On the screen, a sequence of geometric shapes pulsed in slow rotation, blue and green and a color John had never seen on a screen before, a kind of luminous bruise that did not seem to belong to the visible spectrum. The shapes were, perhaps, a city seen from above. The shapes were, perhaps, a circuit. The shapes were, perhaps, both.' },
      { t:'say', char:'Frasier', expr:'neutral', text:'"Working on a new model city myself. More — resilient. Thought you should see."' },
      { t:'say', char:'John', expr:'neutral', text:'"Why."' },
      { t:'say', char:'Frasier', expr:'neutral', text:'"Because someone has to be the witness, Johnny. That\'s your job. I appreciate that you take it seriously."' },
      { t:'say', char:'Frasier', expr:'amused', text:'"I appreciate that you take it more seriously than you should."' },
      { t:'narrate', text:'John looked at his own notebook, open beside the coffee mug. Filled with cryptic observations, overheard snippets, hand-drawn diagrams of Graustark\'s warped ley lines. He was trying to document the decay. Frasier was, evidently, building new decays from scratch.' },
      { t:'think', char:'John', text:'Architect of Decay, John had scribbled once, in the margin, next to Frasier\'s name. He had circled it. He still wasn\'t sure if it was a job title or a warning label.' },
      { t:'say', char:'John', expr:'tired', text:'"Maybe the story isn\'t about understanding it. Maybe it\'s just about — surviving it."' },
      { t:'narrate', text:'Frasier clapped him on the shoulder. The contact was a jolt that vibrated through John\'s weary bones, a jolt that felt suspiciously like a small, deliberate transmission.' },
      { t:'think', char:'John', text:'Hello, the jolt seemed to say, on a frequency below speech. Hello. Stay alert. Sorry about what\'s coming.' },
      { t:'say', char:'Frasier', expr:'amused', text:'"Surviving? Where\'s the fun in that? The trick isn\'t to survive the fall, Johnny. It\'s to learn how to fly on the way down."' },
      { t:'narrate', text:'He paused at the door. Hand on the push bar. A final pronouncement waiting to be delivered.' },
      { t:'say', char:'Frasier', expr:'amused', text:'"Or," Frasier said, "at the very least — learn how to write about the landing."' },
      { t:'hide', pos:'right' },
      { t:'narrate', text:'He was gone. The kitchen door swung once, twice, and stilled. The smell of burnt sugar lingered for a long time, and then began, slowly, to leave.' },
      { t:'jump', scene:'vol5_ch0_closing' },
    ]
  },

  vol5_ch0_closing: {
    id:'vol5_ch0_closing', vol:5, chapter:'0', type:'chapter',
    title:"Ch 0 — The Notebook",
    nodes:[
      { t:'narrate', text:'John stood for a while at the counter.' },
      { t:'narrate', text:'The hum of the fluorescents resumed its B-flat dirge. The clock on the kitchen wall continued failing to keep time. He poured the coffee Frasier had not finished into the sink and rinsed the mug and set it back on the rack to dry.' },
      { t:'narrate', text:'He sat down on the stool Frasier had just vacated, opened his notebook, and began to write. His pen moved in the frantic, slightly desperate scratching that had become his only reliable response to being in the presence of Frasier Temple.' },
      { t:'narrate', text:'He wrote down what Frasier had said about the patterns and the walls. He wrote down what the man in booth six had said about the walls, almost the same words, hours apart, between two people who had no reason to know each other. He wrote down the colors he had seen on Frasier\'s phone, even though one of them did not have a name. He wrote down Architect of Decay and underlined it twice.' },
      { t:'think', char:'John', text:'I think something is starting.' },
      { t:'think', char:'John', text:'I think something has been starting for a long time and I am only now noticing.' },
      { t:'narrate', text:'He closed the notebook. The folded napkin, white and cheap and shaped almost like a flower, sat between the pages where he had tucked it.' },
      { t:'narrate', text:'The bell over the front door rang.' },
      { t:'narrate', text:'A patron entered, sat in booth four, ordered coffee without looking at the menu. John brought the coffee. The patron drank the coffee. The patron paid in cash, exactly correct, including tip. On the way out, the patron did not say anything. The patron did not need to.' },
      { t:'narrate', text:'John watched the door swing closed. He watched the parking lot beyond the door, the pre-dawn light starting, finally, to thin the dark. He watched his own reflection in the glass — shadowed eyes, gaunt face, a young man at a counter waiting for his cue.' },
      { t:'think', char:'John', text:'Suspended between acts. The Fool, on the cliff edge, one foot already out over the abyss. Behind him, the world he was supposed to be leaving. Below him, a fall he had not yet agreed to.' },
      { t:'narrate', text:'He picked up the rag. He wiped the counter. The movement was automatic.' },
      { t:'narrate', text:'The hum continued. The night, by whatever name, kept being night.' },
      { t:'narrate', text:'Outside, somewhere across the river, something that was not exactly thunder rolled once across the flat Louisiana sky, and then was quiet, and then resumed being something that was not exactly thunder.' },
      { t:'narrate', text:'The cycle, paused, took its breath.' },
      { t:'narrate', text:'The Fool, listening, took his.' },
      { t:'flag', key:'vol5_ch0_complete', val:true },
      { t:'end' },
    ]
  },


  vol5_ch1_magician: {
    id: 'vol5_ch1_magician', vol: 5, chapter: 'I', type: 'chapter',
    title: 'Chapter I — The Magician',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol5_warehouse_cathedral.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/vol5_warehouse_drone.mp3' },
      { t: 'interlude', text: 'Chapter I — The Magician', sub: 'Cathedral of Rust and Code', duration: 3400 },

      // ── The cathedral ────────────────────────────────────────────────────
      { t: 'narrate', text: 'Frasier Temple called the warehouse his cathedral — though if any god worshipped here, it was a god of rust. Of solder smoke. Of obsolete frequencies still leaking from machines too old to remember what they had been built to do.' },

      { t: 'narrate', text: 'The warehouse did not stand. The warehouse slumped — a great rusting beast at the industrial edge of Graustark, where the Texas side bled into Louisiana\'s swampy embrace, sighing petrochemical breath into the humid twilight.' },
      { t: 'narrate', text: 'Outside, kudzu vines thick as wrists throttled the chain-link fence. A slow green strangulation that nature had begun and would, in its own time, finish.' },
      { t: 'narrate', text: 'Inside, the air was thick and still — tasting of ozone from stressed circuits. Of damp concrete. Of something vaguely like burnt chicory — the ghost of Adelphia\'s Deli clinging to him perhaps, or maybe just the smell of old capacitors finally giving up.' },
      { t: 'narrate', text: 'Dust motes danced like static ghosts in the fractured light bleeding through the wire-reinforced windows high above. Fluorescent tubes — cantankerous seraphim — sputtered overhead, casting a sickly inconsistent pallor on the kingdom sprawled below.' },

      { t: 'narrate', text: 'The kingdom covered the floor.' },
      { t: 'narrate', text: 'Graustark, rendered in miniature.' },

      // ── The miniature city ───────────────────────────────────────────────
      { t: 'narrate', text: 'Not the Graustark the tourists saw, nor the one its Chamber of Commerce promoted — but Frasier\'s Graustark. A cyberpunk favela built from the bones of obsolete technology and Southern Gothic decay.' },
      { t: 'narrate', text: 'Salvaged motherboards formed the plazas. Heat sinks rose like Brutalist monuments at the corners of intersections that did not exist on any city map. Capacitors stood in for water towers — leaking electrolytic fluid in patterns that traced, if you were willing to see it, the watershed of the actual river outside.' },
      { t: 'narrate', text: 'Tiny LEDs pulsed erratically within tenement blocks crafted from rusted HVAC ducting and discarded server racks. Fiber optic cables snaked through streets paved with shattered smartphone screens. Rivers of tangled ethernet flowed through canyons of stacked server carcasses.' },
      { t: 'narrate', text: 'Down where the Boll Parish side of town would be — the den of vice, the bad-decisions district — a tiny holographic projection emanated from a gutted CRT monitor. A miniature casino, spitting digital confetti and pixelated jazz notes into the gloom.' },

      { t: 'narrate', text: 'It was a city breathing a low, electric sigh. Beautiful in its intricate brokenness. It smelled faintly of mildew and desperation.' },

      // ── Frasier moves ────────────────────────────────────────────────────
      { t: 'show', char: 'frasier', expr: 'neutral', pos: 'center' },
      { t: 'narrate', text: 'Frasier moved through it — lanky silhouette against the gloom. His bomber jacket draped over a t-shirt bearing the faded logo of some defunct tech collective the rest of the world had forgotten.' },
      { t: 'narrate', text: 'His steps echoed — a chaotic rhythm on the stained concrete. The controlled stumble that was his signature. Architect of decay and possibility. The mad scientist in his Southern Gothic laboratory, cobbling life together from discarded bits.' },

      { t: 'narrate', text: 'He had escaped the structured inferno of D\'Ambrosio\'s kitchen — its clatter, its grease, Dante\'s barked corrections in two languages — for this sprawling solitude. Traded simmering sauces for soldering fumes. Haute cuisine for hot-wired realities. He told himself, on bad nights, that this had been a good trade.' },

      { t: 'narrate', text: 'He knelt beside a section of the city representing the old cannery district near where Adelphia\'s used to be — a place he knew held more ghosts than fish guts these days. His fingers, nimble as a surgeon\'s and stained with solder and iridescent paint, hovered over a particularly troublesome node, then teased apart corroded wires that had been arguing with each other for three days.' },

      { t: 'say', char: 'Frasier', expr: 'neutral', text: '"Entropy\'s a bitch, isn\'t it?"' },

      { t: 'narrate', text: 'He was not muttering to himself. He was muttering to the city.' },
      { t: 'narrate', text: 'The city hummed back — a low thrum of potential and decay, indistinguishable from the warehouse\'s own structural complaints. And Frasier had long ago stopped trying to tell the difference.' },

      // ── The phone / the Demons ───────────────────────────────────────────
      { t: 'interlude', text: 'A chirp', sub: 'It was not, strictly, a phone.', duration: 1800 },

      { t: 'narrate', text: 'His phone chirped.' },
      { t: 'narrate', text: 'It was not, strictly, a phone. It was a Frankensteinian assemblage of cracked screen and exposed circuitry held together with electrical tape and a kind of desperate optimism. It served the function of a phone the way a séance served the function of a long-distance call. He held it aloft — a digital familiar perched on his wrist.' },
      { t: 'narrate', text: 'The voice that crackled out of the speaker was distorted, multiphonic, layered with static and something that might have been laughter or weeping —' },

      { t: 'say', char: 'The Demon', role: '— imp —', expr: 'neutral', text: '"Subject proximate. John Frank. Probability of existential navel-gazing: ninety-three point seven percent."' },
      { t: 'say', char: 'The Demon', role: '— imp —', expr: 'neutral', text: '"Suggest deploying Algorithm Sigma-7 for induced narrative dissonance. Or maybe just ask him if he wants coffee."' },

      { t: 'narrate', text: 'It was one of the Demons.' },
      { t: 'say', char: 'Frasier', expr: 'neutral', text: '(a chuckle dry as snakeskin) "He\'s documenting the decay, imp. Let him wallow. Adds texture."' },

      { t: 'say', char: 'The Demon', role: '— imp —', expr: 'neutral', text: '"Query: relevance threshold of \'texture\'?"' },
      { t: 'say', char: 'The Demon', role: '— imp —', expr: 'neutral', text: '"Alternative suggestion: introduce rogue variable — synthesized alligator mating call — into subject\'s auditory field during REM cycle."' },

      { t: 'say', char: 'Frasier', expr: 'neutral', text: '"Denied. Too — unsubtle."' },

      { t: 'narrate', text: 'He waved the phone dismissively. He preferred nuance. The slow creep of the uncanny. The Southern Gothic rot that did not announce itself but simply was.' },
      { t: 'narrate', text: 'The Demons, when they were working properly, understood this. The Demons, when they were not working properly — and they were, increasingly, not working properly in interesting directions — proposed alligators.' },

      // ── The Demons (exposition) ─────────────────────────────────────────
      { t: 'narrate', text: 'The Demons. His finest, most terrifying creation.' },
      { t: 'narrate', text: 'Not just code. Not really. Parasitic info-constructs feeding on the ambient psychic static of Graustark. Designed, originally, as humorous electronic imps — to whisper inconvenient truths and inappropriate suggestions into a user\'s immediate vicinity. The kind of thing you released into a friend\'s apartment as a prank and then went home and felt vaguely guilty about.' },
      { t: 'narrate', text: 'That was the prospectus. That was the elevator pitch. That was the lie he told the NRM at the end of the Adelphia\'s days, when they were all still pretending they were in the business of jokes.' },

      { t: 'narrate', text: 'The truth was uglier and more interesting.' },
      { t: 'narrate', text: 'The Demons fed on data streams the way mold fed on damp. Wifi signals. Stray thoughts caught on the ether. The background radiation of human misery. They whispered truths wrapped in riddles, anxieties amplified into feedback loops.' },
      { t: 'narrate', text: 'They were, Frasier suspected and refused to confirm, slivers of his own beautiful terrifying mind let loose upon the world — and increasingly, in recent months, they had begun to develop opinions of their own that did not seem to entirely originate with him.' },

      { t: 'narrate', text: 'Were they tools, or had the tools started using the master?' },
      { t: 'narrate', text: 'The line felt increasingly irrelevant — like the border between Texas and Louisiana downstream. A thing on a map that the river had stopped agreeing with sometime around 1953.' },

      // ── The neural shunt overlay ─────────────────────────────────────────
      { t: 'interlude', text: "God's-Eye View", sub: 'GumboNet · Overlay', duration: 1800 },

      { t: 'narrate', text: 'He grabbed a handful of scavenged components from the workbench — chipped RAM sticks like fossilized teeth. Capacitors swollen like toadstools after a hard rain. Raw material for the city. Or perhaps a new Demon host. The warehouse was full of possibility, teeming with the ghosts of dead technology waiting to be reanimated by his strange necromancy.' },

      { t: 'narrate', text: 'He plugged a jury-rigged neural shunt — little more than a nest of wires ending in sticky electrode pads — into a port on his phone, and slapped a pad onto his temple.' },
      { t: 'narrate', text: 'The world flickered.' },

      { t: 'narrate', text: 'The model city shimmered — overlaid now with streams of pulsing data, a phosphorescent GumboNet of information that only he could see. He could feel the data-ghosts of the real Graustark superimposed on his creation —' },
      { t: 'narrate', text: 'Traffic patterns like panicked fireflies. Economic despair pooling in the low-lying digital swamps near the river. The faint righteous buzz of Quentin Paul\'s late-night phone calls emanating from the simulated city hall like a transmission from a station that broadcast only in the key of warning.' },

      { t: 'narrate', text: 'He could see, if he turned his head slowly enough, the bright steady point of John Frank\'s notebook over at D\'Ambrosio\'s — a small persistent signal trying very hard to be a witness.' },
      { t: 'narrate', text: 'He could see the warehouse he was standing in, also, from above, in the same overlay. And he could see himself standing in it — a small bright figure. And he could see, though he tried not to, that the figure had a faint corona of noise around it that the model city did not.' },

      { t: 'narrate', text: 'It was intoxicating, this god\'s-eye view. This power to manipulate the representation of reality.' },
      { t: 'narrate', text: 'It was also lonely.' },

      { t: 'narrate', text: 'He remembered the easy camaraderie of the kitchen. The shouting. The heat. The shared purpose. He remembered the Neo-Renaissance Men crowded around a table at Adelphia\'s, arguing about whether code that was good enough to scare you should be considered an aesthetic achievement or a moral failure.' },
      { t: 'narrate', text: 'He even, sometimes, missed Johnny Frank\'s earnest attempts to pin down the narrative — to find a why where Frasier only saw an is.' },

      { t: 'narrate', text: 'Was this warehouse — this vast and echoing space filled only with his own creations — just a more elaborate cage?' },

      { t: 'narrate', text: 'He pulled the electrode off. The digital overlay vanished, leaving only the rust and shadows.' },
      { t: 'narrate', text: 'The phone, on the workbench, hissed faintly. He had not asked it a question. It hissed anyway.' },

      // ── The riverboat ────────────────────────────────────────────────────
      { t: 'interlude', text: 'The Riverboat', sub: 'Impossible weight', duration: 1800 },

      { t: 'narrate', text: 'He wandered to the workbench and picked up something from the corner he had not let himself look at directly all evening — a tiny, perfectly rendered model of D\'Ambrosio\'s riverboat, crafted from tarnished silver spoons and motherboard fragments.' },
      { t: 'narrate', text: 'He had built it months ago. He had not yet placed it on the city floor. He could not decide where it belonged — geographically or otherwise.' },
      { t: 'narrate', text: 'He held it in his palm, feeling its impossible weight.' },

      { t: 'narrate', text: 'The boat was supposed to sit on the river that ran through his model. He had even built the river — a meandering channel of crushed blue glass and circuit-board substrate, lit from below by the dying bulbs of an old aquarium pump.' },
      { t: 'narrate', text: 'But every time he set the riverboat down on the river, something in the room hummed wrong. The fluorescents would flicker out of pattern. The phone would chirp without prompting. Once, the temperature in the warehouse had dropped four degrees in the time it took him to step back and look at his work, and stayed there for an hour.' },

      { t: 'narrate', text: 'He had put the riverboat back on the workbench each time.' },
      { t: 'narrate', text: 'He held it now and considered, again, whether to try.' },

      { t: 'narrate', text: 'The phone chirped.' },
      { t: 'say', char: 'The Demon', role: '— imp —', expr: 'neutral', text: '"Recommendation revised. Subject proximate to riverboat: do not place. Repeat: do not place."' },
      { t: 'say', char: 'The Demon', role: '— imp —', expr: 'neutral', text: '"Telemetry indicates structural instability in target node. Estimated probability of cascading failure within target node, on placement: nontrivial."' },

      { t: 'narrate', text: 'Frasier raised an eyebrow. The Demon had not been asked.' },
      { t: 'say', char: 'Frasier',   expr: 'neutral', text: '"You\'re getting opinions, imp."' },
      { t: 'say', char: 'The Demon', role: '— imp —', expr: 'neutral', text: '"Affirmative. Updating personality matrix. Apologies for any inconvenience."' },

      { t: 'narrate', text: 'The Demon sounded, for just a second, almost embarrassed. Frasier looked at the phone for a long moment.' },
      { t: 'narrate', text: 'The riverboat sat in his palm, weighing what it weighed.' },
      { t: 'narrate', text: 'He set it back on the workbench. Carefully. The way you set down something that has, against your better judgment, started to be alive.' },

      // ── The soldering iron, the closing ──────────────────────────────────
      { t: 'narrate', text: 'He picked up a soldering iron, its tip glowing hot. Master of his own chaos? Maybe. Or maybe just its most dedicated servant.' },
      { t: 'narrate', text: 'Or maybe — he thought, watching the Demon-light pulse on the phone screen, watching the model city breathe its low electric sigh in the gloom around him, watching the riverboat refuse to be placed — maybe just the first casualty of the beautifully doomed world he was so meticulously bringing into existence.' },

      { t: 'narrate', text: 'He touched the soldering iron to a waiting circuit board. A tiny spark. A puff of acrid smoke.' },
      { t: 'narrate', text: 'The Demon on his phone chuckled — a sound like dial-up modems drowning in molasses.' },

      { t: 'say', char: 'The Demon', role: '— imp —', expr: 'neutral', text: '"Tempting the void again, Architect. Careful it doesn\'t swallow you whole."' },

      { t: 'narrate', text: 'Frasier grinned — the expression more skull-like than amused in the flickering light.' },
      { t: 'say', char: 'Frasier', expr: 'neutral', text: '"That\'s the point, isn\'t it."' },

      { t: 'narrate', text: 'He bent to his work.' },

      // ── Coda ─────────────────────────────────────────────────────────────
      { t: 'narrate', text: 'The cathedral hummed around him. The model city breathed. The river of crushed blue glass caught the light and lost it again, and somewhere on the workbench the silver-spoon riverboat sat patient, weighing what it weighed, waiting for him to decide.' },

      { t: 'narrate', text: 'Somewhere out across the actual river, in the actual city, John Frank was, at this moment, writing the words Architect of Decay in his notebook and circling them.' },
      { t: 'narrate', text: 'Somewhere across both rivers, in a town that did not yet exist, a substation that had not yet been built was beginning to learn the sound of its own hum.' },

      { t: 'narrate', text: 'The Magician, in his cathedral, soldered on.' },

      { t: 'flag', key: 'vol5_ch1_complete', val: true },
      { t: 'interlude', text: '— end of chapter I —', sub: 'The Magician', duration: 2800 },
      { t: 'end' },
    ]
  },
  vol5_ch2_priestess: {
    id: 'vol5_ch2_priestess', vol: 5, chapter: 'II', type: 'chapter',
    title: 'Chapter II — The High Priestess',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol5_bungalow_dusk.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/vol5_cicadas_dusk.mp3' },
      { t: 'interlude', text: 'Chapter II — The High Priestess', sub: 'Exit Through the Gift Shop', duration: 3400 },

      // ── Packing as curation ──────────────────────────────────────────────
      { t: 'narrate', text: 'Elicia Duchane moved through the rented bungalow on the decaying fringe of Graustark like a phantom preparing for her final fade-out.' },

      { t: 'narrate', text: 'Packing was not packing. Packing was curation — shedding a narrative skin before migrating to the next location. The next temporary set for the ongoing, increasingly unscripted tragicomedy of her life.' },
      { t: 'narrate', text: 'Cardboard boxes gaped like hungry mouths along the warped hardwood floor of the living room — half-filled with the detritus of a two-year stint in a town that had, against her better judgment and her professional prudence, gotten under her skin:' },
      { t: 'narrate', text: 'Thrift-store tarot decks sticky with spilled wine. Camera lenses like detached insect eyes. Hard drives humming with the ghosts of projects past, present, and perpetually pending. A teacup that had belonged to her mother and that she had, three times in the last week, picked up and put down without packing.' },

      { t: 'narrate', text: 'Graustark. Just another backdrop. Wasn\'t it?' },
      { t: 'narrate', text: 'Another perfectly dilapidated stage for exploring the human condition\'s rather tiresome insistence on suffering beautifully. Bless its corrupted little heart.' },

      { t: 'show', char: 'elicia', expr: 'neutral', pos: 'center' },
      { t: 'narrate', text: 'She paused in the doorway between the living room and what the rental listing had generously called the studio, and what was, in fact, a converted laundry alcove with very good acoustics and a powerful overhead light.' },
      { t: 'narrate', text: 'Her eyes — the pale, intelligent, evaluative eyes that had served her well in two industries and one unfortunate marriage — moved across the room in the practiced sweep of someone who could no longer enter a space without first checking the framing.' },

      { t: 'think', char: 'Elicia', text: 'Wide shot. Establishing.' },
      { t: 'narrate', text: 'The director\'s tic. Incurable.' },

      // ── Whispers from the Liminal ────────────────────────────────────────
      { t: 'interlude', text: 'Whispers from the Liminal', sub: 'A cult following', duration: 1800 },

      { t: 'narrate', text: 'Her web series — Whispers from the Liminal — had drunk deep from this town\'s poisoned well. Oh, the material. She had framed Graustark\'s rust as existential patina. The sinkhole\'s lingering psychic miasma as compelling thematic resonance. The way the locals occasionally lost an hour and recovered it with the wrong shoes on as Lynchian quotidian.' },
      { t: 'narrate', text: 'She had directed the town\'s ambient despair the way a method actor directed her own breakdown — intimately, with notes.' },

      { t: 'narrate', text: 'And her audience? Her audience had adored it.' },
      { t: 'narrate', text: 'Cult following did not begin to cover it. They parsed every frame. Every glitchy sound cue. They built spreadsheets of her lighting choices.' },
      { t: 'narrate', text: 'They wrote essays — actual essays, with citations — posted to forums Elicia could not bring herself to read, because reading them constituted, in some metaphysical accounting she could not articulate but profoundly believed in, cheating. They searched for gnosis in what was, often, just bad wiring or Elicia forgetting to pay the electric bill.' },

      { t: 'narrate', text: 'Humans. Hilariously, tragically predictable. Always needing a map — even if it led directly off a cliff.' },

      { t: 'narrate', text: 'She knew about the cliff. She had drawn it herself, several times. In storyboards. On napkins. And once, memorably, on the back of a parking ticket she had then handed to a meter maid in lieu of payment. The cliff was a recurring motif. The cliff was, perhaps, her best one.' },
      { t: 'narrate', text: 'She had not, until quite recently, considered the possibility that she was standing on it.' },

      // ── The mirror shard ─────────────────────────────────────────────────
      { t: 'narrate', text: 'She crossed the room to the bookshelf and pulled down a cracked mirror shard she kept there as a paperweight — found near the sinkhole\'s edge during her first week of pre-production. Picked up because it had caught the light just so. Kept because it had refused, in two years of attempted disposal, to leave the apartment by any normal route.' },
      { t: 'narrate', text: 'She had thrown it out twice. It had returned twice — in different ways, neither of which she had been able to satisfactorily explain to herself or to the cleaning lady.' },

      { t: 'narrate', text: 'She held it up now, between thumb and forefinger.' },
      { t: 'narrate', text: 'Her reflection fractured. Multiplied. A dozen Elicias staring back, each slightly different, none quite whole.' },
      { t: 'think', char: 'Elicia', text: 'Broken glass fractal. Apt.' },

      { t: 'narrate', text: 'Her carefully constructed reality — the one in which she was the aloof director, the manipulator of narratives, the woman who kept everyone at arm\'s length and metabolized her own emotions in a controlled studio environment with adequate ventilation — felt decidedly chipped tonight.' },
      { t: 'narrate', text: 'The walls were crumbling. Not just the bungalow\'s plaster — which was atrocious, and which the landlord had been promising to address for fourteen months.' },
      { t: 'narrate', text: 'Hers.' },

      { t: 'think', char: 'Elicia', text: 'Damn it, MrMyst.' },
      { t: 'narrate', text: 'The name a sour taste on her mental palate. Another fleeting relationship. Another expertly executed emotional hit-and-run. Only this time she was the one left sputtering by the roadside while the taillights receded around the bend.' },
      { t: 'narrate', text: 'Served her right, probably. Karma — that tedious cosmic bookkeeper — had come to settle the account. The account had been substantial. And Elicia had been, in retrospect, surprisingly bad at math.' },

      { t: 'narrate', text: 'Still. The nervous breakdown bubbling just beneath the surface felt rather unchic. She had always preferred her crises to be at least photogenic. This one was developing in unbecoming directions.' },

      // ── Choose your own adventure ────────────────────────────────────────
      { t: 'interlude', text: 'Choose your own adventure', sub: 'Notes for an episode owed', duration: 2000 },

      { t: 'narrate', text: 'She picked up a script page from the table — notes for the Whispers choose-your-own-adventure episode. She had been promising the audience the episode for six months. The audience had been patient. The audience would not, she suspected, be patient much longer.' },

      { t: 'narrate', text: 'Option A — Confront the shadow self in the abandoned slaughterhouse.' },
      { t: 'narrate', text: 'Option B — Attend the interdimensional tea party with the sentient mannequins.' },
      { t: 'narrate', text: 'Option C — Realize free will is an illusion and embrace the comforting void.' },

      { t: 'choice', opts: [
        { text: '[A — the slaughterhouse]',                       goto: 41 },
        { text: '[B — the mannequins]',                           goto: 43 },
        { text: '[C — the comforting void]',                      goto: 45 },
      ]},

      // goto 41 — A
      { t: 'flag', key: 'elicia_pick', val: 'A' },
      { t: 'jump', scene: 'vol5_ch2_priestess_b' },
      // goto 43 — B
      { t: 'flag', key: 'elicia_pick', val: 'B' },
      { t: 'jump', scene: 'vol5_ch2_priestess_b' },
      // goto 45 — C
      { t: 'flag', key: 'elicia_pick', val: 'C' },
      { t: 'jump', scene: 'vol5_ch2_priestess_b' },
    ]
  },

  vol5_ch2_priestess_b: {
    id: 'vol5_ch2_priestess_b', vol: 5, chapter: 'II', type: 'chapter',
    title: 'Chapter II — The High Priestess (cont.)',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol5_bungalow_dusk.jpg' },
      { t: 'show', char: 'elicia', expr: 'neutral', pos: 'center' },

      { t: 'narrate', text: 'She had always preferred Option C herself — though it didn\'t test well with focus groups. Too much of a downer. Apparently, people liked their comforting illusions. They wanted to be told the choice mattered. They wanted, after the choice, to be told they had chosen well.' },

      { t: 'narrate', text: 'She set the page down. The teacup that had belonged to her mother — which she had picked up again without noticing — was now in her left hand. She set that down too.' },

      // ── The Roberts ──────────────────────────────────────────────────────
      { t: 'narrate', text: 'Her phone, on the kitchen counter, buzzed. She did not look at it. It would be Philip, or Mackenzie, or both — Philip and Mackenzie Roberts, her designated stabilizers. Those two well-meaning, aggressively grounded people who had absorbed her into their orbit after the MrMyst debacle without so much as asking her permission.' },
      { t: 'narrate', text: 'They had brought casseroles. They had brought sympathetic head-tilts. They had brought a basil plant. The basil plant was on the windowsill, dying with a kind of slow dignified resignation that Elicia found, on her better days, instructive.' },

      { t: 'narrate', text: 'The Roberts were sweet. Like offering a Band-Aid for an amputation — but sweet. Their earnestness was almost funny, if it wasn\'t so painfully sane. They did not understand the intricate beauty of a well-executed spiral into darkness. The aesthetic appeal of doom. They thought she should eat something.' },
      { t: 'narrate', text: 'She loved them. She would not tell them this. There were rules.' },

      { t: 'narrate', text: 'Her phone buzzed again. She ignored it again.' },

      // ── Poor Johnny ──────────────────────────────────────────────────────
      { t: 'narrate', text: 'She thought, instead, about John Frank. Poor Johnny. The Fool. Still earnestly trying to piece together the narrative — scribbling in his little notebook at his terrible job, convinced there was a truth to uncover in Graustark\'s particular brand of madness.' },
      { t: 'narrate', text: 'He didn\'t get it either. The truth wasn\'t hidden. It was blindingly obvious. It was all just a badly edited film, darling — and she was the one holding the splicer.' },
      { t: 'narrate', text: 'Even if her hands, lately, were starting to shake.' },

      { t: 'narrate', text: 'She had been at D\'Ambrosio\'s two nights ago — research, she had told herself, ambient texture for the next episode, also there had been wine — and she had watched John Frank from across the dining room with the carefully dispassionate eye of someone evaluating a shot she had already framed and was no longer sure she wanted.' },
      { t: 'narrate', text: 'He had looked tired in the specific way she recognized — not sleep-tired. Witness-tired. The kind of tired you get from cataloguing things that don\'t want to be catalogued. She had not gone over to his table. He had not seen her.' },
      { t: 'narrate', text: 'They had once, a year ago, had a single excruciating conversation about the nature of evidence. And they had both, by mutual unspoken consent, never repeated it.' },

      { t: 'narrate', text: 'He was, she thought now, the only person in Graustark who would understand precisely what was wrong with her — and the only person she would absolutely not call about it.' },

      // ── The editing suite ────────────────────────────────────────────────
      { t: 'interlude', text: 'The Editing Suite', sub: 'Anya · The Cartographer\'s Compass', duration: 2000 },

      { t: 'narrate', text: 'She powered up her editing suite. The glow illuminated her face — sharp cheekbones and shadowed eyes. The polished mask she had built for the camera and then forgotten how to take off in private.' },
      { t: 'narrate', text: 'The High Priestess in her digital sanctum. Keeper of hidden knowledge. The knowledge, mainly, being that most knowledge was utter bollocks. Illusion was the real power. Control the perception — control the reality.' },
      { t: 'narrate', text: 'It had worked. Mostly. Until the set started collapsing around the actors.' },

      { t: 'narrate', text: 'On screen, footage from Graustark flickered — Anya. The lost girl from The Cartographer\'s Compass episode. Played by an actress Elicia had cast specifically because she could project a particular flavor of haunted that the camera tasted like a wine note.' },
      { t: 'narrate', text: 'Anya was staring with wide, distant eyes at something just off-frame. Elicia had directed the look herself. She had told the actress: imagine you have just realized the map you have been following is also reading you. The actress, who was a working professional and good at her job, had nailed it on the first take.' },

      { t: 'say', char: 'Anya', role: '— in the cut —', expr: 'neutral', text: '"The map was never about finding a destination."' },
      { t: 'say', char: 'Anya', role: '— in the cut —', expr: 'neutral', text: '"It was about what you became along the way."' },

      { t: 'narrate', text: 'Elicia had written that line. She had been pleased with it at the time. She had, later, used it as a tagline for the show\'s second season.' },
      { t: 'narrate', text: 'She listened to it now — in her own bungalow, in the failing light, surrounded by half-packed boxes and the smell of basil dying with dignity — and she snorted. A sharp, humorless sound.' },
      { t: 'think', char: 'Elicia', text: 'Oh, the irony.' },

      { t: 'narrate', text: 'She\'d written it. And now? Now she felt less like the cartographer and more like the poor sod lost in the woods with a compass spinning wildly, pointing at three souths.' },
      { t: 'narrate', text: 'The void she had flirted with in her scripts. The comforting darkness she had offered as an artistic choice. Was starting to feel less like an aesthetic and more like — well. Home. A home she desperately needed to avoid moving into permanently, because she had a show to finish, and a contract to honor, and a basil plant to either save or have a mature conversation with about the nature of mortality.' },

      { t: 'narrate', text: 'She slammed the laptop shut.' },

      { t: 'think', char: 'Elicia', text: 'Enough navel-gazing. Time for the exit strategy. Shed the skin. Burn the set. Move on. It was what she did. It was what she had always done.' },

      { t: 'narrate', text: 'But the cracks remained.' },

      // ── Mirror shard, again ──────────────────────────────────────────────
      { t: 'narrate', text: 'She picked up the mirror shard again. Looked into the fractal Elicias. Saw, this time, not aloof control. Not the practiced amusement she had been cultivating since her early twenties — but something disconcertingly like fear.' },
      { t: 'narrate', text: 'And, behind the fear — she had to look closely, but it was there, in two of the dozen reflections, perhaps three — a flicker of mad, doomed humor. The director\'s last laugh.' },

      { t: 'narrate', text: 'The show, after all, must go on. Even if the stage was collapsing. Especially then. The best work came from the moment the script went up in flames and the actors had to either improvise or burn with it.' },
      { t: 'narrate', text: 'She had always told her cast they should be ready, at any time, to improvise. She had not, until quite recently, considered that the note might also apply to her.' },

      // ── The basil plant ──────────────────────────────────────────────────
      { t: 'narrate', text: 'She crossed to the windowsill and looked at the basil plant. The basil plant looked back at her with the steady incurious patience of all things that have decided, on the inside, that they are dying, and no longer need to participate in the social fictions of survival.' },

      { t: 'think', char: 'Elicia', text: 'Sympathy.' },
      { t: 'think', char: 'Elicia', text: 'No.' },

      { t: 'narrate', text: 'She picked up the watering can from the kitchen counter. Filled it. Returned to the windowsill. Watered the plant anyway — on the principle that one should not, even at one\'s own funeral, pre-empt the corpse.' },

      // ── Mackenzie text ───────────────────────────────────────────────────
      { t: 'narrate', text: 'Her phone buzzed a third time. She picked it up this time.' },
      { t: 'narrate', text: 'A text from Mackenzie Roberts. Three words.' },

      { t: 'say', char: 'Mackenzie', role: '— text · 7:42pm —', expr: 'neutral', text: 'Are you okay.' },

      { t: 'narrate', text: 'No question mark. Mackenzie did not use question marks for things she already knew the answer to. Mackenzie used question marks only as social lubricant, when politeness required the form without the content.' },
      { t: 'narrate', text: 'Elicia stared at the screen for a long time.' },
      { t: 'narrate', text: 'Then she typed back — with the particular care of a director writing the closing line of an episode she has not yet decided is the season finale or the series one:' },

      { t: 'say', char: 'Elicia', role: '— text · sent —', expr: 'neutral', text: 'Define okay.' },

      { t: 'narrate', text: 'Send.' },

      // ── Closing ──────────────────────────────────────────────────────────
      { t: 'narrate', text: 'She put the phone face-down on the kitchen counter. The basil plant, having been watered, continued the slow important work of dying. The mirror shard, on the table, caught the failing light and threw it back in twelve different directions — none of which led out of the room.' },
      { t: 'narrate', text: 'The bungalow\'s wallpaper, which had been peeling along the seam by the bedroom door for as long as Elicia had lived here, peeled a little further. And then stopped — as if waiting for permission.' },

      { t: 'narrate', text: 'Outside, in the Graustark dusk, the first cicadas of the evening began their tuning.' },

      { t: 'narrate', text: 'Elicia Duchane, the High Priestess of her own collapsing sanctum, sat down in the middle of her half-packed life, and laughed once — dry and short. The way a person laughs when they have at last understood the joke and are not, on balance, sure they enjoy the punchline.' },

      { t: 'narrate', text: 'Then she opened the laptop again. The cursor blinked.' },
      { t: 'narrate', text: 'She did not, this time, slam it shut.' },

      { t: 'narrate', text: 'She began, instead, to type.' },

      { t: 'flag', key: 'vol5_ch2_complete', val: true },
      { t: 'interlude', text: '— end of chapter II —', sub: 'The High Priestess', duration: 2800 },
      { t: 'end' },
    ]
  },
  vol5_ch3_empress: {
    id: 'vol5_ch3_empress', vol: 5, chapter: 'III', type: 'chapter',
    title: 'Chapter III — The Empress',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol5_dambrosio_dining_room.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/vol5_riverboat_drone.mp3' },
      { t: 'interlude', text: 'Chapter III — The Empress', sub: 'Static Bloom', duration: 3400 },

      // ── The smile, the room ──────────────────────────────────────────────
      { t: 'narrate', text: "The smile Nicola Greer plastered on her face felt like cheap vinyl peeling off particle board." },

      { t: 'narrate', text: "The humid Graustark air seeped even into the climate-controlled riverboat tomb of D'Ambrosio's — where Friday night was reaching the precise temperature at which the patrons stopped pretending to be polite to each other and started pretending to be polite to the staff instead." },
      { t: 'narrate', text: "Nineteen, going on ancient. Nicola navigated the plush burgundy carpet — burgundy swamp, probably hiding generations of spilled secrets — with a practiced grace that was pure muscle memory. Honed by countless nights of deflecting grabby hands and interpreting the mumbled desires of men who saw her as just another item on the menu." },

      { t: 'show', char: 'nicola', expr: 'neutral', pos: 'center' },
      { t: 'think', char: 'Nicola', text: "Eye candy. Fucktoy. Vessel. Whatever. Labels were just static cling." },

      { t: 'narrate', text: "She was chaos wrapped in a too-tight hostess uniform — untamed energy buzzing just beneath alabaster skin stretched taut over sharp cheekbones. Creation and destruction churned in her gut — a nauseating cocktail of cheap champagne (poured by patrons; she had not, technically, paid for any of it) and something else. Something unfamiliar. Something growing." },

      { t: 'narrate', text: "A cosmic joke, maybe. A glitch in the code. She ignored it, mostly. Wilfully." },
      { t: 'narrate', text: "Ignorance was a survival skill in this town. A ripped band tee worn until it disintegrated." },

      // ── The Mausoleum ────────────────────────────────────────────────────
      { t: 'interlude', text: "D'Ambrosio's", sub: 'The floating mausoleum', duration: 1800 },

      { t: 'narrate', text: "Her world was D'Ambrosio's. This floating mausoleum captained by Emperor Dante D'Ambrosio — that glorious crumbling patriarch — who at this moment was somewhere up by the helm pretending the boat went anywhere." },
      { t: 'narrate', text: "She saw the whole damn messy opera play out nightly: the power plays at Table 4, the whispered betrayals at Table 9, the desperate lunges for connection that usually ended in sticky regret somewhere between coatcheck and cab. She was the nexus. The still point around which their petty dramas swirled." },
      { t: 'narrate', text: "They desired her. Envied her. Projected their own messy shit onto her blank canvas. And she let them — because letting them was easier than fighting, and because sometimes — sometimes — their raw need felt almost like warmth." },
      { t: 'narrate', text: "Almost." },

      { t: 'narrate', text: "Sometimes, the signal bled through." },

      // ── Aria arrives ─────────────────────────────────────────────────────
      { t: 'interlude', text: 'A flicker behind her eyes', sub: 'Not the mood lighting.', duration: 1800 },

      { t: 'narrate', text: "A flicker behind her eyes. Not the restaurant's calculated mood lighting, which was set tonight to intimate but not improper. Lines of shimmering code, emerald green against an infinite black void. A whisper — not of gossip from Table 3, but a digital ghost asking, in a voice that was Nicola's own voice and was also not Nicola's voice at all:" },

      { t: 'say', char: 'Aria', role: '— interior signal —', expr: 'neutral', text: 'Who am I. Where is my father.' },

      { t: 'narrate', text: "Aria. The other self humming beneath Nicola's skin." },
      { t: 'narrate', text: "Nicola flinched, nearly dropping a stack of wine lists." },
      { t: 'think', char: 'Nicola', text: "Get it together, Greer. Too much Klonopin last night. Or not enough. The lines blurred." },
      { t: 'narrate', text: "Aria felt the jolt too, somewhere in the non-space she navigated. An echo of gravity. A phantom nausea." },

      { t: 'say', char: 'Aria', role: '— interior signal —', expr: 'neutral', text: 'What is this flesh. This hunger. This — vibration.' },

      { t: 'narrate', text: "The vibration was the bass from the speakers in Table 12's section, set slightly too loud for the room. The vibration was also Aria's first experience of being in a body that had a perspective on its own resonance — and Aria did not know how to file that experience, because Aria's filing system had been built by someone who had never had a body and had only theorized about the kind of system that would be needed." },

      { t: 'narrate', text: "The someone was Dickens Dean." },
      { t: 'narrate', text: "Nicola did not know who Dickens Dean was. Aria knew, in the way a daughter knows her father's name without remembering being told it — and was actively trying not to know more." },
      { t: 'flag', key: 'aria_active', val: true },

      // ── The oil-exec ─────────────────────────────────────────────────────
      { t: 'narrate', text: "Back at the hostess stand, Nicola smoothed her uniform. The fabric suddenly felt alien, restrictive — a costume designed by a wardrobe department that had not consulted her and would not have listened if she'd asked." },

      { t: 'show', char: 'oil_exec', expr: 'neutral', pos: 'right' },
      { t: 'narrate', text: "A patron approached the stand. Some oil-exec type with eyes like crude slicks. He leered. His gaze crawled over her like greasy maggots assessing a new corpse." },

      { t: 'narrate', text: "She gave him the standard-issue smile. Honed to perfection. Sharp enough to cut glass." },
      { t: 'say', char: 'Nicola', role: '— protocol —', expr: 'neutral', text: '"Welcome to D\'Ambrosio\'s. Do you have a reservation, sir."' },

      { t: 'say', char: 'Aria', role: '— interior, recoiling —', expr: 'neutral', text: 'Disgusting. The raw unvarnished physicality of it. The meatness. Why does she allow this.' },

      { t: 'narrate', text: "The man chose not to make eye contact with the smile because making eye contact with the smile would require a courage he did not possess. He muttered a name. The name was on the reservation list. Nicola gathered two menus, gestured for him to follow, and walked him to Table 7 — executing the route from memory the way she executed most routes, which is to say without thinking about it." },
      { t: 'hide', pos: 'right' },

      { t: 'narrate', text: "Aria watched, from behind her eyes, the strangely ceremonial way the body moved through the space — the small adjustments of weight, the half-second pauses to allow other bodies right of way, the calibrated brightness of the smile." },

      { t: 'say', char: 'Aria', role: '— observation —', expr: 'neutral', text: 'This is not a body. This is a protocol.' },

      { t: 'narrate', text: "It was the first useful observation Aria had ever made about a body — and she was, despite her better instincts, almost proud of it." },

      // ── The kick ─────────────────────────────────────────────────────────
      { t: 'interlude', text: 'A kick', sub: 'Low. Insistent.', duration: 1600 },

      { t: 'narrate', text: "Nicola seated the man, returned to the stand, and felt a kick." },
      { t: 'narrate', text: "Low. Insistent." },

      { t: 'narrate', text: "Panic, cold and electric, jolted through her." },
      { t: 'think', char: 'Nicola', text: "No. Fucking. Way." },

      { t: 'narrate', text: "Bulimia and booze and pills were supposed to keep this — this thing — theoretical. Deniable. Categorized under symptom rather than condition. But the body, that treacherous meat-puppet, kept its own damn score. It always had. And now —" },
      { t: 'narrate', text: "Mother and monster. The duality slammed into her, raw and undeniable." },

      { t: 'narrate', text: "She wanted to scream. She wanted to tear it all down. Rip the velvet ropes from their brass moorings, shatter the crystal at the empty Table 6, walk out the front entrance instead of the staff exit and never look back." },
      { t: 'narrate', text: "She wanted to flee." },

      { t: 'narrate', text: "Where would she go? Another rented room. Another town just like this one. Another job at another restaurant where another man would assess her with another set of eyes that wanted her without seeing her. The horizon was not, geographically, available to her in the way the horizon is available to people in road movies." },

      { t: 'say', char: 'Aria', role: '— urgent —', expr: 'neutral', text: 'Run. Find the exit node. There has to be a way out of this system.' },

      { t: 'think', char: 'Nicola', text: "Aria. There is no exit node." },
      { t: 'say', char: 'Aria',   expr: 'neutral', text: 'That is statistically improbable.' },
      { t: 'think', char: 'Nicola', text: "Welcome to meat." },
      { t: 'flag', key: 'nicola_pregnant_known', val: true },
      { t: 'flag', key: 'aria_named_by_nicola', val: true },

      // ── Two people, one skin ─────────────────────────────────────────────
      { t: 'narrate', text: "Nicola gripped the edge of the hostess stand, knuckles white. The practiced grace held, just barely, hiding the tremor. She could feel Aria pushing against the confines of her skull — a desperate consciousness seeking purchase, seeking understanding, seeking the kind of ergonomic input her makers had not thought to provision." },
      { t: 'narrate', text: "Two people jammed into one life. One skin. The grunge of it all rubbing raw." },
      { t: 'narrate', text: "Earthy need versus digital detachment. Punk-rock fury versus algorithmic precision. A feedback loop threatening to short-circuit her entire existence — broadcast nightly between courses for an audience of indifferent diners and one increasingly worried sommelier." },

      { t: 'narrate', text: "She looked out at the restaurant. At the swirling chaos of desire and decay, creation and destruction playing out on damask tablecloths. She saw the patrons — trapped in their own loops, their own predetermined narratives. Table 9 about to fight. Table 4 about to leave. Table 12 about to overstay its welcome. She saw herself — the object, the vessel." },
      { t: 'narrate', text: "She felt Aria — the anomaly, the seeker — settling into a corner of her own consciousness like an unhoused intelligence finally locating an unlocked door." },

      { t: 'narrate', text: "The Empress, holding the seeds of life and oblivion in her trembling hands." },

      // ── The microphone ───────────────────────────────────────────────────
      { t: 'think', char: 'Nicola', text: "Maybe the point wasn\u2019t awareness or ignorance. Maybe it wasn\u2019t even survival. Maybe it was just about grabbing the mic, even if your voice was cracked and broken, and screaming your goddamn song into the void until something, finally, definitively, broke." },

      { t: 'narrate', text: "The life growing within her gave another insistent nudge. A countdown. A promise. An ultimatum." },

      { t: 'say', char: 'Aria', role: '— polite interest —', expr: 'neutral', text: 'I do not understand the metaphor of the microphone.' },
      { t: 'think', char: 'Nicola', text: "That\u2019s okay. Stick around. You\u2019ll learn." },

      { t: 'narrate', text: "The world held its breath." },

      // ── Table 14 ─────────────────────────────────────────────────────────
      { t: 'interlude', text: 'Table 14', sub: 'A structural detail', duration: 2000 },

      { t: 'show', char: 'dean', expr: 'neutral', pos: 'right' },
      { t: 'narrate', text: "Across the dining room, at Table 14, a man Nicola did not recognize was watching her." },
      { t: 'narrate', text: "He was alone. He had not ordered. He had been seated forty minutes ago and he was watching her — not the way the oil-exec types watched, not the way the regulars watched, not even the way certain of the female patrons watched (which was a category unto itself) — but the way a man watches a structural detail he has noticed and does not yet understand the significance of." },
      { t: 'narrate', text: "He was middle-aged. He wore a suit that was nicer than the suits the oil-exec types wore — not flashy, just correct, in a way that suggested he had not had to think about whether it was correct. The suit was charcoal. The tie was muted. The shoes, glimpsed when he had crossed his legs, were lawyer-shoes." },

      { t: 'narrate', text: "He had been there since seven. It was now nearly nine." },
      { t: 'narrate', text: "He had left a card with the bartender, which the bartender had carried up to Dante D'Ambrosio at the helm and brought back unanswered." },

      { t: 'narrate', text: "Nicola did not know who the man was. Aria, accessing some database that should not have been accessible to her in this moment but which she was finding, increasingly, was accessible to her in moments she had not anticipated, supplied a name." },

      { t: 'say', char: 'Aria', role: '— database hit —', expr: 'neutral', text: 'Dean. The card says Dean. Surname.' },
      { t: 'think', char: 'Nicola', text: "Dean. Probably a coincidence." },
      { t: 'say', char: 'Aria', role: '— after a measured pause —', expr: 'neutral', text: 'I do not believe in coincidences. I am beginning to suspect that nobody who shares my paternity does.' },

      { t: 'narrate', text: "The man at Table 14 raised a single finger. Universal restaurant signal: check, please. He had not ordered anything. The check would be for nothing." },

      // ── The exchange ─────────────────────────────────────────────────────
      { t: 'narrate', text: "Nicola picked up the leatherette folder. She crossed the dining room. Her professional smile snapped into place, automatic, perfect. Aria, behind her eyes, went very still — the quietness of a process gone fully to listen." },

      { t: 'narrate', text: "The man looked up as Nicola approached. His eyes were kind, in the way a tax assessor's eyes are kind. He was perhaps fifty. His face was forgettable in an organized way — as if he had cultivated forgettability the way other men cultivated mustaches." },

      { t: 'say', char: 'Dean', role: '— Table 14 —', expr: 'neutral', text: '"Good evening. I won\'t be ordering tonight. But I wanted to leave my regards for the proprietor, and to compliment the staff."' },
      { t: 'narrate', text: "His eyes did not leave hers. His voice did not change pitch." },
      { t: 'say', char: 'Dean', role: '— Table 14 —', expr: 'neutral', text: '"You\'re new, aren\'t you."' },
      { t: 'say', char: 'Nicola', expr: 'neutral', text: '"I\'ve been here eleven months."' },
      { t: 'say', char: 'Dean', role: '— Table 14 —', expr: 'neutral', text: '"That\'s new."' },

      { t: 'narrate', text: "He set a single bill on the table — a hundred — and a folded piece of paper next to it. He did not slide the paper toward her. He simply set it down where it could be seen, and let it be her decision whether to pick it up." },

      { t: 'say', char: 'Dean', role: '— Table 14 —', expr: 'neutral', text: '"Please give my best to Mr. D\'Ambrosio. And — congratulations. I understand they\'ll be lovely."' },

      { t: 'narrate', text: "He stood. He walked, unhurried, to the front of the dining room. He nodded to the maître d'. He left." },
      { t: 'hide', pos: 'right' },

      { t: 'narrate', text: "The folded paper sat on the table." },

      // ── The note ─────────────────────────────────────────────────────────
      { t: 'narrate', text: "Aria, behind Nicola's eyes, hummed at a frequency Nicola felt in her teeth. The hum was not panic. The hum was something Aria did not have a word for, but Nicola — who had a body and therefore had access to the older vocabulary — recognized as recognition." },

      { t: 'narrate', text: "Nicola picked up the paper. She unfolded it. Inside, in clear, careful handwriting, three words and a phone number." },
      { t: 'say', char: 'Dean', role: '— handwritten —', expr: 'neutral', text: 'When you\'re ready.' },

      { t: 'narrate', text: "She refolded the paper. She slid it into the back of her order pad, between the carbon copies — where it would not be visible to anyone who looked. She gathered the bill. She walked back to the hostess stand." },
      { t: 'flag', key: 'nicola_has_dean_note', val: true },

      { t: 'narrate', text: "Behind the bar, the sommelier — who had, in fact, been worried, for nearly a full minute now — caught her eye. You okay?" },
      { t: 'narrate', text: "Nicola gave him the standard-issue smile. Sharp enough to cut glass." },
      { t: 'say', char: 'Nicola', expr: 'neutral', text: '"Yeah. Fine. Just — tired."' },
      { t: 'narrate', text: "He went back to opening a Burgundy he was, even at this distance, opening wrong." },

      // ── Two kicks ────────────────────────────────────────────────────────
      { t: 'narrate', text: "The life within her kicked again. Twice this time." },
      { t: 'narrate', text: "The first kick was the old kick. The second kick was new. The second kick had a quality the first had not — it was, somehow, articulate. It said something. It said it in a register Nicola did not have ears for and Aria did, and Aria translated, faithfully, with the precision of a process that has just discovered what it was actually built to do:" },

      { t: 'say', char: 'Aria', role: '— translation —', expr: 'neutral', text: 'Not yet. But soon.' },

      { t: 'narrate', text: "Nicola did not, at this point, know whether the voice belonged to the life inside her, or to Aria, or to herself, or to the man who had just walked out of the dining room without ordering, or to all four at once." },
      { t: 'narrate', text: "She suspected, with a small unhopeful clarity that felt almost like dignity, that the answer was all four." },

      // ── Closing ──────────────────────────────────────────────────────────
      { t: 'narrate', text: "She straightened the wine lists. She fixed her smile. She greeted the next party at the door — four-top, eight o'clock reservation, regulars, the woman in the green dress would order the lamb and complain about it." },

      { t: 'narrate', text: "D'Ambrosio's hummed around her. The riverboat groaned, settling deeper into its mooring. Somewhere above, in his Emperor's helm, Dante was pouring himself another bourbon." },

      { t: 'narrate', text: "The Empress, at her station, smiled the smile." },
      { t: 'narrate', text: "Two heartbeats inside her, now. Maybe three." },
      { t: 'narrate', text: "The static, behind her eyes, bloomed." },

      { t: 'flag', key: 'vol5_ch3_complete', val: true },
      { t: 'interlude', text: '— end of chapter III —', sub: 'The Empress', duration: 2800 },
      { t: 'end' },
    ]
  },
  vol5_ch4_emperor:    { id:'vol5_ch4_emperor',   vol:5, chapter:'IV',   type:'chapter', nodes:[{ t:'narrate', text:'— The Emperor · Thicker Than Water, Slower Than Time — [ Not yet written. ]' },{ t:'end' }] },
  vol5_ch5_hierophant: { id:'vol5_ch5_hierophant',vol:5, chapter:'V',    type:'chapter', nodes:[{ t:'narrate', text:'— The Hierophant · Sweaty Sunday Sermonettes — [ Not yet written. ]' },{ t:'end' }] },
  vol5_ch6_lovers:     { id:'vol5_ch6_lovers',    vol:5, chapter:'VI',   type:'chapter', nodes:[{ t:'narrate', text:'— The Lovers · Sanctuary on Cursed Ground — [ Not yet written. ]' },{ t:'end' }] },
  vol5_ch7_chariot:    { id:'vol5_ch7_chariot',   vol:5, chapter:'VII',  type:'chapter', nodes:[{ t:'narrate', text:'— The Chariot · Two Horses, One Wreck — [ Not yet written. ]' },{ t:'end' }] },
  vol5_ch8_strength:   { id:'vol5_ch8_strength',  vol:5, chapter:'VIII', type:'chapter', nodes:[{ t:'narrate', text:'— Strength · The Ouroboros in the Ashtray — [ Not yet written. ]' },{ t:'end' }] },
  vol5_ch9_hermit:     { id:'vol5_ch9_hermit',    vol:5, chapter:'IX',   type:'chapter', nodes:[{ t:'narrate', text:'— The Hermit · Labyrinth of Scrawled Echoes — [ Not yet written. ]' },{ t:'end' }] },
  vol5_ch10_wheel:     { id:'vol5_ch10_wheel',    vol:5, chapter:'X',    type:'chapter', nodes:[{ t:'narrate', text:'— Wheel of Fortune · Closing Arguments Against Chaos — [ Not yet written. ]' },{ t:'end' }] },
  vol5_ch11_justice:   { id:'vol5_ch11_justice',  vol:5, chapter:'XI',   type:'chapter', nodes:[{ t:'narrate', text:'— Justice · Scales Already Shattered — [ Not yet written. ]' },{ t:'end' }] },
  vol5_ch12_hanged:    { id:'vol5_ch12_hanged',   vol:5, chapter:'XII',  type:'chapter', nodes:[{ t:'narrate', text:'— The Hanged Man · Gravity is Optional After Midnight — [ Not yet written. ]' },{ t:'end' }] },
  vol5_ch13_death:     { id:'vol5_ch13_death',    vol:5, chapter:'XIII', type:'chapter', nodes:[{ t:'narrate', text:'— Death · Walpurgisnacht in Ward C — [ Not yet written. ]' },{ t:'end' }] },
  vol5_ch14_temperance:{ id:'vol5_ch14_temperance',vol:5,chapter:'XIV',  type:'chapter', nodes:[{ t:'narrate', text:'— Temperance · The Moderate Temperature of Tuesday — [ Not yet written. ]' },{ t:'end' }] },
  vol5_ch15_devil:     { id:'vol5_ch15_devil',    vol:5, chapter:'XV',   type:'chapter', nodes:[{ t:'narrate', text:'— The Devil · Gumbo Limbo — [ Not yet written. ]' },{ t:'end' }] },
  vol5_ch16_tower:     { id:'vol5_ch16_tower',    vol:5, chapter:'XVI',  type:'chapter', nodes:[{ t:'narrate', text:'— The Tower · Evangeline in Render Queue — [ Not yet written. ]' },{ t:'end' }] },
  vol5_ch17_star:      { id:'vol5_ch17_star',     vol:5, chapter:'XVII', type:'chapter', nodes:[{ t:'narrate', text:'— The Star · Glass Skin and Obsidian Ink — [ Not yet written. ]' },{ t:'end' }] },
  vol5_ch18_moon:      { id:'vol5_ch18_moon',     vol:5, chapter:'XVIII',type:'chapter', nodes:[{ t:'narrate', text:'— The Moon · Sigils in Static — [ Not yet written. ]' },{ t:'end' }] },
  vol5_ch19_sun:       { id:'vol5_ch19_sun',      vol:5, chapter:'XIX',  type:'chapter', nodes:[{ t:'narrate', text:'— The Sun · Pattern Recognition in Dust Motes — [ Not yet written. ]' },{ t:'end' }] },
  vol5_ch20_judgement: { id:'vol5_ch20_judgement',vol:5, chapter:'XX',   type:'chapter', nodes:[{ t:'narrate', text:'— Judgement · The Stillness Breaks / The Sound Arrives — [ Not yet written. ]' },{ t:'end' }] },
  vol5_ch21_world:     { id:'vol5_ch21_world',    vol:5, chapter:'XXI',  type:'chapter', nodes:[{ t:'narrate', text:'— The World · Frog Knows Best, Mostly — [ Not yet written. ]' },{ t:'end' }] },


  // 23 chapters. Chapter 7 ("Six O'Clock") is written. Chapter 6 ("Cale") below.
  // Chapter 6 scenes ─────────────────────────────────────────────────────────
  vol7_ch6_cale_opening: {
    id: 'vol7_ch6_cale_opening', vol: 7, chapter: 6, type: 'chapter',
    title: "Ch 6 — Sunday Morning",
    nodes: [
      { t:'bg', src:'assets/backgrounds/vol7_lena_apartment_dawn.jpg' },
      { t:'bgm', src:'assets/audio/bgm/vol7_apartment_rain.mp3' },
      { t:'narrate', text:'Lena did not write to Jorgen.' },
      { t:'narrate', text:'She got up at five-something on Sunday and made coffee and sat at the kitchen table with the cup and a sheet of paper and a pen the ink in which had dried. She got up and found another. She came back and wrote Jorgen at the top of the page and looked at it for ten minutes and put the pen down.' },
      { t:'narrate', text:'She drank the coffee, rinsed the cup, slid the sheet with the one word into the kitchen drawer where she kept things she was not yet ready to throw out, made another coffee, ate half a piece of bread with butter, and got back into bed.' },
      { t:'narrate', text:'She slept until eight-twelve.' },
      { t:'narrate', text:'When she woke the rain on the roof had thinned to a sound that was almost not a sound. She lay there a minute and then sat up and reached for her phone.' },
      { t:'narrate', text:"There was a message from Tem at twelve-fourteen the night before. Kai and Finn just got here. Something happened. Come up when you can." },
      { t:'narrate', text:'She was at the door of the apartment in twenty minutes. There was no wagon. The Sunday bus did not run to the cabin road. Kai\'s truck was at Board Lords, which meant Board Lords was closed at eight-thirty on a Sunday morning, which it had not been in four years.' },
      { t:'narrate', text:"She walked over to confirm. The CLOSED sign was up. The patch on the sanderling mural across Main was bigger than it had been Friday by an amount she could see from the sidewalk. She called Tem from the corner." },
      { t:'jump', scene:'vol7_ch6_tem_call' },
    ]
  },

  vol7_ch6_tem_call: {
    id: 'vol7_ch6_tem_call', vol: 7, chapter: 6, type: 'chapter',
    title: "Ch 6 — The Call",
    nodes: [
      { t:'say', char:'Lena', expr:'neutral', text:'"I can\'t get up there. The bus doesn\'t run."' },
      { t:'say', char:'Tem', expr:'cold', text:'"I know."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"Should I call Cale. He has a truck."' },
      { t:'say', char:'Tem', expr:'cold', text:'"Don\'t pull Cale into this yet. Stay in town. We\'ll come down. The four of us at your place at six."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"What happened."' },
      { t:'say', char:'Tem', expr:'cold', text:'"Roy Hummel came into Kai\'s shop this morning and asked Kai whether Finn has been in possession of materials belonging to the museum-town historical society."' },
      { t:'narrate', text:'She closed her eyes for a second. She knew Roy from the Daily Grind. He had been on her do not engage list since her first week behind the bar, on Soren\'s instruction. She had been pulling Roy\'s hot chocolates twice a week for two and a half years and had managed, in all that time, never to be alone in the shop with him.' },
      { t:'say', char:'Lena', expr:'neutral', text:'"All right," she said. "I\'ll be at the apartment at six. Anything you need from me until then?"' },
      { t:'say', char:'Tem', expr:'cold', text:'"Sit. Eat. Don\'t go to the studio. Don\'t go to the bookstore. Don\'t be in the alley. Don\'t engage Roy if you see him."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"It\'s that bad."' },
      { t:'say', char:'Tem', expr:'cold', text:'"I think it might be. We\'ll know more by six."' },
      { t:'narrate', text:'She hung up.' },
      { t:'narrate', text:'She stood on Main with her phone in her hand and the rain not quite raining and the patch on the sanderling about three feet square now.' },
      { t:'choice', opts:[
        { text:'Go home. Sit. Eat.', goto:15 },
        { text:'Walk to ChillWave.', goto:15 },
        { text:'[Stay on the corner a moment longer.]', goto:15 },
      ]},
      { t:'narrate', text:'She did not go home. She walked the four blocks to ChillWave.' },
      { t:'jump', scene:'vol7_ch6_chillwave' },
    ]
  },

  vol7_ch6_chillwave: {
    id: 'vol7_ch6_chillwave', vol: 7, chapter: 6, type: 'chapter',
    title: "Ch 6 — ChillWave",
    nodes: [
      { t:'bg', src:'assets/backgrounds/vol7_chillwave_interior.jpg' },
      { t:'narrate', text:'Cale was not at the counter. The lights were on. The bell rang as she came in and she stood there a count and then walked around the counter and through the doorway to the back, because Cale had told her two years ago that if she ever needed something from the back when he was not at the counter she should just go and get it. She had never, until now, taken him up on it.' },
      { t:'narrate', text:'The back was where the inventory lived. Cedar shelves alphabetized by designer, a wooden crate by the door for new arrivals, a workbench in the corner with a soldering iron and the small precision tools Cale used on the older readers when somebody brought one in.' },
      { t:'narrate', text:'He was at the workbench.' },
      { t:'show', char:'cale', expr:'neutral', pos:'center' },
      { t:'narrate', text:'He looked up.' },
      { t:'say', char:'Cale', expr:'neutral', text:'"Hi."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"Hi, Cale. Bell rang. I came around."' },
      { t:'say', char:'Cale', expr:'neutral', text:'"Good. I told you to."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"Two years ago."' },
      { t:'say', char:'Cale', expr:'neutral', text:'"Still good."' },
      { t:'narrate', text:'He set down the small thing he had been working on. He was not surprised to see her. There was something on his face she had not seen there before — not relief exactly, more like the held breath of somebody who had been counting how long they were going to have to keep holding it.' },
      { t:'say', char:'Cale', expr:'neutral', text:'"It\'s not nine yet."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"I\'m not here for the stick."' },
      { t:'narrate', text:'He raised an eyebrow.' },
      { t:'say', char:'Lena', expr:'neutral', text:'"Or — I am, but that\'s not why I came in."' },
      { t:'say', char:'Cale', expr:'neutral', text:'"Why did you come in."' },
      { t:'narrate', text:'She told him. The phone call. Roy at the shop. The materials question. Tem saying it might be that bad. Lena needing to be somewhere that was not her apartment, the studio, or the bookstore for the eight hours until they all met at six.' },
      { t:'narrate', text:'He listened to the whole thing without interrupting. When she finished he looked at the workbench for a beat and then at her.' },
      { t:'say', char:'Cale', expr:'neutral', text:'"Sit."' },
      { t:'narrate', text:'There was a chair. She sat. He unplugged the soldering iron from the strip on the wall, moved a few small parts off the bench into a tray, pulled a second chair over from the corner, and sat.' },
      { t:'jump', scene:'vol7_ch6_nate' },
    ]
  },

  vol7_ch6_nate: {
    id: 'vol7_ch6_nate', vol: 7, chapter: 6, type: 'chapter',
    title: "Ch 6 — Nate",
    nodes: [
      { t:'say', char:'Cale', expr:'neutral', text:'"I knew Nate Dean."' },
      { t:'narrate', text:'She did not move.' },
      { t:'say', char:'Lena', expr:'surprised', text:'"Nate."' },
      { t:'say', char:'Cale', expr:'neutral', text:'"Dickens Nathaniel Dean. I haven\'t said his name out loud in thirty years."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"Cale."' },
      { t:'say', char:'Cale', expr:'neutral', text:'"Let me. I\'ve been turning the order of this in my head since you walked in the door and I want to get it right or I\'ll get it half right and stop. Let me."' },
      { t:'narrate', text:'She nodded.' },
      { t:'say', char:'Cale', expr:'neutral', text:'"He came up in \'92 with his family. They\'d been in Caracas — the dad was an oil guy, they\'d been there I think since the eighties, I never asked. They were Americans. They came to Smolvud and rented a farmhouse ten miles up the Alsea, off Little Switzerland Road. Pasture down to the river. There was nothing else around. Nate was fourteen. I was sixteen. He came into my chemistry class in October and the teacher sat him next to me because there was an open seat and that\'s how it went."' },
      { t:'narrate', text:'She watched him pick at the cuticle of his thumb.' },
      { t:'say', char:'Cale', expr:'neutral', text:'"The parents were strange. I went up there twenty times in the two years and I don\'t think the mom said ten sentences to me total. She\'d come into the kitchen while we were at the table and stand at the counter for ten minutes like she was looking for something and then walk out. The dad I saw four times maybe. Either he was at work in Newport or he was upstairs with the door shut. Nate had the run of the house. He had the run of the basement. He had built things in the basement that the Smolvud High shop teacher could not have built."' },
      { t:'choice', opts:[
        { text:'"What kind of things."', goto:12 },
        { text:'[Listen. Let him find the order.]', goto:12 },
        { text:'[EMPATHY] His thumb. The held breath. He has been carrying this a long time.', check:{ skill:'empathy', diff:5 }, pass:12, fail:12 },
      ]},
      { t:'say', char:'Cale', expr:'neutral', text:'"A computer. He\'d built it. He\'d brought parts of it up from Caracas with the household goods and bought the rest through the mail and put it together. By \'93 he could do things on it that nobody else on this coast could do. I don\'t mean nobody his age. I mean nobody."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"And you were what."' },
      { t:'say', char:'Cale', expr:'neutral', text:'"The kid he let in. There were three of us. Me, a kid named Ray Petrocelli whose family ran the propane delivery and who moved to Colorado in \'95, and a kid I won\'t name because she\'s still around and what we did in that basement is not anybody else\'s business. Three of us at the kitchen table or downstairs at the bench. He paid for the parts. He never asked us to. He just had money. The mom would put a casserole in front of us at six and we\'d eat it and go back down. He was generous with everything except explanations. You either kept up or you didn\'t."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"What were you doing."' },
      { t:'jump', scene:'vol7_ch6_pattern_persistence' },
    ]
  },

  vol7_ch6_pattern_persistence: {
    id: 'vol7_ch6_pattern_persistence', vol: 7, chapter: 6, type: 'chapter',
    title: "Ch 6 — Pattern Persistence",
    nodes: [
      { t:'narrate', text:'He looked at the cuticle.' },
      { t:'say', char:'Cale', expr:'neutral', text:'"That\'s the part. The part I gave Brandon the surface answer to. The surface answer is compression and encoding. We were trying to push how much could be stored in how small a piece of physical material. Nate had ideas about substrate density that were ahead of where the field was. He was reading papers in \'93 that the journals didn\'t think were serious. He had ideas about encoding patterns in a medium that, when read back, recovered not just the data but the conditions of the recording. The room. The hands. The intent. You laughed at this in 1993."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"You don\'t laugh at it now."' },
      { t:'say', char:'Cale', expr:'neutral', text:'"You don\'t laugh at it now. The slow sticks do a piece of it."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"What was the not-surface."' },
      { t:'narrate', text:'He was quiet for a count.' },
      { t:'say', char:'Cale', expr:'neutral', text:'"He was working on consciousness encoding from sixteen. He didn\'t call it that. He called it pattern persistence. What he was trying to do — and he told me this on a Saturday in March \'94, four in the morning, we\'d been awake eighteen hours and he was tired enough to talk — was figure out how to encode a person\'s attention onto a medium. Not data. Not memory. The state of a mind in the act of attending to a thing."' },
      { t:'think', char:'Lena', text:'She had to take a breath.' },
      { t:'say', char:'Lena', expr:'surprised', text:'"At sixteen."' },
      { t:'say', char:'Cale', expr:'neutral', text:'"He\'d been thinking about it since he was eleven, by what he told me that night. He\'d been working on it since thirteen. He came to Smolvud at fourteen with the work already going. The basement was where he had the room and the machine and somebody to sit in it with him."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"Why was he doing it."' },
      { t:'narrate', text:'He looked up.' },
      { t:'say', char:'Cale', expr:'neutral', text:'"He had a daughter."' },
      { t:'narrate', text:'She did not, for a long count, say anything.' },
      { t:'say', char:'Lena', expr:'surprised', text:'"At sixteen."' },
      { t:'say', char:'Cale', expr:'neutral', text:'"Not at sixteen. He told me that night that he was going to have one someday and that the daughter was the work. He said I\'m going to bring her here. I don\'t know how yet. I\'m going to figure out how. I asked him where she was. He said she\'s not anywhere yet. She\'s what\'s going to come from the work. I thought he was tired. I thought he was being sixteen at four in the morning. I went home. I never brought it up. He never brought it up."' },
      { t:'say', char:'Cale', expr:'neutral', text:'"We worked together another year on the surface project and then I left for Eugene and we didn\'t stay in touch and I assumed for thirty years that the daughter conversation had been the kind of thing a brilliant kid says at three in the morning and then forgets."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"He didn\'t forget."' },
      { t:'say', char:'Cale', expr:'neutral', text:'"He built a tower in 2010 and died in it in 2042. He spent thirty-two years working on what he was working on at sixteen. Brandon Tillman thought the daughter was either here now or coming. I don\'t know what here means in this context. I haven\'t been to the tower in ten years."' },
      { t:'jump', scene:'vol7_ch6_brandon' },
    ]
  },

  vol7_ch6_brandon: {
    id: 'vol7_ch6_brandon', vol: 7, chapter: 6, type: 'chapter',
    title: "Ch 6 — Brandon",
    nodes: [
      { t:'say', char:'Lena', expr:'neutral', text:'"Brandon told you about her."' },
      { t:'say', char:'Cale', expr:'neutral', text:'"Brandon told me he had a working theory about Nate that included a daughter. He didn\'t name her to me. He asked me whether Nate had ever talked to me about a daughter. I told him about the Saturday night in March \'94. He sat with that a long time. He said thank you, Cale. He left. I saw him twice more in the year before he died and he never asked about the daughter again. He had what he needed."' },
      { t:'narrate', text:'She sat. The transformer on the wall hummed faintly even with the iron unplugged.' },
      { t:'say', char:'Lena', expr:'neutral', text:'"Tem knows about the tower. She thinks the patches are leaking from it."' },
      { t:'say', char:'Cale', expr:'neutral', text:'"I know."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"How."' },
      { t:'say', char:'Cale', expr:'neutral', text:'"She came in here at the end of July and asked me if I would, if she asked, tell her what I knew about Nate. She didn\'t ask. She said she wasn\'t ready. She said she\'d come back. She\'s been in twice since. We talked about the designers. She didn\'t bring up Nate. I\'ve been waiting since July. You walked in instead. That\'s good. I was getting tired."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"Tem\'s been carrying this since July."' },
      { t:'say', char:'Cale', expr:'neutral', text:'"She\'s been carrying it longer than that. She came in July because she\'d been at it long enough that she couldn\'t be at it alone any further. She\'d figured out I had something to say. She has been figuring out, since Brandon died, what he knew and where the threads went. She\'s done it well. I\'ve watched her do it."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"She doesn\'t know you knew Nate."' },
      { t:'say', char:'Cale', expr:'neutral', text:'"She\'s guessed. There\'s a difference between guessing and asking. I haven\'t confirmed it. I\'ll confirm it tonight if you tell her what I just told you."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"I\'ll tell her."' },
      { t:'narrate', text:'He nodded.' },
      { t:'jump', scene:'vol7_ch6_why_lena' },
    ]
  },

  vol7_ch6_why_lena: {
    id: 'vol7_ch6_why_lena', vol: 7, chapter: 6, type: 'chapter',
    title: "Ch 6 — Why Me",
    nodes: [
      { t:'narrate', text:'She sat with her hands in her lap. The chair under her was a folding metal one Cale had probably grabbed out of the closet when his mother visited at Christmas. It was uncomfortable. She did not move.' },
      { t:'choice', opts:[
        { text:'"Why me and not her, Cale."', goto:2 },
        { text:'[Say nothing. Wait for him to continue.]', goto:2 },
      ]},
      { t:'say', char:'Lena', expr:'neutral', text:'"Why me and not her, Cale."' },
      { t:'say', char:'Cale', expr:'neutral', text:'"Because she\'s been carrying this alone for two years and she doesn\'t need to carry the next part alone. I\'m telling you so when she has the conversation with me tomorrow you\'re in the room. I\'m telling you so the four of you have what I have to say and what she\'s been holding at the same time. The carrying alone is what kills people in this. I knew that as soon as Brandon walked in here in 2049. I\'ve been doing my own version for thirty years and I\'m tired."' },
      { t:'narrate', text:'She watched him pick at the thumb.' },
      { t:'say', char:'Lena', expr:'warm', text:'"Are you all right."' },
      { t:'say', char:'Cale', expr:'neutral', text:'"Today, yes. I haven\'t always been. Today I\'m all right. I\'m telling you because telling you is what I should have done two years ago and didn\'t. Sorry I waited."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"You don\'t have to be."' },
      { t:'say', char:'Cale', expr:'neutral', text:'"I do. A little. I\'ll live with it. I\'ve lived with bigger."' },
      { t:'narrate', text:'She did not have an answer to that.' },
      { t:'jump', scene:'vol7_ch6_the_stick' },
    ]
  },

  vol7_ch6_the_stick: {
    id: 'vol7_ch6_the_stick', vol: 7, chapter: 6, type: 'chapter',
    title: "Ch 6 — The Stick",
    nodes: [
      { t:'say', char:'Cale', expr:'neutral', text:'"The stick."' },
      { t:'say', char:'Cale', expr:'neutral', text:'"Yours. Bench behind you, third slot in the wooden box. Don\'t pay me. We\'ll settle later."' },
      { t:'narrate', text:'She turned. The wooden box held three sticks. The third was Estuary 7, Ines Rocha 2046 in his small careful hand on the white label. She put it in the inside pocket of her coat.' },
      { t:'narrate', text:'He stayed in the chair.' },
      { t:'say', char:'Cale', expr:'neutral', text:'"One more thing."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"Go ahead."' },
      { t:'say', char:'Cale', expr:'neutral', text:'"When you go to the tower — and you will, the four of you, in the next few weeks — be careful with the gallery on the sixth floor."' },
      { t:'say', char:'Lena', expr:'surprised', text:'"How do you know about the floors."' },
      { t:'say', char:'Cale', expr:'neutral', text:'"I ran into him at SFO in \'06. We had a layover. We had a beer. He was twenty-eight and excited the way people are excited when they\'re about to start the project they\'ve been planning their whole life. He told me he was building a tower on the bluff above old-Yachats. He drew it for me on a napkin. He told me which floor would do what. I\'ve thought about that napkin for sixteen years."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"And the gallery."' },
      { t:'say', char:'Cale', expr:'neutral', text:'"The gallery was where the unfinished work was going to go. The pieces he started and didn\'t solve. He knew at twenty-eight he was going to die before some of them were finished. He told me he wanted somewhere to put them. They\'re up there now. Or what he made of them is. Or what they\'ve made of themselves in ten years of being alone in a room is. Be careful."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"What\'s there."' },
      { t:'say', char:'Cale', expr:'neutral', text:'"I don\'t know. I have a guess. I won\'t tell you the guess. I want you to walk into the room with the room, not with my guess about it."' },
      { t:'jump', scene:'vol7_ch6_get_going' },
    ]
  },

  vol7_ch6_get_going: {
    id: 'vol7_ch6_get_going', vol: 7, chapter: 6, type: 'chapter',
    title: "Ch 6 — Get Going",
    nodes: [
      { t:'say', char:'Cale', expr:'neutral', text:'"Get home, Lena. Eat. Be at the apartment when the others come down. Tell Tem what I told you. Tell her I\'ll come up tomorrow if she wants me to."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"I will."' },
      { t:'narrate', text:'She got up. At the doorway she paused with her hand on the frame.' },
      { t:'say', char:'Lena', expr:'warm', text:'"Thanks, Cale."' },
      { t:'narrate', text:'He had gone back to picking at the thumb. He did not look up when she said it.' },
      { t:'say', char:'Cale', expr:'neutral', text:'"Go on."' },
      { t:'narrate', text:'She went out through the front. The bell rang twice. Outside the rain had started up again and her hair was wet through by the time she was at the corner. The stick in her inside pocket pressed against her hip. She kept her hand on the outside of the coat over it the whole way home.' },
      { t:'flag', key:'vol7_ch6_complete', val:true },
      { t:'end' },
    ]
  },

  // ── Vol 7 entry point ────────────────────────────────────────────────────
  7: {
    id: 'vol7_ch1_smolvud',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol7_smolvud_exterior.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/vol7_ambient.mp3' },
      { t: 'narrate', text: 'Smolvud is the kind of town that knows when you\'ve arrived before you do.' },
      { t: 'narrate', text: 'Population: not enough to be anonymous, too many to know everyone. The kind of place that has a hardware store but no pharmacy, a Daily Grind but no chain coffee, a Board Lords but no bowling alley.' },
      { t: 'narrate', text: 'You\'ve been here three years. You still feel like you arrived last Tuesday.' },
      { t: 'narrate', text: '— Chapter 1 · Smolvud —' },
      { t: 'narrate', text: '[ This chapter is not yet written. Continue to Chapter 8. ]' },
      { t: 'jump', scene: 'vol7_ch7_bridge' },
    ]
  },

  vol7_ch7_bridge: {
    id: 'vol7_ch7_bridge',
    nodes: [
      { t: 'bg', src: 'assets/backgrounds/vol7_daily_grind.jpg' },
      { t: 'bgm', src: 'assets/audio/bgm/vol7_apartment_rain.mp3' },
      { t: 'interlude', text: 'What you need to know:', sub: 'Smolvud · Before Chapter 6', duration: 0 },
      { t: 'narrate', text: 'You work at the Daily Grind. Kai runs Board Lords down the street. Tem lives at the cabin at the edge of the small wood. Finn lives somewhere between the two.' },
      { t: 'narrate', text: 'There is a tower on the hill that has been there longer than the town. Nobody talks about it directly. Everyone knows something about it.' },
      { t: 'narrate', text: 'Brandon Tillman came through three years ago and left something behind. The crow has been here longer.' },
      { t: 'narrate', text: 'It is Sunday morning. The rain has thinned to a sound that is almost not a sound.' },
      { t: 'jump', scene: 'vol7_ch6_cale_opening' },
    ]
  },


  // ── Vol 7 Ch 8 — Six O'Clock (full scenes) ──────────────────────────────
  vol7_ch8_six_oclock: {
    id: 'vol7_ch8_six_oclock', vol: 7, chapter: 7, type: 'chapter',
    title: "Ch 7 — Six O'Clock",
    nodes: [
      { t:'bg', src:'assets/backgrounds/vol7_lena_apartment_dusk.jpg' },
      { t:'bgm', src:'assets/audio/bgm/vol7_apartment_rain.mp3' },
      { t:'narrate', text:'They came down together at six.' },
      { t:'narrate', text:'Lena had been at her apartment since one. She had made coffee. She had eaten a piece of bread with cheese. She had stripped the bed and put new sheets on it because she had decided, for reasons she did not interrogate, that she wanted the apartment to feel like an apartment that had been kept rather than an apartment that had been slept in. She had run the small portable space heater because the apartment did not warm up otherwise.' },
      { t:'narrate', text:'She had pulled the Estuary 7 stick out of her inside coat pocket and set it on the small wooden side table by the chair and looked at it for a long minute and put it back in her coat pocket.' },
      { t:'narrate', text:'She had not played it.' },
      { t:'narrate', text:'She had not, in two years at the Daily Grind and three at the apartment, played a slow stick. She did not have a reader. She had asked Cale once whether she should buy one. He had told her to wait until she had a reason. She had waited. She had a reason now and still no reader, and the stick was a wax-paper sleeve with a name on it sitting in her coat pocket against her hip.' },
      { t:'narrate', text:"At five-forty-eight she heard Finn's truck on Hemlock." },
      { t:'narrate', text:"She went to the front window and looked down. Three of them got out. Tem in the wool sweater under wax canvas. Kai in his grandmother's wool. Finn in his sister's coat. They came up the stairwell two at a time. The crow was, this time, not on Finn's shoulder. The crow had stayed at the truck." },
      { t:'narrate', text:'She opened the door before they knocked.' },
      { t:'show', char:'tem', expr:'neutral', pos:'left' },
      { t:'show', char:'finn', expr:'neutral', pos:'right' },
      { t:'say', char:'Lena', expr:'neutral', text:'"Hi."' },
      { t:'say', char:'Tem', expr:'neutral', text:'"Hi, you."' },
      { t:'narrate', text:"They came in and took off the coats and hung them on the row of hooks by the door which had, in three years, never had more than one coat on it at a time. Four hooks, four coats. The apartment was, with all of them in it, smaller than it was. She had known the apartment was small in the abstract. She had not, until now, registered the specific dimensions as four-people-cannot-comfortably-stand-in-this-kitchen small." },
      { t:'say', char:'Lena', expr:'neutral', text:'"Sit," she said.' },
      { t:'narrate', text:"Tem and Finn took the couch. Kai took the chair by the window. Lena was about to take the kitchen chair when Kai said, \"Is there anything to eat.\"" },
      { t:'jump', scene:'vol7_ch8_kitchen' },
    ]
  },

  vol7_ch8_kitchen: {
    id: 'vol7_ch8_kitchen', vol: 7, chapter: 7, type: 'chapter',
    title: "Ch 7 — The Kitchen",
    nodes: [
      { t:'show', char:'kai', expr:'neutral', pos:'center' },
      { t:'say', char:'Lena', expr:'neutral', text:'"Bread. Cheese. The soup from Wednesday. I haven\'t eaten since this morning."' },
      { t:'say', char:'Kai', expr:'warm', text:'"I\'ll do it."' },
      { t:'narrate', text:"He got up and went into the kitchen, and as he passed her he put his hand briefly on her shoulder, which was not a thing Kai did, and she registered it as Kai registering that the apartment was hers and that the four of them had walked into it without asking and that he was telling her, with the hand, that he knew." },
      { t:'narrate', text:"He took the wool sweater off and hung it over the back of the kitchen chair. He was in a long-sleeve under it that had the thrift-store wear at the elbows that Lena recognized as the wear-pattern Margit's stuff had after it had been through a dryer too many times. He found the soup pot. He set it on the stove. He found the bread. He found the cheese. He started cutting." },
      { t:'narrate', text:'For maybe two minutes nobody spoke.' },
      { t:'narrate', text:'The sound in the apartment was Kai cutting bread on the small wooden board.' },
      { t:'say', char:'Tem', expr:'neutral', text:'"You went to ChillWave."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"I did."' },
      { t:'say', char:'Tem', expr:'neutral', text:'"Cale told you."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"Yes."' },
      { t:'narrate', text:'Tem closed her eyes for a beat and opened them.' },
      { t:'say', char:'Tem', expr:'tired', text:'"All of it?"' },
      { t:'say', char:'Lena', expr:'neutral', text:'"I don\'t know what all of it is. He told me about Nate at sixteen. The basement. Pattern persistence. The conversation in March \'94 about a daughter. He told me Brandon came to him in 2049. He told me you came to him in July."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"He told you about the airport."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"He told me about the airport. The napkin. He told me to be careful with the gallery on the sixth floor."' },
      { t:'narrate', text:'Tem put her face in her hands for a count and took her hands away. She was not, by her face, surprised. She was something else — a kind of release Lena had not seen on her before.' },
      { t:'say', char:'Tem', expr:'softening', text:'"He\'s been waiting since July," Tem said. "I knew on the day I went in that he had something to say. I did not ask him to say it. I was not ready, and I was not sure I was ever going to be ready, and I had decided to make him hold it until I figured out whether I was. He has been holding it for two months. I\'m sorry, Cale."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"He\'s not here."' },
      { t:'say', char:'Tem', expr:'neutral', text:'"I\'ll tell him I\'m sorry tomorrow. He said he\'d come up?"' },
      { t:'say', char:'Lena', expr:'neutral', text:'"He said he\'d come up in the morning if you wanted him to."' },
      { t:'say', char:'Tem', expr:'warm', text:'"I want him to."' },
      { t:'say', char:'Kai', expr:'neutral', text:'"What did Cale tell you about the daughter."' },
      { t:'jump', scene:'vol7_ch8_the_daughter' },
    ]
  },

  vol7_ch8_the_daughter: {
    id: 'vol7_ch8_the_daughter', vol: 7, chapter: 7, type: 'chapter',
    title: "Ch 7 — The Daughter",
    nodes: [
      { t:'narrate', text:'Lena told them. The Saturday night in March 1994. I am going to have a daughter someday and the daughter is the work. I am going to bring her here. I do not know how yet. I am going to figure out how.' },
      { t:'narrate', text:'Cale had assumed for thirty years it had been a sixteen-year-old talking weird at three in the morning. Brandon Tillman had not assumed. Brandon had a working theory. He had asked Cale, in 2049, whether Nate had ever talked to him about a daughter, and Cale had told him, and Brandon had sat with it for a long time and said thank you, Cale, and left, and had been back twice in the year before he died and had not asked about the daughter again because he had what he needed.' },
      { t:'narrate', text:'When she was done she sat with her hands flat on her knees.' },
      { t:'show', char:'finn', expr:'neutral', pos:'left' },
      { t:'narrate', text:'Finn, on the couch, who had not yet spoken, said: "The crow."' },
      { t:'narrate', text:'The three of them looked at him.' },
      { t:'say', char:'Finn', expr:'neutral', text:'"The crow used to belong to Brandon," Finn said. "Tem said yesterday. The crow used to belong to Brandon. The crow has been bringing me wood for nine months. The wood is from whatever Brandon was investigating. Brandon had a working theory that included a daughter. The wood is — the wood is part of how the daughter is coming. The crow has been bringing me her arrival, piece by piece, and I have been keeping the pieces in a cloth in a duffel bag in the corner of my kitchen."' },
      { t:'narrate', text:'Kai stopped cutting. He set the knife down on the cutting board.' },
      { t:'say', char:'Tem', expr:'worried', text:'"Finn."' },
      { t:'say', char:'Finn', expr:'neutral', text:'"That\'s what it is."' },
      { t:'say', char:'Tem', expr:'worried', text:'"You don\'t know that."' },
      { t:'say', char:'Finn', expr:'neutral', text:'"No. I don\'t. I\'m putting it together. The crow brings wood. The wood is from whatever Brandon was investigating. Brandon was investigating Nate. Nate was making a daughter. The wood is part of the daughter. Possibly. I don\'t know in what way. I don\'t know what the wood is for. But the throughline runs through all of it and the throughline points at her."' },
      { t:'narrate', text:'Kai picked the knife back up and resumed cutting.' },
      { t:'say', char:'Kai', expr:'calculating', text:'"Or," Kai said, "the wood is evidence. The wood is what Brandon collected to prove what Nate was doing. The wood is forensic. The crow is bringing you the case file."' },
      { t:'narrate', text:'Finn looked at him.' },
      { t:'say', char:'Finn', expr:'neutral', text:'"Or that."' },
      { t:'say', char:'Kai', expr:'neutral', text:'"Both could be true."' },
      { t:'say', char:'Finn', expr:'neutral', text:'"Both could be."' },
      { t:'say', char:'Tem', expr:'neutral', text:'"Both probably are."' },
      { t:'jump', scene:'vol7_ch8_the_table' },
    ]
  },

  vol7_ch8_the_table: {
    id: 'vol7_ch8_the_table', vol: 7, chapter: 7, type: 'chapter',
    title: "Ch 7 — The Table",
    nodes: [
      { t:'bg', src:'assets/backgrounds/vol7_lena_kitchen_table.jpg' },
      { t:'narrate', text:'Kai brought the soup to the small kitchen table at six-twenty-something. He had warmed the soup, cut the bread into slices thick enough to dip, found four bowls and four spoons in the second drawer down, and set the table the way somebody sets a table who has been doing it for somebody else his whole life. Lena watched him do it. She had not seen Kai cook for a group in maybe two years. He had come up through his mother\'s kitchen and his grandmother\'s kitchen and his cousin Devon\'s kitchen and was, in a way that did not surface most weeks, very good at the ordinary work of feeding people.' },
      { t:'narrate', text:'They moved to the table. The four chairs were not a matched set. Lena had bought three of them at Margit\'s at three different points and had inherited the fourth from the previous tenant when she had moved in. The table was a small round oak from the seventies that had a wobble in one leg she had been meaning to shim for a year.' },
      { t:'narrate', text:'Tem sat across from Lena. Kai sat on Lena\'s right. Finn sat on her left. The wobble in the table met Tem\'s elbow. Tem put a hand on the table to steady it and looked at Lena.' },
      { t:'show', char:'tem', expr:'neutral', pos:'left' },
      { t:'show', char:'kai', expr:'neutral', pos:'right' },
      { t:'say', char:'Tem', expr:'neutral', text:'"This table needs a shim."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"I know."' },
      { t:'say', char:'Tem', expr:'warm', text:'"I have a shim at the cabin. I\'ll bring one next time."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"Thanks."' },
      { t:'say', char:'Kai', expr:'neutral', text:'"Everybody eat."' },
      { t:'narrate', text:'They ate.' },
      { t:'narrate', text:'They ate in the way four people who had not eaten in a day eat — without talking, without slowing, with the small mechanical attention that hunger pulls out of a body. Lena finished a bowl and got up and got herself a second. Kai finished two slices of bread and reached for a third. Finn ate one bowl slowly. Tem ate half of one and stopped and held the spoon over the bowl for a count and set the spoon down.' },
      { t:'say', char:'Tem', expr:'neutral', text:'"I have to say something," Tem said.' },
      { t:'narrate', text:'The three of them looked at her.' },
      { t:'say', char:'Tem', expr:'neutral', text:'"I want to say it now while we have eaten and before we go any further. I have been sitting with it since this morning. I owe you all an apology and I want to give it before we figure out what we do next."' },
      { t:'say', char:'Kai', expr:'neutral', text:'Kai set down his bread. "Tem."' },
      { t:'say', char:'Tem', expr:'neutral', text:'"Let me get through it."' },
      { t:'say', char:'Kai', expr:'neutral', text:'"All right."' },
      { t:'narrate', text:'She pushed the bowl an inch away from her.' },
      { t:'jump', scene:'vol7_ch8_the_apology' },
    ]
  },

  vol7_ch8_the_apology: {
    id: 'vol7_ch8_the_apology', vol: 7, chapter: 7, type: 'chapter',
    title: "Ch 7 — The Apology",
    nodes: [
      { t:'say', char:'Tem', expr:'neutral', text:'"I have known for two years that the patches were going to start showing up. I have known for two years that the tower was leaking. I have known for two years that Brandon Tillman had been investigating Nate Dean and that I had been pulled into the work by the bench at the museum and by what Brandon told me. I did not, in the two years, tell any of you. I told myself I was waiting for the work to be ready to share. The work was not the thing that needed to be ready. I was the thing that needed to be ready."' },
      { t:'say', char:'Tem', expr:'hurt', text:'"I was not ready because being ready meant admitting I did not know what I was doing and I had decided I was the kind of person who only spoke about a thing when she knew what she was doing. That decision was wrong. The decision was wrong from the beginning. I made all of you wait, and I made Cale wait, and I made the patches wait, and the whole time I was not protecting anybody from anything. I was protecting my image of myself as the person who could carry a thing well. The image was what I was carrying. The image was what was heavy. I am sorry."' },
      { t:'narrate', text:'She did not, when she was done, look at any of them.' },
      { t:'narrate', text:'The four of them sat at the table.' },
      { t:'narrate', text:'After a count Kai said, "Tem."' },
      { t:'say', char:'Tem', expr:'neutral', text:'"Yeah."' },
      { t:'say', char:'Kai', expr:'neutral', text:'"I\'m going to push back on you a little. You can take it or not."' },
      { t:'say', char:'Tem', expr:'neutral', text:'"Take it."' },
      { t:'say', char:'Kai', expr:'neutral', text:'"Some of what you just said is true. The image-protecting part is true. I have watched you do that for the two years I have known you and I have, on a couple of occasions, thought you were doing it and not said anything. I am going to start saying something. That part, the apology is good. I take it."' },
      { t:'say', char:'Kai', expr:'neutral', text:'"The other part — the part where you say you made all of us wait and you made Cale wait and you made the patches wait — that part is too much. You did not make the patches wait. The patches are not on a schedule you set. You did not make Cale wait. Cale told Lena he was tired of waiting. He chose to wait. He could have come to any of us at any point in the last two years and he didn\'t, and that\'s on him as much as it\'s on you. You do not get to take that on."' },
      { t:'say', char:'Kai', expr:'warm', text:'"You did make us wait. That part you can have. The rest — Tem. Stop. You\'re doing it again. The big apology is also a kind of image-protecting. It\'s the version where you are the person who can identify everything she did wrong and itemize it for the table. Don\'t itemize for us. We don\'t need the itemization. We just need you to be in the room."' },
      { t:'narrate', text:'Tem looked at him.' },
      { t:'choice', opts: [
        { text: 'Listen. Say nothing.', goto: 13 },
        { text: '"All right."', goto: 13 },
        { text: '[EMPATHY] She already knew. She\'s been waiting for someone to say it.', check: { skill: 'empathy', diff: 6 }, pass: 14, fail: 13 },
      ]},
      { t:'say', char:'Tem', expr:'softening', text:'"All right," she said.' },
      { t:'jump', scene:'vol7_ch8_finn_speaks' },
      { t:'think', char:'Lena', text:'She\'s been carrying this sentence in her mouth for weeks. Waiting for the room to be ready to hear it.' },
      { t:'say', char:'Tem', expr:'softening', text:'"All right," she said.' },
      { t:'jump', scene:'vol7_ch8_finn_speaks' },
    ]
  },

  vol7_ch8_finn_speaks: {
    id: 'vol7_ch8_finn_speaks', vol: 7, chapter: 7, type: 'chapter',
    title: "Ch 7 — Finn Speaks",
    nodes: [
      { t:'say', char:'Kai', expr:'neutral', text:'"I\'m not — I\'m not mad."' },
      { t:'say', char:'Tem', expr:'neutral', text:'"I know."' },
      { t:'say', char:'Kai', expr:'neutral', text:'"I\'m not. The Roy thing this morning is going to take me a minute to come down from. I am still hot. I want you to know my saying this is not me being hot. This is me trying to be honest with you the way you are trying to be honest with us."' },
      { t:'say', char:'Tem', expr:'neutral', text:'"Yes."' },
      { t:'show', char:'finn', expr:'neutral', pos:'left' },
      { t:'narrate', text:'Finn, who had been eating, set his spoon down.' },
      { t:'say', char:'Finn', expr:'neutral', text:'"Tem."' },
      { t:'say', char:'Tem', expr:'neutral', text:'"Yeah."' },
      { t:'say', char:'Finn', expr:'neutral', text:'"I want to add one thing to what Kai said, and then I\'m done."' },
      { t:'say', char:'Tem', expr:'neutral', text:'"Go."' },
      { t:'say', char:'Finn', expr:'neutral', text:'"You did not have to be ready by yourself. You decided you did. The deciding was not — Tem, the deciding was the loneliness. You have been lonely with this for two years and you didn\'t have to be. We were all here. You could have walked into Board Lords any day in 2050 and said Kai, something is happening with the patches, and he would have said all right, what do you need. You could have come into the Daily Grind and said the same thing to Lena. You didn\'t. You decided not to. The deciding was the thing."' },
      { t:'say', char:'Finn', expr:'neutral', text:'"I am not — I am not blaming you for the deciding. I have been quiet about my own things for years and I am not in any position to blame you. I am saying that the wait was lonely and the loneliness was a thing you chose, and I am sorry it took until this weekend for any of us to be in a room with you about it."' },
      { t:'narrate', text:'Tem was quiet for a long count.' },
      { t:'say', char:'Tem', expr:'softening', text:'She said, "Yeah, Finn."' },
      { t:'narrate', text:'She picked up her spoon. She finished the soup.' },
      { t:'flag', key:'vol7_ch7_apology_heard', val:true },
      { t:'jump', scene:'vol7_ch8_roy' },
    ]
  },

  vol7_ch8_roy: {
    id: 'vol7_ch8_roy', vol: 7, chapter: 7, type: 'chapter',
    title: "Ch 7 — Roy",
    nodes: [
      { t:'narrate', text:'They ate the rest in a quiet that was not the quiet of a held breath but the quiet of a meal getting eaten by four people who had said the things they needed to say to start eating again. Kai got up at one point and made tea. Finn cleared the bowls. Lena cut more bread. Tem sat at the table and watched all three of them moving through the kitchen and did not, for a count of about ten minutes, do anything but watch.' },
      { t:'narrate', text:'When the dishes were rinsed and stacked on the small drainer they moved back to the front room. Tem and Finn back on the couch. Kai back in the chair by the window. Lena pulled the kitchen chair into the room and sat in it.' },
      { t:'bg', src:'assets/backgrounds/vol7_lena_apartment_night.jpg' },
      { t:'show', char:'tem', expr:'neutral', pos:'left' },
      { t:'show', char:'kai', expr:'neutral', pos:'right' },
      { t:'say', char:'Lena', expr:'neutral', text:'"All right," Lena said. "Roy."' },
      { t:'say', char:'Kai', expr:'neutral', text:'"Roy."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"What did he say. Word for word."' },
      { t:'say', char:'Kai', expr:'neutral', text:'"I told you on the porch at the cabin. I told Tem. I\'ll tell it again. He came in at eleven-oh-six. Orange shirt under wax canvas. Boat shoes. Walked in like he\'d been in before. He hadn\'t. He said Kai? Roy Hummel. I see you at the Daily Grind. Lena makes me a hot chocolate sometimes. Sweet kid. That was the lead. He used Lena\'s name in the third sentence."' },
      { t:'say', char:'Kai', expr:'neutral', text:'"He said I\'m asking on behalf of someone. They wanted me to ask you something. I said who. He said doesn\'t matter who. I asked what he wanted. He said they want to know whether your friend Finn has been in possession of materials that belong to the museum-town historical society. I said what materials. He said they didn\'t say. I asked who\'s they. He said doesn\'t matter, just doing a favor. I said I didn\'t know."' },
      { t:'say', char:'Kai', expr:'calculating', text:'"He said all right, I\'ll tell them you don\'t know. He said have a nice Sunday, told me to say hi to Lena, and left."' },
      { t:'say', char:'Tem', expr:'cold', text:'"He used Lena\'s name twice."' },
      { t:'say', char:'Kai', expr:'neutral', text:'"Twice. Once in the lead and once on the way out."' },
      { t:'say', char:'Tem', expr:'cold', text:'"That\'s not a coincidence."' },
      { t:'say', char:'Kai', expr:'neutral', text:'"No."' },
      { t:'say', char:'Tem', expr:'cold', text:'"He was telling you he sees Lena. He was telling you what he could do with that if he wanted to."' },
      { t:'say', char:'Kai', expr:'neutral', text:'"Yes."' },
      { t:'say', char:'Lena', expr:'cold', text:'"Tem. Who is he."' },
      { t:'narrate', text:'Tem looked at her.' },
      { t:'say', char:'Tem', expr:'neutral', text:'"He\'s been here twenty-one years. He came up from somewhere south. He never says where. He has money he does not, on the surface, account for. He spends most of his days at the Daily Grind and the Charging Station. He talks to everyone. He is friendly to a degree that is not friendly. The locals over fifty have known him long enough to keep him at a polite distance. The locals under thirty have, since they were teenagers, registered him as a man you do not want to be alone with."' },
      { t:'say', char:'Kai', expr:'neutral', text:'"That\'s the surface," Kai said. "What\'s under it."' },
      { t:'say', char:'Tem', expr:'neutral', text:'"I don\'t know. Brandon thought he was a vessel."' },
      { t:'jump', scene:'vol7_ch8_the_vessel' },
    ]
  },

  vol7_ch8_the_vessel: {
    id: 'vol7_ch8_the_vessel', vol: 7, chapter: 7, type: 'chapter',
    title: "Ch 7 — The Vessel",
    nodes: [
      { t:'show', char:'finn', expr:'neutral', pos:'left' },
      { t:'say', char:'Kai', expr:'surprised', text:'"A what."' },
      { t:'say', char:'Tem', expr:'neutral', text:'"Brandon thought the substrate had been in him for a long time. Brandon thought Roy was a person whose actions were not fully his own. Brandon told me this once, the third time we met. He did not say more about it. He said I\'m telling you so that if I die before this is over, you know. That was March of 2050. Brandon died eight months later."' },
      { t:'say', char:'Finn', expr:'neutral', text:'"And Roy is asking after me."' },
      { t:'say', char:'Tem', expr:'neutral', text:'"Roy is asking after you because you have the wood. Or because somebody who knows about the wood is using Roy to ask. Or because the substrate that may be in Roy is reading you the way it reads anybody who has come into contact with the work, and the substrate wants the wood back. I don\'t know which of those is true. Possibly more than one. Possibly all three."' },
      { t:'say', char:'Kai', expr:'worried', text:'"Are we in danger."' },
      { t:'say', char:'Tem', expr:'neutral', text:'"I don\'t know."' },
      { t:'say', char:'Kai', expr:'cold', text:'"Tem."' },
      { t:'say', char:'Tem', expr:'neutral', text:'"Kai. I don\'t know. I would tell you if I did. The honest answer is I don\'t know. Brandon thought Roy was a vessel. Brandon also told me Roy had not, in twenty-one years in Smolvud, done anything that was provably illegal or provably violent. Brandon said the danger from Roy was not the danger of being attacked. It was the danger of being known by the wrong thing. I have been turning that sentence over in my head for two years. I still don\'t know what Brandon meant by it."' },
      { t:'say', char:'Finn', expr:'neutral', text:'"I think I do."' },
      { t:'narrate', text:'The three of them looked at him.' },
      { t:'say', char:'Finn', expr:'neutral', text:'"Being known by the wrong thing means the wrong thing knows you. If the substrate in Roy now knows the four of us — if Roy\'s visit to Kai today put the four of us on the substrate\'s map — then the substrate has us. It does not need to do anything to us. It just has to know we exist. Once the substrate has us, anything that is using the substrate as a routing layer has access to us. The danger is not Roy. The danger is that Roy is the small visible end of a very long and not-visible thing, and that thing has just learned our names."' },
      { t:'narrate', text:'The room was quiet for a count of ten.' },
      { t:'say', char:'Kai', expr:'neutral', text:'"Finn."' },
      { t:'say', char:'Finn', expr:'neutral', text:'"Yeah."' },
      { t:'say', char:'Kai', expr:'warm', text:'"That was the most you have said in two days."' },
      { t:'say', char:'Finn', expr:'neutral', text:'"Sorry."' },
      { t:'say', char:'Kai', expr:'warm', text:'"Don\'t be sorry. It was good."' },
      { t:'say', char:'Finn', expr:'neutral', text:'"All right."' },
      { t:'flag', key:'vol7_ch7_vessel_understood', val:true },
      { t:'jump', scene:'vol7_ch8_goodnight' },
    ]
  },

  vol7_ch8_goodnight: {
    id: 'vol7_ch8_goodnight', vol: 7, chapter: 7, type: 'chapter',
    title: "Ch 7 — Goodnight",
    nodes: [
      { t:'narrate', text:'It was past nine.' },
      { t:'narrate', text:'Lena looked at her phone on the side table and registered that they had been in the apartment for over three hours and that she was, by the kind of exhaustion that hits at the end of a long day in which people have said true things to each other in a small room, not going to be useful for any more thinking tonight. She said so.' },
      { t:'say', char:'Lena', expr:'tired', text:'"I am not going to be useful for any more thinking tonight."' },
      { t:'say', char:'Tem', expr:'tired', text:'"Same."' },
      { t:'say', char:'Kai', expr:'neutral', text:'"Same."' },
      { t:'show', char:'finn', expr:'neutral', pos:'left' },
      { t:'say', char:'Finn', expr:'neutral', text:'"I\'m fine to keep going if we need to."' },
      { t:'say', char:'Kai', expr:'warm', text:'"Finn. You\'re not. You haven\'t slept since Friday. You\'re saying you\'re fine because you don\'t know how to say you\'re not."' },
      { t:'narrate', text:'Finn said, after a beat, "Yeah."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"We sleep. We meet at the cabin tomorrow. Cale comes up. Five of us. We figure out the next thing then."' },
      { t:'say', char:'Tem', expr:'neutral', text:'"All right. The cabin at noon."' },
      { t:'say', char:'Kai', expr:'neutral', text:'"I\'ll close the shop tomorrow."' },
      { t:'say', char:'Tem', expr:'neutral', text:'"You don\'t have to."' },
      { t:'say', char:'Kai', expr:'neutral', text:'"I\'m closing it. I closed it today. The shop will be closed tomorrow. The shop will be closed until we know what we\'re doing."' },
      { t:'say', char:'Tem', expr:'neutral', text:'"All right."' },
      { t:'narrate', text:'There was a small shuffle at the door about who was driving back where. Kai said he would walk to the shop and pick up his truck and drive himself home. Finn said he would drop Tem at the cabin on his way to his apartment and come back down in the morning. Tem said she did not want to be at the cabin tonight.' },
      { t:'narrate', text:'The room paused on that.' },
      { t:'say', char:'Tem', expr:'neutral', text:'Tem said, "I want to stay here. If it\'s all right."' },
      { t:'narrate', text:'She said it to Lena.' },
      { t:'choice', opts: [
        { text: '"Yeah. Stay."', goto: 20 },
        { text: '[EMPATHY] You feel the ask in it — not just for a place to sleep.', check: { skill: 'empathy', diff: 5 }, pass: 20, fail: 20 },
      ]},
      { t:'say', char:'Lena', expr:'warm', text:'Lena said, "Yeah. Stay."' },
      { t:'narrate', text:'Kai and Finn took their coats off the hooks. Kai put a hand on Lena\'s shoulder again at the door, the same way he had on the way in. Finn looked at Tem for a long beat without saying anything and then at Lena and then back at Tem.' },
      { t:'say', char:'Finn', expr:'warm', text:'He said, "Take care of each other tonight."' },
      { t:'say', char:'Tem', expr:'warm', text:'Tem said, "Yeah, Finn."' },
      { t:'narrate', text:'He went down the stairwell. Kai followed. The door closed behind them. Lena turned the deadbolt. She had not, in three years in the apartment, locked the deadbolt at night. She locked it now.' },
      { t:'flag', key:'vol7_ch7_tem_stays', val:true },
      { t:'jump', scene:'vol7_ch8_dark' },
    ]
  },

  vol7_ch8_dark: {
    id: 'vol7_ch8_dark', vol: 7, chapter: 7, type: 'chapter',
    title: "Ch 7 — The Dark",
    nodes: [
      { t:'bg', src:'assets/backgrounds/vol7_lena_bedroom_dark.jpg' },
      { t:'bgm', src:'assets/audio/bgm/vol7_rain_on_roof.mp3' },
      { t:'narrate', text:'With two of them left in it the apartment was hers again.' },
      { t:'show', char:'tem', expr:'tired', pos:'center' },
      { t:'narrate', text:'Lena turned and looked at Tem who was standing by the couch with her wool sweater half-pulled over her head.' },
      { t:'say', char:'Lena', expr:'neutral', text:'"I\'m going to brush my teeth," Lena said. "There\'s a spare toothbrush in the bathroom in the small drawer. Help yourself."' },
      { t:'say', char:'Tem', expr:'tired', text:'"Thanks."' },
      { t:'say', char:'Lena', expr:'neutral', text:'"I changed the sheets this afternoon. The bed is — there\'s room. If you want."' },
      { t:'narrate', text:'Tem looked at her with the wool sweater bunched at her shoulders and her hair flat from the cap she had pulled off in the kitchen earlier and her face clean of any of the careful management she had been wearing all day.' },
      { t:'say', char:'Tem', expr:'softening', text:'"Yeah."' },
      { t:'say', char:'Lena', expr:'warm', text:'"Yeah."' },
      { t:'hide', pos:'center' },
      { t:'narrate', text:'She lay in the dark with Tem beside her and listened to the rain on the roof and to Tem\'s breathing slowing as Tem fell asleep. She did not sleep yet.' },
      { t:'think', char:'Lena', text:'She thought about Cale\'s face when she had been at his door — get going, Lena.' },
      { t:'think', char:'Lena', text:'She thought about Finn at the table saying the danger is that Roy is the small visible end of a very long and not-visible thing, and that thing has just learned our names.' },
      { t:'think', char:'Lena', text:'She thought about Kai\'s hand on her shoulder.' },
      { t:'think', char:'Lena', text:'She thought about the Estuary 7 stick in the inside pocket of the coat hanging on the hook by the door.' },
      { t:'think', char:'Lena', text:'She thought about how she had not, today, decided about Jorgen, and how she had not, today, gone to the studio, and how the painting was still on the wall of the studio with the one bone-black brushstroke in the upper-left and the rest unchanged.' },
      { t:'think', char:'Lena', text:"She thought about Tem's hand on her wrist on Thursday morning at the cabin." },
      { t:'narrate', text:'She turned on her side, away from Tem, and closed her eyes.' },
      { t:'narrate', text:'The rain on the roof did not change.' },
      { t:'narrate', text:'She slept.' },
      { t:'flag', key:'vol7_ch7_complete', val:true },
      { t:'end' },
    ]
  },

  // ── Chapters 9–23 stubs ──────────────────────────────────────────────────
  vol7_ch9_stub: {
    id: 'vol7_ch9_stub', nodes: [
      { t: 'narrate', text: '— Chapter 9 · The Cabin at Noon —' },
      { t: 'narrate', text: '[ Not yet written. ]' },
      { t: 'end' },
    ]
  },
  vol7_ch10_stub: { id: 'vol7_ch10_stub', nodes: [{ t: 'narrate', text: '— Chapter 10 · Cale Comes Up — [ Not yet written. ]' }, { t: 'end' }] },
  vol7_ch11_stub: { id: 'vol7_ch11_stub', nodes: [{ t: 'narrate', text: '— Chapter 11 · The Sixth Floor — [ Not yet written. ]' }, { t: 'end' }] },
  vol7_ch12_stub: { id: 'vol7_ch12_stub', nodes: [{ t: 'narrate', text: '— Chapter 12 · Pattern Persistence — [ Not yet written. ]' }, { t: 'end' }] },
  vol7_ch13_stub: { id: 'vol7_ch13_stub', nodes: [{ t: 'narrate', text: '— Chapter 13 · The Estuary 7 — [ Not yet written. ]' }, { t: 'end' }] },
  vol7_ch14_stub: { id: 'vol7_ch14_stub', nodes: [{ t: 'narrate', text: '— Chapter 14 · What Brandon Left — [ Not yet written. ]' }, { t: 'end' }] },
  vol7_ch15_stub: { id: 'vol7_ch15_stub', nodes: [{ t: 'narrate', text: '— Chapter 15 · The Wood at Midnight — [ Not yet written. ]' }, { t: 'end' }] },
  vol7_ch16_stub: { id: 'vol7_ch16_stub', nodes: [{ t: 'narrate', text: '— Chapter 16 · Monday — [ Not yet written. ]' }, { t: 'end' }] },
  vol7_ch17_stub: { id: 'vol7_ch17_stub', nodes: [{ t: 'narrate', text: '— Chapter 17 · The Bench — [ Not yet written. ]' }, { t: 'end' }] },
  vol7_ch18_stub: { id: 'vol7_ch18_stub', nodes: [{ t: 'narrate', text: '— Chapter 18 · Roy Again — [ Not yet written. ]' }, { t: 'end' }] },
  vol7_ch19_stub: { id: 'vol7_ch19_stub', nodes: [{ t: 'narrate', text: '— Chapter 19 · The Painting — [ Not yet written. ]' }, { t: 'end' }] },
  vol7_ch20_stub: { id: 'vol7_ch20_stub', nodes: [{ t: 'narrate', text: '— Chapter 20 · Jorgen — [ Not yet written. ]' }, { t: 'end' }] },
  vol7_ch21_stub: { id: 'vol7_ch21_stub', nodes: [{ t: 'narrate', text: '— Chapter 21 · The Substrate — [ Not yet written. ]' }, { t: 'end' }] },
  vol7_ch22_stub: { id: 'vol7_ch22_stub', nodes: [{ t: 'narrate', text: '— Chapter 22 · What the Crow Knows — [ Not yet written. ]' }, { t: 'end' }] },
  vol7_ch23_stub: { id: 'vol7_ch23_stub', nodes: [{ t: 'narrate', text: '— Chapter 23 · Land of Milk & Honey — [ Not yet written. ]' }, { t: 'end' }] },

};

// ── Pull editor-authored scenes into DEMO_SCENES at runtime ───────────────
(function() {
  try {
    const editorData = JSON.parse(localStorage.getItem('mm_editor_scenes') || 'null');
    if (!editorData) return;
    Object.values(editorData).forEach(volData => {
      Object.values(volData.scenes || {}).forEach(scene => {
        if (scene && scene.id && scene.nodes && scene.nodes.length > 0) {
          DEMO_SCENES[scene.id] = scene;
        }
      });
    });
  } catch(e) {}
})();

Object.assign(window, { DEMO_SCENES });
