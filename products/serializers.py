from rest_framework import serializers

from categories.models import Category
from categories.serializers import CategorySerializer

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'category')
        read_only_fields = ('id',)

    def _resolve_category(self, category_data):
        category, _ = Category.objects.get_or_create(
            name=category_data['name'],
            defaults={'description': category_data.get('description', '')},
        )
        return category

    def create(self, validated_data):
        category_data = validated_data.pop('category')
        return Product.objects.create(
            category=self._resolve_category(category_data),
            **validated_data,
        )

    def update(self, instance, validated_data):
        category_data = validated_data.pop('category', None)
        if category_data is not None:
            instance.category = self._resolve_category(category_data)

        return super().update(instance, validated_data)
