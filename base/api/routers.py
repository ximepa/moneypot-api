# -*- encoding: utf-8 -*-

from rest_framework import routers

from .viewsets import CategoryViewSet

router = routers.DefaultRouter()
router.register(r'category', CategoryViewSet)

