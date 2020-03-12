from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from datetime import datetime, timedelta
import jwt
from time import time
from flask_login import UserMixin

from flask_admin.contrib.sqla import ModelView
from app import admin
from flask_admin import BaseView, expose
from flask_admin.contrib import sqla
from flask_security import RoleMixin, SQLAlchemyUserDatastore, current_user, utils
from wtforms import PasswordField
from flask import abort

from flask import render_template


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


supervisor_table = db.Table('supervisor_table',
                            db.Column('employee_id', db.Integer, db.ForeignKey('user.id')),
                            db.Column('supervisor_id', db.Integer, db.ForeignKey('user.id'))
                            )

received_messages_table = db.Table('received_messages_table',
                                   db.Column('received_msg_id', db.Integer, db.ForeignKey('user.id')),
                                   db.Column('receivers_id', db.Integer, db.ForeignKey('message.id'))
                                   )

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    position = db.Column(db.String(64))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))

    auth_level = db.Column(db.Integer)
    login_attempts = db.Column(db.Integer)
    supervisor = db.relationship(
        'User', secondary=supervisor_table,
        primaryjoin=(supervisor_table.c.supervisor_id == id),
        secondaryjoin=(supervisor_table.c.employee_id == id),
        backref=db.backref('subordinate', lazy='dynamic'),
        lazy='dynamic'
    )
    roles = db.relationship(
        'Role',
        secondary=roles_users,
        backref=db.backref('users', lazy='dynamic')
    )

    team = db.relationship('Team', foreign_keys=team_id, backref='team_members')
    reclamation_req = db.relationship('Reclamation', backref='reclamation_requester', lazy='dynamic')
    ticket_req = db.relationship('Ticket', backref='ticket_requester', lazy='dynamic',
                                 foreign_keys='[Ticket.requester]')
    ticket_ass = db.relationship('Ticket', backref='ticket_assigned', lazy='dynamic',
                                 foreign_keys='[Ticket.assigned_employee]')
    note_draf = db.relationship('Note', backref='note_drafter', lazy='dynamic')
    part_no_person = db.relationship('PartNo', backref='part_no_person_in_charge', lazy='dynamic')
    received_messages = db.relationship('Message', secondary=received_messages_table, backref='receivers')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {
                'reset_password': self.id,
                'exp': time() + expires_in
            },
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        ).decode('utf-8')

    @staticmethod
    def verify_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def has_role(self, role):
        if role in self.roles:
            return True
        return False


class Reclamation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requester = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    informed_date = db.Column(db.DateTime, index=True, nullable=False)
    due_date = db.Column(db.DateTime, index=True)
    finished_date = db.Column(db.DateTime, index=True)
    part_sn = db.Column(db.Integer, db.ForeignKey('part_details.part_sn'), nullable=False)
    description_reclamation = db.Column(db.String(512), nullable=False)
    status = db.Column(db.Integer, nullable=False)

    tickets = db.relationship('Ticket', backref='reclamation', lazy='dynamic')

    def __init__(self, requester, customer_id, informed_date, part_sn,
                 description_reclamation, status, due_date=None, finished_date=None):
        self.requester = requester
        self.customer_id = customer_id
        self.informed_date = informed_date
        self.due_date = due_date if due_date else informed_date + timedelta(days=30)
        self.finished_date = finished_date
        self.part_sn = part_sn
        self.description_reclamation = description_reclamation
        self.status = status


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requester = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_employee = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creation_date = db.Column(db.DateTime, index=True)
    due_date = db.Column(db.DateTime, index=True)
    finished_date = db.Column(db.DateTime, index=True)
    description_ticket = db.Column(db.String(512), nullable=False)
    status = db.Column(db.Integer, nullable=False)
    reclamation_id = db.Column(db.Integer, db.ForeignKey('reclamation.id'), nullable=False)

    note_tic = db.relationship('Note', backref='ticket', lazy='dynamic')

    def __init__(self, requester, assigned_employee, description_ticket, status, reclamation_id,
                 due_date=None, finished_date=None):
        self.requester = requester
        self.assigned_employee = assigned_employee
        self.creation_date = datetime.utcnow()
        self.due_date = due_date if due_date else self.creation_date + timedelta(days=30)
        self.finished_date = finished_date
        self.description_ticket = description_ticket
        self.status = status
        self.reclamation_id = reclamation_id


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    drafter = db.Column(db.Integer, db.ForeignKey('user.id'))
    creation_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'))
    content = db.Column(db.String(512))


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    phone_no = db.Column(db.String(12))

    reclamation_cus = db.relationship('Reclamation', backref='reclamation_customer', lazy='dynamic')


class PartDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    part_no_id = db.Column(db.Integer, db.ForeignKey('part_no.id'))
    production_date = db.Column(db.DateTime, index=True)
    part_sn = db.Column(db.String(120), unique=True)

    reclamation_p_sn = db.relationship('Reclamation', backref='reclamation_part_sn', lazy='dynamic')


class PartNo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(120), unique=True)
    manufacturer = db.Column(db.String(120), unique=True)
    person_in_charge = db.Column(db.Integer, db.ForeignKey('user.id'))

    part_no_list = db.relationship('PartDetails', backref='part_no', lazy='dynamic')


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(32), unique=True)
    team_leader_id = db.Column(db.Integer, db.ForeignKey('user.id', use_alter=True, name='fk_team_leader_id'))

    team_leader = db.relationship('User', foreign_keys=team_leader_id, post_update=True)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(512), nullable=False)
    status = db.Column(db.Integer)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id', use_alter=True, name='fk_sender_id'))

    sender = db.relationship('User', foreign_keys=sender_id, post_update=True)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    # __str__ is required by Flask-Admin, so we can have human-readable values for the Role when editing a User.
    def __str__(self):
        return self.name

    # __hash__ is required to avoid the exception TypeError: unhashable type: 'Role' when saving a User
    def __hash__(self):
        return hash(self.name)


user_datastore = SQLAlchemyUserDatastore(db, User, Role)


class NotificationsView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/notify.html')

    def is_accessible(self):
        return current_user.has_role('admin')


class UserAdmin(sqla.ModelView):
    page_size = 50  # the number of entries to display on the list view
    column_exclude_list = ('password',)
    form_excluded_columns = ('password',)
    # Automatically display human-readable names for the current and available Roles when creating or editing a User
    column_auto_select_related = True

    def is_accessible(self):
        return current_user.has_role('admin')

    # On the form for creating or editing a User, don't display a field corresponding to the model's password field.
    # There are two reasons for this. First, we want to encrypt the password before storing in the database. Second,
    # we want to use a password field (with the input masked) rather than a regular text field.
    def scaffold_form(self):
        # Start with the standard form as provided by Flask-Admin. We've already told Flask-Admin to exclude the
        # password field from this form.
        form_class = super(UserAdmin, self).scaffold_form()

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


class RoleAdmin(sqla.ModelView):
    page_size = 50  # the number of entries to display on the list view
    can_delete = False  # disable model deletion
    def is_accessible(self):
        return current_user.has_role('admin')
        # return True

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        # return redirect(url_for('login', next=request.url))
        return render_template('index.html')


admin.add_view(UserAdmin(User, db.session))
admin.add_view(RoleAdmin(Role, db.session))
admin.add_view(NotificationsView(name='Notifications', endpoint='notify'))

# from flask_admin import helpers as admin_helpers
# @security.context_processor
# def security_context_processor():
#     return dict(
#         admin_base_template=admin.base_template,
#         admin_view=admin.index_view,
#         h=admin_helpers,
#         get_url=url_for
#     )
