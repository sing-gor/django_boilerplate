from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

TOKEN_URL = reverse('user:token')
CREATE_USER_URL = reverse('user:create')
ME_URL = reverse('user:me')

def create_user(**param):
    return get_user_model().objects.create_user(**param)




class PublicUserApiTests(TestCase):
    """Test the usersApi (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""

        payload = {
            'email': 'test@wongyusing.com',
            'password': 'testpassword',
            'name': 'testUsername'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)

        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creating user that already exists fails"""
        payload = {'email': 'test@wongyusing.com', 'password': 'testpassword'}
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 8 characters"""
        payload = {'email': 'test2@wongyusing.com', 'password': '11'}
        res = self.client.post(CREATE_USER_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test tha a token is created for the user"""
        payload = {'email': 'test@wongyusing.com', 'password': 'testpassword'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL,payload)

        self.assertIn('token',res.data)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
    
    def test_ccreate_tookn_invalid_credentials(self):
        """Test that token isnot created if invalid credentials are given"""
        payload = {'email': 'test@wongyusing.com', 'password': 'false_testpassword'}
    
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is nott created if user does not exist"""
        payload = {'email': 'test@wongyusing.com', 'password': 'testpassword'}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


    def test_create_token_missing_filed(self):
        """Test that email and password are required"""
        payload = {'email': 'tes', 'password': ''}

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""

        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


    

class PrivateUserApiTests(TestCase):
    """Test Api requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email='test@wongyusing.com',
            password='testpassword',
            name='testUsername'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)


    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in used"""

        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })
        
    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me url"""
        res = self.client.post(ME_URL,{})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_updata_user_profile(self):
        """Test updating the user profile for authenticated user"""

        payload = {'name': 'Sing', 'password': 'newpassword4565'}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)


        
