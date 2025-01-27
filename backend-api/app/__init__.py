from flask import Flask
from app.extensions import db, migrate
from app.auth.auth import auth
from app.api.endpoints.diary import diary
from app.api.endpoints.query import query
def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(diary, url_prefix="/api")
    app.register_blueprint(query, url_prefix="/api")

    return app
