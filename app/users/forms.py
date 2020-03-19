from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length
from wtforms_sqlalchemy.fields import QuerySelectField

from flask_babelex import _, lazy_gettext as _l
from app import db
from app.models import User


class MessageForm(FlaskForm):
    message = TextAreaField(_l('Message'), validators=[
        DataRequired(), Length(min=0, max=512)])
    recipient = QuerySelectField('Recipient',
                                 query_factory=lambda: db.session.query(User).order_by('last_name'),
                                 get_pk=lambda a: a.id,
                                 get_label=lambda a: a, #return first_name last_name
                                 allow_blank=True,
                                 validators=[DataRequired()])

    submit = SubmitField(_l('Submit'))
