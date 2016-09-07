# -*- encoding: utf-8 -*-
from rest_framework import viewsets, filters
from rest_framework.exceptions import NotFound
from django.db.models import Q
from base.models import ItemCategory, VItemMovement

from .serializers import CategorySerializer, VItemMovementSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = ItemCategory.objects.all()
    serializer_class = CategorySerializer
    search_fields = ('name',)


# class ProductFilter(filters.FilterSet):
#     min_price = django_filters.NumberFilter(name="price", lookup_expr='gte')
#     max_price = django_filters.NumberFilter(name="price", lookup_expr='lte')
#     class Meta:
#         model = Product
#         fields = ['category', 'in_stock', 'min_price', 'max_price']


class VItemMovementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = VItemMovement.objects.all()
    serializer_class = VItemMovementSerializer
    search_fields = ('item_category_name', )
    filter_fields = ('category', )

    def get_queryset(self):
        """
        This ViewSet should return a list of all item movements
        for the currently authenticated user.
        """
        place = None
        try:
            place = self.request.user.profile.place
        except Exception as e:
            print(e)
        if not place:
            raise NotFound()
        return VItemMovement.objects.filter(Q(source=place)|Q(destination=place)).order_by('-completed_at')

