import os
import runpy
import secrets
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


class DatabaseConfigurationTests(SimpleTestCase):
	def load_database(self, environment):
		with patch.dict(os.environ, environment, clear=True):
			return runpy.run_path(str(Path(__file__).with_name('settings.py')))['DATABASES']['default']

	def test_sqlite_fallback_preserves_custom_path(self):
		database = self.load_database({'DJANGO_DB_PATH': 'custom.sqlite3'})

		self.assertEqual(database['ENGINE'], 'django.db.backends.sqlite3')
		self.assertEqual(database['NAME'], 'custom.sqlite3')

	def test_postgresql_configuration(self):
		environment = {
			'POSTGRES_HOST': 'db',
			'POSTGRES_DB': 'bookstore',
			'POSTGRES_USER': 'bookstore',
			'POSTGRES_PASSWORD': secrets.token_urlsafe(32),
		}
		database = self.load_database(environment)

		self.assertEqual(database, {
			'ENGINE': 'django.db.backends.postgresql',
			'NAME': environment['POSTGRES_DB'],
			'USER': environment['POSTGRES_USER'],
			'PASSWORD': environment['POSTGRES_PASSWORD'],
			'HOST': 'db',
			'PORT': '5432',
		})
		environment['POSTGRES_PORT'] = '5433'
		self.assertEqual(self.load_database(environment)['PORT'], '5433')

	def test_postgresql_requires_complete_configuration(self):
		with self.assertRaises(KeyError):
			self.load_database({'POSTGRES_HOST': 'db'})


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
