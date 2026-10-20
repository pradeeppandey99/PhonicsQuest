"""Phonics Quest local server.

Serves the app and keeps the recorded voices as plain files in ./sounds, with a
manifest.json beside them. A minute after the last change it commits the folder
and pushes it, so the GitHub Pages copy (phone, tablet) gets the same voices with
nothing to upload by hand.

  python server.py 8766

Only listens on 127.0.0.1. The recordings are PUBLIC once pushed (the repo is public;
PandeyG agreed to this on 20 Oct 2026).
"""
import http.server
import json
import os
import re
import subprocess
import sys
import threading
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
SOUNDS = os.path.join(ROOT, "sounds")
MANIFEST = os.path.join(SOUNDS, "manifest.json")
KEY = re.compile(r"^[a-z0-9-]{1,40}$")
MAX_BYTES = 5 * 1024 * 1024
PUBLISH_DELAY = 60
EXT = {"audio/webm": "webm", "audio/ogg": "ogg", "audio/mp4": "m4a", "audio/mpeg": "mp3", "audio/wav": "wav", "audio/x-wav": "wav"}
os.makedirs(SOUNDS, exist_ok=True)
lock = threading.Lock()
timer = None


def read_manifest():
    try:
        return json.load(open(MANIFEST, encoding="utf-8"))
    except Exception:
        return {}


def write_manifest(m):
    tmp = MANIFEST + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=0, sort_keys=True)
    os.replace(tmp, MANIFEST)


def migrate():
    """Turn the first version's <key>.bin + <key>.mime files into <key>.<ext> plus the manifest."""
    m = read_manifest()
    for f in sorted(os.listdir(SOUNDS)):
        if not f.endswith(".bin"):
            continue
        key = f[:-4]
        mime_path = os.path.join(SOUNDS, key + ".mime")
        mime = open(mime_path).read().strip() if os.path.exists(mime_path) else "audio/webm"
        if mime not in EXT:
            mime = "audio/webm"
        name = key + "." + EXT[mime]
        os.replace(os.path.join(SOUNDS, f), os.path.join(SOUNDS, name))
        if os.path.exists(mime_path):
            os.remove(mime_path)
        m[key] = {"file": name, "mime": mime}
    write_manifest(m)


def publish():
    """Commit and push only the sounds folder. Quiet on failure: the files are safe on disk either way."""
    log = os.path.join(ROOT, "publish.log")
    try:
        def git(*a):
            return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, timeout=120)
        git("add", "-A", "sounds")
        if git("diff", "--cached", "--quiet", "--", "sounds").returncode == 0:
            return
        c = git("commit", "-m", "Update recorded voices", "--", "sounds")
        p = git("push", "origin", "HEAD")
        with open(log, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} commit={c.returncode} push={p.returncode} {p.stderr.strip()[-200:]}\n")
    except Exception as e:
        with open(log, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} publish failed: {e}\n")


def schedule_publish():
    global timer
    if timer:
        timer.cancel()
    timer = threading.Timer(PUBLISH_DELAY, publish)
    timer.daemon = True
    timer.start()


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _key(self):
        m = re.match(r"^/api/sounds/([^/?]+)$", self.path.split("?")[0])
        return m.group(1) if m and KEY.match(m.group(1)) else None

    def do_GET(self):
        p = self.path.split("?")[0]
        if p == "/api/sounds":
            with lock:
                return self._json({"keys": sorted(read_manifest())})
        if p.startswith("/api/sounds/"):
            key = self._key()
            if not key:
                return self._json({"error": "bad key"}, 400)
            with lock:
                e = read_manifest().get(key)
            path = os.path.join(SOUNDS, e["file"]) if e else None
            if not path or not os.path.exists(path):
                return self._json({"error": "not found"}, 404)
            data = open(path, "rb").read()
            self.send_response(200)
            self.send_header("Content-Type", e.get("mime", "audio/webm"))
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
            return
        if p.startswith("/.git") or p.endswith(".log") or p.endswith(".py"):
            return self._json({"error": "not found"}, 404)
        return super().do_GET()

    def do_POST(self):
        key = self._key()
        if not key:
            return self._json({"error": "bad key"}, 400)
        n = int(self.headers.get("Content-Length") or 0)
        if n <= 0 or n > MAX_BYTES:
            return self._json({"error": "bad size"}, 400)
        data = self.rfile.read(n)
        mime = (self.headers.get("Content-Type") or "audio/webm").split(";")[0].strip()[:60]
        if mime not in EXT:
            mime = "audio/webm"
        name = key + "." + EXT[mime]
        with lock:
            m = read_manifest()
            old = m.get(key)
            if old and old["file"] != name and os.path.exists(os.path.join(SOUNDS, old["file"])):
                os.remove(os.path.join(SOUNDS, old["file"]))
            with open(os.path.join(SOUNDS, name), "wb") as f:
                f.write(data)
            m[key] = {"file": name, "mime": mime}
            write_manifest(m)
        schedule_publish()
        return self._json({"ok": True, "key": key, "bytes": len(data)})

    def do_DELETE(self):
        key = self._key()
        if not key:
            return self._json({"error": "bad key"}, 400)
        with lock:
            m = read_manifest()
            e = m.pop(key, None)
            if e and os.path.exists(os.path.join(SOUNDS, e["file"])):
                os.remove(os.path.join(SOUNDS, e["file"]))
            write_manifest(m)
        schedule_publish()
        return self._json({"ok": True})

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    migrate()
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8766
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Phonics Quest on http://localhost:{port}/index.html  (recordings kept in {SOUNDS}, pushed to GitHub a minute after each change)")
    srv.serve_forever()
