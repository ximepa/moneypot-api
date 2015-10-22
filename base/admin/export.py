# -*- encoding: utf-8 -*-
from __future__ import print_function, division, unicode_literals, absolute_import

from import_export import resources
from base.models import Item


class ItemResource(resources.ModelResource):

    class Meta:
        model = Item