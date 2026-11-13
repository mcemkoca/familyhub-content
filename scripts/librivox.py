#!/usr/bin/env python3
"""Free audiobooks for the FamilyHub kid library, collected automatically (no admin step).

Only LibriVox recordings hosted on archive.org are taken: LibriVox puts every recording in the public domain,
and the script still checks each item's licence URL before adding it. Audio is streamed by the app from
archive.org; nothing is re-hosted here.

  python3 scripts/librivox.py collect            # add up to MAX_NEW new items to content/library.json
  python3 scripts/librivox.py item <id> <band>   # print one entry (used when curating by hand)
"""
import json, re, sys, time, pathlib, urllib.request, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
LIB = ROOT / "content" / "library.json"
DENY = ROOT / "content" / "deny.txt"           # one archive.org id per line: never add (or remove) these
UA = {"User-Agent": "FamilyHub-content-bot (+https://github.com/mcemkoca/familyhub-content)"}
PD_LICENCES = ("creativecommons.org/licenses/publicdomain", "creativecommons.org/publicdomain/mark", "creativecommons.org/publicdomain/zero")
LANGS = {"nld": "nl", "dut": "nl", "fre": "fr", "fra": "fr", "eng": "en", "tur": "tr"}
MAX_NEW = 6                 # per weekly run, so the library grows steadily and every change is small
PER_QUERY = 2               # spread over languages
MAX_TRACKS = 120
MAX_HOURS = 20
# Words that keep an item out of a children's library (titles, subjects, description). Old books can carry
# outdated or violent themes; anything that matches is skipped, and deny.txt removes items for good.
BLOCK = re.compile(r"neger|nègre|negro|slave|slaven|slavernij|esclav|savage|sauvage|wilden|murder|moord|meurtre|horror|horreur|"
                   r"maupassant|zola|sade|baudelaire|verlaine|rimbaud|couperus|ghost stor|war |oorlog|guerre|crime|misdaad|erot|amour|liefde|love|vampir|bloed|blood|sang |death|dood|mort ", re.I)
# What the weekly run searches for: (archive.org query, age band, language)
QUERIES = [
    ('language:nld AND (subject:sprookjes OR subject:kinderboek OR subject:kinderen OR subject:jeugd OR title:sprookjes)', "6-12"),
    ('language:fre AND (subject:enfants OR subject:jeunesse OR title:enfants OR title:fables OR subject:"contes pour enfants" OR subject:"conte de fées")', "6-12"),
    ('language:eng AND (subject:"children\'s fiction" OR subject:aesop OR subject:"fairy tales" OR title:"fairy tales")', "6-12"),
    ('language:tur', "6-12"),
]

def get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return json.load(r)
        except Exception:
            if i == tries - 1: raise
            time.sleep(2 * (i + 1))

def seconds(v):
    if v is None: return 0
    s = str(v)
    if ":" in s:
        n = 0
        for part in s.split(":"): n = n * 60 + float(part or 0)
        return int(n)
    try: return int(float(s))
    except ValueError: return 0

def clean(s, n=200):
    s = re.sub(r"<[^>]+>", " ", s or ""); s = re.sub(r"\s+", " ", s).strip()
    return s[:n]

def item(identifier, band, premium=True, auto=False):
    """One library entry from archive.org metadata, or None if it does not pass the checks."""
    d = get("https://archive.org/metadata/" + urllib.parse.quote(identifier))
    m = d.get("metadata", {})
    lic = (m.get("licenseurl") or "").lower()
    if not any(x in lic for x in PD_LICENCES): return None
    if "librivoxaudio" not in (m.get("collection") or []): return None
    lang = m.get("language"); lang = lang[0] if isinstance(lang, list) else lang
    lang = LANGS.get((lang or "").lower())
    if not lang: return None
    files = [f for f in d.get("files", []) if f.get("name", "").endswith("_64kb.mp3")]
    files.sort(key=lambda f: f["name"])
    if not files or len(files) > MAX_TRACKS: return None
    title = clean(m.get("title"), 120); creator = m.get("creator"); creator = ", ".join(creator) if isinstance(creator, list) else (creator or "")
    subject = m.get("subject"); subject = "; ".join(subject) if isinstance(subject, list) else (subject or "")
    if BLOCK.search(" ".join([title, subject, creator, clean(m.get("description"), 600)])): return None
    tracks = [{"f": f["name"], "t": clean(f.get("title") or f["name"], 80), "s": seconds(f.get("length"))} for f in files]
    total = sum(t["s"] for t in tracks)
    if total > MAX_HOURS * 3600: return None
    e = {"id": "lv-" + re.sub(r"[^a-z0-9]+", "-", identifier.lower()).strip("-")[:48], "kind": "audio", "lang": lang, "bands": [band],
         "title": title, "author": clean(creator, 80), "minutes": max(1, round(total / 60)), "license": "public-domain",
         "source": "LibriVox · archive.org", "page": "https://archive.org/details/" + identifier,
         "base": "https://archive.org/download/" + identifier + "/", "tracks": tracks, "premium": premium}
    if auto: e["auto"] = True
    return e

def search(q, rows=50):
    url = "https://archive.org/advancedsearch.php?" + urllib.parse.urlencode(
        {"q": "collection:librivoxaudio AND (" + q + ")", "fl[]": "identifier", "rows": rows, "sort[]": "downloads desc", "output": "json"})
    return [d["identifier"] for d in get(url)["response"]["docs"]]

def collect():
    lib = json.loads(LIB.read_text(encoding="utf-8"))
    deny = {l.strip() for l in DENY.read_text().splitlines() if l.strip() and not l.startswith("#")} if DENY.exists() else set()
    have = {i.get("page", "").rsplit("/", 1)[-1] for i in lib["items"] if i.get("kind") == "audio"}
    before = len(lib["items"])
    lib["items"] = [i for i in lib["items"] if i.get("page", "").rsplit("/", 1)[-1] not in deny]
    added = []
    for q, band in QUERIES:
        n = 0
        for ident in search(q):
            if len(added) >= MAX_NEW or n >= PER_QUERY: break
            if ident in have or ident in deny: continue
            try: e = item(ident, band, premium=True, auto=True)
            except Exception as ex: print("skip", ident, ex); continue
            if e: lib["items"].append(e); added.append(ident); have.add(ident); n += 1
    if added or len(lib["items"]) != before:
        lib["checked"] = time.strftime("%Y-%m-%d")
        LIB.write_text(json.dumps(lib, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("added", len(added), added, "removed", before - (len(lib["items"]) - len(added)))
    return added

if __name__ == "__main__":
    if sys.argv[1:2] == ["collect"]: collect()
    elif sys.argv[1:2] == ["item"]: print(json.dumps(item(sys.argv[2], sys.argv[3], premium=len(sys.argv) < 5 or sys.argv[4] != "free"), ensure_ascii=False))
    else: print(__doc__)
