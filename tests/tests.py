import unittest

from flask import current_app
from app import create_app, db
from config import TestingConfig

from app.models import Role


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


class ConfigurationTestCase(BaseTestCase):
    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing_conf(self):
        self.assertTrue(current_app.config['TESTING'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
