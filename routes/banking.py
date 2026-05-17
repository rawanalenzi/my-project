"""Authenticated banking portal (real admin + deceptive decoy sessions)."""
import datetime

from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

from config import ROLE_DECOY
from services.fake_banking import build_fake_profile
from utils.auth import session_required, template_ctx
from utils.logging import get_client_ip, log_decoy_action, log_page_visit, unified_log

banking_bp = Blueprint("banking", __name__)


@banking_bp.route("/dashboard")
@session_required
def dashboard():
    log_page_visit("/dashboard")
    return render_template("dashboard.html", **template_ctx(nav_active="dashboard"))


@banking_bp.route("/transfer", methods=["GET", "POST"])
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
        **template_ctx(nav_active="transfer"),
    )


@banking_bp.route("/cards")
@session_required
def cards():
    log_page_visit("/cards")
    return render_template("cards.html", **template_ctx(nav_active="cards"))


@banking_bp.route("/cards/action", methods=["POST"])
@session_required
def cards_action():
    action = request.form.get("action", "unknown")
    log_decoy_action("/cards/action", "CARD CONTROL CLICK", {"action": action})
    return redirect(url_for("banking.cards"))


@banking_bp.route("/loans", methods=["GET", "POST"])
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
        **template_ctx(nav_active="loans"),
    )


@banking_bp.route("/statements")
@session_required
def statements():
    log_page_visit("/statements")
    return render_template("statements.html", **template_ctx(nav_active="statements"))


@banking_bp.route("/settings", methods=["GET", "POST"])
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
        **template_ctx(nav_active="settings"),
    )


@banking_bp.route("/bank/api/dashboard-data")
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
