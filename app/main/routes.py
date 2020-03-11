from flask import render_template

from flask import g
from flask_babel import _, get_locale


from app import get_locale
from app.main import bp



@bp.before_app_request
def before_request():
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('main/index.html', title=_('Homepage'))
