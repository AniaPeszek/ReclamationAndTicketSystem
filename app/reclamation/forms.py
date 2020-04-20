from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField, validators
from wtforms.fields.html5 import DateField, DateTimeField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms_components import read_only

from app import db
from app.models import Customer, PartNo, Reclamation


class ReclamationForm(FlaskForm):
    customer = QuerySelectField('Customer',
                                query_factory=lambda: db.session.query(Customer).order_by('name'),
                                get_pk=lambda a: a.id,
                                get_label=lambda a: a.name,
                                allow_blank=True)

    informed_date = DateField('Informed Date', format='%Y-%m-%d')
    due_date = DateField('Due Date', format='%Y-%m-%d')
    part_model = QuerySelectField('Part Model',
                                  query_factory=lambda: db.session.query(PartNo).order_by('model'),
                                  get_pk=lambda a: a.id,
                                  get_label=lambda a: a.model,
                                  allow_blank=True)
    part_sn = StringField('Serial Number')
    part_prod_date = DateField('Part Production Date', format='%Y-%m-%d')
    description = TextAreaField('Description of the issue')

    submit = SubmitField('Create a claim')


class EditReclamationForm(FlaskForm):
    customer = QuerySelectField('Customer',
                                query_factory=lambda: db.session.query(Customer).order_by('name'),
                                get_pk=lambda a: a.id,
                                get_label=lambda a: a.name,
                                allow_blank=True)

    informed_date = DateField('Informed Date', format='%Y-%m-%d')
    due_date = DateField('Due Date', format='%Y-%m-%d')
    part_model = QuerySelectField('Part Model',
                                  query_factory=lambda: db.session.query(PartNo).order_by('model'),
                                  get_pk=lambda a: a.id,
                                  get_label=lambda a: a.model,
                                  allow_blank=True)
    part_sn = StringField('Serial Number')
    part_prod_date = DateField('Part Production Date', format='%Y-%m-%d')
    description = TextAreaField('Description of the issue')
    finished_date = DateTimeField('Finished Date', format='%Y-%m-%d %H:%M', validators=[validators.Optional()],
                                  render_kw={'readonly': True})

    submit = SubmitField('Edit the claim')


class ReadOnlyReclamationForm(EditReclamationForm):
    def __init__(self, *args, **kwargs):
        super(ReadOnlyReclamationForm, self).__init__(*args, **kwargs)
        read_only(self.customer)
        read_only(self.informed_date)
        read_only(self.due_date)
        read_only(self.part_model)
        read_only(self.part_sn)
        read_only(self.part_prod_date)
        read_only(self.description)
        read_only(self.finished_date)


class CloseReclamationForm(FlaskForm):
    submit1 = SubmitField('Close reclamation')


class ReopenReclamationForm(FlaskForm):
    submit1 = SubmitField('Re-open reclamation')
