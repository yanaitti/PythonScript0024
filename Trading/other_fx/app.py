from flask import Flask
from database import init_db
import blueprints
import importlib
from cache import init_cache


def create_app():
    app = Flask(__name__)
    app.secret_key = 'secret'
    app.config.from_object('config.Config')

    for blueprint in blueprints.all_blueprints:
        importlib.import_module(blueprint.import_name)
        app.register_blueprint(blueprint)

    init_db(app)
    init_cache(app)

    return app

app = create_app()
