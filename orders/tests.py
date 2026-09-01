from django.test import TestCase

from categories.models import Category
from products.models import Product

from .serializers import OrderSerializer


class OrderSerializerTests(TestCase):
	def setUp(self):
		category = Category.objects.create(name='Books')
		self.product = Product.objects.create(
			name='Clean Code',
			price='79.90',
			category=category,
		)

	def test_creates_order_with_products(self):
		serializer = OrderSerializer(
			data={'customer_name': 'Ada Lovelace', 'products': [self.product.id]}
		)

		self.assertTrue(serializer.is_valid(), serializer.errors)
		order = serializer.save()
		self.assertEqual(order.customer_name, 'Ada Lovelace')
		self.assertEqual(list(order.products.all()), [self.product])
		self.assertIn('created_at', OrderSerializer(order).data)

	def test_rejects_unknown_product(self):
		serializer = OrderSerializer(
			data={'customer_name': 'Ada Lovelace', 'products': [999]}
		)

		self.assertFalse(serializer.is_valid())
		self.assertIn('products', serializer.errors)
