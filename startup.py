#!/usr/bin/env python3
import http.server
import socketserver
import os
import subprocess
import threading
import time

PORT = 5000

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<html><body><h1>Browser is running</h1><p>Check the VNC tab to see the interface.</p></body></html>")

def run_server():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()

def run_browser():
    # Find the browser
    browser = None
    for cmd in ["ungoogled-chromium", "chromium"]:
        try:
            subprocess.run(["which", cmd], check=True, capture_output=True)
            browser = cmd
            break
        except subprocess.CalledProcessError:
            continue
    
    if not browser:
        # Try to find in nix store as a last resort
        try:
            res = subprocess.run("find /nix/store -maxdepth 4 -type f -executable -name 'chromium' | head -n 1", shell=True, capture_output=True, text=True)
            browser = res.stdout.strip()
        except:
            pass

    if not browser:
        print("Chromium not found")
        return

    print(f"Launching {browser}...")
    
    while True:
        try:
            subprocess.run([
                browser,
                "--no-sandbox",
                "--disable-gpu",
                "--user-data-dir=/tmp/chromium-data",
                "--disable-dev-shm-usage",
                "--no-first-run",
                "--no-default-browser-check",
                "https://www.google.com"
            ])
        except Exception as e:
            print(f"Browser error: {e}")
        
        print("Browser exited, restarting in 1s...")
        time.sleep(1)

if __name__ == "__main__":
    # Ensure data dir exists
    os.makedirs("/tmp/chromium-data", exist_ok=True)
    
    # Start HTTP server in a thread to open port 5000
    threading.Thread(target=run_server, daemon=True).start()
    
    # Start the browser
    run_browser()
