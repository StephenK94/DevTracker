
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class DashboardTests(TestCase):

    # Checks that users must log in to access the dashboard
    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            '/accounts/login/?next=/accounts/dashboard/'
        )
    # chewcks that logged in users can access the dashboard
    def test_logged_in_user_can_access_dashboard(self):
        user = User.objects.create_user(
            username='testuser',
            password='TestPassword123!'
        )

        self.client.force_login(user)

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
class RegistrationTests(TestCase):

    # Checks that registration creates a new user
    def test_user_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'first_name': 'John',
            'email': 'john@example.com',
            'password1': 'SecureTestPassword123!',
            'password2': 'SecureTestPassword123!',
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            User.objects.filter(username='newuser').exists()
        )

    # Checks that duplicate email addresses are rejected 
    def test_duplicate_email_is_rejected(self):
        User.objects.create_user(
            username='existinguser',
            email='john@example.com',
            password='SecureTestPassword123!'
        )

        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'first_name': 'John',
            'email': 'john@example.com',
            'password1': 'SecureTestPassword123!',
            'password2': 'SecureTestPassword123!',
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            User.objects.filter(username='newuser').exists()
        )
        self.assertContains(
            response,
            'This email address is already registered.'
        )
