from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import datetime
import json
import os
import random
import time
import tempfile
from functools import wraps

app = Flask(__name__)
app.secret_key = 'honeygate_pro_2026'

STATE_FILE = "soc_state.json"
login_events = []
blocked_ips = set()
behavior_profiles = {}

REAL_CREDENTIALS = {"email": "admin@bank.com", "password": "123456"}
DECOY_CREDENTIALS = {
    ("admin@bank.com", "admin123"),
    ("backup@bank.com", "123456"),
}

# =========================
# 🔥 UNIFIED LOGGER
# =========================
def get_client_ip():
    return request.headers.get("X-Forwarded-For", request.remote_addr)

def unified_log(event_type, path, action, extra=None):
    ip = get_client_ip()
    user_agent = request.headers.get("User-Agent", "Unknown")
    session_id = session.get("user", "anonymous")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry = {
        "time": timestamp,
        "ip": ip,
        "type": event_type,
        "path": path,
        "action": action,
        "device": user_agent,
        "session": session_id,
        "extra": extra or {}
    }

    with open("attacks_log.txt", "a", encoding="utf-8") as f:
        f.write(str(entry) + "\n")


# =========================
# LOGIN EVENTS TRACKING
# =========================
def register_event(ip, email, password, status, decoy=False):
    login_events.append({
        "ip": ip,
        "email": email,
        "password": password,
        "status": status,
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "decoy": decoy
    })

    if decoy:
        blocked_ips.add(ip)


# =========================
# AUTH DECORATORS
# =========================
def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapper


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if session.get("user") != "admin@bank.com":
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapper


# =========================
# ROUTES
# =========================

@app.route('/')
def home():
    return redirect(url_for('login'))


# -------- LOGIN --------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('index.html')

    email = request.form.get("email")
    password = request.form.get("password")
    ip = get_client_ip()

    # blocked
    if ip in blocked_ips:
        unified_log("LOGIN", "/login", "BLOCKED ATTEMPT")
        return render_template("index.html", status_message="Try again later...")

    # success
    if email == REAL_CREDENTIALS["email"] and password == REAL_CREDENTIALS["password"]:
        session["user"] = email
        unified_log("LOGIN", "/login", "SUCCESS LOGIN")
        register_event(ip, email, password, "SUCCESS")
        return redirect(url_for("dashboard"))

    # decoy hit
    decoy = (email, password) in DECOY_CREDENTIALS
    unified_log("LOGIN", "/login", "FAILED LOGIN", {"email": email})

    register_event(ip, email, password, "FAILED", decoy)

    if decoy:
        unified_log("ALERT", "/login", "DECOY HIT")

    return render_template("index.html", status_message="Login failed")


# -------- DASHBOARD --------
@app.route('/dashboard')
@login_required
def dashboard():
    unified_log("ACCESS", "/dashboard", "USER VIEW")
    return render_template("dashboard.html", user=session["user"])


# -------- FAKE ADMIN (HONEYPOT) --------
@app.route('/secure-admin')
def fake_admin():
    unified_log("HONEYPOT", "/secure-admin", "ADMIN ACCESS ATTEMPT")
    return render_template("admin.html")


# -------- FAKE CONFIG TRAP --------
@app.route('/config')
def config_trap():
    ip = get_client_ip()
    unified_log("HONEYPOT", "/config", "SYSTEM PROBE")

    if ip in blocked_ips:
        return "Access Denied", 403

    return render_template("fake_root_console.html")


# -------- COMMAND LOGGER --------
@app.route('/log_command', methods=['POST'])
def log_command():
    command = request.form.get("command")

    unified_log(
        "COMMAND",
        "/fake_console",
        "EXECUTED COMMAND",
        {"command": command}
    )

    return jsonify({"status": "logged"})


# -------- ADMIN SOC --------
@app.route('/admin')
@admin_required
def admin():
    unified_log("SOC", "/admin", "DASHBOARD VIEW")

    summary = {
        "total": len(login_events),
        "blocked": len(blocked_ips),
    }

    return render_template("admin.html", summary=summary)


# -------- LIVE FEED --------
@app.route('/admin/live')
@admin_required
def live():
    return jsonify({
        "items": list(reversed(login_events[-10:]))
    })


# -------- LOGOUT --------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("home"))


# =========================
# RUN
# =========================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
