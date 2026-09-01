from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import Category
from .serializers import CategorySerializer


class CategorySerializerTests(TestCase):
	def test_accepts_valid_category_data(self):
		serializer = CategorySerializer(
			data={'name': 'Books', 'description': 'Printed books'}
		)

		self.assertTrue(serializer.is_valid(), serializer.errors)
		category = serializer.save()
		self.assertEqual(category.name, 'Books')

	def test_name_is_required(self):
		serializer = CategorySerializer(data={'description': 'Printed books'})

		self.assertFalse(serializer.is_valid())
		self.assertIn('name', serializer.errors)


class CategoryViewSetTests(TestCase):
	def setUp(self):
		self.client = APIClient()

	def test_creates_and_lists_categories(self):
		response = self.client.post(
			'/api/categories/',
			{'name': 'Books', 'description': 'Printed books'},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Category.objects.count(), 1)
		self.assertEqual(
			self.client.get('/api/categories/').data['results'][0]['name'],
			'Books',
		)

	def test_rejects_category_without_name(self):
		response = self.client.post('/api/categories/', {}, format='json')

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn('name', response.data)
