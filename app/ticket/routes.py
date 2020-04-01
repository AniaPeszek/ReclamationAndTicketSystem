from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from flask_babelex import _

from app import db
from app.models import Ticket, Reclamation
from app.ticket import bp
from app.ticket.forms import TicketForm, AssignedUserTicketForm, ReadOnlyTicketForm, \
    RequesterTicketForm, TicketFromReclamationForm, CloseTicketForm, ReopenTicketForm
from app.users.notification import send_message
from app.models_serialized import ticket_schema


@bp.route('/new_ticket/<rec_id>', methods=['GET', 'POST'])
@login_required
def new_ticket(rec_id=0):
    if rec_id == 0:
        form = TicketForm()
        if form.validate_on_submit():
            new_ticket = Ticket(ticket_requester=current_user,
                                ticket_assigned=form.assigned_employee.data,
                                due_date=form.due_date.data,
                                description_ticket=form.description_ticket.data,
                                reclamation=form.reclamation.data)
            db.session.add(new_ticket)
            db.session.commit()
            send_message(Ticket, new_ticket.id, new_ticket.ticket_assigned)
            return redirect(url_for('ticket_bp.ticket', ticket_number=str(new_ticket.id)))
    else:
        form = TicketFromReclamationForm()
        reclamation = Reclamation.query.filter_by(id=int(rec_id)).first_or_404()

        form.reclamation.data = reclamation
        if form.validate_on_submit():
            new_ticket = Ticket(ticket_requester=current_user,
                                ticket_assigned=form.assigned_employee.data,
                                due_date=form.due_date.data,
                                description_ticket=form.description_ticket.data,
                                reclamation=reclamation)
            db.session.add(new_ticket)
            db.session.commit()
            send_message(Ticket, new_ticket.id, new_ticket.ticket_assigned)
            return redirect(url_for('ticket_bp.ticket', ticket_number=str(new_ticket.id)))
        return render_template('ticket/new_ticket.html', form=form)


@bp.route('/ticket/<ticket_number>', methods=['GET', 'POST'])
@login_required
def ticket(ticket_number):
    ticket = Ticket.query.get(ticket_number)
    requester = ticket.ticket_requester.username
    reclamation_number = ticket.reclamation_id
    status = _("Open") if ticket.status == 0 else _("Closed")
    close_form = CloseTicketForm()
    open_form = ReopenTicketForm()

    if ticket.status == 1:
        form = ReadOnlyTicketForm(formdata=request.form,
                                  obj=ticket,
                                  assigned_employee=ticket.ticket_assigned,
                                  reclamation=ticket.reclamation)

        if current_user.id == ticket.ticket_requester.id or current_user.id == ticket.ticket_assigned.id:

            if open_form.validate_on_submit():
                ticket.finished_date = None
                ticket.status = 0
                db.session.add(ticket)
                db.session.commit()
                flash('Ticket has been re-opened')
                return redirect(url_for('ticket_bp.ticket', ticket_number=ticket.id))

    else:

        if current_user.id == ticket.ticket_requester.id:
            form = RequesterTicketForm(formdata=request.form,
                                       obj=ticket,
                                       assigned_employee=ticket.ticket_assigned,
                                       reclamation=ticket.reclamation)


        elif current_user.id == ticket.ticket_assigned.id:
            form = AssignedUserTicketForm(formdata=request.form,
                                          obj=ticket,
                                          assigned_employee=ticket.ticket_assigned,
                                          reclamation=ticket.reclamation)

    if form.validate_on_submit() or close_form.validate_on_submit():
        ticket.ticket_assigned = form.assigned_employee.data
        ticket.reclamation = form.reclamation.data
        ticket.due_date = form.due_date.data
        ticket.description_ticket = form.description_ticket.data
        if close_form.validate_on_submit():
            ticket.finished_date = datetime.utcnow()
        else:
            ticket.finished_date = form.finished_date.data

        if ticket.finished_date is None:
            ticket.status = 0
        else:
            ticket.status = 1

        try:
            if ticket.finished_date < ticket.creation_date:
                flash('Finished date can not be earlier than Creation Date')
                return redirect(url_for('ticket_bp.ticket', ticket_number=ticket.id))
        finally:
            db.session.add(ticket)
            db.session.commit()
            if close_form.validate_on_submit():
                flash('Ticket has been closed')
            else:
                flash('Ticket has been edited')
            return redirect(url_for('ticket_bp.ticket', ticket_number=ticket.id))

    if request.method == "POST":
        return redirect(url_for('reclamation_bp.reclamation', reclamation_number=reclamation_number))

    return render_template('ticket/ticket.html', form=form, requester=requester, status=status, ticket=ticket,
                           reclamation_number=reclamation_number, close_form=close_form, open_form=open_form)


@bp.route('/tickets_get_data', methods=['GET', 'POST'])
@login_required
def tickets_data():
    tickets = Ticket.query.all()
    output = ticket_schema.dump(tickets)
    return jsonify({"tickets": output})


@bp.route('/tickets/all', methods=['GET', 'POST'])
@login_required
def tickets_all():
    return render_template('ticket/tickets_all.html')


@bp.route('/my_tickets')
@login_required
def my_tickets():
    return render_template('ticket/my_tickets.html')


@bp.route('/my_tickets_get_data', methods=['GET', 'POST'])
@login_required
def my_tickets_data():
    tickets = Ticket.query.filter_by(assigned_employee_id=current_user.id).all()
    output = ticket_schema.dump(tickets)
    return jsonify({"tickets": output})
