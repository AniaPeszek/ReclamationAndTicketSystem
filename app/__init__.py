from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_babel import Babel
from flask_bootstrap import Bootstrap

from config import Config

db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap()
babel = Babel()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    babel.init_app(app)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app


@babel.localeselector
def get_locale():
    return 'en'


from app import models
