# -*- encoding: utf-8 -*-

from rest_framework import routers

from .viewsets import CategoryViewSet, VItemMovementViewSet, VSerialMovementViewSet, TransactionViewSet, PlaceViewSet

router = routers.DefaultRouter()
router.register(r'category', CategoryViewSet)
router.register(r'place', PlaceViewSet)
router.register(r'item_movement', VItemMovementViewSet)
router.register(r'serial_movement', VSerialMovementViewSet)
router.register(r'transaction', TransactionViewSet)

