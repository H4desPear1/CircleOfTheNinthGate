"""
Circle of the Ninth Gate — Authentication Server
Deploy on Railway. Handles password verification and issues session tokens.

Environment variables (set in Railway dashboard):
  SECRET_PASSWORD  — the CTF login passphrase
  SECRET_KEY       — random string used to sign tokens (generate with: python -c "import secrets; print(secrets.token_hex(32))")
  FRONTEND_ORIGIN  — your GitHub Pages URL, e.g. https://yourusername.github.io
"""

import os
import hmac
import hashlib
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# ── Config ────────────────────────────────────────────────────────────────────

SECRET_PASSWORD = os.environ.get("SECRET_PASSWORD", "ninthgate")
SECRET_KEY      = os.environ.get("SECRET_KEY",      "change-this-in-production").encode()
FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "*")

# Token validity window in seconds (1 hour)
TOKEN_TTL = 3600

CORS(app, origins=[FRONTEND_ORIGIN], supports_credentials=True)

# ── Token helpers ─────────────────────────────────────────────────────────────

def make_token(timestamp: int) -> str:
    """HMAC-SHA256 token: hex(timestamp) + '.' + hex(signature)"""
    ts_hex = format(timestamp, "x")
    sig = hmac.new(SECRET_KEY, ts_hex.encode(), hashlib.sha256).hexdigest()
    return f"{ts_hex}.{sig}"

def verify_token(token: str) -> bool:
    """Returns True if the token is valid and not expired."""
    try:
        ts_hex, sig = token.split(".", 1)
        expected_sig = hmac.new(SECRET_KEY, ts_hex.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected_sig):
            return False
        issued_at = int(ts_hex, 16)
        return (time.time() - issued_at) < TOKEN_TTL
    except Exception:
        return False

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    """Railway health check endpoint."""
    return jsonify({"status": "node active"}), 200


@app.route("/authenticate", methods=["POST"])
def authenticate():
    """
    POST /authenticate
    Body: { "passphrase": "..." }
    Returns: { "token": "..." }  or 401
    """
    data = request.get_json(silent=True) or {}
    passphrase = data.get("passphrase", "")

    if not hmac.compare_digest(passphrase, SECRET_PASSWORD):
        # Short delay to slow brute-force
        time.sleep(0.4)
        return jsonify({"error": "Access denied — phrase unrecognized"}), 401

    token = make_token(int(time.time()))
    return jsonify({"token": token}), 200


@app.route("/verify", methods=["POST"])
def verify():
    """
    POST /verify
    Body: { "token": "..." }
    Returns: 200 OK or 401
    Used by comms.html on load to confirm the token is still valid.
    """
    data  = request.get_json(silent=True) or {}
    token = data.get("token", "")

    if verify_token(token):
        return jsonify({"status": "authorized"}), 200
    return jsonify({"error": "Session expired or invalid"}), 401


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
