from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_babelex import Babel
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_security import Security
from flask_admin import Admin
from flask_login import LoginManager

from config import Config
from logging.handlers import SMTPHandler
import logging

db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap()
babel = Babel()
mail = Mail()
login = LoginManager()
# from app.admin.routes import MyAdminIndexView
# admin = Admin(name='ERP - Admin', template_mode='bootstrap3', index_view=MyAdminIndexView())
# admin = Admin(name='ERP - Admin', template_mode='bootstrap3')
security = Security()

from app.models import user_datastore

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
    # admin.init_app(app)
    security.init_app(app, user_datastore)

    f_admin = Admin(app, name='ERP - Admin', index_view=MyAdminIndexView(), template_mode='bootstrap3')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    init_admin(f_admin)
    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

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
