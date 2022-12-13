from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL  = reverse('user:token')
ME_URL = reverse('user:me')

def create_user(**params):
    return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
    """ Testing public API for users """
    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """ Test that create and save a valid user """
        payload = {
            'email': 'test@example.com',
            'password': 'testpassword123',
            'name': 'Test name',
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """ Test that create a user that already exist, must fail """
        payload = {
            'email': 'test@example.com',
            'password': 'testpassword123',
            'name': 'Test name',
        }

        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
    
    def test_password_to_short(self):
        """ Test that the password musr be greater than 5 characters """
        payload = {
            'email': 'test@example.com',
            'password': '1234',
            'name': 'test name',
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """ Test that token is create for user """
        payload = {
            'email': 'test@example.com',
            'password': 'testpassword123',
            'name': 'test name',
        }

        create_user(**payload)
        res =  self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """ Test that make sure token is not create with invalid credentials """
        create_user(email='test@example.com',password='testpass')
        payload = {
            'email': 'test@example.com',
            'password': 'wrong',
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """ Test that token is not created if user dont exists """
        payload = {
            'email': 'test@example.com',
            'password': 'testpassword123',
            'name': 'Test name',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """ Test that email and password fields its required """
        payload = {
            'email': 'one',
            'password': '',
        }
        res = self.client.post(TOKEN_URL,)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_url_unauthorized(self):
        """ Test that authentication is required for users """
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """ Testing private API for users """
    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpassword123',
            name='Test name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """ Test that get profile for user with login """
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data,{
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """ Tesst that Post method is not allowed """
        res = self.client.post(ME_URL,{})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """ Test that the user is updated if authenticated """
        payload = {
            'password': 'newpassword123',
            'name': 'new name',
        }
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
