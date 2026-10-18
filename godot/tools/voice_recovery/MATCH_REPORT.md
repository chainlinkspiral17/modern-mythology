# Voice IDs recovered from the recordings (2026-10-18)

Each character's recorded lines (`samples/`) were matched against the preview clip of every voice in the ElevenLabs
workspace with a speaker-embedding model (Resemblyzer). **score** = how alike the character's lines and the voice are
(1.0 = identical); **margin** = how far ahead of the next-best voice. Checked first on vol 5: 314 of 321 lines landed on
their own character, and the voices named for characters (Alberto, Jimmy Daigle, Sam Miller, John Frank, Quentin Paul,
Dante, Erica, Gloria, Jen, maya teenage, stranger, daemon1) all landed on them.

- **sure** (score ≥ 0.85, margin ≥ 0.05, every line agrees): written into voice_map.json.
- **likely** / **listen**: NOT written. Audition the candidates in the voice studio and paste the right one.
- **narrator-fallback**: the lines used the narrator's voice; the character was never cast.
- 22 of the 116 workspace voices had no preview the cloud could fetch; a character cast with one of them reads "listen"
  until the next pack brings those previews.

## Vol 6

| character | tier | match (score · margin) | next candidates |
|---|---|---|---|
| `abuela` | sure ✓ saved | **Grandma Aurora** `aYQAm4rWuigkeuRA5i92` (0.88 · 0.096) | Fena `BlgEcC0TfWpBak7FmvHW` 0.79 · Bella `hpp4J3VqNfWAUOO0d1Us` 0.76 |
| `ben` | sure ✓ saved | **Philip** `uSR22n7NxaTMu8t6Y3XA` (0.88 · 0.078) | Alan James `rNCpBDykmtbS99HIj7Ku` 0.80 · Ben `bAy7UYgFEN38Rel2l1eW` 0.79 |
| `carlos` | sure ✓ saved | **Oliver** `gZgeCxzVQJzACoAiZkVF` (0.87 · 0.145) | Brian Nguyen `bP8FJDHmWVEgXJDitdQd` 0.73 · Greg's Driving Tours App and WalknTours `GlLKN8gKPpScsRIImeN1` 0.71 |
| `claire` | sure ✓ saved | **Natasha** `30Bu3NdpCkBMOF2yyBwC` (0.90 · 0.175) | Shannon `GP1bgf0sjoFuuHkyrg8E` 0.72 · Carol `5u41aNhyCU6hXOcjPPv0` 0.72 |
| `coach_dale` | sure ✓ saved | **Jamie** `K3Ks4ke16Al1uadpOim6` (0.88 · 0.112) | Philip `uSR22n7NxaTMu8t6Y3XA` 0.77 · Michael `iPYqcpY8j8Ap4jUf28I3` 0.75 |
| `coach_k` | sure ✓ saved | **Hank Turner** `2gfDLuf2nZfSrUuWQo1W` (0.92 · 0.156) | Callum `N2lVS1w4EtoT3dr4eOWO` 0.77 · Reginald `Hjzqw9NR0xFMYU9Us0DL` 0.75 |
| `curtis` | sure ✓ saved | **Alan James** `rNCpBDykmtbS99HIj7Ku` (0.87 · 0.081) | Philip `uSR22n7NxaTMu8t6Y3XA` 0.79 · Brian Nguyen `bP8FJDHmWVEgXJDitdQd` 0.78 |
| `dean` | sure ✓ saved | **Dickens Dean** `g8ApuJjVHqj6mZHTWMMq` (0.89 · 0.104) | Kai `JzzBiaudAeJ66VYEoGLw` 0.78 · John Frank `2CZ8eMKC4NY5H5l4mA3t` 0.77 |
| `doug` | sure ✓ saved | **Derek** `Q0Et7LOU7VpeoeCRQAVS` (0.91 · 0.111) | Haven Sands `x8xv0H8Ako6Iw3cKXLoC` 0.80 · marcus `GZQASZOiepkmMNLGnxqT` 0.78 |
| `doyle` | sure ✓ saved | **Alan James** `rNCpBDykmtbS99HIj7Ku` (0.86 · 0.074) | Philip `uSR22n7NxaTMu8t6Y3XA` 0.79 · Brian Nguyen `bP8FJDHmWVEgXJDitdQd` 0.76 |
| `em` | sure ✓ saved | **Shannon B** `wVOQaU8CfoRJqCWsxoLv` (0.94 · 0.113) | Shannon `GP1bgf0sjoFuuHkyrg8E` 0.82 · maya teenage `FQa9Cmg4i9Y2IyaeFgKc` 0.71 |
| `graciela` | sure ✓ saved | **Grandma Aurora** `aYQAm4rWuigkeuRA5i92` (0.91 · 0.132) | Fena `BlgEcC0TfWpBak7FmvHW` 0.78 · Major Arcana Narrator `t7JYIPCZ9tqGj3BqKOaA` 0.76 |
| `grandmother` | sure ✓ saved | **Carol** `5u41aNhyCU6hXOcjPPv0` (0.88 · 0.068) | Narrator 1 `WptDijZASNZGP7KRiviI` 0.81 · Maryanne  `rCuVrCHOUMY3OwyJBJym` 0.81 |
| `jen` | sure ✓ saved | **Jen** `guKlFPMQ7685DwAiM2Go` (0.94 · 0.098) | Amy `OZxMHsGaBmV5pjMIDIn0` 0.84 · Jessica `cgSgspJ2msm6clMCkdW9` 0.84 |
| `jesse` | sure ✓ saved | **Brayden** `3XOBzXhnDY98yeWQ3GdM` (0.87 · 0.067) | Haven Sands `x8xv0H8Ako6Iw3cKXLoC` 0.80 · marcus `GZQASZOiepkmMNLGnxqT` 0.78 |
| `linda` | sure ✓ saved | **Carol** `5u41aNhyCU6hXOcjPPv0` (0.88 · 0.054) | Gloria `oyb5orKqAKJ5eF5JhVmx` 0.82 · Maryanne  `rCuVrCHOUMY3OwyJBJym` 0.78 |
| `lucy` | sure ✓ saved | **Amanda Beans** `QzgYVYSNBgksoEWDkpKt` (0.87 · 0.097) | Bella `hpp4J3VqNfWAUOO0d1Us` 0.78 · Samantha "Sam" Miller `1f9RnWpv02KEl4foblDC` 0.74 |
| `marcus` | sure ✓ saved | **Ben** `bAy7UYgFEN38Rel2l1eW` (0.93 · 0.118) | Alan James `rNCpBDykmtbS99HIj7Ku` 0.81 · Philip `uSR22n7NxaTMu8t6Y3XA` 0.81 |
| `marisol` | sure ✓ saved | **Maryanne ** `rCuVrCHOUMY3OwyJBJym` (0.85 · 0.068) | Narrator 1 `WptDijZASNZGP7KRiviI` 0.79 · Shannon `GP1bgf0sjoFuuHkyrg8E` 0.74 |
| `maya` | sure ✓ saved | **maya teenage** `FQa9Cmg4i9Y2IyaeFgKc` (0.92 · 0.074) | Jen `guKlFPMQ7685DwAiM2Go` 0.84 · Bella `hpp4J3VqNfWAUOO0d1Us` 0.82 |
| `mrs_miller` | sure ✓ saved | **Amy** `OZxMHsGaBmV5pjMIDIn0` (0.85 · 0.062) | Brielle `6u6JbqKdaQy89ENzLSju` 0.79 · Jen `guKlFPMQ7685DwAiM2Go` 0.79 |
| `ramirez` | sure ✓ saved | **Jamie** `K3Ks4ke16Al1uadpOim6` (0.91 · 0.124) | Philip `uSR22n7NxaTMu8t6Y3XA` 0.79 · Michael `iPYqcpY8j8Ap4jUf28I3` 0.74 |
| `sam` | sure ✓ saved | **Samantha "Sam" Miller** `1f9RnWpv02KEl4foblDC` (0.94 · 0.109) | Jen `guKlFPMQ7685DwAiM2Go` 0.83 · Erica `vynY2D82MfA7Y5aWEKrI` 0.81 |
| `sams_mother` | sure ✓ saved | **Natasha** `30Bu3NdpCkBMOF2yyBwC` (0.90 · 0.146) | Shannon `GP1bgf0sjoFuuHkyrg8E` 0.76 · Joanna `QV8QyG5ShhK7cQDmlkPk` 0.72 |
| `tom_bell` | sure ✓ saved | **Alan James** `rNCpBDykmtbS99HIj7Ku` (0.89 · 0.079) | Philip `uSR22n7NxaTMu8t6Y3XA` 0.81 · Burt `kdVjFjOXaqExaDvXZECX` 0.80 |
| `_walkon_older` | likely | **Brielle** `6u6JbqKdaQy89ENzLSju` (0.84 · 0.054) | Amy `OZxMHsGaBmV5pjMIDIn0` 0.78 · Mackenzie `njv3j93ZcaNKtVB1LQrd` 0.78 |
| `bianca` | likely | **Amy** `OZxMHsGaBmV5pjMIDIn0` (0.87 · 0.045) | Jen `guKlFPMQ7685DwAiM2Go` 0.83 · Brielle `6u6JbqKdaQy89ENzLSju` 0.79 |
| `bill` | likely | **Philip** `uSR22n7NxaTMu8t6Y3XA` (0.84 · 0.031) | Ben `bAy7UYgFEN38Rel2l1eW` 0.81 · Alberto `iHlehG75dGoTFETT7zgs` 0.75 |
| `boyd` | likely | **Russ** `HKFOb9iktHA85uKXydRT` (0.86 · 0.027) | Austin Knox V3 `Bj9UqZbhQsanLzgalpEG` 0.83 · Greg's Driving Tours App and WalknTours `GlLKN8gKPpScsRIImeN1` 0.78 |
| `brent` | likely | **James Adelaide** `pAsk6bF7z6dgt9LtmIaQ` (0.82 · 0.044) | Burt `kdVjFjOXaqExaDvXZECX` 0.77 · Alan James `rNCpBDykmtbS99HIj7Ku` 0.74 |
| `chess` | likely | **Matilda** `XrExE9yKIg1WjnnlVkGX` (0.81 · 0.074) | Alice `Xb7hH8MSUJpSbSDYk0k2` 0.73 · Jen `guKlFPMQ7685DwAiM2Go` 0.73 |
| `diego` | likely | **marcus** `GZQASZOiepkmMNLGnxqT` (0.82 · 0.054) | Narrator 1 `WptDijZASNZGP7KRiviI` 0.77 · stranger `ZaI19wteBAgemrNjTUIZ` 0.76 |
| `hal` | likely | **Dan** `a4CnuaYbALRvW39mDitg` (0.80 · 0.031) | Alan James `rNCpBDykmtbS99HIj7Ku` 0.77 · Philip `uSR22n7NxaTMu8t6Y3XA` 0.75 |
| `hugo` | likely | **Gerardo's cool Latin American voice** `NDcVpQJv7Naa7ZKrqtEk` (0.85 · 0.077) | Hank Turner `2gfDLuf2nZfSrUuWQo1W` 0.77 · Hector `EXLdHKbL14iAO216598v` 0.75 |
| `jessa` | likely | **Anne** `MnXdp1RrMFboJjgMtirI` (0.83 · 0.029) | Narrator 1 `WptDijZASNZGP7KRiviI` 0.80 · Matilda `XrExE9yKIg1WjnnlVkGX` 0.74 |
| `jim` | likely | **Philip** `uSR22n7NxaTMu8t6Y3XA` (0.80 · 0.046) | planned community narrator `im48kk7plYeLR9UMpQ2v` 0.76 · Quentin Paul `JOIR3Gn735OhwbPNlY07` 0.75 |
| `miriam` | likely | **Jen** `guKlFPMQ7685DwAiM2Go` (0.86 · 0.025) | Mackenzie `njv3j93ZcaNKtVB1LQrd` 0.83 · Samantha "Sam" Miller `1f9RnWpv02KEl4foblDC` 0.82 |
| `mr_henderson` | likely | **Philip** `uSR22n7NxaTMu8t6Y3XA` (0.85 · 0.051) | Ben `bAy7UYgFEN38Rel2l1eW` 0.80 · planned community narrator `im48kk7plYeLR9UMpQ2v` 0.75 |
| `ms_caldwell` | likely | **Carol** `5u41aNhyCU6hXOcjPPv0` (0.85 · 0.029) | Gloria `oyb5orKqAKJ5eF5JhVmx` 0.83 · Maryanne  `rCuVrCHOUMY3OwyJBJym` 0.80 |
| `stranger` | likely | **stranger** `ZaI19wteBAgemrNjTUIZ` (0.89 · 0.101) | Narrator 1 `WptDijZASNZGP7KRiviI` 0.79 · Major Arcana Narrator `t7JYIPCZ9tqGj3BqKOaA` 0.79 |
| `walt` | likely | **Declan Sage** `kqVT88a5QfII1HNAEPTJ` (0.82 · 0.031) | Oliver `gZgeCxzVQJzACoAiZkVF` 0.79 · Austin Knox V3 `Bj9UqZbhQsanLzgalpEG` 0.79 |
| `_narrator_vol6` | listen | **Brian Nguyen** `bP8FJDHmWVEgXJDitdQd` (0.85 · 0.015) | Alan James `rNCpBDykmtbS99HIj7Ku` 0.84 · planned community narrator `im48kk7plYeLR9UMpQ2v` 0.80 |
| `anita` | listen | **Shannon B** `wVOQaU8CfoRJqCWsxoLv` (0.85 · 0.014) | Shannon `GP1bgf0sjoFuuHkyrg8E` 0.84 · Joanna `QV8QyG5ShhK7cQDmlkPk` 0.76 |
| `anita_kowalski` | listen | **Annie-Beth** `c4TutCiAuWP4vwb1xebb` (0.72 · 0.035) | Amy `OZxMHsGaBmV5pjMIDIn0` 0.68 · Brielle `6u6JbqKdaQy89ENzLSju` 0.67 |
| `bill_kowalski` | listen | **Russ** `HKFOb9iktHA85uKXydRT` (0.79 · 0.009) | Oliver `gZgeCxzVQJzACoAiZkVF` 0.78 · Jimmy Daigle `8VRjudv5cnNTBFs8820G` 0.77 |
| `brenda` | listen | **Joanna** `QV8QyG5ShhK7cQDmlkPk` (0.70 · 0.003) | Sadie `bD9maNcCuQQS75DGuteM` 0.69 · Carol `5u41aNhyCU6hXOcjPPv0` 0.69 |
| `bt` | listen | **marcus** `GZQASZOiepkmMNLGnxqT` (0.78 · 0.016) | Shannon `GP1bgf0sjoFuuHkyrg8E` 0.77 · Shannon B `wVOQaU8CfoRJqCWsxoLv` 0.76 |
| `carl` | listen | **Reginald** `Hjzqw9NR0xFMYU9Us0DL` (0.77 · 0.010) | marcus `GZQASZOiepkmMNLGnxqT` 0.76 · Hector `EXLdHKbL14iAO216598v` 0.76 |
| `chief_miller` | listen | **Derek** `Q0Et7LOU7VpeoeCRQAVS` (0.74 · 0.013) | Oliver `gZgeCxzVQJzACoAiZkVF` 0.72 · Philip `uSR22n7NxaTMu8t6Y3XA` 0.71 |
| `delia` | listen | **Savvy** `ogwqBH5bbF03DSbNiRNN` (0.83 · 0.011) | Jen `guKlFPMQ7685DwAiM2Go` 0.82 · maya teenage `FQa9Cmg4i9Y2IyaeFgKc` 0.80 |
| `dr_patel` | listen | **stranger** `ZaI19wteBAgemrNjTUIZ` (0.74 · 0.008) | Tina `KrfvGW2D1x6nS5QnRj2q` 0.73 · Major Arcana Narrator `t7JYIPCZ9tqGj3BqKOaA` 0.72 |
| `eileen` | listen | **Maryanne ** `rCuVrCHOUMY3OwyJBJym` (0.79 · 0.017) | Elicia Duchane `dtA4A3WoehhgZyId34cH` 0.78 · Narrator 1 `WptDijZASNZGP7KRiviI` 0.77 |
| `eileen_henderson` | listen | **Alan James** `rNCpBDykmtbS99HIj7Ku` (0.83 · 0.005) | Brian Nguyen `bP8FJDHmWVEgXJDitdQd` 0.83 · planned community narrator `im48kk7plYeLR9UMpQ2v` 0.80 |
| `f_t` | listen | **Ben** `bAy7UYgFEN38Rel2l1eW` (0.83 · 0.012) | Chris `iP95p4xoKVk53GoZ742B` 0.82 · Hank Turner `2gfDLuf2nZfSrUuWQo1W` 0.79 |
| `frasier` | listen | **Ben** `bAy7UYgFEN38Rel2l1eW` (0.82 · 0.004) | Hank Turner `2gfDLuf2nZfSrUuWQo1W` 0.81 · Chris `iP95p4xoKVk53GoZ742B` 0.81 |
| `gracie` | listen | **Bella** `hpp4J3VqNfWAUOO0d1Us` (0.80 · 0.024) | maya teenage `FQa9Cmg4i9Y2IyaeFgKc` 0.78 · Jessica `cgSgspJ2msm6clMCkdW9` 0.76 |
| `graciela_ramos` | listen | **Grandma Aurora** `aYQAm4rWuigkeuRA5i92` (0.78 · 0.004) | marcus `GZQASZOiepkmMNLGnxqT` 0.77 · Fena `BlgEcC0TfWpBak7FmvHW` 0.77 |
| `henderson` | listen | **Burt** `kdVjFjOXaqExaDvXZECX` (0.73 · 0.034) | stranger `ZaI19wteBAgemrNjTUIZ` 0.69 · Kai `JzzBiaudAeJ66VYEoGLw` 0.69 |
| `judge` | listen | **Maryanne ** `rCuVrCHOUMY3OwyJBJym` (0.74 · 0.022) | Grandma Aurora `aYQAm4rWuigkeuRA5i92` 0.72 · Major Arcana Narrator `t7JYIPCZ9tqGj3BqKOaA` 0.67 |
| `linda_caldwell` | listen | **Carol** `5u41aNhyCU6hXOcjPPv0` (0.83 · 0.015) | Gloria `oyb5orKqAKJ5eF5JhVmx` 0.82 · Maryanne  `rCuVrCHOUMY3OwyJBJym` 0.78 |
| `m` | listen | **marcus** `GZQASZOiepkmMNLGnxqT` (0.80 · 0.015) | Brian Nguyen `bP8FJDHmWVEgXJDitdQd` 0.79 · Alan James `rNCpBDykmtbS99HIj7Ku` 0.78 |
| `mark` | listen | **Ben** `bAy7UYgFEN38Rel2l1eW` (0.79 · 0.049) | Chris `iP95p4xoKVk53GoZ742B` 0.74 · Dan `a4CnuaYbALRvW39mDitg` 0.72 |
| `mom` | listen | **marcus** `GZQASZOiepkmMNLGnxqT` (0.79 · 0.003) | Alan James `rNCpBDykmtbS99HIj7Ku` 0.79 · Brian Nguyen `bP8FJDHmWVEgXJDitdQd` 0.79 |
| `mrs_henderson` | listen | **Shannon B** `wVOQaU8CfoRJqCWsxoLv` (0.72 · 0.008) | maya teenage `FQa9Cmg4i9Y2IyaeFgKc` 0.72 · Natasha `30Bu3NdpCkBMOF2yyBwC` 0.71 |
| `nate` | listen | **Anatoly** `UgMQ92GJ3C3bUAtHUKyd` (0.79 · 0.090) | James Adelaide `pAsk6bF7z6dgt9LtmIaQ` 0.70 · Reginald `Hjzqw9NR0xFMYU9Us0DL` 0.68 |
| `pete` | listen | **Haven Sands** `x8xv0H8Ako6Iw3cKXLoC` (0.70 · 0.043) | Ben `bAy7UYgFEN38Rel2l1eW` 0.65 · Jamie `K3Ks4ke16Al1uadpOim6` 0.65 |
| `phil` | listen | **Oliver** `gZgeCxzVQJzACoAiZkVF` (0.83 · 0.002) | Philip `uSR22n7NxaTMu8t6Y3XA` 0.83 · Jamie `K3Ks4ke16Al1uadpOim6` 0.79 |
| `ramon` | listen | **Hank Turner** `2gfDLuf2nZfSrUuWQo1W` (0.76 · 0.082) | Chris `iP95p4xoKVk53GoZ742B` 0.68 · marcus `GZQASZOiepkmMNLGnxqT` 0.68 |
| `reporter` | listen | **Brian Nguyen** `bP8FJDHmWVEgXJDitdQd` (0.79 · 0.005) | Alan James `rNCpBDykmtbS99HIj7Ku` 0.78 · marcus `GZQASZOiepkmMNLGnxqT` 0.73 |
| `rick` | listen | **CL Smoot** `qiIL62sOWUkHwxfeC0u5` (0.78 · 0.053) | planned community narrator `im48kk7plYeLR9UMpQ2v` 0.73 · Josh `ZoiZ8fuDWInAcwPXaVeq` 0.72 |
| `russell` | listen | **Greg's Driving Tours App and WalknTours** `GlLKN8gKPpScsRIImeN1` (0.82 · 0.005) | Oliver `gZgeCxzVQJzACoAiZkVF` 0.82 · Derek `Q0Et7LOU7VpeoeCRQAVS` 0.78 |
| `sams_mom` | listen | **Natasha** `30Bu3NdpCkBMOF2yyBwC` (0.77 · 0.131) | Gloria `oyb5orKqAKJ5eF5JhVmx` 0.64 · Maryanne  `rCuVrCHOUMY3OwyJBJym` 0.63 |
| `sunburn_man` | listen | **Brian Nguyen** `bP8FJDHmWVEgXJDitdQd` (0.80 · 0.042) | planned community narrator `im48kk7plYeLR9UMpQ2v` 0.76 · marcus `GZQASZOiepkmMNLGnxqT` 0.76 |
| `tome` | listen | **Alberto** `iHlehG75dGoTFETT7zgs` (0.72 · 0.026) | planned community narrator `im48kk7plYeLR9UMpQ2v` 0.69 · Dr. John `iCCltpMulQlVWET3GYOx` 0.69 |
| `tucker` | listen | **Burt** `kdVjFjOXaqExaDvXZECX` (0.70 · 0.010) | Callum `N2lVS1w4EtoT3dr4eOWO` 0.69 · Brian Nguyen `bP8FJDHmWVEgXJDitdQd` 0.67 |
| `vince` | listen | **Alberto** `iHlehG75dGoTFETT7zgs` (0.81 · 0.006) | Michael `iPYqcpY8j8Ap4jUf28I3` 0.80 · Dan `a4CnuaYbALRvW39mDitg` 0.76 |
| `wren` | listen | **Maryanne ** `rCuVrCHOUMY3OwyJBJym` (0.76 · 0.010) | Grandma Aurora `aYQAm4rWuigkeuRA5i92` 0.75 · Lily `pFZP5JQG7iQjIQuC4Bku` 0.70 |
| `_walkon_child` | narrator-fallback | **Major Arcana Narrator** `t7JYIPCZ9tqGj3BqKOaA` (0.85 · 0.028) | Narrator 1 `WptDijZASNZGP7KRiviI` 0.82 · stranger `ZaI19wteBAgemrNjTUIZ` 0.80 |

