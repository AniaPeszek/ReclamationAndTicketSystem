from flask import render_template, flash, redirect, url_for, request, current_app, jsonify

from flask import g
from flask_babelex import _, get_locale
from flask_login import login_required, current_user

from app import get_locale, db
from app.users import bp
from app.users.forms import MessageForm
from app.models import Message, User, Notification

from datetime import datetime


@bp.route('/send_message', methods=['GET', 'POST'])
@login_required
def send_message():
    form = MessageForm()
    if form.validate_on_submit():
        recipient = User.query.get(form.recipient.data.id)
        msg = Message(author=current_user,
                      recipient=recipient,
                      content=form.message.data)
        db.session.add(msg)
        recipient.add_notification('unread_message_count', recipient.new_messages())
        db.session.commit()

        flash(_('Your message has been sent.'))
        return redirect(url_for('main.index'))
    return render_template('users/send_message.html', title=_('Send Message'),
                           form=form)


@bp.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.utcnow()
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    messages = current_user.messages_received.order_by(
        Message.timestamp.desc()).paginate(
        page, current_app.config['ELEMENTS_PER_PAGE'], False)
    next_url = url_for('users.messages', page=messages.next_num) \
        if messages.has_next else None
    prev_url = url_for('users.messages', page=messages.prev_num) \
        if messages.has_prev else None
    return render_template('users/messages.html', messages=messages.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])
