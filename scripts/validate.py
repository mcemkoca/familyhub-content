#!/usr/bin/env python3
"""Checks every content file before it can be published. Exit code 1 = do not publish."""
import json, sys, re, datetime, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent / "content"
ALLOWED = {"questions.json","skills.json","adventures.json","stories.json","emotions.json","recipes.json","levels.json","prompts.json",
           "activities.json","plans.json","belgium.json","money.json","rights.json","topics.json","turkish.json","savings.json",
           "calendar.json","life.json","learn.json","rules.json","lang.json","library.json","support.json","app.json"}
NON_JSON = {"deny.txt"}
BANDS = {"0-6", "6-12", "12-18"}
LANGS = {"tr", "nl", "fr", "en"}
# Gate for the fully automatic library: only these licences and hosts can ever reach a child's phone.
LICENCES = {"own", "public-domain", "link"}
AUDIO_HOST = "https://archive.org/download/"
LINK_HOSTS = ("https://www.trtcocuk.net.tr", "https://www.gutenberg.org/", "https://librivox.org", "https://childfocus.be", "https://safeonweb.be", "https://www.studentatwork.be")
UNSAFE = re.compile(r"neger|nègre|negro|slave|slavernij|esclav|murder|moord|meurtre|horror|horreur|erot|porn|vampir|casino|gokken|pari sportif", re.I)
EMOJI13 = set("🫁🪜🧑‍🍼🫶🛝🪟🪑🪐")
errors = []
def err(f, m): errors.append(f"{f}: {m}")
def date(f, s, where):
    try: return datetime.date.fromisoformat(s)
    except Exception: err(f, f"bad date {s!r} in {where}")
def url(f, u, where):
    if not isinstance(u, str) or not u.startswith("https://"): err(f, f"link must be https in {where}: {u!r}")
def unique(f, items, key="id"):
    ids = [i.get(key) for i in items]; d = {x for x in ids if ids.count(x) > 1}
    if d: err(f, f"duplicate ids {sorted(d)}")

