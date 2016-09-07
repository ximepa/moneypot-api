# -*- encoding: utf-8 -*-
from rest_framework import viewsets, filters
from rest_framework.exceptions import NotFound
from django.db.models import Q
from base.models import ItemCategory, VItemMovement, VSerialMovement

from .serializers import CategorySerializer, VItemMovementSerializer, VSerialMovementSerializer


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


class FilteredByPlaceMixin(object):
    def get_queryset(self):
        """
        queryset filtered for current user
        """
        place = None
        try:
            place = self.request.user.profile.place
        except Exception as e:
            print(e)
        if not place:
            raise NotFound()
        return self.queryset.filter(Q(source=place)|Q(destination=place)).order_by('-completed_at')


class VItemMovementViewSet(FilteredByPlaceMixin, viewsets.ReadOnlyModelViewSet):
    queryset = VItemMovement.objects.all()
    serializer_class = VItemMovementSerializer
    search_fields = ('item_category_name', )
    filter_fields = ('category', )


class VSerialMovementViewSet(FilteredByPlaceMixin, viewsets.ReadOnlyModelViewSet):
    queryset = VSerialMovement.objects.all()
    serializer_class = VSerialMovementSerializer
    search_fields = ('item_category_name', 'serial')
    filter_fields = ('serial', )
