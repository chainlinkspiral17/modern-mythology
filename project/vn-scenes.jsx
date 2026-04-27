// vn-scenes.jsx — Demo scene content for Modern Mythology volumes
// Scene node types: narrate, say, think, choice, show, hide, bg, bgm, sfx, flag, jump, end
// goto: node index | scene id string
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

  // ── Vol 2 · SMALL WOOD VOLUMES · Literary skin ──────────────────────────
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
};

Object.assign(window, { DEMO_SCENES });
