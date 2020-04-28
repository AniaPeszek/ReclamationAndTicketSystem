from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from datetime import datetime, timedelta
import jwt
from time import time
from flask_login import UserMixin
import json

import redis
import rq

from app.search.search import add_to_index, remove_from_index, query_index


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


supervisor_table = db.Table('supervisor_table',
                            db.Column('employee_id', db.Integer, db.ForeignKey('user.id')),
                            db.Column('supervisor_id', db.Integer, db.ForeignKey('user.id'))
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

    supervisor = db.relationship(
        'User', secondary=supervisor_table,
        primaryjoin=(supervisor_table.c.supervisor_id == id),
        secondaryjoin=(supervisor_table.c.employee_id == id),
        backref=db.backref('subordinate', lazy='dynamic'),
        lazy='dynamic'
    )
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    team = db.relationship('Team', foreign_keys=team_id, backref='team_members')
    reclamation_req = db.relationship('Reclamation', backref='reclamation_requester', lazy='dynamic')
    ticket_req = db.relationship('Ticket', backref='ticket_requester', lazy='dynamic',
                                 foreign_keys='[Ticket.requester_id]')
    ticket_ass = db.relationship('Ticket', backref='ticket_assigned', lazy='dynamic',
                                 foreign_keys='[Ticket.assigned_employee_id]')
    note_draf = db.relationship('Note', backref='note_drafter', lazy='dynamic')
    part_no_person = db.relationship('PartNo', backref='part_no_person_in_charge', lazy='dynamic')

    messages_sent = db.relationship('Message',
                                    foreign_keys='Message.sender_id',
                                    backref='author', lazy='dynamic')
    messages_received = db.relationship('Message',
                                        foreign_keys='Message.recipient_id',
                                        backref='recipient', lazy='dynamic')
    last_message_read_time = db.Column(db.DateTime)

    notifications = db.relationship('Notification', backref='user',
                                    lazy='dynamic')
    tasks = db.relationship('Task', backref='user', lazy='dynamic')

    def launch_task(self, name, description, json_data, *args, **kwargs):
        rq_job = current_app.task_queue.enqueue('app.tasks.' + name, self.id, json_data,
                                                *args, **kwargs)
        task = Task(id=rq_job.get_id(), name=name, description=description,
                    user=self)
        db.session.add(task)
        return task

    def get_tasks_in_progress(self):
        return Task.query.filter_by(user=self, complete=False).all()

    def get_task_in_progress(self, name):
        return Task.query.filter_by(name=name, user=self,
                                    complete=False).first()

    def add_notification(self, name, data):
        self.notifications.filter_by(name=name).delete()
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n

    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(
            Message.timestamp > last_read_time).count()

    def open_tickets(self):
        return Ticket.query.filter_by(ticket_assigned=self).filter_by(status=0).count()

    def __repr__(self):
        return f'<User {self.username}>'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

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

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)


