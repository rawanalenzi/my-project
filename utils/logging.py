"""Unified forensic logging for honeypot and SOC events."""
import datetime

from flask import request, session

from config import ATTACKS_LOG_FILE


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

    with open(ATTACKS_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(str(entry) + "\n")


def log_page_visit(path):
    unified_log("ACCESS", path, "PAGE VIEW")


def log_decoy_action(path, action, extra=None):
    """Silent capture for fake-banking interactions (decoy sessions only)."""
    from config import ROLE_DECOY

    if session.get("role") == ROLE_DECOY:
        unified_log("DECOY_ACTION", path, action, extra)
