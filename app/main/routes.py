from flask import render_template

from flask import g
from flask_babelex import _, get_locale
from flask_login import login_required

from app import get_locale
from app.main import bp




@bp.before_app_request
def before_request():
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('main/index.html', title=_('Homepage'))



@bp.route('/test', methods=['GET', 'POST'])
@login_required
def test():
    return '<h1>This is test</h1>'



