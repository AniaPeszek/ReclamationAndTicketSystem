from app import create_app, db
from app.models import User, Customer, Note, PartDetails, PartNo, Reclamation, Team, Ticket, Message, Role, \
    Notification, File, Task
from app.example_data.load_data import clear_data, upload_example_data

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
            'Notification': Notification,
            "File": File,
            'Task': Task,
            'clear': clear_data,
            'upload': upload_example_data}


@app.cli.command()
def test():
    '''Run the unit tests.'''
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
