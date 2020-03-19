from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField
from wtforms.fields.html5 import DateField
from wtforms_sqlalchemy.fields import QuerySelectField

from app import db
from app.models import Customer, PartNo


class ReclamationForm(FlaskForm):
    customer = QuerySelectField('Customer',
                                query_factory=lambda: db.session.query(Customer).order_by('name'),
                                get_pk=lambda a: a.id,
                                get_label=lambda a: a.name,
                                allow_blank=True)

    informed_date = DateField('Informed Date', format='%Y-%m-%d')
    due_date = DateField('Due Date', format='%Y-%m-%d')
    # finished_date = DateField('Finished Date', format='%Y-%m-%d')
    part_model = QuerySelectField('Part Model',
                                  query_factory=lambda: db.session.query(PartNo).order_by('model'),
                                  get_pk=lambda a: a.id,
                                  get_label=lambda a: a.model,
                                  allow_blank=True)
    part_sn = StringField('Serial Number')
    part_prod_date = DateField('Part Production Date', format='%Y-%m-%d')
    description = TextAreaField('Description of the issue')

    submit = SubmitField('Create a claim')
