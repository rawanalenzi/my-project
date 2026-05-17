"""
HoneyGate Flask application — deception-based banking honeypot.

Authentication model:
  • admin@bank.com / 123456  → real operator (ROLE_ADMIN) → banking UI + SOC (/admin)
  • Any other credentials    → apparent success (ROLE_DECOY) → synthetic banking only

Attackers never see verification challenges or "suspicious activity" messaging.
"""
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
)
import datetime
from functools import wraps

from fake_banking import banking_template_context, build_fake_profile
from soc_service import (
    load_state,
    register_login_event,
    mark_decoy_hit,
    build_admin_summary,
    build_grouped_results,
    build_top_attackers,
    hourly_stats,
    live_feed_items,
)

app = Flask(__name__)
app.secret_key = "honeygate_pro_2026"

# ── Real operator credentials (only path to SOC + legitimate session) ──
REAL_ADMIN_EMAIL = "admin@bank.com"
REAL_ADMIN_PASSWORD = "123456"

# Known decoy pairs — logged as intelligence, still receive fake success UX
DECOY_CREDENTIALS = {
    (REAL_ADMIN_EMAIL, "admin123"),
    ("backup@bank.com", REAL_ADMIN_PASSWORD),
}

ROLE_ADMIN = "admin"
ROLE_DECOY = "decoy"

# =========================
# Logging
# =========================
def get_client_ip():
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


def unified_log(event_type, path, action, extra=None):
    ip = get_client_ip()
    user_agent = request.headers.get("User-Agent", "Unknown")
    session_user = session.get("user", "anonymous")
    session_role = session.get("role", "none")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry = {
        "time": timestamp,
        "ip": ip,
        "type": event_type,
        "path": path,
        "action": action,
        "device": user_agent,
        "session": session_user,
        "role": session_role,
        "extra": extra or {},
    }

    with open("attacks_log.txt", "a", encoding="utf-8") as f:
        f.write(str(entry) + "\n")


def log_page_visit(path):
    unified_log("ACCESS", path, "PAGE VIEW")


def log_decoy_action(path, action, extra=None):
    """Silent intelligence capture for fake-banking interactions."""
    if session.get("role") == ROLE_DECOY:
        unified_log("DECOY_ACTION", path, action, extra)


# =========================
# Auth decorators
# =========================
def session_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "user" not in session or "role" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapper


