from app import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    position = db.Column(db.String(64))
    # team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    # supervisor = db.Column(db.Integer, db.ForeignKey)
    auth_level = db.Column(db.Integer)
    login_attempts = db.Column(db.Integer)


class Reclamation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # requestor = db.Column(db.Integer, db.ForeignKey))
    # customer = db.Column(db.Integer, db.ForeignKey))
    informed_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # due_date = db.Column(db.DateTime, index=True, default=datetime.utcnow + 30 dni)
    finished_date = db.Column(db.DateTime, index=True)
    # part_sn = db.Column(db.Integer, db.ForeignKey)
    description_reclamation = db.Column(db.String(512))
    status = db.Column(db.Integer)
    # ticket_id = db.Column(db.Integer, db.ForeignKey)


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # requestor = db.Column(db.Integer, db.ForeignKey))
    # assigned_employee = db.Column(db.Integer, db.ForeignKey))
    creation_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # due_date = db.Column(db.DateTime, index=True, default=datetime.utcnow + 30 dni)
    finished_date = db.Column(db.DateTime, index=True)
    description_ticket = db.Column(db.String(512))
    status = db.Column(db.Integer)
    # reclamation_id = db.Column(db.Integer, db.ForeignKey)


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # drafter = db.Column(db.Integer, db.ForeignKey))
    creation_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # ticket_id = db.Column(db.Integer, db.ForeignKey)
    content = db.Column(db.String(512))


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    phone_no = db.Column(db.String(12))


class PartDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # part_no = db.Column(db.Integer,db.ForeignKey)
    production_date = db.Column(db.DateTime, index=True)
    part_sn = db.Column(db.String(120), unique=True)


class PartDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(120), unique=True)
    manufacturer = db.Column(db.String(120), unique=True)
    # person_in_charge = db.Column(db.Integer, db.ForeignKey))
