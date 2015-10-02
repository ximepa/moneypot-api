# -*- encoding: utf-8 -*-
__author__ = 'maxim'

from grappelli_filters import RelatedAutocompleteFilter
from mptt.models import MPTTModel


class MPTTRelatedAutocompleteFilter(RelatedAutocompleteFilter):

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.model_admin = model_admin
        self.field_path = field_path
        super(MPTTRelatedAutocompleteFilter, self).__init__(field, request, params, model, model_admin, field_path)

    def get_parameter_name(self, field_path):
        if self.url_parameter:
            field_path = self.url_parameter
        return u'{0}__id__in'.format(field_path)

    def queryset(self, request, queryset):
        if self.used_param():
            param = self.used_param()
            field_paths = self.field_path.split("__")
            mptt_model = queryset.model
            for field_path in field_paths:
                try:
                    mptt_model = getattr(mptt_model, field_path).field.rel.to
                except AttributeError, e:
                    print e

            if issubclass(mptt_model, MPTTModel):
                try:
                    obj = mptt_model.objects.get(pk=param[0])
                except mptt_model.DoesNotExist:
                    pass
                else:
                    request.mptt_filter = obj
                    tree = obj.get_descendants(include_self=True)
                    param = tree.values_list("id", flat=True)

            filter_parameter = self.filter_parameter if self.filter_parameter else self.get_parameter_name(self.field_path)
            return queryset.filter(**{filter_parameter: param})