for p in sorted(ROOT.iterdir()):
    if p.name in NON_JSON: continue
    f = p.name
    if f not in ALLOWED: err(f, "file name not allowed"); continue
    try: data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e: err(f, f"invalid JSON: {e}"); continue
    text = p.read_text(encoding="utf-8")
    if any(c in text for c in "🫁🪜🫶🛝🪟🪑🪐"): err(f, "uses Emoji 13+ that old phones cannot show")
    for m in re.finditer(r'"(?:url)"\s*:\s*"([^"]*)"', text): url(f, m.group(1), "url")
    if f == "calendar.json":
        kinds = {k["id"] for k in data["kinds"]}; unique(f, data["days"])
        for d in data["days"]:
            if d["kind"] not in kinds: err(f, f"unknown kind {d['kind']} ({d['id']})")
            a, b = date(f, d["start"], d["id"]), date(f, d["end"], d["id"])
            if a and b and b < a: err(f, f"end before start ({d['id']})")
    if f == "life.json":
        unique(f, data["items"])
        for i in data["items"]:
            if i["kind"] == "age" and not isinstance(i.get("months"), int): err(f, f"age rule without months ({i['id']})")
            if i["kind"] == "yearly":
                try: datetime.date(2028, i["month"], i["day"])
                except Exception: err(f, f"bad month/day ({i['id']})")
            if i["kind"] not in ("age", "yearly"): err(f, f"unknown kind ({i['id']})")
    if f == "learn.json":
        groups = {g["id"] for g in data["groups"]}; unique(f, data["items"])
        for i in data["items"]:
            if i["group"] not in groups: err(f, f"unknown group ({i['id']})")
            if i["type"] not in ("site", "search", "video", "playlist"): err(f, f"unknown type ({i['id']})")
    if f == "rights.json":
        unique(f, data["items"])
        secs = {s["id"] for s in data["sections"]}
        for i in data["items"]:
            if i["section"] not in secs: err(f, f"unknown section ({i['id']})")
    if f == "rules.json":
        unique(f, data["rules"]); date(f, data["checked"], "checked")
        pk = {"health","carhome","admin","letters","school","kids","money","remote","travel","menu"}
        for r in data["rules"]:
            rid = r.get("id")
            if r.get("pkg") not in pk: err(f, f"unknown pkg ({rid})")
            if r.get("kind") not in ("interval","user","dates","yearly","info"): err(f, f"unknown kind ({rid})")
            if r.get("kind") != "user" and not (r.get("source") or {}).get("url","").startswith("https://"): err(f, f"official rule without https source ({rid})")
            for k, v in (r.get("months") or {}).items():
                if k not in ("all","flanders","brussels","wallonia") or not isinstance(v, int) or v <= 0: err(f, f"bad months {k}={v} ({rid})")
            for d in r.get("dates", []): date(f, d["day"], rid)
            if r.get("kind") == "yearly":
                try: datetime.date(2028, r["month"], r["day"])
                except Exception: err(f, f"bad month/day ({rid})")
            if r.get("kind") == "interval" and not r.get("months"): err(f, f"interval without months ({rid})")
    if f == "lang.json":
        unique(f, data["units"]); unique(f, data["idioms"])
        pids = [ph["id"] for u in data["units"] for ph in u["phrases"]]
        if len(pids) != len(set(pids)): err(f, "duplicate phrase ids")
        levels = {l["id"] for l in data["levels"]}; langs = {l["id"] for l in data["langs"]}
        for u in data["units"]:
            if u["level"] not in levels or u["lang"] not in langs: err(f, f"bad level/lang ({u['id']})")
            if len(u["phrases"]) < 5: err(f, f"unit needs 5+ phrases ({u['id']})")
            for ph in u["phrases"]:
                if not ph["t"].strip() or not ph["tr"].strip(): err(f, f"empty phrase ({ph['id']})")
        for i in data["idioms"]:
            if i["lang"] not in langs: err(f, f"bad idiom lang ({i['id']})")
    if f == "library.json":
        unique(f, data["items"])
        if {b["id"] for b in data["bands"]} != BANDS: err(f, "bands must be 0-6, 6-12, 12-18")
        for i in data["items"]:
            iid = i.get("id")
            if not i.get("bands") or any(b not in BANDS for b in i["bands"]): err(f, f"age band missing/unknown ({iid})")
            if i.get("lang") not in LANGS: err(f, f"unknown lang ({iid})")
            if i.get("license") not in LICENCES: err(f, f"licence not allowed ({iid})")
            if UNSAFE.search(" ".join([i.get("title", ""), i.get("author", "")] + i.get("text", []))): err(f, f"blocked word for a children's library ({iid})")
            k = i.get("kind")
            if k == "audio":
                if i.get("license") != "public-domain": err(f, f"audio must be public domain ({iid})")
                if not i.get("base", "").startswith(AUDIO_HOST): err(f, f"audio must stream from archive.org ({iid})")
                if not i.get("tracks") or any(not t["f"].endswith(".mp3") or "/" in t["f"] for t in i["tracks"]): err(f, f"bad tracks ({iid})")
            elif k in ("story", "guide"):
                if i.get("license") != "own" or len(i.get("text", [])) < 3: err(f, f"story/guide must be our own text ({iid})")
                if i.get("premium"): err(f, f"stories and guides stay free ({iid})")
            elif k == "link":
                if not i.get("url", "").startswith(LINK_HOSTS): err(f, f"link host not on the allow-list ({iid})")
            else: err(f, f"unknown kind ({iid})")
    if f == "app.json":
        u = data.get("crashUrl", "")
        if u and not u.startswith("https://script.google.com/macros/s/"): err(f, "crashUrl must be the developer's Apps Script web app (or empty)")
        if len(data.get("crashToken", "")) < 16: err(f, "crashToken too short")
    if f == "support.json":
        unique(f, data["resources"]); unique(f, data["social"]); unique(f, data["pictos"])
        kinds = {k["id"] for k in data["kinds"]}
        for r in data["resources"]:
            if r["region"] not in ("all", "flanders", "brussels", "wallonia") or r["kind"] not in kinds: err(f, f"bad region/kind ({r['id']})")
            if r.get("phone") and not re.fullmatch(r"\d{3,10}", r["phone"]): err(f, f"phone digits only ({r['id']})")
        if any(UNSAFE.search(json.dumps(x, ensure_ascii=False)) for x in data["social"]): err(f, "blocked word in social stories")
    if f == "turkish.json":
        unique(f, data["words"]); unique(f, data["idioms"]); unique(f, data["phrases"])

if errors:
    print("\n".join(errors)); sys.exit(1)
print("OK", len(list(ROOT.glob("*.json"))), "files")
