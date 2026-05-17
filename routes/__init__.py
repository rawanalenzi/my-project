"""Register all Flask blueprints."""
from routes.banking import banking_bp
from routes.honeypot import honeypot_bp
from routes.public import public_bp
from routes.soc import soc_bp


def register_blueprints(app):
    app.register_blueprint(public_bp)
    app.register_blueprint(banking_bp)
    app.register_blueprint(honeypot_bp)
    app.register_blueprint(soc_bp)
