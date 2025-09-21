from flask import Flask
from .extensions import db, migrate, jwt
from .models import User, Campaign, Donation
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from .routes.campaigns import campaigns_bp
    app.register_blueprint(campaigns_bp, url_prefix="/api/campaigns")
    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    @app.route("/")
    def index():
        return {"msg": "API de Doações rodando!"}

    return app
