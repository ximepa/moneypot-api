# -*- encoding: utf-8 -*-
from rest_framework import serializers

from base.models import ItemCategory, Item, TransactionItem, ItemSerial, Place, VItemMovement, VSerialMovement, \
    Transaction


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    photo = serializers.SerializerMethodField('get_static_thumbnail_url')
    relevance = serializers.SerializerMethodField()

    class Meta:
        model = ItemCategory
        fields = ('id', 'name', 'photo', 'relevance')

    def get_static_thumbnail_url(self, obj):
        request = self.context['request']
        return request.build_absolute_uri(obj.thumbnail.url)

    def get_relevance(self, obj):
        if hasattr(obj, 'distance'):
            return obj.distance
        return None


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


class TransactionItemSerializer(serializers.HyperlinkedModelSerializer):
    serial = ItemSerialSerializer()
    category = CategorySerializer()

    class Meta:
        model = TransactionItem
        fields = ('id', 'quantity', 'category', 'serial')


class PlaceSerializer(serializers.HyperlinkedModelSerializer):
    items = serializers.SerializerMethodField('get_items_empty')
    relevance = serializers.SerializerMethodField()

    class Meta:
        model = Place
        fields = ('id', 'name', 'items', 'relevance')

    def get_items_empty(self, obj):
        return []

    def get_relevance(self, obj):
        if hasattr(obj, 'distance'):
            return obj.distance
        return None


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


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    source = PlaceSerializer()
    destination = PlaceSerializer()
    created_at = serializers.ReadOnlyField()
    is_negotiated_source = serializers.ReadOnlyField()
    is_negotiated_destination = serializers.ReadOnlyField()
    is_confirmed_source = serializers.ReadOnlyField()
    is_confirmed_destination = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    completed_at = serializers.ReadOnlyField()
    detailed = serializers.HyperlinkedIdentityField(view_name="transaction-detail")

    class Meta:
        model = Transaction
        fields = ('id', 'detailed', 'source', 'destination', 'created_at', 'is_negotiated_source',
                  'is_negotiated_destination', 'is_confirmed_source', 'is_confirmed_destination',
                  'is_completed', 'completed_at')


class TransactionSerializerDetailed(serializers.HyperlinkedModelSerializer):
    source = PlaceSerializer()
    destination = PlaceSerializer()
    created_at = serializers.ReadOnlyField()
    is_negotiated_source = serializers.ReadOnlyField()
    is_negotiated_destination = serializers.ReadOnlyField()
    is_confirmed_source = serializers.ReadOnlyField()
    is_confirmed_destination = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    completed_at = serializers.ReadOnlyField()
    transaction_items = TransactionItemSerializer(many=True, read_only=True)

    class Meta:
        model = Transaction
        fields = ('id', 'source', 'destination', 'created_at', 'is_negotiated_source', 'is_negotiated_destination',
                  'is_confirmed_source', 'is_confirmed_destination', 'is_completed',
                  'completed_at', 'transaction_items')
