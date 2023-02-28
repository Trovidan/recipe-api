"""Test for User api."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicUserApi(TestCase):
    """Test public feature of the user API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test user creation is success"""
        payload = {
            'email': 'test@example.com',
            'password': 'Test@123',
            'name': 'Test Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        payload = {
            'email': 'test@example.com',
            'password': 'Test@123',
            'name': 'Test Name'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_with_weak_pass_error(self):
        """Test error returned if weak password."""
        payload = {
            'email': 'testWeakPass@example.com',
            'password': 'test',
            'name': 'Test Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_user_token_creation(self):
        """Test token generation for valid credentials"""
        user_details = {
            'email': 'test@example.com',
            'password': 'Test@123',
            'name': 'Test Name'
        }
        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password']
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_token_creation_invalid_credentials(self):
        "Test for token creation for invalid credentials"
        user_details = {
            'email': 'testInvalidCred@example.com',
            'password': 'Test@123',
            'name': 'Test Name'
        }
        create_user(**user_details)

        invalid_creds = [
            ('', 'invalid_creds'),
            (user_details['email'], 'invalid_creds'),
            (user_details['email'], ''),
            ('invalid_email', ''),
            ('invalid_email', user_details['password'])
        ]

        for (email, password) in invalid_creds:
            payload = {
                'email': email,
                'password': password
            }
            res = self.client.post(TOKEN_URL, payload)

            self.assertNotIn('token', res.data)
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test auth is required for user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API request that require authentication"""

    def setUp(self):
        self.user = create_user(
            email="authTest@example.com",
            password="Test@123",
            name="Test User"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test usere profile retrieval"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        """Test Post is disabled for me endpoint"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test user profile updation"""
        payload = {'name': 'Updated Name', 'password': 'newPassword@123'}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(self.user.name, payload['name'])
