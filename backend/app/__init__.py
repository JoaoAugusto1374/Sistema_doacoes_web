from flask import Flask
from .extensions import db, migrate
from .models import User, Campaign, Donation
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    @app.route("/")
    def index():
        return {"msg": "API de Doações rodando!"}

    return app
