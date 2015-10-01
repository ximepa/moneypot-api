from django.conf.urls import patterns, url

urlpatterns = patterns('base.views',
                       url(r'^index/', 'index', name="index"),
                       url(r'^ajax/qty/(?P<place_id>\d+)/(?P<category_id>\d+)/', 'ajax_qty', name="ajax_qty"),
                       url(r'^ajax/price/(?P<source_id>\d+)/(?P<category_id>\d+)/', 'ajax_price', name="ajax_price"),
                       url(r'^ajax/serial_category/(?P<serial_id>\d+)/', 'ajax_serial_category',
                           name="ajax_serial_category"),
                       url(r'^ajax/cell/(?P<place_id>\d+)/(?P<category_id>\d+)/(?P<serial_id>\d+)/', 'ajax_cell',
                           name="ajax_cell"),
                       url(r'^ajax/cell/(?P<place_id>\d+)/(?P<category_id>\d+)/', 'ajax_cell', name="ajax_cell"),
                       url(r'^ajax/item_cell/(?P<item_id>\d+)/(?P<cell_id>\d+)/', 'ajax_item_cell', name="ajax_item_cell"),
                       )
