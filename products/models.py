from django.db import models

from categories.models import Category


class Product(models.Model):
	name = models.CharField(max_length=150)
	description = models.TextField(blank=True)
	price = models.DecimalField(max_digits=10, decimal_places=2)
	category = models.ForeignKey(
		Category,
		on_delete=models.PROTECT,
		related_name='products',
	)

	def __str__(self):
		return self.name
