# 回译训练句库 — maintenance notes

A static GitHub Pages app (`index.html` + `bank.json`) for spaced-repetition back-translation drills. Progress lives in each viewer's browser (localStorage key `huiyi-v2`), keyed by **chunk id** and **sentence id**.

## Rules that protect saved progress

- Never rename or delete a sentence `id` or a chunk id once published. To retire content, leave it in place; to fix wording, edit `zh`/`en`/`trap`/`tip`/glosses in place.
- When a new sentence reuses an existing collocation, reference the existing chunk id. Sharing chunks across sentences is the point: review rotates example sentences per chunk.
- New sentence ids continue the topic's numbering (`env-04`, `env-05`, …). Topic codes: edu tech env health city work soc cult media sci.
- Each `k` entry is `[chunk_id, surface, gloss]`; `surface` must appear verbatim in `en`. Chunk ids use letters, digits and `-` only.
- British spelling in reference sentences (`-isation`, `ageing`, `fuelled`); the checker's matcher already normalises these against US spellings.

## Before every commit

```
python tools/check_bank.py --against <previous bank.json>
```

It must exit 0. Then bump `updated` in `bank.json`.

## Content quality bar

B2–C1 sentences a native writer would actually produce in an IELTS Task 2 / PTE essay; collocations that are genuinely frequent; a realistic Chinglish `trap` version; a one-line `tip` naming the translation technique. Add `alts` when another natural rendering exists.

## Code changes

`index.html` must keep working with no server besides static hosting. It detects Claude's artifact runtime (`window.claude`) and otherwise uses localStorage with export/import backup in the 进度 tab.
