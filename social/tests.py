from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .models import Post


class SocialApiTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.alice = User.objects.create_user(username='alice', password='alice-pass-123')
		self.bob = User.objects.create_user(username='bob', password='bob-pass-123')

	def authenticate_as(self, user):
		token, _ = Token.objects.get_or_create(user=user)
		self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

	def test_register_and_login_return_a_token(self):
		response = self.client.post(
			'/api/social/auth/register/',
			{'username': 'carol', 'password': 'carol-pass-123'},
			format='json',
		)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertIn('token', response.data)

		response = self.client.post(
			'/api/social/auth/login/',
			{'username': 'carol', 'password': 'carol-pass-123'},
			format='json',
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertIn('token', response.data)

	def test_social_home_page_is_available(self):
		response = self.client.get('/api/social/')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertContains(response, 'Social API')

	def test_profile_can_be_updated_without_changing_all_fields(self):
		self.authenticate_as(self.alice)

		response = self.client.patch(
			'/api/social/profiles/me/',
			{'first_name': 'Alice', 'avatar_url': 'https://example.com/alice.png'},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['first_name'], 'Alice')
		self.assertEqual(response.data['avatar_url'], 'https://example.com/alice.png')

	def test_following_user_populates_personalized_feed(self):
		post = Post.objects.create(author=self.bob, content='Hello from Bob')
		self.authenticate_as(self.alice)

		self.assertEqual(self.client.get('/api/social/posts/feed/').data['count'], 0)
		response = self.client.post(
			f'/api/social/profiles/{self.bob.profile.id}/follow/',
			format='json',
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		response = self.client.get('/api/social/posts/feed/')
		self.assertEqual(response.data['count'], 1)
		self.assertEqual(response.data['results'][0]['id'], post.id)

	def test_user_can_like_and_comment_on_a_post(self):
		post = Post.objects.create(author=self.bob, content='A post to interact with')
		self.authenticate_as(self.alice)

		response = self.client.post(f'/api/social/posts/{post.id}/like/', format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['likes_count'], 1)

		response = self.client.post(
			f'/api/social/posts/{post.id}/comments/',
			{'content': 'Great post!'},
			format='json',
		)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(response.data['author'], 'alice')

	def test_only_author_can_update_post_and_anonymous_requests_are_rejected(self):
		post = Post.objects.create(author=self.bob, content='Private editing')

		self.assertEqual(
			self.client.post('/api/social/posts/', {'content': 'No access'}, format='json').status_code,
			status.HTTP_401_UNAUTHORIZED,
		)

		self.authenticate_as(self.alice)
		response = self.client.patch(
			f'/api/social/posts/{post.id}/',
			{'content': 'Trying to edit'},
			format='json',
		)
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

# Create your tests here.
