
from unittest.mock import patch

import requests

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import SavedRepository


class RepositoryTests(TestCase):

    def setUp(self):
        # Create a test user and log them in
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPassword123!'
        )
        self.client.force_login(self.user)

    @patch('repositories.views.requests.get')
    def test_save_repository(self, mock_get):
        # Simulate a successful response from GitHub
        mock_get.return_value.json.return_value = {
            'id': 12345,
            'full_name': 'django/django',
            'description': 'A Python web framework',
            'html_url': 'https://github.com/django/django',
            'language': 'Python',
        }

        response = self.client.post(
            reverse('save_repository', args=['django', 'django'])
        )

        self.assertEqual(response.status_code, 302)

        # Check that the repository belongs to the test user
        self.assertTrue(
            SavedRepository.objects.filter(
                user=self.user,
                github_id=12345
            ).exists()
        )


    @patch('repositories.views.requests.get')
    def test_duplicate_repository_is_prevented(self, mock_get):
        # Simulate repository data from GitHub
        mock_get.return_value.json.return_value = {
            'id': 12345,
            'full_name': 'django/django',
            'description': 'A Python web framework',
            'html_url': 'https://github.com/django/django',
            'language': 'Python',
        }

        url = reverse('save_repository', args=['django', 'django'])

        # Attempt to save the same repository twice
        self.client.post(url)
        self.client.post(url)

        # Confirm that only one record exists
        self.assertEqual(
            SavedRepository.objects.filter(
                user=self.user,
                github_id=12345
            ).count(),
            1
        )
        
    def test_remove_repository(self):
        # Create a saved repository for the test user
        repository = SavedRepository.objects.create(
            user=self.user,
            github_id=12345,
            name='django/django',
            description='A Python web framework',
            url='https://github.com/django/django',
            language='Python'
        )

        response = self.client.post(
            reverse('remove_repository', args=[repository.pk])
        )

        self.assertRedirects(response, reverse('dashboard'))

        # Confirm the repository has been removed
        self.assertFalse(
            SavedRepository.objects.filter(
                pk=repository.pk
            ).exists()
        )

    def test_user_cannot_remove_another_users_repository(self):
        # Create a second user
        other_user = User.objects.create_user(
            username='otheruser',
            password='TestPassword456!'
        )

        # Create a repository belonging to the second user
        repository = SavedRepository.objects.create(
            user=other_user,
            github_id=67890,
            name='django/django',
            url='https://github.com/django/django',
            language='Python'
        )

        # Attempt to remove another user's repository
        response = self.client.post(
            reverse('remove_repository', args=[repository.pk])
        )

        self.assertEqual(response.status_code, 404)

        # Confirm the repository still exists
        self.assertTrue(
            SavedRepository.objects.filter(
                pk=repository.pk
            ).exists()
        )

    def test_filter_repositories_by_language(self):
        # Create repositories with different languages
        SavedRepository.objects.create(
            user=self.user,
            github_id=12345,
            name='django/django',
            url='https://github.com/django/django',
            language='Python'
        )

        SavedRepository.objects.create(
            user=self.user,
            github_id=67890,
            name='facebook/react',
            url='https://github.com/facebook/react',
            language='JavaScript'
        )

        # Filter the dashboard by Python
        response = self.client.get(
            reverse('dashboard'),
            {'language': 'Python'}
        )

        self.assertEqual(response.status_code, 200)

        # Confirm only the Python repository is displayed
        self.assertContains(response, 'django/django')
        self.assertNotContains(response, 'facebook/react')


    @patch('repositories.views.requests.get')
    def test_search_repositories(self, mock_get):
        # Simulate search results from GitHub
        mock_get.return_value.json.return_value = {
            'items': [
                {
                    'id': 12345,
                    'full_name': 'django/django',
                    'name': 'django',
                    'owner': {'login': 'django'},
                    'description': 'A Python web framework',
                    'html_url': 'https://github.com/django/django',
                    'language': 'Python',
                }
            ]
        }

        response = self.client.get(
            reverse('repository_search'),
            {'q': 'django'}
        )

        self.assertEqual(response.status_code, 200)

        # Confirm the search results are displayed
        self.assertContains(response, 'django/django')
        self.assertContains(response, 'A Python web framework')


    @patch('repositories.views.requests.get')
    def test_github_api_error(self, mock_get):
        # Simulate a failed connection to GitHub
        mock_get.side_effect = requests.ConnectionError(
            "Connection failed"
        )

        response = self.client.get(
            reverse('repository_search'),
            {'q': 'django'}
        )

        self.assertEqual(response.status_code, 200)

        # Confirm a friendly error message is displayed
        self.assertContains(
            response,
            'Unable to retrieve repositories. Please try again.'
        )




