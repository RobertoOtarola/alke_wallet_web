"""Unit tests for the User model."""

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.users.models import User


class UserModelTest(TestCase):

    def _make_user(self, **kwargs):
        defaults = dict(name="Ana García", email="ana@alke.cl", password="hashed")
        defaults.update(kwargs)
        return User(**defaults)

    def test_str_representation(self):
        user = self._make_user()
        self.assertIn("Ana García", str(user))
        self.assertIn("ana@alke.cl", str(user))

    def test_is_active_defaults_to_true(self):
        user = self._make_user()
        self.assertTrue(user.is_active)

    def test_invalid_email_raises_validation_error(self):
        user = self._make_user(email="not-an-email")
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_email_uniqueness(self):
        User.objects.create(name="A", email="dup@alke.cl", password="x")
        duplicate = User(name="B", email="dup@alke.cl", password="y")
        with self.assertRaises(ValidationError):
            duplicate.full_clean()
