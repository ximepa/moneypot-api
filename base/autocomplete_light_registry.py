# -*- encoding: utf-8 -*-
__author__ = 'maxim'

import autocomplete_light

from .models import Place, ItemCategory, Item, ItemSerial

#
# autocomplete_light.register(Place,
#                             search_fields=['name'],
#                             attrs={
#                                 'placeholder': 'place name',
#                                 'data-autocomplete-minimum-characters': 1,
#                             },
#                             widget_attrs={
#                                 'data-widget-maximum-values': 4,
#                                 # 'class': 'modern-style',
#                             },
#                             )


class ItemCategoryAutocomplete(autocomplete_light.AutocompleteModelBase):
    autocomplete_js_attributes = {'placeholder': 'region name ..'}

    def choices_for_request(self):
        q = self.request.GET.get('q', '')
        source_id = self.request.GET.get('source_id', None)

        choices = ItemCategory.objects.filter(name__icontains=q).filter(children__isnull=True)

        if source_id:
            choices = choices.filter(items__place_id=source_id)

        return self.order_choices(choices)[0:self.limit_choices]


autocomplete_light.register(ItemCategory, ItemCategoryAutocomplete, attrs={
                                'placeholder': 'item category name',
                                'data-autocomplete-minimum-characters': 0,
                            },)

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


class ItemSerialAutocomplete(autocomplete_light.AutocompleteModelBase):
    autocomplete_js_attributes = {'placeholder': 'serial ..'}

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
                            },)


class SubPlaceAutocomplete(autocomplete_light.AutocompleteModelBase):
    autocomplete_js_attributes = {'placeholder': 'sub place ..'}

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

        choices = choices.filter(name__icontains=q)

        return self.order_choices(choices)[0:self.limit_choices]


autocomplete_light.register(Place, SubPlaceAutocomplete)