from flask import current_app
from app import db
from datetime import datetime, timedelta

supervisor_table = db.Table('supervisor_table',
                            db.Column('employee_id', db.Integer, db.ForeignKey('user.id')),
                            db.Column('supervisor_id', db.Integer, db.ForeignKey('user.id'))
                            )


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
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

    reclamation_req = db.relationship('Reclamation', backref='reclamation_requester', lazy='dynamic')
    ticket_req = db.relationship('Ticket', backref='ticket_requester', lazy='dynamic', foreign_keys='[Ticket.requester]')
    ticket_ass = db.relationship('Ticket', backref='ticket_assigned', lazy='dynamic', foreign_keys='[Ticket.assigned_employee]')
    note_draf = db.relationship('Note', backref='note_drafter', lazy='dynamic')
    part_no_person = db.relationship('PartNo', backref='part_no_person_in_charge', lazy='dynamic')
    team_lead = db.relationship('Team', backref='team_leader', lazy='dynamic', foreign_keys='[Team.team_leader_id]')

    def __repr__(self):
        return f'<User {self.username}>'


class Reclamation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requester = db.Column(db.Integer, db.ForeignKey('user.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    informed_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # due_date = db.Column(db.DateTime, index=True, default=(informed_date + timedelta(days=30)))
    due_date = db.Column(db.DateTime, index=True)
    finished_date = db.Column(db.DateTime, index=True)
    part_sn = db.Column(db.Integer, db.ForeignKey('part_details.part_sn'))
    description_reclamation = db.Column(db.String(512))
    status = db.Column(db.Integer)
    # ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'))

    tickets = db.relationship('Ticket', backref='reclamation', lazy='dynamic')


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requester = db.Column(db.Integer, db.ForeignKey('user.id'))
    assigned_employee = db.Column(db.Integer, db.ForeignKey('user.id'))
    creation_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # due_date = db.Column(db.DateTime, index=True, default=(creation_date + timedelta(days=30)))
    due_date = db.Column(db.DateTime, index=True)
    finished_date = db.Column(db.DateTime, index=True)
    description_ticket = db.Column(db.String(512))
    status = db.Column(db.Integer)
    # reclamation_id = db.Column(db.Integer, db.ForeignKey) Relation already fixed -> line 33 and 47

    reclamation_id = db.Column(db.Integer, db.ForeignKey('reclamation.id'))
    # reclamation_tic_id = db.relationship('Reclamation', backref='reclamation_ticket_id', lazy='dynamic')
    note_tic_id = db.relationship('Note', backref='note_ticket_id', lazy='dynamic')


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
    part_no = db.Column(db.Integer, db.ForeignKey('part_no.id'))
    production_date = db.Column(db.DateTime, index=True)
    part_sn = db.Column(db.String(120), unique=True)

    reclamation_p_sn = db.relationship('Reclamation', backref='reclamation_part_sn', lazy='dynamic')


class PartNo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(120), unique=True)
    manufacturer = db.Column(db.String(120), unique=True)
    person_in_charge = db.Column(db.Integer, db.ForeignKey('user.id'))

    part_det_part_no = db.relationship('PartDetails', backref='part_details_part_no', lazy='dynamic')


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(32), unique=True)
    team_leader_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    team_members = db.relationship('User', backref='user_team', lazy='dynamic', foreign_keys='[User.team_id]')
    # team_members = db.relationship('User', backref='user_team', lazy='dynamic')
