from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length

from flask_babelex import _, lazy_gettext as _l


class MessageForm(FlaskForm):
    message = TextAreaField(_l('Message'), validators=[
        DataRequired(), Length(min=0, max=512)])
    recipient = IntegerField(_l('Recipient id'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))