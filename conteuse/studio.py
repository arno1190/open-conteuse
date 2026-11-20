"""Local parent studio, revision approvals and explicit pairing simulator.

Run python -m conteuse.studio --root .studio. Token is generated at launch;
enter it in the local UI. Never expose this development server publicly.
"""
import argparse
import hashlib
import hmac
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import secrets
import time
from .packages import (MAX_MANIFEST, activate, atomic_json, check_pack,
                       revision, safe_path)


class Studio:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.path = self.root / "state.json"
        self.state = json.loads(self.path.read_text()) if self.path.exists() else {
            "approvals": {}, "cards": {}, "devices": {}, "episodes": {}, "scripts": {}}
        self.state.setdefault("stations", {})
        self.pending_pair = None

    def save(self):
        atomic_json(self.path, self.state)
        self.path.chmod(0o600)

    def import_audio(self, files, destination, title):
        from .imports import import_playlist
        if not isinstance(files, list) or not all(isinstance(f, str) for f in files):
            raise ValueError("files must be a list of local paths")
        import_playlist(files, destination, title)
        return self.inspect(destination)

    def approve_station(self, station, url, mime):
        from .feeds import station_capability
        from urllib.parse import urlsplit
        parsed = urlsplit(url)
        if (not isinstance(station, str) or not 1 <= len(station) <= 64
                or parsed.username or parsed.password or parsed.fragment
                or station_capability(url, mime) != "direct"):
            raise ValueError("invalid or unsupported station")
        self.state["stations"][station] = {"url": url, "mime": mime, "approved": True}
        self.save()
        return self.state["stations"][station]

    def inspect(self, source):
        pack = check_pack(source)
        return {"title": pack["title"], "revision": revision(pack),
                "approved": revision(pack) in self.state["approvals"], "manifest": pack}

    def approve(self, source):
        pack = check_pack(source)
        digest = revision(pack)
        self.state["approvals"][digest] = {"time": int(time.time()), "kind": "final-content"}
        self.save()
        return digest

    def publish(self, source):
        digest = self.inspect(source)["revision"]
        if digest not in self.state["approvals"]:
            raise ValueError("review and approve this exact final revision first")
        return activate(source, self.root / "library", digest)

    def assign_card(self, uid, digest):
        if not isinstance(uid, str) or not 1 <= len(uid) <= 64 or digest not in self.state["approvals"]:
            raise ValueError("invalid card or unapproved content")
        self.state["cards"][uid] = digest
        self.save()

    def begin_pair(self, physical_presence=False):
        # Host simulator only: actual firmware must originate this event.
        if not physical_presence:
            raise ValueError("physical pairing event required")
        code = secrets.token_urlsafe(18)
        self.pending_pair = (code, time.monotonic() + 120)
        return code

    def claim_pair(self, code, device):
        pair = self.pending_pair
        if (not pair or time.monotonic() > pair[1] or not isinstance(code, str)
                or not hmac.compare_digest(code, pair[0]) or not safe_path(device) or "/" in device):
            raise ValueError("invalid or expired pairing")
        self.pending_pair = None
        secret = secrets.token_urlsafe(32)
        self.state["devices"][device] = hashlib.sha256(secret.encode()).hexdigest()
        self.save()
        return secret

    def authenticate(self, device, secret):
        expected = self.state["devices"].get(device, "")
        return bool(expected) and hmac.compare_digest(expected, hashlib.sha256(secret.encode()).hexdigest())

    def sync(self, device, secret, source, destination, interrupt=False):
        if not self.authenticate(device, secret):
            raise ValueError("device authentication failed")
        digest = self.inspect(source)["revision"]
        if digest not in self.state["approvals"]:
            raise ValueError("unapproved revision")
        return activate(source, destination, digest, interrupt=interrupt)

    def observe_episode(self, guid, audio):
        if not isinstance(guid, str) or not guid or len(audio) > 32 * 1024 * 1024:
            raise ValueError("invalid episode")
        digest = hashlib.sha256(audio).hexdigest()
        previous = self.state["episodes"].get(guid)
        self.state["episodes"][guid] = digest
        self.save()
        return {"sha256": digest, "changed": previous is not None and previous != digest,
                "approval_required": digest not in self.state["approvals"]}


