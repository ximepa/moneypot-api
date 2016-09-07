# -*- encoding: utf-8 -*-

from rest_framework import routers

from .viewsets import CategoryViewSet, VItemMovementViewSet

router = routers.DefaultRouter()
router.register(r'category', CategoryViewSet)
router.register(r'item_movement', VItemMovementViewSet)

