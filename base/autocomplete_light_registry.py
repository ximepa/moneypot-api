# -*- encoding: utf-8 -*-
__author__ = 'maxim'

import autocomplete_light

from .models import Place, ItemCategory, Item


autocomplete_light.register(Place,
                            search_fields=['name'],
                            attrs={
                                'placeholder': 'place name',
                                'data-autocomplete-minimum-characters': 1,
                            },
                            widget_attrs={
                                'data-widget-maximum-values': 4,
                                # 'class': 'modern-style',
                            },
                            )


class ItemCategoryAutocomplete(autocomplete_light.AutocompleteModelBase):
    autocomplete_js_attributes = {'placeholder': 'region name ..'}

    def choices_for_request(self):
        q = self.request.GET.get('q', '')
        source_id = self.request.GET.get('source_id', None)

        choices = ItemCategory.objects.filter(name__icontains=q)

        if source_id:
            try:
                place = Place.objects.get(pk=source_id)
            except Place.DoesNotExist:
                pass
            else:
                choices = choices.filter(items__place=place)

        return self.order_choices(choices)[0:self.limit_choices]


autocomplete_light.register(ItemCategory, ItemCategoryAutocomplete)

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