#!/usr/bin/env python3
"""Builds site/v1 (apps before 4.0: files they know) and site/v2 (4.0+: every file, e.g. rules.json),
each with manifest.json (version, sha256, size) + manifest.json.sig (ECDSA P-256, SHA-256).
Usage: build.py <version> <private-key.pem>   (in GitHub Actions the key comes from the FEED_PRIVATE_KEY secret)."""
import json, sys, hashlib, pathlib, subprocess, datetime, shutil, base64, os
root = pathlib.Path(__file__).resolve().parent.parent
version, key = int(sys.argv[1]), sys.argv[2]
shutil.rmtree(root / "site", ignore_errors=True)
V1_ONLY_KNOWN = {"rules.json"}   # older apps reject unknown files, so v1 never lists these
notes = (os.environ.get("FEED_NOTES", "").strip().splitlines() or [""])[0][:120]
def build(channel, min_app, skip):
    out = root / "site" / channel; out.mkdir(parents=True)
    files = {}
    for p in sorted((root / "content").glob("*.json")):
        if p.name in skip: continue
        b = p.read_bytes(); (out / p.name).write_bytes(b)
        files[p.name] = {"sha256": hashlib.sha256(b).hexdigest(), "bytes": len(b)}
    manifest = {"schema": 1, "version": version, "published": datetime.date.today().isoformat(), "minApp": min_app, "notes": notes, "files": files}
    mb = json.dumps(manifest, ensure_ascii=False, separators=(",", ":")).encode()
    (out / "manifest.json").write_bytes(mb)
    sig = subprocess.run(["openssl", "dgst", "-sha256", "-sign", key, str(out / "manifest.json")], check=True, capture_output=True).stdout
    (out / "manifest.json.sig").write_text(base64.b64encode(sig).decode())
    return len(files)
n1 = build("v1", 16, V1_ONLY_KNOWN)
n2 = build("v2", 23, set())
files = {"v1": n1, "v2": n2}
(root / "site" / "index.html").write_text("<!doctype html><meta charset=utf-8><title>FamilyHub content</title><p>FamilyHub içerik akışı. Kişisel veri yok.</p>")
(root / "site" / ".nojekyll").write_text("")
print("built version", version, "files", files)
