from django.test import TestCase
from django.urls import reverse


class PublicPageTests(TestCase):
    def test_public_pages_load(self):
        for name in ["core:home", "core:about", "core:services", "core:contact"]:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, f"{name} did not return 200")

    def test_contact_form_submission_redirects(self):
        response = self.client.post(reverse("core:contact"), {
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Question about pricing",
            "message": "How much for a full POS setup?",
        })
        self.assertEqual(response.status_code, 302)
