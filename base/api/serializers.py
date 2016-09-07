# -*- encoding: utf-8 -*-
from rest_framework import serializers

from base.models import ItemCategory, Item, ItemSerial, Place, VItemMovement, VSerialMovement


class CategorySerializer(serializers.HyperlinkedModelSerializer):

    photo = serializers.SerializerMethodField('get_static_thumbnail_url')

    class Meta:
        model = ItemCategory
        fields = ('id', 'name', 'photo')

    def get_static_thumbnail_url(self, obj):
        request = self.context['request']
        return request.build_absolute_uri(obj.thumbnail.url)


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

    items = serializers.SerializerMethodField('get_items_empty')

    class Meta:
        model = Place
        fields = ('id', 'name', 'items')

    def get_items_empty(self, obj):
        return []


class VItemMovementSerializer(serializers.HyperlinkedModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = VItemMovement
        fields = ('item_category_name', 'category', 'quantity', 'source_name', 'destination_name', 'completed_at')


class VSerialMovementSerializer(serializers.HyperlinkedModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = VSerialMovement
        fields = ('item_category_name', 'category', 'serial', 'source_name', 'destination_name', 'completed_at')
