from flask import Flask
from app.extensions import db, migrate
from app.auth.routes import auth_bp
from celery import Celery


def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config.get("CELERY_BROKER_URL"),
        backend=app.config.get("CELERY_RESULT_BACKEND"),
    )
    celery.conf.update(app.config)
    return celery


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    app.config["CELERY_BROKER_URL"] = "redis://redis:6379/0"
    app.config["CELERY_RESULT_BACKEND"] = "redis://redis:6379/0"

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth_bp)

    celery = make_celery(app)
    return app, celery
