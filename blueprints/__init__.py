from flask import Flask
from .login import login_bp
from .logout import logout_bp
from .profile import profile_bp
from .dashboard import dashboard_bp
from .academic import academic_bp
from .clubs import clubs_bp
from .placements import placements_bp
from .forum import forum_bp

def register_blueprints(app: Flask):
    """Registers all blueprints with the given Flask app instance."""
    app.register_blueprint(login_bp)
    app.register_blueprint(logout_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(academic_bp)
    app.register_blueprint(clubs_bp)
    app.register_blueprint(placements_bp)
    app.register_blueprint(forum_bp)
