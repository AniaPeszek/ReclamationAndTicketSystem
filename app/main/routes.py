from flask import render_template, url_for, current_app, request

from flask import g
from flask_babelex import _, get_locale
from flask_login import login_required, current_user

from app import get_locale
from app.main import bp

from app.models import Message


@bp.before_app_request
def before_request():
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        messages = current_user.messages_received.order_by(
            Message.timestamp.desc()).limit(5)

        return render_template('main/index.html', title=_('Homepage'), messages=messages)
    return render_template('main/index.html', title=_('Homepage'))


@bp.route('/test', methods=['GET', 'POST'])
@login_required
def test():
    return '<h1>This is test</h1>'



