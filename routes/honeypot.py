"""Hidden honeypot traps — no auth required; probes are logged."""
import datetime

from flask import Blueprint, jsonify, render_template, request

from utils.logging import unified_log

honeypot_bp = Blueprint("honeypot", __name__)


@honeypot_bp.route("/secure-admin")
@honeypot_bp.route("/admin/config_backup")
def honeypot_secure_admin():
    unified_log("HONEYPOT", request.path, "FAKE ADMIN PANEL PROBE")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    return render_template("honeypot_admin.html", datetime=now)


@honeypot_bp.route("/config")
@honeypot_bp.route("/internal")
@honeypot_bp.route("/internal/core")
@honeypot_bp.route("/api/v1/admin")
def honeypot_config_console():
    unified_log("HONEYPOT", request.path, "SYSTEM CONSOLE PROBE")
    return render_template("fake_root_console.html")


@honeypot_bp.route("/backup.sql")
@honeypot_bp.route("/.env")
@honeypot_bp.route("/wp-admin")
def honeypot_asset_probe():
    unified_log("HONEYPOT", request.path, "SENSITIVE ASSET PROBE")
    return (
        "<!DOCTYPE html><html><body><h1>404 Not Found</h1>"
        "<p>The requested resource was not found on this server.</p></body></html>",
        404,
    )


@honeypot_bp.route("/log_command", methods=["POST"])
def log_command():
    command = request.form.get("command", "")
    if request.is_json:
        command = (request.get_json(silent=True) or {}).get("command", command)
    unified_log("COMMAND", "/log_command", "FAKE SHELL COMMAND", {"command": command})
    return jsonify({"status": "logged"})
