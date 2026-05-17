"""Real SOC dashboard — admin session only."""
from flask import Blueprint, jsonify, render_template, request

from services.soc_service import (
    build_admin_summary,
    build_grouped_results,
    build_top_attackers,
    hourly_stats,
    live_feed_items,
    load_state,
)
from utils.auth import admin_required, session_required
from utils.logging import unified_log

soc_bp = Blueprint("soc", __name__)


@soc_bp.route("/admin")
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


@soc_bp.route("/admin/live")
@session_required
@admin_required
def admin_live():
    return jsonify({"items": live_feed_items(load_state())})


@soc_bp.route("/admin/stats")
@session_required
@admin_required
def admin_stats():
    return jsonify(hourly_stats(load_state()))
