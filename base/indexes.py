# -*- encoding: utf-8 -*-
__author__ = 'maxim'

from sphinxql import indexes, fields
from base.models import GeoName


class GeoNameIndex(indexes.Index):
    my_name = fields.Text(model_attr='name')

    class Meta:
        morphology = "stem_ru"
        model = GeoName