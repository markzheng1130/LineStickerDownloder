from flask import Flask
from flask_bootstrap import Bootstrap

bootstrap = Bootstrap()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hard to guess string'

    bootstrap.init_app(app)

    from app.main import blueprint_main
    app.register_blueprint(blueprint_main)

    return app
