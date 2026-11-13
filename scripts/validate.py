#!/usr/bin/env python3
"""Checks every content file before it can be published. Exit code 1 = do not publish."""
import json, sys, re, datetime, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent / "content"
ALLOWED = {"questions.json","skills.json","adventures.json","stories.json","emotions.json","recipes.json","levels.json","prompts.json",
           "activities.json","plans.json","belgium.json","money.json","rights.json","topics.json","turkish.json","savings.json",
           "calendar.json","life.json","learn.json","rules.json"}
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

for p in sorted(ROOT.glob("*.json")):
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
    if f == "turkish.json":
        unique(f, data["words"]); unique(f, data["idioms"]); unique(f, data["phrases"])

if errors:
    print("\n".join(errors)); sys.exit(1)
print("OK", len(list(ROOT.glob("*.json"))), "files")
