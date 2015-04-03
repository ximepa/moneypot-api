from django.conf.urls import patterns, url

urlpatterns = patterns('base.views',
                       url(r'^index/', 'index', name="index"),
)
