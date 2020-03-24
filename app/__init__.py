from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_babelex import Babel
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_admin import Admin
from flask_login import LoginManager
from flask_moment import Moment
from flask_marshmallow import Marshmallow

from config import Config
from logging.handlers import SMTPHandler
import logging

db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap()
babel = Babel()
mail = Mail()
login = LoginManager()
login.login_view = 'auth.login'
moment = Moment()
ma = Marshmallow()

from app.admin.routes import init_admin, MyAdminIndexView


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    babel.init_app(app)
    mail.init_app(app)
    login.init_app(app)
    moment.init_app(app)
    ma.init_app(app)

    f_admin = Admin(app, name='ERP - Admin', index_view=MyAdminIndexView(), template_mode='bootstrap3')

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    init_admin(f_admin)
    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    from app.users import bp as users_bp
    app.register_blueprint(users_bp, url_prefix='/users')

    from app.reclamation import bp as reclamation_bp
    app.register_blueprint(reclamation_bp)

    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'],
                subject='ERP error',
                credentials=auth,
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

    return app


@babel.localeselector
def get_locale():
    return 'en'


from app import models
