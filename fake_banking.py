"""Synthetic banking profiles for deceptive honeypot sessions."""
import hashlib
import random
from datetime import datetime, timedelta


def _seed_from(email, ip):
    digest = hashlib.sha256(f"{email}|{ip}".encode()).hexdigest()
    return int(digest[:12], 16)


def build_fake_profile(email, ip):
    """Deterministic fake account data per email/IP (believable, repeatable)."""
    rng = random.Random(_seed_from(email or "guest", ip or "0.0.0.0"))
    first = (email or "client").split("@")[0].replace(".", " ").replace("_", " ").title()
    balance = rng.randint(84_500, 2_450_000)
    account_suffix = rng.randint(1000, 9999)
    card_last4 = str(rng.randint(1000, 9999))
    savings_last4 = str(rng.randint(1000, 9999))

    now = datetime.now()
    transactions = []
    merchants = [
        ("Payroll Deposit", "INCOMING", 12_500),
        ("Saudi Electric Co.", "BILL PAID", -420),
        ("Carrefour Riyadh", "CARD PAYMENT", -318),
        ("Ahmed Al-Rashid", "TRANSFER OUT", -1200),
        ("Sara Logistics", "TRANSFER OUT", -3800),
    ]
    for i, (label, status, amount) in enumerate(merchants):
        ts = (now - timedelta(days=i, hours=rng.randint(1, 9))).strftime("%Y-%m-%d %H:%M")
        transactions.append(
            {
                "timestamp": ts,
                "email": label,
                "status": status,
                "risk": "LOW",
                "amount": amount,
            }
        )

    transfer_history = [
        {"beneficiary": "Ahmed Al-Rashid", "amount": -1200, "when": transactions[3]["timestamp"]},
        {"beneficiary": "Sara Logistics", "amount": -3800, "when": transactions[4]["timestamp"]},
        {"beneficiary": "Payroll", "amount": 7500, "when": transactions[0]["timestamp"]},
    ]

    return {
        "display_name": first,
        "balance": balance,
        "balance_display": f"{balance:,} SAR",
        "account_number": f"SA-41-{rng.randint(10, 99):02d}-{account_suffix:04d}",
        "account_mask": f"Primary Account •••• {account_suffix % 10000:04d}",
        "savings_mask": f"Savings Account •••• {int(savings_last4):04d}",
        "card_last4": card_last4,
        "card_mask": f"•••• •••• •••• {card_last4}",
        "secondary_cards": [
            f"•••• •••• •••• {rng.randint(1000, 9999)}",
            f"•••• •••• •••• {rng.randint(1000, 9999)}",
            f"•••• •••• •••• {rng.randint(1000, 9999)}",
        ],
        "transactions": transactions,
        "transfer_history": transfer_history,
        "chart_labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        "chart_counts": [rng.randint(2, 9) for _ in range(6)],
        "loan_preapproved": rng.randint(50_000, 250_000),
    }


def banking_template_context(session, ip, nav_active=None):
    """Shared template variables for banking pages."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    sid = session.get("bank_sid") or f"SEC-{datetime.now().strftime('%f')}"
    role = session.get("role")
    ctx = {
        "user": session.get("user", "client@secbank.com"),
        "datetime": now,
        "sid": sid,
        "is_admin": role == "admin",
        "is_decoy": role == "decoy",
        "nav_active": nav_active or "",
    }
    if role == "decoy":
        profile = session.get("fake_profile") or build_fake_profile(ctx["user"], ip)
        ctx.update(profile)
    else:
        ctx.update(
            {
                "display_name": "Administrator",
                "balance": None,
                "balance_display": "Live SOC View",
                "account_number": "SA-ADMIN-0001",
                "account_mask": "Operations Account •••• 0001",
                "savings_mask": "Reserve Account •••• 0002",
                "card_mask": "•••• •••• •••• 0001",
                "secondary_cards": [],
                "transactions": [],
                "transfer_history": [],
                "loan_preapproved": 0,
            }
        )
    return ctx
