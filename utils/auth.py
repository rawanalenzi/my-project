"""Session helpers and route guards."""
import datetime
from functools import wraps

from flask import redirect, render_template, request, session, url_for

from config import (
    DECOY_CREDENTIALS,
    REAL_ADMIN_EMAIL,
    REAL_ADMIN_PASSWORD,
    ROLE_ADMIN,
    ROLE_DECOY,
)
from services.fake_banking import build_fake_profile, banking_template_context
from utils.logging import get_client_ip, unified_log


def is_real_admin_credentials(email, password):
    return email == REAL_ADMIN_EMAIL and password == REAL_ADMIN_PASSWORD


def establish_decoy_session(email, ip):
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


def template_ctx(nav_active=None):
    return banking_template_context(session, get_client_ip(), nav_active=nav_active)


def session_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "user" not in session or "role" not in session:
            return redirect(url_for("public.login"))
        return view(*args, **kwargs)

    return wrapper


def admin_required(view):
    """Real SOC routes only; decoy users get a fake internal panel."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        if session.get("role") != ROLE_ADMIN:
            unified_log("HONEYPOT", request.path, "UNAUTHORIZED ADMIN PROBE")
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            return render_template("honeypot_admin.html", datetime=now), 200
        return view(*args, **kwargs)

    return wrapper


def is_decoy_credential(email, password):
    return (email, password) in DECOY_CREDENTIALS
