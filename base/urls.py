# -*- encoding: utf-8 -*-
from __future__ import print_function, division, unicode_literals, absolute_import

from django.conf.urls import patterns, url


urlpatterns = patterns('base.views',
                       url(r'^index/', 'index',
                           name="index"),
                       url(r'^ajax/qty/(?P<place_id>\d+)/(?P<category_id>\d+)/', 'ajax_qty',
                           name="ajax_qty"),
                       url(r'^ajax/price/(?P<source_id>\d+)/(?P<category_id>\d+)/', 'ajax_price',
                           name="ajax_price"),
                       url(r'^ajax/serial_category/(?P<serial_id>\d+)/', 'ajax_serial_category',
                           name="ajax_serial_category"),
                       url(r'^ajax/cell/(?P<place_id>\d+)/(?P<category_id>\d+)/(?P<serial_id>\d+)/', 'ajax_cell',
                           name="ajax_cell"),
                       url(r'^ajax/cell/(?P<place_id>\d+)/(?P<category_id>\d+)/', 'ajax_cell',
                           name="ajax_cell"),
                       url(r'^ajax/item_cell/(?P<item_id>\d+)/(?P<cell_id>\d+)/', 'ajax_item_cell',
                           name="ajax_item_cell"),
                       url(r'^ajax/serial_cell/(?P<serial_id>\d+)/(?P<cell_id>\d+)/', 'ajax_serial_cell',
                           name="ajax_serial_cell"),
                       url(r'^ajax/chunk_cell/(?P<chunk_id>\d+)/(?P<cell_id>\d+)/', 'ajax_chunk_cell',
                           name="ajax_chunk_cell"),
                       url(r'^ajax/serial_warranty/(?P<serial_id>\d+)/(?P<datestr>.+)/', 'ajax_serial_warranty',
                           name="ajax_serial_warranty"),
                       url(r'^ajax/serial_warranty_delete/(?P<serial_id>\d+)/', 'ajax_serial_warranty',
                           name="ajax_serial_warranty_delete"),
                       url(r'^place_item/(?P<place_id>\d+)/export', 'export_items',
                           name="export_items"),
                       url(r'^get_object_ancestors/(?P<model_name>.+)/(?P<object_id>\d+)/', 'get_object_ancestors',
                           name="get_object_ancestors"),
                       )
