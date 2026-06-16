"""Validate HoneyGate routes, templates, and static assets."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES = os.path.join(BASE, "templates")
STATIC = os.path.join(BASE, "static")

REQUIRED_TEMPLATES = [
    "index.html",
    "dashboard.html",
    "transfer.html",
    "cards.html",
    "loans.html",
    "statements.html",
    "settings.html",
    "admin.html",
    "honeypot_admin.html",
    "fake_root_console.html",
    "verification.html",
    "partials/banking_sidebar.html",
]

REQUIRED_STATIC = ["style.css", "admin.css"]

ROUTES_TO_SMOKE = [
    ("GET", "/", 302),
    ("GET", "/login", 200),
    ("GET", "/verification", 302),
    ("GET", "/config", 200),
    ("GET", "/secure-admin", 200),
    ("GET", "/.env", 404),
]


def main():
    errors = []

    for rel in REQUIRED_TEMPLATES:
        path = os.path.join(TEMPLATES, rel.replace("/", os.sep))
        if not os.path.isfile(path):
            errors.append(f"Missing template: {rel}")

    for rel in REQUIRED_STATIC:
        path = os.path.join(STATIC, rel)
        if not os.path.isfile(path):
            errors.append(f"Missing static file: {rel}")

    with app.test_client() as client:
        for method, path, expected in ROUTES_TO_SMOKE:
            resp = client.open(path, method=method)
            if resp.status_code != expected:
                errors.append(f"{method} {path} -> {resp.status_code}, expected {expected}")

        # Login decoy path
        resp = client.post("/login", data={"email": "test@x.com", "password": "wrong"}, follow_redirects=False)
        if resp.status_code not in (302, 303):
            errors.append(f"POST /login decoy -> {resp.status_code}")

        # Admin login
        resp = client.post(
            "/login",
            data={"email": "admin@bank.com", "password": "123456"},
            follow_redirects=True,
        )
        if resp.status_code != 200:
            errors.append(f"Admin login flow failed: {resp.status_code}")

        # SOC reachable as admin
        resp = client.get("/admin")
        if resp.status_code != 200:
            errors.append(f"GET /admin as admin -> {resp.status_code}")

    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print(" -", e)
        sys.exit(1)

    print("Validation OK: templates, static assets, and core routes.")


if __name__ == "__main__":
    main()
