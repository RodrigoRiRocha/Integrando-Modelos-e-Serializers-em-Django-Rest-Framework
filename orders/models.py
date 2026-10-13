from django.db import models

from products.models import Product


class Order(models.Model):
	customer_name = models.CharField(max_length=150)
	products = models.ManyToManyField(Product, related_name='orders')
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'Order #{self.pk}'
