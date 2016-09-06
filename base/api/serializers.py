# -*- encoding: utf-8 -*-
from rest_framework import serializers

from base.models import ItemCategory, Item, ItemSerial, Place


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ItemCategory
        fields = ('id', 'name', 'photo')


class ItemSerialSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ItemSerial
        fields = ('id', 'serial')


class ItemSerializer(serializers.HyperlinkedModelSerializer):

    serials = ItemSerialSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Item
        fields = ('id', 'quantity', 'category', 'serials')


class PlaceSerializer(serializers.HyperlinkedModelSerializer):

    items = ItemSerializer(many=True, read_only=True)

    class Meta:
        model = Place
        fields = ('id', 'name', 'items')
