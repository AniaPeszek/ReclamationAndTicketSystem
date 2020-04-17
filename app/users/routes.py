from flask import render_template, flash, redirect, url_for, request, current_app, jsonify

from flask import g
from flask_babelex import _, get_locale
from flask_login import login_required, current_user

from app import get_locale, db
from app.users import bp
from app.models import Message, User, Notification

from datetime import datetime


@bp.route("/notifications/", defaults={"page_num": 1})
@bp.route('/notifications/<int:page_num>')
@login_required
def notifications(page_num):
    current_user.last_message_read_time = datetime.utcnow()
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()

    messages = current_user.messages_received.order_by(
        Message.timestamp.desc()).paginate(
        page=page_num, per_page=current_app.config['ELEMENTS_PER_PAGE'], error_out=False)

    return render_template('users/notifications.html', messages=messages)


@bp.route('/get_notifications')
@login_required
def get_notifications():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])
