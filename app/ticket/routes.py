from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from datetime import datetime
from flask_babelex import _

from app import db
from app.models import Ticket
from app.ticket import bp
from app.ticket.forms import TicketForm, EditTicketForm, AssignedUserTicketForm, ReadOnlyTicketForm


@bp.route('/ticket', methods=['GET', 'POST'])
@login_required
def new_ticket():
    form = TicketForm()

    if form.validate_on_submit():
        new_ticket = Ticket(ticket_requester=current_user,
                            ticket_assigned=form.assigned_employee.data,
                            due_date=form.due_date.data,
                            description_ticket=form.description_ticket.data,
                            reclamation=form.reclamation_id.data)
        db.session.add(new_ticket)
        db.session.commit()
        return redirect(url_for('ticket_bp.ticket', ticket_number=str(ticket.id)))

    return render_template('ticket/new_ticket.html', form=form)


@bp.route('/ticket/<ticket_number>', methods=['GET', 'POST'])
@login_required
def ticket(ticket_number):
    ticket = Ticket.query.get(ticket_number)
    requester = ticket.ticket_requester.username
    status = _("Open") if ticket.status == 0 else _("Closed")

    if current_user.id == ticket.ticket_requester.id:
        form = EditTicketForm(formdata=request.form,
                              obj=ticket,
                              assigned_employee=ticket.ticket_assigned,
                              reclamation_id=ticket.reclamation)
    elif current_user.id == ticket.ticket_assigned.id:
        form = AssignedUserTicketForm(formdata=request.form,
                                      obj=ticket,
                                      assigned_employee=ticket.ticket_assigned,
                                      reclamation_id=ticket.reclamation)
    else:
        form = ReadOnlyTicketForm(formdata=request.form,
                                  obj=ticket,
                                  assigned_employee=ticket.ticket_assigned,
                                  reclamation_id=ticket.reclamation)

    if form.validate_on_submit():
        ticket.assigned_employee = form.assigned_employee.data
        ticket.reclamation_id = form.reclamation_id.data
        ticket.due_date = form.due_date.data
        ticket.description_ticket = form.description_ticket.data
        ticket.finished_date = form.finished_date.data
        if ticket.finished_date is None:
            ticket.status = 0
        else:
            ticket.status = 1

        try:
            if ticket.finished_date < ticket.creation_date:
                flash('Finished date can not be earlier than Creation Date')
                return redirect(url_for('ticket_bp.ticket', ticket_number=str(ticket.id)))
        finally:
            db.session.add(ticket)
            db.session.commit()
            flash('Ticket has been edited')
            return redirect(url_for('ticket_bp.ticket', ticket_number=str(ticket.id)))
    return render_template('ticket/ticket.html', form=form, requester=requester, status=status, ticket=ticket)
