# 回译训练句库 — maintenance notes

A static GitHub Pages app (`index.html` + `bank.json`) for spaced-repetition back-translation drills. Progress lives in each viewer's browser (localStorage key `huiyi-v2`), keyed by **chunk id** and **sentence id**. Users read sentences in the bank and add them to their study library; review starts the next day.

## Goal of the content

Train **sentence-building ability at B1–B2**, not idiomatic polish. The learner's bottleneck is fitting an idea into an English sentence frame (`It is … for … to`, `so … that`, `those who`, `, which`, `One reason why … is that`, `too … to`, `not only … but also` …). Plain, correct English beats elegant English.

## Rules that protect saved progress

- Never rename or delete a sentence `id` or a chunk id once published. To take content out of circulation set `"retired": true`: it stays in the data, is hidden from the bank, and still reviews for anyone who already added it. The original 30 B2–C1 sentences are retired this way.
- New sentence ids continue the topic's numbering (check the highest existing id, retired ones included). Topic codes: edu tech env health city work soc cult media sci.
- Each `k` entry is `[chunk_id, surface, gloss]`. A frame with gaps is written with ` … ` (space, U+2026, space) between its literal parts, e.g. `"so … that"`; every part must appear in `en` in order, as whole words. The page turns each part into its own cloze blank.
- Chunk ids use letters, digits and `-` only. The chunk's `en` is the general pattern (`It is + 形容词 + for 人 + to do`); the per-sentence surface is the literal text.

## Content quality bar

- Level B1 or B2. 12–22 words, common vocabulary, one main clause plus at most one or two subordinate structures.
- Every sentence is built around 1–2 **frames**, plus at most one everyday collocation. Reuse existing frame chunk ids wherever they fit: a frame that recurs in 2–4 sentences on different topics is what makes review train the frame rather than one sentence. When adding a batch, prefer frames already in the bank that appear only once or twice.
- `zh`: natural Chinese a learner would think in, so the frame has to be found, not copied.
- `trap`: the sentence a B1 learner really writes (missing who, although…but, sb is difficult to, spend…to do, comma splice).
- `tip`: one or two lines naming the sentence-building move. Add `alts` when a simpler structure is equally correct.
- `tech` tags are structure categories: 形式主语 it, 定语从句, 名词从句, 让步从句, 条件从句, 结果与目的, 比较结构, 并列与递进, 动词句型, 非谓语, 被动语态, 主谓一致.
- British spelling (`-ise`, `travelling`); the page's matcher accepts US spellings for `-isation`, `ageing`, `fuelled`.

## Before every commit

```
python tools/check_bank.py --against <previous bank.json>
```

It must exit 0. Then bump `updated` in `bank.json`.

## Code changes

`index.html` must keep working with no server besides static hosting. It detects Claude's artifact runtime (`window.claude`) and otherwise uses localStorage with export/import backup in the 进度 tab.
