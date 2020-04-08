from app import create_app, db
from app.models import User, Customer, Note, PartDetails, PartNo, Reclamation, Team, Ticket, Message, Role, Notification

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db,
            'User': User,
            'Customer': Customer,
            'Note': Note,
            'PartDetails': PartDetails,
            'PartNo': PartNo,
            'Reclamation': Reclamation,
            'Team': Team,
            'Ticket': Ticket,
            'Message': Message,
            'Role': Role,
            'Notification': Notification}


@app.cli.command()
def test():
        '''Run the unit tests.'''
        import unittest
        tests = unittest.TestLoader().discover('tests')
        unittest.TextTestRunner(verbosity=2).run(tests)
