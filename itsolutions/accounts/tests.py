from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import ClientProfile

User = get_user_model()


class SignUpTests(TestCase):
    def test_signup_creates_user_and_client_profile(self):
        response = self.client.post(reverse("accounts:signup"), {
            "username": "newclient",
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com",
            "phone": "0712345678",
            "company_name": "Jane's Retail Shop",
            "industry": "Retail",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="newclient")
        self.assertTrue(user.is_client)
        self.assertTrue(ClientProfile.objects.filter(user=user, company_name="Jane's Retail Shop").exists())

    def test_signup_logs_user_in(self):
        self.client.post(reverse("accounts:signup"), {
            "username": "newclient2",
            "first_name": "John",
            "last_name": "Smith",
            "email": "john@example.com",
            "company_name": "John's Cafe",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        response = self.client.get(reverse("portal:dashboard"))
        self.assertEqual(response.status_code, 200)
