import json
import unittest

from flask import url_for, request
from flask_login import current_user

from app import create_app, db
from app.models import Role, User
from config import TestingConfig
from tests.tests_basic import BaseTestCase


class UserModelTestCase(BaseTestCase):
    def test_password_verification(self):
        user = User(first_name='John', last_name='Smith', username='johnsmith')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        self.assertTrue(user.check_password('password'))
        self.assertFalse(user.check_password('Password'))

    def test_user_is_administrator(self):
        user = User(first_name='John', last_name='Smith', username='johnsmith')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        self.assertFalse(user.is_administrator())

    def test_admin_is_administrator(self):
        user = User(first_name='John', last_name='Smith', username='johnsmith')
        user.set_password('secret')
        db.session.add(user)
        role_admin = Role.query.filter_by(name='admin').first()
        user.role = role_admin
        db.session.commit()
        self.assertTrue(user.is_administrator())

    def test_user_has_role_user_by_default(self):
        user = User(first_name='John', last_name='Smith', username='johnsmith')
        db.session.add(user)
        user.set_password('secret')
        db.session.commit()
        role_user = Role.query.filter_by(name='user').first()
        self.assertTrue(user.role == role_user)


class UserAuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(use_cookies=True)
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_successful_login(self):
        payload = example_user_data(first_name='John')
        with self.client as client:
            response = client.post('/auth/login', headers={"content-type": "application/json"},
                                   data=payload,
                                   follow_redirects=True)
            self.assertTrue(current_user.is_authenticated)
            self.assertFalse(current_user.is_anonymous)
            self.assertTrue(current_user.first_name == 'John')
            self.assertEqual(200, response.status_code)

    def test_incorrect_login_fail(self):
        user = User(first_name='John', last_name='Smith', username='johnsmith')
        user.set_password('secret')
        db.session.add(user)
        db.session.commit()
        payload = json.dumps({
            "username": "johnsmith",
            "password": "my_secret"
        })

        with self.app.test_client() as client:
            response = client.post('/auth/login', headers={"content-type": "application/json"},
                                   data=payload,
                                   follow_redirects=True)
            self.assertFalse(current_user.is_authenticated)
            self.assertTrue(current_user.is_anonymous)
            self.assertEqual(200, response.status_code)

    def test_logged_user_can_logout(self):
        payload = example_user_data()
        with self.client as client:
            response = client.post('/auth/login', headers={"content-type": "application/json"},
                                   data=payload,
                                   follow_redirects=True)
            self.assertTrue(current_user.is_authenticated)
            self.assertFalse(current_user.is_anonymous)
            self.assertTrue(current_user.first_name == 'John')
            self.assertEqual(200, response.status_code)
            client.get('/auth/logout', follow_redirects=True)
            self.assertFalse(current_user.is_authenticated)
            self.assertTrue(current_user.is_anonymous)

    def test_anonymous_can_not_see_tickets_get_data(self):
        with self.client as client:
            client.get('/tickets_get_data', follow_redirects=True)
            self.assertEqual(request.path, url_for('auth.login'))

    def test_anonymous_can_not_see_reclamation_get_data(self):
        with self.client as client:
            client.get('/reclamation_get_data', follow_redirects=True)
            self.assertEqual(request.path, url_for('auth.login'))

    def test_user_can_not_see_admin_view(self):
        payload = example_user_data()
        with self.client as client:
            client.post('/auth/login', headers={"content-type": "application/json"},
                        data=payload,
                        follow_redirects=True)
            response = client.get('/admin/')
            self.assertEqual(403, response.status_code)

    def test_admin_can_see_admin_view(self):
        payload = example_user_data()
        admin = User.query.first()
        admin_role = Role.query.filter_by(name='admin').first()
        admin.role = admin_role
        with self.client as client:
            client.post('/auth/login', headers={"content-type": "application/json"},
                        data=payload,
                        follow_redirects=True)
            response = client.get('/admin/')
            self.assertEqual(200, response.status_code)
            self.assertEqual(request.path, url_for('admin.index'))


def example_user_data(first_name='John', last_name='Smith', username='johnsmith'):
    user = User(first_name=first_name, last_name=last_name, username=username)
    user.set_password('secret')
    db.session.add(user)
    db.session.commit()
    payload = json.dumps({
        "username": username,
        "password": "secret"
    })
    return payload


if __name__ == '__main__':
    unittest.main(verbosity=2)
