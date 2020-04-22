from flask import render_template, url_for, current_app, request, redirect

from flask import g
from flask_babelex import _, get_locale
from flask_login import login_required, current_user
from flask import jsonify

from app import get_locale, db
from app.main import bp
from app.search.forms import SearchForm

from app.models import Message, Ticket, Reclamation, PartNo, PartDetails
from datetime import datetime, timedelta

from sqlalchemy import func


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    if current_user.is_authenticated:
        open_tickets = db.session.query(Ticket).filter_by(assigned_employee_id=current_user.id).filter_by(status=0). \
            order_by(Ticket.creation_date.desc()).limit(4).all()

        current_user.add_notification('open_tickets_count', current_user.open_tickets())
        part_models_for_chart = db.session.query(PartNo.model).all()
        part_models_list_for_chart = [part[0] for part in part_models_for_chart]

        if current_user.is_administrator():
            return render_template('main/index_for_admin.html', title=_('Homepage'),
                                   model_list=part_models_list_for_chart)

        return render_template('main/index.html', title=_('Homepage'), open_tickets=open_tickets,
                               model_list=part_models_list_for_chart)
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
@bp.route('/get_reclamations_chart_data/<model>')
@login_required
def get_reclamations_chart_data(model='All Models'):
    labels = []
    data = []
    number_of_months = 6
    start = datetime.today()
    end = datetime(start.year, start.month, 1)

    if model == 'All Models':
        for i in range(number_of_months):
            labels.append(start.strftime("%B"))
            recl_in_month = db.session.query(Reclamation). \
                filter(Reclamation.informed_date <= start). \
                filter(Reclamation.informed_date >= end).count()
            data.append(recl_in_month)
            start = end - timedelta(seconds=1)
            end = end - timedelta(days=start.day)
    else:
        part_no = db.session.query(PartNo).filter_by(model=model).first()
        reclamation_part_join = db.session.query(PartDetails).filter(PartDetails.part_no_id == part_no.id).join(
            Reclamation)
        for i in range(number_of_months):
            labels.append(start.strftime("%B"))
            recl_in_month = reclamation_part_join. \
                filter(Reclamation.informed_date <= start). \
                filter(Reclamation.informed_date >= end).count()
            data.append(recl_in_month)
            start = end - timedelta(seconds=1)
            end = end - timedelta(days=start.day)
    labels = labels[::-1]
    data = data[::-1]

    return jsonify({'payload': {'data': data, 'labels': labels}})


@bp.route('/get_pie_chart_data')
@login_required
def get_pie_chart_data():
    labels = []
    data = []
    today = datetime.today()
    end = datetime(today.year, today.month, 1)
    start = end - timedelta(seconds=1)
    end = end - timedelta(days=start.day)

    last_month_reclamations = db.session.query(Reclamation).filter(Reclamation.informed_date <= start). \
        filter(Reclamation.informed_date >= end).subquery()
    models = db.session.query(PartNo.model, func.count(PartNo.model)). \
        join(PartDetails).join(last_month_reclamations, PartDetails.reclamation_p_sn). \
        group_by(PartNo.model).all()

    for result in models:
        labels.append(result[0])
        data.append(result[1])

    return jsonify({'payload': {'data': data, 'labels': labels}})


@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.index'))
    serial_numbers, total = PartDetails.search(g.search_form.q.data, 1, 100)
    results_q = len(serial_numbers[0].reclamation_p_sn.all())

    return render_template('search/search.html', title='Search', serial_numbers=serial_numbers, results_q=results_q)