def admin_required(view):
    """Restrict route to the real bank operator (not honeypot visitors)."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        if session.get("role") != ROLE_ADMIN:
            # Honeypot: attackers probing /admin see a fake internal panel
            unified_log("HONEYPOT", request.path, "UNAUTHORIZED ADMIN PROBE")
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            return render_template("honeypot_admin.html", datetime=now), 200
        return view(*args, **kwargs)

    return wrapper


def is_real_admin_credentials(email, password):
    return email == REAL_ADMIN_EMAIL and password == REAL_ADMIN_PASSWORD


def establish_decoy_session(email, ip):
    """Create a believable logged-in state for non-admin visitors."""
    profile = build_fake_profile(email, ip)
    session["user"] = email
    session["role"] = ROLE_DECOY
    session["fake_profile"] = profile
    session["bank_sid"] = f"SEC-{datetime.datetime.now().strftime('%f')}"


def establish_admin_session(email):
    session["user"] = email
    session["role"] = ROLE_ADMIN
    session.pop("fake_profile", None)
    session["bank_sid"] = f"ADM-{datetime.datetime.now().strftime('%f')}"


def ctx(nav_active=None):
    return banking_template_context(session, get_client_ip(), nav_active=nav_active)


# =========================
# Routes — public
# =========================
@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        # Never show failed-login or security warnings — login form only
        return render_template("index.html")

    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""
    ip = get_client_ip()
    state = load_state()

    # ── Real admin → legitimate banking + SOC access ──
    if is_real_admin_credentials(email, password):
        establish_admin_session(email)
        register_login_event(state, ip, email, password, "SUCCESS")
        unified_log("LOGIN", "/login", "REAL ADMIN LOGIN")
        return redirect(url_for("dashboard"))

    # ── Deception path: every other attempt "succeeds" into fake banking ──
    decoy_hit = (email, password) in DECOY_CREDENTIALS
    if decoy_hit:
        mark_decoy_hit(state, ip)
        unified_log(
            "ALERT",
            "/login",
            "DECOY CREDENTIAL HIT",
            {"email": email, "password": password},
        )

    establish_decoy_session(
        email or f"guest-{ip.replace('.', '-')}@session.local",
        ip,
    )
    register_login_event(
        state,
        ip,
        email,
        password,
        "APPARENT_SUCCESS",
        decoy_hit=decoy_hit,
        deceptive=True,
    )
    unified_log(
        "LOGIN",
        "/login",
        "DECEPTIVE LOGIN ACCEPTED",
        {"email": email, "decoy_hit": decoy_hit},
    )
    return redirect(url_for("dashboard"))


@app.route("/verification", methods=["GET", "POST"])
def verification_legacy():
    """Legacy URL — redirect silently (no challenge UI that tips off attackers)."""
    unified_log("ACCESS", "/verification", "LEGACY URL HIT")
    if session.get("user"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


# =========================
# Banking portal (shared URLs; admin vs decoy content differs via ctx)
# =========================
@app.route("/dashboard")
@session_required
def dashboard():
    log_page_visit("/dashboard")
    return render_template("dashboard.html", **ctx(nav_active="dashboard"))


@app.route("/transfer", methods=["GET", "POST"])
@session_required
def transfer():
    log_page_visit("/transfer")
    transfer_message = None

    if request.method == "POST":
        payload = {
            "beneficiary": request.form.get("beneficiary"),
            "iban": request.form.get("iban"),
            "amount": request.form.get("amount"),
            "from_account": request.form.get("from_account"),
        }
        if session.get("role") == ROLE_DECOY:
            log_decoy_action("/transfer", "FAKE TRANSFER ATTEMPT", payload)
            transfer_message = (
                "Transfer submitted successfully. Reference: TRF-"
                + datetime.datetime.now().strftime("%H%M%S")
            )
        else:
            unified_log("TRANSFER", "/transfer", "ADMIN TRANSFER FORM USE", payload)

    return render_template(
        "transfer.html",
        transfer_message=transfer_message,
        **ctx(nav_active="transfer"),
    )


@app.route("/cards")
@session_required
def cards():
    log_page_visit("/cards")
    return render_template("cards.html", **ctx(nav_active="cards"))


@app.route("/cards/action", methods=["POST"])
@session_required
def cards_action():
    action = request.form.get("action", "unknown")
    log_decoy_action("/cards/action", "CARD CONTROL CLICK", {"action": action})
    return redirect(url_for("cards"))


@app.route("/loans", methods=["GET", "POST"])
@session_required
def loans():
    log_page_visit("/loans")
    loan_message = None
    if request.method == "POST" and session.get("role") == ROLE_DECOY:
        payload = {
            "amount": request.form.get("amount"),
            "purpose": request.form.get("purpose"),
            "product": request.form.get("product"),
        }
        log_decoy_action("/loans", "FAKE LOAN APPLICATION", payload)
        loan_message = (
            "Application received. A relationship manager will contact you within 24 hours."
        )
    return render_template(
        "loans.html",
        loan_message=loan_message,
        **ctx(nav_active="loans"),
    )


@app.route("/statements")
@session_required
def statements():
    log_page_visit("/statements")
    return render_template("statements.html", **ctx(nav_active="statements"))


@app.route("/settings", methods=["GET", "POST"])
@session_required
def settings():
    log_page_visit("/settings")
    settings_message = None
    if request.method == "POST":
        unified_log(
            "SETTINGS",
            "/settings",
            "PROFILE UPDATE ATTEMPT",
            {"fields": list(request.form.keys())},
        )
        settings_message = "Your preferences have been saved."
    return render_template(
        "settings.html",
        settings_message=settings_message,
        **ctx(nav_active="settings"),
    )


# Decoy-only API for dashboard charts (never exposes SOC data)
@app.route("/bank/api/dashboard-data")
@session_required
def bank_dashboard_data():
    if session.get("role") != ROLE_DECOY:
        return jsonify({"error": "not found"}), 404
    profile = session.get("fake_profile") or build_fake_profile(
        session.get("user"), get_client_ip()
    )
    return jsonify(
        {
            "labels": profile.get("chart_labels", []),
            "counts": profile.get("chart_counts", []),
            "items": profile.get("transactions", []),
        }
    )


# =========================
# Hidden honeypot traps (no auth — probes are logged)
# =========================
@app.route("/secure-admin")
@app.route("/admin/config_backup")
def honeypot_secure_admin():
    unified_log("HONEYPOT", request.path, "FAKE ADMIN PANEL PROBE")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    return render_template("honeypot_admin.html", datetime=now)


@app.route("/config")
@app.route("/internal")
@app.route("/internal/core")
@app.route("/api/v1/admin")
def honeypot_config_console():
    unified_log("HONEYPOT", request.path, "SYSTEM CONSOLE PROBE")
    return render_template("fake_root_console.html")


@app.route("/backup.sql")
@app.route("/.env")
@app.route("/wp-admin")
def honeypot_asset_probe():
    unified_log("HONEYPOT", request.path, "SENSITIVE ASSET PROBE")
    return (
        "<!DOCTYPE html><html><body><h1>404 Not Found</h1>"
        "<p>The requested resource was not found on this server.</p></body></html>",
        404,
    )


@app.route("/log_command", methods=["POST"])
def log_command():
    command = request.form.get("command", "")
    if request.is_json:
        command = (request.get_json(silent=True) or {}).get("command", command)
    unified_log("COMMAND", "/log_command", "FAKE SHELL COMMAND", {"command": command})
    return jsonify({"status": "logged"})


# =========================
# Real SOC (admin session only)
# =========================
@app.route("/admin")
@session_required
@admin_required
def admin_soc():
    unified_log("SOC", "/admin", "SOC DASHBOARD VIEW")
    state = load_state()
    selected_ip = request.args.get("ip", "")
    selected_risk = request.args.get("risk", "")
    return render_template(
        "admin.html",
        summary=build_admin_summary(state),
        grouped_results=build_grouped_results(state, selected_ip, selected_risk),
        top_attackers=build_top_attackers(state),
        all_ips=sorted({e["ip"] for e in state.get("login_events", [])}),
        selected_ip=selected_ip,
        selected_risk=selected_risk,
    )


@app.route("/admin/live")
@session_required
@admin_required
def admin_live():
    return jsonify({"items": live_feed_items(load_state())})


@app.route("/admin/stats")
@session_required
@admin_required
def admin_stats():
    return jsonify(hourly_stats(load_state()))


# =========================
# Logout
# =========================
@app.route("/logout")
def logout():
    unified_log("ACCESS", "/logout", "SESSION END")
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
