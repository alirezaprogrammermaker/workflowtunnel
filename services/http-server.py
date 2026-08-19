#!/usr/bin/env python3
"""
Simple HTTP server for Cloudflare Tunnel demonstration.
This can be replaced with any HTTP server (Node. js, PHP, etc.)
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

PORT = 8000
HOST = "localhost"

class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
        elif self.path == "/info":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            import json
            info = {
                "status": "running",
                "port": PORT,
                "cwd": os.getcwd(),
                "pid": os.getpid()
            }
            self.wfile.write(json.dumps(info, indent=2).encode())
        else:
            super().do_GET()

    def log_message(self, format, *args):
        print(f"[HTTP] {args[0]}")

def main():
    server = HTTPServer((HOST, PORT), CustomHandler)
    print(f"HTTP Server running on http://{HOST}:{PORT}")
    print(f"PID: {os.getpid()}")
    print("Press Ctrl+C to stop")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()

if __name__ == "__main__":
    main()