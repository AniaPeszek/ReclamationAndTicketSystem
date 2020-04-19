from app import db
from app.models import User, Customer, PartDetails, PartNo, Reclamation, Team, Ticket, Role, Message
from app.example_data.load_data_from_txt import load_names

import random
import string
from datetime import datetime, timedelta


def create_admin():
    admin = User(username='admin', first_name='John', last_name='Price', email='admin@test.com',
                 position='administrator')
    admin.set_password('admin')
    role_admin = Role.query.filter_by(name='admin').first()
    admin.role = role_admin
    db.session.add(admin)
    admin.team = Team.query.get(4)
    db.session.commit()


def create_teams():
    for i in range(1, 5):
        team_name = 'Team ' + str(i)
        team = Team(team_name=team_name)
        db.session.add(team)
    db.session.commit()


def create_users():
    first_name_list = load_names('app/example_data/first_names.txt')
    last_name_list = load_names('app/example_data/last_names.txt')
    team_list = Team.query.all()

    for i in range(30):
        first_name = first_name_list[i]
        last_name = last_name_list[i]
        username = first_name.lower() + last_name.lower()
        email = username + '@example.com'
        user = User(username=username, first_name=first_name, last_name=last_name, email=email,
                    last_message_read_time=datetime(2020, 4, 15, 7, 00, 00))
        user.set_password('secret')
        if i < 20:
            if i % 5:
                user.position = 'mechanic'
            else:
                user.position = 'specialist'
        else:
            user.position = 'customer service assistant'
        user.team = team_list[i // 10]

        db.session.add(user)
        db.session.commit()


def set_team_leaders():
    team_list = Team.query.all()
    for team in team_list:
        leader = team.team_members[0]
        team.team_leader = leader
        for user in team.team_members[1:]:
            user.supervisor.append(leader)
    db.session.commit()


def create_customers():
    customer_names = ['SwipeWire', 'SecureSmarter', 'Dwellsmith', 'SaleSmarts', 'Industrus', 'AgencyStack',
                      'CloudQuota', 'Overseek', 'ZapLabs', 'SnapCrowd']
    for name in customer_names:
        email = name.lower() + '@test.com'
        phone_no = "".join([str(random.randint(0, 9)) for i in range(10)])
        customer = Customer(name=name, email=email, phone_no=phone_no)
        db.session.add(customer)
        db.session.commit()


def create_part_no():
    manufacturers = ['Shrim', 'Shrim', 'Kiddeo', 'Conceptial', 'Visight', 'Travelemo', 'Mototive', 'Composey',
                     'Triptivo', 'Triptivo']
    models = ['Wheel-XL13-29', 'Wheel-S-23', 'Frame Gian SLx M', 'Frame Roub Pro 12M',
              'Brake Shim Br-V', 'Brake Shim Kl-V', 'Chain KX X9', 'Chain Shim X9',
              'Rear derailleur XTR-11', 'Rear derailleur RD-M970']
    persons_in_charge = []
    for i in range(10):
        user = User.query.get(random.randint(3, 31))
        persons_in_charge.append(user)

    for i in range(len(models)):
        part = PartNo(model=models[i], manufacturer=manufacturers[i], person_in_charge=persons_in_charge[i].id)
        db.session.add(part)
        db.session.commit()


def create_part_details(model):
    part_sn = get_random_alpha_numeric_string()
    part_no = PartNo.query.filter_by(model=model).first()
    part = PartDetails(part_sn=part_sn, part_no=part_no,
                       production_date=get_random_date(min_year=2018, min_month=1, max_year=2019, max_month=6))
    db.session.add(part)
    db.session.commit()
    return part


def get_random_alpha_numeric_string(string_length=10):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join((random.choice(letters_and_digits) for i in range(string_length)))


def create_reclamation(is_open, model, description_reclamation, tickets_descriptions):
    service_assistants = User.query.filter_by(position='customer service assistant').all()
    customers = Customer.query.all()

    for i in range(len(service_assistants)):
        random_customer_id = random.randint(0, len(customers) - 1)
        part = create_part_details(model)
        if is_open:
            today = datetime.now()
            start_date = today - timedelta(days=30)
            date = get_random_date(min_year=start_date.year, min_month=start_date.month, min_day=start_date.day,
                                   max_year=today.year, max_month=today.month, max_day=today.day)
            finished_date = None
        else:
            date = get_random_date()
            finished_date = date + timedelta(days=random.randint(5, 29))
        recl = Reclamation(reclamation_requester=service_assistants[i],
                           reclamation_customer=customers[random_customer_id],
                           informed_date=date,
                           due_date=date + timedelta(days=30),
                           finished_date=finished_date,
                           reclamation_part_sn_id=part,
                           description_reclamation=description_reclamation)
        db.session.add(recl)
        db.session.commit()
        delay = 0
        for ticket in tickets_descriptions:
            if ticket == 'contact with customer':
                create_ticket(ticket, recl, delay=18, customer_service=True, is_open=is_open)
            else:
                delay += 3
                create_ticket(ticket, recl, delay=delay, is_open=is_open)


def create_reclamations(is_open=False):
    reclamation_data = [{'model': 'Wheel-XL13-29',
                         'description_reclamation': 'buckled bike wheel',
                         'tickets_descriptions': ['remove the tyre and straight the wheel', 'put on the tire',
                                                  'contact with customer']},
                        {'model': 'Wheel-S-23',
                         'description_reclamation': 'buckled bike wheel',
                         'tickets_descriptions': ['remove the tyre and straight the wheel', 'put on the tire',
                                                  'contact with customer']},
                        {'model': 'Rear derailleur XTR-11',
                         'description_reclamation': "rear derailleur does not work properly",
                         'tickets_descriptions': ['check part and repair', 'adjust a rear derailleur',
                                                  'contact with customer']},
                        {'model': 'Rear derailleur RD-M970',
                         'description_reclamation': "rear derailleur does not work properly",
                         'tickets_descriptions': ['check part and repair', 'adjust a rear derailleur',
                                                  'contact with customer']}
                        ]
    for i in range(len(reclamation_data)):
        data = random.choice(reclamation_data)
        create_reclamation(is_open, **data)


def get_random_date(min_year=2019, min_month=10, min_day=1,
                    max_year=datetime.now().year, max_month=datetime.now().month, max_day=1):
    start = datetime(min_year, min_month, min_day, 00, 00, 00)
    end = datetime(max_year, max_month, max_day, 00, 00, 00)
    return start + (end - start) * random.random()


def create_ticket(description, reclamation, delay, customer_service=False, is_open=False):
    if customer_service:
        assigned = User.query.get(random.randint(22, 31))
    else:
        assigned = User.query.get(random.randint(3, 21))
    requester = assigned.team.team_leader
    if is_open:
        finished_date = None
    else:
        finished_date = reclamation.informed_date + timedelta(days=delay + random.randint(0, 2))
    ticket = Ticket(ticket_requester=requester, ticket_assigned=assigned, description_ticket=description,
                    reclamation=reclamation,
                    due_date=reclamation.informed_date + timedelta(days=20),
                    finished_date=finished_date)
    db.session.add(ticket)
    ticket.creation_date = reclamation.informed_date
    db.session.commit()
    create_notification(ticket.id, assigned, requester, ticket.creation_date, reclamation)


def create_notification(id, recipient, author, creation_date, reclamation):
    link = f'/ticket/{id}'
    content = f'''You have new ticket.<br>
Reclamation (id={reclamation.id}) from: {reclamation.reclamation_customer.name}<br>
Part Serial Number: {reclamation.reclamation_part_sn_id.part_sn}<br>
Go to <a href="{link}">ticket.</a> '''

    msg = Message(author=author,
                  recipient=recipient,
                  content=content)
    db.session.add(msg)
    msg.timestamp = creation_date
    db.session.commit()


def upload_example_data():
    Role.insert_roles()
    print('Roles created')
    create_teams()
    print('Teams created')
    create_admin()
    create_users()
    print('Users created')
    set_team_leaders()
    print('Team leaders set')
    create_customers()
    print('Customers created')
    create_part_no()
    print('Part_No created')
    create_reclamations()
    print('1 part of Reclamations created')
    create_reclamations()
    print('2 part of Reclamations created')
    create_reclamations()
    print('3 part of Reclamations created')
    create_reclamations()
    print('4 part of Reclamations created')
    create_reclamations(is_open=True)
    print('Reclamations created')


def clear_data(session):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print('Clear table %s' % table)
        session.execute(table.delete())
    session.commit()
