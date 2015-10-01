# -*- encoding: utf-8 -*-
__author__ = 'maxim'

from grappelli_filters import RelatedAutocompleteFilter
from mptt.managers import TreeManager
from base.models import ItemCategory


class MPTTCategoryRelatedAutocompleteFilter(RelatedAutocompleteFilter):

    def queryset(self, request, queryset):
        if self.used_param():
            qs = super(MPTTCategoryRelatedAutocompleteFilter, self).queryset(request, queryset)
            filter_parameter = self.filter_parameter if self.filter_parameter else self.parameter_name
            if filter_parameter == "category__id__exact":
                filter_value = self.used_param()
                cat_qs = ItemCategory.objects.filter(id__exact=filter_value)
                cat_qs = cat_qs.model.objects.get_queryset_descendants(cat_qs, include_self=False)
                qs = qs.model.objects.filter(category__id__in=cat_qs.values_list("id", flat=True))
            return qs
