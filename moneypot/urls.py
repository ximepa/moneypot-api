from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework.authtoken import views as authtoken_views

admin.site.disable_action('delete_selected')


urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'moneypot.views.home', name='home'),
                       url(r'^base/', include('base.urls', namespace="base")),
                       url(r'^grappelli/', include('grappelli.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
                       url(r'^api-token-auth/', authtoken_views.obtain_auth_token),
                       url(r'^autocomplete/', include('autocomplete_light.urls')),
)