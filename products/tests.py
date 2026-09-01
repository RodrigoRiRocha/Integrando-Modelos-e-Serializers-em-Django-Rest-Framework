from django.test import TestCase

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
