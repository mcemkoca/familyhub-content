#!/usr/bin/env python3
"""Builds site/v1: every content file + manifest.json (version, sha256, size) + manifest.json.sig (ECDSA P-256, SHA-256).
Usage: build.py <version> <private-key.pem>   (in GitHub Actions the key comes from the FEED_PRIVATE_KEY secret)."""
import json, sys, hashlib, pathlib, subprocess, datetime, shutil, base64, os
root = pathlib.Path(__file__).resolve().parent.parent
version, key = int(sys.argv[1]), sys.argv[2]
out = root / "site" / "v1"; shutil.rmtree(root / "site", ignore_errors=True); out.mkdir(parents=True)
files = {}
for p in sorted((root / "content").glob("*.json")):
    b = p.read_bytes(); (out / p.name).write_bytes(b)
    files[p.name] = {"sha256": hashlib.sha256(b).hexdigest(), "bytes": len(b)}
notes = (os.environ.get("FEED_NOTES", "").strip().splitlines() or [""])[0][:120]
manifest = {"schema": 1, "version": version, "published": datetime.date.today().isoformat(), "minApp": 16, "notes": notes, "files": files}
mb = json.dumps(manifest, ensure_ascii=False, separators=(",", ":")).encode()
(out / "manifest.json").write_bytes(mb)
sig = subprocess.run(["openssl", "dgst", "-sha256", "-sign", key, str(out / "manifest.json")], check=True, capture_output=True).stdout
(out / "manifest.json.sig").write_text(base64.b64encode(sig).decode())
(root / "site" / "index.html").write_text("<!doctype html><meta charset=utf-8><title>FamilyHub content</title><p>FamilyHub içerik akışı. Kişisel veri yok.</p>")
(root / "site" / ".nojekyll").write_text("")
for page in sorted((root / "pages").glob("*.html")):   # public pages (privacy policy for Google Play)
    shutil.copy(page, root / "site" / page.name)
print("built version", version, "with", len(files), "files")
