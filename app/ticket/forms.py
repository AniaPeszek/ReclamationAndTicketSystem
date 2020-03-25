from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.fields.html5 import DateField
from wtforms_components import read_only
from wtforms_sqlalchemy.fields import QuerySelectField

from app import db
from app.models import User, Reclamation


class TicketForm(FlaskForm):
    assigned_employee = QuerySelectField('Assigned Person',
                                         query_factory=lambda: db.session.query(User).order_by('last_name'),
                                         get_pk=lambda a: a.id,
                                         get_label=lambda a: str(a.first_name) + " " + str(a.last_name),
                                         allow_blank=True)
    reclamation_id = QuerySelectField('Reclamation ID',
                                      query_factory=lambda: db.session.query(Reclamation).order_by('due_date'),
                                      get_pk=lambda a: a.id,
                                      get_label=lambda a: str(a.id) + " " + str(
                                          a.reclamation_customer.name) + " " + str(a.reclamation_part_sn_id.part_sn),
                                      allow_blank=True)
    due_date = DateField('Due Date', format='%Y-%m-%d')
    description_ticket = TextAreaField('Description of the ticket')

    submit = SubmitField('Create a ticket')


class EditTicketForm(FlaskForm):
    assigned_employee = QuerySelectField('Assigned Person',
                                         query_factory=lambda: db.session.query(User).order_by('last_name'),
                                         get_pk=lambda a: a.id,
                                         get_label=lambda a: str(a.first_name) + " " + str(a.last_name),
                                         allow_blank=True)
    reclamation_id = QuerySelectField('Reclamation ID',
                                      query_factory=lambda: db.session.query(Reclamation).order_by('due_date'),
                                      get_pk=lambda a: a.id,
                                      get_label=lambda a: str(a.id) + " " + str(
                                          a.reclamation_customer.name) + " " + str(a.reclamation_part_sn_id.part_sn),
                                      allow_blank=True)
    due_date = DateField('Due Date', format='%Y-%m-%d')
    description_ticket = TextAreaField('Description of the ticket')
    finished_date = DateField('Finished Date', format='%Y-%m-%d')

    submit = SubmitField('Edit a ticket')


class AssignedUserTicketForm(EditTicketForm):
    def __init__(self, *args, **kwargs):
        super(EditTicketForm, self).__init__(*args, **kwargs)
        read_only(self.assigned_employee)
        read_only(self.reclamation_id)
        read_only(self.due_date)


class ReadOnlyTicketForm(EditTicketForm):
    def __init__(self, *args, **kwargs):
        super(EditTicketForm, self).__init__(*args, **kwargs)
        read_only(self.assigned_employee)
        read_only(self.reclamation_id)
        read_only(self.due_date)
        read_only(self.description_ticket)
        read_only(self.finished_date)
