from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.mail import outbox
from unittest.mock import patch
import re


class EmailOTPVerificationTest(TestCase):
    """Test suite for email OTP registration and verification flow"""

    def setUp(self):
        """Set up test client and clear email outbox"""
        self.client = Client()
        self.register_url = reverse('register')
        self.verify_otp_url = reverse('verify_otp')
        self.login_url = reverse('login')
        
        # Test user data
        self.test_email = 'testuser@example.com'
        self.test_password = 'TestPassword123!'
        self.test_full_name = 'Test User'

    def test_user_not_saved_before_otp_verification(self):
        """Test that user is NOT created in database before email OTP verification"""
        # Attempt registration
        response = self.client.post(self.register_url, {
            'full_name': self.test_full_name,
            'email': self.test_email,
            'password': self.test_password,
            'confirm_password': self.test_password,
        })

        # User should NOT exist in database yet
        user_exists = User.objects.filter(email=self.test_email).exists()
        self.assertFalse(user_exists, "User should NOT be saved before OTP verification")

        # Should redirect to verify OTP page
        self.assertRedirects(response, self.verify_otp_url)

    def test_otp_sent_to_email(self):
        """Test that OTP email is sent during registration"""
        # Register and trigger email
        response = self.client.post(self.register_url, {
            'full_name': self.test_full_name,
            'email': self.test_email,
            'password': self.test_password,
            'confirm_password': self.test_password,
        })

        # Check that email was sent
        self.assertEqual(len(outbox), 1, "One email should be sent")
        
        email = outbox[0]
        self.assertEqual(email.to, [self.test_email])
        self.assertIn('OTP', email.subject)
        self.assertIn('verify', email.subject.lower())

    def test_otp_stored_in_session(self):
        """Test that OTP and pending registration data are stored in session"""
        response = self.client.post(self.register_url, {
            'full_name': self.test_full_name,
            'email': self.test_email,
            'password': self.test_password,
            'confirm_password': self.test_password,
        })

        # Get the session from the response
        session = self.client.session
        
        # Verify session contains pending registration data
        self.assertIn('pending_registration', session, "Session should contain pending_registration")
        self.assertIn('registration_otp', session, "Session should contain registration_otp")
        
        pending_data = session['pending_registration']
        self.assertEqual(pending_data['email'], self.test_email)
        self.assertEqual(pending_data['full_name'], self.test_full_name)

    def test_otp_verification_creates_user(self):
        """Test that user is created only AFTER successful OTP verification"""
        # Step 1: Register and get OTP
        response = self.client.post(self.register_url, {
            'full_name': self.test_full_name,
            'email': self.test_email,
            'password': self.test_password,
            'confirm_password': self.test_password,
        })

        # Extract OTP from session
        otp = self.client.session['registration_otp']

        # Step 2: Verify OTP
        response = self.client.post(self.verify_otp_url, {
            'otp': otp,
        })

        # User should NOW exist in database
        user_exists = User.objects.filter(email=self.test_email).exists()
        self.assertTrue(user_exists, "User should be created after OTP verification")

        # Verify user details
        user = User.objects.get(email=self.test_email)
        self.assertEqual(user.first_name, self.test_full_name)
        self.assertTrue(user.check_password(self.test_password))
        self.assertTrue(user.is_active)

    def test_invalid_otp_does_not_create_user(self):
        """Test that wrong OTP does NOT create user"""
        # Step 1: Register
        response = self.client.post(self.register_url, {
            'full_name': self.test_full_name,
            'email': self.test_email,
            'password': self.test_password,
            'confirm_password': self.test_password,
        })

        # Step 2: Submit wrong OTP
        response = self.client.post(self.verify_otp_url, {
            'otp': '000000',  # Wrong OTP
        })

        # User should NOT exist
        user_exists = User.objects.filter(email=self.test_email).exists()
        self.assertFalse(user_exists, "User should NOT be created with wrong OTP")

        # Should stay on verify OTP page with error message
        self.assertContains(response, 'Invalid OTP', status_code=200)

    def test_session_cleared_after_verification(self):
        """Test that session data is cleared after successful verification"""
        # Step 1: Register
        response = self.client.post(self.register_url, {
            'full_name': self.test_full_name,
            'email': self.test_email,
            'password': self.test_password,
            'confirm_password': self.test_password,
        })

        otp = self.client.session['registration_otp']

        # Step 2: Verify OTP
        response = self.client.post(self.verify_otp_url, {
            'otp': otp,
        })

        # Session data should be cleared
        self.assertNotIn('pending_registration', self.client.session, 
                         "pending_registration should be cleared from session")
        self.assertNotIn('registration_otp', self.client.session,
                         "registration_otp should be cleared from session")

        # Should redirect to login
        self.assertRedirects(response, self.login_url)

    def test_cannot_verify_otp_without_registration(self):
        """Test that accessing verify OTP page without registration redirects to register"""
        response = self.client.get(self.verify_otp_url)

        # Should redirect to register page
        self.assertRedirects(response, self.register_url)

    def test_verified_user_can_login(self):
        """Test that verified user can successfully log in"""
        # Step 1: Register
        response = self.client.post(self.register_url, {
            'full_name': self.test_full_name,
            'email': self.test_email,
            'password': self.test_password,
            'confirm_password': self.test_password,
        })

        # Step 2: Verify OTP
        otp = self.client.session['registration_otp']
        response = self.client.post(self.verify_otp_url, {
            'otp': otp,
        })

        # Step 3: Log in with the created user
        user = User.objects.get(email=self.test_email)
        response = self.client.post(self.login_url, {
            'credential': user.username,
            'password': self.test_password,
        })

        # Should redirect to home after successful login
        self.assertRedirects(response, reverse('home'))

    def test_duplicate_email_rejected_at_registration(self):
        """Test that registering with duplicate email is rejected"""
        # Create a user manually
        User.objects.create_user(
            username='existing_user',
            email=self.test_email,
            password='password123'
        )

        # Try to register with same email
        response = self.client.post(self.register_url, {
            'full_name': 'Another User',
            'email': self.test_email,
            'password': self.test_password,
            'confirm_password': self.test_password,
        })

        # Should show error and NOT send OTP
        self.assertContains(response, 'already registered', status_code=200)
        self.assertEqual(len(outbox), 0, "No email should be sent for duplicate email")

    def test_otp_format_validation(self):
        """Test that OTP must be 6 digits"""
        # Register
        response = self.client.post(self.register_url, {
            'full_name': self.test_full_name,
            'email': self.test_email,
            'password': self.test_password,
            'confirm_password': self.test_password,
        })

        # Try submitting with non-6-digit OTP
        response = self.client.post(self.verify_otp_url, {
            'otp': '12345',  # Only 5 digits
        })

        # User should NOT be created
        user_exists = User.objects.filter(email=self.test_email).exists()
        self.assertFalse(user_exists, "User should NOT be created with invalid OTP format")

    def test_multiple_registrations_different_users(self):
        """Test that multiple users can register sequentially"""
        users_data = [
            ('user1@example.com', 'User One', 'Pass123!'),
            ('user2@example.com', 'User Two', 'Pass456!'),
            ('user3@example.com', 'User Three', 'Pass789!'),
        ]

        for email, name, password in users_data:
            # Register
            response = self.client.post(self.register_url, {
                'full_name': name,
                'email': email,
                'password': password,
                'confirm_password': password,
            })

            otp = self.client.session['registration_otp']

            # Verify OTP
            response = self.client.post(self.verify_otp_url, {
                'otp': otp,
            })

            # User should be created
            user = User.objects.get(email=email)
            self.assertEqual(user.first_name, name)

        # All three users should exist
        self.assertEqual(User.objects.filter(email__in=[u[0] for u in users_data]).count(), 3)
