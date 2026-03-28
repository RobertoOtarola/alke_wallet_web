"""Unit tests for the users service layer."""

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.users import services
from apps.users.models import User


class CreateUserServiceTest(TestCase):

    def test_creates_user_with_hashed_password(self):
        user = services.create_user("Pedro", "pedro@alke.cl", "secret123")
        self.assertIsInstance(user, User)
        self.assertEqual(user.email, "pedro@alke.cl")
        # Password must be stored as a hash, not plaintext
        self.assertNotEqual(user.password, "secret123")
        self.assertIn("pbkdf2_sha256", user.password)

    def test_duplicate_email_raises_error(self):
        services.create_user("Pedro", "pedro@alke.cl", "secret123")
        with self.assertRaises(ValidationError):
            services.create_user("Pedro2", "pedro@alke.cl", "other456")

    def test_invalid_email_raises_validation_error(self):
        with self.assertRaises(ValidationError):
            services.create_user("X", "bad-email", "pass1234")


class UpdateUserServiceTest(TestCase):

    def setUp(self):
        self.user = services.create_user("María", "maria@alke.cl", "pass1234")

    def test_updates_name_and_email(self):
        updated = services.update_user(
            self.user, name="María López", email="maria.lopez@alke.cl", is_active=True
        )
        self.assertEqual(updated.name, "María López")
        self.assertEqual(updated.email, "maria.lopez@alke.cl")

    def test_deactivate_user(self):
        updated = services.update_user(
            self.user, name=self.user.name, email=self.user.email, is_active=False
        )
        self.assertFalse(updated.is_active)


class DeleteUserServiceTest(TestCase):

    def test_deletes_user(self):
        user = services.create_user("Carlos", "carlos@alke.cl", "pass1234")
        pk = user.pk
        services.delete_user(user)
        self.assertFalse(User.objects.filter(pk=pk).exists())
