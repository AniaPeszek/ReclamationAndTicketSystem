from app import db
from flask_login import current_user
from app.models import Ticket, Reclamation, User, Message
from flask import url_for


def send_message(EventClass, event_id, recipient):
    if EventClass == Ticket:
        content = create_msg_body_for_new_ticket(event_id)
        msg = Message(author=current_user,
                      recipient=recipient,
                      content=content)
        db.session.add(msg)
        # recipient.add_notification('new_ticket_count', recipient.new_tickets())
        recipient.add_notification('open_tickets_count', recipient.open_tickets())
        recipient.add_notification('unread_message_count', recipient.new_messages())
        db.session.commit()
    if EventClass == Reclamation:
        content = create_msg_body_for_new_reclamation(event_id)
        msg = Message(author=current_user,
                      recipient=recipient,
                      content=content)
        db.session.add(msg)
        recipient.add_notification('unread_message_count', recipient.new_messages())
        db.session.commit()


def create_msg_body_for_new_ticket(event_id):
    link = url_for('ticket_bp.ticket', ticket_number=event_id)
    ticket = Ticket.query.filter_by(id=event_id).first()
    reclamation = ticket.reclamation
    return f'''You have new ticket.<br>
Reclamation (id={reclamation.id}) from: {reclamation.reclamation_customer.name}<br>
Part Serial Number: {reclamation.reclamation_part_sn_id.part_sn}<br>
Go to <a href="{link}">ticket.</a> '''


def create_msg_body_for_new_reclamation(event_id):
    link = url_for('reclamation_bp.reclamation', reclamation_number=event_id)
    reclamation = Reclamation.query.filter_by(id=event_id).first()
    model = reclamation.reclamation_part_sn_id.part_no.model
    return f'You have a new reclamation for your part ({model}).<br>Go to <a href="{link}">reclamation.</a> '
