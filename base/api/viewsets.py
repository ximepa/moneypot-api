# -*- encoding: utf-8 -*-
from rest_framework import viewsets
from base.models import ItemCategory

from .serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = ItemCategory.objects.all()
    serializer_class = CategorySerializer
    search_fields = ('name',)