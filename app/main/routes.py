from flask import render_template, url_for, current_app, request

from flask import g
from flask_babelex import _, get_locale
from flask_login import login_required, current_user
from flask import jsonify

from app import get_locale, db
from app.main import bp

from app.models import Message, Ticket, Reclamation
from datetime import datetime, timedelta


@bp.before_app_request
def before_request():
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        messages = current_user.messages_received.order_by(
            Message.timestamp.desc()).limit(5)
        current_user.add_notification('open_tickets_count', current_user.open_tickets())

        return render_template('main/index.html', title=_('Homepage'), messages=messages)
    return render_template('main/index.html', title=_('Homepage'))


@bp.route('/get_tickets_chart_data')
@login_required
def get_tickets_chart_data():
    labels = []
    data = []

    number_of_months = 6
    start = datetime.today()
    end = datetime(start.year, start.month, 1)

    for i in range(number_of_months):
        labels.append(start.strftime("%B"))
        tickets_in_month = db.session.query(Ticket).filter(Ticket.ticket_assigned == current_user). \
            filter(Ticket.finished_date <= start). \
            filter(Ticket.finished_date >= end).count()
        data.append(tickets_in_month)
        start = end - timedelta(seconds=1)
        end = end - timedelta(days=start.day)
    labels = labels[::-1]
    data = data[::-1]

    return jsonify({'payload': {'data': data, 'labels': labels}})


@bp.route('/get_reclamations_chart_data')
@login_required
def get_reclamations_chart_data():
    labels = []
    data = []
    number_of_months = 6

    start = datetime.today()
    end = datetime(start.year, start.month, 1)

    for i in range(number_of_months):
        labels.append(start.strftime("%B"))
        recl_in_month = db.session.query(Reclamation). \
            filter(Reclamation.informed_date <= start). \
            filter(Reclamation.informed_date >= end).count()
        data.append(recl_in_month)
        start = end - timedelta(seconds=1)
        end = end - timedelta(days=start.day)
    labels = labels[::-1]
    data = data[::-1]

    return jsonify({'payload': {'data': data, 'labels': labels}})
