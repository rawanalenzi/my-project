"""SOC analytics and persistent attack state for the real admin dashboard."""
import ast
import datetime
import json
import os
from collections import Counter, defaultdict

STATE_FILE = "soc_state.json"


def _default_state():
    return {
        "saved_at": None,
        "blocked_ips": [],
        "behavior_profiles": {},
        "login_events": [],
    }


def load_state():
    if not os.path.exists(STATE_FILE):
        return _default_state()
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            data = json.load(f)
        for key in _default_state():
            data.setdefault(key, _default_state()[key])
        return data
    except (json.JSONDecodeError, OSError):
        return _default_state()


def save_state(state):
    state["saved_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def _risk_for_ip(events):
    emails = {e["email"] for e in events}
    passwords = {e["password"] for e in events}
    decoy_hits = sum(1 for e in events if e.get("decoy_hit"))
    count = len(events)

    if decoy_hits >= 1 or count >= 8:
        return "HIGH", "Repeated probing / decoy credential use"
    if count >= 4 or len(passwords) >= 3:
        return "MEDIUM", "Credential stuffing pattern detected"
    if len(emails) >= 3:
        return "MEDIUM", "Multiple identities from same source"
    return "LOW", "Low-volume probing behavior"


def register_login_event(state, ip, email, password, status, decoy_hit=False, deceptive=False):
    """Record a login attempt for SOC analytics."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ip_events = [e for e in state["login_events"] if e.get("ip") == ip]
    risk, reason = _risk_for_ip(
        ip_events
        + [{"email": email, "password": password, "decoy_hit": decoy_hit}]
    )
    blocked = ip in state["blocked_ips"]

    entry = {
        "ip": ip,
        "email": email,
        "password": password,
        "status": status,
        "timestamp": timestamp,
        "timestamp_text": timestamp,
        "decoy_hit": decoy_hit,
        "deceptive": deceptive,
        "risk": risk,
        "reason": reason,
        "blocked": blocked,
    }
    state["login_events"].append(entry)

    profiles = state.setdefault("behavior_profiles", {})
    profile = profiles.get(ip, {"ip": ip, "emails": [], "passwords": [], "decoy_hits": 0})
    if email and email not in profile["emails"]:
        profile["emails"].append(email)
    if password and password not in profile["passwords"]:
        profile["passwords"].append(password)
    if decoy_hit:
        profile["decoy_hits"] = profile.get("decoy_hits", 0) + 1
    profile["attempt_count"] = len([e for e in state["login_events"] if e["ip"] == ip])
    profile["latest_attempt"] = timestamp
    profile["risk_score"] = risk
    profile["reason"] = reason
    profile["blocked"] = blocked
    profiles[ip] = profile
    save_state(state)
    return entry


def mark_decoy_hit(state, ip):
    if ip not in state["blocked_ips"]:
        state["blocked_ips"].append(ip)
    save_state(state)


def build_admin_summary(state):
    events = state.get("login_events", [])
    ips = {e["ip"] for e in events}
    high_risk = sum(
        1
        for ip in ips
        if state.get("behavior_profiles", {}).get(ip, {}).get("risk_score") == "HIGH"
    )
    return {
        "total_attempts": len(events),
        "total_ips": len(ips),
        "high_risk_ips": high_risk,
        "blocked_ips": len(state.get("blocked_ips", [])),
        "decoy_hits": sum(1 for e in events if e.get("decoy_hit")),
    }


def build_grouped_results(state, selected_ip="", selected_risk=""):
    profiles = state.get("behavior_profiles", {})
    rows = []
    for ip, profile in profiles.items():
        risk = profile.get("risk_score", "LOW")
        if selected_ip and ip != selected_ip:
            continue
        if selected_risk and risk != selected_risk:
            continue
        rows.append(
            {
                "ip": ip,
                "risk_score": risk,
                "reason": profile.get("reason", ""),
                "attempt_count": profile.get("attempt_count", 0),
                "decoy_hits": profile.get("decoy_hits", 0),
                "latest_attempt": profile.get("latest_attempt", ""),
                "blocked": profile.get("blocked", False),
                "emails": profile.get("emails", []),
                "passwords": profile.get("passwords", []),
            }
        )
    rows.sort(key=lambda r: r["attempt_count"], reverse=True)
    return rows


def build_top_attackers(state, limit=5):
    return build_grouped_results(state)[:limit]


def hourly_stats(state):
    """Login attempts bucketed by hour for charts."""
    events = state.get("login_events", [])
    buckets = Counter()
    for event in events:
        ts = event.get("timestamp") or event.get("time") or ""
        hour = ts[11:13] if len(ts) >= 13 else "00"
        buckets[f"{hour}:00"] += 1
    if not buckets:
        return {"labels": ["08:00", "10:00", "12:00", "14:00", "16:00"], "counts": [0, 0, 0, 0, 0]}
    labels = sorted(buckets.keys())
    return {"labels": labels, "counts": [buckets[l] for l in labels]}


def live_feed_items(state, limit=10):
    rows = []
    for event in reversed(state.get("login_events", [])[-limit:]):
        rows.append(
            {
                "timestamp": event.get("timestamp", ""),
                "ip": event.get("ip", ""),
                "email": event.get("email", ""),
                "status": event.get("status", ""),
                "risk": event.get("risk", "LOW"),
            }
        )
    return rows


def read_attack_log_tail(limit=50):
    """Parse unified log lines for supplemental SOC review."""
    if not os.path.exists("attacks_log.txt"):
        return []
    entries = []
    try:
        with open("attacks_log.txt", encoding="utf-8") as f:
            lines = f.readlines()[-limit:]
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(ast.literal_eval(line))
            except (SyntaxError, ValueError):
                continue
    except OSError:
        pass
    return entries
