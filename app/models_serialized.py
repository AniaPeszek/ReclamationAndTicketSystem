from flask_marshmallow.fields import Hyperlinks, URLFor
from marshmallow import fields

from app import ma
from app.models import PartDetails, PartNo, User, Customer, Reclamation, Ticket


class PartDetailsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PartDetails
        include_fk = True
        include_relationships = True
        load_instance = True


class PartNoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PartNo
        # include_fk = True
        # include_relationships = True
        # load_instance = True


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        include_fk = True
        include_relationships = True
        load_instance = True


class ReclamationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Reclamation
        include_fk = True
        include_relationships = True
        load_instance = True
        exclude = ('customer_id', 'part_sn_id', 'requester', 'tickets', 'reclamation_requester', 'note_rec')

    # reclamation_requester = fields.Nested(UserSchema, only=('username', 'first_name', 'last_name'))
    reclamation_customer = fields.Nested(CustomerSchema, only=('name',))
    #how to show part model?
    reclamation_part_sn_id = fields.Nested(PartDetailsSchema, only=('part_sn', 'part_no.model'))

    _links = Hyperlinks({'self': URLFor('reclamation_bp.reclamation', reclamation_number='<id>')})


class TicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ticket
        include_relationships = True
        load_instance = True
        include_fk = True

    ticket_assigned = fields.Nested(UserSchema, only=('username', 'first_name', 'last_name'))
    reclamation = fields.Nested(ReclamationSchema, only=('reclamation_customer','reclamation_part_sn_id'))
    _links = Hyperlinks({'self': URLFor('ticket_bp.ticket', ticket_number='<id>')})


user_schema = UserSchema(many=True)
customer_schema = CustomerSchema(many=True)
part_no_schema = PartNoSchema(many=True)
part_detail_schema = PartDetailsSchema(many=True)
reclamation_schema = ReclamationSchema(many=True)
ticket_schema = TicketSchema(many=True)
