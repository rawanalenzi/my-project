"""
HoneyGate — deception-based banking honeypot (Flask entry point).

Run: python app.py
"""
from flask import Flask

from config import SECRET_KEY, ensure_runtime_dirs
from routes import register_blueprints


def create_app():
    ensure_runtime_dirs()
    application = Flask(__name__)
    application.secret_key = SECRET_KEY
    register_blueprints(application)
    return application


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
