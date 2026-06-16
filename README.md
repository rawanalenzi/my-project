# HoneyGate (SeC Bank)

Educational deception-based banking honeypot with integrated SOC dashboard.

> **Disclaimer:** For educational and authorized lab use only. Do not deploy on production systems or against real users.

## Features

- Deceptive login (non-admin attempts always appear successful)
- Synthetic fake banking environment for attackers
- Real admin SOC dashboard (`admin@bank.com` / `123456`)
- Hidden honeypot traps (fake admin panel, shell console, asset probes)
- Unified forensic logging

## Project structure

```
HoneyGate/
├── app.py                 # Flask entry point
├── config.py              # Credentials, paths, constants
├── requirements.txt
├── routes/                # Blueprints (public, banking, honeypot, soc)
├── services/              # fake_banking, soc_service
├── utils/                 # logging, auth helpers
├── templates/             # Jinja2 HTML
├── static/                # CSS
├── logs/                  # attacks_log.txt, soc_state.json (runtime)
└── scripts/
    └── validate_project.py
```

## Installation

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Open http://127.0.0.1:8000

## Credentials

| Role | Email | Password | Result |
|------|-------|----------|--------|
| Real admin | admin@bank.com | 123456 | Banking + SOC Center |
| Decoy (logged) | admin@bank.com | admin123 | Fake banking + alert |
| Any other | * | * | Fake banking (silent) |

## Key routes

| Route | Purpose |
|-------|---------|
| `/login` | Sign-in (deceptive for non-admin) |
| `/dashboard` | Banking home |
| `/admin` | Real SOC (admin only) |
| `/verification` | Legacy redirect (no challenge UI) |
| `/config`, `/internal` | Fake shell honeypot |
| `/secure-admin` | Fake admin panel |

## Validate

```bash
python scripts/validate_project.py
```

## Logs

- `logs/attacks_log.txt` — unified forensic events
- `logs/soc_state.json` — SOC analytics state
