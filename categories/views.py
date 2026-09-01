from rest_framework.viewsets import ModelViewSet

from .models import Category
from .serializers import CategorySerializer


class CategoryViewSet(ModelViewSet):
	queryset = Category.objects.all().order_by('name')
	serializer_class = CategorySerializer
