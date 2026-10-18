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
LEVELS = {"B2", "C1"}
ID_RE = re.compile(r"^[a-z]+-\d{2,}$")
CHUNK_RE = re.compile(r"^[A-Za-z0-9_\-.~:@+]{1,200}$")  # must be a valid db path segment
TOPICS = {"教育", "科技", "环境", "健康", "城市", "工作", "社会", "文化", "媒体", "科学"}


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
        for k in s.get("k", []):
            if len(k) != 3:
                errors.append(f"{where}: each chunk entry is [chunk_id, surface, gloss]")
                continue
            cid, surface, _ = k
            used.add(cid)
            if cid not in chunks:
                errors.append(f"{where}: chunk '{cid}' is not defined in 'chunks'")
            if surface not in en:
                errors.append(f"{where}: '{surface}' does not appear in the English sentence")
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
    n_s, n_c = len(bank["sentences"]), len(bank["chunks"])
    shared = sum(1 for c in bank["chunks"] if sum(c in [k[0] for k in s["k"]] for s in bank["sentences"]) > 1)
    print(f"{n_s} sentences, {n_c} chunks, {shared} chunks used in more than one sentence")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
