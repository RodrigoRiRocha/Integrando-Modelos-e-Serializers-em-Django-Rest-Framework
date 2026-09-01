from django.test import TestCase

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
