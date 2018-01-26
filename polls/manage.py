from flask import Flask

from config import flack_config
from polls.flask_polls.main import frontend

def create_app():
    app = Flask(__name__)

    app.debug = flack_config.DEBUG
    app.host = flack_config.HOST
    app.port = flack_config.PORT

    app.register_blueprint(frontend)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()