# -*- encoding: utf-8 -*-
from __future__ import print_function, division, unicode_literals, absolute_import

import autocomplete_light
from decimal import Decimal, InvalidOperation

from .models import Place, ItemCategory, Item, ItemSerial, ItemChunk, Cell, Purchase, PurchaseItem


###################################################################################
###################################################################################


def addslashes(value):
    """
    Adds slashes before quotes. Useful for escaping strings in CSV, for
    example. Less useful for escaping JavaScript; use the ``escapejs``
    filter instead.
    """
    return value.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")


class ItemCategoryAutocomplete(autocomplete_light.AutocompleteModelBase):

    def choices_for_request(self):
        q = addslashes(self.request.GET.get('q', ''))
        all_nodes = int(self.request.GET.get('all_nodes', "0"))
        source_id = self.request.GET.get('source_id', None)

        _choices = ItemCategory.objects.filter(name__icontains=q)

        if not _choices.count():
            choices = ItemCategory.objects.filter(name__similar=q).extra(
                select={'distance': "similarity(base_itemcategory.name, '%s')" % q}                
            ).order_by('-distance')
        else:
            choices = _choices

        if not all_nodes:
            choices = choices.filter(children__isnull=True)

        if source_id:
            choices = choices.filter(items__place_id=source_id)

        return self.order_choices(choices)[0:self.limit_choices]


autocomplete_light.register(ItemCategory, ItemCategoryAutocomplete, attrs={
                                'placeholder': 'item category name',
                                'style': "width: 200px",
                                'data-autocomplete-minimum-characters': 0,
                            },)


###################################################################################
###################################################################################


autocomplete_light.register(Item,
                            search_fields=['category__name'],
                            attrs={
                                'placeholder': 'item category name',
                                'data-autocomplete-minimum-characters': 1,
                            },
                            widget_attrs={
                                'data-widget-maximum-values': 4,
                                # 'class': 'modern-style',
                            },
                            )


###################################################################################
###################################################################################


class ItemSerialAutocomplete(autocomplete_light.AutocompleteModelBase):

    def choices_for_request(self):
        q = self.request.GET.get('q', '')
        source_id = self.request.GET.get('source_id', None)
        category_id = self.request.GET.get('category_id', None)

        choices = ItemSerial.objects.filter(serial__icontains=q)

        if source_id:
            choices = choices.filter(item__place_id=source_id)

        if category_id:
            choices = choices.filter(item__category_id=category_id)

        return self.order_choices(choices)[0:self.limit_choices]


autocomplete_light.register(ItemSerial, ItemSerialAutocomplete,attrs={
                                'placeholder': 'serial ..',
                                'data-autocomplete-minimum-characters': 0,
                                'style': "width: 140px"
                            },)


###################################################################################
###################################################################################


class ItemChunkAutocomplete(autocomplete_light.AutocompleteModelBase):

    def choices_for_request(self):
        q = self.request.GET.get('q', '0')
        try:
            q = Decimal(q)
        except InvalidOperation:
            q = Decimal("0")
        source_id = self.request.GET.get('source_id', None)
        category_id = self.request.GET.get('category_id', None)

        choices = ItemChunk.objects.filter(chunk__gte=q).order_by('chunk')

        if source_id:
            choices = choices.filter(item__place_id=source_id)

        if category_id:
            choices = choices.filter(item__category_id=category_id)

        return self.order_choices(choices)[0:self.limit_choices]


autocomplete_light.register(ItemChunk, ItemChunkAutocomplete,attrs={
                                'placeholder': 'chunk ..',
                                'data-autocomplete-minimum-characters': 0,
                                'style': "width: 140px"
                            },)


###################################################################################
###################################################################################


class SubPlaceAutocomplete(autocomplete_light.AutocompleteModelBase):

    def choices_for_request(self):
        q = self.request.GET.get('q', '')
        place_id = self.request.GET.get('place_id', None)
        choices = []

        if place_id:
            try:
                place = Place.objects.get(pk=place_id)
            except Place.DoesNotExist:
                pass
            else:
                choices = place.get_descendants(include_self=True)

        if not choices:
            choices = Place.objects.all()

        _choices = choices.filter(name__icontains=q)

        if not _choices.count():

            choices = choices.filter(name__similar=q).extra(
                select={'distance': "similarity(base_place.name, '%s')" % q}
            ).order_by('-distance')

        else:
            choices = _choices

        return self.order_choices(choices)[0:self.limit_choices]


autocomplete_light.register(Place, SubPlaceAutocomplete, attrs={
    'placeholder': 'place ..',
    'style': "width: 140px"
},)


###################################################################################
###################################################################################


class CellAutocomplete(autocomplete_light.AutocompleteModelBase):

    def choices_for_request(self):
        q = self.request.GET.get('q', '')

        choices = Cell.objects.filter(name__icontains=q)

        return self.order_choices(choices)[0:self.limit_choices]


autocomplete_light.register(Cell, CellAutocomplete, attrs={
    'data-autocomplete-minimum-characters': 1,
    'placeholder': 'cell name ..',
    'size': 10,
    'style': "width: 80px"
},)


###################################################################################
###################################################################################


class ItemAutocomplete(autocomplete_light.AutocompleteModelBase):

    def choices_for_request(self):
        q = self.request.GET.get('q', '')
        place = None
        if " - " in q:
            q, place = q.split(" - ")

        _choices = Item.objects.filter(category__name__icontains=q)

        if not _choices.count():
            choices = Item.objects.filter(category__name__similar=q).extra(
                select={'distance': "similarity(base_itemcategory.name, '%s')" % q}
            ).order_by('-distance')
        else:
            choices = _choices

        if place:
            choices = choices.filter(place__name__icontains=place)

        return self.order_choices(choices)[0:self.limit_choices]


autocomplete_light.register(Item, ItemAutocomplete, attrs={
    'data-autocomplete-minimum-characters': 1,
    'placeholder': 'item category name ..',
    # 'size': 30,
    # 'style': "width: 200px"
},)


###################################################################################
###################################################################################


class PurchaseItemAutocomplete(autocomplete_light.AutocompleteModelBase):

    def choices_for_request(self):
        item_id = int(self.request.GET.get('item_id', '0'))
        category_id = None
        destination = None
        try:
            item = Item.objects.get(pk=item_id)
        except Item.DoesNotExist:
            pass
        else:
            category_id = item.category_id
            destination = item.place

        choices = PurchaseItem.objects.filter(category_id=category_id, purchase__destination=destination)

        return self.order_choices(choices)[0:self.limit_choices]

autocomplete_light.register(PurchaseItem, PurchaseItemAutocomplete, attrs={
    'data-autocomplete-minimum-characters': 0,
    'placeholder': 'purchase item ..',
    # 'size': 30,
    # 'style': "width: 200px"
},)


###################################################################################
###################################################################################
