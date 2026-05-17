"""Public routes: home, login, logout, legacy verification redirect."""
from flask import Blueprint, redirect, render_template, request, session, url_for

from services.soc_service import load_state, mark_decoy_hit, register_login_event
from utils.auth import (
    establish_admin_session,
    establish_decoy_session,
    is_decoy_credential,
    is_real_admin_credentials,
)
from utils.logging import get_client_ip, unified_log

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def home():
    return redirect(url_for("public.login"))


@public_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("index.html")

    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""
    ip = get_client_ip()
    state = load_state()

    if is_real_admin_credentials(email, password):
        establish_admin_session(email)
        register_login_event(state, ip, email, password, "SUCCESS")
        unified_log("LOGIN", "/login", "REAL ADMIN LOGIN")
        return redirect(url_for("banking.dashboard"))

    decoy_hit = is_decoy_credential(email, password)
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
    return redirect(url_for("banking.dashboard"))


@public_bp.route("/verification", methods=["GET", "POST"])
def verification_legacy():
    """Legacy URL — silent redirect (no challenge UI)."""
    unified_log("ACCESS", "/verification", "LEGACY URL HIT")
    if session.get("user"):
        return redirect(url_for("banking.dashboard"))
    return redirect(url_for("public.login"))


@public_bp.route("/logout")
def logout():
    unified_log("ACCESS", "/logout", "SESSION END")
    session.clear()
    return redirect(url_for("public.login"))
