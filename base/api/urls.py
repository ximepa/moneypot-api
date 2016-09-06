# -*- encoding: utf-8 -*-
from __future__ import print_function, division, unicode_literals, absolute_import

from django.conf.urls import patterns, url

from base.api.views import HomeView

urlpatterns = patterns('base.api.views',
                       url(r'^home/', HomeView.as_view(),
                           name="home"),
                       )
