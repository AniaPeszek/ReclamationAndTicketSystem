from werkzeug.security import generate_password_hash
from app import db
from app import admin
from flask_admin import BaseView, expose, AdminIndexView
from flask_admin.contrib import sqla
from flask_admin.menu import MenuLink
from flask_security import current_user
from wtforms import PasswordField, SelectField
from flask_admin.form import rules
from flask import redirect, url_for, request

from app.models import User, Role, Reclamation, Ticket, Note, PartNo, PartDetails, Customer, Team


def init_admin(f_admin):
    admin.index_view = MyAdminIndexView()
    f_admin.add_view(UserAdminView(User, db.session))
    f_admin.add_view(RoleAdminView(Role, db.session))
    f_admin.add_view(ReclamationAdminView(Reclamation, db.session))
    f_admin.add_view(TicketAdminView(Ticket, db.session))
    f_admin.add_view(TeamAdminView(Team, db.session))
    f_admin.add_view(NoteAdminView(Note, db.session))
    f_admin.add_view(CustomerAdminView(Customer, db.session))
    f_admin.add_view(PartDetailsAdminView(PartDetails, db.session))
    f_admin.add_view(PartNoAdminView(PartNo, db.session))
    # nie wiem czy chcemy pokazywać messeges, potraktowałabym je jako prywatne
    # admin.add_view(MessageAdminView(Message, db.session))
    f_admin.add_view(NotificationsView(name='Notifications', endpoint='notify'))
    f_admin.add_link(LogoutMenuLink(name='Logout', category='', url="/logout"))
    f_admin.add_link(LoginMenuLink(name='Login', category='', url="/login"))


# dodatkowy widok, jak nie potrzebujemy to można usunąć
class NotificationsView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/notify.html')

    def is_accessible(self):
        return current_user.has_role('admin')


class UserAdminView(sqla.ModelView):
    page_size = 50
    column_exclude_list = ('password',)
    form_excluded_columns = ('password',)
    # order of fields in form
    form_rules = [
        rules.FieldSet(('first_name', 'last_name', 'username', 'email', 'team', 'supervisor', 'position', 'subordinate',
                        'roles', 'password2', 'reclamation_req', 'ticket_ass', 'part_no_person'), 'User')
    ]
    # Automatically display human-readable names for the current and available Roles when creating or editing a User
    column_auto_select_related = True
    column_searchable_list = ('username', 'last_name', 'first_name', 'email')
    column_default_sort = ('last_name', True)

    def is_accessible(self):
        return current_user.has_role('admin')

    # On the form for creating or editing a User, don't display a field corresponding to the model's password field.
    # There are two reasons for this. First, we want to encrypt the password before storing in the database. Second,
    # we want to use a password field (with the input masked) rather than a regular text field.
    def scaffold_form(self):
        # Start with the standard form as provided by Flask-Admin. We've already told Flask-Admin to exclude the
        # password field from this form.
        form_class = super(UserAdminView, self).scaffold_form()

        # Add a password field, naming it "password2" and labeling it "New Password".
        form_class.password2 = PasswordField('New Password')

        return form_class

    # This callback executes when the user saves changes to a newly-created or edited User -- before the changes are
    # committed to the database.
    def on_model_change(self, form, model, is_created):
        # If the password field isn't blank...
        if len(model.password2):
            # ... then encrypt the new password prior to storing it in the database. If the password field is blank,
            # the existing password in the database will be retained.
            model.password = generate_password_hash(model.password2)

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))


class RoleAdminView(sqla.ModelView):
    page_size = 50
    can_delete = False  # disable model deletion

    def is_accessible(self):
        return current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))


class MyAdminIndexView(AdminIndexView):

    def is_accessible(self):
        return current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))


class ReclamationAdminView(sqla.ModelView):
    page_size = 50
    form_overrides = dict(status=SelectField)
    form_args = dict(
        status=dict(
            choices=[(0, 'waiting'), (1, 'in_progress'), (2, 'finished')]
        ))

    def is_accessible(self):
        return current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))


class TicketAdminView(sqla.ModelView):
    page_size = 50
    form_overrides = dict(status=SelectField)
    form_args = dict(
        status=dict(
            choices=[(0, 'waiting'), (1, 'in_progress'), (2, 'finished')]
        ))

    def is_accessible(self):
        return current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))


class NoteAdminView(sqla.ModelView):
    page_size = 50

    def is_accessible(self):
        return current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))


class CustomerAdminView(sqla.ModelView):
    page_size = 50

    def is_accessible(self):
        return current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))


class PartDetailsAdminView(sqla.ModelView):
    page_size = 50

    def is_accessible(self):
        return current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))


class PartNoAdminView(sqla.ModelView):
    page_size = 50

    def is_accessible(self):
        return current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))


class TeamAdminView(sqla.ModelView):
    page_size = 50

    def is_accessible(self):
        return current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))


class MessageAdminView(sqla.ModelView):
    page_size = 50

    def is_accessible(self):
        return current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))


class LoginMenuLink(MenuLink):

    def is_accessible(self):
        return not current_user.is_authenticated


class LogoutMenuLink(MenuLink):

    def is_accessible(self):
        return current_user.is_authenticated
