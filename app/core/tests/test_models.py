"""
Test for models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful"""
        email = "test@example.com"
        password = 'testPass@123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test User email normalization"""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['teSt3@eXaMple.com', 'teSt3@example.com']
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'Test@123')
            self.assertEqual(user.email, expected)

    def test_new_user_invalid_email(self):
        """Test user creation with invalid Email"""
        invalid_emails = [
            '',
            'example.com',
            '@example.com',
            'test1',
            'test1@examplecom'
        ]
        for email in invalid_emails:
            with self.assertRaises(ValueError):
                get_user_model().objects.create_user(email, 'Test@123')

    def test_super_user_creation(self):
        """Test super user creation"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'Test@123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
