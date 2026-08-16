"""Optional HTTP API using only Python's standard library."""
from __future__ import annotations
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json, os
from .ecosystem import EcosystemRuntime

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        rt=EcosystemRuntime(); routes={"/status":rt.status,"/ecosystem":rt.discover,"/nodes":lambda:[n.__dict__ for n in rt.nodes()],"/verify":rt.verify}
        fn=routes.get(self.path.split("?",1)[0])
        if not fn: self.send_error(404); return
        try: body=json.dumps(fn(), ensure_ascii=False, default=str).encode(); self.send_response(200); self.send_header("Content-Type","application/json"); self.end_headers(); self.wfile.write(body)
        except Exception as exc: self.send_error(502, str(exc))
    def log_message(self, fmt, *args): pass

def serve(host=None, port=None):
    host=host or os.getenv("NOESIS_HOST","127.0.0.1"); port=int(port or os.getenv("NOESIS_PORT","8788"))
    ThreadingHTTPServer((host,port),Handler).serve_forever()
