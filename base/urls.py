from django.conf.urls import patterns, url

urlpatterns = patterns('base.views',
                       url(r'^index/', 'index', name="index"),
                       url(r'^ajax/qty/(?P<place_id>\d+)/(?P<category_id>\d+)/', 'ajax_qty', name="ajax_qty"),
                       )
