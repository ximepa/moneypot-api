# -*- encoding: utf-8 -*-
from pprint import pprint

from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets, filters, status
from rest_framework.exceptions import NotFound, PermissionDenied, ParseError
from rest_framework.response import Response
from django.db.models import Q

from base.models import ItemCategory, VItemMovement, VSerialMovement, Transaction, Place, TransactionItem

from .serializers import CategorySerializer, PlaceSerializer, VItemMovementSerializer, VSerialMovementSerializer, \
    TransactionSerializer, TransactionSerializerDetailed, TransactionItemSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ItemCategory.objects.all()
    serializer_class = CategorySerializer
    search_fields = ('name',)

    def get_queryset(self):
        """
        queryset filtered by search
        """
        q = self.request.GET.get('q', None)
        if not q:
            categories = ItemCategory.objects.all()
        elif len(q) > 3:
            categories = ItemCategory.objects.filter(name__similar=q).extra(
                select={'distance': "similarity(base_itemcategory.name, '%s')" % q}
            ).order_by('-distance')
        else:
            categories = ItemCategory.objects.filter(name__icontains=q)
        return categories


class PlaceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    search_fields = ('name',)

    def get_queryset(self):
        """
        queryset filtered by search
        """
        q = self.request.GET.get('q', None)
        if not q:
            places = Place.objects.all()
        elif len(q) > 3:
            places = Place.objects.filter(name__similar=q).extra(
                select={'distance': "similarity(base_place.name, '%s')" % q}
            ).order_by('-distance')
        else:
            places = Place.objects.filter(name__icontains=q)
        return places


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


class TransactionViewSet(FilteredByPlaceMixin, viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_fields = ('source', 'destination')

    def create(self, request, *args, **kwargs):
        data = request.data
        try:
            source = Place.objects.get(pk=data['source']['id'])
        except (Place.DoesNotExist, KeyError, ValueError):
            source = Place.objects.create(name=data['source']['name'])
        try:
            destination = Place.objects.get(pk=data['destination']['id'])
        except (Place.DoesNotExist, KeyError, ValueError):
            destination = Place.objects.create(name=data['destination']['name'])
        transaction = Transaction.objects.create(source=source, destination=destination)
        serializer = TransactionSerializerDetailed(transaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404:
            pass
        else:
            if instance.is_completed:
                raise PermissionDenied(detail=_("rt  Can't delete completed transaction"))
            else:
                self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = TransactionSerializerDetailed(instance, context={'request': request})
        return Response(serializer.data)


class TransactionItemViewSet(viewsets.ViewSet):
    queryset = TransactionItem.objects.all()
    serializer_class = TransactionItemSerializer
    filter_fields = ('transaction',)
    search_fields = ('item_category_name', 'serial')

    def list(self, request, transaction_pk=None):
        queryset = self.queryset.filter(transaction=transaction_pk)
        serializer = TransactionItemSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def create(self, request, transaction_pk=None):
        data = request.data
        serializer = TransactionItemSerializer(data, context={'request': request})
        if serializer.is_valid() and transaction_pk:
            ti = serializer.save()
            ti.transaction_id = transaction_pk
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise ParseError()

