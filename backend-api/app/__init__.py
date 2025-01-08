from flask import Flask
from app.extensions import db, migrate
from app.auth.routes import auth_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth_bp)

    return app
