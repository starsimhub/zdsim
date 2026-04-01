#!/usr/bin/env python3
"""
Start a local static server from the repository root and open the results SPA.

Usage (from anywhere):
  python /path/to/zdsim/web/open_spa.py

Or from repo root:
  python web/open_spa.py
"""

from __future__ import annotations

import os
import sys
import threading
import time
import webbrowser

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
    for _ in range(20):
        try:
            httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
            break
        except OSError:
            port += 1
    else:
        print("No free port found.", file=sys.stderr)
        sys.exit(1)

    url = f"http://127.0.0.1:{port}/web/index.html"

    def _open():
        time.sleep(0.35)
        webbrowser.open(url)

    threading.Thread(target=_open, daemon=True).start()

    print(f"Serving: {ROOT}")
    print(f"Open:    {url}")
    print("Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
