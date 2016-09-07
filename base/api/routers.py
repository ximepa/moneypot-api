# -*- encoding: utf-8 -*-

from rest_framework import routers

from .viewsets import CategoryViewSet, VItemMovementViewSet, VSerialMovementViewSet

router = routers.DefaultRouter()
router.register(r'category', CategoryViewSet)
router.register(r'item_movement', VItemMovementViewSet)
router.register(r'serial_movement', VSerialMovementViewSet)

