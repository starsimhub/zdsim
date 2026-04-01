#!/usr/bin/env python3
"""
Serve the repository root so the SPA can load:
  - /web/index.html
  - /web/data/summary.json  (copied when you run run_simulation.py)
  - /outputs/zerodose_demo_summary.json

Usage (from repository root):
  python web/serve.py
Then open http://127.0.0.1:8765/web/index.html
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PORT = 8765


def main() -> None:
    os.chdir(ROOT)
    try:
        from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
    except ImportError:
        from http.server import HTTPServer as ThreadingHTTPServer, SimpleHTTPRequestHandler

    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            sys.stderr.write("%s - %s\n" % (self.address_string(), format % args))

    port = int(os.environ.get("PORT", DEFAULT_PORT))
    for attempt in range(10):
        try:
            httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
            break
        except OSError:
            port += 1
    else:
        print("Could not bind a port; set PORT=...", file=sys.stderr)
        sys.exit(1)

    print(f"Serving {ROOT}")
    print(f"Open http://127.0.0.1:{port}/web/index.html")
    print("Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
