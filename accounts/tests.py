from django.contrib.auth.models import User
from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse

from .forms import SignUpForm


class SignUpFormTests(TestCase):
    def test_rejects_non_edu(self):
        form = SignUpForm(
            data={
                "username": "someone@gmail.com",
                "password1": "complex-pass-123",
                "password2": "complex-pass-123",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_accepts_edu(self):
        form = SignUpForm(
            data={
                "username": "faculty@university.edu",
                "password1": "complex-pass-123",
                "password2": "complex-pass-123",
            }
        )
        self.assertTrue(form.is_valid())


class RegisterViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_creates_user_and_logs_in(self):
        resp = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser@syr.edu",
                "password1": "register-pass-xyz-99",
                "password2": "register-pass-xyz-99",
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["Location"], "/activities/")
        self.assertTrue(User.objects.filter(username="newuser@syr.edu").exists())
        user = User.objects.get(username="newuser@syr.edu")
        self.assertEqual(user.email, "newuser@syr.edu")

    def test_register_rejects_non_edu(self):
        resp = self.client.post(
            reverse("accounts:register"),
            {
                "username": "bad@gmail.com",
                "password1": "complex-pass-123",
                "password2": "complex-pass-123",
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(username="bad@gmail.com").exists())


class LoginRequiredTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="u@school.edu",
            email="u@school.edu",
            password="pw",
        )

    def test_login_page_loads(self):
        resp = self.client.get(reverse("accounts:login"))
        self.assertEqual(resp.status_code, 200)

    def test_login_post(self):
        resp = self.client.post(
            reverse("accounts:login"),
            {"username": "u@school.edu", "password": "pw"},
        )
        self.assertEqual(resp.status_code, 302)

    def test_login_rejects_non_edu_email(self):
        User.objects.create_user(
            username="legacy@gmail.com",
            email="legacy@gmail.com",
            password="pw",
        )
        resp = self.client.post(
            reverse("accounts:login"),
            {"username": "legacy@gmail.com", "password": "pw"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "university email")


class PasswordResetEduTests(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create_user(
            username="faculty@school.edu",
            email="faculty@school.edu",
            password="old-secret-123",
        )

    def test_password_reset_rejects_non_edu(self):
        mail.outbox.clear()
        resp = self.client.post(
            reverse("accounts:password_reset"),
            {"email": "someone@gmail.com"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        self.assertContains(resp, "university email")

    def test_password_reset_sends_for_edu(self):
        mail.outbox.clear()
        resp = self.client.post(
            reverse("accounts:password_reset"),
            {"email": "faculty@school.edu"},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