## Other volumes

| character | tier | match (score · margin) | next candidates |
|---|---|---|---|
| `_narrator` | sure ✓ saved | **Major Arcana Narrator** `t7JYIPCZ9tqGj3BqKOaA` (0.93 · 0.150) | Grandma Aurora `aYQAm4rWuigkeuRA5i92` 0.78 · Alice `Xb7hH8MSUJpSbSDYk0k2` 0.77 |
| `_walkon_male` | sure ✓ saved | **marcus** `GZQASZOiepkmMNLGnxqT` (0.88 · 0.095) | Sarah `EXAVITQu4vr4xnSDxMaL` 0.78 · Carol `5u41aNhyCU6hXOcjPPv0` 0.77 |
| `alberto` | sure ✓ saved | **Alberto** `iHlehG75dGoTFETT7zgs` (0.91 · 0.133) | planned community narrator `im48kk7plYeLR9UMpQ2v` 0.78 · Hector `EXLdHKbL14iAO216598v` 0.77 |
| `dante` | sure ✓ saved | **Dante D'Ambrosio** `q0SAZTsRRakNDYQoTldc` (0.85 · 0.084) | John Frank `2CZ8eMKC4NY5H5l4mA3t` 0.77 · stranger `ZaI19wteBAgemrNjTUIZ` 0.75 |
| `gloria` | sure ✓ saved | **Gloria** `oyb5orKqAKJ5eF5JhVmx` (0.86 · 0.088) | Maryanne  `rCuVrCHOUMY3OwyJBJym` 0.77 · Grandma Aurora `aYQAm4rWuigkeuRA5i92` 0.77 |
| `jimmy` | sure ✓ saved | **Jimmy Daigle** `8VRjudv5cnNTBFs8820G` (0.97 · 0.138) | Sammy `G0RZSqf0FzZfBKnZHkqH` 0.83 · Austin Knox V3 `Bj9UqZbhQsanLzgalpEG` 0.79 |
| `john` | sure ✓ saved | **John Frank** `2CZ8eMKC4NY5H5l4mA3t` (0.92 · 0.084) | stranger `ZaI19wteBAgemrNjTUIZ` 0.84 · Kai `JzzBiaudAeJ66VYEoGLw` 0.83 |
| `philip` | sure ✓ saved | **Philip** `uSR22n7NxaTMu8t6Y3XA` (0.94 · 0.128) | Alan James `rNCpBDykmtbS99HIj7Ku` 0.81 · Ben `bAy7UYgFEN38Rel2l1eW` 0.79 |
| `quentin_paul` | sure ✓ saved | **Quentin Paul** `JOIR3Gn735OhwbPNlY07` (0.89 · 0.128) | stranger `ZaI19wteBAgemrNjTUIZ` 0.76 · Philip `uSR22n7NxaTMu8t6Y3XA` 0.71 |
| `sammy` | sure ✓ saved | **Sammy** `G0RZSqf0FzZfBKnZHkqH` (0.90 · 0.153) | Jimmy Daigle `8VRjudv5cnNTBFs8820G` 0.74 · stranger `ZaI19wteBAgemrNjTUIZ` 0.70 |
| `the_demon` | sure ✓ saved | **daemon1** `8BuXYUd73q1TWK0pQzvR` (0.93 · 0.169) | Fena `BlgEcC0TfWpBak7FmvHW` 0.76 · Grandma Aurora `aYQAm4rWuigkeuRA5i92` 0.72 |
| `antonio` | likely | **Hank Turner** `2gfDLuf2nZfSrUuWQo1W` (0.83 · 0.041) | Chris `iP95p4xoKVk53GoZ742B` 0.78 · Alberto `iHlehG75dGoTFETT7zgs` 0.77 |
| `elicia` | likely | **Elicia Duchane** `dtA4A3WoehhgZyId34cH` (0.91 · 0.025) | Samantha "Sam" Miller `1f9RnWpv02KEl4foblDC` 0.88 · Narrator 1 `WptDijZASNZGP7KRiviI` 0.88 |
| `erica` | likely | **Erica** `vynY2D82MfA7Y5aWEKrI` (0.92 · 0.079) | Samantha "Sam" Miller `1f9RnWpv02KEl4foblDC` 0.84 · Jen `guKlFPMQ7685DwAiM2Go` 0.79 |
| `mackenzie` | likely | **Mackenzie** `njv3j93ZcaNKtVB1LQrd` (0.83 · 0.041) | Maryanne  `rCuVrCHOUMY3OwyJBJym` 0.79 · Gloria `oyb5orKqAKJ5eF5JhVmx` 0.77 |
| `the_frog` | likely | **Ben** `bAy7UYgFEN38Rel2l1eW` (0.85 · 0.039) | Chris `iP95p4xoKVk53GoZ742B` 0.81 · Philip `uSR22n7NxaTMu8t6Y3XA` 0.77 |
| `aria` | listen | **Narrator 1** `WptDijZASNZGP7KRiviI` (0.87 · 0.057) | Elicia Duchane `dtA4A3WoehhgZyId34cH` 0.82 · Sarah `EXAVITQu4vr4xnSDxMaL` 0.81 |
| `hector` | listen | **Hector** `EXLdHKbL14iAO216598v` (0.74 · 0.086) | JM `EkK5I93UQWFDigLMpZcX` 0.65 · Eric `cjVigY5qzO86Huf0OWal` 0.62 |
| `joanna` | listen | **Joanna** `QV8QyG5ShhK7cQDmlkPk` (0.82 · 0.005) | Sarah `EXAVITQu4vr4xnSDxMaL` 0.82 · Narrator 1 `WptDijZASNZGP7KRiviI` 0.80 |
| `natalie` | listen | **Mackenzie** `njv3j93ZcaNKtVB1LQrd` (0.85 · 0.012) | Jen `guKlFPMQ7685DwAiM2Go` 0.84 · Samantha "Sam" Miller `1f9RnWpv02KEl4foblDC` 0.83 |
| `nicola` | listen | **Mackenzie** `njv3j93ZcaNKtVB1LQrd` (0.77 · 0.018) | Fena `BlgEcC0TfWpBak7FmvHW` 0.75 · daemon1 `8BuXYUd73q1TWK0pQzvR` 0.74 |
| `the_child` | listen | **Mackenzie** `njv3j93ZcaNKtVB1LQrd` (0.81 · 0.011) | Bella `hpp4J3VqNfWAUOO0d1Us` 0.80 · Maryanne  `rCuVrCHOUMY3OwyJBJym` 0.76 |
| `the_third_consciousness` | listen | **Joanna** `QV8QyG5ShhK7cQDmlkPk` (0.83 · 0.021) | Bella `hpp4J3VqNfWAUOO0d1Us` 0.81 · Sarah `EXAVITQu4vr4xnSDxMaL` 0.81 |
| `_walkon_female` | narrator-fallback | **Major Arcana Narrator** `t7JYIPCZ9tqGj3BqKOaA` (0.90 · 0.149) | Narrator 1 `WptDijZASNZGP7KRiviI` 0.75 · Gloria `oyb5orKqAKJ5eF5JhVmx` 0.74 |
| `anya` | narrator-fallback | **Major Arcana Narrator** `t7JYIPCZ9tqGj3BqKOaA` (0.93 · 0.157) | Maryanne  `rCuVrCHOUMY3OwyJBJym` 0.78 · Gloria `oyb5orKqAKJ5eF5JhVmx` 0.78 |
| `jordan` | narrator-fallback | **Major Arcana Narrator** `t7JYIPCZ9tqGj3BqKOaA` (0.75 · 0.055) | Gloria `oyb5orKqAKJ5eF5JhVmx` 0.69 · Grandma Aurora `aYQAm4rWuigkeuRA5i92` 0.65 |

