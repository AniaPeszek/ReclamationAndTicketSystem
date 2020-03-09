"""initial

Revision ID: a7112e4142f7
Revises: 
Create Date: 2020-03-09 15:20:04.983235

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7112e4142f7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('customer',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('phone_no', sa.String(length=12), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_customer_email'), 'customer', ['email'], unique=True)
    op.create_table('note',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('drafter', sa.Integer(), nullable=True),
    sa.Column('creation_date', sa.DateTime(), nullable=True),
    sa.Column('ticket_id', sa.Integer(), nullable=True),
    sa.Column('content', sa.String(length=512), nullable=True),
    sa.ForeignKeyConstraint(['drafter'], ['user.id'], ),
    sa.ForeignKeyConstraint(['ticket_id'], ['ticket.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_note_creation_date'), 'note', ['creation_date'], unique=False)
    op.create_table('part_details',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('part_no', sa.Integer(), nullable=True),
    sa.Column('production_date', sa.DateTime(), nullable=True),
    sa.Column('part_sn', sa.String(length=120), nullable=True),
    sa.ForeignKeyConstraint(['part_no'], ['part_no.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('part_sn')
    )
    op.create_index(op.f('ix_part_details_production_date'), 'part_details', ['production_date'], unique=False)
    op.create_table('part_no',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('model', sa.String(length=120), nullable=True),
    sa.Column('manufacturer', sa.String(length=120), nullable=True),
    sa.Column('person_in_charge', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['person_in_charge'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('manufacturer'),
    sa.UniqueConstraint('model')
    )
    op.create_table('reclamation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('requester', sa.Integer(), nullable=True),
    sa.Column('customer_id', sa.Integer(), nullable=True),
    sa.Column('informed_date', sa.DateTime(), nullable=True),
    sa.Column('due_date', sa.DateTime(), nullable=True),
    sa.Column('finished_date', sa.DateTime(), nullable=True),
    sa.Column('part_sn', sa.Integer(), nullable=True),
    sa.Column('description_reclamation', sa.String(length=512), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['customer_id'], ['customer.id'], ),
    sa.ForeignKeyConstraint(['part_sn'], ['part_details.part_sn'], ),
    sa.ForeignKeyConstraint(['requester'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reclamation_due_date'), 'reclamation', ['due_date'], unique=False)
    op.create_index(op.f('ix_reclamation_finished_date'), 'reclamation', ['finished_date'], unique=False)
    op.create_index(op.f('ix_reclamation_informed_date'), 'reclamation', ['informed_date'], unique=False)
    op.create_table('supervisor_table',
    sa.Column('employee_id', sa.Integer(), nullable=True),
    sa.Column('supervisor_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['employee_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['supervisor_id'], ['user.id'], )
    )
    op.create_table('team',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('team_name', sa.String(length=32), nullable=True),
    sa.Column('team_leader_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['team_leader_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('team_name')
    )
    op.create_table('ticket',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('requester', sa.Integer(), nullable=True),
    sa.Column('assigned_employee', sa.Integer(), nullable=True),
    sa.Column('creation_date', sa.DateTime(), nullable=True),
    sa.Column('due_date', sa.DateTime(), nullable=True),
    sa.Column('finished_date', sa.DateTime(), nullable=True),
    sa.Column('description_ticket', sa.String(length=512), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('reclamation_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['assigned_employee'], ['user.id'], ),
    sa.ForeignKeyConstraint(['reclamation_id'], ['reclamation.id'], ),
    sa.ForeignKeyConstraint(['requester'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ticket_creation_date'), 'ticket', ['creation_date'], unique=False)
    op.create_index(op.f('ix_ticket_due_date'), 'ticket', ['due_date'], unique=False)
    op.create_index(op.f('ix_ticket_finished_date'), 'ticket', ['finished_date'], unique=False)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=64), nullable=True),
    sa.Column('last_name', sa.String(length=64), nullable=True),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('position', sa.String(length=64), nullable=True),
    sa.Column('team_id', sa.Integer(), nullable=True),
    sa.Column('auth_level', sa.Integer(), nullable=True),
    sa.Column('login_attempts', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['team_id'], ['team.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_ticket_finished_date'), table_name='ticket')
    op.drop_index(op.f('ix_ticket_due_date'), table_name='ticket')
    op.drop_index(op.f('ix_ticket_creation_date'), table_name='ticket')
    op.drop_table('ticket')
    op.drop_table('team')
    op.drop_table('supervisor_table')
    op.drop_index(op.f('ix_reclamation_informed_date'), table_name='reclamation')
    op.drop_index(op.f('ix_reclamation_finished_date'), table_name='reclamation')
    op.drop_index(op.f('ix_reclamation_due_date'), table_name='reclamation')
    op.drop_table('reclamation')
    op.drop_table('part_no')
    op.drop_index(op.f('ix_part_details_production_date'), table_name='part_details')
    op.drop_table('part_details')
    op.drop_index(op.f('ix_note_creation_date'), table_name='note')
    op.drop_table('note')
    op.drop_index(op.f('ix_customer_email'), table_name='customer')
    op.drop_table('customer')
    # ### end Alembic commands ###
