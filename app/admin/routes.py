from werkzeug.security import generate_password_hash
from app import db
from flask_admin import BaseView, expose, AdminIndexView
from flask_admin.contrib import sqla
from flask_admin.menu import MenuLink
from flask_login import current_user
from wtforms import PasswordField, SelectField
from flask_admin.form import rules
from app.permission_decorators import admin_required
from app.models import (
    User,
    Role,
    Reclamation,
    Ticket,
    Note,
    PartNo,
    PartDetails,
    Customer,
    Team,
)


def init_admin(f_admin):
    f_admin.index_view = MyAdminIndexView()
    f_admin.add_view(UserAdminView(User, db.session, endpoint="user"))
    f_admin.add_view(RoleAdminView(Role, db.session))
    f_admin.add_view(ReclamationAdminView(Reclamation, db.session))
    f_admin.add_view(TicketAdminView(Ticket, db.session))
    f_admin.add_view(TeamAdminView(Team, db.session))
    f_admin.add_view(NoteAdminView(Note, db.session))
    f_admin.add_view(CustomerAdminView(Customer, db.session))
    f_admin.add_view(PartDetailsAdminView(PartDetails, db.session))
    f_admin.add_view(PartNoAdminView(PartNo, db.session))
    f_admin.add_link(LogoutMenuLink(name="Logout", category="", url="/auth/logout"))
    f_admin.add_link(LoginMenuLink(name="Login", category="", url="/auth/login"))


class UserAdminView(sqla.ModelView):
    @expose("/")
    @admin_required
    def index_view(self):
        return super(sqla.ModelView, self).index_view()

    page_size = 50
    column_exclude_list = ("password",)
    form_excluded_columns = ("password",)
    # order of fields in form
    form_columns = [
        "first_name",
        "last_name",
        "username",
        "email",
        "team",
        "supervisor",
        "position",
        "subordinate",
        "role",
        "reclamation_req",
        "ticket_ass",
        "part_no_person",
    ]
    column_auto_select_related = True
    column_searchable_list = (
        "username",
        "last_name",
        "first_name",
        "email",
        "position",
    )
    column_default_sort = ("last_name", True)

    # On the form for creating or editing a User, don't display a field corresponding to the model's password field.
    def scaffold_form(self):
        form_class = super(UserAdminView, self).scaffold_form()
        form_class.password2 = PasswordField("New Password")
        return form_class

    # This callback executes when the user saves changes to a newly-created or edited User -- before the changes are
    # committed to the database.
    def on_model_change(self, form, model, is_created):
        if len(model.password2):
            # encrypt the new password prior to storing it in the database. If the password field is blank,
            # the existing password in the database will be retained.
            model.password = generate_password_hash(model.password2)


class RoleAdminView(sqla.ModelView):
    @expose("/")
    @admin_required
    def index_view(self):
        return super(sqla.ModelView, self).index_view()

    page_size = 50
    can_delete = False


class MyAdminIndexView(AdminIndexView):
    @admin_required
    @expose("/")
    def index(self):
        return self.render("admin/index.html")


class ReclamationAdminView(sqla.ModelView):
    @expose("/")
    @admin_required
    def index_view(self):
        return super(sqla.ModelView, self).index_view()

    page_size = 50
    form_overrides = dict(status=SelectField)
    form_args = dict(status=dict(choices=[(0, "open"), (1, "closed")], coerce=int))
    column_auto_select_related = True
    column_filters = [
        "status",
        "reclamation_customer.name",
        "reclamation_part_sn_id.part_sn",
    ]
    column_labels = {
        "status": "Status",
        "reclamation_customer.name": "Customer",
        "reclamation_part_sn_id.part_sn": "Part SN",
    }


class TicketAdminView(sqla.ModelView):
    @expose("/")
    @admin_required
    def index_view(self):
        return super(sqla.ModelView, self).index_view()

    page_size = 50
    form_overrides = dict(status=SelectField)
    form_args = dict(status=dict(choices=[(0, "open"), (1, "closed")], coerce=int))
    column_filters = [
        "creation_date",
        "due_date",
        "finished_date",
        "status",
        "reclamation.reclamation_customer",
        "ticket_requester.last_name",
        "ticket_requester.first_name",
        "ticket_assigned.last_name",
        "ticket_assigned.first_name",
    ]
    column_labels = {
        "reclamation.reclamation_customer": "Customer",
        "ticket_requester.last_name": "Requester last name",
        "ticket_requester.first_name": "Requester first name",
        "ticket_assigned.last_name": "Assigned last name",
        "ticket_assigned.first_name": "Assigned first name",
    }


class NoteAdminView(sqla.ModelView):
    @expose("/")
    @admin_required
    def index_view(self):
        return super(sqla.ModelView, self).index_view()

    page_size = 50


class CustomerAdminView(sqla.ModelView):
    @expose("/")
    @admin_required
    def index_view(self):
        return super(sqla.ModelView, self).index_view()

    page_size = 50
    column_searchable_list = ("name", "email", "phone_no")


class PartDetailsAdminView(sqla.ModelView):
    @expose("/")
    @admin_required
    def index_view(self):
        return super(sqla.ModelView, self).index_view()

    page_size = 50
    column_filters = [
        "part_sn",
        "production_date",
        "part_no.model",
        "part_no.manufacturer",
    ]
    column_labels = {
        "part_sn": "Part Serial Number",
        "part_no.model": "Model",
        "part_no.manufacturer": "Manufacturer",
    }


class PartNoAdminView(sqla.ModelView):
    @expose("/")
    @admin_required
    def index_view(self):
        return super(sqla.ModelView, self).index_view()

    page_size = 50
    column_filters = ["model", "manufacturer"]


class TeamAdminView(sqla.ModelView):
    @expose("/")
    @admin_required
    def index_view(self):
        return super(sqla.ModelView, self).index_view()

    page_size = 50
    column_filters = ["team_name", "team_leader.last_name", "team_leader.first_name"]
    column_labels = {
        "team_name": "Team name",
        "team_leader.last_name": "Team leader last name",
        "team_leader.first_name": "Team leader first name",
    }


class LoginMenuLink(MenuLink):
    def is_accessible(self):
        return not current_user.is_authenticated


class LogoutMenuLink(MenuLink):
    def is_accessible(self):
        return current_user.is_authenticated
