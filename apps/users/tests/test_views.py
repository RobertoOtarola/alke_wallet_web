"""Integration tests for users views."""

from django.test import Client, TestCase
from django.urls import reverse

from apps.users.models import User


def _create_user(**kwargs):
    defaults = dict(name="Test User", email="test@alke.cl", password="hashed_pw")
    defaults.update(kwargs)
    return User.objects.create(**defaults)


class BaseUserTest(TestCase):
    def setUp(self):
        self.staff_user = _create_user(email="staff@example.com", is_staff=True)
        self.client.force_login(self.staff_user)


class UserListViewTest(BaseUserTest):
    def test_returns_200(self):
        response = self.client.get(reverse("users:user_list"))
        self.assertEqual(response.status_code, 200)

    def test_lists_all_users(self):
        _create_user(email="a@alke.cl")
        _create_user(email="b@alke.cl")
        response = self.client.get(reverse("users:user_list"))
        self.assertEqual(len(response.context["users"]), 3)


class UserCreateViewTest(TestCase):
    def test_get_returns_form(self):
        response = self.client.get(reverse("users:user_create"))
        self.assertEqual(response.status_code, 200)

    def test_post_creates_user_and_redirects(self):
        data = {
            "name": "Nuevo Usuario",
            "email": "nuevo@alke.cl",
            "password": "strongpass1",
            "confirm_password": "strongpass1",
        }
        response = self.client.post(reverse("users:user_create"), data)
        self.assertRedirects(response, reverse("login"))
        self.assertTrue(User.objects.filter(email="nuevo@alke.cl").exists())

    def test_post_with_mismatched_passwords_shows_error(self):
        data = {
            "name": "X",
            "email": "x@alke.cl",
            "password": "pass1234",
            "confirm_password": "other5678",
        }
        response = self.client.post(reverse("users:user_create"), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email="x@alke.cl").exists())


class UserDetailViewTest(BaseUserTest):
    def test_returns_200_for_existing_user(self):
        user = _create_user(email="other@test.com")
        response = self.client.get(reverse("users:user_detail", args=[user.pk]))
        self.assertEqual(response.status_code, 200)

    def test_returns_404_for_missing_user(self):
        response = self.client.get(reverse("users:user_detail", args=[9999]))
        self.assertEqual(response.status_code, 404)


class UserDeleteViewTest(BaseUserTest):
    def test_post_deletes_user(self):
        user = _create_user(email="del@test.com")
        pk = user.pk
        response = self.client.post(reverse("users:user_delete", args=[pk]))
        self.assertFalse(User.objects.filter(pk=pk).exists())
