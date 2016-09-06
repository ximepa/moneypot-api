from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework.authtoken import views as authtoken_views
from django.views.generic import TemplateView
from filebrowser.sites import site as fb
from django.conf.urls.static import static
from django.conf import settings

from base.api.routers import router

admin.site.disable_action('delete_selected')

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'moneypot.views.home', name='home'),
                       url(r'^base/', include('base.urls', namespace="base")),
                       url(r'^filebrowser/', include(fb.urls)),
                       url(r'^grappelli/', include('grappelli.urls')),
                       url(r'^api/', include(router.urls)),
                       url(r'^api/', include("base.api.urls")),
                       url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
                       url(r'^api-token-auth/', authtoken_views.obtain_auth_token),
                       url(r'^autocomplete/', include('autocomplete_light.urls')),
                       url(r'', include(admin.site.urls)),
                       url(r'^admin/', TemplateView.as_view(template_name="base/redirect.html")),
                       url(r'^p/', include('django.contrib.flatpages.urls')),
                       )

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)