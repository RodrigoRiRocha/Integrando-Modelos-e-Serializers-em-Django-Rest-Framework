import secrets

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


class TokenAuthTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.password = secrets.token_urlsafe(32)
		self.user = User.objects.create_user(username='api-user', password=self.password)

	def test_obtains_token_with_valid_credentials(self):
		response = self.client.post(
			'/api/auth/token/',
			{'username': 'api-user', 'password': self.password},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['token'], Token.objects.get(user=self.user).key)

	def test_rejects_invalid_credentials(self):
		response = self.client.post(
			'/api/auth/token/',
			{'username': 'api-user', 'password': 'wrong-password'},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_grants_access_with_issued_token(self):
		token = Token.objects.create(user=self.user)

		self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
		response = self.client.get('/api/categories/')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
