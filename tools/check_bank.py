"""Validate bank.json before committing.

Usage:
    python tools/check_bank.py                 # check bank.json
    python tools/check_bank.py --against OLD   # also check that no ids from an older bank.json were removed

Exit code 0 means the bank is safe to publish.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEVELS = {"B1", "B2", "C1"}  # C1 only on retired sentences
SEP = " … "  # gap marker inside a frame surface, e.g. "so … that"


def find_parts(en, surface):
    """Locate each literal part of a surface in order, on word boundaries. Returns spans or None."""
    pos, spans = 0, []
    for part in surface.split(SEP):
        pre = r"(?<![A-Za-z])" if part[:1].isalpha() else ""
        post = r"(?![A-Za-z])" if part[-1:].isalpha() else ""
        m = re.compile(pre + re.escape(part) + post).search(en, pos)
        if not m:
            return None
        spans.append(m.span())
        pos = m.end()
    return spans
ID_RE = re.compile(r"^[a-z]+-\d{2,}$")
CHUNK_RE = re.compile(r"^[A-Za-z0-9_\-.~:@+]{1,200}$")  # must be a valid db path segment
TOPICS = {"教育", "科技", "环境", "健康", "城市", "工作", "社会", "文化", "媒体", "科学"}
TECHS = {"形式主语 it", "定语从句", "名词从句", "让步从句", "条件从句", "结果与目的", "比较结构",
         "并列与递进", "动词句型", "非谓语", "被动语态", "主谓一致"}


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def check(bank):
    errors, warnings = [], []
    chunks, sents = bank.get("chunks", {}), bank.get("sentences", [])
    if not isinstance(chunks, dict) or not isinstance(sents, list):
        return ["bank.json must have a 'chunks' object and a 'sentences' list"], []

    for cid, c in chunks.items():
        if not CHUNK_RE.match(cid):
            errors.append(f"chunk id '{cid}' has characters the progress store cannot use")
        if not c.get("en") or not c.get("zh"):
            errors.append(f"chunk '{cid}' needs both 'en' and 'zh'")

    seen, used, zh_seen = set(), set(), {}
    for s in sents:
        sid = s.get("id", "?")
        where = f"sentence {sid}"
        if not ID_RE.match(sid):
            errors.append(f"{where}: id should look like 'env-12'")
        if sid in seen:
            errors.append(f"{where}: duplicate id")
        seen.add(sid)
        for field in ("t", "lv", "tech", "zh", "en", "k", "trap", "tip"):
            if not s.get(field):
                errors.append(f"{where}: missing '{field}'")
        if s.get("lv") not in LEVELS:
            errors.append(f"{where}: level must be one of {sorted(LEVELS)}")
        if s.get("t") and s["t"] not in TOPICS:
            warnings.append(f"{where}: new topic '{s['t']}' (fine, but check the spelling)")
        en = s.get("en", "")
        spans_all = []
        for k in s.get("k", []):
            if len(k) == 3 and find_parts(en, k[1]):
                spans_all += [(a, b, k[0]) for a, b in find_parts(en, k[1])]
        spans_all.sort()
        for (a1, b1, c1), (a2, b2, c2) in zip(spans_all, spans_all[1:]):
            if a2 < b1:
                errors.append(f"{where}: chunks '{c1}' and '{c2}' overlap in the sentence; highlighting and cloze need them apart")
        for k in s.get("k", []):
            if len(k) != 3:
                errors.append(f"{where}: each chunk entry is [chunk_id, surface, gloss]")
                continue
            cid, surface, _ = k
            used.add(cid)
            if cid not in chunks:
                errors.append(f"{where}: chunk '{cid}' is not defined in 'chunks'")
            if find_parts(en, surface) is None:
                errors.append(f"{where}: '{surface}' does not appear (in order, as whole words) in the English sentence")
        if not s.get("retired"):
            for t in s.get("tech", []):
                if t not in TECHS:
                    warnings.append(f"{where}: structure tag '{t}' is not in the agreed list")
        if s.get("lv") == "C1" and not s.get("retired"):
            warnings.append(f"{where}: C1 sentence in the active set (target is B1–B2)")
        if not 2 <= len(s.get("k", [])) <= 5:
            warnings.append(f"{where}: has {len(s.get('k', []))} chunks (2-5 is the sweet spot)")
        zh = s.get("zh", "")
        if zh in zh_seen:
            errors.append(f"{where}: same Chinese text as {zh_seen[zh]}")
        zh_seen[zh] = sid

    for cid in chunks:
        if cid not in used:
            warnings.append(f"chunk '{cid}' is defined but no sentence uses it")
    return errors, warnings


def main():
    bank = load(ROOT / "bank.json")
    errors, warnings = check(bank)
    if "--against" in sys.argv:
        old = load(sys.argv[sys.argv.index("--against") + 1])
        gone_s = {s["id"] for s in old["sentences"]} - {s["id"] for s in bank["sentences"]}
        gone_c = set(old["chunks"]) - set(bank["chunks"])
        for sid in sorted(gone_s):
            errors.append(f"sentence id '{sid}' was removed; saved progress points at it")
        for cid in sorted(gone_c):
            errors.append(f"chunk id '{cid}' was removed or renamed; saved progress points at it")
    for w in warnings:
        print("warning:", w)
    for e in errors:
        print("ERROR:", e)
    active = [s for s in bank["sentences"] if not s.get("retired")]
    uses = {}
    for s in active:
        for k in s["k"]:
            uses[k[0]] = uses.get(k[0], 0) + 1
    shared = sum(1 for v in uses.values() if v > 1)
    print(f"{len(active)} active sentences ({len(bank['sentences']) - len(active)} retired), "
          f"{len(uses)} chunks in use, {shared} of them recur in 2+ sentences")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
