from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from categories.models import Category

from .models import Product
from .serializers import ProductSerializer


class ProductSerializerTests(TestCase):
	def test_returns_nested_category(self):
		category = Category.objects.create(name='Books')
		product = Product.objects.create(
			name='Django for Beginners',
			description='A practical guide',
			price='49.90',
			category=category,
		)

		data = ProductSerializer(product).data

		self.assertEqual(
			data,
			{
				'id': product.id,
				'name': 'Django for Beginners',
				'description': 'A practical guide',
				'price': '49.90',
				'category': {'id': category.id, 'name': 'Books', 'description': ''},
			},
		)

	def test_creates_product_with_nested_category(self):
		serializer = ProductSerializer(
			data={
				'name': 'Django REST Framework',
				'description': 'API development',
				'price': '59.90',
				'category': {'name': 'Programming', 'description': 'Technical books'},
			}
		)

		self.assertTrue(serializer.is_valid(), serializer.errors)
		product = serializer.save()
		self.assertEqual(product.category.name, 'Programming')
		self.assertEqual(Product.objects.count(), 1)

	def test_rejects_invalid_price_and_missing_category(self):
		serializer = ProductSerializer(
			data={'name': 'Invalid product', 'price': 'not-a-price'}
		)

		self.assertFalse(serializer.is_valid())
		self.assertIn('price', serializer.errors)
		self.assertIn('category', serializer.errors)


class ProductViewSetTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.category = Category.objects.create(name='Programming')
		self.product = Product.objects.create(
			name='Django',
			price='59.90',
			category=self.category,
		)

	def test_retrieves_nested_category_and_updates_product(self):
		response = self.client.get(f'/api/products/{self.product.id}/')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['category']['name'], 'Programming')

		response = self.client.patch(
			f'/api/products/{self.product.id}/',
			{'price': '69.90'},
			format='json',
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.product.refresh_from_db()
		self.assertEqual(str(self.product.price), '69.90')

	def test_creates_product_and_returns_404_for_missing_product(self):
		response = self.client.post(
			'/api/products/',
			{
				'name': 'Django REST Framework',
				'price': '64.90',
				'category': {'name': 'APIs', 'description': 'API books'},
			},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(response.data['category']['name'], 'APIs')
		self.assertEqual(
			self.client.get('/api/products/999/').status_code,
			status.HTTP_404_NOT_FOUND,
		)