class Reclamation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requester = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    informed_date = db.Column(db.DateTime, index=True, nullable=False)
    due_date = db.Column(db.DateTime, index=True)
    finished_date = db.Column(db.DateTime, index=True)
    part_sn_id = db.Column(db.Integer, db.ForeignKey('part_details.id'), nullable=False)
    description_reclamation = db.Column(db.String(512), nullable=False)
    status = db.Column(db.Integer, nullable=False)

    tickets = db.relationship('Ticket', backref='reclamation', lazy='dynamic')
    note_rec = db.relationship('Note', backref='rec', lazy='dynamic')
    files = db.relationship('File', backref='reclamation', lazy=True)

    def __init__(self, reclamation_requester, reclamation_customer, informed_date, reclamation_part_sn_id,
                 description_reclamation, due_date=None, finished_date=None):
        self.informed_date = informed_date
        self.due_date = due_date if due_date else informed_date + timedelta(days=30)
        self.finished_date = finished_date
        self.description_reclamation = description_reclamation
        self.status = 1 if finished_date else 0
        self.reclamation_requester = reclamation_requester
        self.reclamation_customer = reclamation_customer
        self.reclamation_part_sn_id = reclamation_part_sn_id


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_employee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creation_date = db.Column(db.DateTime, index=True)
    due_date = db.Column(db.DateTime, index=True)
    finished_date = db.Column(db.DateTime, index=True)
    description_ticket = db.Column(db.String(512), nullable=False)
    status = db.Column(db.Integer, nullable=False)
    reclamation_id = db.Column(db.Integer, db.ForeignKey('reclamation.id'), nullable=False)

    def __init__(self, ticket_requester, ticket_assigned, description_ticket, reclamation,
                 due_date=None, finished_date=None):
        self.ticket_requester = ticket_requester
        self.ticket_assigned = ticket_assigned
        self.creation_date = datetime.utcnow()
        self.due_date = due_date if due_date else self.creation_date + timedelta(days=30)
        self.finished_date = finished_date
        self.description_ticket = description_ticket
        self.status = 1 if finished_date else 0
        self.reclamation = reclamation


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    drafter = db.Column(db.Integer, db.ForeignKey('user.id'))
    creation_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    rec_id = db.Column(db.Integer, db.ForeignKey('reclamation.id'))
    content = db.Column(db.String(512))


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    phone_no = db.Column(db.String(12))

    reclamation_cus = db.relationship('Reclamation', backref='reclamation_customer', lazy='dynamic')

    def __repr__(self):
        return self.name


class PartDetails(SearchableMixin, db.Model):
    __searchable__ = ['part_sn']
    id = db.Column(db.Integer, primary_key=True)
    part_no_id = db.Column(db.Integer, db.ForeignKey('part_no.id'))
    production_date = db.Column(db.DateTime, index=True)
    part_sn = db.Column(db.String(120), unique=True)

    reclamation_p_sn = db.relationship('Reclamation', backref='reclamation_part_sn_id', lazy='dynamic')

    def __repr__(self):
        return f'Part SN:{self.part_sn}, ID:{self.id}'


class PartNo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(120), unique=True)
    manufacturer = db.Column(db.String(120))
    person_in_charge = db.Column(db.Integer, db.ForeignKey('user.id'))

    part_no_list = db.relationship('PartDetails', backref='part_no', lazy='dynamic')

    def __repr__(self):
        return f'Model: {self.model}, from: {self.manufacturer}'


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(32), unique=True)
    team_leader_id = db.Column(db.Integer, db.ForeignKey('user.id', use_alter=True, name='fk_team_leader_id'))

    team_leader = db.relationship('User', foreign_keys=team_leader_id, post_update=True)

    def __repr__(self):
        return f'{self.team_name}'


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.String(512), nullable=False)
    status = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Message {}>'.format(self.content)


class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    # __str__ is required by Flask-Admin, so we can have human-readable values for the Role when editing a User.
    def __str__(self):
        return self.name

    # __hash__ is required to avoid the exception TypeError: unhashable type: 'Role' when saving a User
    def __hash__(self):
        return hash(self.name)

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remote_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    # method to update roles or create role if doesn't exist
    @staticmethod
    def insert_roles():
        roles = {
            'user': [Permission.READ, Permission.EDIT],
            'super_user': [Permission.READ, Permission.EDIT, Permission.MODERATE],
            'admin': [Permission.READ, Permission.EDIT, Permission.MODERATE, Permission.ADMIN]
        }
        default_role = 'user'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()


class Permission:
    READ = 1
    EDIT = 2
    MODERATE = 4
    ADMIN = 16


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.Float, index=True, default=time)
    payload_json = db.Column(db.Text)

    def get_data(self):
        return json.loads(str(self.payload_json))


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    path = db.Column(db.String(300), unique=True)
    relative_path = db.Column(db.String(300))
    reclamation_id = db.Column(db.Integer, db.ForeignKey('reclamation.id'))


class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    complete = db.Column(db.Boolean, default=False)

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100
