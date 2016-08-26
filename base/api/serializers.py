# -*- encoding: utf-8 -*-
from rest_framework import serializers

from base.models import ItemCategory


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ItemCategory
        fields = ('id', 'name', 'photo')

