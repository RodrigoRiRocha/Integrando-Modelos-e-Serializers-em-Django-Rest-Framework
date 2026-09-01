from rest_framework.viewsets import ModelViewSet

from .models import Order
from .serializers import OrderSerializer


class OrderViewSet(ModelViewSet):
	queryset = Order.objects.prefetch_related('products').order_by('-created_at')
	serializer_class = OrderSerializer