UI = br'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Galia parent studio</title><style>body{font:18px system-ui;max-width:48rem;margin:3rem auto;padding:1rem;background:#faf7ee;color:#213b35}input,button{font:inherit;padding:.6rem;margin:.3rem}pre{white-space:pre-wrap}</style>
<h1>Parent studio</h1><p>Local prototype. Inspect a pack, review its contents locally, approve its exact revision, then activate it.</p>
<label>Session token <input id="token" type="password" autocomplete="off"></label><br>
<label>Pack directory <input id="source" value="examples/first-adventure"></label><br>
<button data-action="inspect">Inspect pack</button><button data-action="approve">Approve final content</button><button data-action="publish">Activate library</button>
<details><summary>Import recordings or a playlist</summary>
<p>Enter local file paths, one per line. Listen to the originals before approving the imported pack.</p>
<label>Audio paths <textarea id="files" rows="3"></textarea></label><br>
<label>New pack directory <input id="destination" value="work/my-pack"></label><br>
<label>Title <input id="title" value="My recordings"></label><button data-action="import">Import audio</button></details>
<details><summary>Assign a card</summary><label>Card UID <input id="uid"></label>
<label>Approved revision <input id="revision"></label><button data-action="card">Assign card</button></details>
<pre id="result" role="status"></pre><script>
for(const button of document.querySelectorAll('button'))button.onclick=async()=>{
const action=button.dataset.action;
let payload={source:document.getElementById('source').value};
if(action==='import')payload={files:document.getElementById('files').value.split('\n').filter(x=>x.trim()),destination:document.getElementById('destination').value,title:document.getElementById('title').value};
if(action==='card')payload={uid:document.getElementById('uid').value,revision:document.getElementById('revision').value};
try{const r=await fetch('/api/'+action,{method:'POST',headers:{'Content-Type':'application/json','Authorization':'Bearer '+document.getElementById('token').value},body:JSON.stringify(payload)});document.getElementById('result').textContent=JSON.stringify(await r.json(),null,2)}catch(e){document.getElementById('result').textContent=String(e)}};
</script></html>'''


def make_server(studio, token, port=8765):
    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(5)

        def log_message(self, *_):
            pass  # Do not log tokens or private paths.

        def send(self, code, value, mime="application/json"):
            data = value if isinstance(value, bytes) else json.dumps(value).encode()
            self.send_response(code)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(data)

        def trusted_host(self):
            return self.headers.get("Host") == f"127.0.0.1:{self.server.server_port}"

        def do_GET(self):
            if not self.trusted_host():
                return self.send(403, {"error": "invalid host"})
            self.send(200 if self.path == "/" else 404, UI if self.path == "/" else {}, "text/html; charset=utf-8")

        def do_POST(self):
            if (not self.trusted_host() or self.headers.get("Origin") not in
                    (None, f"http://127.0.0.1:{self.server.server_port}")
                    or not hmac.compare_digest(self.headers.get("Authorization", "").encode("utf-8"), ("Bearer " + token).encode("utf-8"))):
                return self.send(403, {"error": "unauthorized"})
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= MAX_MANIFEST:
                    raise ValueError("invalid request size")
                body = json.loads(self.rfile.read(size))
                if not isinstance(body, dict):
                    raise ValueError("request must be a JSON object")
                operation = {
                    "/api/inspect": (studio.inspect, (("source", str),)),
                    "/api/approve": (studio.approve, (("source", str),)),
                    "/api/publish": (studio.publish, (("source", str),)),
                    "/api/import": (studio.import_audio, (("files", list), ("destination", str), ("title", str))),
                    "/api/card": (studio.assign_card, (("uid", str), ("revision", str))),
                }.get(self.path)
                if operation is None:
                    return self.send(404, {"error": "unknown operation"})
                action, fields = operation
                for field, expected in fields:
                    if not isinstance(body.get(field), expected):
                        raise ValueError("invalid field: " + field)
                self.send(200, {"result": action(*(body[field] for field, _ in fields))})
            except (ValueError, OSError, KeyError, TypeError, RecursionError) as exc:
                self.send(400, {"error": str(exc)})
    server = HTTPServer(("127.0.0.1", port), Handler)
    server.timeout = 5
    return server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".studio")
    parser.add_argument("--port", default=8765, type=int)
    args = parser.parse_args()
    token = secrets.token_urlsafe(32)
    server = make_server(Studio(args.root), token, args.port)
    print(f"Open http://127.0.0.1:{server.server_port}/\nSession token: {token}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
