"""Phonics Quest local server.

Serves the app and keeps the recorded voices on disk in ./sounds so they survive
clearing the browser and need no manual backup or upload.

  python server.py 8766

Only listens on 127.0.0.1. The recordings stay on this computer: sounds/ is in
.gitignore, so they are never pushed to the public repo.
"""
import http.server
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SOUNDS = os.path.join(ROOT, "sounds")
KEY = re.compile(r"^[a-z0-9-]{1,40}$")
MAX_BYTES = 5 * 1024 * 1024
os.makedirs(SOUNDS, exist_ok=True)


def paths(key):
    return os.path.join(SOUNDS, key + ".bin"), os.path.join(SOUNDS, key + ".mime")


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
            keys = sorted(f[:-4] for f in os.listdir(SOUNDS) if f.endswith(".bin"))
            return self._json({"keys": keys})
        if p.startswith("/api/sounds/"):
            key = self._key()
            if not key:
                return self._json({"error": "bad key"}, 400)
            b, m = paths(key)
            if not os.path.exists(b):
                return self._json({"error": "not found"}, 404)
            data = open(b, "rb").read()
            mime = open(m).read().strip() if os.path.exists(m) else "audio/webm"
            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
            return
        if p.startswith("/sounds/") or p.startswith("/.git"):
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
        mime = (self.headers.get("Content-Type") or "audio/webm").split(";")[0][:60]
        if not re.match(r"^[a-z0-9.+/-]+$", mime):
            mime = "audio/webm"
        b, m = paths(key)
        with open(b, "wb") as f:
            f.write(data)
        with open(m, "w") as f:
            f.write(mime)
        return self._json({"ok": True, "key": key, "bytes": len(data)})

    def do_DELETE(self):
        key = self._key()
        if not key:
            return self._json({"error": "bad key"}, 400)
        for p in paths(key):
            if os.path.exists(p):
                os.remove(p)
        return self._json({"ok": True})

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8766
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Phonics Quest on http://localhost:{port}/index.html  (recordings kept in {SOUNDS})")
    srv.serve_forever()
