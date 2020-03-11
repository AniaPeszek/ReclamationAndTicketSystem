from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired,  Email, EqualTo

from flask_babel import _, lazy_gettext as _l


class LoginForm(FlaskForm):
    username = StringField(_l('Login'), validators=[DataRequired(_l("That field is required"))])
    password = PasswordField(_l('Password'), validators=[DataRequired(_l("That field is required"))])
    remember_me = BooleanField(_l('Remember'))
    submit = SubmitField(_l('Sign in'))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l("Reset password"))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(_l('Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Set a new password'))
