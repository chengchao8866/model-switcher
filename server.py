#!/usr/bin/env python3
"""Hermes Model Switcher — lightweight web panel for switching AI models."""

import http.server
import json
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import yaml

CONFIG_PATH = Path.home() / ".hermes" / "config.yaml"
HTML_PATH = Path(__file__).parent / "index.html"
PORT = int(os.environ.get("PORT", 8899))

def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)

def get_models():
    """Return all models grouped by provider, with current default marked."""
    cfg = load_config()
    providers = cfg.get("providers", {})
    default_model = cfg.get("model", {}).get("default", "")
    default_provider = cfg.get("model", {}).get("provider", "")

    result = {"default_model": default_model, "default_provider": default_provider, "providers": {}}

    for pname, pcfg in providers.items():
        models = []
        for m in pcfg.get("models", []):
            if isinstance(m, str):
                models.append(m)
            elif isinstance(m, dict):
                models.append(m.get("id", m.get("name", str(m))))
        result["providers"][pname] = {"name": pcfg.get("name", pname), "base_url": pcfg.get("base_url", ""), "models": models}

    return result

def switch_model(provider, model):
    """Switch default model + provider via hermes CLI."""
    try:
        r1 = subprocess.run(
            ["hermes", "config", "set", "model.default", model],
            capture_output=True, text=True, timeout=15,
        )
        r2 = subprocess.run(
            ["hermes", "config", "set", "model.provider", provider],
            capture_output=True, text=True, timeout=15,
        )
        if r1.returncode == 0 and r2.returncode == 0:
            return {"ok": True, "model": model, "provider": provider}
        else:
            return {"ok": False, "error": f"set model.default: {r1.stderr.strip()}\nset model.provider: {r2.stderr.strip()}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # Suppress default logging to stderr
        pass

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def _send_html(self, content, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            try:
                with open(HTML_PATH, "rb") as f:
                    self._send_html(f.read())
            except FileNotFoundError:
                self._send_json({"error": "index.html not found"}, 404)
        elif parsed.path == "/api/models":
            try:
                self._send_json(get_models())
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/switch":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length else b"{}"
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                self._send_json({"ok": False, "error": "Invalid JSON"}, 400)
                return
            provider = data.get("provider", "")
            model = data.get("model", "")
            if not provider or not model:
                self._send_json({"ok": False, "error": "Missing provider or model"}, 400)
                return
            result = switch_model(provider, model)
            self._send_json(result, 200 if result["ok"] else 500)
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

def main():
    if not CONFIG_PATH.exists():
        print(f"Config not found: {CONFIG_PATH}", file=sys.stderr)
        sys.exit(1)
    print(f"🧠 Hermes Model Switcher → http://localhost:{PORT}")
    print("   Press Ctrl+C to stop.")
    server = http.server.HTTPServer(("0.0.0.0", PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Shutting down.")
        server.server_close()

if __name__ == "__main__":
    main()
