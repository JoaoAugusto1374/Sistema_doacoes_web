from flask import Flask
from .extensions import db, migrate, jwt, cors
from .models import User, Campaign, Donation
from config import Config
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)

    from .routes.campaigns import campaigns_bp
    app.register_blueprint(campaigns_bp, url_prefix="/api/campaigns")
    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    from .routes.donations import donations_bp
    app.register_blueprint(donations_bp, url_prefix="/api/donations")

    @app.route("/")
    def index():
        return {"msg": "API de Doações rodando!"}

    return app
