from django.conf.urls import patterns, include, url
from django.contrib import admin


urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'moneypot.views.home', name='home'),
                       url(r'^base/', include('base.urls', namespace="base")),
                       url(r'^admin/', include(admin.site.urls)),
)
