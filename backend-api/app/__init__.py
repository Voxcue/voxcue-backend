from flask import Flask
from app.extensions import db, migrate
from app.auth.routes import auth_bp
from celery import Celery,shared_task


def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config["broker_url"],
        backend=app.config["result_backend"],
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    # Use new-style configuration keys
    app.config["broker_url"] = "redis://redis:6379/0"
    app.config["result_backend"] = "redis://redis:6379/0"

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth_bp)

    celery = make_celery(app)

    celery.conf.beat_schedule = {
        "run-every-30-seconds": {
            "task": "app.auth.tasks.add_together",
            "schedule": 30.0,
        },
        "run-every-5-seconds": {
            "task": "app.auth.tasks.add_together",
            "schedule": 5.0,
        },
    }


    # example beat Process
    @shared_task(name="app.auth.tasks.add_together")
    def add_together(a=1, b=2):
        """Simple arithmetic task for testing"""
        return a + b

    return app, celery
