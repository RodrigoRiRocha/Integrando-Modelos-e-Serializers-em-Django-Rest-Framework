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

    def create(self, validated_data):
        category_data = validated_data.pop('category')
        category, _ = Category.objects.get_or_create(
            name=category_data['name'],
            defaults={'description': category_data.get('description', '')},
        )
        return Product.objects.create(category=category, **validated_data)