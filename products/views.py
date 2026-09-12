from rest_framework.viewsets import ModelViewSet

from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(ModelViewSet):
	queryset = Product.objects.select_related('category').order_by('name')
	serializer_class = ProductSerializer
